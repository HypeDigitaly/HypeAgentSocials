# Phase 0 — Virlo & Postiz trial protocols

*Written 2026-08-06. These are the two vendor trials Phase 0 requires, stated as executable test scripts so they can run the day the MCP connections exist. Verdicts are recorded here and in `DECISION_LOG.md`. Governing text: `ARCHITECTURE_PLAN.md` §17.2 Phase 0, §16.2 OD-16/OD-17a, §7.8 OP-2.*

**Connection method (both vendors):** hosted MCP servers added to Claude Code user-scope config — Virlo at `https://dev.virlo.ai/api/mcp/mcp`, Postiz at `https://api.postiz.com/mcp`, each with a bearer-token header. Keys live in the operator's local Claude config, never in this repository.

---

## Trial 1 — Virlo (1 week, decides OD-16)

**Precondition (OD-17a, binding):** Virlo's terms of service are retrieved, dated, and read for a pipeline/derivative-use permission **before the first credit is spent**. Any surprise is logged in the vendor roster.

**The three gating questions the trial must answer before any subscription renews:**

| # | Question | How the trial answers it | Verdict |
|---|---|---|---|
| Q1 | **Is full programmatic MCP/API access genuinely included at the Starter tier (~$49/mo)?** Virlo's own guide and pricing page conflict on this, and this single fact gates adoption | Connect via MCP on the trial/deposit account; enumerate the exposed tools; call at least one tool from each family the pipeline needs (trends, tracking, sounds/audio, audience). Record which calls succeed at which tier and what each costs in credits | *(pending)* |
| Q2 | **Does a niche monitor in this subject area (AI / B2B SaaS, Czech + English) beat what the free portfolio already surfaces?** | Run the same 5 watch topics through Virlo trend queries and through the free sources (HN, PH, HF, Bluesky, Google News, YouTube) for 3–5 consecutive days; compare: does Virlo surface anything the free portfolio missed, earlier, or with better velocity data? A vendor that only re-confirms what free sources already found fails this question | *(pending)* |
| Q3 | **What are the unpublished rate limits?** | Observe throttling behaviour during Q1/Q2 calls; deliberately batch a realistic per-run call volume (one full collection pass) and record any 429s, credit-burn rate per call class, and the effective calls-per-day ceiling | *(pending)* |

**Verdict rule (OD-16):** pass on all three → **adopt (a)**. Fail on any → move to **(b) Shortimize** on the same three questions. If that also fails → **(c) the short-form trend axis is absent** — and per `RISK_LOG.md` W7-01 there is no rung below: the digest must say "absent," never "degraded."

**Czech note:** during Q2, specifically check Virlo's CZ-market coverage — the Czech axis now rests on only four automated sources (W8-2), and Virlo CZ is one of them.

---

## Trial 2 — Postiz (one sitting, decides OP-2)

**What is being tested:** the entire distribution design (§7) rests on a paper claim — that Postiz can hold **drafts that never auto-publish**. This trial converts the claim into evidence. No real social account needs to be connected for most checks; a test/sandbox channel is enough for the rest.

**Checklist:**

| # | Check | Pass condition |
|---|---|---|
| 1 | **Draft-without-schedule creation** via MCP/API | A post can be created in draft state with no schedule time and no auto-publish trigger ever firing |
| 2 | **Draft persistence** | The draft survives a logout/restart and remains in draft state indefinitely — no silent expiry into a publish queue |
| 3 | **State transitions** | Draft → scheduled and scheduled → draft both work and are visible via the API |
| 4 | **Review surface** | Drafts are visible and readable in Postiz's own UI, where a human can inspect them before anything moves |
| 5 | **No-publish guarantee under MCP** | Enumerate the MCP tools: identify every tool capable of publishing or scheduling; confirm draft creation is possible without invoking any of them. Record the full tool list — this becomes the allowlist input for §7.4's single enforcement point |
| 6 | **AI-disclosure field probe** | Note which connected platforms expose a native AI-label field through Postiz today (re-tested formally in Phase 6; a first reading now is free) |

**Verdict rule (OP-2):** checks 1–5 pass → the drafts-only bridge design stands. Any failure → the fallback ladder (§7.2) governs; rung 2/3 becomes the working posture and the finding is logged before Phase 6 commits to the bridge.

**Safety note:** in v1 design, nothing ever publishes live by default. During this trial, no tool call that publishes or schedules to a real channel is made at all — draft-state calls only. If a real channel must be connected for check 1, use a private/test account, not a brand account.

---

## Recording the outcome

Each trial's verdict gets: a dated row in `DECISION_LOG.md` (OD-16 resolved to a/b/c; OP-2 confirmed or fallback invoked), the raw observations appended to this file, and any terms-of-service surprise logged in the vendor roster. A failed trial is a normal, recorded outcome — never a silent gap.
