# W8-11 OUTPUT-QUALITY OVERHAUL — IMPLEMENTATION PLAN

*Authored 2026-08-07 from `FINDINGS_SYNTHESIS.md` (14 analysis workstreams over confirmation run
`2026-08-07_fa51`) plus a full read of the engine. Revised the same day after a three-reviewer panel
(concurrency · prompt-design · code-quality), all approve-with-edits — every edit is folded in below.
Binding governance: `CODING_GUIDELINES.md` at repo root. Companion specs: `RENDER_CONTRACT_SPEC.md`,
`SLOT_MODEL_SPEC.md`, `COMPOSITING_SPEC.md`, `STYLE_SYSTEMS_SPEC.md`, `MULTI_MODEL_SPEC.md` — each
self-contained enough for an executor to implement from.*

*Amended 2026-08-07 (same day, second operator session) to integrate two approved spec amendments:
the `STYLE_SYSTEMS_SPEC.md` round-2 state (eleven style systems, two-stage Virlo-weighted selection,
serif vendoring, five anti-ad Hard DON'Ts, the diffusion-first logo policy) and the new
`MULTI_MODEL_SPEC.md` (side-by-side test harness on `gpt-image-2-text-to-image` + `nano-banana-pro`).
Operator decisions recorded in §13 rounds 2-3. New wave IV-B added; Waves 0-IV briefs extended in
place. Ground-truth API docs: `reference/kie-models/*.md`.*

*Reviewed again 2026-08-07 (architecture panel: conditionally executable — 5 blockers B1-B5, 8
assignables N1-N8, 29 redundancy findings R1-R29, 3 risks). All findings folded in: spec-side
corrections are encoded as Wave 0 task **0-6** (single documentation-engineer pass over the four
companion specs, before I-0 — Risk-3 mitigation: this plan does not silently diverge from specs it
cites); plan-side deletions/rewires applied directly below. Headline change: R1 collapses N-D to
photoreal scene slots only; all other diffusion surfaces become deterministic `templated_diffusion`.
Recomputed arithmetic in §9.3. §13 carries the review round.*

***AMENDED 2026-08-07/08 (operator-ratified after 44 live simulation renders across 5 rounds —
`simulation/SIM_REPORT.md`, findings F1-F19). Eight ratified changes, folded in below and recorded as
§13 items 19-20:*** *(A) **the rendering flip** — canonical creative rendering becomes
`gpt-image-2-text-to-image` FULL-DESIGN renders with styled expressive typography rendered in-image
(F9, F12); Pillow compositing is DEMOTED to the fallback rung of a QA-gated ladder (F18: ~5% Czech
display-type defect rate makes the per-glyph text gate mandatory, not optional); `nano-banana-pro`
becomes the canonical **specialist** route for `image_input` reference renders and, with
`nano-banana-2`, a test-track challenger. (B) **logos with every tool mention** (F8, F13) — a hard
coverage rule plus a per-tool manifest carrying a verbal mark description AND an icon-form PNG URL.
(C) the **three-tier unknown-tool ladder** with a runtime brand-asset fetch (F13-F15), browser
User-Agent mandatory on every HTTP fetch. (D) a **Czech-nativeness gate** on N-C/N-F. (E) **bilingual
CS/EN** as per-destination config (F12). (F) **accent-hex pinning + screens-off** guardrails (F10,
F11). (G) **four new "wilder" style classes** — `website_showcase`, `robot_caricature`,
`concept_dashboard`, `anime_scene` (F16, F17). (H) the **`brand_promo` class** — deliberately
promotional, exempt from the anti-ad Hard DON'Ts, outside the Virlo quota (F19). Doc-only
reconciliation is absorbed into Wave 0 task **0-6**; new implementation work lands as edits to
existing tasks plus the renamed `brand_assets.py` leaf. §9.3 arithmetic recomputed end-to-end.*

---

## 1. Overview (operator skim)

**What this is.** fa51 shipped 2 of 6 usable images. The other 4 came from an *ungoverned* fallback
prompt path that bypassed the claim gate and skipped vision QA entirely, and all 3 Instagram carousels
died before generating a single slide because two config sources disagreed about how many words a slide
may hold. W8-11 removes the second creative authority, makes the constraint set a single shared object,
turns Instagram into real multi-image carousels, gives trend evidence a mechanical link to the image,
and typesets all text-dense slides ourselves instead of asking a diffusion model to spell.

**Seven waves, in dependency order.**

| Wave | Theme | Lands |
|---|---|---|
| **0** | Deletion notification, **six** ADRs, NAVIGATION/CLAUDE.md, **spec reconciliation 0-6** (review blockers B1-B5 + the ratified-package sweep + stale-reference sweep, before I-0) | no engine code |
| **I** | **Shared contract + fail-closed ladder + de-cruft** — stops the bleeding | `render_contract` / `asset_model` / `fsutil` complete (incl. the `FALLBACK_COMPOSITING` state), `GovernedPrompt`, unconditional QA, browser-UA downloads, `compose_prompt` deleted |
| **II** | Prompts, voice, tokens, claim-gate co-location | institutional voice + **Czech-nativeness gate**, one constraint set in every prompt, token budgets by cardinality, N-E booleans incl. per-glyph `text_matches`, `logo_fidelity_ok` / `ground_standalone_ok` |
| **III** | Slot model + **conditional** carousels | evidence-gated 5-slot Instagram assets (single-image otherwise), per-slot state machine, slide-value gate, all-or-nothing delivery, config-authored `brand_promo` assets |
| **IV** | Virlo evidence link + **canonical full-design rendering** + compositing-as-fallback + **twenty-nine** style systems + two-stage selection + brand-asset pipeline | evidence-blocked generation, `gpt-image-2` full-design renders behind a per-glyph text gate, Pillow fallback rung, `style_select` quota/rotation/carousel-gate layer, `brand_assets` three-tier ladder, fonts vendored, version bump |
| **IV-B** | Multi-model test harness — **built and disabled** (`MULTI_MODEL_SPEC.md`) | `test_render.py` leaf, two `test`-tier **challenger** routes (`nano-banana-pro`, `nano-banana-2`) shipped `enabled: false`; registry two-door + reserved-route refusal + disabled-path tests. Zero spend at the default config |
| **V** | Docs + confirmation run | FLOW_MAP/ARCHITECTURE_PLAN amended, artifact republished, live run |

**Wave I is shape b:** a single barrier task builds the shared types **complete** (contract, slot model,
state machine, crafted-prompt shape, atomic writes, `trace.try_decision`) before anything fans out.
Every later wave consumes frozen types instead of designing them mid-flight.

**The one-paragraph root cause.** Four defects compound. **D1 (dual creative authority)** — the
copywriter's free-text `image_brief` was itself renderable via `compose_prompt()`
(`media_gen.py:229-241`, call sites `:1300`, `:1479`), so whenever the governed prompt failed
validation the ungoverned author won; 4/6 fa51 images shipped this way, carrying gibberish, literal
"EYEBROW TAG" placeholders and a gate-blocked "35,095". **D2 (constraint topology)** — hard constraints
lived in validators rather than in the authoring contract: `style_guide.yaml:93` told the copywriter
"60-90 words per slide" while `promptcraft.py:664` capped rendered bodies at 28 and the crafter had to
embed slide text verbatim, which is deterministically unsatisfiable and killed all three carousels.
**D3 (degrade-to-ungoverned)** — the spec's terminal rung is plan-only, but the implementation submitted
the ungoverned prompt and emitted no decision event, so the substitution was invisible in the trace
*and* documented as intended in `FLOW_MAP.md` §3. **D4 (evidence is decoration)** — the same-day
fetch-idempotency path never rebuilt `virlo_corpus.yaml` (`collectors/virlo.py:402-404,482-502`), so N-A
never ran, no `visual_profile` existed, and `_legacy_pick_archetype_register` hardcoded
`register="editorial"` at `promptcraft.py:425` while the run reported success. The fix is one idea
applied four times: **make the governed path the only path, and make every constraint, every gate and
every QA verdict unconditional.**

**The rendering flip (ratified 2026-08-08 on 44 live renders — §13 items 19-21).** The plan above was
written on the assumption that a diffusion model cannot be made to spell, so *we* typeset every
text-dense surface. The simulation falsified the premise for one specific model: across 5 rounds
`gpt-image-2-text-to-image` rendered dense, diacritic-heavy Czech display type with **one defect in
roughly twenty renders** (F18 — `ktery` lost its ý), and the operator's aesthetic verdict was
unambiguous: not one of the ten hand-picked favourites is a flat composited caption (F9, F12, plus
`reference/OPERATOR_FAVORITES_DNA.md`'s anti-signal list). So the canonical creative render becomes a
**FULL-DESIGN render** — expressive styled typography rendered in-image by
`gpt-image-2-text-to-image` — and Pillow compositing is demoted from "the only deliverable path" to
**the fallback rung of a QA-gated ladder**:

> `canonical full-design render` → **per-glyph vision text verification against the gated
> `on_image_text` strings** → *defect* → **one retry** → *second defect* → **composited fallback**
> (programmatic or `nano-banana-2` ground + Pillow text — the round-1 canonical, kept whole) →
> *composite unavailable / overflow / verification fail* → **copy-only**.

Fail-closed is unchanged: every rung is governed, every rung emits a decision event, and no rung is
reachable without the one before it failing. The 5% defect rate is exactly why the text gate is
**mandatory, not optional** — it is the mechanism that makes the flip safe, and the composited path
is exactly why the flip is reversible.

**Single-model production (operator decision 2026-08-08, §13 item 22.3).** `gpt-image-2-text-to-image`
is the **only active render model**. `nano-banana-pro` and `nano-banana-2` stay in the registry as
**reserved** routes — configured, documented, unreachable from any resolution path (the same
built-but-disabled pattern as `tiktok`, §13.4) — and the multi-model test track ships **built and
disabled** (`test_render.enabled: false`), so no test wallet appears in the active arithmetic. Two
consequences follow mechanically: the composited fallback's *ground* is a second
`gpt-image-2-text-to-image` render with **no text requested** and the slot's `reserved_text_zone`
honoured (the case-(b) flow `COMPOSITING_SPEC.md` already specifies), never a second model; and the
unknown-tool Tier 1 stops being an `image_input` reference render and becomes **a reserved artifact
zone rendered empty, with the fetched real assets composited into it pixel-exact by Pillow** — which
is strictly better integrity than F15's faithful-but-redrawn reference.

**No open operator decisions remain** — everything formerly blocking is resolved in §13 (Pillow, slot
count, fonts, tiktok, rounds 2-3, the ratified package, the favourites DNA). The one gate before
engine code is Wave 0 task **0-6**: the spec-reconciliation pass that clears review blockers B1-B5
**and applies the ratified-package sweep** inside the four companion specs before I-0 freezes the
shared types against them.

---

## 2. Governing documents & PRD status

`CODING_GUIDELINES.md` §1 makes the PRD the source of truth. **This repo has no `prd/` tree** (checked:
no `prd/`, no `docs/prd/`). The PRD-equivalent hierarchy in force here is:

1. `docs/architecture/ARCHITECTURE_PLAN.md` — the design contract (§4.2a, §5.3, §5.6, §11.3, §12.4,
   §14.3 are the sections W8-11 touches).
2. `docs/architecture/DECISION_LOG.md` — operator decisions, binding once recorded.
3. `docs/architecture/FLOW_MAP.md` — the live flow, plus the standing rule that its published artifact
   is re-published at the same URL on every flow amendment.
4. `docs/plans/GOAL_ROADMAP.md` — milestone state.

**PRD Amendment Proposal 1 — `ARCHITECTURE_PLAN.md` §5.6 + `FLOW_MAP.md` §3.**
*What:* delete the documented "ungoverned fallback prompt" rung; the terminal rung becomes
plan-only / copy-only, and the deleted `compose_prompt` path is named as removed. *Why:* the current
documents sanction the exact behaviour that produced 4/6 defective fa51 images — the code and the doc
agree with each other and both are wrong against operator-locked decision 3 (fail-closed).
*Affected code:* `media_gen.py:113-117, 229-241, 706-717, 1300, 1479`, `stages.py:850-851`.
*Approval:* covered by locked decision 3 in `FINDINGS_SYNTHESIS.md` §0; recorded in `DECISION_LOG.md`
by task V-3 (the code change is already authorised).

**PRD Amendment Proposal 2 — claim-gate qualification co-location.**
*What:* `_kvalifikovat_satisfied` (`claim_gate.py:141-145`) stops accepting a qualification marker found
anywhere in the asset and requires it in the **sentence containing the number**. *Why:* fa51's
unqualified "35,095" passed because "reported" sat three slides away. *Affected code:* `claim_gate.py`
only (task II-5). **This is a user-visible behaviour change: copy that passed the gate before may now be
blocked, and that is the intent.** It must be stated in the doc amendment, not slipped in. Deliberately
**no feature flag** — a flag would leave the weak path reachable; rollback is a one-file `git revert`.

Two governance notes:

- `CODING_GUIDELINES.md` §21 refers to `CLAUDE.md` §9/§9a and `NAVIGATION.md` at repo root. **Neither
  exists in this repo.** §21 *Orientation* obliges us to flag and fix a missing navigation doc — task
  **0-5** authors a repo-accurate `NAVIGATION.md` **first**, and each wave's conductor appends its new
  paths/config/commands in the same commit as that wave. The §9a spawn-topology triggers have no local
  source, so §6 restates them inline rather than citing a file that is not there.
- `docs/adr/` does not exist. §18 requires ADRs for non-trivial design decisions — task **0-3** creates
  the directory and the four ADRs this overhaul needs.

---

## 3. Reuse audit (`CODING_GUIDELINES.md` §2 — search before creating)

| Searched | Found | Decision |
|---|---|---|
| `grep -rn "compose_prompt\|_NEGATIVE_CONSTRAINTS" engine/ config/ docs/` | `media_gen.py:229-241` + 2 call sites; `process_summary.py:901-916,919-971`; `promptcraft.py:40-51` docstring; `config_load.py:663-670`; `config/themes/hypedigitaly.yaml:265` comment; tests | **DELETE everywhere.** Negative constraints already exist as `promptcraft.GUARDRAILS` (`promptcraft.py:85-89`) — one thing, one place |
| `grep -rn "MAX_BODY_WORDS\|_DESTINATION_CONSTRAINTS\|MIN_CAROUSEL_SLIDES"` | `promptcraft.py:664`; `copy_gen.py:829-848` (dead data — set, serialized, never read); `copy_gen.py:295` | **EXTEND into `ConstraintSet`.** Three parallel caps become one projection |
| `grep -rn "_QUOTED_SPAN_RE"` | `promptcraft.py:668` **and** an unaccounted twin at `media_gen.py:818` | **CONSOLIDATE.** `render_contract` owns the pattern; promptcraft adopts it; the media_gen twin is deleted |
| `grep -rn "run_claim_gate"` | producers `copy_gen.py:1131,1212`; `promptcraft.gate_check_prompts:982-1005`. **Never called from `media_gen.py`** | **EXTEND.** `render_contract.govern()` becomes the third caller — on the submitted bytes, not a preview |
| `grep -rn "visual_profile\|analyzed_items"` | produced `analysis.py:653-764`, consumed `stages.py:834-848` → `promptcraft.py:539-616,780-816` | **REUSE.** Wave IV adds `evidence_class`, does not rebuild the pipeline |
| `grep -rn "trace.decision"` | `trace.py:308-310`, free-text `decision`/`rule` pair | **REUSE** for all I5 events; add one sibling helper `try_decision` for except-block writes |
| `grep -rn "sha256\|atomic\|os.replace"` | `media_gen.prompt_sha256:244`, ad-hoc `yaml.safe_dump` writes in 4 modules, no atomic write anywhere | **CONSOLIDATE** into `fsutil.py` (5+ callers — §18 "extract when a second caller appears") |
| Existing image/text overlay code | none — `assets/fonts/README.md` documents an FFmpeg `drawtext` path for *video* only | **NEW module** `compositing/` — ADR-0002, §4 gate |
| Existing per-slot planning | `media_gen.plan_media_assets:656-718` already expands carousels 1:N | **EXTEND**, do not fork — the derivation flips from crafter-output to contract |
| Write-ahead ledger / idempotency / caps / leak checks / dedupe / banding | `store.py:150-186,1016-1182`; `media_gen.py:567-588,851-876,1366-1412` | **KEEP** — `FINDINGS_SYNTHESIS.md` §7 verified load-bearing |
| Test doubles for LLM + image provider | `collectors/base.FixtureFetcher:129-157`; `test_media_gen.QueuedFetcher:37-59` | **REUSE.** No new harness; no `conftest.py` exists and none is added |

**Round-2/3 addendum (2026-08-07, second session):**

| Searched | Found | Decision |
|---|---|---|
| Second image transport for the test harness | `KieClient` is the one transport; `_submit_new` the one `create_task` site | **REUSE.** `test_render.py` submits through the same `GovernedPrompt` choke point; `KieClient` unmodified except one `CREATE_TASK_ALLOWED_KEYS` entry (`"resolution"`) — `MULTI_MODEL_SPEC.md` §3.4 |
| HTTP fetch idiom for logo assets | `collectors/base.py` injectable `Fetcher` protocol over `urllib` | **REUSE the idiom.** `brand_assets.py` (round-3's `logo_assets.py`, renamed before it was built) takes an injectable fetcher (urllib default), offline-testable like every collector |
| Run-level selection / rotation | `pick_generation_mode` Phase-8 rotation (`promptcraft.py:444-581`) | **KEEP as the degrade path** (`STYLE_SYSTEMS_SPEC.md` §4.1 step 0 config gate + out-of-scope destinations). The two-stage selector layers above it in a new leaf, never replaces it |
| Ledger identity for per-model rows | `model_string` column already exists (`store.py:161`, populated since M4) | **EXTEND the UNIQUE only.** No new column, no backfill — guarded table rebuild widens the constraint (`MULTI_MODEL_SPEC.md` §7.2) |

**Ratified-package addendum (2026-08-08, rounds 4-5 + the favourites DNA):**

| Searched | Found | Decision |
|---|---|---|
| A second renderer for full-design canonical images | `KieClient` + `_submit_new` + `GovernedPrompt` — the same transport and the same single `create_task` choke point already carry every image request | **REUSE, no new transport.** The flip is a *route* change (`img-standard-gpt-image-2` becomes the canonical route) plus a prompt-builder change, not a new subsystem. `MULTI_MODEL_SPEC.md`'s capability fields (`full_text_render`, `resolution_constraints`, `image_input_max`) already model everything the flip needs |
| A retry/fallback mechanism for a failed render | `ATTEMPT_MAX = 2` + the existing attempt semantics + `resolve_render_route()` + the `composite-local` route from IV-7 | **EXTEND.** The ladder is `attempt 2` (existing) then the composite path (already being built as the canonical path in this plan) — zero new machinery; only the *order* changes |
| The composited path after the demotion | the whole `compositing/` package (IV-3), unchanged | **KEEP WHOLE.** Demoted, never deleted — it is the fallback rung AND the kill-switch destination. Cutting it would leave the flip irreversible |
| A logo/asset fetch helper before writing `brand_assets.py` | round-2/3's planned `logo_assets.py` (not yet built) + `collectors/base.py`'s injectable `Fetcher` | **RENAME + WIDEN, do not fork.** `logo_assets.py` becomes `brand_assets.py`: same module, same fetcher idiom, one extra responsibility (product visuals via `og:image`) that would otherwise become a second parallel fetcher |
| `image_input` plumbing | `MULTI_MODEL_SPEC.md` §4.6 recorded it as capability-present-but-unused | **STILL NOT BUILT** (operator decision 2026-08-08, §13 item 22.3 — single-model production). The capability field stays on the reserved `nano-banana-pro` route for a future re-enable; Tier 1 uses a reserved artifact zone + Pillow composite of fetched assets instead, which is pixel-exact rather than redrawn (F15) |
| A pixel-exact way to put a real logo/screenshot into a model-rendered card | `compositing.render_slot` + `LayoutRecipe.logo_zone` + the `reserved_text_zone` / `check_ground_safe_zone` flow (IV-3) | **REUSE, one new rect kind.** `artifact_zone` is `logo_zone` generalised to "a rect the model is told to leave empty and the compositor fills"; no second compositing path |
| A place for the new style classes | `style_guide.yaml`'s `style_systems:` map + `format_class` + §4's two-stage selector | **EXTEND.** New classes are new map entries + new quota keys; the selector is unchanged except for group expansion and the brand_promo reservation |
| A copy source for `brand_promo` assets | N-C (`copy_gen`) authors from trend evidence — structurally wrong for a service message | **NEW, but config-authored, not a second authoring node.** The rotation list lives in config; `copy_gen` builds the `CopyAsset` from it with **zero LLM calls**; the claim gate still runs. No parallel authoring system |

**No parallel system is created.** The only new modules are `fsutil.py`, `asset_model.py`,
`render_contract.py` (shared leaves with five consumers each), the `compositing/` package, and the
round-2/3/4/5 leaves `style_select.py`, `brand_assets.py`, `test_render.py` (each single-purpose,
wired by a conductor, never imported by the six giants).

---

## 4. Architecture-Change Gate (`CODING_GUIDELINES.md` §3)

1. **`compositing/` — a new deterministic rendering layer.** Condition: *current architecture cannot
   safely support the behaviour.* A diffusion model cannot be made to spell reliably; fa51 rendered
   lorem ipsum, "EYEBROW TAG" pills and a wrong CTA keyword into delivered artwork. ADR-0002.
2. **`RenderContract` — constraints move from validators into the authoring contract.** Condition:
   *change removes a duplicated system.* Three independent copies of the same caps collapse into one.
   ADR-0001.
3. **`GovernedPrompt` — a type that cannot exist without a passing gate.** Condition: *PRD requires it*
   (`ARCHITECTURE_PLAN.md` §5.6 terminal rung = plan-only) **and** the operator explicitly asked
   (locked decision 3). ADR-0001.
4. **Round-2/3 leaves `style_select.py`, `brand_assets.py`, `test_render.py`.** Condition: §3a — W8-11's
   new code goes into leaf modules rather than growing the six giants; each has one consumer surface
   (stage_copy selection · media_gen asset repair + tier ladder · stage_media test phase) and is wired
   only by a conductor. The test harness additionally isolates a genuinely new concern (test-tier
   submission, separate wallet, per-model identity) that must be structurally unable to touch
   delivery — ADR-0004.
5. **The rendering flip — canonical creative rendering moves from "composited by us" to "full-design
   rendered by the model, verified by us".** Condition: *the operator explicitly asked* (ratified
   2026-08-08 after reviewing 44 live renders and hand-picking 10 favourites), **and** *the current
   architecture cannot safely support the behaviour* the operator wants: expressive, oversized,
   emphasis-colored display typography integrated with the image is not reachable from a Pillow
   zone-typesetter at any reasonable cost. The failure mode the flip introduces (a ~5% Czech
   display-type defect, F18) is contained by a mandatory per-glyph verification gate and a fallback
   that is the *previous* canonical path kept whole. ADR-0005.
6. **`brand_assets.py` — a runtime HTTP fetch of third-party brand assets (logo + product visual) as
   an input to delivered creative.** Condition: *current architecture cannot safely support the
   behaviour.* F13 showed unaided marks for mid/long-tail tools come out as plausible **inventions** —
   indistinguishable from real to a casual viewer, which is strictly worse than obviously wrong. The
   only mechanism that makes a real product's depiction honest is real bytes fetched from the
   vendor's own site. This adds a new outbound-HTTP surface (allowlisted to the tool's own origin,
   GET-only, browser User-Agent, permanently cached) and a new integrity rule. ADR-0006.
7. **`brand_promo` — a deliberately promotional format class exempt from the anti-ad Hard DON'Ts.**
   Condition: *the operator explicitly asked* (§13 item 20). Gated structurally: the exemption is a
   per-system config list, only `brand_promo`-class systems may carry it, the exemption covers only
   §5.6-§5.10 (ad *aesthetics*) and never §5.1-§5.5/§5.11 (integrity), and consistency check 11
   refuses any organic system that claims one. No ADR — it is a content-policy dial inside the
   existing style-system machinery, recorded in `DECISION_LOG.md` by V-3.

**Explicitly NOT done** (fails the gate): splitting the six >500-line modules (`media_gen.py` 1757,
`store.py` 1296, `copy_gen.py` 1248, `stages.py` 1167, `collectors/virlo.py` 1166, `promptcraft.py`
1005) into feature-first submodules per §3a. Doing it *during* an overhaul that rewrites all six creates
merge hell for zero behavioural gain. Recorded as follow-up **W8-12** (task V-3). W8-11's own new code
goes into new leaf modules rather than growing the giants further.

---

## 5. Standing executor preamble (applies verbatim to EVERY task brief below)

> 1. **First action, no exceptions:** read `CODING_GUIDELINES.md` at the repo root **in full**, then
>    `NAVIGATION.md` (authored by task 0-5). They are engineering law and outrank this plan on every
>    general rule. If your context is compacted mid-task, read them again before resuming.
> 2. Read `docs/plans/w8-11-overhaul/PLAN.md` and every companion spec named in your task **in full**
>    (`CODING_GUIDELINES.md` §21: "if plans are attached or mentioned, subagents must always read them
>    fully").
> 3. **Stack reality — ignore any stack assumptions in your own agent definition.** This engine is
>    Python 3.13, **stdlib + `pyyaml` only**, SQLite via `sqlite3`, HTTP via `urllib` behind an
>    injectable `Fetcher` protocol, **fully synchronous** (no async, no ORM, no server, no migration
>    framework). Tests are plain pytest with `tmp_path` and no `conftest.py`.
> 4. **You own exactly the files listed in your task's path set. Touch nothing else** — not even a
>    one-line import in a sibling's file. If your change appears to need another file, stop and report
>    it as a wire-in request; the conductor applies it.
> 5. Do not create a parallel system. Search for the existing implementation first (§3); extend, don't
>    fork. Report why any new file was necessary.
> 6. Run the **full** suite before reporting — `cd engine && python -m pytest -q`, not just your own
>    test file. Your change can break a sibling's test.
> 7. End with the canonical report from `CODING_GUIDELINES.md` §20: Files changed / What changed /
>    What was wired in / What was reused / Tests-checks run / Dead code / PRD / Simple summary.
> 8. Output contract: lead with the conclusion, bullets over prose, cite `path:line`, no preamble.
> 9. Never pass a `model` override when spawning a child; agent frontmatter pins govern.

**Deletions require notification.** `CODING_GUIDELINES.md` §2: dead code is deleted, but the user is
notified first. Every deletion in this plan is pre-cleared by task **0-2**; an executor that discovers
*additional* dead code reports it and does not delete it.

---

## 6. Wave plan

**Wave shapes:** **a** — flat parallel leaves. **b** — shared-dependency barrier first (one task the
siblings *read*), then flat parallel leaves. **c** — flat parallel leaves, then the conductor writes the
aggregating files and applies the wire-in.

Per `CODING_GUIDELINES.md` §21 *Flat-wave first*: **every wave below is flat — leaf executors dispatched
directly by main. No orchestrating parent is used anywhere in this plan.** The three triggers that would
justify one (restated inline, since the `CLAUDE.md` §9a they normally live in does not exist here) are:
**(a)** decomposition unknowable up front; **(b)** ≥5 tasks in one domain in a single wave; **(c)** tasks
sharing a file, or a new shared module that must be *designed during the work*. Each wave below states
why none fired. Trigger (c) is neutralised structurally: the shared modules are designed and frozen in
task **I-0** before any fan-out.

**Spawn topology.** main → executor is one hop for every task. Only `agent-pipeline` holds the `Agent`
tool and may spawn read-only `Explore`/`hypeagent-explorer` children (depth 2). `python-pro`,
`prompt-engineer`, `test-engineer`, `documentation-engineer` and `ui-designer` are **leaves** and spawn
nothing. Soft cap 3, hard cap 5 — never approached.

---

### WAVE 0 — Notifications, ADRs, navigation, spec reconciliation

**Shape:** a. **Triggers:** none — three doc tasks + one notification, disjoint files, decomposition
known. *(R26: former tasks 0-1 (Pillow approval) and 0-4 (slot count) are DELETED — both decisions
were already answered by the operator, §13.2 and §13.1; their residue folds into 0-2. Numbering is
not reused.)*
**Barrier before Wave I:** 0-5 must land before any executor runs, since the preamble tells them to
read it; **0-6 must land before I-0** — I-0 freezes the shared types against the reconciled specs,
and 0-6's grep checks are the wave barrier. Wave I may start as soon as 0-5 and 0-6 land.

| Task | Executor | Depends on | Path set |
|---|---|---|---|
| **0-2** Deletion notification (+ record of already-made decisions) | **main → operator** | — | decision only |
| **0-3** Author six ADRs | `documentation-engineer` | — | `docs/adr/0001-fail-closed-render-contract.md`, `0002-deterministic-compositing-layer.md`, `0003-slot-model-and-true-carousels.md`, `0004-multi-model-test-harness.md`, `0005-canonical-full-design-rendering.md`, `0006-runtime-brand-asset-fetch.md` |
| **0-5** Repo navigation + governance docs | `documentation-engineer` | — | `NAVIGATION.md` (NEW, repo root), `CLAUDE.md` (NEW, repo root) |
| **0-6** Spec reconciliation (review blockers + stale sweep) | `documentation-engineer` | — | `docs/plans/w8-11-overhaul/RENDER_CONTRACT_SPEC.md`, `COMPOSITING_SPEC.md`, `STYLE_SYSTEMS_SPEC.md`, `MULTI_MODEL_SPEC.md` |

**0-2 — Deletions to notify.** `compose_prompt` + `_NEGATIVE_CONSTRAINTS` (`media_gen.py:113-117,
229-241`, pre-cleared by locked decision 3) and every stale reference to it (`process_summary.py`,
`promptcraft.py:40-51` docstring, `config_load.py:663-670`, `hypedigitaly.yaml:265` comment) · the
unreachable matched-terms veto (`ranking.py:276-277`, replaced by a one-line comment preserving intent
for a future model-backed `FitJudge`) · `MAX_BODY_WORDS` (`promptcraft.py:664`) ·
`_DESTINATION_CONSTRAINTS` (`copy_gen.py:829-848`) · `MIN_CAROUSEL_SLIDES` (`copy_gen.py:295`) ·
the `_QUOTED_SPAN_RE` twin (`media_gen.py:818`) · the "60-90 words per slide" prose
(`style_guide.yaml:91-93`) · `people_free_composition` in `config/model_registry.yaml` (contradicts the
W8-10 person policy) · `process_summary._find_image_brief` (`:901-916`) and `_reconstruct_prompt`
(`:919-971`) · `CraftedPromptSet.hero_prompt()`/`usable()` (`promptcraft.py:208-220`).
**R26 residue (folded from deleted 0-1/0-4):** the same notification records the already-made
decisions for the audit trail — Pillow ≥12,<13 approved as the compositing dependency (§13.2;
declined-fallback text is moot) and Instagram slot count = 5 **when the carousel format is selected**
(§13.22.2), `style_guide` amended to `slides: [5, 7]` (§13.1). No question is asked; these are
records, not requests.

**Ratified-package additions to the deletion notice (2026-08-08, §13 items 19-22).** Also notify, and
delete only with the same pre-clearance: `RenderPolicy.diffusion_text_max_spans` /
`diffusion_text_max_words_per_span` (already pending-deletion under R3 — they now die for the
*opposite* reason: the cap is **lifted**, not zeroed, because canonical prompts embed the complete
gated `on_image_text` verbatim, exactly as `MULTI_MODEL_SPEC.md` §4.2 already lifts it for test
prompts) · the R3 plan text "canonical N-E drops `text_matches`" (**reversed** — canonical N-E is now
the per-glyph text gate and `text_matches` is its central boolean) · every "logo library" /
"composited real PNG asset" residue superseded by the manifest schema change (§13.19.B) · the
never-built `logo_assets.py` module name (superseded by `brand_assets.py` before it exists — a rename
in the plan, not a code deletion). Nothing else joins the list; an executor that finds additional
dead code reports it and does not delete it.

**0-3 brief.** Standing preamble +: six ADRs in `CODING_GUIDELINES.md` §18 shape (context / decision /
alternatives / consequences), each ≤1 page, each linking the spec it records. 0001 = fail-closed render
contract + `GovernedPrompt` choke point (alternatives: keep the fallback but gate it; validator-only
enforcement). 0002 = compositing layer — Pillow vs headless Chromium vs FFmpeg drawtext vs status quo,
with the dependency cost stated. 0003 = slot model, true carousels, all-or-nothing at delivery
(alternative: variable-length carousels from crafter output). 0004 = multi-model test harness
(`MULTI_MODEL_SPEC.md`) — test-tier two-door route resolution, `model_string` joining the ledger
identity, separate $3 test wallet, test-renders-are-evidence-never-product (alternatives: a separate
test DB with no ledger; manual post-hoc model testing; testing in the delivery path behind a flag) —
**record that the harness ships built-and-disabled** (§13 item 22.3) and that the evidence which
would have justified it was instead produced by the 44-render pre-implementation simulation.
**0005 = canonical full-design rendering + the QA-gated fallback ladder** (`SIM_REPORT.md` F9/F12/F18,
`reference/OPERATOR_FAVORITES_DNA.md`): context = the operator's ten picks contain zero flat
composited captions and `gpt-image-2-text-to-image` renders dense Czech/English display type at a
measured ~5% defect rate; decision = model-rendered full-design canonical + mandatory per-glyph text
verification + one retry + composited fallback + copy-only; alternatives = keep compositing canonical
and accept the aesthetic ceiling · flip without a verification gate (rejected: ships the 5%) · flip
with unlimited retries (rejected: unbounded spend for a defect class retries do not reliably fix);
consequences = every slot becomes a paid render, QA reserve grows, the compositing package becomes
load-bearing as a fallback rather than as the primary path and therefore may never be deleted.
**0006 = runtime brand-asset fetch and the three-tier unknown-tool ladder** (F13-F15): context =
unaided marks for mid/long-tail tools are plausible *inventions*, which is worse than obviously wrong;
decision = fetch the tool's own `og:image` + `apple-touch-icon`/favicon with a browser User-Agent,
composite them pixel-exact into a reserved artifact zone, degrade through logo-only then explicitly
illustrative, never a diffusion-invented "real-looking" product screenshot; alternatives = a bundled
logo library (rejected round 2) · `image_input` reference renders (deferred with the reserved route —
redrawn, not pixel-exact, F15) · trusting the model (rejected: F13); consequences = a new outbound
HTTP surface with SSRF/allowlist obligations, a permanent on-disk cache, an optional operator-override
folder, and an integrity rule that is now an invariant (LG3). Create `docs/adr/`.

**0-5 brief.** Standing preamble (minus its own item 1 reference to this file) +: author `NAVIGATION.md`
from **today's** repo, before any W8-11 code exists — paths (`engine/src/hypeagent/`, `config/`,
`docs/architecture/`, `logs/runs/<run_id>/`, `assets/`, `secrets/`, `calibration/`), commands
(`python -m hypeagent` from repo root; `--resume`, `--summarize <run_id>`, `--render`, `--delete-key`;
`cd engine && python -m pytest -q`), secrets (`.env` / `OPENROUTER_API_KEY`, `secrets/kie.key`), the
doc hierarchy, and the project terms an agent needs (run pack, claim gate, N-A…N-F nodes, write-ahead
ledger). **N8:** also author the minimal repo-accurate `CLAUDE.md` §13.6 approved (what the engine is,
stack = stdlib+pyyaml+Pillow/SQLite/sync, non-negotiable invariants I1-I5, subagent notes, per the
`CODING_GUIDELINES.md` end-of-file template) — closing the gap that §21 references a `CLAUDE.md` this
repo does not have. Each later wave's conductor appends that wave's new paths and config keys.

**0-6 brief — Spec reconciliation (runs BEFORE I-0; single writer for all four spec files).**
Standing preamble +: apply the architecture review's spec-side corrections so I-0 implements against
reconciled documents instead of inheriting contradictions. Exactly these items, nothing else:
- **B1 — three-category slot routing.** Replace `diffusion_touched_slots()`'s two-field definition
  (`RENDER_CONTRACT_SPEC.md:130-133`) with three routing categories: **`llm_crafted`**
  (`ground_source: diffusion` scene slots — the photoreal systems; the only slots N-D ever sees),
  **`templated_diffusion`** (partial-area `logo_zone`/`photo_inset`/flat-ground covers — a
  deterministic template prompt built in promptcraft, NO N-D call), **`programmatic`** (no provider
  call). Wire `slot_has_diffusion_surface(slot, style_system)`
  (`STYLE_SYSTEMS_SPEC.md:768-777`) into the definition it feeds — one truth table, one consumer
  chain.
- **B2 — style system owns per-slot routing.** Per-slot `text_render_mode`/`ground_source` resolve
  from the STYLE SYSTEM ONLY; delete them from `generation.render_contract.<dest>.slots[*]`
  (`RENDER_CONTRACT_SPEC.md:409-431`). Add **consistency check 10**: every `style_systems[*].slots`
  role set must equal the destination's role sequence.
- **B3** — delete `RenderPolicy.composited_roles` (`RENDER_CONTRACT_SPEC.md:406`) — a redundant
  third declaration of the same routing fact.
- **B4 — check-6 arithmetic.** The QA-reserve denominator counts **vision-QA-eligible slots only**
  (composite-verified slots consume no vision call, `COMPOSITING_SPEC.md:646-656`). Recompute and
  state the number in the spec: worst case ≈ 10 eligible slots/run under the default quota
  (photoreal 5+2 scene slots + up to 3 partial-area templated surfaces) × `ATTEMPT_MAX 2` + logo
  repair re-QA ⇒ `qa_reserved_calls: 24` exactly covers; state it as derived, not padded.
- **B5 + R12 — one logo boolean.** `TextFidelityVerdict.to_qa_yaml_dict()`
  (`COMPOSITING_SPEC.md:588-601`) must emit `ui_fidelity_ok`/`ground_standalone_ok`/
  `logo_fidelity_ok`; fold `logos_ok` into `logo_fidelity_ok` EVERYWHERE (one boolean, one
  subject); delete the now-false "logos_ok: True by construction" claim.
- **R22 — govern once, submit twice.** `MULTI_MODEL_SPEC.md` §4: build + govern the test prompt
  ONCE per slot; submit the single `GovernedPrompt` to both routes — same-bytes becomes a
  structural guarantee (experimental validity), not a "may be byte-identical" aspiration.
- **N6/N7 — stale round-1 references, ALL of them:** `RENDER_CONTRACT_SPEC.md:104`, `:446-447`,
  `:450`; `COMPOSITING_SPEC.md:444` (Bold-weight system list), `:502`, `:766-768` (identity tuple).
  Also restate the §2.1 census sentence (`RENDER_CONTRACT_SPEC.md:143-147`, already once-corrected
  by the planner) under B1's three categories and the R2/R3 defaults (five fully-programmatic
  systems of eleven under the R3 default; four if R3 is vetoed; canonical diffusion-TEXT surface
  zero under R3).
- **R5/R6/R8 spec-side:** move the `BANNED_RENDERED_STRINGS` span-scan to N-C authoring
  (repairable, cheap point); delete `_FONT_NAME_RE` and `govern()` wiring point 2 of
  `_AD_BANNER_RE`; mark `_LOGO_INVENT_RE` as deleted-with-R1 (templated logo prompts are
  deterministic — authoring-time invention is impossible). **R7:** the register-keyed leak table is
  ONE shared function called from both validation and `govern()` step 4 — state it where the table
  is specified.
- **R29 spec-side:** merge the two `per_run_call_cap` formulas into ONE check owned by
  `RENDER_CONTRACT_SPEC.md` §4 check 8 (extended); `MULTI_MODEL_SPEC.md` §12 check 7 becomes a
  reference to it, not a second formula.
- **R3 REVERSED (§13 item 19.A).** R3's recommendation (zero canonical diffusion text) is dead: the
  canonical path now renders ALL text in-image. Delete
  `diffusion_text_max_spans`/`diffusion_text_max_words_per_span` outright — not "pending", and for
  the opposite reason (the cap is **lifted**, not zeroed) — and restore `text_matches` to the
  canonical N-E rubric as the per-glyph text gate. Leave a one-line tombstone at each former site
  naming R3 and its reversal so the record reads honestly.

**Ratified-package sweep (2026-08-08 — §13 items 19-22; same task, same single writer).** These are
doc-only reconciliations of the ratified package across the four companion specs. Exactly these:
- **Rendering-flip terminology, everywhere.** "canonical = programmatic/Pillow-composited" becomes
  "canonical = `gpt-image-2-text-to-image` full-design render; Pillow compositing = fallback rung".
  Sweep `RENDER_CONTRACT_SPEC.md`, `COMPOSITING_SPEC.md` (its §0/§2/§3/§6 all describe compositing as
  the primary path — **this spec was not amended by the planner and its reconciliation is entirely
  this task's**), `STYLE_SYSTEMS_SPEC.md` and `MULTI_MODEL_SPEC.md`. `COMPOSITING_SPEC.md` keeps
  every algorithm unchanged; only its *position in the ladder* changes, plus the two additions named
  below.
- **`COMPOSITING_SPEC.md` additions (no algorithm changes):** (i) the fallback ground for an
  `llm_crafted` slot is a **second `gpt-image-2-text-to-image` render with no text requested** and
  the slot's `reserved_text_zone` honoured — the existing case-(b) flow, single-model; (ii)
  `artifact_zone: RectPct | None` on `LayoutRecipe` — `logo_zone` generalised to "a rect the model is
  told to leave empty and the compositor fills pixel-exact" (unknown-tool Tier 1, D4's artifact
  devices); (iii) the QA-accounting subsection states that a composited image carries
  `qa.status = "composite-verified"` and consumes no vision call **because it was reached only after
  two vision-verified failures**, so invariant I4 is satisfied by the ladder as a whole.
- **Census restatement: eleven → twenty-nine style systems** (27 organic + 2 promotional), and the
  fully-programmatic census is **retired**: under the flip every slot of every system is a canonical
  render, and the three-category routing (B1) re-partitions as `llm_crafted` (scene/illustration
  slots needing a per-topic description) · `templated_diffusion` (recipe-determined cards) ·
  `programmatic` (**fallback and kill-switch only**). Every "N of eleven", "fully programmatic",
  "zero image-generation calls" sentence is restated under this partition.
- **The screens-off sentence (supersedes §13 item 18a's narrower wording task):** every photoreal and
  illustration template/N-D prompt fragment carries verbatim *"Every screen and monitor in the frame
  is OFF (dark glass) or angled away — never render any UI content."* (the live-verified wording from
  `simulation/round2/prompts/*5_scene_hook_styled*`, F11: 0/4 scene renders showed invented UI).
- **Accent-hex pinning (F10):** every template prompt states its own accent hex literal
  (`#302B87` indigo · `#00A39A` teal · `#E8A63B` amber-for-numerals-only); an unpinned prompt drifts
  to coral, which is Anthropic's trademark colour (§3.6).
- **`MULTI_MODEL_SPEC.md` role inversion + disable:** `gpt-image-2-text-to-image` is the canonical
  incumbent; `nano-banana-pro`/`nano-banana-2` are reserved routes and disabled test-track
  challengers; §4.6 (`image_input` out of scope) **stands, now permanently for W8-11**; §14's "what
  this spec does NOT change" gains "the canonical model — which this spec no longer names".
- **`assets/logos/manifest.yaml` schema change** propagated to every citation:
  `tool → {description, icon_url, source}` (§13 item 19.B).
- **Language:** every "Czech" assumption becomes "the asset's configured language"; the default is
  **`en`** (§13 item 22.1) with `cs` a supported switch. The Czech-diacritics QA instruction and the
  Czech-glyph font gate become **language-conditional**, retained in full, off the default
  confirmation run's critical path.
- **Carousels are conditional** (§13 item 22.2): every "5-slot Instagram carousel" statement becomes
  "single-image by default; 5-slot carousel only when the Virlo slideshow gate fires".

**Barrier greps (the wave gate):**
`grep -rn "four of (the )?six|logos_ok|composited_roles|_FONT_NAME_RE|_LOGO_INVENT_RE" docs/plans/w8-11-overhaul/*.md`
returns only tombstone/changelog lines that name the deletion;
`grep -rn "diffusion_touched_slots" docs/plans/w8-11-overhaul/*.md` shows the three-category
definition everywhere it is defined or consumed; and
`grep -rniE "eleven (style )?systems|fully programmatic|diffusion_text_max_(spans|words)|nano-banana-2 \+ Pillow[- ]composit|the canonical (nano-banana-2|composited) path" docs/plans/w8-11-overhaul/*.md`
returns only tombstone/changelog lines naming the flip.

---

### WAVE I — Shared contract, fail-closed ladder, de-cruft deletions

*Stops the bleeding: deletes the ungoverned submission path (D1/D3) and makes QA unconditional — the
mechanism that turned 4 defective fa51 images into shipped artefacts.*

**Shape:** b + c. **Triggers:** (a) no — decomposition fully known. (b) no — 2 build tasks. (c)
**neutralised**: the shared modules are designed and frozen in the barrier task I-0, not during the
fan-out. → **no orchestrating parent.**
**Barrier justification (§21 obligation 1):** I-1 and I-2 both *read* the types I-0 creates. That is a
real input dependency, the only kind that earns serialisation.

| Task | Executor | Depends on | Path set (touch nothing else) |
|---|---|---|---|
| **I-0** *(barrier)* Shared types, complete | `agent-pipeline` | 0-2, 0-5, **0-6** | `engine/src/hypeagent/fsutil.py` (NEW), `asset_model.py` (NEW), `render_contract.py` (NEW), `config_load.py`, `trace.py` |
| **I-1** Fail-closed submission + QA totality | `agent-pipeline` | I-0 | `engine/src/hypeagent/media_gen.py`, `engine/src/hypeagent/llm.py` |
| **I-2** De-cruft in untouched modules | `python-pro` | I-0 | `engine/src/hypeagent/ranking.py`, `process_summary.py`, and **docstrings only** in `copy_gen.py:136-138` and `promptcraft.py:841-843` |
| **I-3** Wire-in + registration | **main (conductor)** | I-1, I-2 | `engine/src/hypeagent/stages.py`, `config/themes/hypedigitaly.yaml`, `NAVIGATION.md` |
| **I-4** Tests | `test-engineer` | I-3 | `engine/tests/test_render_contract.py` (NEW), `test_asset_model.py` (NEW), `test_media_gen.py`, `test_stages.py`, `test_ranking.py`, `test_process_summary.py`, `test_llm.py`, `test_config.py`, `test_trace.py` |

**I-0 brief.** Standing preamble + `RENDER_CONTRACT_SPEC.md` and `SLOT_MODEL_SPEC.md` **in full**.
Everything this task produces is **frozen** for the rest of the overhaul — later waves consume, never
reshape.
- `fsutil.py`: `atomic_write_text`, `atomic_write_bytes`, `sha256_hex` (`RENDER_CONTRACT_SPEC.md` §1.1).
- `asset_model.py` **complete** (`SLOT_MODEL_SPEC.md` §2-§3): `SlotRole`, `OnImageText`, `VisualIntent`,
  `Slot`, `CopyAsset`, `SlotState` (all 13 states incl. `PENDING_EXTERNAL`, `SUBMITTED_UNKNOWN`),
  `TERMINAL`, `advance()`, `InvalidTransition`, `asset_deliverability()` (incl. `held_incomplete`).
  **Ratified-package addition (§13 item 19.A) — the render ladder is a state, not a flag.** `SlotState`
  gains a **14th** state `FALLBACK_COMPOSITING` and exactly two edges:
  `RENDERED --text_defect_after_retry--> FALLBACK_COMPOSITING` (reachable ONLY when the slot has two
  recorded failing text verdicts, or when `canonical_render_enabled` is false) and
  `FALLBACK_COMPOSITING --composite_verified--> DELIVERABLE`; a composite that cannot be produced or
  cannot be verified goes `FALLBACK_COMPOSITING --composite_failed--> BLOCKED_NO_IMAGE`. No edge
  reaches `FALLBACK_COMPOSITING` from `PLANNED`/`CRAFTED`/`GOVERNED` — the ladder's order is enforced
  by the state graph, not by an `if`. `advance()` raising `InvalidTransition` is what makes invariant
  **RL1** structural.
- `render_contract.py` **complete** (`RENDER_CONTRACT_SPEC.md` §2-§6): `CONTRACT_VERSION = 3`, every
  dataclass, `resolve_render_contract`, `ConstraintSet`, `check_contract_consistency` (all nine checks,
  each error naming **both** disagreeing sources), `GovernedPrompt`, `UngovernedSubmission`, `govern()`,
  `QUOTED_SPAN_RE`, and `deterministic_prompt_leak_check` **moved in from `media_gen.py:851-864`**
  (I-1 deletes the original and imports it back — import direction `media_gen → render_contract`).
- **Ratified-package additions to `render_contract` (§13 items 19-22).** `RenderPolicy` **loses**
  `diffusion_text_max_spans`/`diffusion_text_max_words_per_span` (0-6 deletes them spec-side: the cap
  is lifted, not zeroed) and **gains** `canonical_render_enabled: bool = True`,
  `text_qa_retry_max: int = 1` and `fallback_to_composite: bool = True`. `SlotSpec.text_render_mode`'s
  value set becomes `"full_design"` (canonical — the model renders the complete gated text in-image)
  | `"composited"` (the fallback rung, and what a `canonical_render_enabled: false` run uses for every
  slot) | `"none"`; `SlotSpec.ground_source` now governs the **fallback** ground only
  (`"programmatic"` = recipe ground, `"diffusion"` = a text-free `gpt-image-2` re-render honouring
  `reserved_text_zone`). `RenderContract` gains `language: str` semantics per §13 item 22.1 (the field
  already exists — its **source** becomes `generation.language_by_destination`, resolved server-side,
  never model-chosen) and `format: str` becomes an *evidence-gated* per-asset value (`"single"` |
  `"carousel"`, §13 item 22.2) rather than a per-destination constant, so `resolve_render_contract`
  takes the stage-1 `format` decision as an input alongside `VisualPolicy`.
- **Pin the crafted-prompt shape** (`SLOT_MODEL_SPEC.md` §5.1): `CraftedImagePrompt` and
  `CraftedPromptSet` as dataclasses **here**, so Wave III's copy-side and media-side tasks build against
  a frozen contract instead of one designed mid-wave. `promptcraft` adopts them in Wave II.
- `config_load.py`: the `generation.render_contract` / `require_visual_evidence` / `compositing` schema
  (`RENDER_CONTRACT_SPEC.md` §7, as reconciled by 0-6 — per-slot `text_render_mode`/`ground_source`
  are NOT in this schema, they resolve from the style system only, B2), following the
  frozen-dataclass + safe-defaults idiom of
  `GenerationConfig` (`config_load.py:537-553`) and its loader (`:556-651`); purge the `compose_prompt`
  reference at `:663-670`. **N3:** the schema also includes `generation.destinations_enabled`
  (list; absent ⇒ all configured destinations enabled — the pre-W8-11 truth), read at contract
  resolution so a disabled destination (tiktok, §13.4) is never planned, crafted or spent on; the
  value and the read wiring are IV-8's. **Write no YAML** — the schema is code; the values are I-3.
- **R7:** the register-keyed leak check is ONE shared function, defined here (pattern table passed as
  data), called from `govern()` step 4 and later from `promptcraft.validate_crafted_prompt` — two
  call sites, zero duplicate implementations.
- `trace.py`: add `try_decision(stage, *, decision, rule)` — identical to `decision` (`:308-310`) but
  wrapping the write in its own `except Exception: pass`. Every degrade event emitted from inside an
  `except` block uses it, so a failing trace write cannot escalate a degrade into a crash.
- **Territory invariants:** these are leaf modules — `asset_model` imports nothing from `hypeagent`;
  `render_contract` imports only `fsutil`, `asset_model`, `claim_gate`, `config_load`. Every existing
  `GenerationConfig` field keeps its default so a theme predating W8-11 still loads.

**I-1 brief.** Standing preamble + `RENDER_CONTRACT_SPEC.md` §6/§8, `SLOT_MODEL_SPEC.md` §3/§7.
- **Delete** `compose_prompt` (`:229-241`), `_NEGATIVE_CONSTRAINTS` (`:113-117`), both call sites
  (`:1300`, `:1479`), the `_QUOTED_SPAN_RE` twin (`:818`), and the local
  `deterministic_prompt_leak_check` body (`:851-864` — import it from `render_contract`). A hero/slot
  plan with no crafted prompt becomes `BLOCKED_NO_IMAGE` with a decision event and **no ledger row**
  (no spend). `deterministic_qa_text_leak_check` (`:867-876`) stays — it is post-QA, not submission.
- `_submit_new` (`:1465-1524`) accepts a `GovernedPrompt` and passes `governed.text` to the single
  `create_task` call site (`:1493`). `MediaGenerator.__init__` gains **required** `claim_snapshot` and
  `hard_excludes` — a generator that cannot gate cannot be constructed (I2).
- **Ledger prompt-sha guard** (`RENDER_CONTRACT_SPEC.md` §8 guard 4): in `_submit_or_resolve`'s
  existing-row branch (`:1286-1291`), compare `existing.prompt_sha256` with the current
  `GovernedPrompt.prompt_sha256`; mismatch → `BLOCKED_NO_IMAGE` + `trace.decision` ("identity exhausted,
  no re-submission"), asset closes `copy_only`. **Do not widen the UNIQUE key in this wave — and never
  widen it by prompt content** (that would authorise unbounded re-spend). The single approved widening
  is by `model_string`, landing in Wave IV task IV-1 per `MULTI_MODEL_SPEC.md` §7; Waves I-III run on
  the narrow v3 tuple.
- **Phase-0 quarantine** (`SLOT_MODEL_SPEC.md` §7.2): `_resolve_one_row` (`:1137-1172`) gains the
  ordered branch set — composite-local first, then quarantine on version / not-in-plan / sha mismatch.
  Quarantined rows **settle their money exactly as today** (spend reconciliation untouched) but download
  to `logs/runs/<run_id>/adopted_prior_version/`, never `pack_media_dir`, write no pack provenance, and
  emit a decision event. Without this, the first W8-11 run imports ungoverned W8-10 images into a W8-11
  pack unreviewed. **Risk-1 mitigation — write the FINAL ordered branch list as a comment block at the
  top of `_resolve_one_row`, which later tasks extend in place, never reorder:**
  ```
  # _resolve_one_row branch order (FINAL — extend, don't reorder):
  #   1. route_id == "composite-local"      -> local deterministic re-render   (IV-7)
  #   2. route resolves to tier "test"      -> skip; TestRenderRunner adopts   (IV-B-1)
  #   3. version / not-in-plan / sha mismatch -> quarantine adopted_prior_version/ (I-1, this task)
  #   4. normal provider resolution (query by task_id, settle)                 (existing)
  ```
  I-1 implements branch 3+4 and the comment; IV-7 and IV-B-1 fill their slots above it.
- **Extract `_settle_intent(row, *, image_path, checksum, qa, observed_usd, final_state)`** — used by
  both `_complete_success` (`:1575-1638`) and, in Wave IV, the composite render path. The only
  differences between those callers are: no `create_task`, no `check_caps`, different `route_id`.
  Existing-row idempotency and the prompt-sha comparison live **inside** the shared helper so the two
  paths cannot drift.
- **QA totality:** delete the `qa_expected_text=None ⇒ skip` coupling (`:706-717` esp. `:712`,
  `:1010-1011`); text-conditional booleans skip individually while subject / logo / composition /
  gibberish always run; reserve QA budget **before** submission (`GOVERNED --qa_budget_unavailable-->
  BLOCKED_NO_IMAGE`), and if budget vanishes after the image is paid for and rendered, the slot is
  **HELD_QA**, never auto-delivered (`SLOT_MODEL_SPEC.md` §3).
- **Browser User-Agent on the result-CDN download (§13 item 19.C, empirically forced).** The
  simulation's first collector run failed to download finished images: the kie result CDN returns
  **403 to a bare `urllib` User-Agent** (`simulation/collect.py` exists only because of this; the
  same 403 hit `lovable.dev` in round 3). The image-download call in `media_gen` must send a browser
  UA. One header on one request — but without it, every canonical render in W8-11 pays for an image
  it cannot fetch. Put the UA string in one module constant reused by `brand_assets.py` (IV-11); do
  not spell it twice. **Named acceptance test:** `test_result_download_sends_browser_user_agent`.
- **Expose rollup counters** on `MediaStageResult`: `image_count`, `vision_eligible`,
  `vision_qa_successes`. `media_gen` does **not** compute the stage outcome — that is I-3's job.
  Under the flip `vision_eligible` counts **every canonical render** (all of them carry text), not
  just the old diffusion-touched subset; composite-fallback images are excluded (they are
  `composite-verified`, and they were only reached through two vision-verified failures).
- `llm.py`: add `qa_headroom() -> int` — an additive read-only method returning QA calls still
  reservable (`per_run_call_cap`/`qa_reserved_calls` arithmetic already in `_check_budget`). One method,
  no behaviour change; the token-budget work is Wave II.
- `PROMPT_PATTERN_VERSION` (`:91`) becomes `= CONTRACT_VERSION` — an alias, never an edited literal.
  **It does not bump in this wave** (§9.6).
- **Territory invariants:** write-ahead order (ledger row before `create_task`, `:1481-1493`); the
  identity tuple and `asset_slot` format (`:641-647`, `store.py:182`); `ATTEMPT_MAX = 2`; caps and
  circuit breaker (`:567-588`, `:1366-1412`); spend reconciliation (delta sum == ledger == balance).
  Never widen `create_task` to a second call site. Add a one-line comment at the per-day spend read
  (`:1318`) recording that its correctness depends on `run_identity.RunLock` serialising runs.

**I-2 brief.** Standing preamble +:
- `ranking.py`: delete the unreachable matched-terms veto (`:276-277`) leaving a one-line comment for a
  future model-backed `FitJudge`; fix fit-score granularity (`:159-179`) so distinct candidates stop
  tying at 0.426 and falling back to insertion order — weighted overlap ratio, or reduce `fit` to
  gate+band only. **Do not touch the freshness window** (Wave IV, task IV-4).
- `process_summary.py`: delete `_find_image_brief` (`:901-916`) and `_reconstruct_prompt` (`:919-971`) —
  they exist only to re-compose the deleted fallback. Read the actually-submitted prompt from the slot
  provenance YAML (`prompt_full`, `media_gen._write_provenance_yaml:1697-1758`) instead.
- Docstring-only corrections: `copy_gen.py:136-138` (`response_shape_expected` still says "people-free",
  contradicting the W8-10 person policy) and `promptcraft.py:841-843` (claims `analyzed_items` is "not
  yet wired"; `stages.py:834-848` wires it). **Docstrings only in those two files — no logic, and do
  not touch `_QUOTED_SPAN_RE` at `promptcraft.py:668`** (that is II-3's).
- **Territory invariants:** `process_summary` is best-effort by contract (`DECISION_LOG.md` W8-8) — a
  crash there must never change a run's exit class; it must still summarise pre-W8-11 runs, degrading
  missing facts to "not recorded by this engine version" (`RUN_TRACE_SPEC.md` §6).
- **Co-landing note:** I-1 deletes `compose_prompt`; I-2 deletes its last consumers. Both must land for
  the tree to import — that is what the wave barrier verifies.

**I-3 (conductor) — aggregating writes.**
- `stages.py`: delete the panel-`None` guard (`:850-851`), make `brand_truth_panel` mandatory in
  `stage_media` (index, not `.get()`), matching `stage_copy:714`; pass `claim_snapshot` +
  `hard_excludes` into `MediaGenerator(...)` (`:917`); call `check_contract_consistency` in
  `stage_theme_load` after the config loaders; **compute the QA-outage rollup here** at the stage-outcome
  site (`:926-946`) from I-1's counters — if `vision_eligible > 0 and vision_qa_successes == 0` the
  stage is **degraded**, not ok. Composite-verified images are excluded from that denominator (they need
  no vision call) but still count toward "every delivered image has a verdict".
- `config/themes/hypedigitaly.yaml`: the minimal `generation.render_contract` block needed for
  consistency checks to pass at `CONTRACT_VERSION = 3`; purge the `compose_prompt` comment at `:265`.
- `NAVIGATION.md`: append the new leaf modules and the `render_contract` config surface.

**Barrier verification (before Wave II):**
```
cd C:/Users/Pavli/Desktop/HypeDigitaly/GIT/HypeAgentSocials/engine && python -m pytest -q
```
Baseline **515 passed** (verified 2026-08-07); expect a changed count, **zero failures**. Plus:
`grep -rn "compose_prompt" engine/ config/ docs/` returns nothing outside git history, this plan and
the `docs/plans/w8-11-overhaul/` specs (which name the deletion); and
`grep -rn "create_task(" engine/src/` returns exactly one production call site.

---

### WAVE II — Prompts, voice, tokens, claim-gate co-location

**Shape:** b + c. **Triggers:** (a) no. (b) no — 4 build tasks after the barrier. (c) no — the shared
module was frozen at I-0. → **no orchestrating parent.**
**Barrier justification:** II-2 and II-3 both *call* the token-budget and feedback-retry primitives that
II-1 adds to `llm.py`. II-4 and II-5 are independent and could launch with the barrier, but are batched
after it to keep one dispatch per sub-wave.

| Task | Executor | Depends on | Path set (touch nothing else) |
|---|---|---|---|
| **II-1** *(barrier)* Token budgets by cardinality + feedback-retry primitive | `python-pro` | I-* | `engine/src/hypeagent/llm.py` |
| **II-2** N-C voice, caps, speaker validator, critic rubric | `prompt-engineer` | II-1 | `engine/src/hypeagent/copy_gen.py` |
| **II-3** N-D prompt rewrite, per-slide repair, coherence | `prompt-engineer` | II-1 | `engine/src/hypeagent/promptcraft.py` |
| **II-4** N-E rubric, content-based trigger | `agent-pipeline` | II-1 | `engine/src/hypeagent/media_gen.py` |
| **II-5** Claim-gate qualification co-location | `python-pro` | II-1 | `engine/src/hypeagent/claim_gate.py` |
| **II-6** Wire-in + config registration | **main (conductor)** | II-1…II-5 | `engine/src/hypeagent/stages.py`, `config/themes/hypedigitaly.yaml`, `config/style_guide.yaml`, `NAVIGATION.md` |
| **II-7** Tests | `test-engineer` | II-6 | `test_llm.py`, `test_copy_gen.py`, `test_promptcraft.py`, `test_media_gen.py`, `test_claim_gate.py`, `test_render_contract.py`, `test_config.py` |

**II-1 brief.** Standing preamble + `RENDER_CONTRACT_SPEC.md` §7. `llm.py` only: add `per_slide_tokens`
to `LlmNodeOverride` resolution (`LlmNodeOverride` is at `config_load.py:427-436`; resolution site
`llm.py:341-352`) and an optional `slide_count` argument to `call_json`, so
`max_tokens = base + slide_count × per_slide`. Add a **feedback-retry primitive** — a public way for a
caller to re-ask with an appended corrective message — distinct from the existing truncation/parse retry
(`:369-420`), which stays exactly as is. **Territory invariants:** truncation
(`finish_reason == "length"`) is never silently accepted (`:374-376`); the budget check runs per HTTP
attempt (`:437`); `qa_reserved_calls` remains a floor only QA may spend into; `qa_headroom()` (added in
I-1) keeps working.

**II-2 brief.** Standing preamble + `RENDER_CONTRACT_SPEC.md` §3, `STYLE_SYSTEMS_SPEC.md` §7,
`FINDINGS_SYNTHESIS.md` §4 items 1-2 and §6. `copy_gen.py` only.
- **Voice.** Rewrite `_VOICE_RULES_BLOCK` (`:427-454`) for **faceless institutional voice**: rule 1's
  named founder ("Pavel Čermák") becomes "you are HypeDigitaly / HypeLead speaking as an organisation";
  ban any self-introduction; ban fabricated personal anecdotes; first-person plural only when honest.
  Keep the countable structural rules (rhythm, one antithesis, em-dash density, one CTA, the
  usable-artifact requirement) — they worked in fa51 and are why copy voice was the run's one
  unambiguous win. Add the five hard slop constraints from the copy audit.
- **Corporate-slop ban.** The institutional voice has its own failure mode, the mirror image of the
  invented persona. Extend the deterministic pre-filter `_SLOP_TELL_RE` (`:964-967`) **and** the voice
  rules with: "we believe", "our mission", "we're proud/excited to", "empowering", "seamless",
  "cutting-edge", "at HypeDigitaly, we".
- **Rewrite critic rubric items 1-2, do not merely append 13-15.** `_HUMANNESS_CRITIC_RUBRIC`
  (`:1025-1044`) items 1-2 currently *demand a named human writer and personal anecdote* — left as-is,
  N-F would faithfully rewrite compliant institutional copy back into a persona, undoing II-2 at the
  last node. Item 1 becomes institutional-speaker consistency; item 2 generalises to "concrete
  observation grounded in this run's material" and explicitly permits an honest institutional "we"
  while banning unverifiable "we did X". Then add **13** — narrowed per R13: *fabricated first-person
  experience without a name* (a lived-experience claim no organisation can honestly make; the
  deterministic speaker regex owns ALL name-matching, the critic never re-does it) — and **14**
  (structural-formula check: Old way/New way, ❌/→ chains, arrow lists >4, duplicate CTA mechanism
  across sibling assets). **R14: the former item 14 (cap re-verification against `ConstraintSet`) is
  DELETED** — caps are enforced deterministically at authoring and validation; asking a model to
  re-verify arithmetic adds a false authority, not a defense.
- **Native-language voice gate (§13 item 19.D, generalised by item 22.1).** The gate is
  **parameterized by `contract.language`**, not hardcoded to Czech: the requirement is native,
  colloquial, spoken-register quality in whichever language is active. Rewrite the authoring block
  so it carries, for the active language: (i) the out-loud test — *"would a native speaker say this
  sentence out loud to a colleague?"*; (ii) an explicit **translationese / calque ban** — no
  literally-translated English idiom in `cs`, no literally-translated Czech construction in `en`, no
  marketing-agency register in either; (iii) **few-shot exemplars, verbatim from the ratified
  simulation copy**, selected by language:
  - `cs` — *"Poptávka přišla ve dvě ráno. Odpověď odešla ve 2:01."* · *"Firma bez webu? Do večera to
    jde."* · *"Scénáře naklikáte, kód neřešíte."*
  - `en` (default, §13 item 22.1; from `simulation/round2/prompts/*_en`) — *"AI won't take your job.
    A company that uses it will."* · *"The lead came in at 2 a.m. The reply went out at 2:01."* ·
    *"Make — click your scenarios together, skip the code."*

  The exemplar block is a **voice-only** grounding source under the same rule as `_load_exemplar_block`
  — it is never `allowed_facts`. Add critic rubric item **15 — `<language>_nativeness`**: "does this
  read as written by a native speaker of the asset's language, or as translated/agency copy? Name the
  offending sentence." Add item **16 — concrete-specifics (D6)**: every hook and every body slide must
  carry a *specific* — a number, a time, a named tool, or a named step; abstractions ("efficiency",
  "transformation", "the future of work") without a specific attached are a FAIL, and the critic names
  the slide index. Both items are rubric lines, not deterministic gates; the deterministic partner for
  16 is the slide-value check below.
- **Slide-value gate for carousels (§13 item 22.2, operator: "must be really valuable, practical and
  specific — no AI slop").** Deterministic, at authoring, over each `BODY`/`PROMPT_QUOTE` slot's gated
  `on_image_text`: the slide must contain **at least one concrete token** — a numeral, a tool name
  from `assets/logos/manifest.yaml`'s keys plus the style-guide topic lexicon, or an imperative
  step/verb marker — **and** must not be a near-restatement of the cover (token-overlap ratio against
  the cover's own spans above a fixed threshold is a failure). Failure → repair round with the
  verbatim reason and the slide index, exactly like the speaker validator; still failing after the
  bounded rounds ⇒ the asset is **held with the verbatim reason** (existing gate-fail→held semantics,
  `:1156-1248`, unchanged). It is never silently shortened — all-or-nothing at delivery is unchanged,
  and a carousel that cannot fill five valuable slides is a carousel that should not ship.
- **Gold-standard caption exemplars + caption-craft rules (§13 item 24).** The four ratified
  exemplars below go into the N-C prompt as **few-shot gold standard** for the active language (EN
  default), keyed by format class so a meme asset is not shown a LinkedIn workflow caption:
  - *website_showcase (IG)* — "A bakery with no website got one by dinner. / The workflow: Claude
    reads your customer reviews and writes the copy. Lovable turns it into a working site. One
    evening, zero code. / Save this for the next time an agency quotes you six weeks. /
    #aitools #automation #smallbusiness"
  - *artifact_showcase / workflow map (LinkedIn)* — "A lead came in at 2:00 AM. The reply went out at
    2:01. / Nobody woke up. / The stack: a web form, Zapier, Claude, Gmail. Four pieces, one afternoon
    to set up. The lead booked a call before breakfast. / Speed is the cheapest advantage left. The
    exact setup is in the comments."
  - *meme_reaction (IG — short, the image carries it)* — "Somewhere, an ops coordinator just felt a
    disturbance. / #aiagents #opslife"
  - *brand_promo (IG)* — "Free AI audit: we map where your team loses the most hours and which two
    automations pay for themselves first. 30 minutes, no obligation. / Click the link in bio to book."

  The rules these encode become explicit prompt lines **and**, where deterministic, checks:
  **hook line first** · **concrete specifics** (times, counts, tool names — D6, and the partner of
  the slide-value gate) · **zero slop vocabulary** — extend `_SLOP_TELL_RE` with `game-changer`,
  `unlock`, `revolutionize`/`revolutionise` alongside the existing set · **meme captions stay
  minimal** (the image carries the joke) · **promo CTA is the link-in-bio pattern** · **hashtags
  ≤3 on LinkedIn, ≤5 on Instagram** — a new `hashtag_max_count` in `CaptionRules` and in
  `ConstraintSet.caps`, enforced deterministically at authoring like every other cap, never as prose.
  Like `_load_exemplar_block`, these exemplars are a **voice-only** grounding source and never
  `allowed_facts`.
- **Critic items 17-18 (§13 item 24).** **17 — `visual_logic_coherent`**, applied to **every
  illustration-class asset**: the actor and scene named in the slot's `visual_intent` must match the
  caption's subject. The round-6 v1 failure is the canonical example — the brand robot panicking
  about *hiring a human coordinator* is nonsense, because the robot is not the one who would hire.
  N-F sees both the copy and the visual intent **before any render is paid for**, which is exactly
  why the check belongs here and not only in N-E; `subject_relevant` remains the post-render backstop.
  **18 — `instant_read`**, meme classes only: the joke must land in about one second, on
  universally-known visual grammar, with minimal symmetric captions. A meme that needs a paragraph is
  a failed meme, and the critic names it as such.
- **`brand_promo` assets are not authored by N-C (§13 item 20).** A `format_class: brand_promo` asset's
  copy comes verbatim from `generation.brand_promo.messages[...]` + the verbatim CTA pill text —
  **zero LLM calls, zero critic pass, zero repair loop**. `copy_gen` builds the `CopyAsset` from
  config (the construction itself is III-1's) and the claim gate still runs on those strings exactly
  as on authored copy. This is why the non-QA LLM estimate counts **7** N-C calls for an **8**-asset
  run: the six organic assets plus the reserved meme asset are authored; only `brand_promo` is not.
- **Speaker validator**, deterministic, three limbs: (a) **unconditional** ban on `I'm` / `I am`
  self-identification; (b) name-adjacency check for `"<Name> here"` / `"this is <Name>"` where `<Name>`
  is a capitalised token **not** in the brand-term allowlist (`HypeDigitaly`, `HypeLead`); (c) Czech
  patterns — `jsem <Name>`, `jmenuji se`, `<Name> tady`. Failure → repair round with the verbatim
  reason; still failing ⇒ held. fa51 invented "Marcus", "Radka" and a near-miss of the real operator's
  name with **no name anywhere in the request**.
- **Route the validator through both paths.** It runs in `process_copy_asset`'s repair loop **and** in
  `apply_humanness_critic`'s rewrite-acceptance path (`:1083-1153`) — an N-F rewrite that reintroduces a
  persona must be rejected exactly like a gate failure, keeping the original.
- **Constraints.** Insert `contract.constraints().as_prompt_block()` into `_build_openrouter_prompt`'s
  `system` (`:457-585`) after the voice block, **and repeat the numeric caps compactly immediately
  before `schema_hint`** (constraint sandwich). Add `validate_against_contract(result, contract)` inside
  `OpenRouterProvider.generate` (`:730-822`) before the corrective-retry decision. Add `self_check`
  word-count fields — **discarded after independent recomputation**, never trusted as a gate input
  (json_schema-typed responses are an explicit scope cut: `llm.py` supports only `json_object`).
  Thread `caps["prompt_quote_max_words"]` (50) — `exempt_from_word_cap` alone means unbounded, and the
  first failure would otherwise land at compositing, the most expensive point. Round 2 adds a second
  named exemption with its own derived ceiling: `value_sheet_max_words: 220` for `ig_value_sheet`
  dense slides (`STYLE_SYSTEMS_SPEC.md` §2.8/§2.9) — enforce at authoring exactly like the
  prompt-quote cap; no third exemption exists.
- **Anti-ad banner scan at craft time** (`STYLE_SYSTEMS_SPEC.md` §5.9): run `_AD_BANNER_RE` over every
  gated `on_image_text` string in the repair loop and the N-F rewrite-acceptance path — the primary
  defense, because composited text never passes through a RENDER prompt. Failure → repair with the
  verbatim reason, exactly like the speaker validator. **R4/R6: only wiring points 1 (here, craft
  time) and 3 (QA free text, II-4) exist — the pre-generation `<<…>>` span scan (point 2) is
  deleted; the spans ARE the gated strings already scanned here.**
- **R5:** also scan gated `on_image_text` against `BANNED_RENDERED_STRINGS` at authoring — moving the
  catch to the repairable, cheap point instead of post-render.
- Delete `_DESTINATION_CONSTRAINTS` (`:829-848`); derive `CopyRequest.destination_constraints` from
  `contract.constraints().caps`. Replace `HUMANNESS_CRITIC_DEFAULT_MAX_TOKENS` (`:975`) with resolution
  through the node override.
- **Territory invariants:** the claim gate stays the arbiter and N-F rewrites re-enter it
  (`:1131-1134`); a gate-failing rewrite keeps the original (`:1143`); post_mix branching and the
  numbered-promise hard gate (`:618-657`) survive unchanged — both confirmed working in fa51;
  `_load_exemplar_block` (`:355-414`) is a **voice-only** grounding source and must never become a
  claims source — exemplar text is not `allowed_facts`.
- **Named acceptance tests:** `test_speaker_validator_blocks_invented_persona`,
  `test_critic_rubric_does_not_demand_a_named_person`, `test_corporate_slop_is_prefiltered`,
  `test_prompt_quote_word_cap_enforced_at_authoring`,
  `test_nativeness_block_and_exemplars_match_the_asset_language`,
  `test_critic_rubric_carries_nativeness_and_concrete_specifics_items`,
  `test_filler_carousel_slide_is_repaired_then_held`,
  `test_brand_promo_asset_makes_no_llm_call`,
  `test_exemplars_are_selected_by_format_class_and_language`,
  `test_hashtag_cap_enforced_at_authoring_per_destination`,
  `test_slop_prefilter_catches_game_changer_unlock_revolutionize`,
  `test_critic_rubric_carries_visual_logic_and_instant_read_items`.

**II-3 brief.** Standing preamble + `RENDER_CONTRACT_SPEC.md` §3/§6, `STYLE_SYSTEMS_SPEC.md` §5-§6,
`SLOT_MODEL_SPEC.md` §5.1. `promptcraft.py` only.
- `SYSTEM_PROMPT` (`:109-166`) becomes a template receiving `constraints.as_prompt_block()`. N-D's job
  narrows to **layout and scene** — the on-image text is *given* and must be embedded verbatim, never
  authored or paraphrased (the verbatim instruction at `:116-117` stays; what changes is that the text
  it receives is now guaranteed to satisfy the caps it is judged against).
- Delete `MAX_BODY_WORDS` (`:664`); `validate_crafted_prompt` (`:687-751`) takes `caps`. All eleven
  existing checks stay. Adopt `render_contract.QUOTED_SPAN_RE` and delete the local copy at `:668`.
- **Validation-failure feedback retry:** one bounded round re-asking with the exact failing reason, via
  II-1's primitive. Today the only retry is `llm.py`'s truncation/parse retry — a *semantically* invalid
  prompt has never been re-asked.
- **Per-slide granularity:** replace the whole-set kill at `:953-969`; a failing slide repairs or blocks
  by itself. Adopt the frozen `CraftedImagePrompt`/`CraftedPromptSet` shapes from I-0 and delete
  `hero_prompt()`/`usable()` (`:208-220`).
- **R1 (headline review finding): N-D runs iff `format_class == photoreal`.** The LLM crafter exists
  for exactly one job — describing a real scene for `ground_source: diffusion` slots (`llm_crafted`
  category, B1). Every OTHER diffusion surface (partial-area `logo_zone`, `photo_inset`, any
  remaining flat-ground cover) is **`templated_diffusion`**: a deterministic template prompt
  assembled in promptcraft from the style recipe — no LLM call, still governed through `govern()`
  and the single choke point. Programmatic slots go `PLANNED --no_diffusion_surface--> CRAFTED` with
  no call of any kind. Size the N-D token budget on the **`llm_crafted` slot count only**.
  **Re-partitioned by the flip (§13 item 19.A) — R1's mechanism survives, its membership changes.**
  There is no longer a "fully programmatic" system: every slot of every system is a canonical
  `gpt-image-2-text-to-image` render, and `programmatic` is now **the fallback rung and the
  kill-switch destination only**. The three categories re-partition as: **`llm_crafted`** = slots
  whose image is a *scene or illustration that must be described per topic* — the three photoreal
  systems' scene slots plus the illustration classes' signature slots (`website_showcase`,
  `robot_caricature`, `anime_scene`, `concept_dashboard`, `meme_reaction`); **`templated_diffusion`**
  = every
  recipe-determined card (`designed_card`, `serif_editorial`, `editorial_grotesque`,
  `artifact_showcase`, `brand_promo`, and the illustration systems' non-signature body slides) — a
  deterministic full-design template prompt, no LLM call, still governed; **`programmatic`** =
  fallback/kill-switch. Under the default quota that is **4 N-D calls per run** (1 photoreal asset +
  2 illustration-group assets + at most 1 when the occasional token lands on `concept_dashboard`),
  each sized on that asset's own `llm_crafted` slot count (photoreal: lifestyle 5 / scene_hook 2 /
  scene_hero 1; illustration: 1, or 2 for `anime_scene`).
- **Anti-ad Hard DON'T constants** (`STYLE_SYSTEMS_SPEC.md` §5.6-§5.10, as reconciled by 0-6): extend
  `_GRADIENT_MESH_RE` (radial glow / premium gradient) and `_CLIPART_ROW_RE` (benefit pills /
  checkmark rows); add `_DEVICE_MOCKUP_RE` and `_TEMPLATE_BACKDROP_RE` (scanned over RENDER excluding
  the reserved-zone fragment). All join the ONE shared register-keyed leak function from I-0 (R7 —
  called here and in `govern()` step 4, no duplicate implementation). **Deleted per review:**
  `_LOGO_INVENT_RE` (R8 — templated logo prompts are deterministic, authoring-time invention is
  impossible), `_FONT_NAME_RE` (R6), and `_AD_BANNER_RE`'s span wiring point (R4 — craft-time + QA
  free-text remain, II-2/II-4). Keep §5.11's nominative-use precondition: every tool a `logo_zone`
  brief names must appear in the asset's own copy/`allowed_facts`.
- **Mode selection moves to the copy stage** (explicitly in scope here): `pick_generation_mode` is
  called once per asset while resolving the contract, and its result is carried on `VisualPolicy`. II-6
  only passes the result through — it does not re-pick. This is what stops mode/register drifting
  between the copy and media stages.
- Add a **register/mode coherence validator** and generalise `_EDITORIAL_LEAK_RE` (`:679`) into the
  register-keyed table (`STYLE_SYSTEMS_SPEC.md` §6). Add `contract_version` + `contract_sha256` and the
  per-slot state block to `media_prompts.yaml`; `load_media_prompts` (`:266-279`) returns `{}` on
  mismatch. Use `fsutil.atomic_write_text` for that write (`:258-263`). Purge the `compose_prompt`
  reference in the module docstring (`:40-51`).
- **Do not touch** `_legacy_pick_archetype_register:425` — that hardcode is Wave IV (IV-6), which needs
  the evidence layer to replace it correctly.
- **Territory invariants:** the STYLE block stays deterministic Python (`_build_style_section:294-383`),
  never LLM-authored; "STYLE is never rendered as text" holds; the photographic register never inherits
  editorial cream-paper/Didone directives; the "N percent" spelling that keeps STYLE numerals from
  tripping the claim gate (`:371-375`) is preserved.
- **Ratified-package validators (§13 items 19.B/19.F, 21) — deterministic, all in
  `validate_crafted_prompt` and all fed by the ONE shared leak/pattern function from I-0:**
  1. **Accent-hex pinning (F10).** Every submitted prompt must contain at least one accent hex
     **literal** from its own style system's palette (`#302B87` indigo · `#00A39A` teal · `#E8A63B`
     amber) and must not name a colour outside that system's palette in accent position. Rationale is
     empirical, not stylistic: with no hex pinned the model chose coral/orange accents twice, and
     coral is Anthropic's trademark colour, usable only as an accurate Claude mark (§3.6). A missing
     accent hex is a validation failure, repairable by the feedback retry.
  2. **Screens-off (F11).** Every photoreal/illustration template and every N-D RENDER brief for a
     scene slot carries verbatim *"Every screen and monitor in the frame is OFF (dark glass) or
     angled away — never render any UI content."* Checked as a literal-substring precondition, not a
     regex; 0/4 scene renders showed invented UI once this sentence was present, versus 2/3 without
     it.
  3. **Tool-mark coverage (F8/F13 — the hard rule, §13 item 19.B).** For every gated `on_image_text`
     span of the slot, extract named tools (keys of `assets/logos/manifest.yaml` plus the style-guide
     topic lexicon). **Every named tool must have a mark in that slot's brief** — an `icon_row` /
     inline chip / `node_diagram` node — and the brief must carry that tool's manifest
     `description:` string verbatim (F8: precise verbal mark descriptions took fidelity from ~50% to
     ~95%). A named tool with no mark is a `GovernFailure`, not a warning (invariant **LG2**). The
     existing nominative-use precondition (§5.11) is the mirror check and stays: a mark for a tool the
     copy never names also fails.
  4. **Emphasis-token discipline (D2, `reference/OPERATOR_FAVORITES_DNA.md`).** Exactly **one**
     emphasis token per headline, in a brand colour; amber is reserved for numerals/times. Two
     emphasis instructions in one prompt, or an amber emphasis on a non-numeral, is a validation
     failure.
- **Named acceptance tests:** `test_single_bad_slide_does_not_kill_the_set`,
  `test_feedback_retry_reasks_with_verbatim_reason`,
  `test_programmatic_slot_makes_no_llm_call`, `test_media_prompts_version_mismatch_forces_recraft`,
  `test_prompt_without_pinned_accent_hex_fails_validation`,
  `test_scene_prompt_carries_screens_off_sentence`,
  `test_named_tool_without_mark_fails_governance`,
  `test_second_emphasis_token_fails_validation`.

**II-4 brief.** Standing preamble + `FINDINGS_SYNTHESIS.md` §4 item 6, `STYLE_SYSTEMS_SPEC.md` §5.
`media_gen.py` only: make the N-E trigger **content-based** — scan the submitted prompt for
renderable-text markers rather than keying off a code path; text booleans skip individually;
subject / composition / gibberish / logo always run. Extend `QA_SYSTEM_PROMPT` (`:883-937`) with "no
multi-panel collage when one image was requested" (fa51's fallback carousel prompts produced 2×2
collages) and "no lorem ipsum / placeholder-label words"; add **three** booleans to `VisionQaResult`,
all in the overall-pass computation: `ui_fidelity_ok` (fake-dashboard DON'T, §5.4 — a device mockup
showing an invented product is `false` by definition, §5.8), `ground_standalone_ok` (§5.10 — judged
only for `ground_source: diffusion` slots, vacuously true otherwise: the ground must read as finished
content with the text mentally removed), and `logo_fidelity_ok` (§5.11 — **never skipped when the
prompt names a tool logo**: every depicted third-party mark accurate, and false when an unrequested
mark appears; the repair wiring on failure is Wave IV task IV-7's). *(B5/R12, applied spec-side by
0-6: `logo_fidelity_ok` is THE logo boolean — the old `logos_ok` folds into it; one boolean, one
subject.)* Extend `composition_ok`'s rubric
with §5.6-§5.9's clauses (radial-glow grounds, pill rows, 3D device mockups, price/urgency banner
furniture). Wire the extended `BANNED_RENDERED_STRINGS` list
(`STYLE_SYSTEMS_SPEC.md` §5.3) into `_scan_banned_and_hex` (`:822-832`) — post-render backstop only;
the authoring-time scan is II-2's (R5). **R16, restated under the flip:** `series_consistent` is
judged across all canonically-rendered slots of a carousel (which is now all of them);
composite-fallback slots are byte-deterministic and are excluded from the cross-slide vision
judgment. **R3 is REVERSED (§13 item 19.A) — `text_matches` becomes the load-bearing canonical
boolean, not a deleted one.** Every canonical render is verified **per glyph** against that slot's
gated `on_image_text` strings: the QA prompt instructs character-for-character comparison including
diacritics **when the asset's language is `cs`** (`š`≠`s`, `ř`≠`r`, `é`≠`e` — a dropped or
substituted diacritic is a FAIL, never a near-match) and character-for-character comparison of every
word when it is `en`; the verdict names each offending span. This is the gate that catches F18's
`ktery` and it may never be skipped for a canonically-rendered image (invariant **RL2**;
`text_matches` joins the never-skipped set alongside subject / logo / composition / gibberish, and
only genuinely text-free surfaces skip it). The verdict drives the ladder: pass ⇒ deliverable, first
failure ⇒ one retry, second failure ⇒ `FALLBACK_COMPOSITING` (the transition is IV-7's wiring; the
boolean and the rubric are this task's). **Territory invariant:** "a
non-empty `mismatches` list can never pass" (`:935-936`, `:1073-1076`) — the W8-10 fix that must not
regress. **Named acceptance tests:** `test_qa_runs_on_image_with_no_expected_text`,
`test_logo_fidelity_never_skips_when_prompt_names_a_tool`,
`test_text_matches_never_skips_for_a_canonical_render`,
`test_dropped_diacritic_is_a_text_failure_not_a_near_match`,
`test_qa_text_instruction_follows_the_asset_language`.

**II-5 brief.** Standing preamble + `RENDER_CONTRACT_SPEC.md` §6 (co-location subsection).
`claim_gate.py` only: `_kvalifikovat_satisfied` (`:141-145`) takes the **sentence containing the
matched number** — split the field on `[.!?\n]`, take the span holding the digits — instead of the
asset-wide `combined_text` built at `:189-190`. No feature flag; rollback is `git revert` of one file.
**Territory invariants:** the claim lexicons, `run_claim_gate`'s signature (`:162-269`) and the
`abstain`-behaviour path (`:226-232`) are load-bearing and unchanged; `ClaimGateVerdict.checked_fields`
must reflect reality once slides are included. **Ratified-package addition (§13 item 22.1 — EN is now
the default language):** the qualification-marker lexicon becomes **language-keyed**, selected by
`contract.language`, with the existing Czech markers untouched and an English set added (`reported`,
`according to`, `roughly`, `approximately`, `about`, `up to`, `median`, `average`, `in our own
runs`…). Without this, every EN asset's numbers would be judged against a Czech-only marker list and
the gate would block correct copy or — worse, if the list is treated as "no markers found, abstain" —
pass unqualified ones. The **co-location logic itself is language-agnostic** (sentence split on
`[.!?\n]`, take the span holding the digits) and is not duplicated per language.
**Named acceptance tests:** `test_qualification_must_be_colocated_with_the_number`, the fa51
regression `test_fa51_35095_with_distant_reported_now_blocks` ("35,095" in a slide body with
"reported" three slides away must now block), and
`test_qualification_lexicon_follows_contract_language`.

**II-6 (conductor) — aggregating writes.**
- `config/themes/hypedigitaly.yaml`: full `generation.render_contract` block
  (`RENDER_CONTRACT_SPEC.md` §7, B2-reconciled — no per-slot `text_render_mode`/`ground_source` keys)
  carrying **both** Instagram formats (`single` 1 slot, `carousel` 5 slots per **§13.1**; the choice
  is the evidence-gated stage-1 decision, §13 item 22.2, default `single`); token budgets — copywriter
  4000→**8000**; prompt_crafter 6000 + `per_slide_tokens: 1200`; **new** `humanness_critic` override
  (4000 + `per_slide_tokens: 400` — it has *no* entry today and silently inherits
  `default_max_tokens`, which is why N-F failed on 2/6 fa51 assets and shipped the originals
  unreviewed); `media.require_visual_evidence: true`.
  **Recomputed caps (§9.3 — the ratified package moves all of them; the derivations are there, do not
  re-derive here):** `llm.qa_reserved_calls` 16→**42** · `llm.per_run_call_cap` 60→**80** ·
  `llm.per_run_usd_cap` $2.00→**$4.00** · `media.per_run_count_cap` 14→**42** ·
  `media.per_run_usd_cap` **$3.00 unchanged** · `media.per_day_usd_cap` **$6.00 unchanged**
  (operator-confirmed, §13 item 22.4). *(These four LLM/media caps used to be split between this task
  and IV-B-5; with the test track shipping disabled, IV-B-5 sets no caps and they all land here —
  one writer, one wave.)*
  Also here: `generation.language_by_destination` — **`en` for every enabled destination** (§13 item
  22.1), with `cs` documented inline as the supported switch. If consistency check 8 fails, raise
  `per_run_call_cap` / `per_run_usd_cap` rather than weakening the check.
- `config/style_guide.yaml`: delete the "60-90 words per slide" prose (`:91-93`); add `register:` to
  every `visual_archetypes[*]` entry (`STYLE_SYSTEMS_SPEC.md` §3.2); reconcile `carousel.slides` with
  §13.1 (`slides: [5, 7]`).
- `stages.py`: resolve the contract once per asset in `stage_copy` **before**
  `copy_gen.build_copy_request`, stash on `ctx.extra["render_contracts"][asset_id]`, re-read (never
  re-resolve) in `stage_media`; use `fsutil.atomic_write_text` at `:548-550`.
- `NAVIGATION.md`: append the new config keys.

**Barrier verification:** full pytest green, plus a **config-load smoke** — a deliberately contradictory
`slides:`/`max_generated_slides:` pair must raise `ConfigError` and policy-stop
(`test_config.py::test_contract_consistency_refuses_contradiction`).

---

### WAVE III — Slot model and true carousels

**Shape:** a + c. **Triggers:** (a) no. (b) **five build tasks — but not one domain**: they span copy,
prompting, media, packaging and resume, each owning exactly one file, with the shared types frozen at
I-0. (c) no. → **no orchestrating parent.**

| Task | Executor | Depends on | Path set (touch nothing else) |
|---|---|---|---|
| **III-1** N-C emits `CopyAsset`/`Slot` | `agent-pipeline` | II-* | `engine/src/hypeagent/copy_gen.py` |
| **III-2** N-D crafts per slot | `agent-pipeline` | II-* | `engine/src/hypeagent/promptcraft.py` |
| **III-3** Plans 1:1 with slots, state machine | `agent-pipeline` | II-* | `engine/src/hypeagent/media_gen.py` |
| **III-4** Packaging + summary consume slots | `python-pro` | II-* | `engine/src/hypeagent/packaging.py`, `process_summary.py` |
| **III-5** Resume carries contract + policy | `python-pro` | II-* | `engine/src/hypeagent/resume_state.py` |
| **III-6** Wire-in | **main (conductor)** | III-1…III-5 | `engine/src/hypeagent/stages.py`, `NAVIGATION.md` |
| **III-7** Tests | `test-engineer` | III-6 | `test_copy_gen.py`, `test_promptcraft.py`, `test_media_gen.py`, `test_packaging.py`, `test_process_summary.py`, `test_resume.py`, `test_asset_model.py`, `test_phase3_pipeline.py` |

All briefs: standing preamble + `SLOT_MODEL_SPEC.md` **in full** + `RENDER_CONTRACT_SPEC.md` §2.

**III-1 — scope.** `CopyRequest` gains `contract`; `CopyResult.slides` → `CopyResult.slots`;
`_parse_openrouter_response` (`:660-687`) maps JSON to `Slot`s by index and assigns `role` from
`contract.slots[i].role` (the model does not choose roles); `AssetCopyStatus` (`:897-911`) collapses
`slides`/`image_brief`/`headline` into `asset: CopyAsset | None`; `_carousel_deficiency` (`:588-601`)
and `MIN_CAROUSEL_SLIDES` (`:295`) are replaced by a contract check honouring `exempt_from_word_cap`
*and* `prompt_quote_max_words`; `_content_slide_count` counts `BODY` + `PROMPT_QUOTE` roles;
`on_image_text` enters the claim gate via `slides=[…]` at authoring.
**Ratified-package addition — `build_brand_promo_asset(contract, brand_promo_cfg, run_date)` (§13
item 20).** A pure function that returns a `CopyAsset` for a `format_class: brand_promo` contract
with **no LLM call anywhere**: headline + body line taken verbatim from
`generation.brand_promo.messages[int(sha256(run_date_iso)[:8], 16) % len(messages)]` (seeded rotation,
same seed idiom as `style_select`), and the CTA span taken **verbatim, never paraphrased** from
`generation.brand_promo.cta_text` (`"Klikněte na odkaz v popisku"` for `cs`, the configured EN
equivalent for `en`). The asset goes through the claim gate exactly like authored copy — a promo is
not exempt from truth — but skips the repair loop, the critic, the speaker validator and the
slide-value gate (there is nothing generated to police). `process_copy_asset` routes to it on
`contract.visual.style_system`'s `format_class`; the run-level decision to *create* the asset is
`style_select`'s (IV-10) and the wiring is main's (IV-8).
**Territory invariants:** the repair loop and gate-fail→held semantics (`:1156-1248`) are unchanged; N-F
still re-enters the gate; the speaker validator from II-2 still runs on both paths; `CopyResult.slots`
is 1:1 with `contract.slots` for **both** the `single` and `carousel` shapes — the format is an input
from stage 1, never inferred from the destination or from how much copy the model produced.
**Named acceptance tests:** `test_copy_result_slots_match_contract_roles`,
`test_on_image_text_is_claim_gated_at_authoring`,
`test_brand_promo_copy_is_verbatim_from_config_and_calls_no_llm`,
`test_brand_promo_cta_text_is_never_paraphrased`,
`test_single_format_instagram_asset_has_exactly_one_slot`.

**III-2 — scope.** Craft per slot index against the frozen `CraftedImagePrompt`; emit
`state`/`reason`/`repairs_used` per slot; persist the per-slot block in `media_prompts.yaml`; never
invent a slot the contract did not declare; skip N-D for zero-diffusion slots (carried from II-3).
**Territory invariants:** as II-3, plus: crafted output is 1:1 with contract slots or the missing slot is
explicitly blocked — never silently dropped.
**Named acceptance tests:** `test_crafted_set_is_one_to_one_with_contract_slots`,
`test_per_slot_state_persisted_across_resume`.

**III-3 — scope.** Rewrite `plan_media_assets` (`:656-718`) to the contract-driven signature
(`SLOT_MODEL_SPEC.md` §5); drive `SlotState` through `advance()` with a decision event per transition;
make `_status_from_row` (`:1646-1684`) a pure `MediaIntentRow.state → SlotState` mapping; compute
`asset_deliverability` at delivery (incl. `held_incomplete` for `SUBMITTED_UNKNOWN` or mixed
`contract_sha256`).
**Territory invariants:** `asset_slot` string format must not drift (ledger identity, `store.py:182`);
all-or-nothing applies at **delivery**, not craft; deliverability derives from manifest/ledger state and
**never** from `image_path` on disk; a partial carousel is never shipped short and never downgraded to a
hero; the write-ahead order, caps, circuit breaker and `_settle_intent` behaviour from I-1 are unchanged.
**Named acceptance tests:** `test_plan_count_matches_contract_not_crafter`,
`test_partial_carousel_is_copy_only`, `test_mixed_contract_carousel_is_held_incomplete`.

**III-4 — scope.** `packaging` reads slot states and `asset_deliverability`, and writes the verbatim
blocking reason into the digest for `copy_only` / `held` / `held_incomplete`; `process_summary` renders
the slot model and the per-slot decision trail.
**Territory invariants:** `--summarize` on a pre-W8-11 run must still work, degrading missing facts to an
explicit "not recorded by this engine version" line (`RUN_TRACE_SPEC.md` §6); a summary crash never
changes a run's exit class.
**Named acceptance tests:** `test_digest_states_why_an_asset_is_copy_only`,
`test_summarize_old_run_degrades_gracefully`.

**III-5 — scope.** `ResumeState` (`:55-71`) gains `contract_version: int = 0`,
`visual_policies: dict[str, VisualPolicy]` and `contract_sha256s: dict[str, str]`, all following the
`viral_playbook_path` precedent (`:231-247`: new field, safe default, explicit `to_dict`/`from_dict`).
`resume_pipeline` refuses with a policy-stop and an explicit operator message when `contract_version !=
render_contract.CONTRACT_VERSION` — **compare the constant, never a literal**. Swap
`fsutil.atomic_write_text` in at `:246`.
**Why `visual_policies` is mandatory:** `stage_analysis` is **not** in `RESUME_STAGE_NAMES`
(`stages.py:1050`), so a resumed run cannot re-derive `VisualPolicy`. Without persistence it either
derives a *different* policy (contract sha drifts → every asset re-crafts → straight into the
prompt-sha guard, blocking the whole run) or finds no evidence and blocks every image. On resume
`stage_copy` **reads** the persisted policy and never re-derives it; a sha mismatch is a policy-stop.
**Named acceptance tests:** `test_resume_refuses_stale_contract_version`,
`test_resume_reuses_persisted_visual_policy_without_reanalysis`.

**Barrier verification:** full pytest green, plus `test_media_gen.py::test_plan_count_matches_contract_not_crafter`
and `test_asset_model.py::test_partial_carousel_is_copy_only` present and passing.

---

### WAVE IV — Virlo evidence link, compositing module, eleven style systems, selection, logos

**Shape:** b + c. **Triggers:** (a) no. (b) **ten build tasks across seven domains** (store, collector,
compositing, promptcraft, ranking, analysis/selection, logos), each owning a disjoint path set. (c) no
— the round-2/3 leaves build against frozen spec shapes (`STYLE_SYSTEMS_SPEC.md` §4,
`MULTI_MODEL_SPEC.md` §7), not shapes designed mid-wave. → **no orchestrating parent.**
**Barrier justification:** only IV-4 and IV-5 *read* IV-1's new store API. Everything else launches in
batch 1.

**Batch 1 (parallel):**

| Task | Executor | Depends on | Path set (touch nothing else) |
|---|---|---|---|
| **IV-1** *(barrier for IV-4/IV-5)* `first_seen_at` + schema version + widened ledger UNIQUE | `python-pro` | III-* | `engine/src/hypeagent/store.py` |
| **IV-2** Virlo corpus re-materialisation | `python-pro` | III-* | `engine/src/hypeagent/collectors/virlo.py` |
| **IV-3** Compositing package (incl. round-2 additions) | `agent-pipeline` | III-* (Pillow approved, §13.2) | `engine/src/hypeagent/compositing/**` (NEW) |
| **IV-6** Register from mode; style system into STYLE; new modes | `agent-pipeline` | III-* | `engine/src/hypeagent/promptcraft.py` |
| **IV-10** Two-stage selection layer + format gate + brand-promo reservation (`STYLE_SYSTEMS_SPEC.md` §4) | `python-pro` | III-* | `engine/src/hypeagent/style_select.py` (NEW), `engine/src/hypeagent/config_load.py`, `engine/src/hypeagent/resume_state.py` |
| **IV-11** Brand-asset fetch/cache helper — logo **and** product visual, three-tier ladder *(renamed from `logo_assets.py`; §13 item 19.C)* | `python-pro` | III-* | `engine/src/hypeagent/brand_assets.py` (NEW) |
| **IV-12** Brand-asset manifest authoring — **REQUIRES WEBSEARCH; owned by main or a web-capable leaf (`documentation-engineer`); never assign to `python-pro`/`agent-pipeline`** | **main** or `documentation-engineer` | III-* | `assets/logos/manifest.yaml` (NEW) |

**Batch 2 (parallel, after batch 1 completes — IV-4/IV-5 read IV-1's store API; IV-7 reads IV-3's
package and IV-11's helper):**

| Task | Executor | Depends on | Path set |
|---|---|---|---|
| **IV-4** R1 freshness on first-seen | `python-pro` | IV-1 | `engine/src/hypeagent/ranking.py` |
| **IV-5** `evidence_class` + durable `VisualProfile` | `agent-pipeline` | IV-1 | `engine/src/hypeagent/analysis.py` |
| **IV-7** Render ladder (canonical → retry → composited fallback → copy-only), artifact-zone routing, composite QA verdict, brand-asset repair + tier ladder | `agent-pipeline` | IV-3, IV-11 | `engine/src/hypeagent/media_gen.py` |
| **IV-8** Wire-in, config, dependency, fonts, version bump | **main (conductor)** | IV-1…IV-7, IV-10…IV-12 | `engine/src/hypeagent/stages.py`, `engine/src/hypeagent/render_contract.py` *(one-line `CONTRACT_VERSION` bump only)*, `config/style_guide.yaml`, `config/themes/hypedigitaly.yaml`, `config/model_registry.yaml`, `engine/pyproject.toml`, `assets/fonts/**`, `NAVIGATION.md` *(spec staleness fixes moved to 0-6)* |
| **IV-9** Tests | `test-engineer` | IV-8 | `test_store.py`, `test_virlo.py`, `test_ranking.py`, `test_analysis.py`, `test_promptcraft.py`, `test_media_gen.py`, `test_compositing.py` (NEW), `test_style_select.py` (NEW), `test_brand_assets.py` (NEW), `test_resume.py`, `test_config.py` |

**IV-1 brief.** Standing preamble + `RENDER_CONTRACT_SPEC.md` §8, `CODING_GUIDELINES.md` §9.
`store.py` only. Add `first_seen_at` to `normalized_signals` (`:83-98`) with **insert-only** semantics —
`store_signal`'s `ON CONFLICT DO UPDATE` (`:641-697`) currently refreshes `retrieval_time` on every
re-collect, which is exactly why the R1 freshness window skipped 0 of 566 stale fa51 rows.
`first_seen_at` must be excluded from the `DO UPDATE` set, mirroring `provenance_durable`'s `DO NOTHING`
(`:679`). Add `signals_first_seen_since(theme, since)` and a covering index. There is **no migration
framework**: follow the hand-written additive idiom in `_migrate_schema` (`:453-460`) —
`PRAGMA table_info` then `ALTER TABLE … ADD COLUMN` — and add a `schema_version` table alongside for
bookkeeping. **`PRAGMA table_info` remains the schema-truth mechanism**: the version row records intent,
the PRAGMA check decides, so a hand-edited DB cannot lie to the engine. Backfill
`first_seen_at = retrieval_time` for existing rows in the same additive step (idempotent, logged count).
**Second migration in the same task — widen the `media_intents` UNIQUE by `model_string`**
(`MULTI_MODEL_SPEC.md` §7, read it in full): the column already exists (`store.py:161`, populated
since M4) — no new column, no backfill. SQLite cannot alter an inline constraint, so this is a
**guarded table rebuild** inside `_migrate_schema`: detect via `sqlite_master.sql` (idempotent — a
UNIQUE already ending in `model_string` means do nothing), then `CREATE TABLE media_intents_new`
(identical columns, widened UNIQUE) → loss-free `INSERT … SELECT` → `DROP`/`RENAME` → recreate the
three indexes, one transaction. Old rows keep their identity semantics (every historical old-tuple
group holds exactly one `model_string`). Add the `model_string` identity parameter to
`find_media_intent` and the intent-lookup path (the insert already writes it) — **N4: keyword-only
with a default of the canonical model string**, so every pre-harness call site compiles and behaves
identically without edits.
**Territory invariants:** the M4 ledger API semantics (`:1016-1182`) are otherwise untouched —
`model_string` is the **only** approved widening, ever (widening by prompt content would authorise
unbounded re-spend, `MULTI_MODEL_SPEC.md` §14); `PRAGMA table_info` + `sqlite_master` stay the
schema-truth mechanism. **Named acceptance tests:** `test_first_seen_at_survives_recollect`,
`test_additive_migration_is_idempotent`, `test_unique_rebuild_is_idempotent_and_loss_free`,
`test_widened_tuple_accepts_two_models_refuses_duplicate`.

**IV-2 brief.** Standing preamble + `FINDINGS_SYNTHESIS.md` §1 D4 and §7. `collectors/virlo.py` only.
On the same-day idempotent-hit path (`:402-404`), re-materialise `virlo_corpus.yaml` and the media
manifest from the day's already-captured raw payloads (`Store.find_raw_payload`, `store.py:756`;
`raw_payload_path` written by `record_request`, `store.py:541-546`) instead of `break`-ing with
`selected_payload` left `None` (`:379-380`, guard at `:482`). The `/videos` and `/slideshows` subpath
pages are **separate captures with their own query signatures** — locate all of them; if only the agent
payload is recoverable, build a thin corpus and record it so the evidence layer classifies it
`evidence-thin` rather than `evidence-absent`. Replace the bare `except OSError: pass` (`:501-502`) and
the broader `except Exception: pass` on the manifest write (`:551-552`) with a **`trace.try_decision`**
degrade event *and* an entry in the in-memory degrade-reasons list — a failing trace write must not
erase the fact, and must not escalate the degrade into a crash. Use `fsutil.atomic_write_text` at
`:904-914`. **Territory invariants:** GET-only, never POST, never loop-poll; within-run fetch
idempotency and the "today's decision was already made" principle (`:374-378`) are preserved — this task
re-derives the *corpus artefact*, it does not re-fetch or re-decide. **Named acceptance tests:**
`test_idempotent_hit_rebuilds_corpus_without_fetch`,
`test_corpus_write_oserror_does_not_escalate_when_trace_also_fails`.

**IV-3 brief.** Standing preamble + `COMPOSITING_SPEC.md` **in full** + `STYLE_SYSTEMS_SPEC.md` §2 for
the zone recipes. `engine/src/hypeagent/compositing/**` only — **do not** edit `media_gen.py` (IV-7),
`pyproject.toml`, `config/` or `assets/` (IV-8). Public API via `__init__.py` exporting exactly
`render_slot`, `GroundSpec`, `CompositeResult`, `CompositingError`, and (N1)
`request_reserved_zone_prompt_fragment` — the one grounds-module function promptcraft may call
(§3a, §18 — deep module, simple
interface): the caller passes a contract, a slot, a style system and a ground *spec*, and gets back a
verified PNG; it never orchestrates ground-building, safe-zone checks, fitting or verification.
**Round-2 additions** (all inside the `compositing/` package, from `STYLE_SYSTEMS_SPEC.md`):
- **Rich-text runs** — mid-headline color emphasis inside one zone (one capability, two consumers:
  §2.13's `emphasis_ink` phrase and §3.1's `headline_split`). If the run-styling engine is cut for
  time, the **documented safe interim** is whole-zone single color with emphasis carried by weight,
  decision-logged — never a silent drop.
- **`photo_inset` support** — a small partial-area diffusion inset composited into an otherwise
  programmatic slot (§2.13's ~6%-of-canvas grid photo; the same partial-area pattern the logo policy
  reuses for `logo_zone` marks).
- **`reserved_text_zone` flow in `grounds.py`** — case-(b) photoreal slots (§2.10-§2.12):
  `request_reserved_zone_prompt_fragment` receives the slot's declared `reserved_text_zone` rect
  verbatim, `check_ground_safe_zone` validates the downloaded ground against the same rect; a failure
  degrades to a programmatic ground (never a re-roll loop), decision-logged per I5.
- **`paper_grain` + warmed paper** — the shared grain spec and warmed ground `#F1ECE1` consumed by the
  `paper` ground recipe (§3.1's shared block).

**Ratified-package additions (§13 items 19-22) — same package, no new module.** Read them together
with the flip: **this package is no longer the canonical renderer; it is the fallback rung and the
kill-switch destination.** That *raises* its stakes rather than lowering them — it is the only thing
standing between a text defect and a copy-only asset, so nothing here may be cut for time.
- **`artifact_zone` compositing (§13 item 22.3 — the Tier-1 mechanism).** `LayoutRecipe` gains
  `artifact_zone: RectPct | None` — `logo_zone` generalised to "a rect the model was told to leave
  **empty** and the compositor fills **pixel-exact**". `render_slot` composites the fetched assets
  supplied by `brand_assets` (IV-11) into it: the D4 device library — `browser_frame` (macOS-style
  chrome, 20-24px corner radius, soft shadow, the fetched `og:image` inside),
  `icon_row` / `icon_lineup` (fetched icon-form PNGs on a rule-spaced row), `node_diagram` (fetched
  icons as node glyphs). Real bytes only: this path never draws an approximation of a mark it could
  not fetch — that is Tier 2/3's job, and the tier decision is `brand_assets`'.
- **Emptiness verification.** Before compositing into an `artifact_zone`, verify the rect is
  substantially empty in the delivered render (the same statistic `check_ground_safe_zone` already
  computes for `reserved_text_zone`). A model that filled the zone with its own invented artifact
  fails the slot to the next rung rather than letting us paste real assets on top of fake ones.
- **Fallback-ground contract.** For an `llm_crafted` slot the fallback ground is **not** built here —
  it is a second `gpt-image-2-text-to-image` render with no text requested and `reserved_text_zone`
  honoured, handed to `render_slot` as a `GroundSpec` exactly like today's case (b). Single-model
  production (§13 item 22.3) means `grounds.py` never names a second provider.
- **Operator-override assets (§13 item 22.5).** `render_slot` consumes whatever `brand_assets` hands
  it and never reads the override folder itself — precedence lives in one place (IV-11).

**Territory invariants:** fail-closed on overflow (never truncate or clip — the engine's
truncation-never-accepted invariant); byte-identical output for identical inputs (the ledger's
idempotency and IV-7's local re-render both depend on it); fully offline; `fsutil` for every write and
hash; no Pillow import outside this package.

**IV-6 brief.** Standing preamble + `STYLE_SYSTEMS_SPEC.md` §1-§2, §5-§6. `promptcraft.py` only: derive
`register` from the generation mode in **every** path — delete the `return archetype, "editorial"`
hardcode at `:425`, the single line that made 100% of fa51's imagery editorial while the trend corpus's
winners were 96% photoreal. Thread `VisualPolicy.style_system` into `_build_style_section` (`:294-383`)
and enforce **one design system per asset** (§4.2 — all 5 carousel slots share one
`(register, archetype, generation_mode, style_system)` tuple). **`GENERATION_MODES`, round-2 final
state:** three NEW entries — `annotated_proof_ui` (§2.2), `cinematic_scene_hook` (§2.11),
`grid_photo_inset` (§2.13) — each with the full `ModeSpec` text the spec publishes in place, plus a
directive **amendment** to the existing `aspirational_lifestyle_scene` entry (§2.10).
**Ratified-package modes (§13 items 20-21, 23) — seven more, each with the full `ModeSpec` text
published in `STYLE_SYSTEMS_SPEC.md` §2.15-§2.22:** `website_showcase`, `robot_caricature`,
`concept_dashboard`, `anime_scene`, `meme_reaction`, `deadpan_memo`, `brand_promo_card`. Three of
them carry **pinned character descriptions** (D5) copied verbatim into every render so the characters
recur as brand assets rather than drifting: the robot — shared by `robot_caricature` **and**
`meme_reaction`, byte-identical in both (*rounded retro body in indigo `#302B87`, teal accents,
visible ink outlines, friendly single-lens eye, no human face, premium editorial-cartoon register —
never childish clip-art*) — and the anime mood (*hand-drawn painterly night scene, any human
character strictly from behind with the face never visible, teal/amber screen glow against dark, no
named persona*). The pin lives in **one** module constant that both modes interpolate; two
divergent copies of the robot description would be two different robots within a month — and the
round-6 v2 tombstone render already drifted slightly from the pinned design, which is the empirical
argument for pinning it verbatim rather than paraphrasing it per template (§13 item 24.4).
**Meme-class template requirements (§13 item 24):** `meme_reaction`'s canonical shape is a
**human-chaos panel vs brand-robot-serene panel** with **symmetric, time-stamped captions**
("Your ops team at 11 PM." / "The AI agent at 11 PM.") — the contrast *is* the joke, so the captions
must be parallel in structure and minimal in length; `deadpan_memo` gains the **RIP-tombstone** as a
second approved device variant (celebratory-graveyard grammar: party hat, confetti, the robot laying
a flower). Both carry the `instant_read` constraint in the prompt itself, not only in the critic.
**Persona carve-out, codified explicitly (§13 item 24.3):** cartoon humans **are allowed** in the
illustration and meme classes when the joke requires a human-vs-AI contrast — **strictly from behind
or with the face obscured, faces never visible, no named characters**. This is a carve-out from the
depiction rule only; `PersonaPolicy` (who *speaks*) is untouched — the institutional voice and the
no-named-individual rule stand exactly as they are.
Every other system reuses existing mode keys and must not add more.
**The builder is now the MAIN path, not a side path (§13 item 19.A).** R1's deterministic
template-prompt builder becomes `build_full_design_prompt(contract, slot, style_recipe, marks)` — the
canonical prompt for every `templated_diffusion` slot, and the wrapper that carries N-D's scene
description for every `llm_crafted` slot. It assembles, deterministically and with zero LLM:
the complete gated `on_image_text` verbatim with role/hierarchy labels (the same shape
`MULTI_MODEL_SPEC.md` §4.2 already specifies, and the ≤2-span/≤6-word cap is **lifted** for the same
reason); the D1 ground token (warm cream `#F6F1E7` + paper grain by default, cinematic-dark as the
secondary — no mid-gray, cold, saturated or gradient grounds in any default); the D2 type voice
(**exactly one** of editorial serif *or* heavy grotesque, oversized, 30-60% of canvas) with **exactly
one** emphasis token in a pinned accent hex; the D3 brand furniture (letterspaced small-caps kicker +
`HYPEDIGITALY` wordmark footer on every card-class slot); the D4 artifact device and its
`artifact_zone` "leave this region empty" instruction where one applies; the manifest `description:`
string for every named tool mark (§13 item 19.B); `promptcraft.GUARDRAILS` verbatim; and the
screens-off sentence on every scene/illustration prompt. It is governed through `govern()` like every
other prompt — determinism is not an excuse to skip the choke point.
**N1:** when assembling the RENDER brief for an `llm_crafted`
(case-b) slot, call `compositing.request_reserved_zone_prompt_fragment` with the slot's declared
`reserved_text_zone` — the fragment is the ONLY sanctioned negative-space request (0-6 adds the
function to the compositing `__init__` export list). **Selection itself is NOT this task** — the
two-stage selector is IV-10's `style_select.py`; this task only consumes the pinned
`VisualPolicy.register/archetype/mode/style_system` it produces.
**Named acceptance tests:** `test_register_is_never_hardcoded_editorial`,
`test_templated_diffusion_prompt_is_deterministic_and_makes_no_llm_call`,
`test_full_design_prompt_embeds_every_gated_span_verbatim`,
`test_full_design_prompt_carries_ground_type_emphasis_and_furniture_tokens`,
`test_character_pins_are_byte_identical_across_runs`,
`test_artifact_zone_prompt_asks_the_model_to_leave_the_region_empty`.

**IV-10 brief.** Standing preamble + `STYLE_SYSTEMS_SPEC.md` §4 **in full** (round-2 rewrite) +
`RENDER_CONTRACT_SPEC.md` §2/§8. The two-stage Virlo-weighted selector, at contract resolution:
- `style_select.py` (NEW leaf) — pure deterministic functions, **no LLM, no I/O**:
  `assign_format_classes(assets, quota, reweight_cfg, visual_profile, run_date) -> Stage1Assignment`
  (stage 1: quota → Virlo reweight moving **at most one** slot per run when a signal-bearing class
  gap ≥ `win_rate_gap` with `n_c ≥ min_sample`, silence-is-not-evidence → largest-remainder scaling to
  run size with fixed-class-order tie-breaks → `sha256(run_date)`-seeded rotation → content-plan-order
  assignment with **destination-compatibility substitution** to `designed_card` + a
  `quota_substitution` decision event) and `select_style_system(asset, format_class, topic_text,
  style_systems, seed, asset_index) -> str` (stage 2: the seven topic-tag regexes with their fixed
  precedence, class-default fallback, within-class seeded rotation, and the §4.1 step-9 pin of
  `register`/`archetype`/`mode` from the chosen entry). The reweight decision — shift or no-shift,
  with all class rates and sample counts — is always a decision event.
- **Ratified-package rewrite of stage 1 (§13 items 20-22; `STYLE_SYSTEMS_SPEC.md` §4.1 as amended).**
  Three mechanical additions, all deterministic, all decision-logged, none of which change the
  algorithm's shape:
  1. **Quota groups.** A quota key may name a *group* of classes holding `k` slots jointly; the group
     expands to `k` **distinct** members by the same `sha256(run_date)` seeded rotation over the
     group's fixed member order. This is how "double down" is expressed without deleting anything:
     the default quota is `serif_editorial: 1 · photoreal: 1 · artifact_showcase: 1 ·
     illustration: 2 (group: website_showcase, robot_caricature, anime_scene) · occasional: 1 (group:
     designed_card, editorial_grotesque, concept_dashboard)` — the two meme classes are NOT in this
     pool; they hold their own reserved slot (§13 item 25) — the operator's picked shapes get
     4 of 6 organic slots, the unpicked ones stay in a 1-of-6 rotation reserve, and the Virlo reweight
     can still promote a demoted class back (`reference/OPERATOR_FAVORITES_DNA.md`, selection
     re-weighting). A group's `n_c`/`win_rate_c` for the reweight is the **roll-up over its members'
     corpus labels**.
  2. **Reserved slots — brand promo AND meme (§13 items 20, 25).** Before the organic walk, reserve
     **additional** assets — appended to the run, never carved out of it, never consuming a Virlo
     quota token:
     - `batch_composition.reserved.brand_promo.slots_per_run` (default **1**, dial) ⇒ assets pinned
       to `format_class: brand_promo`, copy from config, skipped by the topic-regex stage entirely.
     - `batch_composition.reserved.meme.slots_per_run` (default **1**, dial **0-2**, §13 item 25) ⇒
       assets pinned to a meme class, **alternating between `meme_reaction` and `deadpan_memo`** by
       the same `sha256(run_date)` seeded rotation so consecutive runs alternate and a 2-slot run
       gets one of each. Unlike brand promo, a meme asset **is** topical: it runs the normal topic
       stage to pick its humour angle from the run's Virlo trends, and its copy is authored by N-C
       under the `instant_read` minimal-caption rules (§13 item 24).
     A 6-asset organic content plan therefore produces an **8-asset run** at the defaults
     (6 organic + 1 promo + 1 meme).
  3. **Carousel gate (§13 item 22.2) — `select_asset_format(asset, visual_profile, gate_cfg)`.**
     Instagram assets are **`single` by default**; `carousel` is selected only when the Virlo corpus
     for the asset's topic clears the same n-floor discipline the format reweight uses:
     `n_slideshow ≥ min_sample` (12) **and** `win_rate_slideshow − win_rate_single ≥ win_rate_gap`
     (0.25), with a "win" being weighted virality ≥ `virality_strong` (18). `evidence-thin` and
     `evidence-absent` never select `carousel`. The chosen format, both counts and both rates are
     always a decision event — including the no-carousel case, so an operator can see *why* today's
     run shipped singles. The format feeds `resolve_render_contract` and is persisted/read back on
     `--resume` exactly like the stage-1 class map.
  Most-constrained-first ordering: step 5 now walks assets in ascending order of
  **compatible-token count** (ties broken by content-plan order) instead of raw content-plan order —
  with nine organic classes and destination-restricted members, first-come-first-served produced
  avoidable `quota_substitution` events. Deterministic, and it strictly reduces substitutions.
- **ONE config block for batch composition (§13 item 25).** Every dial above lives under a single
  `generation.batch_composition:` block, not scattered across `generation.*` — an operator planning a
  batch should read one block, and a reviewer should be able to see the whole run shape at a glance:
  ```yaml
  generation:
    batch_composition:
      organic_assets: 6
      destination_split: {linkedin: 3, instagram_feed: 3}
      language_by_destination: {linkedin: en, instagram_feed: en}   # cs is a supported switch
      format_quota: {serif_editorial: 1, photoreal: 1, artifact_showcase: 1, illustration: 2, occasional: 1}
      format_quota_groups:
        illustration: [website_showcase, robot_caricature, anime_scene]
        occasional:   [designed_card, editorial_grotesque, concept_dashboard]
      format_quota_reweight: {min_sample: 12, win_rate_gap: 0.25, virality_strong: 18}
      carousel_gate:         {min_sample: 12, win_rate_gap: 0.25, virality_strong: 18}
      reserved:
        brand_promo: {slots_per_run: 1, destinations: [instagram_feed], messages: [...], cta_text: "..."}
        meme:        {slots_per_run: 1, destinations: [instagram_feed], classes: [meme_reaction, deadpan_memo]}
  ```
- `config_load.py`: the `batch_composition` schema above, optional-keys idiom — **absence of
  `format_quota` disables the entire two-stage selector**
  and the degrade path is **the Phase-8 rotation DIRECTLY** (R18: the never-shipped round-1
  three-topic-pair selection layer is deleted, not kept as an intermediate rung — one selector, one
  degrade); **absence of `carousel_gate` ⇒ `single` always** (the conservative direction); **absence
  of `reserved.brand_promo` / `reserved.meme` ⇒ no such asset**; absence of the whole
  `batch_composition` block ⇒ pre-W8-11 behaviour, so a theme predating this wave still loads.
  Schema only; values are IV-8's.
- `resume_state.py`: persist the stage-1 output (`format_classes: dict[str, str]` + the reweight
  decision record) following III-5's field idiom; on `--resume` it is **read back, never re-derived**.
- **Territory invariants:** the evidence gate stays first and absolute (`evidence-absent` blocks before
  either stage runs; `evidence-thin` never changes the selection); destinations outside
  {linkedin, instagram_feed} always use the Phase-8 rotation; `stages.stage_copy` wiring is IV-8's,
  not this task's.
- **Named acceptance tests:** `test_same_run_date_reproduces_identical_assignment`,
  `test_reweight_moves_at_most_one_slot_and_respects_sample_floor`,
  `test_largest_remainder_scaling_ties_break_by_class_order`,
  `test_linkedin_asset_never_receives_editorial_grotesque`,
  `test_absent_format_quota_falls_back_to_phase8_rotation`,
  `test_group_expands_to_distinct_members_and_rotates_by_run_date`,
  `test_demoted_class_can_be_promoted_back_by_virlo_reweight`,
  `test_brand_promo_is_appended_and_never_consumes_the_virlo_quota`,
  `test_carousel_requires_slideshow_evidence_above_the_floor`,
  `test_thin_or_absent_evidence_never_selects_carousel`,
  `test_format_decision_is_always_a_decision_event`.

**IV-11 brief.** Standing preamble + `STYLE_SYSTEMS_SPEC.md` §2's logo-policy block, §5.11 and §5.12
(the three-tier ladder) + `SIM_REPORT.md` round 3 (F13-F15). `brand_assets.py` (NEW leaf — **renamed
from the never-built `logo_assets.py`**, because the module now resolves a tool's *product visual* as
well as its mark and a second parallel fetcher would be exactly the forked system §2 forbids).
Stdlib-only (`urllib` behind the injectable `Fetcher` idiom from `collectors/base.py`).

**Public API — one function, deep module (§18):**
`resolve_brand_assets(tool: str, *, fetcher) -> BrandAssets` where `BrandAssets` carries
`tier: 1|2|3`, `logo_path: Path | None`, `product_visual_path: Path | None`, `description: str`,
`source: str`. The caller passes a tool name and gets back "here is what you may honestly depict, and
at which tier" — it never orchestrates manifest lookup, fetching, parsing or degradation.

**Resolution order, in this order, each step decision-logged:**
1. **Operator override (§13 item 22.5, OPTIONAL and never blocking).** If
   `assets/logos/override/<tool>/logo.png` and/or `product.png` exist, they **win over everything
   below**. No operator is ever *required* to supply a file; this folder is a manual escape hatch,
   documented in `NAVIGATION.md`, empty by default, and its absence is not a degrade.
2. **Manifest (`assets/logos/manifest.yaml`, IV-12).** `description` is always taken from here (it is
   the prompt-injection string, F8's ~95%-fidelity mechanism, and it works even when no byte is ever
   fetched). `icon_url` is lazily downloaded on first need into `assets/logos/cache/` (permanent
   cache, checksum recorded, atomic write via `fsutil`).
3. **Runtime site fetch (F14) — the unknown-tool path.** For a tool with no manifest entry: GET the
   tool's own site HTML, parse `og:image` (the real vendor product visual) and
   `apple-touch-icon`/`favicon` (the real mark) — ~3 HTTP calls, results cached permanently.
4. **Tier assignment.** Tier 1 = mark **and** product visual available; Tier 2 = mark only; Tier 3 =
   neither.

**Binding rules.**
- **Browser User-Agent on every request, no exceptions.** A bare `urllib` UA gets **403** from vendor
  sites (`lovable.dev`, verified round 3) *and* from the kie result CDN. Reuse the single UA constant
  I-1 defines; do not spell it twice.
- **SSRF discipline (`CODING_GUIDELINES.md` §12).** GET-only, no polling, no redirects to private IP
  ranges, fetches restricted to the tool's own origin (and the origin the manifest names), size and
  content-type validated before the bytes are written, timeout on every call.
- **Never raises through the repair path.** A missing entry, a 403, a malformed page, a timeout — all
  return a typed result carrying the tier actually achieved, so the caller degrades instead of
  crashing mid-render.
- **No brand binaries are ever committed** — the manifest of URLs plus the (gitignored) cache and the
  (gitignored, optional) override folder are the whole story.
- Offline-testable with a fixture fetcher; every path in the ladder has a fixture.
**Named acceptance tests:** `test_second_resolve_hits_cache_without_fetch`,
`test_missing_manifest_entry_is_typed_error_not_crash`,
`test_all_fetches_send_browser_user_agent`,
`test_og_image_and_apple_touch_icon_are_parsed_from_site_html`,
`test_operator_override_wins_over_manifest_and_fetch`,
`test_tier_degrades_from_1_to_2_to_3_on_missing_assets`,
`test_fetch_refuses_private_ip_and_off_origin_redirect`.

**IV-12 brief.** **Websearch task — executable ONLY by main or a web-capable agent
(`documentation-engineer`); a sandboxed `python-pro`/`agent-pipeline` executor cannot do this work.**
Author `assets/logos/manifest.yaml`. **Schema, ratified 2026-08-08 (§13 item 19.B) — three fields per
tool, not one URL:**

```yaml
<tool>:
  description: "<precise verbal description of the mark, for prompt injection>"
  icon_url:    "<direct PNG — ICON FORM, never the wordmark>"
  source:      "<official press-kit / brand page the icon came from>"
```

- `description` is the field that does most of the work: F8 showed that *naming* a mark yields ~50%
  fidelity while *describing* it ("Anthropic Claude coral starburst", "Zapier orange asterisk",
  "Gmail multicolour M envelope") yields ~95% — and it costs nothing at render time. Write each one
  from the real mark, in the register the live-verified round-2 prompts use
  (`simulation/round2/prompts/*3_tool_stack*`, `*4_workflow_map*`).
- `icon_url` **must be the icon form, not the wordmark** — round 2's nano-banana-pro reference probe
  reproduced the supplied file faithfully, which meant it reproduced the *wordmark* because the
  reference file was a wordmark (F8). The icon is what a row, chip or node needs.
- **Seed set, required BEFORE the confirmation run (§13 item 19.B):** Claude/Anthropic,
  ChatGPT/OpenAI, Zapier, Gemini, Notion, Make, n8n, Calendly, Gmail, Loom, Airtable — eleven tools,
  chosen as the marks the twenty-nine systems' briefs actually name. Treat model-drawn Claude and
  Zapier marks as **expected-fail** in `logo_fidelity_ok` (all three models missed Claude's in round
  1; only gpt-image-2 drew Zapier's current asterisk).
- Official sources only — no logo-aggregator sites; respect §3.6's nominative-use governance (the
  Claude coral entry cites §3.6 explicitly). The manifest is consumed lazily at run time by IV-11 —
  authoring it during plan execution is what keeps websearch out of the engine.

**IV-4 brief.** Standing preamble. `ranking.py` only: key the R1 freshness window on `first_seen_at` /
publish date rather than the upsert-refreshed `retrieval_time` (`:644-652`, `:715-764`).
**Territory invariants:** stale candidates skip scoring without touching
`observe_cluster`/`resolve_resurgence` (`:720-724`); quantile banding and the top-N cap unchanged.

**IV-5 brief.** Standing preamble + `FINDINGS_SYNTHESIS.md` §3 *Evidence posture* +
`RENDER_CONTRACT_SPEC.md` §2 `VisualPolicy`. `analysis.py` only: add
`evidence_class ∈ {evidence-backed, evidence-thin, evidence-absent}` computed from the **durable store**
keyed (theme, date-window) via IV-1's API — never from this run's fetch side effects. Expose
`resolve_visual_evidence(...) -> VisualPolicy` as the single producer, preferring the run corpus and
falling back to the store's most recent capture inside the window. `evidence-absent` ⇒ image generation
blocked (`media.require_visual_evidence`), reason surfaced for the digest banner; `evidence-thin` ⇒
generate + review-required. `VisualPolicy` must round-trip through `resume_state` (III-5) — it is
persisted, not re-derived, on `--resume`. **Round-2 addition:** each Virlo corpus item carries a
**`format_class` label** (`designed_card` / `photoreal` / `editorial_grotesque` / `serif_editorial`),
computed deterministically by the corpus classifier here and exposed on `VisualProfile` as per-class
counts + win-rates (weighted virality ≥ 18 = a "win") — this is the input contract for IV-10's Virlo
reweight (`STYLE_SYSTEMS_SPEC.md` §4.1 step 2); the labels are facts about corpus items, never asked
of an LLM. **Territory invariants:** N-A never fails the run;
`visual_profile` stays deterministically computed in Python, never asked of the LLM (`:36-39`,
`:653-745`); the `ViralPlaybook` YAML round-trip (`:235-249`, `:844-912`) stays backward-compatible.
**Named acceptance test:** `test_evidence_class_from_durable_store_not_run_fetch`.

**IV-7 brief.** Standing preamble + `COMPOSITING_SPEC.md` §3, §5, §6, §7 + `SIM_REPORT.md` F13-F18.
`media_gen.py` only.
- **THE RENDER LADDER (§13 item 19.A) — this task's headline, implemented as a state walk, never as
  nested `if`s.** For every slot, in this order, each transition an `advance()` call with a
  `trace.decision` (I5):
  1. **Canonical full-design render.** Submit the governed full-design prompt (IV-6's builder) on the
     canonical route `img-standard-gpt-image-2`, attempt 1. **Resolution pin, applied mechanically
     from `route.resolution_constraints`, never hand-written per call site:** an aspect listed in
     `unsupported_aspects_at_2k_4k` forces `resolution: "1K"` — Instagram's `4:5` is in that list, so
     every IG render pins `1K` even when config says `2K`. Download with the browser UA (I-1).
  2. **Per-glyph text verification** (II-4's `text_matches`). Pass ⇒ `DELIVERABLE`.
  3. **One retry** — attempt 2, same governed bytes, same identity semantics, `ATTEMPT_MAX = 2`
     unchanged. Re-verify.
  4. **Second failure ⇒ `FALLBACK_COMPOSITING`.** For a `templated_diffusion` slot the ground is the
     style recipe drawn programmatically; for an `llm_crafted` slot the ground is a **second
     `gpt-image-2-text-to-image` render with no text requested** and the slot's `reserved_text_zone`
     honoured (case (b), single-model — §13 item 22.3). Pillow typesets the gated strings;
     draw-then-compare produces `qa.status = "composite-verified"`; no vision call is consumed
     (the slot already spent two).
  5. **Anything unavailable at rung 4** — compositing disabled, `TypesetOverflowError`, verification
     mismatch, missing glyph — ⇒ `BLOCKED_NO_IMAGE`, asset `copy_only`. **Never a clipped, truncated
     or unverified image.**
  `canonical_render_enabled: false` (the kill switch) enters at rung 4 directly for every slot,
  which is exactly the pre-flip behaviour — that is what makes the flip reversible by config alone.
  **The order is enforced by `asset_model.advance()`'s edge set (I-0), so a future edit cannot
  quietly promote the fallback ahead of the gate** (invariant RL1).
- Route slots by the **B1 three-category routing** (`llm_crafted` / `templated_diffusion` /
  `programmatic`), resolved from the style system via the amended
  `contract.diffusion_touched_slots()` — **N2: the routing decision is the existing
  `resolve_render_route()` extended, named and called; never re-implemented inline.** Programmatic
  slots make **no provider
  call**, cost `$0.00`, and take a `media_intents` row with `route_id="composite-local"` and no
  `task_id`; they **must not** consume `per_run_count_cap` (a spend guard, not a volume guard —
  `COMPOSITING_SPEC.md` §6). They settle through the **shared `_settle_intent`** helper extracted in
  I-1. `templated_diffusion` slots submit their deterministic prompt (built by IV-6) through the same
  choke point and settle like any paid slot.
- `_resolve_one_row` gains its **first** branch: `route_id == "composite-local"` → re-render
  deterministically and locally (free, no network); if the slot is not in this run's contract, mark
  `state='failed'`, terminal, with a reason. **Never `submitted_unknown`, never a provider call.**
- Record `qa.status = "composite-verified"` from the draw-then-compare verdict so QA totality (I4) is
  satisfied without a vision call; composite-verified images are excluded from the vision-QA outage
  denominator computed in `stages.py`.
- **Partial-area diffusion routing** (round-2 logo policy + §2.13): a slot that is otherwise
  programmatic but carries a diffusion `logo_zone` or `photo_inset` makes exactly one provider call
  for that partial surface and still counts as one diffusion-touched slot for budgets (§2.7's census);
  a slot whose ground already diffuses renders its marks in that same call — never a second call.
- **Mark repair path** (`STYLE_SYSTEMS_SPEC.md` §5.11, wiring II-4's `logo_fidelity_ok`): on
  `logo_fidelity_ok == false`, resolve the tool's real mark via `brand_assets.resolve_brand_assets`
  (IV-11; manifest from IV-12, operator override, lazy fetch, permanent cache), composite it over the
  SAME `logo_zone` rect, and **re-run QA exactly once**; a second failure fails the slot closed,
  decision-logged. The repair is ledger-visible (no new provider call — compositing is local) and its
  provenance names the repair and the tier used. A tool that resolves to Tier 3 ⇒ no repair, slot
  fails closed with a reason naming the tool.
- **Unknown-tool three-tier ladder (§13 item 19.C — the integrity rule, F13-F15).** When a slot's copy
  names a tool that has no manifest entry, `brand_assets` decides the tier and this task honours it:
  **Tier 1** — the render carries an `artifact_zone` the model was told to leave empty, and the
  fetched real logo **and** real product visual (`og:image`) are composited into it **pixel-exact**
  by IV-3 (§13 item 22.3 replaced the `image_input` reference render with this — it is a paste, not a
  redraw, which removes F15's caveat entirely); **Tier 2** — fetched mark only, over the system's
  styled typography card, no product visual anywhere; **Tier 3, fail-closed** — a **clearly
  ILLUSTRATIVE** stylized UI plus a name chip, and the prompt says so in those words.
  **The integrity line, codified and non-negotiable: the engine NEVER renders a diffusion-invented
  "real-looking" screenshot of a real product.** A plausible invention is worse than an obvious one
  because a casual viewer cannot tell (F13). Fictional UI is fine and is a whole style class
  (`website_showcase` — invented business, greeked body text); a *real* product's UI is Tier 1 real
  bytes or nothing. Invariant **LG3**.
- **Territory invariants:** write-ahead order, spend reconciliation (delta sum == ledger == balance —
  test-enforced) and the circuit breaker are unchanged; a composited image is still a delivered image and
  still needs a verdict; the phase-0 quarantine from I-1 still applies to non-composite rows.
- **DoD addition (Risk 1):** the `_resolve_one_row` branch order matches I-1's comment block exactly —
  this task fills branch 1 (composite-local) above the quarantine branches, never reorders.
- **Named acceptance tests:** `test_interrupted_composite_row_is_not_submitted_unknown`,
  `test_composited_slot_makes_no_provider_call_and_costs_zero`,
  `test_text_defect_retries_exactly_once_then_falls_back_to_composite`,
  `test_composite_fallback_is_unreachable_before_two_text_defects`,
  `test_kill_switch_enters_the_ladder_at_the_composited_rung`,
  `test_instagram_render_pins_resolution_1k_mechanically`,
  `test_unknown_tool_tier1_composites_fetched_assets_into_an_empty_artifact_zone`,
  `test_unknown_tool_never_renders_invented_real_ui`.

**IV-8 (conductor) — aggregating writes.**
- `engine/pyproject.toml`: add `Pillow>=12,<13` (§13.2 approved).
- `assets/fonts/**` — **round-2 font vendoring** (`STYLE_SYSTEMS_SPEC.md` §3.5, operator-locked):
  vendor **Montserrat** (intended sans, unchanged) **plus Playfair Display** (Regular, Italic, Bold,
  **Bold Italic**; Black Italic optional for `headline_split`) **and Lora** (Regular, Italic, Bold) —
  all SIL OFL 1.1, licence file alongside each family per the NotoSans precedent in
  `assets/fonts/README.md`. **Czech-diacritics glyph verification is a ship gate**: re-run the
  README's exact corpus (`ěščřžýáíéúůďťňó / ĚŠČŘŽÝÁÍÉÚŮĎŤŇÓ`, `Kč`) on the ACQUIRED files, never
  assumed from published coverage; additionally run the **`ig_value_sheet` `type_floor: 0.0185`
  legibility pass on the vendored Lora file at that exact size** (§2.9/§3.5 — the standard glyph test
  does not cover it) and record the result before that system's first ship. Until a family lands AND
  verifies, every `*_fallback` stays `NotoSans-Variable.ttf` — fallbacks are the current truth, the
  families the intent. (Acquiring binaries needs web access — conductor work, like IV-12.)
- `config/style_guide.yaml`: the **twenty-nine-system** `style_systems:` map (eleven from §3.1 +
  the eighteen ratified entries §3.1 appends verbatim from `STYLE_SYSTEMS_SPEC.md` §2.15-§2.22 —
  nine shapes × their `ig_`/`li_` variants) — per-slot
  `zones:`, `ground_source`/`text_render_mode` (**the style system is their ONLY declaration — B2;
  the theme YAML carries none**), `format_class` on every entry, `reserved_text_zone` on
  case-(b) slots, the shared `paper_grain` block and warmed paper `#F1ECE1`, §3.6's accent tokens
  (`highlight_bar: "#E8A63B"` single-purpose; coral = Claude mark only, never decorative); the
  archetype `register:` bindings from §3.2 (round-2 rows **and** the ratified rows for the new
  classes); the §3.4 per-destination `visual.default_archetypes` changes; the **D1 ground defaults**
  (warm cream `#F6F1E7` + paper grain as the organic default, cinematic-dark as the secondary — no
  mid-gray/cold/saturated/gradient ground survives as any system's default), including
  **`ig_value_sheet` restyled from its dark terminal ground onto the cream serif-editorial recipe**
  (`reference/OPERATOR_FAVORITES_DNA.md` anti-signal: the dark dense list card was the one
  technically-clean render the operator did not pick); the **D3 furniture** (`kicker_zone` +
  `wordmark_zone` on every card-class system); the **D4 `artifact_device`** field; and the
  `hard_dont_exemptions:` lists — **only** `brand_promo`-class systems may carry §5.6-§5.10 and only
  `concept_dashboard` may carry §5.6 (consistency check 11 refuses any other). **R2 stands** in its
  fallback form — `ig_stat_slab`'s cover text is ours to typeset when the ladder reaches rung 4.
  **R3 is REVERSED** (§13 item 19.A): no system is "fully programmatic" any more, the canonical
  diffusion-TEXT surface is **every slot**, and the ≤2-span/≤6-word cap is deleted rather than
  universalised.
- `config/themes/hypedigitaly.yaml`: `media.compositing` block; **the whole
  `generation.batch_composition` block** (schema landed in IV-10) with the ratified defaults —
  `organic_assets: 6`, `destination_split {linkedin: 3, instagram_feed: 3}`,
  `language_by_destination` all `en`, quota `serif_editorial 1 · photoreal 1 · artifact_showcase 1 ·
  illustration 2 · occasional 1` with its two groups, `format_quota_reweight` and `carousel_gate`
  both `{min_sample: 12, win_rate_gap: 0.25, virality_strong: 18}`, and the two reserved slots:
  `brand_promo {slots_per_run: 1, destinations: [instagram_feed]}` with the three ratified service
  messages seeded and the CTA pill text **verbatim** (§13 item 20), and
  `meme {slots_per_run: 1, destinations: [instagram_feed], classes: [meme_reaction, deadpan_memo]}`
  (§13 item 25).
- `config/model_registry.yaml` — **the canonical route flip (§13 items 19.A / 22.3):**
  (a) add `img-standard-gpt-image-2` (`model_string: gpt-image-2-text-to-image`, 6 credits ≈ $0.03
  live-confirmed, `full_text_render: true`, `resolution_constraints.unsupported_aspects_at_2k_4k:
  ["5:4","4:5","3:1","1:3","9:21"]`) and point `route_by_class` / `defaults.draft_route` /
  `defaults.fallback_draft_route` at it; (b) mark the incumbent `img-standard-nano-banana-pro`
  (`model_string: nano-banana-2`) **`status: reserved`** — retained, documented, referenced by
  nothing, and refused by `resolve_route()` (the same built-but-disabled pattern as `tiktok`, §13.4);
  (c) add `img-specialist-nano-banana-pro` (`model_string: nano-banana-pro`, `image_input_max: 8`)
  also **`status: reserved`**, so the `image_input` capability is on record for a future re-enable
  without being reachable now; (d) keep the naming-collision comment block — `img-standard-nano-
  banana-pro` carries `nano-banana-2`, `img-specialist-nano-banana-pro` carries the real, distinct
  `nano-banana-pro` — and extend it with the flip's own note, so nobody "restores" the old default;
  (e) remove `people_free_composition` (contradicts the W8-10 person policy).
  *(The two `test`-tier challenger routes are Wave IV-B's, not this task's.)*
- `stages.py`: evidence resolution into the contract; digest banner for blocked assets; compositing
  wiring; **stage-1 selection wiring** — call `style_select.assign_format_classes` once per run in
  `stage_copy` immediately before the per-asset loop, then `select_style_system` per asset feeding
  `resolve_render_contract`; persist the stage-1 map + reweight decision via IV-10's resume fields.
  **N5 — the explicit `--resume` branch:** when resuming, `stage_copy` reads `format_classes`, the
  per-asset **`format` decision** (single/carousel, §13 item 22.2), the brand-promo reservation and
  each asset's `style_system`/`VisualPolicy` from `resume_state.yaml` and **never calls
  `assign_format_classes`/`select_asset_format`/`select_style_system` again** — re-derivation is the
  contract-sha-drift path III-5/IV-10 exist to close, and a carousel that re-derives as a single
  mid-run would strand four paid slots.
  **Ratified-package wiring:** resolve `generation.language_by_destination` into the contract before
  authoring (§13 item 22.1 — server-side, never model-chosen); append the reserved `brand_promo`
  asset(s) to the run's asset list after the organic loop is planned and route them to
  `copy_gen.build_brand_promo_asset` (§13 item 20). **N3:** set `generation.destinations_enabled:
  [linkedin, instagram_feed]` in the theme YAML and wire the read at contract resolution (schema
  landed in I-0) — no tiktok asset is planned, crafted or spent on while disabled (§13.4).
- `NAVIGATION.md`: new leaves (`style_select`, `brand_assets`), `assets/logos/**` (manifest, the
  gitignored `cache/`, the optional gitignored `override/` folder — §13 item 22.5), font files, the
  new config keys (`language_by_destination`, `carousel_gate`, `brand_promo`, `format_quota_groups`,
  `render_contract.canonical_render_enabled`).
- **And the single version bump:** `CONTRACT_VERSION` 3 → **4** in
  `render_contract.py` plus the matching `contract_version: 4` in the theme YAML (consistency check 9
  enforces they agree). This is the only wave that bumps it — see §9.6.

**Barrier verification:** full pytest green, plus a **zero-media-spend rehearsal** from the repo root
with `generation.media.dry_run: true`:
```
cd C:/Users/Pavli/Desktop/HypeDigitaly/GIT/HypeAgentSocials && python -m hypeagent
```
**This is not a free run — `dry_run` suppresses *media* spend only; the LLM wallet still spends roughly
$1-2.** Expect: exit success, full plan + forecast, composited slots actually written to `pack/media/`,
`process_summary.md` regenerating (`python -m hypeagent --summarize <run_id>`). Set
`generation.llm.enabled: false` as well for a structurally-complete zero-cost rehearsal (every LLM node
degrades, compositing and planning still exercise). Revert both flags before Wave IV-B.

---

### WAVE IV-B — Multi-model test harness (`MULTI_MODEL_SPEC.md`)

*Side-by-side test renders with FULL slide text in-image, per-model output folders, N-E QA +
scoreboard. **Roles inverted and the track disabled by the ratified package (§13 items 19.A / 22.3):**
`gpt-image-2-text-to-image` is no longer a candidate — it is the **canonical incumbent**, and its own
canonical rows are the scoreboard's anchor. The two remaining challengers are `nano-banana-pro` and
`nano-banana-2`, and the whole track ships **built and `enabled: false`** — single-model production.
Governing decision unchanged where it still applies: test renders are **evidence, never product**;
invariants T1-T6 (`MULTI_MODEL_SPEC.md` §15) are binding whenever the flag is flipped. **Scope is
slimmed accordingly:** the registry two-door + reserved-route refusal, the config surface, the leaf
module and the scoreboard are all built (so the flip is a config change, not a project), but the
default run submits **zero** test renders and the $3 wallet does not appear in §9.3's active
arithmetic. A separate wave because the harness consumes Wave IV's final shapes (widened ledger from
IV-1, style recipes, the composited-fallback comparison target) and its `media_gen.py`/
`config_load.py` edits would collide with IV-7/IV-10 as siblings.*

**Why build it at all if it is off?** Because the evidence it was commissioned to produce was
produced instead by the 44-render simulation, and the *next* model question will arrive anyway. The
machinery that keeps a candidate model structurally unable to touch delivery is exactly what makes
turning it on safe; deleting it would mean rebuilding it under time pressure the day a challenger
appears. It is retained on the same terms as `tiktok` (§13.4): configured, coherent, checked by the
consistency checks, and unreachable.

**Shape:** b + c. **Triggers:** (a) no — `MULTI_MODEL_SPEC.md` §2 names every file. (b) no — four
build tasks. (c) **neutralised**: IV-B-2 *imports* the registry API IV-B-1 builds, so IV-B-1 is a
barrier — `test_render.py` (leaf) and `media_gen.py` are different files but sequence on the import
dependency, never sibling-parallel. → **no orchestrating parent.**

| Task | Executor | Depends on | Path set (touch nothing else) |
|---|---|---|---|
| **IV-B-1** *(barrier)* Registry: test tier, capability fields, two-door resolution | `agent-pipeline` | IV-* | `engine/src/hypeagent/media_gen.py` |
| **IV-B-2** `test_render.py` leaf — runner, prompt builder, scoreboard, §12 config checks | `agent-pipeline` | IV-B-1 | `engine/src/hypeagent/test_render.py` (NEW) |
| **IV-B-3** `TestRenderConfig` | `python-pro` | IV-* | `engine/src/hypeagent/config_load.py` |
| **IV-B-4** Digest scoreboard section | `python-pro` | IV-* | `engine/src/hypeagent/process_summary.py` |
| **IV-B-5** Wire-in + routes + config values | **main (conductor)** | IV-B-1…IV-B-4 | `engine/src/hypeagent/stages.py`, `config/model_registry.yaml`, `config/themes/hypedigitaly.yaml`, `NAVIGATION.md` |
| **IV-B-6** Tests | `test-engineer` | IV-B-5 | `engine/tests/test_test_render.py` (NEW), `test_media_gen.py`, `test_store.py`, `test_config.py`, `test_process_summary.py`, `test_stages.py`, `test_phase3_pipeline.py` |

All briefs: standing preamble + `MULTI_MODEL_SPEC.md` **in full** + `reference/kie-models/*.md` (API
ground truth — model strings, params, constraints, price snapshots are verified against these, not
memory).

**IV-B-1 — scope.** `media_gen.py` only. `ModelRoute` gains the five capability fields
(`full_text_render`, `image_input_max`, `prompt_max_chars`, `resolution_constraints`,
`output_format_supported` — loader defaults keep every existing route loading unchanged) **plus
`status: "active" | "reserved"` (default `"active"`, §13 item 22.3)**;
`load_model_registry` parses them and enforces the **registry-side** §12 checks (1, 3, 5, 8).
**Two-door resolution:** `resolve_route()` refuses any `test`-tier route regardless of
`tier_ceiling` **and refuses any `status: reserved` route**; new `resolve_test_route(route_id)`
refuses any non-`test` route. The `reserved` door is what lets `nano-banana-2` and
`nano-banana-pro` stay fully specified in the registry — price, capabilities, comments, consistency
checks — while being unreachable from delivery, the same shape as `tiktok`'s
`destinations_enabled` exclusion.
**Amended §12 check 8 (`MULTI_MODEL_SPEC.md`, applied spec-side by 0-6).** "No two routes share a
`model_string`" cannot survive the flip: `nano-banana-pro` is legitimately both a reserved canonical
route and a test-tier challenger. The rule becomes **"no two routes of the same tier class share a
`model_string`; a `model_string` may appear on at most one canonical-tier route and at most one
`test`-tier route, and when it does the registry comment must state the dual role."** The ledger
consequence is handled in IV-B-2's skip rule, not by widening the identity tuple — `model_string`
remains the only approved widening, ever. Phase-0 adoption filter: the canonical
unresolved-intent pass adopts only rows whose `route_id` resolves non-test (unresolved *test* intents
are IV-B-2's runner's to adopt). `CREATE_TASK_ALLOWED_KEYS` gains `"resolution"` (`KieClient` itself
is a transport and is NOT modified). **Territory invariants:** `_submit_new` stays the sole
`create_task` call site; nothing in `media_gen` imports `test_render` (import direction is strictly
`test_render → media_gen`).
**DoD addition (Risk 1):** the `_resolve_one_row` branch order matches I-1's comment block exactly —
this task fills branch 2 (test-tier skip) between composite-local and quarantine, never reorders.
**Named acceptance tests:** U1 (`test_resolve_route_refuses_test_tier`,
`test_resolve_test_route_refuses_canonical_tier`), `test_phase0_adoption_skips_test_rows`,
`test_resolve_route_refuses_reserved_route`,
`test_same_model_string_on_one_canonical_and_one_test_route_loads`,
`test_same_model_string_twice_in_one_tier_class_raises`.

**IV-B-2 — scope.** `test_render.py` (NEW leaf; may import stdlib, `fsutil`, `asset_model`,
`render_contract`, `media_gen`, `promptcraft`, `store`, `trace`, `config_load`).
- `build_test_render_prompt(contract, slot, style_recipe, route)` — **pure, deterministic, no LLM**:
  the slot's complete gated `on_image_text` verbatim in `<<…>>` with role labels (the ≤2-span/≤6-word
  diffusion-text cap is LIFTED here — it is an N-D authoring constraint and test prompts never pass
  through N-D; no canonical validator weakens), the style-system recipe (palette hexes, type intent,
  zone geometry in prose), `promptcraft.GUARDRAILS` verbatim, persona + fake-UI rules, aspect +
  resolution intent. Raises on `len > route.prompt_max_chars` (caught by the isolation boundary).
- **R22 — build + govern ONCE per slot.** The prompt is built and passed through the **same
  `render_contract.govern()`** exactly once per slot; the resulting single `GovernedPrompt` is then
  submitted to **both** routes — same-bytes across models is a structural guarantee (experimental
  validity), never re-derived per route. Same claim gate on exact bytes, same leak/banned checks; no
  test-mode branch, no new `GovernedPrompt` fields (T3/I1 — the AST guard extends to this call
  path). Submission goes through `_submit_new` (or an extracted shared helper with the identical
  `GovernedPrompt`-typed signature).
- `TestRenderRunner`: walks the finished asset's slots × enabled test models **strictly after** the
  canonical loop; write-ahead intent row keyed by the widened tuple **before** the HTTP call;
  single-shot attempts (`attempt` always 1 — a QA fail is scoreboard data, never a regeneration);
  per-route input construction (§4.4 — the 4:5-pins-`"1K"` rule applied mechanically from
  `resolution_constraints`; `output_format: "png"` for nano-banana-pro; no `image_input` in W8-11);
  **separate test wallet** `spent_usd_test` checked before every submission — on exhaustion, skip all
  remaining test renders with ONE decision event; test spend never touches
  `per_run_count_cap`/`per_run_usd_cap` but DOES land in the ledger, the day cap and the
  circuit-breaker reconciliation; outputs to `<asset_dir>/models/<model_string>/<slot_basename>.png`
  + provenance sibling (canonical schema + `route_id`, `tier: test`, `resolution`,
  `full_text_render`, `expected_text`, `delivered_model`); unresolved test-intent adoption
  (resolve-by-query, reconcile, file into `models/` — even when `enabled` flipped false); test QA via
  the same N-E path with the **Czech diacritics-sensitivity instruction** (`š`≠`s`, `ř`≠`r` — a
  dropped diacritic is a FAIL), drawing from the dedicated `test_render.qa_reserved_calls` reserve —
  exhaustion ⇒ `qa: skipped-test-qa-budget`, counted *unassessed*, never a pass (T6).
- **Skip rule for a dual-role `model_string` (new, forced by IV-B-1's amended check 8).** Before
  submitting a test render for (slot, model), check whether a **canonical** ledger row already exists
  for that (slot, `model_string`); if it does, skip — one row per (slot, model) is preserved
  (invariant H4/T4), and the scoreboard reads that canonical row for the pair. You never need a
  side-by-side of a model against itself.
- `aggregate_scoreboard()` — computed from provenance YAMLs + ledger rows (never in-memory state, so
  a resumed run scores correctly), written to `<run_dir>/test_render_scoreboard.yaml` via
  `fsutil.atomic_write_text`; §9.2 metrics per model. **Three rows under the flip:** the canonical
  incumbent `gpt-image-2-text-to-image` (from its own canonical rows — it is the anchor, not a
  candidate), and the two challengers `nano-banana-pro` and `nano-banana-2`. The
  composited-fallback path gets its own anchor row too (text-perfect by construction), which is what
  makes "was the flip worth it?" answerable from the scoreboard rather than from memory.
- **Disabled by default (§13 item 22.3).** With `test_render.enabled: false` the runner returns an
  empty `TestRenderResult` after one `skipped-disabled` decision event, submits nothing, reserves no
  budget and writes no scoreboard — but **still adopts and reconciles any unresolved test intent** a
  previously-enabled run left behind (money that already moved is always reconciled).
- `check_test_render_consistency(registry, generation)` — the **config-side** §12 checks (2, 4, 6:
  aspect/resolution feasibility with the pin rule, budget-cap sanity, day-cap headroom), called from
  `stage_theme_load` **beside** `check_contract_consistency` — placed here,
  not in `render_contract.py`, because that file is frozen outside the IV-8 version line; each error
  names both offending sources. **R29: the `per_run_call_cap` arithmetic is NOT re-implemented here**
  — `RENDER_CONTRACT_SPEC.md` §4 check 8 (extended, 0-6) owns the single merged formula
  (`per_run_call_cap ≥ non-QA estimate + llm.qa_reserved_calls + test_render.qa_reserved_calls`);
  this module only feeds it the test-reserve term.
- The whole phase runs inside one **isolation boundary**: any exception → `trace.try_decision`,
  counted into `TestRenderResult` (submitted / succeeded / failed / skipped-budget / skipped-disabled
  + reasons); a test failure can never change canonical asset status, pack content, or exit class
  (T2). govern() failures on a test prompt are `blocked — governance` scoreboard rows, no ledger row.
**Named acceptance tests:** U2, U3, U4, U6 from `MULTI_MODEL_SPEC.md` §13.

**IV-B-3 — scope.** `config_load.py` only: `TestRenderConfig` frozen dataclass + loader for
`generation.media.test_render.*` (§11) — optional keys, safe defaults, `enabled: false` when the
block is absent so a theme predating the spec runs canonical-only.

**IV-B-4 — scope.** `process_summary.py` only: the digest "Model test scoreboard" section — one row
per model with §9.2 metrics, the canonical pipeline's own row for the same slots as the comparison
anchor (Pillow-composited cards are text-perfect by construction), budget-skip/failure notes from
`TestRenderResult`. Runs without test renders (or pre-W8-11 runs) degrade gracefully — no section, no
crash.

**IV-B-5 (conductor) — aggregating writes.**
- `stages.py`: invoke `TestRenderRunner` in `stage_media` strictly after canonical
  submission/resolution, inside the isolation boundary; carry `TestRenderResult` to the digest; call
  `check_test_render_consistency` in `stage_theme_load`.
- `config/model_registry.yaml`: append the two `test`-tier **challenger** routes —
  `img-test-nano-banana-pro` (`model_string: nano-banana-pro`) and `img-test-nano-banana-2`
  (`model_string: nano-banana-2`) — as `MULTI_MODEL_SPEC.md` §3.3 publishes them (docs-verified price
  snapshots; annotate LIVE-VERIFIED on first real `creditsConsumed`), plus the **naming-collision +
  dual-role comment block**: `img-standard-nano-banana-pro` carries `model_string: nano-banana-2` and
  is now `status: reserved`; `img-specialist-nano-banana-pro` carries the real, distinct
  `nano-banana-pro`, also reserved; each of those two model strings appears once more on a `test`-tier
  route, which the amended §12 check 8 permits **only** in that exact shape. State it so nobody
  "fixes" one into another. *(`gpt-image-2-text-to-image` gets **no** test route — it is the
  canonical incumbent and its own rows anchor the scoreboard.)*
- `config/themes/hypedigitaly.yaml`: the `generation.media.test_render` block (§11) shipped
  **`enabled: false`** (§13 item 22.3) with every other value present and coherent so a flip is a
  one-line change: both challenger models, `scope: full_asset`, `max_usd_per_run: 3.00`,
  `resolution: "1K"`, `qa_enabled: true`, `qa_reserved_calls: 40`.
  **This task sets NO caps.** All LLM/media caps moved to II-6 with the flip's recomputed arithmetic
  (§9.3). The merged check 8 term for this block is **zero while disabled**; enabling it requires
  raising `llm.per_run_call_cap` from **80** to ≥ `33 + 42 + 40 = 115` (⇒ 120) in the same edit — the
  check refuses the run rather than degrading mid-flight, which is the intended behaviour and is
  worth stating in the block's own comment. Day cap holds either way: $6.00 ≥ canonical forecast
  $1.26 + test $0.00 (disabled) or + $3.00 (enabled) — §13 item 22.4, unchanged.
- `NAVIGATION.md`: `test_render.py`, the scoreboard artefact, the `models/` output convention, config
  keys.

**Barrier verification (before Wave V):** full pytest green, plus grep guards —
`grep -rn "resolve_test_route" engine/src/` shows exactly two definitions/consumers
(`media_gen`, `test_render`), and `grep -rn "import test_render" engine/src/hypeagent/media_gen.py`
returns nothing (no cycle). Integration A1-A7 (`MULTI_MODEL_SPEC.md` §13) present and passing.

---

### WAVE V — Documentation and confirmation run

**Shape:** a + c. **Triggers:** none — three disjoint document tasks.

| Task | Executor | Depends on | Path set |
|---|---|---|---|
| **V-1** FLOW_MAP rebuild | `documentation-engineer` | IV-B-* | `docs/architecture/FLOW_MAP.md` |
| **V-2** ARCHITECTURE_PLAN amendments | `documentation-engineer` | IV-B-* | `docs/architecture/ARCHITECTURE_PLAN.md` |
| **V-3** Roadmap + decision log | `documentation-engineer` | IV-B-* | `docs/plans/GOAL_ROADMAP.md`, `docs/architecture/DECISION_LOG.md` |
| **V-4** Confirmation run + artifact republish | **main + operator** | V-1…V-3 | run artefacts only |

**V-1 brief.** Standing preamble + `FINDINGS_SYNTHESIS.md` §8. Rebuild `FLOW_MAP.md`: §1 diagram —
remove the fallback edge, add a contract-resolution node, mark N-D as layout-only *and skipped entirely
for programmatic slots*, N-E as unconditional, add the terminal no-image states; §2 — retrace the
audit→fix table to D1-D4; §3 — delete the fallback and QA-skip rows (the row at `:105` documenting
"validation + compose_prompt fallback" is the doc half of D3), update every `max_tokens` figure; §4 —
the new config surface (`render_contract`, `require_visual_evidence`, `persona`,
`format`/`max_generated_slides`, `compositing`, `style_systems`, `format_quota`/`format_quota_reweight`,
`media.test_render`); §5 — contract sha in the artifact map,
`adopted_prior_version/`, manifest deliverability states, the `models/<model_string>/` test subtree +
scoreboard artefact, the decision trail; §6 — invariants **I1-I5 verbatim** with owning tests, plus
T1-T6 by reference to `MULTI_MODEL_SPEC.md` §15; §7 — W8-11 restated as the four structural fixes with
status. **Round-2/3 coverage (required):** the style-system library (**twenty-nine** after the ratified package) and the two-stage selection nodes
(stage-1 quota once per run, stage-2 per asset, both in `stage_copy`), the logo policy
(diffusion-first → `logo_fidelity_ok` gate → manifest-composite repair → single re-QA), and the
test-render phase as a post-canonical, isolation-bounded, never-delivered branch.
**Ratified-package coverage (required, §13 items 19-23):** the §1 diagram's image branch is now a
**ladder**, and must be drawn as one — canonical full-design render → per-glyph text verification →
one retry → `FALLBACK_COMPOSITING` → copy-only, with the kill switch entering at the composited rung;
the stage-1 nodes gain the **carousel gate** (evidence-gated single-vs-carousel) and the
**brand-promo reservation** (an appended, config-authored, LLM-free asset); §4's config surface gains
`language_by_destination`, `carousel_gate`, `brand_promo`, `format_quota_groups` and
`canonical_render_enabled`; §5's artifact map gains `assets/logos/{manifest.yaml,cache/,override/}`;
§6's invariant list gains **RL1, RL2, LG2, LG3, BP1, CZ1, LANG1**; and the model story is stated once,
plainly: **one active render model (`gpt-image-2-text-to-image`), two reserved routes, a disabled test
track.** Preserve the standing note that the artifact is republished at the same URL on every flow
amendment — the republish itself is main's, at V-4.

**V-2 brief.** Standing preamble + `FINDINGS_SYNTHESIS.md` §8. Amend `ARCHITECTURE_PLAN.md`: §4.2a
(stale "no legible text" rubric → the N-E binary set); §5.3 (image contract axes); **§5.6 (plan-only as
the only terminal rung; name the deleted fallback — PRD Amendment 1)**; §3.2/§4.5 (destination × asset
matrix with slide counts, reconciled against §8.11 caps); §11.3 (fail-closed triggers: gate unavailable,
evidence absent, QA budget unavailable, prompt identity exhausted); §14.3 (image prompts in checked
surfaces, exact-bytes rule); §12.4 (bind slide-level regen to the slot model); **§6.7 — record PRD
Amendment 2, the claim-gate co-location behaviour change, explicitly as a tightening that may block copy
which previously passed.**

**V-3 brief.** Standing preamble. `GOAL_ROADMAP.md`: re-express W8-11 as the four structural changes plus
the de-cruft list, tick what landed, record **W8-12** (the deferred §3a module split, §4; plus the
test-harness follow-ups documented-not-built: promotion path, `image_input` plumbing, auto-promotion —
`MULTI_MODEL_SPEC.md` §10). `DECISION_LOG.md`:
record the §13 decisions 1-6 (slot count, Pillow, fonts, tiktok, module split, governance docs — the
former 0-1/0-4 approval tasks were deleted per R26, the decisions pre-answered) and the 0-2 deletion
notification; both PRD amendments;
**the §13 rounds 2-3 decisions verbatim** (eleven systems incl. the photoreal reversal and the
`li_product_render` rejection, Playfair+Lora vendoring, two-stage selection, anti-ad DON'Ts, the logo
policy reversal, the multi-model harness with its separate wallet); **the §13 items 19-23 ratified
package verbatim** (the rendering flip and the QA-gated ladder, the tool-mark coverage rule and the
three-field manifest, the three-tier unknown-tool ladder and its integrity line, the
native-language gate, EN as the default language with CS a switch, the accent-hex and screens-off
guardrails, the four wilder classes, `brand_promo`, the operator's ten-pick DNA as normative style
direction, conditional carousels, single-model production with the test track built-and-disabled,
the confirmed $6.00/day cap, and the optional operator-override asset folder) **each with its
SIM_REPORT finding cited**, so a future reader can see the pixels the decision rests on; and
**the exact operator-facing message the resume guard emits on a contract-version mismatch**, so an
operator meeting a refused `--resume` finds it documented rather than surprising.

**V-4 — conductor only, cannot be delegated.** Run the confirmation run, analyse against §10's gate, and
**republish the FLOW_MAP artifact at the same URL** (standing PRD rule — *agents cannot publish
artifacts; only the main thread can*). Report before/after against fa51 and decide whether to keep the
rollout flags on.

---

## 7. Aggregating files — single writer, written LAST

Never handed to a child in a fan-out (`CODING_GUIDELINES.md` §21 obligation 3).

| File | ONE owner | Written after | Why it aggregates |
|---|---|---|---|
| `engine/src/hypeagent/stages.py` | **main** — I-3, II-6, III-6, IV-8, IV-B-5 | all executor tasks in that wave | the run's registration/wiring point |
| `config/themes/hypedigitaly.yaml` | **main** — I-3, II-6, IV-8, IV-B-5 | that wave's executors | active config registration; four nodes read it |
| `config/style_guide.yaml` | **main** — II-6, IV-8 | that wave's executors | read by N-A, N-C, N-D, N-E; content authored in `STYLE_SYSTEMS_SPEC.md` §3, applied here |
| `config/model_registry.yaml` | **main** — IV-8, IV-B-5 | that wave's executors | route + policy registration; IV-B-5 appends the two `test`-tier routes + naming-collision comment |
| `assets/logos/manifest.yaml` | **IV-12** — main or web-capable leaf (websearch required) | — (authored once, consumed lazily by `brand_assets.py`) | single tracked brand artifact; binaries never committed. `assets/logos/cache/` and the optional `assets/logos/override/` are **gitignored, never written by a task** — the cache is runtime, the override is the operator's |
| `reference/OPERATOR_FAVORITES_DNA.md` | **main** — read-only for every executor | — (authored 2026-08-08, pre-dates Wave 0) | normative style direction (D1-D6); executors cite it, none edits it |
| `engine/pyproject.toml` | **main** — IV-8 | IV-3 | dependency registration (Pillow approved, §13.2) |
| the four companion specs (`RENDER_CONTRACT_SPEC.md`, `COMPOSITING_SPEC.md`, `STYLE_SYSTEMS_SPEC.md`, `MULTI_MODEL_SPEC.md`) | **0-6** — sole spec writer this overhaul | — (before I-0) | Risk-3: the plan never silently diverges from the specs it cites; all spec corrections flow through one task |
| `assets/fonts/**` | **main** — IV-8 | IV-3 | licensed binary assets + licence files |
| `NAVIGATION.md` | **main** — appended by each wave's conductor task | that wave's executors | seeded by 0-5 |
| `render_contract.py` `CONTRACT_VERSION` line | **main** — IV-8 only | IV-1…IV-7 | the single version bump; the rest of the file is I-0's |
| `docs/architecture/FLOW_MAP.md` | **main** dispatches V-1 as its sole writer; artifact republished by main at V-4 | all code waves | single source of truth for the flow |
| `docs/plans/w8-11-overhaul/PLAN.md` | **main** | — | this file |

`media_gen.py`, `copy_gen.py`, `promptcraft.py` — and after the amendment `config_load.py`,
`resume_state.py`, `store.py`, `process_summary.py` — are **hotspots, not aggregators**: each is written
by exactly one task per wave, a different task in a later wave (e.g. `config_load.py`: I-0 → IV-10 →
IV-B-3; `media_gen.py` in Wave IV-B is IV-B-1's alone, with `test_render.py` sequenced behind it on the
import dependency). No wave ever fans two siblings into one file.

---

## 8. Wire-in — every new symbol, and who applies it

Live-Path Discipline: a symbol not in this table is dead code. **The conductor applies every row marked
"main"; executors report, they do not reach into a sibling's file.**

| New symbol | Imported / called / registered where | Applied by |
|---|---|---|
| `fsutil.atomic_write_text/bytes` | `resume_state.py:246` (III-5) · `promptcraft.py:258-263` (II-3) · `virlo.py:904-914` (IV-2) · `stages.py:548-550` (main, II-6) · every compositing PNG write (IV-3) | each file's owner |
| `fsutil.sha256_hex` | `media_gen.prompt_sha256` alias (I-1) · `render_contract` sha (I-0) · compositing checksums (IV-3) | I-0, I-1, IV-3 |
| `trace.try_decision()` | every degrade emitted inside an `except` block: `virlo.py:501-502,551-552` (IV-2), compositing §7 failures (IV-3/IV-7) | IV-2, IV-3, IV-7 |
| `asset_model.Slot`/`OnImageText`/`VisualIntent`/`CopyAsset` | produced in `copy_gen._parse_openrouter_response` + `AssetCopyStatus`; consumed by `promptcraft.craft_prompts`, `media_gen.plan_media_assets`, `packaging`, `process_summary` | III-1 (produce), III-2/III-3/III-4 (consume) |
| `asset_model.SlotState`/`advance()`/`TERMINAL` | driven in `MediaGenerator._process_gated_plan` / `_status_from_row`; every transition emits a decision event | III-3 |
| `asset_model.asset_deliverability()` | `packaging.package_candidates` + `write_digest` | III-4 |
| `CraftedImagePrompt`/`CraftedPromptSet` (frozen shapes) | authored in I-0; adopted by `promptcraft` (II-3/III-2), read by `media_gen` (III-3) and `process_summary` (III-4) | I-0 → II-3, III-2, III-3, III-4 |
| `render_contract.RenderContract` | resolved in `stages.stage_copy`, stashed on `ctx.extra["render_contracts"]`, re-read in `stage_media`; persisted sha in `resume_state` | **main** (II-6), III-5 |
| `render_contract.ConstraintSet` | `copy_gen._build_openrouter_prompt` (twice — top block + pre-`schema_hint` restatement) · `copy_gen.validate_against_contract` · `promptcraft.SYSTEM_PROMPT` · `promptcraft.validate_crafted_prompt` *(the critic-rubric consumer is deleted — R14)* | II-2, II-3 |
| `render_contract.check_contract_consistency()` | `stages.stage_theme_load`, after the config loaders; raises `ConfigError` → policy-stop | **main** (I-3) |
| `render_contract.GovernedPrompt` / `govern()` | `MediaGenerator._submit_new` — the sole `create_task` call site accepts nothing else | I-1 |
| `render_contract.deterministic_prompt_leak_check` (moved) | called inside `govern()`; `media_gen` imports it back | I-0, I-1 |
| `render_contract.QUOTED_SPAN_RE` | `govern()` closure check (I-0); `promptcraft` adopts and deletes its copy (II-3); `media_gen` twin deleted (I-1) | I-0, I-1, II-3 |
| `render_contract.CONTRACT_VERSION` | `media_gen.PROMPT_PATTERN_VERSION` alias · `media_prompts.yaml` header · `resume_state` guard · consistency check 9 · theme YAML | I-0, I-1, II-3, III-5, **main** (IV-8) |
| `MediaGenerator(claim_snapshot=…, hard_excludes=…)` | `stages.stage_media` passes `ctx.extra["brand_truth_panel"].snapshot` | **main** (I-3) |
| `_settle_intent()` | `media_gen._complete_success` (I-1) and the composite render path (IV-7) | I-1, IV-7 |
| `MediaStageResult.image_count/vision_eligible/vision_qa_successes` | `stages.py:926-946` stage-outcome rollup | I-1 → **main** (I-3) |
| `llm.qa_headroom()` | QA-budget reservation before submission (I-1); consistency check 6 estimate | I-1, I-0 |
| `llm` feedback-retry primitive + `per_slide_tokens` | `promptcraft.craft_prompts` repair round; N-C/N-F budgets | II-1 → II-2, II-3 |
| speaker validator (`copy_gen`) | `process_copy_asset` repair loop **and** `apply_humanness_critic` rewrite-acceptance | II-2 |
| `compositing.render_slot()` / `GroundSpec` / `CompositeResult` | `media_gen` routing by `text_render_mode`/`ground_source`; result feeds `_settle_intent` + provenance | IV-7 |
| `composite-verified` QA verdict | `_settle_intent` → `_write_provenance_yaml`; excluded from the vision-QA rollup denominator | IV-7, **main** (I-3 rollup) |
| `analysis.resolve_visual_evidence()` / `evidence_class` | `stages.stage_analysis` → `VisualPolicy` → `resolve_render_contract`; persisted to `resume_state`; blocks generation when absent; digest banner | **main** (IV-8), III-5 |
| `store.signals_first_seen_since()` | `ranking` freshness window (IV-4); `analysis.resolve_visual_evidence` (IV-5) | IV-4, IV-5 |
| register-keyed leak table | `promptcraft.validate_crafted_prompt` + `govern()` step 4 | II-3, IV-6 |
| `style_systems` config map + per-slot `zones` | `promptcraft._build_style_section` via `VisualPolicy.style_system`; `compositing.layout` loader | IV-6, IV-3 + **main** (IV-8) |
| `GENERATION_MODES["annotated_proof_ui"]` | `pick_generation_mode` rotation; bound to its register/archetype in `style_guide.yaml` | IV-6 + **main** (IV-8) |
| `ui_fidelity_ok` QA boolean | `QA_SYSTEM_PROMPT` + `VisionQaResult` (`STYLE_SYSTEMS_SPEC.md` §5.4) | II-4 |
| `ground_standalone_ok` QA boolean | `QA_SYSTEM_PROMPT` + `VisionQaResult` + overall pass (§5.10; judged only for diffusion grounds) | II-4 |
| `logo_fidelity_ok` QA boolean | `QA_SYSTEM_PROMPT` + `VisionQaResult` + overall pass; never skips when the prompt names a tool logo (§5.11); failure triggers IV-7's repair path | II-4 (boolean), IV-7 (repair wiring) |
| §5.6-§5.10 deterministic constants (`_DEVICE_MOCKUP_RE`, `_TEMPLATE_BACKDROP_RE`; extended `_GRADIENT_MESH_RE`/`_CLIPART_ROW_RE`; `_AD_BANNER_RE` at craft time + QA free text only — span point deleted R4/R6; `_LOGO_INVENT_RE`/`_FONT_NAME_RE` deleted R8/R6) | the ONE shared register-keyed leak function from I-0 (R7), called by `promptcraft.validate_crafted_prompt` + `govern()` step 4 | II-2 (craft-time), II-3 (pattern data) |
| `promptcraft.build_templated_diffusion_prompt()` (R1) | `media_gen` routing submits it for `templated_diffusion` slots via the same choke point | IV-6 (builder), IV-7 (call site) |
| `compositing.request_reserved_zone_prompt_fragment` (exported — N1) | called by promptcraft when assembling `llm_crafted` RENDER briefs; the rect also feeds `check_ground_safe_zone` | IV-3 (export), IV-6 (caller) |
| `resolve_render_route()` (extended — N2) | the single routing decision for the B1 three categories; named in IV-7, never re-implemented inline | IV-7 |
| `generation.destinations_enabled` (N3) | schema in `config_load.py` (I-0); value + contract-resolution read wired at IV-8; a disabled destination is never planned/crafted/spent on | I-0 (schema), **main** (IV-8 value+read) |
| `style_select.assign_format_classes()` / `select_style_system()` | `stages.stage_copy` — stage 1 once per run before the per-asset loop, stage 2 per asset feeding `resolve_render_contract`; stage-1 map + reweight decision persisted to `resume_state` | IV-10 (fns + persistence) → **main** (IV-8 wiring) |
| `generation.format_quota` / `format_quota_reweight` config keys | schema `config_load.py` (absence ⇒ the Phase-8 rotation directly — R18); values theme YAML | IV-10 (schema), **main** (IV-8 values) |
| `ResumeState.format_classes` + reweight record | written in `stage_copy`, read back on `--resume` (never re-derived) | IV-10 |
| `VisualProfile` per-class `format_class` counts/win-rates | produced by the corpus classifier in `analysis.py`; consumed by `style_select`'s Virlo reweight | IV-5 (produce), IV-10 (consume) |
| ~~`logo_assets.resolve_logo_path()`~~ → **`brand_assets.resolve_brand_assets()`** (renamed before it existed, §13 item 19.C) | `media_gen`'s mark-repair path on `logo_fidelity_ok == false` and its Tier-1 artifact path; reads `assets/logos/manifest.yaml` + the optional `override/`, caches to `assets/logos/cache/` | IV-11 (fn), IV-12 (manifest), IV-7 (call site) |
| `GENERATION_MODES["cinematic_scene_hook"]` / `["grid_photo_inset"]` + amended `aspirational_lifestyle_scene` | `pick_generation_mode` rotation; bound via `style_systems[*].generation_mode` in `style_guide.yaml` | IV-6 + **main** (IV-8) |
| compositing rich-text runs / `photo_inset` / `paper_grain` / `reserved_text_zone` flow | consumed via `style_guide.yaml` zone recipes; `grounds.request_reserved_zone_prompt_fragment` + `check_ground_safe_zone` on case-(b) slots | IV-3 + **main** (IV-8 config) |
| `ModelRoute` capability fields + `resolve_test_route()` + test-tier refusal in `resolve_route()` + Phase-0 tier filter + `CREATE_TASK_ALLOWED_KEYS += "resolution"` | `load_model_registry` parsing + registry checks; consumed by `test_render` | IV-B-1 |
| `test_render.build_test_render_prompt()` / `TestRenderRunner` / `TestRenderResult` | invoked from `stages.stage_media` after the canonical loop, inside the isolation boundary | IV-B-2 → **main** (IV-B-5) |
| `test_render.aggregate_scoreboard()` → `test_render_scoreboard.yaml` + digest section | scoreboard from provenance + ledger (never memory); digest section in `process_summary` | IV-B-2 (writer), IV-B-4 (digest) |
| `test_render.check_test_render_consistency()` | `stages.stage_theme_load`, beside `check_contract_consistency` (keeps `render_contract.py` frozen) | IV-B-2 → **main** (IV-B-5) |
| `TestRenderConfig` + `generation.media.test_render.*` keys | loader in `config_load.py` (absent ⇒ `enabled: false`); values theme YAML | IV-B-3 (schema), **main** (IV-B-5 values) |
| `store.find_media_intent(..., model_string=)` + widened UNIQUE | intent lookup/insert per (slot, model); prompt-sha guard applies per (slot, model) after widening. **N4's keyword default becomes the NEW canonical model string `gpt-image-2-text-to-image`** — every pre-harness call site still compiles, and post-flip rows land under the right identity | IV-1 (migration), IV-B-2 (consumer) |

**Ratified-package wire-in (§13 items 19-23) — every new symbol, and who applies it:**

| New symbol | Imported / called / registered where | Applied by |
|---|---|---|
| `SlotState.FALLBACK_COMPOSITING` + its two edges | driven by the ladder in `media_gen`; rendered by `packaging`/`process_summary` as a delivery-class reason | I-0 (state), IV-7 (driver), III-4 (surfacing) |
| `RenderPolicy.canonical_render_enabled` / `text_qa_retry_max` / `fallback_to_composite` | read by the ladder in `media_gen` (IV-7); values in the theme YAML (II-6); the flag row in §11 | I-0 (schema), **main** (II-6 values), IV-7 (reader) |
| `promptcraft.build_full_design_prompt()` | the canonical prompt for every `templated_diffusion` slot and the wrapper for every `llm_crafted` slot; submitted through `govern()` at the one choke point | IV-6 (builder), IV-7 (call site) |
| pinned character constants (robot, anime mood — D5) | interpolated by `GENERATION_MODES["robot_caricature"]`, `["meme_reaction"]`, `["anime_scene"]` — ONE constant, three consumers | IV-6 |
| accent-hex pin check · screens-off precondition · tool-mark coverage check · single-emphasis check | `promptcraft.validate_crafted_prompt` + `govern()` step 4's shared pattern function | II-3 (checks), IV-6 (builder emits the tokens) |
| `VisionQaResult.text_matches` (restored, per-glyph, language-aware) | `QA_SYSTEM_PROMPT` + the overall-pass computation + **the ladder's branch condition** | II-4 (boolean), IV-7 (ladder) |
| `compositing.LayoutRecipe.artifact_zone` + emptiness verification | `render_slot` composites fetched assets into it; `promptcraft` emits the "leave this region empty" instruction; `media_gen` routes Tier-1 slots to it | IV-3 (compositing), IV-6 (prompt), IV-7 (routing) |
| `brand_assets.resolve_brand_assets()` / `BrandAssets` / the tier ladder | `media_gen`'s mark-repair path and Tier-1 artifact path; `promptcraft` reads `description` for prompt injection | IV-11 (fn), IV-12 (manifest), IV-6 + IV-7 (call sites) |
| the shared browser-User-Agent constant | the result-CDN download in `media_gen` (I-1) **and** every fetch in `brand_assets` (IV-11) — one constant, two consumers | I-1 (define), IV-11 (reuse) |
| `style_select.select_asset_format()` (carousel gate) | `stages.stage_copy` before `resolve_render_contract`; decision persisted to `resume_state` and read back on `--resume` | IV-10 (fn), **main** (IV-8 wiring) |
| `style_select` quota **groups** + brand-promo reservation | `assign_format_classes`; group membership + `brand_promo` values in the theme YAML | IV-10 (fn), **main** (IV-8 values) |
| `copy_gen.build_brand_promo_asset()` | `process_copy_asset` routes to it on `format_class: brand_promo`; the asset itself is appended by `stages.stage_copy` | III-1 (fn), **main** (IV-8 wiring) |
| slide-value gate + nativeness block + critic items 15/16 | `copy_gen`'s repair loop and `apply_humanness_critic` acceptance path | II-2 |
| language-keyed claim-gate qualification lexicon | `claim_gate._kvalifikovat_satisfied`, selected by `contract.language` | II-5 |
| `generation.language_by_destination` | schema `config_load.py` (I-0); value + read at contract resolution (**main**, II-6/IV-8); consumed by N-C/N-F/N-E and the gate | I-0, **main**, II-2, II-4, II-5 |
| `generation.carousel_gate` / `brand_promo` / `format_quota_groups` config keys | schema `config_load.py` (IV-10); values theme YAML (**main**, IV-8) | IV-10, **main** |
| `style_systems[*].hard_dont_exemptions` | consulted by the §5 pattern checks; validated by consistency check 11 | II-3 (consumer), **main** (IV-8 values), I-0 (check) |
| `ModelRoute.status` + `resolve_route()`'s reserved refusal | `load_model_registry` parsing + both resolution doors | IV-B-1 |
| `TestRenderRunner`'s dual-role skip rule | before each test submission, against the canonical ledger row for the same (slot, `model_string`) | IV-B-2 |

---

## 9. Cross-cutting requirements

### 9.1 Invariants (`CODING_GUIDELINES.md` §16)

| ID | Statement | Enforced at | Test |
|---|---|---|---|
| **I1** | Every byte submitted comes from a `GovernedPrompt`; one `create_task` call site whose `prompt` argument derives from a `GovernedPrompt` attribute. | type + signature + AST test | `test_render_contract.py::test_governed_prompt_rejects_failed_verdict`; `test_media_gen.py::test_single_create_task_call_site_takes_governed_prompt` |
| **I2** | The claim gate runs on the exact submitted bytes; a missing snapshot fails closed. | `govern()` + required `MediaGenerator` params | `test_media_gen.py::test_missing_snapshot_refuses_construction`; `::test_gate_blocked_number_never_reaches_provider` |
| **I3** | Every `<<…>>` span in a submitted prompt is a member of that slot's gated `on_image_text`. | `govern()` step 1 | `test_render_contract.py::test_text_set_closure_rejects_invented_span` |
| **I4** | A delivered image always carries a QA verdict; skipped ≠ pass; non-text checks never skip. | no RENDERED→DELIVERABLE edge; per-boolean skip | `test_media_gen.py::test_rendered_without_qa_never_deliverable`; `::test_qa_text_booleans_skip_individually` |
| **I5** | No provenance-class change without a `trace.decision` event. | every `advance()` call site | `test_stages.py::test_substitution_emits_decision_event` |
| **C1** | Two config sources may never disagree about the same number; the run refuses. | `check_contract_consistency` | `test_config.py::test_contract_consistency_refuses_contradiction` |
| **C2** | `ConstraintSet.caps` is the only source of any cap read by an author or validator. | grep test | `test_render_contract.py::test_no_module_level_word_cap_constants` |
| **C3** | One version constant; no literal version numbers in guards. | `CONTRACT_VERSION` + check 9 | `test_render_contract.py::test_version_is_single_sourced` |
| **G1** | A STYLE section's own numerals never trip the claim gate. | "N percent" spelling preserved | `test_render_contract.py::test_style_block_numerals_do_not_trip_the_gate` |
| **G2** | A qualification satisfies a number only in the same sentence. | `claim_gate._kvalifikovat_satisfied` | `test_claim_gate.py::test_fa51_35095_with_distant_reported_now_blocks` |
| **L1** | A ledger hit whose stored prompt sha differs blocks; never re-uses the stale image. | `_submit_or_resolve` existing-row branch | `test_media_gen.py::test_ledger_hit_with_changed_prompt_blocks_instead_of_reusing` |
| **S1** | Slot count equals `len(contract.slots)`; never derived from crafter output. | `plan_media_assets` signature | `test_media_gen.py::test_plan_count_matches_contract_not_crafter` |
| **S2** | All-or-nothing at delivery: no partial carousel ships. | `asset_deliverability` | `test_asset_model.py::test_partial_carousel_is_copy_only` |
| **S3** | Every state transition is legal and traced. | `advance()` raises `InvalidTransition` | `test_asset_model.py::test_illegal_transition_raises` |
| **S6** | All delivered slots of one asset share one `contract_sha256`. | `asset_deliverability` → `held_incomplete` | `test_asset_model.py::test_mixed_contract_carousel_is_held_incomplete` |
| **S7** | A prior-version or out-of-plan intent settles its money but never enters the pack. | `_resolve_one_row` quarantine | `test_media_gen.py::test_prior_version_adoption_never_writes_into_pack` |
| **S8** | A paid, rendered image whose QA budget vanished is held, never auto-delivered. | RENDERED `qa_budget_unavailable` → HELD_QA | `test_media_gen.py::test_rendered_without_qa_budget_is_held_not_delivered` |
| **E1** | `evidence-absent` blocks image generation and says so in the digest. | `stages` + `require_visual_evidence` | `test_stages.py::test_absent_evidence_blocks_generation_with_banner` |
| **X1** | Composited PNGs are byte-identical for identical inputs. | compositing determinism rules | `test_compositing.py::test_render_is_byte_deterministic` |
| **X2** | Rendered text equals the input string exactly. | draw-then-compare verification | `test_compositing.py::test_rendered_text_matches_input_exactly` |
| **M1** | Spend reconciles exactly: delta events sum == ledger == balance move. | existing — must not regress | existing `test_media_gen.py` reconciliation tests |
| **M2** | The write-ahead row is inserted before any provider call. | existing — must not regress | existing `test_media_gen.py` write-ahead tests |
| **T1** | Truncation is never silently accepted. | existing — must not regress | existing `test_llm.py` |
| **SEL1** | Selection is deterministic: same `run_date` + config + Virlo corpus + asset list ⇒ identical `asset_id → format_class` map and per-asset `style_system`; `--resume` reads the map back, never re-derives. | `style_select` pure fns + `resume_state` | `test_style_select.py::test_same_run_date_reproduces_identical_assignment` |
| **SEL2** | The Virlo reweight moves at most ONE quota slot per run, and only on signal (`n_c ≥ min_sample`, gap ≥ `win_rate_gap`); the decision (shift or no-shift, with rates and counts) is always logged. | `assign_format_classes` | `test_style_select.py::test_reweight_moves_at_most_one_slot_and_respects_sample_floor` |
| **LG1** | A third-party mark ships only with `logo_fidelity_ok == true` — either first-pass or after exactly one manifest-composite repair + re-QA; a second failure fails the slot closed. No logo binary is ever committed. | II-4 boolean + IV-7 repair path | `test_media_gen.py::test_logo_repair_path_re_qas_exactly_once` |
| **RL1** | The render ladder is ordered: `FALLBACK_COMPOSITING` is reachable only from a `RENDERED` slot carrying **two** failing text verdicts, or from the `canonical_render_enabled: false` kill switch — never from `PLANNED`/`CRAFTED`/`GOVERNED`. | `asset_model.advance()`'s edge set (not an `if`) | `test_asset_model.py::test_composite_fallback_is_unreachable_before_two_text_defects`; `test_media_gen.py::test_text_defect_retries_exactly_once_then_falls_back_to_composite` |
| **RL2** | A canonically-rendered image is never delivered without a per-glyph text verification verdict against that slot's gated spans; skipped ≠ pass, and a dropped diacritic is a fail, not a near-match. | `text_matches` in the never-skipped set + no RENDERED→DELIVERABLE edge | `test_media_gen.py::test_text_matches_never_skips_for_a_canonical_render`; `::test_dropped_diacritic_is_a_text_failure_not_a_near_match` |
| **LG2** | Every tool named in a slot's gated copy has its mark rendered in that slot; a named tool with no mark is a `GovernFailure`, and a mark for a tool the copy never names is too. | `validate_crafted_prompt` + `govern()` | `test_promptcraft.py::test_named_tool_without_mark_fails_governance` |
| **LG3** | A real product's UI is never diffusion-invented. An unresolvable tool degrades Tier 1 → 2 → 3, and Tier 3 output is explicitly illustrative; fictional UI (`website_showcase`) is unaffected. | `brand_assets` tier ladder + IV-7 routing + the §5.4/§5.12 checks | `test_media_gen.py::test_unknown_tool_never_renders_invented_real_ui`; `test_brand_assets.py::test_tier_degrades_from_1_to_2_to_3_on_missing_assets` |
| **BP1** | Only `brand_promo`-class systems may carry §5.6-§5.10 exemptions (and only `concept_dashboard` may carry §5.6); §5.1-§5.5 and §5.11 bind for every system without exception. | consistency check 11 | `test_config.py::test_only_brand_promo_may_carry_anti_ad_exemptions` |
| **CZ1** | Every authored asset's N-C prompt carries the native-language block and the exemplars for **that asset's** language and format class, and the N-F rubric always carries the nativeness, concrete-specifics, visual-logic and instant-read items. | deterministic prompt assembly | `test_copy_gen.py::test_nativeness_block_and_exemplars_match_the_asset_language`; `::test_critic_rubric_carries_visual_logic_and_instant_read_items` |
| **PC1** | No human face is ever depicted, in any class. Cartoon humans are permitted only in illustration/meme classes and only from behind or with the face obscured; no depicted character is ever named. `PersonaPolicy` (who speaks) is unaffected. | template constants + `_PERSONA_DEPICTION_RE` at craft time + N-E `subject_relevant` | `test_promptcraft.py::test_illustration_human_is_from_behind_or_obscured`; `test_media_gen.py::test_visible_face_fails_qa` |
| **LANG1** | An asset's language is resolved server-side from `generation.language_by_destination` — never chosen by a model, never inferred from the copy. | contract resolution | `test_config.py::test_language_resolves_from_destination_config` |
| **CG1** | `carousel` is selected only on Virlo slideshow evidence above the sample floor and gap; `evidence-thin`/`evidence-absent` always yield `single`; the decision is always logged. | `style_select.select_asset_format` | `test_style_select.py::test_carousel_requires_slideshow_evidence_above_the_floor`; `::test_thin_or_absent_evidence_never_selects_carousel` |
| **H1** *(spec T1)* | A `test`-tier route is unreachable from every canonical resolution path, and vice versa; a `status: reserved` route is unreachable from both. | `resolve_route`/`resolve_test_route` + §12 check 3 | `MULTI_MODEL_SPEC.md` §13 U1/U7; `test_media_gen.py::test_resolve_route_refuses_reserved_route` |
| **H2** *(spec T2)* | Test renders never alter any canonical asset status, pack content, or the run's exit class. | isolation boundary in `stage_media` | §13 A4/A7 |
| **H3** *(spec T3)* | Every test-render byte submitted passed the same `govern()` gate as canonical bytes; one choke point. | I1's AST guard extended to the test call path | §13 U3 |
| **H4** *(spec T4)* | One ledger row per (identity, attempt, model); canonical and test rows can never collide; the prompt-sha guard applies per (slot, model). | widened UNIQUE + §8.2 | §13 U5/A2/A6 |
| **H5** *(spec T5)* | Test spend can exhaust only its own wallet; canonical work is never skipped for test-budget reasons; all test spend is visible to the day cap and the circuit breaker. | §5.2 accounting | §13 A3 |
| **H6** *(spec T6)* | A test render without an assessed QA verdict is never counted as a pass. | §9.1 skip semantics | §13 A5 |

*(Naming note: `MULTI_MODEL_SPEC.md` §15 labels the harness invariants T1-T6; this plan already used
**T1** for the truncation invariant, so they are **H1-H6** here — same statements, no divergence.)*

### 9.2 Concurrency, re-entry & idempotency (`CODING_GUIDELINES.md` §6)

The engine is single-process under `run_identity.RunLock`, so the surface is **re-entry** (`--resume`,
same-day re-runs, retried provider calls, crashed runs), not parallel workers. Carousels are generated
**sequentially** (`SLOT_MODEL_SPEC.md` §4) — 18 submit-poll cycles is roughly 5× fa51's wall clock, and
the per-day spend read at `media_gen.py:1318` is only safe because the run lock serialises runs (a
comment there must say so).

| Task | Shared mutable state | Race / re-entry risk | Idempotency strategy | Required test |
|---|---|---|---|---|
| I-1 | `media_intents` ledger, pack images | a resumed run re-submitting a slot already paid for | identity tuple + UNIQUE (`store.py:182`); write-ahead insert before `create_task` | re-run `process()` over the same plans → zero new provider calls |
| I-1 | ledger row vs current prompt bytes | **a re-crafted slot hits the existing row and ships the stale image** — the UNIQUE key does not include the prompt | compare `prompt_sha256`; mismatch → `BLOCKED_NO_IMAGE`, no re-submission, no key widening | `test_ledger_hit_with_changed_prompt_blocks_instead_of_reusing` |
| I-1 | unresolved rows from a crashed prior run | **ungoverned W8-10 images adopted into a W8-11 pack with `qa=skipped`** | phase-0 quarantine → `adopted_prior_version/`, money settled, nothing packed | `test_prior_version_adoption_never_writes_into_pack` |
| I-1 | QA budget counters | double-reservation across attempts; budget dying mid-flight | reserve before submit via `qa_headroom()`; post-render exhaustion → HELD_QA | `test_qa_budget_reserved_before_spend`; `test_rendered_without_qa_budget_is_held_not_delivered` |
| III-5 | `resume_state.yaml` | a W8-10 file loaded by a W8-11 engine; a re-derived `VisualPolicy` drifting the contract sha | `contract_version` guard vs the constant; persisted `visual_policies` read, never re-derived | `test_resume_refuses_stale_contract_version`; `test_resume_reuses_persisted_visual_policy_without_reanalysis` |
| IV-1 | `normalized_signals` rows | re-collect overwriting first-seen | `first_seen_at` excluded from `ON CONFLICT DO UPDATE` | `test_first_seen_at_survives_recollect` |
| IV-2 | `virlo_corpus.yaml`, media manifest | re-materialisation racing a real fetch; a partial write read by `--resume` | derive from already-captured payloads only; `fsutil.atomic_write_text` | `test_idempotent_hit_rebuilds_corpus_without_fetch` |
| IV-3/IV-7 | composited PNGs, composite ledger rows | resume re-writing an existing composite; an interrupted composite row poisoned to `submitted-unknown` | byte-deterministic output + checksum skip; `_resolve_one_row` composite branch re-renders locally | `test_recompose_is_noop_when_checksum_matches`; `test_interrupted_composite_row_is_not_submitted_unknown` |
| all | trace file | a degrade inside an `except` whose trace write also fails | `trace.try_decision` + in-memory degrade list | `test_corpus_write_oserror_does_not_escalate_when_trace_also_fails` |
| IV-10 | stage-1 format-class map | a resumed run re-deriving a different quota assignment (corpus or config drifted) → contract sha drift | map + reweight decision persisted in `resume_state.yaml`, read back, never re-derived | `test_style_select.py` resume test + `test_resume.py` |
| IV-B-2 | test intent rows, test wallet | crash between test-row commit and HTTP ⇒ resubmission; a resumed run doubling the $3 wallet | write-ahead row before `createTask`, resolved by query on restart; budget check counts already-recorded test spend for the run | `MULTI_MODEL_SPEC.md` §13 A6 |
| IV-B-2 | test rows vs changed prompts | a re-crafted test prompt hitting an existing (slot, model) row | prompt-sha guard per (slot, model) — blocks, never resubmits or reuses; scoreboard row `blocked — identity exhausted` | §13 A6 |
| IV-7 | ladder position of a slot across a crash/resume | **a resumed run re-entering the ladder at rung 1 for a slot that already burned both attempts** ⇒ double spend, or at rung 4 for a slot that never rendered ⇒ an unearned composite | ladder position is derived from `SlotState` + the ledger's `attempt` rows, never from an in-memory counter; `advance()` refuses the illegal edge; `ATTEMPT_MAX = 2` still bounds paid submissions | `test_media_gen.py::test_resume_reenters_the_ladder_at_the_recorded_rung` |
| IV-7 | the composited-fallback row | a resumed run re-writing an existing fallback composite | byte-deterministic output + checksum skip (as IV-3/IV-7's existing composite branch); `route_id="composite-local"` resolves locally, never by provider query | `test_recompose_is_noop_when_checksum_matches` |
| IV-11 | `assets/logos/cache/` | two slots in one run resolving the same tool concurrently-ish (sequential engine, but re-entrant across `--resume`); a crash mid-download leaving a truncated PNG | `fsutil.atomic_write_bytes` (temp + `os.replace`) + checksum recorded; a cache hit is content-addressed, so a half-written file can never be adopted | `test_brand_assets.py::test_partial_download_never_becomes_a_cache_hit` |
| IV-11 | vendor sites / result CDN | a 403, a timeout or a redirect loop inside a render | browser UA on every request, timeout on every call, typed result instead of an exception, tier degrade instead of a crash | `test_brand_assets.py::test_fetch_failure_degrades_tier_and_never_raises` |
| IV-10 | the carousel decision | a resumed run re-deriving `single` for an asset whose 5 carousel slots are already paid for | the format decision is persisted with the stage-1 map and **read back, never re-derived** (same rule, same file) | `test_resume.py::test_resume_reuses_persisted_asset_format` |

No queues, DLQs or scheduled-job locking apply — the run lock plus the write-ahead ledger are the
existing single-run guarantees, unchanged.

### 9.3 Cost budget (`CODING_GUIDELINES.md` §7)

| | LLM (OpenRouter) | Media (Kie / **gpt-image-2-text-to-image**) |
|---|---|---|
| Per-request hard cap | `node_overrides[*].max_tokens` (+ `per_slide_tokens`); truncation never accepted | one `create_task` per slot per attempt, `ATTEMPT_MAX = 2`; the ladder adds at most one *ground* render per slot at rung 4 |
| Per-run hard cap | `llm.per_run_usd_cap` $2.00 → **$4.00**, `per_run_call_cap` 60 → **80** (both at II-6 — merged check-8 arithmetic below) | `media.per_run_usd_cap` **$3.00 unchanged**, `per_run_count_cap` **14 → 42**; test wallet `test_render.max_usd_per_run` $3.00 exists but is **inactive** (`enabled: false`, §13 item 22.3) |
| Per-day hard cap | — | `media.per_day_usd_cap` **$6.00, operator-confirmed unchanged** (§13 item 22.4) |
| Reserved | `qa_reserved_calls` **16 → 42** (QA-only floor, derived below); `test_render.qa_reserved_calls` 40 configured but inactive | — |
| Soft warn | `trace.spend` per call; balance-delta divergence | `unexplained_spend_threshold` 0.20 → circuit breaker |
| Kill switch | `generation.llm.enabled: false`; `humanness_critic_enabled: false` | `generation.media.dry_run: true`; **`render_contract.canonical_render_enabled: false`** (drops the whole run to the composited rung — the flip's own reverse gear) |
| Cost-per-request log field | `trace.spend(stage, wallet=…, expected=…, ledger_recorded=…, balance_delta=…)` (`trace.py:287-302`) | same |

**Run shape after the ratified package (the basis of every number below).** 6 organic assets
(3 `linkedin` singles + 3 `instagram_feed`) **+ 1 reserved `brand_promo` + 1 reserved meme** =
**8 assets** (§13 items 20, 25 — both reserved slots are appended, neither consumes a Virlo quota
token). Instagram assets are `single` unless the carousel gate fires (§13 item 22.2), so:
**expected 8 slots** (3 + 3 + 1 + 1) · **worst case 20 slots** (3 + 3×5 + 1 + 1, every organic IG
asset clearing the gate). Caps are sized on the worst case; forecasts quote the expected case.

**Canonical media — every slot is now a paid render** (that is the flip's real cost, and it is
affordable precisely because gpt-image-2 is the cheapest of the three at **$0.03/render, 6 credits,
live-confirmed**):
- **`media.per_run_count_cap`: 42** = 20 slots × `ATTEMPT_MAX 2` (40) + 2 fallback-ground renders.
  Worst-case USD inside that cap = 42 × $0.03 = **$1.26**, comfortably inside the unchanged $3.00
  run cap. Expected: 8 × $0.03 = $0.24 plus roughly one retry at the measured ~5% defect rate ⇒
  **≈ $0.27**.
- **`llm.qa_reserved_calls`: 42** = 20 vision-QA-eligible slots × `ATTEMPT_MAX 2` (40) + ≤2
  mark-repair re-QA. **The B4 denominator changed meaning:** under the flip *every* canonical render
  carries text, so every one is vision-eligible — the old "composited slots consume no vision call"
  relief now applies only at rung 4, which is reached only after two vision calls were already spent.
  Derived, not padded.
- **N-D calls: 5/run** — 1 photoreal asset + 2 illustration-group assets + at most 1 when the
  occasional token lands on `concept_dashboard` + 1 when the reserved meme slot draws
  `meme_reaction` (`deadpan_memo` is a typographic card and needs no crafter); `slide_count` = that
  asset's `llm_crafted` slots only.
- **Non-QA LLM estimate: 33** = 1 N-A + 7 N-C + ~7 N-C repair/feedback + 7 N-F + 5 N-D + 5 N-D
  feedback retries + 1 headroom. *(N-C and N-F are 7, not 8: the meme asset IS authored — its humour
  angle is topical — while `brand_promo` copy is config.)*
- **Merged check 8 (R29, owned by `RENDER_CONTRACT_SPEC.md` §4):**
  `per_run_call_cap ≥ 33 + 42 + 0 = 75` ⇒ **80**. The third term is `test_render.qa_reserved_calls`
  and it is **0 while the track is disabled**; flipping `test_render.enabled: true` makes it 40 and
  the requirement 115 ⇒ 120, which the check enforces at load time — the run refuses rather than
  degrading mid-flight.
- **`llm.per_run_usd_cap`: $4.00** — ~32 authoring calls plus up to 42 canonical vision-QA calls
  (vision calls carry an image and are the expensive ones); fa51 spent $1.32 on far fewer of them.
- **Day cap:** canonical forecast (count cap 42 × $0.03 = $1.26) + test wallet $0.00 = **$1.26 ≤
  $6.00**; with the test track enabled it is $1.26 + $3.00 = $4.26 ≤ $6.00. The confirmed $6.00 cap
  holds in both configurations without change (§13 item 22.4).
- **Test harness, documented but inactive:** 20 slots × 2 challengers = 40 renders at
  20 × ($0.09 + $0.04) = **$2.60** against the separate $3.00 wallet, 40 test-QA calls against the
  40-call reserve (exactly at the floor — raise the reserve before widening `scope`). Wallet and
  reserve values are **unchanged** from the round-3 plan; they simply do not run. Test spend, if ever
  enabled, still never consumes `per_run_count_cap`/`per_run_usd_cap` but does land in the ledger,
  the day spend and the balance reconciliation — real money is never invisible to the breaker.

**Estimated confirmation-run cost:** LLM ≈ **$1.60-2.60**, canonical media ≈ **$0.27** expected
(**≤$0.66** if every organic Instagram asset clears the carousel gate), test track **$0.00**. Every
line inside caps.

**Generation cadence (§13 item 25).** The engine is an **invoked batch**: one invocation produces one
run pack and exits. There is no scheduler inside it and none is added — daily/weekly cadence is
**external** (Windows Task Scheduler or cron) and **config-gated** (`batch_composition` decides what a
batch contains, the caps decide what it may spend), and the **posting** schedule is Postiz's, not
ours. Every number above is therefore *per invocation*; the day cap is the only cross-invocation
guard, and `run_identity.RunLock` is what keeps two invocations from overlapping.

**Risk-2 mitigation — pre-dispatch desk check (main, ~30 min, BEFORE Wave I is dispatched):**
hand-execute every consistency check (the nine of I-0, check 10 from B2, **check 11 from BP1**, the
merged check 8, and `check_test_render_consistency`'s 2/4/6 in the disabled configuration) against
the exact YAML values this plan ships — using the recomputed numbers above
(33 / 42 / 0 / 75≤80 / 42 renders ≤ $1.26 ≤ $3.00 / day $1.26 ≤ $6.00), **and once more with
`test_render.enabled: true`** to confirm the check fires rather than the run degrading. A check that
fails on paper is a plan bug to fix here, not a `ConfigError` to discover at Wave II's barrier.

### 9.4 Errors & logging (`CODING_GUIDELINES.md` §11)

| Condition | Class | Surface |
|---|---|---|
| Config sources disagree | user/config | `ConfigError` → policy-stop, message names both sources |
| Gate blocks the submitted bytes | operational-by-policy | `trace.gate_verdict` + `trace.decision`; `BLOCKED_NO_IMAGE`; verbatim reason in the digest |
| Prompt identity exhausted (sha mismatch) | operational-by-policy | `trace.decision`; `BLOCKED_NO_IMAGE`; asset `copy_only` |
| Prior-version intent adopted | operational-by-policy | `trace.decision`; bytes to `adopted_prior_version/`; money settled |
| Evidence absent | policy | `trace.degrade` + digest banner |
| QA budget unavailable pre-submit / post-render | policy | `trace.decision`; `BLOCKED_NO_IMAGE` / `HELD_QA` |
| Composite overflow / missing glyph / verification mismatch | programmer-or-content | fail-closed (`COMPOSITING_SPEC.md` §7); never a clipped image |
| Degrade raised inside an `except` | operational | `trace.try_decision` + in-memory degrade list; never escalates |
| `UngovernedSubmission` / `InvalidTransition` | **programmer** | raised, not caught; a bug by definition |
| Provider timeout / refusal | operational | existing `_poll_to_resolution` / refusal heuristics, unchanged |

Redaction unchanged: own-authored content appears in full in summaries and provenance; third-party
verbatim text and secrets never do (`RUN_TRACE_SPEC.md` §3/§6).

### 9.5 Migrations & deployment runbook (`CODING_GUIDELINES.md` §9)

| Migration | Additive? | Lock risk | Backfill | Rollback risk |
|---|---|---|---|---|
| `normalized_signals.first_seen_at` + index (IV-1) | yes | none — local SQLite, hundreds of rows | `= retrieval_time`, idempotent, logged | low; a revert leaves an unused column (dropping it is destructive → §10 approval; prefer leaving it) |
| `schema_version` table (IV-1) | yes | none | seed current version | none — `PRAGMA table_info` stays the schema-truth mechanism |
| `media_intents` UNIQUE widened by `model_string` (IV-1, `MULTI_MODEL_SPEC.md` §7.2) | structurally a guarded table rebuild (SQLite cannot alter an inline constraint), semantically additive — column exists since M4, loss-free `INSERT … SELECT`, one transaction, idempotent on re-open via `sqlite_master` detection | none — local SQLite | none — every historical old-tuple group already holds exactly one `model_string` | low — the widened UNIQUE is inert to old code (canonical inserts carry a constant `model_string`, so dedupe behaviour is unchanged); prefer leaving it on revert |
| `CONTRACT_VERSION` 3→4 (IV-8) | not schema; partitions ledger identities | none | none — v3 rows still resolvable via `unresolved_media_intents` | reverting restores 3, correct because the v3 code returns too; a second roll-forward uses **5**, never reuses 3 |
| `media_prompts.yaml` / `resume_state.yaml` version headers | additive, safe defaults | none | none — mismatches are rejected with a message | none |
| `copy_responses/*.yaml` slot shape (III-1) | breaking for `--summarize` of old runs | none | none | mitigated by the "not recorded by this engine version" degrade |

**Deployment runbook — before Wave I ships:** complete or abandon every in-flight W8-10 run. Any intent
abandoned mid-flight settles at the next W8-11 phase 0 into `adopted_prior_version/` — money reconciled,
nothing shipped. Running a W8-11 engine against a live W8-10 run directory is not supported; the resume
guard refuses it explicitly rather than mixing schemes.

### 9.6 Version bump policy

One constant (`render_contract.CONTRACT_VERSION`), aliased by `media_gen.PROMPT_PATTERN_VERSION`,
compared by every guard, asserted against the theme YAML by consistency check 9. **It bumps exactly once,
at Wave IV (task IV-8)** — the last wave that changes prompt bytes. Waves I-III therefore run on **v3
identity semantics**, which is deliberate: bumping at each wave would strand in-flight spend behind three
successive version walls. What protects the interim is not the number but the two guards that do not
depend on it — the prompt-sha comparison (L1) and the phase-0 quarantine (S7), which also fires on
*not-in-plan* and *sha mismatch*, not only on version difference.

**The version-4 identity story is two-part** (reconciling `MULTI_MODEL_SPEC.md` §7): (a) the ledger
identity tuple widens by `model_string` — `(theme, run_date, cluster_key, asset_slot, language,
prompt_pattern_version, attempt, model_string)` — via IV-1's guarded rebuild; (b) `CONTRACT_VERSION`
bumps 3→4 at IV-8. Both land inside the same Wave IV barrier, so no run ever executes between them;
externally they are one identity change. After the widening, guard 4 (L1) applies **per (slot,
model)** — a re-crafted test prompt against an existing test row blocks that model's render only,
never the canonical row or the other model's. `model_string` is the **only** approved widening, ever;
Wave IV-B adds rows under the widened tuple but changes no identity semantics. A second roll-forward
after any revert still uses **5**, never reuses 3.

---

## 10. Verification plan

**Commands (verified in this repo).** No CI, no Makefile, no ruff/black config, no `conftest.py`.
`mypy 1.20.2` is installed but entirely unconfigured — running it produces noise, so **pytest is the only
gate**:

```
cd C:/Users/Pavli/Desktop/HypeDigitaly/GIT/HypeAgentSocials/engine && python -m pytest -q
```
Baseline **515 passed in ~30s** (verified 2026-08-07). Per-file during development:
`python -m pytest tests/test_media_gen.py -q`. **Executors run the full suite before reporting**, not
just their own file.

**Test idiom** (no `conftest.py` — do not add one): module-level factory helpers (`_config(**overrides)`,
`_client(tmp_path, fetcher)`), `tmp_path` for filesystem isolation, and the existing injectable
transports — `collectors.base.FixtureFetcher` (`base.py:129-157`) and `test_media_gen.QueuedFetcher`
(`:37-59`), which already fakes the Kie image API and the OpenRouter vision-QA call simultaneously.
Everything runs offline.

### Unit (per wave barrier)

| File | New tests |
|---|---|
| `test_render_contract.py` (NEW) | all 9 consistency checks; `sha256` stability; `ConstraintSet` projection; `GovernedPrompt` rejection (`UngovernedSubmission`); text-set closure; `VisualIntent` not submittable; no module-level cap constants; version single-sourced; STYLE numerals do not trip the gate |
| `test_asset_model.py` (NEW) | every legal transition; `InvalidTransition` on each illegal one; `is_cover` role-derived; `asset_deliverability` for deliverable / copy_only / held / held_incomplete / in_progress; mixed-contract carousel |
| `test_compositing.py` (NEW) | text fidelity; overflow fail-closed; byte-determinism; missing-glyph detection; safe-zone contrast check; zero-spend accounting; re-compose no-op on checksum match; zones loader validation |
| `test_media_gen.py` | single `create_task` call site taking a `GovernedPrompt`; missing snapshot refuses construction; gate-blocked number never submitted; QA never skipped for a delivered image; text booleans skip individually; QA budget reserved before spend; rendered-without-budget held; ledger-hit-with-changed-prompt blocks; prior-version adoption never packs; interrupted composite not submitted-unknown; plan count from contract |
| `test_claim_gate.py` | qualification must be co-located; the fa51 `35,095` regression |
| `test_copy_gen.py` | speaker validator (all three limbs, incl. Czech); critic rubric does not demand a named person; corporate slop pre-filtered; prompt-quote cap at authoring; slots match contract roles |
| `test_promptcraft.py` | single bad slide does not kill the set; feedback retry re-asks with the verbatim reason; programmatic slot makes no LLM call; register never hardcoded editorial; `media_prompts` version mismatch forces re-craft |
| `test_llm.py` | `per_slide_tokens` arithmetic; feedback-retry primitive; `qa_headroom`; truncation still never accepted |
| `test_store.py` | `first_seen_at` survives re-collect; additive migration idempotent; `signals_first_seen_since` window; UNIQUE rebuild idempotent + loss-free (opens old DB, rebuilds once); widened tuple accepts two rows differing only in `model_string`, still refuses a full-tuple duplicate |
| `test_virlo.py` | idempotent hit rebuilds corpus without fetch; partial payloads → thin corpus; OSError traced, not swallowed, and not escalated when the trace write also fails |
| `test_ranking.py` | freshness on first-seen; dead gate gone; fit scores no longer tie |
| `test_analysis.py` | the three `evidence_class` values from durable-store inputs |
| `test_resume.py` | refuses a stale `contract_version`; reuses the persisted `VisualPolicy` |
| `test_stages.py` | substitution emits a decision event; absent evidence blocks with banner; QA-outage rollup marks the stage degraded |
| `test_trace.py` | `try_decision` swallows a write failure and never raises |
| `test_config.py` | contradictory config refuses to load; every `MULTI_MODEL_SPEC.md` §12 check has a fixture raising `ConfigError` naming both sources; absent `format_quota` / `test_render` blocks load with their documented safe defaults |
| `test_style_select.py` (NEW) | determinism + resume read-back; reweight moves ≤1 slot, respects the sample floor, logs shift/no-shift; largest-remainder scaling with class-order ties; destination-compat substitution (linkedin never gets `editorial_grotesque`); step-0 fallback straight to the Phase-8 rotation (R18); **groups expand to distinct members and rotate by `run_date`; a demoted class is promotable by the Virlo reweight; `brand_promo` is appended and never consumes the quota; the carousel gate requires slideshow evidence above the floor and thin/absent evidence never selects carousel; the format decision is always a decision event** |
| `test_brand_assets.py` (NEW, renamed from `test_logo_assets.py`) | second resolve hits cache without fetch; missing manifest entry is a typed error; **every fetch sends the browser UA**; `og:image` + `apple-touch-icon` parsed from site HTML; operator override wins over manifest and fetch; tier degrades 1→2→3; private-IP / off-origin redirect refused; a partial download never becomes a cache hit; a fetch failure degrades the tier and never raises. Fixture fetcher — fully offline |
| `test_test_render.py` (NEW) | `MULTI_MODEL_SPEC.md` §13 U2/U3/U4/U6 — prompt builder embeds every span verbatim + recipe + GUARDRAILS, raises over `prompt_max_chars`; govern() closure/gate on test prompts; 4:5 pins `"1K"` on gpt-image-2 even when config says `"2K"`; nano-banana-pro sends `output_format: "png"`, no `image_input`; Czech diacritics instruction present; scoreboard aggregates from provenance + ledger, never memory |

### Integration (`test_phase3_pipeline.py`, fixture transports, offline)

1. `test_over_cap_slide_blocks_without_fallback` — an over-cap slide produces `BLOCKED_NO_IMAGE` and
   copy-only delivery. **No fallback prompt exists to reach.**
2. `test_gate_blocked_number_never_reaches_provider` — the fa51 `35,095` case: the number never appears
   in any `create_task` body.
3. `test_absent_evidence_blocks_generation_with_banner` — no Virlo evidence ⇒ zero image generation and
   a digest banner stating why.
4. `test_every_delivered_image_has_qa_verdict` — across a mixed hero + 5-slot carousel run, every
   delivered image carries a vision verdict or `composite-verified`.
5. `test_interrupt_mid_carousel_then_resume_delivers_matching_images` — kill the run after slot 3,
   resume, and assert every delivered image corresponds to the copy actually shipped (no stale image, no
   mixed contract sha, no partial carousel).
6. `test_test_renders_are_invisible_to_packaging` (`MULTI_MODEL_SPEC.md` §13 A1+A7) — with
   `test_render.enabled: true`, N canonical images land unchanged plus 2N under
   `models/<model_string>/`; the pack manifest is byte-identical to the same run without them.
7. `test_test_budget_exhaustion_never_touches_canonical` (A3) — a wallet sized to trip mid-phase
   skips the remaining test renders with one decision event; every canonical asset delivers.
8. `test_test_phase_failure_is_isolated` (A4) — an injected provider failure and an injected
   exception in the test phase leave the exit class and every canonical status unchanged;
   `trace` shows `try_decision`.
9. `test_selection_quota_holds_on_six_asset_run` (`STYLE_SYSTEMS_SPEC.md` §8.1) — default quota,
   no reweight ⇒ exactly `serif_editorial 1 / photoreal 1 / artifact_showcase 1 / illustration 2 /
   occasional 1` by format class, with the two illustration slots and the one occasional slot
   resolving to **distinct** group members; the reweight decision event exists either way; the
   appended `brand_promo` asset is the 7th and consumed no quota token.
10. `test_ladder_end_to_end_over_a_mixed_run` (§13 item 19.A) — with fixture QA verdicts scripted to
    fail slot 2 once and slot 3 twice: slot 1 delivers at rung 1 with one paid render; slot 2
    delivers at rung 3 with two; slot 3 delivers as `composite-verified` with two paid renders plus
    (if `llm_crafted`) one text-free ground; a fourth slot with compositing disabled goes
    `copy_only`. Ledger, spend reconciliation and decision trail agree with that story exactly.
11. `test_kill_switch_run_is_byte_comparable_to_the_composited_baseline` — a full run with
    `canonical_render_enabled: false` produces composited images for every slot, spends nothing on
    canonical renders, and exits `success`. This is the flip's reverse gear, and it is tested, not
    assumed.
12. `test_disabled_test_track_submits_nothing_and_reconciles_leftovers` (§13 item 22.3) — with
    `test_render.enabled: false`, zero test submissions and no `models/` subtree, but an unresolved
    test intent left by a previous run is still resolved and spend-reconciled.
13. `test_unknown_tool_tier1_end_to_end` (§13 item 19.C) — a topic naming a tool absent from the
    manifest: the fetcher fixture serves site HTML with `og:image` + `apple-touch-icon`, the render
    carries an empty `artifact_zone`, the real bytes are composited pixel-exact, and the provenance
    records tier 1 and the source URLs. With the fixture serving 403s instead, the same run degrades
    to tier 3 and the delivered image is explicitly illustrative.

### Confirmation-run gate (V-4, operator-judged)

- **8/8 assets** (6 organic + 1 `brand_promo` + 1 meme) either **DELIVERABLE with a QA pass** or
  **cleanly held with a stated reason**.
- **Zero gibberish, zero placeholder labels, zero lorem ipsum** in any delivered image.
- **Zero off-topic** imagery; every image traceable to its slide's own sentence.
- **Every delivered image's rendered text is character-identical to its gated `on_image_text`** — the
  flip's whole premise. Report the ladder's own distribution: how many slots delivered at rung 1, how
  many needed the retry, how many fell back to the composite, how many went copy-only. **A retry rate
  materially above the simulation's ~5% is the signal to reconsider the flip**, and it is now
  measurable rather than felt.
- **Carousels:** if the gate fired, delivered as 5 images, never degraded to a hero; if it did not,
  the decision event says so with its counts. Either outcome passes — **a run of singles is not a
  failure**, it is the gate working.
- 100% QA coverage; spend reconciles exactly (delta sum == ledger == balance move).
- `logs/runs/<run_id>/adopted_prior_version/` is empty **or** every file in it is accounted for in the
  trace and absent from `pack/`.
- Copy passes the slop regex, the speaker validator and the slide-value gate; **reads as native EN**
  (§13 item 22.1); no invented persona, no corporate boilerplate, and every carousel body slide
  carries a concrete number, step or tool name.
- **Every tool named in copy has its mark rendered** (LG2), and no image contains an invented
  "real-looking" screenshot of a real product (LG3).
- **Every image carries its pinned accent hex and its brand furniture** (kicker + wordmark), and the
  recurring robot/anime characters look like the same characters as the simulation's picks.
- Format mix matches the (possibly reweighted) quota incl. group rotation; the reweight decision event
  exists; every asset resolved to a named style system; the `brand_promo` asset carries the verbatim
  CTA pill text; **the reserved meme asset is present, alternates class against the previous run, and
  its joke lands in about a second** (§13 items 24-25).
- Test harness: **`models/` folders absent and `test_render_scoreboard.yaml` absent** — the track is
  disabled (§13 item 22.3) and its cost line is $0.00. *(If the operator flips it on for this run
  instead: folders populated per enabled model, scoreboard agreeing with the digest, nothing under
  `models/` referenced by the pack manifest, test spend ≤ $3.00 and reconciled.)*
- Then: before/after against fa51, keep-or-revert decision on the flags — **including the
  `canonical_render_enabled` decision, which is the flip's own accept/revert gate** — FLOW_MAP §7
  status updated and **the artifact republished at the same URL by the conductor**.

---

## 11. Rollout & rollback (`CODING_GUIDELINES.md` §17)

**This is a single-tenant, operator-run batch engine that never publishes** — there is no ramp, no
allowlist, no live user traffic. "Rollout" means which capabilities are on for the confirmation run.

| Flag | Default | Safe value if unreadable | Owner | Removal date |
|---|---|---|---|---|
| `generation.media.require_visual_evidence` | `true` | `true` (blocking is the safe direction) | operator | permanent — a policy, not a temporary flag |
| `generation.render_contract.compositing.compositing_enabled` | `false` until Wave IV lands, then `true` | `true` (it is the fallback rung — turning it off narrows the ladder to copy-only) | operator | **permanent** — no longer a temporary flag: after the flip this is the fallback renderer, and removing it would delete the only rung between a text defect and copy-only |
| `generation.render_contract.canonical_render_enabled` | `true` (the flip) | **`false`** — the composited path is the known-good pre-flip behaviour, so unreadable config lands on the conservative rung | operator | **permanent** — this is the flip's reverse gear, not a migration flag. Removing it would make the flip irreversible |
| `generation.brand_promo.enabled` | `true`, `slots_per_run: 1` | `false` (no promo asset — a missing service post is invisible; a wrong one is not) | operator | permanent — a content dial |
| `generation.media.test_render.enabled` *(restated, §13 item 22.3)* | **`false`** — single-model production | `false` | operator | a dial; retired only at a future promotion decision |
| `generation.media.dry_run` | `false` | `true` (zero **media** spend; LLM still spends) | operator | permanent kill switch |
| `generation.llm.enabled` | `true` | `false` | operator | existing |
| `generation.llm.humanness_critic_enabled` | `true` | `true` | operator | existing |
| ~~`generation.media.test_render.enabled` `true` (operator directive 2026-08-07)~~ | **superseded 2026-08-08 → `false`** (§13 item 22.3; the row above carries the current state) | `false` (canonical-only; unresolved test intents still reconcile) | operator | a dial, not a temp flag |

The claim-gate co-location change (PRD Amendment 2) deliberately has **no flag** — a flag would keep the
weak path reachable; rollback is a one-file `git revert`.

**Kill switch.** `generation.media.dry_run: true` takes effect on the next run (seconds — there is no
long-running process), produces the full plan and forecast, and spends no media money. Add
`generation.llm.enabled: false` for a genuinely zero-cost rehearsal.

**Rollback steps, in order.**
1. **Code revert** — `git revert` the wave's commit(s) and re-run. Waves are committed separately so one
   can be backed out; Wave I is the only one that cannot be reverted alone without restoring the
   ungoverned path, and reverting it means accepting fa51-class defects.
2. **Data rollback** — nothing to undo. `first_seen_at` and `schema_version` are additive and inert to
   old code; leave them (dropping a column is destructive, §10 approval). Ledger rows from the reverted
   run stay valid and reconciled.
3. **Version identity** — a revert restores `CONTRACT_VERSION = 3`, correct because the v3 code returns
   with it. A second roll-forward uses **5**, never reuses 3.
4. **Flag removal** — drop `compositing_enabled` once the confirmation run is green; flags past their
   removal date are dead code.

**Health gates that abort the rollout.** Any of these triggers immediate revert-and-analyse: spend
reconciliation mismatch · the circuit breaker tripping · any delivered image without a QA verdict · any
`create_task` body containing a gate-blocked string · **any file in `adopted_prior_version/` that also
appears in `pack/`** · exit class worse than `success` · `InvalidTransition` or `UngovernedSubmission`
raised anywhere (programmer errors by definition) · **a text-defect retry rate materially above the
simulation's ~5%, or any slot reaching rung 4 more than once per run** (either means the flip's
premise is weaker in production than in the simulation — flip `canonical_render_enabled: false` and
analyse before spending another run) · **any delivered image containing a mark for a tool the copy
does not name, or a real-product screenshot that did not come from fetched bytes** (LG2/LG3 are
integrity gates, not quality ones).

---

## 12. Definition of Done (`CODING_GUIDELINES.md` §19) — every task ticks this

- [ ] Governing spec section read (`ARCHITECTURE_PLAN.md` / this plan / the companion spec) and
      conformance verified.
- [ ] Implementation matches intended behaviour; no user-facing behaviour changed beyond what the locked
      decisions and the two PRD amendments require.
- [ ] New code wired into the active run path (§8) — nothing added that nothing calls.
- [ ] Existing reusable code searched first (§3); no duplicate or parallel system.
- [ ] Tests added/updated in the repo idiom; **full** `cd engine && python -m pytest -q` green.
- [ ] Regression invariants M1, M2, T1 still hold.
- [ ] Error handling classified (§9.4); no secret or third-party verbatim text in a log.
- [ ] Re-entry safe: `--resume`, same-day re-run and a crashed prior run produce no duplicate spend and
      no unreviewed image in the pack.
- [ ] Cost impact considered against the caps in §9.3.
- [ ] Deletions pre-cleared by task 0-2; newly discovered dead code reported, not deleted.
- [ ] **Ratified package respected (§13 items 19-23):** the ladder's order is enforced by the state
      graph, not by an `if`; every prompt this task emits carries its pinned accent hex, its ground
      and type-voice tokens, its single emphasis token, its brand furniture, and (for scenes) the
      screens-off sentence; every named tool has a mark; no real product's UI is invented.
- [ ] **`reference/OPERATOR_FAVORITES_DNA.md` D1-D6 conformance** checked for any task that authors a
      template prompt, a style-system recipe, or a selection weight.
- [ ] `NAVIGATION.md` updated if paths, commands, env vars or config surfaces changed.
- [ ] Canonical report produced (`CODING_GUIDELINES.md` §20).

---

## 13. Open questions — RESOLVED (operator decisions, 2026-08-07)

All six questions were answered by the operator. These are binding inputs to Wave 0/II/IV config:

1. **Instagram slot count: 5 slots.** Amend `style_guide.yaml:89` to `slides: [5, 7]`; lower
   `copy_gen.py:295` `MIN_CAROUSEL_SLIDES` accordingly (superseded by `RenderContract.format` anyway).
2. **Pillow: APPROVED** as a production dependency (ADR-0002 records it). Unblocks Wave IV compositing.
3. **Montserrat: APPROVED — vendor it.** Add Montserrat (SIL OFL, licence file alongside, following the
   NotoSans precedent) to `assets/fonts/` in the IV-8 fonts path.
4. **`tiktok` destination: KEEP but DISABLE.** Operator intent: video generation must eventually work
   properly, so do NOT rip tiktok out of the config surface. Concretely: (a) add
   `aspect_ratio_by_destination["tiktok"] = "9:16"` so consistency check 4 passes; (b) keep the
   `CANVAS_SIZE_BY_ASPECT["9:16"]` entry in COMPOSITING_SPEC (its cut is reversed — it is now
   future-justified); (c) add an explicit `generation.destinations_enabled: [linkedin, instagram_feed]`
   (or equivalent per-destination `enabled: false` flag) read at contract resolution, so no tiktok
   asset is ever planned, crafted, or spent on until the flag flips; (d) `check_contract_consistency`
   validates DISABLED destinations too (config must stay coherent even while off). Proper tiktok/video
   generation is future work (W8-12+), out of scope here.
5. **Module split: DEFERRED to W8-12** as planned (§4 stands).
6. **Repo governance docs: APPROVED.** Task 0-5 authors `NAVIGATION.md` AND a minimal repo-accurate
   `CLAUDE.md` (per the `CODING_GUIDELINES.md` end-of-file template: what the engine is, stack =
   stdlib+pyyaml+Pillow/SQLite/sync, non-negotiable invariants I1-I5, subagent notes).

### Rounds 2-3 (operator decisions, 2026-08-07, second session — binding, do not relitigate)

Sources: `STYLE_SYSTEMS_SPEC.md` round-2 amendment (its preamble records the seven locked decisions),
`MULTI_MODEL_SPEC.md`, and the reference analyses `reference/aisimplified23/DESIGN_DECONSTRUCTION.md`
+ `reference/visual-formats/DESIGN_EXPANSION.md`; API ground truth `reference/kie-models/*.md`.

7. **Style library 6 → 11 systems** — the round-1 photoreal ban is REVERSED (three photoreal systems
   on `register: photographic_ugc`: `ig_lifestyle_stack`, `ig_scene_hook`, `li_scene_hero`), plus
   `ig_value_sheet` and `ig_operator_grid`; **`li_product_render` REJECTED**, recorded not specced
   (§2.14). Census: 3 fully programmatic of 11; diffusion-TEXT surface unchanged at the two round-1
   covers (§2.7).
8. **Serif vendoring: Playfair Display (incl. italic cuts) + Lora, both SIL OFL 1.1** — editorial
   body text switches sans → serif; Czech-glyph verification on the ACQUIRED files is a ship gate,
   and `ig_value_sheet`'s `type_floor: 0.0185` gets its own legibility pass on the vendored Lora
   (§3.5). Montserrat remains the intended sans.
9. **Two-stage Virlo-driven format selection** (§4 rewrite): per-run `format_quota` 2/2/1/1 →
   Virlo reweight (≤1 slot moves, `min_sample: 12`, `win_rate_gap: 0.25`, `virality_strong: 18`) →
   largest-remainder scaling → `sha256(run_date)`-seeded rotation → destination-compat substitution;
   stage 2 = topic-regex inside the class with within-class rotation. Deterministic, no LLM; absent
   `format_quota` ⇒ degrade *(as recorded; superseded by R18, item 14 — the degrade is the Phase-8
   rotation directly)*.
10. **Five anti-ad Hard DON'Ts** (§5.6-§5.10): radial-glow/premium-gradient grounds, benefit-pill /
    checkmark-row grammar, device-mockup/product-render insets, urgency/price/CTA-banner language in
    pixels (three wiring points incl. craft time), and the stand-alone-content test
    (`ground_standalone_ok`).
11. **Logo policy REVERSED to diffusion-first** (§2 logo block + §5.11): models render third-party
    marks in-image; N-E gains `logo_fidelity_ok` (never skips when a tool logo is named); on failure,
    composite the REAL mark from the lazily-fetched `assets/logos/manifest.yaml` (authored via
    websearch during plan execution) and re-QA once; second failure fails closed. No logo library, no
    committed binaries. HypeDigitaly's own marks stay composited from `assets/brand`.
12. **Multi-model test harness** (`MULTI_MODEL_SPEC.md`, operator directive): every creative is ALSO
    rendered on `gpt-image-2-text-to-image` + `nano-banana-pro` with FULL slide text in-image;
    per-model folders under `models/<model_string>/`; ledger identity widens by `model_string`
    (guarded UNIQUE rebuild); N-E QA with Czech-diacritics-sensitive comparison; per-model scoreboard
    in the digest; **$3.00/run separate test wallet**; test renders are evidence, never product —
    test-only tier, never delivered, failures never fail the run. Promotion is a future
    operator-gated registry edit (W8-12+), never automatic.

### Review round (2026-08-07, architecture panel — folded in; supersedes items 7/9 where noted)

13. **Blockers B1-B5: resolved via Wave 0 task 0-6** (three-category slot routing; style-system-only
    per-slot routing + consistency check 10; `RenderPolicy.composited_roles` deleted; check-6
    denominator = vision-QA-eligible slots only, recomputed; `logos_ok` folded into
    `logo_fidelity_ok`), with matching plan-brief updates applied in place (I-0, II-2/II-3/II-4,
    IV-6/IV-7/IV-8, IV-B).
14. **Redundancy deletions adopted:** R1 (N-D iff `format_class == photoreal`; every other diffusion
    surface is deterministic `templated_diffusion`; non-QA LLM estimate 31→23), R2 (`ig_stat_slab`
    cover composited — fourth fully-programmatic system; supersedes item 7's census), R4/R6
    (`_AD_BANNER_RE` span point + `_FONT_NAME_RE` deleted), R5 (banned-strings scan moves to
    authoring), R7 (leak table = one shared function), R8 (`_LOGO_INVENT_RE` deleted with R1),
    R12 (one logo boolean), R13/R14 (critic item 14 deleted; item 13 narrowed — the regex owns
    name-matching), R16 (`series_consistent` judged over diffusion-touched slots only), R18 (step-0
    degrade = Phase-8 rotation directly; supersedes item 9's "round-1 selection" wording), R22
    (build + govern the test prompt once, submit the one `GovernedPrompt` to both routes), R26
    (Wave 0 tasks 0-1/0-4 deleted — decisions were already made; residue in 0-2), R29 (ONE merged
    call-cap check, owned by `RENDER_CONTRACT_SPEC.md` §4 check 8).
15. **R3 — RECOMMENDED DEFAULT, veto-able by operator:** `ig_annotated_proof`'s cover hook is also
    composited, over its programmatic paper ground ⇒ **canonical diffusion-TEXT surface = ZERO**
    (fifth fully-programmatic system); model-rendered text survives only in the test harness;
    `diffusion_text_max_spans`/`diffusion_text_max_words_per_span` become dead fields (0-6 marks
    them pending-deletion); canonical N-E drops `text_matches` — draw-then-compare owns text
    fidelity. A veto restores that one cover to diffusion text ≤2 spans × ≤6 words and keeps the
    fields and the check.
16. **R19 — Virlo reweight KEPT**, explicitly, against the redundancy finding: it is the ONLY
    mechanical link from Virlo evidence to style selection; cutting it would demote the trend corpus
    back to decoration — exactly fa51's D4.
17. **R23 — `scope: full_asset` stays the default** (operator's explicit directive). Recorded knob:
    `scope: cover_only` ⇒ 12 test images/run at $0.72, saving **$1.44/run**, but the §10 promotion
    evidence bar (≥3 runs AND ≥50 test renders) is reached in 3 runs at `full_asset` (108 renders)
    vs ~5 runs at `cover_only` (60). Config flip only; no code change.

18. **Pre-implementation simulation (2026-08-07, operator-requested) — approach CONFIRMED, two
    amendments folded in.** 17 live kie.ai renders (5 nano-banana-2 grounds + 6 gpt-image-2 + 6
    nano-banana-pro full-text) + Pillow composites of 5 planned systems; outputs + full findings at
    `docs/plans/w8-11-overhaul/simulation/` (`SIM_REPORT.md`). Pricing confirmed exactly (8/6/18
    credits ⇒ $0.04/$0.03/$0.09). Composited Czech text: flawless everywhere. Test models rendered
    dense Czech ~99% correctly BUT nano-banana-pro hallucinated `AGENȚURA` (Romanian comma-below Ț)
    in display type — validates R3 (zero canonical diffusion text) and the test-track QA gate. Logo
    probe: every model failed ≥1 of 5 marks; ALL THREE missed Claude's; only gpt-image-2 drew
    Zapier's current asterisk — IV-12's manifest fallback is load-bearing, not theoretical.
    Amendments (absorbed into existing tasks, no new tasks):
    a. **Task 0-6 (spec reconciliation) additionally applies**: every photoreal template/N-D prompt
       fragment gains the sentence "Any screen or monitor in frame is OFF or angled away — never
       render UI content." (both canonical scene modes put faint code/invented dashboards on
       monitors in the sim; N-E's `no_ui_invented` check stays the backstop).
    b. **Task IV-12 (logo manifest)**: seed the manifest with Claude/Anthropic, ChatGPT/OpenAI,
       Zapier, Gemini, Notion, Make, n8n as the minimum set BEFORE the confirmation run; treat
       model-drawn Claude and Zapier marks as expected-fail in `logo_fidelity_ok`.
       *(Superseded and extended by item 19.B: the manifest schema gains `description`/`icon_url`/
       `source`, and the seed set grows to eleven tools.)*

### Ratified package (operator decisions, 2026-08-07/08 — binding, do not relitigate)

*Evidence base: `simulation/SIM_REPORT.md` — 44 live kie.ai renders over 6 rounds, findings F1-F20,
plus the operator's ten hand-picked favourites deconstructed in
`reference/OPERATOR_FAVORITES_DNA.md`. Cost of the entire simulation: ≈ $1.90.*

19. **The six-item ratified package** (operator-ratified after reviewing the pixels).
    **A. RENDERING FLIP** *(F9, F12, F18)* — canonical creative rendering becomes
    **`gpt-image-2-text-to-image` FULL-DESIGN renders**: styled expressive typography rendered
    in-image. Model string exact; **IG 4:5 MUST pin `resolution: "1K"`** (2K/4K unsupported for that
    aspect — hard API constraint, applied mechanically from `resolution_constraints`). **Pillow
    compositing is DEMOTED to fallback.** Every canonical render passes **vision-QA per-glyph text
    verification** against the gated `on_image_text` strings → on defect **one retry** → on a second
    defect **fall back to the old composited path** (the round-1 canonical becomes the fallback) →
    else **copy-only**. Fail-closed preserved. Evidence: gpt-image-2's ~5% Czech display-type defect
    rate (F18: "ktery" lost its ý-accent) is what makes the QA gate **mandatory, not optional**.
    `MULTI_MODEL_SPEC.md` roles invert: gpt-image-2 = canonical incumbent; nano-banana-pro +
    nano-banana-2 = test-track challengers on the existing scoreboard; **test wallet and caps
    unchanged**. §9.3 recomputed end-to-end.
    **B. LOGOS WITH EVERY TOOL MENTION** *(F8, F13)* — **hard rule:** any slot whose copy names a
    platform or tool **must render its mark** (icon row, inline chip, or diagram node).
    `assets/logos/manifest.yaml`'s schema becomes per-tool
    `{description: "<precise verbal mark description for prompt injection>", icon_url: <direct PNG,
    ICON FORM not wordmark>, source}`. Verbal descriptions are injected into gpt-image-2 prompts
    (F8: ~95% fidelity); reference PNGs feed `logo_fidelity_ok` QA comparison and the Pillow
    composite fallback. **Seed set before the confirmation run:** Claude/Anthropic, ChatGPT/OpenAI,
    Zapier, Gemini, Notion, Make, n8n, Calendly, Gmail, Loom, Airtable.
    **C. UNKNOWN-TOOL THREE-TIER LADDER** *(F13-F15, round 3)* — a new runtime asset-fetch capability
    (the `logo_assets.py` task generalises into **`brand_assets.py`**): fetch the tool's own site HTML
    → `og:image` (real vendor product visual) + `apple-touch-icon`/favicon (real logo). **ALL HTTP
    fetches MUST send a browser User-Agent** — a bare UA gets 403 from vendor sites *and* from the kie
    result CDN. **Tier 1** (default): name + real logo + real product visual. **Tier 2:** fetched logo
    only + styled typography card. **Tier 3** (fail-closed): clearly **ILLUSTRATIVE** stylized UI +
    name chip. **NEVER a diffusion-invented "real-looking" screenshot of a real product** — this
    integrity line is codified explicitly and carried as invariant LG3.
    **D. NATIVE-LANGUAGE GATE** — the N-C copywriter prompt is rewritten for natural spoken register
    ("would a native speaker say this out loud?"), with a translationese/calque ban and few-shot
    exemplars taken verbatim from the ratified simulation copy ("Poptávka přišla ve dvě ráno. Odpověď
    odešla ve 2:01." / "Firma bez webu? Do večera to jde." / "Scénáře naklikáte, kód neřešíte.").
    N-F gains an explicit nativeness rubric line. *(Generalised from Czech-only to
    language-parameterized by item 22.1.)*
    **E. BILINGUAL CS/EN** *(F12)* — language becomes **per-destination config**; the ledger identity
    already carries `language`. EN renders proved uniformly ≥ CS quality. *(Default set to EN by item
    22.1.)*
    **F. GUARDRAILS** *(F10, F11)* — every template prompt **pins its accent hex** (`#302B87` indigo /
    `#00A39A` teal / `#E8A63B` amber per system; unpinned prompts drift to coral, which is Anthropic's
    trademark colour), and every photoreal template carries **"Any screen or monitor in frame is OFF
    or angled away — never render UI content"** (supersedes item 18a's narrower wording task).

20. **New style classes** (round 4-5, operator-requested "wilder" visuals — all validated live).
    - **`website_showcase`** — a complete, polished, **FICTIONAL** client website in a browser frame
      (invented business, e.g. a bakery); body text greeked/blurred; at most 3 short legible strings.
      Reads as "look what AI can build".
    - **`robot_caricature`** — premium editorial-cartoon robot (ink outlines, single-lens eye, no
      human face), brand indigo/teal.
    - **`concept_dashboard`** — isometric fictional "mission control" diorama, all panel text greeked;
      **the operator relaxes the anti-ad glow ban FOR THIS CLASS ONLY**.
    - **`anime_scene`** — hand-drawn anime/painterly scenes; any human character **strictly from
      behind, face never visible**; no named personas (institutional voice unchanged).
    These join the Virlo-driven format rotation as **organic, reweightable classes** — §4's stage-1
    quota/selection is updated for them. **Integrity rule codified: fictional UI = allowed
    illustration; real-product UI = Tier-1 real assets only.**
    **`brand_promo`** (round 5, operator directive) — a new format class, **deliberately promotional,
    EXEMPT from the anti-ad Hard DON'Ts** (which remain binding for every organic class). Default
    **1 slot per batch/run** (operator dial), **brand-guideline-driven, NOT Virlo-driven** — it does
    not consume the Virlo quota. Strict brand palette (indigo `#302B87` / dark `#1E1B2E` / cream
    `#F6F1E7` grounds, teal CTA). **Verbatim CTA pill text: "Klikněte na odkaz v popisku"** (the EN
    equivalent when the asset language is `en`). Service-message rotation list in config, seeded with
    "AI audit zdarma." / "Jak zařadit AI do firmy?" / "Chcete nasadit AI agenta?" (extensible).

21. **Operator's ten favourites are normative style direction** (2026-08-08). The operator hand-picked
    10 of the 44 renders as ground truth for "double down on these styles"; the deconstruction lives
    at **`reference/OPERATOR_FAVORITES_DNA.md`** and is **binding style direction** for every template
    prompt and for the stage-1 selection weights. Its six rules:
    **D1 grounds** — warm cream `#F6F1E7` (+ subtle paper grain) as the organic default,
    cinematic-dark as the secondary; **mid-gray, cold, saturated and gradient grounds are retired from
    every default** (7/10 picks are cream/warm; 0/10 use anything in between).
    **D2 typography** — exactly **two voices**, never a third: editorial serif (Playfair/Didone
    spirit) **or** heavy geometric grotesque; always oversized (30-60% of canvas); **exactly ONE
    brand-colour emphasis token per headline** — teal by default, indigo-italic for serif questions,
    **amber reserved for numerals and times**.
    **D3 furniture** — a letterspaced small-caps kicker **and** the `HYPEDIGITALY` wordmark footer on
    every card-class post (8/10 picks; this is the feed-level recognisability engine).
    **D4 artifact devices** — the centrepiece is a tangible, rounded (20-24px), soft-shadowed object
    from the library `{browser_frame, icon_row, icon_lineup, node_diagram}`, carrying **real marks**
    via the manifest/fetch ladder and greeked micro-text. **`icon_lineup` is itself an approved post
    format.** The two picks fed real reference assets beat the verbal-guess variants of the *same*
    concept — authenticity is visible.
    **D5 recurring brand characters** — the robot (indigo body, teal props, ink outlines, single-lens
    eye) and the anime mood (from-behind, teal/amber glow on dark) are **pinned descriptions reused
    verbatim**, so they recur as brand assets instead of drifting.
    **D6 copy** — concrete beats clever: specifics (a number, a time, a named tool) in every hook.
    **Selection re-weighting ("double down"):** elevated — serif statement / serif brand-promo shape ·
    `website_showcase` · tool stack with real marks · workflow map · dark-serif scene hook ·
    `robot_caricature` · `anime_scene` · `icon_lineup`. **Demoted to occasional rotation, NOT
    deleted** (variety reserve, and the Virlo win-rate reweight can promote any of them back) —
    `concept_dashboard`, stat hero, myth-bust split, UGC phone, and the **dark** `ig_value_sheet`,
    whose default is restyled onto the cream serif-editorial ground.

22. **Final operator decisions (2026-08-08) — these override anything conflicting above.**
    1. **LANGUAGE: default is ENGLISH** (`language: en`) for **all** destinations. Czech remains a
       fully supported config switch, not removed. The nativeness gate (item 19.D) **generalises**:
       parameterized by language, requiring native colloquial quality in whichever language is active
       — EN exemplars from `simulation/round2/prompts/*_en`, CS exemplars unchanged. Czech-glyph
       verification tasks stay (CS is still switchable) but leave the critical path of the default
       confirmation run.
    2. **CAROUSELS become CONDITIONAL, not default.** Stage 1 may select the 5-slot carousel format
       **only when Virlo slideshow evidence for the topic shows winning carousels** — evidence-gated,
       same n-floor discipline as the format reweight. Otherwise: single-image post. Additionally,
       **harden the carousel copy gate**: every body slide must carry specific practical value
       (concrete numbers, steps, tool names), and the N-F critic gets an explicit **kill rule for
       generic/filler/cringe slides**. All-or-nothing delivery unchanged. Operator's words: *"must be
       really valuable, practical and specific — no AI slop."*
    3. **SINGLE-MODEL PRODUCTION.** `gpt-image-2-text-to-image` is the **only active render model**.
       The multi-model test track ships **built and DISABLED** (`test_render.enabled: false`) — the
       registry routes and harness code are kept as built-but-disabled, exactly the `tiktok` pattern
       (§13.4) — and IV-B's scope slims to registry + config + disabled-path tests. **The per-run test
       wallet leaves the active arithmetic.** Consequence for the unknown-tool Tier 1: nano-banana-pro
       `image_input` is no longer the mechanism — **Tier 1 becomes gpt-image-2 rendering the card with
       a RESERVED artifact zone (empty browser frame / icon slots) and Pillow compositing the FETCHED
       real assets into that zone pixel-exact**, which also resolves F15's redraw caveat with strictly
       better integrity. The `nano-banana-pro` `image_input` route stays **configured-disabled** for a
       future re-enable. §9.3 recomputed accordingly (canonical $0.03/render; no test wallet in the
       per-run cost).
    4. **BUDGET: `$6.00`/day cap confirmed unchanged.**
    5. **SCREENSHOTS: no operator-supplied PNGs are required anywhere** — the automatic fetch ladder
       is the mechanism. Keep an **OPTIONAL operator-override folder**: a PNG manually dropped for a
       tool **wins** over fetched assets. Documented as optional; its absence is never blocking and
       never a degrade.

23. **Two more style classes** (2026-08-08, operator-requested, validated in `simulation/round6/`,
    finding **F20**) — both enter the **occasional-rotation pool** (same tier as `concept_dashboard`,
    Virlo-promotable):
    - **`meme_reaction`** — a two-panel reaction meme starring the **pinned recurring brand robot**
      (indigo body `#302B87`, teal accents, ink outlines, single-lens eye): top panel = comic distress
      at a manual-busywork scenario, bottom panel = smug relief with the AI-agent alternative; heavy
      grotesque captions, one teal emphasis phrase, cream ground, vintage comic texture, wordmark
      footer.
    - **`deadpan_memo`** — a satirical official-document card: `INTERNAL MEMO` letterhead furniture,
      a huge editorial-serif deadpan announcement, one calm serif body line, a distressed teal
      rubber-stamp device ("APPROVED BY AI" style), cream ground, optional gilded frame, wordmark
      footer.
    **Guardrails codified with them:** humour and satire target **PROCESSES** (meetings, copy-paste
    work, busywork) and **NEVER named people, companies, or competitor tools**; the **claim gate
    applies to any factual-sounding punchline**; language follows the destination default (EN). F20:
    both keep cream grounds, a single teal emphasis, the wordmark footer and the pinned robot —
    recognisably on-brand while being actual memes.
    *(Cadence upgraded by item 25: the meme classes hold a **reserved per-run slot**, not an
    occasional-rotation share.)*

24. **Meme-class refinements and gold-standard copy** (2026-08-08, operator feedback on the round-6
    v1 renders; v2 validated in `simulation/round6/` M1v2/M2v2). **Supersedes item 23's template
    details.**
    1. **New N-F check `visual_logic_coherent`, applied to ALL illustration classes:** the depicted
       actor/scene must match the caption's subject. The v1 failure is the canonical example — the
       brand robot panicking about *hiring a human coordinator* is nonsense, because the robot is not
       the one who would hire.
    2. **`instant_read` rule for the meme classes:** the joke must land in ~1 second, on
       universally-known visual grammar (reaction contrast, RIP tombstone), with **MINIMAL symmetric
       captions** ("Your ops team at 11 PM." / "The AI agent at 11 PM."). **The visuals carry the
       joke — never a paragraph caption on the image.**
    3. **Persona-rule carve-out, codified explicitly:** cartoon humans **ARE allowed** in the
       illustration and meme classes when the joke requires a human-vs-AI contrast — **strictly from
       behind or face-obscured, faces never visible, no named characters**. The speaker-persona rule
       is untouched.
    4. **Templates:** `meme_reaction` = **human-chaos panel vs brand-robot-serene panel** with
       symmetric time-stamped captions; `deadpan_memo` gains the **RIP tombstone** as a second
       approved device variant (celebratory-graveyard grammar: party hat, confetti, robot laying a
       flower). **The robot character description must be PINNED VERBATIM in the templates** for
       cross-post consistency — the v2 tombstone robot drifted slightly from the pinned design, and
       template pinning is what prevents that.
    5. **Gold-standard copy exemplars** (EN default) baked into the N-C prompt as few-shot examples
       and recorded as normative in II-2's brief: the IG website-showcase, LinkedIn workflow-map, IG
       meme and IG brand-promo captions quoted there in full. **Caption-craft rules they encode:**
       hook line first · concrete specifics (times, counts, tool names) · zero slop vocabulary
       (*game-changer*, *unlock*, *revolutionize* banned alongside the existing list) · meme captions
       minimal · promo CTA = the link-in-bio pattern · **hashtags ≤3 on LinkedIn, ≤5 on Instagram**.

25. **Batch composition and generation cadence** (2026-08-08, operator intent — final).
    1. **The meme classes get a GUARANTEED slot in every batch.** Default **1 meme asset per run**,
       config dial **0-2**, **alternating/rotating between `meme_reaction` and `deadpan_memo`** and
       drawing its humour angle from the run's Virlo trends. This **upgrades them out of the
       occasional-rotation pool into a reserved per-run slot**, alongside the reserved `brand_promo`
       slot; the organic Virlo-driven quota fills the rest. A default run is therefore **8 assets**:
       6 organic + 1 promo + 1 meme.
    2. **Batch composition is explicitly configurable in ONE config block** —
       `generation.batch_composition`: slots per class-pool per run, promo cadence, meme cadence,
       destination split, and language. An operator planning a batch reads one block; a reviewer sees
       the whole run shape at a glance. (The keys formerly proposed as scattered `generation.*`
       entries — `format_quota`, `format_quota_groups`, `format_quota_reweight`, `carousel_gate`,
       `brand_promo`, `language_by_destination` — all live inside it.)
    3. **Generation-cadence pattern, documented so nobody builds a scheduler:** the engine runs as an
       **invoked batch** — one invocation, one run pack, exit. **Daily or weekly scheduling is
       external** (Windows Task Scheduler / cron) and config-gated; the **posting** schedule is
       handled by **Postiz**, not by this engine. Consequences that matter for the plan: every §9.3
       number is *per invocation*; the day cap is the only cross-invocation guard; and
       `run_identity.RunLock` remains what keeps two invocations from overlapping.

## 14. Report

```md
W8-11 Output-Quality Overhaul Plan - Report
### Files to change / create
- NEW: engine/src/hypeagent/fsutil.py, asset_model.py, render_contract.py, compositing/** (package),
  style_select.py, brand_assets.py, test_render.py
- NEW: engine/tests/test_render_contract.py, test_asset_model.py, test_compositing.py,
  test_style_select.py, test_brand_assets.py, test_test_render.py
- NEW: docs/adr/0001..0006, NAVIGATION.md, CLAUDE.md, assets/logos/manifest.yaml (websearch-authored,
  descriptions + icon URLs + sources; binaries never committed)
- EDIT: media_gen.py, copy_gen.py, promptcraft.py, stages.py, llm.py, trace.py, claim_gate.py,
  ranking.py, store.py, analysis.py, packaging.py, process_summary.py, resume_state.py,
  config_load.py, collectors/virlo.py, engine/pyproject.toml
- EDIT: config/style_guide.yaml, config/themes/hypedigitaly.yaml, config/model_registry.yaml,
  assets/fonts/**
- EDIT: docs/architecture/FLOW_MAP.md, ARCHITECTURE_PLAN.md, DECISION_LOG.md, docs/plans/GOAL_ROADMAP.md
- DELETE: compose_prompt + _NEGATIVE_CONSTRAINTS (+ every stale reference), MAX_BODY_WORDS,
  _DESTINATION_CONSTRAINTS, MIN_CAROUSEL_SLIDES, _QUOTED_SPAN_RE twin, ranking.py:276-277,
  process_summary._find_image_brief/_reconstruct_prompt, CraftedPromptSet.hero_prompt/usable,
  style_guide.yaml:91-93, model_registry people_free_composition
### What changes
- Wave I freezes the shared contract (RenderContract, slot model, state machine, crafted-prompt shape)
  in ONE barrier task, then deletes the ungoverned prompt path; a GovernedPrompt type makes an
  ungated submission unconstructible, vision QA becomes unconditional, and three ledger guards
  (prompt-sha, phase-0 quarantine, QA-budget) close the re-entry holes.
- One ConstraintSet is read by every author AND every validator; contradictory config refuses to load.
- Instagram becomes a real 5-slot carousel with per-slot state and all-or-nothing delivery.
- Virlo evidence becomes a hard dependency with a trichotomous evidence_class; register derives from
  the generation mode everywhere.
- **The rendering flip (§13 items 19-24).** Canonical creative rendering becomes
  gpt-image-2-text-to-image FULL-DESIGN renders — expressive styled typography in-image — behind a
  mandatory per-glyph text-verification gate, with one retry and the Pillow-composited path demoted
  to the fallback rung and copy-only below it. The deterministic compositing layer is still built in
  full: it is now the fallback, the kill-switch destination and the pixel-exact way real fetched
  brand assets reach an image.
- **A twenty-nine-system style library** with two-stage Virlo-weighted selection (per-run format
  quota with rotating groups + per-asset topic regex, deterministic, seeded) whose defaults "double
  down" on the operator's ten hand-picked favourites (D1-D6) while keeping every unpicked class in a
  1-of-6 rotation reserve that Virlo evidence can promote back. Carousels became conditional on
  slideshow evidence; a `brand_promo` asset is appended each run from config with zero LLM calls.
- **Real brand assets, or nothing.** Every tool named in copy renders its mark; a `brand_assets` leaf
  fetches an unknown tool's real logo and real product visual from the tool's own site (browser UA,
  permanent cache, optional operator override) and composites them pixel-exact into a reserved
  artifact zone. A real product's UI is never diffusion-invented — fictional UI is a whole style
  class, invented "real" UI is an integrity failure.
- **Single-model production.** One active render model; nano-banana-pro and nano-banana-2 are
  reserved routes, and the multi-model test harness ships built and disabled — so a future model
  question is a config flip rather than a project, and today's run spends nothing on it.
### Wire-in points
- §8 table: 47 base symbols + 20 ratified-package symbols, each with its import/call/registration
  site and the task that applies it.
- stages.py, all three config YAMLs, pyproject.toml, assets/fonts, NAVIGATION.md and the single
  CONTRACT_VERSION bump are conductor-owned aggregating files, written last in each wave
  (IV-B-5 for the test-harness wave). `reference/OPERATOR_FAVORITES_DNA.md` is read-only for every
  executor.
### Reuse audit
- §3: 10 searches. Reuse: trace.decision, claim gate, ledger, caps, leak checks, test doubles,
  visual_profile pipeline, plan_media_assets 1:N expansion. Consolidate: three cap constants → one
  ConstraintSet; two _QUOTED_SPAN_RE copies → one; ad-hoc sha/writes → fsutil. Round-2/3: same
  KieClient transport + create_task choke point for test renders; Fetcher idiom for logo fetches;
  Phase-8 rotation kept as the selection degrade path; model_string column reused, only the UNIQUE
  widens. New only where nothing exists: fsutil, asset_model, render_contract, compositing,
  style_select, brand_assets, test_render. Round-4/5: the flip is a route + prompt-builder change on
  the SAME transport and choke point, not a new renderer; the ladder is `ATTEMPT_MAX` + the existing
  composite route re-ordered; `logo_assets` widened into `brand_assets` rather than forked;
  `artifact_zone` is `logo_zone` generalised; `brand_promo` copy is config-authored through the
  existing `CopyAsset` shape, not a second authoring node.
### Tests / acceptance criteria
- Barrier per wave: full `cd engine && python -m pytest -q` (baseline 515 passed).
- 19 test files touched, 6 new; **13** integration scenarios; the confirmation-run gate in §10.
### Dead code
- Found: 11 items (§0-2 list). Deletion pre-cleared by operator task 0-2; executors report but never
  delete anything additional.
### PRD
- Relevant section: no prd/ tree exists; ARCHITECTURE_PLAN.md §5.6 + FLOW_MAP.md §3 are the governing
  equivalents.
- Conflicts: both documents sanction the ungoverned fallback that produced the fa51 defects.
- Amendments proposed (2): (1) §5.6 terminal rung becomes plan-only/copy-only and names the deleted
  fallback — pre-authorised by locked decision 3; (2) claim-gate qualification co-location, a
  user-visible tightening that may block copy which previously passed. Applied by V-2, recorded V-3.
- Assumptions: Instagram carousels = 5 slots WHEN the evidence gate fires (Q1 + item 22.2), Pillow
  approved (Q2), Montserrat vendored (Q3), default language EN (item 22.1), one active render model
  (item 22.3), $6.00/day (item 22.4).
- No third PRD amendment is required by the ratified package: the flip changes which component draws
  the pixels, not the fail-closed contract the two amendments are about. V-1/V-2 still restate the
  flow and the image-contract axes.
### Simple summary
- fa51 shipped 2 of 6 usable images because a second, ungoverned prompt path could overrule the
  governed one, and because two config files disagreed about how long a slide may be. This plan
  deletes the second path and makes the rules one shared object that both the writer and the checker
  read. Then 44 test images changed the picture-making half of it: one model turned out to spell
  well enough that we now let it design the whole image, typography and all — checked letter by
  letter against the words we approved, retried once if it slips, and typeset by us if it slips
  again. The library grew to twenty-nine looks built around the ten images the operator actually
  liked, posts are single images unless the trend data says carousels win, every tool we mention
  shows its real logo (fetched from the tool's own site when we do not already have it), we never
  fake a real product's screen, one brand-promo post goes out each run, and the copy has to sound
  like a person saying it out loud. One image model does all of it; two others sit configured and
  switched off, ready for the day the question comes up again.
```

> **NAVIGATION.md: update required** — task 0-5 authors it before any code lands, and each wave's
> conductor appends that wave's new paths, config keys and commands in the same commit, per
> `CODING_GUIDELINES.md` §21 *End-of-Session*.
