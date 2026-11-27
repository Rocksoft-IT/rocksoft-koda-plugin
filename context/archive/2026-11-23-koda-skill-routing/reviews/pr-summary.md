<!-- preview-link -->

**What this delivers:** When a developer works in Claude Code or Codex in a repository that has Koda, Koda now points the assistant to the right Rocksoft path on its own. A new session opens with a short map and the next step for any open change. A request like "add..." or "fix..." (also in Norwegian and Polish) starts the right path, while a question like "how does X work?" starts nothing. The first time, Koda asks once whether changes are built locally in the developer's session or by Koda from an issue, and the team shares that answer. It also tells the team once when their own commands overlap with Rocksoft's tools, asks once which to use, and remembers it. A ready-made section for the team's instruction file and an updated README explain this, and that nothing is sent anywhere and no code is changed. This builds on the previous part and is released after it.

**Your decision is needed on:**
- The Rocksoft workflow tools are pinned to release 3.2.0 of the distribution repository, which is not published yet, and the whole new Koda version depends on it. Please merge both parts only after that release exists, or tell us which release to pin.
- We could not confirm that Codex runs plugin hooks in its command-line version (its documentation mentions only the desktop app). If it does not, routing there works only in the desktop app. Tell us if that is acceptable.

## QA brief (for the preview check)
- **Applies to browser QA:** no (hooks and documentation for Claude Code and Codex; nothing renders in a browser)

**Status:** Ready to merge once release 3.2.0 is published and a developer has tried a new session, an "add..." request and a question in Claude Code (and Codex) with the plugin installed.
