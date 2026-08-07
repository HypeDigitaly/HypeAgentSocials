"""Run packaging and the run digest (ARCHITECTURE_PLAN.md §12.1, §2.6).

The run pack is a plain-file directory, ``logs/runs/<run_id>/pack/``:

- ``digest.md`` — the single entry point, scannable in ~2 minutes.
- ``scorecards/*.yaml`` — one file per candidate (§2.7's inspectable scorecard).
- ``signals/*.yaml`` — the two-part provenance record per §2.6 for every
  signal behind a candidate that passed the fit gate.

Every canonical key written into ``signals/`` is registered in the
run-pack -> canonical-key index **transactionally with the pack write**
(files first, then the index row — so a crash leaves an unregistered file
rather than a phantom index entry pointing at nothing).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from hypeagent.ranking import RankingResult, Scorecard
from hypeagent.store import Store

TRACE_RELATIVE_LINK = "../trace.md"


def _safe_filename(key: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", key)[:120]


@dataclass
class DegradedSourceNote:
    source: str
    reason: str


@dataclass
class PackagingSummary:
    pack_dir: Path
    digest_path: Path
    scorecard_paths: list[Path]
    signal_paths: list[Path]
    registered_keys: int


def write_scorecards(pack_dir: Path, scorecards: list[Scorecard]) -> list[Path]:
    scorecards_dir = pack_dir / "scorecards"
    scorecards_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for sc in scorecards:
        path = scorecards_dir / f"{_safe_filename(sc.cluster_key)}.yaml"
        path.write_text(yaml.safe_dump(sc.to_yaml_dict(), allow_unicode=True, sort_keys=False), encoding="utf-8")
        paths.append(path)
    return paths


def write_signal_provenance_for_candidates(
    pack_dir: Path, store: Store, candidates_with_scorecards: list[tuple[Scorecard, list[str]]]
) -> tuple[list[Path], list[tuple[str, str]]]:
    """As above, but taking explicit (scorecard, canonical_keys) pairs — the
    caller (``stages.py``) has the ``TopicCandidate`` objects with their
    concrete signal list and passes their canonical keys through."""
    signals_dir = pack_dir / "signals"
    signals_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    registrations: list[tuple[str, str]] = []
    seen: set[str] = set()

    for scorecard, canonical_keys in candidates_with_scorecards:
        if scorecard.composite is None:
            continue
        for canonical_key in canonical_keys:
            if canonical_key in seen:
                continue
            seen.add(canonical_key)
            provenance = store.get_provenance(canonical_key)
            if provenance is None:
                continue
            durable, verbatim = provenance
            doc = {
                "canonical_key": canonical_key,
                "cluster_key": scorecard.cluster_key,
                "durable": durable,
                "verbatim": {"excerpt": verbatim["excerpt"], "canonical_link": verbatim["canonical_link"]},
            }
            path = signals_dir / f"{_safe_filename(canonical_key)}.yaml"
            path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
            paths.append(path)
            registrations.append((canonical_key, str(path)))

    return paths, registrations


def render_digest(
    *,
    run_id: str,
    run_date: str,
    theme_name: str,
    ranking_result: RankingResult,
    degraded_sources: list[DegradedSourceNote],
    languages: list[str],
    zero_candidates_message: bool,
    brand_truth_panel: Any | None = None,
    spin_results: dict[str, Any] | None = None,
    copy_asset_statuses: list[Any] | None = None,
    cs_holds: list[dict[str, str]] | None = None,
    media_asset_statuses: list[Any] | None = None,
    media_registry_price_snapshot_date: str | None = None,
) -> str:
    """Render ``digest.md`` (§12.1, Phase-1-relevant lines only)."""
    lines: list[str] = []
    status = "healthy — ranking produced candidates" if not ranking_result.zero_passing_candidates else "healthy — zero passing candidates this run"
    if degraded_sources:
        status = "degraded sources this run — see banners below"

    lines.append(f"# Run Digest — {run_id}")
    lines.append("")
    lines.append(f"- **run id**: {run_id}")
    lines.append(f"- **run date**: {run_date}")
    lines.append(f"- **theme**: {theme_name}")
    lines.append("- **mode**: interactive")
    lines.append(f"- **status**: {status}")
    lines.append("")

    lines.append("## Cost forecast")
    lines.append("")
    lines.append("| line | amount |")
    lines.append("|---|---|")
    if media_asset_statuses is not None:
        media_spent = sum(
            (s.observed_cost_usd or 0.0) for s in media_asset_statuses if getattr(s, "observed_cost_usd", None)
        )
        media_forecast = sum(
            (s.expected_cost_usd or 0.0) for s in media_asset_statuses
            if getattr(s, "expected_cost_usd", None) and s.status not in ("generated",)
        )
        snapshot_note = f" (price snapshot {media_registry_price_snapshot_date})" if media_registry_price_snapshot_date else ""
        lines.append(f"| media — actual spend | ${media_spent:.4f}{snapshot_note} |")
        lines.append(f"| media — forecast (unresolved/planned) | ${media_forecast:.4f}{snapshot_note} |")
    else:
        lines.append("| media | $0.00 |")
    lines.append("| text-per-artifact | $0.00 |")
    lines.append("| text-per-candidate | $0.00 |")
    lines.append("")
    if media_asset_statuses is None:
        lines.append("_Phase 1: no spend-bearing stages enabled._")
    lines.append("")

    lines.append("## Topic table")
    lines.append("")
    any_row = False
    lines.append("| language | topic | composite | band | fit | families | dedupe status | per-language outcome |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for language in languages:
        for sc in ranking_result.top_by_language.get(language, []):
            any_row = True
            lines.append(
                f"| {sc.language} | {sc.representative_title} | {sc.composite} | {sc.band} | "
                f"{sc.sub_scores.get('fit', {}).get('numeric')} | {', '.join(sc.families)} | "
                f"{sc.dedupe_status} | {sc.per_language_outcome} |"
            )
    if not any_row:
        lines.append("| — | — | — | — | — | — | — | — |")
    lines.append("")

    if ranking_result.zero_passing_candidates:
        lines.append(
            "**0 passing candidates — this is a successful outcome, thresholds were not relaxed.**"
        )
        lines.append("")

    lines.append("## Degraded-source banners")
    lines.append("")
    if degraded_sources:
        for note in degraded_sources:
            lines.append(f"- **{note.source}**: {note.reason}")
    else:
        lines.append("_No degraded sources this run._")
    lines.append("")

    lines.append("## Per-language evidence floor")
    lines.append("")
    any_breach = False
    for language in languages:
        if ranking_result.evidence_floor_breached.get(language):
            any_breach = True
            consecutive = ranking_result.evidence_floor_consecutive.get(language, 1)
            lines.append(
                f"- the **{language}** candidate set has been below its evidence floor for "
                f"{consecutive} consecutive run(s)."
            )
    if not any_breach:
        lines.append("_No language is below its evidence-and-volume floor this run._")
    lines.append("")

    lines.append("## Language comparability note")
    lines.append("")
    lines.append(
        "English composites include virality; Czech composites omit it entirely (no counted-evidence "
        "Czech source exists in the Phase-1 portfolio, §2.7). **The two numbers are not comparable.**"
    )
    lines.append("")

    if brand_truth_panel is not None:
        lines.append("## Brand-truth panel")
        lines.append("")
        lines.append(
            f"- **snapshot**: `{brand_truth_panel.snapshot.snapshot_id}` "
            f"(taken {brand_truth_panel.snapshot.taken_at}, {brand_truth_panel.snapshot_age_days}d old, "
            f"max_age_days={brand_truth_panel.snapshot.max_age_days})"
        )
        lines.append(f"- **band**: {brand_truth_panel.band} — copy allowed: {brand_truth_panel.copy_allowed}")
        if brand_truth_panel.degrade_reason:
            lines.append(f"- **degrade cause**: {brand_truth_panel.degrade_reason}")
        lines.append(f"- **fact classes loaded**: {', '.join(brand_truth_panel.fact_classes_loaded)}")
        lines.append("")

    if spin_results:
        lines.append("## Spin rationale (per EN asset)")
        lines.append("")
        for sr in spin_results.values():
            lines.append(f"- {sr.rationale_line}")
        lines.append("")

    if cs_holds:
        lines.append("## Czech candidates — held (not in this goal's scope)")
        lines.append("")
        for hold in cs_holds:
            lines.append(f"- **{hold['topic']}** ({hold['language']}): {hold['outcome']}")
        lines.append("")

    if copy_asset_statuses is not None:
        lines.append("## Copy status (per asset)")
        lines.append("")
        if copy_asset_statuses:
            lines.append("| asset | destination | status | attempt | failing spans |")
            lines.append("|---|---|---|---|---|")
            for s in copy_asset_statuses:
                spans = "; ".join(s.failing_spans) if s.failing_spans else "—"
                lines.append(f"| {s.asset_id} | {s.destination} | {s.status} | {s.attempt} | {spans} |")
        else:
            lines.append("_No copy assets this run (no EN candidates reached spin/copy, or copy was refused)._")
        lines.append("")

    if media_asset_statuses is not None:
        lines.append("## Media status (per asset) — draft-tier images, images only, nothing publishes")
        lines.append("")
        if media_asset_statuses:
            lines.append("| asset | route | cost | provenance | image | logo overlay |")
            lines.append("|---|---|---|---|---|---|")
            for s in media_asset_statuses:
                route = s.route_id or "—"
                cost = f"${s.observed_cost_usd:.4f}" if s.observed_cost_usd else (
                    f"~${s.expected_cost_usd:.4f}" if s.expected_cost_usd else "$0.00"
                )
                provenance = s.delivered_route_state or "—"
                image = s.image_path or "—"
                lines.append(f"| {s.asset_id} ({s.status}) | {route} | {cost} | {provenance} | {image} | deferred to a later phase |")
        else:
            lines.append("_No media assets this run._")
        lines.append("")
        pending = [s for s in media_asset_statuses if s.status == "pending — adopted by a later run"]
        if pending:
            lines.append(
                f"**{len(pending)} media job(s) still pending** — adopted by a later run's phase-0 resolution; "
                "provider media is deleted after 14 days, so re-running this pipeline soon rescues that spend."
            )
            lines.append("")
        unknown = [s for s in media_asset_statuses if s.status == "submitted-unknown"]
        if unknown:
            lines.append(
                f"**{len(unknown)} media job(s) could not be resolved** — treated as `submitted-unknown`, "
                "never auto-resubmitted; expected cost is carried on the ledger's expected side until resolved "
                "or the resolution window lapses to `paid-lost`."
            )
            lines.append("")

    lines.append("## Footer")
    lines.append("")
    lines.append(f"- full run trace: [{TRACE_RELATIVE_LINK}]({TRACE_RELATIVE_LINK})")
    lines.append("")

    return "\n".join(lines) + "\n"


def package_candidates(
    *,
    run_id: str,
    run_dir: Path,
    store: Store,
    ranking_result: RankingResult,
    languages: list[str],
) -> PackagingSummary:
    """The ``packaging`` stage's work: scorecards, signal provenance, and
    registering every included canonical key transactionally with the pack
    write (files land on disk before the index row does). Does not write
    ``digest.md`` — that is the separate ``digest`` stage, see :func:`write_digest`.
    """
    pack_dir = run_dir / "pack"
    pack_dir.mkdir(parents=True, exist_ok=True)

    scorecard_paths = write_scorecards(pack_dir, ranking_result.all_scorecards)

    pairs = [
        (sc, ranking_result.candidate_canonical_keys.get(sc.cluster_key, []))
        for sc in ranking_result.all_scorecards
        if sc.composite is not None
    ]
    signal_paths, registrations = write_signal_provenance_for_candidates(pack_dir, store, pairs)

    # Register transactionally with the pack write: files are already on
    # disk at this point, so the index row and the files it points at are
    # never out of sync in the direction that matters (index -> missing file).
    store.register_pack_keys(run_id=run_id, pack_path=str(pack_dir), entries=registrations)

    # Mark every top-ranked (generate) topic as "generated" in the dedupe
    # index — this is prior-pack state for the NEXT run's resurgence check.
    for language in languages:
        for sc in ranking_result.top_by_language.get(language, []):
            store.mark_generated(sc.cluster_key, run_id)

    return PackagingSummary(
        pack_dir=pack_dir,
        digest_path=pack_dir / "digest.md",
        scorecard_paths=scorecard_paths,
        signal_paths=signal_paths,
        registered_keys=len(registrations),
    )


def write_digest(
    *,
    run_id: str,
    run_date: str,
    theme_name: str,
    run_dir: Path,
    ranking_result: RankingResult,
    degraded_sources: list[DegradedSourceNote],
    languages: list[str],
    brand_truth_panel: Any | None = None,
    spin_results: dict[str, Any] | None = None,
    copy_asset_statuses: list[Any] | None = None,
    cs_holds: list[dict[str, str]] | None = None,
    media_asset_statuses: list[Any] | None = None,
    media_registry_price_snapshot_date: str | None = None,
) -> Path:
    """The ``digest`` stage's work: render and write ``digest.md`` into the
    already-packaged pack directory."""
    pack_dir = run_dir / "pack"
    pack_dir.mkdir(parents=True, exist_ok=True)
    digest_text = render_digest(
        run_id=run_id,
        run_date=run_date,
        theme_name=theme_name,
        ranking_result=ranking_result,
        degraded_sources=degraded_sources,
        languages=languages,
        zero_candidates_message=ranking_result.zero_passing_candidates,
        brand_truth_panel=brand_truth_panel,
        spin_results=spin_results,
        copy_asset_statuses=copy_asset_statuses,
        cs_holds=cs_holds,
        media_asset_statuses=media_asset_statuses,
        media_registry_price_snapshot_date=media_registry_price_snapshot_date,
    )
    digest_path = pack_dir / "digest.md"
    digest_path.write_text(digest_text, encoding="utf-8")
    return digest_path
