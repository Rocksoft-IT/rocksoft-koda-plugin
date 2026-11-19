<!-- preview-link -->

**What this delivers:** Clients who work with OpenAI Codex (command line, IDE extension or Codex cloud) can now install the Rocksoft Koda plugin and use it the same way Claude users do: describe a request in their own words and get a ready-to-build issue in their repository after an explicit yes. Sign-in instructions are now shown for the tool the client is actually using, and the install, sign-in and update steps for both Claude and Codex are in the README and user guide. Claude installs keep working as before; the plugin version moves to 0.6.0.

**Your decision is needed on:**
- The Codex IDE extension and Codex cloud setups are written from OpenAI's documentation and could not be tried before release; we documented them as described there. Tell us if you want them tested with a real account first.
- Codex cloud also needs the Rocksoft sign-in gateway to accept Codex cloud's sign-in; this is tracked separately.

## QA brief (for the preview check)
- **Applies to browser QA:** no (a plugin and documentation change; there is no web page to open)

**Status:** Ready to merge once someone has tried the install and sign-in steps in Codex with a real account.
