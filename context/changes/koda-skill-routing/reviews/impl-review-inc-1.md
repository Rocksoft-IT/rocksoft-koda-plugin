<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Koda skill routing — Increment 1 (Distribution: rs-skills installs with Koda)

**Plan**: context/changes/koda-skill-routing/plan.md   **Scope**: increment 1 (phases 1-2)   **Date**: 2026-11-23
**Round**: 1   **Verdict**: APPROVED   **Findings**: 3

Base: fa1bde3 (commit before the plan commit 65b3cf6; local `main` ref is stale). Documentation/JSON-only diff, reviewed inline without evidence subagents; no build or test suite exists in this repo (tech-stack.md).

## Verdicts
| Dimension | Verdict |
|---|---|
| Plan Adherence | PASS |
| Scope Discipline | PASS |
| Safety & Quality | PASS |
| Architecture | PASS (no `context/architecture/model.c4`, gate not applicable) |
| Pattern Consistency | PASS |
| Success Criteria | PASS |

## Success criteria (run locally)
| Row | Result |
|---|---|
| 1.1 four JSON files parse (`python3 -m json.tool`) | PASS |
| 1.2 both manifests `0.7.0`; README.md and USAGE.md say `0.7.0`, no `0.6.0` left | PASS |
| 1.3 Claude marketplace lists rocksoft-koda + rs-skills (git-subdir, ref `rs-skills--v3.2.0`); plugin.json `dependencies: ["rs-skills"]` | PASS |
| 1.4 Codex marketplace lists both; url, source type and ref identical to Claude | PASS |
| 1.5 `git diff --quiet fa1bde3...HEAD -- skills .mcp.json docs/flow-contract.md` (main is stale; fa1bde3 used) | PASS |
| 2.1 `docs/client-setup.md` contains all required strings | PASS |
| 2.2 README links to `docs/client-setup.md` | PASS |
| 1.6, 1.7, 2.3 Manual | pending (1.6/1.7 need rs-skills#73 published) |

Files in diff outside `context/`: exactly the planned set (4 manifests, README, USAGE, docs/client-setup.md).

## Findings
### F1 — Pinned dist repo and tag cannot be resolved today
- **Severity**: OBSERVATION
- **Impact**: MEDIUM
- **Dimension**: Safety & Quality
- **Location**: .claude-plugin/marketplace.json:17, .agents/plugins/marketplace.json:24
- **Detail**: `git ls-remote` on `Rocksoft-IT/rs-skills-dist` returns "Repository not found", so per the plan's fallback rule the implementer pinned `rs-skills--v3.2.0` (the version named in rs-skills#73). Until that repo and tag exist, `rocksoft-koda` 0.7.0 declares a dependency that cannot resolve, which would also affect chat-adjacent Claude installs and updates of Koda. The plan-brief already records this risk: merge increment 1 only after the tag exists.
- **Fix**: none in code; merge gate for the human (surfaced in pr-summary and as a `decision-to-verify` guard).
- **Decision**: ACCEPT — plan-brief Key decisions "Release pin" row and Open risks.

### F2 — Setup guide mentions hooks that ship in increment 2
- **Severity**: OBSERVATION
- **Impact**: LOW
- **Dimension**: Plan Adherence
- **Location**: docs/client-setup.md:73-80
- **Detail**: "Trust the hooks" says Koda ships session hooks; `hooks/` does not exist until increment 2 (stacked on this one). The text is required by Phase 2 criterion 2.1 (`/hooks`), so it is as planned; it is only accurate once increment 2 is merged.
- **Fix**: none; merge increment 2 together with or right after this one.
- **Decision**: ACCEPT — planned content (plan Phase 2 contract); increment 2 delivers the hooks.

### F3 — JSON reformatting of unrelated lines in both plugin manifests
- **Severity**: OBSERVATION
- **Impact**: LOW
- **Dimension**: Pattern Consistency
- **Location**: .claude-plugin/plugin.json:9-15, .codex-plugin/plugin.json:9-15,23-26
- **Detail**: `keywords` and `capabilities` arrays were expanded to one item per line (json.tool output). Semantically identical, slightly noisier diff; no behaviour change.
- **Fix**: none.
- **Decision**: ACCEPT — cosmetic.

## Guards
- `decision-to-verify`: pin `rs-skills--v3.2.0` and dist repo `Rocksoft-IT/rs-skills-dist` unverified (repo not reachable); merge only after rs-skills#73 publishes the tag.
- `decision-to-verify`: Claude auto-update is documented as a settings/managed-settings field, not a manifest field.
- `manual-pending`: 1.6, 1.7, 2.3.
