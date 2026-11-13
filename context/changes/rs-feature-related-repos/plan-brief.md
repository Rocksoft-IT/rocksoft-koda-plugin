# Rs-feature shapes requests across related repositories — Plan Brief
Full plan: `context/changes/rs-feature-related-repos/plan.md` · issue text: `change.md`

## What & why
A request that spans several of a client's repositories (e.g. an n8n
workflow change plus the MCP gateway plus this plugin) is split by hand
today. Rocksoft-IT/n8n-hosting#130 already shipped a directory server that
can name a repository's related repositories; `rs-feature` should use that to
shape the request with full cross-repository context and end up as one
cross-linked issue per repository instead of a single issue the client has
to split themselves afterwards.

## Starting point
`rs-feature` (`skills/rs-feature/SKILL.md`) binds its whole conversation to
one repository: Step 1 picks it from `list_repositories`, Step 2 reads only
its own context, Steps 5-6 draft and create exactly one issue. Nothing in
the flow, the issue template, or `docs/flow-contract.md` knows repositories
can relate to each other.

## Desired end state
Step 2 also asks for related repositories (`include_related`) and names
them; the client confirms, once, which ones the request touches. A
multi-repository request drafts one issue per touched repository (each with
a `Related repositories` section) and creates them in a client-confirmed
deploy order — including a repository the client is not assigned to, when
it is related to one they are. `docs/flow-contract.md` and
`issue-template.md` document the new field, flag and section.

## Complexity
MEDIUM — four phases across one skill file (`SKILL.md`, at four of its six
steps) plus two reference docs; no code, no build, no tests, but several
non-obvious conversation-design decisions (confirmation semantics,
cross-link format with no edit tool, assumed external JSON shape).

## Key decisions made
| Decision | Choice | Why | Source |
|---|---|---|---|
| Skip rs-research | Yes | The issue is spec-complete (Scope + Acceptance criteria) and names the exact four SKILL.md steps and two docs to touch; `SKILL.md` was read in full directly | Jev (p=0.14) |
| Skip rs-frame | Yes | Pure feature-shape issue (no stated bug, no disputed scope) with an already-merged dependency; nothing to reframe | Jev (p=0.28) |
| Where the related-repos question lives | End of Step 2, before Step 3's track triage, independent of track | AC-01 fires "when rs-feature starts the conversation"; the question applies regardless of quick/feature/initiative, so it does not belong in any one track's budget (`references/tracks.md` untouched) | Auto |
| `get_repository_context` new shape | `include_related: true` input; optional `related_repositories: [{name, git_url, description, files, missing}]` output, absent = no relations | Symmetry with the existing documented shape; n8n-hosting#130 is an external repo not in this checkout, so the exact shape is an assumption | Auto (decision-to-verify) |
| Multi-issue confirmation | One combined "yes" for the whole batch, not per-issue | Mirrors today's single-issue Step 6 exactly; AC-02/AC-04 never ask for per-repository confirmation | Auto |
| Cross-link format | `owner/repo#<number>` for already-created siblings, name+title placeholder for not-yet-created ones, filled in deploy-order creation sequence | No tool to edit an issue after creation (Guardrail 1); this is the only way to cross-link without one | Auto |
| `create_feature_issue` relaxed targeting | `git_url` may be a `list_repositories` entry OR a named related repository; never anything else | Issue's own "Constraints & preserved behavior" bullet, AC-04 | Auto |
| Section placement | `## Related repositories` after `## Scope`, before `## Access & roles`; omitted when the touched set is one repository | Purely additive to the template; keeps scope-adjacent info together, breaks no existing section name/order | Auto |
| Version bump | `0.3.1` → `0.4.0` in `plugin.json`, mirrored into `README.md`/`USAGE.md` version footers | Project precedent: both prior archived changes bump the version (and footers) for every user-visible change | Auto |
| README/USAGE content | Version footer only, no new prose about the capability | Issue's own scope names only `docs/flow-contract.md` and `issue-template.md` for doc updates; adding prose elsewhere would be scope creep | Auto |
| Mid-batch failure handling | Stop, report created vs. not-created by link, no auto-retry | Mirrors Step 6's existing single-issue "one retry then report" philosophy | Auto |

## Scope
**In:** SKILL.md Steps 2, 5, 6; `issue-template.md`'s new section;
`docs/flow-contract.md`; version bump across three files.
**Out:** n8n-hosting#130's own server-side logic; an issue-edit tool;
`references/tracks.md`; new README/USAGE prose about the capability.

## Architecture / Approach
One increment, one area (per the orchestrator's `Areas:` block). Direct,
mechanical extension of the existing four steps plus the two docs the issue
names, same pattern the project's two prior archived changes used
(`mcp-gateway-signin`, `rename-koda-connector`).

## Increments at a glance
| # | Delivers | Depends on | User-visible | Key risk |
|---|---|---|---|---|
| 1 | Related-repositories discovery, confirmation, drafting, cross-linked creation, docs, version bump | — | yes | Assumed external JSON shape for `include_related`/`related_repositories` (decision-to-verify) |

## Phases at a glance
| Phase | Increment | Delivers | Key risk |
|---|---|---|---|
| 1 | 1 | Discover + confirm related repos (Step 2) | AC-03 regression (must behave exactly as today with no relations) |
| 2 | 1 | Cross-linked drafting (Step 5, issue-template.md) | Single-repo draft must stay unchanged |
| 3 | 1 | Deploy order + creation (Step 6) | Cross-link format with no edit tool; mid-batch failure handling |
| 4 | 1 | Contract docs + version bump | Assumed external JSON shape |

## Open risks & assumptions
- `decision-to-verify`: the exact JSON shape of `include_related` /
  `related_repositories` is assumed by symmetry with the existing
  `list_repositories` shape, since Rocksoft-IT/n8n-hosting#130 lives in a
  different repository not present in this checkout. The implementer should
  treat `docs/flow-contract.md`'s new rows as the best-available
  specification and flag any contradiction found against the live server.

## Success criteria (summary)
Grep/JSON-validity checks per phase (see `plan.md` `## Progress`) plus a
manual read-through per phase confirming the single-repository path is
byte-for-byte unchanged and the multi-repository path matches AC-01..04.
