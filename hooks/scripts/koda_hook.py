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
import tempfile
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
    """Names of the rs-skills items (Koda's own rs-feature does not count)."""
    return sorted({i["name"] for i in catalog
                   if i["name"].startswith("rs-") and i["name"] != "rs-feature"
                   and i["source"] != "plugin:rocksoft-koda"})


# --------------------------------------------------------------------------
# Koda doctor: overlaps between installed items and rs-* capabilities
# --------------------------------------------------------------------------

# name_tokens: whole words of the item name; name_contains: substrings of the name
# with punctuation removed; phrases: specific phrases in the description.
CAPABILITIES = {
    "orchestrate": {"rs": "rs-orchestrator",
                    "name_tokens": {"orchestrate", "orchestrator", "orchestration", "autopilot"},
                    "name_contains": [], "phrases": ["orchestrat", "autopilot"]},
    "plan": {"rs": "rs-plan",
             "name_tokens": {"plan", "planner", "planning"},
             "name_contains": [], "phrases": ["implementation plan", "write a plan"]},
    "implement": {"rs": "rs-implement",
                  "name_tokens": {"implement", "implementer", "implementation"},
                  "name_contains": [], "phrases": ["implement the plan", "implement a plan"]},
    "review": {"rs": "rs-impl_review",
               "name_tokens": {"review", "reviewer", "codereview"},
               "name_contains": ["preflight"],
               "phrases": ["code review", "review the diff", "pre-flight", "preflight"]},
    "archive": {"rs": "rs-archive",
                "name_tokens": {"archive", "archiver", "archivist", "closeout"},
                "name_contains": [], "phrases": ["archive a change", "archive the change"]},
}


def item_matches(item, spec):
    name = item["name"].lower()
    tokens = set(re.split(r"[^a-z0-9]+", name))
    squeezed = re.sub(r"[^a-z0-9]", "", name)
    if tokens & spec["name_tokens"]:
        return True
    if any(part in squeezed for part in spec["name_contains"]):
        return True
    description = item.get("description", "").lower()
    return any(phrase in description for phrase in spec["phrases"])


def find_overlaps(catalog):
    """Pairs of (repo-side item, rs-* skill) that cover the same capability."""
    installed_rs = set(rs_items(catalog))
    overlaps = []
    seen = set()
    for item in catalog:
        if is_ours(item):
            continue
        for capability, spec in CAPABILITIES.items():
            if spec["rs"] not in installed_rs or not item_matches(item, spec):
                continue
            overlap_id = "%s-vs-%s" % (item["name"], spec["rs"])
            if overlap_id in seen:
                continue
            seen.add(overlap_id)
            overlaps.append({"id": overlap_id, "capability": capability,
                             "item": item, "rs": spec["rs"]})
    return overlaps


def catalog_fingerprint(catalog):
    keys = sorted([i["kind"], i["name"], i["source"]] for i in catalog)
    return hashlib.sha256(json.dumps(keys).encode("utf-8")).hexdigest()


def doctor_notice(overlaps):
    lines = ["Koda doctor: installed skills, commands or agents overlap with Rocksoft's rs-* skills:"]
    for overlap in overlaps[:5]:
        item = overlap["item"]
        lines.append("- %s `%s` (%s) vs %s  [id: %s]"
                     % (item["kind"], item["name"], item["source"], overlap["rs"], overlap["id"]))
    if len(overlaps) > 5:
        lines.append("- and %d more" % (len(overlaps) - 5))
    lines.append("Default rule: an unnamed request goes to the rs-* skill; the repo's own command "
                 "stays available by name. A team overrides it with overlaps.<id> = \"rs\" or "
                 "\"repo\" in .rocksoft/koda.json. Mention this once, briefly; it is shown only "
                 "when the installed set changes.")
    return lines


# --------------------------------------------------------------------------
# Machine-local state (never inside the repository)
# --------------------------------------------------------------------------

def data_dir():
    for name in ("CLAUDE_PLUGIN_DATA", "PLUGIN_DATA"):
        value = os.environ.get(name)
        if value:
            return Path(value)
    cache = os.environ.get("XDG_CACHE_HOME")
    base = Path(cache) if cache else Path.home() / ".cache"
    return base / "rocksoft-koda"


def repo_key(root):
    return hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]


def load_state():
    try:
        data = json.loads((data_dir() / "state.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"repos": {}}
    if not isinstance(data, dict) or not isinstance(data.get("repos"), dict):
        return {"repos": {}}
    return data


def repo_state(state, root):
    entry = state["repos"].setdefault(repo_key(root), {})
    if not isinstance(entry, dict):
        entry = state["repos"][repo_key(root)] = {}
    return entry


def atomic_write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2)
            out.write("\n")
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def save_state(state):
    atomic_write_json(data_dir() / "state.json", state)


# --------------------------------------------------------------------------
# session-start
# --------------------------------------------------------------------------

def doctor_lines(root, catalog):
    """The overlap notice, only when the installed set changed since the last session."""
    fingerprint = catalog_fingerprint(catalog)
    state = load_state()
    entry = repo_state(state, root)
    if entry.get("fingerprint") == fingerprint:
        return []
    entry["fingerprint"] = fingerprint
    try:
        save_state(state)
    except OSError:
        pass
    overlaps = find_overlaps(catalog)
    return doctor_notice(overlaps) if overlaps else []


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
    lines += doctor_lines(root, catalog)

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


RECORD_USAGE = ("usage: koda_hook.py record mode local|server\n"
                "       koda_hook.py record choice <overlap-id> rs|repo [--repo]\n")
OVERLAP_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:~-]{0,119}$")


def record_fail(message):
    sys.stderr.write("koda_hook.py record: %s\n%s" % (message, RECORD_USAGE))
    return 1


def update_koda_json(root, mutate):
    """Read-modify-write `.rocksoft/koda.json`, keeping unknown keys; refuses a malformed file."""
    path = root / ".rocksoft" / "koda.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise ValueError("%s is not valid JSON; fix or remove it first" % path)
        if not isinstance(data, dict):
            raise ValueError("%s must hold a JSON object" % path)
    mutate(data)
    data["version"] = 1
    atomic_write_json(path, data)
    return path


def record_main(args):
    """The only writer of `.rocksoft/koda.json` and of the personal choice file."""
    try:
        if not args:
            return record_fail("missing subcommand")
        root = find_repo_root(os.getcwd())
        if args[0] == "mode":
            if len(args) != 2 or args[1] not in ("local", "server"):
                return record_fail("mode must be local or server")
            if root is None:
                return record_fail("not inside a git repository")
            value = args[1]
            path = update_koda_json(root, lambda data: data.__setitem__("mode", value))
            print("Saved delivery mode %s in %s" % (value, path))
            return 0
        if args[0] == "choice":
            flags = [a for a in args[1:] if a.startswith("--")]
            rest = [a for a in args[1:] if not a.startswith("--")]
            if any(f != "--repo" for f in flags) or len(rest) != 2:
                return record_fail("choice takes <overlap-id> rs|repo and optionally --repo")
            overlap_id, value = rest
            if not OVERLAP_ID.match(overlap_id):
                return record_fail("invalid overlap id %r" % overlap_id)
            if value not in ("rs", "repo"):
                return record_fail("choice must be rs or repo")
            if root is None:
                return record_fail("not inside a git repository")
            if flags:
                def mutate(data):
                    overlaps = data.get("overlaps")
                    if not isinstance(overlaps, dict):
                        overlaps = data["overlaps"] = {}
                    overlaps[overlap_id] = value
                path = update_koda_json(root, mutate)
                print("Saved repo-wide choice %s=%s in %s" % (overlap_id, value, path))
            else:
                state = load_state()
                entry = repo_state(state, root)
                choices = entry.get("choices")
                if not isinstance(choices, dict):
                    choices = entry["choices"] = {}
                choices[overlap_id] = value
                save_state(state)
                print("Saved personal choice %s=%s (stored outside the repository)"
                      % (overlap_id, value))
            return 0
        return record_fail("unknown subcommand %r" % args[0])
    except (OSError, ValueError) as error:
        sys.stderr.write("koda_hook.py record: %s\n" % error)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
