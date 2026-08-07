"""Tests for hypeagent.llm — the OpenRouter client (W8-9 Q2): JSON contract,
corrective retry, budget caps, vision content-parts, spend/telemetry, and
the never-in-trace secret discipline."""

from __future__ import annotations

import json

import pytest

from hypeagent.collectors.base import FetchError, FetchResponse, FixtureFetcher
from hypeagent.config_load import LlmConfig, LlmNodeOverride
from hypeagent.llm import (
    LlmApiError,
    LlmBudgetExceededError,
    LlmClient,
    LlmParseError,
    LlmTransportError,
    LlmTruncatedError,
    image_content_part,
    text_content_part,
)
from hypeagent.trace import TraceWriter

ENDPOINT_KEY = "chat/completions"


def _config(**overrides) -> LlmConfig:
    base = dict(
        enabled=True, per_run_usd_cap=1.0, per_run_call_cap=20,
        usd_per_1m_input_tokens=2.0, usd_per_1m_output_tokens=10.0,
        # 0 unless a test is specifically exercising the QA reserve (below)
        # — every pre-existing generic budget-cap test is about
        # per_run_call_cap alone, not the reserve interacting with it.
        qa_reserved_calls=0,
    )
    base.update(overrides)
    return LlmConfig(**base)


def _ok_response(content: str, *, usage: dict | None = None) -> FetchResponse:
    payload = {
        "id": "gen-test-1",
        "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
        "usage": usage or {"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70, "cost": 0.0003},
    }
    return FetchResponse(status=200, headers={}, body=json.dumps(payload).encode("utf-8"), latency_ms=42)


def _truncated_response(content: str, *, usage: dict | None = None) -> FetchResponse:
    """A response the provider itself reports as cut off before it
    finished — ``finish_reason='length'`` — even though ``content`` may
    still happen to parse as valid JSON. Module docstring point 1b: this
    must never be accepted as a usable result."""
    payload = {
        "id": "gen-test-truncated",
        "choices": [{"message": {"content": content}, "finish_reason": "length"}],
        "usage": usage or {"prompt_tokens": 50, "completion_tokens": 1500, "total_tokens": 1550, "cost": 0.01},
    }
    return FetchResponse(status=200, headers={}, body=json.dumps(payload).encode("utf-8"), latency_ms=42)


class _QueueFetcher:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []
        self.request_bodies = []

    def fetch(self, url, *, headers=None, method="GET", body=None):
        self.calls.append(url)
        self.request_bodies.append(body)
        return self._responses.pop(0)


def _client(tmp_path, fetcher, *, config=None) -> tuple[LlmClient, TraceWriter]:
    trace_path = tmp_path / "trace.jsonl"
    tw = TraceWriter(trace_path, "run-1")
    client = LlmClient(config=config or _config(), fetcher=fetcher, api_key="sk-test-secret", trace=tw, stage="analysis")
    return client, tw


def _events(trace_path):
    return [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]


class TestJsonHappyPath:
    def test_call_json_returns_parsed_object(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response('{"headline": "hi", "count": 4}')})
        client, tw = _client(tmp_path, fetcher)
        result = client.call_json("analyst", system="sys", user_parts="describe it")
        tw.close()
        assert result == {"headline": "hi", "count": 4}
        assert client.call_count == 1

    def test_call_json_extracts_json_from_prose_and_fence(self, tmp_path):
        content = "Sure thing, here it is:\n```json\n{\"a\": 1, \"b\": 2}\n```\nHope that helps."
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response(content)})
        client, tw = _client(tmp_path, fetcher)
        result = client.call_json("copywriter", system="sys", user_parts="x")
        tw.close()
        assert result == {"a": 1, "b": 2}


class TestCorrectiveRetry:
    def test_bad_json_triggers_one_corrective_retry_then_succeeds(self, tmp_path):
        fetcher = FixtureFetcher(
            responses={ENDPOINT_KEY: _ok_response("not json at all, sorry")}
        )
        # FixtureFetcher returns the SAME response for every call to this
        # URL, so simulate "first bad, second good" via a queue subclass.
        class QueueFetcher:
            def __init__(self, responses):
                self._responses = list(responses)
                self.calls = []
                self.request_bodies = []

            def fetch(self, url, *, headers=None, method="GET", body=None):
                self.calls.append(url)
                self.request_bodies.append(body)
                return self._responses.pop(0)

        fetcher = QueueFetcher([
            _ok_response("not json at all, sorry"),
            _ok_response('{"headline": "fixed"}'),
        ])
        client, tw = _client(tmp_path, fetcher)
        result = client.call_json("analyst", system="sys", user_parts="x")
        tw.close()
        assert result == {"headline": "fixed"}
        assert client.call_count == 2
        second_body = json.loads(fetcher.request_bodies[1])
        second_user_text = second_body["messages"][-1]["content"]
        assert "return only" in second_user_text.lower() or "corrected json" in second_user_text.lower()
        assert "parse error" in second_user_text.lower()

    def test_bad_json_twice_raises_parse_error(self, tmp_path):
        class QueueFetcher:
            def __init__(self, responses):
                self._responses = list(responses)
                self.calls = []
                self.request_bodies = []

            def fetch(self, url, *, headers=None, method="GET", body=None):
                self.calls.append(url)
                self.request_bodies.append(body)
                return self._responses.pop(0)

        fetcher = QueueFetcher([_ok_response("nope"), _ok_response("still nope")])
        client, tw = _client(tmp_path, fetcher)
        with pytest.raises(LlmParseError):
            client.call_json("analyst", system="sys", user_parts="x")
        tw.close()
        assert client.call_count == 2


class TestBudgetCaps:
    def test_call_cap_stops_further_calls(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response('{"ok": true}')})
        client, tw = _client(tmp_path, fetcher, config=_config(per_run_call_cap=1))
        client.call_json("analyst", system="s", user_parts="x")
        with pytest.raises(LlmBudgetExceededError):
            client.call_json("analyst", system="s", user_parts="x")
        tw.close()
        assert len(fetcher.calls) == 1  # the second call never touched the network

    def test_usd_cap_stops_further_calls(self, tmp_path):
        # A single call whose reported cost already exceeds a tiny cap.
        response = _ok_response('{"ok": true}', usage={"prompt_tokens": 1, "completion_tokens": 1, "cost": 5.0})
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: response})
        client, tw = _client(tmp_path, fetcher, config=_config(per_run_usd_cap=1.0))
        client.call_json("analyst", system="s", user_parts="x")
        with pytest.raises(LlmBudgetExceededError):
            client.call_json("analyst", system="s", user_parts="x")
        tw.close()
        assert len(fetcher.calls) == 1


class TestVisionContentPartShape:
    def test_request_body_carries_text_and_image_parts(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response('{"color": "red"}')})
        client, tw = _client(tmp_path, fetcher)
        parts = [text_content_part("what color?"), image_content_part(b"\x89PNG\r\n\x1a\n fakepng", mime="image/png")]
        result = client.call_json("analyst", system="s", user_parts=parts)
        tw.close()
        assert result == {"color": "red"}
        sent_body = json.loads(fetcher.request_bodies[0])
        user_content = sent_body["messages"][1]["content"]
        assert isinstance(user_content, list)
        assert user_content[0]["type"] == "text"
        assert user_content[1]["type"] == "image_url"
        assert user_content[1]["image_url"]["url"].startswith("data:image/png;base64,")
        assert sent_body["response_format"] == {"type": "json_object"}


class TestTelemetry:
    def test_usage_to_spend_event_and_api_call_pair(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response('{"ok": true}')})
        client, tw = _client(tmp_path, fetcher)
        client.call_json("analyst", system="s", user_parts="x")
        tw.close()
        events = _events(tmp_path / "trace.jsonl")
        api_calls = [e for e in events if e["event"] == "api_call"]
        api_responses = [e for e in events if e["event"] == "api_response"]
        spends = [e for e in events if e["event"] == "spend"]
        assert len(api_calls) == 1 and api_calls[0]["detail"]["platform"] == "openrouter"
        assert len(api_responses) == 1
        assert len(spends) == 1
        assert spends[0]["detail"]["wallet"] == "llm"
        assert spends[0]["detail"]["ledger_recorded"] == pytest.approx(0.0003)

    def test_api_key_never_appears_in_trace(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response('{"ok": true}')})
        client, tw = _client(tmp_path, fetcher)
        client.call_json("analyst", system="s", user_parts="secret squirrel content")
        tw.close()
        trace_text = (tmp_path / "trace.jsonl").read_text(encoding="utf-8")
        assert "sk-test-secret" not in trace_text
        # Prompt/response CONTENT never appears either — only hashes/counts.
        assert "secret squirrel content" not in trace_text

    def test_transport_error_raises_and_traces_without_leaking_key(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: FetchError("boom sk-test-secret leaked-in-error")})
        client, tw = _client(tmp_path, fetcher)
        with pytest.raises(LlmTransportError):
            client.call_json("analyst", system="s", user_parts="x")
        tw.close()
        trace_text = (tmp_path / "trace.jsonl").read_text(encoding="utf-8")
        assert "sk-test-secret" not in trace_text

    def test_api_error_object_raises(self, tmp_path):
        payload = {"error": {"code": 400, "message": "bad request"}}
        response = FetchResponse(status=400, headers={}, body=json.dumps(payload).encode("utf-8"), latency_ms=5)
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: response})
        client, tw = _client(tmp_path, fetcher)
        with pytest.raises(LlmApiError):
            client.call_json("analyst", system="s", user_parts="x")
        tw.close()


class TestTruncationDetection:
    """W8-9 point 1b: a truncated response (``finish_reason == 'length'``)
    is treated like a parse failure -- one corrective retry with a bigger
    token-budget hint, then a typed error if it is still truncated. Never
    parsed into a usable-looking partial result, even when the truncated
    content happens to still be valid JSON."""

    def test_truncated_then_recovers_on_retry(self, tmp_path):
        fetcher = _QueueFetcher([
            _truncated_response('{"headline": "cut off mid'),
            _ok_response('{"headline": "complete now"}'),
        ])
        client, tw = _client(tmp_path, fetcher, config=_config(default_max_tokens=1500))
        result = client.call_json("analyst", system="sys", user_parts="x")
        tw.close()
        assert result == {"headline": "complete now"}
        assert client.call_count == 2
        second_body = json.loads(fetcher.request_bodies[1])
        assert second_body["max_tokens"] > 1500  # a genuinely bigger budget hint
        second_user_text = second_body["messages"][-1]["content"]
        assert "truncated" in second_user_text.lower()

    def test_truncated_content_never_parsed_even_though_valid_json(self, tmp_path):
        # This truncated response's content IS valid, parseable JSON --
        # proving truncation is checked BEFORE parsing, not inferred from a
        # parse failure.
        fetcher = _QueueFetcher([
            _truncated_response('{"headline": "looks complete"}'),
            _ok_response('{"headline": "actually complete"}'),
        ])
        client, tw = _client(tmp_path, fetcher, config=_config())
        result = client.call_json("analyst", system="sys", user_parts="x")
        tw.close()
        assert result == {"headline": "actually complete"}

    def test_truncated_twice_raises_typed_error_not_a_partial_result(self, tmp_path):
        fetcher = _QueueFetcher([
            _truncated_response('{"headline": "still cut off'),
            _truncated_response('{"headline": "still cut off again'),
        ])
        client, tw = _client(tmp_path, fetcher, config=_config())
        with pytest.raises(LlmTruncatedError):
            client.call_json("analyst", system="sys", user_parts="x")
        tw.close()
        assert client.call_count == 2


class TestQaReservedCalls:
    """W8-9 point 2: ``qa_reserved_calls`` carves out calls only N-E
    vision-QA (``is_qa=True``) may spend -- non-QA nodes see an effective
    cap of ``per_run_call_cap - qa_reserved_calls`` and can never eat into
    the reserve, but a QA call may use the full ``per_run_call_cap``."""

    def test_non_qa_call_is_capped_by_the_reserved_effective_cap(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response('{"ok": true}')})
        config = _config(per_run_call_cap=5, qa_reserved_calls=2)
        client, tw = _client(tmp_path, fetcher, config=config)
        for _ in range(3):  # effective non-QA cap is 5 - 2 = 3
            client.call_json("analyst", system="s", user_parts="x")
        with pytest.raises(LlmBudgetExceededError):
            client.call_json("copywriter", system="s", user_parts="x")
        tw.close()
        assert client.call_count == 3

    def test_qa_call_may_spend_into_the_reserve(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response('{"text_matches": true}')})
        config = _config(per_run_call_cap=5, qa_reserved_calls=2)
        client, tw = _client(tmp_path, fetcher, config=config)
        for _ in range(3):  # exhausts the non-QA effective cap
            client.call_json("analyst", system="s", user_parts="x")
        # The 2 reserved calls remain available to QA specifically.
        client.call_json("vision_qa", system="s", user_parts="x", is_qa=True)
        client.call_json("vision_qa", system="s", user_parts="x", is_qa=True)
        with pytest.raises(LlmBudgetExceededError):  # the full cap (5) is now exhausted
            client.call_json("vision_qa", system="s", user_parts="x", is_qa=True)
        tw.close()
        assert client.call_count == 5

    def test_zero_reserve_behaves_like_the_old_undifferentiated_cap(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response('{"ok": true}')})
        config = _config(per_run_call_cap=2, qa_reserved_calls=0)
        client, tw = _client(tmp_path, fetcher, config=config)
        client.call_json("analyst", system="s", user_parts="x")
        client.call_json("copywriter", system="s", user_parts="x")
        with pytest.raises(LlmBudgetExceededError):
            client.call_json("prompt_crafter", system="s", user_parts="x")
        tw.close()
        assert client.call_count == 2


class TestNodeOverrides:
    def test_node_override_changes_model_and_tokens_sent(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response('{"ok": true}')})
        config = _config(node_overrides={"prompt_crafter": LlmNodeOverride(model="anthropic/claude-haiku", max_tokens=300, temperature=0.1)})
        client, tw = _client(tmp_path, fetcher, config=config)
        client.call_json("prompt_crafter", system="s", user_parts="x")
        tw.close()
        sent_body = json.loads(fetcher.request_bodies[0])
        assert sent_body["model"] == "anthropic/claude-haiku"
        assert sent_body["max_tokens"] == 300
        assert sent_body["temperature"] == 0.1
