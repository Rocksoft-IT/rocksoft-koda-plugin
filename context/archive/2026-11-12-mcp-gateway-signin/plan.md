# MCP gateway sign-in — Implementation Plan

## Overview
Switch `rocksoft-koda` from the unauthenticated n8n MCP endpoint to the
authenticated Rocksoft MCP gateway (`https://mcp.rocksoft.pl/koda/`), so a
client signs in once via `/mcp` with their Microsoft work account instead of
typing an e-mail Rocksoft Flow could not verify. `rs-feature` stops asking for
or sending `email`; the gateway injects the verified identity, and the skill
handles the gateway's tenant-access denials and a missing sign-in in plain
language. Version bumps to `0.3.0`.

## Current State Analysis
- `.mcp.json:1-7` points `rocksoft-mcp` at
  `https://flow.rocksoft.co/mcp/0b5ef84b-ec12-4d2b-a066-f10ebc2c0643` with no
  auth; anyone with the URL can call the tools as any client e-mail.
- `skills/rs-feature/SKILL.md` Step 0 ("Identify the client (interim:
  confirmed e-mail)") asks for or confirms an e-mail and keeps it "for every
  later tool call"; Step 1 calls `list_repositories` with the e-mail and its
  "None" branch names `<email>` in the stop message; Step 2 calls
  `get_repository_context` "with the `git_url` (and the e-mail)"; Step 6
  sends `email` as one of the `create_feature_issue` arguments.
- `docs/flow-contract.md` (Polish) documents `email` as a required input of
  all three tools and notes (line 29) it is "w fazie 0 deklarowany przez
  klienta; docelowo wstrzykiwany przez proxy OAuth" (self-declared today;
  eventually injected by an OAuth proxy) — this change is that "docelowo".
  It defines no error shape for a tenant that is not yet approved.
- `README.md` and `USAGE.md` (Polish) describe the e-mail step and, in
  README's "Plan rozwoju", point at issue #1 (OAuth proxy) as future work.
  Both end with a `## Wersja` / version line reading `0.2.0`.
- `.claude-plugin/plugin.json` `version` is `0.2.1`.
  `.claude-plugin/marketplace.json` carries no `version` field at all (only
  `name`, `owner`, `plugins[].{name,source,description}`) — there is nothing
  to bump there.
- `skills/rs-feature/references/issue-template.md` keeps a `<email>` metadata
  placeholder (lines 21, 122); out of scope (issue scope list does not name
  it) — the placeholder's *source* changes (gateway-verified instead of
  self-declared) but the template field itself is unaffected.

## Desired End State
- `.mcp.json` points at `https://mcp.rocksoft.pl/koda/`; the client's Claude
  session handles the Microsoft Entra OAuth dance via `/mcp`, no header or
  secret in the repo.
- `rs-feature` never asks for or sends an e-mail. It calls `list_repositories`
  / `get_repository_context` / `create_feature_issue` without an `email`
  argument, reads the signed-in client's e-mail from `list_repositories`'
  response for the issue's `client:` metadata, and handles three gateway
  outcomes in plain language: no sign-in at all (tell the client to authorize
  Rocksoft Koda via `/mcp`), a `pending` tenant (access waits for Rocksoft
  approval; the drafted issue is printed for handover, never lost), and
  `not_allowed`/`revoked` (contact your Rocksoft contact).
- `docs/flow-contract.md` documents `email` as gateway-injected, not a tool
  input, and documents the tenant-access denial shape.
- `README.md` / `USAGE.md` describe signing in with a Microsoft work account
  via `/mcp` (no client ID/secret) and that access needs Rocksoft approval.
- `.claude-plugin/plugin.json` `version` is `0.3.0`.

### Key discoveries
- `.mcp.json:4` — the whole swap is a one-line `url` change plus dropping the
  (already-absent) `headers` block; OAuth is handled client-side, nothing to
  configure in this JSON file.
- `skills/rs-feature/SKILL.md:88-100` (Step 0), `:113-121` (Step 1 incl.
  "None"), `:123-131` (Step 2), `:205-216` (Step 6) are every place `email`
  is read, asked for, or sent.
- `docs/flow-contract.md:29` already names the end state ("docelowo
  wstrzykiwany przez proxy OAuth") — this plan fulfils that note rather than
  inventing a new direction.
- `.claude-plugin/marketplace.json` has no `version` key (verified by reading
  the whole file) — the "and the marketplace entry" clause of the issue has
  nothing to act on for a version bump.

## What we're NOT doing
- The gateway route itself (Rocksoft-IT/mcp-gateway#22) and the n8n workflow
  changes (Rocksoft-IT/n8n-hosting#129) — external services this plugin only
  calls.
- Any change to tracks, the issue template, or the conversation flow beyond
  Step 0/1/2/6's identity handling.
- Moving the claude.ai Koda connector to the new URL — done separately, after
  this plugin's 0.3.0 release (per the client's comment on the issue).
- A second identity provider for clients without Microsoft Entra — the
  client confirmed every current Koda client already signs in via Entra.
- Any automatic or temporary tenant-approval logic — first sign-in creates a
  `pending` row and waits for manual Rocksoft approval; that is the existing
  AC-02 case, nothing new to build server-side.

## Implementation Approach
A documentation/config-only plugin (per `context/foundation/tech-stack.md`):
no code, no build, no tests to run. The approach is a direct, mechanical
rewrite of every place that currently names `email` as a thing the client
states or the skill sends, keeping each file's existing language (Polish for
`README.md`/`USAGE.md`/`docs/flow-contract.md`, English for `SKILL.md`) since
rewriting a file's language is out of scope and would hide the actual diff.
One increment: the five scope items are small, tightly coupled edits to one
integration swap with no independent sub-boundary (per the orchestrator's
`Areas:` decision), so splitting them into separate PRs would only create
cross-file inconsistency windows (e.g. `SKILL.md` referencing `email` while
`flow-contract.md` already says it is gateway-injected).

## Increments
| # | Name | Phases | Depends on | User-visible | Status | PR |
|---|---|---|---|---|---|---|
| 1 | MCP gateway sign-in | 1-4 | — | yes | done | — |

## Phase 1: Point at the authenticated gateway
### Overview
Swap the MCP server URL so the client's Claude session authenticates via the
Rocksoft gateway instead of calling an open n8n endpoint.

### Required changes
#### 1. MCP server config
- **File**: `.mcp.json`
- **Goal**: Replace the unauthenticated n8n URL with the authenticated
  gateway; the client's Microsoft sign-in happens client-side via `/mcp`, so
  no header or credential is added here.
- **Contract**: `mcpServers.rocksoft-mcp.url` = `https://mcp.rocksoft.pl/koda/`
  (`type` stays `http`; no `headers` key).

### Success criteria
#### Automated
- [ ] `python3 -c "import json; json.load(open('.mcp.json'))"` succeeds (still valid JSON)
- [ ] `grep -q 'https://mcp.rocksoft.pl/koda/' .mcp.json`
- [ ] `! grep -q 'flow.rocksoft.co' .mcp.json`
#### Manual
(none)

## Phase 2: Document the gateway contract
### Overview
Record, in the tool contract doc, that `email` is no longer a tool input and
how the gateway signals tenant-access denials, so the n8n side
(Rocksoft-IT/mcp-gateway#22 / n8n-hosting#129) and this skill agree on the
shape before either ships.

### Required changes
#### 1. Flow/gateway contract
- **File**: `docs/flow-contract.md`
- **Goal**: Drop `email` from the required-input row of `list_repositories`,
  `get_repository_context`, and `create_feature_issue`; replace the "w fazie
  0 deklarowany..." note with: identity comes from the verified Microsoft
  Entra token the gateway attaches, keyed by the client directory's e-mail
  (no UPN remapping — the client confirmed the directory uses exactly the
  sign-in address). Add the tenant-access outcomes a tool call can return:
  `pending` (first sign-in for that tenant; a `mcp_tenant_access` row with
  `plugin = koda` waits for manual Rocksoft approval), `not_allowed` /
  `revoked` (access denied or withdrawn).
- **Contract**: error/denial shape `{ error: "pending" | "not_allowed" |
  "revoked" }` returned by any of the three tools when the signed-in tenant
  is not cleared; the existing `{ error: "<message>" }` shape for other
  failures is unchanged.

### Success criteria
#### Automated
- [ ] `! grep -qE '\| *.email.* \| *string *\| *tak' docs/flow-contract.md` (no tool table row still marks `email` required)
- [ ] `grep -q 'pending' docs/flow-contract.md`
- [ ] `grep -q 'not_allowed' docs/flow-contract.md`
- [ ] `grep -q 'revoked' docs/flow-contract.md`
#### Manual
(none)

## Phase 3: Remove the e-mail step from rs-feature
### Overview
`rs-feature` stops asking for or sending an e-mail, reads the signed-in
client's address from the gateway's own tool responses, and tells the client
plainly what to do for each sign-in/approval outcome (AC-01, AC-02, AC-03).

### Required changes
#### 1. Client identification step
- **File**: `skills/rs-feature/SKILL.md`
- **Goal**: Replace Step 0 ("Identify the client (interim: confirmed
  e-mail)") — no question, no confirmation, no interim note about a future
  OAuth release (it has arrived). Before Step 1's first tool call, handle a
  connector with no tools exposed at all (not signed in) by telling the
  client to authorize Rocksoft Koda via `/mcp` (AC-03) and stopping.
- **Contract**: no `email` variable is carried into later steps; the
  client's identity for the rest of the conversation is "the signed-in
  account", resolved only once `list_repositories` answers.

#### 2. Repository lookup and denial handling
- **File**: `skills/rs-feature/SKILL.md`
- **Goal**: `list_repositories` and `create_feature_issue` calls drop the
  `email` argument (the gateway injects it); `get_repository_context` drops
  "(and the e-mail)". Before the existing "Exactly one / Several / None /
  Tool missing or failing" branching, add the gateway-denial branch: a
  `pending` response tells the client access waits for Rocksoft approval and
  prints the running issue draft so far for handover, never losing it
  (AC-02); `not_allowed`/`revoked` tells the client to contact their
  Rocksoft contact. The "None" branch's wording changes from "assigned to
  `<email>`" to "assigned to your account".
- **Contract**: `list_repositories()` / `get_repository_context(git_url)` /
  `create_feature_issue(git_url, title, body, track, labels)` — same shapes
  as `docs/flow-contract.md` minus `email`.

#### 3. Metadata client field
- **File**: `skills/rs-feature/SKILL.md`
- **Goal**: Wherever the skill fills in the issue's `client:` metadata value,
  source it from the e-mail `list_repositories` returned for the signed-in
  account, not from a client-stated value.

### Success criteria
#### Automated
- [ ] `! grep -qi "your e-mail" skills/rs-feature/SKILL.md`
- [ ] `! grep -q "email.*from Step 0" skills/rs-feature/SKILL.md`
- [ ] `grep -qi "pending" skills/rs-feature/SKILL.md`
- [ ] `grep -qi "/mcp" skills/rs-feature/SKILL.md`
#### Manual
- [ ] A read-through confirms no remaining code path asks the client for an
      e-mail or sends one as a tool argument

## Phase 4: Update docs and bump the version
### Overview
Tell the client how first-time sign-in actually works and ship it as 0.3.0.

### Required changes
#### 1. Plugin manifest
- **File**: `.claude-plugin/plugin.json`
- **Goal**: Bump the shipped version.
- **Contract**: `version` = `"0.3.0"`.

#### 2. README
- **File**: `README.md`
- **Goal**: Replace the e-mail-identification description with Microsoft
  work-account sign-in via `/mcp` (no client ID/secret; access needs
  Rocksoft approval for the organization); update "Plan rozwoju" — the OAuth
  proxy it pointed at (issue #1) has landed, so describe the current
  approval flow instead of calling it future work; bump the trailing
  `## Wersja` line to `0.3.0`.
- **Contract**: none (prose only).

#### 3. USAGE
- **File**: `USAGE.md`
- **Goal**: Same sign-in description in the "Przebieg rozmowy" walkthrough
  (point 1, "Kto zgłasza") and the install steps; add the `pending` /
  `not_allowed`/`revoked` outcomes to the troubleshooting table; bump the
  trailing version line to `0.3.0`.
- **Contract**: none (prose only).

### Success criteria
#### Automated
- [ ] `grep -q '"version": "0.3.0"' .claude-plugin/plugin.json`
- [ ] `grep -q '0.3.0' README.md`
- [ ] `grep -q '0.3.0' USAGE.md`
- [ ] `! grep -q '0.2.1' .claude-plugin/plugin.json`
#### Manual
(none)

## Testing Strategy
No test suite applies (brownfield, docs/config-only plugin;
`context/foundation/tech-stack.md` `## Commands`). Verification is the grep/
JSON-validity checks above plus a manual read-through of `SKILL.md` for any
remaining e-mail-collecting code path.

## References
- Issue: https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/4
- `change.md` (issue body verbatim + client's answers to the open questions)
- `context/foundation/tech-stack.md`

## Progress

### Phase 1: Point at the authenticated gateway
#### Automated
- [x] 1.1 `.mcp.json` stays valid JSON — 3c6b349
- [x] 1.2 `.mcp.json` points at `https://mcp.rocksoft.pl/koda/` — 3c6b349
- [x] 1.3 `.mcp.json` no longer references `flow.rocksoft.co` — 3c6b349

### Phase 2: Document the gateway contract
#### Automated
- [x] 2.1 No tool table row in `docs/flow-contract.md` still marks `email` required — 4ea687a
- [x] 2.2 `docs/flow-contract.md` documents the `pending` outcome — 4ea687a
- [x] 2.3 `docs/flow-contract.md` documents the `not_allowed` outcome — 4ea687a
- [x] 2.4 `docs/flow-contract.md` documents the `revoked` outcome — 4ea687a

### Phase 3: Remove the e-mail step from rs-feature
#### Automated
- [x] 3.1 `SKILL.md` no longer asks the client for their e-mail — bc2bc0d
- [x] 3.2 `SKILL.md` no longer carries an e-mail value from Step 0 into later steps — bc2bc0d
- [x] 3.3 `SKILL.md` documents the `pending` tenant outcome — bc2bc0d
- [x] 3.4 `SKILL.md` tells the client to authorize via `/mcp` — bc2bc0d
#### Manual
- [ ] 3.5 A read-through confirms no remaining code path asks for or sends an e-mail

### Phase 4: Update docs and bump the version
#### Automated
- [x] 4.1 `.claude-plugin/plugin.json` version is `0.3.0` — 85188cb
- [x] 4.2 `README.md` states version `0.3.0` — 85188cb
- [x] 4.3 `USAGE.md` states version `0.3.0` — 85188cb
- [x] 4.4 `.claude-plugin/plugin.json` no longer states `0.2.1` — 85188cb
