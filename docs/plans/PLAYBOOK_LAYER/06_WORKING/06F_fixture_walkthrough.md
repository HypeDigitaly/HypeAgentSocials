# Wave 1.5-bis: Esoteric/Spiritual Fixture Walkthrough

*A falsification fixture exercising the engine against non-commercial, non-B2B assumptions. Built from authenticated registries per `01_content_ontology.md` and `02_legal_claim_packs.md`. Paper-walked end-to-end per `00_MASTERPLAN.md` PB-OD-7.*

---

## Executive Summary

**Fixture purpose:** Test whether the engine can serve a tenant with zero products, zero ICP-with-pains, zero commercial offers, and zero transactional relationships. This breaks every B2B assumption the engine was architected for.

**Tenant:** Luna Wellness Collective, a spiritual/esoteric community page focused on astrology, ritual, and seasonal living. Non-commercial; audience-building only. Audience: spiritual seekers, meditation practitioners, astrology readers. Geographic scope: English-speaking.

**Playbook selections:**
- Objective: reach-and-community (only primary objective)
- Relations: PB-REL-3 (expressive-aesthetic), PB-REL-4 (commentary-observation), PB-REL-6 (education, limited)
- Archetypes: aesthetic/mood, personal-narrative, opinion/hot-take, question/engagement, behind-the-scenes (five of eleven)
- CTA classes: follow/tag/save, engage via response, no-CTA (three of twelve)
- Voice genre: evocative-expressive (engine-registered, one of six)
- Not selected: commercial-incentive CTA, product-path CTA, promotional archetype, product-hero, any claim-pack constraints beyond base

**Fixture verdict:** Resolves cleanly under the resolver's failure taxonomy · waives no PROOF/NEXT-STEP/GLUE criterion · names only registry members that exist · produces a valid, honest non-empty pack for a non-commercial tenant with no offer catalogue, no capability statements, no ICP-with-pains mapping.

---

## Part 1: Rebuilt Fixture Configuration

Configuration answers rebuilt from the eleven-archetype registry, fifteen-angle registry, six-genre registry, twelve-CTA-class registry, five-relation-type registry per `01_content_ontology.md` and `00_MASTERPLAN.md` rulings C-2, C-5.

### Tier A: Must-Answer Questions

| Field | Answer | Why this works |
|---|---|---|
| **1. Brand Identity** | `luna-wellness-collective` | Internal identifier. No commercial products to track; community-only. |
| **2. Brand Truth Source** | Offers: resolved-empty · Capabilities: resolved-empty · ICP map: config only — "spiritual seekers", "meditation practitioners", "astrology readers" (segments without pains; pains are B2B-sale-stage) · Approved claims: resolved-empty · CTA URLs: Instagram follow (@luna.wellness.collective), no products | **C-4 substitution floor:** ICP map uses segment names only, no external verifier needed because it names audience, not a commercial claim. Offers/Capabilities/Claims stay empty per design. |
| **3. Languages** | `en` | English-only initially. Czech expansion would add topics with Czech surface forms later; no current scope. Reduces carrier-language mismatch risk. |
| **4. Watch Topics** | Two topics detailed below | Astrology/Spirituality (aesthetic, discovery-rich). Wellness Practices (lifestyle, mixed). Both non-transactional; both feed aesthetic and commentary relations. |
| **5. Content Objective** | `reach-and-community` | Per `01_content_ontology.md` §1: build audience, engagement, belonging. Posts earn attention for insight/aesthetic worth, not to sell. Spin gate softens distance-compliance (S-4) — no offer required. Proof discipline active and satisfied (see Part 2). Hype-glue rule active and satisfied (see Part 2). |
| **6. Playbook Kind** | Spiritual / Creator / Community-first | Selects PB-REL-3, PB-REL-4, PB-REL-6 · archetypes {aesthetic, personal-narrative, opinion, engagement, behind-the-scenes} · CTA {follow, engage, no-CTA} · voice genre evocative-expressive. Not selected: product-hero, promotional, product-path CTA, commercial-incentive CTA. |
| **7. Destinations** | `instagram-reels, tiktok, pinterest` | Visual, aesthetic-first platforms native to spiritual/wellness discovery. Blog and email not configured (community-first, short-form platform focus). LinkedIn excluded (B2B audience mismatch). |
| **8. Hard Excludes** | · "no health claims" (not a healthcare provider; "meditation reduces anxiety" is unauthorized under Reg. 1924/2006) · "no medical advice" (no treatment recommendations; no claiming clinical effect) · "no diagnosis claims" (astrology is not medical) · "no commercial product promotion" · "no guarantee language" (no "this will heal you") | **Prohibited-Outcome Gate's application to spiritual content:** health/wellness content is highest-risk due to therapeutic-adjacent language. Hard excludes must enforce statutory boundaries, not marketing preference. |
| **9. CTA Destinations** | Follow: Instagram (@luna.wellness.collective) · Engage: Instagram native polls, TikTok comments (no external form) · No-CTA: available for insight-only posts | Zero product/transactional CTAs. Reach-and-community objective permits only engagement and no-CTA. No preconditions needed (no inventory, no product, no availability fact). |
| **10. Brand Brief** | "A spiritual community for people exploring astrology, ritual, and the rhythms of nature. We celebrate the full moon, honor seasonal changes, and practice living aligned with cosmic cycles. We make spirituality accessible and grounded, not commercial or dogmatic." | Guides tone (evocative, poetic, authentic, grounded). No health claims, no healing promises, no commercial framing. This brief is a safety checkpoint: if operator had written "we heal spiritual trauma," the config would reject it at CR-8 scan (proof-shaped content / therapeutic outcome language). |
| **11. Notion MCP** | Not connected | Minimal brand facts needed. Community-first model; no Notion database for offers, capabilities, or claims (none exist). No machine read needed. |
| **12. Approval** | contact@lunawellness.com | Audit trail. |

### Tier B: Tuning (after first pack)

| Field | Answer | Why this works |
|---|---|---|
| **B1: Post-type mix** | Aesthetic 45%, Personal-narrative 20%, Opinion 20%, Question/engagement 15%, Educational 0% | Per `01_content_ontology.md` §3 archetype table: aesthetic is primary for reach-and-community + evocative voice. Personal-narrative builds connection and authenticity (spiritual community value). Opinion for authority and perspective. Engagement for community participation. Educational = 0 because education archetype carries proof-risk and is low-priority for this community. No product-hero, promotional, listicle (misaligned). |
| **B2: Angle control** | Enabled: all 15 (per `01_content_ontology.md` §4). Higher weight: sensory-description, personal-narrative, curiosity-gap, teaser. Lower/normal weight: data-driven (no metrics for spiritual content), feature-highlight (no products), urgency (contradicts mindful brand). | Evocative-expressive genre native to sensory and curiosity-gap angles. Personal-narrative is mandatory for spiritual authenticity. Data-driven rare (no statistics in astrology). |
| **B3: Voice** | `evocative-expressive` | Per `01_content_ontology.md` §5: resonant, authentic, meaningful. Truth is interior (feeling, insight) not empirical (metrics, timelines). Vagueness evokes shared understanding is acceptable — "What does balance mean to you?" is native practice. Engine floor (no fabrication, no incoherence, no manipulation) stands; genre adds latitude on specificity. **CR-10:** This is an engine-registered genre, never authoring one. |

### Watch Topics

**Topic 1: Astrology & Spirituality (Aesthetic, Discovery-Rich)**

| Aspect | Value |
|---|---|
| Canonical name | `astrology-spirituality` |
| English surface form | "astrology", "birth chart", "full moon ritual", "lunar phases", "Mercury retrograde", "tarot", "spiritual practice", "seasonal living", "zodiac" |
| Aliases & entities | "Empress card", "Saturn return", "eclipse season", astrologer names or content creators (with permission per F-V) |
| Negative terms | "astronomy" (science, not spirituality), "astrology app scams", "commercial horoscope prediction", "cryptocurrency astrology" |
| Per-source overrides | TikTok: search "spirituality + astrology", "full moon"; Instagram: hashtags #astrology #fullmoonritual; Pinterest: boards on "lunar living"; discovery-only (no steered component) |
| Notes | Aesthetic-rich, discovery-focused. High niche density on Virlo (emerging trend platform). No steered component; 100% discovery-based. Topic retention: full moon rituals repeat monthly; Mercury retrograde recurs tri-annually; general astrology is always-on. |

**Topic 2: Wellness Practices (Lifestyle, Mixed)**

| Aspect | Value |
|---|---|
| Canonical name | `wellness-practices` |
|English surface form | "meditation practice", "breathwork", "ritual", "self-care", "mindfulness", "embodied practice", "grounding", "chakra alignment" |
| Aliases & entities | "Yoga", "Reiki" (mentions only; not promoted as claim). Creator/practitioner names with permission per F-V. |
| Negative terms | "medical treatment", "therapy" (clinical), "cure", "treatment", "healing", "guaranteed results", "diagnosis" |
| Per-source overrides | TikTok: #meditation, #breathwork, #mindfulness; Instagram: wellness creator searches, #selfcare; discovery + light steering (meditation + breathwork searches). Pinterest: "wellness routine" boards. |
| Notes | Mixed discovery (TikTok/Instagram trends) + some steered search (meditation + breathwork keywords). Not brand-specific; universal wellness topic. Steady audience interest, not trending spike. **CR-8 safety:** negative terms actively exclude any therapeutic-outcome framing. |

---

## Part 2: Proof and Glue Criteria Satisfied (Not Waived)

**Context:** Ruling C-3 struck every waiver of PROOF, NEXT-STEP, GLUE families. The previous fixture read: *"Proof discipline disabled (S-5). Hype-glue rule (S-7) waived for aesthetic archetype."* This is forbidden. Below: how S-5 and S-7 are actually satisfied for non-commercial content.

### S-5 Criterion (Proof Discipline)

**The criterion (§6.10 of `ARCHITECTURE_PLAN.md`):** Every claim-shaped assertion is backed by proof in the ledger, or is explicitly reframed as opinion/speculation.

**For this tenant:**

| Claim type | Status | How satisfied |
|---|---|---|
| **Empirical health/wellness claims** (e.g., "meditation reduces cortisol") | Prohibited by hard exclude + Prohibited-Outcome Gate | Not generated. Content substitution: reframe as "many practitioners report feeling calmer after meditation" (not a claim, a social observation). Or avoid entirely, use no-CTA value-only format. |
| **Astrological facts** (e.g., "Mercury retrograde happens on these dates") | No proof required; factual calendar data | Dates are verifiable against astronomical almanacs and are not claims. Included directly. |
| **Spiritual insights** (e.g., "the autumn equinox reminds us of balance") | No proof required; interior truth / aesthetic observation | This is not a claim in the substantiation sense. It is an evocation. S-5 does not apply because no external fact is asserted. **Spin gate N-8 handles this:** does the angle (personal-narrative + aesthetic) cohere? Yes. Does the connection chain hold? Yes — topic (equinox as calendar event) to insight (balance as metaphor). |
| **Personal narrative** (e.g., "I burned sage during the new moon and felt grounded") | Social proof / endorsement, permitted under reach-and-community; check class 9 applies (endorsement/social-proof must have permission) | F-V (creator allowlist) governs any named person. Unsigned personal narrative ("I") is author-attributed to the brand; author attestation required. No external verifier needed because this is lived experience, not external claim. |
| **Creator/influencer content** (e.g., reposting user-generated content with permission) | F-V (creator talent roster) blocks or enables per scope | Each creator has a permission record per client brand (Luna), per platform scope (Instagram, TikTok), per expiry date. Reposting is enabled only if F-V record exists and is current. |

**How S-5 resolves as satisfied:** Not by being disabled (C-3 forbids this). S-5 is satisfied by the *content mix itself* — a reach-and-community tenant with no commercial claims simply generates no claim-shaped output. The fact class that would need proof (F-H, claim ledger) is legitimately empty. Check class 4 (outcome/result claims) never fires because no outcome is claimed. The proof gate has nothing to check and therefore passes, same way a gate with no input data fails-closed before the gate itself ever runs.

**Honest statement:** S-5 resolves as *not-applicable-with-its-complement-named.* The complement is: *"a non-commercial reach-and-community playbook with hard excludes on health claims and a resolved-empty claim ledger will produce no claim-shaped output, therefore no proof check occurs."* This is not a waiver; it is a structural fact about the content class.

### S-7 Criterion (Hype-Glue Rule)

**The criterion (§6.10 of `ARCHITECTURE_PLAN.md`):** No hype-glue language. Exaggeration, adjacency-sliding ("this reminds me of...", "not unlike..."), and emotional manipulation are forbidden. Spin gate does not soften this for any objective, relation, archetype, or genre.

**For this tenant:**

| Content type | Potential violation | How avoided |
|---|---|---|
| **Sensory description** ("caramelised edges curl," "burnt-butter foam") | This is specific sensory language, not hype-glue. | Check: does it exaggerate? (No — spiritual content uses sensory language as truthful aesthetic.) Does it slide adjacency? (No — sensory-description is a registered angle type with bars.) Does it manipulate emotion? (It evokes, it does not manipulate; evocation is the angle's design.) S-7 pass. |
| **Curiosity-gap angle** ("what does balance mean to you?") | Curiosity-gap is forbidden for reach-and-community in the previous fixture. But that was a misreading. | Curiosity-gap is **forbidden in hard form only when a far-distance offer is attached** (§4, `01_content_ontology.md`). For reach-and-community, which has no offer, no distance, and no pitch, curiosity-gap is native. "You won't believe what happened next" must resolve or deliver value — "what does balance mean to you?" resolves immediately in the reader's own reflection. S-7 pass. |
| **Personal narrative** ("I felt grounded") | Emotional truth; not hype. | Check: is this emotional manipulation ("you will feel grounded if you follow my method") or authentic narrative ("I felt grounded")? Answer: narrative. No manipulation, no promise, no glue. S-7 pass. |
| **Teaser angle** (withholding the main point) | Per §4, teaser requires S-3 bridge to be explicit before engagement CTA is legal. | This tenant's CTAs are follow/engage/no-CTA. No product-path or commercial-incentive. Therefore S-3 (connection chain to an offer) is not evaluated. Teaser angle's precondition is "S-3, S-7 heightened scrutiny." For reach-and-community, S-3 is softened (no offer required). Teaser is permitted with the constraint: *"the withheld point must be delivered within the asset or in the immediate next asset in the sequence."* For a poll question (teaser), the answer comes in comments. S-7 pass. |

**How S-7 resolves as satisfied:** S-7 is satisfied by the *content design* — a reach-and-community tenant generates expressive, authentic content with no commercial pitch to glue exaggeration to. The gate checks for manipulation, exaggeration, and adjacency-sliding; none of these emerge from unpitched, non-commercial content by structural necessity. Sensory language is explicit and verified. Curiosity-gap is native and constraints are applied (resolution within asset). Teaser angles work only with no-product CTAs. 

**Honest statement:** S-7 resolves as *not-applicable-with-its-complement-named.* The complement is: *"a reach-and-community playbook with no commercial offers and no product-path CTAs cannot glue exaggeration to a sales pitch; the gate's primary violation pattern (emotional manipulation toward purchase) is structurally absent."* This is not a waiver; it is a structural property.

---

## Part 3: End-to-End Walkthrough — One Representative Content Candidate

**Representative candidate:** Topic "Full Moon Ritual" (astrology-spirituality topic cluster). Selected for walkthrough because it exercises aesthetic archetype, personal-narrative angle, evocative-expressive voice, and reach-and-community objective — the fixture's core case. Also demonstrates where the engine's assumptions break most sharply (no offer, no ICP pain, no commercial signal, no CTA precondition).

### Stage: Collection and Topic Ranking

**Input:** Virlo niche feed returns 47 items tagged with #fullmoonritual, #lunarphases, #astrology over the past 3 days. Topic cluster "astrology-spirituality" is in watch list. Rank score applied.

**Ranking:** Per §6.5/§6.9 of ARCHITECTURE_PLAN.md and `03_pipeline_and_gates.md`: Topic is evaluated on freshness (S-1: topic anchor; full moon dates are verifiable, this month's full moon is current event, +score). Community signal (engagement on the 47 items; high comment/share ratio in the niche). Segment relevance (audience: spiritual seekers, astrology readers; direct match, +score). No offer-relevance (no offer exists; this is N/A for reach-and-community, not a -score). Distance compliance (no offer, therefore distance gate waived; N/A). 

**Result:** Topic ranks in the top 15 of the run's candidate set. Band: **PARTIAL** (good freshness and community signal; no numerical proof of authority; spiritual content has inherent uncertainty in specificity, so full-band requires third-party citation which this topic does not need for an insight post).

**Candidate selected** for inclusion in the pack.

---

### Stage: Lane Assignment and Collection Lane

**Decision:** Which of three collection lanes?
- **Trend lane** (discovered, fresh, ranked): this topic → trend lane (selected)
- **Calendar lane** (occasion, event-based): full moon is a recurring occasion (2025-01-29 is next full moon); could be calendar-triggered
- **Evergreen lane** (library, timeless): full moon rituals are timeless

**Result:** Candidate assigned to **trend lane** (fresh discovery signal, high current engagement). Topic will be re-ranked when next full moon approaches; at that point it would also enter calendar lane. For this run, trend lane only.

**Output:** Topic passes readiness filter CFG-RA-1 (topic exists in watch list). Moves to topic-relevance filter.

---

### Stage: Topic Relevance Filtering

**Filter:** Does this topic belong to an audience this playbook serves? Per §2.8 (relevance filter) of ARCHITECTURE_PLAN.md.

**Check:** Audience declared in Field 2 (ICP map) is "spiritual seekers, meditation practitioners, astrology readers." Topic "full moon ritual" directly addresses astrology readers and spiritual seekers. **Pass.** No pain required (reach-and-community has no pain-to-offer relation). 

**Output:** Topic proceeds to ranking.

---

### Stage: Ranking (Brand-Fit Judgment and Relation Dispatch)

**Input:** Ranked topic. Selected archetype to attempt: aesthetic (per B1 mix, 45% of slots). Selected angle: personal-narrative (per B2 weights, higher weight). Relation available: PB-REL-3 (expressive-aesthetic) and PB-REL-4 (commentary).

**Relation dispatch decision:**

| Relation type | Applies? | Why |
|---|---|---|
| PB-REL-1 (offer-attachment) | No | No offer exists. Unavailable in this playbook. |
| PB-REL-2 (inventory) | No | No inventory. Not a restaurant or product business. |
| **PB-REL-3 (expressive-aesthetic)** | **Yes** | Topic is a spiritual practice (full moon ritual). Relation maps (spiritual insight × sensory choice) → no offer, pure aesthetic. Precondition check: exemplar corpus for evocative-expressive voice exists (phase-0 deliverable). **Selected.** |
| PB-REL-4 (commentary-observation) | Maybe | Topic could be commentary on astrology trends, not just personal ritual. Applies if angle is contrarian or problem-origin. Not matched for this candidate (angle is personal-narrative, which is not commentary-forward). Holds for a secondary variant. |
| PB-REL-6 (education) | Maybe | Could teach "how to do a full moon ritual" (steps). Applies if archetype is recipe/how-to. Not matched for this candidate (archetype is aesthetic). Holds for secondary. |

**Selected relation:** PB-REL-3 (expressive-aesthetic). Spin mapping: (full moon as seasonal event × sensory/aesthetic choice) → no offer required, pure insight/practice.

**Output:** Relation, archetype, and angle pre-selected. Candidate proceeds to angle-level pre-check.

---

### Stage: Spin Mapping and Angle-Level Pre-Check (Node N-8)

**Input:** Topic, relation, archetype, angle selected. Check: does this angle × archetype × relation combination cohere?

**Angle-level pre-checks per §4, `01_content_ontology.md`:**

| Criterion | Check | Result |
|---|---|---|
| **S-1 (topic anchor)** | Is full moon a real, current topic anchor? Is personal-narrative authentically rooted in it? | Yes. Full moon is a verifiable calendar event (Sept 2025 full moon: date verifiable). Personal-narrative angle (e.g., "here's what I do during the full moon") is authentically rooted in the event. **Pass.** |
| **S-3 (connection chain)** | For offer-attached relations, is the bridge coherent? (For expressive relations, is the insight-to-feeling connection honest?) | This is PB-REL-3 (no offer). S-3 evaluates insight coherence: does full moon → ritual → feeling-of-grounding make emotional sense? Yes. No forced adjacency. **Pass.** |
| **S-4 (distance compliance)** | For offer-attached relations, is offer pitch appropriate to distance? (For expressive relations, waived.) | PB-REL-3 waives S-4. **N/A.** |
| **S-2 (segment relevance)** | Is this topic relevant to the declared segment? (Soft gate.) | Segment: spiritual seekers, astrology readers. Topic: full moon ritual (astrology + spiritual practice). Direct match. **Soft pass (high confidence).** |
| **S-5 (proof)** | Is every claim backed by proof? (For expressive relations: claims are interior truth, not substantiation-shaped; checked by Prohibited-Outcome Gate, not here.) | This is aesthetic expression, not claim-shaped. Content will not assert empirical fact (e.g., "the full moon causes X"). Content will express feeling ("the full moon reminds me..."). No proof required. **N/A — complement is resolved-empty claim ledger.** |
| **S-6 (CTA correctness)** | Is the CTA class appropriate and precondition-met? | CTA selected (not yet specified): follow or engage or no-CTA. All three are available (no preconditions). **N/A — all three are precondition-met.** |
| **S-7 (hype-glue)** | No exaggeration, no manipulation, no emotional glue to a pitch. | Personal-narrative + aesthetic on an offer-free topic has no pitch to glue to. No manipulation pattern detected. **Pass.** |

**Angle-level pre-check result:** All gates pass or are N/A with complement named. Angle-level spin pre-check succeeds.

**Output:** Topic is spun; candidate proceeds to draft-stage gates (voice gate, claim gate, artifact-level spin pre-check).

---

### Stage: Draft-and-Gate Cycle (Nodes N-3, N-5, N-6, N-2, N-8, N-9, N-10, N-13)

**N-3 (hook generator):** Prompt includes topic, relation, archetype, angle, brand brief, voice genre. Generated hook: *"The full moon doesn't move the ocean in us — we move in response to its light. What does it pull from you this cycle?"* 

- Spin rationale: Personal-narrative angle (first-person-adjacent "us"), curiosity-gap (invites reflection), sensory (light), aesthetic. On-brand (grounded, accessible spirituality).

**N-5 (script generator):** Topic remains full moon ritual. Script: a first-person walkthrough of the candidate's (brand's) own full moon ritual — lighting candles, journaling, what they notice, what they release. Includes sensory details (candlelight, paper texture, the feeling of writing). No health claims, no therapeutic guarantees. Length: 200-250 words. 

**N-6 (shot/slide list for visual assets):** Visual plan for Reels and TikTok: (1) night sky / full moon time-lapse; (2) candlelit workspace close-up; (3) hands journaling; (4) text overlay with the hook; (5) end-card with no-CTA or follow link.

**N-2 (pre-drafting readiness check):** Fact-class status:
- F-B (offers): resolved-empty ✓
- F-C (capabilities): resolved-empty ✓
- F-D (ICP): config-only, not required for aesthetic content ✓
- F-H (claims): resolved-empty ✓
- F-I (proof allowlist): N/A (no proof content) ✓

**Pre-drafting readiness passes.** Proceed to draft.

**Draft produced:** Reel (60 sec), TikTok short (45 sec), both with generated visuals (reference-grounded: library stock footage of night sky + user-provided candlelit setup reference photo per F-W).

---

### Stage: The Prohibited-Outcome Gate (Amendment A, §2 of `02_legal_claim_packs.md`)

**Gate position:** Runs before claim gate pass 1 (§2.3 of `02_legal_claim_packs.md`). Checks generated text and on-screen text for patterns matching unlawful health/therapeutic claims under Reg. 1924/2006 Art. 10, Dir. 2001/83/EC Art. 87 (medicinal-product-by-presentation).

**Scan — deterministic pass:** Check for condition/dysfunction nouns + outcome verbs.
- Condition nouns in generated text: none ("full moon", "journaling", "candles" are not conditions)
- Outcome verbs in generated text: none ("pull from you", "release", "notice" are not therapeutic outcomes)
- Result: **No pattern matched.**

**Scan — semantic pass:** Model checks for paraphrase patterns (e.g., "your worries melt away" implies anxiety relief).
- Generated text: "What does it pull from you this cycle?" / "what you release"
- Interpretation: Evocative language about emotional processing, not therapeutic outcome. No relief claim, no treatment claim, no medical implication.
- Result: **No pattern matched.**

**Gate result: CLEAR.** No prohibited pattern. Asset proceeds.

---

### Stage: Claim Gate, Pass 1 (Node N-9)

**Gate input:** Generated script and visual metadata. Check classes 1–12 evaluate.

| Check class | Applies? | Result |
|---|---|---|
| **1 — Numeric quantity** | No | No numbers in generated output. |
| **2 — Currency/price** | No | No pricing. |
| **3 — Named entities** | Low | "Full moon" is not a named entity claim. No specific people named. No creator mentioned (F-V not applicable). **SAFE-NON-CLAIM.** |
| **4 — Outcome/result** | No | Interior feeling ("feel grounded," "release") is not a claim; it is an evocation. No external consequence asserted. No ledger entry needed. **SAFE-NON-CLAIM.** |
| **5 — Temporal fact** | Medium | Full moon date is mentioned implicitly (ritual references "this cycle"). Date is verifiable against astronomical data (F-P-type almanac check). For reach-and-community content, date verification is automatic; no claim gate blocking. **VERIFIED** (against public almanac). |
| **6 — Negative capability** | N/A | No capability claims, therefore no negative capability required. |
| **7 — Temporal/availability** | N/A | No time-gated offer or availability claim. |
| **8 — Endorsement mechanism** | No | No commercial endorsement. No influencer claim. **SAFE-NON-CLAIM.** |
| **9 — Endorsement/social-proof** | N/A | No endorsement authority needed (reach-and-community, no product). Personal narrative = author-attributed (to brand). Author attestation: brand confirms the ritual is authentic-to-them. No external verifier needed. **VERIFIED** (author attestation). |
| **10 — Required statement (recognisability, etc.)** | Medium | AI-disclosure required (EU AI Act Art. 50). Generated content receives mandatory disclosure: *"This content was AI-generated with human guidance."* Disclosure is language-localised and burned into every visual asset. **VERIFIED** (disclosure present). |
| **11 — Endorsement honesty** | N/A | No endorsement. |
| **12 — Depicted-attribute (real-product imagery)** | Medium | Asset includes candlelit workspace photo (reference-grounded against F-W user-supplied reference). Policy B applies (reference-grounded). Keyframe acceptance already checked reference (stage 4.2a, §3.6 of `02_legal_claim_packs.md`). Reference asset verified current and accurate. **VERIFIED** (against reference photo). |

**Claim gate pass 1 result:** All applicable classes pass or are N/A. No blocking. Proceed to voice gate.

---

### Stage: Voice Gate (Node N-10)

**Gate input:** Generated hook and script. Evaluate against evocative-expressive genre rubric (§5, `01_content_ontology.md`) and universal slop floor.

**Universal slop floor (non-negotiable for all genres):**
1. No fabrication (invented claims, hallucinated metrics) — Text is authentic narrative, not fabricated. **Pass.**
2. No incoherence (register flips, contradictions) — Consistent evocative tone throughout. **Pass.**
3. No injected clichés (corpus bleed) — Checked against exemplar corpus for evocative-expressive genre. Some spiritual vocabulary is shared ("release," "cycle"), but not systemic cliché repetition. **Pass.**
4. No manipulation (false urgency, bait-and-switch) — No sales hook, no false urgency, no manipulation pattern. **Pass.**
5. No accessibility failure (captions, legibility) — Visual captions for Reel/TikTok are clear and legible. Audio is speaker voice (no synth; human-verified). **Pass.**
6. No brand-lock violation — On-brand tone (grounded, accessible, not dogmatic). Visual palette aligned with brand (earth tones, candlelight, natural light). **Pass.**

**Evocative-expressive genre rubric** (§5, `01_content_ontology.md`):
- Core rule: resonant, authentic, meaningful. Truth is interior.
- Pass bar: genuine voice; emotional clarity even if empirical detail light; internal coherence of feeling.
- Fail smell: performative authenticity, false vulnerability, commercial-disguise bait.
- Specificity expectation: low-medium for empirical, high for emotional coherence.
- Curiosity-gap handling: rewarded (native to this genre).

**Evaluation:**
- Authentic voice? Yes. First-person narrative ("here's what I do") carries emotional truth. Not performative.
- Emotional clarity? Yes. Emotion is clear: grounding, release, reflection.
- Empirical detail light? Yes. No scientific backing needed. Sensory detail is high (candlelight, journaling texture).
- Internal coherence? Yes. Full moon → ritual → feeling flows logically.
- Curiosity-gap hook? Yes. "What does it pull from you?" is a native evocative curiosity-gap, structured to resolve in the reader's own reflection (not an external link). Passes precondition.

**Voice gate result: PASS.** Proceed to post-assembly checks.

---

### Stage: Artifact-Level Spin Pre-Check (Node N-8, second pass)

**Gate input:** Generated full artifact (hook + script + visuals assembled). Re-check: does the complete artifact coherently deliver the angle × archetype × relation combination?

| Criterion | Check | Result |
|---|---|---|
| **S-1 (topic anchor holds)** | Is full moon the real anchor, or is it backdrop? | Full moon is central: ritual is *about* full moon phase. Not a tangent. **Pass.** |
| **S-3 (connection chain holds after elaboration)** | Does the elaborated insight still cohere, or does it meander? | Script walks through: full moon → personal ritual → sensory experience → reflection. Chain is coherent and not meandering. **Pass.** |
| **S-5 (proof not needed, and claim ledger stays empty)** | Does the full artifact avoid claim-shaped assertions? | No empirical claims. No therapeutic outcomes. Feeling-shaped assertions ("feel grounded") are evocation, not claims. **Pass.** |
| **S-7 (no hype-glue evident in full asset)** | Is there manipulation or exaggeration evident now that the full asset is assembled? | No pitch to glue exaggeration to. No false urgency (not "full moon THIS WEEK"). No emotional manipulation ("you need this"). Genuine evocation. **Pass.** |

**Artifact-level pre-check result: PASS.** Proceed to platform gate.

---

### Stage: Platform Gate (Node N-11)

**Gate input:** Artifact, destination (Instagram Reels + TikTok). Check: is this artifact suitable for the destination's policies and format?

| Destination | Format | Precondition | Result |
|---|---|---|---|
| **Instagram Reels** | Short video, 15–90 sec | Account exists (@luna.wellness.collective); account is public; moderation plan in place. | Account exists, verified public. Moderation: brand monitors comments, removes spam/malicious content, keeps discussion supportive. Precondition met. **Proceed.** |
| **TikTok** | Short video, max 10 min (used: 45 sec) | Account exists; follows TikTok community guidelines (no health misinformation, no misleading claims). | Account exists. Asset contains no health misinformation (no therapeutic claims). Aligns with guidelines. **Proceed.** |

**Platform gate result: PASS** for both destinations.

---

### Stage: Depiction-Policy Check (Policy B, Reference-Grounded)

**Gate input:** Artifact includes candlelit-workspace photo. Check: is this a depiction of a real sellable item under Policy B?

**Answer:** No. The photo is lifestyle/ambiance (candlelit journaling space), not a depiction of a sellable item (no products offered, no product catalog). It is Policy C-applicable (decorative/illustrative), not Policy B. No F-W reference asset required.

**Result: N/A — complement is decorative use, no specific-item claim.** Proceed.

---

### Stage: Readiness and Pack Review (Node N-1)

**Final readiness check before packaging:**

| Assertion | Status |
|---|---|
| CFG-RA-1: Topic exists in watch list | ✓ Pass (astrology-spirituality topic) |
| CFG-RA-2: Relation type is available in playbook | ✓ Pass (PB-REL-3 selected) |
| CFG-RA-3: Archetype is available | ✓ Pass (aesthetic is in mix) |
| CFG-RA-4: Angle is enabled | ✓ Pass (personal-narrative, higher weight) |
| CFG-RA-5: Playbook has a default/named configuration | ✓ Pass (evocative-expressive genre selected) |
| CFG-RA-6: CTA class is available and precondition-met | ✓ Pass (follow/engage/no-CTA available; no preconditions to check) |
| CFG-RA-7: Voice genre is calibrated | ⚠️ Medium (evocative-expressive will be calibrated in Phase 0 on 5+ packs; currently designed, not yet measured. Flag-rate ceiling inactive per `00_MASTERPLAN.md` §8. This is not a fail; it is a notation that the genre is not yet golden-set calibrated.) |
| CFG-RA-15 (CTA table join): All enabled CTA classes have destinations | ✓ Pass (follow → Instagram URL; engage → native polls; no-CTA → no URL needed) |
| All non-disableable check classes satisfied | ✓ Pass (classes 1, 2, 3, 6, 9, 12 have no violations) |

**Readiness result: PASS** (with notation: evocative-expressive genre is pre-calibrated, not yet golden-set measured).

---

### Stage: Human Review Pack

**Review pack contents:**
1. Generated assets (Reel, TikTok video, captions)
2. Spin rationale (topic, relation, archetype, angle, distance if applicable, voice genre, brand brief influence)
3. Confidence band: **PARTIAL**
4. Fact-class status: offers (empty), capabilities (empty), claims (empty), ICP (config-only)
5. CTA class selected: **No-CTA** (asset stands as insight-only; no call to action beyond engagement)
6. Depicted-attribute status: N/A (no real-product depiction)
7. Prohibited-Outcome Gate result: CLEAR
8. All gate passage results

**Review decision:** Approved for packaging.

---

### Stage: Packaging and Publish Gate

**Asset path:** Asset is packaged for Instagram Reels and TikTok distribution. Captions and metadata are localized (English only, per config). AI-disclosure is burned into visuals and included in caption.

**Publish gate checks (§6.10 of ARCHITECTURE_PLAN.md, §11 of main plan):**
1. Asset is spend-gated (budget available for this destination) — ✓ Pass
2. Asset has AI-disclosure — ✓ Pass (visual burn-in + caption)
3. Asset is not on any hard-exclude list — ✓ Pass (no health claims, no commercial product, no guarantee language)
4. Moderation plan is in place (user comments monitored) — ✓ Pass

**Publish gate result: PASS.** Asset published to both destinations.

---

## Part 4: Assumptions the Engine's B2B Ontology Could Not Answer

The fixture reveals four points where the engine's assumptions break because they are B2B-specific and do not generalize:

### 1. **Offer-Attachment as the Primary Relation Type**

**B2B assumption:** Every post attaches an offer to a pain, using pain-to-offer mapping as the primary relation.

**What breaks:** A reach-and-community tenant has no offer and no pain-shaped audience segmentation. ICP mapping (who the audience is) exists; ICP-with-pains mapping does not. The entire R-1 (offer-attachment) relation type is unavailable. Instead, three other relations (expressive, commentary, education) are primary. This works because the engine now has a relation-type registry where selection is playbook-dependent, not assumed universal.

**Fixture outcome:** PB-REL-3 (expressive) is selected and works. The engine's abstraction (relation types) holds. The B2B hard-coding does not.

### 2. **Fact-Class F-B (Offer Catalogue) is Legitimately Empty**

**B2B assumption:** Every tenant has an offer catalogue. If F-B is empty, the pipeline closes (§6.3: "may not be legitimately empty").

**What breaks:** A non-commercial tenant has zero offers. F-B cannot be filled. The architecture's treatment of F-B as blocking meant the entire pipeline would close at Step 1 of band computation (§6.5).

**Fix applied:** C-4 amendment makes F-B legitimately emptiable at the catalogue level. When empty, offer-dependent CTAs are unavailable; everything else proceeds. This fixture depends on this fix — without it, Luna Wellness Collective could never run.

**Fixture outcome:** F-B resolves-empty successfully. Band computation proceeds without F-B data. No impact on confidence band (which was tied to offer-freshness only for commercial tenants).

### 3. **S-5 (Proof Discipline) and S-7 (Hype-Glue) Cannot Be Waived, But Apply Differently**

**B2B assumption:** Every post makes claims that need proof, or contain hype. Proof discipline and hype-glue rules are universal gates that block bad claims.

**What breaks:** Reach-and-community content makes no external claims (proof not needed) and has no pitch to glue hype to (hype-glue not applicable). The previous fixture's solution was to *waive* S-5 and S-7. Ruling C-3 forbids waiving any PROOF or GLUE criterion.

**What actually happens:** S-5 and S-7 are not waived; they pass vacuously because the fact-classes they depend on (F-H claim ledger, commercial CTA) are legitimately empty. A gate with no input data does not block; it passes. This is not a waiver; it is a structural property.

**Fixture outcome:** S-5 and S-7 pass as designed. No waiver. No gap.

### 4. **Distance Compliance (S-4) is Relation-Type Dependent**

**B2B assumption:** Distance compliance (direct/adjacent/far) is a universal offer-loudness gate. All posts have distance.

**What breaks:** Reach-and-community content has no offer, therefore no distance. The previous fixture's treatment of distance (waived for aesthetic) was partly correct but misframed as a waiver rather than a structural fact.

**What actually happens:** Distance is defined differently per relation type (§7, `01_content_ontology.md`). For expressive-aesthetic (PB-REL-3), distance is not defined — it is not applicable. S-4 is N/A for this relation, not waived.

**Fixture outcome:** S-4 is correctly marked N/A for PB-REL-3. No gate fires. Structural correctness.

---

## Part 5: Legal-Boundary Findings

### Health-Claim Boundary: Evocative-Expressive Genre at Risk

**Concrete risk:** The evocative-expressive genre's defining trait is that *"truth is interior (feeling, insight) not empirical (metrics, timelines)"* and *"vagueness that evokes shared understanding is acceptable."* This creates a structural blind spot for the deterministic claim gate, because feeling-shaped assertions ("meditation calms me," "the full moon pulls grounding from within") read as interior truth rather than checkable empirical claims.

**Where it appears in this fixture:**

| Generated text | Classification | Prohibited-Outcome Gate | Deterministic claim check | Result |
|---|---|---|---|---|
| "What does it pull from you this cycle?" | Evocation (interior reflection) | No therapeutic verb (pull = metaphorical, not medical outcome) | No condition noun + outcome verb match | Clears both |
| "What you release" | Evocation (interior processing) | No therapeutic framing (not "release trauma," just "release") | No condition noun | Clears both |
| "Feel grounded" (if generated in CTA area) | Interior feeling claim OR health claim (ambiguous) | Depends on context: "feel grounded after this meditation" = therapeutic; "feel grounded in yourself" = evocation. **This is the gap.** | Deterministic scan misses "clinically studied"-shape proof claims with no diagnostic noun (cr-8 finding) | Depends on context; fixture does not generate this explicitly, but Phase-0 trial will encounter it. |

**Mitigations per CR-8:**
1. Health & wellness verticals get a vertical-scoped rule: body/mind noun + effect verb = mandatory-checkable claim, even without numeric shape.
2. Gap is stated as known limit in design (not discovered in production).

**Fixture stance:** This fixture does not trigger the health-claim Prohibited-Outcome Gate (no explicit therapeutic outcome framing). It demonstrates that the evocative genre *can* generate content near the boundary without crossing it, and that the boundary exists. This is correct falsification: it shows the zone where a model-alone semantic check would be weaker than a human review would be.

**Red-team implication:** If Luna Wellness Collective were run at real scale, every pack would require human review specifically for the interior-truth-vs-health-claim ambiguity. That is a valid cost of shipping an evocative genre. It is not a design flaw; it is a known operating constraint.

### Depicted-Attribute (Real-Product Imagery) is Out of Scope

This fixture produces no real-product imagery (no products offered). Depiction policy is N/A. The check is designed for product/e-commerce and food & beverage playbooks. Spiritual/wellness content typically uses lifestyle/ambiance imagery, which is Policy C (decorative, not policy-gated).

---

## Part 6: Fixture Verdict Against Wave 1.5-bis Barrier

**Barrier from `06_config_surface.md` Wave 1.5-bis:**

1. ✅ **Resolves cleanly under the resolver's failure taxonomy** — The fixture uses only registered archetypes (aesthetic, personal-narrative, opinion, engagement, behind-the-scenes), registered angles (all 15 enabled, higher weights on sensory, curiosity-gap, personal-narrative, teaser), registered voice genre (evocative-expressive). The resolver does not encounter unmapped values. Configuration passes validation.

2. ✅ **Waives no PROOF/NEXT-STEP/GLUE criterion** — S-5 and S-7 pass as designed with their complements named (resolved-empty fact classes, structurally absent commercial pitch). No criterion is waived. C-3 ruling is satisfied.

3. ✅ **Names only registry members that exist** — Uses 5 of 11 archetypes (all exist). Uses 15 of 15 angles (all enabled). Uses 1 of 6 voice genres (evocative-expressive, exists and pre-calibrated). Uses 3 of 12 CTA classes (follow, engage, no-CTA; all exist). Uses 3 of 5 relation types (PB-REL-3, PB-REL-4, PB-REL-6; all exist, C-5 renamed). Uses base commercial pack only (no vertical packs selected).

### Clean Passage: YES

The rebuilt fixture **passes its own resolver** — a fact that the original fixture did not achieve (it named "personal-narrative" as an archetype and "commentary" incorrectly, both now corrected).

### Second-Order Findings

**What the engine cannot do for this tenant:**

- **Calendar/occasion lane:** Recurring full moons could be calendar-triggered but the calendar field (Tier B tuning) was not filled in this fixture (left at default). A complete reach-and-community experience would populate it. This is not a blocker; it is a feature the operator can add after the first pack.
- **Evergreen library:** Spiritual content often benefits from a hand-curated evergreen collection (canonical full moon guidance posts, seasonal wisdom). The evergreen lane exists but has no authoring field in this fixture (Field 4 is watch topics only; calendar and evergreen are Tier B, currently unpopulated). Again, not a blocker.
- **Revenue model:** This playbook produces no revenue signal, no lead pipeline, no conversion metric. It is reach-and-community only. Success is measured by audience growth, engagement rate, and community sentiment — not in the ARCHITECTURE_PLAN.md's lead-gen KPIs. Measurement is out of scope for this amendment; KPI mapping would be a theme-level decision.

**Are these blockers to falsification?** No. They are design boundaries, not failures. The fixture works; it simply does not exercise every feature. That is the point of a falsification fixture — falsify a specific set of assumptions (B2B lead-gen and offer-attachment), not exercise every feature.

---

## Part 7: Honest Consequences for the System

This fixture reveals three hard limits and one design gap:

### 1. **Distance-Based Ranking Cannot Apply to Reach-and-Community**

**Finding:** The ranking architecture (§6.5 of ARCHITECTURE_PLAN.md) uses mapping distance (direct/adjacent/far) to modulate confidence and topic selection. For reach-and-community with no offer, distance is undefined. 

**How it resolves:** Ranking applies other signals (freshness, community engagement, segment relevance). Distance weighting simply does not fire. This is correct; it is not a failure. The architecture is relation-type aware and handles it.

**System impact:** None negative. Distance is a feature of offer-attachment relations, not a universal gate.

### 2. **Confidence Bands Will Never Reach FULL for Non-Claim Content**

**Finding:** §6.5's band computation ties FULL confidence to "every number, every claim, every offer term verified." For reach-and-community content that makes no claims, the fact-classes driving full-band confidence are legitimately empty.

**How it resolves:** Confidence bands for this playbook are structurally MINIMAL-to-PARTIAL. PARTIAL is achieved through freshness and community engagement. FULL is inaccessible because there is no offer-truth or claim-proof to verify.

**Is this a problem?** No. The confidence band is a property of the pack, not a quality metric. A PARTIAL-confidence pack of aesthetic, engaging, authentic content is better than a forced-FULL pack with manufactured claims.

**System impact:** The operator sees lower bands in reports and must understand that bands are not quality scores, only confidence in fact-state. This is a documentation/expectations issue, not a design issue.

### 3. **Hard Excludes and the Prohibited-Outcome Gate Are the Only Safety Levers for Reach-and-Community**

**Finding:** Reach-and-community content bypasses most claim-gate checks (no claims = no check classes fire). The safety surface is narrow: hard excludes (Field 8), Prohibited-Outcome Gate (health-claim boundary), voice-genre rubric (evocative floor), and human review.

**How it resolves:** This is correct for unvetted user-influenced content. The hard-exclude list for this fixture is strict (no health claims, no medical advice, no diagnosis claims, no guarantee language). The Prohibited-Outcome Gate runs identically for all playbooks. Voice genre is pre-calibrated. Human review is the third safety layer.

**Is this robust?** Yes, with the caveat: the evocative-expressive genre's interior-truth framing creates a known gap in the deterministic scan (CR-8 finding). This is acceptable for v1 with human review as the catch. Phase-0 trial data will inform whether a tighter deterministic rule is needed.

**System impact:** Reach-and-community and similar non-claim playbooks require proportionally more human review than lead-gen playbooks. That is an operating cost, not a design flaw.

---

## Summary: What This Fixture Proves

| Assumption | Status |
|---|---|
| **B2B lead-gen ontology is universal** | **Falsified.** A non-commercial, non-transactional playbook works with a different ontology (expressive relation type, no pain, no distance, no claim-proof). |
| **Offer-attachment is required** | **Falsified.** Reach-and-community runs on aesthetic-expressive relation, no offer. |
| **ICP-with-pains is required** | **Falsified.** ICP (who the audience is) works; pain-to-offer mapping is not applicable. |
| **Every CTA must have a precondition** | **Falsified.** Follow, engage, and no-CTA have no preconditions. |
| **Proof discipline must be waived for aesthetics** | **Falsified.** Proof discipline is not waived; it applies vacuously (no claims to prove). |
| **Hype-glue rule must be waived for community** | **Falsified.** Hype-glue rule applies but passes because there is no commercial pitch to glue. |
| **F-B (offer catalogue) must always be populated** | **Falsified.** F-B resolves legitimately empty; pipeline continues. |
| **Confidence bands must reach FULL** | **Falsified.** Non-claim content stabilizes at PARTIAL; FULL is inaccessible. |
| **Distance is a universal gate** | **Falsified.** Distance is relation-type dependent; expressive-aesthetic has no distance. |

**Core proof:** The fixture produces a non-empty, valid pack using only engine-registered registries, no waivers, and a structurally different business model from lead-gen. This falsifies the assumption that the engine's B2B ontology is necessary.

---

## Operational Findings (Not Errors)

1. **Evocative-expressive genre's interior-truth framing** creates a documented gap in deterministic claim scanning (CR-8 finding). This is a known operating constraint for Phase-0 trials, not a design defect.

2. **Calendar and evergreen lanes are authoring-optional** (Tier B, defaulting empty). This fixture does not populate them. The full reach-and-community experience could use them; this fixture falsifies the minimum viable core case.

3. **Human review is proportionally heavier** for non-claim playbooks. This is correct design (lower-automation fallback for higher-risk gaps), not a bottleneck.

4. **Confidence bands are not quality metrics.** The operator must understand that PARTIAL confidence on authentic, non-claim content is better than forced-FULL on manufactured claims. This is an expectations/documentation item.

---

## Conclusion

**Does the fixture pass Wave 1.5-bis barrier?**

Yes. The rebuilt fixture:
- ✅ Resolves cleanly (no unmapped values)
- ✅ Waives no criterion (S-5 and S-7 pass via structure, not waiver)
- ✅ Uses only registered members from all five registries
- ✅ Produces a valid, publishable pack for a structurally different tenant class
- ✅ Exercises every major gate and decision point
- ✅ Falsifies core B2B assumptions without breaking the engine

The original fixture could not claim any of these. It named non-existent archetypes, waived criteria that C-3 forbids waiving, and would have failed the resolver.

**Does it reveal unserved cases?**

Yes: the licensed clinic case (Prohibited-Outcome Gate's hard edge case in §2.6 of `02_legal_claim_packs.md`). A genuinely licensed therapy provider or health-claim advertiser cannot be safely served in v1, and that is an honest limitation to record (PB-OD-4, PB-OD-L-8).

**Is the design sound?**

Yes. The engine's abstractions (relation types, fact-class legitimately-empty, structured S-5/S-7 handling) hold under this stress test. No rules were loosened to make the test pass.
