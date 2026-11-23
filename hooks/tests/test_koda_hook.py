"""Tests for hooks/scripts/koda_hook.py.

The script is driven as a subprocess against temporary fixture repositories with
an isolated HOME and plugin-data directory, the way the hosts run it.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PLUGIN_ROOT / "hooks" / "scripts" / "koda_hook.py"
HOOKS_JSON = PLUGIN_ROOT / "hooks" / "hooks.json"


def own_version():
    return json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]


class HookCase(unittest.TestCase):
    """Fixture repo, isolated HOME and plugin data, and a subprocess runner."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="koda-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.home = self.tmp / "home"
        self.data = self.tmp / "data"
        self.home.mkdir()
        self.repo = self.tmp / "repo"
        self.repo.mkdir()

    # -- fixtures ----------------------------------------------------------

    def git(self, *args, cwd=None):
        env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com",
                               *args], cwd=cwd or self.repo, env=env, check=True,
                              capture_output=True, text=True).stdout

    def init_repo(self, branch="main"):
        self.git("init", "-q", "-b", branch)
        (self.repo / "README.md").write_text("fixture\n")
        self.commit_all()

    def commit_all(self):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", "fixture")

    def add_change(self, change_id, status):
        folder = self.repo / "context" / "changes" / change_id
        folder.mkdir(parents=True)
        (folder / "change.md").write_text("---\nchange_id: %s\nstatus: %s\n---\n" % (change_id, status))

    def write_koda_json(self, content):
        folder = self.repo / ".rocksoft"
        folder.mkdir(exist_ok=True)
        text = content if isinstance(content, str) else json.dumps(content)
        (folder / "koda.json").write_text(text)

    def env(self, **extra):
        env = {"PATH": os.environ.get("PATH", ""), "HOME": str(self.home),
               "CLAUDE_PLUGIN_DATA": str(self.data), "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT),
               "PYTHONDONTWRITEBYTECODE": "1", "LANG": "C.UTF-8"}
        env.update(extra)
        return {k: v for k, v in env.items() if v is not None}

    def run_script(self, *args, stdin="", cwd=None, env=None):
        started = time.monotonic()
        result = subprocess.run([sys.executable, "-I", str(SCRIPT), *args], input=stdin,
                                capture_output=True, text=True, cwd=cwd or self.repo,
                                env=env if env is not None else self.env(), timeout=30)
        result.elapsed = time.monotonic() - started
        return result

    def session_start(self, event=None, **env_extra):
        event = {"cwd": str(self.repo), "source": "startup"} if event is None else event
        return self.run_script("session-start", stdin=json.dumps(event), env=self.env(**env_extra))

    def context_of(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.strip(), "expected hook output")
        payload = json.loads(result.stdout)
        self.assertNotIn("decision", payload)
        return payload["hookSpecificOutput"]["additionalContext"]


class SessionStartTests(HookCase):
    def test_map_without_open_changes(self):
        self.init_repo()
        result = self.session_start()
        text = self.context_of(result)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("Rocksoft Koda routing map", text)
        self.assertIn("Branch: main", text)
        self.assertIn("Open changes: none", text)
        self.assertIn("no open change", text)
        self.assertIn("answer normally", text)
        self.assertIn("rs-feature", text)
        self.assertIn("rs-skills:rs-orchestrator", text)
        self.assertLessEqual(len(text.splitlines()), 25)

    def test_map_with_open_changes_names_the_next_step(self):
        self.init_repo(branch="feat/login")
        self.add_change("login", "implementing")
        self.add_change("old-thing", "archived")
        text = self.context_of(self.session_start())
        self.assertIn("Branch: feat/login", text)
        self.assertIn("login (implementing)", text)
        self.assertNotIn("old-thing", text)
        self.assertIn("rs-implement login", text)

    def test_next_step_follows_status(self):
        self.init_repo()
        self.add_change("export", "implemented")
        self.assertIn("rs-impl_review export", self.context_of(self.session_start()))

    def test_mode_unset(self):
        self.init_repo()
        text = self.context_of(self.session_start())
        self.assertIn("not chosen yet", text)
        self.assertIn("record mode", text)

    def test_mode_set(self):
        self.init_repo()
        self.write_koda_json({"version": 1, "mode": "server"})
        text = self.context_of(self.session_start())
        self.assertIn("Delivery mode: server", text)
        self.assertNotIn("not chosen yet", text)

    def test_malformed_koda_json_means_unset(self):
        self.init_repo()
        self.write_koda_json("{not json")
        text = self.context_of(self.session_start())
        self.assertIn("not chosen yet", text)

    def test_unknown_mode_value_means_unset(self):
        self.init_repo()
        self.write_koda_json({"version": 1, "mode": "cloud"})
        self.assertIn("not chosen yet", self.context_of(self.session_start()))

    def test_repo_found_from_a_subdirectory(self):
        self.init_repo()
        sub = self.repo / "src" / "deep"
        sub.mkdir(parents=True)
        text = self.context_of(self.session_start({"cwd": str(sub)}))
        self.assertIn("Branch: main", text)

    def test_missing_rs_skills_is_noted_and_present_ones_are_not(self):
        self.init_repo()
        self.assertIn("no rs-* skills were detected", self.context_of(self.session_start()))
        skill = self.home / ".claude" / "plugins" / "cache" / "m" / "rs-skills" / "1.0.0" \
            / "skills" / "rs-plan"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: rs-plan\ndescription: plan\n---\n")
        self.assertNotIn("no rs-* skills were detected", self.context_of(self.session_start()))

    def test_runs_in_under_one_second(self):
        self.init_repo()
        result = self.session_start()
        self.assertLess(result.elapsed, 1.0)


class FailOpenTests(HookCase):
    def assert_silent_success(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_hooks_json_is_registered_and_fails_open(self):
        data = json.loads(HOOKS_JSON.read_text())
        hooks = data["hooks"]
        self.assertIn("SessionStart", hooks)
        self.assertIn("UserPromptSubmit", hooks)
        self.assertEqual(hooks["SessionStart"][0]["matcher"], "startup|resume")
        for event, groups in hooks.items():
            for group in groups:
                for hook in group["hooks"]:
                    self.assertLessEqual(hook["timeout"], 10, event)
                    self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/scripts/koda_hook.py", hook["command"])
                    self.assertTrue(hook["command"].endswith("2>/dev/null || true"))

    def test_garbage_stdin_never_fails(self):
        self.init_repo()
        for name in ("session-start", "prompt"):
            result = self.run_script(name, stdin="\x00 not json {{{")
            self.assertEqual(result.returncode, 0, result.stderr)
            if result.stdout:
                json.loads(result.stdout)

    def test_non_repo_cwd_is_silent(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        result = self.run_script("session-start", stdin=json.dumps({"cwd": str(outside)}),
                                 cwd=outside)
        self.assert_silent_success(result)

    def test_unknown_subcommand_is_silent(self):
        self.assert_silent_success(self.run_script("nope"))
        self.assert_silent_success(self.run_script())

    def test_forced_exception_is_silent(self):
        self.init_repo()
        for name in ("session-start", "prompt"):
            result = self.run_script(name, stdin=json.dumps({"cwd": str(self.repo), "prompt": "add x"}),
                                     env=self.env(KODA_HOOK_FAULT="raise"))
            self.assert_silent_success(result)

    def test_alarm_timeout_is_silent_and_fast(self):
        self.init_repo()
        result = self.run_script("session-start", stdin=json.dumps({"cwd": str(self.repo)}),
                                 env=self.env(KODA_HOOK_FAULT="hang", KODA_HOOK_TIMEOUT="1"))
        self.assert_silent_success(result)
        self.assertLess(result.elapsed, 5.0)

    def test_never_exits_two_or_prints_a_decision(self):
        self.init_repo()
        result = self.session_start()
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('"decision"', result.stdout)


class UpgradeReminderTests(HookCase):
    COMMAND = "codex plugin marketplace upgrade rocksoft-koda"

    def test_reminder_under_codex_when_minimum_is_newer(self):
        self.init_repo()
        self.write_koda_json({"version": 1, "minKodaVersion": "99.0.0"})
        text = self.context_of(self.session_start(PLUGIN_ROOT=str(PLUGIN_ROOT)))
        self.assertIn(self.COMMAND, text)
        self.assertIn("99.0.0", text)

    def test_no_reminder_outside_codex(self):
        self.init_repo()
        self.write_koda_json({"version": 1, "minKodaVersion": "99.0.0"})
        self.assertNotIn(self.COMMAND, self.context_of(self.session_start()))

    def test_no_reminder_when_minimum_is_not_newer(self):
        self.init_repo()
        for minimum in ("0.0.1", own_version()):
            self.write_koda_json({"version": 1, "minKodaVersion": minimum})
            text = self.context_of(self.session_start(PLUGIN_ROOT=str(PLUGIN_ROOT)))
            self.assertNotIn(self.COMMAND, text, minimum)

    def test_no_reminder_without_or_with_bad_minimum(self):
        self.init_repo()
        self.assertNotIn(self.COMMAND, self.context_of(self.session_start(PLUGIN_ROOT=str(PLUGIN_ROOT))))
        for bad in ("soon", 7, None):
            self.write_koda_json({"version": 1, "minKodaVersion": bad})
            text = self.context_of(self.session_start(PLUGIN_ROOT=str(PLUGIN_ROOT)))
            self.assertNotIn(self.COMMAND, text, repr(bad))

    def test_numeric_comparison_not_lexical(self):
        self.init_repo()
        # 0.10.0 is newer than 0.7.0 although it sorts before it as text.
        self.write_koda_json({"version": 1, "minKodaVersion": "0.10.0"})
        text = self.context_of(self.session_start(PLUGIN_ROOT=str(PLUGIN_ROOT)))
        self.assertIn(self.COMMAND, text)


class ReadOnlyTests(HookCase):
    def test_session_start_leaves_the_repo_untouched(self):
        self.init_repo()
        self.add_change("login", "planned")
        self.write_koda_json({"version": 1, "mode": "local"})
        self.commit_all()
        before = self.git("status", "--porcelain")
        self.assertEqual(before, "")
        self.session_start()
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(sorted(p.name for p in self.repo.iterdir()),
                         sorted([".git", ".rocksoft", "README.md", "context"]))

    def test_session_start_does_not_create_koda_json(self):
        self.init_repo()
        self.session_start()
        self.assertFalse((self.repo / ".rocksoft").exists())
        self.assertEqual(self.git("status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
