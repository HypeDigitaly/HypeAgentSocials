# COMPOSITING SPEC — W8-11

*Companion to `RENDER_CONTRACT_SPEC.md` and `FINDINGS_SYNTHESIS.md` §0 item 5 / §5. Self-contained: an
executor implements `engine/src/hypeagent/compositing/` from this file alone. Authored 2026-08-07 from a
full read of `media_gen.py`, `config/style_guide.yaml`, `assets/`, and `engine/pyproject.toml`.*

Governing decision (`FINDINGS_SYNTHESIS.md` §0 item 5, locked): **the engine typesets all text-dense
slides itself** — exact Montserrat, brand hex, claim-gated strings — over programmatic or diffusion
grounds. Diffusion renders text only for short-hook covers (≤2 spans, ≤6 words each). This spec covers
the first half only: the typesetting/compositing layer. It does **not** touch prompt authoring
(`promptcraft.py`), the claim gate, or the slot state machine — those are `RENDER_CONTRACT_SPEC.md` and
`SLOT_MODEL_SPEC.md` territory. This module is a pure, offline, dependency-light renderer that
`media_gen.py` calls; **no code in this spec is written today** — everything below is a target for the
executor.

---

## 0. Renderer choice (rejecting headless-Chromium HTML/CSS→PNG)

`engine/pyproject.toml:10-12`'s only declared dependency is `pyyaml>=6.0`. There is no HTTP client, no
browser, no Chromium anywhere in this tree. The target platform is Windows 11 with an offline-only test
suite (`cd engine && python -m pytest -q`, 515 passing, no network, no LLM — module docstring convention
throughout this codebase, e.g. `test_media_gen.py:6-10`'s `QueuedFetcher` pattern). Standing up a
headless-Chromium HTML/CSS→PNG pipeline would add a browser binary dependency, an HTTP/IPC transport to
drive it, and a non-trivial new offline-test story (screenshotting requires either a bundled browser in
CI or a mocked rendering surface, neither of which exists). Pillow 12.1.1 is *already installed* in the
ambient environment (verified via `pip show pillow`) though undeclared — it is a pure-Python-plus-C-ext
library with zero further runtime dependencies, imports synchronously, and rasterizes deterministically
given pinned inputs (§8). **Renderer = Pillow.** Declaring it is task 1 in §10.

---

## 1. Module layout

New package `engine/src/hypeagent/compositing/`. Six leaf-ish modules, one orchestrator, one façade.
Import direction is strictly downward — no module below imports a module above it in this table (no
cycles):

| Module | Contains | May import |
|---|---|---|
| `fonts.py` | `FontSpec`, `FontResolutionError`, `resolve_font()`, `load_truetype()`, `missing_glyphs()` | stdlib, `PIL.ImageFont` |
| `typeset.py` | `Rect`, `TypeScale`, `TextBlockSpec`, `TypesetBlock`, `LaidOutLine`, `TypesetOverflowError`, `normalize_text()`, `break_lines()`, `fit_text()`, `BASELINE_GRID_PX`, `SAFE_MARGIN_PCT` | stdlib, `PIL.ImageDraw`, `hypeagent.compositing.fonts` |
| `layout.py` | `RectPct`, `SlotZone`, `LayoutRecipe`, `LayoutRecipeMissing`, `LayoutRecipeConfigError`, `load_layout_recipes()`, `resolve_layout_recipe()`, `CANVAS_SIZE_BY_ASPECT`, `resolve_canvas_size()` | stdlib, `hypeagent.compositing.typeset` (`Rect`, `TypeScale`), `hypeagent.asset_model` (`SlotRole`), `hypeagent.config_load` (`ConfigError`) |
| `grounds.py` | `GroundSpec`, `Ground`, `GroundLoadError`, `make_flat_ground()`, `make_gradient_ground()`, `make_textured_ground()`, `load_diffusion_ground()`, `load_brand_template_ground()`, `SafeZoneVerdict`, `check_ground_safe_zone()`, `request_reserved_zone_prompt_fragment()` | stdlib, `PIL.Image`, `hypeagent.compositing.typeset` (`Rect`) |
| `verify.py` | `TextFidelityVerdict`, `verify_text_fidelity()` | stdlib, `PIL.Image`, `PIL.ImageChops`, `hypeagent.compositing.{fonts,typeset,layout}` |
| `compose.py` | `CompositeResult`, `CompositingError`, `RenderRoute`, `resolve_render_route()`, `render_slot()` | stdlib, `PIL.Image`, `PIL.features`, `hypeagent.fsutil`, `hypeagent.compositing.{fonts,typeset,layout,grounds,verify}`, `hypeagent.render_contract` (`RenderContract`, `SlotSpec`, `RenderPolicy`, `VisualPolicy`), `hypeagent.asset_model` (`Slot`, `SlotRole`, `OnImageText`) |
| `__init__.py` | public façade — **exactly four names**, see the module contract below | `hypeagent.compositing.{compose,grounds}` |

`fsutil.py` (leaf module, not yet built — another W8-11 task owns it, this package only consumes
`atomic_write_bytes()`, `atomic_write_text()`, `sha256_hex()`) is a hard dependency of `compose.py`'s
final write step (§8 item 5); building the compositing package (§10 task 4) therefore also depends on
`fsutil.py` landing, alongside task 2 (Pillow declared).

`hypeagent.render_contract`'s `check_contract_consistency` (`RENDER_CONTRACT_SPEC.md` §4 check 7) needs
to confirm Pillow imports and the configured font resolves — it does this with a **local import inside
the check function**, not a module-level import, so `render_contract.py` stays the dependency-light leaf
`RENDER_CONTRACT_SPEC.md` §1 requires (it must be importable by `copy_gen`/`promptcraft` without pulling
in Pillow at every import site).

### `fonts.py` — the `missing_glyphs` algorithm (panel item A)

```python
# fonts.py
_NOTDEF_PROBE_CODEPOINT = ""   # first Private Use Area codepoint -- guaranteed absent from both
                                       # NotoSans and Montserrat, so its rendered mask IS the font's own
                                       # .notdef glyph -- the reference bitmap below is built from it.

def missing_glyphs(text: str, font: "ImageFont.FreeTypeFont") -> tuple[str, ...]:
    """Render-and-compare against the font's own .notdef bitmap. Chosen over a raw FreeType cmap walk
    (freetype-py) or a fontTools cmap read for two reasons: it needs ZERO additional dependencies --
    Pillow's own `font.getmask()` is enough, matching this package's Pillow-only mandate (§0) -- and it
    is directly testable offline against any `.ttf` already checked into `assets/fonts/`, with no
    binary cmap-table parsing to get wrong.

    For each DISTINCT non-whitespace character in `text`: renders `font.getmask(char)` and compares its
    size and pixel bytes to a reference mask rendered once per `font` from `_NOTDEF_PROBE_CODEPOINT`. A
    character whose mask is byte-identical to that .notdef reference is reported missing. Whitespace is
    always exempt (a font's `.notdef` and its space glyph are both legitimately near-empty masks, which
    would otherwise false-positive on every space). Returns the missing characters in first-occurrence
    order, deduplicated -- an empty tuple means every character has a real glyph."""
```

### `__init__.py` — exact public surface

```python
# __init__.py -- the ONLY public surface of this package.
from hypeagent.compositing.compose import CompositeResult, CompositingError, render_slot
from hypeagent.compositing.grounds import GroundSpec

__all__ = ["render_slot", "GroundSpec", "CompositeResult", "CompositingError"]
```

`CompositingError` is the equivalent of "`CompositeFailure`" named by the panel review — kept under its
existing name rather than introduced as a second type, since it is already the one error class every
row of §7's failure table raises and every existing cross-reference in this document (and in
`media_gen.py`'s planned `_render_locally`/`_complete_success` call sites, §6) already names it.

**One sanctioned deep import, not a second façade.** `resolve_render_route()` (and the `RenderRoute`
Literal it returns) is deliberately *not* in `__init__.py` — it is a pre-render **planning** decision
(§3: called once per slot by the media stage, before `render_slot` is ever invoked, to decide whether a
diffusion call happens at all), not part of `render_slot`'s own call graph, so it does not belong on the
caller-facing rendering interface. `media_gen.py`'s planning layer imports it directly —
`from hypeagent.compositing.compose import resolve_render_route` — the one documented exception to "the
façade is the caller-facing surface," on the same footing as the whitebox-test allowance below.
Submodules (`fonts`, `typeset`, `layout`, `grounds`, `verify`) otherwise stay directly importable only
for whitebox tests (`from hypeagent.compositing import fonts` etc.) — never as a second public surface
for a caller that merely wants to render an image.

### Module contract (CODING_GUIDELINES §18)

**Purpose:** deterministic, offline, $0 typesetting + compositing of gated on-image text over a
programmatic or diffusion-generated ground, for every image this engine ships.

**Public API:** `render_slot(*, contract, slot, style_system, ground_spec, dest_path) -> CompositeResult`
— one call, one business concept ("render this slot"). `GroundSpec` is the only input type a caller
constructs; `CompositeResult`/`CompositingError` are the only output types a caller inspects.

**Invariants:**
- Same inputs → byte-identical PNG (§8).
- Text that cannot fit at `min_pt` is never truncated (§4.4).
- The verified pixels are re-derived from `slot.on_image_text`, never from `render_slot`'s own working
  state (§5).
- Every failure is fail-closed; every failure and every non-fatal fallback is traceable by the caller
  (§7), nothing ships un-traced.

**Do not:**
- Do not call this package's submodules (`fonts`, `typeset`, `layout`, `grounds`, `verify`) from outside
  this package's own tests — whitebox-test-only, never a second public surface.
- Do not construct a `Ground` or a text layer outside this package; the caller supplies a `GroundSpec`
  (declarative) and receives a `CompositeResult` (opaque) — nothing in between crosses the boundary.
- Do not add a network client, an LLM call, `datetime.now()`, or unseeded randomness anywhere in this
  package (§8) — no exception, no "just this once" debug hook.
- Do not add a raw `open(...).write(...)` or a local sha256 helper — use `hypeagent.fsutil` (§8 item 5).
- Do not invent a layout skeleton in code when a `zones` block is missing or malformed —
  `LayoutRecipeMissing`/`LayoutRecipeConfigError`, never a silent default (§4.3).

### Canvas sizes — single source, shared with `RenderContract.visual.aspect_ratio`

```python
# layout.py
CANVAS_SIZE_BY_ASPECT: dict[str, tuple[int, int]] = {
    "16:9": (1920, 1080),   # linkedin
    "4:5":  (1080, 1350),   # instagram_feed — matches assets/brand/hypelead/post-templates/post-portrait-*-1080x1350.png exactly
    "1:1":  (1080, 1080),   # legacy fallback aspect (config/themes/hypedigitaly.yaml:357)
}
# Panel item H: 9:16 deliberately absent — no destination in
# generation.media.aspect_ratio_by_destination uses it today, and the linkedin (16:9) /
# instagram_feed (4:5) pair are the only live destinations. resolve_canvas_size's
# ValueError-on-unknown-aspect (below) is exactly the mechanism that surfaces the day a real
# 9:16 destination is added — carrying dead speculative config now buys nothing.

def resolve_canvas_size(aspect_ratio: str) -> tuple[int, int]:
    """KeyError-free: raises CompositingError-compatible ValueError on an unknown aspect so a
    destination missing from generation.media.aspect_ratio_by_destination fails at compose time
    exactly as check_contract_consistency check 4 (RENDER_CONTRACT_SPEC.md §4) already fails it at
    load time — this is redundant-by-design defence-in-depth, not the primary gate."""
```

---

## 2. The single public entry point

```python
# compose.py
def render_slot(
    *, contract: "RenderContract", slot: "Slot", style_system: str, ground_spec: "GroundSpec",
    dest_path: Path,
) -> CompositeResult: ...
```

`GroundSpec` is a **declarative** descriptor of the ground the caller wants — never a built `Ground`
object. The caller states WHAT it wants; `render_slot` decides HOW to build and validate it, internally:

```python
# grounds.py
@dataclass(frozen=True)
class GroundSpec:
    kind: Literal["programmatic", "diffusion", "brand_template"]
    recipe_id: str | None = None            # e.g. "flat" | "gradient:brand-a" | "textured:paper" -- required iff kind == "programmatic"
    source_path: Path | None = None         # downloaded diffusion image, or the brand-template asset path -- required iff kind != "programmatic"
    safe_rect_pct: "RectPct | None" = None  # the declared safe rectangle (§3) -- required iff kind != "programmatic"

    def __post_init__(self) -> None:
        """Fail-closed on construction, not on first use: a programmatic GroundSpec with no
        recipe_id, or a diffusion/brand_template GroundSpec missing source_path or safe_rect_pct,
        raises ValueError immediately -- the same discipline §4.3's zone loader applies to config."""
```

`render_slot` builds the ground, runs the safe-zone/contrast check, typesets, verifies, and fails closed
— **all internally**. The caller never orchestrates these steps and never constructs a `Ground`, a text
layer, or touches fitting/verification internals (module contract, §1). Concretely, `render_slot`'s
procedure is:

1. `normalize_text()` every zone string sourced from `slot.on_image_text` (§4.2).
2. `layout.resolve_layout_recipe(role=slot.role, style_system=style_system)` (§4.3).
3. Build a `Ground` from `ground_spec` — `grounds.make_flat_ground`/`make_gradient_ground`/
   `make_textured_ground`/`load_diffusion_ground`/`load_brand_template_ground`, dispatched on
   `ground_spec.kind`/`recipe_id`.
4. When `ground_spec.kind == "diffusion"`: `grounds.check_ground_safe_zone(...)`; on failure, rebuild
   the ground as programmatic (§3, case b) — never raised as an error, recorded as a warning instead.
5. `typeset.fit_text()` every zone (§4.4) and run the §4.5 hierarchy check.
6. Draw each zone's `TypesetBlock` onto a fresh transparent RGBA `text_layer` (§5).
7. Alpha-composite `text_layer` onto the ground — the **last** compositing step (§5 already
   cross-references this as "step 7").
8. `verify.verify_text_fidelity()` against `slot.on_image_text`, independently re-deriving the expected
   pixels (§5).
9. `fsutil.atomic_write_bytes(dest_path, png_bytes)` + `fsutil.sha256_hex(png_bytes)` (§8 item 5).

Any stage failing raises `CompositingError`; nothing partially-written ever reaches `dest_path`.

```python
@dataclass(frozen=True)
class CompositeResult:
    path: Path
    checksum_sha256: str
    verified_text: "TextFidelityVerdict"
    font_used: "FontSpec"
    layout_recipe: str                    # f"{slot.role.value}:{style_system}" — provenance identifier
    warnings: tuple[str, ...]             # non-fatal notes, e.g. font fallback used, ground safe-zone fallback (§7)
    canvas_size: tuple[int, int]
    ground_source: str                    # Ground.source ACTUALLY USED — "flat" | "gradient" | "textured" | "diffusion" | "brand_template"
    pillow_version: str                   # PIL.__version__, read once — provenance identity (§6)
```

`verified_text`/`font_used` hold internal types (`TextFidelityVerdict`/`FontSpec`) not re-exported by
`__init__.py` (§1) — a caller uses their fields (`.status`, `.family`, …) without needing to import the
class; a deep import for typing purposes only is the one place this is legitimate, mirroring the
whitebox-test allowance above.

`render_slot` is pure given its inputs: same `(contract.sha256, slot, style_system, ground_spec's own
bytes)` → byte-identical PNG at `dest_path` (§8). No network call, no LLM call, no `datetime.now()`, no
unseeded randomness anywhere in this call graph.

This is the exact shape `media_gen._write_provenance_yaml` (`media_gen.py:1697-1758`) already writes
per slot — `CompositeResult.path`/`checksum_sha256` map straight onto that function's `image_path`/
`checksum` parameters, `CompositeResult.verified_text.to_qa_yaml_dict()` (§5) maps onto its `qa`
parameter, and `font_used`/`layout_recipe`/`pillow_version`/`ground_source` map onto a new `compositing`
provenance block (§6) — so a case-(a) slot (§3) produces a provenance YAML with the exact same
top-level keys as a diffusion-submitted one — `status`, `checksum_sha256`, `qa`, `prompt_pattern_version`,
etc. — just with `requested_route="composite-local"` and `prompt_full=None` (§6).

---

## 3. Routing: which slots are composited vs diffused

```python
# compose.py
RenderRoute = Literal["composite_flat", "composite_over_diffusion", "diffusion_native_text"]

def resolve_render_route(*, slot_spec: "SlotSpec", render_policy: "RenderPolicy") -> RenderRoute: ...
```

Panel item F: `ground_source` is a **per-slot** field on `SlotSpec` (it varies per slot within one
asset — a carousel's cover slide and its body slides commonly want different grounds — so it cannot
live on the asset-wide `RenderPolicy`, which after this move keeps only `compositing_enabled`,
`composited_roles`, `diffusion_text_max_spans`, `diffusion_text_max_words_per_span`). Every reference to
`RenderPolicy.ground_source` in this document is `SlotSpec.ground_source` after W8-11.

| Case | `SlotSpec.text_render_mode` | `SlotSpec.ground_source` | Provider calls | What happens |
|---|---|---|---|---|
| **(a)** | `"composited"` | `"programmatic"` | **0** | `grounds.make_flat_ground` / `make_gradient_ground` / `make_textured_ground` / `load_brand_template_ground` builds the ground; `render_slot` draws all text on top. Zero provider spend, zero diffusion, zero vision-QA call. |
| **(b)** | `"composited"` | `"diffusion"` | **1** (image gen) | The existing `MediaGenerator._submit_new` path (`media_gen.py:1465-1524`) submits a `GovernedPrompt` that reserves a text zone (below); once the image downloads, `render_slot` composites text onto it. |
| **(c)** | `"diffusion"` | n/a | **1** (image gen) | Unchanged existing path — the diffusion model renders its own in-scene text. `compositing` package is **never called** for this case. Bounded by `RenderPolicy.diffusion_text_max_spans` (2) / `diffusion_text_max_words_per_span` (6), enforced in `promptcraft.validate_crafted_prompt` — not this module's concern. Cover-hook slots only (`SlotSpec.is_cover`). |

(Panel item H: no `"auto"` variant — a `SlotSpec.ground_source` is authored explicitly per slot at
config time, exactly like every other number in `RENDER_CONTRACT_SPEC.md` §5's single-source table; an
"auto" value would be a second, ungoverned place ground routing could be decided, which is the same
defect class W8-11 exists to remove.)

`resolve_render_route` is a pure function of the contract, called once per slot by the (not-yet-built)
W8-11 `plan_media_assets` successor to decide, before any submission, whether a `MediaAssetPlan` ever
reaches `KieClient.create_task` at all. It never inspects run-time state — the route is fixed the
moment the contract is resolved (`RENDER_CONTRACT_SPEC.md` §2: "resolved once per asset, before any
authoring").

### Case (b): requesting and validating the reserved text zone

The safe rectangle is **declared before the diffusion call**, from the `LayoutRecipe` (§4), never
discovered afterward by image analysis:

```python
# grounds.py
def request_reserved_zone_prompt_fragment(*, safe_rect_pct: "RectPct", purpose: str) -> str:
    """Returns one English directive clause, e.g.:
    'Reserve a plain, low-detail region occupying the bottom 32% of the frame (x: 6%-94%,
    y: 64%-92%) for text overlay added after generation -- keep this region free of faces, small
    text, high-contrast edges, or business-critical objects; a single soft, low-variance surface
    (out-of-focus background, solid wall, plain sky, blurred surface) is ideal there.'
    Appended into the STYLE section of the crafted prompt (promptcraft.SYSTEM_PROMPT's own
    numbered-directive convention), so it passes through render_contract.govern() (RENDER_CONTRACT_
    SPEC.md §6) unchanged -- it names no on_image_text span, so text-set closure does not apply to
    it, but the leak/register checks still run over it like any other prompt byte."""
```

After the image downloads (`media_gen.download_and_checksum`, `media_gen.py:491-509`) and before
`render_slot` draws anything on top, the compositor validates the **actual returned pixels** in the
declared rectangle:

```python
# grounds.py
@dataclass(frozen=True)
class SafeZoneVerdict:
    ok: bool
    mean_luminance: float
    luminance_stddev: float
    contrast_ratio_vs_text_color: float
    reason: str | None

def check_ground_safe_zone(
    *, ground: "Ground", safe_rect: "Rect", text_color_hex: str,
    max_luminance_stddev: float = 18.0, min_contrast_ratio: float = 4.5,
) -> SafeZoneVerdict:
    """Deterministic, $0, no LLM, no network. Crops ground.image to safe_rect; converts to
    ITU-R BT.601 luminance (0.299R + 0.587G + 0.114B per pixel); computes the population mean and
    stddev of that crop. ok=False (fail-closed) when EITHER:
      - luminance_stddev > max_luminance_stddev (the region is too visually busy -- text laid over
        it would be genuinely illegible, independent of color choice), OR
      - the WCAG relative-luminance contrast ratio between mean_luminance and text_color_hex's own
        luminance is < min_contrast_ratio (the classic (L1+0.05)/(L2+0.05) formula).
    Thresholds are named module constants in grounds.py (not inline magic numbers) so a later
    style-system tuning pass has one place to adjust them without touching the algorithm."""
```

**Panel item G — what happens when the paid-for background fails the safe-zone check.**
`SafeZoneVerdict.ok is False` does **not** raise `CompositingError` and does **not** trigger a paid
regeneration. `render_slot` (step 4 of its procedure, §2 — internal, never surfaced to the caller) falls
back to a **programmatic** ground for that slot only: the same `make_flat_ground`/`make_gradient_ground`/
`make_textured_ground` machinery case (a) already uses, seeded from `contract.visual.style_system`'s own
palette, never the rejected diffusion pixels — and proceeds to typeset and verify exactly as case (a)
would. `CompositeResult.ground_source` then reports `"flat"` (or whichever programmatic recipe was
used), not `"diffusion"`, and `CompositeResult.warnings` gains one entry: `"ground safe-zone check
failed ({reason}); fell back to a programmatic ground for this slot"`.

*Why this option, not a re-submit or a hard block, in three lines.* A programmatic fallback costs $0 and
spends no `ATTEMPT_MAX` budget, unlike re-submitting the SAME `GovernedPrompt` for a second paid image
with no guarantee of a cleaner safe rect. Failing closed to `BLOCKED_NO_IMAGE` would throw away the
diffusion spend that already happened *and* risk collapsing the whole asset to `copy_only`
(`SLOT_MODEL_SPEC.md` §4) for a defect this module can repair itself, deterministically, for free. The
ground swap is real but never silent — it is named in `CompositeResult.warnings` and traced by the
caller as a plain `trace.decision(...)` (success path, not an except block — same treatment as the
font-fallback row in §7), which is what keeps it from violating I5 (substitution must be visible, not
forbidden).

*Resulting `SlotState`:* unchanged — the slot still completes `SUBMITTED` → `RENDERED`
(`SLOT_MODEL_SPEC.md` §3) exactly as a clean diffusion ground would; only `Ground.source` in the
provenance record differs from what was originally requested. No `REGEN`, no `HELD_QA` for this cause.
*Test:* `test_ground_safe_zone_failure_falls_back_to_programmatic_ground` (§9).

**Cross-cutting note on case (b) and N-E vision-QA:** compositing verifies text fidelity (§5) but makes
no claim about the diffusion ground's own subject relevance, logo fidelity, or composition — those
still need `run_vision_qa`'s judgment (`media_gen.py:969-1087`). Today, `run_vision_qa` skips its ENTIRE
call whenever `expected_text` is falsy (`media_gen.py:1010-1011`); for case (b), the compositor — not
the diffusion model — owns the on-image text, so `expected_text` passed to `run_vision_qa` should be
`None`. Under the *current* code, that would skip `subject_relevant`/`logos_ok`/`composition_ok` too,
which `FINDINGS_SYNTHESIS.md` §4 item 6 already names as a required fix ("text booleans skip
individually; subject/composition/gibberish/logo checks always run"). **This spec depends on that N-E
trigger fix landing** for case (b) to satisfy QA totality (I4) — it is out of scope here (owned by the
W8-11 media_gen.py rewrite) but is named as an explicit sequencing dependency in §10.

For case (b), compositing runs **inside** `_complete_success` (`media_gen.py:1575-1638`), immediately
after `download_and_checksum` succeeds and before `qa_runner` is invoked (`media_gen.py:1614-1620`) — so
`run_vision_qa` sees the *final composited* image (ground + text), never the bare diffusion output.
Provenance keeps `qa` = the vision verdict (unchanged shape) and gains a sibling key
`composite_text_fidelity` = `TextFidelityVerdict.to_qa_yaml_dict()` (§5/§6) — two independent verdicts on
the same file, not one replacing the other.

---

## 4. Text layout engine

### 4.1 Inputs and safe margins

```python
# typeset.py
BASELINE_GRID_PX: int = 4          # every laid-out line's y-origin snaps to the nearest multiple of this
SAFE_MARGIN_PCT: float = 0.08      # margin on all four sides, computed off min(canvas_w, canvas_h)

@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

@dataclass(frozen=True)
class TypeScale:
    min_pt: int
    max_pt: int
    step_pt: int = 1
    line_height_mult: float = 1.2

@dataclass(frozen=True)
class TextBlockSpec:
    text: str                      # already normalize_text()-ed
    font_spec: "FontSpec"
    type_scale: TypeScale
    rect: Rect                     # already margin-reduced (safe-zone applied by the caller)
    align: Literal["left", "center", "right"]
    color_hex: str
    max_lines: int
```

`compute_safe_rect(canvas_size: tuple[int, int], margin_pct: float = SAFE_MARGIN_PCT) -> Rect` lives
alongside these and is the box every `LayoutRecipe`'s zone rects are percentages *of* (§4.3).

### 4.2 Normalization — carrying forward `assets/fonts/README.md`'s two findings

`assets/fonts/README.md`'s two findings are about FFmpeg's `drawtext` filter specifically (a literal
`\n` inside a `drawtext` `textfile` renders as a visible `.notdef` box; CRLF puts a `\r` box at every
line end) — Pillow's `ImageDraw.multiline_text`/manual per-line drawing does **not** share the first
defect (it treats `\n` as a genuine line break, never a glyph). The second finding — CRLF/BOM
contamination rendering a stray glyph box — **does** apply here identically, because the underlying
cause (a control character reaching the font's glyph-lookup path) is renderer-agnostic:

```python
def normalize_text(text: str) -> str:
    """Strip a leading BOM (﻿); normalize CRLF and lone CR to LF; collapse 3+ consecutive
    newlines to 2 (visual-only, never drops content). Every string handed to fit_text() has already
    passed through this -- render_slot() calls it once per zone before layout, never leaves it to
    the caller. UTF-8 in, UTF-8 out, LF-only line endings, no BOM -- matching assets/fonts/README.md's
    'the engine's overlay writer must normalize line endings before composition' finding, generalized
    from the FFmpeg overlay writer to this one."""
```

### 4.3 Layout skeleton — `SlotRole` → zones, loaded from config (panel item F)

Layout skeletons are **not** hardcoded in `layout.py`. `layout.py` LOADS them from each style system's
own `zones` block: `style_systems.<system>.slots.<role>.zones: [{name, rect_pct, type_scale, weight,
align, max_lines, color}]` (config shape owned by `STYLE_SYSTEMS_SPEC.md`; `layout.py` is the reader,
not the author, of that block).

```python
# layout.py
@dataclass(frozen=True)
class RectPct:
    x: float; y: float; w: float; h: float    # 0..1, fraction of the safe rect (not the full canvas)
    def to_px(self, safe_rect: Rect) -> Rect: ...

@dataclass(frozen=True)
class SlotZone:
    field: Literal["kicker", "title", "body"]  # matches OnImageText's own field names -- no 4th field invented
    rect_pct: RectPct
    type_scale: TypeScale
    font_weight: Literal["SemiBold", "Regular", "Bold"]   # "Bold" added — two of the six style systems need it
    align: Literal["left", "center", "right"]
    max_lines: int
    color_hex: str | None                       # None == inherit from style_system palette (STYLE_SYSTEMS_SPEC.md)

@dataclass(frozen=True)
class LayoutRecipe:
    role: "SlotRole"
    style_system: str
    zones: tuple[SlotZone, ...]
    hierarchy: tuple[str, ...]                   # dominance order, e.g. ("title", "kicker", "body") -- §4.5
    logo_zone: RectPct | None
    ground_preference: Literal["programmatic", "diffusion", "brand_template"]

class LayoutRecipeMissing(KeyError):
    """A structurally VALID config simply has no zones block for this (role, style_system) pair.
    NEVER falls back to a default skeleton. A silent skeleton swap is exactly the provenance-class
    substitution invariant I5 (RENDER_CONTRACT_SPEC.md §9) forbids for prompts; it is equally forbidden
    for layout. There is no in-code default skeleton anywhere in this package — not even for a style
    system that has authored zero zones blocks."""

class LayoutRecipeConfigError(config_load.ConfigError):
    """A zones block IS present but fails validation (below). Distinct from LayoutRecipeMissing:
    this is a config-authoring bug, caught at load time, never a mid-run surprise — same discipline as
    RENDER_CONTRACT_SPEC.md §4 check 7's font-availability check next to it."""

def load_layout_recipes(style_systems_config: Mapping[str, Any]) -> dict[tuple["SlotRole", str], LayoutRecipe]:
    """Parses every style_systems.<system>.slots.<role>.zones block ONCE, at config-load time (called
    from render_contract.check_contract_consistency's compositing-readiness check, RENDER_CONTRACT_SPEC.md
    §4 check 7, alongside the font-availability check -- so a malformed block is a load-time
    LayoutRecipeConfigError, never a mid-run surprise). For EACH zones block, validates:
      1. Every zone's rect_pct lies inside the canvas: 0 <= x, y and x+w <= 1, y+h <= 1 (fraction of
         the safe rect, per RectPct's own doc).
      2. No two zones overlap in rect_pct space (pairwise rectangle-intersection test) -- every zone in
         this package carries text, so "no overlap for text zones" means no overlap, full stop.
      3. The role's required zone `field` names are present -- a small internal table,
         `_REQUIRED_ZONE_FIELDS_BY_ROLE: dict[SlotRole, frozenset[str]]` (e.g. every role needs at least
         a "title" zone; PROMPT_QUOTE needs a "body" zone instead, per its exemption from the word cap).
      4. `font_weight`/`align`/`color_hex` are each one of their Literal's legal values (or None for
         color_hex, meaning "inherit").
    Any violation raises LayoutRecipeConfigError naming the (role, style_system), the zone, and the
    specific rule broken. Returns one LayoutRecipe per (role, style_system) pair found in a
    STRUCTURALLY VALID config -- resolve_layout_recipe becomes a pure, memoized dict lookup into this
    pre-validated table (built once per process, never re-parsed per slot)."""

def resolve_layout_recipe(*, role: "SlotRole", style_system: str) -> LayoutRecipe:
    """Pure lookup into the table load_layout_recipes() built. Raises LayoutRecipeMissing for a pair
    genuinely absent from a structurally valid config -- never falls back to a default skeleton."""
```

**No fallback, by design.** There is no small in-code default skeleton kept as a documented fallback —
the panel's second option is the one this spec takes. A style system with no `zones` block for a
(role, style_system) pair a live contract actually uses fails exactly like a missing font: at load time
via check 7's extended coverage where reachable, or at first `resolve_layout_recipe` call otherwise —
never silently rendered from a hardcoded shape. This mirrors invariant I5 exactly as this spec's own
`LayoutRecipeMissing` docstring already argued for the missing-pair case, extended to the
present-but-malformed case via `LayoutRecipeConfigError`.

**Coverage requirement, not this file's job to fully populate:** the six named style systems and their
concrete palette/type-scale numbers are `STYLE_SYSTEMS_SPEC.md`'s territory (`FINDINGS_SYNTHESIS.md` §5:
"full specs in the benchmark report"). This spec fixes the *shape* of `LayoutRecipe`/`zones` and requires
one entry per `(role, style_system)` pair actually used: 3 LinkedIn systems × `role=hero` (3 recipes) + 3
Instagram systems × `role ∈ {cover, body, prompt_quote, end_card}` (up to 12 recipes) = ≤15 total.
Worked example (`role=prompt_quote`, `style_system="Prompt Sheet"` — explicitly "text composited, never
diffusion" per `FINDINGS_SYNTHESIS.md` §5): a monospace-styled single `body` zone occupying the safe
rect's full width, `align="left"`, `max_lines=8`, `ground_preference="programmatic"` (flat near-black
card, thin border) — this is the pattern every other recipe follows, tuned per system.

§10 task 10 names authoring the 15 stopgap `zones` blocks as an explicit W8-11 task, sourced from
`FINDINGS_SYNTHESIS.md` §5's table until `STYLE_SYSTEMS_SPEC.md` lands with exact hex/pt values.

### 4.4 Fitting algorithm — deterministic, shrink-to-fit, fail-closed

```python
# typeset.py
class TypesetOverflowError(RuntimeError):
    def __init__(self, spec: TextBlockSpec, *, tried_sizes: tuple[int, ...]) -> None: ...

def break_lines(text: str, *, font: "ImageFont.FreeTypeFont", max_width_px: int) -> list[str]:
    """Deterministic greedy word-wrap. Splits on whitespace; a pre-existing '\n' (post-normalize_text)
    is always a hard break. Accumulates words onto the current line while
    draw.textlength(line, font=font) <= max_width_px; otherwise starts a new line. A single word
    LONGER than max_width_px is never hyphenated or split -- it becomes its own over-width line and is
    left for fit_text's shrink loop (or ultimately TypesetOverflowError) to handle. Never truncates a
    word or drops a word."""

def fit_text(spec: TextBlockSpec) -> TypesetBlock:
    """Tries font_size_pt from spec.type_scale.max_pt DOWN to min_pt in -step_pt steps (largest
    first -- see rationale below). At each size: resolve the font at that size
    (fonts.load_truetype), break_lines() at spec.rect.w, and accept the FIRST size where
    len(lines) <= spec.max_lines AND every line's rendered width <= rect.w AND the total block
    height (len(lines) * size * type_scale.line_height_mult) <= rect.h. Line y-origins snap to the
    nearest BASELINE_GRID_PX multiple.

    Largest-first is the deterministic tie-break: it guarantees the result is the LARGEST size that
    fits, not merely 'the first size that happens to fit' from the small end -- which would make
    otherwise-identical slides in the same role render at inconsistent, non-maximal sizes depending
    on incidental string length, breaking visual hierarchy across a carousel.

    No size in [min_pt, max_pt] satisfies all three conditions -> raises TypesetOverflowError,
    carrying the FULL original spec.text (never a truncated copy) and every size tried. This is the
    hard fail-closed rule: text that cannot fit at min_pt is never silently truncated, clipped, or
    shrunk past min_pt -- matching the codebase's own existing 'truncation-never-accepted' invariant
    (FINDINGS_SYNTHESIS.md §7 KEEP list) applied to this new rendering surface."""
```

**Why word-cap enforcement at CRAFT time does not make this redundant:** `ConstraintSet.caps[...]`
(`RENDER_CONTRACT_SPEC.md` §3) bounds word *count*, not rendered *width* — a Czech compound word or a
long unhyphenated proper noun can satisfy a word cap and still overflow `max_lines` at `min_pt`,
especially for diacritic-heavy Czech text (the exact concern `assets/fonts/README.md`'s Czech glyph
test exists to catch, one layer up). `fit_text` is therefore an independent, mandatory backstop, not a
redundant re-check — it is the last line of defense against ship­ping unreadable or clipped text.

### 4.5 Hierarchy check

After every zone in a `LayoutRecipe` is independently fit, `compose.py` checks
`LayoutRecipe.hierarchy` (a dominance-ordered tuple of zone `field` names, e.g. `("title", "kicker",
"body")`): the resolved `font_size_pt` for each field must be **monotonically non-increasing** along
that order. A subordinate zone (e.g. `body`) ending up strictly larger than a dominant one (e.g.
`title`) after independent shrink-to-fit is a **hierarchy inversion** — `CompositingError(stage=
"typeset", reason="hierarchy inversion: body 34pt > title 30pt")` (§7). This is fail-closed by the same
logic as overflow: a visually backwards hierarchy is a defect class, not a cosmetic nit, and this
codebase does not ship known-defective renders.

---

## 5. Text-fidelity verification (`verify.py`)

No OCR dependency exists or is added. The method is **draw-then-compare**, and its guarantee rests on
one design rule: **the expected side is always re-derived from the slot's own gated `OnImageText`
fields, never from whatever `compose()` internally drew.**

```python
# verify.py
@dataclass(frozen=True)
class TextFidelityVerdict:
    status: Literal["composite-verified", "mismatch"]
    method: str = "draw-then-compare-exact"
    checked_zones: tuple[str, ...] = ()
    mismatched_zone: str | None = None
    mismatched_pixel_count: int = 0
    text_layer_sha256: str = ""
    notes: str | None = None

    def to_qa_yaml_dict(self) -> dict[str, Any]:
        """Same field surface as VisionQaResult.to_yaml_dict() (media_gen.py:954-966) so
        _write_provenance_yaml's `qa` key (media_gen.py:1697-1758) can hold either verdict type
        interchangeably:
        {"status": "composite-verified" | "fail", "text_matches": self.status == "composite-verified",
         "archetype_ok": True, "subject_relevant": True, "logos_ok": True, "composition_ok": True,
         "series_consistent": True, "mismatches": [] or [self.notes], "notes": self.notes,
         "skip_reason": None, "method": self.method}
        The four art-director booleans are True *by construction*, not vacuously skipped: a case-(a)
        ground is programmatic (no subject to be irrelevant to -- it IS the topic's brand palette),
        no third-party logo is ever placed except the fixed files named in §3's ground-asset table,
        and composition follows the deterministic LayoutRecipe -- there is no LLM judgment call left
        to make for a case-(a) image, so recording True-with-reason satisfies QA totality (I4) without
        a vision call, rather than silently omitting the fields."""

def verify_text_fidelity(
    *, text_layer: "Image.Image", zones: Sequence["SlotZone"], expected_spans: Mapping[str, str],
    canvas_size: tuple[int, int],
) -> TextFidelityVerdict: ...
```

**Mechanism.** `render_slot` draws every zone's text onto a **dedicated, fully transparent RGBA buffer**
the size of the canvas (`text_layer`) — never directly onto the ground — using the `TypesetBlock` each
zone's `fit_text()` call returned. `text_layer` is then, and only then, alpha-composited onto the ground
as the *last* compositing step (§2, step 7 in `render_slot`'s procedure below) — nothing drawn afterward
can touch those pixels, so `text_layer` is a faithful stand-in for "what text ends up in the delivered
PNG."

`verify_text_fidelity` receives `expected_spans` sourced **directly from `slot.on_image_text`** (the
single gated field `render_contract.govern()` already trusts, `RENDER_CONTRACT_SPEC.md` §6) — not from
any intermediate value `compose()` computed. For each zone, it **independently**: (1) calls
`fonts.resolve_font()` again, fresh — not the `FontSpec` object `compose()` already built; (2) calls
`typeset.fit_text()` again, fresh, over `expected_spans[zone.field]`; (3) draws the resulting
`TypesetBlock` onto a **new** transparent scratch buffer; (4) crops both the scratch buffer and
`text_layer` to `zone.rect_pct.to_px(...)` and diffs them with
`PIL.ImageChops.difference(scratch_crop, text_layer_crop).getbbox() is None`.

**Why this is a real guarantee, not a tautology.** `fit_text`/font resolution/drawing are pure
deterministic functions: the *same inputs* always produce the *same pixels*. `compose()`'s draw call and
`verify_text_fidelity`'s re-render are therefore two **independent invocations of the same deterministic
pipeline, fed from two different sources of "what should be drawn"** — `compose()`'s internal working
state versus `slot.on_image_text` read fresh. If a bug in `compose()` ever caused it to draw the wrong
field's text (an off-by-one on which slot's text got used), a stale cached string, a mutated/corrupted
`FontSpec`, or a wrong draw coordinate, the independently-recomputed scratch render — built from the
canonical gated source, not from `compose()`'s possibly-corrupted internal state — will diverge in
pixels, and the diff will be non-empty. Determinism is what makes divergence in the *output* provably
mean divergence in the *input*: two runs of a pure function differ only if fed different arguments. A
dedicated test proves this is a real discriminator and not a self-agreeing check: it deliberately draws
a **wrong** string into `text_layer` (bypassing `render_slot`) and asserts `verify_text_fidelity` reports
`status="mismatch"` (§9, `test_text_fidelity_verify_detects_deliberately_wrong_text`).

**This satisfies the QA-totality invariant for composited images without an N-E vision call.** For a
case-(a) image, `TextFidelityVerdict` **is** the `qa` field written by `_write_provenance_yaml`
(`media_gen.py:1752` `"qa": qa.to_yaml_dict()`); `run_vision_qa` (`media_gen.py:969-1087`) is never
invoked, never charged against `qa_reserved_calls`, and the QA-outage rollup defect named in
`FINDINGS_SYNTHESIS.md` §2 ("0 QA successes with N images ⇒ stage degraded") does not apply — a
`status="composite-verified"` row is a real pass, not a skip.

### QA accounting — outage rollup vs. invariant I4 (panel item I)

`composite-verified` slots are **excluded** from the vision-QA outage rollup (which counts only
vision-QA-*eligible* images — case (b)/(c) diffusion slots that actually reach `run_vision_qa`; a
case-(a) slot never reaches it, by design, so it is not part of that denominator at all) but **are
included** in "every delivered image carries a verdict" (invariant I4, `SLOT_MODEL_SPEC.md` §8) — the
`TextFidelityVerdict` recorded as `qa` in its provenance is a real, independently-checked verdict, not a
`skipped` placeholder. Concretely: a run with 5 composite-verified slides and 0 diffusion-QA calls this
run is a **healthy** run, never a "0 QA successes ⇒ stage degraded" alert — that alert's denominator is
the count of vision-QA-eligible images, which is 0 here by construction, not "5 images shipped with no
QA."

---

## 6. Money + ledger integration (case a only — case b is unchanged existing money flow, §3)

Case-(a) images cost `$0` and never call `KieClient.create_task` — but they still need a real ledger row
and a real deliverability state, per this codebase's own rule that "deliverability is derived from
manifest state, never file presence" (`FINDINGS_SYNTHESIS.md` §3).

**Ledger row — yes, with these exact values:**

| Field (`Store.insert_media_intent`, `store.py:1016-1075`) | Value for a case-(a) row |
|---|---|
| `route_id` | `"composite-local"` |
| `model_string` | `"pillow-compositor"` |
| `expected_cost_credits` | `0.0` |
| `expected_cost_usd` | `0.0` |
| `requested_aspect` | the resolved `RenderContract.visual.aspect_ratio` string, e.g. `"4:5"` |
| `prompt_full` | `None` (`prompt_sha256` computed over a stable canonical string, e.g. `f"composite:{contract.sha256}:{slot.index}"`, so the identity tuple's uniqueness is unaffected — no `create_task` prompt exists to hash) |
| `task_id` | **never set** — `Store.set_media_task_id` (`store.py:1099-1108`) is simply never called for this row; the column stays `NULL` for its entire life, which the schema already permits (`MediaIntentRow.task_id: str | None`, `store.py:422`) |

**Provenance gains a `compositing` block.** `_write_provenance_yaml`'s `doc` (`media_gen.py:1730-1754`)
gains one new top-level key, written for BOTH case-(a) and case-(b) rows (not only composite-local
ones, since case (b) also calls `render_slot`, §3):

```python
doc["compositing"] = {
    "font": f"{result.font_used.family}:{result.font_used.weight}",
    "layout_recipe": result.layout_recipe,
    "pillow_version": result.pillow_version,   # PIL.__version__, read once inside render_slot
    "ground_source": result.ground_source,
}
```

so a byte-level investigation months later can immediately tell which Pillow build (and therefore which
bundled FreeType, §8) produced a given file, without cross-referencing a deploy log.

The write-ahead sequence mirrors `_submit_new` (`media_gen.py:1465-1524`) minus the `createTask` call:
`insert_media_intent(...)` (write-ahead, before any rendering) → `render_slot(...)` → on success, the
result is handed to the **shared settlement helper** (below) rather than a bare `update_media_intent` +
`_write_provenance_yaml` pair. On a `CompositingError`, the row is updated `state="failed"`,
`fail_reason=str(exc)`, `terminal=True` — same shape as a provider rejection (`media_gen.py:1512-1520`),
just with no provider ever contacted.

**Interrupted composite rows are never `submitted-unknown` (panel item C1).** `submitted-unknown` exists
to describe a state that can only be resolved by *querying a provider* (`_resolve_one_row`'s sub-cases A
and B, `media_gen.py:1137-1172`) — a composite-local row has no provider to query, so that state can
never legitimately apply to it. `_resolve_one_row` gains a **first branch, before any provider lookup**:

```python
def _resolve_one_row(self, row: MediaIntentRow) -> None:
    if row.route_id == "composite-local":
        if row.asset_slot not in self._current_run_contract_slots():   # slot dropped from this run's contract
            self.store.update_media_intent(
                row.id, state="failed", terminal=True, resolved_at=self._now(),
                fail_reason="composite slot no longer present in this run's render contract",
            )
            self.trace.try_decision(
                self.stage,
                decision=f"composite intent {row.cluster_key}/{row.asset_slot}: slot dropped from contract — failed, not resubmitted",
                rule="W8-11 COMPOSITING_SPEC §6: an interrupted composite row is re-rendered or failed, never submitted-unknown",
            )
            return None
        self._render_locally(row)   # pure, free, no network — re-render is exactly why byte-determinism (§8) is load-bearing
        return None
    if row.task_id is None:
        ...   # existing sub-case A, unchanged, provider-backed rows only
```

A composite-local row is either re-rendered deterministically (the common case — a crash between
`insert_media_intent` and settlement is recovered by simply running `render_slot` again, byte-identical,
§8) or explicitly failed with a named reason. **Never** `submitted_unknown_subcase`, **never** a provider
call. Test: `test_interrupted_composite_row_is_not_submitted_unknown` (§9).

**Shared settlement helper — `_settle_intent` (panel item C2).** `_complete_success`
(`media_gen.py:1575-1638`, the diffusion path) and the composite `_render_locally` path (above) both
route through ONE extracted helper:

```python
def _settle_intent(
    self, row: MediaIntentRow, *, image_path: Path, checksum: str, qa: "VisionQaResult | TextFidelityVerdict",
    observed_usd: float, final_state: str,
) -> None:
    """The ONLY place that writes update_media_intent(..., terminal=True) + _write_provenance_yaml(...)
    for a resolved media intent, diffusion or composite. Existing-row idempotency (re-checking
    find_media_intent for the SAME identity immediately before writing, so two racing settlements of
    the same row are a no-op on the second) and the prompt-sha comparison (below) both live INSIDE this
    helper — so a composite row cannot drift from the diffusion path by skipping a check the other path
    remembered to run."""
```

The only differences between the two callers are: no `asyncio`/polling `create_task` handle to close
out (composite has none), no `check_caps` call ever precedes it (§6's `check_caps` note below), and
`route_id` (`"composite-local"` vs. the resolved provider route). Everything else — the write shape, the
idempotency re-check, the prompt-sha guard, the provenance YAML fields — is written exactly once, in
`_settle_intent`, and both `_complete_success` and `_render_locally` call it as their last step.

**Prompt-sha guard — fail-closed on contract drift (panel item C3).** Inside `_settle_intent`, a
composite row's canonical `prompt_sha256` (`f"composite:{contract.sha256}:{slot.index}"`, above) is
compared against the SAME value freshly recomputed from the CURRENT run's contract before any write
happens. A stored value that differs — the contract changed (e.g. copy was re-crafted, bumping
`contract.sha256`) but the identity tuple's `prompt_pattern_version`/`attempt` happened not to change —
is fail-closed: `_settle_intent` does **not** write `state="done"`. It instead marks the row
`state="failed"`, `terminal=True`, `fail_reason="prompt_sha256 mismatch: contract changed, no silent
reuse"`, and the caller emits `trace.decision(...)` naming the slot `BLOCKED_NO_IMAGE` — identical
treatment to a diffusion row whose stored `prompt_sha256` no longer matches the current run's
`GovernedPrompt.prompt_sha256` (`RENDER_CONTRACT_SPEC.md` §6/§8). No composite row is ever silently
re-used across a contract change, same rule, same helper, both paths.

**Idempotency — the SAME mechanism, no special-casing.** The identity tuple is `(theme, run_date,
cluster_key, asset_slot, language, prompt_pattern_version, attempt)` — identical to every other media
intent. `find_media_intent(**identity_kwargs)` (`store.py:1081-1097`) is checked first, exactly as
`_submit_or_resolve` does today (`media_gen.py:1286-1291`); a terminal row on resume is a no-op, never
re-rendered. Because `render_slot` is pure (§8), even a race that somehow re-ran it twice would produce
byte-identical output — a nice-to-have safety property, but the ledger row (settled exclusively through
`_settle_intent`, above) remains the single source of truth for "was this already done," per this
module's own governing rule (module docstring point 1, `media_gen.py:13-20`).

**`check_caps` (`media_gen.py:567-588`) — case (a) rows must NOT consume `per_run_count_cap`.**
Justification: `check_caps` exists to bound *provider spend risk* — its docstring is explicit that
"both caps are checked at every submission" as a money guard (§8.11), and its only inputs are counts and
USD figures tied to `route.price_usd`. A case-(a) render makes no provider call and has
`expected_cost_usd=0.0` by construction; counting it against a cap whose entire purpose is bounding paid
submissions would either force operators to inflate `per_run_count_cap` to make room for free renders
(silently loosening the *actual* spend guard for paid submissions sharing that cap), or let composited
slots starve paid ones for zero safety benefit. The correct topology-level bound on composited volume
already exists one layer up: `RenderContract.max_generated_slides()` (`RENDER_CONTRACT_SPEC.md` §2) plus
`check_contract_consistency` check 6's budget-feasibility arithmetic (`RENDER_CONTRACT_SPEC.md` §4) — a
config-time refusal, not a runtime cap race. **Concretely: `MediaGenerator`'s case-(a) code path (the
not-yet-built `_render_locally`, sibling to `_submit_new`) calls `insert_media_intent`, `render_slot`,
and finally the shared `_settle_intent` (above) directly, bypassing `_submit_or_resolve`'s `check_caps`
call (`media_gen.py:1319-1333`) entirely** — it is a different method, not a flag on the existing one,
so there is no risk of accidentally threading a `$0` cost through the cap-check arithmetic and getting
the right answer by coincidence.

`MediaStageResult` (`media_gen.py:739-748`) should still be able to report composited volume for
observability (a `composite_count` field alongside `pending_count`/`submitted_unknown_count`) — an
implementation detail of the not-yet-written `media_gen.py` wiring, named here only so the executor does
not lose the number; it is explicitly **not** the same counter as `count_run` (which gates money).
`MediaStageResult` also gains `degrade_reasons: list[str] = field(default_factory=list)` (§7's
`trace.try_decision()` requirement — an in-memory record of every compositing degrade this run, so a
failed trace write can never erase the fact one happened).

---

## 7. Failure modes and fail-closed behaviour

`render_slot` itself has no `trace` dependency (§2 procedure — it stays a pure function of its inputs,
§8). The trace events below are emitted by the CALLER — `MediaGenerator._render_locally` (case a) or the
case-(b) call site inside `_complete_success` (§3) — which wraps its call to `render_slot` in exactly one
`try/except CompositingError` block. **Panel item D:** every decision/degrade event emitted from
*inside* that `except` block goes through `trace.try_decision()` (a new helper, owned by another W8-11
task, that wraps the trace write in its own `except Exception: pass` — a broken trace sink must never
turn a compositing failure into an unhandled crash) — **and** the caller appends the same reason string
to an in-memory `degrade_reasons: list[str]` (a new field on `MediaStageResult`, alongside
`composite_count`, §6) BEFORE calling `trace.try_decision()`, so a failed trace write can never erase the
fact that the degrade happened — the reason still shows up in `MediaStageResult` even if tracing itself
is down. The two success-path rows below (font fallback, ground safe-zone fallback) are NOT inside an
except block — `render_slot` returns normally with a populated `warnings` tuple — so those two keep a
plain `trace.decision()` call (still every row gets its event; only the *mechanism* differs by whether
the call site is a `try` or an `except`).

| Failure | Detected at | Case | Result | `SlotState` | Decision event |
|---|---|---|---|---|---|
| Font family unavailable, fallback disabled | `fonts.resolve_font` | a/b | `CompositingError(stage="font")` | `BLOCKED_NO_IMAGE` | except-block: `trace.try_decision(..., decision="compositing: required font unavailable, fallback disabled")` + appended to `degrade_reasons` |
| Font family unavailable, fallback **allowed** | `fonts.resolve_font` | a/b | Proceeds with NotoSans; `warnings += ("font fallback: Montserrat unavailable, used NotoSans",)` | delivers (not blocked) | success path (not except-block): plain `trace.decision(...)` — font family is a provenance-class fact (I5) even though it doesn't block |
| Glyph missing (`.notdef` for a required character) | `fonts.missing_glyphs`, pre-draw | a/b | `CompositingError(stage="glyphs")`, lists exact missing characters | `BLOCKED_NO_IMAGE` | except-block: `trace.try_decision(..., decision="compositing: font <X> lacks glyphs for {chars!r}")` + `degrade_reasons` |
| Text overflow at `min_pt` | `typeset.fit_text` → `TypesetOverflowError` | a/b | `CompositingError(stage="typeset")` — never truncates | `BLOCKED_NO_IMAGE` (a CRAFT-time repair, not a compositing retry, is the correct remedy — see §4.4) | except-block: `trace.try_decision(..., decision="compositing: text overflow, {field} needs >{max_lines} lines at {min_pt}pt")` + `degrade_reasons` |
| Hierarchy inversion | post-fit check, `compose.py` | a/b | `CompositingError(stage="typeset")` | `BLOCKED_NO_IMAGE` | except-block: `trace.try_decision(...)` naming the two zones and sizes + `degrade_reasons` |
| Ground load failure (corrupt download, brand-template asset missing/wrong size beyond tolerance) | `grounds.load_diffusion_ground` / `load_brand_template_ground` → `GroundLoadError` | a: config bug (caught pre-run by `check_contract_consistency` check 7); b: possible | `CompositingError(stage="ground")` | b: `BLOCKED_NO_IMAGE` (a corrupt download is not retried by compositing — `download_and_checksum` already retries once, `media_gen.py:1594-1596`) | except-block: `trace.try_decision(...)` + `degrade_reasons` |
| Safe-zone/contrast check fails | `grounds.check_ground_safe_zone` | b only | **Not** a `CompositingError` (panel item G, §3) — `render_slot` falls back to a programmatic ground internally and still returns a successful `CompositeResult` | delivers (not blocked); completes `RENDERED` as normal | success path (not except-block): plain `trace.decision(...)` (reads `result.warnings`) + `trace.gate_verdict(gate="ground_safe_zone", verdict="fail")` — same treatment as the font-fallback row above |
| Text-fidelity verification mismatch | `verify.verify_text_fidelity` | a/b | `CompositingError(stage="verify")` | `BLOCKED_NO_IMAGE` — this is a deterministic pure-function check on already-validated inputs; a mismatch here is a **code-bug alarm**, not a data problem, so no regeneration attempt is meaningful | except-block: `trace.try_decision(...)` + `trace.gate_verdict(gate="composite_text_fidelity", verdict="fail")` + `degrade_reasons` |

Every row in this table produces a decision event — no silent substitution (invariant I5,
`RENDER_CONTRACT_SPEC.md` §9). For case (a), `BLOCKED_NO_IMAGE` means the asset ships copy-only per the
locked fail-closed philosophy (`FINDINGS_SYNTHESIS.md` §0 item 3) — there is no "degrade to ungoverned"
available here because there never was an ungoverned prompt path for a programmatic ground in the first
place.

---

## 8. Determinism

Same `(RenderContract.sha256, Slot, style_system, ground image bytes)` → byte-identical PNG. Concretely:

1. **No timestamps.** No `datetime.now()`, no PNG `pnginfo`/`tIME`/`tEXt` chunks with dynamic content —
   `Image.save(buffer, format="PNG", optimize=False, compress_level=6)`, explicit and pinned; never
   pass `exif=` or an `icc_profile` unless it is a fixed, checked-in byte string.
2. **Layout engine pinned at load, not assumed (panel item B).** Pillow's `ImageFont.FreeTypeFont`
   supports two text-shaping engines, `ImageFont.Layout.BASIC` and `ImageFont.Layout.RAQM` (the latter
   needs `libraqm` linked into the specific Pillow wheel installed); the two engines can shape/kern the
   IDENTICAL string into different glyph positions, and therefore different output bytes — and `libraqm`
   availability is a property of the wheel, not of the Pillow version number alone, so "Pillow 12.1.1" is
   not by itself a sufficient determinism pin. `fonts.load_truetype()` therefore ALWAYS passes an
   explicit `layout_engine=ImageFont.Layout.BASIC` — this package only ever typesets Latin + Czech
   diacritics (`assets/fonts/README.md`), which need no complex/RTL shaping, so BASIC is both the safe
   and the deterministic choice, and it needs no `libraqm` dependency at all (§0: zero further runtime
   dependencies). `fonts.py` also asserts, once per process at first font load, that the resolved
   `ImageFont.FreeTypeFont` actually used `BASIC` — Pillow silently falls back to `BASIC` when raqm isn't
   linked today, so this assertion mainly guards against a FUTURE Pillow build changing that fallback
   behaviour, raising `FontResolutionError` rather than silently shipping differently-shaped glyphs.
   Hinting stays at Pillow/FreeType's own untouched default — no non-default hinting flag is used
   anywhere in this package, so there is nothing else to pin there.
3. **No unseeded randomness.** `grounds.make_textured_ground`'s noise/paper-texture pattern uses
   `random.Random(seed)` with a seed **derived deterministically** from its own inputs —
   `seed = int(hashlib.sha256(f"{canvas_size}:{texture_name}:{zone_field}".encode()).hexdigest()[:16], 16)`
   — never `random.random()`/`os.urandom` unseeded. `os.urandom`/`secrets`/wall-clock seeding are banned
   in this package; a grep-based test enforces it (§9).
4. **Fixed resize filter.** Any resize (`grounds.load_diffusion_ground`'s center-crop-to-exact-size path)
   uses a named, pinned filter (`Image.Resampling.LANCZOS`), never "best available."
5. **Write ordering — atomic, via `fsutil` (panel item E).** `render_slot` never calls a bare
   `Image.save(dest_path, ...)`/`open(dest_path, "wb")`. It renders the PNG to an in-memory buffer, then
   writes it with `hypeagent.fsutil.atomic_write_bytes(dest_path, png_bytes)` — a temp file in
   `dest_path`'s own directory, renamed into place on success (mirrors `download_and_checksum`'s "a
   truncated download is never marked done" discipline, `media_gen.py:491-509`) — so a crash mid-render
   never leaves a corrupt file at `dest_path`. `CompositeResult.checksum_sha256` is computed with
   `fsutil.sha256_hex(png_bytes)` — this package defines no local sha256 helper (one thing, one place).
   This package writes no other files today; a future debug-artifact writer would use
   `fsutil.atomic_write_text` the same way.
6. **Environment scope of the guarantee.** Byte-identical output is guaranteed for a fixed Pillow /
   bundled-FreeType build (Pillow wheels statically link FreeType, so pinning the Pillow version in
   `engine/pyproject.toml`, task 2 of §10, pins the rasterizer too) — this spec does not claim
   cross-platform pixel-identical output against a *different* Pillow build; it claims identical output
   across repeated runs on the *same* installed environment, which is what the write-ahead ledger's
   idempotency (§6) and the test suite (§9) both actually need. For the same reason, `compose.py` also
   asserts `PIL.features.check("zlib")` is `True` once at import time, alongside item 2's layout-engine
   assertion — Pillow's bundled zlib is what encodes the written PNG's pixel stream, so a Pillow build
   without it would silently change the byte-level encoding path this package's own determinism claim
   depends on; both assertions fail closed (`FontResolutionError`/import-time `RuntimeError`) rather than
   producing bytes nobody actually checked.

---

## 9. Test plan — `engine/tests/test_compositing.py`

Fully offline, no network, no LLM, matching this file's own module docstring convention
(`test_media_gen.py:1-10`). Module-level `_factory()`-style helpers (a tiny stub `RenderContract`/`Slot`
builder), `tmp_path` for all file I/O, no `conftest.py`, no fixtures.

| Test | Asserts |
|---|---|
| `test_flat_ground_composited_text_produces_valid_png` | Case (a) round trip: `render_slot` succeeds; `dest_path` exists; `checksum_sha256` matches the written file's own sha256; `verified_text.status == "composite-verified"`. |
| `test_text_fidelity_verify_detects_deliberately_wrong_text` | Draws a **wrong** string directly into a scratch `text_layer` (bypassing `render_slot`) and calls `verify_text_fidelity` against the correct `expected_spans` — asserts `status == "mismatch"`. Proves §5's method is a real discriminator, not a tautology. |
| `test_overflow_at_min_size_raises_typeset_overflow_error` | A body string far exceeding the rect at `min_pt` raises `TypesetOverflowError`; `render_slot` raises `CompositingError(stage="typeset")` and never writes `dest_path`. |
| `test_overflow_never_truncates_text` | The raised error's `spec.text` equals the FULL original string byte-for-byte — proves no truncation occurred anywhere in the failure path. |
| `test_render_slot_is_byte_identical_across_two_calls` | Same inputs, two different `dest_path`s → identical file bytes and identical `checksum_sha256` (§8). |
| `test_render_slot_changes_bytes_when_input_text_changes` | Different `on_image_text` → different `checksum_sha256` — guards against a determinism bug that silently ignores its own input. |
| `test_missing_glyph_detected_before_draw` | A codepoint absent from the active font's cmap (e.g. an emoji, or a private-use codepoint) → `CompositingError(stage="glyphs")` naming the exact missing character(s), raised before any pixel is drawn. |
| `test_font_fallback_used_when_montserrat_absent` | With `assets/fonts/montserrat/` missing and `allow_fallback=True`: `result.font_used.family == "NotoSans"`; `warnings` contains the fallback note. |
| `test_font_fallback_disabled_raises_font_resolution_error` | Same missing-font setup with `allow_fallback=False` → `FontResolutionError` / `CompositingError(stage="font")`. |
| `test_ground_safe_zone_rejects_high_variance_region` | A synthetic high-frequency checkerboard ground in the safe rect → `check_ground_safe_zone(...).ok is False`. |
| `test_ground_safe_zone_accepts_flat_low_contrast_region` | A plain dark region with white planned text color passes: `ok is True`, `contrast_ratio_vs_text_color >= 4.5`. |
| `test_ground_safe_zone_rejects_insufficient_contrast` | A flat region whose luminance nearly matches the text color's own luminance → `ok is False` via the contrast branch specifically (not the variance branch — assert `reason` names contrast). |
| `test_ground_safe_zone_failure_falls_back_to_programmatic_ground` | A synthetic diffusion `GroundSpec` whose safe rect is a high-variance checkerboard → `render_slot` does NOT raise; `result.ground_source` is a programmatic value (e.g. `"flat"`), never `"diffusion"`; `result.warnings` contains the fallback note. Proves §3's panel-item-G redesign, not the old `REGEN`/`HELD_QA` path. |
| `test_composite_local_intent_recorded_with_zero_cost` | Hand-builds a `Store` (`Store.open`, matching `test_media_gen.py:207-208`'s `_store` helper) and calls `insert_media_intent(route_id="composite-local", expected_cost_usd=0.0, expected_cost_credits=0.0, ...)` directly — asserts the round-tripped row's `task_id is None` and `expected_cost_usd == 0.0`, proving the §6 ledger shape is constructible with the store's existing API with no schema change needed. |
| `test_interrupted_composite_row_is_not_submitted_unknown` | A `composite-local` `MediaIntentRow` with `task_id=None`, `terminal=False` fed to `_resolve_one_row` → re-rendered via `_render_locally` (deterministic, no network mock needed) and settled `state="done"`, never `state="submitted-unknown"`; a second variant whose `asset_slot` is absent from the current run's contract → `state="failed"`, `terminal=True`, and still never `"submitted-unknown"`. Proves panel item C1 (`media_gen.py:1137-1172`'s new first branch). |
| `test_settle_intent_rejects_prompt_sha_drift` | Seeds an existing `composite-local` row whose stored `prompt_sha256` does not match the value recomputed from the current run's `contract.sha256` → `_settle_intent` does NOT write `state="done"`; row ends `state="failed"`, `fail_reason` names the mismatch. Proves panel item C3. |
| `test_normalize_text_strips_crlf_and_bom` | `normalize_text("Title\r\nLine2﻿")` → `"Title\nLine2"`. |
| `test_break_lines_never_hyphenates_overlong_word` | A single word wider than `max_width_px` stays on its own line, unmodified, never split. |
| `test_fit_text_prefers_largest_size_that_fits` | Constructs a spec where more than one size in the scale technically fits — asserts the returned `font_size_pt` is the *largest* candidate, proving the largest-first tie-break (§4.4). |
| `test_layout_recipe_missing_pair_raises_not_silently_falls_back` | `resolve_layout_recipe(role=..., style_system="nonexistent")` raises `LayoutRecipeMissing`, never returns a default skeleton. |
| `test_layout_zones_loader_rejects_out_of_canvas_rect` | A `zones` block with a `rect_pct` whose `x+w > 1.0` → `load_layout_recipes(...)` raises `LayoutRecipeConfigError` naming the offending zone. Proves §4.3's loader validation rule 1. |
| `test_layout_zones_loader_rejects_overlapping_text_zones` | Two zones in the same `zones` block with intersecting `rect_pct`s → `LayoutRecipeConfigError` naming both zones. Proves rule 2. |
| `test_layout_zones_loader_missing_required_zone_raises_config_error` | A `role=cover` `zones` block with no `"title"` field → `LayoutRecipeConfigError`, never a silently-incomplete `LayoutRecipe`. Proves rule 3. |
| `test_render_slot_over_diffusion_ground_case_b` | A synthetic pre-built "diffusion" `GroundSpec` (clean safe rect) → success; `text_layer_sha256` differs from the case-(a) flat-ground run (sanity: the ground actually differs). |
| `test_missing_glyphs_detects_known_font_facts` | Against `assets/fonts/NotoSans-Variable.ttf`: ASCII `'A'` and Czech `'ě'` are present (consistent with `assets/fonts/czech_glyph_test.txt`'s own claim); an intentionally absurd private-use codepoint, distinct from `fonts._NOTDEF_PROBE_CODEPOINT` (``) is reported missing. |
| `test_layout_engine_asserted_basic_at_font_load` | `fonts.load_truetype(...)` returns a font whose resolved layout engine is asserted `ImageFont.Layout.BASIC`; monkeypatching the assertion to expect `RAQM` raises `FontResolutionError` — proves §8 item 2's pin is actually checked, not just documented. |
| `test_no_unseeded_randomness_in_package` | AST/source scan of every file in `hypeagent/compositing/` for `os.urandom`, bare `random.random(`, `random.Random()` with no argument, and `secrets.` — asserts none are found (mirrors `RENDER_CONTRACT_SPEC.md` §9's own `test_no_module_level_word_cap_constants` grep-test idiom). |
| `test_no_bare_file_writes_or_local_sha256_in_package` | AST/source scan of every file in `hypeagent/compositing/` for a bare write-mode `open(` and a local `hashlib.sha256(` definition → none found; every write goes through `fsutil.atomic_write_bytes`/`atomic_write_text`, every checksum through `fsutil.sha256_hex` (panel item E). |

---

## 10. Tasks + dependencies

1. **Operator decision: vendor Montserrat or accept a NotoSans-only fallback.** Blocks tasks 3 and the
   "real Montserrat" half of task 8's font tests (the fallback half is unblocked either way — `fonts.py`
   is built against the fallback path from day one, per §7's fallback rule, so nothing else in this list
   is actually gated on the decision landing before implementation starts).
2. **Add Pillow to `engine/pyproject.toml`.** `[project] dependencies` gains `"Pillow>=12,<13"` (pin to
   the major version already present in the ambient env, 12.1.1, per §0). No other file changes.
3. **(If task 1 = vendor) Fetch and vendor Montserrat.** `assets/fonts/Montserrat-Variable.ttf` (the SIL
   OFL variable-font release, `wght` axis, matching `RENDER_CONTRACT_SPEC.md` §7's own named path) +
   `assets/fonts/montserrat/OFL.txt` (or reuse the existing `assets/fonts/OFL.txt` if the license text is
   identical — check first) + an addendum to `assets/fonts/README.md` matching the existing
   `NotoSans-Variable.ttf` entry's table row, including a Czech-glyph verification pair
   (`montserrat_glyph_test.png`/`.txt`) analogous to `czech_glyph_test.*` — Montserrat's OFL coverage
   must be *checked*, not assumed, per the precedent this repo already set for NotoSans.
4. **Build the package.** `engine/src/hypeagent/compositing/{__init__.py, fonts.py, typeset.py,
   layout.py, grounds.py, verify.py, compose.py}` per §1-§8 of this spec. Depends on task 2 (Pillow
   declared) AND on `hypeagent/fsutil.py` (`atomic_write_bytes`, `atomic_write_text`, `sha256_hex`,
   panel item E, §1/§8 item 5) landing — owned by another W8-11 task, consumed here, not redefined; does
   not block on task 1/3's outcome (fallback-first, as above).
5. **Config surface.** Add `generation.media.compositing.{enabled, font_path, renderer}` to
   `config/themes/hypedigitaly.yaml` (already sketched in `RENDER_CONTRACT_SPEC.md` §7) — `font_path`
   points at the task-3 result if vendored, else at `assets/fonts/NotoSans-Variable.ttf` with a
   `compositing.allow_font_fallback: true` flag. Depends on tasks 1/3's outcome for the actual path
   value, not on the schema shape.
6. **Wire `check_contract_consistency` check 7** (`RENDER_CONTRACT_SPEC.md` §4) to import
   `hypeagent.compositing.fonts` locally (inside the check function, per §1's note) and call
   `resolve_font(weight="Regular", allow_fallback=<config>)` — a failure here is a `ConfigError` at load
   time, never a mid-run surprise. Depends on task 4.
7. **`media_gen.py` integration** (separate task, out of this spec's file list — owned by the broader
   W8-11 implementation plan, named here only for sequencing): add `MediaGenerator._render_locally` and
   the shared `_settle_intent` helper (§6) as a sibling to `_submit_new`/`_complete_success`; wire
   `resolve_render_route` into the W8-11 successor of `plan_media_assets` to pick, per slot, between
   `_render_locally` (case a), the existing `_submit_or_resolve` path with the case-(b) safe-zone
   fallback inserted into `_complete_success` before `qa_runner` runs (§3), or the unchanged case-(c)
   path; also add `_resolve_one_row`'s new first branch (§6 panel item C1) and `MediaStageResult`'s
   `composite_count`/`degrade_reasons` fields (§6/§7). Depends on tasks 4-6 and on
   `FINDINGS_SYNTHESIS.md` §4 item 6's N-E trigger fix (§3's cross-cutting note) landing for case (b) to
   satisfy QA totality.
8. **`engine/tests/test_compositing.py`** per §9. Depends on task 4 (and task 3 for the
   Montserrat-specific half of the font tests — the NotoSans-fallback half runs regardless).
9. **Verify.** `cd engine && python -m pytest -q` — fully offline, no new network/LLM dependency, the
   pre-existing 515 tests plus the new compositing tests all green.
10. **Author the 15 stopgap `zones` blocks** (§4.3) — one per live `(role, style_system)` pair, sourced
    from `FINDINGS_SYNTHESIS.md` §5's table until `STYLE_SYSTEMS_SPEC.md` lands with exact hex/pt
    values. Depends on task 4 (`load_layout_recipes`'s validation rules must exist to check them
    against) and, for the real palette numbers, on `STYLE_SYSTEMS_SPEC.md`; unblocked in the meantime by
    hand-authoring provisional values that satisfy the loader's structural rules.
