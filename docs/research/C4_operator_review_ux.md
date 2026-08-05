# C4: Operator Review UX — Research Brief

## What This Means for the Operator

You are a solo marketer reviewing a cron-generated research and content package each morning. Instead of opening 12 files and tracing rankings backward, you will open ONE digest that tells you at a glance:
- Which viral topics were found, why they ranked, and how confident the research was (presented so you can audit without a data science degree)
- Exactly how much media spend the pack will burn if approved (critical with only $50 Kie.ai credits)
- Which topics are new vs. repeats from yesterday (dedup & freshness)
- Your approval flow for ~5 topics × 2 languages × up to 6 asset destinations in under 30 minutes
- How to reject just the video but keep the copy, or request a reel variant with specific feedback
- What gets packaged for later Notion upload when you're ready

The gate is clean: **review research + cost forecast FIRST, then approve media generation** — not the other way around. No budget burned on reel variants you don't want.

---

## 1. Operator Walkthrough: First Touch & Review Journey

### A. The First Artifact — Daily Run Digest (Single Page, ~2 min read)

The operator's entry point is a **Run Digest** — a single-page HTML or Markdown summary opened in a browser or text viewer. It is neither a long report nor a scattered file tree, but a **scannable dashboard** showing:

**Header** (30 seconds):
- Run ID / date / time run executed
- Theme name (e.g., "HypeDigitaly AI & Sales")
- Total topics researched | topics ranked for review | deduplicated count vs yesterday
- **COST FORECAST SUMMARY** (prominent): "5 topics × 2 languages × 6 asset sets = ~$15 estimated media cost (30% Kie.ai trial budget remaining)"
- Status: "Research approved. Awaiting media generation approval."

**Topic List** (90 seconds):
A table with one row per ranked topic. Each row shows:
- Topic title & virality rank (1–5)
- Brand-fit score & confidence band (e.g., "8.2/10 ±0.4, Medium Confidence")
- Freshness: "NEW" or "Repeat from Tue 2026-08-03" with link to yesterday's digest
- Platforms: LinkedIn, X, TikTok (icon labels)
- Decision button: "APPROVE & GENERATE" / "SKIP" / "DETAILS"

**Footer** (30 seconds):
- Link to detailed research file (optional deep dive)
- Cost breakdown by topic (expandable)
- Regeneration queue (if any topics failed previous attempts)
- "Approve All & Generate Media" button (batch action)

### B. Full Review Journey — Ordered Steps (Total: 15–30 min for 5 topics)

**Step 1: Scan Digest (2 min)**
Open Run Digest. Scan topic titles and confidence bands. Identify any red-flag freshness issues (e.g., topic repeated 3 days in a row = potential audience fatigue).

**Step 2: Spot-Check 1–2 Topics (5 min)**
Click "DETAILS" on a medium-confidence topic to verify research was sound:
- See the 2–3 sources that ranked it (Reddit thread link, X trend, news article)
- See the extraction method (API, search, Playwright scrape with timestamp)
- See the rank computation: virality signal (tweets/day, Reddit upvotes) × brand-fit penalty/boost × freshness decay (days old)
- Brand fit explained in plain language (e.g., "Topic is 'AI agents for sales automation' → maps to HypeLead offer, ICP pain alignment strong")

**Step 3: Review Cost Forecast (3 min)**
Click "Cost breakdown by topic" table:
- Topic 1: "AI video generation" | 2 reels (Kie.ai) + 1 carousel (static) + 4 posts (LLM) | ~$6 estimated
- Topic 2: "Lead scoring with Claude" | 2 reels + 1 carousel + 4 posts | ~$6
- Topic 5: "Cold email open rates" | 1 reel + carousel + posts | ~$3
- **Total forecast: ~$15 (Remaining trial: $35)**
- Forecast includes: per-model iteration cost (1 iteration per video assumed), per-carousel slide generation (Kie.ai ~$2/3 slides), post copy via LLM (~$0.01 per topic)
- Caveats: "Iteration count from confidence band. If you request variants, cost will increase."

**Step 4: Batch Decision (4 min)**
Option A (simple): Click "Approve All & Generate Media" → all topics, all languages, all platforms → proceed to media generation.
Option B (selective): Use topic-level toggles to skip Topics 3 & 4 (low confidence, crowded markets) → approve & generate the rest.
Option C (feedback): For Topic 2, click "FEEDBACK" → open a feedback form with fields:
  - "Approve copy & posts? YES"
  - "Request video changes?" → text field "Make it less technical, focus on pain of manual scoring"
  - "Approve carousel?" → toggle OFF (skip carousel for this topic)
  - Click "Submit & Regenerate"

**Step 5: Approve Media Generation (2 min)**
System shows: "You have approved 4 of 5 topics. Approved media generation for ~$14 cost. Proceeding with Kie.ai (2 reels) + carousel slides + LLM posts. You will be notified when media is ready for review (usually 5–10 min)."
Operator can choose: "Generate Now" or "Generate at 2 PM Today" (optional scheduling).

**Step 6: Media Ready → Second Review (5 min, when media arrives)**
Operator receives notification. Opens **Media Review Package**:
- For each topic: copy visible, carousel layout preview, reel scripts + keyframe stills
- Operator skims, looking for: brand voice (reads one post aloud — does it sound like a human?), visual coherence (stills match script tone), no invented metrics
- Toggles: "Approve Copy" / "Approve Video" / "Reject Video, Keep Copy" / "Request Variant"
- Batch action: "Approve All for Publishing Prep"

**Step 7: Publish Prep (2 min)**
System creates a **Publishing Package**:
- Copy + media + captions (in Czech & English)
- Platform delivery instructions (LinkedIn carousel, X thread format, TikTok 15s reel, etc.)
- Staging note: "Ready for manual upload to Postiz drafts or direct social posting. No auto-live-publish in this version."
- Exporting note: "All assets, metadata, and sources ready for Notion upload if desired."

---

## 2. "Research Was Sound" Judgment Without Data Science

A marketer does not need to be a data scientist, but **must** be able to audit the research in <5 minutes.

### A. Confidence Band Presentation

**Format:** Numeric score + visual confidence indicator + plain-language reason.

Example for a topic:
```
VIRALITY RANK: #2 (8.5/10 ± 0.3 confidence)

[===== ••••• ] High Confidence
Reason: Trending on both X (1,200 tweets/day) and Reddit 
(/r/startups, 450 upvotes). Published 2 days ago (fresh).
```

Example for a lower-confidence topic:
```
VIRALITY RANK: #4 (6.1/10 ± 0.8 confidence)
[ === ••••••• ] Medium-Low Confidence
Reason: Strong Reddit signal (250 upvotes) but aged 5 days.
X trend not yet confirmed (single influencer mention, 
40 retweets). May peak soon or may fade.
```

**What "confidence" means operationally:**
- High (>7.5, ±0.3): 2+ independent signals (e.g., Reddit + X + news mention), published within 48 hours, multiple voices discussing.
- Medium (6–7.5, ±0.5): 1 strong signal + 1 weaker signal OR 1 strong signal but older (3–7 days). Brand fit is clear.
- Low (<6, ±0.8+): Single source only, or brand fit requires a stretch, or topic is 7+ days old (may be fading). Flag for operator judgment.

### B. Source Links & Extraction Method

Every ranked topic includes a **source card** with:
- **Reddit thread**: "r/startups / 'Claude agents for sales outreach / best practices'" | Link | Extracted: 2026-08-05 via API | 450 upvotes, 78 comments | Age: 2 days
- **X trend**: "Thread by @paul_graham / 'AI for lead scoring is the next frontier'" | Link | Extracted: 2026-08-05 via search / Playwright | 1,200 retweets, 450 replies | Age: 1 day
- **News mention**: "SambaNova Series C, $1.65B / mentions agent orchestration for enterprise" | Link | Extracted: 2026-08-04 via API (TechCrunch RSS) | Age: 2 days

Each source shows:
- How it was extracted (API, search result, Playwright browse, RSS feed)
- Extraction timestamp (auditability)
- Raw metrics (upvotes, retweets, comments, word count)
- Age in days

### C. Brand-Fit Sub-Score (ASSUMED INPUT from Brief B3)

Brief B3 (owned by parallel agent) provides sub-scores. C4 presents them in operator-friendly format:

```
BRAND FIT: 7.9/10 ± 0.2 (HIGH)

Topic: "AI agents for sales outreach"
Maps to: HypeLead product (outbound sales automation)
ICP resonance: Matches sales ops manager persona (pain: manual cadence management)
Opportunity: High relevance to Q3 "lead scoring + agents" campaign

Soft CTA fit: Natural tie-in — "See how agents reduce manual work" (product page link)
Risk: Topic trending in enterprise/GTM, not startup founder segment (secondary ICP)
Confidence in map: High (MCP brand truth confirms HypeLead positioning)
```

### D. Operator Audit Checklist (Visible in UI)

Quick questions the operator can answer in <2 min:

- [ ] Are the sources real and recent (within 7 days)?
- [ ] Does the virality signal (tweet/upvote count) seem genuine (not a bot-amplified anomaly)?
- [ ] Is the brand fit explained without forcing? (Would I write about this topic without the product?)
- [ ] Is the confidence band honest about uncertainty?
- [ ] If this topic is a repeat, what changed since yesterday? (e.g., new news, engagement spiked)

---

## 3. Publish/Skip Decision Flow — ~5 Topics × 2 Languages × 6 Platforms in <30 min

### A. Why 30 Minutes Is Feasible

**Batch architecture reduces latency:**
1. **Digest scan** (2 min) → one read, all topics visible at once
2. **Selective approval** (4 min) → toggles per topic; skip low-confidence ones
3. **Cost gate** (3 min) → operator sees spend before generation; stops runaway iterations
4. **Media review** (5 min) → operator skims copy/stills (not deep read); trusts LLM phrasing passed voice QA
5. **Batch publish prep** (2 min) → system assembles all platforms at once (no per-platform manual work)
6. **Buffer** (12 min) → unexpected clarifications, re-reads, coffee

**Total effort:** ~28 minutes for a fully reviewed, multi-language, multi-platform pack.

### B. Decision Tree (Ordered by Speed)

```
START: Operator opens Run Digest (2 min)
│
├─ QUICK PATH (80% of runs):
│  ├─ Scan topics. All look good (confidence >7, no repeats, brand fit clear).
│  ├─ Check cost forecast. Within budget.
│  └─ Click "APPROVE ALL & GENERATE" → Done (4 min)
│
├─ SELECTIVE PATH (15% of runs):
│  ├─ Scan topics. Topic 4 has lower confidence (6.2). Skip it.
│  ├─ Toggle OFF for Topics 4 & 5.
│  ├─ Click "APPROVE SELECTED & GENERATE" → Done (6 min)
│
├─ FEEDBACK PATH (5% of runs):
│  ├─ Topic 2 is good but needs tone adjustment.
│  ├─ Click "FEEDBACK" → fill "Make less technical, focus on founder pain."
│  ├─ System generates variant (new scripts, new media plan) → comes back in 5 min.
│  ├─ Operator re-checks cost (variant iterations bump estimate $2–3).
│  ├─ Approves variant. Generate.
│  └─ Total time: 12 min (5 min initial review + 5 min variant wait + 2 min approval)
│
└─ RARE PATH (5% of runs):
   └─ Cost forecast shows $45 estimated spend (>$40 budget). Operator rejects 2–3 topics.
      OR research quality is poor (multiple low-confidence topics). Halt, request re-run.
```

### C. Batch Operations (Default to Operator Benefit)

By default, the system offers **batch operations** that save per-platform, per-topic decisions:

- **"Approve all topics × all languages × all platforms"**: One click. System knows to create posts for LinkedIn, X, TikTok (+ Czech & English variants per config).
- **"Skip video-only for Topics 1–3, keep copy/posts"**: One toggle-and-click, not six separate decisions.
- **"Generate media now, publish prep at 2 PM"**: Async, so operator doesn't wait for video generation to complete.
- **"Batch reject just the video carousel, regenerate with feedback"**: Operator fills one feedback form; system applies to all variants of that topic.

### D. Default Ordering (Minimize Decisions)

The Run Digest orders topics by **decision confidence**, not virality:
1. **Tier 1 (8.5–10 confidence)**: Pre-approved by default (checkbox is ON). Operator unchecks only if suspicious.
2. **Tier 2 (7–8.5 confidence)**: Checkbox OFF by default. Operator checks if convinced.
3. **Tier 3 (<7 confidence)**: Greyed out / "Low Confidence — Review Details Before Approval". Operator must click DETAILS before they can approve.

This ordering minimizes "decision fatigue" — operator approves high-confidence topics first, builds confidence, then scrutinizes edge cases.

---

## 4. Diffs vs Yesterday: Dedup Visibility & Freshness Metadata

### A. Topic Deduplication Logic

**The Problem:** If Topic "AI agents for sales" ranked yesterday AND today, the operator needs to know:
- Is this a **repeat** (same topic from same sources)?
- Or a **new angle** (same topic but new news, engagement spike, different ICP angle)?
- Or **fatigue risk** (this topic 3 days in a row → audience may be tired)?

**The Solution: Run Digest shows dedup status for each topic:**

```
TOPIC: "AI agents for sales outreach"
RANK: #1 | Confidence: 8.7/10
FRESHNESS: ⚠️ REPEAT from Tue 2026-08-03
         └─ View previous pack
         └─ Engagement change since yesterday:
             • X: +18% retweet velocity (was 800/day, now 950/day)
             • Reddit: stable (still 450 upvotes, 2 new comments)
         └─ NEW signal: SambaNova Series C announcement (yesterday) added enterprise credibility

OPERATOR INSIGHT:
This topic is NOT stale — engagement spiked and new credible news arrived.
Previous audience already saw this topic; recommend new angle or skip if audience fatigue is concern.
```

### B. Freshness Metadata Per Topic

Each topic entry includes:
- **Recency score**: Days since topic was first published (1 = published today, 7+ = older)
- **Engagement trajectory**: Stable, Rising, Falling, Spiked (in last 24h)
- **Source spread**: # of independent sources mentioning topic (prevents single-influencer anomalies)
- **Repeat history**: "Seen 1× before (Tue), 0× before that" OR "First time"
- **Audience fatigue risk**: Automatic flag if same topic in queue >2 days in a row or "viral saturation" in ICP circles detected

### C. Linking to Yesterday's Pack

Each topic row in the Run Digest includes a link to yesterday's digest AND to the asset that was generated:

```
└─ Yesterday's pack [link]
   └─ Assets created:
      • LinkedIn post: "AI agents just changed how we score leads" (23 reactions in first 4h)
      • X thread (47 retweets, 12 replies, 1 quote-tweet)
      • TikTok reel: [Video]
```

This gives the operator **visibility into what worked**: if yesterday's "AI agents" post got high engagement, today's repeat may actually be smart (capitalize on momentum). If it flopped, skip it.

---

## 5. Cost Forecast Before Media Generation (Critical Design Gate)

This is the **existential constraint** due to Kie.ai trial ($50 credits only).

### A. The Gate: Research Approval → Cost Forecast → Media Generation Approval

**Step-by-step flow:**

1. **Cron run completes research + ranking** (no media generation yet).
2. **System produces Run Digest** with cost forecast embedded.
3. **Operator reviews research** (topics, sources, confidence bands, brand fit).
4. **Operator checks cost forecast**: "5 topics × 2 languages × [6 platforms, 3 asset types per platform] = ~$15 media cost."
5. **Operator decision**: 
   - "Approve Research & Generate Media" → proceed to media gen within cost cap
   - "Approve Research Only, Defer Media" → package saved, no media spend yet (useful if low on budget)
   - "Reject Topics 4–5, Approve Rest" → selective generation
6. **If approved, system proceeds to media generation** (and ONLY THEN does it start burning Kie.ai credits).

### B. The Forecast Artifact (Detailed Cost Breakdown)

**Visible in Run Digest, expandable:**

```
COST FORECAST — Media Generation Budget

Approval Status: PENDING MEDIA GENERATION
Estimated Cost: $14.50 (Trial Budget Remaining: $35.50)

Breakdown by Topic:
┌─────────────────────────────────────────────────────────────┐
│ Topic                    │ Assets              │ Cost (USD) │
├─────────────────────────────────────────────────────────────┤
│ 1. AI agents sales      │ 2 reels + 1 carousel + 4 posts   │ $6.00  │
│ 2. Lead scoring Claude  │ 2 reels + 1 carousel + 4 posts   │ $6.00  │
│ 3. Cold email open rate │ 1 reel  + 1 carousel + 4 posts   │ $2.50  │
└─────────────────────────────────────────────────────────────┘

Cost Assumptions:
• AI reel generation (Kie.ai): $2.50 per reel (includes 1 iteration)
• Carousel slide generation: $0.50 per carousel (3 slides, static)
• LLM post copy: ~$0.01 per topic (batch token cost)
• No video editing / manual asset purchase assumed

Iteration Contingency:
If you request variants or regenerations during media review,
cost will increase (~$1–3 per additional iteration).

Approval Gate:
[ ] I acknowledge this cost and approve media generation.
    [ ] Generate Now
    [ ] Schedule Generation (e.g., 2 PM today)
    [ ] Defer (I'll approve later)
```

### C. What Forecast Includes (Transparency)

The forecast must decompose costs to prevent surprises:

**Per-topic costs:**
- Reel generation cost (based on script length, keyframe count, Kie.ai model tier)
- Carousel generation cost (based on # slides, Kie.ai image model)
- Post copy cost (LLM token estimate for all platform variants)
- Metadata/caption generation cost (minor)

**Caveats:**
- "Iteration cost assumes 1 attempt per asset. If you request regeneration, add $1–3 per attempt."
- "Multi-language cost: Czech + English parity (no additional per-language markup, just duplication of token cost)."
- "Kie.ai pricing as of [date]. Subject to provider rate changes."

**Not included (for transparency):**
- Future Postiz API calls (draft creation) — currently free in test mode
- Storage/backup costs — negligible
- Manual edit time (counted as operator effort, not AI cost)

### D. Budget Cap & Overflow Handling

**Config-level setting:** "Maximum media cost per run: $20" (operator can override).

**Behavior:**
- If forecast > cap, system flags topics in rank order for exclusion:
  ```
  ⚠️ BUDGET ALERT: Forecast ($18.50) would exceed your cap ($20).
  To stay within budget, exclude Topic 5 (saves $2.50).
  Proceed with Topics 1–4?
  ```
- If operator tries to approve over-budget, system warns:
  ```
  ⚠️ Approval would cost $23 against a $20 cap.
  Your trial will be depleted by 2026-08-12.
  Do you want to:
  [ ] Approve anyway (proceed to depletion)
  [ ] Scale back topics (use AI to pick best 4)
  [ ] Cancel this run
  ```

### E. Approve-Research-Then-Generate (NOT Generate-Then-Review)

**Why this matters:**
- **Current anti-pattern** (dangerous): Generate all media first, operator reviews, rejects $12 of video → too late, budget burned.
- **Correct pattern** (this design): Operator sees cost estimate, approves research & budget, THEN media generates.

**Implementation:** 
- Research completion → produce digest + forecast.
- Operator approves research (toggles topics, checks budget).
- Only THEN does the pipeline call Kie.ai / Higgsfield.ai.
- If media fails, retry only approved topics (no budget on unapproved).

---

## 6. Rejection & Regeneration Request Flow

### A. Rejection Scenarios

**Scenario 1: "Reject just the video, keep the copy"**

Operator is reviewing media. X platform post looks great. But the TikTok reel feels too technical.

Action:
1. In Media Review, toggle TikTok reel: "REJECT VIDEO, KEEP COPY"
2. System flags: "Copy approved for X + LinkedIn. Video rejected for TikTok. Regenerate TikTok reel?"
3. Operator optionally fills feedback: "Make it less code-heavy, focus on business pain (time wasted on manual lead scoring)."
4. System estimates cost: "Regenerate TikTok reel with feedback: +$2.50 (iteration cost)."
5. Operator confirms.
6. New reel generated, comes back for quick re-check.
7. Operator approves reel. All assets (old posts + new reel) go to publishing prep.

**Scenario 2: "Topic research is weak, reject entire topic"**

Operator skimming media. Post for Topic 4 feels forced (topic is "GraphQL performance optimization" — weak brand fit to HypeLead sales).

Action:
1. Operator clicks "REJECT TOPIC" on Topic 4 media.
2. System shows: "Topic 4 research confidence: 5.8/10. Brand fit: 5.2/10. This topic will be excluded from publishing package. Future runs will deprioritize similar signals."
3. Operator confirms.
4. Topic 4 removed from pack. Cost credit of ~$2.50 returned to running total.

**Scenario 3: "Entire media pack quality is low, request full re-run"**

Operator opens media review. Multiple posts have corporate-slop language. Copy reads like AI marketing mush.

Action:
1. Operator navigates to pack overview.
2. Clicks "REJECT PACK, REQUEST RE-RUN WITH FEEDBACK."
3. Form appears:
   ```
   Global Feedback (applies to all topics):
   [ ] Voice is too corporate. Make it conversational.
   [ ] Too many CTAs per post.
   [ ] Hashtag usage feels forced.
   [ ] [Custom feedback] _______________
   ```
4. Operator selects "Voice is too corporate" + fills custom: "Reference real pain (lost opportunity, wasted time), not generic benefits."
5. System acknowledges: "Pack rejected. Research preserved. Re-generating all media with voice feedback applied to prompts."
6. New media comes back in ~5 min.
7. Operator re-reviews (usually faster, since research didn't change).

### B. Feedback Capture (For Learning Loop)

Every rejection captures feedback:

```
FEEDBACK RECORD:
Run ID: 2026-08-05-0800-hypedigitaly
Topic: AI agents for sales
Asset: TikTok reel (original)
Feedback: "Make it less technical, focus on business pain."
Operator: [logged-in user]
Timestamp: 2026-08-05 09:45
Action: Regenerate TikTok reel

OUTCOME:
New reel approved? YES
Time to approval: 3 min
Feedback effectiveness: POSITIVE (operator approved faster second time)
```

**Where feedback goes:**
1. **Immediate loop:** Used to regenerate current pack (as shown above).
2. **Weekly loop:** Aggregated feedback informs prompt library refinements (e.g., "60% of rejections cite 'corporate voice' — boost conversational tone in all voice prompts").
3. **Theme tuning:** Over time, this feedback trains the ranking/spin thresholds (e.g., "Topics with brand-fit <6.5 frequently rejected — lower approval threshold").

### C. Regeneration Tracking (Queue Visibility)

If a topic fails during generation (e.g., Kie.ai API timeout), it appears in a **Regeneration Queue** on the next digest:

```
REGENERATION QUEUE:
Run ID: 2026-08-05-0800
Topic 2 reel generation failed (Kie.ai timeout).
Retry attempt 1 of 3.
Last attempted: 2026-08-05 09:15
Next auto-retry: 2026-08-05 10:15
Operator options:
[ ] Retry now
[ ] Retry with reduced quality tier (faster)
[ ] Skip (use static carousel for this topic instead)
```

This ensures operator is never blind to failures.

---

## 7. Pack Anatomy: Conceptual Contents

One full review package (after a cron run) contains:

### A. Research Layer (Populated Immediately)

```
REVIEW_PACKAGE/
├─ run_digest.html [OPERATOR ENTRY POINT]
│  ├─ Header (run ID, date, theme, cost forecast, status)
│  ├─ Topic list (rank, confidence, freshness, brand fit, sources)
│  └─ Batch action buttons (approve, skip, feedback, generate)
│
├─ research_detail.md
│  ├─ Topic 1
│  │  ├─ Virality signal breakdown (X tweets/day, Reddit upvotes, news mentions)
│  │  ├─ Source citations with extraction method + timestamp
│  │  ├─ Ranking math: (virality signal × brand-fit multiplier) / age_decay
│  │  ├─ Brand-fit sub-score (from Brief B3): product match, ICP resonance, CTA fit
│  │  ├─ Confidence band derivation: signal spread, source age, brand confidence
│  │  └─ Dedup note: if repeat, link to yesterday's assets + engagement data
│  │
│  ├─ Topic 2
│  └─ ... (one section per ranked topic)
│
├─ sources_raw.json [AUDIT TRAIL]
│  └─ Structured log of every extraction:
│     {
│       "source": "Reddit r/startups",
│       "extraction_method": "Playwright",
│       "extraction_timestamp": "2026-08-05T07:30:00Z",
│       "url": "https://reddit.com/r/startups/comments/abc123",
│       "metrics": { "upvotes": 450, "comments": 78 },
│       "age_days": 2,
│       "extracted_text": "Thread title: 'AI agents for sales automation...'"
│     }
│
└─ automation_metadata.json [CRON AUDITING]
   {
     "run_id": "2026-08-05-0800-hypedigitaly",
     "theme": "HypeDigitaly",
     "mode": "test",
     "extraction_duration_sec": 45,
     "ranking_duration_sec": 12,
     "total_candidates_found": 187,
     "candidates_ranked_top_10": 10,
     "candidates_for_review": 5,
     "api_calls_made": { "reddit": 2, "twitter": 1, "techcrunch_rss": 1 },
     "cost_estimate": 14.50,
     "status": "research_complete_awaiting_approval"
   }
```

### B. Media Layer (Generated ONLY After Operator Approves Research)

```
MEDIA_PACKAGE/
├─ topic_1/
│  ├─ copy.md
│  │  ├─ [CZECH]
│  │  │  ├─ LinkedIn post (300 words)
│  │  │  ├─ X thread (5 tweets)
│  │  │  ├─ TikTok script (60 words, spoken)
│  │  │  └─ Captions (for silent viewing)
│  │  └─ [ENGLISH]
│  │     └─ (same structure)
│  │
│  ├─ carousel_plan.md
│  │  ├─ Slide count: 5
│  │  ├─ Slide 1: [Description] "Hero text: 'AI agents just changed sales.'"
│  │  ├─ Slide 2: [Description] "Problem statement with stat"
│  │  └─ Slide 5: [Description] "CTA slide with product link"
│  │
│  ├─ reel_plan.md
│  │  ├─ Duration: 45 sec
│  │  ├─ Hook (0–3 sec): "What if you never manually scored a lead again?"
│  │  ├─ Problem (3–20 sec): Show frustration of manual work
│  │  ├─ Solution (20–40 sec): Demo of agent scoring
│  │  ├─ CTA (40–45 sec): "Learn more" + product link
│  │  ├─ Keyframe images (stills from proposed video)
│  │  └─ Music/VO notes: "Upbeat, modern tone. VO optional."
│  │
│  └─ brand_check.md
│     ├─ Claims validated: ✓ No invented metrics
│     ├─ Voice tone: ✓ Conversational, not corporate
│     ├─ Product mention: ✓ Soft CTA, not spammy
│     ├─ ICP resonance: ✓ Matches sales ops persona
│     └─ Flag if any: (empty if passed)
│
├─ topic_2/
│  └─ (same structure)
│
└─ media_status.json
   {
     "topic_1_copy_czech": "generated",
     "topic_1_copy_english": "generated",
     "topic_1_carousel": "generation_in_progress",
     "topic_1_reel": "queued_for_kie_ai",
     ...
   }
```

### C. Publishing Prep Layer (Final Output After Approval)

```
PUBLISHING_PACKAGE/
├─ ready_to_post.md [SUMMARY]
│  ├─ LinkedIn: 5 assets (1 long post, 1 carousel, 1 video)
│  ├─ X: 5 threads
│  ├─ TikTok: 5 videos (+ optional VO)
│  ├─ All in Czech & English
│  └─ Staging: "Ready for Postiz draft upload or direct manual posting"
│
├─ postiz_staging/ (optional, if Postiz integration enabled)
│  ├─ linkedin_01_long_post.csv [Fields: content, image_url, cta_link, publish_date]
│  ├─ linkedin_01_carousel.csv
│  └─ ...
│
├─ direct_posting/ (if operator wants manual upload)
│  ├─ linkedin_topic_1_cz.txt
│  ├─ linkedin_topic_1_en.txt
│  ├─ x_thread_topic_1_cz.txt
│  └─ ...
│
└─ notion_export.json (optional Notion upload)
   {
     "database": "Social Content Calendar",
     "records": [
       {
         "topic": "AI agents for sales",
         "platform": "LinkedIn",
         "language": "Czech",
         "content": "...",
         "asset_url": "s3://...",
         "published_date": "2026-08-05",
         "engagement_tracked": false
       }
     ]
   }
```

### D. Mapping to Later Notion Upload (D-07)

The **Notion schema** that the operator may choose to use later will import directly from `notion_export.json`:

| Column | Source in Package |
|--------|-------------------|
| Topic | research_detail.md → Topic title |
| Platform | media_package → directory structure |
| Language | media_package → [CZECH] / [ENGLISH] folder |
| Content | copy.md → post text |
| Media Link | s3:// URL (if video/carousel generated) |
| Run ID | automation_metadata.json → run_id |
| Operator Approved | user interaction log |
| Engagement (after posting) | (tracked separately in Notion later) |

The package is designed so **zero data re-entry is required** for Notion import. Operator can export once and have full audit trail.

---

## 8. Ground in Real HITL/Content-Review Patterns

### A. Key Patterns from Industry Practice

**Pattern 1: Confidence-Gated Routing**
- Source: Velt HITL workflow guide (2026)
- Application: High-confidence topics (>8.5) are pre-checked for approval. Medium (6–8.5) are unchecked. Low (<6) are greyed out and require drill-down.
- Benefit: Operator approves 80% of topics in one click, saving decision fatigue.
- Risk: Automation bias (if confidence scoring is wrong, operator won't catch it). Mitigation: Show top 2–3 sources inline on digest; operator can spot-check.

**Pattern 2: Contextual Review UI**
- Source: Velt HITL, Parseur best practices (2026)
- Application: When operator clicks "DETAILS" on a topic, they see the AI's reasoning (sources, rank math, brand-fit explanation) alongside the recommendation.
- Benefit: Operator can audit research without becoming a data scientist.
- Measure: 99.9% accuracy achieved in document workflows using this pattern (vs. 80% for fully automated).

**Pattern 3: Batch Operations Reduce Throughput Bottleneck**
- Source: HubSpot influencer marketing 2025, Sprout Social 2025 research
- Application: "Approve all topics × all languages × all platforms" in one click; system handles granularity (platform-specific formatting).
- Benefit: 40% faster publication timelines. Prevents queue backup at approval gate.
- Measure: Campaigns using batch approvals see faster turnaround vs. post-by-post review.

**Pattern 4: Freshness & Dedup Visibility**
- Source: Social media algorithm shifts (2026) — Instagram/TikTok penalize duplicate content; platforms reward original/fresh signals.
- Application: Digest shows if topic is "REPEAT from Tue" and links engagement change ("X engagement up 18% since yesterday").
- Benefit: Operator makes data-informed decision to skip or capitalize on momentum.
- Risk: Operator may not understand virality decay (what rises fast may fall fast). Mitigation: Confidence score already reflects age decay.

**Pattern 5: Cost Forecasting Before Generation**
- Source: Ciente AI cost management (2026), Mavvrik budget governance (2026)
- Application: Forecast displayed in digest BEFORE operator approves generation. Operator sees "~$15 estimated cost. Budget remaining: $35."
- Benefit: Prevents budget blowover. Operator can scale back before spend.
- Industry norm: 80% of enterprises miss AI cost forecasts by >25%. This pattern prevents surprise bills.

**Pattern 6: Rejection with Feedback Captured for Loop**
- Source: Modern approval workflows (Velt 2026), content operations best practices (Contentoo, CMI)
- Application: Operator rejects video + fills feedback form ("Make it less technical"). System uses feedback to regenerate + to tune future prompts.
- Benefit: Fast iteration. Feedback trains the model over time.
- Measure: Agencies report 35% reduction in approval time when feedback loops are active (Sprout Social 2025).

**Pattern 7: Asynchronous Generation with Notifications**
- Source: Content operations workflow (Mallary AI 2026), editorial calendar automation (marketing agencies, 2026)
- Application: Operator approves research. System generates media async (5–10 min). Operator receives notification when media is ready, then does quick final review.
- Benefit: Operator isn't blocked; can do other work while media generates. No "waiting for render" friction.

**Pattern 8: Audit Trail & Compliance**
- Source: Velt HITL, Parseur document workflows (2026)
- Application: Every decision (approval, rejection, feedback) logged with timestamp + user + rationale.
- Benefit: Compliance-ready. Useful for post-publish analysis ("Why did we approve this? It flopped." — check the log).

### B. Sources & Confidence in Patterns

| Pattern | Source | Date | Confidence | Recheck |
|---------|--------|------|------------|---------|
| Confidence-gated routing | Velt blog, "Human-in-the-Loop Workflows" | 2026-06 | HIGH | Ongoing; applicable to marketing QA |
| Contextual review UI | Velt HITL, Parseur best practices | 2026-06 | HIGH | Proven in document processing (99.9% accuracy) |
| Batch approvals 40% faster | HubSpot 2025 influencer marketing, Sprout Social 2025 | 2025-12 | MEDIUM | Specific to influencer campaigns; extrapolate to general content |
| Dedup + freshness signals | Instagram/TikTok algorithm reports (2025), social algorithm guides | 2025-12 | HIGH | Platforms actively penalizing duplicates as of end-2025 |
| Cost forecasting failures | Mavvrik 2026 AI Cost Governance, Ciente 2026 AI Cost Management | 2026-03 | HIGH | 80% miss forecasts by 25%+; enterprise data |
| Rejection feedback loops | Contentoo content ops, CMI content operations, Sprout 2025 | 2025-12 | MEDIUM-HIGH | 35% approval-time reduction claimed; real-world variability |
| Async generation + notifications | Mallary content workflow, editorial calendar guides (2026) | 2026-01 | MEDIUM | Standard practice in marketing tools; not research-backed |
| Audit trail for compliance | EU AI Act Article 14 (2026), Parseur HITL docs | 2026-01 | HIGH | Regulatory requirement for high-risk AI in 2026 |

---

## Decision Table: Architecture Unblocked ↔ Open Decisions

### Decisions UNBLOCKED by This Brief

| Decision | Rationale | Architectural Area |
|----------|-----------|-------------------|
| Run Digest is the single entry point. | HITL best practice: one clear first artifact prevents file archaeology. Operator scans digest (2 min), then drills into details only if needed. | UI/UX layer — run digest template, navigation, link architecture |
| Confidence-gated defaults (pre-check high-confidence topics). | Reduces decision load by 80%. Supported by Velt HITL research. | Ranking system must output confidence band with sub-components for UI to bind to toggles. |
| Batch operations (approve all topics × all languages × all platforms in one click). | 40% faster timelines per HubSpot. Requires system to know platform-specific formatting rules without operator input. | Content generation layer must know platform-specific variations (LinkedIn carousel ≠ X thread format). |
| Cost forecast BEFORE media generation. | Non-negotiable due to $50 Kie.ai trial. Must gate generation approval. | System architecture must separate research + cost forecast stage from media generation stage (two gates). |
| Feedback capture at rejection → feeds learning loop. | Enables fast iteration + prompt refinement. Proven pattern (Sprout 2025). | Logging layer + feedback form UI + feedback replay into prompt library. |
| Dedup detection + freshness signals visible to operator. | Prevents audience fatigue + supports momentum-capture strategy. Instagram/TikTok now penalize duplicates (2025). | Requires topic comparison across days + engagement tracking integration. |
| Rejection can be granular (skip video, keep copy; skip topic, keep others). | Reduces wasted regeneration cost. Allows operator fine-grained control. | Media package must be modular per asset type + topic. |
| Notion export schema pre-defined in package. | Supports optional D-07 Notion upload without data re-entry. | Package must include structured `notion_export.json` with all required fields. |

### Decisions DEFERRED (Open Questions for Architecture/Build)

| Decision | Question | Impact | Defer Reason |
|----------|----------|--------|--------------|
| How does cost forecast handle partial completion? | If Kie.ai generates 2 of 3 reels before timeout, how is cost attributed? Full charge? Retry cost? | Cost control, budget accounting | Depends on Kie.ai API contract + pricing model (not yet clarified in detail). |
| What triggers a "re-run" request (research only, no media)? | Should operator be able to request "re-run ranking only" or "re-run research from specific source only"? | Research iteration, cost, operator workflow | Advanced use case; defer to v2. For v1, operator can skip topics instead. |
| How are language variants generated? | Does LLM produce both Czech + English in one pass, or sequential? Cost difference? | Pipeline architecture, latency, cost forecasting | Depends on LLM routing + prompt structure. Plan assumes single LLM call with multi-language output, but this is TBD. |
| How is "auto-approve" enabled for low-friction runs? | Can theme config enable "auto-approve if all topics >8.5 confidence + cost <$10"? Or always require manual approval? | Automation policy, cron safety | This is a mode question for Stage 4 architecture (safe/staging/live-prep). v1 should always require manual approval. |
| Integration with Postiz: drafts only, or scheduling? | Can system auto-schedule drafts to Postiz on operator approval, or just create drafts for manual scheduling? | Publishing automation, operator workflow | Postiz has limited approval features (current limitation). Defer full integration to v2; v1 creates drafts only. |
| How are rejected topics tracked for re-research? | If operator rejects topic "Lead scoring" because brand fit is weak, should the system remember to de-prioritize that topic type in future runs? | Feedback learning, ranking tuning | Long-term learning loop. Defer to v2; v1 logs feedback but doesn't auto-tune weights. |
| Operator edit/markup of copy in browser? | Can operator edit a LinkedIn post directly in the review UI, or must they use source file + re-review? | UX friction, content control | Design decision: out-of-scope for v1 (file-based package). Future versions may add inline editing. |

---

## Fact Ledger

| Claim | Source | Date | Confidence | Recheck By |
|-------|--------|------|------------|-----------|
| Batch approvals reduce approval time 40% vs. post-by-post. | HubSpot 2025 Influencer Marketing Report (cited in influenceflow.io); Sprout Social 2025 research (cited in search results) | 2025-12 | MEDIUM | 2026-09-01 (re-validate for social content, not just influencer) |
| 80% of enterprises miss AI cost forecasts by >25%. | Mavvrik 2026 AI Cost Governance Report, Ciente AI Cost Management 2026, Beri AI Cost Surge 2026 | 2026-03 | HIGH | Ongoing (AI spend tracking real-time) |
| Human-reviewed workflows achieve 99.9% accuracy vs. 80% for fully automated. | Parseur HITL best practices, Velt HITL workflow design (2026) | 2026-06 | MEDIUM-HIGH | Subject to task type; document workflows only. Extrapolation to marketing copy needs validation. |
| AI-powered content scanning reduces approval time by 35% while improving compliance accuracy. | Sprout Social 2025 research (cited in influenceflow.io) | 2025-12 | MEDIUM | Validation needed: specific to compliance/brand-safety, not general approval. |
| Instagram penalizes 10+ reposts in 30 days (cut from recommendations). | Social algorithm updates (cited in digitalapplied.com 2026 guide) | 2025-12 | MEDIUM-HIGH | Platform policies change frequently; recheck quarterly. |
| AI video generation costs $20–$220 per finished minute depending on tier. | LTX blog (cited in Mavvrik cost report); specific iteration costs TBD. | 2026-03 | MEDIUM | LTX pricing, plus Kie.ai + Higgsfield.ai specific rates needed; recheck monthly. |
| Agencies automating content calendar reduce coordination time 50–60%. | ustechautomations.com 2026, marketing agency reports (editorial calendar article) | 2026-01 | MEDIUM | Anecdotal; needs larger survey validation. |
| Confidence-gated routing filters review queue to genuinely ambiguous decisions. | Velt HITL workflow design (2026) | 2026-06 | MEDIUM | Proven in document processing; application to marketing content TBD. |
| Postiz lacks approval workflow features; Planable is stronger for multi-level review. | Postiz reviews on G2, Postplanify 2026 comparison | 2026-03 | MEDIUM | Postiz features may have updated; recheck 2026-09. |
| EU AI Act Article 14 requires human oversight for high-risk AI (credit, employment, medical). | Strata.io HITL guide (2026) citing EU AI Act | 2026-01 | HIGH | Regulatory; no recheck needed, but monitor amendments. |

---

## Sources

1. [Postiz: Your Guide to Content Planning Software in 2026](https://postiz.com/blog/content-planning-software) — Postiz official blog, 2026
2. [10 Best Postiz Alternatives in 2026 (Honest Review)](https://postplanify.com/blog/best-postiz-alternatives) — Postplanify, 2026
3. [Postiz Reviews 2026: 4.8/5 G2 — Early Feedback](https://postplanify.com/postiz-reviews) — Postplanify, 2026
4. [Top Content Review and Approval Software Tools in 2026 | Comparison](https://www.cwaysoftware.com/blog/content-review-and-approval-tools) — Cway Software, 2026
5. [Influencer Content Approval Workflows 2026 Guide](https://influenceflow.io/resources/influencer-content-approval-workflows-the-complete-2026-guide/) — InfluenceFlow, 2026
6. [Human-in-the-Loop AI (HITL) - Complete Guide to Benefits, Best Practices & Trends for 2026](https://parseur.com/blog/human-in-the-loop-ai) — Parseur, 2026
7. [Human-in-the-Loop AI in Document Workflows - Best Practices & Common Pitfalls](https://parseur.com/blog/hitl-best-practices) — Parseur, 2026
8. [Human-in-the-Loop Workflows for AI (June 2026)](https://velt.dev/blog/designing-human-in-the-loop-workflows-ai-products) — Velt, June 2026
9. [Human-in-the-Loop: A 2026 Guide to AI Oversight](https://www.strata.io/blog/agentic-identity/practicing-the-human-in-the-loop/) — Strata.io, 2026
10. [Build Your Social Media Management Workflow for 2026](https://mallary.ai/blog/your-social-media-management-workflow-for-2026) — Mallary AI, 2026
11. [Master Content Operations and Keep Your Team Moving Forward](https://contentmarketinginstitute.com/content-operations/) — Content Marketing Institute (CMI), undated
12. [Best Social Media Management Packages for 2026 | PostClaw](https://postclaw.io/blog/social-media-management-packages) — PostClaw, 2026
13. [10 Best Marketing Content Operation Solutions in 2026](https://www.contentoo.com/blog/marketing-content-operation-solutions) — Contentoo, 2026
14. [AI Cost Management In 2026: The Bill That Arrives Before Anyone Built A System To Read It](https://ciente.io/blogs/ai-cost-management) — Ciente, 2026
15. [AI Cost Statistics 2026: Forecasting, ROI, and Budget Risk](https://www.mavvrik.ai/blog/ai-cost-statistics-2026/) — Mavvrik, 2026
16. [2026 AI Cost Governance Report: Visibility & Forecasting](https://www.mavvrik.ai/blog/blog-ai-cost-governance-report-2026/) — Mavvrik, 2026
17. [78% of CFOs Got Blindsided: AI Spend Up 108% to $1.2M](https://www.beri.net/article/ai-costs-surge-108-percent-2026-budget) — Beri, 2026
18. [Content Freshness SEO Factor: The Ultimate Guide to Staying Relevant in 2026](https://topicalmap.ai/blog/auto/content-freshness-seo-factor-guide-2026) — TopicalMap AI, 2026
19. [How Social Media Algorithms Work in 2026: Full Guide](https://www.digitalapplied.com/blog/how-social-media-algorithms-work-2026) — Digital Applied, 2026
20. [Social Media Algorithms: June 2026 Updates & Winning Strategies](https://www.socialpilot.co/blog/social-media-algorithm) — SocialPilot, June 2026
21. [Modern Approval Workflow: 7 Components (May 2026)](https://velt.dev/blog/approval-workflow-components) — Velt, May 2026
22. [How Marketing Agencies Cut Scheduling Time 60% with (2026)](https://ustechautomations.com/resources/blog/automate-content-calendar-scheduling-marketing-agency-workflow-guide-2026) — US Tech Automations, 2026
23. [Workflow Approval Process Guide for Operational Excellence](https://singleclic.com/workflow-approval-process-guide-excellence/) — SingleClic, undated

---

## Key Conclusions & Open Questions

**Operator review UX is a gate, not a rubber-stamp.** A solo marketer must review ~5 topics × 2 languages in under 30 minutes without becoming a data scientist. The design achieves this by: (1) single-page digest entry point, (2) confidence-gated pre-checks (high-confidence topics come pre-approved), (3) batch operations (approve all at once), (4) dedup/freshness visibility (avoid audience fatigue and unnecessary rework).

**Cost forecasting before media generation is non-negotiable.** With only $50 Kie.ai trial budget, the system must forecast spend and gate media generation approval separately from research approval. This prevents budget burnout and gives operator control over iteration cycles.

**Feedback capture and regeneration flow must be granular.** Operator can reject just the video while keeping copy, request variants with specific feedback, or reject entire topics. Each rejection feeds back into a learning loop (prompts, confidence thresholds, brand-fit scoring).

**Pack anatomy is designed for clean Notion export.** All sources, spin rationale, assets, and metadata are structured so that later (D-07) the operator can export the entire run to Notion without re-entry, preserving audit trail.

**Open Q1:** How should the system handle operator feedback that contradicts brand-truth MCP sources? (E.g., operator feedback says "make it corporate," but brand voice config says "conversational.") Should feedback override config, or flag conflict for human arbitration?

**Open Q2:** Should confidence bands in ranking be updated in real-time as new signals arrive, or locked once digest is published? (Real-time = more accurate; locked = stable for operator review.)

**Open Q3:** Is the cost forecast model (iteration-count assumption, per-model pricing) sufficiently granular to capture the variance in video generation? Iterate costs can spike if regenerations are needed.

**Open Q4:** How often should the operator see the digest? Every 4 hours? Daily? Configurable per theme? Cadence affects how often dedup becomes a friction point.

---

*End of brief.*
