"""Virlo short-form social intelligence collector (GOAL_ROADMAP.md M3(a),
ARCHITECTURE_PLAN.md §2.3; sub-path collection added W8-9 Phase 2).

Every read below is free (creation/agent-runs cost credits; this collector
**never POSTs**, and every paginated sub-path gets at most ONE pass per run
— never a poll loop):

- ``GET /v1/trends/digest`` — a global, cross-niche digest of today's
  short-form trends. **Opt-in, off by default** (W8-9): it costs $0.25 and
  was discovered to be the least on-topic surface; ``trends_digest_enabled``
  (theme config) controls it.
- ``GET /v1/agents/{monitor_id}`` — a **read** of a recurring content-
  research-agent monitor. ``analysis_data.themes`` is Virlo's own AI-niche
  synthesis (theme name, tactics, why-it-works, video_count, confidence,
  evidence_video_ids), plus richer monitor-level fields (``viral_tactics``,
  ``top_10_breakdown``, ``connecting_thread``, ``key_highlight``,
  ``timing_analysis``). Per the Virlo MCP playbook, ``finalized: true`` is
  the only trustworthy "done" signal; a monitor whose secondary AI job has
  not finished yet carries ``analysis_data: null`` and is treated as
  not-yet-usable, not as empty. ``monitor_ids`` (theme config) is an
  ordered fallback list — read each in turn, at most once each per run,
  until one is finalized; the first finalized monitor is the one used for
  both theme extraction AND the two sub-paths below.
- ``GET /v1/agents/{monitor_id}/videos`` and ``.../slideshows`` (W8-9
  Phase 2) — paginated (``limit``, ``page``, ``order_by=views`` — verified
  live against the real API), hard page cap from theme config
  (``subpath_page_cap``), fetched ONLY for the one selected finalized
  monitor. Every item's rich fields (full creator caption, hook_text,
  text_overlay_content, summary, panel_texts, metrics, thumbnail/panel CDN
  URLs) are captured into a per-run ``virlo_corpus.yaml`` research artifact
  — **not** pushed through ``RawItem``/Scorecards (the existing theme-based
  ranking flow is unchanged); the corpus is additional input for the
  upcoming LLM analysis stage.

Evidence class (GOAL_ROADMAP.md M3(a)), for the still-unchanged theme-based
``RawItem`` flow: **counted** when a numeric virality/views-shaped metric
exists on the entry (``views_per_hour`` for digest trends, ``video_count``
for monitor themes) — percentiled within this source's own trailing
distribution by the existing generic ``compute_virality`` machinery,
absolute-band fallback before ~14 days of history exist. Falls back to
**ranked/presence-only** (hard confidence ceiling) only if neither entry
shape carries a usable number.

New source family: ``short_form_trends``. Language: ``en`` (global-English
per plan §2.3 — Virlo itself carries no per-item language field on these
endpoints). Creator handles (the one per-trend top exemplar's author, where
present) go through the same HMAC handle-hash path as every other collector
(R4-M7) via ``to_normalized_signal`` -> ``Store.store_signal``; corpus/media
author handles (W8-9) are hashed the same way, directly via
``Store.hash_handle``, since they never pass through ``store_signal``.

The API key resolves via ``VIRLO_API_KEY`` (real environment variable >
repo-root ``.env`` > a legacy key file, ``secrets/virlo.key`` by default —
W8-9 Phase 1) and is used **only** to build the ``Authorization`` header
passed as ``extra_headers`` to ``guarded_fetch`` — it is never placed in the
traced ``request`` dict (that dict is built inside ``guarded_fetch`` itself
and never carries headers), so the allowlist-based trace redaction holds by
construction, not by discipline. Fail-closed: an unresolved key -> this
source degrades (not skipped, not fail-run) and the run continues.

Downloaded media (thumbnails/carousel panels, W8-9 Phase 2) is analysis
input only — never traced by URL (counts/checksums only, per
RUN_TRACE_SPEC §3), never re-published, never copied into a pack — and is
registered with the store's existing 30-day raw-artifact retention job
exactly like an HTTP payload body (``Store.register_raw_artifact``).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from hypeagent.collectors.base import (
    Budget,
    CircuitBreaker,
    CollectContext,
    CollectorRunResult,
    RawItem,
    guarded_fetch,
)

SOURCE = "virlo"
SOURCE_ID_FOR_DENY_CHECK = "virlo"
METHOD = "official API"
BASE_URL = "https://api.virlo.ai"
DIGEST_ENDPOINT = f"{BASE_URL}/v1/trends/digest"
AGENT_ENDPOINT_TEMPLATE = f"{BASE_URL}/v1/agents/{{monitor_id}}"

DEFAULT_MONITOR_ID = "9c96fddf-dc35-4be0-bbd9-12f4d22aea12"  # "AI Trends Tracker" (cycles Sundays)

# W8-9 Phase 2: sub-path pagination. ``order_by=views``/``page``/``limit``
# verified live against the real API (2026-08-07); the API's own observed
# max page size is 100. A hard page cap (theme-configurable,
# ``subpath_page_cap``) always bounds the loop to ONE pass — never a poll.
SUBPATH_PAGE_SIZE = 100
DEFAULT_MEDIA_DOWNLOAD_SLIDESHOWS_CONSIDERED = 3
CORPUS_TOP_VIDEOS = 40
CORPUS_TOP_SLIDESHOWS = 15
VIRLO_CORPUS_FILENAME = "virlo_corpus.yaml"

# W8-8: the rich per-theme / per-monitor fields the pipeline reads the
# monitor payload FOR (name, confidence, video_count, stable_key -- see
# ``_parse_agent_monitor``) versus the fields it currently discards at
# normalization time. Named here, once, so both the collector's own
# extraction note and the process summary's raw-payload fallback
# (``hypeagent.process_summary``) agree on the same vocabulary. W8-9 Phase 2
# actually captures these fields in full into ``virlo_corpus.yaml`` (see
# ``build_virlo_corpus`` below); they remain "unused" only in the sense that
# the theme-based ``RawItem``/ranking/copy flow still never sees them.
UNUSED_THEME_FIELDS: tuple[str, ...] = ("tactics", "why_it_works", "viral_tactics", "top_10_breakdown")
UNUSED_MONITOR_FIELDS: tuple[str, ...] = ("connecting_thread", "timing_analysis", "key_highlight")

VIRLO_EXTRACTION_FILENAME = "virlo_extraction.yaml"

# W8-10 Phase 8 (dynamic inspiration): the image<->item join manifest. Lives
# in the run dir next to ``virlo_corpus.yaml``/``virlo_extraction.yaml`` --
# NOT inside ``virlo_media/`` itself -- so it never perturbs that
# directory's own file-count/retention semantics (the media files there are
# individually registered under the store's 30-day raw-artifact job; this
# manifest is registered the same way ``virlo_corpus.yaml`` already is,
# right below).
VIRLO_MEDIA_MANIFEST_FILENAME = "virlo_media_manifest.yaml"


@dataclass
class VirloExtractionNote:
    """A small, per-run record of what the AI Trends Tracker monitor payload
    actually contained (GOAL_ROADMAP.md W8-8): the themes the pipeline
    extracted (name/confidence/video_count/stable_key — exactly what
    normalization used) plus the *names* of richer fields present on the
    payload but not yet fed into copy (tactics, why_it_works, ...). Never
    copies the rich fields' own text — that is a separate quality milestone
    (see the task note); this is a naming inventory only.

    W8-9 Phase 2 additions: which sub-paths were called this run, and how
    many videos/slideshows/media files were captured — so the process
    summary's §3 can report the fuller collection without re-deriving it."""

    monitor_id: str
    themes: list[dict[str, Any]] = field(default_factory=list)
    unused_fields_present: list[str] = field(default_factory=list)
    endpoints_called: list[dict[str, str]] = field(default_factory=list)
    subpaths_called: list[dict[str, str]] = field(default_factory=list)
    videos_captured: int = 0
    slideshows_captured: int = 0
    media_downloaded: int = 0

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "monitor_id": self.monitor_id,
            "endpoints_called": self.endpoints_called,
            "subpaths_called": self.subpaths_called,
            "themes": self.themes,
            "unused_fields_present_in_raw_payload": self.unused_fields_present,
            "videos_captured": self.videos_captured,
            "slideshows_captured": self.slideshows_captured,
            "media_downloaded": self.media_downloaded,
        }


def build_extraction_note(
    payload: dict[str, Any],
    *,
    monitor_id: str,
    endpoints_called: list[dict[str, str]] | None = None,
    subpaths_called: list[dict[str, str]] | None = None,
    videos_captured: int = 0,
    slideshows_captured: int = 0,
    media_downloaded: int = 0,
) -> VirloExtractionNote | None:
    """Build a :class:`VirloExtractionNote` from one ``/v1/agents/{id}``
    response payload. Returns ``None`` when the monitor is not
    ``finalized`` yet (nothing usable to note) or the payload shape is
    unexpected -- mirrors :func:`_parse_agent_monitor`'s own "not yet
    usable, not empty" posture, but never raises: a malformed/unexpected
    payload degrades to "nothing extracted" rather than blowing up a
    best-effort note.

    Reused by ``hypeagent.process_summary`` to reconstruct this same note
    from a raw payload file on disk when a run's own collection stage never
    parsed the monitor fresh this run (a same-day cache hit, §8.5) — the
    exact situation the hand-written analysis of run 2026-08-07_7ded had to
    resolve by hand."""
    data = payload.get("data") or {}
    if not isinstance(data, dict) or not data.get("finalized"):
        return None
    analysis_data = data.get("analysis_data") or {}
    if not isinstance(analysis_data, dict):
        return None
    themes_raw = analysis_data.get("themes") or []
    if not isinstance(themes_raw, list):
        return None

    themes: list[dict[str, Any]] = []
    unused: set[str] = set()
    for theme in themes_raw:
        if not isinstance(theme, dict):
            continue
        name = theme.get("name")
        if not name:
            continue
        themes.append(
            {
                "name": str(name).strip(),
                "confidence": theme.get("confidence"),
                "video_count": theme.get("video_count"),
                "stable_key": theme.get("stable_key") or name,
            }
        )
        for field_name in UNUSED_THEME_FIELDS:
            if theme.get(field_name):
                unused.add(field_name)
    for field_name in UNUSED_MONITOR_FIELDS:
        if analysis_data.get(field_name):
            unused.add(field_name)

    return VirloExtractionNote(
        monitor_id=monitor_id,
        themes=themes,
        unused_fields_present=sorted(unused),
        endpoints_called=endpoints_called or [],
        subpaths_called=subpaths_called or [],
        videos_captured=videos_captured,
        slideshows_captured=slideshows_captured,
        media_downloaded=media_downloaded,
    )


def write_extraction_note(run_dir: Path, note: VirloExtractionNote) -> Path:
    path = Path(run_dir) / VIRLO_EXTRACTION_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(note.to_yaml_dict(), allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def load_extraction_note(run_dir: Path) -> dict[str, Any] | None:
    """Read back a previously-written ``virlo_extraction.yaml``, or
    ``None`` if this run never wrote one (old engine version, or Virlo was
    disabled/not queried this run) -- the process summary's preferred,
    cheapest source for §3's Virlo block, before it falls back to
    re-parsing a raw payload file."""
    path = Path(run_dir) / VIRLO_EXTRACTION_FILENAME
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def _read_api_key(key_path: Path, *, config_dir: Path | None = None) -> tuple[str | None, str | None]:
    """Returns ``(key, degrade_reason)``. Never raises — a missing/unreadable
    key file is this source's own degrade condition, not a run-level error.

    W8-9 Phase 1: when ``config_dir`` is given, ``VIRLO_API_KEY`` is
    resolved first via :func:`hypeagent.config_load.resolve_secret` (real
    environment variable > repo-root ``.env`` > this legacy key file, in
    that order); ``config_dir=None`` (every test that predates W8-9)
    reproduces the exact old file-only behavior."""
    if config_dir is not None:
        from hypeagent.config_load import resolve_secret

        value, _source = resolve_secret("VIRLO_API_KEY", config_dir=config_dir, legacy_path=key_path)
        if value:
            return value, None

    if not key_path.exists():
        return None, f"Virlo API key file missing at {key_path} — source degraded"
    try:
        text = key_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return None, f"Virlo API key file unreadable at {key_path}: {exc} — source degraded"
    if not text:
        return None, f"Virlo API key file at {key_path} is empty — source degraded"
    return text, None


def collect(
    ctx: CollectContext,
    *,
    family: str,
    key_path: Path,
    config_dir: Path | None = None,
    monitor_id: str = DEFAULT_MONITOR_ID,
    monitor_ids: list[str] | None = None,
    budget_max_calls: int = 4,
    circuit_breaker_threshold: int = 3,
    trends_digest_enabled: bool = True,
    subpath_page_cap: int = 0,
    media_download_cap: int = 0,
) -> CollectorRunResult:
    """Collect Virlo signals for one run.

    Every W8-9 Phase-2 knob defaults to the exact pre-Phase-2 behavior at
    the FUNCTION level (``trends_digest_enabled=True``, ``subpath_page_cap=
    0``, ``media_download_cap=0``, ``monitor_ids=None`` falling back to the
    single ``monitor_id``) — every direct caller that predates this phase
    (every existing test) is unaffected. Theme config (``config_load.
    SourceConfig``) carries the opposite, W8-9-intended defaults
    (``trends_digest_enabled=False``, ``subpath_page_cap=6``,
    ``media_download_cap=24``, an ordered ``monitor_ids`` list) and
    ``stages.py`` wires those through explicitly — the production posture
    changes; the function's own defaults do not.
    """
    api_key, key_error = _read_api_key(Path(key_path), config_dir=config_dir)
    if key_error is not None:
        return CollectorRunResult(source=SOURCE, outcome="degraded", degrade_reason=key_error, items=[], calls_made=0)

    auth_headers = {"Authorization": f"Bearer {api_key}"}
    budget = Budget(max_calls=budget_max_calls)
    circuit_breaker = CircuitBreaker(circuit_breaker_threshold)
    now = datetime.now().astimezone()

    items: list[RawItem] = []
    calls_made = 0
    degrade_reasons: list[str] = []
    endpoints_called: list[dict[str, str]] = []

    # -- 1. GET /v1/trends/digest — opt-in, off by default (W8-9: $0.25) ----
    if not trends_digest_enabled:
        endpoints_called.append(
            {"endpoint": DIGEST_ENDPOINT, "status": "skipped — trends_digest_enabled is false (opt-in, $0.25/read)"}
        )
    else:
        digest_outcome = guarded_fetch(
            store=ctx.store,
            trace=ctx.trace,
            stage=ctx.stage,
            fetcher=ctx.fetcher,
            run_id=ctx.run_id,
            run_date=ctx.run_date,
            theme=ctx.theme,
            source=SOURCE,
            source_id_for_deny_check=SOURCE_ID_FOR_DENY_CHECK,
            deny_list=ctx.deny_list,
            query_sig="trends_digest",
            endpoint=DIGEST_ENDPOINT,
            purpose="fetch Virlo global short-form trends digest for AI-topic hype signal",
            circuit_breaker=circuit_breaker,
            budget=budget,
            extra_headers=auth_headers,
        )
        if digest_outcome.skipped_reason == "denied":
            return CollectorRunResult(
                source=SOURCE, outcome="skip", degrade_reason="special-category deny-list", items=[], calls_made=0
            )
        if digest_outcome.skipped_reason == "idempotent-hit":
            endpoints_called.append({"endpoint": DIGEST_ENDPOINT, "status": "already captured today — fetch skipped"})
        elif digest_outcome.body is None:
            if digest_outcome.skipped_reason not in ("budget-exhausted", "circuit-open"):
                calls_made += 1
            degrade_reasons.append(digest_outcome.error or "trends digest endpoint unavailable")
            endpoints_called.append({"endpoint": DIGEST_ENDPOINT, "status": f"unavailable — {degrade_reasons[-1]}"})
        else:
            calls_made += 1
            endpoints_called.append({"endpoint": DIGEST_ENDPOINT, "status": "fetched this run"})
            if digest_outcome.stale_payload:
                degrade_reasons.append("stale payload suspected (trends digest)")
            try:
                payload = json.loads(digest_outcome.body)
            except (json.JSONDecodeError, TypeError):
                degrade_reasons.append("malformed trends digest payload")
            else:
                items.extend(_parse_digest(payload, family=family, now=now))

    # -- 2. GET /v1/agents/{monitor_id} — ordered fallback list (W8-9) ------
    # Try each configured monitor id in turn, at most once each per run,
    # until one is ``finalized``; that monitor is the one used for BOTH
    # theme extraction and the sub-paths below. A same-day idempotent hit on
    # the FIRST monitor tried means today's decision was already made (and
    # any items it produced already stored) -- stop immediately rather than
    # re-deriving that decision against a different monitor mid-day.
    ids_to_try = list(monitor_ids) if monitor_ids else [monitor_id]
    selected_monitor_id: str | None = None
    selected_payload: dict[str, Any] | None = None

    for mid in ids_to_try:
        agent_endpoint = AGENT_ENDPOINT_TEMPLATE.format(monitor_id=mid)
        agent_outcome = guarded_fetch(
            store=ctx.store,
            trace=ctx.trace,
            stage=ctx.stage,
            fetcher=ctx.fetcher,
            run_id=ctx.run_id,
            run_date=ctx.run_date,
            theme=ctx.theme,
            source=SOURCE,
            source_id_for_deny_check=SOURCE_ID_FOR_DENY_CHECK,
            deny_list=ctx.deny_list,
            query_sig=f"agent:{mid}",
            endpoint=agent_endpoint,
            purpose="read a recurring content-research-agent monitor (ordered fallback list, W8-9)",
            circuit_breaker=circuit_breaker,
            budget=budget,
            extra_headers=auth_headers,
        )
        if agent_outcome.skipped_reason == "idempotent-hit":
            endpoints_called.append({"endpoint": agent_endpoint, "status": "already captured today — fetch skipped"})
            break
        if agent_outcome.skipped_reason in ("budget-exhausted", "circuit-open"):
            break
        if agent_outcome.skipped_reason == "denied":
            continue
        if agent_outcome.body is None:
            calls_made += 1
            reason = agent_outcome.error or "agent monitor endpoint unavailable"
            degrade_reasons.append(f"monitor {mid}: {reason}")
            endpoints_called.append({"endpoint": agent_endpoint, "status": f"unavailable — {reason}"})
            continue
        calls_made += 1
        endpoints_called.append({"endpoint": agent_endpoint, "status": "fetched this run"})
        if agent_outcome.stale_payload:
            degrade_reasons.append(f"stale payload suspected (agent monitor {mid})")
        try:
            payload = json.loads(agent_outcome.body)
        except (json.JSONDecodeError, TypeError):
            degrade_reasons.append(f"malformed agent monitor payload ({mid})")
            continue
        parsed, reason = _parse_agent_monitor(payload, family=family, monitor_id=mid, now=now)
        if reason is not None:
            # Not finalized (or an unexpected shape) — fall through to the
            # next configured monitor id, exactly the "may not have a
            # finalized run yet" fallback W8-9 asked for.
            degrade_reasons.append(f"monitor {mid}: {reason}")
            continue
        items.extend(parsed)
        selected_monitor_id = mid
        selected_payload = payload
        break

    # -- 3. Sub-paths /videos, /slideshows — selected finalized monitor only,
    #    paginated, hard cap, ONE pass (W8-9 Phase 2) ------------------------
    videos_raw: list[dict[str, Any]] = []
    slideshows_raw: list[dict[str, Any]] = []
    subpath_endpoints: list[dict[str, str]] = []

    if selected_monitor_id is not None and subpath_page_cap > 0:
        v_entries, v_endpoints, v_degrades, v_calls = _fetch_subpath_pages(
            ctx=ctx,
            circuit_breaker=circuit_breaker,
            budget=budget,
            auth_headers=auth_headers,
            monitor_id=selected_monitor_id,
            subpath="videos",
            list_key="videos",
            page_cap=subpath_page_cap,
        )
        s_entries, s_endpoints, s_degrades, s_calls = _fetch_subpath_pages(
            ctx=ctx,
            circuit_breaker=circuit_breaker,
            budget=budget,
            auth_headers=auth_headers,
            monitor_id=selected_monitor_id,
            subpath="slideshows",
            list_key="slideshows",
            page_cap=subpath_page_cap,
        )
        calls_made += v_calls + s_calls
        subpath_endpoints = v_endpoints + s_endpoints
        endpoints_called.extend(subpath_endpoints)
        degrade_reasons.extend(v_degrades)
        degrade_reasons.extend(s_degrades)

        hash_handle = ctx.store.hash_handle
        videos_raw = [
            parsed_video
            for entry in v_entries
            if (parsed_video := _parse_video_entry(entry, hash_handle=hash_handle)) is not None
        ]
        slideshows_raw = [
            parsed_slideshow
            for entry in s_entries
            if (parsed_slideshow := _parse_slideshow_entry(entry, hash_handle=hash_handle)) is not None
        ]

    # -- 4. Persist the rich research artifact (W8-9 Phase 2) ---------------
    if selected_monitor_id is not None and selected_payload is not None and ctx.run_dir is not None and subpath_page_cap > 0:
        try:
            corpus = build_virlo_corpus(
                monitor_id=selected_monitor_id,
                payload=selected_payload,
                videos=videos_raw,
                slideshows=slideshows_raw,
                subpaths_called=subpath_endpoints,
            )
            corpus_path = write_virlo_corpus(Path(ctx.run_dir), corpus)
            ctx.store.register_raw_artifact(
                run_id=ctx.run_id,
                run_date=ctx.run_date,
                theme=ctx.theme,
                source=SOURCE,
                query_sig=f"corpus:{selected_monitor_id}",
                endpoint="virlo-corpus",
                path=corpus_path,
            )
        except OSError:
            pass

    # -- 5. Download top-K media for offline vision-LLM analysis input ------
    media_downloaded = 0
    if selected_monitor_id is not None and media_download_cap > 0 and (videos_raw or slideshows_raw):
        videos_sorted = sorted(videos_raw, key=lambda v: v.get("views") or 0, reverse=True)
        slideshows_sorted = sorted(slideshows_raw, key=lambda s: s.get("views") or 0, reverse=True)
        downloads = _select_media_downloads(
            videos_sorted=videos_sorted, slideshows_sorted=slideshows_sorted, cap=media_download_cap
        )
        if downloads:
            analysis_data_block: dict[str, Any] = {}
            if selected_payload is not None:
                data_block = selected_payload.get("data") or {}
                if isinstance(data_block, dict):
                    analysis_data_block = data_block.get("analysis_data") or {}
            theme_map = _video_theme_key_map(analysis_data_block if isinstance(analysis_data_block, dict) else {})
            succeeded, failed, manifest_entries = _download_media(ctx=ctx, downloads=downloads, theme_map=theme_map)
            media_downloaded = succeeded
            ctx.trace.decision(
                ctx.stage,
                decision=(
                    f"virlo media download: {succeeded} succeeded, {failed} failed "
                    f"(of {len(downloads)} selected, cap {media_download_cap})"
                ),
                rule=(
                    "RUN_TRACE_SPEC §3: no third-party URLs/handles enter the trace — counts only; "
                    "files retained 30 days under logs/artifacts/raw/<run_id>/virlo_media/"
                ),
            )
            if failed:
                degrade_reasons.append(f"virlo media download: {failed} of {len(downloads)} selected image(s) failed")

            # W8-10 Phase 8: the image<->item join manifest, written next to
            # virlo_corpus.yaml/virlo_extraction.yaml (never inside
            # virlo_media/ itself -- see VIRLO_MEDIA_MANIFEST_FILENAME's own
            # docstring). Best-effort, same posture as the corpus write above.
            if manifest_entries and ctx.run_dir is not None:
                try:
                    manifest_path = write_media_manifest(Path(ctx.run_dir), manifest_entries)
                    ctx.store.register_raw_artifact(
                        run_id=ctx.run_id,
                        run_date=ctx.run_date,
                        theme=ctx.theme,
                        source=SOURCE,
                        query_sig=f"media-manifest:{selected_monitor_id}",
                        endpoint="virlo-media-manifest",
                        path=manifest_path,
                    )
                except Exception:
                    pass

    # -- 6. Extraction note (W8-8, extended W8-9 with sub-path counts) ------
    if selected_monitor_id is not None and selected_payload is not None and ctx.run_dir is not None:
        try:
            note = build_extraction_note(
                selected_payload,
                monitor_id=selected_monitor_id,
                endpoints_called=list(endpoints_called),
                subpaths_called=subpath_endpoints,
                videos_captured=len(videos_raw),
                slideshows_captured=len(slideshows_raw),
                media_downloaded=media_downloaded,
            )
            if note is not None:
                write_extraction_note(ctx.run_dir, note)
        except OSError:
            pass

    outcome_class = "degraded" if degrade_reasons else "ok"
    return CollectorRunResult(
        source=SOURCE,
        outcome=outcome_class,
        degrade_reason="; ".join(degrade_reasons) if degrade_reasons else None,
        items=items,
        calls_made=calls_made,
    )


def _parse_digest(payload: dict[str, Any], *, family: str, now: datetime) -> list[RawItem]:
    items: list[RawItem] = []
    groups = payload.get("data") or []
    if not isinstance(groups, list):
        return items
    for group in groups:
        if not isinstance(group, dict):
            continue
        trends = group.get("trends") or []
        for entry in trends:
            if not isinstance(entry, dict):
                continue
            trend = entry.get("trend") or {}
            name = trend.get("name")
            if not name:
                continue
            momentum = entry.get("momentum") or {}
            views_per_hour = momentum.get("views_per_hour")
            momentum_score = momentum.get("score")
            exemplars = entry.get("top_exemplars") or []
            top = exemplars[0] if exemplars else {}
            trend_id = entry.get("trend_id") or entry.get("id") or "unknown"
            url = top.get("url") or f"https://virlo.ai/trends/{trend_id}"
            author = (top.get("author") or {}).get("username")

            metrics: dict[str, Any] = {}
            if isinstance(views_per_hour, (int, float)):
                evidence_class = "counted"
                metrics["score"] = views_per_hour
            else:
                evidence_class = "ranked"
                metrics["rank"] = entry.get("ranking", 999)
            if isinstance(momentum_score, (int, float)):
                metrics["momentum_score"] = momentum_score
            if isinstance(entry.get("velocity_today_count"), (int, float)):
                metrics["velocity_today_count"] = entry["velocity_today_count"]

            description = (trend.get("description") or name).strip()
            items.append(
                RawItem(
                    platform_id=entry.get("id") or trend_id,
                    url=url,
                    title=name.strip(),
                    excerpt=description[:500],
                    author_handle=author,
                    metrics=metrics,
                    language="en",
                    source=SOURCE,
                    source_family=family,
                    evidence_class=evidence_class,
                    retrieved_at=now,
                    method=METHOD,
                )
            )
    return items


def _parse_agent_monitor(
    payload: dict[str, Any], *, family: str, monitor_id: str, now: datetime
) -> tuple[list[RawItem], str | None]:
    data = payload.get("data") or {}
    if not isinstance(data, dict):
        return [], "unexpected agent monitor payload shape"

    # The Virlo MCP playbook's canonical done signal: "finalized: true" —
    # status "completed" alone can still mean secondary AI jobs are running,
    # and a null analysis_data means "not yet", never "no data" (§ discovery
    # notes above).
    if not data.get("finalized"):
        return [], "AI Trends Tracker monitor analysis not finalized yet — treated as not-yet-usable, not empty"

    analysis_data = data.get("analysis_data") or {}
    themes = analysis_data.get("themes") or []
    if not isinstance(themes, list):
        return [], "unexpected agent monitor analysis_data shape"

    items: list[RawItem] = []
    for theme in themes:
        if not isinstance(theme, dict):
            continue
        name = theme.get("name")
        if not name:
            continue
        stable_key = theme.get("stable_key") or name
        video_count = theme.get("video_count")
        confidence = theme.get("confidence")
        tactics = theme.get("tactics") or []
        why = (theme.get("why_it_works") or "").strip()
        tactics_line = "; ".join(str(t) for t in tactics[:5])
        excerpt = f"{why} Tactics: {tactics_line}".strip()[:500]

        metrics: dict[str, Any] = {}
        if isinstance(video_count, (int, float)):
            evidence_class = "counted"
            metrics["score"] = video_count
            metrics["video_count"] = video_count
        else:
            evidence_class = "ranked"
            metrics["rank"] = 999
        if isinstance(confidence, (int, float)):
            metrics["confidence"] = confidence

        items.append(
            RawItem(
                platform_id=f"{monitor_id}:{stable_key}",
                url=f"https://virlo.ai/agents/{monitor_id}#{stable_key}",
                title=str(name).strip(),
                excerpt=excerpt,
                author_handle=None,
                metrics=metrics,
                language="en",
                source=SOURCE,
                source_family=family,
                evidence_class=evidence_class,
                retrieved_at=now,
                method="official API (recurring content-research-agent monitor)",
            )
        )
    return items, None


# ---------------------------------------------------------------------------
# W8-9 Phase 2 — sub-path pagination, corpus building, media selection.
# ---------------------------------------------------------------------------


def _fetch_subpath_pages(
    *,
    ctx: CollectContext,
    circuit_breaker: CircuitBreaker,
    budget: Budget,
    auth_headers: dict[str, str],
    monitor_id: str,
    subpath: str,
    list_key: str,
    page_cap: int,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[str], int]:
    """Fetch ``/v1/agents/{monitor_id}/{subpath}`` (``videos`` or
    ``slideshows``), ordered by views, one page at a time, up to
    ``page_cap`` pages — exactly ONE pass, never a poll loop. Stops early on
    a same-day idempotent hit, an exhausted budget/open circuit, a fetch
    error, or a short/empty page (the API's own "last page" signal).
    Returns ``(raw_entries, endpoints_called, degrade_reasons,
    calls_made)``."""
    entries: list[dict[str, Any]] = []
    endpoints_called: list[dict[str, str]] = []
    degrade_reasons: list[str] = []
    calls_made = 0

    for page in range(1, max(1, page_cap) + 1):
        endpoint = (
            f"{BASE_URL}/v1/agents/{monitor_id}/{subpath}"
            f"?limit={SUBPATH_PAGE_SIZE}&order_by=views&page={page}"
        )
        outcome = guarded_fetch(
            store=ctx.store,
            trace=ctx.trace,
            stage=ctx.stage,
            fetcher=ctx.fetcher,
            run_id=ctx.run_id,
            run_date=ctx.run_date,
            theme=ctx.theme,
            source=SOURCE,
            source_id_for_deny_check=SOURCE_ID_FOR_DENY_CHECK,
            deny_list=ctx.deny_list,
            query_sig=f"agent:{monitor_id}:{subpath}:page{page}",
            endpoint=endpoint,
            purpose=f"read monitor {subpath} sub-path, page {page} (ordered by views, one pass per run)",
            circuit_breaker=circuit_breaker,
            budget=budget,
            extra_headers=auth_headers,
        )
        if outcome.skipped_reason == "idempotent-hit":
            endpoints_called.append({"endpoint": endpoint, "status": "already captured today — fetch skipped"})
            break
        if outcome.skipped_reason in ("budget-exhausted", "circuit-open", "denied"):
            break
        if outcome.body is None:
            calls_made += 1
            reason = outcome.error or f"{subpath} sub-path page {page} unavailable"
            degrade_reasons.append(reason)
            endpoints_called.append({"endpoint": endpoint, "status": f"unavailable — {reason}"})
            break
        calls_made += 1
        endpoints_called.append({"endpoint": endpoint, "status": "fetched this run"})
        try:
            payload = json.loads(outcome.body)
        except (json.JSONDecodeError, TypeError):
            degrade_reasons.append(f"malformed {subpath} sub-path payload (page {page})")
            break
        data = payload.get("data") or {}
        page_items = data.get(list_key)
        if not isinstance(page_items, list) or not page_items:
            break
        entries.extend(entry for entry in page_items if isinstance(entry, dict))
        if len(page_items) < SUBPATH_PAGE_SIZE:
            break  # short page -- the API's own "last page" signal

    return entries, endpoints_called, degrade_reasons, calls_made


def _common_entry_fields(entry: dict[str, Any], *, hash_handle: Any) -> dict[str, Any]:
    author = entry.get("author") or {}
    raw_handle = author.get("username") if isinstance(author, dict) else None
    return {
        "id": entry.get("id"),
        "url": entry.get("url"),
        "platform": entry.get("platform"),
        "views": entry.get("views") or 0,
        "likes": entry.get("likes"),
        "shares": entry.get("shares"),
        "comments": entry.get("comments"),
        "bookmarks": entry.get("bookmarks"),
        "description": entry.get("description") or "",
        "thumbnail_url": entry.get("thumbnail_url"),
        "publish_date": entry.get("publish_date"),
        "author_handle_hash": hash_handle(raw_handle) if raw_handle else None,
        "hashtags": list(entry.get("hashtags") or []),
    }


def _parse_video_entry(entry: dict[str, Any], *, hash_handle: Any) -> dict[str, Any] | None:
    """One ``/videos`` entry -> a plain corpus dict (never a ``RawItem`` —
    this track never touches ranking/Scorecards, W8-9). Author handle is
    hashed immediately via the store's existing HMAC convention, since this
    item never passes through ``to_normalized_signal``/``store_signal``."""
    if not isinstance(entry, dict):
        return None
    item = _common_entry_fields(entry, hash_handle=hash_handle)
    intel = entry.get("intelligence")
    if entry.get("intelligence_status") == "ready" and isinstance(intel, dict):
        item["hook_text"] = intel.get("hook_text")
        item["text_overlay_content"] = intel.get("text_overlay_content")
        item["summary"] = intel.get("summary")
    return item


def _parse_slideshow_entry(entry: dict[str, Any], *, hash_handle: Any) -> dict[str, Any] | None:
    """One ``/slideshows`` entry -> a plain corpus dict, adding the panel
    image URLs (public CDN, no auth) and, where ready, the verbatim
    per-panel texts."""
    if not isinstance(entry, dict):
        return None
    item = _common_entry_fields(entry, hash_handle=hash_handle)
    images = entry.get("images") or []
    image_urls = [
        img.get("image_url") for img in images if isinstance(img, dict) and img.get("image_url")
    ]
    item["image_urls"] = image_urls
    item["panel_count"] = len(image_urls)
    intel = entry.get("intelligence")
    if entry.get("intelligence_status") == "ready" and isinstance(intel, dict):
        item["hook_text"] = intel.get("hook_text")
        item["summary"] = intel.get("summary")
        item["panel_texts"] = list(intel.get("panel_texts") or [])
        item["narrative_arc"] = intel.get("narrative_arc")
        item["text_density"] = intel.get("text_density")
    return item


def _theme_richness(analysis_data: dict[str, Any]) -> dict[str, Any]:
    """The full, untruncated per-monitor theme richness (GOAL_ROADMAP.md
    W8-9): every ``tactics`` entry, the complete ``why_it_works`` line, plus
    the monitor-level fields the theme-based ``RawItem`` flow has always
    discarded (``viral_tactics``, ``top_10_breakdown``, ``connecting_
    thread``, ``key_highlight``, ``timing_analysis``). No 500-char
    truncation anywhere here (unlike ``_parse_agent_monitor``'s own
    ``RawItem.excerpt``, which stays as-is for the unchanged ranking flow)."""
    themes_raw = analysis_data.get("themes") or []
    themes: list[dict[str, Any]] = []
    for theme in themes_raw:
        if not isinstance(theme, dict):
            continue
        themes.append(
            {
                "name": theme.get("name"),
                "stable_key": theme.get("stable_key") or theme.get("name"),
                "confidence": theme.get("confidence"),
                "video_count": theme.get("video_count"),
                "tactics": list(theme.get("tactics") or []),
                "why_it_works": theme.get("why_it_works"),
                "evidence_video_ids": list(theme.get("evidence_video_ids") or []),
            }
        )
    return {
        "themes": themes,
        "viral_tactics": list(analysis_data.get("viral_tactics") or []),
        "top_10_breakdown": analysis_data.get("top_10_breakdown") or {},
        "connecting_thread": analysis_data.get("connecting_thread"),
        "key_highlight": analysis_data.get("key_highlight"),
        "timing_analysis": analysis_data.get("timing_analysis") or {},
    }


def build_virlo_corpus(
    *,
    monitor_id: str,
    payload: dict[str, Any],
    videos: list[dict[str, Any]],
    slideshows: list[dict[str, Any]],
    subpaths_called: list[dict[str, str]],
) -> dict[str, Any]:
    """Assemble the per-run research artifact (GOAL_ROADMAP.md W8-9): full
    theme richness plus the top items by views per platform, capped so the
    file stays readable (``CORPUS_TOP_VIDEOS``/``CORPUS_TOP_SLIDESHOWS``).
    This is an ADDITIONAL artifact for the upcoming LLM analysis stage — it
    never feeds ranking/Scorecards, which keep reading the unchanged
    theme-based ``RawItem`` flow."""
    data = payload.get("data") or {}
    analysis_data = data.get("analysis_data") or {}
    richness = _theme_richness(analysis_data if isinstance(analysis_data, dict) else {})
    videos_sorted = sorted(videos, key=lambda v: v.get("views") or 0, reverse=True)[:CORPUS_TOP_VIDEOS]
    slideshows_sorted = sorted(slideshows, key=lambda s: s.get("views") or 0, reverse=True)[:CORPUS_TOP_SLIDESHOWS]
    return {
        "monitor_id": monitor_id,
        "monitor_finalized": bool(data.get("finalized")),
        "subpaths_called": subpaths_called,
        **richness,
        "videos": videos_sorted,
        "slideshows": slideshows_sorted,
    }


def write_virlo_corpus(run_dir: Path, corpus: dict[str, Any]) -> Path:
    """Write ``virlo_corpus.yaml`` under the run directory. Verbatim
    third-party text (captions, hook texts, panel texts) is permitted here
    — this is a research artifact under the store's 30-day raw-artifact
    retention (``Store.register_raw_artifact``, called by the caller right
    after this), not a trace (RUN_TRACE_SPEC §3's "no embedded third-party
    text" rule governs the trace, not this artifact)."""
    path = Path(run_dir) / VIRLO_CORPUS_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(corpus, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def load_virlo_corpus(run_dir: Path) -> dict[str, Any] | None:
    """Read back a previously-written ``virlo_corpus.yaml``, or ``None`` if
    this run never wrote one (Phase 2 disabled, no finalized monitor, or an
    older engine version)."""
    path = Path(run_dir) / VIRLO_CORPUS_FILENAME
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


# ---------------------------------------------------------------------------
# W8-10 Phase 8 — the image<->item join manifest: which downloaded filename
# came from which corpus item (video/slideshow panel), at what view count,
# under which theme (when derivable), with a short verbatim caption/
# hook/panel-text snippet for that same item. N-A (``hypeagent.analysis``)
# uses this to select images by views (not hash-sorted filenames), to
# guarantee a video-thumbnail quota, and to label each image in its prompt
# so the model can attribute what it sees back to a real post.
# ---------------------------------------------------------------------------


@dataclass
class MediaManifestEntry:
    """One row of ``virlo_media_manifest.yaml``: a downloaded image file,
    joined back to the corpus item (video or slideshow) it came from."""

    filename: str
    item_id: str | None
    item_kind: str  # "video" | "slideshow"
    panel_index: int | None
    views: int
    theme_key: str | None
    caption: str | None

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "item_id": self.item_id,
            "item_kind": self.item_kind,
            "panel_index": self.panel_index,
            "views": self.views,
            "theme_key": self.theme_key,
            "caption": self.caption,
        }


def write_media_manifest(run_dir: Path, entries: list[MediaManifestEntry]) -> Path:
    """Write ``virlo_media_manifest.yaml`` into ``run_dir`` (the same
    directory ``virlo_corpus.yaml``/``virlo_extraction.yaml`` already live
    in — never inside ``virlo_media/`` itself, see the filename constant's
    docstring above). Verbatim third-party caption/hook/panel-text snippets
    are permitted here for the same reason they are permitted in
    ``virlo_corpus.yaml`` (module docstring: a research artifact under the
    store's 30-day raw-artifact retention, not a trace)."""
    path = Path(run_dir) / VIRLO_MEDIA_MANIFEST_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump({"entries": [e.to_yaml_dict() for e in entries]}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def load_media_manifest(run_dir: Path) -> list[MediaManifestEntry]:
    """Read back a previously-written ``virlo_media_manifest.yaml``, or
    ``[]`` if this run never wrote one (an older engine version, media
    downloads disabled, or no finalized monitor this run) -- never raises;
    a missing/malformed manifest degrades to "nothing joinable", exactly
    the posture ``load_virlo_corpus`` already holds for its own file."""
    path = Path(run_dir) / VIRLO_MEDIA_MANIFEST_FILENAME
    if not path.exists():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return []
    if not isinstance(data, dict):
        return []
    raw_entries = data.get("entries")
    if not isinstance(raw_entries, list):
        return []
    entries: list[MediaManifestEntry] = []
    for raw in raw_entries:
        if not isinstance(raw, dict) or not raw.get("filename"):
            continue
        entries.append(
            MediaManifestEntry(
                filename=str(raw["filename"]),
                item_id=str(raw["item_id"]) if raw.get("item_id") is not None else None,
                item_kind=str(raw.get("item_kind") or "unknown"),
                panel_index=int(raw["panel_index"]) if raw.get("panel_index") is not None else None,
                views=int(raw.get("views") or 0),
                theme_key=str(raw["theme_key"]) if raw.get("theme_key") is not None else None,
                caption=str(raw["caption"]) if raw.get("caption") is not None else None,
            )
        )
    return entries


def _video_theme_key_map(analysis_data: dict[str, Any]) -> dict[str, str]:
    """Best-effort video-id -> theme-name map, derived from each theme's own
    ``evidence_video_ids`` (already captured in full by ``_theme_richness``).
    Slideshows carry no equivalent evidence-linking field on the Virlo API
    today, so slideshow-sourced manifest entries simply get ``theme_key=
    None`` -- a documented, honest gap, not a crash."""
    mapping: dict[str, str] = {}
    themes = analysis_data.get("themes") if isinstance(analysis_data, dict) else None
    if not isinstance(themes, list):
        return mapping
    for theme in themes:
        if not isinstance(theme, dict):
            continue
        name = theme.get("name")
        if not name:
            continue
        for video_id in theme.get("evidence_video_ids") or []:
            if video_id:
                mapping[str(video_id)] = str(name)
    return mapping


def _caption_snippet_for_item(item: dict[str, Any], *, kind: str, panel_index: int | None, limit: int = 200) -> str | None:
    """A short verbatim snippet for the manifest join: the specific panel's
    own text for a slideshow panel (falling back to the item's general
    hook/description), or the item's hook/description/summary for a video
    thumbnail."""
    if kind == "slideshow_panel":
        panel_texts = item.get("panel_texts") or []
        if isinstance(panel_texts, list) and panel_index is not None and 0 <= panel_index < len(panel_texts):
            text = panel_texts[panel_index]
            if text:
                return str(text)[:limit]
    snippet = item.get("hook_text") or item.get("description") or item.get("summary")
    return str(snippet)[:limit] if snippet else None


def _select_media_downloads(
    *,
    videos_sorted: list[dict[str, Any]],
    slideshows_sorted: list[dict[str, Any]],
    cap: int,
) -> list[dict[str, Any]]:
    """Choose which images to download, honoring ``cap`` (GOAL_ROADMAP.md
    W8-9): ALL panels of the top 2-3 slideshows by views (never a partial
    carousel — a slideshow whose full panel set does not fit in the
    remaining budget is skipped entirely, trying the next one), then
    top-viewed video thumbnails filling any remaining budget. Returns an
    ordered list of download descriptors -- ``{"url", "kind", "item",
    "panel_index"}`` -- carrying the source item dict forward (W8-10 Phase
    8) so the manifest join can be built without re-fetching anything."""
    if cap <= 0:
        return []
    selected: list[dict[str, Any]] = []
    remaining = cap

    for slideshow in slideshows_sorted[:DEFAULT_MEDIA_DOWNLOAD_SLIDESHOWS_CONSIDERED]:
        urls = [u for u in (slideshow.get("image_urls") or []) if u]
        if not urls or len(urls) > remaining:
            continue
        for panel_index, url in enumerate(urls):
            selected.append({"url": url, "kind": "slideshow_panel", "item": slideshow, "panel_index": panel_index})
        remaining -= len(urls)
        if remaining <= 0:
            break

    if remaining > 0:
        for video in videos_sorted:
            if remaining <= 0:
                break
            url = video.get("thumbnail_url")
            if url:
                selected.append({"url": url, "kind": "video_thumbnail", "item": video, "panel_index": None})
                remaining -= 1

    return selected


def _extension_from_url(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix and len(suffix) <= 6 and suffix[1:].isalnum():
        return suffix
    return ".bin"


def _download_media(
    *, ctx: CollectContext, downloads: list[dict[str, Any]], theme_map: dict[str, str] | None = None
) -> tuple[int, int, list[MediaManifestEntry]]:
    """Best-effort download of public CDN media (thumbnails/carousel
    panels) for offline vision-LLM analysis input — never re-published,
    never traced by URL (RUN_TRACE_SPEC §3: counts only), registered with
    the store's existing 30-day raw-artifact retention. A per-file failure
    (network error, non-2xx, unwritable disk) degrades gracefully — it
    never raises out of collection. Returns ``(succeeded, failed,
    manifest_entries)`` -- the third element is W8-10 Phase 8's
    image<->item join, one entry per successfully-downloaded file."""
    if not downloads or ctx.run_dir is None:
        return 0, 0, []
    theme_map = theme_map or {}
    media_dir = Path(ctx.store.artifacts_dir) / ctx.run_id / "virlo_media"
    media_dir.mkdir(parents=True, exist_ok=True)
    succeeded = 0
    failed = 0
    manifest_entries: list[MediaManifestEntry] = []
    for descriptor in downloads:
        url = descriptor["url"]
        kind = descriptor["kind"]
        item = descriptor.get("item") or {}
        panel_index = descriptor.get("panel_index")
        try:
            response = ctx.fetcher.fetch(url, method="GET")
        except Exception:
            failed += 1
            continue
        if response.status >= 400 or not response.body:
            failed += 1
            continue
        checksum = hashlib.sha256(response.body).hexdigest()
        file_path = media_dir / f"{kind}_{checksum[:16]}{_extension_from_url(url)}"
        try:
            file_path.write_bytes(response.body)
        except OSError:
            failed += 1
            continue
        try:
            ctx.store.register_raw_artifact(
                run_id=ctx.run_id,
                run_date=ctx.run_date,
                theme=ctx.theme,
                source=SOURCE,
                query_sig=f"media:{checksum[:16]}",
                endpoint=f"virlo-media:{kind}",
                path=file_path,
            )
        except Exception:
            pass  # the file itself is already saved; retention registration is best-effort
        succeeded += 1
        item_id = item.get("id") if isinstance(item, dict) else None
        manifest_entries.append(
            MediaManifestEntry(
                filename=file_path.name,
                item_id=str(item_id) if item_id is not None else None,
                item_kind="slideshow" if kind == "slideshow_panel" else "video",
                panel_index=panel_index,
                views=int(item.get("views") or 0) if isinstance(item, dict) else 0,
                theme_key=theme_map.get(str(item_id)) if item_id is not None else None,
                caption=_caption_snippet_for_item(item, kind=kind, panel_index=panel_index) if isinstance(item, dict) else None,
            )
        )
    return succeeded, failed, manifest_entries
