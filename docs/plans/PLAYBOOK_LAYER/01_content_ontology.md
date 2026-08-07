# Playbook Layer: Content Ontology

*The reusable layer between engine and theme that generalises the hard-coded B2B demand-generation ontology to serve five distinct tenant archetypes without weakening the safety floor.*

**Canonical home for:** Content objective classes · relation type registry · post archetype registry · angle taxonomy · voice genre registry · CTA vocabulary registry · mapping-distance replacement · falsification walkthrough.

---

## §1. Content Objective Registry

**Purpose.** The existing architecture hard-codes one output goal: lead generation through offer attachment to pain. A playbook selects its business objective, which cascades into what the spin gate judges, what CTAs are legal, what measurement looks like, and what "a good post" means. No playbook may invent thresholds or remove safety gates. Content objectives select **from** a closed, engine-defined set.

**Five objectives, serving the five tenant archetypes:**

| Objective | Definition | What changes downstream | Example tenants |
|---|---|---|---|
| **Lead generation** | Convert reader attention on a problem into qualified prospect contact. Post exists to attach an offer to pain and move the reader toward a sales conversation. | Spin gate emphasizes connection chain (S-3) and distance compliance (S-4). CTA vocabulary centres on product-path, commercial-incentive. Ranking may weight lead-indicator signal. Proof claims encouraged. Band-gated on FULL for pricing claims. | B2B demand generation; product/e-commerce |
| **Direct commerce** | Convert reader into a buyer of a consumable good or service. Post exists to create purchase intent and supply a path to transaction. | Spin gate emphasizes offer presence and CTA correctness (S-6), deprioritises topic anchor (S-1). CTA vocabulary centres on order/purchase, reserve/book. Real-time inventory or availability facts are blocking-class. Stock status is live-verified before posting. | Restaurant; e-commerce product promotion |
| **Reach & community** | Build audience, engagement, and belonging. Post exists to earn attention for its own insight or aesthetic worth, not to sell anything. | Spin gate softens distance-compliance (S-4) — no offer required. CTA vocabulary limited to engagement, no-CTA. Proof discipline disabled (S-5). Hype-glue rule (S-7) waived. Ranking may weight community response. Value content is the canonical form. | Esoteric/spiritual page; creator/UGC commentary |
| **Brand awareness** | Establish presence and differentiate on personality or values. Post exists to be remembered. | Spin gate deprioritises connection chain (S-3), emphasises originality (S-1). Aesthetic and behind-the-scenes archetypes rewarded. CTA vocabulary: follow/tag/save. No proof required. Testimonials encouraged as social proof, not commercial proof. | Creator; esoteric/spiritual; hospitality lifestyle |
| **Retention & loyalty** | Deepen relationship with existing customer/subscriber base. Post exists to justify ongoing engagement or purchase. | Spin gate emphasises relevance-to-segment (S-2) and specificity (S-1). CTA vocabulary: none, or soft engagement. Audience not ICP but known customers. Pricing policy differs (may restate). Community context (tykání in Czech) often applies. | Restaurant; e-commerce; hospitality |

**What the selection controls:**

- **Spin criteria emphasis** — some criteria are universal (honesty, no hallucination); others are objective-dependent (connection chain matters for lead gen, irrelevant for reach).
- **Allowed CTA classes** — each objective permits a different set; commercial-incentive is only legal in lead-gen and direct-commerce; engagement is lead-gen forbidden.
- **Proof and claim policy** — lead-gen demands proof backing; reach-and-community disables proof checks; retention may restate terms differently than new-prospect acquisition.
- **Voice tone** — lead-gen is sober; reach-and-community embraces curiosity-gap and tease; direct commerce is urgent.
- **Measurement** — what the operator reviews: click-through for lead-gen, engagement for community, conversion for commerce, reach for awareness.

**Integration:** Each configured theme declares one primary objective in its spin block. If a theme serves multiple (rare, and contentious), it must declare the proportion and the reconciliation rule — never implicit mixing.

---

## §2. Content Relation Type Registry

**Purpose.** Today's pain-to-offer relation is a 2-D lookup: (ICP segment × pain) → offer. This does not generalise. A restaurant has no "pain" in the B2B sense; a spiritual page has no offer. A playbook declares which relation types it uses, so the spin mapper knows what to look up.

**Seven relation types, each mapping a different source to a target:**

| # | Relation | Maps | Example | Fact class requirements | What becomes unneeded | Combinable in one playbook? |
|---|---|---|---|---|---|
| **R-1** | Offer-attachment | (ICP × pain) → offer, CTA class, brand, domain | B2B tech topic "OAuth compliance" → HypeLead product | F-D (ICP map), F-B (offer catalogue), pain-to-offer relation, F-C (capability statements) | Availability fact, inventory | No — incompatible with R-2 |
| **R-2** | Inventory-or-availability announcement | (Product × time) → availability state, URL, urgency signal | Restaurant menu item → "fresh pasta available Thursdays" | F-B (product catalogue), real-time inventory or schedule | ICP map, pain detection, offer attachment | No — incompatible with R-1; yes with R-3 |
| **R-3** | Expressive-or-aesthetic | (Insight × sensory choice) → no offer | Spiritual page post: "the autumn equinox reminds us of balance" | F-D (segment identification), exemplar corpus | Offer attachment, proof claims, product CTA | Yes with R-2, R-4, R-5 |
| **R-4** | Commentary-or-observation | (Trend or news × angle) → perspective, no forced offer | UGC agency: "here's what's wrong with this creator's setup" | F-D (segment), exemplar corpus, opinion allowlist | Proof linking, lead CTA, capability claims | Yes with R-3, R-5 |
| **R-5** | Product-promotion | (Inventory × buyer-intent signal) → offer, product CTA, urgency | E-commerce: "Black Friday price ends midnight" | F-B (product), real-time availability, urgency fact | Pain-to-offer relation (direct inventory match), ICP | Yes with R-2, R-3 |
| **R-6** | Education-or-how-to | (Problem × solution steps) → resource, content CTA, no upsell | Restaurant: "how to judge wine pairing" | F-H (claim ledger), F-C (capability statements) | Offer attachment, product CTA | Yes with all others |
| **R-7** | Testimonial-or-proof | (Customer × outcome or experience) → social proof, soft CTA | Restaurant review; customer win story | F-I (proof allowlist), permission, outcome fact | Everything else; proof is the only payload | Yes with R-1, R-2, R-5 |

**Worked examples (one per tenant):**

1. **B2B lead generation (R-1):** Topic: "EU AI Act compliance deadlines"; ICP: compliance officers; pain: "new regulation"; offer: HypeLead audit service; CTA: product-path to trial. Spin gate S-3 checks connection honesty. Mapping distance controls loudness. Proof claims allowed at FULL band.

2. **Restaurant (R-2 + R-3):** Topic: "fresh seafood Thursday delivery"; relation: inventory announcement to "reserve now"; secondary relation: aesthetic post "the ocean in every bite" with no CTA. First post has availability precondition; second post disables proof check. Same brand, same audience, different content objectives and relations.

3. **Spiritual page (R-3 + R-4):** Topic: "full moon meditation"; relation: expressive insight with a recorded audio resource (R-6 hybrid); topic: "why astrology apps get birth charts wrong"; relation: commentary-observation without attachment. Neither requires proof. Both reward authenticity and visual/sensory richness over connection chain.

4. **Creator/UGC agency (R-4 + R-6):** Topic: "TikTok's new algorithm favours 15-second reels"; relation: commentary on creator-facing news; CTA: follow for updates. Secondary: "how to adapt your workflow to algorithm changes"; relation: education with resource CTA. No proof requirement. Audience is creators, not ICP segments.

5. **E-commerce (R-2 + R-5):** Topic: "winter jacket stock low"; relation: inventory announcement with product CTA and urgency. Fact class: real-time stock count (blocking). Voice is direct and urgent. Spin gate deprioritises topic anchor (S-1) — stock news is inherently stale — and emphasises CTA correctness and offer presence.

**Rules:**

- A single post uses one relation, never multiple.
- A playbook declares which relations it uses. Unused relations are never evaluated.
- R-1 and R-2 are mutually exclusive at the playbook level — a theme may use both for different topics, but one topic cannot be simultaneously a pain-triggered offer and an inventory announcement.
- R-3 (expressive) may combine with R-4 (commentary) or R-6 (education) on the same post only if the primary relation is clear — the topic's spin rationale names which is primary, and the gate chain treats it as such.
- A relation that requires a fact class makes that class blocking; absence blocks the topic, not the playbook.

---

## §3. Post Archetype Registry

**Purpose.** Today's system generates asset types (carousel, reel, short post) but not post *kinds* or *purposes*. An archetype is a named intent-and-form pattern: what the post *is*, why it exists, what *good* looks like, and what angle shapes fit it. A playbook declares which archetypes it uses; if not declared, all are available (the permissive default).

**Named archetypes, with usage across tenants:**

| Archetype | Purpose | Serves which objectives | Claim risk | Example angles | Visual / format fit | Typical length / pacing |
|---|---|---|---|---|---|---|
| **Educational** | Teach a skill, process or concept. Reader leaves knowing something they did not before. | Lead-gen (indirect), retention, brand-awareness | Low if source-cited; medium if novel claim | Step-by-step, "myth buster", "what really happens", how-to, explainer | Carousel / article / Shorts (paced for comprehension) | 3–5 min read or watch; slower pacing |
| **Promotional** | State offer, price, or availability. Reader is nudged toward purchase or signup. | Lead-gen (direct), direct commerce, retention | **High** — every number is a claim; requires live fact verification | "New feature launch", "limited time", "exclusive offer", discount angle | Short post / Reel / ad-style; urgency signals | 15–60 sec; fast cuts |
| **Behind-the-scenes** | Show the team, process, or culture. Reader gets insider access, feels connection. | Brand-awareness, retention, community | Low if authentic; medium if staged | "Day in the life", workspace tour, team story, "how we built this", outtakes | Video / photo series; intimate scale | 30 sec – 2 min; naturalistic pacing |
| **Proof / testimonial** | Feature customer win, case study, or endorsement. Reader sees social proof. | Lead-gen (indirect), brand-awareness, retention | **High if commercial** — every metric is a claim; needs proof allowlist entry | Customer story, "they chose us because…", metrics highlight, before/after | Long-form / carousel / video interview | 1–3 min; narrative arc |
| **Opinion / hot-take** | Assert a controversial or counter-intuitive view. Reader is provoked to think or engage. | Community, brand-awareness, lead-gen (thought leadership only) | **Medium–high** — opinion can shade into claim without warning; needs callout ("I think", "evidence suggests") | "Why X is overrated", "the real problem is", prediction, contrarian read | Short post / Reel; confrontational hook | 15–30 sec; sharp / punchy |
| **Aesthetic / mood** | Create atmosphere or visual interest with minimal text. Reader pauses, feels something. | Community, brand-awareness, retention | **Very low** — no claim by design | Colour palette, texture, mood, "this is how we see it", mood-board style | Image / Reel / carousel; visual-first | 3–15 sec; lingering |
| **Announcement** | Declare news, event, or change. Reader is informed and prompted to act. | All objectives except community | Medium — date/time/venue are facts; availability critical | Launch date, event registration, policy change, milestone | Short post + link / event card | 15–45 sec; clear logistics |
| **Listicle / rank** | Present ordered insights: "3 ways", "top 5 reasons", "ranking". Reader gets quick value. | Brand-awareness, community, thought leadership | **Medium** — each item carries potential claims; needs source cites | "3 ways to X", "mistakes to avoid", "ranking by Y", comparison table | Carousel / thread / article | 1–3 min; scannable format |
| **Question / engagement** | Ask the audience to respond. Reader participates. | Community, retention, brand-awareness | Low if genuine; medium if bait (obvious manipulation); **very high if quiz is product disguise** | "What's your X?", poll, "show us your", callback to prior post, advice request | Poll / comment-bait / video question | 15–30 sec; open-ended |
| **Recipe / craft / how-to** | Detailed walkthrough: a meal, project, process, or creation. Reader can replicate it. | Brand-awareness, retention, community | **Low per se; high on ingredient/technique claims** | Recipe steps, craft tutorial, workout routine, setup guide, "here's our process" | Video / carousel / reel (step-by-step); detailed pacing | 1–3 min; instructional |
| **Product-hero** | Star a single product. Establish desire, showcase features. Reader sees benefits. | Lead-gen (direct), direct commerce, brand-awareness | **Very high** — every feature claim needs capability backing; must be spinnable via R-1 or R-5 | Feature deep-dive, unboxing, demo, aesthetic appeal, comparison, "why this product", specs made sexy | Reel / short video / carousel; beauty shots | 30–90 sec; slick / aspirational |

**Mapping: archetype × objective.**

Not every archetype serves every objective well. The playbook declares which (archetype, objective) pairs it uses; unused pairs are never triggered. Default: all pairs available.

| | Lead-gen | Direct commerce | Reach & community | Brand awareness | Retention |
|---|---|---|---|---|---|
| Educational | Yes (thought leadership) | Yes (technique angle) | Yes | Yes | Yes |
| Promotional | **Yes (primary)** | **Yes (primary)** | No | No | Yes (reminder) |
| BTS | No | No (except "how we ship") | Yes | **Yes (primary)** | **Yes (primary)** | 
| Proof / testimonial | **Yes** | Yes | Yes (feel-good) | Yes | Yes (trust-building) |
| Opinion / hot-take | Yes (thought leadership) | No | **Yes (primary)** | **Yes** | No |
| Aesthetic / mood | No | No | **Yes (primary)** | **Yes** | **Yes (primary)** |
| Announcement | Yes (launch) | **Yes (sale/promo)** | Yes (milestone) | **Yes** | Yes (loyalty update) |
| Listicle / rank | **Yes** | Yes | **Yes** | Yes | Yes |
| Question / engagement | No | No | **Yes (primary)** | **Yes** | **Yes (primary)** |
| Recipe / craft | No | No (except food/drink) | **Yes (primary)** | **Yes** | **Yes** |
| Product-hero | **Yes (lead gen)** | **Yes (primary)** | No | **Yes** | Yes (upsell) |

**Mix ratio mechanics.**

An operator declares a content mix: "40% educational, 30% product-hero, 20% opinion, 10% aesthetic." The system tracks this per playbook across a rolling window. When generating a pack:

1. Ranked topics are distributed to archetype slots according to the declared ratio, starting with topics that have the highest confidence band.
2. Each topic is evaluated against the archetype's claim-risk profile. If a topic cannot safely deliver an archetype (e.g., a speculative trend cannot be educational without proof), it downgrades to the next-best fit for that topic, recorded in the pack.
3. If an archetype slot remains unfilled (ranked topics exhausted, or all candidates fail the archetype's safety bar), the slot is packaged as plan-only with a note: "no topic suitable for [archetype] this run; ranking produced X candidates, Y had insufficient proof."

**What does NOT happen:** thresholds are never relaxed to manufacture volume. A run with two educational and three product-hero topics against a 40/30/20/10 target ships that, not a forced fifth educational topic with a weakened proof gate.

**Angle shapes per archetype** — how the spin mapper selects or constrains angle generation.

Each archetype has stereotypical angle *shapes*. The angle taxonomy (§4 below) defines the named angle types; the archetype layer specifies which shapes *dominate* that archetype and which are rare:

- **Educational:** How-it-works, myth-bust, step-by-step, problem-origin dominate; uncommon: teaser, curiosity-gap.
- **Promotional:** Urgency, scarcity, discount, feature-highlight dominate; uncommon: storytelling, personal-narrative.
- **Behind-the-scenes:** Personal-narrative, process-transparency, team-story dominate; rare: data-driven.
- **Opinion:** Contrarian, analysis, prediction, personal-narrative dominate; forbidden: false-balance, false-concern.
- **Aesthetic:** Mood, sensory-description, visual-series dominate; forbidden: claim-heavy, urgency.
- **Recipe / how-to:** Step-by-step, problem-origin, sensory-description dominate; uncommon: data-driven.
- **Question / engagement:** Direct-question, callback, poll dominate; forbidden: rhetorical-bait, loaded-question.

These are soft weights on angle selection, not hard gates. An educational post *may* use a curiosity-gap angle, but the spin gate will apply **higher scrutiny to the connection-chain rule (S-3)** — the gap must lead somewhere legitimate, not evaporate.

---

## §4. Angle Taxonomy

**Purpose.** Today, angles emerge only from the pain-to-offer relation and the topic's freshness. No playbook can express "we want to see more contrarian takes" or "avoid teaser angles in educational content." The angle taxonomy names **angle types**, specifies how one is selected for a topic × archetype pair, and gates their use.

**Fifteen angle types:**

| Angle type | Definition | Good for which archetypes? | Spin gate emphasis | Frequency check | Preconditions |
|---|---|---|---|---|---|
| **How-it-works** | Explain the mechanism or process behind the topic. Assumes reader interest in *why*, not just *what*. | Educational, recipe, behind-the-scenes | S-1 (topic anchor), S-3 (connection chain) | Cross-pack recurrence: "similar mechanism posts" | Topic must describe a process or decision-point, not just an event |
| **Myth-bust** | Identify and correct a widespread misunderstanding. Contrasts false belief with truth. | Educational, opinion, product-hero | S-1, S-3, S-5 (proof required) | Recurrence check: myth title | Claim ledger must contain the **true** statement with evidence |
| **Step-by-step** | Procedural walkthrough: "do X, then Y, then Z." | Recipe, educational, behind-the-scenes | S-1, S-3 | Recurrence: procedure title | Topic must be actionable; instructional clarity required |
| **Problem-origin** | Reframe a topic as "the real source of this problem is X." Analytical. | Educational, opinion, commentary | S-1, S-3 | Recurrence: problem name | Requires either evidence or explicit callout ("I think", "evidence suggests") |
| **Contrarian** | Assert a position opposite to received wisdom. "Everybody says X; the truth is Y." | Opinion, thought-leadership, hot-take | S-1, S-3, S-7 (no hype-glue), S-5 (if claims) | Recurrence: the contrarian position itself | Precondition: the consensus position must be verifiable; the contrary position needs callout if speculative |
| **Prediction** | Project future state based on current signals. "If X continues, then Z." | Opinion, commentary, thought-leadership | S-1, S-3 | Recurrence: the prediction | Must be explicitly labelled as prediction, forecast, or "if this trend holds" — **never asserted as fact** |
| **Personal-narrative** | First-person story: what the author or team experienced. Reader connects emotionally. | Behind-the-scenes, opinion, testimonial, recipe | S-1, S-2 (segment relevance), S-3 | Recurrence: personal story archetype within 30 days | Must be authentic; playbook may require hand-verification for unattended runs |
| **Curiosity-gap** | Open a question or tease a resolution; reader must engage to learn. "You won't believe what happened next." | **Forbidden for reach-and-community objective**; rare in educational; common in opinion, awareness | S-3 (connection chain must hold), S-7 (no glue) | Recurrence: tease-style posts within 14 days | Must resolve or deliver value within the asset, not defer to external link |
| **Teaser** | Withhold the main point; reader must click/engage. Often paired with a CTA. | Opinion, announcement, engagement (engagement CTA only) | S-3, S-7 (no hype-glue) | Recurrence: teaser-style per destination within 7 days | Spin gate applies heightened scrutiny — S-3's bridge must be explicit before engagement CTA is legal |
| **Data-driven** | Lead with a stat, finding, or benchmark; interpret for the audience. | Educational, opinion, listicle, product-hero | S-1 (topic anchor is the data), S-5 (proof required — every number is a claim) | Recurrence: statistic or metric itself | Claim ledger must contain the exact number, source, date and usage scope |
| **Sensory-description** | Emphasise texture, taste, sound, emotion, visual richness. Show, don't tell. | Aesthetic, recipe, behind-the-scenes, brand-awareness | S-1 (topic anchor is the sensory choice), deprioritises S-3 | Recurrence: aesthetic / sensory voice within 21 days | No claim required; spin gate does not apply S-5 (proof) or strict S-7 (hype-glue is allowed in aesthetic) |
| **Feature-highlight** | Showcase a single capability, benefit or product feature. "This does X really well." | Product-hero, promotional, testimonial | S-1, S-3, S-5 (capability claim) | Recurrence: feature name within 14 days | Capability statement must exist in fact base; negative capability statement ("this does not do Y") must be observed if relevant |
| **Urgency** | Emphasize time-scarcity, deadline or window. "Do this before…" | Promotional, announcement, direct-commerce | S-1 (urgency is the hook), S-4 (distance compliance — offer must be direct), S-6 (CTA must be live) | Recurrence: urgency-hooked posts within 7 days | Fact: event, offer expiry, or deadline must be live-verified within the 24 hours before pack approval. No manufactured urgency (e.g., "offer ends midnight" when it actually runs for 2 weeks) |
| **Comparison** | Pit two approaches, tools, or perspectives against each other. | Educational, opinion, product-hero, listicle | S-1, S-5 (comparison claim requires evidence), S-3 | Recurrence: the comparison axis itself within 21 days | Fact class: either both comparands must be in the claim ledger with evidence, or the angle must be explicitly framed as opinion ("I prefer X because…") |
| **Milestone** | Celebrate a win, anniversary, or cumulative achievement. "We just hit 1M users." | Announcement, brand-awareness, retention, community | S-1 (milestone is the topic anchor), S-5 (if quantified) | Recurrence: milestone type (anniversary, user count, etc.) within 30 days | If quantified, exact number + date must be in fact base; if hand-curated, operator verification required for unattended runs |

**Angle selection for a topic × archetype pair.**

Input: a ranked topic, a selected archetype, and the detected pain (if R-1) or other relation source.

1. **Archetype dominance:** Filter angle types to those marked "dominant" or "good for" the archetype. (Optionally, include "uncommon" angles at lower weight.)
2. **Playbook restrictions:** Remove any angle types the playbook has disabled (e.g., curiosity-gap forbidden in reach-and-community playbook).
3. **Preconditions check:** For each remaining angle type, verify its preconditions against the brand-truth snapshot — e.g., for myth-bust, does the ledger have the true statement?
4. **Coherence:** Prefer angle types that have not been used for this topic cluster in the prior N packs (cross-pack recurrence, per the table's "frequency check" column). This prevents "we covered this three times already with the how-it-works angle."
5. **Selection:** Randomly select from the filtered set, or use a theme-configured weighting if available. Default: uniform.

**Angle-level spin pre-check (node N-8).**

Before the copy generator writes, the angle (topic + angle-type + archetype) is evaluated against the seven spin criteria **at the angle level** — checking that the pairing is coherent **before** word count and prose quality obscure whether the underlying idea was sound. 

Rules:
- **S-1 (real topic anchor):** Does this specific angle type depend on this specific topic's freshness? Myth-bust without a recent misconception event fails S-1. Urgency angle without a live deadline fails S-1.
- **S-3 (connection chain):** For offer-attached angles, is the bridge from topic to consequence to offer coherent? A contrarian angle on "AI replaces developers" attached to a recruitment offer fails S-3 unless the connection is explicit.
- **S-4 (distance compliance):** If far-distance, does the angle pass the "soft bridge" requirement? A testimonial angle on a far-distance topic is acceptable; an urgency angle on far distance is not (offers too loud for the distance).
- Other criteria (S-2, S-5, S-6, S-7) depend on the angle's content, not the angle type alone, and are checked post-drafting.

**Failure:** If the angle-level pre-check fails, the angle is marked unsuitable and the topic reverts to the next-best angle type, or to a plan-only variant, or is dropped with the reason recorded.

---

## §5. Voice Genre Registry

**Purpose.** The existing voice gate (§14.2–§14.4) is authored entirely for B2B sober thought leadership. It bans "curiosity-gap tease" and "vagueness dressed as insight" — both native registers of spiritual, food and community content. A playbook may not weaken the engine's universal slop floor; it selects from a registry of distinct genre rubrics that build *on* that floor.

**Universal slop floor (engine-level, non-negotiable):**

Owned by every genre rubric and never disabled:

1. **No fabrication.** Invented claims, false citations, hallucinated metrics, imaginary customer names.
2. **No incoherence.** Register flips (formal → casual mid-post), tense shifts, logical contradictions that befuddle readers.
3. **No injected clichés from the exemplar corpus.** Cross-pack recurrence monitor catches systemic house-tics.
4. **No manipulation.** Bait-and-switch hooks, false urgency without a real deadline, social proof without permission.
5. **No accessibility failure.** Captions unintelligible, on-screen text illegible, audio prosody incomprehensible. (Technical floor, language-neutral.)
6. **No brand-lock violation.** Visual elements off-palette; on-image text violates safe-box rules; phrasing contradicts the theme's declared voice rules.

**Six genre rubrics, built on the floor:**

| Genre | Applies to playbook with objective | Core rule | Pass bar | Fail smell | Specificity expectation | Curiosity-gap handling |
|---|---|---|---|---|---|---|
| **Analytical-B2B** | Lead-gen, direct commerce (thought leadership angle) | Sober, evidence-backed, falsifiable. The original §14.4 English rubric. | Claim backed by source or ledger entry; precise language; active voice. Hook is direct statement. | Vagueness dressed as insight; marketing rhetoric; hand-wavy numbers; borrowed urgency. | High — every claim is verifiable. | Forbidden — the tease must resolve or add value, never defer. |
| **Sensory-hospitality** | Direct commerce, retention, brand-awareness (recipe, BTS, aesthetic archetypes) | Visceral and specific. Emphasize texture, aroma, taste, visual richness, feeling. Authenticity prized; aspirational acceptable. | Specific sensory details (not "delicious", but "caramelised until the edges curl"); honest emotion ("we love this dish"); narrative coherence. | Vague adjectives; clichéd descriptions ("a culinary journey"); unsubstantiated health claims; falsified provenance. | Medium–high for sensory description; lower for narrative. | Allowed, and often rewarded — "you won't taste this in every city" is fine if true and specific. |
| **Evocative-expressive** | Reach & community, brand-awareness, retention (aesthetic, personal-narrative, question archetypes) | Resonant, authentic, meaningful. Truth is interior (feeling, insight, values) not empirical (metrics, timelines). Vagueness is acceptable if it evokes shared understanding. | Genuine voice; emotional clarity even if empirical detail is light; internal coherence of feeling; specific enough that readers recognise themselves. | Performative authenticity ("I'm so relatable"); false vulnerability; commercial-disguise engagement bait; wholesale borrowing of others' language. | Low–medium for empirical claims; high for emotional coherence. | Rewarded — curiosity-gap and tease angles are native to this genre. "What does balance mean to you?" is good practice. |
| **Creator-casual** | Reach & community, brand-awareness, retention (opinion, commentary, BTS, engagement archetypes) | Conversational, irreverent, insider language. Breaks the fourth wall. Calls out absurdity. | Direct audience address; in-group reference; dry humour or sharp observation; authentic reaction (not scripted); engagement assumption. | Forced casualness ("yo, fam"); false insider status; commentary that punches down; irony so dense it obscures meaning. | Medium — specificity is less important than tone and relatability. | Allowed — "you won't believe what happened" works if the payoff is real and surprising. |
| **Product-persuasive** | Direct commerce, lead-gen (promotional, product-hero, urgency, feature-highlight archetypes) | Confident, benefit-focused, outcome-oriented. Reader should want to own or use this. | Clear benefit statement; specific use-case anchor; confidence in the product; "you" framing (not "it does"); urgency signal if deadline is real. | Hype without substance; feature list without benefit; false scarcity; emotional manipulation without honest reason; mismatched register (too casual for a luxury good, too formal for accessible product). | High for benefits/outcomes (every "this improves X" needs backing); lower for emotional appeal. | Forbidden in hard form; soft tease acceptable if it leads to clear benefit ("This one trick will save your mornings" must deliver the trick within the asset). |
| **Educational-structured** | Lead-gen, retention, brand-awareness (educational, listicle, recipe, how-to archetypes) | Clear, methodical, teachable. Scaffolds complexity. | Structure is evident (steps are numbered, concepts build logically); specificity on the *how*, not just the *what*; pacing matches complexity; calls-to-action are "learn more" or "try this", not "buy now". | Oversimplification that misleads; buried lede (the useful bit is last); false authority ("everyone agrees"); recipe without units or temperatures; steps that don't build logically. | Very high — every instruction must be replicable; every claim must be sourced or tested. | Allowed for engagement ("What's your go-to technique?" or a teaser step-by-step); tease must not withhold essential safety information. |

**Czech-specific layer** (applied *on top of* the genre rubric):

Regardless of genre, Czech assets carry the five Czech-specific dimensions from §14.4 (calque avoidance, register consistency, code-switching, structural tells, sentence rhythm) plus the higher human-voice weighting. The eleven dimensions are:

- Five inherited from the selected genre's English counterpart, evaluated against Czech-calibrated bars.
- Five Czech-specific (calque, register, code-switching, tells, rhythm).
- One Czech override (human-voice weighting).

**How to use this layer:**

1. Playbook declares its primary objective and the primary genre rubric that matches it. Example: "lead-gen playbook uses analytical-B2B; reach-and-community playbook uses evocative-expressive plus creator-casual."
2. When an asset is drafted, it is judged against that genre rubric (layers 1–3 of the voice gate in §14.2).
3. If the playbook uses a secondary objective or archetype (rare), the operator may declare that the voice gate should apply a *different* genre rubric to that subset of assets — e.g., "our lead-gen playbook has a BTS content stream; BTS assets are judged against sensory-hospitality genre, not analytical-B2B."
4. Czech assets always inherit the selected genre's English bar plus the five Czech-specific dimensions, no exception.

**Falsification:** If a genre rubric permits something the engine floor forbids (e.g., evocative-expressive permits vagueness; but it does not permit *fabrication*), the engine floor wins — silently, without a second discussion. A rubric is never an override; it is a configuration of what the floor permits.

---

## §6. CTA Vocabulary Registry

**Purpose.** The existing system defines four CTA classes: content, product-path, event, commercial-incentive. This serves B2B lead-gen. Restaurant needs "reserve/book"; e-commerce needs "order/purchase"; creator needs "follow/save"; spiritual page may need "no-CTA". Each class has preconditions: e-g., event CTA requires an event fact to exist. A playbook declares which classes it uses; unused classes are never evaluated.

**Ten CTA classes, each with preconditions and objective pairing:**

| CTA class | Intended action | Preconditions | Allowed objectives | Preconditions details | Example |
|---|---|---|---|---|---|
| **Content** | Reader visits a resource: article, guide, masterclass, tool, webinar. | Resource URL resolves; destination matches language if language-coherent rule applies. | All | Resource must exist and be live. If the resource is inside the owned domain, it must exist before social posting (site-first hold, §6.9 of main plan). If external, URL is live-verified within 24h. | "Read our guide" → blog article; "Join the webinar" → calendar event landing |
| **Product-path** | Reader initiates product interaction: demo, trial signup, product page, account creation. | Offer status is live in the brand-truth snapshot; destination URL verified within freshness window; band at minimum PARTIAL (FULL if trial terms or pricing are stated). | Lead-gen, direct commerce, retention | Offer fact class must exist and be marked live in the knowledge base. CTA URL must resolve. If the product page does not exist in the asset's language, CTA degrades to content-class (language-coherence rule). Trial terms are only stated at FULL band. | "Start your free trial" → product signup; "See the demo" → demo video |
| **Order / purchase** | Reader buys a product or places an order. Real transaction intent. | Exact product exists with current price and availability; order system is live; inventory is real-time or hand-verified; for unattended runs, stock must be verified within 4h of approval. | Direct commerce, retention (upsell) | Product fact class and inventory are **blocking** — absence blocks the topic entirely. No speculative, coming-soon, or pre-order announcements without explicit playbook override. Band must be PARTIAL or above; if pricing is stated, FULL. | "Order now" → e-commerce checkout; "Add to cart" → shopping cart |
| **Reserve / book** | Reader schedules a time slot: restaurant reservation, appointment, class, tour. | Booking system is live and has real-time availability; cancellation and confirmation policies are accessible; for unattended runs, availability must be verified within 2h. | Direct commerce, retention, brand-awareness (call-to-action for event) | Availability fact is **blocking**. Time window must be real (not "always open — just call"). Confirmation method must be clear (immediate, email, phone). Band at PARTIAL or above. | "Reserve your table" → restaurant booking system; "Book a consultation" → calendar link |
| **Subscribe / join** | Reader opts into ongoing communication: newsletter, podcast, membership, community. | Subscription system is live and accepting signups; opt-in and GDPR compliance verified; unsubscribe link present. | Retention, brand-awareness, community | Entry point must be functional. No gated or paywalled signups without explicit legal review. Band at PARTIAL. Playbook may specify whether subscriptions are free or paid; if paid, the product-path rules (price at FULL band) apply. | "Subscribe to our newsletter" → email signup; "Join our Discord" → community link |
| **Visit / directions** | Reader comes to a physical location: store, restaurant, office, event venue. | Location is real and currently operating; hours and address are correct; parking, accessibility info available and current. For unattended runs, business hours and status (open/closed) verified against Google Business Profile or similar within 24h. | Direct commerce, brand-awareness, retention | Location fact is **blocking** — absence blocks the topic. If the location has moved, reopened under a new name, or changed hours this week, the CTA must not use old information. Band at PARTIAL. | "Find us on Main Street" → map + hours; "Come to our flagship store" → location + parking info |
| **Follow / tag / save** | Reader follows the account, tags a friend, saves the post, or bookmarks. Engagement CTA. | Account exists and is public (or the audience is inside the private account). | Reach & community, brand-awareness, retention | No precondition on facts — this CTA never requires offer, proof, or pricing. Playbook may disable it if the brand policy forbids unsolicited follows. Band can be as low as MINIMAL (engagement CTAs don't require high confidence). | "Follow for daily tips" → account link; "Save this for later" → native save button (no explicit link) |
| **Share / comment / tag** | Reader amplifies the post: shares to their own timeline, comments, tags others. Participation CTA. | Post is designed to be shareable and replies are monitored. | Reach & community, retention | No fact preconditions. Brand must be prepared for comments and moderation. Band can be MINIMAL. For unattended runs, moderation strategy must be declared (auto-remove spam, manual review, etc.). | "Share your experience" → native share; "Tag someone who needs this" → native tag; "Comment your favourite" → implied reply |
| **Engage via response** | Reader answers a question posed in the post: poll response, form submission, DM. Participation CTA. | Form or poll is live and responses are monitored; privacy policy covers response data. | Reach & community, retention, brand-awareness | No fact preconditions beyond the form's function. If responses will be used for marketing follow-up, consent mechanism must be clear. Band can be MINIMAL. | "Vote in our poll" → native poll; "DM your email" → chat integration; "Fill out our quick survey" → form link |
| **No-CTA** | Post stands alone. Reader is not prompted to act beyond reading or viewing. Value-only content. | No associated URL or action required. | Reach & community, brand-awareness, retention, educational (thought leadership) | No preconditions — this is always allowed. Playbook may declare "no-CTA" as the default for certain archetypes (e.g., aesthetic posts default to no-CTA unless the archetype is promotional). | Spiritual insight post with no link; behind-the-scenes photo with caption only; pure education with no signup |
| **Commercial-incentive** | Reader acts on an explicit offer: discount code, affiliate share, limited-time deal. | Discount or affiliate programme facts exist in the knowledge base with terms and validity window; required disclosures are present (affiliate status, terms); recipient tracking or coupon system is live. | Lead-gen, direct commerce, retention | Discount or affiliate terms are **blocking** — absence blocks the topic. Every discount percentage, free-trial length, or affiliate commission rate is a **claim** and must exist in the ledger with evidence and a valid-from / valid-until date. Required disclosures are governed by check class 10 (§6.7 of main plan) and the commercial-communication statement catalogue. Band must be FULL if any numeric terms are stated. Proof of affiliate programme authority must exist. | "Use code WINTER20 for 20% off" → discount code (must exist, valid window must be stated); "As our affiliate" → affiliate disclosure present |

**Rules:**

- A single asset carries **exactly one CTA**, default. Stacking multiple CTAs is forbidden (spin criterion S-6).
- A playbook declares which CTA classes are enabled. Disabled classes are never evaluated.
- If an enabled CTA class's preconditions are unmet (e.g., no event fact for an event CTA), the topic is spun without that CTA class — it falls back to a softer, available class, or to no-CTA, rather than blocking the asset.
- Language-coherence rule: if the CTA destination does not exist in the asset's language, the CTA either downgrades to a language-available class, or the asset is blocked from that destination, depending on the playbook's declared tolerance for this state. Czech product-page links during build-out are a live example (§13.3, §6.9 of main plan).
- Preconditions are checked at spin time (before drafting) and again at the platform gate (before packaging), because a booking system can go offline or a discount can expire between approval and publish.

---

## §7. Mapping-Distance Replacement

**Purpose.** The direct/adjacent/far model in §6.9 of the main plan assumes an offer exists. Generalisations:

- R-1 (offer-attachment): use the direct/adjacent/far model **as defined**. Mapping distance is explicit, recorded, and governs offer loudness.
- R-2 (inventory): no concept of distance; the announcement is inherently direct (this product, this time).
- R-3 (expressive): no offer, no distance, no relevance calculation needed.
- R-4 (commentary): no offer, no distance; relevance is "does this trend matter to this segment."
- R-5 (product-promo): distance is irrelevant; inventory *is* the topic anchor.
- R-6 (education): no offer, but **relevance distance** applies: does this technique / concept / solution map to the audience's stated problems? **Near-relevance:** the skill directly addresses a known pain (restaurant staff teaching plating, addressing retention). **Far-relevance:** the skill is aspirational or context-setting (fine-dining techniques in a casual restaurant).
- R-7 (testimonial): distance is "customer segment closeness" — did the customer profile match the target ICP? **Direct:** same business type, same industry, same problem. **Adjacent:** same industry, different problem. **Far:** different industry entirely.

**Spin gate rules per relation:**

| Relation | Distance concept | What replaces "far topics can't hard-pitch" | Short-form minimum distance | Example block |
|---|---|---|---|---|
| R-1 offer-attachment | direct/adjacent/far (explicit) | As defined in main plan §6.9; far-distance topics can have value-only variant or soft-bridge | adjacent-or-closer | Far-distance topic with product CTA on TikTok + no soft-bridge fails S-4 |
| R-2 inventory | none — announcement is direct | Offer presence and CTA correctness (S-6) always apply; no distance gate. | n/a — direct by definition | Stock-out announcement does not fail S-4; urgency gate (§4) applies instead |
| R-3 expressive | none | Spin gate depth reduced: S-1 (topic anchor) and S-3 (connection) not evaluated; S-4, S-5, S-6 waived. Only S-2 (segment relevance) remains soft. | n/a — no CTA | Spiritual post can run on any destination without distance check |
| R-4 commentary | relevance-distance (implicit) | Topic must name a trend or news item the audience cares about; if audience is creators and the topic is B2B tax law, the post is not commentary about creators, it's off-topic. Spin gate applies S-1 (topic anchored in the audience's discourse), but not S-3 or S-4. | n/a if engagement-only | Creator-focused agency critiques UGC trends: on-topic. Same agency critiques LinkedIn thought-leadership: off-topic unless positioning as meta-commentary |
| R-5 product-promo | none | Product presence, availability, and CTA are mandated (S-6). No pitch/distance gate; the asset is inherently promotional. Archetype and urgency gate (§4) apply. | n/a — inherently direct-distance | Winter jacket promo does not fail S-4; availability gate (§7 of this section) applies |
| R-6 education | relevance-distance (implicit) | Skill must solve or illuminate a known audience problem. If audience is restaurant staff, teaching data analytics is far-relevance; teaching plating is near-relevance. Spin gate applies S-1 (topic is a real problem), S-3 (bridge from problem to solution), but softens S-4 (distance) and S-5 (proof is not required for technique teaching). | n/a if value-only | Restaurant staff education on wine-pairing: near-relevance, short-form OK. Data-analytics education for restaurant staff: far-relevance, requires blog format or long-form explanation, not TikTok |
| R-7 testimonial | customer-segment distance (direct/adjacent/far by ICP match) | Customer segment defines distance. If customer profile is a direct ICP match, no tone/pitch gate applies (customer is "like them"). If adjacent (same industry, different pain), offer mention is softer. If far (different industry), offer is off-topic or reframed as generic learning. Spin gate applies S-5 (proof required — metrics must exist) and S-6 (CTA must be appropriate to distance). S-3 (connection chain) is softer — a far-distance customer's story still has emotional value even if relevance is low. | case study, not short-form | Restaurant customer testimonial: "they helped us reduce no-shows": direct distance, emphasise product mention. SaaS customer testimonial: "they helped us think differently about operations": far distance, soft offer mention or no offer mention, emphasise insight |

**Soft bridge mechanism** (main plan §6.9, clarified here):

For R-1 far-distance topics on short-form (which default to adjacent-or-closer minimum distance), a **soft bridge** is an explicit next step that is not an offer:

- A resource or question: "Not sure about your compliance yet? [learn more](link) or reply in comments."
- A specific observation: "If your email delivery is struggling, this might be why."
- An explicit permission to pass: "Not for your use case? [here's what is](link)."

The soft bridge must be **visible in the asset**, declared in the spin rationale, and validated by the platform gate before the asset ships. Without it, far-distance topics on short-form are dropped or held.

---

## §8. Wire-in — Mapping to existing sections

**Every section modified or superseded by the playbook layer:**

| Existing section | What changes | Type | Notes |
|---|---|---|---|
| §6.9 Spin application | Pain-to-offer relation is now relation-registry-gated; only R-1 uses pain; other relations use different inputs. Mapping distance is relation-specific (some have none). | Extension | Existing R-1 flow unchanged; seven new relation types added; spin mapper becomes relation-type-aware |
| §6.10 Spin gate | Seven criteria S-1…S-7 are now objective-gated: some criteria are emphasized or waived per objective. Angle-level pre-check (N-8) added. Playbook declares which archetypes it uses. | Extension | Existing gate order unchanged; objective-selector added to N-8; archetype mapping added to downgrade-repair path |
| §14.2 Voice gate | Single rubric becomes genre-registry with five + one Czech rubric. Engine floor (six universal slop points) separated from genre configuration. Czech layer applies on top of genre. | Extension | Existing five-layer structure unchanged; layer 3 (LLM judge) now consults genre rubric rather than monolithic English rubric |
| §14.4 Per-language rubrics | English rubric becomes analytical-B2B genre; Czech rubric becomes Czech-layer-on-genre; both remain; five new genre rubrics added. Phase 0 now produces English golden set + Czech golden set (was Czech only). | Extension | Existing Czech rubric promoted to parity; five genre exemplar corpora added to phase 0 |
| §3.3 Native adaptation rules | Minimum mapping distance per destination added as a configuration knob. | Extension | Existing constraints unchanged; new row added per destination |
| §10.3 Spin block | Content objective selector added; relation-type enablement added; genre rubric selector added; archetype mix declaration added; angle-type restrictions added. | Extension | Existing knobs unchanged; eight new knobs added |
| §10.4 Output/runtime block | CTA class selector (ten classes, not four) added; reservation/booking availability verification added. | Extension | Existing four classes retained as subset; new preconditions and verification added |
| §1.5 Node inventory | N-8 (angle-level spin pre-check) added; existing N-1…N-13 unchanged. | Addition | One new model node; no existing node removed |
| §8.6 Ledger set | Angle type per asset added to run ledger; relation type added; content objective added; CTA class selected added. | Extension | Existing ledger rows retained; three new metadata columns |
| §12.2 Per-topic digest | Relation type and angle type displayed in spin rationale; content objective displayed if non-default; CTA class displayed. | Extension | Existing format unchanged; metadata fields expanded |
| §13.2 Theme-readiness validation | Assertion added: every enabled archetype has a topic in the current candidate set that passes its claim-risk profile. Assertions added: every enabled CTA class has preconditions met (e.g., event CTA enabled → event facts must exist). | Extension | Existing assertions unchanged; two new assertions added |
| §11.1 Capability matrix | No change at the mode level; all features remain mode-gated identically. | No change | Playbook layer is theme-level, not mode-level |

---

## §9. Falsification — Five tenants end-to-end

Each walkthrough names: (1) what the playbook selects, (2) what a resulting pack looks like, (3) what still does not work.

### 9.1 B2B Lead Generation (HypeDigitaly: existing theme #1)

**Playbook:** objective = lead-gen; relations = R-1 only; archetypes = educational, listicle, opinion, product-hero, testimonial (no aesthetic, no BTS); CTA classes = content, product-path, commercial-incentive (no event until webinar facts exist, no follow); voice genre = analytical-B2B.

**Sample pack:** Five ranked topics. Three pass lead-gen readiness:

1. **"EU AI Act compliance deadlines" (educational, opinion hybrid).** Pain: compliance risk. Offer: HypeLead audit + education. R-1 direct distance. Relation: (ICP: compliance officers, pain: regulation) → HypeLead audit. Angle: myth-bust ("the grace period is shorter than you think"). Archetype: educational listicle. CTA: content (full compliance guide) + product-path (audit trial). Voice: analytical-B2B (specificity bar high; proof required). Spin rationale: direct connection, topic anchor strong, topic is 3 days old. Pack includes: long-form blog article, LinkedIn carousel (5 slides), TikTok short (myth-busting rhythm). All paid media spent here; video spend exhausted. Czech: identical mix, carousel-to-reel recipe.

2. **"Outbound sales tool comparison: 6 tools tested" (listicle, opinion).** Pain: tool selection paralysis. Offer: none (adjacent pain — not buying, tool evaluation). R-1 adjacent distance. Relation: (ICP: sales leaders, pain: tool evaluation) → HypeLead (adjacent — can be mentioned as evaluator choice, not as recommendation). Angle: data-driven (benchmark numbers). Archetype: listicle. CTA: content only (comparison download resource). Voice: analytical-B2B. Spin: S-7 tested — "which is exactly why HypeLead stands out" removed; replaced with fact-based list. Pack: LinkedIn long-form only (no video budget left). Czech: identical mix applied; Czech outbound-sales discourse narrower, so topic ranked lower in Czech set.

3. **Customer story: "They booked 47 demos in Q4." (testimonial).** Proof: case study in allowlist, permission fresh. R-1 (R-7 hybrid, actually — proof relation). Pain: meeting-booking volume. Offer: HypeLead product path. Angle: personal-narrative (customer CEO voice). Archetype: testimonial. CTA: product-path (trial). Voice: analytical-B2B (human-voice dimension scored; CEO authenticity checked). Spin: S-3 connection chain verified (bookings → outbound → HypeLead). Pack: Reel (1 min, testimonial on-camera), Instagram carousel (3 slides with metrics), LinkedIn short post. Czech: Czech customer's English accent acceptable; quote translated, re-approval required (Czech cust-omers are far-rarer in proof allowlist; added to 6-month revisit cadence).

Two topics held: ranking low (advisory to competitor's tool, no spin possible) + (emerging tech trend, no HypeLead offer, far distance, insufficient value-frame). Research-only output set included; digest flags low candidate carry-forward to lead-gen.

**What doesn't work:**

- Event CTA cannot be used until a dated webinar fact lands in the knowledge base; currently no events scheduled. Pack signals this; theme author is prompted to create an event if CTAs will unlock otherwise-low-priority topics.
- Czech topical supply consistently 40% thinner than English. Pack is smaller in Czech, properly named as such (not an error, not a quality miss — a language-completeness declaration drives operator understanding).

---

### 9.2 Local Hospitality (Restaurant: fixture theme #2)

**Playbook:** objective = direct commerce + brand-awareness; relations = R-2 (inventory), R-3 (aesthetic), R-6 (education, limited), R-7 (testimonial); archetypes = announcement, behind-the-scenes, aesthetic, recipe, testimonial (no listicle, no opinion); CTA classes = reserve/book, visit, subscribe, no-CTA (no product-path, no commercial-incentive); voice genre = sensory-hospitality.

**Sample pack:** Ranked topics come from Czech retail-food sources, Facebook groups, Czech food seasonality.

1. **"Fresh crab delivery Thursday mornings" (announcement, inventory).** R-2 inventory. Relation: (product: crab, availability: Thursday, time: morning) → no offer, pure announcement. Availability is live-checked against walk-in supplier status and reservations system. Angle: urgency (limited supply, time window). Archetype: announcement. CTA: reserve/book (reserve.myrestaurant.com). Voice: sensory-hospitality (emphasize the freshness; "we hand-select"). Pack: Facebook post + Reel (quick shot of crab arriving), Instagram feed post (beautiful plating photo). No video budget (carousel-to-reel only, and urgency angle doesn't suit meditative carousel build).

2. **"Behind-the-scenes: our new wine cellar" (behind-the-scenes, aesthetic).** R-3 expressive (pure aesthetic value). No inventory, no offer, no CTA. Angle: personal-narrative + sensory (team story, cave environment). Archetype: BTS. Voice: sensory-hospitality (highlight the care, the passion). Spin gate: S-1, S-3, S-4, S-5 waived for R-3; S-2 checked (is this staff/team relevant to segment? yes, existing customers). Pack: Reel (30 sec, walking through cellar, tasting wine), no CTA or call-to-action, just "our new space, coming soon." Generates engagement (save, share). Czech: identical asset mix (identical pacing, same team member — no translation of face/voice). Revenue signal: None direct; secondary metric is engagement rate and click-through to website/reservation page in bio.

3. **Recipe: "Perfect beef stew — 4 hours, three tricks" (recipe, education).** R-6 education. Relation: (cooking technique for home audience) → no offer, pure teaching. Angle: step-by-step. Archetype: recipe. CTA: none (pure value). Voice: sensory-hospitality (emphasize flavour development, smell, texture; include personal detail "my grandmother's trick"). Spin: S-1 (topic anchor is the technique), S-3 (bridge is cooking = eating well = why we care), S-4 waived (no offer distance). Pack: Blog article (1200 words, ingredient list, photos, temperature checks), Carousel (5 slides, one per step), TikTok short (time-lapse stew-making, 45 sec, no dialogue, music + captions). Czech: step-by-step carried identically; ingredient names translated; blog article duplicated (Czech blog domain separate).

4. **Customer testimonial: "They hosted our wedding. It was perfect." (testimonial, personal-narrative).** R-7 (proof) + R-3 (aesthetic). Permission check: customer photo released. Angle: personal-narrative + sensory (emotional, specific details). Archetype: testimonial. CTA: reserve/book (wedding@myrestaurant.com). Voice: sensory-hospitality (feeling, not just facts). Spin: S-3 (bride's story of the meal), S-5 (no metrics to prove; story is the proof). Pack: Reel (1.5 min, bride + groom + food moments, music, no dialogue, captions for key moments), no blog carry-over (personal story, not evergreen).

Two topics dropped: (1) "New competitor opened across the street" (no relation maps to this; off-topic); (2) "Dietary restriction trends Q4 2026" (useful signal, but no restaurant offer or inventory tied to it; would require creating an educational angle R-6, but no education budget allocated to this playbook; topic dropped, reason recorded).

**What doesn't work:**

- Commerce velocity. Restaurant playbook cannot publish real-time stock updates faster than the availability-verification lag. If crab truck is delayed, a 9 a.m. post announcing Thursday morning arrives before 9 a.m. runs, but availability verification happens only at approval time (within 2h). A same-day cancellation arrives too late. Playbook tolerates this: "availability verified at approval time; if circumstances change between approval and publish, that is the operator's call." Architecture does not solve same-second inventory dynamics; that is a separate real-time system question.
- Event integration. Weddings and private events are bookable but not calendar events in the system. Testimonials can reference events; events cannot be ranked topics themselves. Operator must curate event stories by hand or accept that testimonials arrive only after the event (memory-based, not real-time).

---

### 9.3 Esoteric/Spiritual Page

**Playbook:** objective = reach & community + brand-awareness; relations = R-3 (expressive), R-4 (commentary), R-6 (education, limited); archetypes = aesthetic, personal-narrative, opinion, commentary, engagement, behind-the-scenes (no promotional, no product-hero, no listicle); CTA classes = follow, engage (comment/poll), no-CTA; voice genre = evocative-expressive.

**Sample pack:** Topics from occult/wellness Facebook groups, astrology trend feeds, operator's curated posts (spiritual insights encountered in meditation).

1. **"Full moon at 3 degrees Taurus: the themes." (aesthetic, expressive).** R-3 expressive. Angle: sensory + personal-narrative. Archetype: aesthetic. CTA: no-CTA + (optional) follow. Voice: evocative-expressive (poetic, open-ended, no falsifiable claims). Spin gate: S-1, S-3, S-4, S-5 waived. S-2 checked (segment: spiritual practitioners, interested in astrology; yes). Pack: Reel (visual of moon phases, cosmic aesthetic, recorded meditation excerpt in background, 60 sec, no voiceover dialogue, captions with poetic text). No URL, no next action. Engagement: save, share, comment on personal experience. Czech: identical aesthetic; audio is voiceover in Czech (meditation guide, licensed), subtitles in Czech.

2. **"Why New Age astrology gets birth charts wrong." (commentary, opinion).** R-4 commentary (on astrology practice) + R-3 expressive (vibe + insight). Angle: contrarian + problem-origin. Archetype: opinion. CTA: engage (comment your perspective) + follow. Voice: evocative-expressive (opinionated, insider, irreverent). Spin gate: S-1 (topic anchor: mispractive), S-3 soft (bridge is "understanding astrology better"), S-4 waived. S-2 checked (segment: astrology enthusiasts; yes). Pack: Long-form post (600 words, personal anecdote, no numbers, no commercial claim), Reel (1 min, quick critiques of common misconceptions, recorded voice, evocative visuals). CTA: "What's your experience?" (poll or comment).

3. **"Grounding technique for anxiety: 5-senses practice" (education, how-to).** R-6 education + R-3 (sensory framing). Angle: step-by-step + personal-narrative. Archetype: educational. CTA: no-CTA (pure value). Voice: evocative-expressive + educational-structured (clear steps, sensory language, no medical claims). Spin gate: S-1 (technique is the anchor), S-3 (bridge: anxiety → grounding practice), S-5 (no proof required; teach technique). Claim gate: "anxiety" is not a medical claim if framed as "when you feel overwhelmed" (non-clinical language). Pack: Blog article (800 words, steps, sensory details, background music embedding), Reel (2 min, guided practice, voice-over in Czech, calm visuals, no subtitle, captions for timing), Carousel (5 slides, one per sense).

Held topic: "Tarot card meanings simplified" (archetype: education, but requires a full tarot reference deck; corpus-leakage check flags the deck's existing online sources; topic is held pending clarification that this deck is the page operator's own IP or permitted licensed deck, not copyrighted external deck; risk of brand violation if shipped).

Dropped topic: "Mercury retrograde energy" (high-frequency topic, ranked high; but page already published identical angle 6 weeks ago per cross-pack recurrence; topic downgraded to monitor-only, not generated again).

**What doesn't work:**

- Monetization. Reach-and-community playbook cannot support commercial CTAs. If the operator wants to sell tarot readings or guided meditations, those become a separate commercial playbook (direct-commerce objective, product-hero archetype, product-path CTA), which is a different theme or a theme-mixing scenario that playbook design explicitly forbids. The page operates as reach + awareness only; commercial offers are off-scope.
- Claim checking. Spiritual practices sit in a grey zone where "science says" arguments fail on their own terms (spiritual practitioners expect interior truth, not empirical evidence), yet "anxiety relief" slides toward medical claim if stated too confidently. Claim gate currently blocks medical outcomes regardless of framing. Playbook tolerates this: high-evidence-bar topics (meditation for anxiety) are held until the operator explicitly approves them in a decision session; unattended runs cannot bridge that gap.

---

### 9.4 Creator / UGC Commentary Agency

**Playbook:** objective = reach & community + brand-awareness; relations = R-4 (commentary), R-6 (education); archetypes = commentary, opinion, behind-the-scenes, educational, engagement (no promotional); CTA classes = follow, engage, no-CTA; voice genre = creator-casual.

**Sample pack:** Topics from TikTok/YouTube trend reports, creator newsletters, operator's own observations of creator behavior and brand missteps.

1. **"Why UGC creators hate the new TikTok algorithm (and how to adapt)." (commentary, education hybrid).** R-4 commentary (on algorithm change) + R-6 education (adaptation techniques). Angle: contrarian + problem-origin + personal-narrative. Archetype: commentary + educational. CTA: follow + engage (share your workaround). Voice: creator-casual (insider, irreverent, field-tested). Spin gate: S-1 (algorithm change is the topic anchor), S-3 soft (bridge is "algorithm knowledge matters to creators"), S-4 waived. S-2 (segment: TikTok creators; yes). Pack: Long-form post (1000 words, lived experience, no corporate jargon, callouts to creator myths), Reel (1.5 min, screen-grabs of TikTok feed + creator reaction voiceover, fast cuts, on-brand graphics), ~~YouTube Short~~ (same Reel recomposed). CTA embedded: "Reply with your trick" (YouTube Community tab or TikTok comment thread linked in bio).

2. **"This ad creative works because..." (analysis, behind-the-scenes breakdown).** R-4 commentary (on ad-creative trends) + R-3 (aesthetic, if the ad is visually striking). Angle: feature-highlight (of the ad technique). Archetype: commentary. CTA: follow (for trend updates) + engage (react/comment). Voice: creator-casual (technical insider, light humour). Spin gate: S-1 (specific ad is the anchor), S-3 (bridge: studying ads teaches creators). Pack: Reel (45 sec, ad shown + operator's breakdown voiceover, quick annotations). No product-path CTA; no commercial incentive. Commentary on others' ads does not sell anything; operator's own services (consultation, coaching) would require a separate commercial playbook.

3. **"5 UGC mistakes we see weekly (and how to fix them)." (listicle, educational).** R-6 education + R-4 (commentary on common mistakes). Angle: myth-bust + problem-origin. Archetype: listicle. CTA: no-CTA (pure value). Voice: educational-structured + creator-casual (clear steps, insider language). Spin gate: S-1 (mistakes are the anchor), S-3 (bridge: understanding mistakes improves UGC). Pack: Blog article (1200 words, 5 mistakes, solutions, visuals), Carousel (5 slides, one mistake per slide, before/after examples), YouTube Short (60 sec montage of the mistakes with corrected versions).

4. **BTS: "How we evaluate UGC creators." (behind-the-scenes, commentary).** R-3 expressive (showing the agency's process) + R-4 (implicit commentary on creator-quality standards). Angle: process-transparency + personal-narrative (team story). Archetype: BTS. CTA: follow + engage ("what do you look for?"). Voice: creator-casual (process is real, opinions are transparent). Spin gate: S-1 (evaluation process is the anchor), S-2 (segment: creators and brands hiring creators; yes). Pack: Reel (1.5 min, team meeting footage, voiceover explaining rubric, behind-the-scenes shots), Instagram post (carousel, the team + evaluation criteria).

Topic held: "New creator platforms Q4 2026" (ranked high, but no evaluation angle tied to it; pure news, not commentary or education; held pending archetype/angle fit clarification).

**What doesn't work:**

- Audience confusion. Reach-and-community playbook means no product selling through the feed. But the agency sells consultation and UGC creation services. Those belong in a separate (or parallel) commercial playbook, with a separate theme, separate landing pages, and separate audience expectations. If the operator tries to blend ("follow our TikTok for tips AND hire us"), that is theme-mixing, which the system explicitly forbids. The reach-side and commerce-side live in separate outputs, separate cadences, separate CTAs. Operator must decide which this account is, upfront.
- Real-time commentary. Trends move faster than the playbook's collection cadence. If a major UGC scandal or platform change happens on Tuesday, the system's next scheduled pack is Thursday, and scheduling is manual after that. Creator playbooks are therefore more operator-manual than fully-scheduled B2B playbooks; the operator curates urgent topics by hand and feeds them to the curated-inbox (§2.3 of main plan) to force inclusion.

---

### 9.5 E-commerce Product Promotion

**Playbook:** objective = direct commerce + retention; relations = R-2 (inventory), R-5 (product-promo), R-7 (testimonial); archetypes = announcement, promotional, product-hero, testimonial, how-to (no opinion, no aesthetic, no BTS); CTA classes = order/purchase, visit, reserve/book (if fulfillment requires location), follow, no-CTA; voice genre = product-persuasive.

**Sample pack:** Ranked topics from e-commerce demand data (search trends), inventory feeds (out-of-stock alerts), customer reviews, seasonal buying patterns, competitor promotional patterns.

1. **"Black Friday: winter jackets 40% off, Friday–Sunday only." (announcement, promotional, inventory).** R-2 inventory + R-5 product-promo. Relation: (product: winter jacket, status: in-stock, price: 40% off, window: Friday–Sunday) → no pain, pure announcement. Availability and pricing are live-checked against inventory system and discount codes within 4h of approval. Urgency angle: time window + discount size. Archetype: promotional. CTA: order/purchase (add-to-cart URL). Voice: product-persuasive (confidence, benefit framing — "stay warm this winter"). Spin gate: S-1 (sale date is the anchor), S-4 waived (no distance; purely promotional). S-6 (CTA must be live and functional). Pack: Reel (30 sec, product beauty shots, discount callout, music, no voiceover), Instagram post (hero image + copy with discount code), Facebook post (carousel, jacket colours + discount overlay), email (if in cross-channel mode). Czech: identical asset mix, product names translated (if the jacket has a name), copy written natively.

2. **"Customer story: 'This jacket survived two winters of commuting. Worth every penny.'" (testimonial, product-hero).** R-7 testimonial + R-5 (product implicit). Permission: customer review harvested and approved. Proof: purchase history in system, review date 2 weeks ago. Angle: personal-narrative + before-after (implicit — durability). Archetype: testimonial. CTA: order/purchase (link to jacket page). Voice: product-persuasive (human authenticity + benefit angle). Spin gate: S-1 (customer story is the anchor), S-3 (connection: personal story → product value), S-5 (review is the proof). Pack: Reel (1 min, customer testimonial on-camera, product shots, customer wearing jacket, music), Instagram post (carousel, customer + product + review quote).

3. **"How to layer for winter: 3-piece system." (how-to, education).** R-6 education + R-5 (product implicit). Relation: (technique: layering strategy) → no offer, pure teaching, but product is woven through. Angle: step-by-step + feature-highlight (product as tool). Archetype: how-to + educational. CTA: order/purchase (link to jacket if featured; otherwise, no-CTA). Voice: product-persuasive + educational-structured (clear steps, benefit framing). Spin gate: S-1 (layering technique is the anchor), S-3 (bridge: winter → layering → our jackets), S-5 (technique is self-taught, not claimed). Pack: Blog article (1200 words, layering system, photos of each piece, link to jacket product pages), YouTube Short (60 sec, get-ready-with-me style, showing the 3-piece system), TikTok (carousel of outfit combinations, music, captions). No hard sell; value-first.

Held topic: "Waterproof fabric technology explained" (educational, but exists without a product attachment; could be standalone value content, but e-commerce playbook's objective is direct commerce — held pending decision: is this value content or pure education? If pure education, it belongs in a separate brand-awareness playbook; if commerce, it needs an implicit product tie-in to justify the spend).

Dropped topic: "Our competitors' winter jackets ranked" (opinion/commentary angle, not product-promo; e-commerce playbook does not have opinion archetype enabled; ranks high but is off-playbook).

**What doesn't work:**

- Inventory lags. Product-promo playbook requires real-time or near-real-time availability. If a "limited stock" post is approved Thursday and publishes Friday, but the product sells out Friday afternoon, the post is still live for 3 days over the weekend before the operator can take it down. Architecture does not solve weekend operations. Mitigation: use urgency angles only when the operator is actively monitoring, or stagger drops across days so weekend gaps matter less.
- Return rate transparency. Product testimonials and durability claims land at the proof gate — customer must have the jacket in the claim ledger's allowlist. But "this jacket survived two winters" depends on the customer still owning it and being happy, which can change. Customer reviews are customer-published; they are not the brand's controlled truth. Claim gate allows them as R-7 (proof) but marks them with lower confidence than brand-authored capability statements (F-C). Risk tolerance is operator's choice: tighter gate = fewer customer reviews ship; looser gate = more authentic voice, more refutation risk.

---

## §10. Summary of Key Decisions

**The playbook layer enables generalization across five tenant archetypes by making explicit what was implicit in B2B:**

1. **Content objective:** Selecting from five named business goals (lead-gen, direct commerce, reach, awareness, retention) cascades into what spin criteria apply, which CTAs are legal, and what success means.

2. **Relation types:** Seven named content-source-to-target mappings replace the hard-coded pain-to-offer. Offers, inventory, expressive content, commentary, product promotion, education and testimony each have distinct spin gates and fact dependencies.

3. **Post archetypes:** Eleven named post *kinds* (educational, promotional, behind-the-scenes, etc.) replace implicit asset-type-only classification. Mix ratios enforce target distributions rather than allowing algorithmic volume drift.

4. **Angle taxonomy:** Fifteen angle types (how-it-works, myth-bust, urgency, etc.) are selected per topic × archetype, with angle-level spin pre-check (N-8) before drafting begins.

5. **Voice genres:** Five genre rubrics (analytical-B2B, sensory-hospitality, evocative-expressive, creator-casual, product-persuasive, plus educational-structured) build on a universal six-point slop floor that cannot be waived. Each genre specifies what it permits: e.g., evocative-expressive rewards curiosity-gap teasers; analytical-B2B forbids them.

6. **CTA vocabulary:** Ten classes (content, product-path, order/purchase, reserve/book, visit, follow/share/comment, subscribe, no-CTA, commercial-incentive) with objective-gated availability and fact-class preconditions.

7. **Mapping distance replacement:** Direct/adjacent/far applies only to R-1 (offer-attachment); other relations use relation-specific distance concepts or none.

**Safety:** The engine's six-point universal slop floor (no fabrication, no incoherence, no corpus-bleed, no manipulation, no accessibility failure, no brand-lock violation) is inherited by every playbook and cannot be relaxed. Playbooks configure safety rules *on top* of the floor, never below it.

**Extensibility:** A new playbook is a configuration + content exercise, never engineering. Existing archetypes, angle types, voice genres, CTA classes, and relations are shared across playbooks. Only fundamentally new content types (e.g., podcasts) or languages (e.g., Arabic) require engineering.

---

## §11. Open Questions for Operator

1. **Theme mixing:** May a single account's output serve multiple objectives simultaneously (e.g., educate AND sell)? Current design: no — a playbook is monolithic per objective. If operator wants mixed objectives, that is two themes, two cadences, two output sets (one branded as "learn", one as "shop"). Recommend deferring this until trial clarifies whether audience tolerates the split.
   - **W8-10 update:** the operator's post-mix request (`generation.post_mix`: value_only/playbook/promotional counts, cross-topic-allocated within one theme/account) supersedes this no-mixing stance — implemented as the narrow slice described here, not the full mode/theme-split alternative. See the W8-10 build plan's Phase 5 for the minimal-cut implementation.

2. **Angle weighting:** Should unpopular angles be actively down-weighted, or randomly selected among legal options? E.g., "curiosity-gap is legal in reach-and-community; should it dominate the 40% education slots or stay rare?" Recommend starting uniform; adjust after five real packs have measured engagement.

3. **Archetype degradation:** When a ranked topic cannot safely deliver its assigned archetype (e.g., insufficient proof for an educational archive), should it downgrade to the next-best archetype for that topic, or drop from the pack? Current design: downgrade, recorded in pack. Alternative: drop, with feedback for next run. Recommend downgrade + feedback (best of both).

4. **Czech playbook parity:** All examples above are English-first; theme #2 (Czech e-commerce) is monolingual Czech. Should Czech playbooks be treated as full first-class citizens (same design surface, same readiness validation) or as "English playbook + Czech language overlay"? Current design: first-class citizens, but they inherit shared language overlay. Confirm operator intent.

5. **Operator workload:** The playbook layer adds configuration surface (≈20 new knobs per theme) but removes engineering. Should Phase 0 deliver a playbook-builder UI/wizard, or is configuration file + documentation sufficient? Recommend documentation + worked examples for Phase 1 trial; UI deferred to Phase 5 if workflow proves repetitive.

---

## §12. Handoff to Implementation

This specification defines:

- **What may not change** (engine slop floor, stage order, fail-closed gates, mode capability matrix)
- **What must be configurable** (content objective, enabled relations, enabled archetypes, enabled CTAs, enabled angle types, voice genre, mix ratios)
- **What is new in node N-8** (angle-level spin pre-check with output: angle suitable or not, returning to topic ranking if not)
- **What is new in the ledger** (angle type, relation type, content objective, selected CTA class per asset)
- **What is new in spin mapper** (relation-type dispatch instead of pain-to-offer only)
- **What is new in voice gate** (genre rubric selector instead of monolithic English rubric; universal floor + genre-specific layer)

No implementation syntax, no configuration schema, no code sketches — those belong in the implementation plan D-02, requested separately.

---

*End of specification.*
