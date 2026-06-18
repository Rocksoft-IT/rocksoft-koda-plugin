---
name: rs-change
description: >
  Initialize a new change folder under context/changes/[change-id] with a
  change.md identity file. A "change" is one unit of work end to end — research,
  framing, planning, implementation, and review all live in one folder keyed by
  the change-id. Use to start a new piece of work before planning. Trigger
  phrases: "new change", "start a change", "open a change folder", "begin a change".
argument-hint: "[change-id-or-path] [freeform intent]"
allowed-tools:
  - Read
  - Glob
  - Write
  - Bash
  - AskUserQuestion
  - mcp__*
---

# rs-change: Start a new change

Open a new change folder at `context/changes/<change-id>/` with a small identity
file (`change.md`) and point the user to the next skill. A change is a single
unit of work; its research, frame, plan, reviews, and other artifacts all live in
this one folder.

## Initial response

If an argument is given, parse it (below) and go to Validation. If none, print:

```
I'll create a new change folder. Please provide a change-id (kebab-case slug):

Examples:
  rs-change context-dir-restructure
  rs-change oauth-login add Google sign-in so users skip the email-password step
  rs-change @context/changes/oauth-login/

The first token becomes the change-id. Anything after it is freeform intent —
used to write a richer title and to pick the next-step suggestion. Path-style
references (with or without a leading @) are accepted; the last path segment is
used as the change-id.

The change-id must be kebab-case and unique across context/changes/ and
context/archive/. I'll also ask for your email and target repository — they bind
the change so it can be merged back via a server-side PR at the end.
```

Then wait.

## Argument parsing

Split on the first whitespace:

- **First token** = the change-id reference. Normalize: strip a leading `@`,
  strip a trailing `/`, and if it still contains `/` take the last path segment.
- **Everything after** = freeform intent (may be empty). A hint for the title and
  the next-step suggestion — NOT a literal title to paste whole.

## Validation

1. **Kebab-case:** `<change-id>` must match `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`. Else
   print `error: change-id "<id>" is not kebab-case…` and STOP.
2. **Uniqueness:** neither `context/changes/<change-id>/` nor an
   `context/archive/*-<change-id>/` may exist. On collision print `error: change
   "<id>" already exists at <path>…` and STOP.
3. **Parent exists:** `context/changes/` must exist (run `rs-init` if not). Do NOT
   auto-create the parent.

## Identity: client email & repository (REQUIRED)

A change is merged at the end of its lifecycle by a **server-side PR** through
the Rocksoft Flow MCP server (`rocksoft-mcp`) — the Claude runtime has no `git`
and no credentials to the repo, so the merge cannot happen locally. The change
must therefore be bound to a **client email** and a **target repository** up
front, and both travel in `change.md` frontmatter so the closing step knows
whom it's for and where to merge. Run this **one sub-step at a time** — never a
wall of questions. There is **NO skip option**: without an email there is no way
to list repositories, and without a repository there is nothing to merge into.

This mirrors `rs-discovery` Step 0.7a–c — keep the two entry skills consistent.

### Client email (REQUIRED)

Ask: "What's your email? I'll record it as the client / driver of this change,
and use it to pull your repositories from Rocksoft Flow." If the harness
provides a known user email, propose it as the recommended AskUserQuestion
option (first, "(Recommended)") — never silently auto-fill, always confirm.

Validate the shape (contains `@` and a dot in the domain part). Re-ask until
valid — there is no skip. If the user explicitly refuses, STOP: "An email is
required to look up your repositories in Rocksoft Flow. Re-run `rs-change` when
you're ready to provide one."

### Pick the repository (REQUIRED)

With the email in hand, call the Rocksoft Flow MCP server to list repositories
for that email. Look for a tool like `list_repositories` (read its schema before
calling; pass the email exactly as the field name expects). Show the returned
repos via AskUserQuestion — label `<repo-name>`, description `<git_url> —
<description?>` — in the order the MCP returned them. There is **no "standalone"
/ "none" option**.

If the tool is unreachable, not exposed, or returns no repos, the change
**cannot be bound** — print the problem in plain language and STOP, offering
retry:

- **Tool not exposed:** "Rocksoft Flow MCP is connected but `list_repositories`
  isn't exposed — I can't bind this change. Ask the Rocksoft Flow admin to wire
  it in n8n, then re-run `rs-change`."
- **Connection / network error:** print the error verbatim, then "I couldn't
  reach Rocksoft Flow to list your repositories. Want to retry?" (retry / abort).
- **Empty list:** "Rocksoft Flow doesn't have any repositories for `<email>`
  yet. Ask the Rocksoft admin to add one, then re-run `rs-change`." STOP.

On selection, capture both `repository.name` and `repository.git_url` for the
frontmatter — use the `git_url` **verbatim** as returned, never rewrite it.

## Creation

1. `mkdir -p context/changes/<change-id>/`.
2. Derive `<title>`: empty intent → humanize the change-id (hyphens → spaces,
   sentence case). Non-empty intent → a concise ≤80-char sentence-case title that
   captures the essence (rephrase freely; don't dump a paragraph).
3. Derive the `## Notes` body: empty intent → the hint comment `<!-- Free-form
   notes for this change: links, ad-hoc context, decisions that don't belong in
   research/frame/plan. -->`. Non-empty intent → paste the user's words verbatim
   as the Notes body (no hint comment).
4. Write `context/changes/<change-id>/change.md` exactly (`client`,
   `repository.name`, `repository.git_url` come from the Identity section — none
   may be empty or `(none)`):

```markdown
---
change_id: <change-id>
title: <title>
client: <client-email>
repository:
  name: <repo name>
  git_url: <git url>
status: new
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
archived_at: null
---

## Notes

<notes-body>
```

`<YYYY-MM-DD>` is today (`date +%Y-%m-%d`).

## Next-step suggestion

Default next step is `rs-plan <change-id>` — most changes go straight to planning.
The two situational options: `rs-research <change-id>` when the intent suggests
the change needs significant codebase exploration before a plan can be written;
`rs-frame <change-id>` when the intent signals the framing is suspect — a bug
shape ("fix", "bug", "broken", "root cause", "regression") or a scope/design
shape ("should we even", "is this the right", "rethink", "challenge the
assumption"). Pick a situational option only when the signal is clear; otherwise
default to `rs-plan`. Copy the chosen command to the clipboard and print:

```
✓ Created context/changes/<change-id>/change.md (status: new)
  bound to <repository.name> · driven by <client>

Next step:
  → <NEXT_CMD>  (✓ copied to clipboard)

Other options:
  rs-research <change-id>   — explore the codebase first (when planning needs grounding)
  rs-frame <change-id>      — challenge the framing first (bug+fix stated as one, or unclear scope)
```

## What this skill does NOT do

- It does not open or merge the PR. It only **binds** the change to a client
  email and repository (in `change.md` frontmatter); the server-side merge PR
  via Rocksoft Flow MCP happens at the closing step of the change lifecycle.
- It does not write `frame.md`, `research.md`, or `plan.md` — those come from
  their own skills.
- It does not write any sidecar state file; `## Progress` in `plan.md` is the
  single source of execution state.
- It does not enforce status transitions; `change.md` is append-friendly identity.
- It does not create the `context/changes/` parent — run `rs-init` if it's missing.
