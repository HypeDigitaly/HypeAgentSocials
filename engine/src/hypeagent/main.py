"""Entrypoint: ``python -m hypeagent``.

Full Phase-1 skeleton run: acquire the run-lock, run_start, execute the
stage pipeline, run_end, render trace.md, write logs/latest.txt, append the
run ledger, release the lock, exit with the mapped code.

Also supports ``python -m hypeagent --render <trace.jsonl>`` to
regenerate ``trace.md`` from an existing (possibly truncated) trace.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from hypeagent import __version__ as ENGINE_VERSION
from hypeagent import process_summary, render_trace, resume_state as resume_state_module, run_identity, run_ledger, stages
from hypeagent.config_load import ConfigError
from hypeagent.exit_codes import EXIT_CODE_MAP, ExitClass
from hypeagent.store import Store
from hypeagent.trace import TraceWriter, last_seq_in_trace

# ``--resume``'s own pre-flight refusal codes (RUN_TRACE_SPEC's nine exit
# classes are the *pipeline's* outcome taxonomy, §8.8 -- these two conditions
# are refused before any pipeline stage runs at all, so they get their own
# small, distinct codes rather than being folded into that enum). A held
# run-lock reuses ``skipped-overlap``'s own mapped code (75): it is the same
# condition (another live run holds the lock) under a different entrypoint.
EXIT_RESUME_TARGET_NOT_FOUND = 42


def _render_mode(argv: Sequence[str]) -> int:
    if len(argv) < 2:
        print("usage: python -m hypeagent --render <trace.jsonl>", file=sys.stderr)
        return 2
    jsonl_path = Path(argv[1])
    md_path = render_trace.render(jsonl_path)
    print(f"rendered {md_path}")
    return 0


def _delete_key_mode(argv: Sequence[str]) -> int:
    """``python -m hypeagent --delete-key <canonical_key>`` — targeted
    deletion (ARCHITECTURE_PLAN.md §2.6): the normalized record, raw
    references, and every archived run pack that included this key, via the
    run-pack -> canonical-key index."""
    if len(argv) < 2:
        print("usage: python -m hypeagent --delete-key <canonical_key>", file=sys.stderr)
        return 2
    canonical_key = argv[1]
    repo_root = Path.cwd()
    logs_dir = repo_root / "logs"
    secrets_dir = repo_root / "secrets"
    config_dir = repo_root / "config"
    store = Store.open(logs_dir, secrets_dir, config_dir=config_dir)
    try:
        report = store.delete_by_canonical_key(canonical_key)
    finally:
        store.close()
    print(
        f"deleted canonical key {canonical_key}: "
        f"normalized_record={report.normalized_record_deleted} "
        f"provenance={report.provenance_deleted} "
        f"packs_rewritten={len(report.packs_rewritten)}"
    )
    for path in report.packs_rewritten:
        print(f"  rewrote pack file: {path}")
    return 0


def _summarize_mode(argv: Sequence[str]) -> int:
    """``python -m hypeagent --summarize <run_id>`` (RUN_TRACE_SPEC.md §6,
    W8-8): (re)generate ``logs/runs/<run_id>/process_summary.md`` from the
    persisted facts already on disk for that run (``trace.jsonl``,
    ``resume_state.yaml``, the spend ledger, provenance YAMLs,
    ``copy_requests``/``copy_responses``) -- works for any existing run,
    including one produced by an older engine version that never persisted
    some of the newer fields (those lines degrade to an explicit
    "not recorded by this engine version" rather than failing outright).

    Refuses, with the same ``EXIT_RESUME_TARGET_NOT_FOUND`` code
    ``--resume`` uses for "not a valid run_id", when no ``trace.jsonl``
    exists for the given run_id -- there is nothing to summarize."""
    if not argv:
        print("usage: python -m hypeagent --summarize <run_id>", file=sys.stderr)
        return 2
    run_id = argv[0]

    repo_root = Path.cwd()
    config_dir = repo_root / "config"
    logs_dir = repo_root / "logs"
    run_dir = logs_dir / "runs" / run_id
    trace_path = run_dir / "trace.jsonl"

    if not run_dir.is_dir() or not trace_path.exists():
        print(
            f"cannot summarize {run_id!r}: no run directory with a trace.jsonl found at {trace_path}",
            file=sys.stderr,
        )
        return EXIT_RESUME_TARGET_NOT_FOUND

    path = process_summary.generate_process_summary(run_id, config_dir=config_dir, logs_dir=logs_dir)
    print(f"wrote {path}")
    return 0


def _resume_mode(argv: Sequence[str]) -> int:
    """``python -m hypeagent --resume <run_id>``.

    Re-enters ONLY copy/media/packaging/digest for an existing run (see
    ``stages.resume_pipeline`` / ``resume_state.py`` module docstrings for
    why collection/ranking/brand_truth/spin are never re-run here). Refuses,
    each with a distinct exit code and no side effects on the target run's
    own trace/ledger, when:

    - ``<run_id>`` was not given at all (usage error, exit 2 — same
      convention as ``--render``/``--delete-key``).
    - ``logs/runs/<run_id>/`` does not exist, or has no ``trace.jsonl``
      (``EXIT_RESUME_TARGET_NOT_FOUND``).
    - the run never reached ``stage_spin`` (no ``resume_state.yaml`` on
      file — nothing to complete; also ``EXIT_RESUME_TARGET_NOT_FOUND``,
      since from the operator's perspective both are "not a resumable
      run_id").
    - the run-lock is already held by a live run (reuses
      ``skipped-overlap``'s mapped exit code; a resume must never write
      into a trace another process is actively appending to).

    Trace sequence numbering continues monotonically from the existing
    file's last ``seq`` (crash-truncation means that may not be a
    ``run_end`` line at all — resume proceeds regardless and marks its own
    start with a ``{"resume": true, "resumed_at_seq": N}`` decision event).
    The run ledger is append-only (``run_ledger.py``): a successful or
    failed resume adds a NEW row referencing the same ``run_id``, with its
    own ``started_at``/``ended_at`` — the same convention every other
    ledger consumer in this engine already has to handle for "more than one
    line can name the same run_id" (e.g. a resumed run's ledger history is
    simply every line whose ``run_id`` matches, in order).
    """
    if not argv:
        print("usage: python -m hypeagent --resume <run_id>", file=sys.stderr)
        return 2
    run_id = argv[0]

    repo_root = Path.cwd()
    config_dir = repo_root / "config"
    logs_dir = repo_root / "logs"
    lock_path = logs_dir / "run.lock"
    ledger_path = logs_dir / "run_ledger.jsonl"
    run_dir = logs_dir / "runs" / run_id
    trace_path = run_dir / "trace.jsonl"

    if not run_dir.is_dir() or not trace_path.exists():
        print(
            f"cannot resume {run_id!r}: no run directory with a trace.jsonl found at {trace_path}",
            file=sys.stderr,
        )
        return EXIT_RESUME_TARGET_NOT_FOUND

    resume_state = resume_state_module.load_resume_state(run_dir)
    if resume_state is None:
        print(
            f"cannot resume {run_id!r}: no resume state on file at "
            f"{run_dir / resume_state_module.RESUME_STATE_FILENAME} "
            "(the run never reached the spin stage, so there is nothing to complete)",
            file=sys.stderr,
        )
        return EXIT_RESUME_TARGET_NOT_FOUND

    lock = run_identity.RunLock(lock_path)
    try:
        lock.acquire()
    except run_identity.RunLockHeld:
        print(f"cannot resume {run_id!r}: run-lock already held by a live run", file=sys.stderr)
        return EXIT_CODE_MAP[ExitClass.SKIPPED_OVERLAP]

    started_at = datetime.now().astimezone()
    exit_class = ExitClass.SUCCESS
    crashed = False
    ctx: stages.RunContext | None = None
    ended_at = started_at
    resumed_at_seq = last_seq_in_trace(trace_path)
    tw = TraceWriter(trace_path, run_id, initial_seq=resumed_at_seq)
    try:
        tw.resume_marker(resumed_at_seq=resumed_at_seq)
        ctx = stages.RunContext(
            run_id=run_id, config_dir=config_dir, logs_dir=logs_dir, theme_name=stages.DEFAULT_THEME_NAME
        )
        try:
            exit_class_value = stages.resume_pipeline(ctx, tw, resume_state)
            exit_class = ExitClass(exit_class_value)
        except ConfigError:
            exit_class = ExitClass.POLICY_STOP
            crashed = True
        except Exception:
            exit_class = ExitClass.HARD_FAILURE
            crashed = True

        ended_at = datetime.now().astimezone()
        if not crashed:
            duration_ms = int((ended_at - started_at).total_seconds() * 1000)
            tw.run_end(
                exit_class.value,
                totals={
                    "duration_ms": duration_ms,
                    "api_calls_per_platform": {},
                    "spend_per_wallet": {},
                    "items_per_stage": {},
                    "degrades_count": 0,
                    "resume": True,
                },
            )
    finally:
        if ctx is not None and ctx.store is not None:
            ctx.store.close()
        tw.close()
        lock.release()

    render_trace.render(trace_path)

    latest_path = logs_dir / "latest.txt"
    latest_path.write_text(str(run_dir), encoding="utf-8")

    run_ledger.append_ledger_entry(
        ledger_path,
        run_id=run_id,
        started_at=started_at,
        ended_at=ended_at,
        exit_class=exit_class.value,
        trace_path=trace_path,
        resume=True,
    )

    return EXIT_CODE_MAP[exit_class]


def _write_skipped_overlap(
    *,
    identity: run_identity.RunIdentity,
    run_dir: Path,
    trace_path: Path,
    ledger_path: Path,
) -> ExitClass:
    """Record a skipped-overlap outcome without touching the live run."""
    tw = TraceWriter(trace_path, identity.run_id)
    try:
        tw.run_start(
            mode="interactive",
            theme=None,
            config_fingerprint=None,
            engine_version=ENGINE_VERSION,
            caps_in_force={},
        )
        tw.run_end(
            ExitClass.SKIPPED_OVERLAP.value,
            totals={"duration_ms": 0, "reason": "run-lock already held by a live run"},
        )
    finally:
        tw.close()
    render_trace.render(trace_path)
    run_ledger.append_ledger_entry(
        ledger_path,
        run_id=identity.run_id,
        started_at=identity.started_at,
        ended_at=datetime.now().astimezone(),
        exit_class=ExitClass.SKIPPED_OVERLAP.value,
        trace_path=trace_path,
    )
    return ExitClass.SKIPPED_OVERLAP


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv) if argv is not None else sys.argv[1:]

    if args and args[0] == "--render":
        return _render_mode(args)

    if args and args[0] == "--delete-key":
        return _delete_key_mode(args)

    if args and args[0] == "--resume":
        return _resume_mode(args[1:])

    if args and args[0] == "--summarize":
        return _summarize_mode(args[1:])

    repo_root = Path.cwd()
    config_dir = repo_root / "config"
    logs_dir = repo_root / "logs"
    lock_path = logs_dir / "run.lock"
    ledger_path = logs_dir / "run_ledger.jsonl"

    identity = run_identity.new_run_identity()
    run_dir = logs_dir / "runs" / identity.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    trace_path = run_dir / "trace.jsonl"

    lock = run_identity.RunLock(lock_path)
    try:
        lock.acquire()
    except run_identity.RunLockHeld:
        exit_class = _write_skipped_overlap(
            identity=identity,
            run_dir=run_dir,
            trace_path=trace_path,
            ledger_path=ledger_path,
        )
        return EXIT_CODE_MAP[exit_class]

    started_at = identity.started_at
    exit_class = ExitClass.SUCCESS
    crashed = False
    theme_name = stages.DEFAULT_THEME_NAME
    ctx: stages.RunContext | None = None
    tw = TraceWriter(trace_path, identity.run_id)
    try:
        tw.run_start(
            mode="interactive",
            theme=theme_name,
            config_fingerprint=None,
            engine_version=ENGINE_VERSION,
            caps_in_force={},
        )
        ctx = stages.RunContext(
            run_id=identity.run_id, config_dir=config_dir, logs_dir=logs_dir, theme_name=theme_name
        )
        try:
            exit_class_value = stages.run_pipeline(ctx, tw)
            exit_class = ExitClass(exit_class_value)
        except ConfigError:
            exit_class = ExitClass.POLICY_STOP
            crashed = True
        except Exception:
            exit_class = ExitClass.HARD_FAILURE
            crashed = True

        ended_at = datetime.now().astimezone()
        if not crashed:
            duration_ms = int((ended_at - started_at).total_seconds() * 1000)
            tw.run_end(
                exit_class.value,
                totals={
                    "duration_ms": duration_ms,
                    "api_calls_per_platform": {},
                    "spend_per_wallet": {},
                    "items_per_stage": {},
                    "degrades_count": 0,
                },
            )
    finally:
        if ctx is not None and ctx.store is not None:
            ctx.store.close()
        tw.close()
        lock.release()

    render_trace.render(trace_path)

    latest_path = logs_dir / "latest.txt"
    latest_path.write_text(str(run_dir), encoding="utf-8")

    run_ledger.append_ledger_entry(
        ledger_path,
        run_id=identity.run_id,
        started_at=started_at,
        ended_at=ended_at,
        exit_class=exit_class.value,
        trace_path=trace_path,
    )

    return EXIT_CODE_MAP[exit_class]


if __name__ == "__main__":
    sys.exit(main())
