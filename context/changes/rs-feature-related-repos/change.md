---
change_id: rs-feature-related-repos
title: Rs-feature shapes requests across related repositories
status: implementing
created: 2026-11-13
updated: 2026-11-13
archived_at: null
---

## Notes

https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/5

<!-- track: feature · client: piotr@rocksoft.pl · repository: Rocksoft Koda Plugin · parked: add the rs-feature label to start Koda -->

## Summary

`rs-feature` should use the related repositories that Koda's repository directory will expose, so a request spanning several repositories is understood with all their context and ends up as one issue per repository instead of being split by hand.

## Problem & context

- **Today:** `rs-feature` binds the conversation to one repository from `list_repositories` and reads only its context via `get_repository_context`. A change that touches e.g. the n8n workflows, the MCP gateway and this plugin has to be split manually.
- **Depends on:** the `related_repositories` field and `include_related` flag from Rocksoft-IT/n8n-hosting#130.

## Scope

### In scope

1. After the client picks a repository, `rs-feature` shows its related repositories and reads their context with `include_related`. Related repositories come from `related_repositories`, not from the top-level `repositories` list: the client may not be assigned to them and still has full access (decided in Rocksoft-IT/n8n-hosting#130).
2. It asks the client which of the related repositories the request touches (never assumes).
3. The issue body gets a **Related repositories** section listing them with one line on what changes in each.
4. When the request needs changes in more than one repository, `rs-feature` proposes one issue per repository, each cross-linking the others, with the deploy order. Issues may target related repositories the client is not assigned to (`create_feature_issue` accepts them, n8n-hosting#130); every issue is still submitted only after explicit confirmation.
5. `docs/flow-contract.md` and `references/issue-template.md` document the new field, flag and section.

### Out of scope (non-goals)

- Server-side directory and tool changes — Rocksoft-IT/n8n-hosting#130.

## Acceptance criteria

### AC-01: Related context used
- **Given** the chosen repository has related repositories, whether or not the client is assigned to them
- **When** rs-feature starts the conversation
- **Then** it names them and uses their context when shaping the request

### AC-02: Multi-repository request
- **Given** the client confirms the request touches two related repositories
- **When** the issue is drafted
- **Then** two cross-linked issues with a deploy order are proposed and created only after confirmation

### AC-04: Issue in a related repository the client is not assigned to
- **Given** the client is assigned to n8n-hosting only, and mcp-gateway is related to it
- **When** the request touches mcp-gateway and the client confirms the draft
- **Then** the issue is created in mcp-gateway

### AC-03: No related repositories
- **Given** a repository without relations, or an older server without the field
- **When** rs-feature runs
- **Then** it behaves exactly as today

## Constraints & preserved behavior

- Works against servers that do not yet return `related_repositories` (field missing = no relations).
- Only repositories from `repositories` or `related_repositories` may be targeted; never a `git_url` the client typed in.

## Sequencing

**Parked.** Start after Rocksoft-IT/rocksoft-koda-plugin#4 (gateway sign-in) and Rocksoft-IT/n8n-hosting#130 are merged. Add the `rs-feature` label to start Koda.

## Metadata

- **Client:** piotr@rocksoft.pl
- **Repository:** Rocksoft Koda Plugin (https://github.com/Rocksoft-IT/rocksoft-koda-plugin)
- **Track:** feature
- **Related:** Rocksoft-IT/n8n-hosting#130, Rocksoft-IT/rocksoft-koda-plugin#4, Rocksoft-IT/n8n-hosting#129

### Areas (from orchestrator)

A1 rs-feature related-repositories flow — extend the rs-feature skill conversation to discover a chosen repository's related repositories (via `related_repositories`/`include_related` from the Koda directory server, already shipped per Rocksoft-IT/n8n-hosting#130), confirm with the client which related repos the request touches, add a Related repositories section to the issue body, support proposing/creating one cross-linked issue per repository (including repos the client is not assigned to) with a deploy order, and update docs/flow-contract.md and skills/rs-feature/references/issue-template.md accordingly; builds on nothing (no other area)
