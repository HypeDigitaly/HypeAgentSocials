"""The per-run process summary (RUN_TRACE_SPEC.md §6, W8-8).

*Written after the operator had to hand-reconstruct exactly this document
for run ``2026-08-07_7ded`` (`docs/reports/RUN_2026-08-07_7ded_ANALYZA.md`)
from ``trace.jsonl``, ``logs/artifacts/raw/``, ``copy_requests/``,
``copy_responses/`` and ``pack/media/*.provenance.yaml`` by hand. This
module automates that reconstruction.*

``generate_process_summary`` writes ``logs/runs/<run_id>/process_summary.md``
-- a neat, scannable, human-readable companion to ``trace.md`` (the complete
machine trace) and ``pack/digest.md`` (the 2-minute result summary). It
never replaces either; it answers a narrower question both of those leave
to manual reconstruction: *exactly* what went to and came back from every
external platform, and the *exact* prompts/copy text used.

Design point that matters for testability and for regenerating summaries of
runs made before this module existed: every section is built from the SAME
persisted facts a run already writes (``trace.jsonl``, ``resume_state.yaml``,
the spend ledger, provenance YAMLs, ``copy_requests``/``copy_responses``),
never from live in-memory pipeline state. That is what makes
``python -m hypeagent --summarize <run_id>`` (main.py) able to regenerate
this file for ANY existing run, including ones from before this feature
shipped -- a fact a section needs but an older engine version never
persisted degrades that one line to an explicit
"not recorded by this engine version" rather than crashing the whole
render (see :func:`_safe_section`).

Redaction boundary (RUN_TRACE_SPEC.md §3, restated in §6): this summary
inherits the trace's redaction rules for everything that touches a third
party -- no secrets, no verbatim third-party text, no raw author handles.
The one deliberate exception is **our own** authored content: image
prompts (§7) and copy headlines/captions (§6) are ours to show and are
printed in full, because they are not the third-party text the redaction
rule exists to protect.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from hypeagent import analysis as analysis_module
from hypeagent import media_gen, promptcraft, render_trace
from hypeagent import resume_state as resume_state_module
from hypeagent.collectors import virlo as virlo_collector
from hypeagent.store import Store

PROCESS_SUMMARY_FILENAME = "process_summary.md"
DEFAULT_THEME_NAME = "hypedigitaly"

_SOURCE_DECISION_RE = re.compile(r"source[=\s]'?([A-Za-z0-9_]+)'?")
_MONITOR_ID_ENDPOINT_RE = re.compile(r"/v1/agents/([0-9a-fA-F-]+)")
_MONITOR_ID_DECISION_RE = re.compile(r"agent:([0-9a-fA-F-]+)")


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------


def generate_process_summary(
    run_id: str,
    *,
    config_dir: Path,
    logs_dir: Path,
    secrets_dir: Path | None = None,
    exit_class: str | None = None,
) -> Path:
    """Write (or overwrite) ``logs/runs/<run_id>/process_summary.md``.

    ``exit_class`` lets a live caller (``stages.run_pipeline`` /
    ``resume_pipeline``) pass the exit class it just computed, before
    ``main.py`` has appended the trace's own ``run_end`` event -- without
    it, the header falls back to reading the last ``run_end`` event already
    on file (the shape ``--summarize`` uses when regenerating after the
    fact for a fully completed run).
    """
    config_dir = Path(config_dir)
    logs_dir = Path(logs_dir)
    run_dir = logs_dir / "runs" / run_id
    trace_path = run_dir / "trace.jsonl"
    events, _malformed = render_trace.load_events(trace_path)

    resolved_secrets_dir = Path(secrets_dir) if secrets_dir is not None else (config_dir.parent / "secrets")
    store: Store | None = None
    try:
        store = Store.open(logs_dir, resolved_secrets_dir)
    except Exception:
        store = None

    try:
        lines = _render(
            run_id=run_id,
            run_dir=run_dir,
            config_dir=config_dir,
            events=events,
            store=store,
            exit_class=exit_class,
        )
    finally:
        if store is not None:
            store.close()

    out_path = run_dir / PROCESS_SUMMARY_FILENAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Rendering scaffolding.
# ---------------------------------------------------------------------------


def _safe_section(title: str, fn: Callable[..., list[str]], *args: Any, **kwargs: Any) -> list[str]:
    """Run one section builder; a single section's failure degrades to a
    one-line note instead of blanking (or crashing) the whole file -- the
    property the "regenerate an old/synthetic run missing new fields"
    acceptance case depends on."""
    try:
        body = fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - deliberately broad: best-effort per section
        body = [f"_section unavailable ({type(exc).__name__}: {exc})_"]
    if not body:
        return []
    return [f"## {title}", ""] + body + [""]


def _render(
    *,
    run_id: str,
    run_dir: Path,
    config_dir: Path,
    events: list[dict[str, Any]],
    store: Store | None,
    exit_class: str | None,
) -> list[str]:
    lines: list[str] = []
    lines.extend(_safe_section_header(run_id=run_id, run_dir=run_dir, events=events, exit_class=exit_class))
    lines.extend(_safe_section("Per-platform I/O", _section_platform_io, events))
    lines.extend(
        _safe_section(
            "Per-source extraction",
            _section_source_extraction,
            run_id=run_id,
            run_dir=run_dir,
            events=events,
            store=store,
        )
    )
    lines.extend(_safe_section("Ranking outcome", _section_ranking, run_dir=run_dir))
    lines.extend(_safe_section("Spin rationale", _section_spin, run_dir=run_dir))
    lines.extend(_safe_section("Viral playbook (N-A)", _section_viral_playbook, run_dir=run_dir))
    lines.extend(_safe_section("Copy I/O", _section_copy_io, run_dir=run_dir, events=events))
    lines.extend(_safe_section("Media prompts (N-D)", _section_media_prompts, run_dir=run_dir))
    lines.extend(_safe_section("Image generation", _section_media, run_dir=run_dir, config_dir=config_dir, events=events))
    lines.extend(_safe_section("Spend summary", _section_spend, events=events))
    lines.extend(_section_hygiene())
    return lines


def _safe_section_header(
    *, run_id: str, run_dir: Path, events: list[dict[str, Any]], exit_class: str | None
) -> list[str]:
    try:
        return _section_header(run_id=run_id, run_dir=run_dir, events=events, exit_class=exit_class)
    except Exception as exc:  # noqa: BLE001
        return [
            f"# Process Summary — {run_id}",
            "",
            f"_header unavailable ({type(exc).__name__}: {exc})_",
            "",
        ]


# ---------------------------------------------------------------------------
# Small shared helpers.
# ---------------------------------------------------------------------------


def _md(value: Any) -> str:
    """Escape a value for embedding inside a markdown table cell."""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _rel(path: Path | None, run_dir: Path) -> str:
    if path is None:
        return "—"
    try:
        return str(Path(path).relative_to(run_dir)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _format_cost(cost: Any) -> str:
    if not cost:
        return "—"
    if isinstance(cost, dict):
        parts = [f"{k}: {v}" for k, v in cost.items() if v is not None]
        return ", ".join(parts) if parts else "—"
    return str(cost)


def _load_resume_state_safe(run_dir: Path) -> resume_state_module.ResumeState | None:
    try:
        return resume_state_module.load_resume_state(run_dir)
    except Exception:
        return None


def _theme_name_from_events(events: list[dict[str, Any]]) -> str:
    run_start = next((e for e in events if e.get("event") == "run_start"), None)
    theme = (run_start or {}).get("detail", {}).get("theme")
    return str(theme) if theme else DEFAULT_THEME_NAME


def _virlo_monitor_id(events: list[dict[str, Any]]) -> str:
    for ev in events:
        if ev.get("stage") != "collection":
            continue
        if ev.get("event") == "api_call":
            match = _MONITOR_ID_ENDPOINT_RE.search(ev.get("detail", {}).get("endpoint", ""))
            if match:
                return match.group(1)
        if ev.get("event") == "decision":
            match = _MONITOR_ID_DECISION_RE.search(ev.get("detail", {}).get("decision", ""))
            if match:
                return match.group(1)
    return virlo_collector.DEFAULT_MONITOR_ID


def _parse_copy_filename(name: str) -> tuple[str, int]:
    """``<asset_id>.yaml`` -> (asset_id, 1); ``<asset_id>.attemptN.yaml`` ->
    (asset_id, N). String-based (not regex) because asset ids
    (``{cluster_key}_{destination}``) never contain a literal dot, so this
    is unambiguous."""
    stem = name[:-5] if name.endswith(".yaml") else name
    if ".attempt" in stem:
        base, _, attempt_str = stem.rpartition(".attempt")
        try:
            return base, int(attempt_str)
        except ValueError:
            return stem, 1
    return stem, 1


def _wall_clock_ms(events: list[dict[str, Any]]) -> int | None:
    run_start = next((e for e in events if e.get("event") == "run_start"), None)
    if run_start is None or not events:
        return None
    try:
        start = datetime.fromisoformat(run_start["ts"])
        end = datetime.fromisoformat(events[-1]["ts"])
    except (KeyError, ValueError):
        return None
    return int((end - start).total_seconds() * 1000)


def _format_ms(ms: int) -> str:
    seconds = ms / 1000.0
    if seconds < 60:
        return f"{seconds:.1f}s ({ms} ms)"
    minutes, sec = divmod(seconds, 60)
    return f"{int(minutes)}m {sec:.0f}s ({ms} ms)"


# ---------------------------------------------------------------------------
# 1. Header.
# ---------------------------------------------------------------------------


def _section_header(*, run_id: str, run_dir: Path, events: list[dict[str, Any]], exit_class: str | None) -> list[str]:
    run_start = next((e for e in events if e.get("event") == "run_start"), None)
    run_ends = [e for e in events if e.get("event") == "run_end"]
    theme = (run_start or {}).get("detail", {}).get("theme") or "unknown"
    mode = (run_start or {}).get("detail", {}).get("mode") or "unknown"
    resumed = any(
        e.get("event") == "decision" and e.get("detail", {}).get("resume") is True for e in events
    )

    resolved_exit_class = exit_class
    if resolved_exit_class is None:
        resolved_exit_class = (
            run_ends[-1]["detail"].get("exit_class") if run_ends else "unknown — run still in progress or crashed before run_end"
        )

    wall_clock_ms = _wall_clock_ms(events)

    lines = [
        f"# Process Summary — {run_id}",
        "",
        f"- **run id**: {run_id}",
        f"- **theme**: {theme}",
        f"- **mode**: {mode}{' (resumed at least once)' if resumed else ''}",
        f"- **exit class**: {resolved_exit_class}",
        f"- **wall clock**: {_format_ms(wall_clock_ms) if wall_clock_ms is not None else 'not available'}",
        "- **full trace**: [../trace.md](../trace.md) (`trace.jsonl` for the raw machine-readable events)",
    ]
    digest_path = run_dir / "pack" / "digest.md"
    if digest_path.exists():
        lines.append("- **run digest**: [pack/digest.md](pack/digest.md)")
    lines.append("")
    lines.append(
        "_This is the human-readable \"what exactly went to and came back from every "
        "platform, and the exact prompts used\" companion to `trace.md` / `pack/digest.md` "
        "(RUN_TRACE_SPEC.md §6) — it complements, never replaces, either. See the "
        "data-hygiene footnote at the end for what it deliberately leaves out and why._"
    )
    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# 2. Per-platform I/O.
# ---------------------------------------------------------------------------


def _section_platform_io(events: list[dict[str, Any]]) -> list[str]:
    calls_by_seq = {e["seq"]: e for e in events if e.get("event") == "api_call" and "seq" in e}
    rows_by_platform: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        if ev.get("event") != "api_response":
            continue
        detail = ev.get("detail", {})
        call = calls_by_seq.get(detail.get("seq_of_call"))
        call_detail = call.get("detail", {}) if call else {}
        platform = call_detail.get("platform", "?")
        rows_by_platform.setdefault(platform, []).append(
            {
                "endpoint": call_detail.get("endpoint", "?"),
                "purpose": call_detail.get("purpose", "?"),
                "status": detail.get("status"),
                "latency_ms": detail.get("latency_ms"),
                "bytes": detail.get("bytes"),
                "cost": detail.get("cost"),
            }
        )

    if not rows_by_platform:
        return ["_No external API calls recorded in this invocation's trace._"]

    lines: list[str] = []
    for platform in sorted(rows_by_platform):
        rows = rows_by_platform[platform]
        lines.append(f"### {platform} ({len(rows)} call(s))")
        lines.append("")
        lines.append("| endpoint | purpose | status | latency (ms) | bytes | cost |")
        lines.append("|---|---|---|---|---|---|")
        total_latency = 0
        total_bytes = 0
        cost_totals: dict[str, float] = {}
        for row in rows:
            lines.append(
                f"| {_md(row['endpoint'])} | {_md(row['purpose'])} | {row['status']} | "
                f"{row['latency_ms']} | {row['bytes']} | {_format_cost(row['cost'])} |"
            )
            if isinstance(row["latency_ms"], (int, float)):
                total_latency += row["latency_ms"]
            if isinstance(row["bytes"], (int, float)):
                total_bytes += row["bytes"]
            if isinstance(row["cost"], dict):
                for key, value in row["cost"].items():
                    if isinstance(value, (int, float)):
                        cost_totals[key] = cost_totals.get(key, 0.0) + value
        cost_summary = ", ".join(f"{k}={v:g}" for k, v in cost_totals.items()) or "—"
        lines.append("")
        lines.append(
            f"_subtotal — {len(rows)} call(s), {total_latency} ms cumulative latency, "
            f"{total_bytes} bytes, cost: {cost_summary}_"
        )
        lines.append("")
    return lines


# ---------------------------------------------------------------------------
# 3. Per-source extraction.
# ---------------------------------------------------------------------------


def _section_source_extraction(
    *, run_id: str, run_dir: Path, events: list[dict[str, Any]], store: Store | None
) -> list[str]:
    collection_end = next(
        (e for e in events if e.get("event") == "stage_end" and e.get("stage") == "collection"), None
    )
    calls_made_by_source: dict[str, int] = {}
    items_fetched_by_source: dict[str, int] = {}
    if collection_end is not None:
        detail = collection_end.get("detail", {})
        calls_made_by_source = dict(detail.get("calls_made_by_source") or {})
        items_fetched_by_source = dict(detail.get("items_fetched_by_source") or {})

    sources: set[str] = set(calls_made_by_source) | set(items_fetched_by_source)
    for ev in events:
        if ev.get("stage") != "collection":
            continue
        if ev.get("event") == "api_call":
            platform = ev.get("detail", {}).get("platform")
            if platform:
                sources.add(platform)
        if ev.get("event") == "decision":
            match = _SOURCE_DECISION_RE.search(ev.get("detail", {}).get("decision", ""))
            if match:
                sources.add(match.group(1))

    stored_counts: dict[str, int] = {}
    if store is not None:
        for sig in store.signals_for_run(run_id):
            stored_counts[sig.source] = stored_counts.get(sig.source, 0) + 1
            sources.add(sig.source)

    reached_ranking: dict[str, int] = {}
    resume = _load_resume_state_safe(run_dir)
    if resume is not None:
        for sc in resume.ranking_result.all_scorecards:
            for src in sc.sources:
                reached_ranking[src] = reached_ranking.get(src, 0) + 1
                sources.add(src)

    if not sources:
        return ["_No sources were touched by collection this run (or the run never reached the collection stage)._"]

    lines = [
        "| source | items fetched (raw) | items stored this run | candidates reaching ranking | API calls made |",
        "|---|---|---|---|---|",
    ]
    for source in sorted(sources):
        fetched = items_fetched_by_source.get(source)
        fetched_str = str(fetched) if fetched is not None else "not recorded by this engine version"
        calls = calls_made_by_source.get(source)
        calls_str = str(calls) if calls is not None else "not recorded by this engine version"
        lines.append(
            f"| {source} | {fetched_str} | {stored_counts.get(source, 0)} | "
            f"{reached_ranking.get(source, 0)} | {calls_str} |"
        )
    lines.append("")
    lines.append(
        "_\"items stored this run\" and \"candidates reaching ranking\" are derived from the "
        "store and `resume_state.yaml`, and are available for any run that reached those "
        "stages; \"items fetched\" and \"API calls made\" per source require an engine "
        "version that persists the collection stage's per-source breakdown (W8-8 onward)._"
    )

    if "virlo" in sources:
        lines.append("")
        lines.append("#### Virlo — theme extraction detail")
        lines.append("")
        theme_name = _theme_name_from_events(events)
        run_date = run_id.split("_")[0]
        monitor_id = _virlo_monitor_id(events)
        lines.extend(
            _virlo_detail(run_dir=run_dir, store=store, theme_name=theme_name, run_date=run_date, monitor_id=monitor_id)
        )
    return lines


def _virlo_detail(*, run_dir: Path, store: Store | None, theme_name: str, run_date: str, monitor_id: str) -> list[str]:
    note_dict = virlo_collector.load_extraction_note(run_dir)
    source_label = "this run's own extraction note (`virlo_extraction.yaml`)"
    if note_dict is None:
        note_dict, source_label = _virlo_note_from_raw_payload(
            store=store, theme_name=theme_name, run_date=run_date, monitor_id=monitor_id
        )
    if note_dict is None:
        return [
            "_No Virlo extraction detail available: no `virlo_extraction.yaml` on file for this "
            "run, and no raw agent-monitor payload could be located — either it was never "
            "captured, or it has already expired under the 30-day raw-payload retention window "
            "(ARCHITECTURE_PLAN.md §2.6)._",
        ]
    lines = [f"_source: {source_label}_", ""]
    themes = note_dict.get("themes") or []
    if themes:
        lines.append("| theme | confidence | video_count | stable_key |")
        lines.append("|---|---|---|---|")
        for theme in themes:
            lines.append(
                f"| {_md(theme.get('name'))} | {theme.get('confidence')} | {theme.get('video_count')} | "
                f"{_md(theme.get('stable_key'))} |"
            )
    else:
        lines.append("_monitor payload present but carried no themes._")
    lines.append("")
    unused = note_dict.get("unused_fields_present_in_raw_payload") or []
    if unused:
        lines.append(
            f"**Rich fields present in the raw payload but not used by this pipeline:** "
            f"{', '.join(unused)} (names only — their text is not copied here; wiring them "
            "into copy is a separate, later milestone)."
        )
    else:
        lines.append("_No additional rich fields detected on the payload beyond what was used._")
    return lines


def _virlo_note_from_raw_payload(
    *, store: Store | None, theme_name: str, run_date: str, monitor_id: str
) -> tuple[dict[str, Any] | None, str]:
    if store is None:
        return None, ""
    found = store.find_raw_payload(
        theme=theme_name, source="virlo", query_sig_prefix="agent:", on_or_before_run_date=run_date
    )
    if found is None:
        return None, ""
    origin_run_id, raw_path_str = found
    raw_path = Path(raw_path_str)
    if not raw_path.exists():
        return None, ""
    try:
        payload = json.loads(raw_path.read_bytes())
    except (json.JSONDecodeError, OSError):
        return None, ""
    note = virlo_collector.build_extraction_note(payload, monitor_id=monitor_id)
    if note is None:
        return None, ""
    label = (
        f"reconstructed from the raw payload captured by run `{origin_run_id}` (still on disk "
        "under the 30-day retention window; this run's own collection stage hit the same-day "
        "within-run-idempotency cache and made no fresh fetch — ARCHITECTURE_PLAN.md §8.5)"
    )
    return note.to_yaml_dict(), label


# ---------------------------------------------------------------------------
# 4. Ranking outcome.
# ---------------------------------------------------------------------------


def _section_ranking(*, run_dir: Path) -> list[str]:
    resume = _load_resume_state_safe(run_dir)
    if resume is None:
        return ["_Ranking outcome not available — this run never reached the spin stage (no `resume_state.yaml` on file)._"]
    ranking_result = resume.ranking_result
    all_scorecards = ranking_result.all_scorecards
    candidates_in = len(all_scorecards)
    passed = [sc for sc in all_scorecards if sc.gate_status.startswith("pass")]
    failed_count = candidates_in - len(passed)
    top_n = sum(len(v) for v in ranking_result.top_by_language.values())

    lines = [
        f"candidates in: **{candidates_in}** -> passed fit gate: **{len(passed)}** -> top-N (generated): **{top_n}**",
        "",
    ]
    if passed:
        lines.append(
            "One line per candidate that passed the fit gate (the ones that did not are summarised below, "
            "not itemized, to keep this scannable — see `pack/scorecards/*.yaml` for every candidate):"
        )
        lines.append("")
        lines.append("| topic | language | composite | fit | method | outcome |")
        lines.append("|---|---|---|---|---|---|")
        for sc in passed:
            fit = (sc.sub_scores.get("fit") or {}).get("numeric")
            lines.append(
                f"| {_md(sc.representative_title)} | {sc.language} | {sc.composite} | {fit} | "
                f"{_md(sc.fit_method)} | {_md(sc.per_language_outcome)} ({_md(sc.gate_status)}) |"
            )
    else:
        lines.append("_No candidate passed the fit gate this run._")
    if failed_count:
        # Every gate-failing candidate uses the same deterministic method
        # label -- naming it once here, rather than 600+ times, is what
        # keeps this scannable.
        method_label = passed[0].fit_method if passed else all_scorecards[0].fit_method if all_scorecards else ""
        lines.append("")
        lines.append(
            f"_{failed_count} further candidate(s) did not pass the fit gate this run (method: "
            f"{_md(method_label)}) — not itemized here; see `pack/scorecards/*.yaml` for the full list._"
        )
    if ranking_result.zero_passing_candidates:
        lines.append("")
        lines.append("_0 passing candidates this run — a successful outcome, thresholds were not relaxed._")
    return lines


# ---------------------------------------------------------------------------
# 5. Spin rationale.
# ---------------------------------------------------------------------------


def _section_spin(*, run_dir: Path) -> list[str]:
    resume = _load_resume_state_safe(run_dir)
    if resume is None or not resume.spin_results:
        return []
    return [f"- {sr.rationale_line}" for sr in resume.spin_results.values()]


# ---------------------------------------------------------------------------
# 5b. Viral playbook (N-A) — W8-9 Q4.
# ---------------------------------------------------------------------------


def _section_viral_playbook(*, run_dir: Path) -> list[str]:
    """``analysis/viral_playbook.yaml``, when this run produced one --
    degrades to an explicit one-liner for every other case (N-A skipped,
    degraded, or the file simply predates this engine version) rather than
    guessing at a shape it cannot find."""
    playbook_path = run_dir / analysis_module.VIRAL_PLAYBOOK_DIRNAME / analysis_module.VIRAL_PLAYBOOK_FILENAME
    if not playbook_path.exists():
        return ["_No `analysis/viral_playbook.yaml` on file for this run (N-A did not run, or this engine version predates it)._"]
    playbook = analysis_module.load_viral_playbook_file(playbook_path)
    if playbook is None:
        return ["_`analysis/viral_playbook.yaml` is present but unreadable/malformed._"]
    if playbook.skipped:
        return [f"_N-A skipped this run: {playbook.skip_reason or 'no reason recorded'}._"]

    lines: list[str] = []
    if playbook.degraded:
        lines.append(f"_degraded: {playbook.degrade_reason or 'unknown reason'}_")
        lines.append("")
    if not playbook.themes and not playbook.viral_tactics_digest and not playbook.connecting_thread:
        lines.append("_Playbook produced no themes or global digest this run._")
        return lines

    for theme in playbook.themes:
        lines.append(f"### {theme.theme}")
        lines.append("")
        if theme.winning_hooks:
            lines.append(f"- winning hooks: {', '.join(theme.winning_hooks)}")
        if theme.formats:
            lines.append(f"- formats: {', '.join(theme.formats)}")
        if theme.visual_archetypes_seen:
            lines.append(f"- visual archetypes seen: {', '.join(theme.visual_archetypes_seen)}")
        if theme.tools_shown:
            lines.append(f"- tools shown: {', '.join(theme.tools_shown)}")
        if theme.numbers_used:
            lines.append(f"- numbers used: {', '.join(theme.numbers_used)}")
        if theme.platform_norms:
            norms = "; ".join(f"{k}: {v}" for k, v in theme.platform_norms.items())
            lines.append(f"- platform norms: {norms}")
        lines.append("")

    if playbook.viral_tactics_digest:
        lines.append("**Global viral tactics digest:**")
        lines.append("")
        lines.extend(f"- {tactic}" for tactic in playbook.viral_tactics_digest)
        lines.append("")
    if playbook.connecting_thread:
        lines.append(f"**Connecting thread:** {playbook.connecting_thread}")
        lines.append("")
    if playbook.do_not_do:
        lines.append("**Do-not-do:**")
        lines.extend(f"- {item}" for item in playbook.do_not_do)
        lines.append("")
    return lines


# ---------------------------------------------------------------------------
# 6. Copy I/O.
# ---------------------------------------------------------------------------


def _section_copy_io(*, run_dir: Path, events: list[dict[str, Any]]) -> list[str]:
    requests_dir = run_dir / "copy_requests"
    responses_dir = run_dir / "copy_responses"
    if not requests_dir.exists() or not any(requests_dir.glob("*.yaml")):
        return ["_No copy requests were written this run (no EN candidates reached spin/copy, or copy was refused)._"]

    assets: dict[str, dict[int, dict[str, Path]]] = {}
    for req_path in sorted(requests_dir.glob("*.yaml")):
        base, attempt = _parse_copy_filename(req_path.name)
        assets.setdefault(base, {}).setdefault(attempt, {})["request_path"] = req_path
    if responses_dir.exists():
        for resp_path in sorted(responses_dir.glob("*.yaml")):
            base, attempt = _parse_copy_filename(resp_path.name)
            assets.setdefault(base, {}).setdefault(attempt, {})["response_path"] = resp_path

    gate_by_asset: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        if ev.get("event") != "gate_verdict":
            continue
        detail = ev.get("detail", {})
        gate_by_asset.setdefault(detail.get("asset_id", ""), []).append(detail)

    lines = [
        "| asset | destination | status | attempt | request | response | failing spans |",
        "|---|---|---|---|---|---|---|",
    ]
    full_text_blocks: list[str] = []
    for base in sorted(assets):
        attempts = assets[base]
        max_attempt = max(attempts)
        latest = attempts[max_attempt]
        request_path = latest.get("request_path") or attempts[min(attempts)].get("request_path")
        response_path = latest.get("response_path")
        destination = _destination_from_request(request_path)

        verdicts = sorted(gate_by_asset.get(base, []), key=lambda d: d.get("regeneration_counter") or 0)
        if verdicts:
            final = verdicts[-1]
            status = "gated-pass" if final.get("verdict") == "pass" else f"blocked — {final.get('verdict')}"
            failing = "; ".join(v.get("failing_span") for v in verdicts if v.get("failing_span")) or "—"
        elif response_path is None:
            status = "held — awaiting operator copy"
            failing = "—"
        else:
            status = "response present, gate verdict not recorded (older engine version)"
            failing = "—"

        lines.append(
            f"| {_md(base)} | {_md(destination)} | {_md(status)} | {max_attempt} | "
            f"{_rel(request_path, run_dir)} | {_rel(response_path, run_dir)} | {_md(failing)} |"
        )

        if response_path is not None:
            try:
                data = yaml.safe_load(response_path.read_text(encoding="utf-8")) or {}
            except OSError:
                data = {}
            headline = data.get("headline")
            caption = data.get("caption")
            if headline or caption:
                full_text_blocks.append(f"**{base}** (final, attempt {max_attempt}):")
                full_text_blocks.append("")
                full_text_blocks.append(f"> Headline: {headline}")
                full_text_blocks.append(">")
                for cap_line in (caption or "").splitlines() or [""]:
                    full_text_blocks.append(f"> {cap_line}")
                full_text_blocks.append("")

    lines.append("")
    if full_text_blocks:
        lines.append("**Final headline + caption text (own-authored content — shown in full):**")
        lines.append("")
        lines.extend(full_text_blocks)
    return lines


def _destination_from_request(request_path: Path | None) -> str:
    if request_path is not None and request_path.exists():
        try:
            data = yaml.safe_load(request_path.read_text(encoding="utf-8")) or {}
            dest = data.get("destination")
            if dest:
                return str(dest)
        except OSError:
            pass
    return "?"


# ---------------------------------------------------------------------------
# 6b. Media prompts (N-D) — W8-9 Q4.
# ---------------------------------------------------------------------------


def _section_media_prompts(*, run_dir: Path) -> list[str]:
    """The full, exact prompt(s) N-D crafted for every gated-pass asset,
    read back from ``media_prompts.yaml`` -- own-authored content (module
    docstring's redaction-boundary exception), shown in full per slot
    (``hero`` or every ``slide_NN``), whether or not it was ever actually
    submitted this run (a carousel's slide prompts are persisted even before
    W8-9 Q4 wired their submission)."""
    path = run_dir / promptcraft.MEDIA_PROMPTS_FILENAME
    if not path.exists():
        return ["_No `media_prompts.yaml` on file for this run (N-D did not run, or this engine version predates it)._"]
    prompt_sets = promptcraft.load_media_prompts(run_dir)
    if not prompt_sets:
        return ["_`media_prompts.yaml` is present but empty or unreadable._"]

    lines: list[str] = []
    for asset_id in sorted(prompt_sets):
        prompt_set = prompt_sets[asset_id]
        lines.append(f"### {asset_id}")
        lines.append("")
        if prompt_set.unavailable:
            lines.append(f"_unavailable: {prompt_set.unavailable_reason or 'no reason recorded'}_")
            lines.append("")
            continue
        if prompt_set.gate_blocked:
            lines.append("_gate-blocked — these crafted prompts failed the deterministic claim gate:_")
            lines.extend(f"- {span}" for span in prompt_set.gate_failing_spans)
            lines.append("")
        if prompt_set.archetype or prompt_set.register:
            lines.append(f"- archetype: {prompt_set.archetype or '—'}; register: {prompt_set.register or '—'}")
            lines.append("")
        for image in prompt_set.images:
            lines.append(f"**{image.slot}:**")
            lines.append("")
            lines.append("> " + image.prompt.replace("\n", "\n> "))
            lines.append("")
    return lines


# ---------------------------------------------------------------------------
# 7. Image generation.
# ---------------------------------------------------------------------------


def _section_media(*, run_dir: Path, config_dir: Path, events: list[dict[str, Any]]) -> list[str]:
    media_dir = run_dir / "pack" / "media"
    # W8-9 Q4 pack layout nests one provenance file per slot inside its own
    # ``<cluster_key>_<destination>/`` folder (``hero.provenance.yaml``,
    # ``slide_01.provenance.yaml``, ...); a run from before that milestone
    # wrote it flat, directly under ``pack/media/``. ``rglob`` finds both
    # without the summarizer needing to know which shape any given run used.
    provenance_paths = sorted(media_dir.rglob("*.provenance.yaml")) if media_dir.exists() else []
    if not provenance_paths:
        return ["_No media assets were generated (or provenance-recorded) this run._"]

    registry = _load_registry_safe(config_dir)
    create_task_calls = [
        ev
        for ev in events
        if ev.get("event") == "api_call"
        and ev.get("detail", {}).get("platform") == "kie"
        and "createTask" in ev.get("detail", {}).get("endpoint", "")
    ]

    docs: list[dict[str, Any]] = []
    for path in provenance_paths:
        try:
            docs.append(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
        except OSError:
            continue

    lines: list[str] = []
    # W8-9 Q4: one row per slot (hero or slide_NN), including carousels --
    # the summary table this milestone adds so a multi-image asset's QA
    # verdicts and per-slot cost are scannable without opening every
    # provenance YAML individually.
    lines.append("| asset | slot | route | cost | QA verdict | checksum |")
    lines.append("|---|---|---|---|---|---|")
    for doc in docs:
        qa = doc.get("qa") or {}
        qa_display = qa.get("status", "—")
        if qa_display == "skipped" and qa.get("skip_reason"):
            qa_display = f"skipped ({qa['skip_reason']})"
        lines.append(
            f"| {_md(doc.get('asset_id', '?'))} | {_md(doc.get('slot', 'hero'))} | "
            f"`{doc.get('requested_route')}` | ${doc.get('observed_cost_usd')} | {_md(qa_display)} | "
            f"{doc.get('checksum_sha256')} |"
        )
    lines.append("")

    for path, doc in zip(provenance_paths, docs):
        asset_id = doc.get("asset_id", path.stem)
        slot = doc.get("slot", "hero")
        lines.append(f"### {asset_id} ({slot})")
        lines.append("")
        lines.append(f"- route: `{doc.get('requested_route')}` (model `{doc.get('requested_model')}`)")
        lines.append(f"- delivered route state: {doc.get('delivered_route_state')} (delivered model: {doc.get('delivered_model')})")
        lines.append(f"- cost: ${doc.get('observed_cost_usd')}")
        lines.append(f"- task id: {doc.get('task_id')}")
        lines.append(f"- provenance state: {doc.get('status', doc.get('delivered_route_state'))}")
        lines.append(f"- checksum (sha256): {doc.get('checksum_sha256')}")
        qa = doc.get("qa") or {}
        if qa:
            lines.append(
                f"- N-E vision-QA: **{qa.get('status', '—')}** "
                f"(text_matches={qa.get('text_matches')}, archetype_ok={qa.get('archetype_ok')}, "
                f"subject_relevant={qa.get('subject_relevant')}, logos_ok={qa.get('logos_ok')}, "
                f"composition_ok={qa.get('composition_ok')}, series_consistent={qa.get('series_consistent')}"
                + (f", skip_reason={qa.get('skip_reason')}" if qa.get("skip_reason") else "")
                + ")"
            )
            if qa.get("mismatches"):
                lines.append(f"  - mismatches: {'; '.join(qa['mismatches'])}")
        image_path = doc.get("image_path")
        lines.append(f"- image path: {_rel(Path(image_path), run_dir) if image_path else '—'}")
        lines.append("")

        prompt_full = doc.get("prompt_full")
        prompt_note: str | None = None
        if not prompt_full:
            prompt_full, prompt_note = _reconstruct_prompt(
                doc=doc, run_dir=run_dir, registry=registry, create_task_calls=create_task_calls
            )

        lines.append("**Full prompt sent:**")
        lines.append("")
        if prompt_full:
            lines.append("> " + str(prompt_full).replace("\n", "\n> "))
            if prompt_note:
                lines.append("")
                lines.append(f"_{prompt_note}_")
        else:
            sha = doc.get("prompt_sha256")
            lines.append(
                "_full prompt text not persisted by this engine version"
                + (f" (sha256 `{sha}`)" if sha else "")
                + " — see RUN_TRACE_SPEC.md §2 for the hash-only trace record._"
            )
        lines.append("")
    return lines


def _load_registry_safe(config_dir: Path) -> media_gen.ModelRegistry | None:
    try:
        return media_gen.load_model_registry(Path(config_dir) / "model_registry.yaml")
    except Exception:
        return None


def _find_image_brief(run_dir: Path, cluster_key: str, destination: str) -> str | None:
    responses_dir = run_dir / "copy_responses"
    if not responses_dir.exists():
        return None
    base_prefix = f"{cluster_key}_{destination}"
    candidates = [p for p in responses_dir.glob(f"{base_prefix}*.yaml") if _parse_copy_filename(p.name)[0] == base_prefix]
    if not candidates:
        return None
    candidates.sort(key=lambda p: _parse_copy_filename(p.name)[1])
    best = candidates[-1]
    try:
        data = yaml.safe_load(best.read_text(encoding="utf-8")) or {}
    except OSError:
        return None
    brief = data.get("image_brief")
    return str(brief) if brief else None


def _reconstruct_prompt(
    *,
    doc: dict[str, Any],
    run_dir: Path,
    registry: media_gen.ModelRegistry | None,
    create_task_calls: list[dict[str, Any]],
) -> tuple[str | None, str | None]:
    """Old-run fallback (no ``prompt_full`` in the provenance YAML): the
    exact prompt is deterministically recoverable as
    ``compose_prompt(image_brief, registry)`` from the copy response's own
    ``image_brief`` plus the (still-current) model registry — verified
    against the trace's recorded ``prompt_sha256`` where available, so a
    silent registry/brief drift since generation is reported rather than
    passed off as ground truth."""
    if registry is None:
        return None, None
    cluster_key = doc.get("cluster_key")
    destination = doc.get("destination")
    if not cluster_key or not destination:
        return None, None
    image_brief = _find_image_brief(run_dir, str(cluster_key), str(destination))
    if image_brief is None:
        return None, None

    composed = media_gen.compose_prompt(image_brief, registry)
    computed_sha = media_gen.prompt_sha256(composed)

    trace_sha = None
    purpose_suffix = f"for {cluster_key}/{destination}"
    for call in create_task_calls:
        if purpose_suffix in call.get("detail", {}).get("purpose", ""):
            trace_sha = call.get("detail", {}).get("request", {}).get("prompt_sha256")
            break

    if trace_sha and trace_sha == computed_sha:
        note = (
            "reconstructed from the copy response's image_brief + the current model registry's "
            "constraints (verified against the trace's recorded sha256 — this engine version "
            "did not yet persist the prompt text itself)"
        )
    elif trace_sha:
        note = (
            "reconstructed from the copy response's image_brief + the current model registry's "
            "constraints — WARNING: sha256 does not match the trace's recorded hash; the "
            "registry's constraints or the image_brief may have changed since this asset was "
            "generated, so this text may not be byte-identical to what was actually sent"
        )
    else:
        note = (
            "reconstructed from the copy response's image_brief + the current model registry's "
            "constraints (no trace sha256 on file to verify against)"
        )
    return composed, note


# ---------------------------------------------------------------------------
# 8. Spend summary.
# ---------------------------------------------------------------------------


def _section_spend(*, events: list[dict[str, Any]]) -> list[str]:
    spend_events = [ev.get("detail", {}) for ev in events if ev.get("event") == "spend"]
    if not spend_events:
        return [
            "_No spend-bearing stage recorded a `spend` event this invocation (no media was "
            "submitted, or nothing new to submit)._",
            "",
            "_text wallet: $0.00 — no spend-bearing text-generation stage exists in this engine "
            "version (interactive-file copy provider)._",
        ]

    by_wallet: dict[str, dict[str, Any]] = {}
    for detail in spend_events:
        wallet = detail.get("wallet", "?")
        agg = by_wallet.setdefault(wallet, {"expected": 0.0, "ledger_recorded": 0.0, "balance_delta": 0.0, "balance_delta_n": 0})
        agg["expected"] += detail.get("expected") or 0.0
        agg["ledger_recorded"] += detail.get("ledger_recorded") or 0.0
        if detail.get("balance_delta") is not None:
            agg["balance_delta"] += detail["balance_delta"]
            agg["balance_delta_n"] += 1

    balances = _credit_balances(events)

    lines = [
        "| wallet | expected | ledger recorded | observed balance delta | balance before -> after |",
        "|---|---|---|---|---|",
    ]
    for wallet, agg in by_wallet.items():
        delta_str = f"${agg['balance_delta']:.4f}" if agg["balance_delta_n"] else "not observed"
        divergence = ""
        if agg["balance_delta_n"] and agg["ledger_recorded"]:
            div_pct = abs(agg["balance_delta"] - agg["ledger_recorded"]) / max(agg["ledger_recorded"], 0.01)
            divergence = f" ({div_pct:.0%} divergence from ledger)"
        bal_str = balances.get(wallet, "—")
        lines.append(
            f"| {wallet} | ${agg['expected']:.4f} | ${agg['ledger_recorded']:.4f} | "
            f"{delta_str}{divergence} | {bal_str} |"
        )
    lines.append("")
    lines.append(
        "_text wallet: $0.00 — no spend-bearing text-generation stage exists in this engine "
        "version (interactive-file copy provider)._"
    )
    return lines


def _credit_balances(events: list[dict[str, Any]]) -> dict[str, str]:
    calls_by_seq = {e["seq"]: e for e in events if e.get("event") == "api_call" and "seq" in e}
    before = None
    after = None
    for ev in events:
        if ev.get("event") != "api_response":
            continue
        detail = ev.get("detail", {})
        call = calls_by_seq.get(detail.get("seq_of_call"))
        purpose = (call.get("detail", {}).get("purpose") if call else "") or ""
        balance = (detail.get("response_summary") or {}).get("balance")
        if balance is None:
            continue
        if "pre-submission" in purpose:
            before = balance
        if "post-submission" in purpose:
            after = balance
    if before is None and after is None:
        return {}
    return {"media": f"{before} -> {after}"}


# ---------------------------------------------------------------------------
# 9. Data-hygiene footnote.
# ---------------------------------------------------------------------------


def _section_hygiene() -> list[str]:
    return [
        "## Data-hygiene footnote",
        "",
        "This summary inherits `trace.jsonl`'s redaction rules (RUN_TRACE_SPEC.md §3) for "
        "everything that touches a third party:",
        "",
        "- **Secrets never appear** — no API keys, tokens, or Authorization headers anywhere above.",
        "- **Third-party verbatim text is never embedded** — collected article/post titles and "
        "excerpts are represented by their canonical key and hash only; the text itself lives in "
        "the research artifact store under its own 30-day expiry (ARCHITECTURE_PLAN.md §2.6).",
        "- **Author handles and permalinks are redacted** wherever they would otherwise appear "
        "(the same rule prompt payloads already follow, R4-M7).",
        "- **Own-authored content appears in full** — this pipeline's own image prompts (§7), "
        "copy headlines/captions (§6), and spin rationales (§5) are ours to show, so they are "
        "printed verbatim rather than hashed (RUN_TRACE_SPEC.md §6).",
        "",
    ]
