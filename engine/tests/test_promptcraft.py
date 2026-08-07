"""Tests for hypeagent.promptcraft — N-D Image-Prompt Crafter (W8-9 Q3c):
hero vs. per-slide prompts, shared style tokens, verbatim slide-text
embedding, the claim-gate check over crafted prompts, persistence, and the
never-raises degrade contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hypeagent import promptcraft
from hypeagent.brand_truth import ClaimSnapshot
from hypeagent.collectors.base import FetchResponse, FixtureFetcher
from hypeagent.config_load import LlmConfig
from hypeagent.llm import LlmClient
from hypeagent.trace import TraceWriter

ENDPOINT_KEY = "chat/completions"


def _snapshot() -> ClaimSnapshot:
    return ClaimSnapshot(snapshot_id="s1", taken_at="2026-08-01", max_age_days=30, claims=[], path=Path("x.yaml"))


def _style_guide() -> dict:
    return {
        "brand": {"palette_primary_gradient": ["#302B87", "#00A39A"], "typeface": "Montserrat", "handle": "@hypedigitaly"},
        "visual_registers": {"editorial": {"ground": "bone/cream", "type": "italic serif", "accent": "teal", "mood": "premium"}},
        "visual_archetypes": [{"key": "editorial-carousel", "desc": "Cream paper texture, italic serif headlines."}],
    }


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
    """W8-9 point 3: a live run leaked 'UII Label', the literal words
    'Montserrat SemiBold', and a quote-wrapped headline straight into
    client-facing images -- the N-D system prompt must explicitly forbid
    all three failure modes."""

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

    def test_hygiene_rules_are_actually_sent_to_the_model(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "prompt": "x"}]})})
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


class TestHeroPath:
    def test_single_image_destination_produces_one_hero_prompt(self, tmp_path):
        fetcher = FixtureFetcher(
            responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "prompt": "A calm desk. @hypedigitaly. token-abc123."}]})}
        )
        client, tw = _client(tmp_path, fetcher)
        result = promptcraft.craft_prompts(
            llm_client=client, asset_id="ck1_linkedin", destination="linkedin", headline="AI agents",
            caption="caption", image_brief="A calm desk.", slides=None, style_guide=_style_guide(),
            theme_playbook=None, series_token="token-abc123",
        )
        tw.close()
        assert result.usable()
        assert result.hero_prompt() == "A calm desk. @hypedigitaly. token-abc123."
        assert result.images[0].slot == "hero"

    def test_request_carries_style_tokens_and_guardrails(self, tmp_path):
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "prompt": "x"}]})})
        client, tw = _client(tmp_path, fetcher)
        promptcraft.craft_prompts(
            llm_client=client, asset_id="ck1_linkedin", destination="linkedin", headline="AI agents",
            caption="caption", image_brief="A calm desk.", slides=None, style_guide=_style_guide(),
            theme_playbook=None, series_token="series-xyz",
        )
        tw.close()
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "series-xyz" in user_text
        assert "@hypedigitaly" in user_text
        assert "NSFW" in user_text
        assert "no text, no lettering" not in user_text.lower()  # the old dead constraints must not reappear
        assert "no people" not in user_text.lower()


class TestCarouselPath:
    def test_per_slide_prompts_share_style_tokens_and_embed_exact_text(self, tmp_path):
        slides = [
            {"role": "cover", "title": "AI Agents Explained", "body": ""},
            {"role": "body", "title": "Step 1", "body": "Connect your CRM."},
        ]
        payload = {
            "images": [
                {"slot": "slide_01", "prompt": "series-tok AI Agents Explained editorial-carousel #302B87."},
                {"slot": "slide_02", "prompt": "series-tok Step 1 Connect your CRM. editorial-carousel #302B87."},
            ]
        }
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_response(payload)})
        client, tw = _client(tmp_path, fetcher)
        result = promptcraft.craft_prompts(
            llm_client=client, asset_id="ck1_instagram_feed", destination="instagram_feed", headline="",
            caption="", image_brief="", slides=slides, style_guide=_style_guide(), theme_playbook=None,
            series_token="series-tok",
        )
        tw.close()
        assert result.usable()
        assert [i.slot for i in result.images] == ["slide_01", "slide_02"]
        assert "AI Agents Explained" in result.images[0].prompt
        assert "Connect your CRM." in result.images[1].prompt
        assert all("series-tok" in i.prompt for i in result.images)  # shared consistency token

        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "Connect your CRM." in user_text
        assert "AI Agents Explained" in user_text


class TestValidateCraftedPrompt:
    """W8-9 point 1c: an invalid prompt (too short/long, cut off mid-
    sentence, or missing a required exact-text segment) is caught
    deterministically — independent of ``llm.LlmClient``'s own
    finish_reason check, a second line of defense."""

    def test_valid_prompt_passes(self):
        assert promptcraft.validate_crafted_prompt(
            "A calm desk with a laptop, teal accent lighting, no people visible.",
        ) is None

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
            "A clean editorial slide where the text <<Connect your CRM.>> appears, rendered without "
            "surrounding quotation marks.",
            required_texts=["Connect your CRM."],
        )
        assert reason is None


class TestInvalidPromptFallback:
    def test_carousel_with_one_invalid_slide_degrades_the_whole_set(self, tmp_path):
        slides = [
            {"role": "cover", "title": "AI Agents Explained", "body": ""},
            {"role": "body", "title": "Step 1", "body": "Connect your CRM."},
        ]
        payload = {
            "images": [
                {"slot": "slide_01", "prompt": "series-tok AI Agents Explained editorial-carousel #302B87."},
                # slide_02 is cut off mid-sentence -- no closing punctuation.
                {"slot": "slide_02", "prompt": "series-tok Step 1 Connect your CRM. and a platform built for"},
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
            responses={ENDPOINT_KEY: _ok_response({"images": [{"slot": "hero", "prompt": "Hi"}]})}
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
                asset_id="ck1_linkedin", images=[promptcraft.CraftedImage(slot="hero", prompt="a desk")]
            ),
            "ck1_instagram_feed": promptcraft.CraftedPromptSet(
                asset_id="ck1_instagram_feed", unavailable=True, unavailable_reason="LLM disabled",
            ),
        }
        promptcraft.write_media_prompts(run_dir, prompt_sets)
        reloaded = promptcraft.load_media_prompts(run_dir)
        assert reloaded["ck1_linkedin"].hero_prompt() == "a desk"
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
                    {"images": [{"slot": "hero", "prompt": "A fully crafted hero prompt for testing, ending properly."}]}
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
        assert first["ck1_linkedin"].hero_prompt() == "A fully crafted hero prompt for testing, ending properly."
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
        assert second["ck1_linkedin"].hero_prompt() == "A fully crafted hero prompt for testing, ending properly."
        assert len(fetcher.calls) == 1  # unchanged — no new network call
