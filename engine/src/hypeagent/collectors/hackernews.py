"""Hacker News collector (ARCHITECTURE_PLAN.md §2.3).

Two official free Firebase APIs, no key: ``topstories.json`` for the front
page, ``item/<id>.json`` for each story. Robots permits reads with a
30-second crawl delay, honoured here by **capping item fetches per run**
(the declared per-source budget) rather than by sleeping — a cap is the
budget mechanism §2.2 calls for, and it composes with the global collection
wall-clock ceiling instead of fighting it.

Evidence class: **counted** (score, descendants) — HN is the P0 anchor for
developer/technical discourse and (per §2.3) launch hype and ICP pain
surfaced in comment threads.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from hypeagent.collectors.base import (
    Budget,
    CircuitBreaker,
    CollectContext,
    CollectorRunResult,
    RawItem,
    guarded_fetch,
)

TOPSTORIES_ENDPOINT = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_ENDPOINT_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
SOURCE = "hacker_news"
SOURCE_ID_FOR_DENY_CHECK = "hacker_news"
DOMAIN = "news.ycombinator.com"
METHOD = "official API"


def collect(
    ctx: CollectContext,
    *,
    family: str,
    max_items: int,
    circuit_breaker_threshold: int = 3,
) -> CollectorRunResult:
    circuit_breaker = CircuitBreaker(circuit_breaker_threshold)
    # +1 call budget for the topstories listing itself.
    budget = Budget(max_calls=max_items + 1)

    items: list[RawItem] = []
    calls_made = 0

    listing = guarded_fetch(
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
        query_sig="topstories",
        endpoint=TOPSTORIES_ENDPOINT,
        purpose="fetch Hacker News front page for launch-hype and developer-discourse signal",
        circuit_breaker=circuit_breaker,
        budget=budget,
    )
    if listing.skipped_reason == "denied":
        return CollectorRunResult(source=SOURCE, outcome="skip", degrade_reason="special-category deny-list", items=[], calls_made=0)
    if listing.skipped_reason == "idempotent-hit":
        return CollectorRunResult(source=SOURCE, outcome="ok", degrade_reason=None, items=[], calls_made=0)
    if listing.body is None:
        return CollectorRunResult(
            source=SOURCE, outcome="degraded", degrade_reason=listing.error or "listing unavailable", items=[], calls_made=1
        )
    calls_made += 1

    try:
        story_ids = json.loads(listing.body)
    except (json.JSONDecodeError, TypeError):
        return CollectorRunResult(source=SOURCE, outcome="degraded", degrade_reason="malformed topstories payload", items=[], calls_made=calls_made)

    degrade_reason: str | None = None
    stale_seen = False

    for item_id in story_ids[:max_items]:
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
            query_sig=f"item:{item_id}",
            endpoint=ITEM_ENDPOINT_TEMPLATE.format(item_id=item_id),
            purpose=f"fetch Hacker News item {item_id}",
            circuit_breaker=circuit_breaker,
            budget=budget,
        )
        if outcome.skipped_reason in ("circuit-open", "budget-exhausted", "denied"):
            break
        if outcome.skipped_reason == "idempotent-hit":
            continue
        calls_made += 1
        if outcome.body is None:
            continue
        if outcome.stale_payload:
            stale_seen = True
        try:
            payload = json.loads(outcome.body)
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(payload, dict) or payload.get("type") != "story":
            continue
        title = payload.get("title") or ""
        if not title:
            continue
        url = payload.get("url") or f"https://news.ycombinator.com/item?id={item_id}"
        metrics: dict[str, object] = {"score": payload.get("score", 0), "comments": payload.get("descendants", 0)}
        if payload.get("time"):
            metrics["published_at"] = (
                datetime.fromtimestamp(payload["time"], tz=timezone.utc).astimezone().isoformat()
            )
        items.append(
            RawItem(
                platform_id=str(item_id),
                url=url,
                title=title,
                excerpt=title,
                author_handle=payload.get("by"),
                metrics=metrics,
                language="en",
                source=SOURCE,
                source_family=family,
                evidence_class="counted",
                # retrieved_at is deliberately "now" (when we fetched this
                # item), not HN's own story-creation "time" field — every
                # store retention clock (§2.6) is keyed off retrieval time.
                # See google_news.py's note for the same real-endpoint lesson.
                retrieved_at=datetime.now().astimezone(),
                method=METHOD,
            )
        )

    if circuit_breaker.is_open:
        degrade_reason = "circuit breaker open after consecutive item-fetch failures"
    elif stale_seen:
        degrade_reason = "stale payload suspected"

    outcome_class = "degraded" if degrade_reason else "ok"
    return CollectorRunResult(source=SOURCE, outcome=outcome_class, degrade_reason=degrade_reason, items=items, calls_made=calls_made)
