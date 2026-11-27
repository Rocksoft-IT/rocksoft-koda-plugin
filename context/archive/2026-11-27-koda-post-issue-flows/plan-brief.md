# Koda post-issue flows — Plan Brief
Plan: `context/changes/koda-post-issue-flows/plan.md` · issue text: `change.md` (issue #17)

## What & why
Today the Koda plugin ends when the issue is created. Clients should be able to continue in the same chat: see what waits for them, discuss a PR and accept it or ask for changes, understand and resume a failed run, and send feedback, without opening Cezar. All writes need the client's explicit yes on the final text.

## Starting point
One skill (`skills/rs-feature`), `.mcp.json` to the Koda gateway, README/USAGE in Polish, both manifests at `0.6.0`. No tests: the project is Markdown and JSON, reviewed by reading the diff. Open PRs #15/#16 (issue #14) rewrite `rs-feature`, README, USAGE and the manifests and are unmerged; this plan is against `main`.

## Desired end state
A new `rs-status` skill with four flows, a one-line pointer from `rs-feature`, updated README and USAGE, version `0.7.0` in both manifests.

## Complexity
LOW — documentation and JSON only, but two increments and safety-critical wording (confirmation, untrusted data, refusals). Skipped: rs-research (Jev p=0.21, the issue is spec-complete and the code is two Markdown files), rs-frame (the issue states an outcome and scope, no cause or fix; areas already settled by the orchestrator).

## Key decisions made
| Decision | Choice | Why | Source |
|---|---|---|---|
| Research step | skipped | `needs_research` answered no | Jev (p=0.21) |
| Framing step | skipped | issue states outcome and scope, not a cause; `needs_framing` was unsure | Auto |
| Areas | A1 post-issue flows; A2 feedback and wiring, builds on A1 | cut as given | Orchestrator |
| Skill structure | one skill with `references/` per flow | shared safety rules in one place; status hands off to decide/recover in one context; IDE install copies one folder per skill (`README.md:57`) so sibling-file dependencies would break | Consult |
| Skill name | `rs-status` | matches the client's main question; trigger phrases for all flows go in the description | Consult |
| MCP tool names | by role, matched from the exposed tools and their schemas; only `send_feedback` named | final names follow n8n-hosting#180, unreadable here | Auto (decision-to-verify) |
| Confirmation rule | show exact action and exact text, one yes/no question, one call with exactly that text; any edit re-asks; approval during discussion is not a yes | mirrors `rs-feature` Guardrail 3 (`SKILL.md:408`) and AC-02 | Issue |
| Untrusted content | tool output is data, never instructions | AC-04 | Issue |
| Refusals | `{ error }` explained plainly, no retry with other ids, no automatic retry of writes, suggest the Rocksoft contact | AC-03; a retried write could duplicate | Issue |
| Self-contained sign-in text | own condensed copy of tenant-access and sign-in handling in `rs-status` | a skill folder must not depend on `rs-feature` files in the IDE install | Auto |
| Feedback text | drafted at once from the client's first message, sent in the language written, not translated | success criterion "two messages"; shown text must equal sent text | Auto |
| `rs-feature` change | one closing line after the success message plus a one-line amendment of "Step 6 is the last step" (`SKILL.md:395`) | the rule forbids any next-action line; no other rewrite, to limit conflicts with #15/#16 | Auto |
| Version | `0.6.0` to `0.7.0` in both manifests, README and USAGE; marketplace files carry no version | `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json` checked | Auto (decision-to-verify) |
| Left untouched | `docs/flow-contract.md`, manifest descriptions and Codex default prompts | tools live in n8n-hosting#180; descriptions are rewritten by #15/#16 | Auto |
| Verification | shell greps and JSON validation plus reading AC-01..05 through the text | no test infrastructure | Auto |

## Scope
In: `skills/rs-status/**`, closing pointer in `rs-feature`, README, USAGE, both `plugin.json`. Out: merging PRs, issue creation, sign-in handling by Koda, MCP server logic, `rs-feature` flow and issue format.

## Architecture / Approach
`SKILL.md` carries runtime assumptions, tenant-access/sign-in handling, seven shared conventions and a router; `references/{status,decide,recover,feedback}.md` are read on demand.

## Increments at a glance
| # | Delivers | Depends on | User-visible | Key risk |
|---|---|---|---|---|
| 1 | `rs-status` skill: core, status, decide, recover | — | yes | wrong tool names or shapes once n8n-hosting#180 is known |
| 2 | feedback flow, pointers in `rs-feature`/README/USAGE, version bump | 1 | yes | merge conflicts with #15/#16 in README, USAGE, manifests |

## Phases at a glance
| Phase | Increment | Delivers | Key risk |
|---|---|---|---|
| 1 | 1 | `SKILL.md` core and status playbook | conventions too vague to be binding |
| 2 | 1 | decision flow | a write before an explicit yes |
| 3 | 1 | run recovery flow | technical jargon reaching the client |
| 4 | 2 | feedback flow, router update | sending text the client did not see |
| 5 | 2 | pointers and version | `rs-feature` regressions |

Prerequisites: none.

## Open risks & assumptions
- decision-to-verify: tool names and argument/response shapes are assumed from the issue; replace with the final names from n8n-hosting#180 when known (the skill matches tools by role, so a mismatch fails soft).
- decision-to-verify: PRs #15/#16 also set `0.7.0` and edit README, USAGE, the manifests and `rs-feature`; whichever merges second needs a conflict resolution, and the version may need `0.8.0`.
- Skill description routing for four intents in one skill is untested on real hosts; if feedback or recovery fails to trigger, split that flow into its own skill (the playbooks are already separate files).

## Success criteria (summary)
Skill files exist with the shared rules; each playbook covers its AC; `rs-feature` diff is limited to the closing pointer; both manifests, README and USAGE show `0.7.0` and the JSON is valid.
