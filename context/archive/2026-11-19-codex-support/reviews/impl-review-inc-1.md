<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Koda plugin works in OpenAI Codex as well as Claude

**Plan**: context/changes/codex-support/plan.md   **Scope**: increment 1 (phases 1-3, full plan)   **Date**: 2026-11-19
**Round**: 1   **Verdict**: APPROVED   **Findings**: 3

Base: `origin/main` (96d125f; local `main` ref is stale). Diff is prose and JSON only (no code files), so it was
reviewed inline without evidence subagents (rs-core §11).

## Verdicts
| Dimension | Verdict |
|---|---|
| Plan Adherence | PASS |
| Scope Discipline | PASS |
| Safety & Quality | PASS |
| Architecture | PASS (no `context/architecture/model.c4`; gate not applicable) |
| Pattern Consistency | PASS |
| Success Criteria | PASS |

## Three-way file classification
In plan and diff: `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.claude-plugin/plugin.json`,
`skills/rs-feature/SKILL.md`, `README.md`, `USAGE.md`, `docs/flow-contract.md` (one sentence),
`context/foundation/tech-stack.md`. In diff, not in plan: only `context/changes/codex-support/*` (change record).
In plan, not in diff: none. `.mcp.json` and `.claude-plugin/marketplace.json` byte-identical to base, as required.

## Success criteria (run locally in this worktree)
All 15 Automated checks of phases 1-3 re-run: PASS. Criteria written against `main` were run against
`origin/main` (same merge-base 96d125f). Codex smoke test in an isolated `CODEX_HOME` (codex-cli 0.167.2):
`codex plugin marketplace add "$PWD"`, `codex plugin add rocksoft-koda@rocksoft-koda` (installs 0.6.0),
`codex plugin list` shows installed/enabled 0.6.0, `codex mcp list` shows `rocksoft-koda` at
`mcp.rocksoft.pl/koda/`, `codex debug prompt-input hi` lists `rocksoft-koda:rs-feature`: PASS (the harmless "helper
binaries under temporary dir" warning appeared). The 3.1 version check was also confirmed per file (each of README,
USAGE and both manifests carries `0.6.0`; no `0.5.0` outside `context/`). No build or typecheck exists
(`context/foundation/tech-stack.md`); nothing SKIPPED.

Manual rows: 2.7 (diff read by this review): Steps 1-6 and Guardrails differ only in the wording the plan names
(Step 0 sign-in wording, Step 1 "tool missing" branch, one added "Not signed in" bullet under Step 6 failures); the
single confirmation, "identity never asked or sent", English issue and repo-from-Flow rules are unchanged; no sentence
makes `/mcp` the only sign-in path (SKILL.md:84, 92-93 keep it as the Claude Code path). Confirmed from diff.
Rows 1.7, 2.8, 3.6, 3.7 remain pending for a human (remote snapshot, live Codex, cloud, end to end).

## Findings
### F1 — Remote marketplace, IDE and cloud paths are documented but unexecuted
- **Severity**: OBSERVATION
- **Impact**: MEDIUM
- **Dimension**: Success Criteria
- **Location**: README.md:29-64, USAGE.md:31-57, `.agents/plugins/marketplace.json:8-11`
- **Detail**: `source: {local, "./"}` was verified only against a local marketplace root; `codex plugin marketplace add
  Rocksoft-IT/rocksoft-koda-plugin` (Git snapshot), `marketplace upgrade` + `plugin add` update flow, the IDE-extension
  path (MCP config + skill copy) and the Codex cloud admin import all rest on OpenAI documentation. Recorded in the
  plan brief as decision-to-verify; Cloud also needs mcp-gateway#26.
- **Fix**: Verify after merge (Manual 1.7, 3.6, 3.7); fallback `source: url` for a root plugin is already noted.
- **Decision**: ACCEPT — deliberate, recorded trade-off (plan-brief Key decisions / Open risks).

### F2 — Host selection for sign-in lines depends on the model judging its host
- **Severity**: OBSERVATION
- **Impact**: LOW
- **Dimension**: Safety & Quality
- **Location**: skills/rs-feature/SKILL.md:77-79
- **Detail**: "judging from the context you can see; when the host is unknown, show both" is non-deterministic but
  degrades safely: the unknown-host fallback prints all four host lines, so a user is never left without a valid path.
- **Fix**: None needed; confirm on the live Codex check (Manual 2.8).
- **Decision**: ACCEPT — safe fallback, matches plan contract.

### F3 — `allowed-tools: mcp__*` frontmatter kept for Codex
- **Severity**: OBSERVATION
- **Impact**: LOW
- **Dimension**: Plan Adherence
- **Location**: skills/rs-feature/SKILL.md (frontmatter, untouched)
- **Detail**: Codex lists the skill with the Claude-only frontmatter (verified: skill appears in prompt input) but
  not runtime-tested in a live session.
- **Fix**: Covered by Manual 2.8 / 3.7.
- **Decision**: ACCEPT — plan Key decision "SKILL.md frontmatter unchanged".

## Round 1 notes
No FIX findings; no prose fix applied. Guards: manual-pending (rows above), decision-to-verify (F1, plus the IDE,
cloud and "connect from plugin page" wording from the plan brief).
