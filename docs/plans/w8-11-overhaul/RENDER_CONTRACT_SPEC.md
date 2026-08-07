# RENDER CONTRACT SPEC — W8-11

*Companion to `PLAN.md`. Self-contained: an executor implements `engine/src/hypeagent/render_contract.py`,
`engine/src/hypeagent/asset_model.py` and `engine/src/hypeagent/fsutil.py` from this file alone.
Authored 2026-08-07 from `FINDINGS_SYNTHESIS.md` §3/§4 plus a full read of the engine; revised after the
three-reviewer panel (concurrency / prompt-design / code-quality).*

***ROUND-4/5 AMENDMENT (2026-08-07/08, operator-ratified — binding; `PLAN.md` §13 items 19-25).***
*Three changes reach into this spec; Wave 0 task **0-6** applies the textual sweep, and the shapes
below are already amended in place:*

1. ***The rendering flip.*** *Canonical creative rendering is a **`gpt-image-2-text-to-image`
   FULL-DESIGN render** — the model draws the finished card, typography included — verified per glyph
   against the gated `on_image_text`, retried once, and only then composited by Pillow. So
   `SlotSpec.text_render_mode` gains the value `"full_design"`, `ground_source` now describes the
   **fallback** ground, `RenderPolicy` loses the two diffusion-text caps (they are **lifted**, not
   zeroed) and gains the ladder's three dials.*
2. ***Language and format become resolved inputs, not per-destination constants.***
   *`RenderContract.language` is resolved server-side from
   `generation.batch_composition.language_by_destination` (**default `en`**, `cs` a supported
   switch), and `RenderContract.format` is the **evidence-gated** stage-1 decision
   (`single` by default, `carousel` only on Virlo slideshow evidence) — so `resolve_render_contract`
   takes both as arguments.*
3. ***Two new load-time checks*** *(10 and 11) and a recomputed §7 config surface.*

---

Governing decision: **the constraint set that authors are told and the constraint set that validators
enforce must be the same object.** D2 (the run-killing defect) exists only because they were two
different things — `style_guide.yaml:93` said "60-90 words per slide" to N-C while
`promptcraft.py:664` enforced 28 words on N-D, with a VERBATIM-embed requirement in between.

---

## 1. Where this code lives

Three new modules, all leaves. `render_contract` and `asset_model` are imported by `copy_gen`,
`promptcraft`, `media_gen`, `packaging` and `process_summary`; keeping them dependency-light is what
lets those five modules share types at all.

| Module | Contains | May import |
|---|---|---|
| `engine/src/hypeagent/fsutil.py` (NEW) | `atomic_write_text`, `atomic_write_bytes`, `sha256_hex` | stdlib only |
| `engine/src/hypeagent/asset_model.py` (NEW) | `SlotRole`, `Slot`, `OnImageText`, `VisualIntent`, `CopyAsset`, `SlotState`, `advance()`, `asset_deliverability()` | stdlib only |
| `engine/src/hypeagent/render_contract.py` (NEW) | `CONTRACT_VERSION`, `SlotSpec`, `CaptionRules`, `ClaimPolicy`, `PersonaPolicy`, `VisualPolicy`, `RenderPolicy`, `RenderContract`, `ConstraintSet`, `resolve_render_contract()`, `check_contract_consistency()`, `GovernedPrompt`, `UngovernedSubmission`, `govern()`, `deterministic_prompt_leak_check()`, `QUOTED_SPAN_RE` | stdlib, `fsutil`, `asset_model`, `claim_gate`, `config_load` |

Nothing else is created. Everything else in W8-11 is an edit to an existing module.
`asset_model.py` is specified in `SLOT_MODEL_SPEC.md`; this file specifies `render_contract.py`,
`fsutil.py` and the `GovernedPrompt` choke point.

**Why new modules rather than growing `media_gen.py`:** these types have five consumers each. Placing
them in any one consumer would make the other four import a 1757-line module to get a dataclass.
(Note: there is no import *cycle* in the engine today — `media_gen.plan_media_assets` types its inputs
`Any` at `media_gen.py:657-669` to avoid *creating* one. The new leaves remove the need for that
work-around; that is a readability gain, not a cycle fix.)

### 1.1 `fsutil.py` — shared infrastructure primitives

```python
def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None
def atomic_write_bytes(path: Path, data: bytes) -> None
def sha256_hex(data: bytes | str) -> str
```

Atomic writes are temp-file-plus-`os.replace` in the destination directory. Every artefact write in the
engine routes through these: `resume_state.py:246`, `promptcraft.py:258-263` (`media_prompts.yaml`),
`collectors/virlo.py:904-914` (`virlo_corpus.yaml`), `stages.py:548-550`, and every compositing PNG
write. Today a crash mid-write leaves a truncated YAML that `--resume` then reads.

`sha256_hex` is the **single** hashing helper. `media_gen.prompt_sha256` (`media_gen.py:244-245`)
becomes a thin alias for call-site stability; `render_contract` and `compositing` use `fsutil.sha256_hex`
directly and define no local copy.

---

## 2. `RenderContract` — resolved once per asset, before any authoring

```python
CONTRACT_VERSION: Final[int] = 3      # see §8 — bumps to 4 exactly once, at Wave IV

@dataclass(frozen=True)
class SlotSpec:
    index: int                      # 1-based, matches Slot.index
    role: SlotRole                  # from asset_model
    required: bool                  # a missing required slot fails the asset
    max_title_words: int
    max_body_words: int | None      # None == this role carries no body
    exempt_from_word_cap: bool      # prompt_quote slides carry a verbatim prompt
    text_render_mode: str           # ROUND-4/5: "full_design" (canonical — the model renders the
                                    #   complete gated text in-image) | "composited" (the fallback
                                    #   rung, and what a canonical_render_enabled: false run uses
                                    #   for every slot) | "none"
    ground_source: str              # "programmatic" | "diffusion" — PER SLOT, see §2.1.
                                    #   ROUND-4/5: this now governs the FALLBACK ground only;
                                    #   "diffusion" means a text-free gpt-image-2 re-render that
                                    #   honours reserved_text_zone (single-model production).
    is_cover: bool

@dataclass(frozen=True)
class CaptionRules:
    min_words: int
    max_words: int
    max_chars: int
    disclosure_literal: str         # "[AI-generated content]" — one source, see §5
    hashtags_allowed: bool
    cta_max_count: int              # 1 (style_guide cta_stack: pick_one_of)

@dataclass(frozen=True)
class ClaimPolicy:
    checked_fields: tuple[str, ...]         # ("headline","caption","on_image_text","visual_intent")

@dataclass(frozen=True)
class PersonaPolicy:
    mode: str                       # "institutional" | "none"  (never a named individual in W8-11)
    speaker_name: str               # "HypeDigitaly" — the ONLY name allowed to self-identify

    # Everything else is DERIVED from mode, not configured:
    #   first_person_singular_allowed == False for both modes
    #   first_person_plural_allowed   == (mode == "institutional")
    #   self_intro_banned             == True for both modes

@dataclass(frozen=True)
class VisualPolicy:
    mode: str | None                # promptcraft GENERATION_MODES key
    register: str                   # derived from mode — NEVER hardcoded (kills promptcraft.py:425)
    archetype: str | None
    evidence_class: str             # "evidence-backed" | "evidence-thin" | "evidence-absent"
    aspect_ratio: str               # from media.aspect_ratio_by_destination
    logo_policy: str                # "real_third_party_ok" | "brand_only" | "none"
    style_system: str               # one of the six named systems, see STYLE_SYSTEMS_SPEC.md

@dataclass(frozen=True)
class RenderPolicy:
    compositing_enabled: bool
    # composited_roles DELETED (review blocker B3 — a third declaration of the same routing fact).
    # diffusion_text_max_spans / diffusion_text_max_words_per_span DELETED (ROUND-4/5): the canonical
    # prompt now embeds the COMPLETE gated on_image_text verbatim, exactly as MULTI_MODEL_SPEC §4.2
    # already lifted the cap for test prompts. The cap is lifted, not zeroed — R3's opposite
    # recommendation is reversed, see PLAN §13 item 19.A.
    canonical_render_enabled: bool = True       # the flip's reverse gear: false => every slot enters
                                                #   the ladder at the composited rung (pre-flip
                                                #   behaviour), and the run spends nothing on
                                                #   canonical renders
    text_qa_retry_max: int = 1                  # one retry after the first text defect (ATTEMPT_MAX 2)
    fallback_to_composite: bool = True          # false => a second text defect goes straight to
                                                #   copy-only instead of the composited rung

@dataclass(frozen=True)
class RenderContract:
    contract_version: int           # == CONTRACT_VERSION; asserted at resolve time
    destination: str
    asset_id: str
    language: str                   # ROUND-4/5: resolved server-side from
                                    #   generation.batch_composition.language_by_destination
                                    #   (default "en"; "cs" a supported switch). NEVER model-chosen.
    format: str                     # "single" | "carousel" — ROUND-4/5: the EVIDENCE-GATED stage-1
                                    #   decision, not a per-destination constant. "single" unless the
                                    #   Virlo slideshow gate fires (STYLE_SYSTEMS_SPEC §4.1).
    slots: tuple[SlotSpec, ...]
    caption: CaptionRules
    claim: ClaimPolicy
    persona: PersonaPolicy
    visual: VisualPolicy
    render: RenderPolicy
    sha256: str                     # over the canonical JSON of every field above except sha256

    def slot(self, index: int) -> SlotSpec: ...
    def max_generated_slides(self) -> int: ...          # len(self.slots)
    def diffusion_touched_slots(self) -> tuple[SlotSpec, ...]:
        """Slots with any diffusion surface (ground_source == "diffusion" or
        text_render_mode == "diffusion"). N-D is skipped entirely for the rest,
        and N-D's carousel token budget is sized on THIS count, not len(slots)."""
    def constraints(self) -> ConstraintSet: ...          # §3
```

`sha256` = `fsutil.sha256_hex(json.dumps(asdict(self_without_sha), sort_keys=True, ensure_ascii=False))`.
It is written into `media_prompts.yaml`, into every slot provenance YAML, and into `resume_state.yaml`
(§8) so a resumed or re-crafted asset can prove it was authored against the same contract.

### 2.1 `ground_source` is per-slot

Placing it on `RenderPolicy` was a schema mismatch; it lives on `SlotSpec`.

**ROUND-4/5 restatement (supersedes the round-2 census sentence that stood here).** Under the flip
there is no "fully programmatic" system left: **every slot of every one of the twenty-nine style
systems is a canonical `gpt-image-2-text-to-image` render**, so the diffusion-TEXT surface is the
whole library rather than two covers. What the three routing categories now partition is *how the
prompt is authored*, not *whether the model is called* — `llm_crafted` (scene/illustration slots that
need a per-topic description from N-D), `templated_diffusion` (recipe-determined cards, deterministic
prompt, zero LLM), `programmatic` (**the fallback rung and the kill-switch destination only**).
`SlotSpec.ground_source` therefore answers one question: *when this slot falls back, is its ground
drawn by Pillow from the recipe (`"programmatic"`) or re-rendered text-free by gpt-image-2 honouring
`reserved_text_zone` (`"diffusion"`)?* `RenderPolicy` keeps only the asset-wide keys listed above.

### Resolution

```python
def resolve_render_contract(
    *, asset_id: str, destination: str, language: str,
    generation: GenerationConfig, style_guide: dict[str, Any],
    visual: VisualPolicy,
) -> RenderContract
```

Pure function, no I/O, no LLM. Called **once per asset**, in `stages.stage_copy`, *before*
`copy_gen.build_copy_request` — the contract is an input to authoring, not a post-hoc check. It is
stashed on `ctx.extra["render_contracts"][asset_id]` and re-read by the media stage; it is **never
re-resolved** in the media stage (re-resolution is how the two constraint sets drifted apart in the
first place).

`VisualPolicy` is built by the evidence layer (`analysis.resolve_visual_evidence`, Wave IV) and passed
in. Until Wave IV lands, the caller passes a `VisualPolicy` with `evidence_class="evidence-thin"` and
the register derived from `promptcraft.pick_generation_mode`'s mode — never the string `"editorial"`
written by hand. On a `--resume`, the policy is **read from `resume_state.yaml`, never re-derived** (§8).

---

## 3. `ConstraintSet` — the single projection that authors AND validators read

```python
@dataclass(frozen=True)
class ConstraintSet:
    lines: tuple[str, ...]          # numbered, human-readable HARD CAPS, verbatim for prompts
    caps: Mapping[str, int]         # machine-readable, for validators
    contract_sha256: str

    def as_prompt_block(self) -> str:
        # "HARD CAPS — every one is checked by a deterministic validator after you answer:\n"
        # "1. ...\n2. ...\n"
```

`caps` keys (exact — both sides read these, no second copy anywhere):
`headline_max_words`, `caption_min_words`, `caption_max_words`, `caption_max_chars`,
`slot_count`, `slide_title_max_words`, `slide_body_max_words`, **`prompt_quote_max_words`**,
`on_image_text_max_spans`, `on_image_text_max_words_per_span`, `cta_max_count`,
**`hashtag_max_count`** (ROUND-4/5, `PLAN.md` §13 item 24: **3** on `linkedin`, **5** on
`instagram_feed`; enforced deterministically at authoring like every other cap, never as prose).

`prompt_quote_max_words` (value **50**, derived from the Prompt Sheet type scale in
`STYLE_SYSTEMS_SPEC.md` §2.6) exists because `exempt_from_word_cap` alone means *unbounded*, and the
first place an over-long verbatim prompt fails is at compositing — the most expensive point in the
chain. The exemption is from the *body* cap, not from all bounds.

Threading (Live-Path Discipline — each row is a required wire-in, not optional):

| Consumer | Where | What it replaces |
|---|---|---|
| N-C authoring prompt | `copy_gen._build_openrouter_prompt` (`copy_gen.py:457-585`) — `constraints().as_prompt_block()` into `system`, right after the voice block, **and repeated as a compact numeric restatement immediately before `schema_hint`** (constraint sandwich: caps stated once at the top of a long prompt are the ones models drop) | the style-guide YAML dump that carried `style_guide.yaml:93`'s "60-90 words per slide" |
| N-C post-return validator | new `copy_gen.validate_against_contract(result, contract)` inside `OpenRouterProvider.generate` (`copy_gen.py:730-822`), before the corrective-retry decision | nothing — this check did not exist; the contradiction surfaced two nodes downstream |
| N-D system prompt | `promptcraft.SYSTEM_PROMPT` (`promptcraft.py:109-166`) becomes a template taking `constraints.as_prompt_block()` | the implicit, never-stated 28-word cap |
| N-D validator | `promptcraft.validate_crafted_prompt` (`promptcraft.py:687-751`) takes `caps` | module constant `MAX_BODY_WORDS = 28` (`promptcraft.py:664`) — **delete the constant** |
| N-F critic rubric | `copy_gen._HUMANNESS_CRITIC_RUBRIC` (`copy_gen.py:1025-1044`) item 14 | nothing |

`copy_gen._DESTINATION_CONSTRAINTS` (`copy_gen.py:829-848`) is **dead data today** — set on
`CopyRequest.destination_constraints`, serialized in `to_yaml_dict()` (`copy_gen.py:128`), read by
nobody. W8-11 deletes the dict and derives that field from `contract.constraints().caps`, so the
persisted brief stays informative *and* the numbers are the enforced ones. This is where the
never-applied 12-word headline cap becomes live.

**Self-check fields are not trusted.** `FINDINGS_SYNTHESIS.md` §4 item 4 proposes json_schema-typed
responses; **that is a scope cut** — `llm.py` supports only `response_format: {"type": "json_object"}`
plus a prose `schema_hint` (`llm.py:444`, live-verified against OpenRouter). Instead the model fills
`self_check` word counts, which are **discarded after `validate_against_contract` independently
recomputes them**. A model-reported count is a prompt-adherence signal for the trace, never an input to
a gate.

---

## 4. Load-time consistency check — the run refuses to start on contradiction

```python
def check_contract_consistency(
    *, generation: GenerationConfig, style_guide: dict[str, Any], destinations: Sequence[str]
) -> None:   # raises config_load.ConfigError
```

Called from `stages.stage_theme_load` (`stages.py:137-166`), right after
`load_theme_generation_config` and `load_style_guide`, before any collection. Fail-closed: any two
config sources disagreeing about the same number is a `ConfigError`, and the run stops with the
existing config exit class. It never "picks a winner".

Checks (each names both sources in the error message):

1. **Slide count.** `style_guide.platforms.<dest>.copy.carousel.slides` range must contain
   `generation.render_contract.<dest>.max_generated_slides`, and the range's low end must equal that
   value for a fixed-slot destination. *(`copy_gen.MIN_CAROUSEL_SLIDES` is deleted in Wave III; until
   then the check also compares against it.)*
2. **No word caps outside the contract.** A **structural key check**, not a regex over prose: no key
   matching `*_word*` / `*_words` may appear anywhere under `platforms.*.copy.*` in `style_guide.yaml`
   except the whitelist `{caption_word_count, word_count}` (both caption-level, owned by
   `CaptionRules`). `style_guide.yaml:91-93`'s `body_slide_template` prose is removed by the same wave,
   and the check prevents it growing back in a new key.
3. **Disclosure literal.** `style_guide.brand.disclosure_line` == `copy_gen.AI_DISCLOSURE_LINE`
   (`copy_gen.py:59`) == the literal `claim_gate._has_disclosure` checks.
4. **Aspect ratio.** Every destination in `generation.destinations` — **including disabled ones** —
   has an entry in `generation.media.aspect_ratio_by_destination`. *Operator decision (PLAN §13.4):
   `tiktok` stays configured with `"9:16"` but is excluded from `generation.destinations_enabled`
   (new key, read at contract resolution) — no tiktok asset is planned or spent on until the flag
   flips. The check validates disabled destinations' config coherence too.*
5. **Archetype→register binding.** Every `visual_archetypes[*]` entry in `style_guide.yaml` has a
   `register` key naming a key of `visual_registers`; every `style_systems[*]` names an existing
   register, archetype and `promptcraft.GENERATION_MODES` key; every `GENERATION_MODES[*].register` is
   a known register.
6. **Media + QA budget feasibility — RECOMPUTED under the flip.** Every slot is a paid canonical
   render now, so the denominator is no longer "slots whose ground diffuses":
   `paid_images = slots_total × ATTEMPT_MAX + expected_fallback_grounds` ≤
   `generation.media.per_run_count_cap`; and
   `slots_total × ATTEMPT_MAX + expected_repair_reqa + expected_adoptions` ≤
   `generation.llm.qa_reserved_calls`, where `expected_adoptions` is the count of unresolved
   prior-version intents the run may adopt (`store.unresolved_media_intents`). *At the ratified
   defaults — 8 assets, worst case 20 slots — that is 42 and 42 (`PLAN.md` §9.3), against the old
   `per_run_count_cap: 14` / `qa_reserved_calls: 16` which would both trip immediately.* Compositing
   no longer relieves the media cap (it is reached only after two paid renders), which is precisely
   why both numbers had to be re-derived rather than scaled.
7. **Compositing readiness.** If `render.compositing_enabled`: the font file named by
   `generation.media.compositing.font_path` exists, Pillow imports, its layout engine matches the
   pinned one (`COMPOSITING_SPEC.md` §8), and every `style_systems[*].slots[*].zones` block loads and
   validates. Missing → `ConfigError` at load, never a mid-run surprise.
8. **LLM call-budget feasibility — the ONE merged formula (R29; `MULTI_MODEL_SPEC.md` §12.7 defers
   to this check, it does not restate it).**
   `per_run_call_cap ≥ estimated non-QA calls + llm.qa_reserved_calls + test_render.qa_reserved_calls`,
   where the estimate is `N-A(1) + N-C(authored assets × 2 for the corrective retry) +
   N-F(authored assets) + N-D(assets with ≥1 `llm_crafted` slot, × 2 for the feedback retry) + 1
   headroom`, and the **third term counts only while `test_render.enabled` is true**. At the ratified
   defaults: `33 + 42 + 0 = 75` ⇒ `per_run_call_cap: 80`; flipping the test track on makes it
   `33 + 42 + 40 = 115` ⇒ 120, and **the run refuses at load time** if the cap was not raised in the
   same edit. *(Authored assets are 7 of 8 — `brand_promo` copy is config, not authored.)* A failure
   means raising `per_run_call_cap`/`per_run_usd_cap`, never weakening the check.
9. **Version agreement.** `generation.render_contract.contract_version` ==
   `render_contract.CONTRACT_VERSION` == `media_gen.PROMPT_PATTERN_VERSION`. A config edited without a
   code bump (or vice-versa) refuses to run.
10. **Style-system role coverage** (review blocker B2). Every `style_systems[*].slots` role set equals
    its destination's role sequence — for **both** format shapes now (`single`: `[cover]` /
    `[hero]`; `carousel`: the five-role sequence), since the format is chosen per asset.
11. **Hard-DON'T exemption hygiene (ROUND-4/5, `PLAN.md` §13 item 20 / invariant BP1).** Only a
    system whose `format_class` is `brand_promo` may carry `hard_dont_exemptions` for
    `STYLE_SYSTEMS_SPEC.md` §5.7/§5.8/§5.9/§5.10, and only `concept_dashboard` may carry §5.6. No
    system, ever, may claim an exemption for §5.1–§5.5 or §5.11 — those are integrity rules, not
    ad-aesthetic ones. An organic system claiming any anti-ad exemption is a `ConfigError` naming the
    system and the rule.

---

## 5. Single source per number

| Number | Single source after W8-11 | Everything else reads it via |
|---|---|---|
| slide body max words | `generation.render_contract.<dest>.slots[*].max_body_words` | `caps["slide_body_max_words"]` |
| prompt-quote max words | `generation.render_contract.<dest>.slots[*]` (prompt_quote role) | `caps["prompt_quote_max_words"]` |
| headline max words | `generation.render_contract.<dest>.headline_max_words` | `caps["headline_max_words"]` |
| caption length | `style_guide.platforms.<dest>.copy.caption_word_count` | `CaptionRules` |
| slide count | `generation.render_contract.<dest>.max_generated_slides` | `len(contract.slots)` |
| disclosure line | `style_guide.brand.disclosure_line` | `CaptionRules.disclosure_literal` |
| aspect ratio | `generation.media.aspect_ratio_by_destination` | `VisualPolicy.aspect_ratio` |
| register | `promptcraft.GENERATION_MODES[mode].register` | `VisualPolicy.register` |
| layout geometry | `style_guide.style_systems.*.slots.*.zones` | `compositing.layout` loader |
| contract/prompt version | `render_contract.CONTRACT_VERSION` | `PROMPT_PATTERN_VERSION`, YAML, resume guard |

Delete on sight: `promptcraft.MAX_BODY_WORDS` (:664), `copy_gen._DESTINATION_CONSTRAINTS` (:829-848),
`copy_gen.MIN_CAROUSEL_SLIDES` (:295), the words-per-slide prose in `style_guide.yaml:91-93`.

---

## 6. `GovernedPrompt` — invariant I1, the single submission choke point

The D1 defect is that two authorities could produce a submittable prompt string, and the ungoverned one
won whenever the governed one failed. W8-11 makes "a string that may be submitted" a **type** that
cannot be constructed without passing the gate.

```python
class UngovernedSubmission(RuntimeError):
    """A GovernedPrompt was constructed without a passing gate verdict.
    Programmer error (CODING_GUIDELINES §11) — never caught, never retried."""

@dataclass(frozen=True)
class GovernedPrompt:
    text: str                       # the exact bytes handed to the provider
    contract_sha256: str
    asset_id: str
    slot_index: int
    on_image_text: tuple[str, ...]  # the gated spans this prompt is allowed to render
    gate_verdict: str               # always "pass" — see __post_init__
    prompt_sha256: str

    def __post_init__(self) -> None:
        if self.gate_verdict != "pass":
            raise UngovernedSubmission(f"{self.asset_id}#{self.slot_index}")


def govern(
    *, text: str, contract: RenderContract, slot: Slot,
    snapshot: ClaimSnapshot, hard_excludes: Mapping[str, ResolvedList],
) -> GovernedPrompt | GovernFailure
```

`govern()` runs, in this order, returning `GovernFailure(reason, spans)` on the first failure:

1. **Text-set closure** (invariant I3). Every `<<…>>` span in `text` must be an exact member of
   `slot.on_image_text.spans()`. A span the copywriter never wrote and the gate never saw cannot be
   rendered. `render_contract` defines its own `QUOTED_SPAN_RE`; `promptcraft` adopts it in Wave II
   (it owns `promptcraft.py:668`, where the current copy lives) and `media_gen`'s unaccounted twin at
   `media_gen.py:818` is deleted in Wave I. One pattern, one place.
2. **Claim gate on exact submitted bytes** (invariant I2). `claim_gate.run_claim_gate(headline=…,
   caption="", image_brief=text, snapshot=…, hard_excludes=…, slides=None)`. Not on the copy, not on a
   preview — on `text` itself. `snapshot` is a **required** parameter with no default: a missing
   brand-truth panel is a fail-closed trigger, not a skip (this is the `stages.py:850-851` deletion).
   **Scope note:** the gate sees the whole prompt including the STYLE section, which legitimately
   carries numerals (margin percentages, hex-adjacent tokens). `promptcraft._build_style_section`
   already spells margins as "N percent" rather than "N%" to avoid tripping the number-claim regex
   (`promptcraft.py:371-375`). That work-around is preserved and pinned by
   `test_render_contract.py::test_style_block_numerals_do_not_trip_the_gate`. The STYLE section is
   **not** excluded from the gated bytes — excluding any region would reintroduce an ungoverned
   surface.
3. **Deterministic leak check.** `deterministic_prompt_leak_check` **moves from `media_gen.py:851-864`
   into `render_contract.py`** and runs inside `govern()`, so no caller can forget it. `media_gen`
   imports it back (import direction `media_gen → render_contract`; the reverse edge would be a cycle).
   `deterministic_qa_text_leak_check` (`media_gen.py:867-876`) stays in `media_gen` — it is a
   post-QA concern with no submission role.
4. **Register/mode coherence.** `text`'s STYLE section must not contain a leak pattern belonging to a
   register other than `contract.visual.register` — the register-keyed generalisation of
   `promptcraft._EDITORIAL_LEAK_RE` (`promptcraft.py:679`), table in `STYLE_SYSTEMS_SPEC.md` §6.

Enforcement of the choke point:

- `media_gen.KieClient.create_task` keeps its `prompt: str` signature (it is a transport), but
  `MediaGenerator._submit_new` (`media_gen.py:1465-1524`) takes a `GovernedPrompt` and passes
  `governed.text`. There is exactly one `create_task` call site (`media_gen.py:1493`), reachable only
  from `_submit_new`. The guard test is an AST scan asserting that the `prompt` argument at that call
  site **derives from a `GovernedPrompt` attribute** — a bare-name existence check would pass a
  regression that reintroduced a raw string.
- `MediaGenerator.__init__` gains **required** `claim_snapshot` and `hard_excludes` parameters. A
  `MediaGenerator` that cannot gate cannot be constructed. `stages.stage_media` passes
  `ctx.extra["brand_truth_panel"].snapshot` — `resume_state.ResumeState.brand_truth_panel` already
  round-trips (`resume_state.py:55-71`, `:200-223`), so `--resume` is safe.
- `media_gen.compose_prompt` (`media_gen.py:229-241`) and `media_gen._NEGATIVE_CONSTRAINTS`
  (`media_gen.py:113-117`) are **deleted**. The negative constraints already exist as
  `promptcraft.GUARDRAILS` (`promptcraft.py:85-89`) and stay there — one thing, one place.

### Claim-gate qualification co-location

`claim_gate.py:189-190` builds `combined_text = " ".join(fields.values())` once, outside the per-field
loop, and `_kvalifikovat_satisfied` (`:141-145`) then accepts a qualification marker found *anywhere*
in the asset. W8-11 changes `_kvalifikovat_satisfied` to take the **sentence containing the number**
(split the field on `[.!?\n]`, take the span holding the matched digits) instead of `combined_text`.

This is a **behaviour change to the gate**, owned by its own task (`claim_gate.py` is otherwise
untouched by this plan) and named in the doc amendment: copy that passed the gate before may now be
blocked. That is the intent — the fa51 `35,095` shipped because "reported" sat three slides away. There
is **no feature flag**: a flag here would leave the weak path reachable, and rollback is a one-file
`git revert`. Regression test pins the fa51 case exactly.
Territory invariants for that task: the claim lexicons, `run_claim_gate`'s signature and the
`abstain`-behaviour path are load-bearing and unchanged.

---

## 7. Config surface added (`config/themes/hypedigitaly.yaml`)

**ROUND-4/5 surface (amended — this block supersedes the round-2 one).** Per-slot
`text_render_mode`/`ground_source` are **not** here (blocker B2 — they resolve from the style system
only); each destination declares **both format shapes**, and the run picks one per asset.

```yaml
generation:
  render_contract:
    contract_version: 3            # == render_contract.CONTRACT_VERSION; bumps to 4 at Wave IV (§8)
    persona:
      mode: institutional          # institutional | none  (never a named individual — W8-11 locked)
      speaker_name: HypeDigitaly
    canonical_render_enabled: true # the flip (PLAN §13 item 19.A); false => composited rung for
                                   #   every slot, which is the pre-flip behaviour
    text_qa_retry_max: 1
    fallback_to_composite: true
    compositing:
      compositing_enabled: true    # NOT a temporary flag any more: this is the fallback renderer
      # composited_roles / diffusion_text_max_* deleted — see §2
    linkedin:
      headline_max_words: 12
      hashtag_max_count: 3
      formats:
        single:                    # LinkedIn has one shape today
          max_generated_slides: 1
          slots:
            - {role: hero, max_title_words: 12, max_body_words: 18}
    instagram_feed:
      headline_max_words: 12
      hashtag_max_count: 5
      default_format: single       # carousel requires evidence — STYLE_SYSTEMS_SPEC §4.1
      formats:
        single:
          max_generated_slides: 1
          slots:
            - {role: cover, max_title_words: 10, max_body_words: 18}
        carousel:
          max_generated_slides: 5  # cover + 3 body + end card (locked decision 2)
          slots:
            - {role: cover,        max_title_words: 10, max_body_words: null}
            - {role: body,         max_title_words: 8,  max_body_words: 24}
            - {role: prompt_quote, max_title_words: 8,  max_body_words: null,
               exempt_from_word_cap: true, prompt_quote_max_words: 50}
            - {role: body,         max_title_words: 8,  max_body_words: 24}
            - {role: end_card,     max_title_words: 8,  max_body_words: 12}
  batch_composition:               # PLAN §13 item 25 — ONE block for the whole run shape
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
  media:
    require_visual_evidence: true            # locked decision 4 — absent evidence blocks generation
    per_run_count_cap: 42                    # was 14 — 20 slots x ATTEMPT_MAX 2 + 2 fallback grounds
    per_run_usd_cap: 3.00                    # unchanged; worst case inside the count cap is $1.26
    per_day_usd_cap: 6.00                    # operator-confirmed unchanged (PLAN §13 item 22.4)
    compositing:
      font_path: assets/fonts/Montserrat-Variable.ttf
      renderer: pillow
  llm:
    qa_reserved_calls: 42                    # was 16 — every canonical render carries text, §4 check 6
    per_run_call_cap: 80                     # merged check 8: 33 + 42 + 0
    per_run_usd_cap: 4.00                    # ~26 authoring calls + up to 42 vision-QA calls
    node_overrides:
      copywriter:       {max_tokens: 8000, temperature: 0.9}
      prompt_crafter:   {max_tokens: 6000, per_slide_tokens: 1200}
      humanness_critic: {max_tokens: 4000, per_slide_tokens: 400}
```

`per_slide_tokens` is new: `llm.LlmClient.call_json` gains an optional `slide_count` argument and
resolves `max_tokens = override.max_tokens + slide_count × override.per_slide_tokens`
(resolution site `llm.py:341-352`; `LlmNodeOverride` is defined at `config_load.py:427-436`). For N-D
the count passed is that asset's **`llm_crafted` slot count**, **not** `len(contract.slots)` — under
the flip N-D is called only for scene/illustration slots (about 5 assets per run at the ratified
defaults), while every recipe-determined card gets a deterministic template prompt and no N-D call. `humanness_critic` currently has
**no** `node_overrides` entry and silently inherits `default_max_tokens`, which is why N-F failed on
2/6 fa51 assets and shipped the originals unreviewed (`copy_gen.py:975`).

`GenerationConfig` is the frozen dataclass at `config_load.py:537-553`; its loader (optional keys with
safe defaults throughout) is `load_theme_generation_config` at `config_load.py:556-651`. Every new key
above follows that idiom, so a theme predating W8-11 still loads.

---

## 8. Version identity, resume and migration

**One constant, one bump.**

- `render_contract.CONTRACT_VERSION` is the single source. `media_gen.PROMPT_PATTERN_VERSION`
  (`media_gen.py:91`) becomes `PROMPT_PATTERN_VERSION = CONTRACT_VERSION` — an alias for call-site
  stability, never an independently-edited literal. Every guard (resume, `media_prompts.yaml`,
  consistency check 9) compares against the **constant**, never a literal `4`.
- **Bump policy: exactly once, at Wave IV** — the last wave that changes prompt bytes. Waves I-III run
  on `CONTRACT_VERSION = 3`, i.e. **v3 ledger identity semantics stay in force during the interim**.
  This is deliberate: bumping early would strand in-flight W8-10 spend behind a version wall three
  times over. What protects the interim is bullet 4 below, not the version number.

**Four ledger/resume guards.**

1. **Prior-version adoption is quarantined.** Phase-0 `_resolve_one_row` (`media_gen.py:1137-1172`)
   currently adopts any unresolved row and synthesises `qa.status = "skipped"`
   (`media_gen.py:1616-1620`) — which would import ungoverned W8-10 images straight into a W8-11 pack.
   Full rule and the `adopted_prior_version/` destination: `SLOT_MODEL_SPEC.md` §7.
2. **`media_prompts.yaml`** (`promptcraft.MEDIA_PROMPTS_FILENAME`, :71) gains a header
   `contract_version` + `contract_sha256` and per-slot `{slot_index, slot_state, repairs_used,
   contract_sha256, prompt_sha256}`. `load_media_prompts` (`promptcraft.py:266-279`) returns `{}` when
   the header mismatches the current contract — a resumed run re-crafts rather than mixing schemes.
   Today it returns `{}` only on a malformed file, so a structurally-valid W8-10 document would load
   with silently-missing fields. **All delivered slots of one asset must share one
   `contract_sha256`**; a mixed asset is `held_incomplete`, never shipped.
3. **`resume_state.yaml`** has **no version field of any kind** (`resume_state.py:55-71`) and
   `load_resume_state` reconstructs with `.get(...)` defaults, so a W8-10 file loads silently. It gains,
   all following the `viral_playbook_path` precedent (`resume_state.py:231-247` — new field, safe
   default, explicit `to_dict`/`from_dict`):
   - `contract_version: int = 0` — `resume_pipeline` refuses (policy-stop, explicit operator message)
     when it != `CONTRACT_VERSION`.
   - `visual_policies: dict[str, VisualPolicy]` and `contract_sha256s: dict[str, str]`, keyed by
     `asset_id`. **`stage_analysis` is not in `RESUME_STAGE_NAMES`** (`stages.py:1050` — resume runs
     copy/media/packaging/digest only), so without this a resumed run either re-derives a different
     `VisualPolicy` (contract sha drifts → every asset re-crafts → straight into guard 4) or finds no
     evidence at all and blocks every image. On resume `stage_copy` **reads** the persisted policy and
     never re-derives it; a sha mismatch is a policy-stop.
4. **Ledger identity ignores prompt bytes — so compare them.** The UNIQUE key is
   `(theme, run_date, cluster_key, asset_slot, language, prompt_pattern_version, attempt)`
   (`store.py:182`). A re-crafted slot inside the same run/day therefore *hits the existing row* and
   ships the **stale image** for the new copy. Fix, in `_submit_or_resolve`'s existing-row branch
   (`media_gen.py:1286-1291`): compare `existing.prompt_sha256` with the current
   `GovernedPrompt.prompt_sha256`; on mismatch → **fail closed**, `BLOCKED_NO_IMAGE` + a
   `trace.decision` naming "identity exhausted for this slot, no re-submission", and the asset closes
   `copy_only`. **Do not widen the UNIQUE key** — that would silently authorise unbounded re-spend per
   slot. Test: `test_ledger_hit_with_changed_prompt_blocks_instead_of_reusing`.

**Store migration.** `store.normalized_signals` gains `first_seen_at` (Wave IV) via the existing
hand-written additive idiom in `Store._migrate_schema` (`store.py:453-460`) — `PRAGMA table_info` then
`ALTER TABLE … ADD COLUMN`. A `schema_version` table is added alongside for bookkeeping, but
**`PRAGMA table_info` remains the schema-truth mechanism**: the version row records intent, the PRAGMA
check is what actually decides whether a column exists, so a hand-edited or partially-migrated DB
cannot lie to the engine.

---

## 9. Invariants owned by this spec

| ID | Statement | Enforced at | Test |
|---|---|---|---|
| **I1** | Every byte submitted to the provider comes from a `GovernedPrompt`; exactly one `create_task` call site, and its `prompt` argument derives from a `GovernedPrompt` attribute. | type + signature + AST test | `test_render_contract.py::test_governed_prompt_rejects_failed_verdict`; `test_media_gen.py::test_single_create_task_call_site_takes_governed_prompt` |
| **I2** | The claim gate runs on the exact submitted bytes; a missing snapshot fails closed. | `govern()`, required `MediaGenerator` params | `test_media_gen.py::test_missing_snapshot_refuses_construction`; `::test_gate_blocked_number_never_reaches_provider` |
| **I3** | Every `<<…>>` span in a submitted prompt is a member of that slot's gated `on_image_text`. | `govern()` step 1 | `test_render_contract.py::test_text_set_closure_rejects_invented_span` |
| **I5** | No provenance-class change happens without a `trace.decision` event. | `stages`/`media_gen` call sites | `test_stages.py::test_substitution_emits_decision_event` |
| **RL1** | The render ladder is ordered: the composited rung is reachable only after two failing text verdicts, or from the `canonical_render_enabled: false` kill switch. | `asset_model.advance()` edge set | `test_asset_model.py::test_composite_fallback_is_unreachable_before_two_text_defects` |
| **RL2** | A canonically-rendered image is never delivered without a per-glyph text verification verdict against its gated spans; skipped is not pass. | `text_matches` in the never-skipped set | `test_media_gen.py::test_text_matches_never_skips_for_a_canonical_render` |
| **LANG1** | An asset's language is resolved server-side from `batch_composition.language_by_destination` — never model-chosen, never inferred from the copy. | contract resolution | `test_config.py::test_language_resolves_from_destination_config` |
| **BP1** | Only `brand_promo`-class systems may carry §5.6-§5.10 exemptions (only `concept_dashboard` may carry §5.6); §5.1-§5.5 and §5.11 bind for every system. | check 11 | `test_config.py::test_only_brand_promo_may_carry_anti_ad_exemptions` |
| **C1** | Two config sources may never disagree about the same number; the run refuses. | `check_contract_consistency` | `test_render_contract.py::test_slide_count_disagreement_raises_config_error` |
| **C2** | `ConstraintSet.caps` is the only source of any cap read by an author or a validator. | grep test | `test_render_contract.py::test_no_module_level_word_cap_constants` |
| **C3** | One version constant; no literal version numbers in guards. | `CONTRACT_VERSION` + check 9 | `test_render_contract.py::test_version_is_single_sourced` |
| **G1** | A STYLE section's own numerals never trip the claim gate. | "N percent" spelling, preserved | `test_render_contract.py::test_style_block_numerals_do_not_trip_the_gate` |
| **L1** | A ledger hit whose stored prompt sha differs from the current prompt blocks; it never re-uses the stale image. | `_submit_or_resolve` existing-row branch | `test_media_gen.py::test_ledger_hit_with_changed_prompt_blocks_instead_of_reusing` |

I4 (QA totality), the slot state machine and prior-version adoption are owned by `SLOT_MODEL_SPEC.md`.
