# Phase 0 Calibration Artefacts

The four calibration artefacts plus the frozen eval set required by ARCHITECTURE_PLAN.md
§17.2 Phase 0. These gate Phase 1:

> *Do not start Phase 1 until:* **the four calibration artefacts exist (Czech and English
> structural calibration, Czech and English golden sets), the frozen eval set exists, and the
> two company privacy artefacts exist in their required shape with the EDPB reference
> verified.**

(The privacy artefacts are a separate Phase-0 deliverable and do not live in this directory.)

## The artefacts

| Artefact | File | Governing plan sections |
|---|---|---|
| English structural-calibration corpus + measurement pass | `en/structural_corpus.md` | §14.2 (layer 2), §14.4 (EN rubric), §17.2, R2-M15 |
| Czech structural-calibration corpus + measurement pass | `cs/structural_corpus.md` | §14.2 (layer 2), §14.4 (dim 10), §3.4, §17.2 |
| English judge golden set | `en/golden_set.yaml` | §14.2 (judge calibration), §14.4, §17.2, R2-M15 |
| Czech judge golden set | `cs/golden_set.yaml` | §14.2, §14.4 (eleven dimensions), §17.2, R3-M5, OD-20 |
| Frozen eval set (both languages) | `eval/frozen_eval_en.yaml`, `eval/frozen_eval_cs.yaml` | §14.8, §17.2 |

## The Phase-1 gate criterion (verbatim, §17.2 acceptance criteria)

> **Both golden sets** produce stable judge verdicts on their own known-good and known-bad
> items when run by hand.

**What "stable" will mean operationally (proposed, needs operator sign-off):**

1. The judge is run by hand over the full golden set on **three separate occasions** (separate
   sessions, same rubric version, same model/version string, recorded per §14.7).
2. **No item flips verdict between runs** (pass↔fail across the three runs = unstable), and
3. every item's stable verdict **matches its `expected_verdict`**, tracked **by direction**
   (§14.2): judge-passed/expected-fail (dangerous direction) and judge-failed/expected-pass
   (expensive direction) are counted separately. Phase 0 does not fix numeric agreement
   thresholds — per R-26 those come from this measured data, not from an authored number —
   but any dangerous-direction miss on a deliberate negative is a blocker, not a statistic.
4. Every run is logged (date, model string, rubric version, per-item verdicts). Disagreements
   feed OD-20: dimensions that do not discriminate get down-weighted or merged, logged.

Until a language's golden set passes this, that language's judge **runs deliberately lenient
and its flag-rate ceiling is recorded as inactive** (§14.2, R2-M15).

## Rules that protect these artefacts

- **The frozen eval set is never read while authoring prompts** (§14.8). It is for measuring
  prompt/rubric/model changes before rollout. It grows only by deliberate, logged addition —
  each eval file carries its own append-only additions log.
- Golden set and eval set are **disjoint** — no shared text. The golden set calibrates the
  judge; the eval set regression-tests changes. One corpus doing both jobs measures nothing.
- Structural bands are **outputs of measurement, not authored** — the band tables in both
  corpora stay empty until a real tokenisation and measurement pass runs (per language;
  nothing inherited from English into Czech, dim 10).
- The Czech rubric is a **hypothesis** (R3-M5): the golden-set agreement data decides which
  of the eleven dimensions actually discriminate; changes are logged like threshold moves.

## Status table

| Item | Status | Needs operator approval | Needs tooling |
|---|---|---|---|
| EN corpus — LinkedIn exemplars (10) | Extracted from `docs/marketing`, cited | Confirm curation | — |
| EN corpus — carousel exemplars | 2 structural proxies only | Supply 3+ real carousels | — |
| EN corpus — short-form scripts | **Empty — source files in repo are 0 bytes** | Supply transcripts (e.g. the 1M+-view Gojiberry video) | — |
| EN corpus — captions | 3 DM-script rhythm references only | Supply real captions | — |
| EN measurement pass (bands table) | Template ready, all cells empty | — | Tokenisation + measurement pass |
| CS corpus — real exemplars | **None exist; all slots open** | Supply real Czech posts per slot | — |
| CS corpus — authored drafts (5: CS-LI-D1/D2, CS-CA-D1, CS-SF-D1, CS-SC-D1) | Drafted | Approve each as exemplar | — |
| CS measurement pass (bands table) | Template ready, all cells empty | — | Tokenisation + measurement pass (CS tokeniser) |
| EN golden set (18 items: 5 pos / 8 neg / 5 borderline) | Drafted | Approve 5 adapted positives; sign off set freeze | Hand judge runs (×3) |
| CS golden set (22 items: 5 pos / 12 neg / 5 borderline) | Drafted; all 11 dimensions covered (d5 partial — awaits seed lexicons) | Approve 5 adapted positives; sign off set freeze | Hand judge runs (×3) |
| Frozen eval EN (12 items) | Authored, disjoint | Sign off freeze | — |
| Frozen eval CS (12 items) | Authored, disjoint | Sign off freeze | — |
| "Stable" operational definition (above) | Proposed | Approve | — |

## Operator-approval queue — CLOSED 2026-08-07 (decision W8-6)

**The operator delegated exemplar curation to model judgment at run time** ("the LLM picks
those properly during the flow — we do not want this to be too strict automation"). The
authored calibration artefacts **stand as-is without operator sign-off**; the generation-time
model selects voice exemplars from the corpus pool (including the 13 Notion-mined Czech
candidates in `cs/notion_exemplar_candidates.md`) per asset. This delegates *taste* — which
exemplar fits — never *truth*: the golden sets and frozen eval sets **remain frozen as
authored** (`meta.frozen` is treated as flipped by W8-6), the judge gates are untouched, and
if judge stability against the golden sets proves poor in practice the recourse is
re-authoring with operator input, not silently loosening the judge. Full rationale:
DECISION_LOG.md row W8-6.

*The original queue is kept below for the record only — no item awaits action:*

1. `cs/structural_corpus.md`: approve/reject drafts CS-LI-D1, CS-LI-D2, CS-CA-D1, CS-SF-D1,
   CS-SC-D1 as corpus exemplars; supply real Czech exemplars for the open slots.
2. `en/structural_corpus.md`: confirm the LinkedIn curation; supply real carousels, short-form
   transcripts and captions (the `GojiBerry_YoutubeInspiration/*.txt` files are empty).
3. `en/golden_set.yaml`: approve en-gp-01..05 (adapted from corpus posts, hype stripped).
4. `cs/golden_set.yaml`: approve cs-gp-01..05 (authored Czech, no real corpus exists yet).
5. `eval/frozen_eval_en.yaml` + `eval/frozen_eval_cs.yaml`: sign off the freeze (flip
   `meta.frozen`), after which changes go through the additions log only.
6. Approve the operational definition of "stable" above.
7. Once seed lexicons exist: re-map cs-gn-12 (dimension d5) onto concrete banned patterns.
