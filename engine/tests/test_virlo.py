"""Tests for the Virlo collector (§2.3, GOAL_ROADMAP.md M3(a)) — fully
offline against fixtures modeled on the real payloads observed during live
discovery (2026-08-07)."""

from __future__ import annotations

from pathlib import Path

import yaml

from hypeagent.collectors import virlo
from hypeagent.collectors.base import CollectContext, FetchResponse, FixtureFetcher
from hypeagent.store import SourceDenyList, Store
from hypeagent.trace import TraceWriter

FIXTURES = Path(__file__).parent / "fixtures"


def _fr(path: Path) -> FetchResponse:
    return FetchResponse(status=200, headers={}, body=path.read_bytes(), latency_ms=4)


def _ctx(tmp_path, fetcher, run_id="2026-08-10_v1v1", *, run_dir=None):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    trace = TraceWriter(tmp_path / "logs" / "trace.jsonl", run_id)
    deny_list = SourceDenyList(denied_sources=set(), denied_communities=set())
    ctx = CollectContext(
        store=store, trace=trace, fetcher=fetcher, deny_list=deny_list,
        run_id=run_id, run_date=run_id.split("_")[0], theme="hypedigitaly",
        run_dir=run_dir,
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


class TestVirloExtractionNote:
    """W8-8: a small per-run note naming the themes actually extracted
    (name/confidence/video_count/stable_key) and the richer fields present
    on the raw payload but not yet used by copy — so the process summary's
    §3 can read it back without re-parsing the raw payload itself."""

    def test_collect_writes_extraction_note_when_run_dir_set(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_dir = tmp_path / "logs" / "runs" / "2026-08-10_v1v1"
        fetcher = FixtureFetcher(responses={
            "v1/trends/digest": _fr(FIXTURES / "virlo_trends_digest.json"),
            "v1/agents/9c96fddf-dc35-4be0-bbd9-12f4d22aea12": _fr(FIXTURES / "virlo_agent_monitor.json"),
        })
        ctx, store, trace = _ctx(tmp_path, fetcher, run_dir=run_dir)
        try:
            result = virlo.collect(ctx, family="short_form_trends", key_path=key_path)
            assert result.outcome == "ok"
        finally:
            store.close()
            trace.close()

        note_path = run_dir / virlo.VIRLO_EXTRACTION_FILENAME
        assert note_path.exists()
        doc = yaml.safe_load(note_path.read_text(encoding="utf-8"))
        assert doc["monitor_id"] == "9c96fddf-dc35-4be0-bbd9-12f4d22aea12"
        names = {t["name"] for t in doc["themes"]}
        assert "AI Agents for Business Automation and Outbound Sales" in names
        assert "Claude Code for Development and Automation" in names
        first = next(t for t in doc["themes"] if t["name"].startswith("AI Agents for Business"))
        assert first["confidence"] == 0.92
        assert first["video_count"] == 33
        assert first["stable_key"] == "ai-agents-business-automation-outbound-sales"
        # The fixture's themes carry "tactics" and "why_it_works" -- named,
        # never their text.
        assert "tactics" in doc["unused_fields_present_in_raw_payload"]
        assert "why_it_works" in doc["unused_fields_present_in_raw_payload"]
        for theme in doc["themes"]:
            assert "tactics" not in theme
            assert "why_it_works" not in theme
        assert any("fetched this run" in e["status"] for e in doc["endpoints_called"])

    def test_no_run_dir_never_writes_a_note(self, tmp_path):
        key_path = _key_path(tmp_path)
        fetcher = FixtureFetcher(responses={
            "v1/trends/digest": _fr(FIXTURES / "virlo_trends_digest.json"),
            "v1/agents/9c96fddf-dc35-4be0-bbd9-12f4d22aea12": _fr(FIXTURES / "virlo_agent_monitor.json"),
        })
        ctx, store, trace = _ctx(tmp_path, fetcher, run_dir=None)
        try:
            virlo.collect(ctx, family="short_form_trends", key_path=key_path)
        finally:
            store.close()
            trace.close()
        assert not (tmp_path / "logs" / "runs").exists()

    def test_cache_hit_second_call_does_not_rewrite_note(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_dir = tmp_path / "logs" / "runs" / "2026-08-10_v1v1"
        fetcher = FixtureFetcher(responses={
            "v1/trends/digest": _fr(FIXTURES / "virlo_trends_digest.json"),
            "v1/agents/9c96fddf-dc35-4be0-bbd9-12f4d22aea12": _fr(FIXTURES / "virlo_agent_monitor.json"),
        })
        ctx, store, trace = _ctx(tmp_path, fetcher, run_dir=run_dir)
        try:
            virlo.collect(ctx, family="short_form_trends", key_path=key_path)
            note_path = run_dir / virlo.VIRLO_EXTRACTION_FILENAME
            first_bytes = note_path.read_bytes()

            result2 = virlo.collect(ctx, family="short_form_trends", key_path=key_path)
            assert result2.items == []
            assert note_path.read_bytes() == first_bytes
        finally:
            store.close()
            trace.close()

    def test_load_extraction_note_returns_none_when_absent(self, tmp_path):
        assert virlo.load_extraction_note(tmp_path / "no_such_run") is None

    def test_build_extraction_note_returns_none_when_not_finalized(self):
        import json

        payload = json.loads((FIXTURES / "virlo_agent_monitor_not_finalized.json").read_text(encoding="utf-8"))
        assert virlo.build_extraction_note(payload, monitor_id="x") is None


# ---------------------------------------------------------------------------
# W8-9 Phase 2: monitor_ids fallback, sub-path pagination, virlo_corpus.yaml,
# media download + retention, digest-off default, same-day idempotency.
# ---------------------------------------------------------------------------

V2_MONITOR_ID = "623203a9-c09c-4763-85e0-1c177b5af760"
V1_MONITOR_ID = "9c96fddf-dc35-4be0-bbd9-12f4d22aea12"


def _page_response(list_key: str, item_template: dict, count: int) -> FetchResponse:
    """Build a synthetic sub-path page of exactly ``count`` items (used to
    force multi-page pagination in tests without hand-writing hundreds of
    fixture lines)."""
    import copy
    import json as _json

    items = []
    for i in range(count):
        item = copy.deepcopy(item_template)
        item["id"] = f"{item_template['id']}-{i}"
        item["views"] = item_template.get("views", 1000) - i
        items.append(item)
    body = _json.dumps({"data": {"agent_id": V2_MONITOR_ID, "total": count, "limit": 100, "offset": 0, list_key: items}}).encode(
        "utf-8"
    )
    return FetchResponse(status=200, headers={}, body=body, latency_ms=1)


class TestVirloMonitorIdsFallback:
    def test_falls_through_to_next_monitor_when_first_not_finalized(self, tmp_path):
        key_path = _key_path(tmp_path)
        fetcher = FixtureFetcher(
            responses={
                f"v1/agents/{V2_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor_v2_not_finalized.json"),
                f"v1/agents/{V1_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor.json"),
            }
        )
        ctx, store, trace = _ctx(tmp_path, fetcher)
        try:
            result = virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID, V1_MONITOR_ID], trends_digest_enabled=False,
                budget_max_calls=10,
            )
            assert result.outcome == "degraded"  # v2's "not finalized" is still a recorded degrade
            assert "not finalized" in (result.degrade_reason or "")
            titles = {i.title for i in result.items}
            assert "AI Agents for Business Automation and Outbound Sales" in titles
            assert len(fetcher.calls) == 2
        finally:
            store.close()
            trace.close()

    def test_stops_at_first_finalized_monitor_without_trying_next(self, tmp_path):
        key_path = _key_path(tmp_path)
        fetcher = FixtureFetcher(
            responses={
                f"v1/agents/{V1_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor.json"),
                f"v1/agents/{V2_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor_v2.json"),
            }
        )
        ctx, store, trace = _ctx(tmp_path, fetcher)
        try:
            result = virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V1_MONITOR_ID, V2_MONITOR_ID], trends_digest_enabled=False,
                budget_max_calls=10,
            )
            assert result.outcome == "ok"
            assert len(fetcher.calls) == 1
            assert all(V2_MONITOR_ID not in url for url in fetcher.calls)
        finally:
            store.close()
            trace.close()

    def test_no_finalized_monitor_anywhere_degrades_with_no_theme_items(self, tmp_path):
        key_path = _key_path(tmp_path)
        fetcher = FixtureFetcher(
            responses={
                f"v1/agents/{V2_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor_v2_not_finalized.json"),
                f"v1/agents/{V1_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor_not_finalized.json"),
            }
        )
        ctx, store, trace = _ctx(tmp_path, fetcher)
        try:
            result = virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID, V1_MONITOR_ID], trends_digest_enabled=False,
                budget_max_calls=10,
            )
            assert result.outcome == "degraded"
            assert result.items == []
            assert len(fetcher.calls) == 2
        finally:
            store.close()
            trace.close()


class TestVirloSubpathCollection:
    def _fetcher(self) -> FixtureFetcher:
        # Order matters for FixtureFetcher's substring matching: the
        # sub-path-specific keys must be checked before the shorter
        # agent-id-only key, since the latter is itself a substring of
        # every sub-path URL.
        return FixtureFetcher(
            responses={
                f"v1/agents/{V2_MONITOR_ID}/videos": _fr(FIXTURES / "virlo_videos_small.json"),
                f"v1/agents/{V2_MONITOR_ID}/slideshows": _fr(FIXTURES / "virlo_slideshows_small.json"),
                f"v1/agents/{V2_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor_v2.json"),
            }
        )

    def test_corpus_file_written_with_full_theme_richness_and_top_items(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_dir = tmp_path / "logs" / "runs" / "2026-08-10_v1v1"
        fetcher = self._fetcher()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_dir=run_dir)
        try:
            result = virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, budget_max_calls=20,
            )
            assert result.outcome == "ok"
            # The unchanged theme-based RawItem flow still works.
            titles = {i.title for i in result.items}
            assert "AI Agents for Business Automation and Outbound Sales" in titles
        finally:
            store.close()
            trace.close()

        corpus_path = run_dir / virlo.VIRLO_CORPUS_FILENAME
        assert corpus_path.exists()
        corpus = yaml.safe_load(corpus_path.read_text(encoding="utf-8"))
        assert corpus["monitor_id"] == V2_MONITOR_ID
        assert corpus["monitor_finalized"] is True

        # Full theme richness -- no truncation, tactics complete.
        theme = next(t for t in corpus["themes"] if t["name"].startswith("AI Agents for Business"))
        assert theme["tactics"] == [
            "show AI agents qualifying leads",
            "demonstrate automated outbound sequences",
            "before/after revenue comparisons",
        ]
        assert theme["why_it_works"].startswith("The idea of AI agents handling sales outreach")
        assert theme["evidence_video_ids"] == ["fake-video-id-1", "fake-video-id-2"]
        assert len(corpus["viral_tactics"]) == 3
        assert corpus["top_10_breakdown"]["videos"][0]["video_id"] == "fake-video-id-1"
        assert corpus["connecting_thread"].startswith("These trends collectively")
        assert corpus["key_highlight"].startswith("The dominant trend")
        assert corpus["timing_analysis"]["peak_hours"] == [20, 21, 11]

        # Top items by views, per platform shape.
        assert len(corpus["videos"]) == 2
        top_video = corpus["videos"][0]
        assert top_video["views"] == 4489565
        assert top_video["url"].startswith("https://tiktok.example.com")
        assert top_video["hook_text"] == "This AI agent replaced my entire sales team"
        assert top_video["text_overlay_content"] == "AI AGENT CLOSES DEALS 24/7"
        assert top_video["summary"]
        assert top_video["thumbnail_url"]
        assert top_video["hashtags"] == ["aiagents", "automation", "outbound"]
        # Raw handle never appears; only its hash.
        assert top_video["author_handle_hash"] != "fakecreatorone"
        assert len(top_video["author_handle_hash"]) == 64  # hex sha256

        assert len(corpus["slideshows"]) == 2
        top_slideshow = corpus["slideshows"][0]
        assert top_slideshow["panel_count"] == 3
        assert len(top_slideshow["image_urls"]) == 3
        assert top_slideshow["panel_texts"][0] == "1. AI agent that qualifies leads"

    def test_no_third_party_handle_or_url_leaks_into_the_trace(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_dir = tmp_path / "logs" / "runs" / "2026-08-10_v1v1"
        trace_path = tmp_path / "logs" / "trace.jsonl"
        fetcher = self._fetcher()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, budget_max_calls=20,
            )
        finally:
            store.close()
            trace.close()
        trace_text = trace_path.read_text(encoding="utf-8")
        assert "fakecreatorone" not in trace_text
        assert "fakecreatortwo" not in trace_text

    def test_extraction_note_records_subpath_counts(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_dir = tmp_path / "logs" / "runs" / "2026-08-10_v1v1"
        fetcher = self._fetcher()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, budget_max_calls=20,
            )
        finally:
            store.close()
            trace.close()
        note = virlo.load_extraction_note(run_dir)
        assert note["videos_captured"] == 2
        assert note["slideshows_captured"] == 2
        assert len(note["subpaths_called"]) == 2  # one page each, both short of 100 -> stop

    def test_pagination_cap_honored(self, tmp_path):
        """Full (100-item) pages force the loop to keep paging; a
        ``subpath_page_cap`` of 2 must stop it there regardless of how much
        more data the API claims to have (never a poll loop)."""
        key_path = _key_path(tmp_path)
        video_template = {
            "id": "fake-video-id", "url": "https://tiktok.example.com/@x/video/1", "description": "x",
            "platform": "tiktok", "views": 1000, "likes": 1, "shares": 1, "comments": 1, "bookmarks": 1,
            "publish_date": "2026-07-01T00:00:00Z", "author": {"username": "fakeuser"}, "hashtags": [],
            "thumbnail_url": "https://cdn.example.com/x.jpg", "intelligence_status": "disabled", "intelligence": None,
        }
        full_page = _page_response("videos", video_template, count=100)
        fetcher = FixtureFetcher(
            responses={
                f"v1/agents/{V2_MONITOR_ID}/videos?limit=100&order_by=views&page=1": full_page,
                f"v1/agents/{V2_MONITOR_ID}/videos?limit=100&order_by=views&page=2": full_page,
                f"v1/agents/{V2_MONITOR_ID}/videos?limit=100&order_by=views&page=3": full_page,
                f"v1/agents/{V2_MONITOR_ID}/slideshows": _fr(FIXTURES / "virlo_slideshows_small.json"),
                f"v1/agents/{V2_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor_v2.json"),
            }
        )
        ctx, store, trace = _ctx(tmp_path, fetcher)
        try:
            result = virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=2, budget_max_calls=20,
            )
            assert result.outcome == "ok"
        finally:
            store.close()
            trace.close()
        video_page_calls = [u for u in fetcher.calls if "/videos?" in u]
        assert len(video_page_calls) == 2  # capped at 2 pages even though every page was "full"


class TestVirloMediaDownload:
    def _fetcher_with_media(self) -> FixtureFetcher:
        return FixtureFetcher(
            responses={
                f"v1/agents/{V2_MONITOR_ID}/videos": _fr(FIXTURES / "virlo_videos_small.json"),
                f"v1/agents/{V2_MONITOR_ID}/slideshows": _fr(FIXTURES / "virlo_slideshows_small.json"),
                f"v1/agents/{V2_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor_v2.json"),
                "cdn.example.com/panels/fake-slideshow-id-1/panel1.webp": FetchResponse(200, {}, b"panel-1-bytes", 1),
                "cdn.example.com/panels/fake-slideshow-id-1/panel2.webp": FetchResponse(200, {}, b"panel-2-bytes", 1),
                "cdn.example.com/panels/fake-slideshow-id-1/panel3.webp": FetchResponse(200, {}, b"panel-3-bytes", 1),
                "cdn.example.com/thumbs/fake-video-id-1.jpg": FetchResponse(200, {}, b"thumb-1-bytes", 1),
                "cdn.example.com/thumbs/fake-video-id-2.jpg": FetchResponse(200, {}, b"thumb-2-bytes", 1),
            }
        )

    def test_downloads_top_slideshow_panels_and_video_thumbnails_within_cap(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_id = "2026-08-10_v1v1"
        run_dir = tmp_path / "logs" / "runs" / run_id
        fetcher = self._fetcher_with_media()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_id=run_id, run_dir=run_dir)
        try:
            result = virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, media_download_cap=4, budget_max_calls=20,
            )
            assert result.outcome == "ok"
            media_dir = tmp_path / "logs" / "artifacts" / "raw" / run_id / "virlo_media"
            files = sorted(media_dir.glob("*"))
            # 3 panels from the top (only) slideshow that fits (3 <= 5) +
            # 2 remaining slots go to the top 2 video thumbnails.
            assert len(files) == 4
            assert sum(1 for f in files if f.name.startswith("slideshow_panel_")) == 3
            assert sum(1 for f in files if f.name.startswith("video_thumbnail_")) == 1
        finally:
            store.close()
            trace.close()

    def test_media_downloaded_count_recorded_in_extraction_note(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_id = "2026-08-10_v1v1"
        run_dir = tmp_path / "logs" / "runs" / run_id
        fetcher = self._fetcher_with_media()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_id=run_id, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, media_download_cap=4, budget_max_calls=20,
            )
        finally:
            store.close()
            trace.close()
        note = virlo.load_extraction_note(run_dir)
        assert note["media_downloaded"] == 4

    def test_no_media_urls_or_handles_in_trace_only_counts(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_id = "2026-08-10_v1v1"
        run_dir = tmp_path / "logs" / "runs" / run_id
        trace_path = tmp_path / "logs" / "trace.jsonl"
        fetcher = self._fetcher_with_media()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_id=run_id, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, media_download_cap=4, budget_max_calls=20,
            )
        finally:
            store.close()
            trace.close()
        trace_text = trace_path.read_text(encoding="utf-8")
        assert "cdn.example.com" not in trace_text
        assert "virlo media download: 4 succeeded, 0 failed" in trace_text

    def test_failed_download_degrades_gracefully_and_continues(self, tmp_path):
        from hypeagent.collectors.base import FetchError

        key_path = _key_path(tmp_path)
        run_id = "2026-08-10_v1v1"
        run_dir = tmp_path / "logs" / "runs" / run_id
        responses = self._fetcher_with_media().responses
        responses["cdn.example.com/thumbs/fake-video-id-1.jpg"] = FetchError("simulated network failure")
        fetcher = FixtureFetcher(responses=responses)
        ctx, store, trace = _ctx(tmp_path, fetcher, run_id=run_id, run_dir=run_dir)
        try:
            result = virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, media_download_cap=4, budget_max_calls=20,
            )
            assert result.outcome == "degraded"
            assert "1 of 4 selected image" in (result.degrade_reason or "")
            media_dir = tmp_path / "logs" / "artifacts" / "raw" / run_id / "virlo_media"
            assert len(list(media_dir.glob("*"))) == 3  # the other three still saved
        finally:
            store.close()
            trace.close()

    def test_media_download_cap_zero_downloads_nothing(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_id = "2026-08-10_v1v1"
        run_dir = tmp_path / "logs" / "runs" / run_id
        fetcher = self._fetcher_with_media()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_id=run_id, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, media_download_cap=0, budget_max_calls=20,
            )
        finally:
            store.close()
            trace.close()
        media_dir = tmp_path / "logs" / "artifacts" / "raw" / run_id / "virlo_media"
        assert not media_dir.exists()
        assert "cdn.example.com" not in [c for c in fetcher.calls if "cdn.example.com" in c]

    def test_retention_integration_downloaded_media_expires_after_30_days(self, tmp_path):
        from datetime import datetime, timedelta

        key_path = _key_path(tmp_path)
        run_id = "2026-08-10_v1v1"
        run_dir = tmp_path / "logs" / "runs" / run_id
        fetcher = self._fetcher_with_media()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_id=run_id, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, media_download_cap=4, budget_max_calls=20,
            )
            media_dir = tmp_path / "logs" / "artifacts" / "raw" / run_id / "virlo_media"
            assert len(list(media_dir.glob("*"))) == 4

            report = store.run_expiry_job(now=datetime.now().astimezone() + timedelta(days=31))
            assert report.raw_payloads_deleted >= 4
            assert list(media_dir.glob("*")) == []
        finally:
            store.close()
            trace.close()


class TestVirloMediaManifest:
    """W8-10 Phase 8 (dynamic inspiration): the image<->item join manifest
    -- written to the run dir (never inside ``virlo_media/`` itself, so it
    never perturbs that directory's own file-count/retention semantics,
    see ``TestVirloMediaDownload`` above)."""

    def _fetcher_with_media(self) -> FixtureFetcher:
        return FixtureFetcher(
            responses={
                f"v1/agents/{V2_MONITOR_ID}/videos": _fr(FIXTURES / "virlo_videos_small.json"),
                f"v1/agents/{V2_MONITOR_ID}/slideshows": _fr(FIXTURES / "virlo_slideshows_small.json"),
                f"v1/agents/{V2_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor_v2.json"),
                "cdn.example.com/panels/fake-slideshow-id-1/panel1.webp": FetchResponse(200, {}, b"panel-1-bytes", 1),
                "cdn.example.com/panels/fake-slideshow-id-1/panel2.webp": FetchResponse(200, {}, b"panel-2-bytes", 1),
                "cdn.example.com/panels/fake-slideshow-id-1/panel3.webp": FetchResponse(200, {}, b"panel-3-bytes", 1),
                "cdn.example.com/thumbs/fake-video-id-1.jpg": FetchResponse(200, {}, b"thumb-1-bytes", 1),
                "cdn.example.com/thumbs/fake-video-id-2.jpg": FetchResponse(200, {}, b"thumb-2-bytes", 1),
            }
        )

    def test_manifest_written_next_to_the_corpus_not_inside_virlo_media(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_id = "2026-08-10_manifest1"
        run_dir = tmp_path / "logs" / "runs" / run_id
        fetcher = self._fetcher_with_media()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_id=run_id, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, media_download_cap=4, budget_max_calls=20,
            )
            manifest_path = run_dir / virlo.VIRLO_MEDIA_MANIFEST_FILENAME
            assert manifest_path.exists()
            media_dir = tmp_path / "logs" / "artifacts" / "raw" / run_id / "virlo_media"
            # Still exactly 4 media files -- the manifest lives elsewhere.
            assert len(list(media_dir.glob("*"))) == 4
            assert not (media_dir / virlo.VIRLO_MEDIA_MANIFEST_FILENAME).exists()
        finally:
            store.close()
            trace.close()

    def test_manifest_join_is_correct_for_videos_and_slideshow_panels(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_id = "2026-08-10_manifest2"
        run_dir = tmp_path / "logs" / "runs" / run_id
        fetcher = self._fetcher_with_media()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_id=run_id, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, media_download_cap=4, budget_max_calls=20,
            )
            entries = virlo.load_media_manifest(run_dir)
            assert len(entries) == 4

            video_entries = [e for e in entries if e.item_kind == "video"]
            slideshow_entries = [e for e in entries if e.item_kind == "slideshow"]
            assert len(video_entries) == 1
            assert len(slideshow_entries) == 3

            video_entry = video_entries[0]
            assert video_entry.item_id == "fake-video-id-1"
            assert video_entry.views == 4489565
            assert video_entry.panel_index is None
            # Linked via the theme's own evidence_video_ids.
            assert video_entry.theme_key == "AI Agents for Business Automation and Outbound Sales"
            assert video_entry.caption == "This AI agent replaced my entire sales team"

            panel_indexes = sorted(e.panel_index for e in slideshow_entries)
            assert panel_indexes == [0, 1, 2]
            for e in slideshow_entries:
                assert e.item_id == "fake-slideshow-id-1"
                assert e.views == 890000
                # Slideshows carry no evidence_video_ids link on this API shape.
                assert e.theme_key is None
            captions = {e.panel_index: e.caption for e in slideshow_entries}
            assert captions[0] == "1. AI agent that qualifies leads"
            assert captions[1] == "2. Voice AI that books meetings"
            assert captions[2] == "3. AI that writes cold emails"

            # Every manifest filename actually exists on disk.
            media_dir = tmp_path / "logs" / "artifacts" / "raw" / run_id / "virlo_media"
            on_disk = {p.name for p in media_dir.glob("*")}
            assert {e.filename for e in entries} == on_disk
        finally:
            store.close()
            trace.close()

    def test_manifest_is_registered_for_the_same_retention_job_as_media(self, tmp_path):
        """The manifest lives in the run dir, alongside virlo_corpus.yaml --
        it is registered for the SAME 30-day raw-artifact retention as the
        media files it describes (like ``virlo_corpus.yaml`` already is),
        so it does not outlive the media it joins."""
        key_path = _key_path(tmp_path)
        run_id = "2026-08-10_manifest3"
        run_dir = tmp_path / "logs" / "runs" / run_id
        fetcher = self._fetcher_with_media()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_id=run_id, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, media_download_cap=4, budget_max_calls=20,
            )
            assert (run_dir / virlo.VIRLO_MEDIA_MANIFEST_FILENAME).exists()

            from datetime import datetime, timedelta

            store.run_expiry_job(now=datetime.now().astimezone() + timedelta(days=31))
            assert not (run_dir / virlo.VIRLO_MEDIA_MANIFEST_FILENAME).exists()
        finally:
            store.close()
            trace.close()

    def test_no_media_downloaded_writes_no_manifest(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_id = "2026-08-10_manifest4"
        run_dir = tmp_path / "logs" / "runs" / run_id
        fetcher = self._fetcher_with_media()
        ctx, store, trace = _ctx(tmp_path, fetcher, run_id=run_id, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, media_download_cap=0, budget_max_calls=20,
            )
            assert not (run_dir / virlo.VIRLO_MEDIA_MANIFEST_FILENAME).exists()
            assert virlo.load_media_manifest(run_dir) == []
        finally:
            store.close()
            trace.close()


class TestVirloDigestOffDefault:
    def test_trends_digest_enabled_false_never_calls_digest_endpoint(self, tmp_path):
        key_path = _key_path(tmp_path)
        fetcher = FixtureFetcher(
            responses={f"v1/agents/{V1_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor.json")}
        )
        ctx, store, trace = _ctx(tmp_path, fetcher)
        try:
            result = virlo.collect(
                ctx, family="short_form_trends", key_path=key_path, trends_digest_enabled=False
            )
            assert result.outcome == "ok"
            assert not any("trends/digest" in url for url in fetcher.calls)
            assert len(fetcher.calls) == 1
        finally:
            store.close()
            trace.close()

    def test_source_config_default_is_digest_off_and_subpaths_on(self, tmp_path):
        from hypeagent.config_load import load_theme_research_config

        config_dir = tmp_path / "config"
        (config_dir / "themes").mkdir(parents=True)
        (config_dir / "themes" / "t.yaml").write_text(
            "theme:\n  name: t\n  languages: [en]\n"
            "research:\n  sources:\n    virlo:\n      enabled: true\n"
            "ranking:\n  ranking_config_version: 1\n",
            encoding="utf-8",
        )
        cfg = load_theme_research_config(config_dir, "t")
        virlo_cfg = cfg.sources["virlo"]
        assert virlo_cfg.trends_digest_enabled is False
        assert virlo_cfg.subpath_page_cap == 6
        assert virlo_cfg.media_download_cap == 24


class TestVirloIdempotentSecondCollectWithSubpaths:
    def test_second_call_same_day_makes_no_new_calls_and_does_not_rewrite_corpus(self, tmp_path):
        key_path = _key_path(tmp_path)
        run_dir = tmp_path / "logs" / "runs" / "2026-08-10_v1v1"
        fetcher = FixtureFetcher(
            responses={
                f"v1/agents/{V2_MONITOR_ID}/videos": _fr(FIXTURES / "virlo_videos_small.json"),
                f"v1/agents/{V2_MONITOR_ID}/slideshows": _fr(FIXTURES / "virlo_slideshows_small.json"),
                f"v1/agents/{V2_MONITOR_ID}": _fr(FIXTURES / "virlo_agent_monitor_v2.json"),
            }
        )
        ctx, store, trace = _ctx(tmp_path, fetcher, run_dir=run_dir)
        try:
            virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, budget_max_calls=20,
            )
            first_calls = len(fetcher.calls)
            corpus_path = run_dir / virlo.VIRLO_CORPUS_FILENAME
            first_bytes = corpus_path.read_bytes()

            result2 = virlo.collect(
                ctx, family="short_form_trends", key_path=key_path,
                monitor_ids=[V2_MONITOR_ID], trends_digest_enabled=False,
                subpath_page_cap=6, budget_max_calls=20,
            )
            assert result2.items == []
            assert len(fetcher.calls) == first_calls  # no new network calls at all
            assert corpus_path.read_bytes() == first_bytes
        finally:
            store.close()
            trace.close()
