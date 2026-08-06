# A3 — Legitimate emptiability of F-B, F-C, F-E, and the safe default for F-F

*Design-phase amendment to `docs/architecture/ARCHITECTURE_PLAN.md` · Amendment A, task A3 · closes defect **P-1** · drafted 2026-08-06*
*Status: plan only. No code is written by this document; its output is a set of prose edits to the Stage-4 architecture, listed in §9.*

**Binding source, not re-decided here.** The external-verifier substitution floor and the negative-capability requirement are stated in full at `docs/plans/PLAYBOOK_LAYER/00_MASTERPLAN.md` §4a (ruling C-4). This document restates that ruling for completeness and applies it as architecture; it does not soften, widen or reinterpret it.

**Scope.** This document touches exactly four fact classes — F-B, F-C, F-E, F-F — and their two consequences at the confidence-band gate and at theme-readiness validation. It does not design the new fact classes F-O through F-W (Amendment B), does not design price-handling inversion (Amendment B, informing F-F's default only by analogy), and contains nothing about playbooks, playbook selection, vertical packs, or the playbook layer as a mechanism. Where a source document keys a rule to a vertical or a playbook, this document restates the engine-floor behaviour that is true today and names the vertical-specific extension as deferred.

**Behaviour-preservation invariant.** Theme #1 has a populated offer catalogue: F-B, F-C and F-E all resolve to values, never to the empty state this document defines rules for, and F-F's price values are populated, so the F-F safe default never fires for it either. Nothing in this document changes what theme #1 produces. Every rule below is additive over the case theme #1 already exercises.

---

## 1. The defect, stated precisely, at both bite points

**P-1**, in one sentence: a tenant with no product cannot run, because §6.3 marks F-B (offer catalogue), F-C (capability statements) and F-E (CTA set) blocking and **"may not be legitimately empty."** F-F (pricing policy) is a separate case, addressed at §5 below. The defect has two bite points, and they fail differently, so they need separate fixes.

| Bite point | Mechanism | Failure mode |
|---|---|---|
| **§6.5, Step 1 of the confidence-band computation** | Step 1 requires every blocking class to be "resolved or legitimately resolved-empty." F-B/F-C/F-E have no legitimate-empty state today, so a genuinely offer-less tenant leaves them **unresolved** — the same unresolved state §6.5 treats identically to "we don't know" for any other blocking class. Unresolved sets a hard ceiling on the band. | The band cannot exceed INSUFFICIENT. This is a **gate failure that recurs on every run**, not a one-time setup error — the tenant is permanently research-only. |
| **§13.2, theme-readiness validation** | Readiness's first assertion is "every blocking fact class resolves to values or to a legitimate resolved-empty state; unresolved is a failure and names itself." Because F-B/F-C/F-E have no legitimate-empty state, that assertion fails for any offer-less theme, every time readiness runs. | Readiness failure is not a soft warning: "a theme failing readiness may never be scheduled." The theme can be run by hand, forever, in test mode, but it can never join an unattended schedule — this is a **structural exclusion from the product**, not a degraded output. |

The two bite points must be closed separately because they act at different times and with different consequences: Step 1 is a per-run ceiling that a populated-catalogue theme also passes through every run; readiness is a one-time (repeatable) admission gate that decides whether the theme is allowed onto the schedule at all. A fix that only patches Step 1 leaves readiness failing on its own separately-worded assertion; a fix that only patches readiness leaves every scheduled run still degrading to INSUFFICIENT at Step 1. Both are edited at §7 below, from the same underlying rule.

---

## 2. F-B — legitimately emptiable at the whole-catalogue level

**Ruling.** F-B (offer catalogue with status) may resolve to a legitimate **resolved-empty** state at the whole-catalogue level: a tenant genuinely selling nothing at the time of the run — a community or teaching-only tenant, a seasonal pause, a pre-launch state — has zero rows to be blocking about, and that absence is a first-class, safe, generative signal rather than a hard stop.

**Safety consequence of the change, stated honestly: none negative.** This is the identical pattern §6.3 already applies to F-H (claim ledger) and F-I (proof allowlist): *"resolved-empty is a first-class, safe, generative state — the generator is told it has zero approved [X] and should write teaching-led content."* F-B's fix extends that same sentence to offers: the generator is told it has zero approved offers and writes content with no product-path or commercial-incentive CTA available.

**Why the consumers do not need to change.** Every offer-dependent construct downstream of F-B was already built defensively, because §6.9 already conditions every offer-touching mechanism on the offer resolving:

- The pain-to-offer mapper's own stated rule: *"if nothing matches above threshold, the correct answer is no offer — and the topic can still become genuinely good content with a content CTA or none at all."*
- Every CTA class with an offer-shaped precondition in §6.9's table (product-path: "offer status is live"; commercial-incentive: "programme facts resolved") already fails closed to "this CTA is unavailable" the moment its precondition fact does not resolve — that is exactly the resolved-empty case, not a new one.
- The mapping-distance table's "Far" row already names the no-offer outcome explicitly: *"no offer, no product CTA. Value content with a content CTA or none."*

So the fix is not a rewrite of the consumers; it is a **correction at the gate**, §6.5 Step 1, which today refuses to treat this already-anticipated state as legitimate. Once the gate accepts it, every downstream mechanism that already handles "no offer resolved" handles the whole-catalogue-empty case for free.

---

## 3. F-C — emptiable ONLY jointly with F-B being empty

**Ruling.** F-C (capability statements, positive and negative) may be legitimately empty **only as a joint condition with F-B being empty** — never as an independent emptiness rule.

**The reason, stated in full.** §6.3 gives F-C's own justification for existing: *"negative capability statements are blocking, not enriching… the highest-frequency overclaim in this category is autonomy inflation… so every offer's record carries a does-not list, and capability claims are their own check class."* That discipline exists specifically to prevent a tenant with a real, live offer from making unbounded claims about what it does. **If F-B has live offers, F-C for those offers stays non-emptiable exactly as today** — nothing about a tenant having *some* offers and *no* capability statement for them becomes safer just because this document exists to help offer-less tenants.

Making F-C independently emptiable — allowed to resolve empty even while F-B carries live rows — would let a tenant have live, sellable offers with **no negative-capability grounding at all**, which silently removes check class 6's (capability/autonomy, §6.7) entire basis for that offer: there would be nothing to check an autonomy-inflation claim against, and the class would pass by omission rather than by verification. That is not a relaxation this document is authorised to make (§4a is a floor, not a menu), and it defeats the exact overclaim pattern F-C was created to catch. The joint rule — F-C empty only when F-B is empty — closes that gap by construction: the only way F-C is legitimately empty is the case where there is nothing left for it to be a capability statement *about*.

---

## 4. F-E — emptiable at the whole-set level, following F-B

**Ruling.** F-E (CTA set — allowed CTA classes per offer × destination × language) may be legitimately empty at the whole-set level, following the same emptiness as F-B.

**Safety consequence: none new.** An empty CTA set is not an unhandled case — §6.9's general CTA rules already default every asset with no eligible CTA to a "none" outcome (an asset may run with no CTA at all; this is explicit in the Far-distance row: *"no offer, no product CTA… or none"*). A tenant whose entire offer-bearing CTA set is empty simply produces assets that end without a next step, which the architecture already treats as a legitimate, non-error output.

**The one thing an implementer must not do by habit.** The **content CTA** class (guide, article, resource) is **not offer-scoped** — its precondition in §6.9's table is only *"the resource exists and its URL resolves,"* nothing about F-B or an offer. It therefore **remains available regardless of F-E's emptiness**, and this must be stated explicitly, because the joint pattern established at F-C (§3) trains exactly the wrong reflex here: an implementer who has just wired "F-C empty only when F-B is empty" may reach for the same coupling and make content-CTA availability track F-E's non-emptiness. That would be a new, unjustified restriction — an offer-less, teaching-led tenant is precisely the tenant most likely to want a content CTA (point to the resource, not to a purchase), and coupling its availability to F-E would silently take away the one CTA class this tenant can safely use.

---

## 5. F-F — deliberately NOT the same fix

**Ruling.** F-F (pricing policy) is **not** made emptiable in the sense of §§2–4. F-F is a *rule* — "never state prices in social, link to the pricing page" is a governing instruction, not offer data — and a rule cannot be "resolved-empty" in the way a catalogue or a statement set can; a rule is either authored or it is not. The correct fix is an **engine-level safe default: prices are never stated**, applied automatically whenever the price *value* classes (F-G, and — once Amendment B lands — F-P/F-T) are themselves empty or unresolved. A tenant with nothing to price never has to author a pricing rule by hand; the engine supplies the only rule that could possibly be safe in that state.

**Why treating F-F the same as F-B/F-C/F-E would be dangerous, not merely inconsistent.** §6.3's own load-bearing rule is *"missing is not the same as empty… unresolved is a failure state: we do not know whether [X] exists, so claims are forbidden and the confidence band drops."* If F-F were declared "legitimately empty" in the same sense as F-B, the system would be recording a state that means: **we do not know whether prices may be stated.** That is not an empty rule, it is an absent one, and an absent rule about whether a claim class may fire is exactly the "unresolved, not empty" hazard §6.3 warns against for F-H and F-J. The difference matters operationally: a resolved-empty F-B tells the generator "there is nothing to sell, don't try." An unresolved F-F would tell the generator nothing at all about whether it may state a number that happens to look like a price — which is a check-class-2 (currency/price) failure mode waiting to happen the day a stray figure appears in generated copy. The safe-default fix avoids the ambiguity entirely: F-F is always resolved, either to the tenant's authored rule or to the engine's own default, and the default is chosen at the safe end for exactly the same reason the depiction policy default sits at the safe end (Amendment A, task A2).

**Consequence for the gate.** Because F-F auto-resolves, it never independently causes a Step-1 failure and it is never a reason an offer-less theme fails readiness. The knob a tenant "must configure" to run with no product is, correctly, zero — nobody authors a pricing rule for a business with nothing to price.

---

## 6. The substitution floor

This is the core of this document, and it is the reason A3 exists as a separate task rather than three one-line table edits. §4a states it as a binding prerequisite ruling; this section restates it as architecture and traces its consequences through F-B, F-C and F-E specifically.

### 6.1 Substitution, never exemption

Where F-B, F-C or F-E are legitimately empty, their descriptive content is not simply *omitted* — it is **replaced by a grounded substitute**. "The tenant has no offers" is not the end of the story for what the generator writes; it is the trigger for a different, and still checked, class of statement — teaching-led framing, capability-adjacent description of what the tenant actually does, community or practice-level description — and that substitute content is subject to the same claim-safety discipline as any other descriptive statement the system produces. Exemption (the offer-less path simply stops being checked) is explicitly rejected: it is the thing `03`'s non-triviality test tried to solve for and undershot, and it is the thing this floor exists to raise above.

### 6.2 The external-verifier requirement

**A substitute grounding any descriptive-or-stronger statement class requires an external verifier.** "Descriptive-or-stronger" means: any statement that asserts something about the tenant, its practice, its scope or its nature beyond a pure absence-of-commerce fact — which is most of what a teaching-led or community substitute needs to say to be worth publishing at all. An external verifier is exactly one of the following three, defined precisely because each has a plausible-looking but disqualifying near-miss:

| Verifier | What it is | Qualifying example | Disqualifying look-alike |
|---|---|---|---|
| **Site check** | A visible page element on the tenant's own domain matching the claim's specificity — a human (or the equivalent targeted-fetch machinery, §6.6) confirms an actual element on the page says the thing being claimed. **Explicitly not an HTTP status code.** | A tenant's "About" or "What we do" page states, in visible text, "we run free weekly sessions and do not sell products or services" — the claim of no-commerce, teaching-led operation is directly readable on the page. | The page returns HTTP 200 (it "loads") but is a placeholder, an under-construction notice, or a generic template with no text addressing the claim at all. A 200 response proves the server answered; it proves nothing about what a human reading the page would learn — which is the entire distinction §4a draws. |
| **Resolving URL** | A link the tenant supplies that returns HTML rendering a page containing words or images that substantiate the claim. **Explicitly not a link checker.** | The tenant supplies a link to a published article, a partner's page, or their own "philosophy"/"our approach" page that renders a paragraph actually describing the practice being claimed. | A URL that resolves (200, valid HTML) but redirects to, or renders, a generic homepage, a cookie-consent wall, or a page whose content has since changed to something unrelated. A link-checker view — "the URL is alive" — is satisfied; the claim-supporting content that must actually render is not, which is exactly the case §4a names as insufficient. |
| **Third-party record** | Testimony from an independent source carrying audit authority or transactional grounding — a source that did not write its own description at the tenant's direction. | A local press article describing the tenant's activities, a professional or trade directory entry maintained by the directory operator (not self-submitted free text), an independent review platform's substantiated listing corroborating the tenant's stated scope. | A self-submitted business-directory listing where the tenant typed its own description into a form the directory merely hosts. It looks third-party because the URL and branding are a platform's, but the words are the tenant's own — it carries no independent audit authority or transactional grounding and is tenant self-assertion wearing a third-party interface. |

### 6.3 Operator attestation — the narrow lane that remains

**Operator attestation suffices only for statement classes whose complete absence cannot produce a claim.** This is narrower than the non-triviality test annex `03` proposed, which admitted "an explicit, dated operator attestation" as generally sufficient. §4a raises the floor because tenant self-assertion is precisely what `02` §2.1 spends its argument proving cannot ground a claim — a tenant writing its own description into its own ledger and having the system call it VERIFIED is Defect 1's original shape, and an attestation standing in for an external verifier on a claim-bearing statement class reintroduces that same shape one layer up, inside the emptiability mechanism this document is chartered to fix.

Concretely, this means: the bare **fact of absence** — "this tenant currently has zero live offers" — is a statement that, by itself, asserts nothing about the tenant's capabilities, scope or nature that a viewer could act on or be misled by; its complete absence (i.e., not stating it at all) produces no claim either way. That narrow class of statement may be attested by the operator directly, dated, and used to establish that F-B is genuinely, presently empty. **The moment a substitute statement says anything more** — what the tenant does instead, why, what kind of practice it is, any capability-adjacent framing at all — it has become descriptive-or-stronger and needs the external verifier of §6.2. The line is exact: attestation may establish that the shelf is empty; it may not describe what is on the shelf instead.

### 6.4 The negative-capability field — required for every F-B substitute

**A substitute for F-B must carry a negative-capability field, or the substitution is rejected.** The negative-capability field is a statement, in the operator's own words but structurally required and separately recorded, of what the product or practice does **not** do — a boundary that constrains overgeneralisation, used at enforcement time (check class 6, §6.7) to detect claims that cross a line the operator has drawn. It is F-C's own concept (§6.3: "every offer's record carries a does-not list") applied to the substitute state rather than to a live offer.

**If the field is absent, the substitution is rejected outright**, and the consequence is stated precisely rather than left to default gracefully: **check class 6 (fact-grounding / capability-autonomy) degrades to blocking all descriptive statements for that tenant.** This is a hard, visible failure, not a quiet downgrade, because the reasoning in §4a is exact: *"without it, count preservation becomes numerology, not safety."* A resolved-empty F-B with a plausible-sounding substitute but no negative-capability boundary would let the system count "F-B: resolved" as true while having no mechanism left to catch the autonomy-inflation pattern F-C exists to catch (§3) — the count of resolved classes would look the same as a safely-substituted tenant's, while the actual safety property behind that count is missing. Requiring the field, and failing loudly when it is missing, keeps the count meaning what it says it means.

### 6.5 What the substitution floor does not change

The substitution floor governs the **content that stands in for the empty class**; it does not create a new fact class, does not touch F-D, F-N, F-J, or any class not named in §§2–5 above, and does not require an external verifier for the pure fact-of-absence attestation described at §6.3. It is a floor on descriptive-or-stronger substitute content specifically, applied at exactly the three points (F-B, F-C, F-E) this document is chartered to fix.

---

## 7. What changes at §6.5 Step 1 and at §13.2 readiness

### 7.1 §6.5, Step 1 — the exact edit

Step 1's existing text stands unchanged: *"every blocking class must be resolved or legitimately resolved-empty, non-conflicted and not hard-stale."* What changes is the cash-out value of **"legitimately resolved-empty" for F-B, F-C and F-E specifically.** Today that value is undefined for those three classes (§6.3 answers "No" to whether they may be legitimately empty at all, so the phrase never applies to them). The edit gives it a precise, three-part test:

1. **The absence is genuine and current**, established by an operator attestation of the pure fact-of-absence (§6.3) or a stronger source.
2. **Any substitute descriptive content is grounded by an external verifier** (§6.2) — a site check, a resolving URL, or a third-party record, none satisfied by attestation alone.
3. **For F-B specifically, the substitute carries a negative-capability field** (§6.4).

If all three hold for the classes to which they apply (F-C's test additionally requires F-B's own emptiness per §3; F-E's requires F-B's per §4), the class is **legitimately resolved-empty** and Step 1 passes for it exactly as it would for a populated class. **If any part fails — no attestation, a substitute grounded only by attestation, or a missing negative-capability field — the class is not legitimately resolved-empty.** It reverts to the existing **unresolved** state, and Step 1's existing ceiling behaviour applies unchanged: no new failure mode is invented, the existing one is simply reached by a sharper test than "the catalogue query returned zero rows."

    Step 1, F-B/F-C/F-E specifically:

      catalogue query
        -> non-empty?  ---------------------------> resolved (unchanged path)
        -> empty:
             attestation of absence present?
               no  -> UNRESOLVED -> existing Step-1 ceiling (unchanged)
               yes -> substitute content authored?
                        no substitute needed  -> LEGITIMATELY RESOLVED-EMPTY
                        substitute authored   -> external verifier present?
                                                   no  -> UNRESOLVED -> ceiling
                                                   yes -> (F-B only) negative-
                                                          capability field present?
                                                            no  -> check class 6
                                                                   blocks all
                                                                   descriptive
                                                                   statements
                                                                   (§6.4)
                                                            yes -> LEGITIMATELY
                                                                   RESOLVED-EMPTY

F-F is not part of this test at all: it is never gated at Step 1 as an emptiness question, because it auto-resolves to its safe default the moment the price-value classes it depends on are empty or unresolved (§5). It simply never appears as a Step-1 failure reason for an offer-less tenant.

### 7.2 §13.2, readiness — what it must assert instead

Readiness's first bullet — *"every blocking fact class resolves to values or to a legitimate resolved-empty state; unresolved is a failure and names itself"* — is unchanged in wording and now inherits the sharper test at §7.1 automatically, because it is defined in terms of the same phrase §6.5 defines. What readiness must **additionally** assert, so the failure is legible rather than a bare restatement of the Step-1 outcome, is:

- **For any theme where F-B, F-C or F-E resolve empty, readiness names which of the three tests at §7.1 is unmet**, rather than reporting a single undifferentiated "blocking class unresolved" — an operator told "F-B: no external verifier recorded for the substitute" can fix that in minutes; an operator told "F-B: unresolved" has to guess whether the fix is data entry, a missing attestation, or a missing verifier link.
- **Readiness never fails a theme for having zero offers, in itself.** The thing readiness is entitled to fail on is a missing or inadequate substitution record, not the underlying business fact of having nothing to sell. This is the sentence that closes P-1 at this bite point: today, readiness's assertion is unsatisfiable by construction for an offer-less tenant; after this edit, it is satisfiable by a tenant that has done the (small, one-time) work of attesting absence, grounding its substitute content, and recording a negative-capability boundary.
- **F-F is never named as a readiness failure reason.** Readiness must assert that the F-F safe default is active whenever the price-value classes are empty or unresolved — an automatic, always-true assertion for an offer-less tenant, never a decision the operator is asked to make.

Everything else §13.2 already asserts is unaffected: the non-empty-candidate-set assertion, the format-profile and CTA-liveness assertions, the source-roster assertions, and the ranking-load fit measurement all operate identically whether or not F-B is empty, because none of them is keyed to offer presence.

---

## 8. The interaction with confidence bands

**Ruling: an empty-catalogue tenant, correctly substituted per §6, lands at PARTIAL — never FULL, and never INSUFFICIENT.**

**Why not INSUFFICIENT.** That is the defect this document exists to close. Once F-B/F-C/F-E pass Step 1 as legitimately resolved-empty (§7.1), no blocking-class ceiling applies, and INSUFFICIENT's precondition — *"any blocking gate fails"* — is no longer met. Landing here would mean this document did nothing.

**Why not FULL, and why this is a real ruling rather than a formality.** Read literally, FULL's stated precondition — *"every blocking class resolved (or legitimately resolved-empty) and non-conflicted; every constraining class in one of the two resolved states — never unresolved; every commercially binding fact observed this run or within its stale-warn window; zero conflicts of any severity"* — looks satisfiable by a cleanly-substituted, externally-verified, freshly-attested empty catalogue: nothing is unresolved, nothing conflicts, and the absence itself can be re-confirmed every run. A naive reading would promote such a tenant to FULL. **That reading is rejected.** §6.5's own stated purpose for a counting rule over a score is that the band tells the operator "what actually changed" and is checkable row by row in the brand-truth panel; FULL's capability column promises specific things a populated tenant's corroboration machinery earns — *"approved proof claims allowed. Prices and trial terms may be stated if policy permits"* — as the payoff for **directly-resolved, corroborated commercial facts**. A substitute is not a directly-resolved commercial fact: it is evidence that stands in for missing data, verified externally precisely because there is no primary fact to corroborate against, which is categorically thinner than "the site confirms the price is unchanged." Counting an externally-verified absence as equivalent to a fully corroborated, populated commercial fact set collapses exactly the distinction FULL exists to signal, and repeats the "count preservation becomes numerology" failure §4a warns against at §6.4, one level up — a hollow FULL badge that means "there was nothing here to get wrong" rather than "everything here was checked and holds."

**Why PARTIAL is the honest, and sufficient, answer.** PARTIAL's precondition — *"all blocking gates pass, but... corroboration is thin"* — is exactly the state a substitute-grounded empty catalogue is in: gates pass, and the grounding behind the substitute content is real but structurally thinner than direct corroboration. PARTIAL's capability row already withholds precisely the things an empty-catalogue tenant has nothing to offer anyway — *"all proof claims blocked unless that individual ledger entry is itself at full confidence. No prices, no trial terms, no case metrics, no comparative claims. CTAs limited to the zero-commitment and product-page classes"* — none of which this tenant could use even at FULL, since F-F's safe default already forbids prices (§5), F-E may be wholly empty (§4), and there is no product-path CTA to gate in the first place. **Nothing capability-relevant is lost by refusing FULL**, and the band label stops overstating what was actually verified. The stated capability set for this named case is therefore: spin allowed, using the substitute framing; the content CTA class available per §4; no product-path, event, or commercial-incentive CTA (none resolve); no prices, proof claims, trial terms, case metrics or comparatives (none exist to state); pack marked PARTIAL with the reason "offer catalogue legitimately empty, substitute grounded."

**What would change this ruling.** A tenant whose *substitute* content itself later needs proof-shaped or numeric claims (a stated attendance figure for its sessions, a named partner) reopens the ordinary claim-gate and check-class-4/9 machinery exactly as it would for any tenant — the PARTIAL ceiling here is about the offer-catalogue substitution specifically, not a permanent cap on that tenant ever reaching FULL for unrelated, independently well-corroborated facts (F-D, F-N, and so on can each still be fully resolved and contribute to the ordinary FULL/PARTIAL determination for everything F-B/F-C/F-E do not touch). This document rules only on the offer-catalogue-empty case's own contribution to the band.

---

## 9. Wire-in — sections this design changes

| § in `ARCHITECTURE_PLAN.md` | What changes | Extension / rework / deletion |
|---|---|---|
| **§6.3** (fact taxonomy) | The "may be legitimately empty?" answer for **F-B, F-C, F-E** flips from **No** to **Yes, conditional** — F-B at whole-catalogue level; F-C only jointly with F-B; F-E at whole-set level following F-B — each qualified by the three-part test at §7.1. A new footnote states the substitution floor (§6) in summary and cross-references this document. **F-F's row and answer (No) are unchanged**; a new footnote documents the automatic safe-default resolution (§5) so F-F is never manually authored by an offer-less tenant. | **Rework** of the F-B/F-C/F-E cells — this is the deliberate fix, not an accidental loss; the "No" answer these three classes carried was itself the defect (P-1), and its replacement is the entire point of this document. No sentence is deleted without a replacement standing in the same cell. |
| **§6.4** (precedence, per fact class) | No change to the precedence table's mechanics. Adds a note that the F-B "site check" verifier of §6.2 is the same site-binding row already specified for F-B ("Site (binding)... Red flag if the site shows retired or 404 while Notion says live") — reused, not a new precedence path. | Extension (light) |
| **§6.5** (confidence bands, Step 1 and the band table) | Step 1's cash-out of "legitimately resolved-empty" is defined precisely for F-B/F-C/F-E (§7.1). The PARTIAL row's precondition text gains a named case: an offer-catalogue legitimately empty per the three-part test lands at PARTIAL, with the reason stated in the ruling at §8. | Extension |
| **§6.7** (claim-safety substrate, check class 6) | Check class 6 (capability/autonomy) gains the enforcement consequence of a missing negative-capability field on an F-B substitute: it degrades to blocking all descriptive statements for that tenant (§6.4). This is a new, named failure mode of an existing check class, not a new class. | Extension |
| **§6.9** (spin application, CTA preconditions) | No precondition wording changes — every offer-dependent CTA precondition already required the offer to resolve. Adds an explicit note that the **content CTA's** availability is not, and must not become, coupled to F-E's emptiness, because it is not offer-scoped (§4). | Extension (documentation of an existing behaviour, to prevent a future accidental coupling) |
| **§13.2** (theme-readiness validation) | The first readiness assertion is unchanged in wording; its cash-out inherits §7.1's sharper test automatically. Adds: (a) readiness must name which of the three §7.1 tests is unmet, not report an undifferentiated "unresolved"; (b) readiness must never fail a theme for having zero offers in itself, only for an inadequate substitution record; (c) F-F's safe-default activation is asserted automatically and is never a readiness failure reason. | Extension. **Flagged: this section is not in the combined A1–A3 wire-in list at `00_MASTERPLAN.md` §5 (task A4's row), which names §6.3, §6.5, §6.7, §4.2a, §5.6, §11.3, §12.2, §12.4, §13.4, §14.0, §14.3, §16, §17 but omits §13.2.** §13.2 is P-1's own second bite point, named as such in the masterplan's own defect table (§1: "§13.2 readiness fails → may never be scheduled"). Omitting it from A4's edit list would leave the "may never be scheduled" half of P-1 unfixed. This document rules that §13.2 must be added to A4's edit list; it is included here for that reason. |
| **§10.3** (spin block knobs) | Adds, to the existing brand-truth source-pointers row: a pointer for the external-verifier record per legitimately-empty class (site check reference, resolving URL, or third-party record identifier), and a pointer for the negative-capability field on an F-B substitute. No new knob category — these extend the existing source-pointer and capability-statement knobs already listed. | Extension |

**No binding sentence is deleted by this document.** Every edit either changes a table cell whose prior value was itself the defect being closed (§6.3's F-B/F-C/F-E row), or adds new text alongside an unchanged governing sentence (§6.5 Step 1's wording, §13.2's first assertion). Where this document's edits interact with a rule stated elsewhere (F-C's dependence on §6.3's own capability-discipline justification, §4; the content-CTA's independence from F-E, §4; F-F's "missing is not the same as empty" hazard, §5), the source rule is quoted and preserved, not restated in a way that could drift from it.
