# C1 - Notion MCP & Postiz Integration Research Brief

## What This Means for the Operator

Your brand truth lives in Notion (offers, claims, voice, ICP rules). Our system needs to reliably extract that truth both when you're testing interactively AND when it runs unattended at 03:00 via cron. **Notion's hosted MCP won't work for cron—tokens expire too often and require browser clicks.** The solution: use Notion's REST API with a static internal token for cron, and keep the MCP for quick interactive testing.

For publishing, Postiz is a solid bridge to draft posts without auto-publishing. It supports saving content as "DRAFT" status that sits in your calendar untouched until you approve it. However, Postiz does **not expose AI-content-label fields** (TikTok's AIGC flag, Meta's AI checkbox, YouTube's disclosure field), so you'll need to add those labels manually in each platform after review. The good news: Postiz works the same on cloud and self-hosted, so you can trial cloud risk-free and switch later if needed.

For config-based safety: declare which channels are allowed per mode (test/staging/live). Postiz integration should only connect channels you explicitly list—research-only channels stay disconnected entirely as defense-in-depth. Fail if config allows a channel that isn't connected.

---

## Deep Research: Brand-Truth Extraction from Notion

### 1. Brand-Fact Taxonomy vs. Notion MCP Tool Surface

**Candidate taxonomy (what we must extract):**

| Taxonomy Item | Description | Example |
|---|---|---|
| **Offers** | Configured products/services with accurate names, descriptions | HypeLead, HypeDigitaly s.r.o. |
| **ICP map** | Ideal customer profile: personas, industries, pain points | Startups, 0–50 headcount, lead gen friction |
| **Approved-claims allowlist** | Hard-verified claims safe to attach to CTAs | "Reduces lead-gen time by 40%," "Trusted by 50+ teams" |
| **CTA set** | Valid calls-to-action per offer | Demo → product page, audit → calendar link |
| **Pricing policy** | What can be said about pricing (ranges, hidden, free tier policy) | Starting at $X/mo or "Let's talk" |
| **Proof/case allowlist** | Verified client names, results, testimonials | Client X saw Y, published in Z (public source only) |
| **Voice rules** | Tone, vocabulary, forbidden patterns | Conversational, no "game-changer," no slang |
| **Hard excludes** | Topics, claims, customer types to never touch | Privacy-sensitive claims, GDPR-risky proof |

**Notion MCP tool surface (current capabilities per v2026-03-11):**

| Tool | Purpose | Constraints |
|---|---|---|
| `search_pages` | Full-text semantic search across workspace | Max 25 results, no property-based filtering, capped at 30 searches/min |
| `read_page_content` | Retrieve blocks from a page (text, lists, tables, databases) | One page at a time, must know page ID or search first |
| `read_database` | Fetch database rows with schema | Returns structured data but limited query filters (semantic only, date/creator filters only) |
| `update_database` | Write/modify a database row | Not ideal for brand-truth reads, but possible for sync status |
| `create_content` | Create new pages/blocks | Out of scope for read-only brand truth extraction |
| `query_data_sources` | Query Notion AI data sources (Enterprise only) | Requires Notion AI, not reliable for taxonomy validation |

**Assessment: retrievability gaps**

- **Approved-claims allowlist (structured table):** Requires property-based filtering (e.g., "Status = Approved"). Notion MCP's `read_database` does NOT support filtering by specific property values. **Workaround:** store as a single richly-tagged page, search by keyword, or fetch entire database and filter client-side. **Confidence: Low** (requires post-retrieval filtering).
- **Offers/ICP/CTA mapping:** Can store as database with properties (Offer Name, ICP, CTA), but filtering is semantic-search-only. **Workaround:** fetch all rows and filter in code. **Confidence: Medium** (works but inefficient at scale).
- **Voice rules / hard excludes:** Best stored as page content (structured lists). `read_page_content` retrieves accurately. **Confidence: High**.
- **Pricing policy:** Sensitive; best stored as single page with versioning. `read_page_content` reliable. **Confidence: High**.

**Conclusion:** Notion MCP can retrieve brand truth but struggles with structured queries. For cron reliability, prefer direct Notion REST API with internal token (see §2), which offers full query support via filter objects.

---

### 2. Authentication Model: MCP vs REST API for Unattended Cron

**Notion MCP (hosted, OAuth-based)**

- Flow: Browser OAuth consent → token stored locally → interactive apps only
- Token lifetime: ~3 hours (observed token expiry requires re-auth 3+ times per week)
- Refresh behavior: refresh tokens are stored but NOT automatically used; expired tokens cause interactive re-auth prompts
- Cron suitability: **FAIL**. Unattended cron cannot click "Authorize." A 03:00 scheduled run hits an expired token and blocks indefinitely.
- Evidence: [MCP OAuth re-authentication required every few hours (Notion, Atlassian) on Windows · Issue #44416 · anthropics/claude-code](https://github.com/anthropics/claude-code/issues/44416), [OAuth token expires too frequently — requires re-authentication 3+ times per week · Issue #225 · makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server/issues/225)

**Notion MCP (self-hosted, token-based)**

- Alternative community servers (e.g., `awkoy/notion-mcp-server`) support HTTP transport with bearer-token auth via `--auth-token` command-line flag
- Auth: Static MCP_AUTH_TOKEN environment variable (no browser interaction)
- Cron suitability: **YES**, with setup overhead
- Constraint: Requires separate MCP server instance; not vendor-managed
- Evidence: [Notion MCP vs Notion API for AI Agents: Which to Use](https://www.scalekit.com/blog/notion-mcp-vs-api)

**Notion REST API (internal integration token)**

- Flow: Create integration in Notion workspace → receive static secret token (begins with `secret_*`) → Bearer auth in REST calls
- Token lifetime: Non-expiring (static). No refresh needed.
- Rate limits: 3 requests/sec per integration (sufficient for daily cron)
- Cron suitability: **EXCELLENT**. Token lives in env var; cron job reads it and runs unattended.
- Query power: Full filter objects for databases (e.g., `"filter": {"property": "Status", "select": {"equals": "Approved"}}`)
- Maintenance: Notion owns the API; updates documented; widely used in production automation
- Evidence: [Your Ultimate Notion API Doc Reference for 2026 | NotionSender](https://www.notionsender.com/blog/post/notion-api-doc), [Notion API connections – Notion Help Center](https://www.notion.com/help/create-integrations-with-the-notion-api)

**Honest split recommendation**

| Context | Choice | Rationale |
|---|---|---|
| **Interactive operator testing** | Notion MCP (hosted OAuth) | Easy setup, quick exploration, web UI integration |
| **Unattended cron (03:00 daily)** | Notion REST API (internal token) | Non-expiring token, full query filters, no browser interaction, well-tested in production automation |
| **Fallback if REST API unavailable** | Self-hosted token-based MCP | Requires ops work but possible; do not default to browser-OAuth MCP |

**Capability loss/gain per path:**

- MCP (OAuth): Gain ease of setup, lose unattended execution safety
- REST API: Gain full query power and cron reliability, lose lightweight MCP tool abstraction (must call HTTP directly or wrap in a utility layer)

---

### 3. Rate Limits, Client Maturity, Reliability

**Notion MCP (official, vendor-managed)**

- Hosted rate limit: 180 requests/min per user (search capped at 30/min)
- API version: v2026-03-11 (current as of March 2026)
- GitHub stars: 4,200+, 539 forks; maintained by @notionhq
- Maturity: Stable for read-heavy workloads; known issue with OAuth token persistence; editing/creation edge cases exist
- Community alternatives: `awkoy/notion-mcp-server`, `suekou/mcp-notion-server` (variable update cadence; evaluate before production use)
- Evidence: [Notion MCP Server | MCP Server](https://mcp.so/servers/mcp-notion-server), [GitHub - makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server)

**Notion REST API (official, vendor-maintained)**

- Rate limit: 3 requests/sec per integration (~10,800 requests/hour), adaptive per workspace load
- Maturity: Production-grade; widely used in n8n, Zapier, Make integrations
- Documented failures: Occasional rate-limiting during peak load; exponential backoff advised
- Latest API: v2026-03-11
- Evidence: [Request limits - Notion Docs](https://developers.notion.com/reference/request-limits), [Notion API Rate Limits Explained: 2026 Complete Guide | UnBanAI](https://www.unbanai.org/blog/notion-api-rate-limits-explained-2026)

**Structured-retrieval reliability assessment**

- MCP: Semantic search works reliably; property-based filtering is not exposed → **Medium confidence for allowlist/ICP retrieval**
- REST API: Full query filters with property objects → **High confidence for structured brand-truth retrieval**
- Recommendation for cron: Prefer REST API. Pre-cache brand-truth on startup; refresh daily. If retrieval fails, use fallback from prior successful run or mark reduced brand-confidence in review package (per constraint: do not hallucinate claims).

---

## Deep Research: Postiz as Draft-First Publishing Bridge

### 4. Kill-Switch Question: Unscheduled Drafts Without Auto-Publishing

**Direct answer: YES**

Postiz explicitly supports creating and storing posts in **DRAFT status** without assigning a schedule date. Posts remain in draft state indefinitely until an operator changes the status to "schedule" (with a date) or "now" (immediate publish).

**API contract**

- Endpoint: POST `/public/v1/posts`
- Request parameter: `"type": "draft"` (alternatives: `"schedule"`, `"now"`)
- Post state: stored as `state: "DRAFT"` in database
- Behavior: Draft post appears in calendar/UI; does NOT publish on any automatic trigger
- Evidence: [Create Post - Postiz Documentation](https://docs.postiz.com/public-api/posts/create), [Managing Posts - Postiz Documentation](https://docs.postiz.com/cli/managing-posts)

**Fallback ladder (if draft storage fails)**

| Fallback | Mechanism | Operator Friction |
|---|---|---|
| **1. Unscheduled draft (primary)** | POST with `type: "draft"` | Zero; built-in workflow |
| **2. Far-future scheduled post** | POST with `type: "schedule"`, date = 2099-12-31 | Low; requires date change before publish |
| **3. Local-only staging + manual paste** | Generate post JSON locally, export as JSON/CSV, operator manually copy-pastes per platform | High; manual per platform, error-prone |

**Practical test criteria**

- Can create N posts via API as drafts without auto-publishing? ✓ Yes, documented
- Does draft status persist across service restart? Need to verify in staging trial
- Can API move draft → schedule → draft → schedule as needed? ✓ Yes, via state transitions
- Are draft posts visible in UI for human review? ✓ Yes, appears in calendar

---

### 5. Cloud vs. Self-Hosted Differences

**Feature parity: COMPLETE**

Both cloud and self-hosted Postiz (running same codebase, AGPL-3.0 license) have identical feature sets. **No feature gating between cloud and self-hosted.**

| Aspect | Cloud | Self-Hosted | Difference |
|---|---|---|---|
| **Drafting** | Yes | Yes | None |
| **Scheduling** | Yes | Yes | None |
| **28+ platform connectors** | Yes | Yes | None |
| **AI image/caption generation** | Yes | Yes | None |
| **Approval workflows** | Yes | Yes | None |
| **API access** | Yes | Yes | None |
| **Cost** | $29–$99/mo (channel-based) | $0 (self-host) | Ops responsibility on self-hosted |

**Operational differences (not feature-related)**

| Concern | Cloud | Self-Hosted |
|---|---|---|
| **Infrastructure** | Postiz-managed, SLA available | You own Docker + Kubernetes (or Docker Compose) |
| **Uptime responsibility** | Postiz | Operator |
| **OAuth app management** | Postiz handles (28+ integrations pre-registered) | Operator registers each integration separately with each platform (X, Instagram, etc.); manage API keys |
| **Token refresh / rate limit retries** | Postiz handles | Operator maintains code + monitoring |
| **Infrastructure resource requirement** | None | 2–4 GB RAM, 6–9 Docker containers |
| **Update lag** | Automatic | Manual (pull latest image, redeploy) |
| **Platform API changes** | Postiz adapts | Operator must update connectors |
| **Evidence** | [12 Best Mixpost Alternative Tools for Social Media Management in 2026 - Postiz](https://postiz.com/blog/mixpost-alternative), [The Cheapest and Safest Way to Host Postiz (Self-Hosted Tutorial) - DEV Community](https://dev.to/pratikpathak/the-cheapest-and-safest-way-to-host-postiz-self-hosted-tutorial-4n3g) | [Postiz vs Postproxy: Self-Hosted vs Managed API](https://postproxy.dev/compare/postiz/) |

**Recommendation for HypeDigitaly (trial phase)**

Trial on **cloud ($29/mo Standard tier: 5 channels, 400 posts/mo)** first. Postiz cloud is stable, includes API key auth (no OAuth setup friction), and lets you prove the research→draft workflow before committing to self-hosting ops burden. Later, if you need cost savings or air-gapped deployment, migrate to self-hosted (same features, but plan 2–4 weeks for OAuth app registration across platforms).

---

### 6. Connector Coverage: List B Destinations + Business Account Requirements

**Confirmed connector support (28+ platforms)**

| Destination | Postiz Support | Existing HypeDigitaly Account | Status |
|---|---|---|---|
| **LinkedIn** | ✓ Yes | ✓ Company page exists | Ready |
| **X (Twitter)** | ✓ Yes | ? (Not mentioned in brief) | Needs verification |

**F-2 separation note:** X here is evaluated ONLY as a publish destination via Postiz user-OAuth. This is a separate decision from X research reads, which the operator dropped for v1 (closed D-08). Enabling X publishing later neither requires nor implies any X read access, and vice versa — the architecture must keep these two decisions independent.
| **Instagram** | ✓ Yes | ✓ Meta business account exists | Ready |
| **TikTok** | ✓ Yes | Depends on Meta business account | Ready if eligible |
| **YouTube Shorts** | ✓ Yes | Depends on YouTube channel | Needs verification |
| **Facebook** | ✓ Yes | ✓ Meta business account exists | Ready |
| **Others** | Threads, Bluesky, Mastodon, Reddit, Discord, Pinterest, Discord, Telegram, etc. | N/A for this theme | Lower priority |

**Business account / app review lead times**

- Meta (Instagram, Facebook): Business account already exists (per brief); Postiz cloud uses pre-registered apps, so **zero setup friction**.
- LinkedIn: Company page exists; Postiz cloud uses pre-registered app, so **zero setup friction**.
- TikTok: Requires TikTok For Business account OR personal account with business features. App review typically **2–3 weeks** if first-time.
- X: Requires API access approval; typically **1–2 weeks** if you have an active account; faster if you have media/app experience.
- YouTube: Requires YouTube channel linked to Google account; Postiz cloud uses pre-registered app, so **no additional approval needed**.

Evidence: [How to Automate TikTok, Instagram, and YouTube Short-Form Content with AI: A Complete Workflow - Postiz](https://postiz.com/blog/how-to-automate-tiktok-instagram-and-youtube-short-form-content-with-ai-a-complete-workflow), [Postiz - Comparateur-IA](https://choose-your-ai.com/ai-tools/postiz)

**Practical implication for F-4 (publish-allowlist)**

Config should declare which channels are enabled per mode:
- **Test/Safe mode:** `allowed_channels: []` (empty, no external calls)
- **Staging mode:** `allowed_channels: ["linkedin", "x"]` (research-only channels)
- **Live mode:** `allowed_channels: ["linkedin", "instagram", "facebook", "tiktok"]` (approved publish targets)

If config specifies a channel but Postiz integration is not connected (no OAuth token), **fail closed** with clear error message: "Instagram connector not initialized; cannot publish in live mode."

---

### 7. Platform AI-Label Fields: Disclosure Gaps & Compliance Implications

**Platform-specific AI disclosure requirements (2026 enforcement)**

| Platform | Requirement | Form | Auto-Detection |
|---|---|---|---|
| **TikTok** | AIGC label required on any AI-generated or significantly altered realistic depiction | Manual checkbox OR automatic via C2PA Content Credentials metadata | Yes, if content carries C2PA signals |
| **Meta (Instagram, Facebook)** | AI-generated checkbox required for ads; all platforms require "AI info" label | Manual checkbox in Ads Manager when creating ad | Yes, auto-detection for unlabeled AI; rejection if undisclosed |
| **YouTube** | Altered-content disclosure required for realistic depictions | Creator Studio / YouTube Studio disclosure field | Partial; some auto-detection via hashing |

**Enforcement & penalties (2026)**

- **TikTok:** Removes 51,618 synthetic videos (2H 2025), 340% increase vs. 2024; immediate strikes, not warnings.
- **Meta:** Undisclosed AI is 3rd-largest reason for ad rejection (14% of rejections); 3 violations = account suspension.
- **YouTube:** Strikes issued; videos labeled but not removed; policy still evolving.

Evidence: [AI Video Ad Disclosure Requirements 2026: Meta, YouTube, TikTok & Legal Compliance](https://virvid.ai/blog/ai-video-ad-disclosure-requirements-2026-meta-youtube-tiktok), [AI UGC Disclosure Rules in 2026: Meta and TikTok Requirements — The Social Outline](https://thesocialoutline.com/blog/ai-ugc-disclosure-rules), [TikTok AI Content Policy 2026: 4-Tier Labels & Penalties](https://www.auditsocials.com/blog/tiktok-ai-content-disclosure-rules-2026)

**Postiz capability assessment: DOES NOT EXPOSE AI-LABEL FIELDS**

Current Postiz API and MCP surface do **NOT** expose per-platform AI-content-label, AI-disclosure, or AIGC fields. You can create and schedule posts, but you cannot programmatically set:
- TikTok AIGC toggle
- Meta "AI-generated" checkbox
- YouTube "altered-content" disclosure

Evidence: [Public API - Postiz Docs](https://docs.postiz.com/public-api), [Postiz MCP – The Social Media MCP Server for ChatGPT & Claude](https://postiz.com/mcp)

**Compliance consequence & mitigation**

- **Gap:** Posts generated via this system will be flagged as AI-generated. Operator MUST manually add AI-disclosure labels in each platform after Postiz drafts are created.
- **Risk:** If labels are omitted, platforms will auto-detect and reject/penalize the account.
- **Mitigation strategy:**
  1. In review package, clearly mark posts as "AI-generated content" with red banner
  2. Add checklist item to approval workflow: "Verify AI labels applied in each platform before live-publish"
  3. Consider pre-filling C2PA Content Credentials metadata in video generation (if using video providers) so TikTok auto-labels
  4. Document in operator guide: "After approval, spend 5 min adding AI-disclosure labels in each platform's native UI"

**Open question for implementation phase:** Can we inject C2PA metadata into videos generated via Kie.ai/Higgsfield.ai to auto-label on TikTok/Meta? (Research needed with video provider partnership.)

---

### 8. Side-Effects Surface, MCP Server Status, API Shape

**Postiz MCP server: Official status**

- **Status:** Officially supported by Postiz (available at `/mcp`, `/mcp/:apiKey`, `/mcp-oauth` endpoints on Postiz instance)
- **Tooling:** 9 tools exposed: integrationList, schedulePostTool, generateImageTool, listPostsTool, getPostTool, updatePostTool, deletePostTool, listSchedulesTool, getScheduleTool
- **Auth:** Bearer token, API key in URL, or OAuth (depending on endpoint)
- **Maturity:** Active, documented; used in production by Claude, ChatGPT, and similar agents
- **Evidence:** [Official Postiz MCP Server | Awesome MCP Servers](https://mcpservers.org/servers/postiz-mcp), [GitHub - solomonneas/postiz-mcp](https://github.com/solomonneas/postiz-mcp)

**API shape for draft creation (via MCP & REST)**

```
MCP schedulePostTool:
  Input: { posts: [{integrationId, content, media, ...}], type: "draft|schedule|now", date?: "ISO timestamp" }
  Effect: Creates post in specified state; if type="draft", no publish date

REST POST /public/v1/posts:
  Input: { posts: [...], type: "draft|schedule|now", date?: "ISO timestamp" }
  Response: { success, post: { id, state: "DRAFT", integrations: [...] } }
```

**Side-effects to block in test/safe mode**

| Effect | Severity | Block Method |
|---|---|---|
| Creating a post (even draft) | Medium | Environment flag: `POSTIZ_MODE=test` → all creates fail with error |
| Publishing a post (type="now") | Critical | Reject if `mode != "live"` AND `config.publish_enabled != true` |
| Updating integration/connection | Critical | Read-only mode; no `updateIntegrationTool` calls in test mode |
| Deleting posts | Medium | Block `deletePostTool` unless explicitly enabled in config |
| Fetching analytics | Low | Safe; read-only; no side effect |

**SSRF protection**

Postiz blocks SSRF via server-side request filtering: rejects URLs resolving to private/loopback/link-local IPs. Relevant if you're fetching image URLs from brand site; safe-by-default.

Evidence: [The Cheapest and Safest Way to Host Postiz (Self-Hosted Tutorial) - DEV Community](https://dev.to/pratikpathak/the-cheapest-and-safest-way-to-host-postiz-self-hosted-tutorial-4n3g)

---

### 9. F-4 Hook: Publish-Allowlist Mapping to Postiz Integration

**F-4 Design Requirement:** "Research-only channels never connected at all" = defense-in-depth

**Allowlist concept (prose — exact syntax is an implementation decision)**

Each theme carries a publish allowlist knob, scoped per mode: in test mode the allowlist is empty (publishing wholly disabled); in staging mode it names the few content destinations where drafts are permitted (e.g. LinkedIn only at first); in live-prep mode it names every enabled content destination and additionally requires the human-approval flag. Research-only platforms (Reddit, Product Hunt, Ad Library) can never appear in any allowlist — and as defense-in-depth they are never connected as Postiz channels at all.

**Architecture mapping: allowlist → Postiz**

1. **Initialization:** at startup the app resolves the active mode's allowed-channel set from theme config.
2. **Postiz connector setup:** only the allowlisted channels for the current mode are ever initialized as Postiz integrations.
3. **Validation:** if a channel is allowlisted but its Postiz connector is not actually connected (no valid OAuth), the run **fails closed**: log the error, mark the review package as blocked for that destination, create no posts for that mode.
4. **Publish gate (the ONE enforcement point):** in test mode all Postiz calls are refused outright; in staging mode only draft-type (and never immediate-publish) requests may pass; in live-prep mode requests pass only when the human-approval requirement is satisfied.

**Defense-in-depth layers**

| Layer | Defense |
|---|---|
| **1. Config enforcement** | Allowlist specifies exactly which channels are permitted per mode |
| **2. Integration gating** | Only connect Postiz OAuth tokens for listed channels |
| **3. Publish gate** | Console app refuses to create posts if mode/allowlist conflict |
| **4. Postiz draft state** | Even if a post somehow reaches Postiz, draft state prevents auto-publishing |
| **5. Human approval** | Review package must be approved before live publish gate activates |

**Failure mode: allowlist names a channel Postiz is not connected to**

Example walked in prose: live-prep mode requests Instagram and TikTok, but only LinkedIn is actually connected in Postiz. The run refuses to proceed for the missing destinations, produces the review package with those destinations marked blocked (naming exactly which channels are missing and why), and tells the operator their three options: complete the Postiz OAuth setup for the missing channels and retry, or remove those channels from the theme allowlist and re-run, or accept the partial pack as-is. No silent skip, no silent downgrade to a different channel.

Evidence: [social media publish allowlist configuration automation safety 2026](https://blog.hootsuite.com/social-media-compliance-tools/), [Social Media Automation: Complete Guide (2026) — Mixpost](https://mixpost.app/blog/social-media-automation-guide)

---

## Decision Table

| Decision | Status | Resolution | Architecture Area |
|---|---|---|---|
| **Use Notion MCP or REST API for brand-truth cron extraction?** | UNBLOCKED | REST API (internal token) for cron; MCP for interactive testing | Brand-truth layer, cron scheduling |
| **Support unscheduled drafts in Postiz?** | UNBLOCKED | Yes; Postiz API supports `type="draft"` natively | Draft publishing, review gate |
| **Expose AI-disclosure fields in Postiz integration?** | DEFERRED (implementation phase) | Postiz does NOT expose labels; operator must manually label in each platform UI after approval | Compliance layer, operator workflow |
| **Cloud vs self-hosted Postiz for trial?** | UNBLOCKED | Cloud ($29/mo trial); same features as self-hosted, easier OAuth setup | Deployment choice, cost control |
| **Implement publish-allowlist enforcement?** | UNBLOCKED | Config-driven, 5-layer defense; validation at initialization + publish gate | Config schema, console safety |
| **Handle token expiry for unattended cron?** | UNBLOCKED | Notion REST API (static token); Postiz API key in env var | Secrets management, cron bootstrap |
| **Notion MCP rate limit sufficiency for daily cron?** | UNBLOCKED | 180 req/min Postiz MCP sufficient for 1-2 brand-truth reads/day (~10 requests) | API quota planning |
| **C2PA Content Credentials auto-labeling on TikTok?** | DEFERRED | Requires research into Kie.ai/Higgsfield.ai metadata injection capabilities | Video generation integration phase |

---

## Fact Ledger

| Claim | Source URL | Retrieved Date | Confidence | Recheck By |
|---|---|---|---|---|
| Notion MCP hosted OAuth tokens expire 3+ times per week | [OAuth token expires too frequently — requires re-authentication 3+ times per week · Issue #225 · makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server/issues/225) | 2026-08-05 | HIGH | 2026-11-05 (if no fix released) |
| Notion REST API internal integration tokens are non-expiring | [Notion API connections – Notion Help Center](https://www.notion.com/help/create-integrations-with-the-notion-api) | 2026-08-05 | HIGH | 2026-12-01 (policy change unlikely) |
| Notion MCP rate limit is 180 req/min, search capped 30/min | [Notion API Rate Limits Explained: 2026 Complete Guide \| UnBanAI](https://www.unbanai.org/blog/notion-api-rate-limits-explained-2026) | 2026-08-05 | MEDIUM | 2026-09-05 (platform may change limits) |
| Notion REST API rate limit is 3 req/sec per integration | [Request limits - Notion Docs](https://developers.notion.com/reference/request-limits) | 2026-08-05 | HIGH | 2026-12-01 (official docs) |
| Postiz supports creating posts in DRAFT status without schedule | [Create Post - Postiz Documentation](https://docs.postiz.com/public-api/posts/create) | 2026-08-05 | HIGH | 2026-10-01 (stable API) |
| Postiz cloud and self-hosted have feature parity | [12 Best Mixpost Alternative Tools for Social Media Management in 2026 - Postiz](https://postiz.com/blog/mixpost-alternative) | 2026-08-05 | HIGH | 2026-12-01 (Postiz policy) |
| Postiz self-hosted requires 2-4GB RAM, 6-9 Docker containers | [The Cheapest and Safest Way to Host Postiz (Self-Hosted Tutorial) - DEV Community](https://dev.to/pratikpathak/the-cheapest-and-safest-way-to-host-postiz-self-hosted-tutorial-4n3g) | 2026-08-05 | MEDIUM | 2026-11-05 (resource needs evolve) |
| Postiz supports 28+ platform connectors including all List B destinations | [Postiz - Comparateur-IA](https://choose-your-ai.com/ai-tools/postiz) | 2026-08-05 | HIGH | 2026-09-15 (new platforms added) |
| Postiz API does NOT expose per-platform AI-label/disclosure fields | [Public API - Postiz Docs](https://docs.postiz.com/public-api), [Postiz MCP – The Social Media MCP Server for ChatGPT & Claude](https://postiz.com/mcp) | 2026-08-05 | HIGH | 2026-10-01 (confirm by testing) |
| TikTok AIGC label is required and auto-enforced via C2PA or manual disclosure | [TikTok AI Content Policy 2026: 4-Tier Labels & Penalties](https://www.auditsocials.com/blog/tiktok-ai-content-disclosure-rules-2026) | 2026-08-05 | HIGH | 2026-09-01 (policy enforcement) |
| Meta requires AI-generated checkbox for all ads; 14% of rejections are undisclosed AI (2026) | [Meta Advantage+ AI Variant Disclosure April 2026 ... - AuditSocials](https://www.auditsocials.com/blog/meta-advantage-plus-ai-creative-variant-disclosure-april-2026-auto-generated-labeling-synthetic-watermarking-advertiser-liability) | 2026-08-05 | HIGH | 2026-10-01 (enforcement evolving) |
| Notion MCP official server maintained by Notion; 4,200+ GitHub stars; API v2026-03-11 | [GitHub - makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server) | 2026-08-05 | HIGH | 2026-12-01 (vendor support stable) |
| Postiz MCP is officially supported by Postiz with 9 tools; bearer token auth | [Official Postiz MCP Server \| Awesome MCP Servers](https://mcpservers.org/servers/postiz-mcp) | 2026-08-05 | HIGH | 2026-10-01 (active maintenance) |

---

## Sources

1. [GitHub - makenotion/notion-mcp-server: Official Notion MCP Server · GitHub](https://github.com/makenotion/notion-mcp-server) (Notion, 2026-08-05)
2. [Notion MCP Server | MCP Server](https://mcp.so/servers/mcp-notion-server) (2026-08-05)
3. [OAuth token expires too frequently — requires re-authentication 3+ times per week · Issue #225 · makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server/issues/225) (Notion GitHub Issues, 2026-08-05)
4. [Notion MCP vs Notion API for AI Agents: Which to Use](https://www.scalekit.com/blog/notion-mcp-vs-api) (Scalekit, 2026)
5. [Your Ultimate Notion API Doc Reference for 2026 | NotionSender](https://www.notionsender.com/blog/post/notion-api-doc) (NotionSender, 2026-08-05)
6. [Request limits - Notion Docs](https://developers.notion.com/reference/request-limits) (Notion Developer Docs, official, 2026-08-05)
7. [Notion API connections – Notion Help Center](https://www.notion.com/help/create-integrations-with-the-notion-api) (Notion Official, 2026-08-05)
8. [Notion API Rate Limits Explained: 2026 Complete Guide | UnBanAI](https://www.unbanai.org/blog/notion-api-rate-limits-explained-2026) (UnBanAI, 2026-08-05)
9. [Create Post - Postiz Documentation](https://docs.postiz.com/public-api/posts/create) (Postiz Official, 2026-08-05)
10. [Managing Posts - Postiz Documentation](https://docs.postiz.com/cli/managing-posts) (Postiz Official, 2026-08-05)
11. [Public API - Postiz Docs](https://docs.postiz.com/public-api) (Postiz Official, 2026-08-05)
12. [12 Best Mixpost Alternative Tools for Social Media Management in 2026 - Postiz](https://postiz.com/blog/mixpost-alternative) (Postiz Blog, 2026-08-05)
13. [Postiz Review 2026: Pricing, Features & Alternatives | Toolsplorer](https://toolsplorer.com/tool/postiz/) (Toolsplorer, 2026-08-05)
14. [The Cheapest and Safest Way to Host Postiz (Self-Hosted Tutorial) - DEV Community](https://dev.to/pratikpathak/the-cheapest-and-safest-way-to-host-postiz-self-hosted-tutorial-4n3g) (DEV Community, 2026-06 timeframe)
15. [Postiz vs Postproxy: Self-Hosted vs Managed API](https://postproxy.dev/compare/postiz/) (Postproxy, 2026)
16. [What Is Postiz? Self-Hosting Your Social Scheduling (and the Gotchas Nobody Warns You About) — Joche Ojeda](https://www.jocheojeda.com/2026/06/16/what-is-postiz-self-hosting-social-scheduling/) (Joche Ojeda Blog, 2026-06-16)
17. [How to Automate TikTok, Instagram, and YouTube Short-Form Content with AI: A Complete Workflow - Postiz](https://postiz.com/blog/how-to-automate-tiktok-instagram-and-youtube-short-form-content-with-ai-a-complete-workflow) (Postiz Blog, 2026)
18. [Postiz - Comparateur-IA](https://choose-your-ai.com/ai-tools/postiz) (Comparateur-IA, 2026)
19. [Official Postiz MCP Server | Awesome MCP Servers](https://mcpservers.org/servers/postiz-mcp) (MCP Servers Registry, 2026-08-05)
20. [Postiz MCP – The Social Media MCP Server for ChatGPT & Claude](https://postiz.com/mcp) (Postiz Official, 2026-08-05)
21. [TikTok AI Content Policy 2026: 4-Tier Labels & Penalties](https://www.auditsocials.com/blog/tiktok-ai-content-disclosure-rules-2026) (AuditSocials, 2026-08-05)
22. [AI Video Ad Disclosure Requirements 2026: Meta, YouTube, TikTok & Legal Compliance](https://virvid.ai/blog/ai-video-ad-disclosure-requirements-2026-meta-youtube-tiktok) (Virvid, 2026-08-05)
23. [AI UGC Disclosure Rules in 2026: Meta and TikTok Requirements — The Social Outline](https://thesocialoutline.com/blog/ai-ugc-disclosure-rules) (The Social Outline, 2026-08-05)
24. [Meta Advantage+ AI Variant Disclosure April 2026 ... - AuditSocials](https://www.auditsocials.com/blog/meta-advantage-plus-ai-creative-variant-disclosure-april-2026-auto-generated-labeling-synthetic-watermarking-advertiser-liability) (AuditSocials, 2026-04, reconfirmed 2026-08-05)
25. [Social Media Compliance Tools Guide 2026 | InfluenceFlow](https://influenceflow.io/resources/social-media-compliance-tools-the-complete-guide-for-2026/) (InfluenceFlow, 2026)
26. [Social Media Automation: Complete Guide (2026) — Mixpost](https://mixpost.app/blog/social-media-automation-guide) (Mixpost, 2026-08-05)
27. [MCP Protocol 2026: Build Production Servers for Claude, Cursor, VS Code Copilot](https://pooyagolchian.com/blog/mcp-model-context-protocol-production-2026/) (Pooya Golchian, 2026)

---

## Key Conclusions & Open Questions

**What works:**

1. **Notion REST API (internal token) is the path to unattended cron brand-truth extraction** — non-expiring token, full query filters, 3 req/sec rate limit is ample for daily runs. Do NOT use Notion MCP (OAuth) for cron; it will block indefinitely on expired tokens.

2. **Postiz drafts solve the publish-safety problem** — posts can live unscheduled in draft state indefinitely, giving operators time to review and approve before any publication. Cloud trial ($29/mo) is low-risk and has feature parity with self-hosted.

3. **Defense-in-depth is achievable via config-driven allowlisting** — combine Notion brand-truth retrieval, Postiz draft-first workflow, and multi-layer publish gates (config validation, mode checks, human approval) to keep cron safe by default.

**Open questions for implementation phase:**

- Can Kie.ai or Higgsfield.ai inject C2PA Content Credentials metadata into generated videos so TikTok/Meta auto-label AIGC? (Affects compliance workflow; research needed.)
- What is the exact operator workflow for manually adding AI-disclosure labels in each platform after Postiz draft creation? (UX design question; write runbook before launch.)
- Should we cache Notion brand-truth locally on cron startup to survive short Notion API outages? (Resilience vs complexity trade-off.)
- How do we handle Postiz OAuth token expiry for cloud deployment? (Likely Postiz handles rotation internally; confirm in staging trial.)
- Should publish-allowlist config support per-platform claim-type rules (e.g., "only case studies on LinkedIn, product tips on Instagram")? (Future phase; out of scope for v1.)

**Recommended next steps:**

1. **Staging trial:** Spin up test Notion workspace with brand-truth taxonomy; test Notion REST API queries and Postiz draft creation flow.
2. **Config schema lock:** Define `theme.publish_allowlist` structure and acceptance tests.
3. **Operator workflow doc:** Write step-by-step runbook for "Approve draft + add AI labels + schedule/publish."
4. **Cron bootstrap test:** Test Notion REST API + Postiz API key in a simulated 03:00 cron-like environment (no browser, no interactive prompt).

---

*Deliverable: C1_notion_postiz_integration.md*
*Date: 2026-08-05*
*Agent: T9 (API Documenter role, research mandate)*
