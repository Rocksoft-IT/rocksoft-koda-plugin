---
project: rocksoft-koda
context_type: brownfield
created: 2026-11-12
updated: 2026-11-23
source: detected-from-cwd
---

# Rocksoft Koda Plugin — Tech Stack

## Languages & Runtimes
- The plugin itself is Markdown skill definitions (`skills/rs-feature/SKILL.md`)
  plus JSON configuration (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`,
  `.mcp.json`). No package manager, lockfile, or language manifest is present.
- Python 3, standard library only, for the hook scripts under `hooks/`
  (`hooks/scripts/koda_hook.py`) and their tests (`hooks/tests`). No
  dependencies and no network modules; `python3` on the developer's machine is
  the only requirement.

## Integrations
- MCP server: Rocksoft Flow, configured in `.mcp.json` (`mcpServers.rocksoft-koda`),
  an HTTP MCP endpoint the `rs-feature` skill calls per `docs/flow-contract.md`.
  The same `.mcp.json` serves Claude and Codex (the Codex manifest points to it).

## CI/CD
- None detected (no `.github/workflows/`, `.gitlab-ci.yml`, or equivalent).

## Issue Tracker
- GitHub Issues (default) — `origin` is `github.com/Rocksoft-IT/rocksoft-koda-plugin`.

## Commands
- Test: `python3 -m unittest discover -s hooks/tests` (stdlib `unittest`;
  a single class, e.g. `-k PromptTests`).
- No install or build step; manifest and Markdown changes are reviewed by
  reading the diff.

## Tooling
- None beyond the plugin/marketplace manifests: Claude
  (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) and Codex
  (`.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`). Both
  plugin manifests carry the same version.

## Open Stack Questions
(none — every axis here is either detected or genuinely not applicable to a
documentation/config-only plugin)
