"""N-A Trend & Visual Analyst (W8-9 Q3a; FLOW_MAP.md's ``analysis`` stage).

Runs between ``collection`` and ``ranking`` (FLOW_MAP.md §1) but does not
feed ranking in v1 — ranking stays fully deterministic; this stage's output
feeds ``copy`` instead. One (or, on an unparseable first attempt, two —
``llm.LlmClient``'s own bounded corrective retry) LLM call, batching
everything: the Virlo research corpus (themes/tactics/top videos+captions/
hook texts/panel texts, deterministically truncated) plus up to
``llm.analyst_max_images`` downloaded thumbnails/carousel panels (base64'd)
plus the style guide's own visual-archetype vocabulary, so the model maps
what it sees onto OUR vocabulary rather than inventing a new one.

**This stage never fails the run** (module contract, restated at every
branch below): no corpus on disk, the LLM disabled in config, the run's LLM
budget already exhausted, or the call itself failing all degrade to an
explicit, empty-but-valid ``viral_playbook.yaml`` — copy then grounds on
``style_guide.yaml`` alone, exactly as if this stage did not exist.

Third-party verbatim text (Virlo captions/hook texts/panel texts) legitimately
flows INTO this stage's LLM prompt and MAY appear in ``viral_playbook.yaml``
itself if the model echoes a hook verbatim (both are the "research-artifact
class" the HARD CONSTRAINTS carve out) — but never into a trace event, which
carries counts/keys/hashes only, exactly like ``virlo_corpus.yaml`` already
gets treated.
"""

from __future__ import annotations

import hashlib
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
MAX_THEMES_IN_PROMPT = 5
MAX_VIDEOS_IN_PROMPT = 6
MAX_SLIDESHOWS_IN_PROMPT = 4
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
    '"global": {"viral_tactics_digest": [string], "connecting_thread": string, "do_not_do": [string]}}'
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

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "winning_hooks": self.winning_hooks,
            "formats": self.formats,
            "visual_archetypes_seen": self.visual_archetypes_seen,
            "tools_shown": self.tools_shown,
            "numbers_used": self.numbers_used,
            "platform_norms": self.platform_norms,
        }


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

    def theme_playbook(self, theme_name: str | None) -> ThemePlaybook | None:
        if theme_name:
            for t in self.themes:
                if t.theme == theme_name:
                    return t
        return self.themes[0] if self.themes else None

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
        }


def _coerce_str_list(value: Any, *, limit: int = 20) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v) for v in value if v is not None and str(v).strip()][:limit]


def _coerce_platform_norms(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        str(k): str(v) for k, v in value.items()
        if k in ("linkedin", "instagram_feed", "tiktok") and v
    }


def parse_playbook_response(data: dict[str, Any]) -> ViralPlaybook:
    """Coerce the model's JSON response into a :class:`ViralPlaybook`,
    defensively — an LLM's output shape drift (missing key, wrong type)
    degrades that one field to empty rather than raising."""
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
    return ViralPlaybook(
        themes=themes,
        viral_tactics_digest=_coerce_str_list(
            global_block.get("viral_tactics_digest") or data.get("viral_tactics_digest")
        ),
        connecting_thread=str(connecting_thread) if connecting_thread else None,
        do_not_do=_coerce_str_list(global_block.get("do_not_do") or data.get("do_not_do")),
    )


def _playbook_from_yaml_dict(data: dict[str, Any]) -> ViralPlaybook:
    global_block = data.get("global") or {}
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


def _truncate_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    themes = list(corpus.get("themes") or [])
    themes_sorted = sorted(
        (t for t in themes if isinstance(t, dict)),
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


def select_analysis_images(media_dir: Path, *, max_images: int) -> list[Path]:
    """Prefer full carousel panel sets over single video thumbnails (module
    docstring: "prefer full carousel sets + top thumbnails") — both groups
    are already selected/written in views-descending priority order by
    ``collectors.virlo._select_media_downloads``; this just re-groups by the
    filename's kind prefix and caps the total."""
    media_dir = Path(media_dir)
    if max_images <= 0 or not media_dir.is_dir():
        return []
    files = sorted(p for p in media_dir.iterdir() if p.is_file())
    panels = [p for p in files if p.name.startswith("slideshow_panel_")]
    thumbnails = [p for p in files if p.name.startswith("video_thumbnail_")]
    ordered = panels + thumbnails
    return ordered[:max_images]


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
    *, corpus: dict[str, Any], style_guide: dict[str, Any] | None, image_paths: list[Path]
) -> tuple[str, list[dict[str, Any]], str]:
    """Returns ``(system, user_content_parts, schema_hint)`` for
    ``LlmClient.call_json``."""
    truncated = _truncate_corpus(corpus)
    archetype_lines = _archetype_vocabulary_lines(style_guide)
    reject_lines = _reject_list_lines(style_guide)
    corpus_yaml = yaml.safe_dump(truncated, allow_unicode=True, sort_keys=False)

    lines: list[str] = [
        "This run's Virlo short-form-trends research corpus (themes, tactics, top videos/slideshows "
        "with their captions/hook texts/panel texts, all views-sorted, deterministically truncated):",
        "",
        corpus_yaml,
        "",
    ]
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
    if image_paths:
        lines.append(
            f"{len(image_paths)} representative thumbnail/carousel-panel image(s) from this corpus "
            "follow, for visual pattern analysis."
        )
        lines.append("")
    lines.append(
        "Produce the viral playbook now: per-theme winning hooks/formats/visual archetypes seen/"
        "tools shown/numbers used/platform norms, plus a global viral-tactics digest, connecting "
        "thread, and do-not-do list."
    )

    user_parts: list[dict[str, Any]] = [llm_module.text_content_part("\n".join(lines))]
    for path in image_paths:
        try:
            user_parts.append(llm_module.image_content_part_from_file(path))
        except OSError:
            continue
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
) -> ViralPlaybook:
    """N-A's full stage logic (see module docstring for the never-fails-the-
    run contract). Always writes ``analysis/viral_playbook.yaml`` — even a
    skipped/degraded run writes an explicit, empty-but-valid file, so
    ``copy`` (and a later ``--resume``) always has one consistent path to
    read rather than having to distinguish "never ran" from "ran and found
    nothing"."""
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

    image_paths = select_analysis_images(media_dir, max_images=max_images)
    system, user_parts, schema_hint = build_analyst_prompt(corpus=corpus, style_guide=style_guide, image_paths=image_paths)

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

    playbook = parse_playbook_response(data)
    _persist(run_dir, playbook, trace, stage)
    return playbook


def _persist(run_dir: Path, playbook: ViralPlaybook, trace: TraceWriter, stage: str) -> None:
    path = write_viral_playbook(run_dir, playbook)
    raw = path.read_bytes()
    trace.artifact_write(stage, path=str(path), kind="viral_playbook", bytes_=len(raw), sha256=hashlib.sha256(raw).hexdigest())
