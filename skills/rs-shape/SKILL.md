---
name: rs-shape
description: >
  Run a structured discovery conversation that turns a raw idea — greenfield or
  brownfield — into a small set of shared-context artifacts under
  context/discovery/. Auto-detects context type from project markers in the
  working directory (brownfield) or their absence (greenfield) and adapts the
  discovery phases accordingly. For brownfield, explores the codebase before
  asking. Captures ubiquitous language inline as a glossary and records
  hard-to-reverse decisions as ADRs. Use when starting a new project from
  scratch OR shaping a meaningful change to an existing system (new module,
  significant feature, architectural improvement). Trigger phrases: "new
  project", "from scratch", "starting an app", "shape an idea", "discovery
  session", "grill me on this", "greenfield", "existing project", "brownfield",
  "add a feature to my app".
argument-hint: "[freeform idea or @path/to/notes.md]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
  - mcp__*__upload_spec
  - mcp__*__create_spec
  - mcp__*
---

# rs-shape: Discovery conversation for greenfield and brownfield

This skill turns "I have an idea" (greenfield) or "I want to change this system"
(brownfield) into a small, durable set of context artifacts a team — human or
agent — can build on. It is a **facilitator and an interviewer**, not a content
generator. It never writes vision, requirements, or domain rules the user did
not say. Its value is in the shape and order of the questions, not in the
answers it volunteers.

It blends two complementary approaches:

- **Phased, gated discovery** (greenfield/brownfield detection, scope discipline,
  named anti-patterns, a soft quality gate, resumable checkpoints).
- **Relentless one-at-a-time grilling** with codebase exploration, ubiquitous
  language captured inline, and architecture decisions recorded only when they
  matter.

## Output artifact

This skill writes ONE file — everything lives together so the discovery is
trivially shareable, diffable, and searchable:

```
context/discovery/
└── discovery-notes.md        ← the single shape document — vision, persona,
                                success criteria, FRs, business logic,
                                non-goals, glossary, and decisions/ADRs
```

The structure of `discovery-notes.md` is defined in
`references/discovery-notes-template.md` (relative to this SKILL.md). Read it
before writing the first artifact and re-check it at every checkpoint. The
glossary entry format and the ADR entry format — used for the `## Glossary` and
`## Decisions` sections inside `discovery-notes.md` — live in
`references/glossary-format.md` and `references/adr-format.md`. Do NOT create
separate `glossary.md` or `decisions/` files; everything is a section of the
single notes file.

## When to use, when to skip

**Use when** the user describes a new project idea (greenfield), OR a significant
piece of work on an existing system (brownfield) — a new module, a major feature,
an architectural change, a scaling or hardening effort on a large, mature
codebase — or wants to stress-test a plan before building. Existing and large
projects are a first-class case, not an afterthought: the skill shapes
substantial work, it does not push everything down to a minimal MVP. Also use
when an existing `context/discovery/discovery-notes.md` is incomplete and needs
resuming.

**Skip when** the change is a single bug, a quick refactor, a styling/cosmetic
tweak (colors, spacing, copy), a single-component frontend adjustment, or any
small, localized change that needs no discovery — just make the change. This
skill is for work whose shape is not yet clear and where misalignment would be
expensive. The scope-triage gate below enforces this so the skill bails out
instead of asking a wall of questions.

## Core principles (read before running)

1. **Facilitator, not generator.** Never write domain content the user did not
   say. If a section needs a value the user has not given, ask — do not invent.
   The only exception is mechanical formatting (FR numbering, section headers,
   frontmatter skeleton).
2. **One question at a time.** Walk down each branch of the decision tree,
   resolving dependencies one by one. Wait for the answer before the next
   question. Do not dump a wall of questions.
3. **Recommended answer first, plus an escape hatch.** For every decision,
   provide your recommended option, label it "(Recommended)", and place it
   first. Always include a "Not sure / let's come back to this" option so the
   user is never forced to guess.
4. **Explore the codebase instead of asking.** If a question can be answered by
   reading the code (brownfield) — current auth, existing modules, data shapes,
   naming — read it and confirm, rather than making the user recite it.
5. **Capture ubiquitous language inline.** When a term is resolved or a vague
   word is sharpened, append it to the `## Glossary` section of
   `discovery-notes.md` immediately. Do not batch.
6. **Challenge, don't rubber-stamp.** When the user is fuzzy ("everyone",
   "always", "lots of pain"), push back with one sharp question: "What would
   have to be true for this to be the wrong thing to build?" or "Who exactly did
   you watch hit this in the last month?"
7. **Stay stack-open.** Never ask for, recommend, or commit to a framework,
   database, language family, or hosting platform. Discovery captures
   product-level priorities only. If the user volunteers stack opinions, park
   them under a `## Forward: tech-stack` block in the notes — not in the
   product sections.
8. **Record decisions sparingly.** Offer an ADR only when a decision is
   hard to reverse, surprising without context, AND the result of a real
   trade-off. If any of the three is missing, skip it.
9. **Name anti-patterns specifically.** When you spot an empty-CRUD product or
   an oversized first slice, name the exact missing rule or the exact expensive
   element — never a generic "your idea has gaps".
10. **Bilingual operation: chat in the user's language, write artifacts in
    English.** Detect the language the user is writing in from their messages
    and conduct the entire discovery conversation in that language — questions,
    confirmations, challenges, recommendations, scorecards, AskUserQuestion
    options. The persisted artifacts under `context/discovery/`
    (`discovery-notes.md`, `glossary.md`, ADRs) are ALWAYS written in English,
    regardless of the chat language, so they remain portable across teams and
    tooling. When the user gives a term, phrase, or sentence in their own
    language, translate it to English on the way to disk and capture the
    original term in `glossary.md` under `Avoid` or as a localized alias when
    it's a real domain term. Never write non-English content into the artifacts
    silently; never translate the chat into English just because the artifacts
    are.

## Initial response

When this skill is invoked:

1. **If a freeform idea is given as an argument** (e.g. `rs-shape a recipe app
   that suggests meals from what's in your fridge`), record it verbatim as the
   **initial idea**. Do not paraphrase. Go to Step 0. Project name and client
   email are still asked in Step 0.7 — the inline idea does not skip identity
   capture.
2. **If a file path is given** (e.g. `rs-shape @notes/idea.md`), read it in full
   and use its contents as the initial idea. Go to Step 0. Project name and
   client email are still asked in Step 0.7.
3. **If nothing is given**, respond:

```
I'll help you shape an idea into a small set of shared-context documents —
whether you're starting from scratch (greenfield) or changing an existing
system (brownfield).

Please share:
1. The initial idea — what do you want to build or change, in your own words?
2. (Optional) Any rough notes, sketches, or links I should read first.

Tip: pass the idea inline — `rs-shape a recipe app that uses what's in your
fridge` — or for brownfield — `rs-shape add a recommendation engine to my
recipe app`.
```

Then wait.

## Process

### Step 0: Scope triage — run this FIRST, before anything else

Judge the size of the request before touching discovery. rs-shape is for shaping
a new project or a *meaningful* change (a new module, a significant feature, an
architectural change). It is the wrong tool for a small, localized tweak, and its
six phases would only generate noise.

If the request is small / cosmetic / localized — e.g. changing colors, spacing,
copy, or styling; tweaking a single component; a small frontend adjustment; a
quick bugfix — do NOT run discovery. Say so and route to the lighter path, then
STOP:

```
This looks like a small, localized change — shaping it through full discovery
would be overkill. For a change this size, skip straight to:
  • rs-new <change-id> → rs-plan <change-id>   — a tracked change with a quick plan
  • a direct edit                              — for a truly trivial tweak (e.g. one color value)
```

When the size is genuinely ambiguous, ask exactly ONE question first: "Is this a
small, localized change, or a new project / meaningful feature?" — and route
accordingly. Only continue to Step 0.5 when the request is a new project or a
meaningful change, or the user explicitly insists on full discovery anyway.

### Step 0.5: Set up the discovery folder and detect resume

Check whether a previous session exists:

```bash
test -f context/discovery/discovery-notes.md && echo "RESUME" || echo "FRESH"
```

If `FRESH`, create the folder when you first write to it (lazily — do not create
empty files) and go to Step 1.

If `RESUME`, read `discovery-notes.md` in full. Parse the `checkpoint:`
frontmatter block per `references/discovery-notes-template.md`. Summarize what
you found (project, current phase, phases completed, FRs drafted, quality-check
status) and ask:

AskUserQuestion:
- question: "Found a previous discovery session. How do you want to proceed?"
  header: "Resume?"
  options:
  - label: "Resume from the next phase (Recommended)"
    description: "Continue where the last session left off. Completed phases are summarized in one line each, not re-run."
  - label: "Start over"
    description: "Archive the existing notes to context/discovery/archive/ and begin a fresh session."
  - label: "Cancel"
    description: "Exit without changes."
  multiSelect: false

On "Resume": jump to the next unfinished phase. Do NOT re-run completed phases —
summarize each in one or two sentences so the user has context for what is
already settled. Before resuming, verify that `project` and `client` exist in
the frontmatter (Step 0.7). If either is missing (older session), ask for it
now and patch the frontmatter before continuing. On "Start over": move the
existing file to `context/discovery/archive/discovery-notes-<YYYY-MM-DD-HHMM>.md`,
then go to Step 0.7. On "Cancel": STOP.

### Step 0.7: Identity, repository selection, and project context

Before any discovery work, anchor the session with three identity fields:
client email, target repository, and project/change name. **All three are
required to proceed past Step 0.7.** The flow runs **one sub-step at a time** —
never bundle these into a wall of questions. There is NO standalone mode and
NO "skip" option — without an email there is no way to fetch the user's
repositories, and without a repository there is no project context to anchor
the discovery in.

#### Step 0.7a — Client email (REQUIRED)

Ask: "What's your email? I'll record it as the client / driver of this
discovery, and use it to pull your repositories from Rocksoft Flow." If the
harness provides a known user email in context, propose it as the recommended
answer via AskUserQuestion (first option, "(Recommended)") — never silently
auto-fill, always confirm.

Validate the email shape with a minimal check (contains `@` and a dot in the
domain part). If invalid or empty, re-ask — there is no skip option. Keep
re-asking until you get a syntactically valid email. If the user explicitly
refuses to provide one, STOP the session with a clear message: "An email is
required to look up your repositories in Rocksoft Flow. Restart `rs-shape`
when you're ready to provide one."

#### Step 0.7b — Fetch the user's repositories from Rocksoft Flow MCP (REQUIRED)

With the email in hand, call the Rocksoft Flow MCP server (`rocksoft-mcp`) to
list repositories assigned to this email. Look for a tool whose name suggests
listing repos (e.g. `list_repositories`, `get_repositories`,
`user_repositories`). Read its schema before calling; pass the email exactly as
the field name expects.

If the MCP tool is unreachable, returns no repos, or the tool itself is not
exposed, the session **cannot continue** — there is no fallback. Print the
problem in plain language and STOP, offering exactly one action: retry.

- **Tool not exposed:** "Rocksoft Flow MCP is connected but the
  `list_repositories` tool isn't exposed. I can't proceed without it — ask
  the Rocksoft Flow admin to wire it in n8n, then re-run `rs-shape`."
- **Connection / network error:** print the error verbatim, then "I couldn't
  reach Rocksoft Flow to list your repositories. We can't continue without
  this. Want to retry?" (offer: retry / abort).
- **Empty list:** "Rocksoft Flow doesn't have any repositories for `<email>`
  yet. Ask the Rocksoft admin to add at least one repository for this email,
  then re-run `rs-shape`." STOP.

If repos are returned, expect each entry to carry at minimum a display name
and a git URL (e.g. `name`, `git_url`). Other fields (description, default
branch, last activity) are nice-to-have for the picker UI.

#### Step 0.7c — Pick the repository (REQUIRED)

Show the list via AskUserQuestion. Options are the repo names in the order the
MCP returned them. There is **no "standalone" / "none" option** — the user
must pick one of their repositories to proceed.

- Each repo: label `<repo-name>`, description includes any extra fields the
  MCP returned (`<git_url>` — `<description?>`).

If the user explicitly refuses to pick any, STOP with: "A repository selection
is required to continue. Re-run `rs-shape` once you're ready to pick one of
your Rocksoft repositories."

On a repo selection, capture both `repository.name` and `repository.git_url`
for the frontmatter.

#### Step 0.7d — Fetch project context via Rocksoft MCP

The Claude runtime (Desktop / Web / Code) does NOT have `git` or `ssh`, and has
no credentials for private repositories. Cloning from the user's machine is not
an option. Instead, the repository's context files are fetched server-side by
Rocksoft Flow, which holds the GitHub token.

Call the Rocksoft Flow MCP tool **`get_repository_context`** with the selected
repo's `git_url` (exactly as returned by `list_repositories` — do NOT rewrite
it) and the user's email. The tool returns:

```json
{
  "repository": { "owner": "rocksoft", "repo": "onboarding",
                  "git_url": "git@github.com:rocksoft/onboarding.git" },
  "files": {
    "CLAUDE.md": "...",
    "context/foundation/tech-stack.md": "...",
    "context/prd/prd.md": "..."
  },
  "missing": []
}
```

`files` contains only files that exist. `missing` lists the paths that returned
404 — that is normal, not an error. If the tool itself fails (network, GitHub
credential misconfigured on the n8n side, repo not accessible to the token),
the response contains an `error` field; print it verbatim and ask the user how
to proceed (retry / continue without context / abort).

Summarize what you got in **2–4 sentences** so the user sees the context was
loaded: "Read `CLAUDE.md` (Python backend, FastAPI, postgres), `tech-stack.md`
(monorepo, pnpm), and `prd.md` (focused on B2B onboarding). I'll use this for
the discovery." If `files` is empty or all three are in `missing`, say so
plainly: "No `CLAUDE.md` / `context/foundation/tech-stack.md` / `context/prd/prd.md`
found in this repo — we'll discover from scratch."

This context informs your grilling — it does NOT replace it. You still ask
about intent; you just don't ask the user to recite facts the files already
state. Quote concrete details from the files when relevant ("Your tech-stack
already commits to FastAPI — should this change keep that?").

If the `get_repository_context` tool is not exposed by the connected MCP
server, tell the user plainly: "Rocksoft Flow MCP is connected but the
`get_repository_context` tool isn't exposed in this session — I can't read the
repo's context files. We'll proceed without them." Continue to Step 0.7e
without crashing.

#### Step 0.7e — Project / change name

Now ask: greenfield → "What's the working name of the project you want to
shape?"; brownfield → "What's a short name for this change or initiative?" If
the repo context strongly suggests a name (e.g. the repo is `onboarding` and
the prd mentions "B2B signup overhaul"), propose it as the recommended option.

#### Write identity to frontmatter

After all relevant sub-steps complete, write the discovery-notes frontmatter
immediately (creating the file lazily on this first write):

```yaml
---
project: <user's answer>
client: <user's email>
repository:
  name: <repo name from Step 0.7c>
  git_url: <git url from Step 0.7c>
created: <today>
updated: <today>
checkpoint:
  current_phase: 1
  phases_completed: []
  frs-drafted: 0
  quality_check_status: pending
---
```

All three identity fields (`project`, `client`, `repository.name` /
`repository.git_url`) are required — none can be `(none)`, `(not provided)`,
or empty. If any is missing at this point you should NOT be here; revisit
Step 0.7a–c.

The discovery file is always written under `context/discovery/` in the **current
working directory**. The Claude runtime does not have a local copy of the
repository (no `git clone` is ever performed), so binding to a repo is purely
metadata that travels with the spec when Step 10 hands it back to Rocksoft
Flow via MCP.

Confirm back in one line ("Recorded as `<project>` for `<repository.name>`,
driven by `<client>` — let's continue.") and proceed to Step 1.

### Step 1: Detect context type (greenfield vs brownfield)

Detection happens once; the result (`context_type`) is written to the
discovery-notes frontmatter and drives phase behavior for the rest of the
session. On resume, if `context_type` is already set, skip detection — it is
locked from the previous session.

Evaluate the working directory in three signal tiers. A single manifest file is
not enough — an empty `npm init -y` directory should not trigger brownfield.

```bash
# Tier 1 (strong): version control with history
git log --oneline -1 2>/dev/null && echo "T1:git-history"

# Tier 2 (medium): lockfiles prove real dependency resolution happened
ls package-lock.json yarn.lock pnpm-lock.yaml Cargo.lock poetry.lock go.sum \
   Gemfile.lock composer.lock 2>/dev/null | while read f; do echo "T2:$f"; done

# Tier 3 (weak): manifest files alone — could be a fresh init
ls package.json Cargo.toml pyproject.toml go.mod Gemfile composer.json \
   2>/dev/null | while read f; do echo "T3:$f"; done

# Confirming signals (do not trigger on their own): source dirs, CI, configs
ls -d src/ app/ lib/ .github/ Dockerfile tsconfig.json 2>/dev/null \
   | while read f; do echo "B:$f"; done
```

```powershell
# PowerShell (Windows) — use this block instead of the bash block on Windows.
# Do NOT let a bash->PowerShell translator rewrite the bash loop: the pattern
# `while read f; do echo "B:$f"` produces the literal string "B:$f", which
# Windows reads as a drive `B:` and prompts for a non-existent drive.
if (git log --oneline -1 2>$null) { "T1:git-history" }
@('package-lock.json','yarn.lock','pnpm-lock.yaml','Cargo.lock','poetry.lock',
  'go.sum','Gemfile.lock','composer.lock') |
  Where-Object { Test-Path -LiteralPath $_ } | ForEach-Object { "T2:$_" }
@('package.json','Cargo.toml','pyproject.toml','go.mod','Gemfile',
  'composer.json') |
  Where-Object { Test-Path -LiteralPath $_ } | ForEach-Object { "T3:$_" }
@('src','app','lib','.github','Dockerfile','tsconfig.json') |
  Where-Object { Test-Path -LiteralPath $_ } | ForEach-Object { "B:$_" }
```

Decision logic:
- **Any Tier 1 or Tier 2 hit** → propose `brownfield`.
- **Tier 3 only** (manifest, no lockfile, no git) → propose brownfield but flag
  the ambiguity: "I found a manifest but no lockfile or git history — this might
  be a freshly initialized project rather than a real brownfield."
- **No signals** → propose `greenfield`.

Print what you detected in plain language, then confirm:

AskUserQuestion:
- question: "Detected context: [greenfield|brownfield]. Is that right?"
  header: "Context"
  options:
  - label: "[Greenfield|Brownfield] — correct (Recommended)"
    description: "[one-line description of the auto-detected mode]"
  - label: "[Other mode] — override"
    description: "Switch to the other mode instead."
  multiSelect: false

Write the confirmed `context_type` to the discovery-notes frontmatter
immediately.

### Step 1b: Explore the codebase first (brownfield only)

Before interviewing, build your own map of what exists so you grill from
knowledge, not ignorance. Skip this entirely for greenfield.

- Read any existing `CONTEXT.md`, `README.md`, `docs/adr/`, or a prior
  `context/discovery/discovery-notes.md` (including its `## Glossary` and
  `## Decisions` sections) for prior domain language and decisions.
- Map the relevant modules, their public interfaces, and who calls them. Use the
  project's existing vocabulary.
- Note the current auth model, data shapes, and integration points in the area
  the change touches.

Summarize the map back to the user in a short paragraph and ask them to correct
anything you got wrong. From here on, **prefer reading the code over asking the
user to recite it** — only ask about intent, not facts you can verify.

### The discovery loop (applies to every phase below)

Every phase runs the same loop. Internalize it; the per-phase sections say *what*
to ask, not *how*.

1. **Open the phase** with one sentence on what it produces, and one open
   question to draw out the user's first attempt.
2. **Grill one question at a time.** When the first answer is fuzzy or hides a
   fork, ask the next sharpest question. If the answer lives in the code, read
   the code instead of asking.
3. **Surface gray areas as a decision** using AskUserQuestion when several real
   options exist. Each option is a real position with a trade-off, never a
   placeholder. Recommended first; "Not sure" last.
4. **Capture glossary terms** the moment a name is sharpened — append to the
   `## Glossary` section of `discovery-notes.md` inline.
5. **Lock the decision back** to the user in a one-line confirmation before
   writing it to disk.
6. **Write the phase sections** to `discovery-notes.md` and advance
   `checkpoint.current_phase` / `checkpoint.phases_completed`.

### Step 2 — Phase 1: Problem & persona

Produces `## Vision & Problem` and `## User & Persona`. Brownfield also produces
`## Current System`.

**Greenfield.** Open with: "Let's start with the pain. In a sentence or two —
who feels it, at what moment, and what does it cost them today?" Reflect back the
four parts separately (pain / person / moment / cost today). If any is vague
("everyone", "always"), challenge it: "Who specifically did you watch hit this
last month?" Then surface gray areas: pain category, the insight the user has
that the status quo lacks ("if it's obvious, why hasn't it been built?"), and
the precise scope of the primary persona (name a role, not "users").

**Brownfield.** Open with: "Let's start with the current system. In a few
sentences — what exists today, who uses it, and what pain or gap is driving this
change?" Reflect back: current system, tech stack mentioned, users (named
roles), pain/gap, and **what must be preserved** (what cannot break). If the
user can't pin down "must be preserved", challenge: "If this change broke
something tomorrow, what would alert you first?" Write `## Current System`
first (drawing on your Step 1b map), then `## Vision & Problem` framed as a
delta (what changes and why), then `## User & Persona`.

### Step 3 — Phase 2: Access & roles

Produces `## Access Control`. The persona was captured in Phase 1; here we ask
how they reach the product.

**Greenfield.** "How does this person get into the app — login, local profile,
access key, or no auth at all?" Offer the common forms with a recommendation,
then one follow-up on role separation (flat user model vs. roles like
admin/member/guest). Socratic: "What's the smallest access model that still
makes the first release useful?"

**Brownfield.** Read the current auth from the code if you can, then confirm:
"Here's the auth model I see — is that right?" Then ask only what *changes*:
does the auth model change in this work? Are new roles added or existing role
boundaries moving? If nothing changes, write the current model with the note
"No change planned — existing model preserved."

### Step 4 — Phase 3: First increment & success criteria

Produces `## Success Criteria` (Primary / Secondary / Guardrails). The aim is the
first increment that ships **end-to-end and delivers real value** — which may be
substantial. This is incremental-delivery discipline, NOT a push toward a minimal
MVP; an ambitious first increment is entirely valid for a serious or large
project.

**Greenfield.** "Sketch the first end-to-end flow that delivers real value and
proves the approach works. Walk me through it." Reflect it back as a numbered
sequence. Then apply **scope awareness** — judged by size and complexity, not
time: if the flow needs many integrations / external services / custom
infrastructure before anything works end-to-end, name the cost and the expensive
element so the user can choose deliberately:

```
This first increment is sizeable. For an ambitious or large product that can be
the right call — but front-loading a lot of work before anything runs end-to-end
risks stalling. If you'd rather de-risk first, common moves:

  - Defer [the identified expensive element] to a later increment.
  - Replace [the identified integration] with a manual/hardcoded version for now.
  - Narrow the first increment to one user/role, then expand.
```

Offer the choice (de-risk with a smaller first increment / keep the full scope,
consciously / re-sketch). The goal is a deliberate, informed choice — keeping a
large first increment is valid; the skill does not steer toward a minimal MVP.

**Brownfield.** "Describe the first end-to-end increment of this change that
delivers value and proves it works in the real system — this can be a substantial
feature, not a token slice. What does the user do differently once it ships?"
Reflect as a delta sequence. Then ask the **blast radius** question ("which
existing features, integrations, or data flows could break?") and apply the same
size/complexity scope awareness. The brownfield trap is starting a big change and
leaving it half-done — partially modified code is worse than the original — so
the aim is an increment that ships end-to-end, whatever its size.

**Both.** Capture the working flow as the `### Primary` success criterion, then
ask for one `### Secondary` (a nice-to-have) and one or two `### Guardrails`
(things that must not break — privacy, minimum performance, UX). For brownfield,
guardrails must explicitly include the existing behavior that must be preserved.

Finally, ask for a **rough time estimate** for this slice and record it as-is —
"How long do you think this slice will take?" Write the user's answer verbatim to
the `estimated_effort` frontmatter field (free text — e.g. "~2 weeks", "a few
weekends", "unknown"). This is a plain record, not a gate: do not challenge it,
push to cut scope because of it, or ask the user to commit to it.

### Step 5 — Phase 4: Functional requirements & grilling

Produces `## Functional Requirements` and `## User Stories`.

**Greenfield.** "From the first-increment flow, what must the actor be *able* to do? List
the capabilities — I'll format them as FRs." Capture each as:

```
- FR-NNN: [Actor] can [capability]. Priority: must-have | nice-to-have
```

`NNN` is a zero-padded three-digit number starting at `001`. Default
`must-have` for everything in the first-increment flow; ask explicitly if anything is
nice-to-have.

**Brownfield.** Add a change tag:

```
- FR-NNN: [Actor] can [capability]. Priority: must-have | nice-to-have. Change: new | modified | preserved
```

`preserved` FRs are defensive — they explicitly flag existing behavior that must
keep working. Prompt the user: "Which existing capabilities must explicitly
survive this change?" Flagging preservation prevents accidental breakage.

**Both.** Group thematically with `###` subheadings if there are more than ~6
FRs. Then ask the user to translate at least the main flow into a `### US-01`
user story with Given/When/Then. Update `checkpoint.frs-drafted`.

**Then run one Socratic challenge round** — exactly one challenge per FR, in
document order. For each FR, ask what would have to be true for delivering it to
*hurt* the product, or the strongest counterargument to including it in this scope.
Offer 2–4 plausible, domain-specific counterarguments via AskUserQuestion, with
"No counterargument; keep as written" as the LAST option (so the user must
consider the challenge before dismissing it). Capture each answer as a
`> Challenge:` quote block under its FR. If a challenge changes an FR (split,
downgrade, remove), update the line in place.

### Step 6 — Phase 5: Business logic & constraints

Produces `## Business Logic` and `## Non-Functional Requirements`. Brownfield
also produces `## Constraints & Preserved Behavior`. Entities and fields are
deliberately NOT captured as a separate section — they emerge from the FRs and
stories and get pinned down later during implementation planning.

**Greenfield.** "State the one business rule — the domain decision your app
makes — that sets it apart from a generic CRUD list, in a single sentence."
Capture it as the first line of `## Business Logic`, then ≤3 paragraphs on the
user-visible inputs it consumes, its output, and how the user meets it in the
flow. Do NOT name components or actors that perform the computation — those are
later architectural choices.

**Empty-CRUD anti-pattern detection.** If the "business logic" reduces to "users
can add, view, update, and delete records" with no rule the app itself applies,
name it:

```
What you've described is a CRUD list — a known greenfield anti-pattern. CRUD
with no domain decision means the app delivers nothing a spreadsheet couldn't.
A real domain rule answers "what does the app decide for the user?". Common
shapes: recommendation, prioritization, classification, validation, scoring,
workflow, calculation. Which rule does YOUR app apply?
```

Offer those rule shapes as options. If the user genuinely is building plain
CRUD, record it and add an entry to `## Open Questions`.

**Brownfield.** "What's the existing domain rule your system applies for the
user? And does this change add a new rule, modify an existing one, or is it
infrastructure only (no rule change)?" Classify and capture accordingly. For
infrastructure-only work, skip the empty-CRUD check. Then capture `## Constraints
& Preserved Behavior`: existing integrations/APIs/data contracts the change must
respect, data migrations, and backward-compatibility guarantees.

**Both.** Ask one round of non-functional requirements: externally observable
properties the product must hold at its boundary — response time as the user
perceives it, privacy commitments, availability, device/browser support,
retention windows. Reflect mechanical phrasings ("rate-limit per IP", "Postgres
query < 50ms") back into externally observable form before capturing. Capture as
`## Non-Functional Requirements`.

### Step 7 — Phase 6: Framing & non-goals

Produces `## Non-Goals` and the product-level frontmatter fields
(`product_type`, `target_scale`).

Ask the framing questions ONE at a time, in plain language — do not print field
names like `product_type` in the question text:

1. "What kind of thing are you building?" → map to `product_type` (web-app /
   api / cli / mobile / desktop / library / data-pipeline / other).
2. "Roughly how many people will use it once it's working?" → map to
   `target_scale.users` (small / medium / large / enterprise). Follow with:
   "How would your domain rule change at 100x the scale?"

For brownfield, turn these into "does this change?" yes/no gates plus constraint
capture (deployment windows, existing CI/CD, backward compatibility).

Then run **one** multi-select Non-Goals round, drawn from the user's domain (not
generic): capabilities this scope won't build, quality dimensions it won't pursue,
and for brownfield, existing-system changes explicitly out of scope. Append the
selected items to `## Non-Goals` with a one-line rationale each. Park any
technology avoidances under `## Forward: tech-stack`, not in Non-Goals.

### Step 8: Soft quality gate

Run a quality bar over everything captured. This is a **soft gate**: it warns
loudly but lets the user override.

Read the current `discovery-notes.md` and check each item as present or
missing/weak:

1. **Access control** — `## Access Control` exists with a non-trivial value.
2. **Business logic** — `## Business Logic` starts with a single declarative
   sentence (for brownfield infra-only work, "No domain logic change" is valid).
3. **Non-Goals** — `## Non-Goals` has at least one entry.
4. **Preserved behavior** *(brownfield only)* — `## Constraints & Preserved
   Behavior` names what cannot break.
5. **Glossary** — the `## Glossary` section of `discovery-notes.md` has at
   least the core domain terms that came up.

Print a scorecard. For each missing/weak item, name it with a one-line
consequence ("Business logic: not captured as a one-line rule — your build will
have no domain decision to anchor on"). Never write a generic "your notes have
gaps". Then offer: fix the gaps now / accept and finish / resume a specific
phase. On accept, set `checkpoint.quality_check_status` to `warned` (if gaps
remain) or `accepted`, and append a `## Quality cross-check` section listing each
gap.

### Step 9: Handoff & decisions

Final write of `discovery-notes.md`:

- Confirm `checkpoint.quality_check_status` is `warned` or `accepted`.
- Update `updated:` to today's date.
- Re-verify against `references/discovery-notes-template.md`. Forward blocks
  (`## Forward: ...`) stay separate from the product sections.

Then review the **decisions** captured during the session. For any decision that
is hard to reverse, surprising without context, AND a real trade-off, offer to
append it as an entry under the `## Decisions` section of `discovery-notes.md`
using `references/adr-format.md` (each entry headed `### ADR-NNNN: <slug>`).
Skip any that fail the three-part test — do not manufacture ADRs. Do NOT create
separate ADR files under `decisions/`; the section in the notes is the single
home.

Print a short completion summary (project, client, context type, phases
captured, FRs drafted, quality status, and the path to the single artifact
`context/discovery/discovery-notes.md`). Then continue to Step 10.

### Step 10: Open a Pull Request with the specification

Once `discovery-notes.md` is finalized, ask the user whether to open a PR with
it in the repository chosen in Step 0.7c. The Claude runtime has no `git` and
no credentials to the repo, so the PR is created **server-side** via the
Rocksoft Flow MCP tool `create_spec_pr`. The spec is **never committed
directly to the default branch** — it always lands on a fresh branch and goes
through PR review. The question is **always asked**, never auto-executed.

Use AskUserQuestion (translate question and options into the user's chat
language, per guardrail #11):

```
question: "Discovery is complete. Do you want me to open a Pull Request with
           the specification in <repository.name>?"
header:   "Open PR?"
options:
  - label: "Yes, open the PR (Recommended)"
    description: "Create a new branch in <repository.name>, add discovery-notes.md
                 to it, and open a Pull Request against the default branch.
                 Nothing is committed to the default branch directly."
  - label: "Not yet — keep it local"
    description: "Leave the file in context/discovery/discovery-notes.md.
                 You can re-run rs-shape later to open the PR."
multiSelect: false
```

#### Executing "Yes, open the PR"

1. Confirm the MCP tool is available. Look for `create_spec_pr` (or an
   equivalent name like `open_spec_pr`, `submit_spec_as_pr`). If none is
   exposed, say so plainly and STOP — do NOT fall back to a tool that commits
   directly to the default branch (e.g. an older `upload_spec` that hardcodes
   a central repo). The user explicitly chose PR workflow.
2. Read `context/discovery/discovery-notes.md` in full (from the current
   working directory).
3. Call `create_spec_pr` with:
   - `specification`: the full markdown body (including frontmatter)
   - `project`: frontmatter `project`
   - `client`: frontmatter `client`
   - `git_url`: frontmatter `repository.git_url` (this is what tells the
     server WHICH repo to open the PR in — never pass a hardcoded URL)
   - `path` (optional): only if the user explicitly asked for a non-default
     location; otherwise **omit it entirely** (do not pass `path` at all — never
     pass an interpolated value that may be empty/undefined) and let the tool
     default to `context/discovery/discovery-notes.md`
4. On success, the tool returns `{ pr_url, pr_number, branch, base_branch,
   file_path, repository }`. Print a clear confirmation:
   ```
   Opened PR #<pr_number> in <repository.owner>/<repository.repo>:
     branch  : <branch>   (against <base_branch>)
     file    : <file_path>
     link    : <pr_url>
   ```
5. On error, print the error verbatim and offer retry or leave local. Common
   failures and what they mean:
   - `Resource not accessible by integration` / `Bad credentials` → the n8n
     GitHub credential lacks write access to this repo. Ask the user to
     contact the Rocksoft admin.
   - `Reference already exists` → a branch with the generated name already
     exists; retry will produce a new timestamp.
   - `Unable to parse git_url: ...` → the `git_url` we passed didn't match
     the expected pattern. Re-confirm with the user what `list_repositories`
     returned.

#### Executing "Not yet — keep it local"

Print one line confirming the local path
(`context/discovery/discovery-notes.md`) and STOP.

Step 10 is the final step. Do not auto-proceed beyond it.

## Critical guardrails

1. **Facilitator, not generator.** Never write domain content the user didn't
   say. Ask for missing values; only mechanical formatting is auto-filled.
2. **The template is the contract.** The shape of `discovery-notes.md` is
   dictated by `references/discovery-notes-template.md`. Re-check it at every
   checkpoint write; if it drifts, fix the template first.
3. **Stack-openness is binding.** Never ask for, recommend, or commit to a
   framework, database, language family, or platform. Volunteered stack opinions
   go under `## Forward: tech-stack`.
4. **Anti-patterns are named, not generic.** Empty-CRUD detection names the
   missing rule shape; oversized-first-increment detection names the expensive element and
   offers concrete cuts.
5. **Soft gate, not hard gate.** The final check warns but lets the user
   override every gap. Overrides are recorded as `quality_check_status: warned`.
6. **Mode-aware behavior.** Greenfield asks "what are you building from
   scratch?"; brownfield asks "what exists, what changes, what must be
   preserved?" and reads the code before asking.
7. **Glossary is a glossary.** The `## Glossary` section of `discovery-notes.md`
   holds project-specific domain terms only — no implementation details, no
   general programming concepts. Capture inline, stay opinionated (one canonical
   term, the rest under `Avoid`).
8. **ADRs are rare.** Only hard-to-reverse, surprising, real-trade-off decisions
   become ADR entries under `## Decisions`. When in doubt, leave it out. No
   separate per-decision files.
9. **Resume preserves prior work.** On resume, completed phases are summarized
   in one line each, never re-run.
10. **Project identity is captured upfront and is mandatory.** Step 0.7
    captures client email (REQUIRED), repository (REQUIRED — fetched from
    Rocksoft Flow MCP for that email and chosen by the user), and project /
    change name (REQUIRED) before any discovery question. There is no
    standalone or skip mode — without all three the session does not advance
    to Step 1. All three are written to the frontmatter on the very first
    write and never overwritten silently. On resume, missing identity fields
    are backfilled before continuing.
11. **Artifacts are English, chat is the user's language.** Detect the language
    from the user's messages and run the conversation in it. Everything written
    under `context/discovery/` (notes, glossary section, ADR entries, frontmatter
    values like the `project` slug) is always English. Translate user-supplied
    content on the way to disk; preserve the original term in the `## Glossary`
    section if it's a real domain word.
12. **One file only.** All discovery output lives in
    `context/discovery/discovery-notes.md`. The skill must not create
    `glossary.md`, a `decisions/` folder, or any per-decision file. Glossary
    entries and ADRs are sections of the notes.
13. **Persisting to Rocksoft is always asked, and always goes through a PR.**
    After the soft gate and handoff, Step 10 explicitly asks the user whether
    to open a Pull Request via the Rocksoft Flow MCP tool `create_spec_pr`.
    The spec is NEVER committed directly to the default branch — it always
    lands on a fresh branch and goes through PR review. No silent uploads, no
    opt-out by default, no fallback to a tool that commits to main.
14. **No local git, no local clone — repo access is always server-side.** The
    Claude runtime does not have `git`, `ssh`, or credentials to the user's
    repos. Step 0.7d fetches context files via the Rocksoft Flow MCP tool
    `get_repository_context`, never by cloning. Step 10 hands the finished
    spec back via `create_spec_pr`, which opens a Pull Request in the
    user-selected repository — the `git_url` of the target repo travels with
    every call, so there is no possibility of writing to a hardcoded fallback
    repo. The discovery file always lives under
    `./context/discovery/discovery-notes.md` in the current working directory.
    A repository selection is mandatory (see guardrail #10) — there is no
    path where the spec exists without a repo binding.

## Notes

- This is a **discovery** skill. The output is one shared-context file —
  `context/discovery/discovery-notes.md`, with `## Glossary` and `## Decisions`
  as sections inside it — not a finished spec or a build plan. No companion
  files, no `decisions/` folder.
- `references/discovery-notes-template.md` is the single source of truth for the
  notes structure. Any section name or frontmatter key this skill references
  must exist there.
- If the user pushes to skip a phase ("just write the notes"), explain the
  consequence (missing phases leave empty sections), then let them choose. The
  decision is theirs.
