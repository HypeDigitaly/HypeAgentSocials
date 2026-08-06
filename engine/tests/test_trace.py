"""Tests for hypeagent.trace — the run trace centerpiece."""

from __future__ import annotations

import json

from hypeagent.render_trace import load_events
from hypeagent.trace import TraceWriter, redact


def test_seq_is_monotonic(tmp_path):
    tw = TraceWriter(tmp_path / "trace.jsonl", run_id="2026-08-10_a3f2")
    seqs = [
        tw.run_start(mode="interactive", theme=None, config_fingerprint=None, engine_version="0.1.0"),
        tw.stage_start("collection"),
        tw.stage_end("collection", outcome="ok", items_in=0, items_out=0),
        tw.run_end("success", totals={}),
    ]
    tw.close()
    assert seqs == [1, 2, 3, 4]


def test_redaction_drops_non_allowlisted_keys_including_authorization():
    data = {
        "Authorization": "Bearer super-secret-token",
        "endpoint": "/v1/search",
        "cookie": "session=abc123",
        "nested": {"api_key": "shh", "query": "cats"},
    }
    allowed = {"endpoint", "nested"}
    result = redact(data, allowed)
    assert "Authorization" not in result
    assert "cookie" not in result
    assert result["endpoint"] == "/v1/search"
    # nested dict is recursively redacted against the same allowlist
    assert "api_key" not in result["nested"]
    assert "query" not in result["nested"]  # "query" was never allowlisted either


def test_redaction_keeps_allowlisted_nested_fields():
    data = {"nested": {"query": "cats", "secret": "no"}}
    result = redact(data, {"nested", "query"})
    assert result["nested"] == {"query": "cats"}


def test_truncated_trace_file_still_parses_line_by_line(tmp_path):
    path = tmp_path / "trace.jsonl"
    tw = TraceWriter(path, run_id="2026-08-10_a3f2")
    tw.run_start(mode="interactive", theme=None, config_fingerprint=None, engine_version="0.1.0")
    tw.stage_start("collection")
    tw.close()

    # Simulate a crash mid-write: append a truncated, invalid trailing line.
    with open(path, "a", encoding="utf-8") as fh:
        fh.write('{"ts": "2026-08-10T03:14:07.412+02:00", "run_id": "2026-08-1')

    events, malformed = load_events(path)
    assert malformed == 1
    assert len(events) == 2
    assert events[-1]["event"] == "stage_start"


def test_api_call_response_pairing_via_seq_of_call(tmp_path):
    path = tmp_path / "trace.jsonl"
    tw = TraceWriter(path, run_id="2026-08-10_a3f2")
    call_seq = tw.api_call(
        "collection",
        platform="virlo",
        endpoint="/v1/agents",
        method="POST",
        request={"Authorization": "Bearer x", "query": "cats"},
        allowed_keys={"query"},
        attempt=1,
        purpose="poll niche monitor",
    )
    tw.api_response(
        "collection",
        seq_of_call=call_seq,
        status=200,
        latency_ms=123,
        bytes_=456,
        ids_returned=["abc"],
        cost={"credits": 1},
        outcome_class="ok",
        response_summary={"handle": "@someone", "count": 3},
        allowed_keys={"count"},
    )
    tw.close()

    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    call_event, response_event = lines
    assert call_event["event"] == "api_call"
    assert "Authorization" not in call_event["detail"]["request"]
    assert call_event["detail"]["request"] == {"query": "cats"}

    assert response_event["event"] == "api_response"
    assert response_event["detail"]["seq_of_call"] == call_event["seq"]
    assert "handle" not in response_event["detail"]["response_summary"]
    assert response_event["detail"]["response_summary"] == {"count": 3}


def test_czech_text_survives_utf8_round_trip(tmp_path):
    path = tmp_path / "trace.jsonl"
    tw = TraceWriter(path, run_id="2026-08-10_a3f2")
    tw.decision("digest", decision="Příliš žluťoučký kůň", rule="test rule")
    tw.close()

    text = path.read_text(encoding="utf-8")
    assert "Příliš žluťoučký kůň" in text
    event = json.loads(text.splitlines()[0])
    assert event["detail"]["decision"] == "Příliš žluťoučký kůň"
