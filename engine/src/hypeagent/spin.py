"""Spin mapping — deterministic, no LLM (ARCHITECTURE_PLAN.md §6.9, §12.1).

Topic candidate (a ranked ``Scorecard``) -> detected pain -> best-fit ICP
segment -> mapped offer (capability, adjacency-ranked) -> mapping distance
-> CTA class -> the one-line rationale in the §12.1 shape.

**Far distance forces the value-only variant.** This is the deterministic
half of the spin gate's floor (§14.1, §6.10 criterion S-4): a topic whose
best-matching capability's term overlap falls below the "adjacent"
threshold gets no offer, no product/product-adjacent CTA, ever — it is
structurally impossible for far-distance spin output to carry a pitch,
not merely discouraged.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from hypeagent.brand_truth import BrandFacts, CtaOption, IcpSegment
from hypeagent.config_load import MappingDistanceBands, PostMixConfig
from hypeagent.ranking import Scorecard

_WORD_RE = re.compile(r"[a-zA-Z0-9À-žА-я]+")
_STOPWORDS = {
    "the", "a", "an", "of", "for", "and", "or", "to", "in", "on", "with", "is", "are",
    "how", "why", "what", "this", "that", "new", "your", "you", "it", "as", "at", "by", "from",
}


def _tokens(text: str) -> set[str]:
    return {t for t in _WORD_RE.findall(text.lower()) if t not in _STOPWORDS and len(t) > 2}


def _overlap_score(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


@dataclass(frozen=True)
class OfferMatch:
    capability_id: str | None
    capability_text: str | None
    score: float
    adjacency_rank: int  # 1 = best match; 0 when no capability configured at all


@dataclass(frozen=True)
class SpinResult:
    cluster_key: str
    topic: str
    language: str
    icp_id: str
    icp_text: str
    pain: str
    offer_id: str | None
    offer_text: str | None
    mapping_distance: str  # near | adjacent | far
    mapping_score: float
    cta_id: str
    cta_class: str
    cta_text: str
    band: str
    value_only: bool
    rationale_line: str
    # W8-10 Phase 5 (``generation.post_mix``): value_only | playbook |
    # promotional. Defaults to "promotional" -- ``spin_for_scorecard`` never
    # sets this itself (it stays fully distance-derived); only
    # ``allocate_post_types`` assigns anything else, and only when a theme's
    # ``post_mix`` block is non-zero.
    post_type: str = "promotional"

    def to_yaml_dict(self) -> dict:
        return {
            "cluster_key": self.cluster_key,
            "topic": self.topic,
            "language": self.language,
            "icp": {"id": self.icp_id, "text": self.icp_text},
            "pain": self.pain,
            "offer": {"id": self.offer_id, "text": self.offer_text},
            "mapping_distance": self.mapping_distance,
            "mapping_score": round(self.mapping_score, 3),
            "cta": {"id": self.cta_id, "class": self.cta_class, "text": self.cta_text},
            "band": self.band,
            "value_only": self.value_only,
            "rationale_line": self.rationale_line,
            "post_type": self.post_type,
        }


def detect_pain(matched_terms: list[str], *, representative_title: str) -> str:
    """The detected pain is the topic's matched theme terms — a lookup, not
    an inference (§6.9)."""
    if matched_terms:
        return ", ".join(matched_terms[:4])
    return f"unspecified pain — no matched theme term for '{representative_title}'"


def best_icp(topic_terms: set[str], icp_segments: list[IcpSegment]) -> tuple[IcpSegment, float]:
    """Best-scoring of the ICP segments by term overlap (§6.9). ``icp_segments``
    is never empty at this call site — brand-truth resolution fails closed on
    an empty F-D ICP list before spin ever runs."""
    best: IcpSegment | None = None
    best_score = -1.0
    for segment in icp_segments:
        score = _overlap_score(topic_terms, _tokens(segment.en))
        if score > best_score:
            best, best_score = segment, score
    assert best is not None
    return best, max(0.0, best_score)


def best_offer(topic_terms: set[str], facts: BrandFacts) -> OfferMatch:
    """The mapped offer: the F-C positive capability with the highest term
    overlap, adjacency-ranked (§6.9). Empty F-C -> no offer, ever — the
    correct answer when nothing matches above threshold is *no offer*."""
    if not facts.capabilities_positive:
        return OfferMatch(capability_id=None, capability_text=None, score=0.0, adjacency_rank=0)
    scored = sorted(
        (
            (cap, _overlap_score(topic_terms, _tokens(cap.en)))
            for cap in facts.capabilities_positive
        ),
        key=lambda pair: pair[1],
        reverse=True,
    )
    best_cap, best_score = scored[0]
    return OfferMatch(capability_id=best_cap.id, capability_text=best_cap.en, score=best_score, adjacency_rank=1)


def mapping_distance_for(score: float, bands: MappingDistanceBands) -> str:
    if score >= bands.near_min:
        return "near"
    if score >= bands.adjacent_min:
        return "adjacent"
    return "far"


def _cta_by_class(cta_set: list[CtaOption], cta_class: str) -> CtaOption | None:
    for cta in cta_set:
        if cta.cta_class == cta_class:
            return cta
    return None


def choose_cta(distance: str, cta_set: list[CtaOption]) -> CtaOption:
    """CTA class is chosen by mapping distance (§6.9): far -> content only,
    never a direct/product-adjacent CTA on far distance. Falls back to the
    first available CTA of a looser class if the preferred class is not
    configured, rather than crashing spin on a thin CTA set — but a
    far-distance topic never falls back past "content"."""
    preference_by_distance = {
        "near": ("direct", "product-adjacent", "content"),
        "adjacent": ("product-adjacent", "content"),
        "far": ("content",),
    }
    for cta_class in preference_by_distance[distance]:
        cta = _cta_by_class(cta_set, cta_class)
        if cta is not None:
            return cta
    # No CTA of any allowed class is configured at all: content-CTA
    # availability is meant to be independent of F-E (§6.9), so this branch
    # only fires if F-E is resolved-empty; degrade to a safe, explicit
    # no-CTA marker rather than inventing one.
    return CtaOption(id="none", cta_class="none", en="(no CTA available — F-E empty)")


def spin_for_scorecard(
    scorecard: Scorecard,
    facts: BrandFacts,
    *,
    mapping_distance_bands: MappingDistanceBands,
) -> SpinResult:
    topic_terms = _tokens(scorecard.representative_title) | {t.lower() for t in scorecard.matched_terms}
    pain = detect_pain(scorecard.matched_terms, representative_title=scorecard.representative_title)
    icp, icp_score = best_icp(topic_terms, facts.icp)
    offer = best_offer(topic_terms, facts)
    distance = mapping_distance_for(offer.score, mapping_distance_bands)
    value_only = distance == "far"
    offer_id = None if value_only else offer.capability_id
    offer_text = None if value_only else offer.capability_text
    cta = choose_cta(distance, facts.cta_set)

    offer_label = f"{offer_text} ({distance})" if offer_text else f"none — value-only ({distance})"
    rationale_line = (
        f"Topic: {scorecard.representative_title} · ICP: {icp.en} · Pain: {pain} · "
        f"Offer: {offer_label} · CTA: {cta.cta_class} · Band: {scorecard.band}"
    )

    return SpinResult(
        cluster_key=scorecard.cluster_key,
        topic=scorecard.representative_title,
        language=scorecard.language,
        icp_id=icp.id,
        icp_text=icp.en,
        pain=pain,
        offer_id=offer_id,
        offer_text=offer_text,
        mapping_distance=distance,
        mapping_score=offer.score,
        cta_id=cta.id,
        cta_class=cta.cta_class,
        cta_text=cta.en,
        band=scorecard.band,
        value_only=value_only,
        rationale_line=rationale_line,
    )


# ---------------------------------------------------------------------------
# W8-10 Phase 5 — ``generation.post_mix``: a cross-topic post-type allocator,
# deterministic, no LLM (same posture as the rest of this module). Runs
# AFTER every candidate has already been spun (``stages.stage_spin`` calls it
# right after the spin loop, before ``spin_results`` is persisted/stored).
# ---------------------------------------------------------------------------


def allocate_post_types(results: list[SpinResult], mix: PostMixConfig) -> list[SpinResult]:
    """Assign ``post_type`` across ``results`` honouring ``mix``'s counts, in
    a fixed priority order: value_only slots first, then playbook, then
    promotional (promotional is never the first assignment this function
    makes when any value_only/playbook slot is configured).

    ``mix`` all-zero (the default) is a total no-op: ``results`` is returned
    completely unchanged, in its original order — every asset keeps today's
    fully distance-derived ``post_type``/``value_only`` behaviour.

    When ``results`` has more entries than ``mix`` has slots for, the extra
    entries are appended, in their original relative order, with their
    already-computed ``post_type`` left untouched (today's distance-derived
    behaviour) — never dropped, never forced into one of the three classes.

    A ``value_only`` slot additionally overrides the assigned result to the
    no-brand shape the marketer/copywriter audits called for: ``offer``
    nulled, ``cta_class="none"``, ``cta_text=""`` — there was previously no
    no-brand path at all (``mapping_distance=="far"`` still injected a
    brand CTA + offer text)."""
    if mix.value_only <= 0 and mix.playbook <= 0 and mix.promotional <= 0:
        return list(results)

    remaining = list(results)
    allocated: list[SpinResult] = []

    def _take(count: int, post_type: str) -> None:
        for _ in range(count):
            if not remaining:
                return
            sr = remaining.pop(0)
            if post_type == "value_only":
                sr = replace(
                    sr, post_type=post_type, value_only=True,
                    offer_id=None, offer_text=None, cta_class="none", cta_text="",
                )
            else:
                sr = replace(sr, post_type=post_type)
            allocated.append(sr)

    _take(mix.value_only, "value_only")
    _take(mix.playbook, "playbook")
    _take(mix.promotional, "promotional")

    # Extras beyond the configured mix: today's distance-derived behaviour,
    # appended after every allocated slot, original relative order kept.
    allocated.extend(remaining)
    return allocated
