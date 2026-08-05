# C2 — Platform Hard Constraints (List B) + Stack Verification (D-06)

Wave 1 research brief — agent T10. Written 2026-08-06. Design phase only: no code, no config syntax.
Scope: Part 1 = per-platform hard constraints for the content destinations in List B (LinkedIn, X, Instagram, TikTok, YouTube Shorts, Facebook, blog). Part 2 = verification of the Python working hypothesis for D-06, Windows Task Scheduler ergonomics, Linux-cron parity, and a stack recommendation.

---

## 1. What this means for the operator

Every platform we publish to has its own hard box: how long a post can be, what shape a picture or video must have, how long a video may run, and — new for 2026 — how AI-made content must be labeled. The good news for Czech content: on every platform except none, letters like š, č, ř, ě count as **one character, same as English letters** — including on X, which has the strictest limit (280 characters free, 25,000 with Premium). Links on X always "cost" 23 characters no matter how long they are. Instagram and TikTok captions cannot contain clickable links at all — the only clickable link lives in the profile bio, which changes how we write calls-to-action there. The practical video shape everywhere is vertical 1080×1920 (9:16); the practical carousel shape is portrait 1080×1350 (4:5). Sweet spots are much smaller than the maximums: LinkedIn posts read best at 1,300–2,500 characters, short videos at roughly 15–35 seconds, carousels at 5–10 slides.

On AI labeling: TikTok, YouTube, and Meta each have their **own** mandatory disclosure switch for realistic AI content (a checkbox or API field at upload time), and separately the **EU AI Act's transparency rules start applying on 2 August 2026** — so our review package must record, for every asset, whether it needs the "AI-generated" flag, and the publishing step must actually set that flag. Google does **not** punish blog articles for being AI-assisted — it punishes low-value mass-produced content — so the human-review gate we already planned is also our SEO insurance.

On technology: the research **confirms Python** as the right stack. Every library we need (Anthropic/OpenAI/Google AI SDKs, the MCP protocol for Notion brand-truth, Playwright for browsing) is first-class in Python. The one real trap is Windows scheduling: a task run under the SYSTEM account cannot see the operator's browsers or decrypt the operator's saved secrets, and the Czech Windows console does not speak UTF-8 by default. The design answer is simple: run scheduled jobs **as the operator's own account**, force UTF-8 everywhere explicitly, write everything to log files, and never rely on anything the operating system "usually" provides — then the same job moves to a Linux server cron with almost no changes.

---

## 2. Body

### 2.1 Character limits, Czech character counting, links, hashtags (mandate item 1)

**How platforms count Czech text.** All List B platforms count Unicode characters (code points after normalization), not UTF-8 bytes. Czech diacritic letters (á é í ó ú ů ý č ď ě ň ř š ť ž) live in Latin-1 Supplement and Latin Extended-A (below U+0180) and are single code points in NFC form — so one Czech letter = one character on LinkedIn, Instagram, TikTok, Facebook, and YouTube. X is the only platform with weighted counting, and it is verified favorable: X normalizes to NFC and counts code points U+0000–U+10FF (decimal 0–4351) at weight 1 — the twitter-text v3 configuration file lists exactly the ranges 0–4351, 8192–8205, 8208–8223, 8242–8247 at weight 100 out of 200 — which covers all Czech letters. Emoji always count as 2 on X; CJK counts as 2. **Design rule:** the character-count validator must normalize to NFC before counting, count code points (not bytes), and apply X's weighting table plus the fixed 23-character URL cost only on X.

**Per-destination limits (verified 2026 values):**

| Destination | Asset | Hard limit | Visible-before-truncation | Engagement sweet spot |
|---|---|---|---|---|
| LinkedIn | Post | 3,000 chars | ~210 desktop / ~140 mobile before "see more" | 1,300–2,500 chars (highest median engagement) |
| LinkedIn | Article | ~110,000 chars body; headline 100 | — | long-form; blog-first rule applies |
| LinkedIn | Comment | 1,250 chars | — | — |
| X | Post | 280 weighted chars free; 25,000 Premium | Premium long posts collapse to preview + "Show more" | 71–100 chars; threads 4–8 posts, one idea per post |
| X | URL in post | Always 23 chars via t.co, any real length | — | — |
| Instagram | Caption | 2,200 chars | ~125 chars before "more" | front-load first 125 chars |
| Instagram | Bio | 150 chars | — | only clickable link surface |
| TikTok | Caption | 4,000 chars (raised from 2,200) | first ~1 line in feed | keyword-rich for TikTok SEO |
| YouTube (Shorts) | Title | 100 chars | ~40 chars in Shorts feed | <50 chars |
| YouTube (Shorts) | Description | 5,000 chars | ~150 before "Show more" | — |
| Facebook | Post | 63,206 chars | collapses after ~400 chars | 40–80 chars for community posts |
| Blog | Article | none | — | SEO-driven; see 2.4 |

**Link handling per platform.**
- X: every URL costs a flat 23 characters (t.co wrap). External links are widely reported to depress organic reach; norm is link-in-reply for threads (medium confidence — algorithmic, unannounced).
- LinkedIn: links allowed in posts; the long-standing operator norm of "link in first comment" to protect reach is contested in 2026 — treat as a per-theme style choice, not a hard rule (low-medium confidence).
- Instagram: **caption links are not clickable** — hard constraint. CTAs must point to the bio link or use Stories link stickers. Design implication: IG CTA templates must be "link in bio" style.
- TikTok: same — organic caption links are not clickable; clickable website link requires business account bio. Same CTA implication as IG.
- Facebook: links auto-expand to a preview card; posting the bare URL is fine, no counting quirk.
- YouTube: links allowed in description; links are not clickable in Shorts overlay text.

**Hashtag norms (all hashtags count toward the character limits everywhere).**
- LinkedIn: 3–5 relevant hashtags.
- Instagram: hard max 30 per caption; current best practice 3–5.
- TikTok: 3–6, keyword-style (caption acts as search surface).
- X: 1–2 max; more reads as spam.
- Facebook: 0–2; hashtags carry little weight.
- YouTube Shorts: 1–3 in title/description; the dedicated #Shorts tag is no longer required for classification (medium confidence).

### 2.2 Aspect ratios, resolutions, carousels, durations, captions (mandate item 2)

**Canonical shapes.** Two master formats cover nearly all of List B: **1080×1350 (4:5 portrait)** for feed stills and carousels, and **1080×1920 (9:16 vertical)** for Reels / TikTok / Shorts / Stories / Facebook Reels. Producing these two plus an optional 1200×675 (16:9) for X covers every destination.

| Destination | Asset | Ratio / resolution | Count / duration limits | Sweet spot |
|---|---|---|---|---|
| LinkedIn | Document post (carousel) | PDF, 1080×1350 recommended (also 1:1, 16:9) | up to **300 pages**, 100 MB; PDF renders most consistently | 5–15 slides |
| LinkedIn | Feed image | 1200×627 (1.91:1), 1080×1080, 1080×1350 | — | portrait for mobile reach |
| Instagram | Carousel | 4:5 at 1080×1350 recommended; **whole carousel locked to first slide's ratio** | up to **20 slides** (raised from 10 in 2024); video slides ≤60 s / 4 GB each | 5–10 slides |
| Instagram | Reel | 9:16, 1080×1920 | max **20 minutes** (raised during 2026 from 3 min); **Reels >3 min are not recommended to non-followers** | 15–60 s; ≤90 s for reach |
| TikTok | Video | 9:16, 1080×1920 | in-app record 10 min; upload up to 60 min | **21–34 s** |
| TikTok | Photo post (slideshow) | 9:16, 1080×1920, ≤20 MB/photo | up to **35 images** | 5–10 slides |
| YouTube | Shorts | 9:16, 1080×1920 | ≤ **3 minutes** (since Oct 2024; longer = regular video) | 20–40 s |
| Facebook | Reel / video | 9:16, 1080×1920, ≥30 fps, MP4/MOV, ≤4 GB | since mid-2025 all videos publish as Reels, no practical length cap; legacy 90 s figure still cited | 15–30 s |
| Facebook | Feed image | 1:1 or 4:5 | — | — |
| X | Images | up to 4 per post, ≤5 MB each (GIF ≤15 MB); 1200×675 for single landscape; 4-image grid crops to 2:1 | — | consistent sizes within threads |
| X | Video | 16:9 or 9:16, 1280×720+ | free: 2 min 20 s / 512 MB; Premium: up to ~4 h at 1080p / 16 GB (web+iOS; Android ~10 min) | <60 s organic |

**Caption/subtitle rules for video assets (design-relevant, medium confidence — practice, not published spec):**
- Burned-in (open) captions are the norm for Reels/TikTok/Shorts because a large share of feed viewing is muted; every video plan should include an on-screen text/caption track.
- TikTok auto-generates closed captions and enables them by default; Instagram and YouTube offer auto-captions; burned-in captions must not fight the platform's auto-caption placement.
- Safe zones: keep text and captions inside the central area — roughly avoid the top ~10%, bottom ~15–20% (progress bar, caption row, description) and the right-hand ~15% (action buttons) on all three vertical platforms. Templates for 9:16 assets must encode these margins.
- Hook text in the first 1–3 seconds and readable on-image text only (ties to the F-quality rules on AI-slop rejection).

### 2.3 AI-content-label mechanics per platform (F-8) (mandate item 3)

These are **platform obligations, separate from EU AI Act Article 50** (which binds us as provider/deployer regardless of platform). Both layers apply simultaneously.

**TikTok — AIGC label.**
- What triggers it: mandatory self-disclosure for content that is realistic and entirely AI-generated or significantly AI-edited — synthetic or altered people, places, events; AI speech/voice clones; photorealistic AI products. Clearly stylized/unrealistic AI content does not require the label but may still carry it.
- Where the flag lives: (a) UI toggle in the upload flow ("AI-generated content"); (b) **API field** — the Content Posting API Direct Post endpoint exposes an AIGC boolean parameter (named "is_aigc", defaults to false) that applies the "Creator labeled as AI-generated" tag; (c) **automatic labeling** via C2PA Content Credentials metadata read at upload.
- Enforcement: TikTok's detection can auto-label, reduce distribution of, or remove unlabeled realistic AI content; TikTok states the label itself is not a reach penalty.
- Design implication: every video/slideshow asset must carry an internal "AI-label required" flag; if publishing ever goes through TikTok's API (directly or via Postiz), that flag must map to the AIGC parameter; if a human publishes manually from the review package, the package must instruct them to set the toggle.

**YouTube — altered/synthetic content disclosure.**
- What triggers it: content that could be mistaken for real — a real person appearing to say/do something they didn't, altered footage of real events/places, realistic scenes that didn't happen. Clearly fictional/animated/stylized content and productivity uses (scripts, ideas) are exempt.
- Where the flag lives: (a) "Altered content" question in the YouTube Studio upload flow; (b) **API field** — YouTube Data API v3 supports the boolean "containsSyntheticMedia" property under the video status object, settable on video insert/update (added 30 Oct 2024). Label appears in the description ("Altered or synthetic content"), and more prominently on sensitive topics.
- Enforcement 2026: YouTube has rolled out automatic detection with proactive, non-removable labels for detected undisclosed synthetic content; repeated non-disclosure risks strikes/monetization penalties.
- Design implication: same per-asset flag; the review package for Shorts must state "answer YES to the altered-content question" when the flag is set.

**Meta (Instagram + Facebook) — "AI info" / "Made with AI" label.**
- What triggers it: photorealistic AI-generated or significantly AI-altered image/video/audio. Mandatory self-disclosure applies to realistic video/audio; Meta also auto-applies labels when it detects **C2PA / IPTC provenance metadata** in the uploaded file (rollout since 2024, expanded through 2026 across FB, IG, Threads, WhatsApp Channels).
- Where the flag lives: organic posting UI toggle at publish time (creator self-disclosure); no clearly documented organic Graph/Content Publishing API field as of Aug 2026 (auto-detection via embedded metadata is the machine path) — **open item to verify against the Instagram Content Publishing API before build**. Ads have a separate, mandatory AI-disclosure toggle in Ads Manager (2026 rules, actively enforced with rejection/strike escalation) — relevant only for the later paid phase.
- Meta states the organic label is disclosure, not a reach penalty.
- Design implication: because Meta's machine path is metadata-driven, our asset pipeline should **preserve C2PA Content Credentials** emitted by generation providers (Kie.ai routes to models that increasingly embed credentials) rather than stripping metadata during re-encode; then Meta labels correctly even on manual upload.

**Cross-platform layer — EU AI Act Article 50 (separate obligation).**
- Transparency obligations under Article 50 apply from **2 August 2026** — i.e., already in force during this project's build. Two duties matter to us: (i) Art. 50(2): providers of generative systems must ensure outputs are marked machine-readably as AI-generated (this largely sits with model/tool providers, but we assemble and re-encode assets, so we must not destroy the marking, and where we operate generation pipelines we inherit provider-like duties); (ii) Art. 50(4): deployers must visibly disclose deepfakes and certain AI-generated text; ordinary marketing content with human editorial review is in a lighter position, but realistic synthetic humans/voices in our reels trigger disclosure regardless of platform toggles.
- Status caveat: the Digital/AI Omnibus proposal contemplates moving the Art. 50(2) marking-and-detection deadline to **2 December 2026**; not formally adopted — track it.
- The European Commission is preparing a **Code of Practice on transparency of AI-generated content** (draft published; adherence is the low-friction compliance route).
- Design implication: one internal per-asset field ("AI-content class: none / assisted / realistic-synthetic") drives (a) platform flags, (b) visible disclosure text where required, (c) metadata preservation. This is cheaper than per-platform ad-hoc handling and satisfies both layers.

### 2.4 Blog: SEO and AI-content policy state, 2026 (mandate item 4)

- No hard character/format limits. Constraints are quality constraints.
- Google's standing policy (unchanged through 2026): AI-generated content is **not** penalized for being AI-generated; quality, originality, and usefulness are judged regardless of production method. What is penalized: **scaled content abuse** (mass-produced low-value pages), site-reputation abuse, and thin content. 2026 core updates continue to reward demonstrable E-E-A-T (experience, expertise, authoritativeness, trust) and to demote generic "robotic" AI text.
- Practical bar for this system: blog output is safe exactly because of the designed human gate — human review/edit, real brand facts from the brand-truth layer, no invented metrics, named author where possible. Volume caps per run (already a cron budget concept) also keep us clearly outside "scaled abuse" territory.
- Google requires no AI-disclosure label; the EU AI Act text-transparency duty (Art. 50(4)) has an exemption where AI-assisted text has undergone human review with editorial responsibility — which our workflow provides by design. Note it, don't over-engineer it.
- Secondary trend worth one design hook: AI answer engines (AI Overviews, LLM search) reward clearly structured, citable pages — an argument for the blog-first-then-atomize rule already in the assignment.

### 2.5 Python vs Node/TypeScript for this system (mandate item 5)

Judged criterion by criterion; working hypothesis was Python.

| Criterion | Python | Node/TypeScript | Verdict |
|---|---|---|---|
| MCP client maturity | Official MCP Python SDK; beta released in lockstep with TS for the 2026-07-28 spec (both Tier-1). Anthropic's Python SDK additionally ships MCP conversion helpers that plug MCP tools straight into its tool-runner. | Official TS SDK (historically first; v2 client/server packages). | **Parity**; Python has the nicer Anthropic-SDK bridge. |
| Notion MCP | Notion's supported path is the **hosted remote server** (mcp.notion.com, Streamable HTTP + OAuth) — language-agnostic; any compliant client connects. Local server repo may be sunset. | Same. | **Neutral** — decision unaffected by language. |
| LLM SDK coverage | Anthropic, OpenAI, Google Gen AI all ship first-class official Python SDKs (Google's unified google-genai SDK is GA, latest release July 2026). | All three equally official in TS/JS. | **Parity.** |
| Playwright | Core automation at full parity (auto-waiting, tracing, codegen). Python spawns a Node driver process per instance — a minor overhead irrelevant at our scale (a handful of concurrent pages). | Native home of Playwright; test-runner extras we don't need (we automate, we don't run test suites). | **Node slightly ahead, immaterial here.** |
| Async job orchestration | asyncio + mature scheduling/queueing libraries; our pipeline is IO-bound, low-concurrency, sequential-stage — trivially served. Rich data-wrangling ecosystem for the research/ranking stages is a genuine plus. | Event loop native; equally capable. | **Parity; Python +ecosystem for ranking/data stages.** |
| Distribution to a Windows operator | Honest finding: a true single-file EXE is **not achievable for this system in either language**, because Playwright's browser binaries (hundreds of MB) always live outside the executable. Realistic model: versioned project + locked dependencies + a modern Python manager (uv) that installs the interpreter and env in one step + a thin launcher. PyInstaller one-file exists as fallback (mature, but ~100–200 MB artifacts, slow cold start, AV false-positive risk). | pkg is deprecated (archived; community fork yao-pkg); Node SEA is stable since Node 22 / improved in 24 but asset bundling and native modules remain fiddly — and the browser-binary problem is identical. | **Python wins on the realistic path** (uv-style managed checkout), tie on the illusory single-exe path. |
| Cross-platform console behavior | Needs explicit UTF-8 discipline until Python 3.15 makes UTF-8 mode default (PEP 686 accepted); mitigable today with one environment switch and explicit encodings. | Strings are UTF-16 internally, output UTF-8; still hits legacy Windows console codepages for display. | **Parity** — both require the "explicit UTF-8 everywhere" design rule. |
| Adjacent facts | Postiz is a TypeScript product, but we integrate over its REST API, not in-process — no language pull. Kie.ai / Higgsfield are HTTP APIs — neutral. | | |

Conclusion: **Python confirmed** — no criterion disqualifies it, two criteria favor it (distribution realism, data/ranking ecosystem + Anthropic MCP bridge), and the only Node edge (Playwright nativeness) is immaterial at this workload.

### 2.6 Windows Task Scheduler ergonomics for the unattended console app (mandate item 6)

**SYSTEM-account gotchas (all confirmed patterns):**
- SYSTEM runs with its own profile under the Windows system profile directory; its local-app-data path is **not** the operator's. Playwright installs browsers per-user in the user's local app data — so a job scheduled as SYSTEM finds **no browsers**. Fixes: run the task as the operator account, or pin the Playwright browsers directory to a shared machine-wide path via its dedicated environment variable, set both at install time and run time.
- DPAPI and Windows Credential Manager secrets are **per-user**: anything encrypted under the operator's account cannot be decrypted by SYSTEM (and vice versa). If secrets are DPAPI-protected, the encrypting account and the task account must be the same account.
- SYSTEM has no interactive desktop and different network identity; mapped drives don't exist for it.
- **Design decision this forces:** schedule the job under a dedicated standard user account (the operator account or a service user), "run whether user is logged on or not", highest privileges only if needed — not SYSTEM. This makes browser profiles, DPAPI, and credential stores line up.

**UTF-8 / Czech locale in console and scheduled context:**
- Czech Windows consoles default to legacy code pages (852 OEM / 1250 ANSI); Python before 3.15 uses the ANSI code page for default file encoding and the console code page for stdio — Czech diacritics then mangle in redirected logs or crash on encode. PEP 686 makes UTF-8 mode the default only in Python 3.15; until then the design must set Python's UTF-8 mode environment switch for every entry point (interactive and scheduled) and open every artifact file with explicit UTF-8.
- In the scheduled (no-console) context there is no code page at all — stdout goes to whatever the wrapper redirects it to; the rule "never rely on ambient encoding, always declare UTF-8" removes the whole class of bugs on both OSes.

**Exit-code propagation and the run.bat reality:**
- Task Scheduler records the process exit code as "Last Run Result" (0x0 = success). The infamous 0x1 result usually means: the wrapper script's last command failed, the working directory wasn't set (the task's "Start in" field left empty — must be set, unquoted), or environment differences (PATH) broke a command.
- If a batch wrapper is used, it must end by explicitly exiting with the child process's error level, otherwise the app's carefully designed exit codes (success / partial / fail-closed) never reach the scheduler. Cleaner: register the interpreter/launcher executable directly as the task action with arguments, and keep the wrapper only for environment setup (UTF-8 switch, env-file loading, log redirection to dated files).
- Because the scheduled console is invisible, **file logging is the only observability** — the app writes its own logs; the wrapper additionally captures stdout/stderr to a file as a safety net.
- Fail-closed mapping (ties to assignment constraint 15): reserve distinct exit codes for "completed", "completed with skips", "blocked by policy/missing secrets", "crashed" — Task Scheduler shows them verbatim, and the same codes work under cron.

### 2.7 Linux-cron parity (mandate item 7)

**What is different under cron:**
- Minimal environment: PATH is just the two system bin directories; no LANG/LC_ALL → **POSIX/C locale → ASCII encoding** — the classic way Czech UTF-8 breaks server-side. Interactive shell dotfiles are not read.
- Crontab quirks: percent signs must be escaped, no variable expansion in the crontab itself, jobs run under a minimal shell, unhandled output is mailed rather than logged.
- Cron has no "Start in" concept — relative paths break exactly like the empty Start-in field on Windows.

**What breaks moving Windows → Linux, and the design that avoids it:**

| Breakage class | Windows form | Linux form | Design avoidance |
|---|---|---|---|
| Encoding | ANSI cp1250 defaults | C/POSIX locale under cron | App forces UTF-8 mode itself and opens all files with explicit UTF-8; never trusts ambient locale. Same rule fixes both. |
| Secrets | DPAPI / Credential Manager (per-user, Windows-only) | env files, keyring, or secret manager | A secrets interface with pluggable backends; the contract is "secrets arrive as environment/config values", never "read the OS vault directly" in pipeline code. Fail closed when absent. |
| Paths & FS | backslashes, case-insensitive | slashes, case-sensitive | All paths come from config, resolved to absolute at startup; consistent lowercase artifact naming; no hard-coded separators. |
| Scheduler semantics | Task Scheduler triggers, Last Run Result | cron expressions, exit status + mail | The app is scheduler-agnostic: one non-interactive entry mode, documented exit codes, own logs, own lock/dedupe file for idempotency (both schedulers can double-fire). Thin per-OS wrapper is the only OS-specific piece. |
| Timezones | Windows zone names | IANA zone names | Config uses IANA names everywhere; schedule cadence documented in one place. |
| Playwright browsers | per-user local app data | per-user cache dir; distro deps needed | Browsers path pinned via Playwright's environment variable to a project-owned directory on both OSes; install step is part of setup checklist. |
| Line endings | CRLF | LF | Repository policy: LF for all config/content artifacts. |

Bottom line: if the console app owns its encoding, paths, secrets access, logging, locking, and exit codes — treating the scheduler as nothing more than "something that starts the process" — the Windows→Linux move is a wrapper rewrite, not an application change.

### 2.8 Stack recommendation (mandate item 8)

**Recommended: Python 3.12/3.13, distributed as a uv-managed project checkout with locked dependencies and a thin per-OS launcher; Playwright (Python) for browser automation; official Anthropic + OpenAI + Google Gen AI SDKs; official MCP Python SDK (Notion via the hosted remote MCP server); scheduling via Task Scheduler under the operator account now, cron later.** Move to Python 3.15 when released to retire the explicit UTF-8 switch.

Rejected alternatives (≥2 required):

1. **Node.js/TypeScript end-to-end.** Rejected. Parity on MCP and LLM SDKs; slight Playwright edge is immaterial at our concurrency; but the Windows distribution story is worse (pkg deprecated/archived with a community fork; SEA stable but asset/native-module friction), the data-wrangling ecosystem for the research/ranking stages is thinner, and the Anthropic Python SDK's MCP bridge is a concrete accelerator. Postiz being TypeScript is irrelevant — we integrate via its REST API.
2. **Single-file executable packaging (PyInstaller one-file, or Node SEA/Bun compile).** Rejected as the primary distribution mode. Playwright's browser binaries cannot live inside any single executable, so the "one file" promise is false for this system; one-file bundles add ~100–200 MB artifacts, multi-second cold starts, and antivirus false-positive risk. Kept as an optional later convenience for a browserless subset only.
3. **C#/.NET console app.** Rejected. Best-in-class Windows service/Task Scheduler ergonomics and an official Anthropic SDK exist, but MCP tooling, LLM-ecosystem velocity, and Playwright bindings all trail Python/TS, and it doubles the skill surface against every other AI-tooling choice in this project.
4. **(Considered, deferred rather than rejected)** Containerized Linux-first runtime from day one — clean cron story, but conflicts with the Windows-first operator requirement (D-05); revisit at the server-migration phase.

---

## 3. Decision table

| # | Decision unblocked | → Architecture area |
|---|---|---|
| U1 | Czech text counts 1:1 on all platforms; X weighting (NFC, 0–4351 = weight 1, emoji = 2, URL = 23) is fully specified → a deterministic per-platform length validator can be designed | Asset validation / review package |
| U2 | Two master visual formats (1080×1350 4:5, 1080×1920 9:16) + 16:9 for X cover List B | Media pipeline / template system |
| U3 | Hard caps for generation: IG carousel ≤20 slides, TikTok slideshow ≤35 images, LinkedIn PDF ≤300 pages (target 5–15), Shorts ≤3 min, sweet-spot durations 15–35 s | Content generation budgets |
| U4 | IG + TikTok organic captions cannot carry clickable links → "link in bio" CTA variants are a required template dimension | Copy/CTA templating per platform |
| U5 | One internal per-asset "AI-content class" field drives TikTok AIGC flag, YouTube containsSyntheticMedia, Meta toggle/metadata, and EU AI Act disclosure — platform flags exist and are documented | Compliance layer / review package / publishing adapter |
| U6 | Preserve C2PA/provenance metadata through the media pipeline (never strip on re-encode) | Media pipeline |
| U7 | Blog: human-gated, capped-volume AI-assisted articles are policy-safe under Google's 2026 stance — no extra SEO machinery needed at design time | Blog pipeline |
| U8 | Stack = Python (see 2.8); Node, single-exe packaging, and .NET rejected with rationale | D-06 closed |
| U9 | Scheduled runs execute under the operator/service **user** account, never SYSTEM (browsers, DPAPI, credential store alignment) | Scheduler architecture |
| U10 | App is scheduler-agnostic: explicit UTF-8, absolute paths from config, pluggable secrets interface, file logging, lock-file idempotency, documented exit codes (success / partial / policy-block / crash) | Runtime core; makes Windows→Linux a wrapper swap |
| U11 | Register the interpreter directly as the task action (wrapper only for env setup); always set the task working directory; propagate exit codes explicitly | Windows deployment runbook |

| # | Decision deferred | → Open decision |
|---|---|---|
| D1 | Does Postiz pass through TikTok's AIGC flag / YouTube's synthetic-media field / Meta's AI toggle when creating drafts? | Verify against Postiz API before making Postiz the compliance path; otherwise manual-publish instructions carry the flags |
| D2 | Meta organic API field for AI self-disclosure (vs metadata-only) | Verify against Instagram Content Publishing API docs at build time |
| D3 | EU AI Act Art. 50(2) marking deadline: 2 Aug 2026 in force vs Omnibus shift to 2 Dec 2026 | Track legislation; adopt the transparency Code of Practice either way |
| D4 | Whether Kie.ai / Higgsfield outputs carry C2PA credentials (determines how much labeling is automatic on Meta/TikTok) | Provider-evaluation agent / build-time test |
| D5 | "Link in first comment" norm on LinkedIn (reach folklore vs measurable) | Per-theme style config; A/B later via feedback loop |
| D6 | Exact secrets backend on Windows (ACL-protected env file vs Credential Manager under the task account) | Security design detail at build; interface already fixed by U10 |
| D7 | X Premium subscription assumption (25k chars, long video) per theme/tenant | Theme config decision — validator must support both tiers |
| D8 | LinkedIn native video full spec (durations/codecs) — not fully verified this pass | Re-verify if LinkedIn video becomes a first-class asset type (carousel + post are primary today) |

---

## 4. Fact ledger

All rows retrieved **2026-08-06**. Confidence: H = official/primary source; M = multiple recent secondary sources agree; L = single/contested source. Recheck-by is the date by which the claim should be re-verified before implementation relies on it.

| Claim | Source URL | Retrieved | Conf. | Recheck by |
|---|---|---|---|---|
| X counts NFC-normalized code points; ranges 0–4351, 8192–8205, 8208–8223, 8242–8247 weigh 1; others 2; limit 280 weighted | https://raw.githubusercontent.com/twitter/twitter-text/master/config/v3.json | 2026-08-06 | H | 2027-02 |
| X: URLs always count 23 chars (t.co); emoji count 2; NFC normalization | https://docs.x.com/fundamentals/counting-characters | 2026-08-06 | H | 2027-02 |
| X Premium long posts up to 25,000 chars; free 280 | https://fmax.io/blog/twitter-character-limit-2026 ; https://zeroutil.com/blog/character-limits-social-2026/ | 2026-08-06 | M | 2026-11 |
| X video: free 2:20/512 MB; Premium ~4 h 1080p (web/iOS), 16 GB; Android ~10 min | https://www.nemovideo.com/blog/twitter-video-length-limits ; https://socialk.it/en/sizes/x-video-size | 2026-08-06 | M | 2026-11 |
| X images: 4/post, 5 MB (GIF 15 MB), 1200×675 landscape, 2×2 grid crops 2:1 | https://skedsocial.com/blog/twitter-post-size-guide ; https://influencermarketinghub.com/twitter-image-size/ | 2026-08-06 | M | 2027-02 |
| X engagement: 71–100 chars best; threads 4–8 posts | https://toolsoasis.dev/blog/twitter-x-post-best-practices/ ; https://socialrails.com/blog/how-to-grow-on-twitter-x-complete-guide | 2026-08-06 | L–M | 2026-11 |
| LinkedIn post 3,000 chars; headline 220; about 2,600; comment 1,250; articles ~110,000 | https://authoredup.com/blog/linkedin-character-limit ; https://www.linkedhelper.com/blog/linkedin-character-limit/ | 2026-08-06 | M | 2026-11 |
| LinkedIn truncation ~210 desktop / ~140 mobile; 1,301–2,500 chars = highest engagement; 3–5 hashtags | https://connectsafely.ai/articles/ideal-linkedin-post-length-engagement-guide-2026 ; https://www.viralbrain.ai/tools/linkedin-character-limits | 2026-08-06 | M | 2026-11 |
| LinkedIn document post: ≤300 pages, ≤100 MB; PDF/PPTX/DOCX; 1080×1350 recommended; 5–15 slides perform best | https://postnitro.ai/blog/post/linkedin-post-specs ; https://www.oktopost.com/blog/linkedin-carousel-pdf-best-practices/ ; https://trustypost.ai/blog/linkedin-carousel-size-2026-page-dimensions-and-exports/ | 2026-08-06 | M | 2026-11 |
| Instagram caption 2,200 chars, ~125 visible; bio 150; hashtags max 30, best 3–5 | https://boomp.net/blog/social-media-caption-length ; https://lettercounter.org/blog/social-media-character-limits-comparison/ | 2026-08-06 | M | 2026-11 |
| Instagram carousel: 20 slides max (raised 2024); ratio locked to first slide; 1080×1350 4:5 recommended; video slides ≤60 s / 4 GB | https://storrito.com/resources/how-instagrams-20-slide-carousels-work-and-what-the-new-limits-are/ ; https://contentdrips.com/blog/2026/05/instagram-carousel-size-format/ ; https://carouselpost.io/guides/instagram-carousel-size | 2026-08-06 | M | 2026-11 |
| Instagram Reels: max 20 min (2026); >3 min not recommended to non-followers; optimal 45–60 s | https://zeely.ai/blog/how-long-can-instagram-reels-be/ ; https://www.sellerpic.ai/blog/instagram-reel-size ; https://activids.com/instagram-reels-length-guide/ | 2026-08-06 | M | 2026-11 |
| TikTok caption 4,000 chars | https://boomp.net/resources/questions/social-media-caption-character-limits-2026 ; https://sociality.io/blog/tiktok-video-length/ | 2026-08-06 | M | 2026-11 |
| TikTok video: 10 min in-app record, 60 min upload; best 21–34 s | https://sociality.io/blog/tiktok-video-length/ ; https://flowshorts.app/blog/how-long-can-tiktok-be | 2026-08-06 | M | 2026-11 |
| TikTok slideshow: ≤35 photos, 1080×1920, ≤20 MB/photo; 5–10 slides best | https://wavegen.ai/tiktok-slideshow-size ; https://www.attentionclaw.com/blog/tiktok-slideshow-limits-and-specs ; https://openclip.app/learn/tiktok-slideshow-size | 2026-08-06 | M | 2026-11 |
| TikTok AIGC: mandatory label for realistic AI content; C2PA auto-labeling; undisclosed content may be auto-labeled/reduced/removed; label ≠ reach penalty | https://storrito.com/resources/tiktoks-2026-ai-labeling-rules-and-what-they-signal-for-platform-governance/ ; https://www.auditsocials.com/blog/tiktok-ai-content-disclosure-rules-2026 ; https://newsroom.tiktok.com/en-us/new-labels-for-disclosing-ai-generated-content | 2026-08-06 | M | 2026-11 |
| TikTok Content Posting API Direct Post exposes an AIGC boolean ("is_aigc", default false) applying the AI-generated tag | search synthesis over TikTok developer docs coverage (https://www.cinerads.com/blog/tiktok-ai-content-policy ; TikTok developers docs) | 2026-08-06 | M (verify against developers.tiktok.com before build) | 2026-10 |
| YouTube Shorts ≤3 min (since 2024-10-15); title 100 chars (~40 visible in Shorts); description 5,000 | https://charactercount.tools/youtube/ ; https://typecount.com/blog/youtube-description-character-limit ; https://fluxnote.io/guides/youtube-title-character-limit-2026 | 2026-08-06 | M | 2026-11 |
| YouTube Data API v3: status.containsSyntheticMedia settable on videos.insert/update (added 2024-10-30) | https://developers.google.com/youtube/v3/revision_history | 2026-08-06 | H | 2027-02 |
| YouTube disclosure duty for realistic altered/synthetic content; Studio "Altered content" question; 2026 auto-detection with non-removable proactive labels | https://blog.youtube/news-and-events/disclosing-ai-generated-content/ ; https://minimatters.com/youtube-altered-or-synthetic-content-disclosure/ ; https://shortsfast.com/blog/youtube-ai-content-disclosure-rules-2026/ | 2026-08-06 | M–H | 2026-11 |
| Facebook post max 63,206 chars; collapses ~400 | https://gtrsocials.com/blog/character-limits-on-social-media ; https://typecount.com/blog/social-media-character-limits | 2026-08-06 | M | 2027-02 |
| Facebook: all videos publish as Reels since mid-2025; 9:16 1080×1920 recommended; 15–30 s best; ≤4 GB MP4/MOV | https://www.crowbert.com/blog/facebook-video-format-and-size ; https://postfa.st/sizes/facebook/reels ; https://www.aiarty.com/knowledge-base/facebook-reel-size.htm | 2026-08-06 | M | 2026-11 |
| Meta organic "Made with AI"/"AI info": self-disclosure toggle + automatic C2PA/IPTC-metadata labeling; label not a reach penalty; ads have separate mandatory AI disclosure (2026, enforced) | https://transparency.meta.com/governance/tracking-impact/labeling-ai-content/ ; https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/ ; https://coinis.com/blog/meta-ai-content-labeling-facebook-instagram-ads-2026 ; https://influencermarketinghub.com/ai-disclosure-rules/ | 2026-08-06 | M | 2026-11 |
| EU AI Act Art. 50 transparency applies from 2026-08-02; Art. 50(2) machine-readable marking; deployers' deepfake disclosure; Omnibus proposal may move marking deadline to 2026-12-02 (not adopted); transparency Code of Practice in progress | https://artificialintelligenceact.eu/article/50/ ; https://www.gtlaw.com/en/insights/2026/6/deepfakes-chatbots-ai-generated-text-european-commission-details-transparency-obligations-under-the-ai-act ; https://www.hsfkramer.com/notes/ip/2026-03/transparency-obligations-for-ai-generated-content-under-the-eu-ai-act-from-principle-to-practice ; https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content | 2026-08-06 | H | 2026-12 |
| Google: AI content not penalized per se; scaled content abuse & thin content penalized; E-E-A-T emphasis in 2026 updates | https://www.rankability.com/data/does-google-penalize-ai-content/ ; https://rankai.ai/articles/google-policy-on-ai-content-seo-compliance-guide ; https://www.digitalapplied.com/blog/scaled-content-abuse-google-march-update-ai-pages-decimated | 2026-08-06 | M–H | 2026-12 |
| MCP: 2026-07-28 spec release; official Python + TypeScript (+Go, C#) SDK betas shipped simultaneously; Streamable HTTP is the recommended remote transport | https://blog.modelcontextprotocol.io/posts/sdk-betas-2026-07-28/ ; https://blog.modelcontextprotocol.io/posts/2026-07-28/ | 2026-08-06 | H | 2026-12 |
| Notion's supported MCP path is the hosted remote server at mcp.notion.com (Streamable HTTP, OAuth/bearer); local OSS server may be sunset | https://developers.notion.com/guides/mcp/get-started-with-mcp ; https://www.notion.com/blog/notions-hosted-mcp-server-an-inside-look ; https://github.com/makenotion/notion-mcp-server | 2026-08-06 | H | 2026-12 |
| Anthropic SDKs: first-class Python & TS incl. tool-runner; Python SDK ships MCP conversion helpers (anthropic[mcp], Python 3.10+) | claude-api skill (bundled Anthropic reference, cached 2026-06) + https://github.com/anthropics/anthropic-sdk-python | 2026-08-06 | H | 2027-02 |
| Google Gen AI SDK official & GA in Python and JS/TS (google-genai; releases through July 2026) | https://pypi.org/project/google-genai/ ; https://ai.google.dev/gemini-api/docs/libraries ; https://github.com/googleapis/js-genai | 2026-08-06 | H | 2027-02 |
| Playwright: core automation parity across languages; Node runner extras; Python spawns a Node driver process per instance | https://playwright.dev/python/docs/languages ; https://github.com/microsoft/playwright/issues/27187 ; https://pixeljets.com/blog/web-scraping-playwright-python-nodejs/ | 2026-08-06 | H | 2027-02 |
| pkg deprecated (vercel archived; yao-pkg fork active); Node SEA stable since Node 22, improved Node 24 | https://github.com/vercel/pkg ; https://joyeecheung.github.io/blog/2026/01/26/improving-single-executable-application-building-for-node-js/ ; https://www.hirenodejs.com/blog/nodejs-single-executable-applications-2026 | 2026-08-06 | H | 2027-02 |
| PyInstaller one-file: mature; large bundles (~180 MB heavy stacks), seconds-level cold start | https://pyinstaller.org/en/stable/operating-mode.html ; https://ahmedsyntax.com/pyinstaller-onefile/ | 2026-08-06 | M | 2027-02 |
| PEP 686: UTF-8 mode default lands in Python 3.15; until then Windows uses legacy ANSI/console code pages; UTF-8 mode opt-in via environment switch | https://peps.python.org/pep-0686/ | 2026-08-06 | H | 2027-06 |
| Task Scheduler: Last Run Result = process exit code; 0x1 typically wrapper/working-dir/env issues; set Start-in; propagate errorlevel explicitly | https://blog.matrixpost.net/task-scheduler-task-returns-0x1-for-batch-file/ ; https://www.tutorialpedia.org/blog/windows-scheduled-task-succeeds-but-returns-result-0x1/ | 2026-08-06 | M–H | 2027-02 |
| SYSTEM account: separate profile (systemprofile), per-user DPAPI/credential stores don't cross accounts; per-user browser installs invisible to SYSTEM | https://hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/dpapi-extracting-passwords.html ; https://techcommunity.microsoft.com/discussions/windowspowershell/is-it-possible-to-launch-a-browser-with-task-scheduler-as-system-account/3495457 | 2026-08-06 | M–H | 2027-02 |
| cron: minimal PATH (two system dirs), no locale (POSIX/C → non-UTF-8), no crontab variable expansion, % escaping; set locale or make app locale-independent | https://oneuptime.com/blog/post/2026-03-04-set-environment-variables-cron-jobs-rhel-9/view ; https://www.crongen.com/blog/environment-variables-cron-jobs ; http://www.robertprice.co.uk/robblog/utf-8-aware-cron-scripts/ | 2026-08-06 | H | 2027-06 |
| Caption/safe-zone practice for 9:16 (burned-in captions; avoid bottom/right UI zones) | https://posteverywhere.ai/blog/tiktok-video-sizes ; https://wavegen.ai/tiktok-video-size (+ practice consensus) | 2026-08-06 | M (practice, not spec) | 2026-11 |

Volatile-source recency check: of the volatile-topic sources above (platform limits, AI-label policy, SEO stance, packaging state), well over 60% are dated or last-updated Feb 2026 or later (2026-dated guides, 2026-03/06 law-firm analyses, 2026-07 MCP release notes, 2026-01 Node SEA analysis, 2026-03 cron guide, 2026-05 carousel guide, April/July 2026 postfa.st updates); the remainder are stable primary references (twitter-text config, PEP 686, YouTube API revision history, Meta/TikTok newsrooms).

---

## 5. Sources (dated)

Platform limits and formats
- X developer docs — Counting characters (canonical, current): https://docs.x.com/fundamentals/counting-characters
- twitter-text v3 configuration (canonical weight table): https://raw.githubusercontent.com/twitter/twitter-text/master/config/v3.json
- FMAX — Twitter/X character limits 2026: https://fmax.io/blog/twitter-character-limit-2026
- ZeroUtil — Social character limits 2026: https://zeroutil.com/blog/character-limits-social-2026/
- Nemovideo — X video length limits 2026: https://www.nemovideo.com/blog/twitter-video-length-limits
- Sked Social — X image/video size guide 2026: https://skedsocial.com/blog/twitter-post-size-guide
- AuthoredUp — LinkedIn character limits 2026: https://authoredup.com/blog/linkedin-character-limit
- ConnectSafely — LinkedIn post length engagement guide 2026: https://connectsafely.ai/articles/ideal-linkedin-post-length-engagement-guide-2026
- PostNitro — LinkedIn post specs 2026: https://postnitro.ai/blog/post/linkedin-post-specs
- Oktopost — LinkedIn carousel/PDF best practices 2026: https://www.oktopost.com/blog/linkedin-carousel-pdf-best-practices/
- Storrito — Instagram 20-slide carousels explained (2026): https://storrito.com/resources/how-instagrams-20-slide-carousels-work-and-what-the-new-limits-are/
- ContentDrips — Instagram carousel size/format (2026-05): https://contentdrips.com/blog/2026/05/instagram-carousel-size-format/
- Zeely — Instagram Reels limits 2026: https://zeely.ai/blog/how-long-can-instagram-reels-be/
- SellerPic — Instagram Reel size & limits 2026: https://www.sellerpic.ai/blog/instagram-reel-size
- Sociality — TikTok video length guide 2026: https://sociality.io/blog/tiktok-video-length/
- WaveGen — TikTok slideshow size 2026: https://wavegen.ai/tiktok-slideshow-size
- AttentionClaw — TikTok slideshow limits & specs 2026: https://www.attentionclaw.com/blog/tiktok-slideshow-limits-and-specs
- CharacterCount.tools — YouTube limits 2026: https://charactercount.tools/youtube/
- FluxNote — YouTube title limit 2026: https://fluxnote.io/guides/youtube-title-character-limit-2026
- Crowbert — Facebook video format & upload limits 2026: https://www.crowbert.com/blog/facebook-video-format-and-size
- Postfa.st — Facebook Reels size (updated 2026-04): https://postfa.st/sizes/facebook/reels
- Boomp — Social caption/character limits 2026: https://boomp.net/resources/questions/social-media-caption-character-limits-2026

AI-content labeling and law
- TikTok Newsroom — New labels for disclosing AI-generated content: https://newsroom.tiktok.com/en-us/new-labels-for-disclosing-ai-generated-content
- TikTok Newsroom — Partnering to advance AI transparency (C2PA): https://newsroom.tiktok.com/en-us/partnering-with-our-industry-to-advance-ai-transparency-and-literacy
- Storrito — TikTok 2026 AI labeling rules: https://storrito.com/resources/tiktoks-2026-ai-labeling-rules-and-what-they-signal-for-platform-governance/
- AuditSocials — TikTok AI disclosure rules 2026: https://www.auditsocials.com/blog/tiktok-ai-content-disclosure-rules-2026
- YouTube Blog — Disclosing altered or synthetic content: https://blog.youtube/news-and-events/disclosing-ai-generated-content/
- YouTube Data API revision history (containsSyntheticMedia, 2024-10-30): https://developers.google.com/youtube/v3/revision_history
- ShortsFast — YouTube AI disclosure rules 2026: https://shortsfast.com/blog/youtube-ai-content-disclosure-rules-2026/
- Meta Transparency Center — Labeling AI content: https://transparency.meta.com/governance/tracking-impact/labeling-ai-content/
- Meta Newsroom — Labeling AI-generated images (2024-02, foundation): https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/
- Coinis — Meta AI labels in FB/IG ads (2026): https://coinis.com/blog/meta-ai-content-labeling-facebook-instagram-ads-2026
- Influencer Marketing Hub — AI disclosure rules by platform: https://influencermarketinghub.com/ai-disclosure-rules/
- EU AI Act Article 50 (text): https://artificialintelligenceact.eu/article/50/
- Greenberg Traurig — Commission details Art. 50 transparency obligations (2026-06): https://www.gtlaw.com/en/insights/2026/6/deepfakes-chatbots-ai-generated-text-european-commission-details-transparency-obligations-under-the-ai-act
- HSF Kramer — Art. 50 from principle to practice (2026-03): https://www.hsfkramer.com/notes/ip/2026-03/transparency-obligations-for-ai-generated-content-under-the-eu-ai-act-from-principle-to-practice
- European Commission — Code of Practice on transparency of AI-generated content: https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content
- Jones Day — Draft Code of Practice on AI labelling (2026-01): https://www.jonesday.com/en/insights/2026/01/european-commission-publishes-draft-code-of-practice-on-ai-labelling-and-transparency

Blog / SEO
- Rankability — Does Google penalize AI content (2026 study): https://www.rankability.com/data/does-google-penalize-ai-content/
- RankAI — Google policy on AI content, 2026 compliance guide: https://rankai.ai/articles/google-policy-on-ai-content-seo-compliance-guide
- Digital Applied — Scaled content abuse analysis: https://www.digitalapplied.com/blog/scaled-content-abuse-google-march-update-ai-pages-decimated

Stack verification
- MCP blog — SDK betas for 2026-07-28 spec (2026-07): https://blog.modelcontextprotocol.io/posts/sdk-betas-2026-07-28/
- MCP blog — The 2026-07-28 specification: https://blog.modelcontextprotocol.io/posts/2026-07-28/
- Notion — Connect to Notion MCP (developer docs): https://developers.notion.com/guides/mcp/get-started-with-mcp
- Notion — Hosted MCP server, inside look: https://www.notion.com/blog/notions-hosted-mcp-server-an-inside-look
- Anthropic SDK (Python, incl. MCP helpers): https://github.com/anthropics/anthropic-sdk-python (+ bundled Anthropic claude-api reference, cached 2026-06)
- Google Gen AI SDK — PyPI (release 2026-07-30): https://pypi.org/project/google-genai/ ; JS SDK: https://github.com/googleapis/js-genai ; libraries overview: https://ai.google.dev/gemini-api/docs/libraries
- Playwright — supported languages: https://playwright.dev/python/docs/languages ; language comparison issue: https://github.com/microsoft/playwright/issues/27187
- Pixeljets — Playwright Python vs Node for scraping: https://pixeljets.com/blog/web-scraping-playwright-python-nodejs/
- vercel/pkg (archived/deprecated): https://github.com/vercel/pkg ; yao-pkg fork: https://yao-pkg.github.io/pkg/
- Joyee Cheung — Improving Node SEA (2026-01-26): https://joyeecheung.github.io/blog/2026/01/26/improving-single-executable-application-building-for-node-js/
- HireNodeJS — Node SEA production guide 2026: https://www.hirenodejs.com/blog/nodejs-single-executable-applications-2026
- PyInstaller docs — operating mode: https://pyinstaller.org/en/stable/operating-mode.html ; one-file guide (2025): https://ahmedsyntax.com/pyinstaller-onefile/
- PEP 686 — Make UTF-8 mode default (target 3.15): https://peps.python.org/pep-0686/
- Matrixpost — Task Scheduler 0x1 for batch files: https://blog.matrixpost.net/task-scheduler-task-returns-0x1-for-batch-file/
- Tutorialpedia — Scheduled task 0x1 fix: https://www.tutorialpedia.org/blog/windows-scheduled-task-succeeds-but-returns-result-0x1/
- HackTricks — DPAPI (per-user key scoping): https://hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/dpapi-extracting-passwords.html
- Microsoft Tech Community — launching a browser as SYSTEM via Task Scheduler: https://techcommunity.microsoft.com/discussions/windowspowershell/is-it-possible-to-launch-a-browser-with-task-scheduler-as-system-account/3495457
- OneUptime — Env vars in cron jobs, RHEL 9 (2026-03-04): https://oneuptime.com/blog/post/2026-03-04-set-environment-variables-cron-jobs-rhel-9/view
- Crongen — Env vars missing in cron: https://www.crongen.com/blog/environment-variables-cron-jobs
- Robert Price — UTF-8 aware cron scripts: http://www.robertprice.co.uk/robblog/utf-8-aware-cron-scripts/
