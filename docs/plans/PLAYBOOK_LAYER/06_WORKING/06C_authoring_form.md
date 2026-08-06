# Authoring Form — Operator Configuration Surface
*Design phase · playbook layer implementation · August 2026*

**Document status: design only. No code, no CLI syntax, no configuration file syntax.**

This document specifies what the human operator sees, writes, and understands when filling in a playbook configuration. It owns the form surface, the two-tier visibility model, the resolver readback, and two complete worked configurations ready to fill and use.

---

## Part 1: Tier-A Form — Must-Answer Questions

**Scope:** 12 fields maximum, hard ceiling. The questions are operator-facing plain language, not technical names. A first-time operator must complete these and nothing else before a first run.

Every field is bound by CR-5 from CONDUCTOR_RULINGS: no field reads "no engine default." Every field has a real, coherent default if never touched, or is identity-shaped and has no default.

### Field 1: Brand Identity — Your internal name for this playbook and brand

**Question as the operator reads it:**
> What do you call this brand, internally? (Internal identifier, no spaces, used in reports and logs.)

**Input type:** Free text, single line, 2–32 alphanumeric and dash-only characters.

**Helper text:**
> This is how the system refers to this playbook in logs and dashboards — not the public brand name. Examples: "hype-lead-gen", "restaurant-franco", "wellness-collective". Changing this later breaks report continuity, so choose once.

**Worked examples:**
- HypeDigitaly: `hype-b2b-lead-gen`
- Esoteric fixture: `luna-wellness-collective`

**What goes wrong if answered badly:**
> If you use spaces, special characters, or very short names: form rejects it and asks you to re-type. If you reuse a name that already exists: error, choose a different one. If you leave it blank: form stays in edit mode, the "Save and run" button is disabled.

**Time to answer honestly:** 2 minutes. Pick a name that describes the audience or business model. You will see it in reports.

---

### Field 2: Brand Truth Source — Where do your facts live?

**Question as the operator reads it:**
> Where does your brand keep its offers, team names, and case studies? (Point the system to your source of truth.)

**Input type:** Array of pointers (one per fact class). Each pointer is either a URL (for websites) or a source identifier (for connected systems like Notion, Slack, etc.).

**Helper text:**
> The system reads your live pricing, offers, customer names, and approved claims from here. You must point at *exactly* where each fact lives, because reading from the wrong place is how outdated claims escape.
>
> **You need:**
> - **Offers and their status** (live/retired/testing) — usually a Notion database, a product page, or a CSV
> - **Capability statements** (what this product does and does NOT do) — usually a Notion database or a feature table
> - **ICP segments and their pains** (who buys this, what do they struggle with) — usually Notion
> - **Approved claims and proof** (evidence for things you say in posts) — usually Notion
> - **CTA destinations** (the URLs that posts link to) — product page URLs, landing pages, booking systems
>
> If a source goes offline during a run, the system degrades gracefully with a named reason in the report — no silent failures.

**Worked examples:**

*HypeDigitaly:*
- Offers catalogue: `Notion: prod-market.notion.site/offers-db` (MCP read, interactive)
- Capabilities: `Notion: prod-market.notion.site/features` (MCP read)
- ICP map: `Notion: prod-market.notion.site/segments` (MCP read)
- Approved claims: `Notion: prod-market.notion.site/claim-ledger` (MCP read, empty is OK)
- CTA URLs: Config (internal — product.hype.com, app.hype.com, demo.hype.com)

*Esoteric fixture:*
- Offers catalogue: `None — this is a non-commercial content brand` (resolved-empty)
- Capabilities: `None` (resolved-empty)
- ICP map: `Config: spiritual seekers, meditation practitioners, astrology readers` (segment names only)
- Approved claims: `None` (resolved-empty — no proof claims will be made)
- CTA URLs: Config (follow links only)

**What goes wrong if answered badly:**
> If a source is unreachable (Notion offline, URL 404), the system marks it and suggests retry. If you point at the wrong Notion database or the wrong feature table, posts will use outdated or incorrect information. If you leave a required source blank: form marks the field and the configuration cannot be saved. **The system verifies liveness at every run** — if your pricing page goes down mid-week, the system notices and downgrades what it generates automatically, with a named reason in the report.

**Time to answer honestly:** 10–15 minutes. Gather your Notion URLs or site URLs for each category. If you're not using Notion: write down the exact URL of the page where that fact lives (pricing page, features page, team page). Copy-paste them carefully.

---

### Field 3: Languages

**Question as the operator reads it:**
> In which languages will this playbook create content? (Tick all that apply.)

**Input type:** Array of language codes, pick from a short list.

**Helper text:**
> The system will watch for topics, create posts, and search for proof in each language you select. Today, English and Czech are fully supported. Selecting a language means you commit to having brand truth (offers, capabilities, claims) in that language, and watch topics in that language.

**Worked examples:**
- HypeDigitaly: `cs, en` (both)
- Esoteric fixture: `en` (English only, Czech audience may not exist or may be out of scope)

**What goes wrong if answered badly:**
> If you select Czech but your Notion offers catalogue has no Czech descriptions: the system flags the gap and generates only in English that week. If you select both but forget to add Czech topic terms: discovery in Czech will find nothing, and the digest will tell you so. If you select a language and then never provide any facts in it: all-English output will run fine, but you are using a slot wastefully.

**Time to answer honestly:** 1 minute.

---

### Field 4: Watch Topics — The subjects you care about

**Question as the operator reads it:**
> What subjects should the system look for? (Name the 2–5 topics that matter most to your audience.)

**Input type:** Structured array of topic entries (one per topic). Each entry has:
- Canonical name (the topic cluster's identity)
- Surface forms per language (the actual strings sent to news feeds, search engines, social networks — not translations)
- Aliases and related terms (product names, problem names, competitor names that match this topic)
- Negative terms (the homonym-killer: what this topic is NOT about)

**Helper text:**
> The system watches social networks, news, and forums for these topics. It does **not** search for everything — it searches for *these specific things* you tell it to watch.
>
> **For each topic, provide:**
> - **The main idea** in English (e.g., "AI coding assistants")
> - **The exact phrases** people use when discussing this (not a translation, but the actual phrases: "cold outreach", "StudenĂ˝ outreach" are different, both real)
> - **What to ignore** (e.g., topic "agents" should ignore: real estate agents, sports agents, travel agents)
>
> The system will not search for your watch topics on every platform equally — some platforms don't accept keyword searches (like TikTok). That's handled automatically. Your job is to name the topics.

**Worked examples:**

*HypeDigitaly, Topic 1: Lead Generation (steered, discovery-thin)*
| Aspect | Value |
|---|---|
| **Canonical name** | lead-generation |
| **English surface form** | "lead generation", "sales pipeline", "prospecting", "cold outreach", "outbound sales" |
| **Czech surface form** | "generování leádů", "prodejní pipeline", "prospecting", "studená kontaktace", "sales outreach" |
| **Aliases & entities** | "demand gen", "lead magnet", "lead qualification", HubSpot, Outreach, Clay, Instantly |
| **Negative terms** | "lead-free" (chemistry), "leading" (sports/politics), "lead paint" |
| **Notes** | This topic is almost entirely steered (searches, ad libraries). Discovery mode will find almost nothing. Expect ranking to rely on demand data and Reddit. |

*HypeDigitaly, Topic 2: AI Coding (discovery-rich)*
| Aspect | Value |
|---|---|
| **Canonical name** | ai-coding-tools |
| **English surface form** | "AI coding", "code generation", "GitHub Copilot", "cursor", "aider", "code assistants" |
| **Czech surface form** | "AI programování", "generování kódu", "GitHub Copilot", "code assistants" |
| **Aliases & entities** | "pair programming", "coding efficiency", "developer productivity", Claude, OpenAI, Anthropic, Vercel |
| **Negative terms** | "coding interview" (job interview, not tools), "coding standards" (policy, not tools), "binary code" |
| **Notes** | Discovery-rich: Hacker News, Product Hunt, Hugging Face, Bluesky all carry real momentum. Steering sharpens. |

*Esoteric fixture, Topic 1: Astrology & Spiritual Practice*
| Aspect | Value |
|---|---|
| **Canonical name** | astrology-spirituality |
| **English surface form** | "astrology", "birth chart", "full moon ritual", "lunar phases", "Mercury retrograde", "tarot", "spiritual practice" |
| **Czech surface form** | "astrologie", "horoskop", "lunární fáze", "spiritualita", "tarotové čtení" |
| **Aliases & entities** | "Empress card", "Saturn return", "eclipse season", astrologer names or creators as needed |
| **Negative terms** | "astronomy" (science, not spirituality), "horoscope" (commercial prediction, watch for scams) |
| **Notes** | Aesthetic-rich, discovery-focused. Virlo's niche density for this topic may be high. Not steered (no cold outreach to sell). |

**What goes wrong if answered badly:**
> If you name a topic but don't provide surface forms in your chosen languages: the system searches only in English and misses local material. If your negative terms are too broad ("agent" blocks real estate agents but also "software agents" and "CIA agents"), the system filters too aggressively and misses posts. If you name topics but never provide proof/claims about them: posts will run value-only and CTAs will be weak. If you reuse the same topic word for two very different subjects (e.g., "agents" for both real-estate and AI): you must add negative terms to separate them, or create two topics.

**Time to answer honestly:** 20–30 minutes. Brainstorm what your audience cares about. Write down the phrases *they* use, not the phrases you prefer. Include product names and competitor names so the system can match them correctly. Test your negative terms by asking: "If I see this phrase in a post, should I ignore it?" If yes, add it.

---

### Field 5: Content Objective — What are posts *for*?

**Question as the operator reads it:**
> Why do you create posts? What do you want to happen when someone reads one? (Pick the primary goal.)

**Input type:** Pick from a short list of 5 options.

**Helper text:**
> Every post has a purpose. Yours is one of:
>
> - **Lead generation** — Convert readers into sales conversations. You have an offer, and posts exist to attach it to a problem the reader has. Use this if you are selling B2B software, services, or courses with a sales team behind them.
>
> - **Direct commerce** — Convert readers into buyers right now. You sell a consumable good or service people buy immediately. Use this if you run a restaurant, e-commerce shop, or services business.
>
> - **Reach & community** — Build audience and belonging. Posts exist for insight or beauty, not to sell. Use this if you are a creator, spiritual teacher, or community builder with no product to sell.
>
> - **Brand awareness** — Be remembered and differentiated. Posts exist so people recognize and like you. Use this if you build a personal or corporate brand (creator, agency, restaurant, lifestyle).
>
> - **Retention & loyalty** — Deepen relationships with existing customers. Posts justify why they should keep buying or stay engaged. Use this if you have a customer base and want to keep them.

**Worked examples:**
- HypeDigitaly: `lead-generation`
- Esoteric fixture: `reach-and-community`

**What goes wrong if answered badly:**
> If you pick "direct commerce" but have no product with real-time inventory: the system will block posts that need live stock data. If you pick "lead generation" but have no offer configured: the system degrades to research-only until you add an offer. If you pick "reach and community" but you also want to sell: the system will not attach offers to posts (by design). You can use a second playbook for that.

**Time to answer honestly:** 3 minutes.

---

### Field 6: Playbook Kind — What business model is this?

**Question as the operator reads it:**
> What *kind* of business or creator is this playbook for? (This determines what post types, voice, and CTAs are possible.)

**Input type:** Pick from a short list. The list grows over time; today there are 2.

**Helper text:**
> This setting tells the system what kinds of things to write and how to write them. Each playbook kind comes with:
> - **Post types** it uses (educational, behind-the-scenes, aesthetic, promotional, etc.)
> - **A voice** (analytical B2B, sensory food writing, evocative and artistic, etc.)
> - **CTA classes** it's allowed to use (product trials, reservations, follow buttons, engagement, etc.)
>
> You can override individual post types and voice later (Tier B), but you start with a playbook that matches your business model.

**Worked examples:**
- HypeDigitaly: `B2B-lead-generation` (or just select from the dropdown)
- Esoteric fixture: `Reach-and-community / Spiritual or Creator` (or a name like `Creative-expressive-niche`)

**What goes wrong if answered badly:**
> If you pick "B2B lead generation" but you run a restaurant: every post will assume there's a product, and you'll get offers attached to food posts. Start over and pick the restaurant playbook. If your business model is not in the list: the system will ask you to pick the closest one or create a custom playbook (which requires design review).

**Time to answer honestly:** 2 minutes. The system shows you what each playbook can do in a side-by-side table.

---

### Field 7: Destinations — Where do posts go?

**Question as the operator reads it:**
> Which platforms and channels will you publish to? (Tick all that will ever receive content from this playbook.)

**Input type:** Array of destination identifiers, pick from a list.

**Helper text:**
> The system generates posts in formats for each channel you select. Each destination has its own timing, post length, and what kinds of CTAs work there.
>
> **Common destinations:**
> - LinkedIn (long-form, professional, written and video)
> - Instagram / Reels (short video, carousel, feed posts)
> - TikTok (short video, fast pacing)
> - Facebook (community, longer video, event posts)
> - Blog / email (long-form, site-first, newsletter)
>
> You don't need to use all of them immediately. The system scales up as you add destinations.

**Worked examples:**
- HypeDigitaly: `linkedin, blog` (email distribution is secondary; TikTok will be added later)
- Esoteric fixture: `instagram-reels, tiktok, pinterest` (visual, aesthetic-first platforms)

**What goes wrong if answered badly:**
> If you tick "TikTok" but never configure a TikTok posting account: the system will generate content but can't schedule it, and you'll see a named error in the report. If you tick "LinkedIn" and later want to remove it: the system will not re-generate old content for the removed destination, but will stop making new posts for it.

**Time to answer honestly:** 3 minutes. Write down which platforms you actually use or plan to use.

---

### Field 8: Hard Excludes — What you never write about

**Question as the operator reads it:**
> Are there topics, words, or claims that must never appear in any post? (Name anything that is off-limits for this brand.)

**Input type:** Array of free-text exclusion rules. Each can be a word, a phrase, or a general rule.

**Helper text:**
> Hard excludes are things that, if they appear in a post, you reject it immediately. This is your safety rail. Examples:
>
> - A specific competitor you never name (even neutrally)
> - A claim type you don't back up (like "guaranteed results")
> - A word or phrase that sounds wrong for your brand ("hustle", "disrupt", "synergy")
> - A topic that is off-brand (a B2B company might exclude NFTs or crypto)
> - A health claim you're not licensed to make
>
> These are **unionized** — if your brand-truth source (Notion) says "exclude X" and your config says "exclude Y", the system excludes both X and Y.

**Worked examples:**
- HypeDigitaly:
  - "no health claims" (not licensed)
  - "no AI will replace humans" (contradicts brand narrative)
  - "no pricing specific to customers (confidential)")
  - "no mentions of: [named competitor]"

- Esoteric fixture:
  - "no medical claims" (not a healthcare provider)
  - "no specific astrological dates (too specific, not verifiable)"
  - "no explicit product promotion"

**What goes wrong if answered badly:**
> If you exclude a phrase too broadly (e.g., "AI" when you use AI in half your topics): every post fails the check. If you list excludes but never enforce them: they are silently ignored and do no good. If you forget to add an exclude and later regret a post: the system will have already published it. Update the excludes list, and future posts will be filtered.

**Time to answer honestly:** 10 minutes. Brainstorm what could go wrong. Include things you're not licensed to say, competitor names you don't want to name, and words that don't sound like you.

---

### Field 9: CTA Destinations That Exist — Which CTAs can actually be used?

**Question as the operator reads it:**
> For each type of call-to-action, what URLs or systems do you have set up? (Only list the CTAs you can actually deliver.)

**Input type:** Array of CTA type + destination pairs. Pick CTA types from a list and provide URLs or system names.

**Helper text:**
> A call-to-action is when a post asks the reader to do something: "Click here", "Sign up", "Book a table", "Follow us". Each CTA type needs a working destination.
>
> **CTA types** (per your playbook kind):
> - **Content** — A guide, article, or resource (provides a URL)
> - **Product-path** — A product page, trial, or demo (provides a product URL)
> - **Order / Purchase** — A shopping cart or checkout (e-commerce system)
> - **Reserve / Book** — A calendar or reservation system (restaurant booking, appointments)
> - **Follow / Save** — A social account (your Instagram, TikTok, etc.)
> - **Engage** — A poll, comment, or question (native social feature)
> - **No-CTA** — No call-to-action (just value, no ask)
>
> Only list the ones you have set up and working. If you have a product trial setup, list it. If you don't have a booking system yet, don't list it — the system will skip posts that need it.

**Worked examples:**

*HypeDigitaly:*
| CTA Type | Destination | URL / System |
|---|---|---|
| Content | Blog articles | `blog.hype.com/articles` |
| Product-path | Trial signup | `app.hype.com/trial` |
| No-CTA | Value-only | (always available) |

*Esoteric fixture:*
| CTA Type | Destination | System |
|---|---|---|
| Follow | Instagram | `@luna_wellness_collective` |
| Engage | Questions & polls | Instagram native polls |
| No-CTA | Insight-only | (always available) |

**What goes wrong if answered badly:**
> If you list a CTA type but the URL is broken or the system is offline: the system notices at pack review and removes that CTA from posts, with a named reason. If you don't list any CTA type: posts will run value-only with no calls to action — which is fine if that's intentional, but limits lead generation. If you list "product trial" but the trial system requires login credentials you haven't set up: the system will block until the CTA is actually live.

**Time to answer honestly:** 5 minutes. Check that each CTA you list actually works by clicking the link or logging into the system.

---

### Field 10: Brand Brief — A paragraph about this brand (optional but powerful)

**Question as the operator reads it:**
> Briefly describe this brand in your own words. What is it about? Who is it for? What is it *not*?
> *(Optional. Maximum 200 words. No prices, client names, or results claims.)*

**Input type:** Free text, single paragraph, maximum 200 characters. Strictly enforced: no numbers, no prices, no client names, no claim numbers or proof.

**Helper text:**
> Write as if explaining the brand to someone who's never heard of it. What problem does it solve? What makes it different? What does it believe?
>
> This is used by the system only to steer tone and voice — it does not reach posts. Think of it as "brand flavour" for the generation system.
>
> **Examples of good briefs:**
> - "We help sales teams book more meetings through intelligent lead scoring and personalized outreach."
> - "A spiritual community centered on astrology, ritual, and seasonal living. We celebrate the full moon, not just talk about it."
>
> **Examples that will be rejected:**
> - "We've generated 500 leads for our customers" (no results claims)
> - "Starting at $99 per month" (no prices)
> - "As seen in TechCrunch and recommended by [Client Name]" (no external claims)

**Worked examples:**
- HypeDigitaly: "We make lead-generation software for B2B sales teams. Our platform automates cold outreach, scoring, and follow-up. We believe in efficiency without manipulation."
- Esoteric fixture: "A spiritual community for seekers exploring astrology, ritual, and the rhythms of nature. We combine accessible education with genuine practice."

**What goes wrong if answered badly:**
> If you include a price, client name, or results claim: the system rejects it with a quoted error message and asks you to remove it. If you write more than 200 words: it's truncated and you're warned. If you leave it blank: that's fine — posts will run without this guidance.

**Time to answer honestly:** 5 minutes.

---

### Field 11: Notion MCP Connection (if using Notion for brand truth)

**Question as the operator reads it:**
> Do you use Notion for your brand facts? If yes, how does the system connect to it?

**Input type:** 
- If yes: select a pre-configured Notion workspace from a list (one-click setup, done during brand-truth setup in Field 2)
- If no: this field is skipped and hidden

**Helper text:**
> If you put your offers, capabilities, ICP segments, and approved claims in Notion, the system reads them automatically every run. One-time setup, then hands-off.
>
> If you use a spreadsheet, a database, or a manual text file instead: the system still works, but you'll manually paste/upload updated data.

**Worked examples:**
- HypeDigitaly: Connected via MCP (automatic, interactive)
- Esoteric fixture: Not connected (brand facts are kept minimal or in separate docs)

**What goes wrong if answered badly:**
> If you select a Notion workspace but never grant access: the system can't read it and degrades. If you connect to the wrong workspace: the system reads old or incorrect data. If your Notion goes down mid-run: the system gracefully falls back to offline cache (last-known facts) and flags the issue.

**Time to answer honestly:** 2 minutes (if Notion; 0 if not).

---

### Field 12: Who approved this configuration?

**Question as the operator reads it:**
> Your name and email, so the system can track who made this decision.

**Input type:** Free text email, single line.

**Helper text:**
> This is for audit and support. If something goes wrong, we know who to ask.

**Worked examples:**
- HypeDigitaly: pavlis.cermak@gmail.com
- Esoteric fixture: contact@lunawellness.com

**What goes wrong if answered badly:**
> If you enter an invalid email format: form rejects it. If you leave it blank: form stays in edit mode (required field).

**Time to answer honestly:** 1 minute.

---

## Part 2: Tier-B Surface — Tuning After First Pack

**Visibility rule:** Tier B is **hidden by default** on first load. It becomes visible **only** when:
1. An operator has one completed, reviewed pack (Tier A has been filled), **and**
2. The digest (pack summary report) surfaces a tuning opportunity with a one-line suggestion.

**Entry point:** The digest's **"Optimize" section** includes a sentence like:
> "Your posts are 80% educational; consider increasing opinion posts to match your intended 40/30/20/10 mix. [Show tuning controls]"

Clicking that link expands Tier B for that one section, or opens a Tier-B settings panel. **No operator should see Tier B before they have a first pack to review.**

---

### B1: Post-Type Mix Control

**Question as the operator reads it:**
> What mix of post types do you want? (Set the ratio, and the system tracks it over a rolling window.)

**Input type:** Guidance field (free text) + array of named post types with weights.

**How it works:**

The operator writes one sentence saying what they want, e.g.:
> "Educational 40%, promotional 30%, opinion 20%, aesthetic 10%"

The system parses this and creates a ratio. It then tracks this across a rolling window (default: last 5 packs, ~2 weeks). When generating the next pack:

1. Ranked topics are distributed to archetype slots according to the declared ratio, starting with the highest-confidence topics.
2. Each topic is tested against the archetype's safety bar. If a topic cannot deliver an archetype (e.g., speculative trend cannot be educational without proof), it downgrades to the next-best fit for that topic, and the downgrade is **recorded in the pack**.
3. If an archetype slot remains unfilled (no topics qualified), the slot is shipped as **plan-only** with a note: *"no topic suitable for [archetype] this run; 5 ranked topics available, 2 failed educational's proof bar"*.

**What does NOT happen:**
Per `01_content_ontology.md` §3 and confirmed in CONDUCTOR_RULINGS CR-1: **Thresholds are never relaxed to manufacture volume.** If you want 40% educational but only 2 good educational topics exist and 3 promotional, you ship 2 educational and 3 promotional — not a forced 3rd educational topic with a weakened proof gate.

**Field entry (guided, not free-form):**

| Archetype | Your target % | How to change it |
|---|---|---|
| Educational | 40% | Slider: 0–100% (in 5% increments) |
| Promotional | 30% | Slider |
| Opinion / hot-take | 20% | Slider |
| Aesthetic / mood | 10% | Slider |
| Behind-the-scenes | 0% | Slider |
| Product-hero | 0% | Slider |
| Listicle / ranked | 0% | Slider |
| Testimonial / proof | 0% | Slider |
| Announcement | 0% | Slider |
| Question / engagement | 0% | Slider |
| Recipe / craft / how-to | 0% | Slider |
| **Total** | **100%** | (auto-calculated) |

**Measurement window:** Last 5 published packs or 14 days, whichever is smaller.

**Worked example:**
HypeDigitaly, after 3 packs, wants to increase opinion/thought-leadership content:
- Current mix (measured): Educational 45%, Promotional 25%, Opinion 15%, Aesthetic 5%, Product-hero 10%
- New target: Educational 35%, Promotional 25%, Opinion 30%, Aesthetic 5%, Product-hero 5%
- Next pack: System prioritizes opinion-eligible topics and fills them first; if not enough, it ships educational and promotional to fill the ratio.

**What goes wrong if answered badly:**
> If your percentages don't add up to 100%: the form resets with a red error. If you set all archetypes to 0%: form rejects it (at least one must be > 0). If your target is 80% educational but topics never qualify for educational: the system degrades to 40% that run and flags it in the digest ("target unmet: 0 qualified educational topics"). The operator sees this and adjusts topic selection or archetypes.

---

### B2: Angle Control

**Question as the operator reads it:**
> Do you want to use all 15 angle types, or steer toward some and away from others?

**Input type:** Guidance field (free text, optional) + simple table.

**How it works:**

The operator can:
- **Do nothing** — all 15 angle types are equally weighted (default).
- **Write a sentence** — *"we love contrarian takes and myth-busting; avoid teaser angles"* — and the system parses this and weights accordingly.
- **Use the table below** — explicitly enable/disable or weight each angle.

**The 15 angles** (as the operator would read them, not as engineers see them):

| # | Angle type | What it does | Enable? | Weight (if enabled) |
|---|---|---|---|---|
| 1 | **How-it-works** | Explain the mechanism or process. "This is why it happens." | Y / N | Normal / Higher |
| 2 | **Myth-bust** | Correct a widespread misunderstanding. "Everyone thinks X; it's actually Y." | Y / N | Normal / Higher |
| 3 | **Step-by-step** | Procedural walkthrough. "Do X, then Y, then Z." | Y / N | Normal / Higher |
| 4 | **Problem-origin** | Reframe as "the real source of this problem is X." | Y / N | Normal / Higher |
| 5 | **Contrarian** | Assert a position opposite to received wisdom. "Everyone says X; the truth is Y." | Y / N | Normal / Higher |
| 6 | **Prediction** | Project future state. "If X continues, then Z." | Y / N | Normal / Higher |
| 7 | **Personal-narrative** | First-person story. What you or your team experienced. | Y / N | Normal / Higher |
| 8 | **Curiosity-gap** | Open a question; reader must engage to learn. "You won't believe what happened next." | Y / N | Normal / Higher |
| 9 | **Teaser** | Withhold the main point; reader must click to see. | Y / N | Normal / Higher |
| 10 | **Data-driven** | Lead with a stat or finding. "Here's what the numbers show." | Y / N | Normal / Higher |
| 11 | **Sensory-description** | Emphasize texture, taste, sound, emotion, visual richness. | Y / N | Normal / Higher |
| 12 | **Feature-highlight** | Showcase a single product capability. "This does X really well." | Y / N | Normal / Higher |
| 13 | **Urgency** | Emphasize time-scarcity or deadline. "Do this before…" | Y / N | Normal / Higher |
| 14 | **Comparison** | Pit two approaches or perspectives against each other. | Y / N | Normal / Higher |
| 15 | **Milestone** | Celebrate a win or anniversary. "We just hit 1M users." | Y / N | Normal / Higher |

**Preconditions:**
Each angle has prerequisites. If **every enabled angle fails its precondition** for a topic, the topic is downgraded to plan-only or dropped, and the digest says why.

**Example:** If you disable all angles except "data-driven", but a topic has no good stats backing it, the system cannot use data-driven and must either downgrade it or drop it.

**Worked example:**
HypeDigitaly disables "teaser" and "curiosity-gap" (because they want educational tone, not suspense). Enables all others. When generating, the system will never suggest "you won't believe what happens next" — but if a high-ranking topic would only work with that angle and curiosity-gap is disabled, the system drops the topic and flags it: *"High-potential topic 'AI API rate limits' cannot be angled without curiosity-gap (disabled for this playbook)."*

**What goes wrong if answered badly:**
> If you disable too many angles: topics become unspinnable and you get plan-only entries in your pack. If you disable "data-driven" but your playbook is data-heavy: proof claims get harder to make and confidence bands drop. If you enable all angles but disable preconditions (e.g., enable "myth-bust" but clear out your claim ledger): the angle silently cannot fire and the system falls back.

---

### B3: Voice — Tone and Personality

**Question as the operator reads it:**
> How should posts sound? (Pick a voice style, or describe your brand voice in a paragraph.)

**Input type:** Pick from 6 pre-built genres, OR write a 1–3 sentence description of voice.

**The 6 genres** (as the operator would read them):

| Genre | For playbooks like | Sounds like | Examples |
|---|---|---|---|
| **Analytical-B2B** | B2B SaaS, consulting, fintech | Sober, evidence-backed, falsifiable. Every claim is cited or sourced. Active voice. Specific language. No fluff. | "Cold outreach success rates depend on list quality. Here's what the data shows." |
| **Sensory-hospitality** | Restaurants, food/beverage, hospitality | Visceral and specific. Emphasizes texture, aroma, taste, feeling. Authentic emotion. Aspirational is OK, but specific beats vague. | "Caramelized until the edges curl, served with burnt-butter foam." |
| **Evocative-expressive** | Spiritual communities, wellness, personal creators | Resonant, authentic, meaningful. Truth is interior (feeling, insight) not empirical. Vagueness that evokes shared understanding is acceptable. | "The autumn equinox reminds us that all things cycle. What are you ready to release?" |
| **Creator-casual** | Creators, influencers, UGC agencies, personal brands | Conversational, irreverent, insider language. Breaks the fourth wall. Calls out absurdity. Direct address. | "Okay so every algorithm change I've survived, and here's the one thing that always works." |
| **Product-persuasive** | E-commerce, direct commerce, product launches | Confident, benefit-focused, outcome-oriented. Reader should want to own or use this. "You" framing. Clear benefit + urgency if real. | "This saves your mornings. Set it up once, it runs itself." |
| **Educational-structured** | Courses, tutorials, how-to communities, training brands | Clear, methodical, teachable. Steps are numbered, concepts build logically. Specificity on *how*, not just *what*. | "Step 1: Measure. Step 2: Design. Step 3: Test. Here's why that order matters." |

**Alternatively: Write your own voice description**

If none of the above fit, write 1–3 sentences:
> "We sound playful but expert. We name specific tools and numbers. We make complex things simple without dumbing down. We use humour to make hard truths easier to swallow."

The system will parse this and apply it to generation, flagged as a custom voice. **Custom voices are calibrated per-genre**, so the first time you use a custom voice, you get a note: *"First-run custom voice: flag-rate ceiling inactive. This voice will be measured on your first 5 packs and calibrated then."*

**Worked examples:**
- HypeDigitaly: `analytical-b2b`
- Esoteric fixture: `evocative-expressive` (or custom: "We celebrate the sacred, the mundane, and the in-between. Practical spirituality, not dogma.")

**What goes wrong if answered badly:**
> If you pick "analytical-B2B" but you run a spiritual community: posts will sound corporate and cold. If you pick "creator-casual" but you're a law firm: posts will sound unprofessional. If you write a custom voice that is contradictory: the system flags it and asks you to clarify ("sounds playful but also serious" is unclear). The dialect library checks for Czech-specific voice requirements (tykání vs vykání, formal vs informal register); the system will validate voice against language.

---

## Part 3: Progressive Disclosure and First-Time Experience

### The operator's journey:

**Step 1 — First load (no config exists):**
> Operator sees only Tier A (12 fields, clean, no clutter). Page says: "Fill in this information once, and we'll start generating content next week."

**Step 2 — First pack review (after Tier A is complete):**
> Operator gets a digest (report) showing what the system created. At the bottom of the digest, a new section called **"Optimize your mix"** appears, with one specific suggestion:
>
> *"Your first pack included: 5 educational, 2 promotional, 1 opinion. Our recommendation is 40% educational, 30% promotional, 20% opinion, 10% aesthetic. To adjust, click here."*
>
> Clicking "here" scrolls to **Tier B** and reveals the B1 post-type mix control, pre-filled with the detected ratio from the pack.

**Step 3 — Ongoing tuning:**
> After the first pack, Tier B remains visible whenever the operator returns to configuration. Each digest includes one or two specific tuning recommendations based on what was produced and what was targeted.

### What the operator never sees unless they ask:

- Knob tables
- Node names or pipeline details
- "Resolver" concepts
- Configuration file formats
- Technical architecture

---

## Part 4: Two Shipped Configurations

Both configurations are written out in full as filled-in forms, Tier A and Tier B complete, for immediate use.

---

### Configuration (a): HypeDigitaly — The Default, Behaviour-Preserving

**Status:** Production configuration. Reproduces today's designed behaviour exactly per `05_query_steering.md` §6.1 and MASTERPLAN §2.

**Tier A: Must-Answer Questions**

| Field | Answer | Rationale |
|---|---|---|
| **1. Brand Identity** | `hype-b2b-lead-gen` | Internal name, used in reports. |
| **2. Brand Truth Source** | **Offers:** Notion MCP, `prod-market.notion.site/offers-db` (status filter live/testing/retired) **Capabilities:** Notion MCP, `prod-market.notion.site/features` **ICP map:** Notion MCP, `prod-market.notion.site/segments` (segments with pains and platform) **Approved claims:** Notion MCP, `prod-market.notion.site/claim-ledger` (empty is OK; operator may add claims as they are proved) **CTA URLs:** Config pointers: product.hype.com, app.hype.com, demo.hype.com | All from Notion. Notion is the single source of truth for offers and capabilities. Claim ledger starts empty (no pre-existing proof body). CTAs are internal, config-verified. |
| **3. Languages** | `cs, en` | Czech and English. Brand truth must exist in both languages (or is explicitly resolved-empty for Czech if operator hasn't translated yet). Topics provided per language. |
| **4. Watch Topics** | See detailed topic table below | Three topics: **Lead generation** (steered, discovery-thin), **AI coding** (discovery-rich), **AI agents** (discovery-rich). Per `05_query_steering.md` §6.1: AI coding and AI agents rely on discovery (Hacker News, Product Hunt, Virlo); lead generation is nearly steered-only (demand data, ad libraries). |
| **5. Content Objective** | `lead-generation` | Convert reader attention to qualified prospect contact. Spin gate emphasizes connection chain (S-3) and distance compliance (S-4). CTA vocabulary centered on product-path and commercial-incentive (if claims are proved). Ranking may weight lead-indicator signal. |
| **6. Playbook Kind** | `B2B-lead-generation` (or: "HypeDigitaly / B2B SaaS lead gen") | Selects: relation type R-1 (offer-attachment), archetypes (educational, listicle, opinion, product-hero, testimonial), CTA classes (content, product-path, commercial-incentive), voice genre (analytical-B2B). |
| **7. Destinations** | `linkedin, blog, email` | LinkedIn (long-form, professional, video-ready). Blog (long-form, site-first). Email (newsletter, text-heavy). TikTok marked for future. Instagram/Reels not yet in scope. |
| **8. Hard Excludes** | • "no health claims" (not licensed) • "no AI will replace humans" (contradicts brand strategy) • "no confidential pricing" (customer-specific deals) • "no mention of: [named competitor]" | Safety rails. Union with Notion excludes. Updated weekly as brand strategy evolves. |
| **9. CTA Destinations** | **Content:** blog.hype.com/articles **Product-path:** app.hype.com/trial (trial signup page) **Commercial-incentive:** (none yet; no discount programme active) | Content and Product-path are live and tested. No commercial-incentive until a discount/affiliate programme is set up and added to the claim ledger with terms and valid-from/until. |
| **10. Brand Brief** | "We make B2B lead-generation software for sales teams. Our platform automates outbound prospecting, lead scoring, and follow-up sequences. We believe in efficiency without manipulation and transparency in how our tools work." | Guides tone (sober, specific, evidence-backed). Does NOT reach posts; used by generation system for context. No prices, no claims. |
| **11. Notion MCP** | Connected (interactive read/write via MCP during brand-truth setup). | Automated fact fetching every run. Offers, capabilities, segments, claims all pulled fresh. Offline fallback (last-known snapshot) if Notion is down. |
| **12. Approval** | pavlis.cermak@gmail.com | Audit trail. |

**Watch Topics — Detailed Table**

*Topic 1: Lead Generation (Steered, Discovery-Thin)*

| Aspect | Value |
|---|---|
| Canonical name | `lead-generation` |
| English surface form | "lead generation", "sales pipeline", "prospecting", "cold outreach", "outbound sales", "demand gen" |
| Czech surface form | "generování leádů", "prodejní pipeline", "prospecting", "studená kontaktace", "sales outreach", "demand gen" |
| Aliases & entities | "lead magnet", "lead qualification", "sales funnel", HubSpot, Outreach, Clay, Instantly, Apollo |
| Negative terms | "lead-free" (chemistry), "leading" (sports/politics), "lead paint", "leading edge" (technology term unrelated to outreach) |
| Per-source overrides | Google News CZ: "vedení leádů"; DataForSEO: "lead generation + sales"; Virlo: intent = "B2B lead generation strategies" |
| Notes | Nearly 100% steered (demand data, ad library search). Discovery mode contributes <5%. Expect to see this topic mostly from Reddit, Meta ads, LinkedIn, and manual keyword searches. |

*Topic 2: AI Coding (Discovery-Rich)*

| Aspect | Value |
|---|---|
| Canonical name | `ai-coding-tools` |
| English surface form | "AI coding", "code generation", "GitHub Copilot", "cursor", "aider", "code assistants", "pair programming", "developer productivity" |
| Czech surface form | "AI programování", "generování kódu", "GitHub Copilot", "code assistants", "produktivita vývojářů" |
| Aliases & entities | Claude, OpenAI, Anthropic, Vercel, JetBrains, VS Code extensions, LLM-as-IDE |
| Negative terms | "coding interview" (job preparation, not tools), "coding standards" (policy/compliance), "binary code", "coding bootcamp" (education, not tools) |
| Per-source overrides | Hacker News: `q=coding+AI`, tags=`story,front_page`; Product Hunt: `topic=developer-tools`; Hugging Face: `search=code generation` |
| Notes | High discovery signal. Hacker News, Product Hunt, Hugging Face, Bluesky all carry real momentum. Steering (DataForSEO keyword search) sharpens but does not originate. |

*Topic 3: AI Agents (Discovery-Rich)*

| Aspect | Value |
|---|---|
| Canonical name | `ai-agents` |
| English surface form | "AI agents", "autonomous agents", "agent framework", "agentic AI", "multi-agent systems", "LLM agents" |
| Czech surface form | "AI agenti", "autonomní agenti", "agentic AI", "vícagentní systémy" |
| Aliases & entities | CrewAI, Anthropic (Claude agent APIs), AutoGPT, BabyAGI, LangChain agents, ReAct, LLM frameworks |
| Negative terms | "real estate agents", "sports agents", "travel agents", "agent provocateur", "agent (espionage)" |
| Per-source overrides | Bluesky: `q=AI agents`, `lang=en`; Virlo: intent = "emerging AI agent frameworks and tools"; Hugging Face: repos tagged with "agents" |
| Notes | Emerging topic with high discovery momentum. May see rapid topic-cluster rotation as new frameworks launch. Keep negative terms updated. |

**Tier B: Tuning (Visible after first pack)**

| Field | Answer | Rationale |
|---|---|---|
| **B1: Post-type mix** | Educational 40%, Promotional 30%, Opinion 20%, Aesthetic 5%, Product-hero 5% | Leads with education (thought leadership). Promotional is direct but not dominant (lead-gen can lead with value). Opinion for authority. Minimal aesthetic (not the brand voice). Minimal product-hero (B2B SaaS, not consumer). Measurement window: last 5 packs (≈2 weeks). |
| **B2: Angle control** | All 15 angles enabled. Higher weight on: how-it-works, myth-bust, data-driven, contrarian, feature-highlight. Lower weight (normal) on: curiosity-gap, teaser, sensory (doesn't fit voice). | B2B SaaS values mechanism clarity and proof. Contrarian angles for thought leadership. Sensory angles are rare (not food, not lifestyle). Curiosity-gap discouraged but not banned (may soften for opinion posts). |
| **B3: Voice** | `analytical-b2b` | Sober, evidence-backed. Every claim sourced or in the ledger. Active voice. Specific language. No hype. No "you won't believe this" (hard contradiction of analytical tone). |

---

### Configuration (b): The Esoteric Fixture — Falsification Probe

**Status:** Fixture for falsification per `00_MASTERPLAN.md` PB-OD-1. **NOT RUN AT A REAL AUDIENCE** until the Prohibited-Outcome Gate (Amendment A) has been exercised in review. This playbook is designed to break B2B assumptions. **Fields that would be legally dangerous if run:**
- Field 10 (brand brief) — spiritual claims without medical licensing
- Field 8 (hard excludes) — must include health-claim exclusions
- No offers, no ICP, no commercial claims allowed

**Tier A: Must-Answer Questions**

| Field | Answer | Rationale |
|---|---|---|
| **1. Brand Identity** | `luna-wellness-collective` | Internal name. Spiritual/wellness niche. |
| **2. Brand Truth Source** | **Offers:** None (resolved-empty; no product) **Capabilities:** None (resolved-empty) **ICP map:** Config only — "spiritual seekers", "meditation practitioners", "astrology readers" (segment names, no pain mapping; pains don't apply to non-transactional content) **Approved claims:** None (resolved-empty; no proof claims will be made; relational objective is R-3 expressive and R-4 commentary, neither of which requires proof) **CTA URLs:** Instagram follow (@luna_wellness_collective), Pinterest save (native), no product URLs | **FIXTURE SAFETY MECHANISM:** No offers, no product paths, no pricing. CTA restricted to follow/engage only. This breaks every B2B assumption. |
| **3. Languages** | `en` | English only. Czech audience may not exist or may be out of scope for a spiritual wellness brand. Topic terms provided in English. If Czech expansion happens later, topics would be created with Czech surface forms. |
| **4. Watch Topics** | See detailed topic table below | Two topics: **Astrology & Spirituality** (aesthetic, discovery-rich), **Wellness Practices** (lifestyle, discovery + some steering). Both are aesthetic/expressive, not transactional. |
| **5. Content Objective** | `reach-and-community` | Build audience, engagement, belonging. Posts earn attention for insight or aesthetic worth, not to sell. Spin gate softens distance-compliance (S-4) — no offer required. CTA vocabulary limited to engagement (follow, comment), no-CTA. Proof discipline disabled (S-5). Hype-glue rule (S-7) waived for aesthetic archetype. |
| **6. Playbook Kind** | `creative-expressive-niche` (or: "Spiritual / Creator / Community-first") | Selects: relation types R-3 (expressive-aesthetic), R-4 (commentary), R-6 (education, limited); archetypes (aesthetic, personal-narrative, opinion, commentary, engagement, behind-the-scenes); CTA classes (follow, engage, no-CTA); voice genre (evocative-expressive). |
| **7. Destinations** | `instagram-reels, tiktok, pinterest` | Visual, aesthetic-first platforms. No blog (long-form not needed). No LinkedIn (B2B, off-audience). Email not configured (low volume, community-first not newsletter). |
| **8. Hard Excludes** | • "no health claims" (not a healthcare provider; "meditation reduces anxiety" is not approved) • "no medical advice" (e.g., don't recommend crystals as treatment) • "no diagnosis claims" • "no specific birth-chart readings for people" (too specific, not verifiable) • "no commercial products without explicit permission" | **LEGALLY CRITICAL.** Spiritual content is at risk of health-claim regulation. Hard excludes must be strict and actively enforced. |
| **9. CTA Destinations** | **Follow:** Instagram (@luna_wellness_collective) **Engage:** Instagram native polls and comment (no external form) **No-CTA:** Available for insight-only posts | Zero product or transactional CTAs. All CTAs are engagement or no-CTA. |
| **10. Brand Brief** | "A spiritual community for people exploring astrology, ritual, and the rhythms of nature. We celebrate the full moon, honor seasonal changes, and practice living aligned with cosmic cycles. We make spirituality accessible and grounded, not commercial." | Guides tone (evocative, poetic, authentic). **NOTE: No health claims, no healing guarantees, no commercial promises.** This is the safety checkpoint. If the operator writes health claims here, the system rejects the config. |
| **11. Notion MCP** | Not connected. | Minimal brand facts. No Notion needed for a community-first, non-commercial brand. |
| **12. Approval** | contact@lunawellness.com | Audit trail. |

**Watch Topics — Detailed Table**

*Topic 1: Astrology & Spirituality (Aesthetic, Discovery-Rich)*

| Aspect | Value |
|---|---|
| Canonical name | `astrology-spirituality` |
| English surface form | "astrology", "birth chart", "full moon ritual", "lunar phases", "Mercury retrograde", "tarot", "spiritual practice", "seasonal living" |
| Czech surface form | (not provided; English-discovery-only) |
| Aliases & entities | "Empress card", "Saturn return", "eclipse season", "astrologer", creator names (if permission granted); no commercial product names |
| Negative terms | "astronomy" (science, not spirituality), "astrology app scams", "commercial horoscope prediction" |
| Per-source overrides | TikTok: search term "spirituality + astrology"; Instagram: hashtags #astrology #fullmoonritual; Pinterest: boards on "lunar living"; Bluesky: trending spiritual topics (discovery only, no keyword) |
| Notes | Aesthetic-rich, discovery-focused. Virlo's niche density likely high for this topic (emerging trend platform with strong wellness/spiritual coverage). No steered component; purely discovery-based. |

*Topic 2: Wellness Practices (Lifestyle, Mixed)*

| Aspect | Value |
|---|---|
| Canonical name | `wellness-practices` |
| English surface form | "meditation practice", "breathwork", "ritual", "self-care", "mindfulness", "embodied practice", "grounding", "chakra" |
| Czech surface form | (not provided) |
| Aliases & entities | "Yoga", "Reiki" (mentions only; not promoted), creator/practitioner names with permission |
| Negative terms | "medical treatment", "therapy" (clinical), "cure", "guaranteed results" |
| Per-source overrides | TikTok: #meditation, #breathwork, #mindfulness; Instagram: wellness creator searches; Pinterest: "wellness routine" boards |
| Notes | Mixed discovery (trends on TikTok/Instagram) and some steered search (meditation + breathwork). Not brand-specific; universal wellness topic. Low velocity — not a trending spike topic, but steady audience interest. |

**Tier B: Tuning (Visible after first pack)**

| Field | Answer | Rationale |
|---|---|---|
| **B1: Post-type mix** | Aesthetic 40%, Personal-narrative 30%, Opinion 20%, Engagement 10%, Educational 0% | Aesthetic-first (brand voice). Personal stories build connection. Opinion for authority and thought leadership (e.g., "why astrology is misunderstood by science"). Engagement (polls, questions) for community. Educational avoided (risk of teaching health practices or medical claims). No product-hero, no promotional, no behind-the-scenes (not relevant). |
| **B2: Angle control** | All angles enabled. Highest weight on: sensory-description, personal-narrative, curiosity-gap, teaser. Lower weight on: data-driven (no metrics to cite), feature-highlight (no products), urgency (not aligned with mindful brand). | Evocative tone loves sensory angles. Curiosity-gap and teaser are **native to this genre** and encouraged (unlike B2B). Personal narrative builds community. Data-driven angles rare (aesthetic content doesn't need stats). |
| **B3: Voice** | `evocative-expressive` | Resonant, authentic, meaningful. Truth is interior (feeling, insight) not empirical. Vagueness that evokes shared understanding is acceptable — "What does balance mean to you?" is good practice. No data required; emotional coherence required. |

**FIXTURE SAFETY DECLARATION:**
This playbook is a falsification fixture. It does not represent a paying customer. **It is not run at a real audience until the Prohibited-Outcome Gate (Amendment A, A1) has been exercised in design review.** The operator must explicitly acknowledge this before scheduling any run:

> "This is a non-commercial spiritual/wellness community. Posts created here make no health claims and carry no offers. I understand this is a fixture for testing edge cases, and I will not publish without explicit approval from legal review."

---

## Part 5: What the Operator Cannot Do

Stated clearly where the operator will look for it.

### You cannot write free-prompt instructions into gate nodes.

**Why:** Gate nodes make safety-critical decisions (is this a valid claim? does the CTA link work?). If the operator writes instructions, they can launder an invalid claim or override safety checks.

**What to do instead:** Use the brand brief (Field 10, Tier A) to guide *tone* and *style* for generation nodes only. Use Tier-B voice selection to pick from pre-built genres. Write your hard excludes (Field 8) as specific banned phrases or topics.

### You cannot disable the five non-disableable check classes.

**Why:** These are legal safety floors (numeric claims, prices, entities, endorsements, required disclosures). Disabling them puts you at regulatory risk.

**What to do instead:** Fill out your claim ledger with all the numbers you want to use. Add required disclosures to Field 10. Ensure every claim has an evidence pointer.

### You cannot create new archetypes or angles.

**Why:** Every archetype and angle has defined safety bars and preconditions. An operator-invented archetype has no bars, and posts would use it without safety gates.

**What to do instead:** Use the 11 archetypes and 15 angles provided. If none fit your need, file a feature request (product-manager reviews, designs the bars, adds it to the engine, then it becomes available to all playbooks).

### You cannot set per-axis ranking weights or per-relation-type score overrides.

**Why:** Ranking weights are uncalibratable (no golden set exists to measure them against). A custom weight you think improves results actually introduces drift you cannot see.

**What to do instead:** Use ranking profiles (pre-built combinations of criteria emphasis) if your playbook supports multiple profiles. If your ranking needs are special, request a custom profile design (done at play book build time, not per-run).

### You cannot write new relation types or claim-pack variants.

**Why:** Relations and claim packs are engine-level registries. A new relation type interacts with distance rules, spin criteria, and fact classes. Operator-authored relations would have no validated bars.

**What to do instead:** Pick from the five relation types your playbook supports. If you need a relation that doesn't exist, request it at playbook design time.

### You cannot relax the Prohibited-Outcome Gate.

**Why:** The gate blocks content that would be unlawful (e.g., unauthorized health claims, misleading product depictions). It runs before the claim ledger and cannot be overridden.

**What to do instead:** Ensure your hard excludes and brand brief do not include unlawful claims. If a claim is important to you, work with legal review to get it authorized (by a regulator or by your business counsel), add evidence to the claim ledger, and submit a bounded brief for approval.

### You cannot disable AI disclosure.

**Why:** EU AI Act (and Czech law) require disclosure that content is AI-generated. Disabling it is non-compliance.

**What to do instead:** All AI-generated content carries the disclosure automatically. You can choose the phrasing (if multiple variants exist in your language), but you cannot turn it off.

---

## Part 6: Open Design Questions (CFG-OD-n)

### CFG-OD-1: Per-topic brand-brief override

**The question:**
Should the operator be able to write a brand-brief paragraph for a specific topic (e.g., "when you generate content about our new product, emphasize X"), or does every topic get the playbook-wide brand brief?

**Recommendation:**
**Not in v1. Defer.** Per-topic briefs are powerful but create a decision tree at run time that is hard to audit. v1 ships with one playbook-wide brief (Field 10). **If an operator wants topic-specific tone, they use Tier-B angle control or post-type control** to steer generation. A topic that consistently needs different voice is a signal that it should be a separate playbook.

---

### CFG-OD-2: Visible confidence-band targets in the form

**The question:**
Should the operator see target confidence bands (e.g., "aim for FULL band 80% of the time, PARTIAL 20%")? Or is the band a diagnostic-only output?

**Recommendation:**
**Diagnostic-only in v1.** The band is computed per run and shown in the digest. The operator sees it, but does not set it. This keeps configuration focused on identity and strategy, not on internal safety mechanics. If an operator's goals consistently don't match the band (e.g., "we want FULL band but our brand truth is spotty"), that's a signal for interview-based playbook improvement, not a form knob.

---

### CFG-OD-3: Czech genre calibration corpus

**The question:**
Who authors the Czech exemplar corpus for each genre (e.g., Czech golden examples of evocative-expressive voice)? When?

**Recommendation:**
**Defer to Phase 0 extension.** Analytical-B2B and the operator's chosen playbook #2 get Czech corpora during Phase 0 build. Other genres are registered but marked as "calibration pending" with inactive flag-rate ceilings. Cost is added to PB-OD-3. Author: `content-marketer` (Czech-native, linguistic expertise). Measure: first 5–10 packs per genre per language.

---

### CFG-OD-4: Brand-brief leakage checking

**The question:**
The brand brief (Field 10) is checked for proof-shaped and numeric content (CR-8). Should it also be checked for competitor names, prices, or other sensitive data?

**Recommendation:**
**Yes, extend CR-8's leakage check.** Add to the rejection list: competitor names (matched against hard excludes), prices (any number with a currency symbol or payment term), client names (checked against proof allowlist), case metrics (numbers paired with outcome words). Same readback: *"Brief contains 'saved 3 customers $50k' — remove the metric or provide evidence."* This keeps a casual operator from accidentally leaking confidential information into the form.

---

## Contradictions Found

**CTA class count inconsistency** (from 01_content_ontology.md):
- Table §6 says 10 classes (rows: content, product-path, order/purchase, reserve/book, subscribe/join, visit/directions, follow/tag/save, share/comment/tag, engage-via-response, no-cta)
- Prose §6 summary lists "ten CTA classes"
- BUT: `01_content_ontology.md` §1 (Worked examples, section 9.1) states "CTA classes = content, product-path, commercial-incentive" (3 total for that playbook)

**Resolution used:** The table in §6 is canonical (10 classes). The 3-class description in §9.1 is a *subset* of enabled classes for that playbook, not the total universe. A playbook picks which of the 10 classes it uses; `ARCHITECTURE_PLAN.md` §6.9 calls this "CTA class selector" and lists 4 in the current config. The unified count is 10 classes, of which every playbook uses a subset.

**Post archetype count mismatch:**
- Section §3 names 11 archetypes (Educational, Promotional, Behind-the-scenes, Proof/testimonial, Opinion/hot-take, Aesthetic/mood, Announcement, Listicle/rank, Question/engagement, Recipe/craft, Product-hero)
- Section §9.1 (walkthrough) uses only 5 archetypes for HypeDigitaly (educational, listicle, opinion, product-hero, testimonial)

**Resolution used:** 11 is canonical. Each playbook declares which archetypes it uses; unused archetypes are never triggered. HypeDigitaly uses 5 of 11; other playbooks use different subsets.

---

## Summary

**Tier-A field list (12 fields, must-answer):**
1. Brand Identity (internal name)
2. Brand Truth Source (pointers to offers, capabilities, ICP, claims)
3. Languages (array of language codes)
4. Watch Topics (structured topic entries with surface forms per language)
5. Content Objective (pick 1 of 5)
6. Playbook Kind (pick 1 of 2+ available)
7. Destinations (array of platforms)
8. Hard Excludes (array of banned phrases/topics)
9. CTA Destinations That Exist (array of CTA type + URL pairs)
10. Brand Brief (optional, max 200 words, no prices/names/claims)
11. Notion MCP Connection (if using Notion)
12. Approval Contact (email)

**Tier-B fields exposed (3 fields, tuning after first pack):**
1. Post-type mix (11 archetypes, weighted)
2. Angle control (15 angle types, enable/disable + weight)
3. Voice (6 genres or custom description)

**Open questions with recommendations:**
- CFG-OD-1: Per-topic brand-brief override → Defer v1
- CFG-OD-2: Visible confidence-band targets → Diagnostic-only v1
- CFG-OD-3: Czech genre calibration corpus → Phase-0 extension, cost noted
- CFG-OD-4: Brand-brief leakage checking → Recommend extend CR-8 checks
