"""Hugging Face Hub collector (ARCHITECTURE_PLAN.md §2.3).

The official free Hub API with trending sorts — model and tool launches
upstream of mainstream coverage. Evidence class: **counted** (likes,
downloads) — "counted evidence" per §2.7's evidence-class table.
"""

from __future__ import annotations

import json
from datetime import datetime

from hypeagent.collectors.base import (
    Budget,
    CircuitBreaker,
    CollectContext,
    CollectorRunResult,
    RawItem,
    guarded_fetch,
)

SOURCE = "hugging_face"
SOURCE_ID_FOR_DENY_CHECK = "hugging_face"
METHOD = "official API"
# NOTE (real-endpoint quirk, found during the Phase-1 smoke run): the Hub API
# rejects ``sort=trending`` outright (HTTP 400, "Invalid sort parameter:
# trending"). The correct value for "what's trending right now" is
# ``trendingScore`` — verified live against https://huggingface.co/api/models.
ENDPOINT_TEMPLATE = "https://huggingface.co/api/models?sort=trendingScore&limit={limit}"


def collect(
    ctx: CollectContext,
    *,
    family: str,
    limit: int = 20,
    circuit_breaker_threshold: int = 3,
) -> CollectorRunResult:
    budget = Budget(max_calls=1)
    circuit_breaker = CircuitBreaker(circuit_breaker_threshold)
    endpoint = ENDPOINT_TEMPLATE.format(limit=limit)

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
        query_sig="trending",
        endpoint=endpoint,
        purpose="fetch Hugging Face Hub trending models for launch-hype signal",
        circuit_breaker=circuit_breaker,
        budget=budget,
    )
    if outcome.skipped_reason == "denied":
        return CollectorRunResult(source=SOURCE, outcome="skip", degrade_reason="special-category deny-list", items=[], calls_made=0)
    if outcome.skipped_reason == "idempotent-hit":
        return CollectorRunResult(source=SOURCE, outcome="ok", degrade_reason=None, items=[], calls_made=0)
    if outcome.body is None:
        return CollectorRunResult(
            source=SOURCE, outcome="degraded", degrade_reason=outcome.error or "trending endpoint unavailable", items=[], calls_made=1
        )

    try:
        payload = json.loads(outcome.body)
    except (json.JSONDecodeError, TypeError):
        return CollectorRunResult(source=SOURCE, outcome="degraded", degrade_reason="malformed trending payload", items=[], calls_made=1)
    if not isinstance(payload, list):
        return CollectorRunResult(source=SOURCE, outcome="degraded", degrade_reason="unexpected trending payload shape", items=[], calls_made=1)

    now = datetime.now().astimezone()
    items: list[RawItem] = []
    for entry in payload:
        model_id = entry.get("id") or entry.get("modelId")
        if not model_id:
            continue
        tags = entry.get("tags") or []
        pipeline_tag = entry.get("pipeline_tag") or ""
        author = model_id.split("/", 1)[0] if "/" in model_id else None
        items.append(
            RawItem(
                platform_id=model_id,
                url=f"https://huggingface.co/{model_id}",
                title=model_id,
                excerpt=f"pipeline: {pipeline_tag}; tags: {', '.join(tags[:8])}" if (pipeline_tag or tags) else model_id,
                author_handle=author,
                metrics={"likes": entry.get("likes", 0), "downloads": entry.get("downloads", 0)},
                language="en",
                source=SOURCE,
                source_family=family,
                evidence_class="counted",
                retrieved_at=now,
                method=METHOD,
            )
        )

    reason = "stale payload suspected" if outcome.stale_payload else None
    outcome_class = "degraded" if reason else "ok"
    return CollectorRunResult(source=SOURCE, outcome=outcome_class, degrade_reason=reason, items=items, calls_made=1)
