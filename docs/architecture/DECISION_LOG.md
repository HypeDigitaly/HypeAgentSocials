# Decision Log — HypeAgentSocials design phase

*Seeded Wave 0 (2026-08-05). Append-only per wave; single writer per wave (see masterplan aggregating-files table). Each entry: status (LOCKED / OPEN / RESOLVED), owner wave, decision, rationale.*

---

## Locked decisions (from the grill, binding on all design work)

| ID | Status | Decision | Rationale |
|----|--------|----------|-----------|
| D-01 | LOCKED | Design phase only; implementation is a separate future plan after human approval | Assignment Stages 5–6 boundary |
| D-02 | LOCKED | Output languages = per-theme config array; every listed language gets its own full, first-class output set (first theme: `cs` + `en`); never a translation pass. Every architecture layer states its cs behavior explicitly | User decision; F-7 (Czech ≠ translated English) |
| D-03 | LOCKED | Brand truth: Notion MCP primary → theme config → live public website verification. Degrade honestly; unattended runs downgrade to research-only below a confidence threshold | User confirmed Notion MCP available; assignment fail-closed mandate |
| D-04 | LOCKED (amended W0.5) | Accounts: Kie.ai trial exists with **$50 credits** (model choice open — T2 recommends best image-gen + video-gen models). **No Postiz account yet** — operator trials it later; priority = prove research→assets pipeline first, distribution is a later phase. Higgsfield = paper evaluation only (confidence-tagged output + open decision). No paid official X API | User account reality, updated at W0.5 fact intake 2026-08-05 |
| D-05 | LOCKED | Runtime: Windows-first console app (run.bat + Task Scheduler) now; Linux server cron later → cross-platform mandatory | User deployment reality |
| D-06 | LOCKED | Tech stack: architecture plan recommends with justification + rejected alternatives (Python = working hypothesis; verified by brief C2) | User delegated ("go with what's best") |
| D-07 | LOCKED | Review UX: human reviews packs manually in an organized output folder; later optional config-driven upload to Notion. Operator = solo, marketing-literate, limited patience for file archaeology | User decision |
| D-08 | LOCKED (closed W0.5) | X for v1: no paid X reads, **reseller REJECTED by operator (2026-08-05)** — X reads are skipped/degraded-optional in v1. X-as-publish-destination remains a separate later-phase decision (F-2) | Pre-decided + operator answer at W0.5 fact intake |

## Open decisions (to be resolved at W0.5 / W2.5 gates or in §16 of the architecture plan)

| ID | Status | Decision needed | Gate | Notes |
|----|--------|-----------------|------|-------|
| OD-1 | RESOLVED (W0.5) | X reseller rejected → X reads skipped in v1; X only as degraded/optional free-surface source if any legitimately exists | — | D-08 closed. Reseller ToS/retention questions moot for v1 |
| OD-2 | OPEN | Reddit stance: licensed/aggregator path vs human-curated input vs drop for v1 | W2.5 (human) | F-1: ToS prohibits commercial API use; OAuth approval manual 2–4 wks; public JSON same-ToS + CDN-blocked. Only real options may be presented. Note: `GojiBerry_Reddit_01.txt` transcript = practitioner evidence of Reddit's value in this niche |
| OD-3 | OPEN | Higgsfield role: complement, competitor, or ignore for v1 | W2.5 (human) | F-6; paper-only eval (D-04) must output confidence + options |
| OD-4 | OPEN | Notion access split for cron: MCP (interactive) vs direct REST internal-integration token (unattended) — or MCP-only if auth reality allows | W2.5 (informed by T9) | Assignment says "MCP-extractable"; unattended-cron auth collision must be argued honestly |
| OD-5 | OPEN | Stack confirmation (Python working hypothesis vs alternative) | W2.5 (informed by T10) | D-06 delegates recommendation to the plan |
| OD-6 | RESOLVED (W0.5, 2026-08-05) | Fact intake answered: **Kie.ai = $50 credits**, model roster choice open — operator wants a recommendation for best image-gen + video-gen models (→ T2). **Postiz = no account yet**, trial later; prove research→assets first. **Notion = KB about HypeDigitaly + projects exists, MCP-connectable** (→ T9/T14). **Meta business accounts + LinkedIn company page both exist.** **GojiBerry_YoutubeInspiration files are real content** (4 GTM/growth transcripts, ~150 KB) — analyze meticulously (→ T1/T5/T8/T13) | — | Postiz draft-without-schedule capability remains empirically unverifiable until an account exists → paper research + mandatory fallback ladder (T9), logged as risk OP-2 |
