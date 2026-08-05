# B2 — Per-Source Extraction Methods & Collection Mechanics

Research brief T6 · Wave 1 · Design phase · Written 2026-08-06
Scope: Block B items 3–4 of the assignment — the per-source extraction METHOD matrix for the List A universe, robots/ToS factual surface, do-not-scrape list, fallback ladders, unattended collection mechanics, raw-artifact storage, freshness reality, and the licensed-data escape hatch.
Boundary: B1 owns source roles/value/priority. Legal interpretation (ToS meaning, GDPR consequences) is owned by parallel brief C7 — everywhere it matters this brief records the factual surface and marks the working assumption as "ASSUMED INPUT (from C7)".
Locked inputs honored: D-08 (X reads skipped in v1), hard rule "no login-walled scraping ever", operator holds Meta business accounts + a LinkedIn company page, Windows-first now / Linux cron later (D-05).

---

## 1. What this means for the operator

The honest picture in mid-2026: the open web where a script could quietly read Reddit, Twitter, or TikTok is gone. Reddit switched off its last anonymous door in May 2026 and is actively suing companies that scrape it. X (Twitter) killed its free tier and now charges per request. TikTok, LinkedIn, and Instagram detect and block automated browsers almost instantly, and LinkedIn just litigated a $10M/year scraping company out of existence. Trying to sneak past these defenses with a headless browser is not a plan — it is a way to get accounts banned, IP ranges burned, and legal letters.

The good news: you do not need any of that to get strong daily research signal. A surprising amount of the AI/dev/startup conversation is fully, officially open — Hacker News, Product Hunt, Hugging Face, tech press RSS feeds, YouTube's official API, and (if adopted) Bluesky's free public firehose. Google search demand is buyable for fractions of a cent per query from legitimate data vendors. Competitor ads are visible through Meta's own Ad Library, which under EU law now shows every ad delivered in the EU — and you operate in the EU. Reddit — the best source of raw customer pain — is the one gap on day 1: the plan is to run without it first (the pain axis is the slowest-moving signal, so this hurts less than it sounds), while pursuing the legitimate paths (Reddit's free Reddit Pro trends tool you use by hand, a commercial API application, or a licensed reseller).

Practically: the system reads official APIs and feeds on a schedule, stores exactly where every topic came from so you can check it at review time, backs off politely when a source pushes back, skips a broken source instead of crashing the run, and never does anything twice if the scheduler fires twice. A short list of surfaces is marked "never scrape, ever" — those come to you only through official tools or through your own eyes and a paste-in form.

---

## 2. Body

### 2.1 The 2026 anti-bot reality (grounding for F-9)

The F-9 pessimism flag is confirmed by current evidence, and the design should treat it as settled for v1:

- Major anti-bot vendors (Cloudflare, DataDome, Kasada, Akamai, HUMAN/PerimeterX) now combine TLS/JA4 handshake fingerprinting, low-level hardware/browser-environment verification, and behavioral ML (mouse/scroll/typing cadence). DataDome alone reportedly runs 85,000+ customer-specific ML models — every protected site is a distinct detection problem. Detection of stock Playwright/Puppeteer on protected surfaces is effectively immediate.
- A commercial "bypass" industry claims 98–99% success rates. Those numbers are real only inside an expensive, perpetually churning arms race (patched Chromium builds, residential proxy pools, CAPTCHA farm hand-offs). Buying a bypass does not change the ToS position — it usually worsens it (circumvention of technical measures is itself a named violation on Meta, TikTok, Reddit surfaces). Interpretation of circumvention-clause risk: ASSUMED INPUT (from C7); working assumption — circumvention products are out of bounds for this product.
- The legal temperature rose sharply in 2025–2026: Reddit sued Anthropic (June 2025), then Perplexity plus scraping vendors SerpApi, Oxylabs, and AWM Proxy (Oct 2025), and blocked the Internet Archive (Aug 2025). LinkedIn's suit drove Proxycurl (≈$10M ARR) to shut down and delete its data (Jan–Jul 2025). Cloudflare moves to blocking AI crawlers by default on ad-supported pages from Sept 15, 2026, with pay-per-crawl emerging.
- Counterweight to keep honest: Meta v. Bright Data (Jan 2024) — a federal court found Meta's terms did not bar logged-off scraping of public data by a non-user, and X v. Bright Data was dismissed (2024). Public-data scraping is not per se illegal in the US. But (a) this product's operator is EU-based, (b) the contractual/ToS exposure and platform retaliation (account bans — the operator's Meta business accounts and LinkedIn page are real assets at risk) remain, and (c) the technical blocking is decisive regardless of legality. Full legal reading: ASSUMED INPUT (from C7).

Consequence: Playwright/browser automation is justified in the v1 collection path essentially nowhere on List A. Every major surface is either officially accessible (use the API), officially closed and defended (do not scrape), or reachable through plain HTTP feeds where a browser adds nothing. The honest v1 architecture is: official APIs + RSS/Atom feeds + licensed data vendors + operator-supplied inputs, with browser automation reserved as a possible future, per-source, explicitly-approved exception (e.g., an open niche site with no feed and no anti-bot), never a default tool.

### 2.2 Per-source method matrix (List A universe)

Method vocabulary used below: OFFICIAL-API (documented API, keys self-serve or app-gated) · FEED (RSS/Atom/JSON feed over plain HTTP) · LICENSED-VENDOR (paid third party that lawfully licenses or lawfully collects the data) · AUTH-INTEGRATION (non-MCP integration using the operator's own authenticated platform accounts, within platform tooling) · MCP (existing MCP server wrapping one of the legitimate methods) · OPERATOR-INPUT (human browses official UI, pastes/exports findings into the run) · SKIP. "Browser automation" appears only to say why it is rejected.

| Source | v1 method | Anti-bot state (2026) | Why this method (under F-9) | Playwright verdict |
|---|---|---|---|---|
| Reddit | SKIP in month 1 → OPERATOR-INPUT (Reddit Pro Trends) immediately; pursue OFFICIAL-API commercial approval or LICENSED-VENDOR for month 2+ | Near-total: unauthenticated JSON deprecated 2026-05-28; Cloudflare-fronted; robots.txt closed; litigation-active | Free API tier is non-commercial only; commercial tier is manual approval 2–4 wks (~$0.24/1k calls). Public JSON path is both same-ToS and now technically dead. Reddit Pro is Reddit's own free business tool with a Trends tab — legitimate by construction | Rejected: technically blocked + ToS-prohibited + most litigation-active surface on the list |
| X (Twitter) | SKIP (D-08, locked) | Near-total; aggressive | Reads closed for v1 by decision. Note for the record: since 2026-02-06 X's default is pay-per-use ($0.005/read, 2M reads/mo cap, no free tier) — a cheap, legitimate re-entry path when D-08 is revisited | Rejected: ToS prohibits scraping without prior written consent; heavily defended |
| Hacker News | OFFICIAL-API (Firebase HN API + Algolia HN Search API), both free, no auth | Effectively none; robots.txt permissive with 30s crawl-delay | Genuinely open — the canonical F-9 exception. Two redundant official endpoints (live items + search/ranking) | Unnecessary: APIs cover everything a browser would see |
| Product Hunt | OFFICIAL-API (GraphQL v2; 6,250 complexity pts/15 min) — pending commercial-use clarification; FEED (public front-page RSS) as floor | Low-moderate on web pages; API is the sanctioned door | API free tier is read-only and non-commercial by default; commercial use = ask Product Hunt (their docs invite it). Whether internal research for a marketing agency counts as "commercial" here: ASSUMED INPUT (from C7); working assumption — send the permission email in week 1, use FEED until answered | Unnecessary/rejected: API + feed suffice |
| Hugging Face | OFFICIAL-API (Hub API; trending/sort endpoints; anonymous ≈500 API calls per 5-min window per IP, higher with free token) | None meaningful for the Hub API | Genuinely open; trending models/datasets/spaces is exactly the launch-hype signal wanted | Unnecessary |
| Tech press, vendor/model-lab blogs | FEED (RSS/Atom with conditional GET) for headlines/summaries/links; article-body fetch only where robots.txt and site posture allow | Rising on article bodies: Cloudflare default AI-crawler blocking from 2026-09-15; ~60% of reputable sites block AI agents in robots.txt | Feeds are the sanctioned syndication channel — polling them is what they are for. Store snippet+link, not full articles (copyright + blocking trend) | Rejected as default; a plain HTTP fetch honoring robots.txt is the only body-fetch method, per-domain allowlisted |
| Google Trends | OPERATOR-INPUT (UI + CSV export) at launch; LICENSED-VENDOR (DataForSEO Google Trends endpoint ≈$0.00225/task queued) for automation; apply to Google's official Trends API alpha (announced 2025-07-24, still gated in 2026) | High on the web UI; Google ToS bars automated access | No GA official API yet; pytrends-style scraping is ToS-adverse and brittle. Vendor route is cheap and stable; alpha application costs nothing | Rejected: ToS + fragility; vendor exists |
| SERP / search demand | LICENSED-VENDOR (DataForSEO ≈$0.60–2.00/1k queries; Serper; SerpApi ≈$15–25/1k) | High on Google SERP directly | Buying SERP data is a mature, low-cost market; scraping Google directly is ToS-adverse and pointless at our volume. Vendor-selection note: SerpApi is a named defendant in Reddit's Oct 2025 suit — character consideration for C7 | Rejected: vendor market solves it |
| Meta Ad Library | AUTH-INTEGRATION / OFFICIAL-API (Ad Library API with operator's verified Meta identity; under DSA every ad delivered to EU users is in the archive ~12 months with reach data) + OPERATOR-INPUT (web UI browsing for creative inspection) | High on the web UI (Meta perimeter); API is the sanctioned door | Operator already holds Meta business accounts; identity verification + dev app + 60-day tokens is the real friction. EU coverage fits a Czech operator's competitive set precisely. Creative files themselves often need UI viewing — that stays human | Rejected: Meta ToS bars automated collection without written permission; circumvention clause; operator's business assets at ban risk |
| TikTok Creative Center | OPERATOR-INPUT only (human browses trend/hashtag/creative surfaces; structured paste-in). Research API is academic-only; Commercial Content API is transparency-scoped and app-gated | Near-total: signed app-style requests, device fingerprinting, behavioral checks; Apr 2026 ToS update explicitly reinforces the scraping ban | No sanctioned programmatic door exists for our use; the defended surface + explicit prohibition makes this a do-not-scrape archetype | Rejected outright |
| YouTube | OFFICIAL-API (Data API v3; free; 10,000 units/day; search = 100 units/call) | N/A via API | Official, free, adequate: ~100 searches/day or thousands of cheap video/channel reads. Constraint that shapes storage: API data must be refreshed or deleted within 30 days (see 2.7) | Unnecessary |
| LinkedIn public | OPERATOR-INPUT only (operator reads feed/competitor pages; paste-in). Company-page analytics via operator's page tools if ever needed | Near-total + most aggressive legal posture (Proxycurl outcome) | No read API for public feed content; User Agreement bars scraping and even unauthorized crawling tools; operator's company page is an asset at risk | Rejected outright — hard |
| Instagram public patterns (P2) | AUTH-INTEGRATION (IG Graph API Hashtag Search via operator's business account: ~30 unique hashtags per 7-day window) + OPERATOR-INPUT | Near-total on web surfaces | Only sanctioned door is the Graph API through owned business assets; narrow but real for format-trend spot checks | Rejected outright (Meta perimeter) |
| Podcasts / transcripts (P2) | OFFICIAL-API (Podcast Index API — free key; iTunes Search API) + FEED (episode RSS, incl. transcript tags where present) | None meaningful | Podcast distribution is RSS-native; fully open by design | Unnecessary |
| Review sites (G2-style) (P2) | OPERATOR-INPUT; G2 paid seller/data products if a theme ever justifies cost | High (G2 is bot-defended; data is its product) | Reviews are the vendor's licensed asset; no free sanctioned door | Rejected |
| Bluesky (method-level observation for B1) | OFFICIAL-API (AT Protocol; public Jetstream WebSocket — no auth; ~5,000 rate-limit points/hr authenticated; no app review, no fee) | None — openness is the platform's design | With X reads closed (D-08), Bluesky is the one real-time public-discourse surface that is fully open in 2026; AI/dev discourse presence is meaningful. Whether it earns a role/priority is B1's call; method-wise it is free and trivial | Unnecessary |
| MCP tools (cross-cutting) | MCP wrappers are acceptable only when they front one of the legitimate methods above (e.g., an HN or search-API MCP server). An MCP server that internally scrapes a closed surface inherits the full ToS/technical problem — the transport does not launder the method | — | Evaluate MCP servers by what they call, not what they are | — |

### 2.3 Robots/ToS factual surface per source

Facts only; operative-clause pointers. All interpretation: ASSUMED INPUT (from C7).

- Reddit — Developer Terms + "Developer Platform & Accessing Reddit Data" (support.reddithelp.com): free Data API is non-commercial; commercial use requires express written approval; no selling/licensing Reddit data onward; deleted content must be honored. Unauthenticated JSON endpoints deprecated as of 2026-05-28. reddit.com/robots.txt is itself served behind blocking (our fetcher was refused); Reddit's public posture since mid-2024 is disallow-by-default for unapproved agents. Litigation record as in 2.1.
- X — Terms of Service: scraping "in any form, for any purpose" without prior written consent expressly prohibited; Developer Agreement governs API use; as of 2026-02-06 access is pay-per-use or Enterprise.
- Hacker News — news.ycombinator.com/robots.txt (retrieved 2026-08-06, verbatim character): applies to all agents, sets a 30-second crawl-delay, and disallows only interaction/auth endpoints — "/collapse?", "/context?", "/fave?", "/flag?", "/hide?", "/login", "/logout", "/r?", "/reply?", "/submitlink?", "/vote?", "/x?". Read surfaces are allowed. Official API published by YC on GitHub with no key requirement.
- Product Hunt — API docs + producthunt.com/legal: free API tier read-only and non-commercial by default; commercial use invited via contact address; attribution requested; GraphQL quota 6,250 complexity points/15 min; 429 on exhaustion with reset headers.
- Hugging Face — Hub docs publish explicit anonymous/authenticated rate limits (anonymous ≈500 API calls per 5-min window per IP); Hub content licensing varies per repo (relevant only if redistributing).
- Tech press / blogs — per-domain robots.txt governs body fetches; feeds are offered for syndication. Sector fact: AI-agent blocking in robots.txt on reputable sites rose from ~23% (Sept 2023) to ~60% (May 2025); Cloudflare default-blocks AI crawlers on ad-supported pages from 2026-09-15.
- Google (Trends + SERP) — Google ToS bar automated access/queries to its services without permission; Trends has a UI CSV export and an application-gated official API alpha; SERP data is available only via third-party vendors, whose own lawful-basis characterization differs per vendor (C7 input).
- Meta (Ad Library, Facebook, Instagram) — Meta ToS: "You may not access or collect data from our Products using automated means (without our prior permission)…"; separate Automated Data Collection Terms define scraping broadly and ban circumvention of technical measures. The Ad Library API is Meta's sanctioned door (identity verification + developer app + expiring tokens); DSA obliges an archive of all EU-delivered ads (~12 months, with reach). Counter-fact for C7: Meta v. Bright Data (N.D. Cal., Jan 2024) rejected Meta's contract claim over logged-off public scraping.
- TikTok — ToS prohibit automated collection ("automated scripts to collect information"); April 2026 update reinforces that Creative Center harvesting violates API/CCL terms where applicable; Research API restricted to vetted academics; Commercial Content API is transparency-scoped, application-gated.
- YouTube — API Services ToS + Developer Policies: Non-Authorized Data storable max 30 calendar days, then refresh or delete; stored data must be kept consistent with live API values; user-deletion requests honored within 7 days. Scraping the site instead of the API violates the same ToS.
- LinkedIn — User Agreement "Dos and Don'ts": no software/devices/scripts/robots "to scrape the Services", no copying profiles/data via automated means, no bypassing security features. Enforcement record: Proxycurl suit (Jan 2025) → shutdown + mandated data deletion (2025).
- Bluesky — AT Protocol is public-by-design; public Jetstream endpoints require no auth; developer guidelines impose rate limits, not access gating.
- Podcast Index / iTunes Search — open APIs with published free terms; podcast RSS is a syndication format by intent.
- G2 — ToS reserve review data as licensed property; access products are paid; site is bot-defended.

### 2.4 Do-not-scrape list (explicit, v1-binding)

Never targeted by any automated fetcher, headless browser, or "bypass" service, in any mode, including degraded modes:

1. Reddit (any surface: HTML, JSON endpoints, old.reddit, mirrors) — closed, defended, litigation-active.
2. X / Twitter (any surface, incl. nitter-style mirrors) — ToS-prohibited; D-08 skips it anyway.
3. LinkedIn (any surface, logged-in or public) — hard rule; operator's company page must never be the automation identity.
4. Instagram + Facebook web surfaces (incl. Ad Library web UI) — Meta automated-collection ban; operator's business accounts at risk; only the Graph/Ad Library APIs and human eyes.
5. TikTok (site, app endpoints, Creative Center) — explicit ToS ban + strongest technical defense on the list.
6. Google web surfaces (SERP pages, Trends UI) — ToS-adverse; vendor market exists.
7. G2 and equivalent review platforms — data is their licensed product.
8. Any login wall, anywhere (locked hard rule — no login-walled scraping EVER, including "operator lends cookies" schemes).
9. Any surface serving a CAPTCHA/anti-bot challenge — a challenge is a "no"; the system logs and skips, never solves.
10. Paywalled press bodies; any site whose robots.txt disallows our fetch path (feeds excepted where the feed itself is offered).

Standing rule: absence from this list is not permission — new sources enter the matrix through the method-evaluation gate (2.2), not by default scraping.

### 2.5 Fallback ladders per source

Ladder grammar: primary → degraded → operator-supplied → skip-with-log. Every rung is legitimate; rungs never fall through to scraping. "Skip-with-log" always records: source, rung attempted, error class, timestamp, and impact note for the review package.

| Source | Primary | Degraded | Operator-supplied | Skip-with-log trigger |
|---|---|---|---|---|
| Reddit | (month 2+) commercial Data API or licensed vendor | Reddit Pro Trends observations entered via structured paste-in | Screenshots/notes of specific threads the operator judges relevant | No approval/budget yet → run proceeds Reddit-less; pack notes "pain axis degraded" |
| Hacker News | Algolia HN Search (ranked/filtered) | Firebase HN API (top/new/best IDs + item fetch) | Operator pastes a thread URL to force-include | Both endpoints failing (rare) |
| Product Hunt | GraphQL v2 API within complexity budget | Public front-page RSS feed | Operator pastes launch URLs | 429-storm or token failure after backoff |
| Hugging Face | Hub API trending (authenticated, free token) | Anonymous Hub API within 5-min window quotas | Operator notes a model launch by hand | Persistent 429/5xx |
| Tech press / blogs | Conditional-GET feed polling of the per-theme feed roster | Feed-metadata-only mode (skip body fetches entirely) | Operator pastes an article URL + why it matters | Feed 404/410 (mark roster entry stale), repeated timeouts |
| Google Trends | DataForSEO Trends endpoint (once budget approved) | Official alpha API if/when admitted | Operator exports CSV from Trends UI on a weekly rhythm | No vendor budget and no CSV this window → demand axis marked stale |
| SERP demand | Chosen SERP vendor (DataForSEO-class) | Second vendor as configured spare | Operator pastes observed SERP notes for priority keywords | Vendor outage/credit exhaustion |
| Meta Ad Library | Ad Library API (EU-wide ads, operator identity) | — (no honest degraded automation) | Operator browses Ad Library UI, saves ad links + creative notes | Token expiry (60-day) not renewed; identity re-verification pending |
| TikTok Creative Center | — (no automated primary exists) | — | Operator browses Creative Center; structured trend/format paste-in | Operator skipped this window → format axis marked stale |
| YouTube | Data API v3 within a per-run unit budget (search calls capped; prefer cheap list reads) | Channel-uploads playlist reads + published channel RSS feeds (1-unit-class reads instead of 100-unit searches) | Operator pastes video URLs | Daily quota exhausted (log units spent; resume next window) |
| LinkedIn public | — | — | Operator observation form (what B2B framing is circulating) | Operator skipped |
| Instagram patterns | IG Graph API hashtag search within the ~30-hashtags/7-day window | — | Operator browsing notes | Window exhausted or token issue |
| Podcasts | Podcast Index API + episode RSS | iTunes Search API | Operator pastes episode links/quotes | API + feed both failing |
| Bluesky (if adopted) | Jetstream filtered consumption during collection window | App-view public API queries (search/feeds) | Operator pastes post URLs | Stream connect failures after backoff |
| Review sites | — | — | Operator excerpts (with URL) when category-relevant | Not gathered this window |

Cross-cutting rung rule: a source that fails its ladder twice in a row raises a source-health flag in the next review package; three consecutive failures open a maintenance task rather than silently degrading forever.

### 2.6 Collection mechanics for unattended runs

Design obligations (behavioral, not implementation syntax):

Rate limits and backoff.
- Every source carries a declared budget per run (calls, quota units, vendor credits, wall-clock) sized well under published limits — e.g., YouTube search calls are 100 units each against 10,000/day shared by all runs; Product Hunt complexity points regenerate per 15 minutes; Hugging Face anonymous windows are per-IP per 5 minutes.
- On 429/quota signals: honor Retry-After when present; otherwise exponential backoff with jitter, bounded retries, then ladder-descent (2.5) — never tighten the loop.
- Per-source circuit breaker: after N consecutive failures the source is closed for the rest of the run and skip-logged; a global wall-clock ceiling ends collection gracefully so ranking/packaging always runs on whatever was gathered.
- Politeness floor for the few plain-HTTP fetches: honor robots.txt (incl. crawl-delay, e.g., HN's 30s), identify with a stable, truthful user-agent string and contact URI, never parallel-hammer a single host.

Caching.
- Feed polling uses HTTP conditional requests (ETag / If-Modified-Since) — most polls should cost a 304, not a body.
- API responses cached keyed by canonicalized request (endpoint + normalized params), with TTLs matched to signal freshness class (2.8) — a Trends series fetched this morning is not re-bought this afternoon.
- Vendor credits are treated like money: cache-before-call is mandatory on paid endpoints.

Deduplication.
- Identity dedupe: every collected item gets a canonical key — platform-native ID where one exists (HN item ID, PH post ID, YouTube video ID, HF repo ID, Bluesky URI), else canonicalized URL (scheme/host lowered, tracking parameters stripped, fragments dropped).
- Near-dup dedupe: content fingerprint (normalized-text hash) catches the same story syndicated across feeds.
- Cross-run dedupe ledger: keys persist for a rolling window (default 14 days, per-source overridable) so daily runs don't resurface Tuesday's topic on Wednesday; a re-seen item may still update engagement metrics on the existing record ("seen again, hotter now" is signal, not duplication).

Idempotent re-runs (same cron fires twice).
- A run is identified by its logical collection window (theme + date-bucket), not by wall-clock start. A second firing inside the same window must detect the existing run record and either resume incomplete stages or no-op with a clear exit status — never produce a second, competing review package.
- A single-holder lease guards the window; a crashed run leaves a resumable manifest (per-source progress cursors), so restart means continue, not repeat.
- All collection writes are append-only records under natural keys, so replaying a stage cannot double-insert.

Pagination stability.
- Prefer cursor/token pagination (PH GraphQL cursors, YouTube page tokens) over offset pagination; ranked lists reorder under offset paging and cause both gaps and dupes.
- Snapshot-then-detail: list endpoints are read first into a fixed snapshot for the run; detail fetches work off the snapshot, so mid-run reordering can't skew coverage.
- Bounded depth: every paginated read has a max-pages cap; cursor expiry mid-walk is an expected event (resume from manifest or accept partial with log), not an error.

Poison-pill inputs.
- Structural: per-item size caps, fetch timeouts, content-type validation, encoding sanity checks; malformed items are quarantined with their raw bytes for inspection, and the run continues — one bad item never kills a source, one bad source never kills a run.
- Semantic (specific to this product): all collected text is untrusted input that will later sit inside LLM ranking/spin prompts. Prompt-injection via a crafted post title or feed entry is a live hazard. Collected content must be carried as quoted data with provenance tags, never treated as instructions; ranking-stage prompts must be built on the assumption that item text is adversarial. Items that trip injection heuristics get flagged for human review rather than silently ranked.
- Repeat offenders (a feed that serves garbage daily) accumulate a poison score that feeds the source-health flag in review packages.

### 2.7 Raw-artifact storage for auditability

Why store anything raw: at review time the operator must be able to answer "where did this topic come from, and did we collect it legitimately?" without trusting the pipeline's summary. That means every topic candidate carries provenance a human can click and check — and, if a source ever disputes our access, the request log is the defense exhibit.

What to store, per item class:

| Artifact | Store? | Content | Why |
|---|---|---|---|
| Request log | Always | Source, endpoint/feed, normalized params, timestamp, HTTP status, quota/credits spent, method rung used | Audit trail of how collection behaved; proves politeness and budget compliance |
| Raw payload | APIs/feeds: yes, briefly | The response body as received | Debugging, re-extraction, dispute evidence |
| Normalized signal record | Always | Canonical key, title/text excerpt, metrics, author handle (minimized), language, retrieval time | The working substance of ranking |
| Provenance snapshot (in review package) | Always, permanent with the pack | Canonical link + the minimal quoted excerpt that triggered candidacy + retrieval time + method | Reviewer-facing "click to verify"; survives raw-payload expiry |
| Full article bodies / media files | No (links + excerpts only) | — | Copyright posture of press; Ad Library creatives and TikTok material stay on-platform, referenced by link |

Retention windows (working defaults; GDPR consequence — lawful basis, minimization, author-handle treatment, deletion-request handling — is ASSUMED INPUT (from C7); working assumption: handles are personal data → minimize, pseudonymize in analytics, purge raw on schedule):

- Raw payloads: 30 days default, then delete (aligning with the strictest per-source rule, YouTube's 30-day refresh-or-delete obligation, which is adopted as the global default rather than special-cased). Sources with stricter contractual terms (a future Reddit agreement's deletion-sync duty) override downward.
- Normalized signal records: 90 days — long enough to compute freshness/velocity across runs and do post-hoc "which sources produced winners" analysis.
- Request logs: 12 months — compliance memory, small.
- Provenance snapshots inside review packages: retained with the pack (the pack is the business record); they carry links + short excerpts, not payloads, precisely so pack retention doesn't fight source-data retention rules.
- YouTube-specific: stored metrics carry their retrieval date and are refreshed or purged at 30 days; deletion of a video upstream must propagate on next refresh.
- Reddit-specific (future): any licensed feed will contractually require honoring content deletions — the storage layer must support targeted deletion by canonical key from day one (cheap now, painful to retrofit).

### 2.8 Freshness reality — day 1 without Reddit, and staleness budgets

Day-1 research axis (Reddit blocked until month 2, X skipped indefinitely): the launch-hype and search-demand axes are fully served from open doors; real-time discourse is served adequately if Bluesky is adopted (B1 call), else thinly via HN comment velocity; the ICP-pain axis is the genuine gap — served in month 1 by HN comment threads (Ask HN and complaint threads are concentrated pain), operator-supplied Reddit Pro observations, review-site excerpts, and the operator's own sales-conversation notes as a first-class OPERATOR-INPUT source. This is a degraded-but-honest posture, and it should be labeled as such in every month-1 review package ("pain axis: operator-fed").

Staleness budgets — how old each signal type can be before its tie-in value dies:

| Signal type | Fresh | Usable | Dead | Consequence for cadence |
|---|---|---|---|---|
| Launch hype (PH/HF/vendor announcements) | 0–48h | to ~7 days | >1–2 weeks (riding it late reads as slow) | Daily collection; same-day-to-next-day content |
| Viral discourse (HN front page, Bluesky threads) | 0–24h | 24–72h | >1 week | Daily; the axis X/Reddit absence hurts most on velocity |
| Short-form format trends (TikTok CC, IG patterns) | days | 1–4 weeks | >4–6 weeks | Weekly operator browse is sufficient; formats decay slower than memes |
| Ad creative patterns (Meta Ad Library) | 1–2 weeks | 2–8 weeks (long-running ads are proven ads) | >1 quarter | Weekly-to-biweekly API pulls; age of a still-running ad is positive signal |
| Search demand (Trends/SERP) | this week | weeks–months (trend direction matters more than the day) | >1 quarter for tactical use | Weekly vendor pulls or operator CSV |
| ICP pain / evergreen complaints (Reddit-class) | — | months; a 6-month-old pain thread still fuels evergreen content | ~12+ months (product landscape shifts) | THE key insight: the axis Reddit serves is the slowest-decaying signal — losing it for month 1 costs breadth of pain evidence, not timeliness. Backfilling pain history in month 2 (once a legitimate Reddit path opens) recovers most of the value |

Net: being Reddit-less on day 1 does not block launch. It blocks claiming "we saw this pain across 40 threads" — month-1 packs lean on hype + demand + operator-fed pain, and say so.

### 2.9 Aggregator / licensed-data landscape (the F-1/F-9 escape hatch)

Real options for legally consuming Reddit/X/social signals, with pricing ballpark and terms character:

| Option | Covers | Ballpark cost | Terms character | Fit |
|---|---|---|---|---|
| Reddit commercial Data API (direct) | Reddit, first-party | ~$0.24/1k calls after written approval; approval 2–4 wks, not guaranteed | Restrictive: no resale, deletion-sync, use-case-bound | Best long-term Reddit path for a small operator; apply in week 1 |
| SocialGist | Reddit (official data partner), other boards/blogs | Enterprise, quote-only | Licensed firehose with compliance guardrails; built for resellers/listening platforms | Likely oversized for one operator; the fallback if direct approval fails and budget allows |
| Brandwatch / Talkwalker / Meltwater class | Reddit (via partner) + broad social | ≈$800–3,000+/mo | Enterprise listening suites; data stays in their tooling — closer to OPERATOR-INPUT than an API feed | Only if the agency wants a listening suite anyway; then its exports become operator-supplied input |
| Reddit Pro (Trends tab) | Reddit first-party trends, ~100k tracked phrases, community/conversation views | Free | Reddit's own business tool; UI-only, no export API | The month-1 answer; human-in-the-loop by design |
| X pay-per-use API (direct) | X, first-party | $0.005/read (2M reads/mo cap); no free tier since 2026-02-06 | First-party, metered; e.g., 10k post-reads ≈ $50/mo | The clean re-entry path when D-08 is revisited — cheap at research volumes |
| twitterapi.io-class gray-market gateways | X, scraped/unofficial | ≈$0.15/1k tweets | Not licensed by X; gateway absorbs technical risk, not the customer's ToS/compliance posture | Flag to C7; working assumption — excluded (conflicts with the project's legitimate-access principle) |
| DataForSEO / Serper / SerpApi | Google SERP + Trends | SERP $0.30–2.00/1k; Trends ≈$0.00225/task (queued) | Data-vendor ToS; lawful-basis characterization varies; SerpApi is a Reddit-suit defendant (character datum) | Primary automation path for the demand axis; prefer the vendor with the cleanest posture per C7 |
| Exploding Topics / Glimpse | Curated trend discovery over search data | $39–197/mo; Glimpse from ~$99/mo (10 free searches) | SaaS subscriptions, UI-first with limited export | Optional operator tooling; outputs enter as operator-supplied input |
| BuzzSumo-class content-trend tools | Cross-web content engagement | ≈$199+/mo | SaaS; API on higher tiers | Optional, later |
| Bluesky (direct) | Bluesky, first-party | Free (public firehose/Jetstream) | Open by protocol design | The only free, unrestricted real-time social feed in 2026 |

Character summary: for every signal List A wants, at least one legitimate paid or free door exists in 2026. The total worst-case monthly bill for the full automation posture (SERP/Trends vendor + Reddit commercial API + optional X pay-per-use) sits in the low hundreds of dollars — an order of magnitude below one enterprise listening seat, and infinitely below the cost of a burned Meta business account.

---

## 3. Decision table

| # | Decision | Status | Flows to |
|---|---|---|---|
| U1 | v1 method per source is fixed as per matrix 2.2 (APIs/feeds/vendors/operator-input; no Playwright in the v1 collection path) | UNBLOCKED | Collection architecture; theme-config "extraction method" vocabulary |
| U2 | Do-not-scrape list 2.4 is binding for all modes, incl. degraded and cron | UNBLOCKED | Safety/mode design; fail-closed rules |
| U3 | Fallback ladders 2.5 (primary → degraded → operator-supplied → skip-with-log) are the per-source failure model | UNBLOCKED | Runtime orchestration; review-package "source health" section |
| U4 | Unattended mechanics 2.6: window-keyed idempotent runs, leases, append-only writes, dedupe ledger (14-day default), snapshot-then-detail pagination, per-source circuit breakers, injection-hardened handling of collected text | UNBLOCKED | Cron/scheduler architecture; storage design |
| U5 | Storage/retention 2.7: raw 30d / normalized 90d / request-log 12mo / provenance snapshots permanent with pack; targeted-deletion capability from day one; YouTube 30-day rule adopted as global raw default | UNBLOCKED (retention numbers adjustable by C7) | Storage architecture; review-package contents |
| U6 | Day-1 posture 2.8: launch Reddit-less with pain axis operator-fed and labeled; Reddit Pro browsing rhythm from week 1 | UNBLOCKED | Phase-1 roadmap; operator workflow |
| U7 | Demand axis via licensed SERP/Trends vendor, not scraping; Google Trends alpha application submitted regardless | UNBLOCKED (vendor choice deferred, D3) | Provider integration area |
| D1 | Does "internal marketing research by an agency" count as commercial use under Reddit/Product Hunt/vendor ToS? | DEFERRED → C7 | Determines whether PH free tier suffices and shapes the Reddit application |
| D2 | Reddit month-2 path: direct commercial API vs SocialGist vs stay operator-fed | DEFERRED → C7 (terms) + operator (budget) + Reddit's approval outcome | Research-axis completeness |
| D3 | SERP/Trends vendor selection (incl. whether SerpApi's litigation posture disqualifies it) | DEFERRED → C7 character read + cost check | Provider integration |
| D4 | Adopt Bluesky as a discourse source, and at what priority | DEFERRED → B1 (role/priority is B1's domain; method is trivially available) | Source roster |
| D5 | Revisit D-08 (X reads) once pay-per-use economics are accepted | DEFERRED → operator decision, month 2+ | Source roster; budget |
| D6 | Gray-market gateways (twitterapi.io-class): confirm exclusion | DEFERRED → C7 (working assumption: excluded) | Compliance posture |
| D7 | Retention-window and author-handle (personal-data) final values | DEFERRED → C7 | Storage architecture |
| D8 | Meta Ad Library API onboarding (identity verification, app review, 60-day token renewal as an operational duty) | DEFERRED → operator action item, week 1–2 | Ads-signal availability |

---

## 4. Fact ledger

All retrieved 2026-08-06. Confidence: H = multiple/official corroboration; M = single credible source or fast-moving; L = directional.

| Claim | Source URL | Retrieved | Conf. | Recheck by |
|---|---|---|---|---|
| Reddit commercial API: written approval required, manual review typically 2–4 weeks, not guaranteed | https://www.redditapis.com/blogs/reddit-data-api-2026 | 2026-08-06 | M | 2026-11-01 |
| Reddit commercial pricing ≈$0.24/1k calls; free tier non-commercial only | https://prowlo.com/blog/reddit-api-pricing | 2026-08-06 | M | 2026-11-01 |
| Reddit Developer Platform terms: no commercialization of Reddit data without express written approval | https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data | 2026-08-06 | H | 2027-02-01 |
| Reddit deprecated unauthenticated JSON endpoints, announced 2026-05-28 | https://crawlora.net/blog/reddit-json-api-blocked-2026 | 2026-08-06 | M | 2026-10-01 |
| Reddit sued Anthropic (Jun 2025); sued Perplexity + SerpApi + Oxylabs + AWM Proxy (Oct 2025); blocked Wayback Machine (Aug 2025) | https://crawlora.net/blog/reddit-json-api-blocked-2026 | 2026-08-06 | H | 2027-02-01 |
| SocialGist is Reddit's official data partner for listening-platform licensing | https://www.thesilab.com/resource/the-truth-about-social-data-access | 2026-08-06 | H | 2027-02-01 |
| Reddit Pro is free for businesses; Trends tab (launched Jan 2025) tracks ~100k smart keywords with conversation volume, communities, threads | https://techcrunch.com/2025/01/07/reddit-intros-new-trends-tools-for-businesses-and-an-ama-ad-format/ | 2026-08-06 | H | 2027-02-01 |
| X API: pay-per-use default since 2026-02-06 — $0.005/read (2M reads/mo cap), $0.015/post created, no free tier; Basic/Pro closed to new signups; Enterprise ≈$42k/mo | https://www.netrows.com/blog/x-twitter-api-pricing-tiers-2026 | 2026-08-06 | H | 2026-11-01 |
| X ToS expressly prohibits scraping without prior written consent | https://twitterapi.io/blog/understanding-twitter-official-api-guide | 2026-08-06 | H | 2027-02-01 |
| twitterapi.io: unofficial X gateway ≈$0.15/1k tweets; no X developer account needed; compliance posture rests on gateway, not customer | https://twitterapi.io/acceptable-use | 2026-08-06 | M | 2026-12-01 |
| HN robots.txt: all agents allowed on read surfaces, 30s crawl-delay, interaction endpoints disallowed (verbatim capture) | https://news.ycombinator.com/robots.txt | 2026-08-06 | H | 2027-02-01 |
| Product Hunt GraphQL v2 quota: 6,250 complexity points/15 min; 429 + reset headers on exhaustion | https://api.producthunt.com/v2/docs/rate_limits/headers | 2026-08-06 | H | 2027-02-01 |
| Product Hunt free API tier is read-only, non-commercial by default; commercial use via contact address | https://api.producthunt.com/v2/docs | 2026-08-06 | H | 2027-02-01 |
| Hugging Face Hub anonymous limits ≈500 API calls / 3,000 resolvers per 5-min window per IP; token raises limits | https://huggingface.co/docs/hub/main/en/rate-limits | 2026-08-06 | H | 2027-02-01 |
| Google Trends official API announced 2025-07-24; still application-gated alpha, not GA, in 2026 | https://developers.google.com/search/blog/2025/07/trends-api ; https://scrapebadger.com/blog/does-google-trends-have-an-api-what-to-use-in-2026 | 2026-08-06 | H | 2026-11-01 |
| DataForSEO Google Trends: ≈$0.00225/task queued, $0.009/task live; SERP market ≈$0.30–25/1k, DataForSEO SERP ≈$0.60–2.00/1k, SerpApi ≈$15–25/1k | https://www.socialcrawl.dev/blog/best-google-trends-apis-2026 ; https://cloro.dev/blog/best_serp_apis/ | 2026-08-06 | M | 2026-11-01 |
| Meta Ad Library API: free with identity verification + developer app; 60-day tokens; DSA puts all EU-delivered ads in archive ~12 months with reach data | https://adlibrary.com/posts/meta-ad-library-api-limitations ; https://adlibrary.com/posts/eu-dsa-ad-repositories-developers | 2026-08-06 | M | 2026-11-01 |
| Meta ToS bars automated collection without prior permission; Automated Data Collection Terms ban circumvention of technical measures | https://www.facebook.com/legal/automated_data_collection_terms | 2026-08-06 | H | 2027-02-01 |
| Meta v. Bright Data (Jan 2024): court rejected Meta's contract claim over logged-off public scraping | https://www.fbm.com/publications/major-decision-affects-law-of-scraping-and-online-data-collection-meta-platforms-v-bright-data/ | 2026-08-06 | H | stable |
| TikTok ToS prohibits automated Creative Center harvesting; April 2026 rules reinforce; defense = signed requests, device fingerprinting, behavioral checks; Research API academic-only | https://scrapebadger.com/blog/tiktok-scraping-apis-in-2026-the-complete-deep-guide ; https://dataimpulse.com/blog/how-to-scrape-tiktok/ | 2026-08-06 | M | 2026-11-01 |
| YouTube Data API v3: free, 10,000 units/project/day, search.list = 100 units | https://www.getphyllo.com/post/youtube-api-limits-how-to-calculate-api-usage-cost-and-fix-exceeded-api-quota | 2026-08-06 | H | 2027-02-01 |
| YouTube Developer Policies: stored API data must be refreshed or deleted within 30 calendar days; user-deletion honored within 7 days | https://developers.google.com/youtube/terms/developer-policies | 2026-08-06 | H | 2027-02-01 |
| LinkedIn sued Proxycurl (Jan 2025); Proxycurl (~$10M ARR) shut down Jul 2025 and must delete scraped data | https://www.startuphub.ai/ai-news/startup-news/2025/the-1-linkedin-scraping-startup-proxycurl-shuts-down ; https://www.socialmediatoday.com/news/linkedin-wins-legal-case-data-scrapers-proxycurl/756101/ | 2026-08-06 | H | stable |
| Anti-bot 2026: TLS/JA4 + hardware verification + behavioral ML standard; DataDome runs 85,000+ customer-specific models; bypass vendors claim 98–99% inside an arms race | https://github.com/techinz/browsers-benchmark ; https://scrapfly.io/blog/posts/how-to-bypass-datadome-anti-scraping ; https://nerdbot.com/2026/04/28/bypass-cloudflare-turnstile-in-2026-headless-browser-scaling-and-deep-dive-into-native-chromium-patching/ | 2026-08-06 | M | 2026-12-01 |
| AI-blocking in robots.txt on reputable sites rose ~23% (Sep 2023) → ~60% (May 2025); Cloudflare default-blocks AI crawlers on ad-supported pages from 2026-09-15 | https://technologychecker.io/blog/robots-txt-ai-crawlers-blocking-report ; https://crawlora.net/blog/reddit-json-api-blocked-2026 | 2026-08-06 | M | 2026-12-01 |
| Bluesky: no paid tier, no app review; public Jetstream WebSocket needs no auth; ~5,000 rate-limit points/hr | https://www.blotato.com/blog/bluesky-api-pricing ; https://docs.bsky.app/blog/jetstream | 2026-08-06 | H | 2026-12-01 |
| Brandwatch-class listening realistically $800–3,000+/mo; Reddit coverage via official partner | https://www.xpoz.ai/blog/comparisons/social-listening-tools-pricing-compared-2026/ | 2026-08-06 | M | 2026-12-01 |
| Exploding Topics $39–197/mo; Glimpse from ~$99/mo with 10 free searches/mo | https://meetglimpse.com/software-guides/exploding-topics-alternatives/ ; https://www.toolsurf.com/exploding-topics-pricing-2025-plans-features-and-is-it-worth-it-2026-plans-features-best-deals-compared/ | 2026-08-06 | M | 2026-12-01 |

Volatile-claim currency check: of the 20 volatile rows (excluding the two stable court outcomes and evergreen ToS locations), 14 rest on sources published or updated Feb 2026 or later (70%), satisfying the ≥60% requirement.

---

## 5. Sources

- https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data — Reddit official developer-data terms (retrieved 2026-08-06)
- https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy — Reddit Responsible Builder Policy (retrieved 2026-08-06)
- https://www.redditapis.com/blogs/reddit-data-api-2026 — Reddit Data API access state, 2026 (retrieved 2026-08-06)
- https://prowlo.com/blog/reddit-api-pricing — Reddit API pricing breakdown, 2026 (retrieved 2026-08-06)
- https://crawlora.net/blog/reddit-json-api-blocked-2026 — Reddit unauthenticated JSON deprecation, May 2026, + litigation timeline (retrieved 2026-08-06)
- https://techcrunch.com/2025/01/07/reddit-intros-new-trends-tools-for-businesses-and-an-ama-ad-format/ — Reddit Pro Trends launch, Jan 2025 (retrieved 2026-08-06)
- https://www.thesilab.com/resource/the-truth-about-social-data-access — SocialGist as Reddit's official data partner (retrieved 2026-08-06)
- https://www.netrows.com/blog/x-twitter-api-pricing-tiers-2026 — X API pay-per-use switch, Feb 2026 (retrieved 2026-08-06)
- https://twitterapi.io/acceptable-use ; https://twitterapi.io/blog/understanding-twitter-official-api-guide — gray-market gateway terms + X ToS scraping clause (retrieved 2026-08-06)
- https://news.ycombinator.com/robots.txt — HN robots.txt, verbatim (retrieved 2026-08-06)
- https://api.producthunt.com/v2/docs ; https://api.producthunt.com/v2/docs/rate_limits/headers — Product Hunt API terms and rate limits (retrieved 2026-08-06)
- https://huggingface.co/docs/hub/main/en/rate-limits — Hugging Face Hub rate limits (retrieved 2026-08-06)
- https://developers.google.com/search/blog/2025/07/trends-api — Google Trends API alpha announcement, 2025-07-24 (retrieved 2026-08-06)
- https://scrapebadger.com/blog/does-google-trends-have-an-api-what-to-use-in-2026 — Trends API gated-alpha status in 2026 (retrieved 2026-08-06)
- https://www.socialcrawl.dev/blog/best-google-trends-apis-2026 ; https://cloro.dev/blog/best_serp_apis/ ; https://www.proxies.sx/blog/cheapest-serp-api-comparison-2026 — SERP/Trends vendor pricing, 2026 (retrieved 2026-08-06)
- https://adlibrary.com/posts/meta-ad-library-api-limitations ; https://adlibrary.com/posts/eu-dsa-ad-repositories-developers — Meta Ad Library API + DSA repository facts, 2026 (retrieved 2026-08-06)
- https://www.facebook.com/legal/automated_data_collection_terms — Meta Automated Data Collection Terms (retrieved 2026-08-06)
- https://www.fbm.com/publications/major-decision-affects-law-of-scraping-and-online-data-collection-meta-platforms-v-bright-data/ — Meta v. Bright Data analysis, 2024 (retrieved 2026-08-06)
- https://scrapebadger.com/blog/tiktok-scraping-apis-in-2026-the-complete-deep-guide ; https://dataimpulse.com/blog/how-to-scrape-tiktok/ — TikTok defenses + April 2026 ToS update (retrieved 2026-08-06)
- https://www.getphyllo.com/post/youtube-api-limits-how-to-calculate-api-usage-cost-and-fix-exceeded-api-quota — YouTube quota mechanics, 2026 (retrieved 2026-08-06)
- https://developers.google.com/youtube/terms/developer-policies — YouTube Developer Policies, 30-day storage rule (retrieved 2026-08-06)
- https://www.startuphub.ai/ai-news/startup-news/2025/the-1-linkedin-scraping-startup-proxycurl-shuts-down ; https://www.socialmediatoday.com/news/linkedin-wins-legal-case-data-scrapers-proxycurl/756101/ — Proxycurl shutdown, 2025 (retrieved 2026-08-06)
- https://github.com/techinz/browsers-benchmark ; https://scrapfly.io/blog/posts/how-to-bypass-datadome-anti-scraping ; https://nerdbot.com/2026/04/28/bypass-cloudflare-turnstile-in-2026-headless-browser-scaling-and-deep-dive-into-native-chromium-patching/ — anti-bot state of the art, 2026 (retrieved 2026-08-06)
- https://technologychecker.io/blog/robots-txt-ai-crawlers-blocking-report — robots.txt AI-blocking adoption data (retrieved 2026-08-06)
- https://docs.bsky.app/blog/jetstream ; https://www.blotato.com/blog/bluesky-api-pricing — Bluesky firehose/Jetstream openness + 2026 pricing state (retrieved 2026-08-06)
- https://www.xpoz.ai/blog/comparisons/social-listening-tools-pricing-compared-2026/ — listening-suite pricing, 2026 (retrieved 2026-08-06)
- https://meetglimpse.com/software-guides/exploding-topics-alternatives/ ; https://www.toolsurf.com/exploding-topics-pricing-2025-plans-features-and-is-it-worth-it-2026-plans-features-best-deals-compared/ — trend-tool pricing (retrieved 2026-08-06)
