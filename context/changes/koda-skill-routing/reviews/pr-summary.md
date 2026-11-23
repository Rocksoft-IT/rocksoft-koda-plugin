<!-- preview-link -->

**What this delivers:** Teams that add the Koda marketplace to their repository now get the Rocksoft workflow tools (plan, build, review, archive) installed together with Koda in Claude Code and Codex, plus a setup guide that shows the one-time team configuration for both. This is the first part of two; the automatic routing of requests comes in the next part, which builds on this one and is released after it.

**Your decision is needed on:**
- The workflow tools are pinned to release 3.2.0 of the Rocksoft distribution repository, which is not published yet. Please merge this part only once that release exists; until then installing the updated Koda would fail to find the workflow tools. Tell us if a different release should be pinned.
- Automatic updates for Claude Code can be switched on in the team settings, but Claude documents this only for centrally managed setups, so developers may need to enable it once themselves. The guide says so.

## QA brief (for the preview check)
- **Applies to browser QA:** no (documentation and plugin configuration only, nothing renders in a browser)

**Status:** Ready to merge once the Rocksoft distribution release 3.2.0 is published and a developer has followed the new setup guide on a fresh clone.
