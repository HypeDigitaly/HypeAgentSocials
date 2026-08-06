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
    lines.append("| media | $0.00 |")
    lines.append("| text-per-artifact | $0.00 |")
    lines.append("| text-per-candidate | $0.00 |")
    lines.append("")
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
    )
    digest_path = pack_dir / "digest.md"
    digest_path.write_text(digest_text, encoding="utf-8")
    return digest_path
