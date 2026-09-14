# Glossary format

The Glossary section of the issue holds the **ubiquitous language** of the
change: the canonical terms humans and agents should use from now on in code,
conversation, and documentation. Capture terms the moment a fuzzy word is
sharpened during the conversation; do not batch at the end.

## Entry format

```md
**Order**:
A confirmed request for goods placed by a Customer.
_Avoid_: purchase, transaction

**Customer**:
A person or organization that places Orders.
_Avoid_: client, buyer, account
```

## Rules

- **Be opinionated.** When several words mean the same thing, pick one and list
  the rest under `_Avoid_`.
- **Keep definitions tight.** One or two sentences. What it IS, not what it does.
- **Project-specific terms only.** General programming concepts (timeout,
  retry, cache) do not belong even if they come up a lot.
- **Keep the client's original term** as an alias when the conversation ran in
  another language and the term is a real domain word — e.g. `_Also_: "faktura
  pro forma" (PL)`.
- **Challenge conflicts.** If the client uses a term in a way that contradicts
  the repository context or an earlier definition, say so and settle it.

## When to include the section

Always on the initiative track. On the feature track only when at least two
real domain terms were sharpened. Never on the quick track.
