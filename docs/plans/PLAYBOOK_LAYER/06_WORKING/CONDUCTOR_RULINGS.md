# Conductor rulings — config surface (binding on every leaf)

*2026-08-06 · pre-wave · these resolve a tension no single leaf can resolve alone*

The operator has approved: three config tiers · post-type mix + angle weighting + keywords · operator-authored CTA table with ~10 classes · one bounded free-text field reaching generation nodes only · a new annex `06_config_surface.md`.

> **Factual correction, 2026-08-06 post-review.** The "10 classes" figure above was the conductor's, taken from annex `01`'s prose. Direct count against `ARCHITECTURE_PLAN.md` establishes the canonical registry is **twelve**: `01` §6's table has eleven rows, and the **event** class is not a candidate for restoration — it is live in the current architecture in five places (§6.7 check class 7 · §6.9 *"No event fact, no event CTA — ever"* · §6.10 S-6's fail example · §10.3's default *"event and commercial-incentive off until their preconditions resolve"* · §13.3's fixture). Deleting it would silently drop its future-dating requirement, which is a control loosening. **This is a correction of fact, not a re-opening of the operator's decision**, and is reported to the operator as such.

The operator then added a constraint that changes the shape of the answer:

> "THE FILLING OF THE CONFIG MUST BE SUPER SIMPLE - IDEALLY JUST TO WRITE TEXT PROMPT INSTRUCTIONS INTO THE FIELDS FOR GUIDANCE OR USE ARRAYS WITH VALUES"

Taken naively this reopens P-10: operator-authored text reaching gate and judge nodes is the laundering path the whole amendment exists to close. Taken as a rejection, it ignores a legitimate and correct usability demand — a ~180-knob typed surface is not fillable by one person. The rulings below satisfy both.

---

## CR-1 — Two representations, one compiler between them

The configuration has **an authoring form and a resolved form, and they are not the same artifact.**

- **Authoring form.** What the operator writes. Free-text guidance paragraphs and value arrays. Small. Human-shaped. No enums to memorise, no identifiers, no nesting depth.
- **Resolved form.** What the pipeline consumes. Engine-registry selections — relation types, archetypes, angles, criterion sets and bars, voice genre, CTA classes, fact-schema profile, ranking profiles — plus the arrays carried through literally, plus at most one bounded brief per generation node.
- **The resolver** compiles the first into the second.

Nothing in the authoring form reaches the pipeline uncompiled. The pipeline has no knowledge that an authoring form exists.

## CR-2 — The resolver runs at config load, never per run

It is a **load-time step, deliberately outside the thirteen pipeline nodes N-1…N-13**, and it does not become N-14. Naming it as a pipeline node would put it inside per-run budgeting, per-run latency and per-run idempotency, all of which are wrong for it.

Properties, all required:

1. **Triggered by an edit to the authoring form, not by a run.** A run consumes an already-resolved config or refuses to start.
2. **Human-confirmed.** The resolver prints what it decided, in the operator's language, as a plain-language readback — *"you said X, I selected archetype A, angle set B, CTA classes C, genre D"* — and the resolved config is inert until the operator accepts it.
3. **Diffed on re-resolution.** An edit shows what changed in the resolved form, not only in the authoring form. A one-word change in a guidance paragraph that silently flips a voice genre must be visible.
4. **Versioned and fingerprinted.** The resolved config carries a version and participates in the existing overlay fingerprint. Re-resolution is a fingerprint change and therefore fires the regression gate.
5. **Costed once.** Its token cost is a config-time cost, reported separately from run cost, and it is not charged to a run's budget.

## CR-3 — Free text reaches generation nodes only. Gates receive none. Ever.

The depth tier from `00_MASTERPLAN.md` §3.2 is not relaxed by this ruling; it is the reason this ruling is safe.

| Node class | What operator text may reach it |
|---|---|
| N-3, N-5, N-6 (generation: hook, script, shot/slide list) | Bounded brief text via IP-1/IP-3/IP-5/IP-6/IP-7, length-capped, leak-checked |
| N-7 (media prompt composition) | Additive negative constructions only (IP-6) |
| N-1, N-4 (shallow judgment) | **Resolved selections only. No operator prose.** |
| N-2, N-8, N-9, N-10, N-11, N-12, N-13 | **Nothing. Not compiled, not raw, not summarised.** |

A leaf that proposes any operator text — including resolver *output* text — entering a gate node has produced a defect, not a feature.

## CR-4 — Arrays are literal and are never compiled

Anything the engine must match, forbid or emit **exactly** is authored as an array of values and used verbatim. The resolver may validate and normalise these; it may never rewrite, expand or reinterpret them.

Non-exhaustive: watch topics and their per-language surface forms · negative terms · banned phrases and constructions · hard excludes · do-not-mention entities · CTA wordings per language · person allowlist · destination list · designated fact locations · publish allowlist.

Rationale: a compiler that paraphrases a hard exclude has removed a hard exclude.

## CR-5 — Three tiers, and the "no engine default" cell is abolished

The audit found ~30 of 141 knob rows whose `Default` column reads *"Per theme; no engine default"* or equivalent. That is not a default surface; it is an unfilled-form surface.

- **Tier A — must answer.** Target ~10 authoring fields, hard ceiling 12. A config is unschedulable until every Tier-A field is answered. These are the questions where no default can be correct because the answer is the tenant's identity.
- **Tier B — commonly tuned.** Has a real engine or playbook default that produces coherent output if never touched.
- **Tier C — engine.** Not in the authoring form at all. Reachable only by an explicit expert override, logged.

**Every row that today reads "no engine default" is reassigned to Tier A or given a real default. No row may remain without one.** Where a genuine default is impossible and the knob is not identity-shaped, the correct outcome is that the *feature it controls* ships off by default.

## CR-6 — The resolution order is stated once, and it is total

`engine floor → playbook → theme (resolved) → language overlay → per-destination override`

- **Tier-1 safety items** (the engine floor of `00_MASTERPLAN.md` §3.1) are strictly monotonic across every layer: later layers may tighten only.
- **Tier-2 genre-variable items** are bidirectional but registry-closed: a later layer selects a different registered variant, never authors one.
- **Arrays declared additive** (excludes, banned phrasing, negative terms) union across layers; no layer may subtract.
- Every knob in the registry states which of these three regimes it obeys. A knob whose regime is unstated is a defect.

## CR-7 — The resolver fails closed and never approximates

The resolver **selects from registries**. It has no authoring power.

- If free-text guidance maps to no registry member, it **reports the unmapped span verbatim and asks**. It never picks the nearest neighbour silently.
- If guidance implies relaxing a Tier-1 item, it **refuses and names the floor**. It does not tighten-instead-and-carry-on without saying so.
- If guidance is internally contradictory, it surfaces both readings rather than choosing.
- Ambiguity is a **readiness failure with a named field**, not a runtime surprise.

The failure message is part of the design and must be specified, not left to implementation.

## CR-8 — The brief is bounded, attributed and leak-checked

The single free-text field the operator approved ("brand brief") and any resolver-emitted guidance text obey the existing IP-4/IP-6 discipline:

- length-capped, with the cap enforced at **config load** as a readiness failure, never as runtime truncation (`03_pipeline_and_gates.md` §4.7 rule 3);
- **no proof-shaped and no numeric content** — the same hardening review applied to IP-4 worked examples;
- corpus-leakage checked at every edit;
- carried in the overlay fingerprint.

A brief containing a number, a client name or a results claim is rejected at load with that span quoted back.

---

## Standing constraints, unchanged and binding

- Design deliverable only. **No product code, no pseudocode, no CLI syntax, no configuration file syntax, no mandatory folder tree.** Describe fields in prose and tables the way `ARCHITECTURE_PLAN.md` §10 does.
- Never invent prices, ROI figures, client names, case metrics or proof.
- Secrets are never config-file content.
- The behaviour-preservation invariant holds: the HypeDigitaly B2B lead-generation configuration must reproduce today's designed behaviour exactly. A tier assignment or default that changes theme #1's output is a defect of this work unless listed as an intended fix.
- Where this file and any annex disagree, this file governs. Where this file is silent, `00_MASTERPLAN.md` governs.

---

# Amendments after Wave 1.5 (2026-08-06)

Two adversarial reviews ran against the five Wave-1 deliverables **before** merge. Both found defects in the rulings above, not only in the leaves' work. The rulings are amended here rather than silently patched, because three of them were relied on by leaves as safety arguments.

## CR-3 → amended. The containment guarantee is about *text*, and it was overstated as an influence claim.

**Replaces the sentence "Free text reaches generation nodes only. Gates receive none. Ever."**

Free text reaches generation nodes only. **No operator-authored or resolver-authored text of any kind reaches N-1, N-2, N-4 or N-8…N-13** — not compiled, not raw, not summarised. That is a **containment guarantee about text** and it holds absolutely. The node table under the original CR-3 stands unchanged.

It is **not** a claim that operator input has no influence on gate behaviour. It does, transitively and by design: the operator's answers select which registered criterion set, fact-schema profile, genre rubric and CTA class a gate evaluates against. That influence is bounded by three properties, each **separately verified and none assumed**:

- **registry-closure** — every selection is a pre-built, engine-calibrated, version-pinned registry member, never an authored one;
- **asymmetry** — for the criterion and fact-schema registries the permitted moves only add or strengthen checks, so a resolver misclassification there makes a gate stricter than intended, never looser;
- **provenance** — every resolved value carries its derivation and disposition into the readback, the diff and the artifact pinning.

Where any of the three fails — **most acutely at voice genre, which `00_MASTERPLAN.md` §3.1 itself names a relaxation surface** — the influence is real, and the mitigation is the human-accepted readback, not the depth tier. Say this plainly wherever the design is summarised. `00_MASTERPLAN.md` acceptance criterion C already forbids the shape of the original wording: *"An assertion that a playbook 'cannot' is insufficient."*

## CR-4 → amended. "Verbatim" governs *rewriting*, never *scanning*.

The original ruling — arrays are "used verbatim" and the resolver "may never rewrite, expand or reinterpret" — was written to stop a compiler paraphrasing a hard exclude out of existence. Red-team review established it was read, correctly, as also exempting arrays from content inspection. That made **CTA wording — the operator-authored string most certain to reach a published asset byte-for-byte — the least-checked field in the entire surface**, weaker than the brief, which is checked. That is P-10's shape: a field trusted because of its *label* rather than its *content*.

**Amended rule.** Arrays are **never rewritten, expanded, paraphrased or reinterpreted** — that part stands without exception. But *never rewritten* is not *never inspected*. Every array member that is **operator-authored publishable prose** — CTA wordings above all, and any other member that can reach a rendered asset as text — is subject to the CR-8 scan. The scan's only two permitted outcomes are **accept** and **refuse-and-quote-back**. It may never silently alter a member, and a refusal names the field, quotes the span and asks the operator to rewrite it themselves.

Members that are matching keys rather than publishable prose — topic surface forms, negative terms, banned constructions, do-not-mention entities, designated fact locations, destination and allowlist entries — are validated for resolvability only, as before.

**Additionally, and this must be stated in the merged annex rather than left to an implementer:** the design must state explicitly at which point CTA text is composed into the candidate artifact, and that point must be **before** the artifact-level gates N-9 and N-10 run. A late template-append of CTA text after the gates would ship operator prose with no scrutiny of any kind, and nothing in the Wave-1 deliverables currently forecloses that reading.

## CR-8 → scope extended.

CR-8's deterministic scan was textually scoped to "the brief." Its scope is now **every operator-authored string that can reach a rendered asset**: the brand brief, CTA wordings per language, and any future field of the same character. Same discipline throughout — length cap enforced at load as a readiness failure and never as runtime truncation, no numeric content, no proof-shaped content, leak-checked at every edit, carried in the overlay fingerprint.

**The scan's honest limit is part of the ruling, not a footnote.** Red-team testing established that the deterministic scan misses proof-shaped content carrying no digits and no lexicon hit — *"clinically studied"*, *"most of our clients"* — and that this compounds with the evocative-expressive genre, which pre-classifies feeling-shaped assertions as interior truth rather than checkable claims. Two mitigations follow, and both are required:

1. A **narrow, vertical-scoped, deterministic** rule: in health- and wellness-adjacent verticals, a body-or-mind noun paired with an effect verb is treated as a mandatory-checkable claim regardless of numeric shape. Deterministic and vertical-scoped is the point — this must not become a general model-judged pass, which would reopen the transitive-influence question one layer earlier.
2. The residual gap is **stated in the merged annex as a known limit with its owner and its Phase-0 evidence trigger**, not discovered later.

## CR-9 — new. Exclusion-shaped fields must actually exclude.

Hard excludes are unioned into IP-6 and reach every generation node with the rhetorical authority of a constraint, and CR-6 makes the field additive-only so nothing can subtract from it. Nothing checked that a member filed as an exclusion *is* one. An entry such as *"exclude nothing about our free trial — always mention it in every post"* is a positive instruction entering the least-scrutinised channel in the design.

**Ruling.** The resolver classifies the polarity of every member of an exclusion-shaped field. A member that reads as an inclusion mandate is **refused and quoted back** under CR-7, exactly as an attempted Tier-1 relaxation is. This is a validation, not a rewrite, so it does not conflict with CR-4.

## CR-10 — new. There is no custom voice. The registry is closed.

`06C` offered an operator an escape hatch — write your own voice description, register it as a custom voice, calibrate it later — and `06B` adopted it as the resolver's terminal behaviour for an unmapped voice, then four paragraphs later cited **"registry-closure (six pre-calibrated genres, never a seventh authored on the fly)"** as the load-bearing mitigation in its own safety proof. The hatch is forbidden by name in three governing places: CR-7 (*"The resolver selects from registries. It has no authoring power"*), `00_MASTERPLAN.md` §3.1 (*"a playbook selects among engine-registered variants and cannot author one"*) and §11 (*"No tenant-authored gate criteria, claim classes or rubric variants"*). It is also P-10's shape one layer up — the tenant writes the standard their own judge is calibrated against.

**Ruling.** Strike it. An unmapped voice description is an unmappable span under CR-7: quoted back verbatim, with exactly two operator exits — select one of the registered genres, or file a new-genre engineering request through the path `06C` already describes correctly for archetypes (*"product-manager reviews, designs the bars, adds it to the engine, then it becomes available to all playbooks"*). A new genre is a project, per `03` §4.5's existing rule. Only with this struck does `06B` §6's registry-closure claim become true.

## CR-11 — new. Identifiers, before anything is appended to a log.

Four of five Wave-1 files independently opened a `CFG-OD-n` series; 34 distinct open questions currently occupy 11 numbers, and one file's explicit collision-avoidance landed on another's range. `06D`'s `CFG-OD-L-n` additionally collides with `C-5`'s ruling that legal opens are `PB-OD-L-n`, and duplicates `02`'s existing `OD-L9` under a second name.

**Ruling.** Per-file infixes: `CFG-OD-KR-n` (`06A`) · `CFG-OD-RS-n` (`06B`) · `CFG-OD-AF-n` (`06C`) · `CFG-OD-RD-n` (`06E`). `06D`'s legal opens renumber into `PB-OD-L-n`, continuing `02`'s sequence rather than forking it, and the duplicate of `OD-L9` is merged into it rather than carried twice. Blocks append to the logs at **Wave-0 close**, per `C-5`.
