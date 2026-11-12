---
change_id: rename-koda-connector
title: Rename the MCP connector key from rocksoft-mcp to rocksoft-koda
status: implementing
created: 2026-11-12
updated: 2026-11-12
archived_at: null
---

## Notes

https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/7

<!-- rs-feature · track: quick · client: piotr@rocksoft.pl · repository: Rocksoft Koda Plugin -->

## Summary

In Claude Desktop the connector list shows the Rocksoft plugins as `rocksoft-client-portal`, `rocksoft-mcp` and `rocksoft-sales`. `rocksoft-mcp` does not say what it is. Rename the plugin's MCP server key to `rocksoft-koda` so the Koda connector is recognizable and consistent with the other two.

## Problem & context

- **Who / cost:** every Koda user sees an unclear `rocksoft-mcp` entry next to `rocksoft-client-portal` and `rocksoft-sales`.
- **Current system:** a plugin's connector name is the server key in its `.mcp.json`; it is both the display name and part of the tool names (`mcp__plugin_rocksoft-koda_<server>__<tool>`), so it must stay lowercase kebab-case (no spaces). Free-text display names exist only for connectors added in claude.ai settings, which this plugin does not use.

## Scope

### In scope

1. `.mcp.json`: rename the server key `rocksoft-mcp` → `rocksoft-koda` (URL `https://mcp.rocksoft.pl/koda/` unchanged).
2. Update the mentions of `rocksoft-mcp` in `README.md` (2) and `USAGE.md` (1); mention that after updating the plugin the user signs in once more via `/mcp`.
3. `.claude-plugin/plugin.json`: version `0.3.1`.
4. Check `skills/rs-feature/SKILL.md` and `docs/` for any reference to the old server name or to fully prefixed tool names, and update them if found.

### Out of scope (non-goals)

- Renaming `rocksoft-client-portal` or `rocksoft-sales` (other repository, already consistent).
- Display names with spaces — not supported for plugin MCP servers.
- The claude.ai Koda connector — moved separately before n8n phase 2.

## Acceptance criteria

### AC-01: New connector name
- **Given** plugin 0.3.1 is installed
- **When** the user opens the connector list in Claude Desktop or `/mcp` in Claude Code
- **Then** the Koda connector is listed as `rocksoft-koda` and `rocksoft-mcp` is gone

### AC-02: Skill still works
- **Given** the user signed in again through `/mcp`
- **When** they run rs-feature
- **Then** `list_repositories`, `get_repository_context` and `create_feature_issue` work as in 0.3.0

## Constraints & preserved behavior

- No change to the gateway URL, tools, inputs or outputs.
- Renaming the server drops the stored sign-in; users authorize once more.

## Metadata

- **Client:** piotr@rocksoft.pl
- **Repository:** Rocksoft Koda Plugin (git@github.com:Rocksoft-IT/rocksoft-koda-plugin.git)
- **Track:** quick
- **Created with:** rocksoft-koda rs-feature 0.3.0
- **Related:** Rocksoft-IT/rocksoft-koda-plugin#4
