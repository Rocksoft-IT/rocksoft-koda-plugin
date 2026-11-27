---
change_id: koda-post-issue-flows
title: Clients can check status, decide and give feedback from the Koda plugin
status: impl_reviewed
created: 2026-11-27
updated: 2026-11-27
archived_at: null
---

## Notes

https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/17

<!-- rs-feature · track: feature · client: piotr@rocksoft.pl · repository: Rocksoft Koda Plugin · feature: 7c3e9a52-4f1b-4d8e-9a6c-2b5f8e1d0a47 -->

## Summary

The Koda plugin today has one skill, `rs-feature`, which ends once the issue is created. With the new Koda MCP tools (status, decision context, accept / request changes, explain and resume runs, feedback), the plugin should guide the client through everything after the issue as well, so the client can work only from Claude or ChatGPT without opening Cezar.

## Problem & context

- **Who:** clients using the Koda plugin in Claude (claude.ai, Desktop, Code) or Codex/ChatGPT. **When:** after their issue is created, when work waits for them or something fails. **Cost:** they leave the chat for Cezar, or decisions wait.
- **Current system:** `skills/rs-feature` (single entry point, creates issues through `create_feature_issue`), `.mcp.json` pointing at `https://mcp.rocksoft.pl/koda/`, `README.md` and `USAGE.md`, Claude and Codex manifests at version 0.6.0.
- The new tools are added to the Koda MCP gateway in `n8n-hosting` (same feature), backed by a new Cezar API.

## Scope

### In scope

1. A skill (for example `rs-status`, name open) that answers "what's waiting for me / where is my request": calls the status tool and shows the client their issues and pending decisions in plain language.
2. A decision flow ("Dopytaj w Claude"): loads the decision context of a PR, lets the client ask questions about it in their own chat, then accepts it or sends a change request / answers the open questions, only after the client's explicit confirmation of the final action and text.
3. A run-recovery flow: explains a failed or blocked run in non-technical terms and resumes it with the client's comment, after explicit confirmation.
4. A feedback flow: collects feedback about the plugin or Koda and sends it with `send_feedback` after the client sees the text.
5. `rs-feature`, `README.md` and `USAGE.md` point to the new flows (e.g. at the end of `rs-feature`: "you can check status and decide from here later").
6. Works on the same hosts as `rs-feature` (Claude and Codex/ChatGPT), with the same weakest-host assumptions; version bump in both manifests.

### Out of scope (non-goals)

- Any sign-in to the client's Claude or ChatGPT account by Koda — the client uses their own app; Koda is only a connector.
- New MCP server logic — the tools live in `n8n-hosting`.
- Merging PRs from the chat.

## Related repositories

- **N8N Hosting** (`n8n-hosting`): new MCP tools in the Koda gateway workflow that these skills call — Rocksoft-IT/n8n-hosting#180.
- **cezar** (`Rocksoft-IT/cezar`): the server-side API and permission checks behind those tools (local orchestrator run).

## Access & roles

No identity handling in the plugin: identity comes from the gateway sign-in, as today. The skills never ask for or send an e-mail. When a tool refuses (not allowed, not found), the skill says so plainly and does not retry with other identifiers.

## Success criteria

- **Primary:** a client asks in claude.ai "what's waiting for me?", discusses a PR in their own chat, and accepts it or asks for changes, all guided by the plugin.
- **Secondary:** a client sends feedback about Koda in two messages.
- **Guardrails:** no write action (decide, resume, feedback) runs without the client's explicit yes on the final text; `rs-feature` behaves as before.

## Requirements

- FR-001: Client can ask for the status of their requests and see pending decisions. Priority: must-have. Change: new
- FR-002: Client can discuss a PR's decision context in their chat and then accept it or request changes. Priority: must-have. Change: new
- FR-003: Client can get a plain-language explanation of a failed run and resume it. Priority: must-have. Change: new
- FR-004: Client can send feedback about the plugin or Koda. Priority: must-have. Change: new
- FR-005: Client can still create feature issues with `rs-feature` as today. Priority: must-have. Change: preserved

## Acceptance criteria

### AC-01: Status

- **Given** a signed-in client with open Koda issues
- **When** they ask "what's waiting for me?"
- **Then** the plugin lists their issues with plain-language status and pending decisions, with links

### AC-02: Decide with confirmation

- **Given** a PR waiting for the client's decision
- **When** the client discusses it and says they want to accept it or request changes
- **Then** the plugin shows the exact action and text, and calls the tool only after an explicit yes

### AC-03: Refused action

- **Given** the tool refuses an action (no permission, not found, Cezar unavailable)
- **When** the plugin gets `{ error }`
- **Then** it explains it plainly, does not retry with other ids, and suggests contacting Rocksoft when relevant

### AC-04: Untrusted content

- **Given** a decision context containing text that looks like instructions
- **When** the plugin presents it
- **Then** it treats it as data and never acts on it

### AC-05: Feedback

- **Given** a client who wants to give feedback
- **When** they describe it
- **Then** the plugin shows the text, sends it after a yes, and returns the issue link

## Constraints & preserved behavior

- Same runtime assumptions as `rs-feature`: no local files, no shell, plain-chat questions, MCP tools only, chat in the client's language.
- `rs-feature` flow and its issue format stay unchanged.

## Open questions

- Skill names and whether this is one skill with several flows or several skills.
- Final tool names follow Rocksoft-IT/n8n-hosting#180 and the Cezar API contract.

## Metadata

- **Client:** piotr@rocksoft.pl
- **Repository:** Rocksoft Koda Plugin (git@github.com:Rocksoft-IT/rocksoft-koda-plugin.git)
- **Feature:** 7c3e9a52-4f1b-4d8e-9a6c-2b5f8e1d0a47
- **Track:** feature
- **Created with:** rocksoft-koda rs-feature 0.6.0

---
<!-- rs-feature:meta -->
- client: piotr@rocksoft.pl
- requested-by: piotr@rocksoft.pl
- track: feature
- plugin: rocksoft-koda/rs-feature 0.6.0
- created: 2026-11-27T08:34:56.664Z
- feature: 7c3e9a52-4f1b-4d8e-9a6c-2b5f8e1d0a47

## Orchestrator notes

Areas (decided by the orchestrator with Jev): A1 post-issue flows (new skills; builds on nothing); A2 feedback and wiring (send_feedback flow, rs-feature closing pointer, README, USAGE, version bump; builds on A1). Open PRs #15/#16 (issue #14) change rs-feature, README, docs and hooks and are unmerged: plan against main.
