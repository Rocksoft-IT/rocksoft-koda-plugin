# Fix round 1

- Finding 1 (MEDIUM): FIXED - trigger rewritten around what the agent observes (issue number/link or "an issue exists"); bare tracker ids get one question "Is there already a GitHub issue for this?" and branch on the answer.
- Finding 2 (LOW): FIXED - trigger limited to requests to build or fix that issue itself; Step 0 continues when the issue is wrong or incomplete, or the request is separate or new.
- Finding 3: FIXED - one clause: no tool is called, so the Step 0 sign-in check is not needed for the hand-off.

Verification (run, not read): 1.1 `grep -q 'already has an issue'` exit 0 (wording kept, grep unchanged), 1.2 `grep -q 'never implement'` exit 0, 1.3 no em dash in diff exit 0. Manual 1.4 left unflipped.
