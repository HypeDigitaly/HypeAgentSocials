# 05 — Query steering: how each source is told what to look for

*Design annex · researched 2026-08-06 · four parallel readers (three web, one repo audit)*
*Answers the operator's question: how are trends actually searched on each platform, and can watch keywords be set in configuration and reach the wire?*

---

## 1. The defect this annex exists to close

**Short answer to the operator's question: partly yes, and the design does not currently make it work.**

The repo audit establishes the following, quote-backed:

- The phrase **"query-shaped collector"** occurs **exactly twice in the entire repository** — both times in §10, in the *Watch topics, keywords and entities* knob (*"the seed for every query-shaped collector"*) and in §10.1's minimum-viable decision list. **It is never defined, no criterion is given, and no source is ever tagged as query-shaped or not.** §2.3's roster table has columns for role, priority, connector class, cadence, method and failure mode — and **no column for what is sent to the source**. §2.8's collection flow begins at the per-source budget and goes straight to the failure ladder; there is no query-construction step anywhere.
- **There is no per-source query template, and no mapping from configured keywords to per-source query syntax.** The only steering that survives into the design is locale (`geo=CZ`, `hl=cs`).
- **There is no local topic filter.** §2.8's normalisation is stated exhaustively — canonical key → near-dup fingerprint → language stamp → quoted-data wrapper — and subject matter is absent from it.
- **The ranking brief assumes a filter that nobody owns.** B3 §2 and §3g both say *"collection is already scoped to configured watch topics… the taxonomy pre-filter upstream (**owned by B1/B2**) is the first line of defense"*. B1 and B2 contain no such filter. The first line of defence is **unowned**, so an unfiltered Google News feed, a Czech trade-press feed, a Bluesky trending list and a newsletter all arrive whole, and the first substantive relevance test is node N-1 — **an LLM call, per item**.
- **Watch topics are not per language.** §10.2 carries one flat *Watch topics, keywords and entities* row and a separate *Language array* row. There is no Czech surface form for a topic, no per-source phrasing, and no statement anywhere that a keyword useful on one source is useless on another.
- §13.2 readiness asserts every source has *"a method, a budget, a ladder and a source-family membership"* — **a query obligation is conspicuously absent**, so a theme whose keywords reach nothing still passes readiness.

**This is defect P-12**, and it belongs beside P-1…P-11 in `00_MASTERPLAN.md` §1: *the configured watch topics have no path to the wire on roughly half the roster, and no path to a filter on the other half.*

Its consequence is not subtle. Roughly half the automated core is feed-shaped. For those sources the operator's keywords currently do nothing at all, and every irrelevant item they return is paid for twice — once in ranking-stage tokens, once in the operator's attention.

---

## 2. Per-source query surface — the meticulous answer

Confidence is marked per row. **Live-verified** means a call was actually executed during research; **doc-verified** means read from primary documentation; **unverified** means the source could not be reached and the entry rests on prior public knowledge that must be re-checked.

### 2.1 Steerable — the source accepts our keywords

| Source | Query field | Also accepts | Engagement returned | Cost / limit | Confidence |
|---|---|---|---|---|---|
| **Hacker News (Algolia)** `hn.algolia.com/api/v1` | `query` | `tags` (`story`, `front_page`, `show_hn`, `ask_hn`, `author_*`), `numericFilters` (`points>100`, `created_at_i>…`), `/search` relevance vs `/search_by_date` chronological | `points`, `num_comments`, `created_at_i` | free, no key; **~100 hits per request** (asked for 1000, got 100 with `exhaustiveNbHits:false`); documented rate limit not published | **Live-verified** — a keyword + points-threshold + date-window query was executed and returned only stories 130–369 points after the cutoff |
| **Bluesky** `app.bsky.feed.searchPosts` | `q` (Lucene-ish, grammar explicitly unspecified) | `sort=top\|latest`, `since`/`until`, `lang`, `tag`, `author`, `mentions`, `domain`, `limit` 1–100, `cursor` | `likeCount` / `repostCount` / `replyCount` via `postView` | app-password or OAuth session; public AppView "generous limits", no number published; PDS 3,000 req / 5 min / IP | **Doc-verified** from the raw lexicon; engagement field names inferred from `postView` — confirm before relying |
| **YouTube** `search.list` | `q` (supports `-` NOT, `\|` OR) | `order` (`date`, `viewCount`, `rating`), `publishedAfter/Before`, `regionCode`, `relevanceLanguage`, `type` | **none inline** — must follow with `videos.list` | **100 quota units per call**; default project quota 10,000/day ⇒ **~100 keyword searches per day, total** | **Doc-verified**; this ration is the single hardest constraint on keyword mode |
| **Hugging Face Hub** `/api/models`, `/api/datasets` | `search` | `filter`, `author`, `sort` (`downloads`, `likes`, `lastModified`, `trending_score`), `direction`, `limit` | `downloads`, `likes`, `trending_score` | anonymous 500 req / 5 min per IP; free logged-in 1,000; token recommended | Rate limits **doc-verified** in full; parameter set **medium** — not freshly re-verified against the 2026 OpenAPI spec |
| **Meta Ad Library** `ads_archive` | `search_terms` (≤100 chars) | `search_type` (`KEYWORD_UNORDERED` / `KEYWORD_EXACT_PHRASE`), `ad_reached_countries`, `ad_delivery_date_min/max`, `languages`, `media_type`, `publisher_platforms`, `search_page_ids` (≤10), `ad_active_status`, `estimated_audience_size_min/max` | impressions and spend as **ranges**, demographic breakdown — EU/political ads only | Graph API token; **government-ID verification required**, current 2026 process and turnaround **could not be verified** (every Meta help-centre URL returned 403/404) | Params **doc-verified**; verification process **unverified — do not quote a timeline** |
| **Google News RSS** `news.google.com/rss/search` | `q` | `hl`, `gl`, `ceid` | none — presence only | free; ~100 items per feed | **Live-verified** (a feed was fetched and parsed). **Undocumented and unofficial** — the search endpoint has no Google documentation; the nearest official page redirects to News Sitemaps, an unrelated feature. Functional but tolerated, may break without notice |
| **DataForSEO** — see §4 | `keyword` / `keywords` | `location_code`, `language_code`, `date_from/to`, `time_range`, `depth`, `filters`, `order_by`; SERP `target` restricts to one domain | volume, CPC, competition, 12-month series, rising % | pay-per-task, **$50 minimum top-up** | **Doc-verified** on pricing and parameters |
| **Virlo** — see §3 | `intent` (free text, **required**) + `keywords` array | `platforms`, `region`, `start_date`/`end_date`, `english_only`, `min_views`, `follower_tier`, `order_by`, `limit`, `cadence` | views / likes / comments, outlier scores, sound and hashtag velocity | credits; `search_keywords` 50–100, niche-monitor run 50 | **Doc-verified** from `dev.virlo.ai/docs`; **tier entitlement contradicts the pricing page — see §3.4** |
| **Reddit** `/search`, `/r/{sub}/search` | `q` (supports `author:`, `subreddit:`, `title:`, `flair:`) | `sort` (`relevance`, `top`, `new`, `comments`), `t` (`hour`…`all`), `restrict_sr`, `limit` ≤100, `after`/`before` | `ups`, `upvote_ratio`, `num_comments` | OAuth2; free tier historically 100 QPM per client id; **commercial use needs approval** | **UNVERIFIED — every Reddit domain was blocked to the researcher this session.** Rests on last-known 2023-era policy. Must be re-checked before the W6-1 application is filed |

### 2.2 Not steerable — fixed feeds we must filter ourselves

| Source | What it gives | Filters it *does* accept | Confidence |
|---|---|---|---|
| **Hacker News (Firebase)** `/v0/topstories` etc. | arrays of item IDs; each needs its own fetch | none — no keyword, no category, no window | **Doc-verified**: *"a dump of our in-memory data structures"* |
| **YouTube** `videos.list?chart=mostPopular` | current regional popularity chart | `regionCode`, `videoCategoryId` only; **no time window, no query** | Doc-verified. **1 quota unit** — cheap enough to poll constantly, which is the inverse of `search.list` |
| **Product Hunt** GraphQL `posts` | launches | **`topic` slug, not free text**; `postedAfter`/`postedBefore`; `order` | Doc-verified that `topic` takes a slug and no free-text search argument is documented. Semi-steerable at best |
| **Bluesky Jetstream / firehose** | full event stream | collection NSID or repo DID only — **no keyword filtering at stream level** | Doc-verified |
| **Virlo Analytics family** | `get_trends`, `get_trending_videos`, `get_emerging_trends`, `get_trends_digest`, `get_trending_sounds`, `get_breakout_sounds` | platform, region, date range — **no topic query** | Doc-verified |
| **Google Trends** | rising/related terms | **seed-keyword-dependent** — see §4.3 | Doc-verified |
| **Newsletters, podcast RSS, Czech trade press, GitHub trending** | whole feed | none | As designed |
| **LinkedIn Ad Library** | — | **No API exists.** LinkedIn's current Marketing API catalogue (moniker `li-lms-2026-07`) lists Advertising, Event Management, Community Management, Lead Sync, Matched Audiences, Conversions, Company Intelligence, Audience Insights, Media Planning — **no Ad Library, no Ad Transparency product**. Browser only | **High — definitively established** |

### 2.3 The one-line conclusion

**Nine sources take our keywords. Eight do not.** For the eight, the operator's watch topics are inert unless a local filter exists — and none does. That is the whole of P-12.

---

## 3. Virlo — the detailed control surface

Server: `https://dev.virlo.ai/api/mcp/mcp`, streamable-HTTP transport, server card at `virlo.ai/.well-known/mcp/server-card.json`. Auth: API key `virlo_tkn_…` as a bearer token for non-Anthropic clients; Claude clients use an OAuth-style connector flow. **The key form is what matters for us — it means unattended cron operation with no interactive login**, which the design already requires.

**Virlo's own pages disagree on how many tools exist — 20, 48 and 49 all appear.** Treat the list below as indicative and run a live `tools/list` during the trial to get the authoritative set.

### 3.1 The two tool families, and why the distinction decides the design

**Family A — Analytics. Browse-shaped. No topic query.**
`get_trends` · `get_trends_digest` · `get_emerging_trends` (momentum-ranked, ~25 credits) · `get_trending_videos` (~25–50, last ~48h) · `search_hashtags` (~5–10) · `get_hashtag_performance` · `get_trending_sounds` · `get_breakout_sounds`
These return platform-wide or region-scoped precomputed trends. `search_hashtags` and `search_sounds` do fuzzy matching **on hashtag and sound names only**, not on topical content — a weak filter, not a query.

**Family B — Orbit and Comet. Query-shaped. This is the one that answers the operator's question.**

| Tool | Shape | Key parameters |
|---|---|---|
| `suggest_keywords` | **free** | `intent` (≤500 chars, required), `topic_hint`, `platforms`, `existing_keywords`, `mode` (`create`/`refresh`/`opportunity`), `desired_count` (clamped 7–12), `use_web_grounding` |
| `search_keywords` | one-shot, ~50–100 credits | `intent` (**required free text**), `keywords` (6–10 phrases recommended), `english_only` (default true), `data_intelligence_enabled` (+$1). Async: auto-polls ~55s, full run reportedly 15–20 min |
| `create_niche_monitor` | **recurring** | same as above plus `cadence` (daily / weekly / monthly) |
| `get_niche_monitor_data` | **free read** | `data_type`: overview · videos · slideshows · ads · outliers · analysis · trends · sounds · hashtags · benchmarks |
| `list_keyword_searches`, `get_keyword_search_results` | **free reads** | by `data_type` |

**The decisive finding: niches are user-defined by free text, not chosen from a fixed enum.** Virlo's docs explicitly instruct the caller to write a real multi-word intent rather than invent one from a keyword list, and no page anywhere lists selectable preset niches. So *"trending short-form content about AI coding tools and AI agents, last 7 days"* with a keyword array is a supported call shape — this is exactly what the operator asked whether we can do.

Steering parameters confirmed present across the REST/MCP surface: `region` (ISO-3166-1 alpha-2), `start_date`/`end_date` (ISO 8601), `platforms` (`tiktok` / `instagram` / `youtube`), `english_only`, `min_views`, `follower_tier` (`nano`/`micro`/`mid`/`macro` — tiers only, no raw numeric follower filter), `order_by` (`views`, `publish_date`, `weighted_score`, `rising`, `usage`, `volume`, `growth`), `limit` (REST default 50, max 100), `page`.

### 3.2 How this maps onto our design

**One standing niche monitor is the right primary integration, not per-run keyword searches.**

- `create_niche_monitor` at daily cadence costs **50 credits per run**; `get_niche_monitor_data` reads are **free**. A per-run `search_keywords` costs 50–100 and takes 15–20 minutes to complete — wrong shape for a cron job that must finish inside a wall-clock ceiling.
- So: the monitor is created once from the theme's watch topics, refreshed when the topic set changes, and each pipeline run performs a **free read** of the already-computed result. Virlo's async job semantics stop being a runtime problem, because the run never waits on a job.
- `get_emerging_trends` (25 credits) remains the discovery-mode complement — it answers *"what is rising that we did not ask about"*, which is precisely the signal keyword steering cannot produce.

Against the modelled 2,000-credit Starter allowance: one daily monitor run (1,500/mo) plus twice-weekly emerging-trends (200) plus occasional hashtag spot checks leaves headroom. **Note this is a different allocation from B5's modelled plan** (which budgeted a *weekly* niche-monitor run at 200/mo and a *daily* trend digest at 750/mo) — daily monitoring of our own niche is worth more to this pipeline than a daily generic digest, and the trial should test that preference rather than inherit the brief's guess.

### 3.3 Coverage

Platforms: **TikTok, Instagram Reels, YouTube Shorts** — stated consistently. Granularity is video/creator level, sound level, hashtag level **and** topic-cluster level via the trends family.

**Czech coverage is unknown.** No Virlo page mentions Czech Republic or Central Europe, positively or negatively. `region` appears to be *inferred from platform metadata* (`tiktok_region`, `youtube_channel_country`, `instagram_location_tag`, `inferred_normalize`, or unresolved) rather than drawn from a curated allowlist — so CZ content could surface if its metadata resolves. The `features` page declares `availableLanguage: English` and a US address. **This must be tested with `region: "CZ"` on day one of the trial.** The architecture's current assumption (§2.3, *"assume global-English"*) is the safe default and should stand until disproven.

### 3.4 The gating contradiction, restated because it decides adoption

Virlo's **pricing page lists "API access" as an Enterprise-tier bullet**, while its **MCP documentation and Claude-connector guide describe obtaining API keys and connecting with no stated plan gate**, and both Starter and Pro list "Orbit Search" — the same product exposed as `search_keywords` — as an included feature. B5 already flagged this (W2-17) as *"the single gating fact for the adopt verdict"*. Research confirms it is still unresolved from public sources.

**Trial day-one checklist, in order:** (1) does an API key issued on Starter authenticate against the MCP endpoint at all; (2) `tools/list` for the authoritative tool and parameter set; (3) `create_niche_monitor` with an AI-agents/AI-coding intent, then read it free — does the AI/B2B niche have enough tracked density to return anything useful; (4) `region: "CZ"` on any trends call; (5) measure actual refresh latency, since Virlo's own pages claim both *"daily data refresh"* and *"sub-hour"*.

Also unresolved and worth capturing during the trial: exact free-trial length and starting credit grant (a changelog entry confirms trial credits exist; no page states the amount), and any request-rate ceiling — only per-call credit costs are published, never a requests-per-minute limit. No independent reviews were obtainable (Trustpilot 403, Product Hunt 404, `virlo.ai/about` 404, no status page at the obvious host) — the only comparison content available is Virlo writing about itself.

---

## 4. DataForSEO — and the honest limit on "rising"

### 4.1 What we would actually call

| Endpoint | Returns | Price |
|---|---|---|
| `/v3/keywords_data/google_trends/explore/` | interest over time, interest by subregion, **related topics and related queries each split into `top` and `rising`** | **$0.011/task live** (~32 s), **$0.0027 standard** (~45 min); ≤5 keywords per task |
| `/v3/keywords_data/google_ads/search_volume/` | monthly volume, competition, CPC, 12-month series | $0.09 live / $0.06 standard; **up to 1,000 keywords per task** |
| `/v3/dataforseo_labs/google/related_keywords/live/` | semantic expansion from one seed, depth 0–4, up to 4,680 results, with `search_volume_trend` % change | Labs bucket: $0.012/task + $0.00012/item |
| `/v3/serp/google/organic/live/advanced/` | organic SERP, **`target` parameter restricts to one domain** | $0.002 live / $0.0006 standard. Operators like `allintitle:` in the keyword field **multiply cost 5×** |

That `target` parameter is the mechanism for **W6-1's Reddit fallback**: a domain-restricted SERP query against `reddit.com` for our watch topics, at $0.002 per call, with no Reddit credential involved.

### 4.2 Czech

`location_code` **2203** = Czech Republic — cited from a Google Ads geo-target reference, **not** confirmed against DataForSEO's own locations endpoint, which was unreachable. The literal `language_code` DataForSEO expects for Czech (`"cs"` vs a numeric criterion) is **unconfirmed**. Both must be verified live against `/v3/keywords_data/google_ads/locations` and the languages endpoint before anything is built.

### 4.3 The limit that matters, stated plainly

**There is no endpoint in DataForSEO's entire catalogue that surfaces breakout or trending terms without a seed keyword.** The Labs catalogue was checked end to end — Keywords For Site, Related Keywords, Keyword Suggestions, Keyword Ideas, Bulk Keyword Difficulty, Search Intent, Keyword Overview, Historical Keyword Data, Categories For Domain/Keywords, Keywords For Categories, Top Searches — and none is a momentum feed. Google Trends Explore's `rising` arrays are the only momentum signal, and they are **relative to a keyword you supply**.

**The design consequence:** DataForSEO is a *steered* instrument only. It answers *"is what we care about growing, and what adjacent terms are growing around it"*. It cannot answer *"what should we be looking at"*. That question is answered only by Virlo's emerging-trends family, Hacker News, Product Hunt, Hugging Face and Bluesky. **A theme that turns off every discovery-mode source becomes blind to anything outside its own keyword list** — that is a readiness condition, not a preference (§6.4).

### 4.4 Cost and the corrected figure

Billing is literal USD per task from a prepaid balance, **minimum top-up $50** — the architecture's "~$10–15/month" is a *usage* estimate, not a deposit, and §2.3's economics should say so. Rate limits: 2,000 req/min per account, 30 concurrent, ≤100 tasks per POST, 120 s live timeout (medium confidence — retrieved via snippet, primary page unreachable). A sandbox exists at `sandbox.dataforseo.com` but returns **structurally-identical mock data**, useful for integration testing only.

At confirmed unit prices, $10/month buys roughly: 900 live Trends Explore tasks (≈4,500 keyword explorations), or 5,000 live organic SERPs, or 111 Search Volume tasks covering up to 111,000 keywords. Our actual need is a small fraction of any of these — **the demand axis is not where money goes.**

An official open-source MCP server exists (`github.com/dataforseo/mcp-server-typescript`, Apache-2.0, npm `dataforseo-mcp-server`) exposing 10 modules including SERP, Keywords Data and Labs. Individual tool names appear to be auto-derived from endpoints rather than hand-curated; introspect with `tools/list` rather than trusting docs.

### 4.5 One thing the plan assumed that is now wrong

**Google announced an official Google Trends API (alpha) on 2025-07-24** (`developers.google.com/search/blog/2025/07/trends-api`), with documented sections on data availability, consistently-scaled data, time ranges and aggregations, and geography. The full body could not be retrieved and its **2026 status — still alpha, expanded, or GA — is unresolved**. `pytrends`, the unofficial route the evidence base leaned on, was **archived read-only on 2025-04-17** and is unmaintained.

This does not change the recommendation — DataForSEO's wrapper remains the automated path — but §2.3's framing of Trends as *"manual CSV export as the designed degraded state"* should note that an official API now exists and may make the vendor unnecessary later. Add it to the vendor-roster recheck cycle.

---

## 5. The design: two collection modes and a topic object

### 5.1 Collection mode becomes an explicit per-source property

Every source is tagged with exactly one of:

- **Steered** — the source accepts our keywords. The query profile (§5.2) builds the request. Relevance is enforced *at the source*, so almost everything returned is on-topic and cheap to rank.
- **Discovery** — the source returns a fixed feed. Our keywords cannot reach it. Relevance must be enforced *after* collection, by the topic filter (§5.3).
- **Both** — the source offers each surface separately, and the design must say which is used when. Hacker News (Algolia search vs Firebase lists), YouTube (`search.list` vs `mostPopular`) and Virlo (Orbit/Comet vs Analytics) are all of this kind, and today the plan silently conflates them.

This replaces the undefined phrase "query-shaped collector" with a real, enumerable property, and gives §13.2 something to validate.

**Neither mode may be turned off wholesale.** Steered-only collection can only ever return what the operator already thought of, which is the mechanism by which a content pipeline slowly narrows into its own echo. Discovery-only collection cannot honour the theme's focus at all. Readiness therefore asserts **at least one enabled source in each mode, per language** (§6.4).

### 5.2 The query profile — one per (source × language)

A **query profile** states, in prose per source, how a topic entry becomes a wire request:

1. **Which field carries the query**, named exactly (`query`, `q`, `search_terms`, `intent`+`keywords`, `topic` slug, `keyword`).
2. **Syntax and operator support** — quoting, boolean, phrase-vs-unordered (Meta's `search_type`), what is silently ignored.
3. **Time window** — a parameter (`numericFilters` on `created_at_i`, `since`/`until`, `publishedAfter`, `ad_delivery_date_min`, `start_date`) or a post-filter (Firebase lists, `mostPopular`, Product Hunt without dates).
4. **Engagement threshold** — a parameter (Algolia `points>N`, Virlo `min_views`) or a post-filter (everywhere else).
5. **Result cap and pagination**, with the *empirical* value where it differs from the documented one — Algolia's ~100 rather than 1,000 is the worked example.
6. **Cost per call**, in the source's own unit, so §2.3's per-source run budget becomes computable rather than declared. YouTube's 100-units-per-search against a 10,000/day quota is the case where this changes behaviour.
7. **Language handling** — whether the language is a parameter (`hl`/`gl`/`ceid`, `lang`, `relevanceLanguage`, `language_code`, `english_only`), or is carried only by the query string's own language, or is unsupported.

### 5.3 The missing local topic filter — deterministic, before ranking

A **topic-relevance filter** runs inside normalisation (§2.8), after language stamping and before dedupe, on **discovery-mode items only** — steered items already passed relevance at the source and must not be filtered twice.

It is **deterministic and model-free**: match against the topic object's surface forms, aliases and entities for the item's stamped language, with the theme's research-side excludes applied as a negative pass. Its output is a **retained / dropped** decision with the matched term recorded, so a run digest can say *"Google News CZ returned 87 items, 6 matched watch topics"* — which is the diagnostic that tells an operator their Czech keywords are wrong, and which the design currently cannot produce.

Three properties, stated because each closes a specific failure:

- **It filters *in*, not *out*.** The existing rules-first brand-fit tier filters out (category mismatch, competitor saturation, controversy). This is the positive pre-filter B3 assumed existed and named as the first line of defence. Both are needed; neither substitutes for the other.
- **It never blocks a run and never manufactures volume.** A discovery source matching nothing produces a named digest line, exactly like the per-language evidence-and-volume band.
- **It is a cost control before it is a quality control.** Every item it drops is an item that does not reach node N-1, and N-1 is a per-candidate LLM call. On an unfiltered Czech news feed that is the difference between tens of model calls and a handful.

### 5.4 Watch topics become a structured, per-language object

Today: one flat list, shared across languages, sent nowhere in particular. Replaced by a **topic entry** carrying:

- a **canonical name** (the cluster identity used by dedupe and by the resurgence rule);
- **surface forms per language** — the actual strings sent on the wire, which are not translations: *"cold outreach"* and *"studený outreach"* are both real, and neither is produced by translating the other;
- **aliases and entity names** for the local filter (product names, model names, company names — this is also where check class 3's culturally-shared-noun problem gets its input);
- **negative terms** — the homonym killer. *"agents"* without a negative set collects real-estate and sports content forever;
- **per-source overrides**, because the same topic needs different phrasing on different surfaces: a Product Hunt `topic` slug, a Meta `search_terms` phrase, a Virlo `intent` sentence and a Google News `q` string are four different artefacts describing one topic.

**Per-language surface forms are the load-bearing addition**, and they interact with a fact the design already states honestly: only four sources carry direct Czech signal, and everything else discovers in English. So a Czech surface form is worth authoring for Google News, DataForSEO, the ad libraries and the alert services — and is close to worthless on Hacker News, Product Hunt and Hugging Face. **The query profile is where that asymmetry gets recorded per source, instead of being rediscovered by the operator as a mystery.**

---

## 6. Consequences

### 6.1 The default HypeDigitaly theme, concretely

Primary configuration, per the operator: brand truth from the HypeDigitaly Notion workspace (MCP interactive, REST for records, per D-10), watch topics seeded on **lead generation · AI coding · AI agents**.

Those three are not one shape and should not be configured as one. *AI coding* and *AI agents* are discovery-rich — Hacker News, Product Hunt, Hugging Face, Bluesky and Virlo all carry real momentum on them, so discovery mode does most of the work and steering mainly sharpens it. *Lead generation* is nearly absent from those same sources; it lives in demand data, the ad libraries and Reddit, and is almost entirely a **steered** topic. A theme whose three headline topics split that way is a good first test of whether the two-mode design earns its keep.

### 6.2 A second theme for falsification

An expressive/esoteric theme remains the falsification fixture of `00_MASTERPLAN.md` PB-OD-1, and query steering is one more axis on which it falsifies: its topics are aesthetic rather than lexical, its Virlo niche density is likely *higher* than the AI/B2B niche, and its discovery/steered balance inverts. It is not run against a real audience until the Prohibited-Outcome Gate has been exercised in review.

### 6.3 Cost

Adding steering **reduces** spend rather than raising it. Each steered call replaces an unfiltered feed pull whose every item paid for a ranking pass, and the local filter drops the rest before node N-1. The one place steering costs real money is YouTube, where `search.list` at 100 units against a 10,000/day quota affords roughly **100 keyword searches per day in total** — so YouTube keyword search is a weekly instrument on a small topic set, while `mostPopular` at 1 unit stays the daily one. That asymmetry must be written into the query profile, or an implementer will burn the day's quota before lunch.

### 6.4 New readiness assertions (§13.2)

- Every source carries a **collection mode** and, if steered, a **query profile per configured language**.
- Every configured language has **at least one steered and one discovery source enabled**.
- Every topic entry has a **surface form in every configured language**, or an explicit recorded declaration that this topic is English-discovery-only.
- Dry-run collection reports, per source, **items returned and items retained after the topic filter** — a source retaining zero across a dry run is a readiness failure, not a silent pass.

### 6.5 Wire-in

| Change | Section |
|---|---|
| Collection mode as a per-source property; the roster gains the column | §2.2, §2.3, §10.2 |
| Query profile concept and its seven statements | §2.3, §2.4, new subsection under §2 |
| Topic-relevance filter placed inside normalisation | §2.8, §2.7 (what reaches the fit gate), §12.1 (digest line) |
| Structured per-language topic entry replacing the flat knob | §10.2, §10.1 minimum-viable set, §2.7, §6.9 |
| Virlo integrated as a standing niche monitor read freely per run, not a per-run search | §2.3, §5.4a, §8.2 |
| DataForSEO `target`-restricted SERP as the W6-1 Reddit fallback | §2.3, `DECISION_LOG` W6-1, OD-29 |
| Google Trends official alpha API noted; `pytrends` recorded as archived | §2.3, vendor roster recheck cycle |
| DataForSEO $50 minimum top-up corrected in the economics | §2.3, §5.4 |
| P-12 added to the defect list; new readiness assertions | `00_MASTERPLAN.md` §1, §13.2 |

---

## 7. What is not yet known — trial and verification list

Recorded so none of it is silently assumed. Each is a Phase-0 item.

**Blocking before build:** Reddit's entire current 2026 policy set — the researcher was blocked from every Reddit domain, so the query surface, rate limits and commercial-approval process all rest on 2023-era knowledge · Virlo's tier entitlement (does a Starter key authenticate against the MCP endpoint) · Virlo's authoritative `tools/list` · DataForSEO's Czech `location_code` and `language_code` against the live locations and languages endpoints · Meta's current identity-verification requirement and turnaround, which no reachable page documented.

**Measure during trial:** Virlo AI/B2B niche density · Virlo `region: "CZ"` behaviour · Virlo true refresh latency (its own pages claim both daily and sub-hour) · Virlo free-trial length and credit grant · Virlo and Algolia rate limits, neither published · Product Hunt's `PostsOrder` enum values and `Post` field names · Hugging Face's exact `sort` enum and whether a trending endpoint exists for models · Bluesky's `postView` engagement field names and whether `searchPosts` works unauthenticated.

**Confirm from primary text:** the Google Trends alpha API's current status, whether its data is absolute or normalised, and its quotas · Google News RSS topic-feed syntax and whether date operators work · YouTube's current ToS position on caching metadata · Meta Ad Library ToS on redistribution of derived output · commercial-use terms for the Algolia HN endpoint.
