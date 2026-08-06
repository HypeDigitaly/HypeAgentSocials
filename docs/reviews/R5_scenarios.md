# R5 — Scenario Red-Team Review

Reviewer: R5 (Wave 4, independent). Method: walk five mandated failure scenarios plus four
invented ones end to end through `ARCHITECTURE_PLAN.md` (2340 lines, read in full) and
`RISK_LOG.md` (read in full), quoting section numbers at each step, and marking every point
where the plan is silent, ambiguous, or self-contradictory. Supporting facts cross-checked
against `docs/research/A2_video_providers.md`, `C3_cron_ops_state.md`, `C1_notion_postiz_integration.md`
and `B3_ranking_scheduling.md` where the plan's own text pointed there. No new web research.
No style commentary — every observation below is a concrete gap with a required change.

Findings use the mandatory format: **severity (blocker / major / minor) | section ID | claim
(the gap) | required change**. They are numbered F1–F23 in the order they appear and are
also collected in the summary table at the end.

---

## Scenario (i) — 03:00 unattended run, Notion internal-integration token revoked the day before

**Setup.** The token was not merely expired (REST internal-integration tokens are documented
as non-expiring, plan fact-ledger row 5, §0.3) — it was actively revoked, e.g. by a workspace
admin rotating credentials, deleting the integration, or a permissions change. This is a
materially different failure than the "MCP token expires every three hours" case the plan
spends real design effort on (§6.2).

**Trace, minute by minute.**

03:00 — scheduler fires, run identity pinned, lock acquired (§8.3). Phase 0 adopts any
pending media (none relevant here) (§8.13, §9.2).

03:00+ε — **Brand-truth resolution runs first, before collection and before any spend**
(§6.1, §9.2): "config load → snapshot validity → Notion pull → targeted site verification"
(§6.6). The Notion pull is attempted over **Notion REST, internal integration token** — "the
only one that survives a run with nobody watching" (§6.2, §9.3 divergence table). With the
token revoked, every REST call returns an authorization failure.

03:00+ε — **Gap.** §8.10 defines retry policy only by call *shape* ("submission-type calls…
exponential backoff with a capped attempt count") — it never distinguishes an
authentication-class failure (permanent, will never self-resolve) from a transient
network/5xx failure (worth retrying). Nothing in §6, §8 or §11 says the Notion-pull path
recognises "401/revoked" as a distinct, non-retryable class versus "timed out, try again."
This matters because the *content* of what the operator eventually reads depends on whether
the system actually knows *what kind* of failure this was.

> **F1 | major | §6.2, §6.6, §8.10 | claim: brand-truth resolution "reads only from
> designated fact locations" and produces "a specific fix action" (§6.5) for the operator,
> but no section anywhere states that the Notion-pull failure path classifies *why* the pull
> failed (revoked vs expired-elsewhere vs network-down vs endpoint-moved). Retry policy is
> defined only by call shape, not by error class. | Required change: state explicitly that
> the brand-truth reader classifies HTTP/auth error codes into at least {transient, permanent-auth,
> permanent-endpoint} and that only the transient class is retried with backoff; specify that
> a permanent-auth failure is recorded verbatim (status code, timestamp) into the brand-truth
> panel so "the actual cause and the actual fix" (§6.5) is not aspirational.**

03:00+ε — With Notion REST unreachable, §6.2's own table says: "REST integration unavailable
→ A self-hosted token-based MCP server — a contingency, not a design branch." This is
explicitly *not* a built path — it is a stated non-implementation. So in practice: "All paths
fail → Offline snapshot → band capped at MINIMAL → unattended degrades to research-only."

03:00+ε — Because the token was revoked *the day before*, yesterday's run presumably
succeeded and wrote a valid FULL/PARTIAL snapshot (§6.6: "The last successful FULL or
PARTIAL snapshot is persisted append-only"). Today's run falls back to it. **Snapshot reuse
TTL is correctly scoped** — "How long a resolved snapshot may be reused **across runs on the
same day**" (§10.3) — so the daily 03:00 run does not accidentally skip re-pulling Notion by
reusing a stale intra-day cache; this part of the design holds up.

03:00+ε — Offline snapshot within the 7-day unattended window (§6.6) → band capped at
**MINIMAL**, which is below PARTIAL → **unattended degrade trigger condition 1 fires**
(§6.5): "The band is below PARTIAL." Run proceeds on the **completed-degraded** path (§9.2,
§11.3): research and ranking complete and are saved, zero brand content, zero media spend,
digest states this "in one sentence."

**Gap.** §11.3's "missing secrets" trigger reads: "Any required secret absent **or
unreadable** at theme load is a hard stop (policy-stop or hard-failure)." A revoked token is
neither absent nor unreadable *as a file* — it is present and syntactically fine, but invalid
*in use*, which is only discoverable deep inside brand-truth resolution, not at theme load.
The plan never draws this boundary explicitly, so a reader cannot tell from the text alone
whether a revoked-but-present credential is meant to trip the theme-load hard-stop path or
the brand-truth degrade path (which is what actually happens, per the trace above, but only
because brand-truth resolution is the first stage to *use* the token, not because the plan
says so).

> **F2 | minor | §11.3, §6.2 | claim: "missing secrets… absent or unreadable at theme load"
> is a hard stop, distinct from the brand-truth degrade path — but "unreadable" is never
> defined narrowly enough to exclude "present but invalid/revoked," leaving two fail-closed
> mechanisms with an unstated boundary between them. | Required change: state explicitly that
> theme-load secret checks are presence/syntax-only, and that credential *validity* is
> discovered only at first use (brand-truth resolution, site verification, media-router
> auth), each reporting through its own already-defined degrade path.**

08:20/09:00 — Operator opens digest. Per §6.5, the digest should show "one plain sentence…
naming the actual cause and the actual fix" plus "a brand-truth panel with one row per
blocking class showing state, source used, observation age and a specific fix action." Given
F1 above, whether that sentence actually says "Notion integration token was rejected —
reissue it in Notion → Settings → Connections" (actionable) or the generic "brand truth
degraded, see log" (not actionable) is not determinable from the text — the plan asserts the
*outcome* (a specific fix) without specifying the *mechanism* that would produce it for this
exact failure class.

**Gap — the sharpest one in this scenario.** The plan gives Meta Ad Library's 60-day token a
named, proactive, fail-closed alarm and an explicit Phase-0 runbook item: "**Token-expiry
alarm with fail-closed behaviour**… Renewal is a named runbook item" (R-05, §17 Phase 0:
"token-renewal runbook written (W2-15)"). The Notion internal-integration token gates **all
brand content for both languages, every single run** — a strictly larger blast radius than
one research axis — yet no equivalent proactive alarm, expiry/health check, or runbook entry
exists anywhere for it. The design's own confidence that this token is "non-expiring"
(fact-ledger row 5) appears to have substituted for a health check, when "non-expiring" says
nothing about "cannot be revoked."

> **F3 | major | §2.3 (R-05), §6.2, §17 Phase 0 | claim: the plan treats credential health as
> a named, alarmed, runbooked risk for the Meta Ad Library token but has no equivalent
> mechanism for the Notion internal-integration token, despite the latter gating strictly more
> of the system's output (both languages, every fact class, every run) than the former gates
> (one research axis). | Required change: add a Notion-token health check (a cheap read-only
> API call at run start, independent of the full brand-truth pull) with the same fail-closed
> alarm treatment as R-05, and a Phase-0 runbook item for token reissue, so a revocation is
> caught and named specifically rather than discovered only via the generic brand-truth
> degrade path.**

A secondary, smaller gap: the plan never states what happens if **no** offline snapshot
exists at all (e.g., a brand-new theme's very first run coincides with a Notion outage before
any successful pull has ever completed). The table in §6.2 implies "offline snapshot" is
always available as a rung, but §6.6 concedes a snapshot can be genuinely absent.

> **F4 | minor | §6.2, §6.6 | claim: the access-path table's "all paths fail → offline
> snapshot" rung is stated as if a snapshot is always available; §6.5's INSUFFICIENT band
> ("expired or unverifiable snapshot") implies the no-snapshot-at-all case is handled, but this
> is never stated for the case where a snapshot has never yet been written. | Required
> change: add "no snapshot exists" as an explicit precondition of INSUFFICIENT, distinct from
> "snapshot exists but expired," so a first-run failure and a seventh-day failure are both
> named cases rather than one being inferred.**

**Scenario (i) verdict: DEGRADED-OK, with a MAJOR detection/actionability gap.** Nothing
unsafe ships — the degrade trigger correctly fires and no brand content is fabricated. But
the operator's ability to fix the *actual* problem at 09:00 rests on diagnostic mechanisms
(F1, F3) the plan asserts but never specifies, and the one comparable credential risk in the
document (Meta Ad Library) got a proactive alarm and a runbook that this one — arguably more
consequential — did not.

---

## Scenario (ii) — run deadline hits with 2 media jobs pending; one later succeeds, one becomes submitted-unknown

**Trace.** Per-stage timeout / overall run ceiling approaches → **graceful wind-down**:
"stop starting new paid work, checkpoint everything in flight, package whatever is complete —
never a hard kill" (§8.7). At this instant, both pending jobs already have a **provider task
id** recorded (they are in the "polling" state per the state progression in §8.13: "submitted
→ polling → completed-pending-download → rehosted → done"). The run packages what is
complete and exits **completed-with-pending-media** (§8.8) or, if a cap tripped rather than a
timeout, a different class (see Scenario iv) — the plan doesn't actually give the
timeout-with-jobs-pending case its own distinct exit class; it is folded into
completed-with-pending-media regardless of *why* the run stopped submitting, which is
probably fine but is never stated as a deliberate choice.

Next run's **Phase 0**: "adopt any pending media jobs from a prior run and drain the download
queue ordered by nearest expiry, before anything new is submitted" (§9.2, §8.13). For job A,
the query resolves cleanly to success → re-hosted with checksum → marked done (§5.5). Good —
this path is concrete and well specified.

For job B, the scenario stipulates it becomes **submitted-unknown**. Here the plan
contradicts itself on what that state actually means and when it can arise.

**Gap 1 — definition mismatch.** §8.5 defines submitted-unknown narrowly: "a process death
**between committing the intent row and recording the returned task id** leaves a
submitted-unknown state." By this definition, job B — which already has a task id recorded
(it was "polling," not merely "submitted") — cannot become submitted-unknown from a clean
wind-down; it can only become submitted-unknown from a specific crash window that has already
passed for it. Yet §8.13's own state-progression line says a diversion "to failed, expired,
or submitted-unknown [is] possible **at any point before done**" — which implies a
job that already has a task id (was "polling") *can* still land in submitted-unknown, e.g. if
the resolve-by-query call itself times out or returns an ambiguous answer on the next run.
These two statements describe different triggering conditions for the same named state and
are never reconciled.

> **F5 | major | §8.5, §8.13 | claim: "submitted-unknown" is defined once (crash between
> intent-commit and task-id-write, §8.5) but used again as a general diversion possible "at
> any point before done" (§8.13) — including from an already-task-id-bearing "polling" job
> whose resolve-by-query itself fails to return a clean answer. The plan never states whether
> a second, distinct trigger condition exists (query timeout / query returns neither
> success-nor-failure) or whether this is meant to be the same case described twice. |
> Required change: name submitted-unknown's trigger conditions exhaustively (crash-before-task-id,
> AND unresolvable resolve-by-query on a known task id) as two named sub-cases with the same
> terminal handling, so the state machine in §8.13 and the mechanism description in §8.5
> agree.**

**Gap 2 — no terminal resolution path.** The plan is emphatic that submitted-unknown is
"never auto-resubmitted" (§5.6, §8.13, R-09) and is "reconciled via a balance-delta check."
But a balance-delta check only tells you *whether unexplained spend happened in aggregate* —
it does not resolve *this specific job* to a terminal state. If the provider's own
task-status endpoint never returns a clean answer for this task id (purged, rate-limited,
transient 5xx repeated across runs), what happens on run 3, run 10, run 30? Does the asset
slot's "one paid attempt chain" permanently occupy that identity, silently never completing
and never being retriable even by explicit human action? The plan states the rule that
prevents double-billing (no auto-resubmit) but never states the rule that eventually frees
the slot.

> **F6 | major | §5.6, §8.13, §8.5 | claim: "a named submitted-unknown state with no
> automatic resubmission" is stated as the safety property, but no give-up threshold, manual
> override affordance, or terminal-state assignment is ever specified for a submitted-unknown
> job that remains unresolvable across many runs. "One asset identity permits at most one paid
> attempt chain" (§8.5) reads as if this could be permanent. | Required change: define a
> bounded resolution window (e.g., N days or until the provider's own 14-day deletion window
> closes) after which an unresolved submitted-unknown job is declared a named terminal state
> ("lost — unexplained spend possibly incurred, no artifact"), surfaced to the operator with an
> explicit, human-gated "retry this asset slot" affordance — because §8.5's "one paid attempt
> chain" rule, taken literally and forever, means a permanently ambiguous provider response
> permanently strands that content slot.**

**Gap 3 — unreconciled tension with the owning research brief.** A2, the brief that owns
provider facts, recommends the opposite of the plan's absolute rule for exactly this
situation: "A task older than a timeout… is declared lost and **eligible for controlled
re-submission** under the spend rules" (A2 §2.6). The assembled plan instead states flatly
and repeatedly that submitted-unknown is never auto-resubmitted, with no inline
acknowledgment of overriding A2's own recommended recovery step — despite the plan's own
citation discipline promising that "where this plan and a single brief disagree, the plan
carries the synthesis's resolution **and says so inline**" (§0.4).

> **F7 | minor | §0.4, §5.6, §8.13; A2 §2.6 | claim: the plan's "never auto-resubmit" rule for
> submitted-unknown silently supersedes A2's own recommended "controlled re-submission after a
> timeout" without the inline acknowledgment §0.4 promises for exactly this kind of
> disagreement. | Required change: add one sentence at §8.13 stating that A2's
> controlled-resubmission recommendation was considered and rejected in favour of the stricter
> no-auto-resubmit rule, and why (the money-safety argument already exists — it just isn't
> connected to the specific brief it overrides).**

**Gap 4 — reconciliation math is underspecified.** The spend ledger records "expected cost"
(registry snapshot) and "observed cost" (balance delta), with "unexplained spend" as "a
first-class alarm that halts new submissions" (§5.6). While job B sits unresolved, does its
possibly-incurred cost count toward "expected"? If excluded, a real charge for job B would
show up as unexplained spend and could trip the circuit breaker on an otherwise-healthy run;
if included, the ledger is asserting a cost for a job whose outcome is explicitly unknown. The
plan states the alarm exists but not how the arithmetic treats an outstanding
submitted-unknown row.

> **F8 | major | §5.6, §8.6 | claim: "the ledger records both an expected cost… and an
> observed cost… and unexplained spend is a first-class alarm" — but the treatment of an
> unresolved submitted-unknown row's cost within that comparison (included as a provisional
> expected charge, or excluded until resolved) is never stated, and either choice changes when
> the circuit breaker fires. | Required change: specify that a submitted-unknown row
> contributes its full expected cost to the "expected" side of the reconciliation the moment it
> is written (worst-case assumption), so an actual charge never surprises the circuit breaker,
> and state this explicitly next to the reconciliation description.**

Finally, the "unexplained-spend tolerance" knob is named ("Tight," §10.4) but never given a
number or even a directional formula (percentage of run budget? absolute cents?) — unlike the
brand-fit floor, which at least gets a directional starting value (0.35).

> **F9 | minor | §10.4 | claim: "Unexplained-spend tolerance… Tight" is the only value given
> for a knob that gates a hard circuit breaker on money; every other consequential threshold in
> the plan gets at least a directional starting number. | Required change: give a directional
> starting value (e.g., "$0.05 or 10% of the run's expected spend, whichever is larger") with
> the same "calibration starting point, not an empirical finding" caveat used elsewhere.**

**Scenario (ii) verdict: SILENT on the recovery path.** The plan's forward path (job A
succeeds, adopted cleanly next run) is genuinely well designed. The backward path (job B,
permanently ambiguous) has no stated ending — a real gap given how central "no idempotency,
no dedup semantics" (fact-ledger row 7) is to this whole layer of the design.

---

## Scenario (iii) — the same topic trends four days running with rising engagement

**Setup.** This is the scenario the plan's own supporting research (B3) treats in the most
detail of any cross-day mechanic, with a named worked example ("a coding-agent
context-window debate trends on Hacker News day 1… resurfaces on X day 3… appears again on
Reddit day 4," B3 §6.2) and a concrete decision table:

| Trajectory | Prior-pack state | Outcome (per B3 §6.2) |
|---|---|---|
| Rising | Never generated | Normal candidate |
| Rising/sustained | Already generated | Resurgence **only if** new angle detected; tagged "revisit: new angle"; else suppressed |
| Declining | Never generated | Ranks normally, usually falls below threshold |
| Declining | Already generated | Suppress permanently |

**Gap — this rule is not in the architecture plan.** `ARCHITECTURE_PLAN.md` is described as
"the single canonical architecture and delivery plan" (title page) whose evidence base is
`SYNTHESIS.md`, with each figure "trac[ing] to a row there" (§0.3). But this is not a figure —
it is the entire control-flow rule for the exact risk this review mandate names. Searching the
plan's own text for the actual decision logic turns up only:

- §1.2 (Dedupe Index component): "Remembers topic cluster keys, first-seen and last-seen
  dates, **trajectory samples and prior-pack state** across a rolling lookback so yesterday's
  topic does not reappear as today's discovery."
- §2.8 flow diagram: "dedupe index consulted (**trajectory x prior-pack state**)."
- §12.1: digest carries "freshness and cross-day dedupe status (**what changed since a prior
  appearance**, per the topic cluster key)."

Every one of these *names the inputs* (trajectory, prior-pack state) and *promises an output*
("what changed") without ever stating the **rule that maps one to the other**. B3's actual
resurgence-vs-suppression table — the one piece of text in the whole research corpus that
answers "can four near-identical packs ever ship?" — is never carried into the plan, never
referenced by section number, and never reconciled with the "top-N cap applied after
filtering" language that appears instead (§2.8), which addresses volume-per-run, not
repetition-across-days.

> **F10 | blocker | §1.2, §2.7, §2.8, §8.5, §12.1 | claim: the dedupe index "remembers…
> trajectory samples and prior-pack state" and is "consulted" during ranking, and the digest
> shows "what changed since a prior appearance" — but the actual decision rule (when a
> rising-and-already-generated topic resurfaces as a tagged "revisit" versus is suppressed;
> when a declining-and-already-generated topic is suppressed permanently) is never stated
> anywhere in `ARCHITECTURE_PLAN.md`, even though the owning research brief (B3 §6.2) states it
> in full with a worked example matching this exact scenario. Without this rule stated as
> canonical plan text, an implementer has two equally plausible readings — blanket
> cross-day suppression by cluster key (which would silently kill legitimate follow-up
> coverage of a genuinely developing story, undermining the launch-hype/evergreen-pain
> centre-of-gravity the ranking design depends on, §2.7) or blanket re-generation every time the
> topic re-ranks (which is exactly the "four near-identical packs" failure this scenario
> tests for) — and the plan currently authorizes neither explicitly, meaning either could get
> built. | Required change: import B3 §6.2's trajectory × prior-pack-state table into §2.7 or
> §2.8 verbatim as canonical rule text (not merely cited), name which stage computes "is there a
> genuinely new angle" (an LLM call — is this the bounded self-critique node named in §1.5?),
> and state its cost and where it is checkpointed.**

Even if this rule were imported, two further problems remain:

The B3 table's "prior-pack state" values include **published**, which this architecture
cannot observe: the system never publishes (§7, §11.1), Postiz drafts are created by the
system but turned live only by a human inside Postiz's own interface, and outcome capture
back into the system is optional, off by default, and manual ("Pack upload enablement… Off,"
§10.4; Phase 7's "outcome capture for published assets" is "a deliberate, low-friction
operator input path," §17 Phase 7 — i.e., the operator has to type it back in, and nothing
requires them to).

> **F11 | major | §7, §11.1, §12.6, §17 Phase 7 | claim: B3's decision matrix (the only
> stated version of the resurgence rule, and the one F10 asks to be imported) depends on
> distinguishing "already generated" from "already published," but this architecture has no
> mechanism to know whether a prior pack's asset was ever actually published — that fact lives
> entirely inside Postiz and the operator's own head, and feeds back only through an optional,
> off-by-default, manual step. | Required change: either collapse the granularity to what is
> actually observable (never-generated / drafted-or-approved / rejected), or make outcome
> capture a required rather than optional input before the resurgence rule can use
> "published" as a distinct state.**

And the digest's own promised "what changed since a prior appearance" content (§12.1) has no
stated owner: which stage computes it, at what point in the pipeline, at what cost, and
whether it is the same LLM call B3 describes ("LLM judgment: 'what changed since last
time?'") or a separate one.

> **F12 | major | §12.1, §1.5, §2.7 | claim: the digest "carries… freshness and cross-day
> dedupe status (what changed since a prior appearance…)" as a stated content item, but no
> section names the stage, the model call, or the cost that produces this sentence — it is
> promised as an artifact with no promised producer. | Required change: name the producing
> stage (most likely ranking, per §1.5's allowance for one bounded self-critique node there)
> explicitly, and add it to §2.7's per-candidate scorecard fields and to the ranking knob
> roster in §10.2.**

**Scenario (iii) verdict: SILENT — and the specific question this scenario mandate asks
("can four near-identical packs ever ship?") is genuinely unanswerable from the plan text as
written.** This is the single most consequential gap in this review, because it is a control
this exact document was supposed to specify (RA-1's "cron idempotency/dedupe… not
hand-waved") and the specification exists in the evidence base but was not carried forward.

---

## Scenario (iv) — budget cap trips mid-pack, 3 of 6 destinations' media done, identical-mix cs+en

**Trace.** The cost gate runs "before submission, never after" (§4.6), checked "at
submission, against the remaining budget" (§8.11). Mid-pack cap-hit is a named, deliberate
outcome: "if the cap trips after three of six planned destinations are generated, **the
pipeline ships the partial pack, clearly marked incomplete**, with the three completed
destinations reviewable and the other three explicitly flagged as not-generated-due-to-budget"
(§8.11).

**Gap — this example contradicts the plan's own resolved counting model.** §8.11's own
worked description is phrased entirely in **destination** units ("three of six planned
destinations"). But §0.2's "six things resolved at assembly," item 3, states explicitly:
"**Media-bearing caps count masters per language, not destination derivatives**, because one
9:16 master legitimately serves TikTok, Reels and Shorts through layered re-composition." §3.2
restates this as the operative rule: "the cap counts masters produced, and the derivative
count is unbounded because a derivative costs a re-render, not a generation" — and derivative
rendering is described elsewhere as "$0 marginal" cost (§4.4). Under this model, once a video
master is generated, **all five video-bearing destinations it feeds (LinkedIn native video,
Instagram Reel, TikTok, YouTube Shorts, Facebook Reel) become available together**, near-
instantly and at no further submission cost — there is no scenario in which a dollar-based
cap trips **between** two of those five destinations, because the money was already spent
(or not) at the master-generation step, before any per-destination re-composition happens.
A literal "3 of 6 destinations partially done" mid-pack state is therefore not something the
masters-counting model can actually produce; it is a leftover from before that model was
adopted, and the two sections were never reconciled.

> **F13 | blocker | §8.11 vs §0.2 item 3, §3.2, §10.4 | claim: §8.11's canonical illustration
> of mid-pack cap-hit behaviour ("three of six planned destinations") is written in a counting
> unit (per-destination) that the plan's own later, definitive resolution ("cap counts masters
> produced, not destination derivatives," §3.2) makes architecturally implausible, since five
> of the six destinations in the identical-mix matrix are free, near-simultaneous derivatives
> of one shared master. The two sections directly contradict each other on the unit at which
> "partial completion" can even occur, and this is precisely the risk RA-6 in `RISK_LOG.md`
> names as needing to be "concrete… not hand-waved." | Required change: rewrite §8.11's
> worked example in masters-and-languages units (e.g., "if the cap trips after the English
> video master and English slide-art master complete but before the Czech pair starts, the
> pack ships with English's five derivative destinations reviewable and Czech's explicitly
> flagged not-generated-due-to-budget") so the illustration matches the counting rule the rest
> of the document commits to.**

A related, unresolved interaction: the **masters-per-language-per-run cap is a count** ("one
to two per language," §10.4), while the **cost gate is a dollar figure** checked "at
submission" (§8.11). Given the plan's own economics — English's default recipe buys
generative clips at roughly $0.30–$1.25 per clip while Czech's CS-B recipe "buys no clips at
all" (§3.1, §5.4) — a shared per-run dollar cap could plausibly exhaust itself on English
alone while Czech's cheap masters are still within their count allowance, or vice versa. The
plan never states which limit is checked first, or how a count-based stop and a dollar-based
stop are reconciled when they would give different answers for the two languages in the
identical run.

> **F14 | major | §8.11, §5.4, §10.4 | claim: two independent per-run limits exist — a
> masters-per-language count cap and a dollar cost-gate cap — and both apply to the same
> media-generation stage in the same run, but no ordering or precedence rule is given for the
> (realistic, given the stated cost asymmetry between languages) case where they would produce
> different stop points. | Required change: state explicitly that the dollar cap is checked
> per submission regardless of the count cap's remaining allowance (or the reverse), and walk
> one worked case where English and Czech diverge under the two caps, the way Appendix A walks
> the happy path.**

**Gap — no stated recovery path for the deliberately-incomplete pack.** Once a pack ships
"partial… clearly marked incomplete" (§8.11), how are the missing masters ever completed? The
knob list names a "regenerate-media-only" stage-enablement flag (§10.4) as a plausible
mechanism, but §8.11, §15 (R-12) and Appendix A never connect the two: nowhere does the plan
state "to complete a budget-capped pack, the operator invokes a regenerate-media-only run
against this run id." It is equally unclear whether the **next scheduled pack-production run**
would independently re-rank the same topic (subject to whatever cross-day dedupe rule
eventually gets written per F10) and regenerate it fresh, potentially duplicating the
already-approved copy/spin work from the capped pack, or whether the capped pack simply sits
forever unless the operator manually intervenes.

> **F15 | major | §8.11, §10.4, §17 | claim: the "regenerate-media-only" stage-enablement
> flag is named as a knob but never wired to the mid-pack cap-hit outcome as its designed
> recovery mechanism, and the interaction with the next scheduled run's independent topic
> ranking (which might re-rank and re-spin the same still-current topic from scratch) is
> never addressed. | Required change: state explicitly, next to §8.11's mid-pack cap-hit
> description, that a capped pack's missing masters are completed only via an explicit
> regenerate-media-only invocation referencing the run id, and that the topic is marked in the
> dedupe index as "already generated (capped)" so the next scheduled run does not silently
> re-spin and re-copy it from zero.**

Finally, Appendix A's own worked arithmetic for "masters produced" does not add up on its own
terms, which matters because Appendix A is explicitly offered as the proof that "the seams
between sections actually join" (Appendix A preamble). It states: "**Masters produced:
two** — one 9:16 video master per language — plus one 4:5 slide-art set per language" (§A.5).
One 9:16 master per language is two items (English, Czech); "plus" a 4:5 slide-art set per
language is two more — four items total, not two, unless the slide-art sets are silently
being excluded from what the cap counts (in which case the plan needs to say the cap is
video-master-only, since §3.2's prose ("media-bearing assets… counted as masters") does not
itself restrict the term to video).

> **F16 | major | §3.2, §10.4, Appendix A.5 | claim: it is never stated whether the
> "masters per language per run" cap applies to video masters only or to all media-bearing
> masters including 4:5 image/carousel sets, and the plan's own flagship worked example
> contradicts itself arithmetically on this exact point ("Masters produced: two" followed by an
> enumeration of four items). A secondary consequence, never stated plainly: under the "~5
> topics per run, 1–2 masters per language per run" pairing (OD-8), the overwhelming majority
> of ranked topics in every single pack — 3 to 4 of 5 — receive **no rendered media of any
> kind**, by design, every run, which is a legitimate economic choice but is never surfaced as
> starkly as this to the operator anywhere the caps are introduced. | Required change: state
> explicitly whether the masters cap counts video masters only or all media-bearing masters;
> fix the Appendix A.5 arithmetic to match; and add one sentence near OD-8/§8.11 stating plainly
> that most ranked topics in a normal pack ship as text-plus-plan-only by design, so this is
> read as an intentional trade-off rather than discovered as a surprise.**

**Scenario (iv) verdict: CONTRADICTS.** The mechanism the plan actually resolved to (masters,
not destinations) and the mechanism its own canonical mid-pack cap-hit illustration describes
(destinations) are two different models, and RA-6 explicitly asked for this to be concrete.

---

## Scenario (v) — human rejects one pack's video only, keeps the copy, requests regeneration with feedback

**Trace.** Rejection is granular and reason-coded, recorded in the review-decision store at
the asset-slot level ("reject just the video and keep the copy," §3.5, §11.4, §12.4). The
**immediate loop** regenerates "within the current pack, with the specific feedback fed back
as corrective context, subject to the same bounded regenerate cap and cost circuit breaker as
any other regenerate (§14)" (§12.4).

Appendix A's worked instance of exactly this scenario is concrete and appealing: the operator
rejects "the English 9:16 video master" with reason code "motion integrity: limb warp at
0:05" and free-text "second clip only; the hook and the close are fine" (§A.9). The
regeneration is then costed as "one workhorse-route call, $0.30" — i.e., **one clip out of
three**, reusing "the same already-approved keyframe" (§A.9) — not a full re-shoot of the
master (which the same appendix priced at "$0.90" for three clips, §A.6).

**Gap — the appendix shows a granularity the normative sections never commit to.** Every
gate in §14 that defines a "regenerate cap" defines it **per artifact**: "a hard, configurable
regenerate cap… counted per artifact" (§14.2, voice gate); the claim gate's allowance is "per
pack, not per asset" (§14.3, §6.7); the spin gate's ladder operates on "the asset" as a whole
(§14.1, §6.10). Review-decision granularity itself is stated at the **asset-type** level
("reject the video and keep the copy" — video-as-a-whole versus copy-as-a-whole, §3.5,
§11.4), never at the sub-asset (one shot within a multi-shot video) level. Nowhere in the
normative text does the plan state that a human's free-text note can be mapped — automatically,
mechanically, or even by a described manual step — onto a specific shot index within the shot
list (§4.2's "shot list = N independent, self-contained prompts, each row naming which
approved keyframe it animates" makes this *architecturally possible*, but "possible" is not
the same as "specified"). Appendix A's own preamble concedes its numbers are "illustrative
rather than observed" — which means the one place this economically important behaviour is
shown is explicitly not binding.

> **F17 | major | §12.4, §14.1–§14.3, §3.5, §11.4, §4.2, Appendix A.9 | claim: the only place
> the plan shows shot-level (not whole-artifact) regeneration in response to a human's
> free-text rejection reason is the non-normative Appendix A worked example ("second clip
> only… $0.30" for one of three clips); every normative statement about regenerate caps defines
> the unit as "per artifact" or "per pack," and review-decision granularity is stated at the
> asset-type level, not the sub-asset level. There is no stated mechanism (structured field,
> parsed free text, or manual operator action) that would actually route "second clip only" to
> regenerating just that clip rather than the whole master. | Required change: state explicitly,
> in §12.4 or §4.2, whether the decision file/console command exposes a structured field for
> "which shot/segment failed" (recommended, given the shot list is already segment-addressable),
> or whether the free-text note is fed whole to a full-master regeneration (in which case
> Appendix A's $0.30 figure is wrong and should be corrected to the full re-shoot cost).**

**Gap — no bounded ladder if the regeneration also fails.** This is the sharpest gap in this
scenario. Every other gate in the system has an explicit multi-step enforcement ladder ending
in a defined terminal state: the spin gate (fail → regenerate → downgrade to value-only →
drop, §14.1); the claim gate (block → regenerate → downgrade repair → drop, §14.3); the voice
gate (lexicon → structural → judge → bounded regenerate → **escalate to review**, terminal,
§14.2). The **asset QA rubric** — the machine gate that actually catches things like "limb
warp at 0:05" — explicitly has **no such ladder**: Appendix A's own table states plainly,
"Not a refusal, so the refusal ladder does not apply; the asset **enters the pack flagged for
human decision** rather than being silently retried" (§A.7). So the only trigger for a
video-QA-driven regeneration is a **human rejection**, and the human-rejection "immediate
loop" is a single pass with no described behaviour for a second failure. If the regenerated
clip introduces a *new* defect, or the *same* defect recurs, or the human simply rejects it
again for a different reason — what happens? Does it loop indefinitely (bounded only by the
blunt per-run/day/month dollar cap, not by any stated per-asset ceiling)? Does it degrade to
plan-only (as the *refusal* ladder would, but this is explicitly stated not to be a refusal)?
The plan never says. Given W2-10's own finding that exactly this class of unattended
cost-spiral ("a too-strict judge… pays… for zero quality gain") is a named, serious risk
(R-10, R-21), the absence of an equivalent circuit breaker for the *human-driven* QA-rejection
loop is a real, not theoretical, gap — a busy or perfectionist operator rejecting the same
video three or four times across three or four sessions has no stated point at which the
system says "stop, downgrade, or escalate" rather than quietly accepting another paid
regeneration each time.

> **F18 | blocker | §4.2, §4.9, §14.2, §12.4, Appendix A.7 | claim: the asset QA rubric
> explicitly does not use the refusal ladder's bounded-attempt-then-plan-only terminal state
> ("not a refusal… flagged for human decision," §A.7), and the human-rejection-driven
> "immediate loop" (§12.4) that is the only path back from a QA-flagged defect has no stated
> cap, downgrade rule, or escalation terminal state of its own — unlike every other gate in the
> document (spin, voice, claim), each of which names an explicit bounded ladder ending in a
> defined terminal state. A repeatedly-failing video asset can therefore be regenerated an
> unbounded number of times, one human rejection at a time, with no architectural circuit
> breaker other than the same blunt dollar caps W2-10 already showed are insufficient on their
> own for this exact failure shape. | Required change: give the human-rejection regenerate
> loop its own named cap (e.g., two regenerations per asset slot per pack) and a terminal state
> on exhaustion (ship the last-generated version flagged "did not clear QA after N attempts,"
> mirroring the voice gate's "escalate to review" terminal, §14.2, Layer 5) — do not leave this
> as the one gate in the document without a stated ending.**

A smaller, related terminology gap: "regenerate cap," "per-pack regenerate allowance," and
"the same bounded regenerate cap… as any other regenerate" are used across at least three
distinct mechanisms (claim-gate pack-level budget, voice-gate per-artifact cap, and the
human-rejection immediate loop) without ever stating whether these share one counter or are
independent counters.

> **F19 | minor | §6.7, §14.2, §14.3, §12.4 | claim: at least three different regeneration
> budgets in the document are referred to with overlapping language ("regenerate cap,"
> "per-pack regenerate allowance") without stating whether they are the same counter or
> independent ones — in particular §12.4's claim that the immediate loop is "subject to the
> same bounded regenerate cap… as any other regenerate" does not say *which* of the (at least
> two, differently-scoped) caps named elsewhere it means. | Required change: give each
> regeneration budget a distinct name (e.g., claim-retry-budget, voice-regenerate-cap,
> QA-rejection-cap) and state explicitly that they are independent counters, or that they share
> a pool, whichever is intended.**

**Scenario (v) verdict: DANGEROUS on the failure path, SAFE on the happy path.** The
happy-path behaviour (reuse the keyframe, regenerate the flagged clip cheaply) is exactly
right *if* it is actually what gets built — but it is only ever shown, never specified, and
the one case this scenario explicitly asks about (regeneration also fails the judge) has no
answer in the document at all.

---

## Invented scenario A — Task Scheduler fires while a long interactive run is still in progress

**Trace.** §8.3 states overlap policy unconditionally: "If the run-lock is already held by a
live run, a new invocation does not queue and does not kill the running instance — it logs
and notifies a distinct skipped-overlap outcome." §8.1 frames this as a property of "the one
application": "Whether it is invoked by an operator at the keyboard or by an OS scheduler…
changes nothing about which code executes." Taken together, these should mean a manual
interactive session and a scheduled trigger are symmetric with respect to the lock.

**Gap.** §9.2 (the unattended walkthrough) explicitly narrates lock acquisition: "run
identity + lock acquired, or the run exits immediately as skipped-overlap if one is already
held." §9.1 (the interactive walkthrough) **never mentions the lock at all** — it goes
straight from "theme load (operator selects theme, mode…)" to "secrets load" to "brand-truth
resolution" with no lock-acquisition step narrated anywhere in the flow. Given §12.5's
static-file review model (the pipeline process itself exits after packaging/notification;
review happens later, asynchronously, against files on disk, with no process running during
review) — an interactive run that is "long" in the sense of "the operator is slowly reviewing
the digest" holds no lock at all by then, which is fine and correctly implied. But an
interactive run that is "long" in the sense of "media generation is still polling and the
operator chose to wait synchronously, or stepped away and intends to return" (§9.1: "the
operator may wait synchronously or return to the pack later") is genuinely ambiguous about
whether the *process* — and therefore the lock — is still alive during that wait. If the
operator's console session is closed (terminal closed, laptop put to sleep) during this
window without the process being explicitly backgrounded, does the process (and its lock)
survive? The plan never says how an "interactive" console process is meant to keep running
unattended for the "return to the pack later" case, since there is explicitly no daemon, no
service and no session-persistence layer in this design (§12.5, §8.1).

> **F20 | major | §9.1, §9.2, §8.1, §8.3, §12.5 | claim: the run-lock and skip-on-overlap
> policy is asserted as a property of "the one application" regardless of invocation mode, and
> is explicitly narrated in the unattended walkthrough (§9.2), but is never narrated in the
> interactive walkthrough (§9.1) at all. Separately, §9.1 permits the operator to "return to
> the pack later" while generation continues asynchronously, but no section states what keeps
> the interactive process (and therefore its lock) alive if the operator's console session
> itself ends, given the design has no background service or daemon. | Required change: add an
> explicit lock-acquisition step to §9.1's walkthrough matching §9.2's, and state plainly
> whether "return to the pack later" requires the operator to leave the console session open
> (in which case say so, since it is an operational constraint the operator needs to know) or
> whether the process is expected to be explicitly backgrounded/detached by the operator (in
> which case name the mechanism, since none exists elsewhere in the document).**

**Verdict: AMBIGUOUS.** The stated policy (skip-on-overlap, symmetric across invocation
modes) is almost certainly the intended behaviour, but the interactive walkthrough's silence
on lock acquisition, combined with the total absence of a background-execution story for "the
operator steps away mid-run," leaves a real reader unable to confirm from the text that a
scheduled trigger during a long manual session is actually caught.

---

## Invented scenario B — Virlo (or any MCP source) returns syntactically valid but stale/garbage data, silently

**Setup.** The trend-intelligence vendor's programmatic access is already flagged as
uncertain at the purchased tier (W2-17, R-04), and the Bluesky trending-topics endpoint is
described as "explicitly unspecced and unstable" (§2.3). Suppose one of these sources does
not fail outright — it returns a well-formed response, but the data is stale (yesterday's
trending list served again with today's timestamp due to a caching bug on the vendor's side)
or partially garbage (a truncated/malformed field that still parses).

**Trace.** Every detection mechanism the plan describes for source health is keyed to
**absence**: the per-source circuit breaker "trips on consecutive **failures**" (§15 R-01);
"a source producing **zero signals** for a full cadence period is itself an alarm" (§2.2);
degraded-source banners fire when a source "returned nothing" (Appendix A.2). Nothing in
§2.2, §2.7, §2.8 or §15 describes a check on the **content** of a non-empty, non-erroring
response — there is no staleness fingerprint (e.g., "this payload is byte-identical or
near-identical to yesterday's"), no schema/sanity validation beyond "collected text is
carried as quoted data" (which guards against prompt injection, not data quality), and the
confidence-ceiling treatment for "ranked/presence-only" evidence (§2.7) mitigates *how much
weight* a shaky source gets, not *whether its data is actually current*. A stale-but-present
payload would sail through as a normal, non-degraded, non-banner-worthy signal — its
timestamp would read as fresh (it's today's fetch, even though the underlying content is
old), so the freshness scorer (§2.7) would have no reason to discount it either.

> **F21 | major | §2.2, §2.7, §2.8, §15 (R-01, R-03, R-04) | claim: every stated detection
> mechanism for source degradation (circuit breaker, zero-signal alarm, confidence ceiling on
> ranked/presence-only evidence) detects *absence* of data or *structural* unreliability of the
> evidence class — none detects *presence of wrong data* (stale-but-freshly-timestamped,
> partially malformed, or vendor-side caching bugs), which is a distinct and realistic failure
> mode for exactly the two named sources (the trend vendor, W2-17; Bluesky's trending endpoint,
> §2.3) the plan itself flags as least well-specified. | Required change: add a cheap
> content-fingerprint check per MCP source (e.g., hash of the returned item set, compared
> against the last N pulls) that flags "identical or near-identical payload across pulls" as a
> distinct degraded-source reason, separate from and in addition to the zero-signal alarm.**

**Verdict: SILENT.** This is a real gap given the plan names both candidate sources as
already shaky in exactly this way, and the entire ranking layer's freshness and corroboration
math implicitly trusts that a non-empty, non-erroring payload is telling the truth about being
current.

---

## Invented scenario C — the weekly Reddit curated-inbox ritual lapses for three weeks running

**Trace.** Week 1 miss: staleness flag set, pack labelled "pain axis: operator-fed" and
stale, no escalation yet (one miss, §2.2, §8.12). Week 2 miss: "two consecutive misses
escalate notification prominence rather than repeating an identical low-signal message"
(W2-01, §8.12) — escalation fires, correctly.

**Gap.** Week 3 miss: what happens? The only counter named anywhere in the document is "two
consecutive misses" (§2.2, §8.12, §10.2: "Curated-inbox staleness threshold and escalation
count… escalate at two consecutive misses"). There is exactly **one** escalation tier defined
— the mechanism goes from "normal staleness banner" to "escalated" once, and nothing in
§8.12's "anti-flap principle generalizes: two consecutive identical degrades of any kind
escalate rather than repeat" describes what a **third**, **fourth**, or **tenth** consecutive
identical degrade does. Read literally, the notification at week 3 is identical in prominence
to week 2's — which is precisely the "repeating an identical low-signal message" failure the
escalation mechanism exists to prevent, just occurring one rung higher up the prominence
scale. Theme-readiness validation, the other place a systemic problem like this could in
principle be caught, is a gate "the scheduler refuses to bypass" only at scheduling time
(§13.2) — it is not re-run continuously during ongoing scheduled operation, so a ritual that
lapses well after the theme was already approved for scheduling produces no readiness
failure, only the one-time notification escalation described above.

> **F22 | minor | §2.2, §8.12, §10.2, §13.2 | claim: the curated-inbox staleness escalation
> mechanism defines exactly one escalation tier ("two consecutive misses"), with no further
> escalation, hard-stop, or automatic degraded-axis-suppression defined for continued misses
> beyond that, and theme-readiness validation (the only other structural check available) runs
> only at scheduling time, not continuously — so a three-week, three-month, or indefinite
> lapse produces the identical notification prominence as the second week, forever. |
> Required change: define at least one further escalation tier for staleness beyond a
> configurable further-miss count (e.g., a distinct "axis has been stale for over a month" banner
> that differs in wording/urgency from the two-miss escalation, or an explicit rule that the
> pain-axis label downgrades from "stale" to "abandoned" after a stated number of consecutive
> misses), so the mechanism does not itself become the thing it was designed to prevent.**

**Verdict: DEGRADED-OK, but the degrade signal itself goes stale.** No unsafe content ships
(the pack is honestly labelled throughout), but the operator's alerting has a ceiling that the
document never states is a ceiling.

---

## Invented scenario D — disk fills up mid-download during the expiry-ordered drain, with paid jobs mid-flight

**Trace.** A run begins after a period where several prior runs' media jobs are still
pending. Phase 0's stated job is to "adopt any pending media jobs from a prior run and drain
the download queue ordered by nearest expiry, **before anything new is submitted**" (§9.2,
§8.13) — this drain can legitimately be a backlog of several runs' worth of large video files,
larger than a single run's normal download volume. The proactive low-disk-space check runs
"at run start and again before the media stage specifically" (§8.10) — i.e., **two
point-in-time checks**, not a continuous guard during the drain loop itself. Suppose the check
at run start passes (disk has "enough" free space by the configured threshold for what a
*normal* run needs), but the actual backlog being drained this run is unusually large (e.g.,
several prior runs' pending jobs accumulated because the operator was travelling), and disk
fills partway through the drain — after some files have been re-hosted successfully, before
others have.

**Gap.** §8.10 classifies disk-full as "a hard-failure class, not a per-unit soft failure,
because it risks corrupting an in-progress ledger write; the correct behaviour is a proactive
low-disk-space check… failing closed before further writes once a safe threshold is crossed."
This describes disk-full as something the *proactive check* is meant to prevent from ever
being reached mid-operation — but the check is explicitly only run at two fixed points, not
continuously during a long, variable-length drain loop. If the drain loop itself exhausts
disk **after** the pre-check passed, the stated response ("hard-failure… failing closed
before further writes") would abort the run **mid-drain**, leaving some already-completed
(provider-side) media un-downloaded. Those jobs are now racing the provider's fixed 14-day
deletion window and shorter result-URL expiry (fact-ledger row 6) with **no guaranteed next
attempt** before that window closes, if the underlying disk-space problem (an operator
action: free up space, move the run folder, add storage) is not resolved before the next
scheduled run. This is exactly the "crash discards paid work" failure the entire checkpoint
design exists to prevent (§0.1, §8.7) — except here it is not a crash, it is the *correct,
designed* hard-failure response to disk pressure, colliding with the *correct, designed*
expiry-ordered drain-first rule, and the plan never reconciles what happens when the two
collide.

> **F23 | blocker | §8.10, §8.13, §5.5, §0.1 | claim: the low-disk-space check is a
> point-in-time gate run only "at run start and again before the media stage," not a
> continuous guard during the (potentially large, backlog-dependent) expiry-ordered download
> drain that Phase 0 requires to run to completion "before anything new is submitted." If disk
> fills mid-drain despite both checks having passed, the stated hard-failure response ("failing
> closed before further writes") would abort the run before the drain finishes, leaving
> already-generated, already-paid-for media undownloaded and now exposed to the provider's
> 14-day deletion window with no guaranteed next attempt if the disk issue persists past that
> window — directly contradicting the plan's own prime directive that a crash or hard stop
> "must not discard paid work" (§0.1). | Required change: make the low-disk check a running
> guard evaluated before each individual download within the drain loop (not merely twice per
> run), and, on a mid-drain disk-full event, prioritise completing re-hosting of the
> nearest-to-expiry remaining jobs (even if it means refusing only new submissions rather than
> aborting the drain itself) so the specific already-paid-for jobs closest to permanent loss are
> protected first.**

**Verdict: DANGEROUS.** Two individually well-reasoned, explicitly designed safety mechanisms
(proactive disk-full hard-failure; expiry-ordered drain-first) can collide in a way that
produces exactly the outcome both were built to prevent, and the document never notices the
collision.

---

## Summary — findings by severity

| # | Severity | Section(s) | One-line gap |
|---|---|---|---|
| F1 | Major | §6.2, §6.6, §8.10 | No error-class distinction (auth-revoked vs transient) in brand-truth pull retry logic |
| F2 | Minor | §11.3, §6.2 | "Absent or unreadable" secret trigger vs brand-truth degrade path boundary undrawn |
| F3 | Major | §2.3 (R-05), §6.2, §17 | No proactive alarm/runbook for Notion token health, unlike Meta Ad Library's |
| F4 | Minor | §6.2, §6.6 | No-offline-snapshot-at-all case not explicitly named |
| F5 | Major | §8.5, §8.13 | "submitted-unknown" defined narrowly once, used generally elsewhere — trigger conditions don't match |
| F6 | Major | §5.6, §8.13, §8.5 | No terminal give-up/resolution path for a permanently unresolvable submitted-unknown job |
| F7 | Minor | §0.4, §5.6, §8.13; A2 §2.6 | Plan silently overrides A2's "controlled re-submission" recommendation without the inline note §0.4 promises |
| F8 | Major | §5.6, §8.6 | Unresolved submitted-unknown job's cost treatment in balance-delta reconciliation unspecified |
| F9 | Minor | §10.4 | "Unexplained-spend tolerance: Tight" has no directional number |
| F10 | Blocker | §1.2, §2.7, §2.8, §8.5, §12.1 | Cross-day resurgence-vs-suppression decision rule (B3 §6.2) never carried into the plan |
| F11 | Major | §7, §11.1, §12.6, §17 | "Prior-pack state = published" is unobservable by this architecture |
| F12 | Major | §12.1, §1.5, §2.7 | Digest's "what changed since a prior appearance" has no stated producing stage or cost |
| F13 | Blocker | §8.11 vs §0.2/§3.2 | Mid-pack cap-hit example uses "destinations" units; the resolved model counts "masters" — architecturally incompatible |
| F14 | Major | §8.11, §5.4, §10.4 | Count-cap (masters) vs dollar-cap (cost gate) precedence unspecified when they diverge by language |
| F15 | Major | §8.11, §10.4, §17 | No stated link between mid-pack cap-hit and the "regenerate-media-only" recovery mechanism |
| F16 | Major | §3.2, §10.4, Appendix A.5 | Masters-cap scope (video-only vs all media) unstated; Appendix A's own arithmetic (2 vs 4) doesn't add up |
| F17 | Major | §12.4, §14, §3.5, §4.2, App. A.9 | Shot-level regeneration shown only in a non-normative appendix, never stated as a rule |
| F18 | Blocker | §4.2, §4.9, §14.2, §12.4, App. A.7 | No bounded ladder/terminal state when a human-rejection-driven video regeneration also fails |
| F19 | Minor | §6.7, §14.2, §14.3, §12.4 | "Regenerate cap" terminology overloaded across ≥3 distinct, unreconciled budgets |
| F20 | Major | §9.1, §9.2, §8.1, §8.3, §12.5 | Interactive walkthrough never confirms lock acquisition; no background-execution story for "return later" |
| F21 | Major | §2.2, §2.7, §2.8, §15 | No detection mechanism for stale-but-present/garbage source data, only for absence |
| F22 | Minor | §2.2, §8.12, §10.2, §13.2 | Staleness escalation has exactly one tier; no further escalation for prolonged lapses |
| F23 | Blocker | §8.10, §8.13, §5.5, §0.1 | Point-in-time disk-check vs continuous expiry-drain loop can collide, risking exactly the "discard paid work" outcome the design exists to prevent |

Totals: **4 blocker, 13 major, 6 minor** (23 findings).

---

## Scenario verdicts

| Scenario | Verdict |
|---|---|
| (i) Notion token revoked overnight | DEGRADED-OK, with a major detection/actionability gap (F1–F4) |
| (ii) Two media jobs pending at deadline, one submitted-unknown | SILENT on the recovery path (F5–F9) |
| (iii) Same topic trends four days running | SILENT — the mandate's own question ("can four near-identical packs ship?") is unanswerable from the text (F10–F12) |
| (iv) Budget cap trips mid-pack, 3 of 6 destinations | CONTRADICTS — the canonical mid-pack illustration and the resolved counting model disagree (F13–F16) |
| (v) Video-only rejection, regenerate, regenerate also fails | DANGEROUS on the failure path; SAFE on the (unspecified) happy path (F17–F19) |
| (A) Scheduler overlap during a long manual run | AMBIGUOUS (F20) |
| (B) Trend vendor returns stale/garbage data silently | SILENT (F21) |
| (C) Reddit ritual lapses for three-plus weeks | DEGRADED-OK, but the alarm itself has a ceiling (F22) |
| (D) Disk fills mid-drain with paid jobs mid-flight | DANGEROUS (F23) |

## Overall verdict

**Reject the following sections for revision before this plan is build-ready**: §2.7/§2.8's
cross-day dedupe rule (F10 — the single most consequential gap found, since a mandated review
scenario is literally unanswerable from the text); §8.11's mid-pack cap-hit illustration
(F13, self-contradicts the plan's own masters-counting resolution); the asset-QA/human-
rejection regeneration path in §4.2/§14.2/§12.4 (F18, the only gate in the document with no
terminal state); and the interaction between §8.10's disk-full hard-failure and §8.13's
expiry-ordered drain (F23, two correct mechanisms that can jointly produce the one outcome the
whole design exists to prevent). Everything else in the document that this review touched —
brand-truth degrade mechanics, the async job model's forward path, the granular rejection
model's happy path, the overlap and staleness-escalation mechanisms — is sound in direction
and only needs the sharpening the major/minor findings above describe. None of the four
blockers requires a redesign; each requires the plan to finish a decision it has already
started (the rule exists in B3 for F10; the counting model exists in §3.2 for F13; the ladder
pattern exists three times over in §14 for F18; the drain-first and disk-check rules both
already exist for F23) and state it where the scenario actually needs it.
