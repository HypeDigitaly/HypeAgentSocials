# 06A — The knob registry: authoritative per-knob table

*Design phase · playbook layer, config-surface annex · no code, no pseudocode, no CLI syntax, no configuration-file syntax, no mandatory folder tree, per `CONDUCTOR_RULINGS.md`'s standing constraints.*

**Owns:** the single authoritative table of every configuration knob in the system — ID, tier, default, layering regime, authoring/resolved status, consumer — old and new. **Does not own:** the operator-facing form presentation (`06C_authoring_form.md`), the CTA-table design (`06D_cta_authoring.md`), or the resolver's internal mechanics (a parallel task). Where this file and `06C`/`06D` name the same field, this file is the field's registry entry and the other files are its presentation and worked-example layer; they should agree, and §7 below records the one place they were found not yet reconciled.

**Sits beneath:** `CONDUCTOR_RULINGS.md` (CR-1…CR-8), binding on every leaf. Where this file and the rulings appear to diverge, the rulings govern and this file is wrong. Where the rulings are silent, `00_MASTERPLAN.md` governs.

---

## 0. Method — how this table was built, so a reader can audit it

**Sources read, in the order the task specified:** `CONDUCTOR_RULINGS.md` in full; `ARCHITECTURE_PLAN.md` §10 in full (§10.1–§10.6) and §13.2; `00_MASTERPLAN.md` §2, §3, §8 (and, for the surrounding argument, §1 and §4); `03_pipeline_and_gates.md` §6.2 and §10.1; `05_query_steering.md` §5. `01_content_ontology.md` was consulted only where `00_MASTERPLAN.md` §8 explicitly attributes new-knob claims to it, and only after filtering it through the corrections `00_MASTERPLAN.md` §3 and §4 (C-1…C-13) already impose — that annex is an **input, not binding**, and several of its knobs are reshaped or dropped below because a ruling already supersedes them (noted inline).

**Row count method.** Every row in `ARCHITECTURE_PLAN.md` §10.2 through §10.4a was counted mechanically (`awk` over the table markup, one count per subsection, summed). The result is reported in §1.9.

**Tier.** Per CR-5: **A** — must-answer, no correct default exists because the answer is the tenant's identity; target ten fields, hard ceiling twelve. **B** — has a real default (a value, a rule, or an explicit "ships off until configured") and produces coherent output untouched. **C** — engine-level; not in the authoring form; reachable only by a logged expert override.

**Layering regime.** Per CR-6, one of four, applied by the following classification rule (stated once here rather than re-justified 178 times; exceptions are called out inline):

| Tag | Regime | Rule of thumb applied |
|---|---|---|
| **MONO** | monotonic-tighten-only | The knob is a floor, ceiling, cap, or on/off safety switch belonging to the Tier-1 set `00_MASTERPLAN.md` §3.1 names (universal slop floor, non-disableable checks, hard excludes, negative-prompt layers 1–3, AI-disclosure floor, Prohibited-Outcome Gate, fail-closed triggers, publish gate, spend gating) or is described in `ARCHITECTURE_PLAN.md` itself with tighten-only language ("engine floor," "a theme may only tighten," "stricter wins," "never a looser class"). |
| **REG** | registry-selection | The value is one member of an engine-owned, closed, versioned set (a method, a route, a class, a profile, an archetype, a genre) and a layer *selects*, never authors, a member. |
| **UNION** | additive-union | The value is an array whose purpose is to make the system safer or more precise by being *larger* (excludes, banned phrasing, negative terms, veto conditions, refresh triggers); every layer may append, none may remove another layer's entry. |
| **LLW** | last-layer-wins | A plain scalar, pointer, or non-safety array with no cross-layer composition logic; the most specific configured layer governs, falling back to the stated default if unset. |
| **N/A-machine** | orthogonal to the theme stack | The five `§10.4a` machine-block rows sit outside `engine → playbook → theme → language → destination` entirely — they describe the computer, not the tenant, and CR-6's stack has nothing to say about them. Flagged rather than force-fit. |

**Authoring mode** (CR-1, and task item 6). Three values: **Literal** — authored as a scalar or array and used verbatim, never compiled (CR-4). **Either** — a closed, small registry the operator may name directly or describe in prose for the resolver to map (CR-7 applies if unmapped). **Resolver-derived** — the field is normally free text and the resolver's job is to map it to a registry member, reporting the mapping in the CR-2 readback. **General rule applied:** UNION, MONO and LLW rows are Literal by default (a theme types a number, a URL, a name, an array entry); REG rows are Either by default. Two REG rows are flagged **Resolver-derived** explicitly because the base documents motivate them that way in prose (genre selection, angle-type restriction from a described preference) — see §2.2 and §2.3. Tier-C rows carry **N/A — not in the authoring form** (CR-5).

**Consumed by.** Existing rows keep `ARCHITECTURE_PLAN.md`'s own §-references verbatim. New rows cite the annex and section that introduces them (`03§x`, `05§x`, `00§x`).

---

## 1. The existing 141-row surface, reproduced grouped by block

### 1.0 The count, corrected

`ARCHITECTURE_PLAN.md` §10.1 states: *"Counting the tables below gives **roughly 130 settings**..."* Counting the seven tables in §10.2–§10.4a mechanically gives **141** rows exactly (29 + 29 + 16 + 18 + 19 + 25 + 5), not "roughly 130." This is not a new finding — `CONDUCTOR_RULINGS.md` CR-5 already uses "141 knob rows" as its working figure, and `00_MASTERPLAN.md` §1 independently states *"100 of ~141 knobs are vertical-neutral."* Two documents already agree on 141; only §10.1's own prose disagrees with the tables sitting directly beneath it in the same file. See §7 (Contradictions found) for the verbatim quotes. This file uses **141** as the confirmed base count and recommends §10.1's sentence be corrected in the same edit pass that lands this annex.

### 1.1 Research block (`§10.2`) — `CFG-RB-01`…`29`

| ID | Knob | What it controls | Tier | Default | Regime | Auth. | Consumed by |
|---|---|---|---|---|---|---|---|
| RB-01 | Watch topics, keywords and entities | Subject matter; seeds every collector and the brand-fit reference set | **A** | *(see §4)* | LLW | Literal | §2.3, §2.7, §6.9 |
| RB-02 | Research-side excludes | Topics/framings/entities that never become candidates | B | Empty (distinguished from unresolved) | UNION | Literal | §2.7, §6.3 |
| RB-03 | Language array | Which output languages the theme produces | **A** | *(see §4 — flagged, not "Czech/English")* | LLW | Literal | §2.7, §3.2, §3.4, §6.5, §13 |
| RB-04 | Source roster with per-source priority | Which List-A sources are active, in what order | B | The §2.3 portfolio | REG | Either | §2.3, §2.7, §8.2 |
| RB-05 | Per-source extraction method | Which of seven method values a source uses | B | Per §2.3 | REG | Either | §2.3, §2.4 |
| RB-06 | Per-source cadence | Poll frequency per source | B | Daily core; weekly–monthly curated | LLW | Literal | §2.3, §8.2 |
| RB-07 | Per-source evidence class | Counted / ranked-presence / human-asserted | B | Per §2.7 | REG | Either | §2.7, §12.1 |
| RB-08 | Per-source run budget | Ceiling in calls/quota/credits/seconds per source per run | B | Per source; sub-10% of quota (video collector) | MONO | Literal | §2.2, §2.3, §11.1 |
| RB-09 | Source-family membership | Which of seven families a source belongs to | B | Per §2.7 | REG | Either | §2.7 |
| RB-10 | Ladder-rung configuration per source | Primary→degraded→operator-supplied→skip chain | B | Per §2.2 | REG | Either | §2.2, §2.5, §8.10 |
| RB-11 | Per-source circuit-breaker threshold | Failures before a source drops for the run | B | *(disposed, §3)* | MONO | Literal | §2.8, §8.10 |
| RB-12 | Source-health escalation count | Consecutive degraded runs before alert prominence rises | B | Two | LLW | Literal | §2.2, §8.12 |
| RB-13 | Collection wall-clock ceiling | Global collection time budget | B | *(disposed, §3)* | MONO | Literal | §2.8, §8.7 |
| RB-14 | Cache time-to-live per signal class | Reuse window before re-request | B | *(disposed, §3)* | LLW | Literal | §2.8 |
| RB-15 | Topic dedupe lookback window | How far back dedupe is consulted | B | *(disposed, §3)* | LLW | Literal | §2.7, §8.5, §12.1 |
| RB-16 | Freshness half-life per signal class | Decay rate per signal class | B | Directional starting values (§2.7) | LLW | Literal | §2.7 |
| RB-17 | Brand-fit floor | Hard numeric floor below which a candidate is skipped | B | Directional 0.35, calibration starting point | MONO | Literal | §2.7, §12.1, §16 |
| RB-18 | Veto list contents | Binary stop conditions before scoring | B | Per §2.7 | UNION | Literal | §2.7 |
| RB-19 | Corroboration bonus magnitude | Cross-family confirmation lift | B | *(disposed, §3)* | LLW | Literal | §2.7 |
| RB-20 | Top-N topics cap per language | Max ranked topics carried forward | B | ~5/run (OD-8, open) | MONO | Literal | §2.7, §12.1, §16 |
| RB-21 | Monitor-only band boundary | Watched-but-not-generated score range | B | *(disposed, §3)* | LLW | Literal | §2.7 |
| RB-22 | Absolute-band fallback thresholds | Fixed per-source bands before a baseline exists | B | *(disposed, §3)* | LLW | Literal | §2.7 |
| RB-23 | Demand-modifier weight | Post-composite search-demand influence | B | *(disposed, §3)* | LLW | Literal | §2.7 |
| RB-24 | Ranking-config version | Version stamp on every scorecard | B | Incremented on threshold change | LLW | Literal | §2.7, §8.5, §12.2 |
| RB-25 | Retention windows | Durations: request log / raw payload / signal record / curated verbatim | B | 12mo / 30d / 90d / 30d (OD-15) | MONO | Literal | §2.6, §8.6, §15 |
| RB-26 | Author-handle handling policy | Drop / hash / retain, and for how long | B | Hashed where needed; never clear-text long-term | MONO | Literal | §2.6 |
| RB-27 | MCP-source credit budget per month & pacing | Metered spend ceiling per licensed vendor | B | *(disposed, §3)* | MONO | Literal | §2.2, §11.1, §15 |
| RB-28 | Vendor roster with last-verified/recheck-by | Licensed-source registry, degrade-on-lapse | B | *(disposed, §3)* | LLW | Literal | §2.2, §5.2, §15 |
| RB-29 | Curated-inbox staleness threshold & escalation | Staleness flag and alert escalation count | B | One cadence period; escalate at 2 misses | LLW | Literal | §2.2, §8.12, §12.1 |

### 1.2 Spin block (`§10.3`) — `CFG-SB-01`…`29`

| ID | Knob | What it controls | Tier | Default | Regime | Auth. | Consumed by |
|---|---|---|---|---|---|---|---|
| SB-01 | Brand-truth source pointers & designated fact locations | Which KB locations may be read per fact class | **A** | *(see §4)* | LLW | Literal | §6.2, §6.3 |
| SB-02 | Access path per context | MCP interactive vs REST for records | **C†** | MCP interactive, REST for records (D-10) | REG | N/A | §6.2, §9.3 |
| SB-03 | Site-verification URL set, budget, timeout | Live-page checks per run | B | A handful of timeboxed fetches | MONO | Literal | §6.6 |
| SB-04 | Stale-warn / hard-stale thresholds per fact class | When an observation warns vs blocks | B | *(disposed, §3)* | MONO | Literal | §6.6, §6.5 |
| SB-05 | Maximum offline window — interactive only | Last-good snapshot reuse window; no unattended limb | B | 14 days interactive | MONO | Literal | §6.5, §6.6, §11.3 |
| SB-06 | Confidence band floor per mode | Minimum band for generation, per mode | B | Below PARTIAL → research-only unattended | MONO | Literal | §6.5, §11.3 |
| SB-07 | Claim-ledger pointer | Approved-claim allowlist location and query | B | Notion typed DB (OD-9) | LLW | Literal | §6.3, §6.7, §14.3, §16 |
| SB-08 | Hard-excludes baseline | Exclusion list surviving a KB outage; union always wins | **A** | *(see §4)* | UNION | Literal | §6.3, §6.4, §11.3 |
| SB-09 | Check-class enablement | Which of eleven claim checks run; five non-disableable | B | All eleven on; five locked | MONO | Literal | §6.7, §14.3 |
| SB-10 | Per-pack regenerate allowance | Claim-gate retry budget, per pack | B | Small fixed number | MONO | Literal | §6.7, §12.4, §14.3 |
| SB-11 | Pain-to-offer relation | ICP×pain → offer/CTA/brand lookup | **A†** | *(see §4, generalised by PS-09)* | LLW | Literal | §6.9, §14.1 |
| SB-12 | Mapping-distance policy per offer | Loudness at direct/adjacent/far | B | Per §6.9 | REG | Either | §6.9, §14.1 |
| SB-13 | CTA class enablement per destination per language | Which CTA classes run where | B | Content/product-path on; others off until precond. | REG | Either | §6.9, §3.3 |
| SB-14 | CTA phrase bank pointer per language | Literal approved phrasings per CTA class | B | Language overlay | LLW | Literal | §6.9, §14.4 |
| SB-15 | Site-first offer list & hold-vs-substitute | Article-first gating; hold vs alt-CTA | B | Site-first listed; hold is default | LLW | Literal | §6.9, §7.3 |
| SB-16 | Person allowlist | Named humans exempt from unknown-entity flag | B | *(disposed, §3)* | UNION | Literal | §6.3, §6.7 |
| SB-17 | Brand-and-domain routing map | Offer → brand → domain, so CTAs can't cross wires | **A** | *(see §4)* | LLW | Literal | §6.3, §6.9 |
| SB-18 | Pricing policy | Whether prices may be stated at all | B | Config-primary; stricter wins | MONO | Literal | §6.3, §6.4, §6.7 |
| SB-19 | Compliance obligations | Entity/affiliate disclosure, AI labelling duties | B | *(disposed, §3)* | MONO | Literal | §6.3, §6.7, §14.6 |
| SB-20 | Speech-recognition sampling rate & adherence alarm | Spoken-output sampling and disable trigger | B | Every asset early, then rolling sample | MONO | Literal | §6.8, §14.5 |
| SB-21 | Exemplar corpus pointer per language | Style-only reference material location | B | *(disposed, §3 — ships off)* | LLW | Literal | §6.11, §14.2, §14.4 |
| SB-22 | Corpus-leakage sensitivity | How aggressively output is checked against the corpus | B | Block on any unledgered overlap | MONO | Literal | §6.7, §6.11 |
| SB-23 | Resolver rule version | Precedence/threshold version on every snapshot | B | Incremented on precedence change | LLW | Literal | §6.6 |
| SB-24 | Snapshot reuse time-to-live | Reuse window across same-day runs | B | *(disposed, §3)* | LLW | Literal | §6.6 |
| SB-25 | Event-driven refresh trigger set | Events forcing a full re-pull regardless of TTL | B | Per §6.6 | UNION | Literal | §6.6 |
| SB-26 | Language overlay pointer per language | Which shared overlay this theme uses | B | Shared, per language | LLW | Literal | §3.4, §14.4 |
| SB-27 | Peer-community context declaration | The only setting permitting Czech tykání | B | Absent — vykání by default (D-26) | MONO | Literal | §3.1, §14.4 |
| SB-28 | Visual brand baseline | Logo, palette, on-image text rules | B | *(disposed, §3 — minimal/off)* | LLW | Literal | §4.4, §6.3 |
| SB-29 | Voice rules and banned phrasing | Theme additions atop the overlay's slop lexicon | B | *(disposed, §3 — empty)* | UNION | Literal | §3.4, §14.2 |
| SB-30 | **Brand & entity identity** *(newly identified gap, not a §10 row today — see §4)* | Legal entity, brand name(s), which brand owns which domain | **A** | *(see §4)* | LLW | Literal | *new — recommend §6.3* |

*† SB-02: listed in §10.3 as a theme knob, but its value is locked by decision D-10 — it does not actually vary per theme. Recommend re-scoping to §10.5 in the next edit; see CFG-OD-1. SB-11: generalised beyond B2B by `CFG-PS-09` below; kept as the R-1-specific instance rather than deleted, see CFG-OD-5.*

### 1.3 Output/runtime — destinations & assets (`§10.4`, table 1) — `CFG-XD-01`…`16`

| ID | Knob | What it controls | Tier | Default | Regime | Auth. | Consumed by |
|---|---|---|---|---|---|---|---|
| XD-01 | Per-language destination × asset-type matrix | Which destinations/asset types are on, per language | **A** | *(see §4)* | LLW | Literal | §3.2, §12.2, §13 |
| XD-02 | X destination enablement | Whether X assets are produced at all | B | Config-gated, default off | LLW | Literal | §3.2, §7.5, §16 |
| XD-03 | Blog enablement & routing | Long-form on/off, per language/domain | B | Drafts only in v1 (OD-14) | LLW | Literal | §3.2, §7.3 |
| XD-04 | Per-destination format profile | Char limits, aspect, duration, hashtag norms | **C†** | Verified 2026 values | N/A | N/A | §3.3, §12.2 |
| XD-05 | Link policy per destination | Where links may appear (incl. first-comment) | B | *(disposed, §3)* | LLW | Literal | §3.3 |
| XD-06 | CTA placement convention per destination | Where the single CTA sits | B | *(disposed, §3)* | LLW | Literal | §3.3, §6.9 |
| XD-07 | Carousel size caps | Slides per carousel / pages per doc | B | 5–15 slides target | MONO | Literal | §3.2, §3.3 |
| XD-08 | Per-language volume targets | Assets/type a healthy week produces | B | *(disposed, §3)* | LLW | Literal | §3.2, §12.1 |
| XD-09 | Masters per language per run cap | Media-bearing ceiling, counted per master | B | 1–2/language (OD-8, open) | MONO | Literal | §3.2, §4.6, §8.11, §16 |
| XD-10 | Minimum mapping distance per destination | Closest distance a destination accepts w/o a soft bridge | B | Adjacent-or-closer TikTok/Reels/Shorts; else unrestricted | MONO | Literal | §3.3, §6.9 |
| XD-11 | Czech short-form revisit trigger | Asset-count/week backstop for review | B | 20 assets or 12 weeks (OD-22) | LLW | Literal | §3.1, §12.1, §16 |
| XD-12 | Per-destination derivative set | Which re-compositions come from a master | B | Per §4.4 | REG | Either | §3.2, §4.4 |
| XD-13 | Review-depth profile per asset type | Expected operator attention, drives digest order | B | Per §3.5 | LLW | Literal | §3.5, §12.1 |
| XD-14 | Czech short-form production floor checklist | Extra acceptance items for CS short-form | B | Mandatory when CS short-form enabled | MONO | Literal | §3.1, §4.4, §12.2 |
| XD-15 | AI-content class — tightening override only | Realistic-synthetic derivation; theme may only tighten | C | Engine-derived; no override set | MONO | N/A | §3.3, §7.7, §14.6 |
| XD-16 | AI-label-required flag & packaging checklist | Platform label obligation, auto-set | C | Set automatically from AI-content class | MONO | N/A | §3.3, §7.2, §7.7 |

*† XD-04: the values are platform facts (character limits, aspect ratios), not tenant choices. Recommend Tier-C reclassification alongside XM-08/09 below; see CFG-OD-2.*

### 1.4 Output/runtime — video & media production (`§10.4`, table 2) — `CFG-XM-01`…`18`

| ID | Knob | What it controls | Tier | Default | Regime | Auth. | Consumed by |
|---|---|---|---|---|---|---|---|
| XM-01 | Recipe per language | Which of three production paths a language uses | B | EN generative-clip; CS carousel-to-reel (D-14) | REG | Either | §4.8, §12.2 |
| XM-02 | Audio policy per language | Native speech / TTS / none; CS native speech banned | B | EN may use native speech; CS never | REG | Either | §4.8, §14.5 |
| XM-03 | TTS provider & voice identity per language | Provider/voice for the verified script; licensed-catalogue only | B | Primary + cost/fallback tier (OD-13, trial-gated) | REG | Either | §4.8, §5.1, §5.3, §16 |
| XM-04 | Caption timing source per language | Native timestamps / forced alignment / slide-timing | B | TTS-native where available | REG | Either | §4.4, §16 |
| XM-05 | Caption style & word-level reveal | Burn-in style; reveal unavailable on subtitles-only path | B | *(disposed, §3)* | LLW | Literal | §4.4, §13.2 |
| XM-06 | Adherence-similarity threshold | Script/audio similarity floor for QA-flag routing | B | *(disposed, §3)* | MONO | Literal | §4.4, §4.9 |
| XM-07 | QA-rejection cap | Regenerations per asset slot before terminal state | B | Two | MONO | Literal | §4.9, §12.4 |
| XM-08 | Music source & bed selection | Licensed library/generator only; no trending audio | **C†** | Licensed only | MONO | N/A | §4.4 |
| XM-09 | Loudness targets & QA tolerance band | Mastering target and fail-closed range | **C†** | −14 LUFS / −1.0 dBTP | N/A | N/A | §4.4 |
| XM-10 | Safe-box dimensions | Universal composition area | **C†** | ≈900×1400 centred | N/A | N/A | §4.4 |
| XM-11 | End-card recipe | Layered CTA shape, loop-friendly no-outro variant | B | Mid-video cue + 1.5–2.0s dual close | REG | Either | §4.4 |
| XM-12 | Shot count & clip length per asset type | Shots requested and duration | B | *(disposed, §3)* | LLW | Literal | §4.2, §4.3 |
| XM-13 | Hook overgeneration count | Hook candidates drafted before selection | B | Three to five | LLW | Literal | §4.2, §5.4a |
| XM-14 | Keyframe variant count | Keyframe options before acceptance | B | Two or three | LLW | Literal | §4.2 |
| XM-15 | Keyframe-acceptance policy per mode & rubric threshold | Human vs rubric-automatic approval | B | Human interactive; rubric-automatic unattended, ≥ floor | MONO | Literal | §4.2a, §4.9, §11.1 |
| XM-16 | Asset QA rubric thresholds | Machine accept/reject bar for finished media | B | At or above engine floor | MONO | Literal | §4.2, §4.4, §12.2 |
| XM-17 | Disclosure overlay text & placement — above engine floor | Exact wording/position/duration/contrast; tighten-only | B | Per language; mandatory; floor enforced | MONO | Literal | §4.4, §4.4a, §14.6 |
| XM-18 | Slide timing range for carousel-to-reel | Seconds per slide, hook held longer | B | 2.5–4 seconds | LLW | Literal | §4.5 |

*† XM-08/09/10: fixed technical/rights facts, not tenant-variable. Recommend Tier-C reclassification; see CFG-OD-2.*

### 1.5 Output/runtime — providers, tiers & money (`§10.4`, table 3) — `CFG-XP-01`…`19`

| ID | Knob | What it controls | Tier | Default | Regime | Auth. | Consumed by |
|---|---|---|---|---|---|---|---|
| XP-01 | Media router selection & per-theme override | Which router hosts routes | B | The v1 router (D-04a) | REG | Either | §5.1, §5.3 |
| XP-02 | Permitted tiers per mode (tier ceiling) | Highest auto-selectable tier; hero never auto | B | Standard; hero never auto | MONO | Literal | §4.6, §5.3, §8.11, §11.1 |
| XP-03 | Preferred routes within a tier | Which registry routes this theme prefers | B | *(disposed, §3)* | LLW | Literal | §5.3 |
| XP-04 | Hero auto-promote flag & per-run hero cap | Whether hero ever auto-selects; run cap | B | Off; cap per run | MONO | Literal | §4.6, §5.3, §11.1 |
| XP-05 | Media budget caps (asset/run/day/month) | Four spend ceilings, pre-submission enforced | B | Sized against trial envelope | MONO | Literal | §5.4, §8.11, §11.1, §12.3 |
| XP-06 | Text budget caps (run/day/month) | Token/currency ceilings, pre-call enforced | B | Sized against artifact count × gate profile | MONO | Literal | §5.4a, §8.11, §11.1, §12.3 |
| XP-07 | Per-stage text call ceilings | Max model calls per stage per run | B | Derived from candidate/asset counts | MONO | Literal | §1.5, §5.4a, §8.11 |
| XP-08 | Per-pack judge allowance | Judge-role calls per pack | B | Small fixed number | MONO | Literal | §5.4a, §14.2, §14.3 |
| XP-09 | Per-node per-call token ceiling | Bounded input/output size per node class | B | Engine floor with theme tightening | MONO | Literal | §1.5, §5.4a, §6.6 |
| XP-10 | Global cross-theme daily/monthly caps | Ceilings above per-theme ones | B | Mandatory once >1 theme | MONO | Literal | §5.4, §8.11, §13.1 |
| XP-11 | Unexplained-spend tolerance | Balance-delta divergence before circuit breaker halts | B | Directional: greater of a few cents or 10% | MONO | Literal | §5.6, §8.13, §15 |
| XP-12 | Refusal-ladder attempt cap | Paid attempts before degrading to plan-only | B | Three, terminating plan-only | MONO | Literal | §4.9, §5.6 |
| XP-13 | Poll interval & per-job poll budget | Async job check frequency and duration | B | ~30 seconds; bounded | LLW | Literal | §5.6, §8.13 |
| XP-14 | `submitted-unknown` resolution window | Re-query window before `paid-lost` | B | Bounded by provider deletion horizon | LLW | Literal | §8.5, §8.13 |
| XP-15 | Price-recheck cadence, grace, grace behaviour | Registry price re-verification and staleness handling | B | Monthly recheck; grace, not instant cut-off | MONO | Literal | §5.2, §15 |
| XP-16 | Rights-class allowlist per destination | Which licence classes reach which destination | B | *(disposed, §3 — restrictive)* | MONO | Literal | §5.3, §5.8 |
| XP-17 | Person-policy defaults per theme | No-people / adults-only / region-restricted defaults | B | Region-appropriate | MONO | Literal | §5.2, §5.3 |
| XP-18 | Fallback-router engagement threshold | Spend/reliability level to integrate fallback router | B | Named open item (§16) | LLW | Literal | §5.7, §16 |
| XP-19 | Trial budget envelope & reserve | Split between bake-off / real packs / reserve | B | ~$8 / $35 / $7 (W2-14) | MONO | Literal | §5.4, §17 |

### 1.6 Output/runtime — schedule, safety & runtime (`§10.4`, table 4) — `CFG-XT-01`…`25`

| ID | Knob | What it controls | Tier | Default | Regime | Auth. | Consumed by |
|---|---|---|---|---|---|---|---|
| XT-01 | Research-collection cadence | How often collection/ranking/dedupe run | B | **Off** (W2.5-7); daily once enabled | MONO | Literal | §8.2, §9.2, §13 |
| XT-02 | Pack-production cadence | How often the full pipeline runs | B | **Off** (W2.5-7); a few×/week once enabled | MONO | Literal | §8.2, §9.2, §13 |
| XT-03 | Theme timezone | Timezone the pinned run-date derives from | B | *(disposed, §3 — UTC)* | LLW | Literal | §8.3 |
| XT-04 | Mode | Which capability-matrix row applies | B | test | REG | Either | §11.1, §11.2 |
| XT-05 | Publish allowlist per mode | Exact destinations publishing may touch | B | Empty in test, by construction | MONO | Literal | §7.4, §11.1, §11.2 |
| XT-06 | Unattended draft-creation enablement | Whether an unattended run may create drafts | B | Off | MONO | Literal | §7.6, §9.2, §11.1 |
| XT-07 | Blog/site prep enablement | Whether an article draft artifact is produced | B | Off unless needed | LLW | Literal | §7.3, §3.2 |
| XT-08 | Notification channel & preferences | Push channel for "packs ready"/failure alerts | B | Email (W2.5-8), flag mandatory | LLW | Literal | §8.12, §12.1 |
| XT-09 | Anti-flap escalation counts | Consecutive identical degrades before escalation | B | Two | LLW | Literal | §8.12, §2.2 |
| XT-10 | Idempotency key composition per stage | Which inputs/versions form each stage's content-hash key | C | Per §8.5 | N/A | N/A | §8.5, §14.7 |
| XT-11 | Per-stage timeout & overall run ceiling | Stage/run time budgets before wind-down | B | *(disposed, §3)* | MONO | Literal | §1.5, §8.7 |
| XT-12 | Internal-iteration cap | Bounded self-critique for ranking/drafting only | C | Small; pipeline-enforced | N/A | N/A | §1.5 |
| XT-13 | Model selection per role per language | Drafting-role and judge-role route selection | B | Per language (OD-28) | REG | Either | §1.5, §5.1, §14.2, §14.7 |
| XT-14 | Stage enablement flags for partial runs | Research-only / spin-only / regen-media-only | B | Full run | LLW | Literal | §1.5, §9.1 |
| XT-15 | Voice regenerate cap per artifact | Judge-driven regeneration ceiling, per artifact | B | Small; escalate to review on exhaustion | MONO | Literal | §14.2, §12.4 |
| XT-16 | Per-pack voice-regenerate allowance | Pack-level regeneration ceiling across artifacts | B | Small fixed number | MONO | Literal | §14.2, §14.3, §6.7 |
| XT-17 | Combined per-artifact repair ceiling | Repairs counted across spin/claim-1/voice/claim-2 | B | Small fixed number | MONO | Literal | §6.10, §14.0 |
| XT-18 | Cross-pack recurrence window & similarity threshold | House-style-tic comparison window/sensitivity | B | *(disposed, §3)* | MONO | Literal | §14.2 |
| XT-19 | Judge flag-rate ceiling | Rolling flag rate above which the judge is suspected | B | Calibrated from golden set | MONO | Literal | §14.2, §17 |
| XT-20 | Prompt-pattern & rubric version pinning | Every artifact records prompt/rubric/model version | C | Always on | N/A | N/A | §14.7, §8.5 |
| XT-21 | Confidence-gated digest defaults | Pre-selected/unselected/detail-required per band | B | High pre-sel.; medium unsel.; low detail-req. | LLW | Literal | §12.1 |
| XT-22 | Pack upload enablement | Whether a pack is written back into the KB | B | Off (later phase) | LLW | Literal | §12.6 |
| XT-23 | Retry attempt caps & retry-time budget per call class | Submission-call backoff, separate from job polling | B | *(disposed, §3)* | MONO | Literal | §8.10 |
| XT-24 | Failed-unit share threshold | Failure share escalating asset→stage/run failure | B | *(disposed, §3)* | MONO | Literal | §8.10 |
| XT-25 | Per-language minimum evidence-and-volume band | Floor on clearing candidates and corroborating families | B | Deliberately loose; alarmable | MONO | Literal | §2.7, §12.1 |

### 1.7 Machine/runtime block (`§10.4a`, not part of a theme) — `CFG-MC-01`…`05`

| ID | Knob | What it controls | Tier | Default | Regime | Auth. | Consumed by |
|---|---|---|---|---|---|---|---|
| MC-01 | Low-disk threshold & reserved ledger headroom | Free-space level halting submissions; reserved headroom | C | Per machine | N/A-machine | N/A | §8.10 |
| MC-02 | Log verbosity & retention | File-log detail and duration; secrets always redacted | C | Per machine; secrets redacted | N/A-machine | N/A | §1.5, §8.9 |
| MC-03 | Secrets location & permission policy | Where secrets live; which account may read them | C | Permission-restricted to run-as account | N/A-machine | N/A | §8.9 |
| MC-04 | Launcher & interpreter path resolution | Runtime discovery, absolute paths, exit-code propagation | C | Absolute paths from configuration | N/A-machine | N/A | §1.4, §8.1 |
| MC-05 | Working & output root locations | Where run folders/packs/ledgers are written | C | Per machine | N/A-machine | N/A | §8.6, §12.5 |

### 1.8 Engine-level settings (`§10.5`) — reference list, not authoring rows

Per the task's instruction, §10.5 is prose, not a table, and its contents are not counted in the 141/178 totals — they were never rows to begin with. Named here for completeness, all Tier C: the model registry and route records; the four routing contracts; rights-class definitions and the person-policy constraint layer; the v1 likeness/voice-clone ban; tier definitions; the refusal ladder's shape; submission pacing rate and download-queue drain policy; the dry-run default per mode; the AI-content-class derivation rule; the engine-level disclosure floor; the keyframe-acceptance rubric's contents; negative-prompt layers 1–3 and the four skill bundles' shared pattern sets; the do-not-scrape list and method-evaluation gate; the canonical stage order, per-asset gate chain, and repair re-entry rule; the nine exit-code classes; overlap and missed-run policies; the language overlay's contents per language; the mode capability resolver.

---

## 2. New playbook-layer knobs

### 2.0 Where each comes from, and what was filtered out

Sources: `00_MASTERPLAN.md` §8 (the knob-count claim itself); `03_pipeline_and_gates.md` §6.2 (ranking-profile knobs, verbatim table) and §10.1 (the wire-in table naming what §10.2/§10.3/§10.4/§10.5 gain); `05_query_steering.md` §5 (collection mode, query profile, structured topic object) and §6.5 (wire-in). Where `01_content_ontology.md` is the only source for a concept (relation types, archetypes, angles, genres, CTA vocabulary, objectives), it is used **only as filtered by `00_MASTERPLAN.md` §3/§4**:

- **Relation-type set is five, not seven** (`00_MASTERPLAN.md` C-2): offer-attachment · inventory/availability · expressive-aesthetic · commentary-observation · product-promotion. Annex `01`'s R-6 (education) and R-7 (testimonial) are not separate relation types under the ruling — C-2 requires the reconciler to state where their content lives, which `04_RECONCILIATION.md` has not yet done (it does not exist — `00_MASTERPLAN.md` §0). `CFG-PS-03` below is scoped to the five, with a note that R-6/R-7's disposition is a Wave-0 dependency this file cannot pre-empt.
- **No criterion in the PROOF/NEXT-STEP/GLUE families may be waived by objective, relation, archetype, angle or genre** (C-3). Annex `01` §1's per-objective table ("proof discipline disabled," "hype-glue rule waived") is struck as written; `CFG-PS-06` below is scoped to genre-variable families only, and is Tier B/REG, never a proof-family waiver.
- **CTA class count.** `CONDUCTOR_RULINGS.md`'s preamble states "operator-authored CTA table with 10 classes" — binding text. Annex `01` §6's own table has eleven rows under a "Ten CTA classes" heading, and `00_MASTERPLAN.md` §4 already flags this exact miscount as a Wave-0 barrier item. `06D_cta_authoring.md` (a parallel deliverable in this same wave) independently argues the count should be twelve, restoring an "Event" class. This file does **not** resolve that count — it is Wave-0's job — and represents the CTA-class-enablement knob (`CFG-PO-06`) with its member-count marked pending. See `CFG-OD-3`.
- **Genre count.** Six genres (analytical-B2B, sensory-hospitality, evocative-expressive, creator-casual, product-persuasive, educational-structured), matching `00_MASTERPLAN.md` §8's "six genres × two languages" framing exactly — no contradiction found here.
- **Objective count.** Five, unchanged from annex `01` §1 — no contradiction found.

### 2.1 New research-block additions — `CFG-PR-01`…`16`

| ID | Knob | What it controls | Tier | Default | Regime | Auth. | Consumed by |
|---|---|---|---|---|---|---|---|
| PR-01 | Calendar register contents & horizon | Occasion entries and how far ahead they're considered | B | Empty until populated (feature inert) | LLW | Literal | 03§10.1, 03§2.3 |
| PR-02 | Evergreen library contents, rest intervals, review-by dates | Library entries and their reuse floor | B | Empty until populated; engine floor on min. rest interval | LLW | Literal | 03§10.1, 03§2.3 |
| PR-03 | Trigger-lane enablement per language | Which of trend/occasion/library lanes are active | B | Trend on (existing behaviour); occasion/library off | LLW | Literal | 03§1.6, 03§10.1 |
| PR-04 | Ranking-profile selection per language per trigger class | Which registered profile scores a lane's candidates | B | Trend profiles per existing per-language rule | REG | Either | 03§6.2, 03§13.2 |
| PR-05 | Occasion-proximity window shape | Lead-in length, anchor emphasis, tail length | B | Per-entry, per-theme default; engine floor on tail | LLW | Literal | 03§6.2 |
| PR-06 | Rotation-rest curve | Min. rest interval and saturation point (library) | B | Per-item, per-theme default; engine floor on minimum | LLW | Literal | 03§6.2, 03§2.8a |
| PR-07 | Demand-modifier enablement per profile | Whether the demand modifier applies to a lane | B | On: trend, occasion; **off: library** | LLW | Literal | 03§6.2 |
| PR-08 | Top-N cap per language per lane | Candidates a lane carries forward | B | Lane caps small; sum ≤ per-run ceiling | MONO | Literal | 03§6.2, 05.4a, §12.1 |
| PR-09 | Monitor-only band boundary per lane | Watched-but-not-generated range, per comparison class | B | Per lane | LLW | Literal | 03§6.2 |
| PR-10 | Per-run topic ceiling | Bound on the sum of all lane caps | B | At or below today's per-language figure | MONO | Literal | 03§6.2, §5.4a, §12.1 |
| PR-11 | Collection mode per source | Steered / discovery / both | B | Per existing source's actual capability (fact, not choice) | REG | Either | 05§5.1, 05§6.4 |
| PR-12 | Query profile per source per language | Field, syntax, time window, engagement threshold, cap, cost, language handling | B | Per source, empirically verified where possible | LLW | Literal | 05§5.2 |
| PR-13 | Topic entry — per-language surface forms | Actual wire strings per language, not translations | **A** | *(see §4)* | LLW | Literal | 05§5.4 |
| PR-14 | Topic entry — aliases, entity names, negative terms | Local-filter input; the homonym killer | **A** | Negative terms empty is a readiness-flaggable gap, not silently accepted | UNION | Literal | 05§5.4, 05§5.3 |
| PR-15 | Topic entry — per-source query-field overrides | Per-source phrasing of one topic (slug/phrase/sentence/string) | B | Canonical surface form used unmodified per source | LLW | Literal | 05§5.4 |
| PR-16 | Tenant-register connector — budget, cadence, failure/swap path | The fourth connector class (C-8); its own operational envelope | B | *(disposed pattern — off until a register is attached)* | MONO | Literal | 00§4 (C-8), 03§10.1 |

### 2.2 New spin-block additions — `CFG-PS-01`…`12`

| ID | Knob | What it controls | Tier | Default | Regime | Auth. | Consumed by |
|---|---|---|---|---|---|---|---|
| PS-01 | Playbook selection and version pin | Which registered playbook this theme runs; exactly one | **A** | *(see §4)* | REG | Either | 00§2 (PB-1, PB-7), 03§8 |
| PS-02 | Fact-schema profile selection | Obligation level per fact class; substitution rule content | B | Universal mandatory core present at mandatory level | REG | Either | 03§5.2, 03§10.1 |
| PS-03 | Relation-type set enablement | Which of the five registered relation types the theme uses | B | Playbook's declared default set | REG | Either | 00§3/C-2, 03§10.1 |
| PS-04 | Content-objective declaration (primary + secondary) | What a post exists to do; cascades to CTA legality, proof policy, voice | **A** | *(see §4)* | REG | Either | 01§1 (filtered by C-3), 03§10.1 |
| PS-05 | Vertical declaration | Which vertical(s) union to select the claim-pack set | B | Matches the declared playbook's default vertical | REG | Either | 00§4 (C-6), 03§10.1 |
| PS-06 | Criterion selections and bar choices (genre-variable families only) | Which registered member/bar is active per relation type | B | Playbook default set; PROOF/NEXT-STEP/GLUE families excluded from this knob's surface entirely (C-3, Tier C) | REG | Either | 03§3, 03§10.1 |
| PS-07 | Genre rubric-profile selection | Which of six registered genre rubrics judges a content stream | B | Playbook's primary genre; v1 calibrates two genres, rest inactive-ceiling | REG | **Resolver-derived** | 01§5 (filtered), 00§8, 03§10.1 |
| PS-08 | Recurrence-share band | Ceiling on declared-recurring slots as a share of a lane cap | B | Bounded by cadence × lane cap (readiness-enforced) | MONO | Literal | 03§2.8a, 03§10.1 |
| PS-09 | Relation-content mapping content | The theme's own lookup for whichever relation(s) it enables (generalises `CFG-SB-11`'s pain-to-offer for non-R-1 relations) | **A†** | *(see §4)* | LLW | Literal | 00§3, 03§10.1; see `CFG-OD-5` |
| PS-10 | Audience-descriptor registry selection | Which registered audience-descriptor entries apply, bound to S-2's per-relation bars | B | Playbook default | REG | Either | 00§4 (C-9) |
| PS-11 | Brand brief | The single bounded free-text field reaching generation nodes only | **A** | *(see §4)* | LLW | Literal (bounded text, CR-1/CR-8) | `CONDUCTOR_RULINGS.md` preamble, CR-8 |
| PS-12 | Configuration approval attestation | Who/when accepted the resolver's plain-language readback | **A** | *(see §4)* | LLW | Literal | CR-2 property 2 |

*† PS-09 is Tier A only where the theme's enabled relation set includes a relation that requires a content mapping at all (offer-attachment, inventory/availability, product-promotion); expressive-aesthetic and commentary-observation relations need none, per `01`§7 as filtered. The field is conditionally Tier A, not universally.*

### 2.3 New output-block additions — `CFG-PO-01`…`08`

| ID | Knob | What it controls | Tier | Default | Regime | Auth. | Consumed by |
|---|---|---|---|---|---|---|---|
| PO-01 | Archetype mix declaration | Ratio of posts per archetype across a rolling window | B | Uniform split across enabled archetypes | LLW | Literal | 01§3 (filtered), 03§10.1 |
| PO-02 | Archetype enablement/eligibility narrowing | Which (archetype × objective × destination) pairs a theme keeps from the playbook's permissive default | B | All playbook-registered pairs available (permissive default) | MONO | Literal | 01§3, 03§10.1 |
| PO-03 | Angle-type restrictions per playbook | Forbidden/weighted angle types, e.g. "avoid teaser in educational" | B | Playbook's dominant/uncommon weighting; uniform selection | MONO | **Resolver-derived** | 01§4 (filtered), 00§1 (P-8) |
| PO-04 | Bundle eligibility | Which of the seven skill bundles may serve a (relation × archetype) | C | Playbook-owned; not in theme authoring form | N/A | N/A | 03§7.3 |
| PO-05 | Per-injection-point overlay caps | Bounded brief length per generation node (IP-1…IP-7) | C | Engine ceiling; theme cannot raise it | N/A | N/A | 03§4.10, §5.4a |
| PO-06 | Next-step/CTA class enablement (registered CTA classes, count pending Wave-0) | Which classes are legal where, superseding the four-class set | B | Content/product-path on; others off until preconditions resolve (extends `CFG-SB-13`) | REG | Either | 01§6 (filtered), 03§10.1; see `CFG-OD-3` |
| PO-07 | Eval-set and golden-set pointers per playbook per language | Frozen eval set; calibration corpus pointer | B | Engine-provided frozen set for calibrated genres; flag-rate ceiling recorded inactive for the rest (00§8) | LLW | Literal | 03§4.5, 03§10.1, 00§8 |
| PO-08 | Genre-negative prompt layer 3b contents | Playbook-level negative-prompt additions, additive over layers 1–3 | B | Empty beyond the playbook's own baseline | UNION | Literal | 03§7.3 |

### 2.4 The honest total

| | Count |
|---|---|
| Existing `§10.2`–`§10.4a` rows, mechanically counted | 141 |
| Pre-existing gap identified during this task (`CFG-SB-30`, brand & entity identity — never a §10 row) | 1 |
| New research-block knobs (`CFG-PR-*`) | 16 |
| New spin-block knobs (`CFG-PS-*`) | 12 |
| New output-block knobs (`CFG-PO-*`) | 8 |
| **Total** | **178** |

`00_MASTERPLAN.md` §8 quotes annex `01` as claiming *"eight new knobs"* (its own §8 wire-in row) while its own §11 Q5 says *"≈20 new knobs per theme"* — an internal contradiction the master plan already names and hands to this file to correct honestly (§7 reproduces both quotes). Annex `03`'s own text separately estimates *"roughly twenty more"* on top of `01`'s number. **The actual count, filtered through the corrections `00_MASTERPLAN.md` §3/§4 already impose and counted row by row rather than estimated, is 36 new knobs** (16 + 12 + 8) plus the one pre-existing gap this audit surfaced independently. None of "eight," "≈20," or "twenty more" survives contact with the real annex content once C-2's relation-type collapse, C-3's proof-family strike, and the query-steering annex's own additions are all applied. **178 is the honest total: old 141, plus one gap this task found, plus 36 genuinely new authoring decisions.** The eleven new readiness *assertions* `03_pipeline_and_gates.md` §8 adds are validation rules over this registry, not knobs in it, and are deliberately not counted here — the base plan already keeps §10.6 (knobs) and §13.2 (assertions) as two different jobs, and this file preserves that split.

---

## 3. The "no engine default" rows — disposition, not ~30 but 35

`CONDUCTOR_RULINGS.md` CR-5 cites *"the audit found ~30 of 141 knob rows"* reading "Per theme; no engine default" or equivalent. A row-by-row read of every Default cell in the seven §10.2–§10.4a tables (reproduced in §1) finds **35** — every row whose Default column is a bare "Per theme" / "Per source" / "Per fact class" / "Per vendor" / "Per signal class" / "Per destination" / "Per call class" with no elaboration, plus the two rows using the literal audit phrases. Excluded from this list, deliberately: rows reading "Per §X" (these point at real, defined content elsewhere in the document, not an unfilled form — e.g. `RB-05`'s "Per §2.3" means "follow the source portfolio §2.3 already specifies"); rows already carrying an explicit "directional starting point, not an empirical finding" framing (e.g. `RB-17` the brand-fit floor) — that framing **is** CR-5's disposition (b) already applied, just not literally blank; rows reading "small fixed number" — the plan's own established idiom for "there is a default, it is deliberately small and left unnumbered," which is disposition (b) already in force, not an unfilled cell; and the five `§10.4a` machine-block rows, which are legitimately per-machine (not per-tenant identity gaps) and sit outside the theme layering stack entirely (§0).

| # | ID | Knob | Disposition | New treatment |
|---|---|---|---|---|
| 1 | RB-01 | Watch topics, keywords and entities | **(a) Tier A** | Identity-shaped; no vertical-neutral default is coherent. See §4 field 4. |
| 2 | RB-11 | Per-source circuit-breaker threshold | (b) concrete default | 3 consecutive failures within one run, mirroring the plan's own small-integer convention (QA-rejection cap = 2, refusal-ladder cap = 3). |
| 3 | RB-13 | Collection wall-clock ceiling | (b) concrete default | Directional starting point, calibration starting point — same footing as the brand-fit floor; bounded so ranking always has something to run on. |
| 4 | RB-14 | Cache TTL per signal class | (b) concrete default | Equal to that signal's own per-source cadence (`CFG-RB-06`) — cached until the next scheduled poll, no invented number needed. |
| 5 | RB-15 | Topic dedupe lookback window | (b) concrete default | 90 days, reusing the normalised-signal-record retention window (`CFG-RB-25`) as the anchor rather than inventing a new figure. |
| 6 | RB-19 | Corroboration bonus magnitude | (b) concrete default | Directional starting point, calibration starting point (same footing as the brand-fit floor). |
| 7 | RB-21 | Monitor-only band boundary | (b) concrete default | Directional starting point, calibration starting point. |
| 8 | RB-22 | Absolute-band fallback thresholds | (b) concrete default | Directional starting bands per source, same convention `RB-16`'s freshness half-life already uses. |
| 9 | RB-23 | Demand-modifier weight | (b) concrete default | Directional starting point, calibration starting point. |
| 10 | RB-27 | MCP-source credit budget per month & pacing | **(c) ships off** | Zero spend (source degrades to skip/off) until a human sets a per-vendor cap — matches §10.1's own placement rule that anything able to spend money defaults safe. |
| 11 | RB-28 | Vendor roster last-verified/recheck-by | (b) concrete default | Monthly recheck with a grace period, reusing `XP-15`'s already-stated price-recheck convention. |
| 12 | SB-01 | Brand-truth source pointers & designated fact locations | **(a) Tier A** | Identity-shaped; points at a specific tenant's private knowledge base. See §4 field 2. |
| 13 | SB-04 | Stale-warn / hard-stale thresholds per fact class | (b) concrete default | Warn at the interactive offline-window anchor (14 days, `SB-05`); hard-stale at roughly double, per fact class, tunable down (tighten-only). |
| 14 | SB-08 | Hard-excludes baseline | **(a) Tier A** | Legal/reputational identity; "empty" and "reviewed-and-confirmed-empty" are materially different commitments. See §4 field 8. |
| 15 | SB-11 | Pain-to-offer relation | **(a) Tier A, conditional** | Required only when the theme's enabled relation set includes offer-attachment; not applicable otherwise. See §4 field 11 and `CFG-PS-09`. |
| 16 | SB-16 | Person allowlist | (b) concrete default | Empty (nobody pre-cleared) — reuses `RB-02`'s existing "empty, distinguished from unresolved" convention. |
| 17 | SB-17 | Brand-and-domain routing map | **(a) Tier A** | Identity-shaped; a wrong default risks a CTA pointing at the wrong property. See §4 field 1. |
| 18 | SB-19 | Compliance obligations | (b) concrete default | All obligations presumed required (entity disclosure, affiliate disclosure, AI-labelling) until a theme narrowly states one does not apply; "stricter wins" already governs conflicts. |
| 19 | SB-21 | Exemplar corpus pointer per language | **(c) ships off** | No exemplar corpus configured by default; style-matching is skipped and corpus-leakage checking is vacuously satisfied. Argued in full at §4 (borderline case). |
| 20 | SB-24 | Snapshot reuse time-to-live | (b) concrete default | Reused for the remainder of the same calendar day, reusing the knob's own descriptive text rather than inventing a new figure. |
| 21 | SB-28 | Visual brand baseline | **(c) ships minimal** | No logo overlay or palette lock beyond the mandatory disclosure/safe-box floor until a theme supplies brand assets — a wrong logo is worse than none. |
| 22 | SB-29 | Voice rules and banned phrasing (theme additions) | (b) concrete default | Empty; the theme relies on the shared language-overlay slop lexicon alone until it adds its own. |
| 23 | XD-05 | Link policy per destination | (b) concrete default | Link in the asset/caption itself, not first-comment, until a theme states otherwise. |
| 24 | XD-06 | CTA placement convention per destination | (b) concrete default | Single CTA at the end of the asset (final caption line / final slide / outro card). |
| 25 | XD-08 | Per-language volume targets | (b) concrete default | Directional starting point (a small number, calibration starting point) — avoids inventing a precise weekly count. |
| 26 | XM-05 | Caption style and word-level reveal | (b)+(c) hybrid | Standard burned-in captions are the safe base (disclosure floor requires legible captions regardless); word-level reveal — the enhancement — **ships off**. |
| 27 | XM-06 | Adherence-similarity threshold | (b) concrete default | Directional starting point, calibration starting point, same footing as the brand-fit floor. |
| 28 | XM-12 | Shot count and clip length per asset type | (b) concrete default | A small fixed per-type default, explicitly labelled directional/calibration starting point, anchored to the existing hook-overgeneration (3–5) and keyframe-variant (2–3) conventions rather than inventing an authoritative production spec. |
| 29 | XP-03 | Preferred routes within a tier | (b) concrete default | Registry order — the engine's own default route order within the tier governs when a theme states no preference. |
| 30 | XP-16 | Rights-class allowlist per destination | **(c) ships restrictive** | Only the licensed-catalogue rights class reaches any destination by default, consistent with the v1 likeness/voice-clone ban already being the safety floor. |
| 31 | XT-03 | Theme timezone | (b) concrete default | UTC until set — safe because both cadence knobs (`XT-01`/`XT-02`) default off, so nothing schedules against the wrong timezone before a human sets one. |
| 32 | XT-11 | Per-stage timeout and overall run ceiling | (b) concrete default | Directional default, calibration starting point; bounded so a run finishes within one scheduling cycle. |
| 33 | XT-18 | Cross-pack recurrence window and similarity threshold | (b) concrete default | Rolling 30-day window; similarity threshold as a calibration starting point, same footing as the brand-fit floor. |
| 34 | XT-23 | Retry attempt caps & retry-time budget per call class | (b) concrete default | Small fixed retry cap with backoff, per call class, bounded within the per-stage timeout — mirrors the QA-rejection-cap and refusal-ladder conventions already in force. |
| 35 | XT-24 | Failed-unit share threshold | (b) concrete default | Directional starting point, calibration starting point, same footing as the brand-fit floor. |

**Tally:** 5 promoted to Tier A (rows 1, 12, 14, 15, 17) · 5 dispositioned as feature-ships-off/restrictive (rows 10, 19, 21, 26, 30) · 25 given a concrete safe default. **35, not ~30 — report the real count, per the task's own instruction.** The gap is modest (35 vs. "~30," a 17% undercount against the audit figure) and does not change CR-5's underlying finding that the "no engine default" cell must be abolished; it only corrects how many cells actually said so.

---

## 4. Tier A — the must-answer set

**Twelve fields**, at the ceiling CR-5 sets, one field above the operator's own ten-field draft and matched exactly to `06C_authoring_form.md`'s independently-derived twelve-field form (Fields 1–12) — the two documents were built from the same source material without coordination and converged on the same count and, largely, the same fields; that convergence is itself evidence the set is right-sized rather than padded. Each field states what breaks if it is wrong, not merely that it is required, per the task's own instruction.

| Field | Knob ID(s) | Question the field answers | Authoring mode | What breaks if wrong |
|---|---|---|---|---|
| **1. Identity** | `CFG-SB-30` (new) + `CFG-SB-17` | Legal entity, brand name(s), which brand owns which domain | Literal | A CTA, an AI-disclosure label, or an affiliate disclosure attributes copy to the wrong legal entity; a multi-brand tenant's routing map has nothing correct to route against. This field is **absent from §10 entirely today** — no existing row states it — which is a pre-existing gap this audit found independently of the playbook layer (§2.4). |
| **2. Brand-truth location** | `CFG-SB-01` | Where does brand truth (offers, capabilities, ICP, claims) actually live, per fact class | Literal | Brand-truth resolution reads nothing (safe: research-only forever, per P-1) or, worse, under-specified pointers silently resolve against the wrong tenant's workspace. |
| **3. Output languages** | `CFG-RB-03` | Which languages this theme produces | Literal | A listed language with no real content behind it dies quietly by arithmetic while every policy document still calls it first-class (the exact failure §2.7/W2-07 names); an unlisted language never gets a first-class asset matrix, violating D-02. **§10's own recorded "default" here — "First theme: Czech and English" — is a historical fact about theme #1, not a genuine engine default a new theme could safely inherit; this file disagrees with treating it as anything but Tier A.** |
| **4. Watch topics, per-language surface forms, negative terms** | `CFG-RB-01`, `CFG-PR-13`, `CFG-PR-14` | The subject matter, in the actual wire-language phrasing, with the homonym killers named | Literal | Per P-12: sources are sent no query or the wrong one, discovery feeds are filtered by nothing, every irrelevant item pays for a per-candidate LLM brand-fit call, and an un-negated homonym ("agents") silently collects the wrong domain's content indefinitely. |
| **5. Playbook / kind of business** | `CFG-PS-01` | Which registered playbook this theme runs | Either | The wrong criterion set, fact-schema profile, CTA vocabulary and genre registry apply; e.g. a restaurant configured under the B2B playbook has every candidate evaluated for a connection chain to a nonexistent offer and fails closed on everything — P-1's failure mode, reintroduced by misconfiguration instead of engine limitation. |
| **6. Content objective** | `CFG-PS-04` | What a post exists to do (one of five, plus optional secondaries) | Either | The wrong CTA classes become legal, and the operator's digest measures the wrong thing (click-through reviewed for a community-objective theme, engagement reviewed for a lead-gen one). The non-waivable PROOF/NEXT-STEP/GLUE floor (C-3) holds regardless, so this field cannot itself create an unlawful claim — but it can still make a coherent theme produce content nobody asked for. |
| **7. Destinations** | `CFG-XD-01` | Where output goes, per language | Literal | Assets are produced for platforms the tenant doesn't operate on (wasted spend) or a platform the tenant depends on gets nothing; readiness's "every configured language produces a non-empty, quality-gated asset matrix" assertion is meaningless against the wrong set. **This file promotes `XD-01` to Tier A** even though §10 records a soft default ("Per §3.2") for it, on the same reasoning as field 3: destinations are identity-shaped (a restaurant on Facebook is not a fallback state of a SaaS on LinkedIn), and no vertical-neutral default set is coherent. |
| **8. Hard excludes** | `CFG-SB-08` | What this brand never says, ever | Literal | The one thing a brand can never legally or reputationally say is unprotected; because this array is additive-union (§5), absence here is never compensated by a later layer — nothing downstream can retroactively add an exclude the theme never named. |
| **9. CTA destinations that genuinely exist** | `CFG-PS-09` + brand-truth offer data (field 2) + the CTA-precondition readiness check (03§8) | Which CTA targets — URLs, booking, ordering, location — are real and live | Literal | A CTA points at a URL, booking system, or location that 404s or doesn't exist, degrading into the permanent-and-invisible funnel gap §13.2 already names, unless the theme also carries the dated language-completeness acceptance banner. This is a **composite** field — it is not satisfied by a single §10 row, and this file does not force one. |
| **10. Brand brief** | `CFG-PS-11` | One bounded free-text paragraph of guidance, generation nodes only | Literal (bounded text) | Without it, N-3/N-5/N-6 have nothing brand-specific to draw on beyond the exemplar corpus — itself Tier B, ships off by default (§3) — and output regresses toward the shared language overlay's generic voice: safe, but indistinguishable from any other tenant's. |
| **11. Relation-content mapping** | `CFG-PS-09` (conditional; generalises `CFG-SB-11`) | The theme's own lookup content for whichever relation(s) it enables — pain→offer for offer-attachment, inventory source for inventory/availability, etc. | Literal ("a relation, never an inference" — §10.3's own words for the pre-existing instance) | For an offer-attachment or product-promotion relation, the spin mapper has nothing to attach an offer to a pain or inventory signal with — exactly P-1's failure mode (INSUFFICIENT → research-only forever → may never be scheduled). Not required for expressive-aesthetic or commentary-observation relations (§2.2 footnote). |
| **12. Configuration approval attestation** | `CFG-PS-12` | Who accepted the resolver's plain-language readback, and when | Literal | Without a recorded acceptance, CR-2 property 2 ("the resolved config is inert until the operator accepts it") has nothing to point at — a resolved config could be treated as live without anyone having actually read the readback, defeating the entire purpose of CR-2. |

### 4.1 The operator's borderline cases, argued

- **Budget caps.** The operator's position — Tier B with a low safe default — is already what §10 does: `CFG-XP-05`/`XP-06` read "sized against the trial envelope" / "sized against the artifact count × gate-stack profile," both real, both MONO (tighten-only across layers), neither blank. **Confirmed, no change.**
- **Cadence.** The operator's position — Tier B, defaulting off — is already what §10 does: `CFG-XT-01`/`XT-02` read "**Off** (W2.5-7)," an explicit, named operator decision. **Confirmed, no change.**
- **Exemplar-corpus pointer.** The operator's draft did not list this as Tier A but flagged it as a case to check. This file finds it **Tier B, ships off** (§3, row 19), not Tier A: the corpus is style-only, never a fact source (§6.11), and a theme can produce entirely coherent, safe output with none configured — voice is still governed by the language overlay and the theme's own banned-phrasing additions. Promoting it to Tier A would push the ceiling past twelve for a field whose absence degrades gracefully rather than breaking anything. **Recommend the operator confirm this reading — it is the one place this file's judgment call is closest to a coin flip** (`CFG-OD-6`).
- **Publish allowlist.** Not argued for Tier A by the operator, and this file agrees: `CFG-XT-05` is Tier B, "empty in test, by construction" — a real, safe, MONO-regime default that requires no per-theme decision until the theme is genuinely ready to publish. **Confirmed, no change.**

---

## 5. The resolution algorithm, as a table

| Regime | What it means | Which layers may write | What happens on conflict | Worked example |
|---|---|---|---|---|
| **MONO** — monotonic-tighten-only | A floor may only rise, a ceiling may only fall, as a value passes through later layers | Engine sets the floor/ceiling; playbook, theme, language overlay, and per-destination override may each tighten further | The strictest value across every layer wins automatically; no negotiation, no averaging | `CFG-SB-06` (confidence band floor per mode): engine states "below PARTIAL degrades to research-only unattended"; a theme may raise its own floor to require PARTIAL-or-above for every mode; a per-destination override could raise it further for one risk-sensitive destination, but no layer may lower it below the engine's floor. |
| **REG** — registry-selection | A layer selects one member of an engine-owned, closed, versioned set; it may never author a new member | Playbook selects a default member; theme may re-select a different registered member; per-destination override may select a different member where the registry supports per-destination variance; language overlay generally does not touch these (they are shared) | The most specific layer's selection governs for that field, but only among registered members — an attempted non-member value is refused and named per CR-7, never approximated to the nearest neighbour | `CFG-PS-07` (genre rubric-profile selection): playbook #1 (B2B lead-gen) selects analytical-B2B by default; a theme with a behind-the-scenes content stream may declare that subset judged against sensory-hospitality instead — both are registered members, and the universal slop floor (Tier 1, MONO) still applies underneath either choice. |
| **UNION** — additive-union | An array declared additive combines by set-union across every layer that contributes an entry; no layer may remove an entry a different layer added | Any layer — engine, playbook, theme, language overlay, per-destination — may append | There is no "losing" entry; the only failure mode is a later layer's content (e.g. an offer, a CTA) relying on something an earlier layer's excludes forbids, which readiness catches, not the array logic itself | `CFG-SB-08` (hard-excludes baseline): the engine's own universal excludes (Tier 1) ∪ a playbook's genre-negative additions (`CFG-PO-08`) ∪ the theme's own excludes (this row) ∪ the language overlay's slop-lexicon exclusions all union together; a per-destination override may add further exclusions for that one destination but can never remove an exclusion a theme set globally. |
| **LLW** — last-layer-wins | A plain scalar, pointer, or non-safety array with no cross-layer composition logic; whichever configured layer is most specific governs | Any single layer may set it; earlier layers merely supply the fallback if a later layer leaves it unset | The most specific non-null value wins outright; if no layer sets it, the stated Default (§1, §3) applies | `CFG-XD-06` (CTA placement convention per destination): the engine has no opinion, the playbook has no opinion, the theme sets "end of asset" as house style; a per-destination override could set LinkedIn's placement differently (e.g. first line, not last), and that value governs LinkedIn alone while the theme's value continues to govern every other destination. |

**A fifth, informal category exists and is named rather than force-fit:** the five `CFG-MC-*` machine-block rows sit **orthogonal** to `engine → playbook → theme → language → destination` entirely, because they describe the computer a run executes on, not the tenant it executes for (§10.4a's own framing). CR-6's stack has nothing to say about them, and this file does not invent a regime for rows the stack was never meant to cover.

---

## 6. Authoring form vs. resolved form

Folded into the master tables in §1–§2 as an eighth column ("Auth.") rather than reproduced as a second ~178-row table. This extends the task's seven-column schema by one column; the seven required columns (ID, Knob, What it controls, Tier, Default, Regime, Consumed by) are present unmodified as columns 1–7 in every table above, with "Auth." appended as column 8 so the resolver author's question — *what must the resolver be able to produce for this field?* — has a direct answer next to every row rather than a second lookup. Three values, defined in §0 and applied via the stated general rule: **Literal** (arrays and scalars used verbatim, CR-4), **Either** (the operator may name a registry member directly or describe it in prose for the resolver to map, CR-7 governing the unmapped case), **Resolver-derived** (normally free text; the resolver's job is the mapping, reported at CR-2's readback). Tier-C rows carry **N/A** — they are not in the authoring form at all, per CR-5.

Two rows are flagged **Resolver-derived** explicitly, against the REG-implies-Either general rule, because the source annexes motivate them that way in prose rather than as a direct pick: `CFG-PS-07` (genre selection — annex `01`§5's own "how to use this layer" describes an operator declaring a content stream's *character*, not naming a genre by ID) and `CFG-PO-03` (angle-type restriction — the concrete example driving P-8's entire defect, "avoid teaser angles in educational content," is prose, not a registry ID).

---

## 7. Contradictions found

Per the task's instruction: recorded rather than papered over, both sides quoted verbatim.

**1. `ARCHITECTURE_PLAN.md` §10.1 disagrees with its own tables.**
> `ARCHITECTURE_PLAN.md` §10.1: *"Counting the tables below gives **roughly 130 settings** across the four blocks plus the publish allowlist, the exemplar-corpus pointer and the shared language overlay..."*

Mechanically counting the same tables (§1.0 above) gives 141, not "roughly 130" — an 8% undercount inside the same document, against the same tables, in the same section. Two other documents already use the correct figure without flagging a discrepancy:
> `00_MASTERPLAN.md` §1: *"100 of ~141 knobs are vertical-neutral"*
> `CONDUCTOR_RULINGS.md` CR-5: *"The audit found ~30 of 141 knob rows..."*

This file uses 141 (§1.0) and recommends §10.1's sentence be corrected in the same pass that lands this annex.

**2. `01_content_ontology.md` disagrees with itself on the new-knob count, and `00_MASTERPLAN.md` reproduces both halves without resolving them.**
> `01_content_ontology.md` §8 (wire-in table, re §10.3): *"Existing knobs unchanged; **eight new knobs** added"*
> `01_content_ontology.md` §11, Q5: *"The playbook layer adds configuration surface (**≈20 new knobs per theme**) but removes engineering."*
> `00_MASTERPLAN.md` §8: *"`01` itself says the layer adds "≈20 new knobs per theme," `03` adds roughly twenty more..."*

`00_MASTERPLAN.md` §8 already names the contradiction between `01`'s own two figures but does not correct it — it moves straight to citing `01`'s larger number and adding `03`'s estimate on top, without noting that "eight" and "≈20" cannot both describe the same wire-in table. This file's own count (§2.4) is 36, arrived at by counting the actual new rows in the annexes as filtered through the binding corrections, not by re-asserting either annex figure.

**3. The CTA-class count is wrong in three different ways inside one section of one annex.**
> `00_MASTERPLAN.md` §4 (Wave-0 barrier, already flagging this): *"the annexes miscount their own registries in at least four places — 'five genres' listing six, 'ten CTA classes' over an eleven-row table, 'eight new fact classes' over nine"*
> `01_content_ontology.md` §6: *"**Ten CTA classes**, each with preconditions and objective pairing"* — the table beneath this heading has eleven rows (verified by direct count during this task: Content, Product-path, Order/purchase, Reserve/book, Subscribe/join, Visit/directions, Follow/tag/save, Share/comment/tag, Engage via response, No-CTA, Commercial-incentive).

This file confirms the miscount by independent count and does not resolve it — `CFG-PO-06`'s member count is marked pending Wave-0, and `CFG-OD-3` records that a parallel deliverable in this same wave (`06D_cta_authoring.md`) has independently argued for a twelfth class ("Event"), which only deepens the case that this is Wave-0's decision, not a single leaf's.

---

## 8. Open questions — `CFG-OD-n`

1. **`CFG-OD-1`.** `CFG-SB-02` (access path per context) is listed as a per-theme knob in §10.3, but its value is locked by decision D-10 and does not actually vary per theme. Should it move to §10.5's engine-level list, the way the disk threshold and three siblings were carved into §10.4a? *Recommendation: yes — reclassify Tier C in the next §10 edit pass; nothing in this amendment depends on it staying theme-scoped.*
2. **`CFG-OD-2`.** `CFG-XD-04` (per-destination format profile) and `CFG-XM-08`/`09`/`10` (music/loudness/safe-box) state fixed platform or technical facts, not tenant choices, yet sit inside the theme's §10.4 tables. Should these be carved out the same way §10.4a carved out the machine block? *Recommendation: yes, same pattern, same rationale — copying a theme should not copy a platform's own character limit or a mastering target any more than it should copy a disk threshold.*
3. **`CFG-OD-3`.** The CTA-class registry count is unresolved across three sources (§7, item 3) and a fourth, independent leaf (`06D_cta_authoring.md`) argues for yet a different count (twelve). This file represents `CFG-PO-06` with the count marked pending. *Recommendation: this is squarely Wave-0's job (`04_RECONCILIATION.md` does not yet exist); no leaf, including this one, should guess.*
4. **`CFG-OD-4`.** `CFG-SB-30` (brand & entity identity) is a gap in the existing 141-row table, independent of the playbook layer entirely — no row in `ARCHITECTURE_PLAN.md` §10 today states legal entity or brand name(s) as a knob at all. Should it be added to `ARCHITECTURE_PLAN.md` regardless of whether Amendment B ships? *Recommendation: yes, in a small, independent edit — it is not playbook-layer scope and should not wait on Wave 2's merge.*
5. **`CFG-OD-5`.** `CFG-PS-09` (relation-content mapping) generalises `CFG-SB-11` (pain-to-offer relation) to cover relations that have no "pain" concept at all. Should `CFG-SB-11` be folded into `CFG-PS-09` at Wave-2 merge, or kept as the named R-1-specific instance with `PS-09` as a sibling field? *Recommendation: fold — two names for the same underlying "theme's own relation-lookup content" field invites drift — but this is `T6`'s call at the Wave-2 merge (§10.3/§10.4 rework), not this file's to force.*
6. **`CFG-OD-6`.** This file dispositions the exemplar-corpus pointer (`CFG-SB-21`) as Tier B, ships off by default, against the operator's own instinct that it might be borderline Tier A. For theme #1 specifically, the corpus is already populated, so this disposition changes nothing about theme #1's behaviour (the behaviour-preservation invariant holds) — it only affects new themes built after this amendment lands. *Recommendation: Tier B stands, but flagged for explicit operator confirmation since it is the single judgment call in this file closest to a coin flip.*
7. **`CFG-OD-7`.** `CFG-XP-16` (rights-class allowlist per destination) and `CFG-XP-17` (person-policy defaults) are classified MONO on the inferred principle that a rights or person-policy loosening should require the same logged rationale the brand-fit floor already requires (§10.1's placement rule). Neither `CONDUCTOR_RULINGS.md` nor `ARCHITECTURE_PLAN.md` states this explicitly for these two specific rows. *Recommendation: keep MONO — a rights-class or person-policy loosening is exactly the kind of thing that should require a logged rationale — but this is inferred, not quoted, and should be confirmed rather than assumed at Wave-2 merge.*
8. **`CFG-OD-8`.** `06C_authoring_form.md` (a parallel deliverable in this same wave) also uses the `CFG-OD-n` prefix for its own, separately-numbered open-questions list. The two lists are not yet in one namespace. *Recommendation: at whatever merge step plays the role `00_MASTERPLAN.md` §4/C-5 played for `PB-REL-n` vs. the risk log's `R-01…R-41`, renumber one of the two `CFG-OD-n` lists (e.g. this file's items become `CFG-OD-KR-n` for "knob registry") so a future reader can cite one without ambiguity.*

---

## 9. Summary

**Total knob count.** 178, honestly counted: 141 existing rows (confirmed by mechanical count against §10.2–§10.4a, correcting §10.1's own "roughly 130" self-claim by 11 rows) + 1 pre-existing gap this audit found independently (brand & entity identity, never a §10 row) + 36 genuinely new playbook-layer knobs (16 research, 12 spin, 8 output) — not the annexes' contradictory "eight," "≈20," or "twenty more" figures.

**Tier split.** Tier A: 12 fields (11 pre-existing-surface promotions/confirmations + 1 pre-existing gap, all argued in §4, converging independently with `06C_authoring_form.md`'s own 12-field form). Tier C: 12 rows (2 flagged-but-not-yet-reclassified theme-table rows plus 3 more recommended for the same treatment in `CFG-OD-2`, the 5 machine-block rows, and the explicitly engine-derived AI-content-class pair). Tier B: the remaining 154 rows.

**Defaultless-row disposition.** 35 rows found (not the audit's "~30" — the real count, per the task's own instruction to report it honestly), disposed as: 5 promoted to Tier A, 5 dispositioned feature-ships-off/restrictive, 25 given a concrete safe default reusing an existing anchor value wherever one existed rather than inventing a new figure.

**Open questions.** Eight, `CFG-OD-1` through `CFG-OD-8`, covering: two mis-scoped theme-table rows that are really engine facts; the CTA-class count (deliberately left to Wave-0, not guessed); the newly found brand-identity gap; whether the pain-to-offer row should fold into its generalised sibling; the one genuinely close judgment call (exemplar-corpus disposition); an inferred-not-quoted MONO classification for two rights/person-policy rows; and a namespace collision with a sibling document's own `CFG-OD-n` list.

**Contradictions found.** Three, all quoted verbatim in §7: §10.1's "roughly 130" against its own 141-row tables; annex `01`'s "eight new knobs" against its own "≈20 new knobs per theme"; and the CTA-class count disagreeing across three places in one annex section, independently confirmed here and left to Wave-0 rather than resolved by this file alone.
