---
change_id: rs-feature-multi-repo-split
title: Rs-feature picks the right client repository and splits multi-repo requests
status: archived
created: 2026-11-16
updated: 2026-11-16
archived_at: 2026-11-16T12:01:20Z
---

## Notes

https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/10


Clients can now have several repositories in Koda (for example a backend and a frontend). `list_repositories` returns each repository's `role`, `description` and `client` (after Rocksoft-IT/n8n-hosting#159).

1. Repository choice: never assume one repository. When the user has one repository, use it. When several, group them by client; pick the repository yourself only when the request clearly matches one repository's role or description, and say which one you picked and why in one line; otherwise ask the user with the repositories listed by role and description. Never mention repositories the user's list does not contain.
2. Cross-repository requests: when one request needs work in more than one repository of the same client (for example a new API in the backend and its screen in the frontend), agree the split with the user, then create one issue per repository with `create_feature_issue`, all with the same new `feature` value (a UUID generated once per request). Each issue states its own part and names the other parts by role, with links once they exist. Only repositories of the same client may be in one split.
3. Confirmation: show all the issues of the split in the summary before submitting, and submit them only after the user confirms.

Acceptance: a two-repository client is asked (or told) which repository; a backend + frontend request produces two issues with the same `feature` footer line, shown on the Cezar Pipeline as one feature.

Related: Rocksoft-IT/cezar#257 (PRs #262, #263, #265, #266, #267).
