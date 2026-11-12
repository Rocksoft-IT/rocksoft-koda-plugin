# Rename the Koda MCP connector — Plan Brief
Full plan: `context/changes/rename-koda-connector/plan.md` · issue text: `change.md`

## Complexity
TRIVIAL — one mechanical key rename across five known files plus a version
bump, with an obvious approach and no design choices. Skipped: rs-research
(no codebase exploration needed, the issue names every file), rs-frame
(no bug shape or scope ambiguity — skipped (Jev p=0.06 / p=0.22)).

## Key decisions made
| Decision | Choice | Why | Source |
|---|---|---|---|
| Server key rename | `rocksoft-mcp` → `rocksoft-koda` in `.mcp.json` | issue's core ask; URL unchanged | Issue |
| Version bump | `.claude-plugin/plugin.json` → `0.3.1` | explicit scope item | Issue |
| Sync version footers | `README.md` / `USAGE.md` `## Wersja` → `0.3.1` | repo precedent: commit `85188cb` bumped these footers alongside the last version bump | Research |
| `SKILL.md` / `docs/` scan | no changes needed | grep confirmed neither file references `rocksoft-mcp` | Research |
| `tech-stack.md` stale mention | left unchanged | outside this change's Areas scope (foundation doc, not user-facing) | Auto |
| Re-auth note | add one sentence near the connector mention in `README.md` and `USAGE.md` | issue scope item 2 requires telling users to sign in again via `/mcp` | Issue |
