"""The run trace log — THE CENTERPIECE (RUN_TRACE_SPEC.md §1-§3).

``TraceWriter`` produces ``trace.jsonl``: append-only, one JSON event per
line, written and flushed as events happen (never buffered until run end),
so a crashed run's trace ends at the crash line — that truncation is the
debugging value, not a defect.

Redaction is allowlist-based, never blocklist-based (§3.1): secrets never
pass through, on the strength of what is *not* named as safe, not on
guessing what the dangerous field names might be.
"""

from __future__ import annotations

import json
import os
import threading
import time
from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

# Fields over this many bytes (serialized) are summarised rather than
# embedded verbatim (§2 api_call row: "bodies over 2 KB summarised with
# byte count + hash").
_LARGE_BODY_THRESHOLD_BYTES = 2048

# §4: a single supervised run may opt into extra debug fields via this
# env flag — never the default, never in scheduled mode.
_TRACE_LEVEL_ENV = "TRACE_LEVEL"


def _now_iso() -> str:
    """ISO-8601 timestamp, millisecond precision, explicit UTC offset."""
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def _sha256_hex(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def summarize_if_large(value: Any, threshold: int = _LARGE_BODY_THRESHOLD_BYTES) -> Any:
    """Summarise an oversized body as byte-count + hash instead of embedding it.

    Used for request/response bodies that would otherwise bloat the trace
    (§2 api_call row).
    """
    if isinstance(value, (bytes, bytearray)):
        raw = bytes(value)
    elif isinstance(value, str):
        raw = value.encode("utf-8")
    else:
        return value
    if len(raw) <= threshold:
        return value
    return {"summarized": True, "bytes": len(raw), "sha256": _sha256_hex(raw)}


def redact(data: Mapping[str, Any] | None, allowed_keys: Iterable[str]) -> dict[str, Any]:
    """Allowlist-based redaction (§3.1): keep only named-safe fields.

    Any key not in ``allowed_keys`` is dropped outright — not masked, not
    partially shown — including ``Authorization``, tokens, cookies and any
    other field nobody thought to name. Nested dicts and lists-of-dicts are
    redacted recursively against the same allowlist.
    """
    if not data:
        return {}
    allowed = set(allowed_keys)
    result: dict[str, Any] = {}
    for key, value in data.items():
        if key not in allowed:
            continue
        if isinstance(value, Mapping):
            result[key] = redact(value, allowed)
        elif isinstance(value, list):
            result[key] = [
                redact(item, allowed) if isinstance(item, Mapping) else item for item in value
            ]
        else:
            result[key] = value
    return result


class TraceWriter:
    """Append-only writer for one run's ``trace.jsonl``.

    Every public method writes exactly one event and returns its ``seq``
    (useful for ``api_call`` -> ``api_response`` pairing via
    ``seq_of_call``). Every write is flushed (and fsync'd where supported)
    immediately, so a crash leaves a valid, truncated trace.
    """

    def __init__(self, path: Path, run_id: str) -> None:
        self.path = Path(path)
        self.run_id = run_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path, "a", encoding="utf-8", newline="\n")
        self._seq = 0
        self._lock = threading.Lock()
        self._stage_starts: dict[str, float] = {}

    # -- low level -----------------------------------------------------

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def _write_event(self, stage: str, event: str, detail: dict[str, Any]) -> int:
        with self._lock:
            seq = self._next_seq()
            record = {
                "ts": _now_iso(),
                "run_id": self.run_id,
                "seq": seq,
                "stage": stage,
                "event": event,
                "detail": detail,
            }
            line = json.dumps(record, ensure_ascii=False)
            self._fh.write(line + "\n")
            self._fh.flush()
            try:
                os.fsync(self._fh.fileno())
            except OSError:
                # Not all filesystems/handles support fsync; flush() already
                # guarantees the OS buffer has the bytes, which is enough
                # for a process crash (as opposed to a power loss).
                pass
            return seq

    def close(self) -> None:
        if not self._fh.closed:
            self._fh.close()

    def __enter__(self) -> "TraceWriter":
        return self

    def __exit__(self, *exc: object) -> bool:
        self.close()
        return False

    # -- event helpers ---------------------------------------------------

    def run_start(
        self,
        *,
        mode: str,
        theme: str | None,
        config_fingerprint: str | None,
        engine_version: str,
        caps_in_force: dict[str, Any] | None = None,
    ) -> int:
        detail: dict[str, Any] = {
            "mode": mode,
            "theme": theme,
            "config_fingerprint": config_fingerprint,
            "engine_version": engine_version,
            "caps_in_force": caps_in_force or {},
        }
        return self._write_event("run", "run_start", detail)

    def stage_start(self, stage: str, **extra: Any) -> int:
        self._stage_starts[stage] = time.monotonic()
        detail = {"stage": stage, **extra}
        return self._write_event(stage, "stage_start", detail)

    def stage_end(
        self,
        stage: str,
        *,
        outcome: str,
        items_in: int,
        items_out: int,
        input_refs: list[dict[str, Any]] | None = None,
        output_refs: list[dict[str, Any]] | None = None,
        **extra: Any,
    ) -> int:
        start = self._stage_starts.pop(stage, None)
        duration_ms = int((time.monotonic() - start) * 1000) if start is not None else None
        detail: dict[str, Any] = {
            "stage": stage,
            "outcome": outcome,
            "duration_ms": duration_ms,
            "items_in": items_in,
            "items_out": items_out,
            "input_refs": input_refs or [],
            "output_refs": output_refs or [],
            **extra,
        }
        return self._write_event(stage, "stage_end", detail)

    def api_call(
        self,
        stage: str,
        *,
        platform: str,
        endpoint: str,
        method: str,
        request: Mapping[str, Any] | None,
        allowed_keys: Iterable[str],
        attempt: int,
        purpose: str,
    ) -> int:
        redacted = redact(request, allowed_keys)
        if "body" in redacted:
            redacted["body"] = summarize_if_large(redacted["body"])
        if os.environ.get(_TRACE_LEVEL_ENV) == "debug" and request is not None:
            body = request.get("body")
            if isinstance(body, (bytes, bytearray, str)):
                raw = body if isinstance(body, (bytes, bytearray)) else body.encode("utf-8")
                redacted["request_raw_bytes"] = len(raw)
        detail = {
            "platform": platform,
            "endpoint": endpoint,
            "method": method,
            "request": redacted,
            "attempt": attempt,
            "purpose": purpose,
        }
        return self._write_event(stage, "api_call", detail)

    def api_response(
        self,
        stage: str,
        *,
        seq_of_call: int,
        status: str | int,
        latency_ms: int,
        bytes_: int | None,
        ids_returned: list[str] | None,
        cost: dict[str, Any] | None,
        outcome_class: str,
        response_summary: Mapping[str, Any] | None,
        allowed_keys: Iterable[str],
    ) -> int:
        detail = {
            "seq_of_call": seq_of_call,
            "status": status,
            "latency_ms": latency_ms,
            "bytes": bytes_,
            "ids_returned": ids_returned or [],
            "cost": cost,
            "outcome_class": outcome_class,
            "response_summary": redact(response_summary, allowed_keys),
        }
        return self._write_event(stage, "api_response", detail)

    def gate_verdict(
        self,
        stage: str,
        *,
        gate: str,
        asset_id: str,
        verdict: str,
        failing_span: str | None = None,
        regeneration_counter: int | None = None,
    ) -> int:
        detail = {
            "gate": gate,
            "asset_id": asset_id,
            "verdict": verdict,
            "failing_span": failing_span,
            "regeneration_counter": regeneration_counter,
        }
        return self._write_event(stage, "gate_verdict", detail)

    def artifact_write(
        self,
        stage: str,
        *,
        path: str,
        kind: str,
        bytes_: int,
        sha256: str,
    ) -> int:
        detail = {"path": path, "kind": kind, "bytes": bytes_, "sha256": sha256}
        return self._write_event(stage, "artifact_write", detail)

    def spend(
        self,
        stage: str,
        *,
        wallet: str,
        expected: float,
        ledger_recorded: float,
        balance_delta: float | None = None,
    ) -> int:
        detail = {
            "wallet": wallet,
            "expected": expected,
            "ledger_recorded": ledger_recorded,
            "balance_delta": balance_delta,
        }
        return self._write_event(stage, "spend", detail)

    def degrade(self, stage: str, *, condition: str, caused: str) -> int:
        detail = {"condition": condition, "caused": caused}
        return self._write_event(stage, "degrade", detail)

    def decision(self, stage: str, *, decision: str, rule: str) -> int:
        detail = {"decision": decision, "rule": rule}
        return self._write_event(stage, "decision", detail)

    def error(
        self,
        stage: str,
        *,
        error_class: str,
        message: str,
        stack_hash: str | None = None,
        retried: bool = False,
        disposition: str = "",
    ) -> int:
        detail = {
            "class": error_class,
            "message": message,
            "stack_hash": stack_hash,
            "retried": retried,
            "disposition": disposition,
        }
        return self._write_event(stage, "error", detail)

    def run_end(self, exit_class: str, *, totals: dict[str, Any]) -> int:
        detail = {"exit_class": exit_class, "totals": totals}
        return self._write_event("run", "run_end", detail)
