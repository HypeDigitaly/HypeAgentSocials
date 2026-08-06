# 06E — Readiness and defaults: what a blank field means, how layers resolve, and what the system does when the config is thin

*2026-08-06 · working annex under `CONDUCTOR_RULINGS.md`, which governs · design deliverable, no code*

---

## 0. What this file owns, and what it does not

The configuration is being split into an **authoring form** and a **resolved form** with a resolver between them (CR-1), run at config load and never per run (CR-2). Three parallel tasks own three parts of that: the **per-knob table** (which knob sits in which tier, with which default and which regime), the **resolver's internal design** (how free text becomes registry selections, and what its failure messages look like in the operator's language), and the **operator-facing form** (the ~10 Tier-A questions as they are actually worded).

This file owns the fourth part, which is the semantics underneath all three:

- what each of the three kinds of "blank" *means*, and how they are told apart at load (§1);
- the layer-resolution procedure, stated once and totally, including the ordering ruling on theme versus language overlay (§2);
- the readiness assertions the config surface now contributes to `ARCHITECTURE_PLAN.md` §13.2 (§3);
- what happens when the resolved config goes stale or the world drifts underneath it (§4);
- the degradation ladder for a minimum config, and an honest statement of what none of this catches (§5);
- the one-time migration of theme #1 and the comparison that proves it behaviour-preserving (§6);
- open questions as `CFG-OD-n` (§7).

It contains **no per-knob rows**. Where it needs to talk about a specific knob it does so as a worked example and names it in prose, the way `ARCHITECTURE_PLAN.md` §10 does.

Two further ownership notes, so the merge is clean: the **statement-class registry** and the **fact-schema profile** rules are `03_pipeline_and_gates.md` §5's and T6's, and are referenced here as interlocks rather than restated; **ranking-profile selection** is T4's and appears here only as a knob that obeys the registry-selection regime.

---

## 1. Three kinds of blank, not one

### 1.1 The rule being extended, quoted

`ARCHITECTURE_PLAN.md` §6.3 states, of the fourteen **fact** classes:

> **The single most important rule in this layer: missing is not the same as empty.** Every constraining class resolves to an explicit state — *resolved-with-values*, *resolved-empty*, or *unresolved*. **Resolved-empty is a first-class, safe, generative state**: the generator is told it has zero approved proof points and should write teaching-led content. **Unresolved is a failure state**: we do not know whether proof exists, so claims are forbidden *and* the confidence band drops, because we also cannot trust the excludes list that lives beside it.

**This section extends that rule; it does not diverge from it.** The trichotomy is imported wholesale, with the same asymmetry (empty is safe, unknown is not) and the same reason (a system that cannot tell the two apart will treat not-knowing as permission). What is added is that configuration knobs need **one more state than facts do**, and the reason is structural rather than a matter of taste.

A fact class resolves once, against external sources, and has no layer above it — if no source carries it, nobody carries it, and that is `unresolved`. A configuration knob resolves against a **stack of five layers** (CR-6), and a knob the operator never touched is, in the overwhelming majority of cases, not a gap at all: a layer above supplied the value, deliberately, and that is the intended and dominant state of a well-designed config. Folding that case into either of the fact-side states would be wrong in both directions. Calling it `resolved-with-values` erases the fact that nobody at the tenant layer chose it, which is exactly the information the CR-2 readback exists to show. Calling it `unresolved` would make every coherent config fail readiness on a hundred-odd counts.

So: **three states for knobs, and the third is the common one.**

### 1.2 The three states

| State | Plain meaning | How it arises | Safe? |
|---|---|---|---|
| **Inherited** | The operator did not answer at this layer, and a layer above supplied the value | The fold (§2) reaches the knob with a value already in the accumulator and no later contribution | **Yes.** It is the majority state and the reason a ~130-knob surface is fillable at all |
| **Deliberately empty** | The operator answered, and the answer was "none" — and that answer is meaningful, safe and load-bearing | An affirmative act with an empty payload, recorded with author, date and the consequence accepted | **Yes.** This is §6.3's *resolved-empty*, applied to config: "this tenant runs no affiliate programme", "this theme declares no research-side excludes beyond the floor" |
| **Unanswered** | Nobody supplied anything: no layer carried a value, and no empty answer exists | Either never answered (only reachable at Tier A, see §1.4) or orphaned by drift (§4) | **No. This is a failure state**, and it never becomes a zero, an empty set, an "off", or a "whatever the engine had lying around" |

A fourth condition exists on the **authoring** side and deliberately does not get its own resolved state: the resolver's non-mapping outcomes. Per CR-7, guidance that maps to no registry member is reported with the unmapped span quoted verbatim; guidance that is internally contradictory has both readings surfaced; guidance implying a Tier-1 relaxation is refused with the floor named. All three land in the resolved form as **`unanswered` with a reason attached**, because from the pipeline's point of view they are identical — there is no value — while from the operator's point of view they need three different messages. Inventing a fourth resolved state would put resolver bookkeeping into the artifact the pipeline consumes, which is precisely the separation CR-1 draws.

### 1.3 The rule that distinguishes them at load

The distinction cannot be made by looking at the value. A deliberately-empty array and an unanswered array both present as nothing; a deliberately-off feature and an unanswered feature both present as off. This is the same trap §6.4's third asymmetry names on the fact side:

> **Silence is not agreement, and unreadable is not disagreement.** A source that does not mention a fact reduces corroboration; a **failed fetch is recorded as "not observed", never as "the site disagrees"**.

The config analogue, and the governing rule of this section:

> **A blank field is recorded as "not answered". It is never recorded as "answered: none". The two are distinguished by the record of the answering act, never by the shape of the value.**

Mechanically, that means every knob in the **resolved form** carries a **provenance stamp** alongside its value, comprising three things: the **deciding layer** (which of the five last changed it), the **authorship class** (affirmative / inherited / declared-empty), and the **resolution timestamp**. A knob without a complete provenance stamp is itself a defect, and is asserted as such (CFG-RA-18), because without provenance every other assertion in §3 degrades into guesswork about a value that looks fine.

The provenance stamp does three jobs at once and is cheap enough to be worth all three. It makes the trichotomy evaluable. It makes the CR-2.2 readback able to say *which layer decided*, not merely what was decided. And it makes visible the failure class nobody can currently see: **an answer that changed nothing** — the operator set a value at the theme layer that a per-destination override later replaced, or wrote guidance outside a layer's write set, and has no way today to discover the edit was a no-op. §5.3 returns to this, because it is the one genuine reduction this design makes in the R-35 surface.

### 1.4 Why an unanswered Tier-A field can never degrade into an empty one

CR-5 defines Tier A as "the questions where no default can be correct because the answer is the tenant's identity". That definition carries the whole argument, but it is worth writing out, because the pressure to degrade will be real: a half-filled config that produces *something* feels better than one that produces a readiness failure, and every implementer who has ever shipped a form has felt that pressure.

**An empty answer to an identity question is not a safe generative state. It is a false one.** The difference is that a resolved-empty *fact* tells the generator something true and useful — "you have zero approved proof points, write teaching-led content" — and the generator behaves correctly on that information. A silently-emptied *identity knob* tells the generator nothing and tells the operator nothing, and the system's behaviour on it is coherent, complete-looking and wrong. Three worked cases, each grounded in a rule the design already holds:

- **Watch topics silently emptied.** The topic array becomes the empty set. Every collector runs. The topic-relevance filter (`05` §5.3) retains nothing, correctly. Ranking runs on nothing, correctly. Zero candidates is correct behaviour by design (`00_MASTERPLAN.md` §7 criterion D), so no assertion fires, no gate trips, no exit class is unusual. The theme produces nothing, forever, at full operational health. This is `RISK_LOG.md` W4-12's silent-language failure generalised to the whole tenant.
- **Hard excludes silently emptied.** §6.5's fifth unattended degrade trigger already refuses this on the fact side: "**Hard excludes are unresolved** — again, not empty, unresolved. You cannot enforce 'never say X' without knowing X." The config side must refuse it at load, which is strictly earlier and strictly cheaper than refusing it at 3am.
- **Designated fact locations silently emptied.** Every blocking class becomes unreadable, the band gate fails, and the run degrades to research-only every single night — a fail-closed outcome, so nothing unsafe is published, but the operator receives a degrade notice whose named cause is a fact-resolution failure when the actual cause is an unfilled form field. A degrade that misnames its own cause is a degrade the operator will learn to ignore.

The rule, therefore:

> **The Tier-A no-degradation rule.** For a Tier-A field, the empty answer is either *not in the field's answer domain at all*, or admitted only as a **declaration** — a named, dated, operator-authored statement of the form "this tenant has none of X, and I accept consequence C" — which is carried as a banner in every run digest until it is cleared or expires. There is no third path. Silence never becomes a declaration by the passage of time, by a run needing a value, or by any layer's default.

This is not a new instrument. It is §13.2's **language-completeness declaration** — *"the Czech product page does not exist; degraded Czech CTAs are accepted until date D"* — generalised from one field to the whole Tier-A set. §13.2 already gives the reason it must be a dated declaration rather than a state: *"week one it is a noted state, week eight it is the background."*

### 1.5 A consequence worth naming: after CR-5, `unanswered` is almost a Tier-A-only state

CR-5 abolishes the "no engine default" cell: "**Every row that today reads 'no engine default' is reassigned to Tier A or given a real default. No row may remain without one.**" Take that seriously and a pleasant property falls out. A Tier-B knob always has a real default, so it can never be unanswered by inaction. A Tier-C knob is not in the authoring form at all, so it can never be unanswered by omission. Therefore **the only knob that can be unanswered by never having been answered is a Tier-A field** — which is precisely the set whose failure messages the operator can act on directly, because each names one of about ten questions rather than one of a hundred and thirty settings.

The property is *almost* total, and the exception is the bridge to §4. A knob of any tier can become unanswered by **drift**: a registry version changes and the member the default named no longer exists; a substitute fact class is withdrawn; a destination profile is retired. Orphaned-by-drift and never-answered are both `unanswered` in the resolved form, and both are failures, but their messages and their fixes are different — one says "answer this", the other says "the thing your config pointed at is gone". The reason class travels with the state.

---

## 2. The layer resolution algorithm, stated once and totally

### 2.1 The order

Per CR-6, and not restated anywhere else in the annex set:

> `engine floor → playbook → theme (resolved) → language overlay → per-destination override`

### 2.2 The procedure, normatively

Resolution is a **left fold over the five layers, per knob, under the knob's declared regime**. It runs once, at config load, and produces the resolved form the pipeline consumes.

1. **Precondition — the registry must be complete before the fold begins.** For every knob the resolved form will carry, the engine registry must state: the knob's regime (one of the four in §2.3), its **scope** (engine / playbook / theme / language-formal / destination), its **strictness ordering** where the regime is monotonic, and its **identity rule** where the regime is additive. CR-6 is explicit that "a knob whose regime is unstated is a defect." Resolution does not proceed on an incomplete registry and does not fold a knob it cannot combine — this is the one place where the readiness report stops at first failure rather than aggregating, because everything downstream of an incomplete registry is fiction.

2. **Enumerate contributions.** For each knob, collect the ordered sequence of layer contributions. Each contribution carries its layer, its authorship class (affirmative, or declared-empty), and the registry version it was authored against. A layer that did not answer contributes nothing; that absence is recorded per layer, not merely inferred from the final value, because the readback must be able to say *"you did not answer this; the playbook did."*

3. **Seed the accumulator from the engine floor.** The engine floor always contributes, by CR-5. A knob whose engine-floor contribution is absent is a registry defect caught at step 1, not a resolution outcome.

4. **Fold, layer by layer, in order.** Each later contribution is combined into the accumulator under the regime's combination rule (§2.3). Two things are recorded at every step: whether the accumulator changed, and — where the regime refused the contribution — a **refusal record** naming the knob, the attempting layer, the scope of the attempt, the floor value and the attempted value.

5. **Do not stop on refusal.** A refused contribution leaves the accumulator unchanged and the fold continues, so that a single load reports every violation in the config rather than the first one. The config does not thereby become acceptable: any standing refusal is a readiness failure (CFG-RA-9, CFG-RA-10). Continuing the fold is a diagnostic decision, not a tolerance decision.

6. **Check the write set at every contribution.** A layer may contribute only to knobs whose declared scope it is entitled to write (§2.4, §2.5). A contribution outside a layer's write set is not merely refused — it is a **containment violation**, which is more serious than a relaxation attempt, because it means the fold produced a value no layer was entitled to author and every value derived from it downstream is untrustworthy. Containment violations block the run (CFG-RA-11).

7. **Terminate and stamp.** After the per-destination layer, each knob holds a value, a deciding layer, an authorship class and a timestamp. A knob still holding no value is **`unanswered`** with its reason class attached (§1.2), and readiness fails naming it.

8. **Fingerprint.** The resolved form's version participates in the overlay fingerprint (CR-2.4), so a re-resolution is a fingerprint change and fires the regression gate.

### 2.3 The four regimes and what each does on conflict

| Regime | Applies to | Combination on conflict | Permitted direction | Behaviour when the contribution is refused |
|---|---|---|---|---|
| **Monotonic-tighten-only** | Tier-1 safety items — the engine floor of `00_MASTERPLAN.md` §3.1: the universal slop floor, the non-disableable check classes, hard excludes, negative-prompt layers 1–3, the AI-disclosure floor, the Prohibited-Outcome Gate, every fail-closed trigger, the publish gate, spend gating | The later value is accepted only if it is at-or-tighter on the knob's declared strictness ordering. Anything looser is refused | Tighten only, at every layer, without exception | A refusal record is written and the accumulator stays at the tighter value. Per CR-7 the resolver "refuses and names the floor. It does not tighten-instead-and-carry-on without saying so" — so the refusal is never silently absorbed |
| **Registry-selection** | Tier-2 genre-variable items — rubric bars, fail smells, hook bars, specificity expectations, voice genre, archetype and angle selections, ranking profiles, skill-bundle eligibility, fact-schema obligation levels | The later layer's selection replaces the earlier one, provided it names a registered member at the pinned registry version **and** that member is eligible under every earlier layer's declared eligibility set | Either direction. Strictness is **not** preserved here — `00_MASTERPLAN.md` §3.1 says so plainly: "Tier 2 is a relaxation surface", and its safety property is registry-closure plus per-variant calibration, not monotonicity | A non-member is **unmapped**, not a near-neighbour (CR-7). An ineligible member is refused naming the layer whose eligibility set excluded it, and is **not** silently downgraded to the earlier layer's choice — a silent downgrade would be the resolver choosing, which it may not do |
| **Additive-union** | Arrays declared additive: hard excludes, banned phrases and constructions, negative terms, do-not-mention entities, research-side excludes, the negative-prompt layer stack | Union across all contributing layers, order-insensitive, deduplicated on the knob's declared identity rule. No layer may subtract | Grow only | A layer expressing a removal is refused, naming the term verbatim. This is §6.4's first asymmetry as a config rule: "Any source saying 'never say X' wins permanently for that run. No precedence rule may *remove* an exclusion" |
| **Last-layer-wins** | The residual: operational knobs that can neither spend, publish, nor relax a threshold | The later value replaces the earlier outright | Any | None. But see the constraint immediately below |

**`Last-layer-wins` is the residual regime and is deliberately the smallest of the four.** Assigning a knob to it is a positive claim that the knob is safety-neutral in the sense of §10.1's own placement rule — *"anything that can spend money, publish, or relax a safety threshold defaults to the safe value"* — and that claim is recorded in the registry and asserted at readiness (CFG-RA-5) rather than assumed. The design's own history says this claim is wrong more often than expected: four knobs sat in the theme block describing a machine rather than a tenant (§10.4a), and submission pacing sat in a per-theme table while §10.5 already placed it at engine level, because "pacing that one tenant can loosen is not pacing".

**One rule for arrays that are not additive.** An array knob is declared either *additive* or *replace-whole*. Element-wise merging of a replace-whole array is forbidden, because it produces a value no layer authored: a per-language surface-form list half from the theme and half from an overlay is a list nobody wrote and nobody can review. Replace-whole arrays fold under `last-layer-wins` at whole-array granularity, and the readback prints the whole array with its deciding layer.

### 2.4 Why the language overlay sits *after* the theme — and what happens when they genuinely conflict

This is a real ordering question and deserves an answer rather than a restatement of the sequence.

**The ordering is not a claim about authority in general. It is a claim about what kind of statement each layer makes.** The theme makes claims about *this brand*: what it sells, what it will never say, how loud an offer may be, which destinations are on. The language overlay makes claims about *what is well-formed in this language*: the slop lexicon, register norms, the CTA phrase bank, on-screen-text conventions — and it is deliberately **shared across every theme in that language** (§3.4, §10.1, and §13.3 records that sharing as the concrete return on refusing to fold it into the theme).

Where the two appear to conflict on a linguistic-form knob, the conflict is almost always a **category error in the theme's answer**, not a genuine disagreement. The dominant real case: the operator writes guidance in English, the resolver applies it to both configured languages by inheritance, and the resulting Czech value is an English preference wearing a Czech label. The overlay sitting *later* is the thing that stops one tenant's English-shaped answer from silently degrading its Czech output. That is the same protection D-02 exists for, and putting the overlay before the theme would hand every tenant a private veto over the shared Czech investment that theme #1 paid for and theme #2 inherits.

**But that argument only justifies the ordering for linguistic form. It does not justify letting an overlay override brand substance — and that is where the real ruling is needed.** The ruling is that the overlay's *position* is late and its *write set* is narrow, and the second is what makes the first safe:

> **The language overlay's authority is bounded by knob scope, not by position.** It may contribute only to knobs the registry marks **language-formal** — knobs whose value is a statement about *how* something is said. It may never contribute to knobs marked **brand-substantive**: the offer catalogue and status, the pain-to-offer relation, brand-and-domain routing, next-step class enablement, destination enablement, budgets, cadence, mode, the publish allowlist, designated fact locations. An overlay contribution touching a brand-substantive knob is a containment violation (§2.2 step 6) and the registry entry that permitted it is a defect.

So the ordering only ever *bites* on knobs where the theme authored a linguistic-form value — and there it should bite, because a single brand's opinion about Czech idiom is worth less than the shared overlay every Czech-writing theme depends on.

**The one genuine collision that survives, and its ruling.** The theme and the overlay meet on a shared object: the **literal CTA wording per language**. The theme carries it because §6.3 makes it fact class F-E — "literal phrasing per language" — and CR-4 makes it an array that is "used verbatim… never rewritten, expanded or reinterpreted". The overlay carries a CTA phrase bank because that phrase bank is exactly what a shared language overlay is for.

Ruling: **the theme's literal wording wins, and the overlay may flag but never author.**

- Where the theme carries a wording for that language, it is used verbatim. The overlay's phrase bank does not substitute, does not normalise, and does not "improve".
- Where the theme carries none for that language, the overlay's phrase bank supplies the value, and the readback says so, so the operator knows they are shipping a shared phrase rather than their own.
- Where the theme's wording is present and the overlay's conventions score it as non-idiomatic, the correct output is a **readiness warning naming the phrase and the language** — never a substitution, and never a silent one.

The shape of that ruling is deliberately the same as §6.4's second asymmetry, "the site can subtract but never add." The overlay can *flag* a brand fact; it can never *author* one. A layer that could rewrite a CTA wording could rewrite a hard exclude by the same mechanism, and CR-4 gives the reason that must never happen: "a compiler that paraphrases a hard exclude has removed a hard exclude."

**The cost of the late position, named honestly.** Because the overlay resolves after every theme, an overlay edit changes the resolved form of *every* theme in that language. It is therefore a fingerprint change for all of them, it fires the regression gate for all of them (`00_MASTERPLAN.md` §6 T5: the gate fires on any fingerprint change at any layer), and it re-opens the CR-2.2 readback for each. The overlay's late position buys correctness and costs blast radius. At one tenant that cost is invisible; at five it is the reason overlay edits should be batched rather than continuous.

### 2.5 What happens when a per-destination override would relax a Tier-1 item

Three things, and the first is the one implementers get wrong.

**It is refused, and the refusal is not silently converted into a tighten.** CR-7 is unambiguous: the resolver "refuses and names the floor. It does not tighten-instead-and-carry-on without saying so." The accumulator stays at the floor — that part is obvious — but the *record* is the point. A resolution that quietly clamps the value and reports success produces an operator who believes their setting is in force and a system behaving differently, which is the most expensive kind of disagreement because nothing is visibly wrong.

**The consequence is: blocks scheduling, permits interactive.** This follows §13.2's standing rule directly — "A theme failing readiness may still be run interactively in test mode, which is how a new theme is built up. It may never be scheduled." An interactive run proceeds with the floor in force and a digest banner naming the refused relaxation, so the operator watches the consequence of the thing they asked for rather than being told nothing happened. Blocking the run outright would be over-strict: the floor is enforced either way, so the interactive run is safe, and refusing it would remove the only cheap way to see what the floor costs.

**The per-destination layer's write set is bounded.** It may contribute only to destination-scoped knobs: format-profile selections, minimum mapping distance (§6.9), next-step class enablement per destination, per-destination length and caption constraints, per-destination review depth. It may never contribute to a knob whose scope is theme-wide or language-wide — a destination override may not change the language array, the budgets, the fact-schema profile or the publish allowlist. And **a destination override that tightens is accepted, recorded and shown in the readback**, because tightening one destination while leaving another looser is a legitimate and common operator intent — a stricter disclosure treatment on a short-form destination, a stricter minimum mapping distance on a peer-community destination.

### 2.6 Three worked examples

**Example 1 — an additive union: banned phrasing.**

Four layers contribute. The engine floor contributes the universal slop floor's forbidden constructions. The playbook (B2B lead generation) contributes its genre-negative set — layer 3b in the negative-prompt stack (`03` §7.3). The theme contributes this brand's own do-not-say list. The Czech language overlay contributes the Czech slop lexicon. The per-destination layer contributes nothing.

The resolved value is the union of all four, deduplicated on the knob's declared identity rule (normalised surface form, per language). Three behaviours are worth stating because each is a decision:

- Every retained member carries **the layer that introduced it**, so when a gate blocks an asset the digest can say which layer's constraint fired. A block whose origin is unnameable is a block the operator will argue with.
- Where the theme's list repeats a phrase already in the engine floor, the duplicate collapses and the **earlier** layer is recorded as the origin. A later duplicate is not a new constraint and must not be presented as one — otherwise a readback shows the operator "you added 12 banned phrases" when they added two and re-typed ten.
- Where the theme attempts to *remove* an engine-floor construction — expressible in the authoring form as guidance like "it's fine for us to say X" — the attempt is refused, the term is named verbatim, and the union is unchanged. The union may only grow.

**Example 2 — a registry selection where two layers select different variants: voice genre.**

The playbook (B2B lead generation) selects the analytical-B2B genre variant. The theme's authoring guidance resolves to a different registered variant — warmer, more conversational. Registry-selection is bidirectional and registry-closed, so **the theme's selection wins** and the resolved genre is the theme's.

Three things are then simultaneously true and all three must be recorded:

- The readback names **both**: *"the playbook selected analytical-B2B; your guidance selected \<the other registered variant\>; the second is in force."* CR-2.3 requires exactly this visibility — "a one-word change in a guidance paragraph that silently flips a voice genre must be visible."
- The selected variant's **calibration state travels with it**. `00_MASTERPLAN.md` §8 caps v1 calibration at two genres and states that the rest are "design-complete with flag-rate ceilings recorded inactive". If the theme's variant is one of the uncalibrated ones, readiness prints that its flag-rate ceiling is inactive and the digest repeats it every run. It does not hide behind the fact that the selection was legal.
- **Selecting a genre never selects out of the floor.** If the chosen variant's bars would relax a Tier-1 item — a non-disableable check class, the disclosure floor, the Prohibited-Outcome Gate — that part is refused under example 3's rule while the genre selection itself stands. Tier-2 is a relaxation surface for bars; it is not a route into Tier 1.

The variant of this example that fails: the playbook declares an **eligibility set** for genres, and the theme's selection is a registered member that is not in it. Then the theme's selection is refused as ineligible, naming the playbook and the eligibility set, and readiness fails. It is emphatically **not** downgraded back to the playbook's choice — a silent downgrade is the resolver picking a value, and CR-7 forbids the resolver from picking anything.

**Example 3 — an attempted relaxation that is refused: disclosure treatment on a short-form destination.**

The operator's per-destination guidance for a short-form destination asks for a less prominent AI-disclosure treatment, on the reasonable-sounding grounds that the burn-in hurts the composition. The knob's regime is monotonic-tighten-only; the AI-disclosure floor is Tier-1 (`00_MASTERPLAN.md` §3.1); the proposed value is looser on the knob's declared strictness ordering.

Resolution: the contribution is refused. A refusal record is written naming the knob, the layer (per-destination override), the destination, the floor value and the attempted value. The accumulator remains at the floor. The fold continues, so any other violations in the same config surface in the same load. Readiness then fails with a message carrying all five of those names, and scheduling is blocked. Interactive test-mode runs proceed at the floor with a banner, and the operator sees exactly what the floor looks like on that destination — which is the useful outcome, because the underlying complaint is a composition problem that the visual-first skill bundle's *"disclosure legibility measured rather than assumed"* emphasis (`03` §7.2) is the right place to solve.

Nothing here is silently tightened and forgotten, and nothing is approximated.

---

## 3. Readiness — the new assertions

### 3.1 Standing rules for these assertions

`03` §8 adds eleven readiness assertions and `05` §6.4 adds four. This section adds the **config surface's** contribution to §13.2. Where an assertion here strengthens an existing one rather than introducing a new check, it is marked **extends** and states what changed; the intent is that the merged §13.2 carries one statement of each check, not two.

**Three consequence classes, defined exactly.**

| Consequence | Meaning | Grounding |
|---|---|---|
| **Blocks scheduling** | The scheduler refuses. Interactive runs in test mode are permitted, which is how a theme is built up | §13.2's standing rule, unchanged: "A theme failing readiness may still be run interactively in test mode… It may never be scheduled" |
| **Blocks the run** | No run starts, in any mode, including interactive. Reserved for conditions under which there is nothing coherent to run *with* | Exits at an existing class from §8.8 — **policy-stop** where the config exists but may not be used, **hard-failure** where the artifact is absent or unreadable. No new exit class is introduced |
| **Warns** | A named digest banner on every run until cleared, escalating under the existing anti-flap rule (§6.5, §8.12). Never a gate | §12.1's banner mechanism, reused |

**Failure-message discipline, binding on every row below.** CR-7 states that "the failure message is part of the design and must be specified, not left to implementation." Four rules give that teeth:

1. **Name the field the operator recognises**, in the operator's language — the authoring-form question, not the resolved form's internal identity. An operator cannot fix a knob they have never seen.
2. **Name the layer** that produced the condition, which the provenance stamp (§1.3) makes possible. "This value is refused" is half a message; "this value is refused, and it came from your per-destination override on \<destination\>" is a whole one.
3. **Name a specific fix action**, in the shape §6.5 already demands of the brand-truth panel — "a *specific* fix action", not "confidence low".
4. **Quote operator text verbatim** wherever the condition concerns something the operator wrote — the unmapped span, the contradictory pair, the over-length brief, the offending numeric (CR-7, CR-8).

**Aggregation.** Readiness reports **all** failures in one pass, not the first. An operator who fixes one field per cycle across ten cycles does not finish. The single exception is the incomplete-registry precondition (§2.2 step 1), where continuing would produce fictional results.

### 3.2 The assertions

| ID | What it checks | What the failure message names | Consequence |
|---|---|---|---|
| **CFG-RA-1** | **A resolved form exists.** The theme has a resolved config artifact at all | The theme, and that its authoring form has never been resolved | **Blocks the run.** CR-2.1: "A run consumes an already-resolved config or refuses to start" |
| **CFG-RA-2** | **The resolved form is current.** Its recorded input fingerprint matches the authoring form's present content, field by field | Each authoring field edited since the last resolution, **by its operator-facing name** | **Blocks the run.** An out-of-date resolved form is a config the operator did not write |
| **CFG-RA-3** | **The resolved form is accepted.** An acceptance record exists naming the accepting person, the resolved-config version and the timestamp | The version awaiting acceptance, and the count of knobs whose value changed since the last accepted version | **Blocks the run.** CR-2.2: the resolved config "is inert until the operator accepts it". Auto-acceptance is never config-enabled, in any mode, mirroring §11.4's rule for approvals |
| **CFG-RA-4** *(extends `03` §8's first assertion)* | **Versions pinned, resolving and current.** Resolver version, every engine registry version, playbook version and language-overlay version are pinned in the resolved form; every pin resolves; every registry identity resolves *at its pin*; and the resolved form is inside its **recheck-by** window (§4.7) | The registry, the pin, and the identity that failed to resolve — or, for currency, the pin, the newer version available and the recheck-by date passed | **Blocks the run** where an identity dangles (selections no longer denote). **Blocks scheduling** where all identities resolve but the config is stale or past recheck-by |
| **CFG-RA-5** | **Every knob declares a regime**, exactly one of the four; and every knob assigned `last-layer-wins` carries a recorded safety-neutrality claim (cannot spend, publish, or relax a threshold) | The knob, and which of the two defects applies — no regime, or a neutrality claim absent or contradicted by the knob's own consumers | **Blocks the run.** CR-6 calls an unstated regime a defect, and a fold with no combination rule has no defined result |
| **CFG-RA-6** | **No knob is left `unanswered`.** After the fold, every knob is resolved-with-values, deliberately-empty or inherited | Each unanswered knob, its tier, and its **reason class**: never answered · unmapped, with the span quoted verbatim · contradictory, with both readings shown · orphaned by a registry change, naming the vanished identity | **Blocks scheduling** always. **Blocks the run** where the unanswered knob is Tier-A, or is an input to a §11.3 fail-closed trigger — hard excludes, publish allowlist, designated fact locations, or any knob declaring a required secret |
| **CFG-RA-7** | **Every Tier-A field is answered by an affirmative act** — not merely non-blank after inheritance. An empty payload counts only where the field admits a declaration and a live one exists (§1.4) | The Tier-A field by its operator-facing question, plus **the count still outstanding**, so the operator sees progress rather than one recurring mystery | **Blocks scheduling.** A theme under construction is exactly this state and must stay interactively runnable |
| **CFG-RA-8** | **Every deliberately-empty answer is a live declaration** — carrying an author, a date, the consequence the operator accepted in their own words, and, where the registry marks the field expiring, an unexpired date | The field, the declaration date, the expiry, and the operator's own consequence sentence read back to them | **Warns** while live — a banner on every run until cleared or expired, per §13.2's language-completeness instrument. **Blocks scheduling** once expired |
| **CFG-RA-9** | **No refused relaxation stands unresolved.** Every monotonic-tighten-only refusal recorded during the fold has been either withdrawn or accepted as refused | The knob, the attempting layer, the destination or language scope, the floor value, the attempted value | **Blocks scheduling.** Interactive runs proceed at the floor with a banner naming the refusal |
| **CFG-RA-10** | **No additive array carries a subtraction attempt.** Separate from CFG-RA-9 because the operator's fix is different — remove the removal, do not tighten anything | The array, the layer, and the term the layer tried to remove, verbatim | **Blocks scheduling** |
| **CFG-RA-11** | **Layer write-sets are contained.** No language overlay contributes to a brand-substantive knob; no per-destination override contributes to a theme- or language-scoped knob; no theme contributes to an engine-level knob (§10.5) other than through a logged Tier-C expert override | The layer, the knob, the knob's declared scope, and the value it tried to write | **Blocks the run.** A containment violation means the fold produced a value no layer was entitled to author; every value derived from it downstream is untrustworthy, and there is no safe subset to run |
| **CFG-RA-12** | **The brand brief is within bounds and clean.** Length cap per injection point measured **on the resolved form**; no numeric content, no client name, no proof-shaped construction; corpus-leakage check passes | The injection point, the cap and the measured length — or the offending span quoted back verbatim with its classification | **Blocks the run.** CR-8: rejected at config load, "never as runtime truncation", with the span quoted back |
| **CFG-RA-13** *(extends `03` §4.7 rule 3 and `03` §8)* | **Every node's resolved prompt fits its input ceiling — measured after resolution.** The extension is threefold: the measurement is taken on the **resolved** form at the **accepted brief contents**, per node × language × any destination whose override contributes to a prompt-bearing overlay; and it is re-taken on **every re-resolution**, not only at playbook load, because the brand brief is a contributor that did not exist when that rule was written | The node, the language, the overrun in the ceiling's own unit, **and the largest contributing injection point** — "N-5 overruns by X, largest contributor IP-4" is actionable; "N-5 overruns" is not | **Blocks scheduling.** In interactive mode the affected node cannot execute and its assets are held, which is a hold, not a truncation — `03` §4.7 excludes runtime truncation absolutely |
| **CFG-RA-14** *(extends `03` §5 rule 4 and `03` §8)* | **The criterion/fact-schema interlock holds on the resolved form.** Re-evaluated **after the fold**, because a theme-layer or destination-layer narrowing can demote a fact class below *constraining* after the playbook layer's interlock already passed. `03` §5 rule 4 asserts the interlock; this asserts it survives layering | The criterion, the fact class, the obligation level it now holds, and **the layer that demoted it** | **Blocks scheduling.** In interactive mode the criterion fails closed under §11.3's fifth trigger — a gate with nothing to check against is a gate that cannot execute — so the operator sees blocked assets rather than a silent pass |
| **CFG-RA-15** *(extends §13.2's destination assertion)* | **Every row of the operator-authored CTA table resolves, per configured language**, on five sub-conditions: the next-step class is registered and enabled for this playbook · the destination is enabled in the matrix for that language · a literal wording exists in that language, carried verbatim per CR-4 · the destination URL resolves at readiness time **and returns content in that language**, or a live language-completeness declaration covers it · **brand routing is coherent** — the row's destination domain matches the owning brand of the row's offer, so §6.9's wrong-brand-CTA defect is caught at load rather than only per asset | The row by its operator-facing label, the language, which of the five sub-conditions failed, and for a URL failure the URL and its response class | **Blocks scheduling** where a row is dead and undeclared — §6.4's "site wins absolutely" makes a 404 fatal to that CTA whatever the knowledge base says. **Warns** where the row is alive but degraded under a live declaration. Never blocks the run: §6.9 already handles a dead CTA at runtime by degrading the class |
| **CFG-RA-16** *(complements `05` §6.4, in the opposite direction)* | **Every topic entry reaches at least one source, in every configured language.** `05` asserts source-side coverage (surface forms exist; dry-run retention is non-zero per source). This asserts the **topic-side** mapping: for each topic × language, at least one enabled source can carry it — a steered source whose query profile has a field accepting that language's surface form, or a discovery source whose feed the topic filter can match against that topic's surface forms, aliases and entities | The topic's canonical name, the language, and **which shortfall it is**: "no steered source accepts this language" versus "no enabled discovery source this topic could match" — because the fixes are different | **Blocks scheduling** if *every* topic in a configured language reaches zero sources: that language will produce nothing forever, which is `RISK_LOG.md` W4-12's failure discovered at load rather than after weeks. **Warns**, with a named digest line, if some do — one unreachable topic is a normal state to iterate through |
| **CFG-RA-17** | **The resolved form participates in the fingerprint, and the fingerprint is consistent.** The resolved config's version is inside the overlay fingerprint (CR-2.4); the fingerprint recorded on the last accepted readback equals the one the run would compute now; the regression gate has fired and completed for the current fingerprint | The two fingerprints that differ, and the layer whose change produced the difference | **Blocks scheduling.** An un-regression-tested fingerprint may be run interactively — that is how it gets tested |
| **CFG-RA-18** | **Provenance is complete.** Every knob in the resolved form carries a deciding layer, an authorship class and a resolution timestamp (§1.3) | The knob missing its stamp, and which of the three parts is absent | **Blocks the run.** Without provenance the §1 trichotomy cannot be evaluated and every other assertion here reduces to guesswork about a value that looks fine |

**Eighteen assertions.** Four block the run unconditionally (RA-1, RA-2, RA-3, RA-5, plus RA-11, RA-12 and RA-18 — seven in total), two are conditional on what is missing (RA-4, RA-6), and the remainder block scheduling or warn. The distribution is deliberate: almost everything the operator can get wrong while building a theme leaves the theme interactively runnable, which is the property §13.2 identifies as the way a theme actually gets built.

---

## 4. Staleness and drift — the resolved config is not a static artifact

### 4.1 The governing principle

The resolved form is an artifact with a **fixed meaning** and an **ageing relationship to the world**. Those two properties need two different instruments, and conflating them is how config systems become either brittle or dishonest.

> **Pins protect the meaning. Readiness protects the relationship. Neither ever re-resolves by itself.**

A pin that never expires is a config quietly diverging from the engine. A re-resolution that happens automatically is the resolver authoring, which CR-7 forbids outright. The instrument that reconciles those is one the design already owns: **a recheck-by date on the resolved form**, in the exact shape of the vendor roster's "last-verified and recheck-by dates" (§10.2), where "a lapsed recheck drops a source to degraded and stops credit spend". A resolved config past its recheck-by blocks scheduling and permits interactive; it never auto-re-resolves; the operator's action is to re-resolve, read the diff and accept.

### 4.2 An engine registry version changes after resolution

**Detection.** At load, by CFG-RA-4. Also at run start, by the pin check before any stage executes — but registries are engine artifacts that change on upgrade, not during a run, so the case that actually occurs is *a run started after an upgrade and before re-resolution*, not a mid-flight change.

**Consequence, in two tiers.** If every pinned identity still resolves at the new version and no identity's semantics version moved, the config is **stale but valid**: blocks scheduling until re-resolved and re-accepted, permits interactive on the pinned versions. If any identity has vanished or its semantics version moved, the selections no longer denote: **blocks the run** at policy-stop.

**Never auto-migrate.** Silently re-pointing a dangling selection at a successor member is authoring, and the resolver has no authoring power. The orphaned knob becomes `unanswered` with reason class *orphaned by registry change*, naming the vanished identity, and the operator re-answers.

### 4.3 The resolver's model version changes

**Detection.** At load only. The resolver never runs per run (CR-2), so there is no run-time detection and there should not be one.

**Consequence.** The existing resolved form **remains valid and in force**. It does not become stale merely because a newer resolver exists — the resolved form is the artifact of record, and re-resolution is an operator action, not an obligation. This is deliberately more permissive than the registry case, and the reason is that a registry change alters what a selection *means* while a resolver change alters only how the *next* mapping would be made.

**Warns**, once per resolver-version change rather than on every run.

**The thing this pin actually buys.** When the operator does re-resolve, CR-2.3's diff must distinguish two kinds of change that look identical in the resolved form: an **operator-intent change** (the authoring text changed, the selection followed) and a **resolver-drift change** (the authoring text is byte-identical, the model version moved, the selection changed anyway). The second is CR-2.3's own nightmare case — "a one-word change in a guidance paragraph that silently flips a voice genre" — with the word unchanged and the machine having changed its mind. The two are shown in separate sections of the diff, because one is what the operator asked for and the other is what the system did on its own, and an operator scanning a merged list will read both as theirs.

### 4.4 A CTA destination 404s

**Detection.** At **both**. At load by CFG-RA-15; at run time by §6.6's targeted site verification, which already runs once per run "before anything is spent and before collection" and already covers "CTA URL liveness".

**Consequence at load.** Blocks scheduling, absent a live language-completeness declaration — §6.4 gives the reason with no room for interpretation: "F-E CTA destination liveness — Site wins absolutely — A 404 kills that CTA whatever Notion says."

**Consequence at run, mid-flight.** The existing §6.9 behaviour is unchanged and correct: that CTA degrades to a content class for the affected assets, and the pack says why. **The run continues.**

**This is the one non-fail-closed case in this document, and it is named as such and defended.** §11.3's mandate is that a run stops on missing secrets, ambiguous brand truth, or a policy violation. A dead CTA URL is none of the three. It is a fact resolving to a state for which the design already holds a defined safe answer, that answer degrades rather than fabricates, and stopping the run would discard already-paid-for research over a condition that costs exactly one next-step class on some assets. §6.5's own argument applies verbatim: "a system that cries wolf daily gets its alarms ignored or gets switched off — which is the real failure."

**What must not happen is the degradation becoming permanent and invisible**, and §13.2 already names that risk: "week one it is a noted state, week eight it is the background." So one addition: **a run-time CTA death writes a readiness-affecting record**, so the *next* config load fails CFG-RA-15 naming that row rather than the condition being rediscovered weekly by a degrade note nobody reads. The runtime stays soft; the load-time gate hardens behind it. That is the mechanism §13.2 asks for and does not currently have.

### 4.5 A topic array stops matching anything on any source

**Detection.** At run time, by the topic-relevance filter's retained-count (`05` §5.3), which already produces the diagnostic line — *"Google News CZ returned 87 items, 6 matched watch topics"*. At load, weakly, by CFG-RA-16's static reachability check and, more strongly but more slowly, by `05` §6.4's dry-collection assertion.

**Honest asymmetry, stated because it decides the design.** The load check proves a topic *could* match. Only run data proves it *does*. Neither substitutes for the other and both are cheap enough to keep.

**Consequence.** Never blocks a run — `05` §5.3 is explicit: "It never blocks a run and never manufactures volume." Warns, with a named digest line, escalating under the anti-flap rule. **Then, after a configured number of consecutive runs at zero retained for that topic in that language, the topic is marked `dormant` in the resolved form**, and dormancy is a *readiness* condition: it blocks scheduling until the operator either re-authors the surface forms or declares the topic dormant deliberately, with a date, under §1.4's declaration instrument.

That conversion is the point. A slow bleed becomes a dated decision. It is the same medicine `RISK_LOG.md` W4-12 prescribes for a thinning language, applied one level down at the topic.

**Mid-flight.** The run continues; the lane produces fewer candidates; "zero passing candidates is correct behaviour" stands (`00_MASTERPLAN.md` §7 criterion D).

### 4.6 Notion fact locations move

**Detection.** At run time only, and this is the important one: designated fact locations are *pointers* (§10.3, §6.2), so a moved or renamed location is **not a config edit**. Nobody touched the config. No authoring-side check can see it. It is detected by brand-truth resolution, which runs once per run "before anything is spent and before collection" (§6.6).

**Consequence.** Squarely §11.3's second fail-closed trigger. A blocking class that cannot be read is *unresolved*, not empty — §6.5's fourth degrade condition says it exactly: "**The claim ledger could not be read at all** — distinct from being empty. Unknown is not empty." The band gate fails and the run routes to **completed-degraded**: research-only output, zero brand content, zero media spend, stated in the digest.

**Mid-flight behaviour is bounded by design.** Because brand-truth resolution runs before collection and before any spend, "mid-flight" here means "at the earliest possible point", and no money is at risk when it fires. The research output remains complete and reusable, per §6.5's own requirement that a degrade never throws away the run's work.

**One addition, and it is a config-surface concern.** The failure message must distinguish a **pointer failure** (the designated location was not found) from a **content failure** (the location was found; the class is empty, stale or conflicted). Today both arrive as a resolution failure on that class. The fixes are entirely different — repoint versus populate — and the first is a config edit while the second is knowledge-base work that may belong to a different person. A pointer failure additionally writes a readiness-affecting record, so the next load fails naming the pointer: same instrument as §4.4.

### 4.7 The operator edits the authoring form but never accepts the readback

**Detection.** At load, by CFG-RA-2 and CFG-RA-3. At run start, by the same check.

**Consequence.** **Blocks the run**, in every mode, including interactive.

**Defence of that severity**, since it is the strictest rule here. The alternative is that the run consumes the last accepted resolved form while the operator believes their edit is in force. That is a silent no-op on a config change — the failure mode that destroys trust in the readback permanently, because after it happens once the operator can never again be sure that accepting meant anything. CR-2.1 and CR-2.2 between them leave no room: a run "consumes an already-resolved config or refuses to start", and the resolved config "is inert until the operator accepts it". An edited-but-unresolved form satisfies neither; a resolved-but-unaccepted form satisfies neither.

The severity is affordable because the remedy is one action and the readback already exists. What the operator sees: a message naming the edited fields, stating plainly that the last accepted resolved config is **not** in use and no run will occur, and offering the two exits — accept the new resolution, or revert the edit.

### 4.8 Detection timing and cron behaviour, in one view

| Drift | Detectable at load | Detectable at run | What a cron run does on discovering it | Fail-closed? |
|---|---|---|---|---|
| Engine registry version changed | Yes | At start only | Refuses to start (**policy-stop**) if any identity dangles; otherwise proceeds on the pins, with scheduling already blocked so this run is the last one | Yes |
| Resolver model version changed | Yes | Never — the resolver does not run per run | Nothing. The pinned resolved form is the artifact of record | N/A |
| CTA destination 404s | Yes | Yes, pre-spend | **Continues**, degrades that CTA to a content class, states it in the pack, and writes a record that fails the next load | **No — named exception, defended at §4.4** |
| Topic array matches nothing | Reachability only | Yes | Continues; digest line; dormancy after N consecutive zero-retention runs, which then blocks scheduling | N/A — not a safety condition |
| Notion fact locations moved | **Never** | Yes, pre-spend and pre-collection | Degrades to **completed-degraded**: research-only, zero brand content, zero media spend, cause named, research retained | Yes |
| Authoring edited, readback unaccepted | Yes | At start only | Refuses to start | Yes |

**Nothing here adds a sixth fail-closed trigger, and nothing here weakens the five.** §11.3's triggers stand unchanged in every particular. What this section does is move *detection* earlier — from run time to load time — for four of the six drifts, and add one deliberately soft runtime behaviour (§4.4) that hardens at the next load rather than at the next run.

---

## 5. Thin config — the degradation ladder, and the failure it cannot see

### 5.1 What a minimum config is

An operator who answers Tier A only: about ten authoring fields, hard ceiling twelve (CR-5), everything else inherited from the engine floor, the playbook and the shared language overlay. This must produce coherent output, or the tiering is decoration.

### 5.2 What is off, and why — the ladder

Nothing in the list below is a special case for thin configs. Each falls out of a default the design already holds, which is the test of whether the tiering works.

| What is off | Why | Grounding |
|---|---|---|
| **All scheduling** | Both cadence knobs default to off. The first state of any config is interactive-only, by construction | §10.1: "no scheduled run of any kind happens until the operator makes an explicit choice per theme" |
| **All publishing** | Mode defaults to test; in test the publish allowlist is empty by construction and publishing-bridge calls are refused before they are attempted | §10.1, §11.1, §7.4 |
| **All media spend** | Dry run defaults on for media generation in test mode, and that default is engine-level so a theme cannot weaken it. Plans and forecasts are produced; nothing is submitted | §10.1, §10.4a, §11.1 |
| **The event next-step class** | It has an unconditional fact precondition | §6.9: "**No event fact, no event CTA — ever.** A webinar CTA is a promise that an event exists" |
| **The commercial-incentive next-step class** | Requires resolved programme facts — a stated revenue share is a number and therefore a claim — plus the required disclosure statement | §6.9 |
| **The calendar/occasion lane and the evergreen/library lane** | Each requires its own populated register: a calendar with an entry intersecting the horizon, or a library whose depth over rest interval supports the cadence | `03` §8's trigger assertion |
| **The blog / site-first path** | Depends on product rules (F-K), which are blocking only when the blog is enabled, and on an article that can exist | §6.3, §6.9 |
| **Any licensed-vendor lane** | Reaches its engine-floor budget, which is deliberately small, rather than an unlimited one — because **an unanswered budget is never an unlimited budget**, and CR-5's rule that a knob with no possible default ships its feature *off* applies directly | CR-5; §10.2's per-source run budget |
| **Anything Tier-C** | Not in the authoring form, reachable only by an explicit logged expert override | CR-5 |

The shape of that list is the ladder: **a thin config is not a degraded config, it is a narrow one.** It produces fewer asset types on fewer lanes to fewer destinations, and every narrowing has a named cause the digest can state. That is a materially different thing from a config producing confident output on shaky ground.

### 5.3 What band to expect, derived rather than asserted

A minimum config answers Tier A, which includes the designated fact locations and the pain-to-offer relation. So the **blocking** classes can resolve and §6.5's Step 1 gate can pass. FULL, however, additionally requires "**every constraining class** in one of the two resolved states — never *unresolved*", plus every commercially binding fact observed this run or inside its warn window, plus zero conflicts of any severity.

That produces a distinction a new operator will not anticipate and should be told outright:

> **An empty-but-readable claim ledger is compatible with FULL. An unpointed or unreadable one is not.** §6.3's rule is the whole reason: resolved-empty is safe and unresolved is a failure, and on day one the difference between the two is whether the operator pointed at a location that exists, not whether they put anything in it.

**Expect PARTIAL on the first pack**, and expect it for a reason that is not a fault: the binding facts have not yet been observed against the live site in a run, and at least one constraining class will typically be unpointed on day one. At PARTIAL the tenant gets statement classes 0–2, with classes 3, 4 and 5 blocked, and next steps limited to the zero-commitment and destination-page classes (`03` §5.3). That is a coherent, publishable posture — teaching-led content with a content or destination next step — which is exactly what §6.3 says resolved-empty is *for*.

### 5.4 What the first review pack looks like

Interactive, test mode, dry-run media. Small. Concretely, it carries:

- the standard header with mode and a plain-language status line, plus the **two-line cost forecast** where the media line reads as forecast-only under dry run and the text line is the only real spend (§12.1, §5.4a);
- the **brand-truth panel**, one row per blocking class with state, source used, observation age and a specific fix action (§6.5) — on a first pack this is the most useful page in the document;
- **a per-asset spin-rationale line** (§12.1). This is not decoration: R-35 names it as the actual detection mechanism for a config that is wrong rather than broken, and §5.6 depends on it entirely;
- **per-topic completeness reasons** distinguishing budget-capped, count-capped and deliberately-held (§12.1) — on a thin config nearly everything absent will be *deliberately held*, and the operator needs to read that as design rather than as breakage;
- every **warn-level readiness item** as a banner: live deliberately-empty declarations with their dates, topics reaching no source, genre variants whose flag-rate ceiling is recorded inactive, and any language-completeness declaration;
- volume that is **small, and correct**. Zero passing candidates on a lane is correct behaviour and must not read as an error.

### 5.5 What the digest tells them to fix first

An ordering rule, not a list, and deterministic so that two consecutive runs give the same order:

1. **Anything blocking the run.** Nothing else matters until these clear.
2. **Tier-A gaps**, one line each, by the operator-facing question.
3. **Band-raising items, in the order §6.5's counting rule counts them**: unresolved blocking classes, then unresolved constraining classes, then binding facts outside their warn window, then recorded conflicts. This ordering is not arbitrary — it is the derivation of the band read backwards, so each item the operator clears moves the count they can see in the panel.
4. **Capability-unlocking items**, stated as consequences rather than as gaps: *"populate a dated event fact with a registration URL and the event next step becomes available on these destinations."*
5. **Warn-level drift**: expiring declarations, dormant topics, uncalibrated genre variants, a lapsed recheck-by.

And a hard cap: **the digest names at most the top handful, with the remainder behind a link.** A list of forty fixes is read as a wall and produces no action — which is W3-01's overwhelm failure recurring at the remediation end, after the eleven-decision minimum set already solved it at the authoring end. Solving overwhelm on the way in and recreating it on the way out would be a poor trade.

### 5.6 The opposite failure: a config that is complete, coherent and simply wrong

**What this design does catch.** Absence. Unmappability. Contradiction between two things the operator authored. Structural unreachability — a topic no source can carry, an archetype with no destination, a CTA row whose URL is dead or whose domain contradicts its offer's brand, a criterion with no fact class behind it. Refused relaxations and containment violations. Version drift, staleness and unaccepted edits.

And one class that is genuinely new here, worth claiming precisely because it is narrow: **the silent no-op**. An operator who sets a value that a later layer replaces, or writes guidance outside a layer's write set, or authors a Tier-1 relaxation that is refused, today has no way to discover the edit did nothing. The provenance stamp (§1.3) plus the readback's deciding-layer line makes that visible. That is a real reduction in the R-35 surface, and it is the only one this document claims.

**What it does not catch, stated flatly.** Every one of the following passes all eighteen assertions in §3:

- a pain-to-offer relation that is coherent, resolvable and mistaken;
- a next-step class that is enabled, live, brand-coherent and the wrong invitation for that audience;
- watch topics that match plenty of items, all of them the wrong items;
- an archetype mix that is well-formed, inside the engine band, and wrong for this brand;
- a voice genre variant that is registered, calibrated and not this brand's voice;
- a brand brief that is inside its cap, clean of numbers, names and proof, and says the wrong thing.

R-35 says it already and this document does not improve on it: *"There is no machine detection for 'this relation is coherent but mistaken', and there is not going to be one — the first pack is the test."*

**The compensating controls, with what each costs.**

| Control | What it actually catches | What it costs, honestly |
|---|---|---|
| **The CR-2.2 readback** | *Misunderstanding*, not mistakenness. It tells the operator the machine heard "warm and conversational" and selected variant V. It cannot tell them warm is wrong for their buyer | Cheap; fires on every edit; the only place prose becomes selections in front of a human |
| **The first pack read with the spin-rationale column open** (R-35's own named control, §12.1) | Mistakenness — the actual failure | One focused hour, once, and it is a **ritual, not a mechanism**. Nothing enforces it and nothing can |
| **Reason-coded rejection frequency** (§11.4, §12.4) | A systematic mis-mapping, as a cluster in the reason distribution, within a week or two | Needs a fortnight of packs **and** needs rejections to be reason-coded rather than batch-approved. §12.1 makes batch approval the default affordance, so **the default affordance actively erodes this control.** That tension is real and is raised as CFG-OD-3 rather than papered over |
| **The migration differential** (`00_MASTERPLAN.md` §7 criterion B; §6 below) | *Changes* to a previously-correct config | Says nothing at all about a config that was wrong from the first day |
| **Tier-A answer age** *(added here)* | Nothing, detectably — but it prompts. Every Tier-A answer carries its authorship date, so the digest can state how old each is and when it was last revisited | Cheap. A pain-to-offer relation authored eleven months ago and never revisited is not detectably wrong, but its **age is a fact worth printing**. Proposed as a warn-only recheck-by on Tier-A answers (CFG-OD-1) — a prompt, explicitly not a detector, and it must not be sold as one |

---

## 6. Migration of theme #1

### 6.1 What is being migrated

Theme #1 (HypeDigitaly) exists today as a §10-shaped configuration: the research block, the spin block and the output/runtime block, plus the publish allowlist per mode, the exemplar-corpus pointer per language, and the shared language overlay — roughly 130 settings, of which eleven are decisions and the rest inherit (§10.1). Roughly thirty of those rows currently read "Per theme; no engine default", which CR-5 abolishes.

The behaviour-preservation invariant governs absolutely: "the HypeDigitaly B2B lead-generation configuration must reproduce today's designed behaviour exactly. A tier assignment or default that changes theme #1's output is a defect of this work unless listed as an intended fix."

### 6.2 The migration, in four movements

**Movement 1 — freeze and fingerprint the reference.** The current §10-shaped configuration is captured as the **reference configuration** at a named version, together with the registry versions it implicitly assumes and the prompt and model pins in force. Nothing else happens until this exists, because behaviour preservation is a *comparison* and a comparison needs a left-hand side. A migration that begins by editing has already lost the ability to prove anything.

**Movement 2 — classify every knob, and resolve every "no engine default" cell.** Each existing knob is assigned a tier under CR-5 and a regime under CR-6. The ~30 cells reading "no engine default" each become either a Tier-A field or a real default. One rule governs the choice of default, and it is what makes the migration behaviour-preserving by construction rather than by luck:

> **Defaults are back-fitted from theme #1's current value wherever safety permits. Where safety does not permit — where the current value can spend, publish, or sit looser than the safe end — the engine default takes the safe value and theme #1 carries an explicit answer restoring its current one.**

The cost of that rule must be stated rather than absorbed: **the engine's defaults are then shaped by a single tenant.** The mitigation is not to pretend otherwise but to mark every default derived this way as **provisional-from-theme-#1** in the registry, and to name the moment it gets re-examined — the authoring of playbook #2's configuration, which is the first point at which a second data point exists (CFG-OD-7). This is registered as a debt, with its trigger named.

**Movement 3 — write the authoring form by answering, not by transcribing.** Two different treatments, and the split matters:

- The **free-text Tier-A fields are authored fresh**, as answers to the questions, not as transcriptions of the old structure's values. Transcription would reproduce the old surface's assumptions and would forfeit the only chance to discover whether the ten questions are actually answerable by the person who has to answer them.
- The **literal arrays are carried across verbatim**, with an equality check on the transferred contents. CR-4 makes them literal by rule — "the resolver may validate and normalise these; it may never rewrite, expand or reinterpret them" — so re-typing them would introduce error for no benefit, and the equality check is what proves none was introduced.

**Movement 4 — resolve, diff, classify, accept.** Run the resolver. Produce the CR-2.2 readback and the CR-2.3 diff. Then produce the **migration differential**: one row per knob in the resolved form, carrying the reference value, the migrated value, and for every difference a classification of *intended fix* (with a pointer to the `00_MASTERPLAN.md` §7 row or operator decision authorising it), *tier reassignment with no value change*, or **defect**. A single unclassified difference, or any difference classified as defect, blocks the migration.

### 6.3 How behaviour preservation is verified rather than assumed

Two comparisons. Both are needed, because neither is sufficient alone, and the reason each is insufficient is worth stating.

**Comparison 1 — resolved-form equivalence (static, complete over the surface).**

> For every knob in the engine registry, the value produced by folding the migrated authoring form through the five layers is **identical** to the value theme #1 holds today under the reference configuration — with the sole exception of knobs appearing in the migration differential classified as *intended fix*.

This is mechanical, exhaustive over the knob surface, and the strongest available form of the claim. Its pass condition is a single testable predicate: **the unexplained-difference set is empty.** Its honest limit is that it proves the *inputs* to the pipeline are identical, not that the pipeline consumes them identically — a tier reassignment that changes nothing about a value can still change when the value is read, or which layer may later override it. That limit is why comparison 2 exists.

This comparison is the **config-surface half of `00_MASTERPLAN.md` §7 criterion B**, and extends it rather than replacing it: criterion B demands one row per *engine decision point* theme #1 traverses; this demands one row per *knob*. Both are needed and they intersect at the knobs that feed decision points.

**Comparison 2 — frozen-eval-set replay (dynamic, decision-level).**

> The frozen eval set (§14.8) and theme #1's per-playbook eval set (`03` §4.5), replayed against the **migrated** config at the pinned model, prompt and registry versions, produce — for every item, in both configured languages — the same **gate verdicts**, the same **confidence band**, the same **spin-rationale tuple** (ICP segment · pain · offer · mapping distance · next-step class · owning brand and domain), and the same **asset-presence set**, as against the reference configuration.

Verdict-level, not byte-level, and that choice is deliberate. Generation is not deterministic; asserting identical output text would produce a test that fails for the wrong reason forever and is switched off within a month, which is worse than no test. **What must be identical is every decision. What may differ is wording.** Pass condition: zero differing verdicts, zero differing bands, zero differing spin-rationale tuples, zero assets present in one replay and absent in the other.

Run it in test mode with dry-run on, so the verification costs text tokens and no media spend, and charge that cost as a **config-time cost reported separately from run cost** (CR-2.5).

### 6.4 The acceptance criterion, stated testably

> **AC-CFG-1 — the theme #1 migration is accepted when, and only when, all five hold:**
>
> **(a)** Comparison 1's unexplained-difference set is empty.
> **(b)** Comparison 2 shows zero differences on verdicts, bands, spin-rationale tuples and asset-presence, across the whole frozen eval set and theme #1's per-playbook eval set, in **both** configured languages.
> **(c)** Every difference in either comparison that *is* explained appears in the migration differential classified as *intended fix*, with a pointer to the `00_MASTERPLAN.md` §7 row, the operator decision, or the named defect it closes. No difference is explained by prose alone.
> **(d)** The migrated resolved config has been accepted by the operator through the CR-2.2 readback, with the acceptance record naming the person and the resolved-config version.
> **(e)** The regression gate has fired on the new overlay fingerprint and passed.
>
> Failing any of (a)–(e), the migration is **not done** and the reference configuration remains in force.

**Rollback.** The reference configuration is retained for at least one full cadence period after acceptance, and the system can be pointed back at it. A migration whose only exit is forward is not a migration; it is a rewrite, and it removes the operator's ability to answer "was it better before?" with anything but memory.

---

## 7. Open questions — `CFG-OD-n`

| ID | Question | Recommendation |
|---|---|---|
| **CFG-OD-1** | **Do Tier-A answers expire?** §5.6 proposes a recheck-by date on Tier-A answers as an R-35 prompt. Does a lapsed Tier-A recheck warn only, or eventually block scheduling? | **Warn only**, at a deliberately long period, escalating under the anti-flap rule, never blocking. A blocking recheck on a config that is working produces exactly the alarm fatigue §6.5 warns against, and the control is a prompt rather than a detector — blocking on a prompt is not defensible. Revisit only if a production mis-mapping is ever found that a revisit would have caught |
| **CFG-OD-2** | **Who may accept a readback?** CR-2.2 requires human acceptance. In a solo-operator system the same person authors and accepts, so acceptance is a self-check whose value is attention, not independence. Is that sufficient, or does a Tier-1-touching change (a resolved relaxation refusal, a fact-schema profile change, a claim-pack change) require a second named person? | **Sufficient for v1**, stated as a limitation in the same register as R-35 rather than left implicit. Require the acceptance record to name the person and the resolved-config version now, so the audit trail already exists the day a second person does. Do not build a two-person rule that one person cannot satisfy |
| **CFG-OD-3** | **Should batch approval be narrowed to protect the rejection-reason signal?** §5.6 identifies a real tension: reason-coded rejection frequency is one of only two controls that detect a coherent-but-wrong mapping, and §12.1 makes batch approval the default affordance, which erodes it | Keep batch approval as the default — §12.1 is right that decision load is the binding constraint — but **present unselected** any asset whose spin-rationale tuple is new or changed for its ICP × pain pair relative to the last few packs. Low cost, and it targets precisely the assets whose rejection reason carries information |
| **CFG-OD-4** | **How long may a deliberately-empty declaration live?** §13.2's language-completeness declaration carries "until date D" with no stated maximum. May an operator declare a five-year acceptance? | **Cap the declaration period at one engine-level maximum** — a single value, engine-level per §10.5's placement rule and therefore not weakenable per theme. A declaration longer than the operator's own planning horizon is a permanent state wearing a date. The number itself is a §16-class open decision and is not set here |
| **CFG-OD-5** | **Does a newer resolver model version warn, or stay silent?** §4.3 recommends warning. The counter-argument is that a warning nobody can act on cheaply — re-resolution costs tokens and an acceptance cycle — is noise | **Warn once per resolver-version change**, not per run, and frame it as an offered action rather than as information. Note honestly that the genuinely useful form ("re-resolving would change N knobs") is computable only by actually re-resolving, so a cheap preview may not exist; if it does not, the warning states the version change and nothing more |
| **CFG-OD-6** | **Is `last-layer-wins` needed at all?** Every knob assigned to it carries a safety-neutrality claim, and this design's own history — four machine-scoped knobs in the theme block, submission pacing a tenant could loosen — suggests neutrality claims are wrong more often than expected | **Keep the regime.** Some knobs genuinely are neutral, and forcing them into a strictness ordering would be false precision that makes the other three regimes less meaningful. But require its assignment to be reviewed **as a set**, at the moment the per-knob table is authored, and require CFG-RA-5 to assert the neutrality claim rather than assume it |
| **CFG-OD-7** | **Do defaults back-fitted from theme #1 get re-examined, and when?** §6.2 accepts that the engine's defaults will be shaped by one tenant, and records it as a debt | Mark every such default **provisional-from-theme-#1** in the registry, and name the authoring of playbook #2's configuration as the trigger for re-examining the set as a whole. Cost it honestly: a second, smaller migration-shaped exercise, landing inside `00_MASTERPLAN.md`'s Wave 1.5 falsification rather than after it, where acting on findings is still cheap |
| **CFG-OD-8** | **Does the operator ever see the readiness report when it passes?** A report seen only on failure trains the operator to read readiness as an obstacle rather than as a description of what their config will do | **Always emit a report.** A passing report is one screen: the band it expects, the features currently off and why, the live declarations with their dates, and §5.5's fix ordering. This is also the natural home for the thin-config ladder, which is otherwise only legible after the first pack has already been produced |
| **CFG-OD-9** | **Is CFG-RA-16's topic reachability check static or does it require a dry collection pass?** The static check is cheap, deterministic and offline; the dry-collection evidence (`05` §6.4) is stronger but slower and network-dependent | **Static at load**, on every load, because it must be cheap enough to run constantly. **Dry collection on demand, and mandatorily before scheduling is enabled for the first time** — which is the moment the stronger evidence is worth its cost, and the last moment it is cheap to act on |

---

## 8. Where this lands

| Content | Target section |
|---|---|
| The three-state config trichotomy and the Tier-A no-degradation rule (§1) | §10.1, alongside the placement rules; cross-referenced from §6.3 as the config-side sibling of the fact trichotomy |
| The provenance stamp (§1.3) | §10.1; consumed by §12.1's digest and by the CR-2.2 readback |
| The fold, the four regimes, the write-set containment rule (§2.2–§2.3, §2.5) | §10.1 and the new config-surface annex; referenced from §5.3's resolution-algorithm precedent |
| The theme-versus-overlay ordering ruling (§2.4) | §3.4 (language overlay) and §10.1; the CTA-wording collision belongs beside §6.9's CTA-language-coherence rule |
| CFG-RA-1 … CFG-RA-18 (§3) | §13.2, merged with `03` §8's eleven and `05` §6.4's four; the consequence vocabulary belongs in §13.2's preamble |
| Staleness, drift and the §4.4 non-fail-closed exception (§4) | §11.3 (as a named exception that adds no trigger), §6.6 (targeted verification), §10.2 (recheck-by, by analogy to the vendor roster) |
| The thin-config ladder and the fix ordering (§5.2, §5.5) | §10.1's minimum-viable set and §12.1's digest contents |
| The honest R-35 statement and the compensating-control table (§5.6) | §15.2 R-35's mitigation and detection columns |
| The migration and AC-CFG-1 (§6) | `00_MASTERPLAN.md` §7 criterion B, as the config-surface half |
| `CFG-OD-1` … `CFG-OD-9` | `DECISION_LOG.md` open-decision block, in the `PB-OD-n` namespace's neighbourhood per CR-5's identifier ruling |
