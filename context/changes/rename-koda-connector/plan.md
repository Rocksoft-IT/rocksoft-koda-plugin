# Rename the Koda MCP connector — Implementation Plan

## Overview
Rename the plugin's MCP server key from `rocksoft-mcp` to `rocksoft-koda` in
`.mcp.json` so the connector is recognizable in Claude's connector list,
update every doc mention of the old key, bump the plugin version to `0.3.1`,
and tell users they need to sign in again via `/mcp` after updating.

## Current State Analysis
- `.mcp.json:3` declares the server key `"rocksoft-mcp"` with
  `url: https://mcp.rocksoft.pl/koda/` — the URL stays unchanged.
- `README.md:8` and `README.md:46` mention `rocksoft-mcp`; `USAGE.md:8`
  mentions it once — matches the issue's claimed counts (2 + 1).
- `.claude-plugin/plugin.json:2-3` has `"name": "rocksoft-koda"` already
  (unrelated to the MCP server key) and `"version": "0.3.0"`.
- `skills/rs-feature/SKILL.md` and `docs/flow-contract.md` contain no
  `rocksoft-mcp` references (confirmed by search) — nothing to change there.
- `context/foundation/tech-stack.md:18` also says `mcpServers.rocksoft-mcp`
  but is not in the Areas scope for this change (foundation doc, not
  user-facing); left as a known stale reference for a future refresh.
- Precedent: commit `85188cb` ("update docs and bump the version (p4)") bumped
  `.claude-plugin/plugin.json`'s version and, in the same commit, updated the
  `## Wersja` footer in both `README.md` and `USAGE.md` to match — this plan
  follows the same pattern for `0.3.1`.

## Desired End State
- `.mcp.json` declares the server key `rocksoft-koda`; the connector list in
  Claude Desktop / Claude Code shows `rocksoft-koda` instead of `rocksoft-mcp`.
- `README.md` and `USAGE.md` refer to the connector as `rocksoft-koda`
  everywhere, and both tell the user that updating the plugin requires
  signing in again via `/mcp` (the rename drops the stored sign-in).
- `.claude-plugin/plugin.json` is at version `0.3.1`; `README.md` and
  `USAGE.md` footers say `0.3.1` too.

### Key discoveries
- `.mcp.json:3` — the only place the server key is declared.
- `README.md:8,46`, `USAGE.md:8` — the only doc mentions of `rocksoft-mcp`.
- `skills/rs-feature/SKILL.md`, `docs/flow-contract.md` — searched, no
  `rocksoft-mcp` references found.

## What we're NOT doing
- Not touching `rocksoft-client-portal` or `rocksoft-sales` (other repo).
- Not adding a display name with spaces (unsupported for plugin MCP servers).
- Not touching the claude.ai Koda connector (moved separately, per issue).
- Not updating `context/foundation/tech-stack.md`'s stale `rocksoft-mcp`
  mention — outside this change's Areas scope.

## Implementation Approach
A single mechanical rename across the five files the issue names, plus a
version bump and the two version-footer updates the project's own precedent
makes part of "bump the version". No alternative approach considered — the
issue fully specifies the target state and the current code confirms every
claim it makes.

## Increments
| # | Name | Phases | Depends on | User-visible | Status | PR |
|---|---|---|---|---|---|---|
| 1 | Rename connector key + docs + version | 1 | — | yes | in-progress | — |

## Phase 1: Rename the connector key, update docs, bump version

### Overview
Renames the MCP server key everywhere it is declared or mentioned, bumps the
plugin version, and documents the one-time re-sign-in.

### Required changes

#### 1. MCP server declaration
- **File**: `.mcp.json`
- **Goal**: the server key the connector list reads must say `rocksoft-koda`.
- **Contract**: `mcpServers` object key renamed `rocksoft-mcp` → `rocksoft-koda`;
  `type` and `url` fields unchanged.

#### 2. Plugin manifest version
- **File**: `.claude-plugin/plugin.json`
- **Goal**: ship the rename under a new version number.
- **Contract**: `version` field `"0.3.0"` → `"0.3.1"`.

#### 3. README
- **File**: `README.md`
- **Goal**: every mention of the connector name matches the new key, and the
  reader knows to sign in again after updating.
- **Contract**: `rocksoft-mcp` → `rocksoft-koda` at the connector description
  (currently line 8) and in the directory tree comment (currently line 46);
  add one sentence near the connector description that updating the plugin
  requires signing in again via `/mcp`; `## Wersja` footer `0.3.0` → `0.3.1`.

#### 4. USAGE
- **File**: `USAGE.md`
- **Goal**: same as README — name consistency plus the re-sign-in note.
- **Contract**: `rocksoft-mcp` → `rocksoft-koda` at the connector description
  (currently line 8); add the same re-sign-in-via-`/mcp` sentence there;
  `## Wersja` footer `0.3.0` → `0.3.1`.

### Success criteria

#### Automated
- `grep -rn "rocksoft-mcp" .mcp.json README.md USAGE.md .claude-plugin/plugin.json skills/rs-feature/SKILL.md docs/` returns no matches.
- `grep -q '"rocksoft-koda"' .mcp.json` matches (server key present).
- `grep -q '"version": "0.3.1"' .claude-plugin/plugin.json` matches.
- `grep -q '0.3.1' README.md` and `grep -q '0.3.1' USAGE.md` both match.

#### Manual
- A human reinstalls/updates the plugin in Claude Desktop or runs `/mcp` in
  Claude Code and confirms the connector list shows `rocksoft-koda` (not
  `rocksoft-mcp`), and that `list_repositories`, `get_repository_context` and
  `create_feature_issue` still work after signing in again (AC-01, AC-02).

## Testing Strategy
No test suite applies (docs/config-only plugin, per `tech-stack.md`); the
Automated criteria above are the verification, and the Manual criterion
covers the one check only a human can perform (the live connector list and
re-auth flow).

## References
- Issue: https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/7
- `change.md` — issue text verbatim
- Precedent commit: `85188cb` (prior version bump pattern)

## Progress

### Phase 1: Rename the connector key, update docs, bump version
#### Automated
- [x] 1.1 `grep -rn "rocksoft-mcp" .mcp.json README.md USAGE.md .claude-plugin/plugin.json skills/rs-feature/SKILL.md docs/` returns no matches
- [x] 1.2 `grep -q '"rocksoft-koda"' .mcp.json` matches
- [x] 1.3 `grep -q '"version": "0.3.1"' .claude-plugin/plugin.json` matches
- [x] 1.4 `grep -q '0.3.1' README.md` and `grep -q '0.3.1' USAGE.md` both match
#### Manual
- [ ] 1.5 Connector list shows `rocksoft-koda` after update/re-sign-in, and the three tools still work (AC-01, AC-02)
