"""N-A Trend & Visual Analyst (W8-9 Q3a; FLOW_MAP.md's ``analysis`` stage).

Runs AFTER ``ranking`` (Q6 re-audit R2, W8-10 Phase 6 — moved from its
original collection->analysis->ranking position): N-A now studies only the
themes that WON this run's ranking (the topics ``stages.stage_ranking``
marked ``generate``), deeper, rather than every theme the raw Virlo corpus
happened to contain. Its output (``analysis/viral_playbook.yaml``) feeds
``copy``/``media`` (prompt crafting), and its path is carried into
``resume_state.yaml`` (via ``stage_spin``) so a ``--resume`` re-entry into
``copy``/``media`` still has it without re-running this stage. Ranking
itself stays fully deterministic and untouched by this stage either way —
this reorder is a pure input-quality change, not a new dependency edge.

One (or, on an unparseable first attempt, two — ``llm.LlmClient``'s own
bounded corrective retry) LLM call, batching everything: the Virlo research
corpus (themes/tactics/top videos+captions/hook texts/panel texts,
deterministically truncated, filtered to this run's winning themes when
known) plus up to ``llm.analyst_max_images`` downloaded thumbnails/carousel
panels (base64'd), selected by VIEWS via the image<->item join manifest
(``collectors.virlo.MediaManifestEntry``) with a guaranteed video-thumbnail
quota, each labeled in the prompt with its source item/views/caption so the
model can attribute what it sees to a real post — plus the style guide's
own visual-archetype vocabulary, so the model maps what it sees onto OUR
vocabulary rather than inventing a new one.

**This stage never fails the run** (module contract, restated at every
branch below): no corpus on disk, the LLM disabled in config, the run's LLM
budget already exhausted, or the call itself failing all degrade to an
explicit, empty-but-valid ``viral_playbook.yaml`` — copy then grounds on
``style_guide.yaml`` alone, exactly as if this stage did not exist.

W8-10 Phase 8 (dynamic-inspiration fidelity trace) additions: a per-image
``analyzed_items`` record (closed-vocabulary-leaning fields — an unknown
enum value from the model is kept as a plain string, never a crash) fusing
each image with that same post's Virlo metadata, plus a per-theme
``visual_profile`` aggregate computed DETERMINISTICALLY in Python from
``analyzed_items`` (never asked of the LLM) — the concrete, inspectable
answer to "this theme wins with X style" that ``promptcraft.py`` reads to
pick a generation mode instead of a positional ``seen[0]`` lottery.

Third-party verbatim text (Virlo captions/hook texts/panel texts) legitimately
flows INTO this stage's LLM prompt and MAY appear in ``viral_playbook.yaml``
itself if the model echoes a hook verbatim (both are the "research-artifact
class" the HARD CONSTRAINTS carve out) — but never into a trace event, which
carries counts/keys/hashes only, exactly like ``virlo_corpus.yaml`` already
gets treated.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from hypeagent import llm as llm_module
from hypeagent.collectors import virlo as virlo_collector
from hypeagent.llm import LlmClient, LlmError
from hypeagent.trace import TraceWriter

VIRAL_PLAYBOOK_DIRNAME = "analysis"
VIRAL_PLAYBOOK_FILENAME = "viral_playbook.yaml"

# Deterministic truncation caps (module docstring: "batch everything ... if
# the corpus is large, truncate deterministically: top themes by
# confidence, top items by views" — the corpus's own ``videos``/
# ``slideshows`` lists are already views-sorted by
# ``collectors.virlo.build_virlo_corpus``, so slicing here is enough).
#
# W8-9 (live-run token-starvation fix): a live run sent a ~70k-token N-A
# prompt, which blew the (then-1500) completion budget on the corrective
# retry alone and wasted real money re-sending it. These caps (fewer items,
# top themes only) plus :func:`_trim_prompt_item` (caption-length trimming
# below) are chosen to keep the assembled prompt comfortably under ~30k
# tokens for a typically-sized corpus -- this is a deterministic, traceable
# input-size cap, not a token counter (the engine has no tokenizer
# dependency; stdlib+pyyaml only).
#
# Q6 re-audit R2 (W8-10 Phase 6): raised from 6/4 -- N-A now runs AFTER
# ranking and studies only the winning themes, so it can afford to look
# deeper per theme without repeating the old token-starvation incident
# (fewer themes in scope more than offsets the larger per-item caps).
MAX_THEMES_IN_PROMPT = 5
MAX_VIDEOS_IN_PROMPT = 10
MAX_SLIDESHOWS_IN_PROMPT = 8
MAX_VIRAL_TACTICS_IN_PROMPT = 8
MAX_PANEL_TEXTS_PER_SLIDESHOW = 6
PROMPT_CAPTION_TRIM_CHARS = 300
# Heavy/irrelevant-to-the-analyst fields dropped from the PROMPT copy of
# each video/slideshow item (still present in full in the on-disk
# ``virlo_corpus.yaml`` research artifact — this trims the prompt only):
# long CDN URLs and a hashed handle carry no pattern-analysis value and cost
# real tokens for nothing, since the analyst never needs to dereference them.
_PROMPT_DROP_FIELDS = ("thumbnail_url", "image_urls", "author_handle_hash")
_PROMPT_CAPTION_FIELDS = ("description", "hook_text", "text_overlay_content", "summary")

DEFAULT_ANALYST_MAX_IMAGES = 12
# Q6 re-audit / W8-10 Phase 8: at least this share of the image slots is
# reserved for video thumbnails (person/talking-head evidence), even when
# slideshow panels would otherwise out-rank them purely by views — the
# fidelity trace's root cause #1 was ALL 6 person/talking-head thumbnails
# in a 24-image corpus getting silently excluded by a flat top-12-by-hash
# selection.
THUMBNAIL_QUOTA_FRACTION = 1 / 3

SYSTEM_PROMPT = (
    "You are the Trend & Visual Analyst for HypeDigitaly's AI-agency social content pipeline "
    "(FLOW_MAP.md node N-A). You study short-form social content (TikTok/Reels/Shorts captions, "
    "hooks, and images) in the AI-agents/chatbots/automation niche to extract what is ACTUALLY "
    "working right now, so a downstream copywriter and image-prompt crafter can ground their own "
    "output in real, observed patterns instead of guessing. Only describe patterns you can point to "
    "in the material given to you below — never invent a number, a tool name, or a hook that is not "
    "present in it. This is internal research/analysis, not copy for publication."
)

SCHEMA_HINT = (
    'Schema: {"themes": [{"theme": string, "winning_hooks": [string], "formats": [string], '
    '"visual_archetypes_seen": [string], "tools_shown": [string], "numbers_used": [string], '
    '"platform_norms": {"linkedin": string, "instagram_feed": string, "tiktok": string}}], '
    '"global": {"viral_tactics_digest": [string], "connecting_thread": string, "do_not_do": [string]}, '
    '"analyzed_items": [{"image_index": int, "post_kind": string, '
    '"person": {"present": bool, "prominence": string, "face_visible": bool, "framing": string, "count": int}, '
    '"logos": {"present": bool, "kind": [string], "names": [string], "treatment": string}, '
    '"visual_style": {"ground": string, "realism": string, "lighting": string, "color_key": string}, '
    '"text_treatment": {"density": string, "style": string, "placement": string, "has_numbering": bool, '
    '"verbatim_sample": string}, "environment": {"setting": string, "aspiration_signal": bool}, '
    '"confidence": number, "summary": string, "consists_of": [string]}]}'
)

# ---------------------------------------------------------------------------
# W8-10 Phase 8 — closed-vocabulary guidance for ``analyzed_items`` (advisory
# only: parsing is lenient by design, module docstring — an unknown value is
# kept verbatim as a plain string, never a parse failure or a crash).
# ---------------------------------------------------------------------------

_ANALYZED_ITEM_VOCAB_LINES = (
    "post_kind: informational | value | ugc-lifestyle | showcase | meme | screenshot-proof",
    "person.prominence: none | background | secondary | primary",
    "person.framing: face-closeup | waist-up | full-body | hands-only | voiceover-only | not-applicable",
    "logos.kind: app-icon | wordmark | favicon | ui-chrome | other",
    "logos.treatment: prominent | subtle | blurred | fictional-stylized",
    "visual_style.ground: photoreal | designed_graphic | app_screenshot | ugc_casual | mixed",
    "visual_style.realism: photographic | illustrated | 3d_render | stylized",
    "visual_style.lighting: natural | studio | screen_glow | flat | dramatic",
    "visual_style.color_key: warm | cool | neutral | high_contrast | pastel | monochrome",
    "text_treatment.density: none | light | moderate | heavy",
    "text_treatment.style: sticker | editorial_typography | native_caption | meme_caption | ui_label | handwritten",
    "text_treatment.placement: overlay_top | overlay_bottom | overlay_center | lower_third | full_screen | caption_only",
    "environment.setting: home | office | outdoor | studio | screen_only | travel | vehicle | event | unknown",
)


# ---------------------------------------------------------------------------
# The playbook shape.
# ---------------------------------------------------------------------------


@dataclass
class ThemePlaybook:
    theme: str
    winning_hooks: list[str] = field(default_factory=list)
    formats: list[str] = field(default_factory=list)
    visual_archetypes_seen: list[str] = field(default_factory=list)
    tools_shown: list[str] = field(default_factory=list)
    numbers_used: list[str] = field(default_factory=list)
    platform_norms: dict[str, str] = field(default_factory=dict)
    # W8-10 Phase 8: additive 8th field — the deterministic per-theme visual
    # aggregate built from this run's ``analyzed_items`` (``None`` when no
    # analyzed item ever matched this theme's name, e.g. a text-only run
    # with no images, or a theme this run had zero linked media for).
    visual_profile: "VisualProfile | None" = None

    def to_yaml_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "theme": self.theme,
            "winning_hooks": self.winning_hooks,
            "formats": self.formats,
            "visual_archetypes_seen": self.visual_archetypes_seen,
            "tools_shown": self.tools_shown,
            "numbers_used": self.numbers_used,
            "platform_norms": self.platform_norms,
        }
        d["visual_profile"] = self.visual_profile.to_yaml_dict() if self.visual_profile else None
        return d


@dataclass
class ViralPlaybook:
    """The per-run N-A output. ``skipped`` covers the two normal, expected,
    config/data-driven "nothing to do" conditions (LLM disabled; no corpus
    this run) — these are NOT pipeline degrades (a run with the LLM
    deliberately turned off is not unhealthy). ``degraded`` covers a genuine
    attempted-and-failed call (budget exhausted mid-attempt, transport/API/
    parse failure) — the stage still never raises, but this is the one case
    ``stages.stage_analysis`` reports as a degraded stage outcome."""

    themes: list[ThemePlaybook] = field(default_factory=list)
    viral_tactics_digest: list[str] = field(default_factory=list)
    connecting_thread: str | None = None
    do_not_do: list[str] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str | None = None
    degraded: bool = False
    degrade_reason: str | None = None
    # W8-10 Phase 8: additive 8th top-level field — every per-image analyzed
    # record this run produced (see :class:`AnalyzedItem`), the atom each
    # theme's ``visual_profile`` is aggregated from.
    analyzed_items: list["AnalyzedItem"] = field(default_factory=list)

    def theme_playbook(self, theme_name: str | None, *, warn: Callable[[str], None] | None = None) -> ThemePlaybook | None:
        """Look up a theme by exact name. Falls back to ``themes[0]`` when
        no exact match exists (or none was asked for) and at least one
        theme is on file — this fallback used to be silent (W8-10 Phase 8
        fidelity trace, root cause #4); ``warn`` (optional — a trace/log
        sink) is now called with a human-readable message every time the
        fallback actually fires, so a mismatched topic name is visible
        instead of quietly borrowing an unrelated theme's playbook."""
        if theme_name:
            for t in self.themes:
                if t.theme == theme_name:
                    return t
        if self.themes:
            if warn is not None:
                warn(
                    f"theme_playbook fallback: no exact match for {theme_name!r} among "
                    f"{[t.theme for t in self.themes]!r} — using themes[0] ({self.themes[0].theme!r})"
                )
            return self.themes[0]
        return None

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "version": 1,
            "skipped": self.skipped,
            "skip_reason": self.skip_reason,
            "degraded": self.degraded,
            "degrade_reason": self.degrade_reason,
            "themes": [t.to_yaml_dict() for t in self.themes],
            "global": {
                "viral_tactics_digest": self.viral_tactics_digest,
                "connecting_thread": self.connecting_thread,
                "do_not_do": self.do_not_do,
            },
            "analyzed_items": [ai.to_yaml_dict() for ai in self.analyzed_items],
        }


def _coerce_str_list(value: Any, *, limit: int = 20) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v) for v in value if v is not None and str(v).strip()][:limit]


_NOISE_PHRASES = (
    "not observed",
    "no evidence",
    "n/a",
    "none observed",
    "not present in",
    "no data",
)


def _coerce_platform_norms(value: Any) -> dict[str, str]:
    """Q6 re-audit R4: only platforms the model actually wrote a real norm
    for survive — any value that reads like the "not observed in corpus"
    noise the audit called out (case-insensitively matched against
    ``_NOISE_PHRASES``) is dropped entirely rather than kept as an empty
    line. This is enforced HERE, deterministically, regardless of whether
    the model actually follows the prompt's own instruction to omit such
    platforms (see :func:`build_analyst_prompt`)."""
    if not isinstance(value, dict):
        return {}
    result: dict[str, str] = {}
    for k, v in value.items():
        if k not in ("linkedin", "instagram_feed", "tiktok") or not v:
            continue
        text = str(v)
        if any(phrase in text.lower() for phrase in _NOISE_PHRASES):
            continue
        result[str(k)] = text
    return result


# ---------------------------------------------------------------------------
# W8-10 Phase 8 — per-image ``analyzed_items`` schema (closed-vocab-leaning,
# lenient parsing: an unrecognized enum value is kept as a plain string, not
# validated against the vocabulary above and never a parse failure).
# ---------------------------------------------------------------------------


def _b(value: Any, default: bool = False) -> bool:
    return bool(value) if value is not None else default


def _s(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _i(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _f01(value: Any, default: float = 0.0) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, f))


@dataclass
class PersonAnalysis:
    present: bool = False
    prominence: str = "none"
    face_visible: bool = False
    framing: str = "not-applicable"
    count: int = 0

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "present": self.present, "prominence": self.prominence, "face_visible": self.face_visible,
            "framing": self.framing, "count": self.count,
        }

    @classmethod
    def from_model(cls, data: Any) -> "PersonAnalysis":
        data = data if isinstance(data, dict) else {}
        return cls(
            present=_b(data.get("present")),
            prominence=_s(data.get("prominence"), "none"),
            face_visible=_b(data.get("face_visible")),
            framing=_s(data.get("framing"), "not-applicable"),
            count=_i(data.get("count"), 0),
        )


@dataclass
class LogosAnalysis:
    present: bool = False
    kind: list[str] = field(default_factory=list)
    names: list[str] = field(default_factory=list)
    treatment: str = "none"

    def to_yaml_dict(self) -> dict[str, Any]:
        return {"present": self.present, "kind": self.kind, "names": self.names, "treatment": self.treatment}

    @classmethod
    def from_model(cls, data: Any) -> "LogosAnalysis":
        data = data if isinstance(data, dict) else {}
        return cls(
            present=_b(data.get("present")),
            kind=_coerce_str_list(data.get("kind")),
            names=_coerce_str_list(data.get("names")),
            treatment=_s(data.get("treatment"), "none"),
        )


@dataclass
class VisualStyleAnalysis:
    ground: str = "unknown"
    realism: str = "unknown"
    lighting: str = "unknown"
    color_key: str = "unknown"

    def to_yaml_dict(self) -> dict[str, Any]:
        return {"ground": self.ground, "realism": self.realism, "lighting": self.lighting, "color_key": self.color_key}

    @classmethod
    def from_model(cls, data: Any) -> "VisualStyleAnalysis":
        data = data if isinstance(data, dict) else {}
        return cls(
            ground=_s(data.get("ground")), realism=_s(data.get("realism")),
            lighting=_s(data.get("lighting")), color_key=_s(data.get("color_key")),
        )


@dataclass
class TextTreatmentAnalysis:
    density: str = "none"
    style: str = "unknown"
    placement: str = "unknown"
    has_numbering: bool = False
    verbatim_sample: str = ""

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "density": self.density, "style": self.style, "placement": self.placement,
            "has_numbering": self.has_numbering, "verbatim_sample": self.verbatim_sample,
        }

    @classmethod
    def from_model(cls, data: Any) -> "TextTreatmentAnalysis":
        data = data if isinstance(data, dict) else {}
        sample = data.get("verbatim_sample")
        return cls(
            density=_s(data.get("density"), "none"), style=_s(data.get("style")),
            placement=_s(data.get("placement")), has_numbering=_b(data.get("has_numbering")),
            verbatim_sample=str(sample)[:PROMPT_CAPTION_TRIM_CHARS] if sample else "",
        )


@dataclass
class EnvironmentAnalysis:
    setting: str = "unknown"
    aspiration_signal: bool = False

    def to_yaml_dict(self) -> dict[str, Any]:
        return {"setting": self.setting, "aspiration_signal": self.aspiration_signal}

    @classmethod
    def from_model(cls, data: Any) -> "EnvironmentAnalysis":
        data = data if isinstance(data, dict) else {}
        return cls(setting=_s(data.get("setting")), aspiration_signal=_b(data.get("aspiration_signal")))


@dataclass
class AnalyzedItem:
    """One analyzed image, fused with its source post's metadata. The first
    four fields are INJECTED from the image<->item join manifest (never
    asked of the model — the model only ever sees an ``image_index`` to
    report against); everything else is model-provided, defensively parsed."""

    item_id: str | None
    media_file: str
    panel_index: int | None
    theme_key: str | None
    views: int
    post_kind: str = "unknown"
    person: PersonAnalysis = field(default_factory=PersonAnalysis)
    logos: LogosAnalysis = field(default_factory=LogosAnalysis)
    visual_style: VisualStyleAnalysis = field(default_factory=VisualStyleAnalysis)
    text_treatment: TextTreatmentAnalysis = field(default_factory=TextTreatmentAnalysis)
    environment: EnvironmentAnalysis = field(default_factory=EnvironmentAnalysis)
    confidence: float = 0.0
    summary: str = ""
    consists_of: list[str] = field(default_factory=list)

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "media_file": self.media_file,
            "panel_index": self.panel_index,
            "theme_key": self.theme_key,
            "views": self.views,
            "post_kind": self.post_kind,
            "person": self.person.to_yaml_dict(),
            "logos": self.logos.to_yaml_dict(),
            "visual_style": self.visual_style.to_yaml_dict(),
            "text_treatment": self.text_treatment.to_yaml_dict(),
            "environment": self.environment.to_yaml_dict(),
            "confidence": round(self.confidence, 3),
            "summary": self.summary,
            "consists_of": self.consists_of,
        }


# ---------------------------------------------------------------------------
# W8-10 Phase 8 — image selection via the manifest join (views-ordered,
# thumbnail quota) + per-image ``SelectedImage`` (path + manifest entry) so
# the prompt builder can label each image and ``analyzed_items`` can be
# built with the injected join fields.
# ---------------------------------------------------------------------------


@dataclass
class SelectedImage:
    path: Path
    entry: virlo_collector.MediaManifestEntry


def select_analysis_images(
    media_dir: Path,
    *,
    max_images: int,
    manifest: list[virlo_collector.MediaManifestEntry] | None = None,
    thumbnail_quota_fraction: float = THUMBNAIL_QUOTA_FRACTION,
) -> list[SelectedImage]:
    """Select up to ``max_images`` downloaded images for the N-A prompt.

    W8-10 Phase 8 fidelity-trace fix: when a ``manifest`` (the image<->item
    join, ``collectors.virlo.load_media_manifest``) is available, images are
    ordered by VIEWS (not hash-sorted filenames — the old docstring claimed
    views-ordering; it was false), with a guaranteed video-thumbnail quota
    (``thumbnail_quota_fraction``, default 1/3 of slots, or every thumbnail
    available if fewer) so person/talking-head evidence is never silently
    excluded by slideshow panels out-ranking it purely on view count.

    Without a manifest (an older engine version's run, or media downloaded
    outside the normal collector path), falls back to the pre-Phase-8
    behaviour: hash-sorted filenames, panels before thumbnails, no
    guaranteed quota — wrapped in a :class:`SelectedImage` with a
    best-effort (mostly-unknown) manifest entry so callers have one uniform
    return type either way.
    """
    media_dir = Path(media_dir)
    if max_images <= 0 or not media_dir.is_dir():
        return []

    if not manifest:
        files = sorted(p for p in media_dir.iterdir() if p.is_file())
        panels = [p for p in files if p.name.startswith("slideshow_panel_")]
        thumbnails = [p for p in files if p.name.startswith("video_thumbnail_")]
        ordered = (panels + thumbnails)[:max_images]
        return [
            SelectedImage(
                path=p,
                entry=virlo_collector.MediaManifestEntry(
                    filename=p.name,
                    item_id=None,
                    item_kind="slideshow" if p.name.startswith("slideshow_panel_") else "video",
                    panel_index=None,
                    views=0,
                    theme_key=None,
                    caption=None,
                ),
            )
            for p in ordered
        ]

    by_filename = {e.filename: e for e in manifest}
    available: list[tuple[virlo_collector.MediaManifestEntry, Path]] = [
        (by_filename[p.name], p) for p in media_dir.iterdir() if p.is_file() and p.name in by_filename
    ]
    available_sorted = sorted(available, key=lambda pair: pair[0].views, reverse=True)

    thumb_pairs = [pair for pair in available_sorted if pair[0].item_kind == "video"]
    quota = 0
    if thumb_pairs and thumbnail_quota_fraction > 0:
        quota_target = max(1, math.ceil(max_images * thumbnail_quota_fraction))
        quota = min(len(thumb_pairs), quota_target)
    guaranteed = thumb_pairs[:quota]
    guaranteed_names = {entry.filename for entry, _ in guaranteed}
    remaining_slots = max(0, max_images - len(guaranteed))
    pool = [pair for pair in available_sorted if pair[0].filename not in guaranteed_names]
    fill = pool[:remaining_slots]

    combined = sorted(guaranteed + fill, key=lambda pair: pair[0].views, reverse=True)[:max_images]
    return [SelectedImage(path=path, entry=entry) for entry, path in combined]


# ---------------------------------------------------------------------------
# W8-10 Phase 8 — the deterministic per-theme ``visual_profile`` aggregate.
# Computed entirely in Python from ``analyzed_items`` — never asked of the
# LLM (module docstring).
# ---------------------------------------------------------------------------


@dataclass
class VisualProfile:
    theme_key: str
    items_analyzed: int
    items_available: int
    person_rate: float
    face_visible_rate: float
    dominant_person_framing: str
    logo_rate: float
    dominant_logo_treatment: str
    logos_ranked: list[dict[str, Any]]
    ground_mix: dict[str, float]
    dominant_ground: str
    text_treatment_mix: dict[str, float]
    dominant_text_style: str
    dominant_text_density: str
    numbering_rate: float
    dominant_environment: str
    aspiration_signal_rate: float
    recommended_generation_mode: str
    evidence_item_ids: list[str]

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "theme_key": self.theme_key,
            "items_analyzed": self.items_analyzed,
            "items_available": self.items_available,
            "person_rate": round(self.person_rate, 3),
            "face_visible_rate": round(self.face_visible_rate, 3),
            "dominant_person_framing": self.dominant_person_framing,
            "logo_rate": round(self.logo_rate, 3),
            "dominant_logo_treatment": self.dominant_logo_treatment,
            "logos_ranked": self.logos_ranked,
            "ground_mix": self.ground_mix,
            "dominant_ground": self.dominant_ground,
            "text_treatment_mix": self.text_treatment_mix,
            "dominant_text_style": self.dominant_text_style,
            "dominant_text_density": self.dominant_text_density,
            "numbering_rate": round(self.numbering_rate, 3),
            "dominant_environment": self.dominant_environment,
            "aspiration_signal_rate": round(self.aspiration_signal_rate, 3),
            "recommended_generation_mode": self.recommended_generation_mode,
            "evidence_item_ids": self.evidence_item_ids,
        }


def _view_weight(views: int) -> float:
    """Views-weighting helper: a zero/missing view count still contributes
    a nominal weight of 1 rather than vanishing from every mix entirely
    (defensive — the manifest's ``views`` field is best-effort)."""
    return float(views) if views and views > 0 else 1.0


def _weighted_tally(pairs: list[tuple[str, float]]) -> dict[str, float]:
    tally: dict[str, float] = {}
    for key, weight in pairs:
        if not key:
            continue
        tally[key] = tally.get(key, 0.0) + weight
    return tally


def _normalized_mix(tally: dict[str, float]) -> dict[str, float]:
    total = sum(tally.values())
    if total <= 0:
        return {}
    return {k: round(v / total, 4) for k, v in sorted(tally.items(), key=lambda kv: kv[1], reverse=True)}


def _dominant(tally: dict[str, float], default: str = "unknown") -> str:
    if not tally:
        return default
    return max(tally.items(), key=lambda kv: kv[1])[0]


def recommended_generation_mode_for(*, dominant_ground: str, person_rate: float, dominant_text_style: str) -> str:
    """The rule table (W8-10 Phase 8 BUILD SPEC), applied in this fixed
    order:

    1. photoreal ground + sticker text + person_rate >= 0.4 -> photoreal_person_ugc
    2. photoreal ground + sticker text (lower person share)  -> photoreal_lifestyle_sticker
    3. designed_graphic dominant                             -> designed_card
    4. app_screenshot dominant                                -> live_app_ui
    5. fallback                                                -> designed_card
    """
    if dominant_ground == "photoreal" and dominant_text_style == "sticker":
        return "photoreal_person_ugc" if person_rate >= 0.4 else "photoreal_lifestyle_sticker"
    if dominant_ground == "designed_graphic":
        return "designed_card"
    if dominant_ground == "app_screenshot":
        return "live_app_ui"
    return "designed_card"


def compute_visual_profile(theme_key: str, items: list[AnalyzedItem], *, items_available: int) -> VisualProfile:
    """Deterministic per-theme aggregate from ``items`` (every
    :class:`AnalyzedItem` whose ``theme_key`` matches ``theme_key``). Rate
    fields (``*_rate``) are simple counts over ``items``; mixes/dominants
    (``ground_mix``, ``text_treatment_mix``, and every ``dominant_*`` field)
    are VIEWS-WEIGHTED — a theme's actual reach votes on what its
    "dominant" style is, not a flat per-item count. Never fails: an empty
    ``items`` list produces an all-zero/"unknown" profile, not an error."""
    n = len(items)
    if n == 0:
        return VisualProfile(
            theme_key=theme_key, items_analyzed=0, items_available=items_available,
            person_rate=0.0, face_visible_rate=0.0, dominant_person_framing="not-applicable",
            logo_rate=0.0, dominant_logo_treatment="none", logos_ranked=[],
            ground_mix={}, dominant_ground="unknown", text_treatment_mix={}, dominant_text_style="unknown",
            dominant_text_density="none", numbering_rate=0.0, dominant_environment="unknown",
            aspiration_signal_rate=0.0,
            recommended_generation_mode=recommended_generation_mode_for(
                dominant_ground="unknown", person_rate=0.0, dominant_text_style="unknown"
            ),
            evidence_item_ids=[],
        )

    person_rate = sum(1 for it in items if it.person.present) / n
    face_visible_rate = sum(1 for it in items if it.person.face_visible) / n
    framing_tally = _weighted_tally(
        [(it.person.framing, _view_weight(it.views)) for it in items if it.person.present]
    )
    dominant_person_framing = _dominant(framing_tally, "not-applicable")

    logo_rate = sum(1 for it in items if it.logos.present) / n
    treatment_tally = _weighted_tally(
        [(it.logos.treatment, _view_weight(it.views)) for it in items if it.logos.present]
    )
    dominant_logo_treatment = _dominant(treatment_tally, "none")

    logo_name_tally = _weighted_tally(
        [(name, _view_weight(it.views)) for it in items for name in it.logos.names]
    )
    logos_ranked = [
        {"name": name, "weight": round(weight, 1)}
        for name, weight in sorted(logo_name_tally.items(), key=lambda kv: kv[1], reverse=True)
    ]

    ground_tally = _weighted_tally([(it.visual_style.ground, _view_weight(it.views)) for it in items])
    ground_mix = _normalized_mix(ground_tally)
    dominant_ground = _dominant(ground_tally)

    style_tally = _weighted_tally([(it.text_treatment.style, _view_weight(it.views)) for it in items])
    text_treatment_mix = _normalized_mix(style_tally)
    dominant_text_style = _dominant(style_tally)

    density_tally = _weighted_tally([(it.text_treatment.density, _view_weight(it.views)) for it in items])
    dominant_text_density = _dominant(density_tally, "none")

    numbering_rate = sum(1 for it in items if it.text_treatment.has_numbering) / n

    environment_tally = _weighted_tally([(it.environment.setting, _view_weight(it.views)) for it in items])
    dominant_environment = _dominant(environment_tally)

    aspiration_signal_rate = sum(1 for it in items if it.environment.aspiration_signal) / n

    evidence_item_ids = []
    seen_ids: set[str] = set()
    for it in sorted(items, key=lambda x: x.views, reverse=True):
        key = it.item_id or it.media_file
        if key and key not in seen_ids:
            seen_ids.add(key)
            evidence_item_ids.append(key)

    return VisualProfile(
        theme_key=theme_key,
        items_analyzed=n,
        items_available=max(items_available, n),
        person_rate=person_rate,
        face_visible_rate=face_visible_rate,
        dominant_person_framing=dominant_person_framing,
        logo_rate=logo_rate,
        dominant_logo_treatment=dominant_logo_treatment,
        logos_ranked=logos_ranked,
        ground_mix=ground_mix,
        dominant_ground=dominant_ground,
        text_treatment_mix=text_treatment_mix,
        dominant_text_style=dominant_text_style,
        dominant_text_density=dominant_text_density,
        numbering_rate=numbering_rate,
        dominant_environment=dominant_environment,
        aspiration_signal_rate=aspiration_signal_rate,
        recommended_generation_mode=recommended_generation_mode_for(
            dominant_ground=dominant_ground, person_rate=person_rate, dominant_text_style=dominant_text_style
        ),
        evidence_item_ids=evidence_item_ids,
    )


def attach_visual_profiles(playbook: ViralPlaybook, *, items_available_by_theme: dict[str, int] | None = None) -> ViralPlaybook:
    """Group ``playbook.analyzed_items`` by ``theme_key`` and attach a
    :class:`VisualProfile` to every matching :class:`ThemePlaybook` entry
    (mutates ``playbook.themes`` in place; returns ``playbook`` for
    chaining). A theme with zero matching analyzed items still gets an
    all-zero profile attached (never ``None`` once this function has run),
    for a uniform downstream shape."""
    items_available_by_theme = items_available_by_theme or {}
    by_theme: dict[str, list[AnalyzedItem]] = {}
    for item in playbook.analyzed_items:
        if item.theme_key:
            by_theme.setdefault(item.theme_key, []).append(item)
    for theme in playbook.themes:
        theme_items = by_theme.get(theme.theme, [])
        available = items_available_by_theme.get(theme.theme, len(theme_items))
        theme.visual_profile = compute_visual_profile(theme.theme, theme_items, items_available=available)
    return playbook


def _parse_analyzed_items(raw: Any, images: list[SelectedImage]) -> list[AnalyzedItem]:
    """Build :class:`AnalyzedItem` records by joining the model's
    ``analyzed_items`` array (keyed by ``image_index``, matched positionally
    against the SAME ``images`` list the prompt was built from) with the
    injected manifest fields. Lenient throughout: a missing/out-of-range/
    malformed ``image_index`` is simply skipped (never a crash) — this
    stage never fails the run."""
    if not isinstance(raw, list) or not images:
        return []
    items: list[AnalyzedItem] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        idx = entry.get("image_index")
        if not isinstance(idx, int) or idx < 0 or idx >= len(images):
            continue
        manifest_entry = images[idx].entry
        items.append(
            AnalyzedItem(
                item_id=manifest_entry.item_id,
                media_file=manifest_entry.filename,
                panel_index=manifest_entry.panel_index,
                theme_key=manifest_entry.theme_key,
                views=manifest_entry.views,
                post_kind=_s(entry.get("post_kind")),
                person=PersonAnalysis.from_model(entry.get("person")),
                logos=LogosAnalysis.from_model(entry.get("logos")),
                visual_style=VisualStyleAnalysis.from_model(entry.get("visual_style")),
                text_treatment=TextTreatmentAnalysis.from_model(entry.get("text_treatment")),
                environment=EnvironmentAnalysis.from_model(entry.get("environment")),
                confidence=_f01(entry.get("confidence")),
                summary=_s(entry.get("summary"), ""),
                consists_of=_coerce_str_list(entry.get("consists_of")),
            )
        )
    return items


def parse_playbook_response(data: dict[str, Any], *, images: list[SelectedImage] | None = None) -> ViralPlaybook:
    """Coerce the model's JSON response into a :class:`ViralPlaybook`,
    defensively — an LLM's output shape drift (missing key, wrong type)
    degrades that one field to empty rather than raising. ``images`` (the
    same list :func:`build_analyst_prompt` was given) is required to join
    ``analyzed_items`` back to the manifest; omitted or empty simply
    produces zero analyzed items, never an error."""
    themes: list[ThemePlaybook] = []
    for item in (data.get("themes") or [])[:MAX_THEMES_IN_PROMPT] if isinstance(data.get("themes"), list) else []:
        if not isinstance(item, dict):
            continue
        name = item.get("theme") or item.get("name")
        if not name:
            continue
        themes.append(
            ThemePlaybook(
                theme=str(name),
                winning_hooks=_coerce_str_list(item.get("winning_hooks")),
                formats=_coerce_str_list(item.get("formats")),
                visual_archetypes_seen=_coerce_str_list(item.get("visual_archetypes_seen")),
                tools_shown=_coerce_str_list(item.get("tools_shown")),
                numbers_used=_coerce_str_list(item.get("numbers_used")),
                platform_norms=_coerce_platform_norms(item.get("platform_norms")),
            )
        )
    global_block = data.get("global") if isinstance(data.get("global"), dict) else {}
    connecting_thread = global_block.get("connecting_thread") or data.get("connecting_thread")
    analyzed_items = _parse_analyzed_items(data.get("analyzed_items"), images or [])
    return ViralPlaybook(
        themes=themes,
        viral_tactics_digest=_coerce_str_list(
            global_block.get("viral_tactics_digest") or data.get("viral_tactics_digest")
        ),
        connecting_thread=str(connecting_thread) if connecting_thread else None,
        do_not_do=_coerce_str_list(global_block.get("do_not_do") or data.get("do_not_do")),
        analyzed_items=analyzed_items,
    )


def _playbook_from_yaml_dict(data: dict[str, Any]) -> ViralPlaybook:
    global_block = data.get("global") or {}

    def _visual_profile_from_dict(vp: Any) -> VisualProfile | None:
        if not isinstance(vp, dict) or not vp:
            return None
        return VisualProfile(
            theme_key=str(vp.get("theme_key", "")),
            items_analyzed=int(vp.get("items_analyzed", 0)),
            items_available=int(vp.get("items_available", 0)),
            person_rate=float(vp.get("person_rate", 0.0)),
            face_visible_rate=float(vp.get("face_visible_rate", 0.0)),
            dominant_person_framing=str(vp.get("dominant_person_framing", "not-applicable")),
            logo_rate=float(vp.get("logo_rate", 0.0)),
            dominant_logo_treatment=str(vp.get("dominant_logo_treatment", "none")),
            logos_ranked=list(vp.get("logos_ranked") or []),
            ground_mix=dict(vp.get("ground_mix") or {}),
            dominant_ground=str(vp.get("dominant_ground", "unknown")),
            text_treatment_mix=dict(vp.get("text_treatment_mix") or {}),
            dominant_text_style=str(vp.get("dominant_text_style", "unknown")),
            dominant_text_density=str(vp.get("dominant_text_density", "none")),
            numbering_rate=float(vp.get("numbering_rate", 0.0)),
            dominant_environment=str(vp.get("dominant_environment", "unknown")),
            aspiration_signal_rate=float(vp.get("aspiration_signal_rate", 0.0)),
            recommended_generation_mode=str(vp.get("recommended_generation_mode", "designed_card")),
            evidence_item_ids=list(vp.get("evidence_item_ids") or []),
        )

    def _analyzed_item_from_dict(ai: dict[str, Any]) -> AnalyzedItem:
        return AnalyzedItem(
            item_id=ai.get("item_id"),
            media_file=str(ai.get("media_file", "")),
            panel_index=ai.get("panel_index"),
            theme_key=ai.get("theme_key"),
            views=int(ai.get("views", 0)),
            post_kind=str(ai.get("post_kind", "unknown")),
            person=PersonAnalysis.from_model(ai.get("person")),
            logos=LogosAnalysis.from_model(ai.get("logos")),
            visual_style=VisualStyleAnalysis.from_model(ai.get("visual_style")),
            text_treatment=TextTreatmentAnalysis.from_model(ai.get("text_treatment")),
            environment=EnvironmentAnalysis.from_model(ai.get("environment")),
            confidence=float(ai.get("confidence", 0.0)),
            summary=str(ai.get("summary", "")),
            consists_of=list(ai.get("consists_of") or []),
        )

    return ViralPlaybook(
        themes=[
            ThemePlaybook(
                theme=str(t.get("theme", "")),
                winning_hooks=list(t.get("winning_hooks") or []),
                formats=list(t.get("formats") or []),
                visual_archetypes_seen=list(t.get("visual_archetypes_seen") or []),
                tools_shown=list(t.get("tools_shown") or []),
                numbers_used=list(t.get("numbers_used") or []),
                platform_norms=dict(t.get("platform_norms") or {}),
                visual_profile=_visual_profile_from_dict(t.get("visual_profile")),
            )
            for t in (data.get("themes") or [])
        ],
        viral_tactics_digest=list(global_block.get("viral_tactics_digest") or []),
        connecting_thread=global_block.get("connecting_thread"),
        do_not_do=list(global_block.get("do_not_do") or []),
        skipped=bool(data.get("skipped", False)),
        skip_reason=data.get("skip_reason"),
        degraded=bool(data.get("degraded", False)),
        degrade_reason=data.get("degrade_reason"),
        analyzed_items=[
            _analyzed_item_from_dict(ai) for ai in (data.get("analyzed_items") or []) if isinstance(ai, dict)
        ],
    )


def write_viral_playbook(run_dir: Path, playbook: ViralPlaybook) -> Path:
    path = Path(run_dir) / VIRAL_PLAYBOOK_DIRNAME / VIRAL_PLAYBOOK_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(playbook.to_yaml_dict(), allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def load_viral_playbook_file(path: Path) -> ViralPlaybook | None:
    path = Path(path)
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return None
    return _playbook_from_yaml_dict(data)


def load_viral_playbook(run_dir: Path) -> ViralPlaybook | None:
    return load_viral_playbook_file(Path(run_dir) / VIRAL_PLAYBOOK_DIRNAME / VIRAL_PLAYBOOK_FILENAME)


# ---------------------------------------------------------------------------
# Deterministic corpus truncation + image selection.
# ---------------------------------------------------------------------------


def _trim_caption_text(value: Any, *, limit: int = PROMPT_CAPTION_TRIM_CHARS) -> Any:
    """Trim one caption-shaped string to ``limit`` chars for the PROMPT copy
    only — never mutates/truncates the on-disk research artifact. Non-string
    values pass through unchanged (defensive; the corpus is untyped YAML)."""
    if not isinstance(value, str) or len(value) <= limit:
        return value
    return value[:limit].rstrip() + "…"


def _trim_prompt_item(item: dict[str, Any]) -> dict[str, Any]:
    """One video/slideshow corpus item, shrunk for the N-A prompt: heavy
    URL/hash fields dropped, every caption-shaped field trimmed to
    ``PROMPT_CAPTION_TRIM_CHARS``, and ``panel_texts`` both capped in count
    and trimmed per-entry."""
    if not isinstance(item, dict):
        return item
    trimmed = {k: v for k, v in item.items() if k not in _PROMPT_DROP_FIELDS}
    for field_name in _PROMPT_CAPTION_FIELDS:
        if field_name in trimmed:
            trimmed[field_name] = _trim_caption_text(trimmed.get(field_name))
    panel_texts = trimmed.get("panel_texts")
    if isinstance(panel_texts, list):
        trimmed["panel_texts"] = [
            _trim_caption_text(t) for t in panel_texts[:MAX_PANEL_TEXTS_PER_SLIDESHOW]
        ]
    return trimmed


_MATCH_STOPWORDS = {
    "the", "a", "an", "of", "for", "and", "or", "to", "in", "on", "with", "is", "are", "how",
    "why", "what", "this", "that", "new", "your", "you", "it", "as", "at", "by", "from",
}


def _tokens_for_match(text: str) -> set[str]:
    return {t for t in text.lower().split() if len(t) > 2 and t not in _MATCH_STOPWORDS}


def _theme_matches_winning_topics(theme_name: str, winning_topics: list[str]) -> bool:
    """A lightweight, dependency-free (no import of ``hypeagent.ranking``)
    token-overlap match between a Virlo corpus theme's own name and one of
    this run's winning-ranked topic titles (Q6 re-audit R2) — exact string
    equality is common (Virlo theme names flow into ``TopicCandidate``
    titles directly for Virlo-sourced signals) but not guaranteed, since a
    winning topic can equally have come from HN/Google News/Product Hunt/
    Hugging Face clustering. Common stopwords are excluded from the overlap
    test so two unrelated theme names sharing only "for"/"the"/etc. never
    counts as a match."""
    theme_tokens = _tokens_for_match(theme_name)
    for topic in winning_topics:
        if theme_name.strip().lower() == topic.strip().lower():
            return True
        if theme_tokens & _tokens_for_match(topic):
            return True
    return False


def _truncate_corpus(corpus: dict[str, Any], *, winning_topics: list[str] | None = None) -> dict[str, Any]:
    themes = [t for t in (corpus.get("themes") or []) if isinstance(t, dict)]

    # Q6 re-audit R2 (W8-10 Phase 6): N-A now runs after ranking and should
    # study only the themes that WON this run's ranking, deeper. Filtering
    # is best-effort and never removes everything: if ``winning_topics`` is
    # given but matches nothing (e.g. an all-non-Virlo winning set, or a
    # naming mismatch), falling back to the unfiltered theme list is safer
    # than handing the model an empty corpus.
    if winning_topics:
        filtered = [t for t in themes if _theme_matches_winning_topics(str(t.get("name") or ""), winning_topics)]
        if filtered:
            themes = filtered

    themes_sorted = sorted(
        themes,
        key=lambda t: (t.get("confidence") or 0, t.get("video_count") or 0),
        reverse=True,
    )[:MAX_THEMES_IN_PROMPT]
    videos = [
        _trim_prompt_item(v) for v in list(corpus.get("videos") or [])[:MAX_VIDEOS_IN_PROMPT] if isinstance(v, dict)
    ]
    slideshows = [
        _trim_prompt_item(s)
        for s in list(corpus.get("slideshows") or [])[:MAX_SLIDESHOWS_IN_PROMPT]
        if isinstance(s, dict)
    ]
    return {
        "themes": themes_sorted,
        "viral_tactics": list(corpus.get("viral_tactics") or [])[:MAX_VIRAL_TACTICS_IN_PROMPT],
        "top_10_breakdown": corpus.get("top_10_breakdown") or {},
        "connecting_thread": corpus.get("connecting_thread"),
        "key_highlight": corpus.get("key_highlight"),
        "videos": videos,
        "slideshows": slideshows,
    }


# ---------------------------------------------------------------------------
# Prompt construction.
# ---------------------------------------------------------------------------


def _archetype_vocabulary_lines(style_guide: dict[str, Any] | None) -> list[str]:
    if not style_guide:
        return []
    lines = []
    for entry in style_guide.get("visual_archetypes") or []:
        if not isinstance(entry, dict):
            continue
        key = entry.get("key")
        if key:
            lines.append(f"- {key}: {entry.get('desc', '')}".strip())
    return lines


def _reject_list_lines(style_guide: dict[str, Any] | None) -> list[str]:
    if not style_guide:
        return []
    return [str(x) for x in (style_guide.get("reject") or [])]


def build_analyst_prompt(
    *,
    corpus: dict[str, Any],
    style_guide: dict[str, Any] | None,
    image_paths: list[Path] | list[SelectedImage],
    winning_topics: list[str] | None = None,
) -> tuple[str, list[dict[str, Any]], str]:
    """Returns ``(system, user_content_parts, schema_hint)`` for
    ``LlmClient.call_json``. ``image_paths`` accepts either plain
    ``Path``s (unlabeled — legacy callers) or :class:`SelectedImage`
    (labeled with item/views/caption, W8-10 Phase 8)."""
    truncated = _truncate_corpus(corpus, winning_topics=winning_topics)
    archetype_lines = _archetype_vocabulary_lines(style_guide)
    reject_lines = _reject_list_lines(style_guide)
    corpus_yaml = yaml.safe_dump(truncated, allow_unicode=True, sort_keys=False)

    images: list[SelectedImage] = [
        p if isinstance(p, SelectedImage)
        else SelectedImage(
            path=p,
            entry=virlo_collector.MediaManifestEntry(
                filename=Path(p).name, item_id=None, item_kind="unknown",
                panel_index=None, views=0, theme_key=None, caption=None,
            ),
        )
        for p in image_paths
    ]

    lines: list[str] = [
        "This run's Virlo short-form-trends research corpus (themes, tactics, top videos/slideshows "
        "with their captions/hook texts/panel texts, all views-sorted, deterministically truncated"
        + (
            ", filtered to this run's ranking-winning themes"
            if winning_topics else ""
        )
        + "):",
        "",
        corpus_yaml,
        "",
    ]
    if winning_topics:
        lines.append(
            "This run's ranking already picked the winning topics below — study THESE themes deeper "
            "rather than spreading attention across the whole corpus:"
        )
        lines.extend(f"- {t}" for t in winning_topics)
        lines.append("")
    if archetype_lines:
        lines.append(
            "Our own visual-archetype vocabulary — map 'visual_archetypes_seen' onto these keys "
            "wherever they genuinely match what you see in the images/descriptions below; note a "
            "pattern outside this vocabulary in plain words if it does not match any of these:"
        )
        lines.extend(archetype_lines)
        lines.append("")
    if reject_lines:
        lines.append(
            "Our brand's standing reject list — if you observe any of these tactics in the corpus, "
            "name them in 'global.do_not_do' as a warning to the downstream copywriter:"
        )
        lines.extend(f"- {r}" for r in reject_lines)
        lines.append("")
    lines.append(
        "platform_norms: this corpus is overwhelmingly TikTok-heavy evidence (Virlo covers short-form "
        "video). For each theme, OMIT any of linkedin/instagram_feed/tiktok entirely from "
        "'platform_norms' when you have no real evidence for it — never write a placeholder line like "
        "'not observed in corpus'. For every platform_norms entry you DO include, name which platform's "
        "evidence it is actually based on in the text itself (e.g. 'tiktok evidence: hook + screenshot')."
    )
    lines.append("")
    if images:
        lines.append(
            f"{len(images)} representative thumbnail/carousel-panel image(s) from this corpus follow, "
            "each preceded by a label naming which post it came from. For EACH image, also add one "
            "entry to 'analyzed_items' keyed by that image's number (0-based 'image_index' matching the "
            "label below) with: post_kind, person{present,prominence,face_visible,framing,count}, "
            "logos{present,kind,names,treatment}, visual_style{ground,realism,lighting,color_key}, "
            "text_treatment{density,style,placement,has_numbering,verbatim_sample}, "
            "environment{setting,aspiration_signal}, confidence (0-1), summary (plain words: what is "
            "this creative actually about, fusing what you see with its caption/hook/panel text?), and "
            "consists_of (a short list inventorying what it's built from: person/hands/face, text "
            "overlays + their treatment, app UI, logos, setting/environment, color world, props). Use "
            "the vocabulary below where it genuinely fits; if nothing fits, use a short plain-word label "
            "instead of forcing one of these — never invent a different JSON shape."
        )
        lines.extend(f"- {v}" for v in _ANALYZED_ITEM_VOCAB_LINES)
        lines.append("")
    user_parts: list[dict[str, Any]] = [llm_module.text_content_part("\n".join(lines))]
    for idx, image in enumerate(images):
        entry = image.entry
        caption = _trim_caption_text(entry.caption, limit=200) if entry.caption else "(none)"
        label = (
            f"IMAGE {idx} — item {entry.item_id or 'unknown'}, {entry.item_kind} "
            f"panel {entry.panel_index if entry.panel_index is not None else 'n/a'}, "
            f"{entry.views} views, caption: {caption}"
        )
        user_parts.append(llm_module.text_content_part(label))
        try:
            user_parts.append(llm_module.image_content_part_from_file(image.path))
        except OSError:
            continue
    user_parts.append(
        llm_module.text_content_part(
            "Produce the viral playbook now: per-theme winning hooks/formats/visual archetypes seen/"
            "tools shown/numbers used/platform norms, the global viral-tactics digest/connecting thread/"
            "do-not-do list, and the per-image analyzed_items array described above."
        )
    )
    return SYSTEM_PROMPT, user_parts, SCHEMA_HINT


# ---------------------------------------------------------------------------
# The stage entry point.
# ---------------------------------------------------------------------------


def run_trend_visual_analyst(
    *,
    run_dir: Path,
    media_dir: Path,
    style_guide: dict[str, Any] | None,
    llm_client: LlmClient | None,
    trace: TraceWriter,
    stage: str = "analysis",
    max_images: int = DEFAULT_ANALYST_MAX_IMAGES,
    winning_topics: list[str] | None = None,
) -> ViralPlaybook:
    """N-A's full stage logic (see module docstring for the never-fails-the-
    run contract). Always writes ``analysis/viral_playbook.yaml`` — even a
    skipped/degraded run writes an explicit, empty-but-valid file, so
    ``copy``/``media`` (and a later ``--resume``) always has one consistent
    path to read rather than having to distinguish "never ran" from "ran and
    found nothing".

    ``winning_topics`` (Q6 re-audit R2, W8-10 Phase 6): the representative
    titles of this run's ranking-winning candidates (``stages.stage_ranking``
    -> ``ranking_result.top_by_language``) — ``None``/empty analyzes every
    theme the corpus has, exactly the pre-R2 behaviour."""
    if llm_client is None:
        playbook = ViralPlaybook(skipped=True, skip_reason="LLM disabled for this theme (generation.llm.enabled=false)")
        trace.degrade(stage, condition=playbook.skip_reason or "", caused="copy grounds on style_guide.yaml alone")
        _persist(run_dir, playbook, trace, stage)
        return playbook

    corpus = virlo_collector.load_virlo_corpus(run_dir)
    if corpus is None:
        playbook = ViralPlaybook(skipped=True, skip_reason="no virlo_corpus.yaml on file for this run")
        trace.degrade(stage, condition=playbook.skip_reason or "", caused="copy grounds on style_guide.yaml alone")
        _persist(run_dir, playbook, trace, stage)
        return playbook

    manifest = virlo_collector.load_media_manifest(run_dir)
    images = select_analysis_images(media_dir, max_images=max_images, manifest=manifest)
    system, user_parts, schema_hint = build_analyst_prompt(
        corpus=corpus, style_guide=style_guide, image_paths=images, winning_topics=winning_topics,
    )

    llm_client.set_stage(stage)
    try:
        data = llm_client.call_json(
            "analyst", system=system, user_parts=user_parts, schema_hint=schema_hint,
            purpose="N-A trend & visual analyst — build this run's viral playbook",
        )
    except LlmError as exc:
        playbook = ViralPlaybook(degraded=True, degrade_reason=f"{type(exc).__name__}: {exc}")
        trace.degrade(
            stage, condition=f"analyst LLM call failed: {type(exc).__name__}",
            caused="copy grounds on style_guide.yaml alone",
        )
        _persist(run_dir, playbook, trace, stage)
        return playbook

    playbook = parse_playbook_response(data, images=images)

    # W8-10 Phase 8: attach the deterministic per-theme visual_profile,
    # using the FULL manifest (every downloaded image, not just the subset
    # selected into this prompt) for each theme's "items_available" count.
    items_available_by_theme: dict[str, int] = {}
    for entry in manifest:
        if entry.theme_key:
            items_available_by_theme[entry.theme_key] = items_available_by_theme.get(entry.theme_key, 0) + 1
    attach_visual_profiles(playbook, items_available_by_theme=items_available_by_theme)

    _persist(run_dir, playbook, trace, stage)
    return playbook


def _persist(run_dir: Path, playbook: ViralPlaybook, trace: TraceWriter, stage: str) -> None:
    path = write_viral_playbook(run_dir, playbook)
    raw = path.read_bytes()
    trace.artifact_write(stage, path=str(path), kind="viral_playbook", bytes_=len(raw), sha256=hashlib.sha256(raw).hexdigest())
