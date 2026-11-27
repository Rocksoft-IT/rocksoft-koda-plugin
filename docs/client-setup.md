# Client setup: Koda with rs-skills in a repository

One-time setup so every developer who clones a client repository gets Koda and
the Rocksoft rs-* skills (plan, implement, review, archive) without installing
anything by hand or naming a skill. Koda lists `rs-skills` in its own
marketplace, so adding the Koda marketplace is the only source you configure.

Chat hosts (Claude Desktop, claude.ai) are not covered here: they use Koda
through Rocksoft Flow only, see the README.

## Claude Code

### Project settings (committed)

Add this to `.claude/settings.json` in the client repository:

```json
{
  "extraKnownMarketplaces": {
    "rocksoft-koda": {
      "source": {
        "source": "github",
        "repo": "Rocksoft-IT/rocksoft-koda-plugin"
      },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "rocksoft-koda@rocksoft-koda": true
  }
}
```

`rocksoft-koda` declares `rs-skills` as a dependency, so installing Koda brings
rs-skills with it; there is no second plugin to enable.

### Per developer, once per clone

`enabledPlugins` alone does not install anything. Each developer runs:

```bash
claude plugin marketplace add Rocksoft-IT/rocksoft-koda-plugin
claude plugin install rocksoft-koda@rocksoft-koda
```

### Auto-update

- Marketplace manifests have no auto-update switch. `autoUpdate` is a boolean on
  an `extraKnownMarketplaces` entry in settings, and Claude documents it for
  managed settings. In a project `.claude/settings.json` it may be ignored.
- If it is ignored, turn auto-update on per developer in `/plugin` (Marketplaces,
  `rocksoft-koda`, enable auto-update), or update by hand with
  `claude plugin marketplace update rocksoft-koda`.

## Codex

Codex plugins have no dependencies, so both packages are listed in the Koda
marketplace and both are enabled.

### Project config (committed)

Add this to `.codex/config.toml`:

```toml
[plugins."rocksoft-koda@rocksoft-koda"]
enabled = true

[plugins."rs-skills@rocksoft-koda"]
enabled = true
```

### Per developer, once per clone

```bash
codex plugin marketplace add Rocksoft-IT/rocksoft-koda-plugin
codex plugin add rocksoft-koda@rocksoft-koda
codex plugin add rs-skills@rocksoft-koda
codex mcp login rocksoft-koda
```

Then start a new Codex session.

### Trust the hooks

Koda ships session hooks. Codex asks you to trust a plugin's hooks once: open
`/hooks` in Codex, review the Koda hooks and trust them. Until you do, the hooks
do not run and Codex behaves as if Koda had none. The Codex documentation words
plugin hooks as desktop-only and does not confirm them in the CLI; if no hook
output appears after trusting them in the CLI, that is the reason.

### Updates

Codex has no auto-update. Upgrade the marketplace and start a new session:

```bash
codex plugin marketplace upgrade rocksoft-koda
```

## Pinned release

The `rs-skills` entry in both Koda marketplaces is pinned to a release tag of
the rs-skills distribution repository. Rocksoft bumps that tag, together with the
Koda plugin version, when a new rs-skills release is published.
