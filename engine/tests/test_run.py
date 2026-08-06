"""End-to-end tests for the run skeleton (hypeagent.main)."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from hypeagent import main as main_module
from hypeagent import run_identity, stages
from hypeagent.exit_codes import EXIT_CODE_MAP, ExitClass


def _write_brand_truth_config(config_dir):
    """M3's brand-truth stage (stages.stage_brand_truth) fails closed on a
    missing ``brand_facts.yaml`` or claim-ledger snapshot — every fixture
    that runs the full pipeline needs a minimal, valid pair. ``taken_at`` is
    always "today" so the snapshot is never stale against the real clock
    these end-to-end tests run under."""
    (config_dir / "brand_facts.yaml").write_text(
        "identity:\n"
        "  legal_name: Test Co\n"
        "  source: test fixture\n"
        "capabilities:\n"
        "  positive:\n"
        "    - id: cap-test\n"
        "      en: AI chatbots and automation for businesses\n"
        "      source: test fixture\n"
        "  negative:\n"
        "    - No physical products\n"
        "icp:\n"
        "  - id: icp-test\n"
        "    en: Small businesses wanting AI automation\n"
        "    source: test fixture\n"
        "cta_set:\n"
        "  - id: cta-test\n"
        "    class: content\n"
        "    en: Learn more\n"
        "pricing_policy:\n"
        "  policy: prices-never-stated\n"
        "  rationale: test fixture\n"
        "hard_excludes_ref: config/hard_excludes.yaml\n"
        "spin_notes: {}\n",
        encoding="utf-8",
    )
    snapshots_dir = config_dir / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().astimezone().date().isoformat()
    (snapshots_dir / f"claim_ledger_snapshot_{today}.yaml").write_text(
        "meta:\n"
        "  snapshot_id: test-snapshot\n"
        f"  taken_at: \"{today}\"\n"
        "  max_age_days: 30\n"
        "claims: []\n",
        encoding="utf-8",
    )


def _write_minimal_config(repo_root):
    """The Phase-1 fail-closed config surface, minimal but complete.

    Milestone 2 extends ``theme_load`` to also require the special-category
    deny-list, the special-category lexicon, and a theme research block
    (config_load.load_theme_research_config) — all fail-closed, same as
    hard_excludes.yaml. The theme here declares zero enabled sources, so a
    run through this minimal fixture makes zero network calls and produces
    zero candidates: a legitimate, deterministic "success" outcome, not a
    stub. Dedicated fixture-driven collector/ranking tests live in
    test_phase1_pipeline.py.
    """
    config_dir = repo_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "hard_excludes.yaml").write_text(
        "hard_excludes:\n"
        "  topics: []\n"
        "  framings: []\n"
        "  claim_types: []\n"
        "  do_not_mention_entities: []\n",
        encoding="utf-8",
    )
    (config_dir / "special_category_source_deny_list.yaml").write_text(
        "special_category_deny_list:\n"
        "  denied_defining_characteristics: []\n"
        "  denied_sources: []\n"
        "  denied_communities: []\n",
        encoding="utf-8",
    )
    (config_dir / "special_category_lexicon.yaml").write_text(
        "special_category_lexicon:\n"
        "  health_condition: []\n",
        encoding="utf-8",
    )
    themes_dir = config_dir / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    (themes_dir / "hypedigitaly.yaml").write_text(
        "theme:\n"
        "  name: hypedigitaly\n"
        "  languages: [en, cs]\n"
        "research:\n"
        "  watch_topics: {en: [], cs: []}\n"
        "  icp_terms: {en: [], cs: []}\n"
        "  sources: {}\n"
        "ranking:\n"
        "  ranking_config_version: 1\n"
        "  brand_fit_floor: 0.35\n"
        "  top_n_per_language: 3\n"
        "  freshness_half_life_hours: {spike: 6, rising: 24, launch-hype: 72, evergreen-pain: 720}\n"
        "  evidence_floor: {en: {min_candidates: 1, min_families: 1}, cs: {min_candidates: 1, min_families: 1}}\n",
        encoding="utf-8",
    )
    _write_brand_truth_config(config_dir)


def test_end_to_end_run_produces_all_artifacts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_minimal_config(tmp_path)

    exit_code = main_module.main([])

    assert exit_code == EXIT_CODE_MAP[ExitClass.SUCCESS]

    logs_dir = tmp_path / "logs"
    latest_path = logs_dir / "latest.txt"
    ledger_path = logs_dir / "run_ledger.jsonl"
    assert latest_path.exists()

    from pathlib import Path

    run_dir = Path(latest_path.read_text(encoding="utf-8").strip())
    trace_path = run_dir / "trace.jsonl"
    md_path = run_dir / "trace.md"

    assert trace_path.exists()
    assert md_path.exists()
    assert ledger_path.exists()

    ledger_lines = ledger_path.read_text(encoding="utf-8").splitlines()
    assert len(ledger_lines) == 1
    ledger_entry = json.loads(ledger_lines[0])
    assert ledger_entry["exit_class"] == ExitClass.SUCCESS.value
    assert ledger_entry["trace_path"] == str(trace_path)

    trace_lines = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    assert trace_lines[0]["event"] == "run_start"
    assert trace_lines[-1]["event"] == "run_end"
    assert trace_lines[-1]["detail"]["exit_class"] == ExitClass.SUCCESS.value

    seqs = [line["seq"] for line in trace_lines]
    assert seqs == list(range(1, len(seqs) + 1))

    md_text = md_path.read_text(encoding="utf-8")
    assert "Timing waterfall" in md_text


def test_second_invocation_while_locked_is_skipped_overlap(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_minimal_config(tmp_path)

    logs_dir = tmp_path / "logs"
    lock_path = logs_dir / "run.lock"
    held_lock = run_identity.RunLock(lock_path)
    held_lock.acquire()
    try:
        exit_code = main_module.main([])
        assert exit_code == EXIT_CODE_MAP[ExitClass.SKIPPED_OVERLAP]

        ledger_path = logs_dir / "run_ledger.jsonl"
        ledger_lines = ledger_path.read_text(encoding="utf-8").splitlines()
        assert len(ledger_lines) == 1
        entry = json.loads(ledger_lines[0])
        assert entry["exit_class"] == ExitClass.SKIPPED_OVERLAP.value
    finally:
        held_lock.release()


def test_stage_exception_yields_hard_failure_and_truncated_trace_ends_at_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_minimal_config(tmp_path)

    def _boom(ctx, trace):
        raise RuntimeError("simulated mid-run kill")

    broken_stages = tuple(
        (name, _boom) if name == "collection" else (name, fn) for name, fn in stages.CANONICAL_STAGES
    )
    monkeypatch.setattr(stages, "CANONICAL_STAGES", broken_stages)

    exit_code = main_module.main([])
    assert exit_code == EXIT_CODE_MAP[ExitClass.HARD_FAILURE]

    logs_dir = tmp_path / "logs"
    latest_path = logs_dir / "latest.txt"
    from pathlib import Path

    run_dir = Path(latest_path.read_text(encoding="utf-8").strip())
    trace_path = run_dir / "trace.jsonl"

    trace_lines = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    # The trace ends at the error — no stage_end, no run_end was ever written,
    # exactly as a genuine crash would leave it (RUN_TRACE_SPEC §5(b)).
    assert trace_lines[-1]["event"] == "error"
    assert "simulated mid-run kill" in trace_lines[-1]["detail"]["message"]
    assert not any(line["event"] == "run_end" for line in trace_lines)

    ledger_path = logs_dir / "run_ledger.jsonl"
    ledger_entry = json.loads(ledger_path.read_text(encoding="utf-8").splitlines()[0])
    assert ledger_entry["exit_class"] == ExitClass.HARD_FAILURE.value

    # trace.md must still render from the truncated trace.
    md_path = run_dir / "trace.md"
    assert md_path.exists()


def test_missing_config_yields_policy_stop(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # No config/ directory at all -> ConfigError at theme_load -> policy-stop.
    exit_code = main_module.main([])
    assert exit_code == EXIT_CODE_MAP[ExitClass.POLICY_STOP]


def test_render_mode_regenerates_trace_md(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_minimal_config(tmp_path)
    main_module.main([])

    logs_dir = tmp_path / "logs"
    from pathlib import Path

    run_dir = Path((logs_dir / "latest.txt").read_text(encoding="utf-8").strip())
    trace_path = run_dir / "trace.jsonl"
    md_path = run_dir / "trace.md"
    md_path.unlink()
    assert not md_path.exists()

    exit_code = main_module.main(["--render", str(trace_path)])
    assert exit_code == 0
    assert md_path.exists()
