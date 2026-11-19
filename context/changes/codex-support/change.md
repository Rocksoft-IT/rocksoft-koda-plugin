---
change_id: codex-support
title: Koda plugin works in OpenAI Codex as well as Claude
status: planned
created: 2026-11-19
updated: 2026-11-19
archived_at: null
---

## Notes

https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/12

<!-- rs-feature · track: feature · client: piotr@rocksoft.pl · repository: Rocksoft Koda Plugin · feature: 7c3e9a2f-4b1d-4e8a-9f6c-2d5b8a1e3f70 -->

## Summary

Some clients (first: FIDE) develop with OpenAI Codex, not only Claude, so today they bypass Koda and Rocksoft has no say in how their changes are shaped. The Koda plugin (rs-feature + the `rocksoft-koda` MCP server) must install and work in Codex CLI, the Codex IDE extension and Codex cloud, so every client request goes through rs-feature and Rocksoft Flow regardless of the agent. Paid access stays enforced by the MCP gateway, not by the plugin.

## Problem & context

- **Who:** client developers using Codex; Rocksoft, which loses control of context and process when they do.
- **Current system:** plugin 0.5.0 ships only `.claude-plugin/plugin.json` + `marketplace.json`, `.mcp.json` (HTTP server `https://mcp.rocksoft.pl/koda/`), and `skills/rs-feature`. SKILL.md is written for Claude Desktop / Claude Code: it names `AskUserQuestion`, tells users to sign in via `/mcp`, and README/USAGE document only Claude installs.

## Scope

### In scope

1. A Codex user installs the Koda plugin from this repository (Codex plugin manifest and marketplace entry next to the Claude ones).
2. They sign in with their Microsoft work account through Codex's MCP OAuth login (or Codex cloud connector setup).
3. They describe a change; Codex runs rs-feature: picks the repo, reads context, runs the track, shows the full draft, and creates the issue only after an explicit yes — same behaviour as in Claude.
4. Docs (README, USAGE) cover install, sign-in and update for Claude and Codex.

### Out of scope (non-goals)

- Codex support for the rs-skills pipeline (rs-plan, rs-implement …) — separate repository and issue.
- Local license or subscription checks — access stays enforced by the gateway.
- Changes to the MCP tool contract (`docs/flow-contract.md`).

## Related repositories

- **RS MCP Gateway** (`mcp-gateway`): accepts Codex CLI and Codex cloud / ChatGPT OAuth callbacks so the sign-in in step 2 works — Rocksoft-IT/mcp-gateway#26.

## Success criteria

- **Primary:** from Codex CLI and Codex cloud, a client signs in, runs rs-feature end to end and gets an issue in their repository.
- **Guardrails:** Claude Desktop, claude.ai and Claude Code installs keep working unchanged; no secrets in plugin files.

## Requirements

- FR-001: Codex user can install and update the plugin from this repository. Priority: must-have. Change: new
- FR-002: rs-feature runs in Codex with agent-neutral instructions (no Claude-only tool names or `/mcp` as the only sign-in path; questions fall back to numbered chat options). Priority: must-have. Change: modified
- FR-003: Codex user can connect the `rocksoft-koda` MCP server with Microsoft sign-in in CLI, IDE and cloud. Priority: must-have. Change: new
- FR-004: Tenant-access answers (pending / not_allowed / revoked / not signed in) give Codex users correct, agent-specific instructions. Priority: must-have. Change: modified
- FR-005: Claude users keep the same install, sign-in and behaviour. Priority: must-have. Change: preserved
- FR-006: Plugin version is bumped consistently across both manifests. Priority: must-have. Change: new

## Acceptance criteria

### AC-01: Codex CLI end to end
- **Given** an active-tenant user with Codex CLI
- **When** they install the plugin, sign in and ask for a change
- **Then** rs-feature runs its normal flow and creates the issue after an explicit yes

### AC-02: Codex cloud
- **Given** the same user in Codex cloud
- **When** they connect the Koda server and ask for a change
- **Then** the same flow completes

### AC-03: Not signed in in Codex
- **Given** a Codex user who has not signed in
- **When** rs-feature starts
- **Then** it tells them how to sign in in Codex (not Claude's `/mcp`) and stops

### AC-04: Claude unchanged
- **Given** an existing Claude Code / Desktop install
- **When** the plugin is updated
- **Then** install, sign-in and rs-feature behave as before

## Constraints & preserved behavior

- Distribution only through this GitHub repository (no zip packages).
- Identity always injected by the gateway; skill never asks for or sends an e-mail.
- Draft shown in full and explicit yes before `create_feature_issue`.

## Open questions

- Codex cloud loads plugins/skills differently from the CLI (environment setup vs. local install) — research decides the supported install path there.
- Whether one shared manifest standard (Agent Plugins) can replace two manifests — research.

## Metadata

- **Client:** piotr@rocksoft.pl
- **Repository:** Rocksoft Koda Plugin (git@github.com:Rocksoft-IT/rocksoft-koda-plugin.git)
- **Feature:** 7c3e9a2f-4b1d-4e8a-9f6c-2d5b8a1e3f70
- **Track:** feature
- **Created with:** rocksoft-koda rs-feature 0.5.0

---
<!-- rs-feature:meta -->
- client: piotr@rocksoft.pl
- requested-by: piotr@rocksoft.pl
- track: feature
- plugin: rocksoft-koda/rs-feature 0.5.0
- created: 2026-11-19T18:16:01.038Z
- feature: 7c3e9a2f-4b1d-4e8a-9f6c-2d5b8a1e3f70
