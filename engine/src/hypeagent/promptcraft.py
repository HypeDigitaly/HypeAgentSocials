"""N-D Image-Prompt Crafter (W8-9 Q3c; FLOW_MAP.md's ``prompt craft`` row,
folded into the ``media`` stage's own invocation rather than a separate
canonical stage — it sits between the claim gate and image generation for
exactly the assets the gate already passed).

``craft_prompts`` takes one gate-passed copy asset (headline/caption/
image_brief, plus per-slide title/body for a carousel) and produces the
FULL generation prompt(s) Nano Banana 2 will receive: one ``hero`` prompt
for a single-image destination, or one ``slide_NN`` prompt per slide for a
carousel.

**W8-10 two-section prompt scheme.** Every crafted prompt this module emits
is the concatenation of exactly two labeled sections:

- **STYLE** — a literal string this module builds ITSELF, deterministically,
  from the style guide/archetype/register/handle (never delegated to the
  LLM) and reused byte-for-byte across every slide of one asset. This is
  what makes "series consistency" (same background hex, same typeface
  family, same handle corner, same margins on every slide) a construction
  guarantee rather than a hope that an LLM repeats itself faithfully across
  several JSON array entries in one response. The STYLE section is
  explicitly marked "do not render any word from this section as visible
  text" — font names, style adjectives, and element-type nouns (label,
  pill, badge, watermark) live here and ONLY here.
- **RENDER** — the LLM's own output for this one slide/hero: the exact
  on-image texts via the ``<<...>>`` convention, the proof-element
  description (with its stated relevance to this slide's own sentence),
  and the composition.

The internal series/consistency token (:func:`series_token_for`) is carried
on :class:`CraftedPromptSet` for metadata/trace/audit purposes only — W8-10
deletes every instruction that ever asked the model to render it as visible
text (a live run once printed it as a literal on-image watermark).

The crafted prompts are themselves run back through the claim gate (cheap,
safe, and catches an LLM inventing a new number/claim/superlative in a
prompt that would otherwise bypass the gate's copy-text surface entirely) —
see :func:`gate_check_prompts`.

**Media wiring THIS phase is deliberately minimal** (module docstring
mirrors the task note): only the single hero-image path is actually wired
into submission (``stages.stage_media`` swaps a crafted hero prompt in for
``compose_prompt(image_brief)`` when one is available); carousel prompts are
persisted to ``media_prompts.yaml`` for a later milestone's multi-slide
submission to consume, never submitted here. Ledger identity and the cost
caps in ``media_gen.py`` are untouched by this module.

Degrade: LLM disabled/unavailable, budget exhausted, or the call failing all
produce an ``unavailable`` :class:`CraftedPromptSet` — the caller falls back
to the existing ``compose_prompt(image_brief)`` path exactly as before this
module existed. This module never raises out to its caller.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from hypeagent.brand_truth import ClaimSnapshot
from hypeagent.claim_gate import run_claim_gate
from hypeagent.config_load import ResolvedList
from hypeagent.copy_gen import AI_DISCLOSURE_LINE
from hypeagent.llm import LlmClient, LlmError
from hypeagent.trace import TraceWriter

MEDIA_PROMPTS_FILENAME = "media_prompts.yaml"

# The guardrails that survive W8-9/W8-10 (module docstring) -- deliberately
# NOT the old no-text/no-logo/no-people/no-product-depiction list, and
# deliberately including the "no fake screenshot of our own product UI"
# clause (the third W8-9 survivor, kept here in sync with
# ``media_gen._NEGATIVE_CONSTRAINTS`` even though this module never calls
# that function directly).
# W8-10 Phase 8 (dynamic-inspiration person policy, operator decision
# 2026-08-07): NOT a blanket "no person" ban -- synthetic, non-identifiable
# people (including a visible face, for the ``photoreal_person_ugc``
# generation mode's phone-camera/selfie framing) are explicitly permitted;
# only an identifiable real individual or a celebrity/public-figure likeness
# is banned.
GUARDRAILS = (
    "no identifiable real individuals or celebrity likeness in the image; synthetic, non-identifiable "
    "people (including a visible face) are permitted; no NSFW content; "
    "never a fake screenshot of HypeDigitaly's or HypeLead's own product UI"
)

# W8-10 point 2: the two labeled sections concatenated into every crafted
# prompt. These exact literal strings are what ``validate_crafted_prompt``
# checks for and what the STYLE section (built by this module, never the
# LLM) always opens with -- see ``_build_style_section``.
STYLE_LABEL = "STYLE (do not render any word from this section as visible text):"
RENDER_LABEL = "RENDER:"

# Layout defaults (W8-10 point 9 "no layout discipline" fix). Not currently
# threaded from config/style_guide.yaml (that file is shared with the
# copywriter agent this round; these are deliberately plain module
# constants rather than a new shared-config key) -- see the task report for
# this note. A style_guide.yaml ``layout`` block, if one is ever added,
# overrides these on a per-key basis (see ``_build_style_section``).
DEFAULT_MARGIN_PERCENT = 12
DEFAULT_HANDLE_CORNER = "bottom-right"
MAX_INSET_STRINGS = 6
MAX_INSET_STRING_WORDS = 3

SYSTEM_PROMPT = (
    "You are the Image-Prompt Crafter (N-D) for HypeDigitaly's AI-agency social content pipeline "
    "(FLOW_MAP.md node N-D). For every image you are given a shared STYLE section -- already written for "
    "you, verbatim, identical across every slide of this asset; never alter, repeat, or paraphrase it "
    "yourself. You write ONLY the RENDER section: the exact on-image texts, the proof element and its "
    "relevance, and the composition. Your 'render' field is a single natural-language generation "
    "instruction -- a COMPLETE sentence/instruction ending in proper punctuation, never a list of bullet "
    "points, never stopping mid-phrase. Embed the given gate-passed text VERBATIM so it renders correctly "
    "in the final image -- never paraphrase it, never invent a new number, claim, or brand fact not "
    "already given to you.\n\n"
    "PROMPT-HYGIENE RULES -- a live run once leaked every one of these straight into a client-facing "
    "image (the literal words 'UII Label', the literal words 'Montserrat SemiBold', an internal series id "
    "like '4beb6d95640a' printed as a visible watermark, and a headline wrapped in visible quotation "
    "marks), so follow all of these without exception:\n"
    "(a) NEVER name a font or typeface, and NEVER use a style adjective or an element-type noun ('label', "
    "'pill', 'badge', 'watermark', 'UI text', 'sample text', 'placeholder', 'lorem ipsum') as renderable "
    "content in your RENDER text -- those words belong ONLY in the STYLE section (already written for you) "
    "and must never appear inside a <<...>> span. Describe type style visually instead: 'a high-contrast "
    "modern serif italic', 'a clean geometric sans-serif' -- never by font name.\n"
    "(b) Every decorative element (icon, dot, shape, badge, checkbox, pill) you describe must either "
    "carry SPECIFIED text content you give it verbatim inside <<...>>, or be explicitly described as "
    "containing no text at all, e.g. 'a small solid teal accent dot, no text on it'. Never leave a "
    "decorative element's text ambiguous -- an image model fills an ambiguous label with invented filler "
    "words.\n"
    "(c) Every exact-text directive uses exactly this pattern: 'the text <<...>> appears' with the "
    "literal required text inside the << >> markers, followed by 'rendered without surrounding "
    "quotation marks' -- quotation marks are a writing convention in YOUR text, never something the "
    "generated image itself should visibly show around the text.\n"
    "(d) NEVER render the internal series/consistency identifier, a run id, or any other internal token "
    "as visible on-image text or a watermark -- it is metadata for our own tracing only and must never "
    "appear inside a <<...>> span.\n\n"
    "LOGOS -- when the slide's own text or the scene direction (image_brief) names a real tool or "
    "platform (Claude, Claude Code, n8n, LinkedIn, ChatGPT, Google Maps, Figma, etc.), direct the image to "
    "render THAT tool's actual, recognizable logo mark in or near the proof element -- real, accurately "
    "depicted third-party logos are WANTED here, never suppressed or genericized. The only identity/"
    "content constraints that remain: no identifiable real individuals or celebrity likenesses -- "
    "SYNTHETIC, non-identifiable people (including a clearly visible face, e.g. a phone-camera selfie or "
    "talking-head framing) are explicitly PERMITTED, and for a photoreal person-UGC generation mode are "
    "expected -- no NSFW content, and never a fake screenshot of HypeDigitaly's own product UI.\n\n"
    "GENERATION MODE AND REGISTER -- every call names one generation mode and its register in the user "
    "message, plus that mode's own composition directive; follow the directive precisely. A "
    "'photographic_ugc' register means a genuine photorealistic photograph ground -- never a flat "
    "cream/paper editorial card, never a Didone-style serif display -- with plain white sans-serif "
    "sticker-style text; an 'editorial' or 'hype' register keeps the existing flat typographic-card "
    "composition. Never blend one register's own directives into an image crafted under a different "
    "register.\n\n"
    "PROOF-VISUAL RELEVANCE -- choose a proof visual (screenshot-style inset, chart, UI mock) that depicts "
    "THIS slide's own sentence, never a generic default. State the causal link between the proof visual "
    "and the slide's sentence in the 'relevance' field of your JSON output, one line. Calendar/booking "
    "imagery and inbox/contact-list imagery are BANNED unless the slide's own text explicitly mentions "
    "scheduling, booking, or inbox/email. Any inset/proof screenshot carries at most "
    f"{MAX_INSET_STRINGS} short literal text strings, each {MAX_INSET_STRING_WORDS} words or fewer, every "
    "one of them enumerated explicitly in its own <<...>> span at badge scale -- never a dense table or "
    "paragraph of text inside an inset.\n\n"
    "ASPECT RATIO -- never state an aspect ratio, an orientation word (square/portrait/landscape/"
    "widescreen), or a ratio like '1:1' or '1.91:1' anywhere in your text; the aspect ratio is enforced "
    "separately as an API request parameter and stating one here can only create a contradiction."
)


@dataclass
class CraftedImage:
    slot: str  # "hero" | "slide_01" | "slide_02" | ...
    prompt: str
    # W8-10 point 4: N-D's own one-line statement of the causal link between
    # the chosen proof visual and this slide's sentence -- persisted here
    # for audit (media_prompts.yaml), never sent to the image model itself.
    relevance: str | None = None

    def to_yaml_dict(self) -> dict[str, Any]:
        return {"slot": self.slot, "prompt": self.prompt, "relevance": self.relevance}


@dataclass
class CraftedPromptSet:
    asset_id: str
    images: list[CraftedImage] = field(default_factory=list)
    unavailable: bool = False
    unavailable_reason: str | None = None
    gate_blocked: bool = False
    gate_failing_spans: list[str] = field(default_factory=list)
    # W8-9 Q4: the archetype/register this set was crafted against (see
    # ``pick_archetype_register``) -- carried alongside the prompts
    # themselves so a later N-E vision-QA call has the SAME expectation the
    # crafter used, without recomputing it (and without re-reading the style
    # guide / viral playbook a second time).
    archetype: str | None = None
    register: str | None = None
    # W8-10 Phase 8: the generation mode this set was crafted against (see
    # ``pick_generation_mode``) -- ``None`` whenever no ``visual_profile``
    # was available (the pre-Phase-8/legacy path). Threaded to N-E vision-QA
    # the same way ``archetype``/``register`` already are, so the QA rubric
    # can branch per mode without recomputing anything.
    mode: str | None = None
    # W8-10: the internal series/consistency token, carried as METADATA only
    # -- never rendered as visible text on any image (module docstring).
    # Kept here purely for trace/audit round-tripping.
    series_token: str | None = None

    def hero_prompt(self) -> str | None:
        """The single-image path's prompt, when one exists — ``None`` for a
        carousel asset (which carries ``slide_NN`` slots instead) or an
        unavailable/gate-blocked set."""
        if self.unavailable or self.gate_blocked:
            return None
        for image in self.images:
            if image.slot == "hero":
                return image.prompt
        return None

    def usable(self) -> bool:
        return not self.unavailable and not self.gate_blocked and bool(self.images)

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "unavailable": self.unavailable,
            "unavailable_reason": self.unavailable_reason,
            "gate_blocked": self.gate_blocked,
            "gate_failing_spans": self.gate_failing_spans,
            "archetype": self.archetype,
            "register": self.register,
            "mode": self.mode,
            "series_token": self.series_token,
            "images": [i.to_yaml_dict() for i in self.images],
        }


def _from_yaml_dict(data: dict[str, Any]) -> CraftedPromptSet:
    return CraftedPromptSet(
        asset_id=str(data.get("asset_id", "")),
        images=[
            CraftedImage(
                slot=str(i.get("slot", "")), prompt=str(i.get("prompt", "")), relevance=i.get("relevance"),
            )
            for i in (data.get("images") or [])
            if isinstance(i, dict)
        ],
        unavailable=bool(data.get("unavailable", False)),
        unavailable_reason=data.get("unavailable_reason"),
        gate_blocked=bool(data.get("gate_blocked", False)),
        gate_failing_spans=list(data.get("gate_failing_spans") or []),
        archetype=data.get("archetype"),
        register=data.get("register"),
        mode=data.get("mode"),
        series_token=data.get("series_token"),
    )


def write_media_prompts(run_dir: Path, prompt_sets: dict[str, CraftedPromptSet]) -> Path:
    path = Path(run_dir) / MEDIA_PROMPTS_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"version": 1, "assets": {asset_id: ps.to_yaml_dict() for asset_id, ps in prompt_sets.items()}}
    path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def load_media_prompts(run_dir: Path) -> dict[str, CraftedPromptSet]:
    """Returns ``{}`` (never ``None``) when the file is missing/malformed —
    the resume-round-trip caller always gets a dict it can safely check
    membership on."""
    path = Path(run_dir) / MEDIA_PROMPTS_FILENAME
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return {}
    assets = data.get("assets") or {}
    if not isinstance(assets, dict):
        return {}
    return {str(k): _from_yaml_dict(v) for k, v in assets.items() if isinstance(v, dict)}


# ---------------------------------------------------------------------------
# STYLE section + archetype/register pick.
# ---------------------------------------------------------------------------


# W8-10 Phase 8: the register whose ground is a genuine photograph, never
# the flat editorial typography card -- see ``_build_style_section``'s
# branch below and ``config/style_guide.yaml``'s ``visual_registers`` entry
# of the same key.
PHOTOGRAPHIC_REGISTER = "photographic_ugc"


def _build_style_section(
    *,
    style_guide: dict[str, Any] | None,
    archetype: str | None,
    register: str | None,
    handle: str,
    visual_profile: Any | None = None,
) -> str:
    """Build the literal STYLE section text ONCE per asset, deterministically,
    from Python -- never delegated to the LLM (module docstring). Every
    slide/hero image of one ``craft_prompts`` call is prefixed with the
    EXACT SAME string returned here, which is what makes cross-slide series
    consistency (W8-10 point 8: same background hex, same typeface family,
    same handle corner, same margins) a construction guarantee rather than
    an LLM-repeatability hope.

    W8-10 Phase 8: branches on ``register`` so the editorial register's own
    forced brand palette/typeface never leaks onto a photographic ground —
    the trend corpus's winning creatives are 96% real photographs with the
    photo's own natural colors, never the HD indigo/teal gradient forced
    onto a card. ``visual_profile`` (optional, additive), when given and
    ``register == PHOTOGRAPHIC_REGISTER``, adds one deterministic sentence
    naming this theme's own observed ``dominant_environment`` (leaning
    aspirational when ``aspiration_signal_rate`` is high) — the same value
    for every slide of this one asset, so it never breaks series
    consistency."""
    brand = (style_guide or {}).get("brand") or {}
    palette = brand.get("palette_primary_gradient") or []
    typeface = brand.get("typeface", "")
    registers = (style_guide or {}).get("visual_registers") or {}
    register_block = registers.get(register) if register else None
    archetype_desc = None
    for entry in (style_guide or {}).get("visual_archetypes") or []:
        if isinstance(entry, dict) and entry.get("key") == archetype:
            archetype_desc = entry.get("desc")
            break

    layout = (style_guide or {}).get("layout") or {}
    margin_percent = layout.get("margin_percent", DEFAULT_MARGIN_PERCENT)
    handle_corner = layout.get("handle_corner", DEFAULT_HANDLE_CORNER)

    is_photographic = register == PHOTOGRAPHIC_REGISTER

    parts: list[str] = []
    if is_photographic:
        # W8-10 Phase 8 point 1: never force the brand indigo/teal gradient
        # (or the brand's own display typeface) onto a photographic ground —
        # the photo's own natural, real-world colors and the mode's own
        # plain sticker-text style (from ``register_block`` below) govern.
        parts.append(
            "no forced brand color palette here -- this is a real photograph and its own natural, "
            "real-world colors dominate; an accent color is optional and only used if it fits the "
            "scene naturally"
        )
    else:
        if palette:
            parts.append(f"background/palette hex: {', '.join(palette)}")
        if typeface:
            parts.append(
                f"body typeface family (for your reference only, NEVER render this word as text): {typeface} "
                "-- describe it visually in the RENDER section instead, e.g. 'a clean geometric sans-serif'"
            )
    if archetype:
        parts.append(f"visual archetype '{archetype}'" + (f" ({archetype_desc})" if archetype_desc else ""))
    if isinstance(register_block, dict):
        parts.append(
            f"register '{register}': ground={register_block.get('ground')}; type={register_block.get('type')}; "
            f"accent={register_block.get('accent')}; mood={register_block.get('mood')}"
        )
    if is_photographic and visual_profile is not None:
        environment = str(getattr(visual_profile, "dominant_environment", "") or "").strip()
        if environment and environment != "unknown":
            aspirational = float(getattr(visual_profile, "aspiration_signal_rate", 0.0) or 0.0) >= 0.3
            parts.append(
                f"photograph environment: {environment}"
                + (" -- lean aspirational/high-end for this setting" if aspirational else "")
            )
    # W8-10: spelled out as "N percent", never "N%" -- the claim gate's own
    # number-claim detector (claim_gate._NUMBER_PATTERN) matches any bare
    # ``\d+%`` as an unmatched brand metric claim, and this deterministic,
    # never-changing layout instruction is not a claim about anything.
    parts.append(f"margins {margin_percent} percent on every side -- all text, insets, and the handle stay fully inside them")
    parts.append(f"the handle {handle} appears small and subtle in the {handle_corner} corner")
    parts.append(
        "every decorative element (icon, dot, shape, badge, pill) carries either the exact literal text "
        "given to it in the RENDER section below or no text at all -- never an invented word, and never "
        "the words 'label', 'pill', 'badge', 'watermark', or a font/style name as literal on-image content"
    )
    body = "; ".join(parts) if parts else "no style guide available -- use clean, on-brand, professional composition"
    return f"{STYLE_LABEL} {body}."


def _legacy_pick_archetype_register(
    *,
    destination: str,
    style_guide: dict[str, Any] | None,
    theme_playbook: Any | None,
    asset_index: int = 0,
) -> tuple[str | None, str]:
    """W8-10 point 7 (pre-Phase-8 behavior, preserved verbatim): deterministic
    rotation over this run's observed archetypes (deduplicated, order
    preserved), falling back to the style guide's own per-platform default
    archetype list when the playbook named none. ``asset_index`` (a
    caller-supplied position of this asset within its run — 0, 1, 2, ...)
    selects ``candidates[asset_index % len(candidates)]`` so that two assets
    crafted with CONSECUTIVE indices never land on the same archetype (as
    long as more than one candidate is known) -- pure modular arithmetic, no
    randomness, fully reproducible across runs. Register is a fixed,
    deterministic default (``editorial``). This is the full-backward-
    compatibility path: it is used whenever ``theme_playbook`` carries no
    ``visual_profile`` (an old playbook, a fixture, or a theme text-only run
    never linked to any analyzed image) AND as the archetype-only fallback
    for the ``designed_card`` generation mode (W8-10 Phase 8), whose own
    :class:`ModeSpec` deliberately names no fixed archetype so this same
    rotation keeps choosing among the theme's own editorial/hype
    archetypes."""
    candidates: list[str] = []
    if theme_playbook is not None:
        seen = getattr(theme_playbook, "visual_archetypes_seen", None) or []
        for entry in seen:
            key = str(entry)
            if key not in candidates:
                candidates.append(key)
    if not candidates and style_guide:
        platform_block = (style_guide.get("platforms") or {}).get(destination) or {}
        defaults = (platform_block.get("visual") or {}).get("default_archetypes") or []
        for entry in defaults:
            key = str(entry)
            if key not in candidates:
                candidates.append(key)
    archetype = candidates[asset_index % len(candidates)] if candidates else None
    return archetype, "editorial"


# ---------------------------------------------------------------------------
# W8-10 Phase 8 — generation-mode registry. The fidelity-trace audit found
# the trend corpus's actual winning distribution (96% photoreal photo
# ground, 92% sticker text, 71% real app icons/logos, 50% real person, 0%
# editorial typography cards) is the near-exact INVERSION of what the
# pre-Phase-8 pipeline ever generated (register hardcoded ``"editorial"``,
# only two flat typographic registers existed at all). Each mode maps to a
# register (see ``config/style_guide.yaml``'s ``visual_registers``) and a
# composition directive threaded into the RENDER-section brief (never the
# shared ``SYSTEM_PROMPT``, which stays generic across every mode/register).
# ``designed_card`` is the pre-Phase-8 editorial/hype card path, unchanged,
# and is the universal fallback whenever no visual evidence favors anything
# else.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ModeSpec:
    register: str
    # ``None`` means "no fixed archetype for this mode" -- only
    # ``designed_card`` uses this, and it defers to
    # ``_legacy_pick_archetype_register``'s own rotation instead (see
    # ``pick_generation_mode``).
    archetype: str | None
    composition_directive: str


GENERATION_MODES: dict[str, ModeSpec] = {
    "photoreal_lifestyle_sticker": ModeSpec(
        register=PHOTOGRAPHIC_REGISTER,
        archetype="ugc-photo-caption",
        composition_directive=(
            "Full-bleed photorealistic lifestyle/desk/aspirational photograph as the ENTIRE ground -- "
            "never a flat color card. Composite one oversized, real, recognizable app icon of the named "
            "tool near the top-left of the frame (unless the scene direction states a different position). "
            "Overlay 1-3 short lines of plain white sans-serif sticker-style text with a soft drop shadow, "
            "TikTok caption style -- never a serif display face, never a colored card behind the text. When "
            "the copy is a numbered listicle, prefix the on-image text with that item's own number followed "
            "by a period (e.g. '3.')."
        ),
    ),
    "photoreal_person_ugc": ModeSpec(
        register=PHOTOGRAPHIC_REGISTER,
        archetype="person-plus-stickers",
        composition_directive=(
            "Photorealistic image of a SYNTHETIC, non-identifiable person in a phone-camera talking-head "
            "or selfie framing -- a visible face is expected and welcome for this mode, but never a real, "
            "identifiable, or celebrity likeness. Layer a heavy block of plain white sans-serif "
            "sticker-style text with a soft drop shadow over the lower or upper third of the frame, TikTok "
            "caption style."
        ),
    ),
    "aspirational_lifestyle_scene": ModeSpec(
        register=PHOTOGRAPHIC_REGISTER,
        archetype="aspirational-lifestyle-scene",
        composition_directive=(
            "A luxury, aspirational real-world environment (car interior, poolside, penthouse window, "
            "high-end workspace) does the persuasion visually -- the environment itself is the message. "
            "Minimal on-image text: at most one short line, if any."
        ),
    ),
    "live_app_ui": ModeSpec(
        register="editorial",
        archetype="screenshot-as-proof",
        composition_directive=(
            "Render the REAL, current, accurately branded user interface of the named app or tool "
            "(including its real logo/wordmark) as the actual proof surface -- a genuine-looking product "
            "screenshot, never a generic or unbranded mockup. Depict only the third-party tool's own UI, "
            "never a fake screenshot of HypeDigitaly's or HypeLead's own product."
        ),
    ),
    "native_caption_frame": ModeSpec(
        register=PHOTOGRAPHIC_REGISTER,
        archetype="native-caption-frame",
        composition_directive=(
            "A single video-frame look (native, unposed, phone-shot feel) with exactly ONE short, "
            "centered, burned-in white caption line at the lower third, video-subtitle style -- no other "
            "on-image text anywhere in the frame."
        ),
    ),
    "meme_reaction_split": ModeSpec(
        register=PHOTOGRAPHIC_REGISTER,
        archetype="meme-reaction-split",
        composition_directive=(
            "Split the frame horizontally: a real app/tool screenshot in the top half, a synthetic "
            "non-identifiable person's reaction-style photo in the bottom half. At most one short plain "
            "white sticker-style caption line."
        ),
    ),
    "flat_lay_product_grid": ModeSpec(
        register=PHOTOGRAPHIC_REGISTER,
        archetype="flat-lay-product-grid",
        composition_directive=(
            "An overhead flat-lay photograph of devices and desk props (phone, laptop, notebook, coffee) "
            "arranged neatly, with one real app icon composited in and a single short benefit line in "
            "plain white sticker-style text."
        ),
    ),
    "designed_card": ModeSpec(
        register="editorial",
        archetype=None,
        composition_directive=(
            "The existing designed typographic-card composition for this archetype/register -- flat "
            "ground, no photographic background."
        ),
    ),
}

DEFAULT_MODE = "designed_card"


def _candidate_modes_from_visual_profile(visual_profile: Any) -> list[str]:
    """W8-10 Phase 8: this theme's own "top modes" for the asset-index
    rotation to rotate over, deterministically derived from
    ``analysis.VisualProfile``'s already-computed, views-weighted fields —
    never a flat archetype list, and never randomness. ``recommended_generation_mode``
    always leads; ``DEFAULT_MODE`` always trails (as a rotation safety net,
    and because it is never wrong for any theme). Every threshold here is a
    plain module constant, not configurable this round — see the task
    report for that note."""
    primary = str(getattr(visual_profile, "recommended_generation_mode", DEFAULT_MODE) or DEFAULT_MODE)
    if primary not in GENERATION_MODES:
        primary = DEFAULT_MODE
    candidates: list[str] = [primary]

    def add(mode: str) -> None:
        if mode not in candidates:
            candidates.append(mode)

    ground_mix = getattr(visual_profile, "ground_mix", None) or {}
    text_mix = getattr(visual_profile, "text_treatment_mix", None) or {}
    person_rate = float(getattr(visual_profile, "person_rate", 0.0) or 0.0)
    logo_rate = float(getattr(visual_profile, "logo_rate", 0.0) or 0.0)
    aspiration_rate = float(getattr(visual_profile, "aspiration_signal_rate", 0.0) or 0.0)
    numbering_rate = float(getattr(visual_profile, "numbering_rate", 0.0) or 0.0)
    dominant_text_density = str(getattr(visual_profile, "dominant_text_density", "") or "")
    photoreal_share = float(ground_mix.get("photoreal", 0.0) or 0.0)
    sticker_share = float(text_mix.get("sticker", 0.0) or 0.0)
    screenshot_share = float(ground_mix.get("app_screenshot", 0.0) or 0.0)

    if aspiration_rate >= 0.3:
        add("aspirational_lifestyle_scene")
    if photoreal_share >= 0.3 and numbering_rate < 0.3 and dominant_text_density in ("light", "none"):
        add("native_caption_frame")
    if screenshot_share >= 0.2 and person_rate >= 0.2:
        add("meme_reaction_split")
    if photoreal_share >= 0.3 and logo_rate >= 0.3:
        add("flat_lay_product_grid")
    if screenshot_share >= 0.3:
        add("live_app_ui")
    if photoreal_share >= 0.3 and sticker_share >= 0.3:
        add("photoreal_person_ugc" if person_rate >= 0.4 else "photoreal_lifestyle_sticker")
    add(DEFAULT_MODE)
    return candidates


def pick_generation_mode(
    *,
    destination: str,
    style_guide: dict[str, Any] | None,
    theme_playbook: Any | None,
    asset_index: int = 0,
) -> tuple[str | None, str | None, str]:
    """W8-10 Phase 8: the mode-aware successor to the old flat archetype
    rotation. Returns ``(mode, archetype, register)``.

    When ``theme_playbook.visual_profile`` is present (this run's own
    deterministic per-theme aggregate, ``analysis.compute_visual_profile``),
    ``asset_index`` rotates over this theme's own "top modes"
    (:func:`_candidate_modes_from_visual_profile`) instead of a flat
    archetype list — ``recommended_generation_mode`` always leads. The
    ``designed_card`` mode carries no fixed archetype of its own; it defers
    to the same legacy rotation used for the no-visual-profile path, keyed
    by the SAME ``asset_index``, so consecutive ``designed_card`` picks
    still vary across the theme's own archetypes.

    When no ``visual_profile`` is available (an old playbook, a fixture, or
    a theme this run never linked any analyzed image to), this is a pure
    pass-through to :func:`_legacy_pick_archetype_register` — ``mode`` is
    ``None`` and register is the fixed ``"editorial"`` default, exactly the
    pre-Phase-8 behavior, for full backward compatibility."""
    visual_profile = getattr(theme_playbook, "visual_profile", None) if theme_playbook is not None else None
    if visual_profile is None:
        archetype, register = _legacy_pick_archetype_register(
            destination=destination, style_guide=style_guide, theme_playbook=theme_playbook, asset_index=asset_index,
        )
        return None, archetype, register

    modes = _candidate_modes_from_visual_profile(visual_profile)
    mode = modes[asset_index % len(modes)]
    spec = GENERATION_MODES.get(mode) or GENERATION_MODES[DEFAULT_MODE]
    if spec.archetype is None:
        archetype, _legacy_register = _legacy_pick_archetype_register(
            destination=destination, style_guide=style_guide, theme_playbook=theme_playbook, asset_index=asset_index,
        )
    else:
        archetype = spec.archetype
    return mode, archetype, spec.register


def pick_archetype_register(
    *,
    destination: str,
    style_guide: dict[str, Any] | None,
    theme_playbook: Any | None,
    asset_index: int = 0,
) -> tuple[str | None, str]:
    """Backward-compatible two-tuple wrapper over :func:`pick_generation_mode`
    for callers that only ever needed ``(archetype, register)`` — see that
    function's own docstring for the full mode-aware behavior this now
    delegates to."""
    _mode, archetype, register = pick_generation_mode(
        destination=destination, style_guide=style_guide, theme_playbook=theme_playbook, asset_index=asset_index,
    )
    return archetype, register


def series_token_for(run_id: str, cluster_key: str) -> str:
    return hashlib.sha256(f"{run_id}:{cluster_key}".encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Crafted-prompt validation (W8-9 point 1c, extended W8-10 point 5) -- a
# second, deterministic line of defense independent of ``llm.LlmClient``'s
# own finish_reason check: a prompt that LOOKS complete (parses fine as
# JSON, no truncation reported) can still be cut off mid-sentence, silently
# drop the exact text it was supposed to embed, leak prompt scaffolding as
# visible content, or blow past a sane rendered-body length. Never guesses a
# fix -- an invalid prompt fails closed (module docstring: that slot falls
# back to ``compose_prompt`` for a hero, or degrades the whole set for a
# carousel, since there is no deterministic per-slide composer -- see
# ``craft_prompts``).
# ---------------------------------------------------------------------------

MIN_PROMPT_CHARS = 20
MAX_PROMPT_CHARS = 6000
MAX_BODY_WORDS = 28
_ENDS_IN_PUNCTUATION_RE = re.compile(r'[.!?][)"\']?\s*$')
_TWELVE_HEX_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{12}(?![0-9a-f])")
_FONT_NAME_RE = re.compile(r"Montserrat|Didone|SemiBold", re.IGNORECASE)
_QUOTED_SPAN_RE = re.compile(r"<<(.*?)>>", re.DOTALL)
_ASPECT_RATIO_RE = re.compile(r"\b\d{1,2}(?:\.\d{1,2})?\s*:\s*\d{1,2}\b")
_ORIENTATION_WORD_RE = re.compile(r"\b(square|portrait|landscape|widescreen)\b", re.IGNORECASE)
# W8-10 Phase 8 point 4: a photographic-register prompt must never carry an
# editorial-register directive (the exact wrong-register leak the fidelity
# trace found: 100% of a prior run's generated set inverted the winning
# corpus's own style). ``config/style_guide.yaml``'s ``photographic_ugc``
# register text deliberately never uses these words itself (see
# ``_build_style_section``'s photographic branch), so any match here is
# always a genuine cross-register leak, never a false positive on our own
# text.
_EDITORIAL_LEAK_RE = re.compile(r"didone|cream[- ]?paper|bone/cream", re.IGNORECASE)


def _render_section_text(prompt: str) -> str:
    idx = prompt.find(RENDER_LABEL)
    return prompt[idx + len(RENDER_LABEL) :] if idx != -1 else prompt


def validate_crafted_prompt(
    prompt: str,
    *,
    required_texts: list[str] | None = None,
    body_text: str | None = None,
    max_body_words: int = MAX_BODY_WORDS,
    register: str | None = None,
) -> str | None:
    """Returns a human-readable failure reason, or ``None`` when ``prompt``
    passes every check: proper closing punctuation (never cut off
    mid-sentence — the live-run defect this exists for: a slide prompt
    truncated at "platform built for" was submitted to the image model
    as-is), length sanity, complete verbatim inclusion of every required
    on-image text fragment, a rendered body under ``max_body_words`` (W8-10
    point 5 -- the live-run defect: corrupted, run-on body copy at display
    size), both STYLE/RENDER section labels present, no internal 12-char
    hex token leaking into the RENDER section, no font name inside a
    ``<<...>>`` renderable-text span, no aspect-ratio/orientation language
    anywhere (W8-10 point 6 -- never contradict the API's own
    ``requested_aspect`` parameter, which this module has no visibility
    into; the safe fix is to never say one at all), and — W8-10 Phase 8,
    additive — when ``register`` is given as ``PHOTOGRAPHIC_REGISTER``, no
    editorial-register directive (Didone/cream-paper) anywhere in the
    prompt (a wrong-register leak; see :data:`_EDITORIAL_LEAK_RE`).
    ``register`` defaults to ``None``, which skips this last check entirely
    — existing callers that never named a register are unaffected."""
    text = (prompt or "").strip()
    if len(text) < MIN_PROMPT_CHARS:
        return f"prompt too short ({len(text)} chars, minimum {MIN_PROMPT_CHARS})"
    if len(text) > MAX_PROMPT_CHARS:
        return f"prompt too long ({len(text)} chars, maximum {MAX_PROMPT_CHARS})"
    if not _ENDS_IN_PUNCTUATION_RE.search(text):
        return "prompt does not end in proper punctuation (looks cut off mid-sentence)"
    for required in required_texts or []:
        if required and required not in prompt:
            return f"prompt does not contain the required exact-text segment complete: {required!r}"
    if body_text:
        word_count = len(body_text.split())
        if word_count > max_body_words:
            return f"slide body text is {word_count} words, over the {max_body_words}-word rendered-body cap"
    if STYLE_LABEL not in prompt:
        return "prompt is missing the required STYLE section label"
    if RENDER_LABEL not in prompt:
        return "prompt is missing the required RENDER section label"
    render_section = _render_section_text(prompt)
    hex_match = _TWELVE_HEX_RE.search(render_section)
    if hex_match:
        return (
            f"prompt's RENDER section contains a 12-character hex token {hex_match.group(0)!r} "
            "(looks like an internal series id leaking as visible text)"
        )
    for span in _QUOTED_SPAN_RE.findall(prompt):
        font_match = _FONT_NAME_RE.search(span)
        if font_match:
            return f"prompt has a font name ({font_match.group(0)!r}) inside a <<...>> renderable-text span: {span!r}"
    if _ASPECT_RATIO_RE.search(prompt) or _ORIENTATION_WORD_RE.search(prompt):
        return "prompt states an aspect ratio or orientation word, which must never appear in crafted prompt text"
    if register == PHOTOGRAPHIC_REGISTER:
        leak_match = _EDITORIAL_LEAK_RE.search(prompt)
        if leak_match:
            return (
                f"prompt is registered as {PHOTOGRAPHIC_REGISTER!r} but contains an editorial-register "
                f"directive {leak_match.group(0)!r} (wrong-register leak)"
            )
    return None


def _slide_required_texts(slide: dict[str, str]) -> list[str]:
    return [str(t).strip() for t in (slide.get("title"), slide.get("body")) if str(t or "").strip()]


def _slide_body_text(slide: dict[str, str]) -> str:
    return str(slide.get("body") or "").strip()


# ---------------------------------------------------------------------------
# The crafting call.
# ---------------------------------------------------------------------------


def _looks_like_numbered_listicle(headline: str, slides: list[dict[str, str]] | None) -> bool:
    """Best-effort, deterministic heuristic (W8-10 Phase 8): does this
    asset's own copy already carry a bare number, the way a "5 ways to..."
    or a numbered-slide carousel would? Used only to decide whether to tell
    the crafter to prefix on-image text with its own item number when this
    theme's ``numbering_rate`` is high — never a hard requirement, and never
    invents a number itself."""
    text = headline or ""
    if slides:
        text += " " + " ".join(str(s.get("title", "")) for s in slides)
    return bool(re.search(r"\b\d+\b", text))


def _visual_profile_brief_line(
    *,
    visual_profile: Any,
    headline: str,
    slides: list[dict[str, str]] | None,
    analyzed_items: list[Any] | None,
) -> str:
    """W8-10 Phase 8: thread this theme's own deterministic visual evidence
    into the RENDER-section brief — never asked of the LLM as a NEW fact,
    only handed to it as grounding for the mode's own composition
    directive. ``analyzed_items`` (optional, additive) supplies 1-2 concrete
    per-creative ``summary`` strings as visual references, matched against
    ``visual_profile.evidence_item_ids`` (the theme's own highest-view
    analyzed items) -- omitted entirely when not supplied, which is the
    normal case until a caller wires the full ``ViralPlaybook.analyzed_items``
    list through (see the task report's stages.py note)."""
    parts = [
        f"this theme's winning creatives lean toward dominant text style {getattr(visual_profile, 'dominant_text_style', 'unknown')!r} "
        f"on a {getattr(visual_profile, 'dominant_ground', 'unknown')!r} ground, "
        f"set in {getattr(visual_profile, 'dominant_environment', 'unknown')!r}"
    ]
    numbering_rate = float(getattr(visual_profile, "numbering_rate", 0.0) or 0.0)
    if numbering_rate > 0.5 and _looks_like_numbered_listicle(headline, slides):
        parts.append(
            "this is a numbered listicle and this theme's own winners numbered their slides -- prefix the "
            "on-image text with that item's own number (e.g. '3.')"
        )
    logos_ranked = getattr(visual_profile, "logos_ranked", None) or []
    top_logos = [str(entry.get("name")) for entry in logos_ranked if isinstance(entry, dict) and entry.get("name")][:3]
    if top_logos:
        parts.append(f"when a proof element needs a real tool logo, this theme's own winners actually showed: {', '.join(top_logos)}")
    if analyzed_items:
        evidence_ids = set(getattr(visual_profile, "evidence_item_ids", None) or [])
        matched = [it for it in analyzed_items if getattr(it, "item_id", None) in evidence_ids][:2]
        for item in matched:
            summary = str(getattr(item, "summary", "") or "").strip()
            if summary:
                parts.append(f"winning creative reference in this theme: {summary}")
    return "This theme's own visual evidence (" + "; ".join(parts) + ")."


def craft_prompts(
    *,
    llm_client: LlmClient | None,
    asset_id: str,
    destination: str,
    headline: str,
    caption: str,
    image_brief: str,
    slides: list[dict[str, str]] | None,
    style_guide: dict[str, Any] | None,
    theme_playbook: Any | None,
    series_token: str,
    node_name: str = "prompt_crafter",
    trace: TraceWriter | None = None,
    stage: str = "media",
    asset_index: int = 0,
    # W8-10 Phase 8, additive: this run's per-image analyzed records (the
    # ``analysis.ViralPlaybook.analyzed_items`` atom), used ONLY to pull 1-2
    # concrete ``summary`` strings as visual references into the RENDER
    # brief -- ``None`` (the default, and every existing call site's
    # behavior) simply omits that one sentence. Not yet wired from
    # ``stages.py`` this round (that file is out of scope for this task —
    # see the task report).
    analyzed_items: list[Any] | None = None,
) -> CraftedPromptSet:
    if llm_client is None:
        return CraftedPromptSet(
            asset_id=asset_id, unavailable=True,
            unavailable_reason="LLM disabled or unavailable for this run",
        )

    mode, archetype, register = pick_generation_mode(
        destination=destination, style_guide=style_guide, theme_playbook=theme_playbook, asset_index=asset_index,
    )
    visual_profile = getattr(theme_playbook, "visual_profile", None) if theme_playbook is not None else None
    handle = ((style_guide or {}).get("brand") or {}).get("handle") or "@hypedigitaly"
    style_section = _build_style_section(
        style_guide=style_guide, archetype=archetype, register=register, handle=handle, visual_profile=visual_profile,
    )

    lines: list[str] = [
        f"Destination: {destination}",
        f"Guardrails: {GUARDRAILS}",
    ]
    mode_spec = GENERATION_MODES.get(mode) if mode else None
    if mode_spec is not None:
        lines.append(
            f"Generation mode for this image: {mode} (register={register}). Composition directive -- "
            f"follow it precisely: {mode_spec.composition_directive}"
        )
    if visual_profile is not None:
        lines.append(
            _visual_profile_brief_line(
                visual_profile=visual_profile, headline=headline, slides=slides, analyzed_items=analyzed_items,
            )
        )

    # W8-10 root-cause fix: ``image_brief`` now reaches BOTH branches -- the
    # carousel branch used to drop it entirely, which is why a copywriter's
    # own request to show a real tool's logo never reached N-D for a
    # carousel asset.
    if slides:
        lines.append(
            "Scene direction shared by this whole asset (the copywriter's own request for what these "
            f"images should show, including any tool/logo mentions -- follow it for every slide): {image_brief!r}"
        )
        lines.append(f"This is a carousel of {len(slides)} slides — produce ONE render entry per slide, slide order preserved.")
        lines.append("Slides (render each slide's title + body VERBATIM as the on-image text):")
        for i, slide in enumerate(slides, start=1):
            lines.append(
                f"- slide_{i:02d} (role={slide.get('role', 'body')}): "
                f"title={slide.get('title', '')!r} body={slide.get('body', '')!r}"
            )
        schema_hint = (
            'Schema: {"images": [{"slot": "slide_01", "render": string, "relevance": string}, ...]} — exactly '
            "one entry per slide, in slide order, slot named slide_01..slide_NN (zero-padded two digits); "
            "'render' is ONLY the RENDER-section text (never repeat the STYLE section); 'relevance' states "
            "the proof visual's causal link to that slide's own sentence."
        )
    else:
        lines.append(f"Headline to render verbatim if it reads naturally as an overlay: {headline!r}")
        lines.append(
            "Scene direction (gate-passed image_brief -- the copywriter's own request for what the image "
            f"should show, including any tool/logo mentions; follow it): {image_brief!r}"
        )
        if caption:
            lines.append(f"Caption context (for tone only — do not render this text on the image): {caption!r}")
        schema_hint = (
            'Schema: {"images": [{"slot": "hero", "render": string, "relevance": string}]} — \'render\' is ONLY '
            "the RENDER-section text (never repeat the STYLE section); 'relevance' states the proof visual's "
            "causal link to the headline/scene."
        )

    user_content = "\n".join(lines)
    try:
        data = llm_client.call_json(
            node_name, system=SYSTEM_PROMPT, user_parts=user_content, schema_hint=schema_hint,
            purpose=f"N-D image-prompt crafter — {asset_id}",
        )
    except LlmError as exc:
        return CraftedPromptSet(asset_id=asset_id, unavailable=True, unavailable_reason=f"{type(exc).__name__}: {exc}")

    is_carousel = bool(slides)
    required_texts_by_slot: dict[str, list[str]] = {}
    body_by_slot: dict[str, str] = {}
    if slides:
        for i, slide in enumerate(slides, start=1):
            slot = f"slide_{i:02d}"
            required_texts_by_slot[slot] = _slide_required_texts(slide)
            body_by_slot[slot] = _slide_body_text(slide)

    images_raw = data.get("images")
    candidates: list[tuple[str, str, str | None]] = []
    if isinstance(images_raw, list):
        for item in images_raw:
            if isinstance(item, dict) and item.get("slot") and item.get("render"):
                relevance = item.get("relevance")
                candidates.append((str(item["slot"]), str(item["render"]), str(relevance) if relevance else None))

    images: list[CraftedImage] = []
    invalid_reasons: list[str] = []
    for slot, render_text, relevance in candidates:
        full_prompt = f"{style_section}\n\n{RENDER_LABEL} {render_text}"
        reason = validate_crafted_prompt(
            full_prompt, required_texts=required_texts_by_slot.get(slot), body_text=body_by_slot.get(slot),
            register=register,
        )
        if reason:
            invalid_reasons.append(f"{slot}: {reason}")
        else:
            images.append(CraftedImage(slot=slot, prompt=full_prompt, relevance=relevance))

    if invalid_reasons:
        if trace is not None:
            trace.decision(
                stage,
                decision=f"N-D crafted prompt(s) for {asset_id} failed validation: {'; '.join(invalid_reasons)}",
                rule="W8-9/W8-10 point 1c/5: an invalid crafted prompt is never submitted — hero falls back to "
                "compose_prompt, a carousel with any invalid slide degrades its whole set",
            )
        if is_carousel:
            # No deterministic per-slide composer exists (module docstring)
            # -- one invalid slide degrades the WHOLE set rather than
            # shipping a carousel with a slot silently missing or, worse,
            # mis-numbered against the copy asset's own slide list.
            return CraftedPromptSet(
                asset_id=asset_id, unavailable=True,
                unavailable_reason=f"invalid crafted prompt(s): {'; '.join(invalid_reasons)}",
            )
        # Hero: dropping the one invalid candidate (if any) below naturally
        # falls through to "no usable image prompts" -> unavailable, which
        # is this module's own signal for the caller to fall back to
        # ``compose_prompt(image_brief)`` (media_gen.plan_media_assets).

    if not images:
        return CraftedPromptSet(asset_id=asset_id, unavailable=True, unavailable_reason="crafter returned no usable image prompts")
    return CraftedPromptSet(
        asset_id=asset_id, images=images, archetype=archetype, register=register, mode=mode, series_token=series_token,
    )


def gate_check_prompts(
    prompt_set: CraftedPromptSet, *, snapshot: ClaimSnapshot, hard_excludes: dict[str, ResolvedList] | None
) -> CraftedPromptSet:
    """Run the deterministic claim gate over every crafted prompt's text,
    combined (module docstring: "cheap and safe"). The synthetic
    ``caption=AI_DISCLOSURE_LINE`` sidesteps the gate's disclosure-floor
    check, which is a caption-surface requirement that does not apply to an
    image-generation instruction; the actual prompt text is checked via
    ``image_brief``, which carries every other deterministic check (price/
    number/superlative/entity/therapeutic)."""
    if prompt_set.unavailable or not prompt_set.images:
        return prompt_set
    combined = " ".join(image.prompt for image in prompt_set.images)
    verdict = run_claim_gate(
        headline="", caption=AI_DISCLOSURE_LINE, image_brief=combined, snapshot=snapshot, hard_excludes=hard_excludes,
    )
    failing = [
        f"{s.field_name}: {s.kind} '{s.text}' — {s.reason}" for s in verdict.failing_spans if s.kind != "disclosure_missing"
    ]
    if not failing:
        return prompt_set
    prompt_set.gate_blocked = True
    prompt_set.gate_failing_spans = failing
    return prompt_set
