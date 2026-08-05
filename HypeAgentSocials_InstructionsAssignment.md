# Assignment: Design (then later build) a configurable multi-theme marketing research → spin → create → review agent

## Your goal

Your goal is to **research first**, then **devise a plan for how to design and architect** a configurable AI marketing agent system — and only implement after that plan is sound.

You are **not** required to invent code, pseudocode, CLI syntax, config syntax, schemas, or a fixed repository tree in the design phase. Those decisions are yours **after** deep research and architecture planning. The human will approve the architecture direction before a full build is treated as complete.

**Do not assume any existing product, codebase, folder layout, or prior implementation.** Uncover tools, workflows, source strategies, provider choices, and architecture yourself through research and reasoning. Treat this document as goals and constraints only.

Primary product idea in one line:

> Research what the theme config says to watch → resolve brand/product spin from config **and MCP-extractable brand truth** → create multi-platform marketing assets (including AI-generated viral-style video/reel assets) → package for human review → only later stage/publish via approved channels → and ultimately run this whole loop on a schedule as a **cron-executable console job**.

Illustrative first theme (example values for the first tenant, not eternal hardcoding of the engine):

- **Research topics (examples):** AI, Claude Code / coding agents, lead generation, outbound / AI sales discourse, related pains and viral discussions  
- **Brand spin (examples):** HypeDigitaly s.r.o., HypeLead.ai / HypeLead and other configured offers, configured ICP / voice / CTAs / claim rules  

The same engine must later support other topics and other companies by changing theme configuration (and brand-truth sources), not by rewriting the whole agent.

---

## North star

Optimize for **clients, engagement quality, and pipeline** — not vanity post counts.

The long-term operating model is **automation by default on a schedule**, with **humans reviewing and approving** before anything truly goes live.

---

## Non-negotiable product constraints

1. **Human gate for live outcomes:** never auto-publish live social or merge production site without explicit human approval (or an explicitly enabled, carefully designed auto-draft policy that still does not live-post by default).  
2. **Default safe/test mode:** local reviewable outputs only; external publish disabled.  
3. **Never invent** prices, ROI, client names, case metrics, or fake proof.  
4. **Soft CTAs by default** (audit / product page / demo) unless theme config says otherwise.  
5. **Human voice is mandatory** — conversational, not AI marketing slop.  
6. **Research platforms ≠ content platforms.** Keep two lists separate in design.  
7. **Multi-theme:** one main config per theme/tenant; first theme oriented around the HypeDigitaly / HypeLead example; more themes later.  
8. **Console/operator-facing app intent:** runnable by operators interactively **and** non-interactively.  
9. **Cron / scheduled execution is a first-class end goal:** the same console app must be executable as a **cron job** (or equivalent scheduler) to run the pipeline automatically on a cadence defined by config.  
10. **Brand spin must be extractable via MCP** (and fallbacks), not static config only.  
11. **Asset generation providers in scope to evaluate:** **Kie.ai** and **Higgsfield.ai**, plus any better options your research finds.  
12. **Publishing/posting path in scope:** ultimately **Postiz.ai** for social drafts → human schedules (not silent auto-live posting by default).  
13. **Blog/site path:** when a theme requires it, approved long-form can later go to that brand’s website/blog pipeline, still human-merged by default.  
14. **Legal/ethical collection:** prefer public APIs and legitimate access; if browser automation/scraping (e.g. Playwright) is proposed, the plan must cover ToS risk, rate limits, robustness, and fallbacks — not reckless scraping.  
15. **Unattended runs must be safe:** cron mode must fail closed on missing secrets, ambiguous brand truth, policy violations, or publish actions not allowed by mode.  

---

## Critical first research mandate (do this before architecture lock)

### Deep research block A — Viral AI video generation (best practices, tools, prompts, agents)

Before designing system architecture, conduct **deep research** on how high-performing short-form / viral-style videos are actually produced with AI in current practice.

Cover at least:

1. **Best practices** for AI-generated viral/short-form video (hooks in first 1–3s, pacing, captions, pattern interrupts, loops, faceless vs UGC, B2B-safe adaptations).  
2. **Real use cases and examples** (what works for consumer vs B2B; what fails; what looks like obvious AI slop).  
3. **Software / platforms** for generation and editing pipelines, including evaluation of:
   - **Kie.ai**
   - **Higgsfield.ai**
   - other serious options your research surfaces (model routers, editors, caption tools, avatar/UGC tools, music/VO tools) — recommend with tradeoffs  
4. **Model/job fit** conceptually: text-to-video vs image-to-video, keyframe-first workflows, carousel-to-reel, batch draft vs final quality, cost controls.  
5. **LLM prompts, skills, and agents** used by strong practitioners:
   - prompt structures for hooks, scripts, shot lists, on-screen text, negative prompts, brand locks  
   - reusable skill packs / agent patterns for reels scripting, social video, ad creative, UGC workflows  
   - what should live as shared skills vs theme-specific overlays  
6. **Quality rubrics** for accepting/rejecting AI video (motion glitches, unreadable text, fake metrics, brand mismatch, “AI slop” look).  
7. **Operator workflow** from idea → script → keyframes → video variants → human pick → publish-prep.  
8. **What can safely be automated on a schedule** vs what should remain human-reviewed before spend or publishing.  

**Deliverable:** a dedicated research brief section:  
*Viral AI video generation — tools, prompts/skills/agents, workflows, recommendations for this project.*

### Deep research block B — Where viral topics come from + how extraction should work

Also before architecture lock, research **where** to extract trending/viral topics and **how** collection should work in a maintainable system.

Cover at least:

1. **Places / platforms to extract viral topics and formats** (use List A below as a starting universe; validate, prioritize, and extend with evidence).  
2. **Signal types:** viral discourse, ICP pain, launch hype, search demand, ad creative patterns, short-form format trends.  
3. **Extraction methods per source:**
   - official/public APIs where available  
   - search and legitimate page browse  
   - authenticated tool integrations if relevant  
   - browser automation (e.g. **Playwright**) where APIs are weak — with clear rules  
4. **Scraping / automation design concerns** (if Playwright or similar is recommended):
   - which sources justify automation vs API/search  
   - stability risk, anti-bot, pagination, login walls  
   - rate limiting, caching, deduplication, idempotent runs  
   - robots/ToS/legal/ethical constraints and a “do not scrape” list  
   - fallback when automation breaks  
   - what raw artifacts to store for auditability  
5. **Ranking pipeline:** how raw signals become scored topic candidates (virality × brand fit × freshness).  
6. **Human review of research:** what operators should see before content generation burns time/money.  
7. **Scheduled collection:** how topic extraction should behave when run unattended via cron (freshness windows, dedupe across days, max items per run, poison-pill handling).  

**Deliverable:** a dedicated research brief section:  
*Viral topic extraction sources, methods (including Playwright where justified), ranking, and guardrails.*

Only after Blocks A and B (plus broader systems research) should you lock the architecture plan.

---

## LIST A — Research platforms / places  
### (deep research: trending topics, virality, pains, demand, competitor DNA)

Architecture must define roles, priority, cadence, extraction method, and failure modes per source. Treat the following as the intended starting universe to evaluate and organize:

### P0 — primary candidates

| Source | Role |
|--------|------|
| **X (Twitter)** | Viral hooks, real-time AI/dev/sales discourse |
| **Reddit** | ICP pains, objections, unfiltered complaints |
| **Web AI / tech news & launches** | Product Hunt, model/vendor blogs, major tech press, Hugging Face, Hacker News, similar public hubs |
| **Google Trends + SERP/demand signals** | Search demand vs pure hype |
| **Meta Ad Library** | Competitor ad hooks, offers, creative patterns (research only) |

### P1 — secondary candidates

| Source | Role |
|--------|------|
| **TikTok Creative Center** / public short-form trend surfaces | Formats and hooks that work in short video |
| **YouTube** | Topic demand, titles/packaging patterns, discussion themes |
| **LinkedIn public** | B2B framing (lighter virality signal) |

### P2 — tertiary / optional candidates

- Instagram public patterns  
- Podcasts / transcripts  
- Review sites (e.g. G2-style) when category-relevant  
- Other public tools your research recommends  

### Always for spin accuracy (not trend discovery)

- Theme brand config  
- **MCP-connected brand knowledge** (preferred when available)  
- Public live company/product pages for verification  

### Usually weak as primary AI-topic discovery

- Facebook organic feeds as a main trend engine  

**Extraction methods to evaluate per source:** APIs, search/browse, MCP tools, and browser automation (**Playwright** as a candidate) where justified.

**Ranking intent:** attention/virality × brand fit × freshness.  
Weak brand fit → skip or handle honestly; do not force product spam onto unrelated trends.

**Important:** Reddit, Ad Library, Product Hunt, etc. are **research sources**, not default publish targets unless a future theme explicitly says otherwise.

---

## LIST B — Content platforms / marketing assets  
### (where we generate posts, carousels, reels/videos, blog)

Creation destinations are separate from research.

### Owned / long-form

- Company website **blog/articles** when enabled (possibly multiple languages if theme requires)  
- Product-led rule when configured: **blog/site first**, then social atomization  

### Organic social destinations and typical assets

| Destination | Typical assets |
|-------------|----------------|
| **LinkedIn** | Long post, carousel/document-style |
| **X** | Single post, thread |
| **Instagram** | Carousel, Reel, caption |
| **TikTok** | Short vertical video / slideshow + spoken script |
| **YouTube Shorts** | Short vertical script + packaging |
| **Facebook** | Community-style post |

### Visual / motion asset types supporting the above

- Feed stills / single-image posts  
- Multi-slide carousels  
- Short reels / vertical videos (**major focus after viral-video research**)  
- Optional voiceover/audio  
- Blog heroes / supporting diagrams when blog is in scope  

### Later phase (leave room in architecture)

- Meta Ads / paid creatives (generate/write; spend still human-controlled)  

### Not default publish destinations

- Reddit posting  
- Product Hunt as a publish channel  
- Ad Library as a publish channel  

For each content platform, the architecture plan must say how research insights adapt natively, which asset types apply, and what humans review.

---

## Asset generation providers (must be researched and planned)

### Must evaluate

- **Kie.ai** — multi-model route candidate for images, carousels, short video, related jobs  
- **Higgsfield.ai** — alternative/complement candidate for marketing visual/video-style assets  

### Also discover

- Any better or complementary tools for viral video, captions, UGC, VO, editing, batching, or brand consistency  

Your research must recommend **when to use which provider**, whether dual/multi-provider routing belongs in theme or global settings, cost guards, retention/download risks, dry-run vs real generation, and QA rules (brand lock, no fake metrics on graphics, readable short on-image text only, reject AI-slop look).

### Rules for visuals/video

- Always produce **plans/prompts/scripts/shot lists** even when generation keys/budget are missing.  
- Actual generation optional per run (especially important for cron cost control).  
- Prefer workflows proven in your viral-video research (e.g. keyframe-first / image-to-video when appropriate).  
- Scheduled runs must support budgets/caps (max videos, max carousel slides, max provider spend per run/day).  

---

## Publishing / distribution (must be in the plan)

### Social: Postiz.ai

- Ultimate intended bridge for social publishing/posting workflows.  
- Correct default pattern: after human approval → create **drafts in Postiz** → **human schedules/publishes**.  
- Safe/test mode must refuse Postiz side effects.  
- Staging may allow drafts only.  
- Cron may later auto-create **drafts** if config explicitly allows it — still not live-post by default.  
- Never silent auto-live posting as default.  

### Blog / site

- After human approval, prepare for the brand’s website/blog pipeline when the theme requires it.  
- Human merges/publishes production by default.  

### Optional later

- Knowledge-base / content pipeline notes if useful  
- Feedback capture for winners/losers  
- Notifications that a scheduled run finished and needs review  

---

## Brand spin layer (config + MCP + public verification)

Brand spin must **not** depend on static config alone.

Resolve spin inputs from:

1. **Theme configuration** (company, products, ICP map, voice, CTAs, hard excludes, product rules)  
2. **MCP-connected brand truth** when available (preferred for accuracy)  
3. **Public live site pages** for verification  
4. **Human run overrides** when provided  

Use this layer to:

- know who we are and what we sell  
- map pains to offers  
- keep CTAs correct  
- avoid inventing prices, ROI, client names, or case metrics  
- apply product rules (e.g. site-first for certain offers)  

If MCP is unavailable, degrade to config + public sources and mark reduced brand-confidence in the review package — **do not hallucinate** missing commercial facts.

For cron/unattended runs: if brand confidence is too low or required MCP truth is missing, **stop or produce research-only output** rather than inventing spin claims.

Architecture must define required vs optional brand facts, refresh cadence, and conflict resolution when config / MCP / site disagree.

### What “spin” means

Good spin:

- starts from a real external topic or pain found via List A  
- explains meaning for the configured ICP  
- connects naturally to configured/MCP-resolved offers  
- ends with a soft named next step when appropriate  

Bad spin:

- trend dump + random product mention  
- forced relevance  
- invented commercial proof  
- generic AI-marketing voice  

---

## Voice quality bar (first-class design concern)

Self-check every artifact:

> Would a real human write this in ordinary professional conversation — or does this only exist as an LLM pattern?

Avoid by default:

- “It’s not X, it’s Y” templates  
- “changed the rules of the game” / game-changer clichés  
- “Here’s the thing,” “Let’s dive in,” “In today’s fast-paced world…”  
- corporate AI mush (seamless, leverage, streamline, unlock, supercharge…)  
- fake urgency/scarcity, invented metrics, slogan stacks  

Prefer concrete symptoms, natural rhythm, one reader in mind, soft named CTAs.

---

## Multi-theme / config intent

There should be **one main configuration per theme/tenant**, conceptually covering at least:

### A) Research block — what to watch + how to collect

Topics/keywords/entities, source priorities, excludes, extraction methods (API / search / MCP / Playwright or equivalents), ranking preferences, language, cadence hints for scheduled runs.

### B) Spin / brand block — how we interpret

Company/products, ICP, voice, CTAs, claim policy, product rules, MCP brand-source pointers, visual brand baseline.

### C) Output / runtime / automation block

Enabled content platforms/formats, blog rules, modes/guards, media provider preferences (Kie / Higgsfield / others), Postiz enablement by mode, video/reel pipeline preferences, review package expectations, **schedule/cron settings**, per-run budgets, notification preferences, idempotency/dedupe rules.

First real theme orientation: **HypeDigitaly / HypeLead example**.  
Architecture must allow additional themes later without redesigning the whole agent from zero.

---

## Operator / console / cron intent

### Interactive operator use

Operators should eventually be able to:

- choose a theme  
- run research topic extraction and/or full pack generation  
- optionally focus a topic for one run  
- get a clear review package  
- regenerate parts after feedback  
- validate theme readiness  
- dry-run expensive media generation  
- keep default mode safe  
- later: staging to Postiz drafts / blog prep after approval  

### Unattended scheduled use (end goal)

The **same console application** must be designed so it can run as a **cron job** (or equivalent OS/cloud scheduler) and automatically perform the configured pipeline without a human sitting at the keyboard.

Cron/scheduled intent includes, at minimum:

- run on a cadence (e.g. daily / multiple times per week — exact cadence is a design/config decision)  
- load theme + mode + secrets non-interactively  
- extract viral topics / pains  
- resolve brand spin  
- generate content packs + visual/video plans (and optional media within budget caps)  
- write a reviewable run package every time  
- exit with clear success/failure codes suitable for cron monitoring  
- log enough for debugging unattended failures  
- avoid duplicate work when the same cron fires again (idempotency / dedupe)  
- optionally notify that “new packs are ready for review”  
- optionally, only if explicitly enabled by mode/config, push **Postiz drafts** — still not live-publish by default  

Exact commands, flags, file formats, and cron expressions are **not prescribed** here; design them after research.  
But the architecture plan **must** treat “cron-executable full pipeline” as a first-class requirement, not a later afterthought.

---

## Intended end-to-end loop (behavior to architect)

1. Load theme configuration (interactive or cron).  
2. Resolve brand spin truth (config + MCP + public verification).  
3. Extract/research viral topics and pains from **List A** using collection methods you design (APIs / search / browse / MCP / **Playwright where justified**).  
4. Rank candidate angles (attention × brand fit × freshness).  
5. Spin chosen angles through resolved brand/product truth.  
6. Create **List B** assets:
   - human-sounding copy/scripts  
   - carousels/stills plans  
   - viral-style short video/reel plans and optional generation via researched providers (**Kie.ai**, **Higgsfield.ai**, and/or others)  
7. Package a human review bundle (sources used, extraction method notes, spin rationale, platform assets, visual/video plans, claim-safety notes, provider choices, brand-truth sources used, automation metadata).  
8. Stop for human decision before live outcomes.  
9. After approval only (or explicit staging policy): **Postiz.ai drafts** for social; blog/site prep when relevant; human still schedules/merges by default.  
10. Later: feedback loop improves research sources, prompts, and video recipes.  
11. Repeat on schedule via **cron** so the machine keeps producing review-ready work automatically.  

Internal architecture, storage, orchestration, and tooling are yours to propose — without code or syntax in the design phase.

---

## Modes / safety intent

| Mode intent | Allowed (conceptually) | Forbidden by default |
|-------------|------------------------|----------------------|
| **Test / safe** | Local research + copy + visual/video plans; optional media gen if keys; ideal default for early cron | Postiz live/publish, production site merge, live schedule |
| **Staging** | Drafts only (e.g. Postiz drafts, draft web/sandbox); cron may create drafts if enabled | Live schedule, unattended production main merge |
| **Live-prep** | Production-ready artifacts/drafts/PRs for human action | Unattended live posting / unattended main merge |

**Cron policy principle:** automate research + creation + packaging aggressively; automate live publishing only with extreme caution and never as the default.

Secrets only via secure env/secret handling — never embedded in prompts committed to source.

---

## Multi-stage work order (follow this)

### Stage 0 — Restate the problem

In your own words cover:

- research vs content platform split  
- config-driven topics + MCP-extractable brand spin  
- viral AI video generation as a core design driver  
- topic extraction methods including possible Playwright automation  
- Kie.ai + Higgsfield.ai (+ researched alternatives) for assets  
- Postiz.ai for social draft publishing path  
- human gate + human voice  
- multi-theme + console intent  
- **cron/scheduled unattended execution as an end goal**  
- success criteria for the **design phase**  
- what is out of scope until implementation is requested  

### Stage 1 — Deep research: viral AI video generation (MANDATORY FIRST)

Complete **Critical first research mandate — Block A** in depth.  
Produce the viral video research brief with recommendations for this project.

### Stage 2 — Deep research: viral topic sources + extraction/scraping methods (MANDATORY)

Complete **Critical first research mandate — Block B** in depth.  
Include explicit evaluation of APIs vs browse vs **Playwright**/browser automation, with legal/ToS/robustness guardrails.  
Include how scheduled/unattended extraction should behave.  
Produce the topic-extraction research brief.

### Stage 3 — Broader systems research

Research approaches for:

1. Configurable multi-brand / multi-topic content agent architectures  
2. Separating research platforms from content platforms in content ops  
3. Brand-truth resolution from config + MCP/knowledge tools + public web  
4. Topic → brand-fit scoring and anti-forced product placement  
5. Multi-platform asset generation (posts, carousels, reels/video, blog)  
6. Postiz-style draft-first social publishing patterns and safety  
7. Human-in-the-loop review packages operators will actually use  
8. Anti-slop voice control methods that hold up in production  
9. Console/operator app patterns for maintainable day-to-day runs  
10. **Cron/scheduled agent pipelines**: idempotency, logging, exit codes, secrets, retries, partial failure, budget caps, notifications  
11. Cheap addition of new themes  

Deliverable: systems research brief with options, tradeoffs, recommendation, rejected alternatives.

### Stage 4 — Devise the design / architecture plan

Only after Stages 1–3, produce a plain-language architecture + delivery plan including:

1. Major components and responsibilities  
2. Explicit **List A research + extraction architecture** (sources, methods, Playwright/API policy, ranking, storage of research artifacts)  
3. Explicit **List B content architecture** (platforms, asset types, adaptation rules)  
4. **Viral video pipeline architecture** informed by Stage 1 research  
5. Media provider architecture for **Kie.ai + Higgsfield.ai (+ others if justified)**  
6. Brand-truth/spin architecture including **MCP extraction + fallbacks**  
7. Distribution architecture for **Postiz.ai** (drafts) + blog/site prep  
8. **Scheduler / cron architecture**: how the console app runs unattended, what a scheduled job does end-to-end, safety defaults, budgets, dedupe, observability  
9. End-to-end flow for both interactive and cron execution  
10. Theme config conceptual contents (research / spin / runtime / collection methods / schedule)  
11. Modes and human approval gates under automation  
12. Conceptual run/review package contents  
13. Multi-theme extensibility  
14. Voice + claim-safety enforcement by design  
15. Risks, failure modes, mitigations (scraping breakage, provider outages, cron partial runs, cost blowups)  
16. Open decisions needing human input  
17. Phased roadmap with acceptance criteria  
18. How a human should test/review the architecture plan **before build**  

Use diagrams if helpful.  
**Do not invent code, pseudocode, CLI syntax, schema syntax, or a mandatory folder tree in this stage.**

### Stage 5 — Present for approval

End with:

- recommended architecture direction  
- alternatives considered  
- assumptions  
- blocking questions for the human  
- recommended next step only after approval  

### Stage 6 — Implementation (only if human says proceed)

If and only if approved:

- implement according to the plan  
- first theme oriented around the HypeDigitaly / HypeLead example  
- prove multi-theme readiness conceptually or with a second theme fixture  
- keep test/safe default  
- produce reviewable packs; optional media via configured providers  
- support non-interactive execution suitable for cron  
- Postiz only in allowed modes after the human approval path is clear  

### Stage 7 — Quality gate (after build)

Multiple packs a human would publish; human voice passes; zero invented commercial claims; research→spin logic is explicit; video/reel plans match researched best practices; optional generated assets are on-brand; a scheduled/unattended-style run can complete safely and leave a reviewable package.

---

## Success definition

### Design-phase success (main bar for this assignment)

A researched, reasoned architecture plan that makes all of the following clear:

- **best practices and tool/prompt/skill stack for viral AI video generation**  
- **where viral topics are extracted and how** (including Playwright/automation policy where justified)  
- which platforms are for **deep research** vs **marketing asset generation**  
- how brand spin is resolved from **config + MCP + public verification**  
- how **Kie.ai** and **Higgsfield.ai** (and any extra tools) fit asset generation  
- how **Postiz.ai** fits draft-first social publishing after human approval  
- how multi-theme config can change both research targets and brand spin  
- how humans review before anything goes live  
- how the **console app will run automatically via cron** while remaining safe by default  
- what should be built first, second, and third — and how to know each phase is good  

### Later build success (only after approval)

An operator-usable console system that:

1. Can be run interactively for a theme, and  
2. Can be run unattended on a schedule (cron) to automatically research, spin, create packs, and optionally prepare drafts, and  
3. Still keeps live publishing human-gated by default.

---

## Start now

1. Do **not** look for or depend on a pre-existing project implementation. Uncover everything yourself.  
2. Complete **Stage 0**, then **Stage 1 (viral AI video research)** and **Stage 2 (topic extraction + scraping/automation research)** before anything else.  
3. Complete **Stage 3** systems research, including cron/scheduled execution patterns.  
4. Produce the **Stage 4 architecture/design plan**.  
5. Stop at **Stage 5** for human approval.  
6. Do **not** implement unless explicitly told to proceed.  

After each stage, state:

- what you concluded  
- what inputs you still need from the human  
- what the next review/test step is  
```