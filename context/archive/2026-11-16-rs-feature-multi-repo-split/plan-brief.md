# Rs-feature picks the right client repository and splits multi-repo requests — Plan Brief
Full plan: `context/changes/rs-feature-multi-repo-split/plan.md` · issue text: `change.md`

## What & why
`list_repositories` now returns each repository's `role`, `description` and
`client` (Rocksoft-IT/n8n-hosting#159). Today `rs-feature` shows a client's
repositories as one flat list and always asks when there is more than one,
and has no way to split a request across two repositories of the same
client as one tracked feature. This change groups the list by client, lets
an obvious request pick its repository without asking, and — when a request
spans more than one repository of the same client — splits it into one
issue per repository, all tagged with a shared `feature` id so the Cezar
Pipeline (Rocksoft-IT/cezar#257) shows them as one feature.

## Starting point
`skills/rs-feature/SKILL.md` Step 1 lists repositories flat (name +
description) and always asks when there is more than one; Step 2 already
asks once about *configured* `related_repositories` and carries the answer
as "touched repositories"; Steps 5-6 already draft/create one issue per
touched repository with a `## Related repositories` section, but with no
shared id across the batch and no notion of same-client siblings.

## Desired end state
Step 1 groups by `client`, shows `role`/`description`, and auto-picks on a
clear match. Step 2's existing question also offers same-client siblings
and, once the touched set has more than one repository, the skill generates
one `feature` UUID itself. Steps 5-6 carry that id in every draft's footer
and Metadata, name siblings by role first, and pass `feature` to every
`create_feature_issue` call of the batch — only ever combining repositories
of one client in a same-client split. `docs/flow-contract.md` documents the
new fields; the plugin version moves to `0.5.0`.

## Complexity
MEDIUM — four phases across one skill file (`SKILL.md`, at Steps 1, 2, 5, 6)
plus two reference docs; no code, no build, no tests, but several
non-obvious conversation-design decisions (auto-pick without asking, merging
two sibling-discovery sources into one question, where the shared id lives,
and how far it extends into the already-shipped related-repos path).

## Key decisions made
| Decision | Choice | Why | Source |
|---|---|---|---|
| Skip rs-research | Yes | Jev was unsure (p=0.42); the issue names the exact mechanism and the three files it touches, all already read in full, and the repo is a tiny markdown/JSON-only plugin — same reasoning the prior archived related-repos change used | Jev (p=0.42) + Auto |
| Skip rs-frame | Yes | Jev was unsure (p=0.32); pure feature-shape issue, no stated bug, no disputed scope — same reasoning as the prior change | Jev (p=0.32) + Auto |
| Where repo choice vs. split live | Repo choice (grouping, auto-pick) in Step 1 only; split discovery in Step 2, reusing its existing question | Mirrors the issue's own two numbered points, and Step 2 already owns the "touched repositories" concept | Issue |
| Auto-pick without asking on a clear role/description match | Yes, with a one-line "picked X because Y" | Issue's explicit wording ("pick the repository yourself... say which one you picked and why"); a deliberate change from today's "always ask, just recommend first" | Issue |
| Same-client siblings join the *existing* related-repos question (one combined question) | Yes, one question, two candidate sources | Reuses already-shipped "touched repositories" plumbing in Step 5/6 instead of a second near-identical flow; keeps the "one question at a time" / bounded-conversation principles | Auto |
| Shared `feature` id applies to *any* multi-issue batch, not only same-client splits | Yes | Gives the Cezar Pipeline one consistent grouping signal for every split (fits cezar#257's purpose); avoids a hidden internal flag forking Step 5/6's logic | Auto (decision-to-verify: extends the already-shipped related-repos path beyond issue #10's literal wording) |
| "Same client only" gates the new source, not the pre-existing `related_repositories` allowance | Yes | The prior change's AC-04 already lets a related repo be one the client isn't directly assigned to; narrowing that now would silently break an accepted behavior the current issue never mentions | Auto |
| Feature id generation | Model generates a UUID v4 itself, as text, once per request — no tool call | The skill has no shell/file access (Runtime assumptions); there is no MCP tool for this | Auto |
| Sibling naming in `## Related repositories` | Lead with role when known, else fall back to name | Issue: "names the other parts by role"; role is absent on `related_repositories` siblings, so the fallback preserves today's format there | Issue + Auto |
| `feature` as both a tool argument and drafted body text | Yes, mirrored in footer + Metadata | Matches how `track`/`client` already work today: both an argument and drafted text | Auto |
| Version bump | `0.4.0` → `0.5.0`, mirrored into README/USAGE footers, no new prose | Project precedent (every user-visible change bumps it); issue names only `flow-contract.md`/`issue-template.md` for doc content | Auto |

## Scope
**In:** SKILL.md Steps 1, 2, 5, 6; `issue-template.md`'s footer, Metadata,
and `## Related repositories` line format; `docs/flow-contract.md`; version
bump across three files.
**Out:** n8n-hosting#159's own server-side logic; Cezar Pipeline's grouping
UI (cezar#257); the already-shipped `related_repositories` mechanism's own
question/allowances (#5); an issue-edit tool; `references/tracks.md`; new
README/USAGE prose.

## Architecture / Approach
One increment, one area (per the orchestrator's `Areas:` block). Direct
extension of the existing four SKILL.md steps plus the two reference docs,
reusing the "touched repositories" / draft-many/create-many machinery the
prior related-repos change already built, rather than adding a parallel
flow.

## Open risks & assumptions
- Applying the shared `feature` id to the pre-existing `related_repositories`
  split path too (not only the new same-client source) is a deliberate
  consistency choice beyond the issue's literal wording — flagged as
  `decision-to-verify`.
- `list_repositories`'s exact `role`/`client` shape and `create_feature_issue`'s
  `feature` input are assumed by symmetry with the fields `docs/flow-contract.md`
  already documents; Rocksoft-IT/n8n-hosting#159 is an external repo not in
  this checkout.
