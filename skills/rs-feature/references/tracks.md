# Track playbooks

Each track lists what it must settle, the questions in the order that usually
works, and when it is done. Questions are prompts for you, not scripts — phrase
them in the client's language and skip any the repository context or the
initial request already answers (confirm instead).

Common rules for every track live in SKILL.md ("Run the track"). Rough question
budgets are guidance, not limits; when you exceed one, say so.

---

## quick

**Settles:** current behavior, desired behavior, where it appears, what must not
change.

**Budget:** 2–4 questions.

1. "Where exactly does this show up today, and what happens now?" (screen,
   flow, message, report — get the concrete location and the current behavior.)
2. "What should happen instead?" (Reflect back as one sentence of desired
   behavior. If it hides two changes, split and confirm both.)
3. "Is there anything around it that must stay exactly as it is?"
4. Only if a bug: "How do you reproduce it, and how often does it happen?"

**Done when** you can write one or two acceptance criteria in Given/When/Then
that an engineer could verify without asking anything.

**Issue sections:** Summary · Scope (in / out) · Acceptance criteria ·
Constraints & preserved behavior (if any) · Open questions (if any) · Metadata.

**Upgrade signal:** if the answers reveal new roles, new data, or several
interacting cases, say "this is bigger than a quick change" and propose the
feature track.

---

## feature

**Settles:** problem and persona, the first end-to-end increment, requirements
with acceptance criteria, constraints and preserved behavior, non-goals.

**Budget:** roughly 6–12 questions plus one challenge round.

### Round 1 — Problem & persona

- "Who feels this today, at what moment, and what does it cost them?" Reflect
  back the four parts separately (pain / person / moment / cost). Challenge
  vague answers: "Who specifically hit this in the last month?"
- If the repo context describes the product, frame the request as a delta:
  "So today X happens; you want Y. Right?"
- Ask what must be preserved: "If this broke something tomorrow, what would
  alert you first?"

### Round 2 — First end-to-end increment

- "Walk me through the first version that delivers real value end to end.
  What does the user do differently once it ships?" Reflect it back as a
  numbered sequence.
- Scope awareness: if the sequence needs several integrations or a lot of new
  infrastructure before anything works, name the expensive element and offer
  the choice: defer it / replace it with a manual or hardcoded version for now /
  narrow to one role first / keep the full scope consciously. Any answer is
  valid; the point is a deliberate choice.
- Blast radius: "Which existing features, integrations, or data could this
  affect?"

### Round 3 — Requirements & acceptance criteria

- "From that flow, what must the user be able to do?" Capture each as
  `FR-NNN: [Actor] can [capability]. Priority: must-have | nice-to-have.
  Change: new | modified | preserved`. Default must-have for everything in the
  first increment; ask explicitly for nice-to-haves.
- Ask which existing capabilities must explicitly survive (they become
  `preserved` FRs).
- Turn the main flow into at least one acceptance criterion in
  Given/When/Then. Add one for the most likely error or edge case.

### Challenge round (once)

For each must-have FR, ask one sharp counter-question: "What would have to be
true for delivering this to hurt the product?" Offer two to four plausible,
domain-specific counterarguments with "No counterargument, keep it" **last**.
If a challenge changes an FR (split, downgrade, drop), apply it. Record notable
outcomes as a `> Challenge:` line under the FR.

### Round 4 — Constraints, non-functionals, non-goals

- Constraints & preserved behavior: existing integrations, APIs, data contracts,
  migrations, backward compatibility the change must respect.
- One round of non-functional requirements, phrased as the user experiences
  them (perceived speed, privacy commitments, availability, devices/browsers,
  retention). Reflect mechanical phrasings back into observable form.
- One multi-select non-goals round, drawn from the client's domain: things this
  scope will not build, quality dimensions it will not pursue, existing-system
  changes explicitly out of scope. One-line rationale each.

**Done when** every must-have FR has an acceptance criterion, preserved
behavior is named, and at least one non-goal exists.

**Issue sections:** everything in the template except Glossary and Decisions,
unless real domain terms or a hard-to-reverse decision emerged.

---

## initiative

**Settles:** everything in the feature track plus the business rule, access
model, framing (what kind of thing, what scale), glossary, and decisions.

**Budget:** a full interview; expect 15–25 questions. Announce phases as you
enter them so the client knows where they are.

### Phase 1 — Problem & persona

As in the feature track, Round 1. For a new product also draw out the insight:
"If the problem is this obvious, why hasn't it been solved already — what do
you know that the status quo doesn't?" Name a role for the primary persona, not
"users".

### Phase 2 — Access & roles

- New product: "How does this person get in — login, local profile, access key,
  no auth at all?" Offer the common forms with a recommendation, then one
  follow-up on role separation. "What's the smallest access model that still
  makes the first release useful?"
- Existing product: state the auth model you see in the repo context and ask
  only what changes. If nothing changes, record "No change planned — existing
  model preserved."

### Phase 3 — First increment & success criteria

As in the feature track, Round 2. Then capture success criteria: the working
flow as **Primary**, one **Secondary** (nice-to-have outcome), and one or two
**Guardrails** (must not break: privacy, performance floor, existing behavior).

### Phase 4 — Functional requirements & challenge

As in the feature track, Round 3 plus the challenge round. Group FRs under
sub-headings when there are more than about six.

### Phase 5 — Business logic & constraints

- "State the one rule this product applies for the user — the decision it makes
  that a spreadsheet couldn't — in a single sentence." Capture it as the first
  line of the Business rule section, then up to three short paragraphs on its
  inputs, output, and where the user meets it. No components, no actors that
  perform the computation.
- **Empty-CRUD check.** If the "logic" reduces to add/view/update/delete with
  no rule the product applies, say so plainly and offer the common rule shapes:
  recommendation, prioritization, classification, validation, scoring,
  workflow, calculation. If the client genuinely wants plain CRUD, record it
  and add an open question.
- Existing product: "Does this change add a rule, modify one, or is it
  infrastructure only?" For infrastructure-only work skip the CRUD check.
- Constraints & preserved behavior and one round of non-functional requirements,
  as in the feature track.

### Phase 6 — Framing & non-goals

One at a time, in plain words:

1. "What kind of thing is this?" (web app / API / CLI / mobile / desktop /
   library / data pipeline / other)
2. "Roughly how many people will use it once it works?" then "How would the
   main rule change at a hundred times that scale?"
3. The non-goals round as in the feature track.

For an existing product turn 1 and 2 into "does this change?" gates plus any
delivery constraints (deployment windows, existing CI/CD, compatibility).

### Glossary & decisions

- Keep the glossary as you go (`glossary-format.md`): one canonical term,
  synonyms under Avoid, project-specific terms only.
- Before drafting, review the decisions made in the conversation against the
  three-part test in `adr-format.md` (hard to reverse, surprising without
  context, a real trade-off). Record only the ones that pass, as short
  entries under Decisions. Stack choices do not qualify at this stage — park
  them under Technical notes from the client.

### Soft quality check

Before printing the draft, check: access model captured; business rule is one
declarative sentence (or "no domain logic change"); at least one non-goal;
preserved behavior named for an existing product; glossary has the core terms
that came up. Name each gap with its consequence in one line. The client may
accept gaps; list accepted gaps under Open questions.

**Issue sections:** the full template.
