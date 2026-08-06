"""Tests for the §2.8a cross-day dedupe resurgence rule, all three
Phase-1-gated states plus rejected/capped."""

from __future__ import annotations

from datetime import datetime, timedelta

from hypeagent.ranking import Phase1DeterministicNewAngleJudge, resolve_resurgence
from hypeagent.store import Store


def test_rising_never_generated_ranks_normally(tmp_path):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        obs = store.observe_cluster(cluster_key="c1", families=["developer_technical_discourse"], percentile=0.6, fingerprints=["f1"])
        result = resolve_resurgence(
            cluster_key="c1", observation=obs, current_families={"developer_technical_discourse"},
            current_fingerprints={"f1"}, new_angle_judge=Phase1DeterministicNewAngleJudge(),
            min_new_signals=3, rejected_at=None, rejection_suppression_days=14,
            corroboration_growth_override_families=2, now=datetime.now().astimezone(),
        )
        assert result.outcome == "normal"
    finally:
        store.close()


def test_rising_generated_with_new_angle_reenters_tagged_revisit(tmp_path):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        # Day 1: observe and mark generated.
        store.observe_cluster(cluster_key="c1", families=["developer_technical_discourse"], percentile=0.5, fingerprints=["f1"])
        store.mark_generated("c1", run_id="run1")

        # Day 3: new corroborating family + new fingerprints -> new angle.
        obs = store.observe_cluster(
            cluster_key="c1", families=["developer_technical_discourse", "launch_registries"],
            percentile=0.7, fingerprints=["f1", "f2"],
        )
        assert obs.prior_pack_state == "generated"
        result = resolve_resurgence(
            cluster_key="c1", observation=obs,
            current_families={"developer_technical_discourse", "launch_registries"},
            current_fingerprints={"f1", "f2"}, new_angle_judge=Phase1DeterministicNewAngleJudge(),
            min_new_signals=3, rejected_at=None, rejection_suppression_days=14,
            corroboration_growth_override_families=2, now=datetime.now().astimezone(),
        )
        assert result.outcome == "revisit"
        assert result.tag == "revisit: new angle"
        assert "new corroborating source family" in result.what_changed
    finally:
        store.close()


def test_rising_generated_with_nothing_new_is_suppressed(tmp_path):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        store.observe_cluster(cluster_key="c1", families=["developer_technical_discourse"], percentile=0.5, fingerprints=["f1"])
        store.mark_generated("c1", run_id="run1")

        # Day 4: same family, same fingerprint — nothing new.
        obs = store.observe_cluster(cluster_key="c1", families=["developer_technical_discourse"], percentile=0.55, fingerprints=["f1"])
        assert obs.prior_pack_state == "generated"
        result = resolve_resurgence(
            cluster_key="c1", observation=obs, current_families={"developer_technical_discourse"},
            current_fingerprints={"f1"}, new_angle_judge=Phase1DeterministicNewAngleJudge(),
            min_new_signals=3, rejected_at=None, rejection_suppression_days=14,
            corroboration_growth_override_families=2, now=datetime.now().astimezone(),
        )
        assert result.outcome == "suppressed"
        assert result.tag is None
    finally:
        store.close()


def test_new_angle_judge_unavailable_fails_closed_to_suppressed(tmp_path):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        store.observe_cluster(cluster_key="c1", families=["developer_technical_discourse"], percentile=0.5, fingerprints=["f1"])
        store.mark_generated("c1", run_id="run1")
        obs = store.observe_cluster(
            cluster_key="c1", families=["developer_technical_discourse", "launch_registries"],
            percentile=0.9, fingerprints=["f1", "f2", "f3"],
        )
        result = resolve_resurgence(
            cluster_key="c1", observation=obs, current_families={"developer_technical_discourse", "launch_registries"},
            current_fingerprints={"f1", "f2", "f3"}, new_angle_judge=None,
            min_new_signals=3, rejected_at=None, rejection_suppression_days=14,
            corroboration_growth_override_families=2, now=datetime.now().astimezone(),
        )
        assert result.outcome == "suppressed"
        assert "undetermined" in result.what_changed
    finally:
        store.close()


def test_declining_generated_is_suppressed_permanently(tmp_path):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        store.observe_cluster(cluster_key="c1", families=["developer_technical_discourse", "launch_registries"], percentile=0.8, fingerprints=["f1", "f2"])
        store.mark_generated("c1", run_id="run1")
        # Fewer families and lower percentile next time -> declining.
        obs = store.observe_cluster(cluster_key="c1", families=["developer_technical_discourse"], percentile=0.3, fingerprints=["f1"])
        assert obs.trajectory == "declining"
        result = resolve_resurgence(
            cluster_key="c1", observation=obs, current_families={"developer_technical_discourse"},
            current_fingerprints={"f1"}, new_angle_judge=Phase1DeterministicNewAngleJudge(),
            min_new_signals=3, rejected_at=None, rejection_suppression_days=14,
            corroboration_growth_override_families=2, now=datetime.now().astimezone(),
        )
        assert result.outcome == "suppressed"
        assert "permanently" in result.dedupe_status
    finally:
        store.close()


def test_rejected_topic_suppressed_within_window_then_override_on_growth(tmp_path):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        store.observe_cluster(cluster_key="c1", families=["developer_technical_discourse"], percentile=0.5, fingerprints=["f1"])
        store.mark_rejected("c1")
        rejected_at = store.get_rejected_at("c1")
        assert rejected_at is not None

        obs = store.observe_cluster(cluster_key="c1", families=["developer_technical_discourse"], percentile=0.5, fingerprints=["f1"])
        result = resolve_resurgence(
            cluster_key="c1", observation=obs, current_families={"developer_technical_discourse"},
            current_fingerprints={"f1"}, new_angle_judge=Phase1DeterministicNewAngleJudge(),
            min_new_signals=3, rejected_at=rejected_at, rejection_suppression_days=14,
            corroboration_growth_override_families=2, now=datetime.now().astimezone(),
        )
        assert result.outcome == "suppressed"

        # Corroboration grows by 2 new families -> override even inside the window.
        obs2 = store.observe_cluster(
            cluster_key="c1", families=["developer_technical_discourse", "launch_registries", "editorial_relay"],
            percentile=0.5, fingerprints=["f1"],
        )
        result2 = resolve_resurgence(
            cluster_key="c1", observation=obs2,
            current_families={"developer_technical_discourse", "launch_registries", "editorial_relay"},
            current_fingerprints={"f1"}, new_angle_judge=Phase1DeterministicNewAngleJudge(),
            min_new_signals=3, rejected_at=rejected_at, rejection_suppression_days=14,
            corroboration_growth_override_families=2, now=datetime.now().astimezone(),
        )
        assert result2.outcome == "normal"
    finally:
        store.close()
