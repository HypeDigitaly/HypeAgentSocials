"""Render ``trace.jsonl`` into the human-readable ``trace.md`` (RUN_TRACE_SPEC §1, §4).

Grouped by stage, with a timing waterfall (per-stage wall clock alongside
per-API cumulative latency) and an API-call table. Sequence gaps are
flagged ("events lost here") rather than hidden. Works line-by-line so a
truncated trace (crashed run) still renders everything it holds.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_events(jsonl_path: Path) -> tuple[list[dict[str, Any]], int]:
    """Parse a (possibly truncated) trace.jsonl.

    Returns ``(events, malformed_line_count)``. A malformed/truncated final
    line (e.g. a crash mid-write) is skipped, not fatal — the rest of the
    trace still renders.
    """
    events: list[dict[str, Any]] = []
    malformed = 0
    jsonl_path = Path(jsonl_path)
    if not jsonl_path.exists():
        return events, malformed
    with open(jsonl_path, "r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                malformed += 1
    return events, malformed


def detect_sequence_gaps(events: list[dict[str, Any]]) -> list[tuple[int, int]]:
    """Return (prev_seq, next_seq) pairs where seq is non-contiguous."""
    seqs = sorted(ev["seq"] for ev in events if "seq" in ev)
    gaps = []
    for prev, curr in zip(seqs, seqs[1:]):
        if curr != prev + 1:
            gaps.append((prev, curr))
    return gaps


def render(jsonl_path: Path, md_path: Path | None = None) -> Path:
    """Render ``jsonl_path`` to a markdown file, returning its path."""
    jsonl_path = Path(jsonl_path)
    out_path = Path(md_path) if md_path is not None else jsonl_path.with_name("trace.md")

    events, malformed = load_events(jsonl_path)
    run_id = events[0].get("run_id") if events else jsonl_path.parent.name
    gaps = detect_sequence_gaps(events)

    stage_order: list[str] = []
    stage_events: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        stage = ev.get("stage", "run")
        if stage not in stage_events:
            stage_events[stage] = []
            stage_order.append(stage)
        stage_events[stage].append(ev)

    api_calls_by_seq: dict[int, dict[str, Any]] = {
        ev["seq"]: ev for ev in events if ev.get("event") == "api_call"
    }
    api_rows: list[dict[str, Any]] = []
    for ev in events:
        if ev.get("event") != "api_response":
            continue
        detail = ev.get("detail", {})
        call = api_calls_by_seq.get(detail.get("seq_of_call"))
        call_detail = call.get("detail", {}) if call else {}
        api_rows.append(
            {
                "platform": call_detail.get("platform", "?"),
                "endpoint": call_detail.get("endpoint", "?"),
                "status": detail.get("status"),
                "latency_ms": detail.get("latency_ms"),
                "cost": detail.get("cost"),
            }
        )

    stage_durations: dict[str, Any] = {}
    for stage, evs in stage_events.items():
        for ev in evs:
            if ev.get("event") == "stage_end":
                stage_durations[stage] = ev.get("detail", {}).get("duration_ms")

    platform_latency: dict[str, int] = {}
    for row in api_rows:
        latency = row.get("latency_ms")
        if isinstance(latency, (int, float)):
            platform_latency[row["platform"]] = platform_latency.get(row["platform"], 0) + latency

    lines: list[str] = []
    lines.append(f"# Run Trace — {run_id}")
    lines.append("")

    if malformed:
        lines.append(
            f"> Note: {malformed} malformed/truncated trailing line(s) skipped "
            "(crash-safe: the rest of the trace still renders)."
        )
        lines.append("")

    if gaps:
        lines.append("## Sequence gaps — events lost here")
        lines.append("")
        for prev, curr in gaps:
            lines.append(f"- gap between seq {prev} and seq {curr} ({curr - prev - 1} event(s) missing)")
        lines.append("")

    lines.append("## Timing waterfall")
    lines.append("")
    lines.append("Per-stage wall clock:")
    lines.append("")
    lines.append("| stage | wall clock (ms) |")
    lines.append("|---|---|")
    for stage in stage_order:
        if stage == "run":
            continue
        lines.append(f"| {stage} | {stage_durations.get(stage, 'n/a')} |")
    lines.append("")
    lines.append("Per-API cumulative latency:")
    lines.append("")
    if platform_latency:
        lines.append("| platform | cumulative latency (ms) |")
        lines.append("|---|---|")
        for platform, total in platform_latency.items():
            lines.append(f"| {platform} | {total} |")
    else:
        lines.append("_No external API calls in this run._")
    lines.append("")

    lines.append("## API-call table")
    lines.append("")
    if api_rows:
        lines.append("| platform | endpoint | status | latency (ms) | cost |")
        lines.append("|---|---|---|---|---|")
        for row in api_rows:
            lines.append(
                f"| {row['platform']} | {row['endpoint']} | {row['status']} | "
                f"{row['latency_ms']} | {row['cost']} |"
            )
    else:
        lines.append("_No external API calls in this run._")
    lines.append("")

    lines.append("## Events by stage")
    for stage in stage_order:
        lines.append("")
        lines.append(f"### {stage}")
        lines.append("")
        for ev in stage_events[stage]:
            detail_json = json.dumps(ev.get("detail", {}), ensure_ascii=False)
            lines.append(f"- `seq={ev.get('seq')}` `{ev.get('ts')}` **{ev.get('event')}** — {detail_json}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path
