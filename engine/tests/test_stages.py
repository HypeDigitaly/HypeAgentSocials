"""Tests for hypeagent.stages — Q6 re-audit R2 (analysis moved AFTER
ranking, receiving only this run's winning topics) and the archetype-
rotation ``asset_index`` wiring into ``promptcraft.craft_prompts``."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from hypeagent import analysis, promptcraft, stages
from hypeagent.collectors.base import FixtureFetcher
from hypeagent.copy_gen import AssetCopyStatus
from hypeagent.ranking import RankingResult, Scorecard
from hypeagent.store import Store
from hypeagent.trace import TraceWriter
from test_phase1_pipeline import _default_fixture_responses, _write_config


def _scorecard(cluster_key: str, language: str, title: str) -> Scorecard:
    return Scorecard(
        cluster_key=cluster_key, language=language, representative_title=title,
        composite=0.5, band="High", sub_scores={}, rationale={}, sources=[], families=[],
        evidence_quality_label="", signal_class="", signal_age_hours=0.0, gate_status="pass",
        per_language_outcome="generate", per_language_outcome_rationale="", ranking_config_version=1,
        fit_method="", dedupe_status="", what_changed="", demand_modifier_label="",
    )


class TestCanonicalStageOrder:
    def test_ranking_precedes_analysis_in_the_canonical_order(self):
        names = stages.CANONICAL_STAGE_NAMES
        assert names.index("ranking") < names.index("analysis")
        assert [name for name, _fn in stages.CANONICAL_STAGES] == list(names)

    def test_analysis_and_ranking_are_not_resumable_stages(self):
        assert "analysis" not in stages.RESUME_STAGE_NAMES
        assert "ranking" not in stages.RESUME_STAGE_NAMES

    def test_full_run_trace_shows_ranking_stage_start_before_analysis(self, tmp_path):
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        run_id = "2026-08-10_ord01"
        logs_dir = tmp_path / "logs"
        run_dir = logs_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        trace_path = run_dir / "trace.jsonl"
        tw = TraceWriter(trace_path, run_id)
        ctx = stages.RunContext(
            run_id=run_id, config_dir=tmp_path / "config", logs_dir=logs_dir,
            theme_name="hypedigitaly", fetcher_factory=lambda: fetcher,
        )
        tw.run_start(mode="interactive", theme="hypedigitaly", config_fingerprint=None, engine_version="0.1.0")
        try:
            stages.run_pipeline(ctx, tw)
        finally:
            if ctx.store is not None:
                ctx.store.close()
            tw.run_end("success", totals={})
            tw.close()

        import json

        lines = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
        starts = [e["stage"] for e in lines if e["event"] == "stage_start"]
        assert starts.index("ranking") < starts.index("analysis")
        assert starts.index("collection") < starts.index("ranking")


class TestAnalysisReceivesOnlyWinningTopics:
    def test_stage_analysis_passes_winning_topics_from_ranking_result(self, tmp_path, monkeypatch):
        _write_config(tmp_path)
        logs_dir = tmp_path / "logs"
        run_id = "2026-08-10_win01"
        ctx = stages.RunContext(
            run_id=run_id, config_dir=tmp_path / "config", logs_dir=logs_dir, theme_name="hypedigitaly",
        )
        stages._load_theme_and_config(ctx)
        ctx.store = Store.open(logs_dir, tmp_path / "secrets", config_dir=ctx.config_dir)
        run_dir = logs_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        trace = TraceWriter(run_dir / "trace.jsonl", run_id)
        try:
            en_winner = _scorecard("c1", "en", "AI Agents for Outbound Sales")
            cs_winner = _scorecard("c2", "cs", "AI agenti pro prodej")
            ranking_result = RankingResult(
                all_scorecards=[en_winner, cs_winner],
                top_by_language={"en": [en_winner], "cs": [cs_winner]},
                evidence_floor_breached={}, evidence_floor_consecutive={}, active_family_count=1,
                zero_passing_candidates=False, candidate_canonical_keys={},
            )
            ctx.extra["ranking_result"] = ranking_result

            captured: dict = {}

            def fake_run_trend_visual_analyst(**kwargs):
                captured.update(kwargs)
                return analysis.ViralPlaybook()

            monkeypatch.setattr(stages.analysis, "run_trend_visual_analyst", fake_run_trend_visual_analyst)

            stages.stage_analysis(ctx, trace)
            # Only the EN winner's title -- CS is not this goal's generation
            # language (GENERATION_LANGUAGE) and is never included.
            assert captured["winning_topics"] == ["AI Agents for Outbound Sales"]
        finally:
            trace.close()
            ctx.store.close()

    def test_no_ranking_result_yet_analyzes_everything(self, tmp_path, monkeypatch):
        """Direct unit invocation without a prior ranking stage (e.g. a
        future caller/test) degrades to ``winning_topics=None`` — analyze
        everything, exactly the pre-R2 behaviour -- rather than crashing."""
        _write_config(tmp_path)
        logs_dir = tmp_path / "logs"
        run_id = "2026-08-10_win02"
        ctx = stages.RunContext(
            run_id=run_id, config_dir=tmp_path / "config", logs_dir=logs_dir, theme_name="hypedigitaly",
        )
        stages._load_theme_and_config(ctx)
        ctx.store = Store.open(logs_dir, tmp_path / "secrets", config_dir=ctx.config_dir)
        run_dir = logs_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        trace = TraceWriter(run_dir / "trace.jsonl", run_id)
        try:
            captured: dict = {}

            def fake_run_trend_visual_analyst(**kwargs):
                captured.update(kwargs)
                return analysis.ViralPlaybook()

            monkeypatch.setattr(stages.analysis, "run_trend_visual_analyst", fake_run_trend_visual_analyst)
            stages.stage_analysis(ctx, trace)
            assert captured["winning_topics"] is None
        finally:
            trace.close()
            ctx.store.close()


class TestArchetypeRotationAssetIndexWiring:
    """The coordinator hand-off: ``_craft_media_prompts_for_run`` must pass
    a distinct, incrementing ``asset_index`` per crafted asset this run so
    ``promptcraft.pick_archetype_register``'s rotation actually rotates."""

    def _status(self, asset_id: str, cluster_key: str, destination: str) -> AssetCopyStatus:
        return AssetCopyStatus(
            asset_id=asset_id, cluster_key=cluster_key, destination=destination, status="gated-pass",
            attempt=1, headline="h", caption="c [AI-generated content]", image_brief="a calm scene",
        )

    def test_two_consecutively_crafted_assets_receive_different_asset_index(self, tmp_path, monkeypatch):
        _write_config(tmp_path)
        logs_dir = tmp_path / "logs"
        run_id = "2026-08-10_idx01"
        ctx = stages.RunContext(
            run_id=run_id, config_dir=tmp_path / "config", logs_dir=logs_dir, theme_name="hypedigitaly",
        )
        stages._load_theme_and_config(ctx)
        ctx.store = Store.open(logs_dir, tmp_path / "secrets", config_dir=ctx.config_dir)
        run_dir = logs_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        trace = TraceWriter(run_dir / "trace.jsonl", run_id)
        try:
            ctx.extra["llm_client"] = None  # LLM disabled path -- craft_prompts still gets called, unavailable=True
            statuses = [
                self._status("c1_linkedin", "c1", "linkedin"),
                self._status("c1_instagram_feed", "c1", "instagram_feed"),
            ]

            captured_indices: list[int] = []
            real_craft_prompts = promptcraft.craft_prompts

            def spy_craft_prompts(**kwargs):
                captured_indices.append(kwargs.get("asset_index"))
                return real_craft_prompts(**kwargs)

            monkeypatch.setattr(promptcraft, "craft_prompts", spy_craft_prompts)
            monkeypatch.setattr(stages.promptcraft, "craft_prompts", spy_craft_prompts)

            stages._craft_media_prompts_for_run(ctx, trace, statuses)

            assert captured_indices == [0, 1]
        finally:
            trace.close()
            ctx.store.close()
