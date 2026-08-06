# Stage 5 — Approval Summary

*HypeAgentSocials design phase · 2026-08-06 · conductor deliverable (Wave 6)*
*The full plan: `docs/architecture/ARCHITECTURE_PLAN.md` (§0–§18 + worked example + review changelog). Evidence: 16 research briefs + `SYNTHESIS.md`. Governance: `DECISION_LOG.md` (D-01…D-59, W2.5 operator rows), `RISK_LOG.md`. How to review the plan yourself: its §18 (start with Appendix A, the worked example).*

---

## 1. Recommended architecture direction

**One paragraph:** A cross-platform Python console app runs a deterministic pipeline with narrow, budgeted LLM nodes — never a free-running agent. On each enabled run it collects signals from a legitimate source portfolio (free APIs/RSS: Hacker News, Product Hunt, Hugging Face, Bluesky, Google News, newsletters, YouTube; both EU ad libraries; the Virlo trend-vendor via MCP and DataForSEO — ~$60–65/mo; plus Reddit through its official Data API — commercial approval filed in Phase 0, with a DataForSEO search-index fallback so the pipeline never waits on it (W6-1: no manual pipeline inputs; the operator supplies configuration and review decisions only); X absent; zero scraping), ranks topic candidates multiplicatively (virality × brand-fit × freshness × confidence, with hard veto lists, per-language fit, a Czech-specific composite, and a resurgence rule for repeat topics), resolves brand truth from Notion (REST token for unattended runs, MCP for interactive; live site overrides on binding commercial facts; below a confidence threshold the run degrades to research-only), then writes cs+en asset sets for every enabled destination (identical mixes — your decision) through a gate chain (spin gate → claim gate → voice gate → claim re-check, plus a platform gate) grounded in your exemplar corpus (style only, never facts). Video runs keyframe-first through the Kie.ai router (Seedance drafts, Veo 3.1 Fast workhorse, Nano Banana images), assembled locally with FFmpeg (carousel-to-reel is the Czech workhorse; Czech audio = TTS, never model-native speech; synthetic human presenters and voice clones are banned in v1), with an engine-level burned-in AI disclosure that config can tighten but never disable. Two wallets (media + LLM tokens) are independently capped with a write-ahead spend ledger and per-unit checkpoints so a crash never discards paid work. Every run ends in a folder-based review package fronted by a one-page Run Digest with a cost forecast **before** media money is spent; you approve, reject-with-feedback, or skip per asset. Publishing stays out of v1: when you later add Postiz, drafts-only through a single allowlist choke point, never live by default. Cadence is a config knob that ships OFF.

**The economics split across two independent wallets:** **media** runs approximately $1.91 per default two-language pack under clean conditions (no regenerations), or $2.20–$2.50 when accounting for the plan's documented ~one-third first-pass defect rate with regenerations; **text** spans cents to low single dollars per pack (read from the registry at run time). Your $50 Kie router credit funds **media only** — and not all of it is available for packs: the documented trial envelope allocates roughly $8 to a bake-off and holds roughly $7 in reserve, leaving about $35 for real packs, which is **roughly 14–18 two-language topic packs** at the default recipe with rework — fewer again once the separate router account required to bound a runaway loop splits the balance (§5.4) and the weekly availability probe draws its share. The old "13–26 packs" figure read the full $50 against a clean, no-rework cost; both halves of that were optimistic. **No text tokens are purchasable from router credit at all** — the text wallet is a different vendor and a different account, and it needs its own separately funded envelope with a hard account-level spend cap set at that vendor before Phase 2, which is the first text-heavy phase. Steady-state monthly cost (derived from §5.4 rates, not measured): media API $90–140 plus text API $90–140 (same order per §5.4) plus Virlo (~$49) plus DataForSEO (~$10–15) plus mandatory music licensing and commercial TTS subscriptions (vendor rates TBD, not currently itemized in cost tables), plus a Phase-6 publishing-bridge delta; weekly availability probe is drawn from the media wallet.

## 2. Alternatives considered (and why not)

| Alternative | Verdict |
|---|---|
| Agentic orchestration (LLM decides pipeline steps) | Rejected — non-deterministic cost, unbudgetable, unsafe unattended (§1) |
| Node/TypeScript stack | Rejected — weaker MCP/AI SDK maturity; Python verified (C2) |
| Per-language-appropriate asset mixes (research recommendation) | **Overruled by you** — identical mixes chosen (W2.5-4); six Czech design commitments compensate |
| X reads (first-party pay-per-use ~$50/mo) | Declined by you for v1 (W2.5-1); reopening path documented |
| Reddit weekly human ritual (W2.5-2) | **Overruled by you at W6-1** — no manual inputs; official Data API (Phase-0 commercial application) with DataForSEO search-index fallback, scraping still banned |
| Scraping/Playwright-led collection | Rejected honestly — 2026 anti-bot reality; do-not-scrape list is binding (F-9) |
| Higgsfield in the pipeline | Rejected for v1 (W2.5-6); fal.ai is the registered fallback router |
| Cloud assembly APIs | Contingency only — local FFmpeg is the engine of record (A4) |
| Web-app review UI | Rejected — static folder digest fits a solo operator (D-07) |

## 3. Assumptions

- All prices/capabilities are a **2026-08-06 snapshot** with recheck-by dates in the fact ledger (Kie pricing has moved twice this year; model churn is structural — the model registry with re-verification cadence is the mitigation, F-3).
- Postiz capabilities are **paper claims** — no account exists; draft-without-schedule verification is an implementation acceptance criterion (OP-2).
- Virlo's AI/B2B niche coverage is unproven — the 1-week trial decides (Shortimize fallback).
- Your Notion KB can be structured into the brand-fact taxonomy (offers, claims allowlist, CTA set, excludes).
- Reddit's commercial API approval is obtainable (OD-29); until and unless it lands, the search-index fallback carries a coarser, low-confidence Reddit signal (W6-02).
- Meta Ad Library ID verification is obtainable (start it in week 1).
- EU AI Act Art. 50 compliance via burned-in disclosure; Omnibus grace timing tracked.

## 4. What needs your action (none blocks approving the direction)

**Before/at implementation start (Phase 0 hard items):**
1. **Legal counsel items** — OD-L1–OD-L5 (primary-text confirmation of Reg. 1924/2006 Art. 10, Dir. 2001/83/EC Title VIII, MDR Art. 7, Reg. 1169/2011 Art. 7(3), UCPD Annex I cure-claim item), OD-L8 (licensed-claims pathway design, if ever needed), OD-24 (Art. 50(4) editorial-review carve-out scope), OD-25 (Czech statutes primary-text check), **OD-26 (EDPB scraping-guideline verification — Phase-0 blocker: the lawful-basis analysis rests on it; processor/data-transfer mapping has no evidence yet)**.
2. Manual browser pulls: Kie.ai ToS + Reddit Data API developer terms (replaces the Reddit Pro pull — W6-1; both blocked automated retrieval).
3. Start: Meta Ad Library ID verification · Reddit Data API commercial-use application (OD-29) · Virlo 1-week trial · Postiz trial (draft capability check).
4. Set final per-run caps (OD-8) — the plan's acceptance gates now measure spend-vs-forecast, not just "reserve survived" (the trial envelope proved ~2× conservative).
5. Veto window on adopted defaults: ElevenLabs cs TTS, FFmpeg local assembly, DataForSEO, 30-day raw retention, Notion REST-for-cron split, claim-ledger location recommendation (OD-9).
6. **Music licensing commitment** — §4.4 mandates licensed music for all audio assets (library subscription or paid-plan AI music generator); the plan currently has no vendor-roster entry, no recheck-by date, and no rights-class treatment for music. This must be resolved before Phase 6's first published asset: music licensing is a rights chain on output and cannot be deferred to later phases.

**One honest limitation to know:** no machine check can detect a theme config that is *coherent but wrong* (plausible pack, wrong emphasis). The first pack review is the test — the plan says this openly (risk R-35).

## 5. Recommended next step

**Amendment A is now applied.** It closes three defects: the claim-ledger laundering defect (P-10) via the Prohibited-Outcome Gate; the unchecked-depiction defect (P-11) via check class 12 and reference-grounding verification; and the hard-failure exclusion defect (P-1) via legitimate emptiability of F-B/F-C/F-E with external-verifier substitution floor. All three apply to theme #1 immediately, not only to later verticals.

**One intended capability removal.** Policy A (no depiction) as the engine floor removes an existing capability from theme #1: ungrounded generated depiction of the product's own dashboard or interface. This is a permitted change (P-11 closes it), and theme #1 may restore this capability by opt-in to Policy B, subject to the named preconditions at §10.4.

**One new per-call cost line.** The Prohibited-Outcome Gate's semantic pass (N-14) adds a new per-call text-wallet line item with a per-call token ceiling listed at §5.4a, read from the registry at run time. The text-wallet estimate in §1 is correspondingly a floor rather than a ceiling.

Next step: approve the architecture direction → run an **implementation masterplan** that turns `ARCHITECTURE_PLAN.md` §17 into a build plan, starting with Phase 0 (credentials, legal verifications, trials, golden sets, calibration corpora) — keeping test-mode/dry-run defaults, the human gate, and fail-closed cron exactly as designed. Implementation does not start until you say so (D-01).
