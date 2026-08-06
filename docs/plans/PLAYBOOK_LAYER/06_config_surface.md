# Config surface — master annex

*Design-phase amendment to `docs/architecture/ARCHITECTURE_PLAN.md` · drafted 2026-08-06 · conductor deliverable*
*Status: **plan only**. No code is written by this plan; its output is an amended Stage-4 architecture.*

**What this file is.** The operator asked for a configuration surface they can fill in by writing plain-language guidance into fields and supplying arrays of values, with defaults for everything they leave alone. Five specialists designed it in parallel. Two adversarial reviewers then attacked the result **before** merge, and returned a verdict of **do not merge**: seven blockers, thirteen majors, six red-team findings, three of which land on the conductor's own rulings rather than on the leaves.

This file records the rulings that resolve them and the waves that execute the fix. **The five Wave-1 files are inputs, not the design** — the same relationship `01`/`02`/`03` have to `00_MASTERPLAN.md`. Nothing in them is binding until §3 rules on it.

---

## 0. Folder contents

| File | What it is |
|---|---|
| `06_config_surface.md` | **This file.** The operator's request, what is and is not answered, the reconciliation rulings, the waves, acceptance criteria, open decisions. |
| `06_WORKING/CONDUCTOR_RULINGS.md` | The binding rulings CR-1…CR-11, including the four amendments forced by Wave 1.5. **Read this before any other file in the folder.** |
| `06_WORKING/06A_knob_registry.md` | Input — per-knob table with IDs, tiers, defaults, layering regimes; 178 knobs honestly counted. |
| `06_WORKING/06B_resolver.md` | Input — the free-text-to-registry resolver, its readback, its failure taxonomy, its safety argument. |
| `06_WORKING/06C_authoring_form.md` | Input — the operator-facing form and the two fixture configurations. **The weakest of the five; five blockers originate here.** |
| `06_WORKING/06D_cta_authoring.md` | Input — the operator-authored CTA table and its per-class preconditions. |
| `06_WORKING/06E_readiness_and_defaults.md` | Input — default semantics, layer resolution, eighteen readiness assertions, migration acceptance. **The strongest of the five.** |

---

## 1. What was asked, and what is honestly answered

The operator's request had five parts. After five documents, the state is:

| The ask | State | Why |
|---|---|---|
| **Which keywords / trends to look for** | ✅ **Served** | `05_query_steering.md`'s design plus `06C` Field 4's structured per-language topic object. The best-specified part of the corpus. |
| **Connect to company information** | ✅ **Served** | Fact-class pointers already existed; `06C` Field 2 plus `06B`'s substitution handling against `C-4`'s external-verifier floor genuinely closes **P-1** at the config layer. |
| **What the posts should be about** | ⚠️ **Partly** | Post-type mix, angle weighting and objective become authorable — but only the **collected-trend** lane can be fed. The calendar/occasion and evergreen lanes have knobs and no fields, so **P-3 and P-4 stay open**. |
| **What the spin should be** | ⚠️ **Barely** | Relation type is derived with no field; criterion selection sits at Tier C; and the **pain-to-offer relation — which `ARCHITECTURE_PLAN.md` §10.1 calls "the theme's actual intellectual content"** — has no field at all, while three other documents route their reasoning through it. |
| **What the CTAs should be** | ❌ **Not served** | The operator-authored CTA table exists in exactly one document. No form field, no knob row, no resolver input — and `06E` wrote its readiness assertion against a differently-keyed table, so four of that assertion's five sub-conditions are unevaluable. |

**The honest summary for §19.** A person filling twelve fields plus three tuning fields today gets keywords, destinations, safety rails, an objective, a voice and an archetype mix. They do not get the CTA table they explicitly approved, the pain-to-offer mapping, the occasion calendar, or their own public brand identity. **P-8 is downgraded, not closed.** Wave 2 closes it; this plan does not claim it is already closed.

**One thing worth stating without hedging:** the sharpest evidence that the complexity is not yet honestly bridged is not an argument in a review. It is that **the authors could not fill in their own form correctly** — the shipped falsification fixture assigns 30% of its content mix to an archetype that does not exist in its own registry, and would fail resolution.

---

## 2. Rulings the conductor was forced to make against itself

Recorded here because a plan that hides the reviewer's hits on the plan's own author is worth less than one that does not. Full text in `06_WORKING/CONDUCTOR_RULINGS.md`.

- **CR-3 was overstated.** *"Gates receive none. Ever."* is true of **text** and false as a claim about **influence**. Operator answers do reach gate behaviour transitively, by selecting which registered criterion set, profile, rubric and CTA class a gate evaluates against. Amended to separate the containment guarantee from the influence claim, and to name voice genre as the point where the bound is weakest.
- **CR-4 was read as exempting arrays from inspection, and that reading was correct.** It made CTA wording — the operator string most certain to ship byte-for-byte — the least-checked field in the surface, weaker than the brief. *Never rewritten* now explicitly does not mean *never inspected*.
- **CR-8's scan was scoped to the brief alone.** Extended to every operator-authored string that can reach a rendered asset, with its own residual limit stated rather than implied.
- **CR-9, CR-10, CR-11 are new** — exclusion-polarity checking, the removal of the custom-voice authoring hatch, and the identifier namespace.
- **The "10 CTA classes" figure in the rulings preamble was the conductor's error**, taken from annex `01`'s prose. The canonical count is **twelve**. This is reported to the operator as a correction of fact, not as a re-opened decision.

---

## 3. Reconciliation rulings

Binding. Wave 0 applies them; no Wave-2 task starts until it passes its barrier.

| ID | Conflict | Ruling |
|---|---|---|
| **CFG-C-1** | CTA class count: `06C` ruled 10, `06D` ruled 12, `06A` refused to rule | **Twelve.** `06D` is right on the merits and `06A` was procedurally right to refuse — a leaf may not self-authorise a change to a conductor ruling. `06C`'s resolution paragraph is struck; its Field 9 pick list expands. `06B` is structurally unaffected (its CTA row changes only in the length of the list it iterates); `06E` is unaffected, having already assumed both event and commercial-incentive exist. |
| **CFG-C-2** | The operator-authored CTA table has no field, no knob and no resolver input; `06E`'s assertion targets a different table | **Both tables exist and they join; neither replaces the other.** `06D`'s `(archetype × objective) → class` is **intent** and lands as a Tier-B field. `06C`'s Field 9 is a **destination inventory** and stays Tier A. `06E`'s `CFG-RA-15` is the **join** of the two plus fact class F-E, and is re-scoped to name which input supplies each of its five sub-conditions. A knob row is added to `06A`; an input row is added to `06B` §1.1. |
| **CFG-C-3** | `06D` says variously that the table *replaces* the pain-to-offer lookup and that it *joins* it; its no-table default is No-CTA | **"Joined" governs.** Precedence is explicit: specific row → wildcard row → **pain-to-offer lookup** → No-CTA. This preserves theme #1 by construction (whose current default is *"content and product-path on"*) and keeps No-CTA as the genuine floor for a tenant with neither table nor lookup. §1.1 and §1.4 of `06D` yield. |
| **CFG-C-4** | Pain-to-offer / relation-content mapping has no field, but `06A`, `06E` and `ARCHITECTURE_PLAN.md` all depend on it | **Field 11 becomes relation-content mapping**, conditional Tier A — required whenever an offer-attachment or product-promotion relation is in use, absent otherwise. The Notion connection currently occupying that slot is **not tenant-variable content**; it moves to a setup step outside the twelve. Brand-and-domain routing is carried explicitly by Field 1. |
| **CFG-C-5** | Declaring an archetype mix changes theme #1's behaviour; `06A`'s uniform-split default is worse still | **`CFG-PO-01` defaults to archetype slotting inactive** — CR-5's disposition (c), feature off. Theme #1 ships with B1, B2 and the added `email` destination **unset**. If the operator wants a mix for theme #1, it lands as a deliberate post-migration change with its own differential, or as a named exception in `00_MASTERPLAN.md` §7 criterion B. It may not arrive as a silent consequence of an amendment whose invariant is behaviour preservation. |
| **CFG-C-6** | `06C`'s esoteric fixture reproduces *"Proof discipline disabled (S-5). Hype-glue rule (S-7) waived"* — text `C-3` already struck | **Struck, again.** `C-3` forbids waiving any PROOF, NEXT-STEP or GLUE criterion by any objective, relation, archetype, angle or genre, and singles out the expressive class as *the* highest unlawful-claim exposure. For a reach-and-community objective those criteria stay active and are satisfied with non-commercial content or fail closed. Relation identifiers renumber to `PB-REL-n` per `C-5`; R-6 and R-7 drop pending `C-2`. |
| **CFG-C-7** | The fixture assigns 30% of its mix to *"personal-narrative"* and names *"commentary"* — neither is an archetype in its own registry (personal-narrative is angle #7) | **The fixture is rebuilt from the eleven-archetype registry and re-walked before it ships anywhere.** A falsification fixture that cannot pass its own resolver will be "fixed" by relaxing whatever it trips — which is **P-9's mechanism recurring inside the amendment that exists to close P-9**. It moves into Wave 1.5, where `00_MASTERPLAN.md` deliberately puts falsification because acting on it is still cheap. |
| **CFG-C-8** | Brief cap stated as 200 words, 200 characters, and "truncated and you're warned" — the last forbidden verbatim by CR-8 | **`06B` §5.3's derivation is the single definition**: the cap is not an independently chosen number, it is derived from §4.7's reserved-first allocation as the tightest per-node overlay allowance the brief must fit inside. Both counts are struck from `06C`. Nothing is ever silently shortened. The helper text claiming the brief *"does not reach posts"* is **false** — it reaches N-3, N-5 and N-6, the nodes that write the posts — and is replaced with wording that says so. |
| **CFG-C-9** | `06A` invents a fifth regime (`N/A-machine`); `06E`'s `CFG-RA-5` blocks the run on any knob without one of four. Eight knobs carry neither | **`06A`'s reasoning is right — a disk threshold is not a tenant knob — and `06E`'s assertion is right to be absolute.** The §10.4a machine rows are formally **excluded from the fold's domain** rather than given a fifth regime, which is `06A`'s own recommendation. As merged today, no configuration could ever execute. |
| **CFG-C-10** | Two incompatible provenance vocabularies; `CFG-RA-18` blocks the run on a stamp the resolver does not produce | **One stamp, five axes:** deciding layer · authorship class (affirmative / declared-empty / inherited) · derivation (named / inferred / defaulted) · disposition (applied / refused) · timestamp. `CFG-RA-18` and `06B` §2.0 are rewritten against it **together, by one owner**. This matters more than a vocabulary clash: provenance is the strongest safety argument in the corpus, and the merge was about to break the best control in the set. |
| **CFG-C-11** | The one non-fail-closed behaviour — a CTA URL dying mid-run | **The exception stands; the mitigation does not.** Continuing the run is correct: a dead URL is none of §11.3's three triggers, the CTA *degrades to a content class* rather than shipping dead, and stopping would discard paid research. But three fixes are required: **(a)** readiness re-evaluates before **every scheduled run**, stated as binding — otherwise "fails the next load" is not a control, because a cron theme in steady state never loads; **(b)** `06D`'s event-class pattern (*re-checked at spin time **and** at the platform gate*) **generalises to every CTA class carrying a URL**, closing the real dead-next-step window, which neither document currently closes; **(c)** the record auto-clears on a subsequent successful verification and escalates under the existing anti-flap rule instead of latching. |
| **CFG-C-12** | `06A` claims its twelve fields and `06C`'s twelve *"converged"* and calls that evidence the set is right-sized | **Struck.** They differ on three of twelve, and the count matched only because two errors cancelled — `06C` dropped a Tier-A knob and added one `06A` classifies Tier C. Arithmetic coincidence presented as evidence, in the document whose authority rests on counting carefully. Fields reconcile one-by-one against registry IDs, and the ceiling is re-checked: with CFG-C-2 and CFG-C-4 both needing homes, twelve is already breached in substance. |
| **CFG-C-13** | Occasion and evergreen lanes have knobs and no fields, so every theme resolves Trend-only — while the fixture's entire subject matter is occasion-shaped | **Add calendar and evergreen fields at Tier B, both defaulting empty-and-inert** (behaviour-preserving for theme #1). If Wave 2 cannot land them, the merged annex **states explicitly that PB-3's authoring surface is deferred and P-3/P-4 remain open, with a named owner.** The merge may not imply they are closed. |
| **CFG-C-14** | `06E` works from *"roughly 130 settings"* and *"roughly thirty"* defaultless rows | **141 and 35 are the counted figures; `06A` is right.** The section that owns behaviour preservation was working from the wrong denominator. `06A` is corrected in the same breath: the literal phrase *"no engine default"* occurs once, not twice, and its 35 silently widens CR-5's predicate to include "per source / per fact class / per vendor" — a defensible broadening, but it must be declared as one rather than presented as a correction to a count it does not measure. |
| **CFG-C-15** | Tier B is hidden until the operator has reviewed a first pack — and every editorial control the operator asked for lives in Tier B | **Progressive disclosure stays as the default affordance; an explicit "show advanced settings" path is added.** Otherwise the shipped configurations are not authorable at setup and the operator's request is answered on day fourteen. `06C` is internally inconsistent here already, shipping both configs with Tier B fully populated. |
| **CFG-C-16** | Broken and false citations, including one to `04_RECONCILIATION.md` — a file `00_MASTERPLAN.md` §0 records as *"Does not yet exist"* — and one attaching a safety rule to CR-1, which does not contain it | **Full citation sweep before merge; every §-reference must resolve.** A false citation attached to a safety claim is worse than no citation. Already a Wave-1 barrier condition; it was not enforced. |
| **CFG-C-17** | `06C` ships query syntax (`q=`, `tags=`, `lang=`, `intent = "…"`), workspace-shaped paths and a personal email address in a design document | **Format sweep.** The standing constraint is no code, no CLI syntax, no configuration syntax. Query surfaces are described in prose, as `05_query_steering.md` does. No addresses, no credential-shaped strings, no live-looking paths. |

**Two red-team findings are already ruled on in `CONDUCTOR_RULINGS.md` and are listed here for completeness:** the CTA-wording scanning gap (CR-4/CR-8) and the exclusion-polarity inversion (CR-9). **One remains open and is escalated to the operator** — see `CFG-OD-3` in §6.

---

## 4. The waves

Flat-wave leaf dispatch is the default. An orchestrating parent is used nowhere here: no wave has five or more tasks in one domain, no decomposition is unknowable up front, and file ownership is disjoint by construction.

### Wave 0 — reconciliation *(shared dependency: runs first, sequentially, single owner)*

| Task | Agent | Writes | Does |
|---|---|---|---|
| **W0** | `architect-reviewer` | `06_WORKING/06_RECONCILIATION.md` | Applies CFG-C-1…CFG-C-17 as binding rulings. Produces the reconciled twelve-field list against registry IDs, the single provenance stamp, the regime set with the machine rows excluded, the identifier renumbering, and a **verified count** of the merged readiness surface (§13.2's 11 + `03`'s 11 + `05`'s 4 + `06E`'s 18, de-duplicated — nobody has yet counted this, and four are marked *extends*). |

**Barrier:** every §-reference in the rulings resolves · every open-question ID is unique across all six files · the readiness count is stated as a number with its de-duplication shown · no ruling contradicts `CONDUCTOR_RULINGS.md` as amended.

### Wave 1.5-bis — falsification of the fixture *(before, not after)*

| Task | Agent | Writes | Does |
|---|---|---|---|
| **V1** | `content-marketer` | `06_WORKING/06F_fixture_walkthrough.md` | Rebuilds the esoteric fixture from the real registries (CFG-C-6, CFG-C-7) and **paper-walks it end to end**, naming every gate and decision point it touches and every one it fails. Per `00_MASTERPLAN.md` PB-OD-7 a fully paper-walked second playbook is a passing falsification outcome — this is that walk. |

**Barrier:** the fixture resolves cleanly under `06B`'s failure taxonomy · it waives no PROOF/NEXT-STEP/GLUE criterion · every archetype and angle it names exists in the registry it cites.

**Why this wave exists at all:** scheduling falsification after the irreversible merge is defect **P-9**, and this plan has now caught itself committing it twice. The first time was in `00_MASTERPLAN.md`'s original wave order. This is the second.

### Wave 2 — rework *(flat; disjoint by file; all five spawn together)*

| Task | Agent | Owns | Applies |
|---|---|---|---|
| **T1** | `api-designer` | `06A_knob_registry.md` | CFG-C-2 (new knob row) · CFG-C-9 · CFG-C-12 · CFG-C-14 · CFG-C-13's two lane fields · the duplicate `CFG-PS-09` key |
| **T2** | `prompt-engineer` | `06B_resolver.md` | CR-3 amended · CR-4/CR-8 extended scan · CR-9 polarity · **CR-10 (strike the custom-voice path)** · CFG-C-2 input row · CFG-C-10 stamp · CFG-C-8 cap derivation · genre *consequence* in the readback, not just its name |
| **T3** | `content-marketer` | `06C_authoring_form.md` | CFG-C-4 (Field 11) · CFG-C-5 · CFG-C-6 · CFG-C-8 helper text · CFG-C-15 · CFG-C-17 · CFG-C-1's expanded pick list · Field 1 carrying public brand identity and brand-domain routing |
| **T4** | `api-designer` | `06D_cta_authoring.md` | CFG-C-1 · CFG-C-2 · CFG-C-3 precedence chain · CFG-C-11(b)'s generalised platform-gate re-check · legal opens renumbered to `PB-OD-L-n` |
| **T5** | `workflow-orchestrator` | `06E_readiness_and_defaults.md` | CFG-C-2 (`CFG-RA-15` re-scoped) · CFG-C-9 · CFG-C-10 · CFG-C-11(a) and (c) · CFG-C-14 · its own assertion miscount |

`T4` is assigned to `api-designer` rather than a legal agent by operator instruction; the legal *content* of `06D` is preserved unchanged and only its structure, precedence and identifiers are reworked.

**Barrier:** each file passes a self-check that its assigned CFG-C rulings are applied and cited · no file re-opens a ruling · citation and format sweeps pass.

### Wave 3 — merge *(single writer, aggregating file, LAST)*

| Task | Agent | Writes |
|---|---|---|
| **T6** | conductor (main thread) | `06_config_surface.md` — this file, extended with the merged design |

The five working files remain as inputs. This file is the only aggregating artifact and has exactly one writer.

---

## 5. Aggregating files and wire-in

**Aggregating files — single writer, written LAST:**

| File | Sole owner |
|---|---|
| `06_config_surface.md` | conductor (Wave 3) |
| `06_WORKING/06_RECONCILIATION.md` | `architect-reviewer` (Wave 0) |
| `06_WORKING/CONDUCTOR_RULINGS.md` | conductor only — **no leaf may edit it in any wave** |
| `DECISION_LOG.md`, `RISK_LOG.md` | conductor, at Wave-0 close, per `C-5` |

**Wire-in — for every new symbol, where it is registered and who applies it:**

| New thing | Lands in | Applied by |
|---|---|---|
| Per-knob IDs, tiers, regimes | `ARCHITECTURE_PLAN.md` §10.2–§10.4a (column extension), §10.1 (count correction 130 → 141 → 178) | T1 |
| The resolver as a load-time step | §13.1/§13.2 load sequence; explicitly **not** §1.5's node inventory | T2 |
| Overlay/provenance stamp | §14.7's version-pinning list; §8.5 idempotency keys | T2 + T5 |
| Operator-authored CTA intent table | §10.3 (new knob), §6.9 (precedence chain), §6.3 F-E | T4 |
| Twelfth CTA class confirmed live | §6.7, §6.9, §6.10 S-6, §10.3 default, §13.3 fixture | T4 |
| Extended CR-8 scan | §6.11's leakage discipline; the claim gate's composition point | T2 |
| Config readiness assertions | §13.2 | T5 |
| Calendar / evergreen authoring fields | §10.2 | T1 + T3 |
| Second fixture | §13.3 | V1 + T3 |

---

## 6. Acceptance criteria

- **A.** Every CFG-C ruling is applied and cited in the file that owns it.
- **B.** No document asserts a safety property another document contradicts. `06B`'s registry-closure claim in particular must be **true**, not merely stated.
- **C.** An assertion that a playbook *"cannot"* is insufficient — every containment claim names the mechanism that enforces it and the point at which it fails. Inherited from `00_MASTERPLAN.md` §7.
- **D.** **Behaviour preservation is proved, not assumed.** `06E`'s AC-CFG-1 stands: resolved-form equivalence with an empty unexplained-difference set, plus frozen-eval-set replay at **decision level** — identical verdicts, bands, spin-rationale tuples and asset presence. Identical text is explicitly rejected as a test that would fail for the wrong reason. **The shipped theme #1 configuration must pass this**; today's does not.
- **E.** The second fixture falsifies a different ontology from theme #1 and **passes its own resolver**.
- **F.** No code, pseudocode, CLI syntax, configuration syntax, folder tree, address or credential-shaped string in any deliverable.
- **G.** The honest-limits section survives to §19: what the config surface **cannot** catch, and the fact that all readiness assertions pass on a config that is complete, coherent and simply wrong (**R-35**, unamended).

---

## 7. Open decisions for the operator

| ID | Question | Recommendation |
|---|---|---|
| **CFG-OD-1** | **The CTA class count is twelve, not the ten stated when you approved it.** Event is live in the current architecture in five places and deleting it would silently drop its future-dating requirement. | Accept as a correction of fact. Nothing about the mechanism you approved changes — only the length of the list. |
| **CFG-OD-2** | **The custom-voice escape hatch is removed** (CR-10). You pick one of six registered voices, or a new one is built as an engineering task. | Accept. The alternative is a tenant authoring the standard their own quality judge is calibrated against, which is the defect this amendment exists to close, one layer up. |
| **CFG-OD-3** | **A residual safety gap is being accepted, not closed.** The deterministic scan catches numbers and known proof lexicon. It does **not** catch proof-shaped claims with no digits — *"clinically studied"*, *"most of our clients"* — and this compounds with the expressive voice, which treats feeling-shaped assertions as interior truth rather than checkable claims. Closing it properly needs a judgment model at the config boundary, which reopens the transitive-influence problem one layer earlier. | **Accept the gap with the two narrow mitigations in CR-8** and revisit on Phase-0 evidence. State it plainly in §19 rather than discovering it in production. |
| **CFG-OD-4** | **The readback is self-attesting.** The resolver generates the description of its own decision. The reflexive check catches non-determinism (same input, different output) but not systematic bias (same input, confidently wrong every time). Your reading of it is the only real control. | Accept for v1, and set the confidence floors from Phase-0 trial data rather than asserting them now. The honest statement is that the readback currently asserts a confidence it has not yet earned. |
| **CFG-OD-5** | **P-3 and P-4 stay open** unless Wave 2 lands the calendar and evergreen authoring fields. Recurring and calendar content — a daily menu, a seasonal ritual, "post five times a week regardless" — remains impossible. | Land the two fields at Tier B, defaulting inert. If they slip, record P-3/P-4 as open with an owner rather than letting the merge imply otherwise. |

---

## 8. What this plan deliberately does not do

- It does not merge the five working files. They contain seven blocker-grade defects and are Wave-0 input.
- It does not close **P-8**. It downgrades it and names what remains.
- It does not add a judgment model at the config boundary, and says why.
- It does not reduce the number of decisions a tenant faces — 178 knobs is the honest count, up from a plan that believed it had 130. What it reduces is the number of decisions **wrong by default**, and the number a person must answer to start: twelve.
- It does not claim extensibility is proven. That requires either a real second tenant or the paper-walk in Wave 1.5-bis, per `PB-OD-7`.
