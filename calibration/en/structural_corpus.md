# English Structural-Calibration Corpus

**Governing plan sections:** ARCHITECTURE_PLAN.md §14.2 (layer 2 — structural heuristics), §14.4 (English rubric), §17.2 Phase 0, ruling R2-M15.

**What this file is.** The curated English exemplar corpus from which layer 2's structural
bands (sentence-length variance, em-dash density, bullet vagueness vs. density, opener
repetition) will be **measured, not authored**. Per R2-M15, the English structural-threshold
measurement pass is a Phase-0 deliverable: until a real tokenisation and measurement pass runs
over this corpus, the English numeric bands are **undefined** and the English judge runs
deliberately lenient with its flag-rate ceiling recorded as inactive.

**Design note carried over from §14.4:** the corpus's *craft* is borrowed while its *hype
language and gamified hard CTAs are explicitly rejected* — several of the corpus's
best-performing posts would fail this project's own rules if reproduced verbatim. Each
exemplar below is annotated accordingly. An exemplar being in this corpus means "measure its
structure", never "imitate its claims or its CTA mechanics".

**Status:** exemplars extracted and cited — DRAFT curation, needs operator confirmation that
this is the intended English exemplar set. Bands table empty pending measurement tooling.

---

## 1. LinkedIn long post exemplars

Structural spec (plan §3.3): 3,000-char hard cap; ~210 desktop / ~140 mobile visible before
the fold; highest median engagement at 1,300–2,500 characters; 3–5 hashtags norm.

### EN-LI-01 — "LinkedIn SDR that runs 24/7" (system-reveal post)
Source: `docs/marketing/Winning Posts from competitors Linkedin.txt` (post 1, lines 3–35).
Structural notes: one-line tool-result hook; short 1–2 sentence paragraphs; problem framed as
an 80/20 split; arrow-bullet capability list (4 items); second arrow list itemising the lead
magnet; question CTA + link. Hype markers present (🚀, 🔥) — structure borrowed, hype rejected.

> We turned Claude COWORK + GojiberryAI into a LinkedIn SDR that runs 24/7.
>
> At YASO, we don't spend on paid marketing, but we do a lot of direct outreach. We send 250+ LinkedIn messages a week to prospects and potential clients.
>
> We needed a system that could keep up. So we built one [...]
>
> The problem with traditional prospecting? You spend 80% of your time figuring out WHO to contact.
>
> And 20% writing messages nobody reads.
>
> [...] Here's what runs while I focus on other tasks:
> → Scans 1,000+ profiles to detect real buying signals
> → Adapts tone based on the prospect's seniority level
> → Manages conversation threads over multiple days without losing context
> → Knows exactly when to push for a call and when to back off

### EN-LI-02 — "just killed manual prospecting" (before/after post, single-block variant)
Source: same file, post 2 (line 39).
Structural notes: the whole post is one paragraph block — a deliberate outlier for the
paragraphing measurement. "No more X. No more Y. No more Z." triple; arrow list; goal line;
comment-gated CTA (rejected mechanic).

### EN-LI-03 — "just killed manual prospecting" (line-broken variant)
Source: same file, post 3 (lines 44–80).
Structural notes: same template as EN-LI-02 re-lineated one sentence per line — the pair is a
measurement gift: identical lexical content, different structural shape. "The difference? 12+
hours saved." short-sentence pivot; two arrow lists; link CTA.

### EN-LI-04 — "I built 3 sales AI agents" (giveaway post)
Source: same file, post 11 (lines 403–435).
Structural notes: builder-claim hook + parenthetical give-away line; ➤ bullet trio; "Most B2B
teams are still doing outbound like it's 2019." — direct-observation contrast hook mid-post;
bolded Unicode subheads (𝗥𝗲𝘀𝗲𝗮𝗿𝗰𝗵 𝗮𝗴𝗲𝗻𝘁 — note: Unicode bold survives tokenisation
badly, measurement pass must normalise); direct link CTA (no comment gate — closest to an
allowed CTA class in the whole corpus).

### EN-LI-05 — "R.I.P generic cold emails" (authority/contrast post)
Source: same file, post 12 (lines 442–482).
Structural notes: R.I.P. hook; one-word paragraph rhythm ("GPT. / Gemini. / Grok. / Llama.");
9-item arrow list (top of the bullet-density range); "The result? / Outbound that feels human.
/ At scale." staccato close; comment-gated CTA (rejected). Contains the corpus's flattest
unverifiable claim ("outperforming entire outreach teams") — structure in, claims out.

### EN-LI-06 — "LK prospecting is still 90% guesswork" (myth-busting post)
Source: same file, post 13 (lines 486–539).
Structural notes: stat-shaped hook; ❌ negative list vs → positive list opposition; "That
worked 12 months ago. / Not anymore." two-beat pivot; "The real unlock isn't the writing. /
It's the intelligence layer." contrast pair; P.S. line; repost bait (rejected mechanic).

### EN-LI-07 — "BYE BYE manual outreach" (result-story post, variant A)
Source: same file, post 14 (lines 543–595).
Structural notes: "I woke up to this email today:" — concrete personal-stake moment, the
corpus's best personal-stake exemplar; numbered workflow (1–5); example sub-list; "The
difference is intent." thesis sentence; —> arrow results pair; P.S. coda.

### EN-LI-08 — "BYE BYE manual outreach" (variant B, different author)
Source: same file, post 15 (lines 599–633).
Structural notes: near-identical template to EN-LI-07 published under a different name —
**kept in the corpus deliberately as the documented house-tic/recurrence phenomenon** the
cross-pack recurrence check (§14.2 layer 1) exists to catch in our own output. Counts toward
opener-repetition statistics; must NOT count twice toward "normal" band mass — measurement
pass should tag the pair as one template family.

### EN-LI-09 — "one excellent post per day" (interview pull, narrative post shape)
Source: `docs/marketing/Gojiberry's 7 Figure GTM Playbook.txt` (lines 43–45, 143–145).
Structural notes: first-person practice statement; concrete schedule ("8am to 2pm is content
[...] 2pm to 8pm is sales calls"); direct quote as proof of stake. Article prose, but
post-shaped — included as the personal-stake register reference.

### EN-LI-10 — "Intent-based outbound numbers" (data-anchored prose)
Source: same file, lines 56–67 and 127–137.
Structural notes: the specificity/proof-anchoring reference exemplar — every claim carries a
number and an owner ("Our best campaigns hit 62% acceptance rate with 49% reply rate. Out of
100 people contacted, that's 30 replies. Market average is about 5. That's 6x."). Sentence
rhythm: short declaratives with arithmetic shown.

## 2. Carousel / document-carousel copy exemplars

Structural spec (plan §3.2/§3.3): 5–15 slides target (7–13 typical); per-slide headline +
support line; narrative arc; first-and-last-slide conventions; on-image text density limits.

No native carousel exists in `docs/marketing`. Two step-sequence sources carry the closest
real slide-shaped copy; both are **structural proxies**, marked as such.

### EN-CA-01 — Playbook problem/solution sequence (proxy)
Source: `docs/marketing/The-LinkedIn-High-Intent-Outreach-System-How-We-Booked-12-demos-in-5-days.md` (lines 24–48).
Slide-shaped beats as published: "Here's the brutal truth about LinkedIn outreach in 2025:" →
"1-2% response rate" → "Takes 100 messages to book 1 meeting" → "People are defensive from the
start" → [contrast] "25-40% response rate" → "Takes 10 messages to book 1 meeting" → "Intent
signals." — a clean 7-beat problem/contrast/reveal arc.
[PROXY — needs operator approval as carousel exemplar; a real published carousel would be better]

### EN-CA-02 — 7-step feature sequence (proxy)
Source: `docs/marketing/Winning Posts from competitors Linkedin.txt` (post 8, lines 287–324):
"1/ Détecter…" pattern rendered in its EN sibling structure — numbered slide-per-capability,
headline + one support line each, 7 beats + CTA slide.
[PROXY — needs operator approval as carousel exemplar]

### EN-CA-03 .. EN-CA-05 — [OPERATOR TO SUPPLY — real published carousel exemplars needed]
Target: 3+ real LinkedIn document carousels or IG carousels from own/competitor accounts,
5–15 slides, B2B lead-gen niche, with per-slide text transcribed.

## 3. Short-form video script exemplars

Structural spec (plan §3.3/§4.5): 9:16; TikTok sweet spot 21–34 s; Shorts 20–40 s target;
Reels 15–60 s target; hook in first 3 seconds; EN default recipe is generative-clip led.

**Gap, recorded honestly:** the intended source files
`docs/marketing/GojiBerry_YoutubeInspiration/*.txt` (GojiBerry_0_to_1_Mil, 90_Day_Playbook,
ColdEmail_01, Reddit_01) are **empty (0 bytes)** in the repo. There is no real EN short-form
script exemplar to extract.

### EN-SF-01 .. EN-SF-05 — [OPERATOR TO SUPPLY — transcripts of real short-form videos needed]
Suggested source: the Gojiberry video that per the playbook "drove +$30K in MRR and hit 1M+
views" (Gojiberry's 7 Figure GTM Playbook.txt, line 24/70) — its transcript would be the
anchor exemplar. Until supplied, the EN short-form band row stays empty and the judge has no
short-form structural baseline.

## 4. Caption / short-copy exemplars

Structural spec (plan §3.3): IG caption 2,200 cap, ~125 chars visible — front-load; TikTok
caption 4,000, first line visible, doubles as search surface; link-in-bio CTA shapes only.

No native captions exist in `docs/marketing`. The playbook's DM scripts are included as
short-copy *rhythm* references only (they are DMs, not captions):

### EN-SC-01 — 23-word opener
Source: `The-LinkedIn-High-Intent-Outreach-System...md` (line 122):
> Hey [Name], Quick question - what's your biggest challenge with [topic] right now?

### EN-SC-02 — 27-word follow-up
Source: same file (line 130):
> Interesting - we just solved that exact problem for [similar company]. Mind if I send you a 3-minute video showing how?

### EN-SC-03 — 29-word re-engage
Source: same file (line 146).

### EN-SC-04 .. EN-SC-06 — [OPERATOR TO SUPPLY — real published IG/TikTok captions needed]

---

## Measurement-pass template

**To be filled by a real tokenisation and measurement pass — the bands are OUTPUTS of
measurement, not authored.** (§14.2 layer 2, §17.2 Phase 0, R2-M15.) No cell below may be
filled by hand, from memory, or from a vendor blog (R-26). The pass must: normalise Unicode
(incl. mathematical-bold glyphs, EN-LI-04), tag template families so near-duplicates
(EN-LI-07/08) do not double-count, and record tokeniser identity + version beside the numbers.

| Destination / asset type | n exemplars | Median tokens | Token band (p25–p75) | Median chars | Char band (p25–p75) | Mean sentence length (words) | Sentence-length variance band | Em-dashes / 100 words | Bullet lines / 100 words | Opener-pattern notes |
|---|---|---|---|---|---|---|---|---|---|---|
| LinkedIn long post | | | | | | | | | | |
| Document/IG carousel (per slide) | | | | | | | | | | |
| Short-form video script | | | | | | | | | | |
| Caption (IG/TikTok/Shorts) | | | | | | | | | | |
| Facebook community post | | | | | | | | | | |

Measurement-pass run log (append-only): *none yet.*
