# B5 — Trend-Intelligence Platforms & Short-Form Trend Surfaces (Buy-on-Top vs Build)

Wave 1 research brief — agent T-B5 · Design phase · Written 2026-08-06
Scope: (1) deep current-state evaluation of TikTok, Instagram, and YouTube as viral-topic *research* sources; (2) survey of the trend-intelligence market — who already watches viral topics as a service, and whether our pipeline can legitimately consume their output; (3) the build-vs-buy-on-top verdict with a revised source portfolio and monthly cost.
Boundaries honored: B1 owns source roles/priorities; B2 owns extraction mechanics and the do-not-scrape list; C7 owns legal interpretation. This brief fills the gaps those briefs left open and revises their conclusions only where new evidence justifies it. All binding constraints respected: no login-walled scraping ever, F-9 scraping pessimism, Reddit API closed v1, X reads skipped v1, solo-operator budget.
Retrieval date for all volatile claims: 2026-08-06 unless noted. Priority addition per operator lead: Virlo.ai and its MCP server evaluated in depth (§3.2).

---

## 1. What this means for the operator

Short answer to your question: **yes — platforms that already watch viral topics exist, one of them fits this system unusually well, and you should buy on top of it rather than build collectors for the closed short-form platforms.** The tool is Virlo ($49/month), which tracks trends and viral outliers across exactly the three platforms you asked about — TikTok, Instagram Reels, and YouTube Shorts — refreshes daily, and, uniquely in this market, exposes its data through an MCP server, the same integration standard your pipeline already plans to use for brand truth. Instead of you building and babysitting scrapers that would break weekly (and violate platform terms), your nightly run can simply ask Virlo "what's trending, what's breaking out, what's happening in my tracked niches" over an API key that works unattended. Its weak spot: it leans consumer-creator; whether its niche monitors produce real signal for "AI tools / coding agents / AI sales" content is exactly what the free trial must answer before you pay.

On the three platforms themselves: nothing changed the B1/B2 pessimism, and some things got stricter. TikTok's Creative Center now requires a (free) business login even to browse trend analytics — it stays a monthly human ritual, and Virlo becomes your automated TikTok eye. Instagram gives you one genuine, legal, automated door because you hold Meta business accounts: the official hashtag search (top posts for up to 30 hashtags per week, with captions and engagement counts) plus business discovery for watching named competitor accounts. It cannot tell you what is trending — only how hashtags you already care about are performing — so it is a probe, not a radar. YouTube remains the best of the three: the official API's most-popular chart works per country including Czechia at a trivial quota cost, though YouTube retired the human-facing Trending page in 2025, so treat that chart as "popular now," not an editorial trend list.

Everything else in the market is either too expensive for one person (BuzzSumo's API starts at $999/month, Brandwatch/Tubular are enterprise), pointed at the wrong niche (Kalodata is TikTok Shop e-commerce, TrendHunter is consumer product ideation), or already free in your portfolio (AI newsletters, Hacker News, alerts). The honest buy list for v1 is small: Virlo at $49, the SERP/Trends data vendor B2 already chose at roughly $10–15/month of usage, and two free alert services. Total new spend: about $60–65 a month — comfortably inside budget — and it replaces the two collector families that would have been the most fragile and least legal to build yourself.

---

## 2. Part 1 — TikTok / Instagram / YouTube as viral-topic research sources

### 2.1 TikTok — Creative Center narrowed further; the automated eye must be bought, not built

**What exists in mid-2026.** The Creative Center still has two research surfaces: the **Top Ads** gallery (searchable high-performing auction ads, filters for region / objective / language / format, sortable by reach or CTR) and the **Trends** modules (ranked hashtags, songs, creators, videos, scoped by industry, time window, and region). The open-corpus hashtag search died in early 2024 (B1 §3.6) and has not returned. **New, 2026-current finding: the Trends analytics side now sits behind a TikTok for Business login** — free to create, but a login nonetheless; only the Top Ads gallery remains browsable logged-out. TikTok's own July 2026 help guidance for hashtag research begins with "Log in to Creative Center." This does not violate our rules for a *human* (the operator logging into a free business account and reading is ordinary use) — but it hardens the case that no automated fetcher will ever touch this surface (login wall + the strongest anti-bot stack on List A + explicit ToS ban, reaffirmed April 2026 per B2).

**API reality.** Unchanged and closed: the Research API is vetted-academics-only; the Commercial Content API is ad-transparency-scoped; the "API" advertised on the Creative Center site is Symphony — a generative-ad-production API, not a data-out API. There is no legitimate programmatic read path for trend data, and none is coming. The EU Commercial Content Library (DSA) remains a browse surface for ad transparency, covering CZ.

**CZ coverage.** Region filters exist in both Trends and Top Ads, but Czechia's presence is inconsistent across modules and could not be verified from outside the login wall this cycle (the Creative Center is a script-rendered app; the operator should confirm the region list on first login). Expect CZ to be missing or thin in trend modules; EU-wide and DE/PL proxies are the realistic filter.

**Signal value for this theme.** For AI/B2B/sales *topics*: weak — Creative Center trend lists are consumer-skewed. For **short-form format and hook patterns — the prize** — it remains genuinely valuable: trending sounds, pacing conventions, and the Top Ads gallery showing which hooks sustain CTR. Failure modes: module scope changes without notice (it has form), region list churn, login-session friction.

**Verdict (revises B1 slightly):** keep the monthly manual Creative Center ritual for ad-creative and sound inspiration, but move the *automated* TikTok trend feed to a licensed third party (Virlo, §3.2). TikTok is the one platform of the three where "buy on top" is not an optimization but the only automated option.

### 2.2 Instagram — the operator's Meta business account unlocks a real (narrow) official door

The operator holds Meta business accounts, which changes Instagram from "P2 minimal, do not build" (B1) to "one legitimate probe worth wiring in v2, plus a competitor watchlist." What the official Instagram platform API (business/Facebook-login flavor) genuinely exposes:

- **Hashtag search** — resolve a hashtag name to a global ID, then read that hashtag's **top media** and **recent media**: caption, media type, like count (omitted when the owner hides likes), comments count, media URL, permalink, timestamp. Top-media ranking uses "a mix of views and viewer interaction," the same methodology as the app's own top-posts surface. Public posts only; promoted/boosted content excluded; the poster's username is deliberately not returned; up to 50 items per page, forward-only pagination. **The binding quota: 30 unique hashtags per rolling 7-day window** per app user. Requirements: Instagram Business/Creator account, the Instagram Public Content Access feature (App Review — days-to-weeks lead time, same Meta developer plumbing as the Ad Library API and Threads), and standard permissions.
- **Business discovery** — read another *professional* account's public profile and media with followers count, media count, and per-post comments/likes/views. This is a legal, official competitor-watch surface: track named AI-tool and lead-gen brands' IG presence and which of their Reels formats earn engagement.
- **What it does NOT expose — and this is the ceiling:** no "what is trending" surface of any kind. No trending-hashtag list, no trending audio, no Reels trend feed, no keyword search over public content, no discovery of accounts you don't already know. The API answers "how is hashtag X / account Y doing," never "what should I be looking at." The 30-hashtag window makes it a *probe* for a curated watchlist (theme-config hashtags like ai, aitools, salestips, plus CZ-locale tags), not a radar.

**Web surfaces under F-9:** unchanged — login/anti-bot-walled, Meta ToS-hostile, and the operator's own business assets would be the collateral in any ban. Stays on B2's do-not-scrape list permanently. **CZ coverage:** hashtag search works for Czech-language hashtags where they exist; volume in this niche is thin. **Signal value:** modest for topic discovery (near zero), moderate for format/engagement validation on a known hashtag set and for competitor-account watching. **Failure modes:** app-review friction; token lifecycle (same 60-day discipline as Ad Library); the 30-hashtag window silently consumed by careless retries (budget it like money); Meta deprecation churn.

**Verdict:** adopt as a **v2 probe** (after the day-1 core is stable and the Meta app review from the Ad Library work is done anyway — it is the same developer app). Not a v1 blocker; it discovers nothing on its own.

### 2.3 YouTube — still the best official surface of the three; the Trending page is gone but the API chart lives

- **Most-popular chart, per region.** The Data API's video listing with the most-popular chart parameter is alive and documented, accepts ISO-3166 region codes (CZ accepted; historically returns Czech results), optionally filtered by video category, at a **quota cost of 1 unit per call** — effectively free. Caveat discovered this cycle: **YouTube retired the human-facing Trending page in 2025** (announced July 2025; confirmed current state: the help center now describes only "YouTube Charts" — Trending Music Videos, Trending Movie Trailers, gaming trends in the Gaming Explore page — updated roughly every 30 minutes, same list for everyone in a country, not personalized). Design consequence: the API chart should be read as "most popular right now in region X," a raw-popularity signal that skews music/entertainment/mainstream — useful for CZ mainstream context, nearly useless for niche AI/B2B topics directly.
- **Search as the niche radar.** Search ordered by date or view count for theme keywords ("AI sales agent", "Claude Code", "studený outreach") remains the real discovery tool at 100 units per call. Quota math for a daily cron on the free 10,000-unit budget: 5–8 niche searches (500–800 units) + ~50 cheap video/channel/playlist reads (~50 units) + 2 most-popular chart pulls for CZ and US (2 units) ≈ **under 900 units/day, less than 9% of quota** — comfortable, with B2's caching/dedupe discipline. The 30-day refresh-or-delete storage rule (B2 §2.7) already governs retention.
- **Research API / BigQuery.** The YouTube Researcher Program grants scaled corpus access but is explicitly restricted to students/staff/faculty of accredited degree-granting non-profit institutions — no commercial path for this operator, ever. There is no public YouTube trends dataset in BigQuery beyond community re-uploads of the old trending feed (stale; do not build on them).
- **Signal value for this theme:** the strongest of the three — titles/thumbnail packaging patterns for AI-tool content, comment threads as secondary ICP pain, Shorts format observation via channel watchlists; cs-language queries work (thin volume, B1). **Failure modes:** quota greed on search, most-popular chart mistaken for a niche trend signal, API data-retention rule.

**Verdict:** unchanged from B1 (P1, official API), with two refinements: add the 1-unit most-popular CZ pull to the daily cron for mainstream-context awareness, and treat vidIQ/1of10-class outlier tools (§3.4) as the human-facing lens for hook patterns rather than spending quota trying to replicate outlier detection in-house.

### 2.4 Platform summary

| Platform | Legit automated read path | What it yields | CZ signal | Cadence | Role in revised portfolio |
|---|---|---|---|---|---|
| TikTok | None first-party; licensed SaaS only (Virlo) | Format/hook/sound trends; Top Ads patterns | Weak, unverified region filters | Daily via Virlo; monthly human CC browse | Buy-on-top exemplar |
| Instagram | Official hashtag search (30/7d) + business discovery via operator's business account | Engagement validation on known hashtags; competitor Reels watch | Thin cs hashtag volume | Weekly probe (v2) | Narrow official probe |
| YouTube | Official Data API: search + most-popular chart (CZ), 10k units/day | Topic demand, packaging patterns, comments pain, CZ mainstream chart | Medium (cs queries work) | Daily cron | Keep, extend with chart pull |

---

## 3. Part 2 — The trend-intelligence market: who already watches viral topics

### 3.1 How to read the verdicts

**Adopt v1** = enters the day-1-to-month-1 portfolio at solo-operator cost with a legitimate machine-read path. **Candidate v2** = real value, but blocked by price, niche fit, or a dependency; has a named trigger. **Trap** = looks attractive in a listicle, fails on at least one of: price reality, export path, ToS reuse, data freshness, niche fit, or company viability. A recurring evaluation lens: *does the tool's ToS allow its output to feed our content pipeline?* Derived-insight SaaS almost universally permits internal use and forbids redistribution — our use (insights in, our own original content out) is the permitted pattern; raw-data resale APIs are where legitimacy questions live (C7).

### 3.2 PRIORITY — Virlo.ai: the MCP-native trend platform (adopt v1, trial-gated)

**What it is and tracks.** Virlo is a short-form video intelligence platform founded 2024, covering **TikTok, YouTube Shorts, and Instagram Reels** — precisely the closed-platform triangle this project cannot legally collect from itself. Feature set: Orbit search over viral videos, custom **niche monitors** (keyword-defined, recurring, with proposal/review workflow and configurable autonomy), a Tracking Center for creators/videos with alerts, trending/emerging-trend feeds, sounds intelligence (trending/breakout sounds, usage history), creator audience demographics and geography, and Meta Ads intelligence on the Pro tier. Starter-tier data is refreshed **daily**. Company-maturity signals: active weekly blog (263 posts, current through August 2026), coherent developer docs, a March 2026 MCP launch guide, product breadth growing — a young company but visibly alive and investing; churn risk is real (F-3 applies to data vendors) and is priced into the exit plan below.

**The MCP server — the architectural fit.** Virlo exposes a hosted MCP endpoint (dev.virlo.ai, path /api/mcp/mcp) with **~40 tools** across analytics, keyword research, niche monitoring, creator/sound intelligence, and tracking. Auth is a bearer API key (virlo_tkn_ prefix) minted in the developer dashboard — **which means fully unattended, cron-compatible operation with no interactive OAuth**; the OAuth flow exists only as a convenience for interactive Claude clients. Long operations auto-poll ~25 seconds then return a job ID with a documented completion signal — the collector must handle async jobs, which fits B2's snapshot-then-detail and circuit-breaker mechanics cleanly. Representative credit costs: trend digest / emerging trends / trending videos 25 credits each; hashtag search 5; keyword search 50; niche-monitor run 50 per run; creator lookup 50; most reads of already-computed results are free. Rate limits are not published (treat as a fact to capture during trial; B2's backoff discipline applies regardless).

**Pricing and the one open conflict.** Starter **$49/mo, 2,000 credits**; Pro **$199/mo, 12,000 credits** (adds Meta Ads intelligence, 3 seats, Slack/Discord/webhook alerts, Zapier/n8n); Enterprise custom. Free trial available. Conflict found and flagged: the March 2026 MCP guide states "any paid plan includes full API access; all plans support every endpoint," while the pricing page lists "API access" as an Enterprise bullet. The developer docs (API keys self-minted from the dashboard, plan-agnostic credit costs) support the blog's reading, but **this must be verified during the trial before committing** — it is the single gating fact for the adopt verdict.

**Credit budget math (Starter, 2,000/mo).** A realistic daily cron: one trend digest (25) daily = 750/mo; emerging trends twice weekly = 200; one AI/B2B niche-monitor run weekly = 200; ~10 hashtag/sound spot-checks weekly = ~250; slack for occasional creator lookups = ~300. Total ≈ 1,700 of 2,000 credits — **Starter fits the designed cadence with ~15% headroom**, and the free-read pattern (monitors' stored results cost nothing to re-read) rewards exactly the cache-before-call discipline B2 mandates.

**ToS on feeding our pipeline.** Explicitly workable: users may incorporate "API responses into their own applications, internal analyses, dashboards, and end-user products," and content created with Virlo's tools "belongs to you." Prohibited: scraping, reselling, sublicensing, or redistributing Virlo's data outputs to third parties; using the API to build a competing product or train models to replicate its analytics. Our pattern — trend insights in, original human-reviewed brand content out, no republication of Virlo data — sits squarely in the permitted zone. One honest caveat for C7: Virlo's *upstream* collection from TikTok/IG/YT is undisclosed and cannot be platform-licensed (no such license program exists); consuming a vendor's derived analytics is a materially different posture than buying raw scraped passthrough (the twitterapi.io class B2 excluded), and is the same posture as using Exploding Topics or BuzzSumo — but it deserves one paragraph in C7's read.

**Niche fit and CZ — the two honest weaknesses.** Virlo's marketing and examples are consumer-creator (skincare, home gym, personal-injury-law creators). Niche monitors are keyword-defined, so pointing one at "AI tools / coding agents / AI sales" content is supported by design — but whether short-form AI/B2B content has enough tracked density to yield signal is unproven. No CZ/regional trend filtering is evidenced; assume global-EN. **Trial gate (one week, before paying):** (1) confirm MCP/API access on Starter; (2) run an "AI tools + AI sales" niche monitor and judge whether its outliers beat what the free portfolio already surfaces; (3) capture actual rate limits. **Exit plan** if Virlo churns or degrades: the pipeline loses the automated short-form trend axis and falls back to the operator's monthly Creative Center ritual — a degraded-but-designed state (B2's ladder grammar), not a break.

**Verdict: adopt v1 at Starter $49/mo, gated on the one-week trial.** It replaces the collector family we must not build (TikTok/IG/Shorts trend automation), feeds the video pipeline's hook/format research directly, and is the only tool in this survey whose integration surface (MCP, bearer-key, headless) matches the architecture as designed.

### 3.3 Trend-spotting SaaS (search/consumer-demand class)

- **Exploding Topics** — trend database + forecasting over search/social data. Pricing verified: Entrepreneur **$39/mo** (100 tracked trends), Investor **$99/mo** (500 trends, **CSV export**, forecasting), Business **$249/mo** (2,000 trends, reports); 7-day trial. **No public API found** (the API path 404s; no tier lists one). Niche fit: genuinely decent for AI/B2B SaaS topic *validation* — it tracks tools and category terms in this space; freshness is weekly-scale, not viral-scale. CZ: none (global search demand). ToS: standard internal-use SaaS. Verdict: **candidate v2** at the $99 tier if the demand axis (Trends UI + DataForSEO) proves too thin — the CSV export is the machine path; at $39 there is no export, making it operator eye-candy only. Not v1: overlaps heavily with free newsletters + HN for discovery, and demand validation is already covered cheaper.
- **Glimpse** — Google Trends augmentation (absolute volumes, channel breakdowns incl. TikTok/LinkedIn/Reddit, alerts, forecasting), strong Chrome extension. Pricing page is script-rendered and shows no figures (B2's earlier capture: from ~$99/mo, 10 free searches); API exists only as an enterprise offering, unverified. Verdict: **candidate v2** as operator tooling on top of the manual Trends ritual; the free extension tier is worth installing day 1 (zero cost, enriches the weekly manual pull). Not a pipeline input.
- **Treendly** — Google-Trends-derived niche trend finder. Site is bot-walled (403) and shows staleness signals in the wider market; no verified export/API path. Verdict: **trap** (stale-data class; adds nothing over Trends + Glimpse).
- **TrendHunter** — consumer-product trend ideation database + enterprise reports/AI. Bot-walled this cycle; known model: free browsing with account, monetized via enterprise reports. Niche fit for B2B AI/sales: poor (consumer product innovation focus). Verdict: **trap** for this theme (wrong niche, enterprise monetization).

### 3.4 Content intelligence

- **BuzzSumo** — cross-web content engagement, Trending Feeds, Question Analyzer. Pricing verified: Content Creation **$199/mo**, PR & Comms $299, Suite $499, Enterprise **$999/mo — the only tier with API access**; free trials. Verdict: **trap for a solo operator** — the useful machine path costs $12k/yr (exactly the enterprise class the constraints exclude), and the $199 UI tier duplicates what HN + newsletters + Virlo provide. Revisit only at agency scale.
- **Tubular Labs** — enterprise social-video intelligence (25B+ videos, YouTube/IG/FB/Twitch), seat-based, quote-only, API exists. Verdict: **trap** (enterprise pricing, media-company ICP).
- **vidIQ** — YouTube trend/outlier research + AI tooling. Free tier includes niche trends and content ideas; Boost (misrendered price on the pricing page; historically ~$19–25/mo billed yearly) adds "unlimited trends research"; Max **$39/mo** (billed yearly); no public API. Works for researching *any* channel/niche, not just your own. Verdict: **free tier as operator tooling day 1; candidate v2 paid** when the YouTube video pipeline scales. Not a pipeline input (no export path).
- **TubeBuddy** — own-channel optimization extension; weaker than vidIQ/1of10 for researching others. Verdict: skip.
- **1of10** — YouTube **outlier finder** (videos performing 10–100x their channel baseline) + thumbnail/title pattern research; exactly the "hook patterns are the prize" tool for YouTube. Pricing verified: **free tier** (outlier search, 3 tracked channels), Basic **$29/mo**, Pro $69/mo; no API. Verdict: **adopt v1 at the free tier as operator tooling** (weekly outlier session feeding the curated inbox); candidate paid at $29 when Shorts production ramps.

### 3.5 TikTok-specific trackers

- **Trendpop** — **dead as a standalone product**: trendpop.com now 301-redirects to collab.inc (acquired/absorbed). Verdict: **trap (gone)** — and a vendor-churn cautionary tale for this whole category.
- **Kalodata** — TikTok *Shop* e-commerce intelligence (product/creator/livestream revenue); site bot-walled this cycle; free-trial model per third-party listing. Niche: e-commerce sellers, not B2B content. Verdict: **trap for this theme** (wrong niche entirely).
- **Exolyt** — TikTok analytics, Essentials ~$400/mo (per Virlo's comparison listicle; vendor-biased source, medium-low confidence). Verdict: **trap** (price class above justification for one platform).
- **TrendTok-class prediction apps** — consumer creator apps (~$15/mo, mobile-first, no export). Verdict: skip.
- **TikHub-class data APIs** ($29/mo+, "TikTok data API") — unofficial scraper-backed passthrough of raw platform data, the same class as the twitterapi.io gateway B2 flagged: the vendor absorbs technical risk, not our compliance posture, and raw-data passthrough is the least defensible corner of this market. Verdict: **trap (excluded by the project's legitimate-access principle; confirm with C7 as with D6).**
- **Shortimize, Pentos** — short-form tracking (Shortimize cross-platform with free tier; Pentos TikTok sounds/music history). Thin public pricing; overlap with Virlo. Verdict: skip v1; Shortimize is the natural **fallback candidate if Virlo fails its trial** — same category, evaluate with the same gate.

### 3.6 Social listening — the solo-friendly end, and free alerts

- **Brand24** — the most credible solo-adjacent listening suite. Pricing verified: Individual **$249/mo monthly ($199 annual)** — 3 keywords, 12-hour updates; Team $349/$299 — hourly; Pro $499/$399 — real-time; **API is a $99 add-on at any tier**; 14-day trial. Coverage claims include TikTok, Instagram, YouTube, Reddit, X, podcasts, newsletters. Verdict: **candidate v2** — it is the cheapest legitimate route to *mention-level* social coverage (including a Reddit-shaped signal without a Reddit API), but $199–348/mo including API sits in "low hundreds needs justification" territory, and v1's topic-discovery needs are already covered. Trigger: a paying second theme/tenant that needs brand-mention monitoring (a different job than trend discovery — note the category difference: listening watches *your keywords being mentioned*; trend platforms watch *what is rising*).
- **Mention** — pricing now opaque (site shows a "Company Plan" with placeholder values; API as a paid add-on; free trial). Verdict: skip — cannot even price it without a sales call.
- **Awario** — $29–299/mo mention monitoring (vendor-listicle sourced); collection posture on closed platforms unclear (C7-class question). Verdict: skip v1.
- **Talkwalker Alerts** — **verified live and free in 2026** despite the Hootsuite acquisition: keyword alerts over news/blogs/forums/X, delivered by **email and RSS**, Slack integration. RSS delivery makes it directly machine-readable. Verdict: **adopt v1** (free alert layer for theme keywords + competitor names, cs and en).
- **Google Alerts** — free keyword alerts over Google's index. Email delivery confirmed current; **RSS delivery is no longer documented in the current help article** — a possible quiet removal; verify at setup and design the ingest around email-to-inbox (which the pipeline needs for newsletters anyway), with RSS as a bonus if the option still appears. Verdict: **adopt v1** (free, cs-locale capable).
- Enterprise suites (Brandwatch, Talkwalker full, Meltwater, Sprout at $399/mo+) — remain out per B1/B2; nothing new changes that.

### 3.7 Newsletter / digest products with structured output

B1 already adopted AI newsletters at P0; this brief adds the *machine-readability* facts: **Ben's Bites** now lives on Substack (confirmed), which exposes a standard RSS feed by platform design — as do TLDR AI and The Rundown via their platforms; **email-to-inbox ingest plus RSS covers the whole class** without any vendor API. Smol AI's daily "AI News" digest (RSS + email) is a strong structured-adjacent addition for the AI/coding-agents topics — it clusters Discord/Reddit/X discourse editorially, partially compensating for closed platforms. HN digest services (Hackernewsletter etc.) are redundant for us: the HN Algolia API in the day-1 core is already the superior machine path. No newsletter product surveyed offers a true public API worth building against; none is needed.

### 3.8 The emerging "agent-accessible trend intelligence" subcategory

Virlo is not alone in exposing data to AI agents — it is early in a visible 2026 pattern:

- **DataForSEO** (already B2's chosen SERP/Trends vendor) publishes an **official open-source MCP server** (actively maintained, 10 API modules including SERP, Keywords Data, Labs, and an AI-optimization module) with basic-credential auth against the same pay-as-you-go account. Design consequence: **both paid data vendors in the revised portfolio speak MCP** — the research-collector layer can standardize on one integration idiom for licensed data (Virlo for short-form trends, DataForSEO for search demand), with bespoke collectors reserved for the free open APIs (HN, PH, HF, Bluesky, YouTube, feeds).
- Virlo's own comparison content (vendor-biased, but the only 2026 survey of this exact subcategory) positions Brand24, Brandwatch, Sprout, Modash, Phyllo, TikHub, Awario as API-bearing adjacents — none MCP-native, and each already dispositioned above. No second MCP-native *trend* platform surfaced this cycle; if the Virlo trial fails, the fallback is Shortimize-class + manual ritual, not another MCP vendor.

### 3.9 Master verdict table

| Tool | Watches | Freshness | Machine path | Solo price reality | ToS reuse posture | Niche fit (AI/B2B/sales) | CZ | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Virlo** | TikTok + Reels + Shorts trends/outliers/sounds/creators | Daily (Starter) | **MCP + REST, bearer key, headless** | $49/mo | Internal use OK; no redistribution | Unproven — trial gate | None evidenced | **Adopt v1 (trial-gated)** |
| **DataForSEO** | Google SERP + Trends (demand axis) | On-demand | REST + **official MCP** | ~$10–15/mo usage | Data-vendor terms (C7 D3) | Good (keyword-driven) | Yes (geo) | **Adopt v1** (per B2 D3) |
| **Talkwalker Alerts** | News/blogs/forums/X mentions | Near-real-time | Email + **RSS** | Free | Alerts for internal use | Keyword-driven | Yes (cs keywords) | **Adopt v1** |
| **Google Alerts** | Google index mentions | Daily-ish | Email (RSS uncertain) | Free | Ordinary use | Keyword-driven | Yes (cs) | **Adopt v1** |
| **1of10** | YouTube outliers/hooks | Continuous | UI only | Free tier; $29/mo | Internal use | Strong for packaging | EN | **Adopt v1 (free, operator tool)** |
| vidIQ | YouTube trends/AI ideas | Continuous | UI only | Free; ~$19–39/mo | Internal use | Good (YouTube) | EN | Candidate v2 |
| Exploding Topics | Search/consumer trend database | Weekly-scale | CSV at $99 tier; **no API** | $39–249/mo | Internal use | Decent (validation) | None | Candidate v2 ($99 trigger) |
| Glimpse | Trends augmentation | Weekly-scale | Extension; ent. API only | ~$99/mo; free ext. | Internal use | Decent (validation) | Partial (Trends geo) | Candidate v2; free ext. day 1 |
| Brand24 | Mentions across socials incl. Reddit-shaped | 12h–real-time by tier | API +$99 add-on | $199–448/mo | Internal use | Keyword-driven | Yes (cs keywords) | Candidate v2 (2nd-tenant trigger) |
| Shortimize / Pentos | Short-form tracking | Continuous | Thin/unclear | Free tiers exist | Unclear | Overlap w/ Virlo | None | Fallback if Virlo trial fails |
| BuzzSumo | Content engagement/trending | Real-time-ish | **API only at $999/mo** | $199+ UI | Internal use | Moderate | None | **Trap** (API price wall) |
| Tubular Labs | Social video (enterprise) | Continuous | API, quote-only | Enterprise | — | Media-company ICP | None | **Trap** |
| TrendHunter | Consumer product trends | Slow | None useful | Ent. reports | — | Wrong niche | None | **Trap** |
| Treendly | Search niche trends | Stale-class | None verified | ~$/yr class | — | Weak | None | **Trap** |
| Trendpop | TikTok (was) | — | — | — | — | — | — | **Trap (dead — redirects to collab.inc)** |
| Kalodata | TikTok Shop e-commerce | Continuous | Unclear | Trial model | — | Wrong niche | None | **Trap** |
| Exolyt | TikTok analytics | High-frequency | Implied API | ~$400+/mo | — | Overkill single-platform | None | **Trap** (price) |
| TikHub-class raw APIs | Scraped platform data | Continuous | REST | $29+/mo | **Raw passthrough — excluded class** | — | — | **Trap** (legitimacy, per D6 posture) |
| Mention / Awario | Mentions | Real-time-ish | Add-on/unclear | Opaque / $29+ | Unclear | Keyword-driven | Partial | Skip |

---

## 4. Part 3 — Build vs buy-on-top: the verdict and the revised portfolio

### 4.1 The verdict

**Buy on top exactly where platforms are closed; keep building only what is free and officially open.** The market genuinely contains "already watches viral topics for us" products, but only one intersects all four constraints (solo price, legitimate machine path, unattended operation, short-form coverage): Virlo. The correct posture is therefore a **hybrid**: the free official-API collectors from B1/B2 remain the discovery backbone (they cost nothing and cannot be bought better), while two licensed vendors — Virlo (short-form trend axis) and DataForSEO (demand axis, already chosen by B2) — replace the two collector families that were either impossible to build legally (TikTok/IG/Shorts trends) or ToS-adverse to build directly (Google Trends/SERP). Both vendors speak MCP, which collapses integration cost and matches the brand-truth MCP pattern already in the architecture. Nothing in this survey replaces the human-curated inbox (Reddit Pro, LinkedIn browsing, communities) — no affordable product covers ICP pain legitimately; Brand24 comes closest and is priced as a v2 decision.

### 4.2 Revised v1 source portfolio (supersedes B1 §5 "honest day-1 portfolio" by addition, not replacement)

| Layer | Sources | Method | Monthly cost |
|---|---|---|---|
| Automated discovery core (daily cron) | HN, AI newsletters (email/RSS incl. Ben's Bites, Smol AI), Product Hunt, Hugging Face, Bluesky, Google News RSS | Free official APIs/feeds (B1/B2 as designed) | $0 |
| Automated short-form trend axis (daily cron) | **Virlo via MCP** — trend digest, emerging trends, one AI/B2B niche monitor, sound/hashtag spot-checks (~1,700 of 2,000 credits) | Licensed SaaS, bearer-key MCP, headless | **$49** |
| Automated demand axis (weekly cron) | **DataForSEO** Trends + SERP tasks for theme keywords, cs + en, geo=CZ | Licensed vendor (REST or official MCP) | **~$10–15 usage** |
| Automated alert layer (continuous) | Talkwalker Alerts (RSS/email) + Google Alerts (email) on theme keywords + competitor names, cs + en | Free alert services into the ingest inbox | $0 |
| Official platform probes | YouTube Data API: niche searches + CZ most-popular chart (<900 units/day); (v2: IG hashtag probe + business discovery) | Official APIs, operator's own accounts | $0 |
| Weekly human layer | Trends UI CSV, Meta + LinkedIn Ad Libraries, Reddit Pro + curated inbox, 1of10 free outlier session, Glimpse extension | Operator ritual (B1 as designed) | $0 |
| Monthly human layer | TikTok Creative Center (business login), G2-class review browse | Operator ritual | $0 |

**Total new recurring spend: ~$60–65/month** (Virlo $49 + DataForSEO usage) — inside the "tens of dollars" comfort band. One-time: DataForSEO minimum account funding (small, consumed as usage), Virlo trial (free).

### 4.3 v2 candidates with named triggers

| Candidate | Cost | Trigger |
|---|---|---|
| Exploding Topics Investor | $99/mo | Demand axis proves too thin after 8 weeks of DataForSEO + manual Trends; CSV export is the integration path |
| Brand24 Individual/Team + API | $199–448/mo | Second paying theme/tenant needs brand-mention monitoring; partially substitutes Reddit-shaped signal |
| IG hashtag probe + business discovery | $0 | Meta app review completed (rides Ad Library onboarding); 30-hashtag watchlist defined in theme config |
| vidIQ Boost / 1of10 Basic | ~$19–29/mo | Shorts/YouTube production ramps and outlier research becomes a daily rather than weekly need |
| Virlo Pro | $199/mo | Credit exhaustion at Starter, or Meta Ads intelligence + webhook alerts justify the jump |
| Shortimize evaluation | TBD | Virlo fails its trial gate or churns (F-3 vendor risk) |

### 4.4 Traps — attractive but rejected (rationale one line each)

BuzzSumo (API behind $999/mo enterprise wall); Tubular Labs (enterprise, wrong ICP); TrendHunter (consumer-product niche, enterprise reports); Treendly (stale-class, no verified export); Trendpop (dead — domain redirects to its acquirer); Kalodata (TikTok Shop e-commerce, wrong niche); Exolyt ($400+/mo for one platform); TikHub-class raw-data APIs (unofficial scraped passthrough — excluded by the project's legitimate-access principle, C7 to confirm as with D6); Mention (opaque pricing, API as add-on, sales-call wall); enterprise listening suites (B1/B2 disposition stands).

---

## 5. Decision table

### Decisions unblocked by this brief → architecture area

| Decision | → Architecture area |
|---|---|
| Short-form trend axis (TikTok/Reels/Shorts) is bought, not built: Virlo Starter via its MCP server, trial-gated on Starter-tier API access + AI/B2B niche signal quality | Research collectors; MCP client layer; provider budget guards (credit metering as first-class budget) |
| Licensed-vendor integration standardizes on MCP where offered (Virlo, DataForSEO official MCP); bespoke collectors only for free open APIs/feeds | Collector architecture; one integration idiom for licensed data |
| Virlo collector must handle async job-polling (auto-poll then job ID) and treat stored-result re-reads as free | Collector scheduling; cache-before-call discipline |
| TikTok Creative Center: trend analytics now login-gated — remains human-only monthly ritual; Top Ads stays logged-out browsable; no engineering spend (B1 stance reaffirmed, tightened) | Operator runbook |
| Instagram official probe adopted for v2: hashtag search (30-unique/7-day budget managed like money) + business discovery watchlist, riding the same Meta app/token plumbing as Ad Library | Theme config (hashtag watchlist); Meta token lifecycle; v2 roadmap |
| YouTube daily cron adds CZ + US most-popular chart pulls (1 unit each) as mainstream-context signal, explicitly labeled non-niche; search stays the niche radar under a <10% quota budget | YouTube collector; ranking (chart signal weighted as context, not topic candidate) |
| YouTube Researcher Program ruled out permanently (academic-only) | Closed question — no revisit trigger |
| Free alert layer (Talkwalker Alerts RSS/email + Google Alerts email) feeds the same ingest inbox as newsletters | Ingest architecture (email-to-inbox is a first-class transport) |
| 1of10 free tier + Glimpse free extension enter the weekly operator ritual (hook/packaging research) | Operator runbook; curated-inbox inputs |
| Trap list (§4.4) is settled — no further evaluation cycles on BuzzSumo/Tubular/TrendHunter/Treendly/Trendpop/Kalodata/Exolyt/Mention this phase | Scope control |
| Vendor-churn resilience: every licensed source gets a designed degraded state (Virlo → monthly CC ritual; DataForSEO → manual Trends CSV) per B2's ladder grammar | Fallback ladders; source-health flags |

### Decisions deferred → open decision

| Deferred decision | Trigger / owner |
|---|---|
| Virlo adopt/reject confirmation | One-week free trial: Starter API access confirmed + niche-monitor signal quality for AI/B2B topics — operator, week 1–2 |
| Virlo upstream-collection legitimacy paragraph (derived-analytics vendor vs raw-passthrough class) | C7 legal read; working assumption: permitted class (same as Exploding Topics/BuzzSumo) |
| Exploding Topics $99 adoption | 8-week demand-axis review — operator |
| Brand24 adoption | Second-tenant brand-monitoring need — operator + budget |
| IG probe hashtag watchlist contents (which 30 hashtags, cs/en split) | Theme-config design — after Meta app review completes |
| Google Alerts RSS availability (undocumented in current help) | Verify at setup; email ingest is the design default regardless |
| Shortimize as Virlo fallback | Only if Virlo trial fails or vendor churns |
| TikTok CC region-list CZ verification | First operator login to Creative Center — runbook item |

---

## 6. Fact ledger

All retrieved 2026-08-06 by direct fetch unless noted. Confidence: High = first-party page; Med = credible secondary or partially rendered page; Low = vendor-biased or knowledge-inferred.

| Claim | Source URL | Retrieved | Confidence | Recheck by |
|---|---|---|---|---|
| IG hashtag search: max 30 unique hashtags per 7-day period; requires Instagram Public Content Access feature + business/creator account; returns hashtag ID | https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag-search | 2026-08-06 | High | 2027-02-01 |
| IG hashtag top-media: returns caption, comments_count, like_count (omitted if hidden), media_type, media_url, permalink, timestamp; no username; public only; ads excluded; 50/page, after-cursor only; ranking = views + interaction | https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag/top-media | 2026-08-06 | High | 2027-02-01 |
| IG Business Discovery: followers_count, media_count, per-media comments/likes/views for professional accounts; age-gated accounts excluded | https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/business-discovery | 2026-08-06 | High | 2027-02-01 |
| YouTube videos.list chart=mostPopular live, regionCode ISO-3166, videoCategoryId filter, quota cost 1 unit | https://developers.google.com/youtube/v3/docs/videos/list | 2026-08-06 | High | 2027-02-01 |
| YouTube help now describes Charts only (Trending Music Videos / Movie Trailers / Gaming via Explore), ~30-min updates, same per country — Trending page no longer a surface | https://support.google.com/youtube/answer/7239739 | 2026-08-06 | High (current state); Med (July 2025 removal date, knowledge-based) | 2026-12-01 |
| YouTube Researcher Program: academic-only (students/staff/faculty of accredited non-profit degree-granting institutions), 60+ countries | https://research.youtube/how-it-works/ | 2026-08-06 | High | 2027-02-01 |
| TikTok Creative Center 2026: Top Ads browsable logged-out; Trends hashtag analytics requires business login ("Log in to Creative Center", July 2026 help); industry/time/region-scoped ranked lists only | https://novoads.ai/en/blog/tiktok-creative-center (article dated 2026-07-19) | 2026-08-06 | Med-High | 2026-12-01 |
| Virlo pricing: Starter $49/mo (2,000 credits, daily data refresh), Pro $199/mo (12,000 credits, Meta Ads intelligence, 3 seats, webhooks/Zapier/n8n), Enterprise custom; free trial | https://virlo.ai/pricing | 2026-08-06 | High | 2026-11-01 |
| Virlo covers TikTok, YouTube Shorts, Instagram Reels; niche monitors, tracking center, sounds, Meta Ads intelligence, MCP server | https://virlo.ai/ | 2026-08-06 | High | 2026-11-01 |
| Virlo MCP: endpoint at dev.virlo.ai (path /api/mcp/mcp), bearer API keys (virlo_tkn_ prefix) minted in dashboard, headless-capable; ~40 tools; credits: trend digest/emerging trends/trending videos 25, hashtag search 5, keyword search 50, niche-monitor run 50/run, creator lookup 50, most result-reads free; async auto-poll ~25s then job ID | https://dev.virlo.ai/docs/mcp | 2026-08-06 | High | 2026-11-01 |
| Virlo MCP guide (2026-03-27): "any paid plan includes full API access; all plans support every endpoint" — CONFLICTS with pricing page listing API access under Enterprise | https://virlo.ai/blog/how-to-connect-virlo-to-claude-desktop-cowork-and-openclaw-via-mcp vs https://virlo.ai/pricing | 2026-08-06 | Med (conflict — verify at trial) | trial, week 1–2 |
| Virlo ToS: incorporation of API responses into own applications/analyses/products permitted; created content belongs to user; resale/redistribution/sublicensing of Virlo data prohibited; no competing-product or model-replication use | https://virlo.ai/terms | 2026-08-06 | High | 2027-02-01 |
| Virlo maturity: founded 2024 (schema markup), 263 blog posts, weekly trend updates current through 2026-08-03 | https://virlo.ai/blog | 2026-08-06 | Med | 2026-12-01 |
| Exploding Topics Pro: Entrepreneur $39/mo (100 trends), Investor $99/mo (500 trends, CSV export, forecasting), Business $249/mo (2,000 trends); 7-day trials; no API mentioned on pricing; /api path returns 404 | https://explodingtopics.com/pro ; https://explodingtopics.com/api (404) | 2026-08-06 | High | 2026-11-01 |
| BuzzSumo: Content Creation $199/mo, PR&Comms $299, Suite $499, Enterprise $999 (annual billing); API (Account + Search) Enterprise-only; trials on all tiers | https://buzzsumo.com/pricing/ | 2026-08-06 | High | 2026-11-01 |
| Brand24: Individual $249/mo ($199 annual, 3 keywords, 12h updates), Team $349/$299 (hourly), Pro $499/$399 (real-time), Business $699/$599, Enterprise $1,499+/yr; API $99 add-on all tiers; 14-day free trial; sources incl. TikTok/IG/YT/Reddit/X/podcasts/newsletters | https://brand24.com/prices/ | 2026-08-06 | High | 2026-11-01 |
| Talkwalker Alerts live and free in 2026; email + RSS + Slack delivery; 600k+ users claimed; no discontinuation notice | https://www.talkwalker.com/alerts | 2026-08-06 | High | 2026-12-01 |
| Google Alerts current help documents email delivery only; RSS delivery no longer mentioned | https://support.google.com/websearch/answer/4815696 | 2026-08-06 | Med (absence of evidence) | 2026-11-01 |
| Mention pricing opaque: "Company Plan" with placeholder values; API as paid add-on; free trial | https://mention.com/en/pricing/ | 2026-08-06 | Med | 2026-12-01 |
| vidIQ: Max $39/mo (billed yearly); "unlimited trends research" from Boost tier; Boost price misrendered on fetch (historically ~$19–25/mo yearly); no API on pricing page | https://vidiq.com/pricing/ | 2026-08-06 | Med (partial render) | 2026-11-01 |
| 1of10: free tier (outlier search, 3 tracked channels), Basic $29/mo ($349/yr), Pro $69/mo (1,000 AI credits); no API; active | http://1of10.com/ | 2026-08-06 | High | 2026-12-01 |
| Tubular Labs: enterprise seat-based quote-only; 25B+ videos across YT/IG/FB/Twitch; API exists | https://www.tubularlabs.com/ | 2026-08-06 | High | 2027-02-01 |
| Trendpop dead as standalone: trendpop.com 301-redirects to collab.inc | https://trendpop.com (redirect observed) | 2026-08-06 | High | stable |
| Kalodata site bot-walled (403); positioned as TikTok Shop e-commerce intelligence with free 7-day trial | https://www.kalodata.com/ (403) ; https://virlo.ai/blog/best-real-time-competitor-performance-tracking-tools-short-form-video-2026 | 2026-08-06 | Med-Low | 2026-12-01 |
| DataForSEO official MCP server: open-source, 10 modules (SERP, Keywords Data, Labs, OnPage, Backlinks, Business Data, Domain Analytics, Content Analysis, Merchant, AI Optimization), credential auth, actively maintained (217 commits) | https://github.com/dataforseo/mcp-server-typescript | 2026-08-06 | High | 2027-02-01 |
| Competitor pricing per Virlo listicles (vendor-biased): TikHub $29/mo+ free tier; Modash $99+; Awario $29–299; Sprout $399+; Exolyt Essentials $400/Advanced $950; Socialinsider $82–199; Keyhole from $79; Metricool free/$22+; Shortimize + Pentos free tiers, pricing unlisted; only Virlo claims agent-accessible integration | https://virlo.ai/blog/best-real-time-social-video-monitoring-platforms-api-2026 ; https://virlo.ai/blog/best-real-time-competitor-performance-tracking-tools-short-form-video-2026 (both 2026-07-28) | 2026-08-06 | Med-Low (vendor source) | 2026-12-01 |
| Brand24 pricing discrepancy: Virlo listicle claims $79–179/mo vs first-party $249+ — first-party adopted | https://brand24.com/prices/ (authoritative) | 2026-08-06 | High | 2026-11-01 |
| Glimpse: free signup exists; channel breakdown across TikTok/LinkedIn/Reddit/IG/X/YT/FB/Pinterest; Chrome extension 170k+ users; pricing not displayed (script-rendered); B2's prior capture: from ~$99/mo | https://meetglimpse.com/pricing/ ; B2 §2.9 | 2026-08-06 | Med | 2026-11-01 |
| Ben's Bites operates as a Substack newsletter (archive to Jun 2024, consistent cadence) — RSS available by platform design | https://www.bensbites.com/ | 2026-08-06 | Med-High | 2027-02-01 |
| Treendly (403) and TrendHunter (403) bot-walled; no machine path verified for either | https://treendly.com/ ; https://www.trendhunter.com/ | 2026-08-06 | Med (access state only) | 2026-12-01 |

Volatile-claim currency: all 27 rows rest on pages fetched live 2026-08-06 (or observed redirects/404s the same day) — 100% current against the ≥60% Feb-2026+ requirement. Note: session search quota was exhausted by earlier Wave 1 agents; this brief is built on direct first-party fetches, which strengthens (not weakens) the pricing/API rows, at the cost of two knowledge-inferred dates flagged Med above (YouTube Trending removal announcement date; vidIQ Boost price).

---

## 7. Sources

First-party platform documentation (all retrieved 2026-08-06):
- https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag-search
- https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag/top-media
- https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/business-discovery
- https://developers.google.com/youtube/v3/docs/videos/list
- https://support.google.com/youtube/answer/7239739
- https://research.youtube/how-it-works/
- https://support.google.com/websearch/answer/4815696
- https://ads.tiktok.com/business/creativecenter/pc/en

Vendor first-party (all retrieved 2026-08-06):
- https://virlo.ai/ ; https://virlo.ai/pricing ; https://virlo.ai/mcp ; https://virlo.ai/terms ; https://virlo.ai/blog
- https://dev.virlo.ai/docs/mcp
- https://virlo.ai/blog/how-to-connect-virlo-to-claude-desktop-cowork-and-openclaw-via-mcp (published 2026-03-27)
- https://explodingtopics.com/pro
- https://buzzsumo.com/pricing/
- https://brand24.com/prices/
- https://www.talkwalker.com/alerts
- https://mention.com/en/pricing/
- https://vidiq.com/pricing/
- http://1of10.com/
- https://www.tubularlabs.com/
- https://meetglimpse.com/pricing/
- https://www.bensbites.com/
- https://github.com/dataforseo/mcp-server-typescript

Secondary, 2026-dated (retrieved 2026-08-06):
- https://novoads.ai/en/blog/tiktok-creative-center (2026-07-19) — Creative Center current state incl. login-gated Trends
- https://virlo.ai/blog/best-real-time-social-video-monitoring-platforms-api-2026 (2026-07-28) — API-bearing monitoring platforms survey (vendor-biased)
- https://virlo.ai/blog/best-real-time-competitor-performance-tracking-tools-short-form-video-2026 (2026-07-28) — competitor tracking tools survey (vendor-biased)

Negative/observational evidence (2026-08-06): https://trendpop.com → 301 to https://www.collab.inc/ ; https://explodingtopics.com/api → 404 ; https://meetglimpse.com/api/ → 404 ; https://treendly.com/ , https://www.trendhunter.com/ , https://www.kalodata.com/ → 403 bot walls.

Cross-referenced sibling briefs: B1_sources.md (source roles/priorities, Ad Library and Trends resolutions), B2_extraction_methods.md (method matrix, do-not-scrape list, DataForSEO selection, aggregator landscape).
