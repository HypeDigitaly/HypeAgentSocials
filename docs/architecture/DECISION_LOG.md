# Decision Log — HypeAgentSocials design phase

*Seeded Wave 0 (2026-08-05). Append-only per wave; single writer per wave (see masterplan aggregating-files table). Each entry: status (LOCKED / OPEN / RESOLVED), owner wave, decision, rationale.*

---

## Locked decisions (from the grill, binding on all design work)

| ID | Status | Decision | Rationale |
|----|--------|----------|-----------|
| D-01 | LOCKED | Design phase only; implementation is a separate future plan after human approval | Assignment Stages 5–6 boundary |
| D-02 | LOCKED | Output languages = per-theme config array; every listed language gets its own full, first-class output set (first theme: `cs` + `en`); never a translation pass. Every architecture layer states its cs behavior explicitly | User decision; F-7 (Czech ≠ translated English) |
| D-03 | LOCKED | Brand truth: Notion MCP primary → theme config → live public website verification. Degrade honestly; unattended runs downgrade to research-only below a confidence threshold | User confirmed Notion MCP available; assignment fail-closed mandate |
| D-04 | LOCKED | Accounts: Kie.ai trial + Postiz trial exist. Higgsfield = paper evaluation only (confidence-tagged output + open decision, not a firm recommendation). No paid official X API | User account reality |
| D-05 | LOCKED | Runtime: Windows-first console app (run.bat + Task Scheduler) now; Linux server cron later → cross-platform mandatory | User deployment reality |
| D-06 | LOCKED | Tech stack: architecture plan recommends with justification + rejected alternatives (Python = working hypothesis; verified by brief C2) | User delegated ("go with what's best") |
| D-07 | LOCKED | Review UX: human reviews packs manually in an organized output folder; later optional config-driven upload to Notion. Operator = solo, marketing-literate, limited patience for file archaeology | User decision |
| D-08 | LOCKED (half) | Default stance on X for v1: assume no paid X reads; design X as degraded/optional research source. Reseller access = OPEN (OD-1) | Pre-decided so research isn't paralyzed; F-2 |

## Open decisions (to be resolved at W0.5 / W2.5 gates or in §16 of the architecture plan)

| ID | Status | Decision needed | Gate | Notes |
|----|--------|-----------------|------|-------|
| OD-1 | OPEN | X research reads via third-party reseller: acceptable spend or drop? | W2.5 (human) | Resolves the open half of D-08. Reseller ToS on storing/deriving content affects artifact retention (F-2) |
| OD-2 | OPEN | Reddit stance: licensed/aggregator path vs human-curated input vs drop for v1 | W2.5 (human) | F-1: ToS prohibits commercial API use; OAuth approval manual 2–4 wks; public JSON same-ToS + CDN-blocked. Only real options may be presented |
| OD-3 | OPEN | Higgsfield role: complement, competitor, or ignore for v1 | W2.5 (human) | F-6; paper-only eval (D-04) must output confidence + options |
| OD-4 | OPEN | Notion access split for cron: MCP (interactive) vs direct REST internal-integration token (unattended) — or MCP-only if auth reality allows | W2.5 (informed by T9) | Assignment says "MCP-extractable"; unattended-cron auth collision must be argued honestly |
| OD-5 | OPEN | Stack confirmation (Python working hypothesis vs alternative) | W2.5 (informed by T10) | D-06 delegates recommendation to the plan |
| OD-6 | OPEN | W0.5 fact intake: Kie credits/models, Postiz plan tier + draft-without-schedule reality, Notion workspace shape, Meta/LinkedIn account status, empty GojiBerry placeholder files | W0.5 (human) | If unavailable: pessimistic defaults, each logged here as OPEN |
