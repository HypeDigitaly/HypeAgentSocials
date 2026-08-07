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
- [ ] **Q1 — .env loader + rich Virlo collection** (builder in flight): env>-.env->legacy
      precedence; free /videos + /slideshows sub-path reads (page cap, one pass);
      virlo_corpus.yaml (full tactics/why_it_works/panel_texts, 30-day retention regime);
      top-K image download for vision analysis; digest read default OFF; monitor_ids
      fallback list. → verify, commit, /compact if needed.
- [ ] **Q2 — OpenRouter LLM client** (`anthropic/claude-sonnet-5`, key OPENROUTER_API_KEY
      in .env): system prompts, JSON output w/ parse-retry, vision content-parts, per-run
      ceilings, llm wallet in spend ledger + trace. Offline-tested via FixtureFetcher.
- [ ] **Q3 — LLM node graph**: N-A trend/visual analyst (→ analysis/viral_playbook.yaml),
      N-C copywriter (LinkedIn 7-beat / IG-TikTok caption + per-slide carousel texts;
      claim gate over every slide; interactive-file fallback kept), N-D image-prompt
      crafter (full prompt → provenance).
- [ ] **Q4 — media upgrade**: Nano Banana 2 standard tier (verify price live), remove
      draft-only hard-raises, per-slide ledger identity `destination:slideNN`,
      PROMPT_PATTERN_VERSION → 2, W8-9 constraint set, caps $3/run $6/day; N-E vision-QA
      readback gate (text match + archetype; 1 retry then held). Kill/resume test on a
      carousel (no double-billing).
- [ ] **Q5 — brand assets**: pull HypeLead v2 pack essentials (logos, wordmarks, 7 post-*
      templates) from Notion into assets/brand/ for prompt grounding.
### Q6 STATUS SNAPSHOT (2026-08-07, pre-compaction — read this first after /compact)
- Q1–Q5 COMMITTED (through 98f74ce): .env, rich Virlo collection, OpenRouter LLM client,
  N-A/N-C/N-D nodes, NB2 standard tier (LIVE price 8cr/$0.04), per-slide ledger, N-E QA,
  brand assets. 283/283 tests at last commit.
- **Full live test run DONE + ANALYZED: `2026-08-07_e4d8`** (exit 0, 12m09s, real cost
  ~$1.06 = $0.62 LLM + $0.44 images/88 credits, balance 10056→9968). Output quality:
  major leap — editorial-carousel archetype achieved, 7-beat LinkedIn copy w/ honest
  trend attribution, gates + QA + per-slide billing all proven live.
- **6 defects found (analysis in chat + evidenced in the run dir): (1) max_tokens 1500
  truncation — 2 LinkedIn assets fell to held, carousels 2-4 slides not 6-10, slide_04
  prompt cut mid-sentence → hallucinated filler text in image; (2) per_run_call_cap 20
  starved N-E QA (4 of 11 images QA'd, broken slide among skipped); (3) instruction
  leakage in images ('UII Label' pill, literal 'Montserrat SemiBold', quoted headline);
  (4) QA rubric too lenient (passed duplicated phrase); (5) media spend events record
  CUMULATIVE → summary reported $2.64 vs real $0.44 (reporting only); (6) missing
  end-card/6-slide validation.**
- **IN FLIGHT: fix builder agent** (python-pro, background) addressing all 6: per-node
  max_tokens (analyst 4000/copy 4000/craft 6000/QA 1000), finish_reason truncation
  detection (never accept truncated output), crafted-prompt completeness validation,
  call cap 60 + qa_reserved_calls 16, prompt-hygiene rules, strict QA rubric, spend
  delta fix, slide-count validation. On its completion: pytest, secret scan, commit.
- **THEN the Q6(c) flow re-audit** (not started): judge the flow structure against run
  e4d8's evidence, update FLOW_MAP.md + artifact
  https://claude.ai/code/artifact/576e658b-81ea-4d1e-bc19-3fcdf99312f3 (favicon 🗺️,
  same URL), propose structural improvements to the operator. Optionally re-run a
  test after fixes to confirm (cheap: ~$1).
- Known open oddities for the re-audit: ranking rescores stale Google News candidates
  (566 noise rows), spin bands all "Low", LinkedIn hero got decorative toggle switches,
  analyst prompt was 70k tokens (trim), platform_norms "not observed in corpus" for
  LinkedIn/IG (corpus is TikTok-heavy — inspiration folder fills the gap).

- [ ] **Q6 — FINISH (operator directive 2026-08-07): test thoroughly, then re-audit the
      flow itself.** (a) Full EN test run: 1 LinkedIn post + hero image, 1 IG carousel
      (~6 slides + caption), real Virlo + OpenRouter + Kie, ≤$2.50. (b) Analyze results:
      process_summary.md, trace, spend ledger, QA verdicts, pack quality vs the
      inspiration corpus. (c) THEN re-analyze the ENTIRE flow start-to-finish against
      FLOW_MAP.md — is the structure optimal for the goal (value-packed, trend-grounded,
      platform-native assets)? Propose structural improvements with evidence, update
      FLOW_MAP.md + the artifact, and put the recommendation to the operator. The
      campaign is NOT done at "tests pass" — it is done when the flow has been re-judged
      against its results.

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
