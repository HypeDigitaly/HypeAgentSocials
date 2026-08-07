"""M4 pipeline-wiring tests (GOAL_ROADMAP.md): the ``media`` stage inserted
between ``copy`` and ``packaging``, fully offline against fixtures."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from hypeagent import media_gen, packaging, render_trace, run_identity, stages
from hypeagent.collectors.base import FixtureFetcher
from hypeagent.exit_codes import ExitClass
from hypeagent.trace import TraceWriter
from test_media_gen import (
    RESULT_IMAGE_URL,
    QueuedFetcher,
    _create_task_ok,
    _credit_balance,
    _image_response,
    _record_info_success,
)
from test_phase1_pipeline import _default_fixture_responses, _write_config

FIXTURES = Path(__file__).parent / "fixtures"


def _run_once_with_ctx(tmp_path: Path, fetcher, run_id: str):
    identity = run_identity.RunIdentity(run_id=run_id, run_date=run_id.split("_")[0], started_at=datetime.now().astimezone())
    logs_dir = tmp_path / "logs"
    run_dir = logs_dir / "runs" / identity.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    trace_path = run_dir / "trace.jsonl"
    tw = TraceWriter(trace_path, identity.run_id)
    ctx = stages.RunContext(
        run_id=identity.run_id, config_dir=tmp_path / "config", logs_dir=logs_dir,
        theme_name="hypedigitaly", fetcher_factory=lambda: fetcher,
    )
    tw.run_start(mode="interactive", theme="hypedigitaly", config_fingerprint=None, engine_version="0.1.0")
    try:
        exit_class_value = stages.run_pipeline(ctx, tw)
    finally:
        if ctx.store is not None:
            ctx.store.close()
    tw.run_end(exit_class_value, totals={})
    tw.close()
    render_trace.render(trace_path)
    return ctx, run_dir, trace_path, exit_class_value


def _merged_fetcher(kie_responses: dict) -> QueuedFetcher:
    """A single fetcher instance serving both the free-collector fixtures
    (single-response-per-URL, from test_phase1's helper) and the Kie
    endpoints (queued responses, from test_media_gen's helper)."""
    responses: dict = {k: [v] for k, v in _default_fixture_responses().items()}
    responses.update(kie_responses)
    return QueuedFetcher(responses=responses)


class TestAwaitingCopyMediaPlanOnly:
    def test_held_assets_plan_only_through_full_pipeline(self, tmp_path):
        _write_config(tmp_path)
        fetcher = _merged_fetcher({})
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, "2026-08-10_m4a1")

        assert exit_class_value == ExitClass.SUCCESS.value
        media_statuses = ctx.extra.get("media_asset_statuses", [])
        assert media_statuses  # the fixture set produces at least one EN copy asset
        assert all(s.status == "awaiting copy — not submitted" for s in media_statuses)
        assert all(s.observed_cost_usd is None and s.expected_cost_usd is None for s in media_statuses)

        # No Kie key file exists in this test's secrets dir -> zero network
        # calls to api.kie.ai were made at all.
        assert not any("kie.ai" in url for url in fetcher.calls)

        digest_text = (run_dir / "pack" / "digest.md").read_text(encoding="utf-8")
        assert "Media status" in digest_text
        assert "awaiting copy — not submitted" in digest_text
        assert "logo overlay" in digest_text.lower()
        assert "deferred to a later phase" in digest_text.lower()

        # No media_intents rows were ever written -- planning is zero-cost
        # and never touches the write-ahead ledger.
        from hypeagent.store import Store

        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            assert store.unresolved_media_intents("hypedigitaly") == []
        finally:
            store.close()


class TestGatedPassGeneratesRealImage:
    def test_gated_pass_asset_generates_downloads_and_digest_shows_it(self, tmp_path):
        _write_config(tmp_path)
        fetcher = _merged_fetcher({})
        run_id = "2026-08-10_m4b1"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)

        statuses = ctx.extra.get("copy_asset_statuses", [])
        assert statuses, "fixture set is expected to produce at least one EN copy asset"
        held = next(s for s in statuses if s.status == "held — awaiting operator copy")

        resp_dir = run_dir / "copy_responses"
        resp_dir.mkdir(parents=True, exist_ok=True)
        (resp_dir / f"{held.asset_id}.yaml").write_text(
            yaml.safe_dump({
                "headline": "AI agents are changing outbound sales",
                "caption": "See how small businesses use AI chatbots. Learn more at example.com. [AI-generated content]",
                "image_brief": "A calm, people-free office scene, no product depiction.",
            }),
            encoding="utf-8",
        )

        # Re-run only the copy stage against the same context -- the
        # response is now consumed and gated, exactly as test_phase2 proves.
        second_trace = TraceWriter(tmp_path / "logs" / "second_trace.jsonl", run_id)
        try:
            copy_result = stages.stage_copy(ctx, second_trace)
        finally:
            second_trace.close()
        assert copy_result.outcome == "ok"

        # A Kie API key now "arrives" -- write it, and give the fetcher a
        # queued Kie createTask/recordInfo/credit round trip.
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir(parents=True, exist_ok=True)
        (secrets_dir / "kie.key").write_text("kie_test_secret_value_12345", encoding="utf-8")

        # ``_run_once_with_ctx`` closed ``ctx.store`` on exit (mirrors the
        # real engine closing it at run end) -- the media stage needs it
        # open again, exactly as a fresh interactive invocation would reopen
        # the same on-disk engine.db.
        from hypeagent.store import Store

        ctx.store = Store.open(ctx.logs_dir, tmp_path / "secrets")

        gated = next(s for s in ctx.extra["copy_asset_statuses"] if s.status == "gated-pass")
        kie_fetcher = _merged_fetcher(
            {
                "createTask": [_create_task_ok("task_pipeline_1")],
                "recordInfo": [_record_info_success("task_pipeline_1")],
                "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                RESULT_IMAGE_URL: [_image_response()],
            }
        )
        ctx.fetcher_factory = lambda: kie_fetcher

        media_trace_path = tmp_path / "logs" / "media_trace.jsonl"
        media_trace = TraceWriter(media_trace_path, run_id)
        try:
            media_result = stages.stage_media(ctx, media_trace)
        finally:
            media_trace.close()
        render_trace.render(media_trace_path)

        assert media_result.outcome == "ok"
        media_statuses = ctx.extra["media_asset_statuses"]
        generated = next(s for s in media_statuses if s.asset_id == gated.asset_id)
        assert generated.status == "generated"
        assert generated.image_path is not None
        assert Path(generated.image_path).exists()

        # The key never reaches the trace.
        media_trace_text = media_trace_path.read_text(encoding="utf-8")
        assert "kie_test_secret_value_12345" not in media_trace_text
        # The provider result URL never reaches the trace or the pack.
        assert RESULT_IMAGE_URL not in media_trace_text

        # Re-package and re-render the digest with the media statuses now
        # present, exactly as ``stage_packaging``/``stage_digest`` would.
        packaging_trace = TraceWriter(tmp_path / "logs" / "packaging_trace.jsonl", run_id)
        try:
            stages.stage_packaging(ctx, packaging_trace)
            stages.stage_digest(ctx, packaging_trace)
        finally:
            packaging_trace.close()

        pack_dir = run_dir / "pack"
        for path in pack_dir.rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                assert RESULT_IMAGE_URL not in text
                assert "kie_test_secret_value_12345" not in text

        digest_text = (pack_dir / "digest.md").read_text(encoding="utf-8")
        assert "generated" in digest_text
        assert "media — actual spend" in digest_text.lower()
        assert "price snapshot" in digest_text.lower()

        provenance_path = pack_dir / "media" / f"{gated.cluster_key}_{gated.destination}" / "hero.provenance.yaml"
        assert provenance_path.exists()
        doc = yaml.safe_load(provenance_path.read_text(encoding="utf-8"))
        assert doc["delivered_route_state"] in (
            media_gen.IDENTITY_REPORTED, media_gen.SUBSTITUTED_UNKNOWN, media_gen.ASSUMED_AS_REQUESTED,
        )
        assert doc["logo_overlay"].startswith("deferred to a later phase")

        ctx.store.close()


class TestKieKeyResolutionPrecedence:
    """W8-9 Phase 1: the media stage resolves ``KIE_API_KEY`` via real
    environment variable > repo-root ``.env`` > the legacy key file --
    exercised through the real ``stage_media`` code path (not a unit test
    of ``resolve_secret`` in isolation)."""

    def test_dotenv_value_is_used_with_no_legacy_key_file_present(self, tmp_path, monkeypatch):
        monkeypatch.delenv("KIE_API_KEY", raising=False)
        _write_config(tmp_path)
        fetcher = _merged_fetcher({})
        run_id = "2026-08-10_m4kie1"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)

        statuses = ctx.extra.get("copy_asset_statuses", [])
        held = next(s for s in statuses if s.status == "held — awaiting operator copy")
        resp_dir = run_dir / "copy_responses"
        resp_dir.mkdir(parents=True, exist_ok=True)
        (resp_dir / f"{held.asset_id}.yaml").write_text(
            yaml.safe_dump({
                "headline": "AI agents are changing outbound sales",
                "caption": "See how small businesses use AI chatbots. Learn more at example.com. [AI-generated content]",
                "image_brief": "A calm, people-free office scene, no product depiction.",
            }),
            encoding="utf-8",
        )
        second_trace = TraceWriter(tmp_path / "logs" / "second_trace.jsonl", run_id)
        try:
            stages.stage_copy(ctx, second_trace)
        finally:
            second_trace.close()

        # No legacy secrets/kie.key file anywhere -- the ONLY source of the
        # key is the repo-root .env this test writes next to config_dir.
        (tmp_path / ".env").write_text("KIE_API_KEY=kie_dotenv_secret_value\n", encoding="utf-8")

        from hypeagent.store import Store

        ctx.store = Store.open(ctx.logs_dir, tmp_path / "secrets", config_dir=ctx.config_dir)
        gated = next(s for s in ctx.extra["copy_asset_statuses"] if s.status == "gated-pass")
        kie_fetcher = _merged_fetcher(
            {
                "createTask": [_create_task_ok("task_dotenv_1")],
                "recordInfo": [_record_info_success("task_dotenv_1")],
                "chat/credit": [_credit_balance(100.0), _credit_balance(96.0)],
                RESULT_IMAGE_URL: [_image_response()],
            }
        )
        ctx.fetcher_factory = lambda: kie_fetcher

        media_trace_path = tmp_path / "logs" / "media_trace_dotenv.jsonl"
        media_trace = TraceWriter(media_trace_path, run_id)
        try:
            media_result = stages.stage_media(ctx, media_trace)
        finally:
            media_trace.close()

        assert media_result.outcome == "ok"
        generated = next(s for s in ctx.extra["media_asset_statuses"] if s.asset_id == gated.asset_id)
        assert generated.status == "generated"

        # The .env-sourced key never reaches the trace.
        media_trace_text = media_trace_path.read_text(encoding="utf-8")
        assert "kie_dotenv_secret_value" not in media_trace_text

        ctx.store.close()


class TestExitClassMapping:
    def test_media_budget_capped_mid_pack_maps_to_its_own_exit_class(self, tmp_path, monkeypatch):
        def fake_media(ctx, trace):
            return stages.StageResult(outcome="degraded", items_in=2, items_out=2, extra={"budget_capped_mid_pack": True})

        monkeypatch.setattr(stages, "CANONICAL_STAGES", (("media", fake_media),))
        ctx = stages.RunContext(run_id="x", config_dir=tmp_path / "config", logs_dir=tmp_path / "logs")
        trace = TraceWriter(tmp_path / "trace.jsonl", "x")
        try:
            exit_class_value = stages.run_pipeline(ctx, trace)
        finally:
            trace.close()
        assert exit_class_value == ExitClass.PARTIAL_SUCCESS_BUDGET_CAPPED_MID_PACK.value

    def test_media_pending_only_maps_to_completed_with_pending_media(self, tmp_path, monkeypatch):
        def fake_media(ctx, trace):
            return stages.StageResult(outcome="degraded", items_in=1, items_out=1, extra={"pending_media_only": True})

        monkeypatch.setattr(stages, "CANONICAL_STAGES", (("media", fake_media),))
        ctx = stages.RunContext(run_id="x", config_dir=tmp_path / "config", logs_dir=tmp_path / "logs")
        trace = TraceWriter(tmp_path / "trace.jsonl", "x")
        try:
            exit_class_value = stages.run_pipeline(ctx, trace)
        finally:
            trace.close()
        assert exit_class_value == ExitClass.COMPLETED_WITH_PENDING_MEDIA.value

    def test_media_circuit_breaker_maps_to_completed_degraded(self, tmp_path, monkeypatch):
        def fake_media(ctx, trace):
            return stages.StageResult(outcome="degraded", items_in=2, items_out=2, extra={"circuit_breaker_tripped": True})

        monkeypatch.setattr(stages, "CANONICAL_STAGES", (("media", fake_media),))
        ctx = stages.RunContext(run_id="x", config_dir=tmp_path / "config", logs_dir=tmp_path / "logs")
        trace = TraceWriter(tmp_path / "trace.jsonl", "x")
        try:
            exit_class_value = stages.run_pipeline(ctx, trace)
        finally:
            trace.close()
        assert exit_class_value == ExitClass.COMPLETED_DEGRADED.value
