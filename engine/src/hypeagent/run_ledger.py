"""The run ledger: one append-only JSONL line per run.

Complements — never replaces — the trace (RUN_TRACE_SPEC.md, intro): the
trace says what a run did, in order; the ledger says what it concluded and
carries the trace's own path for cross-reference.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def append_ledger_entry(
    ledger_path: Path,
    *,
    run_id: str,
    started_at: datetime,
    ended_at: datetime,
    exit_class: str,
    trace_path: Path,
    resume: bool = False,
) -> None:
    """Append one run's outcome to ``logs/run_ledger.jsonl``.

    ``resume=True`` (``main.py``'s ``--resume <run_id>``) marks this row as a
    resumed invocation of an *existing* ``run_id`` rather than a fresh one —
    the ledger stays append-only (never rewritten/updated in place), so more
    than one line can legitimately share a ``run_id``; a resumed run's full
    history is every line whose ``run_id`` matches, in ``started_at`` order.
    The key is only ever written when true, so an ordinary run's ledger row
    is byte-for-byte identical to what it always was."""
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    entry: dict[str, object] = {
        "run_id": run_id,
        "started_at": started_at.isoformat(timespec="milliseconds"),
        "ended_at": ended_at.isoformat(timespec="milliseconds"),
        "exit_class": exit_class,
        "trace_path": str(trace_path),
    }
    if resume:
        entry["resume"] = True
    with open(ledger_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        fh.flush()
