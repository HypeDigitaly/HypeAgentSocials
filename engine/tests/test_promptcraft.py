"""Tests for hypeagent.promptcraft — N-D Image-Prompt Crafter (W8-9 Q3c,
extended W8-10): hero vs. per-slide prompts, the deterministic
STYLE/RENDER two-section scheme, image_brief reaching both branches, the
positive logo rule, proof-visual relevance, archetype rotation, the claim
gate check over crafted prompts, persistence, and the never-raises degrade
contract."""

from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from hypeagent import promptcraft
from hypeagent.brand_truth import ClaimSnapshot
from hypeagent.collectors.base import FetchResponse, FixtureFetcher
from hypeagent.config_load import LlmConfig, load_style_guide
from hypeagent.llm import LlmClient
from hypeagent.trace import TraceWriter

ENDPOINT_KEY = "chat/completions"


def _snapshot() -> ClaimSnapshot:
    return ClaimSnapshot(snapshot_id="s1", taken_at="2026-08-01", max_age_days=30, claims=[], path=Path("x.yaml"))


def _style_guide() -> dict:
    return {
        "brand": {"palette_primary_gradient": ["#302B87", "#00A39A"], "typeface": "Montserrat", "handle": "@hypedigitaly"},
        "visual_registers": {
            "editorial": {"ground": "bone/cream", "type": "italic serif", "accent": "teal", "mood": "premium"},
            "photographic_ugc": {
                "ground": "a genuine photorealistic photograph",
                "type": "plain white sans-serif TikTok-style sticker text with a soft drop shadow",
                "accent": "optional; natural photo palette dominates",
                "mood": "authentic, native, UGC-credible",
            },
        },
        "visual_archetypes": [{"key": "editorial-carousel", "desc": "Cream paper texture, italic serif headlines."}],
    }


def _visual_profile(**overrides) -> types.SimpleNamespace:
    """A minimal, duck-typed stand-in for ``analysis.VisualProfile`` --
    promptcraft only ever reads these fields via ``getattr(..., default)``,
    so a plain namespace is a faithful enough fixture for these tests
    without importing ``hypeagent.analysis`` (this module has no such
    dependency, and these tests should not introduce one)."""
    defaults = dict(
        recommended_generation_mode="photoreal_lifestyle_sticker",
        person_rate=0.1,
        face_visible_rate=0.05,
        dominant_person_framing="not-applicable",
        logo_rate=0.6,
        dominant_logo_treatment="composited",
        logos_ranked=[{"name": "Claude", "weight": 10.0}, {"name": "n8n", "weight": 4.0}],
        ground_mix={"photoreal": 0.8, "designed_graphic": 0.2},
        dominant_ground="photoreal",
        text_treatment_mix={"sticker": 0.9, "none": 0.1},
        dominant_text_style="sticker",
        dominant_text_density="light",
        numbering_rate=0.7,
        dominant_environment="home office desk",
        aspiration_signal_rate=0.1,
        evidence_item_ids=["item-1", "item-2"],
    )
    defaults.update(overrides)
    return types.SimpleNamespace(**defaults)


def _theme_playbook_with_profile(visual_profile, *, visual_archetypes_seen=None) -> types.SimpleNamespace:
    return types.SimpleNamespace(
        visual_profile=visual_profile, visual_archetypes_seen=visual_archetypes_seen or [],
    )


def _ok_response(payload: dict) -> FetchResponse:
    body = {
        "choices": [{"message": {"content": json.dumps(payload)}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 200, "completion_tokens": 100, "cost": 0.001},
    }
    return FetchResponse(status=200, headers={}, body=json.dumps(body).encode("utf-8"), latency_ms=10)


def _client(tmp_path, fetcher, **overrides) -> tuple[LlmClient, TraceWriter]:
    tw = TraceWriter(tmp_path / "trace.jsonl", "run-1")
    return LlmClient(config=LlmConfig(enabled=True, **overrides), fetcher=fetcher, api_key="sk-secret", trace=tw), tw


class TestPromptHygieneSystemPrompt:
    """W8-9 point 3 / W8-10 point 1: a live run leaked 'UII Label', the
    literal words 'Montserrat SemiBold', an internal series id printed as a
    watermark, and a quote-wrapped headline straight into client-facing
    images -- the N-D system prompt must explicitly forbid all of these
    failure modes."""

    def test_system_prompt_forbids_font_names_as_content(self):
        assert "font" in promptcraft.SYSTEM_PROMPT.lower()
        assert "Montserrat" in promptcraft.SYSTEM_PROMPT

    def test_system_prompt_requires_decorative_elements_to_specify_text_or_none(self):
        assert "no text on it" in promptcraft.SYSTEM_PROMPT

    def test_system_prompt_gives_the_no_quotation_marks_exact_text_pattern(self):
        assert "<<...>>" in promptcraft.SYSTEM_PROMPT
        assert "without surrounding quotation marks" in promptcraft.SYSTEM_PROMPT

    def test_system_prompt_forbids_placeholder_words(self):
        lowered = promptcraft.SYSTEM_PROMPT.lower()
        for placeholder in ("label", "ui text", "sample text", "lorem ipsum"):
            assert placeholder in lowered

    def test_system_prompt_forbids_rendering_the_series_token(self):
        lowered = promptcraft.SYSTEM_PROMPT.lower()
        assert "series" in lowered
        assert "watermark" in lowered

    def test_system_prompt_never_asks_for_aspect_ratio_language(self):
        lowered = promptcraft.SYSTEM_PROMPT.lower()
        assert "never state an aspect ratio" in lowered

    def test_hygiene_rules_are_actually_sent_to_the_model(self, tmp_path):
        fetcher = FixtureFetcher(
            responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "render": "A calm desk.", "relevance": "shows the desk."}]})}
        )
        client, tw = _client(tmp_path, fetcher)
        promptcraft.craft_prompts(
            llm_client=client, asset_id="ck1_linkedin", destination="linkedin", headline="AI agents",
            caption="caption", image_brief="A calm desk.", slides=None, style_guide=_style_guide(),
            theme_playbook=None, series_token="series-xyz",
        )
        tw.close()
        sent_body = json.loads(fetcher.request_bodies[0])
        system_text = sent_body["messages"][0]["content"]
        assert "<<...>>" in system_text
        assert "Montserrat" in system_text


class TestPositiveLogoRule:
    """W8-10 point 4 (marketer/UX findings item 4): suppression language
    ('no real brand logos', 'generic, unbranded') is DELETED; a positive
    rule directs rendering a named tool's actual logo."""

    def test_no_logo_suppression_language_present(self):
        lowered = promptcraft.SYSTEM_PROMPT.lower()
        assert "no real brand logo" not in lowered
        assert "generic, unbranded" not in lowered
        assert "unbranded" not in lowered

    def test_positive_logo_rule_present(self):
        lowered = promptcraft.SYSTEM_PROMPT.lower()
        assert "logo" in lowered
        assert "recognizable" in lowered
        assert "claude" in lowered

    def test_guardrails_no_longer_ban_logos_or_text_or_people(self):
        lowered = promptcraft.GUARDRAILS.lower()
        assert "no logos" not in lowered
        assert "no text" not in lowered
        assert "no people" not in lowered


class TestProofVisualRelevance:
    """W8-10 point 4: N-D must state the proof visual's causal link and
    calendar/inbox imagery is banned by default."""

    def test_system_prompt_requires_relevance_and_bans_calendar_inbox_by_default(self):
        lowered = promptcraft.SYSTEM_PROMPT.lower()
        assert "relevance" in lowered
        assert "calendar" in lowered
        assert "inbox" in lowered
        assert "banned" in lowered

    def test_system_prompt_caps_inset_strings(self):
        lowered = promptcraft.SYSTEM_PROMPT.lower()
        assert "6 short literal text strings" in lowered or "at most 6" in lowered


class TestHeroPath:
    def test_single_image_destination_produces_two_section_prompt(self, tmp_path):
        fetcher = FixtureFetcher(
            responses={
                ENDPOINT_KEY: _ok_response(
                    {"images": [{"slot": "hero", "render": "The text <<AI agents>> appears, rendered without surrounding quotation marks.", "relevance": "depicts the headline."}]}
                )
            }
        )
        client, tw = _client(tmp_path, fetcher)
        result = promptcraft.craft_prompts(
            llm_client=client, asset_id="ck1_linkedin", destination="linkedin", headline="AI agents",
            caption="caption", image_brief="A calm desk.", slides=None, style_guide=_style_guide(),
            theme_playbook=None, series_token="token-abc123",
        )
        tw.close()
        assert result.usable()
        hero = result.hero_prompt()
        assert hero is not None
        assert promptcraft.STYLE_LABEL in hero
        assert promptcraft.RENDER_LABEL in hero
        assert "AI agents" in hero
        assert result.images[0].relevance == "depicts the headline."
        # The internal series token is metadata only -- never rendered.
        assert "token-abc123" not in hero
        assert result.series_token == "token-abc123"

    def test_request_carries_guardrails_and_never_the_series_token(self, tmp_path):
        fetcher = FixtureFetcher(
            responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "render": "x.", "relevance": "y"}]})}
        )
        client, tw = _client(tmp_path, fetcher)
        promptcraft.craft_prompts(
            llm_client=client, asset_id="ck1_linkedin", destination="linkedin", headline="AI agents",
            caption="caption", image_brief="A calm desk.", slides=None, style_guide=_style_guide(),
            theme_playbook=None, series_token="series-xyz",
        )
        tw.close()
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "@hypedigitaly" not in user_text  # handle lives in the STYLE section, built by this module, not asked of the LLM
        assert "NSFW" in user_text
        assert "series-xyz" not in user_text  # W8-10: never instruct the model to render the series token
        assert "no text, no lettering" not in user_text.lower()  # the old dead constraints must not reappear
        assert "no people" not in user_text.lower()


class TestCarouselPath:
    def test_per_slide_prompts_share_identical_style_section_and_embed_exact_text(self, tmp_path):
        slides = [
            {"role": "cover", "title": "AI Agents Explained", "body": ""},
            {"role": "body", "title": "Step 1", "body": "Connect your CRM."},
        ]
        payload = {
            "images": [
                {"slot": "slide_01", "render": "The text <<AI Agents Explained>> appears, rendered without surrounding quotation marks.", "relevance": "cover matches the hook."},
                {"slot": "slide_02", "render": "The text <<Step 1>> appears and the text <<Connect your CRM.>> appears, rendered without surrounding quotation marks.", "relevance": "step 1 shows the CRM connection."},
            ]
        }
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response(payload)})
        client, tw = _client(tmp_path, fetcher)
        result = promptcraft.craft_prompts(
            llm_client=client, asset_id="ck1_instagram_feed", destination="instagram_feed", headline="",
            caption="", image_brief="Show the real n8n and Claude logos.", slides=slides, style_guide=_style_guide(),
            theme_playbook=None, series_token="series-tok",
        )
        tw.close()
        assert result.usable()
        assert [i.slot for i in result.images] == ["slide_01", "slide_02"]
        assert "AI Agents Explained" in result.images[0].prompt
        assert "Connect your CRM." in result.images[1].prompt

        # Series consistency: the STYLE section (everything before RENDER:)
        # is BYTE-IDENTICAL across every slide of this asset -- a
        # construction guarantee, not an LLM-repeatability hope.
        style_sections = [img.prompt.split(promptcraft.RENDER_LABEL, 1)[0] for img in result.images]
        assert style_sections[0] == style_sections[1]
        assert promptcraft.STYLE_LABEL in style_sections[0]

        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "Connect your CRM." in user_text
        assert "AI Agents Explained" in user_text

    def test_image_brief_reaches_the_carousel_branch(self, tmp_path):
        """W8-10 root-cause fix: the carousel branch used to DROP
        ``image_brief`` entirely (promptcraft.py:320-331 in the pre-fix
        code) -- the copywriter's own request to show real tool logos never
        reached N-D for a carousel asset. It must now reach the LLM request
        exactly like the hero branch already did."""
        slides = [{"role": "cover", "title": "Cover", "body": ""}]
        payload = {"images": [{"slot": "slide_01", "render": "The text <<Cover>> appears, rendered without surrounding quotation marks.", "relevance": "r"}]}
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response(payload)})
        client, tw = _client(tmp_path, fetcher)
        promptcraft.craft_prompts(
            llm_client=client, asset_id="ck1_instagram_feed", destination="instagram_feed", headline="",
            caption="", image_brief="Show real third-party tool logos (Claude, n8n).", slides=slides,
            style_guide=_style_guide(), theme_playbook=None, series_token="series-tok",
        )
        tw.close()
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "Show real third-party tool logos (Claude, n8n)." in user_text


class TestValidateCraftedPrompt:
    """W8-9 point 1c / W8-10 point 5: an invalid prompt (too short/long, cut
    off mid-sentence, missing a required exact-text segment, missing a
    section label, leaking a 12-hex token into RENDER, a font name inside
    <<...>>, or an over-length rendered body) is caught deterministically —
    independent of ``llm.LlmClient``'s own finish_reason check, a second
    line of defense."""

    def _labeled(self, render_body: str) -> str:
        return f"{promptcraft.STYLE_LABEL} clean editorial composition, teal accent, no people visible.\n\n{promptcraft.RENDER_LABEL} {render_body}"

    def test_valid_labeled_prompt_passes(self):
        assert promptcraft.validate_crafted_prompt(self._labeled("A calm desk with a laptop.")) is None

    def test_too_short_fails(self):
        reason = promptcraft.validate_crafted_prompt("Hi.")
        assert reason is not None and "short" in reason

    def test_cut_off_mid_sentence_fails(self):
        reason = promptcraft.validate_crafted_prompt(
            "A clean editorial composition with a bold headline and a platform built for"
        )
        assert reason is not None and "punctuation" in reason

    def test_missing_required_exact_text_fails(self):
        reason = promptcraft.validate_crafted_prompt(
            "A clean editorial slide with some unrelated copy on it.", required_texts=["Connect your CRM."],
        )
        assert reason is not None and "exact-text" in reason

    def test_present_required_exact_text_passes(self):
        reason = promptcraft.validate_crafted_prompt(
            self._labeled("A clean editorial slide where the text <<Connect your CRM.>> appears, rendered without "
            "surrounding quotation marks."),
            required_texts=["Connect your CRM."],
        )
        assert reason is None

    def test_missing_style_label_fails(self):
        reason = promptcraft.validate_crafted_prompt(f"{promptcraft.RENDER_LABEL} A clean editorial slide, no people visible.")
        assert reason is not None and "STYLE" in reason

    def test_missing_render_label_fails(self):
        reason = promptcraft.validate_crafted_prompt(f"{promptcraft.STYLE_LABEL} A clean editorial composition, no people visible.")
        assert reason is not None and "RENDER" in reason

    def test_twelve_hex_token_in_render_section_fails(self):
        reason = promptcraft.validate_crafted_prompt(
            self._labeled("The text <<4beb6d95640a>> appears as a watermark, rendered without surrounding quotation marks.")
        )
        assert reason is not None and "hex" in reason

    def test_twelve_hex_token_in_style_section_alone_is_fine(self):
        # A palette hex (6 chars incl. '#') never matches the 12-hex check;
        # this test just documents the boundary is the RENDER section only.
        prompt = f"{promptcraft.STYLE_LABEL} background #302b879e40aa (not literally 12 lowercase hex, just style metadata), no people visible.\n\n{promptcraft.RENDER_LABEL} A calm desk, no people visible."
        reason = promptcraft.validate_crafted_prompt(prompt)
        assert reason is None

    def test_font_name_inside_quoted_span_fails(self):
        reason = promptcraft.validate_crafted_prompt(
            self._labeled("The text <<Montserrat SemiBold>> appears, rendered without surrounding quotation marks.")
        )
        assert reason is not None and "font name" in reason

    def test_font_name_outside_quoted_span_is_fine(self):
        # Font names are ALLOWED in the STYLE section (never rendered) --
        # only a <<...>> renderable span is checked.
        prompt = f"{promptcraft.STYLE_LABEL} body typeface family Montserrat, described visually only, no people visible.\n\n{promptcraft.RENDER_LABEL} A calm desk, no people visible."
        reason = promptcraft.validate_crafted_prompt(prompt)
        assert reason is None

    def test_over_length_rendered_body_fails(self):
        long_body = " ".join(["word"] * 40)
        reason = promptcraft.validate_crafted_prompt(self._labeled("A calm desk, no people visible."), body_text=long_body)
        assert reason is not None and "word" in reason

    def test_body_at_or_under_cap_passes(self):
        ok_body = " ".join(["word"] * 28)
        reason = promptcraft.validate_crafted_prompt(self._labeled("A calm desk, no people visible."), body_text=ok_body)
        assert reason is None

    def test_aspect_ratio_language_fails(self):
        reason = promptcraft.validate_crafted_prompt(self._labeled("A calm desk in 1.91:1 aspect, no people visible."))
        assert reason is not None and "aspect" in reason

    def test_orientation_word_fails(self):
        reason = promptcraft.validate_crafted_prompt(self._labeled("A calm desk in a square frame, no people visible."))
        assert reason is not None and "aspect" in reason


class TestInvalidPromptFallback:
    def test_carousel_with_one_invalid_slide_degrades_the_whole_set(self, tmp_path):
        slides = [
            {"role": "cover", "title": "AI Agents Explained", "body": ""},
            {"role": "body", "title": "Step 1", "body": "Connect your CRM."},
        ]
        payload = {
            "images": [
                {"slot": "slide_01", "render": "The text <<AI Agents Explained>> appears, rendered without surrounding quotation marks.", "relevance": "r1"},
                # slide_02 is cut off mid-sentence -- no closing punctuation.
                {"slot": "slide_02", "render": "The text <<Step 1>> appears and the text <<Connect your CRM.>> appears and a platform built for", "relevance": "r2"},
            ]
        }
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response(payload)})
        client, tw = _client(tmp_path, fetcher)
        tracer = TraceWriter(tmp_path / "trace2.jsonl", "run-1")
        result = promptcraft.craft_prompts(
            llm_client=client, asset_id="ck1_instagram_feed", destination="instagram_feed", headline="",
            caption="", image_brief="", slides=slides, style_guide=_style_guide(), theme_playbook=None,
            series_token="series-tok", trace=tracer, stage="media",
        )
        tw.close()
        tracer.close()
        assert result.unavailable
        assert not result.usable()
        assert "slide_02" in (result.unavailable_reason or "")

        decisions = [
            json.loads(line)["detail"]["decision"]
            for line in (tmp_path / "trace2.jsonl").read_text(encoding="utf-8").splitlines()
            if json.loads(line)["event"] == "decision"
        ]
        assert any("failed validation" in d for d in decisions)

    def test_hero_with_invalid_prompt_becomes_unavailable_so_caller_falls_back(self, tmp_path):
        fetcher = FixtureFetcher(
            responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "render": "Hi", "relevance": "r"}]})}
        )
        client, tw = _client(tmp_path, fetcher)
        result = promptcraft.craft_prompts(
            llm_client=client, asset_id="ck1_linkedin", destination="linkedin", headline="AI agents",
            caption="caption", image_brief="A calm desk.", slides=None, style_guide=_style_guide(),
            theme_playbook=None, series_token="token-abc123",
        )
        tw.close()
        assert result.unavailable
        assert result.hero_prompt() is None


class TestGateCheck:
    def test_clean_prompts_pass_through_unchanged(self, tmp_path):
        prompt_set = promptcraft.CraftedPromptSet(
            asset_id="a1", images=[promptcraft.CraftedImage(slot="hero", prompt="A calm desk, teal accent, no people visible.")]
        )
        checked = promptcraft.gate_check_prompts(prompt_set, snapshot=_snapshot(), hard_excludes=None)
        assert not checked.gate_blocked

    def test_superlative_in_prompt_is_blocked(self, tmp_path):
        prompt_set = promptcraft.CraftedPromptSet(
            asset_id="a1", images=[promptcraft.CraftedImage(slot="hero", prompt="The best AI agent dashboard ever.")]
        )
        checked = promptcraft.gate_check_prompts(prompt_set, snapshot=_snapshot(), hard_excludes=None)
        assert checked.gate_blocked
        assert checked.gate_failing_spans

    def test_unavailable_set_is_not_gate_checked(self, tmp_path):
        prompt_set = promptcraft.CraftedPromptSet(asset_id="a1", unavailable=True, unavailable_reason="disabled")
        checked = promptcraft.gate_check_prompts(prompt_set, snapshot=_snapshot(), hard_excludes=None)
        assert checked is prompt_set
        assert not checked.gate_blocked


class TestDegradeNeverRaises:
    def test_llm_none_is_unavailable(self, tmp_path):
        result = promptcraft.craft_prompts(
            llm_client=None, asset_id="a1", destination="linkedin", headline="h", caption="c", image_brief="b",
            slides=None, style_guide=None, theme_playbook=None, series_token="t",
        )
        assert result.unavailable
        assert result.hero_prompt() is None

    def test_llm_call_failure_is_unavailable(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: FetchResponse(status=500, headers={}, body=b"boom", latency_ms=1)})
        client, tw = _client(tmp_path, fetcher)
        result = promptcraft.craft_prompts(
            llm_client=client, asset_id="a1", destination="linkedin", headline="h", caption="c", image_brief="b",
            slides=None, style_guide=None, theme_playbook=None, series_token="t",
        )
        tw.close()
        assert result.unavailable
        assert result.hero_prompt() is None


class TestPersistenceAndRoundTrip:
    def test_write_and_load_round_trip(self, tmp_path):
        run_dir = tmp_path / "run"
        prompt_sets = {
            "ck1_linkedin": promptcraft.CraftedPromptSet(
                asset_id="ck1_linkedin",
                images=[promptcraft.CraftedImage(slot="hero", prompt="a desk", relevance="shows the desk")],
                series_token="tok123",
            ),
            "ck1_instagram_feed": promptcraft.CraftedPromptSet(
                asset_id="ck1_instagram_feed", unavailable=True, unavailable_reason="LLM disabled",
            ),
        }
        promptcraft.write_media_prompts(run_dir, prompt_sets)
        reloaded = promptcraft.load_media_prompts(run_dir)
        assert reloaded["ck1_linkedin"].hero_prompt() == "a desk"
        assert reloaded["ck1_linkedin"].images[0].relevance == "shows the desk"
        assert reloaded["ck1_linkedin"].series_token == "tok123"
        assert reloaded["ck1_instagram_feed"].unavailable

    def test_load_missing_file_returns_empty_dict(self, tmp_path):
        assert promptcraft.load_media_prompts(tmp_path / "nope") == {}


class TestArchetypeRegisterPick:
    def test_prefers_playbook_observed_archetype(self):
        class _FakeThemePlaybook:
            visual_archetypes_seen = ["editorial-carousel", "statement-card"]

        archetype, register = promptcraft.pick_archetype_register(
            destination="instagram_feed", style_guide=_style_guide(), theme_playbook=_FakeThemePlaybook()
        )
        assert archetype == "editorial-carousel"
        assert register == "editorial"

    def test_falls_back_to_style_guide_default_when_no_playbook(self):
        style_guide = {"platforms": {"linkedin": {"visual": {"default_archetypes": ["statement-card"]}}}}
        archetype, _register = promptcraft.pick_archetype_register(
            destination="linkedin", style_guide=style_guide, theme_playbook=None
        )
        assert archetype == "statement-card"

    def test_no_candidates_returns_none(self):
        archetype, _register = promptcraft.pick_archetype_register(
            destination="linkedin", style_guide=None, theme_playbook=None,
        )
        assert archetype is None


class TestArchetypeRotation:
    """W8-10 point 7: deterministic rotation over ``visual_archetypes_seen``
    (deduplicated) keyed by ``asset_index`` -- no two consecutive assets in
    one run should land on the same archetype, purely via modular
    arithmetic (no randomness)."""

    class _FakeThemePlaybook:
        visual_archetypes_seen = ["editorial-carousel", "statement-card", "dense-spec-card"]

    def test_consecutive_indices_never_repeat(self):
        seen: list[str | None] = []
        for i in range(6):
            archetype, _register = promptcraft.pick_archetype_register(
                destination="linkedin", style_guide=None, theme_playbook=self._FakeThemePlaybook(), asset_index=i,
            )
            seen.append(archetype)
        for a, b in zip(seen, seen[1:]):
            assert a != b

    def test_rotation_is_deterministic_across_repeated_calls(self):
        results_run1 = [
            promptcraft.pick_archetype_register(
                destination="linkedin", style_guide=None, theme_playbook=self._FakeThemePlaybook(), asset_index=i,
            )[0]
            for i in range(5)
        ]
        results_run2 = [
            promptcraft.pick_archetype_register(
                destination="linkedin", style_guide=None, theme_playbook=self._FakeThemePlaybook(), asset_index=i,
            )[0]
            for i in range(5)
        ]
        assert results_run1 == results_run2

    def test_rotation_wraps_around(self):
        archetype0, _ = promptcraft.pick_archetype_register(
            destination="linkedin", style_guide=None, theme_playbook=self._FakeThemePlaybook(), asset_index=0,
        )
        archetype3, _ = promptcraft.pick_archetype_register(
            destination="linkedin", style_guide=None, theme_playbook=self._FakeThemePlaybook(), asset_index=3,
        )
        assert archetype0 == archetype3 == "editorial-carousel"

    def test_default_asset_index_zero_matches_old_first_pick_behavior(self):
        archetype, _register = promptcraft.pick_archetype_register(
            destination="linkedin", style_guide=None, theme_playbook=self._FakeThemePlaybook(),
        )
        assert archetype == "editorial-carousel"


class TestStageWiringResumeIdempotency:
    """W8-9 Q3c: ``stages._craft_media_prompts_for_run`` persists
    ``media_prompts.yaml`` and reuses an already-crafted asset_id rather
    than re-crafting (and re-spending) it — the "resume round trip" the
    task note asks for."""

    def _ctx(self, tmp_path, fetcher):
        from hypeagent.brand_truth import BrandFacts, BrandTruthPanel
        from hypeagent.config_load import (
            GenerationConfig, MappingDistanceBands, MediaConfig, OpenAICompatibleConfig, ThemeConfig,
        )
        from hypeagent.spin import SpinResult
        from hypeagent import stages

        ctx = stages.RunContext(
            run_id="2026-08-10_pc1", config_dir=tmp_path / "config", logs_dir=tmp_path / "logs",
            fetcher_factory=lambda: fetcher,
        )
        ctx.theme_config = ThemeConfig(hard_excludes={}, fingerprint="x")
        ctx.generation = GenerationConfig(
            destinations=["linkedin"], copy_provider="openrouter", repair_budget=2,
            mapping_distance=MappingDistanceBands(), exemplar_pool=[],
            openai_compatible=OpenAICompatibleConfig(), media=MediaConfig(),
            llm=LlmConfig(enabled=True),
        )
        facts = BrandFacts(
            identity={"legal_name": "Test Co"}, capabilities_positive=[], capabilities_negative=[],
            icp=[], cta_set=[], pricing_policy="prices-never-stated", pricing_rationale="",
            hard_excludes_ref="config/hard_excludes.yaml", spin_notes={}, source_path=Path("brand_facts.yaml"),
        )
        panel = BrandTruthPanel(
            facts=facts, snapshot=_snapshot(), snapshot_age_days=1, band="fresh", copy_allowed=True,
            degrade_reason=None,
        )
        ctx.extra["brand_truth_panel"] = panel
        ctx.extra["spin_results"] = {
            "ck1": SpinResult(
                cluster_key="ck1", topic="AI agents", language="en", icp_id="icp", icp_text="x", pain="y",
                offer_id=None, offer_text=None, mapping_distance="far", mapping_score=0.1, cta_id="c",
                cta_class="content", cta_text="Learn more", band="Low", value_only=True, rationale_line="r",
            )
        }
        return ctx

    def test_second_invocation_reuses_persisted_prompts_without_new_calls(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-secret-test")
        from hypeagent.copy_gen import AssetCopyStatus
        from hypeagent import stages

        fetcher = FixtureFetcher(
            responses={
                ENDPOINT_KEY: _ok_response(
                    {"images": [{"slot": "hero", "render": "A fully crafted hero render, ending properly.", "relevance": "r"}]}
                )
            }
        )
        ctx = self._ctx(tmp_path, fetcher)
        statuses = [
            AssetCopyStatus(
                asset_id="ck1_linkedin", cluster_key="ck1", destination="linkedin", status="gated-pass",
                attempt=1, headline="h", caption="c", image_brief="a desk",
            )
        ]
        tw = TraceWriter(tmp_path / "logs" / "trace1.jsonl", ctx.run_id)
        try:
            first = stages._craft_media_prompts_for_run(ctx, tw, statuses)
        finally:
            tw.close()
        assert "A fully crafted hero render, ending properly." in (first["ck1_linkedin"].hero_prompt() or "")
        assert len(fetcher.calls) == 1

        run_dir = ctx.logs_dir / "runs" / ctx.run_id
        assert (run_dir / "media_prompts.yaml").exists()

        # A second invocation (simulating --resume re-entering media) must
        # not re-call the LLM for an asset_id already on disk.
        ctx.extra.pop("llm_client", None)
        tw2 = TraceWriter(tmp_path / "logs" / "trace2.jsonl", ctx.run_id)
        try:
            second = stages._craft_media_prompts_for_run(ctx, tw2, statuses)
        finally:
            tw2.close()
        assert second["ck1_linkedin"].hero_prompt() == first["ck1_linkedin"].hero_prompt()
        assert len(fetcher.calls) == 1  # unchanged — no new network call


# ---------------------------------------------------------------------------
# W8-10 Phase 8 (dynamic inspiration) -- generation modes/registers.
# ---------------------------------------------------------------------------


class TestGenerationModeRegistry:
    """Every mode maps to a valid register + a non-empty composition
    template; ``designed_card`` is the universal, unchanged fallback."""

    def test_every_mode_maps_to_a_known_register_and_directive(self):
        valid_registers = {"editorial", "hype", promptcraft.PHOTOGRAPHIC_REGISTER}
        for mode, spec in promptcraft.GENERATION_MODES.items():
            assert spec.register in valid_registers, f"{mode} has unknown register {spec.register!r}"
            assert isinstance(spec.composition_directive, str) and spec.composition_directive.strip()

    def test_required_modes_are_present(self):
        expected = {
            "photoreal_lifestyle_sticker", "photoreal_person_ugc", "aspirational_lifestyle_scene",
            "live_app_ui", "native_caption_frame", "meme_reaction_split", "flat_lay_product_grid",
            "designed_card",
        }
        assert expected <= set(promptcraft.GENERATION_MODES)

    def test_designed_card_is_the_default_and_has_no_fixed_archetype(self):
        assert promptcraft.DEFAULT_MODE == "designed_card"
        assert promptcraft.GENERATION_MODES["designed_card"].archetype is None
        assert promptcraft.GENERATION_MODES["designed_card"].register == "editorial"

    def test_photographic_modes_use_the_photographic_register(self):
        for mode in (
            "photoreal_lifestyle_sticker", "photoreal_person_ugc", "aspirational_lifestyle_scene",
            "native_caption_frame", "meme_reaction_split", "flat_lay_product_grid",
        ):
            assert promptcraft.GENERATION_MODES[mode].register == promptcraft.PHOTOGRAPHIC_REGISTER

    def test_live_app_ui_composition_directive_asks_for_real_branded_ui(self):
        directive = promptcraft.GENERATION_MODES["live_app_ui"].composition_directive.lower()
        assert "real" in directive
        assert "logo" in directive or "wordmark" in directive
        assert "never a generic" in directive or "never suppress" in directive


class TestModeSelection:
    """W8-10 Phase 8: ``pick_generation_mode`` honors
    ``visual_profile.recommended_generation_mode`` when present, rotates
    over this theme's own derived "top modes" (never a flat archetype list),
    and falls back cleanly (mode=None, register="editorial") when no
    ``visual_profile`` is on the playbook at all — full backward
    compatibility with the pre-Phase-8 archetype-only path."""

    def test_primary_mode_is_the_recommended_one(self):
        vp = _visual_profile(recommended_generation_mode="photoreal_person_ugc", person_rate=0.9)
        theme_playbook = _theme_playbook_with_profile(vp)
        mode, archetype, register = promptcraft.pick_generation_mode(
            destination="tiktok", style_guide=_style_guide(), theme_playbook=theme_playbook, asset_index=0,
        )
        assert mode == "photoreal_person_ugc"
        assert register == promptcraft.PHOTOGRAPHIC_REGISTER
        assert archetype == promptcraft.GENERATION_MODES["photoreal_person_ugc"].archetype

    def test_unknown_recommended_mode_falls_back_to_default(self):
        vp = _visual_profile(recommended_generation_mode="some-mode-analysis-never-emits")
        theme_playbook = _theme_playbook_with_profile(vp)
        mode, _archetype, register = promptcraft.pick_generation_mode(
            destination="tiktok", style_guide=_style_guide(), theme_playbook=theme_playbook, asset_index=0,
        )
        assert mode == promptcraft.DEFAULT_MODE
        assert register == "editorial"

    def test_no_visual_profile_returns_none_mode_and_editorial_register(self):
        class _OldPlaybook:
            visual_archetypes_seen = ["editorial-carousel"]

        mode, archetype, register = promptcraft.pick_generation_mode(
            destination="linkedin", style_guide=_style_guide(), theme_playbook=_OldPlaybook(), asset_index=0,
        )
        assert mode is None
        assert register == "editorial"
        assert archetype == "editorial-carousel"

    def test_no_theme_playbook_at_all_falls_back_cleanly(self):
        mode, _archetype, register = promptcraft.pick_generation_mode(
            destination="linkedin", style_guide=_style_guide(), theme_playbook=None, asset_index=0,
        )
        assert mode is None
        assert register == "editorial"

    def test_pick_archetype_register_wrapper_matches_legacy_behavior_without_visual_profile(self):
        class _FakeThemePlaybook:
            visual_archetypes_seen = ["editorial-carousel", "statement-card"]

        archetype, register = promptcraft.pick_archetype_register(
            destination="instagram_feed", style_guide=_style_guide(), theme_playbook=_FakeThemePlaybook()
        )
        assert archetype == "editorial-carousel"
        assert register == "editorial"

    def test_rotation_over_top_modes_avoids_consecutive_repeats(self):
        vp = _visual_profile(
            recommended_generation_mode="photoreal_lifestyle_sticker",
            aspiration_signal_rate=0.9,  # also qualifies aspirational_lifestyle_scene
        )
        theme_playbook = _theme_playbook_with_profile(vp, visual_archetypes_seen=["statement-card", "dense-spec-card"])
        picks = [
            promptcraft.pick_generation_mode(
                destination="tiktok", style_guide=_style_guide(), theme_playbook=theme_playbook, asset_index=i,
            )
            for i in range(6)
        ]
        pairs = [(mode, archetype) for mode, archetype, _register in picks]
        for a, b in zip(pairs, pairs[1:]):
            assert a != b

    def test_rotation_is_deterministic(self):
        vp = _visual_profile(aspiration_signal_rate=0.9)
        theme_playbook = _theme_playbook_with_profile(vp)
        run1 = [
            promptcraft.pick_generation_mode(
                destination="tiktok", style_guide=_style_guide(), theme_playbook=theme_playbook, asset_index=i,
            )
            for i in range(4)
        ]
        run2 = [
            promptcraft.pick_generation_mode(
                destination="tiktok", style_guide=_style_guide(), theme_playbook=theme_playbook, asset_index=i,
            )
            for i in range(4)
        ]
        assert run1 == run2

    def test_designed_card_rotation_still_varies_archetype(self):
        """When the picked mode is ``designed_card`` (no fixed archetype),
        the legacy archetype rotation still applies underneath it."""
        vp = _visual_profile(
            recommended_generation_mode="designed_card", ground_mix={"designed_graphic": 1.0},
            dominant_ground="designed_graphic",
        )
        theme_playbook = _theme_playbook_with_profile(
            vp, visual_archetypes_seen=["statement-card", "dense-spec-card"],
        )
        mode0, archetype0, _ = promptcraft.pick_generation_mode(
            destination="linkedin", style_guide=_style_guide(), theme_playbook=theme_playbook, asset_index=0,
        )
        mode1, archetype1, _ = promptcraft.pick_generation_mode(
            destination="linkedin", style_guide=_style_guide(), theme_playbook=theme_playbook, asset_index=1,
        )
        assert mode0 == mode1 == "designed_card"
        assert archetype0 != archetype1


class TestPhotographicRegisterBranching:
    """W8-10 Phase 8 point 1: the STYLE block builder branches per register
    -- editorial cream/Didone directives never leak into a photographic_ugc
    prompt, and vice versa."""

    def _hero_style_section(self, *, register: str, mode: str | None = None, tmp_path, aspiration_signal_rate=0.1):
        vp = _visual_profile(
            recommended_generation_mode=mode or "photoreal_lifestyle_sticker",
            ground_mix=(
                {"photoreal": 0.9} if register == promptcraft.PHOTOGRAPHIC_REGISTER else {"designed_graphic": 0.9}
            ),
            dominant_ground="photoreal" if register == promptcraft.PHOTOGRAPHIC_REGISTER else "designed_graphic",
            aspiration_signal_rate=aspiration_signal_rate,
        )
        theme_playbook = _theme_playbook_with_profile(vp) if register == promptcraft.PHOTOGRAPHIC_REGISTER else None
        fetcher = FixtureFetcher(
            responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "render": "A scene.", "relevance": "r"}]})}
        )
        client, tw = _client(tmp_path, fetcher)
        result = promptcraft.craft_prompts(
            llm_client=client, asset_id="a1", destination="tiktok", headline="h", caption="c",
            image_brief="b", slides=None, style_guide=_style_guide(), theme_playbook=theme_playbook,
            series_token="t",
        )
        tw.close()
        return result.hero_prompt() or ""

    def test_photographic_prompt_never_contains_editorial_directives(self, tmp_path):
        prompt = self._hero_style_section(register=promptcraft.PHOTOGRAPHIC_REGISTER, tmp_path=tmp_path)
        lowered = prompt.lower()
        assert "didone" not in lowered
        assert "bone/cream" not in lowered
        assert "cream" not in lowered

    def test_photographic_prompt_never_forces_the_brand_palette(self, tmp_path):
        prompt = self._hero_style_section(register=promptcraft.PHOTOGRAPHIC_REGISTER, tmp_path=tmp_path)
        assert "#302B87" not in prompt
        assert "#00A39A" not in prompt

    def test_photographic_prompt_carries_its_own_photographic_directives(self, tmp_path):
        prompt = self._hero_style_section(register=promptcraft.PHOTOGRAPHIC_REGISTER, tmp_path=tmp_path)
        lowered = prompt.lower()
        assert "photorealistic photograph" in lowered
        assert "sticker" in lowered

    def test_editorial_prompt_never_contains_photographic_sticker_directive(self, tmp_path):
        prompt = self._hero_style_section(register="editorial", tmp_path=tmp_path)
        lowered = prompt.lower()
        assert "tiktok-style sticker text" not in lowered

    def test_editorial_prompt_still_carries_the_brand_palette(self, tmp_path):
        prompt = self._hero_style_section(register="editorial", tmp_path=tmp_path)
        assert "#302B87" in prompt

    def test_photographic_environment_line_reflects_visual_profile(self, tmp_path):
        prompt = self._hero_style_section(
            register=promptcraft.PHOTOGRAPHIC_REGISTER, tmp_path=tmp_path, aspiration_signal_rate=0.9,
        )
        lowered = prompt.lower()
        assert "home office desk" in lowered
        assert "aspirational" in lowered or "high-end" in lowered


class TestValidateCraftedPromptRegisterLeak:
    def _labeled(self, render_body: str, style_body: str) -> str:
        return f"{promptcraft.STYLE_LABEL} {style_body}\n\n{promptcraft.RENDER_LABEL} {render_body}"

    def test_photographic_prompt_with_editorial_leak_fails(self):
        prompt = self._labeled(
            "A calm photo, no people visible.",
            "a genuine photorealistic photograph but somehow also a bone/cream paper texture and Didone serif display.",
        )
        reason = promptcraft.validate_crafted_prompt(prompt, register=promptcraft.PHOTOGRAPHIC_REGISTER)
        assert reason is not None
        assert "wrong-register" in reason or "leak" in reason

    def test_photographic_prompt_without_leak_passes(self):
        prompt = self._labeled(
            "A calm desk photo, no people visible.",
            "a genuine photorealistic photograph, plain white sticker text, no people visible.",
        )
        reason = promptcraft.validate_crafted_prompt(prompt, register=promptcraft.PHOTOGRAPHIC_REGISTER)
        assert reason is None

    def test_editorial_prompt_with_didone_is_unaffected_when_register_not_passed(self):
        # Backward compatibility: omitting ``register`` (every pre-Phase-8
        # call site) never triggers this new check.
        prompt = self._labeled(
            "A calm desk, no people visible.", "bone/cream paper texture, italic Didone serif, no people visible.",
        )
        reason = promptcraft.validate_crafted_prompt(prompt)
        assert reason is None

    def test_editorial_register_itself_is_never_checked_for_the_leak(self):
        prompt = self._labeled(
            "A calm desk, no people visible.", "bone/cream paper texture, italic Didone serif, no people visible.",
        )
        reason = promptcraft.validate_crafted_prompt(prompt, register="editorial")
        assert reason is None


class TestPersonPolicyWording:
    """Operator decision (W8-10 Phase 8): NOT a blanket people ban --
    synthetic, non-identifiable people (including visible faces) are
    permitted; only identifiable real individuals/celebrities stay banned."""

    def test_guardrails_state_synthetic_people_are_permitted(self):
        lowered = promptcraft.GUARDRAILS.lower()
        assert "synthetic" in lowered
        assert "identifiable" in lowered
        assert "celebrity" in lowered
        assert "permitted" in lowered

    def test_guardrails_no_longer_read_as_a_blanket_ban(self):
        lowered = promptcraft.GUARDRAILS.lower()
        assert "no identifiable real individuals or celebrity likeness in the image" in lowered
        assert "no real person" not in lowered
        assert "no people" not in lowered

    def test_system_prompt_states_photoreal_person_ugc_expects_visible_faces(self):
        lowered = promptcraft.SYSTEM_PROMPT.lower()
        assert "synthetic" in lowered
        assert "non-identifiable" in lowered
        assert "visible face" in lowered

    def test_style_guide_reject_list_is_not_a_blanket_people_ban(self):
        config_dir = Path(__file__).resolve().parents[2] / "config"
        style_guide = load_style_guide(config_dir)
        reject = [str(r) for r in style_guide.get("reject") or []]
        people_line = next((r for r in reject if "celebrity" in r.lower()), None)
        assert people_line is not None
        assert "synthetic" in people_line.lower()
        assert "allowed" in people_line.lower() or "permitted" in people_line.lower()


class TestLiveAppUiRelaxation:
    def test_style_guide_screenshot_as_proof_no_longer_demands_unretouched_zero_design(self):
        config_dir = Path(__file__).resolve().parents[2] / "config"
        style_guide = load_style_guide(config_dir)
        entries = {e["key"]: e.get("desc", "") for e in style_guide.get("visual_archetypes") or [] if isinstance(e, dict)}
        desc = entries.get("screenshot-as-proof", "").lower()
        assert desc
        # The desc now MENTIONS the old phrasing (to document the change),
        # but must never STATE it as this archetype's own current
        # requirement -- i.e. it must not open with that demand.
        assert not desc.strip().lower().startswith("unretouched")
        assert "zero design applied." not in desc
        assert "real, current, accurately branded" in desc

    def test_style_guide_has_photographic_ugc_register(self):
        config_dir = Path(__file__).resolve().parents[2] / "config"
        style_guide = load_style_guide(config_dir)
        registers = style_guide.get("visual_registers") or {}
        assert "photographic_ugc" in registers
        block = registers["photographic_ugc"]
        assert "sticker" in str(block.get("type", "")).lower()


class TestVisualProfileBriefThreading:
    """W8-10 Phase 8 point 3: dominant text style, numbering, logos_ranked,
    dominant_environment, and (when supplied) analyzed_items summaries reach
    the LLM's own RENDER-section brief."""

    def test_visual_profile_fields_reach_the_llm_request(self, tmp_path):
        vp = _visual_profile()
        theme_playbook = _theme_playbook_with_profile(vp)
        fetcher = FixtureFetcher(
            responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "render": "A scene.", "relevance": "r"}]})}
        )
        client, tw = _client(tmp_path, fetcher)
        promptcraft.craft_prompts(
            llm_client=client, asset_id="a1", destination="tiktok", headline="5 tools I use",
            caption="c", image_brief="b", slides=None, style_guide=_style_guide(),
            theme_playbook=theme_playbook, series_token="t",
        )
        tw.close()
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "sticker" in user_text
        assert "home office desk" in user_text
        assert "Claude" in user_text
        # headline contains a bare number ("5") and numbering_rate=0.7 > 0.5.
        assert "own number" in user_text

    def test_analyzed_item_summaries_reach_the_llm_request(self, tmp_path):
        vp = _visual_profile(evidence_item_ids=["item-1"])
        theme_playbook = _theme_playbook_with_profile(vp)
        analyzed_item = types.SimpleNamespace(
            item_id="item-1", summary="A desk photo with a giant Claude icon and sticker text.",
        )
        fetcher = FixtureFetcher(
            responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "render": "A scene.", "relevance": "r"}]})}
        )
        client, tw = _client(tmp_path, fetcher)
        promptcraft.craft_prompts(
            llm_client=client, asset_id="a1", destination="tiktok", headline="h", caption="c",
            image_brief="b", slides=None, style_guide=_style_guide(), theme_playbook=theme_playbook,
            series_token="t", analyzed_items=[analyzed_item],
        )
        tw.close()
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "A desk photo with a giant Claude icon and sticker text." in user_text

    def test_generation_mode_composition_directive_reaches_the_llm_request(self, tmp_path):
        vp = _visual_profile(recommended_generation_mode="photoreal_person_ugc", person_rate=0.9)
        theme_playbook = _theme_playbook_with_profile(vp)
        fetcher = FixtureFetcher(
            responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "render": "A scene.", "relevance": "r"}]})}
        )
        client, tw = _client(tmp_path, fetcher)
        promptcraft.craft_prompts(
            llm_client=client, asset_id="a1", destination="tiktok", headline="h", caption="c",
            image_brief="b", slides=None, style_guide=_style_guide(), theme_playbook=theme_playbook,
            series_token="t",
        )
        tw.close()
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "photoreal_person_ugc" in user_text
        assert "phone-camera" in user_text or "selfie" in user_text

    def test_no_visual_profile_omits_the_brief_line(self, tmp_path):
        fetcher = FixtureFetcher(
            responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "render": "A scene.", "relevance": "r"}]})}
        )
        client, tw = _client(tmp_path, fetcher)
        promptcraft.craft_prompts(
            llm_client=client, asset_id="a1", destination="tiktok", headline="h", caption="c",
            image_brief="b", slides=None, style_guide=_style_guide(), theme_playbook=None, series_token="t",
        )
        tw.close()
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "Generation mode for this image" not in user_text
        assert "this theme's own visual evidence" not in user_text.lower()
