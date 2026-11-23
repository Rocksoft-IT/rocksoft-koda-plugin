# AGENTS.md section template: Rocksoft Koda

Copy the section below into the `AGENTS.md` at the root of the client repository
through a normal PR. `AGENTS.md` is the single source for both Claude Code and
Codex: Codex reads it directly, and Claude Code reads it through a short
`CLAUDE.md` pointer (snippet at the end; `AGENTS.md` has no import syntax, so
nothing is imported).

Koda never writes `AGENTS.md` or `CLAUDE.md` for you.

---

## Rocksoft Koda and rs-skills

This repository works with Rocksoft. Koda (the `rocksoft-koda` plugin) brings
the Rocksoft rs-* skills with it, so nobody installs skills by hand or has to
remember which one to run.

### What Koda does here

- **At session start** it shows a short map of where each kind of request goes
  and the next step for any open change under `context/changes/`.
- **When a message looks like work** ("add", "fix", "change", "legg til",
  "fiks", "endre", "dodaj", "popraw", "zmien", ...) it adds a routing hint so the
  right path starts. It never blocks or rewrites your message.
- **Questions are answered normally.** "How does X work?" starts nothing.
- **Overlaps are named once.** If this repo has its own commands or skills that
  do the same job as an rs-* skill (for example a `/preflight` next to
  `rs-impl_review`), Koda says so once per change of the installed set and asks
  once which one to use for an unnamed request.

Hooks only read local repository state, send nothing anywhere and change no
code. The only files written are `.rocksoft/koda.json` (after you answer a
question) and small cache files outside the repository.

### Workflow

| You ask for | What happens |
|---|---|
| A change (add, fix, change something) | The path chosen in `.rocksoft/koda.json`: `local` runs the rs-orchestrator agent in your session, `server` hands the request to Koda (rs-feature), which turns it into an issue Rocksoft builds |
| Review, plan, implement or archive an existing change | The matching rs-* skill (rs-impl_review, rs-plan, rs-implement, rs-archive) |
| A question or an explanation | Answered normally, no change path |

### One-time install

Set up the project once and each developer installs once per clone. The exact
settings and commands for both hosts are in
[client-setup.md](https://github.com/Rocksoft-IT/rocksoft-koda-plugin/blob/main/docs/client-setup.md)
in the Koda plugin repository (Claude Code:
`.claude/settings.json` plus one install command; Codex: `.codex/config.toml`
plus the marketplace commands).

Codex only: hooks run after each developer trusts them once. Open `/hooks` in
Codex and trust the Koda hooks.

### `.rocksoft/koda.json`

Tracked in the repo, so the whole team shares one decision. It is created the
first time Koda asks how changes should be built; change it through a PR.

```json
{
  "version": 1,
  "mode": "local",
  "overlaps": { "preflight-vs-rs-impl_review": "rs" },
  "minKodaVersion": "0.7.0"
}
```

- `mode`: `local` (rs-orchestrator builds in the developer's session) or
  `server` (Koda builds from an issue).
- `overlaps`: team-wide answer for an overlap, by the id Koda printed. `rs`
  means the rs-* skill, `repo` means the repo's own command. A developer's
  personal answer is kept outside the repo and the team entry wins.
- `minKodaVersion`: bump it when Rocksoft announces a release. On Codex, which
  has no auto-update, a session start older than this version reminds the
  developer to run `codex plugin marketplace upgrade rocksoft-koda`.

### Use the Rocksoft skills

Prefer the rs-* skills for planning, implementing, reviewing and archiving a
change; they keep the plan, the commits and the review in one place. Name them
only when you want a specific step, otherwise just describe what you need.

### Rocksoft is a partner, not a vendor

Rocksoft is available at any time: describe a request to Koda in chat (Claude
Desktop, claude.ai or Codex), or write to koda@rocksoft.pl.

### `CLAUDE.md` pointer

Add these lines to the repository's `CLAUDE.md`, so Claude Code follows the
same instructions:

```markdown
# Claude Code

This repository's instructions live in AGENTS.md, including the Rocksoft Koda
section. Read AGENTS.md before starting work and follow it.
```
