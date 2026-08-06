# Legitimate Interest Assessments — HypeAgentSocials Phase 0

**DRAFT FOR COUNSEL REVIEW — not final, not published. Written 2026-08-06.**

Per ARCHITECTURE_PLAN.md §17.2 and C7_legal_compliance.md §2.6, this document contains **per-purpose, per-source-family** assessments of legitimate interest (Article 6(1)(f) GDPR) for processing of personal data from publicly available sources. Blanket assessments are explicitly ruled out by EDPB guidance. Each assessment includes the three-part test: purpose, necessity, and balancing, plus the objection and erasure route.

---

## Assessment Index

This section processes personal data in the following purpose×family combinations:

| Purpose | Source Family | Personal Data? | Assessment Included |
|---|---|---|---|
| Trend research (viral discourse scoring) | Developer/technical discourse | YES | ✓ [A-1] |
| Trend research | Editorial relay | NO | — |
| Trend research | Video/packaging trends | NO | — |
| ICP pain research | Developer/technical discourse | YES | ✓ [A-2] |
| ICP pain research | Human-curated (operator notes) | YES | ✓ [A-3] |
| Launch hype research | Launch registries (user discussions) | YES | ✓ [A-4] |
| Launch hype research | Editorial relay | NO | — |
| Ad creative pattern research | Ad creative (Meta Ad Library) | NO | — |
| Format trend research | Video/packaging | NO | — |
| Content generation / spin | Derived signals (post-processing) | NO | — |

---

## [A-1] Trend Research × Developer/Technical Discourse

**Source family:** Hacker News (official APIs, public posts); Bluesky (official protocol API, public posts); GitHub (public repositories, issue discussions).

**Personal data involved:** Author identities (usernames, handles), post content (quoted excerpts), metadata (timestamps, engagement counts). A username plus post history can identify or at least pseudonymise a natural person under GDPR Recital 26.

**Purpose test:** *Legitimate interest exists.* HypeDigitaly's stated purpose is to identify emerging trends, vocabulary shifts, and practitioner concerns in AI, coding agents, and lead generation — marketing signals that reflect authentic industry discourse. Collecting and ranking these signals guides content strategy and validates spending decisions. This is a legitimate business interest: understanding market dynamics and practitioner sentiment informs commercial strategy and reduces spend on topics unlikely to resonate with the target audience (development teams, AI practitioners, lead-generation professionals).

**Necessity test:** Collection of *authored posts and comments* (not usernames in isolation) is necessary because:
1. Virality and engagement metrics alone do not convey authentic pain points — comment context matters;
2. The pipeline discards raw posts after 30 days (§2.6), keeping only de-identified signals (topic label, source, engagement metric, timestamp);
3. Redaction of author handles before model-provider transmission (§2.6a) and hashing of identifiers in long-term signal storage (§2.6) further minimise the surface;
4. The pipeline makes no independent attempt to contact or identify authors — it reads public discourse as published and aggregates it;
5. Alternative designs (e.g., buying pre-packaged trend reports from third parties) either lack specificity or were evaluated and rejected (e.g., licensed trend vendors gate on purchase, reducing responsiveness to emerging signals).

**Balancing test:** *Legitimate interest outweighs data-subject interests.* Authors posting on Hacker News, Bluesky, or GitHub are aware that their content is public and indexed by search engines. They are not reasonably surprised that industry-analytics platforms read public discourse; they are aware that their posts are read by strangers. The pipeline does not:
- Republish author names or direct posts verbatim;
- Contact, profile, or attempt to influence individual authors;
- Retain full post context in archived packs (only de-identified signals persist);
- Use posts to build profiles or infer personal attributes unrelated to the industry topic;
- Sell author data or identities to third parties.

The processing is limited to topic-ranking and brand-fit assessment. Data subjects retain full visibility (the posts remain public) and have recourse (objection or erasure requests are honoured, per the route below). The countervailing interest — that individuals' casual public comments might later be aggregated into trend data without per-comment notice — is weaker than HypeDigitaly's interest in understanding genuine market signals without friction.

**Objection and erasure route:** A data subject may object to processing or request erasure via the contact point in the published privacy notice [OPERATOR TO CONFIRM EMAIL] or by mailing HypeDigitaly s.r.o. [OPERATOR TO CONFIRM ADDRESS]. Objections to this specific purpose/source-family combination will result in:
1. **Immediate:** Halt any new collection from public posts authored by or attributed to the objecting person;
2. **30-day verbatim data:** Replaced with de-identified placeholder on the standard 30-day expiry (§2.6);
3. **De-identified signals (topic, timestamp, source):** Deleted immediately from the signal database if attributed to the objecting person, or retained if already sufficiently de-identified;
4. **Archived packs:** Targeted deletion via canonical-key lookup (§2.6) reaches into archived packs; any archived signal attributed to the objecting person is redacted.

The operator will confirm that the deletion occurred and provide a written notice within 30 calendar days.

---

**CRITICAL:** This assessment rests on **EDPB Guidelines on web scraping in the context of generative AI** (reported approved 7 July 2026; exact guideline reference and full text not independently verified in this review session — **VERIFICATION PENDING, OD-26**). The assessor relied on C7_legal_compliance.md §2.6's characterisation of the EDPB position and has not independently confirmed the guideline's number, publication date, or scope against the EDPB's official register. Counsel must verify the guideline exists, retrieve its full text, and confirm that this assessment correctly applies its three-part test before finalisation.

---

## [A-2] ICP Pain Research × Developer/Technical Discourse

**Source family:** Hacker News (comment threads on personal experiences, pain points); YouTube comments (developer reaction to tools and workflows); GitHub issue discussions (technical problems and feature requests).

**Personal data involved:** Author identities (usernames, handles), specific problem descriptions or pain-point narratives. A username identifying a developer at a company, plus a post describing a technical problem the developer faced, can identify that person and potentially infer professional context.

**Purpose test:** *Legitimate interest exists.* HypeDigitaly's purpose is to identify pain points, workflow frustrations, and unmet needs in the target ICP (development teams, outbound-sales teams, lead-generation professionals). Understanding authentic frustration — not aggregated sentiment, but specific problems practitioners face — directly informs content strategy (e.g., "this team is frustrated by API rate limits; an article on managing rate limits will resonate") and validates spending on topics aligned with ICP problems. This is a legitimate business interest: content that addresses real pain performs better and justifies marketing spend.

**Necessity test:** Collection of *specific problem narratives* (not identities) is necessary because:
1. Aggregated sentiment scores do not convey the problem; a specific description ("rate limits killed my deployment") is necessary to understand what problem an article should solve;
2. Authors are posting under pseudonyms (Hacker News usernames, GitHub handles) rather than legal names in most cases, already reducing direct identifiability;
3. The pipeline treats each collected problem as a de-identified signal — the stored record is "developer pain point: API rate limits, GitHub source, timestamp" rather than "username1 complained about rate limits";
4. Raw posts are deleted after 30 days; only the de-identified signal persists;
5. Alternative designs (e.g., purchasing ICP research reports from third-party analysts) lack the specificity necessary to identify authentic, emerging pain points.

**Balancing test:** *Legitimate interest outweighs data-subject interests, with specific limitations.* Authors posting problem statements on public technical forums and issue trackers are aware that the posts are public, indexed, and read by practitioners, tool vendors, and analysts. They are not reasonably surprised that a platform monitoring developer sentiment would read public technical discussions. Countervailing interests are limited because:
- The pipeline does not retain the author's identity with the problem description; it de-identifies immediately upon storage;
- The pipeline does not use problem narratives to build profiles, infer other personal attributes, or target the author;
- Archived retention is de-identified (only the topic/signal remains; the author name and direct URL are purged after 30 days);
- Data subjects have recourse.

However, one constraint applies: **problem narratives that incidentally reveal sensitive personal information** (e.g., health conditions, political views, family status) beyond the technical problem itself must be excluded at collection and must not be stored. Per §2.6, the pipeline applies a deterministic special-category filter post-collection to exclude excerpts containing Article 9 indicators; see [special-category exclusion, below].

**Objection and erasure route:** Identical to [A-1]. A data subject may request that any problem narrative associated with their handle/account be de-identified immediately (rather than waiting 30 days) and that the de-identified topic signal be deleted if it can be attributed to that person. The operator will confirm deletion within 30 days.

---

**CRITICAL:** This assessment also rests on the EDPB web-scraping guideline (**VERIFICATION PENDING, OD-26**). Same verification requirement as [A-1].

---

## [A-3] ICP Pain Research × Human-Curated (Operator-Authored Notes)

**Source family:** Operator's manual notes and observations from reading Reddit, community forums, and public discussions (e.g., a personal note: "I read a Reddit thread in r/webdev about X issue; included notes: {excerpt}").

**Personal data involved:** Quoted excerpts from Reddit, which are authored by identifiable users (Redditors with persistent usernames). When the operator writes down a specific quote ("user123 said 'I have this problem'"), the quote plus username is personal data.

**Purpose test:** *Legitimate interest exists.* The operator sources human-curated observations to capture authentic, emerging pain points that may not yet be amplified by engagement metrics on mainstream platforms. This directly serves the stated purpose of understanding ICP problems and validating spending. This is a legitimate business interest equivalent to [A-2].

**Necessity test:** *Limited necessity.* The operator is explicitly *not* using automated collection from Reddit (per C7 §2.1; Reddit is on the do-not-scrape list for v1). Instead, the operator is reading Reddit as a human — a permitted activity — and selectively noting down observations. The necessity is limited to the degree that the operator chooses to include specific quotes and usernames. Recommendations:
1. The operator should quote *problems and context*, not usernames;
2. If a username is included for audit purposes (e.g., "verify this claim by reading user123's post history"), it should be hashed in storage, not retained in clear text;
3. The observation should be treated as a de-identified signal on the same 30-day retention as automated-collection records.

**Balancing test:** *Legitimate interest outweighs data-subject interests, conditional on the operator following minimisation practices.* A Reddit author is aware that their posts are public and may be read by strangers, researchers, and industry participants. However, the operator's decision to manually transcribe a username into an internal note is a deliberate act of capture; it differs from automated collection's inherent scale. The balancing test requires:
- The operator does not routinely transcribe usernames; if a username is included, it is for a specific, documented reason;
- The transcribed observation is stored with the same de-identification and expiry rules as automated sources;
- The operator does not use a Reddit username to identify or contact the author, or to build a profile beyond the immediate observation.

Under these conditions, legitimate interest outweighs data-subject interests because the operator is acting on behalf of their employer (HypeDigitaly) reading public content in the course of business, similar to a human analyst reading tech news and writing summary notes.

**Objection and erasure route:** A data subject who is aware that their Reddit post was quoted in HypeDigitaly's research notes may object or request erasure via the contact point in the privacy notice [OPERATOR TO CONFIRM EMAIL]. HypeDigitaly will:
1. Immediately cease storing that person's quoted observations;
2. De-identify or delete any existing notes attributed to that person (replacing with "quote from community observation, username redacted");
3. Delete any hash-based linkage from the person's identifier to the stored observation within 30 days.

Notably, if the person is not aware that their public Reddit post was transcribed into an internal note (which is likely), the right to erasure is technically available under Article 17 but the practical route to exercise it depends on HypeDigitaly's contact information being accessible and the person reaching out. The privacy notice must make clear that data subjects can object even if they were not individually notified.

---

**CRITICAL:** This assessment rests on the same EDPB guideline (**VERIFICATION PENDING, OD-26**). Additionally, because Reddit is explicitly on the do-not-scrape list in the architecture and the operator is using manual (human) reading rather than automated collection, this assessment depends on Reddit's framing (per C7 §2.1) that a human reading public posts in an ordinary browser session does not constitute a commercial use requiring a contract. **Counsel should confirm that an operator taking notes from public Reddit browsing falls outside Reddit's Responsible Builder Policy restrictions and does not trigger a commercial-contract requirement.**

---

## [A-4] Launch Hype Research × Launch Registries

**Source family:** Product Hunt (public launches, user comments on launches); Hugging Face Hub (model and tool launches, user comments); official APIs and public feeds where available; user discussions and comments within each registry.

**Personal data involved:** User identities (Product Hunt usernames, Hugging Face user profiles), public comments and feedback on launches. A username plus a comment can identify a natural person and reveal professional interest/expertise (e.g., "username1 works with LLMs and is evaluating this model").

**Purpose test:** *Legitimate interest exists.* HypeDigitaly's purpose is to identify emerging launches and competitive products entering the market, and to understand early-adopter sentiment and feedback. Monitoring who is adopting new tools, what feedback they provide, and how adoption spreads informs content strategy (e.g., "this open-source model is gaining traction; an article comparing it to existing alternatives will drive traffic") and validates spending decisions. This is a legitimate business interest.

**Necessity test:** Collection of *user comments on launches* (not user profiles/identities in isolation) is necessary because:
1. Adoption data (engagement count, comment volume) alone does not convey use-case fit — reading comments reveals what practitioners actually use the tool for;
2. The pipeline discards raw comments after 30 days, retaining only aggregated signals (launch name, launch date, comment volume, dominant themes);
3. Usernames are de-identified in long-term storage;
4. Launch registries are purpose-built platforms for public discourse on new products; it is their intended use case for vendors, competitors, and analysts to monitor feedback.

**Balancing test:** *Legitimate interest outweighs data-subject interests.* Authors posting comments on Product Hunt and Hugging Face are aware that their comments are public, attributed to their account, and indexed by search engines. They are posting in spaces explicitly designed for public feedback on launches; they have chosen a pseudonymous or real identity with the knowledge that the comment will be visible. The pipeline does not:
- Attempt to contact or identify commenters beyond their public username;
- Build individual profiles or infer personal attributes unrelated to their interest in the product;
- Republish comments with author names.

However, one constraint applies: **[A-4 special case: launch registries that serve EU users]** Product Hunt and Hugging Face both serve EU users and may host EU personal data. The necessity test is strong (it is the intended use of the platform), but counsel should confirm whether Product Hunt's and Hugging Face's terms of service permit third-party analytics and data collection. If terms of service require consent or restrict analytics use, an alternative (purchasing aggregated launch data from a third-party analytics vendor) may be necessary.

**Objection and erasure route:** Identical to [A-1] and [A-2]. A data subject may request that comments attributed to their account be de-identified and that any launch-registry-derived signals be deleted if attributable to that account.

---

**CRITICAL:** This assessment rests on the same EDPB guideline (**VERIFICATION PENDING, OD-26**). Additionally, counsel should confirm:
1. **Product Hunt ToS:** Whether monitoring public comments and feedback on launches constitutes a permitted use case or requires an explicit consent/integration agreement.
2. **Hugging Face ToS:** Same question.
3. **Necessity of collecting comments vs. launches alone:** If Product Hunt and Hugging Face provide aggregated "trending launches" data via API without requiring collection of individual comments, that may be a more privacy-protective alternative. (Current architecture uses public pages + GraphQL API per OD-19; confirm that individual comments must be collected, or if aggregated data suffices.)

---

## Special-Category Exclusion: Article 9 Processing

**Applicability:** All four assessments above [A-1 through A-4].

The pipeline applies a two-part exclusion for Article 9 special-category data (health, political opinion, sexual orientation, etc.):

1. **Source-level deny-list (§2.6):** Communities or sources defined by a special category (e.g., Reddit's r/disability, r/mentalhealth, or explicit LGBTQ+ communities) are explicitly excluded from automated collection before any post is stored. This deny-list is configured per theme and reviewed during theme-load validation.

2. **Post-collection deterministic check (§2.6):** Each stored excerpt is scanned for Article 9 keywords and patterns (e.g., medical terminology, mental-health-related language, references to protected characteristics). Any excerpt flagged is **not stored; it is deleted immediately**. This is a hard block, not a flag-and-continue.

**Rationale:** Legitimate interest alone does not lawfully cover processing of Article 9 data. Even if a developer publicly discusses depression, chronic illness, or family trauma on a technical forum, HypeDigitaly's legitimate interest in understanding market trends does not outweigh the special safeguards Article 9 requires. The exclusion is part of the pipeline's design (§14, Prohibited-Outcome Gate) and applies before data is retained.

---

## Withdrawal of Blanket Assessment (Corrected Approach)

The earlier design document contained a single, blanket statement: "Processing is lawful based on legitimate interest." This has been withdrawn and replaced with the four per-purpose, per-source-family assessments above. The withdrawal reflects the EDPB guidance (per C7 §2.6) that **"there are no blanket legitimate interest assessments for this purpose."** Each assessment must be specific to the purpose, the source, the retention, and the safeguards applied.

---

## EDPB Guideline Verification Status

**CRITICAL: ALL FOUR ASSESSMENTS ARE CONDITIONAL ON OD-26 CLOSURE.**

This document cites the **"EDPB Guidelines on web scraping in the context of generative AI"** (reported approved July 2026) as the normative source for the three-part legitimate-interest test and the requirement for per-purpose, per-source-family assessments rather than blanket statements.

**Verification status as of 2026-08-06:**
- **Guideline name and number:** Not independently confirmed; reliance on C7_legal_compliance.md §2.6's reference
- **Publication and approval date:** Reported as "7 July 2026"; not independently verified
- **Full guideline text:** Not reviewed in this drafting session
- **Scope and applicability:** Assumed to cover automated collection of public content for commercial analytics; scope vis-à-vis human-curated collection (e.g., [A-3]) not confirmed

**Before Phase 1 gates:** Counsel must:
1. Retrieve the EDPB guideline from the EDPB's official register (`edpb.europa.eu`);
2. Confirm the guideline number, date of approval, and effective date;
3. Re-read the three-part legitimate-interest test and confirm this assessment applies it correctly;
4. Confirm the guideline covers (or does not cover) human-curated collection as distinguished from automated scraping;
5. Report any divergence between this assessment and the guideline's actual contents.

If the guideline does not exist, has been withdrawn, or applies differently than assumed here, these assessments must be rewritten by counsel before finalisation.

---

**Prepared by:** Documentation for counsel review  
**Date:** 2026-08-06  
**Status:** Phase 0 input — awaiting counsel verification of EDPB guideline (OD-26) and confirmation that per-purpose, per-source-family assessments are complete and correctly apply the three-part test.
