# B1 — Research Source Universe: Roles, Priorities, Access Reality (List A + Extensions)

Wave 1 research brief — agent T5. Design phase only. Scope: the global List A research-source universe — per-source role, signal value, priority, cadence, failure modes, resolved stances on contested sources, cs-relevance flags, and day-1 usability. Extraction *mechanics* are owned by brief B2; Czech-native venues are owned by brief B4 (this brief only flags which global sources carry Czech-market signal). Retrieved dates for all volatile claims: 2026-08-06.

---

## 1. What this means for the operator

The original List A assumed a world where the big social platforms could be read by software. In mid-2026 that world mostly does not exist. X killed its free read tier in February 2026 and you have already decided not to pay a reseller, so the system will not read X in v1 — and honestly, it loses less than it sounds like, because the same AI news breaks on Hacker News, AI newsletters, and Bluesky within hours, and your publishing is human-gated anyway. Reddit closed its last free doors in late 2025 and May 2026; the realistic v1 answer is not an API at all — it is Reddit's own free business tool (Reddit Pro) plus roughly an hour a week of you reading threads and dropping the good ones into the system's inbox. That hour is worth it: the GojiBerry founder interview you supplied shows Reddit is exactly where your buyers (SaaS founders, sales and marketing people) complain about outreach tools in public, in detail, with numbers.

The good news is bigger than the bad news. A surprisingly strong research portfolio is available **on day 1, free, with zero legal risk**: Hacker News (full official API), Product Hunt, Hugging Face, Bluesky (free firehose plus a trending endpoint), AI newsletters, Google Trends through its website and RSS, YouTube's official API, and — this is the sleeper hit for you — the **ad libraries**. Because of the EU's Digital Services Act, every Meta ad and every LinkedIn ad shown to EU users (including Czech users) is in a public, searchable library, LinkedIn's without any login at all. That is competitor hooks, offers, and creative patterns targeted at *your* market, legally, for free. Meta's version even has an API you can unlock in about a week with an ID check — your existing Meta business account makes the setup smoother but does not skip the ID check.

What you should expect: an automated daily/weekly harvest from the open sources, a weekly human curation ritual for Reddit and LinkedIn, and manual monthly check-ins on TikTok's Creative Center and review sites. What you should not expect: automated reading of X, LinkedIn feeds, or Reddit in v1 — every "workaround" for those is either against terms of service, technically dead, or both, and this system is built to never scrape behind logins.

---

## 2. Source-by-source evaluation

### 2.1 How to read the priorities

Priorities below are **re-ranked from List A based on access reality**, not just signal value. A source with world-class signal but no legal automated access (Reddit, X, LinkedIn organic) cannot be P0 for an unattended cron pipeline; it becomes a human-curated input or drops. Conversely, sources List A treated as one bucket ("tech news") contain the single best free API in the niche (Hacker News) and deserve promotion. Signal-type legend: **VD** viral discourse · **IP** ICP pain · **LH** launch hype · **SD** search demand · **AC** ad creative patterns · **FT** short-form format trends.

### 2.2 Re-ranked portfolio at a glance

| Source | Signals | Old rank | New rank | Access mode (v1) | Realistic cadence | Day-1? | cs-signal |
|---|---|---|---|---|---|---|---|
| Hacker News | VD, IP, LH | P0 (bucketed) | **P0 — anchor** | Official free APIs (Firebase + Algolia), no key | Daily | Yes | None (EN) |
| AI newsletters *(extension)* | LH, VD | — | **P0** | Email/RSS ingest, free | Daily | Yes | None (EN) |
| Product Hunt | LH | P0 (bucketed) | **P0** | Free GraphQL API (non-commercial caveat) + public pages | Daily–weekly | Yes | None (EN) |
| Hugging Face | LH | P0 (bucketed) | **P0** | Official free Hub API (trending) | Weekly | Yes | None (EN) |
| Bluesky *(extension)* | VD, LH | — | **P0** | Official free API incl. trending endpoint | Daily | Yes | Weak |
| Google Trends | SD | P0 | **P0 (manual) / P1 (automated)** | UI + CSV + RSS day 1; official API = gated alpha | Weekly (niche terms), daily (RSS general) | Yes (manual) | **Yes** (geo=CZ) |
| Meta Ad Library | AC | P0 | **P0** | UI day 1; API after ID verification (~1–2 wks) | Weekly | Yes (UI) | **Yes** (EU/DSA incl. CZ) |
| Reddit | IP (best-in-class), VD | P0 | **P1 — human-gated** | Reddit Pro (free, official) + operator curation; no automation | Weekly human session | No (~days) | Weak |
| YouTube | SD, IP (comments), VD | P1 | **P1** | Official Data API v3, 10k units/day free | Weekly | Yes (same-day key) | Medium (cs queries work) |
| LinkedIn Ad Library *(extension)* | AC | — | **P1** | Public web, no login | Biweekly | Yes | **Yes** (EU targeting data) |
| TikTok Creative Center | FT | P1 | **P1 — narrowed** | Public/business-login UI only; no commercial API | Monthly manual | Yes (UI) | Weak–medium |
| LinkedIn organic (public) | VD (B2B framing) | P1 | **P2 — human only** | Operator's own browsing + own page analytics | Weekly human glance | Yes (human) | Medium (operator's network) |
| X (Twitter) | VD, LH | P0 | **Skipped v1 (D-08)** | Nothing legitimate free for programmatic read | — | No | — |
| Threads *(extension)* | VD | — | **P2** | Official keyword-search API after app review | Daily once approved | No (~days–wks) | Weak |
| GitHub trending *(extension)* | LH (coding agents) | — | **P2** | Public page browse; no official trending API | Weekly | Yes (browse) | None |
| Podcasts | IP, VD | P2 | **P2** | RSS + PodcastIndex API (free key) | Monthly | Yes | Weak (cs pods → B4) |
| Review sites (G2 etc.) | IP, AC (positioning) | P2 | **P2** | Manual browse; API partner-gated | Quarterly | Yes (manual) | None |
| Instagram public | FT | P2 | **P2 — minimal** | Via Meta Ad Library + own accounts only | Monthly | Partial | Weak |
| Discord/Slack communities *(extension)* | IP | — | **P2 — human only** | Operator membership, zero automation (login-walled) | Ad hoc | Yes (human) | Weak |
| Google News RSS *(extension)* | LH, VD | — | **P1** | Free per-query RSS feeds, supports Czech locale | Daily | Yes | **Yes** (hl=cs) |

### 2.3 Per-source detail

**Hacker News — P0 anchor.** The single best free, legal, cron-friendly source for this theme (AI, Claude Code, coding agents, AI-sales tooling all trend here constantly). Role: viral dev discourse, launch hype, and — underrated — ICP pain in comment threads ("Ask HN" threads about outbound spam, AI SDR fatigue). Two official free APIs: the Firebase live API run by HN itself and the Algolia full-text search API, no key required. Failure modes: fully EN and dev-skewed (sales/marketing pains appear refracted through a technical audience); occasional Algolia latency; ranking is community-driven so hype can be anti-commercial in tone. Cadence: daily automated pull of front page plus keyword search; dedupe across days is mandatory (stories linger 24–48 h).

**AI newsletters (extension — promote to P0).** The Rundown (~2M subscribers as of 2026), TLDR AI, Ben's Bites. Role: professionally pre-curated launch hype and tool discovery — effectively a free human editorial layer over X, which partially compensates for the X skip. Overlap between dailies is ~80% on big news days, so ingest one or two, not five. Method note: email-to-inbox or RSS ingest, trivially legal. Failure modes: 12–36 h behind X on breaking items; editorial bias toward consumer-facing AI; sponsor placements must be filtered out as non-signal. Cadence: daily.

**Product Hunt — P0.** Role: launch hype and competitor DNA in the AI/lead-gen tool space. Free GraphQL v2 API (6,250 complexity points per 15 min) is live and self-serve as of Aug 2026, but maker/social fields were redacted back in 2023 and PH's terms restrict commercial use without consent — same legal *class* of question as Reddit, though far lower stakes at our read volume. Fallback that removes all doubt: the public daily leaderboard pages and the PH newsletter carry the needed signal (product name, tagline, category, vote momentum). Failure modes: gaming/launch-pod distortion of vote counts; category tagging is loose; API deprecations with little notice. Cadence: daily or weekly digest.

**Hugging Face — P0.** Role: model/tool launch hype upstream of mainstream coverage; strong for the "AI" and "coding agents" topics, irrelevant to lead-gen topics. Official free Hub API includes trending sorts for models/datasets/spaces. Failure modes: research-crowd skew — trending-on-HF does not equal marketable topic; needs a brand-fit filter more than any other source. Cadence: weekly is enough; the half-life of an HF trend is days, not hours.

**Bluesky (extension — add at P0).** The only real-time public social firehose that is free and officially sanctioned in 2026. Role: partial X substitute for viral AI/dev discourse; a meaningful slice of the AI/dev commentariat is active there. Official API: free, documented rate limits, public trending-topics endpoint, plus the Jetstream firehose. Failure modes: much smaller than X and skews anti-big-tech, so "sales/outbound" discourse is thin; trends surface later and smaller; the unspecced trending endpoint is explicitly unstable API surface and can change without notice. Cadence: daily automated.

**Google Trends — P0 manual, P1 automated.** Role: search-demand validation — the "is this hype or demand" arbiter, and one of only three global sources with direct Czech-market signal (geo=CZ works throughout). Access reality (F-9 confirmed): no stable official API for general use — the official Trends API announced July 2025 is still an application-gated alpha in 2026; unofficial libraries are ToS-gray and rate-limit-broken. What is real on day 1: the web UI with CSV export (manual, weekly, per configured topic list) and the Trending Now RSS feed (free, automatable, but general-population trends, not niche AI terms — useful mostly for cs mainstream context). Complements: Google Ads Keyword Planner through the operator's own Ads account (free, official, monthly volumes incl. CZ) and Google News per-query RSS. Failure modes: relative-not-absolute index confuses ranking logic; RSS reliability wobbles; alpha access may never arrive. Cadence: weekly manual pull for theme keywords; daily RSS.

**Meta Ad Library — P0.** Role: competitor ad hooks, offers, and creative patterns (research only). Access is genuinely two-lane. Lane 1, day 1: the public web UI, searchable without login. Lane 2, ~1–2 weeks: the official Ad Library API — free, but requires personal government-ID verification (1–3 business days) plus terms acceptance, ~200 calls/hour standard, tokens need refresh every 60 days. Critical DSA nuance verified against Meta's own docs: **commercial ads that reached EU users are returned by the API** (with reach and demographic breakdowns); non-EU commercial ads are UI-only. For a Czech operator this is exactly backwards from the usual complaint — the EU/CZ competitor set is the *well-covered* part. Operator's existing Meta business account: does **not** waive ID verification (it is personal), but satisfies the developer-account prerequisite and makes app/token administration cleaner. Failure modes: 60-day token expiry silently breaking cron runs; rate-limit ceilings on broad keyword sweeps; ad text is returned but video creative requires viewing in UI; Meta pulled political ads from the EU in late 2025, which does not affect our commercial-ads use. Cadence: weekly per configured competitor/keyword list.

**Reddit — P1, human-gated (full resolution in §3.1).** Role: best-in-class ICP pain — unfiltered complaints about outbound tools, AI SDRs, lead-gen spam, plus viral founder-story formats. The GojiBerry transcript is direct practitioner evidence in exactly this niche: an intent-based outreach SaaS took itself from $0 to ~$30k MRR with ~11M Reddit impressions and ~40k site visits, and its founder's virality recipe (story + receipts + curiosity gap, never naming the product) is itself a reusable *content-format* insight our engine should learn from. Note the transcript describes Reddit as a publishing channel with ToS-gray tactics (upvote pods, account warming) — we take the *evidence of audience and formats*, not the tactics. Access reality: see §3.1 — no legitimate automated read path at our scale in v1. Cadence: one weekly 30–60 min operator session (Reddit Pro trends review + manual thread curation into the system's inbox). Failure modes: operator skips the ritual and the pipeline silently loses its best pain source (design a staleness flag); Reddit Pro is Reddit's own product and can change scope at will.

**YouTube — P1 (keep).** Role: topic demand and packaging patterns (titles/thumbnails of AI-tools and lead-gen videos), plus comment threads as a secondary ICP-pain vein; also the research feed for B-brief video-format work. Official Data API v3: free, 10,000 units/day (search costs 100 units ≈ 100 searches/day), key issued same day, no card. Czech-language queries work, though cs AI/lead-gen volume is thin. Failure modes: quota exhaustion if search is used greedily (cache aggressively, prefer channel playlists at 1 unit); captions/transcripts are not freely available via API for arbitrary videos — treat transcript mining as a B2 method question, not a given. Cadence: weekly.

**LinkedIn Ad Library (extension — add at P1).** The legitimate LinkedIn surface. Public, searchable, **no login required**, covers ads since June 2023, retained one year after last impression; for EU-targeted ads (CZ included) it exposes impression ranges per country and targeting parameters (job function, seniority, industry, geo) under DSA. Role: B2B ad hooks and offers aimed at our exact ICP — including what competitors run against Czech decision-makers. Failure modes: no engagement metrics; no API (systematic browse only — method question for B2); search is basic. Cadence: biweekly manual/assisted sweep of competitor names + category keywords.

**TikTok Creative Center — P1, narrowed (full resolution in §3.6).** Role reduced to short-form format/hook inspiration (FT), not topic discovery. Cadence: monthly manual browse. Failure modes: scope changes without notice (form: the 2024 hashtag-search removal); some views require a free TikTok for Business login; regional filters may not include Czechia for all modules.

**LinkedIn organic — P2, human only (full resolution in §3.4).** Operator's own feed browsing plus own company-page analytics. No automation, ever, on this surface.

**X — skipped in v1 under closed D-08 (full resolution in §3.2).**

**Threads (extension — P2).** Meta's official keyword-search API for public posts exists (2,200 queries per rolling 24 h per user), gated behind app review — days-to-weeks of lead time, same Meta developer plumbing as Ad Library. Role: secondary real-time discourse probe. Worth queueing after day-1 sources are live, ahead of any X reconsideration, since it is free and first-party. Failure modes: sensitive-keyword empty responses; app-review friction; AI/dev discourse density lower than Bluesky's.

**GitHub trending (extension — P2).** Role: coding-agents niche signal (what repos the Claude Code audience is excited about). No official trending API; the public trending page is browsable, and the official Search API sorted by stars is a legal approximation. Failure modes: trending page markup changes; star-farming noise. Weekly glance, automatable later per B2's call.

**Podcasts — P2.** Role: slower-moving ICP pain and narrative framing (sales-tech and AI pods). Access: open RSS universe plus the free PodcastIndex API; transcripts increasingly ship with episodes. Monthly. Czech podcasts belong to B4. Failure modes: transcript availability inconsistent; signal lags social by weeks — use for depth, not freshness.

**Review sites (G2-class) — P2.** Role: category pains and competitor positioning language for lead-gen tooling. Access: APIs are partner-gated; public pages sit behind aggressive anti-bot; ToS prohibit scraping. Verdict: quarterly manual review by the operator, treated as background research, not pipeline input. No automation.

**Instagram public — P2, minimal.** Public-page automated reading is login/anti-bot-walled and Meta ToS-hostile. Realistic v1 role: none beyond what Meta Ad Library already reveals about IG ad creative, plus the operator's own accounts. Do not build against this surface.

**Discord/Slack communities (extension — P2, human only).** Real ICP pain lives in founder/sales communities, but everything is login-walled; automated extraction would violate both platform ToS and this project's own no-login-scraping rule. Legitimate mode: operator is a member, reads, and manually forwards insights to the same curated inbox as Reddit. Zero build cost, zero legal cost.

**Google News RSS (extension — P1).** Free per-query RSS feeds over Google News, supporting Czech locale — a cheap, legal, automatable tech-news monitor for theme keywords in both languages, and one of the few automatable cs-signal carriers. Failure modes: feed format quirks; clickbait density. Daily.

---

## 3. Resolved recommendations — contested sources

### 3.1 Reddit (F-1) — resolved: human-gated in v1, no API

The flag is confirmed and 2026 made it stricter. Timeline of door-closings: paid API tiers (2023) → self-serve commercial API access closed (Nov 2025) → GummySearch, the dominant affordable research tool, shut down commercially Nov 2025 after Reddit denied API terms (full shutdown Dec 2026) → unauthenticated .json endpoints deprecated and returning 403 (announced May 28, 2026). Free non-commercial OAuth (100 QPM) exists but our use is commercial on its face; commercial use requires approval at ~$0.24/1k calls with a reported ~$12k/yr enterprise floor and weeks-to-months of negotiation. The only real options:

| Option | Cost | Lead time | Legal caveat | Verdict |
|---|---|---|---|---|
| A. Licensed social-listening partner (Brandwatch/Cision, Sprinklr, Meltwater — official partner as of Feb 13 2026, Sprout Social, Talkwalker) | Enterprise SaaS, roughly $10k–40k+/yr (estimate; no public rate cards) | Days–weeks (sales cycle) | Fully compliant; verify the vendor's Reddit license covers *your* use in writing | Overkill for one operator; revisit at agency scale |
| B. Reddit Pro (Reddit's own free business tool; Trends launched Jan 2025 — keyword tracking, conversation volume, AI thread summaries) | Free | Days (business account setup) | Compliant — it is Reddit's product; insight use, not bulk export; scope can change at Reddit's whim | **Adopt for v1** |
| C. Human-curated input: operator reads Reddit normally, pastes selected pain threads/links into the system's research inbox | Operator time, ~30–60 min/wk | Zero | Clean — a human reading a public site is ordinary use; the hard line: never automate the logged-in session | **Adopt for v1** |
| D. Drop Reddit entirely for v1 | Zero | Zero | None | Rejected — GojiBerry evidence says this niche's richest pain signal lives here; B+C captures most value at near-zero cost |

**Resolution: B + C together.** Reddit stays in the portfolio as a *human-gated weekly source*, and the architecture should treat "curated human input" as a first-class source type (it also serves Discord/Slack/LinkedIn browsing). Enterprise API (A) is a deferred decision with a concrete trigger: multiple paying themes/tenants wanting Reddit signal.

### 3.2 X under closed D-08 (flag F-2) — resolved: skipped; here is what honestly remains and what is lost

*(F-2 note: this section covers the READ path only. X-as-publish-destination via Postiz user-OAuth is a separate, independent later decision — owned by brief C1.)*

D-08 stands: no paid reseller, no research reads in v1. What remains legitimately free/public as of Aug 2026: effectively **nothing for programmatic discovery**. X replaced tiered pricing with pay-per-use as the default on Feb 6, 2026 and discontinued the free tier (which had been write-only since 2023 anyway); web search has been login-walled since 2023; Nitter-class mirrors are dead; scraping behind the login wall is off the table by project rule. The only legitimate free touchpoints are non-discovery: rendering a specific known post via embeds, and *secondhand* X discourse relayed through tech press, newsletters, and HN/Bluesky threads — which the portfolio already ingests.

What the system loses: (1) earliest-hours virality — major AI announcements still break on X first; (2) X-native formats (quote-tweet dunks, thread structures) as direct format inspiration; (3) a slice of AI-sales/outbound practitioner discourse that never leaves X. Honest damage assessment: **low for v1.** The pipeline publishes through a human review gate on a daily-to-weekly rhythm; a 6–24 h relay delay via HN/newsletters/Bluesky is immaterial at that cadence. Documented for the deferred table, not as a recommendation: X's own first-party pay-per-use read pricing ($0.005/read, so ~10k reads/month ≈ $50) is not a reseller and would be the natural reopening path if the operator ever revisits D-08 for v2.

### 3.3 Meta Ad Library access path (F-9) — resolved: two-lane, and the business account helps but does not shortcut

Lane 1 (day 1): public UI research, no login, covers CZ/EU competitor ads. Lane 2 (~1–2 weeks): official API — free; requires a Meta developer account, **personal government-ID verification** (1–3 business days) and Ad Library API terms acceptance; ~200 calls/hr; 60-day token expiry. Does the operator's existing business account change the path? **Partially:** it does not waive ID verification (that is bound to a person, not a business), but it removes account-setup friction, anchors the developer app, and eases long-lived token management. DSA coverage means EU-delivered commercial ads — the ones aimed at the Czech market — are API-queryable with reach and demographic data. Resolution: start Lane 1 on day 1, initiate Lane 2 verification in week 1, design cron jobs to fail closed and alert on token expiry.

### 3.4 LinkedIn read reality (F-9) — resolved: organic surface is human-only; the Ad Library is the machine-readable surface

Confirmed and worse than the flag: no public read API exists; the Marketing/Community APIs are partner-gated around managing *your own* presence; enforcement visibly escalated through 2026 (HeyReach's company page removed and its founder's profile banned, March 2026; Apollo.io and Seamless.ai page removals reported 2025). One more angle matters to this operator: holding a LinkedIn company page means the company itself is in a contractual relationship with LinkedIn — scraping would not be a gray-zone stranger's act, it would be the operator's own breach, endangering the page that is also a *publishing* destination (List B). Resolution: (a) LinkedIn organic reading = operator's human browsing, funneled through the curated inbox; (b) own company-page analytics through the page admin surface = legitimate feedback signal; (c) **LinkedIn Ad Library** (public, no login, DSA targeting data for EU) = the systematic research surface, added at P1; (d) zero LinkedIn automation of any logged surface, permanently, not just v1.

### 3.5 Google Trends access (F-9) — resolved: manual-first, alpha application in parallel

Options, all real: (1) web UI + CSV export — day 1, manual, weekly, per-theme keyword list, geo=CZ supported — **adopt**; (2) Trending Now RSS feed — free and automatable but general-population trends only — adopt for mainstream/cs context; (3) official Trends API — announced July 24, 2025, still application-gated alpha in 2026 with restricted quotas; apply immediately, plan nothing on it — **apply and wait**; (4) third-party paid wrappers (SerpApi-class, DataForSEO-class) — they work by scraping Google, which transfers commercial risk but not ToS cleanliness; **defer**, flag honestly if ever adopted; (5) adjacent official signals — Keyword Planner via the operator's own Google Ads account (free, official, CZ volumes) and Brave Search API as a legitimate licensed SERP-ish probe (free tier replaced by ~$5/mo credits ≈ 1,000 queries in Feb 2026) — adopt as complements when B2 wants them. Search-demand's pipeline role is *validator/ranking modifier*, not discovery — weekly manual cadence is genuinely sufficient for v1.

### 3.6 TikTok Creative Center — resolved: keep at P1 with a narrowed, honest role

The open hashtag-search era ended in early 2024 (removed after researcher/lawmaker scrutiny); what remains is industry-scoped ranked trend lists, Top Ads views (some behind a free TikTok for Business login), and songs/creators modules. The research-grade Commercial Content API is academics-only — no commercial path exists or is likely. The EU Commercial Content Library (library.tiktok.com, DSA-mandated, covers EEA incl. CZ) adds an ad-transparency browse surface. Resolution: TikTok CC is a **monthly, manual, format-inspiration source** — hooks, pacing, sound trends for the reels pipeline — not a topic-discovery engine and not an automation target. Value for B2B AI/lead-gen topics is modest; do not spend engineering on it.

---

## 4. Czech-relevance flags (global sources only — Czech-native venues are B4's)

| Source | Carries CZ-market signal? | Nature of the signal |
|---|---|---|
| Google Trends | **Yes — direct** | geo=CZ interest data, cs queries; Trending Now for CZ mainstream |
| Meta Ad Library | **Yes — direct** | DSA: all ads delivered to CZ users searchable; API returns EU reach/demographics |
| LinkedIn Ad Library | **Yes — direct** | EU-targeted ads show CZ impression counts + targeting (job function, seniority) |
| Google News RSS | **Yes — direct** | cs-locale feeds per theme keyword |
| YouTube | Medium | cs-language search works via API; thin cs volume in AI/lead-gen niches |
| TikTok Creative Center / CCL | Weak–medium | CCL covers EEA incl. CZ ads; Creative Center regional filters inconsistent for Czechia |
| LinkedIn organic (human) | Medium | Operator's own CZ B2B network is itself a cs-signal source |
| Reddit | Weak | Czech subreddits exist but are small; the pain signal here is global-EN |
| Bluesky, Threads | Weak | Marginal Czech presence in these niches |
| HN, Product Hunt, Hugging Face, newsletters, GitHub, G2, podcasts | None–weak | Global-EN only; use for topic discovery, localize via B4 sources |

Design implication: the cs side of the pipeline leans on Trends-CZ + the two ad libraries + Google News cs + B4's native venues; global-EN sources feed topic discovery that then gets a Czech spin, not Czech evidence.

---

## 5. Day-1 reality — the honest starting portfolio

**Usable day 1, zero legal/account lead time:** Hacker News (no key at all), Bluesky (public endpoints), Google Trends UI/CSV/RSS, Meta Ad Library UI, LinkedIn Ad Library, TikTok Creative Center browse, Google News RSS, newsletters (subscribe today), GitHub trending browse, podcasts RSS, G2 manual browse, YouTube Data API (key same day, no card), Product Hunt API (self-serve token same day; or skip the API and use public pages).

**Days to ~2 weeks:** Meta Ad Library API (ID verification 1–3 business days + terms + app setup); Reddit Pro (business account setup, days); Threads keyword-search API (app review); PodcastIndex key (instant, listed here only for accuracy of "requires signup").

**Weeks, months, or never:** Reddit commercial API (enterprise negotiation — months, five figures); Google Trends official API (gated alpha, indefinite wait — apply day 1 anyway); licensed social-listening suites (sales cycle, budget-gated); TikTok research APIs (academics only — never); LinkedIn read API (does not exist for this purpose — never); X reads (closed by D-08).

**The honest day-1 portfolio** is therefore: HN + newsletters + Product Hunt + Hugging Face + Bluesky + Google News RSS as the automated discovery core; Trends UI + both ad libraries as the weekly manual/assisted layer; YouTube API as the packaging/demand probe. Coverage by signal type on day 1: launch hype **excellent**; viral dev discourse **good** (X-shaped hole, largely relayed); search demand **adequate** (manual); ad creative patterns **good** (both ad libraries, CZ included); ICP pain **the real day-1 gap** — closed within the first two weeks by the Reddit Pro + curated-inbox ritual, with YouTube comments as an interim vein. No source in the day-1 set carries meaningful legal risk, and none violates the no-login-scraping rule.

---

## 6. Decision table

### Decisions unblocked by this brief → architecture area

| Decision | → Architecture area |
|---|---|
| Reddit v1 = Reddit Pro + weekly human-curated inbox; no Reddit API calls in v1 | Research collectors; "curated human input" as first-class source type; staleness flagging |
| X reads absent from v1 source registry; Bluesky + newsletters + HN designated as relay coverage | Source registry / collector design; ranking must not assume X-style velocity data |
| Meta Ad Library: UI research from day 1, API onboarding started week 1; cron must fail closed on 60-day token expiry | Collector scheduling; secrets/token lifecycle; failure alerting |
| LinkedIn: zero automation on logged surfaces permanently; LinkedIn Ad Library adopted at P1 as the machine-usable B2B ad surface | Do-not-automate policy list; ad-pattern research module |
| Google Trends: manual weekly UI/CSV + RSS in v1; role = ranking validator, not discovery; alpha application filed | Ranking pipeline (search-demand as modifier); operator runbook |
| TikTok CC: monthly manual, format-inspiration only; no engineering spend | Format-trend input to video pipeline; operator runbook |
| Day-1 automated core = HN, Product Hunt, Hugging Face, Bluesky, Google News RSS, newsletters, YouTube API | Collector build order; cron cadence defaults (daily core / weekly manual layer) |
| cs-signal routing: Trends-CZ + Meta AL + LinkedIn AL + Google News cs are the global carriers; EN sources discover, B4 sources localize | Theme config (language/source mapping); ranking |
| Curated-inbox pattern serves Reddit, LinkedIn browsing, Discord/Slack, podcasts alike | Operator workflow; review package inputs |

### Decisions deferred → open decision

| Deferred decision | Trigger / owner |
|---|---|
| Reddit licensed aggregator (Brandwatch/Meltwater/Sprinklr class) | Multiple paying themes want Reddit signal; budget approval — operator |
| Reopening X via first-party pay-per-use (~$0.005/read; ≈$50/mo at 10k reads) | Operator explicitly reopens D-08 for v2; not a v1 action |
| Threads API adoption at P2 | After day-1 core is stable; requires Meta app review — B2 for mechanics |
| Paid Trends wrappers (SerpApi/DataForSEO class) despite ToS grayness | Only if search-demand automation becomes blocking; honest risk flag required — operator |
| Brave Search API / Keyword Planner as SERP-demand complements | B2's method design for the demand validator |
| GitHub trending automation approach (page vs. star-sorted Search API) | B2 mechanics decision; browse suffices meanwhile |
| Product Hunt API commercial-use posture (API vs. public-pages fallback) | Legal-comfort call by operator; public pages are the no-question fallback |
| Podcast transcript mining depth | Post-v1; depends on topic gaps observed in practice |

---

## 7. Fact ledger

| Claim | Source URL | Retrieved | Confidence | Recheck by |
|---|---|---|---|---|
| X replaced tiered API pricing with pay-per-use as default on 2026-02-06; no free tier for new developers; reads $0.005/post capped at 2M/mo | https://www.netrows.com/blog/x-twitter-api-pricing-tiers-2026 (corroborated: https://docs.x.com/x-api/getting-started/about-x-api — credit-based pay-per-use confirmed first-party) | 2026-08-06 | High | 2026-11-01 |
| X legacy Basic ($200/mo) / Pro ($5,000/mo) closed to new signups; Enterprise ≈ $42k/mo | https://www.xpoz.ai/blog/guides/understanding-twitter-api-pricing-tiers-and-alternatives/ | 2026-08-06 | Medium-high | 2026-11-01 |
| Reddit Data API: free non-commercial at ≤100 QPM; commercial use needs approval, ~$0.24/1k calls, enterprise floor ≈ $12k/yr, no self-serve commercial tier | https://www.techloy.com/reddit-api-pricing-in-2026-complete-guide-for-developers-and-businesses/ and https://www.socialcrawl.dev/blog/reddit-data-api-2026 | 2026-08-06 | Medium-high | 2026-11-01 |
| Reddit deprecated unauthenticated .json endpoints (announced 2026-05-28; now 403); self-serve API access closed Nov 2025 | https://crawlora.net/blog/reddit-json-api-blocked-2026 | 2026-08-06 | Medium-high | 2026-11-01 |
| GummySearch shut down commercially Nov 2025 after Reddit denied API terms; full shutdown 2026-12-01 | https://prowlo.com/blog/gummysearch-shut-down-what-now and https://redreach.ai/directory/reddit-tools/gummysearch | 2026-08-06 | High | 2026-12-01 |
| Reddit Pro is free for businesses; Trends tool (launched Jan 2025) tracks keywords, conversation volume, communities, AI thread analysis | https://techcrunch.com/2025/01/07/reddit-intros-new-trends-tools-for-businesses-and-an-ama-ad-format/ (2025-01-07) | 2026-08-06 | High | 2026-11-01 |
| Official Reddit data partners include Brandwatch/Cision, Sprinklr, Sprout Social, Talkwalker; Meltwater gained official partner status 2026-02-13 | https://markets.financialcontent.com/observerreporter/article/gnwcq-2026-2-13-meltwater-earns-official-data-partner-status-with-reddit | 2026-08-06 | Medium-high | 2027-02-01 |
| Meta Ad Library API: free but requires personal government-ID verification (1–3 business days) + terms; ~200 calls/hr standard; 60-day token expiry | https://adlibrary.com/guides/facebook-ad-library-api and https://admanage.ai/blog/facebook-ads-library-api | 2026-08-06 | Medium-high | 2026-11-01 |
| Meta ads_archive API returns EU-delivered commercial ads; non-EU ads only if political/social-issue ("Ads that did not reach any location in the EU will only return if they are about social issues, elections or politics") | https://developers.facebook.com/docs/graph-api/reference/ads_archive/ (first-party) | 2026-08-06 | High | 2027-02-01 |
| Google Trends official API announced 2025-07-24; still application-gated alpha with restricted quotas as of 2026 | https://developers.google.com/search/blog/2025/07/trends-api (first-party) and https://scrapebadger.com/blog/does-google-trends-have-an-api-what-to-use-in-2026 | 2026-08-06 | High | 2026-11-01 |
| Google Trends Trending Now RSS export exists and is active | https://support.google.com/trends/answer/3076011 and https://trends.google.com/trending | 2026-08-06 | Medium-high | 2026-11-01 |
| LinkedIn enforcement escalation: HeyReach company page removed + founder banned (March 2026); Apollo.io / Seamless.ai page removals (2025); UA §8.2 bars scraping/automation | https://linkedinsider.blog/linkedin-automation-crackdown-2026 and https://nubela.co/blog/is-scraping-linkedin-legal-in-2026/ | 2026-08-06 | Medium-high | 2026-11-01 |
| LinkedIn Ad Library: public, no login, covers ads since June 2023, retained 1 yr after last impression; EU-targeted ads expose impression ranges + targeting parameters (DSA) | https://adlibrary.com/guides/linkedin-ad-library-guide and https://spideraf.com/articles/linkedin-ads-library-legally-spy-on-competitors-top-linkedin-ads | 2026-08-06 | Medium-high | 2026-11-01 |
| TikTok removed open hashtag search in Creative Center (early 2024) over censorship-research scrutiny; industry-scoped ranked lists remain | https://www.socialmediatoday.com/news/tiktok-implements-restrictions-hashtag-search-creative-center/703956/ (2024) and https://novoads.ai/en/blog/tiktok-creative-center | 2026-08-06 | High | 2027-02-01 |
| TikTok Commercial Content API is restricted to approved researchers (US/EU), non-commercial commitment, ~1,000 req/day; no path for marketers; CCL at library.tiktok.com covers EEA/UK/CH | https://adlibrary.com/guides/tiktok-ad-library-api and https://www.auditsocials.com/blog/tiktok-eu-digital-services-act-ad-transparency-compliance-2026 | 2026-08-06 | Medium-high | 2027-02-01 |
| Bluesky API free (no paid tier); public trending endpoint app.bsky.unspecced.getTrendingTopics; Jetstream firehose free | https://www.blotato.com/blog/bluesky-api-pricing and https://github.com/bluesky-social/atproto/discussions/3822 | 2026-08-06 | High | 2026-11-01 |
| Threads keyword-search API: official, public posts, 2,200 queries per rolling 24 h, requires app approval; sensitive keywords return empty | https://developers.facebook.com/docs/threads/keyword-search/ (first-party) | 2026-08-06 | High | 2027-02-01 |
| Product Hunt GraphQL v2 API live and self-serve: 6,250 complexity pts / 15 min (GraphQL), 450 req / 15 min (other v2); maker/social fields redacted since Feb 2023 | https://api.producthunt.com/v2/docs/rate_limits/headers (first-party) and https://norahsakal.com/blog/product-hunt-api-changes/ | 2026-08-06 | High | 2027-02-01 |
| Hacker News: official free Firebase API + free Algolia search API, no key required | https://www.algolia.com/developers/code-exchange/hacker-news and https://cotera.co/articles/hacker-news-api-guide | 2026-08-06 | High | 2027-02-01 |
| YouTube Data API v3: free, 10,000 units/day default (search = 100 units), key same day, no card; quota raise by request only | https://www.getphyllo.com/post/youtube-api-limits-how-to-calculate-api-usage-cost-and-fix-exceeded-api-quota and https://www.socialcrawl.dev/blog/youtube-data-api-2026 | 2026-08-06 | High | 2027-02-01 |
| Brave Search API: free tier removed Feb 2026; new users get ~$5/mo credits (≈1,000 queries); card required | https://www.implicator.ai/brave-drops-free-search-api-tier-puts-all-developers-on-metered-billing/ | 2026-08-06 | Medium-high | 2026-11-01 |
| The Rundown ~2M+ subscribers (2026); daily AI newsletters overlap ~80% on major news days | https://dupple.com/learn/best-ai-newsletters-2026 and https://www.demandsage.com/ai-newsletters/ | 2026-08-06 | Medium | 2027-02-01 |
| GojiBerry AI: ~$30k MRR, ~11M Reddit impressions, ~40k site visitors, first ~100 customers via Reddit; virality recipe = story + proof + curiosity gap, product never named in post | Local: docs\marketing\GojiBerry_YoutubeInspiration\GojiBerry_Reddit_01.txt (practitioner interview transcript) | 2026-08-06 | High (as testimony; self-reported figures) | — |

---

## 8. Sources

Primary / first-party:
- Meta ads_archive reference — https://developers.facebook.com/docs/graph-api/reference/ads_archive/ (retrieved 2026-08-06)
- Threads Keyword Search docs — https://developers.facebook.com/docs/threads/keyword-search/ (retrieved 2026-08-06)
- X API overview (pay-per-use credits) — https://docs.x.com/x-api/getting-started/about-x-api (retrieved 2026-08-06)
- Google Trends API alpha announcement — https://developers.google.com/search/blog/2025/07/trends-api (published 2025-07-24)
- Google Trends "Trending Now" + help — https://trends.google.com/trending ; https://support.google.com/trends/answer/3076011 (retrieved 2026-08-06)
- Product Hunt API v2 docs / rate limits — https://api.producthunt.com/v2/docs/rate_limits/headers (retrieved 2026-08-06)
- Algolia HN Search — https://www.algolia.com/developers/code-exchange/hacker-news (retrieved 2026-08-06)
- Bluesky trending-topics discussion (atproto) — https://github.com/bluesky-social/atproto/discussions/3822 (retrieved 2026-08-06)
- Local evidence — GojiBerry_Reddit_01.txt practitioner transcript (read in full 2026-08-06)

Secondary, 2026-dated:
- Reddit API pricing 2026 — https://www.techloy.com/reddit-api-pricing-in-2026-complete-guide-for-developers-and-businesses/ ; https://www.socialcrawl.dev/blog/reddit-data-api-2026
- Reddit .json shutdown (May 2026) — https://crawlora.net/blog/reddit-json-api-blocked-2026
- GummySearch shutdown — https://prowlo.com/blog/gummysearch-shut-down-what-now ; https://redreach.ai/directory/reddit-tools/gummysearch
- Meltwater–Reddit official partner (2026-02-13) — https://markets.financialcontent.com/observerreporter/article/gnwcq-2026-2-13-meltwater-earns-official-data-partner-status-with-reddit
- X pricing 2026 — https://www.netrows.com/blog/x-twitter-api-pricing-tiers-2026 ; https://www.xpoz.ai/blog/guides/understanding-twitter-api-pricing-tiers-and-alternatives/
- Meta Ad Library API 2026 guides — https://adlibrary.com/guides/facebook-ad-library-api ; https://admanage.ai/blog/facebook-ads-library-api
- LinkedIn crackdown 2026 — https://linkedinsider.blog/linkedin-automation-crackdown-2026 ; https://nubela.co/blog/is-scraping-linkedin-legal-in-2026/
- LinkedIn Ad Library 2026 — https://adlibrary.com/guides/linkedin-ad-library-guide ; https://spideraf.com/articles/linkedin-ads-library-legally-spy-on-competitors-top-linkedin-ads
- TikTok CC / CCL 2026 — https://novoads.ai/en/blog/tiktok-creative-center ; https://adlibrary.com/guides/tiktok-ad-library-api ; https://www.auditsocials.com/blog/tiktok-eu-digital-services-act-ad-transparency-compliance-2026
- Google Trends API status 2026 — https://scrapebadger.com/blog/does-google-trends-have-an-api-what-to-use-in-2026
- Bluesky API pricing 2026 — https://www.blotato.com/blog/bluesky-api-pricing
- YouTube quota 2026 — https://www.getphyllo.com/post/youtube-api-limits-how-to-calculate-api-usage-cost-and-fix-exceeded-api-quota ; https://www.socialcrawl.dev/blog/youtube-data-api-2026
- Brave free-tier removal (Feb 2026) — https://www.implicator.ai/brave-drops-free-search-api-tier-puts-all-developers-on-metered-billing/
- AI newsletters 2026 — https://dupple.com/learn/best-ai-newsletters-2026 ; https://www.demandsage.com/ai-newsletters/

Secondary, pre-2026 (historical events):
- Reddit Pro Trends launch — https://techcrunch.com/2025/01/07/reddit-intros-new-trends-tools-for-businesses-and-an-ama-ad-format/ (2025-01-07); Reddit Pro suite launch — https://techcrunch.com/2024/03/08/reddit-launches-a-suite-of-free-growth-tools-for-businesses/amp (2024-03-08)
- TikTok hashtag-search removal — https://www.socialmediatoday.com/news/tiktok-implements-restrictions-hashtag-search-creative-center/703956/ (2024); https://searchengineland.com/tiktok-restrictions-hashtags-creative-center-436421 (2024)
- Product Hunt API redactions — https://norahsakal.com/blog/product-hunt-api-changes/ (2023)
