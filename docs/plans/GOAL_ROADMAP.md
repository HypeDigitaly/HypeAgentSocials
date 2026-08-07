# Goal roadmap — "implement all the way through, finish with a real Virlo+Kie test run"

*Written 2026-08-07 from the operator's /goal directive (recorded as DECISION_LOG W8-7):
"PROCEED WITH THE IMPLEMENTATION ALL THE WAY THROUGH UNTIL LAST PHASE — COMPACT CONTEXT
BETWEEN EACH PHASE SO THAT NEXT ONE CAN CONTINUE — THIS GOAL IS FINISHED AS SOON AS LAST
PHASE IS IMPLEMENTED AND SMALL TEST RUN IS TESTED ON VIRLO AND KIE FOR COUPLE IMAGE
GENERATION ONLY IN ENGLISH ONLY BASED ON THE LATEST AI TRENDS AND HYPEDIGITALY SPIN."*

**This file is the cross-compaction state anchor. Each work session: read this file, do the
next unchecked milestone, update the checkboxes, commit, tell the operator to /compact, and
continue.**

## The finish line (verbatim interpretation, recorded so nobody re-litigates it)

The goal's completion criterion is the **test run**, and the test run defines the scope of
"last phase":

- **In scope:** Virlo (latest AI trends, real API/MCP, reads are cheap) → ranking →
  HypeDigitaly spin (brand-truth + spin + copy, with the claim gates) → **Kie image
  generation, a couple of images, draft tier** → run pack + digest + full trace.
- **English only** for the test (Czech machinery stays designed-in but is not exercised).
- **Images only** — no video generation, no voice, no assembly of motion masters.
- **Drafts only, nothing publishes** — Postiz is NOT part of the goal's finish line;
  the never-live-by-default posture is untouched. Phase 6 (real publishing) is *beyond*
  this goal and still gated (incl. the one-time counsel re-ask per W8-4/memory).
- Full plan phases 4–7 (standard tier, Czech recipes, video pipeline, publishing,
  outcome capture) remain on the book but are NOT required by this goal.

## Milestones

- [x] **M1 — engine skeleton** (commit cbc5b88): run identity, trace per RUN_TRACE_SPEC,
      fail-closed config loader, 5-stage stub pipeline, run ledger, 9 exit classes,
      17/17 tests, smoke run verified.
- [x] **W8-6 lands-at edits** (commit 9ca1b27).
- [x] **M2 — zero-cost collection + ranking + digest** (commit 87ae0f3, 2026-08-07).
      68/68 tests; real smoke runs 2026-08-07_9578/_e434/_d6a7 pulled live EN+CS AI-trend
      signal end to end. Two live-endpoint fixes: HF `sort=trendingScore` (not `trending`),
      `retrieved_at` = fetch moment (not source pubDate — retention clocks key on retrieval).
      Four free collectors (HN, Google News RSS en+cs, HF trending, PH feed),
      research artifact store w/ GDPR machinery (retention+expiry job, split provenance,
      keyed handle hash, special-category double exclusion, targeted deletion reaching into
      packs), ranking (evidence classes, family corroboration, fit gate w/ deterministic
      Phase-1 heuristic behind a FitJudge protocol, EN vs CS composites), dedupe index w/
      full §2.8a resurgence rule, run pack + §12.1 digest, offline tests + real smoke run.
      → review, test, commit, **/compact**.
- [x] **M3 — Virlo collector + brand truth + spin + copy (EN)** (commit 10654e8,
      2026-08-07). 121/121 tests; smoke run `2026-08-07_7d0a` live: both Virlo GETs
      succeeded (`/v1/trends/digest` global + `/v1/agents/{id}` monitor read — the
      monitor's `analysis_data.themes` is the on-topic gold; `finalized:false` degrades
      that endpoint only), `short_form_trends` family ranked, spin mapped HypeLead as
      adjacent on the lead-gen topic and forced value-only on far topics, 6 copy briefs
      written, all assets `held — awaiting operator copy` (expected terminal state),
      key nowhere in artifacts (grep-verified). Copy resume = same run_id re-invoked
      (engine has no --resume; documented in copy_gen.py).
      (a) Virlo as a real collector in the engine via its REST API (token in API_KEYS.txt;
      reads only: trends digest / monitor data / existing keyword-search results — NEVER
      create paid jobs from the engine without the cost gate; respect the polling policy).
      **API surface (verified 2026-08-07 from dev.virlo.ai/docs):** base `/v1`, Bearer
      `virlo_tkn_…`; current surface is `/v1/agents` (Orbit/Comet endpoints deprecated,
      removal 2026-08-03 — do NOT build on them even though the MCP keeps legacy tool
      names); Trends resource exposes trending topics / digests / emerging trends as GET
      reads; GET reads are free, POST creation costs credits. Existing recurring agent to
      read: "AI Trends Tracker" monitor id `9c96fddf-dc35-4be0-bbd9-12f4d22aea12`
      (cycles Sundays). Also seed the brand-truth stage from `config/brand_facts.yaml`
      (authored 2026-08-07, commit 6ad692a).
      (b) Brand-truth resolution, config-primary seed: F-A identity + F-C capabilities +
      F-D ICP + F-E CTA set + F-F pricing policy ("prices never stated") as config YAML,
      sourced from docs/research/NOTION_KB_INVENTORY.md + Notion "Čísla a sliby" (F-H:
      10 approved claims — mirror by *reference*, fetch at run time or snapshot with id).
      (c) Spin mapping + EN copy generation behind a pluggable TextModel provider.
      **RESOLVED 2026-08-07 (pre-checked while M2 built): text-model provider.** Kie's
      official docs expose NO chat/LLM family (the DeepSeek chat endpoint at
      kieai.erweima.ai is third-party-reported legacy, not in docs.kie.ai — do not build
      on it). M3 therefore ships a `TextModel` protocol with two providers: (1)
      `interactive-file` — the run writes a structured request file (topic, brand facts,
      constraints), the operator/Claude fills the response file, the run consumes it and
      all deterministic gates still run on the output; this is the finish-line-test path,
      costs nothing. (2) `openai-compatible-http` — generic config-driven provider
      (base_url, model, key file path) so any future key drops in without code change.
      (d) Claim gates on copy: deterministic passes (claim-shaped-string detection vs the
      10-row ledger + abstain rules) — the LLM judge halves stay pluggable.
      → tests, commit, **/compact**.
- [x] **M4 — Kie image generation, draft tier** (commit e93f050, 2026-08-07).
      153/153 tests. Model strings VERIFIED vs docs.kie.ai (`google/nano-banana`
      live-confirmed 2×; seedream corrected to `bytedance/seedream-v4-text-to-image`;
      "nano-banana-pro" doesn't exist → `nano-banana-2`). Real-spend proof: 8 credits
      ($0.04) total — one full round trip + one kill/resume with real paid work,
      resolve-by-query adopted the job with ZERO createTask on restart, balance
      10080→10072 (each submission billed exactly once). recordInfo returns
      `state`/`resultJson`/`creditsConsumed`; `model` echoes request (non-authoritative,
      §5.6 three-state rule governs). Credit balance: GET /api/v1/chat/credit.
      Smoke `2026-08-07_30f1`: held copy → media plans only, $0, zero API calls.
- [x] **M4b — `--resume <run_id>` CLI** (commit 2f35ae7, 2026-08-07). 164/164 tests.
      Re-enters copy→media→packaging→digest via persisted resume_state.yaml; trace seq
      continues monotonically with a resume decision marker; no dedupe re-trigger.
      **API surface (verified 2026-08-07 from docs.kie.ai/market/quickstart):** unified
      jobs API — `POST https://api.kie.ai/api/v1/jobs/createTask`, poll
      `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=...`, `Authorization: Bearer`;
      per-model params vary; image routes available include GPT Image 2, Nano Banana 2,
      Seedream 5, Flux-2. Draft tier = cheapest adequate image route in the registry.
      Model registry (image routes only), routing contract, cost gate (pre-submission,
      per-run cap from config), write-ahead spend ledger + (identity, attempt) idempotency
      (§8.5 — intent row before submission, resolve-by-query on restart, submitted-unknown
      state), async job polling per §8.13, download + checksum re-host into the pack
      (provider URLs nowhere in a pack), §5.6 three-state delivered-route inference
      (identity-reported / substituted-unknown / assumed-as-requested), people-free
      composition default (R2-M18). Image prompts carry HypeDigitaly brand context; the
      model picks brand assets per W8-6 (taste, not truth). Spend telemetry in trace
      (spend events) + digest cost lines go live.
      → tests incl. kill/resume without double-spend, commit, **/compact**.
- [x] **M5 — THE FINISH: small end-to-end test run. DONE 2026-08-07.**
      Run **`2026-08-07_7ded`** (fresh run + two `--resume` invocations, exit 0 each):
      - **Virlo live AI trends in**: "Claude AI for Productivity and Business Hacks",
        "AI Tools for Lead Generation (General)", "Claude AI for Real Estate
        Professionals" (short_form_trends family, AI Trends Tracker monitor read).
      - **HypeDigitaly spin**: lead-gen topic mapped to HypeLead (adjacent,
        product-adjacent CTA); far topics forced value-only with content CTA.
      - **Operator copy** (Claude-as-operator) for 2 assets; **the claim gate blocked
        attempt 1 of the LinkedIn asset live** ("treating AI as…" tripped the
        therapeutic lexicon's 'treat' — §14.1a over-blocking by design), repair
        request attempt 2 written with the span named, reworded copy passed. The
        repair loop is proven on real content, not just tests.
      - **2 real Kie images generated** (google/nano-banana draft, $0.02 each,
        8 credits total; balance 10072→10064): both exactly on-brief, people-free,
        no text, no logos. Provenance `assumed-as-requested`, checksums recorded,
        provider URLs nowhere in pack, key nowhere in artifacts (grep-verified).
      - Spend ledger: exactly 2 intent rows, 1 paid submission each, no re-billing
        across resumes. Pack: digest + scorecards + spin rationale + provenance +
        media under `logs/runs/2026-08-07_7ded/pack/`. Nothing published; Postiz
        untouched. **W8-7 GOAL COMPLETE.**

## Post-goal backlog (not part of W8-7; next campaign picks from here)
- Czech copy path (M3 designed it in; exercise it), logo overlay composition (§4.4a),
  LLM judge halves of the gates (spin/voice/claim pass 2), video pipeline (Phase 3-full),
  Postiz draft delivery (Phase 6 gate — counsel re-ask fires once there, per W8-4).

## CAMPAIGN W8-9 — quality overhaul (approved 2026-08-07; plan of record:
## ~/.claude/plans/recursive-stargazing-sunrise.md; flow map: docs/architecture/FLOW_MAP.md)

- [x] **Q0 — W8-8 process summary landed** (commits 2026-08-07): process_summary.md every
      run + `--summarize` CLI + full prompts in provenance. 178/178 tests. Verified on 7ded.
- [x] **Q0b — groundwork**: DECISION_LOG W8-8/W8-9 rows, brand_facts visual-policy
      reversal (third-party logos/screenshots/people allowed; no fake screenshots of OUR
      product UI), config/style_guide.yaml (inspiration-corpus distillation), FLOW_MAP.md,
      .env + .env.example (API_KEYS.txt deleted), Virlo monitor v2 with data-intelligence
      created (`623203a9-c09c-4763-85e0-1c177b5af760`, $1.50/weekly cycle — deactivate old
      `9c96fddf-…` once v2 finalizes).
- [x] **Q1 — .env loader + rich Virlo collection** (builder in flight): env>-.env->legacy
      precedence; free /videos + /slideshows sub-path reads (page cap, one pass);
      virlo_corpus.yaml (full tactics/why_it_works/panel_texts, 30-day retention regime);
      top-K image download for vision analysis; digest read default OFF; monitor_ids
      fallback list. → verify, commit, /compact if needed.
- [x] **Q2 — OpenRouter LLM client** (`anthropic/claude-sonnet-5`, key OPENROUTER_API_KEY
      in .env): system prompts, JSON output w/ parse-retry, vision content-parts, per-run
      ceilings, llm wallet in spend ledger + trace. Offline-tested via FixtureFetcher.
- [x] **Q3 — LLM node graph**: N-A trend/visual analyst (→ analysis/viral_playbook.yaml),
      N-C copywriter (LinkedIn 7-beat / IG-TikTok caption + per-slide carousel texts;
      claim gate over every slide; interactive-file fallback kept), N-D image-prompt
      crafter (full prompt → provenance).
- [x] **Q4 — media upgrade**: Nano Banana 2 standard tier (verify price live), remove
      draft-only hard-raises, per-slide ledger identity `destination:slideNN`,
      PROMPT_PATTERN_VERSION → 2, W8-9 constraint set, caps $3/run $6/day; N-E vision-QA
      readback gate (text match + archetype; 1 retry then held). Kill/resume test on a
      carousel (no double-billing).
- [x] **Q5 — brand assets**: pull HypeLead v2 pack essentials (logos, wordmarks, 7 post-*
      templates) from Notion into assets/brand/ for prompt grounding.
### Q6 COMPLETION RECORD (2026-08-07)
- Q1–Q5 committed through `98f74ce`; **defect-fix round committed as `539e808`**
  (316/316 tests, offline-only, secret-scanned): per-node max_tokens
  (4000/4000/6000/1000), finish_reason truncation detection (retry w/ doubled budget →
  LlmTruncatedError degrade), crafted-prompt completeness validation + compose_prompt
  fallback, call cap 60 / usd cap $2.00 / qa_reserved_calls 16, N-D prompt-hygiene
  rules, strict exact-match QA rubric, DELTA spend events (sum==ledger==balance delta,
  test-enforced), carousel 6–10-slide+end_card validation (1 retry, accept-with-note).
- Live run `2026-08-07_e4d8` (exit 0, 12m09s, real cost ~$1.06, balance 10056→9968,
  11 images billed exactly once) was the evidence base: quality leap confirmed, 6
  defects found, all fixed above.
- **Q6(c) re-audit DONE**: verdict + 6 ranked recommendations in FLOW_MAP.md §7
  (artifact republished, same URL). Backbone confirmed structurally sound — defects
  were parameter/validation class, not structure class. Open 🟠 proposals awaiting
  operator: R1 ranking freshness window, R2 analysis-after-ranking reorder, R3
  scorecard band calibration, R4 playbook platform-norm polish, R5 (deferred) parallel
  image submission, R6 ~$1 live confirmation re-run.

- [x] **Q6 — FINISH (operator directive 2026-08-07): test thoroughly, then re-audit the
      flow itself.** (a) Full EN test run: 1 LinkedIn post + hero image, 1 IG carousel
      (~6 slides + caption), real Virlo + OpenRouter + Kie, ≤$2.50. (b) Analyze results:
      process_summary.md, trace, spend ledger, QA verdicts, pack quality vs the
      inspiration corpus. (c) THEN re-analyze the ENTIRE flow start-to-finish against
      FLOW_MAP.md — is the structure optimal for the goal (value-packed, trend-grounded,
      platform-native assets)? Propose structural improvements with evidence, update
      FLOW_MAP.md + the artifact, and put the recommendation to the operator. The
      campaign is NOT done at "tests pass" — it is done when the flow has been re-judged
      against its results.

## CAMPAIGN W8-10 — output-quality deep audit → rebuild (2026-08-07; plan of record:
## ~/.claude/plans/recursive-stargazing-sunrise.md, superseded W8-9 content in same file)

### W8-10 STATUS SNAPSHOT (2026-08-07 ~17:11, pre-compaction — read this first after /compact)
- Three-lens audit of run e4d8 DONE (UX/UI: 0/10 shippable, 12 systemic defects;
  copywriter: nativeness 3-4/10, 5 smoking guns in our own prompts; marketer:
  per-post verdicts + post-mix strategy + code seams). Virlo inspiration-fidelity
  trace DONE: style-transfer fidelity was ~0% (winners: 96% photoreal, 92% sticker
  text, 71% real logos, 50% people; we generated 100% editorial cards). All findings
  + full build spec live in the plan file.
- **BUILD COMPLETE, COMMITTED `f4b2943`** (515/515 tests, secret-scanned): N-C founder
  voice (12 countable rules, exemplars injected, temp 0.9, lang pinned en), N-F
  humanness critic (blind editor, rewrite re-enters claim gate), N-D two-section
  prompts + image_brief-on-carousel fix + real-logo rule + relevance rule + archetype
  rotation, N-E art-director QA (relevance/logos/composition/series vs cover,
  mismatches⇒never-pass, $0 pre-spend leak checks), Phase 8 dynamic inspiration
  (virlo_media_manifest join, views-ordered+thumbnail-quota image selection, labeled
  images, analyzed_items per-creative records w/ summary+consists_of, deterministic
  visual_profile w/ recommended_generation_mode, photographic_ugc register, 8
  generation modes, editorial register NO LONGER hardcoded), post_mix
  (value_only/playbook/promotional, promo-never-first; value_only = zero brand
  grounding but @handle+disclosure kept), R1 freshness 14d, R2 ranking→analysis
  reorder (winning themes only), R3 quantile bands, R4 norm polish, LinkedIn aspect
  16:9. Person policy: synthetic non-identifiable people ALLOWED, identifiable/
  celebrity BANNED.
- FLOW_MAP.md rebuilt to W8-10 + artifact republished same URL (`d0178ad`). STANDING
  PRD RULE (memory flow-map-artifact-always-current.md): every flow amendment ⇒
  FLOW_MAP update + artifact republish same URL, same cycle.
- **IN FLIGHT RIGHT NOW: live confirmation run `2026-08-07_fa51`** (operator-authorized
  "PROCEED WITH THE FULL TEST RUN AFTER EVERYTHING LANDS"; post_mix 1/1/1 enabled in
  theme yaml, commit `d0178ad`; caps $2 LLM/$3 img/$6 day unchanged; expected
  ~$1.50-2.50, ~12-20 min; background shell task). At snapshot time it was in the
  copy stage making OpenRouter calls.
- **ON RUN COMPLETION (the standing next steps): analyze `2026-08-07_fa51` fully** —
  process_summary.md, trace, spend reconciliation (delta events must sum==ledger==
  balance move), VIEW every generated image, judge against the audit checklist: real
  logos present+undistorted, photoreal/dynamic modes actually used (NOT all editorial
  cards), zero scaffolding/token/quote leakage, series consistency, copy passes
  slop-regex + voice rules, one ask per asset, post-mix distribution respected
  (1 value-only w/ no brand mention, 1 playbook w/ comment-CTA, 1 promotional),
  carousels 6-10 slides w/ end cards (numbered promises fulfilled), 100% QA coverage,
  N-F critic diffs visible. Then report before/after vs e4d8 to operator; decide
  whether to keep post_mix on; tick W8-10 checkbox; update FLOW_MAP §7 status +
  republish artifact if flow facts changed.
- [x] **W8-10 — confirmation run `2026-08-07_fa51` COMPLETED + fully analyzed 2026-08-07
      (~17:35).** Verdict: partial confirmation — the W8-10 machinery that ran is a step
      change up from e4d8, but a same-day idempotency gap kept Phase 8 out of the loop
      entirely. Results record below; fix round W8-11 proposed to operator.

### W8-10 CONFIRMATION RUN RESULTS (`2026-08-07_fa51`, exit success, 23m, $1.32 LLM + $0.24 media)

**What PASSED (before/after vs e4d8):**
- Copy voice: night-and-day. All 6 assets gated-pass attempt 1; founder first-person,
  short rhythms, concrete verbatim prompts as the "usable artifact", zero
  "creators are reporting", zero slop-tell regressions. N-F critic rewrote all 3
  LinkedIn assets (diffs traced seq 47/75/103).
- post_mix 1/1/1 EXACT: 3bc9=value_only (zero brand mention ✓ handle+disclosure ✓),
  948c=playbook (comment-CTA ✓), bcba=promotional (brand+URL, promo not first ✓).
- Real third-party logos RENDERED AND RECOGNIZABLE where crafted prompts ran:
  n8n + Apify on 3bc9_linkedin (QA pass 6/6 bools). bcba_linkedin delivered a
  PHOTOREAL UGC hand-holding-phone shot (the e4d8 audit's #1 missing style) — QA pass.
- Zero scaffolding/font-name/hex/quote leakage on both crafted images. Spend
  reconciliation exact (ledger==balance delta, media $0.24, LLM $1.32 ≤ caps).
- Claim gate + N-D validation + fail-closed degradation all fired correctly as designed.

**What FAILED (the W8-11 fix list, priority order):**
1. **Same-day idempotency starved the whole Phase 8 path**: every source fetch was
   "already captured today — skip" (§8.5) → no virlo_corpus.yaml/media manifest
   materialized for THIS run → N-A skipped → no analyzed_items/visual_profile → all
   modes fell back to editorial register + style-guide rotation. Dynamic inspiration
   NEVER EXERCISED live. Fix: on fetch-skip, re-materialize corpus+manifest from the
   day's captured store/raw payloads so analysis always has input.
2. **N-C×N-D contradiction killed ALL 3 IG carousels**: copywriter slide bodies came
   out 29–37 words; N-D's 28-word rendered-body cap + exact-text-complete requirement
   are then mutually unsatisfiable → all 3 crafted sets invalid → whole sets degraded
   to compose_prompt heroes (no slides generated at all). Fix: enforce ≤28-word slide
   bodies at N-C generation+validation time; exempt the monospace prompt-quote slide
   from the cap (it legitimately carries the verbatim prompt).
3. **compose_prompt fallback bypasses claim gate on image text**: gate correctly
   blocked N-D's '35,095' (missing required qualification) — then the fallback prompt
   rendered '35,095 AI-handled answers. Zero spreadsheets.' unqualified anyway
   (948c_linkedin hero, generated + delivered). Fix: run fallback prompts through the
   same claim gate; gate-fail ⇒ held, never submit.
4. **QA skip on fallback images = 4/6 images unreviewed**: "no crafted on-image text"
   skips N-E entirely — exactly the riskiest images. 948c_instagram hero is e4d8-class
   garbage (gibberish headlines, literal 'EYEBROW TAG' pills rendered, Lorem ipsum,
   wrong CTA keyword 'GROWTH' vs copy's 'PLAYBOOK', random Slack/GDrive/Mailchimp
   logos); bcba_instagram hero is off-topic generic SaaS filler; both shipped to pack
   unreviewed. Fix: N-E always runs (subject relevance/logos/composition rubric works
   without exact-text list); fallback carousel prompts must not describe a whole
   carousel in one image (model renders a 2x2 collage).
5. **Fabricated speaker personas**: "I'm Marcus." / "I'm Radka." / "Pavel Čermák
   here" — NO name exists anywhere in copy_requests; the model invented all three
   identities (one dangerously close to the real operator's name) and attached
   first-person experience claims to them. Fix: pin the speaker in config (real,
   operator-approved persona per destination) and hard-fail any other proper-name
   self-introduction.
6. **N-F critic failed on all 3 IG assets** (2× truncated even at 4000-token retry,
   1× malformed JSON) → originals kept (fail-safe worked, but IG copy went
   un-critiqued). Fix: raise N-F budget for carousel assets (base 4000/retry 8000) or
   make the critic return per-field diffs instead of the full rewritten asset.
7. Minor: N-C base max_tokens 4000 truncated on ALL 6 first attempts (every asset
   needed the corrective retry — doubles copy latency+cost; raise base to 6000);
   R1 freshness window skipped 0 of 566 news rows (window keys on dates that are all
   recent — semantics need a second look); stale '1.91:1' aspect string still inside
   compose_prompt fallback text (theme is 16:9 now); AI-rendered Claude logo on
   bcba_linkedin is orange-ish but NOT the real Claude mark (QA passed it —
   logo-fidelity rubric too lenient; n8n/Apify rendered fine).

**Scoreboard: 2/6 images shippable (both crafted+QA'd LinkedIn heroes — vs 0/10 in
e4d8), 6/6 copy assets shippable pending persona fix. post_mix stays ON (worked
exactly).**

## Standing constraints that bind every milestone (do not re-derive)

- Secrets: API_KEYS.txt is untracked, never committed, never logged; keys never in prompts.
- Never `git add -A`; stage explicitly. Commits end with the Claude co-author line.
- Postiz: five real brand channels connected — draft-state calls only; not in this goal.
- Virlo: never poll in a loop; reads free, creation costs credits; monitor cycle Sundays.
- Kie: 10,080 credits; silent-fallback-on-content-review hazard → §5.6 inference rule.
- Frozen eval sets are never read by the prompt author (me).
- No legal agents / no counsel nagging (W8-4, memory) — resurface once at Phase 6 only,
  which is beyond this goal.
- Engine: Python 3.13, stdlib+pyyaml only, everything traces per RUN_TRACE_SPEC.
