"""Tests for hypeagent.packaging — the run pack and the digest (§12.1, §2.6)."""

from __future__ import annotations

from datetime import datetime

import yaml

from hypeagent.packaging import DegradedSourceNote, package_candidates, write_digest
from hypeagent.ranking import RankingConfig, rank
from hypeagent.store import NormalizedSignal, SpecialCategoryLexicon, Store


def _config():
    return RankingConfig(
        version=1, brand_fit_floor=0.05, top_n_per_language=3,
        half_life_hours={"spike": 6, "rising": 24, "launch-hype": 72, "evergreen-pain": 720},
        baseline_lookback_days=90, absolute_band_fallback={"hacker_news": {"low": 5, "mid": 50, "high": 200}},
        dedupe_lookback_days=30, rejection_suppression_days=14, corroboration_growth_override_families=2,
        new_angle_min_new_signals=3, corroboration_bonus=0.15,
        evidence_floor_min_candidates={"en": 1, "cs": 1}, evidence_floor_min_families={"en": 1, "cs": 1},
    )


def test_package_and_digest_zero_candidates(tmp_path):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        result = rank(
            store=store, signals=[], watch_terms_by_language={"en": ["agents"]}, hard_exclude_topics=[],
            lexicon=SpecialCategoryLexicon(terms_by_category={}), config=_config(), run_id="run1", languages=["en"],
        )
        run_dir = tmp_path / "logs" / "runs" / "run1"
        package_candidates(run_id="run1", run_dir=run_dir, store=store, ranking_result=result, languages=["en"])
        digest_path = write_digest(
            run_id="run1", run_date="2026-08-10", theme_name="hypedigitaly", run_dir=run_dir,
            ranking_result=result, degraded_sources=[], languages=["en"],
        )
        text = digest_path.read_text(encoding="utf-8")
        assert "0 passing candidates" in text
        assert "trace.md" in text
    finally:
        store.close()


def test_package_writes_scorecards_signals_and_registers_keys(tmp_path):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        normalized = NormalizedSignal(
            canonical_key="hacker_news:1", source="hacker_news", source_family="developer_technical_discourse",
            language="en", title="AI agents for sales automation launch", excerpt="AI agents for sales automation launch",
            metrics={"score": 200}, raw_author_handle="alice", near_dup_fingerprint="fp1", evidence_class="counted",
            injection_flagged=False, retrieval_time=datetime.now().astimezone(),
            canonical_link="https://news.ycombinator.com/item?id=1", domain="news.ycombinator.com", method="official API",
        )
        stored, _ = store.store_signal(normalized, run_id="run1", lexicon=SpecialCategoryLexicon(terms_by_category={}))
        assert stored

        signals = store.signals_since()
        result = rank(
            store=store, signals=signals, watch_terms_by_language={"en": ["agents", "automation", "sales"]},
            hard_exclude_topics=[], lexicon=SpecialCategoryLexicon(terms_by_category={}), config=_config(),
            run_id="run1", languages=["en"],
        )
        assert not result.zero_passing_candidates

        run_dir = tmp_path / "logs" / "runs" / "run1"
        summary = package_candidates(run_id="run1", run_dir=run_dir, store=store, ranking_result=result, languages=["en"])
        assert summary.registered_keys >= 1
        assert len(summary.scorecard_paths) >= 1
        assert len(summary.signal_paths) >= 1

        signal_doc = yaml.safe_load(summary.signal_paths[0].read_text(encoding="utf-8"))
        assert signal_doc["canonical_key"] == "hacker_news:1"
        assert signal_doc["durable"]["source"] == "hacker_news"
        assert "alice" not in yaml.safe_dump(signal_doc)

        packs = store.packs_for_key("hacker_news:1")
        assert len(packs) == 1
    finally:
        store.close()


def test_digest_shows_degraded_source_banner_and_evidence_floor_line(tmp_path):
    store = Store.open(tmp_path / "logs", tmp_path / "secrets")
    try:
        result = rank(
            store=store, signals=[], watch_terms_by_language={"en": ["agents"], "cs": ["agenti"]},
            hard_exclude_topics=[], lexicon=SpecialCategoryLexicon(terms_by_category={}), config=_config(),
            run_id="run1", languages=["en", "cs"],
        )
        run_dir = tmp_path / "logs" / "runs" / "run1"
        digest_path = write_digest(
            run_id="run1", run_date="2026-08-10", theme_name="hypedigitaly", run_dir=run_dir,
            ranking_result=result,
            degraded_sources=[DegradedSourceNote(source="product_hunt", reason="feed unavailable")],
            languages=["en", "cs"],
        )
        text = digest_path.read_text(encoding="utf-8")
        assert "product_hunt" in text
        assert "feed unavailable" in text
        assert "evidence floor" in text.lower()
        assert "not comparable" in text
    finally:
        store.close()
