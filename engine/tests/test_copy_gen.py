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
    build_copy_request,
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


def _request(asset_id="ck1_linkedin", attempt=1, destination="linkedin"):
    return build_copy_request(
        asset_id=asset_id, destination=destination, spin=_spin_result(), excerpt_refs=["hacker_news:1"],
        allowed_facts=[], negative_capabilities=["No physical products"],
        pricing_policy_line="prices-never-stated", hard_excludes={}, exemplar_pool_paths=["calibration/en/structural_corpus.md"],
        snapshot_id="test-snap", attempt=attempt,
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
