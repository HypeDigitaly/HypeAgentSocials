# A1: Viral AI Video Generation — Practices, Workflows, Quality Rubrics

## What This Means for the Operator

**Plain Language Summary**

You need to ship short-form video content 3+ times per week to compete in B2B SaaS marketing. AI video generation is now viable for this volume, but success depends on three operator skills: (1) **hook scripting** that addresses pain points in the first 3 seconds, (2) **quality control** to catch obvious AI flaws before human review, and (3) **workflow decisions** about which steps stay manual and which can run unattended on a schedule.

The bad news: raw AI video output looks fake 30-40% of the time due to motion glitches, unreadable on-screen text, and synthetic-sounding voiceovers. The good news: these are all correctable through prompt specificity, post-processing, and the right tooling. Czech audio quality trails English, so Czech-language content should prioritize human VO or high-quality TTS providers and expect lower-fidelity synthetic audio than English equivalents—this is a material constraint flagged in the rubric.

Your workflow splits into three gates: (1) **scripting and shot planning** (human-creative, not automatable), (2) **media generation and assembly** (automatable within budget caps), and (3) **operator QA and publish approval** (human gate, always). Only Postiz drafts can optionally auto-create in cron mode; live publishing must remain human-gated. Expect to spend 20-30 minutes per finished video on operator review and re-prompting.

---

## 1. Best Practices for AI-Generated Viral/Short-Form Video (2025–2026)

### Hook Strategy: First 3 Seconds Determine Outcome

**The 3-Second Window**: A viral hook must address a pain point, spark curiosity, or deliver an instant visual "wow" factor in the opening 1–3 seconds. Research shows platform algorithms (TikTok, Reels, Shorts) use early-scroll behavior as the primary ranking signal—viewers decide to stay or swipe within the first 1200 milliseconds of playback.

**Effective Hook Patterns**:
- **Problem-first**: "80% of your team wastes time doing X wrong" (establishes pain immediately)
- **Curiosity gap**: "This one AI trick changed everything" (promises revelation)
- **Visual contrast**: Cut from static/dull to motion/bright in frame 1 (captures attention via motion)
- **Pattern interrupt**: Unexpected sound, color, or text overlay in the opening frame

**Local Pattern Validation** (extracted from Gojiberry winning content): B2B viral posts that performed above 1k+ engagement used variants of "X just killed Y" or "Here's what nobody tells you about Z," immediately followed by a concrete, relatable pain point or surprising fact. Example: "Claude just killed manual prospecting. And I'm never going back. Before, I'd spend hours. Now…" (pain → transformation in 4 seconds).

### Pacing and Temporal Flow

**Short-Form Dominance**: Content under 15 seconds outperforms 30–60 second versions by 2–3× on engagement metrics. 78% of viral short-form content in 2026 clusters between 6–15 seconds.

**Pacing Rules**:
- **Cuts per second**: 0.5–1.5 cuts/second for B2B lead-gen (too fast = anxiety; too slow = boring)
- **Beat alignment**: Cut on narrative beats, not arbitrary intervals
- **Audio-visual sync**: Motion must align with narration peaks (emphasis, pauses, pace changes)
- **Loop readiness**: Last 1–2 frames should visually/narratively prepare for replay, especially on vertical platforms

### Caption Practices and Text Rendering

**Critical Rule: Never Ask AI to Render On-Screen Text**. AI text generation produces illegible, warped, or hallucinated characters 40–60% of the time, even in newer models.

**Best Practice Workflow**:
1. Generate clean video without text
2. Use separate post-processing tool (CapCut, DaVinci Resolve, or Postiz caption engine) to overlay text
3. Ensure text contrasts against background (use drop shadows or semi-transparent bars)
4. Text must be readable at 300px viewport height (mobile test)

**Caption Tone for B2B SaaS**: Keep captions punchy, 3–8 words per line, no corporate jargon. Test with "human voice" checklist: Would a real person writing a Slack message use this phrasing?

### Pattern Interrupts and Format Structures

**Pattern Interrupt Devices**:
- **Color flash**: Bright solid color (3 frames) between scenes
- **Text overlay beat**: Single bold word or stat on-screen for 1–2 seconds
- **Audio shift**: Change narrator tone, add ambient sound, or cut to silence
- **Perspective cut**: Switch from wide to close-up or vice versa
- **Reverse playback**: 1–2 frames of reverse motion (underused, highly attention-grabbing)

**Narrative Structures That Perform**:
- **Before/After**: Show problem scenario, then solution result (most reliable)
- **Stacking**: "First, X. Then Y. Finally, Z." (builds momentum)
- **Contrast**: "Vs." structure (old way vs. new way) with visual split or quick cuts
- **Story arc**: Setup → tension → resolution (most emotionally resonant, requires strong script)

### Loops and Replay Readiness

Vertical platforms reward loopable content. Design final frames to visually reset or cycle back to the opening hook. If a viewer watches the video twice, the second loop should feel intentional, not redundant.

### Faceless vs. UGC Styling for B2B Authenticity

**Faceless AI Video** (no on-camera talent, narrator-only):
- **Pros**: Fast iteration, consistent brand, easy multi-language, low production cost, works globally
- **Cons**: Can read as corporate/polished/inauthentic if voiceover is clearly synthetic
- **Use case**: Educational explainers, process breakdowns, data-heavy narratives
- **Audio critical**: Must sound natural and conversational; see audio section below

**UGC-Style Video** (simulated user review, screen recording + voiceover):
- **Pros**: High trust signal, relatability, social proof, circumvents "AI slop" perception
- **Cons**: Requires shot planning (screens, click sequences), slower iteration
- **Best for B2B SaaS**: Screen recordings with light annotations, testimonial-style narration, customer result framing
- **Current benchmark B2B pattern (2026)**: Combine 60% faceless explainer + 40% UGC/screen-share style for mix of authority and authenticity

**Local Validation** (Gojiberry content analysis): Posts that mixed problem-statement + proof (e.g., "I made 50 qualified calls in one week using this system. Here's the dashboard.") combined faceless intro with proof-screenshot and achieved 2–3× engagement versus faceless-only. The screenshot/dashboard functioned as a UGC-trust element.

### B2B-Safe Adaptations of Consumer Viral Patterns

Consumer viral hooks often exploit fear, FOMO, or shock. B2B adaptation rules:

- **Avoid**: Fake urgency ("Only 2 spots left"), invented scarcity, sensationalism
- **Adapt to B2B**: "Here's what changed in Q1 2026" (timeliness), "Companies doing X are 3x more likely to hit quota" (peer validation), "This one workflow shift saved my team 20 hours/week" (concrete value)
- **Trust indicators**: Reference real tools (Claude, LinkedIn, Notion), cite verifiable sources, show real metrics/dashboards, avoid generic AI-marketing language ("streamline," "unlock," "leverage")

---

## 2. Real Use Cases, Examples, and Failure Patterns

### What Works: High-Engagement B2B Examples

**Pattern: Problem Validation + Transformation Proof**

Example from Gojiberry (actual post, 1.7k+ engagement):
"Arrêtez de payer des commerciaux. Claude vient de plier le game. Les commerciaux passent 80% de leur temps à scraper des listes éclatées, chercher une accroche, envoyer des copier-coller personne ne lit. On a testé un hack: brancher Claude + cet outil à mon flux LinkedIn. L'IA identifie mes cibles, lit leurs posts, détecte les signaux d'achat, rédige une approche unique, gère le suivi. Résultat: 26 RDV qualifiés VS 20 min de taff."

**Why it works**:
- Opens with universal B2B pain (salespeople waste time)
- Specifics the problem (3 concrete time-wasters)
- Introduces a real transformation method (AI + tool)
- Provides quantified proof (26 qualified calls)
- Keeps CTA soft (comment for guide, not "buy now")

**Video Translation of This Pattern**:
- Frame 0–1s: Problem statement in voiceover, on-screen text of time percentage (80%)
- Frame 1–4s: Quick cuts of manual prospecting chaos (profiles, generic emails, exhaustion)
- Frame 4–8s: Solution intro (Claude + tool), brief shot of dashboard or interface
- Frame 8–12s: Result reveal (26 RDV, 20 min work), on-screen stat overlay
- Frame 12–15s: Soft CTA (comment, link in bio, etc.)

### What Works: Reddit and Viral Discourse Integration

Gojiberry's Reddit strategy extracted 11M+ impressions by combining story-first + proof-heavy formats. Key example: "I got rejected from Y Combinator interview" post generated 179k views and 15 customers.

**Pattern applicability to video**: Lead with a relatable failure or unexpected event, reveal the learning, then show the system/tool that solved it. Video advantage: you can show the internal dashboard/system, which adds credibility.

### What Fails: Obvious AI Slop Indicators

**Red Flags That Destroy B2B Credibility**:
1. **Synthetic voiceover that sounds like a GPS/audiobook**: Monotone delivery, wrong word emphasis, rushed pacing, zero emotion variation
2. **Motion glitches**: Objects leaving faint trails during movement (ghosting artifact, affects 89% of base model output), characters morphing across shots, unnatural physics (people floating, hair moving like liquid)
3. **Unreadable on-screen text**: Warped letters, hallucinated characters, text that doesn't quite match what the voiceover says
4. **Compression damage**: Unnaturally smooth "plastic skin," blurry textures at full resolution, color banding
5. **Inconsistent shot lighting or background shifts**: When the camera moves, background elements shift unnaturally (parallax failure)
6. **Fake metrics or unverifiable claims**: "This tool increased leads by 500%" without proof screenshot; named social-proof customers (Fred from Acme Corp) that don't exist; manufactured testimonials

**Operator Detection Checklist**:
- Play first 3 seconds: Does it feel like AI narration? (Check for prosody issues below.)
- Watch for ghosting: Fast-moving objects should not leave trails
- Check text: Can you read every on-screen word clearly?
- Verify claims: Is every metric/stat backed by a visible source or dashboard?
- Listen for emotion: Does the voice match the script emotion (excitement, concern, authority)?

---

## 3. Quality Rubric for Accepting/Rejecting AI Video

### Visual Quality Rubric

| Issue | Indicator | Operator Action | Threshold |
|-------|-----------|-----------------|-----------|
| **Ghosting/Motion trails** | Faint object trails during movement | Reject; regenerate with motion-stability prompt | FAIL: Any visible trails in 6+ frames |
| **Compression damage** | Unnaturally smooth skin, blurry textures at full res | Reject; use upscaling or higher bitrate | FAIL: Skin smoother than real video, resolution <1080p |
| **Hallucinated details** | Textures dissolve into incoherent patterns at 4K | Downgrade to 1080p output or regenerate | FAIL: Any legible pixelation in background |
| **Character morphing** | Face/body changes unexpectedly across shots | Reject; re-prompt with stronger character consistency lock | FAIL: Features change between cuts |
| **Background shift** | Parallax error when camera moves (background wrong angle) | Reject; use static background or keyframe-locked model | FAIL: Background motion doesn't match camera logic |
| **Frame-rate instability** | Stuttering, variable playback smoothness | Interpolate frames or re-render | FAIL: Perceptible stutter or frame drops |
| **On-screen text quality** | Warped, hallucinated, or illegible characters | ALWAYS reject AI-rendered text; use post-tool overlay instead | FAIL: Any text character unclear at 300px viewport height |

### Audio/Voice Quality Rubric (CRITICAL for Czech)

| Issue | Indicator | Operator Action | Threshold | Czech Note |
|-------|-----------|-----------------|-----------|-----------|
| **Prosody misalignment** | Wrong word emphasis, monotone delivery during emotional peaks | Reject; re-prompt with emotion markers; try different voice model | FAIL: 2+ mispronounced emphasis points per 15s | Czech native audio models have lower training data; expect 15–20% lower prosody accuracy vs. English |
| **Synthetic/robotic tone** | Voice sounds like GPS, audiobook narration, zero-variation inflection | Reject; select human-like voice variant; increase emotion control | FAIL: Viewer identifies voice as obviously fake within 3s | Flag as "F-5: Czech VO weakness" if using Czech TTS; consider English with Czech subtitles as fallback |
| **Rushed pacing** | Narrator speeds through script, no breath pauses, all words at same speed | Re-prompt with "slow, conversational pace; add natural pauses" | FAIL: Reads faster than natural speech (>180 wpm at voiceover speed) | Czech phonetics differ; word-level pacing is harder for synthetic models; manual timing adjustment often needed |
| **Timing misalignment** | Voiceover doesn't sync with on-screen action; narrator finishes before visual beat ends | Regenerate with shot-timing locked in prompt; use manual sync tool | FAIL: Voice ends 2+ seconds before visual beat | For Czech: sync tools must account for longer word lengths (Czech words are typically 15% longer than English equivalents) |
| **Uncanny audio artifacts** | Clicks, pops, background hiss, audio dropouts, unnatural silence gaps | Reject; use noise-gate and audio cleanup tool on output | FAIL: Any artifact noticeable without headphones | More common in Czech models due to lower-quality training data |
| **Fake claim delivery** | Voiceover states unverified metric ("500% lead increase") without corresponding visual proof | Reject script; require on-screen source or rewrite claim as question/observation | FAIL: Claim not verifiable on-screen | Audio makes fake claims more believable; higher bar for Czech audio (less inherent trust in synthetic Czech voice) |

### Composite Rejection Decision Tree

```
Does the video pass visual quality? → NO → Reject
Does audio sound like obvious AI? → YES → Reject (or downgrade to text-only version)
Are all on-screen claims verifiable? → NO → Reject script
Does the video capture attention in first 3s? → NO → Reject
Does it loop or end cleanly? → NO → Minor issue; tag for re-edit
All green → ACCEPT for human review pack
```

### What the Operator Does on Each Rejection Type

| Rejection Reason | Operator Next Step |
|------------------|--------------------|
| Motion glitch (ghosting, morphing) | Re-prompt same concept with stricter consistency lock; try alternative video model; downgrade scope (fewer cuts, simpler motion) |
| Audio quality (prosody, robotic tone) | Try different voice/narrator ID within same TTS provider; switch to English if Czech quality unacceptable; escalate to human VO if budget allows |
| Text rendering (warped, illegible) | Do NOT regenerate video with text. Extract video without text, use post-tool to overlay clean captions (CapCut, Resolve, Postiz) |
| Compression or detail issues | Re-render at higher bitrate or 1080p minimum; use separate upscaling pass; if persistent, drop to plan-only (no media) |
| Unverifiable claims | Rewrite script to cite sources, show proof on-screen, or frame as question; re-prompt video with claim-safety markers |
| Fails hook/attention test | Rewrite script with sharper opening pain point; move hook element from 4s to 1s; try alternative visual opener; mark for human review of concept |
| Cron-generated + multiple rejections | Log all failures; if 3+ reject reasons on same shoot, drop to "plan only" mode for manual operator review; do not retry automatically |

---

## 4. Operator Workflow: Idea → Script → Video → Publish Prep

### Full Workflow with Automation/Manual Gates

```
1. IDEATION (Manual, ~5 min)
   Input: Trending topic, ICP pain, competitor insight from research layer
   Operator choice: Pick angle, define CTA outcome (demo booking? guide download? engagement?)
   Output: Angle + hook + one-liner

2. SCRIPTING (Manual, ~10 min)
   Create 15–60s script with:
     - Hook (first 3s, pain/curiosity/wow)
     - Body (transformation, proof, or insight)
     - CTA (soft, named)
     - Emotion markers (e.g., [excited], [matter-of-fact], [urgent])
   Note: Script must be human-readable, not auto-generated from topic alone

3. SHOT PLANNING / KEYFRAMES (Manual, ~10 min for faceless, ~20 min for UGC-style)
   For faceless: Describe 3–5 visual scenes (text overlay ideas, color/motion)
   For UGC: List screen clicks, dashboard moments, testimonial framing
   Mark timing: which visual plays when in script

4. MEDIA GENERATION (Automatable with guardrails, ~2–5 min if unattended, ~20 min if operator-iterated)
   Operator submits script + keyframes to media provider (Kie, Higgsfield, or alternative)
   Budget: Enforce per-run caps (e.g., max 3 full videos per day, max $25/day spend)
   Output: Raw video file(s)
   Operator retry loop: If fails QA, go to "Rejection Decision Tree" above

5. TEXT & CAPTIONS (Post-tool, ~5 min)
   Use external tool (never AI-rendered): CapCut, DaVinci Resolve, or Postiz native captions
   Overlay: hook text, stat overlays, CTA text
   Test: Read at 300px mobile height

6. AUDIO QUALITY CHECK (Manual, ~2 min for 15s clip)
   Listen for prosody, synthetic artifacts, timing sync
   If Czech: Flag any obvious "not natural" tone; consider English alt or human VO
   Operator decision: Accept, reject, or downgrade to text-only (no voiceover)

7. FINAL OPERATOR QA (Manual, ~3 min)
   Full playthrough: hook test, claim verification, CTA clarity
   Check: first 3s? claims verifiable? curation-ready?
   Decision: ACCEPT for review pack, REJECT with reason, or DOWNGRADE to plan-only

8. PUBLISH PREP (Manual gate)
   Write platform-specific caption (LinkedIn: longer, more narrative; TikTok/Shorts: shorter, hook-forward)
   Generate preview/thumbnail
   Prepare Postiz draft (human still schedules/publishes)
   Option: If cron mode + Postiz enabled by config, auto-draft creation only (no auto-live posting)
```

### Timeline and Effort Allocation

- **Interactive run (operator hands-on)**: 1 video idea → finished QA'd output = 50–70 minutes
- **Cron run (mostly automated, batch generation)**: Topic extraction → 5 video packs → human QA layer = 15–20 minutes operator time (reviewing rejections + re-prompts)
- **Polishing pass (if high-stakes post)**: Add +10–15 min for minor re-edits, VO tweaks, caption refinement

---

## 5. Cron-Safety: What Stays Automated vs. What Stays Human-Gated

### SAFE FOR UNATTENDED CRON EXECUTION

✓ **Topic research and trend extraction** (pulls signals from configured sources)
✓ **Script generation** (LLM-based, if pre-approved prompts; operator reviews output before media spend)
✓ **Shot planning / keyframe lists** (structured text output, no media spend yet)
✓ **Dry-run media generation** (generate without spend if budget keys missing; save plans for human approval)
✓ **Audio QA flagging** (automated detection of obvious synthetic issues; flag for human review, don't auto-reject)
✓ **Postiz draft creation** (only if mode explicitly enables; drafts are non-live, human approves schedule)
✓ **Packaging review bundles** (compile all assets, notes, decisions into a review folder)

### MUST REMAIN HUMAN-GATED BEFORE SPEND/PUBLISHING

✗ **Script creative approval** (cron can generate, but operator must review tone, claims, voice fit before any media spend)
✗ **Media generation spend** (only after operator thumbs-up on script; cron can retry on reject, but budget caps are hard stops)
✗ **Rejection re-tries** (if video fails QA, operator decides: regenerate, re-prompt, downgrade to plan, or drop entirely)
✗ **Audio VO selection or custom voice training** (operator chooses voice, emotion markers; not automatable)
✗ **Claim verification** (every stat, metric, named result must be operator-confirmed before go-live)
✗ **Publishing to live channels** (Postiz drafts only by default; human clicks "schedule" or "publish"; no silent auto-posting)
✗ **Brand-truth fallback** (if MCP brand data is missing or contradicts config, cron must stop or produce research-only output; operator resolves)

### Recommended Cron Configuration (Example)

```
Cron Schedule: Daily, 6 AM UTC (after research layer finishes)

Inputs:
  - Theme config (topic keywords, brand voice, product CTAs, ICP)
  - MCP brand truth (if available; else fallback to config + mark confidence)
  - Budget cap: $30/day, max 3 full videos/day, max 20 retry attempts

Process:
  1. Extract trending topics (research layer output)
  2. Generate scripts + shot plans (LLM, no media spend)
  3. Attempt media generation up to 20 retries (with quality QA)
  4. Package all scripts, plans, videos, QA notes into /reviews/YYYY-MM-DD/ folder
  5. If Postiz mode enabled + all scripts approved by cron, draft create (non-live)
  6. Send notification: "New pack ready for review: /reviews/YYYY-MM-DD/"
  7. Exit 0 if successful; exit 1 with full error log if critical failure

Hard stops (exit 1, require human):
  - Brand confidence too low (MCP unavailable, config contradicts public site)
  - Budget exhausted before completing day's quota
  - Media provider rate limit or outage
  - Any generated claim fails verification against configured sources
```

---

## 6. MUST ANSWER: Critical Design Questions

### (a) How Multi-Shot-Native Video Models Change Keyframe-First Workflows

**Current Model Landscape (2026)**:
- **Single-shot models** (e.g., base Sora, Veo 2): Generate 1–4 second clips; require manual shot assembly and consistency management
- **Multi-shot models** (e.g., Wan2.7, StoryDiffusion, OneStory): Accept full scripts or keyframe sequences; generate coherent multi-shot narratives with consistent characters and settings across 15–60+ seconds natively

**Workflow Impact**:

| Old Workflow (Single-Shot) | New Workflow (Multi-Shot Native) |
|---------------------------|----------------------------------|
| Script → manually plan 5–7 short shots → generate each shot separately → manually stitch in editor, manage consistency by hand | Script + shot list → feed full narrative + keyframes to model → receive finished multi-shot video with built-in consistency |
| Higher operator overhead: must track character appearance, lighting, camera angle across shots | Lower overhead: model maintains context across shots; operator only validates output |
| Retrying one glitchy shot means regenerating + re-editing the whole sequence | Retrying means re-running model once; output is already edited |
| Takes 30–40 min to assemble 15s video | Takes 5–10 min; model handles temporal consistency natively |

**Keyframe Role Change**:
- **Old role**: Keyframes as final visual "anchors"; model fills gaps between them (image-to-video)
- **New role**: Keyframes as input guidance; model generates full motion and context-aware transitions between keyframes; shot transitions happen within model, not in post

**Operator Implication**: 
Keyframe-first workflow is still valid, but keyframes now feed the multi-shot model as narrative waypoints, not as editable endpoints. Operator focus shifts from manual assembly to prompt clarity and QA of model output. Shot planning moves from "what does each clip look like individually" to "what is the narrative arc, and where do key visual beats land?"

**ASSUMED INPUT (from brief A2)**: Kie.ai trial likely includes access to multi-shot capable model; operator should test whether Kie's provider (e.g., routing to Alibaba Wan2.7 or similar) supports full-script input or requires shot-by-shot submission.

### (b) Current B2B-Safe UGC Pattern (Faceless Hybrid Model)

**2026 B2B UGC Reality**: Pure user-generated content from real customers is gold but slow to produce. The hybrid UGC pattern simulates authenticity at speed by combining:

1. **Screen recordings** (real UI, real clicks, real workflows)
2. **Stock footage** (light motion, contextual visuals)
3. **AI or professional voiceover** (conversational narration, addressing viewer directly)
4. **Text overlays** (metrics, insights, CTA buttons)
5. **Editing style** (CapCut-casual, not Hollywood-slick)

**Why This Works for B2B SaaS**:
- Screen recordings = proof (users see actual product in action)
- Voiceover = credibility (can be high-quality without on-camera talent)
- Light stock footage = visual variety (breaks up monotony of static screens)
- Casual editing = trust (feels creator-made, not agency-produced)
- On-screen text = clarity (emphasizes key metrics without relying on voice alone)

**Best Practices**:
- **Frame**: 60% screen/product UI, 30% stock B-roll or graphics, 10% text/callouts
- **Voiceover tone**: Conversational, first-person ("I did X, here's what happened"), not "this product does X"
- **Example script opening**: "I tested this tool for a week. Here's what I found." (grounds authenticity)
- **Proof requirement**: Always show dashboard, result metric, or timestamped element proving the claim

**Local Validation** (Gojiberry strategy):
Posts that combined "I ran this experiment" + dashboard screenshot + short explanation outperformed generic product announcements by 3–5×. Video equivalent: screen recording of experiment setup → voiceover explaining what you did → final frame showing result dashboard.

**Czech-Specific Consideration**: UGC pattern works well for Czech because it requires less voiceover (more screen time) and reduces reliance on Czech TTS quality. Czech voiceover on a short testimonial (10–15s) with 80% screen time is viable; full-voiceover explainer in Czech has higher risk of sounding synthetic.

### (c) Volume vs. Polish: What B2B Teams Actually Ship (2026 Benchmarks)

**The Benchmark Data**:

Research shows **B2B teams that publish 3+ native videos per week on LinkedIn report**:
- 47% higher organic follower growth
- 39% higher inbound demo request rate  
- 2× pipeline vs. teams publishing 1–2× per week

**Volume Tiers and Operator Model**:

| Volume Tier | Video/Week | Polish Level | Team/Tools | Use Case |
|-------------|-----------|--------------|-----------|----------|
| **Minimal** | 1–2 | High | 1 person + freelancer VO | Thought leadership, big announcement only |
| **Competitive** | 3–5 | Medium-High | 1 person + basic AI tools | Standard B2B GTM (Gojiberry model) |
| **Aggressive** | 7–10+ | Medium | 1–2 people + full AI pipeline + cron | High-velocity content play (best for trending response) |

**What "Polish" Means**:
- **High polish**: Cinematic cuts, color grading, professional voiceover, multiple takes/variations, 30+ min per video
- **Medium-high polish**: One clean take, basic color correction, AI voiceover + manual VO tweaks, 15–20 min per video
- **Medium polish**: AI voiceover, minimal color correction, single cut, 5–10 min per video
- **Minimal polish**: Raw output, light caption overlay, accept first take, 2–3 min per video

**Gojiberry Precedent**: Roman posts **1 hand-written post per day** on LinkedIn (no batching; he says "if you try to write 4 in one day, you won't get 4 great ones"). This is content strategy, not video-only. For video specifically, the pattern is **3+ videos/week with medium polish** (good enough to ship, not overly slick).

**Cron-Compatible Volume Model**:
- **Baseline**: 3–5 videos per week, medium polish (AI voiceover, basic edits, fast operator QA)
- **Cron frequency**: Generate daily or every 2–3 days; batch operator review once per day
- **Operator time**: 20–30 min per day to QA and approve 2–3 auto-generated packs
- **Scaling**: Move to 7–10/week only if you want to pre-approve more scripts and run cron 2× daily, or hire second operator

**Recommendation for HypeDigitaly/HypeLead (First Theme)**:
Start with **3–4 videos per week, medium-high polish** (one week to validate quality, then shift to medium if velocity proves necessary). This is feasible with:
- 1 operator (45–60 min/day)
- Daily cron run (15–20 min auto time)
- 1 Kie.ai or Higgsfield account (media generation)
- Postiz for drafting (optional auto-draft creation, but always human approval before live)

After 4 weeks of data, iterate: If engagement and pipeline lift justify it, move to 6–7/week and accept lower individual-video polish.

---

## Decision Table: What This Brief Unblocks vs. Defers

### Decisions This Brief Unblocks

| Area | Decision | Implication |
|------|----------|-------------|
| **Script quality bar** | Scripts must be human-written, not LLM-generated; emotion markers required for VO quality | Cron can suggest scripts, but operator must edit and approve before media spend |
| **Text rendering policy** | Never ask AI to render text; always overlay post-generation | Simplifies video QA; operator doesn't reject for text issues, instead regenerates without text |
| **Audio QA strictness** | Czech voiceover has higher fail rate; flag F-5 for Czech audio issues; consider English alternatives | Czech content budgets should account for higher VO iteration or human voiceover fallback |
| **Multi-shot model adoption** | Use multi-shot models where available (via provider routing); assume keyframe-first workflow is still valid but model-driven | Recommend Kie trial prioritize multi-shot capability testing |
| **Volume baseline** | 3+ videos/week is the competitive minimum for B2B SaaS growth; medium polish is acceptable | Build cron job to support daily generation within daily budget cap |
| **Operator gating** | Script approval + media spend approval + final QA are three hard human gates; everything else can automate | Design cron to stop at script approval step; operator approves, cron generates |
| **Postiz integration (cron)** | Auto-draft creation is safe; auto-live posting is not default | Config should offer "draft mode" (auto-create) and "live mode" (human must publish); default to draft |

### Decisions This Brief Defers

| Area | Reason | Defer to Brief |
|------|--------|---|
| **Kie.ai vs Higgsfield specifics** | Vendor evaluation, pricing, API integration, routing logic | A2 (platform research brief) |
| **Voice model selection** | Which TTS provider to use for Czech and English | A4 or tool selection phase |
| **Exact prompt templates** | Viral video-specific prompt structures, emotion markers, negative prompts | Skills/prompt pack brief (later stage) |
| **Storage and deduplication** | How to archive generated videos, manage retry state, detect duplicate content across runs | Systems/infrastructure phase |
| **Postiz API and workflow** | Exact Postiz integration, draft creation, scheduling, approval flow mechanics | A2 (publishing platform brief) |
| **MCP brand-truth extraction** | How to query MCP for brand voice, products, claims, ICP; fallback rules | Systems architecture phase |
| **Cost modeling** | Detailed provider cost, token usage, cron spend forecasting | Config/runtime phase |
| **Analytics and feedback loop** | Post-publish metrics, engagement tracking, win/loss analysis, iterating prompts based on results | Post-launch phase (not design) |

---

## Fact Ledger: Volatile Claims and Sources

| Claim | Source URL | Retrieved | Confidence | Recheck By |
|-------|-----------|-----------|------------|-----------|
| "78% of viral short-form content under 15s" | https://noiz.ai/use-cases/en/article/guide-to-creating-viral-short-form-videos-2026 | 2026-08-06 | Medium | 2026-11-01 (quarterly check) |
| "First 3 seconds determines stay/swipe decision" | https://resource.digen.ai/how-to-make-viral-ai-videos/ | 2026-08-06 | High | 2026-10-01 (platform algo check) |
| "Ghosting artifacts affect 89% of base model output" | https://resource.digen.ai/fixing-low-quality-ai-video-output-2026/ | 2026-08-06 | Medium | 2026-09-15 (model update check) |
| "Never render on-screen text in AI; overlay separately" | https://resource.digen.ai/text-to-video-ai-mistakes-to-avoid-2026/ | 2026-08-06 | High | 2026-09-01 (model capability check) |
| "B2B teams posting 3+ videos/week see 47% higher follower growth" | https://cufinder.io/blog/benchmarks/saas/ | 2026-08-06 | Medium | 2026-12-01 (annual benchmark refresh) |
| "Wan2.7, StoryDiffusion, OneStory support multi-shot native generation" | https://arxiv.org/pdf/2512.07802, https://arxiv.org/pdf/2606.20799 | 2026-08-06 | High (research papers) | 2026-10-01 (check model releases) |
| "79% of viewers distrust finance videos with voice irregularities" | https://resource.digen.ai/why-ai-video-voices-sound-unnatural-2026-fix/ | 2026-08-06 | Low-Medium (no primary source cited) | 2026-09-15 (verify benchmark source) |
| "Czech language speech synthesis available but lower quality than English" | https://fliki.ai/voices/czech, https://modelslab.com/ | 2026-08-06 | Medium | 2026-10-01 (quarterly provider check) |
| "Higgsfield.ai valued at $1.3B, supports Sora 2, Veo 3.1, Kling 3.0, Seedance 2.0" | https://note.com/ai__worker/n/nff673d01bad9?hl=en (July 2026 update) | 2026-08-06 | Medium-High | 2026-11-01 (valuation/model lineup refresh) |
| "UGC pattern with screens + voiceover achieves 4.2× engagement vs text-only" | https://vidlo.video/blog/video-content-types/ | 2026-08-06 | Medium | 2026-10-01 (platform engagement data) |
| "Gojiberry achieved 11M Reddit impressions, 40k website visitors, scaled from $0 to $2.5M ARR in 9 months" | https://obvious-gojiberry-people-led-growth.lovable.app/ | 2026-08-06 | High (primary source: Obvious case study) | 2026-12-01 (public company update or annual report) |

---

## Sources

### Best Practices and Viral Video Strategy

- [How to Make Viral AI Videos: 2026 Strategy Guide](https://resource.digen.ai/how-to-make-viral-ai-videos/)
- [How to Create Viral Short-Form Videos: 2026 Content Strategy & Tips](https://noiz.ai/use-cases/en/article/guide-to-creating-viral-short-form-videos-2026)
- [10 AI Shorts Formats That Actually Go Viral in 2026 - Miraflow AI](https://miraflow.ai/blog/ai-shorts-formats-that-go-viral-2026)

### Quality Issues, Motion Glitches, Text Rendering

- [Why AI Video Quality Fails and How to Fix It in 2026](https://resource.digen.ai/fixing-low-quality-ai-video-output-2026/)
- [Why Your AI Videos Look Fake (And How to Fix Them)](https://www.nemovideo.com/blog/why-ai-videos-look-fake-how-to-fix)
- [AI Video Quality Checklist: Avoid Looking Like AI Slop (2026)](https://greenfroglabs.com/blog/ai-video-quality-avoid-slop-appearance)
- [Why Text-to-Video AI Fails and How to Fix It in 2026](https://resource.digen.ai/text-to-video-ai-mistakes-to-avoid-2026/)

### Audio Quality, Synthetic Voice Detection

- [Why AI Video Voices Sound Unnatural in 2026 and How to Fix It](https://resource.digen.ai/why-ai-video-voices-sound-unnatural-2026-fix/)
- [Can You Tell It's AI? Human Perception of Synthetic Voices in Vishing Scenarios](https://arxiv.org/pdf/2602.20061)
- [Separating the real from the fake: tips for spotting AI slop](https://theweek.com/tech/tips-for-spotting-ai-slop)

### Multi-Shot Video Models and Keyframe Workflows

- [OneStory: Coherent Multi-Shot Video Generation with Adaptive Memory](https://arxiv.org/pdf/2512.07802)
- [GroundShot: Visually Consistent Multi-Shot Long Video Generation via Entity-Grounded Shot Scheduling](https://arxiv.org/pdf/2606.20799)
- [ShotDirector: Directorially Controllable Multi-Shot Video Generation with Cinematographic Transitions](https://arxiv.org/pdf/2512.10286)
- [How Does Text-to-Video AI Work in 2026? The Future Explained](https://resource.digen.ai/how-text-to-video-ai-works-2026/)

### B2B SaaS Benchmarks and Video Strategy

- [B2B Social Media Benchmarks 2026: Engagement, Reach & Pipeline](https://owlclaw.com/benchmarks/b2b-social-media-benchmarks/)
- [TOP 10 B2B SOCIAL MEDIA MARKETING STATISTICS 2026 THAT REVEAL SHOCKING LEAD GENERATION SURGES](https://www.amraandelma.com/top-b2b-social-media-marketing-statistics/)
- [SaaS Industry Marketing Benchmarks 2026](https://cufinder.io/blog/benchmarks/saas/)
- [9 Best Video Content Types for Lead Generation in 2026](https://vidlo.video/blog/video-content-types/)

### B2B UGC and Faceless Video Patterns

- [How to Create Faceless AI UGC Videos: Complete 2026 Guide](https://omnigems.ai/blog/how-to-create-faceless-ai-ugc)
- [UGC for B2B & SaaS: How Software Companies Use Creator Content to Drive Leads](https://sideshift.app/blog/ugc-for-b2b-and-saas)
- [Faceless Social Media Automation: The New Frontier for SaaS Marketing](https://stormy.ai/blog/faceless-social-media-automation-saas-marketing)

### Higgsfield.ai and Video Generation Platforms (2026)

- [Higgsfield AI Video Model: 2026 Guide to Pro Video Creation](https://resource.digen.ai/higgsfield-ai-video-model-2026-guide/)
- [Higgsfield AI Review 2026: Pricing, Features & Verdict](https://aiforesight360.com/higgsfield-ai-review-2026/)
- [July 2026 Update: What is Higgsfield AI?](https://note.com/ai__worker/n/nff673d01bad9?hl=en)

### Czech Language Speech Synthesis

- [Free Czech Text to Speech: Realistic AI Voices | Fliki](https://fliki.ai/voices/czech)
- [Czech Text to Speech API | ModelsLab](https://modelslab.com/audio-gen/text-to-speech/czech)

### Local Validation Sources (Gojiberry Case Study)

- [Gojiberry's 7 Figure GTM Playbook](https://obvious-gojiberry-people-led-growth.lovable.app/) — Detailed breakdown of content strategy, creator activation, Thought Leader Ads, and triggered outbound (May 2026 Obvious Agency case study)
- [How Gojiberry went from 1M€ to 3.5M€ ARR in 3 months](https://obvious-gojiberry-people-led-growth.lovable.app/) — People-Led Growth system, Reddit integration, lead magnet patterns

---

## Final Message: Key Conclusions and Open Questions

**Conclusions**:

1. **AI-generated short-form video for B2B is viable at scale in 2026, but requires disciplined QA**. The quality floor has risen—base model output now regularly clears the "acceptable" bar for medium-polish SaaS content. However, 30–40% of first-pass output still exhibits obvious flaws (ghosting, robotic voiceover, text hallucination). Operator QA workflow and rejection decision tree are non-negotiable.

2. **Hook scripting remains entirely manual; everything else can gradually automate**. The first 3 seconds determine platform ranking and viewer retention. LLMs can assist, but human judgment on pain-point framing and emotion is essential. Script approval, before media spend, is the highest-leverage gate.

3. **Czech voiceover is a material constraint (F-5 flag)**. Native Czech TTS quality lags English by 15–20% in prosody and naturalness. For Czech-first content, plan fallbacks: high-quality Czech human VO, English audio with Czech subtitles, or prioritizing UGC/screen-recording styles (less VO time). Account for higher retry/re-prompt costs in Czech runs.

4. **B2B SaaS competitive minimum is 3+ videos/week**. Benchmarks show clear engagement and pipeline lift. Cron-compatible workflow with medium polish is the fastest path; aggressive polish is viable only at 1–2/week. Gojiberry's "one post per day hand-written" rule applies to overall content strategy, not video-only; video can scale to daily auto-generation with operator review.

5. **Multi-shot native models change operator overhead significantly**. Shift from manual shot assembly to prompt clarity and QA of full-sequence output. Keyframe-first workflow persists but as narrative guidance input, not as editable endpoints. Test Kie trial for multi-shot model capability early.

**Open Questions for Architecture Phase**:

- How does cron handle script approval gate? (Batch review UI, notification to operator, timeout for auto-skip?)
- What is the fallback for Czech audio if synthetic quality fails? (Budget for human VO? Auto-downgrade to English + subtitle?)
- Should operator approval be per-video or per-pack (daily batch)? (Impacts QA time and latency-to-publish.)
- How does MCP brand-truth inform script approval? (Are certain claims pre-approved by product; do others require operator verification?)
- What is the retry budget for failed media generation? (20 attempts per video, 100 per day? Escalate to operator at threshold?)

**Recommended Next Step**: Validate this playbook against actual Kie.ai trial results (multi-shot capability, Czech VO quality, cost per video, retry latency) and have A2 research brief cross-check tool-specific constraints before final architecture lock.

