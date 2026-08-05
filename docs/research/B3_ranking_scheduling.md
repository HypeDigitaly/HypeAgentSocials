## B3 — Ranking design, negative brand-fit, anti-forced-placement, per-language fit, unattended scheduling behavior, and calibration

**Brief owner:** T7 (expertise brief, no web access — durable domain knowledge only; volatile/verification items flagged ASSUMED INPUT).
**Assignment scope:** Block B items 5 and 7 (item 6, operator review presentation, is owned by C4/T12 — this brief only supplies the sub-scores C4 will render, not the review UI itself).
**Hard dependency:** every field this brief assumes a source can expose (engagement counts, timestamps, author/account metadata, language tags, historical baselines) is owned by B2 (`B2_extraction_methods.md`). Every such assumption is marked **ASSUMED INPUT (from B2)** inline and collected again in §2.7. Synthesis (Wave 2) must re-derive this design against B2's real findings, not just reconcile wording.

---

### 1. What this means for the operator

Every day (or however often the schedule runs), the system will have looked at a pile of raw "things happening online" — a Reddit thread, a viral tweet, a Product Hunt launch, a Google Trends spike — and needs to decide which of those are worth turning into HypeDigitaly/HypeLead content, in Czech, in English, or neither. This document is the design for that decision.

Three ideas matter most for you as the person who will eventually review the output:

1. **Nothing gets to the "write the post" stage unless it clears a brand-fit bar first, checked before anything gets written.** A topic can be enormously popular and still get thrown out immediately if it has nothing honest to do with what HypeDigitaly/HypeLead sells or who it sells to. The system is built so that popularity alone can never buy its way past a bad fit — the math is deliberately structured (multiplied together, not averaged) so a huge "everyone's talking about this" number cannot cancel out a near-zero "this has nothing to do with us" number. That is the direct answer to "don't force product spam onto unrelated trends."
2. **Every topic that does make it through comes with a report card, not just a number.** Score for "is this actually popular," score for "does this fit our brand," score for "is this still fresh," plus one plain sentence explaining each — e.g. "skipped: this is about AI image generation, unrelated to coding agents or outbound sales" or "kept: matches configured pain — cold email deliverability; seen independently on Reddit and Hacker News." You should never have to trust a black-box number.
3. **Czech and English are judged separately, not translated.** A topic can be huge in English and simply not land for a Czech B2B audience (wrong market maturity, an English pun that doesn't survive translation, no Czech-language discourse about it at all) — or the reverse. The system will tell you, per topic, per language: generate, skip, or "not enough evidence yet, your call."

The rest of this document is the reasoning and the mechanics behind those three promises, plus how the system behaves when run unattended (cron), how it handles junk/spam/manipulated trends, what happens on day one when data sources are thin, and how your accept/reject decisions should (carefully, not automatically) tune the system over time.

---

### 2. Ranking design — raw signals to scored, inspectable candidates

#### 2.1 The four dimensions

Every raw signal (a post, a thread, a trending entry, a launch listing) that survives the upstream collection/topic-taxonomy filter (owned by B1/B2 — collection is already scoped to configured watch topics, so this is a second line of defense, not the only one) gets evaluated on four dimensions before it becomes a ranked candidate.

| Dimension | What it measures | Depends on | Output |
|---|---|---|---|
| Attention/virality | How much organic attention this already has, independent of us | Per-source engagement signal — **ASSUMED INPUT (from B2)**: which sources expose counts vs rank-only vs nothing | 0–1, normalized *within source*, not compared raw across sources |
| Brand-fit | Whether an honest, non-forced connection to configured ICP pains and offers exists, net of negative criteria | Theme config (watch topics, ICP map, offer map, excludes list) + LLM judgment | 0–1, with a hard floor forced to near-zero the instant any veto criterion trips (§3) |
| Freshness | How current the signal is, decay-rated by the *kind* of signal it is, not a flat clock | Signal-class taxonomy (§2.4) + first-seen/last-seen timestamps — **ASSUMED INPUT (from B2)**: timestamp precision per source | 0–1, decaying per signal class |
| Confidence/availability weight | How much structural trust to put in the virality number given what the source actually exposed | Per-source metadata completeness — **ASSUMED INPUT (from B2)** | 0–1 multiplier, also surfaced as a plain evidence-quality label (High/Medium/Low) |

A source that exposes no engagement data at all cannot contribute a virality sub-score in the normal sense. In that case the design substitutes a weaker proxy (existence/rank on a curated list, "featured" placement) explicitly marked as lower-confidence rather than inventing an equivalent number — the confidence weight then structurally caps how much that candidate's composite score can ever reach, so a thin-evidence source cannot masquerade as a strongly-corroborated one.

#### 2.2 Why virality cannot be compared raw across sources

500 upvotes on a small subreddit, 500 likes on X, and a "rising" arrow on Google Trends are not the same unit and must never be summed or averaged directly. The design normalizes virality **within each source's own recent distribution** — a topic's raw count is converted to a percentile against that source's typical volume over a trailing window (e.g., "this is in the top 5% of engagement this source has produced in the last two weeks"), or, where the source gives an already-normalized figure (Google Trends' 0–100 relative index is itself a within-source normalization), that figure is used directly. Only after each source produces its own 0–1 percentile-style score does cross-source combination happen.

**Cross-source corroboration bonus:** when the same real-world topic (see §5.2 on identity/dedupe keys) is independently observed on two or more structurally distinct sources on the same collection run, that agreement is itself evidence of a real trend rather than single-source noise, and should lift the composite (a modest additive or multiplicative bonus, tunable, not dominant). Conversely, a single-source-only topic should carry a corroboration penalty or at least a confidence ceiling — not disqualifying, just honestly labeled as thinner evidence. This interacts directly with cold-start reality (§6.5): with few sources online, corroboration will rarely fire, and that must be shown to the operator as "thin evidence," not silently smoothed over.

#### 2.3 Combining the four dimensions: multiplicative, not additive

Composite score (per candidate, per language — see §5) equals virality sub-score, times the confidence/availability weight, times the freshness sub-score, times the brand-fit sub-score — each already normalized to a 0–1 range. Multiplication is the deliberate choice over a weighted sum for one reason: in a weighted sum, a very high virality number can mathematically outvote a very low brand-fit number (e.g., 0.95 virality and 0.10 fit could still average acceptably with generous weights). In a multiplicative composition, a near-zero factor drags the whole product toward zero regardless of how large the other factors are. This is the primary mathematical mechanism behind "weak brand fit → skip," and it is discussed further as the anti-forced-placement backbone in §4.

#### 2.4 Freshness is signal-class-dependent, not one clock

Not all "recent" means the same thing. The design recognizes at least four freshness classes, each with its own decay behavior (half-life figures below are opinionated starting defaults for calibration, not physics — see the deferred-decisions table in §7):

| Signal class | Example pattern | Suggested decay half-life | Why |
|---|---|---|---|
| Spike | A single viral tweet/thread; a moment everyone is reacting to right now | ~12–24 hours | Dies fast; tomorrow it's old news |
| Rising | A topic climbing over several days (a Google Trends "breakout" query, a growing Reddit thread) | ~2–4 days | Still building; the peak may not have happened yet |
| Launch-hype | A product/feature/model launch cycle | ~3–7 days, then reclassify | Decays with the news cycle, but a durable launch can graduate into an evergreen-pain-adjacent topic (e.g., "how do teams actually use this new agent tool" outlives the launch announcement itself) |
| Evergreen-pain | A recurring ICP complaint/objection (e.g., "cold email deliverability is broken") that isn't tied to one event | ~2–4 weeks, and really governed more by "has this specific angle been covered recently" than raw age | These don't really "trend," they recur — freshness here is mostly a de-duplication question, not a decay curve |

Cadence interaction: freshness windows must be read relative to how often the theme's schedule actually runs, not absolute calendar time alone. A spike-class signal with a 12–24h half-life is a poor match for a theme configured to run twice a week — it will almost always be stale by the next run. This is a design input for whoever sets cadence per theme (owned by the runtime/config layer), but ranking should expose it as an explicit warning ("this theme's cadence may systematically miss spike-class signals") rather than silently under-scoring every spike topic without explanation.

#### 2.5 Inspectable sub-scores — the operator's audit surface

Every candidate that survives collection carries a scorecard, conceptually containing (no schema/format prescribed here, contents only):

- Topic label, the source(s) it was seen on, first-seen and last-seen timestamps, and how many independent sources corroborated it.
- Virality sub-score, in both raw 0–1 form and a plain band (High/Medium/Low), plus a one-line rationale ("top 8% engagement velocity for r/sales over trailing 14 days" or "featured on Product Hunt front page, no engagement counts exposed by source — proxy signal only").
- Brand-fit sub-score, band, and a one-line rationale naming the specific ICP pain/offer it maps to, or the specific negative criterion that tripped (§3).
- Freshness sub-score, band, signal class, and age.
- Evidence-quality label (High/Medium/Low) and which sources fed it.
- Composite score and a gate status: Passed / Hard-skip (with the specific reason) / Monitor-only (below the pass bar but not vetoed — kept visible for trend-watching, not forwarded to content generation).
- Per-language fit outcome (§5): generate / skip / hold, per configured language, each with its own one-line rationale.
- The ranking-config version that produced this scorecard (weights/thresholds/rules-list version — see §7.4), so a score is explainable relative to the logic active when it was computed.

This is designed to be readable without statistics literacy: bands plus one plain sentence per dimension, not just a number. C4 (operator review UX) is the intended consumer of this scorecard's presentation; this brief only guarantees the scorecard's *contents* exist and are inspectable at this level of granularity.

#### 2.6 The hard skip threshold

Two independent gates, not one:

1. **A numeric floor on brand-fit alone**, applied before the composite is even computed. A default starting point of 0.35 (on the 0–1 scale) is suggested — any candidate scoring below this on brand-fit is removed from the ranked list entirely, regardless of how high virality, freshness, or confidence are. This is deliberately a floor on brand-fit specifically, not on the composite, because a low composite could otherwise result from ordinary staleness (fixable by waiting) rather than a genuine fit problem (not fixable by waiting) — collapsing both into one number would hide the difference from the operator.
2. **A binary veto list**, independent of any numeric score (§3, §4c): certain negative criteria (legal/claim-risk, competitor disparagement, high-severity controversy, detected manipulation/spam/prompt-injection) are absolute stop conditions. They are not inputs to an average that a high score elsewhere could outweigh — they are checked and, if tripped, the candidate is removed before scoring proceeds further.

Exact numeric threshold values are a calibration question (see §7 and the deferred-decisions table) — the structural point (a hard floor plus a separate binary veto list, both prior to composite ranking) is the fixed part of this design.

#### 2.7 Consolidated ASSUMED INPUT (from B2) list

For synthesis re-derivation:

- Per-source availability of engagement counts vs rank-only vs no metadata at all (drives §2.1–2.2's normalization method per source).
- Per-source timestamp precision (near-real-time vs daily-granularity vs unknown) — drives freshness resolution (§2.4).
- Per-source language tagging/detectability (drives §5's per-language routing — does the source tell us the content's language, or must it be inferred).
- Per-source retained history / rolling baseline availability — needed for the manipulated-virality outlier check (§6.4) and for the within-source percentile normalization (§2.2) itself; if no history is retained across runs, percentile normalization has nothing to compare against on early runs (this is also a cold-start factor, §6.5).
- Per-source author/account metadata richness (needed for "brand-new account, suspicious spike" detection, §6.4) — expected weaker for browse/scrape-derived sources than for API sources.
- Whether B2's collection layer already produces any per-item topic/entity tag usable as a starting point for the cross-day dedupe key (§5.2), or whether ranking must build semantic clustering from raw text alone.

---

### 3. Negative brand-fit criteria — the anti-forced-placement research core

This is the part of the design that actually enforces "weak brand fit → skip, never force product spam onto unrelated trends." Seven categories, each with how it is concretely detected and what happens when it fires.

| Negative criterion | What it looks like in practice | Detection method | Consequence |
|---|---|---|---|
| **Category mismatch** | Surface keyword overlap with "AI" but no real connection to coding agents, lead-gen, outbound, or sales discourse (e.g., a viral AI-image-generation controversy, a self-driving-car story) | Rule-based keyword/topic-cluster pre-filter catches obvious non-matches cheaply; LLM judgment on borderline cases, required to produce one credible causal-link sentence to the configured ICP pain map — if it can't, it fails | Hard skip |
| **Competitor saturation** | A named competitor's launch/feature where a response would be pure ambulance-chasing, or a topic where the commentary space is already homogeneous/full (everyone said the same take by day 2–3) | Rule-based competitor name-list match (from theme config's excludes/competitor list) as a fast pre-filter; LLM judgment on whether a genuinely independent angle exists and whether the discourse feels "full" (sampled repetitive phrasing across sources) | Score penalty by default; escalates to hard skip if no independent angle can be produced |
| **Tone/controversy risk** | Politically charged, tragedy-adjacent, culture-war-adjacent, or otherwise reputationally disproportionate topics even when nominally on-topic (e.g., an AI company's layoffs/lawsuit/safety scandal) | Primarily LLM judgment producing a severity tier + one-line justification (keyword blocklists alone both over- and under-trigger here); a config-defined keyword list (named litigation, tragedy, protected-class terms) serves only as a cheap first pass | Severity-tiered: theme config sets the acceptable ceiling; above it, hard skip |
| **"Brand looks desperate" pattern** | The connection to the offer requires more than one inferential hop, relies on a coincidental keyword/homonym match (e.g., "agent" meaning a spy, not a software agent), or many unrelated brands are already piggybacking the same trend with generic hot-takes | Rule check for keyword-in-context vs coincidental token match as a first pass; LLM judgment is primary — ideally the *same* judgment step used to attempt writing the honest connection, run as a pre-check ("state the honest connection in one sentence; if you cannot, say so") | Hard skip if no credible one-sentence honest connection can be produced |
| **Legal / claim-risk topics** | Topics that would tempt the writer into unverifiable claims (competitor wrongdoing allegations, a regulated-adjacent claim about AI/legal compliance the brand isn't positioned to make authoritatively) | Rule-based blocklist per theme (named legal proceedings, health claims, financial-advice-adjacent claims, regulatory-compliance-specific claims) as a hard veto list; LLM judgment for "would responding require an unverifiable factual claim," reusing the claim-safety verification substrate — **ASSUMED INPUT (coordinate with brand-truth/claim-safety design, owned outside this brief)** | Hard skip |
| **Off-ICP audience mismatch** | On-topic AI/tech content that resonates with a different audience than the configured ICP (hobbyist/consumer AI enthusiasts, purely academic ML research debates) rather than agencies, sales/GTM leaders, or cold-outreach users | Rule-based ICP-keyword/persona match as a first pass; LLM judgment on "which persona actually engages with this" | Score penalty; hard skip if clearly off-persona |
| **"Nothing to add" / stale consensus** | The topic has been so extensively covered (broadly, not just by named competitors) that a new post offers no incremental angle | LLM judgment: "is there a genuinely new angle we can bring" — overlaps with cross-day dedupe (§5.2) but applies even without a prior pack on this exact topic | Score penalty; feeds into resurgence logic in §5.2 |

**Rules vs LLM judgment, the general split:** rules are cheap, deterministic, and appropriate for anything enumerable — named competitor lists, legal-claim blocklists, obvious keyword exclusions from theme config. LLM judgment is required wherever the decision is contextual and holistic — severity of controversy, whether a connection feels forced, whether a discourse space feels saturated. The recommended pipeline shape is a two-pass filter: a cheap rule-based pass first (runs on every raw signal, before any LLM cost is spent — relevant to cron cost control), then LLM judgment only on survivors. This keeps unattended-run cost bounded while still giving the contextual criteria the reasoning they actually need.

**Worked example 1 (category mismatch):** a new viral text-to-image model release trends heavily across multiple sources. Rule pass flags "AI" keyword match; LLM pass is asked for the causal link to coding-agents/lead-gen/outbound — none exists — hard skip regardless of virality.

**Worked example 2 (competitor saturation with honest angle available):** a competitor's cold-email tool ships a new AI personalization feature. Rule pass flags the named competitor. LLM pass is asked whether an honest, non-piggybacking angle exists — "here's what this means for teams still avoiding AI in outreach because of deliverability fears" is judged as an independent, ICP-relevant angle distinct from "you should switch to us" — score penalty applied but not vetoed, proceeds to spin with an explicit rationale flag for the operator to sanity-check.

---

### 4. Anti-forced-placement design — structural, not aspirational

The assignment specifically warns against "trend dump + random product mention." The mechanisms below are wired into the scoring and pipeline structure itself, not left to an instruction telling a generator to "please don't force it."

**a) Multiplicative composition (§2.3).** A near-zero brand-fit factor drags the composite toward zero no matter how large virality, freshness, or confidence are. This is the mathematical backbone: popularity cannot buy past a genuinely poor fit.

**b) The hard-skip gate runs before the candidate ever reaches the spin/content-generation stage.** Low-brand-fit and vetoed candidates are removed from the candidate list the spin stage receives — structurally, there is no code path in which a generator is handed an unrelated topic and asked to "make something work" with it. Removing the opportunity at the data-flow level is the primary control; relying on an LLM's restraint at write-time is, at best, a secondary backstop.

**c) The binary veto list sits outside any weighted average.** Legal/claim-risk, competitor disparagement, high-severity controversy, and detected manipulation are checked as absolute stop conditions prior to scoring, specifically so they cannot be outvoted by a very high virality number under any composition scheme, multiplicative or otherwise.

**d) The brand-fit judgment step must produce a falsifiable verdict, not a vague score.** It is required to either state the honest connection in one sentence or explicitly say it cannot — and if it cannot, the candidate fails regardless of any other dimension. This design choice makes the *attempt to honestly connect* itself the fit test, so the same reasoning surface used later to write good spin doubles as the veto mechanism for bad spin. A separate, independent "does this feel forced" checker that could disagree with the writer's own judgment would be weaker than making the writer's own honest-connection attempt the gate.

**e) Rationale-carrying scores are a defense-in-depth layer, not the primary control.** Because every scorecard exposes the actual one-line rationale, an operator auditing "why did this rank so high" will see a forced-connection attempt if one somehow slips through automated checks — but this is a human backstop, not a substitute for (a)–(d).

**f) Fail closed, never fail open, on the brand-fit check itself.** If the brand-fit LLM judgment step fails to run at all (timeout, provider outage, budget cap hit mid-pass), the affected candidate must fail to "not-ranked / monitor-only," never default to "assume fit passes." This is an explicit design decision so that an infrastructure failure during an unattended cron run can never accidentally produce bad-spin content by silently defaulting open.

**g) The taxonomy pre-filter upstream (owned by B1/B2) is the first line of defense, not the only one.** Collection is already scoped to configured watch topics, so most of the raw universe never becomes a candidate. The negative-criteria layer in this brief is specifically the second line, catching topics that are nominally on-taxonomy by keyword but off-fit in substance — the two layers are complementary, and neither should be treated as sufficient alone.

---

### 5. Per-language relevance (cs + en, first-class per D-02)

#### 5.1 Why a global fit score is wrong

Per F-7 (Czech is not a translation pass) and D-02 (every configured language is a full first-class output set), brand-fit and freshness must be scored **per language**, not once globally with a translation step bolted on afterward. Three distinct ways languages can disagree:

- **en-fit high, cs-fit low:** a US-specific tool controversy, an English-language wordplay hook, or a launch that hasn't reached Czech market awareness — the Czech ICP wouldn't recognize or care about it yet (local market maturity gap).
- **cs-fit high, en-fit low:** a Czech-specific regulatory/tax/business change affecting Czech B2B outreach, or a Czech-language LinkedIn discourse moment with no international resonance.
- **Both fit, but hook-portability differs:** a topic is genuinely relevant in both markets, but the viral *hook* (a pun, a rhythm, a cultural reference) that makes the English version work is untranslatable — this doesn't fail cs-fit, but should be flagged "hook likely non-portable, needs a cs-native hook, not a literal analog" so the spin/content stage doesn't expect a direct equivalent.

#### 5.2 What per-language fit is built from

Beyond the general brand-fit judgment (§2, §3) run independently per language, three cs-specific sub-considerations matter:

1. **Local market maturity** — is the referenced product/trend already known/adopted in the Czech market, or would content about it feel imported/foreign to a Czech reader? This lowers cs-fit without necessarily zeroing it.
2. **Wordplay/hook untranslatability** — flagged separately from fit itself (see above); a research-stage flag, not a content-generation decision, but one the downstream spin stage needs to know about.
3. **Source-language corroboration** — did the topic actually appear in Czech-language sources/discourse, or is cs-relevance purely inferred from English-language sources with zero local signal? The latter is a much weaker basis for claiming cs-fit and should be reflected in a lower confidence band, not asserted as equal-strength evidence to a directly-corroborated en topic. **ASSUMED INPUT (from B2/B1/B4):** whether Czech-native sources exist in the collection roster at all and what their extraction/access status is — this brief assumes that status is often thin early on (consistent with F-1/F-9 pessimism), which is exactly why "thin cs evidence" is treated as a distinct state from "genuinely poor cs fit" below.

#### 5.3 What happens when languages disagree

| Situation | Outcome |
|---|---|
| en-fit and cs-fit both clear the hard-skip threshold | Generate full first-class packs in both languages (default happy path per D-02) |
| en-fit clears, cs-fit below threshold | Generate en-only; do **not** default to a translated cs pack (this would violate F-7); log "cs: skipped" with rationale so it's visible in review, not silently dropped; optionally hold on a cs watch-list in case local corroboration appears on a later run |
| cs-fit clears, en-fit below threshold | Mirror case: generate cs-only, skip en, log rationale (structurally symmetric even if empirically rarer for global AI/tech topics — a Czech-specific regulatory story is the realistic example) |
| Both below threshold | Standard hard-skip in both languages |
| One language's evidence is thin (not clearly low-fit, just under-evidenced due to sparse cs-native source coverage) | Do **not** auto-skip. Mark "cs: low-confidence, needs operator judgment" and surface it rather than silently deciding — collapsing "under-evidenced" into "poor fit" would systematically under-serve cs output during exactly the period (early runs, thin cs sources) when it needs the most help, not the least |

**Structural requirement handed downstream:** even when both languages are marked "generate," each language must run its own brand-fit/negative-criteria pass and its own voice/spin pass — ranking's output is a per-language decision (generate / skip / hold), never a single global decision with an implied "then translate." This is the mechanism that actually prevents Czech output from becoming a translation pass at the ranking layer; the equivalent guarantee for the writing layer itself belongs to the voice/spin design (owned elsewhere), and is flagged here as a dependency, not solved here.

---

### 6. Unattended collection behavior (Block B item 7)

#### 6.1 Freshness windows per signal type

Covered in §2.4 (signal-class taxonomy and suggested half-lives). The addition relevant to unattended operation specifically: freshness windows must be read relative to the theme's actual run cadence (see §2.4's cadence note), and this brief recommends the run-cadence-vs-decay-half-life mismatch be an explicit, visible warning to the operator rather than a silent scoring quirk, since a mismatch here (e.g., a twice-weekly cadence paired with mostly spike-class sources) would mean the system structurally under-serves that theme regardless of how good the ranking logic is.

#### 6.2 Cross-day dedupe: identity, not text-match

**Dedupe key concept:** topic identity should be a normalized semantic fingerprint — a stable reference to the real-world thing being discussed ("concept: AI coding-agent context-window limitations debate," "entity: [Product X] launch") — not a raw text match, because the same real event surfaces with different headlines/phrasing each day. Two raw items referring to the same real-world referent share a dedupe key regardless of exact wording. **ASSUMED INPUT (from B2):** whether the collection layer already tags items with any entity/topic identifier ranking could reuse, or whether this semantic clustering must be built fresh from raw text (likely requiring an embedding- or LLM-assisted clustering step — a cost/architecture question for coordination with the state/ledger design, not resolved here).

**"Same topic 4 days running" — the actual decision matrix.** This is not a simple duplicate-suppress rule nor a simple always-refresh rule. It depends on three things tracked per topic-cluster key: trajectory (attention rising / flat / declining day over day), prior-pack state (never generated / drafted / approved / published on this cluster), and whether the underlying discourse has materially changed (new development, new counter-take, or an identical rehash).

| Trajectory | Prior-pack state | Outcome |
|---|---|---|
| Rising | Never generated | Normal candidate, ranks fresh — this is just ordinary discovery lag, not a duplicate |
| Rising/sustained | Already generated (drafted or later) | Resurgence candidate **only if** a new angle/development is detectable (LLM judgment: "what changed since last time?"); if yes, re-surface explicitly tagged "revisit: new angle"; if no, suppress — this is exactly the "nothing to add" criterion from §3 |
| Declining | Never generated | Ranks normally; freshness sub-score is already falling per the decay curve, usually falls below threshold without a special rule needed |
| Declining | Already generated | Suppress permanently — duplicate with no new value |

**Worked example:** a coding-agent context-window debate trends on Hacker News day 1 (rising, never generated — ranks, generates an en pack). It resurfaces on X day 3 with a named practitioner's counter-argument (rising/sustained, already generated, but a new angle exists — re-surfaces tagged "revisit"). It appears again on Reddit day 4 as accumulating ICP complaints with no new argument, just more of the same complaints already captured (declining relative to day 3's novelty, already generated, no new angle — suppressed). The dedupe/state ledger needed to support this (first-seen, last-seen, day-count, prior-pack status, trajectory samples per cluster key) is a stateful component that belongs with the cron/state-layer design; the *decision logic* for what counts as "new enough to resurface" is this brief's to own and is what's specified above.

#### 6.3 Max items per run

Not a single global magic number. The cap should be config-set per theme and informed by two things: downstream human review capacity (how many topics a solo operator can realistically judge per run — coordinate with the operator-review design's stated target of roughly five topics in under thirty minutes) and cost control (each passing candidate consumes downstream LLM/media budget). Recommended structure: the cap applies to **top-N passing candidates per language, per run**, applied *after* ranking and filtering — not a cap on raw signal volume, which should be left cheap and effectively unbounded at collection time. A companion rule: if fewer than N candidates clear the hard-skip threshold on a given run (a slow news day, or cold start), that is correct behavior — the system must never lower the threshold to manufacture volume up to the cap. This directly serves the north-star instruction to optimize for engagement quality and pipeline, not vanity post counts, and is a second concrete backstop (alongside §4) against the threshold quietly drifting to hit a quota.

#### 6.4 Poison-pill handling

**Manipulated/inorganic virality.** Detection is partly statistical (an engagement count wildly out of family compared to that source's own recent baseline, or unnaturally uniform/bot-like timing patterns — requires the source to expose enough history, **ASSUMED INPUT (from B2)**) and partly an LLM sanity check on the content itself (near-identical phrasing repeated across many "independent" accounts is a coordination tell). Detected manipulation is a hard veto on the virality sub-score (forced to the lowest band, not merely discounted), and — importantly — logged distinctly from an ordinary low-virality skip, so the operator can see "flagged as suspicious" rather than mistaking it for "just not popular."

**Spam / low-effort content riding real keywords.** Scam accounts hijacking "AI" keywords, fake course/job scams. Rule-based blocklist patterns (configured per theme) as a fast pass, plus LLM content-quality judgment as a secondary check.

**Prompt-injection-in-content.** Raw collected text (a tweet, a post, a page body) may itself contain adversarial instructions aimed at any downstream LLM call that later reads it (e.g., text instructing a model to ignore its instructions or take an unintended action). The structural mitigation is a design principle, applied at every LLM call boundary that touches raw collected text: treat all collected text strictly as **quoted external material to analyze**, never as instructions, with the system/instruction layer kept structurally separate and privileged. Within the negative-criteria checks specifically, a raw item containing injection-style phrasing should itself be treated as a detection signal — at minimum, evidence of a low-quality or manipulated source item, and grounds for a veto rather than pass-through. This brief owns the detection-at-scoring-time behavior; the broader input-sanitization architecture (how raw artifacts are stored and later re-read) is a cross-cutting concern coordinating with the extraction/storage and text-pipeline designs, flagged here rather than solved here.

#### 6.5 Cold-start behavior, day one, thin sources

Given F-1 (Reddit access likely delayed) and F-9 (scraping pessimism generally), a realistic day-one source roster is thin — plausibly just search-demand signals, tech-news/launch hubs, and manually operator-supplied topics. Consequences for ranking, stated as explicit design commitments:

- With few independent sources online, the corroboration bonus (§2.2) will rarely fire — expected, not a defect. The confidence/availability weight should simply reflect this honestly (a lower attainable ceiling on the composite score, not a broken scorer), and the operator-facing label should say "evidence base: thin (1 source)" rather than let a modest score be misread as a modest topic when it's really a modest evidence base.
- **The hard-skip brand-fit threshold and the veto list must never be relaxed to compensate for thin volume.** This is precisely the moment a system under pressure to "produce something" would be tempted to loosen the anti-forced-placement gate — the design commitment is that a run producing zero or very few passing candidates on day one is a correct, expected outcome to show the operator, not a failure to hide.
- An explicit **operator-seeded topic** input path should exist for cold start — letting a human add a topic/angle they already know is relevant (drawing on existing brand/GTM material) — but that seeded topic still passes through the identical brand-fit and negative-criteria checks as any automatically discovered one. Humans do not get a shortcut around the honest-connection test either; this keeps the anti-forced-placement guarantee consistent regardless of where a topic came from.
- Cold start is a **data-availability state**, not a separate code path. As more sources come online over subsequent weeks (e.g., Reddit access resolved), the same scoring mechanics apply unchanged — this is stated as a design invariant so "cold start mode" is never implemented as a different, looser ranking logic that later needs to be torn out.

---

### 7. Score calibration and drift — the feedback-loop phase

#### 7.1 What counts as feedback

Every operator decision on a candidate — approve a pack, reject a topic outright, reject one specific asset but keep others, request regeneration, or let a candidate silently expire unreviewed — is a labeled data point: the full scorecard (all sub-scores, rationale, sources, ranking-config version) paired with the human outcome. Over a rolling window this becomes a small, genuinely useful calibration dataset.

#### 7.2 Reason-coded rejection is required, not optional

An operator might reject a topic for reasons that have nothing to do with whether the ranking was correct — "too much content this week already," "just not my taste today," "the drafted copy was weak, not the topic." Without a reason code attached to rejections, naive feedback would conflate genuine scoring errors with unrelated human variance, and any calibration built on it would drift for the wrong reasons. The design requires at minimum a small reason taxonomy at rejection time (illustrative, not exhaustive): brand-fit was actually wrong, timing/redundant with recent output, subjective/format preference, downstream copy quality unrelated to topic choice. Only "brand-fit was actually wrong" and similar ranking-relevant reasons should feed weight/threshold calibration; the rest are useful operationally but should not move the scoring logic.

#### 7.3 Two feedback mechanisms, kept structurally separate

1. **Manual, periodic review (the recommended primary mechanism, at least through the initial phases).** On a set cadence (e.g., monthly), produce a calibration report: which sub-score dimension best predicted approval vs rejection; which negative criteria produced false positives (good topics wrongly skipped) or false negatives (bad topics that slipped through and were only caught by the human downstream); drift signals such as a previously reliable source's items increasingly getting rejected (source quality degrading) or a competitor now saturating a topic area the negative-criteria list doesn't yet recognize. A human then explicitly adjusts weights, thresholds, or the negative-criteria rules list based on this report. The automated system produces a recommendation; a human moves the actual numbers.
2. **Automatic/structural recalibration (a later-phase, opt-in idea, not a default — flagged as an open decision, not a recommendation).** It is technically possible to let accumulated approve/reject statistics nudge sub-score weights automatically (a lightweight statistical recalibration). This brief recommends **against** enabling this by default: approval is an imperfect proxy for actual business outcome (approving something fast because it was easy to review is not the same as it being a good ranking decision, and the ranking system cannot observe downstream pipeline/engagement results on its own), and an unaudited automatic loop risks optimizing for whatever gets rubber-stamped quickly rather than for the stated north star of clients/engagement quality/pipeline. If this is ever enabled, it should still require periodic human audit of what it changed and why.

The eventual better ground truth — did the resulting published content actually drive engagement/pipeline — sits outside ranking's own visibility (it lives with whatever tracks published-content performance, likely via the publishing/analytics layer) and should be correlated back into the periodic calibration report when available, rather than substituted by approval alone.

#### 7.4 Versioning and governance

Every change to weights, thresholds, or the negative-criteria rules list should be dated and versioned, so a given candidate's score is explainable relative to the exact ranking logic active when it was produced (this is why §2.5's scorecard carries a ranking-config version). Because calibration touches the exact same numbers that prevent forced product placement, any proposed loosening of the brand-fit hard-skip floor in particular should require an explicit, logged human rationale — not simply "we had too few passing candidates lately." This is a deliberate governance rule, not a technical control: it exists specifically to block the failure mode where thresholds quietly relax over months to hit a volume target instead of a quality bar, which is the same failure the assignment's "never force product spam onto unrelated trends" instruction is guarding against in the first place.

---

### 8. Decision table

| Decisions this brief unblocks | Architecture area |
|---|---|
| Multiplicative composite (virality × confidence × freshness × brand-fit) with brand-fit as a pre-composite hard floor | Ranking/scoring component design; spin-stage input contract (only passed candidates are visible to spin) |
| Per-candidate inspectable scorecard: sub-scores + bands + one-line rationale + evidence-quality label + ranking-config version | Pack/scorecard content; operator review package (coordinate with C4's presentation layer) |
| Seven-category negative brand-fit taxonomy with rule-vs-LLM detection split and hard-veto vs score-penalty distinction | Brand-fit judgment component; theme config's negative-criteria/excludes block |
| Anti-forced-placement mechanisms (a)–(g): pre-spin filtering, binary veto list outside the average, falsifiable honest-connection verdict, fail-closed on judgment-step failure | Ranking-to-spin data flow; failure-handling policy for the brand-fit judgment step |
| Per-language fit as a first-class parallel decision (generate/skip/hold per language, not translate-after-rank) | Ranking output contract; downstream per-language spin/content routing |
| Freshness signal-class taxonomy (Spike/Rising/Launch-hype/Evergreen-pain) with differentiated decay, read relative to run cadence | Freshness scoring; cadence-vs-decay-mismatch warning surfaced to operator |
| Cross-day dedupe as (semantic cluster key + trajectory + prior-pack-state), not simple same-day text match | Dedupe/state ledger design (coordinate with cron/state-layer ownership); resurgence-tagging logic |
| Max-items-per-run applied post-filter (top-N passing candidates per language), never by lowering the threshold to hit the cap | Run-budget/cost-control design (coordinate with provider unit-economics and operator review-capacity findings) |
| Poison-pill vetoes (manipulated virality, spam, prompt-injection-in-content) as named checks within the negative-criteria/veto path | Safety layer within scoring; coordinates with raw-artifact storage/handling design |
| Cold-start behavior: no threshold relaxation ever, operator-seeded topics pass identical gates, thin evidence labeled honestly and distinctly from poor fit | Day-one operational behavior; theme onboarding expectations |
| Feedback loop: reason-coded rejections, human-reviewed periodic calibration, versioned thresholds; automatic weight updates explicitly not the default | Calibration/governance process; minimal state need (version history of weights/thresholds/rules) |

| Decisions this brief defers | Open decision |
|---|---|
| Exact numeric values (0.35 brand-fit floor, decay half-lives per class, top-N cap size, corroboration bonus magnitude) | Needs empirical tuning once real source data and operator feedback exist; this brief supplies directional defaults only |
| Whether a cs-only or en-only "hold" list (thin-evidence, not-yet-decided candidates) is worth building for v1 or deferred to a later phase | Product-scope decision |
| Where the semantic topic-clustering/dedupe-key computation technically lives (embedding similarity vs LLM call vs simpler heuristic) | Depends on stack decision (D-06) and per-run cost tolerance; better resolved jointly with the extraction-methods and cron/state-layer designs |
| Whether automatic (non-human-gated) threshold recalibration is ever enabled, and under what audit governance | Left open, later-phase question, not decided here |
| Sourcing the eventual ground-truth "did this actually drive pipeline" signal into calibration (e.g., from published-content/platform analytics) | Owned by whoever designs the publishing/analytics feedback path, out of this brief's scope |
| Precise per-source freshness half-lives and per-source structural confidence tiers | Depend on B2's real field-availability findings (see the consolidated ASSUMED INPUT list, §2.7) |
| How claim-safety verification is technically invoked from the legal/claim-risk negative criterion | Coordinate with the brand-truth/claim-safety design that owns that substrate |

---

### 9. Fact ledger

| Claim | Source | Date | Confidence | Recheck-by |
|---|---|---|---|---|
| Multiplicative composition of heterogeneous sub-scores prevents a single dominant factor from overriding a near-zero factor, unlike additive weighted sums | Expertise (standard multi-criteria scoring practice) | 2026-08-06 | High (general methodology, not source-specific) | Not time-sensitive |
| Google Trends exposes a normalized 0–100 relative index rather than raw search-volume counts | Expertise / general knowledge of the product, not independently re-verified here | 2026-08-06 | Medium — **ASSUMED INPUT, verify against B1/B2's actual findings** | Recheck against B1/B2 briefs at Wave 2 synthesis |
| Reddit and X access for research reads are both constrained (Reddit ToS/OAuth friction; X free-tier read access effectively unavailable) | Carried forward from masterplan flags F-1/D-08, not independently re-verified in this brief | 2026-08-06 | Medium — inherited assumption | Recheck against B1's source-access findings |
| Decay half-lives given per signal class (12–24h spike, 2–4 day rising, 3–7 day launch-hype, 2–4 week evergreen-pain) | Expertise — directional heuristic derived from general social/media attention-decay patterns, not measured against this system's actual sources | 2026-08-06 | Low-medium — explicitly a calibration starting point, not an empirical finding | Recheck after first month of real run data (per §7's calibration cadence) |
| A 0.35 brand-fit hard-skip floor is a reasonable default starting threshold | Expertise — arbitrary but principled starting point (roughly "more miss than hit" on a 0–1 honest-connection judgment) | 2026-08-06 | Low — explicitly flagged as needing empirical tuning | Recheck after first calibration cycle |
| Prompt-injection embedded in third-party collected text is a realistic risk to any downstream LLM call that reads that text unmodified | Expertise — general LLM-security domain knowledge, not specific to any named source in this system | 2026-08-06 | High (general security principle) | Not time-sensitive, but re-verify specific mitigation mechanics against final text-pipeline design |
| HypeLead's configured ICP includes marketing/lead-gen/AI/PPC/appointment-setter agencies, B2B marketing and sales leadership, automation/outreach-interested individuals, startups, and GTM/lead-gen roles | `docs/marketing/HypeLead Areas GTM_Marketing_Strategie.txt` (repo-provided brand material) | 2026-08-06 | High (primary source document, direct read) | Recheck if theme config's ICP definition is later formalized differently |

---

### 10. Sources

- `HypeAgentSocials_InstructionsAssignment.md` (repo) — assignment text, Block B items 5 and 7, List A ranking intent, north-star and mode/safety constraints. Read in full for this brief.
- `docs/plans/DESIGN_PHASE_MASTERPLAN.md` (repo) — locked decisions D-01–D-08, research flags F-1–F-9, Wave 1 task assignment and coordination boundaries (T5/T6/T7/T8/T9/T11/T12/T13/T14 ownership lines referenced throughout this brief).
- `docs/marketing/HypeLead Areas GTM_Marketing_Strategie.txt` (repo) — HypeLead's own ICP segments, used to ground the worked examples and off-ICP-mismatch criterion in real configured audiences rather than generic assumptions.
- Expertise-derived content (marked inline and in the fact ledger): multi-criteria scoring composition practice (multiplicative vs additive gating), attention-decay heuristics by content-event type, prompt-injection-as-untrusted-data mitigation principle, human-in-the-loop calibration and reason-coding practice for feedback loops. No web access was used for this brief; all such claims are durable methodology, not source-specific facts, and are flagged for reconciliation against the web-researched B1/B2/B4 briefs at Wave 2 synthesis.
