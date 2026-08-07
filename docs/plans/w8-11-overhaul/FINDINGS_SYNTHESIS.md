# W8-11 Output-Quality Overhaul — Findings Synthesis (input to the implementation plan)

Consolidated from 14 analysis workstreams over confirmation run `2026-08-07_fa51` (6 per-creative forensic critiques, copy slop audit, Virlo fidelity audit, live Virlo data pull, 2026 design benchmark, LLM prompt-template audit, flow architecture review, pipeline root-cause map, full-flow de-cruft audit). Date: 2026-08-07.

## 0. Operator-locked decisions (binding, do not relitigate)

1. **Voice: faceless institutional.** No named individuals, no invented personas ("I'm Marcus"/"I'm Radka" class), no first-person-singular fabricated experience. Brand speaks as **HypeDigitaly** / **HypeLead**. Tone stays practitioner-direct, not corporate-stiff. Replaces the current `_VOICE_RULES_BLOCK` rule 1 (which pins "Pavel Čermák" — `copy_gen.py:427-430`).
2. **Instagram: true multi-image carousels.** Slot-based asset model, ~5 generated images per IG asset (cover + 3 body + end card), 1:1 slot→image, all-or-nothing delivery per asset. Copywriter is briefed to write exactly the slides that will be generated.
3. **Failure philosophy: fail-closed.** `compose_prompt` as a submission path is DELETED. One bounded repair retry with the verbatim validator reason fed back; still failing → asset ships copy-only (or held) with the reason in the digest. No ungoverned prompt ever reaches the image API; no delivered image ever skips vision QA.
4. **Virlo evidence: hard dependency, block-by-default.** `media.require_visual_evidence: true`. No trend evidence → no image generation, digest banner. Plus the starvation fix so evidence is almost always present (see §4.1).
5. **Text: hybrid compositing.** The engine typesets all text-dense slides itself (exact Montserrat, brand hex, claim-gated strings — HTML/CSS→PNG or Pillow), overlaid on generated or flat/textured backgrounds. Diffusion renders text only for short-hook covers/scenes (≤2 short spans). This is the largest new build item.
6. **De-cruft mandate:** delete/fix the redundant and harmful gates listed in §7.

## 1. Root causes (from the architecture review; all confirmed by code + run evidence)

- **D1 — Dual creative authority.** N-C's free-text `image_brief` is itself renderable via `compose_prompt()` (`media_gen.py:229-241`, call sites `:1300`, `:1479`). When governed N-D output fails validation, the ungoverned author wins. 4/6 fa51 images shipped this way → gibberish, lorem ipsum, "EYEBROW TAG" placeholders, off-topic creative, gate-blocked "35,095" claim rendered.
- **D2 — Constraint topology.** Hard constraints live in validators, not the authoring contract. `style_guide.yaml:93` tells N-C "60-90 words per slide"; `promptcraft.py:664` caps at `MAX_BODY_WORDS = 28`; N-D must embed slide text VERBATIM (`SYSTEM_PROMPT` line ~116) → **deterministically unsatisfiable** for any body >28 words. All 3 IG carousels died this way. Headline 12-word cap is built into `destination_constraints` (`copy_gen.py:829-848`) but **never read into any prompt** (dead data).
- **D3 — Degrade-to-ungoverned instead of fail-closed.** Spec (ARCHITECTURE_PLAN §5.6) says terminal rung = plan-only; implementation submits ungoverned. Gate-block→fallback substitution emits NO decision event (silent). FLOW_MAP §3 documents the fallback as intended — doc must be amended too.
- **D4 — Trend evidence is decoration.** `pick_generation_mode` (`promptcraft.py:584-625`) silently falls to `_legacy_pick_archetype_register` (`:386-425`) which **hardcodes `register="editorial"` at line 425**. N-A skipped in fa51 ("no virlo_corpus.yaml") because the Virlo collector's same-day idempotent-hit path never rebuilds the corpus from the already-captured payload (`collectors/virlo.py:402-404,482-502`). Result: zero mechanical Virlo→image link; static style shipped while run reported success.

## 2. Key defect coordinates (fix targets)

| Defect | File:line |
|---|---|
| Ungoverned fallback `compose_prompt` | `media_gen.py:229-241`, call sites `:1300`, `:1479` |
| QA skip keyed to code path (`qa_expected_text=None` on fallback) | `media_gen.py:706-717` (esp. `:712`), skip at `:1010-1011` |
| Claim gate combined_text weakness (qualification satisfied asset-wide, not co-located) | `claim_gate.py:141-145`, `:189-190` |
| Prompt claim gate conditional on panel (dead guard, delete) | `stages.py:850-851` |
| Register hardcoded "editorial" | `promptcraft.py:425` |
| 28-word cap + verbatim-embed contradiction | `promptcraft.py:664`, `:700-726`; `style_guide.yaml:93` |
| Whole-carousel death from one bad slide | `promptcraft.py:953-969` |
| No feedback retry for validation failures (only truncation/parse retry) | `promptcraft.py:915-969`, `llm.py:369-420` |
| Token ceilings: N-C 4000 (100% truncate), N-D 6000 (all carousels truncate), N-F absent from overrides → 2000 (2/6 assets never critiqued, shipped unreviewed) | `config/themes/hypedigitaly.yaml:319-334`, `copy_gen.py:975` |
| Persona enforcement absent (no speaker check anywhere; critic rubric has no identity item) | `copy_gen.py:427-430` (rule), `:1025-1044` (rubric) |
| Virlo corpus starvation on idempotent hit | `collectors/virlo.py:402-404,482-502` (+ silent `except OSError: pass` at `:501-502`) |
| R1 freshness window can never fire (`retrieval_time` refreshed on every upsert) | `store.py:653-676`, `ranking.py:644-652,715-764` |
| Fit-score quantization (ties at 0.426 → insertion-order ranking) | `ranking.py:159-179` |
| Dead gate: `if not fit_verdict.matched_terms` unreachable | `ranking.py:276-277` |
| Stale `response_shape_expected` doc-string ("people-free") contradicts W8-10 person policy | `copy_gen.py:136-138` |
| N-E rubric lacks explicit multi-panel-collage check | `media_gen.py:883-937` |
| QA-outage rollup missing (all-images-skipped still reports stage ok) | `media_gen.py:1043-1049` |
| Stale docstring: analyzed_items "not yet wired" (it is wired) | `promptcraft.py:842-843` vs `stages.py:834-848` |

## 3. Target architecture (from the architecture review — adopt)

- **RenderContract** resolved once per asset before authoring (destination, format+slot counts, per-slot word caps incl. `exempt_from_word_cap` for prompt-quote slides, caption rules + disclosure literal, claim policy, persona=institutional/none, visual mode/register/archetype/evidence_class/aspect/logo policy, contract_version+sha256). Load-time consistency check: any two config sources disagreeing = config error, run refuses. All authoring prompts and all validators read the SAME object; constraints appear in authoring prompts verbatim (numbered "HARD CAPS" block).
- **On-image text = first-class gated copy** (`Slot.on_image_text {title, body?, kicker?}`), claim-gated at authoring with repair loop. `image_brief` demoted to structured non-renderable `visual_intent {subject, proof_element, tools_named[], environment_hint}` — type-level incapable of reaching the provider.
- **Slot model:** `CopyAsset{caption, slots[]}`; hero = format=single with one slot; carousel = N slots; `MediaPlan` 1:1 with Slot, derived never invented; `is_cover` role-derived. All-or-nothing per asset. `max_generated_slides` lives in destination policy so N-C writes exactly what will be generated.
- **Per-slot state machine:** PLANNED → CRAFTED → validate(contract) → [REPAIR ≤1 with verbatim reason] → BLOCKED_NO_IMAGE | text-set closure check (`<<…>>` ⊆ gated on_image_text) → claim gate on exact submitted bytes → leak check → QA-budget reservation → SUBMITTED → QA (unconditional) → DELIVERABLE | REGEN ≤1 | HELD_QA. Every transition emits a decision event; deliverability derived from manifest state, never file presence.
- **Invariants I1-I5** (add to FLOW_MAP §6 with owning tests): single submission choke point (`GovernedPrompt` value object, one `create_task` call site); gate totality on exact bytes (gate unconditionally available — missing brand panel = fail-closed trigger); text-set closure; QA totality (skipped ≠ pass; text-conditional booleans skip individually, subject/logo/composition/gibberish checks never skip); no silent substitution (every provenance-class change emits a decision event).
- **Evidence posture:** `VisualProfile` computed from the durable store keyed (theme, date-window), never from this run's fetch side effects. `evidence_class ∈ {evidence-backed, evidence-thin, evidence-absent}`; absent ⇒ block (locked decision 4); thin ⇒ generate + review-required. Register derived from mode in ALL paths (kill the line-425 hardcode); add register/mode coherence validator.
- **Sequencing:** fail-closed ladder + invariants first (stops the bleeding) → RenderContract topology → slot model/carousels → evidence link + compositing. Bump `PROMPT_PATTERN_VERSION` 3→4 (write-ahead ledger identity).

## 4. Prompt & LLM changes (from the prompt audit — adopt)

1. **Shared ConstraintSet** (single config source) threaded into: N-C prompt (numbered HARD CAPS block, not style-guide YAML dump), N-C post-return validator, N-D SYSTEM_PROMPT, N-F rubric. Fix/delete `style_guide.yaml:93` "60-90 words per slide". Surface the 12-word headline cap (currently dead data).
2. **Voice rules rewrite** for faceless institutional voice: ban "I'm [Name]" and any self-introduction; ban fabricated personal anecdotes; first-person plural only when honest ("what we see with Czech SMEs"); the 5 hard slop constraints from the copy audit (persona whitelist=∅, max one arrow-list per post, engagement-bait only with named specific payoff, first-person claims sourced-or-institutional, no fake-casual sign-offs). Deterministic speaker check: regex for self-introduction patterns → hold/retry.
3. **Token budgets by output cardinality:** N-C 4000→8000; N-D 6000 hero / 12000 carousel (or base + per-slide); **add `humanness_critic` to node_overrides** (≥4000; 6000 for carousels). General: `max_tokens = base + slides × per_slide`.
4. **Structured outputs:** move to json_schema-typed responses where provider supports; add `self_check` word-count fields the model must fill; N-C validates its own caps pre-return.
5. **Critic rubric additions:** (13) speaker-identity/no-persona check, (14) cap re-verification against ConstraintSet, (15) structural-formula check (Old way/New way, ❌/→ chains, arrow lists >4, duplicate CTA mechanism across siblings). Fix token budget first — the critic never completed on 2/6 assets and silently shipped originals.
6. **N-E trigger content-based:** scan the submitted prompt for renderable-text markers; text booleans skip individually; subject/composition/gibberish/logo checks always run. Add explicit "no multi-panel collage when one image requested" and "no lorem ipsum / placeholder-label words" instructions.
7. **STYLE/RENDER coherence:** archetype→register binding in style_guide (`visual_archetypes[*].register`); one design system per asset; RENDER may not contradict STYLE; generalize `_EDITORIAL_LEAK_RE` to a register-keyed table.

## 5. Design system (from benchmark + Virlo live data — adopt as style_guide/config content)

Six named style systems (full specs in the benchmark report — layout skeleton, palette recipe, type scale, texture, text budget, gibberish-proofing each):
| Topic | LinkedIn | Instagram |
|---|---|---|
| n8n + Apify lead-gen workflow | **Signal Card** (indigo infra-minimal, ≤2 spans) | **Annotated Proof** (real-screenshot + hand-drawn teal annotations) |
| AI sales-agent lead scoring + stat | **Statement Hero** (oversized stat as hero, digits are low-risk) | **Stat Slab** (full-bleed brand color block) |
| Claude ops-assistant for founders | **Editorial Brief** (serif authority, 1 span, vector-overlaid) | **Prompt Sheet** (monospace prompt card — text composited, never diffusion) |

Hard DON'Ts (encode as validator/QA checks): no flattened multi-panel collages; no clip-art icon rows; no lorem ipsum/placeholder labels; no fake/invented dashboards or third-party UI (real accurately-branded UI or none); no default gradient-mesh.

Virlo ground truth (live pull, monitors `9c96fddf-…` and `623203a9-…`, both finalized): UGC-real beats polished (top weighted scores 52.2/49.5 from <4K-follower accounts using real screen recordings/talking heads); winning slideshows = real photo or paper-texture grounds + 1-2 line bold hooks + REAL product screenshots as proof panels; text-dense guide slideshows (tables/steps) are a top faceless format; garbled fake-AI-UI text correlates with the worst relative performance in the dataset (score 8.4 at 157K followers). Flat corporate-navy cards appear nowhere among winners. Style anchors per topic (creator/URL/score) are in the Virlo reference report; wire the strongest into the dynamic-inspiration path as per-topic exemplars. Hook patterns to encode in copy guidance: numbered-promise ("5 apps I use to run my entire business"), dollar/time-boxed specificity, tutorial-promise ("X — Setup Guide"), confessional-reveal — all achievable facelessly.

Compositing module (new): deterministic typesetting layer (HTML/CSS→PNG via headless Chromium, or Pillow) rendering `on_image_text` in real Montserrat + brand hex over (a) flat/textured programmatic grounds or (b) diffusion-generated background scenes with reserved text zones. Text-dense slide roles (body/prompt_quote/checklist/end_card) ALWAYS composited; diffusion-only text allowed solely for cover-hook ≤2 short spans when the mode demands in-scene text. This eliminates the entire gibberish class and unlocks the winning guide formats.

## 6. Copy quality bar (from the copy audit)

Current average 3.5/10 ("would a skeptical Czech/EU SME founder stop and save this"). Payload is decent (7-8/10 on IG carousels) — voice/persona/bait are the failures. Institutional-voice rewrite directives per asset are in the copy audit report. Value-density floor: every post carries ≥1 genuinely actionable, non-obvious, verifiable payload (real settings, real prompts, real numbers with qualification); "Comment X" gating only with a named specific deliverable.

## 7. De-cruft actions (from the de-cruft audit)

**DELETE:** (1) `compose_prompt` + call sites (locked); (2) `ranking.py:276-277` dead matched-terms veto (leave one-line comment for future model-backed FitJudge); (3) `stages.py:850-851` panel-None guard (call gate unconditionally).
**FIX:** Virlo idempotent-hit corpus reconstruction (load `raw_payload_path`, run `build_virlo_corpus`/`write_virlo_corpus`); add trace event to the bare `except OSError: pass` at `collectors/virlo.py:501-502`; R1 freshness gate on `first_seen_at`/publish date instead of upsert-refreshed `retrieval_time` (`store.py:653-676`); fit-score granularity (weighted overlap ratio, or fit=gate+band only); per-slide failure granularity in `craft_prompts` (hold/repair the failing slide, not the whole set — reconciled with all-or-nothing at DELIVERY, not at CRAFT); validation-failure feedback retry in N-D (second LLM round with the exact failing reason); claim-gate qualification co-location (same field/sentence as the number); stale `response_shape_expected` string; stale `promptcraft.py:842-843` docstring; QA-outage aggregate rollup (0 QA successes with N images ⇒ stage degraded, not ok).
**KEEP (verified load-bearing):** within-run fetch idempotency, write-ahead media ledger + spend reconciliation, caps/circuit breakers, leak checks, claim-gate lexicons, dedupe/resurgence, quantile banding, truncation-never-accepted invariant, N-E rubric booleans (all consumed).

## 8. Documentation amendments (same cycle as code — standing rule: FLOW_MAP artifact republished at same URL)

- `FLOW_MAP.md` §1 (diagram: remove fallback edge, add contract-resolution node, N-D layout-only, N-E unconditional, terminal no-image states), §2 (trace fixes to D1-D4), §3 (delete fallback + QA-skip from contracts), §4 (new config surface: render_contract, require_visual_evidence, persona, format/max_generated_slides, compositing), §5 (render_contract.yaml, manifest deliverability states, decision trail), §6 (invariants I1-I5 verbatim), §7 (W8-11 list restated as D1-D4 structural fixes with status).
- `ARCHITECTURE_PLAN.md` §4.2a (stale "no legible text" rubric → N-E binary set), §5.3 (image contract axes), §5.6 (plan-only as only terminal rung; name the deleted fallback), §3.2/§4.5 (destination×asset matrix w/ slide counts vs §8.11 caps), §11.3 (fail-closed triggers: gate unavailable, evidence absent, QA budget unavailable), §14.3 (image prompts in checked surfaces, exact-bytes rule), §12.4 (bind slide-level regen to slot model).
- `config/style_guide.yaml`: word counts become RenderContract projections; archetype→register binding; 6 style systems encoded; institutional voice hooks.
- `GOAL_ROADMAP.md`: W8-11 re-expressed as the 4 structural changes + de-cruft list.
- `PROMPT_PATTERN_VERSION` 3→4.

## 9. Verification bar for the plan

- Unit: contract load-time consistency check; speaker-pattern validator; per-slot state machine transitions; text-set closure; compositing text-fidelity (rendered PNG text == input string via OCR or draw-then-compare).
- Integration: a full run in which (a) an intentionally over-cap slide produces BLOCKED_NO_IMAGE + copy-only delivery, never a fallback; (b) a gate-blocked number never reaches kie; (c) absent virlo evidence blocks generation with banner; (d) every delivered image has a QA verdict.
- Confirmation run gate: 6/6 assets either DELIVERABLE-with-QA-pass or cleanly held with reason; zero gibberish; zero off-topic; carousels delivered as N images.
