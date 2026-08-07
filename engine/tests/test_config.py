"""Tests for hypeagent.config_load — fail-closed config semantics."""

from __future__ import annotations

import pytest

from hypeagent.config_load import (
    ConfigError,
    find_dotenv,
    load_hard_excludes,
    load_theme_config,
    parse_env_file,
    resolve_secret,
)


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


# ---------------------------------------------------------------------------
# W8-9 Phase 1: .env loader / resolve_secret (real environment variable >
# .env > legacy secrets/<file>.key, deprecated but still working).
# ---------------------------------------------------------------------------


class TestParseEnvFile:
    def test_parses_key_value_lines(self, tmp_path):
        env_path = tmp_path / ".env"
        env_path.write_text("FOO=bar\nBAZ=qux\n", encoding="utf-8")
        assert parse_env_file(env_path) == {"FOO": "bar", "BAZ": "qux"}

    def test_ignores_blank_lines_and_comments(self, tmp_path):
        env_path = tmp_path / ".env"
        env_path.write_text(
            "\n# a comment\nFOO=bar\n   \n# VIRLO_API_KEY=should_be_ignored\nBAZ=qux\n",
            encoding="utf-8",
        )
        assert parse_env_file(env_path) == {"FOO": "bar", "BAZ": "qux"}

    def test_strips_surrounding_whitespace_around_key_and_value(self, tmp_path):
        env_path = tmp_path / ".env"
        env_path.write_text("  FOO  =  bar  \n", encoding="utf-8")
        assert parse_env_file(env_path) == {"FOO": "bar"}

    def test_missing_file_returns_empty_dict_never_raises(self, tmp_path):
        assert parse_env_file(tmp_path / "no_such.env") == {}

    def test_empty_value_is_kept_as_empty_string(self, tmp_path):
        env_path = tmp_path / ".env"
        env_path.write_text("FOO=\n", encoding="utf-8")
        assert parse_env_file(env_path) == {"FOO": ""}

    def test_line_without_equals_sign_is_skipped(self, tmp_path):
        env_path = tmp_path / ".env"
        env_path.write_text("not_a_valid_line\nFOO=bar\n", encoding="utf-8")
        assert parse_env_file(env_path) == {"FOO": "bar"}


class TestFindDotenv:
    def test_finds_dotenv_at_config_dir_parent(self, tmp_path):
        (tmp_path / ".env").write_text("FOO=bar\n", encoding="utf-8")
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        found = find_dotenv(config_dir)
        assert found == tmp_path / ".env"

    def test_returns_none_when_nothing_found(self, tmp_path):
        config_dir = tmp_path / "isolated" / "config"
        config_dir.mkdir(parents=True)
        # tmp_path's own tree never contains a stray .env in a test run.
        assert find_dotenv(config_dir) is None

    def test_explicit_path_wins_outright_when_it_exists(self, tmp_path):
        (tmp_path / ".env").write_text("FOO=bar\n", encoding="utf-8")
        explicit = tmp_path / "explicit" / ".env"
        explicit.parent.mkdir(parents=True)
        explicit.write_text("FOO=explicit\n", encoding="utf-8")
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        assert find_dotenv(config_dir, explicit_path=explicit) == explicit

    def test_explicit_path_that_does_not_exist_resolves_to_none(self, tmp_path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        assert find_dotenv(config_dir, explicit_path=tmp_path / "nope" / ".env") is None


class TestResolveSecret:
    def _config_dir(self, tmp_path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        return config_dir

    def test_environment_wins_over_dotenv_and_legacy_file(self, tmp_path, monkeypatch):
        config_dir = self._config_dir(tmp_path)
        (tmp_path / ".env").write_text("MY_SECRET=from_dotenv\n", encoding="utf-8")
        legacy_path = tmp_path / "secrets" / "my.key"
        legacy_path.parent.mkdir(parents=True)
        legacy_path.write_text("from_legacy_file", encoding="utf-8")
        monkeypatch.setenv("MY_SECRET", "from_environment")

        value, source = resolve_secret("MY_SECRET", config_dir=config_dir, legacy_path=legacy_path)
        assert (value, source) == ("from_environment", "environment")

    def test_dotenv_wins_over_legacy_file_when_no_environment_variable(self, tmp_path, monkeypatch):
        monkeypatch.delenv("MY_SECRET", raising=False)
        config_dir = self._config_dir(tmp_path)
        (tmp_path / ".env").write_text("MY_SECRET=from_dotenv\n", encoding="utf-8")
        legacy_path = tmp_path / "secrets" / "my.key"
        legacy_path.parent.mkdir(parents=True)
        legacy_path.write_text("from_legacy_file", encoding="utf-8")

        value, source = resolve_secret("MY_SECRET", config_dir=config_dir, legacy_path=legacy_path)
        assert (value, source) == ("from_dotenv", "dotenv")

    def test_legacy_file_used_when_no_environment_and_no_dotenv(self, tmp_path, monkeypatch):
        monkeypatch.delenv("MY_SECRET", raising=False)
        config_dir = self._config_dir(tmp_path)
        legacy_path = tmp_path / "secrets" / "my.key"
        legacy_path.parent.mkdir(parents=True)
        legacy_path.write_text("from_legacy_file", encoding="utf-8")

        value, source = resolve_secret("MY_SECRET", config_dir=config_dir, legacy_path=legacy_path)
        assert (value, source) == ("from_legacy_file", "legacy-key-file")

    def test_missing_everything_fails_closed_to_none_none(self, tmp_path, monkeypatch):
        monkeypatch.delenv("MY_SECRET", raising=False)
        config_dir = self._config_dir(tmp_path)
        legacy_path = tmp_path / "secrets" / "my.key"  # never created

        value, source = resolve_secret("MY_SECRET", config_dir=config_dir, legacy_path=legacy_path)
        assert (value, source) == (None, None)

    def test_legacy_path_none_is_tolerated(self, tmp_path, monkeypatch):
        monkeypatch.delenv("MY_SECRET", raising=False)
        config_dir = self._config_dir(tmp_path)
        value, source = resolve_secret("MY_SECRET", config_dir=config_dir, legacy_path=None)
        assert (value, source) == (None, None)

    def test_empty_dotenv_value_falls_through_to_legacy_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("MY_SECRET", raising=False)
        config_dir = self._config_dir(tmp_path)
        (tmp_path / ".env").write_text("MY_SECRET=\n", encoding="utf-8")
        legacy_path = tmp_path / "secrets" / "my.key"
        legacy_path.parent.mkdir(parents=True)
        legacy_path.write_text("from_legacy_file", encoding="utf-8")

        value, source = resolve_secret("MY_SECRET", config_dir=config_dir, legacy_path=legacy_path)
        assert (value, source) == ("from_legacy_file", "legacy-key-file")

    def test_unreadable_legacy_file_degrades_to_unresolved(self, tmp_path, monkeypatch):
        monkeypatch.delenv("MY_SECRET", raising=False)
        config_dir = self._config_dir(tmp_path)
        # A directory at the legacy path is "unreadable as text" -- exercises
        # the OSError branch without relying on filesystem permission quirks.
        legacy_path = tmp_path / "secrets" / "my.key"
        legacy_path.mkdir(parents=True)

        value, source = resolve_secret("MY_SECRET", config_dir=config_dir, legacy_path=legacy_path)
        assert (value, source) == (None, None)

    def test_explicit_env_path_override_is_honored(self, tmp_path, monkeypatch):
        monkeypatch.delenv("MY_SECRET", raising=False)
        config_dir = self._config_dir(tmp_path)
        (tmp_path / ".env").write_text("MY_SECRET=wrong_one\n", encoding="utf-8")
        explicit_env = tmp_path / "other" / ".env"
        explicit_env.parent.mkdir(parents=True)
        explicit_env.write_text("MY_SECRET=right_one\n", encoding="utf-8")

        value, source = resolve_secret(
            "MY_SECRET", config_dir=config_dir, legacy_path=None, env_path=explicit_env
        )
        assert (value, source) == ("right_one", "dotenv")
