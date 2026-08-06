# Phase 0 — Plain-English To-Do List

*Written 2026-08-06. This is the operator-facing checklist for Phase 0 of the build. The full, technical version of every item lives in `docs/architecture/ARCHITECTURE_PLAN.md` §17.2 (Phase 0). Where the two disagree, §17.2 governs — this file is a simplified map, not a second source of truth.*

**Why Phase 0 comes first:** almost everything here runs on *other people's clocks* — lawyers, Meta's verification team, Reddit's approval queue, vendor trials. Filing these in week 1 means the waiting happens while the software gets built. Filing them late means the waiting happens at the end, when it hurts.

---

## Part 1 — Things only YOU can do (start this week)

### Applications and verifications (slow — file these first)

- [ ] **Meta Ad Library**: submit your government-ID verification, accept the API terms, and save a dated copy of those terms. This takes days and gates one whole research source.
- [ ] **Reddit**: file the Data API commercial-use application (OD-29). It may take weeks or be refused — the system has a fallback either way, so don't wait on the answer.
- [ ] **Product Hunt**: send the commercial-use permission email (OD-19).

### ~~Lawyer items~~ (SKIPPED 2026-08-07 by your decision — W8-4)

- [x] ~~All counsel items (OD-24/25/26, OD-L1–L5)~~ — **You decided to skip lawyers entirely for now.** The legal drafts stay in `legal/` unverified; the build proceeds. The one place this resurfaces by design: **before Phase 6 (real publishing)**, the plan will ask again — you can waive it again then if you want.
- [ ] **Music licensing**: pick a vendor (library subscription or paid AI-music plan). Not a lawyer item — just a purchase. Needed before anything publishes (Phase 6).

### Trials (each takes about a week)

- [ ] **Virlo** — run the 1-week trial. It must answer three questions (OD-16); the verdict decides adopt / fall back to Shortimize / accept absence.
- [ ] **Postiz** — open a trial account and confirm it can create drafts that never auto-publish. This is currently a paper claim (OP-2).

### Terms nobody has read yet (an afternoon of reading)

- [ ] **Kie.ai** router terms — pull manually in a browser, date it, read it.
- [ ] **Reddit's developer terms** — one question: does it permit commercial use of derived outputs outside Reddit?
- [ ] **Virlo and DataForSEO terms** — check both allow pipeline/derivative use **before spending the first credit**.

### Money and account setup

- [ ] Set the final per-run spending caps (OD-8 — note the default topics-per-run is now 3, not 5, per W7-3).
- [ ] Create the **separate router account** that isolates the runaway-loop risk (§5.4).
- [ ] Set a **hard spend cap at the text-model vendor** — the text wallet is a different vendor from the $50 Kie credit and needs its own funded envelope before Phase 2.

### ~~Your own product's images~~ (CLOSED 2026-08-06 — decision reversed)

- [x] ~~Supply product screenshots for Policy B~~ — **You decided against product imagery entirely (W8-1a supersedes W8-1).** The system stays in safe mode (Policy A): no depictions of your products, ever. Visuals come from generation, licensed sources, and your existing brand assets (logos, published images). **Nothing to supply.**

### Quick yes/no confirmations (the veto window, item 5 of the approval summary)

- [ ] Confirm or veto the adopted defaults: ElevenLabs for Czech voice · local FFmpeg assembly · DataForSEO · 30-day raw retention · Notion REST token for scheduled runs · claim-ledger location (OD-9).

---

## Part 2 — Things the builder does (can run in parallel)

*Listed so you know what's happening; no action from you except where marked. Status updated 2026-08-06 — first build pass done.*

- ⏳ Notion knowledge base: designated fact locations chosen, plan-vs-fact separation confirmed, read-only token issued. *(BLOCKED ON YOU — needs your Notion workspace and a read-only token; you'll be asked to confirm the locations.)*
- ✅ Claim ledger seeded honestly empty (`config/claim_ledger.yaml`) — schema in place, zero claims, location default pending your OD-9 confirmation.
- ✅ Hard excludes baseline written (`config/hard_excludes.yaml`) and special-category source deny-list written (`config/special_category_source_deny_list.yaml`) — structure and semantics complete; the brand-specific values (competitor names, banned topics) are yours to fill.
- ✅ FFmpeg 8.1 pinned (`config/ffmpeg_pin.yaml`), Noto Sans bundled with license (`assets/fonts/`), Czech glyph coverage verified with rendered evidence (`assets/fonts/czech_glyph_test.png`). Two engine constraints discovered and recorded (newline/CRLF rendering).
- ✅ Token runbooks written: Meta Ad Library renewal + Notion token reissue (`runbooks/`).
- 🟡 Exemplar corpora: English drawn from your own marketing docs (15 exemplars, curation needed); **Czech exemplars don't exist in the repo — 5 drafts authored for your approval, rest [OPERATOR TO SUPPLY]** (`calibration/cs/structural_corpus.md`).
- 🟡 **The four calibration artefacts + frozen eval set** — all drafted (`calibration/`): EN golden set 18 items, CS golden set 22 items covering all eleven Czech judge dimensions, frozen eval sets 12+12 items. Numeric measurement bands await tooling (Phase 1); **your approval queue is listed in `calibration/README.md`** (7 items).
- 🟡 The privacy artefacts drafted for counsel (`legal/`): recipient map (10 providers), four legitimate-interest assessments (per purpose × source family), Czech+English privacy notice naming ÚOOÚ. **15 [COUNSEL TO CONFIRM] + [OPERATOR TO CONFIRM] items marked inside** — the EDPB verification (OD-26) still gates finalisation.
- ✅ Two provider questions **answered by inspection** (2026-08-06, Kie.ai account live, 10 080 credits): the router's task status does **NOT** name the rendering model (so the plan's §5.6 inference rule ships, as designed), and person-generation is **not a controllable parameter or allowlist** on this router (people-free composition stays the default; nothing to apply for). Full evidence in `PHASE0_TRIALS.md`, decision row W8-3.

---

## The gate — what "Phase 0 done" means

Phase 1 (first working software, zero cost) may start once:

1. The **four calibration artefacts** exist and give stable verdicts,
2. The **frozen eval set** exists,
3. The **two privacy artefacts** exist in their required shape **with the EDPB reference verified (OD-26)**.

Everything else above can still be in flight — those three cannot.

---

## Decisions already made (so nobody reopens them)

| Decision | Where recorded |
|---|---|
| Amendment A applied; Stage-5 approval unblocked | DECISION_LOG PB-D-1 |
| ~~Theme #1 will opt into Policy B~~ **REVERSED: no product imagery at all — Policy A stands permanently by choice; brand visuals = logos + existing published assets only** | DECISION_LOG W8-1a (supersedes W8-1) |
| Czech axis = 4 automated sources (Virlo/GNews/YouTube/DataForSEO CZ); reduction accepted | DECISION_LOG W8-2 |
| Amendment B (playbook layer) deferred — not started until the operator says so | 00_MASTERPLAN §6; conductor recommendation: after Phase 4 |
