"""Tests for hypeagent.analysis — N-A Trend & Visual Analyst (W8-9 Q3a):
playbook construction from a corpus fixture, image selection, and every
degrade path (no corpus / LLM disabled / call failed) never raising."""

from __future__ import annotations

import json

import pytest
import yaml

from hypeagent import analysis
from hypeagent.collectors import virlo as virlo_collector
from hypeagent.collectors.base import FetchResponse, FixtureFetcher
from hypeagent.config_load import LlmConfig
from hypeagent.llm import LlmClient
from hypeagent.trace import TraceWriter

ENDPOINT_KEY = "chat/completions"


def _corpus() -> dict:
    return {
        "monitor_id": "mon-1",
        "monitor_finalized": True,
        "themes": [
            {
                "name": "AI Agents for Outbound Sales", "stable_key": "ai-agents-outbound", "confidence": 0.9,
                "video_count": 42, "tactics": ["show booked calls", "before/after"], "why_it_works": "concrete proof",
                "evidence_video_ids": ["v1"],
            },
        ],
        "viral_tactics": ["hook in first 2 seconds", "screenshot proof"],
        "top_10_breakdown": {"videos": [{"video_id": "v1"}]},
        "connecting_thread": "AI agents replacing manual prospecting",
        "key_highlight": "screenshot proof format dominates",
        "videos": [
            {
                "id": "v1", "url": "https://tiktok.com/x", "platform": "tiktok", "views": 500000,
                "description": "watch this AI agent book 40 calls", "hook_text": "I built an AI agent that...",
                "summary": "creator shows a booked-calls screenshot", "hashtags": ["ai", "sales"],
            },
        ],
        "slideshows": [
            {
                "id": "s1", "url": "https://instagram.com/x", "platform": "instagram", "views": 100000,
                "panel_texts": ["Step 1: connect your CRM", "Step 2: let the agent qualify leads"],
                "panel_count": 2, "narrative_arc": "problem-solution",
            },
        ],
    }


def _style_guide() -> dict:
    return {
        "visual_archetypes": [
            {"key": "screenshot-as-proof", "desc": "Unretouched software screenshot as proof."},
            {"key": "statement-card", "desc": "Big-type statement card."},
        ],
        "reject": ["fabricated social proof", "prices or price-shaped claims"],
    }


def _playbook_llm_payload() -> dict:
    return {
        "themes": [
            {
                "theme": "AI Agents for Outbound Sales",
                "winning_hooks": ["I built an AI agent that..."],
                "formats": ["screenshot proof", "before/after"],
                "visual_archetypes_seen": ["screenshot-as-proof"],
                "tools_shown": ["CRM dashboard"],
                "numbers_used": ["40 calls booked"],
                "platform_norms": {"linkedin": "long-form proof post", "instagram_feed": "carousel walkthrough", "tiktok": "hook + screenshot"},
            }
        ],
        "global": {
            "viral_tactics_digest": ["hook in first 2 seconds", "screenshot proof"],
            "connecting_thread": "AI agents replacing manual prospecting",
            "do_not_do": [],
        },
    }


def _ok_response(payload: dict) -> FetchResponse:
    body = {
        "choices": [{"message": {"content": json.dumps(payload)}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 800, "completion_tokens": 300, "cost": 0.004},
    }
    return FetchResponse(status=200, headers={}, body=json.dumps(body).encode("utf-8"), latency_ms=50)


def _llm_client(tmp_path, fetcher, **cfg_overrides) -> tuple[LlmClient, TraceWriter]:
    tw = TraceWriter(tmp_path / "trace.jsonl", "run-1")
    client = LlmClient(config=LlmConfig(enabled=True, **cfg_overrides), fetcher=fetcher, api_key="sk-secret", trace=tw)
    return client, tw


class TestPlaybookBuiltFromCorpus:
    def test_playbook_written_from_corpus_and_persisted(self, tmp_path):
        run_dir = tmp_path / "run"
        virlo_collector.write_virlo_corpus(run_dir, _corpus())
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response(_playbook_llm_payload())})
        client, tw = _llm_client(tmp_path, fetcher)

        playbook = analysis.run_trend_visual_analyst(
            run_dir=run_dir, media_dir=tmp_path / "no_media", style_guide=_style_guide(), llm_client=client, trace=tw,
        )
        tw.close()

        assert not playbook.skipped and not playbook.degraded
        assert playbook.themes[0].theme == "AI Agents for Outbound Sales"
        assert "screenshot-as-proof" in playbook.themes[0].visual_archetypes_seen
        assert playbook.connecting_thread == "AI agents replacing manual prospecting"

        path = run_dir / "analysis" / "viral_playbook.yaml"
        assert path.exists()
        on_disk = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert on_disk["themes"][0]["theme"] == "AI Agents for Outbound Sales"

        # Round-trips back through the loader.
        reloaded = analysis.load_viral_playbook(run_dir)
        assert reloaded is not None
        assert reloaded.theme_playbook("AI Agents for Outbound Sales").winning_hooks

    def test_prompt_includes_corpus_and_archetype_vocabulary(self, tmp_path):
        run_dir = tmp_path / "run"
        virlo_collector.write_virlo_corpus(run_dir, _corpus())
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response(_playbook_llm_payload())})
        client, tw = _llm_client(tmp_path, fetcher)
        analysis.run_trend_visual_analyst(
            run_dir=run_dir, media_dir=tmp_path / "no_media", style_guide=_style_guide(), llm_client=client, trace=tw,
        )
        tw.close()
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        if isinstance(user_text, list):
            user_text = "".join(p.get("text", "") for p in user_text if p.get("type") == "text")
        assert "AI Agents for Outbound Sales" in user_text
        assert "screenshot-as-proof" in user_text
        assert "fabricated social proof" in user_text


class TestDegradePathsNeverFailTheRun:
    def test_no_corpus_skips_without_raising(self, tmp_path):
        run_dir = tmp_path / "run"
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response(_playbook_llm_payload())})
        client, tw = _llm_client(tmp_path, fetcher)
        playbook = analysis.run_trend_visual_analyst(
            run_dir=run_dir, media_dir=tmp_path / "no_media", style_guide=None, llm_client=client, trace=tw,
        )
        tw.close()
        assert playbook.skipped and not playbook.degraded
        assert playbook.themes == []
        assert (run_dir / "analysis" / "viral_playbook.yaml").exists()
        assert len(fetcher.calls) == 0  # never even attempted a call

    def test_llm_disabled_skips_without_raising(self, tmp_path):
        run_dir = tmp_path / "run"
        virlo_collector.write_virlo_corpus(run_dir, _corpus())
        tw = TraceWriter(tmp_path / "trace.jsonl", "run-1")
        playbook = analysis.run_trend_visual_analyst(
            run_dir=run_dir, media_dir=tmp_path / "no_media", style_guide=None, llm_client=None, trace=tw,
        )
        tw.close()
        assert playbook.skipped
        assert "disabled" in (playbook.skip_reason or "").lower()

    def test_llm_call_failure_degrades_without_raising(self, tmp_path):
        run_dir = tmp_path / "run"
        virlo_collector.write_virlo_corpus(run_dir, _corpus())
        response = FetchResponse(status=500, headers={}, body=b"boom", latency_ms=5)
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: response})
        client, tw = _llm_client(tmp_path, fetcher)
        playbook = analysis.run_trend_visual_analyst(
            run_dir=run_dir, media_dir=tmp_path / "no_media", style_guide=None, llm_client=client, trace=tw,
        )
        tw.close()
        assert playbook.degraded and not playbook.skipped
        assert playbook.themes == []
        assert (run_dir / "analysis" / "viral_playbook.yaml").exists()

    def test_budget_exhausted_degrades_without_raising(self, tmp_path):
        run_dir = tmp_path / "run"
        virlo_collector.write_virlo_corpus(run_dir, _corpus())
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response(_playbook_llm_payload())})
        client, tw = _llm_client(tmp_path, fetcher, per_run_call_cap=0)
        playbook = analysis.run_trend_visual_analyst(
            run_dir=run_dir, media_dir=tmp_path / "no_media", style_guide=None, llm_client=client, trace=tw,
        )
        tw.close()
        assert playbook.degraded
        assert len(fetcher.calls) == 0


class TestPromptSizeReduction:
    """W8-9 (post-live-run token-starvation fix): the N-A prompt must stay
    well under the old ~70k-token size -- fewer items, top themes only, and
    every caption-shaped field trimmed to ~300 chars. The on-disk
    ``virlo_corpus.yaml`` research artifact itself is never touched (module
    docstring) -- only the PROMPT copy this builds."""

    def _big_corpus(self) -> dict:
        long_caption = "x" * 5000
        themes = [
            {
                "name": f"theme-{i}", "stable_key": f"theme-{i}", "confidence": 1.0 - (i * 0.01),
                "video_count": 10, "tactics": ["a"], "why_it_works": "because", "evidence_video_ids": [],
            }
            for i in range(20)
        ]
        videos = [
            {
                "id": f"v{i}", "url": f"https://tiktok.com/{i}", "platform": "tiktok", "views": 1000 - i,
                "description": long_caption, "hook_text": long_caption, "summary": long_caption,
                "hashtags": ["ai"], "thumbnail_url": "https://cdn.example.com/thumb.jpg",
                "author_handle_hash": "deadbeef" * 8,
            }
            for i in range(20)
        ]
        slideshows = [
            {
                "id": f"s{i}", "url": f"https://instagram.com/{i}", "platform": "instagram", "views": 1000 - i,
                "panel_texts": [long_caption] * 10, "panel_count": 10,
                "image_urls": ["https://cdn.example.com/panel.jpg"] * 10,
            }
            for i in range(20)
        ]
        return {
            "themes": themes, "viral_tactics": [f"tactic-{i}" for i in range(30)],
            "top_10_breakdown": {}, "connecting_thread": "x", "key_highlight": "y",
            "videos": videos, "slideshows": slideshows,
        }

    def test_truncate_corpus_caps_item_counts(self):
        truncated = analysis._truncate_corpus(self._big_corpus())
        assert len(truncated["themes"]) == analysis.MAX_THEMES_IN_PROMPT
        assert len(truncated["videos"]) == analysis.MAX_VIDEOS_IN_PROMPT
        assert len(truncated["slideshows"]) == analysis.MAX_SLIDESHOWS_IN_PROMPT
        assert len(truncated["viral_tactics"]) == analysis.MAX_VIRAL_TACTICS_IN_PROMPT

    def test_truncate_corpus_trims_caption_fields_and_panel_texts(self):
        truncated = analysis._truncate_corpus(self._big_corpus())
        for video in truncated["videos"]:
            assert len(video["description"]) <= analysis.PROMPT_CAPTION_TRIM_CHARS + 1
            assert len(video["hook_text"]) <= analysis.PROMPT_CAPTION_TRIM_CHARS + 1
            assert len(video["summary"]) <= analysis.PROMPT_CAPTION_TRIM_CHARS + 1
            assert "thumbnail_url" not in video
            assert "author_handle_hash" not in video
        for slideshow in truncated["slideshows"]:
            assert len(slideshow["panel_texts"]) <= analysis.MAX_PANEL_TEXTS_PER_SLIDESHOW
            assert all(len(t) <= analysis.PROMPT_CAPTION_TRIM_CHARS + 1 for t in slideshow["panel_texts"])
            assert "image_urls" not in slideshow

    def test_prompt_size_stays_well_under_the_old_70k_token_incident_size(self):
        system, user_parts, _schema_hint = analysis.build_analyst_prompt(
            corpus=self._big_corpus(), style_guide=None, image_paths=[],
        )
        text_part = user_parts[0]["text"]
        # Rough token estimate (~4 chars/token, the conservative direction
        # for English/mixed text) -- the old shape hit ~70k tokens; this
        # must land comfortably under the new <30k-token target.
        assert (len(system) + len(text_part)) / 4 < 30_000


class TestImageSelection:
    def test_prefers_slideshow_panels_over_video_thumbnails_and_caps(self, tmp_path):
        media_dir = tmp_path / "virlo_media"
        media_dir.mkdir(parents=True)
        for i in range(3):
            (media_dir / f"video_thumbnail_thumb{i}.jpg").write_bytes(b"x")
        for i in range(2):
            (media_dir / f"slideshow_panel_panel{i}.jpg").write_bytes(b"x")

        selected = analysis.select_analysis_images(media_dir, max_images=3)
        assert len(selected) == 3
        assert all(p.name.startswith("slideshow_panel_") for p in selected[:2])
        assert selected[2].name.startswith("video_thumbnail_")

    def test_zero_cap_selects_nothing(self, tmp_path):
        media_dir = tmp_path / "virlo_media"
        media_dir.mkdir(parents=True)
        (media_dir / "video_thumbnail_a.jpg").write_bytes(b"x")
        assert analysis.select_analysis_images(media_dir, max_images=0) == []

    def test_missing_media_dir_selects_nothing(self, tmp_path):
        assert analysis.select_analysis_images(tmp_path / "does_not_exist", max_images=5) == []
