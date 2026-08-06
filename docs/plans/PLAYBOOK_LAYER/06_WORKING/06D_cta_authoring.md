# 06D — CTA authoring: the operator table and its legal wrapper

**Status:** design-phase deliverable. No code, no schema, no CLI syntax. Prose and tables only, per `CONDUCTOR_RULINGS.md`'s standing constraints and the format `ARCHITECTURE_PLAN.md` §10 already uses.

**Amends:** `01_content_ontology.md` §6 (CTA vocabulary registry) and §10 item 6; `ARCHITECTURE_PLAN.md` §6.9 (spin application, CTA preconditions), §6.3 (fact class F-E), §6.10 (spin gate criterion S-6), §10.3 (spin block knobs), §13.2 (readiness), §12 (digest). Nothing here removes a control either document already specifies; every change is additive, in keeping with the playbook layer's own governing rule and with `02_legal_claim_packs.md` §1.1's monotonic pack discipline.

**Sits beneath:** `CONDUCTOR_RULINGS.md`, binding on every leaf, in particular CR-1 (authoring form / resolved form split), CR-3 (free text reaches generation nodes only, never gates), CR-4 (arrays are literal, never compiled), CR-5 (no "no engine default" cells), and CR-7 (the resolver selects from registries and fails closed on ambiguity). Where this document and CR-1…CR-8 appear to diverge, the rulings govern and this document is wrong.

**Evidence discipline.** This document inherits `02_legal_claim_packs.md` §0's confidence-marking convention (High / Medium-High / Medium / Low) wherever it cites an EU or Czech legal instrument, and reuses `02`'s own citations at their stated confidence rather than re-deriving them. Where a citation is new to this document and was not independently verified this session, it is marked accordingly and carried into §7 as a counsel item rather than asserted. Nothing below should be read as legal advice; it is a legal advisor's working design analysis for a qualified lawyer to confirm.

---

## 1. The operator-authored CTA table

### 1.1 What replaces the current lookup

Today, CTA class is one output of the pain-to-offer relation lookup: `(ICP segment × pain category) → (offer, preferred CTA class, owning brand and domain, preferred formats)` (`ARCHITECTURE_PLAN.md` §6.9). The operator may only enable or disable whole classes per destination and supply phrasing; class *selection* is an inference the spin mapper makes, not something the operator writes down.

The operator has decided to replace class selection with a table they author (`CONDUCTOR_RULINGS.md`, preamble: "operator-authored CTA table with 10 classes"). This section designs that table's shape, and — because CR-1 requires it — draws the line between what the operator authors (authoring form) and what the pipeline actually consumes (resolved form).

### 1.2 The key: archetype × objective, not archetype alone, not archetype × destination

**Ruling: the table's key is (post archetype × content objective).** Argued, not merely selected, because three other candidate keys were live options and each fails for a stated reason:

- **Archetype alone fails** because the archetype-to-objective mapping table (`01` §3) already shows one archetype serving several objectives with genuinely different correct CTAs. "Promotional" is primary under both lead-generation and direct-commerce, but a lead-gen promotional post wants product-path (a trial, a demo) while a direct-commerce promotional post wants order/purchase (a transaction) — the same archetype, two structurally different next steps. An archetype-only key would force one class across objectives that need different ones, or push the operator to special-case outside the table, which defeats the table's purpose.
- **Archetype × destination fails** because destination does not change *which kind of intent* a CTA embodies; it changes *how that intent renders* — whether the link is clickable in the caption, whether the destination even has a page in the asset's language, whether the destination's minimum mapping distance permits an offer to be loud at all (`ARCHITECTURE_PLAN.md` §3.3, §6.9). Those are rendering and eligibility questions already owned by two knobs that exist today — "CTA class enablement per destination per language" and "Minimum mapping distance per destination" (§10.3) — not questions about which *class* the operator intends. Folding destination into the key would multiply the table by roughly seven destinations and two languages for no safety gain, which directly conflicts with the operator's own stated constraint that "THE FILLING OF THE CONFIG MUST BE SUPER SIMPLE" (`CONDUCTOR_RULINGS.md` preamble) and with CR-5's ~10-field, hard-ceiling-12 Tier-A target.
- **Archetype × objective is correct** because objective is the axis that actually gates legality: each objective permits a distinct CTA class set (`01` §1, "Allowed CTA classes — each objective permits a different set; commercial-incentive is only legal in lead-gen and direct-commerce; engagement is lead-gen forbidden"). Keying on objective means every row the operator writes is checked against a real permission set at load time, and an operator who tries to pair "Follow/tag/save" with a lead-generation objective produces a **named, load-time readiness failure** (CR-7) rather than a silent runtime surprise.

**Row shape, two levels of specificity.** To keep the table small (CR-5), two row shapes are both legal:

- a **wildcard row** — `(archetype, *) → CTA class` — the operator's default for that archetype across every objective the archetype is permitted to serve;
- a **specific row** — `(archetype, objective) → CTA class` — an override for one archetype–objective pairing.

**Specific beats wildcard.** At resolution time, for a given asset's already-determined archetype and objective (both already resolved upstream by the spin mapper and the relation-type dispatch, `01` §2/§7), the resolver looks for a specific row first; if none exists, it falls to the wildcard row for that archetype; if neither exists, it falls to the engine-floor default (§1.4).

**Ties.** Two rows at the *same* specificity level for the *same* key are not resolved by the system picking one — per CR-7, the resolver never approximates. An operator table containing two specific rows for `(Promotional, Direct commerce)`, or two wildcard rows for `Promotional`, is an **authoring-form defect**, reported as a load-time readiness failure naming both conflicting rows verbatim, exactly the shape CR-7 mandates for internally contradictory guidance. A genuinely multi-objective theme (rare, per `01` §1) does not create this ambiguity by itself, because each asset carries one resolved objective by the time the table is consulted — the ambiguity only arises from operator authoring error, and that is exactly the case CR-7 says must surface rather than silently resolve.

### 1.3 Interaction with the existing per-destination knobs

The table's output is a **candidate class**, not a guarantee. Two existing knobs still gate it, unchanged in their own authority:

- **CTA class enablement per destination per language** (§10.3) is checked after the table produces its candidate. If the table selects Order/purchase for an archetype/objective pair but Order/purchase is disabled for TikTok in Czech, the asset on that destination-language pair enters the degradation ladder (§4) for that pairing specifically — the table's selection stands for every other enabled destination-language pair unaffected.
- **Minimum mapping distance per destination** (§3.3, §6.9) is not something the table can satisfy or override. A far-distance topic on a short-form destination still needs a named soft bridge before any offer-attached class may run there, regardless of what the table's row says; the table expresses *intent*, the spin gate's S-4 (distance compliance) and S-6 (next-step correctness) still adjudicate *legality* downstream (`ARCHITECTURE_PLAN.md` §6.10). The table is advisory input to spin, never a bypass of it.

This is the same authoring-form/resolved-form separation CR-1 already requires elsewhere: the operator's table cell is authoring form; the resolver compiles it into a registry-selected CTA class in the resolved config; the pipeline's gates then evaluate that selection against live facts exactly as they would evaluate any other class, table or no table.

### 1.4 The real default when the operator writes no table

CR-5 abolishes "no engine default" as an answer and requires either a real default or, for a knob that is genuinely identity-shaped, that the feature ships off. CTA class selection is close to identity-shaped — which CTA a tenant should push is close to who they are — but a genuine, safe default nonetheless exists, and CR-5 requires it be named rather than left unfilled:

**The engine-floor default, applied to every (archetype × objective) pair with no matching operator row, is No-CTA.**

This is defensible on its own terms, not merely convenient: No-CTA has zero preconditions, can never misfire, never invents a commercial ask, and is legal under every objective (`01` §6). It is also **visible, not silent**: CR-2's resolver readback ("you said X, I selected... CTA classes C") prints, at config load, that no table was authored and that every archetype therefore defaults to No-CTA — an operator who leaves the table empty sees that stated back to them in plain language before the resolved config is ever accepted, which is what makes an aggressively conservative default safe rather than a trap.

### 1.5 Wording: already permitted, not newly granted

The task of this table is **class selection only**. CTA **wording** is not a new authority this design creates — F-E already stores "literal phrasing per language" per (offer × destination × language) (`ARCHITECTURE_PLAN.md` §6.3), a Czech soft-CTA phrase bank already exists mapped to CTA classes (§3.4), and CR-4 already names "CTA wordings per language" as one of the arrays the resolver must carry verbatim and never paraphrase or compile. **What the operator table adds is which class applies where; what phrasing says for that class is, as today, a separate literal array under F-E and the phrase bank, authored freely within CR-4's discipline and untouched by this design.**

One correction is necessary, and it is stated once here because it recurs at §5.6 below: **"literal, never compiled" (CR-4) describes what the *resolver* does with the wording array — it does not describe what the *gate substrate* does with the resulting text.** CTA text is explicitly an in-scope surface for the claim gate and the Prohibited-Outcome Gate (`ARCHITECTURE_PLAN.md` §6.7: "a hashtag can carry a claim"; the gate runs over "post bodies, hooks, captions... CTA text"). An operator writing exact CTA wording verbatim under CR-4 does not exempt that wording from being checked; it only exempts it from being silently rewritten by the resolver before it is checked.

---

## 2. Resolving the CTA registry contradiction

### 2.1 The count is 12, not eleven, not ten, not nine

`01_content_ontology.md` disagrees with itself three ways, and a fourth document treats a class the registry has already dropped as still live:

| Location | Count stated | What it actually enumerates |
|---|---|---|
| `01` §6, prose immediately above the table | "Ten CTA classes" | — (the number is simply wrong against the table beneath it) |
| `01` §6, the table itself | 11 rows | Content · Product-path · Order/purchase · Reserve/book · Subscribe/join · Visit/directions · Follow/tag/save · Share/comment/tag · Engage via response · No-CTA · Commercial-incentive |
| `01` §10 item 6, summary | "Ten classes," nine actually listed | Merges Follow/tag/save and Share/comment/tag into one label ("follow/share/comment") and silently drops Engage via response entirely |
| `01` §8, §9.1 | "event" referenced as a live, enable/disable-able class ("CTA classes = content, product-path, commercial-incentive (no event until webinar facts exist...)") | No row for it anywhere in the §6 registry |

**Ruling 1 — the base registry is the §6 table, corrected to state its own count honestly: eleven, not ten.** The table's own contents are internally coherent (each row has real preconditions and an objective mapping); the "Ten" in the prose above it is the error and is struck.

**Ruling 2 — the §10 summary's merge is rejected; all three engagement-shaped classes stay distinct.** Follow/tag/save and Share/comment/tag both carry zero fact preconditions and MINIMAL-band eligibility — collapsing them costs nothing safety-wise, but Engage via response is not the same kind of class as either: it is the one engagement CTA that **actively solicits personal data** through the asset itself (a poll response, a form submission, a DM) and consequently carries a real precondition the other two do not — "privacy policy covers response data... if responses will be used for marketing follow-up, consent mechanism must be clear" (`01` §6). A merged "follow/share/comment" label that silently absorbed Engage via response would either strip that GDPR-relevant precondition from data-collecting CTAs (a control loosening, forbidden by the monotonic discipline every other layer of this system already applies) or force two genuinely zero-precondition classes to carry a privacy-notice requirement they do not need (safe direction, but a false alarm the operator will learn to ignore). Registry precision is a safety property here, not tidiness, so the three stay separate.

**Ruling 3 — "Event" is restored as its own twelfth class**, neither merged into Content nor demoted to a subtype. Reasons, all independently sufficient:

- Its precondition is materially stronger than Content's. `ARCHITECTURE_PLAN.md` §6.9 gives it an absolute rule with no equivalent elsewhere in the registry: *"A dated event fact with a registration URL exists and the date is in the future. No event fact, no event CTA — ever."* Content's precondition is only that a resource exists and its URL resolves. Folding Event into Content would silently drop the future-dating requirement — a control loosening, which nothing in this amendment is permitted to do.
- `ARCHITECTURE_PLAN.md` §6.7 check class 7 (temporal/availability) already names its home: *"The event CTA class lives here."* Deleting the class breaks an existing cross-reference rather than merely tidying an unused one.
- `02_legal_claim_packs.md` §4.1 defines its own new fact class F-S (booking/reservation availability) by **explicitly mirroring** it — *"Blocking for any asset carrying a booking-type CTA (mirrors the existing Event-CTA precondition)"* — which only makes sense if Event is understood as a live, ongoing pattern worth mirroring, not a deprecated one.
- Event and Reserve/book are close but not the same fact pattern: an event is one dated instance (a webinar, a launch), Reserve/book is a recurring, slot-based availability system (a table, an appointment). Conflating the two would blur a real distinction the new F-Q/F-S fact classes (§3 below) were built to keep separate.

**The canonical CTA class registry is therefore twelve members.** This corrects `01`'s own arithmetic; it does not reopen the operator's decision to adopt an operator-authored table, which is orthogonal to the exact class count and stands regardless of how this correction lands. `CONDUCTOR_RULINGS.md`'s "10 classes" almost certainly inherited `01`'s own miscount rather than reflecting a deliberate operator choice to exclude Event or to merge the engagement classes — this correction should be read back to the operator as a factual update, not a request to relitigate the mechanism.

| # | Class | Origin |
|---|---|---|
| 1 | Content | `01` §6 |
| 2 | Product-path | `01` §6 |
| 3 | Order/purchase | `01` §6 |
| 4 | Reserve/book | `01` §6 |
| 5 | Subscribe/join | `01` §6 |
| 6 | Visit/directions | `01` §6 |
| 7 | Follow/tag/save | `01` §6 |
| 8 | Share/comment/tag | `01` §6 |
| 9 | Engage via response | `01` §6 |
| 10 | No-CTA | `01` §6 |
| 11 | Commercial-incentive | `01` §6 |
| 12 | **Event** (restored) | `ARCHITECTURE_PLAN.md` §6.9, corroborated by `01` §8/§9.1 and `02` §4.1 (F-S) |

This ruling is binding on the rest of this document.

---

## 3. Per-class preconditions the operator can never override

The operator's table (§1) chooses a *candidate* class. Every candidate, regardless of which archetype/objective row selected it, is subject to the same fact-grounding, band, freshness and disclosure floor below — none of which the table, the wording arrays, or an interactive-mode operator override can relax (`ARCHITECTURE_PLAN.md` §6.4: human run overrides "may not create commercial facts," extended by `02` §2.4 to forbid creating a prohibited-outcome assertion under any override).

**Ordering, confirmed once here because §5 depends on it.** Fact-class preconditions (F-B, F-E, F-G, F-Q, F-R, F-S, F-T…) are resolved by the brand-truth resolver *before* generation begins (`ARCHITECTURE_PLAN.md` §6.1–§6.6) — they determine whether a class is *eligible* at all. The Prohibited-Outcome Gate (`02` §2) is a separate, later mechanism that runs over the *generated text* of the CTA itself, at every point the claim gate runs, and — per `02` §2.3 — always **before** check class 4's ledger lookup for that text. These two mechanisms answer different questions (is this class allowed to exist here, versus does this wording contain an unlawful outcome assertion) and neither can substitute for the other. A CTA class being fully precondition-satisfied (inventory verified, booking system live, discount terms resolved) has no bearing on whether its wording independently trips the Prohibited-Outcome Gate — confirmed further at §5.

| CTA class | Required fact class(es) — obligation | Confidence band floor | Liveness / freshness window · verifier | Required disclosures | Legal basis (confidence) |
|---|---|---|---|---|---|
| **Content** | Resource URL (F-K/F-E); site-first hold if owned-domain | Any (MINIMAL and above) | Targeted site verification, standard run cadence · site | AI-content label if resource is generated media | UCPD Art. 6/7, general misleading-omission (Medium-High, per `02` §1.2) |
| **Product-path** | F-B offer status (Blocking) · F-G price/trial terms (Constraining, site-verified) if stated | PARTIAL for the page; **FULL to state trial terms** | Destination URL, targeted verification window · site (F-B binding) | Class 1/2 grounding if any number stated | UCPD Art. 6(1)(b) (Medium-High); Dir. 98/6/EC price indication if pricing stated (Low-Medium, OD-L6) |
| **Order/purchase** | F-T product/SKU/stock (Blocking, specialises F-B) | PARTIAL; **FULL if price stated** | **4h verification window, unattended runs** · site- or feed-verified, per-item quarantine (`02` §5.2) | Guarantee/returns statement (F-U) where implied; check class 12 (depicted-attribute) if imagery accompanies | UCPD Art. 6(1)(b) (Medium-High); Dir. (EU) 2019/771 guarantee provisions (Low, unresearched — OD-L11); Dir. 98/6/EC Art. 6a if a reduction is stated (Low-Medium, OD-L6, **undesigned check — see §7 CFG-OD-L-4**) |
| **Reserve/book** | F-S booking/reservation availability (Blocking for this CTA) | PARTIAL | **2h verification window, unattended runs** · booking-system-verified where reachable, else operator-attested | Confirmation/cancellation method stated | UCPD Art. 6/7 (Medium-High); Czech booking/reservation-contract specifics **not researched — see §7 CFG-OD-L-2** |
| **Visit/directions** | F-R location (Blocking) · F-Q opening hours (Blocking whenever this class is used) | PARTIAL | **24h verification window** against Google Business Profile or equivalent · site-verified | None beyond standard | UCPD Art. 6/7, misleading availability (Medium-High); check class 7 temporal/availability (`ARCHITECTURE_PLAN.md` §6.7) |
| **Subscribe/join** | None in the F-taxonomy today (gap — see §5(c), §7 CFG-OD-L-1); system-live, opt-in, unsubscribe link (prose precondition, `01` §6) | PARTIAL | Standard targeted-verification window · site/system | GDPR Art. 13 notice at the destination; unsubscribe path present | GDPR Art. 6/7 (High); ePrivacy consent for e-marketing, Czech transposition **unverified — CFG-OD-L-1** |
| **Follow/tag/save** | None | MINIMAL | None meaningful | None | General UCPD floor only (no vertical basis) |
| **Share/comment/tag** | None; moderation strategy declared for unattended runs | MINIMAL | None | None | General UCPD floor only |
| **Engage via response** | None in the F-taxonomy today (same gap as Subscribe); form/poll live, privacy policy covers response data (prose precondition, `01` §6) | MINIMAL | Standard targeted-verification window (form/poll liveness) | GDPR Art. 13 notice covering the specific processing purpose | GDPR Art. 5/6/13 (High); ePrivacy for DM-based collection **unverified — CFG-OD-L-1** |
| **No-CTA** | None — always available | Any | n/a | None | n/a — the universal safe floor (§1.4) |
| **Commercial-incentive** | F-G discount/affiliate terms (**Blocking**, tightened beyond F-G's generic Constraining tier per `01` §6); recipient tracking/coupon system live | **FULL if any numeric term is stated** | Programme facts resolved, valid-from/valid-until dated · Notion ledger + site-verification for the number (class-2 self-sufficiency, `02` §5.1) | Affiliate/discount disclosure, check class 10 sub-class, commercial-communication statement catalogue | UCPD Art. 6/7 + Annex I blacklist pattern (Medium, OD-L5); Dir. 98/6/EC Art. 6a (Low-Medium, OD-L6, **undesigned — OD-L9, restated at CFG-OD-L-4**); Czech recognisability duty (Low-Medium, OD-25/OD-L7) |
| **Event** (restored) | Dated event fact + registration URL, date in future (Blocking, absolute — `ARCHITECTURE_PLAN.md` §6.9); no dedicated F-class home yet — **see §7 CFG-OD-L-3** | PARTIAL (reasoned analogy to Reserve/book; not separately stated in source) | Registration URL freshness window; date-in-future re-checked at spin time **and** at platform gate (`01` §6's general re-check rule) | None beyond standard | UCPD Art. 6/7, false-availability pattern (Medium-High); check class 7 temporal/availability |

---

## 4. The degradation ladder

### 4.1 The ladder, ordered and objective-bounded

`01` §6 states the rule qualitatively: an unmet precondition falls back "to a softer, available class, or to no-CTA, rather than blocking the asset." Made concrete:

| Tier | Classes | Rationale for placement |
|---|---|---|
| **5 — highest commitment / claim risk** | Order/purchase, Commercial-incentive | FULL band required whenever numeric; blocking fact classes; highest legal exposure per §3 |
| **4** | Reserve/book, Event | Blocking availability/date facts; PARTIAL band; absolute preconditions ("no event fact, no event CTA — ever") |
| **3** | Product-path, Subscribe/join, Visit/directions | PARTIAL band; blocking or gap-flagged facts, lower numeric exposure |
| **2** | Content | Universal, minimal precondition, any band |
| **1** | Engage via response, Share/comment/tag, Follow/tag/save | Zero-to-minimal fact preconditions; MINIMAL band |
| **0 — floor** | No-CTA | Always available, zero preconditions (§1.4) |

**Degradation moves down exactly one occupied tier at a time, and only within the asset's already-resolved objective's allowed class set** (`01` §1/§6). A Direct-commerce Order/purchase asset failing its precondition does not fall into Follow/tag/save or Engage via response — those classes are not legal for Direct-commerce at all — it falls to Reserve/book or Product-path (tier 4/3, if legal for that objective and precondition-satisfied), then Visit/directions, then Content, then No-CTA. A Reach-and-community asset has no tier-5 or tier-4 members in its allowed set to begin with, so its ladder in practice runs tier 1 → tier 0. This keeps the ladder from ever assigning a class the objective forbids, which is the same objective-gating rule §1 and `01` §1 already establish — the ladder does not create a new exception to it.

### 4.2 Making the downgrade visible

The task names the real failure mode precisely: a silent downgrade means the operator asks for an order CTA every week and quietly never gets one. Three design moves close this, all reusing machinery this document did not need to invent:

1. **Requested-versus-delivered is recorded per asset**, the same pattern `02` §3.4 already uses for a route substitution in image generation ("a silent fallback to ungrounded generation... is visible before approval, not only discoverable in the ledger afterwards"). The per-asset spin rationale line (`ARCHITECTURE_PLAN.md` §12.2) is extended to show both values whenever they differ: *CTA: Order/purchase → degraded to Content (F-T stock feed unresolved)*.
2. **A new, named completeness reason** joins the three the digest already distinguishes — budget-capped, count-capped, deliberately held (`ARCHITECTURE_PLAN.md` §12.1) — a fourth: **CTA-downgraded**, naming the table row (archetype × objective) and the blocking fact class, so it reads as a distinct operator action item rather than folding into "deliberately held."
3. **Repeated downgrade of the same table row escalates**, reusing the existing anti-flap escalation mechanism (§10.3: "Anti-flap escalation counts — how many consecutive identical degrades escalate prominence instead of repeating — default two") rather than inventing a second alarm system. This document's contribution is narrow and specific: **CTA-downgrade-per-table-row is added as a tracked event class under that existing mechanism, keyed to the (archetype × objective) row identity rather than only to the generic degrade categories already enumerated.** At the existing default of two consecutive occurrences, the second consecutive downgrade of the same row promotes from a per-asset note to a named, escalating digest line — reusing `02` §2.5 item 3's own phrasing pattern for exactly this shape of problem: *"the order/purchase CTA for [archetype] has degraded to no-CTA in [N] of the last [M] packs — F-T stock verification has failed each time; check the feed connection."* This tells the operator something about the underlying fact source, not about the table's authoring quality, which is the same distinction `02` draws between an offer-positioning problem and a prompt-quality problem.

Readiness validation (§13.2, static and load-time) already catches the case where a row's required fact class is *structurally* absent (no F-T catalogue configured at all); the escalating digest alarm is deliberately the *runtime, historical* complement — it catches the case readiness cannot, where the fact class exists but its live source keeps failing.

---

## 5. Where the operator's authored intent is legally dangerous

| Risk | Control | Owning layer |
|---|---|---|
| **Order/reserve CTA authored for a tenant with no verified inventory or booking system** | F-T/F-S are Blocking and externally verified (site, feed, or booking system) — never satisfiable by operator attestation alone, per the standing rule that the site can subtract but never add and an override may not create a commercial fact (`ARCHITECTURE_PLAN.md` §6.4). The operator table can select the class; it cannot mark the precondition met | Brand-truth resolver (§6.2–§6.6) + CTA preconditions (§3 above), never the table itself |
| **Commercial-incentive CTA whose percentage is a claim** | F-G blocking grounding, class-2 self-sufficiency (`02` §5.1), FULL-band requirement whenever numeric. **Price-*reduction* wording specifically remains an undesigned check** (`02` OD-L9) — detection-only until it ships | Claim-gate substrate (`ARCHITECTURE_PLAN.md` §6.7), `02`'s product/e-commerce pack; interim posture at CFG-OD-L-4 below |
| **Subscribe CTA without a lawful basis or an unsubscribe path** | GDPR Art. 6/7; prose precondition exists (`01` §6) but **no fact class formalises it** the way F-Q/F-R/F-S/F-T formalise the physical-fact classes | Currently: none, mechanically — flagged as a genuine gap at CFG-OD-L-1 |
| **Engage-response CTA harvesting personal data with no privacy notice** | Same gap as Subscribe; GDPR Art. 13 transparency duty stated in prose (`01` §6) but not a checked precondition today | Same gap, CFG-OD-L-1 |
| **Visit CTA with unverified opening hours** | F-Q Blocking whenever a visit-us CTA is used, 24h verification window (`02` §4.1, `01` §6) — this is the **best-controlled** of the physical-fact risks precisely because `02` already closed it | Brand-truth resolver, already adequate |
| **Wording that is itself a misleading commercial practice regardless of class (manufactured urgency)** | Check class 7 (temporal/availability, "also catches manufactured urgency"), spin gate S-7 (no hype-glue), the Urgency angle-type's explicit precondition against manufactured deadlines (`01` §4). **CR-4's "literal, never compiled" governs only the resolver's treatment of the wording array — it does not exempt that text from the claim gate or spin gate**, both of which check every generated surface including CTA text (`ARCHITECTURE_PLAN.md` §6.7) | Claim gate + spin gate, over the wording itself, regardless of which class or table row produced it |
| **CTA wording that constitutes a prohibited health claim regardless of class** | The Prohibited-Outcome Gate (`02` §2) — engine floor, not a pack member, not reachable by a tenant ledger entry, a playbook selection, or an operator override (`02` §2.4). It runs over CTA text as ordinary generated text, at every point the claim gate runs, **before** any claim-ledger lookup for that text — and a CTA class being fully precondition-satisfied (per §3's table) has no bearing on this check at all, because the two mechanisms answer unrelated questions (§3's "ordering, confirmed once here") | Engine floor, beneath the playbook layer and beneath the operator table entirely — the table has no reach here by construction |

---

## 6. Wire-in

- **`ARCHITECTURE_PLAN.md` §6.9** (spin application, CTA precondition table) — extended from the current four rows to the canonical twelve-class registry (§2) with the precondition table at §3; the pain-to-offer lookup is joined, not replaced, by the operator-authored (archetype × objective) table as an additional playbook-scoped input (§1).
- **`ARCHITECTURE_PLAN.md` §6.3 F-E** (CTA set fact class) — role unchanged; a cross-reference added noting the operator table's cells resolve to CTA-class selections that index into F-E's existing per-language literal phrasing rather than storing wording a second time (§1.5).
- **`ARCHITECTURE_PLAN.md` §6.10 S-6** (next-step correctness) — extended to check the table-selected class against §3's precondition table, and to record both the requested and the delivered class per asset (§4.2).
- **`ARCHITECTURE_PLAN.md` §10.3** (spin block knobs) — a new knob is added alongside "CTA class enablement per destination per language": the operator-authored table itself, its wildcard/specific precedence rule (§1.2), and its no-table default of No-CTA (§1.4).
- **`ARCHITECTURE_PLAN.md` §13.2** (readiness) — a new assertion: every table row resolves to a registry-member archetype, a registry-member objective (or wildcard), and a registry-member CTA class, failing closed with the offending row quoted verbatim on any unmapped token (CR-7); duplicate same-specificity rows are a named readiness failure (§1.2).
- **`ARCHITECTURE_PLAN.md` §12** (digest) — the per-asset spin-rationale line gains a requested-vs-delivered CTA field; the anti-flap escalation mechanism (§8.12/§10.3) gains CTA-downgrade-per-table-row as a tracked event class (§4.2).

---

## 7. Counsel items

| ID | Question a lawyer must answer | Interim safe position |
|---|---|---|
| **CFG-OD-L-1** | Subscribe/join and Engage via response both carry a GDPR/ePrivacy precondition stated only as prose (`01` §6) — no fact class formalises "verified consent mechanism / privacy notice present" the way F-Q/F-R/F-S/F-T formalise the physical-fact classes. Should a new fact class, or a required-statement sub-check under check class 10 (mirroring the allergen and guarantee sub-checks `02` already built), make this machine-checkable rather than an unverified assertion? | Treat as operator-attested only, logged per asset; these two classes may not be authored into the table at volume until a qualified GDPR/ePrivacy lawyer confirms the correct verification mechanism |
| **CFG-OD-L-2** | Reserve/book and Event both carry a booking/reservation-contract dimension under Czech consumer law (cancellation terms, distance-contract disclosure) that has not been researched — a narrower scope than the general recognisability-duty gap already flagged at `02` OD-25/OD-L7 | Rest on UCPD Art. 6/7 (EU-level, Medium-High) alone; assert no specific Czech statutory provision until confirmed |
| **CFG-OD-L-3** | Event has no first-class fact-class home in `02`'s F-O…F-W expansion, despite check class 7 and the new F-S both referencing it as a live pattern. Should a future amendment give it one (an F-class carrying the dated fact, the registration URL, and its freshness state), rather than continuing as an ad hoc check inside §6.9's prose? | Continue the current mechanism (dated fact + future date + registration URL, checked at spin time and re-checked at the platform gate) unchanged; do not treat this as a reason to withhold the Event row from the table — the existing control is real, only its long-term home is unsettled |
| **CFG-OD-L-4** | Commercial-incentive rows in the operator table inherit `02`'s own open gap (OD-L9): price-*reduction* / discount-percentage checking is explicitly undesigned. Should the table refuse to accept a Commercial-incentive row entirely until OD-L9 ships, or is flagging every such row "blocked-pending-OD-L9" in the resolver readback sufficient? | No discount-percentage CTA wording ships as claim-shaped copy under any table row until OD-L9's check class exists, per `02`'s own stated interim posture; recommend the resolver readback (CR-2) explicitly names any Commercial-incentive row as blocked-pending-OD-L9 rather than presenting it as live |
| **CFG-OD-L-5** | `01` §3 itself flags the Question/engagement archetype as "very high [claim risk] if quiz is product disguise." Does a poll/DM/form-based Engage-via-response CTA used for lead qualification constitute profiling or automated decision-making under GDPR Art. 22 in any of the five tenant archetypes? | Treat any Engage-via-response row whose collected data feeds a scoring or qualification process as out of scope for unattended authoring until confirmed; interactive-only, hand-reviewed |
| **CFG-OD-L-6** | Does a short CTA phrase standing alone ("Order now — 20% off") independently trigger the Czech advertising-recognisability duty (`02` OD-25/OD-L5/OD-L7, Low-Medium confidence), distinct from the recognisability of the surrounding post copy — i.e., is CTA text itself an independently regulated surface or only regulated as part of the whole asset? | Treat CTA text as fully in-scope for the recognisability duty, at the same confidence level as the rest of the asset, pending confirmation; no lighter-touch treatment for CTA text specifically |

---

## Summary of key decisions

- **The operator-authored table's key is (post archetype × content objective)**, with a wildcard-then-specific precedence rule and load-time-failure on ties, because objective is the axis that actually gates which CTA classes are legal, and archetype alone or archetype × destination both fail to express that.
- **The canonical CTA registry has twelve members**, correcting `01_content_ontology.md`'s internal "ten"/eleven-rows/"nine" inconsistency: the §6 table's eleven rows stand, the §10 summary's merge of the three engagement classes is rejected, and **Event is restored as its own class**, not folded into Content and not demoted to a subtype, because its precondition is strictly stronger and two other documents (`ARCHITECTURE_PLAN.md` §6.7, `02` F-S) already depend on it existing.
- **Every class carries a fixed, non-overridable precondition floor** (§3) — required fact classes and obligation level, confidence band, freshness window and verifier, required disclosures, legal basis — and the Prohibited-Outcome Gate is confirmed to run over CTA text before any claim-ledger lookup, independent of and unreachable by CTA-class eligibility.
- **The degradation ladder is six tiers, objective-bounded**, and the silent-downgrade failure is closed by recording requested-versus-delivered per asset and by extending the *existing* anti-flap escalation mechanism with CTA-downgrade-per-table-row as a new tracked event class — no new alarm system.
- **Six counsel items** are logged (`CFG-OD-L-1` through `CFG-OD-L-6`), each with an interim posture that never authorises what it cannot yet confirm; two (`CFG-OD-L-1`, `CFG-OD-L-4`) name genuine, currently unclosed gaps in the fact-class and check-class substrate that this document does not attempt to design shut.

**File written:** `C:\Users\Pavli\Desktop\HypeDigitaly\GIT\HypeAgentSocials\docs\plans\PLAYBOOK_LAYER\06_WORKING\06D_cta_authoring.md`
