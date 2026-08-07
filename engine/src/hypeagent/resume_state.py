"""Persisted resume state for ``python -m hypeagent --resume <run_id>``.

``--resume`` re-enters ONLY ``copy`` -> ``media`` -> ``packaging`` ->
``digest`` (main.py, ``stages.resume_pipeline``). Those stages read
``ranking_result``, the brand-truth panel, ``spin_results``, ``cs_holds``
and ``degraded_sources`` out of ``RunContext.extra`` — normally populated by
actually running ``collection`` / ``ranking`` / ``brand_truth`` / ``spin``.
A resumed invocation must NOT re-run those stages (re-running ``ranking``
would re-hit cross-day dedupe and very likely suppress everything; re-running
``brand_truth`` could silently pick up a *different* claim-ledger snapshot
than the one the original run's copy gate was built against).

So every normal run persists everything the resumable stages need into one
file, ``logs/runs/<run_id>/resume_state.yaml``, written once by
``stages.stage_spin`` (the last of the four non-resumable stages, and the
point at which every one of these objects is fully populated in
``ctx.extra``). ``--resume`` loads it back byte-for-byte instead of
re-deriving anything — "persist it at first-run time" rather than
re-computing, exactly the instruction this module exists to satisfy.

Every object serialized here is already a plain-field dataclass
(``Scorecard``, ``SpinResult``, ``DegradedSourceNote``) except the
brand-truth panel, whose ``BrandFacts``/``ClaimSnapshot`` carry a
``pathlib.Path`` field that YAML cannot represent directly — those two get
explicit ``to_dict``/``from_dict`` pairs below rather than a generic
``dataclasses.asdict`` round trip, so the ``Path`` conversion is never left
implicit.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from hypeagent.brand_truth import (
    BrandFacts,
    BrandTruthPanel,
    Capability,
    ClaimEntry,
    ClaimSnapshot,
    CtaOption,
    IcpSegment,
)
from hypeagent.packaging import DegradedSourceNote
from hypeagent.ranking import RankingResult, Scorecard
from hypeagent.spin import SpinResult

RESUME_STATE_FILENAME = "resume_state.yaml"


@dataclass
class ResumeState:
    """Everything ``stages.resume_pipeline`` needs in ``ctx.extra`` to
    re-enter copy/media/packaging/digest without re-running collection,
    ranking, brand_truth or spin."""

    languages: list[str]
    ranking_result: RankingResult
    brand_truth_panel: BrandTruthPanel
    spin_results: dict[str, SpinResult]
    cs_holds: list[dict[str, str]]
    degraded_sources: list[DegradedSourceNote]
    # W8-9 Q3a: the analysis stage's ``viral_playbook.yaml`` path (``None``
    # when the stage never ran on this run_id — e.g. a run predating this
    # engine version). ``copy`` reads it back on ``--resume`` re-entry
    # without re-running ``analysis`` (which is not in ``RESUME_STAGE_NAMES``).
    viral_playbook_path: str | None = None


# ---------------------------------------------------------------------------
# Scorecard / RankingResult
# ---------------------------------------------------------------------------


def _scorecard_to_dict(sc: Scorecard) -> dict[str, Any]:
    return dataclasses.asdict(sc)


def _scorecard_from_dict(d: dict[str, Any]) -> Scorecard:
    return Scorecard(**d)


def _ranking_result_to_dict(rr: RankingResult) -> dict[str, Any]:
    return {
        "all_scorecards": [_scorecard_to_dict(sc) for sc in rr.all_scorecards],
        # Stored as cluster keys, not full scorecards a second time --
        # reconstructed by lookup against ``all_scorecards`` below, so the
        # (rare, currently never-happening) case of a per-language list
        # referencing a scorecard by identity still round-trips correctly
        # by key rather than by a second independent copy.
        "top_by_language": {lang: [sc.cluster_key for sc in scs] for lang, scs in rr.top_by_language.items()},
        "evidence_floor_breached": dict(rr.evidence_floor_breached),
        "evidence_floor_consecutive": dict(rr.evidence_floor_consecutive),
        "active_family_count": rr.active_family_count,
        "zero_passing_candidates": rr.zero_passing_candidates,
        "candidate_canonical_keys": {k: list(v) for k, v in rr.candidate_canonical_keys.items()},
        "stale_skipped_count": rr.stale_skipped_count,
    }


def _ranking_result_from_dict(d: dict[str, Any]) -> RankingResult:
    all_scorecards = [_scorecard_from_dict(sd) for sd in d.get("all_scorecards", [])]
    by_key = {sc.cluster_key: sc for sc in all_scorecards}
    top_by_language = {
        lang: [by_key[k] for k in keys if k in by_key]
        for lang, keys in (d.get("top_by_language") or {}).items()
    }
    return RankingResult(
        all_scorecards=all_scorecards,
        top_by_language=top_by_language,
        evidence_floor_breached=dict(d.get("evidence_floor_breached") or {}),
        evidence_floor_consecutive=dict(d.get("evidence_floor_consecutive") or {}),
        active_family_count=int(d.get("active_family_count", 1)),
        zero_passing_candidates=bool(d.get("zero_passing_candidates", True)),
        candidate_canonical_keys={k: list(v) for k, v in (d.get("candidate_canonical_keys") or {}).items()},
        stale_skipped_count=int(d.get("stale_skipped_count", 0)),
    )


# ---------------------------------------------------------------------------
# SpinResult / cs_holds / degraded_sources
# ---------------------------------------------------------------------------


def _spin_result_to_dict(sr: SpinResult) -> dict[str, Any]:
    return dataclasses.asdict(sr)


def _spin_result_from_dict(d: dict[str, Any]) -> SpinResult:
    return SpinResult(**d)


def _degraded_source_to_dict(note: DegradedSourceNote) -> dict[str, Any]:
    return dataclasses.asdict(note)


def _degraded_source_from_dict(d: dict[str, Any]) -> DegradedSourceNote:
    return DegradedSourceNote(**d)


# ---------------------------------------------------------------------------
# Brand-truth panel (explicit, because of the ``Path`` fields).
# ---------------------------------------------------------------------------


def _brand_facts_to_dict(facts: BrandFacts) -> dict[str, Any]:
    return {
        "identity": facts.identity,
        "capabilities_positive": [dataclasses.asdict(c) for c in facts.capabilities_positive],
        "capabilities_negative": list(facts.capabilities_negative),
        "icp": [dataclasses.asdict(i) for i in facts.icp],
        "cta_set": [dataclasses.asdict(c) for c in facts.cta_set],
        "pricing_policy": facts.pricing_policy,
        "pricing_rationale": facts.pricing_rationale,
        "hard_excludes_ref": facts.hard_excludes_ref,
        "spin_notes": facts.spin_notes,
        "source_path": str(facts.source_path),
    }


def _brand_facts_from_dict(d: dict[str, Any]) -> BrandFacts:
    return BrandFacts(
        identity=d["identity"],
        capabilities_positive=[Capability(**c) for c in d.get("capabilities_positive", [])],
        capabilities_negative=list(d.get("capabilities_negative", [])),
        icp=[IcpSegment(**i) for i in d.get("icp", [])],
        cta_set=[CtaOption(**c) for c in d.get("cta_set", [])],
        pricing_policy=d["pricing_policy"],
        pricing_rationale=d.get("pricing_rationale", ""),
        hard_excludes_ref=d.get("hard_excludes_ref", "config/hard_excludes.yaml"),
        spin_notes=d.get("spin_notes") or {},
        source_path=Path(d["source_path"]),
    )


def _claim_snapshot_to_dict(snapshot: ClaimSnapshot) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot.snapshot_id,
        "taken_at": snapshot.taken_at,
        "max_age_days": snapshot.max_age_days,
        "claims": [dataclasses.asdict(c) for c in snapshot.claims],
        "path": str(snapshot.path),
    }


def _claim_snapshot_from_dict(d: dict[str, Any]) -> ClaimSnapshot:
    return ClaimSnapshot(
        snapshot_id=d["snapshot_id"],
        taken_at=d["taken_at"],
        max_age_days=int(d["max_age_days"]),
        claims=[ClaimEntry(**c) for c in d.get("claims", [])],
        path=Path(d["path"]),
    )


def _panel_to_dict(panel: BrandTruthPanel) -> dict[str, Any]:
    return {
        "facts": _brand_facts_to_dict(panel.facts),
        "snapshot": _claim_snapshot_to_dict(panel.snapshot),
        "snapshot_age_days": panel.snapshot_age_days,
        "band": panel.band,
        "copy_allowed": panel.copy_allowed,
        "degrade_reason": panel.degrade_reason,
        "fact_classes_loaded": list(panel.fact_classes_loaded),
        "per_class_rows": list(panel.per_class_rows),
    }


def _panel_from_dict(d: dict[str, Any]) -> BrandTruthPanel:
    return BrandTruthPanel(
        facts=_brand_facts_from_dict(d["facts"]),
        snapshot=_claim_snapshot_from_dict(d["snapshot"]),
        snapshot_age_days=int(d["snapshot_age_days"]),
        band=d["band"],
        copy_allowed=bool(d["copy_allowed"]),
        degrade_reason=d.get("degrade_reason"),
        fact_classes_loaded=list(d.get("fact_classes_loaded", [])),
        per_class_rows=list(d.get("per_class_rows", [])),
    )


# ---------------------------------------------------------------------------
# Top-level read/write.
# ---------------------------------------------------------------------------


def write_resume_state(run_dir: Path, state: ResumeState) -> Path:
    """Write ``resume_state.yaml`` into ``run_dir`` (called once, at the end
    of ``stages.stage_spin``, on every ordinary run -- not conditional on
    whether any asset ends up held, so any run_id can later be resumed)."""
    doc: dict[str, Any] = {
        "languages": list(state.languages),
        "ranking_result": _ranking_result_to_dict(state.ranking_result),
        "brand_truth_panel": _panel_to_dict(state.brand_truth_panel),
        "spin_results": {k: _spin_result_to_dict(v) for k, v in state.spin_results.items()},
        "cs_holds": list(state.cs_holds),
        "degraded_sources": [_degraded_source_to_dict(d) for d in state.degraded_sources],
        "viral_playbook_path": state.viral_playbook_path,
    }
    path = Path(run_dir) / RESUME_STATE_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def load_resume_state(run_dir: Path) -> ResumeState | None:
    """Load ``resume_state.yaml`` back, or ``None`` if it was never written
    (the run never reached ``stage_spin`` -- e.g. it crashed or policy-stopped
    at an earlier stage). ``main.py``'s ``--resume`` treats ``None`` as a
    refusal condition: there is nothing to complete."""
    path = Path(run_dir) / RESUME_STATE_FILENAME
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ResumeState(
        languages=list(data.get("languages") or []),
        ranking_result=_ranking_result_from_dict(data["ranking_result"]),
        brand_truth_panel=_panel_from_dict(data["brand_truth_panel"]),
        spin_results={k: _spin_result_from_dict(v) for k, v in (data.get("spin_results") or {}).items()},
        cs_holds=list(data.get("cs_holds") or []),
        degraded_sources=[_degraded_source_from_dict(d) for d in (data.get("degraded_sources") or [])],
        viral_playbook_path=data.get("viral_playbook_path"),
    )
