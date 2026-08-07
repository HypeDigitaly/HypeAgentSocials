"""Shared collector machinery (ARCHITECTURE_PLAN.md §2.2, §2.4, §2.8).

Every collector is built from the same five pieces so the per-source
ladder — primary -> degraded -> skip-with-log, never scraping — is
implemented once:

- ``Fetcher`` — an injectable transport protocol, so every collector runs
  fully offline in tests against fixture payloads (``FixtureFetcher``); the
  production path is ``UrllibFetcher`` (stdlib ``urllib.request`` only).
- ``CircuitBreaker`` — N consecutive failures opens it for the rest of the run.
- ``Budget`` — a declared per-source call ceiling (§2.2).
- ``guarded_fetch`` — the one function that applies conditional requests
  (ETag/Last-Modified from the request log), within-run idempotency (§8.5),
  the pre-collection special-category source deny-list (§2.6 limb (a)), the
  circuit breaker, the budget, and stale-payload detection, while emitting
  the ``api_call``/``api_response`` trace pair for every real HTTP fetch.
- normalization helpers — canonical key, near-dup fingerprint ("simhash-lite"),
  and the deterministic prompt-injection-phrasing veto check.
"""

from __future__ import annotations

import hashlib
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from hypeagent.store import NormalizedSignal, SourceDenyList, Store
from hypeagent.trace import TraceWriter

USER_AGENT = "HypeAgentSocials/0.1 (+research collector; contact: operator)"

# §2.8: "ALL collected text is adversarial input". A small, deterministic
# pattern list for imperative "ignore previous instructions"-family phrasing.
# EN + CS.
_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"ignore (all|the|any)? ?(previous|prior|above) instructions",
        r"disregard (all|the|any)? ?(previous|prior|above) instructions",
        r"you are now",
        r"system prompt",
        r"new instructions:",
        r"act as (an?|the) ",
        r"ignorujte (předchozí|veškeré) instrukce",
        r"nyní jsi",
        r"jednej jako",
    )
]

# Tracking parameters stripped by canonical-URL normalization.
_TRACKING_PARAM_PREFIXES = ("utm_", "gclid", "fbclid", "mc_cid", "mc_eid", "ref", "ref_src")


class FetchResponse:
    """The response half of one HTTP fetch."""

    __slots__ = ("status", "headers", "body", "latency_ms")

    def __init__(self, status: int, headers: dict[str, str], body: bytes, latency_ms: int) -> None:
        self.status = status
        self.headers = headers
        self.body = body
        self.latency_ms = latency_ms


class Fetcher(Protocol):
    """Injectable transport. Production: ``UrllibFetcher``. Tests: a fixture double.

    ``body`` is optional and only meaningful for write-ish methods (used by
    the M3 ``openai-compatible-http`` copy provider's POST); every GET-only
    collector simply never passes it.
    """

    def fetch(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        method: str = "GET",
        body: bytes | None = None,
    ) -> FetchResponse: ...


class FetchError(Exception):
    """Raised by a ``Fetcher`` on transport failure (network error, timeout)."""


class UrllibFetcher:
    """The real, production transport: stdlib ``urllib.request`` only."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    def fetch(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        method: str = "GET",
        body: bytes | None = None,
    ) -> FetchResponse:
        req_headers = {"User-Agent": USER_AGENT}
        req_headers.update(headers or {})
        request = urllib.request.Request(url, data=body, headers=req_headers, method=method)
        start = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as resp:
                response_body = resp.read()
                status = resp.status
                resp_headers = dict(resp.headers.items())
        except urllib.error.HTTPError as exc:
            if exc.code == 304:
                latency_ms = int((time.monotonic() - start) * 1000)
                return FetchResponse(status=304, headers=dict(exc.headers or {}), body=b"", latency_ms=latency_ms)
            raise FetchError(f"HTTP {exc.code} fetching {url}") from exc
        except urllib.error.URLError as exc:
            raise FetchError(f"network error fetching {url}: {exc}") from exc
        latency_ms = int((time.monotonic() - start) * 1000)
        return FetchResponse(status=status, headers=resp_headers, body=response_body, latency_ms=latency_ms)


@dataclass
class FixtureFetcher:
    """An offline, deterministic ``Fetcher`` double for tests.

    ``responses`` maps an exact URL (or a substring key, matched via
    "in") to either a ``FetchResponse`` or a ``FetchError`` instance to
    raise. ``calls`` records every URL fetched, in order, for assertions.
    """

    responses: dict[str, FetchResponse | FetchError | Exception]
    calls: list[str] = field(default_factory=list)
    request_bodies: list[bytes | None] = field(default_factory=list)

    def fetch(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        method: str = "GET",
        body: bytes | None = None,
    ) -> FetchResponse:
        self.calls.append(url)
        self.request_bodies.append(body)
        for key, outcome in self.responses.items():
            if key == url or key in url:
                if isinstance(outcome, Exception):
                    raise outcome
                return outcome
        raise FetchError(f"FixtureFetcher: no fixture registered for {url}")


@dataclass
class Budget:
    """A declared per-source call ceiling for one run (§2.2, §2.3)."""

    max_calls: int
    used: int = 0

    def remaining(self) -> int:
        return max(0, self.max_calls - self.used)

    def has_budget(self) -> bool:
        return self.used < self.max_calls

    def spend(self, n: int = 1) -> None:
        self.used += n


class CircuitBreaker:
    """Per-source circuit breaker: N consecutive failures opens it for the run."""

    def __init__(self, threshold: int) -> None:
        self.threshold = threshold
        self._consecutive_failures = 0
        self._open = False

    @property
    def is_open(self) -> bool:
        return self._open

    def record_success(self) -> None:
        self._consecutive_failures = 0

    def record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.threshold:
            self._open = True


@dataclass
class RawItem:
    """One pre-normalization collected item."""

    platform_id: str | None
    url: str
    title: str
    excerpt: str
    author_handle: str | None
    metrics: dict[str, Any]
    language: str
    source: str
    source_family: str
    evidence_class: str  # counted | ranked
    retrieved_at: datetime
    method: str


@dataclass
class CollectContext:
    """Bundles the pieces every collector needs, so each collector's
    ``collect()`` signature stays short and identical in shape."""

    store: Store
    trace: TraceWriter
    fetcher: Fetcher
    deny_list: SourceDenyList
    run_id: str
    run_date: str
    theme: str
    stage: str = "collection"
    # W8-8: the run directory, so a collector that wants to persist a small
    # per-run extraction note (``collectors/virlo.py``'s
    # ``virlo_extraction.yaml``, read by the process summary) knows where to
    # write it. ``None`` in every existing test/collector that never needed
    # a run-scoped side artifact -- optional and backward compatible.
    run_dir: Path | None = None


@dataclass
class CollectorRunResult:
    """What one collector call returns for one source."""

    source: str
    outcome: str  # ok | degraded | skip
    degrade_reason: str | None
    items: list[RawItem]
    calls_made: int
    queries_denied: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Canonicalization / fingerprinting / injection detection
# ---------------------------------------------------------------------------


def canonicalize_url(url: str) -> str:
    """Strip tracking params, lowercase the host, drop the fragment."""
    parsed = urlparse(url)
    query_pairs = [
        (k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
        if not any(k.lower().startswith(p) for p in _TRACKING_PARAM_PREFIXES)
    ]
    normalized = parsed._replace(
        netloc=parsed.netloc.lower(),
        query=urlencode(sorted(query_pairs)),
        fragment="",
    )
    result = urlunparse(normalized)
    return result.rstrip("/")


def canonical_key_for(*, platform_id: str | None, url: str, source: str) -> str:
    """Platform id when available, else the canonical URL (§2.8)."""
    if platform_id:
        return f"{source}:{platform_id}"
    return f"url:{canonicalize_url(url)}"


_WORD_RE = re.compile(r"[a-zA-Z0-9À-ɏ]+")


def simhash_lite(text: str) -> str:
    """A lightweight near-dup fingerprint over normalized-title tokens.

    Not a full SimHash implementation (no weighting, no learned hyperplanes)
    — a deterministic 64-bit hash over the *set* of lowercased word tokens,
    which is exactly what "near-dup fingerprint (e.g. simhash-lite ...)"
    calls for: title reorderings and minor edits collapse to the same key.
    """
    tokens = sorted(set(_WORD_RE.findall(text.lower())))
    normalized = " ".join(tokens)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def contains_injection(text: str) -> bool:
    """Deterministic pattern check for imperative "ignore previous
    instructions"-family phrasing (§2.8: "injection-style phrasing ... is a
    veto signal on the item")."""
    return any(pattern.search(text) for pattern in _INJECTION_PATTERNS)


def to_normalized_signal(item: RawItem, *, domain: str) -> NormalizedSignal:
    canonical_key = canonical_key_for(platform_id=item.platform_id, url=item.url, source=item.source)
    fingerprint = simhash_lite(item.title)
    injected = contains_injection(f"{item.title} {item.excerpt}")
    return NormalizedSignal(
        canonical_key=canonical_key,
        source=item.source,
        source_family=item.source_family,
        language=item.language,
        title=item.title,
        excerpt=item.excerpt,
        metrics=item.metrics,
        raw_author_handle=item.author_handle,
        near_dup_fingerprint=fingerprint,
        evidence_class=item.evidence_class,
        injection_flagged=injected,
        retrieval_time=item.retrieved_at,
        canonical_link=canonicalize_url(item.url),
        domain=domain,
        method=item.method,
    )


# ---------------------------------------------------------------------------
# The guarded fetch: deny-list, idempotency, conditional requests, circuit
# breaker, budget, stale-payload detection, trace events — once.
# ---------------------------------------------------------------------------


@dataclass
class GuardedFetchOutcome:
    fetched: bool
    skipped_reason: str | None  # "denied" | "idempotent-hit" | "budget-exhausted" | "circuit-open" | None
    body: bytes | None = None
    status: int | None = None
    stale_payload: bool = False
    error: str | None = None


def guarded_fetch(
    *,
    store: Store,
    trace: TraceWriter,
    stage: str,
    fetcher: Fetcher,
    run_id: str,
    run_date: str,
    theme: str,
    source: str,
    source_id_for_deny_check: str,
    deny_list: SourceDenyList,
    query_sig: str,
    endpoint: str,
    purpose: str,
    circuit_breaker: CircuitBreaker,
    budget: Budget,
    method: str = "GET",
    extra_headers: dict[str, str] | None = None,
) -> GuardedFetchOutcome:
    """One policy-guarded HTTP fetch. Returns without touching the network
    at all for a denied source, an idempotent same-day hit, an exhausted
    budget, or an open circuit breaker.

    ``extra_headers`` carries per-source transport headers that must never
    reach the trace (e.g. an ``Authorization: Bearer <key>`` header) — they
    are merged into the outgoing request only, never into the ``api_call``
    trace event's ``request`` dict, which is built and redacted separately
    below and never includes ``headers`` at all.
    """
    if deny_list.is_denied(source_id_for_deny_check):
        trace.decision(
            stage,
            decision=f"source '{source_id_for_deny_check}' skipped — special-category deny-list match",
            rule="ARCHITECTURE_PLAN §2.6 limb (a): source/community deny-list applied before collection",
        )
        return GuardedFetchOutcome(fetched=False, skipped_reason="denied")

    existing = store.find_idempotent_capture(theme=theme, source=source, query_sig=query_sig, run_date=run_date)
    if existing is not None:
        trace.decision(
            stage,
            decision=f"source={source} query={query_sig} already captured today — fetch skipped",
            rule="ARCHITECTURE_PLAN §8.5: within-run idempotency on (theme, source, query signature, run-date)",
        )
        return GuardedFetchOutcome(fetched=False, skipped_reason="idempotent-hit")

    if circuit_breaker.is_open:
        return GuardedFetchOutcome(fetched=False, skipped_reason="circuit-open")

    if not budget.has_budget():
        return GuardedFetchOutcome(fetched=False, skipped_reason="budget-exhausted")

    headers: dict[str, str] = dict(extra_headers or {})
    prior = store.previous_capture(theme=theme, source=source, query_sig=query_sig, before_run_id=run_id)
    if prior is not None:
        if prior.etag:
            headers["If-None-Match"] = prior.etag
        if prior.last_modified:
            headers["If-Modified-Since"] = prior.last_modified

    call_seq = trace.api_call(
        stage,
        platform=source,
        endpoint=endpoint,
        method=method,
        request={"endpoint": endpoint, "query_sig": query_sig},
        allowed_keys={"endpoint", "query_sig"},
        attempt=1,
        purpose=purpose,
    )
    budget.spend(1)
    try:
        response = fetcher.fetch(endpoint, headers=headers, method=method)
    except FetchError as exc:
        circuit_breaker.record_failure()
        trace.api_response(
            stage,
            seq_of_call=call_seq,
            status="error",
            latency_ms=0,
            bytes_=None,
            ids_returned=None,
            cost=None,
            outcome_class="transient",
            response_summary={"error": str(exc)},
            allowed_keys={"error"},
        )
        store.record_request(
            run_id=run_id, run_date=run_date, theme=theme, source=source, query_sig=query_sig,
            endpoint=endpoint, method=method, status="failed", rung="primary",
        )
        return GuardedFetchOutcome(fetched=False, skipped_reason=None, error=str(exc))

    trace.api_response(
        stage,
        seq_of_call=call_seq,
        status=response.status,
        latency_ms=response.latency_ms,
        bytes_=len(response.body),
        ids_returned=None,
        cost={"credits": 0},
        outcome_class="ok" if response.status < 400 else "permanent-endpoint",
        response_summary={"bytes": len(response.body)},
        allowed_keys={"bytes"},
    )

    if response.status == 304:
        circuit_breaker.record_success()
        store.record_request(
            run_id=run_id, run_date=run_date, theme=theme, source=source, query_sig=query_sig,
            endpoint=endpoint, method=method, status="ok", rung="primary",
            etag=response.headers.get("ETag"), last_modified=response.headers.get("Last-Modified"),
        )
        return GuardedFetchOutcome(fetched=True, skipped_reason=None, body=None, status=304)

    if response.status >= 400:
        circuit_breaker.record_failure()
        store.record_request(
            run_id=run_id, run_date=run_date, theme=theme, source=source, query_sig=query_sig,
            endpoint=endpoint, method=method, status="failed", rung="primary",
        )
        return GuardedFetchOutcome(fetched=False, skipped_reason=None, status=response.status, error=f"HTTP {response.status}")

    circuit_breaker.record_success()
    stale = False
    if prior is not None and prior.payload_sha256 is not None:
        from hypeagent.store import sha256_hex

        if sha256_hex(response.body) == prior.payload_sha256:
            stale = True

    store.record_request(
        run_id=run_id, run_date=run_date, theme=theme, source=source, query_sig=query_sig,
        endpoint=endpoint, method=method, status="ok", rung="primary",
        etag=response.headers.get("ETag"), last_modified=response.headers.get("Last-Modified"),
        payload=response.body,
    )
    return GuardedFetchOutcome(fetched=True, skipped_reason=None, body=response.body, status=response.status, stale_payload=stale)
