# MCP gateway sign-in — Plan Brief
Full plan: `context/changes/mcp-gateway-signin/plan.md` · issue text: `change.md`

## What & why
Issue #4: clients currently confirm a self-declared e-mail that `rs-feature`
sends unauthenticated to an n8n URL anyone with the link could call as any
client. This change points the plugin at the authenticated Rocksoft MCP
gateway (`https://mcp.rocksoft.pl/koda/`); the client signs in once via
`/mcp` with Microsoft Entra, and `rs-feature` never asks for or sends an
e-mail again.

## Starting point
`.mcp.json` → `flow.rocksoft.co/mcp/<uuid>`, no auth. `SKILL.md` Step 0 asks
for/confirms an e-mail and threads it through every later tool call.
`docs/flow-contract.md` lists `email` as a required input on all three
tools. Version `0.2.1`.

## Desired end state
`.mcp.json` → `mcp.rocksoft.pl/koda/`. No step asks for an e-mail; the
signed-in account's e-mail (from `list_repositories`) fills the issue's
`client:` metadata. Gateway denials (`pending`/`not_allowed`/`revoked`) and a
missing sign-in get plain-language handling. Docs describe Microsoft sign-in
via `/mcp`. Version `0.3.0`.

## Complexity
LOW — seven files, all documentation/config/skill-prose edits (no code, no
build, no tests per `tech-stack.md`); the issue is spec-complete (FR-001..4,
AC-01..3, explicit in/out scope) and its two open questions were already
answered by the client on the issue, so no design ambiguity remains.
Skipped: **rs-research** (Jev p=0.06 — the change is a mechanical rewrite of
named files, not an unfamiliar subsystem); **rs-frame** (not a bug shape —
the issue is a feature spec with requirements and acceptance criteria
already settled, and Jev was unsure (p=0.34) so this was decided directly).

## Key decisions made
| Decision | Choice | Why | Source |
|---|---|---|---|
| Skip rs-research | yes | mechanical rewrite of named files, well within tech-stack's no-code scope | Jev (p=0.06) |
| Skip rs-frame | yes | spec-complete feature issue (FR/AC/scope), not a bug or scope-in-doubt shape | Auto |
| Clients without Microsoft Entra | no second identity provider needed | every current Koda client already signs in via Entra through the existing gateway facade | Issue |
| E-mail vs UPN in repo directory | no remapping | directory uses exactly the sign-in address | Issue |
| claude.ai Koda connector migration | out of scope for this change | moves separately, after 0.3.0, before n8n phase 2 | Issue |
| Tenant approval logic | none to build; first sign-in creates a `pending` `mcp_tenant_access` row and waits for manual approval | exactly AC-02's existing case | Issue |
| Gateway denial shape | `{ error: "pending" \| "not_allowed" \| "revoked" }` | the issue names these three states verbatim for FR-003/AC-02 | Issue |
| Marketplace entry version bump | nothing to change | `.claude-plugin/marketplace.json` carries no `version` field at all | Auto |
| Docs stay in their existing language | Polish for README/USAGE/flow-contract.md, English for SKILL.md | rewriting a file's language is out of scope and would hide the real diff | Auto |
| Increment count | one | five scope items are one tightly coupled integration swap with no independent sub-boundary (Areas: A1) | Orchestrator |
| User-visible | yes | public auth/contract change (rs-core §1 hard-guard forcing rule) | Auto |

## Scope
In: `.mcp.json`, `skills/rs-feature/SKILL.md`, `docs/flow-contract.md`,
`README.md`, `USAGE.md`, `.claude-plugin/plugin.json`. Out: the gateway
route itself (mcp-gateway#22), n8n workflow changes (n8n-hosting#129), the
claude.ai connector's own URL switch, tracks/issue-template/conversation-flow
changes, a second identity provider.

## Architecture / Approach
Direct, mechanical edit of every place `email` is named as a client-stated
or skill-sent value, across config, the tool-contract doc, the skill's own
steps, and the client-facing docs — one increment, no code to run.

## Increments at a glance
| # | Delivers | Depends on | User-visible | Key risk |
|---|---|---|---|---|
| 1 | Gateway swap + sign-in-aware rs-feature + updated docs, v0.3.0 | — | yes | Release is gated externally on mcp-gateway#22 and n8n-hosting#129 phase 1 (not a code dependency; does not block writing or reviewing this change) |

## Phases at a glance
| Phase | Increment | Delivers | Key risk |
|---|---|---|---|
| 1 | 1 | `.mcp.json` → authenticated gateway URL | none |
| 2 | 1 | `docs/flow-contract.md` drops `email`, adds denial shapes | contract doc must match what mcp-gateway#22 actually ships (external, tracked there) |
| 3 | 1 | `SKILL.md` Steps 0/1/2/6 rewritten; denial + no-sign-in handling | none |
| 4 | 1 | README/USAGE sign-in description; version bump to 0.3.0 | none |

Prerequisites: none for writing/reviewing this change; the issue's release
constraint (Rocksoft-IT/mcp-gateway#22 deployed, n8n-hosting#129 phase 1
live) gates only when 0.3.0 is actually released.

## Open risks & assumptions
- The exact gateway denial payload shape is assumed as
  `{ error: "pending" | "not_allowed" | "revoked" }`, matching the issue's
  own wording; Rocksoft-IT/mcp-gateway#22 is the source of truth once built
  and may adjust the literal field name.

## Success criteria (summary)
A client installs 0.3.0, signs in via `/mcp`, and `rs-feature` lists their
repositories and creates an issue without ever being asked for an e-mail
(AC-01); a `pending` tenant is told to wait for approval with no issue draft
lost (AC-02); a signed-out client is told to authorize via `/mcp` (AC-03).
