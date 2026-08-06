"""Stage-runner framework (ARCHITECTURE_PLAN.md §9, §17.2 Phase-1 skeleton).

Phase 1 is "the narrowest end-to-end run that produces something a human
can read" — theme load with fail-closed checking, collection, ranking,
packaging, and the run digest. No brand truth, no generation, no money.

Every Phase-1 stage below is a STUB: it logs honest zero-item input/output
counts and makes zero external API calls. The pipeline shape (canonical
order, per-stage trace events, degrade propagation) is real; the work
inside each stage is not, yet.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hypeagent.config_load import ThemeConfig, load_theme_config
from hypeagent.exit_codes import ExitClass
from hypeagent.trace import TraceWriter

# Canonical Phase-1 stage order (§17.2).
CANONICAL_STAGE_NAMES: tuple[str, ...] = (
    "theme_load",
    "collection",
    "ranking",
    "packaging",
    "digest",
)


@dataclass
class RunContext:
    """Mutable state threaded through the stage pipeline for one run."""

    run_id: str
    config_dir: Path
    logs_dir: Path
    theme_config: ThemeConfig | None = None
    extra: dict[str, Any] = field(default_factory=dict)


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
    """Fail-closed config/theme load. Raises ConfigError on missing/unreadable items."""
    ctx.theme_config = load_theme_config(ctx.config_dir)
    resolved_empty = [
        name for name, item in ctx.theme_config.hard_excludes.items() if item.state == "resolved-empty"
    ]
    return StageResult(
        outcome="ok",
        items_in=0,
        items_out=len(ctx.theme_config.hard_excludes),
        extra={"resolved_empty_lists": resolved_empty},
    )


def stage_collection(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """STUB: no collectors wired yet. Zero external calls, zero cost."""
    return StageResult(outcome="ok", items_in=0, items_out=0)


def stage_ranking(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """STUB: nothing to rank yet."""
    return StageResult(outcome="ok", items_in=0, items_out=0)


def stage_packaging(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """STUB: nothing to package yet."""
    return StageResult(outcome="ok", items_in=0, items_out=0)


def stage_digest(ctx: RunContext, trace: TraceWriter) -> StageResult:
    """STUB: nothing to summarise yet."""
    return StageResult(outcome="ok", items_in=0, items_out=0)


CANONICAL_STAGES: tuple[tuple[str, StageFn], ...] = (
    ("theme_load", stage_theme_load),
    ("collection", stage_collection),
    ("ranking", stage_ranking),
    ("packaging", stage_packaging),
    ("digest", stage_digest),
)


def run_pipeline(ctx: RunContext, trace: TraceWriter) -> str:
    """Run all canonical stages in order.

    Returns the exit-class string (``success`` or ``completed-degraded`` if
    any stage degraded). If a stage raises, this function logs a trace
    ``error`` event for that stage and re-raises without writing
    ``stage_end`` — the trace deliberately ends at the error, exactly as a
    genuine crash would leave it (RUN_TRACE_SPEC §5(b)). Callers decide the
    resulting exit class and are responsible for run-level cleanup.
    """
    degraded = False
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
    return ExitClass.COMPLETED_DEGRADED.value if degraded else ExitClass.SUCCESS.value
