# R2 — AI Pipeline Technical Feasibility Review

*Wave 4 independent review. Reviewer R2 (AI pipeline feasibility). Date 2026-08-06. Subject: `docs/architecture/ARCHITECTURE_PLAN.md` (Wave 3b assembly) judged against the documented evidence in `docs/research/` and the binding rows in `docs/architecture/DECISION_LOG.md`.*

*Stance: adversarial. The question is not "is this well argued" — it is well argued — but "what breaks the week someone actually builds it". No new web research was performed; every objection is grounded in a brief this plan already cites, or in an internal contradiction between two sections of the plan itself.*

---

## 0. How this review was conducted

Deep-read: §1 (orchestration), §3.1–§3.2 (identical mix), §4 (video pipeline), §5 (providers), §6 (brand truth), §8 (cron, ledgers), §11 (modes and gates), §12 (pack), §14 (gates), §15 (risks), §17 (phases), Appendix A (traced topic). Cross-checked against A2 §2.1–§2.11 and its fact ledger, A4 §2.1–§2.9 and U1–U12, C1 §1–§5, C3 §2.1–§2.8, C5 §2–§7, C6 as summarised in the plan's own citations, and B3 as re-derived at D-22.

Three things this review deliberately does **not** re-litigate: the operator's W2.5-4 identical-mix decision (binding), the Python stack (W2.5-5, binding), and Higgsfield's exclusion (W2.5-6, binding). What is fair game is whether the architecture that *follows* from those decisions can actually be built.

Two general observations before the findings. First, the plan is unusually honest about media money and unusually silent about text money — the asymmetry is the single largest structural problem in it. Second, the plan repeatedly states a correct principle in one section and then violates it in another section or in its own worked example; those internal contradictions are where the blockers cluster, because they are the places where two engineers would build two incompatible things.

**Counts: 4 blockers · 19 majors · 9 minors.**

---

## 1. Blockers

### BLOCKER | §4.1, §5.1, §5.4, §8.11, §10.4, §11.1, §12.1, Appendix A.6 — the text-model layer has no provider architecture, no budget, and no place in the economics

**Claim under test.** §4.1's first economic truth is "**Text is free**, images are cheap, clips are not." §11.1's capability matrix says LLM spend is permitted "within per-run budget caps (§8.11)". §12.1 says the digest's cost forecast reads "from the model registry's current price snapshots".

**What the evidence says.** All three statements fail on inspection.

C5 §6 puts one pack at **140,000–150,000 tokens best case and 400,000–450,000 tokens worst case** (every artifact hitting the regenerate cap), for an assumed 24 first-draft artifacts across two languages, before counting the two LLM gate passes it prices at 3,000–4,000 tokens per artifact per pass. The plan's own volumes are larger than C5's assumption, not smaller: §3.2 enables seven destinations with 2–3 asset types each; Appendix A.5 produces roughly thirteen text artifacts per language per topic; OD-8 and Appendix A.3 put **five ranked topics per run**, with A.3 stating explicitly that "the other four proceed too". That is on the order of 130 text artifacts per run, each passing spin pre-check → spin post-check → claim pass 1 → voice judge → claim pass 2, i.e. **five model-mediated evaluations per artifact on top of drafting**. At C5's own per-pack figures multiplied by five topic packs, a single run consumes roughly 0.7–2.25M tokens; at the plan's recommended three pack runs per week that is roughly **9–27M tokens per month**. C5 §6 further directs that the judge and polish roles use the *stronger, pricier* tier. This is the same order of magnitude as §5.4's own $90–140/month media forecast — and it is entirely absent from the plan.

The supporting architecture is absent too, not just the number:

- **§5.1's role table has no text-model provider role.** Media router, fallback router, TTS provider, assembly engine, direct model-vendor API, Higgsfield — that is the complete list. The system's most frequent external dependency is unnamed.
- **§5.2's model registry is a media registry.** Its record shape (capability flags, price snapshot, licence class, person-generation policy, sunset date, prompt-pattern version, refusal statistics) is video/image-shaped. So §12.1's forecast, which reads the registry, structurally cannot price a text call.
- **§8.11 contains no token or text-spend cap.** Its named knobs are the per-run media budget cap, per-day and per-month caps, the tier ceiling, and the media-bearing-assets-per-run cap. §10.4's money block repeats the same four caps as "budget caps per asset, run, day and month" against media. §11.1's cross-reference to §8.11 for LLM spend therefore points at a cap that does not exist.
- The only text-cost control in the entire plan is §14.2's per-artifact regenerate cap plus §6.7's per-pack claim-retry allowance. C5 §4 is explicit that the cap bounds the *worst case multiplier*, not the *base cost* — and the base cost here is five gate evaluations per artifact across 130 artifacts.

The consequence is not merely a missing number. It is that the plan's central safety claim from §1.5 — "**Cost is computable before the run starts**... a hard upper bound exists in advance" — is only true for media. For text it is unenforced by anything except a per-artifact retry counter, and the operator's first surprise bill will not come from Kie.

**Required change.** (a) Add a **text-model provider role** to §5.1 and either extend the model registry to carry text routes with price snapshots, context limits, structured-output reliability grade and per-language suitability, or introduce a parallel text-route registry — either way the §12.1 forecast must read it. (b) Add **per-run, per-day and per-month text-spend caps** to §8.11 and §10.4, enforced by the same cost gate at the same pre-call boundary as media, and state what happens when they trip mid-pack (the mid-pack cap-hit outcome class already exists and should be reused). (c) Rewrite §4.1's first economic truth: text is *cheap per call and expensive in aggregate*, which is a different design instruction — it still justifies hook overgeneration, and it no longer justifies leaving the gate stack unbudgeted. (d) Extend §5.4's economics table and Appendix A.6's spend table with a text row computed from C5 §6's ranges, so the pack economics stop being a media-only figure presented as a pack figure.

---

### BLOCKER | §4.7, §8.5, §8.7, §8.13, §12.2, Appendix A.1/A.7/A.8 — cross-run completion of a partially generated asset has no owner, and the worked example proves it

**Claim under test.** §4.7 and §8.13 make *completed-with-pending-media* a first-class healthy outcome: "a run may legitimately end with jobs still pending" and "the first phase of every run adopts pending tasks and drains the download queue". Appendix A exits on exactly this class with "1 clip + 1 voice render still rendering" and states that "the next morning's collection run adopts both jobs, re-hosts them in expiry order before submitting anything new, and completes the pack."

**What the evidence says.** Adoption is designed only as far as *download and re-host*. §8.13's state machine ends at `done` for a media-job row. Everything downstream of generation is undesigned for the cross-run case:

- **Assembly is not a unit of work.** §8.7 fixes checkpoint granularity at "one (asset slot × language × attempt), which is exactly one media-job-ledger row and exactly one paid attempt chain". Assembly (§4.2 stage 8) consumes *several* media-job rows to produce one master. There is no ledger row, no state, and no resume semantics for "master M is waiting on clip 2 of 3". Nothing in §8.6's ledger set holds it.
- **Packaging's idempotency key breaks on completion.** §8.5: "Packaging is idempotent by construction, keyed on run id + the set of included asset ids." Completing yesterday's clip *changes that set*. So the adopting run either mutates a prior run's pack in place (destroying the idempotency property the plan asserts) or writes a new pack under its own run id (orphaning the review-decision store rows, which §11.4 keys by run id and asset id, and splitting one topic's review across two folders).
- **The mode and cost context is undefined.** The adopting run may be in a different mode, under a different day's caps, and — per §8.2 — may be a *collection-only* run whose cadence explicitly excludes media spend. Appendix A hands the completion to precisely such a run.
- **Appendix A contradicts itself.** A.1 exits with a clip still rendering. A.5 nonetheless lists a completed 9:16 master per language with derivatives for five destinations. A.7 reports a measured loudness gate at −14.2 LUFS and a burned-in disclosure "on every generated asset in both languages". A.9 has the operator reject "the English 9:16 video master" at 08:20. A master cannot be assembled, mastered, disclosed, derived and reviewed while one of its constituent clips is still generating. The trace does not join at this seam, which is exactly what Appendix A exists to demonstrate.

**Required change.** Introduce **assembly as a resumable unit of work with its own ledger state** (blocked-on-inputs → assembling → assembled → failed), so the media-job ledger's completion can trigger it across runs. Define **pack amendment** explicitly: either the adopting run reopens and amends the originating run's pack (and the review-decision store carries an amendment record), or the plan states plainly that a pending master is packaged as a **plan-only artifact with its completed clips attached** and the assembled master arrives in a later pack under a stated cross-reference. Either is buildable; the current text is neither. Rewrite Appendix A's A.5/A.7/A.9 so the pending clip's master is visibly incomplete rather than silently finished — the appendix is the plan's own seam test and currently it passes a test it should fail.

---

### BLOCKER | §6.7, §6.10, §14.1–§14.3, Appendix A.7 — a claim-gate-pass-2 repair re-enters no gate, violating the plan's own stated principle in its own worked example

**Claim under test.** §6.7 states the principle explicitly: "**Any gate that runs before a rewriting step must be re-run after it.**" This is the whole justification for D-16's double claim pass — the voice gate rewrites, so claim must run again.

**What the evidence says.** The principle is applied in exactly one direction and then broken. §14.3's enforcement ladder for the claim gate is "block → bounded regenerate (fed the specific failing spans and a positive constraint) → downgrade repair → drop". A bounded regenerate at claim pass 2 **is a rewriting step**, and it produces new prose that the voice gate has never seen. The canonical order in §6.10 and §14 is linear — spin → claim 1 → voice → claim 2 → platform — with no loop-back arc drawn or described, and no combined ceiling if one were.

Appendix A.7 then demonstrates the defect as a success story. The claim-2 row regenerates the English LinkedIn post after the voice gate's rewrite reintroduced "we've watched reply rates halve", and records "→ passed. Attempt history is attached to the asset in the pack." The asset that ships is text that passed claim 2 and **never passed the voice gate in its final form** — a Czech or English artifact whose slop-control was performed on a superseded draft. The same hole exists for the spin gate: a claim-2 repair that softens an outcome claim can equally weaken the S-3 connection chain, and S-3 is never re-evaluated.

There is a second, distinct instance of the same hole. §14.3 asserts pass 2 is "the final immutable gate on the exact bytes entering the pack". For a video asset the bytes entering the pack are pixels and audio. §4.4 and §6.8 place the burned-in on-screen text composition **at assembly time**, which §6.10's own ordering puts *after* the cost gate and media generation — i.e. after claim pass 2 has already run. So for every video asset, the claim-bearing surface that §6.8 designates as the sole carrier of claim payload ("all claim payload lives in burned-in on-screen text composed at assembly time from verified strings") is composed after the final claim gate closes. "Composed from verified strings" is not sufficient: composition creates juxtaposition, and a verified figure placed beside a verified label can assert something neither string asserts alone — precisely the "300% ROI graphic" case §6.7 names as the artefact type that escapes text-only checking.

**Required change.** (a) Define the **repair re-entry rule** explicitly and cap it: a claim-2 regenerate re-enters the voice gate and the spin post-check, with a single combined per-artifact repair ceiling counted across all gates, and exhaustion routing to the downgrade-repair variant rather than to another lap. (b) Add a **post-assembly claim pass over the composed overlay string set** (deterministic classes only is sufficient — every overlay string is known text, so this is cheap), or state as a binding constraint that overlay composition may only place pre-verified strings in pre-verified template slots with no cross-slot juxtaposition permitted, and make that a checkable assembly rule. (c) Correct Appendix A.7 to show the re-gate.

---

### BLOCKER | §5.6, §8.13, §12.2, §14.6, D-20, R-08 — the provenance record's core field is not evidenced as observable, and it is a publish-gate precondition

**Claim under test.** D-20 and §14.6 make the per-asset provenance record a **publish-gate precondition**, and define its first field as "**delivered route identity and version**", resolved after completion because the router may substitute a model with a different rights class. §5.6 and §8.13 assert the media-job ledger "records requested route, aspect and resolution alongside delivered values".

**What the evidence says.** A2 fact-ledger row 6 documents the substitution behaviour precisely: "silent model-fallback on content review; fallback forces 16:9, no 1080p endpoint". A2 §2.7 restates it as "the delivered artifact may come from a different model than requested" and instructs that "the router must record which model actually rendered" — where "the router" is *our* abstraction, i.e. an obligation on us, not an observed provider capability. **Nowhere in A2 is a delivered-model-identity field in the provider's response evidenced.** The word "silently" in the source finding is doing exactly the work it appears to do: the substitution is detectable only by its *side effects* (forced 16:9, absent 1080p), not by a reported identity.

So the plan makes a field mandatory at the publish gate that the evidence does not show can be filled. Worse, the field it *can* fill (aspect and resolution mismatch) is the one the plan treats as secondary. The consequences chain: no delivered identity → no licence-class resolution → §5.3's rights-class axis has nothing to read → §5.6's "the real control is the per-asset upstream licence snapshot" has no input → the publish gate blocks, correctly and permanently, on every substituted asset with no defined disposition. R-08's operator-visible symptom ("a visible 'delivered ≠ requested' note on the asset, with the substituted route named") names a route the system may have no way to name.

**Required change.** Downgrade the provenance record's model-identity field from *asserted* to *best-effort with a defined inference rule*: record delivered identity when the provider reports it; otherwise record `substituted — identity unknown`, inferred from the documented substitution signature (aspect forced to 16:9, high-resolution endpoint unavailable, or any delivered-versus-requested divergence). Define the **publish-gate disposition for unknown rights class** — the honest one is that an asset whose renderer cannot be identified is not publish-ready and degrades to plan-only with the reason attached, which is consistent with §5.7's "no rung silently produces a worse asset". Add "does the response name the rendering model" to the Phase-0 router checklist alongside the manual terms-of-service pull (R-27), because this single unverified fact gates the publish path.

---

## 2. Majors

### MAJOR | §4.2, §4.6, §4.9, §10.4 — the keyframe-acceptance rubric, the plan's single most important economic control, is undefined for unattended runs

**Claim.** §4.1: "The keyframe is the approval unit... This is the single most important economic control in the system." §4.2 places `[KEYFRAME ACCEPTANCE]` as "the approval event that unlocks clip spend". §10.4's knob makes the policy "human in interactive; **rubric-automatic within caps unattended**".

**Evidence.** No such rubric exists anywhere in the plan. The only rubric named is the "asset QA rubric (machine)" at §4.2 stage 9, which runs *after* assembly on finished media, and whose thresholds are a per-theme knob with no content. The criteria a keyframe acceptance would need are all derivable from cited briefs but none are stated: brand-colour and composition lock (A2 §2.5's stated rationale for keyframe-first), absence of accidental legible gibberish text (A4 §2.6 QA hook, and mandatory given the model-rendered-text ban), safe-box compatibility with the ≈900×1400 box, person-policy compliance before an i2v submission burns an attempt on a refusal, and glyph-free framing for the language-neutral requirement. An unattended run therefore auto-approves the $0.04 decision that authorises the $0.30–$1.35 spend using an unspecified test.

**Required change.** Specify the keyframe-acceptance rubric as a named artifact with its check list and its per-mode thresholds, and state its failure disposition (reject → regenerate within the keyframe variant count → degrade the slot to plan-only). It cannot remain a knob with no defined content when §4.1 calls it the system's most important control.

---

### MAJOR | §4.4, §5.2, D-13, Appendix A.6 — the "text-capable image route" contradicts the ban on model-rendered message-bearing text, and is paid for anyway

**Claim.** §5.2's registry contents include "a text-capable image route for finals carrying type"; D-13 names it for "text-carrying finals"; Appendix A.6 buys two such images per pack at the premium rate.

**Evidence.** §4.4 states the opposite rule in the same document: "**All message-bearing on-screen text, in both languages, is applied post-render**... Generative models are never asked to render message-bearing copy; in-model text is permitted only as incidental English set dressing carrying no message." A4 U5 and A4 §2.6 make this binding, and D-24 adopts it. A2's justification for the premium route (§2.2) was explicitly that "half of all assets carry Czech on-image text (diacritics are where weaker models produce garbage glyphs)" — a rationale that A4's post-render policy deletes entirely. The two decisions were taken in different briefs and never reconciled at assembly. The residue is a live spend: Appendix A.6 pays $0.18 per pack for a capability the plan forbids using.

**Required change.** Resolve in A4's favour (the post-render policy is the safer and already-binding one) and either remove the text-capable route from the v1 registry or re-justify it on non-text grounds (if it is genuinely better at typographic *layout space* — clean negative space for post-render overlay — say that, because it is a different and defensible reason). Remove the premium line from Appendix A.6 or relabel it.

---

### MAJOR | §3.2, §4.4, §4.5, Appendix A.6 — the carousel-to-reel recipe needs 9:16 slide backgrounds that neither the aspect policy nor the budget provides

**Claim.** §3.2: "Two visual master formats cover nearly all of it — 1080×1350 in 4:5 for feed stills and carousels, and 1080×1920 in 9:16 for all vertical video... Producing those two masters and deriving the rest by **layered re-composition — not by cropping** — is the whole visual production strategy." §4.5: carousel-to-reel "is the cheapest reel per asset because it **reuses already-generated slide art**".

**Evidence.** Layered re-composition works for *overlays* because we composite them (A4 §2.7). It does not work for the **generated raster background** underneath. A 1080×1350 generated slide background cannot fill 1080×1920 without cropping (banned), upscaling with crop (same thing), padding (never mentioned), or outpainting (A4 §2.7 defers it as a cost-and-artifact-risk optional tier). So the Czech default recipe — which under W2.5-4 now serves TikTok, Reels *and* Shorts — requires a second, 9:16 slide-art set that Appendix A.6 does not buy: it buys nine EN slide images and four new CS images, with no vertical set for either language. At nine slides per language that is roughly $0.36–0.47 per language per pack unaccounted for, on the recipe the plan calls the Czech workhorse.

**Required change.** State the slide-art aspect policy explicitly. The cheapest correct answer is to **generate slide backgrounds at 9:16 and derive the 4:5 carousel by re-composition downward** (a vertical raster contains a 4:5 crop-free region if the template is designed for it), which makes the reuse claim true rather than aspirational. Whichever answer is chosen, add the line to Appendix A.6 and to §5.4's economics.

---

### MAJOR | §4.2, §4.5, §6.8 — carousel-to-reel's narration source contradicts script-lock

**Claim.** §4.2 makes the script stage 3 and the slide list stage 4, with SCRIPT-LOCK declaring "the script is the artefact of record". §4.5, following A4 §2.2, says the recipe produces "either a narration track **from the slide copy** or a subtitles-plus-music variant".

**Evidence.** These are two different artefacts of record. If narration derives from slide copy, then slide copy is the claim-gated script and the stage-3 script is redundant for this recipe; if the script is primary, slides are a rendering of it and A4's "narration from the slide copy" is wrong for this pipeline. §6.8 rule 1 ("spoken content is generated only from claim-checked script text") cannot be enforced against an ambiguity about which text is the script. The recipe is also missing: whether the 7–13 slide count is the same set as the 5–15 slide carousel §10.4 caps, per-slide Ken Burns direction rules (A4 warns one transition style per template to avoid a slop look, but says nothing about motion direction consistency), and where the burned-in AI disclosure sits relative to the ≈900×1400 safe box on a slide already carrying headline plus support line.

**Required change.** Declare the script primary for both recipes and derive slide copy from it, or declare slide copy the script for CS-B and route it through the identical claim gating. Add the missing recipe parameters to §4.5 — this is the Czech default and it is currently specified to roughly the depth of a paragraph in A4.

---

### MAJOR | §4.4, §4.8 — Czech caption timing depends on capabilities the fallback provider is not evidenced to have, and the fail-closed variant has no timing source at all

**Claim.** §4.4: "On the Czech path, text-to-speech-native timestamps remove speech recognition from the caption path entirely." §4.8 rule 5: fail closed to subtitles-only plus music if the Czech voice provider is unreachable.

**Evidence.** A4 §2.3 evidences timestamps for **ElevenLabs specifically** ("the TTS provider can return character/word timing directly (ElevenLabs exposes timestamps)"). The plan's designated cost and fallback tier is Azure Neural (OD-13, §5.1), for which A4 evidences Czech *voices* but says nothing about word-level timing output. If Azure is engaged, the caption path silently falls back to alignment — and A4 §2.3 documents that **Czech is not among WhisperX's default alignment languages** (en, fr, de, es, it) and requires a separately sourced Hugging Face Czech alignment model. That dependency appears nowhere in the plan, nowhere in §17 Phase 0, and nowhere in §5.1's role table. Separately, the subtitles-only fail-closed variant has **no audio at all**, therefore no timestamps and no alignment target — yet §10.4 keeps "caption style and word-level reveal" as a live knob with no statement that word-level reveal is unavailable on that path.

**Required change.** Add "does the fallback TTS tier expose word-level timestamps in Czech" to the OD-13 trial criteria. Name the Czech forced-alignment model as a Phase-0 deliverable if the answer is no. State explicitly that the subtitles-only variant times captions from the slide-timing model and cannot use word-level reveal.

---

### MAJOR | §4.4, §4.8, §6.8, §14.5 — the EN-A recipe's caption/audio divergence is designed to go uncaught, while a free per-asset check exists

**Claim.** §4.4: captions from the script verbatim make "displayed-text accuracy 100% by construction in both languages". §6.8 and §14.5: speech recognition is "a sampled adherence monitor, never a per-asset gate", and §6.8 concedes "script-lock's own honest failure mode is that adherence is a behaviour, not a guarantee: a model may paraphrase or ad-lib."

**Evidence.** For the EN-A recipe (generative clips with **model-native English speech**), a paraphrasing model produces audio that diverges from the script. Caption *text* remains correct; caption *timing*, produced by aligning the authored script against divergent audio, does not — and the viewer sees captions that do not match what is said. §6.8's four-part argument for sampling over gating is sound for *claim safety* (rule 2 drains the audio of claim payload, so drift is non-consequential for truth) but it is not an argument about **quality**, and this is a visible defect on the asset type §3.5 says costs 20–30 minutes of human QA each. A4 §2.3 documents that FFmpeg 8.0 ships a **local Whisper filter** and recommends it for exactly this: "use for QA (does the audio say what the script says?)". The check is free, local, deterministic, requires no network, and is already inside the binary the assembly engine invokes. The plan's cost argument for sampling does not survive that fact.

**Required change.** Make a **local adherence check a per-asset assembly QA item for any recipe using model-native speech**, using the local filter — a similarity threshold between authored script and recognised audio, failing the asset closed to the QA-flag path (which §4.9 already has for the limb-warp class). Keep sampled ASR as the *provider-level* alarm it is designed to be. Restate §4.4's "100% by construction" claim as being about displayed text only, not about audio-caption correspondence.

---

### MAJOR | §3.1, §4.8, §5.4, R-11 — the plan's named structural cost lever is incompatible with the recipe it selects as default

**Claim.** §5.4: "the recommended structural lever is **language-neutral footage plus language-specific overlays and voice added at assembly**, which collapses the video multiplier back toward one — and under the identical-mix rule this lever is doing more work than ever, since the Czech lane's default recipe buys no clips at all."

**Evidence.** That sentence contains its own refutation. The language-neutral-footage lever (A2 §2.11's recommendation, handed to A4) works by **reusing one clip set across both languages** — that is recipe CS-A (generative clips plus Czech TTS). The plan's Czech default is CS-B, which uses **no clips whatsoever**. The lever is therefore not "doing more work than ever"; it is doing no work at all in the default configuration, because there is no shared footage to share. Two distinct cost stories have been merged into one sentence. The plan also never states whether reusing the *English* clip set for a Czech asset is permitted — it would be the genuinely cheapest path and is arguably CS-A-compliant, but it is also the closest thing to the "translation not recipe" failure the six Czech commitments in §3.1 exist to prevent.

**Required change.** Separate the two levers in §5.4 and in R-11: (i) keyframe reuse across languages, which is real and applies to images; (ii) footage reuse across languages, which applies only under CS-A and is currently unused. Then state the policy on English-footage reuse for Czech assets explicitly — permitted, forbidden, or permitted only outside short-form — because it is a live configuration the plan currently neither allows nor bans.

---

### MAJOR | §5.1, §5.2, §5.3 — the ten routing axes cannot express the requests the plan actually makes

**Claim.** §5.3: "A generation request is expressed provider-neutrally on exactly ten axes (A2 §2.9), each mapping to a registry capability flag."

**Evidence.** A2 §2.9's ten axes were derived for *video*. The plan promises asset types they cannot address:

- **TTS is unrepresentable.** The provider is a named role in §5.1 and Appendix A.6 charges $0.02 to it, so it is inside the spend ledger — but there is no axis for voice identity, language, speaking rate, timestamp requirement or output format, and no registry route carrying its price snapshot or rights class. The cost gate, which §4.6 says "reads expected cost from the model registry's price snapshots", therefore cannot price a TTS call.
- **Image requests have no variant-count axis**, despite §10.4's "keyframe variant count" knob (two to three) and hook overgeneration being core to §4.1's economics.
- **No reference-image axis** exists, despite §4.3 naming reference-to-video as the mechanism for product consistency and A2 documenting reference inputs as temporary uploaded files with their own lifecycle.
- **No moderation-strictness or negative-prompt axis**, despite A2 §2.7 documenting aggregator moderation being stricter than upstream and the refusal ladder's first rung being "sanitise-and-rewrite".

**Required change.** Either extend the axis set to cover images, audio and reference inputs (and say so, since §5.3's "exactly ten" is asserted as complete), or state that the ten axes govern video routing only and define the parallel contracts for image and audio routes. Add TTS as a registry route class so the cost gate can price it.

---

### MAJOR | §5.2, §10.4, R-30 — monthly manual price re-verification with lapse-to-degraded is a self-inflicted outage with a plausible trigger

**Claim.** §5.2 behaviour 2: "**A lapsed recheck-by drops a route to degraded, and the router stops selecting it for spend.** Staleness is enforced, not merely reported." Prices are rechecked monthly.

**Evidence.** A2 §2.1.6 recommends exactly this cadence, and it is right to. But A2 also documents that Kie prices live on marketing pages and change without notice (two documented cuts in 2026), and nothing in A2 evidences a machine-readable per-route price endpoint. So the monthly recheck is **manual operator toil across roughly eight routes**, and the enforcement is total: a solo operator who has a busy month arrives at a pipeline that silently stops generating any media, on every theme, with the failure presenting as "everything degraded to plan-only". The plan half-anticipates this with a "recheck-by grace" knob in §10.4 but never defines grace behaviour, and R-30's operator-visible symptom ("a degraded route simply stops being chosen") describes the outage as if it were a benign property. A2's **weekly availability probe** (credit-balance call plus one draft-tier generation) — the cheap automated half of the same design — is not carried into the plan at all.

**Required change.** Define a two-stage lapse: recheck-by lapse first raises a **forecast-confidence warning** with the stale snapshot still usable for a defined grace period, and only then degrades the route. Carry A2's weekly availability probe into §5.2 as a scheduled health run with its own tiny budget line, since it is the automated signal that makes the manual one less load-bearing.

---

### MAJOR | §5.7, OD-23 — the fallback ladder presents an engineering project as an operational rung

**Claim.** §5.7's ladder runs NORMAL → IN-RUN alternate route → DEGRADE to plan-only → MIGRATE to fallback router → MIGRATE to direct vendor API. §5.1 is honest that the fallback router is "**registered, not integrated** in v1".

**Evidence.** Rungs one and two execute inside a run in seconds. Rungs four and five are multi-day builds: a different API surface, different pricing units (A2 documents fal.ai priced per second against Kie's per clip), different async semantics, different rights classes to snapshot, and a re-verification of the ten axes against a surface the abstraction has never been tested against. Presenting them in one ladder implies a continuity that does not exist, and the plan's guarantee — "no rung silently produces a worse asset" — is true but incomplete: the honest statement is that a sustained primary-router outage means **plan-only output for as long as the integration takes**. OD-23 correctly leaves the engagement threshold open, but openness about the trigger does not substitute for honesty about the lead time. There is also no evidence anywhere that the ten-axis abstraction is expressible against the fallback router's documented surface — the abstraction has exactly one implementation and will encode that implementation's assumptions.

**Required change.** Split the ladder into **runtime rungs** and **migration projects**, with an explicit lead-time statement on the latter and a named plan-only interval. Add a paper-level conformance check of the ten axes against the fallback router's published surface as a design-phase or Phase-3 deliverable — it costs an hour and is the only thing that makes "registered" mean more than "named".

---

### MAJOR | §8.5, §8.13, R-09 — `submitted-unknown` has no terminal disposition, and balance-delta cannot supply one

**Claim.** §8.13: a process death between committing the intent row and recording the task id "leaves a **submitted-unknown** state, which is never auto-resubmitted, only reconciled via a balance-delta check against the provider's own credit-balance endpoint".

**Evidence.** Balance delta answers "was money spent". It cannot answer "which task id" — and without the task id the status endpoint (A2's `recordInfo`, keyed by task id) is unreachable, so the artifact is unrecoverable and will be hard-deleted at 14 days. A2 documents no task-listing or task-search endpoint anywhere in its API-shape findings. So the honest terminal state is **paid, lost, unrecoverable** — and the plan never says so, never says what the asset slot does next, and never says whether a fresh attempt under a new deterministic identity is permitted (the "one identity = at most one paid attempt chain" rule in §8.5 suggests not, which would strand the slot permanently). The operator-visible symptom in R-09 covers the divergence alarm but not the stranded slot.

**Required change.** Define the disposition: on a confirmed charge with no recoverable task id, mark the attempt chain `paid-lost`, degrade the asset slot to plan-only with the reason attached, surface it as a named line in the digest, and permit **exactly one** fresh attempt under a new identity only on explicit operator action. State that the window is small (the gap between intent commit and task-id write) but non-zero and unclosable, since that is the truthful characterisation.

---

### MAJOR | §5.4, §8.3, §8.11, §13 — the money-safety design assumes a single spender, and multi-theme is a first-class requirement

**Claim.** §5.6 and §8.13 rely on **balance-delta reconciliation** with an unexplained-spend circuit breaker. §8.11 sets per-run, per-day and per-month caps. §8.3 sets skip-on-overlap via a run lock keyed to run identity, which is "theme identifier + run-date + attempt".

**Evidence.** Balance delta is only interpretable if exactly one process is spending against that balance for the duration of the snapshot window. The lock is per theme. §13 makes multi-theme a first-class capability and §8.2 makes both cadence knobs per-theme, so two themes can legitimately run concurrently — against **one prepaid router balance** (A2: "one balance, one API surface"). Under concurrency, balance delta minus this run's ledger total is meaningless, and the circuit breaker will either fire falsely (halting a healthy run) or mask real unexplained spend. The same defect hits the caps: per-day and per-month caps are per theme, so total spend across N themes is bounded by N × cap with no global ceiling, against a single wallet. §5.4's mitigation — "a separate router key for scheduled runs with a bounded top-up" — does not help, because a key is not a balance.

**Required change.** Either (a) require a **global spend lock** across themes for the media stage plus a global daily/monthly cap alongside the per-theme ones, or (b) require one router sub-account per theme and state that as an onboarding cost in §13.1. Also correct §5.4's wallet-bounding sentence: bounding by wallet requires a **separate account with limited top-up**, which A2's evidence supports and the per-key mechanism does not.

---

### MAJOR | §6.2, §6.4, §6.6 — targeted site verification cannot supply what the precedence table demands, and it hides an unbounded-input model node

**Claim.** §6.6: "**Site verification is targeted, not a crawl**: only the binding facts and CTA URL liveness, a handful of timeboxed fetches per run." §6.4's precedence table assigns the site a verifier role on F-A (identity, "public-facing usage"), F-C (capability statements, "must not contradict") and F-H (claim ledger, "site may invalidate, never add").

**Evidence.** "Must not contradict" and "may invalidate" are **semantic comparisons over arbitrary site prose**, not liveness checks. To make F-C's degrade-to-the-narrower-wording rule fire, the system must read the pages where a contradicting capability statement would live and compare them to the Notion statement. To make F-H's invalidation rule fire, it must do the same for every claim-ledger entry. Neither is a timeboxed liveness fetch, and neither is possible within "a handful". This creates three problems at once: the verification budget is under-scoped for the precedence it must feed; the comparison is an **LLM node with unbounded input** (arbitrary fetched page content) that appears nowhere in §1.5's node inventory and has no failure mode, no token ceiling and no injection posture despite §2.7's careful injection handling for collected content; and the third asymmetry ("silence is not agreement") is only sound if the fetch actually *covered* the page where a contradiction would live — which a targeted budget cannot guarantee, so "not observed" and "did not look" collapse into one another exactly the way §6.4 warns against.

**Required change.** Bound the site-verifier's job to what a targeted budget can honestly do: **liveness, price values, trial terms and offer status** on a configured URL set. Move F-C and F-H site verification either to a configured **verification page set per fact class** (so coverage is declared, not hoped) or out of the per-run path into an event-driven sweep. If the semantic comparison stays, register it as a named LLM node in §1.5 with a token ceiling, a fail-closed-to-not-observed failure mode, and the same quoted-data-never-instructions posture §2.7 applies to collected content.

---

### MAJOR | §6.5 — the confidence band's step-2 score has no defined cutoffs and no path to calibration

**Claim.** §6.5: "**Step 2** — score inside that ceiling across blocking and constraining classes on coverage, corroboration depth, freshness ratio and conflict count." The four bands are then defined by prose preconditions: FULL requires "constraining classes mostly resolved"; PARTIAL applies when "corroboration is thin or some constraining facts are unresolved".

**Evidence.** "Mostly" and "thin" are the cutoffs, and they are the whole difference between a pack that may state trial terms and one that may not. The gate half of the design (step 1) is genuinely binary and implementable; the score half is not. Unlike the judge threshold — which has a golden set, a direction-split agreement measure and a calibration cadence (§14.2) — the band score has **no calibration mechanism at all** and no measurable ground truth, so §0.3's standing rule ("thresholds come from measured run data") has nothing to measure. Two implementers will produce two different band functions, and the operator-facing meaning of PARTIAL will drift silently.

**Required change.** Make step 2 fully deterministic and inspectable: define each band by **counting rules over the fact classes** (for example, FULL requires every constraining class resolved-with-values or resolved-empty, binding facts observed this run or inside the warn window, and zero conflicts; PARTIAL is the remainder above the gate). A counting rule needs no calibration and is auditable in the brand-truth panel §6.5 already specifies. Drop the language of scoring, or state the score's cutoffs and their derivation.

---

### MAJOR | §14.2, §17 Phase 0, Phase 7 — the English golden set and English structural calibration are nowhere, so the judge-health signal cannot exist until Phase 7

**Claim.** §14.2: layer 2 thresholds are "calibrated from the theme's own exemplar corpus"; the flag-rate ceiling is a rolling rate "meaningfully above what golden-set calibration predicted"; §10.4 gives its default as "calibrated from the golden set".

**Evidence.** §17 Phase 0's calibration deliverables are "Exemplar corpora assembled per language. The **Czech** structural-calibration corpus built... The **Czech** judge golden set built." D-34 makes exactly two Czech artefacts the Phase-0 gate. There is **no English golden set and no English structural-threshold derivation pass** named in any phase. C5 §4 requires the golden set for both, and C5 §2 layer 2 is explicit that exact numeric cutoffs "need a real tokenization/measurement pass over the corpus, which is deferred". The consequence is concrete: the English voice gate runs from Phase 2 through Phase 6 — including the eight-to-ten real trial packs and the first unattended runs — with an uncalibrated judge and undefined structural bands, and the flag-rate ceiling has **no predicted baseline to be measured against**, so R-21's detection mechanism does not exist until Phase 7 delivers it. The plan's own Phase 7 acceptance criterion ("a deliberate over-strict judge configuration is detected by it") is unsatisfiable earlier.

**Required change.** Add the **English golden set and the English structural-calibration measurement pass** to Phase 0 alongside the Czech ones, and add them to D-34's gate. If that is too heavy for Phase 0, state plainly in §14.2 that the flag-rate ceiling is inactive until Phase 7 and that the Phases 2–6 judge runs deliberately lenient per C5 §4 — but say it, rather than describing a control that is not yet instrumented.

---

### MAJOR | §12.4, §14.2, §14.7 — there is no eval set and no pre-rollout regression gate, so prompt changes after launch are unmeasured

**Claim.** §14.7 pins prompt-pattern, rubric and model versions per artifact, "which makes 'did the last prompt or model change actually help' answerable months later". §12.4's weekly loop has aggregated rejection reasons inform "prompt-library and rubric refinements", applied by a human.

**Evidence.** C5 §5 specifies three things the plan does not carry: a **frozen eval set** "never used for prompt-tuning inspiration — only for measuring", against which every candidate prompt or model change is run **before rollout** comparing pass rate, human-agreement rate and token cost to the last known-good version; a **blind A/B on golden topics** for ambiguous results, explicitly to avoid "the circular trap of letting the judge grade a change to its own grading rubric without any human check"; and a **standing human spot-check** on a small percentage of live packs. The plan has version pinning, which is retrospective attribution, not regression prevention. Phase 7's acceptance mentions re-calibrating against the golden set *after* a change is applied — which detects drift after it has already shipped into packs. The eval set is a C5 "decision unblocked" item that fell out at assembly.

**Required change.** Add the **frozen eval set** as a named artifact (§14, and a Phase-0/Phase-2 deliverable), and make a pre-rollout eval comparison a **precondition on any prompt-library or rubric change** in §12.4's weekly loop. Add the blind A/B and the standing spot-check percentage as named, deferred-value knobs. Without these, §12.4's weekly loop is an unmeasured edit path into the system's most safety-relevant prompts.

---

### MAJOR | §8.10, §11.3, §14.2, §14.3 — gate-model unavailability is not a fail-closed trigger, and the plan proves it knows better elsewhere

**Claim.** §11.3 enumerates four fail-closed triggers: missing secrets, ambiguous brand truth, policy violation, mode violation. §8.10 gives one blanket rule for model errors: retry with backoff, then "marked incomplete for that one asset rather than fabricating filler".

**Evidence.** None of these covers "the voice judge returned unparseable output" or "the claim gate's semantic pass was unreachable". §14.2's layer 5 handles judge *fail*, not judge *unavailable*. C5 §6 specifically flags structured-output reliability as a distinct model-selection axis for the judge role because parse failures are expected — and the plan adopts the role separation without adopting the failure handling. The asymmetry is visible inside the plan: §2.7 specifies exactly the right behaviour for the brand-fit node — "**If the judgment step cannot run at all** — timeout, outage, budget cap hit mid-pass — the candidate fails closed to monitor-only. It never defaults open." The gate stack has no equivalent sentence. So an unattended run whose judge endpoint is degraded produces a pack of assets that were never semantically gated, labelled "incomplete" at best, presented alongside properly gated ones. The human review gate bounds the exposure, which is why this is major rather than blocker — but §14.2's opening promise ("nothing here is ever silently shipped") is not currently true of the unavailable case.

**Required change.** Add a fifth fail-closed trigger: **a gate that cannot execute fails its asset closed**, with the asset entering the pack under the same "did not pass — needs a human" label as a cap exhaustion, naming which gate could not run. State the deterministic-half fallback explicitly for the claim gate (deterministic classes still run; the pack records that only deterministic coverage was achieved).

---

### MAJOR | §5.2, §5.3, §17 Phase 0 — EU person-generation restriction is treated as a routing axis when it may be an account-level prerequisite

**Claim.** §5.2: the route-policy constraint layer means "a theme author should never have to know that a particular route restricts person generation in Europe: the router refuses to select an ineligible route, and the prompt composer injects the constraint automatically." §5.3 carries person policy as an axis with values no-people, adults-only, region-restricted.

**Evidence.** A2 fact row 23 documents more than a capability flag: Veo person generation in the EU is "restricted to allow_adult", **model-level refusal of named real people**, and "allowlist requests observed for person i2v" — that is, a per-account approval process with a lead time, for a Czech operator, on the default reel workflow. A2 §2.7 names this as "directly relevant to a Czech operator". The plan's design handles the case where an *eligible route exists*; it does not handle the case where **no route is eligible for person-bearing i2v in this jurisdiction**, which for B2B marketing imagery (people in offices, on calls, at desks) is a large fraction of the natural keyframe space. §17 Phase 0 lists identity verification for the ad-library source but not person-generation eligibility for the media router.

**Required change.** Add **"determine person-generation eligibility for this account and region, and submit any allowlist request"** to §17 Phase 0's prerequisites, alongside the router terms pull. Add the no-eligible-route case to §5.7's ladder with its honest disposition (people-free keyframe composition as the default constraint for this theme, injected at prompt composition, or degrade to plan-only).

---

### MAJOR | §6.7, §14.2, §14.3 — two incompatible budgeting units for regeneration, with an undefined interaction

**Claim.** §14.2's voice regenerate cap is "counted per artifact". §14.3 and §6.7: "The **retry allowance is budgeted per pack, not per asset**". §14.1's spin gate has its own one-regenerate-then-downgrade ladder.

**Evidence.** Three gates, three different budgeting units, no combined ceiling, and an explicit coupling between them: §14.3's own rationale for the double claim pass is that a voice regenerate can create a claim failure, which then draws down the pack's claim allowance. So a per-artifact voice cap can drain a per-pack claim budget, and the plan never states which is checked first, whether a pack whose claim allowance is exhausted still permits voice regeneration, or what the per-artifact worst case is across all three gates. R-10 names the voice cap as "the primary circuit breaker on worst-case unattended cost" — but it is only a circuit breaker on one of the three loops, and blocker 3 above shows a fourth, undefined loop (claim-2 repair → re-gate).

**Required change.** Define a **single per-artifact repair ceiling counted across spin, voice and claim repairs**, with the per-pack allowance as a second, outer bound, and state the check order and the exhaustion outcome at each level. This is also the natural place to attach the missing text-spend cap from blocker 1.

---

### MAJOR | §1.5, §14 — the narrow-LLM-node inventory omits most of the plan's actual model nodes

**Claim.** §1.5: "Language models are called as leaf tasks with defined inputs and outputs — *score this candidate against the ICP map*, *write this caption*, *judge this draft against this rubric*". One bounded concession, for "topic ranking and copy drafting".

**Evidence.** The nodes actually specified across the plan are: rules-second brand-fit judgment (§2.7, failure mode specified), hook candidate generation and hook *selection* by rubric (§4.2, selection mechanism unspecified — model or deterministic?), script writing, shot-list and slide-list generation, media prompt composition with route-policy injection (§5.2), spin gate angle-level pre-check, spin gate artifact-level post-check, claim gate semantic pass (twice), voice gate judge (per language, eleven Czech dimensions), corpus-leakage semantic comparison (§6.11 class 11), and the site-contradiction comparison implied by §6.4. That is a dozen node classes, of which exactly one has a specified failure mode. The plan is right that none of them is a planner — the orchestration argument in §1.5 holds and is well made — but "narrow" is asserted for a set that was never enumerated, and §1.5's own knob list names a **polish model role that appears in no stage of the pipeline** (the voice gate is judge-plus-regenerate, not polish).

**Required change.** Add a **node inventory table** to §1.5: node name, owning stage, bounded input, bounded output shape, per-call ceiling, failure mode, and whether internal iteration is permitted. This is the artifact that makes §1.5's cost-computability claim checkable rather than asserted. Delete the polish role or give it a stage.

---

## 3. Minors

**MINOR | §4.6, Appendix A.7 — the illustrative per-run cap is incompatible with the hero tier.** Appendix A uses a $6.00 per-run cap. A2's hero math is $5.63 per language for three quality clips with the 1.5× reject factor. A single hero promotion therefore consumes 94% of the run cap before any images. *Required change:* state that hero promotion carries its own cap dimension rather than competing inside the standard per-run cap, or raise the illustrative figure so it does not model an impossible configuration.

**MINOR | §5.4 — "a separate router key with a bounded top-up" conflates keys with balances.** A2 §2.8 evidences per-key rate limits and IP whitelisting; a top-up limit is an account property. *Required change:* say "a separate router account for scheduled runs", and note that it splits the $50 trial balance.

**MINOR | §3.2, §4.4 — the LinkedIn document carousel's PDF export is unowned.** §3.2 specifies PDF up to 300 pages; §4.4's assembly ownership list ends at "exports the master and its derivatives" and names no document format. *Required change:* assign PDF composition to the assembly engine explicitly, with the Czech-glyph-complete bundled font requirement carried over.

**MINOR | §4.3, §5.3 — mode-specific constraints are not surfaced against the recipe.** A2 fact row 6 records that reference-to-video is fast/lite only and **fixed at 8 seconds**. The plan's duration axis "picks the legal quantum" but §4.3 uses reference mode for product consistency without noting that selecting it fixes shot length, which interacts with the 20–40 second target and shot count. *Required change:* record the mode→duration coupling in §4.3 or in the registry's capability flags as a stated constraint.

**MINOR | §4.7, §8.2, §8.13 — pending media has no expiry countdown and no forced-adoption path when both cadence knobs are off.** Both cadence knobs default off (W2.5-7). A run exiting with pending media may not be followed by another run for weeks; provider media is deleted at 14 days. *Required change:* surface a days-to-deletion countdown per pending job in the digest and the notification, and state that an interactive run also performs phase 0.

**MINOR | §17 Phase 4 — "eight to ten real two-language packs" is ambiguous.** A2's economics define a pack as one topic × two languages; §12 uses "pack" for the run's whole output and "topic pack" for the per-topic unit. Under the trial envelope's $35, the two readings differ by roughly 5×. *Required change:* use "topic pack" consistently in §17 and in §5.4's trial plan.

**MINOR | §6.6, §14.7 — the fact-usage trace implies a prompt-assembly requirement the plan does not state.** Recording "which fact identifiers this topic pack consumed" requires facts to be injected into prompts as an id-tagged set rather than as rendered prose. *Required change:* state that requirement where the trace is specified; it is cheap if designed in and a rewrite if retrofitted, which is exactly the plan's own stated reason for naming such things early.

**MINOR | §4.3 — hero-tier multi-shot bypasses the keyframe approval unit with no cheap preview.** A2 §2.10 justifies the draft tier as the pre-spend motion check; there is no cheap multi-shot preview route in the registry, so the human promoting to hero approves the most expensive spend in the system with the least information. *Required change:* note the absence explicitly so the operator knows the four-cent protection does not apply at hero tier.

**MINOR | §14.2 layer 1 — the cross-pack recurrence check has no defined window or scope in the knob surface.** §14.2 specifies it as "a rolling window of the theme's own recently generated artifacts, per platform and language", and Appendix A.7 fires it on a six-day-old opener, but §10.4 carries no knob for the window length or the similarity threshold. *Required change:* add it to §10.4's list, since it is an always-on check that can block assets.

---

## 4. Verdict

The plan's AI pipeline is buildable in its overall shape and is unusually well argued where it is honest — the deterministic-pipeline-with-narrow-nodes orchestration is the right call and is defended on the right axes; the keyframe-first economic control is correctly identified as the system's most important lever; the write-ahead spend ledger with resolve-by-query and the named `submitted-unknown` state is a genuine and correct re-derivation of A2's idempotency gap; the brand-truth split follows C1's documented API surface exactly; and the gate ordering rationale (spin before voice, claim bracketing voice) is stronger than most production systems achieve. Those parts should not be reopened. But the plan is not yet buildable **as written**, for four reasons that are structural rather than editorial. It has designed a media-cost architecture with great care and left its text-cost architecture entirely absent — no provider role, no registry, no cap, no forecast line — while its own volumes and C5's own token math put text spend in the same order as media spend; that is not a missing paragraph, it is a missing layer. It has made *completed-with-pending-media* a headline healthy outcome without designing what completes the asset, and its own Appendix A demonstrates the gap by shipping a finished, mastered, reviewed master whose clip is still rendering. It states the principle that any gate preceding a rewrite must re-run after it, and then ships a worked example in which a claim-2 repair reaches the pack without re-entering the voice gate, while making claim pass 2 "final on the exact packed bytes" for video assets whose claim-bearing on-screen text is composed after that gate closes. And it makes a provenance field a publish-gate precondition when the evidence it cites never establishes that the field is observable — turning a rights-defence control into a potential publish deadlock. Around these sit nineteen major gaps, of which the most consequential for a solo operator are the undefined keyframe-acceptance rubric that authorises every unattended clip purchase, the missing English golden set that leaves the judge-health signal uninstrumented through the entire trial, the absent frozen eval set that makes post-launch prompt changes unmeasured, and the single-spender assumption baked into balance-delta reconciliation against a first-class multi-theme requirement. None of the four blockers requires abandoning a design decision; each requires the plan to finish a seam it has correctly identified and then stepped over. **Verdict: approve with required changes — the four blockers must be closed before build sign-off, and the majors in §5 (providers), §6 (site verification, band cutoffs) and §14 (calibration, eval, gate-failure) should be closed before Phase 2 begins, since each of them is cheaper to design now than to retrofit after the first real packs exist.**
