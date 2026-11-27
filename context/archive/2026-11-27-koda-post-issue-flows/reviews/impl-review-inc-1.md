<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Koda post-issue flows (increment 1: status, decide, recover)

**Plan**: context/changes/koda-post-issue-flows/plan.md   **Scope**: increment 1 (phases 1-3)   **Date**: 2026-11-27
**Round**: 1   **Verdict**: APPROVED   **Findings**: 2

Base: `origin/main` (local `main` ref is stale; diff taken with `git diff origin/main...HEAD`). Documentation-only code scope (four Markdown files under `skills/rs-status/`), reviewed inline, no evidence subagents. No `context/architecture/` model, so no boundary gate. No build or test suite exists (tech-stack.md: review by reading the diff).

## Verdicts
| Dimension | Verdict |
|---|---|
| Plan Adherence | PASS |
| Scope Discipline | PASS |
| Safety & Quality | PASS |
| Architecture | PASS |
| Pattern Consistency | PASS |
| Success Criteria | PASS |

## Findings
### F1 — Feedback advertised before its flow exists
- **Severity**: OBSERVATION
- **Impact**: LOW
- **Dimension**: Plan Adherence
- **Location**: skills/rs-status/SKILL.md:9-16, 22, 50, 61
- **Detail**: The description lists feedback trigger phrases ("chcę dać opinię", "give feedback") and the title/conventions mention feedback, but the router (`SKILL.md:139-143`) has no feedback row and `references/feedback.md` does not exist. The plan puts the description phrases and the router row in Phase 4 (increment 2). Increment 2 depends on this one and merges after it, and convention 1 (confirm before write) already covers feedback, so a feedback request reaching this skill is still guarded.
- **Fix**: None needed; increment 2 (Phase 4) adds the router row and playbook.
- **Decision**: ACCEPT — closed by the stacked increment 2; no unsafe behaviour in the interim.

### F2 — Plan criteria diff against `main`, which is stale locally
- **Severity**: OBSERVATION
- **Impact**: LOW
- **Dimension**: Success Criteria
- **Location**: plan.md Phase 1-3 criteria `git diff --quiet main -- skills/rs-feature`
- **Detail**: Local `main` is behind `origin/main`; the criteria were re-run against `origin/main` and pass (no `skills/rs-feature` change in this diff).
- **Fix**: None.
- **Decision**: ACCEPT — environment artefact, verified against the real base.

## Success criteria
Automated 1.1-1.5, 2.1-2.3 (2.4), 3.1-3.3 (3.4): all PASS (commands re-run locally, `main` replaced by `origin/main`). SKILL.md frontmatter parses as YAML (`name: rs-status`, `allowed-tools: [mcp__*]`).

Manual (verified from diff text; left unchecked in Progress for the human on the PR):
- 1.6 AC-01: status flow lists "waiting for you" first with link (`references/status.md:19-28`); AC-03: refusal rule and pending/not_allowed/revoked (`SKILL.md:72-111`); AC-04: untrusted data (`SKILL.md:67-71`, `decide.md:26-30`). Handled.
- 2.5 AC-02: every write is gated by a shown block and a yes/no question (`decide.md:55-63`), edits re-ask, ambiguity sends nothing; send happens once (`decide.md:64-67`). No write precedes the explicit yes. Handled.
- 3.5 AC-03 blocked run: plain explanation (`recover.md:19-30`), no workaround for an un-resumable run (`recover.md:31-34`), confirmed single resume (`recover.md:43-52`), no retry on other ids. Handled.

## Plan checks
- Planned files = changed files (`SKILL.md`, `status.md`, `decide.md`, `recover.md`); `skills/rs-feature` untouched; no out-of-plan code files.
- Not-doing list respected: never merges, never creates issues, no tool names other than `send_feedback`, no e-mail.
- Router links all three playbooks (`SKILL.md:141-143`); skill is self-contained for the Codex IDE install (own sign-in and tenant-access text).
