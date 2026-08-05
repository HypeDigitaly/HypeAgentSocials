# DESIGN PHASE MASTERPLAN — HypeAgentSocials

**Goal:** Execute the design phase (Stages 0–5) of `HypeAgentSocials_InstructionsAssignment.md`: deep research (Block A viral AI video, Block B topic extraction, Stage 3 systems) → architecture plan → expert review → Stage 5 approval presentation. **No implementation.**

**Deliverable constraint:** no product code, pseudocode, CLI syntax, config syntax, or mandatory product folder tree in any deliverable. **Diagrams (mermaid/ASCII) ARE allowed and encouraged.** Conceptual knob tables in prose are the permitted form for config content.

**Governance note:** this repo has no CLAUDE.md/CODING_GUIDELINES.md — the assignment + this plan are the governing documents for this phase.

**Conductor:** main thread only. All waves flat (shape **a**) — leaf executors, spawn chain depth 1 (main → leaf), no agent spawns sub-agents. No §9a trigger fires (≤4 tasks per domain per wave, decomposition known up front, all output paths disjoint).

**Per-stage reporting (assignment obligation):** after EVERY wave barrier, the conductor states in chat: what was concluded · what inputs are still needed from the human · what the next review/test step is.

---

## Locked decisions (binding on all agents)

| ID | Decision |
|----|----------|
| D-01 | Design phase only; implementation is a separate future plan after human approval |
| D-02 | Output languages = per-theme config **array**; every listed language gets its own full, first-class output set (first theme: `cs` + `en`). Never a translation pass. **Every architecture layer must state its cs behavior explicitly** |
| D-03 | Brand truth: **Notion MCP** primary → theme config → live public website verification. Degrade honestly; unattended runs downgrade to research-only below a confidence threshold |
| D-04 | Accounts: **Kie.ai trial** + **Postiz trial** exist. **Higgsfield = paper evaluation only** (output must be confidence-tagged + open decision, not a firm recommendation). **No paid official X API** |
| D-05 | Runtime: Windows-first console app (run.bat + Task Scheduler) now; Linux server cron later → cross-platform mandatory |
| D-06 | Tech stack: recommended in the architecture plan with justification + rejected alternatives (Python = working hypothesis; verified by brief C2) |
| D-07 | Review UX: human reviews packs manually in an organized output folder; later optional config-driven upload to Notion. Operator = solo, marketing-literate, limited patience for file archaeology |
| D-08 | **Default stance on X for v1** (pre-decided so research isn't paralyzed): assume no paid X reads; design X as degraded/optional research source; third-party reseller access = open decision for the human (W2.5 gate) |

## Research flags (scouted + review-hardened, 2026-08-05 — assigned briefs MUST address these)

| Flag | Consequence |
|------|-------------|
| F-1 | **Reddit ToS prohibits commercial API use**; OAuth approval manual, 2–4 wks; public JSON endpoints are same-ToS and CDN-blocked in practice. Realistic fallbacks = licensed aggregator or human-curated input — B1/B2 must treat Reddit as a legal decision point with only real options |
| F-2 | **X free API tier is dead.** Read path per D-08. Note: X-as-*publish*-destination (via Postiz user-OAuth) is a SEPARATE decision from research reads — C1/B1 must not conflate them. Reseller ToS on storing/deriving content feeds the artifact-retention question |
| F-3 | **Model churn is structural** (e.g. Sora 2 API sunset ~Sept 2026). No single-model pinning; deliverable = pinned model registry concept with last-verified dates + re-verification cadence. Churn also invalidates prompt patterns and price tiers, not just model IDs |
| F-4 | **Publish destinations must be a config allowlist with ONE enforcement point** (not a Reddit special case) + defense-in-depth: research-only channels never connected in Postiz at all |
| F-5 | Native-audio video models are standard → **spoken** fake claims are a new safety surface. Enforcement consequence must be researched: lock dialogue to approved script lines vs ASR-verify generated audio. Czech speech quality in native-audio models is materially weaker → possible en/cs pipeline fork |
| F-6 | Higgsfield bundles UGC Builder + Marketing Studio + agent orchestrator; sparse API docs → assess complement-vs-competitor; paper-only eval must output confidence + open decision |
| F-7 | **Czech is not a translation pass**: Czech slop lexicon ≠ translated English; Czech on-screen text/diacritics routinely mangled by video models; Czech TTS quality varies hugely; Czech platform norms differ. Every relevant brief states its cs answer |
| F-8 | **EU AI Act Art. 50 synthetic-content transparency is in force** + platform-native AI labels (TikTok AIGC, YouTube altered-content, Meta AI info) are separate obligations. Technical landmine: re-encode/assembly steps typically strip C2PA provenance. This is an architecture input, not a legal footnote |
| F-9 | **Scraping pessimism is the default**: headless-browser detection in 2026 is near-total on major surfaces; LinkedIn has no public read API + enforced anti-scraping; Google Trends has no stable official API; Meta Ad Library API needs ID verification. Playwright justified only where a source is genuinely open. The honest architecture is likely "almost no scraping + APIs/licensed data + operator-supplied inputs" |

---

## Existing exemplar corpus (user-provided, `docs/marketing/`)

Curated real-world winning content + brand context that research and architecture MUST use as evidence, not ignore:

- `Winning Posts from competitors Linkedin.txt` — exemplar viral LinkedIn posts (en) → primary voice/hook evidence for T13, secondary for T1
- `Gojiberry's 7 Figure GTM Playbook.txt`, `How Gojiberry went from 1M€ to 3.5M€ ARR in 3 months.txt`, `The-LinkedIn-High-Intent-Outreach-System-…​.md` (+2 PNGs) — competitor GTM/content playbooks → T1/T13 evidence for what actually works in this niche
- `HypeLead Areas GTM_Marketing_Strategie.txt` — HypeLead's own GTM/ICP strategy (cs) → **brand context**, feeds T8 (Czech market) and T14 (brand-truth taxonomy: ICP segments already enumerated here)
- `GojiBerry_YoutubeInspiration/*.txt` — **4 real GTM/growth video transcripts (~150 KB, confirmed W0.5; user: "analyze each meticulously")**: `GojiBerry_0_to_1_Mil.txt` (full GTM course, 0→$1M ARR multi-channel engine), `GojiBerry_90_Day_Playbook.txt` (customer-first GTM playbook), `GojiBerry_ColdEmail_01.txt` (cold-email playbook), `GojiBerry_Reddit_01.txt` (Reddit growth system — practitioner evidence for OD-2 Reddit stance) → feed T1 (content practices in-niche), T5 (Reddit evidence), T8 (niche/ICP context), T13 (voice/hook patterns)

**Architectural consequence to carry forward (T13, T17 §6/§14):** brand voice should be grounded in a curated per-theme **exemplar corpus** (winning posts as few-shot/voice reference), not rules alone — this folder is the first theme's seed corpus, and the theme config concept must have a place for it.

## Deliverables layout (process docs for THIS repo — not the product's tree)

```
docs/
  STAGE0_RESTATEMENT.md                 (W0, conductor)
  plans/DESIGN_PHASE_MASTERPLAN.md      (this file)
  research/
    A1_viral_video_practices.md  A2_video_providers.md  A3_video_prompts_skills.md  A4_assembly_postproduction.md
    B1_sources.md  B2_extraction_methods.md  B3_ranking_scheduling.md  B4_czech_b2b_market.md
    B5_trend_intelligence_platforms.md   (late W1 addition, operator-requested 2026-08-06: TikTok/IG/YouTube deep-dive + buy-vs-build on trend-watching platforms; T16 folds it into SYNTHESIS as addendum; W2.5 + W3 consume it)
    C1_notion_postiz_integration.md  C2_platform_constraints_stack.md  C3_cron_ops_state.md
    C4_operator_review_ux.md  C5_voice_models_judge.md  C6_brand_truth_design.md  C7_legal_compliance.md
    SYNTHESIS.md                        (W2)
  architecture/
    DECISION_LOG.md  RISK_LOG.md        (seeded W0, appended each wave)
    drafts/DRAFT_A_core_pipeline.md  drafts/DRAFT_B_runtime_safety.md   (W3)
    ARCHITECTURE_PLAN.md                (W3b assembler, W5 fixes)
    STAGE5_APPROVAL_SUMMARY.md          (W6, conductor)
  reviews/
    R1_architecture.md  R2_ai_pipeline.md  R3_marketing.md  R4_legal.md  R5_scenarios.md   (W4)
```

**Every research brief MUST contain, in this order:**
1. **"What this means for the operator"** — half-page plain-language decision summary (no jargon)
2. Body answering its mandate
3. **Decision table** — "decisions this brief unblocks (→ architecture §X)" and "decisions it defers (→ open decision)"
4. **Fact-ledger rows** (fixed shape: claim | source URL | retrieved date | confidence | recheck-by) for every volatile claim
5. **Sources** — dated URLs; for volatile topics (models, pricing, API terms) ≥60% from the last 6 months

**Thin-brief definition (barrier-enforceable):** missing any of the 5 sections above, or <5 dated sources on a web-research brief, or an unanswered must-answer item.

---

## WAVE 0 — Setup + Stage 0 (conductor only)

1. `git init` + `.gitignore` + commit assignment + this plan.
2. Create `docs/` skeleton.
3. Write `docs/STAGE0_RESTATEMENT.md` covering ALL mandated Stage 0 bullets (research-vs-content split, config topics + MCP spin, viral video as design driver, extraction incl. Playwright, Kie/Higgsfield, Postiz path, human gate + voice, multi-theme + console, cron end goal, design-phase success criteria, out-of-scope-until-approved).
4. Seed `DECISION_LOG.md` (D-01…D-08 locked; open: X reseller, Reddit stance, Higgsfield role, MCP-vs-REST for cron) and `RISK_LOG.md` (F-1…F-9 + the 8 review-risk areas in W4/R1 + **"D-02 doubles media spend against trial quotas"**).

**Barrier:** files exist; Stage 0 bullet checklist complete. Conductor reports per stage-protocol.

## WAVE 0.5 — Human fact intake (conductor asks the user; empirically cheap, architecture-routing facts)

Ask the user for: Kie.ai trial credit balance + actually-enabled model roster · Postiz plan tier, connected channels, and whether draft-without-schedule actually works on that plan (kill-switch fact) · Notion workspace shape — does brand truth already exist there and in what structure? · is X reseller spend acceptable (resolves D-08's open half)? · Meta/LinkedIn business-account + app-review status · fill or drop the empty `GojiBerry_YoutubeInspiration/*.txt` placeholders.
If the user is unavailable: proceed with pessimistic defaults, log each as an open decision.

---

## WAVE 1 — Deep research fan-out (shape: a | 15 leaf agents | all paths disjoint | depth 1)

> Tool-fit rule (hard): web-research tasks ONLY to agents with WebSearch/WebFetch + Write; expertise tasks may go to non-web writers. `general-purpose` used only where no specialist has both web + write. No agent reads another agent's unfinished output; where a brief depends on a parallel brief's facts, it MUST declare **assumed-input placeholders** explicitly (reconciled in W2).

### Domain: viral video (Block A) — 4 tasks

**T1 → `content-marketer` → `A1_viral_video_practices.md`** (web)
Block A items 1, 2, 6, 7, 8: hooks 1–3s, pacing, caption *practices*, pattern interrupts, loops, faceless vs UGC, B2B-safe adaptations; consumer-vs-B2B cases + failure modes; accept/reject rubrics incl. audio items (F-5) AND what the operator does on rejection; workflow idea→script→keyframes→variants→human pick→publish-prep; cron-safe vs human-gated split. Must answer: how multi-shot-native models change keyframe-first; current B2B-safe UGC pattern; volume-vs-polish — what do benchmark B2B teams actually ship (2 polished vs 20 mediocre reels/week)? Input: exemplar corpus (`docs/marketing/`) as evidence of what wins in this exact niche — extract hook/structure patterns transferable to video.

**T2 → `general-purpose` → `A2_video_providers.md`** (web)
Block A items 3, 4 — **sole owner of ALL Kie.ai/Higgsfield facts** (C1 must not fetch them): Kie.ai deep eval (routed roster, credit pricing, API, retention, per-ROUTED-MODEL commercial rights — not just Kie's own ToS); Higgsfield paper eval per F-6; alternatives with tradeoffs; T2V vs I2V vs keyframe-first vs multi-shot-native fit. **Async job lifecycle** (submit→poll/webhook→minutes-long→expiring URL→re-host) and its consequence for cron design; **refusals as normal outcomes** (rates for marketing prompts, refusal signals, re-prompt vs degrade-to-plan); **idempotency×money** (provider idempotency keys / spend-ledger hooks against double-billing); **routing contract axes** (duration, aspect, audio y/n, i2v/t2v, motion class, quality tier, budget ceiling); draft-cheap vs final-expensive tiering; **run-level unit economics table**: cost per finished reel by tier incl. retries + rejected generations, per pack, per run, per month at cs+en (D-02 doubling).

**T3 → `prompt-engineer` → `A3_video_prompts_skills.md`** (expertise; durable patterns)
Block A item 5: prompt structures for hooks/scripts/shot lists/on-screen text/negative prompts/brand locks; reusable skill-pack/agent patterns; shared-skills vs theme-overlay boundary; how multi-shot-native models change shot-list structure (conceptual; model-specific guides come from T2, reconciled W2); which patterns are language-portable vs per-language (F-7); what breaks when a prompt recipe fails unattended (fallback behavior of a recipe, conceptually).

**T4 → `general-purpose` → `A4_assembly_postproduction.md`** (web)
The unowned middle of the pipeline: stitching clips into 20–40s reels; **carousel-to-reel** transform (assignment-named); burned-in captions and caption/music/VO **tooling** (T1 owns practices, T4 owns tools); per-destination aspect/safe-zone conversion; music bed, ducking, loudness; end-card/CTA frames; **build-vs-buy**: local ffmpeg vs API assembly services vs Higgsfield Marketing Studio — incl. what a local binary does to Windows-first distribution (D-05); **C2PA/provenance survival through re-encode** (F-8); Czech on-screen text/diacritics rendering + Czech TTS/native-audio quality and the possible en/cs pipeline fork (F-5/F-7).

### Domain: topic sources (Block B) — 4 tasks

**T5 → `general-purpose` → `B1_sources.md`** (web)
Block B items 1, 2: source-by-source evaluation of full List A (X, Reddit, tech news/PH/HN/HF, Google Trends + SERP, Meta Ad Library, TikTok CC, YouTube, LinkedIn public, P2 extras) — role, signal types, priority, cadence, failure modes, evidence-based extensions. Must resolve as explicit recommendations: Reddit stance (F-1, real options only), X under D-08, Meta Ad Library access path (F-9), LinkedIn read reality (F-9), Google Trends access (F-9), TikTok CC narrowed value. Which sources carry Czech-market signal vs global-English (coordinate boundary: T8 owns Czech-native sources; T5 owns the global List A + flags cs-relevance per source).

**T6 → `general-purpose` → `B2_extraction_methods.md`** (web)
Block B items 3, 4: per-source method matrix — official/public API vs search/browse vs MCP tools vs authenticated non-MCP integrations vs Playwright, under F-9 pessimism (justify automation only where genuinely open; assume detection on major surfaces); hard rule: no login-walled scraping; rate limits, caching, dedupe, idempotent runs; robots/ToS basis per source (legal analysis itself lives in T15/C7 — declare assumed-input placeholder); **do-not-scrape list**; fallback ladders; raw-artifact storage for auditability incl. reseller retention terms; freshness reality: "if Reddit is blocked until month 2, what does the research axis look like on day 1, and how stale is acceptable before tie-in value dies?"

**T7 → `data-scientist` → `B3_ranking_scheduling.md`** (expertise)
Block B items 5, 7 (item 6 operator-review moved to T12): ranking raw signals → scored candidates (attention/virality × brand-fit × freshness × per-source availability/confidence weight); **inspectable sub-scores** + hard skip-threshold; **negative brand-fit criteria research** — what actually makes a trending topic skip-worthy (category mismatch, competitor saturation, tone risk, "brand looks desperate"); anti-forced-placement design; unattended collection: freshness windows, cross-day dedupe keys, max items/run, poison-pill handling; per-language relevance (a topic can be `en`-fit but not `cs`-fit). MUST declare assumed-input placeholders for per-source field availability (T6's territory) — W2 re-derives.

**T8 → `content-marketer` (2nd instance) → `B4_czech_b2b_market.md`** (web)
The Czech layer (F-7, D-02): Czech LinkedIn B2B culture (formality, decision-maker personas, content norms vs global); Czech TikTok/Reels B2B reality (normal or cheap-looking?); FB/IG B2B norms in CZ; Czech tech/startup discourse venues that outrank global sources for cs signal (local media, communities, influencers); **Czech anti-slop inputs**: real lexical/structural patterns of AI-slop Czech B2B copy + phrases real Czech professionals never say; Czech CTA/voice conventions for a lead-gen agency ICP. Input: `docs/marketing/HypeLead Areas GTM_Marketing_Strategie.txt` (the brand's own cs ICP segments — ground the Czech analysis in these audiences). Output feeds T13's rubric design and T5's source table.

### Domain: integrations (facts) — 2 tasks

**T9 → `api-documenter` → `C1_notion_postiz_integration.md`** (web)
**Notion MCP**: FIRST state a candidate brand-fact taxonomy (offers, ICP map, approved-claim allowlist, CTA set, pricing policy, proof/case allowlist, voice rules, hard excludes), THEN assess retrievability against the actual tool surface (not the reverse); auth model and the **unattended-cron collision** (remote OAuth + interactive consent vs 03:00 token expiry) → explicitly evaluate **MCP vs direct Notion REST (internal integration token)** for cron mode, MCP for interactive mode (assignment says "MCP-extractable" — argue the split honestly); rate limits, client maturity. **Postiz**: draft-without-schedule capability as a **kill-switch question** with pre-planned fallback ladder (internal draft → far-future scheduled → local-only staging + manual paste); cloud-trial vs self-host differences; connector coverage + per-connector business-account/app-review lead times (LinkedIn/IG/TikTok); platform AI-label fields exposure (F-8); side-effect surface to block in test mode; official MCP server status; F-4 allowlist hook; X-as-publish-destination separation (F-2). NO Kie/Higgsfield content (T2 owns it).

**T10 → `general-purpose` → `C2_platform_constraints_stack.md`** (web)
Per-platform hard constraints for List B destinations (char limits incl. Czech char counting, aspect ratios, carousel slide counts, Reels/Shorts durations, caption rules, per-platform AI-label mechanics). **Stack verification for D-06**: Python vs Node/TS on MCP client maturity, LLM SDK coverage, Playwright parity, Windows console + Task Scheduler ergonomics (SYSTEM-account gotchas: DPAPI, no user profile, browser profiles), single-machine distribution, Linux-cron parity (env/PATH/locale — Czech UTF-8).

### Domain: systems design (expertise-led) — 4 tasks

**T11 → `sre-engineer` → `C3_cron_ops_state.md`** (expertise)
Stage 3 topics 9, 10 + the state layer: **orchestration paradigm argued with evidence** — agentic loop vs deterministic pipeline with narrow LLM nodes, judged on cost determinism, testability, budget enforceability, cron safety; run identity; cross-platform locking; idempotency/dedupe keys; **the ledger set**: research-artifact store, cross-day topic dedupe index, run ledger, async media-job ledger (assumed-input placeholder: T2's async reality), spend ledger, pack outputs, brand-truth snapshots, review-decision state — substrate options (SQLite vs files vs embedded DB) with tradeoffs; run duration vs cadence, overlap policy, per-stage timeouts, **stage-level checkpoint/resume** (a 04:00 crash must not discard paid work); exit-code taxonomy; unattended secrets (no interactive session: task-level env, DPAPI, ACL'd file — Windows AND Linux answers); retries, partial-failure semantics, budget caps incl. mid-pack cap-hit behavior; notification substrate options; missed-run catch-up semantics. Format: options + tradeoffs + recommendation + **≥2 rejected alternatives** per topic.

**T12 → `product-manager` → `C4_operator_review_ux.md`** (web + expertise)
Stage 3 topics 7, 9(operator half) + Block B item 6 + D-07 as a researched deliverable: a concrete **operator walkthrough** — solo marketer opens the folder after a cron run: what do they open FIRST; single-page digest per run vs 12 files; how they judge "research was sound" without being a data scientist (sub-score presentation, source links, confidence bands); publish/skip decision flow in <30 min for ~5 topics; diffs vs yesterday (dedupe visibility), freshness metadata; **cost forecast before approving media generation** (trial-quota protection); rejection/regeneration request flow (reject just the video, keep the copy); how the pack anatomy maps to later Notion upload (D-07); review-of-research gate before generation burns money (Block B item 6). Grounded in real HITL review-tool patterns (web check ≤ a few lookups).

**T13 → `prompt-engineer` (2nd instance) → `C5_voice_models_judge.md`** (expertise)
Stage 3 topics 4(gate half), 8 + text pipeline: layered anti-slop gate design (lexicon + structural heuristics + LLM judge + bounded regenerate + escalate-to-review flagged, never silently ship); **en rubric designed, cs rubric designed from T8's empirical inputs** (assumed-input placeholder); judge calibration method — golden set, judge-vs-human agreement, false-positive economics (strict judge in unattended run = regenerate loop = cost blowup); **eval/regression concept**: how you know a prompt change improved output; prompt/model version pinning recorded per pack; **text-model routing**: model choice axes for cs vs en copy, structured-output reliability, token-cost sizing at 2 languages × 6 destinations × variants × judge passes; where the good-spin/bad-spin test (trend dump, forced relevance) is enforced — spin gate distinct from voice gate. Input: exemplar corpus (`docs/marketing/`) — derive the en voice/hook patterns FROM the winning posts (exemplar-grounded few-shot design, per-theme **exemplar corpus** as a first-class theme asset), not from generic best-practice lists.

**T14 → `ai-engineer` → `C6_brand_truth_design.md`** (expertise)
Stage 3 topic 3 design half (previously unowned): brand-truth resolution design — required vs optional brand facts (consuming T9's taxonomy as assumed-input placeholder; cross-check against the real ICP segments in `docs/marketing/HypeLead Areas GTM_Marketing_Strategie.txt`); precedence when Notion/config/site disagree; **confidence measurement design** (which facts count, freshness thresholds, band computation, exact research-only-degrade trigger); refresh cadence; **brand-truth snapshot per pack** (hash + timestamp) for auditability + offline snapshot for Notion-down runs; **claim-safety verification substrate**: allowlist + extractor that pulls numbers/currency/company names/percentages from generated copy and cross-checks the ledger; the F-5 spoken-claims consequence (script-lock vs ASR-verify — recommend one); **spin application**: pain→offer mapping, CTA correctness, product rules (site-first offers), good-vs-bad-spin as an enforceable gate.

### Domain: legal — 1 task

**T15 → `legal-advisor` → `C7_legal_compliance.md`** (web — evidence pack for R4)
Snapshot + analyze (with retrieval dates): Reddit ToS commercial-use terms (F-1 verdict input); X reseller legality + storing/deriving content; LinkedIn/Meta Ad Library/TikTok CC/Google ToS + robots for the do-not-scrape list; **EU AI Act Art. 50** obligations for synthetic marketing content + machine-readable marking; platform-native AI-label obligations (F-8); **GDPR on collected research artifacts** (Reddit/X posts are personal data: lawful basis, retention window, pseudonymization, can raw artifacts be stored at all — feeds T6's storage design); likeness/voice consent regimes for avatar/UGC tools; generated-asset commercial-rights layering (provider ToS vs upstream model licenses — legal analysis; T2 holds the factual roster). Czech-law notes where relevant. Each conclusion: severity | affected architecture area | required design consequence.

**Barrier (machine-checkable + conductor read):** all 15 files exist; 5 mandatory sections present per brief (grep for section headers); every F-flag ID appears in ≥1 assigned brief (grep); no fenced code blocks in deliverables (grep); web briefs ≥5 dated sources; must-answers answered; thin briefs → targeted follow-up to same agent type. Conductor reports per stage-protocol (this closes assignment Stages 1+2+3 reporting).

---

## WAVE 2 — Synthesis (shape: a | 1 agent | barrier: ALL of Wave 1)

**T16 → `llm-architect` → `SYNTHESIS.md` + append DECISION_LOG/RISK_LOG**
Consolidate 15 briefs: resolved recommendations; **re-derive** T7's scoring against T6's real field availability and T11's cron model against T2's async reality (placeholders → actuals, not just "resolve conflicts"); reconcile T3-vs-T2 prompting, T13-vs-T8 Czech rubric, T14-vs-T9 taxonomy; **canonical vocabulary table** (normative fixed nouns: component/stage/mode/pack-artifact/config-block/exit-code-class/provider-role names — later authors may not invent new ones); **two consolidated sections carrying the assignment's exact mandated titles**: *"Viral AI video generation — tools, prompts/skills/agents, workflows, recommendations for this project"* and *"Viral topic extraction sources, methods (including Playwright where justified), ranking, and guardrails"*; concatenated fact ledger; open-decision list with options + recommendation; "what changed vs the assignment's assumptions" section.

**Barrier:** cross-references all 15 briefs; placeholders re-derived; vocabulary table present; both mandated titles present.

## WAVE 2.5 — Human checkpoint (conductor; BLOCKING gate)

Report Stage 1–3 conclusions per protocol. Put to the human with recommendations: X access path (reseller yes/no) · Reddit stance · stack confirmation (D-06) · any W0.5 facts still missing · Higgsfield role. Architecture authoring does NOT start until answered — §2/§6/§10/§15 would otherwise be built on open decisions.

---

## WAVE 3 — Architecture drafting (shape: a | 2 agents | disjoint draft files | depth 1)

**T17 → `llm-architect` → `drafts/DRAFT_A_core_pipeline.md`** — §1–§6: components/responsibilities + stack recommendation w/ rejected alternatives + **orchestration paradigm** (§1); List A research/extraction architecture: per-source table, API/search/MCP/Playwright policy under F-9, do-not-scrape list, raw-artifact storage w/ GDPR consequence (§2); List B content architecture: per-destination asset matrix, native adaptation rules, per-language variant rules, human-review-per-asset-type (§3); video pipeline incl. assembly stage, carousel→reel, spend boundary, async job model, human gates, en/cs fork decision (§4); provider architecture: routing contract, config placement, dry-run, cost guards + unit economics, retention, refusal handling, outage ladder, **room for Meta Ads/paid creatives later** (§5); brand-truth/spin: Notion MCP + REST split, taxonomy, precedence, confidence bands + degrade trigger, snapshots, claim-verification substrate, spin application (pain→offer, CTAs, product rules, good/bad-spin gate), **per-theme exemplar corpus as a first-class theme asset** (voice grounded in curated winning posts — `docs/marketing/` seeds theme #1) (§6). Internal write order: §6 first. Uses ONLY canonical vocabulary.

**T18 → `sre-engineer` → `drafts/DRAFT_B_runtime_safety.md`** — §7–§9, §11, §12, §14: distribution: Postiz draft-first + fallback ladder, blog prep, allowlist enforcement point, never-live-by-default (§7); scheduler/cron: one entrypoint Task Scheduler + cron, ledgers, locking, idempotency, checkpoints/resume, exit codes, secrets, retries, partial failure, budgets + mid-pack cap-hit, notifications, catch-up (§8); dual end-to-end flows + divergence table + diagrams (§9); modes/gates capability matrix + single fail-closed choke point (§11); run/review package anatomy per run and language — built from T12's operator walkthrough, incl. cost forecast + Notion-upload mapping (§12); voice + claim-safety enforcement layers incl. spoken-claim consequence + AI-labeling/provenance placement (F-8) (§14). Uses ONLY canonical vocabulary.

**Barrier:** both drafts complete, all assigned §s present, vocabulary respected (grep: no new component nouns).

## WAVE 3b — Assembly (shape: a | 1 agent | single owner of final file)

**T19 → `llm-architect` → `ARCHITECTURE_PLAN.md`**
Merge drafts; author §0.1–0.4 scaffolding (problem restatement, decision-log ref, fact ledger concatenated from briefs, research index); §13 multi-theme extensibility + second-theme fixture; §15 risks table (failure→detection→mitigation→symptom; includes scraping breakage, provider outage, cron partial runs, cost blowups, brand-truth loss, trial-quota exhaustion); §16 open decisions from log; §17 phased roadmap w/ acceptance criteria + do-not-start-next-until + **feedback-loop (winners/losers) phase**; §18 human review method (checklist + adversarial questions mapped to §15) — review changelog goes to a separate appendix, not §18; **§10 theme-config knob table derived by sweeping §2–§8, each knob row citing the consuming section** (prose form per constraint note); **worked end-to-end example appendix**: one concrete topic traced research→rank→spin→cs+en packs→video plan→provider calls→pack folder→Postiz draft, naming artifacts + gate decisions (prose + diagram, no syntax). Consistency pass with vocabulary table.

**Barrier (machine-checkable + read):** §0–§18 + both appendices present; every §10 knob string appears in §2–§8 (grep); every volatile claim traces to fact ledger; no fenced code blocks; Meta-Ads room + feedback loop present.

---

## WAVE 4 — Review (shape: a | 5 leaf reviewers | disjoint findings files | depth 1)

Inputs for ALL reviewers: ARCHITECTURE_PLAN.md + SYNTHESIS.md + the 15 briefs + fact ledger (so unsupported vs brief-supported assertions are distinguishable). Reviewers write ONLY their own findings file; findings carry: severity (blocker/major/minor) | section ID | claim | required change.

- **R1 `architecture-reviewer` → R1_architecture.md** — coherency vs Stage 4 items 1–18 + all 10 design-phase success criteria + the 8 risk areas: cron idempotency/dedupe concreteness; inspectable brand-fit scoring w/ hard skip threshold; anti-slop as machine gate w/ bounded regenerate; source-access policy honesty (X under D-08, Reddit per F-1, F-9 pessimism); brand-truth conflict/confidence gating; budget caps + dry-run boundary + trial-quota exhaustion; cs+en output-set integrity (D-02/F-7); mode enforcement at ONE fail-closed choke point.
- **R2 `ai-engineer` → R2_ai_pipeline.md** — technical feasibility vs the briefs' evidence: video pipeline realism, async/assembly model, provider routing contract, MCP/REST brand-truth split, judge/eval design, cost model plausibility.
- **R3 `content-marketer` → R3_marketing.md** — will research→rank→spin→create produce publishable content; voice bar realism per language (cs rubric grounded in B4, not translated); platform adaptation correctness; operator walkthrough usability (D-07); north-star fit (clients/pipeline, not vanity).
- **R4 `pravnik` → R4_legal.md** — legal review USING C7's evidence pack (no web needed): Reddit/X/scraping stances, GDPR on artifacts, AI Act + labeling placement in the architecture, asset-rights layering, Czech-law specifics. Findings in Czech OK + one structured English line each (severity | section | claim | required change).
- **R5 `chaos-engineer` → R5_scenarios.md** — scenario red-team; walk ≥5 concrete failures end-to-end and report where the doc is SILENT: (i) 03:00 cron, Notion token expired; (ii) 2 media jobs pending at run deadline; (iii) same topic trends 4 days running; (iv) budget cap trips mid-pack, 3 of 6 destinations done; (v) human rejects one pack's video only, wants regeneration; plus any it invents.

**Barrier:** 5 findings files; conductor triages every blocker/major → accept/reject + one-line rationale appended to DECISION_LOG. Conductor reports per stage-protocol.

## WAVE 5 — Fix (shape: a | 1 agent | single owner — same assembler)

**T25 → `llm-architect`** — apply accepted findings; emit a **finding → section → edit mapping table** (surgical edits, no re-derivation); rejected findings recorded with rationale in the review-changelog appendix; unresolved → §16 open decisions.

**Barrier:** every blocker/major fixed-or-logged; mapping table complete.

## WAVE 6 — Stage 5 presentation (conductor)

Write `STAGE5_APPROVAL_SUMMARY.md` + present in chat: recommended architecture direction · alternatives considered · assumptions · blocking questions (any still-open: X, Reddit, Higgsfield, stack, Postiz plan limits) · recommended next step = implementation xmasterplan. **STOP for human approval.**

---

## Aggregating files (single-writer-LAST; ONE owner per wave)

| File | Owner |
|------|-------|
| `ARCHITECTURE_PLAN.md` | assembler `llm-architect` (W3b create, W5 edit) — drafts A/B are inputs, never edited after merge |
| `SYNTHESIS.md` | T16 (W2 only) |
| `DECISION_LOG.md` / `RISK_LOG.md` | sequential, never parallel: conductor (W0) → T16 (W2) → conductor (W2.5, W4 triage) → T19 (W3b) → T25 (W5) |
| `STAGE0_RESTATEMENT.md`, `STAGE5_APPROVAL_SUMMARY.md` | conductor |

## Wire-in (cross-reference map)

| Artifact | Referenced in | Who adds it |
|----------|--------------|-------------|
| Each W1 brief | SYNTHESIS.md; ARCHITECTURE_PLAN §0.4 | T16 / T19 |
| Fact-ledger rows (per brief) | concatenated in SYNTHESIS; referenced §0.3 | T16 / T19 |
| Canonical vocabulary | consumed by T17/T18/T19 (no new nouns) | T16 defines |
| Drafts A/B | merged into ARCHITECTURE_PLAN | T19 |
| R1–R5 findings | review-changelog appendix + §16 | T25 |
| C7 legal evidence | R4's input; §2/§14 legal consequences | T17/T18 cite |

## Execution notes for xecutor

- W1 spawns all 15 agents in ONE dispatch; W3 spawns 2; W4 spawns 5. W2/W3b/W5 single-agent. Conductor asks the human at W0.5 and W2.5 (blocking) and reports after every wave.
- Barrier checks: use the grep-based checks named per wave (section headers, F-flag coverage, no code fences, §10 knob citations) + conductor read-through. No build/tests exist.
- Agents receive: assignment path, their task text verbatim, locked-decision table, their F-flags, output path, the 5-section brief template, and (W3+) SYNTHESIS + relevant briefs. Parallel agents never read each other's unfinished files; assumed-input placeholders are mandatory where noted.
- Budget: web-heavy briefs (T1, T2, T4, T5, T6, T8, T9, T10, T12, T15) are deep-research; expertise briefs (T3, T7, T11, T13, T14) cheaper. Thin brief per definition → one follow-up to same agent type, then escalate to conductor.
- Git commit after each wave barrier.
