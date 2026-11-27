---
change_id: rs-feature-existing-issue
title: rs-feature hands off a request that already has an issue
status: planned
created: 2026-11-27
updated: 2026-11-27
archived_at: null
---

## Notes

In the Rocksoft Koda plugin repo, make the `rs-feature` skill handle a request that points to an existing issue.

Why: a developer asked an agent to "fix Linear issue 1687". The matching GitHub issue (#1247) already existed. The agent skipped the skill's issue creation ("the issue is already complete") and implemented the change locally in its own session, so Rocksoft Flow/Koda never started. Koda starts a run only from the `rs-feature` or `rs-bug` label on a GitHub issue. The skill's three tools (list_repositories, get_repository_context, create_feature_issue) can only create NEW issues, with labels ["rs-feature","<track>"]; none can label an existing issue.

Wanted behaviour:
1. In "Initial response": when the request points to work that already has an issue (GitHub issue number or link, or a tracker ticket id whose issue already exists in the repository), do not create a duplicate and do not build the change. Tell the client, in their language, that the issue already exists and that the run starts from the issue's `rs-feature`/`rs-bug` label, which this skill cannot add; ask them to add the label or send the issue number to their Rocksoft contact. Continue with Step 0 only if the client says the existing issue is wrong or incomplete and wants a new one. Treat this as a complete outcome, not an error.
2. In Guardrails #1: add that the skill never implements the request itself, including when the issue exists; building happens in Rocksoft Flow after the issue carries the label.

Constraints: keep the existing style (numbered guardrails, bold lead-ins, no em dashes, plain dashes only). English text. Small diff. Version bump / USAGE.md / README only if recent skill-text commits did so.
