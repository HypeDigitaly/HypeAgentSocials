"""Brand-truth resolution (ARCHITECTURE_PLAN.md §6.3-§6.6, goal-scoped M3).

Two config-side inputs, both fail-closed at the loader boundary
(``ConfigError`` -> the run's existing ``policy-stop`` path, exactly like
every other config file in this engine):

- ``config/brand_facts.yaml`` — F-A identity, F-C capabilities (positive
  and negative), F-D ICP (may **not** be empty, §6.3), F-E CTA set, F-F
  pricing policy.
- ``config/snapshots/claim_ledger_snapshot_*.yaml`` — the F-H claim ledger,
  offline-snapshotted from Notion "Čísla a sliby" (§6.6). The loader always
  picks the **latest dated file** in the snapshots directory (lexicographic
  == chronological for ``YYYY-MM-DD`` filenames).

Goal-scoped simplification of §6.5's confidence-band machinery: a single
band, ``fresh`` or ``stale``, derived purely by counting the snapshot's age
against its own declared ``max_age_days`` — structured so a Phase-2-full
band computation can widen this field without changing its shape or its
callers. ``stale`` is the one degrade trigger this milestone implements:
the run continues research-only (collection + ranking still happen), and
the copy stage refuses to generate, with the cause stated in the digest.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from hypeagent.config_load import ConfigError, load_yaml_config

DEFAULT_MAX_AGE_DAYS = 30


# ---------------------------------------------------------------------------
# config/brand_facts.yaml
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Capability:
    id: str
    en: str
    note: str | None
    source: str


@dataclass(frozen=True)
class IcpSegment:
    id: str
    en: str
    source: str


@dataclass(frozen=True)
class CtaOption:
    id: str
    cta_class: str
    en: str
    note: str | None = None


@dataclass(frozen=True)
class BrandFacts:
    identity: dict[str, Any]
    capabilities_positive: list[Capability]
    capabilities_negative: list[str]
    icp: list[IcpSegment]
    cta_set: list[CtaOption]
    pricing_policy: str
    pricing_rationale: str
    hard_excludes_ref: str
    spin_notes: dict[str, Any]
    source_path: Path


def load_brand_facts(config_dir: Path) -> BrandFacts:
    """Load ``config/brand_facts.yaml``, fail-closed (§6.3).

    Missing file, missing F-A identity, or an empty F-D ICP list all raise
    :class:`ConfigError` — F-D is the one class in this file that "may NOT
    be empty" (§6.3 table); every other list here may legitimately be
    resolved-empty, but this milestone's brand_facts.yaml always carries
    F-C, F-E and F-F, so those are treated as required-present too rather
    than silently defaulting, since a missing key here means the config
    file itself regressed, not a deliberate empty statement.
    """
    path = config_dir / "brand_facts.yaml"
    data = load_yaml_config(path, name="brand_facts.yaml")

    identity = data.get("identity")
    if not identity or not isinstance(identity, dict):
        raise ConfigError("brand_facts.yaml: 'identity' (F-A) is missing or malformed")

    capabilities_block = data.get("capabilities") or {}
    positive_raw = capabilities_block.get("positive") or []
    positive = [
        Capability(
            id=c["id"], en=c["en"], note=c.get("note"), source=c.get("source", ""),
        )
        for c in positive_raw
    ]
    negative = [str(n) for n in (capabilities_block.get("negative") or [])]

    icp_raw = data.get("icp") or []
    icp = [IcpSegment(id=i["id"], en=i["en"], source=i.get("source", "")) for i in icp_raw]
    if not icp:
        raise ConfigError(
            "brand_facts.yaml: 'icp' (F-D) must not be empty (§6.3: F-D may NOT be legitimately empty)"
        )

    cta_raw = data.get("cta_set") or []
    cta_set = [
        CtaOption(id=c["id"], cta_class=c["class"], en=c["en"], note=c.get("note"))
        for c in cta_raw
    ]

    pricing_block = data.get("pricing_policy") or {}
    policy = pricing_block.get("policy")
    if not policy:
        raise ConfigError("brand_facts.yaml: 'pricing_policy.policy' (F-F) is missing")

    return BrandFacts(
        identity=identity,
        capabilities_positive=positive,
        capabilities_negative=negative,
        icp=icp,
        cta_set=cta_set,
        pricing_policy=str(policy),
        pricing_rationale=str(pricing_block.get("rationale", "")),
        hard_excludes_ref=str(data.get("hard_excludes_ref", "config/hard_excludes.yaml")),
        spin_notes=data.get("spin_notes") or {},
        source_path=path,
    )


# ---------------------------------------------------------------------------
# config/snapshots/claim_ledger_snapshot_*.yaml
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ClaimEntry:
    claim_key: str
    notion_row_id: str
    category: str
    behavior: str  # citovat | kvalifikovat | abstain
    text_cs: str
    canonical_source: str
    verified: str
    qualification: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class ClaimSnapshot:
    snapshot_id: str
    taken_at: str
    max_age_days: int
    claims: list[ClaimEntry]
    path: Path


def find_latest_snapshot(snapshots_dir: Path) -> Path | None:
    """Latest dated ``claim_ledger_snapshot_*.yaml`` file — lexicographic
    sort on an ISO-dated filename is chronological sort."""
    if not snapshots_dir.exists():
        return None
    candidates = sorted(snapshots_dir.glob("claim_ledger_snapshot_*.yaml"))
    return candidates[-1] if candidates else None


def load_claim_snapshot(snapshots_dir: Path) -> ClaimSnapshot:
    """Load the latest dated claim-ledger snapshot, fail-closed.

    No snapshot file at all is §6.5 condition 4 ("the claim ledger could
    not be read at all") — this loader treats that identically to every
    other "missing config" condition in this engine: :class:`ConfigError`,
    which the run maps to ``policy-stop``. A snapshot that exists but is
    older than its own ``max_age_days`` loads successfully here; staleness
    is a *degrade*, evaluated by :func:`resolve_brand_truth`, not a load
    failure.
    """
    path = find_latest_snapshot(snapshots_dir)
    if path is None:
        raise ConfigError(
            f"no claim ledger snapshot found under {snapshots_dir} — "
            "the claim ledger could not be read at all (§6.5 condition 4)"
        )
    data = load_yaml_config(path, name=f"snapshots/{path.name}")
    meta = data.get("meta") or {}
    snapshot_id = meta.get("snapshot_id")
    taken_at = meta.get("taken_at")
    max_age_days = meta.get("max_age_days", DEFAULT_MAX_AGE_DAYS)
    if not snapshot_id or not taken_at:
        raise ConfigError(f"malformed claim snapshot {path.name}: 'meta.snapshot_id'/'meta.taken_at' required")

    claims_raw = data.get("claims") or []
    claims = [
        ClaimEntry(
            claim_key=c["claim_key"],
            notion_row_id=c.get("notion_row_id", ""),
            category=c.get("category", ""),
            behavior=c.get("behavior", ""),
            text_cs=c.get("text_cs", ""),
            canonical_source=c.get("canonical_source", ""),
            verified=c.get("verified", ""),
            qualification=c.get("qualification"),
            note=c.get("note"),
        )
        for c in claims_raw
    ]
    return ClaimSnapshot(
        snapshot_id=str(snapshot_id),
        taken_at=str(taken_at),
        max_age_days=int(max_age_days),
        claims=claims,
        path=path,
    )


def snapshot_age_days(snapshot: ClaimSnapshot, *, now: date) -> int:
    taken = date.fromisoformat(snapshot.taken_at)
    return (now - taken).days


# ---------------------------------------------------------------------------
# The brand-truth panel: what gets packed and what the digest reads.
# ---------------------------------------------------------------------------


@dataclass
class BrandTruthPanel:
    facts: BrandFacts
    snapshot: ClaimSnapshot
    snapshot_age_days: int
    band: str  # fresh | stale  (goal-scoped stand-in for §6.5's FULL/PARTIAL/MINIMAL/INSUFFICIENT)
    copy_allowed: bool
    degrade_reason: str | None
    fact_classes_loaded: list[str] = field(default_factory=list)
    per_class_rows: list[dict[str, Any]] = field(default_factory=list)

    def to_yaml_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot.snapshot_id,
            "snapshot_taken_at": self.snapshot.taken_at,
            "snapshot_age_days": self.snapshot_age_days,
            "snapshot_max_age_days": self.snapshot.max_age_days,
            "band": self.band,
            "copy_allowed": self.copy_allowed,
            "degrade_reason": self.degrade_reason,
            "fact_classes_loaded": self.fact_classes_loaded,
            "per_class": self.per_class_rows,
        }


def resolve_brand_truth(config_dir: Path, *, now: date | None = None) -> BrandTruthPanel:
    """Load both brand-truth inputs and derive the goal-scoped fresh/stale
    band. Raises :class:`ConfigError` (fail-closed, ``policy-stop``) for
    every condition that is a genuine load failure; staleness alone is a
    degrade, not a raise."""
    moment = now if now is not None else datetime.now().astimezone().date()
    facts = load_brand_facts(Path(config_dir))
    snapshot = load_claim_snapshot(Path(config_dir) / "snapshots")

    age = snapshot_age_days(snapshot, now=moment)
    is_stale = age > snapshot.max_age_days
    band = "stale" if is_stale else "fresh"
    degrade_reason = None
    copy_allowed = True
    if is_stale:
        degrade_reason = (
            f"claim ledger snapshot '{snapshot.snapshot_id}' is {age}d old "
            f"(max_age_days={snapshot.max_age_days}) — degrading to research-only; "
            "the copy stage refuses to generate until a fresher snapshot is taken"
        )
        copy_allowed = False

    fact_classes_loaded = [
        "F-A identity", "F-C capabilities", "F-D icp", "F-E cta_set",
        "F-F pricing_policy", "F-H claim_ledger_snapshot",
    ]
    per_class_rows = [
        {"class": "F-A", "source": facts.identity.get("source", str(facts.source_path)), "verified": None},
        {"class": "F-C", "source": str(facts.source_path), "verified": None},
        {"class": "F-D", "source": str(facts.source_path), "verified": None},
        {"class": "F-E", "source": str(facts.source_path), "verified": None},
        {"class": "F-F", "source": str(facts.source_path), "verified": None},
        {"class": "F-H", "source": snapshot.path.name, "verified": snapshot.taken_at},
    ]

    return BrandTruthPanel(
        facts=facts,
        snapshot=snapshot,
        snapshot_age_days=age,
        band=band,
        copy_allowed=copy_allowed,
        degrade_reason=degrade_reason,
        fact_classes_loaded=fact_classes_loaded,
        per_class_rows=per_class_rows,
    )
