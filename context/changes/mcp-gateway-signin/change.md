---
change_id: mcp-gateway-signin
title: Switch rs-feature to the authenticated Rocksoft MCP gateway sign-in
status: implemented
created: 2026-11-12
updated: 2026-11-12
archived_at: null
---

## Notes

https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/4

## Summary

The plugin points at the Rocksoft MCP gateway (`https://mcp.rocksoft.pl/koda/`) instead of the unauthenticated n8n endpoint. The user signs in once through `/mcp` with their Microsoft account; the gateway passes the verified e-mail to Rocksoft Flow. `rs-feature` no longer asks for or sends an e-mail. The rest of the conversation and the issue it produces stay the same.

## Problem & context

- **Who / cost:** today `.mcp.json` points at `https://flow.rocksoft.co/mcp/0b5ef84b-…` with no authentication, and `rs-feature` Step 0 asks the user to confirm "`<email>` as your Rocksoft client identity". Anyone with the URL can act as any client e-mail.
- **Current system:** tools `list_repositories`, `get_repository_context`, `create_feature_issue` all take `email` (`docs/flow-contract.md`). The `rocksoft-portal` and `rocksoft-sales` plugins already use `https://mcp.rocksoft.pl/<slug>/`.

## Scope

### In scope

1. `.mcp.json`: `url` → `https://mcp.rocksoft.pl/koda/` (no headers, OAuth handled by the client).
2. `skills/rs-feature/SKILL.md`: remove the e-mail question/confirmation in Step 0 and the `email` argument from every tool call; "no repositories" wording refers to the signed-in account; handle gateway denials (`pending` → access waits for Rocksoft approval, `not_allowed`/`revoked` → contact your Rocksoft contact) and a missing sign-in (tell the user to authorize via `/mcp`). Metadata `client:` uses the e-mail returned by `list_repositories`.
3. `docs/flow-contract.md`: `email` is no longer a tool input; it is injected by the gateway from the verified token.
4. `README.md` / `USAGE.md`: first-time sign-in with a Microsoft work account via `/mcp`; no client ID or secret needed; access needs Rocksoft approval for the organization.
5. `.claude-plugin/plugin.json` (and marketplace entry): version `0.3.0`.

### Out of scope (non-goals)

- Gateway route — Rocksoft-IT/mcp-gateway#22.
- n8n workflow changes — Rocksoft-IT/n8n-hosting#129.
- Changes to tracks, issue template or conversation flow.

## Success criteria

- **Primary:** a client installs 0.3.0, signs in via `/mcp`, and `rs-feature` lists their repositories and creates an issue without ever being asked for an e-mail.
- **Guardrails:** the issue body and metadata are unchanged apart from the identity source.

## Requirements

- FR-001: Client can sign in to Koda with their Microsoft work account. Priority: must-have. Change: new
- FR-002: Client can run rs-feature without stating an e-mail. Priority: must-have. Change: modified
- FR-003: Client sees a clear message when their organization is not yet approved. Priority: must-have. Change: new
- FR-004: Client can still create a feature issue in an assigned repository. Priority: must-have. Change: preserved

## Acceptance criteria

### AC-01: Signed-in flow
- **Given** plugin 0.3.0 and a signed-in user from an approved tenant
- **When** they start rs-feature
- **Then** their repositories are listed without an e-mail prompt and the issue is created as before

### AC-02: Organization pending approval
- **Given** a signed-in user whose tenant is `pending`
- **When** rs-feature calls a tool
- **Then** the user is told access waits for Rocksoft approval and no issue draft is lost (it is printed for handover)

### AC-03: Not signed in
- **Given** the connector is not authorized
- **When** rs-feature starts
- **Then** the user is told to authorize Rocksoft Koda via `/mcp`

## Constraints & preserved behavior

- Release only after Rocksoft-IT/mcp-gateway#22 is deployed and n8n-hosting#129 phase 1 is live.
- The fallback "print title and body for handover" when a tool is unavailable stays.

## Open questions

- Clients without Microsoft Entra accounts cannot sign in; decide whether they stay on 0.2.x until another identity provider exists.
- The claude.ai Koda connector (outside the plugin) must also move to the new URL before n8n phase 2.

## Metadata

- **Client:** piotr@rocksoft.pl
- **Repository:** Rocksoft Koda Plugin (git@github.com:Rocksoft-IT/rocksoft-koda-plugin.git)
- **Track:** feature
- **Created with:** rocksoft-koda rs-feature 0.2.1
- **Related:** Rocksoft-IT/n8n-hosting#129, Rocksoft-IT/mcp-gateway#22

### Issue comments

**rocksoft-koda** (2026-11-12T15:09:23Z):
Answers to the open questions (from the client, piotr@rocksoft.pl):

1. **Clients without Microsoft Entra:** not an issue. Every client currently using Koda signs in with Microsoft Entra. Entra-only sign-in through the existing gateway facade is enough; no second identity provider.
2. **E-mail vs UPN:** the repository directory uses exactly the addresses clients sign in with. No remapping is needed.
3. **claude.ai Koda connector:** it is moved to the new URL at the very end (after plugin 0.3.0 is released, before n8n phase 2 removes the UUID endpoint).
4. **Tenant approval:** no automatic approval and no temporary logic. A client tenant's first sign-in creates a `pending` row in `mcp_tenant_access` (`plugin = koda`) and waits for manual approval by Rocksoft. Before phase 2, the tenants of current Koda clients must be approved, otherwise they would see "pending" after the switch.

Related: Rocksoft-IT/n8n-hosting#129, Rocksoft-IT/mcp-gateway#22, Rocksoft-IT/rocksoft-koda-plugin#4
