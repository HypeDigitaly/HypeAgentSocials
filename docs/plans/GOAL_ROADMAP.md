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
- [ ] **M3 — Virlo collector + brand truth + spin + copy (EN)** (goal-scoped Phase 2).
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
- [ ] **M4 — Kie image generation, draft tier** (goal-scoped Phase 3).
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
- [ ] **M5 — THE FINISH: small end-to-end test run.** One interactive run, EN only:
      Virlo latest AI trends (+ free collectors) → ranking → spin → copy → gates →
      **2–3 Kie images, draft tier, a few dollars max** → pack with digest, scorecards,
      spin rationale, provenance, spend reconciliation vs Kie credit balance, trace.md.
      Verify: no publish path touched, disclosure/provenance recorded, redaction holds.
      Present the pack to the operator. **Goal complete.**

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
