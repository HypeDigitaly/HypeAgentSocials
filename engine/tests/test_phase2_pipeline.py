"""M3 pipeline-wiring tests (GOAL_ROADMAP.md): brand_truth -> spin -> copy,
inserted between ranking and packaging, fully offline against fixtures."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import yaml

from hypeagent import render_trace, run_identity, stages
from hypeagent.collectors.base import FixtureFetcher
from hypeagent.exit_codes import ExitClass
from hypeagent.trace import TraceWriter
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


class TestBrandTruthSpinCopyWiring:
    def test_en_candidate_reaches_copy_and_is_held(self, tmp_path):
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, "2026-08-10_p2p2")

        # Held state is a legitimate successful outcome, not a degrade.
        assert exit_class_value == ExitClass.SUCCESS.value

        panel_path = run_dir / "pack" / "brand_truth_panel.yaml"
        assert panel_path.exists()
        panel_doc = yaml.safe_load(panel_path.read_text(encoding="utf-8"))
        assert panel_doc["band"] == "fresh"
        assert panel_doc["copy_allowed"] is True

        digest_text = (run_dir / "pack" / "digest.md").read_text(encoding="utf-8")
        assert "Brand-truth panel" in digest_text
        assert panel_doc["snapshot_id"] in digest_text

        statuses = ctx.extra.get("copy_asset_statuses", [])
        if statuses:  # at least one EN candidate passed the fit gate in this fixture set
            assert any(s.status == "held — awaiting operator copy" for s in statuses)
            assert "Copy status" in digest_text
            assert "held" in digest_text.lower()
            requests_dir = run_dir / "copy_requests"
            assert requests_dir.exists()
            assert any(requests_dir.glob("*.yaml"))
            for req_file in requests_dir.glob("*.yaml"):
                doc = yaml.safe_load(req_file.read_text(encoding="utf-8"))
                assert "spin_rationale" in doc
                assert "disclosure_requirement" in doc

        if ctx.extra.get("spin_results"):
            assert "Spin rationale" in digest_text
            assert "Topic:" in digest_text

        if ctx.extra.get("cs_holds"):
            assert "Czech copy not in goal scope" in digest_text

    def test_stale_snapshot_degrades_run_and_refuses_copy(self, tmp_path):
        _write_config(tmp_path)
        # Overwrite the (fresh) snapshot the shared helper wrote with a stale one.
        snapshots_dir = tmp_path / "config" / "snapshots"
        for f in snapshots_dir.glob("*.yaml"):
            f.unlink()
        (snapshots_dir / "claim_ledger_snapshot_2020-01-01.yaml").write_text(
            "meta:\n  snapshot_id: old-snap\n  taken_at: \"2020-01-01\"\n  max_age_days: 30\nclaims: []\n",
            encoding="utf-8",
        )
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, "2026-08-10_stale")

        assert exit_class_value == ExitClass.COMPLETED_DEGRADED.value
        panel = ctx.extra["brand_truth_panel"]
        assert panel.band == "stale"
        assert panel.copy_allowed is False
        assert ctx.extra.get("copy_asset_statuses") == []

        requests_dir = run_dir / "copy_requests"
        assert not requests_dir.exists() or not any(requests_dir.glob("*.yaml"))

        digest_text = (run_dir / "pack" / "digest.md").read_text(encoding="utf-8")
        assert "stale" in digest_text.lower()
        assert "research-only" in digest_text.lower() or "refuses" in digest_text.lower()

    def test_resume_after_operator_writes_response_gates_and_passes(self, tmp_path):
        """Re-running the ``copy`` stage against the SAME run identity after
        a response file appears consumes it and runs the gate — the round
        trip the interactive-file provider exists for.

        This deliberately re-invokes ``stage_copy`` directly (not the whole
        pipeline a second time): a second full-pipeline pass on the same
        calendar day would hit cross-day dedupe's own "generated previously,
        nothing new — suppressed" rule (§2.8a, already covered by
        ``test_phase1_pipeline.py``'s dedupe tests) and never re-reach spin
        at all, which would test dedupe, not copy resumability."""
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        run_id = "2026-08-10_resu1"
        ctx, run_dir, trace_path, exit_class_value = _run_once_with_ctx(tmp_path, fetcher, run_id)

        statuses = ctx.extra.get("copy_asset_statuses", [])
        assert statuses, "fixture set is expected to produce at least one EN copy asset"
        held = next(s for s in statuses if s.status == "held — awaiting operator copy")

        requests_dir = run_dir / "copy_requests"
        assert (requests_dir / f"{held.asset_id}.yaml").exists()

        resp_dir = run_dir / "copy_responses"
        resp_dir.mkdir(parents=True, exist_ok=True)
        (resp_dir / f"{held.asset_id}.yaml").write_text(
            yaml.safe_dump({
                "headline": "AI agents are changing outbound sales",
                "caption": "See how small businesses use AI chatbots. Learn more at example.com. [AI-generated content]",
                "image_brief": "A calm, people-free office scene.",
            }),
            encoding="utf-8",
        )

        # Re-run only the copy stage against the same context/run_dir — the
        # request file must not be rewritten, and the response must now gate.
        second_trace_path = tmp_path / "logs" / "second_trace.jsonl"
        second_trace = TraceWriter(second_trace_path, run_id)
        try:
            result = stages.stage_copy(ctx, second_trace)
        finally:
            second_trace.close()
        assert result.outcome == "ok"
        statuses2 = ctx.extra.get("copy_asset_statuses", [])
        matching = next(s for s in statuses2 if s.asset_id == held.asset_id)
        assert matching.status == "gated-pass"
        assert matching.headline
