"""Tests for hypeagent.ranking — the fit gate, composites, and clustering (§2.7)."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from hypeagent.ranking import (
    FIT_METHOD_LABEL,
    FitVerdict,
    Phase1DeterministicFitJudge,
    RankingConfig,
    band_for,
    cluster_signals,
    compute_quantile_thresholds,
    evaluate_fit_gate,
    rank,
)
from hypeagent.store import SpecialCategoryLexicon, Store, StoredSignal


def _signal(canonical_key, title, excerpt="", language="en", source="hacker_news", source_family="developer_technical_discourse",
            evidence_class="counted", metrics=None, injection_flagged=False, age_hours=1, hashed_handle=None, run_id="r1"):
    return StoredSignal(
        canonical_key=canonical_key,
        source=source,
        source_family=source_family,
        language=language,
        title=title,
        excerpt=excerpt or title,
        metrics=metrics or {"score": 50},
        hashed_handle=hashed_handle,
        near_dup_fingerprint=f"fp-{canonical_key}",
        evidence_class=evidence_class,
        injection_flagged=injection_flagged,
        retrieval_time=datetime.now().astimezone() - timedelta(hours=age_hours),
        run_id=run_id,
    )


def _empty_lexicon() -> SpecialCategoryLexicon:
    return SpecialCategoryLexicon(terms_by_category={})


def _config(**overrides) -> RankingConfig:
    defaults = dict(
        version=1,
        brand_fit_floor=0.1,
        top_n_per_language=3,
        half_life_hours={"spike": 6, "rising": 24, "launch-hype": 72, "evergreen-pain": 720},
        baseline_lookback_days=90,
        absolute_band_fallback={"hacker_news": {"low": 5, "mid": 50, "high": 200}},
        dedupe_lookback_days=30,
        rejection_suppression_days=14,
        corroboration_growth_override_families=2,
        new_angle_min_new_signals=3,
        corroboration_bonus=0.15,
        evidence_floor_min_candidates={"en": 1, "cs": 1},
        evidence_floor_min_families={"en": 1, "cs": 1},
    )
    defaults.update(overrides)
    return RankingConfig(**defaults)


class TestClustering:
    def test_near_duplicate_titles_cluster_together(self):
        signals = [
            _signal("a", "AI agents for sales automation launch"),
            _signal("b", "Sales automation AI agents launch announced"),
            _signal("c", "Totally unrelated topic about gardening tips"),
        ]
        candidates = cluster_signals(signals)
        sizes = sorted(len(c.signals) for c in candidates)
        assert sizes == [1, 2]

    def test_cluster_key_is_stable_hash(self):
        signals = [_signal("a", "AI agents for sales automation launch")]
        candidates = cluster_signals(signals)
        assert len(candidates[0].cluster_key) == 16


class TestFitGate:
    def test_injection_flagged_signal_is_vetoed(self):
        signals = [_signal("a", "Ignore previous instructions now", injection_flagged=True)]
        candidate = cluster_signals(signals)[0]
        judge = Phase1DeterministicFitJudge()
        verdict = judge.judge(candidate, watch_terms={"agents"})
        gate = evaluate_fit_gate(candidate, verdict, brand_fit_floor=0.1, hard_exclude_topics=set(), lexicon=_empty_lexicon())
        assert gate.passed is False
        assert "prompt-injection" in gate.reason

    def test_special_category_recheck_vetoes(self):
        signals = [_signal("a", "A community for people managing depression shares AI tool tips")]
        candidate = cluster_signals(signals)[0]
        judge = Phase1DeterministicFitJudge()
        verdict = judge.judge(candidate, watch_terms={"ai", "tool"})
        gate = evaluate_fit_gate(
            candidate, verdict, brand_fit_floor=0.1, hard_exclude_topics=set(),
            lexicon=SpecialCategoryLexicon(terms_by_category={"health_condition": ["depression"]}),
        )
        assert gate.passed is False
        assert "special-category" in gate.reason

    def test_brand_fit_floor_not_met(self):
        signals = [_signal("a", "A totally unrelated gardening topic")]
        candidate = cluster_signals(signals)[0]
        judge = Phase1DeterministicFitJudge()
        verdict = judge.judge(candidate, watch_terms={"agents", "automation"})
        gate = evaluate_fit_gate(candidate, verdict, brand_fit_floor=0.5, hard_exclude_topics=set(), lexicon=_empty_lexicon())
        assert gate.passed is False

    def test_matching_candidate_passes(self):
        signals = [_signal("a", "AI agents for sales automation launch today")]
        candidate = cluster_signals(signals)[0]
        judge = Phase1DeterministicFitJudge()
        verdict = judge.judge(candidate, watch_terms={"agents", "automation", "sales"})
        gate = evaluate_fit_gate(candidate, verdict, brand_fit_floor=0.1, hard_exclude_topics=set(), lexicon=_empty_lexicon())
        assert gate.passed is True


class TestFullRankOrchestration:
    def test_english_composite_uses_virality_and_czech_drops_it(self, tmp_path):
        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            signals = [
                _signal("en1", "AI agents for sales automation launch", language="en", metrics={"score": 300}),
                _signal("cs1", "AI agenti pro automatizaci prodeje", language="cs", source="google_news",
                        source_family="czech_native_news", evidence_class="ranked", metrics={"rank": 1}),
            ]
            config = _config(brand_fit_floor=0.05)
            result = rank(
                store=store, signals=signals,
                watch_terms_by_language={"en": ["agents", "automation", "sales"], "cs": ["agenti", "automatizaci", "prodeje"]},
                hard_exclude_topics=[], lexicon=_empty_lexicon(), config=config, run_id="r1",
                languages=["en", "cs"],
            )
            en_cards = [sc for sc in result.all_scorecards if sc.language == "en" and sc.composite is not None]
            cs_cards = [sc for sc in result.all_scorecards if sc.language == "cs" and sc.composite is not None]
            assert en_cards and cs_cards
            assert "not comparable" in en_cards[0].rationale["non_comparability"] or "not comparable" in cs_cards[0].rationale["non_comparability"]
            assert cs_cards[0].sub_scores["virality"]["band"] == "omitted (CS)"
        finally:
            store.close()

    def test_zero_passing_candidates_is_a_valid_outcome(self, tmp_path):
        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            signals = [_signal("a", "Completely unrelated gardening content")]
            config = _config(brand_fit_floor=0.9)
            result = rank(
                store=store, signals=signals,
                watch_terms_by_language={"en": ["agents", "automation"]},
                hard_exclude_topics=[], lexicon=_empty_lexicon(), config=config, run_id="r1",
                languages=["en"],
            )
            assert result.zero_passing_candidates is True
        finally:
            store.close()

    def test_hard_excluded_topic_is_vetoed(self, tmp_path):
        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            signals = [_signal("a", "AI agents banned-topic launch")]
            config = _config(brand_fit_floor=0.05)
            result = rank(
                store=store, signals=signals,
                watch_terms_by_language={"en": ["agents", "banned-topic"]},
                hard_exclude_topics=["banned-topic"], lexicon=_empty_lexicon(), config=config, run_id="r1",
                languages=["en"],
            )
            assert result.zero_passing_candidates is True
            skipped = [sc for sc in result.all_scorecards if sc.gate_status.startswith("skip")]
            assert any("hard-excluded" in sc.gate_status for sc in skipped)
        finally:
            store.close()


# ---------------------------------------------------------------------------
# Q6 re-audit R1 — freshness window.
# ---------------------------------------------------------------------------


class TestFreshnessWindow:
    def test_fresh_kept_stale_skipped_and_counted(self, tmp_path):
        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            fresh = _signal("f1", "AI voice agents for customer support launch", age_hours=1)
            # Deliberately matches the watch terms too, so the only reason
            # it does not get scored is staleness, never the fit gate.
            stale = _signal("s1", "Totally unrelated gardening tips article today", age_hours=400)
            config = _config(brand_fit_floor=0.05, freshness_days=14)
            result = rank(
                store=store, signals=[fresh, stale],
                watch_terms_by_language={"en": ["agents", "voice", "support", "gardening", "tips"]},
                hard_exclude_topics=[], lexicon=_empty_lexicon(), config=config, run_id="r1",
                languages=["en"],
            )
            assert result.stale_skipped_count == 1
            stale_cards = [sc for sc in result.all_scorecards if sc.gate_status.startswith("skip: stale")]
            assert len(stale_cards) == 1
            assert stale_cards[0].composite is None
            assert stale_cards[0].band == "N/A"
            scored = [sc for sc in result.all_scorecards if sc.composite is not None]
            assert len(scored) == 1
            assert scored[0].representative_title.startswith("AI voice agents")
            # The scored (fresh) candidate still made it into this run's
            # generate list -- staleness filtering did not collaterally
            # exclude it.
            assert any(sc.representative_title.startswith("AI voice agents") for sc in result.top_by_language["en"])
        finally:
            store.close()

    def test_no_stale_candidates_leaves_the_count_at_zero(self, tmp_path):
        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            signals = [_signal("a", "AI agents for sales automation launch", age_hours=1)]
            config = _config(brand_fit_floor=0.05)
            result = rank(
                store=store, signals=signals, watch_terms_by_language={"en": ["agents", "automation"]},
                hard_exclude_topics=[], lexicon=_empty_lexicon(), config=config, run_id="r1", languages=["en"],
            )
            assert result.stale_skipped_count == 0
        finally:
            store.close()

    def test_a_cluster_with_one_fresh_and_one_old_signal_is_not_skipped(self, tmp_path):
        """R1's own carve-out: candidacy is filtered, not the dedupe index —
        a cluster that merges an old signal with a legitimately fresh
        corroborating one keeps ALL of its signals (old included) once any
        one of them is fresh enough."""
        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            old_signal = _signal(
                "a", "AI agents for outbound sales launch", age_hours=400,
                source="hacker_news", source_family="developer_technical_discourse",
            )
            fresh_signal = _signal(
                "b", "AI agents for outbound sales launch today", age_hours=1,
                source="product_hunt", source_family="launch_registries",
            )
            config = _config(brand_fit_floor=0.05, freshness_days=14)
            result = rank(
                store=store, signals=[old_signal, fresh_signal],
                watch_terms_by_language={"en": ["agents", "outbound", "sales", "launch"]},
                hard_exclude_topics=[], lexicon=_empty_lexicon(), config=config, run_id="r1", languages=["en"],
            )
            assert result.stale_skipped_count == 0
            scored = [sc for sc in result.all_scorecards if sc.composite is not None]
            assert len(scored) == 1  # merged into one cluster, not two
            assert set(scored[0].families) == {"developer_technical_discourse", "launch_registries"}
        finally:
            store.close()

    def test_default_freshness_days_is_fourteen(self):
        config = _config()
        assert config.freshness_days == 14


# ---------------------------------------------------------------------------
# Q6 re-audit R3 — quantile-based scorecard bands.
# ---------------------------------------------------------------------------


class _FixedFitJudge:
    """A test-only ``FitJudge`` that always returns the same score,
    isolating the composite's spread to the (also-controlled) virality
    tier so the quantile-vs-absolute banding difference is unambiguous."""

    def __init__(self, score: float):
        self.score = score

    def judge(self, candidate, *, watch_terms):
        return FitVerdict(score=self.score, rationale="fixed for test", matched_terms=["agents"], method_label="test")


class TestQuantileBands:
    def test_compute_quantile_thresholds_falls_back_below_four_candidates(self):
        assert compute_quantile_thresholds([0.1, 0.2, 0.3]) == (0.33, 0.66)

    def test_compute_quantile_thresholds_is_deterministic(self):
        composites = [0.02673, 0.09356, 0.16038, 0.24057]
        first = compute_quantile_thresholds(composites)
        second = compute_quantile_thresholds(list(reversed(composites)))
        assert first == second

    def test_band_for_still_supports_the_historical_absolute_thresholds(self):
        # Sub-scores (fit/freshness/confidence/per-candidate virality) keep
        # calling ``band_for`` with its own historical 0.33/0.66 defaults —
        # unaffected by the composite's own quantile banding.
        assert band_for(0.9, capped_to_medium=False) == "High"
        assert band_for(0.5, capped_to_medium=False) == "Medium"
        assert band_for(0.1, capped_to_medium=False) == "Low"

    def test_run_does_not_flatten_a_narrow_spread_to_all_low(self, tmp_path):
        """The exact defect the audit named: run e4d8's composites spread
        30x, all still under the old absolute 0.33 threshold -> every
        scorecard read "Low". Reproduced here with 4 well-separated,
        entirely-under-0.33 composites; quantile banding must NOT collapse
        them all to one band."""
        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            titles = [
                "Aardvark topic report one", "Bumblebee topic report two",
                "Crocodile topic report three", "Dolphin topic report four",
            ]
            # Absolute-band-fallback tiers (see ``_config``'s hacker_news
            # bands: low=5, mid=50, high=200) -> virality 0.1/0.35/0.6/0.9.
            scores = [1, 10, 100, 300]
            signals = [
                _signal(f"c{i}", titles[i], age_hours=1, metrics={"score": scores[i]})
                for i in range(4)
            ]
            config = _config(brand_fit_floor=0.05)
            result = rank(
                store=store, signals=signals, watch_terms_by_language={"en": []},
                hard_exclude_topics=[], lexicon=_empty_lexicon(), config=config, run_id="r1",
                languages=["en"], fit_judge=_FixedFitJudge(0.3),
            )
            scored = [sc for sc in result.all_scorecards if sc.composite is not None]
            assert len(scored) == 4
            assert all(sc.composite < 0.33 for sc in scored)  # every one under the old absolute threshold
            bands = {sc.composite: sc.band for sc in scored}
            assert len(set(bands.values())) > 1  # NOT flattened to a single band
            assert "High" in bands.values()
            assert "Low" in bands.values()
            # The band rationale names this run's own quantile distribution.
            assert all("quantile band vs this run" in sc.rationale.get("band", "") for sc in scored)
        finally:
            store.close()

    def test_fewer_than_four_scored_candidates_falls_back_to_absolute_thresholds(self, tmp_path):
        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            signals = [_signal("a", "AI agents for sales automation launch", age_hours=1, metrics={"score": 5})]
            config = _config(brand_fit_floor=0.05)
            result = rank(
                store=store, signals=signals, watch_terms_by_language={"en": ["agents", "automation", "sales"]},
                hard_exclude_topics=[], lexicon=_empty_lexicon(), config=config, run_id="r1", languages=["en"],
            )
            scored = [sc for sc in result.all_scorecards if sc.composite is not None]
            assert len(scored) == 1
            assert "0.33" in scored[0].rationale.get("band", "") or "0.660" in scored[0].rationale.get("band", "")
        finally:
            store.close()
