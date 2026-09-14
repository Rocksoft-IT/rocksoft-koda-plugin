# Decision (ADR) format

Decisions live as short entries under the issue's `## Decisions` section. There
are no separate files. Most issues have none; that is the expected outcome.

## Entry format

```md
### ADR-0001: events-not-http-between-ordering-and-billing

Ordering and Billing communicate through domain events rather than synchronous
calls, so Billing can be down without blocking checkout. Accepted the extra
eventual-consistency handling in return.
```

One to three sentences: the context, what was decided, why. Optional lines only
when they add real value: **Considered options**, **Consequences**.

## The three-part test

Offer an entry only when **all three** hold:

1. **Hard to reverse** — changing course later costs real time or money.
2. **Surprising without context** — a future reader would ask "why on earth?"
3. **A real trade-off** — genuine alternatives existed and one was chosen for
   specific reasons.

Easy to reverse: skip, you will just reverse it. Not surprising: skip, nobody
will wonder. No alternative: skip, there is nothing to record beyond "we did
the obvious thing".

## What qualifies

- Boundary and scope decisions ("Customer data is owned by the Customer
  context; others reference it by ID only").
- Integration patterns (events vs synchronous calls).
- Deliberate deviations from the obvious path.
- Constraints not visible in the code ("cannot use provider X for compliance
  reasons", "must answer under 200 ms because of a partner contract").

## What does not qualify at this stage

Framework, database, language, or hosting choices. rs-feature stays stack-open;
if the client volunteers such opinions, they go under **Technical notes from
the client**, not under Decisions.
