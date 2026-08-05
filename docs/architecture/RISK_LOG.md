# Risk Log — HypeAgentSocials design phase

*Seeded Wave 0 (2026-08-05). Append-only per wave; single writer per wave. Each row: risk, consequence if ignored, owning brief/section, status.*

---

## Research flags (scouted 2026-08-05, review-hardened; assigned briefs MUST address)

| ID | Risk | Consequence if ignored | Owner |
|----|------|------------------------|-------|
| F-1 | Reddit ToS prohibits commercial API use; OAuth approval manual 2–4 wks; public JSON endpoints same-ToS + CDN-blocked in practice | Architecture built on an illegal/unavailable source; realistic fallbacks = licensed aggregator or human-curated input | T5/T6 (facts), T15 (legal), OD-2 |
| F-2 | X free API tier is dead; read path ≠ publish path (Postiz user-OAuth publish is a separate decision) | Conflating reads with publishing blocks both; reseller ToS affects artifact retention | T5 (reads), T9 (publish), OD-1 |
| F-3 | Model churn is structural (e.g. Sora 2 API sunset ~Sept 2026); churn also invalidates prompt patterns and price tiers | Any single-model pin rots before build; deliverable = model registry concept with last-verified dates + re-verification cadence | T2, §5 |
| F-4 | Publish destinations need a config allowlist with ONE enforcement point + defense-in-depth (research-only channels never connected in Postiz) | Scattered per-source checks → one missed path auto-publishes to a research platform | T9, §7/§11 |
| F-5 | Native-audio video models → spoken fake claims are a new safety surface; Czech speech quality materially weaker | Claim gate that only reads text misses audio; possible en/cs pipeline fork | T1/T2/T4 (facts), T14 (enforcement: script-lock vs ASR-verify), §14 |
| F-6 | Higgsfield bundles UGC Builder + Marketing Studio + agent orchestrator; sparse API docs | Mis-classifying complement-vs-competitor skews provider architecture; paper-only eval must carry confidence tags | T2, OD-3 |
| F-7 | Czech is not a translation pass: cs slop lexicon ≠ translated en; video models mangle Czech diacritics on-screen; cs TTS quality varies; cs platform norms differ | Czech outputs read as obvious AI slop → brand damage in home market | T8 (empirical), T13 (rubric), T4 (rendering/TTS), all briefs state cs behavior |
| F-8 | EU AI Act Art. 50 synthetic-content transparency in force + separate platform-native AI labels (TikTok AIGC, YouTube altered-content, Meta AI info); re-encode/assembly typically strips C2PA provenance | Non-compliant published assets; provenance silently lost mid-pipeline — architecture input, not a legal footnote | T15 (law), T4 (C2PA survival), T9 (label fields), §14 |
| F-9 | Scraping pessimism default: headless detection near-total on major surfaces; LinkedIn no public read API; Google Trends no stable official API; Meta Ad Library API needs ID verification | Architecture assuming easy scraping collapses on contact; honest shape ≈ APIs/licensed data + operator-supplied inputs, Playwright only where genuinely open | T5/T6, §2 |

## Review-risk areas (from plan review; R1 verifies each in W4)

| ID | Risk area | What must be concretely true in the plan |
|----|-----------|------------------------------------------|
| RA-1 | Cron idempotency/dedupe | Concrete run identity, dedupe keys, overlap policy — not hand-waved |
| RA-2 | Brand-fit scoring | Inspectable sub-scores + hard skip threshold; anti-forced-placement |
| RA-3 | Anti-slop gate | Machine gate with bounded regenerate + escalate-to-review; never silently ship |
| RA-4 | Source-access honesty | X under D-08, Reddit per F-1, F-9 pessimism throughout — no fantasy access paths |
| RA-5 | Brand-truth conflicts | Precedence + confidence bands + degrade trigger defined |
| RA-6 | Budget caps & dry-run | Caps incl. mid-pack cap-hit behavior; dry-run boundary explicit |
| RA-7 | cs+en output-set integrity | D-02 first-class in every layer (F-7), not bolted on |
| RA-8 | Mode enforcement | ONE fail-closed choke point, capability matrix per mode |

## Operational risks (seeded W0)

| ID | Risk | Consequence | Owner |
|----|------|-------------|-------|
| OP-1 | D-02 doubles media spend against trial quotas (cs + en = 2× video generations per pack); confirmed W0.5: only **$50 Kie credits** exist | Kie trial credits exhausted mid-evaluation; unit economics must price the doubling explicitly against the $50 reality | T2 (economics), §5 |
| OP-2 | No Postiz account exists yet (W0.5) → draft-without-schedule kill-switch question cannot be verified empirically during design | Distribution architecture rests on paper claims; fallback ladder (internal draft → far-future schedule → local-only staging + manual paste) must be designed as first-class, and Postiz capability verification becomes an implementation-phase acceptance criterion | T9, §7 |
