# Koda skill routing — Implementation Plan

## Overview
Enabling Koda in a client repository brings rs-skills with it, and Koda's hooks
(Claude Code and Codex) read local repo state to route work to the right
Rocksoft path: a session-start routing map, a never-blocking hint on work-like
prompts, a once-asked delivery mode in tracked `.rocksoft/koda.json`, a once-per
-change "Koda doctor" overlap notice, and a remembered answer for ambiguous
requests. A shared `AGENTS.md` section template and the README present the
workflow and Rocksoft as a reachable partner. Chat hosts and `rs-feature` stay
exactly as they are.

## Current State Analysis
- The repo has no source code: Markdown skill (`skills/rs-feature/SKILL.md`) and
  JSON manifests only (`context/foundation/tech-stack.md:11-16`). No hooks, no
  dependencies, no CI, no tests, no `.gitignore`.
- `.claude-plugin/marketplace.json:1-12` lists one plugin (`rocksoft-koda`,
  `source: ./`); `.agents/plugins/marketplace.json:1-19` lists one local entry
  with `policy` and `category`. Neither lists rs-skills.
- Both plugin manifests are `0.6.0` (`.claude-plugin/plugin.json:3`,
  `.codex-plugin/plugin.json:3`); the version also appears in `README.md:104`
  and `USAGE.md:163`. `.codex-plugin/plugin.json` sets only `skills` and
  `mcpServers`, so default hook discovery (`hooks/hooks.json`) applies.
- `README.md:25` states the plugin never reads or writes local files; that
  sentence is wrong once hooks exist and must be rewritten (issue Scope 7).
- `skills/rs-feature/SKILL.md:40-47` runs on the weakest chat host and does not
  accept "question or help" requests; the issue's partner messaging says it
  does (Scope 6). Left unchanged (constraint: rs-feature flow unchanged).
- External facts checked against host docs during planning (not verifiable from
  the repo, re-checked by the implementer where a criterion depends on them):
  - Claude `plugin.json` `dependencies` entries are `"name"`, `"name@market"` or
    `{name, marketplace, version}`; bare names resolve in the plugin's own
    marketplace. Marketplace `git-subdir` sources take `url`, `path`, `ref`, `sha`.
  - Claude `marketplace.json` has **no** `autoUpdate` field; `autoUpdate` is a
    boolean on an `extraKnownMarketplaces` entry in settings, documented for
    managed settings only.
  - Claude plugin hooks live in `hooks/hooks.json` (wrapped in a top-level
    `hooks` key), `${CLAUDE_PLUGIN_ROOT}` is substituted and exported,
    `CLAUDE_PLUGIN_DATA` survives updates; `SessionStart` and `UserPromptSubmit`
    accept `hookSpecificOutput.additionalContext`; only exit code 2 blocks a
    prompt, any other non-zero exit and a timeout let the prompt through.
  - Codex discovers `hooks/hooks.json` too, sets `PLUGIN_ROOT`/`PLUGIN_DATA` and,
    for compatibility, `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA`; stdin carries
    `cwd`, `prompt`, `source`; hooks need a one-time `/hooks` trust; the docs
    word plugin hooks as desktop-only and never confirm them in the CLI.
- `Rocksoft-IT/rs-skills#73` (the client packages) is open and no
  `rs-skills-dist` repository or tag is reachable yet, so the release tag to pin
  cannot be read from the network today.

## Desired End State
- A client project that adds the Koda marketplace and enables `rocksoft-koda`
  gets rs-skills too (Claude: dependency; Codex: both packages from the Koda
  marketplace, both enabled), both pinned to a release tag; both Koda manifests
  carry the same version.
- In Claude Code and Codex, a session start shows a short routing map and next
  step; "add/fix/legg til/popraw ..." prompts get a routing hint; questions get
  nothing; the first change request asks local vs server once and records it in
  `.rocksoft/koda.json`; overlaps are named once per installed-set change; an
  ambiguous request is asked once and remembered; any hook error or timeout
  leaves the session untouched.
- `docs/agents-md-section.md` is a ready `AGENTS.md` section (with a `CLAUDE.md`
  pointer), README and USAGE describe hooks honestly, tech-stack names the new
  runtime.

### Key discoveries
- Two host constraints shape the design: hooks cannot ask questions, only inject
  context (`additionalContext`), and a hook cannot see the user's answer; so the
  answer is persisted by a non-hook `record` subcommand the model runs.
- A single `hooks/hooks.json` serves both hosts when the command uses
  `${CLAUDE_PLUGIN_ROOT}` (Codex exports it for compatibility) and reads the
  project directory from stdin `cwd` (Codex documents no project-dir variable).
- Claude's marketplace manifest cannot switch on auto-update; FR-002 is met by
  documenting the settings entry, not by a manifest field.

## What we're NOT doing
- Building or publishing the rs-skills client packages (rs-skills#73), or
  creating tags in another repository.
- Any network call, API key or external classifier in hooks; no Jev/OpenRouter.
- Changing `rs-feature`, the MCP tools, `.mcp.json` or `docs/flow-contract.md`.
- Hooks for Claude Desktop chat, claude.ai or Codex cloud.
- Auto-writing `.gitignore`, `CLAUDE.md` or `AGENTS.md` in a client repo: the
  template is shipped, the client team adds it through a normal PR.
- A new CI pipeline.

## Implementation Approach
**Distribution (increment 1).** List `rs-skills` as a second plugin in both
marketplaces (`git-subdir` into the public distribution repo
`Rocksoft-IT/rs-skills-dist`, `claude` and `./codex` subdirectories, `ref`
pinned to a `rs-skills--v<X.Y.Z>` tag, the tag format Claude uses to resolve
dependencies). Claude `rocksoft-koda` declares the bare dependency `rs-skills`;
Codex has no dependencies, so the setup doc enables both plugins. Both manifests
move `0.6.0` to `0.7.0` so Claude's version-keyed auto-update sees the change.
Rejected: a cross-marketplace dependency (needs an allowlist, issue forbids it)
and a version range on the dependency (the pin lives in the marketplace entry,
one place for Rocksoft to bump).

**Hooks (increment 2).** One Python 3 stdlib script,
`hooks/scripts/koda_hook.py`, with subcommands `session-start`, `prompt` (the two
hooks, read-only) and `record` (not a hook; the only code that writes
`.rocksoft/koda.json`, and the personal choice file). Python matches the house
palette and rs-skills' own hook scripts, needs no dependencies and parses JSON
without `jq`; Node would add a runtime the palette does not list, Bash is poor at
JSON. The hook command is shell-form and fails open by construction:
`python3 -I "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/koda_hook.py" <event> 2>/dev/null || true`;
inside the script a top-level `try/except` and a 4 s `signal.alarm` end in
empty output and exit 0. Routing is local and model-decided: the script gathers
facts (branch, open changes and their status, mode, installed catalog) and
writes a short context text; a keyword pre-filter (English, Norwegian, Polish
verbs; question words and `?` exclude) only decides whether a hint is worth
adding, and the hint tells the model to confirm intent itself.

**State files.** Tracked, team-wide: `.rocksoft/koda.json`
`{"version":1,"mode":"local|server","overlaps":{"<id>":"rs|repo"},"minKodaVersion":"x.y.z"}`
(all but `version` optional). Machine-local, never in the repo, under
`CLAUDE_PLUGIN_DATA` / `PLUGIN_DATA` (fallback `$XDG_CACHE_HOME/rocksoft-koda`):
`state.json` keyed by a hash of the repo path, holding the last seen installed-set
fingerprint (doctor notice once) and personal choices.

**Doctor and ambiguity.** The script carries a small table of rs-* capabilities
(orchestrate, plan, implement, review, archive) with name/description keywords,
scans the catalog sources named in the issue (installed plugins' skills/commands/
agents, `~/.claude/skills`, repo `.claude/skills|commands|agents`,
`.agents/skills`), and reports an overlap as `<repo item> vs <rs skill>`. Default
resolution rule, printed with the notice: an unnamed request goes to the rs-*
skill, the repo's own command stays available by name, and a team overrides via
`overlaps.<id>` in `.rocksoft/koda.json`. When a work-like prompt hits a
capability with an overlap and neither a repo policy nor a personal choice
exists, the hint tells the model to ask one question with both options and run
`record choice`.

**Docs.** `docs/agents-md-section.md` is the single template (AGENTS.md is the
source; a three-line CLAUDE.md pointer snippet is included). `rs-feature`
stays untouched, so the partner text promises only what exists today: describe a
request to Koda in chat, or write to koda@rocksoft.pl.

## Increments
| # | Name | Phases | Depends on | User-visible | Status | PR |
|---|---|---|---|---|---|---|
| 1 | Distribution: rs-skills installs with Koda | 1-2 | — | yes | done | — |
| 2 | Hooks, routing and docs | 3-6 | 1 | yes | in-progress | — |

## Critical Implementation Details
- **Fail open, three layers.** Shell `|| true`; in-script `try/except` plus
  `signal.alarm` (skipped where `alarm` is missing); hooks.json `timeout` of 5 s.
  A hook never prints `decision`, never exits 2.
- **Read-only hooks.** `session-start` and `prompt` write only the machine-local
  `state.json`. A test runs both in a fixture git repo and asserts
  `git status --porcelain` stays empty.
- **No network.** The script imports only the standard library, none of the
  networking modules; `git` is invoked only for `rev-parse`/`status`-style local
  reads (or `.git/HEAD` is read directly).
- **Codex upgrade reminder (FR-010).** With no network, "a newer release is
  available" is read locally: when the host is Codex (`PLUGIN_ROOT` set) and
  `minKodaVersion` in tracked `.rocksoft/koda.json` is greater than this plugin's
  own `version`, the session-start text tells the developer to run
  `codex plugin marketplace upgrade rocksoft-koda`. The team bumps
  `minKodaVersion` in a PR when Rocksoft announces a release.
- **Release pin.** The real tag is unknown until rs-skills#73 publishes. The
  implementer first lists `git ls-remote --tags` of the dist repo and pins the
  highest `rs-skills--v*` tag; when the repo is not reachable it pins
  `rs-skills--v3.2.0` (the rs-skills version named in rs-skills#73) and raises a
  `decision-to-verify` guard. Both marketplaces carry the identical tag.
- **Language.** Hook text injected into the model is English (the model answers
  in the developer's language); README/USAGE stay Polish; `docs/` template is
  English with Norwegian/Polish trigger words listed.

## Phase 1: Marketplaces, dependency and version
### Overview
Both marketplaces list rs-skills next to Koda, Claude Koda depends on it, both
manifests move to `0.7.0`.

### Required changes
#### 1. Claude marketplace and manifest
- **File**: `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`
- **Goal**: list `rs-skills` as a second plugin (so the bare dependency resolves
  in this marketplace) and make `rocksoft-koda` depend on it.
- **Contract**: new entry `{name: "rs-skills", description, source: {source:
  "git-subdir", url: "https://github.com/Rocksoft-IT/rs-skills-dist.git", path:
  "claude", ref: "rs-skills--v<X.Y.Z>"}}`; `plugin.json` gains
  `"dependencies": ["rs-skills"]` and `version: "0.7.0"`; the `rocksoft-koda`
  marketplace entry is unchanged.

#### 2. Codex marketplace and manifest
- **File**: `.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json`
- **Goal**: list both packages in the Codex marketplace, same pin as Claude.
- **Contract**: second entry `{name: "rs-skills", source: {source: "git-subdir",
  url (same), path: "./codex", ref (same tag)}, policy: {installation:
  "AVAILABLE", authentication: "ON_INSTALL"}, category: "Productivity"}`;
  `version: "0.7.0"`, identical to the Claude manifest.

#### 3. Version mentions
- **File**: `README.md` (`## Wersja`), `USAGE.md` (last line)
- **Goal**: keep the documented version equal to the manifests (`0.7.0`).

### Success criteria
#### Automated
- All four manifest and marketplace JSON files parse: `for f in .claude-plugin/marketplace.json .claude-plugin/plugin.json .agents/plugins/marketplace.json .codex-plugin/plugin.json; do python3 -m json.tool "$f" >/dev/null || exit 1; done`
- Claude and Codex plugin manifests carry the same version `0.7.0`, also stated in README.md and USAGE.md
- Claude marketplace lists rocksoft-koda and rs-skills, rs-skills as git-subdir with a `rs-skills--v<X.Y.Z>` ref, and plugin.json depends on rs-skills
- Codex marketplace lists rocksoft-koda and rs-skills with the same url, git-subdir source and ref as the Claude marketplace
- Chat behaviour is preserved: `git diff --quiet main...HEAD -- skills .mcp.json docs/flow-contract.md`
#### Manual
- Once rs-skills#73 has published the distribution tag: add the marketplace in Claude Code, install `rocksoft-koda`, and see rs-* skills and agents available (AC-01)
- Once published: add the marketplace in Codex, enable both plugins, and see rs-* skills available (AC-01)

## Phase 2: Client setup guide
### Overview
Document the one-time, per-clone setup so FR-001 and FR-002 are reproducible.

### Required changes
#### 1. Client setup document
- **File**: `docs/client-setup.md` (new), `README.md` (a link in `## Instalacja` and the `## Struktura` tree)
- **Goal**: show the project-level configuration and the per-developer commands
  for both hosts, and state the auto-update caveats honestly.
- **Contract**: Claude project `.claude/settings.json` snippet with
  `extraKnownMarketplaces.rocksoft-koda` (source github
  `Rocksoft-IT/rocksoft-koda-plugin`, `autoUpdate: true`) and `enabledPlugins`
  for `rocksoft-koda@rocksoft-koda`; the note that `enabledPlugins` alone does
  not install (one install command per clone) and that `autoUpdate` is documented
  for managed settings, otherwise turned on in `/plugin`. Codex `.codex/config.toml`
  with `[plugins."rocksoft-koda@rocksoft-koda"]` and
  `[plugins."rs-skills@rocksoft-koda"]` (`enabled = true`), the
  `codex plugin marketplace add/upgrade` commands, and the `/hooks` trust step.

### Success criteria
#### Automated
- `docs/client-setup.md` exists and contains `extraKnownMarketplaces`, `autoUpdate`, `enabledPlugins`, both Codex plugin tables, `codex plugin marketplace upgrade rocksoft-koda` and `/hooks`
- README.md links to `docs/client-setup.md`
#### Manual
- A Fide developer can follow the guide on a fresh clone without naming any skill (read-through on the PR)

## Phase 3: Hook runtime and session start
### Overview
The hook entry points, fail-open envelope and the session-start routing map with
the Codex upgrade reminder.

### Required changes
#### 1. Hook registration
- **File**: `hooks/hooks.json` (new)
- **Goal**: register `SessionStart` (matcher `startup|resume`) and
  `UserPromptSubmit` for both hosts in one file.
- **Contract**: top-level `hooks` key; command hooks of the form
  `python3 -I "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/koda_hook.py" session-start 2>/dev/null || true`
  (and `prompt`), `timeout` 5.

#### 2. Script core and session start
- **File**: `hooks/scripts/koda_hook.py` (new)
- **Goal**: read the event from stdin, locate the repo root from `cwd`, collect
  local facts and print the routing map; end silently on any problem.
- **Contract**: subcommand `session-start`. Facts: branch, each
  `context/changes/*/change.md` with its `status` (open = not `archived`),
  `.rocksoft/koda.json` (mode, `minKodaVersion`; missing or malformed = unset),
  rs-* skills present in the catalog. Output: JSON
  `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":<text>}}`;
  text is under ~25 lines: intent-to-path map (change request -> mode path;
  question -> answer normally; review/plan/implement/archive -> the rs-* skill),
  the next step (continue the first open change's next rs-* step, else "describe
  the change"), the mode (or "not chosen yet"), and the Codex upgrade reminder
  when `PLUGIN_ROOT` is set and `minKodaVersion` > own version. Errors and
  timeout: empty stdout, exit 0.

#### 3. Tests
- **File**: `hooks/tests/test_koda_hook.py` (new)
- **Goal**: drive the script as a subprocess in temp fixture repos (own `HOME`,
  `CLAUDE_PLUGIN_DATA`), classes `SessionStartTests`, `FailOpenTests`,
  `UpgradeReminderTests`, `ReadOnlyTests`.
- **Contract**: covers map content with and without open changes, mode unset/set,
  malformed `koda.json`, garbage stdin, non-repo cwd, forced exception and alarm
  timeout (exit 0, empty output, AC-07), under-one-second run, no tracked-file
  change, reminder only under Codex env and only when `minKodaVersion` is newer.

### Success criteria
#### Automated
- `hooks/hooks.json` parses, declares SessionStart and UserPromptSubmit, every timeout is 10 s or less
- `python3 -m unittest discover -s hooks/tests -k SessionStartTests` passes
- `python3 -m unittest discover -s hooks/tests -k FailOpenTests` passes
- `python3 -m unittest discover -s hooks/tests -k UpgradeReminderTests` passes
- `python3 -m unittest discover -s hooks/tests -k ReadOnlyTests` passes
- Script imports no networking module: `! grep -nE '^\s*(import|from)\s+(urllib|http|socket|ssl|requests|ftplib|smtplib)' hooks/scripts/koda_hook.py`
#### Manual
- In Claude Code with the plugin installed, a new session shows the routing map and next step (AC covered by FR-003)
- In Codex CLI, after trusting the hooks in `/hooks`, the same map appears; if it does not, record that plugin hooks are desktop-only in the PR (open question in the issue)

## Phase 4: Koda doctor, record subcommand and choices
### Overview
Overlap detection reported once per installed-set change, plus the single write
path for the delivery mode and for remembered choices.

### Required changes
#### 1. Catalog and doctor
- **File**: `hooks/scripts/koda_hook.py`
- **Goal**: build the installed catalog, detect overlaps against the rs-*
  capability table, show one notice per change of the set.
- **Contract**: catalog sources as listed in the issue; each item has kind
  (skill/command/agent), name, source. Capability table: orchestrate, plan,
  implement, review, archive, with name/description keywords (for example
  `preflight`, `review` -> review; `orchestrate`, `autopilot` -> orchestrate).
  rs-* items and Koda's own skill never count as the repo side. Fingerprint =
  sha256 of the sorted `(kind, name, source)` list; `session-start` compares it
  with `state.json` for the repo, prints the notice (overlap pair, resolution
  rule, how to override) only when it differs from the stored one, then stores
  it. No overlap = no notice (the fingerprint is still stored).

#### 2. Record subcommand
- **File**: `hooks/scripts/koda_hook.py`
- **Goal**: the one writer of tracked and personal choices, validating input.
- **Contract**: `record mode local|server` writes `.rocksoft/koda.json` (creates
  directory, keeps unknown keys, `version: 1`, atomic replace);
  `record choice <overlap-id> rs|repo [--repo]` writes `overlaps.<id>` into
  `.rocksoft/koda.json` with `--repo`, else into the machine-local `state.json`;
  invalid values exit non-zero with a message and write nothing. Not a hook: its
  output and exit code never reach a prompt.

#### 3. Tests
- **File**: `hooks/tests/test_koda_hook.py`
- **Goal**: classes `DoctorTests`, `RecordTests`.
- **Contract**: AC-05 fixture (repo `.claude/commands/preflight.md` + rs-impl_review
  in a fake plugin cache): first session prints one notice naming both and the
  rule, second identical session prints no notice, adding a command re-triggers
  it; `record` writes valid JSON, preserves unknown keys, rejects bad values,
  leaves the repo clean when the choice is personal.

### Success criteria
#### Automated
- `python3 -m unittest discover -s hooks/tests -k DoctorTests` passes
- `python3 -m unittest discover -s hooks/tests -k RecordTests` passes
- `python3 -m unittest discover -s hooks/tests -k SessionStartTests` still passes
#### Manual
- On a real machine with a repo `/preflight` command and rs-impl_review installed, the first session names the overlap and the second shows nothing (AC-05)

## Phase 5: Prompt hook, mode question and ambiguity
### Overview
The `UserPromptSubmit` routing hint: work-like prompts only, mode asked once,
ambiguity asked once, nothing blocked or rewritten.

### Required changes
#### 1. Prompt classification and hint
- **File**: `hooks/scripts/koda_hook.py`
- **Goal**: add a short hint for change requests, nothing for questions.
- **Contract**: subcommand `prompt` reads `prompt` from stdin. Work-like = a
  work verb at the start or after a polite opener (add, fix, change, implement,
  build, create, remove, update; `legg til`, `fiks`, `endre`, `lag`, `fjern`;
  `dodaj`, `popraw`, `zmien`, `napraw`, `usun`, `stworz`) and not a question
  (leading how/why/what/where/can you explain, `hvordan`, `hvorfor`, `jak`,
  `dlaczego`, or a trailing `?` with no imperative verb). Output only the
  `additionalContext` JSON; no `decision`, no rewrite, exit 0 always; empty
  output for non-work prompts and on any error.
- Hint by mode: `server` -> start the `rs-feature` skill with the user's words,
  no need to name it; `local` -> run the `rs-skills:rs-orchestrator` agent with
  `Request: <prompt>`; mode unset -> ask once, with two options (local: built in
  this session; server: Koda builds it from an issue), then run
  `python3 "<abs script path>" record mode <choice>` and continue on that path.

#### 2. Ambiguity
- **File**: `hooks/scripts/koda_hook.py`
- **Goal**: ask one question per overlapping pair, then remember.
- **Contract**: when the prompt's capability (by the same keywords) has an overlap
  with no `overlaps.<id>` in `koda.json` and no personal choice, the hint adds
  one instruction: ask which of the two to use, then run `record choice`. With a
  stored choice the hint names the chosen skill and asks nothing.

#### 3. Tests
- **File**: `hooks/tests/test_koda_hook.py`
- **Goal**: class `PromptTests`.
- **Contract**: AC-02 (unset mode -> ask-once hint with the record command, then
  after `record mode` no ask), AC-03 (`server` + "fix the invoice total rounding"
  -> rs-feature hint), local mode hint, AC-04 ("how does invoice rounding work?",
  "hvordan fungerer ..?", "jak dziala ..?" -> empty output), Norwegian/Polish verbs
  detected, AC-06 (overlap without choice -> one question; after `record choice`
  none), never a `decision` key, garbage stdin -> empty output.

### Success criteria
#### Automated
- `python3 -m unittest discover -s hooks/tests -k PromptTests` passes
- `python3 -m unittest discover -s hooks/tests` passes in full
- `git status --porcelain` is empty after the full test run (hooks and tests leave the checkout clean)
#### Manual
- In Claude Code, typing "add X" in a repo without `.rocksoft/koda.json` leads the model to ask local vs server once and write the file (AC-02)
- With `mode: server`, "fix the invoice total rounding" starts rs-feature without naming it; "how does invoice rounding work?" starts nothing (AC-03, AC-04)
- The same two prompts behave the same in Codex after hooks are trusted

## Phase 6: AGENTS.md template, README, USAGE and tech stack
### Overview
Ship the shared team template and bring the user-facing docs and the stack
record in line with the new hooks.

### Required changes
#### 1. Shared AGENTS.md section
- **File**: `docs/agents-md-section.md` (new)
- **Goal**: a copy-ready `AGENTS.md` section (source of truth for Claude and
  Codex) plus the `CLAUDE.md` pointer.
- **Contract**: sections: what Koda does in this repo, the workflow (change
  request -> chosen mode path; questions answered normally), one-time install
  steps per host (pointing to `docs/client-setup.md`, the `/hooks` trust in
  Codex, the per-clone install), `.rocksoft/koda.json` fields (`mode`,
  `overlaps`, `minKodaVersion`), promoting rs-* skills, Rocksoft as a partner
  available at any time through Koda in chat or at koda@rocksoft.pl (no claim
  that rs-feature handles questions), and a `CLAUDE.md` snippet that points to
  `AGENTS.md` (no import syntax assumed).

#### 2. README, USAGE and tech stack
- **File**: `README.md`, `USAGE.md`, `context/foundation/tech-stack.md`
- **Goal**: replace the "never reads local files" claim; describe hooks,
  `.rocksoft/koda.json`, the doctor, the template and the repo layout; record
  Python 3 (stdlib only) and the test command.
- **Contract**: README (Polish): in chat the plugin works only through Rocksoft
  Flow; in Claude Code and Codex the hooks read local repo state to pick the
  skill, send nothing and change no code (the only writes are `.rocksoft/koda.json`
  after the user answers and local cache files outside the repo); the Codex
  hooks need `/hooks` trust; the `## Struktura` tree lists `hooks/` and the new
  docs. USAGE: a short section on routing and the mode question. Tech stack:
  `## Languages & Runtimes` names Python 3 stdlib for hook scripts only,
  `## Commands` lists `python3 -m unittest discover -s hooks/tests`, `updated`
  bumped.

### Success criteria
#### Automated
- `docs/agents-md-section.md` exists and contains `koda@rocksoft.pl`, `AGENTS.md`, `CLAUDE.md`, `/hooks`, `.rocksoft/koda.json` and `client-setup.md`
- README.md no longer says the plugin never reads local files (`! grep -q 'nie czyta ani nie zapisuje plików' README.md`) and mentions `.rocksoft/koda.json` and `hooks/`
- `context/foundation/tech-stack.md` names Python 3 and the `unittest` command
- Chat behaviour is preserved: `git diff --quiet main...HEAD -- skills .mcp.json docs/flow-contract.md`
#### Manual
- A client reader understands from README and the template which prompts are routed, what is read locally, that nothing is sent, and whom to contact

## Testing Strategy
No test infrastructure exists, so phase 3 adds a stdlib `unittest` suite for the
script (subprocess runs against temp fixture repos with an isolated `HOME` and
plugin-data directory). Manifests are checked with short Python assertions in the
Automated criteria. Host behaviour (Claude Code, Codex CLI, Desktop) is Manual.

| Acceptance criterion | Covered by |
|---|---|
| AC-01 one install | Phase 1 (structure, Automated; install, Manual after rs-skills#73) |
| AC-02 first request asks mode | Phase 5 `PromptTests`, Phase 4 `RecordTests` |
| AC-03 saved mode routes silently | Phase 5 `PromptTests` |
| AC-04 questions not routed | Phase 5 `PromptTests` |
| AC-05 overlap once | Phase 4 `DoctorTests` |
| AC-06 ambiguity once | Phase 5 `PromptTests`, Phase 4 `RecordTests` |
| AC-07 hook failure harmless | Phase 3 `FailOpenTests` |

## Performance Notes
Session start only reads a few small files and directory listings and runs no
subprocess that touches the network; the test asserts under one second and the
hook `timeout` is 5 s.

## References
- Issue: https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/14 (`change.md`)
- rs-skills client packages: Rocksoft-IT/rs-skills#73
- Existing files: `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json`, `README.md:25`, `context/foundation/tech-stack.md`
- Prior change: `context/archive/2026-11-19-codex-support/plan.md` (manifest and marketplace precedent)

## Progress

### Phase 1: Marketplaces, dependency and version
#### Automated
- [x] 1.1 All four manifest and marketplace JSON files parse — efec016
- [x] 1.2 Claude and Codex plugin manifests carry the same version 0.7.0, also stated in README.md and USAGE.md — efec016
- [x] 1.3 Claude marketplace lists rocksoft-koda and rs-skills, rs-skills as git-subdir with a rs-skills--v<X.Y.Z> ref, and plugin.json depends on rs-skills — efec016
- [x] 1.4 Codex marketplace lists rocksoft-koda and rs-skills with the same url, git-subdir source and ref as the Claude marketplace — efec016
- [x] 1.5 Chat behaviour is preserved: git diff --quiet main...HEAD -- skills .mcp.json docs/flow-contract.md — efec016
#### Manual
- [ ] 1.6 Once rs-skills#73 has published the distribution tag: add the marketplace in Claude Code, install rocksoft-koda, and see rs-* skills and agents available (AC-01)
- [ ] 1.7 Once published: add the marketplace in Codex, enable both plugins, and see rs-* skills available (AC-01)

### Phase 2: Client setup guide
#### Automated
- [x] 2.1 docs/client-setup.md exists and contains extraKnownMarketplaces, autoUpdate, enabledPlugins, both Codex plugin tables, the marketplace upgrade command and /hooks — 5984e53
- [x] 2.2 README.md links to docs/client-setup.md — 5984e53
#### Manual
- [ ] 2.3 A Fide developer can follow the guide on a fresh clone without naming any skill (read-through on the PR)

### Phase 3: Hook runtime and session start
#### Automated
- [ ] 3.1 hooks/hooks.json parses, declares SessionStart and UserPromptSubmit, every timeout is 10 s or less
- [ ] 3.2 SessionStartTests pass: python3 -m unittest discover -s hooks/tests -k SessionStartTests
- [ ] 3.3 FailOpenTests pass: python3 -m unittest discover -s hooks/tests -k FailOpenTests
- [ ] 3.4 UpgradeReminderTests pass: python3 -m unittest discover -s hooks/tests -k UpgradeReminderTests
- [ ] 3.5 ReadOnlyTests pass: python3 -m unittest discover -s hooks/tests -k ReadOnlyTests
- [ ] 3.6 Script imports no networking module
#### Manual
- [ ] 3.7 In Claude Code with the plugin installed, a new session shows the routing map and next step
- [ ] 3.8 In Codex CLI, after trusting the hooks in /hooks, the same map appears, or the PR records that plugin hooks are desktop-only

### Phase 4: Koda doctor, record subcommand and choices
#### Automated
- [ ] 4.1 DoctorTests pass: python3 -m unittest discover -s hooks/tests -k DoctorTests
- [ ] 4.2 RecordTests pass: python3 -m unittest discover -s hooks/tests -k RecordTests
- [ ] 4.3 SessionStartTests still pass
#### Manual
- [ ] 4.4 On a real machine with a repo /preflight command and rs-impl_review installed, the first session names the overlap and the second shows nothing (AC-05)

### Phase 5: Prompt hook, mode question and ambiguity
#### Automated
- [ ] 5.1 PromptTests pass: python3 -m unittest discover -s hooks/tests -k PromptTests
- [ ] 5.2 The full suite passes: python3 -m unittest discover -s hooks/tests
- [ ] 5.3 git status --porcelain is empty after the full test run
#### Manual
- [ ] 5.4 In Claude Code, typing "add X" in a repo without .rocksoft/koda.json leads the model to ask local vs server once and write the file (AC-02)
- [ ] 5.5 With mode server, "fix the invoice total rounding" starts rs-feature without naming it, and "how does invoice rounding work?" starts nothing (AC-03, AC-04)
- [ ] 5.6 The same two prompts behave the same in Codex after hooks are trusted

### Phase 6: AGENTS.md template, README, USAGE and tech stack
#### Automated
- [ ] 6.1 docs/agents-md-section.md exists and contains koda@rocksoft.pl, AGENTS.md, CLAUDE.md, /hooks, .rocksoft/koda.json and client-setup.md
- [ ] 6.2 README.md no longer says the plugin never reads local files and mentions .rocksoft/koda.json and hooks/
- [ ] 6.3 context/foundation/tech-stack.md names Python 3 and the unittest command
- [ ] 6.4 Chat behaviour is preserved: git diff --quiet main...HEAD -- skills .mcp.json docs/flow-contract.md
#### Manual
- [ ] 6.5 A client reader understands from README and the template which prompts are routed, what is read locally, that nothing is sent, and whom to contact
