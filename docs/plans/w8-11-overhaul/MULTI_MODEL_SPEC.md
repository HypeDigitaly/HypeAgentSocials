# MULTI-MODEL TEST-RENDER SPEC — W8-11

*Companion to `PLAN.md`. Self-contained: an executor implements `engine/src/hypeagent/test_render.py`
plus the registry/config/store/stages edits below from this file alone. Authored 2026-08-07 from the
operator-supplied kie.ai API docs (`reference/kie-models/nano-banana-pro-api.md`,
`reference/kie-models/gpt-image-2-api.md` — authoritative for model strings, params, constraints,
price snapshots), `config/model_registry.yaml`, `RENDER_CONTRACT_SPEC.md` and a read of
`media_gen.py` / `store.py`.*

**Operator directive (binding, 2026-08-07).** Every creative is ALSO generated on two additional
kie.ai models — `gpt-image-2-text-to-image` and `nano-banana-pro` — alongside the canonical
nano-banana-2 pipeline. Outputs are saved per-model in model-named folders, and on these test models
the FULL slide text is embedded in the prompt for the model to render in-image (both have strong
text-rendering claims). Purpose: side-by-side output testing to pick the future canonical model.

Governing decision: **test renders are evidence, never product.** Test renders are never
delivered, never gate delivery, and their failures never fail the run. Everything below is a
recommended default — each dial is marked **[operator-default, config-overridable]** where a config
key exists; structural rules (choke point, ledger identity, fail-isolation) are binding.

---

***ROUND-4/5 AMENDMENT (2026-08-07/08, operator-ratified — binding; `PLAN.md` §13 items 19.A and
22.3).*** *The 44-render simulation answered the question this spec was commissioned to ask, so its
roles invert and its default flips off:*

1. ***`gpt-image-2-text-to-image` is the CANONICAL INCUMBENT, not a candidate.*** *It renders the
   complete finished creative — styled expressive typography in-image — as the first rung of the
   delivery ladder (`PLAN.md` §1). It therefore gets **no `test`-tier route**: its own canonical rows
   are the scoreboard's anchor. Every "canonical = nano-banana-2 + Pillow" sentence below is stale
   and is corrected by Wave 0 task 0-6; the deliverable path is now
   **`gpt-image-2` full-design render → per-glyph text verification → one retry → Pillow-composited
   fallback → copy-only**.*
2. ***`nano-banana-pro` and `nano-banana-2` are the two challengers*** *— each defined twice in the
   registry, once as a **`status: reserved`** canonical route (unreachable from delivery, kept for a
   future re-enable: nano-banana-2 as a ground renderer, nano-banana-pro as the `image_input`
   specialist) and once as a `test`-tier route. §12 check 8 is amended for exactly this shape.*
3. ***The whole track ships `enabled: false` — single-model production.*** *Everything in this spec is
   still BUILT (registry two-door, reserved refusal, the leaf, the scoreboard, the consistency
   checks, the tests) so that turning it on is a one-line config change rather than a project; but the
   default run submits **zero** test renders, spends **$0.00**, and the $3 wallet does not appear in
   `PLAN.md` §9.3's active arithmetic. The wallet and reserve values themselves are **unchanged**.*
4. ***`image_input` remains out of scope*** *(§4.6) — permanently for W8-11. The Tier-1 unknown-tool
   mechanism is instead a **reserved artifact zone composited pixel-exact by Pillow**
   (`PLAN.md` §13 item 22.3), which beats a faithful-but-redrawn reference (F15) on integrity.*

*Read every "test model", "candidate" and "canonical" below through this amendment.*

---

## 1. What is built, in one paragraph

After the canonical media stage finishes an asset, a `TestRenderRunner` walks that asset's slots and,
for each enabled test model, deterministically builds a full-text prompt (the slot's complete gated
`on_image_text` verbatim in `<<…>>` markers plus the asset's style-system recipe), passes it through
the **same** `render_contract.govern()` gate as every canonical prompt, writes a write-ahead ledger
intent keyed by `(…, model_string)`, submits through the **same single `create_task` choke point**,
saves the result under `<asset_dir>/models/<model_string>/`, runs N-E vision QA on it, and rolls the
verdicts into a per-model scoreboard in the run digest. Zero additional LLM *authoring* calls are made
— the test prompt is assembled programmatically from copy that already passed the claim gate; the only
new LLM spend is QA. A per-run USD ceiling caps test spend; hitting it skips remaining test renders
with a decision event and never touches canonical work.

Fully-programmatic (Pillow-composited) slots are tested too — that is the core comparison: the
model-rendered card vs the Pillow-composited card for the same slot, same text, same style recipe.

---

## 2. Where this code lives

One new leaf module; everything else is an edit to an existing file (PLAN §4: W8-11's new code goes
into leaves rather than growing the six giants).

| Module | Contains | May import |
|---|---|---|
| `engine/src/hypeagent/test_render.py` (NEW) | `TestRenderConfig` consumption, `build_test_render_prompt()`, `TestRenderRunner`, `aggregate_scoreboard()` | stdlib, `fsutil`, `asset_model`, `render_contract`, `media_gen` (KieClient, ModelRoute, ModelRegistry, vision-QA entry point, `_write_provenance_yaml` sibling), `promptcraft` (GUARDRAILS, style-section builder), `store`, `trace`, `config_load` |
| `engine/src/hypeagent/media_gen.py` (EDIT) | `ModelRoute` capability fields, `load_model_registry` parsing + checks (§12), `resolve_test_route()`, Phase-0 adoption filter (§8.3) | — |
| `engine/src/hypeagent/store.py` (EDIT) | widened UNIQUE migration (§7), `find_media_intent(..., model_string=...)` | — |
| `engine/src/hypeagent/stages.py` (EDIT) | `stage_media` invokes `TestRenderRunner` after canonical processing, inside the isolation boundary (§5.4) | — |
| `engine/src/hypeagent/process_summary.py` (EDIT) | digest scoreboard section (§9.3) | — |
| `engine/src/hypeagent/config_load.py` (EDIT) | `TestRenderConfig` frozen dataclass + loader (optional keys, safe defaults — a theme predating this spec still loads with `enabled: false`) | — |
| `config/model_registry.yaml` (EDIT) | two `test`-tier routes + capability fields (§3) | — |
| `config/themes/hypedigitaly.yaml` (EDIT) | `generation.media.test_render` block (§11) | — |

Import direction is strictly `test_render → media_gen`; nothing in `media_gen` imports `test_render`
(no cycle). `stages` calls `test_render.TestRenderRunner` directly.

---

## 3. Registry amendment — two `test`-tier routes with capability fields

### 3.1 New tier and its resolution rule

A new tier `test` is added. It is deliberately **outside** `TIER_ORDER`'s canonical draft→standard
ranking: `resolve_route()` (the canonical/route_by_class path) **refuses any route whose tier is
`test`** regardless of `tier_ceiling` — a test model can never be routed into delivery by config
accident. Symmetrically, a new `ModelRegistry.resolve_test_route(route_id)` refuses any route whose
tier is **not** `test`. Two disjoint resolution doors; promotion (§10) is the only way a model crosses
between them, and that is a registry edit, not a runtime path.

**Third door, added by the round-4/5 amendment: `status`.** Every route gains
`status: "active" | "reserved"` (default `"active"`). `resolve_route()` **also refuses any
`status: reserved` route**, and no reserved route may appear in `route_by_class` or in the defaults.
This is what lets `nano-banana-2` and `nano-banana-pro` stay fully specified — price, capabilities,
comments, consistency checks — while being unreachable from delivery, exactly the way `tiktok` stays
configured-but-disabled (`PLAN.md` §13.4). A reserved route is not dead config: it is a documented,
checked, one-word-away capability, and the checks in §12 apply to it in full.

### 3.2 New per-route capability fields

`ModelRoute` gains (loader defaults keep every existing route loading unchanged):

```python
full_text_render: bool = False        # True ⇒ the full-text embed variant (§4) applies
image_input_max: int = 0              # max reference-image URLs the model accepts (0 = none)
prompt_max_chars: int = 20000         # provider prompt-length limit; §4.5 checks against it
resolution_constraints: Mapping[str, tuple[str, ...]] = {}
                                      # e.g. {"unsupported_aspects_at": ("2K:4:5", ...)} — see YAML shape below
output_format_supported: tuple[str, ...] = ()   # empty = no output_format param documented
```

### 3.3 The two route definitions (exact YAML to append to `config/model_registry.yaml`)

Model strings, params, constraints and price snapshots come from the operator-supplied official API
docs in `reference/kie-models/` — the same verification-status comment discipline as the existing
routes applies (docs-verified now; annotate LIVE-VERIFIED with the first real `creditsConsumed`
figures, exactly as `img-standard-nano-banana-pro` was annotated in W8-9 Q4).

**Round-4/5 amendment — the gpt-image-2 route MOVED, it was not duplicated.** The block below is
kept as the authoritative capability record, but it now ships at
**`route_id: img-standard-gpt-image-2`, `tier: standard`, `status: active`**, and it is the target of
`route_by_class` / `defaults.draft_route` / `defaults.fallback_draft_route` (task IV-8). There is **no
`img-test-gpt-image-2`** — the incumbent does not test against itself, and §12 check 3 would refuse a
`test`-tier route that delivery depends on. `price_credits: 6` is now **LIVE-CONFIRMED** (44
simulation renders, `SIM_REPORT.md`), not a planning figure. The `resolution_constraints` block below
is load-bearing in the canonical path: Instagram's `4:5` appears in it, so every IG render pins
`resolution: "1K"` mechanically.

```yaml
  - route_id: img-standard-gpt-image-2          # CANONICAL INCUMBENT (was img-test-gpt-image-2)
    tier: standard
    status: active
    display: "GPT Image 2 (text-to-image) — canonical full-design renderer"
    model_string: "gpt-image-2-text-to-image"   # VERIFIED 2026-08-07 vs operator-supplied kie.ai docs (reference/kie-models/gpt-image-2-api.md)
    price_credits: 6      # LIVE-CONFIRMED 2026-08-07/08 across 44 simulation renders (SIM_REPORT.md)
    price_usd: 0.03
    input_params: {prompt: string, aspect_ratio: string, resolution: string}
    full_text_render: true
    image_input_max: 0                          # text-to-image variant has no image_input
    prompt_max_chars: 20000
    resolution_constraints:
      # HARD CONSTRAINT from the API doc: these aspects are NOT supported at 2K/4K.
      unsupported_aspects_at_2k_4k: ["5:4", "4:5", "3:1", "1:3", "9:21"]
    output_format_supported: []                 # no output_format param documented — PNG assumed
    notes: "Canonical renderer. IG 4:5 MUST pin resolution '1K' (aspect unsupported at 2K/4K), applied mechanically from resolution_constraints. LinkedIn 16:9 unconstrained. ~5% Czech display-type defect rate (SIM_REPORT F18) is why the per-glyph text-QA gate is mandatory."

  - route_id: img-test-nano-banana-2            # CHALLENGER (dual role — see status: reserved twin below)
    tier: test
    status: active
    display: "Nano Banana 2 — side-by-side challenger"
    model_string: "nano-banana-2"
    price_credits: 8
    price_usd: 0.04
    input_params: {prompt: string, aspect_ratio: string}
    full_text_render: true
    image_input_max: 0
    prompt_max_chars: 20000
    resolution_constraints: {}
    output_format_supported: []
    notes: "Test-tier challenger. Its model_string also appears on the RESERVED canonical route img-standard-nano-banana-pro (the historical ground renderer, now the composited-fallback reserve) — permitted by §12 check 8's amended dual-role rule, and TestRenderRunner skips any (slot, model) that already carries a canonical row."

  - route_id: img-test-nano-banana-pro
    tier: test
    display: "Nano Banana Pro (Gemini 3.0 Pro) — side-by-side test"
    model_string: "nano-banana-pro"             # VERIFIED 2026-08-07 vs operator-supplied kie.ai docs (reference/kie-models/nano-banana-pro-api.md)
    price_credits: 18     # ~$0.09 @1K-2K (≈18 credits), ~$0.12 @4K (≈24) — page-derived; reconcile vs creditsConsumed on first live call
    price_usd: 0.09
    input_params: {prompt: string, image_input: array, aspect_ratio: string, resolution: string, output_format: string}
    full_text_render: true
    image_input_max: 8                          # up to 8 reference URLs, ≤30MB each, jpeg/png/webp — UNUSED in W8-11 (§4.6)
    prompt_max_chars: 20000
    resolution_constraints: {}                  # both destination aspects (16:9, 4:5) supported at any resolution
    output_format_supported: [png, jpg]
    notes: "Test-tier only. Text-rendering + localization claims are exactly what the Czech-diacritics QA target (§9.1) tests."
```

**Naming-collision note (documentation, not code):** the historical route
`img-standard-nano-banana-pro` carries `model_string: nano-banana-2` — the M4 audit found no
nano-banana-pro page on docs.kie.ai at the time. That page now exists and `nano-banana-pro` is a real,
distinct model. After the round-4/5 amendment there are **four** adjacent entries and the registry
comment block must state all of them explicitly so nobody "fixes" one into another:

| route_id | model_string | tier | status | role |
|---|---|---|---|---|
| `img-standard-gpt-image-2` | `gpt-image-2-text-to-image` | standard | active | **the canonical renderer** |
| `img-standard-nano-banana-pro` | `nano-banana-2` | standard | **reserved** | historical ground renderer, kept for re-enable |
| `img-specialist-nano-banana-pro` | `nano-banana-pro` | standard | **reserved** | `image_input` specialist, kept for re-enable (§4.6) |
| `img-test-nano-banana-2` / `img-test-nano-banana-pro` | `nano-banana-2` / `nano-banana-pro` | test | active | the two challengers (inert while `test_render.enabled: false`) |

§12 check 8 makes the distinction mechanical — see its amended dual-role rule.

### 3.4 Endpoints

Identical to the existing integration — same `createTask`/`recordInfo` URLs from `meta`, same
`waiting|success|fail` states, same `resultJson.resultUrls`, same `creditsConsumed` reconciliation.
`KieClient` is a transport and is **not modified**; only the `input` dict contents differ per route
(`resolution` is a new input key for these two routes; `CREATE_TASK_ALLOWED_KEYS` gains
`"resolution"` so the trace can carry it).

---

## 4. Test prompt construction — the GovernedPrompt TEST variant

### 4.1 One governed prompt per (slot, model)

`build_test_render_prompt(contract, slot, style_recipe, route) -> str` is a **pure, deterministic
function** — no LLM call. It is invoked once per slot per enabled test model; the two models' prompts
may be byte-identical (identity separation comes from the ledger tuple §7, never from prompt bytes).
The resulting string goes through the **same** `render_contract.govern()` as every canonical prompt —
same choke point, same claim gate on the exact submitted bytes, same leak/banned-string checks, same
persona and fake-UI rules. There is no second door: `_submit_new` remains the only reachable
`create_task` call site, and `TestRenderRunner` submits through it (or through an extracted shared
helper with the identical `GovernedPrompt`-typed signature — invariant I1's AST guard test must cover
whichever shape lands).

### 4.2 What the prompt contains (for routes with `full_text_render: true`)

1. **The slot's complete gated `on_image_text`, verbatim, in `<<…>>` markers** — every span
   (title / kicker / body), each labelled with its role and hierarchy, e.g.
   `TITLE (largest, render verbatim, character-for-character including diacritics): <<…>>`. The
   ≤2-span / ≤6-word diffusion-text cap (`RenderPolicy.diffusion_text_max_spans` /
   `diffusion_text_max_words_per_span`) is **LIFTED** for these prompts — that cap is a canonical
   *authoring* constraint enforced by the N-D validator, and test prompts never pass through N-D;
   deterministic construction sidesteps it without weakening any canonical validator.
2. **The style-system recipe**: palette hexes, type intent (family class, weight, case), and the
   slot's layout description (zone geometry in prose) from the asset's style system
   (`STYLE_SYSTEMS_SPEC.md`), so the model renders the ENTIRE finished creative including text — the
   model-rendered card is directly comparable to the Pillow-composited card.
3. **Guardrails**: `promptcraft.GUARDRAILS` verbatim (one thing, one place — `compose_prompt` and
   `_NEGATIVE_CONSTRAINTS` are deleted by Wave I and are not resurrected here).
4. **Persona + fake-UI rules**: `PersonaPolicy` wording and the no-fake-HypeDigitaly-UI rule apply
   unchanged.
5. **Aspect + resolution intent** matching the `input` params (§4.4).

### 4.3 Why govern() needs no test-mode branch

`govern()`'s four steps hold as-is:

- **Text-set closure (I3)** passes because every `<<…>>` span *is* a member of
  `slot.on_image_text.spans()` — the embed is the gated set, whole and verbatim. An invented span
  still fails, exactly as it must.
- **Claim gate on exact bytes (I2)**: numerals inside the embedded body travel *with their
  qualifying sentence* (the full span is embedded), so the Wave-II qualification co-location change
  works in our favour rather than against it. The style recipe keeps the "N percent" spelling
  work-around (invariant G1).
- **Leak check** and **register/mode coherence** run unchanged; the recipe is derived from
  `contract.visual`, so its register matches by construction.

`GovernedPrompt` itself is **unchanged** — no new fields. Route identity rides on the submission call
and the ledger row, not on the prompt object.

### 4.4 Input construction per route

| | `gpt-image-2-text-to-image` | `nano-banana-pro` |
|---|---|---|
| `prompt` | governed text | governed text |
| `aspect_ratio` | from `VisualPolicy.aspect_ratio` (`16:9` linkedin, `4:5` instagram_feed) | same |
| `resolution` | config default `"1K"`; **`4:5` MUST pin `"1K"`** (hard API constraint) — the pin is applied mechanically whenever the aspect appears in the route's `unsupported_aspects_at_2k_4k` list | config default `"1K"` **[operator-default, config-overridable]** (2K is the same snapshot price; 1K is kept for cross-model comparability) |
| `output_format` | omitted (not documented) | `"png"` |
| `image_input` | n/a | omitted in W8-11 (§4.6) |

### 4.5 Length check

`build_test_render_prompt` raises (config-class error, caught by the isolation boundary §5.4 and
recorded as that slot's test failure) if the built prompt exceeds `route.prompt_max_chars` (20,000
for both). Full slide text + recipe is well under this; the check exists so a future style system
cannot silently truncate.

### 4.6 image_input — explicitly out of W8-11 scope

`nano-banana-pro` accepts up to 8 reference images (real logos / screenshots). The capability is
**recorded in the registry but unused** this milestone: no logo-file plumbing exists on the test path
and adding it would blur the model-vs-Pillow comparison. Follow-up dial, noted in §10.

---

## 5. Scope, budget, scheduling, isolation

### 5.1 Scope **[operator-default, config-overridable]**

`scope: full_asset` — every slot of every asset gets a test render per enabled model. The dial-down
is `scope: cover_only` — only the cover/hero slot per asset. At current volume (3 IG × 5 slots +
3 LI × 1 slot = 18 slots), `full_asset` ⇒ 36 test images/run; forecast spend
18 × ($0.03 + $0.09) = **$2.16**, inside the $3.00 ceiling. `cover_only` ⇒ 12 images, $0.72.

### 5.2 Budget **[operator-default, config-overridable]**

`max_usd_per_run: 3.00` is a **separate test wallet**, enforced with the existing mechanics:

- Test spend is accounted in its own accumulator (`spent_usd_test`), checked via the existing
  `check_caps` helper (run-USD dimension only) **before every test submission**. When the next
  submission's `route.price_usd` would exceed the ceiling, that render and **all remaining** test
  renders are skipped with one `trace.decision` naming the cap, the count skipped, and the rule
  ("test budget exhausted — canonical work is never skipped for test-budget reasons"). The digest
  notes the skip (§9.3).
- Test spend does **NOT** count toward `per_run_count_cap` / `per_run_usd_cap` (those are canonical
  budgets; letting tests drain them could starve canonical on a resumed run). It **DOES** land in the
  ledger and therefore in `media_spend_usd_for_day` — real money is never invisible to the day
  ceiling. §12 check 6 forces the day cap to be sized for both.
- **Circuit breaker:** test submissions move real credits, so they flow through the same
  balance-reconciliation accounting — `ledger_recorded_usd` includes test spend, `trace.spend` events
  are emitted per test submission with delta semantics. (If test spend were excluded, the
  unexplained-spend breaker would false-trip on the first test render.) A tripped breaker halts test
  submissions exactly as it halts canonical ones.

### 5.3 Scheduling

Test renders run **strictly after** all canonical submission/resolution work in `stage_media` —
`TestRenderRunner` is invoked once the canonical loop completes. Consequences: (a) within a run,
no cap interaction can ever consume budget canonical work needed; (b) the canonical cover image
exists before test renders of the same asset, should a future dial want it as `image_input`.
Test attempts are **single-shot**: `attempt` is always 1; a QA fail on a test render is scoreboard
data (§9), never a regeneration trigger — regeneration would double test spend for zero promotion
evidence.

### 5.4 Failure isolation (binding)

The entire test-render phase runs inside one isolation boundary in `stage_media`: any exception —
transport, API, prompt-build, QA, filesystem — is caught, written as `trace.try_decision`
(except-block-safe writer), counted, and the run proceeds. The stage outcome is an isolated
`TestRenderResult` (submitted / succeeded / failed / skipped-budget / skipped-disabled counts +
per-failure reasons) carried to the digest. A test failure can never change any canonical asset's
status, the pack manifest, or the run's exit class. Individual govern() failures on a test prompt
(gate block, leak finding) are recorded per (slot, model) as `blocked — governance` scoreboard rows —
no ledger row is written, mirroring the canonical $0 pre-submission returns.

---

## 6. Output layout & provenance

Canonical outputs stay **exactly** where they are today
(`pack/media/<cluster_key>_<destination>/<slot>.png` + `<slot>.provenance.yaml`). Test renders land
beside them, namespaced by model:

```
pack/media/<cluster_key>_<destination>/
  hero.png                        # canonical (unchanged)
  hero.provenance.yaml            # canonical (unchanged)
  models/
    gpt-image-2-text-to-image/
      hero.png
      hero.provenance.yaml
    nano-banana-pro/
      hero.png
      hero.provenance.yaml
```

- Folder name is the exact `model_string`, with any path-hostile character (`/`, `\`, `:`) replaced
  by `_` (deterministic; both current strings are already clean). `<slot_basename>` matches the
  canonical slot file names (`hero`, `slide_01` …).
- The sibling `<slot_basename>.provenance.yaml` uses the **same schema** as the canonical
  provenance document (asset_id, cluster_key, destination, slot, language, status, requested_route,
  requested_model, requested_aspect, price_snapshot_date, task_id, checksum_sha256,
  observed_cost_usd, image_path, prompt_pattern_version, prompt_sha256, prompt_full, attempt,
  created_at, qa) **plus**: `route_id`, `tier: test`, `resolution`, `full_text_render: true`,
  `expected_text` (the exact span list QA compared against), `delivered_model` (the `recordInfo`
  echo — the three-state model-identity rule from the registry header applies to test rows too and
  any divergence is recorded, not trusted). Written with `fsutil.atomic_write_text`.
- **Packaging must never pick these up**: the packaging slot enumeration reads only top-level
  `<slot>.png` files of an asset dir; the `models/` subtree is explicitly excluded (acceptance
  criterion A7). Test renders ship to the operator as files on disk + scoreboard, never as pack
  deliverables.

---

## 7. Ledger identity — `model_string` joins the tuple

### 7.1 The widened identity

The write-ahead identity tuple becomes:

```
(theme, run_date, cluster_key, asset_slot, language, prompt_pattern_version, attempt, model_string)
```

so a canonical row (`nano-banana-2`) and the two test rows for the same slot can never collide, each
remaining its own at-most-one-paid-submission-ever unit. Spend reconciliation
(`creditsConsumed` → `observed_cost_usd`) stays per-row, unchanged. The
`RENDER_CONTRACT_SPEC.md` §8 guard 4 (prompt_sha256 comparison on an existing-row hit → fail closed,
never reuse a stale image) now applies **per (slot, model)** — a re-crafted test prompt against an
existing test row blocks that model's test render for the slot; it never blocks the canonical row or
the other model's row.

`Store.find_media_intent` and the intent-insert path gain the `model_string` identity parameter
(the insert already writes the column; the lookup must now filter on it).

### 7.2 Migration note — reality differs from the obvious guess

**The `model_string` column already exists** (`store.py:161`, `TEXT NOT NULL`, populated on every
insert since M4) — there is no column to add and no backfill to synthesize: every existing row
already carries the canonical model string it was submitted with. What changes is the **UNIQUE
constraint** (`store.py:182`), and SQLite cannot alter an inline table constraint, so the migration
is a guarded table rebuild inside `Store._migrate_schema`, following the codebase's
PRAGMA-is-schema-truth discipline:

1. Detect: inspect `sqlite_master.sql` for `media_intents`; if the UNIQUE clause already ends in
   `model_string`, do nothing (idempotent re-open).
2. Rebuild: `CREATE TABLE media_intents_new (…identical columns…, UNIQUE(…, attempt, model_string))`;
   `INSERT INTO media_intents_new SELECT * FROM media_intents;` (loss-free — same column set);
   `DROP TABLE media_intents; ALTER TABLE media_intents_new RENAME TO media_intents;` recreate the
   three indexes. One transaction.
3. `PRAGMA table_info` + the `sqlite_master` check remain the truth mechanism; the `schema_version`
   bookkeeping row records intent only.

Old rows keep their original identity semantics — widening the tuple cannot merge or split existing
rows because every historical (old-tuple) group holds exactly one `model_string` value already.

---

## 8. Idempotency / resume

1. **Write-ahead unchanged in shape.** A test-render intent row (state `intended`, `tier`-implied via
   `route_id`, expected costs from the route snapshot) is committed **before** the `createTask` HTTP
   call. Crash between commit and HTTP ⇒ on restart the row is found by the widened identity and
   resolved by query (`recordInfo` via stored `task_id`, or closed as never-submitted per the
   existing subcase logic) — never resubmitted. No new money can move for an existing
   (identity, attempt, model) row.
2. **prompt_sha256 guard per (slot, model)** — §7.1. Mismatch ⇒ that test render is blocked with a
   `trace.decision`; scoreboard row reads `blocked — identity exhausted`.
3. **Phase-0 adoption filter.** The canonical unresolved-intent adoption pass (`_resolve_one_row`
   Phase 0) must filter to rows whose `route_id` resolves to a **non-test** tier. Unresolved *test*
   intents are adopted by `TestRenderRunner` itself: resolved by query, spend-reconciled, filed into
   `models/<model_string>/`; if `test_render.enabled` is now false, they are still **resolved and
   reconciled** (money already moved) but no new test submissions occur. A test row can never be
   adopted into a canonical slot — the tier filter enforces what the model-string tuple already
   makes collision-impossible.
4. **Resume ordering.** On `--resume`, canonical resolution still runs first; the test phase then
   resumes exactly like a fresh phase (existing rows resolved, missing ones submitted, budget check
   counts already-recorded test spend for the run so a resumed run cannot double the wallet).

---

## 9. QA and the per-model scoreboard

### 9.1 N-E vision QA on EVERY test render

Each successfully downloaded test image gets one N-E vision-QA call (same node, same provider path as
canonical QA):

- **`text_matches`** against the slot's expected exact text — the full gated `on_image_text` spans.
  The QA prompt must **explicitly instruct diacritics-sensitive comparison for Czech**: háčky and
  čárky are load-bearing (`š`≠`s`, `ř`≠`r`, `é`≠`e`); a dropped or substituted diacritic is a
  text-accuracy FAIL, not a near-match. This is precisely the localization claim the
  nano-banana-pro marketing page makes — the test exists to verify it.
- **Gibberish check** — any invented/garbled text anywhere on the card.
- **Style adherence** — palette (the recipe's hexes, allowing photographic tolerance), type intent,
  layout vs the asset's style system.

QA calls draw from a dedicated reserve `test_render.qa_reserved_calls`
**[operator-default, config-overridable]** — sized at 40 for `full_asset` (36 needed at current
volume) — so test QA can never starve the canonical `llm.qa_reserved_calls` pool. If the test-QA
reserve runs dry mid-phase, remaining test renders keep their images but carry
`qa: skipped-test-qa-budget` in provenance and count as *unassessed* on the scoreboard — never as
passes.

### 9.2 Scoreboard metrics (per model, per run)

| Metric | Definition |
|---|---|
| `text_accuracy_rate` | text_matches passes ÷ QA-assessed renders |
| `qa_pass_rate` | overall QA pass ÷ QA-assessed renders |
| `avg_cost_usd` | mean `observed_cost_usd` over resolved submissions (reconciled, not snapshot) |
| `failure_count` | provider fails + transport fails + governance blocks + budget skips (each sub-counted) |
| `renders` | submitted / succeeded / unassessed counts |

`aggregate_scoreboard()` computes this from the test provenance YAMLs + ledger rows (never from
in-memory state, so a resumed run scores correctly) and writes
`<run_dir>/test_render_scoreboard.yaml` via `fsutil.atomic_write_text`.

### 9.3 Digest

The run digest gains a "Model test scoreboard" section: one row per model with the §9.2 metrics,
plus the canonical pipeline's own rows for the same slots — after the flip that is **two** anchor
rows: `gpt-image-2-text-to-image`'s own canonical renders (the incumbent) and the
Pillow-composited fallback rows (text-perfect by construction), plus any budget-skip / failure notes from
`TestRenderResult`. **The scoreboard is the promotion evidence** — §10.

---

## 10. Promotion path (documented here, NOT built in W8-11)

Flipping the canonical pipeline to a test model is a **config change, gated on evidence + operator
sign-off**, never an automatic act:

1. Evidence: scoreboard across ≥ N runs (operator judgment; suggested ≥ 3 runs / ≥ 50 test renders)
   showing text-accuracy and QA pass rates at or above the canonical path's, at acceptable cost.
2. Operator sign-off recorded in `DECISION_LOG.md`.
3. Registry edit: the promoted model gets a **new** route at a canonical tier (`standard`), with
   live-verified pricing; `route_by_class`/defaults point at it. The `test`-tier route may then be
   retired or kept for the next candidate. Whether Pillow compositing remains in front of a
   promoted full-text model is its own decision at promotion time (the scoreboard's
   model-vs-composited comparison is exactly the input to it).
4. Auto-promotion, scoreboard-driven route flipping, and `image_input` reference plumbing (§4.6) are
   **out of scope** for W8-11.

---

## 11. Config surface added (`config/themes/hypedigitaly.yaml`)

All keys optional with safe defaults (`enabled: false` when the block is absent — a theme predating
this spec runs canonical-only). Every value below is **[operator-default, config-overridable]**.

```yaml
generation:
  media:
    test_render:
      enabled: false                  # ROUND-4/5: single-model production (PLAN §13 item 22.3).
                                      # Everything below is present, coherent and checked so that
                                      # flipping this to true is a one-line change — but see §12.10:
                                      # enabling it also requires raising llm.per_run_call_cap.
      models: [nano-banana-pro, nano-banana-2]   # the two CHALLENGERS; must each match exactly one test-tier route's model_string (§12.1)
      scope: full_asset               # full_asset | cover_only  (§5.1)
      max_usd_per_run: 3.00           # separate test wallet (§5.2); canonical caps untouched
      resolution: "1K"                # default request resolution; auto-pinned to "1K" where a
                                      # route's resolution_constraints forbid the destination aspect
                                      # at 2K/4K (gpt-image-2 × IG 4:5 — hard API constraint)
      qa_enabled: true                # N-E vision QA on every test render (§9.1)
      qa_reserved_calls: 40           # dedicated test-QA reserve — never drawn from llm.qa_reserved_calls
```

`TestRenderConfig` is a frozen dataclass in `config_load.py`, loaded by
`load_theme_generation_config` with the same optional-keys idiom as every `GenerationConfig` field.

---

## 12. Consistency checks (registry + config load time — the run refuses to start on contradiction)

Added to `load_model_registry` and to `check_contract_consistency`'s call site (fail-closed,
`ConfigError`, each error names both offending sources):

1. **Unknown model string.** Every entry of `test_render.models` matches exactly one registered
   route's `model_string`, and that route's tier is `test`.
2. **Capability/aspect conflict.** For every enabled destination × enabled test route: the
   destination's aspect (from `media.aspect_ratio_by_destination`) must be a supported aspect for
   that route, and if the configured `test_render.resolution` conflicts with the route's
   `resolution_constraints` for that aspect, the pin-to-1K rule must resolve it — an aspect
   unsupported at *every* resolution is a `ConfigError` (nothing may silently skip at run time that
   config could have refused at load time).
3. **Test tier never canonical.** No `test`-tier route may appear in any `route_by_class` value,
   `defaults.draft_route`, or `defaults.fallback_draft_route`. (Belt to §3.1's runtime braces.)
4. **Budget cap sanity.** `test_render.enabled` ⇒ `max_usd_per_run > 0`, `models` non-empty, and
   `max_usd_per_run ≥ min(route.price_usd over enabled test routes)` — a ceiling below the cheapest
   single render means nothing would ever render, which is a config contradiction, not a dial.
5. **Full-text capability.** Every route named in `test_render.models` has
   `full_text_render: true` — the full-text embed is the entire point of the test.
6. **Day-cap headroom.** `per_day_usd_cap ≥` (canonical forecast per RENDER_CONTRACT §4 check 6's
   paid-image count × route price) `+ test_render.max_usd_per_run` — test spend lands in day spend
   (§5.2) and must not be able to starve tomorrow-morning's canonical run by config design.
7. **QA budget feasibility.** `qa_enabled` ⇒ `test_render.qa_reserved_calls ≥` expected test renders
   (scope-derived slot count × len(models)); and the global `llm.per_run_call_cap` covers
   non-QA estimate + `llm.qa_reserved_calls` + `test_render.qa_reserved_calls` (extends
   RENDER_CONTRACT §4 check 8).
8. **Registry hygiene — AMENDED (round-4/5).** The original rule ("no two routes share a
   `model_string`") cannot survive the role inversion: `nano-banana-pro` and `nano-banana-2` are each
   legitimately a **reserved canonical** route *and* a **test-tier challenger**. The rule becomes:
   **no two routes of the same tier class may share a `model_string`; a `model_string` may appear on
   at most one canonical-tier route and at most one `test`-tier route, and when it does, the registry
   comment block must state the dual role.** The ledger consequence is handled by
   `TestRenderRunner`'s **skip rule** — before submitting for (slot, model), skip if a *canonical* row
   already exists for that (slot, `model_string`) — so "one row per (slot, model)" (T4) is preserved
   without widening the identity tuple. `model_string` remains the **only** approved widening, ever.
   Unchanged: every `test`-tier route defines the capability fields it is consumed through
   (`full_text_render`, `image_input_max`, `prompt_max_chars`); `price_usd ≈ price_credits ×
   meta.credit_usd` within rounding.
9. **Reserved-route hygiene (new).** No `status: reserved` route appears in any `route_by_class`
   value or in `defaults.*`; `resolve_route()` refuses it at runtime; and a reserved route must still
   satisfy every other check in this section, so it can never rot into config that would fail the day
   someone flips it to `active`.
10. **Disabled-track arithmetic (new).** When `test_render.enabled: false`, checks 4, 6 and 7 treat
    the test terms as **zero** — but the block's values must still be internally coherent (models
    resolvable, `max_usd_per_run > 0`, reserve sized for the scope), so enabling it is a one-line
    change and never a debugging session. Check 7's global term then becomes
    `llm.per_run_call_cap ≥ non-QA estimate + llm.qa_reserved_calls + test_render.qa_reserved_calls`
    **with the third term counted only when enabled** — flipping the flag without raising the cap
    makes the run **refuse at load time**, which is the intended, stated behaviour.

---

## 13. Acceptance criteria

Unit (pytest, `FixtureFetcher`/`QueuedFetcher` doubles, `tmp_path` — no new harness):

- **U1** `resolve_route` raises on a `test`-tier route id regardless of `tier_ceiling`;
  `resolve_test_route` raises on any non-`test` route.
- **U2** `build_test_render_prompt` output contains every `on_image_text` span verbatim inside
  `<<…>>`, the style recipe's hexes, and GUARDRAILS; raises when built length > `prompt_max_chars`.
- **U3** `govern()` on a test prompt: full-text embed passes text-set closure; an invented span
  fails; a gate-blocked numeral blocks submission with no ledger row written.
- **U4** Input construction: IG 4:5 on `img-test-gpt-image-2` pins `resolution: "1K"` even when
  config says `"2K"`; LinkedIn 16:9 honours the configured resolution; `nano-banana-pro` sends
  `output_format: "png"` and no `image_input`.
- **U5** Store migration: a DB created with the old UNIQUE opens, is rebuilt once (idempotent on
  re-open), preserves all rows, and afterwards accepts two rows differing only in `model_string`
  while still refusing a duplicate of the full widened tuple.
- **U6** QA prompt for a Czech-language slot contains the diacritics-sensitivity instruction and
  the exact expected spans.
- **U7** Consistency checks: each of §12.1–.7 has a fixture config that raises `ConfigError` naming
  both sources.

Integration (fixture-driven full `stage_media` runs):

- **A1** A run with `test_render.enabled: true`, 2 models, `scope: full_asset` produces N canonical
  images in their unchanged locations **plus 2N test images** under
  `<asset_dir>/models/<model_string>/<slot_basename>.png`, each with a provenance sibling carrying
  `tier: test`, `route_id`, `prompt_sha256`, `expected_text` and QA verdict.
- **A2** Ledger holds one row per (slot, model): canonical + 2 test rows per slot, keyed by the
  widened tuple; spend reconciliation recorded per row; `find_media_intent` distinguishes them.
- **A3** Budget-cap skip: with `max_usd_per_run` sized to trip mid-phase, remaining test renders are
  skipped with a single decision event, canonical assets are all untouched/delivered, and the digest
  names the skipped count. Canonical is never skipped for test-budget reasons.
- **A4** Failure isolation: an injected provider failure (and separately, an injected exception) in
  the test phase leaves the run's exit class and every canonical asset status unchanged; the digest
  carries the failure note; `trace` shows `try_decision` for the exception path.
- **A5** Scoreboard: the digest contains a per-model table with text-accuracy rate, QA pass rate,
  avg cost/image and failure count consistent with the fixture QA verdicts;
  `test_render_scoreboard.yaml` agrees with it.
- **A6** Resume: kill after a test intent row is written but before resolution; restart resolves by
  query with zero new submissions for that identity; a changed test prompt for an existing (slot,
  model) row blocks instead of resubmitting or reusing.
- **A7** Packaging output for a run with test renders present is byte-identical in manifest terms to
  the same run without them — nothing under `models/` is ever referenced by the pack manifest or
  delivery.

---

## 14. What this spec does NOT change

- **Delivery & packaging.** The deliverable pipeline (after the round-4/5 flip: `gpt-image-2`
  full-design renders with the Pillow-composited fallback rung), the pack
  manifest, and packaging's slot enumeration are untouched; `models/` subtrees are invisible to it.
- **Canonical QA gating.** N-E verdicts on canonical slots keep their existing gating/regeneration
  semantics; test QA gates nothing.
- **The claim gate itself.** Lexicons, `run_claim_gate` signature, abstain behaviour — unchanged
  (the Wave-II co-location change is owned by RENDER_CONTRACT/PLAN, not here).
- **KieClient.** Transport, tracing, redaction discipline unchanged; only one allowlist key
  (`resolution`) is added.
- **Canonical ledger semantics.** Existing rows, `prompt_pattern_version` policy, attempt semantics
  and the no-widening-beyond-`model_string` rule (widening further would authorise unbounded
  re-spend) — unchanged.
- **Copy authoring.** N-A/N-C/N-D/N-F prompts, token budgets and validators — untouched; the test
  prompt is assembled downstream of gated copy, not authored.
- **tiktok** stays configured-but-disabled (`destinations_enabled`) — no test renders are planned or
  spent for a disabled destination.
- **No auto-promotion**, no `route_by_class` changes, no `image_input` plumbing (§10, §4.6).

---

## 15. Invariants owned by this spec

| ID | Statement | Enforced at | Test |
|---|---|---|---|
| **T1** | A `test`-tier route is unreachable from every canonical resolution path, and vice versa. | `resolve_route` / `resolve_test_route` + §12.3 | U1, U7 |
| **T2** | Test renders never alter any canonical asset status, pack content, or the run's exit class. | §5.4 isolation boundary | A4, A7 |
| **T3** | Every test-render byte submitted passed the same `govern()` gate as canonical bytes; one choke point. | I1's AST guard extended to the test call path | U3 |
| **T4** | One ledger row per (identity, attempt, model); canonical and test rows can never collide, and the prompt_sha256 guard applies per (slot, model). | widened UNIQUE + §8.2 | U5, A2, A6 |
| **T5** | Test spend can exhaust only its own wallet; canonical work is never skipped for test-budget reasons; all test spend is visible to the day cap and the circuit breaker. | §5.2 accounting | A3 |
| **T6** | A test render without an assessed QA verdict is never counted as a pass. | §9.1 skip semantics | A5 |
