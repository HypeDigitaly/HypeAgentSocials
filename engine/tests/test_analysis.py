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
        """No manifest on file for this run (legacy fallback path) —
        pre-W8-10 behaviour: hash-sorted filenames, panels before
        thumbnails, no guaranteed quota."""
        media_dir = tmp_path / "virlo_media"
        media_dir.mkdir(parents=True)
        for i in range(3):
            (media_dir / f"video_thumbnail_thumb{i}.jpg").write_bytes(b"x")
        for i in range(2):
            (media_dir / f"slideshow_panel_panel{i}.jpg").write_bytes(b"x")

        selected = analysis.select_analysis_images(media_dir, max_images=3)
        assert len(selected) == 3
        assert all(p.path.name.startswith("slideshow_panel_") for p in selected[:2])
        assert selected[2].path.name.startswith("video_thumbnail_")

    def test_zero_cap_selects_nothing(self, tmp_path):
        media_dir = tmp_path / "virlo_media"
        media_dir.mkdir(parents=True)
        (media_dir / "video_thumbnail_a.jpg").write_bytes(b"x")
        assert analysis.select_analysis_images(media_dir, max_images=0) == []

    def test_missing_media_dir_selects_nothing(self, tmp_path):
        assert analysis.select_analysis_images(tmp_path / "does_not_exist", max_images=5) == []


class TestImageSelectionWithManifest:
    """W8-10 Phase 8: views-ordered selection via the image<->item join
    manifest, with a guaranteed video-thumbnail quota so person/talking-head
    evidence is never silently excluded by high-view slideshow panels."""

    def _manifest_entry(self, filename, *, kind, views, item_id=None, panel_index=None, theme_key=None):
        return virlo_collector.MediaManifestEntry(
            filename=filename, item_id=item_id or filename, item_kind=kind,
            panel_index=panel_index, views=views, theme_key=theme_key, caption=f"caption for {filename}",
        )

    def test_selects_by_views_not_hash_order(self, tmp_path):
        media_dir = tmp_path / "virlo_media"
        media_dir.mkdir(parents=True)
        for name in ("slideshow_panel_zzz.jpg", "slideshow_panel_aaa.jpg", "video_thumbnail_bbb.jpg"):
            (media_dir / name).write_bytes(b"x")
        manifest = [
            self._manifest_entry("slideshow_panel_zzz.jpg", kind="slideshow", views=100),
            self._manifest_entry("slideshow_panel_aaa.jpg", kind="slideshow", views=900000),
            self._manifest_entry("video_thumbnail_bbb.jpg", kind="video", views=500000),
        ]
        selected = analysis.select_analysis_images(media_dir, max_images=2, manifest=manifest)
        assert [s.path.name for s in selected] == ["slideshow_panel_aaa.jpg", "video_thumbnail_bbb.jpg"]

    def test_thumbnail_quota_guarantees_a_slot_even_when_outranked_by_views(self, tmp_path):
        media_dir = tmp_path / "virlo_media"
        media_dir.mkdir(parents=True)
        panel_names = [f"slideshow_panel_p{i}.jpg" for i in range(5)]
        thumb_name = "video_thumbnail_low_views.jpg"
        for name in panel_names + [thumb_name]:
            (media_dir / name).write_bytes(b"x")
        manifest = [
            self._manifest_entry(name, kind="slideshow", views=1_000_000 - i) for i, name in enumerate(panel_names)
        ] + [self._manifest_entry(thumb_name, kind="video", views=1)]  # lowest views of all, by a wide margin

        selected = analysis.select_analysis_images(media_dir, max_images=3, manifest=manifest)
        assert len(selected) == 3
        assert any(s.path.name == thumb_name for s in selected)  # guaranteed, despite last-place views

    def test_no_thumbnails_available_never_forces_an_empty_slot(self, tmp_path):
        media_dir = tmp_path / "virlo_media"
        media_dir.mkdir(parents=True)
        for i in range(3):
            (media_dir / f"slideshow_panel_p{i}.jpg").write_bytes(b"x")
        manifest = [
            self._manifest_entry(f"slideshow_panel_p{i}.jpg", kind="slideshow", views=100 - i) for i in range(3)
        ]
        selected = analysis.select_analysis_images(media_dir, max_images=3, manifest=manifest)
        assert len(selected) == 3

    def test_manifest_entries_without_a_matching_file_on_disk_are_skipped(self, tmp_path):
        media_dir = tmp_path / "virlo_media"
        media_dir.mkdir(parents=True)
        (media_dir / "video_thumbnail_present.jpg").write_bytes(b"x")
        manifest = [
            self._manifest_entry("video_thumbnail_present.jpg", kind="video", views=10),
            self._manifest_entry("video_thumbnail_expired.jpg", kind="video", views=999999),
        ]
        selected = analysis.select_analysis_images(media_dir, max_images=5, manifest=manifest)
        assert [s.path.name for s in selected] == ["video_thumbnail_present.jpg"]


# ---------------------------------------------------------------------------
# W8-10 Phase 8 — prompt image labeling.
# ---------------------------------------------------------------------------


class TestPromptImageLabeling:
    def test_each_image_is_preceded_by_a_labeled_text_part(self, tmp_path):
        media_dir = tmp_path / "virlo_media"
        media_dir.mkdir(parents=True)
        (media_dir / "video_thumbnail_a.jpg").write_bytes(b"x")
        manifest = [
            virlo_collector.MediaManifestEntry(
                filename="video_thumbnail_a.jpg", item_id="vid-42", item_kind="video",
                panel_index=None, views=123456, theme_key="AI Agents", caption="I built an AI agent that...",
            )
        ]
        images = analysis.select_analysis_images(media_dir, max_images=5, manifest=manifest)
        assert len(images) == 1

        system, user_parts, _schema = analysis.build_analyst_prompt(
            corpus={"themes": [], "videos": [], "slideshows": []}, style_guide=None, image_paths=images,
        )
        text_parts = [p["text"] for p in user_parts if p.get("type") == "text"]
        joined = "\n".join(text_parts)
        assert "IMAGE 0" in joined
        assert "item vid-42" in joined
        assert "video panel n/a" in joined
        assert "123456 views" in joined
        assert "I built an AI agent that..." in joined

    def test_analyzed_items_instruction_present_when_images_given(self, tmp_path):
        media_dir = tmp_path / "virlo_media"
        media_dir.mkdir(parents=True)
        (media_dir / "video_thumbnail_a.jpg").write_bytes(b"x")
        manifest = [
            virlo_collector.MediaManifestEntry(
                filename="video_thumbnail_a.jpg", item_id="vid-1", item_kind="video",
                panel_index=None, views=10, theme_key=None, caption=None,
            )
        ]
        images = analysis.select_analysis_images(media_dir, max_images=5, manifest=manifest)
        _system, user_parts, _schema = analysis.build_analyst_prompt(
            corpus={"themes": [], "videos": [], "slideshows": []}, style_guide=None, image_paths=images,
        )
        joined = "\n".join(p["text"] for p in user_parts if p.get("type") == "text")
        assert "analyzed_items" in joined
        assert "consists_of" in joined


# ---------------------------------------------------------------------------
# Q6 re-audit R2 — corpus filtered to this run's ranking-winning themes.
# ---------------------------------------------------------------------------


class TestWinningTopicsFilter:
    def _two_theme_corpus(self) -> dict:
        return {
            "themes": [
                {"name": "AI Agents for Outbound Sales", "confidence": 0.9, "video_count": 10},
                {"name": "Claude Code for Development", "confidence": 0.95, "video_count": 20},
            ],
            "videos": [], "slideshows": [], "viral_tactics": [],
        }

    def test_filters_to_matching_winning_topic_only(self):
        truncated = analysis._truncate_corpus(
            self._two_theme_corpus(), winning_topics=["AI Agents for Outbound Sales"]
        )
        names = [t["name"] for t in truncated["themes"]]
        assert names == ["AI Agents for Outbound Sales"]

    def test_no_match_falls_back_to_unfiltered_rather_than_empty(self):
        truncated = analysis._truncate_corpus(
            self._two_theme_corpus(), winning_topics=["Something Entirely Unrelated Xyz"]
        )
        assert len(truncated["themes"]) == 2

    def test_no_winning_topics_analyzes_everything(self):
        truncated = analysis._truncate_corpus(self._two_theme_corpus(), winning_topics=None)
        assert len(truncated["themes"]) == 2

    def test_prompt_mentions_winning_topics_when_given(self):
        system, user_parts, _schema = analysis.build_analyst_prompt(
            corpus=self._two_theme_corpus(), style_guide=None, image_paths=[],
            winning_topics=["AI Agents for Outbound Sales"],
        )
        joined = "\n".join(p["text"] for p in user_parts if p.get("type") == "text")
        assert "AI Agents for Outbound Sales" in joined
        assert "ranking already picked" in joined


# ---------------------------------------------------------------------------
# Q6 re-audit R4 — platform_norms noise filter.
# ---------------------------------------------------------------------------


class TestPlatformNormsPolish:
    def test_noise_lines_are_dropped_entirely(self):
        norms = analysis._coerce_platform_norms(
            {
                "linkedin": "not observed in corpus",
                "instagram_feed": "carousel walkthrough, tiktok evidence",
                "tiktok": "hook + screenshot",
            }
        )
        assert "linkedin" not in norms
        assert norms["instagram_feed"] == "carousel walkthrough, tiktok evidence"
        assert norms["tiktok"] == "hook + screenshot"

    def test_prompt_instructs_omission_and_evidence_labeling(self):
        system, user_parts, _schema = analysis.build_analyst_prompt(
            corpus={"themes": [], "videos": [], "slideshows": []}, style_guide=None, image_paths=[],
        )
        joined = "\n".join(p["text"] for p in user_parts if p.get("type") == "text")
        assert "OMIT" in joined
        assert "not observed in corpus" in joined  # named as the exact anti-pattern to avoid
        assert "TikTok-heavy" in joined


# ---------------------------------------------------------------------------
# W8-10 Phase 8 — themes[0] silent-fallback warning made visible.
# ---------------------------------------------------------------------------


class TestThemesFallbackWarning:
    def _playbook(self) -> analysis.ViralPlaybook:
        return analysis.ViralPlaybook(themes=[analysis.ThemePlaybook(theme="Only Theme")])

    def test_exact_match_never_warns(self):
        warnings = []
        result = self._playbook().theme_playbook("Only Theme", warn=warnings.append)
        assert result.theme == "Only Theme"
        assert warnings == []

    def test_mismatch_falls_back_and_warns(self):
        warnings = []
        result = self._playbook().theme_playbook("Some Other Topic", warn=warnings.append)
        assert result.theme == "Only Theme"
        assert len(warnings) == 1
        assert "Some Other Topic" in warnings[0]
        assert "themes[0]" in warnings[0] or "Only Theme" in warnings[0]

    def test_none_theme_name_falls_back_and_warns(self):
        warnings = []
        result = self._playbook().theme_playbook(None, warn=warnings.append)
        assert result.theme == "Only Theme"
        assert len(warnings) == 1

    def test_no_themes_at_all_returns_none_without_warning(self):
        warnings = []
        result = analysis.ViralPlaybook(themes=[]).theme_playbook("anything", warn=warnings.append)
        assert result is None
        assert warnings == []

    def test_warn_is_optional_and_backward_compatible(self):
        # copy_gen.py's existing call site never passes warn= -- must not raise.
        result = self._playbook().theme_playbook("mismatch")
        assert result.theme == "Only Theme"


# ---------------------------------------------------------------------------
# W8-10 Phase 8 — analyzed_items parsing (lenient: unknown enum values kept
# as plain strings, never a crash).
# ---------------------------------------------------------------------------


class TestAnalyzedItemsParsing:
    def _images(self) -> list[analysis.SelectedImage]:
        return [
            analysis.SelectedImage(
                path=__import__("pathlib").Path("video_thumbnail_a.jpg"),
                entry=virlo_collector.MediaManifestEntry(
                    filename="video_thumbnail_a.jpg", item_id="vid-1", item_kind="video",
                    panel_index=None, views=5000, theme_key="AI Agents for Outbound Sales",
                    caption="I built an AI agent...",
                ),
            ),
            analysis.SelectedImage(
                path=__import__("pathlib").Path("slideshow_panel_b.jpg"),
                entry=virlo_collector.MediaManifestEntry(
                    filename="slideshow_panel_b.jpg", item_id="slide-1", item_kind="slideshow",
                    panel_index=2, views=9000, theme_key="AI Agents for Outbound Sales",
                    caption="Step 3: qualify the lead",
                ),
            ),
        ]

    def test_injected_fields_come_from_the_manifest_not_the_model(self):
        data = {
            "analyzed_items": [
                {
                    "image_index": 0, "post_kind": "value",
                    "person": {"present": True, "prominence": "primary", "face_visible": True, "framing": "waist-up", "count": 1},
                    "confidence": 0.8, "summary": "founder demoing an AI agent", "consists_of": ["face", "app_ui"],
                }
            ]
        }
        items = analysis._parse_analyzed_items(data["analyzed_items"], self._images())
        assert len(items) == 1
        item = items[0]
        assert item.item_id == "vid-1"
        assert item.media_file == "video_thumbnail_a.jpg"
        assert item.theme_key == "AI Agents for Outbound Sales"
        assert item.views == 5000
        assert item.post_kind == "value"
        assert item.person.present is True
        assert item.person.framing == "waist-up"
        assert item.summary == "founder demoing an AI agent"
        assert item.consists_of == ["face", "app_ui"]

    def test_unknown_enum_value_is_kept_as_a_plain_string_not_a_crash(self):
        data = [
            {
                "image_index": 0,
                "visual_style": {"ground": "cyberpunk-hologram", "realism": "unknown-alien-style"},
                "text_treatment": {"style": "some-brand-new-style-the-model-invented"},
            }
        ]
        items = analysis._parse_analyzed_items(data, self._images())
        assert items[0].visual_style.ground == "cyberpunk-hologram"
        assert items[0].visual_style.realism == "unknown-alien-style"
        assert items[0].text_treatment.style == "some-brand-new-style-the-model-invented"

    def test_out_of_range_image_index_is_skipped_not_a_crash(self):
        data = [{"image_index": 99, "post_kind": "value"}]
        assert analysis._parse_analyzed_items(data, self._images()) == []

    def test_malformed_image_index_is_skipped_not_a_crash(self):
        data = [{"image_index": "not-an-int", "post_kind": "value"}, {"post_kind": "value"}]
        assert analysis._parse_analyzed_items(data, self._images()) == []

    def test_non_list_payload_never_crashes(self):
        assert analysis._parse_analyzed_items({"not": "a list"}, self._images()) == []
        assert analysis._parse_analyzed_items(None, self._images()) == []

    def test_no_images_never_crashes(self):
        assert analysis._parse_analyzed_items([{"image_index": 0}], []) == []

    def test_playbook_round_trips_analyzed_items_through_yaml(self, tmp_path):
        images = self._images()
        data = {
            "themes": [{"theme": "AI Agents for Outbound Sales"}],
            "analyzed_items": [
                {"image_index": 0, "post_kind": "value", "summary": "s1"},
                {"image_index": 1, "post_kind": "showcase", "summary": "s2", "text_treatment": {"has_numbering": True}},
            ],
        }
        playbook = analysis.parse_playbook_response(data, images=images)
        analysis.attach_visual_profiles(playbook, items_available_by_theme={"AI Agents for Outbound Sales": 5})

        run_dir = tmp_path / "run"
        analysis.write_viral_playbook(run_dir, playbook)
        reloaded = analysis.load_viral_playbook(run_dir)
        assert reloaded is not None
        assert len(reloaded.analyzed_items) == 2
        assert reloaded.analyzed_items[0].summary == "s1"
        theme = reloaded.theme_playbook("AI Agents for Outbound Sales")
        assert theme.visual_profile is not None
        assert theme.visual_profile.items_analyzed == 2
        assert theme.visual_profile.items_available == 5


# ---------------------------------------------------------------------------
# W8-10 Phase 8 — visual_profile math: rates, dominants, and every branch of
# the recommended_generation_mode rule table.
# ---------------------------------------------------------------------------


class TestVisualProfileMath:
    def _item(self, **overrides) -> analysis.AnalyzedItem:
        base = dict(
            item_id="i1", media_file="f1.jpg", panel_index=None, theme_key="T", views=1000,
        )
        base.update(overrides)
        item = analysis.AnalyzedItem(**{k: v for k, v in base.items() if k in (
            "item_id", "media_file", "panel_index", "theme_key", "views",
        )})
        for key in ("post_kind", "person", "logos", "visual_style", "text_treatment", "environment", "confidence", "summary", "consists_of"):
            if key in overrides:
                setattr(item, key, overrides[key])
        return item

    def test_empty_items_produce_an_all_zero_unknown_profile(self):
        profile = analysis.compute_visual_profile("T", [], items_available=0)
        assert profile.items_analyzed == 0
        assert profile.person_rate == 0.0
        assert profile.dominant_ground == "unknown"
        assert profile.recommended_generation_mode == "designed_card"
        assert profile.evidence_item_ids == []

    def test_person_and_face_visible_rates(self):
        items = [
            self._item(item_id="a", person=analysis.PersonAnalysis(present=True, face_visible=True)),
            self._item(item_id="b", person=analysis.PersonAnalysis(present=True, face_visible=False)),
            self._item(item_id="c", person=analysis.PersonAnalysis(present=False)),
            self._item(item_id="d", person=analysis.PersonAnalysis(present=False)),
        ]
        profile = analysis.compute_visual_profile("T", items, items_available=4)
        assert profile.person_rate == pytest.approx(0.5)
        assert profile.face_visible_rate == pytest.approx(0.25)

    def test_logo_rate_and_ranked_names_views_weighted(self):
        items = [
            self._item(item_id="a", views=100, logos=analysis.LogosAnalysis(present=True, names=["Claude"], treatment="prominent")),
            self._item(item_id="b", views=900, logos=analysis.LogosAnalysis(present=True, names=["n8n"], treatment="subtle")),
            self._item(item_id="c", views=10, logos=analysis.LogosAnalysis(present=False)),
        ]
        profile = analysis.compute_visual_profile("T", items, items_available=3)
        assert profile.logo_rate == pytest.approx(2 / 3)
        assert profile.logos_ranked[0]["name"] == "n8n"  # higher view-weight wins first place

    def test_ground_mix_is_views_weighted_and_dominant_matches(self):
        items = [
            self._item(item_id="a", views=100, visual_style=analysis.VisualStyleAnalysis(ground="photoreal")),
            self._item(item_id="b", views=900, visual_style=analysis.VisualStyleAnalysis(ground="designed_graphic")),
        ]
        profile = analysis.compute_visual_profile("T", items, items_available=2)
        assert profile.dominant_ground == "designed_graphic"
        assert profile.ground_mix["designed_graphic"] > profile.ground_mix["photoreal"]
        assert sum(profile.ground_mix.values()) == pytest.approx(1.0)

    def test_numbering_and_aspiration_rates(self):
        items = [
            self._item(item_id="a", text_treatment=analysis.TextTreatmentAnalysis(has_numbering=True),
                       environment=analysis.EnvironmentAnalysis(aspiration_signal=True)),
            self._item(item_id="b", text_treatment=analysis.TextTreatmentAnalysis(has_numbering=False),
                       environment=analysis.EnvironmentAnalysis(aspiration_signal=False)),
        ]
        profile = analysis.compute_visual_profile("T", items, items_available=2)
        assert profile.numbering_rate == pytest.approx(0.5)
        assert profile.aspiration_signal_rate == pytest.approx(0.5)

    def test_evidence_item_ids_ordered_by_views_descending(self):
        items = [
            self._item(item_id="low", views=10),
            self._item(item_id="high", views=999),
            self._item(item_id="mid", views=500),
        ]
        profile = analysis.compute_visual_profile("T", items, items_available=3)
        assert profile.evidence_item_ids == ["high", "mid", "low"]

    def test_items_available_is_never_less_than_items_analyzed(self):
        items = [self._item(item_id="a")]
        profile = analysis.compute_visual_profile("T", items, items_available=0)
        assert profile.items_available >= profile.items_analyzed


class TestRecommendedGenerationModeRuleTable:
    def test_photoreal_sticker_high_person_rate_is_photoreal_person_ugc(self):
        mode = analysis.recommended_generation_mode_for(
            dominant_ground="photoreal", person_rate=0.6, dominant_text_style="sticker",
        )
        assert mode == "photoreal_person_ugc"

    def test_photoreal_sticker_low_person_rate_is_photoreal_lifestyle_sticker(self):
        mode = analysis.recommended_generation_mode_for(
            dominant_ground="photoreal", person_rate=0.1, dominant_text_style="sticker",
        )
        assert mode == "photoreal_lifestyle_sticker"

    def test_person_rate_boundary_is_inclusive_at_0_4(self):
        mode = analysis.recommended_generation_mode_for(
            dominant_ground="photoreal", person_rate=0.4, dominant_text_style="sticker",
        )
        assert mode == "photoreal_person_ugc"

    def test_designed_graphic_dominant_is_designed_card(self):
        mode = analysis.recommended_generation_mode_for(
            dominant_ground="designed_graphic", person_rate=0.9, dominant_text_style="sticker",
        )
        assert mode == "designed_card"

    def test_app_screenshot_dominant_is_live_app_ui(self):
        mode = analysis.recommended_generation_mode_for(
            dominant_ground="app_screenshot", person_rate=0.0, dominant_text_style="editorial_typography",
        )
        assert mode == "live_app_ui"

    def test_unrecognized_ground_falls_back_to_designed_card(self):
        mode = analysis.recommended_generation_mode_for(
            dominant_ground="ugc_casual", person_rate=0.9, dominant_text_style="native_caption",
        )
        assert mode == "designed_card"

    def test_photoreal_without_sticker_text_falls_back_to_designed_card(self):
        mode = analysis.recommended_generation_mode_for(
            dominant_ground="photoreal", person_rate=0.9, dominant_text_style="editorial_typography",
        )
        assert mode == "designed_card"
