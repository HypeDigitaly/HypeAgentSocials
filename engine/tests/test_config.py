"""Tests for hypeagent.config_load — fail-closed config semantics."""

from __future__ import annotations

import pytest

from hypeagent.config_load import ConfigError, load_hard_excludes, load_theme_config


def test_missing_file_raises_config_error_naming_it(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    # hard_excludes.yaml deliberately absent.
    with pytest.raises(ConfigError) as excinfo:
        load_hard_excludes(config_dir)
    assert "hard_excludes.yaml" in str(excinfo.value)


def test_empty_lists_resolve_to_resolved_empty(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "hard_excludes.yaml").write_text(
        """
hard_excludes:
  topics: []
  framings: []
  claim_types: []
  do_not_mention_entities: []
""",
        encoding="utf-8",
    )
    result = load_hard_excludes(config_dir)
    assert set(result) == {"topics", "framings", "claim_types", "do_not_mention_entities"}
    for item in result.values():
        assert item.state == "resolved-empty"
        assert item.values == []


def test_non_empty_list_resolves_to_resolved(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "hard_excludes.yaml").write_text(
        """
hard_excludes:
  topics: ["politics"]
  framings: []
  claim_types: []
  do_not_mention_entities: []
""",
        encoding="utf-8",
    )
    result = load_hard_excludes(config_dir)
    assert result["topics"].state == "resolved"
    assert result["topics"].values == ["politics"]
    assert result["framings"].state == "resolved-empty"


def test_unreadable_yaml_raises_config_error(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "hard_excludes.yaml").write_text("not: [valid: yaml: at all", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_hard_excludes(config_dir)


def test_load_theme_config_produces_a_fingerprint(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "hard_excludes.yaml").write_text(
        "hard_excludes:\n  topics: []\n  framings: []\n  claim_types: []\n  do_not_mention_entities: []\n",
        encoding="utf-8",
    )
    theme_config = load_theme_config(config_dir)
    assert theme_config.fingerprint
    assert isinstance(theme_config.fingerprint, str)


def test_missing_config_dir_raises_config_error(tmp_path):
    config_dir = tmp_path / "does_not_exist"
    with pytest.raises(ConfigError):
        load_theme_config(config_dir)
