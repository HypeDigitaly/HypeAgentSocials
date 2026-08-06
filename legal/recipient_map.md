# External Data Recipients — Phase 0 Mapping

**DRAFT FOR COUNSEL REVIEW — not final, not published. Written 2026-08-06.**

This map identifies every external provider that receives collected personal data or derived data from the HypeAgentSocials pipeline, their processing role, and data transfer characteristics. This map is the authoritative source for the privacy notice's Article 13 recipients section.

---

## Recipients and Processing Roles

| Provider | Role | Service | DPA / Processing Agreement | EEA Status | Categories of Data Received | Notes |
|---|---|---|---|---|---|---|
| **Anthropic** (claude models) | Processor | Text-model provider (spin/copy generation) | [COUNSEL TO CONFIRM] | **Third-country** (USA) | Collected excerpts (quoted, canonical-keyed, author-handles redacted), topic labels, source classification | Receives text prompts containing excerpt data for context; no raw author identifiers transmitted; excerpts passed with 30-day retention noted in prompt metadata |
| **Kie.ai** | Processor | Media router (generative video/image) | [COUNSEL TO CONFIRM] | **Third-country** (unclear headquarters; [OPERATOR TO CONFIRM]) | Topic label, thematic context, keyframe reference, no text excerpts | Media generation requests are derived from ranked candidates; no raw collected text in routing payloads |
| **fal.ai** | Processor | Fallback media router | [COUNSEL TO CONFIRM] | **Third-country** (unclear; [OPERATOR TO CONFIRM]) | Same as Kie.ai (topic, context, reference metadata only) | Registered fallback only in Phase 0; live routing begins Phase 3 |
| **ElevenLabs** | Processor | Text-to-speech provider (primary) | [COUNSEL TO CONFIRM] | **Third-country** (USA) | Synthesised copy text (generated, not collected) | Receives authored copy and branded voice-ID parameters; no raw collection data; Czech voice specialisation per plan requirement |
| **Azure Cognitive Services / Neural Speech** | Processor | Text-to-speech provider (fallback) | [COUNSEL TO CONFIRM] | **EEA** (Czech or EU region deployable) | Synthesised copy text (generated, not collected) | Fallback tier; cost-driven fallback per plan; no raw collection data |
| **Notion** (via REST + MCP) | Processor | Brand-truth store (queries only, read-only access) | [COUNSEL TO CONFIRM] | **Third-country** (USA) | Fact-class queries (phrased as requests for resolution, not raw excerpt data); brand-truth snapshots written by human operator | Read-only integration on MCP and REST; credential scoping per plan §6.2; no collected personal data sent to Notion |
| **Postiz** | Processor | Publishing bridge (draft creation + scheduling) | [COUNSEL TO CONFIRM] | **Third-country** ([OPERATOR TO CONFIRM]) | Generated copy, media assets, AI-label metadata, scheduled publication timestamps | Bridge receives only generated/authored content; no raw collection data; human operator controls scheduling; drafts only, no auto-publish |
| **Virlo.ai** | Processor | Trend-intelligence vendor (MCP input) | [COUNSEL TO CONFIRM] — **terms must be read before Phase 0 close** (OD-16) | **Third-country** ([OPERATOR TO CONFIRM]) | Query parameters only (keywords, niche IDs, time windows); receives no collected personal data | Receives aggregation requests; returns trend signals; no personal data in either direction; terms must confirm pipeline/derivative-use permission |
| **DataForSEO** | Processor | Search-demand data vendor (MCP input) | [COUNSEL TO CONFIRM] — **terms must be read before Phase 0 close** (OD-17b) | **Third-country** ([OPERATOR TO CONFIRM]) | Query parameters only (search terms, geographies, time windows); receives no collected personal data | Receives aggregation/search-volume requests; returns demand signals; no personal data in either direction; terms must confirm pipeline/derivative-use permission and upstream source (note: active litigation exposure, OD-17b) |
| **Meta (Facebook / Instagram) / Meta Ad Library API** | Independent Controller | Collection source (data provided to us) | N/A — source, not recipient | **Third-country** (USA) | Meta controls its own advertiser data; we receive aggregated ad-creative metadata only | Collection source, not recipient of our data; identity-verified API access required (government ID); no personal data flows to Meta from our pipeline |
| **GitHub** | Processor / Data Host | Repository hosting (run packs, archived records) | [COUNSEL TO CONFIRM] | **Third-country** (USA) | Archived run packs (derived signals, provenance snapshots — no raw verbatim excerpts after 30-day expiry) | Repository is git-backed; no live collection data; packs are de-identified post-expiry; assumption: GitHub's standard DPA applies to private repository access |

---

## Summary by Transfer Mechanism

### EEA Providers
- **Azure Neural Speech** — EU region deployable; no standard third-country transfer mechanism needed (clarify deployment region at implementation)

### Third-Country Transfers (USA / Unknown)
- **Anthropic** (USA) — Standard Contractual Clauses or [COUNSEL TO CONFIRM preferred mechanism]
- **Kie.ai** (unknown) — [OPERATOR TO CONFIRM jurisdiction]; [COUNSEL TO CONFIRM transfer mechanism]
- **fal.ai** (unknown) — [OPERATOR TO CONFIRM jurisdiction]; [COUNSEL TO CONFIRM transfer mechanism]
- **ElevenLabs** (USA) — Standard Contractual Clauses or [COUNSEL TO CONFIRM preferred mechanism]
- **Notion** (USA) — Standard Contractual Clauses or [COUNSEL TO CONFIRM preferred mechanism]
- **Postiz** (unknown) — [OPERATOR TO CONFIRM jurisdiction]; [COUNSEL TO CONFIRM transfer mechanism]
- **Virlo.ai** (unknown) — [OPERATOR TO CONFIRM jurisdiction]; [COUNSEL TO CONFIRM transfer mechanism]
- **DataForSEO** (unknown) — [OPERATOR TO CONFIRM jurisdiction]; [COUNSEL TO CONFIRM transfer mechanism]
- **Meta** (USA, collection source only) — No outbound transfer; Meta controls sourced data
- **GitHub** (USA) — Standard Contractual Clauses or [COUNSEL TO CONFIRM preferred mechanism]

---

## Data Minimisation and Redaction Applied at Entry

Per §2.6a and C7 §2.6, author handles and direct permalinks are **redacted from all prompt payloads** before transmission to external providers. Collected text is passed to model providers as:
- Quoted excerpt (required for context)
- Canonical key / stable identifier (required for dedupe and audit)
- Source class / family (required for scoring)
- **Not**: original author username, direct URL, or full context thread

---

## Outstanding Confirmations Required Before Phase 1

1. **DPA status for all processors** — confirm each provider has a current Data Processing Agreement or advise on preferred mechanism
2. **Third-country transfer safeguards** — confirm Standard Contractual Clauses or alternative for each USA-based processor; clarify mechanism for unknown-jurisdiction vendors
3. **Virlo.ai and DataForSEO terms** — Phase 0 acceptance criterion requires terms pulled, dated, and confirmed for pipeline/derivative-use permission (OD-16, OD-17a, OD-17b)
4. **Kie.ai, fal.ai, Postiz, Virlo.ai jurisdictions** — operators confirm each provider's incorporation/data-center location
5. **GitHub repository DPA scope** — confirm standard repository DPA applies to private run-pack archives

---

**Prepared by:** Documentation for counsel review  
**Date:** 2026-08-06  
**Status:** Phase 0 input — awaiting counsel confirmation on transfer mechanisms and DPA status
