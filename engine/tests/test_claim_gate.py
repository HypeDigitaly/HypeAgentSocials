"""Tests for hypeagent.claim_gate — the deterministic half of the claim
gate (§14.3, §14.1a, §14.6)."""

from __future__ import annotations

from pathlib import Path

from hypeagent.brand_truth import ClaimEntry, ClaimSnapshot
from hypeagent.claim_gate import run_claim_gate
from hypeagent.config_load import resolve_list

DISCLOSURE = "[AI-generated content]"


def _snapshot(claims: list[ClaimEntry] | None = None) -> ClaimSnapshot:
    return ClaimSnapshot(
        snapshot_id="test-snap", taken_at="2026-08-01", max_age_days=30,
        claims=claims or [], path=Path("config/snapshots/claim_ledger_snapshot_2026-08-01.yaml"),
    )


def _claim(**overrides) -> ClaimEntry:
    defaults = dict(
        claim_key="case study answers", notion_row_id="row-1", category="metric", behavior="citovat",
        text_cs="35 095 AI odpovědí z 5 krajů", canonical_source="https://example.com", verified="2026-08-01",
        qualification=None, note=None,
    )
    defaults.update(overrides)
    return ClaimEntry(**defaults)


def _hard_excludes(entities: list[str] | None = None) -> dict:
    return {"do_not_mention_entities": resolve_list("do_not_mention_entities", entities or [])}


class TestPriceAlwaysBlocked:
    def test_kc_price_blocked_even_if_it_matches_a_snapshot_number(self):
        claim = _claim(text_cs="Starter: 5 000 Kč/měsíc")
        snapshot = _snapshot([claim])
        verdict = run_claim_gate(
            headline="Starter plan", caption=f"Only 5 000 Kč/month. {DISCLOSURE}", image_brief="",
            snapshot=snapshot,
        )
        assert verdict.verdict == "blocked"
        assert any(s.kind == "price" for s in verdict.failing_spans)

    def test_dollar_price_blocked(self):
        snapshot = _snapshot([])
        verdict = run_claim_gate(headline="", caption=f"Just $99/month. {DISCLOSURE}", image_brief="", snapshot=snapshot)
        assert verdict.verdict == "blocked"
        assert any(s.kind == "price" for s in verdict.failing_spans)


class TestNumberMatching:
    def test_unmatched_number_blocked_with_named_span(self):
        snapshot = _snapshot([])
        verdict = run_claim_gate(
            headline="500 businesses trust us", caption=f"Great results. {DISCLOSURE}", image_brief="", snapshot=snapshot,
        )
        assert verdict.verdict == "blocked"
        number_spans = [s for s in verdict.failing_spans if s.kind == "number"]
        assert number_spans
        assert "500" in number_spans[0].text

    def test_matched_claim_passes(self):
        claim = _claim(behavior="citovat", qualification=None)
        snapshot = _snapshot([claim])
        verdict = run_claim_gate(
            headline="35,095 AI answers delivered", caption=f"See the case study. {DISCLOSURE}", image_brief="",
            snapshot=snapshot,
        )
        assert verdict.verdict == "pass"

    def test_kvalifikovat_without_qualification_blocked(self):
        claim = _claim(
            behavior="kvalifikovat",
            text_cs="35 095 AI odpovědí z 5 krajů, období leden–červenec 2025",
            qualification="Vždy uvést období (leden–červenec 2025) a že jde o source-reported data",
        )
        snapshot = _snapshot([claim])
        verdict = run_claim_gate(
            headline="35,095 AI answers delivered", caption=f"Amazing results. {DISCLOSURE}", image_brief="",
            snapshot=snapshot,
        )
        assert verdict.verdict == "blocked"
        assert any("qualification" in s.reason for s in verdict.failing_spans)

    def test_kvalifikovat_with_qualification_present_passes(self):
        claim = _claim(
            behavior="kvalifikovat",
            text_cs="35 095 AI odpovědí z 5 krajů, období leden–červenec 2025",
            qualification="Vždy uvést období (leden–červenec 2025) a že jde o source-reported data",
        )
        snapshot = _snapshot([claim])
        verdict = run_claim_gate(
            headline="35,095 AI answers, Jan-Jul 2025",
            caption=f"Source-reported data from 2025. {DISCLOSURE}", image_brief="",
            snapshot=snapshot,
        )
        assert verdict.verdict == "pass"


class TestProhibitedShapes:
    def test_superlative_blocked(self):
        snapshot = _snapshot([])
        verdict = run_claim_gate(headline="The best AI chatbot", caption=DISCLOSURE, image_brief="", snapshot=snapshot)
        assert verdict.verdict == "blocked"
        assert any(s.kind == "superlative" for s in verdict.failing_spans)

    def test_outcome_promise_blocked(self):
        snapshot = _snapshot([])
        verdict = run_claim_gate(
            headline="", caption=f"This will double your leads. {DISCLOSURE}", image_brief="", snapshot=snapshot,
        )
        assert verdict.verdict == "blocked"
        assert any(s.kind == "outcome_promise" for s in verdict.failing_spans)

    def test_therapeutic_lexicon_blocked(self):
        snapshot = _snapshot([])
        verdict = run_claim_gate(
            headline="", caption=f"Our AI can cure your marketing problems. {DISCLOSURE}", image_brief="", snapshot=snapshot,
        )
        assert verdict.verdict == "blocked"
        assert any(s.kind == "therapeutic" for s in verdict.failing_spans)

    def test_ragus_current_mention_blocked(self):
        snapshot = _snapshot([])
        verdict = run_claim_gate(
            headline="", caption=f"Powered by RAGus. {DISCLOSURE}", image_brief="", snapshot=snapshot,
        )
        assert verdict.verdict == "blocked"
        assert any(s.kind == "entity" for s in verdict.failing_spans)

    def test_hard_excludes_entity_blocked(self):
        snapshot = _snapshot([])
        verdict = run_claim_gate(
            headline="", caption=f"As seen with Acme Corp. {DISCLOSURE}", image_brief="", snapshot=snapshot,
            hard_excludes=_hard_excludes(["Acme Corp"]),
        )
        assert verdict.verdict == "blocked"
        assert any(s.kind == "entity" for s in verdict.failing_spans)


class TestDisclosure:
    def test_missing_disclosure_blocked(self):
        snapshot = _snapshot([])
        verdict = run_claim_gate(headline="Clean copy", caption="No disclosure here at all.", image_brief="", snapshot=snapshot)
        assert verdict.verdict == "blocked"
        assert any(s.kind == "disclosure_missing" for s in verdict.failing_spans)

    def test_disclosure_present_does_not_block_on_its_own(self):
        snapshot = _snapshot([])
        verdict = run_claim_gate(headline="Clean copy", caption=f"Just fine copy. {DISCLOSURE}", image_brief="", snapshot=snapshot)
        assert verdict.verdict == "pass"


class TestCleanCopyPasses:
    def test_no_claim_shaped_strings_passes(self):
        snapshot = _snapshot([])
        verdict = run_claim_gate(
            headline="AI agents are changing outbound sales",
            caption=f"See how small businesses use AI chatbots. Learn more at example.com. {DISCLOSURE}",
            image_brief="A calm office desk with a laptop, no people, no product shots.",
            snapshot=snapshot,
        )
        assert verdict.verdict == "pass"
        assert verdict.failing_spans == []
