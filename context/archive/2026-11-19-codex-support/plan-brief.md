# Koda plugin works in OpenAI Codex as well as Claude — Plan Brief
Full plan: `context/changes/codex-support/plan.md` · issue text: `change.md` (issue #12)

## What & why
Clients such as FIDE develop with OpenAI Codex and today bypass Koda. The plugin
must install and run `rs-feature` in Codex CLI, the Codex IDE extension and Codex
cloud, with Microsoft sign-in through the `rocksoft-koda` MCP server, while
Claude installs stay exactly as they are. Paid access stays enforced by the
gateway, not the plugin.

## Starting point
Only Claude files exist (`.claude-plugin/*`, `.mcp.json`); `SKILL.md` names
`AskUserQuestion` and makes `/mcp` the only sign-in path; README/USAGE cover
Claude only. Spiked with the installed Codex CLI (0.167.2, isolated
`CODEX_HOME`): Codex already installs the Claude layout, and a Codex-native
manifest + `.agents/plugins/marketplace.json` installs end to end, exposes the
shared `.mcp.json` server ("Not logged in" until `codex mcp login`), and lists
the skill as `rocksoft-koda:rs-feature`.

## Desired end state
Codex users install via a Codex marketplace entry, log in with `codex mcp login
rocksoft-koda`, and rs-feature runs unchanged; not-signed-in and tenant-access
messages are host-aware; README/USAGE document Claude and Codex; both manifests
and docs say `0.6.0`.

## Complexity
MEDIUM — one increment, three phases, no code or tests, but a multi-host
distribution surface, several decisions that rest on external documentation, and
parts (remote Git marketplace, IDE, cloud) that cannot be exercised before merge.

## Key decisions made
| Decision | Choice | Why | Source |
|---|---|---|---|
| Skip rs-research | Skipped (Jev p=0.23); the open questions were answered inline from OpenAI docs and CLI spikes during planning | Issue is spec-complete; evidence is cited in plan.md Current State | Jev (p=0.23) |
| Skip rs-frame | Skipped (Jev p=0.30) | Feature-shaped issue with no stated cause or fix | Jev (p=0.30) |
| Areas | One area A1, one increment | Merged by the orchestrator: the three sub-areas share the same small file set | Orchestrator |
| Two manifests vs one shared Agent Plugins manifest | Keep two: `.claude-plugin/` + `.codex-plugin/` | Claude Code is not documented to read root `plugin.json`/`mcp.json` and FR-005 is must-have; the Codex compatibility manifest is documented as supported and verified with the CLI | Auto |
| Codex manifest format | `.codex-plugin/plugin.json` (compat) with `skills: ./skills/`, `mcpServers: ./.mcp.json`, `interface` | Verified `codex plugin add`/`list`/`mcp list`/skill listing; docs mark it supported | Auto |
| MCP definition | Reuse `.mcp.json` unchanged (no second file) | Verified: Codex accepts it with its `type: http`; one definition cannot drift | Auto |
| Codex marketplace | `.agents/plugins/marketplace.json`, name `rocksoft-koda`, `source: {local, "./"}`, `AVAILABLE`/`ON_INSTALL` | Verified locally; same install id `rocksoft-koda@rocksoft-koda` as Claude | Auto |
| Claude marketplace and `.mcp.json` | Byte-identical; plugin.json only version + description | FR-005 / AC-04 | Issue |
| Version | `0.5.0` → `0.6.0` in both manifests, README, USAGE | Project precedent: new capability = minor bump; FR-006 | Auto |
| SKILL.md frontmatter | Unchanged (`allowed-tools: mcp__*` kept) | Codex loads the skill with it (verified); Claude behaviour must not move | Auto |
| Question fallback | Numbered chat options by default; a host question tool only if offered, never named | FR-002; Claude-only tool name must go | Issue |
| Sign-in text | One "Signing in, per host" section (Claude Desktop/claude.ai, Claude Code `/mcp`, Codex `codex mcp login rocksoft-koda`, Codex cloud connect) referenced from Step 0 and the tenant outcomes | FR-002/FR-004/AC-03; avoids repeating per host in every place | Auto |
| IDE extension | Documented as MCP config + standalone skill copy (`~/.agents/skills`), not a plugin install | OpenAI docs: IDE has no plugin browser but shares MCP config and skills with the CLI | Auto (decision-to-verify) |
| Codex cloud | Documented as workspace-admin GitHub marketplace import (repo root) + member Connect; "Desktop only" caveat noted | OpenAI enterprise plugin-management doc; cannot be run here; gateway callback is mcp-gateway#26 | Auto (decision-to-verify) |
| Public-directory metadata (privacy/terms/support URLs, icons) | Omitted | Not available; must not be invented; publishing is off | Auto |

## Scope
**In:** `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`,
`.claude-plugin/plugin.json` (version, description), `skills/rs-feature/SKILL.md`,
`README.md`, `USAGE.md`, one sentence in `docs/flow-contract.md`,
`context/foundation/tech-stack.md`.
**Out:** rs-skills pipeline in Codex, license checks, MCP tool contract, gateway
changes, Agent Plugins root manifest, public OpenAI directory submission.

## Architecture / Approach
Side-by-side manifests, one skill, one `.mcp.json`. SKILL.md changes are
surgical: Runtime assumptions, tenant-access/Step 0 wording and one new sign-in
section; Steps 1-6 and Guardrails keep their behaviour word for word.

## Increments at a glance
| # | Delivers | Depends on | User-visible | Key risk |
|---|---|---|---|---|
| 1 | Codex install + agent-neutral skill + docs, `0.6.0` | — | yes | Remote Git/IDE/cloud paths unverified before merge |

## Phases at a glance
| Phase | Increment | Delivers | Key risk |
|---|---|---|---|
| 1 | 1 | Codex manifest, marketplace, version bump, CLI smoke test | Remote snapshot of `source: "./"` untested |
| 2 | 1 | Agent-neutral `SKILL.md` with per-host sign-in | Wording drift from Claude behaviour |
| 3 | 1 | README/USAGE (Polish), tech-stack, flow-contract sentence | Doc claims for IDE/cloud rest on OpenAI docs |

## Open risks & assumptions
- decision-to-verify: `source: {local, "./"}` verified only against a local
  marketplace root; `codex plugin marketplace add Rocksoft-IT/rocksoft-koda-plugin`
  (Git snapshot) and the update flow (`marketplace upgrade` + `plugin add`) are
  checked manually after merge. Fallback if it fails: `source: "url"` form for a
  root plugin (documented).
- decision-to-verify: IDE-extension path (MCP config + skill copy) and Codex cloud
  path (workspace marketplace import, "Desktop only" label) are taken from OpenAI
  documentation and not run here; AC-02 additionally needs mcp-gateway#26.
- decision-to-verify: host-specific connect wording for Codex cloud / ChatGPT
  ("connect from the plugin page") follows docs, not a live UI.
- decision-to-verify: `codex mcp login` name equals the MCP server key
  `rocksoft-koda` (verified in `codex mcp list`); if a user also adds the server
  by hand while the plugin is installed, a duplicate server may appear (docs warn).
- Skills ignore `allowed-tools` in Codex (observed: skill listed); not
  runtime-tested in a live session.

## Success criteria (summary)
JSON validity, equal versions, byte-identical Claude marketplace/`.mcp.json`,
Codex CLI installs the plugin into an isolated `CODEX_HOME` and lists the MCP
server and `rocksoft-koda:rs-feature`, no `AskUserQuestion`, Codex sign-in text
present, docs mention both agents. Manual: Codex CLI end to end (AC-01), cloud
(AC-02), not-signed-in text (AC-03).
