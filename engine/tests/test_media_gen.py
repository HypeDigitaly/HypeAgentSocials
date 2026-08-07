"""Tests for hypeagent.media_gen — Kie.ai image generation, the write-ahead
spend ledger, cost gate, async job lifecycle, per-slide carousel submission,
and the N-E vision-QA gate (GOAL_ROADMAP.md M4/W8-9 Q4; ARCHITECTURE_PLAN.md
§4.6-§4.7, §5.2-§5.7, §8.5, §8.11, §8.13).

Fully offline: the paid path is mocked via ``QueuedFetcher`` (a
``Fetcher`` double that returns queued responses per matched URL substring,
so a single test can script a poll sequence like waiting -> waiting ->
success); the same instance doubles as the OpenRouter transport for
vision-QA calls (a "chat/completions" queue alongside the Kie ones)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml

from hypeagent import media_gen
from hypeagent.collectors.base import FetchError, FetchResponse, Fetcher
from hypeagent.config_load import LlmConfig, MediaConfig
from hypeagent.copy_gen import AssetCopyStatus
from hypeagent.llm import LlmClient
from hypeagent.store import MediaIntentAlreadyExists, Store
from hypeagent.trace import TraceWriter

CREATE_TASK_URL = "https://api.kie.ai/api/v1/jobs/createTask"
RECORD_INFO_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"
CREDIT_URL = "https://api.kie.ai/api/v1/chat/credit"
RESULT_IMAGE_URL = "https://tempfile.example.com/generated/img.png"

_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64  # valid magic bytes; body content is irrelevant to our checks


@dataclass
class QueuedFetcher:
    """A ``Fetcher`` double that pops one queued response per call for a
    matched URL substring — the last item in a queue repeats indefinitely,
    which is what a "still pending" poll-timeout scenario needs. Also
    serves as the OpenRouter transport for vision-QA calls (a
    "chat/completions" queue) so one fetcher instance can back both
    KieClient and LlmClient in the same test."""

    responses: dict[str, list[FetchResponse | Exception]]
    calls: list[str] = field(default_factory=list)
    request_bodies: list[bytes | None] = field(default_factory=list)

    def fetch(self, url: str, *, headers=None, method: str = "GET", body: bytes | None = None) -> FetchResponse:
        self.calls.append(url)
        self.request_bodies.append(body)
        for key, queue in self.responses.items():
            if key in url:
                item = queue.pop(0) if len(queue) > 1 else queue[0]
                if isinstance(item, Exception):
                    raise item
                return item
        raise FetchError(f"QueuedFetcher: no fixture registered for {url}")


def _json_response(payload: dict) -> FetchResponse:
    return FetchResponse(status=200, headers={}, body=json.dumps(payload).encode("utf-8"), latency_ms=1)


def _create_task_ok(task_id: str = "task_test_1") -> FetchResponse:
    return _json_response({"code": 200, "msg": "success", "data": {"taskId": task_id}})


def _record_info_waiting(task_id: str = "task_test_1") -> FetchResponse:
    return _json_response(
        {"code": 200, "msg": "success", "data": {
            "taskId": task_id, "model": "google/nano-banana", "state": "waiting",
            "resultJson": None, "failCode": "", "failMsg": "", "creditsConsumed": None,
        }}
    )


def _record_info_success(task_id: str = "task_test_1", *, result_url: str = RESULT_IMAGE_URL, model: str | None = "google/nano-banana", credits: float = 4.0) -> FetchResponse:
    return _json_response(
        {"code": 200, "msg": "success", "data": {
            "taskId": task_id, "model": model, "state": "success",
            "resultJson": json.dumps({"resultUrls": [result_url]}),
            "failCode": "", "failMsg": "", "creditsConsumed": credits,
        }}
    )


def _record_info_fail(task_id: str = "task_test_1", *, fail_msg: str = "content policy violation") -> FetchResponse:
    return _json_response(
        {"code": 200, "msg": "success", "data": {
            "taskId": task_id, "model": None, "state": "fail", "resultJson": "{}",
            "failCode": "content_policy", "failMsg": fail_msg, "creditsConsumed": 0,
        }}
    )


def _credit_balance(value: float) -> FetchResponse:
    return _json_response({"code": 200, "msg": "success", "data": value})


def _image_response(body: bytes = _PNG_BYTES) -> FetchResponse:
    return FetchResponse(status=200, headers={}, body=body, latency_ms=1)


def _qa_response(*, text_matches: bool, archetype_ok: bool, mismatches: list[str] | None = None, notes: str = "") -> FetchResponse:
    """An OpenRouter chat-completions response carrying N-E's JSON verdict
    shape (same envelope ``hypeagent.llm``'s own tests use)."""
    content = json.dumps(
        {"text_matches": text_matches, "archetype_ok": archetype_ok, "mismatches": mismatches or [], "notes": notes}
    )
    payload = {
        "id": "gen-qa-1",
        "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70, "cost": 0.001},
    }
    return FetchResponse(status=200, headers={}, body=json.dumps(payload).encode("utf-8"), latency_ms=5)


def _registry(**overrides) -> media_gen.ModelRegistry:
    draft_route = media_gen.ModelRoute(
        route_id="img-draft-nano-banana", tier="draft", display="Nano Banana",
        model_string="google/nano-banana", price_credits=4.0, price_usd=0.02,
    )
    standard_route = media_gen.ModelRoute(
        route_id="img-standard-nano-banana-pro", tier="standard", display="Nano Banana 2",
        model_string="nano-banana-2", price_credits=24.0, price_usd=0.12,
    )
    defaults = dict(
        registry_version=1, price_snapshot_date="2026-08-07", credit_usd=0.005,
        create_task_url=CREATE_TASK_URL, record_info_url=RECORD_INFO_URL,
        routes={draft_route.route_id: draft_route, standard_route.route_id: standard_route},
        draft_route_id=draft_route.route_id, fallback_draft_route_id=draft_route.route_id,
        tier_ceiling="draft",
        people_free_composition=True, policy_a_no_product_depiction=True,
    )
    defaults.update(overrides)
    return media_gen.ModelRegistry(**defaults)


def _media_config(**overrides) -> MediaConfig:
    defaults = dict(
        dry_run=False, per_run_usd_cap=1.0, per_run_count_cap=4, per_day_usd_cap=1.0,
        poll_interval_seconds=0.0, poll_timeout_seconds=0.05, resolution_window_days=14,
        aspect_ratio="1:1", output_format="png", key_path="", unexplained_spend_threshold=0.20,
        route_by_class={"hero": "img-draft-nano-banana", "slide": "img-draft-nano-banana"},
        aspect_ratio_by_destination={"linkedin": "1:1", "instagram_feed": "4:5"},
    )
    defaults.update(overrides)
    return MediaConfig(**defaults)


def _copy_status(
    asset_id="ck1_linkedin", cluster_key="ck1", destination="linkedin", status="gated-pass",
    image_brief="A calm office desk, no people.", headline="AI agents are changing outbound sales",
) -> AssetCopyStatus:
    return AssetCopyStatus(
        asset_id=asset_id, cluster_key=cluster_key, destination=destination, status=status,
        attempt=1, image_brief=image_brief if status == "gated-pass" else None,
        headline=headline if status == "gated-pass" else None,
    )


def _carousel_copy_status(
    asset_id="ck1_instagram_feed", cluster_key="ck1", destination="instagram_feed", n_slides=3
) -> AssetCopyStatus:
    slides = [{"title": f"Slide {i} title", "body": f"Slide {i} body text.", "role": "body"} for i in range(1, n_slides + 1)]
    return AssetCopyStatus(
        asset_id=asset_id, cluster_key=cluster_key, destination=destination, status="gated-pass",
        attempt=1, image_brief="A carousel about AI agents.", headline="AI agents headline", slides=slides,
    )


def _crafted_carousel(asset_id: str, n_slides: int, *, archetype="editorial", register="editorial"):
    from hypeagent import promptcraft

    images = [promptcraft.CraftedImage(slot=f"slide_{i:02d}", prompt=f"Prompt for slide {i}") for i in range(1, n_slides + 1)]
    return promptcraft.CraftedPromptSet(asset_id=asset_id, images=images, archetype=archetype, register=register)


def _crafted_hero(asset_id: str, prompt: str = "The N-D crafted prompt, verbatim text and all. @hypedigitaly.", *, archetype="editorial", register="editorial"):
    from hypeagent import promptcraft

    return promptcraft.CraftedPromptSet(
        asset_id=asset_id, images=[promptcraft.CraftedImage(slot="hero", prompt=prompt)],
        archetype=archetype, register=register,
    )


def _store(tmp_path: Path) -> Store:
    return Store.open(tmp_path / "logs", tmp_path / "secrets")


def _trace(tmp_path: Path, name: str = "trace.jsonl") -> TraceWriter:
    return TraceWriter(tmp_path / name, "run1")


def _llm_config(**overrides) -> LlmConfig:
    base = dict(enabled=True, per_run_usd_cap=1.0, per_run_call_cap=20, usd_per_1m_input_tokens=2.0, usd_per_1m_output_tokens=10.0)
    base.update(overrides)
    return LlmConfig(**base)


def _llm_client(fetcher: Fetcher, trace: TraceWriter, **overrides) -> LlmClient:
    return LlmClient(config=_llm_config(**overrides), fetcher=fetcher, api_key="sk-test", trace=trace, stage="media")


def _generator(
    tmp_path: Path, *, store: Store, trace: TraceWriter, fetcher: Fetcher, registry=None, media_config=None,
    api_key="test-kie-key-value", sleep_calls: list | None = None, llm_client: LlmClient | None = None,
) -> media_gen.MediaGenerator:
    registry = registry or _registry()
    media_config = media_config or _media_config()
    kie_client = media_gen.KieClient(fetcher=fetcher, api_key=api_key, trace=trace, registry=registry, stage="media")
    sleep_fn = (lambda s: sleep_calls.append(s)) if sleep_calls is not None else (lambda s: None)
    return media_gen.MediaGenerator(
        store=store, trace=trace, registry=registry, media_config=media_config, kie_client=kie_client,
        theme="hypedigitaly", run_id="run1", run_date="2026-08-10", pack_media_dir=tmp_path / "pack" / "media",
        sleep_fn=sleep_fn, llm_client=llm_client,
    )


# ---------------------------------------------------------------------------
# Prompt composition + cost gate + provenance inference (pure functions).
# ---------------------------------------------------------------------------


class TestPromptComposition:
    def test_w8_9_constraint_set_is_exactly_the_three_survivors(self):
        registry = _registry()
        prompt = media_gen.compose_prompt("A busy SaaS dashboard with a person at a desk.", registry)
        assert "no identifiable real individuals or celebrity likenesses" in prompt
        assert "no NSFW or shocking content" in prompt
        assert "screenshot of HypeDigitaly's or HypeLead's own product UI" in prompt
        assert "A busy SaaS dashboard with a person at a desk." in prompt
        # The OLD W8-1a set is gone entirely -- text/logos/generic people/
        # generic software UI are now allowed, not filtered.
        assert "no people" not in prompt
        assert "no text" not in prompt
        assert "no logos" not in prompt
        assert "no product screenshots" not in prompt

    def test_crafted_prompts_are_never_double_appended(self, tmp_path):
        """A crafted prompt is sent to Kie VERBATIM -- ``compose_prompt`` is
        never run over it (module docstring: "no double-appending")."""
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_x")],
                    "recordInfo": [_record_info_success("task_x")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(76.0)],
                    RESULT_IMAGE_URL: [_image_response()],
                }
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher)
            plans = media_gen.plan_media_assets([_copy_status()], crafted_prompts={"ck1_linkedin": _crafted_hero("ck1_linkedin", "Exact crafted prompt text.")})
            generator.process(plans)
            trace.close()
            body = json.loads(next(b for url, b in zip(fetcher.calls, fetcher.request_bodies) if "createTask" in url))
            assert body["input"]["prompt"] == "Exact crafted prompt text."
            assert "Constraints:" not in body["input"]["prompt"]
        finally:
            store.close()


class TestTierOrderPolicy:
    def test_route_within_ceiling_resolves(self):
        registry = _registry(tier_ceiling="standard")
        route = registry.resolve_route("img-standard-nano-banana-pro")
        assert route.route_id == "img-standard-nano-banana-pro"

    def test_route_above_ceiling_raises_policy_stop(self):
        registry = _registry(tier_ceiling="draft")
        with pytest.raises(media_gen.MediaGenerationError, match="policy-stop"):
            registry.resolve_route("img-standard-nano-banana-pro")

    def test_unregistered_route_id_raises(self):
        registry = _registry()
        with pytest.raises(media_gen.MediaGenerationError):
            registry.resolve_route("does-not-exist")

    def test_process_raises_only_when_a_plan_of_that_class_is_actually_used(self, tmp_path):
        """A theme that points ``slide`` at a too-high tier never trips the
        policy-stop for a run that only ever emits hero plans this run."""
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_hero_only")],
                    "recordInfo": [_record_info_success("task_hero_only")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                    RESULT_IMAGE_URL: [_image_response()],
                }
            )
            registry = _registry(tier_ceiling="draft")
            media_config = _media_config(
                route_by_class={"hero": "img-draft-nano-banana", "slide": "img-standard-nano-banana-pro"}
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, registry=registry, media_config=media_config)
            plans = media_gen.plan_media_assets([_copy_status()])  # hero-only, no carousel
            result = generator.process(plans)
            trace.close()
            assert result.statuses[0].status == "generated"
        finally:
            store.close()


class TestCostGate:
    def test_count_cap_and_budget_cap_are_distinct_statuses(self):
        count_capped = media_gen.check_caps(
            count_so_far=2, usd_so_far_run=0.0, usd_so_far_day=0.0, expected_cost_usd=0.02,
            count_cap=2, run_usd_cap=1.0, day_usd_cap=1.0,
        )
        assert count_capped.allowed is False
        assert count_capped.status == media_gen.STATUS_COUNT_CAPPED

        budget_capped = media_gen.check_caps(
            count_so_far=0, usd_so_far_run=0.19, usd_so_far_day=0.0, expected_cost_usd=0.02,
            count_cap=10, run_usd_cap=0.20, day_usd_cap=1.0,
        )
        assert budget_capped.allowed is False
        assert budget_capped.status == media_gen.STATUS_BUDGET_CAPPED
        assert count_capped.status != budget_capped.status

    def test_day_cap_also_trips_budget_capped(self):
        decision = media_gen.check_caps(
            count_so_far=0, usd_so_far_run=0.0, usd_so_far_day=0.39, expected_cost_usd=0.02,
            count_cap=10, run_usd_cap=1.0, day_usd_cap=0.40,
        )
        assert decision.allowed is False
        assert decision.status == media_gen.STATUS_BUDGET_CAPPED

    def test_allowed_when_under_every_cap(self):
        decision = media_gen.check_caps(
            count_so_far=0, usd_so_far_run=0.0, usd_so_far_day=0.0, expected_cost_usd=0.02,
            count_cap=4, run_usd_cap=0.20, day_usd_cap=0.40,
        )
        assert decision.allowed is True
        assert decision.status is None


class TestThreeStateProvenanceInference:
    def test_identity_reported_when_model_field_diverges(self):
        state, model = media_gen.infer_delivered_route_state(
            requested_model="google/nano-banana", reported_model="bytedance/seedream-v4-text-to-image",
        )
        assert state == media_gen.IDENTITY_REPORTED
        assert model == "bytedance/seedream-v4-text-to-image"

    def test_substituted_unknown_on_aspect_divergence_with_no_name(self):
        state, model = media_gen.infer_delivered_route_state(
            requested_model="google/nano-banana", reported_model=None,
            requested_aspect="1:1", reported_aspect="16:9",
        )
        assert state == media_gen.SUBSTITUTED_UNKNOWN
        assert model is None

    def test_assumed_as_requested_when_no_divergence_signal(self):
        state, model = media_gen.infer_delivered_route_state(
            requested_model="google/nano-banana", reported_model="google/nano-banana",
        )
        assert state == media_gen.ASSUMED_AS_REQUESTED
        assert model == "google/nano-banana"

        state2, model2 = media_gen.infer_delivered_route_state(
            requested_model="google/nano-banana", reported_model=None,
        )
        assert state2 == media_gen.ASSUMED_AS_REQUESTED
        assert model2 == "google/nano-banana"


class TestDownloadAndChecksum:
    def test_valid_image_downloads_and_checksums(self, tmp_path):
        fetcher = QueuedFetcher(responses={RESULT_IMAGE_URL: [_image_response()]})
        dest = tmp_path / "out.png"
        result = media_gen.download_and_checksum(fetcher, RESULT_IMAGE_URL, dest)
        assert result.ok is True
        assert dest.exists()
        assert result.checksum_sha256 == __import__("hashlib").sha256(_PNG_BYTES).hexdigest()

    def test_truncated_or_bad_magic_never_marked_complete(self, tmp_path):
        fetcher = QueuedFetcher(responses={RESULT_IMAGE_URL: [_image_response(body=b"not an image")]})
        dest = tmp_path / "out.png"
        result = media_gen.download_and_checksum(fetcher, RESULT_IMAGE_URL, dest)
        assert result.ok is False
        assert not dest.exists()
        assert result.checksum_sha256 is None


# ---------------------------------------------------------------------------
# KieClient: request/response shapes + key-never-in-trace.
# ---------------------------------------------------------------------------


class TestKieClient:
    def test_create_task_success_and_key_never_in_trace(self, tmp_path):
        secret = "kie_super_secret_key_value"
        fetcher = QueuedFetcher(responses={"createTask": [_create_task_ok("task_abc")]})
        trace = _trace(tmp_path)
        client = media_gen.KieClient(fetcher=fetcher, api_key=secret, trace=trace, registry=_registry())
        result = client.create_task(model="google/nano-banana", input_={"prompt": "a desk", "output_format": "png", "aspect_ratio": "1:1"}, purpose="test")
        trace.close()
        assert result.task_id == "task_abc"

        trace_text = (tmp_path / "trace.jsonl").read_text(encoding="utf-8")
        assert secret not in trace_text
        assert "Authorization" not in trace_text
        # Body was sent with the model + input shape docs.kie.ai documents.
        sent = json.loads(fetcher.request_bodies[0])
        assert sent == {"model": "google/nano-banana", "input": {"prompt": "a desk", "output_format": "png", "aspect_ratio": "1:1"}}

    def test_create_task_transport_error_raises_kie_transport_error(self, tmp_path):
        fetcher = QueuedFetcher(responses={"createTask": [FetchError("connection reset")]})
        trace = _trace(tmp_path)
        client = media_gen.KieClient(fetcher=fetcher, api_key="k", trace=trace, registry=_registry())
        with pytest.raises(media_gen.KieTransportError):
            client.create_task(model="google/nano-banana", input_={"prompt": "x"}, purpose="test")

    def test_create_task_definite_rejection_raises_kie_api_error(self, tmp_path):
        fetcher = QueuedFetcher(responses={"createTask": [_json_response({"code": 401, "msg": "unauthorized", "data": None})]})
        trace = _trace(tmp_path)
        client = media_gen.KieClient(fetcher=fetcher, api_key="k", trace=trace, registry=_registry())
        with pytest.raises(media_gen.KieApiError):
            client.create_task(model="google/nano-banana", input_={"prompt": "x"}, purpose="test")

    def test_record_info_parses_result_urls_and_credits(self, tmp_path):
        fetcher = QueuedFetcher(responses={"recordInfo": [_record_info_success()]})
        trace = _trace(tmp_path)
        client = media_gen.KieClient(fetcher=fetcher, api_key="k", trace=trace, registry=_registry())
        info = client.record_info("task_test_1", purpose="test")
        assert info.is_success
        assert info.result_urls == [RESULT_IMAGE_URL]
        assert info.credits_consumed == 4.0

    def test_get_credit_balance_returns_none_on_failure_never_raises(self, tmp_path):
        fetcher = QueuedFetcher(responses={"chat/credit": [FetchError("timeout")]})
        trace = _trace(tmp_path)
        client = media_gen.KieClient(fetcher=fetcher, api_key="k", trace=trace, registry=_registry())
        assert client.get_credit_balance(purpose="test") is None


# ---------------------------------------------------------------------------
# Store: write-ahead ledger, identity uniqueness.
# ---------------------------------------------------------------------------


class TestMediaIntentLedger:
    def test_insert_and_find_round_trip(self, tmp_path):
        store = _store(tmp_path)
        try:
            row = store.insert_media_intent(
                theme="hypedigitaly", run_date="2026-08-10", run_id="run1", cluster_key="ck1",
                asset_slot="linkedin", language="en", prompt_pattern_version=1, attempt=1,
                route_id="img-draft-nano-banana", model_string="google/nano-banana",
                requested_aspect="1:1", requested_output_format="png", prompt_sha256="abc123",
                expected_cost_credits=4.0, expected_cost_usd=0.02,
            )
            assert row.state == "intent"
            assert row.task_id is None
            found = store.find_media_intent(
                theme="hypedigitaly", run_date="2026-08-10", cluster_key="ck1", asset_slot="linkedin",
                language="en", prompt_pattern_version=1, attempt=1,
            )
            assert found is not None
            assert found.id == row.id
        finally:
            store.close()

    def test_identity_attempt_uniqueness_enforced(self, tmp_path):
        store = _store(tmp_path)
        try:
            kwargs = dict(
                theme="hypedigitaly", run_date="2026-08-10", run_id="run1", cluster_key="ck1",
                asset_slot="linkedin", language="en", prompt_pattern_version=1, attempt=1,
                route_id="img-draft-nano-banana", model_string="google/nano-banana",
                requested_aspect="1:1", requested_output_format="png", prompt_sha256="abc123",
                expected_cost_credits=4.0, expected_cost_usd=0.02,
            )
            store.insert_media_intent(**kwargs)
            with pytest.raises(MediaIntentAlreadyExists):
                store.insert_media_intent(**kwargs)
        finally:
            store.close()

    def test_unresolved_media_intents_excludes_terminal_rows(self, tmp_path):
        store = _store(tmp_path)
        try:
            row1 = store.insert_media_intent(
                theme="t", run_date="2026-08-10", run_id="r", cluster_key="a", asset_slot="linkedin",
                language="en", prompt_pattern_version=1, attempt=1, route_id="x", model_string="m",
                requested_aspect="1:1", requested_output_format="png", prompt_sha256="h1",
                expected_cost_credits=4, expected_cost_usd=0.02,
            )
            row2 = store.insert_media_intent(
                theme="t", run_date="2026-08-10", run_id="r", cluster_key="b", asset_slot="linkedin",
                language="en", prompt_pattern_version=1, attempt=1, route_id="x", model_string="m",
                requested_aspect="1:1", requested_output_format="png", prompt_sha256="h2",
                expected_cost_credits=4, expected_cost_usd=0.02,
            )
            store.update_media_intent(row2.id, state="done", terminal=True)
            unresolved = store.unresolved_media_intents("t")
            assert [r.id for r in unresolved] == [row1.id]
        finally:
            store.close()

    def test_asset_slot_free_text_supports_slide_encoding(self, tmp_path):
        """W8-9 Q4: no schema change needed -- ``asset_slot`` already free
        text, so ``"<destination>:<slot>"`` round-trips exactly like any
        other value."""
        store = _store(tmp_path)
        try:
            row = store.insert_media_intent(
                theme="hypedigitaly", run_date="2026-08-10", run_id="run1", cluster_key="ck1",
                asset_slot="instagram_feed:slide_01", language="en", prompt_pattern_version=2, attempt=1,
                route_id="img-standard-nano-banana-pro", model_string="nano-banana-2",
                requested_aspect="4:5", requested_output_format="png", prompt_sha256="abc123",
                expected_cost_credits=24.0, expected_cost_usd=0.12,
            )
            found = store.find_media_intent(
                theme="hypedigitaly", run_date="2026-08-10", cluster_key="ck1",
                asset_slot="instagram_feed:slide_01", language="en", prompt_pattern_version=2, attempt=1,
            )
            assert found is not None and found.id == row.id
        finally:
            store.close()


# ---------------------------------------------------------------------------
# plan_media_assets: hero vs per-slide expansion.
# ---------------------------------------------------------------------------


class TestPlanMediaAssets:
    def test_hero_plan_reads_crafted_prompt_map(self):
        statuses = [_copy_status()]
        crafted = {"ck1_linkedin": _crafted_hero("ck1_linkedin", "crafted!")}
        plans = media_gen.plan_media_assets(statuses, crafted_prompts=crafted)
        assert len(plans) == 1
        assert plans[0].asset_class == "hero"
        assert plans[0].slot == "hero"
        assert plans[0].crafted_prompt == "crafted!"
        assert plans[0].asset_slot == "linkedin"

    def test_ignores_crafted_prompt_when_copy_not_gated_pass(self):
        statuses = [_copy_status(status="held — awaiting operator copy", image_brief=None)]
        crafted = {"ck1_linkedin": _crafted_hero("ck1_linkedin", "crafted!")}
        plans = media_gen.plan_media_assets(statuses, crafted_prompts=crafted)
        assert plans[0].crafted_prompt is None
        assert plans[0].asset_class == "hero"

    def test_carousel_with_crafted_slides_expands_to_one_plan_per_slide(self):
        statuses = [_carousel_copy_status(n_slides=3)]
        crafted = {"ck1_instagram_feed": _crafted_carousel("ck1_instagram_feed", 3)}
        plans = media_gen.plan_media_assets(statuses, crafted_prompts=crafted)
        assert len(plans) == 3
        assert [p.slot for p in plans] == ["slide_01", "slide_02", "slide_03"]
        assert all(p.asset_class == "slide" for p in plans)
        assert plans[0].asset_slot == "instagram_feed:slide_01"
        assert plans[1].crafted_prompt == "Prompt for slide 2"
        assert plans[0].qa_expected_text == "Slide 1 title — Slide 1 body text."
        assert plans[0].qa_archetype == "editorial"

    def test_carousel_without_usable_crafted_set_falls_back_to_single_hero_plan(self):
        from hypeagent import promptcraft

        statuses = [_carousel_copy_status(n_slides=3)]
        crafted = {"ck1_instagram_feed": promptcraft.CraftedPromptSet(asset_id="ck1_instagram_feed", unavailable=True, unavailable_reason="LLM disabled")}
        plans = media_gen.plan_media_assets(statuses, crafted_prompts=crafted)
        assert len(plans) == 1
        assert plans[0].asset_class == "hero"
        assert plans[0].crafted_prompt is None
        assert plans[0].qa_expected_text is None  # nothing to verify on the fallback path


# ---------------------------------------------------------------------------
# MediaGenerator.process — the full per-asset orchestration.
# ---------------------------------------------------------------------------


class TestAwaitingCopyPlanOnly:
    def test_held_and_blocked_assets_never_touch_the_network(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(responses={})  # any fetch call fails the test
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher)
            plans = media_gen.plan_media_assets(
                [
                    _copy_status(status="held — awaiting operator copy", image_brief=None),
                    _copy_status(asset_id="ck2_linkedin", cluster_key="ck2", status="blocked — claim gate (repair budget exhausted)", image_brief=None),
                ]
            )
            result = generator.process(plans)
            trace.close()
            assert fetcher.calls == []
            assert result.total_spent_usd == 0.0
            statuses = {s.asset_id: s.status for s in result.statuses}
            assert statuses["ck1_linkedin"] == "awaiting copy — not submitted"
            assert statuses["ck2_linkedin"] == "not generated — copy blocked (no approved brief)"
        finally:
            store.close()


class TestHappyPathGeneration:
    def test_gated_pass_asset_generates_downloads_and_records_provenance(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_1")],
                    "recordInfo": [_record_info_success("task_1")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],  # 4 credits drop == $0.02, matches creditsConsumed
                    RESULT_IMAGE_URL: [_image_response()],
                }
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher)
            plans = media_gen.plan_media_assets([_copy_status()])
            result = generator.process(plans)
            trace.close()

            assert len(result.statuses) == 1
            status = result.statuses[0]
            assert status.status == "generated"
            assert status.slot == "hero"
            assert status.route_id == "img-draft-nano-banana"
            assert status.observed_cost_usd == pytest.approx(4.0 * 0.005)
            assert status.image_path is not None
            image_path = Path(status.image_path)
            assert image_path.exists()
            assert image_path.read_bytes() == _PNG_BYTES
            # W8-9 Q4 pack layout: one folder per asset, ``hero.png`` inside it.
            assert image_path.name == "hero.png"
            assert image_path.parent.name == "ck1_linkedin"

            provenance_path = tmp_path / "pack" / "media" / "ck1_linkedin" / "hero.provenance.yaml"
            assert provenance_path.exists()
            doc = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
            assert doc["delivered_route_state"] == media_gen.ASSUMED_AS_REQUESTED
            assert doc["checksum_sha256"] is not None
            assert doc["slot"] == "hero"
            assert doc["destination"] == "linkedin"
            assert doc["qa"]["status"] == "skipped"  # no LLM client wired -> skipped, not a failure
            provenance_text = provenance_path.read_text(encoding="utf-8")
            assert RESULT_IMAGE_URL not in provenance_text

            # Provider URL absent from the whole pack directory, not just this file.
            for path in (tmp_path / "pack").rglob("*"):
                if path.is_file():
                    assert RESULT_IMAGE_URL not in path.read_text(encoding="utf-8", errors="ignore")

            trace_text = (tmp_path / "trace.jsonl").read_text(encoding="utf-8")
            assert RESULT_IMAGE_URL not in trace_text
            assert "test-kie-key-value" not in trace_text

            # The ledger row is the source of truth and reflects the same facts.
            row = store.find_media_intent(
                theme="hypedigitaly", run_date="2026-08-10", cluster_key="ck1", asset_slot="linkedin",
                language="en", prompt_pattern_version=media_gen.PROMPT_PATTERN_VERSION, attempt=1,
            )
            assert row is not None
            assert row.state == "done"
            assert row.terminal is True
            assert row.checksum_sha256 is not None

            # W8-8: the full, exact composed prompt is persisted on the
            # ledger row AND in the per-asset provenance YAML -- own-authored
            # content, unlike the trace's hash-only record.
            expected_prompt = media_gen.compose_prompt("A calm office desk, no people.", _registry())
            assert row.prompt_full == expected_prompt
            assert doc["prompt_full"] == expected_prompt
            assert doc["prompt_sha256"] == media_gen.prompt_sha256(expected_prompt)
        finally:
            store.close()

    def test_provider_refusal_degrades_to_plan_only_with_reason(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_2")],
                    "recordInfo": [_record_info_fail("task_2", fail_msg="content policy violation: depiction refused")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(100.0)],
                }
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher)
            plans = media_gen.plan_media_assets([_copy_status()])
            result = generator.process(plans)
            trace.close()
            status = result.statuses[0]
            assert status.status == "failed — provider refused"
            assert "content policy" in (status.reason or "").lower()
        finally:
            store.close()


class TestBothCapsDistinctAndMidPack:
    def test_count_cap_stops_second_asset_with_distinct_status(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_a"), _create_task_ok("task_b")],
                    "recordInfo": [_record_info_success("task_a"), _record_info_success("task_b")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                    RESULT_IMAGE_URL: [_image_response(), _image_response()],
                }
            )
            media_config = _media_config(per_run_count_cap=1, per_run_usd_cap=10.0, per_day_usd_cap=10.0)
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, media_config=media_config)
            plans = media_gen.plan_media_assets(
                [_copy_status(), _copy_status(asset_id="ck1_instagram_feed", destination="instagram_feed")]
            )
            result = generator.process(plans)
            trace.close()
            statuses = [s.status for s in result.statuses]
            assert statuses[0] == "generated"
            assert statuses[1] == media_gen.STATUS_COUNT_CAPPED
            assert statuses[1] != media_gen.STATUS_BUDGET_CAPPED
        finally:
            store.close()

    def test_budget_cap_stops_second_asset_with_distinct_status(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_a")],
                    "recordInfo": [_record_info_success("task_a")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                    RESULT_IMAGE_URL: [_image_response()],
                }
            )
            # Route price 0.02; a run cap of 0.03 allows exactly one submission.
            media_config = _media_config(per_run_count_cap=10, per_run_usd_cap=0.03, per_day_usd_cap=10.0)
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, media_config=media_config)
            plans = media_gen.plan_media_assets(
                [_copy_status(), _copy_status(asset_id="ck1_instagram_feed", destination="instagram_feed")]
            )
            result = generator.process(plans)
            trace.close()
            statuses = [s.status for s in result.statuses]
            assert statuses[0] == "generated"
            assert statuses[1] == media_gen.STATUS_BUDGET_CAPPED
        finally:
            store.close()

    def test_cap_hit_mid_carousel_blocks_only_remaining_slides(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_s1"), _create_task_ok("task_s2")],
                    "recordInfo": [_record_info_success("task_s1"), _record_info_success("task_s2")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0), _credit_balance(92.0)],
                    RESULT_IMAGE_URL: [_image_response(), _image_response()],
                }
            )
            # Exactly 2 submissions allowed by count cap; the carousel has 4 slides.
            media_config = _media_config(per_run_count_cap=2, per_run_usd_cap=10.0, per_day_usd_cap=10.0)
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, media_config=media_config)
            statuses_in = [_carousel_copy_status(n_slides=4)]
            crafted = {"ck1_instagram_feed": _crafted_carousel("ck1_instagram_feed", 4)}
            plans = media_gen.plan_media_assets(statuses_in, crafted_prompts=crafted)
            result = generator.process(plans)
            trace.close()
            statuses = [s.status for s in result.statuses]
            assert statuses[0] == "generated"
            assert statuses[1] == "generated"
            assert statuses[2] == media_gen.STATUS_COUNT_CAPPED
            assert statuses[3] == media_gen.STATUS_COUNT_CAPPED
            # Traced, never silently dropped.
            trace_text = (tmp_path / "trace.jsonl").read_text(encoding="utf-8")
            assert "count capped" in trace_text or "STATUS_COUNT_CAPPED" in trace_text or "not generated" in trace_text
        finally:
            store.close()


class TestIntentBeforeSubmissionAndCrashResume:
    def test_transport_failure_at_submission_leaves_submitted_unknown_and_restart_never_resubmits(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            # createTask itself fails at the transport level -- the ambiguous
            # case: we do not know whether the provider received it.
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [FetchError("connection reset by peer")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(100.0)],
                }
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher)
            plans = media_gen.plan_media_assets([_copy_status()])
            result = generator.process(plans)
            trace.close()

            assert result.statuses[0].status == "submitted-unknown"
            create_task_calls = [c for c in fetcher.calls if "createTask" in c]
            assert len(create_task_calls) == 1  # exactly one createTask attempt -- never retried inline

            row = store.find_media_intent(
                theme="hypedigitaly", run_date="2026-08-10", cluster_key="ck1", asset_slot="linkedin",
                language="en", prompt_pattern_version=media_gen.PROMPT_PATTERN_VERSION, attempt=1,
            )
            assert row is not None
            assert row.state == "submitted-unknown"
            assert row.submitted_unknown_subcase == "A"
            assert row.task_id is None
            assert row.terminal is False

            # --- restart: a fresh generator (simulating a new process) ---
            trace2 = _trace(tmp_path, "trace2.jsonl")
            fetcher2 = QueuedFetcher(responses={})  # createTask must NEVER be called again
            generator2 = _generator(tmp_path, store=store, trace=trace2, fetcher=fetcher2)
            generator2.resolve_pending()  # phase 0: resolve-by-query, never resubmit
            trace2.close()
            assert fetcher2.calls == []  # no double submission

            # A second full process() call for the same identity/attempt must
            # also refuse to submit again -- it resolves the existing row.
            trace3 = _trace(tmp_path, "trace3.jsonl")
            fetcher3 = QueuedFetcher(responses={})
            generator3 = _generator(tmp_path, store=store, trace=trace3, fetcher=fetcher3)
            result3 = generator3.process(plans)
            trace3.close()
            assert fetcher3.calls == []
            assert result3.statuses[0].status == "submitted-unknown"
        finally:
            store.close()

    def test_phase_zero_resolves_a_known_task_id_and_adopts_completed_media(self, tmp_path):
        """A prior run committed the intent row and got a task id, but the
        process died before polling to completion. Phase 0 of the NEXT
        media stage invocation resolves it by query and adopts the result --
        it never resubmits."""
        store = _store(tmp_path)
        try:
            row = store.insert_media_intent(
                theme="hypedigitaly", run_date="2026-08-10", run_id="run0", cluster_key="ck1",
                asset_slot="linkedin", language="en", prompt_pattern_version=media_gen.PROMPT_PATTERN_VERSION,
                attempt=1, route_id="img-draft-nano-banana", model_string="google/nano-banana",
                requested_aspect="1:1", requested_output_format="png", prompt_sha256="h",
                expected_cost_credits=4.0, expected_cost_usd=0.02,
            )
            store.set_media_task_id(row.id, "task_prior_run")

            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "recordInfo": [_record_info_success("task_prior_run")],
                    RESULT_IMAGE_URL: [_image_response()],
                }
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher)
            generator.resolve_pending()
            trace.close()

            assert "createTask" not in " ".join(fetcher.calls)
            refreshed = store.get_media_intent(row.id)
            assert refreshed.state == "done"
            assert refreshed.terminal is True
            assert refreshed.image_path is not None
            assert Path(refreshed.image_path).exists()
            # Phase-0 adoption has no plan context -- QA is honestly
            # recorded as skipped, not silently omitted.
            provenance_path = Path(refreshed.image_path).with_suffix(".provenance.yaml")
            doc = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
            assert doc["qa"]["status"] == "skipped"
            assert "phase0" in doc["qa"]["skip_reason"]
        finally:
            store.close()

    def test_kill_after_slide_2_resume_adopts_1_and_2_submits_only_3_plus(self, tmp_path):
        """W8-9 Q4 per-slide idempotency: a process that submitted slides 1-2
        and then died is resumed by a fresh generator that must adopt 1-2 by
        query and submit ONLY 3+ -- zero double ``createTask``."""
        store = _store(tmp_path)
        try:
            # Simulate "process 1" committing + getting task ids for slides
            # 1 and 2 (one already resolved to done, one still polling when
            # the process died) without ever running the full submission
            # loop (that is exactly the scenario: a crash mid-pack).
            for slot, task_id in (("slide_01", "task_r1_s1"), ("slide_02", "task_r1_s2")):
                row = store.insert_media_intent(
                    theme="hypedigitaly", run_date="2026-08-10", run_id="run0", cluster_key="ck1",
                    asset_slot=f"instagram_feed:{slot}", language="en",
                    prompt_pattern_version=media_gen.PROMPT_PATTERN_VERSION, attempt=1,
                    route_id="img-draft-nano-banana", model_string="google/nano-banana",
                    requested_aspect="4:5", requested_output_format="png", prompt_sha256=f"h-{slot}",
                    expected_cost_credits=4.0, expected_cost_usd=0.02,
                )
                store.set_media_task_id(row.id, task_id)

            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_r2_s3"), _create_task_ok("task_r2_s4")],
                    "recordInfo": [
                        _record_info_success("task_r1_s1", result_url=RESULT_IMAGE_URL),
                        _record_info_success("task_r1_s2", result_url=RESULT_IMAGE_URL),
                        _record_info_success("task_r2_s3", result_url=RESULT_IMAGE_URL),
                        _record_info_success("task_r2_s4", result_url=RESULT_IMAGE_URL),
                    ],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0), _credit_balance(92.0)],
                    RESULT_IMAGE_URL: [_image_response()] * 4,
                }
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher)
            statuses_in = [_carousel_copy_status(n_slides=4)]
            crafted = {"ck1_instagram_feed": _crafted_carousel("ck1_instagram_feed", 4)}
            plans = media_gen.plan_media_assets(statuses_in, crafted_prompts=crafted)
            result = generator.process(plans)
            trace.close()

            assert [s.status for s in result.statuses] == ["generated", "generated", "generated", "generated"]
            create_task_calls = [c for c in fetcher.calls if "createTask" in c]
            assert len(create_task_calls) == 2  # ONLY slides 3 and 4 submitted fresh
            record_info_calls = [c for c in fetcher.calls if "recordInfo" in c]
            assert len(record_info_calls) == 4  # slides 1-2 resolved by query, 3-4 polled after submission
        finally:
            store.close()


class TestPollTimeoutPendingAdopted:
    def test_still_pending_at_timeout_returns_pending_adopted(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_slow")],
                    "recordInfo": [_record_info_waiting("task_slow")],  # repeats forever (single-item queue)
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                }
            )
            media_config = _media_config(poll_interval_seconds=0.0, poll_timeout_seconds=0.0)
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, media_config=media_config)
            plans = media_gen.plan_media_assets([_copy_status()])
            result = generator.process(plans)
            trace.close()

            assert result.statuses[0].status == "pending — adopted by a later run"
            assert result.pending_count == 1
            row = store.find_media_intent(
                theme="hypedigitaly", run_date="2026-08-10", cluster_key="ck1", asset_slot="linkedin",
                language="en", prompt_pattern_version=media_gen.PROMPT_PATTERN_VERSION, attempt=1,
            )
            assert row is not None
            assert row.terminal is False
            assert row.state == "polling"
        finally:
            store.close()


class TestUnexplainedSpendCircuitBreaker:
    def test_large_balance_divergence_halts_further_submissions(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_a"), _create_task_ok("task_b")],
                    "recordInfo": [_record_info_success("task_a"), _record_info_success("task_b")],
                    # Ledger only expects ~$0.02 for the first asset, but the
                    # observed balance moved by 20 credits ($0.10) -- a huge
                    # divergence that must trip the breaker before asset 2.
                    "chat/credit": [_credit_balance(100.0), _credit_balance(80.0), _credit_balance(80.0)],
                    RESULT_IMAGE_URL: [_image_response(), _image_response()],
                }
            )
            media_config = _media_config(per_run_count_cap=10, per_run_usd_cap=10.0, per_day_usd_cap=10.0, unexplained_spend_threshold=0.20)
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, media_config=media_config)
            plans = media_gen.plan_media_assets(
                [_copy_status(), _copy_status(asset_id="ck1_instagram_feed", destination="instagram_feed")]
            )
            result = generator.process(plans)
            trace.close()

            assert result.circuit_breaker_tripped is True
            assert result.statuses[0].status == "generated"
            assert result.statuses[1].status == "not generated — unexplained-spend circuit breaker"
            # The second asset's createTask must never have been called.
            assert fetcher.calls.count(CREATE_TASK_URL) == 1 or sum(1 for c in fetcher.calls if "createTask" in c) == 1
        finally:
            store.close()


class TestDryRun:
    def test_dry_run_produces_plan_only_and_spends_nothing(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(responses={})
            media_config = _media_config(dry_run=True)
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, media_config=media_config)
            plans = media_gen.plan_media_assets([_copy_status()])
            result = generator.process(plans)
            trace.close()
            assert fetcher.calls == []
            assert result.statuses[0].status == "plan-only — dry run"
            assert result.total_spent_usd == 0.0
        finally:
            store.close()


class TestRouteByClassSelection:
    def test_hero_and_slide_can_use_different_routes(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_hero"), _create_task_ok("task_slide")],
                    # Credits consumed match each route's own price exactly,
                    # so the balance-delta reconciliation never trips the
                    # circuit breaker (unrelated to what this test checks).
                    "recordInfo": [
                        _record_info_success("task_hero", model="nano-banana-2", credits=24.0),
                        _record_info_success("task_slide", model="google/nano-banana", credits=4.0),
                    ],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(76.0), _credit_balance(72.0)],
                    RESULT_IMAGE_URL: [_image_response(), _image_response()],
                }
            )
            registry = _registry(tier_ceiling="standard")
            media_config = _media_config(
                route_by_class={"hero": "img-standard-nano-banana-pro", "slide": "img-draft-nano-banana"},
                per_run_usd_cap=10.0, per_run_count_cap=10, per_day_usd_cap=10.0,
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, registry=registry, media_config=media_config)
            hero_status = _copy_status()
            slide_status = _carousel_copy_status(n_slides=1)
            crafted = {"ck1_instagram_feed": _crafted_carousel("ck1_instagram_feed", 1)}
            plans = media_gen.plan_media_assets([hero_status, slide_status], crafted_prompts=crafted)
            result = generator.process(plans)
            trace.close()
            by_slot = {(s.asset_id, s.slot): s for s in result.statuses}
            assert by_slot[("ck1_linkedin", "hero")].route_id == "img-standard-nano-banana-pro"
            assert by_slot[("ck1_instagram_feed", "slide_01")].route_id == "img-draft-nano-banana"
        finally:
            store.close()


class TestCraftedHeroPromptWiring:
    """W8-9 Q3c/Q4: the hero-image path prefers an N-D-crafted prompt over
    ``compose_prompt(image_brief)`` when one is available on the plan."""

    def test_crafted_hero_prompt_is_sent_instead_of_composed_prompt(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_crafted")],
                    "recordInfo": [_record_info_success("task_crafted")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                    RESULT_IMAGE_URL: [_image_response()],
                }
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher)
            plans = media_gen.plan_media_assets([_copy_status()])
            plans[0].crafted_prompt = "The N-D crafted prompt, verbatim text and all. @hypedigitaly."
            result = generator.process(plans)
            trace.close()

            assert result.statuses[0].status == "generated"
            create_task_body = json.loads(
                next(b for url, b in zip(fetcher.calls, fetcher.request_bodies) if "createTask" in url)
            )
            assert create_task_body["input"]["prompt"] == "The N-D crafted prompt, verbatim text and all. @hypedigitaly."
            expected_composed = media_gen.compose_prompt("A calm office desk, no people.", _registry())
            assert create_task_body["input"]["prompt"] != expected_composed
        finally:
            store.close()

    def test_no_crafted_prompt_falls_back_to_compose_prompt_exactly_as_before(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_fallback")],
                    "recordInfo": [_record_info_success("task_fallback")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                    RESULT_IMAGE_URL: [_image_response()],
                }
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher)
            plans = media_gen.plan_media_assets([_copy_status()])  # crafted_prompt defaults to None
            assert plans[0].crafted_prompt is None
            result = generator.process(plans)
            trace.close()
            assert result.statuses[0].status == "generated"
            create_task_body = json.loads(
                next(b for url, b in zip(fetcher.calls, fetcher.request_bodies) if "createTask" in url)
            )
            expected_composed = media_gen.compose_prompt("A calm office desk, no people.", _registry())
            assert create_task_body["input"]["prompt"] == expected_composed
        finally:
            store.close()


# ---------------------------------------------------------------------------
# N-E Vision-QA gate.
# ---------------------------------------------------------------------------


class TestVisionQaGate:
    def test_pass_verdict_keeps_status_generated(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_qa_pass")],
                    "recordInfo": [_record_info_success("task_qa_pass")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                    RESULT_IMAGE_URL: [_image_response()],
                    "chat/completions": [_qa_response(text_matches=True, archetype_ok=True)],
                }
            )
            llm_client = _llm_client(fetcher, trace)
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, llm_client=llm_client)
            plans = media_gen.plan_media_assets(
                [_copy_status()], crafted_prompts={"ck1_linkedin": _crafted_hero("ck1_linkedin")}
            )
            result = generator.process(plans)
            trace.close()
            assert result.statuses[0].status == "generated"
            assert result.statuses[0].qa_verdict == "pass"
            provenance_path = tmp_path / "pack" / "media" / "ck1_linkedin" / "hero.provenance.yaml"
            doc = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
            assert doc["qa"]["status"] == "pass"

            trace_text = (tmp_path / "trace.jsonl").read_text(encoding="utf-8")
            assert '"gate": "vision_qa"' in trace_text
        finally:
            store.close()

    def test_skipped_when_no_llm_client_is_not_a_failure(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_qa_skip")],
                    "recordInfo": [_record_info_success("task_qa_skip")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                    RESULT_IMAGE_URL: [_image_response()],
                }
            )
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, llm_client=None)
            plans = media_gen.plan_media_assets(
                [_copy_status()], crafted_prompts={"ck1_linkedin": _crafted_hero("ck1_linkedin")}
            )
            result = generator.process(plans)
            trace.close()
            assert result.statuses[0].status == "generated"
            assert result.statuses[0].qa_verdict == "skipped"
        finally:
            store.close()

    def test_fail_then_pass_regenerates_exactly_once_as_attempt_2(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_a1"), _create_task_ok("task_a2")],
                    "recordInfo": [_record_info_success("task_a1"), _record_info_success("task_a2")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0), _credit_balance(92.0)],
                    RESULT_IMAGE_URL: [_image_response(), _image_response()],
                    "chat/completions": [
                        _qa_response(text_matches=False, archetype_ok=True, mismatches=["headline missing"]),
                        _qa_response(text_matches=True, archetype_ok=True),
                    ],
                }
            )
            llm_client = _llm_client(fetcher, trace)
            media_config = _media_config(per_run_usd_cap=10.0, per_run_count_cap=10, per_day_usd_cap=10.0)
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, llm_client=llm_client, media_config=media_config)
            plans = media_gen.plan_media_assets(
                [_copy_status()], crafted_prompts={"ck1_linkedin": _crafted_hero("ck1_linkedin")}
            )
            result = generator.process(plans)
            trace.close()

            assert result.statuses[0].status == "generated"
            assert result.statuses[0].qa_verdict == "pass"
            create_task_calls = [c for c in fetcher.calls if "createTask" in c]
            assert len(create_task_calls) == 2  # exactly one regeneration

            # Attempt 2's ledger row exists under the SAME asset_slot, attempt=2.
            attempt2 = store.find_media_intent(
                theme="hypedigitaly", run_date="2026-08-10", cluster_key="ck1", asset_slot="linkedin",
                language="en", prompt_pattern_version=media_gen.PROMPT_PATTERN_VERSION, attempt=2,
            )
            assert attempt2 is not None
            assert attempt2.state == "done"
        finally:
            store.close()

    def test_fail_twice_holds_for_operator_review(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_b1"), _create_task_ok("task_b2")],
                    "recordInfo": [_record_info_success("task_b1"), _record_info_success("task_b2")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0), _credit_balance(92.0)],
                    RESULT_IMAGE_URL: [_image_response(), _image_response()],
                    "chat/completions": [
                        _qa_response(text_matches=False, archetype_ok=True, mismatches=["headline missing"]),
                        _qa_response(text_matches=False, archetype_ok=True, mismatches=["still missing"]),
                    ],
                }
            )
            llm_client = _llm_client(fetcher, trace)
            media_config = _media_config(per_run_usd_cap=10.0, per_run_count_cap=10, per_day_usd_cap=10.0)
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, llm_client=llm_client, media_config=media_config)
            plans = media_gen.plan_media_assets(
                [_copy_status()], crafted_prompts={"ck1_linkedin": _crafted_hero("ck1_linkedin")}
            )
            result = generator.process(plans)
            trace.close()

            assert result.statuses[0].status == "held-qa-failed"
            create_task_calls = [c for c in fetcher.calls if "createTask" in c]
            assert len(create_task_calls) == 2  # never a third attempt

            provenance_path = tmp_path / "pack" / "media" / "ck1_linkedin" / "hero.provenance.yaml"
            doc = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
            assert doc["status"] == "held-qa-failed"
            assert doc["qa"]["status"] == "fail"

            # Still terminal, never re-attempted on a later process() call.
            trace2 = _trace(tmp_path, "trace2.jsonl")
            fetcher2 = QueuedFetcher(responses={})
            generator2 = _generator(tmp_path, store=store, trace=trace2, fetcher=fetcher2, media_config=media_config)
            result2 = generator2.process(plans)
            trace2.close()
            assert fetcher2.calls == []
            assert result2.statuses[0].status == "held-qa-failed"
        finally:
            store.close()

    def test_no_expected_text_skips_without_calling_the_llm(self, tmp_path):
        store = _store(tmp_path)
        try:
            trace = _trace(tmp_path)
            fetcher = QueuedFetcher(
                responses={
                    "createTask": [_create_task_ok("task_noqa")],
                    "recordInfo": [_record_info_success("task_noqa")],
                    "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                    RESULT_IMAGE_URL: [_image_response()],
                    # No "chat/completions" fixture registered -- a real call
                    # here would raise FetchError and fail the test.
                }
            )
            llm_client = _llm_client(fetcher, trace)
            generator = _generator(tmp_path, store=store, trace=trace, fetcher=fetcher, llm_client=llm_client)
            plans = media_gen.plan_media_assets([_copy_status()])  # no crafted prompt -> no qa_expected_text
            result = generator.process(plans)
            trace.close()
            assert result.statuses[0].status == "generated"
            assert result.statuses[0].qa_verdict == "skipped"
        finally:
            store.close()
