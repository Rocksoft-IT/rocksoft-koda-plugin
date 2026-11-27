<!-- IMPL-REVIEW-REPORT -->
# Implementation Review: Koda post-issue flows (increment 2: feedback flow and wiring)

**Plan**: context/changes/koda-post-issue-flows/plan.md   **Scope**: increment 2 (phases 4-5)   **Date**: 2026-11-27
**Round**: 1   **Verdict**: APPROVED   **Findings**: 1

Base: `feat/koda-post-issue-flows/1` (diff `git diff feat/koda-post-issue-flows/1...HEAD`). The local `main` ref is stale; the real base is `origin/main` (`fa1bde3`). Documentation-only scope (Markdown, two JSON manifests, no code), reviewed inline, no evidence subagents. No `context/architecture/` model, so no boundary gate. No build or test suite exists (tech-stack.md: review by reading the diff).

## Verdicts
| Dimension | Verdict |
|---|---|
| Plan Adherence | PASS |
| Scope Discipline | PASS |
| Safety & Quality | PASS |
| Architecture | PASS |
| Pattern Consistency | PASS |
| Success Criteria | PASS |

## Success criteria (run locally)
- 4.1, 4.2, 4.3: PASS (feedback.md exists and names `send_feedback`, contains yes and link; router links `references/feedback.md`).
- 5.1 JSON valid: PASS. 5.2 both manifests `0.7.0`: PASS. 5.3 `0.7.0` in README/USAGE, no `0.6.0` left in README, USAGE, manifests: PASS. 5.4 `rs-status` in rs-feature, README, USAGE: PASS.
- 5.5 rs-feature diff size: PASS against `origin/main` (5 changed lines, limit 8). Against the stale local `main` the same command prints 225 because that ref predates `fa1bde3`; environment artefact, not a defect.
- Manual 4.4 (two client messages from description to sent feedback): feedback.md steps 1-3 give description, then yes; confirmed by reading. Manual 5.6 (rs-feature behaves as before apart from the closing line): the diff touches `skills/rs-feature/SKILL.md` in two places only (the added closing line after the success message, and the amended "last step" rule); flow, tools, guardrails and issue format untouched. Both stay `- [ ]` in the plan for the human on the PR.

## Plan adherence notes
- Feedback playbook matches the phase 4 contract: draft in the client's words and language right away, full text shown, one yes/no question naming the action, single `send_feedback` call with exactly the confirmed text, link printed on success, `{ error }` handled with the refusal rule and the text offered for the Rocksoft contact, no e-mail, untrusted tool output, no feature issues, no merging (`skills/rs-status/references/feedback.md`).
- Router row and description: feedback row added (`skills/rs-status/SKILL.md:144`); the trigger phrases ("chcę dać opinię", "uwagi do Koda", "give feedback") are already in the description from increment 1. Only the router changed in this increment, as the contract says.
- Docs: README and USAGE describe the second skill and four flows in Polish, structure tree, Codex IDE install lines (both folders), a troubleshooting row, version `0.7.0`. Manifests changed on the `version` line only; marketplace files and manifest descriptions untouched, as planned.
- Closes the increment-1 observation F1 (router did not yet list feedback).

## Findings
### F1 — Closing rs-status line sits inside the per-issue success message
- **Severity**: OBSERVATION
- **Impact**: LOW
- **Dimension**: Pattern Consistency
- **Location**: skills/rs-feature/SKILL.md:366-369, 397-398
- **Detail**: The new line is appended to the per-issue success template, which is printed for each issue of a batch ("Print each created issue's link as it is created"), while the amended rule says it is printed once, after the last issue of a batch. The two sentences can be reconciled by a model reading both, and the worst case is the pointer repeated per issue; no write or safety behaviour depends on it.
- **Fix**: Optionally mark the line in the template as "print once, after the last issue of a batch".
- **Decision**: ACCEPT — LOW wording ambiguity in a runtime prompt (behaviour wording, not a prose-only doc), cosmetic worst case; the plan fixed the line count at 8 and the placement as planned.
