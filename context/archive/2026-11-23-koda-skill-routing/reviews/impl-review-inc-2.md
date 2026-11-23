<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Koda skill routing — Increment 2 (Hooks, routing and docs)

**Plan**: context/changes/koda-skill-routing/plan.md   **Scope**: increment 2 (phases 3-6); last increment, full-plan verdict applies   **Date**: 2026-11-23
**Round**: 1   **Verdict**: APPROVED   **Findings**: 3

Base: `feat/koda-skill-routing/1` (diff `git diff feat/koda-skill-routing/1...HEAD`); original base fa1bde3 (local `main` is stale). Code part of the diff is one script (784 lines) plus its tests (635 lines) plus `hooks.json`: over the inline-review line threshold, but read in full by the reviewer directly and exercised with adversarial probes instead of spawning evidence subagents (Auto decision: the code is one file with one author-unit, a second reader would re-read the same 784 lines). Full-plan verdict: increment 1 is APPROVED (`impl-review-inc-1.md`), increment 2 APPROVED, so the plan is APPROVED.

## Verdicts
| Dimension | Verdict |
|---|---|
| Plan Adherence | PASS |
| Scope Discipline | PASS (one out-of-plan file, F2) |
| Safety & Quality | PASS (one low-impact edge, F1) |
| Architecture | PASS (no `context/architecture/model.c4`, gate not applicable) |
| Pattern Consistency | PASS |
| Success Criteria | PASS (Manual rows pending) |

## Success criteria (run locally)
No build step exists (tech-stack.md); nothing SKIPPED.
| Row | Result |
|---|---|
| 3.1 `hooks/hooks.json` parses, SessionStart + UserPromptSubmit, timeouts 5 s | PASS |
| 3.2-3.5 `SessionStartTests` (10), `FailOpenTests` (7), `UpgradeReminderTests` (5), `ReadOnlyTests` (2) | PASS |
| 3.6 no networking import in `koda_hook.py` | PASS |
| 4.1-4.3 `DoctorTests` (9), `RecordTests` (9), `SessionStartTests` | PASS |
| 5.1 `PromptTests` (15) | PASS |
| 5.2 full suite `python3 -m unittest discover -s hooks/tests` | PASS (57 tests OK, 6.9 s) |
| 5.3 `git status --porcelain` empty after the full run | PASS (needs `hooks/.gitignore`, F2) |
| 6.1 template contains koda@rocksoft.pl, AGENTS.md, CLAUDE.md, /hooks, .rocksoft/koda.json, client-setup.md | PASS |
| 6.2 README lost "nie czyta ani nie zapisuje plików", mentions `.rocksoft/koda.json` and `hooks/` | PASS |
| 6.3 tech-stack names Python 3 and the unittest command | PASS |
| 6.4 `git diff --quiet fa1bde3...HEAD -- skills .mcp.json docs/flow-contract.md` (main is stale) | PASS |
| 3.7, 3.8, 4.4, 5.4-5.6, 6.5 Manual | pending (host behaviour; Codex CLI hook support unconfirmed) |

Manual rows are `[ ]` in Progress, so no blind signing. Diff evidence exists for 6.5: README, USAGE and the template state what is routed, what is read, that nothing is sent, and koda@rocksoft.pl.

## Probes run by the reviewer
- Garbage stdin to `prompt`: empty stdout, exit 0.
- Question-like and request-like prompts classify as the plan says; output never carries `decision`.
- Overlap fixture (repo command + rs-impl_review in a fake plugin cache): hint asks one question and names the record command (see F1 for the edge).
- Hooks and tests leave the checkout clean; no networking import; chat paths (`skills`, `.mcp.json`, `docs/flow-contract.md`) untouched.

## Findings
### F1 — Overlap id built from the raw item name can be unrecordable and is unquoted in the hint
- **Severity**: OBSERVATION
- **Impact**: LOW
- **Dimension**: Safety & Quality
- **Location**: hooks/scripts/koda_hook.py:330 (id), :592-597 (hint), :706 (`OVERLAP_ID`)
- **Detail**: `overlap_id = "<item name>-vs-<rs skill>"` uses the name verbatim, but `record choice` validates ids against `OVERLAP_ID` (no spaces). Probe: a repo command file `my review.md` yields the id `my review-vs-rs-impl_review`, the hint prints it unquoted in a shell command, and `record choice` rejects it, so for such a name the question is never remembered. The same unsanitized name also lands in injected text and a command line; exploiting that needs a hostile skill already installed, which already has more power. Normal skill and command names (kebab-case) are unaffected.
- **Fix**: slugify the name to the `OVERLAP_ID` charset when building the id (follow-up, not blocking).
- **Decision**: ACCEPT — rare input, no data or safety impact, AC-06 holds for conventional names; recorded for a later hardening pass.

### F2 — Out-of-plan file `hooks/.gitignore`
- **Severity**: OBSERVATION
- **Impact**: LOW
- **Dimension**: Scope Discipline
- **Location**: hooks/.gitignore:1
- **Detail**: Not in the plan's file list. It ignores `__pycache__/`, which criterion 5.3 (clean `git status` after the test run) needs; the plan's "no `.gitignore`" was a current-state note, not a prohibition. Raised as an `out-of-plan-files` soft guard.
- **Fix**: none.
- **Decision**: ACCEPT — required by an Automated criterion, scoped to `hooks/`.

### F3 — Host behaviour and the release pin stay unverified
- **Severity**: OBSERVATION
- **Impact**: MEDIUM
- **Dimension**: Success Criteria
- **Location**: plan.md Progress 1.6, 1.7, 3.7, 3.8, 4.4, 5.4-5.6; .claude-plugin/marketplace.json:17, .agents/plugins/marketplace.json:24
- **Detail**: The hooks are proven by subprocess tests only; real Claude Code and Codex runs are Manual. Codex documents plugin hooks as desktop-only and never confirms the CLI (plan, Current State). Separately, the `rs-skills--v3.2.0` tag in the unpublished `Rocksoft-IT/rs-skills-dist` repository (increment 1, F1) is still unresolved: the whole 0.7.0 release depends on it.
- **Fix**: none in code; client decision on the tag, human check of the Manual rows on the preview.
- **Decision**: ACCEPT — carried as `decision-to-verify` and `manual-pending` guards and in `pr-summary.md`.

## Guards
- `decision-to-verify`: release tag `rs-skills--v3.2.0` pinned in both marketplaces but the distribution repository and tag are not published; merge only after they exist or the client names another release.
- `decision-to-verify`: Codex CLI support for plugin hooks is unconfirmed; fallback is desktop-only routing.
- `out-of-plan-files`: `hooks/.gitignore`.
- `manual-pending`: 3.7, 3.8, 4.4, 5.4, 5.5, 5.6, 6.5 (and 1.6, 1.7, 2.3 from increment 1).
