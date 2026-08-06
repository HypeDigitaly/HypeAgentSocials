# R10 — Full-plan adversarial review

*Fresh blind pass over the entire design-phase document set · 2026-08-06 · nine specialist reviewers, conductor-triaged*

**Scope reviewed.** `docs/architecture/ARCHITECTURE_PLAN.md` (§0–§18, Appendices A–B), `DECISION_LOG.md`, `RISK_LOG.md`, `STAGE5_APPROVAL_SUMMARY.md`, `docs/plans/PLAYBOOK_LAYER/` (masterplan + annexes 01, 02, 03, 05, 06 and the six `06_WORKING/` files), plus `HypeAgentSocials_InstructionsAssignment.md` and `docs/research/B4`.

**Method.** Nine specialists reviewed disjoint slices **blind to `docs/reviews/R1–R5`**, by operator instruction, so that findings are not anchored on five prior rounds. No legal-review agents were used (standing operator preference); that surface was covered by the security and architecture reviewers as *system requirements*, not legal opinion. Findings were then deduplicated, cross-checked and verified against the source text by the conductor. Every finding below carries its verification state.

**Verdict: 🛠️ Changes requested — do not approve Stage 5 as written.**

Not because the design is unsound. The core architecture is genuinely strong and its safety instincts are right. But this pass found **six confirmed defects that would each cause real damage in build**, and two of them (F-1, F-2) sit on the money and safety paths respectively. The prior five rounds (17 blockers, 61 majors, 34 minors) hardened the *content* of each section; what this pass found is concentrated in the **seams between sections** and in the **arithmetic behind the headline claims** — exactly the two places a section-by-section review does not look.

---

## 0. What the conductor verified personally

Before triage, five load-bearing claims were checked directly against the text. This matters because agent findings are hypotheses until confirmed.

| Claim | Verification | Result |
|---|---|---|
| W6-1 ("no manual pipeline inputs") never reconciled into the architecture plan | `grep -c "W6-1" ARCHITECTURE_PLAN.md` → **0**; `grep -ic "curated inbox"` → **23** | ✅ **CONFIRMED** |
| §9's canonical stage order differs from §14's canonical per-asset chain | Read both. §9 (line 1708) ends `…assembly → packaging`. §14 (line 2180) ends `…assembly → asset QA rubric → packaging` | ✅ **CONFIRMED** — §9 omits the asset QA rubric |
| §6.5 still says "four fail-closed triggers"; §11.3 says five | §6.5 line 1265 "one of the **four** fail-closed triggers"; §11.3 line 2011 "None of these **five** trigger classes" | ✅ **CONFIRMED** |
| Rung 3 is the destination for gate-blocked content, yet packaging precedes the publish gate | §7.2 line 1487: "rung 3 is the destination for every unconnected channel and **for every asset the gate blocks**"; checklist "produced at packaging, not at the gate"; §9 line 1708 places packaging **before** the publish gate | ✅ **CONFIRMED as an ordering contradiction** (partially mitigated — see F-2) |
| Exactly eight `06A` knob rows carry a bare `N/A` regime | `grep -o "| N/A |"` → **17** cells; `grep -o "N/A-machine"` → **6**. Could not reproduce the count of 8 | ⚠️ **KIND CONFIRMED, COUNT NOT** — the two-tag distinction is real; the arithmetic in F-11 must be re-derived before acting |

---

## 1. 🔴 CRITICAL findings

### F-1 · The cost forecast omits the highest-volume model node in the system
**Where:** `ARCHITECTURE_PLAN.md` §5.4a (LLM budget block) + §1.5 node inventory row N-1
**Found by:** AI-pipeline reviewer **and independently** by the cost reviewer. **Confidence: HIGH.**

§5.4a computes the text forecast as *planned artifact count × the gate stack's per-artifact call profile × token ceilings* — roughly five evaluations across ~130 artifacts. **N-1 (brand-fit judgment) runs once per candidate, in the ranking stage, before artifacts exist.** It is not in that arithmetic at all. Its stated bound is "candidate count × the N-1/N-2 nodes" — i.e. the bound is a function of the very quantity that is unbounded. **No section of the plan or of any annex ever states an expected candidate volume.**

This is not a rounding error. The plan's central architectural justification — *cost is computable before the run starts* — rests on a number that is not computed.

**Failure scenario.** A normal daily run: HN Algolia ~100 hits, Bluesky up to 100/query, Google News ~100 items × several feeds × two locales, plus Product Hunt, HF, YouTube, newsletters, Virlo. After deterministic screens, several hundred candidates still reach N-1. The pre-run forecast is derived from ~130 artifacts and is off by an order of magnitude before a single word of copy is drafted. The text budget trips *inside ranking*, and the pack is empty for a reason the forecast could not show.

**Compounding:** research collection is recommended **daily** (§8.2) while economics are denominated **per topic pack**. Seven ranking passes a week are therefore invisible to every cost figure the operator ever sees.

**Fix.** Declare per-source result caps in the query profile (05 §5.2 already requires them), sum them into a **declared maximum candidate count per run**, and add `candidate_count × N-1 call profile` as an explicit third term in §5.4a, printed as its own digest line beside media and text-per-artifact. Add a per-collection-run cost line denominated per collection run. Readiness asserts the summed caps × N-1's ceiling fits the ranking stage ceiling.

---

### F-2 · Human approval is not bound to the bytes approved
**Where:** `ARCHITECTURE_PLAN.md` §11.4, §7.4 check 3, §4.7a, §8.11, §12.4, Appendix A.8
**Found by:** Security reviewer. **Confidence: HIGH.**

The publish gate asks only *"does the review-decision store hold a recorded approve decision for this asset."* §11.4 keys decisions **by run id and asset id**. Meanwhile §4.7a reopens an already-reviewed pack as revision 2 when a later run assembles a pending master; §8.11 does the same for budget-capped masters; §12.4's immediate loop regenerates in place. **Packaging's idempotency key gained a revision number; the approval record did not.**

The claim gate is specified as *"final, immutable, on the exact bytes that enter the pack."* The approval that authorises those bytes has no equivalent binding.

**Failure scenario.** Appendix A's own run. The operator batch-approves at revision 1 (§12.1 makes whole-pack approval the default affordance, with high-band topics **pre-selected**); the English video master is plan-only, blocked on clip 2. Next night, unattended, the pipeline adopts the clip, assembles, masters, and amends the pack to revision 2. With the unattended draft-creation knob on — whose stated precondition is *exactly* "a human-approval state was already recorded during an earlier interactive session for that asset" — the publish gate finds an approve against that asset id and prepares drafts for a 20–30-minute-review-class video **that no human has ever watched**.

**Fix.** Bind each approve decision to a content fingerprint (packed-bytes hash + pack revision). Any amendment, regenerate or re-assembly invalidates prior approvals for that asset and returns it to unapproved. Add "approval fingerprint matches current bytes" as a publish-gate check and as a Phase-6 fail-closed acceptance condition.

---

### F-3 · The canonical gate chain is stated three times with three different contents
**Where:** §9 (line 1708, "canonical"), §14 (line 2180, "canonical … D-21, binding"), §6.10 diagram (1393–1412); §10.5 assigns ownership to all three at once
**Found by:** Architecture reviewer. **Confidence: HIGH — conductor-verified.**

- §9 ends: `platform gate → media planning → cost gate → media generation → assembly → packaging`
- §14 ends: `… assembly → asset QA rubric → packaging`
- §6.10 ends: `… assembly → POST-ASSEMBLY OVERLAY CLAIM PASS → asset QA rubric → packaging`, plus the claim-2 repair re-entry loop

So **§9 omits both** the asset QA rubric and the post-assembly overlay claim pass; §14 omits the overlay pass and then four lines later states flatly that "the claim check runs twice." §0.2's single-owner list does not cover the stage order at all, and §10.5 names all three sections as joint owners — so there is no tiebreak.

**Failure scenario.** An implementer builds the pipeline from §9 — explicitly labelled canonical, and the section both walkthroughs use — and never builds the post-assembly overlay claim pass. Every claim-bearing on-screen string, including the "300% ROI graphic" §6.7 calls *"exactly the artefact type that escapes text-only checking"*, is composed at assembly after claim pass 2 has closed and is **never checked at all**. No Phase-3 or Phase-4 acceptance criterion tests the overlay pass. This ships.

**Fix.** Name one owner — §14's opening is the natural home — and make §9 and §6.10 pointers with no ordering of their own. Add both missing steps to that single statement, name which deterministic check classes the overlay pass runs, and add a Phase-3 acceptance criterion: an unsupported number composed into on-screen text at assembly is blocked.

---

### F-4 · Every start-time fail-closed stop fires before the phase-0 drain, so a config edit can destroy already-paid media
**Where:** §9.2 (unattended stage order), §11.3, §8.13; `06E_readiness_and_defaults.md` §3.2 CFG-RA-1/2/3/5/11/12/18 and §4.7
**Found by:** Cron/state reviewer. **Confidence: HIGH.**

§8.13 makes phase-0 adoption + expiry-ordered drain the **only** mechanism converting paid provider media into a durable artifact, and §4.7 says opening the application at all is what rescues paid work. But §9.2 orders the unattended run `secrets load → run identity → lock → phase 0`, and §11.3 makes any absent-or-unreadable secret a hard stop at theme load. 06E adds seven config assertions that block the run outright. **All of these execute before phase 0 and none has a carve-out for the drain.**

Note also: §9.1 (interactive) puts phase 0 **before** secrets load. The two paths differ in exactly the way §8.1 promises they never do — and the unattended one is the broken ordering.

**Failure scenario.** Run N submits 12 clips, exits `completed-with-pending-media`. Next day the operator edits one authoring field and does not accept the readback (or a key is rotated and one declared secret is now malformed). Every subsequent scheduled invocation refuses to start. Nothing drains. Day 14: the provider hard-deletes all 12 paid artifacts. The block message names config fields, not undownloaded media, so the operator has no reason to know it is urgent.

**Fix.** Make the phase-0 drain a pre-gate stage depending only on the router credential and the media-job ledger, executed before secrets validation, readiness assertions and brand-truth resolution. Every "blocks the run" condition then blocks *new work*, not the drain. Add a `drain-only` invocation with its own exit class, and make every blocking message name outstanding pending jobs and their deletion dates.

---

### F-5 · Nothing prevents a second *completed* run for the same run-date — double spend on DST and wake-from-sleep
**Where:** §8.3, §8.4, §8.5
**Found by:** Cron/state reviewer. **Confidence: HIGH.**

The lock and `skipped-overlap` defend only against a **live** second process. No uniqueness rule exists on `(theme, run-date)` for a run that already finished, and §8.5 positively argues a same-day rerun is legitimately different work — so the media identity (which carries attempt number) will not deduplicate it.

**Failure scenario.** Autumn DST fall-back, local-time trigger: 02:30 fires, the run finishes 03:10, the clock rolls back to 02:00, 02:30 fires again. Lock free, run-date identical, attempt increments, the cost gate sees a fresh per-run budget — **the whole pack is generated and paid for twice.** Identical shape when Windows' "run task as soon as possible after a missed start" fires after a manual catch-up run, or when a laptop resumes from sleep after a normal run.

**Fix.** Run-ledger uniqueness on `(theme, run-date)` for spend-bearing runs; a completed-run guard exiting at a named `skipped-duplicate` class; attempts above 1 only via explicit operator invocation; per-run budget counters keyed to run-date, not to a process.

---

### F-6 · W6-1 abolished the curated inbox, and the architecture plan has not heard about it
**Where:** `DECISION_LOG.md` W6-1; `ARCHITECTURE_PLAN.md` §2.2, §2.3, §8.12, §9.1, §10.2, §12.1, §13.3, §15 R-06, §16.2 OD-16, §17 Phase 7, §18, Appendix A
**Found by:** Architecture reviewer **and independently** by the cost reviewer. **Confidence: HIGH — conductor-verified (`W6-1`: 0 references; `curated inbox`: 23).**

W6-1 states: *"No manual pipeline inputs of any kind."* The risk log retires W2-01 and re-sources **Reddit only**. But the curated inbox is not a Reddit mechanism — per §2.3 it is the declared connector class for **six** sources:

| Source | What is lost |
|---|---|
| LinkedIn Ad Library | The B2B ad-creative axis — "systematic browse is a human activity, permanently" |
| Google Trends CSV | The **designed degraded state** for the demand axis |
| TikTok Creative Center | Per OD-16 option (c), the **terminal rung of the trend-vendor fallback ladder** |
| LinkedIn organic | "P2, human only, permanently" |
| Czech-native venues | "Czech communities and meetups are human-only" |
| Long-tail P2 group | GitHub trending, podcasts, review sites, Discord/Slack |

Three consequences, none recorded anywhere:
1. **The trend axis loses its floor.** If Virlo fails and Shortimize fails, the short-form axis has no bottom rung — it just goes absent.
2. **Two of the four Czech-signal carriers go.** §2.3 names four; the demand-axis CSV fallback and the LinkedIn ad library are both curated-inbox-only. W6-03 accepted a Czech residual risk sized against the loss of a *remedy*, not the loss of the *sources*.
3. **Phase 7's winners loop loses its input path** — §17 describes outcome capture as running "through the same curated-inbox mechanism already built in Phase 1." Phase 7's acceptance criterion becomes unsatisfiable, and Phase 8 cannot start because its gate is a completed calibration cycle.

**Fix.** Reconcile before approval. For each of the six sources state explicitly: dropped (with the axis loss named in §2.3), re-sourced (with vendor and cost), or retained as an operator activity *outside* the pipeline. Restore a terminal rung for the trend ladder that is not a human ritual. Either carve outcome notes out of W6-1 as a third permitted input (defensible — they are post-hoc annotations, not pipeline inputs) or redesign Phase 7's winners half. Re-open W6-03's risk acceptance.

---

## 2. 🟠 MAJOR findings

### F-7 · The headline per-pack cost is media-only, and the text wallet has no trial funding
**Where:** `STAGE5_APPROVAL_SUMMARY.md` line 12; §5.4 table, §5.4a, Appendix A.6, §17 Phase 4. **Found by:** cost reviewer (+ product reviewer). **Confidence: HIGH.**

Four compounding defects:
- **(a)** "~$1.91 per default two-language pack" is Appendix A.6's **media total**. A.6 says so plainly ("The media total is not the pack total"); §5.4 says text is "the same order of magnitude." The approval summary drops the qualifier. The all-in figure is roughly double.
- **(b)** §5.4's economics table header reads **"What $50 buys (media + text)"**. The $50 is Kie.ai router credit. Kie credits cannot buy text tokens — different vendor, different account, and the whole point of §5.4a is that these are two independently capped wallets. The column is arithmetically impossible.
- **(c)** The trial envelope ($8 bake-off / $35 packs / $7 reserve) has **no text line**, yet Phase 4's gate requires "both wallets are measured." Phases 0, 2 and 3 are the text-heaviest phases in the build — golden sets in two languages, frozen eval sets, the full gate chain exercised with deliberate failure injection, plus a mandated pre-rollout eval comparison on *every* prompt change (§14.8). Phase 2 is described as "still zero media spend," which reads as cheap and is not.
- **(d)** $1.91 is a **best case**: A.6 includes one rejected keyframe and zero clip regenerations, while §4.1 states roughly a third of first-pass AI video shows obvious flaws and §4.9/D-54 sets a QA-rejection cap of two. One regenerated clip is +$0.30; one non-localisable rejection re-shoots the whole master at +$0.90 on a $1.91 base.

**Fix.** Restate as two numbers (media, text) everywhere including the approval summary. Correct the "$50 buys (media + text)" column. Add a separately funded text envelope with a hard account-level cap at the text vendor. Publish an expected-cost-with-rework figure using the plan's own one-third defect rate. Add Phase-0/2/3 text-budget lines.

### F-8 · Operator review capacity is oversubscribed by 3–6×, and the plan's own table contradicts its own target
**Where:** §3.5, §3.2, §12.1, §16.2 OD-8. **Found by:** cost reviewer (+ product reviewer). **Confidence: HIGH.**

§3.5's per-asset times and §3.5's whole-pack target are arithmetically incompatible. The identical-mix matrix produces ~13 assets per topic per language. At §3.5's own rates that is 14–20 min per topic per language; two languages, 28–40 min. Five topics = **140–200 minutes of copy review alone**, before video. Add 1–2 masters per language at 20–30 min each and a pack run costs **3–5.5 hours**. §3.5's stated target is *"five topics reviewed in under thirty minutes."* Recommended cadence is three runs a week.

The offered mitigation — confidence-gated pre-selection and whole-pack batch approval as "normal" — is not a throughput fix. It is the same failure the plan condemns in R-21 ("turns the gate into theatre"), applied to the human gate. And this gate is not merely quality control: §11.4/§12.2 make approver identity and the editorial-responsibility holder the evidence base for OD-24's AI-Act editorial-review carve-out. **A batch-approved pack is an unevidenced carve-out.** R-35's stated detection for a coherent-but-wrong theme is "the first pack, read with the spin rationale column open" — the one control with no machine substitute is the first one dropped under load.

**Fix.** Cost the burden explicitly as a table (assets × minutes × languages × topics × cadence) and reconcile it against the target, which must be deleted or re-derived. Then either cut the default matrix (X off, one of TikTok/Shorts video per language per run, blog off), or cut default topics per run to two or three, or record a batch approval as a **distinct decision class** ("approved unread") that cannot be used as OD-24 evidence. Add a §15 risk row: review-capacity insolvency, detected by decisions-per-minute rate in the review-decision store.

### F-9 · Amendment A is not severable from Amendment B
**Where:** `00_MASTERPLAN.md` §5 tasks A2/A3, §4 rulings C-4 and C-12, §6 Wave 0. **Found by:** architecture reviewer. **Confidence: HIGH.**

A2's charge is "check class 12 **deterministic-only per C-12**"; A3's is emptiability "with **C-4's** external-verifier substitution floor." C-4 and C-12 are rows in a table headed *"Wave 0 of **Amendment B**"*, and no Wave-1 task starts until `04_RECONCILIATION.md` passes its barrier. C-4's own text says: *"The merged wording is written in `04_RECONCILIATION.md`, not deferred to a Wave-1 author."* **That file does not exist** and is produced by a wave that runs *after* the approval Amendment A is supposed to precede. So Amendment A either ships against one-line table summaries instead of merged wording, or it waits for Amendment B — which is exactly the bundling the split was created to avoid.

**Fix.** Lift C-4 and C-12 into an "Amendment A prerequisite rulings" section written in full before A1–A3 dispatch. Strike C-4's "written in 04_RECONCILIATION" instruction for the Amendment A portion; state that 04 may restate but not re-decide them.

### F-10 · Check class 12 has no execution point in the canonical order, and its flag cannot be set deterministically
**Where:** `00_MASTERPLAN.md` C-12; `02_legal_claim_packs.md` §3.1, §3.6; `ARCHITECTURE_PLAN.md` §6.7, §8.13, §5.6, §10.3, §0.2. **Found by:** architecture reviewer **and** security reviewer, from different angles. **Confidence: HIGH.**

Two independent defects in the P-11 fix:

**(a) No execution point.** Check classes execute at the claim gate, which runs passes 1 and 2 *before* media planning and generation. The provenance record does not exist yet — §8.13 and D-20 both state it is resolved *after* completion. So the fix for P-11 sits in a gate that closes before the artefact it must inspect exists. A4's edit list omits every section that could relocate it (§7.4, §9, §6.10), and also omits §10.3 (still reads "which of the **eleven** claim check classes run") and §0.2 (still says "the eleven claim check classes live in §6.7").

**(b) The flag has no deterministic setter.** C-12 reduces class 12 to verifying that every asset **flagged as depicting a real sellable item** carries a linked reference. But §3.1 defines the flag with a two-limb test whose second limb is explicitly perceptual — the image "reads to a viewer as a depiction of *that specific item*." Limb (a) is derivable from the spin record; limb (b) is derivable from nothing v1 possesses, because C-12 simultaneously rules out a vision node and budgets zero for one. No component is named as the flag's setter.

**Failure scenario.** A Policy-B restaurant tenant's asset is planned as "Policy C — ambience/mood." A plain text-to-image route renders a photorealistic plated dish. Nothing flags it, class 12 never fires, no reference is required, no attestation triggers, and the image ships publish-ready depicting a dish the tenant does not serve — **the exact P-11 scenario, passing through the fix.**

**Fix.** Move class 12's enforcement to the publish gate's provenance-completeness check (where an incomplete record already hard-blocks) or to the post-assembly overlay pass, and say so in C-12. Make the flag deterministic and over-inclusive: any asset whose spin record touches an F-B/F-P/F-T item **and** whose route class is image/video is flagged, full stop; Policy C available only when the generation request carries no item reference. State that "reads to a viewer as" is a human-review question layered on the machine flag, never the flag's own condition. Add §7.4, §9, §6.10, §10.3, §0.2 to A4's edit list.

### F-11 · Rung-3 staging composes gate-blocked content into paste-ready form
**Where:** §7.2, §7.4 layer 3, §9, §17 Phase 6. **Found by:** architecture reviewer **and** security reviewer. **Confidence: HIGH — conductor-verified as an ordering contradiction; partially mitigated.**

§7.2 is explicit: *"rung 3 is the destination for every unconnected channel and for every asset the gate blocks."* Its fix places the label checklist **at packaging, not at the gate**, and restates §7.4's trigger to "before any distribution preparation" so the gate's scope "covers rung 3." But §9's canonical order places **packaging before the publish gate** — so a rung produced at packaging cannot be inside the scope of a gate that runs after it. Phase 6's acceptance criterion settles which one gets built: it *tests* that a gate-blocked asset arrives in rung-3 staging with an unticked checklist.

The safety consequence: blocked content is composed into paste-ready per-platform form and handed to the operator, and the only compensating control covers the **platform label**, not the **reason for the block**. In test mode — the default — the allowlist is empty by construction, so **every** destination is blocked for **every** asset. That includes assets blocked on a CONTRADICTED claim verdict, on unresolvable rights class, and on absent human approval. Each carries a tick-box about a TikTok AIGC toggle and nothing about why it was refused.

*Fair to the plan:* §7.2 states honestly that the burned-in disclosure was never at risk and that what was skipped was the platform-contractual label layer. That is true. The residual defect is the ordering, and the conflation of *availability* blocks with *safety* blocks.

**Fix.** Split the two cases. Rung 3 is legitimate for **unconnected** destinations (an availability gap). It must be structurally impossible for an asset blocked on a **safety** condition — claim verdict, approval absent, provenance/rights incomplete, disclosure out of band — to be composed into paste-ready form at all; those get the plan-only shape. The rung-3 file carries the refusal reason **above** the content. Correct the D-23/F-4 "single enforcement point" claim to name what it actually enforces.

### F-12 · "Calibrated" means only that a pointer exists
**Where:** §14.2; `03_pipeline_and_gates.md` §4.5, §8 readiness; `00_MASTERPLAN.md` §8. **Found by:** prompt/eval reviewer. **Confidence: HIGH.**

Readiness "asserts a playbook declares an eval-set pointer and a golden-set pointer per configured language" — **existence, not size and not measured agreement.** §14.2 describes golden-set composition qualitatively and names no count. So "v1 calibrates two genres" rests on a binary existence gate. This is the same absence the plan condemns elsewhere (§6.5: *"no calibration mechanism and no measurable ground truth… two implementers would produce two different band functions"*) — and §6.5 was fixed by converting to counting rules. §14.2 was not.

Compounding: `03` §4.6 pools the flag-rate ceiling across themes sharing a genre profile *specifically because* "a ceiling computed on four artifacts is noise dressed as a control" — then gives the pooled ceiling **no volume floor of its own**. At one operator with one or two themes, pooling barely changes the artifact count. It is the same thin stream under a different label.

**Fix.** State a minimum golden-set size and a minimum agreement sample before a genre×language pair may be marked calibrated, on the same footing as §6.5's counting-rule fix. Give the pooled ceiling its own stated volume floor, sized against this operator's real weekly volume, so the plan can say honestly when — if ever — it activates. Record as an open decision that the ten uncalibrated genres may remain **permanently** uncalibrated absent a stated volume trigger.

### F-13 · The discovery-mode topic filter defeats the readiness condition that exists to protect discovery
**Where:** `05_query_steering.md` §5.3 vs §4.3 and §5.1. **Found by:** AI-pipeline reviewer. **Confidence: HIGH.**

§5.1 defines discovery mode as existing because *"steered-only collection can only ever return what the operator already thought of, which is the mechanism by which a content pipeline slowly narrows into its own echo."* §4.3 makes at least one discovery source a **readiness condition**. §5.3 then places a deterministic lexical filter **on discovery-mode items only**, matching against the topic object's surface forms and aliases. An item about something not already in the alias list matches nothing and is dropped. **The filter reimposes, at normalisation, exactly the blindness the discovery-mode readiness condition exists to prevent** — and only on the sources that carry discovery value, since steered items "must not be filtered twice."

**Failure scenario.** An unknown lab ships a coding agent under a name nobody has typed into the theme config. It hits the HN front page at 400 points and leads two newsletters. Discovery-mode; no configured surface form matches; dropped at normalisation; never reaches N-1; never appears on a scorecard. The digest reads "Hacker News returned 30 items, 4 matched watch topics" — which the operator reads as a quiet day.

**Fix.** Split disposition by evidence class. Non-matching **counted-evidence** items above a per-source engagement percentile bypass into a named *unmatched-high-signal* bucket that reaches N-1 (brand fit is the correct arbiter — that is what the fit floor is for); non-matching presence-only items drop as designed. Print the bucket in the digest as a standing "topics we saw that your watch list does not name" line — which is also how the operator learns their keyword set has gone stale.

### F-14 · Every surviving factor in the Czech composite is derived from English observation
**Where:** §2.7, §2.3 (Google Trends row). **Found by:** AI-pipeline reviewer. **Confidence: MEDIUM-HIGH.**

The Czech composite is *brand fit × freshness × confidence-and-availability*, demand modifier applied after. Each factor: **freshness** is keyed to observed attention age, which for an English-discovered topic is the *English* first-sighting; **confidence** counts corroborating source families, all of which observed the topic in English; **brand fit** is judged by N-1 whose bounded input is the ICP map excerpt, with **no statement anywhere that the excerpt is filtered to segments whose language property is Czech**. The only Czech-audience signal in the architecture is the demand modifier at Czech geography — and §2.3 says of it that "at weekly cadence it cannot participate in daily scoring at all." So on any daily run the Czech ranking is a re-sort of English discourse by three English-derived numbers.

**Failure scenario.** A US-only Product Hunt launch with no Czech availability. Clears the Czech fit gate (the ICP map has a lead-gen segment; nothing tests that segment's language). Freshness high, confidence high, Czech composite high — a Czech TikTok/Reels/Shorts master is produced for a topic with zero Czech search demand, costing 20–30 minutes of human video QA.

**Fix.** (a) Scope N-1's ICP excerpt to segments declared in the candidate's target language — a per-language brand-fit verdict, not one verdict reused. (b) Make the demand modifier **gating** rather than modifying for the no-counted-evidence composite: a Czech candidate with no Czech demand observation inside the demand source's cadence window is ranked but capped into monitor-only, not promoted to generate.

### F-15 · Multiplication is not the anti-forced-placement mechanism the plan says it is
**Where:** §2.7; `03_pipeline_and_gates.md` §6.3. **Found by:** AI-pipeline reviewer. **Confidence: HIGH (formal).**

§2.7 justifies the product form: *"in a sum, a very high virality number can outvote a very low fit number; in a product, a near-zero factor drags the whole result toward zero."* A product **is** a weighted sum of logarithms with equal weights — exactly as trade-offable as the sum it replaces. The stated protection comes entirely from a factor being *near zero*, and the fit gate has already made that impossible: after the 0.35 floor, brand fit ranges over [0.35, 1] while percentile-normalised virality ranges over [0, 1]. **Above the gate, virality has strictly more ordering influence than fit** — the opposite of the design intent. `03` §6.3 then refuses per-axis weights *on the grounds that* "multiplication is the anti-forced-placement mechanism" — a governance refusal resting on a property the formula does not have.

*Worked counterexample:* A (fit 0.90 × virality 0.40) = 0.36; B (fit 0.36 × virality 0.95) = 0.34. Near-equals; slightly better freshness and B wins the slot. B is a barely-fit topic riding a launch spike — the precise forced-placement case the section says cannot happen.

**Fix.** State the true mechanism: the floor plus §6.9's mapping-distance rule are the anti-forced-placement controls; the product is a neutral aggregator. Then either raise the floor or rescale brand fit post-gate to span [0,1], restoring the drag-to-zero behaviour the prose promises. Re-argue `03` §6.3's weight refusal on the honest ground — weights have no calibration mechanism, which is true and sufficient.

### F-16 · §2.8a's resurgence state machine is not total, and "suppressed permanently" is unimplementable
**Where:** §2.8a. **Found by:** AI-pipeline reviewer. **Confidence: HIGH.**

Three defects in one table. **(a)** The declared trajectory set is "rising, flat or declining"; the matrix uses "rising", "rising or sustained" and "declining" — **"flat" appears in no row.** **(b)** Trajectory is sampled from **counted** sources only, so any candidate sourced from presence-only feeds (Google News, newsletters, Czech trade press) has no trajectory value and matches no row. `03` §2.1 diagnoses exactly this for calendar candidates and repairs it only for declared-recurrence entries. **(c)** The section scopes inputs to "the rolling lookback window", but the declining+generated cell says "**suppressed permanently**" — after the window scrolls, prior-pack state is gone, the cluster reads as never-generated, and it regenerates.

**Failure scenario.** A vendor with a weekly release cadence. Week 1 rising/never-generated → pack ships. Week 2 declined from peak, prior state generated → **suppressed permanently**. Every subsequent weekly release is dead, no expiry, no override — while an *operator* rejection of the same cluster gets a bounded window plus a corroboration-growth override. **An algorithmic suppression is stricter and more permanent than a human one.**

**Fix.** Declare the domain {rising, flat, declining, **indeterminate**} and give all twelve cells an outcome; route *indeterminate* to the same treatment as *rising*. Replace "suppressed permanently" with a configured cluster-suppression window bounded by the dedupe lookback, with the same corroboration-growth override the rejection row already has.

### F-17 · The exit-code taxonomy is neither total nor mutually exclusive, and two phase gates are unfalsifiable
**Where:** §8.8; §5.7, §5.6, §4.7a, §5.2, §11.3, §8.13; §17 Phase 1 and Phase 5 gates. **Found by:** cron/state reviewer. **Confidence: HIGH.**

Every media-side and gate-side degrade produces an honest-but-incomplete pack and **none maps to a class**: `partial-success` exists only in two flavours, `completed-degraded` is reserved for the brand-truth degrade, and `success` would be a lie. Conversely the classes routinely co-apply — one dead source + a Czech cap hit + three clips rendering satisfies three at once — and §8.8 states **no precedence** while insisting the exit code is the scheduler-visible signal. Phase 5's gate ("exit classes match what actually happened") cannot be adjudicated when two genuinely match; Phase 1's gate ("classes are distinguishable") passes trivially because with no brand truth, no money and no media, six of nine cannot be produced at all.

**Fix.** State a total ordered precedence (hard-failure > policy-stop > budget-stop > partial-success variants > completed-degraded > completed-with-pending-media > success > skipped-overlap). Add `partial-success — degraded output` covering refusals, paid-lost, assembly failure, stale-route degrade and un-runnable gates. Have the run ledger carry the full co-applying set. Rewrite the Phase-1 gate to require each class be **forced** by fault injection.

### F-18 · Overlay fingerprint in the idempotency key makes resume-after-config-edit a double-spend
**Where:** `03_pipeline_and_gates.md` §4.4; `CONDUCTOR_RULINGS.md` CR-2.4; §8.5, §8.7, §8.11. **Found by:** cron/state reviewer. **Confidence: HIGH.**

The fingerprint digests the resolved config, so **any** accepted config change moves it, and the idempotency key must contain it. Resume identifies work by key. Therefore after any accepted edit, every incomplete unit computes a key never seen and reads as "never started" — **including slots whose paid attempt chain already exists under the old key.** 06E §4.7 forces exactly this edit-then-accept sequence before any further run.

**Failure scenario.** A run exits budget-capped. The operator raises the cap — a config edit, so re-resolution and acceptance are forced, so the fingerprint changes. They issue `regenerate-media-only` against the same run id. Under the new key the *completed* English masters also read as never-started and the cost gate pays for them again; under the old key the pack silently mixes two overlay generations, the failure §4.4 exists to prevent. **Both are defensible readings of the current text.**

**Fix.** Split the key: cost-bearing asset identity **excludes** the fingerprint (theme/run-date/topic/slot/language/attempt); the fingerprint is recorded **on** the ledger row. Resume compares recorded vs current and on mismatch takes a named per-unit decision — adopt-as-is (recorded as a mixed-generation pack, flagged in the digest) or abandon-the-slot — never an implicit new key. State the rule in §8.5.

### F-19 · Fail-closed enumeration gaps — deterministic passes and measurement steps have no failure behaviour
**Where:** §11.3 fifth trigger, §1.5, §6.7, §11.2. **Found by:** security reviewer. **Confidence: HIGH.**

The fifth trigger is well built for **model-mediated** nodes — thirteen inventory rows, seven named degraded outcomes. It stops there. Three classes have no stated failure behaviour:
1. **The deterministic passes.** §6.7's whole control-integrity argument is that the deterministic pattern/dictionary/entity pass runs first and *guarantees* nothing escapes examination, and that a model-only checker is not a control. §11.3 says what happens when the semantic pass dies; **nothing says what happens when the deterministic pass dies** — leaving the semantic pass running alone, i.e. the exact configuration §6.7 rejects, with no signal.
2. **The measured gates.** Loudness, disclosure type-height/contrast/timestamp, glyph coverage, local ASR adherence — all fail closed on an out-of-range *result*; none states what happens when the measurement **cannot run**, and none appears in the fifth trigger's list.
3. **The two named gates.** §11.2 says the cost gate and publish gate consume the resolver; the fifth trigger names outcomes for neither.

**Fix.** Extend the trigger from "any gate or judgment node" to "any gate, judgment node, deterministic pass or measurement step," with a named degraded outcome for each. For the deterministic claim pass the outcome must mirror N-10: semantic verdicts alone never suffice, and every claim-shaped candidate blocks.

### F-20 · The AI-disclosure floor is measured but ends in a human-overridable QA flag
**Where:** §4.4, §4.9, §7.4. **Found by:** security reviewer. **Confidence: HIGH.**

§4.4 states the floor is "mandatory, non-relaxable, and measured rather than asserted," and an out-of-range asset "fails closed." §4.9 names the actual disposition: an out-of-tolerance measurement puts the asset **into the pack flagged for human decision**, and on QA-cap exhaustion the terminal is "**ship the last generated version**… The operator may still promote it by hand." §7.4's publish-gate checks include label *acknowledgement* and provenance completeness but **never the disclosure measurement**. So "cannot be marked publish-ready" is enforced for **absence** of the overlay, not for **non-compliance** of it — precisely the grey-8pt-type-in-the-final-half-second case the floor exists to kill.

**Fix.** Move the three measured items into the publish gate as a hard precondition alongside provenance completeness, same disposition (plan-only, reason attached), **no promote-by-hand path**. Add the audible-equivalent disclosure to the measured set — its floor is stated in §4.4/§10.4 but has no measurement defined anywhere, so on a TTS-led Czech asset it is asserted, not checked.

### F-21 · The blog/site path reaches an outward-facing effect without traversing the publish gate
**Where:** §7.3, §11.1, §7.4. **Found by:** security reviewer. **Confidence: HIGH.**

§11.1 records blog/site prep as "Allowed — artifact-only, no live effect, **so no mode restriction applies**," identical in all three modes. §7.4 fires "before any distribution preparation"; producing a run-pack article is not distribution preparation, and no section names an enforcement point for it. Yet the article is the **highest-claim-density asset in the system** (§7.3 concedes it "carries materially more claims per asset"), it ends in a manual production-site merge, and it carries generated hero and supporting visuals. None of the gate's checks — approval naming the editorial-responsibility holder, provenance completeness, rights-class allowlist, label acknowledgement — is asserted on this path. Rung 3 got a packaging-time checklist for exactly this reason; the blog path got nothing.

**Fix.** Either route blog artifacts through the publish gate with "the brand's own site" as an allowlist entry, or emit a packaging-time pre-merge checklist (approval identity, editorial-responsibility holder, per-image provenance and rights class, disclosure measurement) on the rung-3 precedent — and say which in §11.1 rather than exempting the row.

### F-22 · Three stores of personal data sit outside the deletion design
**Where:** §2.6, §8.6, §6.11, §12.6. **Found by:** security reviewer. **Confidence: HIGH.**

The deletion design is genuinely good where it reaches — keyed hashes, split provenance snapshots, an index that reaches inside archived packs, a Phase-1 acceptance test on a real packed pack. It does not reach three places:
1. **The exemplar corpus** (§6.11) — per-theme, per-language, "versioned with the theme," permanent, consisting of **other people's real posts** (§14.2 refers to "near-identical templates recur across different **named authors**"). No retention window, no canonical key, no hash treatment, no index entry.
2. **Backups** — §8.6's model is "a file that ships next to the run and is **backed up by copying it**," with no statement that expiry or targeted deletion reaches the copies.
3. **Uploaded packs** (§12.6) — copies in a third-party workspace, no index entry.

**Failure scenario.** An author whose LinkedIn post is in the English exemplar corpus objects. Re-hashing finds and deletes their signal records and reaches inside archived packs — and their post text remains verbatim in the corpus, still injected as few-shot grounding on every drafting call, and still in every backup. **The system reports the deletion as complete.**

**Fix.** Bring the corpus inside the regime: per-item canonical key and author key on ingestion, an entry in the run-pack → canonical-key index (the corpus is consumed per pack via the fact-usage-trace mechanism already designed), and a stated retention posture. State the backup/restore consequence explicitly — a restore that reinstates deleted records is a re-processing event. Add the upload target to the index.

### F-23 · Pack upload needs a write-capable Notion credential, collapsing the read-only bound
**Where:** §12.6, §10.4, §6.2, §8.9, §11.1. **Found by:** security reviewer. **Confidence: HIGH.**

§6.2 fixes the posture as "internal integration token, **read-only**, scoped to designated fact locations" — and that read-only property is what bounds the blast radius of the single credential §6.2 itself calls larger than any other. §12.6 then designs a config-gated upload that **writes** pack contents into Notion. No write credential is named, scoped or stored: §8.9 does not mention it, the recipient map does not carry it, §10.4a's secrets knob does not distinguish it, and §11.1 has no row for a knowledge-base write — so the resolver, which "never returns unknown," either refuses the feature or is never consulted, and the design does not say which.

**Failure scenario.** With upload enabled, the run-as account holds a token that can write to the workspace hosting the claim ledger and the proof allowlist. A defect or injected instruction reaching a write path — §2.7/§6.6 both treat fetched third-party text as adversarial for good reason — turns the system's own output into brand truth on the next run: **the fact-bootstrapping loop §6.4 asymmetry 2 exists to forbid.**

**Fix.** Require a second, separately stored, write-scoped credential restricted to a dedicated output database containing no fact class. Add a knowledge-base-write row to §11.1 and the resolver. State that fact-location scope and output scope are disjoint by construction. Add the upload target to the recipient map and the deletion index.

### F-24 · The special-category deny-list fails open by omission
**Where:** §2.6, §6.3, §10.6. **Found by:** security reviewer. **Confidence: HIGH.**

Control (a) is "a source- and community-level deny-list, **declared per theme**, applied before collection." Both halves "fail to do not store / delete" — but that is behaviour on a **match**, not on **absence**. §6.3 establishes exactly the needed discipline for F-J ("empty is not the same as unresolved") and §6.5 makes unresolved hard excludes a degrade trigger. The deny-list has no such rule, is not a blocking fact class, and is absent from readiness. **An unwritten deny-list and a deliberately empty one are indistinguishable**, and collection proceeds in both cases against control (b) alone — a lexical check over excerpts *after* retrieval and *after* they reached the ranking prompt.

**Fix.** Make the deny-list a resolved-state fact with F-J semantics — resolved-empty is legitimate, unresolved is blocking — add it to theme-readiness, and state that the source-level half is *pre*-collection so its absence cannot be compensated by the post-collection half.

### F-25 · The Prohibited-Outcome Gate's fail-closed rule is fail-open for the class its semantic pass exists to catch
**Where:** `02_legal_claim_packs.md` §2.2, §2.5; `00_MASTERPLAN.md` A1; `ARCHITECTURE_PLAN.md` §14.0 rule 1. **Found by:** security reviewer. **Confidence: HIGH.**

§2.2 concedes the dictionary pass provably cannot catch paraphrase — that is *why* the semantic pass exists. §2.5 then says that on semantic-pass failure "the Gate degrades to deterministic-only verdicts and treats anything **ambiguous** as a match." But the Gate has only two states, clear and matched, and a dictionary pass produces no "ambiguous" verdict — **there is no producer for the state the safety rule acts on.** Contrast N-10, which is coherent because deterministic *extraction* yields claim-shaped candidates blocked wholesale. Separately, §2.5 requires **drop** on regenerate exhaustion while §14.0 rule 1 sends an artifact with no downgrade variant into the pack "labelled with the gate it could not clear," where §4.9 lets the operator "promote it by hand." The masterplan registers this as an open exception with two candidate fixes that have **opposite outcomes**, and picks neither.

**Fix.** Give the Gate a deterministic **extraction** stage separate from its verdict, so "deterministic-only" means *block every condition-adjacent span* rather than "clear unless the dictionary hits." Resolve the §14.0 exception in one direction: the Gate gets its own allowance outside the claim-retry budget, and its terminal is drop with **no promote-by-hand path**.

### F-26 · The combined repair ceiling excludes the QA-rejection cap it names as needing unification
**Where:** §14.0. **Found by:** prompt/eval reviewer. **Confidence: HIGH.**

§14.0 opens by naming four repair-causing gates needing one outer bound — voice cap, per-pack claim allowance, spin ladder, and "(added at §4.9) a QA-rejection cap" — warning that without a single bound the per-artifact worst case is "unstated and unbounded in practice." The next paragraph defines the ceiling's actual enumeration as "spin regenerate, claim pass 1 regenerate, voice regenerate, claim pass 2 regenerate, and any re-entry those trigger" — **dropping QA-rejection entirely.** The post-assembly overlay claim pass and the asset QA rubric both route to the QA-flag path, which is nowhere stated to draw down the combined ceiling.

**Related:** exhaustion mid re-entry labels the artifact with "the gate it could not clear" — whichever was running when the ceiling hit zero. If exhaustion lands during the voice leg of a claim-2 re-entry, the artifact ships labelled "did not pass voice gate" while **claim pass 2 never re-ran on the final bytes.** A solo operator using batch approval sees a voice label, not a claims-unverified one.

**Fix.** Add QA-rejection regenerates and overlay-pass repairs to the enumerated list, or argue the exemption (none is currently argued). State that exhaustion after a claim-2 rewrite but before claim pass 2 re-runs forces the claim-free downgrade variant or a distinct "claim status not finally verified" label, regardless of which counter tripped.

### F-27 · Four precedence rows demand a semantic judgment no node can produce
**Where:** §6.4 (rows F-A, F-C, F-F, F-K, F-N), §1.5 row N-13. **Found by:** AI-pipeline reviewer. **Confidence: HIGH.**

The precedence table's outcomes include "Degrade to the **intersection**" (F-A identity, entities, people), "Degrade to the **narrower** wording" (F-C), "Take the **stricter** policy" (F-F), "Degrade to the **safer** rule" (F-K), "Take the **stricter**" (F-N). N-13 — the only node comparing site text to a Notion statement — has bounded output "**Contradiction verdict for that one fact class**", a binary. Nothing computes which of two capability wordings is narrower or which policy is stricter, and "intersection" is a set operation applied to scalar facts (a legal entity name, a spokesperson's role) where it has no meaning. The implementer's likely resolution — treat any contradiction as a red flag — silently converts routine wording drift into pack-blocking stops.

**Failure scenario.** Notion: "automates lead research and drafts first-touch messages." Site: "helps you draft first-touch messages." N-13 returns contradiction. With no mechanism to select the narrower wording, the resolver either red-flags (blocking every asset depending on F-C in both languages when nothing is wrong) or applies precedence and takes Notion — **the broader claim**, i.e. the autonomy-inflation overclaim §6.3 names as the highest-frequency failure in this category.

**Fix.** Replace semantic verbs with mechanical ones. For F-C make the *does-not* list authoritative and define "narrower" as the union of both sources' does-not lists intersected with the Notion capability set. For F-F/F-K/F-N require policies declared as an **ordered enum** so "stricter" is a comparison. For F-A replace "intersection" with a per-field rule: present in both and equal → resolved; present in both and unequal → red flag; present in one → resolved from that one, flagged uncorroborated.

### F-28 · CTA liveness is "site wins absolutely" but is only checked on a configured URL subset
**Where:** §6.4 (F-E row), §6.6, §6.5. **Found by:** AI-pipeline reviewer. **Confidence: HIGH.**

§6.4: "**Site wins absolutely** — A 404 kills that CTA whatever Notion says." §6.6 bounds verification to "liveness, price values, trial terms and offer status, **on a configured URL set**." Any CTA destination outside that set is never fetched, so under asymmetry 3 an unchecked URL is *not observed* and **the CTA survives**. F-E is "allowed CTA classes per offer × destination × language" — across two brands, two domains, seven destinations and two languages that is combinatorial, and nothing asserts the verification set covers it. Separately, none of §6.5's five degrade conditions is "the CTA set resolved to zero usable entries," and S-6's bar is "**at most one** CTA" — so zero CTAs passes the spin gate.

**Failure scenario.** Czech product pages move during a bilingual site build-out. The verification set holds the English canonical URLs, which still resolve. Every Czech CTA destination 404s and none is in the set. Band computes FULL. A complete Czech pack generates, every asset passes S-6 with a stale link or no CTA, and the operator publishes assets pointing at dead pages.

**Fix.** Derive the liveness URL set **from F-E** rather than configuring it independently, with the per-run fetch budget spent in rotating, freshness-window-driven order. A CTA whose URL has not been observed inside its freshness window is **unusable**, not assumed-live — this is the one place "not observed" must block, because the fact is binary and the failure is public. Add a sixth degrade condition: zero usable CTA entries for the language being generated degrades to research-only.

### F-29 · The P-12 source-to-query-surface map omits four roster entries, including the one source that is nothing but a query surface
**Where:** `05_query_steering.md` §2.1–§2.3, §6.4 vs `ARCHITECTURE_PLAN.md` §2.3. **Found by:** AI-pipeline reviewer. **Confidence: HIGH.**

Checked row by row, the annex's tables omit **free alert services, TikTok Creative Center, LinkedIn organic, and the curated inbox as a class.** The first is sharpest: §2.3 describes it as "**keyword alerts in both languages**" — a source that is *nothing but* a query surface, whose queries are configured out-of-band in a third-party console and therefore drift from the theme's topic object with no detection mechanism. §6.4 then asserts "Every source carries a collection mode," which four rows cannot satisfy. Related: §5.3 scopes the topic filter to discovery-mode items and **no mode is assigned to human-asserted curated-inbox items** — if discovery, the lexical filter drops the operator's hand-written note; if steered, it bypasses relevance checking entirely.

**Fix.** Assign every roster row a collection mode, and add a fifth mode the annex lacks: **externally-steered** — the query lives in a third-party console, not on our wire. For that mode the profile records the literal configured query strings and their last-verified date; readiness asserts they are a superset of the theme's surface forms; a mismatch is a named readiness failure. State that human-asserted items are exempt from the §5.3 filter and carry the operator's own relevance assertion.

### F-30 · The ranking-stage call ceiling drops candidates in arrival order, and contradicts N-1's own rule
**Where:** §5.4a vs §1.5 row N-1. **Found by:** AI-pipeline reviewer **and** cost reviewer. **Confidence: HIGH.**

§5.4a's trip behaviour: "the stage completes on what it has… **unranked candidates are dropped with a reason**." §1.5 says of N-1 that when it cannot run "**Candidate fails closed to monitor-only; never defaults open**." A budget trip mid-ranking *is* "the node cannot run" — and the two prescribe different outcomes. Worse, **nothing defines the order in which candidates reach N-1**, so which survive a trip is determined by collection sequence — source roster order and feed pagination.

**Failure scenario.** A heavy news day. Volume up 3×, the ceiling trips at candidate 180 of 340. The dropped tail is whatever the roster collected late — plausibly the Czech-locale feeds and weekly instruments. **The busiest signal day of the month is the day with the least complete ranking**, and the digest reports a budget cap while the *selection* of what was lost is arbitrary and invisible.

**Fix.** Reconcile in favour of §1.5: unjudged candidates go to **monitor-only** with reason `ranking budget exhausted`, carried into the next run's pool, never dropped. Add a mandatory deterministic pre-rank before N-1 (evidence class, source priority, corroborating family count, age) so a trip loses the tail of a **defensible ordering** rather than of a fetch sequence.

### F-31 · Corroboration is counted twice, and portfolio reachability does no ordering work
**Where:** §2.7, §2.8a knob roster. **Found by:** AI-pipeline reviewer. **Confidence: MEDIUM-HIGH.**

Confidence "records how many source families corroborated the candidate **and** how much of the portfolio was reachable this run" — while the knob roster separately carries a **corroboration bonus magnitude**. In a product these compound: a four-family candidate gets corroboration counted roughly squared. Separately, portfolio reachability is a **run-level constant** multiplying every candidate identically, so it does no ordering work at all — yet the composite it deflates is compared against an **absolute** monitor-only band boundary.

**Failure scenario.** Bluesky returns a stale payload (correctly suppressed) and the Virlo recheck lapses (degraded). Two of seven families unreachable. Every composite scales down identically, the whole slate lands below the monitor-only boundary, and the run produces zero generate-verdicts — with §2.7's rule "zero passing candidates is correct behaviour" **laundering a two-source outage into a normal quiet night.**

**Fix.** Keep corroboration as a per-candidate term and delete either it or the bonus (say which, so no implementer applies the survivor twice). Move portfolio reachability out of the composite into a run-level digest annotation and a named precondition on the band comparison: below threshold, suspend the comparison and label the run *slate not comparable — portfolio degraded*.

### F-32 · Band thresholds are single-valued across two composites the plan declares non-comparable
**Where:** §2.7 + §2.8a knob roster; `03` §1.6. **Found by:** AI-pipeline reviewer. **Confidence: HIGH.**

§2.7 states the English and Czech composites "have different factor counts — **the two numbers are not comparable and the digest says so beside them**." The knob roster then carries "the monitor-only band boundary" and "absolute-band fallback thresholds" with **no per-language qualifier**, while "top-N cap per language" is explicitly scoped. A three-factor product of values in [0,1] is systematically **larger** than a four-factor one, so a single boundary is systematically lenient toward Czech. `03` §1.6 identifies precisely this reasoning and applies the fix **per lane only**, leaving the identical defect between the two existing per-language composites untouched.

**Fix.** Scope both thresholds to the **comparison class** — (language × trigger class) — exactly as `03` §1.5 already defines that key, and add the readiness assertion that fails when two comparison classes share one boundary value.

### F-33 · Recurring cost is understated by roughly 4–5×
**Where:** `STAGE5_APPROVAL_SUMMARY.md` line 12; §5.4, §4.4, §5.1, §5.2, §16.3. **Found by:** cost reviewer. **Confidence: HIGH.**

$60–65/mo is Virlo ($49) + DataForSEO ($10–15). Outside it:
- **Licensed music** — §4.4: "Music must be licensed — a library subscription or a paid-plan AI music generator," and the router's music route is forbidden for published assets. A **mandatory recurring subscription for the headline asset class**, appearing in no cost table, no vendor roster, no decision row and no risk row — and it is a licence chain on published assets, exactly the class §5.2/§5.6 disciplines everywhere else.
- **TTS** — ElevenLabs commercial use sits on a paid plan floor; Azure Neural fallback is a second account.
- **Publishing bridge** — Postiz from Phase 6, subscription or self-hosting.
- **Both API wallets** — §5.4 already states $90–140/mo of media at the recommended cadence "plus a text line of the same order" = **$180–280/mo of API**, which the summary reduces to "media budget you cap yourself."
- **The weekly availability probe** — a balance call plus one draft-tier generation per route family, every week, forever, never sized, drawing on the $50 trial balance during Phases 3–4.

**Fix.** Replace the $60–65 line with a full steady-state table (vendors, both wallets, music, TTS, bridge, probe) with the Phase-6 delta shown separately. Add music licensing to the vendor roster with a recheck-by date and a rights-class treatment.

### F-34 · Roughly eight of nineteen load-bearing volatile facts expire before the phase that consumes them
**Where:** §0.3 table and standing rule; §5.2, §2.2, §17. **Found by:** cost reviewer. **Confidence: HIGH.**

Today is 2026-08-06 and the build has not started. Phase 0 realistically runs 4–8 weeks solo.

| Fact | Recheck by | Consumed at | Status |
|---|---|---|---|
| #18 EU AI icon standardisation (**marked urgent**) | 2026-09-01 | Phase 3 disclosure floor | **Expired** — overlay spec, wording and Phase-3 criteria all change after they are built |
| #9 Router prices ($0.30/$1.25/$0.04) | 2026-09-06 | Phases 3–4, OD-8 cap sizing | **Expired** — every cost figure, the $50 arithmetic, the cap recommendation |
| #1 AI Act Art. 50 in force | 2026-10-01 | Phase 3 | Expired |
| #8 Silent model substitution / forced 16:9 | 2026-10-06 | Phases 3–4 | Expired |
| #3, #4 Bridge draft-without-schedule; no AI-label fields | 2026-10-01 | **Phase 6** | Expired by months — and both are already unverified paper claims |
| #2 Platforms strip C2PA | 2026-11-01 | Phase 3 | Borderline |
| #6, #7 14-day deletion; no idempotency | 2026-11-06 | Phase 3 | Borderline |

The structural defect is worse than the rows. §0.3 declares "a lapsed recheck-by date is an operational event, not a documentation chore" — then §5.2 and §2.2 implement that discipline for **model registry routes and vendor roster entries only**. §0.3's own nineteen facts have a recheck-by column, **no owner, no store, no probe and no consequence.** A lapsed §0.3 fact does literally nothing. The plan's most load-bearing evidence is the only evidence with no enforcement attached.

**Fix.** Give §0.3's table the machinery the registries have: a stored ledger with owner, recheck-by and status; a Phase-0 deliverable re-verifying every fact whose date falls inside the projected build window; and a phase-entry precondition — **no phase may start while a fact its acceptance criteria depend on is lapsed.** Fact #18 needs re-checking now; fact #9 needs re-pulling immediately before OD-8's caps are set.

### F-35 · "A theme that fails readiness may never be scheduled" is assigned to no component
**Where:** §13.2, §10.6, §9.2, §11.3, §8.1, §1.2, §8.8. **Found by:** architecture reviewer. **Confidence: HIGH.**

§13.2 says readiness is "a validation pass… which the scheduler refuses to bypass" — but §8.1 defines the scheduler as Windows Task Scheduler, "nothing more than something that starts the process." It cannot know a theme's readiness state. No §1.2 component owns the check; the theme loader's refusal is scoped by §11.3 to secrets "and nothing more." §9.2's unattended flow has no readiness step, §11.3's triggers do not include an unready theme, §8.8 has no exit class for one, and §8.6 has no readiness ledger, so nothing persists a verdict.

**Failure scenario.** A theme is built interactively in test mode (the documented workflow), the operator enables both cadence knobs before readiness ever passes, and the first unattended run proceeds — because nothing asks. §13.2's own list goes unchecked at 3 a.m.: a language with an empty candidate set, a destination with no format profile, an allowlisted channel that is not connected. This is precisely "a half-configured tenant producing confident nonsense at three in the morning."

**Fix.** Name the owner (run controller, at theme load, immediately after the secrets check). Add a readiness-state record to §8.6 carrying the verdict, the config hash it was computed against, and its date. Add "theme not ready, or readiness stale against the current config hash" as a sixth fail-closed trigger routing to `policy-stop`. Add a Phase-5 acceptance criterion. State readiness's own cost posture in §11.1 — it makes live knowledge-base, site and ranking calls.

### F-36 · Tier-1 monotonicity is asserted, not enforceable — and the plan already has five unenforced floor knobs
**Where:** `00_MASTERPLAN.md` §3.1, acceptance criterion C; §10.4 rows for AI-content class, disclosure overlay, QA rubric thresholds, keyframe policy, token ceiling; §13.2, §11.2. **Found by:** architecture reviewer. **Confidence: HIGH.**

The entire safety argument for the playbook layer is "Tier 1 — engine floor. Strictly monotonic; a playbook may only tighten." The architecture plan **already** has five theme-level knobs with that property — each phrased "at or above the engine floor" — and **no component owns the comparison.** §11.2's resolver answers mode questions, not floor questions. §13.2's readiness assertions include nothing about floor comparison. Only hard excludes have a real mechanism. So the pattern the playbook layer inherits is unenforced today, and acceptance criterion C demands exactly what does not exist: *"state where the playbook layer is prevented from reaching it. An assertion that a playbook 'cannot' is insufficient."* No wave is charged with producing that mechanism — V1 is charged with *reviewing* whether it exists, which presupposes someone wrote it.

**Fix.** Add to §13.2: "every theme-level and playbook-level value on a floor-bearing knob is at or above its engine floor, evaluated by a named floor-comparison pass over the resolved configuration, with the floor's own value recorded in the readiness record." Assign that pass an owner in §1.2, add it to T6's charge, and change V1's charge to "verify the named mechanism."

### F-37 · Resolution is not total for the highest-traffic authoring field
**Where:** `06B_resolver.md` §5.4, CFG-OD-5; `CONDUCTOR_RULINGS.md` CR-3. **Found by:** config reviewer. **Confidence: HIGH.**

CR-3 states the brand brief reaches N-3/N-5/N-6 via five injection points, each of which `03` §4.2 independently defines as a **bounded, non-free-text slot**. 06B admits none of those definitions "describes a place where a paragraph of open guidance naturally lands," and that its own working answer is "used throughout this design" while simultaneously flagged as unconfirmed and deferred. For the one Tier-A field practically guaranteed to be filled on every theme, **the mapping from authoring form to resolved form is undefined in the governing spec.** Two implementers could split the same brief differently, producing different overlays, different fingerprints, different regression-gate outcomes and different content from byte-identical input.

**Fix.** Treat CFG-OD-5 as a Wave-0 blocker, not a Wave-2 nicety. The composition rule must be settled by the §4.2 owner and stated as a normative per-IP allocation before any resolver totality claim can be verified.

### F-38 · Pending paid media has no watchdog, and the runtime host requirement is unstated
**Where:** §4.7, §8.13, §9.1, §8.12, §8.1, §8.4. **Found by:** cron/state reviewer **and** cost reviewer. **Confidence: HIGH.**

The 14-day deletion clock is defended by a countdown printed in the digest **at the moment the run ends** — when it reads 14, i.e. when it is least alarming. There is no daemon (§9.1 says so), and §8.12's escalation only escalates **across runs**; with cadence off there are no further runs. Meanwhile §8.1 pins the run-as account to the operator's own (per-user secret encryption), so the runtime is **a workstation that must be powered on and logged in** — a dependency that appears in no risk row.

**Failure scenario.** Interactive Friday session, six pending clips, operator takes two weeks' leave, both cadence knobs at their default (off). No process runs. No notification fires. Day 14 the provider deletes six paid artifacts and the run ledger still says `completed-with-pending-media` — **the healthy class.**

**Fix.** Make the drain schedulable independently of pack cadence (this also fixes F-4), or add a hard readiness rule that media spend is not permitted unless a drain cadence is enabled. Write the nearest deletion deadline into the filesystem status flag. Escalate on approach, not at emission. Add a machine-availability risk row and state the uptime requirement in §8.1. Add one non-email alarm rung as **mandatory** for money-losing events.

### F-39 · Phase 3's gate depends on Phase 5 machinery and contradicts its own acceptance criterion
**Where:** §17 Phase 3, Phase 4, Phase 5; §8.13. **Found by:** cron/state reviewer. **Confidence: HIGH.**

Two defects in one gate. **(a)** The acceptance text requires that "any job in the ambiguous window is left in the named submitted-unknown state with no automatic action" — and §8.13 terminates such a row at `paid-lost`, i.e. money lost. **A test that genuinely exercises the ambiguous window cannot satisfy "no money was lost"; a test that satisfies it did not exercise the window.** **(b)** "Restarting resolves every in-flight job by querying task status" *is* phase-0 adoption plus the expiry-ordered drain — which §17 lists as **Phase 5** deliverables, while Phase 4 buys eight to ten real paid packs before Phase 5 exists.

**Fix.** Move phase-0 adoption and the drain into Phase 3's deliverables (they are inseparable from the media-job ledger). Restate the gate in demonstrable terms: every ledger row terminal or explicitly `submitted-unknown` with sub-case recorded; zero duplicate provider task ids for one (identity, attempt); balance delta within tolerance; count of `paid-lost` rows **reported**, not required to be zero.

### F-40 · The write-ahead ledger cannot distinguish "never sent" from "sent, outcome unknown"
**Where:** §8.5 sub-case A, §8.13. **Found by:** cron/state reviewer. **Confidence: HIGH.**

Exactly one row is committed before the submission call, so the ledger's most granular fact is "we intended to submit." Sub-case A therefore covers two physically different events — the process died before the socket was written (**money provably did not move**) and the process died after the request was accepted (money moved). Both are forbidden from auto-resubmission, both accrue full expected cost, and both terminate at `paid-lost`. The plan says expected cost "is reversed when it resolves to a confirmed non-charge" but names **no instrument that can confirm a non-charge** — it simultaneously states there is no task-listing and no task-search endpoint.

**Fix.** Two markers, not one: `intent-committed` (durably written, nothing sent) and `wire-attempted` (fsynced immediately before the socket write, cleared only by a recorded response). Only `wire-attempted` rows are `submitted-unknown`; `intent-committed` rows are provably non-spent, contribute zero to the expected side, and are re-submittable under the same (identity, attempt) with no operator action.

### F-41 · `expired` is a media-job state with no disposition, no exit class and no place in the spend arithmetic
**Where:** §8.13, §5.5. **Found by:** cron/state reviewer. **Confidence: HIGH.**

`failed` has a disposition; `submitted-unknown` has a five-point terminal design. `expired` has neither — nothing states how it is detected, what the slot degrades to, whether its expected cost stays on the expected side, whether it counts against the refusal ladder or the QA cap, or which exit class a run carrying one emits. **It is the state for the exact outcome the whole re-hosting design exists to prevent, and it is the only state named but not designed.**

**Fix.** Give it the same treatment as `submitted-unknown`: detection rule, slot disposition (plan-only with reason), cost treatment (expected cost stays — money moved, artifact lost), digest line, one operator-authorised fresh attempt under a new identity. Add "does task-status re-issue a result URL after the original expires?" to the Phase-0 router checklist beside the model-identity question.

### F-42 · The weekly availability probe spends real money outside every run, lock, ledger and phase
**Where:** §5.2 behaviour 3, §5.4, §8.6, §17. **Found by:** cron/state reviewer. **Confidence: HIGH.**

§5.4 identifies concurrent spend against one balance as the thing that breaks balance-delta reconciliation, and closes it with a global lock scoped to "any spend-bearing media stage **of a theme run**." The probe is not a theme run and has no stage; it submits real paid generations with no run-lock interaction, no spend-ledger identity, no exit class, and no phase.

**Failure scenario.** The probe fires at 03:00 mid-media-stage. Observed balance movement exceeds the run's ledger total, the unexplained-spend circuit breaker halts submissions mid-pack, and the run exits with a divergence alarm on a night when nothing was wrong. The symmetric failure is worse: **the operator learns to attribute divergence to the probe and stops trusting the breaker.**

**Fix.** Give the probe a spend-ledger identity and rows, require the same global lock, exclude its rows from reconciliation **by attribution rather than tolerance**, cap it explicitly, and place it in a phase (it cannot predate Phase 3's ledger or Phase 5's scheduler).

### F-43 · Windows task settings that decide whether the run happens are unspecified, and the defaults produce no run
**Where:** §8.1, §8.4, §8.9, §17 Phase 5. **Found by:** cron/state reviewer. **Confidence: HIGH.**

§8.1 pins the run-as account and treats the rest of the scheduler as "something that starts the process." But on Windows the settings that decide whether an overnight task fires are defaults the plan never names: **Start the task only if the computer is on AC power** (on by default — a laptop on battery silently skips), **Wake the computer to run this task** (off by default — a sleeping machine never fires), **Start only if the following network connection is available**, **Stop the task if it runs longer than 3 days**, and the logon type — "Run whether user is logged on or not" with "Do not store password" (S4U) yields a token that **cannot decrypt user-scoped DPAPI data**, precisely the §8.9 hardening.

**Failure scenario.** The machine sleeps at 01:00. The 03:00 trigger never fires and **no missed-window is recorded**, because missed-run accounting only runs when the pipeline runs. No flag, no email, no drain — and the operator's evidence for "did today's run happen" is *absence*, indistinguishable from "the scheduler was never configured." Phase 5's acceptance passes on an awake, plugged-in desktop and proves none of this.

**Fix.** Ship a pinned exported task definition as a Phase-5 deliverable with every setting stated and justified, including a logon type consistent with the chosen secrets mechanism. Add an out-of-process staleness detector that does not depend on the pipeline having run: the flag file carries a next-expected-run timestamp, and any invocation reports "last successful run older than cadence × 2."

### F-44 · Run packs grow without bound while disk-full is a designed hard failure
**Where:** §2.6 retention table, §8.10, §8.13, §15 R-31/R-40, §10.4a. **Found by:** cost reviewer. **Confidence: HIGH.**

§2.6 sets retention on every research artifact and **none on the run packs themselves**, while §8.13 makes re-hosting every generated video and image mandatory and permanent. The pack store grows monotonically — at three runs a week with two to four masters plus derivatives, a permanently accumulating video archive on a workstation disk. Meanwhile R-31 makes disk-full a **hard-failure class** and R-40 spends real design effort on the disk-full-versus-drain collision, treating it as an anomaly. **Under monotonic growth it is not an anomaly; it is a certainty with an arrival date nobody has computed.** There is also no backup obligation for the ledger set — §8.6 says "backed up by copying it," an instruction with no owner, no cadence and no place in any recurring-task list, guarding the spend ledger, the review-decision store and the deletion index.

**Fix.** Add a pack retention and archival policy: media bodies expire or move to cold storage on a stated clock, with the canonical-key index and de-identified provenance retained. Size the disk requirement per month of operation and put the number in §10.4a next to the threshold. Make the ledger backup a named recurring task with a cadence, and add it to the operator burden accounting.

### F-45 · Two ops-rot clocks have no working detector
**Where:** §5.2 (registry `known sunset date`), §2.3 (Meta row), R-05, §17 Phase 0, §11.3. **Found by:** cron/state reviewer **and** security reviewer. **Confidence: HIGH.**

**(a)** `known sunset date` is recorded twice in the document and **consumed nowhere** — no rule stops a route being selected for spend on or after it, even though a named video model's API removal on 2026-09-24 is the plan's standing proof that pinning rots. The only backstop is the weekly probe (up to seven days late) or a live mid-pack failure. **(b)** R-05's mitigation is "a dated 'this credential expires in N days' line in the digest" — computed from a date **a human typed at Phase 0**. There is no knob for it in §10.4/§10.4a, no ledger row in §8.6, and §11.3 explicitly scopes theme-load secret checking to "presence-and-syntax… nothing more." So the 60-day Meta token's designed *proactive* alarm has no input and degrades to the reactive path — the silent axis loss R-05 exists to prevent. (The Notion path *is* genuinely covered by the run-start health call.)

**Fix.** Give `known sunset date` the two-stage behaviour recheck-by already has — warn inside a horizon, **hard-refuse selection** on and after the date, name it in the digest. Derive credential expiry from the provider where exposed, alarm on the derived value, and make "every credential re-verified and its expiry recorded" an **entry condition for Phase 5**, not a Phase-0 one-shot.

### F-46 · The depiction attestation's inputs are authored by the party it checks
**Where:** `02_legal_claim_packs.md` §3.2–§3.5; §5.6, §12.1, §3.5. **Found by:** security reviewer. **Confidence: HIGH.**

C-12 delegates the entire substantive visual comparison to the human attestation, so the attestation carries the whole control. Three of its four inputs are not independent: the F-W reference and its accuracy attestation are **tenant-supplied**; "which claim dimensions the reference actually grounds" is a semantic judgement no v1 component can make, so it too is tenant-authored; and "**the generation mode actually used**" rests on the field §5.6 corrects at length — delivered identity is best-effort, substitution is *silent*, and the common case is `assumed-as-requested`, "explicitly flagged as an assumption rather than an observation." Meanwhile the reviewer economics are "a glance at two images side by side" against a table budgeting ~1 minute for a feed still, inside a digest that **pre-selects high-band topics** and makes batch approval the default.

**Failure scenario.** The router silently substitutes a model that ignores the reference. No divergence signature is observable, so the record reads `assumed-as-requested` and the review pack displays "reference-grounded." The reviewer glances at two images, one of which was in fact generated from a text prompt, and attests they match. **Class 12 returns VERIFIED because a link exists.**

**Fix.** Treat `assumed-as-requested` as **not** reference-grounded for depiction purposes — an asset whose grounding cannot be observed degrades to plan-only, the disposition an unresolvable rights class already gets. Require the grounded-dimensions statement to be per-reference-asset and dated at supply time, with the tenant surfaced as its author in the review pack. **Exclude depiction-attestation assets from pre-selected and batch approval outright.**

### F-47 · Tier-2 relaxation targets a bar that bundles style with claim-safety
**Where:** `00_MASTERPLAN.md` §3.1; §14.4 dimension 2, §6.7 class 4; `03` S-10. **Found by:** prompt/eval reviewer. **Confidence: MEDIUM (absence-based).**

§3.1's own example of the relaxation surface is dimension 2 — "Specificity and proof anchoring — concrete, attributable, ledger-backed; vagueness dressed as insight is the fail" — relaxable for evocative-expressive genres. **That single bar covers both a style property and a claim-safety-adjacent property.** The only independent shape-level backstop against vague-but-claim-shaped language, S-10, is scoped to "visual-first and ambient relations" only; text-only expressive assets have no equivalent, and claim-gate class 4 (outcome/result) is not among the five non-disableable classes.

**Fix.** Split dimension 2 into a genre-variable **style** bar and a Tier-1 monotonic **ledger-backed proof anchoring** bar, or extend an S-10-style shape check to text-only expressive relations.

### F-48 · Frozen eval set purity is discipline-only, with no mechanism and no separation of duties
**Where:** §14.8, contrasted with §6.11 class-11. **Found by:** prompt/eval reviewer **and** cost reviewer. **Confidence: HIGH.**

§14.8 states the eval set is "never used for prompt-tuning inspiration — only for measuring," with no access control, blinding, custody separation or automated leakage signal. The plan explicitly rejects self-assessment as a control everywhere else ("a component's self-assessment is not a control over that component," motivating check class 11's automated corpus-leakage detection) but leaves this parallel risk to the prompt author's memory — and **one solo operator is simultaneously prompt author, golden-set curator and weekly-loop reviewer.** This is the artefact that certifies every change to the system's most safety-relevant prompts.

**Fix.** Add at least one detection signal independent of memory: flag when pass-rate improvement on the frozen set exceeds gains on a rotating held-out sample never shown at review time, or keep a logged access record the pre-rollout gate checks. Record a checksum at Phase 0, re-verified at each pre-rollout comparison, so tampering is at least visible.

### F-49 · S-3 is stated twice, in two different words, describing two different tests
**Where:** §0.2 (the single-owner claim), §6.10 S-3, §14.1. **Found by:** architecture reviewer. **Confidence: HIGH.**

§0.2 names the spin criteria **first** when asserting "Nothing is restated in two places with two sets of words." §6.10's S-3 is a **presence** test ("an explicit, checkable bridge from topic → consequence → why the offer is relevant"). §14.1, after declaring "They are not restated here," restates it as a **two-way deletion** test ("deleting the offer-mention paragraph still leaves a genuine point, and deleting everything else still leaves something specific to *this* topic"). These are not the same check — an asset with a bridge sentence passes §6.10's and can fail §14.1's — and the second limb duplicates S-1 while the "survives deletion" framing duplicates S-7. Both sections additionally restate the identical enforcement ladder in full.

This matters now because Amendment B's T5 builds the criterion registry keyed on S-1…S-7 and is charged with naming "S-7's complement for bridgeless assets."

**Fix.** Delete §14.1's paraphrase, replacing it with a pointer. If the deletion test is genuinely intended, move it into §6.10's S-3 row as the stated operational test and remove the overlap with S-1 and S-7. **Do this before T5 dispatches.**

### F-50 · The per-genre Czech calibration corpus is costed against a decision that was deleted
**Where:** `00_MASTERPLAN.md` §8, §9; §17 Phase 0. **Found by:** architecture reviewer. **Confidence: HIGH.**

§8 accepts a real cost — each calibrated Czech genre needs its own structural corpus — and assigns it to **`PB-OD-3`**, which appears nowhere in §9's table. It was one of the three demoted pseudo-decisions, so **the cost is attached to a decision that no longer exists.** Independently, §17 Phase 0's four calibration deliverables are all genre-agnostic; **no phase delivers a per-genre corpus or golden set**, and no wave adds one.

**Failure scenario.** Playbook #2 is built. Its genre variant is registered with its flag-rate ceiling "recorded inactive until its golden set exists" — and the golden set is nobody's deliverable in any phase. It never exists, the ceiling stays inactive permanently, and §3.1's "safety comes from calibration and provenance" argument **has no calibration half**. Tier 2 becomes a pure relaxation surface with no control on it.

**Fix.** Repoint §8's sentence to a live decision (PB-OD-7 is the natural home) or raise a new `PB-OD-n`. Add per-genre Czech structural corpus and per-genre golden set as a named deliverable in Phase 0 or a new pre-Phase-8 gate, with the same do-not-start rule the four existing artefacts carry.

### F-51 · Migration is silent on ~100 Tier-B scalar knobs
**Where:** `06E_readiness_and_defaults.md` §6.2, Movements 2–3. **Found by:** config reviewer. **Confidence: MEDIUM-HIGH.**

Movement 2 handles only the ~30 "no engine default" cells. Movement 3 states two treatments: free-text Tier-A fields are authored fresh, literal arrays are carried across verbatim. **Neither addresses the much larger category** — Tier-B *scalar* knobs that already had a stated default in §10 (budget caps, thresholds, windows, cadences) and that theme #1 may hold at a non-default value. There is no rule for whether these are transcribed, re-derived, or left to inherit a possibly-different new default.

**Fix.** State in Movement 3 that all Tier-B scalar/pointer knobs are carried across **verbatim by default**, same discipline as the literal arrays, with the equality check extended to cover them — rather than leaving the middle category to be caught only by a post-hoc differential.

### F-52 · Emptiability has two writers across the two amendments, one declared its sole owner
**Where:** `00_MASTERPLAN.md` A3, T6, T3, §10. **Found by:** architecture reviewer. **Confidence: HIGH.**

A3 (Amendment A) writes "F-B/F-C/F-E legitimate emptiability with C-4's external-verifier substitution floor." T6 (Amendment B Wave 1) writes "the merged emptiability/substitution rule **(sole owner)**," and T3 is told the rule belongs to T6. A4 will already have merged A3's version into §6.3/§6.5 before T6 exists, and nothing instructs T6 to adopt A3's wording verbatim. The Wave-1 barrier ("no file contradicts 04_RECONCILIATION") does not test against §6.3, because §6.3 is not a Wave-1 file.

**Fix.** Either strike A3 and hold the emptiability fix for T6 (accepting that P-1 waits), or strike T6's sole ownership and reduce its charge to "cite §6.3's rule, do not restate it." Add to the Wave-1 barrier an explicit check that no Wave-1 file restates a rule Amendment A already merged.

### F-53 · Extensibility falsification runs in the last phase, and replacing the fixture invalidates its criteria
**Where:** §17.1, §17 Phase 8, §17.3; `00_MASTERPLAN.md` criterion E, §6 Wave 1.5, Wave 2. **Found by:** architecture reviewer. **Confidence: HIGH.**

The masterplan states the principle itself: *"a falsification test positioned where failing it is maximally expensive, so a conductor facing the cost accepts findings as minors."* It applies that principle to its own waves (moving V1/V2 to Wave 1.5) and **never to §17** — where Phase 8's multi-theme proof sits behind four weeks of packs and a full calibration cycle. Separately, Phase 8's criteria are written against the *specific* §13.3 fixture ("a real pack **in its single language**… **no generative video and no counted-evidence source anywhere**"), while criterion E replaces those fixtures and Wave 2 reworks §13.3/§13.4 — **but no task touches §17**, so Phase 8 will test the deleted fixture's properties.

**Fix.** Add §17 Phase 8 to Wave 2's rework list. Split the proof: move a paper-only readiness-and-config walkthrough of the second fixture to a gate on **Phase 2** (the config surface is complete by then and failure is cheap), leaving the paid end-to-end run at Phase 8. Restate Phase 8's criteria in fixture-agnostic terms plus a per-fixture annex.

---

## 3. 🟡 MINOR findings

- **F-54 · §6.5 says "four fail-closed triggers"; §11.3 says five.** *(Conductor-verified: line 1265 vs line 2011.)* Phase 2's gate correctly says "the fifth." A tester working from §6.5 will conflate the five *degrade conditions* with the *fail-closed triggers* and test neither set completely. **Fix:** correct §6.5 to five.
- **F-55 · §7.6 restates the mode capability matrix in its own words**, though §0.2 places it in §11.1–§11.2, and §7.6's staging description omits the dry-run boundary §11.1 calls the actual distinguisher. **Fix:** reduce §7.6 to a pointer plus its own contribution.
- **F-56 · §14.3 restates §6.7's verdicts and enforcement ladder verbatim, with a divergent number** — §6.7 says "recommended maximum two attempts," §14.3 says "a small fixed maximum," §10.3 says "Small fixed number." **Fix:** §6.7 is the only place any regenerate number appears.
- **F-57 · §6.5's "zero was spent" is false on the contradiction path.** N-13 is a model node **inside** brand-truth resolution, so on the red-flag path it has already burned text budget before the degrade is computed. **Fix:** replace the flat statement with two figures — media spend (zero, guaranteed by ordering) and text spend to the point of degrade, itemised. Add N-13's call count to §5.4a's decomposition.
- **F-58 · §15 R-31 still carries the superseded low-disk design**, contradicting §8.10 and R-40 two rows below it in the same table. An implementer building from §15 reintroduces the mid-drain abort W4-07 was raised to remove. **Fix:** rewrite R-31's columns or fold its disk limb into R-40.
- **F-59 · Phase 6 acceptance says "four separate conditions" then names a fifth and arguably a sixth.** **Fix:** enumerate all conditions explicitly and state which are tested.
- **F-60 · The request log stores "normalised parameters" for twelve months with no stated credential-stripping rule.** §8.9's redaction rule covers logging paths; the research artifact store is a data store. Several portfolio sources carry keys in query strings. **Fix:** state that parameter normalisation is credential-stripping and that §8.9 binds the research artifact store by name.
- **F-61 · No sunset policy for a playbook version a theme is pinned to.** §4 of 06E is thorough on registry, resolver, CTA, topic and pointer drift, and silent on the playbook itself. A safety-relevant playbook fix would never reach a theme that never edits its authoring form. **Fix:** extend the recheck-by pattern to playbook pins with a stricter grace window.
- **F-62 · "Claim-boundary-adjacent genres start strict" has no stated test or owner** — unlike every other classification in the plan, which is registry-based. **Fix:** define a registry-based adjacency test keyed to default relation types or statement-class share.
- **F-63 · Two Tier-A fields are both keyed to `CFG-PS-09`** (Field 9 CTA-destination liveness, Field 11 relation-content mapping), which are structurally different concepts. Evidence that the twelve-field ceiling is held by ID reuse rather than a real field count. **Fix:** give Field 9 its own ID once CFG-C-2's row lands.
- **F-64 · `PR-11` ("collection mode per source") violates the plan's own placement rule** — its own Default column says "(fact, not choice)," i.e. a connector property identical for every theme. Same category error as the already-open CFG-OD-2, but on a **newly added** knob that the annex's own audit missed. **Fix:** reclassify Tier C and re-scan the other new PR/PS/PO rows for the pattern.
- **F-65 · "Eight new fact classes" over nine (F-O…F-W).** Independently confirmed live in `02_legal_claim_packs.md` §6.3, not merely as an abstract barrier item. **Fix:** correct at source in the same pass.

---

## 4. ⚪ Rejected, downgraded, or corrected in triage

Triage rejected or downgraded seven agent findings. Recording them so they are not re-raised.

| Claim | Disposition |
|---|---|
| "A theme author could set the AI-content class to `assisted` and skip the disclosure" | **REJECTED — false positive.** §3.3 already states: *"The AI-content class is derived by the engine, not configured by a theme,"* and derives realistic-synthetic from **any** generative component including synthetic speech. The agent read an earlier design. |
| "Move the Czech burned-in disclosure to second 3–5 to reduce the perceived-cheapness penalty" | **REJECTED as a fix.** This relaxes an engine floor that §0.3's standing rule protects explicitly (*"no expected or announced postponement may relax the burned-in disclosure control before it is actually in force"*). The **underlying observation is kept** — the disclosure's organic-performance cost is real and quantified nowhere (see IDEA-5). |
| "The English judge runs uncalibrated from Phase 2 to Phase 6" | **DOWNGRADED — stale.** R2-M15 already added the English golden set and English structural pass to Phase 0, and the do-not-start gate covers four artefacts. Residual concern is F-12 (what "calibrated" means), not the sequencing. |
| "STAGE5_APPROVAL_SUMMARY.md never states Amendment A must land first" | **DOWNGRADED to noted.** Literally true, but masterplan task A4 explicitly charges amending that file. It is a pending task, not an unflagged gap. Worth confirming it actually lands. |
| "Exactly eight `06A` rows carry a bare N/A regime" | **COUNT NOT REPRODUCIBLE.** Conductor grep found 17 bare `| N/A |` cells and 6 `N/A-machine`. The **two-tag distinction and the mismatch between the ruling's target set and its cited count are real and serious** — but the arithmetic must be re-derived by hand before acting on F-11's config sibling. Retained as a MAJOR pending recount. |
| "No non-trend origination pathway exists" | **KNOWN — already logged as P-4**, fixed by operator decision PB-3 (collected trend · calendar/occasion · evergreen library). Not a new finding; the marketing reviewer surfaced it independently, which corroborates the defect's severity. |
| "P-2/P-5/P-7 remain unfixed at Stage 5" | **KNOWN AND INTENDED.** These are Amendment B scope by explicit operator decision. The legitimate residual is F-9 (severability) and the product question in IDEA-8. |

---

## 5. 💡 Improvement ideas

Ideas, not defects. Ordered by leverage per unit of effort.

**IDEA-1 · Keyframe-first async approval (S).** Let the operator approve keyframes in the digest without waiting for video rendering; generation proceeds asynchronously and the digest refreshes with completed videos for a follow-up review. Cuts a single-session review from 40–120 min to 10–20 min of keyframe scanning. Lands in §12.1 and §9.2; reuses the async job queue already designed. **This is the single highest-leverage change against F-8.**

**IDEA-2 · A "strategic slot" that bypasses ranking but not the gates (M).** Reserve one media slot per run (or one run in five) for an operator-nominated topic — a launch, a case study, a position piece — that always gets media regardless of trending momentum. It still passes the spin gate, the claim gate and the voice gate. Without this, the company's most important message competes with trending noise for two slots and loses, shipping as plan-only while the news cycle moves on. Interacts with PB-3; worth building even before the playbook layer.

**IDEA-3 · Per-language topic sourcing (M).** Give Czech-specific venues 2–3× weight when generating the Czech ranked list, separately from English. Directly attacks F-14's root cause: today both languages get the same topics because they are sourced the same way. B4's evidence is that Czech professionals have distinct pain signals and distinct trusted sources.

**IDEA-4 · Bulk-rejection carousel in the digest (M).** One page showing all ranked topics with scorecard, band and one-line rationale, with checkboxes to reject in bulk and regenerate. Reduces per-topic page-opening friction, and — unlike batch *approval* — bulk **rejection** is safe, because the failure mode of rejecting too much is a smaller pack, not an unreviewed one.

**IDEA-5 · Measure the disclosure's performance cost instead of arguing about it (S).** The burned-in disclosure is mandatory and non-negotiable — but its organic-performance cost is currently unmeasured and therefore unmanaged. Log first-appearance timestamp, type-height and contrast per asset (already required) **alongside** the operator's outcome notes, so that after twenty assets there is a real number rather than a debate. If the cost is large, that is a **channel-mix** decision, not a compliance one.

**IDEA-6 · Regenerate-by-reference (M).** On rejecting a video for "hook too slow," let the operator attach a reference URL; the regeneration prompt includes it as a pacing/energy exemplar, with side-by-side display. Removes the burden of verbal articulation, which is where most rejection-reason quality is lost.

**IDEA-7 · Cost-sensitivity table at Phase 4 (M).** For each topic show what cost would change if media were removed, tier downgraded, or a language added. Turns "how do I afford 3× output?" from a mystery into a set of concrete options — and would have surfaced F-7 and F-33 on its own.

**IDEA-8 · Reconsider building the playbook layer before the first published post.** Amendment B generalises to other verticals before theme #1 has produced a single published asset. The counterfactual worth pricing: **Amendment A now (safety, small), Amendment B after Phase 4**, when there is real production data about what the ontology actually constrains. The masterplan's own PB-OD-7 already concedes that without a real second tenant, playbook #2 becomes another B2B variant and proves feature depth, not ontology diversity. Building generalisation against a hypothetical second tenant is the same error as P-9, one level up.

**IDEA-9 · A "sustainable default" configuration, stated as the default.** Per §6's numbers, the configuration one agency-running operator can actually sustain is roughly: **one pack run per week, two or three topics, one master per language, X off, blog off** — about 3–4 h/week and $120–170/mo all-in. The plan's current defaults are sized for something 3–4× larger. Either state the sustainable configuration as the shipped default and let the operator scale up deliberately, or state plainly the hours the current default costs.

---

## 6. Honest numbers

The plan's figures versus what the reviewers reconstructed from its own sections. **These are estimates, not measurements** — but they are derived from the plan's own rates, and the gap is large enough to matter.

| Quantity | Plan's figure | Reconstructed | Reasoning |
|---|---|---|---|
| Per two-language **topic pack**, all-in | **$1.91** | **$3.50–6.00** (media $2.20–2.80 · text $1.30–3.20) | A.6's $1.91 is media-only, assumes one 8¢ keyframe rejection and **zero** clip regenerations; add the plan's own one-third first-pass defect rate (+$0.30 localised, +$0.90 whole-master re-shoot) and the text line §5.4 itself sizes |
| Per **pack run** (5 topics, 1–2 masters/language) | not stated | **$10–20** | Only 1–2 of five topics get media (~$2–4), but **all five pay full text**: 0.7–2.25M tokens/run. Text, not media, is the dominant per-run cost under the default configuration |
| Steady-state monthly, 3 runs/week | **$60–65 vendors + self-capped media** | **$270–400/mo** | Vendors ~$130 (Virlo $49 + DataForSEO $12 + TTS ~$22 + music ~$20 + bridge ~$29 from Phase 6 — the plan counts $61 of it) plus §5.4's own $90–140 media and "a text line of the same order" |
| What the $50 trial buys | **"13–26 packs"** | **~8–14 topic packs of media, and zero text** | Only $35 of the envelope is for packs; the mandatory separate router account splits the balance again; the weekly probe draws on it; **and no text tokens are purchasable from router credits at all** |
| Operator hours/week, steady state | *"five topics in under thirty minutes"* | **9–16 h/week** | Pack review 3–5.5 h × 3 runs; weekly rejection loop + mandatory frozen-eval comparison 1–2 h; per-platform label acknowledgement and manual scheduling from Phase 6 1–2 h; monthly load amortised ~1–1.5 h/week |
| Operator hours/month, additional | not stated | **6–9 h/month** | Manual price recheck across ~12–15 registry routes off marketing pages with no machine-readable endpoint; vendor rechecks; calibration report read/decided/logged/re-run; ledger backup (unowned today) |

**Sustainability verdict.** At the recommended cadence this is **1.5–2 working days a week, indefinitely** — not sustainable alongside running an agency. See IDEA-9.

---

## 7. Recommended disposition

**Before Stage-5 approval — six items.** Each is cheap now and expensive later.

1. **F-6** — reconcile W6-1 into the architecture plan. Six sources and the entire Phase-7 winners loop currently hang on a mechanism the operator abolished. This is a decision, not a rewrite; it needs an hour of the operator's judgement, not a wave.
2. **F-3** — name one owner for the canonical gate chain and add the two missing steps. Currently an implementer can build the pipeline correctly from the wrong section and never build the overlay claim pass.
3. **F-1 and F-7/F-33** — correct the cost arithmetic and the approval summary. What the operator is being asked to approve is not what it costs.
4. **F-9** — lift C-4 and C-12 out of Amendment B's Wave 0 so Amendment A is genuinely severable, which is the entire justification for the split.
5. **F-2** — bind approval to bytes. Small change, and it closes a path where an unreviewed video reaches draft creation.
6. **F-8** — reconcile the review-burden arithmetic against the stated target, and decide which one is wrong.

**Before Phase 1.** F-4, F-5, F-35, F-43, F-54 — the fail-closed ordering, the duplicate-run guard, the readiness owner, the pinned task definition, the stale trigger count.

**Before Phase 3 (first money).** F-38, F-39, F-40, F-41, F-42, F-44, F-45 — the whole money-safety cluster. These are the findings most likely to cost real cash rather than time.

**Before Amendment B dispatch.** F-49 (S-3's double definition, before T5 builds the criterion registry on it), F-36, F-37, F-50, F-52, F-53.

**Standing.** F-34 — re-check volatile facts #18 and #9 **now**, before caps are set and before the disclosure overlay is specified.

---

*Review conducted by nine specialists blind to R1–R5, conductor-triaged with five claims verified directly against source. Findings are design-level; no code exists. Where a finding contradicts a prior accepted finding, the prior one governs until the operator rules.*
