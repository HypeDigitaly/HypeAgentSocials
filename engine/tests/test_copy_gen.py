"""Tests for hypeagent.copy_gen — the TextModel protocol, both providers,
and the per-asset gate/repair orchestration (§6.9, §14.0, §14.3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from hypeagent.brand_truth import ClaimEntry, ClaimSnapshot
from hypeagent.collectors.base import FetchResponse, FixtureFetcher
from hypeagent.config_load import LlmConfig, OpenAICompatibleConfig
from hypeagent.copy_gen import (
    AI_DISCLOSURE_LINE,
    InteractiveFileProvider,
    OpenAICompatibleProvider,
    OpenRouterProvider,
    _build_openrouter_prompt,
    build_copy_request,
    humanness_prefilter,
    process_copy_asset,
)
from hypeagent.llm import LlmClient
from hypeagent.spin import SpinResult

DISCLOSURE = AI_DISCLOSURE_LINE


def _spin_result(value_only: bool = False) -> SpinResult:
    return SpinResult(
        cluster_key="ck1", topic="AI agents automating outbound sales", language="en",
        icp_id="icp-sme", icp_text="Small businesses wanting AI automation", pain="AI agents, automation",
        offer_id=None if value_only else "cap-chatbots",
        offer_text=None if value_only else "AI chatbots and assistants for businesses",
        mapping_distance="far" if value_only else "near", mapping_score=0.5, cta_id="cta-web",
        cta_class="content", cta_text="Learn more at example.com", band="Medium", value_only=value_only,
        rationale_line="Topic: x · ICP: y · Pain: z · Offer: none — value-only (far) · CTA: content · Band: Medium",
    )


def _snapshot(claims=None) -> ClaimSnapshot:
    return ClaimSnapshot(
        snapshot_id="test-snap", taken_at="2026-08-01", max_age_days=30,
        claims=claims or [], path=Path("config/snapshots/claim_ledger_snapshot_2026-08-01.yaml"),
    )


def _request(
    asset_id="ck1_linkedin", attempt=1, destination="linkedin", post_type="promotional",
    exemplar_pool_paths=None, language="en",
):
    return build_copy_request(
        asset_id=asset_id, destination=destination, spin=_spin_result(value_only=(post_type == "value_only")),
        excerpt_refs=["hacker_news:1"],
        allowed_facts=[], negative_capabilities=["No physical products"],
        pricing_policy_line="prices-never-stated", hard_excludes={},
        exemplar_pool_paths=(
            exemplar_pool_paths if exemplar_pool_paths is not None else ["calibration/en/structural_corpus.md"]
        ),
        snapshot_id="test-snap", attempt=attempt, post_type=post_type, language=language,
    )


class TestInteractiveFileProviderRoundTrip:
    def test_writes_request_and_holds_when_no_response(self, tmp_path):
        provider = InteractiveFileProvider(tmp_path)
        request = _request()
        result = provider.generate(request)
        assert result is None
        req_path = tmp_path / "copy_requests" / "ck1_linkedin.yaml"
        assert req_path.exists()
        doc = yaml.safe_load(req_path.read_text(encoding="utf-8"))
        assert doc["topic"] == "AI agents automating outbound sales"
        assert doc["snapshot_id"] == "test-snap"

    def test_does_not_rewrite_existing_request_file(self, tmp_path):
        provider = InteractiveFileProvider(tmp_path)
        request = _request()
        provider.generate(request)
        req_path = tmp_path / "copy_requests" / "ck1_linkedin.yaml"
        original_mtime = req_path.stat().st_mtime_ns
        provider.generate(request)
        assert req_path.stat().st_mtime_ns == original_mtime

    def test_consumes_response_once_written(self, tmp_path):
        provider = InteractiveFileProvider(tmp_path)
        request = _request()
        assert provider.generate(request) is None

        resp_dir = tmp_path / "copy_responses"
        resp_dir.mkdir(parents=True, exist_ok=True)
        (resp_dir / "ck1_linkedin.yaml").write_text(
            yaml.safe_dump({
                "headline": "AI agents are changing outbound sales",
                "caption": f"See how small businesses use AI chatbots. {DISCLOSURE}",
                "image_brief": "A calm office desk, no people, no product depiction.",
            }),
            encoding="utf-8",
        )
        result = provider.generate(request)
        assert result is not None
        assert result.provider == "interactive-file"
        assert "AI agents" in result.headline


class TestProcessCopyAssetGateFlow:
    def test_held_when_no_response_yet(self, tmp_path):
        provider = InteractiveFileProvider(tmp_path)
        status = process_copy_asset(provider=provider, request=_request(), snapshot=_snapshot())
        assert status.status == "held — awaiting operator copy"
        assert status.attempt == 1

    def test_gated_pass_on_clean_response(self, tmp_path):
        provider = InteractiveFileProvider(tmp_path)
        request = _request()
        provider.generate(request)
        (tmp_path / "copy_responses").mkdir(parents=True, exist_ok=True)
        (tmp_path / "copy_responses" / "ck1_linkedin.yaml").write_text(
            yaml.safe_dump({
                "headline": "AI agents are changing outbound sales",
                "caption": f"See how small businesses use AI chatbots. {DISCLOSURE}",
                "image_brief": "A calm office desk, no people.",
            }),
            encoding="utf-8",
        )
        status = process_copy_asset(provider=provider, request=request, snapshot=_snapshot())
        assert status.status == "gated-pass"
        assert status.headline

    def test_blocked_response_writes_regeneration_request_attempt_2(self, tmp_path):
        provider = InteractiveFileProvider(tmp_path)
        request = _request()
        provider.generate(request)
        (tmp_path / "copy_responses").mkdir(parents=True, exist_ok=True)
        (tmp_path / "copy_responses" / "ck1_linkedin.yaml").write_text(
            yaml.safe_dump({
                "headline": "The best AI chatbot ever",  # superlative -> blocked
                "caption": f"Guaranteed results. {DISCLOSURE}",
                "image_brief": "",
            }),
            encoding="utf-8",
        )
        status = process_copy_asset(provider=provider, request=request, snapshot=_snapshot(), max_attempts=2)
        assert status.status == "held — awaiting operator copy"
        assert status.attempt == 2
        attempt2_request = tmp_path / "copy_requests" / "ck1_linkedin.attempt2.yaml"
        assert attempt2_request.exists()
        doc = yaml.safe_load(attempt2_request.read_text(encoding="utf-8"))
        assert doc["prior_failing_spans"]

    def test_attempt_cap_enforced_after_max_attempts(self, tmp_path):
        provider = InteractiveFileProvider(tmp_path)
        request = _request()
        bad_response = {
            "headline": "The best AI chatbot ever",
            "caption": f"Guaranteed results. {DISCLOSURE}",
            "image_brief": "",
        }
        (tmp_path / "copy_responses").mkdir(parents=True, exist_ok=True)
        (tmp_path / "copy_responses" / "ck1_linkedin.yaml").write_text(yaml.safe_dump(bad_response), encoding="utf-8")
        (tmp_path / "copy_responses" / "ck1_linkedin.attempt2.yaml").write_text(yaml.safe_dump(bad_response), encoding="utf-8")

        status = process_copy_asset(provider=provider, request=request, snapshot=_snapshot(), max_attempts=2)
        assert status.status == "blocked — claim gate (repair budget exhausted)"
        assert status.attempt == 2
        assert status.failing_spans


class TestDisclosureFloor:
    def test_response_missing_disclosure_is_blocked(self, tmp_path):
        provider = InteractiveFileProvider(tmp_path)
        request = _request()
        provider.generate(request)
        (tmp_path / "copy_responses").mkdir(parents=True, exist_ok=True)
        (tmp_path / "copy_responses" / "ck1_linkedin.yaml").write_text(
            yaml.safe_dump({
                "headline": "AI agents are changing outbound sales",
                "caption": "See how small businesses use AI chatbots.",  # no disclosure line
                "image_brief": "A calm desk.",
            }),
            encoding="utf-8",
        )
        status = process_copy_asset(provider=provider, request=request, snapshot=_snapshot(), max_attempts=1)
        assert status.status.startswith("blocked")
        assert any("disclosure" in s.lower() for s in status.failing_spans)


class TestOpenAICompatibleProviderShapeOnly:
    def test_disabled_by_default_raises(self, tmp_path):
        config = OpenAICompatibleConfig(enabled=False, base_url="https://example.com/v1", model="test-model", key_path="", max_tokens=200)
        fetcher = FixtureFetcher(responses={})
        provider = OpenAICompatibleProvider(config, fetcher)
        with pytest.raises(Exception):
            provider.generate(_request())

    def test_request_shape_when_enabled(self, tmp_path):
        key_path = tmp_path / "openai.key"
        key_path.write_text("sk-test-key", encoding="utf-8")
        config = OpenAICompatibleConfig(
            enabled=True, base_url="https://api.example.com/v1", model="test-model",
            key_path=str(key_path), max_tokens=200,
        )
        response_payload = {
            "choices": [{"message": {"content": json.dumps({
                "headline": "AI agents are changing outbound sales",
                "caption": f"Copy body. {DISCLOSURE}",
                "image_brief": "A desk.",
            })}}]
        }
        fetcher = FixtureFetcher(responses={
            "api.example.com/v1/chat/completions": FetchResponse(
                status=200, headers={}, body=json.dumps(response_payload).encode("utf-8"), latency_ms=5,
            ),
        })
        provider = OpenAICompatibleProvider(config, fetcher)
        result = provider.generate(_request())
        assert result.provider == "openai-compatible-http"
        assert "AI agents" in result.headline

        assert len(fetcher.calls) == 1
        assert fetcher.calls[0] == "https://api.example.com/v1/chat/completions"
        sent_body = json.loads(fetcher.request_bodies[0])
        assert sent_body["model"] == "test-model"
        assert sent_body["max_tokens"] == 200
        assert "AI agents automating outbound sales" in sent_body["messages"][0]["content"]
        # The API key must never leak into the body sent — only the header.
        assert "sk-test-key" not in json.dumps(sent_body)

    def test_prior_failing_spans_included_in_prompt_on_repair(self, tmp_path):
        """W8-9 Q2 fix: the original prompt dropped prior_failing_spans (and
        negative_capabilities/hard_excludes) on the floor entirely."""
        key_path = tmp_path / "openai.key"
        key_path.write_text("sk-test-key", encoding="utf-8")
        config = OpenAICompatibleConfig(
            enabled=True, base_url="https://api.example.com/v1", model="test-model", key_path=str(key_path),
            max_tokens=200,
        )
        response_payload = {
            "choices": [{"message": {"content": json.dumps({
                "headline": "AI agents are changing outbound sales",
                "caption": f"Copy body. {DISCLOSURE}",
                "image_brief": "A desk.",
            })}}]
        }
        fetcher = FixtureFetcher(responses={
            "api.example.com/v1/chat/completions": FetchResponse(
                status=200, headers={}, body=json.dumps(response_payload).encode("utf-8"), latency_ms=5,
            ),
        })
        provider = OpenAICompatibleProvider(config, fetcher)
        request = _request(attempt=2)
        request = type(request)(**{**request.__dict__, "prior_failing_spans": ["caption: superlative 'best' — blocked"]})
        provider.generate(request)
        sent_body = json.loads(fetcher.request_bodies[0])
        prompt_text = sent_body["messages"][0]["content"]
        assert "superlative" in prompt_text
        assert "No physical products" in prompt_text  # negative_capabilities


ENDPOINT_KEY = "chat/completions"


def _ok_llm_response(payload: dict) -> FetchResponse:
    body = {
        "choices": [{"message": {"content": json.dumps(payload)}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50, "cost": 0.001},
    }
    return FetchResponse(status=200, headers={}, body=json.dumps(body).encode("utf-8"), latency_ms=10)


class _QueueFetcher:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []
        self.request_bodies = []

    def fetch(self, url, *, headers=None, method="GET", body=None):
        self.calls.append(url)
        self.request_bodies.append(body)
        return self._responses.pop(0)


def _llm_client(fetcher, tmp_path) -> LlmClient:
    from hypeagent.trace import TraceWriter

    tw = TraceWriter(tmp_path / "trace.jsonl", "run-1")
    return LlmClient(config=LlmConfig(enabled=True), fetcher=fetcher, api_key="sk-secret", trace=tw)


class TestOpenRouterProviderLinkedinSchema:
    def test_linkedin_result_has_no_slides(self, tmp_path):
        fetcher = FixtureFetcher(responses={
            ENDPOINT_KEY: _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "image_direction": "a desk"}
            )
        })
        client = _llm_client(fetcher, tmp_path)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={"platforms": {"linkedin": {"copy": {"form": "long_post"}}}},
            viral_playbook=None, brand_identity_one_liner="HypeDigitaly is a Czech AI agency.",
        )
        result = provider.generate(_request(destination="linkedin"))
        assert result.slides is None
        assert result.headline == "hi"
        assert result.image_brief == "a desk"


class TestOpenRouterProviderCarouselSchema:
    def test_instagram_result_carries_slides(self, tmp_path):
        slides = [
            {"role": "cover", "title": "Cover", "body": ""},
            {"role": "body", "title": "Step 1", "body": "Do the thing."},
            {"role": "end_card", "title": "Follow us", "body": ""},
        ]
        fetcher = FixtureFetcher(responses={
            ENDPOINT_KEY: _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "slides": slides, "image_direction": "a desk"}
            )
        })
        client = _llm_client(fetcher, tmp_path)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={"platforms": {"instagram_feed": {"copy": {"carousel": {"slides": [6, 10]}}}}},
            viral_playbook=None, brand_identity_one_liner="HypeDigitaly is a Czech AI agency.",
        )
        result = provider.generate(_request(asset_id="ck1_instagram_feed", destination="instagram_feed"))
        assert result.slides == [{**s, "component": ""} for s in slides]
        sent_body = json.loads(fetcher.request_bodies[0])
        assert "carousel" in sent_body["messages"][1]["content"].lower()


class TestCarouselCompleteness:
    """W8-9: a deficient carousel (< MIN_CAROUSEL_SLIDES slides, or no
    role='end_card') gets ONE corrective retry mentioning the deficiency,
    then is accepted with a trace note regardless — never a hard fail."""

    def _slides(self, n: int, *, with_end_card: bool = True) -> list[dict]:
        slides = [{"role": "cover", "title": "Cover", "body": ""}]
        slides += [{"role": "body", "title": f"Step {i}", "body": f"Do thing {i}."} for i in range(1, n - 1)]
        if with_end_card:
            slides.append({"role": "end_card", "title": "Follow us", "body": ""})
        else:
            slides.append({"role": "body", "title": "More", "body": "more content"})
        return slides[:n]

    def test_deficient_slide_count_retries_and_succeeds(self, tmp_path):
        from hypeagent.trace import TraceWriter

        deficient = self._slides(3)  # < 6 slides
        fixed = self._slides(6)
        fetcher = _QueueFetcher([
            _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "slides": deficient, "image_direction": "a desk"}
            ),
            _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "slides": fixed, "image_direction": "a desk"}
            ),
        ])
        tw = TraceWriter(tmp_path / "trace.jsonl", "run-1")
        client = LlmClient(config=LlmConfig(enabled=True), fetcher=fetcher, api_key="sk-secret", trace=tw)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None,
            brand_identity_one_liner="HypeDigitaly is a Czech AI agency.", trace=tw, stage="copy",
        )
        result = provider.generate(_request(asset_id="ck1_instagram_feed", destination="instagram_feed"))
        tw.close()
        assert len(result.slides) == 6
        assert any(s["role"] == "end_card" for s in result.slides)
        assert len(fetcher.request_bodies) == 2
        second_user_text = json.loads(fetcher.request_bodies[1])["messages"][1]["content"]
        assert "deficient" in second_user_text.lower()

    def test_deficiency_persists_after_retry_is_accepted_with_trace_note(self, tmp_path):
        from hypeagent.trace import TraceWriter

        deficient = self._slides(3)
        fetcher = FixtureFetcher(responses={
            ENDPOINT_KEY: _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "slides": deficient, "image_direction": "a desk"}
            )
        })
        trace_path = tmp_path / "trace.jsonl"
        tw = TraceWriter(trace_path, "run-1")
        client = LlmClient(config=LlmConfig(enabled=True), fetcher=fetcher, api_key="sk-secret", trace=tw)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None,
            brand_identity_one_liner="HypeDigitaly is a Czech AI agency.", trace=tw, stage="copy",
        )
        result = provider.generate(_request(asset_id="ck1_instagram_feed", destination="instagram_feed"))
        tw.close()
        # Never a hard fail -- the deficient result still ships.
        assert len(result.slides) == 3
        assert len(fetcher.request_bodies) == 2  # the one corrective retry happened

        events = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        decisions = [e["detail"]["decision"] for e in events if e["event"] == "decision"]
        assert any("persisted after 1 corrective retry" in d for d in decisions)

    def test_missing_end_card_is_a_deficiency(self, tmp_path):
        no_end_card = self._slides(6, with_end_card=False)
        fixed = self._slides(6, with_end_card=True)
        fetcher = _QueueFetcher([
            _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "slides": no_end_card, "image_direction": "a desk"}
            ),
            _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "slides": fixed, "image_direction": "a desk"}
            ),
        ])
        client = _llm_client(fetcher, tmp_path)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None,
            brand_identity_one_liner="HypeDigitaly is a Czech AI agency.",
        )
        result = provider.generate(_request(asset_id="ck1_instagram_feed", destination="instagram_feed"))
        assert any(s["role"] == "end_card" for s in result.slides)
        assert len(fetcher.request_bodies) == 2

    def test_linkedin_destination_is_never_checked_for_slide_completeness(self, tmp_path):
        fetcher = FixtureFetcher(responses={
            ENDPOINT_KEY: _ok_llm_response({"headline": "hi", "caption": f"body {DISCLOSURE}", "image_direction": "a desk"})
        })
        client = _llm_client(fetcher, tmp_path)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None,
            brand_identity_one_liner="HypeDigitaly is a Czech AI agency.",
        )
        result = provider.generate(_request(destination="linkedin"))
        assert result.slides is None
        assert len(fetcher.request_bodies) == 1  # no completeness retry for a non-carousel destination


class TestOpenRouterGateRepairCarriesFailingSpans:
    def test_second_request_body_carries_prior_failing_spans(self, tmp_path):
        bad_payload = {"headline": "The best AI chatbot ever", "caption": f"Guaranteed results. {DISCLOSURE}", "image_direction": ""}
        good_payload = {"headline": "AI agents are changing outbound sales", "caption": f"Clean copy. {DISCLOSURE}", "image_direction": "a desk"}
        fetcher = _QueueFetcher([_ok_llm_response(bad_payload), _ok_llm_response(good_payload)])
        client = _llm_client(fetcher, tmp_path)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None,
            brand_identity_one_liner="HypeDigitaly is a Czech AI agency.",
        )
        status = process_copy_asset(
            provider=provider, request=_request(), snapshot=_snapshot(), max_attempts=2, run_dir=tmp_path,
        )
        assert status.status == "gated-pass"
        assert status.attempt == 2
        assert len(fetcher.request_bodies) == 2
        second_body = json.loads(fetcher.request_bodies[1])
        second_user_text = second_body["messages"][1]["content"]
        assert "superlative" in second_user_text.lower() or "guarantee" in second_user_text.lower()
        # Own-authored LLM copy is persisted for the process summary/provenance.
        assert (tmp_path / "copy_requests" / "ck1_linkedin.yaml").exists()
        assert (tmp_path / "copy_responses" / "ck1_linkedin.attempt2.yaml").exists()


class TestCopyProviderFallbackWhenLlmDisabled:
    def test_stage_falls_back_to_interactive_file_when_llm_disabled(self, tmp_path):
        from hypeagent import stages

        ctx = stages.RunContext(run_id="x", config_dir=tmp_path / "config", logs_dir=tmp_path / "logs")
        from hypeagent.config_load import GenerationConfig, MappingDistanceBands, MediaConfig

        ctx.generation = GenerationConfig(
            destinations=["linkedin"], copy_provider="openrouter", repair_budget=2,
            mapping_distance=MappingDistanceBands(), exemplar_pool=[],
            openai_compatible=OpenAICompatibleConfig(), media=MediaConfig(),
            llm=LlmConfig(enabled=False),
        )
        provider = stages._build_copy_provider(ctx, tmp_path / "logs" / "runs" / "x")
        assert isinstance(provider, InteractiveFileProvider)


# ---------------------------------------------------------------------------
# W8-10 Phase 1 — the copywriter voice overhaul.
# ---------------------------------------------------------------------------


class TestSystemPromptVoiceRules:
    def test_contains_voice_rules_and_not_the_banned_example_phrase(self):
        system, _user, _schema = _build_openrouter_prompt(
            _request(), style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand X",
        )
        assert "VOICE RULES" in system
        assert "first-person singular" in system.lower()
        # The old prompt HANDED the model this exact hedge phrase (copywriter
        # audit finding #1) -- it must never appear in the new one.
        assert "creators are reporting" not in system.lower()
        # The old anxiety clause made the model narrate its own compliance
        # reasoning into the copy (copywriter audit finding #3).
        assert "will be caught by a claim gate and sent back" not in system.lower()

    def test_contains_the_countable_rule_numbers(self):
        system, _user, _schema = _build_openrouter_prompt(
            _request(), style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand X",
        )
        for rule_number in ("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.", "12."):
            assert rule_number in system


class TestExemplarInjection:
    def test_exemplar_file_content_reaches_the_prompt(self, tmp_path):
        exemplar_path = tmp_path / "my_exemplar.md"
        exemplar_path.write_text("A totally distinctive exemplar sentence for the rhythm test.", encoding="utf-8")
        fetcher = FixtureFetcher(responses={
            ENDPOINT_KEY: _ok_llm_response({"headline": "hi", "caption": f"body {DISCLOSURE}", "image_direction": "a desk"})
        })
        client = _llm_client(fetcher, tmp_path)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand X",
            exemplar_base_dir=tmp_path,
        )
        request = _request(exemplar_pool_paths=["my_exemplar.md"])
        provider.generate(request)
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "A totally distinctive exemplar sentence for the rhythm test." in user_text
        assert "do NOT reuse its exact phrases" in user_text

    def test_missing_exemplar_file_is_skipped_with_a_note_not_an_error(self, tmp_path):
        fetcher = FixtureFetcher(responses={
            ENDPOINT_KEY: _ok_llm_response({"headline": "hi", "caption": f"body {DISCLOSURE}", "image_direction": "a desk"})
        })
        client = _llm_client(fetcher, tmp_path)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand X",
            exemplar_base_dir=tmp_path,
        )
        request = _request(exemplar_pool_paths=["does_not_exist.md"])
        result = provider.generate(request)
        assert result is not None
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "not found/unreadable, skipped" in user_text

    def test_resolved_excerpts_are_injected_up_to_the_cap(self, tmp_path):
        fetcher = FixtureFetcher(responses={
            ENDPOINT_KEY: _ok_llm_response({"headline": "hi", "caption": f"body {DISCLOSURE}", "image_direction": "a desk"})
        })
        client = _llm_client(fetcher, tmp_path)
        excerpts = {"hn:1": "First excerpt text.", "hn:2": "Second excerpt text.", "hn:3": "Third.", "hn:4": "Fourth (never resolved)."}
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand X",
            excerpt_resolver=lambda key: excerpts.get(key),
        )
        request = build_copy_request(
            asset_id="ck1_linkedin", destination="linkedin", spin=_spin_result(),
            excerpt_refs=["hn:1", "hn:2", "hn:3", "hn:4"], allowed_facts=[],
            negative_capabilities=[], pricing_policy_line="x", hard_excludes={},
            exemplar_pool_paths=[], snapshot_id="s",
        )
        provider.generate(request)
        sent_body = json.loads(fetcher.request_bodies[0])
        user_text = sent_body["messages"][1]["content"]
        assert "First excerpt text." in user_text
        assert "Second excerpt text." in user_text
        assert "Third." in user_text
        assert "Fourth (never resolved)." not in user_text  # cap of 3


class TestLanguageField:
    def test_defaults_to_en(self):
        request = _request()
        assert request.language == "en"
        assert request.to_yaml_dict()["language"] == "en"

    def test_carries_through_build_copy_request(self):
        request = _request(language="cs")
        assert request.language == "cs"

    def test_output_language_line_reaches_the_system_prompt(self):
        system, _user, _schema = _build_openrouter_prompt(
            _request(language="cs"), style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand X",
        )
        assert "Output language: cs" in system


class TestValueOnlyPromptBranch:
    def test_value_only_drops_brand_identity_from_the_system_prompt(self):
        request = _request(post_type="value_only")
        system, user, _schema = _build_openrouter_prompt(
            request, style_guide={}, viral_playbook=None, brand_identity_one_liner="HypeDigitaly is a Czech AI agency.",
        )
        assert "HypeDigitaly is a Czech AI agency." not in system
        assert "do not mention the brand" in user.lower()
        assert "@hypedigitaly" in user.lower()

    def test_promotional_keeps_brand_identity_in_the_system_prompt(self):
        request = _request(post_type="promotional")
        system, _user, _schema = _build_openrouter_prompt(
            request, style_guide={}, viral_playbook=None, brand_identity_one_liner="HypeDigitaly is a Czech AI agency.",
        )
        assert "HypeDigitaly is a Czech AI agency." in system

    def test_playbook_section_placed_first_for_value_only(self):
        request = _request(post_type="value_only")
        _system, user, _schema = _build_openrouter_prompt(
            request, style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand X",
        )
        assert user.index("This run's viral playbook") < user.index("Destination:")

    def test_playbook_section_placed_after_housekeeping_for_promotional(self):
        request = _request(post_type="promotional")
        _system, user, _schema = _build_openrouter_prompt(
            request, style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand X",
        )
        assert user.index("Destination:") < user.index("This run's viral playbook")

    def test_playbook_post_type_requires_a_comment_keyword_ask(self):
        request = _request(post_type="playbook")
        _system, user, _schema = _build_openrouter_prompt(
            request, style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand X",
        )
        assert "comment-keyword" in user.lower()


class TestNumberedPromiseHardGate:
    """W8-10: a headline/cover promising "N <noun>" with fewer than N
    content slides delivered HARD-fails to held after one corrective
    retry -- distinct from the generic <6-slide shortfall, which still
    accepts-with-note (``TestCarouselCompleteness`` above)."""

    def _slides(self, content_count: int, *, cover_title: str = "6 Prompts You Need") -> list[dict]:
        slides = [{"role": "cover", "title": cover_title, "body": ""}]
        slides += [{"role": "body", "title": f"Step {i}", "body": f"Do thing {i}."} for i in range(1, content_count + 1)]
        slides.append({"role": "end_card", "title": "Follow us", "body": ""})
        return slides

    def test_promise_unmet_after_retry_hard_fails_to_none(self, tmp_path):
        from hypeagent.trace import TraceWriter

        # FixtureFetcher returns the SAME deficient response for both the
        # initial call and the corrective retry -- modelling "the promise
        # is still broken after the one retry".
        deficient = self._slides(2)  # promises 6, delivers 2
        fetcher = FixtureFetcher(responses={
            ENDPOINT_KEY: _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "slides": deficient, "image_direction": "a desk"}
            )
        })
        tw = TraceWriter(tmp_path / "trace.jsonl", "run-1")
        client = LlmClient(config=LlmConfig(enabled=True), fetcher=fetcher, api_key="sk-secret", trace=tw)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand",
            trace=tw, stage="copy",
        )
        result = provider.generate(_request(asset_id="ck1_instagram_feed", destination="instagram_feed"))
        tw.close()
        assert result is None

    def test_promise_met_after_retry_ships_normally(self, tmp_path):
        deficient = self._slides(2)
        fixed = self._slides(6)
        fetcher = _QueueFetcher([
            _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "slides": deficient, "image_direction": "a desk"}
            ),
            _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "slides": fixed, "image_direction": "a desk"}
            ),
        ])
        client = _llm_client(fetcher, tmp_path)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand",
        )
        result = provider.generate(_request(asset_id="ck1_instagram_feed", destination="instagram_feed"))
        assert result is not None
        assert len(result.slides) == 8  # cover + 6 content + end_card

    def test_no_numbered_promise_generic_shortfall_still_accepts_with_note(self, tmp_path):
        # Headline/cover carry no numbered promise at all -- the generic
        # <6-slide shortfall path (accept-with-note) is unaffected.
        deficient = [
            {"role": "cover", "title": "A Cover With No Number", "body": ""},
            {"role": "body", "title": "Step 1", "body": "Do it."},
            {"role": "end_card", "title": "Follow us", "body": ""},
        ]
        fetcher = FixtureFetcher(responses={
            ENDPOINT_KEY: _ok_llm_response(
                {"headline": "hi", "caption": f"body {DISCLOSURE}", "slides": deficient, "image_direction": "a desk"}
            )
        })
        client = _llm_client(fetcher, tmp_path)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand",
        )
        result = provider.generate(_request(asset_id="ck1_instagram_feed", destination="instagram_feed"))
        assert result is not None  # never a hard fail for a non-numbered-promise shortfall
        assert len(result.slides) == 3


# ---------------------------------------------------------------------------
# W8-10 Phase 2 — the humanness critic (N-F).
# ---------------------------------------------------------------------------


class TestHumannessPrefilter:
    def test_detects_slop_tell_phrases(self):
        findings = humanness_prefilter("We're actually seeing creators are reporting huge wins in the space.")
        assert any("slop-tell" in f for f in findings)

    def test_detects_em_dash_density(self):
        text = "This is fine. " * 40 + "It works — but also — and this — too."
        findings = humanness_prefilter(text)
        assert any("em-dash density" in f for f in findings)

    def test_detects_tricolon_pattern(self):
        findings = humanness_prefilter("We tested speed, accuracy, and cost this week.")
        assert any("tricolon" in f for f in findings)

    def test_detects_repeated_antithesis(self):
        text = (
            "It isn't a workflow, it's a system. It isn't magic, it's practice. It isn't hype, it's math."
        )
        findings = humanness_prefilter(text)
        assert any("antithesis" in f for f in findings)

    def test_clean_short_text_has_no_findings(self):
        findings = humanness_prefilter("I wrote this on my phone. It works. Try it today.")
        assert findings == []

    def test_empty_text_has_no_findings(self):
        assert humanness_prefilter("") == []


class TestHumannessCriticFlow:
    def test_rewrite_that_passes_the_gate_is_used(self, tmp_path):
        from hypeagent.trace import TraceWriter

        copy_payload = {"headline": "hi", "caption": f"body actually {DISCLOSURE}", "image_direction": "a desk"}
        critic_payload = {"headline": "A cleaner line", "caption": f"Cleaner body. {DISCLOSURE}", "image_direction": "a desk"}
        fetcher = _QueueFetcher([_ok_llm_response(copy_payload), _ok_llm_response(critic_payload)])
        tw = TraceWriter(tmp_path / "trace.jsonl", "run-1")
        client = LlmClient(config=LlmConfig(enabled=True), fetcher=fetcher, api_key="sk-secret", trace=tw)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None,
            brand_identity_one_liner="Brand", trace=tw, stage="copy",
        )
        status = process_copy_asset(
            provider=provider, request=_request(), snapshot=_snapshot(), max_attempts=2,
            trace=tw, stage="copy", run_dir=tmp_path, llm_client=client, humanness_critic_enabled=True,
        )
        tw.close()
        assert status.status == "gated-pass"
        assert status.headline == "A cleaner line"
        assert status.caption == f"Cleaner body. {DISCLOSURE}"
        assert len(fetcher.request_bodies) == 2

    def test_rewrite_that_fails_the_gate_keeps_the_original(self, tmp_path):
        from hypeagent.trace import TraceWriter

        copy_payload = {"headline": "hi", "caption": f"body {DISCLOSURE}", "image_direction": "a desk"}
        # The critic's own rewrite introduces a superlative -- must never ship.
        critic_payload = {"headline": "The best AI chatbot ever", "caption": f"Guaranteed results. {DISCLOSURE}", "image_direction": "a desk"}
        fetcher = _QueueFetcher([_ok_llm_response(copy_payload), _ok_llm_response(critic_payload)])
        tw = TraceWriter(tmp_path / "trace.jsonl", "run-1")
        client = LlmClient(config=LlmConfig(enabled=True), fetcher=fetcher, api_key="sk-secret", trace=tw)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None,
            brand_identity_one_liner="Brand", trace=tw, stage="copy",
        )
        status = process_copy_asset(
            provider=provider, request=_request(), snapshot=_snapshot(), max_attempts=2,
            trace=tw, stage="copy", run_dir=tmp_path, llm_client=client, humanness_critic_enabled=True,
        )
        tw.close()
        assert status.status == "gated-pass"
        assert status.headline == "hi"  # original, gated copy kept
        assert len(fetcher.request_bodies) == 2

    def test_disabled_config_skips_the_critic_call_entirely(self, tmp_path):
        copy_payload = {"headline": "hi", "caption": f"body actually {DISCLOSURE}", "image_direction": "a desk"}
        fetcher = FixtureFetcher(responses={ENDPOINT_KEY: _ok_llm_response(copy_payload)})
        client = _llm_client(fetcher, tmp_path)
        provider = OpenRouterProvider(
            llm_client=client, style_guide={}, viral_playbook=None, brand_identity_one_liner="Brand",
        )
        status = process_copy_asset(
            provider=provider, request=_request(), snapshot=_snapshot(), max_attempts=2,
            run_dir=tmp_path, llm_client=client, humanness_critic_enabled=False,
        )
        assert status.status == "gated-pass"
        assert status.headline == "hi"
        assert len(fetcher.request_bodies) == 1  # no critic call made

    def test_no_llm_client_is_a_no_op(self, tmp_path):
        provider = InteractiveFileProvider(tmp_path)
        request = _request()
        provider.generate(request)
        (tmp_path / "copy_responses").mkdir(parents=True, exist_ok=True)
        (tmp_path / "copy_responses" / "ck1_linkedin.yaml").write_text(
            yaml.safe_dump({
                "headline": "AI agents are changing outbound sales",
                "caption": f"See how small businesses use AI chatbots. {DISCLOSURE}",
                "image_brief": "A calm office desk, no people.",
            }),
            encoding="utf-8",
        )
        status = process_copy_asset(provider=provider, request=request, snapshot=_snapshot())
        assert status.status == "gated-pass"  # unaffected -- llm_client defaults to None
