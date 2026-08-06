"""Tests for the Virlo collector (§2.3, GOAL_ROADMAP.md M3(a)) — fully
offline against fixtures modeled on the real payloads observed during live
discovery (2026-08-07)."""

from __future__ import annotations

from pathlib import Path

from hypeagent.collectors import virlo
from hypeagent.collectors.base import CollectContext, FetchResponse, FixtureFetcher
from hypeagent.store import SourceDenyList, Store
from hypeagent.trace import TraceWriter

FIXTURES = Path(__file__).parent / "fixtures"


def _fr(path: Path) -> FetchResponse:
    return FetchResponse(status=200, headers={}, body=path.read_bytes(), latency_ms=4)


def _ctx(tmp_path, fetcher, run_id="2026-08-10_v1v1"):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    trace = TraceWriter(tmp_path / "logs" / "trace.jsonl", run_id)
    deny_list = SourceDenyList(denied_sources=set(), denied_communities=set())
    ctx = CollectContext(
        store=store, trace=trace, fetcher=fetcher, deny_list=deny_list,
        run_id=run_id, run_date=run_id.split("_")[0], theme="hypedigitaly",
    )
    return ctx, store, trace


def _key_path(tmp_path, content: str = "virlo_tkn_test_key") -> Path:
    key_path = tmp_path / "secrets" / "virlo.key"
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(content, encoding="utf-8")
    return key_path


class TestVirloCollector:
    def test_collect_normalizes_digest_and_agent_monitor(self, tmp_path):
        key_path = _key_path(tmp_path)
        fetcher = FixtureFetcher(responses={
            "v1/trends/digest": _fr(FIXTURES / "virlo_trends_digest.json"),
            "v1/agents/9c96fddf-dc35-4be0-bbd9-12f4d22aea12": _fr(FIXTURES / "virlo_agent_monitor.json"),
        })
        ctx, store, trace = _ctx(tmp_path, fetcher)
        try:
            result = virlo.collect(ctx, family="short_form_trends", key_path=key_path)
            assert result.outcome == "ok"
            assert result.calls_made == 2
            titles = {i.title for i in result.items}
            assert "AI agents automating outbound sales for small businesses" in titles
            assert "AI Agents for Business Automation and Outbound Sales" in titles

            digest_item = next(i for i in result.items if i.title.startswith("AI agents automating"))
            assert digest_item.evidence_class == "counted"
            assert digest_item.metrics["score"] == 154000
            assert digest_item.language == "en"
            assert digest_item.source_family == "short_form_trends"
            assert digest_item.author_handle == "aiagentsdaily"

            theme_item = next(i for i in result.items if i.title.startswith("AI Agents for Business"))
            assert theme_item.evidence_class == "counted"
            assert theme_item.metrics["score"] == 33
            assert theme_item.author_handle is None
        finally:
            store.close()
            trace.close()

    def test_authorization_header_never_reaches_trace(self, tmp_path):
        key_path = _key_path(tmp_path, content="virlo_tkn_super_secret_value")
        fetcher = FixtureFetcher(responses={
            "v1/trends/digest": _fr(FIXTURES / "virlo_trends_digest.json"),
            "v1/agents/9c96fddf-dc35-4be0-bbd9-12f4d22aea12": _fr(FIXTURES / "virlo_agent_monitor.json"),
        })
        trace_path = tmp_path / "logs" / "trace.jsonl"
        ctx, store, trace = _ctx(tmp_path, fetcher)
        try:
            virlo.collect(ctx, family="short_form_trends", key_path=key_path)
        finally:
            store.close()
            trace.close()
        trace_text = trace_path.read_text(encoding="utf-8")
        assert "virlo_tkn_super_secret_value" not in trace_text
        assert "Authorization" not in trace_text

    def test_missing_key_file_degrades_without_any_network_call(self, tmp_path):
        fetcher = FixtureFetcher(responses={})
        ctx, store, trace = _ctx(tmp_path, fetcher)
        missing_key_path = tmp_path / "secrets" / "virlo.key"
        try:
            result = virlo.collect(ctx, family="short_form_trends", key_path=missing_key_path)
            assert result.outcome == "degraded"
            assert "key file missing" in (result.degrade_reason or "")
            assert fetcher.calls == []
        finally:
            store.close()
            trace.close()

    def test_agent_monitor_not_finalized_is_treated_as_not_yet_usable(self, tmp_path):
        key_path = _key_path(tmp_path)
        fetcher = FixtureFetcher(responses={
            "v1/trends/digest": _fr(FIXTURES / "virlo_trends_digest.json"),
            "v1/agents/9c96fddf-dc35-4be0-bbd9-12f4d22aea12": _fr(FIXTURES / "virlo_agent_monitor_not_finalized.json"),
        })
        ctx, store, trace = _ctx(tmp_path, fetcher)
        try:
            result = virlo.collect(ctx, family="short_form_trends", key_path=key_path)
            assert result.outcome == "degraded"
            assert "not finalized" in (result.degrade_reason or "")
            # The digest endpoint's items are still usable even though the
            # agent-monitor endpoint degraded independently.
            assert any(i.title.startswith("AI agents automating") for i in result.items)
        finally:
            store.close()
            trace.close()

    def test_never_posts_only_get_reads(self, tmp_path):
        key_path = _key_path(tmp_path)
        fetcher = FixtureFetcher(responses={
            "v1/trends/digest": _fr(FIXTURES / "virlo_trends_digest.json"),
            "v1/agents/9c96fddf-dc35-4be0-bbd9-12f4d22aea12": _fr(FIXTURES / "virlo_agent_monitor.json"),
        })
        ctx, store, trace = _ctx(tmp_path, fetcher)
        try:
            virlo.collect(ctx, family="short_form_trends", key_path=key_path)
        finally:
            store.close()
            trace.close()
        assert len(fetcher.calls) == 2
        assert all("api.virlo.ai/v1/" in url for url in fetcher.calls)

    def test_within_run_idempotency_skips_second_fetch_same_day(self, tmp_path):
        key_path = _key_path(tmp_path)
        fetcher = FixtureFetcher(responses={
            "v1/trends/digest": _fr(FIXTURES / "virlo_trends_digest.json"),
            "v1/agents/9c96fddf-dc35-4be0-bbd9-12f4d22aea12": _fr(FIXTURES / "virlo_agent_monitor.json"),
        })
        ctx, store, trace = _ctx(tmp_path, fetcher)
        try:
            virlo.collect(ctx, family="short_form_trends", key_path=key_path)
            first_calls = len(fetcher.calls)
            assert first_calls == 2
            result2 = virlo.collect(ctx, family="short_form_trends", key_path=key_path)
            assert len(fetcher.calls) == first_calls
            assert result2.items == []
        finally:
            store.close()
            trace.close()
