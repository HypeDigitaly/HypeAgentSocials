"""Stage-runner framework (ARCHITECTURE_PLAN.md §9, §17.2 Phase-1 scope).

Phase 1 is "the narrowest end-to-end run that produces something a human
can read": theme load with fail-closed checking, four free collectors,
ranking with the fit gate and cross-day dedupe, packaging and the run
digest. No brand truth, no generation, no money.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from hypeagent import analysis, brand_truth, config_load, copy_gen, llm as llm_module, media_gen, packaging, process_summary, promptcraft, resume_state as resume_state_module, spin as spin_module
from hypeagent.collectors import google_news, hackernews, huggingface, producthunt, virlo
from hypeagent.collectors.base import CollectContext, Fetcher, UrllibFetcher, to_normalized_signal
from hypeagent.config_load import (
    ConfigError,
    GenerationConfig,
    ThemeConfig,
    ThemeResearchConfig,
    load_theme_config,
    load_theme_generation_config,
    load_theme_research_config,
    load_style_guide,
)
from hypeagent.exit_codes import ExitClass
from hypeagent.ranking import (
    Phase1DeterministicFitJudge,
    Phase1DeterministicNewAngleJudge,
    RankingConfig,
    Scorecard,
    rank,
)
from hypeagent.store import SourceDenyList, SpecialCategoryLexicon, Store, load_source_deny_list, load_special_category_lexicon
from hypeagent.trace import TraceWriter

# Canonical stage order. M3 (GOAL_ROADMAP.md) inserts brand_truth, spin and
# copy between ranking and packaging — the goal-scoped Phase-2 core: brand
# truth resolves once per run, spin maps EN topics deterministically, and
# copy generates + gates English social assets only (CS stops at ranking,
# §17.2 Phase-1's four-collector/ranking/pack core stays intact underneath).
# M4 (GOAL_ROADMAP.md) inserts media after copy: one Kie.ai draft-tier image
# per gated-pass copy asset, planning-only for everything else — images
# only, draft tier only, nothing publishes.
CANONICAL_STAGE_NAMES: tuple[str, ...] = (
    "theme_load",
    "collection",
    "analysis",
    "ranking",
    "brand_truth",
    "spin",
    "copy",
    "media",
    "packaging",
    "digest",
)

DEFAULT_THEME_NAME = "hypedigitaly"
GENERATION_LANGUAGE = "en"  # goal-scoped: only EN candidates proceed past ranking into spin/copy
COPY_MAX_ATTEMPTS = 2


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class RunContext:
    """Mutable state threaded through the stage pipeline for one run."""

    run_id: str
    config_dir: Path
    logs_dir: Path
    theme_name: str = DEFAULT_THEME_NAME
    secrets_dir: Path | None = None
    theme_config: ThemeConfig | None = None
    research: ThemeResearchConfig | None = None
    generation: GenerationConfig | None = None
    deny_list: SourceDenyList | None = None
    lexicon: SpecialCategoryLexicon | None = None
    store: Store | None = None
    fetcher_factory: Callable[[], Fetcher] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def run_date(self) -> str:
        return self.run_id.split("_")[0]


@dataclass
class StageResult:
    """What a stage callable returns; feeds directly into ``stage_end``."""

    outcome: str = "ok"  # ok | degraded | failed-closed
    items_in: int = 0
    items_out: int = 0
    input_refs: list[dict[str, Any]] = field(default_factory=list)
    output_refs: list[dict[str, Any]] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


StageFn = Callable[[RunContext, TraceWriter], StageResult]


def _load_theme_and_config(ctx: RunContext) -> None:
    """Shared, fail-closed config load: theme + research + generation +
    the special-category deny-list/lexicon (§2.6, §10.2). Used by both the
    ``theme_load`` stage (a normal run) and ``prepare_resume_context``
    (``--resume``, which does not re-run ``theme_load`` as a canonical
    stage but still needs these same objects on ``ctx`` to re-enter
    copy/media/packaging/digest)."""
    ctx.theme_config = load_theme_config(ctx.config_dir)
    ctx.research = load_theme_research_config(ctx.config_dir, ctx.theme_name)
    ctx.generation = load_theme_generation_config(ctx.config_dir, ctx.theme_name)
    ctx.deny_list = load_source_deny_list(ctx.config_dir / "special_category_source_deny_list.yaml")
    ctx.lexicon = load_special_category_lexicon(ctx.config_dir / "special_category_lexicon.yaml")


def stage_theme_load(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """Fail-closed config/theme load, extended to load the theme's research
    block (§10.2), the special-category source deny-list and lexicon
    (§2.6), and to run the retention expiry job at run start."""
    _load_theme_and_config(ctx)

    secrets_dir = ctx.secrets_dir or (ctx.config_dir.parent / "secrets")
    ctx.store = Store.open(ctx.logs_dir, secrets_dir, config_dir=ctx.config_dir)

    expiry = ctx.store.run_expiry_job()
    trace.decision(
        "theme_load",
        decision=(
            f"retention expiry job: {expiry.raw_payloads_deleted} raw payload(s) deleted, "
            f"{expiry.verbatim_expired} verbatim provenance record(s) expired, "
            f"{expiry.packs_rewritten} archived pack file(s) rewritten, "
            f"{expiry.normalized_records_pruned} normalized record(s) pruned"
        ),
        rule="ARCHITECTURE_PLAN §2.6: the expiry job runs at run start, including inside packed run packs",
    )

    resolved_empty = [
        name for name, item in ctx.theme_config.hard_excludes.items() if item.state == "resolved-empty"
    ]
    return StageResult(
        outcome="ok",
        items_in=0,
        items_out=len(ctx.theme_config.hard_excludes) + len(ctx.research.sources),
        extra={"resolved_empty_lists": resolved_empty, "theme": ctx.theme_name},
    )


def stage_collection(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """The four free collectors (§2.3), each honouring its own budget,
    circuit breaker, and the pre-collection special-category deny-list;
    every item is stored through the post-collection lexical check (§2.6)."""
    assert ctx.research is not None and ctx.store is not None and ctx.deny_list is not None and ctx.lexicon is not None

    fetcher = ctx.fetcher_factory() if ctx.fetcher_factory is not None else UrllibFetcher()
    cctx = CollectContext(
        store=ctx.store,
        trace=trace,
        fetcher=fetcher,
        deny_list=ctx.deny_list,
        run_id=ctx.run_id,
        run_date=ctx.run_date,
        theme=ctx.theme_name,
        stage="collection",
        run_dir=ctx.logs_dir / "runs" / ctx.run_id,
    )

    sources = ctx.research.sources
    results = []

    hn_cfg = sources.get("hacker_news")
    if hn_cfg is not None and hn_cfg.enabled:
        results.append(
            hackernews.collect(
                cctx,
                family=hn_cfg.family or "developer_technical_discourse",
                max_items=max(1, hn_cfg.budget_max_calls - 1),
                circuit_breaker_threshold=hn_cfg.circuit_breaker_threshold,
            )
        )

    gn_cfg = sources.get("google_news")
    if gn_cfg is not None and gn_cfg.enabled:
        results.append(
            google_news.collect(
                cctx,
                queries_by_language=gn_cfg.queries,
                family_by_language={
                    "en": gn_cfg.family_en or "editorial_relay",
                    "cs": gn_cfg.family_cs or "czech_native_news",
                },
                circuit_breaker_threshold=gn_cfg.circuit_breaker_threshold,
            )
        )

    hf_cfg = sources.get("hugging_face")
    if hf_cfg is not None and hf_cfg.enabled:
        results.append(
            huggingface.collect(
                cctx,
                family=hf_cfg.family or "launch_registries",
                limit=hf_cfg.limit,
                circuit_breaker_threshold=hf_cfg.circuit_breaker_threshold,
            )
        )

    ph_cfg = sources.get("product_hunt")
    if ph_cfg is not None and ph_cfg.enabled:
        results.append(
            producthunt.collect(
                cctx,
                family=ph_cfg.family or "launch_registries",
                circuit_breaker_threshold=ph_cfg.circuit_breaker_threshold,
            )
        )

    virlo_cfg = sources.get("virlo")
    if virlo_cfg is not None and virlo_cfg.enabled:
        secrets_dir = ctx.secrets_dir or (ctx.config_dir.parent / "secrets")
        key_path = Path(virlo_cfg.key_path) if virlo_cfg.key_path else (secrets_dir / "virlo.key")
        results.append(
            virlo.collect(
                cctx,
                family=virlo_cfg.family or "short_form_trends",
                key_path=key_path,
                config_dir=ctx.config_dir,
                monitor_id=virlo_cfg.monitor_id or virlo.DEFAULT_MONITOR_ID,
                monitor_ids=virlo_cfg.monitor_ids or None,
                budget_max_calls=virlo_cfg.budget_max_calls,
                circuit_breaker_threshold=virlo_cfg.circuit_breaker_threshold,
                trends_digest_enabled=virlo_cfg.trends_digest_enabled,
                subpath_page_cap=virlo_cfg.subpath_page_cap,
                media_download_cap=virlo_cfg.media_download_cap,
            )
        )

    items_in = sum(len(r.items) for r in results)
    stored_count = 0
    excluded_count = 0
    degraded_sources: list[packaging.DegradedSourceNote] = []

    for result in results:
        if result.outcome == "degraded" and result.degrade_reason:
            trace.degrade("collection", condition=result.degrade_reason, caused=f"source={result.source}")
            degraded_sources.append(packaging.DegradedSourceNote(source=result.source, reason=result.degrade_reason))
        elif result.outcome == "skip":
            trace.decision(
                "collection",
                decision=f"source '{result.source}' skipped entirely — {result.degrade_reason}",
                rule="ARCHITECTURE_PLAN §2.6 limb (a)",
            )

        for item in result.items:
            domain = urlparse(item.url).netloc.lower()
            normalized = to_normalized_signal(item, domain=domain)
            stored, excluded_category = ctx.store.store_signal(normalized, run_id=ctx.run_id, lexicon=ctx.lexicon)
            if stored:
                stored_count += 1
            else:
                excluded_count += 1
                trace.decision(
                    "collection",
                    decision=f"item not stored — special-category lexicon hit ({excluded_category})",
                    rule="ARCHITECTURE_PLAN §2.6 limb (b): do-not-store/delete, never flag-and-continue",
                )

    ctx.extra["degraded_sources"] = degraded_sources
    ctx.extra["collector_calls_made"] = {r.source: r.calls_made for r in results}
    outcome = "degraded" if degraded_sources else "ok"
    return StageResult(
        outcome=outcome,
        items_in=items_in,
        items_out=stored_count,
        extra={
            "excluded_special_category": excluded_count,
            "degraded_sources": [n.source for n in degraded_sources],
            # W8-8: per-source breakdown, so the process summary's §3 can
            # show "source -> items fetched" without re-deriving it from
            # scratch. Going-forward only -- a trace written before this
            # field existed simply lacks the key, and the summarizer
            # degrades that one line gracefully.
            "calls_made_by_source": {r.source: r.calls_made for r in results},
            "items_fetched_by_source": {r.source: len(r.items) for r in results},
        },
    )


def _resolve_llm_api_key(ctx: RunContext) -> str | None:
    assert ctx.generation is not None
    llm_cfg = ctx.generation.llm
    legacy_path = (ctx.config_dir.parent / llm_cfg.legacy_key_path) if llm_cfg.legacy_key_path else None
    api_key, _source = config_load.resolve_secret(llm_cfg.key_env, config_dir=ctx.config_dir, legacy_path=legacy_path)
    return api_key


def _get_or_build_llm_client(ctx: RunContext, trace: TraceWriter, *, stage: str) -> llm_module.LlmClient | None:
    """Build (once per pipeline invocation) and cache the ONE shared
    ``LlmClient`` used by every LLM node this run (analysis/copy/prompt
    craft), so the per-run budget (``llm.per_run_usd_cap`` /
    ``per_run_call_cap``) is enforced across all of them together rather
    than reset per stage. Returns ``None`` — every caller then degrades to
    its pre-existing non-LLM path — when the LLM is disabled in config or
    its API key does not resolve anywhere (the same fail-closed-to-degrade
    posture ``collectors/virlo.py`` and ``media_gen.py`` already hold their
    own key resolution to)."""
    assert ctx.generation is not None
    if "llm_client" in ctx.extra:
        client = ctx.extra["llm_client"]
        if client is not None:
            client.set_stage(stage)
        return client

    llm_cfg = ctx.generation.llm
    if not llm_cfg.enabled:
        ctx.extra["llm_client"] = None
        return None

    api_key = _resolve_llm_api_key(ctx)
    if not api_key:
        trace.decision(
            stage,
            decision=(
                f"OpenRouter API key not resolved ({llm_cfg.key_env} / .env / legacy key file) — "
                "every LLM node this run degrades to its non-LLM path"
            ),
            rule="W8-9 Phase 1 fail-closed-to-degrade posture: same as Virlo/Kie's own key resolution",
        )
        ctx.extra["llm_client"] = None
        return None

    fetcher = ctx.fetcher_factory() if ctx.fetcher_factory is not None else UrllibFetcher()
    client = llm_module.LlmClient(config=llm_cfg, fetcher=fetcher, api_key=api_key, trace=trace, stage=stage)
    ctx.extra["llm_client"] = client
    return client


def _load_style_guide_safe(ctx: RunContext) -> dict[str, Any] | None:
    """Soft-load ``config/style_guide.yaml`` — cached on ``ctx.extra`` so
    every LLM-grounded stage this run shares one copy. ``None`` when the
    file is missing/unreadable/unparseable; every caller degrades to its
    pre-existing non-LLM-grounded path (``load_style_guide``'s own
    docstring) rather than failing the run over a missing style guide."""
    if "style_guide" in ctx.extra:
        return ctx.extra["style_guide"]
    try:
        guide = load_style_guide(ctx.config_dir)
    except ConfigError:
        guide = None
    ctx.extra["style_guide"] = guide
    return guide


def stage_analysis(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """N-A Trend & Visual Analyst (W8-9 Q3a; FLOW_MAP.md's ``analysis``
    stage). Runs between ``collection`` and ``ranking`` but does NOT feed
    ranking in v1 (ranking stays fully deterministic) — its output
    (``analysis/viral_playbook.yaml``) feeds ``copy`` instead, and its path
    is carried into ``resume_state.yaml`` (via ``stage_spin``) so a
    ``--resume`` re-entry into ``copy`` still has it without re-running this
    stage.

    Never fails the run (see ``hypeagent.analysis`` module docstring): no
    Virlo corpus this run, the LLM disabled in config, an exhausted LLM
    budget, or a failed call all produce an explicit, empty-but-valid
    playbook and the pipeline continues."""
    assert ctx.generation is not None and ctx.store is not None
    run_dir = ctx.logs_dir / "runs" / ctx.run_id
    media_dir = ctx.store.artifacts_dir / ctx.run_id / "virlo_media"

    llm_client = _get_or_build_llm_client(ctx, trace, stage="analysis")
    style_guide = _load_style_guide_safe(ctx)

    playbook = analysis.run_trend_visual_analyst(
        run_dir=run_dir, media_dir=media_dir, style_guide=style_guide, llm_client=llm_client,
        trace=trace, stage="analysis", max_images=ctx.generation.llm.analyst_max_images,
    )
    ctx.extra["viral_playbook"] = playbook
    ctx.extra["viral_playbook_path"] = str(run_dir / analysis.VIRAL_PLAYBOOK_DIRNAME / analysis.VIRAL_PLAYBOOK_FILENAME)

    outcome = "degraded" if playbook.degraded else "ok"
    return StageResult(
        outcome=outcome,
        items_in=1,
        items_out=len(playbook.themes),
        extra={
            "skipped": playbook.skipped,
            "skip_reason": playbook.skip_reason,
            "degrade_reason": playbook.degrade_reason,
            "theme_count": len(playbook.themes),
        },
    )


def stage_ranking(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """Cluster -> fit gate -> composite -> cross-day dedupe -> top-N cap
    (§2.7, §2.8, §2.8a)."""
    assert ctx.research is not None and ctx.store is not None and ctx.theme_config is not None

    research = ctx.research
    ranking_cfg = research.ranking

    since = datetime.now().astimezone() - timedelta(days=max(1, ranking_cfg.dedupe_lookback_days))
    signals = ctx.store.signals_since(since=since)

    watch_terms_by_language = {
        lang: list(research.watch_topics.get(lang, [])) + list(research.icp_terms.get(lang, []))
        for lang in research.languages
    }
    topics_item = ctx.theme_config.hard_excludes.get("topics")
    hard_exclude_topics = list(topics_item.values) if topics_item is not None else []

    config = RankingConfig(
        version=ranking_cfg.version,
        brand_fit_floor=ranking_cfg.brand_fit_floor,
        top_n_per_language=ranking_cfg.top_n_per_language,
        half_life_hours=ranking_cfg.half_life_hours,
        baseline_lookback_days=ranking_cfg.baseline_lookback_days,
        absolute_band_fallback=ranking_cfg.absolute_band_fallback,
        dedupe_lookback_days=ranking_cfg.dedupe_lookback_days,
        rejection_suppression_days=ranking_cfg.rejection_suppression_days,
        corroboration_growth_override_families=ranking_cfg.corroboration_growth_override_families,
        new_angle_min_new_signals=ranking_cfg.new_angle_min_new_signals,
        corroboration_bonus=ranking_cfg.corroboration_bonus,
        evidence_floor_min_candidates=ranking_cfg.evidence_floor_min_candidates,
        evidence_floor_min_families=ranking_cfg.evidence_floor_min_families,
    )

    degraded_sources = ctx.extra.get("degraded_sources", [])
    total_enabled_sources = sum(1 for s in research.sources.values() if s.enabled)
    reachable_fraction = (
        (total_enabled_sources - len(degraded_sources)) / total_enabled_sources if total_enabled_sources else 1.0
    )

    result = rank(
        store=ctx.store,
        signals=signals,
        watch_terms_by_language=watch_terms_by_language,
        hard_exclude_topics=hard_exclude_topics,
        lexicon=ctx.lexicon,
        config=config,
        run_id=ctx.run_id,
        fit_judge=Phase1DeterministicFitJudge(),
        new_angle_judge=Phase1DeterministicNewAngleJudge(),
        reachable_source_fraction=max(0.0, reachable_fraction),
        languages=research.languages,
    )
    ctx.extra["ranking_result"] = result

    for language, breached in result.evidence_floor_breached.items():
        if breached:
            trace.degrade(
                "ranking",
                condition=f"per-language evidence-and-volume floor breached ({language})",
                caused=f"{result.evidence_floor_consecutive[language]} consecutive run(s) below floor — never blocks the run",
            )

    if result.zero_passing_candidates:
        trace.decision(
            "ranking",
            decision="0 passing candidates — successful outcome, thresholds were not relaxed",
            rule="ARCHITECTURE_PLAN §2.7 / §17.2 Phase-1 acceptance",
        )

    total_top = sum(len(v) for v in result.top_by_language.values())
    return StageResult(
        outcome="ok",
        items_in=len(signals),
        items_out=total_top,
        extra={
            "zero_passing_candidates": result.zero_passing_candidates,
            "scorecards_total": len(result.all_scorecards),
        },
    )


def stage_brand_truth(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """Load brand facts + the latest dated claim-ledger snapshot and pack
    the per-run brand-truth panel (§6.3-§6.6, goal-scoped M3).

    Fail-closed conditions (missing ``brand_facts.yaml``, an empty F-D ICP
    list, no snapshot file at all) raise :class:`hypeagent.config_load.ConfigError`,
    which ``run_pipeline`` lets propagate exactly like every other config
    load in this engine — the caller maps it to ``policy-stop``. Snapshot
    **staleness alone** is this milestone's one degrade trigger (§6.5,
    simplified): the run continues research-only and the copy stage
    refuses, with the cause named in the digest.
    """
    panel = brand_truth.resolve_brand_truth(ctx.config_dir)
    ctx.extra["brand_truth_panel"] = panel

    run_dir = ctx.logs_dir / "runs" / ctx.run_id
    pack_dir = run_dir / "pack"
    pack_dir.mkdir(parents=True, exist_ok=True)
    panel_path = pack_dir / "brand_truth_panel.yaml"
    panel_path.write_text(
        yaml.safe_dump(panel.to_yaml_dict(), allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    data = panel_path.read_bytes()
    trace.artifact_write(
        "brand_truth", path=str(panel_path), kind="brand_truth_panel", bytes_=len(data), sha256=_sha256_hex(data)
    )

    if panel.band == "stale":
        trace.degrade(
            "brand_truth",
            condition=panel.degrade_reason or "claim ledger snapshot stale",
            caused="claim-ledger snapshot age exceeded max_age_days (§6.5 degrade posture, simplified: one trigger)",
        )
        return StageResult(
            outcome="degraded", items_in=1, items_out=1,
            extra={"snapshot_band": panel.band, "snapshot_id": panel.snapshot.snapshot_id},
        )

    return StageResult(
        outcome="ok", items_in=1, items_out=1,
        extra={"snapshot_band": panel.band, "snapshot_id": panel.snapshot.snapshot_id},
    )


def stage_spin(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """Deterministic spin mapping (§6.9) for EN top-ranked candidates only.

    Non-EN top-ranked candidates (Czech, under full Phase-2 scope) stop
    here with an honest hold note — Czech copy generation is designed-in
    but not exercised for this goal (GOAL_ROADMAP.md: "English only for the
    test... Czech machinery stays designed-in but is not exercised")."""
    assert ctx.generation is not None
    ranking_result = ctx.extra["ranking_result"]
    panel = ctx.extra["brand_truth_panel"]

    en_scorecards: list[Scorecard] = ranking_result.top_by_language.get(GENERATION_LANGUAGE, [])
    spin_results: dict[str, spin_module.SpinResult] = {}
    for sc in en_scorecards:
        result = spin_module.spin_for_scorecard(
            sc, panel.facts, mapping_distance_bands=ctx.generation.mapping_distance
        )
        spin_results[sc.cluster_key] = result
        trace.decision(
            "spin", decision=result.rationale_line,
            rule="ARCHITECTURE_PLAN §6.9/§12.1: every asset records its one-line spin rationale",
        )

    cs_holds: list[dict[str, str]] = []
    for language, scorecards in ranking_result.top_by_language.items():
        if language == GENERATION_LANGUAGE:
            continue
        for sc in scorecards:
            cs_holds.append(
                {
                    "cluster_key": sc.cluster_key, "topic": sc.representative_title, "language": language,
                    "outcome": "hold — Czech copy not in goal scope",
                }
            )
            trace.decision(
                "spin",
                decision=f"{language} candidate '{sc.representative_title}' — hold: Czech copy not in goal scope",
                rule="GOAL_ROADMAP.md M3: English-only for this goal's finish line",
            )

    ctx.extra["spin_results"] = spin_results
    ctx.extra["cs_holds"] = cs_holds

    # Persist everything ``--resume`` will need to re-enter copy/media/
    # packaging/digest without re-running collection/ranking/brand_truth/
    # spin (module docstring in ``resume_state.py``). Written on every run,
    # unconditionally -- not gated on whether any asset ends up held --
    # so any run_id can later be resumed.
    run_dir = ctx.logs_dir / "runs" / ctx.run_id
    resume_state_module.write_resume_state(
        run_dir,
        resume_state_module.ResumeState(
            languages=list(ctx.research.languages),
            ranking_result=ranking_result,
            brand_truth_panel=panel,
            spin_results=spin_results,
            cs_holds=cs_holds,
            degraded_sources=list(ctx.extra.get("degraded_sources", [])),
            viral_playbook_path=ctx.extra.get("viral_playbook_path"),
        ),
    )

    return StageResult(
        outcome="ok",
        items_in=len(en_scorecards) + len(cs_holds),
        items_out=len(spin_results),
        extra={"cs_hold_count": len(cs_holds)},
    )


def _build_copy_provider(ctx: RunContext, run_dir: Path, trace: TraceWriter | None = None) -> copy_gen.TextModel:
    """Provider selection (W8-9 Q3b): ``openrouter`` is the enabled LLM
    path — it only actually activates when ``generation.llm.enabled`` is
    true AND an API key resolves (``_get_or_build_llm_client`` returns a
    client); otherwise this falls through to ``InteractiveFileProvider``,
    exactly the same degrade-to-fallback posture ``openai-compatible-http``
    already had for its own disabled/unconfigured case. ``trace`` is
    ``None``-safe as long as the LLM is disabled (the common case in tests
    that construct a provider directly without a live pipeline run) —
    ``_get_or_build_llm_client`` never touches ``trace`` on that path."""
    assert ctx.generation is not None
    if ctx.generation.copy_provider == "openrouter" and trace is not None:
        llm_client = _get_or_build_llm_client(ctx, trace, stage="copy")
        if llm_client is not None:
            style_guide = _load_style_guide_safe(ctx)
            viral_playbook = ctx.extra.get("viral_playbook")
            if viral_playbook is None:
                playbook_path = ctx.extra.get("viral_playbook_path")
                if playbook_path:
                    viral_playbook = analysis.load_viral_playbook_file(Path(playbook_path))
            brand_identity = ""
            panel = ctx.extra.get("brand_truth_panel")
            if panel is not None:
                brand_identity = str(
                    panel.facts.identity.get("one_liner_en") or panel.facts.identity.get("legal_name") or ""
                )
            return copy_gen.OpenRouterProvider(
                llm_client=llm_client, style_guide=style_guide, viral_playbook=viral_playbook,
                brand_identity_one_liner=brand_identity, trace=trace, stage="copy",
            )
    if ctx.generation.copy_provider == "openai-compatible-http" and ctx.generation.openai_compatible.enabled:
        fetcher = ctx.fetcher_factory() if ctx.fetcher_factory is not None else UrllibFetcher()
        return copy_gen.OpenAICompatibleProvider(ctx.generation.openai_compatible, fetcher)
    return copy_gen.InteractiveFileProvider(run_dir)


def stage_copy(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """Build a copy request per (EN topic x destination), run it through the
    configured ``TextModel`` provider, and gate the result deterministically
    (§14.0 repair budget, §14.3 claim gate, §14.6 disclosure floor).

    Refuses entirely — no requests written, no provider called — if brand
    truth degraded to research-only this run (stale snapshot); this is the
    stage-ordering guarantee that makes "copy spend is zero on the degrade
    path" true by construction rather than by assertion (§6.5)."""
    assert ctx.generation is not None and ctx.theme_config is not None
    panel = ctx.extra["brand_truth_panel"]
    spin_results: dict[str, spin_module.SpinResult] = ctx.extra.get("spin_results", {})
    run_dir = ctx.logs_dir / "runs" / ctx.run_id

    if not panel.copy_allowed:
        trace.decision(
            "copy",
            decision="copy stage refuses — brand truth is research-only this run (stale claim snapshot)",
            rule="ARCHITECTURE_PLAN §6.5 degrade posture, simplified to one trigger for this goal",
        )
        ctx.extra["copy_asset_statuses"] = []
        return StageResult(outcome="degraded", items_in=len(spin_results), items_out=0, extra={"copy_refused": True})

    if not spin_results:
        ctx.extra["copy_asset_statuses"] = []
        return StageResult(outcome="ok", items_in=0, items_out=0)

    provider = _build_copy_provider(ctx, run_dir, trace)
    negative_capabilities = panel.facts.capabilities_negative
    pricing_policy_line = f"{panel.facts.pricing_policy}: {panel.facts.pricing_rationale}".strip()
    allowed_facts = [
        {
            "claim_key": c.claim_key, "text_cs": c.text_cs, "behavior": c.behavior,
            "qualification": c.qualification, "category": c.category, "verified": c.verified,
        }
        for c in panel.snapshot.claims
    ]
    ranking_result = ctx.extra["ranking_result"]

    statuses: list[copy_gen.AssetCopyStatus] = []
    for cluster_key, sr in spin_results.items():
        canonical_keys = ranking_result.candidate_canonical_keys.get(cluster_key, [])
        for destination in ctx.generation.destinations:
            asset_id = f"{cluster_key}_{destination}"
            request = copy_gen.build_copy_request(
                asset_id=asset_id, destination=destination, spin=sr,
                excerpt_refs=canonical_keys, allowed_facts=allowed_facts,
                negative_capabilities=negative_capabilities, pricing_policy_line=pricing_policy_line,
                hard_excludes=ctx.theme_config.hard_excludes, exemplar_pool_paths=ctx.generation.exemplar_pool,
                snapshot_id=panel.snapshot.snapshot_id,
            )
            status = copy_gen.process_copy_asset(
                provider=provider, request=request, snapshot=panel.snapshot,
                hard_excludes=ctx.theme_config.hard_excludes, max_attempts=ctx.generation.repair_budget,
                trace=trace, stage="copy", run_dir=run_dir,
            )
            statuses.append(status)

    ctx.extra["copy_asset_statuses"] = statuses
    held = sum(1 for s in statuses if s.status.startswith("held"))
    blocked = sum(1 for s in statuses if s.status.startswith("blocked"))
    passed = sum(1 for s in statuses if s.status == "gated-pass")
    return StageResult(
        outcome="ok",
        items_in=len(spin_results) * max(1, len(ctx.generation.destinations)),
        items_out=len(statuses),
        extra={"held": held, "blocked": blocked, "gated_pass": passed},
    )


def _craft_media_prompts_for_run(
    ctx: RunContext, trace: TraceWriter, copy_statuses: list[copy_gen.AssetCopyStatus]
) -> dict[str, promptcraft.CraftedPromptSet]:
    """N-D Image-Prompt Crafter (W8-9 Q3c), invoked from the media stage:
    one crafted prompt set per gated-pass copy asset. Persists
    ``media_prompts.yaml`` and is resume-idempotent — an asset_id already
    present on disk is reused rather than re-crafted (and re-spent) on a
    ``--resume`` re-entry into ``media``."""
    run_dir = ctx.logs_dir / "runs" / ctx.run_id
    gated = [s for s in copy_statuses if s.status == "gated-pass"]
    if not gated:
        return {}

    existing = promptcraft.load_media_prompts(run_dir)
    prompt_sets: dict[str, promptcraft.CraftedPromptSet] = dict(existing)
    to_craft = [s for s in gated if s.asset_id not in prompt_sets]
    if not to_craft:
        return prompt_sets

    llm_client = _get_or_build_llm_client(ctx, trace, stage="media")
    style_guide = _load_style_guide_safe(ctx)
    viral_playbook = ctx.extra.get("viral_playbook")
    if viral_playbook is None:
        playbook_path = ctx.extra.get("viral_playbook_path")
        if playbook_path:
            viral_playbook = analysis.load_viral_playbook_file(Path(playbook_path))
    spin_results: dict[str, spin_module.SpinResult] = ctx.extra.get("spin_results", {})
    panel = ctx.extra.get("brand_truth_panel")
    hard_excludes = ctx.theme_config.hard_excludes if ctx.theme_config is not None else None

    for status in to_craft:
        sr = spin_results.get(status.cluster_key)
        topic = sr.topic if sr is not None else None
        theme_playbook = viral_playbook.theme_playbook(topic) if viral_playbook is not None else None
        series_token = promptcraft.series_token_for(ctx.run_id, status.cluster_key)
        prompt_set = promptcraft.craft_prompts(
            llm_client=llm_client, asset_id=status.asset_id, destination=status.destination,
            headline=status.headline or "", caption=status.caption or "", image_brief=status.image_brief or "",
            slides=status.slides, style_guide=style_guide, theme_playbook=theme_playbook, series_token=series_token,
            trace=trace, stage="media",
        )
        if panel is not None:
            prompt_set = promptcraft.gate_check_prompts(prompt_set, snapshot=panel.snapshot, hard_excludes=hard_excludes)
        prompt_sets[status.asset_id] = prompt_set

    promptcraft.write_media_prompts(run_dir, prompt_sets)
    return prompt_sets


def stage_media(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """Kie.ai draft-tier image generation (GOAL_ROADMAP.md M4): one image
    per gated-pass copy asset (§4.6: plan-only is always produced for
    everything else -- held-awaiting-copy assets plan only, zero cost).

    Fail-closed only on genuine machinery faults (bad registry, a
    tier-ceiling violation) via :class:`media_gen.MediaGenerationError`,
    which propagates like every other stage exception. A missing/unreadable
    Kie key file is this stage's own degrade condition (mirrors
    ``collectors/virlo.py``'s posture for its own key file): every
    gated-pass asset plans only, at zero cost, and the run continues."""
    assert ctx.generation is not None and ctx.store is not None
    copy_statuses = ctx.extra.get("copy_asset_statuses") or []
    crafted_prompts = _craft_media_prompts_for_run(ctx, trace, copy_statuses)
    plans = media_gen.plan_media_assets(copy_statuses, language=GENERATION_LANGUAGE, crafted_prompts=crafted_prompts)
    if not plans:
        ctx.extra["media_asset_statuses"] = []
        return StageResult(outcome="ok", items_in=0, items_out=0)

    media_cfg = ctx.generation.media
    registry = media_gen.load_model_registry(ctx.config_dir / "model_registry.yaml")

    secrets_dir = ctx.secrets_dir or (ctx.config_dir.parent / "secrets")
    key_path = Path(media_cfg.key_path) if media_cfg.key_path else (secrets_dir / "kie.key")
    # W8-9 Phase 1: real environment variable > repo-root .env > this legacy
    # key file (deprecated, still supported) — same fail-closed-to-degrade
    # posture as before either way (§4.6: plan-only, never a hard failure).
    api_key, _key_source = config_load.resolve_secret("KIE_API_KEY", config_dir=ctx.config_dir, legacy_path=key_path)
    if api_key is None and not key_path.exists():
        trace.decision(
            "media",
            decision=f"Kie API key file missing at {key_path} — every gated-pass asset plans only, zero spend",
            rule="ARCHITECTURE_PLAN §4.6: plan-only is always produced, even with no keys and no budget",
        )
        statuses = [_plan_only_status(p) for p in plans]
        ctx.extra["media_asset_statuses"] = statuses
        return StageResult(outcome="ok", items_in=len(plans), items_out=len(statuses))

    if not api_key:
        trace.decision(
            "media",
            decision=f"Kie API key file at {key_path} is empty — every gated-pass asset plans only, zero spend",
            rule="ARCHITECTURE_PLAN §4.6: plan-only is always produced, even with no keys and no budget",
        )
        statuses = [_plan_only_status(p) for p in plans]
        ctx.extra["media_asset_statuses"] = statuses
        return StageResult(outcome="ok", items_in=len(plans), items_out=len(statuses))

    fetcher = ctx.fetcher_factory() if ctx.fetcher_factory is not None else UrllibFetcher()
    run_dir = ctx.logs_dir / "runs" / ctx.run_id
    pack_media_dir = run_dir / "pack" / "media"
    pack_media_dir.mkdir(parents=True, exist_ok=True)

    kie_client = media_gen.KieClient(fetcher=fetcher, api_key=api_key, trace=trace, registry=registry, stage="media")
    # W8-9 Q4 N-E vision-QA reuses the SAME shared LlmClient the N-D prompt
    # crafter above already built/cached on ``ctx.extra`` -- one per-run
    # budget across analysis/copy/prompt-craft/vision-QA together, exactly
    # the discipline ``_get_or_build_llm_client`` exists to enforce.
    llm_client = _get_or_build_llm_client(ctx, trace, stage="media")
    generator = media_gen.MediaGenerator(
        store=ctx.store, trace=trace, registry=registry, media_config=media_cfg, kie_client=kie_client,
        theme=ctx.theme_name, run_id=ctx.run_id, run_date=ctx.run_date, pack_media_dir=pack_media_dir,
        llm_client=llm_client,
    )
    result = generator.process(plans)
    ctx.extra["media_asset_statuses"] = result.statuses
    ctx.extra["media_stage_result"] = result

    budget_capped = any(
        s.status in (media_gen.STATUS_BUDGET_CAPPED, media_gen.STATUS_COUNT_CAPPED) for s in result.statuses
    )
    outcome = "ok"
    extra: dict[str, Any] = {
        "generated": sum(1 for s in result.statuses if s.status == "generated"),
        "pending": result.pending_count,
        "submitted_unknown": result.submitted_unknown_count,
        "circuit_breaker_tripped": result.circuit_breaker_tripped,
        "spent_usd": round(result.total_spent_usd, 4),
    }
    if budget_capped:
        outcome = "degraded"
        extra["budget_capped_mid_pack"] = True
    elif result.circuit_breaker_tripped:
        outcome = "degraded"
    elif result.pending_count:
        outcome = "degraded"
        extra["pending_media_only"] = True

    return StageResult(outcome=outcome, items_in=len(plans), items_out=len(result.statuses), extra=extra)


def _plan_only_status(plan: media_gen.MediaAssetPlan) -> media_gen.MediaAssetStatus:
    if plan.copy_status.startswith("held"):
        status = "awaiting copy — not submitted"
    elif plan.copy_status == "gated-pass":
        status = "plan-only — no Kie API key configured"
    else:
        status = "not generated — copy blocked (no approved brief)"
    return media_gen.MediaAssetStatus(
        asset_id=plan.asset_id, cluster_key=plan.cluster_key, destination=plan.destination, status=status,
    )


def stage_packaging(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """Write scorecards + signal provenance, register canonical keys."""
    assert ctx.store is not None and ctx.research is not None
    ranking_result = ctx.extra["ranking_result"]
    run_dir = ctx.logs_dir / "runs" / ctx.run_id

    summary = packaging.package_candidates(
        run_id=ctx.run_id,
        run_dir=run_dir,
        store=ctx.store,
        ranking_result=ranking_result,
        languages=ctx.research.languages,
    )
    ctx.extra["pack_dir"] = summary.pack_dir

    for path in [*summary.scorecard_paths, *summary.signal_paths]:
        data = path.read_bytes()
        kind = "scorecard" if path.parent.name == "scorecards" else "pack"
        trace.artifact_write("packaging", path=str(path), kind=kind, bytes_=len(data), sha256=_sha256_hex(data))

    return StageResult(
        outcome="ok",
        items_in=len(ranking_result.all_scorecards),
        items_out=summary.registered_keys,
        output_refs=[{"path": str(summary.pack_dir), "sha256": ""}],
    )


def stage_digest(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """Render and write ``digest.md`` — the run's single entry point."""
    assert ctx.research is not None
    ranking_result = ctx.extra["ranking_result"]
    degraded_sources = ctx.extra.get("degraded_sources", [])
    run_dir = ctx.logs_dir / "runs" / ctx.run_id

    digest_path = packaging.write_digest(
        run_id=ctx.run_id,
        run_date=ctx.run_date,
        theme_name=ctx.theme_name,
        run_dir=run_dir,
        ranking_result=ranking_result,
        degraded_sources=degraded_sources,
        languages=ctx.research.languages,
        brand_truth_panel=ctx.extra.get("brand_truth_panel"),
        spin_results=ctx.extra.get("spin_results"),
        copy_asset_statuses=ctx.extra.get("copy_asset_statuses"),
        cs_holds=ctx.extra.get("cs_holds"),
        media_asset_statuses=ctx.extra.get("media_asset_statuses"),
        media_registry_price_snapshot_date=_media_price_snapshot_date(ctx),
    )
    data = digest_path.read_bytes()
    trace.artifact_write("digest", path=str(digest_path), kind="digest", bytes_=len(data), sha256=_sha256_hex(data))

    return StageResult(
        outcome="ok",
        items_in=1,
        items_out=1,
        output_refs=[{"path": str(digest_path), "sha256": _sha256_hex(data)}],
    )


def _media_price_snapshot_date(ctx: RunContext) -> str | None:
    try:
        registry = media_gen.load_model_registry(ctx.config_dir / "model_registry.yaml")
    except Exception:
        return None
    return registry.price_snapshot_date


CANONICAL_STAGES: tuple[tuple[str, StageFn], ...] = (
    ("theme_load", stage_theme_load),
    ("collection", stage_collection),
    ("analysis", stage_analysis),
    ("ranking", stage_ranking),
    ("brand_truth", stage_brand_truth),
    ("spin", stage_spin),
    ("copy", stage_copy),
    ("media", stage_media),
    ("packaging", stage_packaging),
    ("digest", stage_digest),
)


# The subset re-entered by ``python -m hypeagent --resume <run_id>``
# (main.py): collection/ranking/brand_truth/spin are never re-run on
# resume -- their outputs are read back from ``resume_state.yaml``
# (persisted once by ``stage_spin`` on every ordinary run) instead of being
# re-derived, so a resume can never re-hit cross-day dedupe or silently pick
# up a different claim-ledger snapshot than the original run gated against.
RESUME_STAGE_NAMES: tuple[str, ...] = ("copy", "media", "packaging", "digest")


def _run_stage_list(ctx: RunContext, trace: TraceWriter, stage_list: tuple[tuple[str, StageFn], ...]) -> str:
    """Run ``stage_list`` in order, exactly as ``run_pipeline`` always has;
    factored out so ``resume_pipeline`` gets identical per-stage trace and
    exit-class semantics over its own (smaller) stage subset.

    Returns the exit-class string. A degraded ``collection`` stage maps to
    ``partial-success — degraded sources`` (§8.8); a degrade anywhere else
    maps to the more general ``completed-degraded``. If a stage raises,
    this function logs a trace ``error`` event for that stage and
    re-raises without writing ``stage_end`` — the trace deliberately ends
    at the error, exactly as a genuine crash would leave it
    (RUN_TRACE_SPEC §5(b)). Callers decide the resulting exit class and are
    responsible for run-level cleanup (e.g. closing ``ctx.store``).
    """
    degraded = False
    degraded_class: str | None = None
    for stage_name, fn in stage_list:
        trace.stage_start(stage_name)
        try:
            result = fn(ctx, trace)
        except Exception as exc:
            trace.error(
                stage_name,
                error_class=type(exc).__name__,
                message=str(exc),
                retried=False,
                disposition="stage aborted — run fails closed",
            )
            raise
        trace.stage_end(
            stage_name,
            outcome=result.outcome,
            items_in=result.items_in,
            items_out=result.items_out,
            input_refs=result.input_refs,
            output_refs=result.output_refs,
            **result.extra,
        )
        if result.outcome == "degraded":
            degraded = True
            if stage_name == "collection":
                degraded_class = ExitClass.PARTIAL_SUCCESS_DEGRADED_SOURCES.value
            elif stage_name == "media" and result.extra.get("budget_capped_mid_pack"):
                degraded_class = ExitClass.PARTIAL_SUCCESS_BUDGET_CAPPED_MID_PACK.value
            elif stage_name == "media" and result.extra.get("pending_media_only") and degraded_class is None:
                degraded_class = ExitClass.COMPLETED_WITH_PENDING_MEDIA.value
            elif degraded_class is None:
                degraded_class = ExitClass.COMPLETED_DEGRADED.value
    if degraded:
        return degraded_class or ExitClass.COMPLETED_DEGRADED.value
    return ExitClass.SUCCESS.value


def _generate_process_summary_best_effort(ctx: RunContext, trace: TraceWriter, exit_class: str) -> None:
    """W8-8: the process summary is generated at the end of every run and
    every ``--resume``, best-effort. A summarizer crash must never change
    the run's exit class -- it is caught here, logged as an ``error`` trace
    event (so it is visible without ever affecting what ``main.py`` writes
    to the run ledger or returns as the process exit code), and swallowed."""
    try:
        process_summary.generate_process_summary(
            ctx.run_id,
            config_dir=ctx.config_dir,
            logs_dir=ctx.logs_dir,
            secrets_dir=ctx.secrets_dir,
            exit_class=exit_class,
        )
    except Exception as exc:  # noqa: BLE001 - deliberately broad: never fail the run for this
        trace.error(
            "digest",
            error_class=type(exc).__name__,
            message=f"process summary generation failed: {exc}",
            retried=False,
            disposition="process summary skipped — run exit class unaffected",
        )


def run_pipeline(ctx: RunContext, trace: TraceWriter) -> str:
    """Run all canonical stages in order. See :func:`_run_stage_list` for
    the exit-class mapping and error/crash semantics."""
    exit_class = _run_stage_list(ctx, trace, CANONICAL_STAGES)
    _generate_process_summary_best_effort(ctx, trace, exit_class)
    return exit_class


def prepare_resume_context(ctx: RunContext) -> None:
    """Load config + open the store for ``--resume`` (main.py), without
    repeating ``theme_load``'s own trace events or its run-start retention-
    expiry job -- both already ran once for this run_id at its original
    invocation. Resume only needs the config objects and a live store handle
    to re-enter copy/media/packaging/digest."""
    _load_theme_and_config(ctx)
    secrets_dir = ctx.secrets_dir or (ctx.config_dir.parent / "secrets")
    ctx.store = Store.open(ctx.logs_dir, secrets_dir, config_dir=ctx.config_dir)


def resume_pipeline(ctx: RunContext, trace: TraceWriter, resume_state: resume_state_module.ResumeState) -> str:
    """``python -m hypeagent --resume <run_id>``'s stage subset (main.py):
    re-enters ONLY copy -> media -> packaging -> digest, against the
    ranking/brand-truth/spin output ``resume_state`` carries in from
    ``resume_state.yaml`` (never re-derived). Collection, ranking,
    brand_truth and spin are not re-run this invocation; per-stage trace
    and exit-class semantics are otherwise identical to a normal run's
    (shared :func:`_run_stage_list`)."""
    prepare_resume_context(ctx)
    ctx.extra["ranking_result"] = resume_state.ranking_result
    ctx.extra["brand_truth_panel"] = resume_state.brand_truth_panel
    ctx.extra["spin_results"] = resume_state.spin_results
    ctx.extra["cs_holds"] = resume_state.cs_holds
    ctx.extra["degraded_sources"] = resume_state.degraded_sources
    ctx.extra["viral_playbook_path"] = resume_state.viral_playbook_path
    resume_stages = tuple((name, fn) for name, fn in CANONICAL_STAGES if name in RESUME_STAGE_NAMES)
    exit_class = _run_stage_list(ctx, trace, resume_stages)
    _generate_process_summary_best_effort(ctx, trace, exit_class)
    return exit_class
