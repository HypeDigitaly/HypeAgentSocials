# A2 — Video & Image Generation Providers: Kie.ai deep evaluation, Higgsfield.ai paper evaluation, alternatives, and provider-contract design

Research wave 1, agent T2. Retrieved dates in this brief are 2026-08-05/06 unless stated. This brief is the sole owner of Kie.ai and Higgsfield.ai facts for this wave; other briefs must cite it rather than re-research.

---

## 1. What this means for the operator

You asked which models to use on Kie.ai for image and video generation. Short answer, in plain language:

- **For images, use Nano Banana 2 as the everyday model (about 4 cents per image) and Nano Banana Pro for the "final" graphics that carry on-image text — including Czech text with diacritics — at about 9–12 cents per image.** These are Google's image models routed through Kie, and they are currently the best price-to-quality options on the platform for marketing graphics.
- **For video, use Veo 3.1 Fast as the workhorse (about 30 cents per 8-second clip, sound included) and reserve Veo 3.1 Quality (about $1.25 per clip) for the one or two "hero" reels you actually want to polish.** A typical finished reel stitches ~3 clips, so a finished English reel costs roughly $1.35 in video generation including retries. Use a very cheap model (Seedance 1.0 Lite or Wan class, ~5–8 cents per clip) only as a motion preview before spending on the good model.
- **Your $50 of trial credit is about 10,000 Kie credits.** Honestly costed — including retries, rejects, and the fact that every pack is produced twice (Czech + English) — that buys roughly **13 full two-language packs at standard quality**, or ~38 draft-quality packs, or ~3–4 hero-quality packs. It is enough to validate the whole pipeline, not enough to run production for a month (standard-tier production at 3 runs/week is roughly $90–140/month in generation spend).
- **Czech spoken audio is the one place native video models will burn you.** Veo's speech generation is English-first; non-English speech is unreliable. The design that works: generate Czech reels with ambient sound or music only, and add Czech voiceover with ElevenLabs (which supports Czech and is also routable through Kie). English reels can use native Veo speech.
- **Do not build anything on Sora 2.** OpenAI is switching the Sora API off on September 24, 2026. This is also the proof that no model may ever be hard-wired: the system needs a small model registry with "last verified" dates, not hardcoded model names.
- **Higgsfield.ai is not evaluated hands-on (no account, per decision).** On paper it is a consumer/creator subscription studio that bundles the same third-party models Kie routes, plus its own UGC/ads tooling. It looks like a *complement for a human operator*, not an API backbone — but that stays an open decision with confidence-tagged options below.
- **Two operational truths shape the whole architecture:** Kie deletes generated files after ~14 days (so every result must be downloaded and re-hosted immediately), and Kie has no idempotency mechanism (so the cron design must keep its own spend ledger to avoid paying twice when a retry fires).

---

## 2. Body

### 2.1 Kie.ai deep evaluation

#### 2.1.1 What Kie.ai is

Kie.ai is a prepaid, credit-based API reseller/aggregator ("wholesale marketplace for AI APIs"): one balance, one API surface, many upstream models at discounted prices (typically ~30% below official, selected models 60–70% below). Credits cost $0.005 each, sold from ~$5 upward, and do not expire. Domain is ~3.8 years old; company ownership is not public; third-party trust scanners rate it legitimate-but-opaque. Trustpilot sits around 2.5/5 on a small review pool, with recurring complaints: credits consumed on stuck/failed generations, tasks hanging at "99% generating," and content filters tightening (422 errors) after top-ups. Kie's own FAQ claims failed tasks are not charged. Net: legitimate, aggressively priced, but **not an SLA-grade vendor — the architecture must treat it as a replaceable routed dependency**, which is exactly what the provider-abstraction contract (2.9) exists for.

Platform mechanics that matter for design:

- **API shape (unified "Market" jobs API):** create a task via a single jobs endpoint (model selected by a model identifier in the payload), query status by task ID via a record-info endpoint, check balance via a credit endpoint. Bearer API-key auth, optional per-key rate limiting and IP whitelisting. Older model families (Veo, Runway, 4o Image) also have dedicated legacy endpoint families with slightly different shapes and state fields — a known model-ID/shape inconsistency the abstraction layer must normalize.
- **Async only:** HTTP 200 on submission means "task accepted," never "done." Results via polling (~30 s interval recommended) or a callback URL that Kie POSTs on completion.
- **Rate limits:** ~20 new generation requests per 10 seconds; 100+ concurrent running tasks typically allowed; HTTP 429 on violation.
- **Retention:** generated media files stored **14 days**, then automatically deleted; logs/metadata ~2 months; uploaded reference files are also temporary. Runway-family docs additionally expose an expiry flag on result URLs. Consequence in 2.6.
- **Free credits:** new accounts get ~80 free playground credits publicly; **our operator account has $50 of trial credit (≈10,000 credits) — locked fact D-04.**

#### 2.1.2 Routed model roster (actually routable as of Aug 2026)

Video (unified Market API + dedicated families):

| Route | Upstream vendor | Notes | Confidence |
|---|---|---|---|
| Veo 3 / 3.1 family: veo3, veo3_fast, veo3_lite | Google | t2v, i2v, first+last-frame, reference-images modes; 4/6/8 s; 720p/1080p/4K; native audio; dedicated endpoint family | High |
| Sora 2 / Sora 2 Pro | OpenAI | With audio, watermark-free; **upstream API sunsets 2026-09-24 — do not adopt** | High |
| Kling (to 3.0 / 3.0 Turbo) | Kuaishou | Strong i2v aesthetics, multi-shot in 3.0 | High |
| Seedance 1.0 / 2.0 / 2.0 Mini ("Bytedance") | ByteDance | 2.0 strong realistic humans; 1.0 Lite is a true budget tier | High |
| Wan family (2.5+) | Alibaba | Budget/workhorse class | Med |
| Hailuo | MiniMax | Mid-tier motion | Med |
| Grok Imagine Video | xAI | New route | Med |
| Runway (dedicated legacy family) | Runway | 5/10 s, 720p/1080p, several aspect ratios, extend-video | Med |

Image:

| Route | Upstream vendor | Notes | Confidence |
|---|---|---|---|
| Nano Banana 2 / 2 Lite (Gemini 3.x Flash Image) | Google | ~$0.04/1K image; fast iteration, editing | High |
| Nano Banana Pro (Gemini 3 Pro Image) | Google | ~$0.09 1K/2K, ~$0.12 4K; best-in-class on-image text incl. multilingual | High |
| GPT Image 2 / 4o Image | OpenAI | ~$0.03/1K t2i; photoreal + text rendering | Med-High |
| Seedream (3.0 → 5.0 Lite/Pro) | ByteDance | ~$0.035/1K (5 Pro); strong photorealism, multilingual visuals | Med-High |
| Flux-2 (multi-variant), Z-image, Google Imagen, Ideogram (V3), Qwen, Recraft, Topaz (upscale) | BFL / various | Roster confirmed; per-route prices not all published | Med |
| Grok Imagine (image) | xAI | Roster confirmed | Med |

Audio/other: ElevenLabs (TTS — **includes Czech**), Suno (music — **unofficial route, see licensing**), Gemini chat models, watermark-removal utility, file upload API. Midjourney is **not** confirmed in the current Market roster (older docs offered an unofficial MJ route); treat as unavailable.

#### 2.1.3 Credit pricing per model (verified snapshots)

$0.005 per credit throughout. "Per clip" = one generation.

| Model / tier | Credits | USD | Unit |
|---|---|---|---|
| Veo 3(.1) Fast, 8 s w/ audio | 60 (recently cut from 80) | $0.30 (was $0.40) | per clip |
| Veo 3(.1) Quality, 8 s w/ audio | 250 (recently cut from 400) | $1.25 (was $2.00); third-party cites ~$1.28 for 1080p | per clip |
| Veo 4K output | ~2× credits of same tier | ~2× | per clip |
| veo3_lite | not published; positioned as most economical | est. < Fast | per clip |
| Sora 2 standard, 10 s w/ audio | 30 | $0.15 | per clip (sunsetting) |
| Sora 2 Pro 10 s / Pro HD 10 s | 90 / 200 | $0.45 / $1.00 | per clip (sunsetting) |
| Kling 3.0 standard, no audio | ~27/s | ~$0.135/s (5 s ≈ $0.68) | per second |
| Seedance 2.0, 720p | — | ~$0.125/s | per second |
| Seedance 1.0 Lite/Pro | — | from ~$0.01/s | per second |
| Nano Banana 2 (1K / 2K) | 8 / 12 | ~$0.04 / ~$0.06 | per image |
| Nano Banana Pro (1K–2K / 4K) | ~18 / 24 | ~$0.09 / ~$0.12 | per image |
| GPT Image 2 (1K t2i) | ~6 | ~$0.03 | per image |
| Seedream 5 Pro (1K) | ~7 | ~$0.035 | per image |
| Sora watermark-remover utility | 10 | $0.05 | per request |

Kie's own docs describe Veo routing as "~25% of official Google pricing." Cross-check vs direct: Google Gemini API Veo 3.1 ≈ $0.40/s standard, $0.15/s Fast (i.e., $3.20 / $1.20 per 8 s) — Kie's $1.25 / $0.30 per 8-s clip is consistent with a deep discount. Prices on Kie change frequently (two documented cuts in 2026); every number above is in the fact ledger with a recheck-by date.

#### 2.1.4 Output retention / expiry

- Generated media: deleted after **14 days**; result URLs carry validity windows and (in some families) an explicit expired flag.
- Logs/metadata: ~2 months. Uploaded reference files (i2v inputs): temporary as well.
- Design consequence: the pipeline must treat Kie as **ephemeral scratch storage** — download every accepted artifact into the run package immediately on task success, and never store Kie URLs as the artifact of record (details in 2.6).

#### 2.1.5 Per-routed-model commercial usage rights (upstream licenses matter, not just Kie ToS)

The blunt structural fact: **Kie resells; it cannot grant more rights than the upstream vendor grants, and buying through a reseller forfeits the contractual protections (notably indemnification) that direct customers get.**

| Routed model | Upstream commercial stance | Via-Kie caveat | Confidence |
|---|---|---|---|
| Veo (Google) | Output usable commercially under Gemini API terms; agency/client work generally permitted. EU/UK/CH/MENA: person generation restricted to "allow_adult"; some person i2v needs allowlisting. Google's generated-output indemnification applies to **direct** paid Google Cloud/Gemini customers | No Google indemnity through Kie; unclear whether Kie's Veo access is a sanctioned resale — treat outputs as commercially usable but uninsured | Med-High |
| Nano Banana / Imagen (Google) | Same Google terms family as above | Same caveat | Med-High |
| GPT Image 2 (OpenAI) | OpenAI terms: user owns output, commercial use allowed | Reseller path may violate OpenAI ToS; no OpenAI recourse | Med |
| Sora 2 (OpenAI) | API being retired 2026-09-24; at least one aggregator listing explicitly labels Kie's Sora route "unofficial" | Do not adopt regardless of rights | High (sunset), Med (unofficial label) |
| Kling (Kuaishou) | Paid plans/API include commercial rights; free tier watermarked, no commercial use | API-class usage via Kie is presumably the commercial class, but no direct contract | Med |
| Seedance / Seedream (ByteDance) | Official commercial API exists (BytePlus ModelArk); outputs commercially usable for API customers | Same reseller caveat | Med |
| Wan (Alibaba) | Wan 2.1/2.2 open weights (Apache-2.0); Wan 2.5+ hosted/commercial API | Open-weight generations are the legally cleanest class in the roster | Med |
| Runway | API outputs commercially usable for paying customers | Same reseller caveat | Med |
| Flux-2 (BFL) | Pro/API variants commercial; some dev-weight variants restricted | Verify per-variant before use | Med |
| Hailuo (MiniMax), Grok Imagine (xAI) | Commercial API offerings exist; terms not deeply verified | Verify before production use | Low |
| ElevenLabs | Commercial rights with paid usage; supports Czech | Fine for VO; keep voice-cloning consent rules in mind | Med-High |
| Suno (music) | **No official API exists; all Suno API routes incl. Kie's are unofficial/reverse-engineered; commercial-license claims by such providers are not guarantees; Suno itself is in active training-data litigation** | **Do not use for brand-published music.** Use licensed stock music or an officially licensed generator instead | High |

Cross-cutting: EU AI Act transparency obligations (AI-content disclosure, Article 50 class) started applying August 2, 2026 — published AI-generated marketing video for an EU/Czech brand should carry AI-content labeling regardless of provider choice (flag for the safety/policy brief; noted here because native-audio "spoken claims" make undisclosed synthetic video a legal surface, F-5).

#### 2.1.6 Model registry concept (answer to F-3: churn is structural)

Evidence that pinning is unsafe, all within ~12 months: Sora 2 API announced March 2026, dead September 2026; Kie cut Veo prices twice; Kie's roster gained Grok Imagine, Flux-2, Seedance 2.0, Nano Banana 2 within months; Higgsfield repriced credits 2–6× per third-party documentation. Prompt patterns and price tiers churn with the models.

Registry concept (design artifact, not config syntax): one registry record per **route** (provider × upstream model × tier), holding — capability flags (modes, durations, aspects, audio, languages), price snapshot with unit, license class (direct-commercial / reseller-uninsured / unofficial-forbidden / open-weight), person-generation policy class, known sunset date, prompt-pattern version it was validated against, last-verified date, recheck-by date, and status (active / degraded / deprecated / dead). Re-verification cadence: **prices and roster monthly; anything with a recheck-by date that lapses drops to "degraded" and the router stops selecting it for spend; vendor-announcement events (deprecations, price changes) trigger immediate review; a cheap availability probe (credit-balance call + one draft-tier generation) belongs in a weekly scheduled health run.** The registry is also where per-model refusal statistics accumulate (2.7).

### 2.2 Explicit recommendation: best models on Kie for B2B viral-style reels within the $50 trial

**Image generation — recommendation: Nano Banana 2 (default) + Nano Banana Pro (finals with on-image text).**
Rationale: NB2 at ~$0.04/1K is the best iteration-speed-per-dollar on the roster and handles prompt-based editing (brand-color lock, layout variants). NB Pro at ~$0.09–0.12 is the roster's strongest at clean, correct on-image typography — which matters doubly here because half of all assets carry **Czech** on-image text (diacritics are where weaker models produce garbage glyphs; NB Pro is explicitly positioned for multilingual visual text). Seedream 5 Pro (~$0.035) is the named fallback for photoreal non-text imagery; GPT Image 2 (~$0.03) the budget fallback. Cost math: a 5-slide carousel + 2 stills, drafted on NB2 and finalized with 2 NB Pro text-heavy slides ≈ 5×$0.04 + 2×$0.09 = **$0.38 per language before retries, ~$0.49 with a 1.3× retry factor.**

**Video generation — recommendation: Veo 3.1 Fast (workhorse) + Veo 3.1 Quality (hero only), with Seedance 1.0 Lite as the pre-spend motion-draft tier.**
Rationale: Veo Fast at $0.30 per 8-s clip with native audio is currently the best quality-per-dollar for B2B-safe, realistic short-form footage, and it supports all four generation modes (t2v, i2v, first+last-frame, reference-to-video) so one route covers the whole keyframe-first workflow from A1's practices. Veo Quality at $1.25 (1080p) is reserved for the chosen winner per pack. Seedance 1.0 Lite at ~$0.05–0.08 per 5-s clip exists purely to test motion/composition before spending 6× on Veo. Kling 3.0 (~$0.68/5 s) is the named alternative when Veo's look fails a specific aesthetic (stylized product motion, multi-shot native). **Sora 2 is explicitly rejected** (sunset). Czech-language reels: generate with ambience/music only and layer ElevenLabs Czech VO (see 2.7/F-5); English reels may use Veo native speech.

Cost math per finished reel (3 clips ≈ 24 s, standard tier, incl. 1.5× retry/reject factor): 3 × $0.30 × 1.5 = **$1.35 per language**; hero tier: 3 × $1.25 × 1.5 = **$5.63 per language**. Full trial arithmetic in 2.11.

$50-trial spending plan (recommendation): ~$8 on a model bake-off (same 3 prompts through Veo Fast, Kling 3.0, Seedance 2.0, plus NB2/NB Pro/Seedream image trio — this produces the operator's own evidence, not blog claims), ~$35 on 8–10 real two-language standard packs end-to-end, ~$7 reserve for retries and one hero reel. This validates the pipeline and the unit economics table against reality before any paid top-up.

### 2.3 Higgsfield.ai paper evaluation (no account — options, not a firm recommendation)

**What it actually is (verified):** a venture-backed creator/marketing studio (founded by ex-Snap AI lead Alex Mashrabov; ~$130M Series A total; ~$1.3B valuation early 2026; reported ~$500M annualized revenue mid-2026 and talks at a $5B valuation — i.e., not a fragile startup). Product surface: a web/mobile studio aggregating 50+ third-party models (Kling 3.0, Sora 2, Veo 3.1, Seedance 2.0, Nano Banana Pro), plus differentiated own tooling — **Cinema Studio / DoP-style camera controls, Soul ID character consistency, UGC Builder (talking-head UGC ads via Veo 3/Seedance 2.0), Marketing Studio (nine ad formats from one product image; a "Hermes" agent scrapes a product URL into a creative brief and renders the ad)** — plus MCP integration with Claude/ChatGPT, CLI batch tools, and native plugins for Premiere/AE/Photoshop/Resolve/Figma. Enterprise tier: SOC 2-aligned, SSO/SAML, RBAC, audit logs, SLA.

**Pricing (volatile; restructured repeatedly in 2026):** Starter ~$9–15, Plus ~$17–39, Ultra ~$24–99/mo (annual-vs-monthly spreads; annual billing is the signup default — widely criticized as a dark pattern), credit pools roughly 150–200 / 600–1,000 / 1,200–3,000+; premium-model clips cost ~40–70 credits; top-up packs ~$5/100 credits that **expire after ~90 days**; monthly credits do not roll over; "unlimited" offerings are throttled; documented 2–6× credit-cost increases; moderation reportedly stricter than the underlying source models; support is AI-only. Paid plans include commercial usage rights per third-party reviews.

**API reality (F-6 — sparse docs confirmed):** a first-party developer surface exists (cloud.higgsfield.ai; submit / poll / cancel generation endpoints, bearer auth, webhooks), and Higgsfield models are additionally routable through third-party routers (eachlabs and similar). But documentation depth, per-generation API pricing, retention, and idempotency are not publicly specified anywhere found — a material contrast with Kie's docs.

**Complement-vs-competitor verdict — confidence-tagged options (OPEN DECISION, per lock):**

- **Option H1 — Ignore for v1 (complement later, maybe).** Kie covers the same underlying models cheaper and with clearer API docs; Higgsfield's differentiators (Soul ID, Cinema Studio, Marketing Studio) are human-studio features that don't fit an unattended cron pipeline. *Confidence this is the right v1 call: Medium-High.*
- **Option H2 — Human-side complement.** Operator buys a personal Plus-tier seat as a *review-and-polish studio* (turn a winning Kie draft into a UGC-style ad, character-consistent series via Soul ID), completely outside the automated pipeline. Cost is bounded ($17–39/mo), no architecture impact. *Confidence this adds real value for viral-style output: Medium.*
- **Option H3 — Second routed provider in the abstraction.** Treat Higgsfield's API as a peer route for UGC-format generation the way Kie routes raw models. Blocked today by sparse API docs, unknown API pricing, credit expiry, and moderation opacity; would need a hands-on spike (which requires an account — currently out of scope). *Confidence it's worth the integration cost now: Low.*
- **Competitor framing:** as an *aggregator*, Higgsfield is a direct Kie competitor with worse unit economics for API automation (subscription + expiring credits vs. non-expiring pay-per-use). As a *product*, its UGC/Marketing Studio is upstream-of-Postiz creative tooling our pipeline partially replicates — competitor to our asset-creation stage, complement to our review stage. *Confidence: Medium.*

### 2.4 Serious alternatives (provider level, with tradeoffs)

| Alternative | What it is | Price signal (2026) | Tradeoff vs Kie |
|---|---|---|---|
| **fal.ai** | Developer-grade model router/inference platform | Veo 3.1 from ~$0.10/s Fast, $0.20–0.40/s standard; Kling 2.5 Turbo Pro $0.07/s; Kling 3.0 Pro $0.112/s; Wan ~$0.05/s | More credible engineering reputation, likely official model partnerships, better reliability record; usually pricier than Kie per clip; strongest fallback router candidate |
| **Replicate** | Router, open-weight strength | Per-model | Best for open-weight (Wan class) routes; commercial closed models thinner |
| **eachlabs** | Router incl. Higgsfield models | Per-model | Only found route to Higgsfield capability without a Higgsfield contract |
| **Google Gemini API / Vertex (direct)** | First-party Veo | Veo 3.1 $0.40/s; Fast $0.15/s; Lite ~$0.05–0.08/s; charged only on success | 3–4× Kie's price, but SLA, indemnification, first-day model access; the "grown-up" migration path when the product earns revenue |
| **Runway (direct API)** | First-party | $0.01/credit: Gen-4 Turbo $0.05/s, Gen-4 $0.12/s, Gen-4.5 $0.25/s (~$0.60/5 s clip) | Premium look, strong tooling; expensive; no native audio at these tiers |
| **Kling (direct API)** | First-party | Kling V3 ~6–8 credits/s (~$0.32/10 s 1080p per third-party math) | Competitive direct pricing emerging; contract/portal friction from EU |
| **OpenRouter / BytePlus (Seedance direct)** | First-party-ish | Seedance 2.0 ~$0.067/s (OpenRouter) | Cheap realistic humans; ByteDance contractual comfort varies |
| **ElevenLabs (direct or via Kie)** | VO provider | Usage-priced; Czech supported (v3 ~70+ langs; multilingual v2 incl. Czech) | The F-5 mitigation; near-negligible per-reel cost |
| **HeyGen / Synthesia class (avatar/UGC)** | Avatar providers | Subscription | Only if a theme wants presenter-style UGC; consent/likeness licensing is clean (licensed avatars), unlike gray UGC routes |
| **Suno via Kie / unofficial music APIs** | Music | Cheap | **Rejected for published assets** — unofficial route, litigation-clouded upstream |
| **Luma, Pika, Vidu, Hailuo direct** | Additional first-party video APIs | Per-model | Monitor via registry; none currently beats the Veo-Fast price/quality point for B2B-safe realism |

Structural recommendation: **primary router Kie.ai (price) + registered fallback router fal.ai (reliability) + a documented direct-API migration path (Google) once spend or reliability justifies it.** Dual-routing belongs in **global** provider settings with per-theme overrides limited to tier/budget preferences — themes should choose "how good/expensive," not "which vendor."

### 2.5 Model/job fit: which generation mode fits which asset type

| Mode | What it is | Best-fit asset in this product | Notes |
|---|---|---|---|
| **Text-to-video** | Prompt → clip | Ambient B-roll, abstract concept shots, background loops for stat overlays | Cheapest to attempt, least brand-controllable; fine for draft tier |
| **Image-to-video (keyframe-first)** | Approved still → motion | **The default for brand-locked reels**: generate/approve the keyframe cheap (NB2/NB Pro, brand colors, correct Czech/English text), then animate | Decouples the expensive spend from the brand-correctness decision; the human (or QA rubric) approves a $0.04 image before a $0.30–1.25 clip is bought; also halves language cost — same motion, two text variants |
| **First+last-frame** | Two stills → transition | Before/after product moments, hook→payoff transitions, seamless loops (last≈first) | Veo route supports natively |
| **Reference-to-video** | 1–3 reference images → clip | Product-in-scene shots, consistent object across clips | Veo fast/lite only; fixed 8 s |
| **Multi-shot-native** | Model plans several shots in one generation | Mini-narrative UGC-style ads | Kling 3.0's territory; less controllable, more "one-roll magic"; use for hero experiments, not the cron default |
| **Native-audio generation** | Speech/SFX baked in | English talking moments, ambience | English-first; Czech speech unreliable → CS reels: ambience/music only + ElevenLabs VO layered in assembly (A4's domain) |
| **Extend-video** | Lengthen existing clip | Stretching a winner to platform minimums | Runway family |

Pipeline consequence: the product's reel unit is **keyframe-first by default** (i2v), with t2v allowed at draft tier and multi-shot reserved for flagged hero experiments. This maps directly onto the draft/standard/hero tiering in 2.10.

### 2.6 Async job lifecycle → consequences for unattended cron

Observed lifecycle on Kie (representative of the whole category):

submit task (get task ID, HTTP 200 = accepted only) → task queued → generating (typically 1–6 min; 1080p post-processing adds 1–2 min; stuck-task incidents reported) → terminal state: success (result URLs) / fail / policy-fail → result URLs valid only for a window; all media hard-deleted at ~14 days.

State signaling is inconsistent across families (numeric success flags 0/1/2/3 in the Veo family; named states wait/queueing/generating/success/fail in the Runway family) — normalize in the abstraction. Completion can be received by webhook (Kie POSTs to a callback URL) or polling every ~30 s.

Consequences for a Windows-first console job that later runs as Linux cron (D-05):

1. **Polling, not webhooks, as the baseline.** A cron console process has no stable public HTTPS endpoint; webhook designs require standing infrastructure. Poll within the run with capped intervals; webhooks become an optional optimization if the product ever grows a small always-on receiver.
2. **A run must be allowed to end with jobs still pending.** Renders are minutes-long and can hang; a cron run needs a wall-clock budget. Persist every submitted task ID with its asset slot in a local job ledger; the *next* run's first phase is "adopt and resolve pending tasks" before submitting new ones. A task older than a timeout (e.g., >10 min per Kie's own 408 semantics) is declared lost and eligible for controlled re-submission under the spend rules of 2.8.
3. **Immediate re-hosting is non-negotiable.** On success, download every artifact into the run package (local disk now; durable store later) before marking the asset done. Kie URLs are never the artifact of record: 14-day deletion plus URL expiry means a review package holding provider URLs silently rots before a human reviews it.
4. **Terminal failure is a first-class packaged outcome** — a failed or refused asset slot appears in the review package as "plan-only + reason," never as a crash (2.7).
5. **Exit-code discipline:** pending-but-healthy ≠ failure; the run should report partial completion distinctly so cron monitoring doesn't page on normal multi-run render arcs.

### 2.7 Refusals as normal outcomes

How refusals surface on Kie: synchronously at submission (HTTP 400 prompt-policy violation, 422 moderation/validation rejection) and asynchronously mid-task (terminal fail states, 501 generation-failed; Veo-family failures for flagged content or inaccessible input images). Kie's Veo route also silently switches to a backup model on some content-review triggers — meaning **the delivered artifact may come from a different model than requested** (fallback outputs can't use the 1080p endpoint and force 16:9). The router must record which model actually rendered.

Marketing-relevant triggers (documented + community-evidenced): real people by name / prominent-person likenesses; **EU/UK person-generation restriction (allow_adult only; some person i2v requires allowlisting — directly relevant to a Czech operator)**; child-related false positives (a documented "wholesome commercial storyboard" i2v block); trademarks/logos in input images; violence/medical/financial claim territory; and — on Kie specifically — community reports of filter tightening over time (422s appearing on previously working prompts). Aggregators can also be **stricter** than upstream (documented at Higgsfield). No provider publishes refusal rates; the honest design stance is that refusal probability is nonzero on every marketing prompt involving people or brands, and must be *measured in-house*: log every refusal with route, trigger class, and prompt-pattern version into the model registry so per-model refusal rates become operator data within weeks.

Strategy ladder (design): refusal taxonomy → (1) one automated sanitize-and-rewrite attempt (strip names/brands/persons, keep message) → (2) one model-swap attempt to a registered alternate route → (3) **degrade to plan-only**: package the approved keyframe, script, and prompt with the refusal reason for the human — never loop retries. Hard cap on paid attempts per asset slot (recommend 3). Refusals cost no credits at submission-reject time (claimed), but mid-task failures have disputed billing on Kie — the spend ledger (2.8) reconciles either way. Native-audio safety corollary (F-5): because refusal filters do *not* catch factual marketing lies, the claim-safety gate for spoken-audio scripts is our own responsibility — no generated speech that states prices, ROI, client names, or metrics; Czech speech additionally routed to ElevenLabs VO (from a reviewed script), which keeps every spoken word in an auditable text artifact.

### 2.8 Idempotency × money

Verified gap: **Kie documents no idempotency key, no client-reference field, and no dedup semantics on task creation** (the docs' notable-gaps list, confirmed across families). Higgsfield's public docs are silent too. A naive cron retry after a crash re-submits and re-pays. Therefore the money-safety machinery must live entirely on our side:

- **Deterministic asset identity:** every generation slot gets a stable identity derived from theme + run date + topic + asset slot + language + prompt-pattern version. One identity = at most one *paid* attempt chain.
- **Write-ahead spend ledger:** append an "intent" record (identity, route, expected credit cost) *before* submission; record task ID on acceptance; record terminal state and actual cost on resolution. On restart, any intent without a terminal state is *resolved by querying* (task status by ID), never blindly re-submitted.
- **Balance reconciliation:** Kie exposes a credit-balance endpoint — snapshot balance at run start and end; delta minus ledger total is the "unexplained spend" alarm (this catches the community-reported charged-but-stuck cases).
- **Budget caps enforced pre-submission** against the ledger (per asset, per run, per day, per month) — a cap check *after* submission is too late.
- **Provider-side keys as blast-radius control:** Kie supports per-key rate limits and IP whitelisting — separate keys for dev vs cron, with the cron key top-up-limited so a runaway loop is bounded by the wallet, not just by our code.

### 2.9 Routing-contract axes for the provider abstraction

A generation request, expressed provider-neutrally, needs exactly these axes (each maps to registry capability flags):

| Axis | Values (conceptual) | Why |
|---|---|---|
| Duration | 4/6/8 s native; 5/10 s; per-second models | Providers quantize differently; the reel plan asks for seconds, the router picks the legal quantum |
| Aspect | 9:16, 16:9, 1:1, auto | Reels are 9:16; some fallbacks force 16:9 (record when it happens) |
| Audio | none / ambient-SFX / native speech (+language) | The Czech/English split lives here (F-5) |
| Mode | t2v / i2v / first+last / reference / multi-shot / extend | 2.5 mapping |
| Motion class | talking human / product b-roll / kinetic-text / scene-narrative | Drives model choice as much as quality does |
| Quality tier | draft / standard / hero | 2.10 |
| Budget ceiling | max credits for this asset incl. retries | Enforced by 2.8 |
| Person policy | no-people / adults-only / people-restricted-region | EU constraint made explicit, not discovered at refusal time |
| Rights class | direct-commercial / reseller-uninsured / open-weight / forbidden | From 2.1.5; publishing gate reads this |
| Resolution | 720p / 1080p / 4K | Price multipliers |

The router resolves (axes → eligible registry routes → cheapest within tier and rights class → submit); everything the router *couldn't* honor (fallback model swap, forced aspect) is recorded on the artifact for the review package.

### 2.10 Draft-cheap vs final-expensive tiering

- **Tier 0 — plan-only ($0):** always produced, even with no keys/budget (assignment rule): prompts, scripts, shot lists, keyframe descriptions. The cron floor.
- **Tier 1 — draft (~$0.05–0.15/asset):** keyframes on NB2 ($0.04); motion previews on Seedance 1.0 Lite / Wan class (~$0.05–0.08 per 5 s); purpose is composition/motion validation and refusal-surface discovery at pocket-change cost.
- **Tier 2 — standard (~$0.30–0.50/clip, ~$0.04–0.09/image):** Veo 3.1 Fast clips from approved keyframes; NB2 images with NB Pro for text-carrying slides. The default cron production tier.
- **Tier 3 — hero (~$1.25–2.50/clip):** Veo 3.1 Quality 1080p (or Kling 3.0 multi-shot experiment), only for assets a human (or later, a scored winner-selection policy) explicitly promotes. Never auto-selected by unattended runs.

Escalation rule: money only moves up a tier through an approval event (human pick, or config-enabled auto-promote with a per-run hero cap of 1). Draft artifacts are never published — they exist to make the expensive call cheap to get right.

### 2.11 Run-level unit economics (honest, cs+en doubled per D-02)

Assumptions: 1 pack = 1 topic × 2 languages; per language: 1 reel (3 × 8-s clips), 5 carousel slides, 2 stills; retry/reject multipliers 1.5× video, 1.3× images (covers paid-but-quality-rejected generations; submission-refusals claimed free); ElevenLabs VO ≈ $0.05/reel (estimate); Kie prices from 2.1.3.

| Tier | Video per lang | Images per lang | Per language | **Per pack (cs+en)** | Per run (2 packs) | Per month (12 runs) | Packs per $50 trial |
|---|---|---|---|---|---|---|---|
| Draft | 3×$0.06×1.5 = $0.27 | 7×$0.04×1.3 = $0.36 | ≈ $0.65 | **≈ $1.30** | ≈ $2.60 | ≈ $31 | ≈ 38 |
| Standard | 3×$0.30×1.5 = $1.35 | (5×$0.04+2×$0.09)×1.3 = $0.49 | ≈ $1.90 | **≈ $3.80** | ≈ $7.60 | ≈ $91 | ≈ 13 |
| Hero | 3×$1.25×1.5 = $5.63 | 7×$0.12×1.3 = $1.09 | ≈ $6.75 | **≈ $13.50** | ≈ $27 | ≈ $324 | ≈ 3.7 |

Honest readings against the $50 reality: (a) the trial validates architecture and quality, not a month of production; (b) cs+en doubling is the single biggest cost driver — keyframe-first softens it for images (one composition, two text variants) but video clips still render twice when text or speech is baked in; a deliberate design lever is *language-neutral footage + language-specific overlays/VO added in assembly*, which collapses video cost back to ~1× and is recommended as the default reel recipe (hand-off to A4's assembly brief); (c) at standard tier the marginal cost of a finished, review-ready two-language pack is ~$3.80 — the economics headline for the whole product; (d) mixed reality will land between rows (e.g., standard packs + 1 hero promotion/week ≈ $110–140/month).

---

## 3. Decision table

| Decisions unblocked (→ architecture area) | Basis |
|---|---|
| Kie.ai as v1 primary generation provider; treated as replaceable, non-SLA dependency (→ provider abstraction) | 2.1, 2.4 |
| Image models: Nano Banana 2 default + Nano Banana Pro for text-carrying finals; Seedream 5 Pro / GPT Image 2 fallbacks (→ model registry seed data) | 2.2 |
| Video models: Veo 3.1 Fast workhorse + Veo 3.1 Quality hero + Seedance 1.0 Lite draft; Kling 3.0 registered alternate (→ model registry seed data) | 2.2 |
| Sora 2 excluded everywhere (API sunset 2026-09-24) (→ model registry: status dead-by) | 2.1.5, F-3 |
| Suno-via-Kie music forbidden for published assets (→ safety/rights gate) | 2.1.5 |
| Keyframe-first (i2v) as default reel workflow; t2v draft-only; multi-shot hero-only (→ reel pipeline) | 2.5 |
| Czech reels: no native model speech; ambience/music + ElevenLabs Czech VO from reviewed scripts (→ reel pipeline, safety) | 2.7, F-5 |
| Language-neutral footage + per-language overlays/VO as default recipe to break the cs+en video-cost doubling (→ assembly contract, with A4) | 2.11 |
| Polling-first job lifecycle; runs may end with pending tasks; next run adopts them (→ cron/job-ledger design) | 2.6 |
| Immediate download/re-host of every artifact; provider URLs never the record (→ storage design) | 2.1.4, 2.6 |
| Client-side write-ahead spend ledger + deterministic asset identity + pre-submission budget caps + balance reconciliation (→ money-safety design) | 2.8 |
| Routing contract axes fixed as listed (→ provider abstraction interface) | 2.9 |
| Model registry with last-verified/recheck-by dates, monthly price recheck, weekly availability probe (→ ops design) | 2.1.6 |
| Provider routing global with per-theme tier/budget overrides only (→ config split) | 2.4 |
| $50 trial plan: bake-off + 8–10 standard packs + reserve (→ operator runbook) | 2.2 |

| Decisions deferred (→ open decision) | What would resolve it |
|---|---|
| Higgsfield role: ignore (H1) vs human-side complement (H2) vs API route (H3) — no firm recommendation permitted or warranted | Operator decision; H3 additionally needs a hands-on API spike (requires an account) |
| Fallback router choice (fal.ai leading candidate) and the trigger threshold for engaging it | Reliability data from the trial period |
| Migration threshold to direct Google API (SLA + indemnification vs ~3–4× price) | Revenue/risk appetite decision after production starts |
| Whether a small always-on webhook receiver is ever worth it vs pure polling | Only if render volume makes polling latency material |
| Exact retry multipliers and per-tier budgets in config | Replace assumed 1.5×/1.3× with measured rates from the trial |
| Avatar/UGC presenter provider (HeyGen-class) if a theme wants talking-presenter formats | Theme demand; consent/likeness policy work |
| EU AI Act labeling mechanics for published AI video/audio | Safety/policy brief ownership (flagged, in force since 2026-08-02) |
| veo3_lite, Wan-on-Kie, Hailuo-on-Kie exact prices (unpublished) — draft-tier candidates pending verification | First live balance-delta measurements on the trial account |

---

## 4. Fact ledger

All retrieved 2026-08-05/06. Confidence: H/M/L. Recheck-by = date after which the claim must be re-verified before being relied on.

| # | Claim | Source URL | Retrieved | Conf. | Recheck-by |
|---|---|---|---|---|---|
| 1 | Kie credit rate $0.005/credit; credits do not expire | https://kie.ai/pricing (via search snippet) + https://www.bitdoze.com/kie-ai-review/ | 2026-08-06 | H | 2026-09-06 |
| 2 | Kie unified jobs API: createTask / recordInfo / credit-balance endpoints, bearer auth, optional callbacks | https://docs.kie.ai/market/quickstart | 2026-08-06 | H | 2026-10-06 |
| 3 | Kie Market roster (video): Kling, Sora2, Bytedance/Seedance, Hailuo, Wan, Grok Imagine Video; (image): Z-image, Grok Imagine, Flux-2, Imagen, Ideogram, Qwen, Recraft, Topaz; (audio): ElevenLabs | https://docs.kie.ai/market/quickstart | 2026-08-06 | H | 2026-09-06 |
| 4 | Kie generated media deleted after 14 days; logs ~2 months | https://docs.kie.ai/ (getting started) + https://www.bitdoze.com/kie-ai-review/ | 2026-08-06 | H | 2026-11-06 |
| 5 | Kie rate limits ~20 new requests/10 s, 100+ concurrent tasks, HTTP 429; per-key limits + IP whitelist | https://docs.kie.ai/ (getting started) | 2026-08-06 | H | 2026-11-06 |
| 6 | Veo route params: veo3/veo3_fast/veo3_lite; t2v, i2v, first+last-frame, reference (fast/lite only, fixed 8 s); 4/6/8 s; 720p/1080p/4K (4K ≈ 2× credits); silent model-fallback on content review; fallback forces 16:9, no 1080p endpoint | https://docs.kie.ai/veo3-api/generate-veo-3-video | 2026-08-06 | H | 2026-10-06 |
| 7 | Kie error semantics: 400 policy violation, 402 credits, 422 moderation, 429 rate limit, 408 >10-min timeout, 501 generation failed | https://docs.kie.ai/veo3-api/generate-veo-3-video | 2026-08-06 | H | 2026-11-06 |
| 8 | Veo Fast 8 s w/ audio was 80 credits ($0.40), cut to 60 ($0.30); Quality was 400 ($2.00), cut to 250 ($1.25) | https://kie.ai/v3-api-pricing + https://www.skool.com/ai-automation-society/kie-ai-just-updated-their-pricing | 2026-08-06 | M-H | 2026-09-06 |
| 9 | Third-party quote: Veo 3.1 Quality 1080p ≈ $1.28 on Kie | https://www.bitdoze.com/kie-ai-review/ (2026-07-17) | 2026-08-06 | M | 2026-09-06 |
| 10 | Kie new accounts get 80 free playground credits | https://www.skool.com/ai-automation-society/kie-ai-just-updated-their-pricing (+ kie.ai/kling-3-0 snippet) | 2026-08-06 | M | 2026-10-06 |
| 11 | Operator trial account holds exactly $50 of Kie credits | Locked decision D-04 (operator statement 2026-08-05) | 2026-08-05 | H | n/a |
| 12 | Kie Sora 2: $0.15/10 s standard (30 cr), Pro $0.45/10 s, Pro HD $1.00/10 s, watermark-free; watermark-remover utility 10 cr ($0.05) | https://www.ilounge.com/articles/sora-2-api-pricing-kie-ai-offers-a-cost-effective-ai-video-generation-integration-solution + https://kie.ai/sora-2-pro | 2026-08-06 | M | dead 2026-09-24 |
| 13 | Sora 2 API deprecation announced 2026-03-24; removal 2026-09-24; consumer app closed 2026-04-26; no successor announced | https://developers.openai.com/api/docs/deprecations + https://help.apiyi.com/en/sora-2-api-shutdown-alternatives-2026-en.html | 2026-08-06 | H | 2026-09-24 |
| 14 | Kie's Sora route described as "unofficial" by an aggregator listing | https://topaihubs.com/item/kieai-affordable-and-stable-unofficial-sora-2-api-for-text-image-to-video-with-audio | 2026-08-06 | M | n/a |
| 15 | Kling 3.0 on Kie: standard no-audio ≈ 27 credits/s (5 s ≈ 135 cr ≈ $0.68); ~$0.075/s at third-party resellers | https://kie.ai/kling-3-0 (snippet) + https://renderful.ai/blog/kling-api-pricing | 2026-08-06 | M | 2026-09-06 |
| 16 | Seedance 2.0 on Kie ≈ $0.125/s 720p; Seedance 1.0 from ~$0.01/s; Seedance 2.5 official price unpublished as of 2026-07-15 | https://www.atlascloud.ai/blog/guides/cheapest-api-provider-seedance-2-kling-wan + https://kie.ai/bytedance/seedance-v1 + https://kie.ai/blog/seedance-2-5-pricing | 2026-08-06 | M | 2026-09-06 |
| 17 | Nano Banana 2 on Kie: ~$0.04/1K, ~$0.06/2K; NB Pro: ~$0.09 1K/2K, ~$0.12 4K (24 cr); Google official NB Pro $0.134/1-2K, $0.24/4K | https://kie.ai/nano-banana-2 + https://www.aifreeapi.com/en/posts/nano-banana-pro-api-pricing + https://www.bitdoze.com/kie-ai-review/ | 2026-08-06 | M-H | 2026-09-06 |
| 18 | GPT Image 2 on Kie ~$0.03/1K t2i; Seedream 5 Pro ~$0.035/1K | https://www.bitdoze.com/kie-ai-review/ | 2026-08-06 | M | 2026-09-06 |
| 19 | Kie claims no charge for failed generations; community reports contradict (credits vanishing on stuck tasks, 99%-hang, filters tightening post-top-up); Trustpilot ≈ 2.5/5 small pool | https://www.bitdoze.com/kie-ai-review/ + https://aiinsightsnews.net/kie-ai-review/ + https://www.trustpilot.com/review/kie.ai | 2026-08-06 | M | 2026-10-06 |
| 20 | Kie domain ~3.8 yrs old, ownership non-public, trust score ~80/100, not flagged malicious | https://www.scamadviser.com/check-website/kie.ai + https://gridinsoft.com/online-virus-scanner/url/kie-ai | 2026-08-06 | M | 2027-02-06 |
| 21 | Runway-on-Kie: 5/10 s, 720p (all) / 1080p (5 s), aspects 16:9/9:16/1:1/4:3/3:4, 14-day retention, expireFlag, states wait/queueing/generating/success/fail | https://docs.kie.ai/runway-api/quickstart | 2026-08-06 | H | 2026-10-06 |
| 22 | Google direct: Veo 3.1 $0.40/s (720/1080p), $0.60/s 4K; Fast $0.15/s; Lite ~$0.05–0.08/s; charged only on success | https://ai.google.dev/gemini-api/docs/veo + https://www.aifreeapi.com/en/posts/veo-3-1-pricing + https://costgoat.com/pricing/google-veo | 2026-08-06 | M-H | 2026-09-06 |
| 23 | Veo person generation: EU/UK/CH/MENA restricted to allow_adult; model-level refusal of named real people; allowlist requests observed for person i2v; child-safety false positives on commercial storyboards documented | https://ai.google.dev/gemini-api/docs/veo + https://discuss.ai.google.dev/t/veo-3-1-image-to-video-blocks-wholesome-commercial-storyboard-child-safety-false-positive/131917 | 2026-08-06 | H | 2026-11-06 |
| 24 | Veo speech is English-first; non-English prompt/speech support limited; dialogue is the weakest audio class | https://www.mindstudio.ai/blog/what-is-google-veo-3-video-audio + https://www.atlascloud.ai/blog/guides/ai-video-models-native-audio-compared | 2026-08-06 | M | 2026-10-06 |
| 25 | ElevenLabs: Eleven v3 supports 70+ languages incl. Czech (alpha); multilingual v2 (production, 29 langs) also lists Czech | https://elevenlabs.io/docs/overview/models + https://help.elevenlabs.io/hc/en-us/articles/13313366263441-What-languages-do-you-support | 2026-08-06 | M-H | 2026-11-06 |
| 26 | fal.ai: Veo 3.1 from $0.10/s Fast, $0.20/s standard ($0.40/s with audio per one comparison); Kling 2.5 Turbo Pro $0.07/s; Kling 3.0 Pro $0.112/s; Wan ~$0.05/s | https://blog.siray.ai/fal-ai-alternative-video-api-pricing/ + https://fluxnote.io/blog/ai-video-generation-pricing-guide-2026 | 2026-08-06 | M | 2026-09-06 |
| 27 | Runway direct API: $0.01/credit; Gen-4 Turbo 5 cr/s, Gen-4 12 cr/s, Gen-4.5 25 cr/s (~$0.60/5 s); API credits separate from subscriptions | https://stacksheriff.com/ai-tools/runway-pricing/ + https://fairstack.ai/blog/runway-pricing | 2026-08-06 | M | 2026-10-06 |
| 28 | Kling direct: V3 ~6–8 cr/s; 10 s 1080p ≈ $0.32; free tier watermarked no commercial use; commercial rights from paid tiers | https://renderful.ai/blog/kling-api-pricing + https://www.eesel.ai/blog/kling-ai-pricing | 2026-08-06 | M | 2026-10-06 |
| 29 | Seedance 2.0 direct ≈ $0.067/s on OpenRouter; BytePlus ModelArk official rates $0.39–0.86/video | https://openrouter.ai/bytedance/seedance-2.0 + https://www.atlascloud.ai/blog/case-studies/seedance-2.0-pricing-full-cost-breakdown-2026 | 2026-08-06 | M | 2026-10-06 |
| 30 | No official Suno API; all third-party Suno APIs (incl. Kie's) unofficial/reverse-engineered; their commercial-license claims not legally guaranteeable; Suno in training-data litigation | https://aimlapi.com/blog/the-suno-api-reality + https://terms.law/ai-output-rights/suno/ | 2026-08-06 | H | 2026-12-06 |
| 31 | Higgsfield plans 2026: Starter ~$9–15, Plus ~$17–39, Ultra ~$24–99 (annual vs monthly spread); credits ~150–200/600–1,000/1,200–3,000+; premium clips 40–70 cr; packs ~$5/100 cr expiring ~90 days; no rollover; annual-default signup criticized as dark pattern | https://www.layer3labs.io/guides/higgsfield-ai-pricing (upd. 2026-07-22) + https://www.gstory.ai/blog/higgsfield-ai/ (2026-05-19) | 2026-08-06 | M | 2026-09-15 |
| 32 | Higgsfield aggregates 50+ models (Kling 3.0, Sora 2, Veo 3.1, Seedance 2.0, NB Pro); products: Cinema Studio, Soul ID, UGC Builder (Veo 3 + Seedance 2.0), Marketing Studio (9 ad formats, Hermes agent brief-from-URL), MCP + CLI, Adobe/Figma plugins | https://www.gstory.ai/blog/higgsfield-ai/ + https://ecom-tools.de/en/higgsfield-review/ + https://higgsfield.ai/enterprise | 2026-08-06 | M | 2026-10-06 |
| 33 | Higgsfield documented issues: 2–6× credit-cost increases, throttled "unlimited," AI-only support, moderation stricter than source models, 5–15 s max lengths | https://www.gstory.ai/blog/higgsfield-ai/ | 2026-08-06 | M | 2026-10-06 |
| 34 | Higgsfield first-party API exists (cloud.higgsfield.ai; submit/poll/cancel, bearer auth, webhooks) but public docs sparse; models also routable via eachlabs | https://apidog.com/blog/higgsfield-api/ (2026-01-26) + https://www.eachlabs.ai/higgsfield/higgsfield | 2026-08-06 | M | 2026-10-06 |
| 35 | Higgsfield company: ~$130M Series A (initial $50M closed Sep 2024 + $80M ext.), $1.3B valuation, ~$500M annualized revenue Jun 2026, talks at $5B pre-money; founders Mashrabov & Dulat; enterprise tier SOC 2-aligned/SSO/SLA | https://www.techtimes.com/articles/319394/20260630/ai-video-startup-higgsfield-hits-500m-revenue-eyes-5b-funding-round.htm + https://sacra.com/c/higgsfield/ + https://higgsfield.ai/enterprise | 2026-08-06 | M-H | 2026-11-06 |
| 36 | Kie discount positioning: ~30% below official broadly, 60–70% on selected models; Veo route "~25% of official Google pricing" | https://kie.ai/ (snippet) + https://docs.kie.ai/veo3-api/generate-veo-3-video | 2026-08-06 | M | 2026-09-06 |
| 37 | Higgsfield paid plans include commercial usage rights (per third-party review; first-party ToS not verified — no account) | https://www.gstory.ai/blog/higgsfield-ai/ | 2026-08-06 | L-M | 2026-10-06 |
| 38 | EU AI Act transparency obligations (AI-content disclosure) applicable from 2026-08-02 | Known regulation timeline; flagged for safety-brief verification | 2026-08-06 | M | 2026-09-06 |
| 39 | Kie 4o Image API exists as dedicated family | https://docs.kie.ai/4o-image-api/quickstart | 2026-08-06 | H | 2026-10-06 |
| 40 | Midjourney not present in current Kie Market roster (historic unofficial route in old docs) | https://docs.kie.ai/market/quickstart (absence) + https://old-docs.kie.ai/ | 2026-08-06 | M | 2026-10-06 |

---

## 5. Sources

Primary documentation (retrieved 2026-08-06):
- https://docs.kie.ai/market/quickstart — Kie unified jobs API + roster
- https://docs.kie.ai/ — Kie getting started: retention, rate limits, async model
- https://docs.kie.ai/veo3-api/generate-veo-3-video — Veo route reference, error codes, fallback behavior
- https://docs.kie.ai/veo3-api/quickstart — Veo lifecycle, polling, 1080p endpoint
- https://docs.kie.ai/runway-api/quickstart — Runway route, 14-day retention, expiry flag, task states
- https://docs.kie.ai/4o-image-api/quickstart — 4o Image family
- https://ai.google.dev/gemini-api/docs/veo — Google Veo 3.1 API (pricing, person-generation policy)
- https://developers.openai.com/api/docs/deprecations — Sora 2 / Videos API deprecation (notice 2026-03-24, removal 2026-09-24)
- https://elevenlabs.io/docs/overview/models — ElevenLabs model/language support
- https://higgsfield.ai/enterprise — Higgsfield enterprise claims

Dated third-party analyses (volatile-topic coverage, 2026-dated unless noted):
- https://www.bitdoze.com/kie-ai-review/ — Kie review, 2026-07-17
- https://www.layer3labs.io/guides/higgsfield-ai-pricing — Higgsfield pricing, updated 2026-07-22
- https://www.gstory.ai/blog/higgsfield-ai/ — Higgsfield review, 2026-05-19
- https://apidog.com/blog/higgsfield-api/ — Higgsfield API walkthrough, 2026-01-26
- https://help.apiyi.com/en/sora-2-api-shutdown-alternatives-2026-en.html — Sora 2 shutdown analysis, 2026
- https://www.techtimes.com/articles/319394/20260630/ai-video-startup-higgsfield-hits-500m-revenue-eyes-5b-funding-round.htm — Higgsfield revenue/funding, 2026-06-30
- https://aiinsightsnews.net/kie-ai-review/ — Kie reliability review, 2026
- https://www.aifreeapi.com/en/posts/veo-3-1-pricing — Veo 3.1 pricing guide, 2026
- https://www.aifreeapi.com/en/posts/nano-banana-pro-api-pricing — Nano Banana Pro pricing, 2026
- https://www.atlascloud.ai/blog/guides/cheapest-api-provider-seedance-2-kling-wan — Seedance/Kling/Wan comparison, 2026
- https://renderful.ai/blog/kling-api-pricing — Kling API pricing, 2026
- https://openrouter.ai/bytedance/seedance-2.0 — Seedance 2.0 direct pricing
- https://stacksheriff.com/ai-tools/runway-pricing/ — Runway Gen-4.5 credits math, 2026
- https://blog.siray.ai/fal-ai-alternative-video-api-pricing/ — fal.ai video pricing comparison, 2026
- https://fluxnote.io/blog/ai-video-generation-pricing-guide-2026 — cross-provider pricing, 2026
- https://aimlapi.com/blog/the-suno-api-reality — unofficial Suno API legal analysis
- https://terms.law/ai-output-rights/suno/ — Suno commercial-rights analysis, 2026
- https://www.skool.com/ai-automation-society/kie-ai-just-updated-their-pricing — Kie Veo price-cut community report
- https://www.ilounge.com/articles/sora-2-api-pricing-kie-ai-offers-a-cost-effective-ai-video-generation-integration-solution — Kie Sora 2 pricing
- https://topaihubs.com/item/kieai-affordable-and-stable-unofficial-sora-2-api-for-text-image-to-video-with-audio — unofficial-route labeling
- https://www.trustpilot.com/review/kie.ai — Kie Trustpilot
- https://www.scamadviser.com/check-website/kie.ai — Kie domain trust
- https://discuss.ai.google.dev/t/veo-3-1-image-to-video-blocks-wholesome-commercial-storyboard-child-safety-false-positive/131917 — refusal false-positive evidence
- https://www.eesel.ai/blog/kling-ai-pricing — Kling plans/commercial rights, 2026
- https://www.eachlabs.ai/higgsfield/higgsfield — Higgsfield via router
- https://www.ecom-tools.de/en/higgsfield-review/ — Higgsfield UGC/Marketing Studio detail, 2026
- https://sacra.com/c/higgsfield/ — Higgsfield revenue/valuation data
- https://www.mindstudio.ai/blog/what-is-google-veo-3-video-audio — Veo audio/language limits
- https://www.atlascloud.ai/blog/guides/ai-video-models-native-audio-compared — native-audio model comparison, 2026
- https://costgoat.com/pricing/google-veo — Veo cost calculator, Aug 2026
