# rs-feature hands off a request that already has an issue — Implementation Plan

## Overview
**Path**: fast
Teach `skills/rs-feature/SKILL.md` to stop, without creating a duplicate or building anything, when the request points to an issue that already exists, and say so in Guardrails.
Out of scope: new tools, labelling existing issues, any version bump.

## Key decisions
| Decision | Choice | Why | Source |
|---|---|---|---|
| Fast path gate 2 | Passes: 1 file, 1 phase, no migration, contract, dependency or security change | `skills/rs-feature/SKILL.md:98` (Initial response) and `:405` (Guardrail 1) are the only places touched | Auto |
| Research and framing | Skipped | The wanted wording is stated in the request | Auto |
| Version bump and USAGE/README | None | `git log` holds a single commit (`fa1bde3`), so no skill-text precedent for a bump; README/USAGE do not describe the Initial response | Auto |

## Increments
| # | Name | Phases | Depends on | User-visible | Status | PR |
|---|---|---|---|---|---|---|
| 1 | Hand off existing issues | 1 | — | yes | in-progress | — |

## Phase 1: Hand off existing issues
### Overview
One skill file gets an existing-issue branch in Initial response and a longer Guardrail 1.

### Required changes
#### 1. Skill text
- **File**: `skills/rs-feature/SKILL.md`
- **Goal**: a request pointing to an existing issue ends with a client-language hand-off message, no duplicate issue and no local implementation
- **Contract**: no other section, tool or label changes

### Success criteria
#### Automated
- `grep -q 'already has an issue' skills/rs-feature/SKILL.md` exits 0
- `grep -q 'never implement' skills/rs-feature/SKILL.md` exits 0
- `! git diff HEAD --  skills/rs-feature/SKILL.md | grep -q '—'` exits 0
#### Manual
- The Initial response reads as a complete outcome, not an error

## Progress

### Phase 1: Hand off existing issues
#### Automated
- [x] 1.1 `grep -q 'already has an issue' skills/rs-feature/SKILL.md` exits 0 — bd1fd2b, re-verified 800a0eb
- [x] 1.2 `grep -q 'never implement' skills/rs-feature/SKILL.md` exits 0 — bd1fd2b, re-verified 800a0eb
- [x] 1.3 `! git diff HEAD --  skills/rs-feature/SKILL.md | grep -q '—'` exits 0 — bd1fd2b, re-verified 800a0eb
#### Manual
- [ ] 1.4 The Initial response reads as a complete outcome, not an error
