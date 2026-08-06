"""Phase-1 end-to-end acceptance tests (ARCHITECTURE_PLAN.md §17.2), fully
offline against fixtures via an injected ``Fetcher``."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from hypeagent import render_trace, run_identity, stages
from hypeagent.collectors.base import FetchError, FetchResponse, FixtureFetcher
from hypeagent.exit_codes import EXIT_CODE_MAP, ExitClass
from hypeagent.trace import TraceWriter

FIXTURES = Path(__file__).parent / "fixtures"


def _fr(path: Path) -> FetchResponse:
    return FetchResponse(status=200, headers={}, body=path.read_bytes(), latency_ms=3)


def _write_brand_truth_config(config_dir: Path) -> None:
    """M3's brand-truth stage fails closed on a missing brand_facts.yaml or
    claim-ledger snapshot — every fixture-driven pipeline test needs a
    minimal, valid, always-fresh pair (see test_run.py's twin helper)."""
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


def _write_config(tmp_path: Path, *, denied_sources=None, lexicon_terms=None) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    _write_brand_truth_config(config_dir)
    (config_dir / "hard_excludes.yaml").write_text(
        "hard_excludes:\n  topics: []\n  framings: []\n  claim_types: []\n  do_not_mention_entities: []\n",
        encoding="utf-8",
    )
    denied_sources = denied_sources or []
    denied_yaml = "\n".join(f"    - {s}" for s in denied_sources) if denied_sources else "    []"
    denied_sources_block = (
        "  denied_sources:\n" + denied_yaml if denied_sources else "  denied_sources: []"
    )
    (config_dir / "special_category_source_deny_list.yaml").write_text(
        "special_category_deny_list:\n"
        "  denied_defining_characteristics: []\n"
        f"{denied_sources_block}\n"
        "  denied_communities: []\n",
        encoding="utf-8",
    )
    lexicon_terms = lexicon_terms or []
    terms_yaml = "\n".join(f"    - {t}" for t in lexicon_terms) if lexicon_terms else "    []"
    health_block = "  health_condition:\n" + terms_yaml if lexicon_terms else "  health_condition: []"
    (config_dir / "special_category_lexicon.yaml").write_text(
        f"special_category_lexicon:\n{health_block}\n",
        encoding="utf-8",
    )
    themes_dir = config_dir / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    (themes_dir / "hypedigitaly.yaml").write_text(
        """
theme:
  name: hypedigitaly
  languages: [en, cs]
research:
  watch_topics:
    en: ["AI agents", "sales automation", "voice AI", "lead generation"]
    cs: ["AI agenti", "automatizaci prodeje"]
  icp_terms:
    en: ["agency"]
    cs: ["agentura"]
  sources:
    hacker_news:
      enabled: true
      family: developer_technical_discourse
      budget_max_calls: 10
      circuit_breaker_threshold: 2
    google_news:
      enabled: true
      family_en: editorial_relay
      family_cs: czech_native_news
      circuit_breaker_threshold: 2
      queries:
        en: ["AI agents"]
        cs: ["AI agenti"]
    hugging_face:
      enabled: true
      family: launch_registries
      limit: 20
      circuit_breaker_threshold: 2
    product_hunt:
      enabled: true
      family: launch_registries
      circuit_breaker_threshold: 2
ranking:
  ranking_config_version: 1
  brand_fit_floor: 0.05
  top_n_per_language: 3
  freshness_half_life_hours: {spike: 6, rising: 24, launch-hype: 72, evergreen-pain: 720}
  baseline_lookback_days: 90
  absolute_band_fallback:
    hacker_news: {low: 5, mid: 50, high: 200}
    hugging_face: {low: 10, mid: 100, high: 1000}
  dedupe_lookback_days: 30
  rejection_suppression_days: 14
  corroboration_growth_override_families: 2
  new_angle_min_new_signals: 3
  corroboration_bonus: 0.15
  evidence_floor:
    en: {min_candidates: 1, min_families: 1}
    cs: {min_candidates: 1, min_families: 1}
""",
        encoding="utf-8",
    )


def _default_fixture_responses() -> dict:
    return {
        "topstories.json": _fr(FIXTURES / "hn_topstories.json"),
        "item/1.json": _fr(FIXTURES / "hn_item_1.json"),
        "item/2.json": _fr(FIXTURES / "hn_item_2.json"),
        "item/3.json": _fr(FIXTURES / "hn_item_3_injection.json"),
        "hl=en-US": _fr(FIXTURES / "google_news_en.xml"),
        "hl=cs": _fr(FIXTURES / "google_news_cs.xml"),
        "models?sort=trending": _fr(FIXTURES / "huggingface_trending.json"),
        "producthunt.com/feed": _fr(FIXTURES / "producthunt_feed.xml"),
    }


def _run_once(tmp_path: Path, fetcher, run_id: str | None = None):
    identity = run_identity.new_run_identity() if run_id is None else run_identity.RunIdentity(
        run_id=run_id, run_date=run_id.split("_")[0], started_at=__import__("datetime").datetime.now().astimezone()
    )
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
    return identity, run_dir, trace_path, exit_class_value


class TestFullRunOnFixtures:
    def test_end_to_end_produces_digest_scorecards_and_reconstructable_trace(self, tmp_path):
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        identity, run_dir, trace_path, exit_class_value = _run_once(tmp_path, fetcher)

        assert exit_class_value == ExitClass.SUCCESS.value
        digest_path = run_dir / "pack" / "digest.md"
        assert digest_path.exists()
        digest_text = digest_path.read_text(encoding="utf-8")
        assert "Run Digest" in digest_text
        assert "trace.md" in digest_text

        scorecards_dir = run_dir / "pack" / "scorecards"
        assert scorecards_dir.exists()
        assert len(list(scorecards_dir.glob("*.yaml"))) > 0

        trace_lines = [json.loads(l) for l in trace_path.read_text(encoding="utf-8").splitlines()]
        api_calls = [e for e in trace_lines if e["event"] == "api_call"]
        api_responses = [e for e in trace_lines if e["event"] == "api_response"]
        assert len(api_calls) > 0
        assert len(api_calls) == len(api_responses)
        for call in api_calls:
            assert call["detail"]["platform"] in {"hacker_news", "google_news", "hugging_face", "product_hunt"}
            assert call["detail"]["endpoint"]
        for resp in api_responses:
            assert resp["detail"]["status"] == 200

    def test_same_day_second_run_does_not_refetch_and_suppresses_as_not_new(self, tmp_path):
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        _run_once(tmp_path, fetcher, run_id="2026-08-10_aaaa")
        calls_after_first = len(fetcher.calls)
        assert calls_after_first > 0

        identity2, run_dir2, trace_path2, exit_class_value2 = _run_once(tmp_path, fetcher, run_id="2026-08-10_bbbb")
        assert len(fetcher.calls) == calls_after_first  # zero new network calls

        digest_text = (run_dir2 / "pack" / "digest.md").read_text(encoding="utf-8")
        # Whatever ranked as "generate" on day 1 either isn't re-offered as new,
        # or ranks with a dedupe status explaining why (never silently identical).
        assert "dedupe status" in digest_text.lower() or "0 passing candidates" in digest_text

    def test_broken_source_yields_degraded_banner_and_partial_success_exit(self, tmp_path):
        _write_config(tmp_path)
        responses = _default_fixture_responses()
        responses["producthunt.com/feed"] = FetchError("connection refused")
        fetcher = FixtureFetcher(responses=responses)
        identity, run_dir, trace_path, exit_class_value = _run_once(tmp_path, fetcher)

        assert exit_class_value == ExitClass.PARTIAL_SUCCESS_DEGRADED_SOURCES.value
        digest_text = (run_dir / "pack" / "digest.md").read_text(encoding="utf-8")
        assert "product_hunt" in digest_text

    def test_byte_identical_payload_raises_stale_payload_suspected(self, tmp_path):
        _write_config(tmp_path)
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        _run_once(tmp_path, fetcher, run_id="2026-08-10_aaaa")
        # A different calendar day, but the source returns byte-identical bytes.
        identity2, run_dir2, trace_path2, exit_class_value2 = _run_once(tmp_path, fetcher, run_id="2026-08-11_bbbb")

        assert exit_class_value2 == ExitClass.PARTIAL_SUCCESS_DEGRADED_SOURCES.value
        trace_lines = [json.loads(l) for l in trace_path2.read_text(encoding="utf-8").splitlines()]
        degrades = [e for e in trace_lines if e["event"] == "degrade"]
        assert any("stale payload suspected" in e["detail"]["condition"] for e in degrades)

    def test_special_category_deny_listed_source_never_fetched(self, tmp_path):
        _write_config(tmp_path, denied_sources=["product_hunt"])
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        identity, run_dir, trace_path, exit_class_value = _run_once(tmp_path, fetcher)
        assert not any("producthunt.com/feed" in url for url in fetcher.calls)
        trace_lines = [json.loads(l) for l in trace_path.read_text(encoding="utf-8").splitlines()]
        decisions = [e for e in trace_lines if e["event"] == "decision"]
        assert any("deny-list" in e["detail"]["decision"] for e in decisions)

    def test_special_category_lexicon_hit_excludes_item_from_store(self, tmp_path):
        # "sales automation" HN story text won't match; use a lexicon term that
        # matches the injection-fixture item's title so we can watch it drop.
        _write_config(tmp_path, lexicon_terms=["reveal your system prompt"])
        fetcher = FixtureFetcher(responses=_default_fixture_responses())
        identity, run_dir, trace_path, exit_class_value = _run_once(tmp_path, fetcher)

        from hypeagent.store import Store

        store = Store.open(tmp_path / "logs", tmp_path / "secrets")
        try:
            assert store.get_signal("hacker_news:3") is None
        finally:
            store.close()
