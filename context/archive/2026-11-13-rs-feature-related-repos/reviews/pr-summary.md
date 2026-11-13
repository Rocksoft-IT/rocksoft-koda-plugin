<!-- preview-link -->

**What this delivers:** When you start a request with Rocksoft Koda, it now also looks at repositories related to the one you picked, tells you about them, and asks which of them your request actually touches. If it touches more than one, it drafts one issue per repository (clearly cross-linked, with a suggested order to build them in) and only creates them once you say yes to the whole batch — including a repository you aren't directly assigned to, if it's related to one you are.

**Please check on the preview:**
- Start a request on a repository that has no related repositories (or try it before this change lands) and confirm the conversation looks exactly as before — no new question appears.
- Start a request that clearly touches two related repositories and confirm you're asked, once, which ones it touches, shown a deploy order, and asked once for a final yes before anything is created.

**Status:** Ready to merge once you have checked the preview.
