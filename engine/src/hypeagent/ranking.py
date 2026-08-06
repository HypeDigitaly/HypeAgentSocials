"""Ranking (ARCHITECTURE_PLAN.md §2.7, §2.8, §2.8a).

Turns normalized signals into topic candidates with an inspectable
scorecard, in five steps:

1. **Clustering** — deterministic, no LLM: group by near-dup fingerprint
   plus normalized key-term overlap.
2. **Fit gate before the composite** — a brand-fit floor and a binary veto
   list, both absolute stop conditions checked before any score is computed.
3. **Composite** — evidence-class-aware virality (or none, for Czech),
   brand fit, freshness by signal class, and a confidence-and-availability
   term that also carries the corroboration bonus. The demand modifier is a
   labelled no-op hook (§2.7: "not present in Phase 1 — no vendor").
4. **Cross-day dedupe / resurgence** (§2.8a) — trajectory × prior-pack state
   decides normal / revisit / suppressed, via a swappable ``NewAngleJudge``.
5. **Top-N cap, applied after filtering** — never by lowering the threshold.

``FitJudge`` and ``NewAngleJudge`` are protocols so Phase 2 can swap in a
model-backed implementation (nodes N-1 and N-2) without touching anything
else in this module.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from hypeagent.store import ClusterObservation, SpecialCategoryLexicon, Store, StoredSignal

FIT_METHOD_LABEL = "phase1-deterministic-heuristic (no model judgment)"
NEW_ANGLE_METHOD_LABEL = "phase1-deterministic-heuristic (no model judgment)"

_STOPWORDS = {
    "the", "a", "an", "of", "for", "and", "or", "to", "in", "on", "with", "is", "are", "how",
    "why", "what", "this", "that", "new", "your", "you", "it", "as", "at", "by", "from",
    "s", "v", "na", "pro", "je", "se", "jak", "co", "a", "o", "z", "do", "ze",
}
_WORD_RE = re.compile(r"[a-zA-Z0-9À-žА-я]+")


def _tokens(text: str) -> set[str]:
    return {t for t in _WORD_RE.findall(text.lower()) if t not in _STOPWORDS and len(t) > 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def stable_cluster_key(term_signature: set[str]) -> str:
    payload = "|".join(sorted(term_signature))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass
class TopicCandidate:
    cluster_key: str
    language: str
    signals: list[StoredSignal]
    representative_title: str
    term_signature: set[str]

    @property
    def families(self) -> set[str]:
        return {s.source_family for s in self.signals}

    @property
    def sources(self) -> set[str]:
        return {s.source for s in self.signals}

    @property
    def has_counted_evidence(self) -> bool:
        return any(s.evidence_class == "counted" for s in self.signals)

    @property
    def fingerprints(self) -> set[str]:
        return {s.near_dup_fingerprint for s in self.signals}

    @property
    def most_recent_retrieval(self) -> datetime:
        return max(s.retrieval_time for s in self.signals)

    @property
    def any_injection_flagged(self) -> bool:
        return any(s.injection_flagged for s in self.signals)


def cluster_signals(signals: list[StoredSignal], *, overlap_threshold: float = 0.4) -> list[TopicCandidate]:
    """Deterministic clustering by language, near-dup fingerprint, and
    normalized key-term overlap (§2.7: "Topic clustering: group signals into
    topic candidates by near-dup fingerprint + normalized key-term overlap.
    (deterministic, no LLM)")."""
    by_language: dict[str, list[StoredSignal]] = {}
    for sig in signals:
        by_language.setdefault(sig.language, []).append(sig)

    candidates: list[TopicCandidate] = []
    for language, lang_signals in by_language.items():
        groups: list[list[StoredSignal]] = []
        group_tokens: list[set[str]] = []
        for sig in lang_signals:
            tokens = _tokens(sig.title)
            placed = False
            for idx, existing_tokens in enumerate(group_tokens):
                same_fingerprint = any(s.near_dup_fingerprint == sig.near_dup_fingerprint for s in groups[idx])
                if same_fingerprint or _jaccard(tokens, existing_tokens) >= overlap_threshold:
                    groups[idx].append(sig)
                    group_tokens[idx] |= tokens
                    placed = True
                    break
            if not placed:
                groups.append([sig])
                group_tokens.append(tokens)

        for group, tokens in zip(groups, group_tokens):
            top_terms = set(sorted(tokens)[:12]) if tokens else {group[0].title.lower()}
            cluster_key = stable_cluster_key(top_terms)
            representative = max(group, key=lambda s: len(s.excerpt))
            candidates.append(
                TopicCandidate(
                    cluster_key=cluster_key,
                    language=language,
                    signals=group,
                    representative_title=representative.title,
                    term_signature=top_terms,
                )
            )
    return candidates


# ---------------------------------------------------------------------------
# Fit gate: FitJudge protocol + Phase-1 deterministic heuristic.
# ---------------------------------------------------------------------------


@dataclass
class FitVerdict:
    score: float
    rationale: str
    matched_terms: list[str]
    method_label: str


class FitJudge(Protocol):
    """Behind this protocol so Phase 2 swaps in the model node (N-1)
    without touching ranking."""

    def judge(self, candidate: TopicCandidate, *, watch_terms: set[str]) -> FitVerdict: ...


class Phase1DeterministicFitJudge:
    """Weighted keyword/term overlap against the theme's watch topics and
    ICP terms — Phase 1 has no LLM, so brand fit is a deterministic
    heuristic, labelled as such on every scorecard (§2.7)."""

    def judge(self, candidate: TopicCandidate, *, watch_terms: set[str]) -> FitVerdict:
        candidate_terms = set()
        for sig in candidate.signals:
            candidate_terms |= _tokens(sig.title)
            candidate_terms |= _tokens(sig.excerpt)
        matched = sorted(candidate_terms & watch_terms)
        if not matched:
            return FitVerdict(
                score=0.0,
                rationale=f"no honest connection: none of the theme's watch terms appear in '{candidate.representative_title}'",
                matched_terms=[],
                method_label=FIT_METHOD_LABEL,
            )
        score = min(1.0, len(matched) / max(3, len(watch_terms) ** 0.5))
        rationale = f"connects to the theme via: {', '.join(matched[:6])}"
        return FitVerdict(score=score, rationale=rationale, matched_terms=matched, method_label=FIT_METHOD_LABEL)


# ---------------------------------------------------------------------------
# New-angle judge (N-2): FitJudge's sibling protocol for resurgence.
# ---------------------------------------------------------------------------


@dataclass
class NewAngleVerdict:
    is_new_angle: bool
    rationale: str
    method_label: str


class NewAngleJudge(Protocol):
    def judge(
        self,
        *,
        cluster_key: str,
        prior_families: set[str],
        current_families: set[str],
        new_fingerprint_count: int,
        min_new_signals: int,
    ) -> NewAngleVerdict | None: ...


class Phase1DeterministicNewAngleJudge:
    """A deterministic heuristic: a new corroborating source family since
    the cluster's last appearance, or at least K new signals with unseen
    fingerprints, counts as a new angle (§2.8a node N-2, Phase-1 stand-in)."""

    def judge(
        self,
        *,
        cluster_key: str,
        prior_families: set[str],
        current_families: set[str],
        new_fingerprint_count: int,
        min_new_signals: int,
    ) -> NewAngleVerdict | None:
        new_families = current_families - prior_families
        if new_families:
            return NewAngleVerdict(
                is_new_angle=True,
                rationale=f"new angle: new corroborating source family — {', '.join(sorted(new_families))}",
                method_label=NEW_ANGLE_METHOD_LABEL,
            )
        if new_fingerprint_count >= min_new_signals:
            return NewAngleVerdict(
                is_new_angle=True,
                rationale=f"new angle: {new_fingerprint_count} new signals with previously-unseen fingerprints",
                method_label=NEW_ANGLE_METHOD_LABEL,
            )
        return NewAngleVerdict(
            is_new_angle=False,
            rationale="nothing new since prior appearance",
            method_label=NEW_ANGLE_METHOD_LABEL,
        )


# ---------------------------------------------------------------------------
# Veto list + brand-fit floor (the fit gate, run BEFORE the composite).
# ---------------------------------------------------------------------------


@dataclass
class GateResult:
    passed: bool
    reason: str | None


def evaluate_fit_gate(
    candidate: TopicCandidate,
    fit_verdict: FitVerdict,
    *,
    brand_fit_floor: float,
    hard_exclude_topics: set[str],
    lexicon: SpecialCategoryLexicon,
) -> GateResult:
    """The fit gate: brand-fit floor (1) and the binary veto list (2), both
    absolute stop conditions checked before scoring (§2.7)."""
    if candidate.any_injection_flagged:
        return GateResult(passed=False, reason="veto: prompt-injection phrasing detected in signal text")

    combined_text = " ".join(f"{s.title} {s.excerpt}" for s in candidate.signals)
    special_category_hit = lexicon.matches(combined_text)
    if special_category_hit is not None:
        return GateResult(passed=False, reason=f"veto: special-category content re-check hit ({special_category_hit})")

    candidate_terms = _tokens(candidate.representative_title)
    if hard_exclude_topics & candidate_terms:
        return GateResult(passed=False, reason=f"veto: hard-excluded topic match ({sorted(hard_exclude_topics & candidate_terms)})")

    if fit_verdict.score < brand_fit_floor:
        return GateResult(passed=False, reason=f"brand-fit floor not met: {fit_verdict.score:.2f} < {brand_fit_floor:.2f}")

    if not fit_verdict.matched_terms:
        return GateResult(passed=False, reason="fit judge could not state an honest connection")

    return GateResult(passed=True, reason=None)


# ---------------------------------------------------------------------------
# Composite scoring.
# ---------------------------------------------------------------------------

RANKED_CONFIDENCE_CEILING = 0.5
LAUNCH_POD_DISCOUNT_FACTOR = 0.7
BASELINE_MIN_DAYS = 14


@dataclass
class VirialityResult:
    score: float
    evidence_quality_label: str


def compute_virality(
    candidate: TopicCandidate,
    *,
    store: Store,
    absolute_band_fallback: dict[str, dict[str, float]],
    baseline_lookback_days: int,
) -> VirialityResult:
    """Evidence-class-aware virality (§2.7's evidence-class table)."""
    if not candidate.has_counted_evidence:
        # Ranked/presence-only: a rank proxy with a hard confidence ceiling —
        # it can never reach the High evidence band.
        best_rank = min(
            (s.metrics.get("rank", 999) for s in candidate.signals if s.evidence_class == "ranked"),
            default=999,
        )
        proxy = 1.0 / (1.0 + max(0, best_rank - 1))
        score = min(RANKED_CONFIDENCE_CEILING, proxy * RANKED_CONFIDENCE_CEILING)
        label = "ranked/presence-only — hard confidence ceiling applied (never reaches High band)"
        if any(s.metrics.get("launch_pod_discount") for s in candidate.signals):
            score *= LAUNCH_POD_DISCOUNT_FACTOR
            label += "; launch-pod vote-distortion discount applied"
        return VirialityResult(score=score, evidence_quality_label=label)

    counted_signals = [s for s in candidate.signals if s.evidence_class == "counted"]
    best_score = 0.0
    labels = []
    for sig in counted_signals:
        metric_name = "score" if "score" in sig.metrics else ("likes" if "likes" in sig.metrics else None)
        if metric_name is None:
            continue
        value = float(sig.metrics.get(metric_name, 0))
        baseline_days = store.trailing_baseline_days(source=sig.source)
        if baseline_days < BASELINE_MIN_DAYS:
            bands = absolute_band_fallback.get(sig.source, {"low": 5, "mid": 50, "high": 200})
            if value >= bands.get("high", 200):
                normalized = 0.9
            elif value >= bands.get("mid", 50):
                normalized = 0.6
            elif value >= bands.get("low", 5):
                normalized = 0.35
            else:
                normalized = 0.1
            labels.append("no baseline yet (absolute-band fallback)")
        else:
            distribution = store.trailing_metric_distribution(
                source=sig.source, metric_name=metric_name, within_days=baseline_lookback_days
            )
            normalized = _percentile_of(value, distribution)
            labels.append("percentile within trailing distribution")
        best_score = max(best_score, normalized)
    label = "; ".join(sorted(set(labels))) if labels else "counted evidence, no usable metric"
    return VirialityResult(score=best_score, evidence_quality_label=label)


def _percentile_of(value: float, distribution: list[float]) -> float:
    if not distribution:
        return 0.5
    below = sum(1 for v in distribution if v <= value)
    return below / len(distribution)


SIGNAL_CLASS_BY_SOURCE = {
    "hacker_news": "spike",
    "hugging_face": "launch-hype",
    "product_hunt": "launch-hype",
    "google_news": "rising",
    "virlo": "spike",  # short-form trends decay fast — same half-life class as HN spikes
}


def classify_signal(candidate: TopicCandidate) -> str:
    classes = {SIGNAL_CLASS_BY_SOURCE.get(s.source, "rising") for s in candidate.signals}
    for preferred in ("spike", "launch-hype", "rising", "evergreen-pain"):
        if preferred in classes:
            return preferred
    return "rising"


def compute_freshness(candidate: TopicCandidate, *, half_life_hours: dict[str, float], now: datetime) -> tuple[float, str, float]:
    signal_class = classify_signal(candidate)
    age_hours = max(0.0, (now - candidate.most_recent_retrieval).total_seconds() / 3600.0)
    half_life = half_life_hours.get(signal_class, 24.0)
    freshness = 0.5 ** (age_hours / half_life) if half_life > 0 else 1.0
    return freshness, signal_class, age_hours


def compute_confidence_availability(
    candidate: TopicCandidate,
    *,
    active_family_count: int,
    reachable_source_fraction: float,
    corroboration_bonus: float,
) -> tuple[float, str]:
    families = candidate.families
    base = len(families) / max(1, active_family_count)
    bonus_multiplier = 1.0 + corroboration_bonus * max(0, len(families) - 1)
    score = min(1.0, base * bonus_multiplier * reachable_source_fraction)
    rationale = (
        f"{len(families)} of {active_family_count} active source families corroborated this candidate; "
        f"{reachable_source_fraction * 100:.0f}% of this run's portfolio was reachable"
    )
    return score, rationale


@dataclass
class DemandModifierResult:
    multiplier: float
    label: str


def apply_demand_modifier(composite: float) -> tuple[float, DemandModifierResult]:
    """Phase 1 has no demand vendor (§2.7). The hook exists so Phase 2 wires
    a real modifier without touching the composite's shape."""
    result = DemandModifierResult(multiplier=1.0, label="demand modifier unavailable (Phase 1: no vendor)")
    return composite * result.multiplier, result


def band_for(composite: float, *, capped_to_medium: bool) -> str:
    if composite >= 0.66 and not capped_to_medium:
        return "High"
    if composite >= 0.33:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Resurgence resolution (§2.8a) — the full outcome table.
# ---------------------------------------------------------------------------


@dataclass
class ResurgenceResult:
    outcome: str  # normal | revisit | suppressed
    tag: str | None
    what_changed: str
    dedupe_status: str


def resolve_resurgence(
    *,
    cluster_key: str,
    observation: ClusterObservation,
    current_families: set[str],
    current_fingerprints: set[str],
    new_angle_judge: NewAngleJudge | None,
    min_new_signals: int,
    rejected_at: datetime | None,
    rejection_suppression_days: int,
    corroboration_growth_override_families: int,
    now: datetime,
) -> ResurgenceResult:
    """The full §2.8a outcome table, exercised in all three of its
    Phase-1-gated states (rising-never-generated, rising-generated-with-new-
    angle, rising-generated-with-nothing-new)."""
    trajectory = observation.trajectory
    prior_state = observation.prior_pack_state

    if prior_state == "rejected":
        window_elapsed = (
            rejected_at is not None and (now - rejected_at).days >= rejection_suppression_days
        )
        new_family_count = len(current_families - observation.prior_families)
        override = new_family_count >= corroboration_growth_override_families
        if window_elapsed or override:
            reason = "rejection-suppression window elapsed" if window_elapsed else "corroboration grew across enough new families to override the rejection"
            return ResurgenceResult(
                outcome="normal", tag=None, what_changed=reason,
                dedupe_status=f"previously rejected; re-entering ({reason})",
            )
        return ResurgenceResult(
            outcome="suppressed", tag=None,
            what_changed="suppressed: within the rejection-suppression window, no corroboration-growth override",
            dedupe_status="rejected — suppressed",
        )

    if prior_state == "capped":
        return ResurgenceResult(
            outcome="suppressed", tag=None,
            what_changed="already generated (capped) — not re-spun from zero; completion is a Phase-2 concern",
            dedupe_status="capped — suppressed",
        )

    if trajectory in ("rising", "sustained") and prior_state == "never-generated":
        return ResurgenceResult(
            outcome="normal", tag=None,
            what_changed="first appearance — ordinary discovery, not a duplicate",
            dedupe_status="never generated before — normal candidate",
        )

    if trajectory in ("rising", "sustained") and prior_state == "generated":
        if new_angle_judge is None:
            return ResurgenceResult(
                outcome="suppressed", tag=None,
                what_changed="resurgence undetermined — new-angle judge could not run (fail-closed)",
                dedupe_status="resurgence undetermined — suppressed",
            )
        verdict = new_angle_judge.judge(
            cluster_key=cluster_key,
            prior_families=observation.prior_families,
            current_families=current_families,
            new_fingerprint_count=len(current_fingerprints - observation.prior_fingerprints),
            min_new_signals=min_new_signals,
        )
        if verdict is None:
            return ResurgenceResult(
                outcome="suppressed", tag=None,
                what_changed="resurgence undetermined — new-angle judge could not run (fail-closed)",
                dedupe_status="resurgence undetermined — suppressed",
            )
        if verdict.is_new_angle:
            return ResurgenceResult(
                outcome="revisit", tag="revisit: new angle",
                what_changed=verdict.rationale,
                dedupe_status=f"revisit: new angle — {verdict.rationale}",
            )
        return ResurgenceResult(
            outcome="suppressed", tag=None,
            what_changed=verdict.rationale,
            dedupe_status="generated previously, nothing new — suppressed",
        )

    if trajectory == "declining" and prior_state == "never-generated":
        return ResurgenceResult(
            outcome="normal", tag=None,
            what_changed="declining but never generated — ranks normally, freshness decay applies",
            dedupe_status="declining, never generated — normal candidate",
        )

    if trajectory == "declining" and prior_state == "generated":
        return ResurgenceResult(
            outcome="suppressed", tag=None,
            what_changed="declining with prior coverage — a duplicate with no new value",
            dedupe_status="declining, previously generated — suppressed permanently",
        )

    return ResurgenceResult(
        outcome="normal", tag=None,
        what_changed="no special dedupe condition applied",
        dedupe_status=f"trajectory={trajectory}, prior_state={prior_state}",
    )


# ---------------------------------------------------------------------------
# Scorecard.
# ---------------------------------------------------------------------------


@dataclass
class Scorecard:
    cluster_key: str
    language: str
    representative_title: str
    composite: float | None
    band: str
    sub_scores: dict[str, dict[str, object]]
    rationale: dict[str, str]
    sources: list[str]
    families: list[str]
    evidence_quality_label: str
    signal_class: str
    signal_age_hours: float
    gate_status: str
    per_language_outcome: str
    per_language_outcome_rationale: str
    ranking_config_version: int
    fit_method: str
    dedupe_status: str
    what_changed: str
    demand_modifier_label: str
    matched_terms: list[str] = field(default_factory=list)

    def to_yaml_dict(self) -> dict:
        return {
            "cluster_key": self.cluster_key,
            "language": self.language,
            "topic": self.representative_title,
            "composite": self.composite,
            "band": self.band,
            "sub_scores": self.sub_scores,
            "rationale": self.rationale,
            "sources": self.sources,
            "families": self.families,
            "evidence_quality_label": self.evidence_quality_label,
            "signal_class": self.signal_class,
            "signal_age_hours": round(self.signal_age_hours, 1),
            "gate_status": self.gate_status,
            "per_language_outcome": self.per_language_outcome,
            "per_language_outcome_rationale": self.per_language_outcome_rationale,
            "ranking_config_version": self.ranking_config_version,
            "fit_method": self.fit_method,
            "dedupe_status": self.dedupe_status,
            "what_changed_since_prior_appearance": self.what_changed,
            "demand_modifier": self.demand_modifier_label,
            "matched_terms": self.matched_terms,
        }


# ---------------------------------------------------------------------------
# Orchestration: theme research config -> ranking config -> full run.
# ---------------------------------------------------------------------------


@dataclass
class RankingConfig:
    version: int
    brand_fit_floor: float
    top_n_per_language: int
    half_life_hours: dict[str, float]
    baseline_lookback_days: int
    absolute_band_fallback: dict[str, dict[str, float]]
    dedupe_lookback_days: int
    rejection_suppression_days: int
    corroboration_growth_override_families: int
    new_angle_min_new_signals: int
    corroboration_bonus: float
    evidence_floor_min_candidates: dict[str, int]
    evidence_floor_min_families: dict[str, int]


@dataclass
class RankingResult:
    all_scorecards: list[Scorecard]
    top_by_language: dict[str, list[Scorecard]]
    evidence_floor_breached: dict[str, bool]
    evidence_floor_consecutive: dict[str, int]
    active_family_count: int
    zero_passing_candidates: bool
    candidate_canonical_keys: dict[str, list[str]]


def _watch_term_tokens(terms: list[str]) -> set[str]:
    tokens: set[str] = set()
    for term in terms:
        tokens |= _tokens(term)
    return tokens


def rank(
    *,
    store: Store,
    signals: list[StoredSignal],
    watch_terms_by_language: dict[str, list[str]],
    hard_exclude_topics: list[str],
    lexicon: SpecialCategoryLexicon,
    config: RankingConfig,
    run_id: str,
    fit_judge: FitJudge | None = None,
    new_angle_judge: NewAngleJudge | None = None,
    reachable_source_fraction: float = 1.0,
    languages: list[str] | None = None,
    now: datetime | None = None,
) -> RankingResult:
    """The full ranking pipeline for one run: cluster -> fit gate ->
    composite -> resurgence -> top-N cap (§2.7, §2.8, §2.8a)."""
    moment = now if now is not None else datetime.now().astimezone()
    fit_judge = fit_judge or Phase1DeterministicFitJudge()
    exclude_tokens = _watch_term_tokens(hard_exclude_topics)

    candidates = cluster_signals(signals)
    active_family_count = max(1, len({s.source_family for s in signals}))

    scorecards: list[Scorecard] = []
    passing_by_language: dict[str, list[tuple[float, Scorecard]]] = {}
    candidate_canonical_keys: dict[str, list[str]] = {
        c.cluster_key: sorted({s.canonical_key for s in c.signals}) for c in candidates
    }

    for candidate in candidates:
        watch_terms = _watch_term_tokens(watch_terms_by_language.get(candidate.language, []))
        fit_verdict = fit_judge.judge(candidate, watch_terms=watch_terms)
        gate = evaluate_fit_gate(
            candidate, fit_verdict,
            brand_fit_floor=config.brand_fit_floor,
            hard_exclude_topics=exclude_tokens,
            lexicon=lexicon,
        )

        if not gate.passed:
            scorecards.append(
                Scorecard(
                    cluster_key=candidate.cluster_key,
                    language=candidate.language,
                    representative_title=candidate.representative_title,
                    composite=None,
                    band="N/A",
                    sub_scores={"fit": {"numeric": round(fit_verdict.score, 3), "band": "Low"}},
                    rationale={"fit": fit_verdict.rationale},
                    sources=sorted(candidate.sources),
                    families=sorted(candidate.families),
                    evidence_quality_label="not scored — gate failed",
                    signal_class=classify_signal(candidate),
                    signal_age_hours=(moment - candidate.most_recent_retrieval).total_seconds() / 3600.0,
                    gate_status=f"skip: {gate.reason}",
                    per_language_outcome="skip",
                    per_language_outcome_rationale=gate.reason or "gate failed",
                    ranking_config_version=config.version,
                    fit_method=FIT_METHOD_LABEL,
                    dedupe_status="not evaluated — gate failed before dedupe",
                    what_changed="n/a — candidate did not pass the fit gate",
                    demand_modifier_label="n/a — not scored",
                )
            )
            continue

        virality = compute_virality(
            candidate, store=store,
            absolute_band_fallback=config.absolute_band_fallback,
            baseline_lookback_days=config.baseline_lookback_days,
        )
        freshness, signal_class, age_hours = compute_freshness(
            candidate, half_life_hours=config.half_life_hours, now=moment
        )
        confidence, confidence_rationale = compute_confidence_availability(
            candidate,
            active_family_count=active_family_count,
            reachable_source_fraction=reachable_source_fraction,
            corroboration_bonus=config.corroboration_bonus,
        )

        drops_virality = candidate.language != "en" and not candidate.has_counted_evidence
        if candidate.has_counted_evidence:
            composite_pre_demand = virality.score * fit_verdict.score * freshness * confidence
        elif candidate.language == "en":
            # English but no counted evidence this cluster happened to gather —
            # still uses the 4-factor EN composite with the (capped) ranked score.
            composite_pre_demand = virality.score * fit_verdict.score * freshness * confidence
        else:
            # Non-English with no counted-evidence source anywhere in the
            # portfolio drops virality entirely (§2.7): composite = fit x
            # freshness x confidence.
            composite_pre_demand = fit_verdict.score * freshness * confidence

        composite, demand_result = apply_demand_modifier(composite_pre_demand)
        capped_to_medium = not candidate.has_counted_evidence
        band = band_for(composite, capped_to_medium=capped_to_medium)

        observation = store.observe_cluster(
            cluster_key=candidate.cluster_key,
            families=sorted(candidate.families),
            percentile=virality.score if candidate.has_counted_evidence else None,
            fingerprints=sorted(candidate.fingerprints),
            now=moment,
        )
        rejected_at = store.get_rejected_at(candidate.cluster_key)
        resurgence = resolve_resurgence(
            cluster_key=candidate.cluster_key,
            observation=observation,
            current_families=candidate.families,
            current_fingerprints=candidate.fingerprints,
            new_angle_judge=new_angle_judge,
            min_new_signals=config.new_angle_min_new_signals,
            rejected_at=rejected_at,
            rejection_suppression_days=config.rejection_suppression_days,
            corroboration_growth_override_families=config.corroboration_growth_override_families,
            now=moment,
        )

        non_comparability_note = (
            "EN composite includes virality; CS composite omits it entirely — the two numbers are not comparable"
            if candidate.language != "en"
            else "comparable only to other EN candidates (CS composite omits virality)"
        )

        scorecard = Scorecard(
            cluster_key=candidate.cluster_key,
            language=candidate.language,
            representative_title=candidate.representative_title,
            composite=round(composite, 4),
            band=band,
            sub_scores={
                "virality": {
                    "numeric": round(virality.score, 3) if drops_virality is False else None,
                    "band": band_for(virality.score, capped_to_medium=capped_to_medium) if not drops_virality else "omitted (CS)",
                },
                "fit": {"numeric": round(fit_verdict.score, 3), "band": band_for(fit_verdict.score, capped_to_medium=False)},
                "freshness": {"numeric": round(freshness, 3), "band": band_for(freshness, capped_to_medium=False)},
                "confidence_availability": {"numeric": round(confidence, 3), "band": band_for(confidence, capped_to_medium=False)},
            },
            rationale={
                "virality": "virality omitted — Czech composite has no counted-evidence source (§2.7)"
                if drops_virality
                else virality.evidence_quality_label,
                "fit": fit_verdict.rationale,
                "freshness": f"signal class '{signal_class}', {age_hours:.1f}h old",
                "confidence_availability": confidence_rationale,
                "non_comparability": non_comparability_note,
            },
            sources=sorted(candidate.sources),
            families=sorted(candidate.families),
            evidence_quality_label=virality.evidence_quality_label,
            signal_class=signal_class,
            signal_age_hours=age_hours,
            gate_status="pass",
            per_language_outcome="pending-topn",
            per_language_outcome_rationale="",
            ranking_config_version=config.version,
            fit_method=FIT_METHOD_LABEL,
            dedupe_status=resurgence.dedupe_status,
            what_changed=resurgence.what_changed,
            demand_modifier_label=demand_result.label,
            matched_terms=fit_verdict.matched_terms,
        )

        if resurgence.outcome == "suppressed":
            scorecard.per_language_outcome = "skip"
            scorecard.per_language_outcome_rationale = f"suppressed by cross-day dedupe: {resurgence.what_changed}"
            scorecard.gate_status = "pass (fit gate) — suppressed by dedupe"
            scorecards.append(scorecard)
            continue

        if resurgence.tag:
            scorecard.dedupe_status = f"{resurgence.tag} — {resurgence.what_changed}"

        scorecards.append(scorecard)
        passing_by_language.setdefault(candidate.language, []).append((composite, scorecard))

    top_by_language: dict[str, list[Scorecard]] = {}
    languages = languages or sorted(set(watch_terms_by_language.keys()) | set(passing_by_language.keys()))
    evidence_floor_breached: dict[str, bool] = {}
    evidence_floor_consecutive: dict[str, int] = {}

    for language in languages:
        entries = sorted(passing_by_language.get(language, []), key=lambda pair: pair[0], reverse=True)
        top_n = config.top_n_per_language
        top_entries = entries[:top_n]
        held_entries = entries[top_n:]
        for _, sc in top_entries:
            sc.per_language_outcome = "generate"
            sc.per_language_outcome_rationale = "ranked within this run's top-N cap for its language"
        for _, sc in held_entries:
            sc.per_language_outcome = "hold"
            sc.per_language_outcome_rationale = "passed the fit gate but fell outside the top-N cap (monitor-only)"
        top_by_language[language] = [sc for _, sc in top_entries]

        families_seen = {f for _, sc in entries for f in sc.families}
        min_candidates = config.evidence_floor_min_candidates.get(language, 1)
        min_families = config.evidence_floor_min_families.get(language, 1)
        breached = len(entries) < min_candidates or len(families_seen) < min_families
        evidence_floor_breached[language] = breached
        evidence_floor_consecutive[language] = store.record_evidence_floor(
            language=language, breached=breached, run_id=run_id
        )

    zero_passing = not any(top_by_language.values())

    return RankingResult(
        all_scorecards=scorecards,
        top_by_language=top_by_language,
        evidence_floor_breached=evidence_floor_breached,
        evidence_floor_consecutive=evidence_floor_consecutive,
        active_family_count=active_family_count,
        zero_passing_candidates=zero_passing,
        candidate_canonical_keys=candidate_canonical_keys,
    )

