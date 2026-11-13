# Rs-feature shapes requests across related repositories — Implementation Plan

## Overview
Extend `rs-feature`'s conversation so a chosen repository's related
repositories (surfaced by `get_repository_context`'s new `include_related`
flag / `related_repositories` field, already shipped in
Rocksoft-IT/n8n-hosting#130) are named, their context is read, and the client
confirms which of them the request actually touches. When it touches more
than one, the skill drafts one cross-linked issue per repository, in a
client-confirmed deploy order, and creates them — including in a repository
the client is not assigned to but that is related to one they are — only
after explicit confirmation. `docs/flow-contract.md` and
`skills/rs-feature/references/issue-template.md` document the new field,
flag, and issue section.

## Current State Analysis
- `skills/rs-feature/SKILL.md:124-144` (Step 1) picks exactly one repository
  from `list_repositories`' top-level `repositories` list and never looks at
  relations between repositories.
- `skills/rs-feature/SKILL.md:146-159` (Step 2) calls
  `get_repository_context(git_url)` for that one repository only and
  summarizes only its own `CLAUDE.md` / `tech-stack.md` / `prd.md`.
- `skills/rs-feature/SKILL.md:209-226` (Step 5) drafts and prints exactly one
  issue body, from `references/issue-template.md`, for the one repository
  chosen in Step 1.
- `skills/rs-feature/SKILL.md:228-265` (Step 6) calls `create_feature_issue`
  exactly once, for that same repository, after one explicit confirmation.
- `skills/rs-feature/SKILL.md:272-274` (Guardrail 2) already states the
  repository must come from Rocksoft Flow, "no free-text repo names, no
  guessing `git_url`, no fallback repository" — a rule this change must keep
  while widening the allowed targets to related repositories.
- `skills/rs-feature/references/issue-template.md:8` names the minimum
  sections ("Summary · Scope · Acceptance criteria · Metadata") and has no
  section for related repositories; `:20-21` is the body's opening HTML
  comment (`track`/`client`/`repository`), unaffected by this change.
- `docs/flow-contract.md:43-55` documents `list_repositories` and
  `get_repository_context` with no `related_repositories` field and no
  `include_related` input; `:56-99` documents `create_feature_issue`'s
  authorization step (`:75-79`) as checking only that `git_url` belongs to
  the repositories assigned to the signed-in tenant, with no allowance for a
  related repository the tenant is not directly assigned to.
- `context/archive/2026-11-12-mcp-gateway-signin/plan.md` and
  `context/archive/2026-11-12-rename-koda-connector/plan.md` both bump
  `.claude-plugin/plugin.json`'s `version` and the matching `## Wersja`
  footers in `README.md` / `USAGE.md` for every user-visible change to the
  skill; `.claude-plugin/plugin.json` is currently at `"0.3.1"`, matching
  both footers.
- Rocksoft-IT/n8n-hosting#130 (the server-side change this depends on) is an
  external repository not present in this checkout; its exact JSON shapes
  for `include_related` / `related_repositories` are assumed by symmetry with
  the existing `list_repositories` / `get_repository_context` shapes
  documented in `docs/flow-contract.md`, not read from its source.

## Desired End State
- After Step 1 picks a repository, Step 2 also requests its related
  repositories (`include_related: true`), names any that come back, and
  reads their context; if none come back (missing field or empty list), the
  conversation behaves exactly as today (AC-03).
- The client is asked, once, which of the named related repositories (if
  any) the request touches; nothing is assumed silently (AC-01).
- When the touched set is a single repository, the flow is unchanged. When it
  is more than one, Step 5 drafts one issue body per touched repository, each
  carrying a **Related repositories** section with one line per sibling on
  what changes there, and Step 6 proposes a deploy order and creates all of
  them, in that order, only after one explicit "yes" — including a repository
  the client is not assigned to when it is related to one they are (AC-02,
  AC-04).
- `docs/flow-contract.md` documents `include_related` and
  `related_repositories`, and the relaxed `create_feature_issue`
  authorization rule. `references/issue-template.md` documents the new
  section. `.claude-plugin/plugin.json` (and the README/USAGE version
  footers) move to `0.4.0`.

### Key discoveries
- `skills/rs-feature/SKILL.md:141-144` already keeps `name` and `git_url`
  "exactly as returned" from `list_repositories` for the primary repository —
  the same discipline extends naturally to each related repository's own
  `name`/`git_url`, read once from `get_repository_context`'s response and
  never retyped by the client.
- `skills/rs-feature/SKILL.md:252-260` already has a plain-language,
  no-auto-retry failure path for a single `create_feature_issue` call
  ("Any other error: quote it, offer one retry; on a second failure fall
  back to printing the body") — the multi-issue case reuses this per issue,
  rather than inventing new retry logic.
- `docs/flow-contract.md:68` already shows the precedent for documenting a
  field the skill does not send as an argument (`email` is not an input;
  `related_repositories`/`include_related` follow the same table style).

## What we're NOT doing
- Any change inside Rocksoft-IT/n8n-hosting#130 itself (the directory
  server, the `related_repositories` data, or `create_feature_issue`'s
  authorization logic) — this plan only documents and consumes the contract
  that repo already shipped.
- Adding a tool to edit or re-link an issue after creation — cross-links are
  plain body text, written at creation time.
- New prose in `README.md` / `USAGE.md` about the related-repositories
  capability — only their version footers move, per the project's existing
  version-bump precedent; the issue's own scope names only
  `docs/flow-contract.md` and `references/issue-template.md` as the docs to
  update for content.
- Any new question playbook entry in `references/tracks.md` — the
  related-repositories question is track-independent (asked once in Step 2,
  before the track is even chosen), so it does not belong to any one track's
  budget.
- Changing the `quick` / `feature` / `initiative` track decision itself —
  multi-repository is orthogonal to how deep the conversation goes.

## Implementation Approach
A documentation/config-only plugin (`context/foundation/tech-stack.md`): no
code, no build, no tests to run. The approach is a direct extension of the
existing four steps (1, 2, 5, 6) plus the two reference docs the issue names,
following the same mechanical-edit pattern the project's two prior archived
changes used. One increment, one area (per the orchestrator's `Areas:`
block — "builds on nothing (no other area)"): discovery (Step 1-2),
drafting (Step 5 + issue-template.md), creation (Step 6), and the contract
docs + version bump are four phases of the same coherent flow change, not
independent deployables — splitting them would leave, e.g., a
`Related repositories` issue section documented before anything in SKILL.md
ever reads a related repository, or the reverse.

Two points left to the implementer as prose, not new tool arguments:
1. **Confirmation is one combined "yes"** for the whole batch of drafts, not
   one per issue — this mirrors today's single-issue Step 6 exactly and the
   issue's acceptance criteria never ask for per-repository confirmation.
2. **Cross-links are filled in creation order**: each issue's "Related
   repositories" lines cite `owner/repo#<number>` for every sibling already
   created earlier in the deploy order, and name the repository and title
   (no number yet) for siblings still to come — there is no tool to edit an
   issue after creation, so a fully-numbered cross-link set only exists once
   the last issue in the order is created, same as the project's existing
   "create once, never edit" rule (Guardrail 1: "The issue is the only
   output... never open PRs").

## Increments
| # | Name | Phases | Depends on | User-visible | Status | PR |
|---|---|---|---|---|---|---|
| 1 | Related-repositories flow | 1-4 | — | yes | in-progress | — |

## Phase 1: Discover and confirm related repositories
### Overview
Step 2 asks for related repositories alongside the primary context, names
them to the client, and asks once which of them the request touches.

### Required changes
#### 1. Load related context
- **File**: `skills/rs-feature/SKILL.md` (Step 2)
- **Goal**: Call `get_repository_context` with `include_related: true`. When
  the response carries a non-empty `related_repositories` list, read each
  entry's own context the same way as the primary repository's, and fold a
  short summary of each into the Step 2 recap ("`<name>` also relates to
  this: ..."). When the field is missing or empty, summarize only the
  primary repository exactly as today (AC-03).
- **Contract**: `get_repository_context(git_url, include_related: true)` may
  return `related_repositories: [{ name, git_url, description, files,
  missing }]` in addition to today's `repository` / `files` / `missing`;
  absence of the key, or an empty list, means no relations.

#### 2. Ask which related repositories the request touches
- **File**: `skills/rs-feature/SKILL.md` (new question at the end of Step 2,
  before Step 3's track triage; applies regardless of which track is picked
  next)
- **Goal**: If one or more related repositories were named, ask the client
  once, in plain language, which of them (if any) this request touches —
  never assume a "yes" from the mere existence of a relation. Carry the
  confirmed set forward as "touched repositories" (the primary repository
  plus any related ones confirmed). No related repositories named → skip the
  question, "touched repositories" is just the primary one.
- **Contract**: none (conversational step; no new tool call).

### Success criteria
#### Automated
- [ ] `grep -q 'include_related' skills/rs-feature/SKILL.md`
- [ ] `grep -q 'related_repositories' skills/rs-feature/SKILL.md`
- [ ] `grep -qi 'which of' skills/rs-feature/SKILL.md`
#### Manual
- [ ] A read-through of Step 2 confirms a repository with no relations (or an
      older server) produces exactly today's conversation, with no new
      question asked (AC-03)

## Phase 2: Draft cross-linked issue bodies
### Overview
`references/issue-template.md` gets a **Related repositories** section; Step
5 drafts one issue body per touched repository when there is more than one,
each carrying that section.

### Required changes
#### 1. Issue template section
- **File**: `skills/rs-feature/references/issue-template.md`
- **Goal**: Insert a `## Related repositories` section, placed after `##
  Scope` and before `## Access & roles`, used only when the touched set has
  more than one repository (omitted otherwise, per the template's existing
  "omit a section that does not apply" rule). One line per sibling
  repository: its name and one sentence on what changes there.
- **Contract**: section heading is exactly `## Related repositories`; not
  part of the "minimum for every track" list (`:8`), since most issues have
  none.

#### 2. Multi-repository drafting
- **File**: `skills/rs-feature/SKILL.md` (Step 5)
- **Goal**: When "touched repositories" (Phase 1) has more than one entry,
  draft a separate issue body per repository — each scoped to that
  repository's own slice of the work, with its own Acceptance criteria — and
  fill its `## Related repositories` section with the sibling repositories
  and what changes in each. Print all drafts together, in the proposed
  deploy order, before asking anything else, exactly as today's single-draft
  review ("Anything to add, change, or remove before I send it?").
  Single-repository requests are unaffected.
- **Contract**: no change to `create_feature_issue`'s arguments; the
  multi-issue case is several calls with the existing argument shape, one
  per drafted body (Phase 3).

### Success criteria
#### Automated
- [ ] `grep -q '## Related repositories' skills/rs-feature/references/issue-template.md`
- [ ] `grep -q 'Related repositories' skills/rs-feature/SKILL.md`
#### Manual
- [ ] A read-through confirms a single-repository request still produces
      exactly one draft with no `Related repositories` section

## Phase 3: Propose a deploy order and create cross-linked issues
### Overview
Step 6 proposes a deploy order for a multi-repository draft set and creates
every issue, in that order, after one combined confirmation — including a
repository the client is not assigned to when it is related to one they are.

### Required changes
#### 1. Deploy order and batch confirmation
- **File**: `skills/rs-feature/SKILL.md` (Step 6)
- **Goal**: When more than one issue was drafted (Phase 2), propose a deploy
  order (which repository's issue should land first, e.g. an API before its
  consumer) and reflect it back in one line; ask the existing "Shall I create
  this issue..." question once, covering the whole batch. On "yes", call
  `create_feature_issue` once per repository, strictly in that order; before
  each call, update that issue's `Related repositories` lines to cite
  `owner/repo#<number>` for every sibling already created earlier in the
  order, and the repository name and title (no number yet) for any sibling
  still to come. Print each created issue's link as it is created. A single
  touched repository keeps today's one-call behavior unchanged.
- **Contract**: `create_feature_issue(git_url, title, body, track, labels)`
  unchanged shape, called once per repository in deploy order.

#### 2. Targeting a related repository the client is not assigned to
- **File**: `skills/rs-feature/SKILL.md` (Step 6; also tighten Guardrail 2)
- **Goal**: `git_url` for a `create_feature_issue` call may be either a
  repository from `list_repositories`' own list or one of the related
  repositories named in Phase 1 — never any other `git_url` (AC-04,
  mirroring the issue's own "Constraints & preserved behavior": "Only
  repositories from `repositories` or `related_repositories` may be
  targeted; never a `git_url` the client typed in").
- **Contract**: none beyond the existing argument shape; the allowed-targets
  rule is enforced in the conversation, same place Guardrail 2 already lives.

#### 3. Mid-batch failure handling
- **File**: `skills/rs-feature/SKILL.md` (Step 6)
- **Goal**: If one of several `create_feature_issue` calls fails, stop the
  batch, report in plain language which issues were already created (with
  their links) and which were not, and do not retry the remaining ones
  automatically — the same one-retry-then-report philosophy Step 6 already
  uses for a single issue.
- **Contract**: none (conversational error path).

### Success criteria
#### Automated
- [ ] `grep -qi 'deploy order' skills/rs-feature/SKILL.md`
- [ ] `grep -q 'related_repositories' skills/rs-feature/SKILL.md`
#### Manual
- [ ] A read-through confirms a single-repository request still issues
      exactly one `create_feature_issue` call after one confirmation
      (regression check against today's Step 6)
- [ ] A read-through confirms the batch failure path names created issues by
      link and never auto-retries

## Phase 4: Document the contract and bump the version
### Overview
`docs/flow-contract.md` documents the new field, flag, and relaxed
authorization; the plugin version moves to `0.4.0`, matching the project's
existing version-bump precedent for every user-visible change.

### Required changes
#### 1. Flow contract
- **File**: `docs/flow-contract.md`
- **Goal**: Add `include_related` (boolean, optional, default false) to
  `get_repository_context`'s input; document its output may add
  `related_repositories: [{ name, git_url, description, files, missing }]`,
  present only when the repository has configured relations (absent or
  empty = no relations, matching the existing `files`/`missing` "missing
  files are normal" convention). Relax the authorization note
  (`:75-79`) for `create_feature_issue`: `git_url` may also be a related
  repository of one assigned to the signed-in tenant, not only a directly
  assigned one (Rocksoft-IT/n8n-hosting#130).
- **Contract**: documentation only; no new skill-side tool call shape beyond
  Phases 1-3.

#### 2. Version bump
- **Files**: `.claude-plugin/plugin.json`, `README.md`, `USAGE.md`
- **Goal**: Ship this change as a new version, per the project's existing
  precedent (both prior archived changes bump `plugin.json` and mirror it
  into the two `## Wersja` footers for any user-visible change).
- **Contract**: `version` field `"0.3.1"` → `"0.4.0"`; `README.md` `##
  Wersja` and `USAGE.md` `## Wersja` footer values move to `0.4.0` too.

### Success criteria
#### Automated
- [ ] `! grep -qE '\| *.include_related.* \| *string *\| *tak' docs/flow-contract.md` (documented as boolean, not required-string)
- [ ] `grep -q 'related_repositories' docs/flow-contract.md`
- [ ] `grep -qi 'include_related' docs/flow-contract.md`
- [ ] `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"` succeeds (still valid JSON)
- [ ] `grep -q '"version": "0.4.0"' .claude-plugin/plugin.json`
- [ ] `grep -q '0.4.0' README.md`
- [ ] `grep -q '0.4.0' USAGE.md`
- [ ] `! grep -q '0.3.1' .claude-plugin/plugin.json`
#### Manual
(none)

## Testing Strategy
No test suite applies (brownfield, docs/config-only plugin;
`context/foundation/tech-stack.md` `## Commands`). Verification is the
grep/JSON-validity checks above plus the manual read-throughs listed per
phase, confirming the single-repository path is unchanged and the
multi-repository path matches the acceptance criteria.

## References
- Issue: https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/5
- `change.md` (issue body verbatim, including Acceptance criteria AC-01..04)
- `context/foundation/tech-stack.md`
- Depends on (already merged): Rocksoft-IT/rocksoft-koda-plugin#4,
  Rocksoft-IT/n8n-hosting#130, Rocksoft-IT/n8n-hosting#129
- Precedent for the version-bump pattern:
  `context/archive/2026-11-12-mcp-gateway-signin/plan.md`,
  `context/archive/2026-11-12-rename-koda-connector/plan.md`

## Progress

### Phase 1: Discover and confirm related repositories
#### Automated
- [x] 1.1 `grep -q 'include_related' skills/rs-feature/SKILL.md` — eb2d353
- [x] 1.2 `grep -q 'related_repositories' skills/rs-feature/SKILL.md` — eb2d353
- [x] 1.3 `grep -qi 'which of' skills/rs-feature/SKILL.md` — eb2d353
#### Manual
- [ ] 1.4 A read-through of Step 2 confirms a repository with no relations (or an older server) produces exactly today's conversation, with no new question asked (AC-03)

### Phase 2: Draft cross-linked issue bodies
#### Automated
- [x] 2.1 `grep -q '## Related repositories' skills/rs-feature/references/issue-template.md` — b61b0e2
- [x] 2.2 `grep -q 'Related repositories' skills/rs-feature/SKILL.md` — b61b0e2
#### Manual
- [ ] 2.3 A read-through confirms a single-repository request still produces exactly one draft with no `Related repositories` section

### Phase 3: Propose a deploy order and create cross-linked issues
#### Automated
- [x] 3.1 `grep -qi 'deploy order' skills/rs-feature/SKILL.md` — 5f5e795
- [x] 3.2 `grep -q 'related_repositories' skills/rs-feature/SKILL.md` — 5f5e795
#### Manual
- [ ] 3.3 A read-through confirms a single-repository request still issues exactly one `create_feature_issue` call after one confirmation (regression check against today's Step 6)
- [ ] 3.4 A read-through confirms the batch failure path names created issues by link and never auto-retries

### Phase 4: Document the contract and bump the version
#### Automated
- [x] 4.1 `! grep -qE '\| *.include_related.* \| *string *\| *tak' docs/flow-contract.md` — 0fa7f43
- [x] 4.2 `grep -q 'related_repositories' docs/flow-contract.md` — 0fa7f43
- [x] 4.3 `grep -qi 'include_related' docs/flow-contract.md` — 0fa7f43
- [x] 4.4 `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"` succeeds — 0fa7f43
- [x] 4.5 `grep -q '"version": "0.4.0"' .claude-plugin/plugin.json` — 0fa7f43
- [x] 4.6 `grep -q '0.4.0' README.md` — 0fa7f43
- [x] 4.7 `grep -q '0.4.0' USAGE.md` — 0fa7f43
- [x] 4.8 `! grep -q '0.3.1' .claude-plugin/plugin.json` — 0fa7f43
