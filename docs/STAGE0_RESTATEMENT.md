# Stage 0 — Problem Restatement

*HypeAgentSocials design phase · restated in our own words · 2026-08-05*
*Governing documents: `HypeAgentSocials_InstructionsAssignment.md` (goals + constraints) and `docs/plans/DESIGN_PHASE_MASTERPLAN.md` (execution plan). This document restates the problem; it decides nothing new.*

---

## What we are building (one paragraph)

A configurable, multi-theme marketing agent: on each run it looks at what the active theme's configuration says to watch, researches what is currently trending or painful in those topics across a defined set of research platforms, filters and ranks those signals for brand fit, "spins" the best ones through the brand's verified truth (who we are, what we sell, what we may claim), produces multi-platform marketing assets — posts, carousels, and viral-style short videos/reels — and packages everything into a reviewable bundle for a human. Publishing is never automatic: after human approval the system can stage social drafts via Postiz and prepare blog material, but a human always pulls the final trigger. The whole loop must eventually run unattended on a schedule (cron), producing review-ready work while a human sleeps — safely.

## The two-list split: research platforms ≠ content platforms

The system keeps two strictly separate lists:

- **List A — where we research.** X, Reddit, tech news/launch hubs (Product Hunt, Hacker News, Hugging Face, vendor blogs), Google Trends + search-demand signals, Meta Ad Library, and secondarily TikTok Creative Center, YouTube, and public LinkedIn. These are read-only inputs: viral discourse, ICP pains, launch hype, search demand, competitor ad creative, and short-form format trends. They are **not** publish targets.
- **List B — where we create for.** LinkedIn (posts, carousels), X (posts, threads), Instagram (carousels, Reels), TikTok (short vertical video), YouTube Shorts, Facebook (community posts), plus the brand's own blog when the theme enables it.

Research sources feed insight; content destinations receive assets. The architecture must enforce this boundary structurally (a publish-destination allowlist with one enforcement point), not as a convention.

## Config-driven topics + MCP-extractable brand spin

Each theme (tenant) carries one main configuration describing **what to watch** (topics, keywords, source priorities, excludes, collection methods, cadence, languages), **how to interpret** (company, products, ICP, voice, CTAs, claim policy, product rules), and **how to run** (enabled destinations, modes/guards, media provider preferences, Postiz enablement, budgets, schedule, review expectations). Output languages are a per-theme array; every listed language (first theme: Czech + English) gets its own full, first-class output set — never a translation pass.

Brand spin must **not** rely on static config alone. It resolves from four sources in a defined precedence: theme config → MCP-connected brand knowledge (Notion MCP is the working choice; preferred when available) → public live company/product pages for verification → human run overrides. If MCP is unavailable, the system degrades honestly to config + public sources and marks reduced brand confidence in the review package. On unattended runs, if brand confidence is too low, the run downgrades to research-only output or stops — it never invents commercial facts.

## Viral AI video generation as a core design driver

Short-form viral-style video is not an add-on asset type; it shapes the architecture. Before any architecture lock we conduct deep research (Block A) on how high-performing short-form video is actually produced with AI today: hooks in the first 1–3 seconds, pacing, captions, pattern interrupts, loops, faceless vs UGC styles, B2B-safe adaptations, what reads as AI slop, model/job fit (text-to-video vs image-to-video vs keyframe-first vs multi-shot-native), carousel-to-reel transforms, draft-cheap vs final-expensive tiering, prompt/skill/agent patterns used by strong practitioners, quality rubrics for accept/reject, and the operator workflow from idea to publish-prep. The video pipeline design — including its cost controls and human gates — follows from that research, not from assumption.

## Topic extraction methods, including possible Playwright automation

For every List A source the design must state how collection works: official/public APIs where available, search and legitimate page browsing, MCP tools, authenticated integrations, or browser automation (Playwright) **only where a source is genuinely open and automation is justified**. Our default posture is scraping pessimism: anti-bot detection on major surfaces is near-total in 2026, several key sources have restrictive or commercial-use-prohibiting terms (Reddit), and some have no viable public read path at all (LinkedIn, X without paid access). The plan must include per-source fallback ladders, rate limiting, caching, deduplication, idempotent runs, a do-not-scrape list, robots/ToS grounding, and what raw artifacts are stored for auditability (with GDPR consequences considered). No login-walled scraping, ever.

## Asset generation providers: Kie.ai + Higgsfield.ai (+ alternatives)

Kie.ai (multi-model router; a trial account exists) and Higgsfield.ai (marketing-focused suite; paper evaluation only — no account) must be evaluated for images, carousels, and short video, alongside any better or complementary tools research surfaces (caption tools, avatar/UGC tools, music/VO tools, editors). The design must say when to use which provider, how routing is configured (theme vs global), cost guards and per-run budgets, dry-run vs real generation, retention/download risks, and QA rules (brand lock, no fake metrics on graphics, readable on-image text, reject the AI-slop look). Plans/prompts/scripts/shot lists are always produced even when generation keys or budget are missing; actual media generation is optional per run.

## Postiz.ai as the social draft publishing path

Postiz (trial account exists) is the intended bridge for social publishing: after human approval, the system creates **drafts** in Postiz and the human schedules or publishes. Safe/test mode refuses all Postiz side effects; staging may allow drafts only; cron may auto-create drafts only if config explicitly allows it. Silent auto-live posting is never the default. Blog content, when a theme enables it, is prepared for the brand's site pipeline with a human merging production.

## Human gate + human voice

Two non-negotiables:

1. **Human gate.** Nothing goes live without explicit human approval. The system's output is a review package per run: sources used, extraction notes, spin rationale, per-platform assets, visual/video plans, claim-safety notes, provider choices, brand-truth sources used, and automation metadata. The operator (a solo, marketing-literate human) must be able to review and decide quickly.
2. **Human voice.** Every artifact must pass the test "would a real human write this in ordinary professional conversation?" — no "it's not X, it's Y" templates, no game-changer clichés, no corporate AI mush, no fake urgency or invented metrics. Voice quality is enforced by design (layered anti-slop gates, per-language rubrics — Czech is its own rubric, not translated English), not by hope. Never invent prices, ROI, client names, case metrics, or proof. Soft CTAs by default.

## Multi-theme + console intent

One engine, many themes. The first theme is oriented around HypeDigitaly / HypeLead (AI, coding agents, lead generation, outbound/AI sales discourse; Czech + English outputs), but adding another company/topic set later must be a configuration exercise, not a rewrite. The product is an operator-facing **console application**: runnable interactively (choose theme, run research only or full pack generation, focus a topic, regenerate parts, validate theme readiness, dry-run expensive media) and non-interactively. It runs Windows-first now (console + run.bat + Task Scheduler) and must port cleanly to a Linux server later — cross-platform is mandatory.

## Cron / scheduled unattended execution as an end goal

The same console app must run as a cron job (or equivalent scheduler) on a config-defined cadence with no human at the keyboard: load theme + mode + secrets non-interactively; extract and rank topics; resolve brand truth; generate content packs and visual/video plans (optional media within budget caps); write a reviewable run package every time; exit with clear success/failure codes; log enough to debug unattended failures; avoid duplicate work across runs (idempotency/dedupe); optionally notify "new packs are ready"; optionally — only if mode/config explicitly allows — push Postiz drafts. Cron mode **fails closed**: missing secrets, ambiguous brand truth, policy violations, or publish actions not allowed by the mode stop the run or downgrade it to research-only. Budgets/caps (max videos, max slides, max provider spend per run/day) are first-class.

## Success criteria for the design phase

The design phase succeeds when a researched, reasoned architecture plan makes all of the following clear:

1. Best practices and the tool/prompt/skill stack for viral AI video generation.
2. Where viral topics are extracted and how — including an honest Playwright/automation policy.
3. Which platforms are for deep research vs marketing asset generation.
4. How brand spin resolves from config + MCP + public verification.
5. How Kie.ai and Higgsfield.ai (and any extra tools) fit asset generation.
6. How Postiz fits draft-first social publishing after human approval.
7. How multi-theme config changes both research targets and brand spin.
8. How humans review before anything goes live.
9. How the console app runs automatically via cron while remaining safe by default.
10. What should be built first, second, and third — and how to know each phase is good.

The plan must be plain-language: **no product code, pseudocode, CLI syntax, config syntax, or mandatory folder tree** (diagrams are allowed and encouraged). It ends at Stage 5 with a presentation for human approval.

## Out of scope until implementation is explicitly requested

- Writing any product code, schemas, config files, CLI commands, or cron expressions.
- Creating accounts, connecting live channels, or publishing anything anywhere.
- Actual media generation spend beyond what the human explicitly approves during design-phase fact-finding.
- The implementation itself (Stage 6) and the post-build quality gate (Stage 7) — both start only after the human approves the architecture at Stage 5, via a separate implementation plan.
