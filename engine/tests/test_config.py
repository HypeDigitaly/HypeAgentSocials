"""Tests for hypeagent.config_load — fail-closed config semantics."""

from __future__ import annotations

import pytest

from hypeagent.config_load import (
    ConfigError,
    find_dotenv,
    load_hard_excludes,
    load_theme_config,
    load_theme_generation_config,
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
# W8-9 (post-live-run token/QA-starvation fix): generation.llm's per-node
# ``max_tokens`` overrides and ``qa_reserved_calls`` must round-trip through
# ``load_theme_generation_config`` exactly as written in the theme YAML.
# ---------------------------------------------------------------------------


def _write_llm_theme_yaml(config_dir, *, extra_llm_yaml: str = "") -> None:
    themes_dir = config_dir / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    (themes_dir / "hypedigitaly.yaml").write_text(
        "theme:\n"
        "  name: hypedigitaly\n"
        "generation:\n"
        "  llm:\n"
        "    enabled: true\n"
        "    default_max_tokens: 1500\n"
        "    per_run_usd_cap: 2.00\n"
        "    per_run_call_cap: 60\n"
        "    qa_reserved_calls: 16\n"
        "    node_overrides:\n"
        "      analyst:\n"
        "        max_tokens: 4000\n"
        "      copywriter:\n"
        "        max_tokens: 4000\n"
        "      prompt_crafter:\n"
        "        max_tokens: 6000\n"
        "      vision_qa:\n"
        "        max_tokens: 1000\n"
        f"{extra_llm_yaml}",
        encoding="utf-8",
    )


class TestLoadThemeGenerationConfigLlm:
    def test_per_node_max_tokens_overrides_merge_correctly(self, tmp_path):
        config_dir = tmp_path / "config"
        _write_llm_theme_yaml(config_dir)
        generation = load_theme_generation_config(config_dir, "hypedigitaly")

        assert generation.llm.default_max_tokens == 1500  # unchanged fallback for any node not named
        assert generation.llm.override_for("analyst").max_tokens == 4000
        assert generation.llm.override_for("copywriter").max_tokens == 4000
        assert generation.llm.override_for("prompt_crafter").max_tokens == 6000
        assert generation.llm.override_for("vision_qa").max_tokens == 1000
        # A node with no override in the YAML falls back to the default.
        assert generation.llm.override_for("some_future_node").max_tokens is None

    def test_raised_caps_and_qa_reserve_parse_correctly(self, tmp_path):
        config_dir = tmp_path / "config"
        _write_llm_theme_yaml(config_dir)
        generation = load_theme_generation_config(config_dir, "hypedigitaly")

        assert generation.llm.per_run_usd_cap == pytest.approx(2.00)
        assert generation.llm.per_run_call_cap == 60
        assert generation.llm.qa_reserved_calls == 16

    def test_qa_reserved_calls_defaults_to_16_when_absent(self, tmp_path):
        config_dir = tmp_path / "config"
        themes_dir = config_dir / "themes"
        themes_dir.mkdir(parents=True, exist_ok=True)
        (themes_dir / "hypedigitaly.yaml").write_text(
            "theme:\n  name: hypedigitaly\ngeneration:\n  llm:\n    enabled: true\n", encoding="utf-8",
        )
        generation = load_theme_generation_config(config_dir, "hypedigitaly")
        assert generation.llm.qa_reserved_calls == 16


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
