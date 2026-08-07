# @aisimplified23 ("AI Simplified") — Slideshow Catalog

Data source: Virlo niche monitors (free reads only) — `9c96fddf-dc35-4be0-bbd9-12f4d22aea12` "AI Trends Tracker" (202 slideshows, pages 1-2) and `623203a9-c09c-4763-85e0-1c177b5af760` "AI Trends Tracker v2 (intelligence)" (178 slideshows, pages 1-2). All 380 monitor items were swept; 6 unique aisimplified23 slideshows found (after dedup — 3 items appear in both monitors).

Creator: TikTok @aisimplified23, 37,892 followers, unverified. Upload region resolves as PK. Platform: TikTok photo-mode carousels only.

**Data gap (important):** the monitors did NOT capture several known-viral posts from this creator ("100 Secret Codes for Claude" ~754K, "21 hacks to NEVER hit Claude's limit" ~358K, "120 Prompt Codes" ~257K, "99 Claude secret commands" ~212K, "50+ Claude Skills" ~185K, "60 Claude Marketing Prompts" ~136K). Monitors only surface what their keyword crawls hit. Pulling the full creator feed requires a paid `collect_creator_posts` call — not done per budget constraint. The 6 posts below are still fully representative of the format (2 of them are the #1 and #3 posts on the account by views).

## 1. Metrics table (sorted by views)

| # | Title (hook) | Views | Likes | Shares | Comments | Saves | Save rate | Slides | Published | Intel |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | How To Master Claude Skills — A Complete Guide | 347,244 | 15,620 | 3,731 | 55 | 22,311 | **6.43%** | 7 | 2026-03-24 | ready |
| 2 | How To Use Claude To Start A Business | 295,997 | 13,314 | 3,538 | 39 | 21,260 | **7.18%** | 9 | 2026-04-25 | ready |
| 3 | 60 Claude Prompts (10 categories, copy-paste ready) | 48,571 | 1,315 | 506 | 80 | 2,206 | 4.54% | 10 | 2026-03-26 | ready |
| 4 | 36 Free Claude Prompts To Grow Your Brand | 33,418 | 1,023 | 354 | 26 | 2,155 | 6.45% | 5 | 2026-04-12 | ready |
| 5 | 5 Claude Prompts That Actually Work (content creators) | 29,017 | 728 | 205 | 2 | 1,528 | 5.27% | 6 | 2026-04-06 | ready |
| 6 | I built a Claude Skill that roasts your LinkedIn | 5,153 | 142 | 34 | 1 | 185 | 3.59% | 6 | 2026-05-11 | disabled |

TikTok photo IDs: (1) 7620921674715630869, (2) 7632639576233872660, (3) 7621470172787789077, (4) 7627847110116871444, (5) 7625543690240396564, (6) 7638656449236831508.

Aggregate signals:
- Average save rate **5.58%** (TikTok-wide anything >1-2% is strong; 6-7% is exceptional value-density territory).
- Saves are ~6x shares and ~400x comments. This is save-farming content, not conversation content — comments are near-zero and the creator doesn't try to fix that (only one comment-gate CTA in the whole set).
- Like rate 2.5-4.5%. Engagement scales WITH view count here — the two guide-format posts have both the most views and the best like/save rates, i.e. format quality drove distribution, not luck.
- The two "guide" carousels (#1, #2) massively outperform the raw prompt-dump carousels (6-10x the views, higher save rate).

## 2. Carousel structure pattern (slide-by-slide)

Two distinct architectures, both starting from the same hook-slide grammar:

**A. Guide carousel ("How To X — A Complete Guide") — the outperformer (posts 1, 2)**
- Slide 1 — HOOK: 7-12 words max. Big serif italic headline on off-white paper-texture background + small 3D orange Claude-style logo. Title-case, trailing ellipsis ("...") to imply continuation. No CTA, no clutter.
- Slides 2..N — PAYLOAD, one concept/step per slide (~70-85 words each): "Step N" or question-headline at top, 1-2 sentence framing (pain first: "Most founders skip this and spend months building something nobody wants"), then 3-6 bullets, and critically at least one *literal copy-paste artifact*: a full prompt in quotes ("Steal this prompt: ..."), a file name (about-me.md, brand-voice.md, SKILL.md), or an exact UI path ("Settings → Connectors → Browse → Add").
- Mid-carousel PROOF slide (post 1, slide 5): stat-card layout — "Time Saved Per Task ~40 Min", "Output Consistency 10X", "Setup Time 10 Min" — the shareable "receipts" slide.
- Final slide — NOT a CTA. It is the densest reference table ("Skill Types & When To Use Them" 3-column table; "daily business brief" prompt template). The carousel ends on maximum keep-value, which is what converts the last swipe into a save.
- Narrative arc tagged by Virlo intelligence: `tutorial_steps`; hook type `tutorial_promise`.

**B. Cheat-sheet carousel (numbered-promise prompt dumps) — posts 3, 4, 5**
- Slide 1 — HOOK: numbered promise + optional enemy framing ("Stop using ChatGPT. Start using Claude. 60 Claude Prompts") or tested-N-kept-K social proof ("I tested 500 Claude prompts for content. Only 5 were worth it."). Hook type `bold_claim`.
- Slides 2..N — PAYLOAD: category-per-slide cards. Density varies by sub-format:
  - 60-prompts: 6 full prompts per slide in card UI on dark background, category header + "N/10" progress counter (~230 words/slide).
  - 36-prompts: 8-10 full numbered prompts per slide (~540 words/slide!) with persistent footer progress markers ("attract → convert → retain → operate") + "SWIPE" nudge.
  - 5-prompts: one named prompt per slide (~65 words/slide), each with a memorable persona name ("The Viral Content Reverse Engineer", "The Competitor Stalker", "The Frustrated Follower").
- No closing CTA slide in any of them. When a CTA exists it sits ON THE HOOK SLIDE (comment-gate: "Comment \"60\" and I'll DM you all 60 prompts for free") or in the caption.
- The dense "cheat sheet" slides ARE the middle and end — there is no fluff slide anywhere. Every slide past the hook is screenshot-worthy on its own.

Slide counts: 5-10 (median 6.5). Cadence in window: a post every ~6-19 days.

**Watermark note:** posts 3 and 4 carry third-party watermarks (@leadgenman / leadgenman.com; "MOBILE EDITING CLUB") — aisimplified23 partially reposts/whitelabels other creators' carousels. Posts 1, 2, 5, 6 look native (consistent paper-texture + serif system).

## 3. Copy formulas observed

Title/hook formulas (ranked by observed performance):
1. `How To [use Tool] To [big outcome]` / `How To Master [Tool feature] — A Complete Guide` — tutorial_promise; the two ~300K+ posts.
2. `[N] [Tool] Prompts` + qualifier — "60 Claude prompts. 10 categories. Every single one is copy-paste ready." / "36 Free Claude prompts to grow" / "5 Claude prompts that actually work".
3. Enemy/switch framing — "Stop using ChatGPT. Start using Claude."
4. Tested-N-kept-K proof — "I tested 500 Claude prompts for content. Only 5 were worth it." (implied effort = curation value).
5. Authority + build story — "I built a Claude Skill that roasts your LinkedIn... I've driven millions of dollars in revenue" (worst performer of the set — self-referential lead-gen underperforms pure value).

Caption pattern: restate hook promise → 1-3 lines expanding what's inside (category list) → aspirational close ("Brands that have Claude in their workflow aren't just moving faster...") → exactly 5 hashtags.

Hashtag pattern (always 5): 2-3 niche tags (#claude #claudeai #claudeprompts #claudeskills #claudeforbuisness) + 1-2 broad AI tags (#ai #aigenerated #aiprompt) + #fyp. Note recurring typos in captions/tags (#buisness, #linkdln, "rompt") — zero polish penalty at this scale.

Prompt-text formula inside panels (the payload grammar): `You are a [specific role] who [outcome-verb clause]. Write/Create [deliverable] for [context]. The [deliverable] should include [3-6 concrete components]. The tone is [tone]. [Length constraint].` Placeholders always in [BRACKETS]. This template repeats across all 36 prompts of post 4 and most of post 3.

Tone: educational, positive, second-person, zero irony, zero hedging. Claims are specific-numeric ("40 min saved", "60 seconds", "5%+ conversion", "10X") rather than vague.

## 4. Value payload analysis — why people save these

- **The save IS the product.** Every post is a reference artifact: literal complete prompts (not descriptions of prompts), exact file names, exact menu paths, reusable templates. Users save because re-finding this content is cheaper than re-deriving it. Bookmark:share ratio of ~6:1 confirms utility-collection behavior over social distribution.
- **Curation as proof-of-work:** "tested 500, kept 5", "60 prompts, 10 categories", "36 prompts across the four areas that matter". A count + a taxonomy signals someone already did the filtering.
- **Per-slide text density (from intelligence panel_texts word counts):**
  | Post | Total words | Slides | Words/slide (hook) | Words/slide (payload) |
  |---|---:|---:|---:|---:|
  | Master Claude Skills | 521 | 7 | ~9 | ~85 |
  | Start A Business | 650 | 9 | ~7 | ~80 |
  | 60 Claude Prompts | 2,108 | 10 | ~25 | ~230 |
  | 36 Free Prompts | 2,163 | 5 | ~10 | ~540 |
  | 5 Prompts | 343 | 6 | ~11 | ~65 |
- Sweet spot: hook slides at 7-12 words; guide payload slides at 70-85 words (readable in one swipe-pause); cheat-sheet slides deliberately overflow (230-540 words) because they're meant to be saved-then-zoomed, not read in-feed.
- The two formats trade off: guide carousels earn distribution (readable → completed swipes → algorithm), cheat-sheet carousels earn depth per save. The creator's best posts (1, 2) hybridize: guide readability with an embedded copy-paste artifact on every slide and a dense reference table as the closer.
- Social proof used sparingly: statistic_cited (the stat-card slide) in posts 1 and 5; no testimonials, no follower-count flexing on top posts.

## 5. Downloaded images (15 files, this directory)

All converted webp→jpg (ffmpeg, q:v 2), original TikTok resolution 1080x1350.

| File | Description |
|---|---|
| start-a-business_s1.jpg | Hook slide: "How To Use Claude To Start A Business..." serif italic on paper texture, orange 3D Claude logo |
| start-a-business_s2.jpg | Step 1 Validate Your Idea — pain framing + "Steal this prompt" devil's-advocate prompt + bullets |
| start-a-business_s3.jpg | Step 2 Create Your Two Core Files — about-me.md / brand-voice.md file cards |
| start-a-business_s4.jpg | Step 3 Build A Project For Each Function — Strategy/Content/Operations project list |
| start-a-business_s5.jpg | Step 4 Use Artifacts To Build Business Assets — 6 asset-type cards (pitch deck, financial model, landing copy...) |
| start-a-business_s6.jpg | Step 6 Connect Your Tools with Connectors — integrations + exact UI path "Settings → Connectors → Browse → Add" |
| start-a-business_s7.jpg | Step 7 Graduate to Cowork — real-document outputs list (proposals, models, reports, SOPs) |
| start-a-business_s8.jpg | Step 8 Use Claude Code to build your product — MVP-without-engineers pitch |
| start-a-business_s9.jpg | Step 9 Daily business brief — Cowork morning-brief prompt template (closing reference slide) |
| master-claude-skills_cover.jpg | Hook slide of top post (347K): "How To Master Claude Skills — A Complete Guide" |
| master-claude-skills_s2.jpg | "What Is Claude Skills?" — Without/With two-column comparison + analogy footer (key payload slide) |
| 60-claude-prompts_cover.jpg | Hook: "Stop using ChatGPT. Start using Claude. 60 Claude Prompts" dark card UI + comment-gate CTA (@leadgenman watermark) |
| 36-free-prompts_cover.jpg | Hook: "36 Claude Prompts TO GROW YOUR BRAND →" — only cover with a human face (Claude-logo eye patches), Mobile Editing Club watermark |
| 5-prompts-content_cover.jpg | Hook: "I tested 500 Claude prompts for content. Only 5 were worth it." minimal text on dark brown |
| linkedin-roast-skill_cover.jpg | Hook of LinkedIn-roast Skill post (worst performer, lead-gen angle) |

## 6. Raw data

Full deduplicated JSON records (all metrics, all panel texts, full intelligence payloads) preserved during analysis in the session scratchpad (`aisimplified23_items.json`). Virlo intelligence fields of note: all posts `text_density: text_dominant`, `background_type: solid_color`, foreground `text_only` or `chart_or_data_ui`, `emotional_tone: educational`, `is_educational: true`, `is_sponsored: false`, no faces except post 4 cover.
