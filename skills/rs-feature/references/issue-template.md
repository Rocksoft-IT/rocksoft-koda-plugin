# Issue template

The issue is the only artifact rs-feature produces, and it is consumed by
people and by automation on the Rocksoft side. Keep the section names and order
exactly as below so downstream tooling can rely on them. Omit a section that
does not apply to the track — never leave an empty header. Always English.

Minimum for every track: Summary · Scope · Acceptance criteria · Metadata.

## Title

Sentence case, ≤ 80 characters, names the outcome for the user, not the work.

- Good: `Customers can export invoices as PDF`
- Good: `Order status e-mails go out in the customer's language`
- Bad: `Invoice export feature`, `Fix e-mails`

## Body

```markdown
<!-- rs-feature · track: <quick|feature|initiative> · client: <email> · repository: <name> -->

## Summary

One paragraph, in the client's words distilled: what they want and why now.
No solutioning.

## Problem & context

- **Who** feels the pain, **when**, and **what it costs** them today.
- **Current system** (existing products only): the relevant part of what
  exists, drawn from the repository context and confirmed by the client.
- **Insight** (new products only): what the client knows that the status quo
  doesn't.

## Scope

### In scope

- The first end-to-end increment, as a numbered sequence of what the user does.

### Out of scope (non-goals)

- <thing this scope will not build> — <one-line rationale>

## Access & roles

<!-- initiative track, or whenever the access model changes -->
Who can do what. For an existing product: "No change planned — existing model
preserved." when that is the case.

## Success criteria

<!-- feature and initiative tracks -->
- **Primary:** the working flow that proves the change delivers value.
- **Secondary:** one nice-to-have outcome.
- **Guardrails:** what must not break (privacy, perceived performance, existing
  behavior).

## Requirements

- FR-001: [Actor] can [capability]. Priority: must-have. Change: new
  > Challenge: <notable outcome of the challenge round, if any>
- FR-002: [Actor] can [capability]. Priority: nice-to-have. Change: modified
- FR-003: [Actor] can still [existing capability]. Priority: must-have. Change: preserved

## Acceptance criteria

### AC-01: <short name>

- **Given** <context>
- **When** <action>
- **Then** <observable result>

### AC-02: <most likely error or edge case>

- **Given** …
- **When** …
- **Then** …

## Business rule

<!-- initiative track; feature track when a rule is added or changed -->
One declarative sentence: the decision the product makes for the user. Then at
most three short paragraphs: inputs the user provides, the output, where the
user meets it in the flow. No components, no implementation.

## Constraints & preserved behavior

- Existing integrations, APIs, data contracts, migrations, and compatibility
  guarantees this change must respect.
- Behavior that must keep working exactly as today.

## Non-functional requirements

- Externally observable properties only: perceived response time, privacy
  commitments, availability, supported devices/browsers, retention.

## Open questions

- Anything unresolved, plus gaps the client consciously accepted in the quality
  check, each with its consequence.

## Glossary

<!-- initiative track, or whenever real domain terms were sharpened -->
**Term**: one- or two-sentence definition. _Avoid_: synonym, synonym

## Decisions

<!-- rare: only decisions that are hard to reverse, surprising without context, and a real trade-off -->
### ADR-0001: <slug>
One to three sentences: context, decision, why.

## Technical notes from the client

<!-- only if the client volunteered stack or implementation opinions; kept out of the product sections -->
- <opinion, verbatim or close to it>

## Metadata

- **Client:** <email>
- **Repository:** <name> (<git_url>)
- **Track:** quick | feature | initiative
- **Product type:** <web app / API / … or "unchanged">   <!-- initiative -->
- **Target scale:** <small / medium / large / enterprise or "unchanged">   <!-- initiative -->
- **Client's size estimate:** <their words, if given>
- **Created with:** rocksoft-koda rs-feature 0.2.0
```
