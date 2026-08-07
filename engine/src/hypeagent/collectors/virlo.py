"""Virlo short-form social intelligence collector (GOAL_ROADMAP.md M3(a),
ARCHITECTURE_PLAN.md §2.3).

Two GET reads, both free (creation/agent-runs cost credits; this collector
**never POSTs**):

- ``GET /v1/trends/digest`` — the confirmed primary endpoint: a global,
  cross-niche digest of today's short-form trends (TikTok/Shorts/Reels),
  ranked with a per-trend momentum score and ``views_per_hour``. It is not
  pre-filtered to AI/agency topics — that filtering is the ranking stage's
  job (fit gate + brand-fit floor), exactly as the other collectors' raw,
  unfiltered feeds already work (§2.7).
- ``GET /v1/agents/{monitor_id}`` — a **read** of the existing recurring
  "AI Trends Tracker" content-research-agent monitor (id given in
  GOAL_ROADMAP.md M3(a); cycles Sundays). Its ``analysis_data.themes`` is
  Virlo's own AI-niche synthesis (theme name, tactics, why-it-works,
  video_count, confidence) — discovered live to be materially more
  on-topic for this brand than the generic global digest. Per the Virlo
  MCP playbook, ``finalized: true`` is the only trustworthy "done" signal;
  a monitor whose secondary AI job has not finished yet carries
  ``analysis_data: null`` and is treated as not-yet-usable, not as empty.

Evidence class (GOAL_ROADMAP.md M3(a)): **counted** when a numeric
virality/views-shaped metric exists on the entry (``views_per_hour`` for
digest trends, ``video_count`` for monitor themes) — percentiled within
this source's own trailing distribution by the existing generic
``compute_virality`` machinery, absolute-band fallback before ~14 days of
history exist. Falls back to **ranked/presence-only** (hard confidence
ceiling) only if neither entry shape carries a usable number.

New source family: ``short_form_trends``. Language: ``en`` (global-English
per plan §2.3 — Virlo itself carries no per-item language field on these
two endpoints). Creator handles (the one per-trend top exemplar's author,
where present) go through the same HMAC handle-hash path as every other
collector (R4-M7) via ``to_normalized_signal`` -> ``Store.store_signal``.

The API key is read at run time from a key file (``secrets/virlo.key`` by
default, path is theme-configurable) and is used **only** to build the
``Authorization`` header passed as ``extra_headers`` to ``guarded_fetch`` —
it is never placed in the traced ``request`` dict (that dict is built
inside ``guarded_fetch`` itself and never carries headers), so the
allowlist-based trace redaction holds by construction, not by discipline.
Fail-closed: missing/unreadable/empty key file -> this source degrades
(not skipped, not fail-run) and the run continues.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

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

# W8-8: the rich per-theme / per-monitor fields the pipeline reads the
# monitor payload FOR (name, confidence, video_count, stable_key -- see
# ``_parse_agent_monitor``) versus the fields it currently discards at
# normalization time. Named here, once, so both the collector's own
# extraction note and the process summary's raw-payload fallback
# (``hypeagent.process_summary``) agree on the same vocabulary.
UNUSED_THEME_FIELDS: tuple[str, ...] = ("tactics", "why_it_works", "viral_tactics", "top_10_breakdown")
UNUSED_MONITOR_FIELDS: tuple[str, ...] = ("connecting_thread", "timing_analysis", "key_highlight")

VIRLO_EXTRACTION_FILENAME = "virlo_extraction.yaml"


@dataclass
class VirloExtractionNote:
    """A small, per-run record of what the AI Trends Tracker monitor payload
    actually contained (GOAL_ROADMAP.md W8-8): the themes the pipeline
    extracted (name/confidence/video_count/stable_key — exactly what
    normalization used) plus the *names* of richer fields present on the
    payload but not yet fed into copy (tactics, why_it_works, ...). Never
    copies the rich fields' own text — that is a separate quality milestone
    (see the task note); this is a naming inventory only."""

    monitor_id: str
    themes: list[dict[str, Any]] = field(default_factory=list)
    unused_fields_present: list[str] = field(default_factory=list)
    endpoints_called: list[dict[str, str]] = field(default_factory=list)

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "monitor_id": self.monitor_id,
            "endpoints_called": self.endpoints_called,
            "themes": self.themes,
            "unused_fields_present_in_raw_payload": self.unused_fields_present,
        }


def build_extraction_note(
    payload: dict[str, Any], *, monitor_id: str, endpoints_called: list[dict[str, str]] | None = None
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


def _read_api_key(key_path: Path) -> tuple[str | None, str | None]:
    """Returns ``(key, degrade_reason)``. Never raises — a missing/unreadable
    key file is this source's own degrade condition, not a run-level error."""
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
    monitor_id: str = DEFAULT_MONITOR_ID,
    budget_max_calls: int = 4,
    circuit_breaker_threshold: int = 3,
) -> CollectorRunResult:
    api_key, key_error = _read_api_key(Path(key_path))
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

    # -- 1. GET /v1/trends/digest (primary, confirmed) ----------------------
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
        return CollectorRunResult(source=SOURCE, outcome="skip", degrade_reason="special-category deny-list", items=[], calls_made=0)
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

    # -- 2. GET /v1/agents/{monitor_id} (recurring AI Trends Tracker read) --
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
        query_sig=f"agent:{monitor_id}",
        endpoint=AGENT_ENDPOINT_TEMPLATE.format(monitor_id=monitor_id),
        purpose="read the existing recurring 'AI Trends Tracker' content-research-agent monitor",
        circuit_breaker=circuit_breaker,
        budget=budget,
        extra_headers=auth_headers,
    )
    agent_endpoint = AGENT_ENDPOINT_TEMPLATE.format(monitor_id=monitor_id)
    if agent_outcome.skipped_reason == "idempotent-hit":
        endpoints_called.append({"endpoint": agent_endpoint, "status": "already captured today — fetch skipped"})
    elif agent_outcome.body is None:
        if agent_outcome.skipped_reason not in ("budget-exhausted", "circuit-open", "denied"):
            calls_made += 1
        if agent_outcome.skipped_reason != "denied":
            degrade_reasons.append(agent_outcome.error or "agent monitor endpoint unavailable")
            endpoints_called.append({"endpoint": agent_endpoint, "status": f"unavailable — {degrade_reasons[-1]}"})
    else:
        calls_made += 1
        endpoints_called.append({"endpoint": agent_endpoint, "status": "fetched this run"})
        if agent_outcome.stale_payload:
            degrade_reasons.append("stale payload suspected (agent monitor)")
        try:
            payload = json.loads(agent_outcome.body)
        except (json.JSONDecodeError, TypeError):
            degrade_reasons.append("malformed agent monitor payload")
        else:
            parsed, reason = _parse_agent_monitor(payload, family=family, monitor_id=monitor_id, now=now)
            items.extend(parsed)
            if reason:
                degrade_reasons.append(reason)

            # W8-8: persist the small per-run extraction note (theme names +
            # confidence + video_count, plus the names of richer fields the
            # pipeline still discards at normalization time) alongside
            # normalization -- only possible when the payload was actually
            # parsed fresh this run (a same-day cache hit above never
            # reaches this branch; the process summary's own raw-payload
            # fallback covers that case instead). Best-effort: a malformed
            # run_dir or write failure never fails collection.
            if ctx.run_dir is not None:
                try:
                    note = build_extraction_note(payload, monitor_id=monitor_id, endpoints_called=endpoints_called)
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
