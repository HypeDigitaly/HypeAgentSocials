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
from hypeagent import render_trace, run_identity, run_ledger, stages
from hypeagent.config_load import ConfigError
from hypeagent.exit_codes import EXIT_CODE_MAP, ExitClass
from hypeagent.store import Store
from hypeagent.trace import TraceWriter


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
    store = Store.open(logs_dir, secrets_dir)
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
