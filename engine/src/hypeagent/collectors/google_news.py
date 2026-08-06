"""Google News RSS collector (ARCHITECTURE_PLAN.md §2.3).

Free per-query feeds, language-scoped by construction: one set of English
queries (``hl=en-US&gl=US&ceid=US:en``) and one set of Czech queries
(``hl=cs&gl=CZ&ceid=CZ:cs``) — language is stamped at the source level, per
query, never guessed per item. Evidence class: **ranked/presence-only** — no
engagement counts are ever exposed by this feed, so it can never reach the
High evidence band (§2.7).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

from hypeagent.collectors.base import (
    Budget,
    CircuitBreaker,
    CollectContext,
    CollectorRunResult,
    RawItem,
    guarded_fetch,
)

SOURCE = "google_news"
SOURCE_ID_FOR_DENY_CHECK = "google_news"
METHOD = "feed"

_LOCALE_PARAMS = {
    "en": "hl=en-US&gl=US&ceid=US:en",
    "cs": "hl=cs&gl=CZ&ceid=CZ:cs",
}


def build_feed_url(query: str, language: str) -> str:
    locale = _LOCALE_PARAMS.get(language, _LOCALE_PARAMS["en"])
    return f"https://news.google.com/rss/search?q={quote_plus(query)}&{locale}"


def collect(
    ctx: CollectContext,
    *,
    queries_by_language: dict[str, list[str]],
    family_by_language: dict[str, str],
    circuit_breaker_threshold: int = 3,
) -> CollectorRunResult:
    total_queries = sum(len(qs) for qs in queries_by_language.values())
    budget = Budget(max_calls=max(1, total_queries))
    circuit_breaker = CircuitBreaker(circuit_breaker_threshold)

    items: list[RawItem] = []
    calls_made = 0
    degrade_reasons: list[str] = []
    any_ok = False

    for language, queries in queries_by_language.items():
        family = family_by_language.get(language, "editorial_relay")
        for query in queries:
            url = build_feed_url(query, language)
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
                query_sig=f"{language}:{query}",
                endpoint=url,
                purpose=f"poll Google News RSS for '{query}' ({language})",
                circuit_breaker=circuit_breaker,
                budget=budget,
            )
            if outcome.skipped_reason in ("circuit-open", "budget-exhausted"):
                degrade_reasons.append(f"{language}:{query} skipped — {outcome.skipped_reason}")
                continue
            if outcome.skipped_reason in ("idempotent-hit", "denied"):
                continue
            calls_made += 1
            if outcome.body is None:
                degrade_reasons.append(outcome.error or f"{language}:{query} unavailable")
                continue
            any_ok = True
            if outcome.stale_payload:
                degrade_reasons.append("stale payload suspected")
            try:
                parsed_items = _parse_rss(outcome.body, language=language, family=family, query=query)
            except ET.ParseError:
                degrade_reasons.append(f"{language}:{query} malformed feed")
                continue
            items.extend(parsed_items)

    if circuit_breaker.is_open:
        outcome_class = "degraded"
        reason = "circuit breaker open after consecutive feed failures"
    elif degrade_reasons:
        outcome_class = "degraded"
        reason = "; ".join(sorted(set(degrade_reasons)))
    else:
        outcome_class = "ok"
        reason = None

    return CollectorRunResult(source=SOURCE, outcome=outcome_class, degrade_reason=reason, items=items, calls_made=calls_made)


def _parse_rss(body: bytes, *, language: str, family: str, query: str) -> list[RawItem]:
    """Parse one RSS feed body into raw items.

    ``retrieved_at`` is deliberately **the moment we fetched this feed**
    (``now``), not the article's own ``pubDate`` — a real-endpoint lesson
    from the Phase-1 smoke run: Google News frequently relays articles that
    are already weeks old, and every retention clock in the store (§2.6) is
    keyed off "retrieval time", i.e. when *we* collected it, not when the
    source originally published it. Using ``pubDate`` here made old-but-
    freshly-discovered articles expire their verbatim provenance almost
    immediately. The article's own publish date is kept as a metric
    (``published_at``) for future freshness-classification use.
    """
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
        metrics: dict[str, object] = {"rank": rank}
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
                language=language,
                source=SOURCE,
                source_family=family,
                evidence_class="ranked",
                retrieved_at=now,
                method=METHOD,
            )
        )
    return out
