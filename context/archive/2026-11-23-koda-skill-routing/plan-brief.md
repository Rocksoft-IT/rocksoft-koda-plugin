# Koda skill routing — Plan Brief
Full plan: `context/changes/koda-skill-routing/plan.md` · issue text: `change.md` (issue #14)

## What & why
Client teams (Fide-Platform first) should get Rocksoft's way of working by
enabling Koda in their repo: rs-skills arrives with Koda, and Koda's hooks route
"add X / fix Y" to the right path (local rs-orchestrator or server-side
rs-feature), warn once about overlapping skills, and present Rocksoft as a
reachable partner. Chat hosts keep working as today.

## Starting point
Koda 0.6.0 is a chat-only plugin: one skill, one MCP server, two manifests and
two marketplaces, no code, no hooks, no tests (`context/foundation/tech-stack.md`).
`README.md:25` says it never reads local files. The rs-skills client packages are
not published yet (rs-skills#73 open; no `rs-skills-dist` repo or tag reachable).

## Desired end state
One install brings both plugins (Claude via dependency, Codex via both entries in
the Koda marketplace, pinned to a release tag, equal manifest versions `0.7.0`);
hooks inject a routing map, work-prompt hints, the once-asked mode
(`.rocksoft/koda.json`), a once-per-change overlap notice and a remembered
ambiguity answer, failing open; AGENTS.md template, README, USAGE and tech stack
updated.

## Complexity
HIGH — a first runtime in a Markdown/JSON repo, a new tracked schema, three host
surfaces (Claude Code, Codex CLI/desktop, chat) whose hook behaviour cannot be
exercised from here, and a distribution pin that depends on another repo's
release. Six phases in two increments, each phase small.
Skipped: rs-research (Jev p=0.54 unsure; the spec-complete issue plus two host-doc
reads during planning answered the open mechanics) and rs-frame (Jev p=0.36
unsure; the issue states observations and requirements, not a cause or a fix).

## Key decisions made
| Decision | Choice | Why | Source |
|---|---|---|---|
| Change type | Normal feature change, not a roadmap/initiative | Feature set inside the existing plugin, not a new module | Orchestrator (Jev discovery_scale p=0.08) |
| Areas | A1 Distribution; A2 Hooks, routing and docs (builds on A1) | Docs merged into the hooks area | Orchestrator |
| Increments | 2: (1) distribution, phases 1-2; (2) hooks, routing, docs, phases 3-6, stacked on 1 | Follows the areas; 4 phases in increment 2 fit the context budget | Orchestrator |
| Hook runtime | Python 3, standard library only, `python3 -I` | House palette and rs-skills hooks use Python; no dependencies; JSON handling without `jq`; Node is not in the palette | Auto |
| Hook command form | Shell-form `python3 -I "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/koda_hook.py" <event> 2>/dev/null \|\| true`, one `hooks/hooks.json` for both hosts | Codex exports `CLAUDE_PLUGIN_ROOT` for compatibility and discovers `hooks/hooks.json`; missing python3 must not error | Auto |
| Fail-open design | `\|\| true`, in-script try/except and `signal.alarm(4)`, hooks.json timeout 5 s, never exit 2, never `decision` | Only exit 2 blocks a prompt; timeouts discard output (host docs) | Issue (AC-07) |
| Project directory | Read `cwd` from stdin, not `CLAUDE_PROJECT_DIR` | Codex documents no project-dir variable | Auto |
| Who writes `.rocksoft/koda.json` | Non-hook subcommand `koda_hook.py record ...` that the injected hint tells the model to run | Hooks cannot see the answer; code-enforced schema beats a model writing JSON; hooks stay read-only | Consult |
| Where personal choices and the doctor cache live | Machine-local `state.json` under `CLAUDE_PLUGIN_DATA`/`PLUGIN_DATA` (fallback XDG cache), keyed by repo-path hash | Always untracked, no `.gitignore` step in client repos; one local store | Consult |
| `koda.json` schema | `{"version":1,"mode","overlaps":{"<id>":"rs\|repo"},"minKodaVersion"}`, all optional but `version` | Smallest shape that carries mode, repo overlap policy and the Codex reminder | Auto |
| Routing is model-decided | Keyword pre-filter (en/no/pl; questions excluded) only gates the hint; the hint asks the model to confirm intent | ADR-0001: local, no classifier; AC-04 | Issue |
| Doctor design | rs-* capability table (orchestrate, plan, implement, review, archive) vs catalog scan of the sources in the issue; fingerprint of the set stored locally; default rule: unnamed request goes to rs-*, repo command stays available by name, overridable in `overlaps.<id>` | Gives AC-05/AC-06 a deterministic base without network | Auto |
| Claude dependency form | Bare `"rs-skills"` in `plugin.json`; the tag pin lives in the marketplace entry | Bare names resolve in the same marketplace; one place to bump | Auto |
| Auto-update (FR-002) | Documented in `docs/client-setup.md` (`extraKnownMarketplaces.<name>.autoUpdate`), not a manifest field; plus a version bump per release | Claude's marketplace manifest has no such field; docs show `autoUpdate` for managed settings only | Auto (decision-to-verify) |
| Release pin | Dist repo `Rocksoft-IT/rs-skills-dist`, paths `claude` / `./codex`, `ref` `rs-skills--v<X.Y.Z>`; implementer pins the highest tag found, else `rs-skills--v3.2.0` | Tag format is what Claude's dependency resolution expects; real tag exists only after rs-skills#73 | Auto (decision-to-verify) |
| Version | `0.6.0` to `0.7.0` in both manifests, README, USAGE, in increment 1 | Precedent: new capability = minor bump; Claude auto-update is version-keyed; FR constraint of equal versions | Auto |
| Codex upgrade reminder (FR-010) | Local compare of the plugin's own version with `minKodaVersion` in tracked `koda.json`, only when `PLUGIN_ROOT` is set | No network allowed; a newer release has no other local signal | Auto (decision-to-verify) |
| rs-feature accepting questions/help | `rs-feature` unchanged; template promises only "tell Koda in chat or write to koda@rocksoft.pl" | Issue constraint "rs-feature flow unchanged" conflicts with Scope 6 wording; smaller scope wins | Auto (decision-to-verify) |
| Test strategy | stdlib `unittest` under `hooks/tests/`, subprocess runs on temp fixture repos | Repo has no test infrastructure; hooks are the first code | Auto |

## Scope
**In:** both marketplaces and plugin manifests, `docs/client-setup.md`,
`hooks/hooks.json`, `hooks/scripts/koda_hook.py`, `hooks/tests/`,
`docs/agents-md-section.md`, `README.md`, `USAGE.md`, `tech-stack.md`.
**Out:** rs-skills packaging (rs-skills#73), network calls in hooks, `rs-feature`,
MCP tools, `.mcp.json`, `docs/flow-contract.md`, Desktop/claude.ai hooks, CI.

## Architecture / Approach
Two manifests/marketplaces list two plugins; one Python script with three
subcommands (`session-start`, `prompt`, `record`) behind one `hooks.json`;
tracked team state in `.rocksoft/koda.json`, machine state in the plugin data
dir; hints are context only, the model decides and asks.

## Increments at a glance
| # | Delivers | Depends on | User-visible | Key risk |
|---|---|---|---|---|
| 1 | rs-skills listed beside Koda in both marketplaces, Claude dependency, `0.7.0`, client setup guide | — | yes | The pinned tag does not exist until rs-skills#73 ships; a missing dependency could break Koda installs |
| 2 | Hooks, mode question, doctor, ambiguity memory, AGENTS.md template, README/USAGE/tech stack | 1 | yes | Codex CLI plugin-hook support unverified; catalog scan paths of other plugins are assumptions |

## Phases at a glance
| Phase | Increment | Delivers | Key risk |
|---|---|---|---|
| 1 | 1 | Marketplace entries, dependency, version | Pin value |
| 2 | 1 | `docs/client-setup.md`, README link | `autoUpdate` scope |
| 3 | 2 | `hooks.json`, script core, session-start map, Codex reminder, tests | Fail-open on every error path |
| 4 | 2 | Doctor, once-per-set notice, `record` subcommand | Catalog scan breadth |
| 5 | 2 | Prompt hint, mode ask, ambiguity ask | Keyword classifier false positives/negatives |
| 6 | 2 | AGENTS.md template, README, USAGE, tech stack | Honest claims (no network, read-only) |
Prerequisite: rs-skills#73 published for the Manual install checks of phase 1.

## Open risks & assumptions
- decision-to-verify: pinned `rs-skills--v<X.Y.Z>` tag and dist repo location are
  unverified until rs-skills#73 publishes; a dependency that cannot resolve would
  also affect chat installs of Koda, so merge increment 1 only after the tag exists.
- decision-to-verify: auto-update through project settings is documented only for
  managed settings; the guide says so.
- decision-to-verify: Codex plugin hooks are described as desktop-only in OpenAI docs;
  Codex CLI behaviour is a Manual check. FR-010 uses a repo-set `minKodaVersion`
  because no network is allowed.
- decision-to-verify: the template does not claim rs-feature answers questions
  (issue Scope 6 wording vs the unchanged-flow constraint).
- Catalog locations of other plugins' skills in Claude and Codex are only partly
  documented; the scan skips what it cannot read and the notice lists only what it saw.

## Success criteria (summary)
AC-01..AC-07 are mapped to phases in `plan.md` Testing Strategy: manifests and
docs by Automated checks, hook behaviour by a stdlib `unittest` suite
(`python3 -m unittest discover -s hooks/tests`), host behaviour (Claude Code,
Codex, install after rs-skills#73) by Manual checks. Chat behaviour is protected
by `git diff --quiet main...HEAD -- skills .mcp.json docs/flow-contract.md`.
