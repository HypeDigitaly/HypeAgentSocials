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
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

ResolutionState = Literal["resolved", "resolved-empty"]

# ---------------------------------------------------------------------------
# W8-9 Phase 1: secrets resolution — real environment variable > repo-root
# `.env` > legacy `secrets/<file>.key` (deprecated but still supported).
#
# The engine never requires `.env` to exist: every call site that already
# tolerated a missing/empty legacy key file (fail-closed-to-degrade, never a
# hard run failure) keeps that exact posture — `.env` and the environment
# are simply two additional, higher-precedence places to look before falling
# back to the file. Nothing here raises; unresolved always means
# ``(None, None)``, identical in effect to today's "key file missing".
# ---------------------------------------------------------------------------

DOTENV_FILENAME = ".env"


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a tiny stdlib ``.env`` file: ``KEY=VALUE`` lines, blank lines
    and ``#``-comments ignored, no quoting games (spec: "no quoting games
    needed"). Returns ``{}`` for a missing, unreadable, or empty file —
    never raises; ``.env`` is optional infrastructure, not a required
    config artifact in the ``load_yaml_config`` fail-closed sense."""
    values: dict[str, str] = {}
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return values
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        values[key] = value.strip()
    return values


def find_dotenv(config_dir: Path, *, explicit_path: Path | None = None) -> Path | None:
    """Locate the repo-root ``.env`` file robustly.

    ``explicit_path`` (an operator- or ``RunContext``-supplied override)
    wins outright when given, existing-or-not. Otherwise walks upward from
    ``config_dir`` (inclusive) through every parent directory, returning the
    first ``.env`` found — in production ``config_dir`` is ``<repo_root>/
    config``, so the first hop (``config_dir.parent``) already finds it; the
    walk is only extra robustness for a differently-nested ``config_dir``.
    Returns ``None`` when nothing is found anywhere up the tree (the normal
    case in tests, whose ``tmp_path`` trees never contain a stray ``.env``).
    """
    if explicit_path is not None:
        return explicit_path if explicit_path.exists() else None
    start = Path(config_dir)
    candidates = [start, *start.parents]
    for directory in candidates:
        candidate = directory / DOTENV_FILENAME
        if candidate.exists():
            return candidate
    return None


def resolve_secret(
    name: str,
    *,
    config_dir: Path,
    legacy_path: Path | None,
    env_path: Path | None = None,
) -> tuple[str | None, str | None]:
    """Resolve one named secret by precedence: real environment variable >
    ``.env`` value > legacy ``secrets/<file>.key`` file content (deprecated,
    still supported). Returns ``(value, source)`` where ``source`` is one of
    ``"environment"``, ``"dotenv"``, ``"legacy-key-file"``, or ``(None,
    None)`` when nothing resolves anywhere — the same fail-closed-to-degrade
    signal every existing key-file reader already treats as "missing".

    Never raises: an unreadable legacy file degrades to unresolved exactly
    like a missing one (the caller already has its own message for that).
    """
    env_value = os.environ.get(name)
    if env_value:
        return env_value.strip(), "environment"

    dotenv_path = find_dotenv(config_dir, explicit_path=env_path)
    if dotenv_path is not None:
        dotenv_value = parse_env_file(dotenv_path).get(name)
        if dotenv_value:
            return dotenv_value.strip(), "dotenv"

    if legacy_path is not None:
        legacy_path = Path(legacy_path)
        if legacy_path.exists():
            try:
                legacy_value = legacy_path.read_text(encoding="utf-8").strip()
            except OSError:
                return None, None
            if legacy_value:
                return legacy_value, "legacy-key-file"

    return None, None


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
    # W8-9 Phase 2 (Virlo only; safe no-op defaults for every other source):
    # an ordered monitor fallback list (v2 intelligence-enabled monitor
    # first, falling through to the next entry when the current one has no
    # finalized run yet — collectors/virlo.py's ``collect()``), the trends
    # digest's opt-in-at-config-level default (the $0.25 read stays off
    # unless a theme explicitly turns it on), and the two Phase-2 collection
    # caps (sub-path pagination, media download count).
    monitor_ids: list[str] = field(default_factory=list)
    trends_digest_enabled: bool = False
    subpath_page_cap: int = 6
    media_download_cap: int = 24


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
    # Q6 re-audit R1 (W8-10 Phase 6): only candidates whose most recent
    # signal was fetched within this many days are scored this run — a
    # theme predating this key gets the same directional default (14 days)
    # the re-audit itself recommended.
    freshness_days: int = 14


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
            monitor_ids=list(cfg.get("monitor_ids") or ([cfg["monitor_id"]] if cfg.get("monitor_id") else [])),
            trends_digest_enabled=bool(cfg.get("trends_digest_enabled", False)),
            subpath_page_cap=int(cfg.get("subpath_page_cap", 6)),
            media_download_cap=int(cfg.get("media_download_cap", 24)),
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
        freshness_days=int(ranking_block.get("ranking_freshness_days", 14)),
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
class PostMixConfig:
    """``generation.post_mix`` (W8-10 Phase 5): per-run counts of each post
    type, cross-topic-allocated by ``spin.allocate_post_types`` in a fixed
    priority order (value_only, then playbook, then promotional — promo
    never placed first by the allocator). All-zero (the default, and the
    behaviour of any theme predating this block) is a total no-op: every
    asset keeps today's fully distance-derived ``post_type``/``value_only``
    behaviour, exactly as if this block did not exist."""

    value_only: int = 0
    playbook: int = 0
    promotional: int = 0


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
class LlmNodeOverride:
    """Optional per-node override of model/temperature/max_tokens (W8-9
    Q2) — e.g. a cheaper/faster model for the prompt crafter than the
    copywriter. Any field left ``None`` falls back to :class:`LlmConfig`'s
    own default for that field."""

    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None


@dataclass(frozen=True)
class LlmConfig:
    """The OpenRouter-backed LLM client config surface (W8-9 Q2), shared by
    every LLM node (N-A analyst, N-C copywriter, N-D prompt crafter).
    Disabled by default — a theme predating this block gets the
    interactive-file copy provider and no analysis-stage LLM call, exactly
    like :class:`OpenAICompatibleConfig` before it (the same
    safe-default-for-a-predating-theme philosophy :class:`GenerationConfig`
    already documents).

    Pricing (``usd_per_1m_*_tokens``) is an ESTIMATE for the spend ledger,
    used only when the OpenRouter response itself does not carry a
    ``usage.cost`` field. Live-verified 2026-08-07 against OpenRouter's own
    ``GET /api/v1/models`` listing for ``anthropic/claude-sonnet-5``
    (``pricing.prompt = 0.000002``, ``pricing.completion = 0.00001`` i.e.
    $2 / $10 per 1M tokens) — OpenRouter and/or Anthropic may reprice this
    model at any time, so these two numbers are a fallback estimate, not a
    source of truth; ``hypeagent.llm.LlmClient`` prefers the response's own
    reported ``usage.cost`` whenever OpenRouter provides it (which it did on
    every one of this milestone's live verification calls).
    """

    enabled: bool = False
    provider: str = "openrouter"
    base_url: str = "https://openrouter.ai/api/v1"
    model: str = "anthropic/claude-sonnet-5"
    key_env: str = "OPENROUTER_API_KEY"
    legacy_key_path: str = "secrets/openrouter.key"
    default_temperature: float = 0.4
    default_max_tokens: int = 1500
    usd_per_1m_input_tokens: float = 2.0
    usd_per_1m_output_tokens: float = 10.0
    per_run_usd_cap: float = 1.00
    per_run_call_cap: int = 20
    analyst_max_images: int = 12
    node_overrides: dict[str, LlmNodeOverride] = field(default_factory=dict)
    # W8-9 Q?? (post-live-run QA-starvation fix): calls set aside for the
    # ``vision_qa`` node ONLY -- non-QA nodes (analyst/copywriter/
    # prompt_crafter) see an effective call cap of
    # ``per_run_call_cap - qa_reserved_calls`` (``LlmClient._check_budget``),
    # so a chatty upstream stage can no longer starve N-E vision-QA of every
    # remaining call before it ever runs (the live-run defect: QA ran for
    # only 4 of 11 images because analyst/copy/craft had already consumed
    # the whole per-run cap). A QA call itself is exempt from this
    # reservation and may use the full ``per_run_call_cap``.
    qa_reserved_calls: int = 16
    # W8-10 Phase 2 (N-F humanness critic): on by default -- every gated-pass
    # copy asset gets one blind rewrite pass by a "native-speaker editor who
    # hates marketing copy" before it ships. A theme predating this knob (or
    # one that sets it to ``false``) gets exactly today's behaviour: no
    # critic call, no extra spend.
    humanness_critic_enabled: bool = True

    def override_for(self, node_name: str) -> LlmNodeOverride:
        return self.node_overrides.get(node_name, LlmNodeOverride())


@dataclass(frozen=True)
class MediaConfig:
    """The M4 media-generation knob surface for one theme (§5.2, §8.11).

    Safe defaults throughout: a theme predating M4 that omits ``media:``
    entirely still runs the media stage -- draft tier, tiny caps, the
    registry's own draft route -- rather than gaining a new fail-closed
    surface. ``dry_run: true`` produces every plan-only artifact and the
    full cost forecast, and submits nothing (§4.6)."""

    dry_run: bool = False
    per_run_usd_cap: float = 0.20
    per_run_count_cap: int = 4
    per_day_usd_cap: float = 0.40
    poll_interval_seconds: float = 7.0
    poll_timeout_seconds: float = 180.0
    resolution_window_days: int = 14  # bounded by the provider's 14-day deletion horizon (§8.13)
    aspect_ratio: str = "1:1"  # legacy fallback, used when a destination has no entry in aspect_ratio_by_destination
    output_format: str = "png"
    key_path: str = ""  # empty -> caller falls back to secrets_dir/kie.key, matching virlo's SourceConfig.key_path pattern
    unexplained_spend_threshold: float = 0.20  # relative divergence that trips the circuit breaker
    # W8-9 Q4: which registered route (config/model_registry.yaml route_id)
    # generates each image class this run -- "hero" (single-image
    # destinations) and "slide" (carousel destinations). Both default to the
    # standard-tier Nano Banana 2 route; draft routes stay registered for
    # cheap iteration but are never auto-selected unless a theme explicitly
    # points a class at one. Still subject to the registry's own
    # ``tier_ceiling`` gate at submission time regardless of what a theme sets.
    route_by_class: dict[str, str] = field(
        default_factory=lambda: {
            "hero": "img-standard-nano-banana-pro",
            "slide": "img-standard-nano-banana-pro",
        }
    )
    # Per-destination aspect ratio -- falls back to ``aspect_ratio`` above for
    # any destination not named here.
    aspect_ratio_by_destination: dict[str, str] = field(
        default_factory=lambda: {"linkedin": "1:1", "instagram_feed": "4:5"}
    )


@dataclass(frozen=True)
class GenerationConfig:
    """The M3 spin/copy/gate knob surface for one theme, extended in M4
    with the media-generation block."""

    destinations: list[str]
    copy_provider: str
    repair_budget: int
    mapping_distance: MappingDistanceBands
    exemplar_pool: list[str]
    openai_compatible: OpenAICompatibleConfig
    media: MediaConfig
    llm: LlmConfig
    # W8-10 Phase 5 (``generation.post_mix``) — default-constructed (all
    # zero = off) so every theme/test predating this block keeps today's
    # fully distance-derived post_type behaviour with zero code changes.
    post_mix: PostMixConfig = field(default_factory=PostMixConfig)


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
    media_block = block.get("media") or {}
    _media_defaults = MediaConfig()
    route_by_class_raw = media_block.get("route_by_class") or {}
    aspect_by_dest_raw = media_block.get("aspect_ratio_by_destination") or {}
    media = MediaConfig(
        dry_run=bool(media_block.get("dry_run", False)),
        per_run_usd_cap=float(media_block.get("per_run_usd_cap", 0.20)),
        per_run_count_cap=int(media_block.get("per_run_count_cap", 4)),
        per_day_usd_cap=float(media_block.get("per_day_usd_cap", 0.40)),
        poll_interval_seconds=float(media_block.get("poll_interval_seconds", 7.0)),
        poll_timeout_seconds=float(media_block.get("poll_timeout_seconds", 180.0)),
        resolution_window_days=int(media_block.get("resolution_window_days", 14)),
        aspect_ratio=str(media_block.get("aspect_ratio", "1:1")),
        output_format=str(media_block.get("output_format", "png")),
        key_path=str(media_block.get("key_path", "")),
        unexplained_spend_threshold=float(media_block.get("unexplained_spend_threshold", 0.20)),
        route_by_class={**_media_defaults.route_by_class, **{str(k): str(v) for k, v in route_by_class_raw.items()}},
        aspect_ratio_by_destination={
            **_media_defaults.aspect_ratio_by_destination,
            **{str(k): str(v) for k, v in aspect_by_dest_raw.items()},
        },
    )

    llm_block = block.get("llm") or {}
    node_overrides_raw = llm_block.get("node_overrides") or {}
    node_overrides = {
        str(name): LlmNodeOverride(
            model=cfg.get("model") if cfg else None,
            temperature=float(cfg["temperature"]) if cfg and cfg.get("temperature") is not None else None,
            max_tokens=int(cfg["max_tokens"]) if cfg and cfg.get("max_tokens") is not None else None,
        )
        for name, cfg in node_overrides_raw.items()
    }
    llm = LlmConfig(
        enabled=bool(llm_block.get("enabled", False)),
        provider=str(llm_block.get("provider", "openrouter")),
        base_url=str(llm_block.get("base_url", "https://openrouter.ai/api/v1")),
        model=str(llm_block.get("model", "anthropic/claude-sonnet-5")),
        key_env=str(llm_block.get("key_env", "OPENROUTER_API_KEY")),
        legacy_key_path=str(llm_block.get("legacy_key_path", "secrets/openrouter.key")),
        default_temperature=float(llm_block.get("default_temperature", 0.4)),
        default_max_tokens=int(llm_block.get("default_max_tokens", 1500)),
        usd_per_1m_input_tokens=float(llm_block.get("usd_per_1m_input_tokens", 2.0)),
        usd_per_1m_output_tokens=float(llm_block.get("usd_per_1m_output_tokens", 10.0)),
        per_run_usd_cap=float(llm_block.get("per_run_usd_cap", 1.00)),
        per_run_call_cap=int(llm_block.get("per_run_call_cap", 20)),
        analyst_max_images=int(llm_block.get("analyst_max_images", 12)),
        node_overrides=node_overrides,
        qa_reserved_calls=int(llm_block.get("qa_reserved_calls", 16)),
        humanness_critic_enabled=bool(llm_block.get("humanness_critic_enabled", True)),
    )

    post_mix_block = block.get("post_mix") or {}
    post_mix = PostMixConfig(
        value_only=int(post_mix_block.get("value_only", 0)),
        playbook=int(post_mix_block.get("playbook", 0)),
        promotional=int(post_mix_block.get("promotional", 0)),
    )

    return GenerationConfig(
        destinations=list(block.get("destinations") or ["linkedin", "instagram_feed"]),
        copy_provider=str(block.get("copy_provider", "interactive-file")),
        repair_budget=int(block.get("repair_budget", 2)),
        mapping_distance=mapping_distance,
        exemplar_pool=list(block.get("exemplar_pool") or []),
        openai_compatible=openai_compatible,
        media=media,
        llm=llm,
        post_mix=post_mix,
    )


# ---------------------------------------------------------------------------
# config/style_guide.yaml (W8-9 Q3) — platform skeletons, visual archetypes/
# registers, brand layer, reject list. Read by every LLM prompt-building
# function (N-A analyst, N-C copywriter, N-D prompt crafter). A separate,
# tiny loader (not folded into ``load_theme_generation_config``) because it
# is cross-theme, not per-theme, config.
# ---------------------------------------------------------------------------


def load_style_guide(config_dir: Path) -> dict[str, Any]:
    """Load ``config/style_guide.yaml``, fail-closed like every other config
    file in this engine. Callers that only need it on the LLM-enabled path
    catch :class:`ConfigError` at the stage boundary and degrade to the
    pre-existing non-LLM path (interactive-file copy, ``compose_prompt``
    image briefs) rather than letting a missing style guide fail the whole
    run — the same "a debugging/quality aid must never become a new failure
    surface" posture the rest of this engine already holds itself to."""
    return load_yaml_config(Path(config_dir) / "style_guide.yaml", name="style_guide.yaml")
