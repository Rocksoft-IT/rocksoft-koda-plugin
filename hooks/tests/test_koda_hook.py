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


class DoctorTests(HookCase):
    def add_rs_skill(self, name="rs-impl_review"):
        folder = (self.home / ".claude" / "plugins" / "cache" / "rocksoft" / "rs-skills"
                  / "3.2.0" / "skills" / name)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "SKILL.md").write_text("---\nname: %s\ndescription: rs skill\n---\n" % name)

    def add_repo_command(self, name, description="Run the checks"):
        folder = self.repo / ".claude" / "commands"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (name + ".md")).write_text("---\ndescription: %s\n---\nbody\n" % description)

    def state(self):
        return json.loads((self.data / "state.json").read_text())

    def test_overlap_is_reported_once_per_installed_set(self):
        self.init_repo()
        self.add_repo_command("preflight")
        self.add_rs_skill()
        first = self.context_of(self.session_start())
        self.assertEqual(first.count("Koda doctor"), 1)
        self.assertIn("preflight", first)
        self.assertIn("rs-impl_review", first)
        self.assertIn("unnamed request goes to the rs-* skill", first)
        self.assertIn("overlaps.<id>", first)
        self.assertLessEqual(len(first.splitlines()), 25)
        second = self.context_of(self.session_start())
        self.assertNotIn("Koda doctor", second)

    def test_changing_the_installed_set_triggers_the_notice_again(self):
        self.init_repo()
        self.add_repo_command("preflight")
        self.add_rs_skill()
        self.session_start()
        self.assertNotIn("Koda doctor", self.context_of(self.session_start()))
        self.add_repo_command("deploy")
        self.assertIn("Koda doctor", self.context_of(self.session_start()))
        self.assertNotIn("Koda doctor", self.context_of(self.session_start()))

    def test_no_overlap_no_notice_but_fingerprint_is_stored(self):
        self.init_repo()
        self.add_repo_command("deploy")
        self.add_rs_skill()
        self.assertNotIn("Koda doctor", self.context_of(self.session_start()))
        entries = list(self.state()["repos"].values())
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(entries[0]["fingerprint"]), 64)

    def test_overlap_needs_the_rs_skill_to_be_installed(self):
        self.init_repo()
        self.add_repo_command("preflight")
        self.assertNotIn("Koda doctor", self.context_of(self.session_start()))

    def test_rs_items_never_count_as_the_repo_side(self):
        self.init_repo()
        self.add_rs_skill("rs-impl_review")
        self.add_rs_skill("rs-plan")
        self.assertNotIn("Koda doctor", self.context_of(self.session_start()))

    def test_description_phrase_and_name_keywords_match(self):
        self.init_repo()
        self.add_rs_skill("rs-impl_review")
        self.add_rs_skill("rs-orchestrator")
        self.add_repo_command("quality-gate", "Run a code review before merge")
        self.add_repo_command("orchestrate", "Do everything")
        text = self.context_of(self.session_start())
        self.assertIn("quality-gate", text)
        self.assertIn("orchestrate", text)
        self.assertIn("rs-orchestrator", text)

    def test_unrelated_commands_do_not_overlap(self):
        self.init_repo()
        self.add_rs_skill("rs-implement")
        self.add_rs_skill("rs-impl_review")
        self.add_repo_command("build", "Build the project")
        self.add_repo_command("lint", "Lint the project")
        self.assertNotIn("Koda doctor", self.context_of(self.session_start()))

    def test_user_skills_and_other_plugins_are_scanned(self):
        self.init_repo()
        self.add_rs_skill()
        user_skill = self.home / ".claude" / "skills" / "pr-review"
        user_skill.mkdir(parents=True)
        (user_skill / "SKILL.md").write_text("---\nname: pr-review\ndescription: x\n---\n")
        self.assertIn("pr-review", self.context_of(self.session_start()))

    def test_state_is_kept_per_repository(self):
        self.init_repo()
        self.add_repo_command("preflight")
        self.add_rs_skill()
        self.session_start()
        other = self.tmp / "other"
        other.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=other, check=True)
        (other / ".claude" / "commands").mkdir(parents=True)
        (other / ".claude" / "commands" / "preflight.md").write_text("x")
        text = self.context_of(self.session_start({"cwd": str(other)}))
        self.assertIn("Koda doctor", text)


class RecordTests(HookCase):
    def record(self, *args, cwd=None):
        return self.run_script("record", *args, cwd=cwd)

    def koda_json(self):
        return json.loads((self.repo / ".rocksoft" / "koda.json").read_text())

    def test_record_mode_writes_valid_json(self):
        self.init_repo()
        result = self.record("mode", "local")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.koda_json(), {"version": 1, "mode": "local"})
        self.assertEqual(self.record("mode", "server").returncode, 0)
        self.assertEqual(self.koda_json()["mode"], "server")

    def test_record_mode_preserves_unknown_keys(self):
        self.init_repo()
        self.write_koda_json({"version": 1, "minKodaVersion": "0.9.0", "custom": {"a": 1},
                              "overlaps": {"x-vs-rs-plan": "repo"}})
        self.assertEqual(self.record("mode", "local").returncode, 0)
        data = self.koda_json()
        self.assertEqual(data["custom"], {"a": 1})
        self.assertEqual(data["minKodaVersion"], "0.9.0")
        self.assertEqual(data["overlaps"], {"x-vs-rs-plan": "repo"})
        self.assertEqual(data["mode"], "local")

    def test_record_rejects_bad_values_and_writes_nothing(self):
        self.init_repo()
        for args in (("mode", "cloud"), ("mode",), ("mode", "local", "extra"), (),
                     ("bogus",), ("choice", "a-vs-b", "maybe"), ("choice", "bad id!", "rs"),
                     ("choice", "a-vs-b"), ("choice", "a-vs-b", "rs", "--nope")):
            result = self.record(*args)
            self.assertNotEqual(result.returncode, 0, args)
            self.assertIn("usage", result.stderr, args)
        self.assertFalse((self.repo / ".rocksoft").exists())
        self.assertFalse((self.data / "state.json").exists())

    def test_record_choice_repo_goes_into_koda_json(self):
        self.init_repo()
        self.assertEqual(self.record("choice", "preflight-vs-rs-impl_review", "repo", "--repo")
                         .returncode, 0)
        self.assertEqual(self.koda_json()["overlaps"], {"preflight-vs-rs-impl_review": "repo"})
        self.assertEqual(self.koda_json()["version"], 1)

    def test_personal_choice_leaves_the_repo_clean(self):
        self.init_repo()
        self.commit_all()
        self.assertEqual(self.record("choice", "preflight-vs-rs-impl_review", "rs").returncode, 0)
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertFalse((self.repo / ".rocksoft").exists())
        entry = list(json.loads((self.data / "state.json").read_text())["repos"].values())[0]
        self.assertEqual(entry["choices"], {"preflight-vs-rs-impl_review": "rs"})

    def test_malformed_existing_file_is_refused_and_untouched(self):
        self.init_repo()
        self.write_koda_json("{broken")
        result = self.record("mode", "local")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.repo / ".rocksoft" / "koda.json").read_text(), "{broken")

    def test_record_from_a_subdirectory_writes_at_the_repo_root(self):
        self.init_repo()
        sub = self.repo / "src"
        sub.mkdir()
        self.assertEqual(self.record("mode", "server", cwd=sub).returncode, 0)
        self.assertEqual(self.koda_json()["mode"], "server")
        self.assertFalse((sub / ".rocksoft").exists())

    def test_record_outside_a_repo_fails(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        result = self.record("mode", "local", cwd=outside)
        self.assertNotEqual(result.returncode, 0)

    def test_no_temp_files_are_left_behind(self):
        self.init_repo()
        self.record("mode", "local")
        self.assertEqual([p.name for p in (self.repo / ".rocksoft").iterdir()], ["koda.json"])


class PromptTests(HookCase):
    def prompt(self, text, **env_extra):
        event = {"cwd": str(self.repo), "prompt": text, "hook_event_name": "UserPromptSubmit"}
        return self.run_script("prompt", stdin=json.dumps(event), env=self.env(**env_extra))

    def hint(self, text, **env_extra):
        return self.context_of(self.prompt(text, **env_extra))

    def assert_no_hint(self, text):
        result = self.prompt(text)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "", text)

    def add_rs_skill(self, name):
        folder = (self.home / ".claude" / "plugins" / "cache" / "rocksoft" / "rs-skills"
                  / "3.2.0" / "skills" / name)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "SKILL.md").write_text("---\nname: %s\ndescription: rs skill\n---\n" % name)

    def add_repo_command(self, name):
        folder = self.repo / ".claude" / "commands"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (name + ".md")).write_text("---\ndescription: repo command\n---\n")

    def test_unset_mode_asks_once_with_the_record_command(self):
        self.init_repo()
        text = self.hint("add a login page")
        self.assertIn("Ask the user ONCE", text)
        self.assertIn("local", text)
        self.assertIn("server", text)
        self.assertIn("record mode local|server", text)
        self.assertIn(str(SCRIPT), text)
        saved = self.run_script("record", "mode", "local")
        self.assertEqual(saved.returncode, 0, saved.stderr)
        after = self.hint("add a login page")
        self.assertNotIn("Ask the user ONCE", after)
        self.assertNotIn("record mode", after)
        self.assertIn("rs-skills:rs-orchestrator", after)

    def test_server_mode_routes_to_rs_feature_silently(self):
        self.init_repo()
        self.write_koda_json({"version": 1, "mode": "server"})
        text = self.hint("fix the invoice total rounding")
        self.assertIn("rs-feature", text)
        self.assertIn("no need to name the skill", text)
        self.assertNotIn("rs-orchestrator", text)
        self.assertNotIn("record mode", text)

    def test_local_mode_routes_to_the_orchestrator(self):
        self.init_repo()
        self.write_koda_json({"version": 1, "mode": "local"})
        text = self.hint("fix the invoice total rounding")
        self.assertIn("rs-skills:rs-orchestrator", text)
        self.assertIn("Request:", text)
        self.assertNotIn("rs-feature", text)

    def test_questions_are_not_routed(self):
        self.init_repo()
        for mode in (None, "local", "server"):
            if mode:
                self.write_koda_json({"version": 1, "mode": mode})
            for question in ("how does invoice rounding work?", "hvordan fungerer fakturaavrunding?",
                             "jak dziala zaokraglanie faktur?", "What should I add here?",
                             "why does the build fail?", "dlaczego to nie dziala?",
                             "explain the invoice flow", "thanks!", "/help", "hi"):
                self.assert_no_hint(question)

    def test_norwegian_and_polish_verbs_are_detected(self):
        self.init_repo()
        for request in ("Legg til en knapp for eksport", "fiks feilen i fakturaen",
                        "Endre fargen pa knappen", "lag en ny rapport", "fjern den gamle siden",
                        "Dodaj przycisk eksportu", "popraw zaokraglanie faktury",
                        "Zmien kolor przycisku", "napraw blad w fakturze", "usun stara strone",
                        "Stw\u00f3rz nowy raport", "Popraw zaokr\u0105glanie"):
            self.assertIn("delivery mode", self.hint(request).lower(), request)

    def test_english_verbs_and_polite_openers_are_detected(self):
        self.init_repo()
        for request in ("add X", "Fix the bug", "change the title", "implement export",
                        "build a report", "create a page", "remove the banner",
                        "update the footer", "please add a footer", "Can you fix the total?",
                        "could you remove the banner", "kan du legg til en knapp?",
                        "czy mo\u017cesz dodaj przycisk"):
            self.assertIn("Koda routing hint", self.hint(request), request)

    def test_overlap_without_choice_asks_one_question_then_remembers(self):
        self.init_repo()
        self.write_koda_json({"version": 1, "mode": "local"})
        self.add_rs_skill("rs-orchestrator")
        self.add_repo_command("orchestrate")
        first = self.hint("add a feature flag")
        self.assertEqual(first.count("Ask the user ONE question"), 1)
        self.assertIn("orchestrate", first)
        self.assertIn("rs-orchestrator", first)
        self.assertIn("record choice orchestrate-vs-rs-orchestrator rs|repo", first)
        saved = self.run_script("record", "choice", "orchestrate-vs-rs-orchestrator", "repo")
        self.assertEqual(saved.returncode, 0, saved.stderr)
        second = self.hint("add a feature flag")
        self.assertNotIn("Ask the user ONE question", second)
        self.assertIn("do not ask", second)
        self.assertIn("repo's", second)

    def test_team_choice_wins_over_a_personal_one(self):
        self.init_repo()
        self.add_rs_skill("rs-impl_review")
        self.add_repo_command("preflight")
        pair = "preflight-vs-rs-impl_review"
        self.assertEqual(self.run_script("record", "choice", pair, "repo").returncode, 0)
        self.assertEqual(self.run_script("record", "choice", pair, "rs", "--repo").returncode, 0)
        text = self.hint("review this branch")
        self.assertIn("the stored choice is rs-impl_review", text)
        self.assertNotIn("Ask the user ONE question", text)

    def test_workflow_prompt_names_the_rs_skill(self):
        self.init_repo()
        text = self.hint("review this branch")
        self.assertIn("rs-impl_review", text)
        self.assertNotIn("Ask the user ONCE", text)
        self.assertNotIn("record mode", text)

    def test_server_mode_has_no_overlap_question_for_a_change(self):
        self.init_repo()
        self.write_koda_json({"version": 1, "mode": "server"})
        self.add_rs_skill("rs-orchestrator")
        self.add_repo_command("orchestrate")
        self.assertNotIn("Ask the user ONE question", self.hint("add a feature flag"))

    def test_unset_mode_and_overlap_asks_the_mode_first(self):
        self.init_repo()
        self.add_rs_skill("rs-orchestrator")
        self.add_repo_command("orchestrate")
        text = self.hint("add a feature flag")
        self.assertIn("Ask the user ONCE", text)
        self.assertIn("If local is chosen: Two installed items", text)

    def test_output_never_blocks_or_rewrites(self):
        self.init_repo()
        result = self.prompt("add a login page")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(list(payload), ["hookSpecificOutput"])
        self.assertEqual(set(payload["hookSpecificOutput"]),
                         {"hookEventName", "additionalContext"})
        self.assertNotIn("decision", payload)

    def test_bad_input_gives_empty_output(self):
        self.init_repo()
        for stdin in ("not json", "", "[]", json.dumps({"cwd": str(self.repo)}),
                      json.dumps({"cwd": str(self.repo), "prompt": 5})):
            result = self.run_script("prompt", stdin=stdin)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "", stdin)

    def test_non_repo_cwd_gives_empty_output(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        result = self.run_script("prompt", cwd=outside,
                                 stdin=json.dumps({"cwd": str(outside), "prompt": "add x"}))
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_prompt_hook_leaves_the_repo_untouched(self):
        self.init_repo()
        self.commit_all()
        self.prompt("add a login page")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertFalse((self.repo / ".rocksoft").exists())


class ReadOnlyTests(HookCase):
    def test_session_start_leaves_the_repo_untouched(self):
        self.init_repo()
        self.add_change("login", "planned")
        self.write_koda_json({"version": 1, "mode": "local"})
        self.commit_all()
        before = self.git("status", "--porcelain")
        self.assertEqual(before, "")
        self.session_start()
        self.run_script("prompt", stdin=json.dumps({"cwd": str(self.repo), "prompt": "add x"}))
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
