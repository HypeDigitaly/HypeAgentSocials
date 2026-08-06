# HypeAgentSocials — Stage 4 Architecture Plan

*The single canonical architecture and delivery plan for the design phase. Assembled 2026-08-06 (Wave 3b) from the Wave-3 drafts, the decision log, the risk log and the sixteen Wave-1 research briefs consolidated in `docs/research/SYNTHESIS.md`.*

*Design phase only (D-01). This document contains no product code, no pseudocode, no command-line or configuration syntax, no schemas and no mandatory folder tree. Diagrams are plain text. Every configuration knob is described in prose. Volatile factual claims cite the research brief that owns them.*

---

## §0. How to use this document

### 0.1 The problem, restated

We are designing one configurable console application that turns *what is happening in the world* into *marketing assets a specific company could actually publish* — and that does it safely enough to run overnight while nobody is watching.

Each run works through one **theme** — a tenant configuration naming a company, its offers, its audience, its languages, the topics it cares about and the destinations it publishes to. The first theme is oriented around HypeDigitaly s.r.o. and HypeLead.ai: research topics around AI, coding agents, lead generation and outbound/AI-sales discourse; outputs in Czech and English. The same engine must later serve a completely different company and topic set by changing configuration and brand-truth pointers, not by rewriting the agent.

The system holds two lists strictly apart. **List A** is where we research — the sources we read for viral discourse, ICP pain, launch hype, search demand, competitor ad creative and short-form format trends. **List B** is where we create for — LinkedIn, Instagram, TikTok, YouTube Shorts, Facebook, optionally X, and the brand's own blog. A research source is never a publish target. That boundary is enforced structurally, by a publish allowlist read at one fail-closed enforcement point, not by convention (§7.4, §11.2).

Between the two lists sits the part that makes the output worth reading. Signals are ranked on attention, brand fit and freshness, with a hard floor on brand fit so weak-fit trends are skipped rather than force-fitted (§2.7). Surviving topics are **spun** through brand truth resolved from three sources with a defined precedence — the theme's own configuration, the company's Notion knowledge base read over a model-context-protocol connection or its REST equivalent, and the live public website used to verify commercially binding facts (§6). Nothing commercial is ever invented: if the truth cannot be resolved, the run degrades honestly to research-only rather than filling the gap.

Assets are then written per destination per language, passed through a fixed chain of gates — spin, claim, voice, claim again, platform (§14) — and accompanied by visual and video plans that are always produced even when there is no budget and no key. Short-form video is a core design driver rather than an add-on: the pipeline is keyframe-first, so the brand-correctness decision is made on a four-cent image before a thirty-cent clip is bought (§4). Media generation is routed through a provider abstraction with a model registry that carries prices, licences and recheck-by dates, because model and vendor churn is structural (§5).

Everything a run produces lands in a **run pack** with a **run digest** the operator can scan in about two minutes (§12). Only after a recorded human decision may anything move toward a live outcome, and even then the system only ever creates **drafts** in the publishing bridge — a human schedules and publishes inside that tool, and a human merges any site content (§7). Live publishing and production site merges are not capabilities this system has in any mode (§11.1).

The same application must run unattended on a schedule, fail closed on missing secrets, ambiguous brand truth, policy violations or side effects the active mode forbids, survive a crash without discarding paid work, avoid duplicate work when the schedule fires again, and exit with an outcome class a scheduler can act on (§8, §9.2).

The design phase succeeds when all of that is clear, argued from evidence, and testable by a human before anything is built. Implementation is a separate plan requested separately (D-01).

### 0.2 How to read this document, and what governs it

**Structure.** §1–§6 are the core pipeline: components and orchestration, List A research and extraction, List B content architecture, the viral video pipeline, media providers, and brand truth and spin. §7–§9 are distribution, scheduling and the two end-to-end flows. §10 is the theme-configuration knob surface. §11–§12 are modes, gates and the run pack. §13 is multi-theme extensibility. §14 is voice and claim-safety enforcement. §15–§18 are risks, open decisions, the phased roadmap and the human review method. Appendix A traces one realistic topic through the whole pipeline; Appendix B is the review changelog.

**Reading paths.** An operator who wants to know *what the machine will do to my morning* should read §0.1, §12, §17 and Appendix A. An operator who wants to know *what it will cost and what could go wrong* should read §4.6, §5.4, §8.11, §15 and §16. A reviewer preparing to approve or reject this plan should start at §18, which is written for exactly that job.

**Vocabulary is normative (D-21).** Every stage, artifact, mode, gate, ledger, config block, exit-code class, provider role and connector class in this document uses the canonical name fixed in `SYNTHESIS.md` §4. No new nouns are coined anywhere, including in the sections authored at assembly. Where a research brief used a different word for the same thing, the canonical word is used and the synonym is avoided.

**Decisions bind.** `docs/architecture/DECISION_LOG.md` governs. Locked decisions **D-01…D-08** (design-phase-only scope; per-language first-class output sets; brand-truth precedence; account reality; Windows-first runtime; stack delegation; folder-based review; X reads closed) and the Wave-2 synthesis decisions **D-09…D-26** are binding on every section. The **Wave 2.5 operator rows (W2.5-1…W2.5-8) govern over any earlier synthesis recommendation they contradict** — most consequentially W2.5-4, which chose identical asset mixes in both languages against the synthesis's own lean. Where the operator overruled research, this plan re-derives the consequences rather than quietly carrying the superseded text. Refinements D-02a, D-03a, D-04a and D-08a narrow their parent decisions and never reverse them; D-02a specifically is superseded, as recorded below.

**Six things resolved at assembly.** Six items were left open when the core sections were drafted. Each is now closed, and each is reflected consistently wherever it matters rather than sitting in a list at the back:

1. **D-02a is superseded by W2.5-4, and `SYNTHESIS.md` §3.1's per-language channel table is void.** Czech gets TikTok, Instagram Reels and YouTube Shorts in v1. §3.1–§3.2 carry the replacement. No section of this plan may be read against the old table.
2. **Risk W2-08's recorded mitigation ("TikTok excluded for cs in v1") is void.** The replacement mitigation is the **six Czech design commitments** in §3.1 — recipe not translation, framing not mimicry, register discipline, understatement as a quality bar, a destination-aware production floor, and a measurable revisit trigger. This is carried in §15 and appended to the risk log as a superseding row.
3. **Media-bearing caps count masters per language, not destination derivatives** (§3.2), because one 9:16 master legitimately serves TikTok, Reels and Shorts through layered re-composition. The §10 knob is defined that way. **Masters per language is the canonical cap unit throughout this plan** — §8.11's mid-pack cap-hit illustration, §10.4's knob and Appendix A.5 all count in it, and no section counts caps in destinations. The unit's scope is *every* media-bearing master, not video alone: one 9:16 video master is one master and one 4:5 slide-art set is one master, because each is a distinct generation event that costs money. The count cap and the dollar cost gate are two independent limits and **whichever trips first stops submission**, with both recorded (§8.11).
4. **X as a publish destination is config-gated and default-off** (§3.2). Assets can be produced at no marginal cost; X is never a connected channel until an explicit decision. Whether to suppress X assets entirely is carried as an open decision (§16, OD-21).
5. **The claim-ledger location (OD-9) is carried as a recommendation, not a lock.** §6.3 assumes the Notion-primary split with hard excludes duplicated in configuration; §16 states the alternative and its cost.
6. **The two Czech prerequisites are scheduled, not assumed.** The Czech structural-calibration corpus and the Czech judge golden set are Phase-0 deliverables with their own acceptance criteria (§17), because neither the sentence-length band nor the judge threshold transfers from English.

Two further consequences follow from item 1 and are stated where they matter rather than repeated: the synthesis's remark that "the Czech mix is cheaper, which softens OP-1" is now **conditional** — true while Czech runs the carousel-to-reel recipe, false the moment Czech is promoted to generative clips (§3.1, §5.4); and every cost figure in this plan is illustrative of a price snapshot, with the forecast the operator actually sees computed from the model registry at run time with the snapshot date displayed (§5.2, §12.1).

These six resolutions, and the three seam decisions taken with them, are recorded in `DECISION_LOG.md` as rows **D-27…D-35** and as new open decisions **OD-21…OD-23**; the replaced mitigation is recorded in `RISK_LOG.md` as the superseding row **W2-08a**, with the original row left untouched so the history stays legible.

**Single-owner rule for repeated material.** Some subjects legitimately touch several sections. Each has exactly one home and the others point to it: the spin criteria S-1…S-7 live in §6.10; the eleven claim check classes live in §6.7; the spoken-claim rationale lives in §6.8; the mode capability matrix and its resolver live in §11.1–§11.2; the ledger substrate choices live in §8.6; the per-source portfolio lives in §2.3; per-stage idempotency lives in §8.5; **the canonical per-asset gate chain lives in §14 and the run-level stage order lives in §9**; **the binding between a human approval and the bytes it approved lives in §11.4**. Nothing is restated in two places with two sets of words.

**The two additions are the ones this rule was written for and did not cover.** The gate chain was stated in three sections with three different contents, each labelled or implied canonical, and §10.5 listed all three as joint owners — so a reader who noticed the divergence had no tiebreak and an implementer who did not notice built the shortest version. **A single-owner list that omits the most-restated object in the document is not doing its job.** The distinction to hold onto: §9 owns the order in which *a run* moves through its stages; §14 owns the order in which *one asset* moves through its gates. They overlap in name and not in scope, which is exactly why each needs an owner rather than a shared custody arrangement.

### 0.3 The evidence base, and which facts rot first

This plan does not restate its evidence. **`docs/research/SYNTHESIS.md` §6 — the consolidated fact ledger — is the plan's evidence base**, holding the union of all sixteen briefs' ledgers with owner, source, retrieval date, confidence grade and a recheck-by date per claim. Any figure in this document that is not a design choice traces to a row there, and the brief that owns it is cited inline.

**One warning about the evidence base itself.** `SYNTHESIS.md` §3.1's per-language channel table and §7 item 8's "equal-quality, per-language-appropriate mixes" recommendation are **void**, superseded by the operator's W2.5-4 decision and by D-27. Supersession banners have been appended in place at both locations (Wave 4, append-only exception logged in `DECISION_LOG.md`), but a reader who arrives at the evidence base by another route should know before opening it: the identical-mix rule in §3.1–§3.2 of this plan is the design, and no section of this plan may be read against the old table. Everything else in `SYNTHESIS.md` stands, including §4's normative vocabulary (D-21).

Two standing rules from that ledger bind the architecture. First, **no threshold in this system may be set from a Low- or Medium-confidence marketing-vendor statistic** — several headline engagement and quality numbers across A1, B4 and C4 come from vendor blogs, are retained as directional, and are barred from setting a gate. Thresholds come from measured run data. Second, **a lapsed recheck-by date is an operational event, not a documentation chore**: a model registry route or a vendor roster entry whose recheck lapses drops to degraded and stops being selected for spend (§5.2, §2.2).

The fifteen-odd claims below carry the most architectural weight, in the sense that if one turned out to be false a section of this plan would have to change rather than be edited. They are the first things a reviewer should sanity-check against the ledger's recheck-by dates.

| # | Load-bearing volatile fact | Owner | Recheck by | What breaks if it is wrong |
|---|---|---|---|---|
| 1 | EU AI Act Article 50 transparency obligations became binding 2026-08-02, no size exemption, fines up to €15M or 3% of turnover | C7 | 2026-10-01 | §4.4 and §14.6 — the burned-in disclosure would stop being the load-bearing control |
| 2 | Platforms re-encode nearly every upload and strip C2PA manifests in the process (characterised as effectively total removal) | C7, A4 | 2026-11-01 | §14.6 — metadata-based compliance would become viable and the render-time overlay could relax |
| 3 | The publishing bridge supports creating posts in draft state with no schedule date, persisting until a human acts — **documentation claim, unverified against a real account** | C1 (OP-2) | 2026-10-01 | §7.2 — rung 1 of the fallback ladder; rungs 2 and 3 exist because of this |
| 4 | The publishing bridge exposes no per-platform AI-disclosure fields | C1 | 2026-10-01 | §7.7 and §14.6 — the manual label acknowledgement could be automated |
| 5 | Notion hosted MCP tokens expire roughly every three hours; REST internal integration tokens are non-expiring and support full property filters | C1 | 2026-11-05 / 2026-12-01 | §6.2 — the entire access split, and the "unreleased offers are unspinnable" control |
| 6 | The media router deletes generated media after 14 days; result URLs expire sooner | A2 | 2026-11-06 | §5.5, §8.13 — mandatory immediate re-hosting and the expiry-ordered download queue |
| 7 | The media router documents no idempotency key, no client-reference field and no dedup semantics on task creation | A2 | 2026-11-06 | §8.5 — the write-ahead spend ledger exists precisely because there is no token to pass |
| 8 | The router's primary video route can silently substitute a backup model; substituted output cannot use the 1080p endpoint and is forced to 16:9 | A2 | 2026-10-06 | §5.6, §8.13 — requested-versus-delivered recording and post-completion licence snapshots |
| 9 | Router prices at the 2026-08-06 snapshot: workhorse video route ≈$0.30 per 8-second clip with audio, quality route ≈$1.25, everyday image route ≈$0.04 | A2 | 2026-09-06 | §4.6, §5.4 — every cost figure and the trial plan; the forecast reads the registry, not this table |
| 10 | One widely-used video model's API is scheduled for removal on 2026-09-24 | A2 | 2026-09-24 | §5.2 — the standing proof that no model may be hard-wired |
| 11 | The media router's own terms of service could not be retrieved; every legal path was blocked and no archive snapshot exists | C7 | manual pull before build sign-off | §5.6 — the "the router grants nothing" posture and the per-asset licence snapshot |
| 12 | The trend-intelligence vendor's own guide and pricing page contradict each other on whether full programmatic access is included at the purchased tier | B5 | trial, week 1–2 | §2.3 — the short-form trend axis; adoption is gated on exactly this |
| 13 | The ad-library source requires personal government-ID verification and issues 60-day tokens | B1 | 2026-11-01 | §2.3 — the ad-creative axis, and a silent cron breakage risk (W2-15) |
| 14 | Reddit is now sourced through its official Data API with a DataForSEO search-index fallback; the unauthenticated JSON endpoint is deprecated (W6-1) | B1, C7 | 2026-10-01 | §2.3, §2.5 — Reddit moved from configuration input to MCP-mediated collection |
| 15 | X's first-party read pricing became pay-per-use at $0.005/read on 2026-02-06 | B1 | 2026-11-01 | §2.3 and OD-7 — the cost of reopening X reads is a budget question, not a compliance one |
| 16 | Czech automatic speech recognition runs roughly 2–3× the English word error rate; dedicated Czech text-to-speech is production-grade | A4 | 2027-02-06 | §4.8, §6.8 — why captions come from the script and why recognition is a monitor, not a gate |
| 17 | All List B platforms count Unicode code points after normalisation, so one Czech diacritic letter costs one character everywhere | C2 | 2027-02-01 | §3.3 — the length validator, and the absence of a Czech-specific truncation defect |
| 18 | The AI Office's Code of Practice on Transparency of AI-Generated Content is voluntary but founds a presumption of conformity for signatories, and a standardised EU "AI" label icon plus modality-specific marking guidance is still being developed | C7 | **2026-09-01 (urgent)** | §4.4 and §14.6 — if the icon is standardised, it replaces the theme-level disclosure wording and the engine-level disclosure floor is re-expressed against it |
| 19 | No EU simplification or "omnibus" package affecting Article 50's timing is evidenced anywhere in the research pack; the only documented grace period runs to 2026-12-02 and applies to generative systems already on the market, not to a new one | C7 (evidence gap) | 2026-10-01 | Nothing — and that is the point. **Standing rule: no expected or announced postponement may relax the burned-in disclosure control before it is actually in force.** Relying on a delay that does not arrive is the only one-way error here |

### 0.4 Research index — the sixteen briefs behind this plan

| Brief | One line |
|---|---|
| **A1** `A1_viral_video_practices` | How high-performing short-form video is actually produced with AI in 2026 — hooks, pacing, captions, what reads as slop, quality rubrics, operator workflow, and the human-QA throughput reality. |
| **A2** `A2_video_providers` | The sole owner of provider and model facts: Kie.ai evaluated deeply, Higgsfield evaluated on paper, alternatives, verified prices, async semantics, retention, refusals, and the provider-contract design. |
| **A3** `A3_video_prompts_skills` | Durable prompt, skill and agent patterns for hooks, scripts, shot lists, on-screen text, negative prompts and brand locks — and the boundary between shared skills and theme overlays. |
| **A4** `A4_assembly_postproduction` | The unowned middle of the video pipeline: stitching, captions from the script, typography, ducking, loudness mastering, safe zones, end cards, provenance signing, and the carousel-to-reel recipe. |
| **B1** `B1_sources` | The List A source universe — per-source role, signal value, priority, cadence, failure modes, Czech-signal flags and day-1 access reality. |
| **B2** `B2_extraction_methods` | Per-source extraction mechanics: the method matrix, robots and terms surface, the do-not-scrape list, fallback ladders, unattended collection behaviour and raw-artifact storage. |
| **B3** `B3_ranking_scheduling` | Ranking design: sub-scores, negative brand-fit criteria, anti-forced-placement, per-language fit, unattended scheduling behaviour and calibration governance. |
| **B4** `B4_czech_b2b_market` | The Czech B2B market layer: where the ICP actually is, how Czech professionals react to AI-generated content, register norms, calques, structural tells and native CTA phrasing. |
| **B5** `B5_trend_intelligence_platforms` | The current state of TikTok, Instagram and YouTube as research surfaces, the trend-intelligence vendor market, and the build-versus-buy-on-top verdict. |
| **C1** `C1_notion_postiz_integration` | Tool-surface facts for the brand-truth reader and the publishing bridge: auth models, rate limits, what is actually retrievable, and the AI-label field gap. |
| **C2** `C2_platform_constraints_stack` | Hard per-destination constraints for List B — character counts, ratios, durations, link behaviour, label mechanics — plus stack verification and scheduler ergonomics. |
| **C3** `C3_cron_ops_state` | Unattended execution and the state substrate: run identity, idempotency, checkpointing, exit codes, secrets, retries, partial failure, budget caps and notifications. |
| **C4** `C4_operator_review_ux` | What a solo operator must see to decide quickly: digest anatomy, confidence-gated defaults, granular rejection, and the feedback loops that follow. |
| **C5** `C5_voice_models_judge` | Anti-slop voice control that survives production: the five-layer voice gate, judge calibration economics, per-language rubrics and text-model role separation. |
| **C6** `C6_brand_truth_design` | Brand-truth resolution and enforcement: the fact taxonomy, per-class precedence, confidence bands, the exact degrade trigger, claim checking, spoken claims and spin application. |
| **C7** `C7_legal_compliance` | The legal evidence pack: platform terms, scraping law, GDPR on research artifacts, EU AI Act Article 50, provenance survival, router rights and Czech consumer-protection exposure. |

Their reconciled picture — including the placeholder re-derivations, the resolved cross-brief conflicts, the canonical vocabulary and the consolidated fact ledger — is `docs/research/SYNTHESIS.md`. Where this plan and a single brief disagree, the plan carries the synthesis's resolution and says so inline.

---

## §1. Components, responsibilities, stack and orchestration

### 1.1 The shape of the system in one paragraph

The system is a **console application that runs one theme end to end and writes a reviewable folder**. It is not a service, not a web app, and not an agent that decides what to do next. It executes a fixed sequence of named stages; inside some of those stages it makes narrow, bounded calls to language models; between the stages it consults ledgers so that a crash, a budget cap or a provider outage leaves a resumable, auditable state rather than a mystery. Everything expensive — paid media generation, anything that touches a live social account — sits behind a gate that can only be passed deliberately.

### 1.2 Major components and their single-sentence responsibilities

Component names are derived from the canonical stage and role names in `SYNTHESIS.md` §4; no new nouns are coined for stages, artifacts, gates, ledgers, config blocks or provider roles.

| Component | Single-sentence responsibility |
|---|---|
| **Run controller** | Executes the fixed stage sequence for one run, owns run identity and checkpointing, enforces stage boundaries and gates, and decides the exit-code class. |
| **Theme loader** | Performs the *theme load* stage: reads the theme's research block, spin block and output/runtime block plus the mode and secrets, non-interactively, and refuses to start on anything missing. |
| **Brand-truth resolver** | Performs *brand-truth resolution*: reads the brand-truth reader (Notion REST for records, Notion MCP for interactive browsing), verifies commercially binding facts against the live public site, applies precedence and conflict rules, and emits the brand-truth snapshot with its confidence band. |
| **Collection layer** | Performs *collection*: runs each configured source through its declared extraction method via one of exactly two connector classes — collector, MCP source — under per-source budgets and fallback ladders. The **curated inbox ceased to be a connector class** when operator-fed inputs were reclassified as configuration (W7-1). |
| **Research artifact store** | Holds the request log, short-lived raw payloads, normalised signal records and permanent provenance snapshots, with targeted deletion by canonical key available from day one. |
| **Ranking engine** | Performs *ranking*: turns signals into topic candidates with inspectable scorecards, applies the fit gate per language, and hands ranked topics forward. |
| **Dedupe index** | Remembers topic cluster keys, first-seen and last-seen dates, trajectory samples and prior-pack state across a rolling lookback so yesterday's topic does not reappear as today's discovery. |
| **Spin mapper** | Performs *spin*: looks up the configured pain-to-offer relation, sets the mapping distance, selects the CTA class and produces the spin brief and per-asset spin rationale. |
| **Copy generator** | Performs *copy generation*: produces text assets per destination per language using the drafting model, the brand lock, the theme overlay and the language overlay. |
| **Gate stack** | The ordered, per-asset enforcement chain: spin gate → claim gate pass 1 → voice gate → claim gate pass 2 → platform gate; each gate has its own repair path and none may be skipped. |
| **Media planner** | Performs *media planning*: produces shot lists, slide lists, keyframe specifications and prompts for every planned asset slot, always, at zero cost. |
| **Media router** | Resolves the routing-contract axes against the model registry to an eligible route, enforces the cost gate before submission, submits and polls, and records requested-versus-delivered route facts. |
| **Model registry** | One record per route: capability flags, price snapshot, license class, person-policy class, sunset date, prompt-pattern version, last-verified and recheck-by dates, status and accumulated refusal statistics. |
| **Assembly engine** | Performs *assembly*: stitches clips or slides, burns captions composed from the authored script, mixes and ducks audio, normalises loudness, enforces safe zones, applies the AI-disclosure overlay and the end card, exports the master and its derivatives, and signs the C2PA manifest after final encode. |
| **Packaging component** | Performs *packaging*: assembles the run pack and writes the run digest as a static file in the run folder. |
| **Ledger set** | Run ledger, spend ledger, media-job ledger, dedupe index, review-decision store, brand-truth snapshot store — the structured, queryable memory of the system. |
| **Notification component** | Writes the filesystem status flag and sends the configured push message; a delivery failure never changes the run's own exit class. |
| **Publish gate and distribution prep** | The single fail-closed enforcement point reading mode × publish allowlist × approval, followed by draft creation in the publishing bridge and blog preparation. *(Detailed in §7 and §11; named here only so the component map is complete.)* |

### 1.3 Component diagram

    THEME CONFIG                 SECRETS
    (research / spin /           (permission-restricted,
     output-runtime blocks)       never in prompts or logs)
         |                            |
         v                            v
    +---------------------------------------------------+
    |                 RUN CONTROLLER                    |
    |  fixed stage sequence · run identity · gates      |
    |  checkpoints · exit-code class                    |
    +---------------------------------------------------+
      |        |         |          |         |        |
      v        |         |          |         |        |
    THEME      |         |          |         |        |
    LOADER     v         |          |         |        |
          BRAND-TRUTH    |          |         |        |
          RESOLVER       |          |         |        |
          |  Notion REST (records)  |         |        |
          |  Notion MCP (browsing)  |         |        |
          |  site verification      |         |        |
          |  human run overrides    |         |        |
          v                         |         |        |
     [brand-truth gate] ------------+         |        |
          |                                   |        |
          v                                   |        |
    COLLECTION LAYER                          |        |
      collectors | MCP sources                |        |
          |                                   |        |
          v                                   |        |
    RESEARCH ARTIFACT STORE                   |        |
          |                                   |        |
          v                                   |        |
    RANKING ENGINE ---- dedupe index          |        |
          |                                   |        |
     [fit gate]                               |        |
          |                                   |        |
          v                                   |        |
    SPIN MAPPER                               |        |
          |                                   |        |
          v                                   |        |
    COPY GENERATOR --> GATE STACK             |        |
      (drafting model)   spin -> claim1 ->    |        |
                         voice -> claim2 ->   |        |
                         platform             |        |
          |                                   |        |
          v                                   v        |
    MEDIA PLANNER  ------------------> MEDIA ROUTER    |
      (always, $0)                     + model registry|
                                            |          |
                                       [cost gate]     |
                                            |          |
                                            v          |
                                       ASSEMBLY ENGINE |
                                            |          |
                                            v          v
                                       PACKAGING --> NOTIFICATION
                                            |
                                            v
                                    [human review gate]
                                            |
                                            v
                                      [publish gate]
                                            |
                                            v
                                   DISTRIBUTION PREP
                                   (publishing bridge, blog)

    LEDGER SET sits beside every stage: run ledger, spend ledger,
    media-job ledger, dedupe index, review-decision store,
    brand-truth snapshot store, claim ledger, model registry.

Two orderings in that diagram are load-bearing and were chosen deliberately. **Brand truth resolves before collection**, because the degrade decision changes what the rest of the run is allowed to do and a research-only run must not have paid for anything before discovering that (C6 §6.1). **Media planning happens whether or not any money is available**, because a plan-only run is a complete, useful run — the assignment states this as a courtesy rule, and A2's tiering shows it is actually the economic spine of the system.

### 1.4 Stack recommendation

**Recommended: Python**, confirmed by the operator at W2.5-5 and locked as D-11, distributed as a managed project checkout with locked dependencies and a thin per-OS launcher, running under the operator's own user account and never under a system account, with UTF-8 forced explicitly at every entry point.

The argument, per C2 §2.5 and §2.8:

- **Model-context-protocol and language-model client maturity is at parity** with Node/TypeScript — both ecosystems shipped official SDK betas in lockstep with the 2026-07-28 spec release (per C2 fact ledger) — and Python additionally has a first-party bridge that plugs MCP tools straight into its tool-runner, which is a concrete accelerator for a system whose brand-truth layer and two licensed data vendors all speak MCP.
- **The realistic Windows distribution story is better.** C2's honest finding is that a true single-file executable is impossible for this system in *either* language, because browser binaries always live outside it; given that, a managed project checkout with a locked dependency set and a modern environment manager is the cleanest path, and Python's is the more mature.
- **The research and ranking stages benefit from a stronger data ecosystem** — percentile normalisation within a source's own trailing distribution, corroboration counting across source families, and calibration reporting are all ordinary data work.
- **Nothing disqualifies it.** The only criterion where Node leads is that Playwright is natively at home there, and Playwright is barely present in this design at all (D-12).

Rejected alternatives, with reasons (C2 §2.8):

1. **Node/TypeScript end to end.** Rejected. Parity on the two things that matter (MCP, model SDKs), a worse Windows distribution story (the established single-binary packager is archived; the newer single-executable path still has asset and native-module friction), a thinner data-wrangling ecosystem for ranking, and no pull from the publishing bridge being a TypeScript product — we integrate over its REST surface, not in process.
2. **Single-file executable packaging** (either ecosystem). Rejected as the primary distribution mode: the "one file" promise is false here because browser binaries cannot live inside the executable; the bundles are large, cold-start slowly, and trip antivirus heuristics. Retained only as a possible later convenience for a browserless subset.
3. **A .NET console application.** Rejected. Best-in-class Windows scheduler ergonomics, but MCP tooling, model-ecosystem velocity and browser-automation bindings all trail, and it doubles the skill surface against every other AI tooling choice in the project.
4. **Containerised Linux-first runtime from day one.** Deferred rather than rejected — a cleaner scheduled-execution story, but it conflicts with the Windows-first operator reality locked in D-05. Revisit at the server-migration phase.

Cross-platform discipline is part of the stack decision, not an afterthought: absolute paths resolved from config, file logging as the only observability under a scheduler, explicit exit-code propagation from any launcher, and UTC-internal timestamps with a pinned run-date (W2-20).

### 1.5 Orchestration paradigm

**Recommended: a deterministic pipeline with narrow, bounded language-model nodes.** The stage sequence is ordinary control-flow code. Language models are called as leaf tasks with defined inputs and outputs — *score this candidate against the ICP map*, *write this caption*, *judge this draft against this rubric* — never as a planner that decides what happens next.

One bounded concession is permitted (C3 §2.1, option C): a small number of named nodes — topic ranking and copy drafting — may run a short internal self-critique iteration, provided the iteration cap is enforced by the pipeline rather than by the model's own judgment, the enclosing stage boundary and cost gate are unaffected, and the whole inner loop is logged as part of that one stage's record.

The argument, judged on the axes that actually matter for this product:

- **Cost is computable before the run starts** — *for both wallets, not only the media one.* Each stage has a fixed or capped number of model calls with per-call ceilings, so a hard upper bound exists in advance. That upper bound is only real if the ceilings are named, so they are: the **node inventory** below fixes the per-call ceiling and failure mode of every model node, and the **LLM budget block** at §5.4a fixes the per-run, per-stage and per-pack aggregates the cost gate enforces before each call. Against a $50 trial budget (D-04, OP-1) and W2-14's finding that one mis-configured run can consume a large share of it, that is not a nicety.
- **Budget enforcement is code, not model discretion.** The cost gate executes at a fixed stage boundary. In an agentic design, a budget check is a tool the model may choose to call, which is not enforcement.
- **Fail-closed points are guaranteed to execute.** Unattended safety (assignment constraint 15) requires that certain checks always run. A fixed graph guarantees it; an emergent one cannot.
- **A 3 a.m. failure has a name.** The artifact left behind is "stopped in *media generation*, after checkpoint N", with one bounded log to read — not an open-ended reasoning transcript.
- **Stages are testable in isolation** as near-pure functions with golden inputs, which is what makes the quality gates trustworthy over time.

Rejected alternatives (C3 §2.1):

1. **A fully agentic loop as the primary orchestrator** — an LLM choosing the next tool call at every step. Rejected: cost is emergent rather than bounded, so nothing structurally prevents token burn before a spend-gated step is ever reached; the same input can produce different call sequences run to run, which destroys testability; and there is no guaranteed halting shape for an unattended run.
2. **A hybrid in which a model-level planner may reorder, skip or add stages** (for example, deciding to skip collection and rank from cache). Rejected: it reintroduces unbounded control flow at coarser granularity. Stage sequencing, checkpointing, spend gating and exit-code determination must remain pipeline code.
3. **Multi-agent debate or critic-actor loops as the default per stage.** Rejected for v1 as a cost multiplier with unproven return at trial-budget scale, and independently discouraged by W2-10 (judge over-strictness cost spiral). Deferred to an explicitly opt-in quality mode with its own budget ceiling once the ledger infrastructure has proven itself.

**The node inventory — what "narrow" actually means here.** "Narrow, bounded language-model nodes" was asserted for a set that was never enumerated, which makes the cost-computability claim unfalsifiable. The complete v1 set is thirteen node classes. Every row states its bounded input, its bounded output shape, whether internal iteration is permitted, and what happens when the node cannot run — that last column being the one §11.3's fifth fail-closed trigger reads.

| # | Node class | Owning stage | Bounded input | Bounded output shape | Internal iteration | Behaviour when the node cannot run |
|---|---|---|---|---|---|---|
| N-1 | Brand-fit judgment (rules-second) | Ranking (§2.7) | One candidate's normalised record plus the ICP map excerpt | Sub-score, one-sentence falsifiable verdict, gate outcome | No | Candidate fails closed to monitor-only; never defaults open |
| N-2 | Resurgence "what changed since last time" | Ranking (§2.8a) | Prior-pack summary plus this run's new signals for one cluster key | New-angle verdict plus one sentence naming the change | No | Cluster is suppressed for this run and labelled "resurgence undetermined" |
| N-3 | Hook candidate generation | Video pipeline stage 2 (§4.2) | Angle, spin brief, language overlay, skill bundle | N hook strings, N fixed by the overgeneration knob | Yes (one bounded self-critique) | Slot degrades to plan-only with the angle attached |
| N-4 | Hook selection by rubric | Video pipeline stage 2 (§4.2) | The N hooks plus the rubric | One index plus one reason line | No | Deterministic fallback: first candidate that passes the lexicon screen |
| N-5 | Script writing | Video pipeline stage 3 (§4.2) | Selected hook, beat scaffold, claim-ledger-scoped facts | One script with beats labelled | Yes (one bounded self-critique) | Slot degrades to plan-only |
| N-6 | Shot-list / slide-list generation | Video pipeline stage 4 (§4.2) | The locked script plus recipe parameters | N rows, each a self-contained prompt with a keyframe reference | No | Slot degrades to plan-only |
| N-7 | Media prompt composition with route-policy injection | Media routing (§5.2) | One shot row plus the route's constraint layer | One prompt string plus a negative-prompt set | No | Route is not selected; slot degrades to plan-only (no unconstrained prompt is ever submitted) |
| N-8 | Spin gate angle-level pre-check | Spin gate (§14.1) | Spin brief plus S-1…S-7 | Per-criterion verdict plus evidence | No | Angle fails closed; asset degrades to the value-only variant |
| N-9 | Spin gate artifact-level post-check | Spin gate (§14.1) | Finished draft plus S-1…S-7 | Per-criterion verdict plus evidence | No | As N-8 |
| N-10 | Claim gate semantic pass (runs twice) | Claim gate (§14.3) | Extracted claim candidates plus ledger entries in scope | Per-candidate verdict from the five-verdict set | No | Deterministic verdicts only; every claim-shaped candidate blocked rather than passed |
| N-11 | Voice gate judge, per language | Voice gate (§14.2) | One artifact plus the language rubric | Per-dimension pass/fail, diagnosis, fix category | No | Artifact enters the pack labelled "voice gate could not run"; never a silent pass |
| N-12 | Corpus-leakage semantic comparison | Claim check class 11 (§6.11) | Generated spans plus corpus index hits | Overlap verdict plus leakage event record | No | Deterministic overlap only; ambiguous cases block |
| N-13 | Site-contradiction comparison | Brand-truth resolution (§6.6) | One configured verification page's text plus one Notion statement, **carried as quoted data, never as instructions** | Contradiction verdict for that one fact class | No | Records "not observed"; never "the site disagrees" (§6.4 asymmetry 3) |

Two consequences of writing this table down. First, **the "polish model" role named in earlier drafts owns no stage and is deleted** — the voice gate is judge-plus-regenerate, and the regenerate call reuses the drafting role. §10.4's model-selection knob therefore names two roles per language, drafting and judge, not three. Second, N-13 is a model node reading fetched third-party text, so it inherits §2.7's injection posture in full: quoted data, provenance-tagged, never instructions, with its own per-call token ceiling from §5.4a.

**Knobs this section contributes to §10.** Per-stage timeout; overall run wall-clock ceiling; the internal-iteration cap for the two nodes that are allowed one; model selection per role (drafting model, judge model) per language; per-node per-call token ceiling; stage enablement flags for partial runs (research-only, spin-only re-run, regenerate-media-only); the run-date timezone from which the pinned logical run-date is derived. *(Log verbosity and retention, launcher and interpreter path resolution, the low-disk threshold and the secrets location move to the **machine/runtime block** in §10.4a — they are properties of a machine, not of a tenant.)*

---

## §2. List A — research and extraction architecture

### 2.1 The honest starting point

The assignment's List A assumed a world that no longer exists. Two of its three primary social candidates cannot be read by software in 2026: X's free read tier is gone and D-08 (reaffirmed at W2.5-1) keeps the paid path closed, and Reddit has no legitimate automated route at this operator's scale (F-1, confirmed independently by B1 §3.1, B2 §2.2 and C7 §2.1). Meanwhile the assignment's bucketed "web AI/tech news" category contains the single best free API in this niche.

The resolved portfolio therefore rests on three connector classes rather than one, and on a principle B5 supplied that the assignment's framing does not contain: **build only what is free and officially open, buy on top exactly where platforms are closed, and where neither is possible, do without and say so in the pack** (per B5 §3.2, adopted as D-25).

### 2.2 The three connector classes

These are named separately because their failure modes, budgets and swap paths genuinely differ, and conflating them is how a credit exhaustion looks like an outage.

| Connector class | What it is | Budget unit | Characteristic failure | Swap path |
|---|---|---|---|---|
| **Collector** | Code we own calling a free official API or feed | Calls, quota units, wall-clock | Quota exhaustion, endpoint deprecation, feed 404 | Rewrite against a sibling endpoint; the source itself is free and not replaceable by a vendor |
| **MCP source** | A licensed vendor consumed over MCP with non-interactive bearer or credential auth | **Credits, metered like money** | Credit exhaustion, unpublished rate limits, vendor churn, plan-tier surprises | Named same-category fallback vendor, then a designed degraded state |
| **Curated inbox** | Operator-supplied items entered by hand | Operator minutes per week | The ritual is skipped and the loss is invisible | None — the axis degrades and the pack must say so |

The **vendor-swap requirement** is architectural, not aspirational (W2-16, evidenced twice: a named short-form trend tracker died mid-2026 and now redirects to its acquirer, per B5's ledger; and a major video model's API sunsets 2026-09-24 per A2's ledger). Every MCP source carries a vendor record with the same discipline as a model registry route — last-verified date, recheck-by date, status — and **a lapsed recheck-by drops the source to degraded, at which point it stops being selected for credit spend**. Every licensed source has a named fallback vendor and, behind that, a *designed* degraded state rather than a break.

The **curated inbox as a per-run input is retired** (W7-1, superseding D-09). Human-asserted evidence still exists — the operator configures theme-level watch topics, surface forms and excludes at setup time rather than supplying them per run. These configuration decisions are auditable and datable in `DECISION_LOG.md`, whereas per-run operator inputs were prone to silent lapse. The evidence class, retention rule and staleness logic that policed the original ritual (D-09) no longer apply, as there is no longer a weekly human input gate to fail.

**Every stated detection mechanism above detects the *absence* of data. One detects the presence of wrong data.** A circuit breaker trips on consecutive failures and a zero-signal run is itself an alarm — but a vendor serving yesterday's cached list under today's timestamp fails neither test, and the freshness scorer has no reason to discount it because the fetch really did happen today. Every MCP source and every ranked/presence-only collector therefore carries a **payload fingerprint**: a hash over the returned item set, compared against the last few pulls. An identical or near-identical payload across consecutive pulls is a **distinct degraded-source reason** — *stale payload suspected* — separate from and additional to the zero-signal alarm, and it suppresses that source's contribution to corroboration counting until it changes. This is cheap, deterministic and aimed at exactly the two sources the portfolio itself flags as least well-specified: the trend-intelligence vendor (W2-17) and the unspecced trending-topics endpoint in §2.3.

### 2.3 The resolved source portfolio

Signal-type legend: **VD** viral discourse · **IP** ICP pain · **LH** launch hype · **SD** search demand · **AC** ad-creative patterns · **FT** short-form format trends. Priority is re-ranked by *access reality*, not by signal value alone (per B1 §2.1) — a world-class source with no legal automated path cannot anchor an unattended pipeline.

| Source | Role / signal | Priority | Connector class | Cadence | Method | Characteristic failure mode |
|---|---|---|---|---|---|---|
| **Hacker News** | Dev discourse, launch hype, and (underrated) ICP pain in comment threads — VD, LH, IP | P0 anchor | Collector | Daily | Two official free APIs, no key; robots permits reads with a 30-second crawl delay (per B2 fact ledger) | English-only and dev-skewed; community ranking can be anti-commercial in tone; stories linger 24–48 h so cross-day dedupe is mandatory |
| **AI newsletters** | Pre-curated launch hype and tool discovery; a free human editorial relay that partly compensates for the X gap — LH, VD | P0 | Collector (email/feed ingest) | Daily | Feed where the platform provides one, otherwise email-to-inbox ingest | ~80% overlap between dailies on big news days, so ingest one or two not five (per B1 fact ledger); 12–36 h behind the original; sponsor placements must be filtered as non-signal |
| **Product Hunt** | Launch hype and competitor DNA in the AI and lead-gen tool space — LH | P0 | Collector | Daily to weekly | Public pages and feed as the floor; the GraphQL API only after the commercial-use question is answered (OD-19) | Launch-pod vote distortion is a *known structural* bias, handled as a standing discount on this source's virality band rather than per-item anomaly detection; loose category tagging |
| **Hugging Face** | Model and tool launches upstream of mainstream coverage — LH | P0 | Collector | Weekly | Official free Hub API with trending sorts | Research-crowd skew: trending here does not mean marketable; needs the brand-fit filter more than any other source |
| **Bluesky** | The only fully open real-time public social firehose in 2026; partial X substitute — VD, LH | P0 | Collector | Daily | Official protocol API, no fee, no app review; the trending-topics endpoint exists but is explicitly unspecced and unstable (per B1 fact ledger) | Much smaller than X, skews away from sales and outbound discourse; the trending endpoint can change without notice — treat as ranked-class evidence with a confidence ceiling |
| **Google News RSS** | Per-query tech-news monitor in both languages — LH, VD | P1 | Collector | Daily | Free per-query feeds, language-scoped by construction, Czech locale supported | Feed format quirks; clickbait density; presence-only evidence, no counts |
| **YouTube Data API** | Topic demand, packaging and title patterns, comment threads as a secondary pain vein — SD, IP, VD | P1 | Collector | Daily (cheap reads) / weekly (searches) | Official Data API; 10,000 free units per day, search costs 100 units per call, a country chart pull costs 1 (per B1 and B5 fact ledgers) | Quota exhaustion if search is used greedily — hence a declared sub-10%-of-quota daily budget; stored metrics carry a hard 30-day refresh-or-delete obligation that also bounds ranking baselines |
| **Meta Ad Library** | Competitor ad hooks, offers and creative patterns aimed at EU and Czech users — AC | P0 | Collector (auth-integration) after verification | Weekly | Official API through the operator's verified identity; public UI browsing by a human for creative inspection | **60-day token expiry silently breaking scheduled runs** (W2-15) — needs a token-expiry alarm with fail-closed behaviour and a named runbook item; personal government-ID verification gates the whole source and belongs in week-1 onboarding; the source is unavailable and its axis is absent until the credential is issued |
| **LinkedIn Ad Library** | B2B ad hooks and offers; reclassified as configuration input (W7-1) — AC is now **Meta-only** | P1, retired as run input | Configuration | — | Competitor naming and hook patterns folded into theme configuration at setup | No engagement metrics, no API, and no longer a per-run input; the ad-creative axis is now **Meta-only** per Spec 3 |
| **Google Trends** | Search-demand validation — reclassified as configuration input (W7-1); the demand axis **loses its fallback** and becomes single-vendor — SD | P1 automated only | MCP source (demand-data vendor) | Weekly | Demand-data vendor over MCP as the sole automated path (adopted at W2.5-3 as an explicitly logged vendor-risk decision); CSV export retired as fallback | The index is *relative, not absolute*, which misleads naive scoring — hence its role as a **demand modifier applied after ranking**, never a virality input; at weekly cadence it cannot participate in daily scoring at all; **no degraded state if vendor fails** — see `RISK_LOG.md` W7-01 |
| **Trend-intelligence vendor** | The short-form trend axis: TikTok, Reels and Shorts outliers, sounds and keyword-defined niche monitors — FT | P1, **trial-gated** | MCP source | Daily refresh, polled per run | Licensed vendor over MCP with bearer auth (W2.5-3) | **Adoption rests on an unresolved vendor-internal contradiction** about whether full API access is included at the purchased tier (W2-17) — the trial must answer it; async job semantics (auto-poll then a job id) and unpublished rate limits must be measured, not assumed; no evidence of Czech or regional filtering, so assume global-English |
| **Reddit** | Best-in-class ICP pain; reclassified as configuration input (W7-1) — IP, VD | P1, retired as run input | Configuration | — | Operator's manual notes from Reddit Pro for theme configuration, not per-run input | No longer a per-run data source; the loss of this input is mitigated by a configured staleness flag for the theme, but there is no per-pack label and no escalation, since no run blocks on it. **Separate open exposure: Reddit Pro is a different product from the ordinary-browser-session reading C7 assessed, with its own terms nobody has read** — a Phase-0 prerequisite (§17), on the same footing as the router's terms |
| **TikTok Creative Center** | Short-form format and hook inspiration only; reclassified as configuration input (W7-1) — FT | P1, retired as run input | Configuration | — | Format and hook inspiration folded into theme configuration at setup | **The trend axis loses its bottom rung.** If Virlo fails and Shortimize fails there is no degraded state, only absence — see `RISK_LOG.md` W7-01 |
| **LinkedIn organic** | B2B framing; reclassified as configuration input (W7-1) — VD | P2, retired as run input | Configuration | — | Framing input folded into theme configuration at setup | Holding a company page means scraping would be *the operator's own* contractual breach; minor loss as it was never load-bearing |
| **Free alert services** | Keyword alerts in both languages feeding the same ingest inbox as newsletters | P2 | Collector | Daily | Email, plus feed where still offered (one provider's feed delivery is no longer documented — verify at setup, OD-18) | Noise; duplicate coverage of the editorial-relay family |
| **GitHub trending, podcasts, review sites, Instagram, Threads, Discord/Slack** | Long-tail — LH, IP | P2 | Collector where open feed or official API exists; otherwise dropped | Weekly to quarterly | Public pages, open feeds, official APIs where they exist; community platforms are dropped (no longer available as manual input per W7-1) | Each is a nice-to-have; none is load-bearing. The Instagram official door can *validate* hashtags you already chose but can never *discover* what is trending (B5), so it is a v2 probe |
| **Czech-native venues** | Local discourse and localisation grounding | P1 for the Czech output set | Collector (feeds) | Daily to weekly | Public feeds from the Czech tech press only; Czech communities and meetups are reclassified as configuration input (W7-1) | Article feeds with no engagement APIs — Czech-by-construction language tagging, but no counted evidence anywhere (the direct cause of the Czech ranking re-derivation in §2.7); **Czech signal carriers drop from four to two** — see `RISK_LOG.md` W6-03a, which reopens the residual-risk acceptance |
| **X (Twitter)** | — | **Absent from v1** | — | — | Skipped for reads (D-08, reaffirmed W2.5-1) | The loss is earliest-hours virality, X-native format inspiration, and a slice of AI-sales practitioner discourse. At a human-gated daily-to-weekly cadence a 6–24 hour relay delay through the editorial-relay family is immaterial (B1 §3.2). Reopening is a budget decision with a measurable v2 trigger, not a compliance one |

**Two global sources now carry direct Czech-market signal** — the demand axis at Czech geography and Czech-locale news feeds — after the reclassification of both ad libraries to configuration inputs (W7-1); everything else discovers in English and is localised through Czech-native feeds only (B1 §4). **This reduction is load-bearing for §2.7's Czech ranking treatment and reopens the residual-risk acceptance at `RISK_LOG.md` W6-03a**: the asymmetry is the root cause of the Czech ranking treatment in §2.7 and is not a defect to be engineered around, but the narrowing of Czech signals is a real constraint the operator must accept actively rather than inherit silently.

### 2.4 Method policy: API, feed, licensed vendor, operator input — and where Playwright is not

The method vocabulary is fixed at seven values (B2 §2.2): official API · feed · licensed vendor · auth-integration · MCP wrapper · operator input · skip. Two rules govern it.

**Rule one — the transport does not launder the method.** An MCP wrapper is acceptable only when it fronts a legitimate method. A server that internally scrapes a closed surface inherits the full contractual and technical problem of scraping that surface. What makes the two licensed vendors in this portfolio acceptable is not that they speak MCP; it is that they sell *derived analytics under terms that permit pipeline use*, which is a materially different posture from raw scraped passthrough (B5 §3.5).

**That permission is an obligation to demonstrate, not a premise to assume.** The plan previously stated the vendors sell under permitting terms as though it were an established fact; nobody had read those terms. Each licensed vendor's own terms are therefore **retrieved manually, dated and read on one specific question — does this permit pipeline and derivative use, and further processing by the customer — before the first credit is spent**, with the answer recorded in the vendor roster beside last-verified and recheck-by. This is a Phase-0 deliverable on exactly the same footing as the manual pull of the media router's terms (§17), and it applies separately to the two vendors because they are not one legal class: one sells derived analytics whose **upstream is undisclosed** (carried as OD-17a), the other sells search-demand data whose **upstream is known, published and the subject of active litigation between the platform and vendors of that class** (OD-17b). Merging them into a single "derived-analytics" question would have answered the wrong one twice.

**Rule two — Playwright is in the stack and nowhere in the v1 collection path** (D-12, per B2 §2.1–2.4 and C7 §2.3). The assignment budgets a full guardrail treatment for browser automation; the honest answer after research is that browser automation is justified essentially nowhere here, because every major surface is either officially open (use the API), officially closed and technically defended (do not touch it), or reachable by plain feed where a browser adds nothing. Playwright therefore remains for exactly three purposes, none of which is collection:

1. A **per-source, explicitly-approved future exception mechanism** for a genuinely open site with no feed and no anti-bot defence, entering through the method-evaluation gate rather than by default. Because this is the only reversible point in an otherwise absolute posture, the exception has a named shape rather than being left to judgement: the **operator is the approver**, the assessment requires a dated reading of that source's terms, a dated reading of its robots file, and evidence that no anti-bot defence is present, and the grant is **recorded as a numbered decision in `DECISION_LOG.md`** naming the source, the date and the three findings. An exception that is not written down did not happen.
2. **Verification fetches against our own public pages** — the §6 site-verification path, where no third-party terms are in tension.
3. **Screenshot and render capture for QA**.

The guardrail mandate is satisfied not by scraping carefully but by publishing the do-not-scrape list, the method-evaluation gate, and an honest reason for each exclusion. This is a simplification, not a loss.

### 2.5 The do-not-scrape list

Binding in **every** mode, including degraded ones. No fallback rung ever descends into scraping; the ladder grammar is primary → degraded → operator-supplied → skip-with-log, and skip-with-log is a legitimate terminal state (B2 §2.4, §2.5; hardened by C7 §2.3).

1. Reddit — any surface, including mirrors and formerly-open JSON endpoints. Closed, defended, and the most litigation-active surface on the list.
2. X — any surface, including third-party mirrors. Its terms expressly prohibit scraping in any form without prior written consent (per C7 fact ledger).
3. LinkedIn — any surface, logged in or public, permanently. Its user agreement bars scripts and crawlers, its robots file blocks non-LinkedIn agents from the paths that matter, and enforcement visibly escalated through 2026 including a company-page removal and founder ban (per B1 and C7 fact ledgers).
4. Meta and Instagram web surfaces, **including the Ad Library UI** — use the API and human eyes. Meta's automated-collection terms define scraping broadly and separately ban circumvention.
5. TikTok, including the Creative Center.
6. Google search and Trends web surfaces.
7. Review platforms of the G2 class — the reviews are the vendor's licensed product.
8. Any login wall, anywhere — including cookie-lending schemes where the operator "just logs in for it".
9. Any surface serving an anti-bot challenge. A challenge is a "no": it is logged and skipped, never solved.
10. Paywalled article bodies, and any path a site's robots file disallows.

**Absence from this list is not permission.** New sources enter through the method-evaluation gate.

Two counterweights are recorded honestly rather than suppressed: US case law has held that scraping public data is not *per se* illegal (per B2's ledger), and that genuinely narrows one legal theory. It does not control here — the operator is EU-based, the contractual and platform-retaliation exposure is real, the operator's own Meta business accounts and LinkedIn company page are assets at risk, and technical blocking is decisive regardless of legality.

### 2.6 Raw-artifact storage and its GDPR consequence

The reason to store anything raw is that at review time the operator must be able to answer "where did this come from, and did we collect it legitimately?" without trusting the pipeline's own summary — and if a source ever disputes our access, the request log is the exhibit.

| Artifact | Stored? | Contents | Default retention |
|---|---|---|---|
| **Request log** | Always | Source, endpoint or feed, normalised parameters, timestamp, status, quota or credits spent, which ladder rung was used | 12 months — compliance memory, small |
| **Raw payload** | Briefly | The response body as received | 30 days, adopting the strictest per-source obligation (YouTube's 30-day refresh-or-delete rule) as the global default rather than special-casing it |
| **Normalised signal record** | Always | Canonical key, title and excerpt, metrics, **minimised or hashed** author handle, language, retrieval time | 90 days — long enough for velocity and for "which sources produced winners" analysis |
| **Provenance snapshot — durable part** | Always, permanent with the pack | Canonical key (the keyed hash), source name, domain, extraction method, retrieval time. **No verbatim text and no direct permalink to a user post** | Permanent with the run pack |
| **Provenance snapshot — verbatim part** | Always, alongside the durable part | The minimal quoted excerpt that triggered candidacy, and the canonical link to the individual post | **30 days**; on expiry it is replaced in the pack by the placeholder "excerpt expired — canonical key *K*" |
| **Full article bodies, media files** | **No** | — | Links and excerpts only — copyright posture of the press, and platform material stays on-platform by reference |

**Why the provenance snapshot is split, when it previously was not.** The earlier design retained the whole snapshot permanently on the reasoning that "it carries links and excerpts, not payloads, so pack retention does not fight source-data retention." **That reasoning is withdrawn: it is the wrong legal test.** Size is not the question. A verbatim excerpt of a public comment plus its canonical permalink is a direct pointer to an identifiable natural person, and it stays one on day 31 — so retaining it permanently in the pack silently nullified the 30-day window set three rows above it. The split above is the fix: the durable half carries everything auditability actually needs (which source, which method, when, and a stable key), and the verbatim half expires on the same clock as every other verbatim record. §12.2's per-signal "source links and extraction notes" are the same two-part record and expire the same way.

**The GDPR consequence is structural, not a footnote** (W2-06, per C7 §2.6). Public social content is personal data even when public: a persistent username plus post history generally identifies a natural person, and pseudonymous data remains personal data. The applicable lawful basis is legitimate interest, which requires a documented case-by-case assessment — blanket assessments are explicitly insufficient under the 2026 guidance C7 cites — plus a published privacy notice. Those are **company artefacts the architecture assumes exist and references; the software cannot generate them.** The Czech supervisory authority — **Úřad pro ochranu osobních údajů (ÚOOÚ)** — is quoted by C7 to the effect that public availability of data does not permit unlimited further processing. The published privacy notice must name ÚOOÚ as the supervisory authority, state the contact point, state the route by which a data subject exercises an objection or an erasure request, and state the right to lodge a complaint; naming the authority is not decoration, it is a mandatory content item the Phase-0 gate now checks (§17).

Seven design consequences follow, and each is cheap now and painful to retrofit:

- **Extract-first storage.** The durable record is the derived signal (topic label, source, timestamp, metrics), not the verbatim text plus username.
- **Bounded retention with an actual expiry job**, not a policy sentence — and the job reaches into packed, archived run packs, not only into the artifact store.
- **Author handles minimised, and where a stable key is needed for dedupe or anomaly detection, produced by a keyed, deterministic hash** — a message-authentication construction over the handle with the key held separately from the data and its deletion documented as a mitigation in its own right. Three things are stated explicitly because each has been assumed wrong elsewhere: a bare hash of a low-entropy public username is dictionary-reversible and is therefore not acceptable; the hash must be **deterministic** so that an objection naming a handle can be resolved by re-hashing it and deleting the matches; and a hashed record is **pseudonymised, not anonymised — it remains personal data** and stays inside every retention and deletion rule.
- **Targeted deletion by canonical key from day one**, so an objection or erasure request is executable — which argues against monolithic raw dumps and for structured, queryable extract records.
- **A run-pack → canonical-key index**, held in the same transactional substrate as the other ledgers (§8.6). Without it, targeted deletion stops at the artifact store and every archived pack becomes an unreachable copy of exactly the data an objection concerns. With it, "delete everything about this person" is a lookup, and Phase 1's acceptance criterion tests it against an already-packaged pack rather than only against a live record (§17).
- **A special-category exclusion, applied twice.** The binary veto list in §2.7 is a *brand-risk* filter and does nothing here: a community defined by a health condition, a political affiliation or a sexual orientation is not "high-severity controversy", yet an excerpt taken from it can carry an Article 9 special-category datum that legitimate interest alone cannot lawfully cover. So: **(a)** a source- and community-level deny-list, declared per theme and applied *before* collection, for any source or community whose defining characteristic is a special category; and **(b)** a deterministic lexical check over each stored excerpt *after* collection. Both fail to **do not store / delete**, never to "flag and continue" — flagging a record that should not exist is not a control.
- **A recipient map.** Collected text demonstrably leaves this system: it sits inside ranking, spin and copy prompts (§2.8), which means it reaches the text-model provider, and derived material reaches the media router, the text-to-speech provider and the licensed vendors. §2.6a names who receives what, in which role, under what agreement, and where.

### 2.6a Recipients, roles and transfers — an assessed gap, not an assessed compliance

*Stated as an obligation with a named owner rather than as a finding, because the research pack contains no evidence on this area at all: processing agreements, controller-versus-processor characterisation and third-country transfers are unaddressed in C7. This subsection defines the artefact and refers the substance to counsel (OD-26 and §16).*

For every external provider that can receive text or derived records originating in collection, the theme's spin block carries a recipient row naming: the provider and its role (**processor** acting on our instructions, or **independent controller**); whether a processing agreement exists and its date; whether the processing involves a transfer outside the European Economic Area and on what safeguard; and which categories of data can actually reach it. The providers in v1 scope are the text-model provider, the media router, the text-to-speech provider and each licensed MCP vendor. The published privacy notice's Article 13 obligations — categories of recipients, and transfer information with safeguards — are written *from* this map, which is why Phase 0 now gates on the notice's content rather than on its existence (§17).

One cheap technical mitigation reduces the surface before any of that is settled, and is adopted now: **author handles and direct permalinks are redacted from prompt payloads.** A prompt needs the topic, the excerpt and the source class; it does not need the username. What goes to a model is therefore the quoted excerpt with its canonical key, never the identifier.

### 2.7 Ranking architecture

Ranking turns signals into topic candidates with scorecards a human can audit. The design below is B3's, re-derived against B1's and B2's real per-source findings (D-22, `SYNTHESIS.md` §2a) — this is not B3 as written, and the differences matter.

**Four dimensions, combined multiplicatively.** Attention/virality × brand fit × freshness × a confidence-and-availability weight, each normalised to a common range. Multiplication rather than a weighted sum is the mathematical backbone of "weak brand fit → skip": in a sum, a very high virality number can outvote a very low fit number; in a product, a near-zero factor drags the whole result toward zero regardless of the others. This is the anti-forced-placement mechanism at the *ranking* layer; the mapping-distance rule in §6 is its counterpart at the *brand* layer, and both are needed.

**Three evidence classes replace one virality model.** The real day-1 roster does not split into "has counts" and "has none":

| Evidence class | Which sources | Virality treatment |
|---|---|---|
| **Counted** | Hacker News, Product Hunt, Hugging Face, Bluesky posts, YouTube | Percentile normalisation *within that source's own recent distribution* — never compared raw across sources |
| **Ranked / presence-only** | Bluesky trending topics, GitHub trending, Creative Center lists, newsletter inclusion, news-feed presence, the Trends index | A presence-or-rank proxy with a **hard confidence ceiling** — it can never reach the High evidence band |
| **Human-asserted** | Curated inbox in all its forms — Reddit threads, LinkedIn observations, community notes, ad-library findings, operator-seeded topics | Replaced by a coarse **operator salience** input, labelled distinctly and never rendered as measured virality |

**Corroboration counts across source families, not source instances.** The day-1 roster is heavily correlated: the developer-discourse sources, the launch registries and the editorial relay routinely cover the same launch within hours, and the newsletters exist precisely as a relay over the same discourse. Counting those as independent confirmations would inflate exactly the topics already over-covered. Corroboration is therefore counted across seven families — developer/technical discourse; launch registries; editorial relay; demand; ad creative; human-curated; video and packaging — and a newsletter relaying a Hacker News story is *the same event echoed*, not a second observation.

**Freshness decays by signal class, and one class runs backwards.** Five classes: spike, rising, launch-hype, **ad-creative-pattern**, evergreen-pain. The ad-creative class has an **inverted age term** — a still-running ad is a proven ad, so longevity is positive signal (B2 §2.8). Evergreen pain stretches to months and is governed in practice by "has this angle been covered recently", which makes it a dedupe question rather than a decay curve. And because X is absent and Reddit is weekly, the only sub-24-hour surface left is the Hacker News front page plus a thin slice of Bluesky: **spike-class signal is largely uncatchable, the pipeline's centre of gravity is launch-hype plus evergreen-pain, and a low spike yield is not a scoring defect.** Collection nonetheless runs daily on the automated core regardless of pack cadence, because that is the only way to catch what little spike-class signal exists.

**Baselines are bounded and the cold start has a date.** Normalised signal records live 90 days, and YouTube-derived metrics are capped at 30 by that platform's developer policy. So the maximum trailing baseline is 90 days generally and 30 for YouTube — and **for roughly the first two weeks of real operation there is no baseline at all.** Counted-class virality therefore runs in an absolute-band fallback with fixed per-source thresholds, explicitly labelled "no baseline yet", and switches to percentile mode once the window fills. This is a data-availability state, not a separate code path.

**Two independent gates run before the composite is computed** — this is the *fit gate*:

1. **A numeric floor on brand fit alone.** Directional starting default 0.35, which per the standing caution on statistics is a calibration starting point and not an empirical finding. The floor is on brand fit specifically, not on the composite, because a low composite could equally result from ordinary staleness — fixable by waiting — and collapsing the two would hide the difference from the operator.
2. **A binary veto list sitting outside any average**: legal and claim-risk topics, competitor disparagement, high-severity controversy, detected manipulation, **prompt-injection phrasing**, and **special-category source or content** (§2.6's Article 9 exclusion — a distinct class from controversy, with a distinct disposition: the item is not stored rather than merely not ranked). These are absolute stop conditions checked before scoring, so no virality number can outweigh them.

Seven negative brand-fit criteria are enumerated with a rules-first, LLM-second split (B3 §3): category mismatch, competitor saturation, tone and controversy risk, the "brand looks desperate" pattern, legal and claim risk, off-ICP audience mismatch, and stale consensus. Cheap deterministic rules run on every raw signal before any model cost is spent; model judgment runs only on survivors.

**The brand-fit judgment must produce a falsifiable verdict.** It is required to state the honest connection in one sentence or explicitly say it cannot — and if it cannot, the candidate fails regardless of every other dimension. Making the *attempt to connect honestly* the test itself is stronger than a separate "does this feel forced" checker that could disagree with the writer. **If the judgment step cannot run at all** — timeout, outage, budget cap hit mid-pass — the candidate fails closed to monitor-only. It never defaults open.

**Czech is ranked by a different formula, deliberately.** None of the four global carriers of Czech signal exposes per-item engagement, and the Czech-native venues are article feeds without engagement APIs. A Czech candidate can therefore essentially never earn a measured virality band. Keeping virality as a multiplicative factor would drive every Czech candidate toward zero and **the Czech output set would die quietly by arithmetic — a silent violation of D-02 that would look like a scoring detail rather than a policy failure** (W2-07).

**The two composites, stated once and exactly. This is the single definition; Appendix A.3 and every other reference read from here.**

- **English (and any language with counted-evidence sources):** composite = *attention/virality × brand fit × freshness × confidence-and-availability*. The **demand modifier is applied after the composite**, multiplying the finished figure — never inside it, because the search-demand index is relative rather than absolute and folding a relative number into a product of normalised ones misstates what it measures.
- **Czech (and any language with no counted-evidence source):** composite = *brand fit × freshness × confidence-and-availability*, with **virality omitted rather than proxied**. The **demand modifier is applied after the composite**, exactly as for English.

**Exactly one factor is dropped for Czech, and confidence-and-availability is not it.** That factor survives precisely because it is the one carrying the honesty: it records how many source families corroborated the candidate and how much of the portfolio was reachable this run, which is what makes "under-evidenced ≠ poor fit" a measured statement rather than a slogan. Dropping it would silently equate *thin evidence* with *good fit*, which is the opposite of the intent. Every Czech candidate additionally carries the honest label that its discourse evidence was observed in English with local demand and ad signal only, and because the two composites have different factor counts **the two numbers are not comparable and the digest says so beside them**.

**A per-language evidence-and-volume floor, so thinness is a named pattern rather than weekly decision fatigue.** Theme-readiness validation asserts that each configured language produces a non-empty candidate set — necessary, but it runs at theme-load time, and "non-empty" is a very low bar. A language can therefore pass validation forever while producing one weak candidate a week: technically valid, commercially anemic, and invisible because nothing ever fails. So each configured language additionally carries a **minimum evidence-and-volume band** — a floor on the number of candidates clearing the fit gate and on the number of corroborating source families behind them, evaluated **at every run**, not only at theme load. The default is deliberately **loose**, because a tight default would fire constantly during cold start and train the operator to ignore it. Breaching the band never blocks a run and never relaxes a threshold to manufacture volume: it raises a named digest line — *"the Czech candidate set has been below its evidence floor for N consecutive runs"* — and, on repetition, escalates under the same anti-flap rule as every other degrade (§8.12). The weekly curated-inbox session that might have remedied thin Czech evidence has been abolished as a per-run input (W7-1); the alarm now fires without a designed remedy. See `RISK_LOG.md` **W6-03a**, which reopens the residual-risk acceptance.

**Every candidate carries an inspectable scorecard** readable without statistics literacy (RA-2): sub-scores in both numeric and plain-band form, one sentence of rationale per dimension, the sources that fed it and how many families corroborated it, the evidence-quality label, the signal class and age, the gate status with the *specific* skip reason, the per-language outcome (generate / skip / hold, each with its own rationale), and the ranking-config version that produced it. Thresholds are versioned and dated. **Any proposed loosening of the brand-fit floor requires a logged human rationale** (OD-20 recommendation) — a governance rule that exists precisely to block the failure mode where thresholds quietly relax over months to hit a volume target.

**A run producing zero passing candidates is correct behaviour**, shown to the operator rather than hidden, and thresholds are never relaxed to manufacture volume.

### 2.8 Collection and ranking flow

    per-source declared budget (calls / units / credits / wall-clock)
              |
              v
    +-------------------------------------------------------+
    |  COLLECTION LAYER — per source, per ladder rung        |
    |    primary -> degraded -> operator-supplied -> skip    |
    |    (no rung ever descends into scraping)               |
    |  conditional requests · cache-before-call on paid      |
    |  cursor pagination · snapshot-then-detail              |
    |  per-source circuit breaker                            |
    |  global wall-clock ceiling (ranking always runs)       |
    +-------------------------------------------------------+
              |
              v
    signals --> canonical key (platform id, else canonical URL)
              --> near-dup fingerprint
              --> language stamped at SOURCE level first,
                  per-item detection only on mixed feeds
              --> quoted-data wrapper + provenance tag
                  (ALL collected text is adversarial input)
              |
              v
    +-------------------------------------------------------+
    |  RANKING ENGINE                                       |
    |   evidence class -> virality treatment                |
    |   corroboration across SOURCE FAMILIES                |
    |   freshness by SIGNAL CLASS (ad-creative inverted)    |
    |   demand modifier applied AFTER the composite         |
    |                                                       |
    |   [fit gate]  = brand-fit floor  +  binary veto list  |
    |                 (both BEFORE the composite)           |
    |                                                       |
    |   composite = virality x confidence x freshness x fit |
    |   cs composite drops virality entirely                |
    +-------------------------------------------------------+
              |
              v
    scorecards -> ranked topics (per language: generate / skip / hold)
              -> dedupe index consulted (trajectory x prior-pack state)
              -> top-N cap applied AFTER filtering, never by lowering
                 the threshold to fill a quota

Two run-scoped mechanics sit underneath this flow and are owned elsewhere so they are stated once: **within-run idempotency** — how a retry recognises captures already made for this run-date and skips or deltas rather than re-hitting a rate-limited source — is §8.5, and it is deliberately a different mechanism from the cross-day **dedupe index** described above; and the substrate that holds the request log, the raw payloads, the normalised records and the provenance snapshots is §8.6.

**Prompt injection is handled as a first-class hazard, not a curiosity** (W2-19). All collected text will later sit inside ranking, spin and copy prompts. It is carried as quoted data with provenance tags and never as instructions; the instruction layer stays structurally separate and privileged; and injection-style phrasing in a source item is itself a veto signal rather than something to pass through.

### 2.8a Cross-day dedupe: the resurgence-versus-suppression rule

*This is control flow, not a figure, and it was the one rule the evidence base specified in full and the plan did not carry. It is stated here as canonical plan text (imported from B3 §6.2, re-derived against what this architecture can actually observe). §1.2's dedupe-index responsibility, §2.8's "dedupe index consulted (trajectory × prior-pack state)" and §12.1's "what changed since a prior appearance" all resolve to this subsection.*

Three inputs are tracked per **topic cluster key** across the rolling lookback window: **trajectory** (attention rising, flat or declining, sampled day over day from the same counted sources that feed the virality band — a cluster's trajectory is the direction of its corroborating signal count and its counted-evidence percentile, not a new measurement); **prior-pack state**; and **whether the underlying discourse has materially changed** — a new development, a new counter-take, or an identical rehash.

**Prior-pack state has three values, not four, and the difference from the source brief is deliberate.** B3's matrix distinguishes *drafted*, *approved* and *published*. This architecture can observe the first two — the review-decision store holds them (§11.4) — and **cannot observe the third**: the system never publishes, a human acts inside the publishing bridge, and outcome capture back into the system is an optional, off-by-default, manual operator input (§17 Phase 7). A rule that branched on *published* would branch on a value that is usually absent, so the granularity collapses to what is real: **never-generated · generated (drafted or approved) · rejected**. Nothing is lost that the system could have known.

| Trajectory | Prior-pack state | Outcome |
|---|---|---|
| Rising | Never generated | Normal candidate. Ordinary discovery lag, not a duplicate |
| Rising or sustained | Generated | **Resurgence candidate only if a genuinely new angle is detected.** If yes, it re-enters ranking tagged **"revisit: new angle"** with the change named in one sentence. If no, it is suppressed for this run — this is the "nothing to add" criterion |
| Declining | Never generated | Ranks normally; the freshness decay curve usually drops it below threshold without a special rule |
| Declining | Generated | **Suppressed permanently** for that cluster key — a duplicate with no new value |
| Any | Rejected by the operator | Suppressed for the configured **rejection-suppression window**, and re-enters before that window closes only if corroboration has grown by more than a configured number of source families since the rejected run. A reason-coded rejection is evidence, and re-offering the same topic next week ignores it |
| Any | Generated, **capped** (media not produced for budget reasons) | Not a resurgence question at all. The cluster is marked *already generated (capped)* and is **not re-spun from zero** by the next scheduled run; completion is the recovery path in §8.11, not a fresh candidacy |

**Who computes the new-angle verdict, and what it costs.** Node **N-2** in §1.5's inventory, running inside the ranking stage, on the bounded input of the prior pack's summary plus this run's new signals for that one cluster key. It is one call per resurgence candidate — never per signal — it draws on the same per-stage call ceiling as every other ranking node (§5.4a), and it is checkpointed with the ranking stage's own idempotency key (§8.5), so a retry does not re-buy the judgment. Its one-sentence output is what the digest prints as "what changed since a prior appearance" (§12.1): that line has a producer, a stage and a cost, and it appears on the candidate's scorecard as a named field. If N-2 cannot run, the cluster is suppressed and labelled *resurgence undetermined* — fail-closed, because the failure direction that matters here is shipping four near-identical packs, not missing one follow-up.

**What this answers.** The question "can the same topic trending four days running ever produce four near-identical packs?" now has a stated answer: **no.** Day 1 generates. Day 3 re-enters only with a named new angle and ships tagged as a revisit. Day 4 with nothing new is suppressed. And the opposite failure — blanket cross-day suppression silently killing legitimate follow-up coverage of a developing story — is equally excluded, because *rising plus a real new angle* is an explicit pass, not an accident.

**Knobs this section contributes to §10.** Watch topics, entities and excludes; the source roster with per-source priority, extraction method, cadence, evidence class and per-run budget; source-family membership; ladder-rung configuration per source; per-source circuit-breaker thresholds and the source-health flag escalation counts; the payload-fingerprint comparison depth and near-identity tolerance; the global collection wall-clock ceiling; conditional-request and cache TTL per signal class; dedupe lookback window and per-source overrides; **the rejection-suppression window and the corroboration-growth override that shortens it**; freshness half-life per signal class; the brand-fit floor; the veto list contents including the special-category deny-list; corroboration bonus magnitude; top-N cap per language; **the per-language minimum evidence-and-volume band and its consecutive-breach escalation count**; the monitor-only band boundary; the absolute-band fallback thresholds used before a baseline exists; retention windows for request log, raw payloads, normalised records and the provenance snapshot's verbatim half; author-handle keyed-hash policy and key location; MCP-source credit budget per month with a pacing rule; vendor roster with last-verified, recheck-by and **terms-read-on-pipeline-use** dates; ranking-config version; the demand-modifier weight.

---

## §3. List B — content architecture

### 3.1 The identical-mix rule and what it actually obliges

W2.5-4 is unambiguous: **both configured languages get the same destination × asset-type matrix.** Czech gets TikTok, Instagram Reels and YouTube Shorts in v1. D-02a — the synthesis's recommendation of per-language-appropriate mixes — is rejected and superseded. D-02 stays literal.

What survives from the research that recommended otherwise is the *evidence*, and it now binds differently. B4 found that entertainment-styled short-form carries perception risk with Czech B2B decision-makers, that no Czech B2B lead-generation player has built a credible short-form presence, and that Czech professionals flag AI-generated content immediately with measurable trust damage (per B4's fact ledger, with the vendor-blog statistics in that ledger explicitly barred from setting thresholds). The operator has decided to publish there anyway. The architecture's obligation is therefore not to argue but to **make Czech short-form not look cheap**, and to make that obligation checkable rather than aspirational.

Six concrete design commitments discharge it. They are referenced from §4, where the production recipes live.

1. **Recipe, not translation.** The Czech short-form default is the carousel-to-reel recipe (CS-B): our own slide typography with Ken Burns motion, Czech text-to-speech or subtitles plus a music bed, and **no generative video model in the loop at all**. Every pixel of text is ours, so diacritics are perfect by construction and the F-7 rendering risk disappears (A4 §2.2, §2.6).
2. **Framing, not mimicry.** Czech short-form is education-first with a problem-to-solution rhythm, not an entertainment hook transplanted from English. The hook is a direct statement of a problem or a specific observation — the Czech judge rubric's pass bar (D-26) — never a scene-setting throat-clear and never an English hook rhythm in Czech words. This commitment was previously asserted and never gated; it is now **hook-shape-and-framing, a named dimension of the Czech judge rubric** (§14.4), with its own pass bar and fail smell, so it is machine-checkable like the other four enforceable commitments rather than a sentence in a policy document.
3. **Register discipline.** Vykání by default in every public post and first-contact call to action, consistently within an asset; tykání only where the theme config declares a peer-community context (D-26 resolves B4's internal conflict this way).
4. **Understatement as a quality bar.** The Czech judge weights the human-voice dimension higher than the English judge. This asymmetry is empirical, not stylistic: B4's evidence is that Czech professionals detect and distrust AI-generated copy, so the cost of a slip is higher in that market.
5. **A destination-aware production floor.** A Czech asset bound for a short-form destination must clear the same assembly QA gates as the English one — loudness targets, safe-box composition, caption legibility, no model-rendered message-bearing text — *and* the Czech-specific ones: TTS prosody acceptance, glyph coverage verified for the bundled font, and no English audio anywhere (A1's suggested fallback of English audio with Czech subtitles is rejected as a direct D-02/F-7 violation).
6. **A measurable revisit trigger, held as a configured threshold rather than as an intention.** Because the operator overruled a research recommendation, the architecture records the disagreement and names what would settle it. The trigger is a **config knob with a named default — twenty published Czech short-form assets, with a twelve-week backstop, whichever comes first** — and it is a knob rather than a note precisely so that the review fires on a counter the system maintains rather than on the operator remembering. When it fires, the digest carries a **Czech short-form review line** built from three things the system already holds: the count of Czech short-form assets approved and marked published-by-hand, the **frequency distribution of reason-coded rejections** on Czech short-form assets versus English ones over the same window (the leading indicator, available from Phase 4 onward), and the operator's own recorded read of engagement quality (the lagging indicator, entering through the same optional outcome-capture path as everything else the system cannot observe, §17 Phase 7). The decision — keep, narrow or expand — remains the operator's; what is no longer optional is that it gets asked. The exact numbers stay open at OD-22 only in the sense that the operator may move them; the mechanism is not deferred.

   **What this honestly does not buy.** There is no engagement baseline and no statistical test here, because the system does not observe engagement and inventing a significance threshold over hand-entered numbers would be false rigour. The leading indicator is rejection-reason drift, which is real, machine-held and available weekly. Phase 4's acceptance criteria include Czech short-form runs specifically so that this distribution exists before production rather than after (§17).

**Cost consequence, stated honestly.** W2.5-4 accepted doubled media spend and OP-1 stands. The doubling A2 priced assumed both languages buying generative clips. Under the identical-mix rule with per-language recipes, the Czech lane buys slide art and voice rather than clips, so the *actual* pack cost lands below A2's $3.80 two-language standard figure when Czech runs CS-B, and at or near it when the operator promotes Czech to the generative-clip-plus-TTS recipe. The architecture does not hard-code either number: the forecast the operator sees before spend is computed from the model registry's price snapshots with the snapshot date displayed (§5.2, §5.4). **The consequence is worth stating plainly, because it is easy to misread: the research conclusion that "the Czech mix is cheaper, which softens OP-1" is now only *conditionally* true — true while Czech runs the CS-B recipe, false the moment Czech is promoted to generative clips.** §15 carries this as risk R-11.

### 3.2 The destination × asset-type matrix

Identical in both languages. "Config-gated" means the destination exists in the engine and is switched on per theme; a destination being switched on never implies it is in the publish allowlist, which is a separate, mode-scoped list read by the single publish gate (D-23).

| Destination | Asset types produced | v1 default | Language behaviour |
|---|---|---|---|
| **LinkedIn** | Long post; document carousel; native short video | On | Identical set per language; Czech copy from the Czech language overlay, never translated |
| **Instagram** | Carousel; Reel; caption | On | Identical set per language |
| **TikTok** | Short vertical video; photo slideshow; caption | On (**Czech included per W2.5-4**) | Identical set per language; Czech uses the CS-B recipe by default |
| **YouTube Shorts** | Short vertical video; title and description packaging | Config-gated, default off in v1 | Identical set per language |
| **Facebook** | Community-style post; Reel (all Facebook video publishes as Reels since mid-2025, per C2 fact ledger) | On | Identical set per language |
| **X** | Single post; thread | **Config-gated, default off in v1** | Assets can be *produced* at no marginal cost; X is a publish-side decision entirely independent of the closed read path (F-2), and until it is taken X is never a connected channel |
| **Blog / site article** | Long-form article with hero and supporting visuals | Config-gated, default off in v1; drafts only when enabled (OD-14 recommendation) | Per language, per domain; the site-first hold rule in §6 governs whether social atomisations may exist before the article does |

**Two visual master formats cover nearly all of it** (C2 §2.2): 1080×1350 in 4:5 for feed stills and carousels, and 1080×1920 in 9:16 for all vertical video, plus a 16:9 still format if and when X is enabled. Producing those two masters and deriving the rest by layered re-composition — not by cropping — is the whole visual production strategy.

**The slide-art aspect policy, stated because the re-composition claim depends on it.** Layered re-composition works for *overlays*, which we composite; it does not work for a generated raster background underneath. A 1080×1350 generated slide image cannot fill 1080×1920 without cropping (banned), crop-upscaling (the same thing), padding (never adopted) or outpainting (deferred as a cost-and-artifact risk). Since the carousel-to-reel recipe is the Czech workhorse and now serves three vertical destinations, the policy is the one that makes the reuse claim true rather than aspirational: **generated slide backgrounds are produced at 9:16, and the 4:5 carousel slide is derived downward by re-composition** into a template designed so its content area sits inside a crop-free 4:5 region of the vertical raster. One generation, two aspects, no crop — and the carousel-to-reel reel genuinely does reuse already-generated slide art rather than quietly needing a second set. §5.4a and Appendix A.6 cost the single 9:16 set, not two sets.

**Media-bearing assets are counted as masters, not as destination derivatives.** This resolves an ambiguity the synthesis left open: OD-8's recommendation of one to two media-bearing assets per language per run was written when the Czech set had fewer video destinations. Under the identical-mix rule, a single 9:16 master per language legitimately serves TikTok, Reels and Shorts through re-composition, so the cap counts *masters produced*, and the derivative count is unbounded because a derivative costs a re-render, not a generation. Video review remains the throughput bottleneck at 20–30 minutes of human QA per finished video (A1), and it is the master that gets reviewed.

**What counts as one master, exactly.** The cap counts **every media-bearing master, not video masters alone**: a 9:16 video master is one, and a 9:16 slide-art set for the carousel-to-reel recipe is one, because each is its own generation event with its own spend. Derivatives — the 4:5 carousel, the per-destination re-compositions — are free re-renders and count as nothing. A default of one to two masters per language per run therefore buys, in the ordinary case, one video master plus one slide-art set per language. **Its stark consequence is stated here rather than discovered later:** at three ranked topics per run and one to two masters per language, **one to two of the three ranked topics in a normal pack receive no rendered media at all** and ship as copy plus a complete plan-only video plan. That is a deliberate economic trade — human video QA at 20–30 minutes per finished video is the binding constraint, not topic supply — but it is a trade the operator should read at the point the caps are introduced, not infer from a thin pack.

### 3.3 Native adaptation rules per destination

These are the platform gate's inputs. All values are C2's verified 2026 figures; the platform gate is deterministic and refuses an asset that violates a hard constraint rather than truncating it silently.

| Destination | Text limits and visible window | Visual / duration | Link behaviour | Hashtag norm | AI-label mechanics |
|---|---|---|---|---|---|
| **LinkedIn** | Post 3,000 characters, ~210 desktop / ~140 mobile visible before the fold; highest median engagement 1,300–2,500; article body ~110,000 | Document carousel as PDF, up to 300 pages (target 5–15 slides), 1080×1350 recommended | Links allowed in posts; the "link in first comment" convention is contested in 2026 and is therefore a **per-theme style choice, not a hard rule** | 3–5 | No confirmed structured toggle; the 2026 authenticity policy expects **per-post** disclosure and explicitly treats a profile-level disclaimer as insufficient (per C7 fact ledger) |
| **Instagram** | Caption 2,200, ~125 visible before "more" — front-load | Carousel up to 20 slides, **the whole carousel locked to the first slide's ratio**; Reel up to 20 minutes but not recommended to non-followers beyond 3; 15–60 s target | **Caption links are not clickable** — a hard constraint; CTA templates must be link-in-bio shaped | 3–5 (hard max 30) | Publish-time UI toggle; the machine path is embedded provenance metadata, with no clearly documented organic API field as of August 2026 |
| **TikTok** | Caption 4,000; first line visible in feed; caption doubles as a search surface | 9:16 at 1080×1920; sweet spot 21–34 s; photo slideshow up to 35 images at ≤20 MB each | **Caption links are not clickable organically** — same link-in-bio consequence | 3–6, keyword-style | Mandatory self-disclosure for realistic AI content; settable by UI toggle, by a posting-API boolean, or automatically from provenance metadata read at upload |
| **YouTube Shorts** | Title 100 characters, only ~40 visible in the Shorts feed — target under 50; description 5,000 | 9:16, ≤3 minutes; 20–40 s target | Description links allowed; not clickable in Shorts overlay text | 1–3 | The Data API exposes a settable synthetic-media boolean; 2026 adds automatic detection with non-removable proactive labels |
| **Facebook** | Post 63,206 characters, collapses around 400; 40–80 characters is the community-post sweet spot | All video publishes as Reels; 9:16, 15–30 s target | Links auto-expand to a preview card; no counting quirk | 0–2 | Publish-time UI toggle plus metadata-driven auto-labelling; ads have a separate mandatory control relevant only to the later paid phase |
| **X** *(if enabled)* | 280 weighted characters free, 25,000 on the paid tier; **every URL costs a flat 23 characters**; weighted counting normalises first and counts Czech letters at weight 1 | 1200×675 for a single landscape still; video under 60 s organically | External links widely reported to depress organic reach; link-in-reply is the thread norm | 1–2 | No documented AI-label field |
| **Blog** | No hard limits; quality constraints only | Hero plus supporting diagrams | Native | — | No search-engine disclosure requirement. The text limb of the transparency obligation has a human-editorial-review carve-out; **our working assessment is that this workflow meets it, and the carve-out's scope is an open question for qualified counsel (OD-24)** — not a settled position. See the two-condition note below |

**Czech text counts one-for-one everywhere** (C2 §2.1). All List B platforms count Unicode code points after normalisation, not bytes, and Czech diacritic letters are single code points in the normalised form — including on X, whose weighted table places them at weight 1. So the length validator normalises first, counts code points, and applies weighting plus the fixed URL cost only where the platform demands it. This removes what would otherwise have been a persistent Czech-specific truncation defect.

**The human-editorial-review carve-out has two conditions, not one.** The first is that the text passed human review or editorial control, which this workflow satisfies and records. The second is that **a named natural or legal person holds editorial responsibility** — and a decision record that says only "approved, reason code X" does not evidence it. The review-decision store therefore carries, per decision, the **identity of the approving person** and a per-asset **editorial-responsibility-held-by** value (§11.4). With one operator this reads as formalism; in front of a supervisory authority it is the difference between a documented carve-out and an asserted one, and the moment a second operator or a second tenant exists it is the difference between knowing who approved something and guessing.

**One internal per-asset AI-content class drives every disclosure obligation** (C2 §2.3, U5). A single field — none, assisted, or realistic-synthetic — feeds the platform-native flag, the burned-in visible disclosure, and the provenance handling, instead of per-platform ad-hoc logic. This is cumulative with, not a substitute for, the render-time burned-in disclosure that D-19 makes the load-bearing control. And because the publishing bridge exposes no per-platform AI-label fields (W2-05), the platform-native layer is a **manual human action in v1**, carried as a per-asset "AI label required" flag, a pack checklist item, and a publish-gate refusal to mark ready without explicit acknowledgement.

**The AI-content class is derived by the engine, not configured by a theme.** This is a correction, and it matters more than its size suggests. The field that drives the single load-bearing compliance control was previously a per-theme knob with a default, which made a hard legal condition into a setting a theme author could edit — failing both of this plan's own placement rules (§10.1: engine-level if it would otherwise be changed in more than one theme at once; safe-by-default for anything that can relax a threshold).

- **Derivation, at engine level, from the generation record.** An asset is classed **realistic-synthetic if any of its visual, audio or motion components was rendered by a generative model** — a generated still, a generated clip, generated motion, **synthetic speech, or generated music**. The generation record already holds this: the media-job ledger names every route that rendered anything for that asset (§8.13), and the text-to-speech provider is a route in that ledger like any other.
- **Synthetic audio is inside the definition, explicitly.** The previous default read "realistic-synthetic for generated video and imagery", which omitted audio — and the omission landed precisely on **CS-B, the Czech default recipe**: our own typography, Czech text-to-speech, and no generative video model anywhere in the loop. Under the old wording the entire Czech output set could class as `assisted` or `none` and skip the burned-in disclosure, while Article 50(2) names synthetic audio as its own modality. A **TTS voice track alone makes an asset realistic-synthetic.**
- **Configuration may only tighten, never relax.** A theme may declare a stricter class than the engine derives; it can never declare a looser one. This is the same monotonic rule the hard-excludes list uses (§6.3), for the same reason: a control that any tenant can weaken is not a control.
- **Tested, not assumed.** Phase 3 carries an acceptance criterion for exactly the case that was broken: an asset whose only generated component is a TTS voice, with no generative video clip anywhere, carries the burned-in disclosure (§17).

**Paid-partnership and commercial-communication mechanics per destination**, kept beside the AI-label mechanics because they are the same shape of obligation and were previously mapped for only one of them. This matters wherever the relationship is not plain owned-brand publishing — the affiliate arrangement in the real strategy is the live case (check class 10, §6.7). LinkedIn, Instagram and Facebook each expose a branded-content or paid-partnership control set in their own publishing interface; TikTok exposes a branded-content toggle; the video platform exposes a paid-promotion declaration in its upload flow. Like the AI labels, **none of these is reachable through the publishing bridge**, so each is a manual action recorded on the same pack checklist, and the required disclosure wording itself comes from the statement catalogue in §6.7 rather than being improvised per post.

### 3.4 Per-language variant rules

**Czech is a first-class output set, never a translation pass** (D-02, F-7). Three architectural consequences run through every layer:

- **Facts are language-scoped.** Offer descriptions, capability statements, CTA phrasing and approved claim texts exist per language. A claim approved in English is *not* automatically approved in Czech, because translation changes claim strength — an English "helps you book more meetings" can land in Czech much closer to a guarantee (C6 §10).
- **Confidence is per (theme, language).** The English pack can proceed at full confidence while the Czech pack sits lower or is blocked, and that is normal rather than an error state (§6.5).
- **Voice is per language with its own overlay.** The language overlay is a *third* axis alongside engine and theme, so every future Czech-writing theme shares one Czech slop lexicon, one register norm set, one CTA phrase bank and one set of on-screen-text conventions rather than re-deriving them (A3 §2.3, D-26).

The Czech rubric is concrete, not a framework (D-26): a calque blocklist with named native alternatives, structural AI tells including the direct Czech analogue of "in today's fast-paced world", a **code-switching allowlist** that permits English tool, metric and category nouns as normal Czech tech register while blocking English-rooted verbs and abstract benefit nouns, an eleven-dimension judge rubric with vykání as the default register — **the eleven enumerated in full at §14.4 as five inherited, five Czech-specific and one Czech override** — and a Czech soft-CTA phrase bank mapped to CTA classes. That allowlist is the single rule that prevents both failure directions: missing real Czech slop, and false-flagging normal Czech technical speech.

Two things the Czech path needs before its first production run, named here as prerequisites rather than assumed: **a Czech structural-calibration corpus** (the sentence-length-variance band does not transfer from English because Czech sentences run longer by default) and **a Czech golden set for judge calibration**, whose negatives are best seeded from machine-translated English marketing copy — translationese being precisely the failure mode the rubric exists to catch.

### 3.5 Human review per asset type

Review effort is not uniform, and pretending it is produces a queue nobody drains. The mapping below is the design input for the review package; §12 owns the digest's presentation.

| Asset type | Review depth | What the human is actually deciding | Typical time |
|---|---|---|---|
| **Short post** (LinkedIn, Facebook, X) | Read-through | Voice, spin honesty, CTA correctness | ~1–2 minutes |
| **Caption** (Instagram, TikTok, Shorts) | Read-through plus link-shape check | Same, plus that a non-clickable-link platform got a link-in-bio-shaped CTA | ~1 minute |
| **Carousel / document carousel** | Slide-by-slide skim | On-image text legibility, claim safety on every slide (an on-image number escapes text-only reading), narrative arc, **burned-in disclosure present on the first and final slide** | ~3–5 minutes |
| **Feed still / hero and supporting visuals** | Look-and-read | On-image text legibility, claim safety on any on-image number, **burned-in disclosure present** | ~1 minute |
| **Keyframe (per master, spend authorisation)** | Look-and-read, one still | §4.2a rubric: brand/composition, no legible text, safe-box, person policy, motion plausibility | Same depth as a feed still, order of a minute |
| **Confirmation pass (per finished master, publish-readiness)** | Full playthrough, narrower than a cold review | Motion integrity, pacing and hook in the first three seconds, audio prosody and timing, caption sync at mobile scale, disclosure legibility in motion | **Not yet measured.** Necessarily shorter than a cold review because five rubric checks are pre-cleared and several more are machine-verified free at assembly; Phase 4 carries the criterion that replaces this with a real number |
| **Blog article** | Full read | Long-form carries more claims per asset and therefore requires the top confidence band; structure, E-E-A-T signals, internal linking, **burned-in disclosure present on every generated image in the article** | ~15–25 minutes |
| **Whole pack** | Digest scan | Which topics to keep, which to drop, and whether the run's cost forecast is acceptable | ~2 minutes to scan |

Rejection is granular and reason-coded at every level — reject the video and keep the copy, reject one topic and keep the rest, reject the pack with global feedback — because reason codes are also what makes ranking calibration trustworthy later, and because "the topic was wrong" must never be conflated with "I had enough content this week".

**Knobs this section contributes to §10.** The per-language destination × asset-type matrix; per-destination character, aspect, duration, slide-count and hashtag profiles; link policy per destination including the link-in-comment style choice; CTA placement convention per destination; **the per-asset AI-content-class tightening override** (the class itself is engine-derived and cannot be relaxed) and the AI-label-required flag; the paid-partnership mechanics checklist per destination; blog enablement and per-language, per-domain article routing; X destination enablement; slides-per-carousel and pages-per-document-carousel caps; per-language volume targets; **masters-per-language-per-run cap, counting all media-bearing masters**; review-depth profile per asset type; the Czech short-form production floor checklist; **the Czech short-form revisit trigger (asset count and week backstop)**; the language overlay pointer per language; **the minimum mapping distance permitted per destination**.

---

## §4. Viral video pipeline

### 4.1 What the pipeline is optimising for

Short-form video is the competitive minimum for B2B in 2026, not an experiment — but roughly a third of first-pass AI video output still shows obvious flaws, and the operator QA gate cannot be removed (A1, whose volume benchmarks come from vendor blogs and are therefore used directionally and never to set a threshold, per the standing caution in `SYNTHESIS.md` §6). The pipeline is therefore designed around three economic truths:

1. **Text is cheap per call and expensive in aggregate; images are cheap; clips are not.** This is a correction of an earlier formulation ("text is free") that was true of one call and false of a pack. One call costs a fraction of a cent, which is exactly why overgenerating three to five hook candidates with a selection rubric and two or three keyframe variants is right — but a two-language pack runs on the order of a hundred and thirty text artifacts, each passing five model-mediated evaluations on top of drafting, and C5 §6's own arithmetic puts a pack at roughly 140,000–150,000 tokens best case and 400,000–450,000 worst case *before* multiplying by the topics in a run. Aggregated across a month of scheduled runs that is the same order of magnitude as the media forecast. The design instruction that follows is unchanged for overgeneration and changed for governance: **overgenerate where the unit is a call, and budget where the unit is a run** (§5.4a). **Never overgenerate clips** (A3 R6 reconciled against A2's prices).
2. **The keyframe is the approval unit.** The brand-correctness decision is made on a ~$0.04 image before a ~$0.30 clip is bought. This is the single most important economic control in the system.
3. **Human video QA is the throughput bottleneck**, at 20–30 minutes per finished video — which is why the media-bearing cap per run is separate from, and much lower than, the topic cap (`SYNTHESIS.md` §3.10).

### 4.2 End-to-end stages

    RANKED TOPIC (with spin brief, mapping distance, CTA class)
            |
            v
    [1] IDEA / ANGLE
        one angle per asset slot; the spin gate has already
        established that this pairing is legitimate
            |
            v
    [2] HOOK CANDIDATES        <-- overgenerate 3-5, selection rubric
            |                      (cheap per call; the run-level
            |                       text budget is at 5.4a)
            v
    [3] SCRIPT  ---> claim gate pass 1
        beat scaffold: hook -> problem -> turn -> mechanism -> soft CTA
        DELIVERY-CHANNEL SLOT set here: model-native speech (en only)
        / TTS voice-over (either language) / silent with captions
        SCRIPT-LOCK: the script is the artefact of record
            |
            v
    [4] SHOT LIST  or  SLIDE LIST
        shot list = N independent, self-contained prompts, each row
                    naming which approved keyframe it animates
        slide list = per-slide headline + support line + visual concept
            |
            v
    [5] KEYFRAMES / SLIDE ART        <-- Tier 1 spend (~$0.04 each)
            |
            v
        [KEYFRAME ACCEPTANCE]  <-- the approval event that unlocks
            |                      clip spend. Rejected work costs
            |                      four cents, not thirty.
            v
    [6] === FORK: AUDIO SOURCING ONLY ===
        EN-A  generative clips + model-native English speech
        EN-B / CS-A  generative clips + TTS voice-over
        CS-B  slide-motion carousel-to-reel + Czech TTS or subtitles
              (the Czech default)
            |
            v
    [7] MEDIA GENERATION   ---> [cost gate] BEFORE submission
        async: submit -> poll -> completed-pending-download ->
               rehosted -> done
        a run may legitimately end here with jobs still pending
            |
            v
    [8] ASSEMBLY  (one shared engine, both languages)
        stitch / Ken Burns -> overlay text composed from verified
        strings -> captions from the script verbatim, alignment
        supplies timing only -> music bed ducked under voice ->
        loudness normalised -> safe box -> layered CTA + end card ->
        BURNED-IN AI DISCLOSURE -> export master -> sign C2PA
        AFTER final encode -> per-destination derivatives by
        layered re-composition, never cropping
            |
            v
    [9] ASSET QA RUBRIC (machine) + measured-loudness gate
            |
            v
    [10] PACKAGING -> [human review gate] -> publish-prep
         per-asset: AI-label-required flag, provenance record,
         platform-native label instructions

### 4.2a The keyframe-acceptance rubric

§4.1 calls the keyframe the single most important economic control in the system, and §10.4 lets an unattended run satisfy it "rubric-automatic within caps" — against a rubric that had no stated content. An unattended run was therefore auto-approving the four-cent decision that authorises the thirty-cent-to-$1.35 one using an unspecified test. The rubric is named here, with its checks, its thresholds and its failure disposition.

**What the rubric checks**, each item derived from a constraint that already exists elsewhere in this plan rather than invented here:

1. **Brand and composition lock** — palette, logo treatment and composition conform to the visual brand baseline (§6.3 F-M). This is the reason keyframe-first exists at all: it is the brand-correctness decision.
2. **No legible text anywhere in frame.** Model-rendered message-bearing text is banned in both languages (§4.4), so accidental legible glyphs — including the gibberish pseudo-text generative models produce — are a hard fail, not a blemish. This check is also what makes one keyframe serve both languages.
3. **Safe-box compatibility** — the subject and its headroom sit inside the ≈900×1400 universal safe box, so the derived re-compositions do not decapitate it.
4. **Person-policy compliance** — the frame conforms to the theme's person policy *before* an image-to-video submission burns a paid attempt on a refusal, and, per the v1 likeness ban (§5.3), contains no synthetic human presenter.
5. **Motion plausibility** — the composition can plausibly animate as the shot row describes, with no limb, hand or product geometry that the motion-draft tier is likely to warp.

**Thresholds per mode, and the failure disposition.** Items 2 and 4 are **binary and non-negotiable in every mode**: one legible glyph or one person-policy breach fails the keyframe outright, because both are compliance surfaces rather than quality ones. Items 1, 3 and 5 are scored, and the acceptance bar is a per-mode knob: **human judgment in interactive**, and a **rubric threshold in unattended** that a theme may raise and may not lower below the engine floor. On failure: regenerate **within the keyframe variant count already budgeted** — the point of overgenerating two or three variants is that a rejection is free-ish — and on exhaustion of the variants, **degrade that slot to plan-only** with the accepted-nothing reason attached. Clip spend is never unlocked by a slot that has no accepted keyframe.

**If the rubric itself cannot run** — model unavailable, timeout, budget ceiling reached mid-pass — the slot degrades to plan-only. It does not unlock clip spend. This is the same fail-closed shape as the brand-fit judgment (§2.7) and is registered as the fifth fail-closed trigger's application to this gate (§11.3).

**Ceiling on unattended auto-acceptance.** The masters-per-language-per-run cap (§3.2, §8.11) is the ceiling: rubric-auto-accepted keyframes can only ever unlock clip spend for as many masters as that cap allows, so no separate keyframe ceiling is introduced. Stated explicitly because "how many can it approve before someone notices" is the question the cap silently answers.

### 4.2b Keyframe-first approval: two moments, two different questions

The keyframe acceptance described above makes the keyframe a still reviewed against five checks. What it does not do is make the keyframe the thing the operator actually looks at in the digest, or say what happens to the finished video afterward. This subsection closes both gaps.

**Two moments, two different questions, neither substituting for the other.**

**Moment one — keyframe acceptance, which authorises SPEND.** The digest presents each generated keyframe as a still, at the same depth as §3.5's feed-still row (order of a minute). The operator sees exactly what §4.2a's rubric checks — brand and composition lock, no legible on-frame text, safe-box compatibility, person-policy compliance, motion plausibility judged from a still — and nothing else, because nothing else exists yet. Accepting authorises the paid clip generation for that slot (§4.6). It is recorded where the plan already records gate outcomes (§4.2a, §14.7), **not in the review-decision store**, because it is not a publish decision and must never be mistaken for one.

**Moment two — the confirmation pass, which authorises PUBLISH-READINESS.** Generation proceeds asynchronously (§4.7). The finished assembled master returns — same digest if assembly completes in-session, or a later digest carrying the pack-amendment line §4.7a already writes. The review is shorter than a cold playthrough because five rubric checks are already closed and several more are machine-reverified free at assembly: brand/composition, on-frame text, safe-box and person-policy were locked at keyframe acceptance; the post-assembly overlay claim pass, the loudness gate and the disclosure measurement run automatically. **What is left is precisely what a still cannot show:** motion integrity in the animated result, pacing and hook strength in the first three seconds at real playback speed, audio prosody and timing, caption legibility and sync at mobile scale, and whether the burned-in disclosure — already machine-verified for size and contrast — actually reads against a moving, cutting frame.

**The confirmation pass is the recorded decision.** It writes the review-decision store's entry (§11.4), keyed to the finished master's delivered bytes, and it is what the publish gate reads (§7.4). **Keyframe acceptance is never sufficient and never substitutes.** An asset with an accepted keyframe and no confirmation-pass decision has no recorded human-approval state, and the publish gate refuses it exactly as it refuses anything else lacking one — not a new rule, the existing rule applied to a two-moment flow.

State this as sharply as the finding demands: **keyframe acceptance authorises spend; the confirmation pass authorises publish-readiness. Different decisions, recorded differently, and only the second is what a recorded approval has always meant in this plan.** The claim-pass-2 discipline that the final gate runs on the exact bytes that ship (D-16, §14.3) is unweakened — the confirmation pass *is* that gate for media, running on the finished master, not on the keyframe that authorised its generation. **This must not weaken R10 finding F-2's rule that approval binds to final bytes.**

**Rejection disposition depends on what failed, and the split matters economically.** A defect in pacing, audio ducking, caption timing or disclosure legibility is an **assembly-level defect** — assembly is local and zero marginal cost — so the fix is a free re-run of assembly against the same keyframe and clip, not a paid regeneration. A defect in motion integrity the keyframe could not have shown (a limb or product warp appearing only once animated) is a **generation-level defect** and follows the existing segment-addressable immediate loop (§12.4): a named shot regenerates alone reusing the approved keyframe, counted against the QA-rejection cap (§4.9); an unlocalisable reason regenerates the whole master. Cap exhaustion reaches the existing terminal state — last version ships labelled "did not clear QA after N attempts", never force-shipped as publish-ready, never quietly dropped.

**Interaction with §4.7a.** The confirmation pass will often fall on a later run than the keyframe acceptance. Not a new seam — §4.7a already designed for it. **The amendment line the operator already reads is the confirmation pass's natural trigger**; no new plumbing, only the recognition that this line is a review moment and not merely a notice.

### 4.3 Keyframe-first, and what happens when a route is multi-shot

**Image-to-video from an approved keyframe is the default reel workflow** (A2 §2.5). It decouples the expensive spend from the brand-correctness decision, and it lets one approved composition serve both languages because the text is overlaid afterwards rather than baked in.

The shot list's anatomy changes accordingly (A3 R1): each row carries a **keyframe-reference slot** naming which approved still it animates, and the textual continuity anchor is demoted from primary control to a consistency *check*. This materially reduces the character-drift and colour-drift failures that A1 and A3 both identify as the most common multi-shot defect — the anchor is carried visually rather than by repeating a description and hoping.

The other generation modes map onto named slots rather than being ad-hoc: **first-and-last-frame** is the mechanism behind a match cut or a seamless loop; **reference-to-video** holds a product consistent across clips; plain text-to-video is permitted **at draft tier only**.

**Selecting a mode can fix the shot length, and that coupling is a registry constraint rather than a surprise.** On the v1 roster, reference-to-video is available only on the fast/lite route and is **fixed at eight seconds** (A2 fact ledger). So choosing reference mode for product consistency silently determines shot count against the 20–40 second target: three shots, not "however many the shot list wanted". The registry carries the mode→duration coupling as a capability constraint per route, the router surfaces it when it resolves the request, and the shot-list stage reads it — a plan that asks for four twelve-second reference shots is refused at planning time, at zero cost, rather than discovered at submission.

**Multi-shot-native generation is a hero-tier experiment, never the scheduled default** (A3 R2 and R8, resolving a genuine A1-versus-A2 conflict in A2's favour because A2 owns provider facts). In v1 exactly one registered route is multi-shot-capable, and it activates only on an explicit human promotion to hero tier. When it does, the shot-list skill switches output shape from N independent prompts to a single sequence brief, and the self-check moves from prompt time to review time — because the model, not the prompt author, is now holding continuity.

**One honest consequence of that, named so the operator is not surprised by it.** There is no cheap multi-shot preview route in the v1 registry, so the four-cent protection does not apply at hero tier: the human promoting to hero approves the most expensive spend in the system with the *least* information — no motion draft of the actual sequence, only keyframes and a brief. This is a real asymmetry, not a design oversight to be papered over, and it is one more reason hero promotion is human-only in every mode.

### 4.4 Assembly — where quality is actually won

Assembly is a **named pipeline stage owned locally** (D-24), with a local FFmpeg-core engine as the engine of record and a cloud assembly API behind an adapter seam as an optional substitute or contingency. The reasoning is not ideological: zero marginal cost per asset matches "runs every night", determinism matches fail-closed requirements, exit-code behaviour is identical on both target platforms, and no third-party outage sits on the nightly critical path (A4 §2.8). The one real cost is obtaining an FFmpeg binary, and the recommendation at OD-10 is a managed install of a pinned version per operating system with fonts bundled and codecs not — because *invoking* the binary as a separate process is low-risk while *distributing* it triggers obligations a solo operator does not need.

What assembly owns:

- **Captions come from the authored script, verbatim.** Speech recognition or forced alignment supplies **timing only**. This makes **displayed-text accuracy** 100% by construction in both languages — a claim about the caption text, and deliberately not a claim about whether the audio matches it — and reduces the Czech accuracy gap, measured at roughly two to three times the English word error rate (per A4's fact ledger), from a *content* problem to a *timing* problem.
- **Caption timing has three sources, and which one is available is a per-route fact rather than an assumption.** (i) **Text-to-speech-native timestamps**, which remove speech recognition from the caption path entirely — evidenced for the primary Czech voice provider specifically (A4 §2.3). (ii) **Forced alignment** against the rendered audio, used when the voice route returns no timestamps — and Czech is **not** among the default alignment languages of the standard alignment toolchain, so a Czech alignment model is a named dependency that must be sourced rather than assumed. (iii) **The slide-timing model**, for the subtitles-only variant, which has no audio at all and therefore no timestamps and no alignment target. Three consequences are stated rather than left implicit: the cost/fallback voice tier's Czech word-level timestamp support is an explicit question the OD-13 trial must answer (§16); if the answer is no, sourcing and pinning a Czech forced-alignment model becomes a Phase-0 deliverable (§17); and **word-level caption reveal is unavailable on the subtitles-only path** — the knob exists but that path times captions per slide, and asking for word-level reveal there is a configuration error caught at theme-readiness, not a silent downgrade.
- **On any recipe using model-native speech, a local adherence check runs per asset.** Script-lock's honest weakness is that adherence is a behaviour, not a guarantee: an English-speaking model may paraphrase or ad-lib. §6.8's argument for sampling rather than gating is sound about *claim safety* — rule 2 drains the audio of claim payload, so drift cannot fabricate anything that matters — but it is not an argument about *quality*, and captions aligned against divergent audio drift out of sync on the asset type that costs 20–30 minutes of human QA each. The assembly engine already invokes a binary that ships a **local speech-recognition filter**, so the check is free, local, deterministic and needs no network: compare the recognised audio against the authored script and fail the asset closed to the **QA-flag path** (§4.9) below a similarity threshold. Sampled recognition stays exactly what it was designed to be — a *provider-level* adherence alarm (§6.8, §14.5) — and this is a *per-asset quality* check sitting beside it, not a replacement for it. It does not apply to text-to-speech recipes, where the provider reads the verified string.
- **All message-bearing on-screen text, in both languages, is applied post-render** with bundled brand fonts verified for complete Czech glyph coverage. Generative models are never asked to render message-bearing copy; in-model text is permitted only as incidental English set dressing carrying no message. Word-by-word karaoke reveal requires the styled subtitle path burned through the appropriate renderer — plain subtitle formats cannot animate words. **This rule governs the registry, not the other way round:** the "text-capable image route" was originally justified on the grounds that half of all assets carry Czech on-image text and weaker models garble diacritics — a rationale this post-render policy deletes entirely. The route stays on the roster **re-justified on layout grounds only** — it composes cleaner negative space for a post-render overlay to sit in — and never on the grounds that it renders type. If it cannot be shown to earn its premium on layout during the Phase-3 bake-off, it leaves the v1 registry (§5.2).
- **Overlay composition is constrained, because composition creates juxtaposition.** All on-screen text is composed at assembly time, which is *after* claim gate pass 2 has closed on the packed text bytes — so for a video asset the claim-bearing surface is assembled after the final claim gate ran. "Composed from verified strings" is not by itself sufficient: a verified figure placed beside a verified label can assert something neither string asserts alone, which is exactly the "300% ROI graphic" case §6.7 names as the artefact type that escapes text-only checking. Two rules close it. **(a) Slot discipline:** overlay composition may only place pre-verified strings into pre-verified template slots, and a template declares which slot pairs may appear in the same frame — no ad-hoc cross-slot juxtaposition. **(b) A post-assembly overlay claim pass:** the deterministic claim classes re-run over the composed overlay string set for each asset, as an assembly QA item. Every overlay string is known text, so this is cheap and needs no model call. A failure blocks the asset from publish-ready and routes it to the QA-flag path with the offending slot pair named.
- **Audio mastering to −14 LUFS integrated with a −1.0 dBTP ceiling**, two-pass, with sidechain ducking of music under voice. The measured values are **logged per asset as a QA gate** and out-of-range assets fail closed. Mastering hot now backfires because all three short-form platforms turn loud masters down more than the loudness gap (A4 §2.4).
- **Music must be licensed** — a library subscription or a paid-plan AI music generator. Platform trending audio is prohibited for the master asset because it is either unlicensed for brand use or licensed only inside one platform, which is useless for a multi-platform master. Music routed through the media router's unofficial music route is forbidden for published assets (D-13).
- **One 1080×1920 master composed inside the ≈900×1400 universal safe box**, with derivatives produced by re-running the template at the target ratio — layered re-composition, not cropping. That single safe box lets one master serve TikTok, Reels and Shorts unchanged, which is exactly what the identical-mix rule needs.
- **A layered call to action**: a soft mid-video cue around seconds 10–20 plus a final 1.5–2.0 second dual-delivery close, spoken and on-screen — because end-card-only CTAs underperform through pre-end drop-off. A loop-friendly no-outro recipe is equally supported.
- **The burned-in, human-perceivable AI disclosure, applied at render time.** This is the load-bearing compliance control (D-19), not a courtesy: the transparency obligation has been binding since 2026-08-02 with no size exemption, and metadata-only compliance provably fails because platforms strip provenance manifests on re-encode. **An asset without the burned-in disclosure cannot be marked publish-ready.** The C2PA manifest is signed *after* the final encode and archived with the pack, and is never relied on as the compliance mechanism.
- **The disclosure has an engine-level floor that a theme may only tighten.** The plan previously fixed *that* a disclosure must be burned in and left *what it looks like* entirely to a per-theme knob — which permits a compliant-looking configuration that still fails the obligation, since the duty is to communicate clearly and distinguishably **at the latest at the time of first exposure**, and to meet accessibility requirements. Grey eight-point type on the end card in the final half-second satisfies the old wording and not the article. The floor, mandatory, non-relaxable, and measured rather than asserted: **visible from the first second** of the asset and held for at least a defined non-shortenable interval (or for the whole duration, which is the simplest compliant choice); **inside the universal safe box**, so no platform's own interface chrome can occlude it; a **minimum ratio of type height to frame height** and a **minimum contrast ratio** against whatever sits behind it; **in the language of the asset**, Czech on a Czech asset; and an **audible equivalent at the start of any asset whose carrying channel is audio** — a spoken or tonal disclosure, because a visual-only label does not reach a listener. Themes may make the wording longer, the interval longer, the type larger or the contrast higher; they may not go below the floor. Phase 3 tests it by measurement, in the same shape as the existing loudness gate: type-height ratio, contrast ratio and first-appearance timestamp are logged per asset and an out-of-range asset fails closed (§17).
- **Disclosure placement is also a fact that may change under our feet.** If the AI Office's transparency Code of Practice standardises an EU "AI" icon (§0.3 row 18), the icon replaces the theme-level wording and the floor is re-expressed against it. That is a dated recheck, not a redesign.

### 4.4a Static-asset composition — the same stage, without motion

Assembly as described above is a *video* stage: it stitches clips or slides, cuts captions, ducks audio, masters loudness and exports a master with derivatives. But §3.2 also produces assets with no motion at all — 4:5 feed stills, Instagram carousels, LinkedIn document carousels, and blog hero and supporting visuals — and those had no named step in which anything was burned in. §14.6 declares the disclosure "applied during assembly" for image and audio as well as video; this subsection is the stage that makes the declaration true.

**Static-asset composition** is a named stage of the assembly engine, symmetric with the video path and running the same ownership list minus the temporal items:

- generated raster background (or brand-designed background) plus **all message-bearing text applied post-render**, in bundled Czech-glyph-complete fonts, under the same slot discipline and the same post-composition overlay claim pass as §4.4;
- the **burned-in AI disclosure**, under the same engine-level floor — for a still, "visible from the first second" means simply *present and legible*; for a **multi-page asset it appears on the first page and on the final page**, because first exposure is the first slide and a reader who lands mid-carousel must still meet it;
- export of the master and its per-destination derivatives by layered re-composition, and **for the LinkedIn document carousel, composition of the multi-page document export itself** — an ownership gap the plan previously left unassigned: the document format is produced by the assembly engine, with the bundled-font requirement carrying over unchanged, because a document export that substitutes a system font is exactly how Czech glyphs go missing;
- **C2PA signed after the final export** and archived with the pack, never relied on.

The asset QA rubric runs over static assets too, with the motion items inapplicable and the legibility, safe-box, glyph-coverage and disclosure-measurement items unchanged.

### 4.5 Carousel-to-reel as a first-class recipe

The transform is mechanical and deterministic: roughly 2.5–4 seconds per slide with the hook slide held slightly longer, which puts 7–13 slides — a typical carousel — squarely in the 20–40 second target; slow Ken Burns motion so the frame is never static; and one transition style per template to avoid a slop look.

**The script is primary for this recipe too, and slide copy is derived from it.** The source brief describes narration as coming "from the slide copy", which would make slide copy the artefact of record and leave two candidate scripts in one pipeline — an ambiguity §6.8 rule 1 ("spoken content is generated only from claim-checked script text") cannot be enforced against. Resolved in favour of the shared spine: **stage 3's script is the artefact of record for every recipe**, script-lock applies unchanged, and the slide list at stage 4 is a *rendering* of the script into per-slide headline and support line. Narration is therefore a reading of the same claim-gated script the captions come from, not a second text with its own provenance. Practically this changes almost nothing about the output and removes the only place in the plan where two artefacts could each claim to be the script.

Four recipe parameters that were previously specified only to the depth of a paragraph, named because this is the Czech default and is now serving three vertical destinations:

- **Slide count is the carousel's own count**, 5–15 per the §10.4 cap, with the 7–13 band being where the timing lands inside the 20–40 second target; a 15-slide carousel is either paced faster or split, and the platform gate refuses the out-of-band combination rather than silently overrunning the duration limit.
- **Motion direction is consistent within a template.** One transition style is not enough on its own — alternating Ken Burns directions slide to slide is itself a recognised slop tell — so a template declares its direction pattern (for example, a single consistent drift with the hook slide held) and every slide obeys it.
- **The burned-in disclosure sits in the safe box on the first slide and the final slide**, composed *before* the headline and support line are laid out rather than squeezed in afterwards, so a slide already carrying two text layers does not push it outside the box (§4.4a).
- **The narration/subtitles fork is an audio-sourcing choice, not a content choice**: both variants render the same script, and the subtitles-only variant times captions from the slide-timing model with word-level reveal unavailable (§4.4).

It is a first-class recipe in the engine, not a fallback, for four reasons: it is **the safest Czech video format available** (our own typography, proper Czech text-to-speech or none, no generative video model in the loop, so neither the spoken-claim risk nor the diacritic risk applies); it is **the cheapest reel per asset** because it reuses already-generated slide art; it is **the Czech workhorse under the identical-mix rule**, which is what makes Czech short-form affordable at English volume; and it is **a legitimate English variant too**, particularly for education-first content where a generative clip adds cost without adding meaning.

### 4.6 The spend boundary

Four tiers, and money only moves up a tier through an approval event (A2 §2.10):

| Tier | What it buys | Role |
|---|---|---|
| **Plan-only ($0)** | Prompts, scripts, shot lists, slide lists, keyframe specifications | **Always produced**, even with no keys and no budget. The scheduled-run floor, and a complete useful run in its own right |
| **Draft** | Cheap keyframes; a low-cost motion preview route | Composition and motion validation, plus refusal-surface discovery, at pocket-change cost |
| **Standard** | The workhorse video route from approved keyframes; everyday image route with the text-capable image route for slides carrying type | The default production tier for scheduled runs |
| **Hero** | The quality video route, or the multi-shot route as an experiment | **Never auto-selected by an unattended run.** Requires explicit human promotion, with a per-run hero cap |

**Hero spend has its own cap dimension and does not compete inside the standard per-run cap.** Three quality clips for one language, with the reject factor A2 prices in, is roughly $5.63 — so a single hero promotion under a shared $6.00 illustrative per-run cap would consume nearly the whole run before a single image is bought, which models a configuration that cannot work. The **per-run hero cap is a separate dimension**, sized independently and consumed only by human-promoted hero work; the standard per-run cap governs everything else. Both are checked, and whichever binds first stops the submission.

**The cost gate runs before submission, never after.** It reads expected cost from the model registry's price snapshots and checks it against per-asset, per-run, per-day and per-month caps — **for text calls as well as media ones** (§5.4a). A check after submission is too late: the money is already committed. The forecast the operator sees in the digest is computed the same way, with the price-snapshot date displayed beside it, because provider prices moved twice during 2026 (A2) and a hard-coded forecast rots silently.

**The dry-run boundary** is precise: a dry run produces every plan-only artifact, resolves routes against the registry, computes and displays the full cost forecast, and **submits nothing**. Dry-run is a flag on media generation, not a mode — the modes are test, staging and live-prep, and confusing the two is how a "safe" run spends money.

**The one sentence that makes the interaction unambiguous: a mode never authorises spend on its own; the dry-run flag is what converts a forecast into a submission.** Test mode does not make a run free, and staging mode does not make it expensive. What decides whether money moves is the dry-run flag, whose *default per mode* is an engine-level setting (dry run on in test) that a theme may tighten and may not weaken (§10.4a, §11.1). A run in test mode with dry-run deliberately switched off spends real money against real caps — which is a legitimate thing to do while proving the media path, and is exactly what Appendix A walks — and the deliberateness is the point: it is a switch someone had to throw.

### 4.7 The asynchronous job model and its consequences

Renders take minutes, higher resolutions add more, and tasks can hang (A2 §2.6). Four consequences shape the pipeline rather than being handled as exceptions:

1. **A run may legitimately end with jobs still pending**, and that is a healthy outcome with its own exit-code class — *completed-with-pending-media*. It must not page a monitor nightly. What it must not do either is sit silently against a 14-day provider deletion clock: **every pending job carries a days-to-deletion countdown, printed in the digest and in the notification**, because both cadence knobs default off (W2.5-7) and a run that ends with pending media may not be followed by another run for weeks. For the same reason, **an interactive run also performs phase 0** — adopting pending jobs and draining the expiry-ordered download queue before anything new is submitted — so that opening the application at all is enough to rescue paid work, without waiting for a schedule that may never fire.
   *What actually completes a pending asset is designed rather than assumed — see §4.7a. Adoption as originally written stopped at re-hosting the file, which is not the same as finishing the asset that file belongs to.*
2. **The first phase of every run adopts pending tasks and drains the download queue, ordered by nearest expiry, before submitting anything new.** Provider media is deleted at 14 days and result URLs expire sooner, so **immediate re-hosting is mandatory** and provider URLs are never the artifact of record. A pack holding provider URLs silently rots before a human reviews it.
3. **Polling is the baseline, not callbacks.** A scheduled console process has no stable public endpoint; a callback receiver is an optional later optimisation.
4. **Submission paces itself well under the published rate ceiling**, because one two-language pack can submit roughly twenty jobs and trip the limit in a single burst.

### 4.7a Cross-run completion: assembly as a resumable unit of work, and pack amendment

*completed-with-pending-media* was declared a first-class healthy outcome, and adoption was designed only as far as *download and re-host*. Everything downstream of that was undesigned for the cross-run case, and the consequences were concrete: assembly consumes several media-job rows to produce one master, so nothing in the ledger set could hold "master M is waiting on clip 2 of 3"; packaging is idempotent on run id plus the set of included asset ids, so completing yesterday's clip changes that set and the adopting run must either mutate a prior run's pack (destroying the idempotency property) or write a new pack (orphaning review-decision rows keyed to the original run id); and the adopting run may be in a different mode, under a different day's caps, or be a collection-only run that is not permitted to spend at all. Three additions close the seam.

**1. Assembly is a resumable unit of work with its own ledger state.** The **assembly ledger** — a new record type in the ledger set (§8.6) — holds one row per (master × language), with states: **blocked-on-inputs → assembling → assembled → failed**. The row names the media-job rows it depends on, so the media-job ledger's transition to `done` on the last outstanding input is what moves the assembly row out of `blocked-on-inputs`, whether that happens inside the originating run or three runs later. Assembly's idempotency key is the ordered set of its input asset identities plus the assembly-template version, so re-entering it after a crash re-uses completed work and re-renders nothing that is already correct. Checkpoint granularity for assembly is therefore the master, not the clip — which is the natural unit, since a master either exists or does not.

**2. Assembly is not a spend-bearing stage, so an adopting run may always finish one.** Local assembly is zero marginal cost (§4.4), so completing a blocked master needs no cost-gate authorisation and no budget headroom — a collection-only run, or a run under a different day's caps, may still assemble. What an adopting run may **not** do is *generate* anything new for the pending master; if a constituent job resolves as failed rather than complete, the master's assembly row goes to `failed` and the slot follows the ordinary refusal disposition (§5.6) in a run that is permitted to spend. This is the rule that lets phase 0 be genuinely useful in every cadence.

**3. Pack amendment is explicit, and the originating pack owns the asset.** The adopting run **reopens and amends the originating run's pack**; it does not write the completed master into its own. Three things make that safe rather than a violation of packaging idempotency:

- Packaging's key becomes **run id + the set of included asset ids + the pack revision number**. An amendment increments the revision; the prior revision is retained, so the pack's history is legible and "the pack changed after I read it" is a visible fact rather than a mystery.
- The amendment writes an **amendment record** into the review-decision store against the original run id — what arrived, from which adopting run, when — so review decisions stay keyed to one run id and one asset id and are never split across two folders.
- **An amendment invalidates the approvals it supersedes, and only those.** The amended asset's prior approve decision and its AI-label acknowledgement are returned to unapproved against the new revision (§11.4); every other asset in the pack keeps its approval, because its bytes did not change. The amendment record carries both the arrival and the invalidation, so the review history reads as one sequence rather than as a decision and a mystery.

**What the operator sees.** The amended pack's digest gains, beside its existing *"amended on date"* line, a **re-approval required** line naming exactly which assets lost approval and why — *"English video master: master completed on <date> by run <id>; approval at revision 1 superseded"* — and those assets' rows return to the unapproved decision state while the rest of the table is untouched. The amendment also raises a notification through the ordinary channel (§8.12) rather than waiting to be discovered, **because the operator's last interactive session ended with them believing the pack was decided**, and a pack that silently un-decides itself is precisely the folder-changing-underneath-them failure this subsection was written to prevent.

**Why this is cheap rather than a re-review.** Re-approval is scoped to the changed asset, and the changed asset is a master the operator has *never seen* — so the work is a first review of one thing, not a second reading of a pack. The alternative designs are both worse in obvious ways. Fingerprinting the pack as a whole would invalidate sixty assets' approvals because one clip arrived, which forces a full re-read for a change the operator does not care about and which operators would defeat within a week by batch-approving on sight — converting a safety control into a rubber stamp, which is worse than not having it. Leaving the approval standing, the behaviour before this rule, prepares drafts for content nobody reviewed. **The asset-level fingerprint is the only one of the three that keeps the cost proportional to the change**, and the proportionality is what makes it survivable as a daily habit. The video master is also, not coincidentally, the asset class §17 sizes at 20–30 minutes of human QA — the single asset in the pack where "nobody looked" matters most and where a whole-pack invalidation would hurt most.

**Until the master is assembled, it is packaged honestly.** A topic pack whose video master is still waiting on inputs contains the **plan-only artifact with its completed clips attached** and a stated pending state with the days-to-deletion countdown — not a finished-looking master. This is the rule Appendix A now follows: a run cannot report a mastered, loudness-gated, disclosure-bearing, reviewed master while one of its constituent clips is still rendering.

### 4.8 The English/Czech fork — at audio sourcing, and nowhere else

    SHARED SPINE (both languages)
    topic -> angle -> hook candidates -> script (claim-gated)
      -> shot list or slide list -> keyframes or slides (approved)
                              |
                        === FORK ===
                              |
      visual source:  generative clips   OR   slide motion
      audio source:   model-native speech (EN ONLY)
                      OR TTS voice-over (either language)
                      OR no speech (music bed + burned-in captions)
                              |
                        === REJOIN ===
                              |
    SHARED ASSEMBLY ENGINE -> master + derivatives -> pack

**Three legal recipes in v1** (D-14): **EN-A**, generative clips plus model-native English speech; **EN-B / CS-A**, generative clips plus text-to-speech voice-over; and **CS-B**, the Czech default — slide motion plus Czech text-to-speech, or subtitles-only plus music.

**Banned in v1**, in any route: model-native Czech speech; model-rendered message-bearing text in either language; model-rendered Czech text of any kind; **any synthetically created or synthetically altered human presenter, and any cloned voice** (§5.3 — the *talking human* motion class is a disabled value in v1 and the voice-identity knob accepts licensed catalogue voices only).

**Six enforcement rules make the fork safe:**

1. **Script-lock.** Audio is a rendering of claim-gated script text. The script is the artefact of record.
2. **In unattended runs, spoken lines carry zero claim tokens** — no numbers, no currency, no entities beyond our own brands, no superlatives, no outcome statements. All claim payload lives in burned-in on-screen text composed at assembly time from verified strings, so model improvisation cannot fabricate anything that matters.
3. **Caption text always comes from the script verbatim**; alignment supplies timing only.
4. **Speech recognition is a sampled adherence monitor**, never a per-asset gate: its job is to measure whether the model said what it was told. A measured adherence drop is a provider-level alarm that disables audio for that route.
5. **Fail closed to subtitles.** If the Czech voice provider is unreachable or the voice is missing, degrade to subtitles-only plus music. Never fall back to model-native Czech speech, and **never fall back to English audio** — A1's suggested English-audio-with-Czech-subtitles fallback is rejected as a direct D-02 and F-7 violation (resolved in A4's favour in the consolidated ledger).
6. **Disclosure is triple**: burned-in visible label at render time (load-bearing), platform-native label flags set at publish-prep (manual in v1), and a signed provenance manifest archived with the pack and never relied on.

The pessimism about Czech voice and the optimism about it are both correct about different things (`SYNTHESIS.md` §3.12): the pessimism applies to **speech generated inside a video model**, which is English-first with unreliable non-English output; the optimism applies to **dedicated text-to-speech providers**, a different product category with genuine Czech production evidence. The design consequence is exactly this fork.

### 4.9 Human gates in the video pipeline

| May run unattended within caps | Must remain human |
|---|---|
| Topic research and ranking; hook, script and shot-list drafting; keyframe generation at draft tier; motion drafts; standard-tier clip generation from approved keyframes where the theme enables it; assembly; audio-QA flagging; packaging | Angle and script *approval* where the theme requires it; **any promotion to hero tier**; rejection retries beyond the bounded ladder; voice selection; final QA on every finished video; anything that touches a live account |

Refusals are normal outcomes, not errors (A2 §2.7): one automated sanitise-and-rewrite, one model swap to a registered alternate, then **degrade to plan-only** with the reason packaged for the human — capped at three paid attempts per asset slot, never a retry loop. Each rejection type has a named next step, and two of them are counter-intuitive enough to state explicitly: **text problems are never fixed by regenerating video with text**, and **audio problems are never fixed by switching to the other language**.

**The QA-flag path, and why it needed a ladder of its own.** The asset QA rubric is not a refusal, so the refusal ladder above does not apply to it: a limb-warp artifact, a failed adherence check or an out-of-tolerance disclosure measurement puts the asset **into the pack flagged for human decision** rather than triggering a silent retry. That was correct and incomplete — it left the only route back from a QA defect running through a human rejection, and the human-rejection regenerate loop (§12.4) had no cap, no downgrade rule and no terminal state. Every other gate in this document names a bounded ladder ending in a defined terminal state; this one did not, which meant a repeatedly-failing video could be regenerated an unbounded number of times, one rejection at a time, bounded only by the blunt dollar caps W2-10 already showed are insufficient for exactly this failure shape.

The **QA-rejection cap** closes it: a named, configurable ceiling on regenerations of one asset slot driven by QA flags or human rejection **within one pack** — default two — counted in the media-job ledger against the asset slot so it survives across sessions and across runs, not just within one sitting. On exhaustion the terminal state mirrors the voice gate's: **ship the last generated version into the pack labelled "did not clear QA after N attempts"**, with every attempt's artifact and reason attached, never force-shipped as publish-ready and never quietly dropped. The operator may still promote it by hand — a recorded decision, like every other — but the system stops paying for another attempt on its own.

**Regeneration budgets, named separately so they can never be confused.** Four distinct counters exist, and §12.4's "the same bounded regenerate cap as any other regenerate" was ambiguous about which it meant. They are: the **spin-regenerate allowance** (per artifact, one, then downgrade to value-only, §14.1); the **voice-regenerate cap** (per artifact, §14.2); the **claim-retry budget** (per pack, §6.7); and the **QA-rejection cap** (per asset slot per pack, here). They are **independent counters**, but they are all subordinate to one outer bound — the **per-artifact repair ceiling** in §14.0, which counts repairs across every gate — so exhausting a specific counter degrades that gate's path while exhausting the repair ceiling stops repair for that artifact entirely.

### 4.10 The prompt and skill layer

Stage 1 required prompt structures for hooks, scripts, shot lists, on-screen text, **negative prompts** and **brand locks**, plus reusable skill packs — and the plan referred to all of it (four "named skill bundles", four uses of "brand lock", one mention of negative prompting in an index line) without ever owning it. Dangling references to material that exists only in the evidence base are the same defect as a missing section. This subsection is that material's home in the architecture; the vocabulary is A3's and remains canonical.

**The brand lock** is the always-injected constraint block that every generative call carries, in both modalities, and it has two halves. The **visual half** comes from fact class F-M: palette, logo treatment and placement rules, on-image text rules, and the composition conventions the safe box implies. The **verbal half** comes from the theme's voice rules plus the language overlay: register, banned phrasing, the code-switching allowlist for Czech, CTA phrasing conventions. It is assembled once per (theme × language) at theme load and is versioned with the theme, so "which brand lock produced this" is answerable from the artifact's own version pinning (§14.7). It is the thing that makes one keyframe serve two languages: nothing language-specific is baked into the pixels.

**Negative prompting is five composable layers**, each configured at the level that owns it, so a theme author never re-types an engine constraint and an engine change never overwrites a theme's own list:

| # | Layer | Owns | Configured at |
|---|---|---|---|
| 1 | **Universal artefact suppression** | The failure modes every generative model shares — malformed hands and limbs, warped geometry, duplicated subjects, mangled pseudo-text | Engine |
| 2 | **Route-policy constraints** | What this specific route refuses or restricts — person policy, named-people refusal, trademark-in-input refusal | Engine, injected from the registry by node N-7 (§5.2) |
| 3 | **Compliance constraints** | The v1 likeness ban (no synthetic presenter, no cloned voice), no model-rendered message-bearing text, no third-party marks | Engine, non-relaxable |
| 4 | **Brand-negative constraints** | What this brand must never look like — off-palette treatments, competitor visual idioms, the stock-photo register the theme rejects | Theme (visual brand baseline) |
| 5 | **Slot-negative constraints** | What *this* shot or slide must avoid, derived from the shot row — usually the previous attempt's specific failure, which is what makes a bounded regenerate actionable | Per call, composed at prompt time |

Layers 1–3 are engine-level and may be tightened by a theme, never removed. Layer 5 is where a refusal-ladder rewrite or a QA-driven regeneration puts its correction, which is why "the regenerate instruction carries the named alternative rather than only *this failed*" is implementable rather than aspirational.

**Four reusable skill bundles**, named in full because three of them previously were not. A bundle is a prompt-pattern set plus its selection rubric plus its own QA emphases, selected per asset type rather than per theme:

1. **Short-form scripting** — hook candidates, the beat scaffold, shot lists, caption conventions. Used by every Reel, Short and vertical video.
2. **Carousel and document** — per-slide headline and support line, narrative arc across slides, on-image text density limits, first-and-last-slide conventions. Used by carousels, document carousels and, via §4.5, by carousel-to-reel.
3. **Ad creative** — the one bundle the plan already named. Carries a stricter claim-safety rubric and a mandatory human gate before any spend, and is dormant until the later paid phase (§5.8).
4. **Long-form article** — structure, section scaffolding, internal-linking conventions, the higher claim density that makes long-form require the FULL band.

Each bundle exists at **engine level** as the shared pattern set; a **theme overlay** may add or narrow patterns; and a **language overlay** supplies the language-specific conventions (§3.4). That three-axis placement is the same one the voice layer uses, deliberately, so there is one mental model rather than two.

**Knobs this section contributes to §10.** Recipe per language; audio policy per language; text-to-speech provider and **voice identity per language, restricted to licensed-catalogue voices**; caption style and whether word-level reveal is used, **with word-level reveal unavailable on the subtitles-only path**; caption timing source per language; music source and bed selection per theme; loudness targets and the QA tolerance band; safe-box dimensions; end-card recipe including the loop-friendly variant; shot count and clip length per asset type; hook overgeneration count; keyframe variant count; keyframe-acceptance policy (human versus rubric-automatic) per mode **and the unattended rubric threshold**; masters per language per run; the asset QA rubric thresholds; **the adherence-similarity threshold for model-native-speech recipes**; disclosure overlay text per language **above the engine floor** (wording, duration, type-height ratio, contrast, audible-equivalent text); slide timing range and motion-direction pattern for carousel-to-reel; per-destination derivative set; **the QA-rejection cap**; **negative-prompt layer 4 contents** (brand-negative) and **skill-bundle selection per asset type**.

---

## §5. Media provider architecture

### 5.1 Roles, and why they are roles rather than vendor names

| Role | Filled in v1 by | Status |
|---|---|---|
| **Text-model provider** | Chosen per role and per language at OD-5a; two roles only — **drafting** and **judge** — ideally from different model lineages to reduce shared blind spots | **The system's most frequent external dependency**, and previously the only one with no role at all. Treated exactly like the media router: replaceable, registry-backed, priced from a snapshot, and consumed by the cost gate before each call (§5.4a) |
| **Media router** | Kie.ai | Primary route host, treated as a **replaceable, non-SLA dependency behind a provider abstraction** (D-04a) |
| **Fallback router** | fal.ai | **Registered, not integrated** in v1 — a named migration *project*, not a runtime rung and not a live second path (§5.7) |
| **TTS provider** | ElevenLabs primary, Azure Neural as the cost and fallback tier | Per OD-13; A/B on real Czech scripts during the trial. **A registry route class in its own right**, so the cost gate can price a voice call and the spend ledger can carry it |
| **Assembly engine** | Local FFmpeg-core stack | With a cloud assembly API behind an adapter seam |
| Direct model-vendor API | — | A documented **migration path**, not a v1 integration |
| **Higgsfield** | — | **Explicitly out of the pipeline for v1** (W2.5-6, per A2's H1 recommendation) |

**Why the text-model provider is a role rather than an implementation detail.** It is called on the order of six hundred times in a two-language pack run — drafting plus five model-mediated evaluations per artifact across roughly a hundred and thirty artifacts — which is far more often than the media router, and its per-call price, context limit and structured-output reliability all vary by vendor and by generation. Leaving it unnamed meant the registry could not price it, the forecast could not include it, and the cost gate had nothing to check. Two role-specific selection axes are stated here because they drive the choice and are easy to conflate: the **judge role weights structured-output reliability above prose quality**, because a judge that wobbles on its output contract fails unattended in a way that looks like a passed artifact; the **drafting role weights prose and language quality**, per language, because the English-side choice does not transfer to Czech by default (C5 §6). A cheaper tier serves bulk first drafts and a stronger tier serves judging — cheap-model breadth plus expensive-model depth being a cost-control pattern independent of which vendor is cheapest this quarter.

Naming these as roles rather than as vendors is the whole point of the abstraction. Model and vendor churn is structural and now evidenced twice (W2-16): one major video model's API is scheduled for removal on 2026-09-24, and a named trend vendor died mid-2026. Any design that hard-wires a vendor name rots before build.

**Why the router and not the model vendor directly.** The router is a prepaid credit product with one balance and one API surface fronting many upstream models at a substantial discount to official pricing (per A2's fact ledger). That discount is real and is what makes a $50 trial buy meaningful evidence. What it costs is SLA and indemnification: buying through a reseller forfeits the direct-customer protections, including generated-output indemnification, that the upstream vendor offers its own customers. The design therefore treats the router as replaceable and records everything needed to migrate.

**Why Higgsfield is out.** It is a different product category, not a peer (`SYNTHESIS.md` §8.8): a subscription creator-and-marketing studio aggregating largely the same underlying models, with genuinely differentiated *human-studio* tooling — cinema-style camera control, character identity, a UGC builder, a marketing studio — but subscription-plus-expiring-credits economics, materially thinner API documentation with per-generation pricing, retention and idempotency all unspecified publicly, and moderation stricter than the source models. Its differentiators do not fit an unattended pipeline. An optional personal seat outside the pipeline has zero architectural impact and remains at the operator's discretion.

### 5.2 The model registry

The registry is the mechanism that answers F-3. One record per **route** (a model as exposed by a router, not a model in the abstract), holding:

capability flags · price snapshot with its date · **licence class** · **the router's own licence representation** · **the upstream model provider's own terms: URL and the date they were read** · person-generation policy class · known sunset date · the prompt-pattern version the route was validated against · **last-verified date** · **recheck-by date** · status · accumulated refusal statistics.

**The registry covers four route classes, not one.** It was originally shaped for video, which is why the forecast could not price anything else. The classes are **video routes**, **image routes**, **text routes** (per role, per language, carrying price per input and output token, context limit, structured-output reliability grade and per-language suitability) and **voice routes** (carrying price per unit of speech, language coverage, voice identity, **voice basis** and whether word-level timestamps are returned). A route class determines which contract in §5.3 governs it. Every class carries the price snapshot and the recheck-by discipline, which is what lets §12.1's forecast cover the whole run rather than the media half of it.

**Two licence fields, not one, and the strict default when the second is missing.** A licence *class* is our classification; it is not a snapshot of anything. And a snapshot taken from the router's own page evidences the router's representation, not the **upstream** model provider's grant — which is the weakest link, because upstream providers of this class hold third-party-beneficiary rights enforceable directly against the customer. So the registry carries both the router's representation and the upstream provider's own terms with a URL and a read date. **Where the upstream terms cannot be retrieved, the rights class defaults to the most restrictive value** — `reseller-uninsured`, or `forbidden` where even that cannot be supported — never to whatever the router declares. This is not hypothetical: the media router's own terms were unretrievable during research (W2-12), and the same could be true of an upstream vendor.

**Voice routes carry a voice basis.** Every voice route records `voice-basis` as either **licensed-catalogue** — a voice the provider licenses for commercial synthesis, with the licence evidence recorded — or **cloned-real-person**. In v1 the second value is a **forbidden route class** (§5.3): a cloned voice cannot be selected, because no consent record exists to authorise one. The field exists now rather than later so that the day avatars or voice cloning enter scope, the gate has somewhere to attach rather than needing a registry migration.

Five behaviours make it more than a list:

1. **Prices are rechecked monthly** and the forecast engine reads from the snapshot, never from a hard-coded number, displaying the snapshot date beside the estimate.
2. **A lapsed recheck-by degrades in two stages, not one.** The original rule — a lapsed recheck drops the route to degraded and the router stops selecting it for spend — is total enforcement against a **manual** monthly task across roughly eight routes, performed by a solo operator whose prices live on marketing pages with no machine-readable endpoint. One busy month and every route on every theme stops generating, presenting as "everything degraded to plan-only": a self-inflicted outage with an entirely plausible trigger. So: **stage one, on lapse** — the route stays selectable for a configured **grace period**, its forecasts are marked **stale** with the snapshot date shown, and any submission drawing on a stale price **requires operator acknowledgement**, recorded like any other decision. Unattended runs during grace do not submit against stale-priced routes; they degrade those slots to plan-only and say so, which is a per-slot degrade rather than a pipeline stop. **Stage two, on grace expiry** — the route drops to degraded and stops being selected, as before. Staleness is still enforced; it is no longer instantaneous and total.
3. **A weekly availability probe runs as a scheduled health check** with its own tiny budget line: a credit-balance call plus one draft-tier generation per registered route family. This is the automated half of route health, and carrying it is what makes the manual price recheck less load-bearing — an endpoint that has quietly died is discovered by the probe within a week rather than at 03:00 in the middle of a pack.
4. **A lapsed rights-class verification is treated like a lapsed price**, with the same two-stage shape, because publishing an asset whose rights record rests on year-old terms is the risk the record exists to prevent.
5. **Refusal statistics accumulate in-house**, because no provider publishes refusal rates. Every refusal is logged with route, trigger class and prompt-pattern version, so within weeks the operator has real per-route data instead of vendor claims.

The registry also supplies a **route-policy constraint layer** to prompt composition (A3 R5). Constraints such as the European person-generation restriction, model-level refusal of named real people, and refusal on trademarks in input images belong to the *route*, not to the theme. A theme author should never have to know that a particular route restricts person generation in Europe: the router refuses to select an ineligible route, and the prompt composer injects the constraint automatically.

The v1 roster is fixed at D-13 and is recorded here as *registry contents*, not as architecture: an everyday image route plus a **layout-optimised image route for finals whose composition must leave clean negative space for post-render type** (with two registered fallbacks) — re-justified on layout grounds because the post-render text policy in §4.4 deletes the original "renders type well" rationale, and dropped from the v1 roster if the Phase-3 bake-off does not show it earning its premium on layout alone; a workhorse video route, a quality video route for hero assets only, and a cheap motion-draft route; one registered alternate that is also the only multi-shot-native route, at hero tier only. One widely-discussed video model is **excluded everywhere** because its API is scheduled for removal, which is also the standing proof that no model may ever be hard-wired. Music routed through the router is forbidden for published assets, because no official upstream API exists for it, every route to it is unofficial, and the upstream is in active litigation.

### 5.3 The routing contract

**Four contracts, one per route class.** The ten axes below were derived for **video** and are complete for video; asserting them as complete for every request the plan makes was wrong, because they cannot express a voice call, an image variant count, a reference input or a negative-prompt set. So: the ten axes are the **video routing contract**, and three shorter contracts govern the other classes. Each is provider-neutral in the same way, and each maps to registry capability flags on its own route class.

- **Image contract:** aspect · resolution · **variant count** (the keyframe-variant and hook-overgeneration knobs need somewhere to live) · **reference-image inputs** with their upload lifecycle · negative-prompt layer set (§4.10) · **moderation-strictness expectation**, because aggregator moderation is documented as stricter than upstream and the refusal ladder's first rung depends on knowing that · person policy · rights class · budget ceiling.
- **Voice contract:** language · voice identity **and voice basis** · speaking rate · **word-level-timestamp requirement** · output format · rights class · budget ceiling. This is what lets the cost gate price a voice call, which it previously could not do even though the spend ledger was charged for one.
- **Text contract:** role (drafting or judge) · language · **per-call input and output token ceiling** · structured-output requirement · **whether internal iteration is permitted** (true for exactly the two nodes §1.5 allows one) · budget ceiling. The cost gate reads this before every call, which is the mechanism §5.4a's caps are enforced through.
- **Video contract — the ten axes**, extended by the same negative-prompt and moderation-strictness axes the image contract carries, since the refusal ladder applies identically:

A video generation request is expressed provider-neutrally on these axes (A2 §2.9), each mapping to a registry capability flag:

| Axis | Why it exists |
|---|---|
| **Duration** | Providers quantise differently; the plan asks for seconds, the router picks the legal quantum |
| **Aspect** | Vertical assets are 9:16; some fallbacks force 16:9, and that must be recorded when it happens |
| **Audio** | None, ambient, or native speech with a language — this is where the English/Czech split lives |
| **Mode** | Text-to-video, image-to-video, first-and-last-frame, reference, multi-shot, extend |
| **Motion class** | Product b-roll, kinetic text, scene narrative — drives model choice as much as quality does. **The *talking human* value is disabled in v1** (see the likeness rule below); it remains in the vocabulary so that the day it is re-enabled it arrives with a gate rather than by omission |
| **Quality tier** | Plan-only, draft, standard, hero |
| **Budget ceiling** | Maximum spend for this asset including retries, enforced pre-submission |
| **Person policy** | No-people, adults-only, region-restricted — the European constraint made explicit rather than discovered at refusal time |
| **Rights class** | Direct-commercial, reseller-uninsured, open-weight, forbidden — the publish gate reads this |
| **Resolution** | Price multipliers, and a constraint some fallback routes cannot satisfy |

The router resolves axes → eligible registry routes → cheapest within tier and rights class → submit. **Everything the router could not honour is recorded on the artifact** and surfaced in the pack.

**The v1 likeness and voice rule — a ban, stated once, here.** The plan previously had a *person policy* (no-people / adults-only / region-restricted) and a route-level refusal of named real people, and treated that as covering the ground. It does not: those are the model provider's content policy, not a personality-rights control. They would stop a generated likeness of a public figure and would not touch an employee rendered as a "founder avatar", a licensed stock actor, or a cloned voice — and the plan simultaneously kept *talking human* as a live motion class and *voice identity* as a free-form knob. Silence on a question the law answers is the worst of the three available positions, so v1 takes the explicit one:

**v1 neither creates nor uses a synthetically created or synthetically altered human presenter, and neither creates nor uses a cloned voice.** Concretely: the *talking human* motion class is a disabled value; no reference input depicting an identifiable person may be supplied to any generative route; the voice-identity knob accepts only routes whose `voice-basis` is **licensed-catalogue**, and a `cloned-real-person` route is a forbidden rights class the router may never select. Human presence in footage, where it occurs at all, is incidental and non-identifying — b-roll of hands, of a workspace, of a screen — and is checked at keyframe acceptance (§4.2a item 4) rather than at submission, so a violation costs four cents rather than a paid clip.

**What the ban buys, and what it defers.** It removes an entire consent regime from v1 scope: no person-basis flag, no consent record with scope, duration, platform list and revocability, no employee likeness agreement, and no deep-fake labelling limb to reason about. **The moment avatars or voice cloning enter scope, that regime is a prerequisite, not a follow-up** — a per-asset `person-basis` field derived non-configurably from the generation inputs (reference photograph, voice-clone identifier), a mandatory reference to a scope-limited consent record whenever the value is `real-identifiable-person`, and a **hard publish-gate block on a missing reference, not a warning**. The separate employee-likeness-and-voice agreement is carried as an open item (§16) so it surfaces at the right moment rather than being rediscovered.

**Config placement: theme versus global.** The split follows one test — if changing it would require touching more than one theme at once, it is global.

- **Global (engine level):** the model registry itself; the routing algorithm and its axes; the refusal ladder and its attempt cap; rate-limit pacing; the download-queue policy; rights-class definitions; the person-policy constraint layer; the tier definitions.
- **Per theme (output/runtime block):** which tiers are permitted in which mode; budget caps at every level; the media router selection and any per-theme override; preferred routes within a tier; hero auto-promote (default off) and its per-run cap; dry-run default; the recipe and audio policy per language; per-destination derivative sets.

### 5.4 Cost guards and unit economics

**Caps at four levels — per asset, per run, per day, per month — all enforced before submission.** The cost gate does not carry its own copy of mode logic: it asks the **mode capability resolver** (§11.2) whether this class of side effect is permitted at all in the active mode, and then applies the caps below on top of that answer. Mid-pack cap-hit behaviour is a named outcome rather than an error: the run stops starting new paid work, checkpoints what is in flight, packages what is complete, and exits with the *partial-success — budget-capped mid-pack* class (RA-6).

The honest economics, from A2's verified prices (all figures are the brief's, at its retrieval date, and all are read from the registry at run time rather than hard-coded):

| Tier | Media, per two-language topic pack | Text, per two-language topic pack | What $50 buys (media only) |
|---|---|---|---|
| Draft | ≈ $1.30 | cents to low single dollars, from the registry's text price snapshots | ≈ 30–35 topic packs |
| **Standard** | **≈ $3.80** | **cents to low single dollars** | **≈ 11–13 topic packs** |
| Hero | ≈ $13.50 | unchanged — hero is a media tier, not a text one | ≈ 3.5 topic packs |

**The text column is not a rounding error at run scale, which is why it is now a column. The text wallet is separately funded at a different vendor with its own account-level cap** — the router's $50 credit and the text model provider's per-run budget are two independent wallets and §5.4a addresses both. A two-language topic pack runs 140,000–450,000 tokens depending entirely on whether regenerate loops fire (C5 §6), and a pack *run* carries three topics (per the corrected default in §10.2, reduced from an initial five once §3.5's review-burden arithmetic was made explicit), so a single run is on the order of 0.42–1.35 million tokens — **recalculated honestly from three topics, not extrapolated from five** — and three pack runs a week is roughly 5.4–17.5 million tokens a month. At mid-tier blended text pricing that is the same order of magnitude as the media forecast, not a fraction of it — and it was entirely absent from this table. It stays expressed as a range read from the registry rather than as a number, on the same principle as every media figure: the forecast is computed at run time from price snapshots with the snapshot date shown, and no figure here is normative.

Four readings the architecture must not soften:

- **The trial validates architecture and quality, not a month of production.** Standard-tier production at three pack runs per week lands near $90–140 per month of **media** spend, plus a text line of the same order — so the monthly figure an operator should plan against covers both wallets, and §12.1's forecast shows them separately rather than blended.

**And the text line is not denominated the way that sentence implies.** Every figure in this table is per two-language topic pack, which is the right unit for media and for the gate stack, and the wrong unit for the ranking stage. **The ranking stage's text spend is charged per collection run**, at the research-collection cadence rather than the pack-production one (§8.2), so a monthly text plan built by multiplying a per-pack figure by packs-per-month **omits every collection run that produced no pack** — which, at the recommended daily collection and a small number of packs per week, is most of them. The per-run, per-day and per-month text caps in §5.4a are enforced on runs, not on packs, and they are the figures that bound this correctly. No number is offered here for the omitted term, because the honest one is computed from the roster's declared per-source result caps at run time and read from the registry's price snapshots like every other figure in this section.

- **The two-language doubling is the single biggest cost driver** (OP-1, accepted at W2.5-4). Two distinct levers address it and they were previously merged into one sentence that contradicted itself. **(i) Keyframe reuse across languages** is real and applies to *images*: one approved composition serves both text variants because all message-bearing type is post-render, so the image multiplier is genuinely close to one today. **(ii) Footage reuse across languages** applies only to the CS-A recipe, where both languages run generative clips over the same footage with language-specific overlays and voice added at assembly — and **it is doing no work at all in the default configuration**, because the Czech default is CS-B, which buys no clips and therefore has no footage to share. The lever is banked for the day Czech is promoted; it is not currently "doing more work than ever". **Reusing the English clip set for a Czech asset is permitted only outside short-form** — a Czech LinkedIn native video or a blog hero may reuse English footage with Czech overlays and Czech voice, because the visual is language-neutral b-roll; Czech short-form may not, because the six Czech commitments exist precisely to stop Czech short-form reading as an English asset with different words over it (§3.1). That is a live configuration the plan previously neither permitted nor forbade.
- **The trial envelope is deliberately conservative, and by roughly a factor of two.** The $8 / $35 / $7 split and the ≈$3.80 standard-pack figure are both sized on the assumption that *both* languages buy generative clips. Under the default configuration that is false — the Czech lane runs CS-B — and a real default-configuration two-language topic pack lands nearer $1.90 in media. The envelope is not wrong; it is sized against the more expensive recipe and therefore holds if Czech is promoted mid-trial. But it must be read as ~2× conservative under the default recipe, which is exactly why Phase 4's acceptance criterion no longer rests on "the reserve was untouched" alone (§17).
- **A documented trial plan bounds the risk** (W2-14): roughly $8 on a bake-off producing the operator's own evidence rather than blog claims, roughly $35 on eight to ten real two-language topic packs end to end, roughly $7 held in reserve. Hero tier is never auto-selected. **Bounding a runaway loop by the wallet requires a separate router *account* with a limited top-up, not a separate key**: a key carries its own rate limits and IP restrictions, but a top-up limit is a property of an account and a balance. The correction matters because the mitigation was doing no work as written. The separate account also splits the $50 trial balance, which is a cost of the mitigation worth stating.

**Multi-theme is where balance-delta reconciliation quietly stops working.** Balance delta is only interpretable if exactly one process is spending against that balance for the duration of the snapshot window — and the run lock is **per theme**, both cadence knobs are per theme, and §13 makes multi-theme first-class, so two themes may legitimately run at once against **one prepaid router balance with one API surface**. Under concurrency, "observed balance movement minus this run's ledger total" is meaningless: the unexplained-spend circuit breaker fires falsely on a healthy run, or masks real unexplained spend, and neither failure announces itself. The same defect hits the caps — per-day and per-month caps are per theme, so total exposure across *N* themes is *N* × cap against a single wallet with no global ceiling. Two rules close it, and the first is mandatory:

1. **A global media-spend lock** held across themes for the duration of any spend-bearing media stage, plus **global daily and monthly caps** sitting above the per-theme ones. A second theme's media stage waits; it does not spend concurrently. Collection, ranking, spin and copy generation are unaffected — the lock covers the balance-consuming window only, so multi-theme concurrency survives everywhere it is cheap.
2. **Or, for an operator who would rather not serialise:** one router sub-account per theme, with its own balance and its own top-up limit, which makes balance delta per-theme-interpretable again. This is a real onboarding cost for theme #2 and is named as such in §13.1 rather than discovered during Phase 8.

### 5.4a The LLM budget block — the second wallet

The plan's central orchestration argument is that a deterministic pipeline is chosen over an agentic one **because cost is computable before the run starts** (§1.5). That was true of the media wallet and untrue of the text wallet: §11.1's matrix pointed LLM spend at "per-run budget caps (§8.11)", and §8.11's caps were all media; the only text-cost control that existed anywhere was a per-artifact regenerate counter, which bounds a *multiplier* and not a *base cost*. The base cost is five model-mediated evaluations per artifact across roughly a hundred and thirty artifacts per run. This subsection is the missing half.

**Three ceilings, all enforced pre-call by the cost gate.**

| Ceiling | Unit | What it bounds | Behaviour when it trips |
|---|---|---|---|
| **Per-run text budget** | Tokens or currency, per run, per theme; plus per-day and per-month text caps mirroring the media ones, and a **global** pair above them for multi-theme | Total text spend for the run | The **mid-pack cap-hit outcome class**, reused rather than reinvented: stop starting new text work, checkpoint, package what is complete, mark the rest *not-generated-due-to-text-budget*, exit **partial-success — budget-capped mid-pack** |
| **Per-stage call ceiling** | Calls, per stage, per run | The ceilings §1.5 asserted existed. One per stage: ranking (bounded by candidate count × the N-1/N-2 nodes), copy generation (bounded by asset count × the drafting nodes), each gate (bounded by artifact count × its node) | The stage completes on what it has and the remainder degrades on that stage's own named path — unjudged candidates go to monitor-only with the reason *not judged — ranking call ceiling reached*, and are carried into the next run's candidate pool; they are never dropped (reconciling with §1.5's N-1 rule and §2.7's fail-closed-to-monitor-only, which the earlier "dropped with a reason" contradicted) — ungenerated assets become plan-only, un-gated artifacts fail closed (§11.3) |
| **Per-pack judge allowance** | Calls, per pack | Judge-role calls specifically, across the voice gate and both claim-gate semantic passes — the loop W2-10 identifies as the dominant unattended cost risk | Exhaustion degrades the pack to **review-required**: remaining artifacts enter the pack labelled "not judged — allowance exhausted", never silently passed |

**Two things had to be fixed together here, because fixing only the first would have left the worse defect standing.** The first was a straight contradiction: this table said unranked candidates are **dropped** with a reason, while §1.5's N-1 row and §2.7 both say a candidate whose brand-fit judgment cannot run **fails closed to monitor-only and never defaults open**. Budget exhaustion is one of the three ways §2.7 already names for that judgment to be unable to run, so the two rules were describing the same event and disagreeing about it. **Monitor-only wins**, and it wins with a consequence attached: a monitor-only candidate is retained as a normalised record and **re-enters the next run's candidate pool ahead of newly collected candidates of equal deterministic rank**. Without that carry-forward priority the tail is not merely deferred, it is starved permanently — the same candidates lose the same race every run and the operator sees no evidence that anything was ever missed.

The second defect is the one the contradiction was hiding. **Nothing in the plan defined the order in which candidates reach N-1**, so under a budget trip *which* candidates survive was determined by collection sequence — source roster order and feed pagination. That is an ordering with no editorial meaning whatsoever: it would make the first-listed source's hundredth item beat the last-listed source's best-corroborated one, and it would change silently whenever a source was added, reordered, or paginated differently. So:

**A deterministic pre-rank runs before N-1, and it is mandatory rather than an optimisation.** It orders the surviving candidate set using only signals the cheap rules-first tier has already computed at zero model cost — **evidence class, source priority, corroborating source-family count, and signal age under the item's own freshness class** (the ad-creative class's inverted age term included, per §2.7). It is model-free, it produces a total order with named tie-breaks, it is **stable under retry** so a resumed run judges the same subset as the interrupted one (§8.5), and its precedence order is **engine-fixed and versioned with the ranking-config version — deliberately not a knob**, because a tenant-tunable survival order would make the pre-run cost bound depend on configuration in exactly the way §1.5 chose a deterministic pipeline to avoid.

The claim this earns is narrow and worth stating precisely: the pre-rank does **not** make the trip harmless, and it is not a substitute for sizing the ceiling correctly at readiness (§13.2). What it changes is *what a trip costs the operator*. **A budget trip now loses the tail of a defensible ordering rather than the tail of a fetch sequence** — and because the pre-rank uses no model judgment, it cannot itself be the thing that runs out of budget. The digest names the count of unjudged candidates, the deterministic rank at which judgment stopped, and the fact that they carry forward (§12.1), so an operator can tell "we ran out of budget on weak candidates" from "we ran out of budget on strong ones", which are different problems with different fixes.

**Per-call ceilings sit underneath all three**, one per node class in §1.5's inventory: a bounded input size and a bounded output size, so a single pathological input cannot consume a run's budget in one call. The site-contradiction node N-13 matters most here, because its input is fetched third-party page content and is therefore the only genuinely unbounded input in the system.

**Enforcement is the same choke point, not a parallel one.** The cost gate asks the mode capability resolver whether spend-type effects are permitted (§11.2), then checks the ceilings above before the call leaves the process — identical in shape to media, and identical in the rule that a check after the call is a report rather than a control. The **spend ledger records text calls alongside media calls**, with expected cost from the text route's price snapshot, so §12.1's forecast and §5.6's reconciliation both cover the whole run.

**What the forecast shows, and the term that was missing from it.** The forecast has **three** terms, not two, and they are never blended: **media**, **text-per-artifact**, and **text-per-candidate**. Each carries its own price-snapshot date. The first two were already here. The third was not, and its absence is the reason the pre-run bound was arithmetic rather than a fact: the per-artifact term is computed from the planned artifact count × the gate stack's per-artifact call profile × the route's token ceilings, which is checkable — but **node N-1 runs once per candidate inside the ranking stage, before any artifact exists**, so no artifact count can ever contain it. The earlier text of this subsection bounded the ranking stage by "candidate count × the N-1/N-2 nodes" and then never said what a candidate count is. **A bound expressed as a function of an unstated quantity is not a bound**, and it sat directly underneath the claim §1.5 uses to reject an agentic orchestrator.

The third term is **the declared maximum candidate count × N-1's per-call profile × the route's token ceiling**, where N-1's profile is one call per candidate with no internal iteration (§1.5), plus **at most one N-2 call per candidate carrying prior-pack state** (§2.8a) — so the ranking stage's worst case is two model calls per candidate and its per-stage call ceiling is sized against that, not against one.

**The declared maximum candidate count is a known number before the run starts, because the query profile already carries it.** Every source's query profile states a **result cap and a per-run page allowance** (query-steering annex §5.2), and the declared maximum is the sum of those caps over every enabled source, every configured language and every query the profile issues in a run. Nothing here is estimated and nothing is emergent: **the operator has already declared this number source by source; the forecast has only ever needed to add it up.** That is what makes the ranking stage's cost computable in the same sense the media stage's is, and it is what closes the gap between §1.5's argument and §5.4a's arithmetic.

The reason the term is not small is worth stating rather than leaving to be discovered. The roster's search surfaces return on the order of a hundred items per query at their empirical caps, several query-feeds exist per language, two locales are configured, and the discovery-mode feeds — launch registries, the model hub, the video surface, newsletters and the trend-vendor read — contribute their own caps on top. **Deterministic screening removes most of it before N-1 ever sees it**: the veto list and the numeric brand-fit floor run before any model cost (§2.7), and the topic-relevance filter drops non-matching discovery items inside normalisation for exactly this reason. But screening is a run-time observation and the forecast is a pre-run promise, so **the forecast term uses the declared maxima and is therefore a ceiling, not a prediction** — deliberately, because the property being defended is that a mis-configured run cannot exceed a number the operator saw beforehand. §12.1 prints the realised post-screen candidate count beside the forecast so the distance between ceiling and reality becomes a measured quantity, and per §0.3 the caps are tightened from that measurement rather than from a guess.

**A fourth, smaller line completes the decomposition: brand-truth verification.** Node N-13 is a model node inside brand-truth resolution (§6.6), running before collection, and it was likewise absent from every text figure. Its call count is bounded the same way and is likewise declared in advance: **the number of pages in the declared verification page set, per fact class requiring semantic comparison**, times one call each at N-13's per-call ceiling. It is small next to the other three terms and it is not zero, which is precisely why §6.5 may no longer tell the operator that a brand-truth degrade cost nothing (Block 6).

**Knob note.** The per-source result cap and per-run page allowance are existing query-profile values and stay where they are; no new default is introduced here, and none should be, because a default candidate ceiling invented in this section would silently overrule a roster the operator configured deliberately.

### 5.5 Retention, re-hosting and the artifact of record

Provider-generated media is deleted after 14 days and result URLs expire sooner, with an explicit expiry flag on at least one route family (per A2's fact ledger). Three rules follow:

1. **Every artifact is re-hosted immediately on completion**, with a byte-length and checksum record, before the asset slot is marked complete — so a truncated download is never marked done.
2. **The download queue is drained in expiry order at the start of every run, before any new submission.**
3. **Provider URLs never appear in a pack** and are never the artifact of record.

### 5.6 Refusals, substitution and the money-safety boundary

**Refusals are a normal outcome class**, not an error path. They surface both synchronously at submission and asynchronously mid-task, and the marketing-relevant triggers are predictable: named real people, the European person-generation restriction that directly affects a Czech operator, trademarks and logos in input images, and documented false positives on entirely wholesome commercial storyboards. The ladder is bounded and terminates in a *useful* state: one automated sanitise-and-rewrite → one model swap to a registered alternate → **degrade to plan-only**, packaging the approved keyframe, script and prompt with the refusal reason. Never a retry loop. A policy refusal is emphatically not transient and must never enter the ordinary backoff path.

**Silent model substitution is guarded explicitly** (W2-03). The router's primary video route can switch to a backup model on some content-review triggers, and such fallback outputs cannot use the high-resolution endpoint and are forced to 16:9. Two consequences are recorded on every artifact: **requested versus delivered route, aspect and resolution**, so a 16:9 asset cannot silently enter a 9:16 destination and fail at publish time; and the **per-asset provenance record is resolved after completion, not at submission** (D-20), because a different model may carry a different rights class and a license snapshot naming a model that did not render the asset destroys the rights-defence record.

**Delivered route identity is best-effort with a defined inference rule, not an asserted fact.** This is a correction with real consequences, because the field is a publish-gate precondition (§7.4, D-20) and the evidence never established that it is observable. The source finding says the substitution is **silent**, and the word is doing exactly the work it appears to do: what the evidence documents is a *side-effect signature* — aspect forced to 16:9, the high-resolution endpoint unavailable — not a reported model identity. "The router must record which model actually rendered" is an obligation the research placed on **our** abstraction; nowhere is a delivered-model-identity field in the provider's response evidenced. Making a mandatory publish-gate field out of an unverified capability turns a rights defence into a publish deadlock on exactly the assets that most need one.

So the field resolves in three states, and the rule is stated rather than hoped:

1. **`identity-reported`** — the provider's response names the rendering model. Record it, resolve the rights class from it, done.
2. **`substituted — identity unknown`** — the provider does not name it, **and** the substitution signature is present (delivered aspect differs from requested, or the high-resolution endpoint was unavailable, or any delivered-versus-requested divergence). Record the signature that triggered the inference, and treat the rights class as **unresolvable**.
3. **`assumed-as-requested`** — the provider does not name it and no divergence is observable. Record the requested route as the working identity, explicitly flagged as an assumption rather than an observation, and resolve rights from it.

**The disposition for an unresolvable rights class is plan-only, not blocked-forever.** An asset whose renderer cannot be identified is **not publish-ready**: it degrades to plan-only with the reason attached and the approved keyframe, script and prompt intact, which is the same complete-outcome shape §5.7 guarantees for every other degrade. It is not silently published on an assumed identity, and it is not left as an undisposed block. The delivered-versus-requested note the operator sees names what was observed rather than a route the system may have no way to name.

**And the underlying question is asked before the build starts, not discovered during it.** "Does the router's task-status response name the rendering model?" joins the manual terms pull as a **Phase-0 router checklist item** (§17), because this single unverified fact gates the publish path for every substituted asset.

**Money safety is entirely client-side, because no provider idempotency exists.** The router documents no idempotency key, no client-reference field and no deduplication semantics on task creation (verified in A2, correcting C3's earlier assumption). The consequences — a write-ahead spend ledger with deterministic asset identity committed before submission, resolve-by-query on restart rather than blind resubmission, a named `submitted-unknown` state with no automatic resubmission, balance-delta reconciliation with an unexplained-spend circuit breaker — are D-17, and **§8.5, §8.6 and §8.13 own their design.** This section references them so the provider architecture is complete; it does not duplicate them.

The billing situation that makes all of this necessary should be stated plainly rather than assumed away (W2-02): the router claims failed tasks are not charged, community reports contradict that, and only a balance snapshot is exposed rather than itemised billing. So the ledger records both an **expected cost** from the registry price snapshot and an **observed cost** from balance delta, and unexplained spend is a first-class alarm that halts new submissions.

**One further honest gap** (W2-12): the router's own terms of service could not be retrieved during research — every legal path was blocked and no archive snapshot exists. The working posture is that **the router grants nothing**, based on the structurally identical terms of two comparable router products that *were* retrievable in full: output ownership is set by each model's own terms, the customer is solely responsible for reviewing them, warranties are disclaimed, and **the upstream model providers hold third-party-beneficiary rights to enforce directly against the customer**. The real control is therefore the per-asset upstream license snapshot, and a manual browser pull of the router's terms is a named prerequisite before build sign-off.

### 5.7 Outage and fallback ladder

    NORMAL:   media router (primary route host)
                |  route unavailable / degraded in registry
                v
    IN-RUN:   alternate registered route within the same router
              (same tier, same rights class, cheapest first)
                |  router-wide outage or sustained failure
                v
    DEGRADE:  plan-only for the affected asset slots
              (a complete, packaged, useful outcome)
                |  sustained across runs, engagement threshold met
                v
    MIGRATE:  fallback router  (registered in v1, integrated on demand)
                |  spend or reliability justifies it
                v
    MIGRATE:  direct model-vendor API
              (3-4x the price, with SLA and indemnification)

**The ladder has two halves and they operate on different timescales — presenting them as one continuous descent implies a continuity that does not exist.** The first two rungs are **runtime rungs**: they execute inside a run, in seconds, automatically. The last two are **migration projects**: a different API surface, different pricing units (the fallback router prices per second of output against the primary's per-clip), different asynchronous semantics, different rights classes to snapshot, and a re-verification of the four routing contracts against a surface the abstraction has never been tested against. They are multi-day builds, not fallbacks.

The honest consequence, stated plainly because "no rung silently produces a worse asset" is true and incomplete: **a sustained primary-router outage means plan-only output for as long as the integration takes** — days, not minutes. Plan-only is a complete, useful, packaged outcome, and that is exactly why it is survivable; but an operator should know they are living in it for a working week, not waiting for an automatic failover that is not built. OD-23 leaves the *trigger* open, correctly; the *lead time* is not open and is stated here.

**One cheap thing makes "registered" mean more than "named".** A paper-level conformance check of the four routing contracts against the fallback router's published surface — do the axes we express have expressible counterparts there, and where do they not — is a Phase-3 deliverable (§17). It costs about an hour, and without it the abstraction has exactly one implementation and will silently encode that implementation's assumptions, which is the failure mode that makes a "registered fallback" worthless on the day it is needed.

**No eligible route is its own rung.** Person-generation eligibility is treated in §5.2 as a route capability flag, which handles the case where *some* eligible route exists. It does not handle the case where **no route is eligible for person-bearing image-to-video in this jurisdiction for this account** — a real possibility for a Czech operator, since the primary video family restricts EU person generation to an adults-only setting, refuses named real people at model level, and has been observed to require a per-account allowlist request with a lead time. Under the v1 likeness ban (§5.3) the pipeline does not produce synthetic presenters at all, which removes most of this surface; what remains is incidental human presence in b-roll. The disposition when no eligible route exists: **people-free keyframe composition becomes the theme's injected default constraint** at prompt composition, and if a slot cannot be composed without a person it degrades to plan-only. Determining that eligibility, and submitting any allowlist request, is a Phase-0 prerequisite (§17), because a lead time discovered in Phase 4 is a lead time paid twice.

The engagement threshold for each migration step is a named open item rather than a guess. What the architecture guarantees is that **no rung silently produces a worse asset**: a degraded run produces plan-only artifacts and says so, rather than substituting a lower-quality route without telling anyone.

### 5.8 Room for the later paid phase

The assignment reserves architectural room for Meta Ads and paid creatives, with generation in scope and spend human-controlled. Three seams already exist and no new ones are needed: the **ad-creative skill bundle** is one of the four named skill bundles and already carries a stricter claim-safety rubric and a mandatory human gate before any spend (A3 §2.2); the **routing contract's rights class** axis already distinguishes assets that may carry paid distribution; and the **publish allowlist** is per mode and per destination, so a paid destination is an allowlist entry rather than a new enforcement path. The one substantive addition the paid phase will need is a separate mandatory ad-disclosure control — undisclosed AI is reported as a leading cause of ad rejection with strike escalation (per C1 and C7 ledgers) — which is a check-class addition, not an architectural change.

**Knobs this section contributes to §10.** Media router selection and per-theme override; **text-model provider and route selection per role per language**; permitted tiers per mode; preferred routes within a tier; hero auto-promote flag and **the separate per-run hero cap dimension**; budget caps per asset, run, day and month; **text budget caps per run, day and month, per-stage call ceilings and the per-pack judge allowance**; **global cross-theme daily and monthly caps**; unexplained-spend tolerance; refusal-ladder attempt cap; submission pacing rate; poll interval and per-job poll budget; **price-recheck cadence and the recheck-by grace period, including whether an unattended run may submit against a stale-priced route (it may not)**; **the weekly availability-probe budget**; rights-class allowlist per destination; person-policy defaults per theme; fallback-router engagement threshold; the trial budget envelope and its reserve. *(The dry-run default per mode is engine-level and no longer a theme knob — §10.4a.)*

---

## §6. Brand-truth and spin architecture

### 6.1 What this layer is for

Everything upstream of this layer decides *what to talk about*. This layer decides *what we are allowed to say about ourselves while talking about it* — and, just as importantly, what happens when we do not know. It is the layer where the assignment's hardest constraint lives: never invent prices, ROI, client names, case metrics or fake proof, and when the truth is unavailable, degrade honestly rather than fill the gap.

It runs **first in every run**, before collection and before any spend, because the degrade decision changes what the rest of the run may do and a research-only run must not have paid for anything before finding that out (C6 §6.1).

### 6.2 Where brand truth comes from

Four inputs, and the access split between them is a decision, not an implementation detail.

    THEME CONFIG (spin block)          NOTION WORKSPACE
      design artefacts:                  internal knowledge:
      voice rules, CTA policy,           identity, offers + status,
      pricing policy, product            capability statements,
      rules, visual baseline,            ICP map, claim ledger,
      hard-excludes baseline             proof allowlist
            |                                   |
            |                    +--------------+--------------+
            |                    |                             |
            |            NOTION REST                    NOTION MCP
            |          internal integration            hosted, OAuth
            |          token, read-only,               interactive only
            |          scoped to designated
            |          fact locations
            |                    |                             |
            |                    v                             v
            |            EVERY pack-bearing              "what does the KB
            |            resolution, including            actually say"
            |            all scheduled runs               exploration
            |                    |
            v                    v
        +--------------------------------------------+
        |          BRAND-TRUTH RESOLVER              |
        |   per-fact-class precedence                |
        |   three asymmetries                        |
        |   conflict outcomes                        |
        |   gate-first then score -> confidence band |
        +--------------------------------------------+
             ^                        |
             |                        v
     LIVE PUBLIC SITE          BRAND-TRUTH SNAPSHOT
     targeted verification     (hashed, timestamped,
     of binding facts and       band recorded, fact-usage
     CTA URL liveness only      trace per topic pack)
             ^
             |
     HUMAN RUN OVERRIDES
     may NARROW, never create commercial facts

**The access split (D-10): MCP is for humans, REST is for records.** The hosted MCP path is genuinely pleasant for exploration and satisfies the assignment's MCP-extractable mandate — but its tokens expire roughly every three hours and require re-authentication several times a week, so a 3 a.m. run hits an expired token and blocks; and its search is capped at 25 results with **no property-based filtering** (per C1 §2 and §1). The REST path with an internal integration token is non-expiring, supports full property filters, and is comfortably within rate limits for a workload of tens of requests per run.

That is not merely an availability argument. Property filtering is *required* to enforce the single most important structural control in this layer — **an offer whose status is not explicitly live is unspinnable** (W2-11) — which MCP cannot do reliably. So:

| Context | Access path |
|---|---|
| Interactive exploration; theme-readiness browsing | Notion MCP (hosted) |
| **Any resolution that produces a snapshot a pack depends on — including every interactive pack run** | Notion REST, internal integration token, read-only, scoped to designated fact locations |
| Unattended scheduled runs, every mode | Notion REST, internal integration token |
| REST integration unavailable | A self-hosted token-based MCP server — a contingency, not a design branch |
| All paths fail | Offline snapshot → band capped at MINIMAL → unattended degrades to research-only |

**Credential health is a named, alarmed, runbooked risk for this token too — not only for the ad library's.** The internal integration token is documented as non-expiring, and that fact appears to have substituted for a health check. "Non-expiring" says nothing about "cannot be revoked": a workspace admin rotating credentials, deleting the integration or changing permissions produces a token that is present, syntactically perfect and rejected in use. Its blast radius is strictly larger than the ad-library token's — it gates every fact class, in both languages, on every run, while that one gates a single research axis — and yet only the smaller one had a proactive alarm and a runbook entry (R-05). So:

- **A cheap read-only health call runs at run start**, independent of the full brand-truth pull, purely to establish that the credential still authenticates. Its failure is named specifically — *the knowledge-base integration token was rejected* — rather than arriving later as a generic brand-truth degrade.
- **Token reissue is a named runbook item**, written in Phase 0 alongside the ad-library one (§17).
- **The reader classifies failures by error class, not only by call shape.** §8.10's retry policy is defined by call shape (submission-type versus polling), which cannot distinguish a permanent authorisation failure from a transient network fault — and retrying a revoked credential six times with backoff is both useless and slow. The brand-truth reader classifies every failure into at least **{transient · permanent-auth · permanent-endpoint}**, retries only the transient class, and records the permanent classes **verbatim — status code and timestamp — into the brand-truth panel**. That is what makes §6.5's promise of "the actual cause and the actual fix" a mechanism rather than an aspiration: the operator reads *"the knowledge-base integration token was rejected — reissue it and update the secrets file"*, not *"brand truth degraded, see log"*.
- **Credential *validity* is discovered at first use, and that boundary is now explicit.** §11.3's "missing secrets — absent or unreadable at theme load" is a **presence-and-syntax check only**; a present-but-invalid credential is not caught there and is not meant to be. Validity is established by the first stage that actually uses each credential — brand-truth resolution for the knowledge base, site verification for the site, the media router's own auth for generation — each reporting through its own already-defined degrade path. Two fail-closed mechanisms, one boundary, stated rather than inferred.

**The plan-versus-fact hazard is handled structurally, not statistically** (W2-11). A Notion workspace contains roadmap pages, drafts and aspirations sitting beside fact pages, and they are fresh, well-written and internally consistent — confidence scoring cannot catch them, and they are the highest-probability source of a false "we do X" claim in this deployment. The control is that resolution reads **only from designated fact locations**, and the live-status filter above. If a workspace cannot cleanly separate plan from fact, that is an escalation to the operator, not something to paper over.

### 6.3 The fact taxonomy

Fourteen classes in three tiers (C6 §3, adopted as canonical after reconciliation against C1's retrievability findings). **B**locking: content cannot be generated without inventing something. **C**onstraining: absence neither blocks generation nor lowers quality in any way the model can perceive — which is exactly why it *silently invites fabrication*. **E**nriching: absence only lowers quality.

| Class | Contents | Tier | Home structure | May be legitimately empty? |
|---|---|---|---|---|
| **F-A** Identity and entities | Legal entity, brand names, which brand owns which domain, spokespeople and roles | B | Page | No |
| **F-B** Offer catalogue **with status** | Named offers, one-line description, status, owning brand, canonical URL | B | Typed database (status filter is load-bearing) | No |
| **F-C** Capability statements, **positive and negative** | What each offer does today, and explicitly what it does **not** do | B | Page | No |
| **F-D** ICP map | Segments with segment **type**, pains, language, platform | B | Typed database | No (at least one segment) |
| **F-E** CTA set | Allowed CTA classes per offer × destination × language, literal phrasing per language, destination URL | B | Typed database | No |
| **F-F** Pricing policy | The *rule* (for example: never state prices in social, link to the pricing page) | B | Config-primary | No |
| **F-G** Price values and commercial terms | Actual prices, plan contents, trial length, guarantees, discount and affiliate terms | C | Typed database + **site-verified** | Yes |
| **F-H** Claim ledger | Per entry: text per language, claim type, provenance, evidence pointer, valid-from and valid-until, usage scope | C | Typed database | Yes (empty ≠ unreadable) |
| **F-I** Proof / case allowlist | Case studies, client names with **permission status and expiry**, metrics with evidence | C | Typed database | Yes |
| **F-J** Hard excludes | Forbidden topics, framings, claim types, do-not-mention entities | B | **Both** config and Notion; union wins | Yes — but empty is not the same as unresolved |
| **F-K** Product rules | Site-first offers, atomisation order, per-language page availability | B when blog enabled, else E | Config-primary | Yes |
| **F-L** Voice rules and exemplar-corpus pointer | Tone rules, banned phrasing, corpus reference | E | Config-primary | Yes |
| **F-M** Visual brand baseline | Logo usage, palette, on-image text rules | E | Config-primary | Yes |
| **F-N** Compliance obligations | Entity disclosure, affiliate disclosure, AI-content labelling obligation | B (policy) | Config-primary | No |

**The single most important rule in this layer: missing is not the same as empty.** Every constraining class resolves to an explicit state — *resolved-with-values*, *resolved-empty*, or *unresolved*. **Resolved-empty is a first-class, safe, generative state**: the generator is told it has zero approved proof points and should write teaching-led content. **Unresolved is a failure state**: we do not know whether proof exists, so claims are forbidden *and* the confidence band drops, because we also cannot trust the excludes list that lives beside it.

**Negative capability statements are blocking, not enriching** (C6 §3.4). The highest-frequency overclaim in this category is autonomy inflation — "runs your outbound on autopilot", "sends for you", "24/7 SDR" — and the competitor corpus in `docs\marketing\` is saturated with exactly that framing. A claim checker that only inspects numbers will never catch it. So every offer's record carries a *does-not* list, and capability claims are their own check class.

**Two brands, two domains, one engine.** The theme's own strategy runs content on two domains with a clear division between the product and the broader agency-facing offer. Brand routing is therefore a **resolved fact**, and "the CTA points at the wrong domain for the offer being discussed" is a real, checkable defect class — not a style nitpick.

**Named humans are brand facts.** A person allowlist is required, because without one the entity checker either flags the founders in every post (and gets switched off) or is loose enough to miss an invented customer name.

**Where the claim ledger lives.** Recommended home is a typed Notion database with a config pointer and the design-time policies in config (OD-9 recommendation; open at the operator's discretion). It can express provenance, evidence pointer, validity window, per-language text and usage scope; it is queryable by property filter; and it is editable by a marketing-literate operator without touching config files. **The one exception is hard excludes**, which live in *both*: config carries a baseline, Notion may add, and the **union wins** — because excludes are monotonic and must remain enforceable during a Notion outage.

### 6.4 Precedence, per fact class — and the three asymmetries

D-03 locks a flat default order. C6 demonstrates that the default is right for internal knowledge and **wrong for commercially binding facts**, because the live site is the thing a prospect can actually read an hour before seeing our post. Precedence is therefore per fact class (D-03a).

| Fact class | Primary | Verifier | Disagreement outcome |
|---|---|---|---|
| F-A identity, entities, people | Notion | Site (public-facing usage) | Degrade to the intersection; flag |
| F-B offer catalogue and status | Notion | **Site (binding)** | **Red flag** if the site shows retired or 404 while Notion says live |
| F-C capability statements | Notion | Site (must not contradict) | Degrade to the **narrower** wording; flag |
| F-D ICP map | Notion | — | Resolvable |
| F-E which CTA | Config | — | Resolvable |
| F-E CTA destination liveness | — | **Site wins absolutely** | A 404 kills that CTA whatever Notion says |
| F-F pricing policy | Config | — | Take the stricter policy |
| **F-G price values, trial terms, guarantees** | **Site (binding)** | Notion | **Red flag — never tie-break** |
| F-H claim ledger | Notion | Site may **invalidate**, never **add** | Contradiction quarantines that entry |
| F-I proof allowlist and permissions | Notion | — | Missing permission means unusable; no precedence question |
| **F-J hard excludes** | **Union of all sources** | — | Never resolvable downward |
| F-K product rules | Config | Site (page existence) | Degrade to the safer rule |
| F-L voice, F-M visual | Config | — | Config wins — these are design artefacts of this system, not business facts |
| F-N compliance obligations | Config | — | Take the stricter |

**Three asymmetries are load-bearing and must survive into implementation.**

1. **Excludes are monotonic.** Any source saying "never say X" wins permanently for that run. No precedence rule may *remove* an exclusion — otherwise a stale config could re-enable a topic the operator banned yesterday.
2. **The site can subtract but never add.** If our own site no longer mentions a feature, that invalidates a capability claim. But our own marketing copy is never *evidence for* a claim — otherwise the system bootstraps its own puffery into approved truth and any hallucination that ever reached the site becomes permanent.
3. **Silence is not agreement, and unreadable is not disagreement.** A source that does not mention a fact reduces corroboration; a **failed fetch is recorded as "not observed", never as "the site disagrees"**. Collapsing those two is how a flaky network becomes a false red flag and trains the operator to ignore alarms.

**Three conflict outcomes.** *Resolvable* — different granularity or wording, one source silent, staleness within tolerance: apply precedence, record which source won, continue. *Degrade* — compatible-but-different statements about a soft fact: take the weaker, narrower statement, mark it partial, continue. The rule of thumb is that when two of your own sources describe your product differently, publish the smaller promise. *Red-flag stop* — **no tie-break permitted** — triggered by any disagreement inside the commercially binding set, an offer-availability disagreement, a claim-ledger entry contradicted by the site, a proof entry whose permission is absent or expired but which appears usable elsewhere, or two different values for the same case metric. The fact is quarantined, every asset depending on it is blocked, and both values are surfaced verbatim with their sources and timestamps.

**Why a price conflict is never tie-broken:** tie-breaking means choosing which of two possibly-wrong numbers to publish. Publishing a wrong price is a commercial promise, potentially a consumer-protection matter under Czech law — which gives the never-invent rule independent legal force (C7 §2.9) — and certainly a trust event with a prospect who read the other number an hour earlier. Not posting today costs almost nothing. There is no scoring function where that trade favours guessing. The correct output is an alert to a human, and it is a *useful* alert: it means the operator's own house is out of sync.

**Human run overrides are bounded, not supreme** (C6 §4.3). They may **narrow** — force a topic, suppress an offer, force one of the already-approved CTAs, restrict to one language, lower the confidence ceiling. They may **not create commercial facts**: no new price, claim, client name, case metric or capability, absolutely, in unattended mode. Interactively, an operator wanting to introduce a new commercial fact is directed to write it into the claim ledger with provenance, evidence pointer and validity window — the same path with the same audit trail as any other fact. **The friction is the point.** Every override is recorded in the snapshot as a source of its own.

### 6.5 Confidence bands and the exact degrade trigger

**Gate first, then score** (C6 §5.3). The tempting design is a weighted average of per-fact confidences, and it fails in a specific, predictable way: a run with a complete ICP map, voice corpus, capability set and excludes list but **no resolved pricing policy** scores beautifully and proceeds. High scores on many soft facts mask one missing hard fact.

So: **Step 1** — every blocking class must be resolved or legitimately resolved-empty, non-conflicted and not hard-stale; any gate failure sets a hard ceiling on the band and **names itself as the reason**. **Step 2** — determine the band inside that ceiling by **counting rules over the fact classes**, not by a score. **Step 3** — capabilities follow the band, which is what makes bands mean something operationally.

**Step 2 is a counting rule, not a score, and the change is deliberate.** The earlier formulation scored coverage, corroboration depth, freshness ratio and conflict count, then defined the bands by prose preconditions — "constraining classes *mostly* resolved" for FULL, "corroboration is *thin*" for PARTIAL. Those adverbs were the cutoffs, and they carried the entire difference between a pack that may state trial terms and one that may not. Unlike the judge threshold, which has a golden set, a direction-split agreement measure and a calibration cadence (§14.2), the band score had **no calibration mechanism and no measurable ground truth** — so §0.3's standing rule that thresholds come from measured run data had nothing to measure, two implementers would produce two different band functions, and the operator-facing meaning of PARTIAL would drift silently. A counting rule needs no calibration, is auditable row by row in the brand-truth panel the section already specifies, and cannot drift:

- **FULL** requires: every blocking class resolved (or legitimately resolved-empty) and non-conflicted; **every constraining class** in one of the two resolved states — never *unresolved*; every commercially binding fact observed this run or inside its stale-warn window; and **zero conflicts of any severity**.
- **PARTIAL** is the remainder above the gate: all blocking gates pass, but at least one constraining class is unresolved, or at least one binding fact sits between its stale-warn and hard-stale thresholds, or a non-red-flag conflict was recorded and degraded.
- **MINIMAL** and **INSUFFICIENT** are unchanged, because both were already precondition-defined rather than scored.

The band therefore has a *derivation* an operator can check against the panel, and the panel's per-class rows are literally the count.

The band is computed **per (theme, language)** — a Czech pack can be blocked while the English pack proceeds, which falls straight out of D-02. Bands are deliberately coarse: four names, no decimals shown. "Brand confidence 0.78" invites arguing with the thermometer; "PARTIAL — proof claims off, prices off" tells the operator what actually changed.

| Band | Precondition | What content may do |
|---|---|---|
| **FULL** | All blocking gates pass; commercially binding facts corroborated by the live site this run or within the warn window; zero conflicts; constraining classes mostly resolved | Full spin. All CTA classes subject to their own preconditions. Approved proof claims allowed. Prices and trial terms may be stated if policy permits. Long-form and site-first content allowed |
| **PARTIAL** | All blocking gates pass, but corroboration is thin or some constraining facts are unresolved or in the warn window | Spin allowed. **All proof claims blocked** unless that individual ledger entry is itself at full confidence. **No prices, no trial terms, no case metrics, no comparative claims.** CTAs limited to the zero-commitment and product-page classes. Pack marked |
| **MINIMAL** | Running from an offline snapshot within its validity window, or config-only resolution of blocking classes | Capability-level statements from the snapshot only. **No numbers of any kind.** No proof, no comparisons, no price or trial CTAs. Interactive-only by default, heavily marked |
| **INSUFFICIENT** | Any blocking gate fails; an unresolved red-flag conflict on a binding fact; a snapshot that is expired, fails its integrity check, **or has never been written at all** | **No brand spin at all.** Research-only output |

**"No snapshot exists" is a named precondition of INSUFFICIENT, distinct from "a snapshot exists but expired."** The access-path table in §6.2 lists the offline snapshot as though a snapshot is always available, which is untrue on the case that matters most: a brand-new theme whose very first run coincides with a knowledge-base outage has never written one. Naming the two cases separately means a first-run failure and a seventh-day failure both have a name and both produce an accurate sentence in the digest, instead of one being inferred from the other.

**The exact unattended degrade trigger.** In an unattended run, for the language being generated, the run degrades to research-only if **any** of the following holds (C6 §5.4):

1. The band is **below PARTIAL**.
2. **Any unresolved red-flag conflict** exists on a blocking or commercially binding fact — regardless of band, because a conflict is not an average and does not get diluted by everything that is fine.
3. Brand truth is available **only from an offline snapshot** older than the configured maximum offline window, or whose integrity check fails.
4. **The claim ledger could not be read at all** — distinct from being empty. Unknown is not empty: if we cannot read the ledger we can neither prove a claim is allowed nor trust the excludes beside it.
5. **Hard excludes are unresolved** — again, not empty, unresolved. You cannot enforce "never say X" without knowing X.

**How conditions 1 and 3 actually interact, stated once because two sections previously said different things.** Running from an offline snapshot caps the band at MINIMAL always (§6.6), and MINIMAL is below PARTIAL — so condition 1 fires on *any* unattended run resolving from a snapshot, immediately and unconditionally, regardless of how recent that snapshot is. **This section is the single owner of the rule and it stands as written** (D-33): an unattended run that cannot reach the knowledge base degrades to research-only, full stop. Two consequences follow and are applied rather than left to be discovered. Condition 3's "older than the configured maximum offline window" is therefore **reachable only in interactive runs**, where an operator may consciously accept a MINIMAL outcome — and the **maximum-offline-window knob is scoped to interactive runs only** (§10.3), because an unattended seven-day snapshot path is a path §6.5 forbids and nobody should build it. R-15's wording is corrected to match (§15.2).

Conditions 1 and 3 are band-driven; **2, 4 and 5 bypass scoring entirely** and cannot be overridden by an operator even interactively, because they are about not knowing the rules rather than about having thin data. The brand-truth gate that acts on this trigger is one of the four fail-closed triggers enumerated at §11.3, and like every other side-effect decision it reads the active mode from the single **mode capability resolver** (§11.2) rather than encoding mode logic of its own.

**Why the threshold sits at "below PARTIAL" rather than "below FULL".** Requiring full confidence for unattended runs would degrade the pipeline every time a site fetch flaked, and a system that cries wolf daily gets its alarms ignored or gets switched off — which is the real failure. PARTIAL is defined *precisely so that everything dangerous is already switched off at PARTIAL*: no prices, no proof, no metrics, no comparative claims, no commitment CTAs. **The safety comes from the capability table, not from the threshold's height.**

**What the operator sees when it fires** (C6 §5.5): a distinct run outcome, separate from both success and failure, so monitoring can alert differently; one plain sentence at the top of the digest naming the actual cause and the actual fix, not "confidence low"; a brand-truth panel with one row per blocking class showing state, source used, observation age and a *specific* fix action; **both conflicting values side by side with sources and timestamps**, so the operator can fix their own systems without opening anything else; **the two spend figures the ledger already holds, itemised rather than summarised as "zero"** — **media spend, which is zero and is guaranteed to be zero by stage ordering** rather than by assertion (brand-truth resolution runs once per run before collection and before any spend-bearing media stage, §6.6), and **text spend to the point of degrade**, which is not zero and must be printed with its parts named: the **N-13 site-contradiction calls** made during brand-truth resolution itself, and — because a research-only degrade still runs collection and ranking — the **ranking stage's N-1 calls** for this run. The flat claim that zero was spent was written when text was not a wallet, and it is now wrong in the one place it is most read: **on the contradiction path, N-13 is a model node inside brand-truth resolution, so text budget has already been burned by the very comparison that computed the degrade.** Telling an operator a degraded run cost nothing, on a run whose ledger says otherwise, damages exactly the trust this panel exists to hold; and — critically — **the research output remains complete and reusable**, so the next run or an interactive re-run spins the same already-paid-for topics. A degrade that throws away the run's work will be engineered around by the operator within a fortnight. An anti-flap rule escalates prominence on repeat rather than repeating an identical low-signal message.

### 6.6 Refresh cadence, the offline snapshot, and the per-pack snapshot

**Cadence.** Once per run, before anything is spent and before collection, cheapest gates first: config load → snapshot validity → Notion pull → targeted site verification. A **TTL-guarded re-pull** avoids pointless re-fetching when a theme runs several times a day. **Site verification is targeted, not a crawl**: only the binding facts and CTA URL liveness, a handful of timeboxed fetches per run, with failures recorded as "not observed".

**What "targeted" can honestly deliver, and what it cannot.** The precedence table (§6.4) assigns the site a verifier role on capability statements ("must not contradict") and on the claim ledger ("may invalidate, never add"). Those are **semantic comparisons over arbitrary site prose**, not liveness checks, and a handful of timeboxed fetches cannot perform them across a site — which created three problems at once: an under-scoped verification budget feeding a precedence rule that needs more; an unregistered model node with unbounded input; and a quiet collapse of the third asymmetry, since "not observed" and "did not look" become the same thing when coverage is hoped for rather than declared. All three are closed by declaring coverage instead of assuming it:

- **The per-run verification budget covers exactly one job: liveness, price values, trial terms and offer status, on a configured URL set.** That is what a handful of fetches can do honestly, and it is what F-B, F-E and F-G actually need.
- **Capability-statement and claim-ledger verification read a declared verification page set per fact class** — the theme names which pages a contradiction would live on for capabilities, and which for each claim class. Coverage is then a stated property with a stated limit, and "silence is not agreement" holds because the pages that *would* carry a contradiction were the ones fetched. Where a theme declares no page set for a class, verification for that class is **not performed and is recorded as not-performed**, which is honest and is not the same as observing agreement.
- **The comparison itself is node N-13** in §1.5's inventory, with a per-call token ceiling from §5.4a, a fail-closed-to-not-observed failure mode, and the same posture §2.7 applies to every other externally fetched text: **quoted data with provenance tags, never instructions**. Fetched page content is adversarial input for the same reason a collected post title is.
- **Whole-site semantic sweeps, if ever wanted, are event-driven and out of the per-run path** — triggered by a claim-ledger edit or a capability-statement change, not run nightly. **Event-driven triggers** force a full re-pull regardless of TTL: theme-readiness validation ran, the theme config's content hash changed, a human rejected a pack citing a wrong brand fact, a claim check produced a contradicted verdict, a CTA URL returned 404, or a new offer status appeared. A **claim-ledger expiry sweep** lists claims expiring within the next 30 days in the digest — otherwise proof silently vanishes from content one day and nobody knows why the posts got vaguer.

**The offline snapshot** is the Notion-down path. The last successful FULL or PARTIAL snapshot is persisted append-only with several generations retained. A snapshot written during a MINIMAL or INSUFFICIENT run is **never promoted to last-good**, otherwise degraded state ratchets forward. Running from a snapshot **caps the band at MINIMAL, always** — you cannot know whether the world changed while you were blind, and the cap is what makes the offline path safe rather than merely convenient. The maximum offline window is configurable **for interactive runs only** (recommended 14 days) and is independently capped by the hard-stale thresholds of the facts inside it. **There is no unattended offline window, because there is no unattended offline path**: MINIMAL is below PARTIAL, so §6.5's first degrade condition fires on any unattended run resolving from a snapshot, whatever its age (§6.5 is the single owner of that rule). **A snapshot failing its integrity check is treated as absent, never as best-effort.**

The realistic 3 a.m. outage behaviour is therefore: research and ranking complete, no brand content, digest explains exactly why, nothing spent.

**The brand-truth snapshot per pack** carries the normalised fact set with per-fact source, observation time and confidence; the computed band and its gate results; all conflicts including quarantined ones; the claim-ledger version; the theme-config version; and the **resolver rule version** — because precedence and thresholds change over time and a snapshot without its rule version is not reproducible.

**Two identifiers, not one** (C6 §6.3). A **content hash** over the canonically ordered, normalised fact set — hashing semantic content rather than serialisation, or trivial key-order churn manufactures spurious "the brand truth changed" events and destroys the signal. And a **fact-usage trace**: the list of fact identifiers and claim-ledger entry identifiers that *this specific topic pack* actually consumed. The hash proves integrity; the trace enables recall. **The trace implies a prompt-assembly requirement worth stating at the point it is created rather than discovering during implementation:** facts are injected into prompts as an **identifier-tagged set**, not as rendered prose, because a trace can only record what was consumed if consumption was addressable. This is cheap when designed in and a rewrite when retrofitted — which is precisely the plan's own stated reason for naming such things early. The question an operator genuinely asks six weeks later is not "was the snapshot intact" but **"we just corrected the trial length — which published packs are affected?"** That is a lookup by fact, answerable only if consumption was recorded per pack. It is the highest-value auditability feature in this layer and it costs almost nothing to record.

Every pack also shows **the age of the oldest blocking fact it consumed** — a single honest number the operator can glance at.

### 6.7 The claim-safety verification substrate

**Two halves that must not be merged.** The **claim ledger** is what may be said; it is brand truth. The **claim gate** is what was actually said; it is a verification pass over generated bytes.

The gate runs over **every generated surface, in every language**: post bodies, hooks, captions, carousel slide text, on-image text, video scripts and spoken lines, alt text, blog copy, CTA text, and hashtags — a hashtag can carry a claim. The on-image and on-screen surfaces matter disproportionately, because a "300% ROI" graphic is exactly the artefact type that escapes text-only checking.

**Deterministic first, semantic second.** A pattern, dictionary and entity pass runs first and guarantees that no digit, currency token, entity mention or superlative escapes examination; a model pass then handles the classes that genuinely need semantics. **This ordering is a control-integrity argument, not an optimisation**: a model-only checker is non-deterministic and can be argued out of a block by the same model family that wrote the copy, and a component's self-assessment is not a control over that component.

**Bidirectional.** The substrate verifies both that forbidden content is absent *and* that required content is present. A missing mandatory disclosure is a defect of the same class as a false claim.

**Eleven check classes** (C6 §7.2), each with Czech-specific extraction requirements where they exist:

| # | Class | Rule | Czech specifics |
|---|---|---|---|
| 1 | **Numeric quantity** | Every number in a claim position must map to a ledger entry; numbers are classified claim versus structural, and **the default is claim — fail closed** | Czech number formats and inflected units need language-specific patterns |
| 2 | **Currency / price** | Includes "free" / "zdarma", which is a price claim. Allowed only if the exact value and terms exist at full confidence and the pricing policy permits stating them | Currency is postfixed; trial terms carry their own dependency |
| 3 | **Named entities** | **Four-way**: own brands and domains allowed; own-team persons from the allowlist allowed; client and customer names blocked unless in the proof allowlist with granted, unexpired permission; third-party and competitor products allowed as **neutral references only**, with any attached performance or comparison assertion escalating to class 8; **unknown entities blocked** as a hallucination tell | Declension of brand names must be handled or the matcher both misses real mentions and over-flags inflected ones |
| 4 | **Outcome / result** | Requires a ledger or proof entry — **including number-free forms** ("we consistently book meetings"). Empty ledger means all outcome claims blocked and generation steered to teaching framing | The highest-volume leakage class from the competitor corpus |
| 5 | **Superlative / absolute / uniqueness** | Blocked by default; permitted only with an explicit substantiated entry | The Czech superlative lexicon is its own list, not a translation of the English one |
| 6 | **Capability / autonomy** | Checked against capability statements **positive and negative**; a claim contradicting the does-not list is *contradicted*, not merely unsupported | Catches false claims containing zero numbers |
| 7 | **Temporal / availability** | Requires a dated event or availability fact; also catches manufactured urgency | The event CTA class lives here |
| 8 | **Comparative / competitive** | Requires a comparison entry with evidence and an observation date; otherwise degrade to neutral positioning | Legitimately common, because one real ICP segment is defined by competitor tools |
| 9 | **Endorsement / social proof** | Requires a proof entry with permission. **Logos count** — an image-only endorsement is still an endorsement | — |
| 10 | **Required-statement (bidirectional)** | Fails if a mandated statement is *missing*: affiliate or discount disclosure, entity disclosure, AI-content labelling, and — as a named sub-class — **commercial-communication recognisability** (see below) | The affiliate arrangement in the real strategy triggers this |
| 11 | **Corpus leakage** | Numbers, metric phrases and named entities appearing in the exemplar corpus but nowhere in the ledger are **blocked**, and the overlap is recorded as a leakage event | See §6.10 |

**Verdicts:** *verified* (matches an in-scope, unexpired entry) · *safe-non-claim* (classified structural or self-referential) · *unsupported* (claim-shaped, no match) → blocks · *contradicted* (conflicts with a resolved fact) → blocks **and raises a brand-truth review flag, because it may mean the ledger itself is wrong** · *disclosure-missing* → blocks until inserted.

**Enforcement ladder, per asset:** block and record the offending spans → **bounded regenerate** (recommended maximum two attempts, each fed the specific failing spans *and a positive constraint* naming what may be said instead) → **downgrade repair**, emitting the claim-free variant of the asset with no proof and a softer CTA, which converts a hard failure into something publishable → drop the asset with the reason recorded and the rejected draft attached. **Never silently ship, never silently discard without a note.**

**Check class 10's recognisability sub-class, and why it needed naming.** The plan implemented one half of the Czech advertising-and-consumer-protection exposure exemplarily — misleading and unverifiable claims, eleven check classes, five of them non-disableable — and did not implement the other half: that **advertising must be recognisable as advertising and not disguised as other content**. Class 10 named affiliate disclosure but nothing defined *what wording*, *in which language*, *for which destination*, *for which relationship*; the "compliance obligations" knob was an enablement flag with no catalogue behind it. The sub-class fixes that with a **statement catalogue indexed by (language × destination × relationship type)**, where relationship type is *owned brand · affiliate · paid partnership*, holding the literal approved wording for each cell, maintained beside the CTA phrase bank and owned by the same person. The check is bidirectional like the rest of class 10: an asset whose relationship type requires a statement and lacks it is **DISCLOSURE-MISSING and blocked until inserted**. The platform-side mechanics that must *also* be set by hand — branded-content and paid-partnership controls, per destination — are mapped in §3.3 alongside the AI-label mechanics, because they are the same manual obligation in a different regime. The underlying statutes are cited from the evidence pack at medium confidence and their primary text is unverified, which is carried honestly as **OD-25** rather than asserted (§16); the control is warranted regardless of how that verification lands, and the risk is genuinely low while everything is organic content on owned accounts — it becomes real exactly where the plan already says it does, at the affiliate arrangement.

**The retry allowance is per pack, not per asset** — otherwise an unattended run with a systematically bad prompt burns its budget on a regeneration storm. This counter has a name, **the claim-retry budget**, and it is one of four distinct regeneration counters enumerated together in §4.9 so that no section can refer to "the regenerate cap" ambiguously again. Exhausting the pack allowance degrades that pack to review-required rather than failing the run.

**Five check classes may never be disabled** — numeric quantity, currency, named entities, endorsement, and required-statement — because those are the classes whose failure is a legal exposure rather than a quality miss.

**The claim gate runs twice** (D-16). Pass 1 runs early and fails fast, before expensive downstream steps. Pass 2 is the **final, immutable gate on the exact bytes that enter the pack**. This is not belt-and-braces: the voice gate *rewrites text*, and a rewrite can reintroduce a claim the early pass cleared. **Any gate that runs before a rewriting step must be re-run after it.**

The per-asset claim-check log doubles as regulatory-defensibility documentation, because Czech consumer-protection law prohibits misleading and unverifiable factual claims independently of any brand-voice preference (C7 §2.9).

### 6.8 Spoken claims — the F-5 consequence

**Script-lock is the primary control; speech recognition is a sampled adherence monitor, never a per-asset gate** (D-16, C6 §8).

1. **Spoken content is generated only from claim-checked script text.** The script is a first-class verified artefact; audio is a rendering of it.
2. **In unattended runs, spoken lines carry no claim-class tokens at all** — no numbers, currency, entities beyond our own brands, superlatives or outcome statements. **All claim payload lives in burned-in on-screen text composed at assembly time from verified strings**, and can be re-read before packaging. The audio channel is deliberately drained of claim payload, so model improvisation cannot fabricate anything that matters.
3. **Speech recognition runs as a monitoring signal** — on every audio asset during the first weeks, then a rolling sample, and always after a provider or model change — measuring *adherence*: did the model say what it was told? A measured adherence drop is a provider-level alarm that can disable audio for that route.

Four reasons this ordering is correct rather than merely convenient: **preventive beats detective**, and under budget caps the worst place to discover a bad claim is after paying for the render; **it reuses a stronger substrate**, since the claim gate already operates deterministically on text and script-lock means the spoken words *are* that text; **it is language-neutral**, whereas a recognition-based gate whose accuracy varies by output language would over-block Czech until it got relaxed and under-block Czech through dropped numbers; and **the failure direction is right** — recognition's characteristic failure is *dropping* content, and a dropped claim in a transcript is a false pass, the worst possible direction for a safety gate.

Script-lock's own honest failure mode is that adherence is a behaviour, not a guarantee: a model may paraphrase or ad-lib. Rule 2 is what makes that drift non-consequential, and where claims genuinely must be spoken, the dedicated text-to-speech path — which reads exactly the verified string — makes script-lock effectively airtight.

### 6.9 Spin application

**Pain-to-offer mapping is a configured relation, not an inference** (C6 §9.1). Ranked topics arrive carrying a detected pain signal; the mapper performs a lookup over (ICP segment × pain category) → (offer, preferred CTA class, owning brand and domain, preferred formats). **If nothing matches above threshold, the correct answer is no offer** — and the topic can still become genuinely good content with a content CTA or none at all. This is the anti-forced-placement mechanism at the *brand* layer; the ranking layer's multiplicative composite is the mechanism at the *topic* layer. Both are needed and they are complementary: ranking decides whether to touch a topic at all; spin decides whether an offer may be attached to it.

**Mapping distance is an explicit, recorded property that governs how loud the offer may be:**

| Distance | Meaning | What the asset may do |
|---|---|---|
| **Direct** | The topic *is* the pain this offer addresses | Offer named, one capability sentence, product CTA |
| **Adjacent** | Same ICP, related workflow, different problem | Offer mentioned once, soft CTA only, no capability elaboration |
| **Far** | Same audience, unrelated problem | **No offer, no product CTA.** Value content with a content CTA or none |

**Mapping distance is platform-aware, because the same distance reads differently per destination.** A far-distance topic on LinkedIn or the blog is thought leadership and lands well: pure value on an adjacent pain, no pitch, authority earned. The identical asset on TikTok, Reels or Shorts is fifteen to thirty seconds that names a problem, offers nothing and asks for nothing — the viewer is left suspended, and the spin gate will not catch it, because S-3 and S-4 check that the *offer* is not forced and say nothing about whether the *format* expects utility. So each destination carries a **minimum mapping distance** in its format profile (§3.3): short-form destinations default to **adjacent-or-closer**, and a far-distance topic may be routed to a short-form destination only when the asset carries a named **soft bridge** — an explicit next step that is not an offer (a resource, a follow-on, a specific question), declared in the spin rationale and visible to the platform gate. LinkedIn, Facebook and blog keep no minimum. This is a per-theme knob with those defaults, not a hard-coded rule, because a theme whose audience genuinely rewards pure short-form education should be able to say so — deliberately, in configuration, rather than by accident.

**CTA correctness has preconditions on brand facts** — this is what makes CTA classes worth having rather than one flat list:

| CTA class | Preconditions beyond the general ones |
|---|---|
| **Content** (guide, article, resource) | The resource exists and its URL resolves |
| **Product-path** (product page, trial, demo) | Offer status is live; destination URL verified within the freshness window; band at least PARTIAL for the page and FULL to state trial terms |
| **Event** (webinar) | A dated event fact with a registration URL exists and the date is in the future. **No event fact, no event CTA — ever.** A webinar CTA is a promise that an event exists |
| **Commercial-incentive** (affiliate share, discount code) | Programme facts resolved — a stated revenue share is a *number* and therefore a claim — **and** the required disclosure statement present |

General preconditions for every CTA: **exactly one per asset by default**, no stacking; the class is allowed at the current band; **brand routing is coherent**, so a product CTA points at the product domain and an agency-service CTA at the agency domain — the **wrong-brand-CTA defect class**; and **CTA-language coherence** — if a Czech asset's destination page has no Czech version, either the CTA changes or the asset says so. That last rule is a direct D-02 consequence and a live risk while both domains are being built out bilingually. A degraded Czech CTA is a normal, expected state, not an error.

**Product rules and the site-first hold** (C6 §9.3). For topics mapped to a site-first offer, the canonical asset is a page or article on our own site and the social assets are atomisations pointing at it. In a pipeline that cannot publish the site itself, that creates a concrete hazard: the system will happily write five social posts pointing at an article URL that does not exist. The default is therefore to **hold the social atomisations in the pack as blocked-pending-article, with the article draft included**, so the operator can publish the article and release the social set as one action. Config may instead select generating the social assets with a non-article CTA — but the hold is the default, because the alternative quietly discards the product rule's whole purpose. Long-form site content carries more claims per asset and requires the FULL band, whereas PARTIAL suffices for social value content. Under the drafts-only blog scope recommended at OD-14, the hold is released by the operator publishing the article manually.

### 6.10 The spin gate — distinct from the voice gate

The assignment's good-versus-bad-spin definition is qualitative. It becomes enforceable by decomposing it into seven binary criteria, each recording the evidence for its verdict (C6 §9.4):

| # | Criterion | Fails when |
|---|---|---|
| **S-1** | **Real topic anchor** — traceable to a specific research artifact | *Trend dump* or evergreen filler. The operational test: **could this asset have been written yesterday without this topic?** If yes, it fails |
| **S-2** | **ICP addressing** — names a recognisable situation for a *configured* segment | Addresses "businesses" or "teams" generically |
| **S-3** | **Connection chain** — an explicit, checkable bridge from topic → consequence for that ICP → why the offer is relevant | *Random product mention*: the offer appears with no bridge sentence |
| **S-4** | **Distance compliance** — offer prominence matches the mapping distance | *Forced relevance*: a far-distance topic carrying a product pitch |
| **S-5** | **Proof discipline** — no proof-*shaped* statement without a ledger entry, including implied results | *Invented commercial proof* — the shape-level sibling of check class 4 |
| **S-6** | **Next-step correctness** — at most one CTA, of an allowed class, correctly routed and language-coherent | Stacked CTAs, wrong domain, dead link, event CTA with no event |
| **S-7** | **No hype-glue** — the bridge survives removal of connector inflation ("this is exactly why…", "which is precisely the problem we solve") | Forced relevance disguised as a transition |

Enforcement: fail → bounded regenerate citing the specific criterion → second failure → **downgrade to the value-only variant** (drop the offer, keep the insight, content CTA) → still failing → drop the asset with the reason recorded. **The value-only downgrade matters**: most spin failures are failures of the *pairing*, not of the writing, and the correct repair is usually to stop selling rather than to rewrite harder.

**The spin gate is architecturally separate from the voice gate, and precedes it**, for three reasons (C6 §9.5): their repairs differ — a voice failure is fixed by rewriting phrasing, a spin failure by dropping the offer; polishing the prose of a structurally wrong asset wastes regeneration passes and budget; and **a well-voiced piece of forced relevance is harder for a reviewer to reject than a clumsy one**. Keeping them separate also keeps their failure reports separately actionable.

**Every asset records its spin rationale**: topic identifier, detected pain, segment, mapped offer, mapping distance, CTA class, and the fact-usage trace. That is what an operator reads to judge "was this a natural connection?" in seconds, and it is what makes the gate auditable rather than a black box.

**The spin gate's position in the chain is fixed and is drawn once, in §14.** It runs after generation and before claim pass 1, and its artifact-level post-check is re-entered whenever a later gate rewrites the text. That is all this section needs to assert about ordering; the full chain — including the platform gate, the cost gate, assembly, the post-assembly overlay claim pass, the asset QA rubric and packaging — belongs to §14, **because a chain drawn in two places becomes two different chains, and this one already had.** The version this section carried was the most complete of the three and still should not have existed: completeness is not ownership.

**Repair re-entry, stated as a rule rather than left as a loop nobody drew.** §6.7 states the governing principle — *any gate that runs before a rewriting step must be re-run after it* — and that principle was applied in exactly one direction and then broken. A **bounded regenerate at claim pass 2 is itself a rewriting step**: it produces new prose the voice gate has never seen, and it can equally weaken the S-3 connection chain the spin gate cleared. Shipping that text meant shipping an artifact whose slop control and whose spin honesty were both performed on a superseded draft. The rule:

- **A claim-2 repair re-enters the voice gate and the spin artifact-level post-check**, in that order, then returns to claim pass 2. The last gate before packaging still sees the exact bytes that ship, which is what pass 2 is for.
- **One combined per-artifact repair ceiling counts every repair across every gate** — spin, claim pass 1, voice, claim pass 2 — so the re-entry cannot become an unbounded cycle between two gates that each individually think they are within budget. The individual counters in §4.9 still apply inside it.
- **Exhaustion routes to the downgrade-repair variant, never to another lap**: the claim-free, proof-free, softer-CTA version of the asset, which is a publishable outcome rather than a failure. If that variant also fails, the asset is dropped with the reason recorded and the rejected drafts attached.
- **For media assets, pass 2's "final on the exact packed bytes" needs the qualifier §4.4 supplies**: for a video or image the bytes that enter the pack are pixels and audio, and the claim-bearing on-screen text is composed at assembly, *after* pass 2 closes. The post-assembly overlay claim pass — positioned in the chain at §14 and specified at §4.4 — is what makes the claim "final on what ships" true for media as well as text.

### 6.11 The exemplar corpus as a first-class theme asset

Every theme owns a **per-language exemplar corpus**: curated reference material that teaches the system what this brand's writing *sounds like*. For theme #1 it is seeded from `docs\marketing\` — a competitor winning-posts file, a GTM playbook, practitioner transcripts and an outreach playbook. It is a named configuration block, versioned with the theme, and it grows over time; theme exemplars outweigh the engine's generic seed set once a theme has run enough cycles.

**The standing normative rule, binding on every later author (D-15): the exemplar corpus is style-only and never a fact source.**

This is not fastidiousness. The local corpus is dense with *other people's* commercial claims — a dozen demos in five days, response rates in the tens of percent, hundreds of leads from one search, seven figures added in a quarter, and the literal word "Guaranteed." It is correctly used as the few-shot grounding for the English voice rubric, and that is precisely why **it is the highest-probability fabrication source in the entire system: the generator is being shown these numbers as examples of good writing at the exact moment it writes.**

Four rules follow:

1. **The corpus feeds style retrieval only.** It is excluded from every retrieval path that answers a factual question, and the claim ledger is never populated from it.
2. **A dedicated corpus-leakage check class** (class 11) compares generated numbers, metric phrases and named entities against corpus content and blocks any overlap lacking a ledger entry — **recording a leakage event**, because a rising leakage rate is the signal that the few-shot design is bleeding facts.
3. **Where an exemplar's structure depends on a metric, the pattern is abstracted before use.** "Open with a specific outcome number" is a structural instruction; the number itself is never carried.
4. **Borrow the craft, reject the tone.** Several of the corpus's best-performing posts use hype absolutism and gamified hard CTAs that this project's own rules forbid, and calibrators must be told this explicitly, so that "but the real post did X" cannot be used to argue down a legitimate flag.

Worth recording: the operator already applies this discipline manually — the GTM playbook tags every third-party figure with a distinct marker and phrases it as *their* claim. The system is formalising an existing instinct, which is the easiest kind of control to get adopted.

### 6.12 Czech behaviour in this layer

- **Facts are language-scoped**, and a claim approved in English is not approved in Czech.
- **Confidence is per (theme, language)**, so the Czech set degrades independently.
- **Extraction must be Czech-aware**: number and currency formatting, diacritics, and declension of brand names — without declension handling the entity matcher both misses real mentions and over-flags inflected forms. The superlative lexicon is its own list.
- **Site verification is asymmetric**: either domain may lack Czech pages for some offers, which is exactly the CTA-language-coherence rule.
- The Czech voice lexicon and judge rubric belong to the language overlay (§3.4); this layer only requires that the **fact and claim layers be per-language rather than translated**.

**Knobs this section contributes to §10.** Brand-truth source pointers, including which Notion locations are designated fact locations, per fact class; access path per context; site-verification URL set, fetch budget and timeout; **the declared verification page set per fact class for capability and claim-ledger checking**; freshness stale-warn and hard-stale thresholds per fact class; **maximum offline window, interactive runs only**; band floor per mode; the claim-ledger pointer; the hard-excludes baseline list in config; **the special-category source deny-list**; **the commercial-communication statement catalogue pointer per language, destination and relationship type**; **the recipient map**; check-class enablement with five classes non-disableable; the claim-retry budget per pack **and the combined per-artifact repair ceiling**; the pain-to-offer relation; mapping-distance policy per offer **and the minimum mapping distance per destination**; CTA class enablement per destination per language and the CTA phrase bank pointer per language; site-first offer list and the hold-versus-substitute choice; the person allowlist; the brand-and-domain routing map; ASR sampling rate and the adherence-alarm threshold; exemplar corpus pointer per theme per language; corpus-leakage sensitivity; resolver rule version; TTL for snapshot reuse; the event-driven refresh trigger set.

### 6.13 Hand-offs from the core pipeline into the rest of the plan

The six sections above establish the spine. Everything after them consumes it rather than restating it, and this table is the map.

| Established in §1–§6 | Consumed by |
|---|---|
| Stage sequence and the per-asset gate order (§1.3, §6.10) | The two end-to-end flows (§9) and the enforcement chain (§14) |
| The outcomes named here — pending media, budget-capped mid-pack, research-only degrade | The nine-class exit-code taxonomy (§8.8) |
| Per-source ladders and staleness flags (§2.2, §2.3) | Degraded-source reporting in the run pack and digest (§12.1), notification escalation (§8.12), and per-stage idempotency keyed on source and run-date (§8.5) |
| Retention windows and targeted deletion (§2.6) | The research artifact store's substrate and operational rules (§8.6) |
| Per-asset AI-content class and the burned-in disclosure (§3.3, §4.4) | The publish gate's readiness precondition (§7.7) and the compliance treatment (§14.6) |
| Cost gate, tiers, caps and the dry-run boundary (§4.6, §5.4) | Budget enforcement under a scheduler including mid-pack cap-hit (§8.11), the mode capability resolver (§11.2), and the operator-facing forecast (§12.3) |
| Write-ahead spend ledger, the `submitted-unknown` state and re-host discipline (§5.5, §5.6) | The ledger set and the async job lifecycle, which own their design (§8.5, §8.6, §8.13) |
| Confidence bands, the degrade trigger and the brand-truth panel (§6.5) | Fail-closed triggers (§11.3) and the digest header (§12.1) |
| Claim gate double pass, spin gate criteria, corpus-leakage class (§6.7, §6.10, §6.11) | Voice and claim-safety enforcement by design (§14) |
| Every knob roster closing §1–§6 | The theme configuration surface (§10) and theme-readiness validation (§13.2) |

---

## §7. Distribution architecture

Distribution is the last stage before a human decides something goes live. Nothing in this section changes that: the publishing bridge (Postiz) creates drafts and never publishes (canonical provider role, SYNTHESIS §4.8); a human always performs the schedule/publish action inside the bridge itself, and a human always merges blog/site content. This section covers how drafts get created safely, what happens when that path is unverified or broken, and the one enforcement point that keeps research-only surfaces from ever becoming publish targets.

### 7.1 The publishing bridge: draft-first, paper-based today (OP-2)

No Postiz account exists yet (D-04, OP-2). Every capability claim in this subsection is a **documentation claim** from C1, not yet verified against a real account — C1 itself flags this explicitly. This architecture therefore treats Postiz's positive findings (draft status with no schedule date, drafts persisting until a human acts, full cloud/self-hosted feature parity, broad connector coverage of List B destinations, an official MCP surface) as the *paper* design, and makes **capability verification an implementation-phase acceptance criterion**, not a design assumption (§7.8).

The correct default pattern, once verified: after the human review gate (§11, §12) is satisfied for a given asset, distribution prep creates a draft in the publishing bridge for each allowlisted, connected destination named in that asset's plan. The pipeline's own responsibility ends at draft creation — or ends earlier still, at a lower rung of the fallback ladder below, if draft creation is itself unavailable.

### 7.2 The fallback ladder (first-class, not an afterthought)

Because OP-2 leaves Postiz's real behavior unverified, and because the assignment requires the plan to cover this honestly, distribution prep is designed against a three-rung ladder. Every rung is independently usable; the ladder never falls through to an unsupported or silent action, and descent from one rung to the next is logged with the reason (the same ladder grammar used throughout collection, §8.5, and media generation, §8.13 — primary → degraded → floor, each rung legitimate on its own terms).

| Rung | Mechanism | Operator friction | When it is used |
|---|---|---|---|
| 1 — primary | Unscheduled draft created via the publishing bridge's own draft state (no schedule date attached) | Zero — this is the built-in workflow | Default rung whenever the bridge is reachable and draft creation succeeds |
| 2 — degraded | A scheduled post created with a date set far enough in the future that it is inert in practice, pending a human moving the date forward | Low — a date change is required before the post could ever go live | Used only if rung 1 is verified broken (draft-without-schedule fails on the real account) or degrades mid-run |
| 3 — floor | Local-only staging: the fully composed per-platform content is written into the run pack for manual per-platform paste, with no call to the publishing bridge at all — **carrying its own unchecked per-platform label checklist, applied at packaging** | High — one paste per platform per asset, plus the labels | Always available regardless of the bridge's health; the guaranteed fallback that makes distribution never depend on Postiz being up |

Rung 3 is never removed once the bridge is proven reliable — it remains the honest floor for any destination the operator has not connected, and for any run where the publish gate (§7.4) blocks a destination outright.

**Rung 3 used to bypass the label acknowledgement entirely, and that is now fixed at packaging rather than at the gate.** The publish gate hung on a call to the publishing bridge; rung 3 makes no such call by definition; so the separately-recorded AI-label acknowledgement (§7.7) never fired on the one path that is *always* available and is explicitly where gate-blocked content lands. The consequence was not theoretical — rung 3 is the destination for every unconnected channel and for every asset the gate blocks, so the busiest failure path was the unlabelled one. Two things close it, and the first is the load-bearing one:

1. **The label checklist is produced at packaging, not at the gate, and travels with the artefact.** Any asset whose AI-content class is not `none` is written into rung-3 staging **with an unchecked, per-platform, per-post checklist line in the same file the operator will paste from** — naming each platform's own label mechanism and leaving a box that is visibly not ticked. The operator publishing by hand sees the obligation in the artefact they are pasting, not in a gate they never crossed.
2. **§7.4's trigger is restated below** from "before any call reaches the publishing bridge" to "before any distribution preparation", so the gate's own scope covers rung 3 rather than excluding it by construction.

Honestly stated, because it bounds how bad this was: **the burned-in disclosure was never at risk** — it is a precondition of publish-ready at assembly and packaging (§4.4, §4.4a), so the EU-law exposure stayed covered on every rung. What was skipped was the *platform-contractual* label layer, and the claim that there is a single fail-closed enforcement point (F-4, D-23), which was untrue on this path and is true again now.

### 7.3 Blog/site prep path

Config-gated per theme via a **blog/site prep enablement** knob (output/runtime config block). Per the operator's v1 scope decision (OD-14), this path is drafts-only: when enabled, an approved long-form piece is produced as a run-pack artifact — an article draft — and no site-publishing integration is built. A human merges/publishes the article manually, exactly as a human schedules/publishes from the publishing bridge; there is no automated equivalent of "distribution prep" for a production site merge in any mode (§11 makes this a permanent "never," not a mode-gated capability).

Long-form content carries materially more claims per asset than a social post, so the article artifact is held to a stricter confidence-band requirement than social atomizations of the same topic (band requirement owned by §6.5; referenced here only for its distribution-side consequence). Where a theme's product rules mark an offer site-first (fact class F-K, §6.3, and the site-first hold rule, §6.9), that topic's social atomizations are held inside the pack pending the article's existence; releasing the hold is a single deliberate operator action, taken once the article has been manually published on the brand's own site. This keeps the site-first rule's whole purpose intact rather than quietly discarding it the moment social assets are ready first.

### 7.4 Publish-destination allowlist: one enforcement point, five-layer defense-in-depth

Per C1 §9 and the locked decision D-23: **the publish gate is the single fail-closed enforcement point** for mode × publish allowlist × human-approval state. Every other layer below is defense-in-depth around that one point, not a second place where the decision could independently be made differently (F-4; RA-8).

1. **Config allowlist per mode.** The **publish allowlist** (canonical config block, SYNTHESIS §4.6) declares, per mode, exactly which content destinations are permitted at all. In test mode this set is empty by construction — publishing is wholly disabled regardless of what a theme's output/runtime block otherwise enables.
2. **Connected-channel gating.** Only destinations present in the current mode's allowlist are ever initialized as publishing-bridge integrations in the first place. A destination the operator has not connected simply does not exist as a callable target, independent of anything else.
3. **The publish gate itself.** It consumes the **mode capability resolver**'s answer for publish-type effects (§11.2) rather than re-deriving mode rules, and then layers five further checks on top. **The gate fires before any distribution preparation — not before any call to the publishing bridge** — which is the wording that keeps rung 3, local-only staging, inside its scope rather than outside it by construction. The publish gate checks:
   - is this destination in the active mode's allowlist;
   - is it actually connected;
   - does the review-decision store hold a recorded human-approval state for this asset (§11), naming the approving person and the holder of editorial responsibility (§3.3, §11.4);
   - for any asset whose AI-content class requires disclosure, has the AI-label acknowledgement (§7.7, §14) been recorded — and on rung 3, has the packaging-time label checklist been emitted with the artefact (§7.2);
   - **is the per-asset provenance record complete — all four items — and is the delivered route's rights class inside the rights-class allowlist for this destination.**
   - **does the approval fingerprint recorded for this asset match the asset's current packed bytes and current pack revision** (§11.4) — an asset whose bytes changed after it was approved is **unapproved**, not approved-with-a-caveat.

   Any failure here is fail-closed: nothing is prepared and nothing is sent.

**Why provenance is a gate check and not merely a pack field.** D-20 records the per-asset provenance and licence snapshot as a publish-gate *precondition*, and the evidence pack is unambiguous that an asset missing that record should fail the ready-to-publish gate as **a hard block, not a warning** — because upstream model providers of this router class hold third-party-beneficiary rights enforceable directly against us while the router disclaims its own. The plan collected exactly the right four items and resolved them at the right moment (after completion, not at submission), and then never said that an incomplete record blocks anything: §7.4's enumerated checks, §11.3's fail-closed triggers and Appendix A's replay all omitted it, so an asset that had been silently substituted and whose rights class could not be resolved would have passed. It now fails, with the disposition §5.6 defines — degrade to plan-only with the reason attached, not an undisposed permanent block — and Phase 3 carries a negative test: an asset with a deliberately damaged provenance record does not reach publish-ready (§17).

**Why the approval is checked against bytes and not against an identifier.** The gate previously asked only whether the review-decision store held a recorded approve decision for this asset, and the store keyed decisions by run id and asset id — while three separate mechanisms are designed to change an asset's bytes after review: pack amendment when a later run completes a pending master (§4.7a), regenerate-media-only completion of a budget-capped pack (§8.11), and the immediate loop's in-place segment regeneration (§12.4). **The failure this closes is not hypothetical and does not require anybody to make a mistake.** The operator batch-approves a pack at revision 1 — §12.1 makes whole-pack approval the default affordance and pre-selects high-band topics — while the English video master is plan-only, blocked on one clip. Overnight, unattended, the pipeline adopts the clip, assembles, masters and amends the pack to revision 2. With the unattended draft-creation knob on — **whose stated precondition is precisely that a human-approval state was already recorded in an earlier interactive session for that asset (§7.6)** — the old gate finds an approve against that asset id and prepares drafts for a video no human has ever watched. Every layer of the defence-in-depth in this section held: the mode was right, the destination was allowlisted and connected, the provenance was complete. The approval was the layer that was wrong, and it was wrong because it pointed at a name rather than at a thing. Disposition matches every other check here: fail-closed, nothing prepared and nothing sent, with the pack naming the asset and the reason as *approval superseded by revision N — re-approval required*.

4. **The publishing bridge's own draft state.** Even a call that reaches the bridge only ever creates a draft (§7.1) — there is no code path in this architecture that ever requests immediate publish or a schedule date inside the live window.
5. **The human review gate.** The human decision recorded before any of the above (§11, §12) is itself a precondition the publish gate reads, not a formality that happened earlier and is trusted implicitly.

**Research sources never appear in this allowlist and are never connected as channels at all** (F-4). This is a structural fact, not a runtime check: Reddit, Product Hunt, the ad libraries and every other research-only surface from List A (§2.3) have no corresponding entry in the connected-channel set, in any mode, ever — there is nothing for a missed check to accidentally enable.

**Named failure mode.** If a destination is present in the allowlist but the operator has not actually completed the publishing bridge's connection for it, the run fails closed for that destination alone: the run pack names exactly which destination is blocked and why, and the operator is offered the honest choices (complete the connection and re-run, remove the destination from the allowlist, or accept the pack with that destination absent). There is no silent skip and no silent substitution to a different, unrelated destination (C1 §9).

### 7.5 X-as-publish separation (F-2)

Two independent decisions live on the X/Twitter surface and must never be conflated in this architecture. Whether X reads feed the research layer is a List A decision, closed for v1 (D-08). Whether X is an allowlisted publish destination through the publishing bridge is a separate, later-phase List B decision. Enabling X as a publish destination neither requires nor implies X read access, and the reverse is equally true. If X is ever allowlisted, the diligence item is on the vendor, not on this pipeline's own compliance posture: confirming the publishing bridge's own X integration operates through X's official, paid API path rather than anything scraping-adjacent — a vendor's compliance failure on that surface would become an availability risk for us, not a legal one, but it is worth naming explicitly before X is ever connected.

### 7.6 Never-live-by-default, mode by mode

- **test** (default): every publishing-bridge side effect is refused outright, before the call is even attempted — this is independent of allowlist contents, because in test mode the allowlist is empty by construction (§7.4, layer 1).
- **staging**: draft creation only, for allowlisted-and-connected destinations, and — for unattended runs specifically — only if the **unattended draft-creation** knob (below) is explicitly on.
- **live-prep**: production-ready drafts prepared for every enabled destination, still never auto-published and never auto-scheduled into the live window; the difference from staging is completeness of preparation, not permission to go further.

The cadence knobs in §8.2 govern *when* a run happens; a separate **unattended draft-creation** knob (output/runtime config block, per theme) governs whether a run happening unattended may create publishing-bridge drafts *at all*. Default off. Even when on, it only ever authorizes draft creation (never a publish/schedule action) and remains fully subject to every layer in §7.4 — turning this knob on does not bypass the publish gate, it only permits distribution prep to be attempted without a human present at that exact moment, provided a human-approval state was already recorded during an earlier interactive session for that asset (§11).

### 7.7 The AI-label gap and the publish-gate acknowledgement

Per C1 §7 and the recorded risk W2-05: the publishing bridge exposes **no per-platform AI-disclosure fields** — no TikTok AIGC toggle, no YouTube synthetic-media property, no Meta AI-info control (confirmed against Postiz's public API and MCP surface, C1). This means the publishing bridge cannot itself carry the compliance flag described in full in §14; setting the platform-native label is a manual human action taken in each platform's own interface, after a draft already exists.

Design response, owned jointly by this section and §14: every asset whose AI-content class requires disclosure carries an **AI label required** flag, visible as a named checklist item in the run pack (§12). The publish gate refuses to treat that asset as "ready" until the operator has given an explicit, separately recorded acknowledgement of that flag — this acknowledgement is not folded into the general approve/reject decision, because bundling it is exactly how the busy-operator-skips-it failure mode in W2-05 happens in practice.

### 7.8 Implementation acceptance criteria (deferred to build, explicitly not a design assumption)

Because OP-2 leaves the publishing bridge unverified, the following must be confirmed against a real account before this section's rung 1 (§7.2) can be trusted as the everyday path, per C1's own open items and the synthesis's W2.5 recommendation:

- unscheduled-draft creation actually succeeds, for a batch of posts, with no auto-publish trigger ever firing;
- draft state persists across a service restart of the publishing bridge;
- draft-to-schedule and schedule-to-draft transitions both work as documented;
- drafts are visible in the bridge's own review surface for a human to act on;
- whether any per-platform AI-disclosure field has appeared since C1 was written — worth re-testing specifically, since this is exactly the kind of capability a vendor adds quietly (C1 §7).

Until these are confirmed, rungs 2 and 3 of the fallback ladder are treated as equally load-bearing, not merely theoretical.

---

## §8. Scheduler and cron architecture

### 8.1 One entrypoint, two invocation modes

The console application has exactly one entrypoint capable of running the full pipeline. Whether it is invoked by an operator at the keyboard or by an OS scheduler with nobody watching changes nothing about which code executes — only the theme, mode, and any interactive overrides differ (the two paths are walked stage by stage in §9). This single-entrypoint property is what makes "cron-executable full pipeline" a fact about the one application, not a separate build artifact.

**Today: Windows Task Scheduler**, with the scheduled task always configured to run under **the operator's own user account — never SYSTEM** (C2 §2.6; D-11). Running as SYSTEM breaks two things simultaneously and silently: browser-automation installs live per-user and are invisible to SYSTEM, and any secret protected by the operating system's own per-user encryption cannot be decrypted by a different account. Both failures are the class of bug that works perfectly in an interactive test and then fails at three in the morning with no one watching (W2-20).

**Later: Linux**, via cron or systemd timers (D-05) — the choice between the two affects only the missed-run catch-up nuance (§8.4) and which secrets-hardening layer is available (§8.9); the pipeline's own behavior is unchanged, because the application treats the scheduler as nothing more than "something that starts the process" (C2 §2.7). Moving from Windows to Linux is a thin per-OS launcher rewrite, not an application change — the app owns its own encoding, paths, secrets access, logging, locking and exit codes throughout.

### 8.2 Cadence knobs: the conceptual split (W2.5-7)

The operator's own framing at the W2.5 checkpoint was: settable in config, default off, otherwise daily or weekly, with the exact shape delegated to the architecture. The recommended shape is **two independent cadence knobs**, not one, because research-collection and pack-production have different natural rhythms and different cost profiles:

- **research-collection cadence** — governs how often the collection stage alone runs (no media spend at this cadence; ranking and dedupe-index maintenance run alongside it). Recommended default once enabled: daily, because Hacker News and Bluesky are the only sub-24-hour-fresh surfaces in the v1 roster, and their signal decays within a day regardless of how often packs are produced (SYNTHESIS §2a Change 7, §5 topic-extraction brief).

**"No media spend at this cadence" is true and has been read as "no spend at this cadence", which is false.** The collection cadence runs the ranking stage, the ranking stage runs node N-1 once per surviving candidate, and N-1 is a model call. **Text spend therefore scales linearly with the research-collection cadence, and it is denominated per collection run — not per topic pack.** A theme collecting daily and producing packs twice a week pays the per-artifact text term twice a week and the per-candidate term **seven** times, and nothing in the economics the operator has been shown so far made those five extra ranking passes visible: every figure in §5.4 is expressed per two-language topic pack, and five of the week's seven ranking passes belong to no pack at all.

Two consequences follow, and both are stated as plainly as they can be because the arithmetic is otherwise invisible. **First, raising the collection cadence raises text spend proportionally** — this knob is a spend knob, and it has never been labelled as one. **Second, lowering the pack-production cadence does not lower the ranking term**, so an operator throttling packs to control cost will see less improvement than expected and may conclude the caps are not working. The per-day and per-month text caps are the controls that actually bound this, and readiness now measures the ranking term against them at the configured cadence (§13.2).

The design conclusion is not to collect less. Daily collection remains correct for the stated reason — spike-class signal decays within a day regardless of pack rhythm. The conclusion is that **the cadence knob's cost consequence is named at the knob**, and that the digest's text-per-candidate line prints on collection-only runs too (§12.1), so seven charges a week produce seven visible lines rather than one monthly surprise.

- **pack-production cadence** — governs how often the full pipeline runs through spin, copy generation, media planning and (budget permitting) media generation, packaging and notification. Recommended default once enabled: a small number of times per week rather than daily, because human video-review throughput — not topic availability — is the real bottleneck (20–30 minutes of operator QA per finished video, A1; SYNTHESIS §3.10).

Both knobs are **default off**: no scheduled runs of any kind occur until the operator makes an explicit enabling choice for each, per theme. Both accept a small named set of frequency options — at minimum daily and weekly, as the operator specified; a mid-frequency option (several times a week) is recommended additionally for pack-production cadence specifically, informed by the throughput reasoning above. A validation rule ties the two together: pack-production cadence should never be configured to run more often than research-collection cadence effectively refreshes signal, or packs would repeatedly re-rank the same stale collection window — this is a sanity check at theme-readiness time, not a runtime restriction.

Both knobs are per-theme (multi-theme is a first-class requirement elsewhere in this architecture), so one theme may collect daily and produce packs twice a week while another theme runs both knobs weekly.

### 8.3 Run identity and overlap policy

A run's identity is theme identifier + **run-date** (a pinned logical day, derived once at run start from a single configured theme timezone) + an attempt number distinguishing a manual rerun from the original scheduled attempt for that run-date (C3 §2.2). This identity is fixed once and carried unchanged through every stage, checkpoint and ledger row for the life of the run. Every stored timestamp is UTC internally; the theme timezone is used only to derive run-date and for human-facing display — this is what keeps a run from confusing "today" with "yesterday" when execution straddles midnight, and what avoids the documented daylight-saving double-fire/skip risk on both target schedulers when schedules are expressed in local time (C3 §2.2, W2-20).

**Overlap policy is skip-on-overlap.** If the run-lock is already held by a live run, a new invocation does not queue and does not kill the running instance — it logs and notifies a distinct **skipped-overlap** outcome (§8.8) and steps aside. Killing a running instance is explicitly rejected: it risks orphaning already-submitted, already-paid-for media jobs with no completing pipeline left to reconcile them against the spend ledger — exactly the "crash discards paid work" failure this whole design exists to prevent (C3 §2.2). A separate, explicitly operator-invoked "queue behind the current run" affordance exists for manual reruns only; the automatic scheduled trigger path never uses it.

**Locking is cross-platform and OS-mediated**: an exclusive lock held on a dedicated run-lock file for the life of the process — Windows exclusive file-open/share-deny and Linux advisory file locking are directly analogous, kernel-guaranteed-release-on-crash primitives (C3 §2.2). A ledger-recorded "in progress" row in the run ledger sits on top as a belt-and-suspenders check, independent of whether the lock file itself is trusted in a given edge case.

### 8.4 Missed-run policy: pipeline-owned skip-missed

Windows Task Scheduler and Linux systemd timers can both be configured to catch up a missed run; bare cron cannot (C2 §2.7, C3 §2.10) — a genuine cross-platform asymmetry. Rather than depend on whichever scheduler happens to be in use, the pipeline decides for itself: **missed windows are skipped, the pipeline runs once for "now," and the run ledger records how many windows were missed** (D-18's exit-code taxonomy carries this as a first-class fact, not a silent gap). This is deliberate on two grounds: content value decays with freshness (re-researching "what was viral three days ago" as if it were today's signal is a content-quality defect, not just an ops inconvenience), and a naive full-backfill policy risks a burst of consecutive, paid, automated runs firing back-to-back the instant a machine comes back online, with no pacing safeguard (C3 §2.10). OS-level "catch up a missed run" settings are harmless to leave enabled, since the pipeline's own run-ledger logic recognizes an unexpected extra invocation and applies the same skip-missed reasoning to it regardless of why it fired.

### 8.5 Idempotency and dedupe keys per stage

**Content-hash-based keys** are the identity mechanism for every cost-bearing stage: theme id + run-date + a stage-defined semantic input hash + the relevant config/prompt-template version (C3 §2.3). Natural keys (run id + stage name) remain a useful human-facing lookup index but are never the sole identity, because a same-day rerun after a deliberate brand-truth or config correction must be recognized as legitimately different work, not silently served from a stale cache.

Per-stage design: research/collection keys on theme + source + query/topic signature + run-date (or a configured rolling freshness window), so a retry recognizes existing raw captures for the run-date and skips or deltas rather than re-hitting rate-limited sources — *source* here meaning one row of the resolved portfolio in §2.3, with the connector class, budget unit and ladder rungs that row carries (§2.2). Cross-day **topic dedupe** is a separate mechanism entirely — the **dedupe index** (canonical ledger, §8.6) keyed by **topic cluster key** (the normalized semantic identity, never raw text match) with a configurable rolling lookback window, distinct from within-run retry idempotency. Ranking keys on the input artifact set plus ranking-config version. Spin keys on ranked-topic id + brand-truth-snapshot id + voice-config version. Copy generation keys on spin-output id + destination/asset-type + prompt-template version. Packaging is idempotent by construction, keyed on run id + the set of included asset ids. Notification keys on run id + notification type, checked against an "already sent" marker so a retried run never double-pings the operator for the same event.

**Media generation is the one stage where the original C3 design must be corrected.** C3 originally specified a client-supplied idempotency token passed to the provider's job-submission call. A2's verified provider facts overturn this: **Kie documents no idempotency key, no client-reference field and no dedup semantics on task creation at all** (A2; corrected in SYNTHESIS §2b, D-17). There is no token to pass. The corrected design: **the write-ahead spend-ledger row is the idempotency mechanism.** A deterministic asset identity — theme, run-date, topic, asset slot, language, prompt-pattern version, **and attempt number** — is committed as an intent row *before* the submission call is made; the provider's task id is written the moment it is accepted; the terminal state and observed cost are written on resolution. On restart, an intent row with no terminal state is **resolved by querying the provider's own task-status endpoint, never by blind resubmission.**

**Idempotency is per (identity, attempt); the attempt count is bounded separately.** The attempt component is not decoration — without it, the refusal ladder's three permitted paid attempts (§5.6) and a QA-driven immediate regenerate (§12.4) would all collide on one identity and every one of them would have to be refused as a duplicate. So the two rules are stated separately because they do different jobs: **one (identity, attempt) pair permits at most one paid submission**, which is what prevents double-billing; and **the total number of attempts for an asset slot is bounded by the refusal-ladder cap and the QA-rejection cap** (§4.9, §5.6), which is what prevents a retry loop. An implementer building either rule alone builds a bug — one that refuses legitimate work, one that permits unbounded spend.

**The `submitted-unknown` state has two trigger conditions, not one, and they share a terminal handling.** The state was defined narrowly in one place (a process death between committing the intent row and writing the returned task id) and used generally in another (a diversion possible at any point before `done`), which described two different things under one name. Both are real:

- **Sub-case A — crash before task id.** Money may have moved; we hold no task id; the status endpoint is keyed by task id, so the job is unreachable by query.
- **Sub-case B — unresolvable resolve-by-query on a known task id.** The job was polling; the status call times out repeatedly, is rate-limited, or returns an answer that is neither success nor failure across runs. We hold the task id and still cannot reach a terminal state.

Both land in `submitted-unknown`, both are **never auto-resubmitted**, and both follow the same terminal disposition in §8.13.

### 8.6 The ledger set

Eight to ten record types need a durable home; the substrate choice is not uniform. **SQLite** — an embedded, serverless, transactional single-file engine — holds every ledger where atomic multi-field updates and fast conditional queries matter: the **run ledger**, the **media-job ledger**, the **spend ledger**, the **dedupe index**, and the **review-decision store** (C3 §2.4; D-05, D-07 solo-operator reality). **Plain files** hold bulky, human-readable content: the bodies stored by the **research artifact store**, the contents of each **run pack**, and the body of each **brand-truth snapshot** — with a lightweight metadata row in SQLite (existence, checksum, snapshot id, confidence band) so other stages can look up "does this exist and what state is it in" without re-parsing a file (C3 §2.4). The **claim ledger**'s recommended home (§6.3, carried as a recommendation pending OD-9) and the **model registry**'s home (§5.2) are owned by those sections; this section only asserts that both are referenced by id from the run pack and the spend ledger, never duplicated into a second store.

| Ledger | Substrate | Why |
|---|---|---|
| Run ledger | SQLite | Transactional checkpoint updates so a crash mid-write leaves a consistent last-known state, never a torn record; the scheduler/monitoring backbone |
| Media-job ledger | SQLite, most strongly of all | A live per-job state machine (§8.13) that must transactionally agree with the spend ledger on what was actually billed, and must answer "which jobs are nearing expiry and not yet downloaded" as a fast indexed query at the start of every run |
| Spend ledger | SQLite, non-negotiably transactional | Every paid call recorded as a row inside a transaction that also updates a running total; a torn write here has direct financial-integrity consequences |
| Dedupe index | SQLite | Needs a fast indexed "has this topic cluster key appeared within the lookback window" query across months of history; recording "topic used today" must be atomic with the ranking decision that used it |
| Review-decision store | SQLite | Inherently relational and status-driven — a pack has many assets each with independent, reason-coded approval state, plus the approving person's identity and the editorial-responsibility holder (§3.3, §11.4); a reviewer approving several assets in one sitting must not be left half-applied by a crash |
| **Assembly ledger** | SQLite | One row per (master × language) with its blocked-on-inputs → assembling → assembled → failed state and the media-job rows it depends on. This is what makes a partially generated master a resumable unit of work across runs rather than an orphan (§4.7a); it must transition transactionally with the media-job ledger, since the last input reaching `done` is what unblocks it |
| **Run-pack → canonical-key index** | SQLite | The index that lets targeted deletion reach *inside already-packaged, archived packs* rather than stopping at the artifact store. Without it, an erasure or objection request is unexecutable against every pack ever written, which is the exact failure the extract-first design exists to prevent (§2.6) |
| Research artifact store (bodies) | Plain files | Bulky, heterogeneous, write-once/append-mostly content that benefits from direct human/text inspection during a source-breakage debug session |
| Run pack (contents) | Plain files | This is what a human directly opens and reads — maximally transparent, portable, readable with nothing more than a text or browser viewer |
| Brand-truth snapshot (body) | Plain files, metadata row in SQLite | Content inspectable during a claim-safety dispute; other stages reference "snapshot id N" as a fast structured lookup |

No client-server database service is installed or administered anywhere in this design — a solo operator with no server infrastructure gets full transactional guarantees from a file that ships next to the run and is backed up by copying it (D-05, D-07).

### 8.7 Per-unit-of-work checkpoint/resume

The explicit scenario this must survive: a crash at four in the morning after roughly ten dollars of media generation must not discard that paid work (C3 §2.5). The checkpoint granularity is **per unit of work** — one (asset slot × language × attempt), which is exactly one media-job-ledger row and exactly one paid attempt chain (G8, SYNTHESIS §2b). Each unit is checkpointed the instant its ledger row transitions state, independent of whether the surrounding stage as a whole finishes. On resume, the pipeline re-enters the stage and asks the relevant ledger what is terminal, what is pending, and what never started — acting only on the incomplete remainder. Whole-run or whole-stage checkpointing were both rejected: a full restart either wastes already-spent money or requires the same fine-grained ledger checks anyway, at which point coarser granularity has bought nothing (C3 §2.5).

Per-stage timeouts nest inside an overall run ceiling. As the ceiling approaches, the run performs **graceful wind-down** — stop starting new paid work, checkpoint everything in flight, package whatever is complete — never a hard kill (C3 §2.5). This directly protects the paid-work-preservation constraint: a single hung research source or a single slow media poll must never be allowed to consume the entire run's time allowance and prevent packaging of otherwise-complete, already-paid-for work.

### 8.8 Exit-code taxonomy

Nine named classes (D-18; SYNTHESIS §4.7), each mapped to one distinct process exit code for scheduler-level monitoring; the numeric mapping itself is deferred to implementation, and full detail (which source degraded, which policy tripped, exact stage and reason) lives in the run ledger, not in the exit code:

**success** · **completed-with-pending-media** (healthy — media jobs adopted by a later run) · **partial-success — degraded sources** · **partial-success — budget-capped mid-pack** · **completed-degraded** (research-only; the brand-truth degrade condition fired) · **budget-stop** (pre-emptive; no new spend occurred in the affected stage) · **policy-stop** (mode, allowlist, claim or policy violation — fail-closed) · **skipped-overlap** (not a failure) · **hard-failure** (infrastructure or technical).

A binary success/failure signal was rejected outright: it collapses "go look now," "fine, just review when convenient," "ran out of budget, nothing's wrong," and "something actually broke" into one bit, forcing a manual log check after every single run and defeating the point of unattended operation (C3 §2.6). A highly granular per-stage-per-reason numeric code was equally rejected — that level of detail belongs in the run ledger, a channel built for it, not in the OS exit code, a channel schedulers treat coarsely.

### 8.9 Unattended secrets

No interactive session exists at three in the morning to type a password. The baseline, identical in shape on both platforms, is **ACL/permission-restricted secret files**: NTFS ACLs on Windows and POSIX file permissions on Linux, each restricting read access to the exact account the unattended job runs as, kept outside source control (C3 §2.7; D-11). OS-native hardening layers on top of this baseline, never replaces it: DPAPI-protect the Windows secrets file's contents at rest once the task's run-as/logon configuration is confirmed to support it; adopt systemd-managed credentials once systemd timers are confirmed as the Linux scheduler (§8.1). A hard design rule independent of storage mechanism: secrets are never placed in source control, never embedded in prompts sent to any model, never written into the run ledger, and are redacted from every logging path.

A client-server secrets-manager service and relying solely on task-level environment variables were both rejected: the former is disproportionate infrastructure for a solo operator with no server (D-07) and introduces a new externally-reachable dependency with its own "unreachable at 3am" failure mode; the latter is more exposed to casual inspection and easy to leak into diagnostic logs or crash dumps than a permission-restricted file (C3 §2.7).

### 8.10 Retries and partial-failure semantics per stage

**Submission-type calls** (research fetch, LLM call, media-job submission) use exponential backoff with a capped attempt count and a capped total retry-time budget. **Polling an already-submitted async job** is a different operation entirely — a patient, bounded-duration loop against the job's own expected completion window — and must never be conflated with a retry: a naive retry wrapper applied to a submission call risks resubmitting and double-billing a job that actually succeeded on the provider side but whose response was merely slow to arrive (C3 §2.8; G3, SYNTHESIS §2b).

Per-failure-type handling: a **research source down** is a soft, per-source failure — logged, marked degraded in the run ledger and the pack, the rest of collection continues; this is what produces the partial-success (degraded-sources) exit class, and hard-failing the whole run over one flaky source was explicitly rejected as making the pipeline hostage to its most fragile dependency. An **LLM error** on a given artifact retries with backoff up to a capped count, and if still failing is marked incomplete for that one asset rather than fabricating filler — escalating to a stage/run-level failure only past a configurable share of failed units in that stage. A **media provider failure** at submission time follows the capped-retry-with-ledger-check path (§8.5); a job erroring out after successful submission is recorded failed in the media-job ledger with no further billing assumed, and is surfaced to the operator as "this asset's media failed, here's why" rather than silently dropped. **Disk full** is a hard-failure class, not a per-unit soft failure, because it risks corrupting an in-progress ledger write; the correct behavior is a proactive low-disk-space check, failing closed before further writes once a safe threshold is crossed (C3 §2.8).

**The disk check is a running guard, not two point-in-time checks — because the two correct mechanisms collided.** As originally written the check ran at run start and again before the media stage. But phase 0's expiry-ordered drain must run to completion *before anything new is submitted*, and that drain is backlog-dependent: several runs' worth of pending video accumulated while an operator was away is far larger than a normal run's download volume. So both checks could pass and the disk could still fill **mid-drain** — at which point the designed hard-failure response ("fail closed before further writes") aborts the run partway through, leaving already-generated, **already-paid-for** media undownloaded and racing a 14-day provider deletion window with no guaranteed next attempt if the disk problem outlives it. Two designed safety mechanisms jointly producing the one outcome the whole checkpoint design exists to prevent — *a stop must not discard paid work* (§0.1) — is not an acceptable seam. The corrected behaviour:

1. **The low-disk check is evaluated before each individual download inside the drain loop**, not merely twice per run, using the file's own expected size where the provider reports it.
2. **On a mid-drain low-disk event, the drain does not abort — it narrows.** New submissions are refused immediately (they are the discretionary spend), and the drain continues in strict expiry order for as long as free space permits, so the jobs closest to permanent loss are rescued first. Only when free space can no longer accommodate even the nearest-to-expiry remaining artifact does the run stop, and it stops as **hard-failure with the undownloaded jobs and their deletion deadlines named in the digest and the notification**, so the operator knows precisely what is at risk and by when.
3. **Ledger writes are protected ahead of media writes.** The safe threshold reserves headroom for ledger and pack writes specifically, so a disk that is too full for another video is still able to record what happened. Losing the record of the paid work is worse than losing one download.

A second, cheaper mitigation follows from the same reasoning and is adopted: the pre-drain check estimates the **whole backlog's** download volume rather than a normal run's, and refuses to start a drain it cannot finish, escalating to the operator instead — a refusal before spending time is better than an abort in the middle of it.

### 8.11 Budget caps, including mid-pack cap-hit

Budget enforcement happens at two granularities that work together. An aggregate **cost forecast** is computed across the whole plan for a pack (all planned assets across all languages) and is what an interactive operator sees and approves before media spend begins (§9, §12) — that approval authorizes *attempting* the plan, it does not disable the second granularity. Each individual media-job submission is still checked in real time, at submission, against the remaining budget (**cost gate**, canonical; pre-submission, never post-submission — A2, C3, C4). This is exactly what makes the mid-pack cap-hit case possible and safe. **The worked illustration is stated in masters and languages, which is the canonical cap unit (§0.2 item 3, §3.2) — not in destinations, which it previously used and which the counting model makes impossible.** The reason the old illustration could not happen is worth keeping: five of the six destinations in the identical-mix matrix are free, near-simultaneous re-compositions of one shared master, so the money is spent (or not) at the master-generation step and there is no moment *between* two of those five destinations at which a dollar cap could trip. The illustration that can happen:

> The English video master and the English slide-art master complete. The cost gate then refuses the Czech pair because the remaining per-run budget no longer covers them. **The pipeline ships the partial pack, clearly marked incomplete**: English's five derivative destinations are fully reviewable, and every Czech media-bearing asset is explicitly flagged *not generated — budget capped*, with the Czech copy, captions, slide list and shot list all present because those cost nothing. The run exits **partial-success — budget-capped mid-pack**.

Withholding the whole pack until the cap is manually raised, or rolling back the already-paid-for English masters for aesthetic consistency, were both rejected — the former delays or risks losing already-paid-for value with no offsetting benefit, the latter is the single most direct possible violation of the paid-work-preservation constraint.

**Two independent limits govern the same stage, and their precedence is stated rather than left to the implementer.** A **count cap** (masters per language per run) and a **dollar cap** (the cost gate, checked at each submission) both apply to media generation, and the plan's own economics guarantee they diverge by language: the English default buys generative clips at roughly $0.30–$1.25 each while the Czech default buys none, so a shared per-run dollar cap can exhaust itself on English while Czech still has count allowance, or Czech can hit its count cap while dollars remain. The rule: **both are checked at every submission, and whichever trips first stops that submission. Both outcomes are logged distinctly** — *count-capped* and *budget-capped* are different lines in the digest, because they call for different operator actions (raise the volume knob versus raise the budget, or neither). Neither limit is ever relaxed at runtime to satisfy the other. The same precedence governs the **text budget** (§5.4a): a per-stage call ceiling and a per-run token budget are independent, whichever binds first stops the call, and both are logged.

**A capped pack is completed by an explicit act, not by the next scheduled run doing the work again.** This was previously unwired: a "regenerate-media-only" stage-enablement flag existed as a knob and was never connected to the outcome it exists for. It is connected here. **The missing masters of a budget-capped pack are completed only by an explicit regenerate-media-only invocation referencing that run id**, which re-enters the media stage for the flagged slots against the current budget and amends the originating pack under §4.7a's pack-amendment rule. And the topic is marked in the dedupe index as **already generated (capped)** (§2.8a), so the next scheduled run does not re-rank it as a fresh discovery and re-spin and re-copy it from zero — which would pay twice for work already approved and would present the operator with a second, subtly different version of a pack they had already reviewed.

Config knobs feeding this (output/runtime block, per theme): a **per-run media budget cap**, **per-day** and **per-month caps**, the **global cross-theme daily and monthly caps** that sit above them (§5.4), the **per-run text budget with its per-stage call ceilings and per-pack judge allowance** (§5.4a), a **tier ceiling** (the highest tier an unattended run may auto-select — hero tier is never auto-selected regardless of ceiling, per A2/SYNTHESIS §1.6), the **separate per-run hero cap dimension** (§4.6), and a **masters-per-run-per-language cap** counting all media-bearing masters, deliberately separate from and much lower than the topics-per-run cap because human video review — not topic volume — is the real throughput bottleneck (SYNTHESIS §3.10).

### 8.12 Notifications (W2.5-8: email)

A **filesystem status flag** is the mandatory, always-written baseline — it requires nothing external, so it cannot itself fail to be produced, and it remains the ground truth of "did today's run happen" independent of whether any push notification got through (C3 §2.9). **Email is the configured default push channel** (W2.5-8), with a chat webhook available as a config alternative (a **notification channel** knob, output/runtime block). Content covers "packs ready," each of the nine exit classes with human-readable framing, and a distinct **escalation rule for degraded automated sources**: when an automated source is unavailable, the pack is labeled with a degradation flag. **Two consecutive identical degrades of any kind escalate rather than repeat**, because repetitive identical alerts are exactly how alarms get ignored (C6 §5.5). This anti-flap principle applies only to degraded automated sources (which may recover): the curated-inbox ritual is no longer a per-run input (W7-1).

A notification-delivery failure is itself logged and reflected in the run ledger but **must never change the run's own exit class** — a failed email send is not the same fact as a failed run, and conflating them would let a mail-relay outage masquerade as a pipeline failure (C3 §2.9).

### 8.13 Kie async job lifecycle handling

Media generation is asynchronous and provider-owned; the console process has no stable public HTTPS endpoint to receive callbacks reliably, so **polling is the baseline** (roughly a 30-second interval), with a webhook receiver registered as a possible later optimization only (A2; G10, SYNTHESIS §2b). Renders typically take one to six minutes, with 1080p adding one to two more; a run legitimately ending with jobs still pending is healthy, not failure — this is exactly the **completed-with-pending-media** exit class, adopted and resolved by whichever run comes next (§8.8).

Three provider facts drive the design directly, all verified by A2 and none assumed:

- **No idempotency exists on the provider side** (§8.5) — the write-ahead spend-ledger row is the only mechanism; a process death between committing the intent row and recording the returned task id, **or an unresolvable status query on a known task id**, leaves a **submitted-unknown** state, which is never auto-resubmitted, only reconciled via a balance-delta check against the provider's own credit-balance endpoint (G1a, G5). *(The owning brief recommended the opposite for this case — declaring a timed-out task lost and eligible for controlled re-submission under the spend rules. That recommendation was considered and is overridden here, per the citation discipline in §0.4: with no provider-side idempotency, no client-reference field and no task-listing endpoint, a "controlled" resubmission is indistinguishable from a blind one, and the money-safety cost of double-billing exceeds the content cost of one lost slot. The stricter rule is a deliberate override, not an oversight.)*
- **Generated media is deleted by the provider after fourteen days**, and result URLs carry their own, often shorter validity windows (A2; W2-02). Re-hosting every artifact is therefore **mandatory before an asset slot is marked complete**, with a checksum verified on download so a truncated transfer is never marked done. The **first phase of every run** — before any new submission is attempted — is to adopt pending tasks and drain the download queue ordered by nearest expiry (G2).
- **Rate limits are locally enforced pacing, not merely respected on 429.** A2 verifies roughly twenty new generation requests per ten seconds; a single two-language standard pack can submit on the order of twenty jobs in one burst. Submission paces itself well under that ceiling rather than bursting up to it, and a 429 response is met with backoff and jitter, never a tighter loop (G3).

A further fact changes what the media-job ledger must record, not just how it behaves: **Kie's routing can silently substitute a different backup model on some content-review triggers**, and a substituted output can be forced to a different aspect ratio than requested (W2-03; G6). The media-job ledger therefore records **requested route, aspect and resolution alongside delivered values** — surfacing any mismatch in the pack before it silently fails the platform gate at publish time, and feeding the per-asset provenance record (owned jointly with §5.6 and §14.6) that is resolved *after* completion, not at submission, since the model that actually rendered an asset may differ from the one requested.

*Media-job state progression (plain description, not a state-machine diagram in code):* submitted → polling → completed-pending-download → rehosted → done, with a diversion to **failed**, **expired**, or **submitted-unknown** possible at any point before done, and with **done** unblocking the assembly ledger row that depends on it (§4.7a). The media-job ledger row is the single source of truth for where a given job sits on this path; resume logic reads that row rather than re-deriving state from scratch (§8.7).

**`submitted-unknown` has a terminal disposition, because "never auto-resubmit" is a safety property and not an ending.** Balance delta answers *whether money moved in aggregate*; it cannot answer *which task id*, and without a task id the status endpoint is unreachable — there is no task-listing or task-search endpoint documented anywhere in the provider's surface. Left as written, an asset identity could hold one paid attempt chain that never resolves, stranding that content slot permanently while the artifact was hard-deleted at fourteen days. The disposition:

1. **A bounded resolution window.** A `submitted-unknown` row is re-queried by the phase-0 adoption of each subsequent run (sub-case B only; sub-case A has nothing to query) until the earlier of a configured window or the provider's own fourteen-day deletion horizon.
2. **A named terminal state at the end of it: `paid-lost`** — money possibly or provably spent, no artifact, unrecoverable. The asset slot **degrades to plan-only with the reason attached**, exactly as a refusal does, so the pack is complete and honest rather than carrying a hole.
3. **It is a named line in the digest**, not a log entry: the operator sees *"one media job could not be resolved; treated as paid-lost; the slot shipped plan-only"*, with the expected cost shown.
4. **Exactly one fresh attempt is permitted under a new identity, on explicit operator action only.** Never automatically, never unattended. This is what frees the slot without ever letting the system decide to pay twice.
5. **The window is small but real and cannot be closed.** It is the gap between committing the intent row and writing the task id (sub-case A), or the interval in which a provider gives no clean answer (sub-case B). Saying so is more useful than implying the write-ahead ledger eliminates it.

**How an unresolved row is treated in the reconciliation arithmetic**, which changes when the circuit breaker fires and was previously unstated. A `submitted-unknown` row **contributes its full expected cost to the expected side of the balance-delta comparison from the moment the intent row is written** — the worst-case assumption. If the charge was real, it is already accounted for and the circuit breaker does not fire spuriously on a healthy run; if it was not, the ledger over-estimates expected spend, which errs toward *not* alarming rather than toward silently absorbing genuine unexplained spend. When the row reaches `paid-lost` the expected cost stays; when it resolves to a confirmed non-charge, the expected cost is reversed with a recorded adjustment.

---

## §9. End-to-end flows

Both walkthroughs execute the same **run-level** stage order (SYNTHESIS §1). **This section owns that order and nothing finer** (§0.2): theme load → run identity and lock → phase 0 (adopt pending media, drain the download queue in expiry order) → brand-truth resolution → brand-truth gate → collection → ranking → fit gate → spin → copy generation → **the per-asset gate chain, run per asset and owned in full by §14** → media planning (always produced) → cost gate → media generation (asynchronous, may span runs) → assembly → packaging → notification → human review gate → publish gate → distribution prep.

**The per-asset chain is deliberately collapsed to one element in that list, and this section no longer restates it.** It was restated here for readability and the restatement drifted: the version this section carried omitted both the post-assembly overlay claim pass and the asset QA rubric, and because §9 is the section both walkthroughs use and was itself labelled canonical, an implementer reading only this page would have built a pipeline in which no claim check ever sees a burned-in on-screen string. **A stage order and a gate chain are different objects with different owners, and conflating them is how one of them silently loses a step.** Where a walkthrough below needs to name a gate — the cost gate's human moment, the brand-truth gate's degrade — it names that gate alone and does not re-enumerate its neighbours.

What differs between the two walkthroughs is *who* satisfies each human-shaped checkpoint and *when* — never the stage order itself, never the per-asset chain, and never which code runs (§8.1).

### 9.1 Walkthrough (a): interactive operator run

theme load (operator selects theme, mode, optionally a single focus topic) → **run identity fixed and the run-lock acquired, or the invocation exits immediately as skipped-overlap if one is already held** — identical to the unattended path, because skip-on-overlap is a property of the one application and not of how it was started (§8.1, §8.3) → **phase 0: adopt any pending media jobs from a prior run and drain the download queue in expiry order, before anything new is submitted** — an interactive run performs this exactly as a scheduled one does, which is what makes simply opening the application enough to rescue paid work when both cadence knobs are off (§4.7) → secrets load (interactive session; may use the brand-truth reader's interactive path for exploration) → brand-truth resolution, using the interactive access path where convenient, but producing the same kind of hashed **brand-truth snapshot** any run would (§6.6) → **brand-truth gate** (if degrade fires, the operator sees the conflict directly and may consciously accept a research-only outcome — never silently) → collection → ranking → **fit gate** → spin → copy generation, with each asset passing individually through the per-asset gate chain (§14) → media planning (always produced, zero cost) → an aggregate **cost forecast** is shown in-session and the operator gives explicit go-ahead — this is the human satisfying the **cost gate** directly, synchronously, in real time (§8.11) → media generation proceeds (the operator may wait synchronously or return to the pack later, since generation is asynchronous regardless of invocation mode, §8.13) → assembly → packaging and run-digest write → notification (visible immediately in the session; email/flag written regardless, §8.12) → the operator opens the run digest, records decisions (§12) — this satisfies the **human review gate** → **publish gate** checks mode, allowlist, connection status and the recorded approval state (§7.4, §11) → distribution prep creates drafts (or falls back per the ladder, §7.2) for any approved, allowlisted, connected destination.

*Flow (plain arrow chain):* operator invocation → theme+mode+secrets (interactive) → run identity + lock (skip-on-overlap) → phase 0 (adopt pending media, drain expiry queue) → brand-truth resolution → brand-truth gate (operator-visible if degraded) → collection → ranking + fit gate → spin → copy generation + per-asset gate chain → media planning → cost gate (synchronous operator approval) → media generation (async) → assembly → packaging + digest → notification → human review gate (operator decision session) → publish gate → distribution prep.

**"Return to the pack later" is an operational constraint, and it is stated rather than implied.** There is no daemon, no background service and no session-persistence layer in this design, so an interactive run's process — and therefore its lock — lives exactly as long as its console session. Two consequences the operator needs to know. **(a)** If the operator waits for asynchronous generation, the console session must stay open; closing the terminal or sleeping the machine ends the process, and the OS-mediated lock is released on process death by construction, so nothing is left stuck. **(b)** The supported way to "return to the pack later" is therefore **not** to leave a process running: the run ends with **completed-with-pending-media**, the pack is written with the pending jobs and their days-to-deletion countdowns, and the *next* invocation — interactive or scheduled — adopts them in phase 0 and amends the pack (§4.7a). That is the design's answer, and it needs no background execution mechanism, which is fortunate because none exists. A scheduled trigger firing during a genuinely live interactive session is caught by the same lock and exits as **skipped-overlap**.

### 9.2 Walkthrough (b): unattended scheduled run

scheduler fires (Windows Task Scheduler under the operator's own account, §8.1) → theme + mode + secrets load non-interactively from ACL-protected files (§8.9) → run identity fixed (theme + run-date + attempt, §8.3) → lock acquired, or the run exits immediately as **skipped-overlap** if one is already held → **phase 0**: adopt any pending media jobs from a prior run and drain the download queue ordered by nearest expiry, before anything new is submitted (§8.13) → brand-truth resolution via the non-interactive access path (the **brand-truth reader**'s unattended route, §6.2) → **brand-truth gate**: if the degrade condition fires here, the run proceeds on the **completed-degraded** path — research and ranking still complete and are still saved, but no brand content is generated, zero media spend occurs, and the digest states this in one sentence (C6 §5.5; this is a hard stop-or-degrade with no human present to override it, §11) → collection, per the theme's **research-collection cadence** (§8.2) → ranking + **fit gate** → spin → copy generation with the identical per-asset gate chain as the interactive path (§14) — identity of chain being the whole point of §8.1 → media planning (always produced) → **cost gate** checked purely against the pre-configured budget caps (§8.11) — there is no human moment here; hero tier is never auto-selected regardless of remaining budget → media generation proceeds within cap, submission-paced (§8.13) → assembly → packaging and run-digest write → notification: filesystem flag always written, email sent (§8.12) → exit code emitted (§8.8) → the run stops. **No publish gate crossing occurs unless a human-approval state was already recorded in an earlier session for the relevant assets and the unattended draft-creation knob is on for this mode** (§7.6) — otherwise distribution prep simply does not run, and the pack waits for the operator's next session.

*Flow (plain arrow chain):* scheduler trigger → theme+mode+secrets (non-interactive) → run identity + lock (skip-on-overlap) → phase 0 (adopt pending media, drain expiry queue) → brand-truth resolution → brand-truth gate (auto-degrade possible, no override) → collection (per cadence) → ranking + fit gate → spin → copy generation + per-asset gate chain → media planning → cost gate (cap-only, no human) → media generation (async, paced) → assembly → packaging + digest → notification (flag + email) → exit code → stop (publish gate/distribution prep only if a prior approval exists and the unattended-draft knob is on).

### 9.3 Divergence table

| Dimension | (a) Interactive | (b) Unattended scheduled |
|---|---|---|
| Auth to brand-truth reader | May use the interactive access path for exploration; pack-bearing resolution still uses the same non-expiring path any run would | Always the non-interactive path — the only one that survives a run with nobody watching (§6.2; C1) |
| Brand-truth gate degrade | Operator sees the conflict card directly and may consciously accept a research-only (MINIMAL) outcome; may not override a red-flag conflict, an unreadable claim ledger, or unresolved excludes (C6 §5.4) | Fires automatically to **completed-degraded**; never overridable by anyone, because no one is present to override it |
| Cost gate | Satisfied synchronously by direct operator approval of the aggregate forecast, in-session, before media generation begins | Satisfied purely by pre-configured caps checked at each submission; no human moment exists; hero tier never auto-selected |
| Spend approval | An explicit go/no-go moment, once, for the whole pack's planned spend | No approval moment at all — only mechanical enforcement against caps, plus the mid-pack cap-hit behavior (§8.11) if they are exceeded |
| Human review gate | Satisfied within the same session, often minutes after packaging | Satisfied later, asynchronously, whenever the operator next opens the run digest — the run itself has already exited by then |
| Notifications | Visible immediately in the console session; email/flag still written for consistency and later audit | The only visibility the operator has until the next session — filesystem flag plus email are load-bearing, not a courtesy |
| Distribution prep | May proceed within the same session once the human review gate and publish gate are satisfied | Never proceeds unless a human-approval state was already recorded in a prior session **and** the unattended draft-creation knob is explicitly on for the active mode; otherwise it is simply skipped, not attempted-and-blocked |
| Output at exit | The operator typically stays engaged through packaging and often through the review decision itself | The run always terminates at a named exit class (§8.8) with the pack waiting, regardless of how "good" the pack turned out to be |

---

## §10. Theme configuration — the knob surface

### 10.1 What a theme is, and what it is not

A **theme** is one tenant's complete answer to three questions: *what do we watch*, *how do we interpret it*, and *how do we run*. Those are the assignment's three configuration blocks and they are the canonical names used throughout this plan — the **research block**, the **spin block** and the **output/runtime block** (`SYNTHESIS.md` §4.6). Two further named blocks hang off the theme rather than sitting inside those three, because they are pointers to bodies of material rather than settings: the **exemplar corpus** (per theme, per language, style-only, never a fact source — §6.11) and the **publish allowlist** (per mode, the one list the publish gate reads — §7.4). A third, the **language overlay**, is deliberately *not* per theme: it is per language and shared across themes, so every future Czech-writing theme inherits one slop lexicon, one register norm set, one CTA phrase bank and one set of on-screen-text conventions (§3.4).

The tables below are the complete sweep of every knob named in §1–§8, §11, §12 and §14. They are prose descriptions of concepts, not keys, not syntax and not a schema. Two rules govern where a knob lives (§5.3): **if changing it would require touching more than one theme at once, it is engine-level, not theme-level**; and **anything that can spend money, publish, or relax a safety threshold defaults to the safe value**, so that a theme created by copying the first one is safe before it is useful.

**Four blocks, not three.** A theme carries the research block, the spin block and the output/runtime block. A fourth, the **machine/runtime block** (§10.4a), is *not* part of a theme at all: it holds the settings that describe the computer a run executes on rather than the tenant it executes for. It is named as a block because four knobs previously sat in the theme's output/runtime block that fail §10.1's own placement rule outright — the low-disk threshold (whose default column literally read "per machine"), the launcher and interpreter path resolution, the secrets location and permission policy, and log verbosity and retention. Copying a theme to create a second one should not copy a disk threshold.

**The size of this surface, stated accurately.** Counting the tables below gives **roughly 130 settings** across the four blocks plus the publish allowlist, the exemplar-corpus pointer and the shared language overlay — not the "roughly ninety" that risk W3-01 sized its mitigation against. The correction matters because W3-01 names theme misconfiguration as the single most likely cause of a bad-but-plausible pack, and a mitigation sized against a number that is 30% low is a mitigation sized against the wrong problem. The risk log's row is corrected accordingly.

**The minimum viable knob set — what a new theme author must actually decide.** Safe-by-default answers the *safety* question and does nothing for the *overwhelm* question, which is the one W3-01 actually raises. Everything not listed here inherits: engine defaults, the shared language overlay, and the §2.3 source portfolio. A new theme in an existing language needs **eleven decisions**:

1. **Language array** — which languages this theme produces.
2. **Watch topics, keywords and entities** — the subject matter, which seeds every query-shaped collector and the brand-fit reference set.
3. **Source roster deviations** — which of the standard portfolio's sources are off or re-prioritised for this audience. Not a fresh roster; a diff.
4. **Designated fact locations** — where in the knowledge base each blocking fact class lives, and the claim-ledger pointer.
5. **Pain-to-offer relation** — the lookup from ICP segment and pain to offer, CTA class and owning brand. This is the theme's actual intellectual content.
6. **Brand-and-domain routing map** — which offer belongs to which brand and domain.
7. **Destination × asset-type matrix** — which destinations are on, per language.
8. **Recipe and audio policy per language.**
9. **Budget caps** — per run, day and month, for both wallets, plus the masters-per-language cap.
10. **Exemplar corpus pointer per language.**
11. **Publish allowlist per mode** — which, in test mode, is empty by construction and needs no decision at all until the theme is real.

Everything else is a tuning knob to be touched when a specific problem appears, and theme-readiness validation (§13.2) tells the author which of the eleven is missing rather than making them read a table of a hundred and thirty.

Three defaults deserve to be stated before the tables, because they are the ones an operator will look for first. **Both cadence knobs default to off** (W2.5-7) — no scheduled run of any kind happens until the operator makes an explicit choice per theme. **Mode defaults to test**, in which the publish allowlist is empty by construction. **Dry run defaults on for media generation in test mode** — and that default is **engine-level** (§10.4a), not a theme knob, precisely so a theme cannot weaken it.

### 10.2 Research block — what to watch and how to collect

| Knob (prose name) | What it controls | Default | Consumed by |
|---|---|---|---|
| **Watch topics, keywords and entities** | The subject matter this theme cares about; the seed for every query-shaped collector and the reference set for brand-fit judgment | Per theme; no engine default | §2.3, §2.7, §6.9 |
| **Research-side excludes** | Topics, framings and entities that must never become candidates, independent of the spin block's hard excludes | Empty, but "empty" is distinguished from "unresolved" | §2.7, §6.3 |
| **Language array** | Which output languages this theme produces; every listed language gets a full first-class set (D-02) | First theme: Czech and English | §2.7, §3.2, §3.4, §6.5, §13 |
| **Source roster with per-source priority** | Which List A sources are active and in what order of importance, re-ranked by access reality rather than by signal value alone | The §2.3 portfolio | §2.3, §2.7, §8.2 |
| **Per-source extraction method** | Which of the seven method values a source uses — official API, feed, licensed vendor, auth-integration, MCP wrapper, operator input, skip | Per §2.3 | §2.3, §2.4 |
| **Per-source cadence** | How often each source is polled, independent of the run cadence | Daily for the automated core | §2.3, §8.2 |
| **Per-source evidence class** | Whether a source's virality signal is counted, ranked/presence-only, or human-asserted | Per §2.7 | §2.7, §12.1 |
| **Per-source run budget** | The ceiling in calls, quota units, vendor credits or wall-clock seconds a single source may consume in one run | Per source; sub-10% of daily quota for the video-platform collector | §2.2, §2.3, §11.1 |
| **Source-family membership** | Which of the seven families each source belongs to, so corroboration counts observations rather than echoes | Per §2.7 | §2.7 |
| **Ladder-rung configuration per source** | The primary → degraded → operator-supplied → skip-with-log chain for each source; no rung may descend into scraping | Per §2.2 | §2.2, §2.5, §8.10 |
| **Per-source circuit-breaker threshold** | Consecutive failures after which a source is dropped for the rest of the run and marked degraded | Per source | §2.8, §8.10 |
| **Source-health escalation count** | How many consecutive degraded runs escalate a source's notification prominence rather than repeating an identical message | Two | §2.2, §8.12 |
| **Collection wall-clock ceiling** | The global time budget for collection, after which ranking runs anyway on what was gathered | Per theme | §2.8, §8.7 |
| **Conditional-request and cache time-to-live per signal class** | How long a fetched result is reused before re-requesting; cache-before-call is mandatory on paid sources | Per signal class | §2.8 |
| **Topic dedupe lookback window** | How far back the dedupe index is consulted for a topic cluster key, with per-source overrides | Rolling; per theme | §2.7, §8.5, §12.1 |
| **Freshness half-life per signal class** | Decay rate for spike, rising, launch-hype and evergreen-pain classes; the ad-creative class runs inverted | Directional starting values only (§2.7) | §2.7 |
| **Brand-fit floor** | The hard numeric floor on brand fit alone, below which a candidate is skipped regardless of every other dimension | Directional 0.35, a calibration starting point and not an empirical finding | §2.7, §12.1, §16 |
| **Veto list contents** | The binary stop conditions checked before scoring: legal and claim risk, competitor disparagement, high-severity controversy, detected manipulation, prompt-injection phrasing | Per §2.7 | §2.7 |
| **Corroboration bonus magnitude** | How much cross-family confirmation lifts a candidate | Per theme | §2.7 |
| **Top-N topics cap per language** | The maximum ranked topics carried forward, applied *after* filtering and never by lowering the threshold to fill a quota | Around three per run (OD-8 recommendation, still open) — reduced from an initial five once the whole-pack review-burden arithmetic in §3.5 was made explicit | §2.7, §12.1, §16 |
| **Monitor-only band boundary** | The score range in which a candidate is watched but not generated against | Per theme | §2.7 |
| **Absolute-band fallback thresholds** | Fixed per-source virality bands used during the roughly two weeks before a trailing baseline exists | Per source | §2.7 |
| **Demand-modifier weight** | How strongly the search-demand axis modifies a composite, applied after the composite rather than inside it | Per theme | §2.7 |
| **Ranking-config version** | The version stamp recorded on every scorecard, so a score is reproducible and a threshold change is visible | Incremented on any threshold change | §2.7, §8.5, §12.2 |
| **Retention windows** | Separate durations for the request log, raw payloads, normalised signal records, and provenance-snapshot verbatim text | 12 months / 30 days / 90 days / 30 days | §2.6, §8.6, §15 |
| **Author-handle handling policy** | Whether handles are dropped, hashed or retained, and for how long | Hashed where needed for dedupe; never clear-text long-term | §2.6 |
| **MCP-source credit budget per month and pacing rule** | The metered spend ceiling for each licensed vendor consumed over MCP, and how it is spread across the month | Per vendor | §2.2, §11.1, §15 |
| **Vendor roster with last-verified and recheck-by dates** | The licensed-source equivalent of the model registry; a lapsed recheck drops a source to degraded and stops credit spend | Per vendor | §2.2, §5.2, §15 |
| **Curated-inbox staleness threshold and escalation count** | How long since the last operator session before the pain axis is flagged stale, and after how many misses the alert escalates | One cadence period; escalate at two consecutive misses | §2.2, §8.12, §12.1 |

### 10.3 Spin block — how we interpret

| Knob (prose name) | What it controls | Default | Consumed by |
|---|---|---|---|
| **Brand-truth source pointers and designated fact locations** | Exactly which knowledge-base locations may be read for each fact class; reading anywhere else is forbidden, which is the structural control against plan-versus-fact contamination | Per theme; must be explicit | §6.2, §6.3 |
| **Access path per context** | Which reader path serves interactive exploration versus every pack-bearing resolution including all scheduled runs | MCP interactive, REST for records (D-10) | §6.2, §9.3 |
| **Site-verification URL set, fetch budget and timeout** | Which live pages are checked, how many fetches per run and how long each may take; verification is targeted, never a crawl | A handful of timeboxed fetches | §6.6 |
| **Stale-warn and hard-stale thresholds per fact class** | When an observation is old enough to warn, and old enough to block | Per fact class | §6.6, §6.5 |
| **Maximum offline window — interactive runs only** | How long the last-good snapshot may be used when the knowledge base is unreachable. **There is deliberately no unattended limb**: an unattended run resolving from a snapshot is capped at MINIMAL, which is below PARTIAL, so it degrades to research-only immediately regardless of the snapshot's age (§6.5). Configuring an unattended window would describe a path the degrade trigger forbids | 14 days interactive | §6.5, §6.6, §11.3 |
| **Confidence band floor per mode** | The minimum band at which content generation is permitted in each mode | Below PARTIAL degrades to research-only unattended | §6.5, §11.3 |
| **Claim-ledger pointer** | Where the approved-claim allowlist lives and how it is queried | Notion typed database, recommended not locked (OD-9) | §6.3, §6.7, §14.3, §16 |
| **Hard-excludes baseline in configuration** | The exclusion list that must survive a knowledge-base outage; the union with any other source always wins | Per theme; monotonic | §6.3, §6.4, §11.3 |
| **Check-class enablement** | Which of the eleven claim check classes run; five may never be disabled | All eleven on; numeric, currency, entities, endorsement and required-statement non-disableable | §6.7, §14.3 |
| **Per-pack regenerate allowance** | The claim-gate retry budget, counted per pack rather than per asset so one bad prompt cannot cause a regeneration storm | Small fixed number | §6.7, §12.4, §14.3 |
| **Pain-to-offer relation** | The configured lookup from ICP segment and pain category to offer, preferred CTA class, owning brand and preferred formats — a relation, never an inference | Per theme | §6.9, §14.1 |
| **Mapping-distance policy per offer** | How loud an offer may be at direct, adjacent and far distance | Per §6.9 | §6.9, §14.1 |
| **CTA class enablement per destination per language** | Which CTA classes are allowed where, and in which language | Content and product-path on; event and commercial-incentive off until their preconditions resolve | §6.9, §3.3 |
| **CTA phrase bank pointer per language** | The literal approved phrasings, per language, mapped to CTA classes | Language overlay | §6.9, §14.4 |
| **Site-first offer list and hold-versus-substitute choice** | Which offers require the article to exist first, and whether social atomisations are held or generated with a different CTA | Site-first offers listed; hold is the default | §6.9, §7.3 |
| **Person allowlist** | Named humans who may appear in copy without being flagged as unknown entities | Per theme | §6.3, §6.7 |
| **Brand-and-domain routing map** | Which offer belongs to which brand and which domain, so a CTA cannot point at the wrong property | Per theme | §6.3, §6.9 |
| **Pricing policy** | The rule about whether prices may be stated at all, distinct from the price values themselves | Config-primary; stricter policy wins on conflict | §6.3, §6.4, §6.7 |
| **Compliance obligations** | Entity disclosure, affiliate disclosure and AI-content labelling duties this theme must satisfy | Per theme; the stricter setting wins | §6.3, §6.7, §14.6 |
| **Speech-recognition sampling rate and adherence-alarm threshold** | How often spoken output is sampled for adherence, and what measured drop disables audio for a route | Every asset for the first weeks, then a rolling sample | §6.8, §14.5 |
| **Exemplar corpus pointer per language** | Where this theme's style-only reference material lives; excluded from every factual retrieval path | Per theme, per language | §6.11, §14.2, §14.4 |
| **Corpus-leakage sensitivity** | How aggressively generated numbers, metric phrases and entities are matched against corpus content and blocked | Block on any overlap lacking a ledger entry | §6.7, §6.11 |
| **Resolver rule version** | The precedence-and-threshold version stamped into every brand-truth snapshot, so a snapshot is reproducible | Incremented on any precedence change | §6.6 |
| **Snapshot reuse time-to-live** | How long a resolved snapshot may be reused across runs on the same day | Per theme | §6.6 |
| **Event-driven refresh trigger set** | Which events force a full re-pull regardless of the time-to-live: readiness validation, config hash change, a rejection citing a wrong brand fact, a contradicted claim verdict, a dead CTA URL, a new offer status | Per §6.6 | §6.6 |
| **Language overlay pointer per language** | Which shared language overlay this theme's Czech and English output uses | Shared, per language | §3.4, §14.4 |
| **Peer-community context declaration** | The only setting that permits tykání (informal register) in Czech; absent it, **vykání** — the formal second-person register — is mandatory in every public post and first-contact CTA | Absent — **vykání by default** (D-26) | §3.1, §14.4 |
| **Visual brand baseline** | Logo usage, palette, on-image text rules and the brand lock's visual half | Per theme | §4.4, §6.3 |
| **Voice rules and banned phrasing** | The theme's own additions on top of the language overlay's slop lexicon | Per theme | §3.4, §14.2 |

### 10.4 Output/runtime block — what we make, how we run, what we may spend

**Destinations and assets.**

| Knob (prose name) | What it controls | Default | Consumed by |
|---|---|---|---|
| **Per-language destination × asset-type matrix** | Which destinations are on and which asset types each produces, per language; identical across languages in v1 (W2.5-4) | Per §3.2 | §3.2, §12.2, §13 |
| **X destination enablement** | Whether X assets are produced at all; production is free and is a separate question from publishing | Config-gated, default off | §3.2, §7.5, §16 |
| **Blog enablement and per-language, per-domain article routing** | Whether long-form is produced, in which languages, for which domain | Drafts only in v1 (OD-14) | §3.2, §7.3 |
| **Per-destination format profile** | Character limits, aspect, duration, slide count and hashtag norms the platform gate enforces | The verified 2026 values in §3.3 | §3.3, §12.2 |
| **Link policy per destination** | Where links may appear, including the contested link-in-first-comment convention, treated as a per-theme style choice rather than a rule | Per theme | §3.3 |
| **CTA placement convention per destination** | Where in an asset the single CTA sits | Per theme | §3.3, §6.9 |
| **Carousel size caps** | Slides per carousel and pages per document carousel | 5–15 slides target | §3.2, §3.3 |
| **Per-language volume targets** | How many assets of each type a healthy week produces | Per theme | §3.2, §12.1 |
| **Masters per language per run cap** | The media-bearing ceiling, **counting all media-bearing masters produced, not destination derivatives** — one 9:16 master serves several destinations through re-composition, while a video master and a slide-art set are two masters, not one | One to two per language (OD-8 recommendation, still open) | §3.2, §4.6, §8.11, §16 |
| **Minimum mapping distance per destination** | The closest-to-far distance a destination will accept without a named soft bridge; short-form expects utility in a way LinkedIn and the blog do not | Adjacent-or-closer for TikTok, Reels and Shorts; unrestricted elsewhere | §3.3, §6.9 |
| **Czech short-form revisit trigger** | The asset count and week backstop at which the digest raises the Czech short-form review line | Twenty published Czech short-form assets or twelve weeks, whichever first (OD-22) | §3.1, §12.1, §16 |
| **Per-destination derivative set** | Which re-compositions are produced from each master | Per §4.4 | §3.2, §4.4 |
| **Review-depth profile per asset type** | How much operator attention each asset type is expected to need, which drives digest ordering and batch defaults | Per §3.5 | §3.5, §12.1 |
| **Czech short-form production floor checklist** | The extra acceptance items a Czech short-form asset must clear: prosody acceptance, glyph coverage, no English audio anywhere, plus every English gate | Mandatory when Czech short-form is enabled | §3.1, §4.4, §12.2 |
| **AI-content class — tightening override only** | The class itself is **derived at engine level from the generation record** and is not configurable: any asset with a model-rendered visual, audio or motion component — **including synthetic speech and generated music** — is realistic-synthetic. This knob may only declare a *stricter* class than the engine derives, never a looser one, on the same monotonic rule as hard excludes | Engine-derived; no theme override set | §3.3, §7.7, §14.6 |
| **AI-label-required flag and the packaging label checklist** | Whether an asset carries the platform-native label obligation, and the per-platform checklist emitted with it into rung-3 staging | Set automatically from the AI-content class | §3.3, §7.2, §7.7 |

**Video and media production.**

| Knob (prose name) | What it controls | Default | Consumed by |
|---|---|---|---|
| **Recipe per language** | Which of the three legal production paths a language uses by default | English generative-clip led; Czech carousel-to-reel (D-14) | §4.8, §12.2 |
| **Audio policy per language** | Model-native speech, text-to-speech voice-over, or none; model-native Czech speech is banned outright | English may use native speech; Czech never | §4.8, §14.5 |
| **Text-to-speech provider and voice identity per language** | Which provider and which voice renders the verified script. **Only routes whose voice basis is licensed-catalogue may be selected**; a cloned-real-person voice is a forbidden rights class in v1 (§5.3) | Primary with a cost/fallback tier (OD-13, trial-gated) | §4.8, §5.1, §5.3, §16 |
| **Caption timing source per language** | Text-to-speech-native timestamps, forced alignment, or the slide-timing model — determined by the selected voice route's capability rather than chosen freely | TTS-native where the route returns timestamps | §4.4, §16 |
| **Caption style and word-level reveal** | How captions are burned in, and whether word-by-word animation is used. **Word-level reveal is unavailable on the subtitles-only path**, which has no audio to align against; requesting it there is a readiness failure, not a silent downgrade | Per theme | §4.4, §13.2 |
| **Adherence-similarity threshold** | The script-versus-recognised-audio similarity below which a model-native-speech asset fails closed to the QA-flag path | Per theme; applies only to model-native-speech recipes | §4.4, §4.9 |
| **QA-rejection cap** | Regenerations of one asset slot driven by QA flags or human rejection within one pack, before the terminal "did not clear QA after N attempts" state | Two | §4.9, §12.4 |
| **Music source and bed selection** | Which licensed library or licensed generator supplies music; platform trending audio is forbidden for masters | Licensed only | §4.4 |
| **Loudness targets and QA tolerance band** | The mastering target and the range outside which an asset fails closed | −14 LUFS integrated, −1.0 dBTP ceiling | §4.4 |
| **Safe-box dimensions** | The universal composition area that lets one master serve every vertical destination | ≈900×1400 centred | §4.4 |
| **End-card recipe** | The layered CTA shape, including the loop-friendly no-outro variant | Mid-video cue plus a 1.5–2.0 second dual-delivery close | §4.4 |
| **Shot count and clip length per asset type** | How many shots a video plan requests and how long each runs | Per asset type | §4.2, §4.3 |
| **Hook overgeneration count** | How many hook candidates are drafted before selection; cheap per call, and drawn against the copy-generation stage's call ceiling (§5.4a) | Three to five | §4.2, §5.4a |
| **Keyframe variant count** | How many keyframe options are generated before the acceptance decision | Two or three | §4.2 |
| **Keyframe-acceptance policy per mode, and the unattended rubric threshold** | Whether the approval event that unlocks clip spend is human or rubric-automatic in each mode, and the scored bar the rubric applies when automatic. The rubric's contents are engine-level (§4.2a); items 2 and 4 — no legible text, person-policy compliance — are binary in every mode and cannot be thresholded | Human in interactive; rubric-automatic within caps unattended, at or above the engine floor | §4.2a, §4.9, §11.1 |
| **Asset QA rubric thresholds** | The machine accept/reject bar for finished media, including the measured disclosure items | Per theme, at or above the engine floor | §4.2, §4.4, §12.2 |
| **Disclosure overlay text and placement per language — above the engine floor** | The exact burned-in wording, its position, its duration, its type-height ratio, its contrast and the audible-equivalent text. **The engine floor (§4.4) is non-relaxable: visible from the first second, inside the safe box, minimum type-height ratio and contrast, in the asset's language, audible equivalent on audio-led assets.** A theme may only tighten | Per language; mandatory; floor enforced | §4.4, §4.4a, §14.6 |
| **Slide timing range for carousel-to-reel** | Seconds per slide, with the hook slide held longer | 2.5–4 seconds | §4.5 |

**Providers, tiers and money.**

| Knob (prose name) | What it controls | Default | Consumed by |
|---|---|---|---|
| **Media router selection and per-theme override** | Which router hosts routes for this theme | The v1 router (D-04a) | §5.1, §5.3 |
| **Permitted tiers per mode (tier ceiling)** | The highest tier an unattended run may auto-select | Standard; hero never auto-selected in any mode | §4.6, §5.3, §8.11, §11.1 |
| **Preferred routes within a tier** | Which registry routes this theme prefers when several are eligible | Per theme | §5.3 |
| **Hero auto-promote flag and per-run hero cap** | Whether hero tier may ever be selected without a human, and how many hero assets a run may contain | Off; cap per run | §4.6, §5.3, §11.1 |
| **Media budget caps per asset, run, day and month** | The four media spend ceilings, all enforced *before* submission | Per theme; sized against the trial envelope | §5.4, §8.11, §11.1, §12.3 |
| **Text budget caps per run, day and month** | The token-or-currency ceilings on text-model spend, enforced pre-call by the same cost gate. Trip behaviour is the mid-pack cap-hit outcome class | Per theme; sized against the artifact count × gate-stack profile | §5.4a, §8.11, §11.1, §12.3 |
| **Per-stage text call ceilings** | The maximum model calls a stage may make in one run — ranking, copy generation, and each gate — which are the ceilings §1.5's cost-computability argument depends on | Derived from candidate and asset counts; per theme override | §1.5, §5.4a, §8.11 |
| **Per-pack judge allowance** | Judge-role calls per pack across the voice gate and both claim semantic passes; exhaustion degrades the pack to review-required | Small fixed number | §5.4a, §14.2, §14.3 |
| **Per-node per-call token ceiling** | Bounded input and output size for each node class in §1.5's inventory, so one pathological input cannot consume a run | Per node class, engine floor with theme tightening | §1.5, §5.4a, §6.6 |
| **Global cross-theme daily and monthly caps** | The ceilings above the per-theme ones, because multiple themes spend against one prepaid balance | Mandatory whenever more than one theme exists | §5.4, §8.11, §13.1 |
| **Unexplained-spend tolerance** | How far observed balance delta may diverge from expected cost before the circuit breaker halts new submissions | **Directional starting point: the greater of a few cents or ten per cent of the run's expected spend** — a calibration starting point, not an empirical finding, on the same footing as the brand-fit floor | §5.6, §8.13, §15 |
| **Refusal-ladder attempt cap** | Paid attempts per asset slot before degrading to plan-only | Three, terminating in plan-only | §4.9, §5.6 |
| **Poll interval and per-job poll budget** | How often an async job is checked and for how long before it is treated as pending across runs | Roughly 30 seconds; bounded | §5.6, §8.13 |
| **`submitted-unknown` resolution window** | How long an unresolved job is re-queried before it becomes terminally `paid-lost` and its slot degrades to plan-only | Bounded by the provider's own deletion horizon | §8.5, §8.13 |
| **Price-recheck cadence, recheck-by grace, and grace behaviour** | How often registry prices are re-verified, how long a lapse is tolerated before the route degrades, and what a stale-priced route may do during grace. **An unattended run never submits against a stale-priced route**; an interactive one may, on a recorded acknowledgement | Monthly recheck; a grace period, not an instant cut-off | §5.2, §15 |
| **Rights-class allowlist per destination** | Which licence classes may reach which destination, including the later paid phase | Per destination | §5.3, §5.8 |
| **Person-policy defaults per theme** | No-people, adults-only or region-restricted generation defaults, so a theme author never has to know a route's regional restriction | Region-appropriate | §5.2, §5.3 |
| **Fallback-router engagement threshold** | The spend or reliability level at which the registered fallback router is actually integrated | Named open item (§16) | §5.7, §16 |
| **Trial budget envelope and reserve** | How the trial credit is apportioned between bake-off, real packs and reserve | Roughly $8 / $35 / $7 (W2-14) | §5.4, §17 |

**Schedule, safety and runtime.**

| Knob (prose name) | What it controls | Default | Consumed by |
|---|---|---|---|
| **Research-collection cadence** | How often collection, ranking and dedupe-index maintenance run, with no media spend at this cadence | **Off** (W2.5-7); daily once enabled | §8.2, §9.2, §13 |
| **Pack-production cadence** | How often the full pipeline runs through spin, copy, media planning and generation, packaging and notification | **Off** (W2.5-7); a small number of times per week once enabled | §8.2, §9.2, §13 |
| **Theme timezone** | The single timezone from which the pinned run-date is derived; every stored timestamp stays UTC internally | Per theme | §8.3 |
| **Mode** | Which capability row of the matrix applies to this run | **test** | §11.1, §11.2 |
| **Publish allowlist per mode** | The exact destinations where publishing side effects are permitted, per mode — the one list the publish gate reads | Empty in test, by construction | §7.4, §11.1, §11.2 |
| **Unattended draft-creation enablement** | Whether a run with nobody present may create drafts in the publishing bridge at all, for assets already carrying a recorded approval | **Off** | §7.6, §9.2, §11.1 |
| **Blog/site prep enablement** | Whether an article draft artifact is produced for this theme | Off unless the theme needs it | §7.3, §3.2 |
| **Notification channel and preferences** | Which push channel carries "packs ready" and failure alerts; the filesystem status flag is always written regardless | Email (W2.5-8), flag mandatory | §8.12, §12.1 |
| **Anti-flap escalation counts** | How many consecutive identical degrades escalate prominence instead of repeating | Two | §8.12, §2.2 |
| **Idempotency key composition per stage** | Which semantic inputs and which config or prompt versions form each cost-bearing stage's content-hash key | Per §8.5 | §8.5, §14.7 |
| **Per-stage timeout and overall run ceiling** | How long each stage and the whole run may take before graceful wind-down | Per theme | §1.5, §8.7 |
| **Internal-iteration cap** | The bounded self-critique allowance for the only two nodes permitted one — topic ranking and copy drafting | Small, enforced by the pipeline not the model | §1.5 |
| **Model selection per role per language** | Which text route fills the **drafting** role and which fills the **judge** role — two roles, not three; the polish role is deleted for owning no stage (§1.5) — chosen independently and ideally from different lineages | Per language (OD-28) | §1.5, §5.1, §14.2, §14.7 |
| **Stage enablement flags for partial runs** | Whether a run is research-only, spin-only, or regenerate-media-only | Full run | §1.5, §9.1 |
| **Voice regenerate cap per artifact** | The hard ceiling on judge-driven regeneration for one artifact | Small; escalate to review on exhaustion | §14.2, §12.4 |
| **Per-pack voice-regenerate allowance** | The pack-level ceiling on judge-driven regeneration across all artifacts — the bound that actually limits worst-case unattended cost, since a per-artifact cap multiplied by sixty artifacts is not a bound. Exhaustion degrades the pack to review-required | Small fixed number, mirroring the claim-retry budget | §14.2, §14.3, §6.7 |
| **Combined per-artifact repair ceiling** | Repairs counted across spin, claim pass 1, voice and claim pass 2 for one artifact, including claim-2 repair re-entry; exhaustion takes the downgrade-repair variant rather than another lap | Small fixed number | §6.10, §14.0 |
| **Cross-pack recurrence window and similarity threshold** | How far back the house-style-tic check compares a new draft's opener and core phrasing, and how similar is too similar. An always-on check that can block assets needs a stated window | Rolling, per theme, per platform and language | §14.2 |
| **Judge flag-rate ceiling** | The rolling flag rate per theme, destination and language above which the judge itself is suspected rather than the generator | Calibrated from the golden set | §14.2, §17 |
| **Prompt-pattern and rubric version pinning** | That every artifact records which prompt version, rubric version and model version produced and judged it | Always on | §14.7, §8.5 |
| **Confidence-gated digest defaults** | Which topics arrive pre-selected, unselected, or requiring the operator to open detail first | High pre-selected, medium unselected, low requires detail | §12.1 |
| **Pack upload enablement** | Whether a completed pack's contents are also written into the knowledge base, later phase | Off | §12.6 |
| **Retry attempt caps and total retry-time budget per call class** | How submission-type calls back off, separately from how already-submitted async jobs are polled | Per call class | §8.10 |
| **Failed-unit share threshold** | What share of failed units in a stage escalates from per-asset incompleteness to a stage or run failure | Per theme | §8.10 |
| **Per-language minimum evidence-and-volume band** | The floor on candidates clearing the fit gate and on corroborating families behind them, evaluated every run; breaching it raises a named digest line rather than blocking anything | Deliberately loose; alarmable | §2.7, §12.1 |

### 10.4a Machine/runtime block — not part of a theme

These describe the computer a run executes on, not the tenant it executes for. They are separated because copying a theme to create a second one must not copy them, and because §10.1's own placement rule fails all of them: changing any one would require touching every theme on that machine at once.

| Knob (prose name) | What it controls | Default | Consumed by |
|---|---|---|---|
| **Low-disk threshold and reserved ledger headroom** | The free-space level below which new submissions stop and the drain narrows, and the space reserved so ledger and pack writes always succeed | Per machine | §8.10 |
| **Log verbosity and log retention** | How much is written to the file log — the only observability under a scheduler — and for how long | Per machine; secrets always redacted | §1.5, §8.9 |
| **Secrets location and permission policy** | Where secret files live and which account may read them; never in source control, never in prompts, never in the run ledger | Permission-restricted to the run-as account | §8.9 |
| **Launcher and interpreter path resolution** | How the per-OS launcher finds the runtime and resolves absolute paths, with explicit exit-code propagation | Absolute paths from configuration | §1.4, §8.1 |
| **Working and output root locations** | Where run folders, packs and ledgers are written on this machine | Per machine | §8.6, §12.5 |

### 10.5 Engine-level settings, deliberately not per theme

These exist so that a theme author never has to know them, and so that a safety property cannot be weakened by editing one tenant's configuration. They are named here for completeness and are consumed where indicated: the **model registry** itself and its route records across all four route classes (§5.2); the **four routing contracts** and the resolution algorithm (§5.3); rights-class definitions and the person-policy constraint layer (§5.2, §5.3); **the v1 likeness and voice-clone ban** (§5.3); tier definitions (§4.6); the refusal ladder's shape (§5.6); **submission pacing rate and download-queue drain policy** — resolved to engine level, since §10.4 previously listed both as per-theme knobs while this section already placed them here, and pacing that one tenant can loosen is not pacing (§8.13); **the dry-run default per mode** (§4.6, §11.1); **the AI-content-class derivation rule** (§3.3); **the engine-level disclosure floor** (§4.4); **the keyframe-acceptance rubric's contents** (§4.2a); **the negative-prompt layers 1–3 and the four skill bundles' shared pattern sets** (§4.10); the **do-not-scrape list** and the method-evaluation gate through which any new source must pass (§2.4, §2.5); the canonical run-level stage order (§9), the per-asset gate chain (§14) and **the repair re-entry rule** (§6.10); the nine exit-code classes (§8.8); the overlap and missed-run policies, which are fixed behaviours rather than knobs (§8.3, §8.4); the **language overlay** contents per language, shared across themes (§3.4, §14.4); and the capability matrix encoded once in the **mode capability resolver** (§11.2).

### 10.6 Theme-readiness validation reads this surface

Every knob above is also an input to **theme-readiness validation** (§13.2). Readiness is not "the file parses" — it is a set of assertions over the resolved configuration plus a dry resolution against live sources: that every blocking fact class resolves, that every configured language produces a non-empty candidate set and a non-empty asset matrix, that every enabled destination has a format profile and a CTA class it may legally use, that every configured source has a method, a budget and a ladder, that the publish allowlist is a subset of the connected channels for the active mode, and that both cadence knobs are either off or consistent with each other. A theme that fails readiness may still be run interactively in test mode; it may never be scheduled.

---

## §11. Modes and gates

### 11.1 Capability matrix

Three modes (canonical, SYNTHESIS §4.3): **test** (default), **staging**, **live-prep** — never a fourth "live" mode, because there is no unattended live-publish mode in this system by design (non-negotiable constraint 1). The matrix below covers every side-effectful capability the assignment names.

| Capability | test (default) | staging | live-prep |
|---|---|---|---|
| Research reads / collection (free sources) | Full — every configured source collects per its extraction method and cadence; research is never gated by publish mode | Full, unchanged | Full, unchanged |
| **Licensed-vendor credit spend** (MCP sources) | Allowed within the per-vendor monthly credit budget and its pacing rule; a lapsed vendor recheck or a stale-payload flag suspends it | Same, unchanged | Same, unchanged |
| **LLM / text-model spend** (drafting, gates, judges) | Allowed, within the **LLM budget block (§5.4a)** — per-run, per-day and per-month text budgets, per-stage call ceilings and the per-pack judge allowance, all enforced pre-call by the cost gate | Allowed, within the same block | Allowed, within the same block |
| Media spend (image/video/voice generation) | **Dry-run enforced by the resolver by default** — every plan and forecast is produced and nothing is submitted. Switching dry-run off is an engine-level change, not a theme edit (§10.4a), and once off the same caps apply: tier ceiling, per-run/day/month, global cross-theme; hero tier never auto-selected in any mode | Dry-run off by default; same caps | Dry-run off by default; same caps |
| Publishing-bridge calls (draft creation) | Refused outright, before the call is attempted — the allowlist is empty by construction | Allowed only for allowlisted-and-connected destinations, only as drafts, and — if unattended — only when the unattended draft-creation knob is on | Same gating as staging; live-prep additionally expects every enabled destination represented in the prepared drafts |
| Publish / schedule-live action | Never a system capability, in any mode | Never | Never — always a manual human action inside the publishing bridge itself |
| Blog/site prep (article draft artifact) | Allowed — artifact-only, no live effect, so no mode restriction applies | Allowed | Allowed |
| Blog/site production merge | Never a system capability, in any mode | Never | Never — always a manual human action |
| Notifications | Always active (filesystem flag baseline always written; push channel per config) | Always active | Always active |

Two rows above are marked "never" rather than mode-gated deliberately: live publishing and production site merges are not capabilities this system has in *any* mode, not capabilities that happen to be switched off in test and staging. This mirrors the assignment's own non-negotiable constraint 1 literally rather than treating it as the strictest end of a gradient.

**What mode does and does not govern on the spending side, stated honestly.** The media-spend row previously read identically in all three modes, which meant the resolver — the one place mode logic lives — had nothing mode-specific to say about the most expensive class of side effect, while what actually made test mode cheap was a **dry-run default sitting in a per-theme block where a theme author could edit it**. Two changes fix that rather than papering over it. The dry-run default is now **engine-level and resolver-enforced**, so test mode genuinely differs from staging in the resolver's own answer and a theme cannot weaken it. And the honest division of labour is written down: **the resolver is the choke point for publish-type effects and for the dry-run boundary; the *magnitude* of permitted spend is governed by the cost gate's caps, which are per theme by design** — because a cap is a business decision per tenant while permission is a safety decision per mode. Both gates read the same resolver (D-35); neither encodes mode logic of its own.

### 11.2 The mode capability resolver: one fail-closed choke point

Every stage about to perform an external side effect — a paid research call against a licensed vendor's credit budget, an LLM call that spends money, a media-generation submission, a publishing-bridge call, a notification send — consults one shared **mode capability resolver** before doing so. This is the single place the capability matrix above is encoded; no stage re-implements its own copy of "is X allowed right now," which is what keeps the matrix from drifting out of sync with itself across the codebase (RA-8).

The resolver's answer is consumed by two named, more specialized gates for the two side-effect families that carry the most risk, rather than by one undifferentiated check everywhere:

- The **cost gate** (canonical, A2/C3/C4) consumes the resolver's answer for spend-type effects — LLM calls, media-generation submissions, licensed-vendor credit spend — checking mode, the relevant budget cap, and (where applicable) brand-confidence band, before the call leaves the process.
- The **publish gate** (canonical, C1/F-4/D-23) consumes the resolver's answer for publish-type effects specifically — it is, per D-23, **the single fail-closed enforcement point** for that family, additionally layering the publish allowlist, connected-channel status and the recorded human-approval state on top of the resolver's mode check (§7.4).

Both gates read from the same resolver rather than encoding mode logic independently, which is what makes this "one choke point" in the sense the risk log asks for: there is exactly one place the answer to "does this mode permit this class of side effect" lives, even though two named, differently-shaped enforcement points act on that answer downstream.

**The resolver's contract, in plain language.** It is asked one question — *may this action be performed on this target in the active mode?* — where the **action** is one of the side-effect classes in §11.1's rows (research read, licensed-vendor credit spend, text-model call, media submission, publishing-bridge call, notification send) and the **target** is the thing acted on (a source, a route, a destination, a channel). It returns three things: **permitted or not**; **a reason code** naming which row and which mode produced the answer, so a refusal is explainable in the digest rather than mysterious; and, where relevant, **the constraint attached to the permission** — most importantly the dry-run flag for media submission, which is a permission qualifier rather than a separate lookup. Two properties are non-negotiable: the resolver **never returns "unknown"**, because an unrecognised action-target pair resolves to *not permitted* with a reason code saying so; and it is **side-effect-free**, so asking it is always safe and no stage can be tempted to skip the question for cost reasons. The specialised gates then layer their own checks on the answer — the publish gate adds allowlist membership, connection status, recorded approval, label acknowledgement and provenance completeness; the cost gate adds the caps and, where applicable, the brand-confidence band.

### 11.3 Fail-closed triggers

Each of the following stops the run at the appropriate named exit class (§8.8) or degrades it to research-only — never proceeds "anyway," and never silently downgrades to a softer behavior than the one it names:

- **Missing secrets.** Any required secret absent or unreadable at theme load is a hard stop (policy-stop or hard-failure, depending on whether the missing secret is theme-specific or infrastructure-level) — there is no silent "skip that provider and continue" for a credential the theme declares it needs. **"Unreadable" here means absent or syntactically unusable, and nothing more**: a credential that is present and well-formed but *invalid in use* — revoked, rotated, permissions withdrawn — is not caught at theme load and is not meant to be. Its validity is discovered by the first stage that uses it, each reporting through its own already-defined path (§6.2). The boundary between these two fail-closed mechanisms is stated so no implementer builds a login check into theme load and no reader assumes one exists.
- **Ambiguous brand truth.** The unattended degrade trigger is exact, not a vibe (stated in full at §6.5, consumed here): the confidence band falls below PARTIAL; any unresolved red-flag conflict exists on a commercially binding fact; the offline brand-truth snapshot is expired or fails its integrity check; the claim ledger could not be read at all (distinct from being legitimately empty); or hard excludes are unresolved (not merely empty). Any one of these routes the run to **completed-degraded**: research-only output, zero brand content, zero media spend, stated as such in the digest.
- **Policy violation.** A claim-gate CONTRADICTED verdict (an asset asserts something the resolved brand facts explicitly deny, §14), a mode/allowlist mismatch, or any other detected policy breach routes to **policy-stop** for the affected asset or run.
- **Mode violation.** An attempted side effect the active mode's row in §11.1 marks as never-permitted (a live-publish call, a production site merge, any publishing-bridge call in test mode) is refused at the resolver before it is attempted, not caught after the fact.
- **A gate that cannot execute.** *(Fifth trigger.)* **Any gate or judgment node that cannot run at all — timeout, outage, unparseable output, a budget ceiling reached mid-pass — fails its artifact closed to that gate's own named degraded outcome, and the gate is named in the pack.** This was previously specified for exactly one node, the brand-fit judgment, whose rule ("if the judgment step cannot run at all… the candidate fails closed to monitor-only. It never defaults open") was correct and applied nowhere else. §8.10's blanket LLM-error rule marks the *artifact* incomplete and says nothing about whether an artifact whose judge errored may still be packed — so an unattended run against a degraded judge endpoint could produce a pack of never-semantically-gated assets sitting beside properly gated ones. A gate that cannot run and therefore does not block is precisely the policy violation the unattended fail-closed mandate exists for. The per-gate degraded outcomes, stated once here and referenced from §14:
  - **Voice judge unavailable** → the artifact enters the pack labelled *"voice gate could not run"*, in the same shape as a cap exhaustion. Never a silent pass.
  - **Claim gate semantic pass unavailable** → **deterministic verdicts only**, and every claim-shaped candidate is **blocked rather than passed**; the pack records that only deterministic coverage was achieved on that asset.
  - **Spin gate unavailable** → the asset degrades to the value-only variant (offer dropped, insight kept, content CTA), which is the same terminal the ladder reaches on repeated failure.
  - **Keyframe-acceptance rubric unavailable** → the slot degrades to plan-only; clip spend is not unlocked (§4.2a).
  - **Platform gate unavailable** → the asset is not marked publish-ready for that destination; hard constraints are never assumed satisfied.
  - **Asset QA rubric unavailable** → the asset enters the pack flagged for human decision, which is what it does on a QA failure anyway.
  - **Post-assembly overlay claim pass unavailable** → the asset is not marked publish-ready and enters the pack flagged for human decision, in the same shape as an asset QA rubric failure.
  - **Resurgence node (N-2) unavailable** → the cluster is suppressed for this run and labelled *resurgence undetermined* (§2.8a).

None of these five trigger classes are configurable away to "warn and continue" — that would defeat the entire point of a system designed to run unattended against a limited budget with nobody watching.

### 11.4 How human-approval states are recorded and consumed

**Recorded.** The **review-decision store** (canonical ledger, §8.6) holds one reason-coded approve/reject/partial decision per asset (and, where useful, per topic or per pack as a whole), with attempt history retained rather than overwritten. **Every approve decision is keyed by run id, asset id, pack revision and a content fingerprint of the bytes it approved** — not by run id and asset id alone.

**Why the key changed.** Packaging's idempotency key gained a pack revision number at §4.7a, because a pack can legitimately change after a human has read it: a later run adopts a pending clip and amends the pack; a regenerate-media-only invocation completes a budget-capped master (§8.11); §12.4's immediate loop regenerates a rejected segment in place. **The approval record did not gain that revision number, and the consequence is that an approval survived the disappearance of the thing it approved.** The claim gate is specified as final and immutable on the exact bytes that enter the pack; the human decision authorising those same bytes was bound to nothing more specific than an identifier that outlives them.

**What the fingerprint covers.** For a text asset, the packed text bytes claim pass 2 closed on. For a media-bearing asset, the mastered export together with its composed overlay string set and its per-destination derivative set — because a re-composition that leaves the video untouched and moves the disclosure is a change the operator has not seen. The fingerprint is computed at packaging, recorded with the pack revision, and carried into the decision the moment one is written.

**The invalidation rule, stated as a rule so no stage has to remember it.** **Any amendment, regenerate or re-assembly that changes an asset's packed bytes invalidates every prior approve decision for that asset and returns it to unapproved**, with the superseding revision named in the record. This binds all three paths uniformly: pack amendment under §4.7a, regenerate-media-only under §8.11, and the immediate loop under §12.4. The **AI-label acknowledgement (§7.7) is invalidated on the same trigger and for the same reason** — a re-assembly can move, shrink or drop the burned-in disclosure, and an acknowledgement of a label that is no longer there is worse than none.

**Rejections are not invalidated, and the asymmetry is deliberate.** A change of bytes expires an approval and never expires a rejection, because the fail-safe direction is unapproved: expiring rejections would let a rejected asset be resurrected by any process that touched its bytes, which is the opposite of what this rule is for. A rejected asset returns to the pack only by an explicit new decision.

**What this control does not do, stated honestly.** It binds the machine to the bytes it showed a human; it cannot bind the human to having looked. An operator who batch-approves a pack without opening a 20–30-minute-review-class video is unbound by anything in this design, and no fingerprint changes that. What it does guarantee is that **the bytes the operator could have looked at are the bytes that publish**, and that any later change puts the asset back in front of them rather than through the gate behind their back.

Each decision additionally carries **the identity of the approving person** and a per-asset **editorial-responsibility-held-by** value — the second condition of the human-editorial-review carve-out (§3.3), and the field that makes "a named natural or legal person holds editorial responsibility" evidenced rather than asserted. It also carries any **pack-amendment records** written when a later run completes a pending master against this run id (§4.7a), so an amended pack's review history stays in one place. **Every recorded decision also carries a decision class**, recording whether the decision was considered or batch-applied without individual asset review. Every whole-pack or whole-language batch approval writes each covered asset's decision with a **decision class** of `approved-unread`, distinct from the ordinary reason-coded per-asset `approved` state; only a decision reached by opening the per-topic or per-asset detail and applying a reason carries the ordinary class. Both satisfy the publish gate's check for a recorded approval state — this adds no gate and slows nothing. It fills a field the store already has room for, honestly instead of silently. **`approved-unread` is never usable as evidence for the human-editorial-review carve-out** (§3.3, OD-24, §16.2) — the carve-out's second condition is not satisfied by a record showing a batch operation swept the asset up without a human reading it. A batch-approved pack is an unevidenced carve-out, and this field is what stops it being invisibly unevidenced. Two input mechanisms write into this same store — they are not two different approval models, only two ways of expressing the same decision: editing a **decision file** that accompanies the run digest (§12), or issuing an interactive console command that references the run id. A rejection is always reason-coded, both because that discipline is what makes the learning loop in §12 trustworthy and because "the topic was wrong" must never be conflated with "I had enough content this week" when feedback is later aggregated.

**Consumed.** The publish gate reads the review-decision store as its human-approval-state layer (§7.4, §11.2): distribution prep will not act on any asset lacking a recorded approve decision, and a partial decision — for example, "approve the copy, reject the video" — is consumed at the individual asset-slot level, never at the whole-topic level, which is exactly the granular rejection model §12 describes. Auto-approve is never config-enabled in v1, in any mode (C4's own open question, resolved conservatively here): every live-affecting decision passes through a human, recorded in this store, before the publish gate will act on it.

---

## §12. Run pack and review package anatomy

The pack anatomy below adopts C4's decision *content* in full — what an operator must see and be able to decide — while replacing C4's interaction *mechanism*, per the synthesis's own correction: **the run digest is a static, human-readable document living with the rest of the run pack's contents, not a web application** (SYNTHESIS §3.11; D-07, C3's no-server reality). Nothing in this section implies a browser back-end, live buttons, or session state; "the operator clicks approve" throughout is shorthand for "the operator edits a decision file, or issues a console command referencing the run id" (§11.4).

### 12.1 The run digest — the single entry point

One document per run, designed to be scannable in about two minutes (C4 §1). It carries, at minimum:

- a header: **run id**, run-date, theme, mode, and a plain-language status line (naming a brand-truth degrade in one sentence if one fired, C6 §5.5);
- a **cost forecast**, prominent, decomposed per topic and **shown as three lines — media, text-per-artifact, and text-per-candidate — never blended**, each reading from the model registry's current price snapshots with its snapshot date rather than any hard-coded figure (so the forecast stays honest as provider prices drift — SYNTHESIS §3.10 corrects an earlier illustrative-figures approach in favor of this; §5.4a owns the three-term decomposition). **The text-per-candidate line is the ranking stage's own spend and it is printed whether or not any pack is produced**, since it is charged on every collection run; it carries beside it the **declared maximum candidate count** the forecast was computed from, the **realised candidate count** that reached node N-1 after deterministic screening, and **which cadence charged it** — so an operator approving spend sees the ranking cost before approving it rather than reconstructing it afterwards from the ledger. A large gap between declared maximum and realised count is not an error; it is the measurement §5.4a's caps are tightened from. The brand-truth verification calls (N-13) are shown inside the text-per-candidate line's breakdown rather than as a fourth headline line, because they are bounded by a declared page set rather than by run volume.
- a topic table: one row per **ranked topic**, each carrying its **scorecard** (sub-scores, confidence band, one-line rationale per dimension, evidence-quality label), freshness and cross-day dedupe status — **the "what changed since a prior appearance" sentence produced by node N-2 inside the ranking stage** (§2.8a), per the **topic cluster key** — and a decision state;
- **a per-asset spin-rationale line**, scannable at one line each rather than only present as a per-asset record, so the operator can judge naturalness by reading down a column. The shape, illustratively: *Topic: mailbox enforcement · ICP: agencies · Pain: deliverability drop · Offer: HypeLead (adjacent) · CTA: content → Czech article · Band: PARTIAL (no pricing, proof blocked)*. If a rationale does not fit one or two lines it is too long to be read, which is itself the test;
- **per-topic completeness reasons, distinguishing the three ways an asset can be absent** — *budget-capped* (the money ran out mid-pack), *count-capped* (the masters allowance was reached), and *deliberately held* (a confidence band too low, the site-first hold, a language-coherence block, or a platform gate refusal). These previously collapsed together and read as one undifferentiated incompleteness; they call for three different operator actions, so each topic row states which applies to it and the exit class distinguishes budget-capped from degraded;
- **a pending-media line per outstanding job with its days-to-deletion countdown** (§4.7), because a pack can outlive its own media if no run follows it;
- degraded-source banners: which sources were unavailable this run and how that is expected to affect coverage (per-source degrade notes, §8.10), **including the *stale payload suspected* reason** (§2.2);
- **a per-language evidence-floor line whenever a language has been below its minimum evidence-and-volume band** for one or more consecutive runs (§2.7), so recurring thinness reads as a named pattern rather than as this week's judgement call;
- **the Czech short-form review line** when the revisit trigger fires (§3.1 commitment 6);
- **an amendment line** when this run completed a pending master belonging to an earlier pack, naming that pack (§4.7a);
- a footer linking to per-topic detail, the full cost breakdown, and any regeneration queue (assets still cycling through the bounded regenerate loop, §14).

Confidence-gated defaults reduce decision load without removing the decision: topics at a high confidence band are presented pre-selected for approval; medium-band topics are presented unselected; low-band topics require the operator to open the per-topic detail before any approval is possible (C4 §1D). Batch operations remain the default affordance — approving an entire pack, or an entire language, in one recorded decision is normal; the granular per-asset override (§12.3) exists for when it is needed, not as the default path. What changes: the digest **states the decision class alongside the batch action itself**, so approving a whole pack or language writes `approved-unread` across every covered asset and the digest says so at the point of action, not only in a later audit. A subsequent per-asset override upgrades that asset's record to the considered class.

### 12.2 Per-topic, per-language contents (the identical-mix rule, W2.5-4)

Under W2.5-4, both configured languages receive the **identical destination × asset-type matrix** — the operator's explicit choice, overruling the synthesis's own lean toward per-language-appropriate mixes, with doubled media spend accepted as the cost of that choice (OP-1 stands). What differs between languages is the **recipe**, not the mix: which production path a given asset type actually uses (owned in full by §4.8, referenced here by pointer only). This section's obligation is that the pack anatomy make the *mix* visibly identical across languages while making the *recipe* difference visible too, so the operator can confirm the Czech assets are not simply the English ones with weaker production values (the reputational risk W2-08 names directly).

Per topic, per language, the pack carries:

- the copy and script assets for every destination the theme's output/runtime block enables, at the identical mix across languages;
- the video plan (shot list or slide list) for every video-bearing asset, always produced regardless of budget (media planning is a zero-cost stage, A2/SYNTHESIS §1.6), plus the generated media itself where the cost gate allowed generation to proceed;
- the **spin rationale** — topic id, detected pain, ICP segment, mapped offer, **mapping distance**, CTA class, and the **fact-usage trace** — so the operator can judge "was this a natural connection" in seconds rather than re-deriving it (C6 §9.4);
- a reference to the **brand-truth snapshot** this topic's pack consumed (by snapshot id and fact-usage trace, not a re-embedded copy), so a later correction to brand truth can be traced forward to exactly the packs it affected;
- claim-check results per asset: which check classes ran, what verdict each extracted candidate received, and the attempt history if any regenerate or downgrade-repair occurred (§14);
- source records for every signal that fed the topic, **in the same two parts as §2.6's provenance snapshot**: a **permanent** part carrying the canonical key, source, domain, extraction method, retrieval timestamp and raw metrics, and a **30-day** part carrying the verbatim excerpt and the direct link to the individual post, replaced on expiry by "excerpt expired — canonical key *K*". The permanent part is what answers "where did this come from" at audit time; the verbatim part is personal data and expires like all the rest (B2 §2.7, C7 §2.6);
- a **provenance record** per generated media asset — the delivered route identity **and its resolution state** (`identity-reported`, `substituted — identity unknown`, or `assumed-as-requested`, §5.6), the version, the generation timestamp, a snapshot of that route's commercial-use terms as they existed at generation time **plus the upstream model provider's own terms URL and read date**, the router transaction id, and delivered-versus-requested route/aspect/resolution where they diverge. **Completeness of this record is a publish-gate check, not merely a pack field** (§7.4, D-20) — an asset whose renderer cannot be identified is not publish-ready and degrades to plan-only with the reason attached (W2-03, C7 §2.8, §8.13);
- **automation metadata** — run id, mode, stage durations, candidate counts at each filtering step, and which cadence produced this run.

### 12.3 The cost gate as an operator-facing checkpoint

Research and ranking complete **at zero *media* cost — not at zero cost** — before anything media-spend-bearing is attempted, and the distinction is load-bearing now that the second wallet is named: **the ranking stage spends text budget on every run, one N-1 call per surviving candidate** (§5.4a), so by the time the operator reads the forecast, the text-per-candidate line describes money already committed rather than money awaiting approval. Media planning genuinely is produced at zero media cost. What the cost gate protects interactively is therefore the **media** decision plus the *remaining* text work — copy generation and the gate stack — and the digest says so rather than implying the run has so far been free.

The cost forecast in the digest is what lets an interactive operator satisfy the **cost gate** directly — reviewing the forecast and giving explicit approval before media generation begins (§9.1). In an unattended run the same gate is satisfied mechanically, against pre-configured caps, with no digest-reading moment involved at all (§9.2); the digest still shows the forecast that resulted, for the operator's next session.

### 12.4 Rejection and regeneration flow

Rejection is granular, recorded at the level it actually applies to, and always reason-coded (§11.4): reject just the video and keep the copy; reject one topic and keep the rest of the pack; reject the whole pack with pack-level feedback. Each of these writes into the review-decision store as its own decision, at its own scope.

Feedback capture feeds three distinct loops, deliberately kept separate so a same-session fix is never confused with a slow, human-governed calibration change:

- **Immediate loop** — a rejected asset regenerates within the current pack, with the specific feedback fed back as corrective context, subject to the **QA-rejection cap** specifically (§4.9 — two per asset slot per pack by default, terminating in "did not clear QA after N attempts"), plus the cost circuit breaker. Naming the counter matters: four distinct regeneration budgets exist and "the same bounded regenerate cap as any other regenerate" did not say which one applied here.

  **Rejection is expressed at the granularity the pipeline can act on, and that granularity is now stated rather than only demonstrated.** The decision file and the console command both expose a **structured segment field** alongside the reason code and the free text: for a multi-shot video the operator names *which shot* failed, addressable because the shot list already numbers rows and each row names the approved keyframe it animates (§4.2); for a carousel, *which slide*. When a segment is named, the immediate loop regenerates **that segment only, reusing the already-approved keyframe** — one clip, not the whole master, which is the difference between a $0.30 repair and a $0.90 re-shoot. When no segment is named, or the reason code is one that cannot be localised (pacing, overall composition, audio), the loop regenerates the whole master and is costed as such. This was previously visible only in the worked example, whose own preamble disclaims it as illustrative rather than binding; it is a rule now, because the economics of the immediate loop depend entirely on which of the two happens.
- **Weekly loop** — aggregated rejection reasons across recent packs inform prompt-library and rubric refinements; this is read and applied by a human, not auto-applied. **No prompt-library or rubric change may be applied without first running the frozen eval set (§14.8) and comparing pass rate, human-agreement rate and token cost against the last known-good version.** Version pinning (§14.7) is retrospective attribution — it answers "did that change help" months later; the eval comparison is regression *prevention*, and without it this weekly loop is an unmeasured edit path into the system's most safety-relevant prompts.
- **Theme-tuning loop** — long-term calibration (ranking thresholds, brand-fit floor, judge cutoffs) is reported monthly and moved only by a logged human rationale; automatic threshold recalibration is explicitly rejected (OD-20, W2-10) because it optimizes for whatever gets rubber-stamped quickly, which is not the north star.

**Post-hoc outcome notes — the third permitted operator input (W7-2).** After a pack's assets are published and engagement is known, the operator may record outcome notes annotating which assets performed well and which did not, with subjective judgement about why. These notes are **inter-run calibration input only** and are **excluded by construction from anything a run reads** — collection, ranking, spin and generation all run with no access to outcome notes. The notes feed the weekly and monthly calibration loops where human judgment is applied manually; they never drive any algorithmic decision. This is what keeps W6-1 intact: outcome notes are annotations about content *already published*, not hand-fed inputs to a run (§17 Phase 7).

### 12.5 Static-file digest, decision mechanism

No web server, no local service, no session state exists in this design (C3, C2's scheduler-agnostic reality). The digest is a static document; a decision is recorded either by editing a plain decision file that sits alongside the digest in the run's own output location, or by issuing an interactive console command that references the run id — both write into the same review-decision store (§11.4). Nothing about the digest's content is diminished by this: it may present headers, tables, confidence bands, and a cost breakdown exactly as rich as a dashboard would, because none of that requires a live backend to render once — it only requires that "clicking a button" be understood, throughout this document, as one of the two recording mechanisms above.

### 12.6 Notion-upload mapping (D-07, later phase, zero re-entry)

An optional, later-phase, config-gated upload of a completed pack's contents into Notion is designed so that it requires no re-entry of anything the pack already contains (D-07). The mapping is conceptual, not a schema:

| Notion destination field | Sourced from |
|---|---|
| Topic | The topic table entry in the run digest |
| Destination / platform | The per-topic, per-language asset set (§12.2) |
| Language | The per-language asset set |
| Content | The copy/script asset body |
| Media reference | The provenance record's route identity plus the re-hosted asset location (never a provider URL, §8.13) |
| Run id | Automation metadata |
| Operator decision | The review-decision store entry for that asset |
| Engagement | Left blank at export time; tracked later, directly in Notion, once the asset is actually live |

This mapping is a later-phase convenience layer on top of an already-complete pack, never a precondition for the pack itself being useful; every field above already exists in the pack for the operator's own review regardless of whether Notion upload is ever enabled.

---

## §13. Multi-theme extensibility

### 13.1 What adding a second theme actually costs

The test of this architecture is not whether a second theme is *possible* but whether adding one is a **configuration and content exercise rather than an engineering one**. Three things must be true, and the design in §1–§12 is what makes them true.

**Nothing about a theme reaches into engine code.** Every stage in the canonical order is theme-agnostic: collection runs whatever source roster it is handed through one of exactly two connector classes (§2.2, reduced from three when the curated inbox was retired under W7-1); ranking applies whatever weights, floors and family memberships it is handed (§2.7); spin performs a lookup over whatever pain-to-offer relation it is handed (§6.9); copy generation composes a brand lock, a theme overlay and a language overlay (§3.4); the gate chain is fixed and its *contents* are configuration (§14); the media router resolves routing axes against a shared registry (§5.3); assembly runs one engine for every theme and language (§4.4). A theme changes the inputs to those stages. It never changes their order, their gates or their enforcement points.

**Everything a theme needs is addressable by pointer.** A theme is a research block, a spin block, an output/runtime block, a publish allowlist per mode, an exemplar corpus pointer per language, and a set of designated fact locations in a knowledge base (§10). The three things that would otherwise be "code" are not: the language overlay is shared per language across all themes, the model registry is engine-level, and the do-not-scrape list is engine-level and binding on everyone.

**The safety properties are inherited, not re-implemented.** A new theme cannot accidentally publish, because the publish allowlist is empty in the default mode and the publish gate is the single enforcement point (§7.4, §11.2). It cannot accidentally spend, because both cadence knobs default off, dry run defaults on in test, and every cap is enforced before submission (§10.4). It cannot accidentally invent claims, because the five non-disableable check classes are engine-level and an unresolved claim ledger is a degrade trigger regardless of theme (§6.5, §6.7).

So the realistic cost of theme #2 breaks into four buckets, only one of which is engineering:

| Bucket | What it is | Realistic effort | Is it engineering? |
|---|---|---|---|
| **Configuration** | The three theme blocks plus the allowlist — topics, sources, ICP map, offers, CTA classes, destinations, caps, cadence. The knob surface is ≈130 settings, but a new theme author decides **eleven** of them and inherits the rest from engine defaults, the shared language overlay and the standard source portfolio — that **minimum viable knob set is enumerated at §10.1**, and it is what makes the estimate below credible rather than optimistic | Hours, mostly deciding rather than typing, against eleven decisions | No |
| **Router account provisioning** *(only if the operator declines the global spend lock)* | A separate router sub-account per theme, so balance-delta reconciliation stays interpretable when two themes can run concurrently against one prepaid balance (§5.4) | Under an hour, plus splitting the balance | No, but it is a real onboarding step and is not free |
| **Brand-truth content** | Designated fact locations populated in the knowledge base: identity, offers with status, positive and negative capability statements, ICP map, CTA set, claim ledger, proof allowlist, hard excludes | The real work — days, and it is the client's work, not the engine's | No |
| **Corpus** | A per-language exemplar corpus of material that sounds like this brand, plus a golden set if the theme introduces a language the system has not written before | Days for a new language; hours for a new theme in an existing language | No |
| **Genuinely new engineering** | Only when a theme needs a source no connector covers, a destination no format profile covers, or a language with no overlay | Per item, and each is an additive registry or overlay entry rather than a change to the pipeline | Yes, but bounded |

That last row is where honesty matters. A new **source** is a new collector or a new MCP source and enters through the method-evaluation gate (§2.4) — additive, and it inherits ladders, budgets and the do-not-scrape list. A new **destination** is a new format profile in §3.3 plus an allowlist entry plus a connector in the publishing bridge — additive, and it inherits the platform gate. A new **language** is the expensive one: it needs its own slop lexicon, register norms, CTA phrase bank, on-screen-text conventions, a structural-calibration corpus and a judge golden set, exactly as Czech does (§3.4, §17 Phase 0). This is deliberate — the alternative is a translation pass, which D-02 forbids. **A new language is a project; a new theme in an existing language is configuration.**

### 13.2 Theme-readiness validation as the proof

Multi-theme readiness is not asserted by argument; it is asserted by a validation pass the operator can run on demand and which the scheduler refuses to bypass. Readiness runs the cheap half of a real run — theme load, brand-truth resolution against the live knowledge base and the live site, a dry collection pass, a ranking pass on whatever it collected — and then makes a set of assertions. The ones that matter most:

- **Every blocking fact class resolves** to values or to a legitimate resolved-empty state; unresolved is a failure and names itself (§6.5).
- **Every configured language produces a non-empty candidate set.** This is the assertion that catches the failure mode W2-07 describes, where a language dies quietly by arithmetic while every policy document still calls it first-class (§2.7).
- **Every configured language has a non-empty, quality-gated asset matrix**, so "cs equals en minus video" can never arrive by omission (§3.2).
- **Every enabled destination has a format profile, an allowed CTA class in each configured language, and a live CTA destination URL**; a Czech asset pointing at a page with no Czech version is surfaced as a known degraded state rather than shipped silently (§6.9).
- **Every configured language has a product-CTA destination that resolves *and returns content in that language* — or the theme carries an explicit, dated acceptance that it does not.** The CTA-language-coherence rule already handles the runtime case correctly: a Czech product page returning 404 degrades that asset's CTA to a content class and the pack says why. What it does not do is stop the degradation from becoming permanent and invisible: week one it is a noted state, week eight it is the background. So the assertion is bidirectional — either the destination resolves in that language, or the theme holds a **language-completeness declaration** (for example, *"the Czech product page does not exist; degraded Czech CTAs are accepted until date D"*) which is **carried as a banner in every run digest until it is cleared or expires**. A known funnel gap becomes a logged operator decision with a date on it rather than a silent operational state that compounds weekly.
- **Every configured language is above its minimum evidence-and-volume band** at the last readiness run, or the failure names the language and the shortfall (§2.7). Non-empty is necessary and not sufficient.
- **No enabled asset requests a capability its selected route cannot supply** — the two live cases being word-level caption reveal on the subtitles-only path (§4.4) and a reference-mode shot list whose durations exceed the mode's fixed quantum (§4.3). Both are caught here, at zero cost, rather than at submission.
- **Every configured source has a method, a budget, a ladder and a source-family membership**, and no source's method is one the do-not-scrape list forbids.
- **The ranking stage's declared maximum candidate load fits inside its own ceilings.** The sum of every enabled source's result cap × per-run page allowance, across every configured language and query, multiplied by N-1's one call per candidate at its per-call token ceiling — and by N-2's worst-case additional call per candidate carrying prior-pack state — is **measured at theme load against the ranking stage's per-stage call ceiling and against the per-run text budget** (§5.4a). A theme whose declared roster cannot fit fails readiness **with the contributing sources named and their individual contributions listed**, so the operator sees which cap to lower rather than a single failing total. This is the same shape as the readiness-time fit measurement already applied to resolved prompt length against the per-node input ceiling, and for the same reason: **a limit discovered at run time is a truncation, and a truncation in the ranking stage is a silent, order-dependent loss of candidates.** The measurement uses declared maxima and is therefore conservative by construction; that is the intended direction of error. The named remedies are all existing knobs — lower a per-source result cap, lower a per-run page allowance, raise the ranking call ceiling, or raise the per-run text budget — and the last two are stated as spend increases rather than as fixes, because they are.

**A second clause on the same assertion, because the cadence multiplies it.** The per-day and per-month text caps must accommodate this term **multiplied by the research-collection cadence**, not by the pack-production cadence (§8.2, Block 4). The existing readiness check that the two cadence knobs are mutually consistent is extended to carry this arithmetic: a theme collecting daily pays the ranking term seven times a week regardless of how few packs it produces, and **a monthly text cap sized against pack production will be exhausted by collection long before the operator connects the two events.**
- **The publish allowlist is a subset of the connected channels for the active mode**, and contains no research source (§7.4).
- **Both cadence knobs are either off or mutually consistent** — pack production never configured to outrun the collection window that feeds it (§8.2).
- **The exemplar corpus resolves and is excluded from every factual retrieval path**, and the corpus-leakage class is enabled (§6.11).

A theme failing readiness may still be run interactively in test mode, which is how a new theme is built up. It may never be scheduled. That single rule is what stops a half-configured tenant from producing confident nonsense at three in the morning.

### 13.3 A second-theme fixture, walked

To prove the configuration surface generalises rather than merely claiming it, here is a deliberately different second theme. It is a *fixture* — a worked configuration used to test the engine, not a commitment to a real client.

**Theme #2: a Czech e-commerce shipping-and-returns automation product**, sold to Czech online-shop owners and their operations staff. Single language: Czech only. The company sells one product with two plans, publishes a Czech-language blog, and reaches its audience mainly on Facebook and in Czech e-commerce communities rather than on LinkedIn.

Every difference below is a configuration value, a corpus, or a knowledge-base pointer. None is an engine change.

| Dimension | Theme #1 (HypeDigitaly / HypeLead) | Theme #2 (Czech e-commerce fixture) | What kind of change |
|---|---|---|---|
| **Language array** | Czech and English | Czech only | Configuration value; the language overlay is reused unchanged |
| **Watch topics** | AI, coding agents, lead generation, outbound and AI-sales discourse | E-commerce operations, shipping and returns, marketplace policy changes, seasonal peak logistics, Czech online-retail platform ecosystem | Configuration value |
| **P0 sources** | Developer-discourse hub, AI newsletters, launch registries, model hub, open social firehose | Czech tech and e-commerce trade press feeds, Czech retail-association publications, the demand-data vendor at Czech geography, the ad libraries for Czech-targeted retail advertisers | Roster values; **all use connector classes that already exist** |
| **Sources dropped** | — | The developer-discourse hub, the model hub and the launch registries drop to P2 or off — they carry almost no signal for this audience | Roster values |
| **Curated inbox** | Weekly threaded-community pain session plus professional-network observations | Czech e-commerce Facebook groups and two seller forums, same ritual shape, same staleness flag | Same source type, different contents |
| **Trend-intelligence vendor** | On, trial-gated, for the short-form axis | **Off** — no short-form axis in this theme's mix, so the credit budget is not spent | Configuration value; the axis degrades by design, not by breakage |
| **Ranking composite** | English candidates use the four-factor composite; Czech candidates drop the virality factor | **Every** candidate drops the virality factor, because this theme has no counted-evidence source at all | No code change — this is the existing per-language rule applied to the only configured language |
| **Evidence classes present** | Counted, ranked, human-asserted | Ranked and human-asserted only; the absolute-band fallback is the permanent state rather than a cold-start state | Configuration and an honest label in the pack |
| **ICP map** | Agencies, B2B marketing teams, sales directors, GTM and lead-gen practitioners, users of named outbound tools | Shop owners, e-commerce operations managers, customer-support leads at small retailers | Knowledge-base content |
| **Offers and mapping** | Several offers across two brands and two domains, so brand routing is load-bearing | One product, one domain — the brand-routing map is trivial but still present, and the wrong-brand-CTA check simply never fires | Knowledge-base content |
| **Destinations** | LinkedIn, Instagram, TikTok, YouTube Shorts, Facebook, X off, blog drafts | **Facebook primary**, Instagram secondary, blog on, LinkedIn light, **TikTok and Shorts off**, X off | Matrix values; the platform gate's profiles already exist |
| **Video recipe** | English generative-clip led; Czech carousel-to-reel | Carousel-to-reel only, with Czech text-to-speech; no generative clips at all | Recipe value; **the same fork, the same assembly engine** |
| **Media budget** | Sized for two languages at standard tier | Roughly half, because there is one language and no generative clips | Cap values |
| **CTA classes** | Content, product-path, event and commercial-incentive all in play | Content and product-path only; no affiliate programme, so the commercial-incentive class is disabled and its required-disclosure check never fires | Enablement values |
| **Register** | Formal by default, informal only where a peer-community context is declared | Formal by default; **informal declared for the seller-community destination**, consistently within an asset | The one setting that permits informal register, used deliberately |
| **Exemplar corpus** | Competitor posts, GTM playbooks, practitioner transcripts | A different corpus entirely: this brand's own newsletters and its founder's community posts | Corpus content; still style-only, still leak-checked |
| **Claim ledger** | A typed database in the shared knowledge base | A different typed database in the same workspace, different designated fact locations | Pointer value |
| **Cadence** | Daily collection, packs a few times a week | Weekly collection, weekly packs — a slower market with a strong seasonal peak | Cadence values, both still default-off until enabled |

**What this fixture proves, and what it exposes.** It proves that the destination matrix, the source roster, the ranking treatment, the recipe fork, the CTA classes and the register rule are all genuinely parameterised — a theme with no English, no short-form, no generative video, no second brand and no counted-evidence source still walks the same canonical stage order through the same gates. It also exposes two things worth naming honestly. First, **a single-language Czech theme runs permanently in the state the first theme only visits during cold start** — no counted evidence anywhere — which makes the honest "under-evidenced ≠ poor fit" labelling in §2.7 load-bearing rather than a nicety, and makes the readiness assertion about a non-empty candidate set the difference between a working theme and a silent one. Second, **the Czech-language investment is amortised**: because the language overlay is shared and theme #1 already paid for the Czech slop lexicon, register norms, CTA phrase bank and judge golden set, theme #2 inherits all of it and needs only its own exemplar corpus. That is the concrete return on refusing to fold the language overlay into the theme overlay (§3.4).

### 13.4 What would have to change for a theme this design cannot yet serve

Stated so that the extensibility claim is falsifiable rather than decorative. A theme needing **a language the system has never written** pays the full new-language cost above. A theme needing **a destination with fundamentally different asset physics** — long-form video as the primary format, or a podcast feed — needs a new asset type and its own review-depth profile, which is additive but not free. A theme whose **brand truth does not live in a knowledge base the reader can address** needs either a migration into one or a new reader implementation behind the existing brand-truth resolver seam. A theme requiring **live publishing** is out of scope by design in every mode (§11.1) and would be a different product, not a configuration.

---

## §14. Voice and claim-safety enforcement by design

This section describes one coherent layered gate, not three independent checks bolted together, and **it is the sole owner of the per-asset gate chain (§0.2)**. The chain was previously drawn in three places — here, at §9 and inside §6.10's diagram — with three different contents, and the three disagreed about the two steps that exist precisely because they are easy to forget. An implementer building from the shortest of the three would have shipped media assets whose on-screen claim-bearing text was never checked by anything. §9 now owns the **run-level** stage order and points here; §6.10 owns the spin criteria and points here; **where any other section's ordering appears to contradict this one, this one governs** (SYNTHESIS §4.4, D-21, binding).

The canonical per-asset chain, in full, once:

    generate
      -> SPIN GATE                  "is this the right thing to say?"
           (the angle-level pre-check already ran before any drafting
            tokens were spent; this is the artifact-level post-check, §14.1)
      -> CLAIM GATE pass 1          "is it true and allowed?"  (fail fast)
      -> VOICE GATE                 "is it said like a human, in this
                                     language?"
      -> CLAIM GATE pass 2          final, immutable, on the exact packed
      |    |                         TEXT bytes
      |    +-- a pass-2 repair is itself a rewriting step, so:
      |        RE-ENTER -> VOICE GATE -> SPIN post-check -> CLAIM pass 2
      |        (every lap counted against the combined per-artifact repair
      |         ceiling, §14.0; on exhaustion take the downgrade-repair
      |         variant, never another lap — §6.10)
      v
      -> PLATFORM GATE              "does it fit this destination's hard
                                     limits?"
      |
      +-- text-only assets go straight to PACKAGING from here
      |
      -> media planning             always produced, zero cost
      -> COST GATE                  media-bearing assets only
      -> media generation           asynchronous; may span runs (§4.7a)
      -> ASSEMBLY, or static-asset composition for assets with no motion
           (§4.4, §4.4a) -- all message-bearing on-screen text is composed
           HERE, which is AFTER claim pass 2 closed
      -> POST-ASSEMBLY OVERLAY CLAIM PASS
           deterministic claim classes re-run over the composed overlay
           string set, per asset (§4.4 rule b)
      -> ASSET QA RUBRIC
      -> PACKAGING                  keyed on run id + included asset ids +
                                     pack revision (§4.7a)
      -> HUMAN REVIEW GATE          the approval is bound to these exact
                                     packed bytes (§11.4)
      -> PUBLISH GATE               seven fail-closed checks (§7.4)
      -> distribution prep

**The post-assembly overlay claim pass is not a second opinion; it is the only opinion that surface ever gets.** For a text asset, claim pass 2's promise — final and immutable on the exact bytes that enter the pack — is literally true. For a video, a carousel or a feed still it is not: the bytes that enter the pack are pixels and audio, and every claim-bearing string burned into them is composed at assembly, after pass 2 has closed. The "300% ROI" graphic §6.7 names as *exactly the artefact type that escapes text-only checking* is composed in that window. Without this pass it escapes.

**Which classes it runs, and why that set and not another.** The overlay pass re-runs the **deterministic** classes of §6.7 over the composed overlay string set: **numeric quantity (1), currency and price (2), named entities (3), superlative and absolute (5), endorsement and social proof (9), required-statement including the AI-disclosure and commercial-communication sub-classes (10), and corpus leakage (11)**. That set is not arbitrary and it is not a compromise: **all five never-disableable classes — the ones whose failure is a legal exposure rather than a quality miss — are deterministic, so all five run here.** Every overlay string is known text drawn from a pre-verified slot, so the pass is a pattern, dictionary and entity comparison over a few dozen short strings. It costs no model call and adds no measurable time to assembly, which is the reason there is no argument for skipping it under budget pressure.

**What it cannot do, stated rather than glossed.** The semantic classes — outcome (4), capability (6), temporal (7), comparative (8) — are not re-run here, so a composed juxtaposition that *implies* an unsupported outcome without containing a checkable token is not caught by this pass. That gap is closed structurally rather than by inspection, by §4.4's slot discipline: overlay composition may only place pre-verified strings into pre-verified template slots, and a template declares which slot pairs may occupy the same frame. **Slot discipline is a template-authoring control and the overlay pass is a runtime control, and neither substitutes for the other** — the honest statement is that the runtime pass catches the unsupported token and the template catches the unsupported juxtaposition, and a template authored carelessly is a hole this section does not fill.

**Disposition.** A failure blocks the asset from publish-ready and routes it to the QA-flag path (§4.9) with the offending string or slot pair named; it does not fail the run and does not discard the paid render. Because assembly is zero marginal cost (§4.4), an overlay failure is repaired by recomposing, not by regenerating — the cheapest repair in the entire pipeline, and one more reason its absence was expensive.

This ordering is deliberate on two counts, both load-bearing rather than stylistic. **Spin precedes voice** because the two failures need different repairs — a spin failure means the topic/offer pairing was wrong and the fix is to drop the offer or change the angle, never to reword; a voice failure means the phrasing is wrong and the fix is a rewrite. A well-voiced piece of forced relevance is *harder* for a reviewer to reject than a clumsy one, so checking connection honesty before polish prevents good prose from laundering a bad idea (C5 §7; C6 §9.5). **Claim checking happens twice over text and, on any media-bearing asset, a third time over the composed overlay strings.** The two text passes bracket the voice gate because the voice gate rewrites text, and a rewrite can silently reintroduce a claim an earlier pass had already cleared — the last gate before packaging must see the exact bytes that will ship (D-16; C6 §7.3). The third pass exists because for media the bytes that ship are not text at all, and *the last gate before packaging* and *the last gate over claim-bearing language* are two different moments (§4.4). Saying "the claim gate runs twice" without that qualifier is what let the overlay pass fall out of two of this plan's three drawings of the chain.

This ordering is deliberate on two counts, both load-bearing rather than stylistic. **Spin precedes voice** because the two failures need different repairs — a spin failure means the topic/offer pairing was wrong and the fix is to drop the offer or change the angle, never to reword; a voice failure means the phrasing is wrong and the fix is a rewrite. A well-voiced piece of forced relevance is *harder* for a reviewer to reject than a clumsy one, so checking connection honesty before polish prevents good prose from laundering a bad idea (C5 §7; C6 §9.5). **The claim gate runs twice, bracketing the voice gate,** because the voice gate rewrites text, and a rewrite can silently reintroduce a claim an earlier pass had already cleared — the last gate before packaging must see the exact bytes that will ship (D-16; C6 §7.3).

### 14.0 The repair budget, across all gates

Four gates can each cause a rewrite, and each previously carried its own counter with no stated interaction — a per-artifact voice cap, a per-pack claim allowance, a one-regenerate-then-downgrade spin ladder, and (added at §4.9) a QA-rejection cap. Two of those are per artifact and two are per pack, they are explicitly coupled (a voice regenerate can create a claim failure, which draws down the pack's claim allowance), and the repair re-entry rule at §6.10 adds a fifth path between them. Without a single outer bound, the per-artifact worst case across all of them was unstated and unbounded in practice.

**The combined per-artifact repair ceiling** is that bound: a small fixed number counting **every repair attempt on one artifact across every gate** — spin regenerate, claim pass 1 regenerate, voice regenerate, claim pass 2 regenerate, and any re-entry those trigger. The individual counters still apply inside it and still do their own work; the ceiling is what stops two gates ping-ponging an artifact between them while each stays within its own budget.

**Check order and exhaustion, stated so two implementers build the same thing:**

1. The **combined per-artifact ceiling** is checked first, on every repair of any kind. If it is exhausted, no further repair of that artifact is attempted by any gate: the artifact takes the **downgrade-repair variant** if one exists for the failing gate (value-only for spin, claim-free for claim), and otherwise enters the pack labelled with the gate it could not clear.
2. The **per-pack budgets** — the claim-retry budget and the per-pack voice-regenerate allowance — are checked next. If either is exhausted, that gate stops regenerating for the rest of the pack and **the pack degrades to review-required**; remaining artifacts are still gated, still labelled, and still packed, they simply are not repaired.
3. The **per-artifact counters** are checked last, and are the ordinary limit in normal operation.

**A pack whose claim allowance is exhausted still permits voice regeneration**, and vice versa — they are independent budgets — but both remain subordinate to rules 1 and 2, so exhaustion of either still ends in a bounded, named, honest state rather than in a loop.

### 14.1 Spin gate

Two checkpoints, not one (C6 §9.5, C5 §7): an **angle-level pre-check** immediately after brand-spin resolution and before any drafting tokens are spent, and an **artifact-level post-check** on the finished draft, catching drift that crept in during writing — a soft, hedged mention in the brief becoming a confident, unhedged claim by the time the copy exists.

Both checkpoints evaluate the same **seven criteria S-1…S-7 — real topic anchor, ICP addressing, connection chain, distance compliance, proof discipline, next-step correctness and no hype-glue — which are stated once, with their failure modes and their evidence requirements, in the table at §6.10.** They are not restated here. Two of them are worth remembering while reading this section, because they are the ones the artifact-level post-check most often catches: **S-3** requires that deleting the offer-mention paragraph still leaves a genuine point, and that deleting everything else still leaves something specific to *this* topic rather than something pastable onto any trend; and **S-4** fails a far-distance topic outright the moment it carries a product pitch (mapping distance is defined at §6.9).

Enforcement: fail on a specific criterion → bounded regenerate citing that criterion → second failure → **downgrade to the value-only variant** (drop the offer, keep the insight, content-class CTA only) → still failing → drop the asset with the reason recorded, never silently. The value-only downgrade matters because most spin failures are failures of the pairing, not of the writing — the correct repair is usually to stop selling, not to rewrite harder (C6 §9.4).

### 14.2 Voice gate

Five layers, cheapest and most mechanical first, most expensive and judgment-heavy last (C5 §2). Nothing here is ever silently shipped, and nothing is ever silently dropped — a failing artifact still enters the pack, explicitly labeled, with its full attempt history attached.

1. **Lexicon screen** — deterministic, near-zero cost, per language. Catches the assignment's seed list of banned phrases and patterns, plus a **cross-pack recurrence check**: comparing a new draft's opener and core phrasing against a rolling window of the theme's own recently generated artifacts, per platform and language, to catch the *system* developing its own repeated house tic — the same failure mode observed directly in the exemplar corpus, where near-identical templates recur across different named authors (C5 §2, fact ledger). This is **house-style-tic drift monitoring**, and it is a standing, always-on check, not a one-time calibration step.
2. **Structural heuristics** — sentence-length variance, em-dash density, bullet vagueness versus bullet density, opener repetition; calibrated from the theme's own exemplar corpus rather than a universal number, and always followed by the LLM judge, never allowed to independently accept or reject on its own (C5 §2, Layer 2).
3. **LLM judge** — semantic evaluation against the full voice rubric (§14.4), producing a structured pass/fail per criterion plus a diagnosis and fix category. The judge is a different call, ideally a different model lineage, from the generator, to reduce shared blind spots (C5 §2, Layer 3).
4. **Bounded regenerate loop** — on judge fail, regenerate with the judge's diagnosis fed back as corrective context, up to a hard, configurable **regenerate cap counted per artifact**, and — the addition that makes the bound real — a **per-pack voice-regenerate allowance** counted across every artifact in the pack. The per-artifact cap alone was described as "the primary circuit breaker on worst-case unattended cost", and it is not: a two-language pack carries roughly sixty text assets across seven destinations, so a per-artifact cap of *c* bounds the pack at 60 × (1 + *c*) generation calls **and** 60 × (1 + *c*) judge calls — which is a multiplier on a large base, not a ceiling. The claim gate had already diagnosed exactly this failure and fixed it with a per-pack allowance and the reasoning to match (§6.7); the voice gate simply did not inherit the fix. **The correct statement is that the per-artifact cap bounds the worst case *per artifact*, and the per-pack allowance is what bounds the worst case *per run*** (C5 §4). Exhausting the per-pack allowance degrades the pack to **review-required** and stops further voice regeneration for that pack; artifacts still enter the pack, labelled.
5. **Escalate to review** — terminal. If either cap is reached without a pass, the artifact ships into the pack clearly labeled "did not pass voice/spin gate," with full diagnosis and attempt history, never force-shipped as a best effort and never quietly dropped (C5 §2, Layer 5). **If the judge itself could not run**, the artifact takes the same shape with a different label — *"voice gate could not run"* — under the fifth fail-closed trigger (§11.3). A gate that is unavailable never defaults open.

**Judge calibration and the false-positive economics.** A golden set (adapted positives, deliberate negatives, real borderline drafts from pilot runs) supports human-vs-judge agreement measurement, tracked **by direction** rather than as one blended accuracy number: judge-passed/human-failed (the dangerous direction — slop ships) is tuned separately from judge-failed/human-passed (the expensive direction — wasted regenerate cycles and review-queue flooding), because the two carry different business costs (C5 §4). A rolling **flag-rate ceiling** is tracked per theme/platform/language as a judge-health signal distinct from any individual artifact's flag — a flag rate meaningfully above what golden-set calibration predicted is a warning about the judge or the generator, not a queue to keep waving through. When launching a new theme or language pair with limited calibration data, the recommendation is to start lenient and tighten as real agreement data accumulates, because an under-strict judge costs a little extra human attention while an over-strict judge in an unattended context costs hard tokens and throughput that compounds silently (C5 §4).

**Both languages get a golden set and a structural-calibration pass in Phase 0, not just Czech.** The flag-rate ceiling is defined against "what golden-set calibration predicted", and layer 2's structural bands are "calibrated from the theme's own exemplar corpus" — and Phase 0 originally built *only* the Czech artefacts, on the reasoning that Czech is the one that does not transfer from English. True, and incomplete: without an **English golden set** there is no predicted baseline for English, and without an **English structural-threshold measurement pass** over the English corpus, layer 2's numeric bands are undefined for English too, because the exact cutoffs need a real tokenisation and measurement pass that the source brief explicitly deferred. The consequence was concrete — the English voice gate would run from Phase 2 through Phase 6, including the eight-to-ten trial packs and the first unattended runs, against an uncalibrated judge and undefined structural bands, with the judge-health signal not existing until Phase 7 delivered it. Both English artefacts are now Phase-0 deliverables alongside the Czech pair, and the do-not-start-Phase-1 gate covers all four (§17). Until a golden set exists for a language, that language's judge **runs deliberately lenient and its flag-rate ceiling is recorded as inactive** rather than described as a control that is quietly not instrumented.

### 14.3 Claim gate

Two halves that must not be merged (C6 §7.1): the **claim ledger** (what may be said — §6.3) and the **claim check** — a verification pass over generated bytes — owned here. The check runs over every generated surface in every language: post bodies, hooks, captions, carousel slide text, on-image text, video scripts and spoken lines, alt text, blog copy, CTA text, and hashtags (a hashtag can itself carry a claim). Deterministic extraction runs first and is followed by semantic checking, never the reverse — an LLM-only checker is non-deterministic and can be argued out of a block by the same model family that wrote the copy; a component's self-assessment is not a control over that component (C6 §7.1).

**The eleven check classes are defined once, with their rules and their Czech-specific extraction requirements, in the table at §6.7**, and are not restated here. Three of them carry consequences that belong to this section rather than to the brand-truth layer. **Capability/autonomy** is checked against both positive *and negative* capability statements, which is what lets a claim like "sends for you" fail with zero digits present — the highest-frequency overclaim class in this niche, and one a numbers-only checker would never see. **Required-statement** is bidirectional — a *missing* mandatory disclosure is a defect of the same class as a false claim — and it is exactly where the AI-label obligation in §14.6 attaches. **Corpus leakage** blocks generated numbers, metric phrases or named entities that appear in the exemplar corpus but nowhere in the claim ledger, and records a leakage event, because a rising leakage rate is the signal that the few-shot design is bleeding facts (§6.11).

Verdicts: VERIFIED, SAFE-NON-CLAIM, UNSUPPORTED (blocks), CONTRADICTED (blocks and raises a brand-truth review flag, since it may mean the ledger itself is wrong), DISCLOSURE-MISSING (blocks until inserted). Enforcement ladder, per asset, never per pack and never per run: block → bounded regenerate (a small fixed maximum, fed the specific failing spans and a positive constraint) → downgrade repair (emit the claim-free variant — value-only, no proof, softer CTA) → drop the asset with the reason recorded. The **retry allowance is budgeted per pack, not per asset** — otherwise a systematically bad prompt in an unattended run burns the token budget on a single regeneration storm; exhausting the pack's allowance degrades that pack to review-required rather than failing the whole run (C6 §7.3).

**The claim check runs twice** for the reason given at the top of this section: pass 1 fail-fast, early; pass 2 as the final immutable gate on the exact bytes entering the pack, because the voice gate's rewrite is what pass 2 exists to catch (D-16).

### 14.4 Per-language rubrics

**English** is exemplar-grounded, authored directly from the local corpus of real winning posts (C5 §3): hook shape, specificity/proof anchoring, personal stake, rhythm, structure, and CTA target-versus-tone are each stated as a pass bar and a fail smell drawn from what the corpus actually does — with an explicit design note that the corpus's craft is borrowed while its hype language and gamified hard CTAs are explicitly rejected, because several of the corpus's best-performing posts would fail this project's own rules if reproduced verbatim.

**Czech** is concrete now, not a placeholder framework, filled from B4's empirical findings via C5 §2c (SYNTHESIS §2c). It carries its own three-layer structure mirroring §14.2's five-layer stack at the language level: a **calque blocklist** with named native alternatives (so a regenerate instruction is actionable, not just "this failed"); structural tells specific to Czech (openers, hedge stacking, formality flips); and a **code-switching allowlist** that is a permission list, not only a block list — English nouns naming tools, metrics and categories are normal Czech tech register and must not be flagged, while English-rooted verbs and abstract benefit nouns are the actual slop. A Czech soft-CTA phrase bank is mapped to the same CTA classes the claim gate and spin gate already use.

**The eleven dimensions, enumerated — because "an eleven-dimension rubric" followed by five or six named items is a dangling promise, and because it matters whether a dimension is inherited or Czech-specific.** The rubric is **five dimensions inherited from the English rubric, five Czech-specific, and one Czech override**:

*Inherited from English (§14.4's English rubric), evaluated against Czech-calibrated bars rather than English ones:*

1. **Hook shape** — and, as the Czech-specific pass bar, this is where **design commitment 2 becomes machine-checkable**: the hook must be a direct statement of a problem or a specific observation. The named fail smell is a **transplanted English hook rhythm** — the scene-setting throat-clear, the curiosity-gap tease, the "here's what nobody tells you" cadence — rendered in Czech words. This dimension is the one that previously had no gate, no knob and no rubric row while §15.4 counted it among the enforceable commitments; it is now enforceable and §15.4 is corrected to match.
2. **Specificity and proof anchoring** — concrete, attributable, ledger-backed; vagueness dressed as insight is the fail.
3. **Structure and formatting** — paragraphing, bullet discipline, and the bullet-vagueness-versus-density balance layer 2 measures.
4. **CTA target versus tone** — one CTA, of an allowed class, whose phrasing matches the register the rest of the asset uses.
5. **Absence of banned patterns** — the engine and theme lexicons, plus the cross-pack recurrence check's house-tic finding.

*Czech-specific:*

6. **Calque avoidance** — against the blocklist, with the named native alternative supplied so a regenerate instruction is actionable rather than merely negative.
7. **Register consistency — vykání by default**, throughout the asset, in every public post and first-contact CTA; tykání only where theme config declares a peer-community context (resolving an internal conflict in the source research, D-26). Mid-asset register flips are a fail in either direction.
8. **Code-switching compliance** — the allowlist is a *permission* list as much as a block list: English nouns naming tools, metrics and categories are normal Czech tech register and must not be flagged, while English-rooted verbs and abstract benefit nouns are the actual slop.
9. **Czech structural tells** — Czech-specific openers, hedge stacking, and the direct Czech analogue of the "in today's fast-paced world" opener.
10. **Sentence rhythm against the Czech band** — Czech sentences run longer by default, so the variance band is measured from the Czech structural-calibration corpus and never inherited from English.

*Czech override:*

11. **Human-voice weighting** — the same dimension the English judge scores, weighted **higher** here, because Czech professionals detect and distrust AI-generated copy more readily and the cost of a slip is empirically higher in that market (C5 §2c). This is a weight, not an extra test, which is why it is counted as the override rather than as a twelfth dimension.

**Phase 0's Czech rubric is a hypothesis, not a law.** The Czech exemplar corpus does not exist until Phase 0 builds it, so the empirical basis for these bars is genuinely weaker than English's. The rubric therefore enters Phase 0 as the hypothesised set, the Czech golden set is built against it, and **the human-versus-judge agreement data from that golden set decides which dimensions actually discriminate Czech voice for this brand** — dimensions that do not are down-weighted or merged, with the change logged like any other threshold move (OD-20). Locking the rubric before the corpus that justifies it exists would be the same error as setting a threshold from a vendor blog.

### 14.5 Spoken-claim enforcement

Three rules, in order of primacy (C6 §8):

1. **Script-lock is the primary control.** Spoken content is generated only from claim-checked script text; the script is the verified artifact of record, and audio is a rendering of it, never an independent source of claims.
2. **In unattended runs, spoken lines carry zero claim tokens** — no numbers, currency, entities beyond the theme's own brand, superlatives, or outcome statements. All claim payload lives in burned-in on-screen text, composed at assembly time from verified strings, which can be re-read before packaging. This deliberately drains the audio channel of anything a model's improvisation could fabricate that would actually matter.
3. **ASR runs as a sampled adherence monitor, never as the per-asset gate.** Its job is to measure whether the model said what it was told, on every asset during the first weeks and then a rolling sample thereafter, and always after a provider or model change. A measured adherence drop is a provider-level alarm that can disable audio for that route — it is not a pass/fail check on any individual asset.

**The four-part argument for this ordering — preventive beats detective under budget caps, it reuses a stronger deterministic substrate, it is language-neutral by construction, and its failure direction is the right one — is made once at §6.8** and is not repeated here. The operative consequence for this section is that rule 2 is what makes script-lock's honest weakness (adherence is a behaviour, not a guarantee) non-consequential: a model that paraphrases or ad-libs cannot fabricate anything that matters, because nothing that matters was ever in the audio channel to begin with.

### 14.6 AI-labeling and provenance placement (F-8, W2-04)

**The burned-in, human-perceivable disclosure applied at render time is the load-bearing compliance control**, not a courtesy. EU AI Act Article 50 became binding on 2 August 2026, with no size exemption and fines up to €15 million or 3% of worldwide turnover (C7 §2.4). Because major platforms re-encode nearly every upload — stripping C2PA Content Credentials in the process, characterized as effectively total removal — metadata-only compliance fails silently (C7 §2.4a; F-8). Every AI-generated video, image, or audio asset therefore carries a visible or audible disclosure baked into the rendered pixels or audio itself, applied during assembly, and **an asset without it cannot be marked publish-ready** regardless of any platform-native label described below.

**C2PA is signed after the final encode and archived with the pack** — worth doing because some platforms read the manifest before stripping it, to power their own auto-labeling, but this is never the compliance mechanism and this architecture makes no claim that provenance metadata survives distribution end to end (C7 §2.4a). The per-asset **provenance record** (delivered route identity and version, generation timestamp, a snapshot of that route's commercial-use terms at generation time, the router transaction id — §8.13, §12.2) is what actually defends a rights or compliance challenge later, not the metadata embedded in the file.

**Per-platform label mechanics** (separate, cumulative contractual obligations, distinct from the EU-law duty above — C2 §2.3): TikTok exposes an AIGC boolean field on its Content Posting API's Direct Post endpoint (defaulting to false), alongside a UI toggle and automatic labeling from read C2PA metadata. YouTube's Data API v3 exposes a settable synthetic-content boolean property on video insert/update, alongside a Studio upload-flow question; 2026 rollout adds automatic detection with non-removable proactive labels for undisclosed content. Meta's organic path is a publish-time UI toggle with no confirmed organic API field as of the research date (an explicit open verification item, C2 D2) — its machine path is metadata-driven, which is one more reason C2PA is worth preserving even though it is not the compliance mechanism. LinkedIn has no confirmed structured toggle at all; the recommended interim practice is a short per-post disclosure line composed directly into the copy for any substantially AI-generated visual asset, revisited if LinkedIn ships a dedicated control.

**Because the publishing bridge cannot carry any of these platform-native flags** (§7.7, W2-05), this mapping cannot be set programmatically through distribution prep in v1 — every one of the mechanics above is a manual action the operator takes in each platform's own interface, after a draft already exists. The **publish-gate label acknowledgement** (§7.7) is the control that keeps this from being silently skipped: every asset whose AI-content class requires disclosure carries an AI-label-required flag, and the publish gate will not treat that asset as ready until the operator has given a separately recorded acknowledgement — not folded into the general pack approval, because bundling it is exactly how a busy operator skips it. **And because the guaranteed floor path never calls the bridge at all, the same checklist is emitted at packaging into rung-3 staging** (§7.2), so the obligation travels with the artefact the operator pastes from rather than living behind a gate that path does not cross.

**A voluntary instrument worth tracking, because adopting it would change what the floor above looks like.** The AI Office's **Code of Practice on Transparency of AI-Generated Content** is voluntary, but signing it founds a **presumption of conformity**, and the work under it includes a **standardised EU "AI" label icon** and modality-specific marking guidance. Neither exists in final form at the time of writing and the status is explicitly time-sensitive (§0.3 row 18, recheck 2026-09-01). Two consequences are recorded rather than discovered later: if the icon is standardised, **adopting it replaces the theme-level disclosure wording** and the engine floor in §4.4 is re-expressed against the standard rather than against our own type-height and contrast numbers; and signing the code is a cheap posture improvement for a small operator whose exposure is entirely Article 50, so it belongs on the operator's decision list rather than in a footnote.

### 14.7 Prompt and model version pinning per pack

Every artifact in every pack carries, as metadata, which prompt-pattern version and rubric version drafted and judged it, and which model/version string ran each of the two roles — **drafting and judge** (C5 §5). *(The "polish" role named in earlier drafts owns no stage in this pipeline and is deleted; the voice gate is judge-plus-regenerate, and the regenerate call reuses the drafting role — §1.5.)* This is what makes "did the last prompt or model change actually help" answerable months later, and it is the precondition for the judge re-calibration cadence in §14.2 — a rubric or model change without a fresh calibration pass against the golden set is exactly how silent drift happens. It also feeds the provenance record's own versioning discipline (§14.6), so a pack's claim-safety and voice-safety state is as auditable after the fact as its media-generation state.

### 14.8 The frozen eval set and the pre-rollout regression gate

Version pinning answers *what produced this* after the fact. It does not stop a prompt or model change from making the system worse, and §12.4's weekly loop is an edit path straight into the most safety-relevant prompts in the system. Three artefacts close that, all specified in the source research and all previously absent:

**The frozen eval set** is a fixed collection of inputs with known-good and known-bad expectations per language, **never used for prompt-tuning inspiration — only for measuring**. That restriction is the whole point: an eval set that authors have read while writing prompts measures nothing, because the prompts have been fitted to it. It is built alongside the golden sets in Phase 0 (English and Czech) and grows only by deliberate, logged addition.

**The pre-rollout comparison is a precondition, not a follow-up.** Any candidate change to a prompt pattern, a rubric or a model selection is run against the frozen eval set **before** it is applied, and compared with the last known-good version on three measures: **pass rate**, **human-agreement rate** and **token cost**. A change that improves pass rate while degrading agreement is a change that made the judge more agreeable, not the writing better — which is exactly the failure a single blended number hides. Phase 7's re-calibration after a change stays, but it detects drift that has *already shipped into packs*; this gate is what stops it shipping.

**A blind A/B on golden topics, for ambiguous results**, plus a **standing human spot-check on a small percentage of live packs**. Both exist for the same reason and it is worth stating plainly: without a human in the measurement loop, the judge grades a change to its own grading rubric, which is circular. The A/B and the spot-check percentage are named, deferred-value knobs — the mechanism is designed now, the numbers are set when there is enough traffic for them to mean anything.

---

## §15. Risks, failure modes and mitigations

### 15.1 How to read this section

Every row states four things: **what fails**, **how we find out** (detection is a design obligation, not a hope), **what the architecture does about it** — with the section that owns the mitigation — and **what the operator actually sees**, because a mitigation nobody notices is not a mitigation. The last column is the one to read if you are the operator; the third is the one to read if you are reviewing whether this plan is honest.

Three principles run through the whole table and are not repeated per row. **Degraded is a designed state, not a break** — every source, every provider and every publishing path has a named rung below "working" that still produces a useful, honestly-labelled pack. **Silence is the enemy** — a failure that produces a complete-looking pack with a missing axis is worse than a failure that stops the run, so every degrade is named in the digest and every repeated degrade escalates rather than repeating (§8.12). **Money is guarded before it moves** — every cap is checked pre-submission, because a check after submission is a report, not a control (§4.6, §8.11).

### 15.2 The risk table

| # | Failure | Detection | Mitigation (owner §) | Operator-visible symptom |
|---|---|---|---|---|
| **R-01** | **Collector breakage** — a free API changes shape, deprecates an endpoint, or a feed starts returning nothing | Per-source circuit breaker trips on consecutive failures; the request log shows status and ladder rung; a source producing zero signals for a full cadence period is itself an alarm | Per-source fallback ladder: primary → degraded → operator-supplied → skip-with-log, no rung ever descending into scraping; collection continues for every other source; ranking always runs on what was gathered (§2.2, §2.5, §8.10) | Digest carries a degraded-source banner naming the source and the expected coverage effect; run exits **partial-success — degraded sources** |
| **R-02** | **A source closes permanently** — terms change, a login wall appears, or anti-bot defence makes an open surface unreachable | The same detection path as R-01, plus the method-evaluation gate on any attempted re-entry | The do-not-scrape list is binding in every mode including degraded ones; the source is dropped with a logged reason and its axis loss is named; the portfolio is deliberately wide enough that no single source is load-bearing (§2.3, §2.5) | A permanent banner rather than an intermittent one, and a §16-style decision for the operator: replace, buy, or accept the axis loss |
| **R-03** | **Licensed-vendor churn** — a trend or demand vendor is acquired, dies, or changes tiering; this is evidenced twice, not hypothetical (W2-16) | Vendor roster carries last-verified and **recheck-by** dates; a lapsed recheck drops the source to degraded automatically | Every licensed source has a named same-category fallback vendor and, behind that, a *designed* degraded state — for the short-form axis, a monthly human browse ritual (§2.2, §2.3) | The axis is labelled degraded in the pack; credit spend on that vendor stops rather than continuing into a dead endpoint |
| **R-04** | **Trend vendor bought but programmatically inaccessible** — the vendor's own guide and pricing page contradict each other on whether full access is included at the purchased tier (W2-17) | The one-week trial exists to answer exactly this question, before money is committed | Adoption is trial-gated; a same-category fallback is named; the designed degraded state is a monthly manual ritual (§2.3, §17 Phase 0) | If the trial fails, the short-form trend axis is simply absent and the packs say so — no silent gap |
| **R-05** | **Ad-library token expiry silently breaks scheduled runs** — 60-day tokens plus a personal identity-verification prerequisite gate the whole source (W2-15) | Token-expiry alarm fires *before* expiry, with fail-closed behaviour on the source | Renewal is a named runbook item; identity verification is week-1 onboarding, not a technical detail; the ad-creative axis is absent until the credential is issued, making the token-expiry alarm load-bearing for continuity (§2.3, §17 Phase 0) | A dated "this credential expires in N days" line in the digest, then a degraded-source banner if it lapses |
| **R-06** | **Curated-inbox ritual lapse** — superseded by `RISK_LOG.md` W2-01a; the ICP-pain axis no longer depends on a weekly operator ritual since curated-inbox inputs were reclassified as configuration (W7-1) | **This risk is retired.** The human-asserted evidence class in ranking is now sourced from configuration decisions made at theme setup, not from per-run operator inputs. Configuration-time decisions are auditable and datable in `DECISION_LOG.md` rather than silently lapsed. | — | — |
| **R-07** | **Media provider outage** — the router is down, or a route is unavailable or degraded in the registry | Submission failures and poll timeouts, distinguished from policy refusals which are never retried | In-run alternate registered route within the same tier and rights class → degrade to plan-only for the affected slots → migrate to the registered fallback router if sustained; **no rung silently produces a worse asset** (§5.7, §8.10) | Affected asset slots arrive as complete plan-only artifacts with the reason attached; run exits **completed-with-pending-media** or **partial-success** |
| **R-08** | **Silent model substitution** — the router's video route can switch to a backup model on some content-review triggers; the substitute cannot use the high-resolution endpoint and is forced to a different aspect ratio (W2-03) | Requested-versus-delivered route, aspect and resolution are recorded on every artifact and compared | Mismatch surfaces in the pack before it can fail the platform gate at publish time; the per-asset provenance record is resolved **after** completion, because a different model carries a different rights class (§5.6, §8.13, §14.6) | A visible "delivered ≠ requested" note on the asset, with the substituted route named |
| **R-09** | **Provider ephemerality and disputed billing** — media deleted at 14 days, result URLs expiring sooner, no idempotency, and a "failed tasks aren't charged" claim contradicted by community reports (W2-02) | Balance-delta reconciliation compares expected cost from the registry price snapshot against observed balance movement; checksum verification on every re-hosted artifact | Write-ahead spend ledger committed before submission; resolve-by-query on restart, never blind resubmission; a named **submitted-unknown** state with no auto-resubmit; expiry-ordered download queue drained before any new submission; **unexplained-spend circuit breaker halts new submissions** (§5.5, §5.6, §8.5, §8.13) | A spend line in the digest showing expected versus observed, and a hard stop with an explicit message if they diverge beyond tolerance |
| **R-10** | **Regenerate-loop cost blowup** — a systematically bad prompt or an over-strict judge burns budget on regeneration in an unattended run (W2-10) | Four named counters are logged separately — the claim-retry budget, the voice-regenerate cap, the QA-rejection cap and the combined per-artifact repair ceiling — plus the rolling flag rate as a judge-health signal | **Pack-level bounds are what limit a run; per-artifact caps limit an artifact.** Both now exist on both sides: the claim-retry allowance and the **per-pack voice-regenerate allowance** bound the run (a per-artifact cap across ~60 assets is a multiplier, not a ceiling); the combined **per-artifact repair ceiling** bounds the interaction between gates including claim-2 repair re-entry; exhaustion degrades the pack to review-required rather than failing the run (§14.0, §14.2, §14.3, §6.7) | Assets arrive labelled "did not pass voice/spin gate" with full attempt history, rather than the run silently costing more |
| **R-11** | **Doubled-language spend** — two first-class languages mean two of everything, against a small trial budget (OP-1, accepted at W2.5-4) | The cost forecast decomposes per topic and per language before spend, computed from registry price snapshots with the snapshot date shown | Keyframe-first so one composition serves both text variants; language-neutral footage with language-specific overlays and voice added at assembly; the Czech carousel-to-reel recipe buys no clips at all — **which is exactly why the "Czech is cheaper" conclusion is conditional and stops being true if Czech is promoted to generative clips** (§3.1, §4.3, §5.4) | A per-language cost breakdown in the digest, and a visible warning when a language is promoted to a more expensive recipe |
| **R-12** | **Trial-quota exhaustion** — one mis-configured run or an unbounded retry loop consumes a large share of a small credit balance (W2-14) | Pre-submission cap enforcement at four levels: per asset, per run, per day, per month | Hero tier never auto-selected in any mode; a documented trial envelope with a reserve; a separate router key for scheduled runs with a bounded top-up, so a runaway loop is limited by the wallet and not only by our code (§4.6, §5.4, §8.11) | Run exits **budget-stop** (pre-emptive, nothing spent) or **partial-success — budget-capped mid-pack** with the ungenerated destinations explicitly named |
| **R-13** | **Cron partial run** — a crash after paid media generation, or a stage hanging until the run ceiling | Run ledger checkpoint state per unit of work; media-job ledger state machine; graceful wind-down as the ceiling approaches | Checkpointing is **per unit of work** — one asset slot × language × attempt, which is one ledger row and one paid attempt chain; on resume the pipeline acts only on the incomplete remainder; wind-down stops new paid work, checkpoints what is in flight and packages what is complete (§8.7, §8.13) | The next run adopts pending jobs and drains the download queue first; nothing already paid for is lost or re-bought |
| **R-14** | **Scheduler traps that only appear unattended** — running as a system account, per-user credential stores, console code pages, minimal environments, daylight-saving double-fires (W2-20) | These fail at 03:00 with no console; the file log is the only observability, so it is designed as such | Scheduled tasks run under the operator's own account, never a system account; UTF-8 forced at every entry point; absolute paths from config; UTC-internal timestamps with a pinned run-date derived once from a configured theme timezone; explicit exit-code propagation from the launcher; skip-on-overlap via an OS-mediated lock (§1.4, §8.1, §8.3) | A run that either happened or did not, provably, from the filesystem status flag — never an ambiguous half-state |
| **R-15** | **Brand-truth unreachable** — the knowledge base is down, the reader path fails, or the integration token has been revoked | Brand-truth resolution runs first, before anything is spent, precisely so this is discovered early; **a cheap read-only health call at run start tests the credential specifically**, and failures are classified into transient / permanent-auth / permanent-endpoint so only the transient class is retried (§6.2) | Fall back to the last-good offline snapshot, which **caps the confidence band at MINIMAL always** — and since MINIMAL is below PARTIAL, **an unattended run resolving from a snapshot degrades to research-only immediately, whatever the snapshot's age**. The maximum-offline-window knob applies to interactive runs only; there is no unattended snapshot path (§6.5, §6.6, §11.3). A failed integrity check, or a snapshot that has never been written, is INSUFFICIENT | Research and ranking complete and are saved; one plain sentence at the top of the digest names the actual cause verbatim — including the rejected-credential case and its fix — and the run exits **completed-degraded** |
| **R-16** | **Plan-versus-fact contamination** — roadmap, draft and aspiration pages sit beside fact pages, are fresh and well written, and confidence scoring cannot catch them; the highest-probability false "we do X" claim in this deployment (W2-11) | Not detectable statistically — this is why the control is structural | Resolution reads **only from designated fact locations**, and any offer whose status is not explicitly live is unspinnable, enforced by property filtering the interactive reader path cannot do; a workspace that cannot separate plan from fact is an escalation to the operator (§6.2, §6.3) | If the separation is absent, readiness validation fails and says which locations are ambiguous |
| **R-17** | **Claim ledger unreadable, or hard excludes unresolved** — distinct from being legitimately empty | The resolver distinguishes resolved-with-values, resolved-empty and unresolved as three states, never two | Both conditions **bypass scoring entirely** and force research-only, because they are about not knowing the rules rather than having thin data; hard excludes are duplicated in configuration precisely so they survive a knowledge-base outage, with the union always winning (§6.3, §6.5, §11.3) | The run stops producing brand content and says which of the two fired; not overridable even interactively |
| **R-18** | **EU AI Act Article 50 exposure** — binding since 2026-08-02, no size exemption, fines up to €15M or 3% of turnover, and metadata-only compliance provably fails because platforms strip provenance manifests on re-encode (W2-04) | An asset without the burned-in disclosure cannot reach publish-ready state; this is a precondition check, not an audit | Burned-in, human-perceivable disclosure applied at render time is the **load-bearing** control; the provenance manifest is signed after final encode and archived, never relied on; platform-native labels are a separate cumulative obligation (§4.4, §14.6) | Any asset missing the overlay is blocked at the publish gate with a named reason, not merely flagged |
| **R-19** | **The publishing bridge cannot carry the label** — no per-platform AI-disclosure fields exist, so labelling is a manual human action a busy operator will skip (W2-05) | The publish gate refuses to treat an asset as ready without a **separately recorded** acknowledgement, deliberately not folded into the general approve decision | Per-asset AI-label-required flag; a named checklist item in the pack; re-test whether the field has appeared at trial time (§7.7, §14.6) | An explicit extra confirmation step per affected asset — friction that exists on purpose |
| **R-20** | **The publishing bridge behaves differently from its documentation** — no account exists yet, so every capability claim is a paper claim (OP-2) | The implementation acceptance criteria in §7.8 are run against a real account before rung 1 is trusted | A three-rung fallback ladder designed as first-class: unscheduled draft → far-future scheduled post → local-only staging for manual paste, the last of which never depends on the bridge being up at all (§7.2) | If rung 1 fails, the operator pastes per platform — high friction, but the pack is still complete and usable |
| **R-21** | **Judge false-positive loop** — an over-strict judge floods the review queue, trains the operator to ignore flags, and turns the gate into theatre (W2-10) | Human-versus-judge agreement tracked **by direction**, not as one blended accuracy number; a rolling flag-rate ceiling per theme, destination and language | The two directions carry different business costs and are tuned separately; a flag rate meaningfully above what golden-set calibration predicted is treated as a warning about the judge, not a queue to wave through; start lenient on a new language and tighten on real agreement data (§14.2, §17 Phase 7) | A monthly calibration report the operator reads and applies; thresholds never move automatically |
| **R-22** | **A configured language suppressed by arithmetic** — no Czech-signal carrier exposes per-item engagement, so a multiplicative composite drives every Czech candidate toward zero and the language dies quietly while every policy document still calls it first-class (W2-07) | Theme-readiness validation asserts a non-empty candidate set **per language** | The Czech composite omits the virality factor rather than proxying it; "under-evidenced ≠ poor fit" becomes the normal Czech path; every Czech candidate carries the honest label that its discourse evidence was observed in English (§2.7, §13.2) | An empty Czech section is a validation failure with a named cause, not a silently short digest |
| **R-23** | **Czech short-form reputational risk under the identical-mix rule** — entertainment-styled short-form reads as cheap to Czech B2B decision-makers, and the operator chose to publish there anyway (W2-08, **mitigation replaced**) | **Leading indicator:** the Czech short-form rejection rate and its reason-code frequency distribution, compared with English over the same window — machine-held, available weekly from Phase 4. **Lagging indicator:** the operator's recorded read of engagement quality, entering through the optional outcome-capture path. **Trigger:** a configured counter — twenty published Czech short-form assets or twelve weeks, whichever first — raising a named Czech short-form review line in the digest | **The original mitigation ("TikTok excluded for cs in v1") is void.** The replacement is the six design commitments in §3.1, **all six now instrumented**: recipe not translation (a recipe knob), framing not mimicry (**rubric dimension 1**, §14.4), register discipline (rubric dimension 7), understatement (rubric dimension 11's weighting), a destination-aware production floor (a hard gate with Phase-4 acceptance), and a revisit trigger that is **a configured threshold rather than an intention** (§3.1, §4.5, §12.1, §12.2) | Czech short-form assets carry a visible recipe label and their own production-floor checklist; when the trigger fires, a review line appears in the digest with both indicators attached, so the review happens because a counter fired rather than because someone remembered |
| **R-24** | **GDPR exposure on research artifacts** — public social content is personal data regardless of pseudonymity, and monolithic raw dumps cannot honour an objection (W2-06) | Not detectable at runtime; this is a design property that either exists from day one or is a painful retrofit | Extract-first storage; bounded retention with an actual expiry job; author handles minimised or hashed; **targeted deletion by canonical key from day one**; the legitimate-interest assessment and published privacy notice named as prerequisite company artefacts the software cannot generate (§2.6, §17 Phase 0) | A retention and deletion capability the operator can actually exercise, rather than a policy sentence |
| **R-25** | **Prompt injection through collected content** — a crafted post title redirects a downstream model call, and the failure looks like a bad topic choice (W2-19) | Injection-style phrasing is itself a veto signal at the fit gate, so an attempt is visible rather than silent | All collected text is carried as quoted data with provenance tags and never as instructions; the instruction layer stays structurally separate and privileged (§2.7, §2.8) | The candidate is vetoed with a specific reason, visible on its scorecard |
| **R-26** | **Vendor-blog statistics hardening into thresholds** — several headline numbers come from marketing blogs and would then be defended as evidence-based (W2-09) | The consolidated fact ledger grades confidence and flags the offending rows explicitly | Standing rule: **no threshold may be set from a Low- or Medium-confidence marketing-blog statistic**; thresholds come from measured run data; the brand-fit floor and the freshness half-lives are labelled directional starting points (§0.3, §2.7) | Threshold changes require a logged human rationale, and the ranking-config version makes them visible |
| **R-27** | **The router's own terms are unread** — every legal path was blocked to retrieval and no archive snapshot exists (W2-12) | A named prerequisite, not a runtime check | Working posture: the router grants nothing, based on two structurally identical retrievable router products; the real control is the **per-asset upstream licence snapshot**; a manual browser pull of the terms is a build-sign-off prerequisite (§5.6, §17 Phase 0) | Nothing at runtime — this one is a gate on starting the build, and it belongs on the operator's checklist |
| **R-28** | **Derived-analytics vendors collect upstream by undisclosed means** — no platform licence programme exists for this data, so the compliance posture is inherited by assumption (W2-18) | Not a runtime condition; a legal reading question | Working assumption recorded rather than left implicit: derived analytics is treated as the permitted class and raw scraped passthrough is explicitly excluded; carried as an open decision needing one paragraph of legal reading (§2.4, §16 OD-17) | Nothing at runtime; the operator sees it as an open decision with a recommendation |
| **R-29** | **Review affordances the runtime does not fund** — a design assuming live buttons and a browser workflow would require a web application nobody decided to build (W2-13) | Caught at design time; recorded here so it cannot creep back in | The digest is a **static document in the run folder**; approval is a decision file or a console command referencing the run id; the decision *content* is adopted in full, the interaction *mechanism* is replaced (§12.1, §12.5) | A file the operator opens and a file the operator edits — nothing to install, nothing to keep running |
| **R-30** | **Model churn rots a pinned route** — one widely-used video model's API is scheduled for removal, which is the standing proof (W2-16, F-3) | Model registry carries last-verified and recheck-by dates per route; prices are rechecked monthly | A lapsed recheck-by **drops a route to degraded and the router stops selecting it for spend**; refusal statistics accumulate in-house because no provider publishes them; the excluded model is recorded as excluded rather than quietly absent (§5.2) | Cost forecasts show their price-snapshot date; a degraded route simply stops being chosen, and the pack says which route rendered what |
| **R-31** | **Infrastructure hard failure** — disk full mid-ledger-write, or an unreadable secret at load time | Proactive low-disk check at run start and again before the media stage; secrets verified at theme load | Disk full is a hard-failure class rather than a per-unit soft failure, because it risks corrupting an in-progress ledger write; a missing required secret is a hard stop with no silent "skip that provider and continue" (§8.10, §11.3) | Run exits **hard-failure** or **policy-stop** with the specific missing item named |
| **R-32** | **Notification delivery failure** — the mail relay is down and the operator concludes the run failed | Notification delivery is logged and reflected in the run ledger separately from the run's own outcome | A delivery failure **never changes the run's exit class**; the filesystem status flag is the mandatory always-written baseline and is the ground truth for "did today's run happen" (§8.12) | The flag file is correct even when the email never arrives |
| **R-33** | **Allowlisted-but-unconnected destination** — the operator listed a destination but never completed its connection | The publish gate checks allowlist membership *and* actual connection state before any call | Fail closed for that destination alone; the pack names exactly which destination is blocked and why, and offers the honest choices; **no silent skip and no silent substitution** (§7.4) | One named blocked destination, with the rest of the pack unaffected |
| **R-34** | **Exemplar-corpus fact leakage** — the corpus is dense with other people's commercial claims and is shown to the generator at the exact moment it writes | A dedicated corpus-leakage check class compares generated numbers, metric phrases and entities against corpus content and records a **leakage event** | The corpus feeds style retrieval only and is excluded from every factual retrieval path; the claim ledger is never populated from it; a rising leakage rate is itself the signal that the few-shot design is bleeding facts (§6.11, §6.7) | Blocked assets with a named leakage reason, and a leakage-rate line the operator can watch over time |
| **R-35** | **A theme that is wrong rather than broken** — the wrong CTA class on the wrong domain, a resolvable-but-mistaken pain-to-offer relation, a language with a technically non-empty candidate set, a cadence pair that re-ranks a stale window nightly. The risk log ranks this as **more likely than any provider or source failure**, because a misconfiguration produces confident, complete-looking output (W3-01) | **Partial, and the honest limit is stated rather than hidden.** Readiness validation checks *structural* completeness and catches the absent, the unresolvable and the internally inconsistent (§13.2) — it does **not** check semantic correctness, and a wrong-but-resolvable CTA class or pain-to-offer relation passes every assertion it makes. What does exist as detection: the **per-language evidence-and-volume floor** across runs (§2.7); the **wrong-brand-CTA check** (§6.9) for the routing half; the **spin rationale printed per asset** in the digest (§12.1), which is the mechanism by which a human notices a wrong mapping in seconds; and reason-coded rejection frequency, which turns a systematic mis-mapping into a visible pattern within a week or two. **There is no machine detection for "this relation is coherent but mistaken", and there is not going to be one** — the first pack is the test | Everything that can spend, publish or relax a threshold **defaults safe**, so a copied theme is safe before it is useful; both cadence knobs default off; mode defaults to test with an empty allowlist; dry-run defaults on in test **at engine level**; readiness is a gate on *scheduling*, not advice — a failing theme may be run interactively and may never be scheduled. The **eleven-decision minimum viable knob set** (§10.1) is the operator-overwhelm half of the mitigation, and it is why the ≈130-knob surface is not the number a new theme author faces (§10.1, §10.6, §13.2) | The first interactive test-mode pack, read with the spin rationale column open. Then, in ongoing operation: an evidence-floor line for a starved language, a rejection-reason distribution that clusters on one mapping, and a readiness failure naming the specific assertion — but never a runtime alarm saying "this theme is wrong", because nothing can say that |
| **R-36** | **Text-model spend is the second wallet and was previously uncapped** — roughly 130 text artifacts per run, each passing five model-mediated evaluations on top of drafting, at 0.7–2.25M tokens per run and 9–27M per month at the recommended cadence: the same order of magnitude as the media forecast | Pre-call enforcement at three levels, all logged: per-run/day/month text budgets, per-stage call ceilings, and the per-pack judge allowance; the spend ledger records text calls beside media ones so balance reconciliation covers the whole run | The **LLM budget block** (§5.4a), consumed by the same cost gate at the same pre-call boundary as media, with the mid-pack cap-hit outcome class reused on exhaustion; per-node per-call token ceilings underneath; the node inventory (§1.5) fixing what each node may consume | A **two-line cost forecast** — media and text, never blended, each with its snapshot date — and, on exhaustion, a run exiting **partial-success — budget-capped mid-pack** naming what was not generated and why |
| **R-37** | **A gate that cannot execute silently does not block** — a degraded judge endpoint, an unparseable structured output, or a ceiling reached mid-pass produces assets that were never semantically gated, sitting in the pack beside properly gated ones | Every gate reports its own execution state, not only its verdict; the pack records which gates ran per asset | **The fifth fail-closed trigger** (§11.3): any gate that cannot run fails its artifact closed to that gate's own named degraded outcome, with the gate named — voice judge unavailable → labelled, never passed; claim semantic pass unavailable → deterministic verdicts only and all claim-shaped candidates blocked; keyframe rubric unavailable → no clip spend | Assets labelled with the gate that could not run, in the same shape as a cap exhaustion — so "not checked" is visibly different from "checked and passed" |
| **R-38** | **Personality rights and voice cloning** — the generative surface can produce a synthetic human presenter or a cloned voice, and no consent regime exists to authorise either | Not a runtime detection question: the value is refused at route selection and at keyframe acceptance, so a violation cannot be generated | **A v1 ban rather than a gate** (§5.3): the *talking human* motion class is disabled, no reference input depicting an identifiable person may be supplied, and only licensed-catalogue voice routes may be selected — `cloned-real-person` is a forbidden rights class. The person-basis flag and the scope-limited consent record are designed but **out of scope until avatars are**, at which point they are prerequisites rather than follow-ups | Nothing at runtime, which is the point. At configuration time, a theme that requests a talking-human motion class or a cloned voice fails readiness with the ban named |
| **R-39** | **Verbatim excerpts retained permanently in packs** — a 30-day window on collected text, silently nullified by a provenance snapshot and per-signal source links kept forever in the run pack, with no path for targeted deletion to reach an archived pack (W2-06, extends R-24) | Not a runtime condition; a design property that exists from day one or is a painful retrofit. The expiry job's coverage is testable, and Phase 1 tests it against an already-packaged pack | Provenance snapshots and per-signal source records are **split into a permanent de-identified part and a 30-day verbatim part** with an in-pack placeholder on expiry; a **run-pack → canonical-key index** lets targeted deletion reach inside archived packs; author handles use a keyed deterministic hash with the key held separately; author handles and permalinks are redacted from prompt payloads (§2.6, §2.6a, §8.6, §12.2) | An erasure or objection request that is actually executable across every pack ever written, demonstrated on a real archived pack rather than asserted |
| **R-40** | **Two designed safety mechanisms colliding** — the point-in-time low-disk hard-failure and the expiry-ordered drain-first rule, which together can abort a run mid-drain and strand already-paid-for media against a 14-day deletion clock: exactly the outcome the whole checkpoint design exists to prevent | The low-disk check becomes a **running guard evaluated before each individual download**, plus a pre-drain estimate of the whole backlog's volume | On a mid-drain low-disk event the drain **narrows rather than aborts**: new submissions stop first, the drain continues in strict expiry order while space allows, ledger and pack headroom is reserved ahead of media writes, and a genuine stop names the undownloaded jobs and their deletion deadlines (§8.10, §8.13) | A named list of at-risk jobs with dates, rather than a hard-failure exit code and a silent loss discovered a fortnight later |
| **R-41** | **A pending master with no owner** — *completed-with-pending-media* was a headline healthy outcome with nothing designed to finish the asset: assembly had no ledger state, packaging's idempotency key broke on completion, and the adopting run's mode and budget context were undefined | The **assembly ledger**'s blocked-on-inputs state is queryable, and a pending master is packaged visibly incomplete with a days-to-deletion countdown rather than as a finished master | Assembly is a **resumable unit of work** whose row unblocks when its last input reaches `done`; assembly is not spend-bearing, so any run may complete one; **pack amendment** is explicit, revision-numbered, and recorded in the review-decision store against the originating run id, so review decisions are never split across two folders (§4.7a, §8.6) | A pack that says "waiting on one clip, deletes in N days", then an amendment line naming which earlier pack this run completed — never a silently changed folder |
| **R-42** | **Review-capacity insolvency** — the operator's real review throughput cannot keep pace with pack volume at the configured cadence, and the response under load is not to review faster but to approve unread, silently converting a quality gate and a legal evidence base into a rubber stamp | The **decisions-per-minute rate** computed from the review-decision store's own timestamps between successive decisions in a session, compared against §3.5's review-burden table; and the **ratio of `approved-unread` to considered decisions** (§11.4), tracked per theme and trending over time | **Keyframe-first approval** narrows the review unit for the largest single time cost (§4.2b). **Reduced default topic count and destination breadth** narrow total volume (§3.2, §10.2). **The `approved-unread` class** (§11.4, §12.1) makes drift visible instead of absorbing it. **§3.5's table** gives the operator a number to check reality against rather than an aspirational one | A rising `approved-unread` share is visible in the digest and the review-decision store; the sharper consequence is that **R-35's only named detection mechanism — "the first pack, read with the spin rationale column open" — silently stops running**, because the column stopped being read. Nothing pages anyone; the decisions-per-minute trend is what would show it, if watched |

### 15.3 Coverage map — every logged risk lands somewhere

Every row in `RISK_LOG.md` maps to a §15 row above or to an inline mitigation in the body of this plan. Nothing is dropped, and nothing is mitigated only by intention.

*This table previously listed 39 of the risk log's 43 rows while claiming completeness — omitting W2-08a, W3-01, W3-02 and W3-03, all appended in the same wave by the same author, and leaving W3-01 (the row the log itself ranks highest by likelihood) with no §15 risk row at all. A coverage map's entire value is exhaustiveness, and one that is 91% complete while claiming 100% is worse than none, because it retires the question. The four rows are added below, W3-01 now has R-35, and the Wave-4 additions are listed with them.*

| Logged risk | Where it lands |
|---|---|
| F-1 Reddit terms and access reality | §2.3, §2.5 (now official Data API with DataForSEO fallback, W6-1) · R-02 |
| F-2 X read path ≠ publish path | §3.2, §7.5 (two independent decisions, never conflated) |
| F-3 Model churn is structural | R-30 · §5.2 (model registry with recheck-by) |
| F-4 One publish enforcement point | R-33 · §7.4, §11.2 (five defence layers around one gate) |
| F-5 Spoken fake claims are a new safety surface | §4.8, §6.8, §14.5 (script-lock primary, recognition as monitor) |
| F-6 Higgsfield classification | §5.1 (out of the pipeline for v1, W2.5-6) |
| F-7 Czech is not a translation pass | R-22, R-23 · §3.1, §3.4, §4.4, §6.12 |
| F-8 AI Act plus platform labels plus provenance loss | R-18, R-19 · §4.4, §14.6 |
| F-9 Scraping pessimism | R-02 · §2.4, §2.5 (do-not-scrape list binding in every mode) |
| RA-1 Cron idempotency and dedupe | R-13 · §8.3, §8.5 |
| RA-2 Brand-fit scoring inspectable | §2.7 (scorecards, hard floor, veto list) |
| RA-3 Anti-slop gate with bounded regenerate | R-10, R-21 · §14.2 |
| RA-4 Source-access honesty | §2.3 (portfolio re-ranked by access reality) |
| RA-5 Brand-truth conflicts | R-15, R-16, R-17 · §6.4, §6.5 |
| RA-6 Budget caps and dry-run boundary | R-12 · §4.6, §5.4, §8.11 |
| RA-7 Per-language output integrity | R-22, R-23 · §3.1, §13.2 |
| RA-8 Mode enforcement choke point | §11.2 (one resolver, two specialised gates) |
| OP-1 Doubled media spend | R-11 |
| OP-2 Publishing bridge unverified | R-20 · §7.2, §7.8 |
| W2-01 Curated-inbox ritual dependency | R-06 |
| W2-02 Router ephemerality, no idempotency, disputed billing | R-09 |
| W2-03 Silent model substitution | R-08 |
| W2-04 EU AI Act exposure | R-18 |
| W2-05 Publishing bridge cannot carry the label | R-19 |
| W2-06 GDPR on research artifacts | R-24 |
| W2-07 Czech suppressed by arithmetic | R-22 |
| W2-08 Czech asset-mix reputational risk | R-23 — **mitigation replaced; see §15.4** |
| W2-09 Vendor-blog statistics in thresholds | R-26 |
| W2-10 Judge over-strictness cost spiral | R-10 and R-21 (cost and queue directions tracked separately) |
| W2-11 Plan-versus-fact contamination | R-16 |
| W2-12 Router terms unread | R-27 |
| W2-13 Review UX assumes unfunded affordances | R-29 |
| W2-14 Trial-budget exhaustion | R-12 |
| W2-15 Ad-library token expiry | R-05 |
| W2-16 Model and vendor churn | R-03 and R-30 |
| W2-17 Trend-vendor tier contradiction | R-04 |
| W2-18 Derived-analytics upstream undisclosed | R-28 |
| W2-19 Prompt injection through collected content | R-25 · and node N-13's quoted-data posture for fetched site text (§6.6) |
| W2-20 Cross-platform scheduler traps | R-14 |
| **W2-08a Czech asset-mix risk under the identical-mix rule (superseding mitigation)** | **R-23 — all six commitments now instrumented; §15.4 corrected** |
| **W3-01 Theme-configuration surface breadth** | **R-35** — a genuine risk row with an honest detection column · §10.1 (≈130 knobs, corrected from "roughly ninety"; eleven-decision minimum set), §10.6, §13.2 |
| **W3-02 Per-run caps unresolved at build start** | **R-12** · §16 OD-8, §17 Phase 4 (acceptance criterion re-based so it discriminates — §15.4) |
| **W3-03 Assets produced for a destination never published to** | §3.2, §7.5, §16 OD-21 — carried as an open decision with both options costed; no §15 row is warranted because the consequence is review-time friction, not a failure mode |
| **W3-01a Theme-configuration surface, correctly sized (supersedes W3-01's sizing)** | **R-35** · §10.1 (≈130 knobs; eleven-decision minimum set), §10.4a machine/runtime block, §10.5 |
| **W4-01 Text wallet unbounded while asserted capped** | **R-36** · §1.5 node inventory, §5.1, §5.4a |
| **W4-02 Personality rights had no regime** | **R-38** · §5.3 v1 ban, §16 OD-27 |
| **W4-03 Article 50 control configurable, default omitted audio** | **R-18** *(extended)* · §3.3 engine derivation, §4.4 disclosure floor, §17 Phase 3 |
| **W4-04 Publish gate structurally bypassed on rung 3** | **R-19** *(extended)* · §7.2, §7.4, §17 Phase 6 |
| **W4-05 Provenance precondition rested on an unobservable field** | **R-08** *(extended)*, **R-36** · §5.6, §7.4, §17 Phase 0 |
| **W4-06 Verbatim retention inside packs nullified the 30-day window** | **R-39** · §2.6, §2.6a, §8.6, §17 Phase 1 |
| **W4-07 Disk-full versus expiry-drain collision** | **R-40** · §8.10, §8.13 |
| **W4-08 Pending master with no owner** | **R-41** · §4.7a, §8.6 |
| **W4-09 Gate unavailability defaulted open** | **R-37** · §11.3 fifth trigger, §14.2 |
| **W4-10 The one gate with no ending (QA/human-rejection loop)** | **R-10** *(extended)* · §4.9 QA-rejection cap, §14.0 |
| **W4-11 Cross-day resurgence rule existed only in the evidence base** | **R-35**'s detection half and §2.8a as the owning mechanism · §12.1, §17 Phase 1 |
| **W4-12 Silent per-language thinness** | **R-22** *(extended)* · §2.7 evidence-and-volume band, §12.1 |

### 15.4 The one amendment this plan makes to the risk log

**W2-08's recorded mitigation is void and is replaced.** The risk log's mitigation for Czech asset-mix reputational risk reads "cs recipe = carousel-to-reel, education-first, LinkedIn and long-form destinations; **TikTok excluded for cs in v1**". W2.5-4 overruled that: Czech gets TikTok, Instagram Reels and YouTube Shorts. The risk itself is unchanged and, if anything, is now larger.

**The replacement mitigation is the six design commitments, which are stated in full once, at §3.1, and are not restated here** (D-33's single-owner rule — this section previously carried a second, differently-worded copy, and the two had already drifted: one said "vykání", the other "formal register", against D-26's named term and D-21's no-new-nouns rule). Read them at §3.1.

**What this section owns is the enforceability claim, and it is corrected.** The claim used to be that the first five commitments are enforceable in the pipeline and the sixth is a governance artefact. That was wrong in both directions. Commitment 2 — framing, not mimicry — had **no gate, no knob and no rubric dimension**: it was asserted twice and checked nowhere, making the count 4/6 rather than 5/6. And commitment 6 was described as a governance artefact when what it needed was a counter. Both are fixed, so the accurate statement is now:

**All six commitments are instrumented.** 1 is a recipe knob; **2 is dimension 1 of the Czech judge rubric — hook shape and framing, with the transplanted English hook rhythm as its named fail smell (§14.4)**; 3 is dimension 7 (vykání by default); 4 is dimension 11's weighting; 5 is the Czech production-floor checklist enforced as a hard gate with a Phase-4 acceptance criterion; and **6 is a configured trigger — twenty published Czech short-form assets or twelve weeks, whichever first — raising a named review line in the digest with a leading indicator (rejection-reason distribution versus English) and a lagging one (the operator's recorded engagement read)**. The governance element that remains is genuinely governance: the *decision* to keep, narrow or expand is the operator's. What is no longer optional is that the question gets asked.

This amendment is appended to `RISK_LOG.md` as a superseding row rather than by editing the original, so the history of the decision stays legible.

---

## §16. Open decisions needing human input

### 16.1 What is on this list and what is not

This section carries only decisions that are **still genuinely open**. Everything the operator settled at the Wave 2.5 checkpoint is closed and binding, and is not re-litigated here: X reads stay out of v1; Reddit is a weekly human ritual and never an API; trend-vendor spend is approved subject to a trial; both languages get identical asset mixes; the stack is Python; Higgsfield is out of the pipeline; the run cadence is a config knob defaulting to off; notifications are email. Several further defaults were adopted without a gate and stand unless vetoed at Stage 5 — the reader split for the brand-truth reader, the primary Czech voice provider, local assembly, thirty-day raw-artifact retention, the demand-data vendor, human-moved calibration, deferring the publishing-bridge trial, and keeping the blog path config-gated.

Each row below states the options honestly, gives a recommendation with its reason, and names **who decides and when** — because an open decision without a decision point is just an unresolved argument.

**Vendors are named here, whatever the rest of the plan does.** §5.1's discipline of naming *roles* rather than vendors is right for an architecture that must survive churn, and it is wrong for a decision table: an operator cannot choose between "the provider with production evidence in Czech" and "the cheaper mature tier" without knowing which two products those are. So every option in the table below **names the product on first use**, keeping the role name as the governing noun everywhere else, and §17 Phase 0 does the same for its prerequisites — those two sections being the ones a human must actually act on.

### 16.2 The open decisions

| ID | Decision needed | Options | Recommendation | Who decides, and when |
|---|---|---|---|---|
| **OD-8** | **Per-run caps.** W2.5-7 settled cadence as a config knob defaulting off; it did not settle how much a single run may produce and spend | (a) Around three topics per run and one to two media-bearing masters per language — revised down from five once §3.5's review-burden table showed the whole-pack digest-scan target was arithmetically incompatible with five topics at the plan's own per-asset rates; (b) fewer topics, more media; (c) more topics, plan-only media by default | **(a).** The binding constraint is human video review at 20–30 minutes per finished video, not topic availability. Note the resolution this plan makes: the cap counts **masters produced, not destination derivatives**, because one vertical master legitimately serves several destinations through re-composition (§3.2) | Operator, at Stage 5. Revisit after four weeks of real runs using measured review time, not the estimate |
| **OD-9** | **Where the claim ledger lives** | (a) Typed database in the knowledge base with a config pointer; (b) configuration only; (c) split | **(c) split, with the knowledge base primary** — it can express provenance, evidence pointer, validity window, per-language text and usage scope, is queryable by property filter, and is editable by a marketing-literate operator without touching config. **Hard excludes are the exception and live in both**, with the union always winning, because excludes are monotonic and must survive an outage. Carried in this plan as a recommendation, not a lock: if the operator prefers config-only, the monotonicity rule survives but the ability to edit claims without touching configuration is lost | Operator, at Stage 5. Cheap to change before Phase 2, expensive after |
| **OD-10** | **Assembly-engine distribution and licence build** — the assembly engine being **FFmpeg** | (a) Bundle an FFmpeg build with the higher-obligation codecs enabled (a GPL-class build); (b) bundle a lower-obligation LGPL-class build and use platform encoders; (c) require a managed install of a pinned FFmpeg version per operating system | **(c).** Invoking the binary as a separate process is low-risk; *distributing* binaries is what triggers source-hosting and notice obligations a solo operator does not need. Pin the same version on both platforms and bundle fonts, not codecs, to preserve rendering parity | Operator, **before Phase 0** — corrected from "before Phase 3", because Phase 0's own deliverables already consume it: the pinned assembly engine is installed and its Czech glyph coverage verified during Phase 0 |
| **OD-13** | **Primary Czech voice provider** | (a) **ElevenLabs** — production evidence in Czech, and the provider for which word-level timestamps are evidenced; (b) **Azure Neural TTS** — the cheaper mature tier, Czech voices evidenced, **word-level timestamp support in Czech unverified**; (c) decide by A/B during the trial | **(c) with (a) as the working default and (b) as the cost/fallback tier.** The per-asset cost of either is near-negligible against video generation, so this is a quality decision, not a budget one — and it should be made on real Czech scripts, not on vendor claims. **The trial must additionally answer one architectural question, not just a quality one: does the fallback tier return word-level timestamps in Czech?** If it does not, the caption path on that tier falls back to forced alignment, and Czech is not among the standard alignment toolchain's default languages — which makes sourcing and pinning a Czech alignment model a Phase-0 deliverable rather than a Phase-4 surprise (§4.4) | Operator, during the Phase 0/3 trial. Decision recorded with the sample scripts used and with the timestamp answer |
| **OD-15** | **Retention windows and personal-data handling for research artifacts** | (a) Adopt the researched defaults; (b) tighten further; (c) defer to counsel | **(a) now, flagged for counsel rather than blocking on counsel** — raw payloads thirty days, normalised records ninety, request log twelve months, provenance permanent with the pack, targeted deletion by canonical key from day one. Curated-inbox verbatim text retention is removed (W7-1); the per-run input class no longer exists. The legitimate-interest assessment and the published privacy notice are **company artefacts the software cannot generate**, and are Phase-0 prerequisites | Operator now; qualified counsel confirms in parallel. Blocking for Phase 1 only in the sense that Phase 0 must have produced the two company artefacts |
| **OD-16** | **Trend-intelligence vendor adoption** — the vendor being **Virlo.ai** at its Starter tier (~$49/mo), approved at W2.5-3 but trial-gated | (a) Adopt Virlo after a passing trial; (b) fall back to **Shortimize**, the named same-category vendor, at the same gate; (c) **accept an absent short-form trend axis** — the TikTok Creative Center monthly browse is no longer available as a per-run input (W7-1), so no degraded state exists (see `RISK_LOG.md` W7-01) | **(a), and the trial must answer three questions before any subscription renews**: is full programmatic MCP/API access genuinely included at the Starter tier (Virlo's own guide and pricing page conflict, and this single fact gates adoption); does a niche monitor in this subject area beat what the free portfolio already surfaces; and what are the unpublished rate limits. **Option (c) is materially worse than the original designed degraded state** because the trend axis simply goes absent rather than degrading to a manual fallback — the operator must accept either (a) spend, (b) a second-choice vendor, or no short-form-trend signal at all | Operator, at the end of the one-week trial in Phase 0. A failed trial moves to (b), then (c) — never to a silent gap |
| **OD-17a** | **Legality posture of derived-analytics vendors with an *undisclosed* upstream** — the short-form trend vendor (Virlo class), where no platform licence programme exists for TikTok/Instagram/YouTube trend data and the vendor does not describe how it collects | (a) Treat as the permitted class, same posture as established derived-analytics products; (b) treat as raw scraped passthrough and exclude; (c) obtain a legal reading | **(a) as the working assumption, with (c) as one paragraph of actual legal reading rather than a shrug.** Raw scraped passthrough remains an explicitly excluded class regardless of the answer. **Independently of the answer, the vendor's own terms are read for a pipeline/derivative-use permission before the first credit is spent** (§2.4, Phase 0) | Operator plus counsel, **before the first credit is spent — moved out of "before renewal", which fell after the trial had already ingested data and spent money** |
| **OD-17b** | **Legality posture of the demand-data vendor, whose upstream is *known*** — **DataForSEO** resells Google SERP and Trends data, Google's terms were retrieved directly and are dated, and Google is in active litigation with vendors of this class | (a) Adopt as an explicitly logged vendor-risk decision; (b) drop the automated demand axis and keep the manual Trends CSV export as the permanent state; (c) obtain a legal reading first | **(a), and it must be recorded as a decision rather than inherited as a default** — it was previously adopted without a user gate. This is a materially different question from OD-17a: not "we do not know where they get it" but "we know exactly where they get it, and we know the source is suing vendors who do". The exposure is contractual and indirect (their risk, our availability), and the manual CSV path is a designed degraded state that already exists | Operator plus counsel, **before the first credit is spent** |
| **OD-18** | **Alert-service feed availability** — one provider's feed delivery is no longer documented | (a) Design email-to-inbox ingest as the default; (b) depend on the feed; (c) drop the source | **(a).** Email ingest is needed for the newsletter family anyway, so the feed is a bonus if the option still appears at setup, and its absence costs nothing | Whoever performs implementation setup, in Phase 1 |
| **OD-19** | **Launch-registry commercial-use characterisation** — the registry being **Product Hunt**, whose free GraphQL tier is read-only and non-commercial by default with commercial use invited by contact | (a) Use public pages and the RSS feed until a permission email is answered; (b) apply for commercial API terms now; (c) drop the source | **(a).** The programmatic surface is not load-bearing — the public pages and feed carry the signal, and the permission request costs one email | Operator, in Phase 0 (send the email), with no dependency for Phase 1 |
| **OD-20** | **Judge and threshold calibration governance** | (a) Human-moved thresholds only; (b) opt-in automatic recalibration; (c) automatic recalibration by default | **(a) for v1.** The system produces a monthly calibration report; a human applies it. Any proposed loosening of the brand-fit floor specifically requires a logged rationale. Automatic recalibration optimises for whatever gets rubber-stamped quickly, which is not the north star | Operator, at Stage 5. Revisit only once several months of directional agreement data exist |
| **OD-21** *(W3b assembler)* | **X assets: produce-but-never-publish, or suppress entirely?** §3.2 makes X config-gated and default-off as a publish destination while still allowing assets to be produced at no marginal cost | (a) Produce X assets, never connect X as a channel; (b) suppress X assets entirely until X is a real destination; (c) enable X as a publish destination now | **(a).** Producing the asset costs nothing beyond a few hundred tokens and means the day X becomes a destination there is a back catalogue and a proven format profile. If the operator finds unused assets in the pack annoying, (b) is a one-knob change. (c) is a separate later decision and would require confirming the publishing bridge's own X integration uses the official paid path | Operator, at Stage 5 — a preference question, not a risk question |
| **OD-22** *(W3b assembler)* | **The Czech short-form revisit window.** Design commitment six in §3.1 promises a measurable revisit trigger but does not name the number of weeks | (a) Six weeks; (b) twelve weeks; (c) a volume threshold instead of a time threshold — for example, after twenty published Czech short-form assets | **(c), with (b) as a backstop.** A time window measures the calendar; a volume threshold measures the evidence, and the evidence is what the operator overruled research to obtain. Whichever is chosen, the review reads reason-coded rejections from the review-decision store plus the operator's own read of engagement quality | Operator, at Stage 5, and the chosen trigger is logged so the review actually happens |
| **OD-23** *(W3b assembler)* | **The fallback-router engagement threshold.** §5.7 names each migration rung but deliberately leaves the trigger for integrating the registered fallback router (**fal.ai**) as an open item rather than guessing | (a) A spend threshold — integrate once monthly media spend exceeds a stated figure; (b) a reliability threshold — integrate after a stated number of degraded runs attributable to the primary router (**Kie.ai**) in a rolling window; (c) integrate now as a live second path | **(b), with (a) as a secondary trigger.** Reliability is the reason the fallback exists; spend is the reason it becomes worth the integration effort. (c) is rejected for v1 — a second live path doubles the money-safety surface for a system whose first router is still unproven. **Whichever trigger is chosen, note that rungs 4 and 5 are migration projects measured in days, not runtime failovers** (§5.7) | Operator, once four weeks of real run data exist — not before, because the threshold should be set against observed reliability rather than imagined reliability |
| **OD-24** *(W4 legal)* | **The scope of the human-editorial-review carve-out from the AI Act's text transparency limb**, and whether it can ever extend to a synthetic-presenter (deep-fake limb) asset. The evidence pack flags the carve-out's scope as an unresolved question requiring qualified counsel; the plan previously asserted the workflow "satisfies it by design" | (a) Rely on the carve-out for blog text, as the working assessment does; (b) label all AI-assisted text regardless, on the principle that over-labelling carries no sanction; (c) obtain a counsel opinion before Phase 6 | **(b) as the standing interim rule, (c) as the resolution.** Until counsel answers, label rather than rely — over-disclosure is not sanctioned and under-disclosure is. §3.3's wording is already downgraded to a working assessment, and the approver-identity and editorial-responsibility fields exist so the carve-out is *evidenceable* if it is ever relied on | **Qualified counsel, before Phase 6.** The deep-fake limb of the same question is moot for v1 under the §5.3 likeness ban, and reopens the moment that ban does |
| **OD-25** *(W4 legal)* | **Primary-text confirmation of the two Czech statutes the plan relies on** — the advertising-regulation act and the consumer-protection act. The evidence pack carries both citations at low-to-medium confidence with direct retrieval blocked, and the plan cites "Czech consumer-protection law" twice without a section reference | (a) Confirm both against the official statute register before Phase 6; (b) proceed on the current citations; (c) drop the citations and rest the controls on brand-risk grounds alone | **(a).** The *controls* are warranted regardless — never-invent, the five non-disableable check classes, and the new commercial-communication recognisability sub-class stand on their own — but a plan that cites a statute should have read it, and an audit that finds a mis-cited statute discredits the controls that were right | Qualified counsel or the operator with the statute register, **before Phase 6**. Binds the recognisability sub-class (§6.7) |
| **OD-26** *(W4 legal)* | **Verification of the EDPB web-scraping guideline reference the legitimate-interest assessment rests on** — the evidence pack carries the guideline's identification as unverified, and the LIA is built on it. Also the home for the unassessed **processor / controller / third-country-transfer** area, on which the evidence pack is silent entirely | (a) Verify the guideline against the EDPB's own register and write the recipient map before finalising the LIA; (b) finalise the LIA now and correct later; (c) obtain a full data-protection review | **(a), and it is a Phase-0 prerequisite rather than a Phase-6 one** — an LIA built on a mis-identified guideline is an LIA that has to be rewritten, and the privacy notice cannot state its Article 13 recipient and transfer sections until the recipient map (§2.6a) exists. (c) is the honest longer answer for a project that will hold personal data from day one | **Operator plus counsel, before the LIA is finalised in Phase 0.** Blocks the Phase-0 privacy gate |
| **OD-27** *(W4 fixer)* | **The employee likeness and voice agreement** — required only if the §5.3 v1 ban is ever lifted | (a) Keep the ban and defer entirely; (b) prepare a signed scope-limited agreement now, so avatars are unblocked when wanted; (c) lift the ban with a consent record designed but no agreement signed | **(a) for v1, and (c) is explicitly rejected**: a consent-record field with nothing to point at is worse than the ban, because it looks like a control. If the ban is lifted, the agreement is a prerequisite — separate, signed, scope-limited by purpose, duration, platform and revocability, and an HR matter as much as a legal one | Operator, only if and when avatars or voice cloning enter scope |
| **OD-28** *(W4 fixer)* | **Text-model provider and per-role selection** — a decision the plan could not previously state because the role did not exist. Which model fills the **drafting** role and which fills the **judge** role, per language | (a) One vendor for both roles in both languages; (b) different lineages for drafting and judging, same vendor family per role; (c) per-language selection on measured Czech and English quality, judged separately from structured-output reliability | **(c), constrained by (b).** The judge should not share a lineage with the generator — shared blind spots are the failure mode the separation exists to prevent — and the Czech drafting choice does not follow from the English one. Decide on the frozen eval set (§14.8) rather than on vendor claims | Operator, at Stage 5 for the shortlist; measured during Phase 2 against the eval set, before the first real packs |

### 16.3 Decisions deliberately deferred with named triggers

These are not open questions for Stage 5; they are future decisions with the trigger written down now so they surface at the right moment rather than being forgotten. Reopening X reads, once four weeks of runs show whether the share of packs anchored on sub-24-hour signals is persistently near zero. Pursuing a commercial contract for the pain-source platform, at multiple paying tenants. A paid demand-axis upgrade, at an eight-week review of demand-signal quality. A social-listening product, at a second paying tenant. The image-platform validation probe, after app review completes. Paid short-form analytics tiers, when short-form production ramps. A higher trend-vendor tier, on credit exhaustion. Direct model-vendor integration, on revenue and risk appetite. A callback receiver instead of polling, only if polling latency becomes material. Self-hosting the publishing bridge, as a later cost decision — feature parity is complete and the difference is operational burden.

---

## §17. Phased roadmap

### 17.1 How the phases are shaped

The phases are small on purpose. Each one ends with a set of acceptance criteria that can be *demonstrated*, not argued, and each is followed by an explicit **do-not-start-next-until** gate. The ordering follows three rules. **Cheap before expensive**: everything that costs nothing is proven before anything that costs money. **Safe before capable**: every fail-closed path is exercised before the capability it guards is enabled. **Honest before complete**: a phase that produces a degraded but truthful output is finished; a phase that produces a complete-looking output with an unproven claim inside it is not.

Phases 0–5 are the build. Phase 6 turns on distribution. Phase 7 closes the loop the assignment asks for. Phase 8 proves the multi-theme claim. Nothing about the ordering prevents an operator from running the system usefully from Phase 2 onward — every phase from that point leaves a working, if narrower, product.

### 17.2 The phases

**Phase 0 — Prerequisites, accounts and calibration material. No pipeline.**

This phase exists because four different kinds of prerequisite would otherwise block later phases at their most expensive moment: identity verifications that take days, legal artefacts the software cannot generate, vendor questions that are only answerable by trial, and calibration corpora that cannot be synthesised.

*Deliverables — accounts and identity.* Personal government-ID verification submitted for the **Meta Ad Library** API and its token-renewal runbook written (W2-15), **and the accepted Ad Library API terms stored and dated** — access is conditioned on both, and only the verification was previously scheduled. **A token-reissue runbook for the Notion internal integration token**, on the same footing, because that credential gates every fact class in both languages on every run while the ad-library one gates a single research axis (§6.2). The Product Hunt commercial-use permission email sent (OD-19).

*Deliverables — terms that nobody has read.* The **Kie.ai** router's terms of service pulled manually in a browser, dated and read (W2-12). **Reddit Pro's terms pulled the same way and read on one specific question — does it permit commercial use of the tool's derived outputs outside Reddit** — because the assessed and approved mitigation in the evidence pack was *reading Reddit in an ordinary browser session*, and Reddit Pro is a separate product with its own terms that nobody has evaluated. **Each licensed vendor's terms — Virlo.ai and DataForSEO — retrieved, dated and checked for a pipeline/derivative-use permission**, recorded in the vendor roster beside last-verified and recheck-by, **before the first credit is spent** (OD-17a, OD-17b, §2.4).

*Deliverables — provider capability questions that gate architecture.* **Person-generation eligibility determined for this account and region, and any allowlist request submitted** — the primary video family restricts EU person generation, refuses named real people at model level, and has been observed to require per-account approval with a lead time; a lead time discovered in Phase 4 is paid twice (§5.7). **"Does the router's task-status response name the rendering model?"** answered by inspection, because the provenance record's delivered-identity field is a publish-gate precondition and the evidence pack never established it is observable (§5.6).

*Deliverables — legal artefacts the software cannot generate.* The **legitimate-interest assessment**, produced **per purpose and per source family** rather than as one blanket document — blanket assessments are explicitly ruled out by the guidance the assessment rests on, and the source portfolio spans genuinely different processing profiles (a public developer forum, an open social protocol, an operator's own hand-written notes). Each assessment states its purpose test, its necessity test, its balancing test, and the route by which a data subject objects. The **published privacy notice**, naming **ÚOOÚ** as the supervisory authority, the contact point, the objection and erasure route, and the right to lodge a complaint — and carrying its Article 13 **categories of recipients** and **third-country transfer** sections, which cannot be written until the **recipient map** (§2.6a) exists. **The EDPB web-scraping guideline reference verified against the EDPB's own register before the assessment is finalised** (OD-26), because an assessment built on a mis-identified guideline has to be rewritten.

*Deliverables — configuration and calibration.* Designated fact locations chosen in the knowledge base and the plan-versus-fact separation confirmed, with an internal integration token issued read-only and scoped (W2-11). The claim ledger seeded with whatever is genuinely approved — **an honestly empty ledger is a valid Phase-0 outcome**; an unreadable one is not. Hard excludes written into configuration as the baseline that must survive an outage. The **special-category source deny-list** written (§2.6). The pinned **FFmpeg** version installed on the target platform with fonts bundled and Czech glyph coverage verified (OD-10 — whose decision point moves to *before Phase 0*, since this deliverable consumes it). Exemplar corpora assembled per language. **Four calibration artefacts, not two:** the **Czech structural-calibration corpus** and the **English structural-calibration measurement pass** over the English corpus — because layer 2's numeric bands need a real tokenisation and measurement pass in *both* languages, and the English one was simply never scheduled; and the **Czech judge golden set** (adapted positives, deliberate negatives seeded from machine-translated English marketing copy, real borderline drafts) **and the English judge golden set**, without which the English flag-rate ceiling has no predicted baseline and the judge-health signal does not exist until Phase 7. The **frozen eval set** per language, built alongside the golden sets and **never read while authoring prompts** (§14.8). The Virlo one-week trial run.

*Acceptance criteria.* The **trend-vendor trial verdict is recorded** and answers its three gating questions (OD-16) — adopt Virlo, fall back to Shortimize, or accept the monthly Creative Center ritual as the designed degraded state. The **ad-library identity verification is confirmed complete**, a token has been issued, its expiry date recorded, and the accepted API terms stored. **Every unread-terms item above has been read and dated, and any surprise is logged** — router, Reddit Pro, both licensed vendors. **Person-generation eligibility is answered and any allowlist request is submitted.** **The router's model-identity reporting question is answered**, and if the answer is no, §5.6's inference rule is the one that ships. **Both golden sets** produce stable judge verdicts on their own known-good and known-bad items when run by hand. **Both privacy artefacts exist *and* meet their stated shape** — the assessment is per purpose and per source family, and the notice carries its recipient and transfer sections — because existence was the old gate and existence is not content.

*Do not start Phase 1 until:* **the four calibration artefacts exist (Czech and English structural calibration, Czech and English golden sets), the frozen eval set exists, and the two company privacy artefacts exist in their required shape with the EDPB reference verified.** Everything else in this phase may run in parallel with Phase 1; these may not, because retrofitting them costs a rewrite of the affected language path and a compliance gap respectively.

**Phase 1 — Zero-cost skeleton: theme load, collection, ranking, packaging.**

The narrowest end-to-end run that produces something a human can read. Theme load with fail-closed secret checking; three or four free collectors only; the research artifact store with its retention rules and targeted deletion; ranking with scorecards, the fit gate and the dedupe index; packaging and the run digest; the run ledger and the exit-code taxonomy. No brand truth, no generation, no money.

*Acceptance criteria.* A run completes end to end and writes a digest an operator can scan in about two minutes. Every candidate carries an inspectable scorecard with sub-scores, plain-language bands, one-line rationales, the sources and families that corroborated it, and the specific gate outcome. **A run producing zero passing candidates completes successfully and says so** rather than being treated as a failure. Running twice on the same day does not re-fetch rate-limited sources and does not re-rank the same topics as new discoveries. A deliberately broken source produces a degraded-source banner and the run still exits **partial-success — degraded sources**. A source returning a **byte-identical payload to its previous pull** raises the *stale payload suspected* degraded reason, distinct from the zero-signal alarm. **Targeted deletion by canonical key works on a real stored record *and reaches inside an already-packaged, archived run pack*** — the second half being the one that makes an Article 17 or 21 request executable at all, and the one the run-pack → canonical-key index exists for. **The provenance snapshot's verbatim half expires on schedule and is replaced in the packed pack by its placeholder**, while the de-identified half remains.

*Do not start Phase 2 until:* the dedupe index demonstrably prevents yesterday's topic from reappearing as today's discovery **and the resurgence rule is exercised in all three of its states — rising-and-never-generated ranks, rising-and-generated-with-a-new-angle re-enters tagged "revisit", rising-and-generated-with-nothing-new is suppressed** (§2.8a) — and the exit-code classes are distinguishable from outside the process.

**Phase 2 — Brand truth, spin, copy and the full gate chain. Still zero media spend.**

Brand-truth resolution with per-fact-class precedence, the three asymmetries and the confidence bands; the exact degrade trigger; spin mapping with mapping distance and CTA classes; copy generation per destination per language; the complete gate chain — spin, claim pass 1, voice, claim pass 2, platform.

*Acceptance criteria.* A deliberately introduced disagreement on a commercially binding fact produces a **red-flag stop with both values shown side by side and their sources and timestamps**, and no tie-break. Making the knowledge base unreachable produces a research-only run that spends nothing, completes research and ranking, saves them for reuse, and states the cause in one sentence. An asset containing an unsupported number is blocked, regenerated once with the specific failing span cited, and either passes or downgrades to the claim-free variant. **A claim reintroduced by the voice gate's rewrite is caught by claim pass 2** — this is the test that proves the double pass is not ceremony — **and the repair that follows re-enters the voice gate and the spin post-check before pass 2 closes again**, which is the test that proves the re-entry rule is real rather than drawn (§6.10). Czech and English packs can be at different confidence bands simultaneously without either being an error. A far-distance topic carrying a product pitch fails the spin gate and downgrades to the value-only variant. **A gate deliberately made unavailable fails its artifact closed with the gate named** — the voice judge labelled, the claim semantic pass falling back to deterministic verdicts with all claim-shaped candidates blocked — rather than defaulting open (§11.3). **The confidence band's derivation is reproducible from the brand-truth panel by counting**, with no scored step to argue about.

*Do not start Phase 3 until:* the degrade trigger has been fired deliberately for each of its five conditions and each names itself correctly in the digest, **and the fifth fail-closed trigger has been fired for at least two different gates**.

**Phase 3 — Media planning, draft-tier generation, assembly and disclosure.**

Media planning (always produced, zero cost); the model registry; the routing contract; the cost gate; draft-tier generation only; the write-ahead spend ledger and the media-job ledger; re-hosting with checksums; the assembly engine with captions from the script, typography, ducking, loudness mastering, safe zones, end card and the burned-in disclosure.

*Acceptance criteria.* **Balance-delta reconciliation is validated against real spend**: a small number of deliberate draft-tier generations are performed and the ledger's expected cost is reconciled against the observed balance movement, with the unexplained-spend circuit breaker proven to halt new submissions when the two diverge beyond tolerance (W2-02). Killing the process mid-generation and restarting resolves every in-flight job **by querying task status, never by resubmitting**, and any job in the ambiguous window is left in the named submitted-unknown state with no automatic action. A truncated download is never marked complete. Provider URLs appear nowhere in a pack. An asset without the burned-in disclosure cannot be marked publish-ready.

**Six further acceptance criteria, each testing something that was previously asserted rather than checked:**

- **An asset whose only generated component is a text-to-speech voice track — no generative video clip anywhere in the loop — carries the burned-in disclosure.** This is the Czech default recipe, the largest volume of assets in the pipeline, and the exact case the old AI-content-class default omitted.
- **The disclosure is verified by measurement, not by presence**: first-appearance timestamp, type-height ratio and contrast ratio are logged per asset in the same shape as the loudness gate, and an out-of-range asset fails closed. A **static asset** — a carousel and a feed still — is measured too, with the disclosure present on the first and final slide of a multi-page asset.
- **An asset with a deliberately damaged provenance record does not reach publish-ready**, and an asset whose delivered route resolves to *substituted — identity unknown* degrades to plan-only with the reason attached rather than publishing on an assumed identity.
- **Measured loudness** is logged per asset and an out-of-range asset fails closed. Czech on-screen text renders with complete glyph coverage in the bundled font, **including in the multi-page document export**.
- **A paper-level conformance check of the four routing contracts against the fallback router's published surface** is completed and its gaps recorded (§5.7) — an hour of work that is the only thing making "registered fallback" mean more than "named".
- **An unsupported number composed into on-screen text at assembly is blocked by the post-assembly overlay claim pass**, and the asset does not reach publish-ready. The test is run in both directions on both asset shapes: a video master whose overlay slot is deliberately fed a figure with no ledger entry, and a carousel slide carrying a deliberately unsupported percentage, each blocked with the offending string named and routed to the QA-flag path (§4.4, §4.9); and a **disallowed slot pair** — two individually verified strings a template forbids in one frame — refused at composition rather than at inspection. The criterion exists because **this is the one claim surface that no earlier gate has ever seen**: on-screen text is composed after claim pass 2 closes, so an asset that passed every text gate cleanly can still ship a fabricated number in 96-point type. A run in which the overlay pass is deliberately made unavailable must fail its assets closed under §11.3's fifth trigger, with the gate named, rather than assembling on.

*Do not start Phase 4 until:* the crash-and-resume test has been run at least twice with real paid draft-tier work in flight, and no money was lost or double-spent.

**Phase 4 — Standard tier, both language recipes, the first real packs.**

Standard-tier generation from approved keyframes; the keyframe-acceptance event as the approval unit; the Czech carousel-to-reel recipe end to end with Czech voice; the identical-mix matrix across both languages; the four-level cap enforcement including mid-pack cap-hit.

*Acceptance criteria.* Eight to ten real two-language **topic packs** — one topic × two languages each, using the term consistently, since "pack" elsewhere means a whole run's output and the two readings differ by roughly five times against a $35 envelope — produced inside the documented trial envelope with the reserve untouched.

**And a criterion that actually discriminates, because "the reserve was untouched" does not.** The envelope is sized on the assumption that both languages buy generative clips (~$3.80 per two-language topic pack); the default configuration runs Czech on CS-B and lands nearer $1.90, so ten topic packs cost roughly $19 against ~$35 of envelope — meaning the caps could be set at roughly double the recommendation and this gate would still pass with the reserve intact. The gate therefore measures the thing directly: **measured per-topic-pack spend is within a stated percentage of the forecast** (which tests that the forecast is honest), **and the configured per-run cap is no more than a stated small multiple of measured per-topic-pack spend** (which tests that the caps are sized against reality rather than against headroom). Both wallets are measured, media and text. The envelope's ~2× conservatism is stated in §5.4 rather than being silently relied on.

The mid-pack cap-hit behaviour is demonstrated **deliberately, at least once, in masters units**: the pack ships partial and clearly marked, one language's masters complete and reviewable with its derivative destinations intact, the other language's media explicitly flagged *not generated — budget capped*, its copy and plans present, and the run exiting **partial-success — budget-capped mid-pack**. **Completion of that capped pack is then exercised through an explicit regenerate-media-only invocation against the same run id**, producing a pack amendment rather than a fresh pack (§8.11, §4.7a). **At least five Czech short-form assets are produced and reviewed**, so the Czech rejection-reason distribution that R-23's leading indicator depends on exists before production rather than after it. **The Czech short-form production floor passes as a hard gate**, not as advice — prosody accepted, glyph coverage verified, no English audio anywhere, and every English assembly gate also cleared. A silent model substitution, if one occurs, is visible on the artifact as requested-versus-delivered; if none occurs naturally, the recording path and the inference rule are verified by inspection. A refusal produces the bounded ladder and terminates in a **complete plan-only artifact with the reason attached**, never a retry loop.

**Measured review time against §3.5's table, not the estimate.** Across the eight to ten real topic packs this phase already requires, the operator's own review time is logged per decision — digest scan, keyframe acceptance, per-asset copy read-through, confirmation pass — timestamped in the review-decision store exactly as §11.4 already records every decision, so no new instrumentation is invented. Logged times are compared against Block 1's table and against the confirmation-pass figure Block 2 left explicitly unmeasured. This closes the gap directly: the 20–30 minutes per finished video the whole review-burden model rests on is currently a citation from A1, used directionally, not a measurement of this pipeline's actual assets. Phase 4 is where it becomes one, and OD-8's own "revisit after four weeks of real runs using measured review time, not the estimate" is the decision this feeds. If measured confirmation-pass time diverges materially from the illustrative bound in Block 4, that figure — and the topics-per-run default it partly justifies — is revisited against the measurement, not defended against it.

*Do not start Phase 5 until:* the operator has reviewed at least five real packs and judged that a majority of assets are publishable — because scheduling a pipeline whose output is not worth reviewing simply automates disappointment.

**Phase 5 — Unattended scheduling.**

The same entrypoint under the operating system's scheduler; run identity and the run-lock; phase-zero adoption of pending media and the expiry-ordered download queue; the missed-run policy; notifications; the mode capability resolver exercised with nobody present.

*Acceptance criteria.* A scheduled run completes overnight under the operator's own account and leaves a reviewable pack. Two overlapping invocations produce exactly one run and one **skipped-overlap** outcome, with no killed process and no orphaned paid job. A run straddling midnight uses one pinned run-date throughout. Czech characters survive the console and the log files. The filesystem status flag is written in every case, including failures, and an email failure does not change the exit class. A missed window is skipped, not backfilled, and the run ledger records how many were missed. A deliberately removed secret produces a fail-closed stop naming the missing item.

*Do not start Phase 6 until:* three consecutive unattended runs have completed without manual intervention and their exit classes match what actually happened.

**Phase 6 — Distribution: the publishing bridge, drafts only.**

The publishing-bridge account is created at this point and not before, per the operator's stated priority of proving research-to-assets first. The publish gate; the connected-channel set; the review-decision store; the AI-label acknowledgement; the three-rung fallback ladder.

*Acceptance criteria.* **Draft-without-schedule verification against a real account** (OP-2): unscheduled draft creation succeeds for a batch of posts with no auto-publish trigger ever firing; draft state persists across a restart of the bridge; draft-to-schedule and schedule-to-draft transitions both work; drafts are visible in the bridge's own review surface. Whether any per-platform AI-disclosure field has appeared since the research date is **re-tested explicitly** and recorded. **The publish gate is proven fail-closed on seven separate conditions — one per check enumerated at §7.4, and the count is derived from that list rather than maintained here:** (1) wrong mode; (2) destination not in the active mode's allowlist; (3) destination allowlisted but not connected; (4) asset lacking any recorded approve decision; (5) asset requiring disclosure without the separately recorded AI-label acknowledgement; (6) provenance record incomplete, or delivered rights class outside the destination's rights-class allowlist; and (7) **an asset whose bytes changed after approval does not reach publish-ready.**

Condition 7 is tested end to end rather than by inspection, because it is the one that only manifests across runs: approve a pack at revision 1 in an interactive session while one video master is plan-only and blocked on a clip; let a later run adopt the clip, assemble, master and amend the pack to revision 2 under §4.7a; **with the unattended draft-creation knob deliberately switched on**, confirm that distribution prep does not run for that asset, that the pack names it as *approval superseded by revision N — re-approval required*, and that every unamended asset in the same pack keeps its approval and remains eligible. The same test is then repeated for the two other byte-changing paths — regenerate-media-only completion of a budget-capped pack (§8.11) and an immediate-loop segment regeneration (§12.4) — because a rule that holds on one path and not the others is not a rule.

Rung 3 — local-only staging for manual paste — is exercised at least once and proven complete enough to publish from; **and specifically, an asset that the publish gate *blocks* for a destination arrives in rung-3 staging carrying a visible, unticked per-platform label checklist rather than as clean pasteable text**, which is the test that the acknowledgement travels with the artefact on the one path that never calls the bridge.

*Do not start Phase 7 until:* the publish gate has been proven fail-closed on all seven conditions, with the rest of the sentence unchanged.

**Phase 7 — The feedback loop: winners and losers.**

The assignment's tenth loop step, and the first phase whose value compounds. Three loops, deliberately separate so that a same-session fix is never confused with a slow calibration change (§12.4): the **immediate loop** (a rejected asset regenerates within the current pack, subject to the same caps); the **weekly loop** (aggregated rejection reasons inform prompt-library and rubric refinements, read and applied by a human); and the **theme-tuning loop** (ranking thresholds, brand-fit floor and judge cutoffs reported monthly and moved only by a logged human rationale).

This phase also adds the winners half, which the review-decision store alone cannot supply: **outcome capture for published assets**. Because the system never publishes, engagement is not something it can observe — so the design is a **third permitted operator input class: post-hoc outcome notes** (W7-2), recorded after a pack's assets are published and engagement is known. These are annotations about content already published and cannot influence what a run collects, ranks or generates; the property W6-1 exists to protect — that no run waits on a human and no pipeline stage takes hand-fed data — is untouched by this input, which **degrades the calibration loop** if never arrives but never degrades a run (§12.4).

*Acceptance criteria.* Reason-coded rejections aggregate across at least four weeks of packs into a report a human can act on in one sitting. The report distinguishes **judge-passed/human-failed** from **judge-failed/human-passed**, because the two directions carry different costs and are tuned separately. A rolling flag-rate ceiling is being tracked per theme, destination and language, and a deliberate over-strict judge configuration is detected by it rather than by the operator noticing a queue. At least one prompt-library or rubric change has been made, applied by a human, and re-calibrated against the golden set afterwards — because a rubric change without a fresh calibration pass is exactly how silent drift happens. Winners are attributable: for at least a handful of published assets, the pack, the topic, the recipe, the route and the operator's outcome note can be read together.

*Do not start Phase 8 until:* at least one calibration cycle has completed end to end — report produced, human decision taken, rationale logged, golden set re-run.

**Phase 8 — Multi-theme proof.**

The second-theme fixture from §13.3 is configured and run. No engine change is permitted during this phase; anything that *requires* one is a finding, logged as such, and is the honest measure of how extensible the design actually turned out to be.

*Acceptance criteria.* The fixture reaches theme-readiness validation and passes every assertion in §13.2. It produces a real pack in its single language, through the same canonical stage order and the same gates, with a different source roster, a different destination matrix, no generative video and no counted-evidence source anywhere. **The shared language overlay is reused unchanged** — the fixture supplies only its own exemplar corpus. Any engine change that turned out to be necessary is documented with its cause.

### 17.3 The phase gates in one view

    Phase 0  prerequisites, corpora, trials, unread terms
      |  gate: FOUR calibration artefacts exist (cs + en structural,
      |        cs + en golden sets) + frozen eval set exists;
      |        privacy artefacts exist IN SHAPE (per purpose/source
      |        family; recipient + transfer sections written;
      |        EDPB reference verified)
      v
    Phase 1  zero-cost skeleton (collect -> rank -> pack -> digest)
      |  gate: cross-day dedupe proven in all three resurgence states;
      |        deletion reaches inside an archived pack;
      |        exit classes distinguishable
      v
    Phase 2  brand truth + spin + copy + full gate chain
      |  gate: all five degrade conditions fired deliberately and named;
      |        fifth fail-closed trigger fired for two gates
      v
    Phase 3  media planning + draft tier + assembly + disclosure
      |  gate: crash-and-resume proven twice with real paid work in flight
      v
    Phase 4  standard tier + both recipes + real packs
      |  gate: operator judges a majority of assets publishable
      v
    Phase 5  unattended scheduling
      |  gate: three consecutive clean unattended runs
      v
    Phase 6  distribution (drafts only)
      |  gate: publish gate fail-closed on four conditions;
      |        draft-without-schedule verified or rung 2 adopted
      v
    Phase 7  feedback loop (winners / losers)
      |  gate: one full calibration cycle completed
      v
    Phase 8  second-theme fixture

---

## §18. How a human should test and review this plan before build

### 18.1 What this review is for

This is the last cheap moment. Every problem found here costs a paragraph; the same problem found in Phase 4 costs a rewrite and some of the trial budget. The review has two halves and they are different activities. The first half is a **completeness check** against the assignment's own design-phase success criteria — does the plan actually say the thing it was asked to say, clearly enough for a marketing-literate operator to act on. The second half is **adversarial**: pick a failure from §15 and interrogate the plan about it until either the answer is concrete or the gap is real.

Do both. A plan can pass the checklist and still be brittle, and it can survive the adversarial pass while quietly omitting something the assignment demanded.

The review changelog — what was asked, what changed, what was accepted as-is — belongs in **Appendix B**, not here.

### 18.2 Half one — the completeness checklist, mapped to the ten success criteria

Each row names what to read, what "good" looks like, and the most likely way the plan could be wrong. Mark each pass, fail, or needs-work.

| # | Success criterion | Read | Passes when | Most likely failure |
|---|---|---|---|---|
| 1 | **Best practices and the tool/prompt/skill stack for viral AI video** | §4 in full — **including §4.2a (the keyframe-acceptance rubric) and §4.10 (the prompt and skill layer)** — plus §5.2 | You can explain, without re-reading, why the keyframe is the approval unit, what the rubric actually checks, and why that single choice controls the budget; the spend tiers are distinguishable; the three legal recipes are clear; **the brand lock has contents, the five negative-prompt layers each have an owner, and all four skill bundles are named** | The plan describes video production but never makes the economics of it legible — or refers to prompt/skill material that lives only in the evidence base |
| 2 | **Where viral topics are extracted and how, including the automation policy** | §2.3, §2.4, §2.5 | Every source has a method, a cadence, a failure mode and a fallback; the do-not-scrape list is binding in every mode; browser automation is honestly argued out of the collection path rather than quietly omitted | The portfolio reads as aspirational — a source listed with no honest account of how it actually breaks |
| 3 | **Which platforms are research versus asset generation** | §2.3, §3.2, §7.4 | You can point at the one enforcement point and the one list it reads; research sources are structurally incapable of being publish targets | The separation exists in prose but is enforced in more than one place |
| 4 | **How brand spin resolves from config, knowledge base and public verification** | §6.2, §6.3, §6.4, §6.5 | Precedence is per fact class and you can say why the live site wins on prices; the three asymmetries make sense; the degrade trigger has five concrete conditions rather than a vibe | Precedence is stated as one flat order, which is wrong for commercially binding facts |
| 5 | **How the media providers fit** | §5.1, §5.2, §5.3, §5.7 | Provider *roles* are separable from vendor names; the registry answers model churn; the fallback ladder never silently produces a worse asset | A vendor name is load-bearing somewhere, so churn would require a redesign |
| 6 | **How draft-first social publishing works after human approval** | §7.1, §7.2, §7.4, §7.6 | Nothing publishes in any mode; the three-rung fallback is genuinely usable at every rung; the label gap has an explicit control | The plan trusts the bridge's documentation as if it were verified |
| 7 | **How multi-theme config changes research targets and brand spin** | §10, §13 | Every knob names its consuming sections; the second-theme fixture changes sources, destinations, ranking treatment, recipes and register without an engine change | The extensibility claim is asserted rather than walked |
| 8 | **How humans review before anything goes live** | §12, §11.4, §3.5 | You would actually use the digest; rejection is granular and reason-coded; the review-effort estimates match your own sense of the work | The review model assumes affordances the runtime does not fund |
| 9 | **How the console app runs automatically while staying safe** | §8, §9.2, §11 | Run identity, overlap, missed runs, secrets, exit classes and budget caps are all concrete; every fail-closed trigger is named and none is configurable away | Cron safety is described as a property rather than as specific mechanisms |
| 10 | **What to build first, second and third, and how to know each phase is good** | §17 | Acceptance criteria are demonstrable rather than arguable; the do-not-start gates are ones you would actually enforce; the feedback-loop phase exists | Phases are big enough that "done" becomes a judgement call |

Two additional completeness checks that are not success criteria but are non-negotiable constraints: **the Czech output set is first-class in every layer** (§2.7, §3.1, §3.4, §4.8, §6.12, §14.4 — check all six, and confirm none of them treats Czech as English plus a translation step); and **nothing in the plan can publish, in any mode** (§11.1 — check that live publishing and production site merges are marked never rather than merely switched off).

### 18.3 Half two — adversarial questions, mapped to §15

Ask the plan each question. A good answer names a mechanism and a section; a bad answer names an intention. If the answer is "we would notice", ask *how*.

| Ask the plan: what happens when… | Should point at | You are testing |
|---|---|---|
| …a free source silently starts returning an empty list at 03:00? | R-01 · §2.2, §8.10 | Whether degradation is detected or merely survived |
| …a source that used to work becomes login-walled? | R-02 · §2.5 | Whether the do-not-scrape list holds under pressure, including in degraded modes |
| …the trend vendor is acquired and its endpoint dies mid-month? | R-03 · §2.2 | Whether vendor churn was designed for or assumed away |
| …the trial reveals the vendor's programmatic access is not included at the tier we bought? | R-04 · §17 Phase 0 | Whether adoption is genuinely trial-gated or already assumed |
| …the ad-library token expires on a Tuesday and nobody notices for six weeks? | R-05 · §2.3 | Whether credential expiry is an alarm or a silent axis loss |
| …the trend vendor fails its trial and the fallback also fails? | OD-16 · §2.3, §16.2, `RISK_LOG.md` W7-01 | Whether an absent short-form trend axis is visible and recoverable in the pack and in the operator's awareness, or whether the pack reads as "complete" while shipping no short-form trend signal |
| …the media router is down for two days? | R-07 · §5.7 | Whether plan-only is a real, complete outcome or a euphemism for failure |
| …the router quietly renders with a different model at a different aspect ratio? | R-08 · §5.6, §8.13 | Whether the pack knows what actually rendered it, and whether the rights record is still true |
| …the process is killed after submitting ten dollars of generation? | R-09, R-13 · §8.5, §8.7 | Whether paid work survives, and whether restart resolves by query rather than by resubmission |
| …the balance drops by more than the ledger expected? | R-09 · §5.6 | Whether unexplained spend is an alarm that stops the system or a line in a log |
| …the judge starts failing everything after a model update? | R-10, R-21 · §14.2 | Whether the cost circuit breaker is independent of the *reason* for failing |
| …Czech is promoted to generative clips and the monthly bill doubles? | R-11 · §3.1, §5.4 | Whether the "Czech is cheaper" claim is stated conditionally, as it must be |
| …a single mis-configured run tries to spend the whole trial balance? | R-12 · §4.6, §8.11 | Whether caps are pre-submission at four levels, and whether hero tier can ever be auto-selected |
| …the schedule fires twice because of a clock change? | R-14 · §8.3 | Whether run identity and the lock are real mechanisms |
| …the knowledge base is unreachable at 03:00? | R-15 · §6.6 | Whether the offline path caps confidence rather than merely continuing |
| …a roadmap page says we do something we do not actually do? | R-16 · §6.2, §6.3 | Whether the control is structural or statistical — statistical answers fail this question |
| …the claim ledger cannot be read, as opposed to being empty? | R-17 · §6.5 | Whether "missing" and "empty" are genuinely distinguished |
| …a finished video reaches publish-ready without a visible AI disclosure? | R-18 · §4.4, §14.6 | Whether the disclosure is a precondition or a checklist item |
| …the operator is in a hurry and skips the platform-native AI label? | R-19 · §7.7 | Whether the acknowledgement is separately recorded or bundled into approval |
| …the publishing bridge turns out not to support unscheduled drafts? | R-20 · §7.2, §7.8 | Whether rungs 2 and 3 are load-bearing or decorative |
| …a Czech pack comes back empty week after week? | R-22 · §2.7, §13.2 | Whether a language can die quietly, or whether validation catches it |
| …the Czech short-form assets get a cold reception in the home market? | R-23 · §3.1, §15.4 | Whether the replacement mitigation for W2-08 is enforceable, and whether the revisit trigger is real |
| …someone asks us to delete everything we hold about them? | R-24 · §2.6 | Whether targeted deletion by canonical key exists from day one |
| …a collected post contains instructions aimed at our own model? | R-25 · §2.7 | Whether collected text is data or instructions |
| …someone proposes lowering the brand-fit floor to hit a volume target? | R-26 · §2.7, OD-20 | Whether threshold governance has friction in it |
| …a destination is in the allowlist but was never connected? | R-33 · §7.4 | Whether the failure is named per destination or silently skipped |
| …a generated post repeats a competitor's impressive number from the exemplar corpus? | R-34 · §6.11 | Whether corpus leakage is a check class or a hope |

### 18.4 A one-hour review path

If time is short, this order finds the most problems per minute. Read §0.1 and §0.2 to know what governs (5 minutes). Read Appendix A end to end — one topic through the whole pipeline is the fastest way to find a seam that does not join (15 minutes). Read §11.1, §11.2 and §7.4 together — the safety story is either coherent in fifteen minutes or it is not coherent (10 minutes). Skim §15's table and pick the five failures that would most annoy you personally, then run their adversarial questions (15 minutes). Read §17's phase gates and ask whether you would actually enforce each one (10 minutes). Record the outcome in Appendix B (5 minutes).

### 18.5 What to do with the outcome

Three verdicts are useful and a fourth is not. **Approve** means the direction is right and the open decisions in §16 can be answered at Stage 5. **Approve with changes** means specific sections are named for revision and the rest proceeds — record the list in Appendix B. **Reject a section** means one part is wrong enough to redesign, which is cheap now and is exactly what this review is for. The fourth verdict — *approve because it is long and looks thorough* — is the one this section exists to prevent. Length is not evidence; the adversarial questions are.

---

## Appendix A — One topic, traced end to end

*A worked example, written so a reviewer can check whether the seams between sections actually join. The topic and the numbers are plausible rather than observed: sub-scores are illustrative, and every cost figure is read from the model registry's 2026-08-06 price snapshot (A2) rather than hard-coded — the forecast an operator actually sees is computed at run time with its snapshot date displayed (§5.2, §12.1). The run described is a **scheduled pack run** in test mode, so every unattended rule applies.*

***Read this before the walkthrough, because it is the one thing about the run that is not the default.*** *This run has **dry-run deliberately switched off**. Test mode defaults dry-run **on** (§10.4a), which means a theme's ordinary first run produces every plan and spends nothing — that is the safe default and it is not what is traced below. An operator switches dry-run off in test for exactly one reason, and it is the reason here: **to prove the media path with real money while every publishing side effect is still structurally impossible**, because in test mode the publish allowlist is empty by construction and no bridge call can be attempted. Test mode is where you go to spend safely, not where you go to spend nothing. The distinction the reader should carry away is §4.6's one-sentence rule: **a mode never authorises spend on its own; the dry-run flag is what converts a forecast into a submission.** A reader who takes "scheduled run in test mode" to imply "free" has learned the wrong rule from an otherwise accurate example — which is why this paragraph sits above the diagram rather than in a footnote.*

### A.1 The run in one diagram

    03:00  scheduler fires -> run identity pinned (theme + run-date + attempt 1)
           lock acquired (no overlap)
             |
             v
    PHASE 0  adopt pending media from the previous run: none
             drain download queue by nearest expiry: empty
             |
             v
    BRAND-TRUTH RESOLUTION (before anything is spent)
      identity, offers+status, capabilities (+/-), ICP map, CTA set,
      claim ledger, excludes  --> read from designated fact locations
      live-site verification: product page 200, Czech product page 404
      band:  en = FULL      cs = PARTIAL
      claim-ledger expiry sweep: 1 entry expires in 21 days
             |
             v
    [BRAND-TRUTH GATE]  pass (both languages above the degrade floor)
             |
             v
    COLLECTION  (7 sources attempted, 6 returned, 1 degraded)
      developer-discourse hub .......... 1 strong thread   [collector]
      AI newsletter relay .............. same event echoed [collector]
      curated inbox .................... 2 saved threads   [curated inbox]
      demand-data vendor ............... rising, incl. CZ  [MCP source]
      open social firehose ............. 3 posts           [collector]
      professional-network ad library .. 1 long-running ad [curated inbox]
      trend-intelligence vendor ........ DEGRADED (credit pacing)
             |
             v
    RANKING  -> 14 candidates -> 1 vetoed (injection phrasing)
                              -> 8 below the brand-fit floor
                              -> 5 ranked topics
      **[Note: This walkthrough was traced under the earlier five-topic default (§10.2), before Block 4 of the review-burden spec reduced it to three. The ratios and proportions illustrated here remain valid at three topics; the absolute count does not. See §3.2 for the consequence statement at three topics: one to two of three now receive no rendered media, versus three or four of five previously.]**
      [FIT GATE] passed by this topic at rank 1
             |
             v
    SPIN  pain -> offer lookup -> mapping distance ADJACENT
                              -> CTA class: product-path (en) / content (cs)
             |
             v
    COPY GENERATION  -> per-asset gate chain -> MEDIA PLANNING (free)
             |
             v
    [COST GATE]  DRY RUN OFF for this run (deliberate, see header)
                 media forecast $2.10 vs per-run cap $6.00 -> proceed
                 text forecast  shown separately, own snapshot date,
                   within the per-run text budget and per-stage
                   call ceilings (§5.4a)
                 hero tier not selected (never auto-selected)
             |
             v
    MEDIA GENERATION (draft tier -> keyframe acceptance -> standard tier)
             |
             v
    ASSEMBLY  -> cs master assembled (all inputs present)
              -> en master BLOCKED-ON-INPUTS (clip 2 still rendering)
              -> ASSET QA RUBRIC on what is assembled
             |
             v
    PACKAGING -> run digest -> NOTIFICATION (flag + email)
             |
             v
    exit: completed-with-pending-media
          (1 en clip + 1 cs voice render still rendering; the en video
           master is packaged as plan-only-plus-completed-clips with a
           days-to-deletion countdown, NOT as a finished master)
             |
             v
    08:20  operator opens the digest -> [HUMAN REVIEW GATE]
           approves most; rejects the cs Reel with segment-level feedback
             |
             v
    next run  PHASE 0 adopts the pending en clip + cs voice render,
              re-hosts in expiry order, the assembly ledger row leaves
              blocked-on-inputs, the en master is assembled and mastered,
              and THIS run's pack is AMENDED (revision 2) with an
              amendment record written against the original run id
             |
             v
    later  [PUBLISH GATE] -> DISTRIBUTION PREP (drafts only)

### A.2 Collected — the signal and where it came from

The anchor signal is a front-page thread on the **developer-discourse hub**, collected by a **collector** against that source's official free API — no key, reads permitted with a crawl delay, and the source is the P0 anchor precisely because it is the only sub-24-hour surface left in the roster (§2.3). The thread reports that a major mailbox provider's bulk-sender enforcement update has started routing legitimate cold outbound to spam folders without any visible bounce, and the comments are full of practitioners comparing before-and-after reply rates.

Four other signals attach to the same **topic cluster key**:

- An **AI newsletter** mentions it the next morning. The ranking engine recognises this as the **editorial relay family echoing the same event**, not a second independent observation, and does not count it toward corroboration (§2.7). This is the mechanism that stops already-over-covered stories from inflating further.
- Two threads saved by the operator during the weekly **curated inbox** session, both from practitioners describing the same symptom in their own words. Evidence class: **human-asserted**, carried as operator salience and never rendered as measured virality.
- The **demand-data vendor**, consumed as an **MCP source**, shows rising query volume for deliverability terms — including at Czech geography, which is one of only four global carriers of direct Czech signal.
- A competitor ad in the professional-network ad library, entered through the **curated inbox** on the biweekly sweep, has been running an "inbox placement audit" offer for six weeks. Signal class **ad-creative-pattern**, whose age term is **inverted** — a still-running ad is a proven ad (§2.7).

One source was unavailable: the **trend-intelligence vendor** hit its monthly credit pacing rule and returned nothing. That is a degraded source, not a failure, and it appears as a banner in the digest naming the short-form trend axis as absent this run.

Everything collected is stored as a normalised signal record with a canonical key, a minimised author handle, a language stamp and a provenance snapshot; the raw payloads expire in thirty days and the provenance snapshot stays with the pack permanently (§2.6). All of it is carried into later prompts as **quoted data with provenance tags, never as instructions** — and one unrelated candidate in the same run was vetoed outright for injection-style phrasing (§2.7).

### A.3 Ranked — the scorecard

| Dimension | English | Czech | Note |
|---|---|---|---|
| Virality / attention | **0.88** (High evidence) | *omitted* | Counted-class, percentile within the source's own trailing distribution. The Czech composite drops virality entirely because no Czech-signal carrier exposes engagement counts (§2.7) |
| Brand fit | **0.81** | **0.78** | Well above the 0.35 floor. The falsifiable verdict: *"Agencies running outbound for clients are watching reply rates fall for reasons they cannot see; the honest connection is diagnosing deliverability before blaming copy."* |
| Freshness | **0.93** | **0.93** | Signal class *rising*, age 14 hours |
| Confidence and availability | **0.85** | **0.85** | **Retained for Czech — only virality is dropped.** Three source families corroborate (developer discourse, human-curated, ad creative); the relay is excluded; the short-form axis is missing this run. This factor is what carries the "under-evidenced ≠ poor fit" honesty, so dropping it for Czech would equate thin evidence with good fit (§2.7) |
| **Composite** | 0.88 × 0.81 × 0.93 × 0.85 = **0.56** | 0.78 × 0.93 × 0.85 = **0.62** | Different formulas, deliberately: English is virality × fit × freshness × confidence; Czech is fit × freshness × confidence, with virality **omitted, not proxied**. The two numbers are not comparable and the digest says so |
| Demand modifier (applied *after* the composite, in both languages) | ×1.08 → **0.61** | ×1.12 → **0.69** | Applied after the composite, never as a virality input and never inside the product, because the demand index is relative rather than absolute (§2.7) |
| Evidence-quality label | High | **Medium — discourse evidence observed in English; local demand and ad signal only** | The honest Czech label required by §2.7 |
| Fit gate | **pass** | **pass** | Brand-fit floor cleared; veto list clean — no legal or claim risk, no competitor disparagement, no controversy, no manipulation, no injection phrasing |
| Dedupe | first appearance of this cluster key | same | Trajectory *rising*, prior-pack state *never generated* → **normal candidate** under §2.8a's first row; no resurgence judgment is needed and node N-2 is not called. A related cluster from three weeks ago carries a different cluster key and is noted as adjacent-but-distinct |

Rank 1 of five ranked topics. The other four proceed too, at lower media priority — the media-bearing cap applies to masters, not to topics. **Stated plainly because it is the shape of every normal pack: with one to two masters per language and five ranked topics, this run renders media for one topic and ships the other four as copy plus complete plan-only video plans.** That is the designed trade — human video QA at 20–30 minutes per finished video is the binding constraint — and it is what the digest shows rather than what the operator has to infer (§3.2).

### A.4 Spun — pain to offer, and why the offer stays quiet

The **spin mapper** performs a lookup, not an inference (§6.9). Detected pain category: *outbound performance dropping with no visible cause*. Matching ICP segment from the theme's ICP map: **agencies running outbound campaigns for their clients** — one of the configured segments, alongside B2B marketing teams, sales directors and practitioners already using named outbound tooling.

The mapped offer is **HypeLead**. But the offer's record carries a **negative capability statement**: it does not manage mailbox warm-up or domain authentication. Deliverability is therefore the same ICP and the same workflow but a *different problem*, so the mapper sets **mapping distance = adjacent**: the offer may be mentioned once, with a soft CTA, and **no capability elaboration** (§6.9). This is the anti-forced-placement mechanism at the brand layer doing its job on a topic the ranking layer was perfectly happy with — both layers are needed, and here they disagree productively.

**CTA selection differs by language, and the difference is a designed state rather than a defect.** For English, the CTA class is **product-path** pointing at the product page: the offer status is live, the destination URL verified 200 this run, and the band is FULL. For Czech, site verification found the Czech product page returns 404, so the **CTA-language-coherence rule** fires (§6.9): the Czech asset degrades to a **content** CTA pointing at the Czech article instead, and the pack states plainly that the Czech product page does not yet exist. A degraded Czech CTA is normal, expected and visible — not an error.

The **spin rationale** recorded on every asset in this topic pack: topic id, detected pain, segment, mapped offer, mapping distance *adjacent*, CTA class, and the **fact-usage trace** naming exactly which facts and claim-ledger entries this pack consumed — which is what makes the question "we just corrected the trial length, which packs are affected?" answerable six weeks later.

### A.5 The pack, per language, under the identical-mix rule

Both languages get the **same destination × asset-type matrix** (W2.5-4). X is config-gated and off, so no X assets exist this run. Every asset below exists in both Czech and English, written from the language overlay rather than translated.

| Destination | Assets produced (each language) |
|---|---|
| **LinkedIn** | Long post · document carousel, 9 slides · native short video (derivative of the 9:16 master) |
| **Instagram** | Carousel, 9 slides at 4:5 (derived downward from the 9:16 slide art) · Reel (derivative) · caption |
| **TikTok** | Short vertical video (derivative) · caption |
| **YouTube Shorts** | Short video (derivative) · title and description packaging |
| **Facebook** | Community-style post · Reel (derivative) |
| **Blog** | English: full article draft at FULL band. **Czech: held** — long-form requires FULL and the Czech band is PARTIAL, so the Czech article is not written and the pack says why |

**Masters produced: four — two per language**, which is exactly the cap's default ceiling of one to two per language. Per language: **one 9:16 video master** and **one 9:16 slide-art set**. The earlier arithmetic here read "masters produced: two" and then enumerated four items, which was the visible symptom of an unstated scope rule; the rule is now stated at §3.2 — **the cap counts every media-bearing master, not video masters alone**, because a slide-art set is its own generation event with its own spend.

Every vertical destination is served by re-composition from the same 9:16 master inside the ≈900×1400 universal safe box, never by cropping, and the 4:5 carousel is derived **downward** from the 9:16 slide art rather than generated separately (§3.2). This is the resolution that matters for the cap: the **media-bearing cap counts masters, not derivatives**, so an identical mix across five vertical destinations does not multiply spend by five.

**One master in this run does not finish inside the run.** The English 9:16 video master is waiting on its second clip at wind-down, so its assembly-ledger row sits at *blocked-on-inputs* and it is packaged as **a plan-only artifact with its two completed clips attached and a days-to-deletion countdown**, not as a finished master. The Czech master, which buys no clips, assembles fully — its pending item is the voice render, so the Czech Reel exists in its subtitles-plus-music form and the voiced variant arrives with the amendment. A.7's gate table and A.9's review reflect that, because a master cannot be mastered, loudness-gated, disclosure-bearing, derived and reviewed while one of its clips is still generating (§4.7a).

Because the Czech band is PARTIAL, the Czech assets carry additional restrictions automatically: no prices, no trial terms, no proof claims, no comparative claims, and CTAs limited to the zero-commitment and content classes. The English assets, at FULL, may state the trial terms — and the pricing policy says social posts never state prices anyway, so they do not.

### A.6 The video plan and the money

**English recipe: EN-A** — generative clips from approved keyframes, with model-native English speech. **Czech recipe: CS-B** — slide motion over our own typography with Czech text-to-speech, no generative video model anywhere in the loop. One fork, at audio sourcing, and nowhere else (§4.8).

Because this is an unattended run, **spoken lines carry zero claim tokens in both languages** — no numbers, no currency, no entities beyond our own brands, no superlatives, no outcome statements. Every claim-bearing string in the finished videos is burned-in on-screen text composed at assembly time from verified strings (§6.8, §14.5). Speech recognition runs afterwards as a sampled adherence monitor, not as a gate.

Spend, tier by tier, with the registry's 2026-08-06 snapshot:

| Step | Route class | Count | Cost |
|---|---|---|---|
| Hook candidates, script, shot list, slide list | — | — | **$0** — plan-only artifacts are always produced |
| English keyframe variants (draft tier) | everyday image route | 6 | $0.24 |
| One rejected keyframe slot regenerated | everyday image route | 2 | $0.08 |
| **Keyframe acceptance** — the approval event that unlocks clip spend | — | 3 accepted | *the four-cent decision that protects the thirty-cent one* |
| Motion draft, one shot | cheap motion-draft route | 1 | $0.05 |
| English clips from approved keyframes | workhorse video route | 3 × 8 s | $0.90 |
| English slide art, generated at **9:16**; the 4:5 carousel is derived downward by re-composition | everyday image route ×7, layout-optimised route ×2 | 9 | $0.46 |
| Czech slide art — English compositions reused, Czech text applied post-render | everyday image route | 4 new | $0.16 |
| Czech voice-over from the verified script | text-to-speech provider (a priced registry route, §5.2) | 1 | ≈$0.02 |
| **Text-model spend — drafting plus five model-mediated evaluations across ~26 artifacts in this topic pack** | text routes, drafting and judge | — | **read from the registry's text price snapshots; a cents-to-low-single-dollars line, shown separately from media in the digest (§5.4a)** |
| Assembly, captions, mastering, derivatives, disclosure overlay, static-asset composition | local assembly engine | all | **$0 marginal** |
| **Topic-pack media total** | | | **≈$1.91** against a $2.10 media forecast |

Four readings the plan does not soften.

This lands **below** A2's ≈$3.80 two-language standard figure precisely because the Czech lane runs CS-B and buys no clips — and the moment Czech is promoted to generative clips, that advantage disappears (§3.1, §5.4). The reason the total is not much higher is the keyframe-first structure: the one composition that was wrong cost eight cents to fix, not ninety.

**The slide art is bought once, at 9:16.** An earlier version of this table bought a 4:5 set and left the carousel-to-reel recipe's vertical backgrounds unfunded — which would have been roughly $0.36–0.47 per language of unaccounted spend on the recipe the plan calls the Czech workhorse, or a silent crop. Generating vertically and deriving the 4:5 carousel downward is what makes "carousel-to-reel reuses already-generated slide art" true rather than aspirational (§3.2).

**The two premium images are bought for layout, not for type.** The route is on the roster because it composes cleaner negative space for a post-render overlay; it is never asked to render message-bearing text, which is banned in both languages (§4.4). If the Phase-3 bake-off does not show it earning its premium on layout alone, this line disappears along with the route (§5.2).

**The media total is not the pack total.** Text spend is real and is shown as its own line and its own forecast, because the previous table presented a media-only figure as a pack figure — and across a run of five topics and a month of scheduled runs, the text wallet is the same order of magnitude as this one (§5.4, §5.4a).

### A.7 Gates fired

| Gate | What happened |
|---|---|
| **Spin gate** | The English LinkedIn long post failed **S-4 distance compliance** on its first draft — it elaborated the product's capabilities at adjacent distance. **Bounded regenerate citing S-4** → passed on attempt 2 with the offer reduced to a single mention |
| **Claim gate pass 1** | The Czech TikTok caption contained *"zdarma"* — a price claim under check class 2. At PARTIAL band, trial terms may not be stated. Blocked → regenerate with the failing span cited **and a positive constraint** naming what may be said instead → passed |
| **Claim gate pass 1** | The English carousel slide 4 asserted the product "handles deliverability for you" — check class 6, capability/autonomy, checked against the **negative** capability statement. Verdict **CONTRADICTED**, not merely unsupported → blocked, and a brand-truth review flag raised in case the ledger itself is wrong → regenerate → passed |
| **Voice gate** | The Czech Reel script tripped the **calque blocklist** on *"zefektivnit"*; the regenerate instruction carried the named native alternative rather than only "this failed" → passed on attempt 2. Separately, the **cross-pack recurrence check** flagged the English hook as reusing an opener from six days ago — house-style-tic drift — → regenerated |
| **Keyframe acceptance** | Six English keyframe variants; one slot's first variant carried accidental legible pseudo-text in frame — a **binary fail** under rubric item 2, since model-rendered message-bearing text is banned in both languages — and was regenerated within the variant budget. Three keyframes accepted, which is the event that unlocked clip spend (§4.2a). The rubric ran automatically because this is an unattended run; had it been unavailable, the slots would have degraded to plan-only rather than unlocking spend |
| **Claim gate pass 2** — *the bounded regenerate that proves the double pass, **and the re-entry that proves the repair rule*** | The voice gate's rewrite of the English LinkedIn post reintroduced a first-person outcome claim — *"we've watched reply rates halve"* — which pass 1 had never seen because it did not exist then. Check class 4, verdict **UNSUPPORTED** (no ledger entry), blocked. **One bounded regenerate**, fed the failing span and the positive constraint "describe the mechanism, attribute the observation to the source thread". **The repaired text then re-entered the voice gate and the spin artifact-level post-check before pass 2 ran again** — because a claim-2 regenerate is itself a rewriting step, and shipping it unre-gated would have meant packing an asset whose slop control and connection chain were both checked on a superseded draft (§6.10). Voice passed; S-3 held; pass 2 passed on the exact bytes. Three repairs total on this artifact, inside the combined per-artifact repair ceiling. Attempt history is attached to the asset in the pack |
| **Platform gate** | The Czech LinkedIn post came in at 3,050 characters against a 3,000 hard limit — **refused rather than truncated** → shortened and re-checked. The TikTok caption contained an inline link, which is not clickable organically — refused, and the CTA template swapped to a link-in-bio shape. Mapping distance *adjacent* satisfies the short-form minimum, so no soft bridge was required (§6.9) |
| **Cost gate** | Media forecast $2.10 against a $6.00 per-run cap; per-asset, per-day and per-month caps all clear; the global cross-theme caps clear because no other theme was spending. **Text forecast checked separately against the per-run text budget, with per-stage call ceilings and the per-pack judge allowance all inside their limits** (§5.4a). Hero tier not selected — it is never auto-selected in any mode, and its cap is a separate dimension anyway |
| **Asset QA rubric** | English clip 2 showed a limb-warp artifact at 0:05. Not a refusal, so the refusal ladder does not apply; the asset enters the pack **flagged for human decision** rather than being silently retried — and the route back is the human-rejection loop, which has its own **QA-rejection cap of two per asset slot per pack** terminating in "did not clear QA after N attempts" (§4.9) |
| **Post-assembly overlay claim pass** | Deterministic claim classes re-run over the composed on-screen strings of the Czech master, since overlay composition happens after claim pass 2 closes. All strings drawn from pre-verified slots with no cross-slot juxtaposition — passed (§4.4) |
| **Loudness gate** | Czech master: measured −14.2 LUFS integrated, −1.1 dBTP — inside tolerance, logged per asset. **The English video master is not measured this run, because it is not assembled** — its assembly-ledger row is *blocked-on-inputs* pending clip 2 |
| **Disclosure** | Burned-in, human-perceivable AI disclosure applied at render time on **every assembled generated asset in both languages** — including the static assets, on the first and final slide of each carousel — and **measured** against the engine floor: visible from the first second, inside the safe box, type-height ratio and contrast within band (§4.4, §4.4a). **The Czech Reel carries it too, on the strength of its TTS voice alone**: an asset whose only generated component is synthetic speech is realistic-synthetic by engine derivation, and a theme cannot configure that away (§3.3). Provenance manifest signed after final encode and archived. Per-asset **AI-label-required** flag set |
| **Provenance completeness** | Each generated asset's record resolved after completion: delivered route identity **reported** for all four English clips and both image routes, so rights class resolved cleanly. Nothing was substituted this run; had the router substituted silently, the record would read *substituted — identity unknown* against the documented signature and that asset would have degraded to plan-only rather than reaching publish-ready (§5.6, §7.4) |

### A.8 What the run pack contains

The run pack is a set of named artifacts the operator opens directly — no server, no application, no session state (§12.5).

The **run digest** sits at the top: run id, run-date, theme, mode **and the fact that dry-run was off for this run**; a plain-language status line; the **three cost lines — media $2.10 forecast versus $1.91 actual, text-per-artifact forecast versus actual, and the ranking stage's text-per-candidate line (§5.4a) — each with its own price-snapshot date**; the five ranked topics with their scorecards, dedupe status and **one-line spin rationale each**; a per-topic completeness reason where media was not produced (here: *not selected — masters cap*, for four of five topics, which is the designed normal state); the **pending-media line with a days-to-deletion countdown** for the English clip and the Czech voice render; the degraded-source banner naming the absent short-form trend axis; the claim-ledger expiry warning; and a footer pointing at per-topic detail. Beneath it, one **topic pack** per ranked topic.

Inside this topic's pack: every asset above in both languages; the video plan — shot list for English, slide list for Czech — produced regardless of budget; the generated media, re-hosted with checksums, with **no provider URLs anywhere**; **the English video master as a plan-only artifact with its two completed clips attached**, marked waiting-on-inputs; the **spin rationale** and **fact-usage trace**; a reference to the **brand-truth snapshot** by id rather than a re-embedded copy; per-asset claim-check results with verdicts and attempt histories; **per-signal source records in two parts — a permanent de-identified part (canonical key, source, domain, method, retrieval time, metrics) and a 30-day part holding the verbatim excerpt and the direct link**, the second expiring in place to a placeholder (§2.6); a **provenance record** per generated media asset naming the delivered route, its identity-resolution state, the version, the generation timestamp, that route's commercial-use terms as they stood at generation time **plus the upstream provider's terms URL and read date**, the router transaction id, and requested-versus-delivered aspect where they diverge; and the automation metadata — run id, mode, stage durations, candidate counts at each filtering step, and which cadence produced this run. Alongside the digest sits the **decision file** the operator edits, and the **filesystem status flag** that says today's run happened.

The run exits **completed-with-pending-media**: one English clip and the Czech voice render were still processing at wind-down. That is a healthy outcome, not an alarm — provided the pack says so honestly, which is why the English master ships visibly incomplete rather than as a finished asset. The next run's phase 0 adopts both jobs, re-hosts them in expiry order before submitting anything new, unblocks the assembly-ledger row, assembles and masters the English video, and **amends this pack as revision 2** with an amendment record written into the review-decision store against *this* run id — so the review history of one topic never splits across two folders (§4.7a).

### A.9 What the operator does at 08:20

The digest scans in about two minutes. The topic is pre-selected because it sits in the high confidence band; two of the other four topics arrive unselected and one requires opening the detail before approval is possible.

The operator **approves** the English and Czech copy sets, both carousels, the Czech Reel in its subtitles-plus-music form, and the English blog article draft. **The English video master is not in front of them to approve or reject — it is marked waiting-on-inputs with its clips attached and a deletion countdown**, which is the honest state of a master whose second clip is still rendering.

The operator **does reject one asset**: English clip 2, already delivered and QA-flagged, with the reason code *motion integrity: limb warp at 0:05*, **the structured segment field set to shot 2**, and the free-text note *"the hook and the close are fine."* Rejection is granular in two senses that matter: rejecting a clip does not touch the approved copy for the same destinations, and **naming the segment is what makes the repair a clip rather than a re-shoot** — the structured field exists precisely so this is a rule rather than a hopeful reading of free text (§12.4).

The immediate loop regenerates that one clip from the **same already-approved keyframe** with the note fed back as corrective context — one workhorse-route call, $0.30, **counted against the QA-rejection cap of two per asset slot per pack**, and re-checked by the cost gate before submission. Had the operator rejected it twice more, the third rejection would not have bought a fourth generation: the asset would ship labelled *"did not clear QA after 2 attempts"* with every attempt attached, which is the terminal state this loop previously lacked (§4.9). The replacement passes the QA rubric. Topic-pack media total: $2.21.

The operator also **acknowledges the AI-label-required flag** on each affected asset — a separate, separately-recorded action, deliberately not folded into the approve decision, because bundling it is exactly how a busy operator skips it (§7.7). The decision record carries **the approver's identity and the editorial-responsibility holder** alongside the reason code (§11.4).

### A.10 What staging would do later

This run was in test mode, so nothing touched the publishing bridge — in test the publish allowlist is empty by construction and every bridge call is refused before it is attempted. When the operator later moves this theme to staging with the allowlist populated, the same approved pack would flow like this:

The **publish gate** fires **before any distribution preparation**, not before a bridge call — which is what keeps rung 3 inside its scope — and checks five things per asset: mode permits publishing side effects; the destination is in the active mode's allowlist; the destination is actually connected; the review-decision store holds a recorded approval naming the approver and the editorial-responsibility holder; and, for every asset whose AI-content class requires it, the recorded label acknowledgement. **The fifth check is provenance: the record is complete on all four items and the delivered route's rights class is inside the rights-class allowlist for that destination** — an asset whose renderer could not be identified does not reach publish-ready and degrades to plan-only with the reason attached (§7.4, D-20).

LinkedIn, Instagram and Facebook are allowlisted and connected, so **distribution prep creates unscheduled drafts** for them — rung 1. TikTok is in the allowlist but the operator never completed its connection, so the run **fails closed for that destination alone**, names it in the pack, and offers the honest choices: complete the connection and re-run, remove it from the allowlist, or accept the pack without it. No silent skip, no silent substitution. YouTube Shorts is not in this mode's allowlist at all, so its assets are written into the pack for **rung 3 local staging** — fully composed, ready to paste by hand, **and carrying an unticked per-platform label checklist in the same file**, because the path that never calls the bridge is exactly the path where a busy operator would otherwise skip the label (§7.2). The same is true of the TikTok assets the gate just blocked: they land in rung 3 with the checklist unticked, not as clean pasteable text.

Nothing is scheduled and nothing is published. Every platform-native AI label — the short-form platform's disclosure boolean, the video platform's synthetic-media property, the social platform's publish-time toggle, and a per-post disclosure line composed directly into the copy for the professional network, which has no structured control — is set **by the operator, by hand, in each platform's own interface**, because the publishing bridge exposes no such fields. The human then schedules or publishes from inside the bridge. The system's own responsibility ended at the draft.

---

## Appendix B — Review changelog

### B.1 Review passes

| Date | Reviewer | Scope | Counts | Disposition |
|---|---|---|---|---|
| 2026-08-06 | **R1** — architecture | Assignment items 1–18, the ten success criteria, RA-1…RA-8, four assembler-flagged weak spots | 3 blockers · 13 majors · 7 minors | Approve with changes. All blockers and majors accepted at Wave-4 triage and applied |
| 2026-08-06 | **R2** — AI pipeline feasibility | §1, §3–§6, §8, §11, §12, §14, §15, §17, Appendix A against the research pack | 4 blockers · 20 majors · 9 minors | Approve with required changes. All blockers and majors accepted and applied |
| 2026-08-06 | **R3** — marketing / commercial viability | Pipeline-to-publishable, per-language voice bar, platform adaptation, operator walkthrough, north-star fit | 1 blocker · 6 majors · 5 minors | Proceed with mandatory pre-Phase-1 clarifications. All accepted and applied |
| 2026-08-06 | **R4** — legal / GDPR / AI Act / Czech law | §2, §3.2–3.5, §4.3–4.5, §5, §6.3–6.10, §7, §10.4, §11, §12, §14, §15–§17, Appendix A | 5 blockers · 9 majors · 7 minors | Conditionally ready. All blockers and majors accepted and applied |
| 2026-08-06 | **R5** — scenario red-team | Five mandated failure scenarios plus four invented ones, walked end to end | 4 blockers · 13 majors · 6 minors | Four sections named for revision; all accepted and applied |
| 2026-08-06 | **W5 fixer** | Applied the accepted findings as surgical edits; produced this changelog; appended new decisions to `DECISION_LOG.md` and new rows to `RISK_LOG.md`; appended supersession banners to `SYNTHESIS.md` §3.1 and §7 item 8 under the T-4 exception | 17 blockers · 61 majors · 34 minors triaged | See B.2 and B.3 |

**Totals: 17 blockers, 61 majors, 34 minors. Applied: 17 blockers, 61 majors, 22 minors. Logged-not-applied: 12 minors, each with a rationale in B.3. Unresolved: 0.**

*One counting note carried honestly: R2's own header states 19 majors while its section contains 20 headed MAJOR findings. All 20 are treated as accepted and all 20 have rows below.*

### B.2 Finding → section → edit mapping (blockers and majors)

**R1 — architecture**

| ID | Sections touched | Edit applied |
|---|---|---|
| R1-B1 | §1.5, §5.1, §5.2, §5.4, §5.4a (new), §8.11, §10.4, §11.1, §12.1 | Text-model provider role added; registry extended to four route classes; **§5.4a LLM budget block** created (per-run/day/month text budgets, per-stage call ceilings, per-pack judge allowance), enforced pre-call by the cost gate; text line added to unit economics and to the digest forecast; §11.1's row repointed from §8.11 to §5.4a. Merged with R2-B1 per conductor direction T-6 |
| R1-B2 | §15.2, §15.3 | Coverage map's false completeness claim corrected and the four missing rows (W2-08a, W3-01, W3-02, W3-03) added, plus the Wave-4 additions; **new risk row R-35** for W3-01 with an honest detection column that states plainly there is no machine detection for a coherent-but-mistaken theme |
| R1-B3 | Appendix A header, A.1, A.6, §4.6 | Appendix A's header now states dry-run was deliberately switched off and why an operator does that; §4.6 gains the one-sentence rule — a mode never authorises spend, the dry-run flag converts forecast to submission, and its per-mode default is engine-level. Per conductor direction T-5, option (a) |
| R1-M1 | §8.5 | Attempt added to the deterministic asset identity; idempotency stated as per (identity, attempt) with the total attempt count bounded separately by the refusal-ladder and QA-rejection caps |
| R1-M2 | §14.2, §14.0 (new), §10.4, R-10 | Per-pack voice-regenerate allowance added beside the per-artifact cap; the "primary circuit breaker" claim corrected; §14.0 introduces the combined per-artifact repair ceiling with check order and exhaustion outcomes |
| R1-M3 | §11.3, §14.2, §4.2a, §2.8a | Fifth fail-closed trigger added — any gate that cannot execute fails its artifact closed — with per-gate degraded outcomes enumerated for seven gates/nodes |
| R1-M4 | §6.5, §6.6, §10.3, R-15 | Resolved in favour of §6.5 as single owner: an unattended run on a snapshot degrades immediately; the maximum-offline-window knob is re-scoped to interactive runs only; R-15's wording corrected |
| R1-M5 | §4.2a (new), §10.4 | Keyframe-acceptance rubric specified: five checks, two binary in every mode, per-mode thresholds, failure disposition, unavailability disposition, and the masters cap named as the auto-acceptance ceiling. Merged with R2-M1 |
| R1-M6 | §16.2, §17 Phase 0 | Vendors named on first use throughout the decision table and Phase-0 prerequisites (FFmpeg, ElevenLabs, Azure Neural, Virlo.ai, Shortimize, DataForSEO, Kie.ai, fal.ai, Meta Ad Library, Product Hunt, Reddit Pro), role names retained as governing nouns |
| R1-M7 | §4.10 (new), §10.4, §18.2 | Prompt and skill layer added: brand lock contents (visual and verbal halves), five negative-prompt layers with their owning level, all four skill bundles named with their engine/theme/language placement |
| R1-M8 | §10.1, §10.4a (new), §10.5, W3-01 | Knob count corrected to ≈130; §10.4/§10.5 pacing and download-queue contradiction resolved to engine level; four machine-scoped knobs moved into a new **machine/runtime block**; **eleven-decision minimum viable knob set** added |
| R1-M9 | §14.4, §3.1, §15.4 | Czech commitment 2 becomes rubric dimension 1 — hook shape and framing, with the transplanted English hook rhythm as its named fail smell; §15.4's "first five are enforceable" corrected to all six instrumented |
| R1-M10 | §2.7, Appendix A.3 | Both composites stated once and exactly in §2.7, with confidence-and-availability retained for Czech and the demand modifier applied after the composite in both languages; A.3 corrected to match (cs composite 0.62 → 0.69 after the modifier) |
| R1-M11 | §17 Phase 4, §5.4, W3-02 | Phase 4's acceptance criterion re-based on measured-versus-forecast spend and a cap-to-spend ratio; §5.4 states the envelope is ~2× conservative under the default recipe |
| R1-M12 | §0.3, `SYNTHESIS.md` §3.1 and §7 item 8 | Supersession banners appended in place at both SYNTHESIS locations under conductor direction T-4 (append-only exception); §0.3 carries the warning for readers arriving at the evidence base by another route |
| R1-M13 | §11.1, §11.2, §10.4a, §10.5 | Dry-run default moved to engine level and enforced by the resolver, so test mode differs in the resolver's own answer; licensed-vendor credit spend added as its own matrix row; the honest division of labour stated — resolver governs permission and the dry-run boundary, cost gate governs magnitude |

**R2 — AI pipeline feasibility**

| ID | Sections touched | Edit applied |
|---|---|---|
| R2-B1 | *(merged with R1-B1 per T-6)* | See R1-B1. Additionally: §4.1's "text is free" rewritten to "cheap per call, expensive in aggregate", with the design instruction that follows |
| R2-B2 | §4.7, §4.7a (new), §8.5, §8.6, §8.13, §12.2, Appendix A.1/A.5/A.7/A.8/A.9 | Assembly made a resumable unit of work with its own **assembly ledger** (blocked-on-inputs → assembling → assembled → failed); assembly declared non-spend-bearing so any run may complete one; **pack amendment** defined with revision numbering and an amendment record against the originating run id; Appendix A recast so the pending master is visibly incomplete |
| R2-B3 | §6.10, §14.0, §4.4, Appendix A.7, §17 Phase 2 | **Repair re-entry rule**: a claim-2 repair re-enters the voice gate and spin post-check, under one combined per-artifact repair ceiling, exhausting to the downgrade-repair variant; **post-assembly overlay claim pass** plus slot discipline added for media, whose on-screen text is composed after pass 2 closes; A.7 corrected to show the re-gate |
| R2-B4 | §5.6, §7.4, §12.2, §17 Phase 0/3, R-08 | Delivered route identity downgraded from asserted to **best-effort with a three-state inference rule**; publish-gate disposition for unresolvable rights class defined as plan-only; "does the response name the rendering model" added to the Phase-0 router checklist. Wired to R4-B4's publish-gate check |
| R2-M1 | §4.2a, §10.4 | *(see R1-M5)* Keyframe-acceptance rubric specified |
| R2-M2 | §4.4, §5.2, Appendix A.6 | Text-capable image route re-justified on **layout** grounds only and renamed accordingly; the type-rendering rationale withdrawn; roster membership made conditional on the Phase-3 bake-off; A.6 relabelled |
| R2-M3 | §3.2, §4.5, Appendix A.6 | Slide-art aspect policy stated: **generate at 9:16, derive 4:5 downward by re-composition**, which makes the reuse claim true; A.6's slide-art line corrected |
| R2-M4 | §4.5, §4.2, §6.8 | Script declared primary for both recipes and slide copy derived from it; four missing recipe parameters added (slide count, motion-direction consistency, disclosure placement, the narration/subtitles fork as audio-only) |
| R2-M5 | §4.4, §16 OD-13, §17 Phase 0 | Three caption-timing sources named with their availability as a per-route fact; the fallback tier's Czech timestamp support added to the OD-13 trial questions; a Czech forced-alignment model made a conditional Phase-0 deliverable; word-level reveal stated unavailable on the subtitles-only path |
| R2-M6 | §4.4, §4.9, §10.4 | **Local per-asset adherence check** added for model-native-speech recipes, failing closed to the QA-flag path; sampled recognition retained as the provider-level alarm; "100% by construction" restated as being about displayed text only |
| R2-M7 | §5.4, R-11 | The two cost levers separated — keyframe reuse (real, images) versus footage reuse (CS-A only, currently unused) — and the English-footage-reuse policy stated: permitted outside short-form, forbidden for Czech short-form |
| R2-M8 | §5.3 | Four routing contracts declared instead of one: video (the ten axes plus negative-prompt and moderation-strictness), image (variant count, reference inputs, moderation), voice (language, voice basis, timestamps, rate), text (role, token ceilings, structured output, iteration) |
| R2-M9 | §5.2, §10.4, R-30 | Two-stage lapse defined — stale-marked forecasts and a grace period first, degradation second — with unattended runs barred from submitting against stale-priced routes; A2's **weekly availability probe** carried into §5.2 with its own budget line. Per conductor direction T-9 |
| R2-M10 | §5.7, §17 Phase 3, OD-23 | Ladder split into **runtime rungs** and **migration projects** with an explicit lead-time statement and a named plan-only interval; a paper-level conformance check of the four contracts against the fallback router made a Phase-3 deliverable |
| R2-M11 | §8.5, §8.13, R-09 | `submitted-unknown` given two named sub-cases and a terminal disposition: bounded resolution window → **`paid-lost`** → slot degrades to plan-only, named in the digest, one operator-initiated fresh attempt permitted |
| R2-M12 | §5.4, §8.11, §13.1 | **Global cross-theme media-spend lock plus global daily/monthly caps** required, with per-theme router sub-accounts as the alternative and a stated onboarding cost; "separate key with bounded top-up" corrected to "separate account" |
| R2-M13 | §6.6, §1.5, §6.4 | Site verification bounded to liveness, prices, trial terms and offer status; capability and claim-ledger verification moved to a **declared verification page set per fact class**, with not-performed recorded honestly; the comparison registered as node **N-13** with a token ceiling, fail-closed-to-not-observed, and quoted-data injection posture |
| R2-M14 | §6.5 | Step 2 converted from a score to **counting rules over fact classes**, with FULL, PARTIAL, MINIMAL and INSUFFICIENT defined by counts that need no calibration and are auditable in the brand-truth panel |
| R2-M15 | §14.2, §17 Phase 0 | **English golden set and English structural-calibration pass** added to Phase 0 alongside the Czech pair; the do-not-start gate now covers four artefacts; until a golden set exists for a language, its judge runs lenient and its flag-rate ceiling is recorded as inactive |
| R2-M16 | §14.8 (new), §12.4 | **Frozen eval set** created as a named artefact, never read while authoring prompts; a pre-rollout comparison on pass rate, human-agreement rate and token cost made a **precondition** on any prompt or rubric change; blind A/B and standing spot-check added as named deferred-value knobs |
| R2-M17 | §11.3, §8.10, §14.2, §14.3 | *(see R1-M3)* Fifth fail-closed trigger, with the deterministic-half fallback stated explicitly for the claim gate |
| R2-M18 | §5.7, §17 Phase 0 | Person-generation eligibility and any allowlist request made a Phase-0 prerequisite; the **no-eligible-route** case added to the ladder with people-free keyframe composition as the injected default and plan-only as the floor |
| R2-M19 | §14.0, §4.9, §6.7 | Single combined per-artifact repair ceiling defined across spin, voice and claim, with the per-pack allowances as the outer bound, check order stated, and the four counters given distinct names |
| R2-M20 | §1.5, §14.7, §10.4 | **Node inventory table** added: thirteen node classes with owning stage, bounded input, output shape, iteration permission and failure mode; the **polish role deleted** for owning no stage, leaving drafting and judge |

**R3 — marketing**

| ID | Sections touched | Edit applied |
|---|---|---|
| R3-B1 | §2.7, §12.1, §10.2 | **Per-language minimum evidence-and-volume band** added, evaluated every run (not only at theme load), default deliberately loose, breaching it raising a named digest line and escalating on repetition; the Czech curation ritual kept merged with the committed weekly Reddit ritual rather than added as a new obligation. Per conductor direction T-3, option (a) |
| R3-M1 | §3.1 commitment 6, §15.2 R-23, §16 OD-22, §17 Phase 4 | Revisit trigger converted from an intention to a **configured counter** (twenty assets or twelve weeks) raising a digest review line, with a machine-held leading indicator (rejection-reason distribution versus English) and a lagging one; Phase 4 now produces at least five Czech short-form assets so the distribution exists first. What the design honestly cannot do — a statistical engagement test — is stated rather than faked |
| R3-M2 | §6.9, §3.3, §10.4, Appendix A.7 | **Minimum mapping distance per destination** added, short-form defaulting to adjacent-or-closer with far distance requiring a named soft bridge; visible at the platform gate and in Appendix A |
| R3-M3 | §12.1, §8.11, §17 Phase 4 | Digest now distinguishes **budget-capped, count-capped and deliberately held** per topic rather than collapsing them; §8.11's cap-hit illustration rewritten in masters units; Phase 4 requires a deliberate cap-hit test and its recovery |
| R3-M4 | §2.8a (new), §10.2 | Trajectory defined and the full resurgence-versus-suppression rule imported as canonical text, including a **rejected-topic reappearance rule** with a suppression window and a corroboration-growth override; Phase 1 tests all three states. Merged with R5-F10 |
| R3-M5 | §14.4, §17 Phase 0 | The eleven Czech dimensions enumerated as **five inherited + five Czech-specific + one Czech override**, with the Phase-0 rubric explicitly a hypothesis to be settled by golden-set agreement data rather than a law |
| R3-M6 | §13.2, §12.1 | Theme-readiness assertion added: every language has a product-CTA destination resolving **in that language**, or the theme carries a dated **language-completeness declaration** that banners every digest until cleared |

**R4 — legal**

| ID | Sections touched | Edit applied |
|---|---|---|
| R4-B1 | §5.3, §4.8, §4.10, §16 OD-27, R-38 | **v1 ban** taken per conductor direction T-1: no synthetic or synthetically altered human presenter, no cloned voice; *talking human* motion class disabled; no identifiable-person reference inputs; only licensed-catalogue voice routes selectable, `cloned-real-person` a forbidden rights class; `voice-basis` field added to the registry; the deferred consent regime named as a prerequisite if the ban is lifted, with the employee agreement as OD-27 |
| R4-B2 | §3.3, §10.4, §17 Phase 3 | AI-content class made an **engine-level derived field** from the generation record; derivation extended to **synthetic speech and generated music**, which is what the old default omitted and what CS-B relies on; configuration may only tighten; Phase-3 acceptance test for a TTS-only asset. Per conductor direction T-2 |
| R4-B3 | §7.2, §7.4, §17 Phase 6, Appendix A.10 | AI-label acknowledgement moved to **packaging** so it travels with the rung-3 artefact as an unticked per-platform checklist; §7.4's trigger restated as "before any distribution preparation"; Phase-6 acceptance test for a gate-blocked asset reaching rung 3 |
| R4-B4 | §7.4, §11.3, §5.2, §12.2, §17 Phase 3, Appendix A.10 | Provenance completeness and delivered rights class added as the **fifth publish-gate check**; upstream-provider terms URL and read date added to the registry as a second licence field; rights class defaults to the most restrictive value when upstream terms are unverifiable; Phase-3 negative test added |
| R4-B5 | §2.6, §2.6a (new), §8.6, §12.2, §17 Phase 1, R-39 | Provenance snapshot **split** into a permanent de-identified part and a 30-day verbatim/permalink part with an in-pack placeholder on expiry; **run-pack → canonical-key index** added to the ledger set; Phase-1 acceptance extended to deletion inside an archived pack; the "links and excerpts, not payloads" justification deleted and named as the wrong legal test |
| R4-M1 | §2.6, §2.7 | Article 9 special-category filtering added as a design consequence and as a distinct veto class: a pre-collection source/community deny-list plus a post-collection deterministic check over stored excerpts, both failing to **do not store / delete** rather than to "flag" |
| R4-M2 | §3.3, §11.4, §16 OD-24 | §3.3's "satisfied by design" downgraded to a working assessment with a named counsel dependency; **approver identity and `editorial-responsibility-held-by`** added to the review-decision store as the carve-out's second condition |
| R4-M3 | §4.4, §10.4, §17 Phase 3 | **Engine-level disclosure floor** defined and made non-relaxable: visible from the first second, minimum duration, minimum type-height ratio and contrast, inside the safe box, language of the asset, audible equivalent for audio-led assets; measured Phase-3 acceptance test beside the loudness gate |
| R4-M4 | §4.4a (new), §3.5, §12.2 | **Static-asset composition** named as a stage applying the disclosure overlay and signing C2PA after export, including the document-carousel export; disclosure checkpoints added to the carousel, feed-still and blog rows of §3.5; first-and-final-page rule for multi-page assets |
| R4-M5 | §2.4, §16 OD-17a/OD-17b, §17 Phase 0 | OD-17 **split into two decisions** (undisclosed upstream versus known-upstream-in-litigation); the legal reading moved **before the first credit is spent** rather than before renewal; a Phase-0 deliverable requires each vendor's terms retrieved, dated and checked for pipeline/derivative-use permission, recorded in the vendor roster |
| R4-M6 | §6.7 class 10, §3.3, §16 OD-25 | **Commercial-communication recognisability** sub-class added with a statement catalogue indexed by language × destination × relationship type; paid-partnership platform mechanics mapped in §3.3 beside the AI-label mechanics; statute confirmation logged as OD-25 |
| R4-M7 | §2.6, §2.6a (new), §17 Phase 0, §16 OD-26 | **Recipient map** added covering every external provider that can receive collected text, with role, processing agreement and EEA/third-country position; Phase-0 gate upgraded from the notice "existing" to its Article 13 recipient and transfer content; author handles and permalinks redacted from prompt payloads; the area referred to counsel as an evidence gap |
| R4-M8 | §2.3, §17 Phase 0 | Reddit Pro named explicitly as a distinct product from the assessed mitigation; a Phase-0 deliverable requires its terms pulled manually, dated and read on commercial use of derived outputs; §2.3 states no bulk export occurs |
| R4-M9 | §16.2, §17 Phase 0 | **OD-24, OD-25 and OD-26** added with named decision points; OD-26 made a Phase-0 prerequisite because the legitimate-interest assessment rests on the guideline it verifies. Per conductor direction T-8 |

**R5 — scenario red-team**

| ID | Sections touched | Edit applied |
|---|---|---|
| R5-F1 | §6.2, §8.10, R-15 | Brand-truth reader now classifies failures into transient / permanent-auth / permanent-endpoint, retries only the transient class, and records permanent failures verbatim into the brand-truth panel so the "specific fix" is a mechanism |
| R5-F3 | §6.2, §17 Phase 0, R-15 | Notion-token **health check** at run start plus a **token-reissue runbook** in Phase 0, on the same footing as the ad-library token whose blast radius is smaller |
| R5-F5 | §8.5, §8.13 | `submitted-unknown` given two exhaustively named trigger sub-cases (crash-before-task-id; unresolvable resolve-by-query) sharing one terminal handling |
| R5-F6 | §8.13, §5.6, R-09 | *(see R2-M11)* Terminal disposition, bounded window, `paid-lost`, plan-only degrade, one operator-initiated retry |
| R5-F8 | §8.13, §8.6 | Reconciliation arithmetic stated: a `submitted-unknown` row contributes its **full expected cost from the moment the intent row is written**, so a real charge never surprises the circuit breaker; reversal on a confirmed non-charge is a recorded adjustment |
| R5-F10 | §2.8a (new), §1.2, §2.7, §12.1, §17 Phase 1 | B3 §6.2's trajectory × prior-pack-state table imported as canonical plan text; the new-angle judgment named as node **N-2** with its stage, cost and checkpoint; Phase-1 acceptance tests all three states. The mandate's question — can four near-identical packs ship — now has a stated answer |
| R5-F11 | §2.8a, §17 Phase 7 | Prior-pack state **collapsed to what is observable** — never-generated / generated / rejected — because *published* lives inside the publishing bridge and the operator's head, and outcome capture is optional and manual |
| R5-F12 | §2.8a, §1.5, §12.1 | The digest's "what changed since a prior appearance" given a producer (node N-2), a stage (ranking), a cost and a scorecard field |
| R5-F13 | §8.11, §0.2, §3.2, §10.4 | §8.11's mid-pack cap-hit illustration rewritten in **masters and languages**, with the reason the destination-unit version was architecturally impossible stated. Per conductor direction T-7 |
| R5-F14 | §8.11, §5.4, §10.4 | Count-cap versus dollar-cap precedence stated — both checked at every submission, **whichever trips first stops it, both logged distinctly** — with the language-divergence case walked |
| R5-F15 | §8.11, §10.4, §2.8a | **Regenerate-media-only** wired to the mid-pack cap-hit outcome as its designed recovery, referencing the run id and producing a pack amendment; the topic marked *already generated (capped)* so the next run does not re-spin it from zero |
| R5-F16 | §3.2, §10.4, Appendix A.5 | Masters-cap scope stated — **all media-bearing masters, not video alone** — and A.5's arithmetic corrected to four masters (two per language); the stark consequence added, that three or four of five ranked topics receive no rendered media by design |
| R5-F17 | §12.4, §4.2, Appendix A.9 | A **structured segment field** added to the decision file and console command, so "second clip only" routes to a clip regeneration as a rule rather than as an illustration; the whole-master fallback and its cost stated for un-localisable reason codes |
| R5-F18 | §4.9, §12.4, §10.4, Appendix A.9 | **QA-rejection cap** created (default two per asset slot per pack) with a terminal state mirroring the voice gate's — ship the last version labelled "did not clear QA after N attempts" — closing the one gate in the document with no stated ending |
| R5-F20 | §9.1, §4.7 | Lock acquisition and phase 0 added explicitly to the interactive walkthrough; "return to the pack later" stated as an operational constraint with the supported mechanism (exit with pending media, adopt on the next invocation) rather than an implied background process |
| R5-F21 | §2.2, §17 Phase 1 | **Payload fingerprint** per MCP source and ranked collector, flagging identical or near-identical payloads as a distinct *stale payload suspected* degraded reason and suppressing that source's corroboration contribution |
| R5-F23 | §8.10, §8.13, R-40 | Low-disk check made a **running guard** evaluated before each download in the drain; on a mid-drain event the drain **narrows rather than aborts** — new submissions stop first, expiry order is honoured, ledger headroom is reserved — and a genuine stop names the at-risk jobs and their deadlines |

### B.3 Minors — applied, or logged with rationale

| ID | Disposition |
|---|---|
| R1-m1 | **Applied.** §15.4 made a pointer to §3.1 rather than a second copy; "vykání" used consistently, glossed at §10.3 and §14.4 |
| R1-m2 | **Applied.** §14.3's juxtaposition resolved by naming the four counters distinctly in §4.9 and bounding them in §14.0 |
| R1-m3 | **Applied.** OD-10's decision point moved to "before Phase 0", which is where its deliverable is consumed |
| R1-m4 | **Applied.** §5.4 states the trial envelope is ~2× conservative under the default CS-B recipe |
| R1-m5 | **Logged, not applied.** The brand-fit floor's starting direction is a calibration question that Phase 1 data answers; changing the number now would substitute one non-empirical value for another, which is the very thing the standing caution forbids. The asymmetric governance friction the finding names is real and already mitigated (OD-20 requires a logged rationale for loosening); rationale recorded here rather than a number changed |
| R1-m6 | **Applied.** §13.1's "hours, mostly deciding" now rests on the eleven-decision minimum viable knob set rather than on a ≈130-knob surface |
| R1-m7 | **Applied.** Appendix B pre-populated with one row per reviewer plus accepted-versus-applied disposition |
| R2-m1 | **Applied.** Hero promotion given its own cap dimension in §4.6, so it no longer models an impossible configuration against the illustrative per-run cap |
| R2-m2 | **Applied.** §5.4 corrected from "separate router key" to "separate router account", with the balance split noted |
| R2-m3 | **Applied.** Document-carousel export assigned to the assembly engine in §4.4a with the bundled-font requirement carried over |
| R2-m4 | **Applied.** The reference-mode → fixed-duration coupling recorded in §4.3 and as a registry capability constraint, refused at planning time |
| R2-m5 | **Applied.** Days-to-deletion countdown per pending job in the digest and notification; interactive runs perform phase 0 |
| R2-m6 | **Applied.** "Topic pack" used consistently in §17 Phase 4 and §5.4 |
| R2-m7 | **Applied.** §6.6 states that facts are injected as an identifier-tagged set, which the fact-usage trace requires |
| R2-m8 | **Applied.** §4.3 states plainly that no cheap multi-shot preview exists, so the four-cent protection does not apply at hero tier |
| R2-m9 | **Applied.** Cross-pack recurrence window and similarity threshold added to §10.4 |
| R3-m1 | **Logged, not applied.** A draft-to-standard promotion decision matrix with times and costs is operator-workflow guidance rather than architecture, and pinning a review-minutes figure now would set an operator-behaviour threshold from an estimate — the same error the standing caution names. The architectural half is applied: §4.2a defines what the keyframe decision actually checks, which is the substance an operator needs |
| R3-m2 | **Logged, not applied.** A second Appendix A worked example exercising exclude-monotonicity and site-subtracts-capability would be genuinely useful and is a page of new narrative, not a correction; the asymmetries are already stated normatively in §6.4 and are enforced by check class 6 and the union rule. Recorded as a documentation improvement for the next revision |
| R3-m3 | **Applied.** §11.2 now states the resolver's contract in plain language — input, output, reason code, the never-unknown rule and side-effect freedom |
| R3-m4 | **Applied.** A one-line spin-rationale format added to §12.1's digest contents, with the fit-on-one-line requirement stated as its own test |
| R3-m5 | **Applied.** R-23's detection column now carries a leading indicator (rejection-reason distribution versus English) and a lagging one, tied to the OD-22 trigger |
| R4-m1 | **Applied.** §2.6 specifies a keyed, deterministic hash with the key held separately, its deletion documented as a mitigation, and states that hashed records remain personal data |
| R4-m2 | **Applied.** §2.4 requires the Playwright exception to name the operator as approver, rest on dated readings of terms and robots plus evidence of no anti-bot defence, and be recorded as a numbered decision |
| R4-m3 | **Applied.** Accepted Ad Library API terms added to Phase-0 deliverables, dated and stored |
| R4-m4 | **Applied.** The AI Office transparency Code of Practice and the forthcoming standardised icon added to §14.6 and to §0.3 row 18 with a 2026-09-01 recheck |
| R4-m5 | **Applied.** §0.3 row 19 records the evidence gap and the standing rule that no expected postponement may relax the disclosure control before it is in force |
| R4-m6 | **Applied.** §17 Phase 0 specifies the assessment's required shape — per purpose and per source family, with purpose, necessity and balancing tests and the objection route — and gates on that shape rather than on existence |
| R4-m7 | **Applied.** ÚOOÚ named in §2.6, with the notice required to state the contact point, the objection and erasure route and the right to complain |
| R5-F2 | **Applied.** §11.3 states that theme-load secret checks are presence-and-syntax only and that validity is discovered at first use |
| R5-F4 | **Applied.** "No snapshot has ever been written" named as an explicit precondition of INSUFFICIENT, distinct from expiry |
| R5-F7 | **Applied.** §8.13 records that A2's controlled-resubmission recommendation was considered and overridden, and why |
| R5-F9 | **Applied.** Unexplained-spend tolerance given a directional starting value with the standard calibration caveat |
| R5-F19 | **Applied.** Four regeneration budgets given distinct names in §4.9 and declared independent counters under one outer ceiling in §14.0 |
| R5-F22 | **Applied.** A second staleness escalation tier added in §2.2 — the axis label moves from *stale* to *abandoned* after a configurable further-miss count |

### B.4 Unresolved findings

**None.** Every accepted blocker and major has been applied. Two minors (R1-m5, R3-m1) are logged unapplied because applying them would mean setting a threshold from an estimate, which the plan's own standing caution forbids; one minor (R3-m2) is logged as a documentation improvement rather than a correction. No finding required a §16 entry as an unresolvable item.

### B.5 Verdict record

| Date | Reviewer | Verdict | Named sections for revision | Open decisions answered |
|---|---|---|---|---|
| 2026-08-06 | R1 | Approve with changes | §15.3 · §11.1/§8.11 budget · Appendix A mode header · §8.5/§8.7 · §6.5/R-15 · §10.4/§10.5 · §16 option columns · new prompt/skill subsection | — |
| 2026-08-06 | R2 | Approve with required changes | Text-model layer · cross-run completion · repair re-entry and post-assembly claim · provenance observability | — |
| 2026-08-06 | R3 | Proceed with pre-Phase-1 clarifications | §2.7 Czech metering · OD-22 · §6.9 platform-aware distance | OD-22 given a default; remains operator-adjustable |
| 2026-08-06 | R4 | Conditionally ready — resolve B-1…B-5 and M-9 before Stage 5 | §5.3 likeness · §3.3/§10.4 AI-content class · §7.2/§7.4 rung 3 · §7.4/§11.3 provenance · §2.6/§12.2 retention · §16.2 | Likeness resolved as a v1 ban (T-1); OD-24/25/26 opened |
| 2026-08-06 | R5 | Reject four sections for revision — all now revised | §2.7/§2.8 cross-day dedupe · §8.11 cap-hit illustration · §4.2/§14.2/§12.4 QA-rejection path · §8.10/§8.13 disk-versus-drain | — |
| 2026-08-06 | W5 fixer | **All 17 blockers and all 61 majors applied; 22 of 34 minors applied, 12 logged with rationale; 0 unresolved** | See B.2 | New decisions appended to `DECISION_LOG.md`; new risk rows to `RISK_LOG.md` |
