"""Product Hunt public feed collector (ARCHITECTURE_PLAN.md §2.3).

The public feed as the floor (the GraphQL API is gated behind an unresolved
commercial-use question, OD-19, and stays out of Phase 1 entirely).
Evidence class: **ranked/presence-only** — feed order only, no vote counts.
The **launch-pod vote-distortion bias is a known structural discount**
carried as a standing flag on this source's evidence rather than per-item
anomaly detection (§2.3): every item from this source is tagged
``launch_pod_discount`` so ranking applies the confidence ceiling twice —
once for being presence-only, once for the named structural bias.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

from hypeagent.collectors.base import (
    Budget,
    CircuitBreaker,
    CollectContext,
    CollectorRunResult,
    RawItem,
    guarded_fetch,
)

SOURCE = "product_hunt"
SOURCE_ID_FOR_DENY_CHECK = "product_hunt"
METHOD = "feed"
ENDPOINT = "https://www.producthunt.com/feed"


def collect(
    ctx: CollectContext,
    *,
    family: str,
    circuit_breaker_threshold: int = 3,
) -> CollectorRunResult:
    budget = Budget(max_calls=1)
    circuit_breaker = CircuitBreaker(circuit_breaker_threshold)

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
        query_sig="feed",
        endpoint=ENDPOINT,
        purpose="poll Product Hunt public feed for launch-hype signal",
        circuit_breaker=circuit_breaker,
        budget=budget,
    )
    if outcome.skipped_reason == "denied":
        return CollectorRunResult(source=SOURCE, outcome="skip", degrade_reason="special-category deny-list", items=[], calls_made=0)
    if outcome.skipped_reason == "idempotent-hit":
        return CollectorRunResult(source=SOURCE, outcome="ok", degrade_reason=None, items=[], calls_made=0)
    if outcome.body is None:
        return CollectorRunResult(
            source=SOURCE, outcome="degraded", degrade_reason=outcome.error or "feed unavailable", items=[], calls_made=1
        )

    try:
        items = _parse_feed(outcome.body, family=family)
    except ET.ParseError:
        return CollectorRunResult(source=SOURCE, outcome="degraded", degrade_reason="malformed feed", items=[], calls_made=1)

    reason = "stale payload suspected" if outcome.stale_payload else None
    outcome_class = "degraded" if reason else "ok"
    return CollectorRunResult(source=SOURCE, outcome=outcome_class, degrade_reason=reason, items=items, calls_made=1)


def _parse_feed(body: bytes, *, family: str) -> list[RawItem]:
    root = ET.fromstring(body)
    out: list[RawItem] = []
    now = datetime.now().astimezone()
    for rank, item_el in enumerate(root.findall(".//item"), start=1):
        title = (item_el.findtext("title") or "").strip()
        link = (item_el.findtext("link") or "").strip()
        guid = (item_el.findtext("guid") or "").strip() or None
        description = (item_el.findtext("description") or "").strip()
        pub_date_raw = item_el.findtext("pubDate")
        published_at_iso = None
        if pub_date_raw:
            try:
                published_at_iso = parsedate_to_datetime(pub_date_raw).astimezone().isoformat()
            except (TypeError, ValueError):
                published_at_iso = None
        if not title or not link:
            continue
        metrics: dict[str, object] = {"rank": rank, "launch_pod_discount": True}
        if published_at_iso:
            metrics["published_at"] = published_at_iso
        out.append(
            RawItem(
                platform_id=guid,
                url=link,
                title=title,
                excerpt=description[:280] if description else title,
                author_handle=None,
                metrics=metrics,
                language="en",
                source=SOURCE,
                source_family=family,
                evidence_class="ranked",
                # retrieved_at is deliberately "now" (when we fetched this
                # feed), not the launch's own pubDate — see google_news.py's
                # note; every store retention clock is keyed off retrieval
                # time, not source-side publish time.
                retrieved_at=now,
                method="feed",
            )
        )
    return out
