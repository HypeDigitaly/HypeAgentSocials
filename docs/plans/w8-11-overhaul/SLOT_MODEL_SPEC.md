# SLOT MODEL SPEC — W8-11

*Companion to `PLAN.md`. Specifies `engine/src/hypeagent/asset_model.py` (new), the per-slot state
machine that replaces today's implicit, path-dependent status handling, and the crafted-prompt shape
that carries it. Self-contained: an executor implements from this file plus `RENDER_CONTRACT_SPEC.md`.
Authored 2026-08-07; revised after the three-reviewer panel.*

Governing decisions: `FINDINGS_SYNTHESIS.md` §0 item 2 (true Instagram carousels, ~5 generated images
per asset, 1:1 slot→image, all-or-nothing delivery) and §3 (slot model, per-slot state machine,
deliverability derived from manifest state and never from file presence).

---

## 1. What is wrong today

| Symptom | Cause | Coordinates |
|---|---|---|
| A carousel is only ever generated if the LLM happened to return `slide_NN`-slotted images; the slide count is whatever came back | `MediaAssetPlan`s are *derived from the crafter's output*, not from the contract | `media_gen.py:684-704` — `slide_images = [img for img in crafted.images if img.slot.startswith("slide")]` |
| On-image text is invented by N-D from a free-text `image_brief` and never gated as copy | `image_brief: str` reaches the provider (`media_gen.py:229-241`, `:1479`) | D1 |
| One over-cap slide kills the whole carousel | `craft_prompts` returns `unavailable=True` for the entire set | `promptcraft.py:961-969` |
| A slide's on-image text is reconstructed from an untyped dict | `_slide_text(slide: dict[str, str])` reads `slide.get("title")`/`.get("body")` | `media_gen.py:650-653`, `:685` |
| `is_cover` is positional, not role-derived | `is_cover=(image.slot == "slide_01")` | `media_gen.py:702` |
| Deliverability is inferred from whichever branch ran | statuses assembled ad hoc in `_status_from_row` | `media_gen.py:1646-1684` |
| A crashed run's unresolved intents are adopted with `qa.status="skipped"`, regardless of which engine version produced them | `_resolve_one_row` passes `qa_runner=None` | `media_gen.py:1137-1172`, `:1616-1620` |
| Per-slot progress is not persisted, so a resumed run cannot tell a crafted slot from a submitted one | `CraftedImage` carries only `slot`/`prompt`/`relevance` | `promptcraft.py:170-179` |

---

## 2. `asset_model.py` — public API

Imports stdlib only. Every other module imports **from** it; it imports from nothing in `hypeagent`.

```python
class SlotRole(str, Enum):
    HERO         = "hero"          # single-image destination
    COVER        = "cover"         # carousel slide 1
    BODY         = "body"          # carousel body slide (checklist is a body pattern, not a role)
    PROMPT_QUOTE = "prompt_quote"  # monospace verbatim prompt — exempt from the body word cap
    END_CARD     = "end_card"      # follow/save CTA close

@dataclass(frozen=True)
class OnImageText:
    """The ONLY text a renderer may put on this slot's image. Claim-gated at
    authoring time; the closure set checked by render_contract.govern()."""
    title: str
    body: str | None = None
    kicker: str | None = None

    def spans(self) -> tuple[str, ...]: ...        # non-empty values, in render order

@dataclass(frozen=True)
class VisualIntent:
    """Replaces the free-text `image_brief`. Structurally incapable of being
    submitted: no `.text`, no `__str__`; govern() accepts only a str built by
    promptcraft from a contract + this object."""
    subject: str
    proof_element: str | None
    tools_named: tuple[str, ...]
    environment_hint: str | None

@dataclass(frozen=True)
class Slot:
    index: int                     # 1-based; matches SlotSpec.index
    role: SlotRole
    on_image_text: OnImageText
    visual_intent: VisualIntent
    exempt_from_word_cap: bool = False

    @property
    def is_cover(self) -> bool:    # role-derived, never positional
        return self.role in (SlotRole.COVER, SlotRole.HERO)

@dataclass(frozen=True)
class CopyAsset:
    asset_id: str
    cluster_key: str
    destination: str
    language: str
    caption: str                   # the platform caption — never rendered on an image
    headline: str
    slots: tuple[Slot, ...]
    contract_sha256: str

    def slot(self, index: int) -> Slot: ...
    def is_carousel(self) -> bool: return len(self.slots) > 1
    def to_yaml_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_yaml_dict(cls, doc: Mapping[str, Any]) -> "CopyAsset": ...
```

`image_brief: str` is **removed** from `CopyResult` (`copy_gen.py:143-155`) and from `MediaAssetPlan`
(`media_gen.py:613`). `VisualIntent` takes its place. The claim gate's `image_brief=` parameter keeps
its name (a positional contract with `claim_gate.run_claim_gate`, `claim_gate.py:162-269`) but is fed
the **rendered prompt bytes** at submission time and the joined `VisualIntent` fields at authoring
time — never a free-text scene description that later becomes a prompt.

---

## 3. The per-slot state machine

```python
class SlotState(str, Enum):
    PLANNED           = "planned"            # contract resolved, no text yet
    CRAFTED           = "crafted"            # N-D produced a RENDER section (or compositing needs none)
    REPAIRING         = "repairing"          # one bounded repair round in flight
    GOVERNED          = "governed"           # GovernedPrompt minted (closure+gate+leak+coherence)
    SUBMITTED         = "submitted"          # create_task returned a task id, or composite queued
    PENDING_EXTERNAL  = "pending_external"   # submitted, provider not yet terminal (poll continues)
    SUBMITTED_UNKNOWN = "submitted_unknown"  # submission ambiguous: money may have moved
    RENDERED          = "rendered"           # bytes on disk, checksummed
    QA_PASSED         = "qa_passed"
    QA_FAILED         = "qa_failed"
    DELIVERABLE       = "deliverable"        # terminal, ships
    REGEN             = "regen"              # QA fail, attempt budget remains
    HELD_QA           = "held_qa"            # terminal, held for operator
    BLOCKED_NO_IMAGE  = "blocked_no_image"   # terminal, asset ships copy-only
```

`PENDING_EXTERNAL` and `SUBMITTED_UNKNOWN` are not new *behaviour* — `media_gen` already distinguishes
these outcomes (`RecordInfoResult.is_terminal`, `submitted_unknown_subcase` on the ledger row,
`MediaStageResult.pending_count`/`submitted_unknown_count`). They are new *states*, so that a resumed
run reads the distinction from the manifest instead of re-deriving it, and so `asset_deliverability`
can tell "still running" from "money moved, outcome unknown".

### Transition table (the only legal moves)

| From | Event | To | Notes |
|---|---|---|---|
| PLANNED | `crafted` | CRAFTED | N-D returned a RENDER section for this slot index |
| PLANNED | `no_diffusion_surface` | CRAFTED | fully-programmatic slot: N-D is skipped entirely, the "prompt" is the composited render spec |
| PLANNED | `craft_failed` | BLOCKED_NO_IMAGE | crafter unavailable / no output for this slot |
| CRAFTED | `validated` | GOVERNED | `validate_crafted_prompt` + `govern()` both pass |
| CRAFTED | `validation_failed` (repairs_left > 0) | REPAIRING | verbatim reason fed back, exactly one round |
| CRAFTED | `validation_failed` (repairs_left == 0) | BLOCKED_NO_IMAGE | **never a fallback prompt** |
| REPAIRING | `crafted` | CRAFTED | re-enters validation with `repairs_left = 0` |
| REPAIRING | `craft_failed` | BLOCKED_NO_IMAGE | |
| GOVERNED | `qa_budget_unavailable` | BLOCKED_NO_IMAGE | reserve QA capacity **before** spending money |
| GOVERNED | `prompt_identity_exhausted` | BLOCKED_NO_IMAGE | ledger hit with a different `prompt_sha256` (`RENDER_CONTRACT_SPEC.md` §8 guard 4) |
| GOVERNED | `capped` | BLOCKED_NO_IMAGE | count/budget cap or circuit breaker |
| GOVERNED | `submitted` | SUBMITTED | the one `create_task` call site, or the compositor |
| SUBMITTED | `polling` | PENDING_EXTERNAL | provider accepted, not yet terminal |
| SUBMITTED | `ambiguous` | SUBMITTED_UNKNOWN | transport error after the request left; money may have moved |
| PENDING_EXTERNAL | `rendered` / `provider_failed` / `timeout` | RENDERED / BLOCKED_NO_IMAGE / SUBMITTED_UNKNOWN | |
| SUBMITTED_UNKNOWN | `resolved_success` / `resolved_failure` | RENDERED / BLOCKED_NO_IMAGE | phase-0 resolution on a later run |
| RENDERED | `qa_pass` | QA_PASSED | vision verdict, or `composite-verified` (`COMPOSITING_SPEC.md` §5) |
| RENDERED | `qa_fail` (attempt < ATTEMPT_MAX) | REGEN | |
| RENDERED | `qa_fail` (attempt == ATTEMPT_MAX) | HELD_QA | |
| RENDERED | `qa_budget_unavailable` | **HELD_QA** | budget died between reservation and verdict: the image exists and is paid for, so it is held for a human — never auto-passed, never silently deliverable |
| REGEN | `crafted` | CRAFTED | attempt 2, `repairs_left` reset to 0 |
| QA_PASSED | `asset_complete` | DELIVERABLE | only via the asset-level closure in §4 |

```python
TERMINAL = {SlotState.DELIVERABLE, SlotState.HELD_QA, SlotState.BLOCKED_NO_IMAGE}

def advance(state: SlotState, event: str, *, attempt: int, repairs_left: int) -> SlotState:
    """Pure. Raises InvalidTransition on any move not in the table above."""
```

**Every transition emits a `trace.decision` event** (`trace.py:308-310`), shape:
`trace.decision("media", decision=f"slot {asset_id}#{index} {from}->{to}: {reason}",
rule="W8-11 I5: no silent substitution")`. This is invariant I5, and it is what makes the fa51
gate-block→fallback substitution (which emitted nothing) impossible to repeat. Transitions emitted
from inside an `except` block use `trace.try_decision()` (see `PLAN.md` §9.4) so a failed trace write
cannot itself escalate.

**There is no `SKIPPED` state.** A skipped QA is not a pass — `RENDERED` without a QA verdict cannot
reach `DELIVERABLE`, which is invariant I4.

---

## 4. All-or-nothing, at DELIVERY not at CRAFT

The synthesis reconciles two rules that look contradictory:

- **At CRAFT time:** granularity is per-slot. One slot failing validation repairs or blocks *by
  itself*; the sibling slots continue. This replaces `promptcraft.py:961-969`, which returned
  `unavailable=True` for the whole set and cost fa51 all three carousels.
- **At DELIVERY time:** the asset is atomic:

```python
def asset_deliverability(states: Sequence[SlotState], shas: Sequence[str], contract: RenderContract) -> str:
    """"deliverable"      — every REQUIRED slot is QA_PASSED and all shas are identical
        "copy_only"        — any required slot is BLOCKED_NO_IMAGE (asset ships caption+copy, no images)
        "held"             — any required slot is HELD_QA (operator decides)
        "held_incomplete"  — any required slot is SUBMITTED_UNKNOWN, or the delivered slots do not
                             all share one contract_sha256 (a mixed-contract carousel)
        "in_progress"      — anything else non-terminal remains"""
```

A partially-generated carousel is **never** published as a shorter carousel and never silently
downgraded to a hero. `copy_only`, `held` and `held_incomplete` all carry the verbatim blocking reason
into the digest (`packaging.write_digest`) so the operator sees *why*, which fa51 did not provide.

Deliverability is computed from the slot states held in the media manifest / ledger rows — **never from
`image_path` existing on disk**. `media_gen._status_from_row` (`media_gen.py:1646-1684`) becomes a pure
mapping from `MediaIntentRow.state` → `SlotState`, and `packaging` reads states, not the filesystem.

**Carousels are generated sequentially.** Each slot is a submit-then-poll cycle
(`_poll_to_resolution`, `media_gen.py:1526-1573`, `poll_interval_seconds: 7`,
`poll_timeout_seconds: 180`), and the engine is deliberately single-threaded. Eighteen slots is
therefore roughly **5× the wall-clock of fa51's four submissions** — minutes, not hours, and entirely
acceptable for a nightly batch. Sequential execution is also what makes the money model simple: the
per-day spend read at `media_gen.py:1318` is safe precisely because `run_identity.RunLock` guarantees
one run at a time (a one-line comment at that read must say so, so a future concurrency change cannot
silently invalidate it). Do not parallelise slot submission without revisiting the cap arithmetic.

---

## 5. `MediaAssetPlan` is derived 1:1 from `Slot`, never invented

`plan_media_assets` (`media_gen.py:656-718`) is rewritten to:

```python
def plan_media_assets(
    assets: Sequence[CopyAsset], *, contracts: Mapping[str, RenderContract],
    crafted: Mapping[str, CraftedPromptSet],
) -> list[MediaAssetPlan]
```

Rules:

1. One `MediaAssetPlan` per `Slot` in `CopyAsset.slots`. The count comes from `len(contract.slots)`;
   it is **not** read off the crafter's output. A crafter returning fewer images than slots leaves the
   missing slots at `BLOCKED_NO_IMAGE` (each with its own decision event), and the asset closes as
   `copy_only`.
2. `MediaAssetPlan` field changes:
   - `image_brief: str | None` → **deleted**.
   - `crafted_prompt: str | None` → `governed: GovernedPrompt | None`.
   - `qa_expected_text: str | None` → `on_image_text: OnImageText` (never `None`; an empty
     `OnImageText` means "this slot renders no text", a *fact about the slot*, not a signal to skip QA).
   - add `slot_index: int`, `role: SlotRole`, `text_render_mode: str`, `ground_source: str`,
     `style_system: str`.
   - `is_cover` becomes a read-only property delegating to `Slot.is_cover`.
   - `asset_slot` keeps its exact current format (`destination` for hero, `f"{destination}:{slot}"`
     otherwise, `media_gen.py:641-647`) — it is a component of the ledger UNIQUE key (`store.py:182`)
     and its shape must not drift.
3. `slot` string stays `"hero"` / `"slide_01"`… for ledger compatibility; `slot_index` is the typed
   handle used in code.

### 5.1 The crafted-prompt shape (pinned here, authored with the shared types)

`promptcraft.CraftedImage` (`promptcraft.py:170-179`) and `CraftedPromptSet` (`:182-234`) are the
hand-off between N-D and the media stage. Their W8-11 shape is fixed **in the shared-types task**, so
the copy-side and media-side tasks can be built in parallel against a frozen contract:

```python
@dataclass(frozen=True)
class CraftedImagePrompt:
    slot: str                       # "hero" | "slide_01" | …  (ledger-facing, unchanged)
    slot_index: int                 # typed handle, 1-based
    role: SlotRole
    prompt: str | None              # None for a fully-programmatic slot (N-D skipped)
    relevance: str | None
    contract_sha256: str
    prompt_sha256: str | None       # None when prompt is None
    state: SlotState                # per-slot progress, persisted
    reason: str | None              # verbatim failure/repair reason when state is a failure state
    repairs_used: int = 0

@dataclass(frozen=True)
class CraftedPromptSet:
    asset_id: str
    contract_version: int           # == render_contract.CONTRACT_VERSION
    contract_sha256: str
    images: tuple[CraftedImagePrompt, ...]
    archetype: str | None
    register: str
    mode: str | None
    style_system: str
    series_token: str
    # `unavailable` / `unavailable_reason` / `gate_blocked` / `gate_failing_spans` are REMOVED:
    # failure is now per-slot (`CraftedImagePrompt.state` + `.reason`), never set-wide.
    def usable_slots(self) -> tuple[CraftedImagePrompt, ...]: ...
```

`hero_prompt()` and `usable()` (`promptcraft.py:208-220`) are deleted — both encode the
one-image-per-asset assumption this wave removes.

---

## 6. Where the slots come from — N-C authors exactly what will be generated

`copy_gen` changes shape, not responsibility:

- `CopyRequest` gains `contract: RenderContract`. The N-C prompt states the slot plan explicitly —
  role, index, per-slot caps — from `contract.constraints().as_prompt_block()`. The copywriter is told
  "you are writing 5 slides: a cover, three body slides (one of which is a verbatim prompt card), and
  an end card", which is the fix for `max_generated_slides` living in destination policy
  (`FINDINGS_SYNTHESIS.md` §3).
- `CopyResult.slides: list[dict] | None` → `CopyResult.slots: tuple[Slot, ...]`. The parser
  (`_parse_openrouter_response`, `copy_gen.py:660-687`) maps the JSON array to `Slot`s by index and
  assigns `role` from `contract.slots[i].role` — the model does **not** choose roles.
- `AssetCopyStatus` (`copy_gen.py:897-911`) replaces `slides`/`image_brief`/`headline` with a single
  `asset: CopyAsset | None`. `status`/`attempt`/`failing_spans`/`request_path` are unchanged.
- Validation (`_carousel_deficiency`, `copy_gen.py:588-601`; `MIN_CAROUSEL_SLIDES`, `:295`) is replaced
  by a contract check: slot count, roles present, per-slot word caps with `exempt_from_word_cap`
  honoured for `PROMPT_QUOTE` **and `prompt_quote_max_words` still enforced**
  (`RENDER_CONTRACT_SPEC.md` §3). **`MIN_CAROUSEL_SLIDES` is deleted.**
- The numbered-promise gate (`copy_gen.py:618-657`) stays, but `_content_slide_count` counts
  `SlotRole.BODY` + `SlotRole.PROMPT_QUOTE` slots rather than guessing from a dict list.

`on_image_text` becomes **first-class gated copy**: it is inside `CopyAsset`, so
`run_claim_gate(..., slides=[slot.on_image_text.to_dict() for slot in asset.slots])` covers it at
authoring, with the existing repair loop (`process_copy_asset`, `copy_gen.py:1156-1248`). A number that
fails the gate is repaired or the asset is held **before** any prompt exists — the fa51 `35,095` path
is closed at both ends.

---

## 7. Persistence, resume and prior-version adoption

### 7.1 Artefacts

| Artefact | Change | Compatibility |
|---|---|---|
| `copy_responses/*.yaml` | slots array replaces slides array; `visual_intent` object replaces `image_brief` string | `process_summary._find_image_brief` (`:901-916`) and `_reconstruct_prompt` (`:919-971`) are **deleted** — they exist only to re-compose the deleted fallback. Replaced by a read of the actually-submitted bytes (`prompt_full`) from the slot provenance YAML |
| `media_prompts.yaml` | header `contract_version` + `contract_sha256`; per-slot `{slot_index, slot_state, repairs_used, contract_sha256, prompt_sha256}` | `load_media_prompts` returns `{}` on header mismatch → re-craft (`RENDER_CONTRACT_SPEC.md` §8) |
| `resume_state.yaml` | `contract_version`, `visual_policies`, `contract_sha256s` (all with safe defaults, `viral_playbook_path` precedent at `resume_state.py:231-247`) | old file loads, then is **rejected with a clear operator message**, never silently mixed |
| `media_intents` rows | schema unchanged | prompt-sha guard (`RENDER_CONTRACT_SPEC.md` §8 guard 4) covers same-version re-crafts; phase-0 quarantine covers cross-version rows |
| `<slot>.provenance.yaml` | add `slot_role`, `slot_index`, `style_system`, `text_render_mode`, `ground_source`, `contract_sha256`, `slot_state`; `qa.status` may be `composite-verified`; `compositing.pillow_version` when composited | additive; `_write_provenance_yaml` (`media_gen.py:1697-1758`) |

`process_summary.py` must degrade gracefully on pre-W8-11 runs (`--summarize <old_run_id>`): a missing
`slots` key prints the old `slides` shape with an explicit "not recorded by this engine version" line,
per `RUN_TRACE_SPEC.md` §6. A crash there must never change a run's exit class (`DECISION_LOG.md` W8-8).

### 7.2 Prior-version adoption must never enter the pack

Phase-0 `_resolve_one_row` (`media_gen.py:1137-1172`) resolves any unresolved ledger row and, having no
plan context, synthesises `qa.status = "skipped"` (`media_gen.py:1616-1620`) and writes the image into
`pack_media_dir`. Left alone, the **first W8-11 run would import ungoverned W8-10 images — the exact
fa51 defects — straight into a W8-11 pack, unreviewed.** Note this is *not* solved by the version bump:
`CONTRACT_VERSION` stays 3 through waves I-III (`RENDER_CONTRACT_SPEC.md` §8), so a W8-10 row is
version-identical during the interim.

`_resolve_one_row` gains an ordered branch set, evaluated **before** any provider lookup:

1. `row.route_id == "composite-local"` → re-render deterministically, locally, free
   (`COMPOSITING_SPEC.md` §6). Never a provider call, never `submitted_unknown`.
2. Otherwise, the row is **quarantined** if any of:
   - `row.prompt_pattern_version != CONTRACT_VERSION`, **or**
   - the row's `asset_slot` is not among this run's planned slots (no plan context — today's
     `qa_runner=None` case), **or**
   - the row's `prompt_sha256` differs from this run's `GovernedPrompt` for that slot.
3. Quarantine behaviour: **settle the money exactly as today** — resolve the task, record
   `observed_cost_usd`, mark the row terminal, leave spend reconciliation untouched (abandoning the row
   would break the sum==ledger==balance invariant) — but download the bytes to
   `logs/runs/<run_id>/adopted_prior_version/` and **never** into `pack_media_dir`, write **no pack
   provenance**, and emit a `trace.decision` naming the rule. The image is evidence and an audit trail,
   not a deliverable.

Test: `test_prior_version_adoption_never_writes_into_pack`.

**Deployment runbook (also in `PLAN.md` §9.5):** complete or abandon all in-flight W8-10 runs before
deploying Wave I. Any intent abandoned mid-flight settles at the next W8-11 phase 0 into
`adopted_prior_version/` — money reconciled, nothing shipped.

---

## 8. Invariants owned by this spec

| ID | Statement | Enforced at | Test |
|---|---|---|---|
| **I4** | A delivered image always carries a QA verdict; `skipped` is never a pass. Text-conditional booleans may skip individually; subject / logo / composition / gibberish never skip. | no RENDERED→DELIVERABLE edge; per-boolean skip | `test_media_gen.py::test_rendered_without_qa_never_deliverable`; `::test_qa_text_booleans_skip_individually` |
| **S1** | Slot count equals `len(contract.slots)`; a plan is never derived from crafter output. | `plan_media_assets` signature | `test_media_gen.py::test_plan_count_matches_contract_not_crafter` |
| **S2** | All-or-nothing at delivery: no partial carousel ships. | `asset_deliverability` | `test_asset_model.py::test_partial_carousel_is_copy_only` |
| **S3** | Every state transition is legal and traced. | `advance()` raises `InvalidTransition` | `test_asset_model.py::test_illegal_transition_raises`; `test_stages.py::test_every_slot_transition_emits_decision` |
| **S4** | `is_cover` is role-derived. | property on `Slot` | `test_asset_model.py::test_is_cover_is_role_derived` |
| **S5** | `VisualIntent` can never be submitted as a prompt. | no `__str__`/`.text`; `govern()` takes a str built by promptcraft | `test_render_contract.py::test_visual_intent_is_not_submittable` |
| **S6** | All delivered slots of one asset share one `contract_sha256`. | `asset_deliverability` → `held_incomplete` | `test_asset_model.py::test_mixed_contract_carousel_is_held_incomplete` |
| **S7** | A prior-version or out-of-plan intent settles its money but never enters the pack. | `_resolve_one_row` quarantine | `test_media_gen.py::test_prior_version_adoption_never_writes_into_pack` |
| **S8** | A paid, rendered image whose QA budget vanished is held, never auto-delivered. | RENDERED `qa_budget_unavailable` → HELD_QA | `test_media_gen.py::test_rendered_without_qa_budget_is_held_not_delivered` |
