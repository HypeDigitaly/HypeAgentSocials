# DRAFT B — Runtime, Safety, Distribution & Review Architecture

*Stage 4 architecture plan, Wave 3 · Agent T18 · 2026-08-06*
*Covers assignment Stage-4 items 7, 8, 9, 11, 12, 14 only. §1–6 (major components; List A; List B; viral video pipeline; media provider architecture; brand-truth/spin architecture) are DRAFT A's territory and are referenced here by section number only — never restated. §10 (theme config conceptual contents) and §13 (multi-theme extensibility) belong to a different Wave-3 author; this draft names every config knob it introduces in prose so that author can sweep them into §10. §15–18 (risks/mitigations, open decisions, roadmap, test plan) are assembled elsewhere from RISK_LOG.md and DECISION_LOG.md.*

**Binding inputs.** Every decision in `docs/architecture/DECISION_LOG.md` (through the Wave-2 synthesis entries) binds this draft; nothing below reopens a LOCKED or RESOLVED item. Canonical vocabulary is fixed by `docs/research/SYNTHESIS.md` §4 (D-21) — no new nouns are introduced for stages, gates, ledgers, modes, artifacts or provider roles. Volatile claims cite their owning brief; design reasoning is marked as such.

**Notation.** Arrows (→) denote pipeline or temporal sequence in plain prose, not code. Tables are descriptive, not schemas. No literal folder trees, CLI syntax, config syntax, or cron expressions appear anywhere below; config knobs are named in bold, in prose, as concepts for the assembler — not as keys or flags.

---

## §7 Distribution Architecture

Distribution is the last stage before a human decides something goes live. Nothing in this section changes that: the publishing bridge (Postiz) creates drafts and never publishes (canonical provider role, SYNTHESIS §4.8); a human always performs the schedule/publish action inside the bridge itself, and a human always merges blog/site content. This section covers how drafts get created safely, what happens when that path is unverified or broken, and the one enforcement point that keeps research-only surfaces from ever becoming publish targets.

### 7.1 The publishing bridge: draft-first, paper-based today (OP-2)

No Postiz account exists yet (D-04, OP-2). Every capability claim in this subsection is a **documentation claim** from C1, not yet verified against a real account — C1 itself flags this explicitly. This architecture therefore treats Postiz's positive findings (draft status with no schedule date, drafts persisting until a human acts, full cloud/self-hosted feature parity, broad connector coverage of List B destinations, an official MCP surface) as the *paper* design, and makes **capability verification an implementation-phase acceptance criterion**, not a design assumption (§7.8).

The correct default pattern, once verified: after the human review gate (§11, §12) is satisfied for a given asset, distribution prep creates a draft in the publishing bridge for each allowlisted, connected destination named in that asset's plan. The pipeline's own responsibility ends at draft creation — or ends earlier still, at a lower rung of the fallback ladder below, if draft creation is itself unavailable.

### 7.2 The fallback ladder (first-class, not an afterthought)

Because OP-2 leaves Postiz's real behavior unverified, and because the assignment requires the plan to cover this honestly, distribution prep is designed against a three-rung ladder. Every rung is independently usable; the ladder never falls through to an unsupported or silent action, and descent from one rung to the next is logged with the reason (the same ladder grammar used throughout collection, §8.5, and media generation, §8.13 — primary → degraded → floor, each rung legitimate on its own terms).

| Rung | Mechanism | Operator friction | When it is used |
|---|---|---|---|
| 1 — primary | Unscheduled draft created via the publishing bridge's own draft state (no schedule date attached) | Zero — this is the built-in workflow | Default rung whenever the bridge is reachable and draft creation succeeds |
| 2 — degraded | A scheduled post created with a date set far enough in the future that it is inert in practice, pending a human moving the date forward | Low — a date change is required before the post could ever go live | Used only if rung 1 is verified broken (draft-without-schedule fails on the real account) or degrades mid-run |
| 3 — floor | Local-only staging: the fully composed per-platform content is written into the run pack for manual per-platform paste, with no call to the publishing bridge at all | High — one paste per platform per asset | Always available regardless of the bridge's health; the guaranteed fallback that makes distribution never depend on Postiz being up |

Rung 3 is never removed once the bridge is proven reliable — it remains the honest floor for any destination the operator has not connected, and for any run where the publish gate (§7.4) blocks a destination outright.

### 7.3 Blog/site prep path

Config-gated per theme via a **blog/site prep enablement** knob (output/runtime config block). Per the operator's v1 scope decision (OD-14), this path is drafts-only: when enabled, an approved long-form piece is produced as a run-pack artifact — an article draft — and no site-publishing integration is built. A human merges/publishes the article manually, exactly as a human schedules/publishes from the publishing bridge; there is no automated equivalent of "distribution prep" for a production site merge in any mode (§11 makes this a permanent "never," not a mode-gated capability).

Long-form content carries materially more claims per asset than a social post, so the article artifact is held to a stricter confidence-band requirement than social atomizations of the same topic (band requirement owned by Draft A's brand-truth architecture; referenced here only for its distribution-side consequence). Where a theme's product rules mark an offer site-first (a fact class owned by Draft A, referenced here by pointer only — the brand-truth and spin layer), that topic's social atomizations are held inside the pack pending the article's existence; releasing the hold is a single deliberate operator action, taken once the article has been manually published on the brand's own site. This keeps the site-first rule's whole purpose intact rather than quietly discarding it the moment social assets are ready first.

### 7.4 Publish-destination allowlist: one enforcement point, five-layer defense-in-depth

Per C1 §9 and the locked decision D-23: **the publish gate is the single fail-closed enforcement point** for mode × publish allowlist × human-approval state. Every other layer below is defense-in-depth around that one point, not a second place where the decision could independently be made differently (F-4; RA-8).

1. **Config allowlist per mode.** The **publish allowlist** (canonical config block, SYNTHESIS §4.6) declares, per mode, exactly which content destinations are permitted at all. In test mode this set is empty by construction — publishing is wholly disabled regardless of what a theme's output/runtime block otherwise enables.
2. **Connected-channel gating.** Only destinations present in the current mode's allowlist are ever initialized as publishing-bridge integrations in the first place. A destination the operator has not connected simply does not exist as a callable target, independent of anything else.
3. **The publish gate itself.** Before any distribution-prep call reaches the publishing bridge, the publish gate checks: is this destination in the active mode's allowlist; is it actually connected; does the review-decision store hold a recorded human-approval state for this asset (§11); and — for any asset whose AI-content class requires disclosure — has the AI-label acknowledgement (§7.7, §14) been recorded. Any failure here is fail-closed: nothing is sent.
4. **The publishing bridge's own draft state.** Even a call that reaches the bridge only ever creates a draft (§7.1) — there is no code path in this architecture that ever requests immediate publish or a schedule date inside the live window.
5. **The human review gate.** The human decision recorded before any of the above (§11, §12) is itself a precondition the publish gate reads, not a formality that happened earlier and is trusted implicitly.

**Research sources never appear in this allowlist and are never connected as channels at all** (F-4). This is a structural fact, not a runtime check: Reddit, Product Hunt, the ad libraries and every other research-only surface from List A (Draft A §2) have no corresponding entry in the connected-channel set, in any mode, ever — there is nothing for a missed check to accidentally enable.

**Named failure mode.** If a destination is present in the allowlist but the operator has not actually completed the publishing bridge's connection for it, the run fails closed for that destination alone: the run pack names exactly which destination is blocked and why, and the operator is offered the honest choices (complete the connection and re-run, remove the destination from the allowlist, or accept the pack with that destination absent). There is no silent skip and no silent substitution to a different, unrelated destination (C1 §9).

### 7.5 X-as-publish separation (F-2)

Two independent decisions live on the X/Twitter surface and must never be conflated in this architecture. Whether X reads feed the research layer is a List A decision, closed for v1 (D-08). Whether X is an allowlisted publish destination through the publishing bridge is a separate, later-phase List B decision. Enabling X as a publish destination neither requires nor implies X read access, and the reverse is equally true. If X is ever allowlisted, the diligence item is on the vendor, not on this pipeline's own compliance posture: confirming the publishing bridge's own X integration operates through X's official, paid API path rather than anything scraping-adjacent — a vendor's compliance failure on that surface would become an availability risk for us, not a legal one, but it is worth naming explicitly before X is ever connected.

### 7.6 Never-live-by-default, mode by mode

- **test** (default): every publishing-bridge side effect is refused outright, before the call is even attempted — this is independent of allowlist contents, because in test mode the allowlist is empty by construction (§7.4, layer 1).
- **staging**: draft creation only, for allowlisted-and-connected destinations, and — for unattended runs specifically — only if the **unattended draft-creation** knob (below) is explicitly on.
- **live-prep**: production-ready drafts prepared for every enabled destination, still never auto-published and never auto-scheduled into the live window; the difference from staging is completeness of preparation, not permission to go further.

The cadence knobs in §8.2 govern *when* a run happens; a separate **unattended draft-creation** knob (output/runtime config block, per theme) governs whether a run happening unattended may create publishing-bridge drafts *at all*. Default off. Even when on, it only ever authorizes draft creation (never a publish/schedule action) and remains fully subject to every layer in §7.4 — turning this knob on does not bypass the publish gate, it only permits distribution prep to be attempted without a human present at that exact moment, provided a human-approval state was already recorded during an earlier interactive session for that asset (§11).

### 7.7 The AI-label gap and the publish-gate acknowledgement

Per C1 §7 and the recorded risk W2-05: the publishing bridge exposes **no per-platform AI-disclosure fields** — no TikTok AIGC toggle, no YouTube synthetic-media property, no Meta AI-info control (confirmed against Postiz's public API and MCP surface, C1). This means the publishing bridge cannot itself carry the compliance flag described in full in §14; setting the platform-native label is a manual human action taken in each platform's own interface, after a draft already exists.

Design response, owned jointly by this section and §14: every asset whose AI-content class requires disclosure carries an **AI label required** flag, visible as a named checklist item in the run pack (§12). The publish gate refuses to treat that asset as "ready" until the operator has given an explicit, separately recorded acknowledgement of that flag — this acknowledgement is not folded into the general approve/reject decision, because bundling it is exactly how the busy-operator-skips-it failure mode in W2-05 happens in practice.

### 7.8 Implementation acceptance criteria (deferred to build, explicitly not a design assumption)

Because OP-2 leaves the publishing bridge unverified, the following must be confirmed against a real account before this section's rung 1 (§7.2) can be trusted as the everyday path, per C1's own open items and the synthesis's W2.5 recommendation:

- unscheduled-draft creation actually succeeds, for a batch of posts, with no auto-publish trigger ever firing;
- draft state persists across a service restart of the publishing bridge;
- draft-to-schedule and schedule-to-draft transitions both work as documented;
- drafts are visible in the bridge's own review surface for a human to act on;
- whether any per-platform AI-disclosure field has appeared since C1 was written — worth re-testing specifically, since this is exactly the kind of capability a vendor adds quietly (C1 §7).

Until these are confirmed, rungs 2 and 3 of the fallback ladder are treated as equally load-bearing, not merely theoretical.

---

## §8 Scheduler / Cron Architecture

### 8.1 One entrypoint, two invocation modes

The console application has exactly one entrypoint capable of running the full pipeline. Whether it is invoked by an operator at the keyboard or by an OS scheduler with nobody watching changes nothing about which code executes — only the theme, mode, and any interactive overrides differ (the two paths are walked stage by stage in §9). This single-entrypoint property is what makes "cron-executable full pipeline" a fact about the one application, not a separate build artifact.

**Today: Windows Task Scheduler**, with the scheduled task always configured to run under **the operator's own user account — never SYSTEM** (C2 §2.6; D-11). Running as SYSTEM breaks two things simultaneously and silently: browser-automation installs live per-user and are invisible to SYSTEM, and any secret protected by the operating system's own per-user encryption cannot be decrypted by a different account. Both failures are the class of bug that works perfectly in an interactive test and then fails at three in the morning with no one watching (W2-20).

**Later: Linux**, via cron or systemd timers (D-05) — the choice between the two affects only the missed-run catch-up nuance (§8.4) and which secrets-hardening layer is available (§8.9); the pipeline's own behavior is unchanged, because the application treats the scheduler as nothing more than "something that starts the process" (C2 §2.7). Moving from Windows to Linux is a thin per-OS launcher rewrite, not an application change — the app owns its own encoding, paths, secrets access, logging, locking and exit codes throughout.

### 8.2 Cadence knobs: the conceptual split (W2.5-7)

The operator's own framing at the W2.5 checkpoint was: settable in config, default off, otherwise daily or weekly, with the exact shape delegated to the architecture. The recommended shape is **two independent cadence knobs**, not one, because research-collection and pack-production have different natural rhythms and different cost profiles:

- **research-collection cadence** — governs how often the collection stage alone runs (no media spend at this cadence; ranking and dedupe-index maintenance run alongside it). Recommended default once enabled: daily, because Hacker News and Bluesky are the only sub-24-hour-fresh surfaces in the v1 roster, and their signal decays within a day regardless of how often packs are produced (SYNTHESIS §2a Change 7, §5 topic-extraction brief).
- **pack-production cadence** — governs how often the full pipeline runs through spin, copy generation, media planning and (budget permitting) media generation, packaging and notification. Recommended default once enabled: a small number of times per week rather than daily, because human video-review throughput — not topic availability — is the real bottleneck (20–30 minutes of operator QA per finished video, A1; SYNTHESIS §3.10).

Both knobs are **default off**: no scheduled runs of any kind occur until the operator makes an explicit enabling choice for each, per theme. Both accept a small named set of frequency options — at minimum daily and weekly, as the operator specified; a mid-frequency option (several times a week) is recommended additionally for pack-production cadence specifically, informed by the throughput reasoning above. A validation rule ties the two together: pack-production cadence should never be configured to run more often than research-collection cadence effectively refreshes signal, or packs would repeatedly re-rank the same stale collection window — this is a sanity check at theme-readiness time, not a runtime restriction.

Both knobs are per-theme (multi-theme is a first-class requirement elsewhere in this architecture), so one theme may collect daily and produce packs twice a week while another theme runs both knobs weekly.

### 8.3 Run identity and overlap policy

A run's identity is theme identifier + **run-date** (a pinned logical day, derived once at run start from a single configured theme timezone) + an attempt number distinguishing a manual rerun from the original scheduled attempt for that run-date (C3 §2.2). This identity is fixed once and carried unchanged through every stage, checkpoint and ledger row for the life of the run. Every stored timestamp is UTC internally; the theme timezone is used only to derive run-date and for human-facing display — this is what keeps a run from confusing "today" with "yesterday" when execution straddles midnight, and what avoids the documented daylight-saving double-fire/skip risk on both target schedulers when schedules are expressed in local time (C3 §2.2, W2-20).

**Overlap policy is skip-on-overlap.** If the run-lock is already held by a live run, a new invocation does not queue and does not kill the running instance — it logs and notifies a distinct **skipped-overlap** outcome (§8.8) and steps aside. Killing a running instance is explicitly rejected: it risks orphaning already-submitted, already-paid-for media jobs with no completing pipeline left to reconcile them against the spend ledger — exactly the "crash discards paid work" failure this whole design exists to prevent (C3 §2.2). A separate, explicitly operator-invoked "queue behind the current run" affordance exists for manual reruns only; the automatic scheduled trigger path never uses it.

**Locking is cross-platform and OS-mediated**: an exclusive lock held on a dedicated run-lock file for the life of the process — Windows exclusive file-open/share-deny and Linux advisory file locking are directly analogous, kernel-guaranteed-release-on-crash primitives (C3 §2.2). A ledger-recorded "in progress" row in the run ledger sits on top as a belt-and-suspenders check, independent of whether the lock file itself is trusted in a given edge case.

### 8.4 Missed-run policy: pipeline-owned skip-missed

Windows Task Scheduler and Linux systemd timers can both be configured to catch up a missed run; bare cron cannot (C2 §2.7, C3 §2.10) — a genuine cross-platform asymmetry. Rather than depend on whichever scheduler happens to be in use, the pipeline decides for itself: **missed windows are skipped, the pipeline runs once for "now," and the run ledger records how many windows were missed** (D-18's exit-code taxonomy carries this as a first-class fact, not a silent gap). This is deliberate on two grounds: content value decays with freshness (re-researching "what was viral three days ago" as if it were today's signal is a content-quality defect, not just an ops inconvenience), and a naive full-backfill policy risks a burst of consecutive, paid, automated runs firing back-to-back the instant a machine comes back online, with no pacing safeguard (C3 §2.10). OS-level "catch up a missed run" settings are harmless to leave enabled, since the pipeline's own run-ledger logic recognizes an unexpected extra invocation and applies the same skip-missed reasoning to it regardless of why it fired.

### 8.5 Idempotency and dedupe keys per stage

**Content-hash-based keys** are the identity mechanism for every cost-bearing stage: theme id + run-date + a stage-defined semantic input hash + the relevant config/prompt-template version (C3 §2.3). Natural keys (run id + stage name) remain a useful human-facing lookup index but are never the sole identity, because a same-day rerun after a deliberate brand-truth or config correction must be recognized as legitimately different work, not silently served from a stale cache.

Per-stage design: research/collection keys on theme + source + query/topic signature + run-date (or a configured rolling freshness window), so a retry recognizes existing raw captures for the run-date and skips or deltas rather than re-hitting rate-limited sources. Cross-day **topic dedupe** is a separate mechanism entirely — the **dedupe index** (canonical ledger, §8.6) keyed by **topic cluster key** (the normalized semantic identity, never raw text match) with a configurable rolling lookback window, distinct from within-run retry idempotency. Ranking keys on the input artifact set plus ranking-config version. Spin keys on ranked-topic id + brand-truth-snapshot id + voice-config version. Copy generation keys on spin-output id + destination/asset-type + prompt-template version. Packaging is idempotent by construction, keyed on run id + the set of included asset ids. Notification keys on run id + notification type, checked against an "already sent" marker so a retried run never double-pings the operator for the same event.

**Media generation is the one stage where the original C3 design must be corrected.** C3 originally specified a client-supplied idempotency token passed to the provider's job-submission call. A2's verified provider facts overturn this: **Kie documents no idempotency key, no client-reference field and no dedup semantics on task creation at all** (A2; corrected in SYNTHESIS §2b, D-17). There is no token to pass. The corrected design: **the write-ahead spend-ledger row is the idempotency mechanism.** A deterministic asset identity — theme, run-date, topic, asset slot, language, prompt-pattern version — is committed as an intent row *before* the submission call is made; the provider's task id is written the moment it is accepted; the terminal state and observed cost are written on resolution. On restart, an intent row with no terminal state is **resolved by querying the provider's own task-status endpoint, never by blind resubmission.** One asset identity permits at most one paid attempt chain (§8.7).

### 8.6 The ledger set

Eight to ten record types need a durable home; the substrate choice is not uniform. **SQLite** — an embedded, serverless, transactional single-file engine — holds every ledger where atomic multi-field updates and fast conditional queries matter: the **run ledger**, the **media-job ledger**, the **spend ledger**, the **dedupe index**, and the **review-decision store** (C3 §2.4; D-05, D-07 solo-operator reality). **Plain files** hold bulky, human-readable content: the bodies stored by the **research artifact store**, the contents of each **run pack**, and the body of each **brand-truth snapshot** — with a lightweight metadata row in SQLite (existence, checksum, snapshot id, confidence band) so other stages can look up "does this exist and what state is it in" without re-parsing a file (C3 §2.4). The **claim ledger**'s recommended home (Notion, per the Wave-2 synthesis) and the **model registry**'s home are owned by Draft A's brand-truth and media-provider architecture respectively; this section only asserts that both are referenced by id from the run pack and the spend ledger, never duplicated into a second store.

| Ledger | Substrate | Why |
|---|---|---|
| Run ledger | SQLite | Transactional checkpoint updates so a crash mid-write leaves a consistent last-known state, never a torn record; the scheduler/monitoring backbone |
| Media-job ledger | SQLite, most strongly of all | A live per-job state machine (§8.13) that must transactionally agree with the spend ledger on what was actually billed, and must answer "which jobs are nearing expiry and not yet downloaded" as a fast indexed query at the start of every run |
| Spend ledger | SQLite, non-negotiably transactional | Every paid call recorded as a row inside a transaction that also updates a running total; a torn write here has direct financial-integrity consequences |
| Dedupe index | SQLite | Needs a fast indexed "has this topic cluster key appeared within the lookback window" query across months of history; recording "topic used today" must be atomic with the ranking decision that used it |
| Review-decision store | SQLite | Inherently relational and status-driven — a pack has many assets each with independent, reason-coded approval state; a reviewer approving several assets in one sitting must not be left half-applied by a crash |
| Research artifact store (bodies) | Plain files | Bulky, heterogeneous, write-once/append-mostly content that benefits from direct human/text inspection during a source-breakage debug session |
| Run pack (contents) | Plain files | This is what a human directly opens and reads — maximally transparent, portable, readable with nothing more than a text or browser viewer |
| Brand-truth snapshot (body) | Plain files, metadata row in SQLite | Content inspectable during a claim-safety dispute; other stages reference "snapshot id N" as a fast structured lookup |

No client-server database service is installed or administered anywhere in this design — a solo operator with no server infrastructure gets full transactional guarantees from a file that ships next to the run and is backed up by copying it (D-05, D-07).

### 8.7 Per-unit-of-work checkpoint/resume

The explicit scenario this must survive: a crash at four in the morning after roughly ten dollars of media generation must not discard that paid work (C3 §2.5). The checkpoint granularity is **per unit of work** — one (asset slot × language × attempt), which is exactly one media-job-ledger row and exactly one paid attempt chain (G8, SYNTHESIS §2b). Each unit is checkpointed the instant its ledger row transitions state, independent of whether the surrounding stage as a whole finishes. On resume, the pipeline re-enters the stage and asks the relevant ledger what is terminal, what is pending, and what never started — acting only on the incomplete remainder. Whole-run or whole-stage checkpointing were both rejected: a full restart either wastes already-spent money or requires the same fine-grained ledger checks anyway, at which point coarser granularity has bought nothing (C3 §2.5).

Per-stage timeouts nest inside an overall run ceiling. As the ceiling approaches, the run performs **graceful wind-down** — stop starting new paid work, checkpoint everything in flight, package whatever is complete — never a hard kill (C3 §2.5). This directly protects the paid-work-preservation constraint: a single hung research source or a single slow media poll must never be allowed to consume the entire run's time allowance and prevent packaging of otherwise-complete, already-paid-for work.

### 8.8 Exit-code taxonomy

Nine named classes (D-18; SYNTHESIS §4.7), each mapped to one distinct process exit code for scheduler-level monitoring; the numeric mapping itself is deferred to implementation, and full detail (which source degraded, which policy tripped, exact stage and reason) lives in the run ledger, not in the exit code:

**success** · **completed-with-pending-media** (healthy — media jobs adopted by a later run) · **partial-success — degraded sources** · **partial-success — budget-capped mid-pack** · **completed-degraded** (research-only; the brand-truth degrade condition fired) · **budget-stop** (pre-emptive; no new spend occurred in the affected stage) · **policy-stop** (mode, allowlist, claim or policy violation — fail-closed) · **skipped-overlap** (not a failure) · **hard-failure** (infrastructure or technical).

A binary success/failure signal was rejected outright: it collapses "go look now," "fine, just review when convenient," "ran out of budget, nothing's wrong," and "something actually broke" into one bit, forcing a manual log check after every single run and defeating the point of unattended operation (C3 §2.6). A highly granular per-stage-per-reason numeric code was equally rejected — that level of detail belongs in the run ledger, a channel built for it, not in the OS exit code, a channel schedulers treat coarsely.

### 8.9 Unattended secrets

No interactive session exists at three in the morning to type a password. The baseline, identical in shape on both platforms, is **ACL/permission-restricted secret files**: NTFS ACLs on Windows and POSIX file permissions on Linux, each restricting read access to the exact account the unattended job runs as, kept outside source control (C3 §2.7; D-11). OS-native hardening layers on top of this baseline, never replaces it: DPAPI-protect the Windows secrets file's contents at rest once the task's run-as/logon configuration is confirmed to support it; adopt systemd-managed credentials once systemd timers are confirmed as the Linux scheduler (§8.1). A hard design rule independent of storage mechanism: secrets are never placed in source control, never embedded in prompts sent to any model, never written into the run ledger, and are redacted from every logging path.

A client-server secrets-manager service and relying solely on task-level environment variables were both rejected: the former is disproportionate infrastructure for a solo operator with no server (D-07) and introduces a new externally-reachable dependency with its own "unreachable at 3am" failure mode; the latter is more exposed to casual inspection and easy to leak into diagnostic logs or crash dumps than a permission-restricted file (C3 §2.7).

### 8.10 Retries and partial-failure semantics per stage

**Submission-type calls** (research fetch, LLM call, media-job submission) use exponential backoff with a capped attempt count and a capped total retry-time budget. **Polling an already-submitted async job** is a different operation entirely — a patient, bounded-duration loop against the job's own expected completion window — and must never be conflated with a retry: a naive retry wrapper applied to a submission call risks resubmitting and double-billing a job that actually succeeded on the provider side but whose response was merely slow to arrive (C3 §2.8; G3, SYNTHESIS §2b).

Per-failure-type handling: a **research source down** is a soft, per-source failure — logged, marked degraded in the run ledger and the pack, the rest of collection continues; this is what produces the partial-success (degraded-sources) exit class, and hard-failing the whole run over one flaky source was explicitly rejected as making the pipeline hostage to its most fragile dependency. An **LLM error** on a given artifact retries with backoff up to a capped count, and if still failing is marked incomplete for that one asset rather than fabricating filler — escalating to a stage/run-level failure only past a configurable share of failed units in that stage. A **media provider failure** at submission time follows the capped-retry-with-ledger-check path (§8.5); a job erroring out after successful submission is recorded failed in the media-job ledger with no further billing assumed, and is surfaced to the operator as "this asset's media failed, here's why" rather than silently dropped. **Disk full** is a hard-failure class, not a per-unit soft failure, because it risks corrupting an in-progress ledger write; the correct behavior is a proactive low-disk-space check at run start and again before the media stage specifically, failing closed before further writes once a safe threshold is crossed (C3 §2.8).

### 8.11 Budget caps, including mid-pack cap-hit

Budget enforcement happens at two granularities that work together. An aggregate **cost forecast** is computed across the whole plan for a pack (all planned assets across all languages) and is what an interactive operator sees and approves before media spend begins (§9, §12) — that approval authorizes *attempting* the plan, it does not disable the second granularity. Each individual media-job submission is still checked in real time, at submission, against the remaining budget (**cost gate**, canonical; pre-submission, never post-submission — A2, C3, C4). This is exactly what makes the mid-pack cap-hit case possible and safe: if the cap trips after three of six planned destinations are generated, **the pipeline ships the partial pack, clearly marked incomplete**, with the three completed destinations reviewable and the other three explicitly flagged as not-generated-due-to-budget (C3 §2.8). Withholding the whole pack until the cap is manually raised, or rolling back the three already-paid-for destinations for aesthetic consistency, were both rejected — the former delays or risks losing already-paid-for value with no offsetting benefit, the latter is the single most direct possible violation of the paid-work-preservation constraint.

Config knobs feeding this (output/runtime block, per theme): a **per-run media budget cap**, **per-day** and **per-month caps**, a **tier ceiling** (the highest tier an unattended run may auto-select — hero tier is never auto-selected regardless of ceiling, per A2/SYNTHESIS §1.6), and a **media-bearing-assets-per-run-per-language cap** that is deliberately separate from and much lower than the topics-per-run cap, because human video review — not topic volume — is the real throughput bottleneck (SYNTHESIS §3.10).

### 8.12 Notifications (W2.5-8: email)

A **filesystem status flag** is the mandatory, always-written baseline — it requires nothing external, so it cannot itself fail to be produced, and it remains the ground truth of "did today's run happen" independent of whether any push notification got through (C3 §2.9). **Email is the configured default push channel** (W2.5-8), with a chat webhook available as a config alternative (a **notification channel** knob, output/runtime block). Content covers "packs ready," each of the nine exit classes with human-readable framing, and a distinct **staleness escalation**: when the curated-inbox ritual that supplies the ICP-pain research axis (Reddit Pro plus weekly human curation, W2.5-2) is missed, the pack is labeled with a staleness flag, and **two consecutive missed rituals escalate the notification's prominence** rather than repeating an identical low-signal message (W2-01). This anti-flap principle generalizes: two consecutive identical degrades of any kind escalate rather than repeat, because repetitive identical alerts are exactly how alarms get ignored (C6 §5.5).

A notification-delivery failure is itself logged and reflected in the run ledger but **must never change the run's own exit class** — a failed email send is not the same fact as a failed run, and conflating them would let a mail-relay outage masquerade as a pipeline failure (C3 §2.9).

### 8.13 Kie async job lifecycle handling

Media generation is asynchronous and provider-owned; the console process has no stable public HTTPS endpoint to receive callbacks reliably, so **polling is the baseline** (roughly a 30-second interval), with a webhook receiver registered as a possible later optimization only (A2; G10, SYNTHESIS §2b). Renders typically take one to six minutes, with 1080p adding one to two more; a run legitimately ending with jobs still pending is healthy, not failure — this is exactly the **completed-with-pending-media** exit class, adopted and resolved by whichever run comes next (§8.8).

Three provider facts drive the design directly, all verified by A2 and none assumed:

- **No idempotency exists on the provider side** (§8.5) — the write-ahead spend-ledger row is the only mechanism; a process death between committing the intent row and recording the returned task id leaves a **submitted-unknown** state, which is never auto-resubmitted, only reconciled via a balance-delta check against the provider's own credit-balance endpoint (G1a, G5).
- **Generated media is deleted by the provider after fourteen days**, and result URLs carry their own, often shorter validity windows (A2; W2-02). Re-hosting every artifact is therefore **mandatory before an asset slot is marked complete**, with a checksum verified on download so a truncated transfer is never marked done. The **first phase of every run** — before any new submission is attempted — is to adopt pending tasks and drain the download queue ordered by nearest expiry (G2).
- **Rate limits are locally enforced pacing, not merely respected on 429.** A2 verifies roughly twenty new generation requests per ten seconds; a single two-language standard pack can submit on the order of twenty jobs in one burst. Submission paces itself well under that ceiling rather than bursting up to it, and a 429 response is met with backoff and jitter, never a tighter loop (G3).

A further fact changes what the media-job ledger must record, not just how it behaves: **Kie's routing can silently substitute a different backup model on some content-review triggers**, and a substituted output can be forced to a different aspect ratio than requested (W2-03; G6). The media-job ledger therefore records **requested route, aspect and resolution alongside delivered values** — surfacing any mismatch in the pack before it silently fails the platform gate at publish time, and feeding the per-asset provenance record (owned jointly with Draft A's media-provider architecture and §14's compliance treatment) that is resolved *after* completion, not at submission, since the model that actually rendered an asset may differ from the one requested.

*Media-job state progression (plain description, not a state-machine diagram in code):* submitted → polling → completed-pending-download → rehosted → done, with a diversion to **failed**, **expired**, or **submitted-unknown** possible at any point before done. The media-job ledger row is the single source of truth for where a given job sits on this path; resume logic reads that row rather than re-deriving state from scratch (§8.7).

---

## §9 End-to-End Flows

Both walkthroughs execute the same overall stage order (SYNTHESIS §1, canonical): theme load → brand-truth resolution → brand-truth gate → collection → ranking → fit gate → spin → copy generation → spin gate → claim gate pass 1 → voice gate → claim gate pass 2 → platform gate → media planning (always produced) → cost gate → media generation (async, may span runs) → assembly → packaging → notification → human review gate → publish gate → distribution prep. What differs between the two walkthroughs is *who* satisfies each human-shaped checkpoint and *when* — never the stage order itself, and never which code runs (§8.1).

### 9.1 Walkthrough (a): interactive operator run

theme load (operator selects theme, mode, optionally a single focus topic) → secrets load (interactive session; may use the brand-truth reader's interactive path for exploration) → brand-truth resolution, using the interactive access path where convenient, but producing the same kind of hashed **brand-truth snapshot** any run would (Draft A's brand-truth architecture) → **brand-truth gate** (if degrade fires, the operator sees the conflict directly and may consciously accept a research-only outcome — never silently) → collection (the operator may also drop items into the **curated inbox** live during this session) → ranking → **fit gate** → spin → copy generation, with each asset passing individually through spin gate → claim gate pass 1 → voice gate → claim gate pass 2 → platform gate → media planning (always produced, zero cost) → an aggregate **cost forecast** is shown in-session and the operator gives explicit go-ahead — this is the human satisfying the **cost gate** directly, synchronously, in real time (§8.11) → media generation proceeds (the operator may wait synchronously or return to the pack later, since generation is asynchronous regardless of invocation mode, §8.13) → assembly → packaging and run-digest write → notification (visible immediately in the session; email/flag written regardless, §8.12) → the operator opens the run digest, records decisions (§12) — this satisfies the **human review gate** → **publish gate** checks mode, allowlist, connection status and the recorded approval state (§7.4, §11) → distribution prep creates drafts (or falls back per the ladder, §7.2) for any approved, allowlisted, connected destination.

*Flow (plain arrow chain):* operator invocation → theme+mode+secrets (interactive) → brand-truth resolution → brand-truth gate (operator-visible if degraded) → collection (+ live curated-inbox entries) → ranking + fit gate → spin → copy generation + per-asset gate chain → media planning → cost gate (synchronous operator approval) → media generation (async) → assembly → packaging + digest → notification → human review gate (operator decision session) → publish gate → distribution prep.

### 9.2 Walkthrough (b): unattended scheduled run

scheduler fires (Windows Task Scheduler under the operator's own account, §8.1) → theme + mode + secrets load non-interactively from ACL-protected files (§8.9) → run identity fixed (theme + run-date + attempt, §8.3) → lock acquired, or the run exits immediately as **skipped-overlap** if one is already held → **phase 0**: adopt any pending media jobs from a prior run and drain the download queue ordered by nearest expiry, before anything new is submitted (§8.13) → brand-truth resolution via the non-interactive access path (the **brand-truth reader**'s unattended route, Draft A's architecture) → **brand-truth gate**: if the degrade condition fires here, the run proceeds on the **completed-degraded** path — research and ranking still complete and are still saved, but no brand content is generated, zero media spend occurs, and the digest states this in one sentence (C6 §5.5; this is a hard stop-or-degrade with no human present to override it, §11) → collection, per the theme's **research-collection cadence** (§8.2) → ranking + **fit gate** → spin → copy generation with the identical per-asset gate chain as the interactive path (spin gate → claim gate pass 1 → voice gate → claim gate pass 2 → platform gate) → media planning (always produced) → **cost gate** checked purely against the pre-configured budget caps (§8.11) — there is no human moment here; hero tier is never auto-selected regardless of remaining budget → media generation proceeds within cap, submission-paced (§8.13) → assembly → packaging and run-digest write → notification: filesystem flag always written, email sent (§8.12) → exit code emitted (§8.8) → the run stops. **No publish gate crossing occurs unless a human-approval state was already recorded in an earlier session for the relevant assets and the unattended draft-creation knob is on for this mode** (§7.6) — otherwise distribution prep simply does not run, and the pack waits for the operator's next session.

*Flow (plain arrow chain):* scheduler trigger → theme+mode+secrets (non-interactive) → run identity + lock (skip-on-overlap) → phase 0 (adopt pending media, drain expiry queue) → brand-truth resolution → brand-truth gate (auto-degrade possible, no override) → collection (per cadence) → ranking + fit gate → spin → copy generation + per-asset gate chain → media planning → cost gate (cap-only, no human) → media generation (async, paced) → assembly → packaging + digest → notification (flag + email) → exit code → stop (publish gate/distribution prep only if a prior approval exists and the unattended-draft knob is on).

### 9.3 Divergence table

| Dimension | (a) Interactive | (b) Unattended scheduled |
|---|---|---|
| Auth to brand-truth reader | May use the interactive access path for exploration; pack-bearing resolution still uses the same non-expiring path any run would | Always the non-interactive path — the only one that survives a run with nobody watching (Draft A's architecture; C1) |
| Brand-truth gate degrade | Operator sees the conflict card directly and may consciously accept a research-only (MINIMAL) outcome; may not override a red-flag conflict, an unreadable claim ledger, or unresolved excludes (C6 §5.4) | Fires automatically to **completed-degraded**; never overridable by anyone, because no one is present to override it |
| Cost gate | Satisfied synchronously by direct operator approval of the aggregate forecast, in-session, before media generation begins | Satisfied purely by pre-configured caps checked at each submission; no human moment exists; hero tier never auto-selected |
| Spend approval | An explicit go/no-go moment, once, for the whole pack's planned spend | No approval moment at all — only mechanical enforcement against caps, plus the mid-pack cap-hit behavior (§8.11) if they are exceeded |
| Human review gate | Satisfied within the same session, often minutes after packaging | Satisfied later, asynchronously, whenever the operator next opens the run digest — the run itself has already exited by then |
| Notifications | Visible immediately in the console session; email/flag still written for consistency and later audit | The only visibility the operator has until the next session — filesystem flag plus email are load-bearing, not a courtesy |
| Distribution prep | May proceed within the same session once the human review gate and publish gate are satisfied | Never proceeds unless a human-approval state was already recorded in a prior session **and** the unattended draft-creation knob is explicitly on for the active mode; otherwise it is simply skipped, not attempted-and-blocked |
| Output at exit | The operator typically stays engaged through packaging and often through the review decision itself | The run always terminates at a named exit class (§8.8) with the pack waiting, regardless of how "good" the pack turned out to be |

---

## §11 Modes & Gates

### 11.1 Capability matrix

Three modes (canonical, SYNTHESIS §4.3): **test** (default), **staging**, **live-prep** — never a fourth "live" mode, because there is no unattended live-publish mode in this system by design (non-negotiable constraint 1). The matrix below covers every side-effectful capability the assignment names.

| Capability | test (default) | staging | live-prep |
|---|---|---|---|
| Research reads / collection | Full — every configured source collects per its extraction method and cadence; research is never gated by publish mode | Full, unchanged | Full, unchanged |
| LLM spend (text generation, gates, judges) | Allowed, within per-run budget caps (§8.11) | Allowed, within caps | Allowed, within caps |
| Media spend (image/video generation) | Allowed if keys and budget are present, within the tier ceiling and per-run/day/month caps; hero tier never auto-selected regardless of mode | Same caps, unchanged | Same caps, unchanged |
| Publishing-bridge calls (draft creation) | Refused outright, before the call is attempted — the allowlist is empty by construction | Allowed only for allowlisted-and-connected destinations, only as drafts, and — if unattended — only when the unattended draft-creation knob is on | Same gating as staging; live-prep additionally expects every enabled destination represented in the prepared drafts |
| Publish / schedule-live action | Never a system capability, in any mode | Never | Never — always a manual human action inside the publishing bridge itself |
| Blog/site prep (article draft artifact) | Allowed — artifact-only, no live effect, so no mode restriction applies | Allowed | Allowed |
| Blog/site production merge | Never a system capability, in any mode | Never | Never — always a manual human action |
| Notifications | Always active (filesystem flag baseline always written; push channel per config) | Always active | Always active |

Two rows above are marked "never" rather than mode-gated deliberately: live publishing and production site merges are not capabilities this system has in *any* mode, not capabilities that happen to be switched off in test and staging. This mirrors the assignment's own non-negotiable constraint 1 literally rather than treating it as the strictest end of a gradient.

### 11.2 The mode capability resolver: one fail-closed choke point

Every stage about to perform an external side effect — a paid research call against a licensed vendor's credit budget, an LLM call that spends money, a media-generation submission, a publishing-bridge call, a notification send — consults one shared **mode capability resolver** before doing so. This is the single place the capability matrix above is encoded; no stage re-implements its own copy of "is X allowed right now," which is what keeps the matrix from drifting out of sync with itself across the codebase (RA-8).

The resolver's answer is consumed by two named, more specialized gates for the two side-effect families that carry the most risk, rather than by one undifferentiated check everywhere:

- The **cost gate** (canonical, A2/C3/C4) consumes the resolver's answer for spend-type effects — LLM calls, media-generation submissions, licensed-vendor credit spend — checking mode, the relevant budget cap, and (where applicable) brand-confidence band, before the call leaves the process.
- The **publish gate** (canonical, C1/F-4/D-23) consumes the resolver's answer for publish-type effects specifically — it is, per D-23, **the single fail-closed enforcement point** for that family, additionally layering the publish allowlist, connected-channel status and the recorded human-approval state on top of the resolver's mode check (§7.4).

Both gates read from the same resolver rather than encoding mode logic independently, which is what makes this "one choke point" in the sense the risk log asks for: there is exactly one place the answer to "does this mode permit this class of side effect" lives, even though two named, differently-shaped enforcement points act on that answer downstream.

### 11.3 Fail-closed triggers

Each of the following stops the run at the appropriate named exit class (§8.8) or degrades it to research-only — never proceeds "anyway," and never silently downgrades to a softer behavior than the one it names:

- **Missing secrets.** Any required secret absent or unreadable at theme load is a hard stop (policy-stop or hard-failure, depending on whether the missing secret is theme-specific or infrastructure-level) — there is no silent "skip that provider and continue" for a credential the theme declares it needs.
- **Ambiguous brand truth.** The unattended degrade trigger is exact, not a vibe (C6 §5.4, owned by Draft A in full detail, consumed here): the confidence band falls below PARTIAL; any unresolved red-flag conflict exists on a commercially binding fact; the offline brand-truth snapshot is expired or fails its integrity check; the claim ledger could not be read at all (distinct from being legitimately empty); or hard excludes are unresolved (not merely empty). Any one of these routes the run to **completed-degraded**: research-only output, zero brand content, zero media spend, stated as such in the digest.
- **Policy violation.** A claim-gate CONTRADICTED verdict (an asset asserts something the resolved brand facts explicitly deny, §14), a mode/allowlist mismatch, or any other detected policy breach routes to **policy-stop** for the affected asset or run.
- **Mode violation.** An attempted side effect the active mode's row in §11.1 marks as never-permitted (a live-publish call, a production site merge, any publishing-bridge call in test mode) is refused at the resolver before it is attempted, not caught after the fact.

None of these four trigger classes are configurable away to "warn and continue" — that would defeat the entire point of a system designed to run unattended against a limited budget with nobody watching.

### 11.4 How human-approval states are recorded and consumed

**Recorded.** The **review-decision store** (canonical ledger, §8.6) holds one reason-coded approve/reject/partial decision per asset (and, where useful, per topic or per pack as a whole), keyed by run id and asset id, with attempt history retained rather than overwritten. Two input mechanisms write into this same store — they are not two different approval models, only two ways of expressing the same decision: editing a **decision file** that accompanies the run digest (§12), or issuing an interactive console command that references the run id. A rejection is always reason-coded, both because that discipline is what makes the learning loop in §12 trustworthy and because "the topic was wrong" must never be conflated with "I had enough content this week" when feedback is later aggregated.

**Consumed.** The publish gate reads the review-decision store as its human-approval-state layer (§7.4, §11.2): distribution prep will not act on any asset lacking a recorded approve decision, and a partial decision — for example, "approve the copy, reject the video" — is consumed at the individual asset-slot level, never at the whole-topic level, which is exactly the granular rejection model §12 describes. Auto-approve is never config-enabled in v1, in any mode (C4's own open question, resolved conservatively here): every live-affecting decision passes through a human, recorded in this store, before the publish gate will act on it.

---

## §12 Run/Review Package Anatomy

The pack anatomy below adopts C4's decision *content* in full — what an operator must see and be able to decide — while replacing C4's interaction *mechanism*, per the synthesis's own correction: **the run digest is a static, human-readable document living with the rest of the run pack's contents, not a web application** (SYNTHESIS §3.11; D-07, C3's no-server reality). Nothing in this section implies a browser back-end, live buttons, or session state; "the operator clicks approve" throughout is shorthand for "the operator edits a decision file, or issues a console command referencing the run id" (§11.4).

### 12.1 The run digest — the single entry point

One document per run, designed to be scannable in about two minutes (C4 §1). It carries, at minimum:

- a header: **run id**, run-date, theme, mode, and a plain-language status line (naming a brand-truth degrade in one sentence if one fired, C6 §5.5);
- a **cost forecast**, prominent, decomposed per topic and reading from the model registry's current price snapshots rather than any hard-coded figure (so the forecast stays honest as provider prices drift — SYNTHESIS §3.10 corrects an earlier illustrative-figures approach in favor of this);
- a topic table: one row per **ranked topic**, each carrying its **scorecard** (sub-scores, confidence band, one-line rationale per dimension, evidence-quality label), freshness and cross-day dedupe status (what changed since a prior appearance, per the **topic cluster key**), and a decision state;
- degraded-source banners: which sources were unavailable this run and how that is expected to affect coverage (per-source degrade notes, §8.10), plus the curated-inbox staleness banner when the Reddit-curation ritual has been missed (W2-01, §8.12);
- a footer linking to per-topic detail, the full cost breakdown, and any regeneration queue (assets still cycling through the bounded regenerate loop, §14).

Confidence-gated defaults reduce decision load without removing the decision: topics at a high confidence band are presented pre-selected for approval; medium-band topics are presented unselected; low-band topics require the operator to open the per-topic detail before any approval is possible (C4 §1D). Batch operations remain the default affordance — approving an entire pack, or an entire language, in one recorded decision is normal; the granular per-asset override (§12.3) exists for when it is needed, not as the default path.

### 12.2 Per-topic, per-language contents (the identical-mix rule, W2.5-4)

Under W2.5-4, both configured languages receive the **identical destination × asset-type matrix** — the operator's explicit choice, overruling the synthesis's own lean toward per-language-appropriate mixes, with doubled media spend accepted as the cost of that choice (OP-1 stands). What differs between languages is the **recipe**, not the mix: which production path a given asset type actually uses (owned in full by Draft A's viral-video-pipeline architecture, referenced here by pointer only). This section's obligation is that the pack anatomy make the *mix* visibly identical across languages while making the *recipe* difference visible too, so the operator can confirm the Czech assets are not simply the English ones with weaker production values (the reputational risk W2-08 names directly).

Per topic, per language, the pack carries:

- the copy and script assets for every destination the theme's output/runtime block enables, at the identical mix across languages;
- the video plan (shot list or slide list) for every video-bearing asset, always produced regardless of budget (media planning is a zero-cost stage, A2/SYNTHESIS §1.6), plus the generated media itself where the cost gate allowed generation to proceed;
- the **spin rationale** — topic id, detected pain, ICP segment, mapped offer, **mapping distance**, CTA class, and the **fact-usage trace** — so the operator can judge "was this a natural connection" in seconds rather than re-deriving it (C6 §9.4);
- a reference to the **brand-truth snapshot** this topic's pack consumed (by snapshot id and fact-usage trace, not a re-embedded copy), so a later correction to brand truth can be traced forward to exactly the packs it affected;
- claim-check results per asset: which check classes ran, what verdict each extracted candidate received, and the attempt history if any regenerate or downgrade-repair occurred (§14);
- source links and extraction notes for every signal that fed the topic — the extraction method used, retrieval timestamp, and raw metrics, so the operator can audit "where did this come from" without trusting the pipeline's summary (B2 §2.7);
- a **provenance record** per generated media asset — the delivered route identity and version, generation timestamp, a snapshot of that route's commercial-use terms as they existed at generation time, the router transaction id, and delivered-versus-requested route/aspect/resolution where they diverge (W2-03, C7 §2.8, §8.13);
- **automation metadata** — run id, mode, stage durations, candidate counts at each filtering step, and which cadence produced this run.

### 12.3 The cost gate as an operator-facing checkpoint

Research and ranking complete, at zero cost, before anything spend-bearing is attempted (media planning is likewise always produced at zero cost). The cost forecast in the digest is what lets an interactive operator satisfy the **cost gate** directly — reviewing the forecast and giving explicit approval before media generation begins (§9.1). In an unattended run the same gate is satisfied mechanically, against pre-configured caps, with no digest-reading moment involved at all (§9.2); the digest still shows the forecast that resulted, for the operator's next session.

### 12.4 Rejection and regeneration flow

Rejection is granular, recorded at the level it actually applies to, and always reason-coded (§11.4): reject just the video and keep the copy; reject one topic and keep the rest of the pack; reject the whole pack with pack-level feedback. Each of these writes into the review-decision store as its own decision, at its own scope.

Feedback capture feeds three distinct loops, deliberately kept separate so a same-session fix is never confused with a slow, human-governed calibration change:

- **Immediate loop** — a rejected asset regenerates within the current pack, with the specific feedback fed back as corrective context, subject to the same bounded regenerate cap and cost circuit breaker as any other regenerate (§14).
- **Weekly loop** — aggregated rejection reasons across recent packs inform prompt-library and rubric refinements; this is read and applied by a human, not auto-applied.
- **Theme-tuning loop** — long-term calibration (ranking thresholds, brand-fit floor, judge cutoffs) is reported monthly and moved only by a logged human rationale; automatic threshold recalibration is explicitly rejected (OD-20, W2-10) because it optimizes for whatever gets rubber-stamped quickly, which is not the north star.

### 12.5 Static-file digest, decision mechanism

No web server, no local service, no session state exists in this design (C3, C2's scheduler-agnostic reality). The digest is a static document; a decision is recorded either by editing a plain decision file that sits alongside the digest in the run's own output location, or by issuing an interactive console command that references the run id — both write into the same review-decision store (§11.4). Nothing about the digest's content is diminished by this: it may present headers, tables, confidence bands, and a cost breakdown exactly as rich as a dashboard would, because none of that requires a live backend to render once — it only requires that "clicking a button" be understood, throughout this document, as one of the two recording mechanisms above.

### 12.6 Notion-upload mapping (D-07, later phase, zero re-entry)

An optional, later-phase, config-gated upload of a completed pack's contents into Notion is designed so that it requires no re-entry of anything the pack already contains (D-07). The mapping is conceptual, not a schema:

| Notion destination field | Sourced from |
|---|---|
| Topic | The topic table entry in the run digest |
| Destination / platform | The per-topic, per-language asset set (§12.2) |
| Language | The per-language asset set |
| Content | The copy/script asset body |
| Media reference | The provenance record's route identity plus the re-hosted asset location (never a provider URL, §8.13) |
| Run id | Automation metadata |
| Operator decision | The review-decision store entry for that asset |
| Engagement | Left blank at export time; tracked later, directly in Notion, once the asset is actually live |

This mapping is a later-phase convenience layer on top of an already-complete pack, never a precondition for the pack itself being useful; every field above already exists in the pack for the operator's own review regardless of whether Notion upload is ever enabled.

---

## §14 Voice + Claim-Safety Enforcement

This section describes one coherent layered gate, not three independent checks bolted together. The canonical per-asset ordering (SYNTHESIS §4.4, D-21, binding) is:

*generate → spin gate → claim gate pass 1 (fail-fast) → voice gate → claim gate pass 2 (final, immutable, on packed bytes) → platform gate → (media only) cost gate → media generation → assembly → asset QA rubric → packaging.*

This ordering is deliberate on two counts, both load-bearing rather than stylistic. **Spin precedes voice** because the two failures need different repairs — a spin failure means the topic/offer pairing was wrong and the fix is to drop the offer or change the angle, never to reword; a voice failure means the phrasing is wrong and the fix is a rewrite. A well-voiced piece of forced relevance is *harder* for a reviewer to reject than a clumsy one, so checking connection honesty before polish prevents good prose from laundering a bad idea (C5 §7; C6 §9.5). **The claim gate runs twice, bracketing the voice gate,** because the voice gate rewrites text, and a rewrite can silently reintroduce a claim an earlier pass had already cleared — the last gate before packaging must see the exact bytes that will ship (D-16; C6 §7.3).

### 14.1 Spin gate

Two checkpoints, not one (C6 §9.5, C5 §7): an **angle-level pre-check** immediately after brand-spin resolution and before any drafting tokens are spent, and an **artifact-level post-check** on the finished draft, catching drift that crept in during writing — a soft, hedged mention in the brief becoming a confident, unhedged claim by the time the copy exists.

Seven criteria, each recording the evidence for its own verdict (C6 §9.4):

- **S-1 real topic anchor** — traceable to a specific logged research signal; operational test: could this asset have been written yesterday without this topic? If yes, fail.
- **S-2 ICP addressing** — names a recognizable situation for a *configured* segment, never a generic "businesses"/"teams."
- **S-3 connection chain** — an explicit, checkable bridge from topic to consequence to offer relevance; deleting the offer-mention paragraph should still leave a genuine point, and deleting everything else should leave something specific to *this* topic, not pastable onto any trend.
- **S-4 distance compliance** — offer prominence matches the mapping distance (direct / adjacent / far, owned by Draft A's brand-truth architecture); a far-distance topic carrying a product pitch fails outright.
- **S-5 proof discipline** — no proof-shaped statement without a claim-ledger entry, including implied results.
- **S-6 next-step correctness** — at most one CTA, of an allowed class, correctly routed and language-coherent.
- **S-7 no hype-glue** — the connection survives removal of connector inflation ("this is exactly why…"); forced relevance disguised as a transition still fails.

Enforcement: fail on a specific criterion → bounded regenerate citing that criterion → second failure → **downgrade to the value-only variant** (drop the offer, keep the insight, content-class CTA only) → still failing → drop the asset with the reason recorded, never silently. The value-only downgrade matters because most spin failures are failures of the pairing, not of the writing — the correct repair is usually to stop selling, not to rewrite harder (C6 §9.4).

### 14.2 Voice gate

Five layers, cheapest and most mechanical first, most expensive and judgment-heavy last (C5 §2). Nothing here is ever silently shipped, and nothing is ever silently dropped — a failing artifact still enters the pack, explicitly labeled, with its full attempt history attached.

1. **Lexicon screen** — deterministic, near-zero cost, per language. Catches the assignment's seed list of banned phrases and patterns, plus a **cross-pack recurrence check**: comparing a new draft's opener and core phrasing against a rolling window of the theme's own recently generated artifacts, per platform and language, to catch the *system* developing its own repeated house tic — the same failure mode observed directly in the exemplar corpus, where near-identical templates recur across different named authors (C5 §2, fact ledger). This is **house-style-tic drift monitoring**, and it is a standing, always-on check, not a one-time calibration step.
2. **Structural heuristics** — sentence-length variance, em-dash density, bullet vagueness versus bullet density, opener repetition; calibrated from the theme's own exemplar corpus rather than a universal number, and always followed by the LLM judge, never allowed to independently accept or reject on its own (C5 §2, Layer 2).
3. **LLM judge** — semantic evaluation against the full voice rubric (§14.4), producing a structured pass/fail per criterion plus a diagnosis and fix category. The judge is a different call, ideally a different model lineage, from the generator, to reduce shared blind spots (C5 §2, Layer 3).
4. **Bounded regenerate loop** — on judge fail, regenerate with the judge's diagnosis fed back as corrective context, up to a hard, configurable **regenerate cap** counted per artifact. This cap is the primary circuit breaker on worst-case unattended cost, independent of *why* the judge is failing things (C5 §4) — a too-strict judge in a cron run pays for (1 + cap) generation calls and (1 + cap) judge calls per artifact for zero net quality gain, and the cap is what bounds that regardless of root cause.
5. **Escalate to review** — terminal. If the cap is reached without a pass, the artifact ships into the pack clearly labeled "did not pass voice/spin gate," with full diagnosis and attempt history, never force-shipped as a best effort and never quietly dropped (C5 §2, Layer 5).

**Judge calibration and the false-positive economics.** A golden set (adapted positives, deliberate negatives, real borderline drafts from pilot runs) supports human-vs-judge agreement measurement, tracked **by direction** rather than as one blended accuracy number: judge-passed/human-failed (the dangerous direction — slop ships) is tuned separately from judge-failed/human-passed (the expensive direction — wasted regenerate cycles and review-queue flooding), because the two carry different business costs (C5 §4). A rolling **flag-rate ceiling** is tracked per theme/platform/language as a judge-health signal distinct from any individual artifact's flag — a flag rate meaningfully above what golden-set calibration predicted is a warning about the judge or the generator, not a queue to keep waving through. When launching a new theme or language pair with limited calibration data, the recommendation is to start lenient and tighten as real agreement data accumulates, because an under-strict judge costs a little extra human attention while an over-strict judge in an unattended context costs hard tokens and throughput that compounds silently (C5 §4).

### 14.3 Claim gate

Two halves that must not be merged (C6 §7.1): the **claim ledger** (what may be said — owned by Draft A's brand-truth architecture) and the **claim check** — a verification pass over generated bytes — owned here. The check runs over every generated surface in every language: post bodies, hooks, captions, carousel slide text, on-image text, video scripts and spoken lines, alt text, blog copy, CTA text, and hashtags (a hashtag can itself carry a claim). Deterministic extraction runs first and is followed by semantic checking, never the reverse — an LLM-only checker is non-deterministic and can be argued out of a block by the same model family that wrote the copy; a component's self-assessment is not a control over that component (C6 §7.1).

Eleven check classes (C6 §7.2, summarized — full lexicon and per-class detail owned by C6/C5 and referenced here rather than restated): numeric quantity, currency/price, named entities (four-way: own brands/team allowlist versus client names requiring permission versus neutral competitor references versus unknown entities, which are blocked as a hallucination tell), outcome/result (including number-free forms), superlative/absolute/uniqueness, capability/autonomy (checked against both positive and negative capability statements, so a claim like "sends for you" fails even with zero digits present), temporal/availability, comparative/competitive, endorsement/social proof, required-statement (bidirectional — a *missing* mandatory disclosure is a defect of the same class as a false claim, and this is exactly where the AI-label acknowledgement in §14.5 attaches), and **corpus leakage** — generated numbers, metric phrases or named entities that appear in the exemplar corpus but nowhere in the claim ledger, blocked outright and logged as a leakage event.

Verdicts: VERIFIED, SAFE-NON-CLAIM, UNSUPPORTED (blocks), CONTRADICTED (blocks and raises a brand-truth review flag, since it may mean the ledger itself is wrong), DISCLOSURE-MISSING (blocks until inserted). Enforcement ladder, per asset, never per pack and never per run: block → bounded regenerate (a small fixed maximum, fed the specific failing spans and a positive constraint) → downgrade repair (emit the claim-free variant — value-only, no proof, softer CTA) → drop the asset with the reason recorded. The **retry allowance is budgeted per pack, not per asset** — otherwise a systematically bad prompt in an unattended run burns the token budget on a single regeneration storm; exhausting the pack's allowance degrades that pack to review-required rather than failing the whole run (C6 §7.3).

**The claim check runs twice** for the reason given at the top of this section: pass 1 fail-fast, early; pass 2 as the final immutable gate on the exact bytes entering the pack, because the voice gate's rewrite is what pass 2 exists to catch (D-16).

### 14.4 Per-language rubrics

**English** is exemplar-grounded, authored directly from the local corpus of real winning posts (C5 §3): hook shape, specificity/proof anchoring, personal stake, rhythm, structure, and CTA target-versus-tone are each stated as a pass bar and a fail smell drawn from what the corpus actually does — with an explicit design note that the corpus's craft is borrowed while its hype language and gamified hard CTAs are explicitly rejected, because several of the corpus's best-performing posts would fail this project's own rules if reproduced verbatim.

**Czech** is concrete now, not a placeholder framework, filled from B4's empirical findings via C5 §2c (SYNTHESIS §2c). It carries its own three-layer structure mirroring §14.2's five-layer stack at the language level: a **calque blocklist** with named native alternatives (so a regenerate instruction is actionable, not just "this failed"); structural tells specific to Czech (openers, hedge stacking, formality flips); and a **code-switching allowlist** that is a permission list, not only a block list — English nouns naming tools, metrics and categories are normal Czech tech register and must not be flagged, while English-rooted verbs and abstract benefit nouns are the actual slop. An eleven-dimension judge rubric sets **vykání as the default register** for every public post and first-contact CTA, with tykání permitted only where theme config explicitly declares a peer-community context (resolving an internal conflict in the source research, D-26). A Czech soft-CTA phrase bank is mapped to the same CTA classes the claim gate and spin gate already use. Because Czech professionals flag AI-generated content faster and more harshly than the English-language evidence base suggests for English readers, the Czech judge weights the human-voice dimension higher than the English judge — an empirical asymmetry, not a stylistic preference (C5 §2c).

### 14.5 Spoken-claim enforcement

Three rules, in order of primacy (C6 §8):

1. **Script-lock is the primary control.** Spoken content is generated only from claim-checked script text; the script is the verified artifact of record, and audio is a rendering of it, never an independent source of claims.
2. **In unattended runs, spoken lines carry zero claim tokens** — no numbers, currency, entities beyond the theme's own brand, superlatives, or outcome statements. All claim payload lives in burned-in on-screen text, composed at assembly time from verified strings, which can be re-read before packaging. This deliberately drains the audio channel of anything a model's improvisation could fabricate that would actually matter.
3. **ASR runs as a sampled adherence monitor, never as the per-asset gate.** Its job is to measure whether the model said what it was told, on every asset during the first weeks and then a rolling sample thereafter, and always after a provider or model change. A measured adherence drop is a provider-level alarm that can disable audio for that route — it is not a pass/fail check on any individual asset.

The rationale is preventive-over-detective: script-lock stops a bad claim before generation is paid for; ASR would only detect it after the money is spent, which is the worst place to discover a problem under cron budget caps (C6 §8). The design is also language-neutral by construction, which matters because Czech ASR accuracy on marketing audio is materially weaker than English — a gate whose accuracy varies by output language would be a poor primary control for a project whose Czech output is mandated first-class (D-02), since it would over-block Czech on false alarms and under-block it on dropped or mistranscribed numbers alike.

### 14.6 AI-labeling and provenance placement (F-8, W2-04)

**The burned-in, human-perceivable disclosure applied at render time is the load-bearing compliance control**, not a courtesy. EU AI Act Article 50 became binding on 2 August 2026, with no size exemption and fines up to €15 million or 3% of worldwide turnover (C7 §2.4). Because major platforms re-encode nearly every upload — stripping C2PA Content Credentials in the process, characterized as effectively total removal — metadata-only compliance fails silently (C7 §2.4a; F-8). Every AI-generated video, image, or audio asset therefore carries a visible or audible disclosure baked into the rendered pixels or audio itself, applied during assembly, and **an asset without it cannot be marked publish-ready** regardless of any platform-native label described below.

**C2PA is signed after the final encode and archived with the pack** — worth doing because some platforms read the manifest before stripping it, to power their own auto-labeling, but this is never the compliance mechanism and this architecture makes no claim that provenance metadata survives distribution end to end (C7 §2.4a). The per-asset **provenance record** (delivered route identity and version, generation timestamp, a snapshot of that route's commercial-use terms at generation time, the router transaction id — §8.13, §12.2) is what actually defends a rights or compliance challenge later, not the metadata embedded in the file.

**Per-platform label mechanics** (separate, cumulative contractual obligations, distinct from the EU-law duty above — C2 §2.3): TikTok exposes an AIGC boolean field on its Content Posting API's Direct Post endpoint (defaulting to false), alongside a UI toggle and automatic labeling from read C2PA metadata. YouTube's Data API v3 exposes a settable synthetic-content boolean property on video insert/update, alongside a Studio upload-flow question; 2026 rollout adds automatic detection with non-removable proactive labels for undisclosed content. Meta's organic path is a publish-time UI toggle with no confirmed organic API field as of the research date (an explicit open verification item, C2 D2) — its machine path is metadata-driven, which is one more reason C2PA is worth preserving even though it is not the compliance mechanism. LinkedIn has no confirmed structured toggle at all; the recommended interim practice is a short per-post disclosure line composed directly into the copy for any substantially AI-generated visual asset, revisited if LinkedIn ships a dedicated control.

**Because the publishing bridge cannot carry any of these platform-native flags** (§7.7, W2-05), this mapping cannot be set programmatically through distribution prep in v1 — every one of the mechanics above is a manual action the operator takes in each platform's own interface, after a draft already exists. The **publish-gate label acknowledgement** (§7.7) is the control that keeps this from being silently skipped: every asset whose AI-content class requires disclosure carries an AI-label-required flag, and the publish gate will not treat that asset as ready until the operator has given a separately recorded acknowledgement — not folded into the general pack approval, because bundling it is exactly how a busy operator skips it.

### 14.7 Prompt and model version pinning per pack

Every artifact in every pack carries, as metadata, which prompt-pattern version and rubric version drafted and judged it, and which model/version string ran each of the drafting, judge, and polish roles (C5 §5). This is what makes "did the last prompt or model change actually help" answerable months later, and it is the precondition for the judge re-calibration cadence in §14.2 — a rubric or model change without a fresh calibration pass against the golden set is exactly how silent drift happens. It also feeds the provenance record's own versioning discipline (§14.6), so a pack's claim-safety and voice-safety state is as auditable after the fact as its media-generation state.

---

*End of Draft B. Sections §7, §8, §9, §11, §12, §14 only — see DRAFT_A_core_pipeline.md (not read by this agent) for §1–6, and the Wave-3 assembler's own output for §10, §13, §15–18.*
