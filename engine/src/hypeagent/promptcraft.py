"""N-D Image-Prompt Crafter (W8-9 Q3c; FLOW_MAP.md's ``prompt craft`` row,
folded into the ``media`` stage's own invocation rather than a separate
canonical stage — it sits between the claim gate and image generation for
exactly the assets the gate already passed).

``craft_prompts`` takes one gate-passed copy asset (headline/caption/
image_brief, plus per-slide title/body for a carousel) and produces the
FULL generation prompt(s) Nano Banana 2 will receive: one ``hero`` prompt
for a single-image destination, or one ``slide_NN`` prompt per slide for a
carousel — every carousel prompt sharing one style-token block (exact
palette hex, register, texture wording) for cross-slide visual consistency,
and every prompt embedding its slide's exact gate-passed text to render
verbatim plus the brand handle and the two guardrails that survive W8-9:
no identifiable real person/celebrity likeness, no NSFW content. **The old
no-text/no-logo/no-people/no-product-depiction constraints
(``media_gen._NEGATIVE_CONSTRAINTS``) are DEAD for this path per W8-9 — do
not re-add them here.**

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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from hypeagent.brand_truth import ClaimSnapshot
from hypeagent.claim_gate import run_claim_gate
from hypeagent.config_load import ResolvedList
from hypeagent.copy_gen import AI_DISCLOSURE_LINE
from hypeagent.llm import LlmClient, LlmError

MEDIA_PROMPTS_FILENAME = "media_prompts.yaml"

# The two guardrails that survive W8-9 (module docstring) — deliberately NOT
# the old no-text/no-logo/no-people/no-product-depiction list.
GUARDRAILS = "no identifiable real person or celebrity likeness in the image; no NSFW content"

SYSTEM_PROMPT = (
    "You are the Image-Prompt Crafter (N-D) for HypeDigitaly's AI-agency social content pipeline "
    "(FLOW_MAP.md node N-D). You write the EXACT image-generation prompt(s) a text-to-image model "
    "will receive. Embed the given gate-passed text VERBATIM so it renders correctly in the final "
    "image — never paraphrase it, never invent a new number, claim, or brand fact not already given "
    "to you. Every prompt must read as a single natural-language generation instruction once "
    "extracted from your JSON response, not as a list of bullet points."
)


@dataclass
class CraftedImage:
    slot: str  # "hero" | "slide_01" | "slide_02" | ...
    prompt: str

    def to_yaml_dict(self) -> dict[str, Any]:
        return {"slot": self.slot, "prompt": self.prompt}


@dataclass
class CraftedPromptSet:
    asset_id: str
    images: list[CraftedImage] = field(default_factory=list)
    unavailable: bool = False
    unavailable_reason: str | None = None
    gate_blocked: bool = False
    gate_failing_spans: list[str] = field(default_factory=list)

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
            "images": [i.to_yaml_dict() for i in self.images],
        }


def _from_yaml_dict(data: dict[str, Any]) -> CraftedPromptSet:
    return CraftedPromptSet(
        asset_id=str(data.get("asset_id", "")),
        images=[
            CraftedImage(slot=str(i.get("slot", "")), prompt=str(i.get("prompt", "")))
            for i in (data.get("images") or [])
            if isinstance(i, dict)
        ],
        unavailable=bool(data.get("unavailable", False)),
        unavailable_reason=data.get("unavailable_reason"),
        gate_blocked=bool(data.get("gate_blocked", False)),
        gate_failing_spans=list(data.get("gate_failing_spans") or []),
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
# Style-token block + archetype/register pick.
# ---------------------------------------------------------------------------


def _style_token_block(*, style_guide: dict[str, Any] | None, archetype: str | None, register: str | None) -> str:
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

    parts: list[str] = []
    if palette:
        parts.append(f"brand palette {', '.join(palette)}")
    if typeface:
        parts.append(f"typeface {typeface}")
    if archetype:
        parts.append(f"visual archetype '{archetype}'" + (f" ({archetype_desc})" if archetype_desc else ""))
    if isinstance(register_block, dict):
        parts.append(
            f"register '{register}': ground={register_block.get('ground')}; type={register_block.get('type')}; "
            f"accent={register_block.get('accent')}; mood={register_block.get('mood')}"
        )
    return "; ".join(parts) if parts else "no style guide available — use clean, on-brand, professional composition"


def pick_archetype_register(
    *, destination: str, style_guide: dict[str, Any] | None, theme_playbook: Any | None
) -> tuple[str | None, str]:
    """Prefer an archetype this run's viral playbook actually observed for
    this theme; fall back to the style guide's own per-platform default
    archetype list. Register is a fixed, deterministic default
    (``editorial``) — a future milestone can make this content-driven."""
    archetype: str | None = None
    if theme_playbook is not None:
        seen = getattr(theme_playbook, "visual_archetypes_seen", None) or []
        if seen:
            archetype = str(seen[0])
    if archetype is None and style_guide:
        platform_block = (style_guide.get("platforms") or {}).get(destination) or {}
        defaults = (platform_block.get("visual") or {}).get("default_archetypes") or []
        if defaults:
            archetype = str(defaults[0])
    return archetype, "editorial"


def series_token_for(run_id: str, cluster_key: str) -> str:
    return hashlib.sha256(f"{run_id}:{cluster_key}".encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# The crafting call.
# ---------------------------------------------------------------------------


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
) -> CraftedPromptSet:
    if llm_client is None:
        return CraftedPromptSet(
            asset_id=asset_id, unavailable=True,
            unavailable_reason="LLM disabled or unavailable for this run",
        )

    archetype, register = pick_archetype_register(destination=destination, style_guide=style_guide, theme_playbook=theme_playbook)
    style_block = _style_token_block(style_guide=style_guide, archetype=archetype, register=register)
    handle = ((style_guide or {}).get("brand") or {}).get("handle") or "@hypedigitaly"

    lines: list[str] = [
        f"Destination: {destination}",
        f"Shared style token block: {style_block}",
        f"Series consistency token (repeat verbatim across every prompt for this asset): {series_token}",
        f"Handle to include, subtly, in the composition: {handle}",
        f"Guardrails: {GUARDRAILS}",
    ]

    if slides:
        lines.append(f"This is a carousel of {len(slides)} slides — produce ONE prompt per slide, slide order preserved.")
        lines.append("Slides (render each slide's title + body VERBATIM as the on-image text):")
        for i, slide in enumerate(slides, start=1):
            lines.append(
                f"- slide_{i:02d} (role={slide.get('role', 'body')}): "
                f"title={slide.get('title', '')!r} body={slide.get('body', '')!r}"
            )
        schema_hint = (
            'Schema: {"images": [{"slot": "slide_01", "prompt": string}, ...]} — exactly one entry per '
            "slide, in slide order, slot named slide_01..slide_NN (zero-padded two digits)."
        )
    else:
        lines.append(f"Headline to render verbatim if it reads naturally as an overlay: {headline!r}")
        lines.append(f"Scene direction (gate-passed image_brief): {image_brief!r}")
        if caption:
            lines.append(f"Caption context (for tone only — do not render this text on the image): {caption!r}")
        schema_hint = 'Schema: {"images": [{"slot": "hero", "prompt": string}]}'

    user_content = "\n".join(lines)
    try:
        data = llm_client.call_json(
            node_name, system=SYSTEM_PROMPT, user_parts=user_content, schema_hint=schema_hint,
            purpose=f"N-D image-prompt crafter — {asset_id}",
        )
    except LlmError as exc:
        return CraftedPromptSet(asset_id=asset_id, unavailable=True, unavailable_reason=f"{type(exc).__name__}: {exc}")

    images_raw = data.get("images")
    images: list[CraftedImage] = []
    if isinstance(images_raw, list):
        for item in images_raw:
            if isinstance(item, dict) and item.get("slot") and item.get("prompt"):
                images.append(CraftedImage(slot=str(item["slot"]), prompt=str(item["prompt"])))
    if not images:
        return CraftedPromptSet(asset_id=asset_id, unavailable=True, unavailable_reason="crafter returned no usable image prompts")
    return CraftedPromptSet(asset_id=asset_id, images=images)


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
