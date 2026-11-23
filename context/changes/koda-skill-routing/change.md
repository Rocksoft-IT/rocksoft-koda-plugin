---
change_id: koda-skill-routing
title: Koda routes work to the right Rocksoft skill and flags overlaps
status: implementing
created: 2026-11-23
updated: 2026-11-23
archived_at: null
---

## Notes

https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/14

<!-- rs-feature · track: initiative · client: piotr@rocksoft.pl · repository: Rocksoft Koda Plugin · feature: 7c3e9a52-4b1d-4f8e-9a27-5d6c1e8b0f43 -->

## Summary

A client team should get Rocksoft's way of working just by enabling Koda in their repository: no manual skill installs, no remembering which skill to run when. Koda installs rs-skills alongside itself, recognizes what the developer wants to do and starts the right path, warns once when other skills overlap with ours, and presents Rocksoft as a partner the team can reach at any moment. Each client chooses whether changes are built locally in the developer's session or server-side by Koda.

## Problem & context

- **Who:** client developers (Fide-Platform first) using Claude Code or Codex in their own repo. Today they must know rs-* skill names and order; Fide's own `/orchestrate` and `/preflight` overlap with rs-orchestrator and rs-impl_review and nothing tells them which to use.
- **Current system:** rocksoft-koda 0.6.0 is chat-only: one skill (`rs-feature`) plus the `rocksoft-koda` MCP server; README states the plugin never reads local files (a description of the chat-only design, not a security rule). Marketplaces exist for Claude (`.claude-plugin/marketplace.json`) and Codex (`.agents/plugins/marketplace.json`). No hooks, no dependencies, no CI.

## Scope

### In scope

1. Client adds the Koda marketplace and enables `rocksoft-koda` in project settings; installing Koda also brings rs-skills. Claude: `dependencies` on the rs-skills package listed in the same marketplace (`git-subdir`, pinned to a release tag), marketplace `autoUpdate`. Codex has no plugin dependencies: the Koda Codex marketplace lists both `rocksoft-koda` and the rs-skills Codex package (`git-subdir`, pinned `ref`); the client project enables both in `.codex/config.toml`.
2. On session start, Koda reads the repo state (branch, open changes under `context/changes/`, `.rocksoft/koda.json`, installed skills/commands/agents) and gives the model a short routing map and the next step.
3. When a prompt looks like work ("add", "fix", "legg til", "popraw"…), Koda adds a routing hint so the model starts the right path; the hint never blocks or rewrites the prompt.
4. On the first change request in a repo without a saved mode, Koda asks once — local (rs-orchestrator in the session) or server-side (rs-feature → Koda builds) — and writes the answer to a tracked `.rocksoft/koda.json`.
5. Koda doctor compares installed skills, commands and agents (other plugins, `~/.claude/skills`, repo `.claude/skills|commands`, `.agents/skills`) with rs-* capabilities and shows one notice when the set changes; when two candidates fit a request equally, Koda asks one question and remembers the choice (repo-level policy in `.rocksoft/koda.json`, personal choices in an untracked local file).
6. Koda ships a shared `AGENTS.md` section template (works for Claude and Codex; `CLAUDE.md` points to it) describing the Koda workflow and the one-time install steps per host, promoting Rocksoft skills, and presenting Rocksoft as a partner available at any time: through Koda itself (rs-feature also accepts questions and help requests) or at koda@rocksoft.pl.
7. README is updated: in chat the plugin works only through Rocksoft Flow; in Claude Code and Codex its hooks read local repo state to pick the right skill, send nothing and change no code.

### Out of scope (non-goals)

- Building the rs-skills client packages — rs-skills issue.
- Any network call or API key in hooks (no OpenRouter/Jev classifier) — routing stays local and model-decided.
- Hooks in Claude Desktop chat / claude.ai — not supported there; rs-feature keeps working as today.

## Related repositories

- **RS Skills** (`rs-skills`): publishes the public Claude/Codex packages Koda depends on and scopes its guards to rs-* runs — Rocksoft-IT/rs-skills#73.
- **Fide-Platform** (`Fide-Platform`): first client enabling Koda in project settings and adding the shared `AGENTS.md` section (issue "Fide developers get Rocksoft Koda and rs-skills automatically in this repo", to be created next).

## Access & roles

No change to the MCP access model. `.rocksoft/koda.json` is edited by the client team through normal PRs.

## Success criteria

- **Primary:** a Fide developer types "add X" in Claude Code or Codex and the right path starts (local orchestrator or rs-feature, per the repo's mode) without naming a skill.
- **Secondary:** overlaps (e.g. Fide `/preflight` vs `rs-impl_review`) are reported once with a resolution rule.
- **Guardrails:** hooks never block prompts, never send data, fail open on any error; chat hosts behave exactly as today; session start stays fast.

## Requirements

- FR-001: Client developer gets rs-skills installed together with Koda (Claude via dependency, Codex via both plugins in the Koda marketplace). Priority: must-have. Change: new
- FR-002: In Claude Code, Koda and rs-skills update on session start via marketplace auto-update, pinned to release tags chosen by Rocksoft. Priority: must-have. Change: new
- FR-003: Koda injects a routing map and next step at session start based on local repo state. Priority: must-have. Change: new
- FR-004: Koda adds a routing hint to work-like prompts without blocking or altering them. Priority: must-have. Change: new
- FR-005: Koda asks once for the delivery mode and stores it in tracked `.rocksoft/koda.json`. Priority: must-have. Change: new
- FR-006: Koda doctor reports overlapping skills/commands/agents once per change of the installed set. Priority: must-have. Change: new
- FR-007: When two candidates fit equally, Koda asks one question and remembers the answer. Priority: must-have. Change: new
- FR-008: Koda provides a shared `AGENTS.md` section template for Claude and Codex with Rocksoft partner messaging and contact koda@rocksoft.pl. Priority: must-have. Change: new
- FR-009: Client can still use rs-feature in Claude Desktop / claude.ai / Codex cloud exactly as today. Priority: must-have. Change: preserved
- FR-010: In Codex, Koda's SessionStart hook reminds the developer to run `codex plugin marketplace upgrade rocksoft-koda` when a newer release is available (Codex has no auto-update). Priority: nice-to-have. Change: new

## Acceptance criteria

### AC-01: One install, both plugins

- **Given** a repo whose project settings add the Koda marketplace and enable `rocksoft-koda`
- **When** a developer installs Koda
- **Then** rs-skills is installed too and rs-* skills are available (and agents, in Claude Code)

### AC-02: First change request asks for the mode

- **Given** a repo without `.rocksoft/koda.json`
- **When** the developer asks for a change
- **Then** Koda asks local vs server-side once, writes the answer to `.rocksoft/koda.json`, and continues on that path

### AC-03: Saved mode routes silently

- **Given** `.rocksoft/koda.json` says `server`
- **When** the developer writes "fix the invoice total rounding"
- **Then** rs-feature starts without the developer naming it

### AC-04: Questions are not routed

- **Given** any mode
- **When** the developer asks "how does invoice rounding work?"
- **Then** no change path starts

### AC-05: Overlap reported once

- **Given** the repo has `/preflight` and rs-impl_review is installed
- **When** a session starts after the installed set changed
- **Then** the developer sees one notice naming the overlap and the resolution rule; the next session with the same set shows nothing

### AC-06: Ambiguity asks once

- **Given** two installed skills fit a request equally and no rule decides
- **When** the developer makes that request
- **Then** Koda asks one question with both options and does not ask again for the same pair

### AC-07: Hook failure is harmless

- **Given** a hook script errors or times out
- **When** the session starts or a prompt is sent
- **Then** the session continues normally without Koda's hint

## Constraints & preserved behavior

- `rs-feature` flow, MCP tools and tenant-access handling unchanged.
- Claude and Codex manifests keep the same version.
- Hooks read only; the only writes are `.rocksoft/koda.json` (after the user answers) and local cache/choice files outside tracked code.
- Cross-marketplace dependency avoided: the rs-skills package is listed in the Koda marketplace.
- Codex: plugin hooks run only after each developer trusts them once (`/hooks`); `AGENTS.md` has no import syntax, so `AGENTS.md` is the source and `CLAUDE.md` points to it.

## Non-functional requirements

- Session-start hook adds well under a second.
- Nothing leaves the developer's machine from hooks.

## Open questions

- Codex docs state plugin hooks for Codex desktop; behavior in Codex CLI must be verified.
- How the Codex upgrade reminder learns about a newer release without a network call.
- Behavior of project-scoped marketplaces in the Claude Desktop Code tab and in cloud sessions (cloud sessions do not add project marketplaces).
- `enabledPlugins` alone does not install; each developer runs one install command per clone (accepted) — documented in the template.

## Glossary

**Delivery mode**: per-repo choice of where changes are built — `local` (rs-orchestrator in the developer's session) or `server` (rs-feature issue, built by Koda). _Avoid_: execution type

**Koda doctor**: the check that compares installed skills, commands and agents with rs-* capabilities and reports overlaps. _Avoid_: linter

**Routing map**: the short context Koda injects that maps intents to paths. _Avoid_: prompt

## Decisions

### ADR-0001: local-model-routing

Routing is done by hooks that only read local state and add context; the model makes the choice. No external classifier, because clients have no API key, hooks cannot reuse the MCP sign-in, and nothing should leave the client's machine.

### ADR-0002: mode-in-repo

The delivery mode lives in a tracked `.rocksoft/koda.json`, asked once, so the whole client team shares one decision and changes it through a PR.

## Metadata

- **Client:** piotr@rocksoft.pl
- **Repository:** Rocksoft Koda Plugin (git@github.com:Rocksoft-IT/rocksoft-koda-plugin.git)
- **Feature:** 7c3e9a52-4b1d-4f8e-9a27-5d6c1e8b0f43
- **Track:** initiative
- **Product type:** Claude Code / Codex plugin
- **Target scale:** unchanged
- **Created with:** rocksoft-koda rs-feature 0.6.0

---
<!-- rs-feature:meta -->
- client: piotr@rocksoft.pl
- requested-by: piotr@rocksoft.pl
- track: initiative
- plugin: rocksoft-koda/rs-feature 0.6.0
- created: 2026-11-23T09:25:29.251Z
- feature: 7c3e9a52-4b1d-4f8e-9a27-5d6c1e8b0f43
