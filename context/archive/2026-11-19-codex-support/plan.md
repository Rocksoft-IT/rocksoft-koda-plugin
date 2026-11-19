# Koda plugin works in OpenAI Codex as well as Claude — Implementation Plan

## Overview
Add a Codex plugin manifest and marketplace entry next to the Claude ones, make
`rs-feature` agent-neutral (no Claude-only tool name, agent-specific sign-in and
tenant-access instructions, numbered-option questions), document install,
sign-in and update for Claude and Codex, and bump the version consistently
(`0.5.0` → `0.6.0`) across both manifests and the docs. Claude installs, the MCP
tool contract and the gateway-enforced access model stay unchanged.

## Current State Analysis
Confirmed against the code and against the installed Codex CLI (`codex-cli
0.167.2`, isolated `CODEX_HOME`, local marketplace spikes):

- The plugin ships only `.claude-plugin/plugin.json` (version `0.5.0`, line 3),
  `.claude-plugin/marketplace.json` (`source: "./"`), `.mcp.json` (`type: http`,
  `https://mcp.rocksoft.pl/koda/`) and `skills/rs-feature`.
- `skills/rs-feature/SKILL.md` is Claude-shaped: line 33 "runs in Claude Desktop /
  claude.ai chat first, Claude Code second"; lines 39-41 name `AskUserQuestion`;
  lines 46-48, 71-73, 120-124 make `/mcp` the only sign-in path. The tenant
  outcome texts (lines 54-69) contain no host-specific instructions.
- `references/*.md` contain no Claude-only wording; `docs/flow-contract.md:12`
  mentions `/mcp` in one sentence (descriptive, not part of the tool contract).
- README.md and USAGE.md document Claude Desktop / claude.ai / Claude Code only
  and carry the version in README "Wersja" (`0.5.0`) and USAGE last line.
- Codex already installs the unmodified Claude layout (marketplace read from
  `.claude-plugin/marketplace.json`, MCP server from `.mcp.json`, skill listed as
  `rocksoft-koda:rs-feature` despite the Claude-only `allowed-tools` frontmatter),
  but with no Codex presentation metadata and no Codex marketplace, and nothing
  in the repository or its docs declares or promises that.
- A Codex-native layout was verified end to end: `.codex-plugin/plugin.json`
  (`skills: "./skills/"`, `mcpServers: "./.mcp.json"`, `interface`) plus
  `.agents/plugins/marketplace.json` with `source: {source: local, path: "./"}`;
  `codex plugin marketplace add`, `codex plugin add rocksoft-koda@rocksoft-koda`
  and `codex plugin list` succeed, `codex mcp list` shows `rocksoft-koda` as "Not
  logged in" (login via `codex mcp login`), and re-running `codex plugin add`
  after a version bump installs the new version. Shared `.mcp.json` (with
  `type: http`) is accepted by Codex.
- OpenAI docs (developers.openai.com/codex/plugins, /plugins/build/plugins,
  learn.chatgpt.com enterprise plugin-management, cloud-environments): the
  Codex IDE extension has no plugin browser but shares `config.toml` MCP setup
  and standalone skills (`.agents/skills`, `~/.agents/skills`) with the CLI;
  Codex cloud / ChatGPT gets plugins through a workspace admin importing a
  GitHub marketplace (accepts `.agents/plugins/marketplace.json` or
  `.claude-plugin/marketplace.json`, repo root, no path) or through a personal
  plugin connection on chatgpt.com/plugins; plugins that declare MCP servers may
  be labelled "Desktop only". Those cloud and IDE paths could not be run here.

## Desired End State
- A Codex CLI user runs `codex plugin marketplace add Rocksoft-IT/rocksoft-koda-plugin`,
  installs `rocksoft-koda`, runs `codex mcp login rocksoft-koda`, and rs-feature
  runs its normal flow. IDE users and cloud users have documented paths.
- When not signed in, rs-feature tells a Codex user to sign in the Codex way and
  a Claude user the Claude way, then stops; tenant-access answers carry the
  same host-aware wording.
- Both manifests, README and USAGE say `0.6.0`; Claude files that are not the
  version/description are byte-identical in behaviour.

### Key discoveries
- `.claude-plugin/marketplace.json` and `.mcp.json` need no change: Codex reads
  both (verified), so the shared `.mcp.json` stays the single MCP definition.
- The Codex install path is name-driven: marketplace `name` and plugin `name`
  are both `rocksoft-koda`, giving `rocksoft-koda@rocksoft-koda` in Codex, as in
  Claude (`README.md:31`).
- Codex lists `allowed-tools` frontmatter without complaint; frontmatter stays
  untouched so Claude behaviour does not move.

## What we're NOT doing
- No Codex support for rs-skills (rs-plan, rs-implement, …); no license or
  subscription check in the plugin; no change to `docs/flow-contract.md`'s tool
  contract or to the gateway (Rocksoft-IT/mcp-gateway#26 owns the OAuth callbacks).
- No replacement of the two manifests by a single Agent Plugins root
  `plugin.json` / `mcp.json`; no `.app.json`, hooks, `onboardingSkill`, icons, or
  submission to the public OpenAI directory (privacy/terms/support URLs are not
  available and must not be invented).
- No zip packages; no secrets in any plugin file; no change to the Claude
  marketplace entry, `.mcp.json`, or SKILL.md frontmatter.

## Implementation Approach
Two manifests side by side, one skill text, one MCP definition. The Codex
compatibility manifest (`.codex-plugin/plugin.json`) plus a repo marketplace
(`.agents/plugins/marketplace.json`) were chosen over the portable Agent Plugins
root manifest because Claude Code is not documented to read a root
`plugin.json`/`mcp.json` (FR-005 is must-have), the compatibility manifest is
documented as supported and was verified with the installed CLI, and the portable
`mcp.json` would need a second MCP file with a different transport type. The
marketplace source is a local `./` path, which resolves to the repository root
the CLI snapshots when a user adds `Rocksoft-IT/rocksoft-koda-plugin`.

The SKILL.md edit is surgical: only Runtime assumptions, the tenant-access
section, Step 0 and the Step 1/6 "no tools" wording change, plus one new "Signing
in, per host" section that the other passages point to. Everything in Steps 1-6
and the Guardrails that governs behaviour (single confirmation, identity never
asked, English issue, repo from Flow) stays word-for-word.

## Increments
| # | Name | Phases | Depends on | User-visible | Status | PR |
|---|---|---|---|---|---|---|
| 1 | Koda plugin installs and runs in Codex | 1-3 | — | yes | in-progress | — |

## Phase 1: Codex manifest, marketplace and version bump
### Overview
Make the repository installable from Codex and move both manifests to `0.6.0`.

### Required changes
#### 1. Codex plugin manifest
- **File**: `.codex-plugin/plugin.json` (new)
- **Goal**: Describe the same plugin to Codex with presentation metadata.
- **Contract**: `name: rocksoft-koda`; `version: 0.6.0`; `description` and
  `author.name: Rocksoft`; `keywords`; `skills: "./skills/"`; `mcpServers:
  "./.mcp.json"`; `interface` with `displayName` (≤30 chars), `shortDescription`
  (≤30 chars), `longDescription`, `developerName: Rocksoft`, `category:
  Productivity`, `capabilities`, and `defaultPrompt` examples. No `$schema`
  (Codex compatibility format), no privacy/terms/support/website URLs, no icons,
  no secrets.

#### 2. Codex marketplace entry
- **File**: `.agents/plugins/marketplace.json` (new)
- **Goal**: Let `codex plugin marketplace add Rocksoft-IT/rocksoft-koda-plugin`
  (and a workspace GitHub import) find the plugin.
- **Contract**: top-level `name: rocksoft-koda`, `interface.displayName`; one
  plugin `rocksoft-koda`, `source: {source: local, path: "./"}`, `policy:
  {installation: AVAILABLE, authentication: ON_INSTALL}`, `category: Productivity`.

#### 3. Claude manifest version
- **File**: `.claude-plugin/plugin.json`
- **Goal**: Bump `version` to `0.6.0` and make `description` agent-neutral
  ("for Claude and Codex"). No other field changes.
- **Contract**: `.claude-plugin/marketplace.json` and `.mcp.json` stay
  byte-identical.

### Success criteria
#### Automated
- Both manifests and the marketplace parse as JSON: `python3 -c "import json;[json.load(open(f)) for f in ('.codex-plugin/plugin.json','.agents/plugins/marketplace.json','.claude-plugin/plugin.json')]"`
- Versions match: `python3 -c "import json;a=json.load(open('.codex-plugin/plugin.json'))['version'];b=json.load(open('.claude-plugin/plugin.json'))['version'];assert a==b=='0.6.0',(a,b)"`
- Claude files are otherwise untouched: `git diff --quiet $(git merge-base HEAD main) -- .mcp.json .claude-plugin/marketplace.json` and `python3 -c "import json,subprocess as s;m=s.check_output(['git','merge-base','HEAD','main'],text=True).strip();b=json.loads(s.check_output(['git','show',m+':.claude-plugin/plugin.json']));c=json.load(open('.claude-plugin/plugin.json'));f=lambda d:{k:v for k,v in d.items() if k not in('version','description')};assert f(b)==f(c)"`
- Codex installs it from the working tree: `export CODEX_HOME=$(mktemp -d) && codex plugin marketplace add "$PWD" && codex plugin add rocksoft-koda@rocksoft-koda && codex plugin list | grep -q 'rocksoft-koda@rocksoft-koda.*installed, enabled.*0.6.0' && codex mcp list | grep -q 'rocksoft-koda.*mcp.rocksoft.pl/koda/'` (a "helper binaries under temporary dir" warning is harmless)
- Codex lists the skill: with the same `CODEX_HOME`, `codex debug prompt-input hi | grep -q 'rocksoft-koda:rs-feature'`
- No secrets in plugin files: `! grep -rniE "secret|token|password|api[_-]?key" .codex-plugin .agents .claude-plugin .mcp.json`
#### Manual
- On a machine with the merged default branch, `codex plugin marketplace add Rocksoft-IT/rocksoft-koda-plugin` finds `rocksoft-koda` (remote Git snapshot path, not testable before merge)

## Phase 2: Agent-neutral rs-feature
### Overview
Remove Claude-only assumptions from `SKILL.md` and give each host correct sign-in
and tenant-access instructions.

### Required changes
#### 1. Runtime assumptions
- **File**: `skills/rs-feature/SKILL.md` (Runtime assumptions)
- **Goal**: Describe the hosts (Claude Desktop, claude.ai, Claude Code, Codex CLI,
  Codex IDE extension, Codex cloud) and keep "design for the weakest": no local
  files, shell or git even where the host offers them; MCP tools only.
- **Contract**: questions are plain chat with numbered options (recommended first,
  last "Not sure / let's come back to this"); a structured question tool may be
  used only if the host offers one, never named. Identity wording points to the
  new sign-in section instead of `/mcp`.

#### 2. Signing in, per host (new section)
- **File**: `skills/rs-feature/SKILL.md`
- **Goal**: One place with the exact sign-in and switch-account steps per host.
- **Contract**: Claude Desktop / claude.ai (Connect on the Rocksoft Koda
  connector; admin on Team/Enterprise), Claude Code (`/mcp`), Codex CLI and IDE
  extension (`codex mcp login rocksoft-koda`, `--no-browser` for headless; check
  with `codex mcp list`; new session afterwards), Codex cloud / ChatGPT (connect
  Rocksoft Koda from its plugin page; a workspace admin installs the plugin
  first). Switching accounts: Claude `/mcp` reconnect; Codex `codex mcp logout
  rocksoft-koda` then login. Pick the host's lines from context; when the host
  is unknown, show the Claude and Codex lines.

#### 3. Not-signed-in and tenant-access outcomes
- **File**: `skills/rs-feature/SKILL.md` (Handling tenant-access outcomes, Step 0,
  Step 1 "tool missing", Step 6)
- **Goal**: "No Rocksoft Koda tools, or a tool call fails with a sign-in /
  unauthorized error" → the per-host sign-in lines, then stop. `pending`,
  `not_allowed`, `revoked` keep their meaning and stop behaviour; `not_allowed` /
  `revoked` add "if you signed in with a different Microsoft account than your
  organization's, switch account (see Signing in)".
- **Contract**: no change to tool names, arguments, labels, the single yes before
  `create_feature_issue`, or the rule that identity is never asked or sent.

### Success criteria
#### Automated
- No Claude-only tool name remains: `! grep -n "AskUserQuestion" skills/rs-feature/SKILL.md skills/rs-feature/references/*.md`
- Codex sign-in path present: `grep -q "codex mcp login rocksoft-koda" skills/rs-feature/SKILL.md` and `grep -q "Not sure / let's come back to this" skills/rs-feature/SKILL.md`
- Claude path still present: `grep -q '/mcp' skills/rs-feature/SKILL.md`
- Frontmatter unchanged: `diff <(git show $(git merge-base HEAD main):skills/rs-feature/SKILL.md | awk '/^---$/{n++} n<2') <(awk '/^---$/{n++} n<2' skills/rs-feature/SKILL.md)`
- Behavioural anchors intact: `grep -q "Shall I create this issue" skills/rs-feature/SKILL.md`, `grep -q "Never ask for or send an" skills/rs-feature/SKILL.md`, `grep -q "Guardrails" skills/rs-feature/SKILL.md`
- The skill still loads in Codex: after reinstalling into a fresh `CODEX_HOME` (the Phase 1 command), `codex debug prompt-input hi | grep -q 'rocksoft-koda:rs-feature'`
#### Manual
- A reviewer reads the diff and confirms Steps 1-6 and the Guardrails differ only in the wording the Contract above names, and that no sentence still makes `/mcp` the only sign-in path
- In Codex CLI with the plugin installed and not logged in, asking for a change gets the Codex sign-in instructions and the skill stops (AC-03)

## Phase 3: README, USAGE and supporting docs
### Overview
Document install, sign-in and update for Claude and Codex (Polish, matching the
existing docs) and mirror the version.

### Required changes
#### 1. README
- **File**: `README.md`
- **Goal**: Say the plugin works in Claude and Codex; add Codex install and
  update (CLI, IDE extension, cloud) next to the Claude sections; list the new
  manifest files in the structure tree; version `0.6.0`.
- **Contract**: Codex CLI: `codex plugin marketplace add
  Rocksoft-IT/rocksoft-koda-plugin`, `codex plugin add rocksoft-koda@rocksoft-koda`
  (or `/plugins`), `codex mcp login rocksoft-koda`; update: `codex plugin
  marketplace upgrade rocksoft-koda` then `codex plugin add
  rocksoft-koda@rocksoft-koda` again, new session. IDE extension (no plugin
  browser): same MCP config as CLI (`codex mcp add rocksoft-koda --url
  https://mcp.rocksoft.pl/koda/`, `codex mcp login rocksoft-koda`) and the skill
  folder `skills/rs-feature` copied to `~/.agents/skills/rs-feature`; do not
  combine with the plugin install (duplicate server). Cloud: workspace admin
  imports `https://github.com/Rocksoft-IT/rocksoft-koda-plugin` (Admin > Plugins >
  Import marketplace, no path), members install and Connect; note the possible
  "Desktop only" label. Access is enforced by the gateway, not the plugin.

#### 2. USAGE
- **File**: `USAGE.md`
- **Goal**: Mirror the install/sign-in per host; make step "Kto zgłasza" and the
  troubleshooting table host-neutral (sign-in via the host's sign-in, with Codex
  rows for "not signed in", `pending`, `not_allowed`/`revoked`); version `0.6.0`.
- **Contract**: all existing Claude instructions remain, unchanged in meaning.

#### 3. Supporting docs
- **File**: `docs/flow-contract.md` (the `/mcp` sentence only),
  `context/foundation/tech-stack.md` (mention the Codex manifests and the
  server name `rocksoft-koda`)
- **Goal**: Keep descriptive text true; no contract or schema change.
- **Contract**: `docs/flow-contract.md` tool and error shapes untouched.

### Success criteria
#### Automated
- Version consistent everywhere: `grep -q '0\.6\.0' README.md USAGE.md .codex-plugin/plugin.json .claude-plugin/plugin.json && ! grep -rn '0\.5\.0' README.md USAGE.md .codex-plugin .claude-plugin skills docs`
- Codex install steps documented: `grep -q "codex plugin marketplace add Rocksoft-IT/rocksoft-koda-plugin" README.md USAGE.md` and `grep -q "codex mcp login rocksoft-koda" README.md USAGE.md`
- Claude steps kept: `grep -q "claude plugin install rocksoft-koda@rocksoft-koda" README.md USAGE.md`
- Structure tree lists the new files: `grep -q ".codex-plugin" README.md` and `grep -q ".agents" README.md`
- Tool contract untouched: `test "$(git diff --numstat $(git merge-base HEAD main) -- docs/flow-contract.md | awk '{print $1+$2}')" -le 6` (only the one `/mcp` sentence changes)
#### Manual
- Codex cloud: a workspace admin imports the repository and a member connects Koda and runs rs-feature to an issue (AC-02); depends on mcp-gateway#26 accepting the cloud OAuth callback
- Codex CLI end to end with an active-tenant account: install, sign in, ask for a change, get an issue after an explicit yes (AC-01)

## Testing Strategy
No code or test suite exists (`context/foundation/tech-stack.md`). Verification is
structural (JSON validity, version equality, grep anchors) plus a real Codex CLI
smoke test in an isolated `CODEX_HOME` (marketplace add, plugin add/list, MCP list,
skill listed). Sign-in, cloud import and end-to-end issue creation need a Rocksoft
account and are Manual.

## Performance Notes
None.

## Migration Notes
None. Existing Claude installs update by version bump; nothing is renamed or removed.

## References
- `change.md` (issue #12, verbatim); `docs/flow-contract.md`
- OpenAI docs: developers.openai.com/codex/plugins, /plugins/build/plugins,
  /plugins/deploy/submission, /codex/mcp, /codex/skills;
  learn.chatgpt.com/docs/enterprise/plugin-management and /docs/environments/cloud-environments
- Rocksoft-IT/mcp-gateway#26 (OAuth callbacks for Codex)

## Progress

### Phase 1: Codex manifest, marketplace and version bump
#### Automated
- [x] 1.1 Both manifests and the marketplace parse as JSON — 531dfe8
- [x] 1.2 Versions match — 531dfe8
- [x] 1.3 Claude files are otherwise untouched — 531dfe8
- [x] 1.4 Codex installs it from the working tree — 531dfe8
- [x] 1.5 Codex lists the skill — 531dfe8
- [x] 1.6 No secrets in plugin files — 531dfe8
#### Manual
- [ ] 1.7 On a machine with the merged default branch, `codex plugin marketplace add Rocksoft-IT/rocksoft-koda-plugin` finds `rocksoft-koda` (remote Git snapshot path, not testable before merge)

### Phase 2: Agent-neutral rs-feature
#### Automated
- [x] 2.1 No Claude-only tool name remains — 6d64944
- [x] 2.2 Codex sign-in path present — 6d64944
- [x] 2.3 Claude path still present — 6d64944
- [x] 2.4 Frontmatter unchanged — 6d64944
- [x] 2.5 Behavioural anchors intact — 6d64944
- [x] 2.6 The skill still loads in Codex — 6d64944
#### Manual
- [ ] 2.7 A reviewer reads the diff and confirms Steps 1-6 and the Guardrails differ only in the wording the Contract above names, and that no sentence still makes `/mcp` the only sign-in path
- [ ] 2.8 In Codex CLI with the plugin installed and not logged in, asking for a change gets the Codex sign-in instructions and the skill stops (AC-03)

### Phase 3: README, USAGE and supporting docs
#### Automated
- [x] 3.1 Version consistent everywhere — 54cf8af
- [x] 3.2 Codex install steps documented — 54cf8af
- [x] 3.3 Claude steps kept — 54cf8af
- [x] 3.4 Structure tree lists the new files — 54cf8af
- [x] 3.5 Tool contract untouched — 54cf8af
#### Manual
- [ ] 3.6 Codex cloud: a workspace admin imports the repository and a member connects Koda and runs rs-feature to an issue (AC-02); depends on mcp-gateway#26 accepting the cloud OAuth callback
- [ ] 3.7 Codex CLI end to end with an active-tenant account: install, sign in, ask for a change, get an issue after an explicit yes (AC-01)
