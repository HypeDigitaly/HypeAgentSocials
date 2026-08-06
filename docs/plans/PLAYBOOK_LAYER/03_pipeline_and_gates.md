# Playbook layer — 03: pipeline and gates

*Design-phase amendment to `docs/architecture/ARCHITECTURE_PLAN.md`. Prose and tables only; no code, no pseudocode, no configuration syntax. Knobs are described the way §10 describes them — as prose names with what they control, a default and a consumer — never as keys.*

---

## 0. What this document owns, and what it does not

The decision that a **playbook** layer sits between engine and theme — `Engine (non-negotiable floor) → Playbook (what a post IS for this kind of business) → Theme → Language overlay` — is taken and is not re-argued here. Two sibling documents own the **content ontology** (relation types, archetypes, angles, voice genres, next-step/CTA vocabulary) and the **legal claim packs**. This document assumes both exist and specifies the machinery they plug into: how candidates originate, how they are ranked, which gates run against them, how the thirteen model nodes are configured, what a tenant must know factually before anything may be written, and what readiness asserts before any of it may be scheduled.

**The governing rule for everything below.** A playbook **selects from engine-provided registries and may only add strictness**. It never authors a rule, never authors a prompt, never removes a gate, never widens a bar, never lowers a floor. Every extension in this document is shaped to make that rule enforceable rather than aspirational — which is why most of what follows is *registry, selection, interlock and readiness assertion* rather than new behaviour.

**Five invariants are load-bearing and survive intact.** They are restated here because every section below is written against them and any future edit that breaks one is a defect, not a trade-off.

1. **A run producing zero candidates is correct behaviour**, shown rather than hidden, and **no threshold is ever relaxed to manufacture volume** (§2.7).
2. **The stage order is fixed**; no planner reorders, skips or adds a stage (§1.5 rejected alternative 2).
3. **No gate ever defaults open.** A gate or judgment node that cannot run fails its artifact closed to that gate's own *named* degraded outcome, and the gate is named in the pack (§11.3, fifth trigger).
4. **Nothing is silently shipped and nothing is silently dropped.** A failing artifact enters the pack labelled with its attempt history, or is dropped with its reason recorded and its rejected drafts attached (§14.2, §6.7).
5. **Cost is computable before the run starts**, because every node has a bounded input, a bounded output and a per-stage ceiling the cost gate enforces pre-call (§1.5, §5.4a).

---

## 1. The trigger model

### 1.1 The problem, stated exactly

Today there is exactly one origination path. Every candidate enters through the collection stage, "operator-seeded topic" is an *evidence-class label* on an item that still entered that way, and the curated inbox is a *source*, not a second door. Downstream, spin criterion **S-1** (*"could this asset have been written yesterday without this topic? If yes, it fails"*) and §2.8a's resurgence suppression are both purpose-built to kill exactly the recurring-slot and evergreen patterns that a restaurant, a local venue or an expressive page depends on. The result is not that those tenants produce weak packs; it is that they produce empty ones, correctly, forever.

The fix is **three first-class origination paths feeding one unchanged ranking and gate machinery**. It is deliberately *not* a second scoring system, not a second stage, and not a bypass around any gate.

### 1.2 The three trigger classes

| Trigger class | What produces a candidate | Where it enters | Evidence class | Confidence weight is a function of |
|---|---|---|---|---|
| **Collected trend** *(existing)* | A signal fetched or entered through a source in the roster during the collection stage | Collection stage, unchanged | Counted · ranked/presence-only · human-asserted, per §2.7 | Corroborating source families and portfolio reachability this run |
| **Calendar occasion** *(new)* | A **calendar register entry** whose occasion window intersects the pinned run-date, emitted deterministically during the collection stage | Collection stage, as a theme-owned register read | **Human-asserted** — the operator asserted this occasion matters | **Entry resolution completeness**: is the occasion date resolved and correctly positioned; is the instance-distinguishing fact resolved; is the entry inside its validity window and its review-by date |
| **Evergreen library** *(new)* | An **evergreen library item** whose minimum rest interval has elapsed, emitted deterministically during the collection stage | Collection stage, as a theme-owned register read | **Human-asserted** | **Entry resolution completeness**, as above, plus rotation state |

**No new evidence class is created, deliberately.** Evidence class governs one thing in §2.7 — *how virality is treated* — and for both new triggers the answer is identical to the existing human-asserted answer: there is no measured external attention and none is proxied. What the digest needs in order to stay honest is a *different* field, orthogonal to evidence class: the **trigger class** itself, carried on the scorecard, the spin rationale and the digest row. Two orthogonal labels, each answering one question — *where did this come from* and *what kind of evidence backs it* — is cheaper and more honest than a fourth evidence class that would silently duplicate the human-asserted virality treatment.

### 1.3 A fourth connector class, and why the three do not stretch

§2.2 names three connector classes and justifies the split on the grounds that *failure modes, budgets and swap paths genuinely differ, and conflating them is how a credit exhaustion looks like an outage*. That argument compels a fourth class rather than folding the registers into the curated inbox.

| Connector class | What it is | Budget unit | Characteristic failure | Swap path |
|---|---|---|---|---|
| **Tenant register** *(new)* | A theme-owned, operator-authored inventory read deterministically at collection time: the calendar register and the evergreen library | **Inventory** — entries within horizon, items outside rest interval. No network, no credits, no wall-clock of consequence | **Horizon exhaustion** (the calendar runs past its last entry), **rotation exhaustion** (every library item is inside its rest interval), **entry staleness** (an entry describes something that ended) | **None.** The lane emits nothing and says so. There is no fallback vendor and no degraded rung, because there is no external dependency to degrade |

Folding these into the curated inbox was considered and rejected. The curated inbox's whole mitigation apparatus — staleness threshold, escalation at two consecutive misses, an *abandoned* tier — is built around *a ritual the operator skipped*, and its failure is invisible. A calendar's failure is neither: it is arithmetic, visible in advance, and its remedy is "extend the horizon", not "run the session you skipped". Applying inbox escalation semantics to a calendar would produce an alarm that fires for the wrong reason and trains the operator to ignore it — the precise anti-pattern §2.2 already names.

The tenant register inherits everything that is genuinely shared: it is a **source** in the roster with a priority, a per-run budget expressed in entries rather than calls, a ladder whose only rungs are *emit* and *skip-with-log*, and an entry in the source-health reporting so an empty lane is a named degraded state rather than a silence.

### 1.4 How the new candidates traverse normalise → dedupe → rank without corrupting the trend axes

    COLLECTION STAGE  (one stage, unchanged position in the order)
      |                        |                          |
      | collectors /           | calendar register        | evergreen library
      | MCP sources /          | (deterministic emit)     | (deterministic emit)
      | curated inbox          |                          |
      v                        v                          v
    signals                  entry instances            library instances
      |                        |                          |
      +--- canonical key ------+--- cluster key ----------+
      |    near-dup fingerprint      (register entry id + instance stamp)
      |    language stamped at source level
      |    quoted-data wrapper (external text only)
      v
    RANKING ENGINE — one engine, three COMPARISON CLASSES
      |
      | pre-model deterministic filters run FIRST, per lane:
      |   trend   : existing rules-first negative screens (§2.7)
      |   calendar: window position, instance fact resolved, due
      |   library : rest interval elapsed, review-by not lapsed
      |
      | [fit gate]  brand-fit floor + binary veto list  (ALL LANES, unchanged)
      |
      | composite per lane, per its ranking profile
      | demand modifier applied AFTER the composite, where enabled
      v
    ranked topics, PER LANE, each lane capped independently
      -> dedupe index consulted (§2.8a, as reworked in §2 below)
      -> per-lane top-N cap applied AFTER filtering, never by lowering a threshold

Three properties of that flow matter and are stated so no implementer invents an alternative.

**The deterministic filters run before any model call.** A calendar entry outside its window, a library item inside its rest interval and an entry past its review-by date never reach node N-1. This keeps the cost of the two new lanes close to zero in the common case and makes the *ordinary* answer to "why did nothing come from the calendar today" free to compute and free to print.

**The fit gate is unchanged and applies to all three lanes.** Brand fit is not trivially satisfied by a tenant's own calendar entry: a venue can absolutely put an occasion on its calendar that does not fit its declared audience, and the binary veto list — legal and claim risk, controversy, special-category content — must apply to a tenant-authored entry exactly as it applies to a fetched one. The one honest asymmetry: prompt-injection screening is a property of *external* text, so it is evaluated on collected signals and on any external material a register entry quotes, and is recorded as *not applicable* for purely internal entries.

**The two new lanes never enter the trend lane's arithmetic.** No calendar candidate contributes to corroboration counting, to a source's trailing distribution, to a percentile baseline, or to the per-language minimum evidence-and-volume band. That band measures *observed external attention* for a language and would be silently falsified by internal inventory. It stays a trend-lane measurement and its digest line says so.

### 1.5 Scoring a calendar candidate — the minimal honest change

The composite is *virality × brand fit × freshness × confidence*, and all four axes are, as the audit says, functions of external attention age. The plan already contains the precedent for the correct fix and it should be reasoned from rather than replaced: **for a language with no counted-evidence source, exactly one factor is dropped — virality — and it is omitted rather than proxied, and the resulting numbers are declared non-comparable with the four-factor ones.**

The minimal change is to move the key of that rule by one notch:

> The composite's factor set is a property of the **(language × trigger class)** pair — the **comparison class** — rather than of the language alone. Virality is present only where counted evidence is *structurally* available for that pair. Brand fit and a confidence-and-availability factor are present in every comparison class and are never droppable. The freshness factor is present in every comparison class, drawn from that class's signal-class map.

That yields four registered comparison shapes, of which two already exist:

| Comparison class | Factors | Status |
|---|---|---|
| Trend, counted-evidence language | virality × brand fit × freshness × confidence | Existing (English) |
| Trend, no-counted-evidence language | brand fit × freshness × confidence | Existing (Czech) |
| Calendar occasion, any language | brand fit × **occasion proximity** × **entry confidence** | New — the same three-factor shape |
| Evergreen library, any language | brand fit × **rotation rest** × **entry confidence** | New — the same three-factor shape |

**Freshness for the new lanes needs two new signal classes, not a new axis.** §2.7 already carries five signal classes with different age functions and one of them — ad-creative — *runs backwards*, which establishes that "a signal class whose age function has a different shape" is an existing concept rather than an invention.

- **Occasion proximity** (sixth signal class). A windowed function rather than a decay: zero before the entry's lead-in opens, rising to a maximum at the anchor date, falling to zero at the end of the declared tail. It measures *is now the right time to say this*, which is precisely what freshness measures for a trend, expressed against a declared date instead of an observed first-sighting.
- **Rotation rest** (seventh signal class). Zero inside the item's minimum rest interval, rising with elapsed time thereafter, saturating at a declared ceiling. It measures *our own* repetition rather than the world's attention, and it is exactly the treatment §2.7 already prescribes for the evergreen-pain class — *"governed in practice by 'has this angle been covered recently', which makes it a dedupe question rather than a decay curve"* — promoted from prose into a scored axis so the ranking has something honest to multiply.

**Confidence is re-expressed, not dropped — and this is the axis that carries the honesty.** §2.7 states plainly why confidence-and-availability survives the Czech drop: it records how much we actually know, and removing it would silently equate thin evidence with good fit. The same reasoning applies to a declared candidate, so the axis stays and its *referent* changes from observation to declaration:

| Comparison class | What the confidence factor measures |
|---|---|
| Trend | Corroborating source families behind the candidate; share of the portfolio reachable this run |
| Calendar occasion | Is the occasion date resolved and unambiguous; is the instance-distinguishing fact resolved for *this* instance; is the entry inside its validity window; was the entry reviewed within its review-by date; did the fact classes the entry depends on resolve this run |
| Evergreen library | The same entry-resolution terms, plus whether the item's dependent facts still resolve and whether its last use ended in an operator rejection |

The phrase the trend lane uses in the pack — *under-evidenced is not the same as poor fit* — has a direct sibling for the new lanes: **unreviewed is not the same as unimportant, and a low entry-confidence figure names a maintenance task rather than a quality judgement.**

**The demand modifier stays outside the composite** for every lane, as today. It is *enabled* for the calendar lane, because occasion demand is genuinely searchable and the demand-data vendor at the right geography is a real corroborator of "people are looking for this now". It is *disabled by default* for the evergreen lane, because there is nothing time-bound to measure and applying it would reintroduce an attention term through the back door.

**Ranking-profile selection is the only new configurability here**, and it is specified in §6 below.

### 1.6 Lanes, caps, and how "zero candidates is correct" survives a five-posts-a-week tenant

Because the four comparison classes produce numbers with different factor counts, they are **not comparable**, exactly as the two existing per-language composites are not. Three consequences follow and all three are enforcement, not presentation:

1. **The top-N cap is applied per lane**, not to a merged pool. The existing knob becomes *top-N topics cap per language per lane*, and a new engine-side rule caps the **sum of a language's lane caps** at a per-run topic ceiling, so the total artifact count — which is what §5.4a's text forecast multiplies — cannot grow silently by adding lanes.
2. **The monitor-only band is declared per lane.** A band boundary calibrated on four-factor numbers means nothing against three-factor ones.
3. **The digest never prints one sorted table across lanes.** Lane sections, each with its factor set named in the header, and the existing sentence about non-comparable numbers extended to lanes.

Now the question the whole amendment exists to answer honestly.

**A tenant that genuinely must post five times a week does not get a floor. It gets a larger ceiling and better diagnostics.** Lane caps are **caps, not quotas**. If the calendar lane has no entry in window, the evergreen lane is rested out, and the trend lane produced nothing above the fit floor, the run produces zero candidates and that remains the correct outcome. Nothing in this design lets an empty lane borrow capacity from a full one, lets a threshold move because a cadence was missed, or lets an item ship inside its rest interval because the week was thin. The single behavioural change is that the empty pack becomes **diagnosable per lane** rather than being one undifferentiated silence:

> *Trend lane: 11 signals, 0 above the brand-fit floor (9 category mismatch, 2 stale consensus). Calendar lane: 0 entries in window; next entry opens in 4 days. Evergreen lane: 7 items, 7 inside rest interval; next eligible in 2 days.*

That is three named remedies the operator can execute — none of which is "lower a number".

**The honest degrade when the evergreen library is exhausted** is a four-rung ladder, and the top rung is a configuration verdict rather than a runtime behaviour:

| Rung | State | Behaviour |
|---|---|---|
| 1 | Eligible items exist | Normal emission, capped by the lane cap |
| 2 | All items inside rest interval | Lane emits nothing; the digest names the next eligible date. **The rest interval is never shortened to fill a slot** |
| 3 | Library depth is structurally below the configured cadence — item count divided by rest interval supports fewer posts per week than the cadence attempts | A **standing digest line** naming the arithmetic (*"7 items at 21 days rest supports 2.3 posts/week against a configured cadence of 5"*) and a **readiness assertion failure**, because this is a misconfiguration discoverable at theme-load time, not a runtime event |
| 4 | Rung 2 or 3 persists across a configured number of consecutive runs | Escalates under the existing anti-flap rule (§8.12), identically to every other degrade |

And the framing sentence that belongs in §8.2, because the operator will otherwise read the cadence knob as a promise: **pack-production cadence is an attempt rate, not a volume commitment.** It governs how often the pipeline tries. Whether anything ships is decided by inventory and gates, and a run that attempts and produces nothing has done its job.

### 1.7 Digest labelling

Every candidate row carries, in addition to its existing scorecard fields: **trigger class**; **comparison class** (which factor set produced its number); **register entry identity and instance stamp** for the two new lanes; **window position** for a calendar candidate, or **days since last use and rest interval** for a library candidate; and **declared salience** where the entry carries one, labelled as an operator assertion and never rendered as measured attention. The digest gains a **lane summary block** — per lane: emitted, deterministically filtered and why, cleared the fit gate, capped, produced — and a **recurrence-share line** described in §2.5 below.

---

## 2. §2.8a rework — deliberate recurrence versus stale repetition

### 2.1 What the current rule actually keys on, and why it misfires

§2.8a keys suppression on *(trajectory × prior-pack state)*. Both inputs presume observed external attention: trajectory is *"the direction of its corroborating signal count and its counted-evidence percentile"*. A weekly special has no trajectory at all, so a recurring cluster either falls into a row that does not describe it or is caught by *"rising or sustained + generated → resurgence candidate only if a genuinely new angle is detected"* and is suppressed week after week for having no new angle — which is a correct verdict about a trend and a nonsensical one about a Tuesday.

The rule is not wrong; it is answering the wrong question for one class of candidate. It asks *what changed in the world since last time*. For a recurring slot the right question is *is this instance due, and is it distinguishable from the last one*.

### 2.2 The split: declared versus undeclared recurrence

**Recurrence is a property of the source entry, declared in advance in configuration, and visible in the digest** — never a property inferred at run time and never a verdict a model produces. That is the whole safety of this rework: the operator declares recurrence deliberately, before the fact, in a place readiness can inspect, rather than the pipeline discovering a reason to permit a repeat after the fact.

| Path | Which candidates | Governing rule |
|---|---|---|
| **Undeclared recurrence** | Every collected-trend candidate; any register entry that does not declare a recurrence period or rest interval | **§2.8a's existing matrix, unchanged in every cell.** N-2 computes the new-angle verdict; unavailability suppresses the cluster as *resurgence undetermined*; declining-plus-generated is still suppressed permanently |
| **Declared recurrence** | A calendar entry carrying a recurrence period; an evergreen library item carrying a minimum rest interval | The **due-and-distinguishable** rule below |

### 2.3 The due-and-distinguishable rule

A declared-recurrence cluster may produce a candidate only when **both** conditions hold. Both are deterministic in the common case, which is why this path costs nothing and cannot be argued into a pass.

**Condition A — due.** The entry's recurrence period or rest interval, evaluated against the pinned run-date and the cluster's last-generated stamp in the dedupe index, says this instance is due now. A cluster that is not due is suppressed with the label **not due**, which is a routine, non-alarming state and reads differently in the digest from *suppressed as stale repetition*. Distinguishing them matters: one is the system working, the other is the system refusing.

**Condition B — distinguishable.** The instance carries at least one **instance-distinguishing fact** — a fact that varies between instances of this cluster, drawn from a fact class the playbook names in the entry (this week's dish, the guest, the date, the seasonal item, the number in the series). The requirement is on *fact resolution*, not on model judgement: if the named fact class does not resolve for this instance, the candidate is suppressed as **instance-undifferentiated** and the digest names the unresolved class. A tenant who forgot to enter this week's special does not get last week's post again; they get a named, actionable blank.

Both conditions fail closed. Neither can be satisfied by a model call, and neither is reachable through a prompt.

### 2.4 Why this does not reopen the four-near-identical-packs failure

That failure was: the same topic trending four days running produces four near-identical packs. The declared path cannot reach it, for four independent reasons, any one of which is sufficient:

1. **A second instance of the same cluster inside one period can never be due.** Condition A is arithmetic over the dedupe index, and the index is the same one that already prevents yesterday's topic from reappearing as today's discovery.
2. **Declared recurrence is unreachable for collected-trend candidates.** A trend cannot acquire a recurrence declaration, because declaration lives on a register entry and trend candidates have none. The two paths cannot cross.
3. **An indistinguishable instance is suppressed before generation**, deterministically, on a fact-resolution test.
4. **Copy-level repetition is caught by an existing check.** §14.2's layer-1 **cross-pack recurrence check** already compares a new draft's opener and core phrasing against a rolling window of the theme's own recent artifacts, per platform and language, precisely to catch the system developing a house tic. For a declared-recurrence cluster that window is **tightened to cover at least the last several instances of the same cluster key**, regardless of calendar age, so the fourth Tuesday post is compared against the previous three Tuesday posts and not merely against the last fortnight of unrelated output. Its failure disposition: bounded regenerate carrying the instance-distinguishing fact as a *positive* constraint; on second failure the asset is dropped with reason **instance-indistinguishable** and the rejected draft attached.

### 2.5 Guards against declaring everything recurrent

Declaration is the loophole a lazy or pressured configuration would reach for, so it is bounded on four sides:

- **Period floor.** Readiness asserts every recurring entry's declared period is at least its minimum rest interval, and that both are at least the engine's floor for the destination class.
- **Slot budget.** Readiness asserts the total number of declared recurring slots per week does not exceed the pack-production cadence multiplied by the per-run lane cap. A theme cannot declare eleven weekly slots against a three-runs-a-week cadence.
- **Recurrence-share line.** The digest prints what share of the pack's assets came from declared-recurrence entries. Above a configured band it raises a named line — non-blocking, alarmable, escalating under the anti-flap rule — on exactly the model of the per-language evidence-floor line.
- **Rejection binds the entry, not only the instance.** The existing rejection-suppression window applies to the instance. New rule: a rejection carrying the reason code *this slot is not working* suppresses the **entry** until the operator clears it, rather than re-offering the same slot next period. A reason-coded rejection is evidence, and the current rule already refuses to re-offer a rejected topic next week; the same respect is owed to a rejected slot.

### 2.6 What happens to node N-2

N-2's prompt, input shape, cost profile, checkpointing and fail-closed behaviour are **unchanged**, and no playbook may touch any of them (see §4.3). What changes is only *which candidates reach it*: declared-recurrence clusters resolve on Conditions A and B and never call it. This is a cost reduction and, more importantly, a governance property — the node whose job is to suppress is the node furthest from tenant configuration.

---

## 3. The spin-criteria registry

### 3.1 From a fixed set to a registry of families

S-1…S-7 are converted from a fixed universal list into an **engine-owned criterion registry**. A playbook **selects a criterion set keyed by content relation type** (relation types are owned by the ontology sibling; this document assumes their existence and specifies the binding). Selection is constrained to four moves, and no fifth exists:

1. Activate an optional criterion the registry offers for that relation type.
2. Choose a **stricter** registered bar for an active criterion.
3. Add a criterion the registry marks *available* for that relation type.
4. Nothing else. A playbook may not deactivate a universal criterion, may not choose a looser bar, may not author a criterion, and may not author a bar.

**Criteria are organised into families, and every family has exactly one active member per relation type.** This is the structural mechanism that stops the registry becoming a loophole: a criterion is never simply "off"; it is replaced by its family sibling.

    CRITERION FAMILIES                 resolved per RELATION TYPE
    ------------------------------------------------------------------
    ANCHOR      exactly one of  S-1 trend anchor
                                S-8 occasion anchor      (new)
                                S-9 library anchor       (new)
    ADDRESSEE   exactly one bar of  S-2 addressee correctness
    BRIDGE      S-3 connection chain   — conditional on offer attachment
                complement: S-4 distance compliance — ALWAYS active
    PROOF       S-5 proof discipline   — universal, non-selectable
    NEXT STEP   S-6 next-step correctness — universal, non-selectable
    GLUE        S-7 no hype-glue       — universal, non-selectable
    SUBJECT     S-11 subject attribution (new) — active when a third party is named
    SURFACE     S-10 aesthetic coherence (new) — active for visual-first relations
    ATTRIBUTE   S-12 product accuracy   (new) — active when product attributes appear

### 3.2 Which criteria are genuinely universal — verified, and one refuted

The working reading offered was that **proof discipline and next-step correctness** are the genuinely universal ones. Both are confirmed; two more are confirmed with a qualification, and one of the seven is refuted as written.

**S-5 proof discipline — universal, confirmed.** *No proof-shaped statement without a ledger entry, including implied results.* This holds for every tenant archetype without modification, and the archetypes furthest from B2B are the ones that need it most: *"voted the best burger in the city"* is a proof-shaped statement; *"this practice relieves anxiety"* is a proof-shaped statement with a regulatory tail; *"our customers reorder within a month"* is a proof-shaped statement with no digits in it. S-5 is marked **non-selectable** — it is not in any playbook's choice set at all.

**S-6 next-step correctness — universal, confirmed, with the reason it is universal made explicit.** The criterion is *at most one CTA, of an allowed class, correctly routed and language-coherent.* Universality survives a no-offer tenant because the bar is *at most one*, so **zero next steps is a pass**. The criterion polices the correctness of whatever next step is present, never its presence. That distinction is written down here because an implementer reading "next-step correctness" against a restaurant playbook would otherwise plausibly build a presence requirement, and a presence requirement is how a gate turns into a sales mandate.

**S-7 no hype-glue — universal, confirmed, with a named hazard.** The test *does the connective tissue survive removal of connector inflation* applies to any relation type, because glue is a property of writing rather than of commerce. The hazard is **vacuous satisfaction**: for a relation type with no bridge, S-7 has nothing to test and would pass by default, which is a quiet violation of invariant 3. The treatment: a criterion with no applicable material records the verdict **not applicable — no bridge present**, and that verdict is **printed in the spin rationale**, never folded into a pass count. A gate that is silently satisfied and a gate that is silently open are the same defect.

**S-2 ICP addressing — refuted as written, and generalised rather than made optional.** As written, S-2 requires that the asset *name a recognisable situation for a configured segment*, which binds it to the F-D ICP map and therefore to a B2B ontology. Making S-2 optional would be the wrong repair, because the underlying quality is real everywhere: content addressed to nobody in particular is bad content for a restaurant too. S-2 is therefore generalised to **addressee correctness** — *the asset is written for a declared audience of this tenant and not for "everyone"* — with the **bar** varying by relation type from an engine-registered set. The B2B bar remains verbatim ("names a configured ICP segment"). A local-venue bar reads "names a declared audience, occasion context or situation". An expressive-page bar reads "addresses the declared readership". The criterion is never off; only its registered bar is profiled, and the bars are engine-owned, not playbook-authored. This dissolves audit finding B without opening a hole.

**S-3 connection chain — genuinely offer-specific, and this is where the complement rule earns its place.** S-3 requires a bridge *topic → consequence for that audience → why the offer is relevant.* With no offer attached there is nothing to bridge, so S-3's precondition is evaluated deterministically from the spin brief (did the mapper attach an offer?) and, when unmet, S-3 records **not applicable — no offer attached**, printed. The enforcement it would have carried does not evaporate; it transfers:

> **The complement rule.** A criterion may become *not applicable* only where a named sibling criterion carries its enforcement, and the registry records that pairing. A criterion with no active complement may never be deactivated by any means.

For S-3 the complement is **S-4 distance compliance**, which is **always active** and, in the no-offer case, applies at its strictest registered bar: no offer named, no product-path next step, no capability implication. So the failure mode "the writer quietly reintroduces a pitch into a no-offer asset" is caught by S-4 rather than escaping through S-3's absence.

**S-1 real topic anchor — universal as a family, refuted as a single criterion.** Its operational test (*"could this asset have been written yesterday without this topic?"*) is a trend test and is exactly what vetoes calendar and evergreen content today. The family — *every asset traces to a named origination record and says something that record supplies* — is universal and is preserved; the member varies by trigger class. That gives three anchor criteria, of which two are new.

### 3.3 The five new criteria

Each carries a pass bar, a fail smell, an evidence requirement, a repair ladder and a behaviour when its node cannot run. All five run inside the existing nodes **N-8** (angle-level pre-check) and **N-9** (artifact-level post-check); **no fourteenth node is created**, because a new node class would require a new per-call ceiling, a new failure disposition and a new line in §5.4a's arithmetic for no gain — the criterion set is bounded data handed to an existing node.

Every repair below counts against the **existing combined per-artifact repair ceiling** (§14.0). No new repair budget is created; the ceiling is what stops two gates ping-ponging an artifact, and adding criteria must not add allowances.

---

**S-8 — Occasion anchor.** *Anchor family; active for the calendar-occasion relation.*

| Aspect | Specification |
|---|---|
| **Pass bar** | The asset names the occasion or its instance-distinguishing fact, and the occasion is doing work in the body rather than in a salutation. The operational test is S-1's inverted: **would this asset be false, stale or nonsensical if it shipped a month from now?** If it would still read perfectly, it is not occasion content |
| **Fail smell** | **Occasion wallpaper** — the occasion appears only in an opening greeting or a hashtag while the body is interchangeable with any other week. Secondary smell: **window drift** — the asset is correct but the run-date sits outside the entry's declared window, which the deterministic filter should have caught and which therefore also indicates a register defect |
| **Evidence requirement** | Calendar entry identity and instance stamp; the resolved occasion date; the instance-distinguishing fact with its fact class and resolution source; window position at the pinned run-date |
| **Repair ladder** | Fail → bounded regenerate citing the criterion, carrying the instance fact as a positive constraint → second failure → **re-route to the evergreen lane** if the entry declares a library counterpart (the asset is genuinely evergreen and was mis-lane; this is a repair, not a defeat) → otherwise **downgrade to the occasion-free variant** if it can stand alone under its remaining criteria → still failing → drop with reason recorded and rejected drafts attached |
| **When the node cannot run** | The deterministic half (window position, instance-fact resolution) still evaluates and can still **fail** the candidate; the semantic half cannot **pass** it. The asset enters the pack labelled *occasion anchor not judged*, is **not marked publish-ready**, and no media spend is unlocked for its slot |

---

**S-9 — Library anchor.** *Anchor family; active for the evergreen-library relation.*

| Aspect | Specification |
|---|---|
| **Pass bar** | The asset instantiates the specific library item it was emitted from — its declared subject, its declared angle and at least one concrete particular the item supplies — rather than the item's general theme. The operational test: **could this asset have been produced from a different item in the same library?** If yes, it fails |
| **Fail smell** | **Category filler** — an asset about the library item's *category* rather than the item, which is how a library of twelve items silently collapses into three interchangeable posts. Secondary smell: **rotation blur** — phrasing that echoes the previous use of the same item, which is the cross-pack recurrence check's material |
| **Evidence requirement** | Library item identity; the item's declared subject and angle; the particulars used, with their fact classes; last-use date and rest interval; the cross-pack recurrence comparison result over prior instances of this item |
| **Repair ladder** | Fail → bounded regenerate constrained to the item's declared particulars → second failure → **return the item to rest** (the instance is abandoned, the item's rest clock is *not* reset, and the item is flagged for operator review as possibly too thin to sustain rotation) → drop with reason recorded |
| **When the node cannot run** | Enters the pack labelled *library anchor not judged*, not publish-ready. The item's rest clock is not reset, so an unjudged instance does not consume the item's rotation |

---

**S-10 — Aesthetic coherence.** *Surface family; active for visual-first and ambient relations.*

For the expressive/spiritual archetype and much lifestyle and hospitality content, the asset is carried by image plus a short line. The failure is not a forced offer; it is incoherence between the declared register and what was produced, and — the dangerous one — meaning drift into claim territory that a numbers-oriented checker will not see.

| Aspect | Specification |
|---|---|
| **Pass bar** | Three conditions, all required. **(i)** The visual concept, the on-image text and the caption instantiate the *same* declared archetype and voice genre — one archetype per asset, named in the brief. **(ii)** No on-image or caption line is claim-*shaped*: no efficacy, outcome, comparative or absolute construction, evaluated at the shape level as S-5's sibling and independently of the claim gate that follows. **(iii)** The asset's aesthetic descriptors resolve to the theme's visual brand baseline and the genre-negative constraint layer rather than to free description |
| **Fail smell** | **Mood-board drift** — the image says one thing and the text another, each defensible alone. **The inspirational-claim slide** — an aphorism that is functionally an efficacy claim ("this will heal your…"), which is the highest-frequency dangerous output of this genre and the reason the criterion exists |
| **Evidence requirement** | Archetype identity and voice-genre identity from the brief; the resolved aesthetic descriptor set with its source fact class; the enumerated on-image and caption spans with their claim-shape verdicts |
| **Repair ladder** | Fail → bounded regenerate constrained to the declared archetype and, for a claim-shape failure, carrying the permitted statement classes as a positive constraint → second failure → **downgrade to the text-free variant** (image plus caption, on-image text removed) or the **caption-only variant**, whichever the destination format profile permits → still failing → drop with reason recorded |
| **When the node cannot run** | Deterministic half — archetype declared, descriptors resolve, claim-shape lexicon — still runs and can fail. The asset enters the pack labelled *aesthetic coherence not judged*, not publish-ready, and **its keyframe and slide-art spend is not unlocked**. This criterion sits before the keyframe-acceptance event for visual-first assets specifically so that a fail-closed here is also a cost control |

---

**S-11 — Subject-attribution correctness.** *Subject family; active whenever the asset names or characterises a third party.*

| Aspect | Specification |
|---|---|
| **Pass bar** | Four conditions. **(i)** Every statement about a third party is attributed to a named source that exists in the asset's provenance record. **(ii)** It is marked as *their* claim rather than ours — formalising the discipline the operator already applies by hand (§6.11). **(iii)** No assertion of motive, intent or internal state. **(iv)** No comparative or disparaging assertion lacking a comparison entry with evidence and an observation date. Additionally, the asset's own opinion must be textually separable from the reported fact |
| **Fail smell** | **Ventriloquism** — a paraphrase presented in quote shape. **Motive attribution** — *"they did this because they are losing ground"*. **The borrowed metric** — their number repeated as though it validates us, which is the corpus-leakage failure surfacing at spin level rather than at claim level |
| **Evidence requirement** | Per attributed statement: the canonical key and provenance snapshot of the source item, its retrieval timestamp, the claim-ledger status of any figure repeated, and the binary-veto result for competitor disparagement |
| **Repair ladder** | Fail → bounded regenerate with a positive attribution constraint naming the source and the required marker → second failure → **downgrade to the subject-free variant**: keep the general observation, remove the named third party entirely → still failing → drop with reason recorded. This mirrors the value-only downgrade's logic exactly: most attribution failures are failures of *naming*, not of writing, and the correct repair is to stop naming rather than to rewrite harder |
| **When the node cannot run** | Fails closed **immediately to the subject-free variant**, which is the same terminal the ladder reaches, so the degraded path is already defined, cheap and reviewable. Named in the pack; never a silent pass |

---

**S-12 — Product accuracy.** *Attribute family; active whenever the asset states a product attribute.*

| Aspect | Specification |
|---|---|
| **Pass bar** | Every product attribute stated resolves to a fact of the declared class, observed within its stale-warn window, **for the specific variant named**; the asset names exactly one product or a declared bundle; availability status is live; any price matches the site-verified value; any discount carries its terms and its end date; and every attribute stated is one the active fact-schema profile declares mandatory or constraining — an attribute drawn from an *enriching* class may not be stated as fact |
| **Fail smell** | **Attribute drift** — a colour, size, material or shipping term that is plausible and unresolved. **The stale offer** — a promotion whose discount window has closed. **Variant blur** — the asset names the family while the price or specification belongs to one variant, which is the most common and most legally exposed form |
| **Evidence requirement** | Per attribute: fact class, source, observation timestamp, variant identity, and the site-verification result for any binding attribute |
| **Repair ladder** | Fail → bounded regenerate with the offending attributes removed and the resolved attribute set supplied as a positive constraint → second failure → **downgrade to the attribute-free variant**: product named, no numbers, no specifications, content-class next step to the product page → still failing → drop with reason recorded |
| **When the node cannot run** | Deterministic extraction still blocks **every attribute-shaped span**, mirroring N-10's rule that a semantic pass outage yields deterministic verdicts only with claim-shaped candidates blocked rather than passed. The asset degrades automatically to the attribute-free variant. It never passes |

### 3.4 Invariants preserved

- **Nothing defaults open.** Every family resolves to exactly one active member per relation type; readiness asserts family coverage for every relation type in the playbook's mix (§8); a criterion that is not applicable prints its verdict and names its complement.
- **Nothing is silently shipped or silently dropped.** Every ladder above terminates either in a named downgrade variant that enters the pack, or in a drop with the reason recorded and the rejected drafts attached.
- **No new budget.** All repairs count against the existing combined per-artifact ceiling and the existing per-pack allowances; exhaustion routes to the downgrade variant, never to another lap.
- **The resolved criterion set is version-pinned** with the playbook and recorded on every artifact (§4.4), so "which criteria judged this" is answerable months later.

---

## 4. Node-level configuration — the operator's actual request

### 4.1 The governing rule

**Structured slot-filling, never free prompt replacement.** Each of the thirteen nodes has an engine-owned prompt skeleton containing the instruction layer, the safety clauses, the data-carriage posture (quoted data, never instructions) and the output schema. A playbook and a theme may supply content into **named injection points** only. The skeleton, the ordering of its parts, its safety clauses and its output schema are **not slot-addressable by anyone**.

The reason is not tidiness. §14.7 pins prompt provenance per pack and §14.8 makes a pre-rollout regression comparison against a frozen eval set the *precondition* of any prompt change. Both mechanisms depend on a prompt being a composition of versioned, enumerable parts. A free-text prompt override destroys that: there is nothing to diff, nothing to pin, and the eval set measures a prompt that no longer exists.

### 4.2 The seven injection points

| # | Injection point | What it supplies | Direction of permitted change | Who may fill it |
|---|---|---|---|---|
| **IP-1** | **Role / genre framing** | Who the writer is speaking as — a voice-genre identity from the ontology registry plus a bounded descriptor | Selection from registry; descriptor bounded in length | Playbook |
| **IP-2** | **Angle space** | The enumerated set of angles this node may select from | **Narrowing only** — a subset of the engine's angle registry. A playbook may never add an angle | Playbook |
| **IP-3** | **Archetype brief** | The structural template — beat scaffold, slide arc, shot rhythm — selected from the engine's archetype registry | Selection from registry | Playbook; theme may narrow further |
| **IP-4** | **Worked examples** | Few-shot exemplars | **Selectors, not literal text.** Examples are drawn by reference from the theme's exemplar corpus (style-only, leak-checked) or the engine example bank. Bounded by count and by total length | Playbook selects classes of example; theme selects instances |
| **IP-5** | **Emphasis directives** | Bounded "weight this dimension" statements from a registry vocabulary | Selection from registry; bounded count | Playbook; theme may add within the same count |
| **IP-6** | **Banned constructions** | Additional forbidden phrasings and patterns | **Additive only, monotonic** — on the same rule as hard excludes. Neither playbook nor theme may remove an engine or language-overlay ban | Playbook and theme, unioned |
| **IP-7** | **Output-shape constraints** | Count, length, ordering within the engine's declared output schema | **Narrowing only** within the schema. The schema itself is engine-owned | Playbook; theme may narrow further |

### 4.3 Which nodes accept what

Three depths are used. **Deep** nodes are generative and accept most injection points. **Shallow** nodes accept framing and emphasis only. **Data-only** nodes accept no prompt-shaped input at all; a playbook influences them exclusively through the structured data they already receive.

| # | Node class | Depth | Playbook injection points | Theme injection points | Never slot-addressable |
|---|---|---|---|---|---|
| N-1 | Brand-fit judgment | Shallow | IP-1, IP-5 | — | The falsifiable-verdict requirement; the fail-closed-to-monitor-only rule; the ICP/audience excerpt, which is data |
| N-2 | Resurgence "what changed" | **Data-only** | **None** | **None** | Everything. See the note below |
| N-3 | Hook candidate generation | **Deep** | IP-1 · IP-2 · IP-3 · IP-4 · IP-5 · IP-6 · IP-7 | IP-4 · IP-6 | The overgeneration count's engine ceiling; the lexicon screen |
| N-4 | Hook selection by rubric | Shallow | IP-5 (bounded re-weighting of registered rubric dimensions) | — | The rubric's dimensions; the deterministic fallback on failure |
| N-5 | Script writing | **Deep** | IP-1 · IP-3 · IP-4 · IP-5 · IP-6 · IP-7 | IP-4 · IP-6 | Script-lock; the claim-ledger scoping of facts; the beat scaffold's engine floor |
| N-6 | Shot-list / slide-list generation | **Deep** | IP-3 · IP-5 · IP-7 | IP-6 | Row self-containment; keyframe reference discipline |
| N-7 | Media prompt composition | Shallow | IP-6 only, entering as the new **genre-negative layer 3b** (§7.2) | IP-6 as layer 4, unchanged | Route-policy constraint injection; compliance layer 3; the no-unconstrained-prompt rule |
| N-8 | Spin gate angle-level pre-check | **Data-only** | None — the resolved criterion set and bars arrive as structured data | None | The whole prompt |
| N-9 | Spin gate artifact-level post-check | **Data-only** | As N-8 | None | The whole prompt |
| N-10 | Claim gate semantic pass | **Data-only** | None — influence is limited to the fact-schema profile raising a class's obligation (§5) | None | The whole prompt; the five non-disableable check classes |
| N-11 | Voice gate judge, per language | **Data-only** | **Rubric-profile selection only** — a registered genre profile that changes bar values, never dimensions (§4.6) | Its existing banned-phrasing additions | The rubric's dimensions; the flag-rate mechanism; the fail-closed label |
| N-12 | Corpus-leakage comparison | **Data-only** | None | None | The whole prompt |
| N-13 | Site-contradiction comparison | **Data-only** | None | None | The whole prompt; the quoted-data-never-instructions posture |

**Two refusals are deliberate and are the ones worth defending.**

**N-2 accepts nothing.** Its job is to suppress the tenant's own repetition, and a suppression judgement a tenant can shape is not a suppression judgement. The restaurant's legitimate need for recurrence is met entirely by the deterministic due-and-distinguishable path in §2, which changes N-2's *inputs* by routing around it, and never its prompt.

**Every gate node is data-only.** A gate whose prompt a tenant can influence is not a gate. Where genre genuinely must change gate behaviour it does so through mechanisms that are inspectable and version-pinned: the resolved criterion set for the spin gate, the fact-schema profile for the claim gate, and a registered rubric profile for the voice judge. Each of those is a selection from an engine registry with its own calibration artefacts, not a sentence a configuration author wrote.

### 4.4 Versioning, pinning, and what a change invalidates

A playbook carries a **playbook version**. Beyond that, each node's resolved overlay carries an **overlay fingerprint** — a stable digest over the playbook identity and version, the resolved contents of every filled injection point, and the registry versions of every identity referenced (relation type, archetype, angle, voice genre, criterion, bar, ranking profile, bundle).

§14.7 currently pins four things per artifact: prompt-pattern version, rubric version, and the model/version for each of the two roles. It becomes **seven**: engine prompt-pattern version · **playbook version** · **per-node overlay fingerprint** · theme overlay version · language overlay version · rubric version (including the selected genre profile) · model version per role.

**Idempotency keys must include the overlay fingerprint.** §10.4's *idempotency key composition per stage* knob already says the key is formed from semantic inputs plus config or prompt versions. If the overlay fingerprint is not in it, a playbook change leaves cost-bearing stages resumable against work produced by the previous overlay — the resume path would silently mix two prompt generations inside one pack. This is a one-line consequence with a large failure mode, so it is stated rather than implied.

### 4.5 The frozen eval set, per-playbook eval sets, and why each playbook needs its own

**When a playbook changes an overlay, three things must happen and none of them is optional.**

1. **The engine frozen eval set still runs, unchanged.** An overlay changes the prompts that produce engine-evaluated behaviour, so it can regress engine-level safety properties — a genre framing that softens a refusal, an emphasis directive that trades precision for warmth. The engine eval set is the instrument that catches this, and its verdict is a **veto**: an overlay that degrades engine pass rate or human-agreement rate against the last known-good version does not ship, regardless of how much better it makes the genre's output look.
2. **The playbook's own eval set runs**, measuring the things the engine set cannot: whether occasion anchoring holds, whether aesthetic coherence discriminates, whether attribute discipline survives the genre's phrasing habits.
3. **The comparison is a precondition, not a follow-up**, on §14.8's existing three measures — pass rate, human-agreement rate and token cost — with token cost mattering more here than it does for an engine change, because overlays are the thing that lengthens prompts.

**Does each playbook need its own eval set and golden set? Yes, and the plan already contains the argument in a different key.** §14.2 makes it for languages: *"without an English golden set there is no predicted baseline for English… until a golden set exists for a language, that language's judge runs deliberately lenient and its flag-rate ceiling is recorded as inactive rather than described as a control that is quietly not instrumented."* Every clause of that transfers verbatim from language to genre.

- The **flag-rate ceiling is defined against what golden-set calibration predicted.** A B2B golden set predicts nothing about an expressive-register genre, so a ceiling inherited across genres is a number with no referent — the exact condition §14.2 refuses to describe as a control.
- The **eval set's entire validity rests on the authors not having read it.** A playbook author writing overlays *is* a prompt author. An eval set they have fitted their overlay to measures nothing, so a playbook that reuses the engine's eval set as its own has, by that act, unfrozen it.
- The **input distribution differs at the root.** The engine set's inputs are trend-shaped B2B candidates. A restaurant playbook's inputs are calendar instances and library items; a promotion playbook's are product records. A pass rate measured on the wrong distribution is a number that cannot move when the thing it should detect happens.

The cost of that answer is stated plainly rather than buried, and it is the sentence that belongs in §13.1's cost table beside the existing one about languages:

> **A new language is a project. A new playbook is a project. A new tenant on an existing playbook, in an existing language, is configuration.**

**Interim posture, on the existing pattern.** Readiness asserts a playbook declares an eval-set pointer and a golden-set pointer per configured language. A playbook whose golden set is empty runs its judge **deliberately lenient**, records its flag-rate ceiling as **inactive**, prints both facts in the digest, **may be run interactively in test mode, and may never be scheduled** — which is §13.2's existing enforcement posture applied to a new object rather than a new posture invented for it.

### 4.6 Calibrating the judge's flag-rate ceiling per genre

The ceiling is tracked today per theme, destination and language. It becomes a function of **genre rubric profile × language**, pooled across every theme using that profile, with per-theme deviation reported but not thresholded until a named artifact volume exists.

Pooling is the deliberate choice, and the reason is sample size. Adding a genre dimension to a per-theme, per-destination, per-language rate splits already-thin data into cells that will never fill for a small operator, and a ceiling computed on four artifacts is noise dressed as a control. Because the rubric profile is **engine-registered and shared across themes**, pooling at profile level is legitimate: two restaurants using the same profile are two samples of the same rubric, not two different rubrics. Per-theme deviation is still computed and printed as a diagnostic, and it becomes a threshold only when a theme's own volume crosses a named floor — a deferred-value knob on exactly the model §14.8 uses for its A/B percentages.

A genre profile may change **bar values only**, never the rubric's dimensions, and may never remove an engine or language-overlay banned construction. The failure this guards against is specific and likely: an "expressive" profile that legitimises hype language and thereby switches off the slop control in the genre most prone to slop.

### 4.7 The token-budget consequence

§5.4a caps per-node per-call input size. Overlays make prompts longer. Four rules resolve that, and the first is the important one.

1. **The per-node input ceiling does not move.** Overlays consume the existing ceiling; they do not receive an allowance of their own. Any other choice would make the pre-run cost bound a function of tenant configuration, which is the property §1.5 chose a deterministic pipeline to obtain.
2. **Allocation inside the ceiling is reserved-first.** The engine skeleton, its safety clauses and the node's structured data are reserved before anything else; what remains is the **overlay allowance**, sub-capped per injection point, with IP-4 (worked examples) capped by both count and total length because it is the only slot that can grow without bound.
3. **Overflow is a readiness failure, never a runtime truncation.** The resolved prompt for every node — engine skeleton plus every overlay at its configured contents — is **measured at theme and playbook load** against that node's ceiling, and a playbook that does not fit fails readiness with the node named. Runtime truncation is excluded absolutely: truncation removes whichever text sits at the end, non-deterministically, and the end of a prompt is where output-shape and safety clauses live.
4. **The forecast decomposes.** §12.1's text forecast line gains an **overlay share** so a surprising figure has a first place to look.

The spend consequence is quantified in §11 below. The one-sentence version, because it is easy to misread: **overlays do not raise the budget, they raise the burn rate against a fixed budget.** The visible symptom of an over-large overlay is a more frequent mid-pack cap-hit, not a larger bill.

---

## 5. Fact-schema profiles

### 5.1 The exact defect

§6.3's taxonomy has fourteen fact classes, of which **nine are blocking** — identity, offer catalogue, capability statements, audience/ICP map, CTA set, pricing policy, hard excludes, product rules (when the blog is enabled) and compliance obligations. Seven of those are marked *may not be legitimately empty*, and **four of the seven are offer-shaped**: the offer catalogue with status, capability statements, the CTA set and the pricing policy. For a tenant with no offer, those four can never resolve to values and cannot legitimately resolve empty, so §6.5's Step 1 gate fails, the band is **INSUFFICIENT**, and §13.2 makes the theme permanently unschedulable. The remaining three mandatory classes — identity, audience, compliance — are genuinely universal.

### 5.2 The profile, and the rule that makes it safe

A **fact-schema profile** is a playbook-declared mapping from the engine's fact-class registry to an **obligation level**, drawn from a fixed engine vocabulary:

| Obligation level | Meaning | Consequence of *unresolved* |
|---|---|---|
| **Mandatory-resolved** | Must resolve to values | Blocking-gate failure → INSUFFICIENT |
| **Mandatory-resolved-or-legitimately-empty** | Must reach an explicit resolved state; empty is a safe generative state | Blocking-gate failure → INSUFFICIENT |
| **Constraining** | Absence neither blocks nor visibly lowers quality — which is why it silently invites fabrication | Caps the band at PARTIAL and blocks the statement classes that depend on it |
| **Enriching** | Absence only lowers quality | Recorded; no band effect |
| **Not-applicable** | This ontology has no such class | Permitted **only** under the substitution rule below |

Four rules govern a profile, and the second is the whole safety argument.

**Rule 1 — the universal mandatory core is not touchable.** Identity and entities, the audience/segment map (at least one declared audience), hard excludes, and compliance obligations are mandatory in every profile and appear in no playbook's choice set. Alongside them, one meta-rule holds everywhere: **unresolved is never a permitted state for any class a profile declares mandatory or constraining** — the distinction between *resolved-empty* (safe) and *unresolved* (a failure state) is engine property and survives every profile.

**Rule 2 — substitution, never exemption.** A playbook may move an offer-shaped class to *not-applicable* **only by declaring a substitute class from the engine registry that carries the same generative dependency**, and the substitute is then mandatory. A restaurant playbook does not switch off the offer catalogue; it declares an *offering register* in its place — the thing whose existence, status and description its content asserts — and that register becomes mandatory with its own resolution test. The count of mandatory classes never falls; only their identity changes.

This is what delivers the required safety property. A tenant cannot make the pipeline generate content it has no factual basis for, because the only permitted move is to **relocate where that basis lives**, never to remove the requirement that one exists.

**Rule 3 — a playbook may add blocking classes.** A promotion playbook raises product attributes, availability and price values from constraining to mandatory, which is the correct posture for a tenant whose content *is* those attributes. Adding is always permitted; it is strictness.

**Rule 4 — criterion/profile interlock.** Every criterion in the spin registry declares its evidence requirement in terms of fact classes. Readiness asserts that every selected criterion's required classes appear in the profile at an obligation level of at least *constraining*. This is what stops a playbook selecting S-12 product accuracy while declaring product attributes enriching, which would be a gate with nothing to check against.

**Rule 5 — substitutes must be non-trivial.** A substitute class is drawn from the engine registry, carries its own resolution test, and readiness asserts that test is non-trivial: at least one required field with either an external verifier role (a site check, a live URL) or an explicit, dated operator attestation. Without this, substitution becomes exemption wearing a different name.

### 5.3 The confidence-band ladder, expressed without commercial-claim vocabulary

The bands themselves are unchanged in structure, in preconditions and in the exact unattended degrade trigger. What changes is the vocabulary of the **capability column**, which is currently written in commercial-claim terms (prices, trial terms, case metrics, comparative claims) and is therefore unreadable for a tenant with none of those. The capability column is re-expressed against **statement classes** — an engine-owned, ontology-neutral vocabulary describing what kind of assertion a sentence makes.

| Statement class | What it asserts | Depends on |
|---|---|---|
| **Class 0 — structural** | No factual dependency: a question, a hook, a rhetorical frame, a description of a feeling | Nothing |
| **Class 1 — identity** | Who we are, where we are, what we call things | The identity class |
| **Class 2 — descriptive** | What a thing is, does or contains **today**: a capability, a dish, a product description, a practice description | The descriptive class the profile names (capability statements, offering register, product attributes) |
| **Class 3 — quantitative and terms** | Numbers, prices, durations, availability windows, guarantees, discounts | The quantitative classes, site-verified where binding |
| **Class 4 — outcome and endorsement** | Results, efficacy, testimonials, third-party proof, comparisons | The claim ledger and the proof allowlist |
| **Class 5 — temporal and availability** | This is happening, on this date, at this place, until this time | Dated event/availability facts |

The band table then reads:

| Band | Precondition *(unchanged)* | Statement classes permitted |
|---|---|---|
| **FULL** | Every mandatory class resolved (or legitimately resolved-empty) and non-conflicted; every constraining class in one of the two resolved states; every binding fact observed this run or inside its stale-warn window; zero conflicts of any severity | Classes 0–5, each still subject to its own preconditions |
| **PARTIAL** | Mandatory gates pass, but at least one constraining class is unresolved, or a binding fact sits in the warn band, or a non-red-flag conflict was recorded and degraded | Classes 0–2 only. **Classes 3, 4 and 5 blocked**, except where the individual ledger or fact entry is itself fully resolved and unexpired. Next steps limited to the zero-commitment and destination-page classes |
| **MINIMAL** | Resolution from an offline snapshot within its validity window, or config-only resolution of mandatory classes | Classes 0–1, and class 2 **from the snapshot only**. No class 3, 4 or 5 of any kind. Interactive-only by default, heavily marked |
| **INSUFFICIENT** | Any mandatory gate fails; an unresolved red-flag conflict on a mandatory or binding fact; a snapshot expired, failing integrity, or never written | No content generation. Research-only output |

Three things are worth noticing about that reclassification, because they are the evidence it is the right one rather than a rewording.

- It is **behaviour-preserving for theme #1**: prices and trial terms are class 3, case metrics and comparative claims are class 4, event CTAs are class 5 — all blocked at PARTIAL exactly as today.
- It makes the **right** thing happen for the risky new tenants without a single special case. *"This practice relieves anxiety"* is class 4 and is therefore blocked at PARTIAL and permitted at FULL only against a ledger entry — which is precisely the treatment an efficacy claim on an expressive/spiritual page deserves. *"Today's special is X, served until eight"* is class 2 plus class 5 and depends on facts the profile made mandatory.
- It re-expresses the **next-step preconditions** in the same currency. §6.9's CTA classes generalise to *next-step classes* (content · destination/visit · product-path · event · commercial-incentive; the vocabulary is the ontology sibling's). A visit next step depends on class 1 and class 5 facts — address, opening hours — so it is permitted at PARTIAL only when those specific facts resolve, which is the same shape as the existing rule that an event CTA requires a dated event fact.

**The degrade trigger, the red-flag rule, the three asymmetries and the bounded-override rule are unchanged in every particular.** This section changes what the capability column says, never when the gate fires.

---

## 6. Ranking-profile selection

### 6.1 What exists today

There is **no per-axis weight knob anywhere**. The axes multiply, which is the anti-forced-placement mechanism at the topic layer; brand fit and freshness are undroppable; and virality is droppable under exactly one stated condition — a language with no counted-evidence source. The knobs that shape ranking today act on axis *inputs* (freshness half-life per signal class, corroboration bonus magnitude, brand-fit floor, demand-modifier weight, absolute-band fallback thresholds), never on axis weights.

### 6.2 The minimal change

Introduce a **ranking profile**: a named, engine-registered tuple of *(axis set · per-axis normalisation shape · freshness signal-class map · demand-modifier enablement)*. A playbook **selects** a profile per (language × trigger class); it does not author one.

| Ranking profile | Axis set | Freshness signal class | Demand modifier |
|---|---|---|---|
| **Trend, counted** | virality × brand fit × freshness × confidence | spike · rising · launch-hype · ad-creative (inverted) · evergreen-pain | Enabled |
| **Trend, uncounted** | brand fit × freshness × confidence | as above | Enabled |
| **Occasion** | brand fit × occasion proximity × entry confidence | occasion proximity | Enabled |
| **Library** | brand fit × rotation rest × entry confidence | rotation rest | **Disabled by default** |

**New knobs, described as §10 describes them.**

| Knob (prose name) | What it controls | Default | Consumed by |
|---|---|---|---|
| **Ranking-profile selection per language per trigger class** | Which registered profile scores this lane's candidates | Trend profiles per the existing per-language rule; occasion and library profiles where those lanes are enabled | §2.7, §12.1, §13.2 |
| **Occasion-proximity window shape** | Lead-in length, anchor emphasis and tail length for the occasion signal class | Per entry, with a per-theme default; engine floor on the tail | §2.7 |
| **Rotation-rest curve** | Minimum rest interval and the saturation point of the rotation-rest signal class | Per library item, with a per-theme default; engine floor on the minimum | §2.7, §2.8a |
| **Demand-modifier enablement per profile** | Whether the post-composite demand modifier applies to this lane | On for trend and occasion; off for library | §2.7 |
| **Top-N topics cap per language per lane**, and the **per-run topic ceiling** above them | How many candidates each lane may carry forward, and the bound on their sum | Lane caps small; the ceiling at or below today's per-language figure | §2.7, §5.4a, §12.1 |
| **Monitor-only band boundary per lane** | The watch-but-do-not-generate range, per comparison class | Per lane | §2.7 |

### 6.3 What is deliberately not configurable, and why

- **Per-axis weights or exponents.** Refused on three grounds. Multiplication is the anti-forced-placement mechanism, and a weight is precisely the instrument for re-inflating virality over fit. Weights have no calibration mechanism — §6.5's argument for replacing the band *score* with a counting rule applies verbatim: no measurable ground truth, two implementers produce two functions, and the operator-facing meaning drifts silently. And the shape control a tenant actually needs already exists in the input knobs, which *are* calibratable against run data.
- **Dropping brand fit or confidence.** Brand fit is the fit gate's own axis; confidence is the axis that carries the honesty and is the one §2.7 explicitly protects from the Czech drop. Neither is droppable in any profile.
- **Adding an axis.** A new axis changes the comparability of every number in its class and would need its own normalisation, its own scorecard row and its own calibration. Profiles are selected, not composed.
- **Per-playbook changes to the brand-fit floor.** The floor stays a per-theme knob whose loosening already requires a logged human rationale. A playbook that could lower it per genre would defeat that governance in one move.
- **Lane caps as quotas.** Caps bound from above only. Raising a lane cap is placed under the same logged-rationale rule as loosening the brand-fit floor, because "raise the cap until the week fills" is the same failure as "lower the threshold until the week fills", wearing different clothes.

---

## 7. Skill-bundle extension

### 7.1 The diagnosis

The four bundles — short-form scripting, carousel/document, ad creative, long-form article — are **production-format-shaped** and each assumes scripted, argumentative content with a thesis and a next step. Three of the five tenant archetypes do not produce that.

It is worth separating three axes the current text runs together, because the confusion is what makes the bundle list look complete when it is not:

- **Trigger class** — where a candidate came from (trend · occasion · library).
- **Relation type** — what the content *is* doing (pain→offer · commentary · promotion · ambient · occasion).
- **Skill bundle** — how the artefact is *produced* (script · slide deck · article · image set).

Occasion content is not a bundle; it is a trigger, and it is produced through whichever bundle its destination and archetype select. Getting this wrong would produce an "occasion bundle" that duplicates three existing ones.

### 7.2 Three new bundles

| # | Bundle | What it carries | QA emphases | Used by |
|---|---|---|---|---|
| 5 | **Visual-first / ambient** | Caption-to-image coherence patterns; near-zero on-image text density; aphorism and single-statement forms; sequencing across a set; alt-text discipline; composition patterns that keep the burned-in AI disclosure legible against low-contrast imagery | S-10 aesthetic coherence; on-image claim-shape; disclosure legibility measured rather than assumed; archetype consistency across a set | Expressive/spiritual pages; hospitality atmosphere content; parts of creator/UGC work |
| 6 | **Product-hero** | Attribute-accurate description patterns; single-variant discipline; specification-to-benefit ordering; hero-shot and detail-shot pairing; per-destination rules for displaying price and availability | S-12 product accuracy; class-3 statement discipline; variant naming; availability freshness against the stale-warn window | Product/e-commerce promotion |
| 7 | **Commentary / reaction** | Attribution frames; *their claim* markers; quote-versus-paraphrase discipline; the separable-opinion structure; disparagement avoidance patterns | S-11 subject attribution; class-4 boundaries; competitor-disparagement veto interlock; provenance-record completeness as a production requirement rather than a packaging one | B2B thought leadership; creator/UGC reaction formats; any tenant commenting on third parties |

### 7.3 Placement across the four axes

§4.10 places each bundle on three axes — engine pattern set, theme overlay, language overlay. A fourth axis is inserted, and the placement rule is stated once for all seven bundles:

| Axis | Owns |
|---|---|
| **Engine** | The shared pattern set, its selection rubric, its QA emphases, and its safety clauses. Non-removable |
| **Playbook** *(new)* | **Bundle eligibility** — which bundles may serve which relation type and archetype — and genre-level narrowing of which patterns within an eligible bundle are in play, plus the emphasis directives that apply |
| **Theme** | Brand-specific additions and narrowing, unchanged |
| **Language** | Language-specific conventions, unchanged |

The **negative-prompt layer stack** gains one layer in the same spirit, inserted without renumbering the existing five: **layer 3b, genre-negative**, owned by the playbook, sitting above the engine's non-relaxable layers 1–3 and below the theme's brand-negative layer 4. It is additive and monotonic like every other tenant-side constraint layer: a playbook may add what this *kind of business* must never look like, and may remove nothing.

Ad creative is unaffected and remains dormant until the later paid phase.

---

## 8. Readiness validation extensions (§13.2)

The enforcement posture is unchanged and is restated because it is what makes these assertions worth writing: **a theme failing readiness may still be run interactively in test mode; it may never be scheduled.**

New assertions, in the register of the existing ones:

- **A playbook is declared and resolves.** The theme names exactly one playbook; it resolves to a registered playbook identity and version; every registry identity it references — relation type, archetype, angle, voice genre, next-step class, criterion, bar, ranking profile, skill bundle, fact class — resolves at the pinned registry version. A dangling identity is a failure that names the identity, not a warning.
- **Exactly one playbook per theme.** A tenant that is genuinely two businesses is two themes. This is asserted rather than assumed because the alternative — a merged playbook — is the shape in which strictness gets lost.
- **The archetype mix is well-formed.** Declared shares fall inside the engine's band; **every archetype in the mix has at least one eligible asset type, at least one eligible destination enabled in the matrix for every configured language, and at least one eligible skill bundle.** An archetype with no destination is a silent producer of nothing.
- **The angle space is non-empty for every (relation type × archetype) pair in the mix.** Empty is the condition under which N-3 has nothing to select from and would either fail or improvise; both are unacceptable and neither should be discovered at three in the morning.
- **Every selected claim pack's mandatory fact classes resolve.** The claim packs are the sibling document's object; this assertion is the interlock, and it fails naming the pack and the class.
- **Criterion coverage and interlock.** Every criterion family resolves to exactly one active member for every relation type in the mix; every criterion that can be *not applicable* has an active complement; every selected criterion's required fact classes appear in the fact-schema profile at obligation level *constraining* or higher.
- **The fact-schema profile is sound.** The universal mandatory core is present at mandatory level; every offer-shaped class moved to not-applicable has a declared substitute; every substitute's resolution test is non-trivial in the sense of §5.2 rule 5.
- **The trigger set is non-empty and every enabled trigger has a source.** The trend trigger requires at least one active source in the roster. The calendar trigger requires a calendar register with at least one entry whose window intersects the next horizon period. The evergreen trigger requires a library whose depth divided by rest interval supports the configured pack-production cadence.
- **Declared-recurrence sanity.** Every recurring entry's period is at least its minimum rest interval and at least the engine floor; total declared recurring slots per week do not exceed cadence multiplied by the per-run lane cap.
- **Ranking configuration is complete per lane.** A ranking profile, a top-N cap and a monitor-only band exist for every (language × enabled trigger class), and the sum of a language's lane caps is within the per-run topic ceiling.
- **Every node's resolved prompt fits its input ceiling.** Measured at load, engine skeleton plus every overlay at configured contents, per node, per language. Failure names the node and the overrun.
- **The playbook declares an eval-set pointer and a golden-set pointer per configured language.** An empty golden set does not fail readiness outright; it forces the lenient-judge posture, records the flag-rate ceiling as inactive, prints both in the digest, and **blocks scheduling**.

---

## 9. Replacing §13.3 and §13.4

### 9.1 Why the current fixture cannot fail

§13.3's second-theme fixture is a Czech e-commerce shipping-and-returns automation product. It differs from theme #1 on language, source roster, destination mix, video recipe, budget, register and cadence — genuinely useful evidence that those surfaces are parameterised. On the dimension this amendment exists to address it differs not at all: it has an offer catalogue with statuses and canonical URLs, positive and negative capability statements, an ICP map of segments, a pain-to-offer relation, product-path CTAs, and trend origination. Every assumption the playbook layer questions is held constant. The audit's characterisation is correct: it is a fixture that cannot fail, because the ontology it would have to falsify is the one it instantiates.

The repair is not to delete it. It proves what it proves. The repair is to **demote it and add fixtures that can fail.**

### 9.2 What the replacement fixture must be

Stated as required properties rather than as a name, so that a future author cannot satisfy the requirement with another near-sibling:

| # | Required property | Which assumption it falsifies |
|---|---|---|
| 1 | **No offer catalogue in the F-B sense** — nothing carrying a status field, a canonical URL and a product-path next step | The S-3 premise; forces the substitution rule to do real work |
| 2 | **A majority of candidates originating outside collection** — the calendar and library lanes carry most of the pack | The single-trigger assumption; exercises lane caps, comparison classes and the honest-empty behaviour |
| 3 | **Deliberate recurrence as a core requirement** — a slot that must ship every week, indefinitely | The §2.8a rework, including its guards |
| 4 | **A dominant relation type other than pain→offer** | The criterion registry, the complement rule and the anchor family |
| 5 | **A primary asset that is visual-first rather than argumentative** | The skill-bundle set and the visual-first bundle's QA emphases |
| 6 | **A statement space dominated by classes 1, 2 and 5 rather than 3 and 4 — with a genuine claim hazard of its own** | The de-commercialised band vocabulary; proves the reclassification is not merely a rewording |

**Two fixtures are required, not one**, and the reason is the failure being repaired: one fixture too close to home is exactly how §13.3 arrived at a proof that could not fail. Two fixtures chosen to fail *different* assumptions is the minimum that makes the generality claim falsifiable.

- **Fixture A — a single-location restaurant.** Czech, one location, a weekly menu with a recurring special, five posts a week, Instagram and Facebook primary, no e-commerce. It satisfies properties 1, 2, 3, 5 and 6, and its dominant relation types are occasion and ambient. Its sharpest test is the one the audit named: a tenant whose entire content model is the recurring-slot pattern §2.8a was built to suppress.
- **Fixture B — an expressive/spiritual page.** No offer, no segments in the ICP sense, no product, evergreen-dominant, visual-first, with a real claim hazard in the efficacy and wellbeing adjacency. It satisfies properties 1, 2, 4, 5 and 6 and stresses the parts fixture A does not: the addressee bar for a readership rather than a market, S-10, class-4 blocking as the load-bearing safety behaviour, and the boundary at which a claim pack stops being sufficient.

The three fixtures should be presented as a **coverage table** stating, per fixture, what it can falsify and what it cannot — the artefact whose absence let the current §13.3 read as a general proof.

### 9.3 What §13.4 must now honestly say it cannot serve

The existing entries stand: a language the system has never written; a destination with fundamentally different asset physics; brand truth outside an addressable knowledge base; live publishing. Seven honest additions:

1. **A tenant whose content is primarily reactive to inbound conversation** — community management, replies, comment-thread engagement. There is no inbound surface, no conversational state and no per-interlocutor memory, and adding one is a different product.
2. **A tenant requiring posting tied to an event as it unfolds.** Cadence is scheduled, the human review gate is asynchronous, and media generation may span runs. Occasion content is *anticipated*, never live.
3. **A creator/UGC agency at full scope.** The archetype is served only in its *brief-and-script* form. Its *asset-assembly* form depends on third-party footage and real people's likenesses, which the v1 likeness and voice-clone ban, the rights-class allowlist and the corpus rules exclude absolutely. This must be stated because the archetype is on the list of five and a reader will otherwise assume it is fully covered.
4. **A tenant whose claims are regulated** — health, financial or legal advice. A playbook cannot make a regulated-claim tenant safe by configuration; strictness selection is not a regulatory regime. The expressive/spiritual archetype sits adjacent to this boundary, and the boundary must be drawn in §13.4 rather than left to the claim packs to imply.
5. **A tenant needing more than one playbook at once.** One playbook per theme is asserted at readiness; a genuinely two-natured business is two themes with two packs and two review streams.
6. **A tenant whose required cadence exceeds what its trigger inventory can supply.** This is not a design gap; it is a configuration impossibility, and it is named here so it is not later mistaken for a bug and repaired by relaxing a threshold.
7. **A new playbook is a project.** Its own criterion selections, fact-schema profile, ranking profiles, bundle eligibilities, eval set and per-language golden sets. Adding a *tenant* to an existing playbook is configuration; adding a playbook is not.

---

## 10. Wire-in

### 10.1 Existing sections changed

| § | What changes | Kind |
|---|---|---|
| §1.2 | Theme loader also resolves the playbook and composes overlays; collection layer also reads tenant registers; ranking engine produces per-lane slates. **No new component and no new stage** | Extension |
| §1.3 | Diagram gains the two register inputs into collection, the lane split at ranking, and overlay composition beside copy generation | Extension |
| §1.5 | Node inventory gains an overlay-acceptance column; per-node ceilings are measured against the resolved overlay. Explicit statement that **no fourteenth node is added** | Extension |
| §2.2 | Fourth connector class — **tenant register** — with its own budget unit, failure modes and (absent) swap path | Extension |
| §2.3 | Calendar register and evergreen library appear as theme-owned source rows with priority, cadence and characteristic failure | Extension |
| §2.7 | Comparison classes; ranking profiles; occasion-proximity and rotation-rest signal classes; confidence re-expressed for declared candidates; top-N and monitor-only per lane; the zero-candidate and never-relax sentences preserved verbatim and extended to lanes | Extension |
| §2.8 | Flow diagram gains the register emitters and the per-lane deterministic pre-filters ahead of any model call | Extension |
| §2.8a | Declared-versus-undeclared recurrence split; due-and-distinguishable rule; guards; N-2 routing. The existing matrix is preserved unchanged for the undeclared path | **Rework** |
| §3.1 | Note that the identical-mix rule is per language and does not interact with lanes | Extension |
| §3.2 | Archetype eligibility per destination joins the matrix | Extension |
| §3.5 | Review-depth profile becomes per archetype and bundle, not per asset type alone | Extension |
| §4.2 | Stage 1 selects from the playbook's angle space; stages 2–4 nodes accept overlays at named injection points | Extension |
| §4.10 | Injection points and the slot-filling rule; genre-negative layer 3b; three new skill bundles; four-axis bundle placement | **Major extension** |
| §5.4a | Reserved-first allocation inside the unchanged per-node ceiling; overlay allowance and per-slot sub-caps; readiness-time fit measurement; forecast gains an overlay share | Extension |
| §6.3 | Obligation levels become profile-declared; universal mandatory core; substitution rule; substitute non-triviality | Extension |
| §6.5 | Capability column re-expressed in statement classes; preconditions, degrade trigger, red-flag rule and asymmetries unchanged | **Rework of vocabulary only** |
| §6.9 | Relation types; next-step classes generalise CTA classes; mapping distance applies to offer-bearing relations with S-4 named as the complement elsewhere | Extension |
| §6.10 | S-1…S-7 become a registry of families; five new criteria; complement rule; not-applicable verdicts must be printed. **The sentence fixing the set at seven is deleted** | **Rework** |
| §8.2 | Cadence is an attempt rate, not a volume commitment; trigger-inventory adequacy is a readiness assertion | Extension |
| §10.2 | New research-block knobs: calendar register contents and horizon; evergreen library contents, rest intervals and review-by dates; per-lane caps and monitor-only bands; ranking-profile selection; occasion-window and rotation-rest shapes; demand-modifier enablement per profile | Extension |
| §10.3 | New spin-block knobs: playbook selection and version pin; fact-schema profile; relation-type set; criterion selections and bar choices; genre rubric-profile selection; recurrence-share band | Extension |
| §10.4 | New output-block knobs: archetype mix; bundle eligibility; per-injection-point overlay caps; per-run topic ceiling; eval-set and golden-set pointers per playbook per language | Extension |
| §10.4 (idempotency) | Idempotency key composition per stage must include the overlay fingerprint | Extension |
| §10.5 | The registries are engine-level and named: criteria and bars, relation types, archetypes, angles, voice genres, statement classes, next-step classes, ranking profiles, signal classes, skill bundles, rubric profiles, injection-point schema | Extension |
| §11.3 | Fifth-trigger enumeration gains the per-criterion degraded outcomes for S-8…S-12 | Extension |
| §12.1 | Digest header gains playbook identity and version; lane summary block; trigger and comparison-class labels; recurrence-share line; non-comparability sentence extended to lanes; overlay share on the text forecast | Extension |
| §12.2 | Spin rationale gains relation type, archetype, angle identity, active criterion set and its version, and per-node overlay fingerprints | Extension |
| §13.1 | Cost table gains a **playbook** row; the "a new language is a project" line gains its playbook sibling | Extension |
| §13.2 | The eleven new assertions in §8 above | Extension |
| §13.3 | Existing fixture demoted to *configuration-surface fixture*; two ontology fixtures added; fixture-coverage table added. **The claim that it proves the configuration surface *generalises* is narrowed** | **Rework** |
| §13.4 | Seven additions to the honest cannot-serve list | **Rework** |
| §14.0 | New criteria's repairs count against the existing combined ceiling; no new budget is created | Extension |
| §14.1 | Reads the resolved criterion set rather than a fixed seven. **The sentence "Both checkpoints evaluate the same seven criteria S-1…S-7" is deleted** | **Rework** |
| §14.2 | Genre rubric-profile selection; flag-rate ceiling per genre profile × language, pooled; cross-pack recurrence window tightened for declared-recurrence clusters | Extension |
| §14.4 | Register profiles are engine-registered rubric variants changing bars, never dimensions; no playbook authorship | Extension |
| §14.7 | Four pins become seven | Extension |
| §14.8 | Per-playbook eval and golden sets; the engine set retains veto power over overlay changes; overlay changes are pre-rollout gated | Extension |
| §15.2 | New risk rows (§11 below) | Extension |
| §16 | New open decisions (lane-cap defaults; pooling volume floor for flag-rate ceilings; whether the expressive/spiritual archetype is accepted given regulated-claim adjacency) | Extension |
| §17 | A playbook's Phase-0-equivalent: eval set, golden sets per language, criterion selections, fact-schema profile, fixtures | Extension |
| Appendix A | A second traced topic, through the calendar lane, so the new path has a worked end-to-end example | Extension |

### 10.2 New concepts and where they must be referenced

| New concept | Must be referenced by |
|---|---|
| **Playbook** (identity, version, resolution) | §1.2, §1.5, §10.1, §10.3, §10.5, §12.1, §13.1, §13.2, §14.7 |
| **Trigger class / lane** | §2.2, §2.3, §2.7, §2.8, §2.8a, §8.2, §12.1, §13.2 |
| **Tenant register** (connector class) | §2.2, §2.3, §10.2, §13.2 |
| **Comparison class** | §2.7, §12.1 |
| **Ranking profile** | §2.7, §10.2, §10.5, §13.2 |
| **Occasion-proximity / rotation-rest signal classes** | §2.7, §10.2 |
| **Declared recurrence; instance-distinguishing fact** | §2.8a, §6.3, §12.1, §13.2, §14.2 |
| **Criterion registry; criterion family; complement rule** | §6.10, §14.1, §11.3, §13.2 |
| **Injection point; overlay fingerprint** | §1.5, §4.10, §5.4a, §10.4, §14.7, §14.8 |
| **Genre-negative layer 3b** | §4.10, §5.2 |
| **Fact-schema profile; obligation level; substitution rule** | §6.3, §6.5, §10.3, §13.2 |
| **Statement class** | §6.5, §6.9, §14.3 |
| **Next-step class** (generalising CTA class) | §6.9, §3.3, §14.3 |
| **Genre rubric profile** | §14.2, §14.4, §10.3, §10.5 |
| **Per-playbook eval set and golden set** | §14.2, §14.8, §13.1, §13.2, §17 |
| **Visual-first / product-hero / commentary bundles** | §4.10, §3.5, §10.4 |

---

## 11. Cost and risk

### 11.1 Direction and rough magnitude of the text-token change

The base §5.4a describes: roughly a hundred and thirty artifacts per run, five model-mediated evaluations per artifact, three ceilings (per-run text budget, per-stage call ceiling, per-pack judge allowance) and per-call ceilings underneath them.

**Where spend rises.**

| Source of increase | Mechanism | Rough magnitude |
|---|---|---|
| Overlays on the three deep nodes (N-3, N-5, N-6) | Input tokens grow by the overlay allowance; worked examples dominate. Output unchanged | Input on those calls up roughly one third to two thirds; those nodes are a minority of total calls |
| Overlays on the shallow nodes (N-1, N-4, N-7) | Framing and emphasis only, both bounded | Low single-digit percent |
| Additional active spin criteria | Slightly larger structured input to N-8/N-9 and one more per-criterion verdict in the output | Roughly ten to fifteen percent on the two spin nodes per additional active criterion |
| Extra candidates from two new lanes reaching N-1 | One brand-fit call per *eligible* entry — but only entries surviving the deterministic pre-filters reach a model call | A handful of calls per run in normal operation |

**Where spend falls, or does not rise.**

- Declared-recurrence clusters resolve on arithmetic and **never call N-2**.
- Every new gate criterion's deterministic half — window position, due, rest elapsed, instance-fact resolution, attribute extraction — costs zero model tokens by design.
- Occasion and library candidates compute no virality, which was never a model cost but does remove per-source normalisation work.

**Net estimate.** Per-run text **input** tokens up roughly **15–30%** in the typical case; total per-run text spend up roughly **10–25%**, concentrated in copy generation; worst case around **40%** for a playbook that uses its full worked-example allowance on all three deep nodes in both languages.

**The framing that matters more than the number.** Because the per-node ceilings and the three §5.4a aggregates are unchanged, **overlays do not raise the budget; they raise the burn rate against a fixed budget.** The observable symptom of an over-large overlay is therefore a more frequent *mid-pack cap-hit* outcome — a pack that stops early and is honestly labelled — rather than an unexpected bill. Two controls make that legible rather than mysterious: the readiness-time prompt-fit measurement, which catches the pathological case before a run exists, and the overlay share on the digest's text-forecast line, which gives a surprising figure a first place to look.

**The real cost lever is the lane caps, not the overlays.** Text spend scales with artifact count, and artifact count scales with topics carried forward. A per-lane cap set generously across three lanes multiplies the artifact count directly, which is why the sum of lane caps is itself capped by a per-run topic ceiling and why the forecast reads it.

### 11.2 New risks

| ID | Risk | Consequence if ignored | Mitigation | Owning section |
|---|---|---|---|---|
| **PB-R-1** | **Playbooks outrun their eval and golden sets.** A playbook ships before its calibration artefacts exist | Genre judges run permanently lenient with flag-rate ceilings recorded as inactive — a control described in the design and not instrumented in reality, which is §14.2's own named failure repeated at a new level | Readiness requires declared eval-set and golden-set pointers; an empty golden set forces lenient posture, records the ceiling inactive, prints both in the digest and **blocks scheduling**; a new playbook is classified as a project, not configuration | §13.2, §14.2, §14.8 |
| **PB-R-2** | **Declared recurrence as a suppression loophole.** A theme declares most of its content recurrent to escape §2.8a | The four-near-identical-packs failure returns through the front door, with configuration as its warrant | Period floor at or above rest interval; recurring-slot budget asserted against cadence; instance-distinguishing fact required per instance and fail-closed when unresolved; cross-pack recurrence window tightened over prior instances of the same cluster; recurrence-share digest line with anti-flap escalation | §2.8a, §13.2, §14.2 |
| **PB-R-3** | **Lane-cap creep as covert threshold relaxation.** Volume pressure is absorbed by raising caps rather than by lowering floors, so the "never relax a threshold" rule is honoured in letter and defeated in effect | The anti-volume-manufacturing principle becomes decorative; packs fill with weak candidates that each individually passed | Caps are caps, never quotas; raising a lane cap requires a logged human rationale under the same rule as loosening the brand-fit floor; the digest prints emitted / filtered / passed / capped per lane so a shortfall is visible rather than fillable | §2.7, §10.2, §12.1 |
| **PB-R-4** | **The evergreen library as a fabrication surface.** A library item is tenant-authored prose with no provenance, unlike a research artifact | Content whose factual basis exists only in a configuration file, laundered into a pack by an anchor criterion that only checks the asset traces to *an item* | Library items are **briefs, not facts**, on the same rule as the exemplar corpus: any factual statement they contain must resolve through the claim ledger or be blocked; items carry an author and a review-by date; entry confidence falls as review-by lapses | §6.3, §6.11, §2.7 |
| **PB-R-5** | **Fact-class substitution used as exemption in disguise.** A playbook substitutes a class that is trivially satisfiable | The offer catalogue's mandatory status is removed by another name, and the no-factual-basis guarantee fails silently for exactly the tenants it was written for | Substitutes are drawn from the engine fact-class registry with their own resolution tests; readiness asserts non-triviality — at least one required field with an external verifier or a dated operator attestation; mandatory-class count may never fall | §6.3, §13.2 |
| **PB-R-6** | **Genre rubric profile as a slop escape hatch.** An "expressive" profile that legitimises hype language | The voice gate stops catching slop in the genre most prone to it, and the failure is invisible because the profile's own flag rate looks healthy | Profiles are engine-registered, change bar values only, never dimensions; banned-construction layers stay monotonic; every profile carries its own golden set; profile changes pass §14.8's pre-rollout gate against both the engine and playbook eval sets | §14.2, §14.4, §10.5 |
| **PB-R-7** | **Token-ceiling squeeze on safety clauses.** An implementer trims engine skeleton text to make an overlay fit | Safety clauses and output-shape constraints are removed non-deterministically from the end of a prompt, and the gate that appears to run is running against a mutilated instruction | Reserved-first allocation with a non-truncatable engine skeleton; overlay overflow is a readiness failure naming the node; runtime truncation is excluded absolutely | §5.4a, §13.2 |
| **PB-R-8** | **Comparison-class confusion in the digest.** An operator compares a three-factor calendar score with a four-factor trend score | The wrong topic is approved and the scorecard, the plan's main defence against unauditable ranking, becomes actively misleading | Scores printed only within lane sections, never in one sorted table; each lane header names its factor set; §2.7's existing non-comparability sentence extended to lanes and reprinted beside the numbers | §12.1, §2.7 |
| **PB-R-9** | **Cadence pressure re-entering as configuration habit.** Rest intervals are shaved week by week until the library rotates faster than it can sustain | Rotation-rest becomes a formality, the same items recur, and the house-tic check becomes the only remaining defence | Rest-interval changes logged with rationale; the digest prints effective rotation period against configured; readiness recomputes library-depth adequacy on every change and fails when depth falls below cadence | §8.2, §13.2 |
| **PB-R-10** | **Ontology drift between playbook and registries.** Sibling-owned registries version independently of playbooks that pin identities into them | A registry change silently re-points a criterion, an archetype or an angle, and pinned artifacts become unreproducible — the exact property §14.7 exists to guarantee | Overlay fingerprints include referenced registry versions; readiness fails on any dangling or moved identity; a registry version change is treated as a prompt change and passes §14.8's pre-rollout gate | §14.7, §14.8, §13.2 |

*Identifiers are provisional and local to this document. Two sibling documents are being authored concurrently against the same logs; final identifiers are allocated at merge from the next free numbers in `RISK_LOG.md`, `DECISION_LOG.md` and the open-decision series.*

---

## 12. Open questions

1. **Registry ownership boundaries.** This document assumes the ontology sibling owns relation types, archetypes, angles, voice genres and next-step vocabulary, and that *audience descriptors* — the generalisation of the ICP map that S-2's addressee bars read — sit there too. If audience descriptors land in the claim-pack document or nowhere, S-2's generalisation has no registry behind it.
2. **Statement class ↔ claim pack binding.** The band table in §5.3 permits statement classes; the claim packs constrain what may be said within them. The binding — whether a claim pack declares statement-class permissions directly, or declares fact-class requirements from which permissions are derived — is a joint decision with the claim-pack sibling.
3. **Acceptance of the fourth connector class.** Folding the tenant register into the curated inbox was rejected on failure-mode grounds. If that is refused, the registers still work, but they inherit staleness-escalation semantics that fire for the wrong reason.
4. **Lane-cap and per-run topic-ceiling defaults.** Directional only in this document. They are the dominant text-cost lever and want an operator decision against a real budget, on the same footing as the existing top-N recommendation.
5. **Pooling volume floor for genre flag-rate ceilings.** The design is specified; the artifact count at which per-theme deviation becomes a threshold rather than a diagnostic is a deferred-value knob.
6. **Whether the expressive/spiritual archetype is accepted at all.** Its claim hazard sits adjacent to regulated advice, and §13.4 now states that a playbook cannot make a regulated-claim tenant safe by configuration. Whether the archetype is served, served with a restricted claim pack, or declined is a business decision, not an architectural one.
