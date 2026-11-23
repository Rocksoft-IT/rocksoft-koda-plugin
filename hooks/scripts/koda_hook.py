#!/usr/bin/env python3
"""Rocksoft Koda hooks for Claude Code and Codex (Python 3 standard library only).

Subcommands
  session-start   SessionStart hook: prints a short routing map as additionalContext.
  prompt          UserPromptSubmit hook: prints a routing hint for work-like prompts.
  record ...      Not a hook. The only code that writes `.rocksoft/koda.json` and the
                  machine-local choice file.

The two hooks only read local repository state and never use the network. They
fail open: any error or timeout ends in empty stdout and exit code 0, they never
print a `decision` and never exit 2, so a prompt or a session is never blocked.
The only file a hook writes is the machine-local `state.json` outside the repo.
"""
import hashlib
import json
import os
import re
import signal
import sys
import time
import unicodedata
from pathlib import Path

DEFAULT_TIMEOUT = 4
MAX_ITEMS = 600
OWN_PLUGINS = ("rs-skills", "rocksoft-koda")

NEXT_STEP = {
    "new": "rs-plan",
    "preparing": "rs-plan",
    "planned": "rs-implement",
    "implementing": "rs-implement",
    "implemented": "rs-impl_review",
    "impl_reviewed": "rs-archive",
}


class HookTimeout(BaseException):
    """Raised by the alarm handler; BaseException so nothing swallows it."""


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def script_path():
    return Path(__file__).resolve()


def plugin_root():
    return script_path().parents[2]


def own_version():
    root = plugin_root()
    for rel in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        try:
            data = json.loads((root / rel).read_text(encoding="utf-8"))
            version = data.get("version")
            if isinstance(version, str):
                return version
        except (OSError, ValueError):
            continue
    return None


def parse_version(text):
    if not isinstance(text, str):
        return None
    match = re.match(r"^\s*v?(\d+(?:\.\d+)*)", text)
    if not match:
        return None
    return tuple(int(p) for p in match.group(1).split("."))


def version_greater(a, b):
    pa, pb = parse_version(a), parse_version(b)
    if pa is None or pb is None:
        return False
    n = max(len(pa), len(pb))
    return pa + (0,) * (n - len(pa)) > pb + (0,) * (n - len(pb))


def read_text(path, limit=8192):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)
    except OSError:
        return ""


def read_frontmatter(path):
    """Return the simple `key: value` pairs of a leading --- block."""
    text = read_text(path, 4096)
    if not text.startswith("---"):
        return {}
    lines = text.split("\n")[1:]
    data = {}
    for index, line in enumerate(lines):
        if line.strip() == "---":
            break
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in (">", "|", ">-", "|-", ">+", "|+"):
            nxt = lines[index + 1] if index + 1 < len(lines) else ""
            value = nxt.strip()
        data[key] = value.strip("\"'")
    return data


def read_stdin_event():
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return {}
        raw = sys.stdin.read()
        event = json.loads(raw)
        return event if isinstance(event, dict) else {}
    except (OSError, ValueError):
        return {}


def find_repo_root(start):
    try:
        current = Path(start).resolve()
    except OSError:
        return None
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def git_branch(root):
    git = root / ".git"
    try:
        if git.is_file():
            first = read_text(git, 512).strip()
            if first.startswith("gitdir:"):
                git = (root / first.split(":", 1)[1].strip()).resolve()
        head = read_text(git / "HEAD", 512).strip()
    except OSError:
        return None
    if head.startswith("ref:"):
        ref = head.split(":", 1)[1].strip()
        return ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
    return head[:8] if head else None


def load_koda_json(root):
    """Return the tracked config dict; missing or malformed means empty."""
    try:
        data = json.loads((root / ".rocksoft" / "koda.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def config_mode(config):
    mode = config.get("mode")
    return mode if mode in ("local", "server") else None


def config_overlaps(config):
    overlaps = config.get("overlaps")
    if not isinstance(overlaps, dict):
        return {}
    return {k: v for k, v in overlaps.items() if v in ("rs", "repo")}


def config_min_version(config):
    value = config.get("minKodaVersion")
    return value if parse_version(value) is not None else None


def open_changes(root):
    """Open changes as (change_id, status), sorted by id."""
    found = []
    base = root / "context" / "changes"
    try:
        entries = sorted(p for p in base.iterdir() if p.is_dir())
    except OSError:
        return found
    for entry in entries:
        meta = entry / "change.md"
        if not meta.is_file():
            continue
        status = read_frontmatter(meta).get("status", "")
        if status == "archived":
            continue
        found.append((entry.name, status or "unknown"))
    return found


# --------------------------------------------------------------------------
# Installed catalog (skills, commands, agents)
# --------------------------------------------------------------------------

def _skill_items(directory, source):
    items = []
    try:
        entries = sorted(directory.iterdir())
    except OSError:
        return items
    for entry in entries:
        skill = entry / "SKILL.md"
        if entry.is_dir() and skill.is_file():
            meta = read_frontmatter(skill)
            items.append({"kind": "skill", "name": meta.get("name") or entry.name,
                          "source": source, "description": meta.get("description", "")})
    return items


def _markdown_items(directory, kind, source):
    items = []
    try:
        entries = sorted(directory.iterdir())
    except OSError:
        return items
    for entry in entries:
        if entry.is_file() and entry.suffix == ".md":
            meta = read_frontmatter(entry)
            items.append({"kind": kind, "name": entry.stem, "source": source,
                          "description": meta.get("description", "")})
    return items


def _tree_items(base, source):
    return (_skill_items(base / "skills", source)
            + _markdown_items(base / "commands", "command", source)
            + _markdown_items(base / "agents", "agent", source))


def build_catalog(root):
    """Every installed skill/command/agent we can see locally, deduplicated."""
    home = Path.home()
    items = []
    for host in (".claude", ".codex"):
        cache = home / host / "plugins" / "cache"
        try:
            versions = sorted(cache.glob("*/*/*"))
        except OSError:
            versions = []
        for version_dir in versions:
            if version_dir.is_dir():
                items += _tree_items(version_dir, "plugin:" + version_dir.parent.name)
    items += _skill_items(home / ".claude" / "skills", "user")
    items += _skill_items(home / ".agents" / "skills", "user")
    items += _skill_items(root / ".claude" / "skills", "repo")
    items += _markdown_items(root / ".claude" / "commands", "command", "repo")
    items += _markdown_items(root / ".claude" / "agents", "agent", "repo")
    items += _skill_items(root / ".agents" / "skills", "repo")
    seen = set()
    unique = []
    for item in items:
        key = (item["kind"], item["name"], item["source"])
        if key not in seen:
            seen.add(key)
            unique.append(item)
        if len(unique) >= MAX_ITEMS:
            break
    return unique


def is_ours(item):
    """rs-* items and Koda's own skill never count as the repo side."""
    plugin = item["source"][len("plugin:"):] if item["source"].startswith("plugin:") else ""
    return item["name"].startswith("rs-") or plugin in OWN_PLUGINS


def rs_items(catalog):
    return sorted({i["name"] for i in catalog if i["name"].startswith("rs-")})


# --------------------------------------------------------------------------
# session-start
# --------------------------------------------------------------------------

def session_start(event):
    root = find_repo_root(event.get("cwd") or os.getcwd())
    if root is None:
        return None
    config = load_koda_json(root)
    mode = config_mode(config)
    catalog = build_catalog(root)
    changes = open_changes(root)
    script = str(script_path())

    lines = ["Rocksoft Koda routing map (read from local repo state; nothing is sent anywhere):"]
    lines.append("Branch: " + (git_branch(root) or "unknown"))
    if mode:
        lines.append("Delivery mode: " + mode + " (tracked in .rocksoft/koda.json)")
    else:
        lines.append("Delivery mode: not chosen yet (asked once, on the first change request)")
    if changes:
        shown = ", ".join("%s (%s)" % c for c in changes[:5])
        extra = " and %d more" % (len(changes) - 5) if len(changes) > 5 else ""
        lines.append("Open changes: " + shown + extra)
    else:
        lines.append("Open changes: none")
    lines.append("Routing:")
    lines.append("- Change request (add, fix, change something) -> follow the delivery mode: "
                 "local = run the rs-skills:rs-orchestrator agent with `Request: <the user's words>`; "
                 "server = start the rs-feature skill (Koda builds it from an issue); "
                 "not chosen = ask the user once, then run "
                 "`python3 \"%s\" record mode local|server`." % script)
    lines.append("- Question or explanation request -> answer normally and start no change path.")
    lines.append("- Review, plan, implement or archive an existing change -> the matching rs-* "
                 "skill (rs-impl_review, rs-plan, rs-implement, rs-archive).")
    if changes:
        change_id, status = changes[0]
        step = NEXT_STEP.get(status)
        if step:
            lines.append("Next step: continue change `%s` (status %s) with %s %s."
                         % (change_id, status, step, change_id))
        else:
            lines.append("Next step: continue change `%s`; read its plan.md for the next step."
                         % change_id)
    else:
        lines.append("Next step: no open change; ask the user to describe the change they want "
                     "and route it as above.")
    if not rs_items(catalog):
        lines.append("Note: no rs-* skills were detected locally; if rs-skills is not enabled, "
                     "see docs/client-setup.md in the Koda plugin.")

    own = own_version()
    minimum = config_min_version(config)
    if os.environ.get("PLUGIN_ROOT") and minimum and own and version_greater(minimum, own):
        lines.append("Upgrade: this repo asks for Koda %s or newer (installed %s). Tell the "
                     "developer to run `codex plugin marketplace upgrade rocksoft-koda`."
                     % (minimum, own))
    return {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                   "additionalContext": "\n".join(lines)}}


# --------------------------------------------------------------------------
# Entry point: fail-open envelope
# --------------------------------------------------------------------------

HOOKS = {"session-start": session_start}


def _alarm_handler(signum, frame):
    raise HookTimeout()


def run_hook(name):
    output = None
    try:
        timeout = DEFAULT_TIMEOUT
        try:
            timeout = max(1, int(os.environ.get("KODA_HOOK_TIMEOUT", DEFAULT_TIMEOUT)))
        except ValueError:
            pass
        if hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, _alarm_handler)
            signal.alarm(timeout)
        fault = os.environ.get("KODA_HOOK_FAULT")  # test hook: simulate a crash or a hang
        if fault == "raise":
            raise RuntimeError("forced failure")
        if fault == "hang":
            time.sleep(60)
        handler = HOOKS.get(name)
        if handler is not None:
            output = handler(read_stdin_event())
    except BaseException:  # fail open: never block the session or the prompt
        output = None
    try:
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)
        if output:
            sys.stdout.write(json.dumps(output))
            sys.stdout.flush()
    except BaseException:
        pass
    sys.exit(0)


def main(argv):
    command = argv[1] if len(argv) > 1 else ""
    if command == "record":
        return record_main(argv[2:])
    run_hook(command)
    return 0


def record_main(args):  # replaced in phase 4
    sys.stderr.write("record is not available yet\n")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
