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
from datetime import datetime
from pathlib import Path
from typing import Any

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
        pass  # already captured today; no new items from this endpoint, keep going
    elif digest_outcome.body is None:
        if digest_outcome.skipped_reason not in ("budget-exhausted", "circuit-open"):
            calls_made += 1
        degrade_reasons.append(digest_outcome.error or "trends digest endpoint unavailable")
    else:
        calls_made += 1
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
    if agent_outcome.skipped_reason == "idempotent-hit":
        pass
    elif agent_outcome.body is None:
        if agent_outcome.skipped_reason not in ("budget-exhausted", "circuit-open", "denied"):
            calls_made += 1
        if agent_outcome.skipped_reason != "denied":
            degrade_reasons.append(agent_outcome.error or "agent monitor endpoint unavailable")
    else:
        calls_made += 1
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
