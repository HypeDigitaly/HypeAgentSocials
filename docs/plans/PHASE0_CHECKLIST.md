# Phase 0 — Plain-English To-Do List

*Written 2026-08-06. This is the operator-facing checklist for Phase 0 of the build. The full, technical version of every item lives in `docs/architecture/ARCHITECTURE_PLAN.md` §17.2 (Phase 0). Where the two disagree, §17.2 governs — this file is a simplified map, not a second source of truth.*

**Why Phase 0 comes first:** almost everything here runs on *other people's clocks* — lawyers, Meta's verification team, Reddit's approval queue, vendor trials. Filing these in week 1 means the waiting happens while the software gets built. Filing them late means the waiting happens at the end, when it hurts.

---

## Part 1 — Things only YOU can do (start this week)

### Applications and verifications (slow — file these first)

- [ ] **Meta Ad Library**: submit your government-ID verification, accept the API terms, and save a dated copy of those terms. This takes days and gates one whole research source.
- [ ] **Reddit**: file the Data API commercial-use application (OD-29). It may take weeks or be refused — the system has a fallback either way, so don't wait on the answer.
- [ ] **Product Hunt**: send the commercial-use permission email (OD-19).

### Lawyer items (book the time now)

- [ ] **OD-26 — the blocker**: have counsel verify the EDPB web-scraping guideline reference against the EDPB's own register. The whole lawful-basis analysis rests on this. Nothing legal can be finalised before it.
- [ ] **OD-24**: scope of the AI Act "editorial review" carve-out.
- [ ] **OD-25**: check the two Czech statute citations against primary text.
- [ ] **OD-L1 to OD-L5** *(new, from Amendment A)*: confirm five EU-law citations behind the Prohibited-Outcome Gate (health-claim rules, medicines law, medical devices, food information, unfair-practices blacklist). None block Phase 0 — they gate Phase 6 — but they can ride along in the same counsel engagement as OD-24/25/26.
- [ ] **Music licensing**: pick a vendor (library subscription or paid AI-music plan). Must be resolved before anything publishes (Phase 6), but choosing early avoids a scramble.

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

### Your own product's images (new, from your W8-1 decision)

- [ ] You chose to turn product-dashboard imagery back on (Policy B). For that to activate you must supply **current, real screenshots of the product interface**, attested as accurate, entered as F-W reference imagery. Until then the system runs in the safe mode (Policy A) automatically.

### Quick yes/no confirmations (the veto window, item 5 of the approval summary)

- [ ] Confirm or veto the adopted defaults: ElevenLabs for Czech voice · local FFmpeg assembly · DataForSEO · 30-day raw retention · Notion REST token for scheduled runs · claim-ledger location (OD-9).

---

## Part 2 — Things the builder does (can run in parallel)

*Listed so you know what's happening; no action from you except where marked.*

- Notion knowledge base: designated fact locations chosen, plan-vs-fact separation confirmed, read-only token issued. *(You'll be asked to confirm the locations.)*
- Claim ledger seeded with whatever is genuinely approved — **an honestly empty ledger is a valid outcome.**
- Hard excludes written into config; special-category source deny-list written.
- FFmpeg installed and pinned, fonts bundled, Czech characters verified.
- Exemplar corpora assembled per language. *(You'll be asked to supply/approve example posts.)*
- **The four calibration artefacts** — Czech + English structural calibration, Czech + English judge golden sets — plus the frozen eval set.
- The two privacy artefacts drafted for counsel: the legitimate-interest assessment (per purpose, per source family) and the privacy notice naming ÚOOÚ.
- Two provider questions answered by inspection: person-generation eligibility for this account/region, and whether the router's task status names the rendering model.

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
| Theme #1 will opt into Policy B (product imagery back, with real screenshots + attestation) | DECISION_LOG W8-1 |
| Czech axis = 4 automated sources (Virlo/GNews/YouTube/DataForSEO CZ); reduction accepted | DECISION_LOG W8-2 |
| Amendment B (playbook layer) deferred — not started until the operator says so | 00_MASTERPLAN §6; conductor recommendation: after Phase 4 |
