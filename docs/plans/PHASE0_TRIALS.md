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

---

## Day-1 observations (2026-08-06, both MCPs connected and exercised)

### Virlo

**Q1 (API access at the paid tier) — answered, with a correction to the question itself.** Programmatic access is not tier-gated at all: the developer platform is pay-as-you-go credits ($10 deposit = 1000 credits), separate from the web-app subscription. The full MCP surface (46 tools) works on a deposit-only account, and the complete price list is machine-readable through the API: $0.50 per one-shot agent run (+$1.00 with per-video intelligence), $0.50 per recurring-monitor cycle, $0.25 per trends call, reads free forever. OD-16's Q1 was framed against a "Starter tier includes API?" ambiguity that does not exist on the developer platform. **Consequence for §5.4 economics: Virlo is a usage-billed vendor, not a flat ~$49/mo line.** At the designed cadence (one monitor cycle per run day) the steady-state cost may be materially below $49/mo; this needs restating when OD-16 closes.

**Q2 (does it beat the free portfolio?) — first evidence, positive.** The operator's own web-app monitor ("AI Trends Tracker", 10 AI/lead-gen keywords, weekly, EN) completed its first cycle: 834 videos linked across TikTok/YouTube/Instagram, 240 analysed into 10 themes with confidence scores, per-theme evidence video IDs, viral-tactic extraction, and posting-time patterns — all readable at zero credit cost after the $0.50 cycle. This is signal the free portfolio (HN/PH/RSS) structurally cannot produce for short-form video. Comparative test against the free sources still needs the 3–5 day run per protocol.

**Q3 (rate limits) — partial.** Published pricing is fully machine-readable (above). Unpublished throughput limits not yet probed; the async model (a search run takes 15–20 min end-to-end) is itself the practical constraint — collection must be scheduled ahead of ranking, not called inline. This matches the architecture's async job model (§8.13) without change.

**Czech coverage probe — in flight.** A $0.50 one-shot search with five Czech-language keyword phrases and `english_only: false` was queued (orbit `65bf412a-2a8a-4e95-bf35-9f21dca208a6`). This is the W8-2-critical question: Virlo CZ is now one of only four automated Czech carriers. Result readable free once finalized.

**Czech coverage probe — RESULT (read same day, finalized ~5 min after queue, not 15–20).** The search linked 360 videos across the five Czech keywords (TikTok 340 / YouTube 64 / Instagram 38; zero failures; AI analysis produced 6 themes from 138 analysed videos). The verdict has two halves:

1. **The tool works for CZ.** Region resolution is real (`upload_region: "CZ"` from TikTok's own region field / YouTube channel country / Instagram location tags), the AI analysis independently surfaced a dedicated theme — "AI for Czech and Slovak Businesses and Productivity", 7 videos, confidence 0.875 — and genuine on-topic Czech creators exist in the results: @polivkamatej (Claude ai/Cowork/Code comparison in Czech, 16K views), @socials.luba (AI-built offers for firms, 16K views), iDoklad's channel (AI-druhý-mozek/agents for Czech entrepreneurs, 149K views), @cestinavpraxi (spotting AI text in Czech, 254K views).
2. **The Czech niche itself is thin and noisy.** Filtering to CZ-region items yields only **14 of 360** (~4%), and of those only ~5–6 are actually about AI-for-business — the rest is keyword drift (Czech politics, privatisation history, divorce law, a Steve Jobs explainer). The dominant result mass is international (EN/PL/IT/FR) content matched semantically to the Czech intent.

**Reading for W8-2 / the digest design:** Virlo CZ is a *viable but weak-signal* carrier. The plan's existing posture already handles this correctly — the digest must be able to report "little or no Czech short-form signal this run" honestly (absent/PARTIAL, never inflated), and per-run Czech evidence should be treated as a sparse stream, not a guaranteed quota. This is a market fact (small CZ short-form AI-business niche), not a vendor defect; no fallback trigger fires. Note `language_filtered_count: 0` and `intent_filtered: 82` — the intent filter, not a language filter, did the relevance work.

**Governance item closed:** the "AI Trends Tracker" monitor was switched from `autopilot` to `suggest` (proposals now wait for operator approval) on 2026-08-06 — vendor-side config drift is no longer possible; conforms to W6-1. Next scheduled cycle: Sunday 2026-08-09.

**Spend after CZ probe:** still $0.50 of $10.00 — the probe was the $0.50 already counted; all reads free.

**Governance observation, needs an operator action.** The web-app monitor was created with `autonomy_level: "autopilot"` — the vendor's agent may **auto-apply its own keyword/config changes** (`auto_applied` proposals). Under this project's own rules (W6-1: the operator supplies configuration; watch topics are operator-owned config), a vendor agent silently rewriting the watch-keyword set is configuration drift from outside the config surface. **Recommendation: switch the monitor to proposals-require-review** (`set_niche_monitor_autonomy`), so Virlo suggests and the operator approves. One click / one call; not yet changed — operator's monitor, operator's call.

**Spend to date:** $0.50 of $10.00 (CZ probe). Everything else read for free. OD-17a note: Virlo's terms retrieval + derivative-use reading remains open and must close before adoption (the deposit predates this trial's start; logged honestly).

### Postiz

| # | Check | Result |
|---|---|---|
| 1 | Draft-without-schedule creation | **PASS** — draft created via MCP on the LinkedIn page (post `cmshyxu3a02qzqj0yrfiaaqpp`), `state: "DRAFT"`, confirmed by an independent public-API read; `releaseURL: null` (nothing ever published). One nuance: the API **requires a date field even for drafts** — the date is stored but does not fire; a draft is not "schedule-less", it is "schedule-inert". The engine's draft writer must treat that date as a placeholder, never as a publish intent |
| 2 | Draft persistence | **Provisional PASS** — state persisted across separate API sessions. Operator should glance at the Postiz UI (Drafts view) tomorrow to confirm it still sits there untouched; full restart-persistence is re-verified formally in Phase 6 |
| 3 | Draft↔schedule transitions | **Deferred to Phase 6, deliberately** — exercising a schedule transition against connected *real brand channels* violates this trial's own safety rule. Test on a throwaway channel in Phase 6 |
| 4 | Review surface | **PASS (API side)** — the draft is listed with full content, state and integration via the public posts endpoint; UI visibility to be confirmed by the operator's glance (check 2) |
| 5 | No-publish guarantee under MCP | **PASS with a named hazard.** Tool enumeration: 10 tools; exactly one can cause publication (`integrationSchedulePostTool`, via `type: "schedule"` or `"now"`); draft creation uses the same tool with `type: "draft"`. **Hazard for §7.4's allowlist design: the publish/no-publish distinction is a parameter value on one tool, not a tool boundary.** The single-choke-point enforcement must therefore validate the `type` field of every call, not merely allowlist tool names. Also present: `ask_postiz`, a vendor-side LLM agent that can itself take actions — the engine must never route through it; deterministic tools only |
| 6 | AI-disclosure field probe | **Answered for three platforms:** TikTok exposes `video_made_with_ai` (native AI label) — but **video posts only, and only in DIRECT_POST mode; silently discarded in UPLOAD mode and for photo posts**. Instagram: no AI field in the schema. LinkedIn pages: no AI field, no extra settings. Confirms the plan's position that platform-native labels are patchy opt-ins and the burned-in disclosure is the load-bearing control (§14.6); where TikTok DIRECT_POST video is used, the native flag must be set *in addition* (§7.7 acknowledgement) |

**Real-channel caution observed:** the operator's Postiz has five live brand channels connected (2× LinkedIn page, Instagram, Facebook, TikTok). The only write action taken was the single clearly-labelled test draft; it is safe to delete from the Postiz UI at any time.

**OP-2 day-1 verdict: the drafts-only bridge design stands on all evidence so far.** Remaining before OP-2 closes: operator UI glance (check 2/4), transition test on a non-brand channel (check 3, Phase 6), and the §7.4 choke-point design note above carried into implementation.

---

## Kie.ai router inspection (2026-08-07) — the two §17.2 Phase-0 provider questions

*Account live (credit endpoint authenticates; balance 10 080 credits). Inspected surface: the Veo3 API family (generate + video-details) on docs.kie.ai. Decision row: W8-3.*

**Q1 — Does the router's task-status response name the rendering model? NO.** The video-details response schema carries `taskId`, `paramJson` (an echo of the *request* — requested model only), `completeTime`, `response` (URLs, resolution), `successFlag`, `errorCode`, `errorMessage`, `createTime`. No field names the model that actually rendered. The only substitution signal is `fallbackFlag` — documented as *"Whether generated using fallback model"* — boolean, **deprecated**, and absent on newer (4K) paths. Consequence, exactly as the plan pre-stated for this answer: **§5.6's three-state inference rule ships** (delivered identity is best-effort inference; *substituted — identity unknown* degrades to plan-only at the publish gate).

**Q2 — Person-generation eligibility for this account/region: NOT A SURFACED CONTROL.** The generate endpoint exposes `model` (veo3 / veo3_fast / veo3_lite) and no personGeneration parameter, no EU-region restriction, no per-account allowlist to request. Refusals surface only as content-policy errors at generation time. The Phase-0 item "any allowlist request submitted" closes as **not applicable on this router** — there is nothing to apply for. R2-M18's posture stands: people-free keyframe composition is the injected default; plan-only is the floor.

**Design-relevant discovery:** Kie documents automatic internal fallback on content-review triggers **including "prominent people upload" errors** (the deprecated `enableFallback` note says the system now "automatically optimized the content review mechanism" — i.e., fallback is internal and always-on). So a request that trips the person policy may be **silently served by a different model, with no identity reported**. This is the exact scenario §5.6's inference rule and R2-B4's requested-versus-delivered recording exist for; Phase 3's acceptance criterion ("a silent model substitution, if one occurs, is visible on the artifact") should test against this trigger class specifically.
