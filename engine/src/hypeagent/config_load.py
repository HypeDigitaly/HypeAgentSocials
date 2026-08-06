"""Fail-closed config loading (ARCHITECTURE_PLAN.md §11.3; config/README.md).

Semantics, shared by every config artifact under ``config/``:

- **Missing or unreadable file = stop.** Raises :class:`ConfigError` naming
  the exact missing/unreadable item — this is a presence-and-syntax check
  only (§11.3); credential *validity* is a separate, later concern.
- **Present-but-empty lists = valid RESOLVED-EMPTY state.** "Missing is not
  the same as empty" (§6.3) — an empty list is a deliberate, safe statement
  of zero entries, never a gate-off signal.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

ResolutionState = Literal["resolved", "resolved-empty"]


class ConfigError(Exception):
    """Raised for fail-closed config conditions: missing, unreadable, or unparseable."""


@dataclass(frozen=True)
class ResolvedList:
    """One config list, resolved to an explicit state.

    ``state`` is ``"resolved-empty"`` when the list is present but has zero
    entries, and ``"resolved"`` otherwise. There is deliberately no
    "unresolved" state here: reaching this point already means the file
    loaded and parsed, so unresolved conditions have already raised.
    """

    name: str
    values: list[Any]
    state: ResolutionState


def resolve_list(name: str, values: list[Any] | None) -> ResolvedList:
    values = list(values) if values is not None else []
    state: ResolutionState = "resolved-empty" if len(values) == 0 else "resolved"
    return ResolvedList(name=name, values=values, state=state)


def load_yaml_config(path: Path, *, name: str | None = None) -> dict[str, Any]:
    """Load one YAML config file, fail-closed.

    ``name`` is the human-facing identifier used in error messages; it
    defaults to the file's own name.
    """
    label = name or path.name
    if not path.exists():
        raise ConfigError(f"missing config item: {label} (expected at {path})")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"unreadable config item: {label} ({path}): {exc}") from exc
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"unparseable config item: {label} ({path}): {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(f"malformed config item: {label} ({path}): expected a mapping at top level")
    return data


_HARD_EXCLUDE_KEYS = ("topics", "framings", "claim_types", "do_not_mention_entities")


def load_hard_excludes(config_dir: Path) -> dict[str, ResolvedList]:
    """Load ``config/hard_excludes.yaml`` (§6.3 F-J, config/README.md).

    Missing/unreadable file -> ``ConfigError`` naming ``hard_excludes.yaml``
    (this is degrade condition 5 of §6.5 upstream of this loader; the caller
    decides what to do with the raised error). Present-but-empty lists
    resolve to ``RESOLVED-EMPTY``, a valid state.
    """
    path = config_dir / "hard_excludes.yaml"
    data = load_yaml_config(path, name="hard_excludes.yaml")
    excludes = data.get("hard_excludes")
    if excludes is None:
        excludes = {}
    if not isinstance(excludes, dict):
        raise ConfigError(
            f"malformed config item: hard_excludes.yaml ({path}): "
            "'hard_excludes' key must be a mapping"
        )
    return {key: resolve_list(key, excludes.get(key)) for key in _HARD_EXCLUDE_KEYS}


@dataclass(frozen=True)
class ThemeConfig:
    """Phase-1 resolved config bundle. Grows as later phases add sources."""

    hard_excludes: dict[str, ResolvedList] = field(default_factory=dict)
    fingerprint: str = ""


def _fingerprint(hard_excludes: dict[str, ResolvedList]) -> str:
    payload = json.dumps(
        {key: sorted(map(str, item.values)) for key, item in hard_excludes.items()},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def load_theme_config(config_dir: Path) -> ThemeConfig:
    """Load the Phase-1 config surface, fail-closed.

    Raises :class:`ConfigError` naming the exact missing/unreadable item if
    any required config file cannot be resolved.
    """
    hard_excludes = load_hard_excludes(config_dir)
    return ThemeConfig(hard_excludes=hard_excludes, fingerprint=_fingerprint(hard_excludes))


# ---------------------------------------------------------------------------
# Theme research block (§10.2) — what to watch and how to collect.
#
# A separate loader from ``load_theme_config`` above (which stays exactly as
# milestone 1 left it): the research block is a *per-theme* artifact under
# ``config/themes/<name>.yaml``, consumed by the collection and ranking
# stages, whereas ``load_theme_config`` covers the cross-theme baseline
# (hard excludes) that predates any theme existing at all.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceConfig:
    """One source's row of the resolved portfolio (§2.3), as configured for
    one theme."""

    enabled: bool = True
    family: str | None = None
    family_en: str | None = None
    family_cs: str | None = None
    budget_max_calls: int = 10
    circuit_breaker_threshold: int = 3
    limit: int = 20
    queries: dict[str, list[str]] = field(default_factory=dict)
    key_path: str | None = None
    monitor_id: str | None = None


@dataclass(frozen=True)
class RankingKnobs:
    """The ranking-config block (§2.7, §10.2), versioned and dated."""

    version: int
    brand_fit_floor: float
    top_n_per_language: int
    half_life_hours: dict[str, float]
    baseline_lookback_days: int
    absolute_band_fallback: dict[str, dict[str, float]]
    dedupe_lookback_days: int
    rejection_suppression_days: int
    corroboration_growth_override_families: int
    new_angle_min_new_signals: int
    corroboration_bonus: float
    evidence_floor_min_candidates: dict[str, int]
    evidence_floor_min_families: dict[str, int]


@dataclass(frozen=True)
class ThemeResearchConfig:
    """The Phase-1 research block for one theme: watch topics/ICP terms per
    language, the source roster, and the ranking-config block."""

    theme_name: str
    languages: list[str]
    watch_topics: dict[str, list[str]]
    icp_terms: dict[str, list[str]]
    sources: dict[str, SourceConfig]
    ranking: RankingKnobs


def load_theme_research_config(config_dir: Path, theme_name: str) -> ThemeResearchConfig:
    """Load ``config/themes/<theme_name>.yaml``, fail-closed.

    Missing or unreadable -> :class:`ConfigError` naming the file — a run
    cannot collect or rank without knowing what it is watching for.
    """
    path = Path(config_dir) / "themes" / f"{theme_name}.yaml"
    data = load_yaml_config(path, name=f"themes/{theme_name}.yaml")

    theme_block = data.get("theme") or {}
    languages = list(theme_block.get("languages") or [])
    if not languages:
        raise ConfigError(f"malformed config item: themes/{theme_name}.yaml: 'theme.languages' must be non-empty")

    research_block = data.get("research") or {}
    watch_topics = {k: list(v or []) for k, v in (research_block.get("watch_topics") or {}).items()}
    icp_terms = {k: list(v or []) for k, v in (research_block.get("icp_terms") or {}).items()}

    sources_block = research_block.get("sources") or {}
    sources: dict[str, SourceConfig] = {}
    for name, cfg in sources_block.items():
        cfg = cfg or {}
        sources[name] = SourceConfig(
            enabled=bool(cfg.get("enabled", True)),
            family=cfg.get("family"),
            family_en=cfg.get("family_en"),
            family_cs=cfg.get("family_cs"),
            budget_max_calls=int(cfg.get("budget_max_calls", 10)),
            circuit_breaker_threshold=int(cfg.get("circuit_breaker_threshold", 3)),
            limit=int(cfg.get("limit", 20)),
            queries={k: list(v or []) for k, v in (cfg.get("queries") or {}).items()},
            key_path=cfg.get("key_path"),
            monitor_id=cfg.get("monitor_id"),
        )

    ranking_block = data.get("ranking") or {}
    if not ranking_block:
        raise ConfigError(f"malformed config item: themes/{theme_name}.yaml: 'ranking' block is required")
    ranking = RankingKnobs(
        version=int(ranking_block.get("ranking_config_version", 1)),
        brand_fit_floor=float(ranking_block.get("brand_fit_floor", 0.35)),
        top_n_per_language=int(ranking_block.get("top_n_per_language", 3)),
        half_life_hours={k: float(v) for k, v in (ranking_block.get("freshness_half_life_hours") or {}).items()},
        baseline_lookback_days=int(ranking_block.get("baseline_lookback_days", 90)),
        absolute_band_fallback={
            k: {bk: float(bv) for bk, bv in (v or {}).items()}
            for k, v in (ranking_block.get("absolute_band_fallback") or {}).items()
        },
        dedupe_lookback_days=int(ranking_block.get("dedupe_lookback_days", 30)),
        rejection_suppression_days=int(ranking_block.get("rejection_suppression_days", 14)),
        corroboration_growth_override_families=int(ranking_block.get("corroboration_growth_override_families", 2)),
        new_angle_min_new_signals=int(ranking_block.get("new_angle_min_new_signals", 3)),
        corroboration_bonus=float(ranking_block.get("corroboration_bonus", 0.15)),
        evidence_floor_min_candidates={
            k: int(v.get("min_candidates", 1)) for k, v in (ranking_block.get("evidence_floor") or {}).items()
        },
        evidence_floor_min_families={
            k: int(v.get("min_families", 1)) for k, v in (ranking_block.get("evidence_floor") or {}).items()
        },
    )

    return ThemeResearchConfig(
        theme_name=theme_name,
        languages=languages,
        watch_topics=watch_topics,
        icp_terms=icp_terms,
        sources=sources,
        ranking=ranking,
    )


# ---------------------------------------------------------------------------
# M3 generation block (§6.9 spin, §14.1/§14.3 gates) — spin/copy/gate knobs,
# goal-scoped to EN. A separate loader for the same reason the research
# block is separate from the cross-theme baseline: this is per-theme
# generation policy, consumed only by the spin/copy/claim-gate stages.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MappingDistanceBands:
    """Term-overlap score thresholds for spin's near/adjacent/far mapping
    distance (§6.9). A score at or above ``near_min`` is "near" (the plan's
    "direct"); at or above ``adjacent_min`` is "adjacent"; below that, "far"
    — which structurally forces the value-only variant (no offer, no
    product CTA)."""

    near_min: float = 0.35
    adjacent_min: float = 0.12


@dataclass(frozen=True)
class OpenAICompatibleConfig:
    """Generic OpenAI-chat-completions-shaped provider config. Disabled by
    default — no key exists for this goal; wired for structure only, proven
    by a fixture test of the request shape."""

    enabled: bool = False
    base_url: str = ""
    model: str = ""
    key_path: str = ""
    max_tokens: int = 400


@dataclass(frozen=True)
class GenerationConfig:
    """The M3 spin/copy/gate knob surface for one theme."""

    destinations: list[str]
    copy_provider: str
    repair_budget: int
    mapping_distance: MappingDistanceBands
    exemplar_pool: list[str]
    openai_compatible: OpenAICompatibleConfig


def load_theme_generation_config(config_dir: Path, theme_name: str) -> GenerationConfig:
    """Load the ``generation:`` block of ``config/themes/<theme_name>.yaml``.

    Entirely optional-with-safe-defaults (unlike the research block): a
    theme with no ``generation:`` block gets the interactive-file provider,
    the default mapping-distance bands, and both goal destinations — the
    generation stages are additive to Phase 1 and must not become a new
    fail-closed surface for themes that predate M3.
    """
    path = Path(config_dir) / "themes" / f"{theme_name}.yaml"
    data = load_yaml_config(path, name=f"themes/{theme_name}.yaml")
    block = data.get("generation") or {}

    dist_block = block.get("mapping_distance_bands") or {}
    mapping_distance = MappingDistanceBands(
        near_min=float(dist_block.get("near_min", 0.35)),
        adjacent_min=float(dist_block.get("adjacent_min", 0.12)),
    )
    oai_block = block.get("openai_compatible") or {}
    openai_compatible = OpenAICompatibleConfig(
        enabled=bool(oai_block.get("enabled", False)),
        base_url=str(oai_block.get("base_url", "")),
        model=str(oai_block.get("model", "")),
        key_path=str(oai_block.get("key_path", "")),
        max_tokens=int(oai_block.get("max_tokens", 400)),
    )
    return GenerationConfig(
        destinations=list(block.get("destinations") or ["linkedin", "instagram_feed"]),
        copy_provider=str(block.get("copy_provider", "interactive-file")),
        repair_budget=int(block.get("repair_budget", 2)),
        mapping_distance=mapping_distance,
        exemplar_pool=list(block.get("exemplar_pool") or []),
        openai_compatible=openai_compatible,
    )
