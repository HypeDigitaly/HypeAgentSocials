# A3 — Durable Prompt / Skill / Agent Patterns for Viral AI Video (Wave 1, Track T3)

**Assignment mandate covered:** Block A item 5 (LLM prompts, skills, and agents used by strong practitioners for hooks/scripts/shot-lists/on-screen text/negative prompts/brand locks; reusable skill packs; shared-skills vs theme-overlay boundary).
**Scope boundary:** This is an EXPERTISE brief — durable prompt-engineering and skill-architecture patterns that hold regardless of which specific model API is behind them. It does NOT rank or specify Kie.ai/Higgsfield.ai/other vendor model names, endpoints, or pricing — that is A2's territory (model-specific guides) and is treated here as **ASSUMED INPUT (from A2)** wherever a model capability is referenced. No web access was used for this brief; all patterns are grounded in durable prompt-engineering practice (chain-of-thought, few-shot, constitutional/rubric-gated generation, template architecture) applied to the specific domain of short-form video/reel content.

---

## 1. What this means for the operator

When the system needs to turn "AI is changing outbound sales" into an actual 20-second vertical video, it doesn't send one vague instruction to a video model and hope. Strong practice breaks that job into a small pipeline of narrow, checkable steps — hook idea, then script, then a shot-by-shot plan, then on-screen text, then a list of things to explicitly avoid, then a check that the brand still looks and sounds like us — each with its own focused instruction ("prompt") and its own quick self-check before moving to the next step. That is what "prompt structure" means in this brief: not a single clever sentence, but a small assembly line of instructions, each with a defined input, output, and pass/fail check.

The reusable parts of that assembly line (how to write a hook, how to structure a shot list, how to phrase a negative-prompt, how to run a brand-consistency check) should be built **once**, generically, and reused for every theme/brand the system ever serves. Only the specific voice, offers, target customer, and example library for "HypeDigitaly this week" should be swapped in per theme. Getting this boundary right is what lets the system add a tenth theme in an afternoon instead of a rewrite.

Czech content is not English content translated — the whole assembly line needs a Czech-native pass at the hook/script/on-screen-text layer, because slang, cringe markers, and platform norms differ by language, not just by dictionary.

Finally, because this will eventually run at 3 AM with nobody watching, every step in the assembly line needs a defined "what happens when this step fails" behavior: try again a bounded number of times, fall back to a safer/plainer version, or stop and flag for a human — never silently invent or silently publish a broken result.

---

## 2. Body

### 2.1 Prompt structures for hooks, scripts, shot lists, on-screen text, negative prompts, brand locks

The durable pattern across all six artifact types below is the same **four-part anatomy**: (1) role/constraint framing, (2) grounded inputs (what real facts/exemplars the model is allowed to draw on), (3) the generation instruction itself with explicit output shape, (4) a self-check/rubric the model applies to its own output before it is considered "done." This mirrors constitutional-AI and self-critique patterns generalized to a creative-writing + video-planning domain. Each artifact type below is described as an anatomy (slots + ordering + rationale), not as literal text.

**A. Hook prompts (first 1–3 seconds of the video)**

Anatomy, in order:
1. *Role framing slot* — establishes the writer persona as a specific human voice (e.g., "an operator who has personally seen this problem," not "a marketing assistant"), because persona framing measurably shifts register away from generic AI phrasing.
2. *Grounded-topic slot* — the actual researched pain/trend/quote this hook must be about (never invented), sourced from the research/ranking pipeline output.
3. *Brand-fit slot* — one line stating how this connects to the configured ICP, so the hook doesn't drift into unrelated virality.
4. *Hook-pattern menu slot* — a small enumerated set of hook mechanics to choose among (contrarian claim, specific number/stat framed as observation, "POV" address, blunt problem statement, pattern-interrupt visual cue described in words) rather than one fixed template — this is what keeps hooks from converging on a single repeated shape across dozens of runs.
5. *Negative-constraint slot* — explicit "do not" list scoped to hooks specifically (no fake urgency, no invented stat, no "you won't believe," no rhetorical question opener as a crutch).
6. *Output-shape slot* — exactly what to return: 3–5 short candidate hook lines (spoken line) each paired with a one-phrase visual/on-screen concept, so downstream steps can pick without regenerating.
7. *Self-check slot* — a short rubric the model runs against its own candidates before returning them (would a real person say this out loud; is it specific not generic; does it contain zero invented facts) — rejecting/regenerating candidates that fail before they ever reach a human.

Rationale: hooks are the highest-leverage, highest-risk 3 seconds of the asset (viral literature consensus: most drop-off happens here), so this is the one artifact type that most benefits from generating *several* candidates plus a selection rubric rather than one best-guess output — cheap to overgenerate text, expensive to overgenerate video.

**B. Script prompts (full spoken/read narration)**

Anatomy:
1. Inherits the chosen hook verbatim as a locked opening line (scripts should not be free to rewrite the hook that was already vetted).
2. *Structure-scaffold slot* — a beat-map the model fills in rather than free-writes: hook → problem/relatable beat → turn/insight beat → soft proof or mechanism beat → soft CTA beat. This scaffolding is the chain-of-thought equivalent for short-form copy: it forces intermediate structure instead of one long generative pass, which measurably reduces rambling and clichés.
3. *Length/pacing budget slot* — target spoken duration and words-per-beat so the script maps cleanly to a target video length before shot planning begins.
4. *Voice-lock slot* — theme-specific voice descriptors and a small negative-lexicon reference (see 2.5) injected here, not hardcoded into the shared template.
5. *Claim-safety slot* — explicit instruction that only facts present in the supplied brand-truth/context object may be asserted; anything else must be phrased as a general/industry statement, not a specific claim.
6. *Self-check slot* — rubric pass for: human-voice test ("would a person say this in conversation"), banned-phrase scan, claim-safety scan, CTA softness scan.

**C. Shot-list prompts (visual plan mapped to script beats)**

Anatomy:
1. *Script-beat input slot* — the approved script broken into its beats (from B), each beat becomes one or more shot rows.
2. *Shot-grammar menu slot* — a small vocabulary of camera/composition descriptors the model must choose from per shot (static talking-to-camera framing, close insert/product-style detail, screen-capture-style overlay, text-card beat, b-roll/cutaway concept) — constrained vocabulary rather than free description, because unconstrained shot description is where video-model prompts drift into unfilmable or inconsistent requests.
3. *Continuity-anchor slot* — a short description of the recurring visual anchor (same "character"/avatar look, same color/graphic treatment, same lower-third style) repeated identically across every shot row — this is the mechanism that keeps a multi-shot sequence feeling like one video instead of disconnected clips (see 2.4 for how this anchor is expressed differently for multi-shot-native models).
4. *Per-shot duration/pacing slot* — target seconds per shot tied back to the pacing budget from the script step.
5. *Transition-intent slot* — how this shot is expected to connect to the next (hard cut, match cut on motion, text-card interstitial) described conceptually, not as model-specific transition syntax.
6. *Self-check slot* — does total shot duration match target length; does every shot have a continuity anchor reference; are there any shots that require something the brand doesn't have (a real spokesperson likeness, a real office, a real product screenshot) that must instead route to a flagged "needs real asset" state rather than being invented.

**D. On-screen text prompts (captions/burned-in text overlays)**

Anatomy:
1. *Source-of-truth slot* — on-screen text must be generated from the *approved script*, not independently invented, to avoid mismatch between spoken claim and displayed claim.
2. *Readability-constraint slot* — hard limits expressed as rules, not code: short line count, plain words, no dense sentences, because unreadable/too-dense on-screen text is one of the most common "AI slop" tells and quality-rubric rejection reasons (assignment explicitly lists "unreadable text" as a rejection criterion).
3. *Emphasis-marking slot* — which 3–6 words per beat get visual emphasis (the "keyword pull"), decided explicitly rather than left to a renderer default, since keyword emphasis is a large driver of short-form retention.
4. *Platform-variant slot* — caption style differs by destination (TikTok/Reels burned-in captions read differently than YouTube Shorts packaging text) — this slot pulls the platform-specific rendering convention rather than assuming one universal style.
5. *Claim-safety re-check slot* — a second claim-safety pass specifically on the shortened/emphasized text, because compression during captioning is a common place where a softened spoken claim becomes an overstated on-screen claim.

**E. Negative-prompt structures (what to explicitly exclude)**

Negative prompting in this domain is best organized as **layered, reusable lists** rather than one bag of "don't do X," because different layers change at different rates and are owned by different parts of the system:
- *Engine-level visual negative list* (shared, rarely changes): morphing/warping artifacts, extra/malformed limbs or faces, text that renders as garbled characters, inconsistent lighting/character drift across a sequence, stock-photo/stock-footage look, generic corporate-stock-video aesthetic.
- *Engine-level copy negative list* (shared, the "anti-slop lexicon" — see also F): banned phrase families independent of language (game-changer clichés, "it's not X it's Y," false urgency, fake countdown/scarcity, invented statistics, generic superlatives).
- *Theme-level negative list* (overlay, changes per brand/theme): named competitors never to depict/imply, category claims this brand is not allowed to make, visual elements off-brand for this specific company (e.g., no stock "hustle culture" imagery if the brand voice is calm/technical).
- *Language-level negative list* (overlay, changes per language — see 2.5): a Czech-specific slop lexicon that is not a translation of the English one.

Rationale for layering: a single flat negative-prompt list becomes unmaintainable once there are more than a few themes and both languages — every new theme would otherwise require re-auditing one giant blob. Layering means each list can be edited independently and composed at generation time.

**F. Brand-lock structures (visual/voice identity constraints)**

A brand lock is best modeled as a **small structured fact set** injected into every relevant prompt step (script, shot-list, on-screen text, and any image/video-model prompt), rather than a paragraph of prose repeated everywhere. Durable slots inside a brand lock:
- Identity anchor (company name, product name, allowed self-description — sourced from brand-truth resolution, not invented here).
- Visual baseline (color/logo/typography treatment if the theme has one; whether a consistent avatar/presenter look is used and, if so, its locked description so it doesn't drift shot-to-shot or run-to-run).
- Voice descriptors (3–6 adjectives plus 2–3 example lines of "sounds like us" vs "does not sound like us" pulled from the theme's exemplar corpus).
- Claim boundaries (what may be asserted, what must stay generic, what is always forbidden — prices/ROI/client names/case metrics per the non-negotiable product constraints).
- CTA policy (soft-CTA default, named next step, forbidden hard-sell phrasing).

The brand lock is consumed identically by every downstream prompt step; its *contents* are theme-specific but its *slot structure* is engine-level (see 2.3).

### 2.2 Skill-pack / agent pattern for reels scripting, social video, ad creative, UGC workflows

A durable way strong practitioners organize this (borrowing directly from the "skill" concept used in agent tooling generally: a bundle of instructions + exemplars + rubrics + fallback behavior, not just a single prompt) is to define one **skill bundle per artifact family**, each containing the same four internal parts:

| Part | What it holds | Who edits it |
|---|---|---|
| Instructions | The anatomy/prompt structure for that artifact (as in 2.1) — the durable "how" | Engine maintainers (rare edits) |
| Exemplars | A small curated set of "good" and "bad" example outputs used as few-shot grounding and as negative examples | Theme owners contribute theme exemplars; engine owns a generic seed set |
| Rubric | The pass/fail self-check criteria applied before an artifact is considered acceptable (maps directly to the quality-rubric research from Block A: motion glitches, unreadable text, fake metrics, brand mismatch, slop-look, human-voice test) | Shared rubric core + theme-specific additions |
| Fallback | What to do if the rubric fails N times: degrade to a simpler/safer variant, drop to plan-only (no media spend), or escalate to human review flag | Engine-level policy, theme can tighten (never loosen safety) |

Four skill bundles cover the assignment's named workflows:
- **Reels/short-video scripting skill** — hook → script → shot-list → on-screen text, chained as in 2.1, output is a full "video plan" object plus optional generation trigger.
- **Ad-creative skill** — same chain but with a stricter claim-safety rubric (paid distribution raises the cost of an overstated claim) and a mandatory human-review gate before any spend, consistent with the assignment's "spend still human-controlled" constraint for the later-phase paid path.
- **UGC-style skill** — a variant of the reels skill where the shot-grammar menu (2.1-C) is constrained to handheld/testimonial-style shots and the script scaffold is constrained to first-person "I tried this" phrasing; this is the skill most sensitive to looking fake if claim-safety and human-voice rubrics are skipped, so its rubric weight on "would a human actually say this" should be highest of the four.
- **Carousel/still-asset skill** — same hook+copy chain, shot-list step replaced by a slide-list step (per-slide headline + supporting line + visual concept), same on-screen-text and negative-prompt layering applies.

Each bundle is a chain of narrow steps with a checkpoint after each (per 2.1's self-check slots), not one monolithic generation call — this is the same "decompose into verifiable intermediate steps" principle that chain-of-thought and tool-use agent patterns rely on generally, applied here to creative production instead of reasoning tasks.

### 2.3 Shared-skills vs theme-specific-overlay boundary

Placement rule (the operative test): **if changing it would require touching more than one theme at once, it belongs at the engine level; if it can change for a single brand without affecting any other brand, it belongs in the theme overlay.**

| Asset | Engine-level (shared) | Theme-level (overlay) |
|---|---|---|
| Prompt anatomy/slot structure (2.1) | Yes — the ordering, the self-check mechanism, the output shape | No |
| Hook-pattern menu (mechanics: contrarian/POV/stat/etc.) | Yes — the menu of mechanics | Theme may weight which mechanics are preferred (e.g., a conservative B2B theme deprioritizes "shock" hooks) |
| Shot-grammar vocabulary | Yes — the vocabulary itself | Theme may restrict which shot types are allowed (e.g., no "real spokesperson" shot type until a licensed avatar exists) |
| Rubric core (slop-look, motion glitches, unreadable text, human-voice test) | Yes | Theme may add extra rubric lines (e.g., "never depict competitor X") |
| Engine-level negative lists (visual artifacts, generic copy-slop lexicon) | Yes | — |
| Voice descriptors, tone adjectives | No | Yes — this is definitionally per-brand |
| ICP definitions, pains, offers, CTAs | No | Yes |
| Exemplar corpora ("sounds like us" examples) | Engine owns a small generic seed set for cold-start | Theme owns and grows its own corpus over time; theme exemplars should outweigh engine seed exemplars once a theme has run enough cycles |
| Claim-boundary specifics (what facts exist to assert) | No — engine only defines *that* a claim-boundary slot exists and how it's enforced | Yes — the actual facts come from brand-truth resolution (config + MCP + public verification), which is out of this brief's scope but is the data source this slot reads from |
| Language-specific slop lexicon and platform-norm notes | No (engine defines that a language overlay exists) | Yes, per-language overlay (see 2.5) — note this is a *third* axis, not purely theme, since it's shared across all themes writing in the same language |
| CTA softness policy default | Yes — the default posture ("soft by default") is an engine-level safety rule | Theme may only make it *harder* to loosen (e.g. explicit config flag) never silently override |

Practical implication for extensibility: adding theme #2 should mean writing a new voice/ICP/exemplar/claim-fact overlay and, if needed, a restricted shot-grammar subset — it should never require touching the hook/script/shot-list/on-screen-text anatomy, the rubric core, or the engine-level negative lists. If a new theme's needs cannot be met by overlay alone (e.g., it needs a genuinely new hook mechanic), that mechanic should be added to the shared menu (benefiting all themes) rather than special-cased inside that one theme.

### 2.4 Multi-shot-native video models vs single-clip models — conceptual shot-list structure change

This section is deliberately conceptual; which specific model families are single-clip vs multi-shot-native, their exact duration/continuity limits, and vendor-specific prompt syntax are **ASSUMED INPUT (from A2)** and must be reconciled with A2's model-specific findings during synthesis.

The durable conceptual distinction:

- **Single-clip models** generate one short, usually visually self-contained clip per generation job. The shot-list step (2.1-C) must therefore treat each row as an *independent generation job*: every shot row's prompt must fully re-state the continuity anchor (character look, color treatment, setting) from scratch, because the model has no memory of a prior shot in the same sequence. This means the shot-list skill's output is effectively a list of N separate, fully self-contained generation prompts, and a separate downstream edit/assembly step (cuts, ordering, transitions, pacing) is required to stitch them into one coherent video. Continuity is achieved *entirely through prompt discipline* (repeating the same anchor description verbatim across shots) plus post-hoc editing, and is the most common failure point for visual drift (character/face changing between shots, color grade shifting) that a brand-lock/quality-rubric must specifically watch for.

- **Multi-shot-native models** (models capable of producing several coherent shots — or a full short sequence with implied cuts/camera changes — inside a single generation job) shift where continuity is enforced: instead of the *prompt author* repeating an anchor description N times, the *model itself* is asked to maintain a stated identity/setting/style across an internally-generated sequence. Conceptually this changes the shot-list prompt structure in three ways: (a) the shot-list becomes a single structured brief describing the whole sequence (beat-by-beat intent, pacing, and the anchor stated once at the top) rather than N independent self-contained prompts; (b) the self-check step shifts from "does each shot separately match the anchor" to "does the model's *output* sequence hold the anchor across shots" — i.e., the rubric check moves from prompt-time to review-time; (c) the negative-prompt and brand-lock injections need to be stated once at the sequence level rather than repeated per shot, reducing prompt length and repetition-drift risk, but increasing the blast radius of a single wrong instruction (one bad global constraint now affects every shot in the job rather than just one).

Operational implication for the skill design (kept generic on purpose): the shot-list skill bundle should support **both output shapes** — an N-row independent-shot-prompt list, and a single sequence-brief — selected based on which capability class the target generation route belongs to (a routing fact that A2's model research determines), with the same upstream hook/script/continuity-anchor inputs feeding either shape. This keeps the hook/script layer (2.1-A, 2.1-B) fully reusable regardless of which shot-list shape gets produced downstream.

### 2.5 Language portability — cs vs en, not translation

Per the assignment's explicit framing (F-7), Czech is a first-class language variant, not a translation pass on English output. The durable distinction for prompt design:

**Portable across languages (engine-level, language-agnostic):**
- The four-part prompt anatomy itself (role framing → grounded input → generation instruction → self-check) — structure is language-independent.
- The beat-scaffold for scripts (hook → problem → turn → proof/mechanism → soft CTA) — a structural pattern, not language-specific wording.
- The shot-grammar vocabulary and continuity-anchor mechanism (2.1-C) — visual planning is largely language-independent (a close-up is a close-up in either language).
- The rubric *categories* (human-voice test, claim-safety scan, slop-look check, readability check) — the categories themselves transfer; only the concrete lexicon each category checks against does not.
- The engine-level visual negative list (2.1-E) — motion glitches and garbled text render the same regardless of spoken language.

**Not portable — requires a genuine per-language overlay, not a translated copy:**
- **The slop lexicon.** English AI-marketing slop markers ("game-changer," "let's dive in," "unlock," "leverage," "seamless") do not map one-to-one onto Czech slop markers. Czech has its own set of AI-translation-smelling constructions and corporate-mush calques that a native Czech speaker recognizes as "obviously translated/AI" even when no single word is wrong — this overlay must be authored by/validated against native speaker judgment (or a native-Czech exemplar corpus), not derived by translating the English list. This brief flags the specific Czech lexicon content itself as needing native-speaker/language-research validation (recheck-by item, see Fact Ledger) rather than asserting concrete Czech phrases here, since getting this wrong in either direction (missing real Czech slop, or false-flagging normal Czech phrasing as slop) is a direct human-voice-quality risk.
- **Platform/register norms.** What reads as natural short-form register on Czech social platforms (level of informality, use of diminutives, code-switched English tech terms which are actually normal in Czech tech discourse rather than a red flag, sentence rhythm) differs from English short-form norms and must be captured as its own reference/exemplar set, not inferred from the English rubric.
- **Hook mechanics weighting.** Which hook mechanics (contrarian claim, direct address, blunt statement) land naturally in Czech vs feel imported/foreign is a register question specific to the language and target platform, and should be tuned via the Czech exemplar corpus rather than assumed identical to English weighting.
- **On-screen text conventions.** Line-break/emphasis conventions, diacritics rendering risk in generated video-burned text (a concrete technical risk worth flagging for the video-pipeline architecture: some text-rendering paths in video/image models handle non-ASCII diacritics unreliably — this is an ASSUMED INPUT for A2/architecture to verify per provider, not asserted as fact here), and caption length norms may differ per language and platform.

**What a cs-specific prompt overlay must carry, concretely (structure, not literal text):** a Czech slop-lexicon reference list (native-validated), a Czech "sounds human" vs "sounds AI/translated" exemplar pair set (mirroring the theme's English exemplar corpus structure from 2.3), a note on acceptable English-tech-term code-switching (which English terms are normal in Czech tech/marketing register and therefore not slop, vs which are lazy anglicisms to avoid), and any diacritic/rendering caveat relevant to on-screen text generation. This overlay sits at the *language* layer described in 2.3's table — it is shared across every theme that publishes in Czech, and composes with (does not replace) the theme-specific voice overlay: a given run uses theme-voice-overlay + language-overlay + engine-core together.

Placement rule extension: because a language overlay is shared across all themes writing in that language (not owned by one theme), it should be modeled as a **third overlay axis alongside theme**, not folded into the theme overlay — otherwise every future Czech-language theme would have to re-derive its own Czech slop lexicon independently, duplicating research and risking drift between themes' Czech quality bars.

### 2.6 Unattended failure behavior of a prompt recipe

At 03:00 with no human present, every skill bundle's "fallback" part (2.2) needs a concrete, bounded behavior rather than an open-ended retry-forever or silent-acceptance default. Durable pattern, applicable regardless of which step (hook/script/shot-list/on-screen-text/negative-check/media-generation) failed:

1. **Classify the failure type** before deciding a response — conceptually: (a) *soft rubric miss* (output produced but failed a self-check, e.g., a banned phrase slipped through, a claim was slightly overstated), (b) *generation refusal or provider error* (the underlying model declined or errored, e.g., content-policy refusal, timeout, malformed output), (c) *hard input problem* (upstream input this step needed was missing or invalid — e.g., no valid research topic ranked highly enough, or brand-truth confidence too low to write a claim-bearing script).

2. **Bounded retry only for (a) and transient (b).** A small, fixed retry ceiling (not unlimited) with a variation instruction on retry (regenerate with an adjusted instruction addressing exactly which rubric line failed, rather than blindly resubmitting the same prompt) — this mirrors standard robust-agent retry design (bounded attempts, informed retry, not identical resubmission). Retrying identically on a refusal or rubric failure without changing anything is a known anti-pattern that wastes budget and usually reproduces the same failure.

3. **Degrade to a lesser deliverable on repeated failure, never invent to fill the gap.** If retries are exhausted: for a copy-layer failure (hook/script/on-screen-text), degrade means falling back to the plainest, most conservative rubric-safe variant already generated earlier in the same run (e.g., use the lowest-risk hook candidate from the initial batch rather than the most creative one) rather than forcing acceptance of a failing artifact. For a media-generation-layer failure (video/image job itself refusing or failing repeatedly), degrade means the run still delivers the **plan/script/shot-list artifacts** (which the assignment explicitly requires to always be produced, generation-optional) marked as "media generation not completed this run," rather than blocking the entire pack or fabricating a placeholder video. This directly matches the assignment's rule that plans/prompts/scripts/shot lists must always be produced even when generation is skipped.

4. **Hard input problems short-circuit immediately, no retry loop.** If the underlying problem is missing/ambiguous brand truth or no adequately-ranked topic, retrying the same generation step will not help — the correct behavior is to stop that artifact's generation early (not spend further budget looping) and mark the item as blocked-on-input, consistent with the assignment's broader cron safety principle of failing closed on ambiguous brand truth rather than guessing.

5. **Escalate via a flag in the run/review package, never a silent drop.** Every degraded or blocked artifact must surface as an explicit, visible line item in the human review package (which asset, which step failed, which failure class, what was substituted or omitted) so a human reviewing in the morning sees exactly what happened and why, rather than a mysteriously thin or missing pack. This is the creative-pipeline-specific instance of the assignment's general cron observability requirement (log enough for debugging unattended failures, exit codes suitable for cron monitoring) applied at the level of an individual prompt/skill step rather than the whole run.

6. **A run-level ceiling, separate from a per-step ceiling.** Bounded retry belongs at both the individual step level (a few attempts on one hook) and the whole-run level (a cap on total degraded/blocked items before the run itself flags as "needs attention" rather than quietly completing with many silent substitutions) — this prevents a systemic issue (e.g., a provider-wide outage, or a broken shared rubric) from producing a full batch of degraded packs that look superficially "complete" to a human skimming a dashboard.

Summary rule of thumb for the recipe designer: **retry small, degrade safely, never fabricate, always surface.**

---

## 3. Decision table

| Decision area | Status | Detail |
|---|---|---|
| Prompt anatomy for hooks/scripts/shot-lists/on-screen-text as a 4-part structure (role/constraint → grounded input → generation+output-shape → self-check) | **Unblocked** → architecture area: content-generation skill design | Adopt as the standard shape for every copy/plan-generation step in the pipeline |
| Negative-prompt layering (engine visual / engine copy-slop / theme / language) as four independent, composable lists | **Unblocked** → architecture area: skill-pack / brand-lock design, config schema for overlays | Config/schema should model these as separate composable layers, not one flat list |
| Brand lock as a structured fact-set (identity/visual baseline/voice/claim boundaries/CTA policy) consumed identically by every downstream step | **Unblocked** → architecture area: brand-truth/spin resolution interface with content-generation | Brand lock is the connective object between brand-spin resolution (out of this brief's scope) and every creative skill |
| Four skill bundles (reels/short-video, ad-creative, UGC, carousel/still) each = instructions+exemplars+rubric+fallback | **Unblocked** → architecture area: skill-pack catalog / prompt-library structure | Ad-creative skill needs a stricter rubric + mandatory spend gate; UGC needs highest human-voice rubric weight |
| Shared-vs-theme-vs-language three-axis overlay boundary with the "touches >1 theme = engine level" placement rule | **Unblocked** → architecture area: theme config structure, overlay composition order (engine core + language overlay + theme overlay) | Directly informs Theme Config Block B/C conceptual contents and multi-theme extensibility |
| Language overlay modeled as its own axis (not folded into theme) so multiple Czech-writing themes share one Czech lexicon/exemplar base | **Unblocked** → architecture area: theme config structure | Prevents duplicated/drifting Czech-quality research per theme |
| Unattended failure classification (soft rubric miss / refusal-transient / hard input problem) with distinct handling per class | **Unblocked** → architecture area: cron/scheduler run-loop design, review-package schema | Review package must have an explicit "degraded/blocked items" section per run |
| Bounded per-step retry + separate run-level degraded-item ceiling that flags the whole run for attention | **Unblocked** → architecture area: cron safety design, observability/exit-code design | Complements assignment's general fail-closed cron principle at the per-artifact level |
| Shot-list dual output shape (N independent self-contained prompts vs one sequence-brief) selected by target model's shot-capability class | **Deferred** → open decision: requires A2's concrete model capability findings (which routes are single-clip vs multi-shot-native, actual continuity/duration limits) before the shot-list skill's routing logic can be finalized | Reconcile in synthesis with A2 |
| Concrete Czech slop-lexicon content and Czech "sounds human" exemplar corpus | **Deferred** → open decision: needs native-Czech-speaker validation / dedicated language research, not assertable from general expertise alone | Recommend a follow-up focused language-QA pass before first Czech-language production run |
| Diacritic/non-ASCII rendering reliability in on-screen burned-in text across candidate video providers | **Deferred** → open decision: provider-specific technical verification, belongs to A2/media-provider research | Flag as a concrete risk for the video pipeline architecture to test early |
| Exact rubric scoring mechanics (numeric threshold vs binary pass/fail vs human-weighted score) | **Deferred** → open decision: belongs to Stage 3/4 systems-architecture synthesis, needs decision on tooling (LLM-judge vs rules-based checks vs hybrid) | Not a prompt-structure question per se; depends on broader architecture choices |

---

## 4. Fact ledger

| Claim | Source | Date | Confidence | Recheck-by |
|---|---|---|---|---|
| Decomposing a generation task into narrow chained steps with an explicit self-check per step improves reliability over one monolithic prompt, generalized here from chain-of-thought/self-critique prompting practice to creative/video-planning tasks | expertise | 2026-08-06 | high (general prompting principle); medium (its specific transfer to video-shot-list planning is reasoned analogy, not directly tested in this brief) | at architecture-lock review, re-validate against any pilot-run evidence |
| Few-shot exemplar pairs ("sounds like us" vs "does not") are an effective mechanism for voice control in production LLM systems | expertise | 2026-08-06 | high | n/a — durable prompting principle |
| Negative-prompt layering (shared vs theme vs language lists) reduces maintenance burden vs one flat list as theme/language count grows | expertise (architectural reasoning, not empirical measurement) | 2026-08-06 | medium-high | revisit once >3 themes exist to confirm the boundary still holds |
| Czech AI-marketing "slop" lexicon differs meaningfully from English and cannot be produced by direct translation of the English banned-phrase list | expertise / general cross-linguistic register knowledge; concrete Czech lexicon items are NOT asserted in this brief | 2026-08-06 | medium (the general claim is high-confidence; any specific Czech phrase list would be low-confidence without native-speaker/language-research validation) | before first Czech production run — recommend dedicated native-speaker language QA pass |
| Non-ASCII diacritics (Czech-specific characters) may render unreliably in some AI video/image models' burned-in text layers | ASSUMED INPUT (from A2) / general pattern seen across generative text-rendering systems, not verified against any specific current model in this brief | 2026-08-06 | low-medium — flagged as a risk to verify, not a settled fact | before committing to any provider for Czech-language on-screen text; verify per A2's model-specific findings |
| Multi-shot-native vs single-clip video model capability distinction changes where continuity/negative-prompt information is injected (per-shot vs once per sequence) | expertise (conceptual/architectural reasoning); which concrete models fall in which class is out of this brief's scope | 2026-08-06 | high for the conceptual distinction; unresolved for concrete model mapping | reconcile with A2's model capability matrix at synthesis |
| Unreadable/dense on-screen text and visual/character drift across shots are common, recognizable "AI slop" quality-rejection triggers | expertise, consistent with assignment's own stated quality-rubric criteria | 2026-08-06 | high | n/a — durable production-quality principle |
| Ad-creative (paid distribution) contexts warrant a stricter claim-safety rubric and mandatory human spend-gate than organic content | expertise, consistent with assignment's non-negotiable constraints (never invent claims; spend human-controlled) | 2026-08-06 | high | n/a |

---

## 5. Sources

- Chain-of-thought / decomposed-reasoning prompting principle: general LLM prompt-engineering practitioner canon (widely documented pattern of breaking a generation task into intermediate, checkable steps rather than one-shot generation) — expertise-derived, no single paper cited.
- Constitutional-AI-style self-critique/self-check-before-output pattern: general practitioner canon of having a model apply a rubric to its own draft before finalizing — expertise-derived.
- Few-shot exemplar-pair grounding ("good" vs "bad" example) for voice/tone control: standard few-shot prompting practice — expertise-derived.
- Short-form video attention/drop-off concentration in the first few seconds, and captions/on-screen text as a major retention and readability lever: general short-form content-marketing practitioner knowledge, consistent with and cross-referenced against the assignment's own Block A framing (hooks in first 1-3s, unreadable text as a rejection criterion) rather than an independent external source.
- Skill-bundle concept (instructions + exemplars + rubric + fallback as the four parts of a reusable "skill") — modeled here as a domain-specific application of the general "agent skill" organizing concept referenced in this agent's own operating brief/system context, adapted to the video/reels/ad-creative/UGC content domain.
- Cross-linguistic register/slop divergence (Czech vs English AI-marketing tells) — general cross-linguistic/sociolinguistic reasoning about register markers not transferring 1:1 across languages; no specific Czech corpus or study cited — flagged low-confidence for concrete lexicon content, high-confidence for the general principle.
- Model-specific capability facts (which named providers/models are single-clip vs multi-shot-native, diacritic rendering behavior, exact continuity/duration limits): explicitly out of scope for this brief; treated throughout as **ASSUMED INPUT (from A2)** and flagged for reconciliation at synthesis.

---

**Key conclusions (5-10 lines):**
1. Durable prompt structure for video content is a four-part anatomy (role/constraint → grounded input → generation+output-shape → self-check) repeated across hook, script, shot-list, and on-screen-text steps — not a single clever prompt.
2. Negative prompting and brand locks should be layered/composable objects (engine-visual, engine-copy-slop, theme, language) rather than flat lists, to survive multi-theme and multi-language growth.
3. Four skill bundles (reels/short-video, ad-creative, UGC, carousel) each need instructions+exemplars+rubric+fallback; ad-creative needs the strictest claim-safety gate, UGC the strictest human-voice rubric.
4. The engine-vs-theme boundary rule: shared if it would affect more than one theme to change; theme-owned if it's brand-specific voice/ICP/offers/exemplars. Language (Czech vs English) is a third overlay axis, not folded into theme, since multiple themes may share a language.
5. Czech is not a translation pass: its slop lexicon, platform register, and hook-mechanic weighting need native-validated overlays; concrete Czech lexicon content is flagged low-confidence here and needs dedicated language QA before first Czech production run.
6. Multi-shot-native vs single-clip models change shot-list structure conceptually (per-shot repeated continuity anchors vs one sequence-level brief) — concrete model-capability mapping is deferred to A2.
7. Unattended failure handling follows "retry small, degrade safely, never fabricate, always surface": classify failure type, bounded informed retries, degrade to the safest already-generated variant or plan-only output, and always surface degraded/blocked items explicitly in the human review package.
8. Open questions for synthesis: A2's concrete model capability matrix (single-clip vs multi-shot-native, diacritic rendering reliability) and a dedicated native-Czech-speaker language-QA pass are both blocking inputs this brief could not resolve from expertise alone.
