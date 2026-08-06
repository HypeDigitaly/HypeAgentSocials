# Playbook layer — master plan

*Design-phase amendment to `docs/architecture/ARCHITECTURE_PLAN.md` · drafted 2026-08-06 · revised after adversarial review the same day · conductor deliverable*
*Status: **plan only**. No code is written by this plan; its output is an amended Stage-4 architecture.*

**Revision note.** The first draft proposed one amendment of four waves. Three independent reviewers — architecture, product, prompt/eval — converged on the same structural objection: the two safety defects are severable from the generalisation programme, bundling them delays a decision the operator can already make, and the plan's own falsification step was scheduled after its irreversible merge. This revision splits the work into **Amendment A (safety, small, before Stage-5 approval)** and **Amendment B (the playbook layer, after)**, and repairs eight further findings recorded in §10.

---

## 0. Plan folder contents

| File | What it is |
|---|---|
| `00_MASTERPLAN.md` | **This file.** Problem, decisions, reconciliation rulings, the two amendments, waves, agents, barriers, aggregating files, wire-in, acceptance criteria, review disposition. |
| `01_content_ontology.md` | Design annex — content objectives, relation types, post archetypes, angle taxonomy, voice-genre registry, CTA vocabulary, mapping-distance replacement. |
| `02_legal_claim_packs.md` | Design annex — claim-pack architecture, the Prohibited-Outcome Gate, depicted-attribute checking, new fact classes, price handling, counsel items. |
| `03_pipeline_and_gates.md` | Design annex — trigger lanes, ranking profiles, recurrence rework, criterion registry, node injection points, fact-schema profiles, readiness extensions, fixture replacement. |
| `04_RECONCILIATION.md` | **Produced by Amendment B Wave 0.** Binding rulings on C-1…C-13. Does not yet exist. |

**The annexes are inputs, not the design.** Each was authored in parallel from a different domain and they contradict each other in thirteen places (§4). Nothing in an annex is binding until §4 rules on it. Where this master plan and an annex disagree, this file governs.

---

## 1. The problem

`ARCHITECTURE_PLAN.md` generalises across language, source portfolio, destinations, budgets, providers and safety — 100 of ~141 knobs are vertical-neutral — while hard-coding **one content ontology**: B2B demand generation, in which an audience is a set of ICP segments carrying *pains*, a post exists to attach an *offer* through a *CTA*, and quality is sober, falsifiable thought leadership. Six knobs are ontology-bound; that count understates the problem, because **the gates read the ontology directly rather than reading configuration**.

| # | Defect | Mechanism | Effect |
|---|---|---|---|
| **P-1** | A tenant with no product can never run | §6.3 marks F-B (offer catalogue), F-C (capability statements) and F-E (CTA set) blocking and **"may not be legitimately empty"**; F-F (pricing policy) is a separate case with a different fix | §6.5 gate fails → INSUFFICIENT → research-only forever; §13.2 readiness fails → **may never be scheduled** |
| **P-2** | Non-transactional assets are all dropped | S-2 and S-3 are **binary** and the ladder terminates in dropping the asset | Empty pack for any tenant without an offer |
| **P-3** | Recurring and calendar content is banned | S-1: *"could this have been written yesterday? If yes, it fails"*, plus §2.8a resurgence suppression | A restaurant can never post a daily menu |
| **P-4** | No non-trend origination exists | Every candidate enters through collection; stage order is fixed | "Post five times a week regardless" is forbidden in four places |
| **P-5** | Non-B2B voices fail by construction | §14.4 names the curiosity-gap tease a fail smell and "vagueness dressed as insight" a fail; a theme may only make voice rules **stricter** | Food, expressive and creator registers are rejected as slop |
| **P-6** | Subject matter is treated as hallucination | Check class 3 (non-disableable) has no bucket for culturally-shared non-commercial nouns | "cardamom", "the Empress card", a named creator — blocked |
| **P-7** | CTA vocabulary is a closed enum of four | content · product-path · event · commercial-incentive | No book, no order, no visit, no engagement CTA |
| **P-8** | No editorial control surface exists | Zero knobs for archetypes, mix, angle taxonomy or objective | The operator's literal request has no home |
| **P-9** | The generality proof cannot fail | §13.3's second fixture is *another Czech B2B SaaS*; the four ontology primitives are held constant in kind | The extensibility claim was never tested against what breaks it |
| **P-10** | **The claim ledger can launder an unlawful claim** | The ledger is tenant-authored; all eleven check classes are substantiation-shaped | A tenant writes *"our sessions relieve anxiety"* into their own ledger → **VERIFIED**. EU health claims run on a **closed positive list** (Reg. 1924/2006 Art. 10): a true, evidenced claim is still unlawful if unauthorised |
| **P-11** | **Generated imagery makes unchecked claims** | The claim gate covers text, including text on pixels, never what the pixels **depict** | An image of a dish not served, or packaging that does not exist, passes every gate. The AI disclosure is not a defence to a misleading-action claim about the product's nature |

**P-10 and P-11 are safety defects independent of generalisation.** They apply to every tenant, every vertical, every playbook, and neither depends on the playbook layer. That severability is why they move to Amendment A.

---

## 2. Decisions taken by the operator (2026-08-06)

| ID | Decision |
|---|---|
| **PB-1** | A **playbook** layer is inserted between engine and theme. Engine (non-negotiable floor) → Playbook (what a post *is* for this kind of business) → Theme (this brand's values) → Language overlay (unchanged). |
| **PB-2** | *(Revised — see §3.)* A playbook **selects from engine-owned registries and never authors rules freely.** |
| **PB-3** | Non-trend origination becomes first class: **collected trend · calendar/occasion · evergreen library**. |
| **PB-4** | Editorial control becomes configurable: **post archetypes with a mix ratio, an angle taxonomy, a declared content objective.** |
| **PB-5** | *(Revised — see §3.)* LLM-step configuration is **depth-tiered slot-filling**, never free prompt replacement. |
| **PB-6** | **Product promotion is a first-class use case.** Generative depiction of real sellable products is permitted **only when reference-grounded** in tenant-supplied genuine imagery, with the engine default at the safe end and a recorded human attestation. |
| **PB-7** | Ship order: **playbook #1 = HypeDigitaly B2B lead generation**, behaviour-preserving. Then **one deliberately different playbook** as a falsification fixture. Four playbooks up front is rejected. |

**The behaviour-preservation invariant, binding on every wave.** The B2B lead-generation playbook must reproduce today's behaviour exactly. Any edit changing what theme #1 produces is a defect of this amendment, not an improvement, unless listed in §7 as an intended fix.

---

## 3. Two decisions corrected by review

Review found two of the above are false as written. They are corrected here rather than handed to a leaf, because a leaf cannot resolve a contradiction inside a decision it is forbidden to reopen.

### 3.1 PB-2 was false at the voice gate — replaced by a two-tier rule

"May only add strictness, never remove it" cannot express the genre registry, because **genres differ in kind, not in degree**. §14.4 dimension 2 makes *"vagueness dressed as insight"* a fail; the evocative-expressive rubric makes vagueness acceptable where it evokes shared understanding. §14.4 dimension 1 names the curiosity-gap tease a fail smell; two genres reward it. A polarity flip is not a loosened bar on a shared axis. Annex `03`'s attempted containment — *"bar values only, never dimensions"* — does not hold either, since a bar moved downward **is** a removal of strictness.

**PB-2 is replaced by:**

- **Tier 1 — engine floor. Strictly monotonic; a playbook may only tighten, never relax, never re-key.** Contents: the universal slop floor (no fabrication, no incoherence, no corpus bleed, no manipulation, no accessibility failure, no brand-lock violation); the non-disableable check classes; hard excludes; negative-prompt layers 1–3; the AI-disclosure floor; the Prohibited-Outcome Gate; every fail-closed trigger; the publish gate; spend gating.
- **Tier 2 — genre-variable. Bidirectional, but registry-closed.** Contents: rubric bars, fail smells, hook bars, specificity expectations. A playbook **selects among engine-registered variants** and cannot author one. **Strictness is not preserved here. Safety comes from calibration and provenance, not from monotonicity**: every variant is engine-registered, versioned, carries its own golden set, and its flag-rate ceiling stays *inactive* until that golden set exists.

This must be stated plainly in §19 — Tier 2 is a relaxation surface. The original wording bought reassurance the design does not deliver, which is the same defect class this amendment exists to fix.

### 3.2 PB-5 was stated as uniform — it is depth-tiered

The safety property is not slot-filling as such; it is that **judgment nodes accept no playbook-authored text at all.** Generation nodes (hook, script, shot list) take bounded compositional slots; gate, judge and verdict nodes (N-2, N-8…N-13) are **data-only**, and genre influence reaches them exclusively through engine-registered, version-pinned selections. Stated as one uniform rule, an implementer could read it as "every node gets the same seven slots," which would put tenant-authored text inside the claim gate. PB-5 is restated as **depth-tiered slot-filling** with the node depth table as its normative form.

---

## 4. Wave 0 of Amendment B — reconciliation rulings

Shared dependency: every downstream task reads the canonical registries, so these are resolved first, sequentially, and no Wave-1 task starts until `04_RECONCILIATION.md` passes its barrier.

| ID | Conflict | Ruling to apply, or overturn with reasons |
|---|---|---|
| **C-1** | `01` says node N-8 is *added*; `03` says no fourteenth node | `03` is correct on the facts — N-8 already exists as the spin-gate angle-level pre-check. `01`'s wire-in row is struck. Inventory stays at thirteen for **text** nodes; see C-12 for the depiction question. |
| **C-2** | `01` defines seven relation types including *education* and *testimonial*, and separately lists both among its eleven archetypes | The collision is real; **deletion is the wrong fix** — review established that `03`'s criterion registry keys its ANCHOR family on relation type, and `01` §7 keys two distance concepts on R-6/R-7. Ruling: **keep the ontology-bearing set at five** (offer-attachment · inventory/availability · expressive-aesthetic · commentary-observation · product-promotion) **and simultaneously re-key the anchor family on trigger class, not relation type** — occasion and library anchors are properties of the lane, which is where they belong. The reconciler must then state where proof/testimonial content's relation and distance live, and rewrite `01` §9's five walkthroughs, which currently declare R-6/R-7 as relations. A ruling that leaves those four consequences unpriced is not a ruling. |
| **C-3** | Proof-discipline waivers | `03` governs. Restated with full scope: **no criterion in the PROOF, NEXT-STEP or GLUE families may be waived, softened, deprioritised or marked not-applicable by any objective, relation type, archetype, angle or genre.** Every such statement in `01` §1, §3.1, §5 and §7 is struck — four locations, not one. Where a genre needs phrasing latitude that is a rubric-bar question at the voice gate, not a spin-criterion question. Waiving proof discipline for the expressive archetype is exactly inverted: that is the tenant class with the highest unlawful-claim exposure. |
| **C-4** | `02` makes F-B/F-C/F-E legitimately emptiable; `03` requires substitution, never exemption | Merged, **and the substitution floor is raised**. `03`'s non-triviality test admitted *"an explicit, dated operator attestation"* as sufficient — which is tenant self-assertion, precisely what `02` §2.1 spends its argument proving cannot ground a claim. Ruling: **a substitute grounding any descriptive-or-stronger statement class requires an external verifier** (a site check, a resolving URL, a third-party record). Operator attestation suffices only for classes whose absence cannot produce a claim. Additionally: a substitute for F-B **must carry a negative-capability field**, or check class 6 degrades to blocking all descriptive statements for that tenant. Count preservation alone is numerology, not safety — say so. **The merged wording is written in `04_RECONCILIATION.md`, not deferred to a Wave-1 author.** |
| **C-5** | Identifier namespace | Canonical: decisions `PB-D-n`, risks `PB-R-n`, open decisions `PB-OD-n`, legal opens `PB-OD-L-n` (overruling `02`'s instruction to renumber into the main OD sequence — say so explicitly). **Relation types are renamed `PB-REL-n`**: `01`'s R-1…R-7 collides with `R-01…R-41` in `RISK_LOG.md`, and `02` already cites "R-08" as a risk inside a document merging into the same section. Verify against `D-01…D-59`, `OD-1…OD-29`, `F-1…F-9`, `RA-*`, `W2-*`, `W3-*`, `W4-*`, `W6-*`, `R-01…R-41`. **Append the identifier blocks to the logs at Wave-0 close**, not at Wave-2 close, or every Wave-1 file cites rows that will not exist for two waves. |
| **C-6** | Objective composability | A playbook declares **one primary objective and zero or more secondary objectives**; permissions are the union. **But the key is wrong as first drafted**: no annex contains an objective→claim-pack mapping — `02` keys packs on **vertical**. Re-keyed: *a playbook declares its vertical(s); the pack set is the union of every declared vertical's packs; objectives govern next-step permission only.* Union on obligations, union on permissions, never intersection on obligations. `01`'s walkthrough conclusions ("cannot monetise", "requires a separate theme") contradict this and are rewritten. |
| **C-7** | Expressive/spiritual archetype acceptance | Operator decision `PB-OD-1` (§9). The reconciler records both branches and their consequences; it does not decide. |
| **C-8** | Fourth connector class (tenant register) | Accept unless failure modes, budgets and swap paths genuinely do not differ. The curated inbox is dormant under W6-1, which strengthens the case for a distinct class over an overload. |
| **C-9** | *(new — review finding)* **Audience descriptors have no owner.** `03` states it outright: without them, S-2's generalisation "has no registry behind it". S-2 is universal, its bars are engine-owned, and readiness asserts family coverage — the criterion is currently unimplementable | Assign the audience-descriptor registry to **T1**, add it to the Wave-0 canonical registry list, and state its binding to S-2's per-relation bars. |
| **C-10** | *(new)* **Statement classes have no owner.** `03` §5.3 rewrites §6.5's entire capability column in statement-class vocabulary and flags the statement-class ↔ claim-pack binding as undecided; no task is charged with it | Assign the statement-class registry to **T6**, with an explicit interlock note to T3 (packs) and T5 (criteria). §6.5's rework has no author until this is done. |
| **C-11** | *(new)* **Conditional blocking tiers cannot be evaluated where §6.5 evaluates them.** `02` introduces classes blocking *"only when a temporal CTA class is used"* or *"whenever depiction policy is B for an asset"* — but brand-truth resolution runs once per run **before collection**, while CTA class is chosen at spin and depiction policy resolves per asset. The inputs do not exist at Step 1 | Split cleanly: **band computation reads only unconditionally blocking classes; conditional classes become per-asset preconditions** evaluated when their condition is known — the existing model where a missing event fact kills the event CTA rather than the band. This keeps §6.5 genuinely unchanged, which is what the annex claims and does not currently deliver. |
| **C-12** | *(new)* **Depicted-attribute enforcement has no node, no ceiling and no cost line.** Both enforcement points require image comparison; the inventory is thirteen **text** nodes, §5.4a's per-call ceilings are keyed to that inventory, and `03`'s cost model budgets zero for vision calls — so the fix for P-11, the operator's confirmed critical path, is costed at exactly nothing | **Ruled for Amendment A, deterministic-only in v1**: check class 12 verifies that every asset flagged as depicting a real sellable item carries a linked, in-window reference in its provenance record — a pure provenance check with no model call. The **substantive** visual comparison is the human attestation's job, which `02` already designs in full. A model-mediated comparison node is registered as deferred value with its cost named, not promised and unbudgeted. |
| **C-13** | *(new)* **Genre rubric dimension polarity.** `03` says profiles change *"bar values only, never dimensions"*; `01`'s registry flips curiosity-gap from forbidden to rewarded. This is the mitigation `PB-R-6` relies on, and it does not hold | Resolved by §3.1's two-tier rule. The reconciler restates `PB-R-6`'s mitigation accordingly: the guarantee is **registry-closure plus per-variant calibration**, not monotonicity. Any risk row still claiming monotonicity as its mitigation is rewritten. |

**Wave-0 barrier.** `04_RECONCILIATION.md` exists; C-1…C-13 each carry a ruling with reasons; C-7 is recorded rather than decided; **every canonical registry is stated once with its full member list and a verified count** (the annexes miscount their own registries in at least four places — "five genres" listing six, "ten CTA classes" over an eleven-row table, "eight new fact classes" over nine); the §7 wire-in list and the Wave-2 edit list are reconciled into one; identifier blocks are appended to the logs. Conductor approves before dispatch.

---

## 5. Amendment A — safety, before Stage-5 approval

**Rationale.** P-10 and P-11 apply to every tenant and depend on nothing in the playbook layer — the Prohibited-Outcome Gate sits *beneath* it by design and check class 12 is base-pack and universal. Bundling them into a multi-wave generalisation programme means the operator either approves a design with two known safety defects or waits weeks for a decision unrelated to them. Neither is acceptable. The P-1 hard-failure fix rides along because it is two paragraphs and closes a "may never be scheduled" defect outright.

**Scope — one wave, four leaves, one merge.**

| Task | Agent | Writes | Content |
|---|---|---|---|
| **A1** | `legal-advisor` | `docs/architecture/playbook/A1_prohibited_outcome_gate.md` | The Prohibited-Outcome Gate: contents, its position **ahead of any ledger lookup** so authorisation is never queried, its mode-invariance, and why ledger, playbook and operator authorisation all lack a verb to reach it. Its terminal is **drop**, which §14.0's exhaustion rule does not currently permit — register the exception, or give the Gate its own allowance outside the claim-retry budget, since it is not a claim check. State the licensed-clinic limitation honestly. |
| **A2** | `legal-advisor` *(after A1, same owner-domain, sequential — shares the gate-order statement)* | `docs/architecture/playbook/A2_depiction.md` | Check class 12 **deterministic-only per C-12**; fact class F-W reference imagery; the three-value depiction policy with the engine default at the safe end; the human attestation and the mandatory side-by-side the review pack must show. Note explicitly that Policy A as engine floor **removes an existing capability from theme #1** (its own product-dashboard renders) — that is a permitted change only if called out as intended. |
| **A3** | `api-designer` | `docs/architecture/playbook/A3_emptiability.md` | F-B/F-C/F-E legitimate emptiability with C-4's **external-verifier** substitution floor and the negative-capability requirement; F-F's separate safe-default fix. Nothing about playbooks. |
| **A4** | `documentation-engineer` *(merge, single writer, LAST)* | `ARCHITECTURE_PLAN.md`, `STAGE5_APPROVAL_SUMMARY.md` | Apply A1–A3 to §6.3, §6.5, §6.7, §4.2a, §5.6, §11.3, §12.2, §12.4, §13.4, §14.0, §14.3, §16, §17; amend the approval summary so what the operator approves is accurate. |

*shape: a · flat, three leaves then one single-writer merge · barrier: the differential table of §7 restricted to A's changes, plus a format sweep*

**Amendment A does not touch:** relation types, archetypes, angles, genres, CTA vocabulary, trigger lanes, node overlays, ranking profiles, or the config surface. If it grows to touch them, it has failed its purpose.

---

## 6. Amendment B — the playbook layer

Runs **after** Stage-5 approval, in parallel with Phase 0's externally-latency-bound work (Meta ID verification, the Reddit API application, the Virlo and Postiz trials, counsel items OD-24/25/26). None of those clocks depends on this amendment, and none should wait for it.

### Wave 0 — reconciliation *(shared dependency, sequential, one task)*

| Task | Agent | Writes |
|---|---|---|
| **T0** Resolve C-1…C-13; publish canonical registries | `architect-reviewer` | `04_RECONCILIATION.md` |

*barrier: §4 above*

### Wave 1 — author the new architecture content *(flat, six leaves, disjoint files)*

No task edits `ARCHITECTURE_PLAN.md`. Every prompt carries the format prohibition (no code, pseudocode, CLI syntax, **configuration syntax of any kind**, or mandatory folder trees), the behaviour-preservation invariant, §3's two corrected decisions, and the Wave-0 registries.

| Task | Agent | Writes (`docs/architecture/playbook/`) | Content |
|---|---|---|---|
| **T1** | `content-marketer` | `19A_ontology_registries.md` | Playbook concept and layer contract; objective registry; relation-type registry (five, `PB-REL-n`); **audience-descriptor registry (C-9)**; archetype registry with mix mechanics and the honest shortfall degrade; angle taxonomy and selection |
| **T2** | `prompt-engineer` | `19B_voice_and_expression.md` | Tier-1 universal slop floor versus Tier-2 registered genre variants per §3.1, stated as a relaxation surface with calibration as its safety property; per-genre hook bar, fail smells, specificity expectation; **claim-boundary-adjacent genres start strict, not lenient** (review B2); CTA vocabulary with per-class preconditions; skill-bundle extension |
| **T3** | `legal-advisor` | `19C_claim_packs.md` | Base pack plus four vertical packs, additive, vertical-keyed per C-6; extraction requirements in both languages; counsel items with per-citation confidence. **Fact-class definitions only** — the emptiability rule belongs to T6 (review MJ-3) |
| **T4** | `ai-engineer` | `19D_triggers_and_ranking.md` | Three lanes and the tenant-register connector; comparison-class scoring generalised from the Czech single-axis-drop precedent; occasion-proximity and rotation-rest signal classes; per-lane caps and digest labelling; how volume integrity survives a five-posts-a-week tenant; evergreen-exhaustion ladder; declared-recurrence rework; **ranking-profile selection in full** (sole owner) |
| **T5** | `workflow-orchestrator` | `19E_criteria_and_nodes.md` | Criterion registry with families and the complement rule — **and its three holes closed** (review MJ-7): name S-7's complement for bridgeless assets; make activation predicates deterministic and fail-closed so a criterion can never silently not-exist; register the no-offer S-4 as its own family member rather than a bar of S-4. Depth-tiered injection points per §3.2; overlay versioning; **overlay fingerprint in idempotency keys (§8.5, not §8.6)**; **the regression gate fires on any fingerprint change at any layer, including theme-level corpus and banned-phrase edits** (review B1); **IP-4 worked examples hardened** — no proof-shaped or numeric content, leakage-audited at every addition (review M2); per-playbook eval and golden sets; per-genre flag-rate calibration; token ceilings with overflow as a readiness failure |
| **T6** | `api-designer` | `19F_config_surface.md` | Layer placement rules; **statement-class registry (C-10)**; fact-schema profiles and the merged emptiability/substitution rule (sole owner); knob migration theme → playbook; **the honest knob-count statement per §8**; revised minimum-viable decision set; §13.2 readiness assertions; §13.3/§13.4 fixture replacement |

*shape: a · six leaves, disjoint file paths. Two cross-task statement dependencies existed in the first draft and are resolved by single-owner assignment rather than by parenting: emptiability/substitution is T6 alone, ranking-profile selection is T4 alone.*

**Wave-1 barrier.** All six files exist; format sweep passes; every §-reference resolves; no file contradicts `04_RECONCILIATION.md`; registry member lists and counts match across all six; no file silently changes theme #1 behaviour. Failures route back inside the wave.

### Wave 1.5 — falsification, *before* the irreversible merge *(new; review BL-7)*

The first draft scheduled the five-tenant walkthrough and the layer-boundary review at Wave 3 — after ~45 sections of surgical edits. That is structurally the same error as P-9: a falsification test positioned where failing it is maximally expensive, so a conductor facing the cost accepts findings as minors. Both design-validity reviews move here, where acting on them is cheap.

| Task | Agent | Writes | Charge |
|---|---|---|---|
| **V1** | `architecture-reviewer` | `docs/reviews/R6_boundary.md` | Is the two-tier layer boundary enforceable against the six files as written, or asserted? Does any invariant weaken? |
| **V2** | `content-marketer` | `docs/reviews/R8_walkthrough.md` | Five tenant archetypes end to end on paper. Each must produce a non-empty valid pack **or an honestly named refusal**. At least one must exercise the Prohibited-Outcome Gate; at least one a reference-grounded product image |

**Wave-1.5 barrier.** Blockers fixed in the Wave-1 files before Wave 2 begins.

### Wave 2 — merge *(sequential, one writer, three checkpoints)*

`ARCHITECTURE_PLAN.md` has exactly one owner and is written last. The first draft made this one task with one barrier; review established the work is not homogeneous — six sections are *reworks*, two of which **delete binding sentences** whose rules may be stated nowhere else. Three checkpoints, same owner, three recoverable states.

| Task | Agent | Content |
|---|---|---|
| **T7a** | `documentation-engineer` | Insert **§19** assembled from the six Wave-1 files, one voice, no duplicated registry statements. Update §0.2/§0.3 and §18 |
| **T7b-i** | *same* | **Reworks first, while the document is otherwise intact:** §2.8a, §6.5, §6.10, §13.3, §13.4, §14.1. Barrier: every deleted sentence has a named replacement owner; **the §7 differential table is produced here**, not at the end |
| **T7b-ii** | *same* | Knob tables: §10.1–§10.5, §5.4a, §8.2. Barrier: §10.1's minimum-viable count restated with its honest new number |
| **T7b-iii** | *same* | Pointer insertions: everything else. Barrier: mechanical — every §7 row's target resolves and points at §19 |
| **T8** | *conductor* | `DECISION_LOG.md`, `RISK_LOG.md` — append `PB-D-n`, `PB-R-n`, `PB-OD-n` |

### Wave 3 — post-merge review *(flat, two leaves)*

Only the reviews that genuinely need the assembled §19 in context.

| Task | Agent | Writes | Charge |
|---|---|---|---|
| **R2** | `pravnik` | `docs/reviews/R7_playbook_legal.md` | Does the Gate resist ledger, playbook and operator authorisation as merged? Are Czech positions defensible and unverified citations flagged? Czech with English finding lines |
| **R4** | `prompt-engineer` | `docs/reviews/R9_playbook_evals.md` | Do pinning, the frozen eval set and the regression gate survive overlays? Is the calibration burden affordable and honestly costed? Is the token estimate defensible against §5.4a? |

### Wave 4 — fix and close

`documentation-engineer` applies accepted findings and extends Appendix B's audit table; conductor logs and re-amends the Stage-5 summary.

---

## 7. Acceptance criteria

**A · The five-tenant walkthrough** (Wave 1.5, re-verified after merge). Each of B2B lead generation · local hospitality · expressive/community · creator-UGC · product/e-commerce terminates in a non-empty valid pack **or a named, reasoned refusal**. A walkthrough that succeeds by hand-waving a gate fails.

**B · Behaviour preservation, checked by a differential table — not by re-reading Appendix A.** Review established Appendix A traces one topic that names no third party, depicts no product, uses no event CTA and never runs at MINIMAL — so it cannot see the new relation-agnostic criteria firing on theme #1, the repair-ceiling contention they create, the PARTIAL-band vocabulary drift, or the depiction-policy capability removal. Replace it with **one row per engine decision point theme #1 traverses** — thirteen nodes, twelve check classes, the criterion set, four bands × their capability columns, five fail-closed triggers, the CTA classes, the repair ceiling, the depiction default — each with today's value, the post-amendment value, and for every changed cell a justification naming P-10, P-11, an operator decision, or "defect." Plus **two additional traced topics** chosen to hit Appendix A's blind spots: one naming a competitor with a comparative, one at FULL band stating trial terms with an event CTA.

**C · The safety floor is intact and the mechanism is named.** For each of: fail-closed on missing secrets, ambiguous brand truth and policy violation; no gate defaults open; nothing silently shipped or dropped; one publish enforcement point; spend gated before submission; the AI-disclosure floor; never invent prices, ROI, client names or case metrics — state *where* the playbook layer is prevented from reaching it. An assertion that a playbook "cannot" is insufficient.

**D · Volume integrity.** "Zero passing candidates is correct behaviour" and "thresholds are never relaxed to manufacture volume" remain true, and evergreen exhaustion degrades honestly.

**E · Falsifiability restored.** §13.3's fixtures no longer share theme #1's ontology — **two** fixtures falsifying different assumptions — and §13.4 honestly names what remains unserved, including the licensed clinic.

**F · Format compliance.** No code, pseudocode, CLI syntax, configuration syntax or mandatory folder tree. Diagrams permitted.

**G · Traceability.** Every P-1…P-11 maps to the subsection closing it, or is recorded as accepted-and-open with a reason.

---

## 8. The knob-count claim, stated honestly

The first draft asserted that selecting a playbook would **reduce** the decisions a new tenant faces. Review refuted it against the annexes: `01` itself says the layer adds *"≈20 new knobs per theme"*, `03` adds roughly twenty more and eleven new readiness assertions, and of §10.1's eleven minimum-viable decisions only one — the pain-to-offer relation — is genuinely replaced by selection, while two others grow.

**The honest formulation, which §19 must carry:** selecting a playbook does not reduce the decision count. It reduces the number of decisions that are **wrong by default**, and it moves the hardest decision — what a post is *for* — from per-tenant authorship to per-vertical selection. That is a real benefit and it should be claimed accurately.

**A consequence review drew out and the plan accepts:** six genres × two languages is twelve calibration cells, each needing a golden set and — because the Czech rhythm band is measured from a structural corpus — its own per-genre Czech corpus. At one tenant and a few runs a week those cells will not fill for years, and `03`'s own sample-size argument ("a ceiling computed on four artifacts is noise dressed as a control") condemns them. **v1 therefore registers all genres but calibrates two**: analytical-B2B, plus whichever playbook #2 needs. The rest are design-complete with flag-rate ceilings recorded inactive — the mechanism already used for a new language, applied to a new genre. The per-genre Czech calibration corpus is added to PB-OD-3's cost.

---

## 9. Open decisions for the operator

Reduced from five: review established three of the original five were pseudo-choices with no credible alternative, and those are now stated as design decisions rather than offered as questions. Two additions came out of review.

| ID | Question | Recommendation |
|---|---|---|
| **PB-OD-1** | Is the **expressive/spiritual** archetype shipped at all? It is simultaneously the best falsification fixture (no product, no ICP, no offer) and the archetype closest to the regulated health-claim boundary. | Ship it **as the fixture**, do not run a real tenant on it until the Gate has been exercised in review. Local hospitality is the safer commercial second playbook. |
| **PB-OD-4** | The **licensed-clinic case** — a lawfully authorised health-claim advertiser cannot be safely served in v1 and must author that content outside the system. Accept as a stated limitation? | Accept and state it in §13.4. The alternative is an authorised-claim register nobody will maintain. |
| **PB-OD-6** | *(new — review BL-5)* **Price grounding.** `02` resolves the class-1/class-2 overlap by making a site-verified price value self-sufficient without a ledger entry. That is defensible engineering — hand-entering forty menu items weekly is a real burden and a fetched price beats a stale ledger row — but it is **a reduction in required grounding that applies to theme #1**, and it was self-authorised inside an annex that opens by claiming it loosens nothing. | Accept, but as a **logged operator decision with rationale**, added to acceptance criterion B's explicit-exception list. Strike the annex's blanket "loosens nothing" sentence — it is false as written and it is the sentence a reviewer would rely on. |
| **PB-OD-7** | *(new — review finding 3)* **Falsification without a real second tenant.** The operator named a restaurant, an esoteric page and a UGC agency as *examples*, not customers. If no second tenant materialises, playbook #2 becomes another B2B variant and proves feature depth, not ontology diversity. | Record explicitly that v1 requires **either a real second tenant with a built playbook, or a fully paper-walked second playbook exercising every gate and decision point**, and that the latter is a passing outcome. Do not ship claiming extensibility is proven without one of the two. |

**Stated as decisions, not questions** (each was previously offered as open and has no credible alternative): playbook #2 in build order is **product/e-commerce** if the operator has a real product, because it is the only choice that exercises PB-6 and check class 12 · each new playbook runs deliberately lenient with its flag-rate ceiling inactive until its golden set exists, **except** claim-boundary-adjacent genres, which start strict (review B2) · Amendment A lands before Stage-5 approval and Amendment B after.

---

## 10. Review disposition

Three reviewers, 7 blockers and 21 majors. Accepted and applied in this revision: the split into Amendments A and B (all three reviewers, independently) · PB-2's replacement by the two-tier rule (BL-2, M4) · PB-5's restatement as depth-tiered (m1) · Wave 1.5 moved before the merge (BL-7) · Wave 2 split into three checkpoints (MJ-4) · the differential table replacing the Appendix-A check (MJ-1) · C-9, C-10, C-11, C-12, C-13 added (BL-4, MJ-8, BL-6) · C-2, C-3, C-4, C-6 re-ruled with their consequences priced (BL-1, MJ-6, BL-3, MJ-10) · single-owner re-cut of emptiability and ranking profiles (MJ-3) · the honest knob-count statement and the two-genre calibration cap (MJ-2) · PB-OD-6 and PB-OD-7 raised (BL-5, finding 3) · three pseudo-decisions demoted to design decisions (finding 6) · claim-boundary genres start strict (B2) · the regression gate fires on any fingerprint change at any layer (B1) · IP-4 hardened (M2) · the criterion complement rule's three holes closed (MJ-7) · minors: agent-name consistency, §8.5 versus §8.6, `PB-REL-n` renaming, identifier blocks appended at Wave-0 close, T9 scope excluding the frozen file, the Gate's drop terminal registered as a §14.0 exception.

**Carried as known-open rather than fixed:** the token-budget estimate remains a hypothesis until measured against playbook #2's Phase-0 trial packs, and must be stated in two regimes — if the per-run cap already binds, the symptom is cap-hits; if it does not, the symptom is a proportionally larger bill (M3). The `AGENTS.md §9a` dispatch authority cited in the first draft does not exist in this repository; the dispatch rules are restated inline here instead.

**Rejected with reasons:** the suggestion to state the language overlay as PB-1's justifying precedent is **struck** — review is right that the two constructs differ (the overlay is per-language, shared, orthogonal, composable; the playbook is one-per-theme, hierarchical, constraining), and an analogy that does no work should not carry a layer. The genuinely cheaper alternative review named — a declared-vertical field plus three engine lookup tables plus a theme preset, with genre variants registered at the language-overlay level — is recorded in §19 as **rejected**, with the reason stated: it delivers the safety floors but not the criterion/fact-schema interlock that must validate as a unit, and presets are defaults-with-override where claim-pack selection must be a floor without one. Forking the pipeline per vertical is rejected outright: this architecture's entire value is its invariant set, and duplicated invariants drift.

---

## 11. What this plan deliberately does not do

- **No code.** The output is an amended Stage-4 architecture; implementation remains downstream of Stage-5 approval.
- **No four playbooks.** One plus a fixture (PB-7). Five walkthroughs are paper falsification, not five builds.
- **No tenant-authored gate criteria, claim classes or rubric variants.** Registries are engine-owned; playbooks select. A new *kind* of rule is engineering work; a new *combination* is configuration.
- **No per-axis ranking weight knob.** Profiles are selected, not authored, on §6.5's own reasoning about uncalibratable thresholds.
- **No reopening of any LOCKED decision or any W2.5/W6 operator decision.** Where one constrains this design — W2.5-4 identical asset mixes, W6-1 no manual inputs — the design bends to it.
