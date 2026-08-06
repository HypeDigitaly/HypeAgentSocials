"""Tests for hypeagent.brand_truth (§6.3-§6.6, goal-scoped M3)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from hypeagent import brand_truth
from hypeagent.config_load import ConfigError

_BRAND_FACTS_YAML = """
identity:
  legal_name: Test Co
  source: test fixture
capabilities:
  positive:
    - id: cap-test
      en: AI chatbots and automation for businesses
      source: test fixture
  negative:
    - No physical products
icp:
  - id: icp-test
    en: Small businesses wanting AI automation
    source: test fixture
cta_set:
  - id: cta-test
    class: content
    en: Learn more
pricing_policy:
  policy: prices-never-stated
  rationale: test fixture
hard_excludes_ref: config/hard_excludes.yaml
spin_notes: {}
"""


def _write_brand_facts(config_dir: Path, text: str = _BRAND_FACTS_YAML) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "brand_facts.yaml").write_text(text, encoding="utf-8")


def _write_snapshot(config_dir: Path, *, filename: str, taken_at: str, max_age_days: int = 30, snapshot_id: str = "snap-1") -> None:
    snapshots_dir = config_dir / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    (snapshots_dir / filename).write_text(
        "meta:\n"
        f"  snapshot_id: {snapshot_id}\n"
        f"  taken_at: \"{taken_at}\"\n"
        f"  max_age_days: {max_age_days}\n"
        "claims:\n"
        "  - claim_key: test claim\n"
        "    notion_row_id: row-1\n"
        "    category: metric\n"
        "    behavior: citovat\n"
        "    text_cs: \"35 095 AI odpovědí\"\n"
        "    canonical_source: https://example.com\n"
        "    verified: \"2026-08-01\"\n",
        encoding="utf-8",
    )


class TestLoadBrandFacts:
    def test_loads_valid_brand_facts(self, tmp_path):
        _write_brand_facts(tmp_path)
        facts = brand_truth.load_brand_facts(tmp_path)
        assert facts.identity["legal_name"] == "Test Co"
        assert facts.icp[0].id == "icp-test"
        assert facts.pricing_policy == "prices-never-stated"

    def test_missing_file_fails_closed(self, tmp_path):
        with pytest.raises(ConfigError):
            brand_truth.load_brand_facts(tmp_path)

    def test_empty_icp_fails_closed(self, tmp_path):
        text = _BRAND_FACTS_YAML.replace(
            "icp:\n  - id: icp-test\n    en: Small businesses wanting AI automation\n    source: test fixture\n",
            "icp: []\n",
        )
        _write_brand_facts(tmp_path, text)
        with pytest.raises(ConfigError, match="icp"):
            brand_truth.load_brand_facts(tmp_path)


class TestClaimSnapshotLoader:
    def test_picks_latest_dated_snapshot(self, tmp_path):
        _write_snapshot(tmp_path, filename="claim_ledger_snapshot_2026-01-01.yaml", taken_at="2026-01-01", snapshot_id="old")
        _write_snapshot(tmp_path, filename="claim_ledger_snapshot_2026-08-07.yaml", taken_at="2026-08-07", snapshot_id="new")
        snapshot = brand_truth.load_claim_snapshot(tmp_path / "snapshots")
        assert snapshot.snapshot_id == "new"

    def test_no_snapshot_fails_closed(self, tmp_path):
        (tmp_path / "snapshots").mkdir(parents=True, exist_ok=True)
        with pytest.raises(ConfigError, match="could not be read"):
            brand_truth.load_claim_snapshot(tmp_path / "snapshots")


class TestResolveBrandTruth:
    def test_fresh_snapshot_allows_copy(self, tmp_path):
        _write_brand_facts(tmp_path)
        _write_snapshot(tmp_path, filename="claim_ledger_snapshot_2026-08-01.yaml", taken_at="2026-08-01", max_age_days=30)
        panel = brand_truth.resolve_brand_truth(tmp_path, now=date(2026, 8, 10))
        assert panel.band == "fresh"
        assert panel.copy_allowed is True
        assert panel.degrade_reason is None

    def test_stale_snapshot_degrades_and_refuses_copy(self, tmp_path):
        _write_brand_facts(tmp_path)
        _write_snapshot(tmp_path, filename="claim_ledger_snapshot_2026-01-01.yaml", taken_at="2026-01-01", max_age_days=30)
        panel = brand_truth.resolve_brand_truth(tmp_path, now=date(2026, 8, 10))
        assert panel.band == "stale"
        assert panel.copy_allowed is False
        assert "stale" not in "" or panel.degrade_reason is not None
        assert "research-only" in panel.degrade_reason
        assert "refuses" in panel.degrade_reason

    def test_panel_carries_snapshot_id_and_fact_classes(self, tmp_path):
        _write_brand_facts(tmp_path)
        _write_snapshot(tmp_path, filename="claim_ledger_snapshot_2026-08-01.yaml", taken_at="2026-08-01", snapshot_id="cisla-a-sliby-test")
        panel = brand_truth.resolve_brand_truth(tmp_path, now=date(2026, 8, 5))
        assert panel.snapshot.snapshot_id == "cisla-a-sliby-test"
        assert "F-D icp" in panel.fact_classes_loaded
        yaml_dict = panel.to_yaml_dict()
        assert yaml_dict["snapshot_id"] == "cisla-a-sliby-test"
