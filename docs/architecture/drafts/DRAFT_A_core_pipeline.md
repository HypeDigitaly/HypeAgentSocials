# DRAFT A — Core pipeline architecture (§1–§6)

*Agent T17 · Wave 3 · design phase · 2026-08-06 · Stage 4 items 1–6*

**What this document is.** The first half of the Stage 4 architecture plan: components and orchestration (§1), the List A research and extraction architecture (§2), the List B content architecture (§3), the viral video pipeline (§4), the media provider architecture (§5), and the brand-truth / spin architecture (§6). A sibling draft covers distribution, scheduling, end-to-end flow, theme config, modes, review packages, and voice/claim enforcement. The assembler merges both.

**How to read it.** Every section is written so a marketing-literate operator can follow the argument, with the engineering precision underneath. Volatile factual claims cite the brief that owns them. Design-phase rules are honoured: no code, no pseudocode, no CLI or config syntax, no schemas, no mandatory folder tree. Diagrams are plain text. Every configuration knob this draft implies is *named in prose* so the §10 author can sweep for it — each section ends with a short knob roster.

**What binds this document.** Every locked decision in `DECISION_LOG.md` (D-01…D-26, the Wave 2.5 operator decisions W2.5-1…8, and the defaults adopted without a gate), every risk in `RISK_LOG.md` (F-1…F-9, RA-1…RA-8, OP-1/OP-2, W2-01…W2-20), and the normative vocabulary fixed in `SYNTHESIS.md` §4. Where the synthesis recommended something the operator overruled, the operator wins and this document re-derives the consequences rather than quietly carrying the old text.

**The one place that re-derivation is large.** W2.5-4 rejected the synthesis's D-02a recommendation and chose **identical asset mixes in both languages**. The synthesis's per-language channel table (its §3.1) — which excluded TikTok from the Czech set — is therefore superseded. Czech gets TikTok, Reels and Shorts in v1. Production *recipes* still differ per language (Czech video is TTS voice-over or carousel-to-reel; model-native Czech speech stays banned per D-14). B4's warning that entertainment-styled short-form reads as cheap to Czech B2B decision-makers does not disappear because the mix changed — it converts from a *mix reduction* into a **design obligation**, and §3 and §4 discharge it explicitly.

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
| **Collection layer** | Performs *collection*: runs each configured source through its declared extraction method via one of exactly three connector classes — collector, MCP source, curated inbox — under per-source budgets and fallback ladders. |
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
| **Publish gate and distribution prep** | The single fail-closed enforcement point reading mode × publish allowlist × approval, followed by draft creation in the publishing bridge and blog preparation. *(Detailed in the sibling draft; named here only so the component map is complete.)* |

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
      collectors | MCP sources | curated inbox|        |
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

- **Cost is computable before the run starts.** Each stage has a fixed or capped number of model calls with per-call ceilings, so a hard upper bound exists in advance. Against a $50 trial budget (D-04, OP-1) and W2-14's finding that one mis-configured run can consume a large share of it, that is not a nicety.
- **Budget enforcement is code, not model discretion.** The cost gate executes at a fixed stage boundary. In an agentic design, a budget check is a tool the model may choose to call, which is not enforcement.
- **Fail-closed points are guaranteed to execute.** Unattended safety (assignment constraint 15) requires that certain checks always run. A fixed graph guarantees it; an emergent one cannot.
- **A 3 a.m. failure has a name.** The artifact left behind is "stopped in *media generation*, after checkpoint N", with one bounded log to read — not an open-ended reasoning transcript.
- **Stages are testable in isolation** as near-pure functions with golden inputs, which is what makes the quality gates trustworthy over time.

Rejected alternatives (C3 §2.1):

1. **A fully agentic loop as the primary orchestrator** — an LLM choosing the next tool call at every step. Rejected: cost is emergent rather than bounded, so nothing structurally prevents token burn before a spend-gated step is ever reached; the same input can produce different call sequences run to run, which destroys testability; and there is no guaranteed halting shape for an unattended run.
2. **A hybrid in which a model-level planner may reorder, skip or add stages** (for example, deciding to skip collection and rank from cache). Rejected: it reintroduces unbounded control flow at coarser granularity. Stage sequencing, checkpointing, spend gating and exit-code determination must remain pipeline code.
3. **Multi-agent debate or critic-actor loops as the default per stage.** Rejected for v1 as a cost multiplier with unproven return at trial-budget scale, and independently discouraged by W2-10 (judge over-strictness cost spiral). Deferred to an explicitly opt-in quality mode with its own budget ceiling once the ledger infrastructure has proven itself.

**Knobs this section contributes to §10.** Per-stage timeout; overall run wall-clock ceiling; the internal-iteration cap for the two nodes that are allowed one; model selection per role (drafting model, judge model, polish model) per language; stage enablement flags for partial runs (research-only, spin-only re-run, regenerate-media-only); log verbosity and log retention; launcher and interpreter path resolution; the run-date timezone from which the pinned logical run-date is derived.

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

The **curated inbox is a first-class source type**, not a paste box (D-09). It carries its own evidence class (human-asserted), its own retention rule, its own staleness flag, and its own honest label in the pack. Two consecutive misses escalate notification prominence rather than repeating an identical low-signal message (W2-01).

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
| **Meta Ad Library** | Competitor ad hooks, offers and creative patterns aimed at EU and Czech users — AC | P0 | Collector (auth-integration) after verification; curated inbox before | Weekly | Official API through the operator's verified identity; public UI browsing by a human for creative inspection | **60-day token expiry silently breaking scheduled runs** (W2-15) — needs a token-expiry alarm with fail-closed behaviour and a named runbook item; personal government-ID verification gates the whole source and belongs in week-1 onboarding |
| **LinkedIn Ad Library** | B2B ad hooks and offers, with EU targeting parameters and impression ranges — AC | P1 | Curated inbox | Biweekly | Public, no login; human sweep of competitor names and category keywords | No engagement metrics and no API; systematic browse is a human activity, permanently |
| **Google Trends** | Search-demand validation — the hype-versus-demand arbiter, and one of only four global carriers of direct Czech signal — SD | P0 manual / P1 automated | Curated inbox (CSV) + MCP source (demand-data vendor) | Weekly | Manual UI export as the *designed* degraded state; a demand-data vendor over MCP as the automated path (adopted at W2.5-3 as an explicitly logged vendor-risk decision) | The index is *relative, not absolute*, which misleads naive scoring — hence its role as a **demand modifier applied after ranking**, never a virality input; at weekly cadence it cannot participate in daily scoring at all |
| **Trend-intelligence vendor** | The short-form trend axis: TikTok, Reels and Shorts outliers, sounds and keyword-defined niche monitors — FT | P1, **trial-gated** | MCP source | Daily refresh, polled per run | Licensed vendor over MCP with bearer auth (W2.5-3) | **Adoption rests on an unresolved vendor-internal contradiction** about whether full API access is included at the purchased tier (W2-17) — the trial must answer it; async job semantics (auto-poll then a job id) and unpublished rate limits must be measured, not assumed; no evidence of Czech or regional filtering, so assume global-English |
| **Reddit** | Best-in-class ICP pain — IP, VD | P1, **human-gated** | Curated inbox | Weekly, ~30–60 min operator session | Reddit's own free business tool plus manual thread curation; **no API, no scraping, ever** (D-09, W2.5-2) | The ritual is skipped and the loss is invisible (W2-01) — mitigated by a per-source staleness flag, a digest banner naming the axis as degraded, packs labelled "pain axis: operator-fed", and escalation after two consecutive misses |
| **TikTok Creative Center** | Short-form format and hook inspiration only — FT | P1, narrowed | Curated inbox | Monthly | Human browse; as of July 2026 the trends analytics modules sit behind a business login and only the top-ads gallery is browsable logged out (per B5 fact ledger) | Scope changes without notice; a login wall puts it permanently beyond any automated fetcher under this project's own rules |
| **LinkedIn organic** | B2B framing and the operator's own Czech network as a signal — VD | P2, human only, **permanently** | Curated inbox | Weekly glance | Operator's own browsing plus own page analytics | Holding a company page means scraping would be *the operator's own* contractual breach, endangering an asset that is also a publish destination (B1 §3.4) |
| **Free alert services** | Keyword alerts in both languages feeding the same ingest inbox as newsletters | P2 | Collector | Daily | Email, plus feed where still offered (one provider's feed delivery is no longer documented — verify at setup, OD-18) | Noise; duplicate coverage of the editorial-relay family |
| **GitHub trending, podcasts, review sites, Instagram, Threads, Discord/Slack** | Long-tail — LH, IP | P2 | Mixed (collector, curated inbox) | Weekly to quarterly | Public pages, open feeds, official APIs where they exist; community platforms are human-only because they are login-walled | Each is a nice-to-have; none is load-bearing. The Instagram official door can *validate* hashtags you already chose but can never *discover* what is trending (B5), so it is a v2 probe |
| **Czech-native venues** | Local discourse and localisation grounding | P1 for the Czech output set | Collector (feeds) + curated inbox | Daily to weekly | Public feeds from the Czech tech press; Czech communities and meetups are human-only | Article feeds with no engagement APIs — Czech-by-construction language tagging, but no counted evidence anywhere (the direct cause of the Czech ranking re-derivation in §2.7) |
| **X (Twitter)** | — | **Absent from v1** | — | — | Skipped for reads (D-08, reaffirmed W2.5-1) | The loss is earliest-hours virality, X-native format inspiration, and a slice of AI-sales practitioner discourse. At a human-gated daily-to-weekly cadence a 6–24 hour relay delay through the editorial-relay family is immaterial (B1 §3.2). Reopening is a budget decision with a measurable v2 trigger, not a compliance one |

Four global sources carry direct Czech-market signal — the demand axis at Czech geography, both ad libraries, and Czech-locale news feeds — and everything else discovers in English and is localised through Czech-native venues (B1 §4). This asymmetry is the root cause of the Czech ranking treatment in §2.7 and is not a defect to be engineered around.

### 2.4 Method policy: API, feed, licensed vendor, operator input — and where Playwright is not

The method vocabulary is fixed at seven values (B2 §2.2): official API · feed · licensed vendor · auth-integration · MCP wrapper · operator input · skip. Two rules govern it.

**Rule one — the transport does not launder the method.** An MCP wrapper is acceptable only when it fronts a legitimate method. A server that internally scrapes a closed surface inherits the full contractual and technical problem of scraping that surface. What makes the two licensed vendors in this portfolio acceptable is not that they speak MCP; it is that they sell *derived analytics under terms that permit pipeline use*, which is a materially different posture from raw scraped passthrough (B5 §3.5, carried as OD-17 for a paragraph of legal reading rather than a shrug).

**Rule two — Playwright is in the stack and nowhere in the v1 collection path** (D-12, per B2 §2.1–2.4 and C7 §2.3). The assignment budgets a full guardrail treatment for browser automation; the honest answer after research is that browser automation is justified essentially nowhere here, because every major surface is either officially open (use the API), officially closed and technically defended (do not touch it), or reachable by plain feed where a browser adds nothing. Playwright therefore remains for exactly three purposes, none of which is collection:

1. A **per-source, explicitly-approved future exception mechanism** for a genuinely open site with no feed and no anti-bot defence, entering through the method-evaluation gate rather than by default.
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
| **Provenance snapshot** | Always, permanent with the pack | Canonical link, the minimal quoted excerpt that triggered candidacy, retrieval time, method | Retained with the run pack — it carries links and excerpts, not payloads, precisely so pack retention does not fight source-data retention |
| **Curated-inbox verbatim text** | Yes | The operator's notes and quoted threads | 30 days, with hashed author keys (OD-15 recommendation) |
| **Full article bodies, media files** | **No** | — | Links and excerpts only — copyright posture of the press, and platform material stays on-platform by reference |

**The GDPR consequence is structural, not a footnote** (W2-06, per C7 §2.6). Public social content is personal data even when public: a persistent username plus post history generally identifies a natural person, and pseudonymous data remains personal data. The applicable lawful basis is legitimate interest, which requires a documented case-by-case assessment — blanket assessments are explicitly insufficient under the 2026 guidance C7 cites — plus a published privacy notice. Those are **company artefacts the architecture assumes exist and references; the software cannot generate them.** The Czech supervisory authority's own guidance is quoted by C7 to the effect that public availability of data does not permit unlimited further processing.

Four design consequences follow, and each is cheap now and painful to retrofit:

- **Extract-first storage.** The durable record is the derived signal (topic label, source, timestamp, metrics), not the verbatim text plus username.
- **Bounded retention with an actual expiry job**, not a policy sentence.
- **Author handles minimised, hashed where needed for dedupe or anomaly detection, never retained in clear text long-term.** Manipulation detection therefore operates on hashed author keys.
- **Targeted deletion by canonical key from day one**, so an objection or erasure request is executable — which argues against monolithic raw dumps and for structured, queryable extract records.

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
2. **A binary veto list sitting outside any average**: legal and claim-risk topics, competitor disparagement, high-severity controversy, detected manipulation, and **prompt-injection phrasing**. These are absolute stop conditions checked before scoring, so no virality number can outweigh them.

Seven negative brand-fit criteria are enumerated with a rules-first, LLM-second split (B3 §3): category mismatch, competitor saturation, tone and controversy risk, the "brand looks desperate" pattern, legal and claim risk, off-ICP audience mismatch, and stale consensus. Cheap deterministic rules run on every raw signal before any model cost is spent; model judgment runs only on survivors.

**The brand-fit judgment must produce a falsifiable verdict.** It is required to state the honest connection in one sentence or explicitly say it cannot — and if it cannot, the candidate fails regardless of every other dimension. Making the *attempt to connect honestly* the test itself is stronger than a separate "does this feel forced" checker that could disagree with the writer. **If the judgment step cannot run at all** — timeout, outage, budget cap hit mid-pass — the candidate fails closed to monitor-only. It never defaults open.

**Czech is ranked by a different formula, deliberately.** None of the four global carriers of Czech signal exposes per-item engagement, and the Czech-native venues are article feeds without engagement APIs. A Czech candidate can therefore essentially never earn a measured virality band. Keeping virality as a multiplicative factor would drive every Czech candidate toward zero and **the Czech output set would die quietly by arithmetic — a silent violation of D-02 that would look like a scoring detail rather than a policy failure** (W2-07). The Czech composite is therefore **brand fit × freshness × demand modifier**, with virality *omitted rather than proxied*, and every Czech candidate carries the honest label that its discourse evidence was observed in English with local demand and ad signal only. Theme-readiness validation additionally asserts that each configured language produces a non-empty candidate set, so a systematic Czech famine surfaces as a validation failure rather than as an empty section of a digest.

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

**Prompt injection is handled as a first-class hazard, not a curiosity** (W2-19). All collected text will later sit inside ranking, spin and copy prompts. It is carried as quoted data with provenance tags and never as instructions; the instruction layer stays structurally separate and privileged; and injection-style phrasing in a source item is itself a veto signal rather than something to pass through.

**Knobs this section contributes to §10.** Watch topics, entities and excludes; the source roster with per-source priority, extraction method, cadence, evidence class and per-run budget; source-family membership; ladder-rung configuration per source; per-source circuit-breaker thresholds and the source-health flag escalation counts; the global collection wall-clock ceiling; conditional-request and cache TTL per signal class; dedupe lookback window and per-source overrides; freshness half-life per signal class; the brand-fit floor; the veto list contents; corroboration bonus magnitude; top-N cap per language; the monitor-only band boundary; the absolute-band fallback thresholds used before a baseline exists; retention windows for request log, raw payloads, normalised records and curated-inbox verbatim text; author-handle handling policy; MCP-source credit budget per month with a pacing rule; vendor roster with last-verified and recheck-by dates; curated-inbox staleness threshold and escalation count; ranking-config version; the demand-modifier weight.

---

## §3. List B — content architecture

### 3.1 The identical-mix rule and what it actually obliges

W2.5-4 is unambiguous: **both configured languages get the same destination × asset-type matrix.** Czech gets TikTok, Instagram Reels and YouTube Shorts in v1. D-02a — the synthesis's recommendation of per-language-appropriate mixes — is rejected and superseded. D-02 stays literal.

What survives from the research that recommended otherwise is the *evidence*, and it now binds differently. B4 found that entertainment-styled short-form carries perception risk with Czech B2B decision-makers, that no Czech B2B lead-generation player has built a credible short-form presence, and that Czech professionals flag AI-generated content immediately with measurable trust damage (per B4's fact ledger, with the vendor-blog statistics in that ledger explicitly barred from setting thresholds). The operator has decided to publish there anyway. The architecture's obligation is therefore not to argue but to **make Czech short-form not look cheap**, and to make that obligation checkable rather than aspirational.

Six concrete design commitments discharge it. They are referenced from §4, where the production recipes live.

1. **Recipe, not translation.** The Czech short-form default is the carousel-to-reel recipe (CS-B): our own slide typography with Ken Burns motion, Czech text-to-speech or subtitles plus a music bed, and **no generative video model in the loop at all**. Every pixel of text is ours, so diacritics are perfect by construction and the F-7 rendering risk disappears (A4 §2.2, §2.6).
2. **Framing, not mimicry.** Czech short-form is education-first with a problem-to-solution rhythm, not an entertainment hook transplanted from English. The hook is a direct statement of a problem or a specific observation — the Czech judge rubric's pass bar (D-26) — never a scene-setting throat-clear and never an English hook rhythm in Czech words.
3. **Register discipline.** Vykání by default in every public post and first-contact call to action, consistently within an asset; tykání only where the theme config declares a peer-community context (D-26 resolves B4's internal conflict this way).
4. **Understatement as a quality bar.** The Czech judge weights the human-voice dimension higher than the English judge. This asymmetry is empirical, not stylistic: B4's evidence is that Czech professionals detect and distrust AI-generated copy, so the cost of a slip is higher in that market.
5. **A destination-aware production floor.** A Czech asset bound for a short-form destination must clear the same assembly QA gates as the English one — loudness targets, safe-box composition, caption legibility, no model-rendered message-bearing text — *and* the Czech-specific ones: TTS prosody acceptance, glyph coverage verified for the bundled font, and no English audio anywhere (A1's suggested fallback of English audio with Czech subtitles is rejected as a direct D-02/F-7 violation).
6. **A measurable revisit trigger, logged rather than assumed.** Because the operator overruled a research recommendation, the architecture records the disagreement and names what would settle it: after a defined number of weeks of real Czech short-form publishing, the review-decision store's reason-coded rejections and the operator's own read of engagement quality are the evidence for keeping, narrowing or expanding the Czech short-form set. This is a governance artefact, not an automatic behaviour.

**Cost consequence, stated honestly.** W2.5-4 accepted doubled media spend and OP-1 stands. The doubling A2 priced assumed both languages buying generative clips. Under the identical-mix rule with per-language recipes, the Czech lane buys slide art and voice rather than clips, so the *actual* pack cost lands below A2's $3.80 two-language standard figure when Czech runs CS-B, and at or near it when the operator promotes Czech to the generative-clip-plus-TTS recipe. The architecture does not hard-code either number: the forecast the operator sees before spend is computed from the model registry's price snapshots with the snapshot date displayed (§5.5). This is flagged for the assembler as a place where the synthesis's "the Czech mix is cheaper, which softens OP-1" sentence is now only conditionally true.

### 3.2 The destination × asset-type matrix

Identical in both languages. "Config-gated" means the destination exists in the engine and is switched on per theme; a destination being switched on never implies it is in the publish allowlist, which is a separate, mode-scoped list read by the single publish gate (D-23).

| Destination | Asset types produced | v1 default | Language behaviour |
|---|---|---|---|
| **LinkedIn** | Long post; document carousel; native short video | On | Identical set per language; Czech copy from the Czech language overlay, never translated |
| **Instagram** | Carousel; Reel; caption | On | Identical set per language |
| **TikTok** | Short vertical video; photo slideshow; caption | On (**Czech included per W2.5-4**) | Identical set per language; Czech uses the CS-B recipe by default |
| **YouTube Shorts** | Short vertical video; title and description packaging | On | Identical set per language |
| **Facebook** | Community-style post; Reel (all Facebook video publishes as Reels since mid-2025, per C2 fact ledger) | On | Identical set per language |
| **X** | Single post; thread | **Config-gated, default off in v1** | Assets can be *produced* at no marginal cost; X is a publish-side decision entirely independent of the closed read path (F-2), and until it is taken X is never a connected channel |
| **Blog / site article** | Long-form article with hero and supporting visuals | Config-gated; **drafts only in v1** (OD-14 recommendation) | Per language, per domain; the site-first hold rule in §6 governs whether social atomisations may exist before the article does |

**Two visual master formats cover nearly all of it** (C2 §2.2): 1080×1350 in 4:5 for feed stills and carousels, and 1080×1920 in 9:16 for all vertical video, plus a 16:9 still format if and when X is enabled. Producing those two masters and deriving the rest by layered re-composition — not by cropping — is the whole visual production strategy.

**Media-bearing assets are counted as masters, not as destination derivatives.** This resolves an ambiguity the synthesis left open: OD-8's recommendation of one to two media-bearing assets per language per run was written when the Czech set had fewer video destinations. Under the identical-mix rule, a single 9:16 master per language legitimately serves TikTok, Reels and Shorts through re-composition, so the cap counts *masters produced*, and the derivative count is unbounded because a derivative costs a re-render, not a generation. Video review remains the throughput bottleneck at 20–30 minutes of human QA per finished video (A1), and it is the master that gets reviewed.

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
| **Blog** | No hard limits; quality constraints only | Hero plus supporting diagrams | Native | — | No search-engine disclosure requirement; the text limb of the transparency obligation has a human-editorial-review carve-out our workflow satisfies by design |

**Czech text counts one-for-one everywhere** (C2 §2.1). All List B platforms count Unicode code points after normalisation, not bytes, and Czech diacritic letters are single code points in the normalised form — including on X, whose weighted table places them at weight 1. So the length validator normalises first, counts code points, and applies weighting plus the fixed URL cost only where the platform demands it. This removes what would otherwise have been a persistent Czech-specific truncation defect.

**One internal per-asset AI-content class drives every disclosure obligation** (C2 §2.3, U5). A single field — none, assisted, or realistic-synthetic — feeds the platform-native flag, the burned-in visible disclosure, and the provenance handling, instead of per-platform ad-hoc logic. This is cumulative with, not a substitute for, the render-time burned-in disclosure that D-19 makes the load-bearing control. And because the publishing bridge exposes no per-platform AI-label fields (W2-05), the platform-native layer is a **manual human action in v1**, carried as a per-asset "AI label required" flag, a pack checklist item, and a publish-gate refusal to mark ready without explicit acknowledgement.

### 3.4 Per-language variant rules

**Czech is a first-class output set, never a translation pass** (D-02, F-7). Three architectural consequences run through every layer:

- **Facts are language-scoped.** Offer descriptions, capability statements, CTA phrasing and approved claim texts exist per language. A claim approved in English is *not* automatically approved in Czech, because translation changes claim strength — an English "helps you book more meetings" can land in Czech much closer to a guarantee (C6 §10).
- **Confidence is per (theme, language).** The English pack can proceed at full confidence while the Czech pack sits lower or is blocked, and that is normal rather than an error state (§6.5).
- **Voice is per language with its own overlay.** The language overlay is a *third* axis alongside engine and theme, so every future Czech-writing theme shares one Czech slop lexicon, one register norm set, one CTA phrase bank and one set of on-screen-text conventions rather than re-deriving them (A3 §2.3, D-26).

The Czech rubric is concrete, not a framework (D-26): a calque blocklist with named native alternatives, structural AI tells including the direct Czech analogue of "in today's fast-paced world", a **code-switching allowlist** that permits English tool, metric and category nouns as normal Czech tech register while blocking English-rooted verbs and abstract benefit nouns, an eleven-dimension judge rubric with vykání as the default register, and a Czech soft-CTA phrase bank mapped to CTA classes. That allowlist is the single rule that prevents both failure directions: missing real Czech slop, and false-flagging normal Czech technical speech.

Two things the Czech path needs before its first production run, named here as prerequisites rather than assumed: **a Czech structural-calibration corpus** (the sentence-length-variance band does not transfer from English because Czech sentences run longer by default) and **a Czech golden set for judge calibration**, whose negatives are best seeded from machine-translated English marketing copy — translationese being precisely the failure mode the rubric exists to catch.

### 3.5 Human review per asset type

Review effort is not uniform, and pretending it is produces a queue nobody drains. The mapping below is the design input for the review package; the sibling draft owns the digest's presentation.

| Asset type | Review depth | What the human is actually deciding | Typical time |
|---|---|---|---|
| **Short post** (LinkedIn, Facebook, X) | Read-through | Voice, spin honesty, CTA correctness | ~1–2 minutes |
| **Caption** (Instagram, TikTok, Shorts) | Read-through plus link-shape check | Same, plus that a non-clickable-link platform got a link-in-bio-shaped CTA | ~1 minute |
| **Carousel / document carousel** | Slide-by-slide skim | On-image text legibility, claim safety on every slide (an on-image number escapes text-only reading), narrative arc | ~3–5 minutes |
| **Short video / Reel / Short / slideshow** | **Full playthrough, and this is the bottleneck** | Motion integrity, hook in the first three seconds, caption legibility at mobile scale, audio prosody and timing, claim verifiability, clean loop or ending, burned-in disclosure present | **20–30 minutes per finished video** (A1) |
| **Blog article** | Full read | Long-form carries more claims per asset and therefore requires the top confidence band; structure, E-E-A-T signals, internal linking | ~15–25 minutes |
| **Whole pack** | Digest scan | Which topics to keep, which to drop, and whether the run's cost forecast is acceptable | ~2 minutes to scan, target five topics reviewed in under thirty minutes |

Rejection is granular and reason-coded at every level — reject the video and keep the copy, reject one topic and keep the rest, reject the pack with global feedback — because reason codes are also what makes ranking calibration trustworthy later, and because "the topic was wrong" must never be conflated with "I had enough content this week".

**Knobs this section contributes to §10.** The per-language destination × asset-type matrix; per-destination character, aspect, duration, slide-count and hashtag profiles; link policy per destination including the link-in-comment style choice; CTA placement convention per destination; the per-asset AI-content class defaults and the AI-label-required flag; blog enablement and per-language, per-domain article routing; X destination enablement; slides-per-carousel and pages-per-document-carousel caps; per-language volume targets; masters-per-language-per-run cap; review-depth profile per asset type; the Czech short-form production floor checklist; the language overlay pointer per language.

---

## §4. Viral video pipeline

### 4.1 What the pipeline is optimising for

Short-form video is the competitive minimum for B2B in 2026, not an experiment — but roughly a third of first-pass AI video output still shows obvious flaws, and the operator QA gate cannot be removed (A1, whose volume benchmarks come from vendor blogs and are therefore used directionally and never to set a threshold, per the standing caution in `SYNTHESIS.md` §6). The pipeline is therefore designed around three economic truths:

1. **Text is free, images are cheap, clips are not.** Overgenerate three to five hook candidates with a selection rubric; overgenerate two or three keyframe variants; **never overgenerate clips** (A3 R6 reconciled against A2's prices).
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
            |                      (text is free)
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

### 4.3 Keyframe-first, and what happens when a route is multi-shot

**Image-to-video from an approved keyframe is the default reel workflow** (A2 §2.5). It decouples the expensive spend from the brand-correctness decision, and it lets one approved composition serve both languages because the text is overlaid afterwards rather than baked in.

The shot list's anatomy changes accordingly (A3 R1): each row carries a **keyframe-reference slot** naming which approved still it animates, and the textual continuity anchor is demoted from primary control to a consistency *check*. This materially reduces the character-drift and colour-drift failures that A1 and A3 both identify as the most common multi-shot defect — the anchor is carried visually rather than by repeating a description and hoping.

The other generation modes map onto named slots rather than being ad-hoc: **first-and-last-frame** is the mechanism behind a match cut or a seamless loop; **reference-to-video** holds a product consistent across clips; plain text-to-video is permitted **at draft tier only**.

**Multi-shot-native generation is a hero-tier experiment, never the scheduled default** (A3 R2 and R8, resolving a genuine A1-versus-A2 conflict in A2's favour because A2 owns provider facts). In v1 exactly one registered route is multi-shot-capable, and it activates only on an explicit human promotion to hero tier. When it does, the shot-list skill switches output shape from N independent prompts to a single sequence brief, and the self-check moves from prompt time to review time — because the model, not the prompt author, is now holding continuity.

### 4.4 Assembly — where quality is actually won

Assembly is a **named pipeline stage owned locally** (D-24), with a local FFmpeg-core engine as the engine of record and a cloud assembly API behind an adapter seam as an optional substitute or contingency. The reasoning is not ideological: zero marginal cost per asset matches "runs every night", determinism matches fail-closed requirements, exit-code behaviour is identical on both target platforms, and no third-party outage sits on the nightly critical path (A4 §2.8). The one real cost is obtaining an FFmpeg binary, and the recommendation at OD-10 is a managed install of a pinned version per operating system with fonts bundled and codecs not — because *invoking* the binary as a separate process is low-risk while *distributing* it triggers obligations a solo operator does not need.

What assembly owns:

- **Captions come from the authored script, verbatim.** Speech recognition or forced alignment supplies **timing only**. This makes displayed-text accuracy 100% by construction in both languages and reduces the Czech accuracy gap — measured at roughly two to three times the English word error rate (per A4's fact ledger) — from a *content* problem to a *timing* problem. On the Czech path, text-to-speech-native timestamps remove speech recognition from the caption path entirely.
- **All message-bearing on-screen text, in both languages, is applied post-render** with bundled brand fonts verified for complete Czech glyph coverage. Generative models are never asked to render message-bearing copy; in-model text is permitted only as incidental English set dressing carrying no message. Word-by-word karaoke reveal requires the styled subtitle path burned through the appropriate renderer — plain subtitle formats cannot animate words.
- **Audio mastering to −14 LUFS integrated with a −1.0 dBTP ceiling**, two-pass, with sidechain ducking of music under voice. The measured values are **logged per asset as a QA gate** and out-of-range assets fail closed. Mastering hot now backfires because all three short-form platforms turn loud masters down more than the loudness gap (A4 §2.4).
- **Music must be licensed** — a library subscription or a paid-plan AI music generator. Platform trending audio is prohibited for the master asset because it is either unlicensed for brand use or licensed only inside one platform, which is useless for a multi-platform master. Music routed through the media router's unofficial music route is forbidden for published assets (D-13).
- **One 1080×1920 master composed inside the ≈900×1400 universal safe box**, with derivatives produced by re-running the template at the target ratio — layered re-composition, not cropping. That single safe box lets one master serve TikTok, Reels and Shorts unchanged, which is exactly what the identical-mix rule needs.
- **A layered call to action**: a soft mid-video cue around seconds 10–20 plus a final 1.5–2.0 second dual-delivery close, spoken and on-screen — because end-card-only CTAs underperform through pre-end drop-off. A loop-friendly no-outro recipe is equally supported.
- **The burned-in, human-perceivable AI disclosure, applied at render time.** This is the load-bearing compliance control (D-19), not a courtesy: the transparency obligation has been binding since 2026-08-02 with no size exemption, and metadata-only compliance provably fails because platforms strip provenance manifests on re-encode. **An asset without the burned-in disclosure cannot be marked publish-ready.** The C2PA manifest is signed *after* the final encode and archived with the pack, and is never relied on as the compliance mechanism.

### 4.5 Carousel-to-reel as a first-class recipe

The transform is mechanical and deterministic: roughly 2.5–4 seconds per slide with the hook slide held slightly longer, which puts 7–13 slides — a typical carousel — squarely in the 20–40 second target; slow Ken Burns motion so the frame is never static; one transition style per template to avoid a slop look; and either a narration track from the slide copy or a subtitles-plus-music variant that is itself a platform-native format (A4 §2.2).

It is a first-class recipe in the engine, not a fallback, for four reasons: it is **the safest Czech video format available** (our own typography, proper Czech text-to-speech or none, no generative video model in the loop, so neither the spoken-claim risk nor the diacritic risk applies); it is **the cheapest reel per asset** because it reuses already-generated slide art; it is **the Czech workhorse under the identical-mix rule**, which is what makes Czech short-form affordable at English volume; and it is **a legitimate English variant too**, particularly for education-first content where a generative clip adds cost without adding meaning.

### 4.6 The spend boundary

Four tiers, and money only moves up a tier through an approval event (A2 §2.10):

| Tier | What it buys | Role |
|---|---|---|
| **Plan-only ($0)** | Prompts, scripts, shot lists, slide lists, keyframe specifications | **Always produced**, even with no keys and no budget. The scheduled-run floor, and a complete useful run in its own right |
| **Draft** | Cheap keyframes; a low-cost motion preview route | Composition and motion validation, plus refusal-surface discovery, at pocket-change cost |
| **Standard** | The workhorse video route from approved keyframes; everyday image route with the text-capable image route for slides carrying type | The default production tier for scheduled runs |
| **Hero** | The quality video route, or the multi-shot route as an experiment | **Never auto-selected by an unattended run.** Requires explicit human promotion, with a per-run hero cap |

**The cost gate runs before submission, never after.** It reads expected cost from the model registry's price snapshots and checks it against per-asset, per-run, per-day and per-month caps. A check after submission is too late — the money is already committed. The forecast the operator sees in the digest is computed the same way, with the price-snapshot date displayed beside it, because provider prices moved twice during 2026 (A2) and a hard-coded forecast rots silently.

**The dry-run boundary** is precise: a dry run produces every plan-only artifact, resolves routes against the registry, computes and displays the full cost forecast, and **submits nothing**. Dry-run is a flag on media generation, not a mode — the modes are test, staging and live-prep, and confusing the two is how a "safe" run spends money.

### 4.7 The asynchronous job model and its consequences

Renders take minutes, higher resolutions add more, and tasks can hang (A2 §2.6). Four consequences shape the pipeline rather than being handled as exceptions:

1. **A run may legitimately end with jobs still pending**, and that is a healthy outcome with its own exit-code class — *completed-with-pending-media*. It must not page a monitor nightly.
2. **The first phase of every run adopts pending tasks and drains the download queue, ordered by nearest expiry, before submitting anything new.** Provider media is deleted at 14 days and result URLs expire sooner, so **immediate re-hosting is mandatory** and provider URLs are never the artifact of record. A pack holding provider URLs silently rots before a human reviews it.
3. **Polling is the baseline, not callbacks.** A scheduled console process has no stable public endpoint; a callback receiver is an optional later optimisation.
4. **Submission paces itself well under the published rate ceiling**, because one two-language pack can submit roughly twenty jobs and trip the limit in a single burst.

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

**Banned in v1**, in any route: model-native Czech speech; model-rendered message-bearing text in either language; model-rendered Czech text of any kind.

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

**Knobs this section contributes to §10.** Recipe per language; audio policy per language; text-to-speech provider and voice identity per language; caption style and whether word-level reveal is used; music source and bed selection per theme; loudness targets and the QA tolerance band; safe-box dimensions; end-card recipe including the loop-friendly variant; shot count and clip length per asset type; hook overgeneration count; keyframe variant count; keyframe-acceptance policy (human versus rubric-automatic) per mode; masters per language per run; the asset QA rubric thresholds; disclosure overlay text and placement per language; slide timing range for carousel-to-reel; per-destination derivative set.

---

## §5. Media provider architecture

### 5.1 Roles, and why they are roles rather than vendor names

| Role | Filled in v1 by | Status |
|---|---|---|
| **Media router** | Kie.ai | Primary route host, treated as a **replaceable, non-SLA dependency behind a provider abstraction** (D-04a) |
| **Fallback router** | fal.ai | **Registered, not integrated** in v1 — a named migration target with a documented engagement threshold, not a live second path |
| **TTS provider** | ElevenLabs primary, Azure Neural as the cost and fallback tier | Per OD-13; A/B on real Czech scripts during the trial |
| **Assembly engine** | Local FFmpeg-core stack | With a cloud assembly API behind an adapter seam |
| Direct model-vendor API | — | A documented **migration path**, not a v1 integration |
| **Higgsfield** | — | **Explicitly out of the pipeline for v1** (W2.5-6, per A2's H1 recommendation) |

Naming these as roles rather than as vendors is the whole point of the abstraction. Model and vendor churn is structural and now evidenced twice (W2-16): one major video model's API is scheduled for removal on 2026-09-24, and a named trend vendor died mid-2026. Any design that hard-wires a vendor name rots before build.

**Why the router and not the model vendor directly.** The router is a prepaid credit product with one balance and one API surface fronting many upstream models at a substantial discount to official pricing (per A2's fact ledger). That discount is real and is what makes a $50 trial buy meaningful evidence. What it costs is SLA and indemnification: buying through a reseller forfeits the direct-customer protections, including generated-output indemnification, that the upstream vendor offers its own customers. The design therefore treats the router as replaceable and records everything needed to migrate.

**Why Higgsfield is out.** It is a different product category, not a peer (`SYNTHESIS.md` §8.8): a subscription creator-and-marketing studio aggregating largely the same underlying models, with genuinely differentiated *human-studio* tooling — cinema-style camera control, character identity, a UGC builder, a marketing studio — but subscription-plus-expiring-credits economics, materially thinner API documentation with per-generation pricing, retention and idempotency all unspecified publicly, and moderation stricter than the source models. Its differentiators do not fit an unattended pipeline. An optional personal seat outside the pipeline has zero architectural impact and remains at the operator's discretion.

### 5.2 The model registry

The registry is the mechanism that answers F-3. One record per **route** (a model as exposed by a router, not a model in the abstract), holding:

capability flags · price snapshot with its date · license class · person-generation policy class · known sunset date · the prompt-pattern version the route was validated against · **last-verified date** · **recheck-by date** · status · accumulated refusal statistics.

Three behaviours make it more than a list:

1. **Prices are rechecked monthly** and the forecast engine reads from the snapshot, never from a hard-coded number, displaying the snapshot date beside the estimate.
2. **A lapsed recheck-by drops a route to degraded, and the router stops selecting it for spend.** Staleness is enforced, not merely reported.
3. **Refusal statistics accumulate in-house**, because no provider publishes refusal rates. Every refusal is logged with route, trigger class and prompt-pattern version, so within weeks the operator has real per-route data instead of vendor claims.

The registry also supplies a **route-policy constraint layer** to prompt composition (A3 R5). Constraints such as the European person-generation restriction, model-level refusal of named real people, and refusal on trademarks in input images belong to the *route*, not to the theme. A theme author should never have to know that a particular route restricts person generation in Europe: the router refuses to select an ineligible route, and the prompt composer injects the constraint automatically.

The v1 roster is fixed at D-13 and is recorded here as *registry contents*, not as architecture: an everyday image route plus a text-capable image route for finals carrying type (with two registered fallbacks); a workhorse video route, a quality video route for hero assets only, and a cheap motion-draft route; one registered alternate that is also the only multi-shot-native route, at hero tier only. One widely-discussed video model is **excluded everywhere** because its API is scheduled for removal, which is also the standing proof that no model may ever be hard-wired. Music routed through the router is forbidden for published assets, because no official upstream API exists for it, every route to it is unofficial, and the upstream is in active litigation.

### 5.3 The routing contract

A generation request is expressed provider-neutrally on exactly ten axes (A2 §2.9), each mapping to a registry capability flag:

| Axis | Why it exists |
|---|---|
| **Duration** | Providers quantise differently; the plan asks for seconds, the router picks the legal quantum |
| **Aspect** | Vertical assets are 9:16; some fallbacks force 16:9, and that must be recorded when it happens |
| **Audio** | None, ambient, or native speech with a language — this is where the English/Czech split lives |
| **Mode** | Text-to-video, image-to-video, first-and-last-frame, reference, multi-shot, extend |
| **Motion class** | Talking human, product b-roll, kinetic text, scene narrative — drives model choice as much as quality does |
| **Quality tier** | Plan-only, draft, standard, hero |
| **Budget ceiling** | Maximum spend for this asset including retries, enforced pre-submission |
| **Person policy** | No-people, adults-only, region-restricted — the European constraint made explicit rather than discovered at refusal time |
| **Rights class** | Direct-commercial, reseller-uninsured, open-weight, forbidden — the publish gate reads this |
| **Resolution** | Price multipliers, and a constraint some fallback routes cannot satisfy |

The router resolves axes → eligible registry routes → cheapest within tier and rights class → submit. **Everything the router could not honour is recorded on the artifact** and surfaced in the pack.

**Config placement: theme versus global.** The split follows one test — if changing it would require touching more than one theme at once, it is global.

- **Global (engine level):** the model registry itself; the routing algorithm and its axes; the refusal ladder and its attempt cap; rate-limit pacing; the download-queue policy; rights-class definitions; the person-policy constraint layer; the tier definitions.
- **Per theme (output/runtime block):** which tiers are permitted in which mode; budget caps at every level; the media router selection and any per-theme override; preferred routes within a tier; hero auto-promote (default off) and its per-run cap; dry-run default; the recipe and audio policy per language; per-destination derivative sets.

### 5.4 Cost guards and unit economics

**Caps at four levels — per asset, per run, per day, per month — all enforced before submission.** Mid-pack cap-hit behaviour is a named outcome rather than an error: the run stops starting new paid work, checkpoints what is in flight, packages what is complete, and exits with the *partial-success — budget-capped mid-pack* class (RA-6).

The honest economics, from A2's verified prices (all figures are the brief's, at its retrieval date, and all are read from the registry at run time rather than hard-coded):

| Tier | Per two-language pack | What $50 buys |
|---|---|---|
| Draft | ≈ $1.30 | ≈ 38 packs |
| **Standard** | **≈ $3.80** | **≈ 13 packs** |
| Hero | ≈ $13.50 | ≈ 3.7 packs |

Three readings the architecture must not soften:

- **The trial validates architecture and quality, not a month of production.** Standard-tier production at three pack runs per week lands near $90–140 per month.
- **The two-language doubling is the single biggest cost driver** (OP-1, accepted at W2.5-4). Keyframe-first softens it for images because one composition serves two text variants; the recommended structural lever is **language-neutral footage plus language-specific overlays and voice added at assembly**, which collapses the video multiplier back toward one — and under the identical-mix rule this lever is doing more work than ever, since the Czech lane's default recipe buys no clips at all.
- **A documented trial plan bounds the risk** (W2-14): roughly $8 on a bake-off producing the operator's own evidence rather than blog claims, roughly $35 on eight to ten real two-language packs end to end, roughly $7 held in reserve. Hero tier is never auto-selected, and a separate router key for scheduled runs with a bounded top-up means a runaway loop is limited by the wallet rather than only by our code.

### 5.5 Retention, re-hosting and the artifact of record

Provider-generated media is deleted after 14 days and result URLs expire sooner, with an explicit expiry flag on at least one route family (per A2's fact ledger). Three rules follow:

1. **Every artifact is re-hosted immediately on completion**, with a byte-length and checksum record, before the asset slot is marked complete — so a truncated download is never marked done.
2. **The download queue is drained in expiry order at the start of every run, before any new submission.**
3. **Provider URLs never appear in a pack** and are never the artifact of record.

### 5.6 Refusals, substitution and the money-safety boundary

**Refusals are a normal outcome class**, not an error path. They surface both synchronously at submission and asynchronously mid-task, and the marketing-relevant triggers are predictable: named real people, the European person-generation restriction that directly affects a Czech operator, trademarks and logos in input images, and documented false positives on entirely wholesome commercial storyboards. The ladder is bounded and terminates in a *useful* state: one automated sanitise-and-rewrite → one model swap to a registered alternate → **degrade to plan-only**, packaging the approved keyframe, script and prompt with the refusal reason. Never a retry loop. A policy refusal is emphatically not transient and must never enter the ordinary backoff path.

**Silent model substitution is guarded explicitly** (W2-03). The router's primary video route can switch to a backup model on some content-review triggers, and such fallback outputs cannot use the high-resolution endpoint and are forced to 16:9. Two consequences are recorded on every artifact: **requested versus delivered route, aspect and resolution**, so a 16:9 asset cannot silently enter a 9:16 destination and fail at publish time; and the **per-asset provenance record is resolved after completion, not at submission** (D-20), because a different model may carry a different rights class and a license snapshot naming a model that did not render the asset destroys the rights-defence record.

**Money safety is entirely client-side, because no provider idempotency exists.** The router documents no idempotency key, no client-reference field and no deduplication semantics on task creation (verified in A2, correcting C3's earlier assumption). The consequences — a write-ahead spend ledger with deterministic asset identity committed before submission, resolve-by-query on restart rather than blind resubmission, a named `submitted-unknown` state with no automatic resubmission, balance-delta reconciliation with an unexplained-spend circuit breaker — are D-17, and **the sibling draft owns their design.** This section references them so the provider architecture is complete; it does not duplicate them.

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

The engagement threshold for each migration step is a named open item rather than a guess. What the architecture guarantees is that **no rung silently produces a worse asset**: a degraded run produces plan-only artifacts and says so, rather than substituting a lower-quality route without telling anyone.

### 5.8 Room for the later paid phase

The assignment reserves architectural room for Meta Ads and paid creatives, with generation in scope and spend human-controlled. Three seams already exist and no new ones are needed: the **ad-creative skill bundle** is one of the four named skill bundles and already carries a stricter claim-safety rubric and a mandatory human gate before any spend (A3 §2.2); the **routing contract's rights class** axis already distinguishes assets that may carry paid distribution; and the **publish allowlist** is per mode and per destination, so a paid destination is an allowlist entry rather than a new enforcement path. The one substantive addition the paid phase will need is a separate mandatory ad-disclosure control — undisclosed AI is reported as a leading cause of ad rejection with strike escalation (per C1 and C7 ledgers) — which is a check-class addition, not an architectural change.

**Knobs this section contributes to §10.** Media router selection and per-theme override; permitted tiers per mode; preferred routes within a tier; hero auto-promote flag and per-run hero cap; budget caps per asset, run, day and month; unexplained-spend tolerance; dry-run default per mode; refusal-ladder attempt cap; submission pacing rate; poll interval and per-job poll budget; download-queue drain policy; price-recheck cadence and recheck-by grace; rights-class allowlist per destination; person-policy defaults per theme; fallback-router engagement threshold; the trial budget envelope and its reserve.

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

So: **Step 1** — every blocking class must be resolved or legitimately resolved-empty, non-conflicted and not hard-stale; any gate failure sets a hard ceiling on the band and **names itself as the reason**. **Step 2** — score inside that ceiling across blocking and constraining classes on coverage, corroboration depth, freshness ratio and conflict count. **Step 3** — capabilities follow the band, which is what makes bands mean something operationally.

The band is computed **per (theme, language)** — a Czech pack can be blocked while the English pack proceeds, which falls straight out of D-02. Bands are deliberately coarse: four names, no decimals shown. "Brand confidence 0.78" invites arguing with the thermometer; "PARTIAL — proof claims off, prices off" tells the operator what actually changed.

| Band | Precondition | What content may do |
|---|---|---|
| **FULL** | All blocking gates pass; commercially binding facts corroborated by the live site this run or within the warn window; zero conflicts; constraining classes mostly resolved | Full spin. All CTA classes subject to their own preconditions. Approved proof claims allowed. Prices and trial terms may be stated if policy permits. Long-form and site-first content allowed |
| **PARTIAL** | All blocking gates pass, but corroboration is thin or some constraining facts are unresolved or in the warn window | Spin allowed. **All proof claims blocked** unless that individual ledger entry is itself at full confidence. **No prices, no trial terms, no case metrics, no comparative claims.** CTAs limited to the zero-commitment and product-page classes. Pack marked |
| **MINIMAL** | Running from an offline snapshot within its validity window, or config-only resolution of blocking classes | Capability-level statements from the snapshot only. **No numbers of any kind.** No proof, no comparisons, no price or trial CTAs. Interactive-only by default, heavily marked |
| **INSUFFICIENT** | Any blocking gate fails; an unresolved red-flag conflict on a binding fact; an expired or unverifiable snapshot | **No brand spin at all.** Research-only output |

**The exact unattended degrade trigger.** In an unattended run, for the language being generated, the run degrades to research-only if **any** of the following holds (C6 §5.4):

1. The band is **below PARTIAL**.
2. **Any unresolved red-flag conflict** exists on a blocking or commercially binding fact — regardless of band, because a conflict is not an average and does not get diluted by everything that is fine.
3. Brand truth is available **only from an offline snapshot** older than the configured maximum offline window, or whose integrity check fails.
4. **The claim ledger could not be read at all** — distinct from being empty. Unknown is not empty: if we cannot read the ledger we can neither prove a claim is allowed nor trust the excludes beside it.
5. **Hard excludes are unresolved** — again, not empty, unresolved. You cannot enforce "never say X" without knowing X.

Conditions 1 and 3 are band-driven; **2, 4 and 5 bypass scoring entirely** and cannot be overridden by an operator even interactively, because they are about not knowing the rules rather than about having thin data.

**Why the threshold sits at "below PARTIAL" rather than "below FULL".** Requiring full confidence for unattended runs would degrade the pipeline every time a site fetch flaked, and a system that cries wolf daily gets its alarms ignored or gets switched off — which is the real failure. PARTIAL is defined *precisely so that everything dangerous is already switched off at PARTIAL*: no prices, no proof, no metrics, no comparative claims, no commitment CTAs. **The safety comes from the capability table, not from the threshold's height.**

**What the operator sees when it fires** (C6 §5.5): a distinct run outcome, separate from both success and failure, so monitoring can alert differently; one plain sentence at the top of the digest naming the actual cause and the actual fix, not "confidence low"; a brand-truth panel with one row per blocking class showing state, source used, observation age and a *specific* fix action; **both conflicting values side by side with sources and timestamps**, so the operator can fix their own systems without opening anything else; the statement that zero was spent; and — critically — **the research output remains complete and reusable**, so the next run or an interactive re-run spins the same already-paid-for topics. A degrade that throws away the run's work will be engineered around by the operator within a fortnight. An anti-flap rule escalates prominence on repeat rather than repeating an identical low-signal message.

### 6.6 Refresh cadence, the offline snapshot, and the per-pack snapshot

**Cadence.** Once per run, before anything is spent and before collection, cheapest gates first: config load → snapshot validity → Notion pull → targeted site verification. A **TTL-guarded re-pull** avoids pointless re-fetching when a theme runs several times a day. **Site verification is targeted, not a crawl**: only the binding facts and CTA URL liveness, a handful of timeboxed fetches per run, with failures recorded as "not observed". **Event-driven triggers** force a full re-pull regardless of TTL: theme-readiness validation ran, the theme config's content hash changed, a human rejected a pack citing a wrong brand fact, a claim check produced a contradicted verdict, a CTA URL returned 404, or a new offer status appeared. A **claim-ledger expiry sweep** lists claims expiring within the next 30 days in the digest — otherwise proof silently vanishes from content one day and nobody knows why the posts got vaguer.

**The offline snapshot** is the Notion-down path. The last successful FULL or PARTIAL snapshot is persisted append-only with several generations retained. A snapshot written during a MINIMAL or INSUFFICIENT run is **never promoted to last-good**, otherwise degraded state ratchets forward. Running from a snapshot **caps the band at MINIMAL, always** — you cannot know whether the world changed while you were blind, and the cap is what makes the offline path safe rather than merely convenient. The maximum offline window is configurable (recommended 7 days unattended, 14 interactive) and is independently capped by the hard-stale thresholds of the facts inside it. **A snapshot failing its integrity check is treated as absent, never as best-effort.**

The realistic 3 a.m. outage behaviour is therefore: research and ranking complete, no brand content, digest explains exactly why, nothing spent.

**The brand-truth snapshot per pack** carries the normalised fact set with per-fact source, observation time and confidence; the computed band and its gate results; all conflicts including quarantined ones; the claim-ledger version; the theme-config version; and the **resolver rule version** — because precedence and thresholds change over time and a snapshot without its rule version is not reproducible.

**Two identifiers, not one** (C6 §6.3). A **content hash** over the canonically ordered, normalised fact set — hashing semantic content rather than serialisation, or trivial key-order churn manufactures spurious "the brand truth changed" events and destroys the signal. And a **fact-usage trace**: the list of fact identifiers and claim-ledger entry identifiers that *this specific topic pack* actually consumed. The hash proves integrity; the trace enables recall. The question an operator genuinely asks six weeks later is not "was the snapshot intact" but **"we just corrected the trial length — which published packs are affected?"** That is a lookup by fact, answerable only if consumption was recorded per pack. It is the highest-value auditability feature in this layer and it costs almost nothing to record.

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
| 10 | **Required-statement (bidirectional)** | Fails if a mandated statement is *missing*: affiliate or discount disclosure, entity disclosure, AI-content labelling | The affiliate arrangement in the real strategy triggers this |
| 11 | **Corpus leakage** | Numbers, metric phrases and named entities appearing in the exemplar corpus but nowhere in the ledger are **blocked**, and the overlap is recorded as a leakage event | See §6.10 |

**Verdicts:** *verified* (matches an in-scope, unexpired entry) · *safe-non-claim* (classified structural or self-referential) · *unsupported* (claim-shaped, no match) → blocks · *contradicted* (conflicts with a resolved fact) → blocks **and raises a brand-truth review flag, because it may mean the ledger itself is wrong** · *disclosure-missing* → blocks until inserted.

**Enforcement ladder, per asset:** block and record the offending spans → **bounded regenerate** (recommended maximum two attempts, each fed the specific failing spans *and a positive constraint* naming what may be said instead) → **downgrade repair**, emitting the claim-free variant of the asset with no proof and a softer CTA, which converts a hard failure into something publishable → drop the asset with the reason recorded and the rejected draft attached. **Never silently ship, never silently discard without a note.**

**The retry allowance is per pack, not per asset** — otherwise an unattended run with a systematically bad prompt burns its budget on a regeneration storm. Exhausting the pack allowance degrades that pack to review-required rather than failing the run.

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

The canonical per-asset order, stated once:

    generate
      -> SPIN GATE            "is this the right thing to say?"
      -> CLAIM GATE pass 1    "is it true and allowed?"  (fail fast)
      -> VOICE GATE           "is it said like a human, in this language?"
      -> CLAIM GATE pass 2    final, immutable, on the exact packed bytes
      -> PLATFORM GATE        "does it fit this destination's hard limits?"
      -> (media only) COST GATE -> media generation -> assembly
      -> asset QA rubric -> packaging
      -> HUMAN REVIEW GATE -> PUBLISH GATE

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

**Knobs this section contributes to §10.** Brand-truth source pointers, including which Notion locations are designated fact locations, per fact class; access path per context; site-verification URL set, fetch budget and timeout; freshness stale-warn and hard-stale thresholds per fact class; maximum offline window per mode; band floor per mode; the claim-ledger pointer; the hard-excludes baseline list in config; check-class enablement with five classes non-disableable; per-pack regenerate allowance; the pain-to-offer relation; mapping-distance policy per offer; CTA class enablement per destination per language and the CTA phrase bank pointer per language; site-first offer list and the hold-versus-substitute choice; the person allowlist; the brand-and-domain routing map; ASR sampling rate and the adherence-alarm threshold; exemplar corpus pointer per theme per language; corpus-leakage sensitivity; resolver rule version; TTL for snapshot reuse; the event-driven refresh trigger set.

---

## Cross-references and hand-offs

| This draft establishes | The sibling draft or a later section consumes it as |
|---|---|
| Stage sequence and gate order (§1.3, §6.10) | The end-to-end flow for interactive and scheduled execution |
| The exit-relevant outcomes named here — pending media, budget-capped mid-pack, research-only degrade | The nine-class exit-code taxonomy |
| Per-source ladders, staleness flags, curated-inbox misses (§2.2, §2.3) | Degraded-source reporting in the run pack and digest |
| Retention windows and targeted deletion (§2.6) | The research artifact store's operational rules |
| Per-asset AI-label-required flag and the burned-in disclosure (§3.3, §4.4) | The publish gate's readiness precondition and the operator runbook |
| Cost gate, tiers, caps and the dry-run boundary (§4.6, §5.4) | Budget enforcement under a scheduler and the cost forecast in the digest |
| Write-ahead spend ledger, `submitted-unknown`, re-host discipline (§5.5, §5.6) | The ledger designs, which the sibling draft owns |
| Confidence bands, degrade trigger and the brand-truth panel (§6.5) | Mode capability matrices and the digest's header |
| Claim gate double-pass, spin gate criteria, corpus-leakage class (§6.7, §6.10, §6.11) | Voice and claim-safety enforcement by design |
| Knob rosters at the end of every section | The theme config's research, spin and output/runtime blocks |

## Open items this draft surfaces for the assembler

1. **D-02a is superseded by W2.5-4 and should be marked as such in the decision log.** The synthesis's per-language channel table is obsolete; §3.1–3.2 above replace it.
2. **W2-08's recorded mitigation is void.** The risk log's mitigation for Czech asset-mix reputational risk reads "TikTok excluded for cs in v1". That is no longer the design. §3.1's six design commitments are the replacement mitigation and the risk log should carry them.
3. **The "Czech mix is cheaper, which softens OP-1" conclusion is now conditional**, not general — true while Czech runs the carousel-to-reel recipe, false the moment it is promoted to generative clips. §3.1 and §5.4 state it that way; the cost forecast reads from the registry regardless.
4. **Media-bearing caps count masters, not destination derivatives.** OD-8's recommendation was framed before the identical-mix decision; §3.2 resolves the ambiguity and the §10 author should carry the resolution into the knob definition.
5. **X as a publish destination remains genuinely undecided.** §3.2 treats it as config-gated and default-off, producing assets at no marginal cost while never being a connected channel. If the operator wants X assets suppressed entirely rather than merely unpublished, that is a one-knob change and should be asked at Stage 5.
6. **The claim-ledger location (OD-9) is carried as a recommendation, not a lock.** §6.3 assumes the Notion-primary split with hard excludes duplicated in config; if the operator prefers config-only, the monotonicity rule survives but the operator loses the ability to edit claims without touching config.
7. **Two Czech prerequisites are named but not scheduled**: the Czech structural-calibration corpus and the Czech judge golden set. Both must exist before the first Czech production run and belong in the phased roadmap.
