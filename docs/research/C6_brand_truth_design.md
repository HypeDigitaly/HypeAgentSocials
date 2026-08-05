# C6 — Brand-truth resolution, confidence, claim safety, and spin application (design)

*Wave 1 · T14 · Stage 3 topic 3 (design half) · expertise brief · 2026-08-06*
*Owner boundary: C1 owns the Notion/Postiz **tool-surface facts** (auth model, rate limits, what is actually retrievable). This brief owns the **resolution, verification and enforcement design** that sits on top of whatever tool surface C1 lands on. Every dependency on C1 is marked **ASSUMED INPUT (from C1)**.*
*Method: durable AI-systems and content-governance practice, cross-checked against two real local artifacts — the brand's own Czech GTM/ICP strategy and the brand's own GTM playbook. No web access; volatile external claims are flagged for verification.*

---

## 1. What this means for the operator

The system will never be allowed to guess what your company sells, what it costs, or what it has achieved. Before it writes anything, it goes and looks: first at your Notion knowledge base, then at the theme's own configuration file, then at your live public pages (hypelead.ai, hypedigitaly.ai) to check that the commercially important things still match. It writes down what it found, timestamps it, and hashes it, so that months later you can open any published pack and answer the question "what did the machine believe when it wrote this?"

Three practical consequences for your day.

**One: the machine can refuse to do brand content, and that is a feature.** If Notion is unreachable at 3 a.m., or your site says the trial is 14 days while Notion says 7, the unattended run does not pick a winner and carry on. It finishes the research half of its job — topics found, ranked, saved — and skips the brand half. You get a run that says, in one line at the top of the digest: *"I researched 7 topics but wrote no brand content. Reason: the site and Notion disagree about the trial length. Fix that and re-run the spin step; the research is already done and won't be re-paid for."* Nothing is wasted, nothing is invented, no media money is spent. A price disagreement is treated as an alarm, not as a tie to be broken — if two of your own sources disagree about a number, the honest conclusion is that we don't currently know that number.

**Two: everything the machine writes gets frisked for claims before it goes in the pack.** A separate pass reads the finished copy — post bodies, captions, carousel slides, on-image text, video scripts — and pulls out every number, every currency amount, every percentage, every company or person name, every superlative, every "we got X result" sentence. Each one has to match something on your approved-claims list. Anything that doesn't match blocks that asset: it gets rewritten up to a small fixed number of attempts, then either downgraded to a safe version without the claim, or dropped and reported. It never quietly ships. Note the subtle case this catches with no number involved at all: your own material says HypeLead "finds people who just showed a buying signal and drafts your first message — you approve and send; it does not send on its own." A post claiming it "sends for you" would be false without containing a single digit. That class of claim is checked too.

**Three: your competitor-post folder is a voice reference, never a fact source.** The winning-posts file and the GojiBerry playbook are full of other people's numbers — "12 demos in 5 days", "25-40% response rate", "added 7 figures in Q1", "Guaranteed". Those are the single most likely things to leak into your copy, because the model is being shown them as examples of good writing. The design walls them off: style in, facts never. Your own GTM playbook already does this manually — it tags every GojiBerry number as *their* claim with a different visual marker. The system formalises that same instinct.

For spoken video, the recommendation is simple: the voice only ever says text that has already passed the claim check, and in unattended runs the spoken lines are not allowed to carry numbers or claims at all — those go into the on-screen text, which we render ourselves and can re-read. Transcribing the finished audio to check it afterwards is used as a periodic audit of whether the video model actually says what it was told, not as the gate. Checking after the money is spent is the wrong place to find out.

---

## 2. Scope, assumed inputs, and the working vocabulary

### 2.1 Assumed inputs

| ID | Assumption | Owner | If it turns out false |
|----|-----------|-------|----------------------|
| AI-1 | The Notion KB about HypeDigitaly + projects exists and is MCP-connectable | **FRESH FACT** (W0.5 intake, DECISION_LOG OD-6) | n/a — confirmed |
| AI-2 | Notion is readable non-interactively in an unattended run (token model, MCP-vs-REST split per OD-4) | **ASSUMED INPUT (from C1)** | The offline-snapshot path (§6) becomes the *normal* unattended path, not the exception; expect most cron runs at MINIMAL band → research-only far more often than designed for. This is the single biggest design risk in this brief |
| AI-3 | Notion structure can express per-fact records (a page or database row per offer/claim/CTA) rather than only free prose | **ASSUMED INPUT (from C1)** | Resolution needs an extraction step from prose, which lowers per-fact confidence by one level across the board and makes conflict detection unreliable → recommend the theme config becomes primary for the commercially binding classes |
| AI-4 | Notion rate limits allow a per-run pull of the whole brand-fact set | **ASSUMED INPUT (from C1)** | Cadence in §5 shifts from per-run to a longer TTL with snapshot reuse |
| AI-5 | A candidate brand-fact taxonomy (offers, ICP map, approved-claim allowlist, CTA set, pricing policy, proof/case allowlist, voice rules, hard excludes) is being stated by C1 | **ASSUMED INPUT (from C1)** | §3 states an independent working taxonomy that supersets it; W2 reconciles |
| AI-6 | Ranked topics arrive carrying an inspectable pain/category signal and a brand-fit sub-score | **ASSUMED INPUT (from T7/B3)** | The pain→offer mapper in §9 needs its own classification step, adding one LLM call per topic |
| AI-7 | A run/state store exists that can hold append-only snapshots and per-pack metadata | **ASSUMED INPUT (from T11/C3)** | Snapshots fall back to files beside the pack; recall-by-fact (§6.3) becomes a manual grep |
| AI-8 | The anti-slop voice gate, its rubrics, and its bounded-regenerate loop exist as a separate layer | **ASSUMED INPUT (from T13/C5)** | The spin gate in §9.4 would have to absorb voice checks, which is a bad merge — argued in §9.5 |
| AI-9 | Legal analysis of comparative advertising, AI-content labelling (F-8), and affiliate disclosure | **ASSUMED INPUT (from T15/C7)** | The check classes in §7 exist regardless; only their *mandatory* status and exact required wording depend on C7 |
| AI-10 | Czech ASR quality on marketing audio with anglicisms/brand names is materially weaker than English (F-5/F-7) | expertise, **needs web verification** | Weakens one of four arguments for script-lock; the recommendation in §8 survives on the other three |

### 2.2 Nouns proposed here (T16 canonicalises later)

**brand-fact** (one atomic resolved fact with a source, a timestamp and a confidence) · **fact class** (the ~13 groups in §3) · **fact tier** (blocking / constraining / enriching) · **claim ledger** (the approved-claim allowlist plus its provenance and validity metadata) · **brand-truth snapshot** (the frozen, hashed fact set used by a run) · **confidence band** (FULL / PARTIAL / MINIMAL / INSUFFICIENT) · **red-flag conflict** (a disagreement that stops rather than tie-breaks) · **fact-usage trace** (which fact IDs a given pack actually consumed) · **spin gate** (the good-vs-bad-spin enforcement point) · **claim check** (the extraction-and-verification pass over generated copy).

---

## 3. Required vs optional brand facts

### 3.1 The binary is wrong — there are three tiers

"Required vs optional" hides the dangerous middle. A fact is **blocking** if content cannot be generated without inventing something. A fact is **enriching** if its absence only lowers quality. But there is a third group — **constraining** facts — whose absence does not block generation and does not lower quality in any way the model can perceive, and which therefore *silently invites fabrication*. Proof points and approved claims are the canonical example: with no case studies loaded, nothing stops a generator from writing a plausible-sounding result sentence. It has no way to know it was supposed to be sad about the gap.

The design consequence is the most important single rule in this brief:

> **Missing is not the same as empty.** Every constraining fact class must be resolved to an explicit state — *resolved-with-values*, *resolved-empty*, or *unresolved*. "Resolved-empty" is a first-class, safe, generative state: the generator is told "you have zero approved proof points, write teaching-led content." "Unresolved" is a failure state: we don't know whether proof exists, so we behave as if claims are forbidden **and** we lower the confidence band, because we also cannot trust the excludes list that lives beside it.

### 3.2 Working taxonomy

Tier column: **B** = blocking, **C** = constraining, **E** = enriching. "Resolved-empty OK" means the class may legitimately be empty as long as it was *checked*.

| # | Fact class | Tier | Contents | Resolved-empty OK | Why this tier |
|---|-----------|------|----------|-------------------|---------------|
| F-A | **Identity & entities** | B | Legal entity, brand names, which brand owns which domain, spokespeople and their roles | No | Every asset carries identity; getting it wrong is unrecoverable |
| F-B | **Offer catalogue** | B | Named offers, one-line what-it-is, **status** (live / beta / planned / retired), owning brand, canonical destination URL | No | Cannot spin toward an offer that may not exist |
| F-C | **Capability statements (positive *and* negative)** | B | What each offer does today, and explicitly **what it does not do** | No | The anti-overclaim spine. See §3.4 |
| F-D | **ICP map** | B | Segments, segment type, their pains, language, platform | No (≥1 segment) | "Who is this for" is an input to every generation step |
| F-E | **CTA set** | B | Allowed CTA classes per offer × platform × language, literal phrasing per language, destination URL | No | A CTA is a promise; an unresolved CTA set means promising blind |
| F-F | **Pricing policy** | B | The *rule* (e.g. "never state prices in social; link to the pricing page"), plus trial terms if any | No | The policy is required even when prices are not. Prices themselves are C |
| F-G | **Price values & commercial terms** | C | Actual prices, plan contents, trial length, guarantees, discount/affiliate terms | Yes | Absence just means "link, don't quote". Presence demands corroboration (§4) |
| F-H | **Claim ledger (approved-claim allowlist)** | C | Per-entry: text per language, claim type, **provenance**, evidence pointer, valid-from/valid-until, usage scope | Yes | Empty ledger = no-proof mode, which is publishable. Unresolved ledger = stop (§5.4) |
| F-I | **Proof / case allowlist** | C | Case studies, client names + permission status + permission expiry, metrics + evidence | Yes | Same logic; permission status is what makes it dangerous, not the metric |
| F-J | **Hard excludes** | B | Forbidden topics, forbidden framings, banned claim types, do-not-mention clients/competitors | Yes (empty ≠ unknown) | You cannot enforce "never say X" if you do not know X. Unresolved excludes is a hard stop |
| F-K | **Product rules** | B *if blog/site-first enabled*, else E | Site-first offers, atomisation order, per-language page availability | Yes | Determines whether social assets may exist before the article does (§9.3) |
| F-L | **Voice rules + exemplar-corpus pointer** | E | Tone rules, banned phrasing, curated winning-post corpus reference | Yes | The voice gate has its own defaults; the corpus improves quality only |
| F-M | **Visual brand baseline** | E | Logo usage, palette, on-image text rules | Yes | Degrades to unbranded plans |
| F-N | **Compliance obligations** | B (policy) | Entity disclosure, affiliate disclosure requirement, AI-content labelling obligation | No | These add *required* text; see §7.2 class 10 (**ASSUMED INPUT from C7** for their exact legal status) |

**Required set for content generation** = all B rows resolved, non-conflicted, not hard-stale, in the language being generated. **Optional enrichment** = E rows. **Constraining** = C rows, which never block but bound what may be said.

### 3.3 Cross-check against the real ICP segments

Reading the brand's own Czech GTM strategy against this taxonomy produced four corrections I would not have made from a generic template.

**(a) ICP entries need a segment *type*, because spin risk differs by type.** The real segment list mixes three kinds:
- *Firmographic*: agencies — and notably **sub-typed** (marketing, web design, UGC, lead-gen, SMMA, AI agencies, PPC, appointment setters), plus startups.
- *Role-based*: B2B marketing, sales / commercial directors, "LinkedIn expert", GTM / lead-gen people.
- *Technographic*: **"firms using Instantly.ai / Lemlist / Prospeo"**, and "people interested in automation / outreach / AI".

The technographic segment is the important one. It is *defined by a competitor's product*, which means natural, well-targeted content for that segment will name third-party tools. A naive claim checker that blocks all company names would block the brand's best-fitting content; a naive one that allows all company names would let comparative performance claims through. So the entity check must be four-way, not binary (§7.2 class 3), and comparative claims get their own class with their own evidence requirement.

**(b) The CTA set is richer and riskier than the assignment's default.** The assignment's default soft CTAs are audit / product page / demo. The real strategy uses: free trial ("free trial, we want your opinion"), **free webinar with a specific title**, demo, free guide / lead magnet, and an **affiliate arrangement with a stated 20% recurring share plus a discount code**. These are not interchangeable. A webinar CTA is a promise that a dated event exists; an affiliate CTA carries a disclosure obligation and a hard number (20%). Hence CTA classes with *preconditions on brand facts* (§9.2) rather than one flat CTA list.

**(c) Two brands, two domains, one engine.** The strategy explicitly runs SEO articles on both hypedigitaly.ai and hypelead.ai, and the GTM playbook draws the line: *hypelead.ai = the product; hypedigitaly.ai = broader sales/AI help for agencies*. So brand-routing is a resolved fact, and "CTA points at the wrong domain for the offer being discussed" is a real, checkable defect class.

**(d) Named humans are brand facts.** The strategy names Pavel Čermák, Erik Čermák, Miroslava Čermáková as the people who post and amplify. A person allowlist is therefore required — otherwise the name checker either flags the founders in every post (and gets switched off) or is too loose to catch an invented customer name.

### 3.4 Why negative capability statements are blocking, not enriching

The brand's own GTM playbook contains this line, in both languages: *"Say what HypeLead really does today: it finds people with buying signals and drafts your first message. You approve and send. It does not send on its own."*

That sentence is a fact with two halves, and the second half is the one that prevents the highest-frequency overclaim in this category — autonomy inflation ("runs your outbound on autopilot", "sends for you", "24/7 SDR"). Note that the competitor corpus in the same folder is *saturated* with exactly that framing ("a LinkedIn SDR that runs 24/7", "killed manual prospecting", "while I focus on other tasks"). Voice-imitating the corpus and drifting into its capability claims is a single short step. A claim checker that only looks at numbers will never catch it. Therefore: every offer's fact record carries a *does-not* list, and capability claims are a named check class (§7.2 class 6).

One honesty flag: that capability line comes from a *planning* document. **A plan is not brand truth.** Notion will contain roadmap pages, drafts, and aspirations sitting next to fact pages. This is the most likely source of a false "we do X" claim in this specific deployment, and it is not something confidence scoring catches, because a roadmap page is fresh, well-written and internally consistent. Mitigation is structural, not statistical: fact resolution must read only from designated fact locations (**ASSUMED INPUT from C1** on how those are designated in the actual Notion workspace), and any offer whose status is not explicitly `live` may not be spun toward at all. If C1 finds that the workspace cannot cleanly separate plan from fact, that is an escalation to the operator, not something to paper over.

---

## 4. Precedence design

### 4.1 There is no single precedence order

D-03 locks the *default* order (Notion → theme config → live site). That default is right for internal knowledge and wrong for commercially binding facts, because the live site is the thing a prospect can actually read. Precedence is therefore per fact class.

| Fact class | Primary | Secondary | Verifier | Disagreement outcome |
|-----------|---------|-----------|----------|---------------------|
| F-A identity, entities, people | Notion | config | site (public-facing usage) | Degrade to the intersection; flag |
| F-B offer catalogue & **status** | Notion | config | **site (binding)** | **Red flag** if site shows retired/404 while Notion says live |
| F-C capability statements | Notion | config | site (must not contradict) | Degrade to the *narrower* wording; flag |
| F-D ICP map | Notion | config | — | Resolvable; internal facts, low external risk |
| F-E CTA set (which CTA) | config | Notion | — | Resolvable |
| F-E CTA destination (URL liveness) | — | — | **site wins absolutely** | A 404 kills that CTA whatever Notion says |
| F-F pricing policy | config | Notion | — | Take the stricter policy |
| F-G price values, trial terms, guarantees | **site (binding)** | Notion | — | **Red flag — never tie-break** |
| F-H claim ledger | Notion (+config-declared) | — | site may **invalidate**, never **add** | Contradiction → quarantine that entry |
| F-I proof / case allowlist + permissions | Notion | — | — | Missing permission = unusable; no precedence question |
| F-J hard excludes | **union of all sources** | — | — | Never resolvable downward; excludes are monotonic |
| F-K product rules | config | Notion | site (page existence) | Degrade to the safer rule (hold social until the article exists) |
| F-L voice rules, exemplar corpus | **config** | Notion | — | Config wins; it is a design artefact of this system, not a business fact |
| F-M visual baseline | config | Notion | site | Resolvable |
| F-N compliance obligations | config policy | Notion | — | Take the stricter |

Three asymmetries are load-bearing:

- **Excludes are monotonic.** Any source that says "never say X" wins permanently for this run. No precedence rule may *remove* an exclusion. Otherwise a stale config could re-enable a topic the operator banned in Notion yesterday.
- **The site can subtract but not add.** If hypelead.ai no longer mentions a feature, that invalidates a capability claim. But marketing copy on our own site is not evidence *for* a claim — otherwise the system would bootstrap its own puffery into an approved claim, and any hallucination that ever reached the site becomes permanent truth.
- **Silence is not agreement, and unreadable is not disagreement.** A source that does not mention a fact reduces corroboration (lowering confidence) but never creates a conflict. A *failed fetch* (site down, anti-bot, timeout) must be recorded as "not observed", never as "site disagrees". Collapsing these two is how a flaky network turns into a false red flag and trains the operator to ignore alarms.

### 4.2 Three conflict outcomes

**Resolvable** — different granularity, wording, formatting; one source silent; staleness within tolerance. Apply precedence, record which source won, move on.

**Degrade** — the sources say compatible-but-different things about a soft fact (capability wording, ICP phrasing, tone). Take the *weaker, narrower* statement, mark the fact PARTIAL, continue. Rule of thumb: when two of your own sources describe your product differently, publish the smaller promise.

**Red flag / stop** — no tie-break permitted. Triggers:
1. Any disagreement inside the commercially binding set: price, trial length, plan/package contents, guarantee terms, discount/affiliate terms.
2. Offer availability disagreement (site 404 / "discontinued" vs Notion "live").
3. A claim-ledger entry contradicted by the live site.
4. A client name in the proof allowlist whose permission status is absent or expired, but which appears as usable elsewhere.
5. Two sources giving different *values* for the same case metric.

Effect: the fact is quarantined (unusable, not silently replaced), every asset depending on it is blocked, and the conflict is surfaced verbatim — both values, both sources, both timestamps. If the quarantined fact is Tier-B, the band collapses to INSUFFICIENT and the unattended degrade fires (§5.4).

**Why a price conflict is a red flag and not a tie-break:** tie-breaking means choosing which of two possibly-wrong numbers to publish to the market. The expected cost of publishing a wrong price (a commercial promise, potentially a consumer-protection matter, certainly a trust event with a prospect who read the other number on the site an hour earlier) is orders of magnitude above the cost of not posting today. There is no scoring function where that trade comes out in favour of guessing. The correct output of "our two systems of record disagree about our price" is *an alert to a human*, and it is a useful alert — it means the operator's own house is out of sync, which is worth knowing independently of this pipeline.

### 4.3 Human run overrides — bounded, not supreme

The assignment allows human run overrides as a spin input. Unbounded, they are a hallucination-laundering channel: anything typed on the command line becomes "truth" with no source and no timestamp. Bounded design:

- Overrides may **narrow**: force a specific topic, suppress an offer, force one of the already-approved CTAs, restrict to one language, lower the confidence ceiling.
- Overrides may **not create commercial facts**: no new price, claim, client name, case metric or capability. In unattended mode this is absolute.
- In interactive mode, an operator who wants to introduce a new commercial fact is directed to write it into the claim ledger (with provenance, evidence pointer and validity window) — the same path, with the same audit trail, as any other fact. A one-run inline fact is refused. Friction here is the point.
- Every override is recorded in the snapshot as a source of its own, so a pack can be traced to "the human said so on this date".

---

## 5. Confidence measurement design

### 5.1 Which facts count

Tier-B and Tier-C classes count. Tier-E never affects the band — otherwise a missing tone example could stop a run, which is absurd and teaches operators to ignore the band. The band is computed **per (theme, language)** pair, not per theme: a Czech pack can be blocked while the English pack proceeds, which is a direct consequence of D-02 (every language is a first-class output set, not a translation).

Each brand-fact carries four inputs to its own confidence:
1. **Resolution state** — resolved / resolved-empty / unresolved / conflicted (conflicted contributes zero and quarantines).
2. **Corroboration depth** — how many independent sources agree (Notion, config, site). Two independent agreeing sources is the practical ceiling; one is normal; zero means it came from a snapshot only.
3. **Freshness** — age of the newest supporting observation against that class's thresholds.
4. **Source authority for that class** — per the §4.1 table; a fact resolved only from a non-authoritative source for its class is capped.

### 5.2 Freshness thresholds per fact class

Two boundaries per class: **stale-warn** (usable, visibly marked in the pack) and **hard-stale** (treated as unresolved for band purposes — never silently used). Values below are expertise-derived starting points, and all of them should be theme-configurable.

| Fact class | Stale-warn | Hard-stale | Reasoning |
|-----------|-----------|-----------|-----------|
| F-G price values, trial terms, guarantees | 7 days | 14 days | Highest consequence, cheapest to re-check (one page fetch) |
| F-E CTA destination liveness | 7 days | 14 days | Cheap check, and a 404 CTA burns a real prospect |
| F-B offer catalogue & status | 14 days | 30 days | Status changes are infrequent but decisive |
| F-C capability statements | 30 days | 90 days | Product reality moves slower than pricing |
| F-H claim-ledger entries | per-entry `valid-until` (mandatory) | 90 days global review | Time-bound claims are the norm ("last quarter we…") |
| F-I proof / case entries + permissions | 90 days | per-entry permission expiry | Client permission drifts; expiry is contractual, not statistical |
| F-D ICP map | 90 days | 180 days | Strategy-level, changes with GTM cycles |
| F-A identity, entities, people | 180 days | 365 days | Rarely changes; a change is huge |
| F-J hard excludes, F-L voice, F-M visual | 180 days | — (config-owned, never hard-stale) | Config is present by definition; staleness is an operator concern |
| F-N compliance obligations | 90 days | 180 days | Regulatory surface is moving (F-8) — **ASSUMED INPUT (from C7)** |

### 5.3 Band computation: gate first, then score

The tempting design is a weighted average of per-fact confidences. It is the wrong shape, and it fails in a specific, predictable way: a run with a beautifully complete ICP map, voice corpus, capability set and excludes list, but **no resolved price policy**, scores 0.91 and proceeds. High scores on many soft facts mask one missing hard fact. So:

**Step 1 — gates (pass/fail, per language).** Every Tier-B class must be *resolved or legitimately resolved-empty*, non-conflicted, and not hard-stale. Any gate failure sets a hard ceiling on the band regardless of everything else, and names itself as the reason.

**Step 2 — score inside the ceiling.** Over Tier-B + Tier-C facts, combine: coverage (fraction resolved), corroboration depth (how many are single-sourced vs corroborated), freshness ratio (how many are inside stale-warn), and conflict count (must be zero to exceed PARTIAL). Round into a band. Deliberately coarse: four bands, no decimals shown to the operator. A number like "brand confidence 0.78" invites arguing with the thermometer; "PARTIAL — proof claims off, prices off" tells the operator what actually changed.

**Step 3 — capabilities follow the band.** This is what makes the bands mean something operationally:

| Band | Precondition | What content may do |
|------|-------------|--------------------|
| **FULL** | All Tier-B gates pass; commercially binding facts corroborated by the live site this run or within stale-warn; zero conflicts; Tier-C mostly resolved | Full spin. All CTA classes (subject to their own preconditions, §9.2). Approved proof claims allowed. Prices/trial terms may be stated if policy permits. Long-form/site-first content allowed |
| **PARTIAL** | All Tier-B gates pass, but corroboration is thin (Notion-only; site check failed or skipped) or some Tier-C is unresolved/stale-warn | Spin allowed. **All proof claims blocked** unless that individual ledger entry is itself FULL. **No prices, no trial terms, no case metrics, no comparative claims.** CTAs limited to zero-commitment + product-page classes. Pack marked |
| **MINIMAL** | Running from an offline snapshot within its validity window, or config-only resolution of Tier-B | Capability-level statements from the snapshot only. **No numbers of any kind.** No proof, no comparisons, no price/trial CTAs. Product-page and content CTAs only. Interactive-only by default; heavily marked |
| **INSUFFICIENT** | Any Tier-B gate fails; or an unresolved red-flag conflict on a binding fact; or the snapshot is expired/unverifiable | **No brand spin at all.** Research-only output |

### 5.4 The exact research-only degrade trigger (D-03)

In **unattended** mode, for the language being generated, the run degrades to research-only if **any** of the following holds:

1. The confidence band is **below PARTIAL** (i.e. MINIMAL or INSUFFICIENT).
2. Any **unresolved red-flag conflict** exists on a Tier-B or commercially binding fact — regardless of band. A conflict is not an average; it does not get diluted by everything that is fine.
3. Brand truth is available **only from an offline snapshot** that is older than the configured max-offline window, or whose integrity/validity check fails.
4. The **claim ledger could not be read at all** (distinct from being empty). Unknown ≠ empty: if we cannot read the ledger we can neither prove a claim is allowed nor trust the excludes that live beside it.
5. **Hard excludes are unresolved** (not empty — unresolved). You cannot enforce "never say X" without knowing X.

Conditions 1 and 3 are band-driven; 2, 4 and 5 are independent stop conditions that bypass scoring entirely.

**Why the threshold is "below PARTIAL" rather than "below FULL".** Requiring FULL for unattended runs would degrade the pipeline every time a site fetch flakes, and a system that cries wolf daily gets its alarms ignored — or gets switched off, which is the real failure. PARTIAL is defined *precisely so that everything dangerous is already switched off at PARTIAL*: no prices, no proof, no metrics, no comparative claims, no commitment CTAs. The band boundary is drawn at the line where fabrication risk lives, so the trigger can be permissive without being unsafe. This is the argument to make to a reviewer: the safety comes from the capability table, not from the threshold's height.

**Interactive mode** applies the same conditions but never silently proceeds: the operator sees the conflict card and may consciously accept MINIMAL (with numbers and proof still blocked by the capability table). The operator may **not** override conditions 2, 4 or 5 — those are about not knowing the rules, not about having thin data.

### 5.5 What the operator sees when it fires

- **A distinct run outcome**, separate from both success and failure, so scheduler monitoring can alert differently ("completed-degraded" — exact exit-code taxonomy is **ASSUMED INPUT from T11/C3**).
- **One plain sentence at the top of the run digest**, in the operator's language, e.g.: *"I researched 7 topics and ranked them, but wrote no brand content — the live site says the trial is 14 days and Notion says 7. Nothing was generated, €0 spent. Fix the mismatch and re-run just the spin step; the research is saved."*
- **A brand-truth panel**: one row per Tier-B class → state (ok / stale / missing / **CONFLICT**), which source was used, the age of the observation, and a *specific* fix action. Not "confidence low" — "Notion page 'Offers' returned unauthorized; the integration token expired on 3 Aug."
- **Both conflicting values shown side by side with their sources and timestamps.** The operator should be able to fix their own systems from this panel without opening anything else.
- **The research output remains complete and reusable** — this is what makes the degrade acceptable to a human. The next run, or an interactive re-run after the fix, spins the same already-paid-for topics. A degrade that throws away the run's work will be engineered around by the operator within a fortnight.
- **Zero media spend, stated explicitly as zero.**
- **Anti-flap rule**: two consecutive degrades for the same reason escalate the notification's prominence rather than repeating an identical low-signal message; an operator-acknowledged known conflict still degrades but notifies quietly. Repetitive identical alerts are how alarms die.

---

## 6. Refresh cadence and the brand-truth snapshot

### 6.1 Cadence

- **Once per run, before anything is spent, and before topic research.** Brand truth first is a deliberate ordering: the degrade decision changes what the rest of the run does, and a research-only run should not have paid for generation before finding out. Within brand-truth resolution, cheapest gates first (config load → snapshot validity → Notion pull → targeted site verification).
- **TTL-guarded re-pull.** If a theme runs several times a day, re-pull only when the cached snapshot is older than the *shortest stale-warn threshold in play* (effectively daily for the binding classes); otherwise reuse the snapshot and record that it was reused. This respects Notion rate limits (**ASSUMED INPUT from C1**).
- **Targeted site verification, not a crawl.** Verify only what needs corroboration: the binding facts (F-G) and CTA URL liveness (F-E). A handful of fetches per run, budgeted and timeboxed, with failures recorded as "not observed". Full-site reading is out of scope and would be fragile.
- **Event-driven refresh triggers** (each forces a full re-pull regardless of TTL): the operator ran theme-readiness validation; the theme config's content hash changed; a human rejected a pack citing a wrong brand fact; a claim check produced a CONTRADICTED verdict (that is evidence the ledger has drifted); a CTA URL returned 404; a new offer status appeared. A Notion change webhook, if one exists, is a nice-to-have — **ASSUMED INPUT (from C1)**, assume absent.
- **Claim-ledger expiry sweep.** Because entries carry `valid-until`, the digest should list "claims expiring in the next 30 days". Otherwise proof silently vanishes from content one day and nobody knows why the posts got vaguer.

### 6.2 Staleness marking

Every fact carries observed-at and source. The snapshot carries resolved-at and the reuse chain. Every pack shows the age of the *oldest Tier-B fact it consumed* — a single honest number the operator can glance at. Stale-warn facts are usable and visible; hard-stale facts are excluded from generation entirely and count as unresolved in the gates.

### 6.3 Brand-truth snapshot per pack

**Contents.** The normalised fact set (value + source + observed-at + per-fact confidence), the computed band and its gate results, all conflicts including quarantined ones, the claim-ledger version, the theme-config version, and the **resolver rule version** (precedence and thresholds change over time; a snapshot without its rule version is not reproducible).

**Hashing.** A content hash over the *canonically ordered, normalised* fact set — hash the semantic content, not the serialisation, or trivial key-order and whitespace churn will manufacture spurious "the brand truth changed" events and destroy the signal.

**Two identifiers, not one.** Record (a) the full snapshot hash, and (b) a **fact-usage trace** — the list of fact IDs and claim-ledger entry IDs this specific pack actually consumed. The hash proves integrity; the trace enables *recall*. The question an operator will genuinely ask six weeks later is not "was the snapshot intact" but **"we just corrected the trial length / retracted that case metric — which published packs are affected?"** That is a lookup by fact, and it is only answerable if consumption was recorded per pack. This is the single highest-value auditability feature in this brief and it costs almost nothing to record.

Per pack, therefore: snapshot hash · resolved-at (UTC + local) · band and degrade flags · fact-usage trace with per-fact confidence · claim-ledger entry IDs used · the source of every CTA and URL · the resolver rule version.

**Offline snapshot (Notion-down runs).** The last successful FULL or PARTIAL snapshot is persisted append-only, never overwritten, with N generations kept for rollback. A snapshot written during a MINIMAL or INSUFFICIENT run is never promoted to "last good" — otherwise degraded state ratchets forward. Rules:

- Running from a snapshot **caps the band at MINIMAL**, always. You cannot know whether the world changed while you were blind, and the cap is what makes the offline path safe rather than merely convenient.
- MINIMAL unattended → research-only (§5.4). So the realistic 3 a.m. Notion-outage behaviour is: research and ranking complete, no brand content, digest explains why.
- MINIMAL interactive → the operator may proceed with numbers, proof, comparisons and commitment CTAs all blocked.
- **Max-offline window**: recommended 7 days unattended / 14 days interactive, configurable, and independently capped by the hard-stale thresholds of the Tier-B facts inside it (so a snapshot containing 15-day-old price facts is already invalid at day 15 regardless of the window).
- A snapshot that fails its integrity check is treated as **absent**, never as best-effort. Fail closed.

---

## 7. Claim-safety verification substrate

### 7.1 Shape of the substrate

Two halves that must not be merged: the **claim ledger** (what may be said) and the **claim check** (what was actually said). The ledger is brand truth; the check is a verification pass over generated bytes.

The check runs over **every generated surface, in every language**: post bodies, hooks, captions, carousel slide text, on-image text, video scripts and spoken lines, alt text, blog copy, CTA text, and hashtags (a hashtag can carry a claim — "#1LeadGenTool"). The on-image and on-screen surfaces matter disproportionately: "300% ROI" graphics are exactly the artefact type that escapes text-only checking.

**Deterministic first, semantic second.** A pattern/dictionary/entity pass runs first and guarantees that no digit, currency token, entity mention or superlative escapes examination; an LLM pass then handles the classes that genuinely need semantics (outcome framing, capability inflation, comparative implication, superlative-in-context). The ordering is not an optimisation, it is a control-integrity argument: an LLM-only checker is non-deterministic and can be argued out of a block by the same model family that wrote the copy. Self-assessment by the generator is not a control at all.

**Bidirectional.** The substrate verifies both that forbidden content is absent *and* that required content is present (disclosures, AI labelling). A missing mandatory disclosure is a defect of the same class as a false claim.

### 7.2 Check classes

| # | Class | What is extracted | Verification rule | Notes / Czech (F-7) |
|---|-------|------------------|-------------------|--------------------|
| 1 | **Numeric quantity** | Any digit-bearing token: percentages, multipliers ("3x"), counts, durations ("in 5 days"), rates | Every number in a *claim position* must map to a ledger entry. Numbers are classified claim vs structural (list index, year, version, "3 steps" describing the post itself); **default is claim — fail closed** | Czech number formats (1 000; 1,5 mil.; percent spacing) and inflected units need language-specific patterns |
| 2 | **Currency / price** | Currency symbols, codes, words — and **"free"/"zdarma"**, which is a price claim | Allowed only if the exact value and terms exist in F-G at FULL confidence and the pricing policy permits stating them; otherwise rewrite to a link | "Zdarma" and "trial" carry the trial-terms dependency; Kč is postfixed |
| 3 | **Named entities** | Organisations and people | Four-way: **own brands/domains** = allowed; **own-team persons** (allowlist) = allowed; **client/customer names** = blocked unless in F-I with granted, unexpired permission; **third-party / competitor products** = allowed as *neutral references only*, any attached performance or comparison assertion escalates to class 8; **unknown entities** = blocked (a hallucination tell) | Driven by the real ICP: "firms using Instantly / Lemlist / Prospeo" makes competitor mentions legitimate and common. Czech declension of brand names ("v HypeLeadu", "Instantly.ai jsme") must be handled or the matcher both misses and over-flags |
| 4 | **Outcome / result** | "booked X demos", "increased reply rates", "saved hours", "built pipeline" — **including number-free forms** ("we consistently book meetings") | Requires an F-H/F-I entry. Empty ledger → all outcome claims blocked and generation steered to teaching/opinion framing | The highest-volume leakage class from the competitor corpus |
| 5 | **Superlative / absolute / uniqueness** | "best", "first", "only", "#1", "guaranteed", "never", "always"; cs: "nejlepší", "jediný", "zaručeně", "garantujeme", "100%" | Blocked by default; permitted only with an explicit substantiated ledger entry | The corpus literally contains "Guaranteed." — a competitor's line, one prompt away from ours |
| 6 | **Capability / autonomy** | "fully automated", "on autopilot", "sends for you", "24/7 SDR", "no human needed" | Checked against F-C positive **and negative** statements. A claim contradicting the does-not list is CONTRADICTED, not merely unsupported | Catches false claims containing zero numbers — see §3.4 |
| 7 | **Temporal / availability** | "launching next week", "now available", "limited spots", "ends Friday", webinar dates | Requires a dated event or availability fact; also catches manufactured urgency (which the voice gate rejects for different reasons) | The real strategy's webinar CTA lives here |
| 8 | **Comparative / competitive** | "faster than X", "cheaper than lemlist", "unlike Instantly" | Requires a comparison ledger entry with evidence and an observation date; otherwise degrade to neutral positioning | Legal exposure is real; **ASSUMED INPUT (from C7)** for the comparative-advertising rules |
| 9 | **Endorsement / social proof** | "used by 500 agencies", testimonial quotes, client logos, "our clients say" | Requires F-I with permission | Logos count — an image-only endorsement is still an endorsement |
| 10 | **Required-statement (bidirectional)** | Absence of mandated text: affiliate/discount disclosure, entity disclosure, AI-content labelling | Fails if a required statement is missing for the context | The 20% affiliate arrangement in the real strategy triggers this; AI labelling per F-8, **ASSUMED INPUT (from C7)** |
| 11 | **Corpus leakage** | Numbers, metric phrases and named entities that appear in the exemplar corpus but nowhere in the ledger | Any overlap = blocked, and flagged as a leakage event (a signal that the few-shot design is bleeding facts) | See §7.4 — this class exists because of what is actually in `docs/marketing/` |

### 7.3 Verdicts and enforcement

Per extracted candidate: **VERIFIED** (matches an in-scope, unexpired ledger entry) · **SAFE-NON-CLAIM** (classified structural/self-referential) · **UNSUPPORTED** (claim-shaped, no ledger match) → blocks · **CONTRADICTED** (conflicts with a resolved fact) → blocks and raises a brand-truth review flag, because it may mean the ledger itself is wrong · **DISCLOSURE-MISSING** → blocks until inserted.

Enforcement ladder, per **asset** (never per pack, never per run):
1. Block the asset. Record the offending spans and their verdicts.
2. **Bounded regenerate** — recommended maximum 2 attempts, each fed the specific failing spans and a positive constraint ("you asserted a 40% reply rate; you may only say that the approach targets people already showing intent").
3. Still failing → **downgrade repair**: emit the claim-free variant of the asset (value-only, no proof, softer CTA). This converts a hard failure into something publishable, which matters for run yield.
4. Still failing → drop the asset from the pack, record why, attach the rejected draft. **Never silently ship, never silently discard without a note.**

Budget note: the retry allowance is **per pack**, not per asset — otherwise an unattended run with a systematically bad prompt burns its token budget on a regeneration storm. Exhausting the pack allowance degrades that pack to review-required rather than failing the run.

**The claim check runs twice.** Once early (fail fast, before expensive downstream steps) and once as the **final immutable gate on the exact bytes that enter the pack**. This matters because the voice gate rewrites text, and a rewrite can reintroduce a claim that the early pass cleared. Any gate that runs before a rewriting step must be re-run after it.

### 7.4 Provenance separation: the exemplar corpus is style, never fact

The local corpus (`Winning Posts from competitors Linkedin.txt`, the GojiBerry playbook and transcripts, the LinkedIn outreach playbook) is dense with other people's commercial claims: "12 demos in 5 days", "25–40% response rate", "300 high-intent leads from a single search", "added 7-figures of revenue in Q1", "12+ hours saved every week", "book your first meeting within 7 days. Guaranteed." These files are, correctly, the voice reference for T13's few-shot design. They are also the highest-probability fabrication source in the entire system, because the generator is being *shown* them as examples of good writing at the exact moment it writes.

Design rules:
- The corpus feeds **style retrieval only**. It is excluded from any retrieval path that answers factual questions, and the claim ledger is never populated from it.
- Check class 11 explicitly compares generated numbers and metric phrases against corpus content and blocks overlaps that lack a ledger entry.
- Where a corpus exemplar's *structure* depends on a metric, the pattern is abstracted before use ("open with a specific outcome number" is a structural instruction; the number is not carried).

Worth noting for the record: the operator already applies this discipline manually. The GTM playbook tags every GojiBerry figure with a distinct claim marker and phrases them as *"their claim: $7k/month in sales before any code existed"*. The system is formalising an instinct the operator already has, which is the easiest kind of control to get adopted.

---

## 8. F-5 spoken claims: script-lock vs ASR-verify

**Recommendation: script-lock as the primary control; ASR-verify as a sampled audit of script adherence, not as the per-asset gate.**

Concretely, three rules:
1. **Spoken content is generated only from claim-checked script text.** The script is a first-class, verified artefact; audio is a rendering of it.
2. **In unattended runs, spoken lines may not contain claim-class tokens at all** — no numbers, currency, entities beyond own brand, superlatives or outcome statements. Claims live in **burned-in on-screen text**, which is composed at assembly time from verified strings and can be re-read before packaging. The audio channel is deliberately drained of claim payload, so model improvisation cannot fabricate anything that matters.
3. **ASR runs as a monitoring signal**: on every audio asset during the first weeks, then a rolling sample, and always after a provider or model change. Its job is to measure *adherence* (did the model say what it was told?). A measured adherence drop is a provider-level alarm that can disable audio for that model — not a per-asset pass/fail.

### Rationale

- **Preventive beats detective.** Script-lock stops the claim before generation; ASR detects it after the money is spent. Under cron budget caps, the worst place to discover a bad claim is after paying for the render.
- **Reuse of an existing, stronger substrate.** The claim check already operates on text with deterministic extraction. Script-lock means the spoken words *are* that verified text. ASR-verify introduces a second, weaker verification path over a noisy transcript with entirely new error modes.
- **Language asymmetry (F-5/F-7).** Czech ASR on marketing audio containing anglicisms and brand names is materially weaker than English (**expertise, needs web verification**). A gate whose accuracy varies by output language is a poor primary control for a mandated-bilingual product (D-02): it will over-block Czech (false alarms → the gate gets relaxed) and under-block Czech (dropped or mistranscribed numbers → false passes). Script-lock is language-neutral because it operates on the source text.
- **Failure direction.** ASR's characteristic failure is *dropping* content. A dropped claim in the transcript is a false pass — the worst possible direction for a safety gate.

### Failure modes, stated honestly

**Script-lock fails when:** the video model paraphrases, adds filler, or ad-libs instead of speaking the provided lines — adherence is a behaviour, not a guarantee, and it varies by model and by prompt length. Mitigations: prefer providers/modes with explicit dialogue-line control (**ASSUMED INPUT from T2** on which do); keep spoken lines short and plain; apply rule 2 above so drift cannot produce a *consequential* falsehood; and where claims genuinely must be spoken, use a separate TTS/VO step muxed at assembly, which makes script-lock near-airtight. Second failure mode: model-rendered on-screen text is *not* under script-lock and is unreliable for Czech diacritics (F-7) — hence the preference for assembly-time captions we compose ourselves.

**ASR-verify fails when:** transcription errs in either direction (homophones, numbers, brand names); the claim is carried by visuals rather than words; two runs disagree (non-determinism in a control surface); and it creates a discover-after-spend loop whose only repair is another paid generation. As a *sampled adherence monitor* none of these are disqualifying, because the signal is aggregate rather than per-asset — which is exactly why it belongs there and not on the gate.

---

## 9. Spin application design

### 9.1 Pain → offer mapping

The mapping is a **configured relation, not an inference**: (ICP segment × pain category) → (offer, preferred CTA class, owning brand/domain, preferred formats). Ranked topics arrive carrying a detected pain signal (**ASSUMED INPUT from T7/B3**); the mapper performs a lookup. If nothing matches above threshold, the correct answer is **no offer** — and the topic can still become genuinely good value content with a content-only CTA or none at all. This is the anti-forced-placement mechanism at the *brand* layer; T7's brand-fit score is the mechanism at the *ranking* layer. They are complementary and both are needed: ranking decides "should we touch this topic at all", spin decides "may we attach an offer to it".

**Mapping distance** is an explicit, recorded property, and it governs how loud the offer is allowed to be:

| Distance | Meaning | What the asset may do |
|----------|---------|----------------------|
| **Direct** | The topic *is* the pain this offer addresses | Offer named, one capability sentence, product CTA |
| **Adjacent** | Same ICP, related workflow, different problem | Offer may be mentioned once, soft CTA only, no capability elaboration |
| **Far** | Same audience, unrelated problem | **No offer, no product CTA.** Value content with a content CTA or none |

Illustrative shapes using the real segments (the *offers* themselves must come from resolved brand truth, never from this document): the technographic segment "firms using Instantly / Lemlist / Prospeo" with a deliverability-or-reply-rate pain is a **direct** match to a signal-based-targeting offer — and, because the segment is defined by competitor tools, it automatically engages check class 8 (comparative). "AI agencies whose clients are asking for AI outbound they cannot yet deliver" is plausibly **adjacent**, and which brand answers it (product vs the agency side on hypedigitaly.ai) is a routing fact, not a guess. A trending model release with no lead-gen consequence is **far**: post about it if it ranks, sell nothing.

### 9.2 CTA correctness rules

A CTA is emitted only when *all* preconditions hold — this is where CTA classes earn their existence:

| CTA class | Preconditions beyond the general ones |
|-----------|--------------------------------------|
| **Content** (guide, article, resource) | The resource exists and its URL resolves |
| **Product-path** (product page, trial, demo) | Offer status = live; destination URL verified within freshness window; band ≥ PARTIAL for the page, ≥ FULL to state trial terms |
| **Event** (webinar) | A dated event fact with a registration URL exists and the date is in the future. **No event fact → no webinar CTA**, ever. A webinar CTA is a promise that an event exists |
| **Commercial-incentive** (affiliate share, discount code) | Programme facts resolved (the real strategy's 20% share is a *number* and therefore a claim) **and** the required disclosure statement present (check class 10) |

General preconditions for every CTA: exactly one CTA per asset by default (no stacked CTAs); the CTA class is allowed at the current band; **brand routing is coherent** (a product CTA points at the product domain, an agency-service CTA at the agency domain); and **CTA-language coherence** — if a Czech asset's destination page has no Czech version, either the CTA changes or the asset says so. That last rule is a direct D-02 consequence and a live risk given that both domains are being built out bilingually.

Per-platform CTA placement conventions (link-in-comment on LinkedIn, etc.) belong to T10/C2 and T13/C5, not here.

### 9.3 Product rules (site-first offers)

"Site-first" means: for topics mapped to a site-first offer, the canonical asset is a page or article on the brand's own site, and social assets are atomisations pointing at it. In a pipeline that cannot publish the site itself, that creates a concrete ordering hazard: the system will happily write five social posts pointing at an article URL that does not exist yet.

Design: when the site-first article is not yet live, the default is **(a) hold the social atomisations in the pack as "blocked pending article", with the article draft included**, so the operator can publish the article and release the social set as one action. Config may select **(b) generate the social assets with a non-article CTA instead**. Option (a) is the default because option (b) quietly discards the product rule's whole purpose. Additionally, long-form site content carries more claims per asset and should require the FULL band, whereas PARTIAL is sufficient for social value content.

### 9.4 The good-vs-bad-spin test as an enforceable gate

The assignment's definition is qualitative; it becomes enforceable by decomposing it into binary criteria, each of which records the evidence for its verdict:

| # | Criterion | Fails when (the assignment's "bad spin") |
|---|-----------|------------------------------------------|
| S-1 | **Real topic anchor** — the asset references the actual researched topic/pain and is traceable to a specific research artefact ID | *Trend dump* / evergreen filler. Operational test: **could this asset have been written yesterday without this topic?** If yes → fail |
| S-2 | **ICP addressing** — names a recognisable situation for a *configured* segment | Addresses "businesses" / "teams" generically |
| S-3 | **Connection chain** — an explicit, checkable bridge from topic → consequence for that ICP → why the offer is relevant | *Random product mention*: the offer appears with no bridge sentence |
| S-4 | **Distance compliance** — offer prominence matches the mapping distance (§9.1) | *Forced relevance*: a far-distance topic carrying a product pitch |
| S-5 | **Proof discipline** — no proof-*shaped* statement without a ledger entry, including implied results | *Invented commercial proof* (the shape-level sibling of check class 4) |
| S-6 | **Next-step correctness** — at most one CTA, of an allowed class, correctly routed and language-coherent | Stacked CTAs, wrong domain, dead link, webinar with no event |
| S-7 | **No hype-glue** — the bridge survives removal of connector inflation ("this is exactly why…", "which is precisely the problem we solve") | Forced relevance disguised as a transition |

Enforcement: fail → bounded regenerate citing the specific criterion → second failure → **downgrade to the value-only variant** (drop the offer, keep the insight, content CTA) → still failing → drop the asset with the reason recorded. The value-only downgrade is important: most spin failures are failures of the *pairing*, not of the writing, and the correct repair is usually to stop selling rather than to rewrite harder.

Every asset also records its **spin rationale**: topic ID, detected pain, segment, mapped offer, distance, CTA class, and the fact-usage trace. This is what an operator reads to judge "was this a natural connection?" in seconds, and it is what makes the gate auditable rather than a black box.

### 9.5 Where the spin gate sits relative to the voice gate

Recommended per-asset order:

    brand-truth gate (band + fact availability)   → decides what may be attempted, BEFORE generation
      → generate
      → spin gate (S-1…S-7)                       → "is this the right thing to say?"
      → claim check, pass 1 (fail fast)           → "is it true and allowed?"
      → voice gate (anti-slop, per language)      → "is it said like a human?"
      → claim check, pass 2 — final, immutable    → re-verify the exact bytes after rewriting
      → platform-constraint check
      → pack

The spin gate precedes the voice gate because the two failures have different repairs. A voice failure is fixed by rewriting phrasing; a spin failure usually means the topic/offer pairing was wrong, and the repair is to drop the offer. Polishing the prose of a structurally wrong asset wastes regeneration passes and budget — and, worse, a well-voiced piece of forced relevance is *harder* for a reviewer to reject than a clumsy one. Keeping the two gates separate (rather than folding spin criteria into the voice judge) also keeps their failure reports separately actionable: "the connection was forced" and "this reads like AI marketing" call for different fixes by different owners.

The claim check appears twice for the reason given in §7.3: the voice gate rewrites text, and the last gate before packaging must see the final bytes.

---

## 10. Czech behaviour (D-02 / F-7)

- **Facts are language-scoped.** Offer descriptions, capability statements, CTA phrasings and claim texts exist per language, and a claim approved in English is **not** automatically approved in Czech. Translation changes claim strength — an English "helps you book more meetings" can land in Czech as something much closer to a guarantee. Ledger entries carry independent per-language approval.
- **Confidence is per (theme, language).** A missing Czech CTA phrasing or a missing Czech destination page degrades the Czech output set independently; the English pack can proceed at FULL while the Czech pack sits at PARTIAL or is blocked. This falls straight out of D-02's "never a translation pass".
- **Extraction must be Czech-aware**: number and currency formatting (1 000; 1,5 mil.; Kč postfixed; percent spacing), diacritics, and declension of brand names ("v HypeLeadu", "HypeLeadem") — without declension handling the entity matcher both misses real mentions and over-flags inflected forms. The superlative lexicon is its own list ("nejlepší", "jediný", "zaručeně", "garantujeme", "100% jistota"), not a translation of the English one.
- **Site verification is asymmetric**: both domains may lack Czech pages for some offers, which is exactly the CTA-language-coherence rule in §9.2. A degraded Czech CTA is a normal, expected state, not an error.
- The Czech-specific voice lexicon and rubric belong to T8/T13; this brief only requires that the *fact and claim* layers be per-language rather than translated.

---

## 11. Failure modes and mitigations

| Failure | Detection | Design response |
|---------|-----------|-----------------|
| Notion token expired at 03:00 (**ASSUMED INPUT from C1**) | Auth error during pull | Offline snapshot → MINIMAL → research-only; digest names the token, not "low confidence" |
| Site fetch fails / anti-bot | Fetch error | Record "not observed" — **never** as disagreement. Lowers corroboration, does not red-flag |
| Roadmap page read as fact | Not detectable statistically | Structural: read only designated fact locations; offers not explicitly `live` are unspinnable (§3.4) |
| Claim silently expires mid-week | Ledger expiry sweep | Digest lists claims expiring within 30 days |
| Checker too strict → operator disables it | Rising block rate, falling pack yield | Measure block rate and false positives against a golden set of known-good copy; allow per-class tuning; **never** allow disabling classes 1, 2, 3, 9 or 10 |
| Regeneration storm burns budget unattended | Retry counters | Per-pack retry allowance; exhaustion degrades the pack, not the run |
| Bad snapshot persisted as "last good" | Band recorded at write time | Only FULL/PARTIAL snapshots are promoted; N generations retained; integrity failure = absent |
| Human override laundering a new price/claim | Override schema | Overrides may narrow, never create commercial facts (§4.3) |
| Competitor metrics leak from the exemplar corpus | Check class 11 | Style-only retrieval; corpus-overlap blocking; leakage events reported |
| Wrong brand's CTA on a pack | CTA-brand coherence rule | Blocked at S-6 / §9.2 |
| Social posts pointing at a not-yet-published article | Site-first hold rule | Atomisations held pending the article (§9.3) |
| Alarm fatigue from repeated identical degrades | Consecutive-degrade counter | Escalate prominence rather than repeat; quiet acknowledged conflicts (§5.5) |

---

## 12. Decision table

### Decisions this brief unblocks

| # | Decision | → Architecture area |
|---|----------|--------------------|
| U-1 | Three fact tiers (blocking / constraining / enriching) with "missing ≠ empty"; resolved-empty is a first-class safe state | §6 brand-truth/spin; §10 theme-config knobs |
| U-2 | Fact classes F-A…F-N with per-class tier, including **negative capability statements** as blocking | §6; §10 |
| U-3 | ICP entries carry a segment *type* (firmographic / role / technographic) because technographic segments legitimise competitor mentions | §6; §2 ranking inputs; §10 |
| U-4 | Per-fact-class precedence, overriding the flat D-03 order for commercially binding facts (site wins) | §6 |
| U-5 | Excludes are monotonic; the site subtracts but never adds; silence ≠ agreement; unreadable ≠ disagreement | §6 |
| U-6 | Three conflict outcomes; red-flag list (price, trial, plan, guarantee, availability, contradicted claim, case metric) never tie-breaks | §6; §11 gates |
| U-7 | Human overrides may narrow but never create commercial facts | §6; §11 modes |
| U-8 | Gate-then-score band computation (not a weighted average); four coarse bands with a capability table | §6; §12 pack anatomy |
| U-9 | Per-class freshness thresholds with stale-warn vs hard-stale | §6; §10 |
| U-10 | **Exact unattended degrade trigger**: below PARTIAL, or any unresolved red-flag conflict, or expired/invalid snapshot, or unreadable claim ledger, or unresolved excludes | §6; §8 cron; §11 |
| U-11 | Confidence and the degrade decision are computed **per (theme, language)** | §6; §3; §12 |
| U-12 | Brand truth resolves *before* research and generation so degrade precedes spend | §8; §9 flows |
| U-13 | Snapshot = normalised hashed fact set + **fact-usage trace per pack** (recall by fact, not just integrity) | §6; §12 |
| U-14 | Offline snapshot caps the band at MINIMAL; max-offline window 7d unattended / 14d interactive; integrity failure = absent | §6; §8 |
| U-15 | Eleven claim check classes, deterministic-first then semantic, bidirectional (forbidden-absent + required-present), across all surfaces incl. on-image text | §14; §6 |
| U-16 | Enforcement ladder: block asset → bounded regenerate (2) → **downgrade repair** → drop with note; retry budget per pack | §14; §8 budgets |
| U-17 | Claim check runs twice, the second time as the final immutable gate on packed bytes | §14 |
| U-18 | Exemplar corpus is style-only; corpus-leakage check class | §6 exemplar corpus; §14 |
| U-19 | **F-5: script-lock primary; spoken lines carry no claim tokens unattended; ASR as sampled adherence monitor** | §4 video; §14 |
| U-20 | Pain→offer mapping is configured, with direct/adjacent/far distance governing offer prominence | §6; §10 |
| U-21 | CTA classes with fact preconditions (content / product-path / event / commercial-incentive) + brand-routing and language coherence | §6; §3; §10 |
| U-22 | Site-first offers hold their social atomisations until the article exists (default) | §6; §3; §7 |
| U-23 | Spin gate S-1…S-7 as an enforceable gate placed **before** the voice gate, with per-asset spin rationale recorded | §14; §12 |
| U-24 | Operator-facing degrade UX: distinct outcome, one-sentence reason, brand-truth panel with both conflicting values, research preserved, €0 stated, anti-flap | §12; §8 |

### Decisions this brief defers

| # | Open decision | Why deferred | Owner |
|---|--------------|-------------|-------|
| D-a | Whether unattended Notion access is viable at all (MCP vs REST token) | Tool-surface fact | C1 / OD-4 — if unviable, the offline-snapshot path becomes the normal unattended path and the degrade rate must be re-forecast |
| D-b | Whether the Notion workspace can express per-fact records and separate *plan* pages from *fact* pages | Workspace shape | C1 + operator. If not, recommend config-primary for binding classes |
| D-c | Exact numeric freshness thresholds and the max-offline window | Depend on the operator's real change frequency | Operator, at first-theme setup |
| D-d | Whether the claim ledger lives in Notion, in theme config, or split | Editing ergonomics vs auditability | Human decision, informed by C1 |
| D-e | Legal status of comparative claims, affiliate disclosure wording, AI-labelling obligations | Legal | C7 / R4 |
| D-f | Which video providers actually support enforceable dialogue lines (script-lock strength) | Provider facts | T2 / A2 |
| D-g | Czech ASR accuracy on brand-name-heavy marketing audio | Needs web verification | W2 or implementation spike |
| D-h | Where the fact-usage trace is stored and how recall-by-fact is queried | State substrate | T11 / C3 |
| D-i | Whether an operator may raise the band ceiling in interactive mode beyond MINIMAL when offline | Risk appetite | Human, at §16 |
| D-j | Deterministic entity matching for Czech declension: rule-based vs model-assisted | Implementation tradeoff | Implementation phase |

---

## 13. Fact ledger

| Claim | Source | Date | Confidence | Recheck by |
|-------|--------|------|-----------|-----------|
| Real ICP segments include agencies (marketing, web design, UGC, lead-gen, SMMA, AI, PPC, appointment setters), B2B marketing, sales/commercial directors, automation/outreach/AI-interested people, startups, LinkedIn experts, GTM/lead-gen, and **firms using Instantly.ai / Lemlist / Prospeo** | `docs/marketing/HypeLead Areas GTM_Marketing_Strategie.txt` | 2026-08-06 (read) | High (operator-authored) | 2026-11-06 |
| Real CTA/offer angles in play: free trial ("we want your opinion"), free webinar, demo, free guide/lead magnet, affiliate with **20% recurring share** + discount code | same file | 2026-08-06 | High | 2026-11-06 |
| Own-team named humans who post/amplify: Pavel Čermák, Erik Čermák, Miroslava Čermáková | same file | 2026-08-06 | High | 2027-02-06 |
| SEO articles are planned on both hypedigitaly.ai and hypelead.ai → two-brand routing is real | same file | 2026-08-06 | High | 2026-11-06 |
| Brand split: hypelead.ai = the product; hypedigitaly.ai = broader sales/AI help for agencies | `docs/marketing/GTM/00-GTM-Playbook.html` | 2026-08-06 | Medium-high (planning doc; verify against Notion + live sites) | 2026-09-06 |
| Stated capability boundary: HypeLead "finds people with buying signals and drafts your first message. You approve and send. **It does not send on its own.**" | same file | 2026-08-06 | Medium (planning doc, may be aspirational — this is exactly the plan-vs-fact hazard in §3.4) | 2026-09-06 |
| A 7-day free trial is referenced in the brand's own draft copy | same file | 2026-08-06 | **Low-medium** — must be site-verified before any use; a trial-term mismatch is a §4.2 red flag | Before first use |
| The operator already tags competitor metrics as *their* claims with a distinct marker in their own GTM doc | same file (claim-marker class usage) | 2026-08-06 | High | n/a |
| The exemplar corpus contains third-party commercial claims ("12 demos in 5 days", "25–40% response rate", "300 leads", "7-figures in Q1", "12+ hours saved", "Guaranteed") | `docs/marketing/Winning Posts from competitors Linkedin.txt`, `The-LinkedIn-High-Intent-Outreach-System-…​.md` | 2026-08-06 | High | n/a — standing hazard |
| The LinkedIn outreach playbook in `docs/marketing/` is a **competitor/affiliate** artefact (gojiberry.ai referral links), not the brand's own case study | same file | 2026-08-06 | High | n/a |
| Notion KB about HypeDigitaly + projects exists and is MCP-connectable | Masterplan W0.5 intake / DECISION_LOG OD-6 | 2026-08-05 | High (operator-confirmed) | 2026-09-06 |
| Notion auth model, unattended-cron viability, rate limits, per-fact retrievability | **ASSUMED INPUT (from C1)** | pending | Unknown | W2 reconciliation |
| Ranked topics carry an inspectable pain signal and brand-fit sub-score | **ASSUMED INPUT (from T7/B3)** | pending | Unknown | W2 |
| A separate anti-slop voice gate with bounded regenerate exists | **ASSUMED INPUT (from T13/C5)** | pending | Unknown | W2 |
| Video providers vary in whether spoken dialogue lines can be enforced | **ASSUMED INPUT (from T2/A2)**; expertise | pending | Medium | W2 |
| Czech ASR on marketing audio with anglicisms/brand names is materially weaker than English | expertise + F-5/F-7 | 2026-08-06 | **Medium — needs web verification** | W2 or implementation spike |
| EU AI Act Art. 50 synthetic-content transparency in force; platform AI labels are separate obligations | Masterplan F-8; **ASSUMED INPUT (from C7)** | 2026-08-05 | Medium (not verified here) | W2 / R4 |
| Gate-then-score confidence (rather than weighted averaging) prevents soft-fact scores masking a missing hard fact | expertise (standard control-design practice) | 2026-08-06 | High (design reasoning, not an external fact) | n/a |
| Deterministic-first extraction is required because an LLM-only checker is non-deterministic and self-assessable | expertise | 2026-08-06 | High (design reasoning) | n/a |
| Preventive controls (script-lock) dominate detective controls (ASR) when the detected event costs money to repair | expertise | 2026-08-06 | High (design reasoning) | n/a |

---

## 14. Sources

**Local files read for this brief** (all read 2026-08-06):
- `HypeAgentSocials_InstructionsAssignment.md` — "Brand spin layer (config + MCP + public verification)" and "What 'spin' means"; the never-invent red line; unattended fail-closed mandate.
- `docs/marketing/HypeLead Areas GTM_Marketing_Strategie.txt` — **mandatory input**; the real Czech ICP segments, outreach angles, CTA/offer set, affiliate terms, two-domain SEO plan, named team members. Used to cross-check and correct the taxonomy (§3.3).
- `docs/marketing/GTM/00-GTM-Playbook.html` — brand/product split, capability boundary wording, competitor-claim tagging precedent, bilingual CTA drafts. Treated as a **planning** artefact, not brand truth (§3.4).
- `docs/marketing/Winning Posts from competitors Linkedin.txt` and `docs/marketing/The-LinkedIn-High-Intent-Outreach-System-How-We-Booked-12-demos-in-5-days.md` — exemplar corpus; read here **only** to enumerate the third-party claims that must never leak (§7.4).
- `docs/plans/DESIGN_PHASE_MASTERPLAN.md`, `docs/architecture/DECISION_LOG.md`, `docs/STAGE0_RESTATEMENT.md` — D-01…D-08, F-1…F-9, W0.5 fact intake, mandated brief structure.
- Not read, per instruction: other agents' briefs under `docs/research/`.

**Durable canon this design draws on** (expertise, no web access — named so a reviewer can check the lineage):
- Data-quality and master-data-management practice: source-of-record precedence per attribute class, conflict quarantine rather than automatic merge, provenance and lineage recorded per record.
- Safety/verification engineering: preventive vs detective controls; fail-closed defaults; the principle that a component's self-assessment is not a control over that component; defence in depth via independent deterministic and semantic layers.
- Content governance and regulated-marketing practice: approved-claim libraries with substantiation and expiry, claim provenance (own / customer-attributed / third-party / competitor), mandatory-statement checking alongside prohibited-content checking, review-of-record for published assertions.
- Reproducibility practice from ML systems: hashed, versioned input snapshots pinned to every produced artefact, including the version of the rules that produced it; artefact recall by input identity when an input is later found to be wrong.
- Retrieval-system design: separation of style/few-shot corpora from factual retrieval corpora to prevent exemplar facts being absorbed as truth.
- Alerting/operations practice: coarse bands over false precision, actionable alert text, anti-flap escalation, and the empirical fact that noisy gates get disabled by their operators.

**Explicitly marked as expertise-derived, not externally verified**: all threshold values in §5.2 and §6.3, the four-band capability table, the eleven check classes, the S-1…S-7 spin criteria, the gate ordering in §9.5, and the script-lock recommendation's Czech-ASR argument (flagged for verification in the fact ledger).
