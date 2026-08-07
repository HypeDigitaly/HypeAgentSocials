"""Tests for hypeagent.spin — deterministic spin mapping (§6.9)."""

from __future__ import annotations

from hypeagent import spin
from hypeagent.brand_truth import BrandFacts, Capability, CtaOption, IcpSegment
from hypeagent.config_load import MappingDistanceBands, PostMixConfig
from hypeagent.ranking import Scorecard
from hypeagent.spin import SpinResult


def _facts(**overrides):
    defaults = dict(
        identity={"legal_name": "Test Co"},
        capabilities_positive=[
            Capability(id="cap-chatbots", en="AI chatbots and assistants for businesses", note=None, source="x"),
            Capability(id="cap-automation", en="AI process automation and workflow integrations", note=None, source="x"),
        ],
        capabilities_negative=["No physical products"],
        icp=[
            IcpSegment(id="icp-sme", en="Small businesses wanting AI chatbots and automation", source="x"),
            IcpSegment(id="icp-public", en="Public-sector organizations deploying citizen chatbots", source="x"),
        ],
        cta_set=[
            CtaOption(id="cta-web", cta_class="content", en="Learn more at example.com"),
            CtaOption(id="cta-hypelead", cta_class="product-adjacent", en="See HypeLead"),
            CtaOption(id="cta-contact", cta_class="direct", en="Talk to us"),
        ],
        pricing_policy="prices-never-stated",
        pricing_rationale="test",
        hard_excludes_ref="config/hard_excludes.yaml",
        spin_notes={},
        source_path=None,
    )
    defaults.update(overrides)
    return BrandFacts(**defaults)


def _scorecard(title: str, matched_terms: list[str], band: str = "Medium") -> Scorecard:
    return Scorecard(
        cluster_key="ck1", language="en", representative_title=title, composite=0.5, band=band,
        sub_scores={}, rationale={}, sources=["hacker_news"], families=["developer_technical_discourse"],
        evidence_quality_label="", signal_class="rising", signal_age_hours=1.0, gate_status="pass",
        per_language_outcome="generate", per_language_outcome_rationale="", ranking_config_version=1,
        fit_method="test", dedupe_status="normal", what_changed="", demand_modifier_label="",
        matched_terms=matched_terms,
    )


BANDS = MappingDistanceBands(near_min=0.35, adjacent_min=0.12)


class TestDetectPain:
    def test_uses_matched_terms(self):
        assert spin.detect_pain(["chatbots", "automation"], representative_title="x") == "chatbots, automation"

    def test_falls_back_when_no_matched_terms(self):
        result = spin.detect_pain([], representative_title="Some topic")
        assert "unspecified pain" in result


class TestBestIcp:
    def test_picks_highest_overlap_segment(self):
        terms = {"chatbots", "businesses", "automation"}
        icp, score = spin.best_icp(terms, _facts().icp)
        assert icp.id == "icp-sme"
        assert score > 0


class TestBestOffer:
    def test_picks_highest_overlap_capability(self):
        terms = {"chatbots", "assistants", "businesses"}
        offer = spin.best_offer(terms, _facts())
        assert offer.capability_id == "cap-chatbots"
        assert offer.score > 0

    def test_no_capabilities_returns_no_offer(self):
        facts = _facts(capabilities_positive=[])
        offer = spin.best_offer({"chatbots"}, facts)
        assert offer.capability_id is None
        assert offer.score == 0.0


class TestMappingDistance:
    def test_near_far_adjacent_bands(self):
        assert spin.mapping_distance_for(0.5, BANDS) == "near"
        assert spin.mapping_distance_for(0.2, BANDS) == "adjacent"
        assert spin.mapping_distance_for(0.05, BANDS) == "far"


class TestChooseCta:
    def test_far_never_gets_direct_or_product_cta(self):
        cta = spin.choose_cta("far", _facts().cta_set)
        assert cta.cta_class == "content"

    def test_near_prefers_direct(self):
        cta = spin.choose_cta("near", _facts().cta_set)
        assert cta.cta_class == "direct"

    def test_adjacent_prefers_product_adjacent(self):
        cta = spin.choose_cta("adjacent", _facts().cta_set)
        assert cta.cta_class == "product-adjacent"


class TestSpinForScorecard:
    def test_direct_hit_produces_offer_and_direct_cta(self):
        sc = _scorecard("AI chatbots and assistants for small businesses", ["chatbots", "assistants", "businesses"])
        result = spin.spin_for_scorecard(sc, _facts(), mapping_distance_bands=BANDS)
        assert result.mapping_distance == "near"
        assert result.offer_id == "cap-chatbots"
        assert result.value_only is False
        assert result.cta_class == "direct"
        assert "Topic:" in result.rationale_line and "Band:" in result.rationale_line

    def test_far_distance_forces_value_only_variant(self):
        # No term overlap with any capability at all — a genuinely unrelated topic.
        sc = _scorecard("Quantum computing breakthroughs in cryptography research", [])
        result = spin.spin_for_scorecard(sc, _facts(), mapping_distance_bands=BANDS)
        assert result.mapping_distance == "far"
        assert result.value_only is True
        assert result.offer_id is None
        assert result.offer_text is None
        assert result.cta_class == "content"
        assert "value-only" in result.rationale_line

    def test_rationale_line_matches_the_12_1_shape(self):
        sc = _scorecard("AI process automation for small businesses", ["automation", "businesses"])
        result = spin.spin_for_scorecard(sc, _facts(), mapping_distance_bands=BANDS)
        for label in ("Topic:", "ICP:", "Pain:", "Offer:", "CTA:", "Band:"):
            assert label in result.rationale_line

    def test_defaults_to_promotional_post_type(self):
        sc = _scorecard("AI process automation for small businesses", ["automation", "businesses"])
        result = spin.spin_for_scorecard(sc, _facts(), mapping_distance_bands=BANDS)
        assert result.post_type == "promotional"
        assert result.to_yaml_dict()["post_type"] == "promotional"


def _spin_result(cluster_key: str, *, offer_text: str = "AI chatbots", value_only: bool = False) -> SpinResult:
    return SpinResult(
        cluster_key=cluster_key, topic=f"topic {cluster_key}", language="en", icp_id="icp-sme",
        icp_text="Small businesses", pain="pain",
        offer_id=None if value_only else "cap-x", offer_text=None if value_only else offer_text,
        mapping_distance="far" if value_only else "near", mapping_score=0.5, cta_id="cta-web",
        cta_class="content", cta_text="Learn more at example.com", band="Medium", value_only=value_only,
        rationale_line="Topic: x · ICP: y · Pain: z · Offer: a · CTA: content · Band: Medium",
    )


class TestAllocatePostTypes:
    def test_all_zero_mix_is_a_total_no_op(self):
        results = [_spin_result("ck1"), _spin_result("ck2")]
        out = spin.allocate_post_types(results, PostMixConfig())
        assert out == results
        assert [r.post_type for r in out] == ["promotional", "promotional"]

    def test_ordering_is_value_only_then_playbook_then_promotional(self):
        results = [_spin_result("ck1"), _spin_result("ck2"), _spin_result("ck3")]
        mix = PostMixConfig(value_only=1, playbook=1, promotional=1)
        out = spin.allocate_post_types(results, mix)
        assert [r.post_type for r in out] == ["value_only", "playbook", "promotional"]
        assert [r.cluster_key for r in out] == ["ck1", "ck2", "ck3"]

    def test_value_only_slot_nulls_offer_and_cta(self):
        results = [_spin_result("ck1", offer_text="AI chatbots")]
        out = spin.allocate_post_types(results, PostMixConfig(value_only=1))
        sr = out[0]
        assert sr.post_type == "value_only"
        assert sr.value_only is True
        assert sr.offer_id is None
        assert sr.offer_text is None
        assert sr.cta_class == "none"
        assert sr.cta_text == ""

    def test_playbook_and_promotional_slots_keep_their_offer_and_cta(self):
        results = [_spin_result("ck1")]
        out = spin.allocate_post_types(results, PostMixConfig(playbook=1))
        assert out[0].post_type == "playbook"
        assert out[0].offer_text == "AI chatbots"
        assert out[0].cta_class == "content"

    def test_extras_beyond_the_mix_keep_original_post_type_and_relative_order(self):
        results = [_spin_result("ck1"), _spin_result("ck2"), _spin_result("ck3")]
        out = spin.allocate_post_types(results, PostMixConfig(value_only=1))
        assert [r.cluster_key for r in out] == ["ck1", "ck2", "ck3"]
        assert out[0].post_type == "value_only"
        assert out[1].post_type == "promotional"
        assert out[2].post_type == "promotional"

    def test_more_mix_slots_than_results_never_raises(self):
        results = [_spin_result("ck1")]
        out = spin.allocate_post_types(results, PostMixConfig(value_only=5, playbook=5, promotional=5))
        assert len(out) == 1
        assert out[0].post_type == "value_only"
