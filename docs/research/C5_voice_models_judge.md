# C5 — Voice, Anti-Slop Judging, and Text-Model Pipeline (Czech + English)

Agent T13, Wave 1 expertise brief. Scope: Stage 3 systems-research items 4 (topic→brand-fit / anti-forced-placement, addressed here as the **spin gate**) and 8 (anti-slop voice control that holds up in production), plus the supporting judge-calibration, eval, and text-model-routing questions that make those two gates trustworthy in an unattended, multi-language, multi-platform pipeline. This is a design-phase, no-code brief: everything below is rubric/process/architecture description in prose and tables, not implementation.

Grounded in the mandatory local inputs: `docs/marketing/Winning Posts from competitors Linkedin.txt`, all four transcripts in `docs/marketing/GojiBerry_YoutubeInspiration/`, `docs/marketing/Gojiberry's 7 Figure GTM Playbook.txt`, `docs/marketing/How Gojiberry went from 1M€ to 3.5M€ ARR in 3 months.txt`, and `docs/marketing/HypeLead Areas GTM_Marketing_Strategie.txt`, all read in full before writing this brief. No web access was used; anything that needs live verification is marked **ASSUMED INPUT**.

---

## 1. What this means for the operator

Every piece of copy the system drafts has to pass through a stack of checks before a human ever sees it in a review package — and if it can't pass, the system does not hide that fact or quietly ship its best attempt anyway. It flags it, clearly, in the package, with a note on what failed and what was tried.

The checks happen in cheapest-first order. First a fast, free word-and-pattern scan catches obvious giveaways (cliché phrases, robotic sentence rhythm, a post that looks suspiciously like one we already wrote last week). Then a smarter AI "judge" reads the draft properly and scores it against a rubric built from real winning posts we studied — not generic internet advice, but patterns pulled directly from posts that actually performed well in this niche. If the judge finds a problem, the system gets one or two bounded chances to fix it with the judge's actual feedback in hand, not a blind retry. If it still fails after those tries, the draft goes into the review package clearly marked "did not pass — needs a human," rather than being force-shipped or silently deleted.

There are actually two separate checks, not one, because two different things can go wrong with a piece of content and they need different fixes. One check asks "does this sound like a real person wrote it, in this language, in this register?" (the voice check). The other asks "does this actually connect a real trend to our offer honestly, or is it a random product mention bolted onto someone else's news?" (the spin check — this is what the assignment calls "good spin vs. bad spin"). A post can sound perfectly human and still be bad spin (forced relevance dressed up nicely), or read a bit clunky while being completely honest and well-connected. Fixing the wrong one wastes a regeneration attempt, so they're kept separate.

The tricky part the operator should know about: a judge that is too strict is its own cost problem, not just an inconvenience. In an unattended overnight run, an overly harsh judge makes everything fail, burns the retry budget on every single post, and floods tomorrow's review queue with false alarms — which trains the operator to stop trusting flags at all. So the judge's strictness gets tuned and monitored like any other production system, using a small reference set of known-good and known-bad examples, checked periodically against what a human reviewer would actually decide.

One honest caveat up front: the winning LinkedIn posts we studied are genuinely great at hooks, specificity, and personal voice — but several of them also use hype language ("just killed manual prospecting," "R.I.P.") and gamified hard CTAs ("comment X and I'll DM you the guide") that this project's own rules explicitly rule out (soft CTAs only, no manufactured urgency, no game-changer absolutism). We are borrowing the craft — how they hook, how they prove things with numbers, how they sound like one person talking to one reader — not the tone or the CTA mechanic. Czech voice rules are structured the same way in this brief, but the actual Czech "words a real Czech professional would never say" list does not exist yet locally and is explicitly parked as an input owed by a parallel research track (B4).

---

## 2. Layered anti-slop gate design

Design principle carried through every layer: **cheapest, most mechanical checks run first; the most expensive, most judgment-heavy check runs last; nothing is ever silently shipped, and nothing is ever silently dropped either** — a failing artifact still appears in the review package, explicitly labeled as failing, with its attempt history attached.

### Layer 1 — Lexicon screen

**Job.** Deterministic string/pattern matching against a maintained banned-phrase and banned-pattern list, per language. Catches: the assignment's explicit seed list ("it's not X, it's Y" clause-shape, "changed the rules of the game" / "game-changer," "here's the thing," "let's dive in," "in today's fast-paced world," corporate-mush vocabulary — seamless, leverage, streamline, unlock, supercharge, elevate, revolutionize — fake-urgency phrasing, slogan-stacking). Also runs a **cross-pack recurrence check**: compares the opening lines and core phrasing of a new draft against a rolling window of the theme's own recently generated artifacts (per platform and language) to catch the system developing its own repeated "house tic" — the same failure mode we observed directly in the exemplar corpus (see Fact Ledger row 3): near-identical opener templates recurring across different authors are themselves a tell of formulaic, ghostwritten content, and our own generator repeating itself across packs would be the same tell in our own voice.

**Cost.** Near-zero — no model call, sub-second, pure text matching.

**Failure mode.** High false-negative rate for anything paraphrased around the literal banned string (a rewritten "it's not really X, more like Y" slips through); risk of false positives if a banned word is banned context-free (e.g. "unlock" used literally, not as marketing mush) — needs light context allowlisting. This layer is a tripwire, not a verdict.

### Layer 2 — Structural heuristics

**Job.** Statistical/typographic fingerprinting that doesn't require semantic understanding: em-dash density, sentence-length variance (very low variance reads as robotic uniform rhythm), listicle-tell overuse (arrow-bullet lists where every bullet is an abstract adjective rather than a concrete noun or number — the winning-post corpus uses arrow bullets constantly, but pairs them with specifics like "71% acceptance rate" or "5,500 messages per day," not vague abstractions, so bullet *density* alone is not the tell; bullet *vagueness* is), repeated sentence-opener patterns, emoji/hashtag over-stacking, passive-voice ratio.

**Calibration source.** These thresholds should be derived from the theme's own curated exemplar corpus (see Section 3), not from a universal arbitrary number. Directly observed in the local exemplar corpus: near-zero em-dash usage, short one-to-two-sentence paragraphs used as a deliberate rhythm device, and heavy first-person narrative framing. A generated draft that falls statistically far outside the corpus's own observed range on these axes is worth a second look; exact numeric cutoffs need a real tokenization/measurement pass over the corpus, which is deferred (see Decision Table).

**Cost.** Cheap — token/sentence-level statistics, no external model call, sub-second.

**Failure mode.** Correlational, not causal. A post can pass every structural check and still be semantically empty slop (structurally human-shaped, content-hollow), or fail a check while being genuinely good, deliberately uniform, punchy writing. This layer is a triage pre-filter that must always be followed by the LLM judge — it should never independently accept or reject on its own.

### Layer 3 — LLM judge

**Job.** Semantic evaluation against the full voice rubric (Section 3) and, as a separate pass, the spin-gate rubric (Section 7). Outputs a structured verdict: pass/fail per criterion, an overall call, and — on fail — a short diagnosis plus a fix category (this is feedback for the *next* generation attempt, not a rewrite the judge performs itself; keeping "judge" and "editor" as different roles avoids a model rationalizing away its own draft's flaws). Design preference: the judge should not be the same call, ideally not even the same pinned model/prompt lineage, that produced the draft — a fresh, independent evaluation context reduces the chance that generator and judge share the same blind spots.

**Cost.** One real model call per artifact per pass — meaningful tokens, real latency (seconds), the first layer in this stack with genuine per-call cost.

**Failure mode.** Two distinct directions with two distinct business costs: a **too-lenient** judge ships slop (reputation risk); a **too-strict** judge triggers unnecessary regenerate loops (token-cost and throughput risk in unattended runs). Both must be bounded — see Section 4.

### Layer 4 — Bounded regenerate loop

**Job.** On judge fail, regenerate with the judge's diagnosis fed back as corrective context (targeted retry, not a blind reroll), up to a hard, configurable cap per artifact. The cap is an architectural requirement regardless of its exact number (deferred to config/tuning): it must exist, be visible in configuration, be counted per artifact (not per pack), and draw down from the run's overall token/cost budget so one stubborn artifact cannot silently consume a disproportionate share of a day's spend.

**Cost.** Multiplies both generation and judge cost by up to (1 + cap) for any artifact that keeps failing — this is the single largest cost-variance lever in the whole text pipeline (see Section 6).

**Failure mode.** Uncapped, this is an unattended-run hazard (infinite loop). Even capped, watch for "regenerate collapse": each corrective pass nudges the model toward blander, more hedged, more judge-pleasing phrasing, which can itself curdle into a new, subtler kind of slop (over-safe, over-generic). Mitigation: log every attempt (not only the final one) into the review package so a human can see the drafting trail, not just the last try.

### Layer 5 — Escalate to review (terminal, never silent)

**Job.** If the cap is reached without a pass, the artifact ships into the review package clearly labeled "did not pass voice/spin gate — needs manual rewrite or discard," with the judge's diagnosis and full attempt history attached. It is not force-shipped as a "best effort," and it is not quietly dropped from the pack either — both of those would hide a real problem from the operator, which conflicts directly with the "unattended runs must be safe... fail closed" and "never auto-publish without approval" constraints in the assignment.

**Cost.** None beyond Layers 1–4.

**Failure mode.** Alert fatigue — if flagged items pile up and operators start ignoring them, the gate becomes theater. Mitigation: track the **flag rate** per theme/platform/language over time as its own health metric (see Section 4); a creeping flag rate is a signal to fix the gate or the generator, not a queue to keep waving through.

---

## 3. English voice rubric — derived from the exemplar corpus

This rubric is built from what the winning posts in `Winning Posts from competitors Linkedin.txt` and the Gojiberry transcripts actually *do*, cross-checked against the assignment's own "voice quality bar" and "what spin means" sections — not from a generic listicle of LinkedIn tips. Each dimension below states the corpus evidence, the pass bar synthesized from it, and the fail smell (including where the corpus itself models something we must explicitly *not* copy).

| Dimension | Evidence from the exemplar corpus | Pass bar | Fail smell |
|---|---|---|---|
| Hook shape (first 1–2 lines) | Declarative claim + immediate personal contrast ("X just killed Y. And I'm never going back."); rhetorical self-question ("Is 1% good? What's good, what's bad?"); reframe hook ("Most people use Claude to write posts. That's 1% of what it can do."). | Opens with one concrete claim or contrast tied to a real event/number, not a scene-setting throat-clear. | Generic scene-setter ("In today's fast-paced world..."), abstract observation with no anchor. |
| Specificity / proof anchoring | Concrete numbers everywhere: "250+ messages/week," "71% acceptance rate," "126 fresh leads," named tools (Instantly, Claude, GojiberryAI), named timeframes ("30 days," "2 hours"), dashboard-refresh moments as literal proof. | Every claim of outcome is tied to a number, a named tool, or a traceable source — never a vague superlative. | "Amazing results," "game-changing performance" with no number or source attached — this overlaps with the spin gate's invented-proof check (Section 7) but the voice rubric flags the *phrasing* of unearned certainty even when the underlying claim later turns out to be sourced correctly. |
| Personal stake / one reader in mind | First-person narrative arc throughout ("I used to spend hours...", "I woke up to this email today..."); admits struggle ("we're really naze en outbound haha"); addresses one implied reader, not a market segment. | Reads as one specific person telling one specific reader something true that happened to them or their brand — not a marketing department addressing "audiences." | Third-person brand-voice plural ("we empower our customers to..."), no admitted friction or specificity of experience. |
| Rhythm | Short sentences, one-thought-per-line paragraph breaks, rule-of-three repetition for emphasis ("No more X. No more Y. No more Z."), near-zero em-dash usage observed across the whole corpus. | Sentence length varies naturally; short punchy lines mixed with a longer connecting sentence here and there; em-dashes essentially absent. | Uniform medium-length sentences throughout (a classic LLM tell), heavy em-dash use, "not just X, but Y" sentence-pattern stacking. |
| Structure / formatting | Arrow-bullet (→) lists are common but always carry concrete nouns/numbers, never vague verbs alone; posts are visually broken into short paragraphs, not walls of text. | Bullet lists, when used, list specific things (features, numbers, named steps) — bullets are a delivery format for specifics, not a way to pad word count with abstractions. | Bullet lists of generic capability adjectives ("seamless," "scalable," "efficient") with nothing concrete under them. |
| CTA — target vs. tone | Corpus CTAs are hard and gamified ("comment X and I'll DM you") — explicitly **not** to be copied as-is; this project's own rule is soft, named CTAs (audit / product page / demo). | Ends with one specific, low-pressure named next step relevant to *this* topic and *this* reader's likely stage — not a generic "learn more." | Manufactured urgency ("only a few spots left"), absolutist hype framing ("this changes everything," "R.I.P. to the old way") — present in several corpus posts and explicitly banned by this project regardless of how well it performed for the original poster. |
| Absence of banned patterns (semantic layer, beyond Layer 1's literal string match) | Corpus is largely free of the assignment's exact banned phrases, but leans on a *different* risk family: hype absolutism and gamified engagement bait. | No literal banned phrase, and no paraphrase-around-the-edges of one (this is exactly what Layer 1 can miss and the judge must still catch). | A rewritten "here's the thing" as "so here's what's actually going on," a rewritten "game-changer" as "this changes the entire game" — same cliché, different words. |

**Design note on borrow vs. reject.** The corpus is high-performing but not automatically rubric-compliant — several of its strongest posts would fail this project's own CTA and hype-language rules if reproduced verbatim (Fact Ledger row 2). The rubric above is written to extract the transferable craft (hook construction, specificity, personal stake, rhythm, honest structure) while explicitly excluding the tone and CTA mechanic that made those specific posts viral. This distinction should be stated to any human reviewer calibrating the judge, so "but the real post did X" isn't used to argue down a legitimate flag.

---

## 4. Judge calibration method

**Golden set construction.** Build a small, deliberately mixed reference set (order of magnitude: dozens of items, not hundreds — large enough to be statistically informative about agreement, small enough that a human can label all of it without it becoming its own bottleneck):

- **Adapted positives** — exemplar corpus posts lightly rewritten to swap in a compliant, soft, named CTA in place of the original hard/gamified one, while keeping the hook, structure, specificity, and personal-stake craft intact. These represent "this is what pass looks like, fully compliant."
- **As-is corpus edge cases** — a handful of real corpus posts left completely unmodified, deliberately included *because* they contain hype language or a hard CTA the rubric should catch. These test that the judge is applying our specific rules, not just pattern-matching "sounds like a proven viral post = pass."
- **Deliberate negatives** — hand-written or lightly modified drafts seeded with banned patterns and forced-relevance spin (trend-dump-plus-random-product-mention), to test both the voice rubric and the spin rubric explicitly.
- **Real borderline drafts** — outputs from early pilot runs where a human reviewer's gut call was genuinely uncertain; these test the rubric's actual edges, which the clean positive/negative cases above cannot do.

**Judge-vs-human agreement measurement.** A human reviewer scores the golden set independently against the same rubric, blind to the judge's verdict. Compute agreement, but break it out **by direction**, not as one blended accuracy number: judge-said-pass/human-said-fail (the dangerous direction — slop ships) versus judge-said-fail/human-said-pass (the expensive direction — wasted regenerate cycles and inflated flag rate). These two error types carry different business costs and should be tuned asymmetrically, not averaged away.

**Threshold tuning.** Where the judge produces a numeric score rather than a flat pass/fail, the pass cutoff should be chosen to minimize the dangerous (slop-ships) error at an acceptable rate of the expensive (over-strict) error — then adjusted per the false-positive economics below.

**Re-calibration cadence.** Re-run the golden-set agreement check whenever the judge prompt, judge rubric text, or judge model/version changes (this ties directly to the version-pinning requirement in Section 5) — a rubric or model change without a fresh calibration pass is exactly how silent drift happens. Also re-sample periodically against real production output, since golden sets go stale as real topics and real brand facts move faster than a fixed test set is refreshed (exact cadence deferred — see Decision Table).

**False-positive economics — the bound that keeps unattended runs safe and affordable.** A too-strict judge in a cron run is not merely "extra caution" — it is a specific, quantifiable cost problem: every artifact that keeps failing pays for (1 + regenerate-cap) generation calls *and* (1 + regenerate-cap) judge calls for zero net quality gain, and then floods the review package with false flags, which is exactly the alert-fatigue failure mode noted in Layer 5. Bounding this:

- Track a **rolling flag rate** per theme/platform/language across recent runs.
- Treat a flag rate meaningfully above what was observed during golden-set calibration as a **judge-health warning** surfaced to the operator as its own signal — distinct from individual per-artifact flags — rather than treating each escalation as an isolated content problem.
- The regenerate cap (Layer 4) is itself the primary circuit breaker on worst-case spend, independent of *why* the judge is failing things — so cap sizing is a false-positive-economics lever, not only an infinite-loop guard.
- When launching a new theme or a new language pair with limited golden-set data, prefer starting the threshold slightly lenient and tightening once real judge-vs-human agreement data accumulates. An under-strict judge in the early days costs a bit of extra human-review attention; an over-strict judge in an unattended cron context costs hard tokens and throughput that compounds silently until someone notices the bill or an empty-looking review queue.

---

## 5. Eval / regression concept

- **Fixed eval set.** A frozen subset of (or superset built the same way as) the golden set, never used for prompt-tuning inspiration — only for measuring. Every candidate prompt or model change is run against this frozen set before rollout, comparing pass rate, human-agreement rate, and token cost against the last known-good version.
- **A/B on golden topics.** For ambiguous eval-set results, run old and new prompt versions across the same set of real or golden topics, blind-mix the outputs for a human reviewer (reviewer doesn't know which version produced which draft), and let human preference plus judge-agreement decide. Avoid the circular trap of letting the judge grade a change to its own grading rubric without any human check in the loop.
- **Human spot-check cadence.** Even after a change passes eval, keep a standing lightweight human spot-check on a small percentage of live production packs on an ongoing basis (exact percentage/frequency deferred), specifically because golden sets and real topics/brand facts drift at different rates.
- **Prompt + model version pinning per pack.** Every artifact in every review package should carry, as metadata, which prompt version and rubric version drafted and judged it, and which model/version string ran each role. This is what makes "did the last change actually help" answerable in an audit months later, and it is also the precondition for the re-calibration cadence in Section 4 (you cannot know a judge needs re-calibration if you do not know which judge version is live against which theme right now).

---

## 6. Text-model routing (Czech vs. English, tiering, cost sizing)

**Model-choice axes.**

- *Language quality axis.* Frontier LLM families have historically shown uneven quality across languages, with English typically the highest-resourced and most fluent, and lower-resource languages (Czech among them) historically trailing on idiom-naturalness and fluency — though this gap narrows with each model generation. This is a durable industry trend; which specific current-generation model is strongest for Czech right now is **ASSUMED INPUT** requiring live verification, not something this expertise-only brief can certify. The durable, non-assumed conclusion: plan for an explicit per-language model-routing decision — do not assume one model serves both languages equally well, and do not assume the English-side model choice transfers to Czech by default.
- *Structured-output reliability axis.* The judge role and any machine-parsed metadata (pass/fail flags, diagnosis fields, version tags) need a model that reliably follows an output contract every time in an unattended run. This is a separate axis from raw prose elegance — a model can write beautiful copy and still wobble on strict formatting, or vice versa. Recommendation: weight structured-output reliability higher than prose elegance specifically for the judge role; weight prose/voice quality higher for the generator role. These may or may not end up being the same model — that should be an explicit, revisitable choice, not an assumption.
- *Draft-vs-final tiering.* Use a cheaper/faster model tier for bulk first-draft generation across the many language×destination×variant combinations, and reserve a stronger/pricier tier for the final polish pass and for the judge itself. Cheap-model breadth plus expensive-model depth is a durable cost-control pattern independent of which vendor happens to be cheapest this quarter (exact vendor/pricing: **ASSUMED INPUT**).

**Order-of-magnitude cost math (illustrative, not a committed budget — every specific figure below is ASSUMED INPUT).**

| Cost driver | Illustrative order of magnitude | Why it matters |
|---|---|---|
| Draft artifacts per pack | 2 languages × up to 6 destinations × ~2 sub-assets per destination (e.g. caption + short script) ≈ 24 first-draft generation calls | This is the multiplier the whole pipeline scales from; adding a destination or a language doubles/adds linearly here. |
| Tokens per generation call | ~2,000 input (theme config, brand-truth snippet, research angle, a few exemplar few-shot lines) + ~600 output per short-form asset | Longer for carousels/video scripts, shorter for a single tweet — average used for order-of-magnitude only. |
| Tokens per gate pass (spin + voice, LLM layers only) | ~3,000–4,000 combined per artifact per pass (lexicon/structural layers cost ~0 tokens) | Two LLM gate passes per artifact roughly matches or slightly exceeds the generation cost itself. |
| Regenerate multiplier (worst case) | Up to 3× (1 initial + up to 2 regenerates) on both generation and gate cost | The single largest cost-variance lever in the whole text pipeline — this is exactly why Section 4's false-positive economics is a first-order cost control, not polish. |
| Resulting pack range | Roughly 140,000–150,000 tokens per pack best case (no regenerates) up to roughly 400,000–450,000 tokens per pack worst case (every artifact hits the regenerate cap) | Order of magnitude: "a few hundred thousand tokens per pack," dominated by whether the regenerate loop fires, not by base drafting cost. |

At illustrative blended pricing (low-single-digit dollars per million tokens for a mid-tier model — **ASSUMED INPUT**, market-dependent), a few hundred thousand tokens per pack lands in a cents-to-low-single-dollars range for text alone, before any image/video generation spend (a separate, likely much larger cost center owned by the visual/video pipeline brief). The qualitative conclusion — regenerate-loop governance dominates text-pipeline cost variance far more than base model choice does — is high confidence even though the specific numbers are illustrative.

**Judge robustness as a multi-model consideration.** Consider periodically cross-checking a sample of judge verdicts with a second, different judge model as a lightweight "judge-of-the-judge" spot check, to catch a single judge model's systematic blind spot (e.g., reliably missing one specific banned-phrase family). This is a durable eval-engineering practice (ensemble/cross-model agreement checking as a way to surface single-model blind spots), not a specific vendor recommendation.

---

## 7. Spin gate — distinct from the voice gate

**Why it must be separate.** A perfectly human-sounding, well-rhythmed paragraph can still be bad spin — forced relevance dressed up in great prose. Conversely, an honest, well-anchored, naturally-connected point can read a little clunky and still be good spin. Folding both checks into one rubric forces a single prompt to hold two unrelated failure taxonomies, which raises both false-negative and false-positive risk in the judge, and — more importantly — a spin failure and a voice failure need *different fixes*: a spin failure needs a different angle or a different resolved brand-truth fact, not a rewording; a voice failure needs a rewording, not a new angle. Feeding the wrong fix back into the regenerate loop (Layer 4) wastes an attempt.

**Where it sits in the pipeline.** Two checkpoints, not one:

1. **Angle-level pre-check**, immediately after brand-spin resolution and before full copy drafting begins. Cheap (operates on the short angle/brief, not the finished asset) and catches forced relevance before any drafting tokens are spent on the wrong idea.
2. **Artifact-level post-check**, run alongside (not instead of) the voice judge pass on the finished draft. Catches spin drift that crept in during drafting — e.g. a soft, hedged mention in the brief becoming a confident, unhedged claim by the time the copy is written.

**Spin gate criteria, operationalized from the assignment's "what spin means" section:**

- **Real topic anchor.** The artifact must reference a specific, verifiable external topic/event/pain traceable to a logged research source from the topic-extraction stage. No traceable source → fail. This blocks the model from inventing a generic "trend" out of thin air.
- **Natural connection test.** Two-sided check: (a) delete the offer-mention paragraph — does the rest still read as a genuine, complete point about the topic on its own? If yes, the bridge likely feels earned. (b) delete everything except the offer-mention — is it specific to *this* topic, or could it be pasted onto any unrelated trend with no edits? If it could be pasted anywhere, that is the trend-dump-plus-random-product-mention smell the assignment names explicitly as bad spin.
- **No forced relevance.** The angle must already clear the topic-ranking pipeline's brand-fit threshold (virality × brand fit × freshness, per the assignment's List A ranking intent) before it is allowed into drafting at all; the spin gate re-validates that the threshold wasn't gamed by an overly generous upstream scorer.
- **No invented commercial proof.** Every number, quote, client name, or metric in the artifact must trace to the resolved brand-truth ledger (config + MCP + public verification) or to a cited external source. Anything untraceable is a hard fail — not a candidate for a regenerate-and-hope retry, since inventing a commercial fact is a policy violation (per the assignment's "never invent" constraint), not a style miss. This should escalate rather than loop.
- **CTA target correctness.** Confirms the closing next step matches the theme's configured CTA policy (the right *named* next step for this specific offer/pain pairing) — a companion check to the voice rubric's CTA *tone* check in Section 3; spin gate owns "is this the right CTA," voice gate owns "is this CTA phrased softly."

---

## Decision table

| Decisions unblocked → architecture area | Decisions deferred → open decision |
|---|---|
| Five-layer anti-slop pipeline (lexicon → structural → LLM judge → bounded regenerate → escalate-to-review), never-silent-ship principle → feeds Stage-4 "voice + claim-safety enforcement by design." | Exact banned-phrase lexicon size, maintenance ownership, and update cadence over time. |
| Spin gate as architecturally distinct from voice gate, with angle-level pre-check + artifact-level post-check → feeds "brand-truth/spin architecture" and "review package contents." | Czech slop lexicon and "phrases Czech professionals never say" phrase bank — owned by B4; blocks full Czech rubric population until delivered. |
| English voice rubric authored now from the local exemplar corpus, usable immediately as rubric content and judge few-shot context → feeds "voice + claim-safety enforcement" and registers the exemplar corpus as a first-class theme asset in "theme config conceptual contents." | Exact numeric thresholds: regenerate cap count, flag-rate ceiling, golden-set size, human spot-check %/cadence, judge pass-score cutoff — all need real pilot-run data before locking. |
| Golden-set + human-agreement calibration method, with asymmetric tuning of the two judge-error directions → feeds "risks, failure modes, mitigations" and the eval/regression tooling area. | Specific model/vendor choice per language and per role (draft vs. judge vs. final-polish) — needs a current, web-verified comparison; explicitly out of this expertise-only brief's scope. |
| Draft-vs-final model tiering and a distinct judge-model framing as a durable cost/quality pattern → feeds media/text provider architecture and the per-artifact version-metadata requirement. | Whether a cross-model "judge-of-the-judge" ensemble check is worth its added cost vs. a single well-calibrated judge — needs pilot false-negative-rate data first. |
| Prompt/model version pinning as a required per-artifact metadata field → feeds "conceptual run/review package contents" and makes the re-calibration cadence enforceable. | Absolute token/cost budget ceiling per pack/day — a commercial/economics decision (value per pack), not a prompt-engineering call alone. |
| Regenerate cap and per-run token/cost budget as first-class cost/safety controls → feeds "cron/scheduler architecture," "budgets," "risks/mitigations." | Exact re-calibration trigger for the judge (time-based vs. pack-count-based). |
| Cross-pack phrase-recurrence check (house-style-tic detection) added to the structural heuristic layer → feeds anti-slop gate architecture. | Structural-heuristic numeric thresholds (em-dash rate, sentence-length variance bands, etc.) — need a real tokenized measurement pass over the exemplar corpus, not just qualitative observation. |

---

## Fact ledger

| Claim | Source | Date | Confidence | Recheck-by |
|---|---|---|---|---|
| Winning LinkedIn posts in this niche show near-zero em-dash usage, short fragment-heavy paragraphs, first-person narrative framing, and concrete quantified proof as consistent hook/rhythm patterns. | Corpus file: `docs/marketing/Winning Posts from competitors Linkedin.txt` | Corpus undated (collected 2026) | High — directly observed in the file | Re-derive if/when the theme's exemplar corpus is refreshed with new posts |
| Several corpus "winning" posts use hype/absolutist language ("just killed," "R.I.P.," "ended the grind") and gamified hard CTAs ("comment X and I'll DM you") that would fail this project's own soft-CTA / no-manufactured-urgency rules if copied verbatim — technique should be borrowed, tone/CTA mechanic should not. | Expertise synthesis, cross-referencing the corpus file against `HypeAgentSocials_InstructionsAssignment.md` "Voice quality bar" section | 2026-08-06 (this brief) | High — direct textual comparison | Re-validate whenever the assignment's CTA policy changes or new exemplars are added |
| Near-identical post templates recur across different named authors in the corpus (e.g. a "prospecting is dead, Claude proved it" template repeated with only the bracketed tool name changed across at least three posters) — evidence of an affiliate/ghostwritten template network, and a directly observable "house style tic" recurrence tell. | `docs/marketing/Winning Posts from competitors Linkedin.txt`; corroborated by the "Real Posts From The Campaign" list in `docs/marketing/How Gojiberry went from 1M€ to 3.5M€ ARR in 3 months.txt` | Corpus undated (2026) | High — direct observation | Durable structural observation; no recheck trigger needed |
| Gojiberry's own growth agency explicitly used an LLM (Claude) to extract recurring hooks/structures/angles/lead-magnet formats from a curated corpus of best-performing niche posts as an input to content strategy, rather than asking the model to write from a blank page — a direct real-world precedent for exemplar-corpus-driven prompt design. | `docs/marketing/How Gojiberry went from 1M€ to 3.5M€ ARR in 3 months.txt`, Step 1 | Undated (2026 campaign write-up) | High — explicit process description in source | None |
| Gojiberry's founder describes authoring non-English (French) posts by dictating to ChatGPT by voice and having it translate/correct into the target language — i.e., in their own stated practice, non-English copy was produced via translation-of-dictation, the opposite of this project's D-02 "never translation, each language first-class" mandate for Czech. Noted as a contrast to avoid, not a method to copy. | `docs/marketing/GojiBerry_YoutubeInspiration/GojiBerry_Reddit_01.txt`; corroborated in `GojiBerry_90_Day_Playbook.txt` | Transcript undated (2026) | High — explicit quote in source | None (durable contrast note) |
| No finished-voice Czech marketing exemplar exists in the local corpus; the one Czech-language local artifact is informal internal planning shorthand, not polished B2B voice, and cannot serve as a Czech rubric calibration corpus. | `docs/marketing/HypeLead Areas GTM_Marketing_Strategie.txt` (direct inspection) | File undated | High | Re-check once a genuine Czech exemplar corpus is sourced (owned by B4 per assignment's theme-config routing) |
| LLM output quality (fluency, idiom-naturalness, structured-output reliability) varies by language and model family, with English historically the best-resourced/highest-quality language across most frontier families; specific current-generation model-vs-Czech rankings are not verifiable without live web access. | Expertise / durable ML-industry canon | N/A (durable trend) | Medium — trend is durable, current specific rankings are not verified | Before locking cs-vs-en model routing — needs live, dated model comparison (**ASSUMED INPUT**) |
| A too-strict LLM judge in an unattended (cron) run causes bounded-but-costly regenerate-loop cost multiplication plus review-queue flooding — a distinct failure mode from "judge misses real slop," with a different business cost (token/throughput vs. reputation/quality risk), warranting asymmetric tuning. | Expertise-derived (standard LLM-judge/eval engineering practice), cross-referenced with the assignment's "unattended runs must be safe... fail closed" constraint and its cron budget-cap requirement | 2026-08-06 (this brief) | High — well-established eval-engineering pattern | Re-validate thresholds after the first pilot run's real false-positive rate is measured |
| Order-of-magnitude token volume per content pack (2 languages × up to 6 destinations × sub-assets × gate passes) lands roughly in the hundreds-of-thousands-of-tokens range per pack in a worst-case regenerate-cap scenario, making regenerate-loop governance the dominant cost-variance lever in the text pipeline. | Expertise-derived illustrative arithmetic in this brief (Section 6) | 2026-08-06 (this brief) | Low-medium on exact figures, high on the qualitative conclusion | Replace illustrative token/price assumptions with real figures after the first pilot run and model/vendor selection |
| The assignment's own banned-pattern seed list is largely absent from the winning-post corpus, while the corpus carries a different genre-specific risk family (hype absolutism, gamified hard CTAs, template recurrence) — meaning a lexicon built only from the assignment's seed list would miss a theme's own genre-specific risk, so each theme's banned-lexicon should extend beyond the seed list using its own exemplar corpus, not stay fixed and universal. | Comparative reading of `HypeAgentSocials_InstructionsAssignment.md` ("Voice quality bar") against `docs/marketing/Winning Posts from competitors Linkedin.txt` | 2026-08-06 (this brief) | High | Re-derive whenever a new theme's exemplar corpus is onboarded |

---

## Sources

**Local corpus (read in full, mandatory inputs for this brief):**
- `docs/marketing/Winning Posts from competitors Linkedin.txt` — primary English (and some French) exemplar corpus; direct source of the voice rubric in Section 3.
- `docs/marketing/GojiBerry_YoutubeInspiration/GojiBerry_ColdEmail_01.txt`
- `docs/marketing/GojiBerry_YoutubeInspiration/GojiBerry_Reddit_01.txt`
- `docs/marketing/GojiBerry_YoutubeInspiration/GojiBerry_90_Day_Playbook.txt`
- `docs/marketing/GojiBerry_YoutubeInspiration/GojiBerry_0_to_1_Mil.txt`
- `docs/marketing/Gojiberry's 7 Figure GTM Playbook.txt`
- `docs/marketing/How Gojiberry went from 1M€ to 3.5M€ ARR in 3 months.txt`
- `docs/marketing/HypeLead Areas GTM_Marketing_Strategie.txt` — read in full; noted as informal Czech planning shorthand, not a Czech voice exemplar.
- `HypeAgentSocials_InstructionsAssignment.md` — "Voice quality bar" and "What spin means" sections drive the entire gate design and rubric structure in this brief.

**Durable canon (expertise-derived, no external citation available or needed — standard, stable practice in LLM prompt engineering and evaluation):**
- Layered-defense design for content-safety/quality gates (cheap deterministic filters before expensive model judgment) is standard production LLM-eval practice, not specific to this project.
- Golden-set construction, human-vs-model agreement measurement, and asymmetric error-cost tuning are standard evaluation-methodology practice for LLM-as-judge systems.
- Draft-tier/final-tier model routing for cost control, and separating "best writer" from "most reliable structured-output follower" as distinct model-selection axes, are durable prompt-engineering patterns independent of any specific current vendor.
- Cross-model ensemble judging as a way to surface a single judge model's blind spots is a known eval-engineering practice.
- All specific model names, current-generation language-quality comparisons, and token pricing are marked **ASSUMED INPUT** throughout this brief and require live, dated web verification before being used to lock a routing decision.
