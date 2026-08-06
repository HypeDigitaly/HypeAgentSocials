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

from hypeagent import packaging
from hypeagent.collectors import google_news, hackernews, huggingface, producthunt
from hypeagent.collectors.base import CollectContext, Fetcher, UrllibFetcher, to_normalized_signal
from hypeagent.config_load import (
    ThemeConfig,
    ThemeResearchConfig,
    load_theme_config,
    load_theme_research_config,
)
from hypeagent.exit_codes import ExitClass
from hypeagent.ranking import (
    Phase1DeterministicFitJudge,
    Phase1DeterministicNewAngleJudge,
    RankingConfig,
    rank,
)
from hypeagent.store import SourceDenyList, SpecialCategoryLexicon, Store, load_source_deny_list, load_special_category_lexicon
from hypeagent.trace import TraceWriter

# Canonical Phase-1 stage order (§17.2).
CANONICAL_STAGE_NAMES: tuple[str, ...] = (
    "theme_load",
    "collection",
    "ranking",
    "packaging",
    "digest",
)

DEFAULT_THEME_NAME = "hypedigitaly"


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


def stage_theme_load(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """Fail-closed config/theme load, extended to load the theme's research
    block (§10.2), the special-category source deny-list and lexicon
    (§2.6), and to run the retention expiry job at run start."""
    ctx.theme_config = load_theme_config(ctx.config_dir)
    ctx.research = load_theme_research_config(ctx.config_dir, ctx.theme_name)
    ctx.deny_list = load_source_deny_list(ctx.config_dir / "special_category_source_deny_list.yaml")
    ctx.lexicon = load_special_category_lexicon(ctx.config_dir / "special_category_lexicon.yaml")

    secrets_dir = ctx.secrets_dir or (ctx.config_dir.parent / "secrets")
    ctx.store = Store.open(ctx.logs_dir, secrets_dir)

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
    )
    data = digest_path.read_bytes()
    trace.artifact_write("digest", path=str(digest_path), kind="digest", bytes_=len(data), sha256=_sha256_hex(data))

    return StageResult(
        outcome="ok",
        items_in=1,
        items_out=1,
        output_refs=[{"path": str(digest_path), "sha256": _sha256_hex(data)}],
    )


CANONICAL_STAGES: tuple[tuple[str, StageFn], ...] = (
    ("theme_load", stage_theme_load),
    ("collection", stage_collection),
    ("ranking", stage_ranking),
    ("packaging", stage_packaging),
    ("digest", stage_digest),
)


def run_pipeline(ctx: RunContext, trace: TraceWriter) -> str:
    """Run all canonical stages in order.

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
    for stage_name, fn in CANONICAL_STAGES:
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
            elif degraded_class is None:
                degraded_class = ExitClass.COMPLETED_DEGRADED.value
    if degraded:
        return degraded_class or ExitClass.COMPLETED_DEGRADED.value
    return ExitClass.SUCCESS.value
