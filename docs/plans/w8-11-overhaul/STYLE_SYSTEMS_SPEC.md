# STYLE SYSTEMS SPEC — W8-11

*Companion to `RENDER_CONTRACT_SPEC.md` and `FINDINGS_SYNTHESIS.md` §5. Authored 2026-08-07. This
document is a SPEC, not code: it proposes the `VisualPolicy.style_system` values, the
`config/style_guide.yaml` amendment that defines them, the selection rule that resolves
`style_system` per asset, and the enforceable checks that keep an asset from drifting off the system
it was assigned. An executor implements the amendment against the live `config/style_guide.yaml`; a
reviewer checks the acceptance criteria in §8. No code or YAML in this file is live config — it is the
full, implementable content for the "full specs" that `FINDINGS_SYNTHESIS.md`'s §5 table promised and
that no surviving workstream report ever wrote down.*

***ROUND-2 AMENDMENT (2026-08-07, operator-approved, binding).*** *Same-day expansion from six style
systems to eleven, plus one recorded rejection, implementing seven operator-locked decisions: (1) serif
vendoring — Playfair Display (display, incl. italic cuts) + Lora (body), both SIL OFL, §3.5, with
editorial body text switching from sans to serif; (2) `ig_value_sheet` (§2.9, recipe from
`reference/aisimplified23/DESIGN_DECONSTRUCTION.md` §C); (3) three photoreal/grotesque systems —
`ig_lifestyle_stack` (§2.10), `ig_scene_hook`/`li_scene_hero` (§2.11/§2.12), `ig_operator_grid`
(§2.13) — recipes from `reference/visual-formats/DESIGN_EXPANSION.md` §B, with `li_product_render`
REJECTED and the rejection recorded (§2.14); (4) five anti-ad Hard DON'Ts (§5.6–§5.10); (5) round-1
refinements — warmed paper `#F1ECE1` + grain spec, optional `inline_artifact_card`/`icon_zone`/
`checkbox_style` body-slot additions, optional `end_card_override: artifact_close`, and the composited-
cover `max_spans` relaxation (§2 conventions, §3.1); (6) accent governance (§3.6); (7) Virlo-driven
two-stage format selection with a per-run variety quota (§4, full rewrite). A same-day operator policy
change additionally REVERSES the round-1 logo mechanism: third-party marks are now diffusion-first,
QA-gated, with a URL-manifest composite fallback — no bundled logo library (§2's logo-policy block,
§5.11). Net-new build dependencies introduced by this amendment, each flagged inline where it binds:
font vendoring (§3.5), rich-text run styling inside one zone (§2.13's emphasis run and §3.1's
`headline_split` — one capability, two consumers), the photoreal reserved-zone ground flow in
`grounds.py` (§2.10–§2.12), and the logo pipeline (N-E `logo_fidelity_ok` rubric addition,
`assets/logos/manifest.yaml` + lazy-fetch/cache helper, composite-repair + QA re-run path — §2's
logo-policy block, §5.11).*

***ROUND-4/5/6 AMENDMENT (2026-08-07/08, operator-ratified, binding — `PLAN.md` §13 items 19-25).***
*Six changes, all evidenced by the 44-render simulation (`simulation/SIM_REPORT.md`, F8-F20) and the
operator's ten hand-picked favourites:*

1. ***The rendering flip.*** *Canonical rendering is a **`gpt-image-2-text-to-image` FULL-DESIGN
   render** — the model draws the finished card, expressive typography included — verified per glyph
   against the gated `on_image_text`, retried once, and only then composited by Pillow. **Every
   "fully programmatic" and "diffusion-TEXT surface is exactly two covers" statement below is
   superseded** (see §2.7's amended totals): every slot of every system is now a canonical render,
   and the ≤2-span/≤6-word diffusion-text cap is **lifted**, not universalised. Wave 0 task 0-6
   sweeps the residual wording.*
2. ***`reference/OPERATOR_FAVORITES_DNA.md` is NORMATIVE style direction*** *for every recipe and
   every template prompt in this document — rules **D1** (grounds: warm cream `#F6F1E7` default,
   cinematic-dark secondary, nothing in between), **D2** (two type voices only, oversized, EXACTLY
   one brand-colour emphasis token — teal default, indigo-italic for serif, amber for
   numerals/times), **D3** (caps kicker + `HYPEDIGITALY` wordmark footer on every card class),
   **D4** (artifact device library, real marks only), **D5** (pinned recurring brand characters),
   **D6** (concrete specifics in copy).*
3. ***Eighteen new entries, nine new shapes*** *(§2.15-§2.22) — library total **twenty-nine**
   (27 organic + 2 promotional).*
4. ***Selection is re-weighted and gains two reserved slots*** *(§4.1) — plus an evidence-gated
   **carousel decision**: Instagram assets are single-image unless Virlo slideshow evidence clears
   the same floor the format reweight uses.*
5. ***`ig_value_sheet`'s default ground moves from dark terminal to the cream serif-editorial
   recipe*** *(DNA anti-signal: the dark dense list card was the one technically-clean render the
   operator did not pick). Its zone geometry, `type_floor` and `value_sheet_max_words` are unchanged.*
6. ***Language is per-destination config, default `en`*** *(`cs` a supported switch), so every
   "Czech" statement below reads as "the asset's configured language".*

---

Governing decision this document inherits from `RENDER_CONTRACT_SPEC.md` §2: `VisualPolicy` already
carries `style_system: str` as a field independent of `mode`/`archetype`/`register`
(`RENDER_CONTRACT_SPEC.md:70-77`). This document defines what goes in that field, and nothing here
contradicts the `RenderContract`/`ConstraintSet` machinery that spec already locked — every word cap,
span cap, and slot role below is the SAME number `RENDER_CONTRACT_SPEC.md` §7's config surface
already names; this document adds the palette/type/texture/layout recipe on top, keyed by
`style_system` rather than by `mode`/`archetype`/`register` alone (those three stay as they are today,
reused wherever possible — see §2's per-system "keys" line and §4).

---

## 0. Scope, sources, and one clarification on slot roles

**In scope (round 2):** the three named topics from `FINDINGS_SYNTHESIS.md` §5 and their six style
systems (one LinkedIn + one Instagram each), PLUS the five round-2 systems (§2.9–§2.13). The round-2
systems are format-generic, not topic-bound, so §4's rewritten two-stage selector now covers EVERY
topic on `linkedin`/`instagram_feed`: an unmatched topic no longer falls to the W8-10 Phase 8 rotation
on those two destinations — it falls to its assigned format class's default system (§4.1 step 7).
**Out of scope:** TikTok (its own `dark-hype-poster`/`ugc-photo-caption`/`editorial-carousel` rotation
is untouched; `style_guide.yaml:98-105`) and any destination outside {linkedin, instagram_feed} —
those keep the existing W8-10 Phase 8 dynamic-inspiration rotation (`promptcraft.GENERATION_MODES`,
`_candidate_modes_from_visual_profile`, `promptcraft.py:444-581`) completely unchanged. The Phase-8
rotation also remains the loaded-and-working degrade path for a theme whose config predates
`generation.format_quota` (§3.4, §4.1 step 0).

**Slot roles used below.** `RENDER_CONTRACT_SPEC.md` §7's config literals are the only role vocabulary
that exists today: `hero` (LinkedIn, single slot) and `cover` / `body` / `prompt_quote` / `end_card`
(Instagram, `RENDER_CONTRACT_SPEC.md:317,323-327`). The task brief that commissioned this document
also lists `checklist` as a possible role — **it is not a `SlotRole`.** A checklist (rows of ✓ + short
line) is a *content pattern applied inside a `body` slot*, not a new slot kind; §2 marks which systems'
`body` slots use it. This keeps `asset_model.SlotRole` (owned by the not-yet-written
`SLOT_MODEL_SPEC.md`) at the five values `RENDER_CONTRACT_SPEC.md` already committed to.

**Canvas conventions used throughout §2** (single source: `generation.media.aspect_ratio_by_destination`,
`config/themes/hypedigitaly.yaml:358-363`):

| Destination | Aspect | Reference canvas | % basis below |
|---|---|---|---|
| `linkedin` (hero) | `16:9` | 1920×1080 | all `%` = % of the 1080px canvas **height** unless marked "of width" |
| `instagram_feed` (5 slots) | `4:5` | 1080×1350 | all `%` = % of the 1350px canvas **height** unless marked "of width" |

**Safe zone (ALL systems, round 1 and round 2, no exceptions):** `margin_percent = 12` — the existing
`DEFAULT_MARGIN_PERCENT` (`promptcraft.py:104`), i.e. every text block, inset, and the handle stay
fully inside a 12%-of-canvas inset on all four sides, exactly as `_build_style_section` already states
(`promptcraft.py:375`). **Handle:** small, subtle, bottom-right corner — `DEFAULT_HANDLE_CORNER`
(`promptcraft.py:105,376`) — every slot, every system.

**Font gap (read before any type scale below).** `assets/fonts/` contains exactly one file,
`NotoSans-Variable.ttf` (variable weight/width, full Czech/Latin-Extended coverage per
`assets/fonts/README.md:9,13-15`). `style_guide.yaml:195` names **Montserrat** as the brand typeface,
and `RENDER_CONTRACT_SPEC.md:333` names `assets/fonts/Montserrat-Variable.ttf` as the compositor's
font path — **neither exists in the repo.** Two of the round-1 systems below (Editorial Brief, Prompt
Sheet) also want a serif display face and a monospace face respectively — **neither exists in the repo
either.** Every type scale in §2 therefore names an *intended* family and a *concrete, currently-true*
fallback; §4's config-consistency check (`RENDER_CONTRACT_SPEC.md` §4 item 7) already fails the run
closed if `compositing.font_path` doesn't resolve — this document does not relax that; it tells the
executor what ships in the interim (Noto Sans only) versus what an acquired-font follow-up unlocks.
**Round-2 update:** the serif acquisition is now DECIDED, not open — Playfair Display (display, incl.
italic cuts) + Lora (body), both SIL OFL 1.1, vendored into `assets/fonts/` (§3.5). Every "intended
serif" below now means those two families; the concrete in-repo fallback remains
`NotoSans-Variable.ttf` until the vendoring task lands AND the Czech-diacritics glyph verification
(`assets/fonts/README.md`'s protocol, re-run on the vendored files) passes. Montserrat remains the
intended sans for every non-serif-editorial system — still not in-repo, an unchanged gap.

---

## 1. Shared vocabulary

| Term | Meaning |
|---|---|
| **register** | `visual_registers.<key>` (`style_guide.yaml:162-190`) — governs the coarse photographic-vs-typographic-card boundary and feeds `_build_style_section`'s branch (`promptcraft.py:335-347`). The six round-1 systems plus §2.9/§2.13 bind `register: editorial`; the three photoreal round-2 systems (§2.10–§2.12) bind `register: photographic_ugc` (existing key inside `visual_registers`, `style_guide.yaml:162-190` — no new register anywhere in this document). |
| **archetype** | `visual_archetypes[*].key` (`style_guide.yaml:108-160`) — a named creative pattern; reused wherever possible (§2 states the mapping per system). |
| **generation_mode** | `promptcraft.GENERATION_MODES[*]` key (`promptcraft.py:455-534`) — supplies the `composition_directive` threaded into N-D's RENDER brief (`promptcraft.py:867-869`). |
| **style_system** | THIS document's new key — `VisualPolicy.style_system` (`RENDER_CONTRACT_SPEC.md:77`). One of eleven string ids (§2 headers). Carries the concrete palette/type/ground/layout recipe that `register`+`archetype` alone under-specify — see the worked example under §3.1. |
| **format_class** | Round-2 field on every `style_systems[*]` entry — one of `designed_card` \| `photoreal` \| `editorial_grotesque` \| `serif_editorial`. Consumed ONLY by §4's stage-1 per-run variety quota; it never appears in a prompt and never reaches N-D. Assignments and class defaults: §4.1's table. |
| **ground_source** | **Panel edit (W8-11 review):** moved off `RenderPolicy` onto `SlotSpec.ground_source` — it is a per-slot property, not one value for a whole asset (an Instagram carousel's `cover` may diffuse while its `body`/`prompt_quote`/`end_card` stay programmatic in the same asset). `"programmatic"` (Pillow/HTML-CSS renders the exact hex/texture, zero diffusion call, zero gibberish risk), `"diffusion"` (Nano Banana 2 generates a scene), or `"auto"` (unused by any system in this document, round 1 or round 2 — every slot below picks one explicitly, and §3.1's YAML already places `ground_source` inside each `slots.<role>:` entry, never at the system's top level). |
| **text_render_mode** | `SlotSpec.text_render_mode` (`RENDER_CONTRACT_SPEC.md:43`) — `"composited"` (this engine typesets the text, real font, exact bytes, zero OCR risk) or `"diffusion"` (Nano Banana 2 renders the text itself; capped at `diffusion_text_max_spans=2`, `diffusion_text_max_words_per_span=6` — `RENDER_CONTRACT_SPEC.md:84`, and HARD FACTS). Only `cover` slots use `"diffusion"` anywhere in this document. |

**A note on why `archetype` is reused but not `ModeSpec.archetype`.** Five of the six round-1 systems
below (and round 2's §2.9) name `mode: designed_card`. `GENERATION_MODES["designed_card"].archetype` is `None` by design
(`promptcraft.py:526-533`) — it defers to `_legacy_pick_archetype_register`'s asset-index rotation
(`promptcraft.py:386-425`). Because `VisualPolicy.archetype` is its own field, independent of `mode`
(`RENDER_CONTRACT_SPEC.md:73`), the resolver rule in §4 below **pins** `archetype` directly from the
`style_systems` table whenever a `style_system` is matched, bypassing the rotation entirely for that
asset. This requires no change to `GENERATION_MODES` — `designed_card`'s `composition_directive`
("the existing designed typographic-card composition for this archetype/register" — `promptcraft.py:529-532`)
is generic on purpose and remains correct regardless of which archetype is pinned. Round 1 needed
exactly one new `GENERATION_MODES` entry (`annotated_proof_ui`, §2.2). Round 2 adds two more —
`cinematic_scene_hook` (§2.11) and `grid_photo_inset` (§2.13) — plus a directive AMENDMENT to the
existing `aspirational_lifestyle_scene` entry (§2.10); each is flagged explicitly in place, with the
full proposed `ModeSpec` text, exactly as §2.2 does.

---

## 2. The style systems — six round-1 (§2.1–§2.6), five round-2 (§2.9–§2.13), one rejection (§2.14)

**Zone contract (reviewer edit — the layout tables below are now machine-readable, not just prose).**
Every per-slot layout table in this section is followed by a `zones:` block in the exact shape
`layout.py` loads (`COMPOSITING_SPEC.md` §4.3's `SlotZone`/`LayoutRecipe`). Conventions, fixed for all
systems, round 1 and round 2 alike:

- `rect_pct: [x, y, w, h]` — fractions of the FULL canvas width/height (not the margin-reduced safe
  rect `COMPOSITING_SPEC.md`'s `compute_safe_rect` derives internally) — matching this document's own
  §0 Y-band/X-band convention, so every number below is a straight percent-to-fraction conversion of
  the table above it. *Reconciliation note for the executor:* `COMPOSITING_SPEC.md`'s own `RectPct` is
  currently specified as a fraction of the safe rect, not the full canvas — that spec's executor
  reconciles the basis (full-canvas fractions here are the source of truth; `layout.py` converts once
  at load time) rather than this document silently picking a different basis than the sibling spec.
- `type_scale` is a single float — the LARGEST size to try, as a fraction of canvas height
  (`fit_text`'s largest-first shrink loop, `COMPOSITING_SPEC.md` §4.4, starts here and only shrinks
  below it if the string doesn't fit).
- `weight` ∈ `{Regular, Medium, SemiBold, Bold}` — Bold entered with round 1's `li_statement_hero` and
  `ig_stat_slab` (§2.3/§2.4, oversized numerals); several round-2 systems (§2.9, §2.11, §2.13) use it
  too, so the "only two systems" note is historical. Italic is NOT a `weight` value: where a system
  intends an italic cut (Playfair Display Bold Italic, §3.5), the italic-ness is carried by the named
  font FILE in `type.display_family`, never by a zone field — zone `weight:` continues to drive only
  the variable-weight axis of whichever file is actually loaded (incl. the NotoSans fallback).
- Every zone entry maps onto `OnImageText`'s three-field schema (`kicker`/`title`/`body` —
  `COMPOSITING_SPEC.md`'s `SlotZone.field` enum) by name: the slot's single dominant text (`headline`,
  `numeral`, `cta`, `prompt_text`) → `title`; a short label sitting above it (`eyebrow`, `kicker`) →
  `kicker`; everything else (`qualification`, `supporting_line`, `attribution`, `subtext`) → `body`.
  `layout.py` groups same-`field` zones by declaration order when a role needs two `body`-mapped zones
  (e.g. `li_statement_hero`'s eyebrow-less body has only one; `ig_annotated_proof`'s checklist body is
  one multi-line zone, not several).
- **Required zone names per `SlotRole`** (checked at recipe-registration time, not just documented
  here): `cover` → at least one zone literally named `headline` (used directly when that cover's
  `text_render_mode: composited`; when `text_render_mode: diffusion`, the SAME rect is instead handed
  to `grounds.request_reserved_zone_prompt_fragment` as the reserved text region, so one number governs
  the cover's text position regardless of which route the slot takes). `end_card` → at least one zone
  named `cta`. `hero` (LinkedIn, single-slot systems) → at least one zone named `headline`. `body` /
  `prompt_quote` → at least one zone named `body`. No other zone name is constrained; supporting zones
  are named descriptively per system, per the mapping rule above.
- Non-text visual elements — a logo lockup, a screenshot inset, a vector accent shape, save/follow
  glyphs — are never a `zones:` entry (`SlotZone` typesets `OnImageText`-gated strings only). They use
  `LayoutRecipe`'s own `logo_zone: RectPct | None` field, or (screenshot insets only, §2.2) the typed
  `screenshot_inset` block defined there. **Zones inside one slot never overlap in `rect_pct`, and every
  `rect_pct` is fully inside `[0,1]×[0,1]`** — spot-checked per system below, not asserted on faith.
- **`max_spans` semantics (round-2 relaxation, operator-locked).** The 2-span cap exists solely to
  bound diffusion-text legibility risk (`diffusion_text_max_spans=2`,
  `RENDER_CONTRACT_SPEC.md:84`), so it binds ONLY where `text_render_mode: diffusion`. For any slot
  with `text_render_mode: composited`, `max_spans` is a *layout property* of the recipe — the recipe
  may define as many zones as its design needs (a composited slot has zero gibberish risk regardless
  of span count), and the values shipped in §3.1 are design choices, not caps. Diffusion covers keep
  ≤2 spans × ≤6 words exactly as before, unchanged and un-relaxable.
- **`reserved_text_zone` (round-2 — case-(b) photoreal slots only).** Every slot with
  `ground_source: diffusion` + `text_render_mode: composited` (`COMPOSITING_SPEC.md`'s case (b))
  declares `reserved_text_zone: RectPct` — the exact bounding rect of that slot's own `zones:`
  entries — which is handed verbatim to `grounds.request_reserved_zone_prompt_fragment` at prompt
  time and to `check_ground_safe_zone` after the ground downloads, so the diffusion scene keeps that
  region plain/low-detail for the compositor. One number governs both the requested negative space
  and where the text actually lands — the same single-rect principle the diffusion-cover convention
  above already applies. This is the `grounds.py` build dependency the preamble names; a safe-zone
  check failure degrades to a programmatic ground (never a re-roll loop), decision-logged per I5.

**Logo rendering policy (round-2 REVERSAL 2026-08-07, EXTENDED by the round-4/5 amendment
2026-08-08 — supersedes every round-1 "composited real PNG asset" logo statement in this section).**

**The hard rule first (`PLAN.md` §13 item 19.B, F8/F13): any slot whose copy names a platform or a
tool MUST render that tool's mark** — as an icon row, an inline chip, or a diagram node. A tool named
in words but absent in pixels is a governance failure (invariant LG2), not a stylistic choice; the
round-2 renders that named tools *and showed their marks* are the ones the operator picked, and the
ones that named them without marks are not.

**Three mechanisms, in this order:**

- **`description:` injection (the workhorse).** `assets/logos/manifest.yaml` carries, per tool,
  `{description, icon_url, source}`. The **verbal mark description** ("Anthropic Claude coral
  starburst", "Zapier orange asterisk", "Gmail multicolour M envelope") is injected into the render
  prompt and took mark fidelity from ~50% (naming alone) to **~95%** (F8) at zero marginal cost.
- **`icon_url:` bytes (the guarantee).** The icon-form PNG — **never the wordmark**; round 2
  reproduced a supplied wordmark faithfully *because the file was a wordmark* — feeds the
  `logo_fidelity_ok` QA comparison and the Pillow composite repair, and fills an `artifact_zone`
  pixel-exact where the design calls for real bytes rather than a rendered impression.
- **The three-tier ladder for tools with no manifest entry** — §5.12.

The QA gate and the fallback below are unchanged in shape; what changed is that the marks are now
described precisely rather than merely named, and that the fallback composites **fetched** bytes:

1. **Primary path:** the image model renders third-party logo marks **in-image** — current models
   (nano-banana-pro / gpt-image-2 class) reproduce well-known marks (n8n, Apify, Claude) reliably.
   The N-D/RENDER prompt names the exact tool and asks for its **accurate official mark**; no bundled
   logo library is required or shipped. For a slot that is otherwise programmatic, the `logo_zone`
   rect becomes a small partial-area diffusion surface (the same partial-area pattern as §2.13's
   `photo_inset`); for a slot whose ground already diffuses, the marks are rendered in that same call.
2. **QA gate:** N-E gains a **`logo_fidelity_ok`** boolean (§5.11) — true only when every depicted
   third-party mark is accurate (correct glyph shape, correct colors, no invented/garbled variant).
   This check NEVER skips when the prompt names a tool logo.
3. **Fallback (only on a `logo_fidelity_ok` failure):** the engine composites a REAL mark instead —
   sourced from a URL manifest (`assets/logos/manifest.yaml`: tool → official brand-asset URL,
   authored during plan execution via websearch), lazily downloaded via `urllib` on first need and
   cached to `assets/logos/cache/`. After compositing the real mark over the SAME `logo_zone` rect,
   QA re-runs. No logo PNGs are committed to the repo up front — a manifest of URLs only.
4. **Unchanged:** the fake-UI Hard DON'T (§5.4 — logos ≠ UI chrome; still never invent
   dashboards/screens) and the nominative-use governance (marks appear only where the copy
   legitimately names the tool; §3.6 for the Claude coral mark specifically).

Two scoping clarifications: (i) this policy covers **third-party** marks only — HypeDigitaly's own
wordmark/handle (e.g. §2.13's masthead `logo_zone`) stays composited from `assets/brand`, zero
diffusion; (ii) a rendered official **wordmark** (e.g. "n8n") is a logo mark, not an `on_image_text`
span — it is policed by `logo_fidelity_ok`, never counted against the ≤2-span/≤6-word diffusion-text
caps.

### 2.1 `li_signal_card` — LinkedIn "Signal Card"

**Topic:** n8n + Apify lead-gen workflow. **Intent:** per the Virlo ground truth
(`FINDINGS_SYNTHESIS.md` §5), winning LinkedIn creatives for an infra/automation topic are a
"Tool + Platform = result" logo-equation card, not a screenshot wall — this is exactly
`visual_archetypes.statement-card`'s own description (`style_guide.yaml:121-122`: "Tool + Platform =
result number... 1-3 real logos"). The card reads in under a second on a feed scroll: two real tool
logos, one connective glyph, one number. It wins because it states the mechanism (n8n → Apify) and the
payoff in one glance, with digits doing the persuasive work — digits are the lowest claim-gate risk
surface in the whole system (a sourced/qualified number, never a superlative).

**Keys:** `register: editorial` (reused) · `archetype: statement-card` (reused, pinned — see §1 note)
· `generation_mode: designed_card` (reused) · destination: `linkedin`, format `single`, one `hero` slot.

**Layout skeleton (`hero` slot, 1920×1080):**

| Element | Y-band (% of height) | X-band (% of width) | Notes |
|---|---|---|---|
| Logo-equation row | 30–42% | 12–88% (safe zone) | tool logo · `+` glyph · tool logo · `=` glyph, left-to-right, all three glyphs the same cap-height as the logos |
| Result numeral/short phrase | 44–62% | 12–88% | the single hero on-image text span |
| Supporting line (optional) | 64–72% | 12–88% | ≤1 line, only if the number needs one qualifying word (e.g. "per workflow run") |
| Handle | 88–94% | bottom-right, inside 12% margin | small, subtle |

**Zones (machine-readable — `layout.py`, canvas 1920×1080):**
```yaml
logo_zone: [0.12, 0.30, 0.76, 0.12]   # tool marks + '+'/'=' glyphs — diffusion-first partial-area surface per §2's logo policy (QA-gated, manifest-composite fallback); glyphs and white chips drawn programmatically
zones:
  - {name: headline, rect_pct: [0.12, 0.44, 0.76, 0.18], type_scale: 0.11, weight: SemiBold, align: left, max_lines: 1, color: "#FFFFFF"}
  - {name: supporting_line, rect_pct: [0.12, 0.64, 0.76, 0.08], type_scale: 0.032, weight: Regular, align: left, max_lines: 1, color: "#FFFFFF"}
```
`supporting_line` is the layout table's "optional" row — an empty string is a valid `on_image_text.body`
for this zone; `layout.py` skips drawing (not error) a declared-but-empty zone.

**Palette (Brand Card recipe):** ground `linear-gradient(135deg, #302B87 0%, #00A39A 100%)` — the
brand's own `palette_primary_gradient` (`style_guide.yaml:194`), exactly as `_build_style_section`
already emits for non-photographic registers (`promptcraft.py:349-350`). Text primary `#FFFFFF`.
Logo tiles: white `#FFFFFF` rounded-rect chips behind each third-party logo (never let a colored logo
sit directly on the gradient — legibility and mark-fidelity both suffer). Connective glyphs (`+`, `=`)
`#FFFFFF` at 70% opacity.

**Type scale:** intended `Montserrat SemiBold` for the numeral/phrase, `Montserrat Regular` for the
supporting line — fallback (today, in-repo): `assets/fonts/NotoSans-Variable.ttf` at variable-weight
630 (SemiBold-equivalent) for the numeral, 400 for the supporting line. Numeral: 9–11% of canvas
height, line-height 1.05, **max 1 line**. Supporting line: 3.2% of canvas height, line-height 1.3,
**max 1 line**.

**Texture/ground:** flat gradient card, `ground_source: programmatic` — Pillow/HTML-CSS renders the
exact two-stop gradient; the ground itself never diffuses. **Under the round-2 logo policy the
`logo_zone` is a partial-area diffusion surface** (the two tool marks, rendered by the image model
against their programmatic white chips), so this system is no longer zero-diffusion — §2.7's census
carries the corrected row.

**Text budget:** `max_title_words: 12`, `max_body_words: 18` (the existing `linkedin.hero` `SlotSpec`,
`RENDER_CONTRACT_SPEC.md:317` — unchanged by this document). In practice this system uses far fewer:
the numeral/phrase span is ≤6 words, the supporting line ≤10 words. `text_render_mode: composited` —
**every gated text span is typeset programmatically**, including the numeral. No diffusion TEXT
anywhere in this system (the rendered official wordmarks are logo marks, not `on_image_text` spans —
§2's logo-policy clarification (ii)).

**Gibberish-proofing:** the ONLY imagery content is the two named tool marks plus flat color and
typeset text. Under the round-2 logo policy (§2's logo-policy block) the marks are diffusion-first:
the RENDER brief for the `logo_zone` names each tool exactly and asks for its accurate official mark
— nothing else — and `logo_fidelity_ok` (§5.11) gates the result; on failure the engine composites
the real mark from the `assets/logos/manifest.yaml` fetch-and-cache path over the same rect and
re-runs QA. The prompt must never be asked to draw a "dashboard," "screen," or "UI" (§5.4, unchanged
— logos are not UI chrome) — only the two named tool marks; the `+`/`=` glyphs, chips, and gradient
are drawn programmatically and are never described to the image model.

**Register/mapping:** `register=editorial`, `archetype=statement-card` (existing key, reused, pinned),
`generation_mode=designed_card` (existing key, reused). No new keys.

---

### 2.2 `ig_annotated_proof` — Instagram "Annotated Proof"

**Topic:** n8n + Apify lead-gen workflow (LinkedIn sibling: §2.1). **Intent:** the Virlo ground truth
is explicit that winning slideshows for this class of topic are "real photo or paper-texture grounds +
1-2 line bold hooks + REAL product screenshots as proof panels" (`FINDINGS_SYNTHESIS.md` §5) — and that
garbled fake-AI-UI text is the single worst-performing pattern in the dataset (score 8.4 at 157K
followers). This system is designed around that exact contrast: a real, pre-captured screenshot of the
n8n canvas or Apify actor console, annotated by hand-drawn-style teal circles/arrows pointing at the
specific proof detail the slide's own sentence names.

**Keys:** `register: editorial` (reused) · `archetype: screenshot-annotated` (existing key,
`style_guide.yaml:119-120`, currently unbound to any `GENERATION_MODES` entry) · `generation_mode:
annotated_proof_ui` — **NEW**, proposed below. Destination `instagram_feed`, format `carousel`, 5
slots.

**New `GENERATION_MODES` entry (proposal for `promptcraft.py`, illustrative — not executed by this
document):**

```python
"annotated_proof_ui": ModeSpec(
    register="editorial",
    archetype="screenshot-annotated",
    composition_directive=(
        "Composite this run's own pre-captured, real screenshot asset of the named tool (n8n canvas, "
        "Apify actor console, or the resulting lead-gen output) as a framed inset card -- do NOT ask "
        "diffusion to invent the screenshot's own pixel content; if no captured screenshot asset "
        "exists for this run, omit the inset entirely rather than fabricate one. Draw a hand-drawn-"
        "style teal annotation layer (circles, arrows, brackets) in the brand accent hex directly over "
        "the inset, pointing at the one proof detail this slide's own sentence names. No other UI "
        "chrome, no invented dashboard elements."
    ),
),
```

This is the only new key required by any of the six round-1 systems (round 2 adds two more —
`cinematic_scene_hook` §2.11, `grid_photo_inset` §2.13 — each proposed in place).

**Layout skeleton (5 slots, 1080×1350):**

| Slot role | Layout | Text budget | text_render_mode |
|---|---|---|---|
| `cover` | Cream paper ground; bold 2-line hook headline centered 30–55% Y; small n8n+Apify logo lockup bottom-left inside margin | ≤2 spans, ≤6 words/span (diffusion cap) | `diffusion` |
| `body` (slide 2) | Typed `screenshot_inset` (below) 15–70% Y, 76% width, centered, 4% corner radius, 3% drop shadow; kicker "0N" **is not used as literal text** (see §5 placeholder-label ban) — kicker is the step's own short verb phrase (e.g. "Trigger fires"), 74–80% Y; body sentence 81–88% Y | title ≤8 words, body ≤24 words | `composited` |
| `prompt_quote` (slide 3) | **Not used by this system** — see note below | n/a | n/a |
| `body` (slide 4) | Same skeleton as slide 2, next proof step | title ≤8 words, body ≤24 words | `composited` |
| `end_card` | Cream ground, "Follow for more automation breakdowns" pattern, save/follow glyphs | title ≤8 words, body ≤12 words | `composited` |

Note: `RENDER_CONTRACT_SPEC.md:317-327`'s fixed 5-role sequence (`cover, body, prompt_quote, body,
end_card`) is destination-level and shared by every Instagram carousel regardless of system — Annotated
Proof has no verbatim-prompt content to show, so its `prompt_quote` slot is populated as a **third
proof/body beat** (same skeleton as the two `body` slots, `exempt_from_word_cap` unused) rather than a
literal prompt card. This is a content decision inside the fixed slot topology, not a topology change.

**Zones (machine-readable — `layout.py`, canvas 1080×1350):**
```yaml
cover:
  logo_zone: [0.12, 0.80, 0.30, 0.06]   # n8n + Apify lockup — marks rendered in the cover's own diffusion call per §2's logo policy (QA-gated, manifest-composite fallback)
  zones:
    - {name: headline, rect_pct: [0.12, 0.30, 0.76, 0.25], type_scale: 0.09, weight: SemiBold, align: center, max_lines: 2, color: "#302B87"}
body:   # slides 2 and 4 — identical shape, different content
  zones:
    - {name: kicker, rect_pct: [0.12, 0.74, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#302B87"}
    - {name: body, rect_pct: [0.12, 0.81, 0.76, 0.07], type_scale: 0.030, weight: Regular, align: left, max_lines: 3, color: "#2B2B2B"}
  screenshot_inset:
    mode: required_or_omit          # composited real asset only; never a diffusion fake — §5.4
    rect_pct: [0.12, 0.15, 0.76, 0.55]
    asset_key: "<topic>.screenshot.<slide_index>"   # resolved against the run's captured-screenshot library
    corner_radius_pct: 4
    shadow_pct: 3
    fallback: solid_color_placeholder_tile           # never a diffused fake — §2.2's own degrade rule
prompt_quote:   # slide 3, third proof beat — identical shape to body above
  zones:
    - {name: kicker, rect_pct: [0.12, 0.74, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#302B87"}
    - {name: body, rect_pct: [0.12, 0.81, 0.76, 0.07], type_scale: 0.030, weight: Regular, align: left, max_lines: 3, color: "#2B2B2B"}
  screenshot_inset: {mode: required_or_omit, rect_pct: [0.12, 0.15, 0.76, 0.55], asset_key: "<topic>.screenshot.<slide_index>", corner_radius_pct: 4, shadow_pct: 3, fallback: solid_color_placeholder_tile}
end_card:
  zones:
    - {name: cta, rect_pct: [0.12, 0.40, 0.76, 0.10], type_scale: 0.045, weight: SemiBold, align: center, max_lines: 2, color: "#302B87"}
    - {name: subtext, rect_pct: [0.12, 0.52, 0.76, 0.08], type_scale: 0.028, weight: Regular, align: center, max_lines: 2, color: "#2B2B2B"}
```
The `screenshot_inset` field is **kept and typed**, not removed as speculative generality (G): it is the
single structural element the Virlo ground truth names as this topic's winning proof mechanism (§2.2's
own intent paragraph) — dropping it removes the system's reason to exist, not just its generality. It
was previously an untyped `required_or_omit` string passthrough (W8-10-era); this document replaces it
with the typed block above so `layout.py`/`grounds.py` have an actual rect, asset-key pattern, and
fallback to consume instead of a bare enum value with no shape.

**Palette (Paper Card recipe):** ground `#F1ECE1` — the round-2 warmed value (operator-locked from
the reference deconstruction's observed warm bone, `DESIGN_DECONSTRUCTION.md` §A.1; supersedes round
1's `#F2F0EC`, which survives only as `style_guide.yaml:164`'s register-prose family wording) — with
the shared `paper_grain` spec (`opacity_pct: 5`, uniform speck, §3.1). Headline/kicker ink `#302B87` (brand indigo, doubling as the
editorial register's "single mint/teal accent" carrier via the annotation layer instead). Body ink
`#2B2B2B` (near-black, not pure black — higher legibility on cream than `#000`). Annotation ink
(hand-drawn circles/arrows) `#00A39A` (brand teal) at 90% opacity, 3–4px equivalent stroke weight.
Screenshot inset frame: `#FFFFFF` card, 1px `#E3E0D8` hairline border.

**Type scale:** intended `Montserrat SemiBold` (headline/kicker) / `Montserrat Regular` (body) —
fallback `assets/fonts/NotoSans-Variable.ttf` at 630 / 400 respectively (same font-gap note as §2.1;
no serif requirement in this system, so the gap is cosmetic weight only, not a missing typeface
family). Cover headline: 7–9% of canvas height, line-height 1.1, max 2 lines. Body kicker: 2.6% of
height, max 1 line. Body sentence: 3% of height, line-height 1.35, max 3 lines (≤24 words).

**Texture/ground:** paper texture, `ground_source: programmatic` for every slot except `cover`, which
uses `ground_source: diffusion` only insofar as the *hook headline* needs a photographic or scene
element behind it per the mode's own directive — in practice this system's cover may also stay
`programmatic` (flat paper) since the winning corpus pattern here is proof-panel-led, not scene-led;
`diffusion` is permitted for `cover` only, never required.

**Gibberish-proofing:** the screenshot insets on `body`/`body` slots are **composited real assets**,
never diffused (this is the single most important gibberish-proofing rule in this whole document — see
§4 item 4's Hard DON'T). The RENDER prompt must never be asked to draw a dashboard, browser chrome, or
generic SaaS screen; it is only ever asked to draw the annotation *marks* (circles/arrows/brackets),
which carry no text at all and are therefore immune to the entire gibberish-text class. Every other
text element on every slot is `composited`. **Dependency flagged:** this system requires a real
screenshot-asset capture pipeline (out of scope of this document) — until one exists, the `body` slots
degrade to the annotation-marks-only layout with a solid-color placeholder tile instead of a screenshot
inset (never a diffused fake one), and the run's decision log records the degrade per I5
(`RENDER_CONTRACT_SPEC.md:383`).

**Register/mapping:** `register=editorial` (reused), `archetype=screenshot-annotated` (existing key,
newly bound), `generation_mode=annotated_proof_ui` (**new key**).

---

### 2.3 `li_statement_hero` — LinkedIn "Statement Hero"

**Topic:** AI sales-agent lead scoring + stat. **Intent:** per `FINDINGS_SYNTHESIS.md` §5, "digits are
low-risk" — an oversized, sourced, qualified stat is the entire creative. This is the highest-density
persuasion-per-pixel system in the set: one number, one context line, nothing else competing for
attention. Distinct from Signal Card (§2.1) in that there is no logo-equation — the tool is named in
copy/caption, not depicted.

**Keys:** `register: editorial` (reused) · `archetype: statement-card` (reused, pinned — same
archetype key as §2.1, different concrete recipe, see §1's note on why archetype and style_system are
separate axes) · `generation_mode: designed_card` (reused). Destination `linkedin`, single `hero` slot.

**Layout skeleton (`hero` slot, 1920×1080):**

| Element | Y-band | X-band | Notes |
|---|---|---|---|
| Eyebrow context tag | 18–24% | 12–88% | short label naming the domain, e.g. "AI SALES AGENTS" — never the literal word "eyebrow"/"tag"/"label" rendered (see §5) |
| Oversized numeral/stat | 28–62% | 12–88% | the hero element — digits + unit only, e.g. "+38%", "3.2x", never a bare unqualified superlative |
| Qualification line | 66–78% | 12–88% | the sourced/qualified context the claim gate's co-location rule requires sit in the SAME sentence as the number (`RENDER_CONTRACT_SPEC.md` §6) |
| Handle | bottom-right | inside margin | |

**Zones (machine-readable — `layout.py`, canvas 1920×1080):**
```yaml
zones:
  - {name: eyebrow, rect_pct: [0.12, 0.18, 0.76, 0.06], type_scale: 0.024, weight: Medium, align: left, max_lines: 1, color: "#FFFFFF"}
  - {name: headline, rect_pct: [0.12, 0.26, 0.76, 0.36], type_scale: 0.36, weight: Bold, align: left, max_lines: 1, color: "#FFFFFF"}
  - {name: qualification, rect_pct: [0.12, 0.66, 0.76, 0.12], type_scale: 0.034, weight: Regular, align: left, max_lines: 2, color: "#FFFFFF"}
```
`eyebrow` renders at 75% opacity, `qualification` at 90% opacity, per the palette below — opacity is a
draw-time alpha applied on top of `color_hex`, not a fifth zone field; `weight: Bold` here is one of the
two places in this document that needs the fourth weight value (`ig_stat_slab`, §2.4, is the other).

**Palette (Brand Card recipe, same as §2.1):** `linear-gradient(135deg, #302B87 0%, #00A39A 100%)`
ground, `#FFFFFF` numeral, eyebrow tag `#FFFFFF` at 75% opacity in a thin all-caps tracked style,
qualification line `#FFFFFF` at 90% opacity.

**Type scale:** numeral is the dominant element — intended `Montserrat SemiBold` (or Bold if the
family ships one), 28–36% of canvas height, line-height 1.0, **max 1 line, digits/unit/symbol only** —
fallback `NotoSans-Variable.ttf` at weight 700 (Bold-equivalent, the top of Noto Sans's variable
weight axis). Eyebrow tag: 2.4% of height, all-caps, letter-spacing +6%, max 1 line, ≤5 words.
Qualification line: 3.4% of height, line-height 1.3, max 2 lines, ≤12 words.

**Texture/ground:** flat gradient, `ground_source: programmatic`.

**Text budget:** `max_title_words: 12`, `max_body_words: 18` (unchanged `linkedin.hero` `SlotSpec`).
The numeral itself is not word-counted the same way a sentence is (it is a 1-4 token glyph run); the
eyebrow + qualification line together stay within the 18-word body cap. `text_render_mode: composited`
— entirely programmatic, no diffusion text.

**Gibberish-proofing:** no imagery at all beyond flat color and typeset digits — the lowest-risk system
in the set by construction. The claim gate runs on the qualification line + numeral as one co-located
unit (`RENDER_CONTRACT_SPEC.md` §6's `qualification_must_colocate` rule) — this is the system the fa51
`35,095` defect (`FINDINGS_SYNTHESIS.md` line 16, "gate-blocked '35,095' claim rendered") maps directly
onto: a Statement Hero numeral is a first-class gated `on_image_text` span, never an `image_brief`
free-text escape.

**Register/mapping:** `register=editorial` (reused), `archetype=statement-card` (reused, pinned),
`generation_mode=designed_card` (reused). No new keys.

---

### 2.4 `ig_stat_slab` — Instagram "Stat Slab"

**Topic:** AI sales-agent lead scoring + stat (LinkedIn sibling: §2.3). **Intent:** "full-bleed brand
color block" (`FINDINGS_SYNTHESIS.md` §5) — deliberately a **solid** slab, not the two-stop gradient
Signal Card/Statement Hero use, so the carousel reads as its own distinct rhythm: alternating solid
indigo/teal panels, each one stat or one step, maximal legibility, zero photographic risk.

**Keys:** `register: editorial` (reused) · `archetype: statement-card` (reused) · `generation_mode:
designed_card` (reused). Destination `instagram_feed`, carousel, 5 slots.

**Layout skeleton (5 slots, 1080×1350):**

| Slot role | Ground | Layout | Text budget | text_render_mode |
|---|---|---|---|---|
| `cover` | solid `#302B87` | numeral/hook centered 32–58% Y, ≤2 spans | ≤2 spans, ≤6 words/span | `diffusion` (text only; ground stays flat, described not generated) |
| `body` (slide 2) | solid `#00A39A` | kicker 16–22% Y + numeral 26–52% Y + qualification 56–68% Y | title ≤8, body ≤24 | `composited` |
| `prompt_quote` (slide 3) | solid `#302B87` | same skeleton, alternating color | title ≤8, body exempt but ≤60-word practical ceiling (§1) — unused here since no verbatim prompt exists; treated as a third stat beat, same as §2.2's note | `composited` |
| `body` (slide 4) | solid `#00A39A` | same skeleton | title ≤8, body ≤24 | `composited` |
| `end_card` | solid `#302B87` | follow/save CTA, platform glyphs outlined (existing `end-card` archetype convention, `style_guide.yaml:139-140`) | title ≤8, body ≤12 | `composited` |

Color alternates indigo→teal→indigo→teal→indigo across the five slots — this alternation IS the
system's series-consistency signature (see §4's series-consistency note: N-E's `series_consistent`
check for this system verifies the alternation pattern itself, not a single fixed hue, so its rubric
instruction must name the expected sequence explicitly per asset).

**Zones (machine-readable — `layout.py`, canvas 1080×1350):**
```yaml
cover:
  zones:
    - {name: headline, rect_pct: [0.12, 0.32, 0.76, 0.26], type_scale: 0.10, weight: Bold, align: center, max_lines: 2, color: "#FFFFFF"}
body:   # slides 2 and 4 — identical shape, alternating ground per the color-alternation rule above
  zones:
    - {name: kicker, rect_pct: [0.12, 0.16, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#FFFFFF"}
    - {name: headline, rect_pct: [0.12, 0.26, 0.76, 0.26], type_scale: 0.26, weight: Bold, align: left, max_lines: 1, color: "#FFFFFF"}
    - {name: qualification, rect_pct: [0.12, 0.56, 0.76, 0.12], type_scale: 0.032, weight: Regular, align: left, max_lines: 2, color: "#FFFFFF"}
prompt_quote:   # slide 3, third stat beat — identical shape to body above, alternating ground
  zones:
    - {name: kicker, rect_pct: [0.12, 0.16, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#FFFFFF"}
    - {name: headline, rect_pct: [0.12, 0.26, 0.76, 0.26], type_scale: 0.26, weight: Bold, align: left, max_lines: 1, color: "#FFFFFF"}
    - {name: qualification, rect_pct: [0.12, 0.56, 0.76, 0.12], type_scale: 0.032, weight: Regular, align: left, max_lines: 2, color: "#FFFFFF"}
end_card:
  zones:
    - {name: cta, rect_pct: [0.12, 0.40, 0.76, 0.10], type_scale: 0.045, weight: SemiBold, align: center, max_lines: 2, color: "#FFFFFF"}
    - {name: subtext, rect_pct: [0.12, 0.52, 0.76, 0.08], type_scale: 0.028, weight: Regular, align: center, max_lines: 2, color: "#FFFFFF"}
```
`headline`'s `weight: Bold` is the second of the two places this document needs the fourth weight value
(`li_statement_hero`, §2.3, is the first) — an oversized numeral on a solid brand panel is the one shape
in this whole set that reads correctly only at the heaviest cut available.

**Palette:** solid `#302B87` / solid `#00A39A`, alternating per slot as above. Text `#FFFFFF` on both.
No gradients anywhere in this system — this is the deliberate distinction from §2.1/§2.3's Brand Card
recipe.

**Type scale:** same numerals-dominant scale as §2.3 but scaled for the 4:5 canvas: numeral 22–28% of
canvas height (a 5-slot carousel numeral reads slightly smaller than a single hero to leave room for
kicker+qualification in the same slide), kicker 2.6% of height, qualification 3.2% of height. Intended
`Montserrat SemiBold`/`Bold`, fallback `NotoSans-Variable.ttf` 630/700.

**Texture/ground:** `ground_source: programmatic` for all 5 slots — grounds are never diffused in this
system (the deliberate distinction from a photographic register). **Default:** `cover`'s
`text_render_mode` stays `diffusion` (the destination default, §2.7) — this is the one diffusion-touched
slot in the system, and its own layout table above already states this plainly (`diffusion (text only;
ground stays flat, described not generated)`). **Documented alternate configuration, not the default:**
an operator may override `cover.text_render_mode` to `composited` for this system specifically, which
makes `ig_stat_slab` need **zero image-generation calls** for the entire asset — a deliberate, statable
cost property worth carrying into `RenderContract` budget planning (`RENDER_CONTRACT_SPEC.md` §4 item 6)
if that override is ever exercised, but §2.7's diffusion-surface census below counts this system's
`cover` as diffusion-touched under the shipped default.

**Gibberish-proofing:** identical rationale to §2.3 — no imagery, no diffusion text risk beyond the
optional cover span. No screenshot, no logo, no photographic content anywhere in this system.

**Register/mapping:** `register=editorial` (reused), `archetype=statement-card` (reused),
`generation_mode=designed_card` (reused). No new keys.

---

### 2.5 `li_editorial_brief` — LinkedIn "Editorial Brief"

**Topic:** Claude ops-assistant for founders. **Intent:** "serif authority, 1 span, vector-overlaid"
(`FINDINGS_SYNTHESIS.md` §5) — this topic (an ops-assistant that helps a founder run their business) is
the one system in the set explicitly aiming for a premium, calm, high-trust register rather than an
urgent/direct-response one; `visual_registers.editorial`'s own `mood: "premium, calm, high-trust"`
(`style_guide.yaml:166`) is the literal fit. One authoritative sentence, one small vector graphic
(never a photograph, never a screenshot), cream paper ground.

**Keys:** `register: editorial` (reused) · `archetype: editorial-carousel` (existing key,
`style_guide.yaml:125-126` — description "cream/bone paper texture, italic Didone serif headlines,
teal accent checkboxes, quoted prompt boxes" is the exact recipe this system and §2.6 draw from; note
it is the *default* archetype for `instagram_feed`/`tiktok`, not `linkedin`
(`style_guide.yaml:83,96,104`) — reused here for LinkedIn anyway because `style_system` pinning
overrides the per-destination default-archetype rotation entirely, §1's note) · `generation_mode:
designed_card` (reused). Destination `linkedin`, single `hero` slot.

**Layout skeleton (`hero` slot, 1920×1080):**

| Element | Y-band | X-band | Notes |
|---|---|---|---|
| Small vector accent (line, bracket, or single geometric mark) | 14–20% | 12–30% | never a pictorial icon (see §5's clip-art-icon-row ban) — a single deliberate line/shape, teal |
| Headline (the 1 span) | 24–58% | 12–88% | the authoritative sentence — 1 span only |
| Attribution/context micro-line | 62–68% | 12–88% | e.g. "HypeDigitaly — Claude ops playbooks", never a named individual (persona policy, `RENDER_CONTRACT_SPEC.md:62-68`) |
| Handle | bottom-right | inside margin | |

**Zones (machine-readable — `layout.py`, canvas 1920×1080):**
```yaml
decorative_zone: [0.12, 0.14, 0.18, 0.06]   # vector accent line/bracket/mark — drawn programmatically, no OnImageText, not in `zones:`
zones:
  - {name: headline, rect_pct: [0.12, 0.24, 0.76, 0.34], type_scale: 0.08, weight: SemiBold, align: left, max_lines: 2, color: "#302B87"}
  - {name: attribution, rect_pct: [0.12, 0.62, 0.76, 0.06], type_scale: 0.026, weight: Regular, align: left, max_lines: 1, color: "#2B2B2B"}
```
`weight: SemiBold` on `headline` is the fallback-upright rendering named below — the intended italic
Didone cut is a separate, stated font-acquisition dependency, not a different zone shape.

**Palette (Paper Card recipe, same family as §2.2):** ground `#F1ECE1` (round-2 warmed value + grain,
same note as §2.2), headline ink `#302B87`, attribution ink `#2B2B2B` at 75% opacity, vector accent
`#00A39A`.

**Type scale:** intended **Playfair Display Bold Italic** for the headline (the italic-Didone
treatment `visual_registers.editorial.type` describes, `style_guide.yaml:165` — round 2 names the
family; §3.5's vendoring task) and **Lora Regular** for the attribution line (round 2's
body-sans-to-serif switch). Neither is in-repo until §3.5 lands — concrete fallback:
`NotoSans-Variable.ttf` at weight 630, rendered **upright** (the italic-serif visual effect is not
achievable until the vendored files land and pass the Czech-glyph verification per
`assets/fonts/README.md`'s protocol — a stated dependency, not a silent substitution). Headline: 6–8% of
canvas height, line-height 1.15, **max 2 lines**, ≤12 words (the `linkedin.hero.max_title_words` cap).
Attribution: 2.6% of height, roman (never italic — the italic slant is reserved for the headline
concept only, moot until the serif exists), max 1 line.

**Texture/ground:** paper texture, `ground_source: programmatic`.

**Text budget:** `max_title_words: 12`, `max_body_words: 18` — headline alone typically uses 6-10 of
the 12; the attribution line is not a second span of the SAME cap, it is treated as the `max_body_words`
allotment (≤18, in practice ≤8). `text_render_mode: composited`.

**Gibberish-proofing:** no photographic or screenshot content at all — the vector accent is a single
deterministic shape (drawn programmatically, not diffused, or diffused only as an explicitly
"no-text, decorative-only" element per the existing rule already in N-D's system prompt,
`promptcraft.py:129-132`). Nothing here can produce garbled text because nothing beyond the two typeset
spans exists on the canvas.

**Register/mapping:** `register=editorial` (reused), `archetype=editorial-carousel` (existing key,
reused across destinations), `generation_mode=designed_card` (reused). No new keys.

---

### 2.6 `ig_prompt_sheet` — Instagram "Prompt Sheet"

**Topic:** Claude ops-assistant for founders (LinkedIn sibling: §2.5). **Intent:** "monospace prompt
card — text composited, never diffusion" (`FINDINGS_SYNTHESIS.md` §5) — the Virlo ground truth names
text-dense guide/tutorial slideshows (tables/steps) as "a top faceless format" (`FINDINGS_SYNTHESIS.md`
§5), and a literal, copy-pasteable Claude prompt is the single most actionable, non-obvious payload this
theme can offer (the copy-quality bar's own value-density floor, `FINDINGS_SYNTHESIS.md` §6). This
system exists specifically to be the vehicle for the locked decision 5 example case: the `prompt_quote`
slot role.

**Keys:** `register: editorial` (reused) · `archetype: editorial-carousel` (existing key — its own
description literally names "quoted prompt boxes", `style_guide.yaml:126`) · `generation_mode:
designed_card` (reused). Destination `instagram_feed`, carousel, 5 slots.

**Layout skeleton (5 slots, 1080×1350):**

| Slot role | Ground | Layout | Text budget | text_render_mode |
|---|---|---|---|---|
| `cover` | cream `#F1ECE1` | hook headline 30–55% Y, small Claude wordmark/logo bottom-left | ≤2 spans, ≤6 words/span (only relevant if the diffusion route is exercised — see below) | `composited` — **firmed default for this system, overriding the destination's own diffusion default for `cover`** (see Texture/ground below and §2.7) |
| `body` (slide 2) | cream `#F1ECE1` | eyebrow context 16–22% Y + headline 24–40% Y + 3-row checklist (✓ + short line) 46–88% Y | title ≤8, body ≤24 (checklist rows count toward body budget, ≤6 words/row × ≤4 rows) | `composited` |
| `prompt_quote` (slide 3) | **dark terminal card**, see palette below | full-bleed dark card 10–90% Y inset from a 6%-wide cream border; monospace-styled verbatim prompt text, left-aligned, top-anchored | `exempt_from_word_cap: true` (`RENDER_CONTRACT_SPEC.md:325`) but capped at **`prompt_quote_max_words: 50`** (derived below from this system's own type scale) so the card never overflows the safe zone at carousel scale | `composited` — **never diffusion, by design** (this is the literal case `FINDINGS_SYNTHESIS.md` §5 names) |
| `body` (slide 4) | cream `#F1ECE1` | same skeleton as slide 2, next step | title ≤8, body ≤24 | `composited` |
| `end_card` | cream `#F1ECE1` | follow/save CTA | title ≤8, body ≤12 | `composited` |

**Zones (machine-readable — `layout.py`, canvas 1080×1350):**
```yaml
cover:
  logo_zone: [0.12, 0.80, 0.30, 0.06]   # small Claude mark, bottom-left — partial-area diffusion surface per §2's logo policy (nominative use only, §3.6; QA-gated, manifest-composite fallback)
  zones:
    - {name: headline, rect_pct: [0.12, 0.30, 0.76, 0.25], type_scale: 0.08, weight: SemiBold, align: center, max_lines: 2, color: "#302B87"}
body:   # slides 2 and 4 — identical shape
  zones:
    - {name: eyebrow, rect_pct: [0.12, 0.16, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#302B87"}
    - {name: headline, rect_pct: [0.12, 0.24, 0.76, 0.16], type_scale: 0.07, weight: SemiBold, align: left, max_lines: 2, color: "#302B87"}
    - {name: body, rect_pct: [0.12, 0.46, 0.76, 0.42], type_scale: 0.028, weight: Regular, align: left, max_lines: 4, color: "#2B2B2B"}   # 4 checklist rows
prompt_quote:
  ground_recipe: dark_terminal
  zones:
    - {name: prompt_text, rect_pct: [0.10, 0.14, 0.80, 0.72], type_scale: 0.032, weight: Regular, align: left, max_lines: 8, color: "#00A39A"}
end_card:
  zones:
    - {name: cta, rect_pct: [0.12, 0.40, 0.76, 0.10], type_scale: 0.045, weight: SemiBold, align: center, max_lines: 2, color: "#302B87"}
    - {name: subtext, rect_pct: [0.12, 0.52, 0.76, 0.08], type_scale: 0.028, weight: Regular, align: center, max_lines: 2, color: "#2B2B2B"}
```

**Palette:** cream slots (`cover`, `body`×2, `end_card`) use the same Paper Card recipe as §2.2/§2.5:
ground `#F1ECE1` (round-2 warmed value + grain, §2.2's note), headline ink `#302B87`, body ink
`#2B2B2B`, checkbox/accent `#00A39A`. The
`prompt_quote` slot alone breaks the paper ground: ground `#1E1B2E` (a near-indigo near-black,
deliberately dark to read as a code/terminal surface, distinct from `visual_registers.hype`'s
`near-black` — see §6's leak table for why this must NOT be described using hype-register vocabulary),
prompt text `#00A39A` (brand teal, terminal-green-adjacent without being literal terminal green),
a thin `#302B87` top rule separating the card from its cream border.

**Type scale:** cream-slot type identical to §2.5 (headline intended Playfair Display Bold Italic,
body/checklist intended Lora Regular — §3.5's round-2 vendoring; fallback `NotoSans-Variable.ttf` 630
upright / 400 until the vendored files land and glyph-verify). The `prompt_quote` slot wants an
intended **monospace** family (e.g. a licensed variable mono such as JetBrains Mono or IBM Plex Mono) —
**not bundled in this repo either.** Concrete fallback: `NotoSans-Variable.ttf` at weight 400 with
letter-spacing increased ~4% to approximate a fixed-pitch rhythm; this is a visual approximation, not a
true monospace grid, and is stated here as a second, separate font-acquisition dependency from §2.5's
serif gap. Prompt text: 2.8–3.2% of canvas height, line-height 1.4, max 8 lines.

**`prompt_quote_max_words: 50` — derivation.** The dark card spans x:[0.06,0.94]/y:[0.10,0.90] of the
1080×1350 canvas (the "6%-wide cream border" inset); the prompt-text zone itself pads a further ~4%
inside that card on every side, giving a usable text rect of `rect_pct: [0.10, 0.14, 0.80, 0.72]` —
864px wide. At this system's own stated minimum readable size (`min_pt` for this `TypeScale`, taken one
notch below the 2.8% floor already named above, i.e. ~2.4% of 1350px ≈ 32px), the monospace-approximated
fallback (`NotoSans-Variable.ttf` at +4% letter-spacing, ~0.6em average advance per character) fits
≈42-43 characters per line. At ≈6 characters/word (5-letter average English word + 1 space — the same
heuristic this system's own prompt-sheet content is written to), that is ≈7 words/line × `max_lines: 8`
= ≈56 words theoretically fittable at the size floor. **`prompt_quote_max_words: 50`** is that ceiling
rounded down for a safety margin, because a verbatim tool prompt (this slot's actual payload) runs
longer average token/word length than prose English — punctuation-dense instructions, parameter names,
code-adjacent tokens — so the same character budget buys fewer of them. 50 is enforced at CRAFT time
(N-C/N-F, same choke point as every other cap in this document) so an over-long verbatim prompt never
reaches `compositing.fit_text`'s `TypesetOverflowError` in the first place — that failure is the most
expensive point in the chain to discover it at (`COMPOSITING_SPEC.md` §4.4/§7).

**Texture/ground:** `ground_source: programmatic` for all 5 slots' GROUNDS — including `cover`, whose
`text_render_mode` this system **firms to `composited`** (flat cream + typeset hook), overriding the
destination's own `SlotSpec.text_render_mode: diffusion` default for the `cover` role
(`RENDER_CONTRACT_SPEC.md:323`) — not merely "recommended," but this system's shipped default, since the
whole point of Prompt Sheet is "text composited, never diffusion." (An operator MAY re-enable diffusion
for this cover via an explicit per-run override.) **Round-2 logo-policy exception:** the cover's small
Claude mark makes its `logo_zone` a partial-area diffusion surface (§2's logo-policy block — QA-gated,
manifest-composite fallback), so §2.7's census now counts this system as diffusion-touched on exactly
that partial area; every gated text string on every slot remains composited, unchanged.

**Gibberish-proofing:** the `prompt_quote` slot's entire raison d'être is eliminating diffusion-text
risk for exactly the content class (a verbatim, copy-pasteable prompt) where a single dropped or
garbled character makes the payload worthless. It is composited byte-for-byte from the gated
`on_image_text` string — this is the system that makes literal the locked decision 5 sentence "Diffusion
renders text only for a cover hook of ≤2 spans... text-dense slide roles are typeset deterministically."
The RENDER prompt for this slot must not describe ANY renderable text at all — the compositor lays the
prompt text down after the ground image (or flat color) is finalized, with no diffusion pass touching
that region.

**Register/mapping:** `register=editorial` (reused), `archetype=editorial-carousel` (existing key,
reused), `generation_mode=designed_card` (reused). No new keys.

---

### 2.7 Diffusion-surface census — which slots actually need N-D (extended round 2, ALL systems)

Per-slot answer, under each system's SHIPPED default (§2.1–§2.6 above and §2.9–§2.13 below — the
round-2 rows are FORWARD references; the census keeps its round-1 section number because the sibling
spec cites it by number, `RENDER_CONTRACT_SPEC.md:143`. The documented alternate overrides —
`ig_stat_slab`'s optional zero-diffusion cover, `ig_lifestyle_stack`'s optional programmatic
`end_card` — are called out in their own text and do NOT change the counts below):

| System | `cover` | `body`×2 | `prompt_quote` | `end_card` | Any diffusion surface? |
|---|---|---|---|---|---|
| `li_signal_card` (hero only) | n/a | n/a | n/a | n/a | **Yes — partial-area.** Ground and every text span are programmatic/composited, but the `logo_zone`'s two tool marks are a diffusion-first surface under the round-2 logo policy (§2.1, §2's logo-policy block). |
| `ig_annotated_proof` | **diffusion** (hook headline, §2.2) | programmatic | programmatic | programmatic | **Yes — `cover` only.** |
| `li_statement_hero` (hero only) | n/a | n/a | n/a | n/a | **No — fully programmatic.** No imagery beyond flat color and typeset digits (§2.3). |
| `ig_stat_slab` | **diffusion** (text only, ground flat — §2.4's own table row) | programmatic | programmatic | programmatic | **Yes — `cover` only**, under the shipped default (a documented, non-default operator override can zero this out — §2.4). |
| `li_editorial_brief` (hero only) | n/a | n/a | n/a | n/a | **No — fully programmatic.** Vector accent is drawn programmatically, never diffused (§2.5). |
| `ig_prompt_sheet` | ground programmatic + text composited (firmed default, §2.6); **diffusion on the cover `logo_zone` only** (Claude mark, round-2 logo policy) | programmatic | programmatic (dark terminal ground, still non-diffused) | programmatic | **Yes — 1 of 5, partial-area (cover logo only).** |
| `ig_value_sheet` (§2.9) | programmatic (firmed, same override as §2.6; no logo anywhere) | programmatic | programmatic | programmatic | **No — fully programmatic.** |
| `ig_lifestyle_stack` (§2.10) | **diffusion** (ground only — caption composited, case (b)) | **diffusion** ×2 (same) | **diffusion** (same) | **diffusion** (same; shipped default) | **Yes — ALL 5 slots.** First full-photoreal system in the library. |
| `ig_scene_hook` (§2.11) | **diffusion** (ground only — caption composited) | programmatic (dark terminal) | **diffusion** (second scene beat, ground only) | programmatic | **Yes — 2 of 5.** |
| `li_scene_hero` (§2.12, hero only) | n/a | n/a | n/a | n/a | **Yes — the single `hero` slot diffuses its ground (caption composited, case (b)).** |
| `ig_operator_grid` (§2.13) | **diffusion** (small photo inset ONLY, ~6% of canvas — ground/text all programmatic) | programmatic | programmatic | programmatic | **Yes — 1 of 5, partial-area.** |

**ROUND-4/5 AMENDMENT — the census above is HISTORY, kept because the per-system rows still record
which slots carry a *scene* and which carry a *card*. Under the flip its totals are void:**

> **Every slot of every one of the twenty-nine systems is a canonical `gpt-image-2-text-to-image`
> render.** There is no fully-programmatic system, no partial-area exception and no two-cover
> diffusion-TEXT surface. `programmatic` now names **the fallback rung and the kill-switch
> destination only** — reached after two failing per-glyph text verdicts, or when
> `canonical_render_enabled: false`.

What the census is still *for*, restated as the live truth table, is the **`llm_crafted` vs
`templated_diffusion`** split — i.e. *does this slot's image need a per-topic description from N-D,
or does the recipe plus the gated text determine it completely?*

| Category | Which slots | N-D? |
|---|---|---|
| **`llm_crafted`** | the photoreal systems' scene slots (§2.10-§2.12) and the illustration systems' signature slots (§2.17-§2.21: website showcase, robot caricature, anime scene, concept dashboard, meme reaction) | **yes**, one call per asset, sized on that asset's `llm_crafted` slot count |
| **`templated_diffusion`** | every recipe-determined card — all `designed_card`, `serif_editorial`, `editorial_grotesque`, `artifact_showcase` and `brand_promo` slots, plus the illustration systems' non-signature body slides | **no** — a deterministic template prompt, still governed through the one choke point |
| **`programmatic`** | none, by default | **no** — fallback and kill switch only |

At the ratified quota that is **~5 N-D calls per run** (`PLAN.md` §9.3), against **20 paid canonical
renders in the worst case** — the opposite shape from round 2, where N-D was rare because most slots
were free. Slots are no longer free; prompts mostly are.
`ig_lifestyle_stack` is the first system where EVERY slot is
diffusion-touched — a genuinely new cost/risk shape that N-D's per-asset token budget (below) and
`RenderContract` budget planning must account for explicitly, never amortized into the round-1
"usually 0 or 1 diffusion slot" assumption. Note the round-2 photoreal slots put diffusion on the
GROUND only — `text_render_mode` stays `composited` on every one of them, so the diffusion-TEXT
surface of the whole library is still exactly the two round-1 covers (`ig_annotated_proof`,
`ig_stat_slab`).

**What this drives (real optimisation, not just bookkeeping):**
- **N-D (`promptcraft`, the image-prompt crafter) is SKIPPED ENTIRELY** for an asset whose `style_system`
  resolves to one of the three fully-programmatic rows above — there is no slot for it to craft a prompt
  for. This is decided once, at the same point `style_system` itself resolves (`RENDER_CONTRACT_SPEC.md`
  §2, before authoring) — never discovered slot-by-slot mid-asset. The asset goes straight from N-C
  (copy) to `compositing.render_slot` (§`COMPOSITING_SPEC.md` §2), never touching `MediaGenerator` at
  all for a case-(a)-only asset.
- **The N-D carousel token budget is computed per diffusion-touched slot, not per slot.** Concretely:
  `llm.LlmClient.call_json`'s `slide_count` argument (`RENDER_CONTRACT_SPEC.md` §7's
  `prompt_crafter: {max_tokens: 6000, per_slide_tokens: 1200}`) should be threaded as
  `len([s for s in contract.slots if slot_has_diffusion_surface(s, style_system)])`, not
  `len(contract.slots)` — for `ig_annotated_proof`/`ig_stat_slab` that is **1**, not 5, so N-D's actual
  per-asset budget is `6000 + 1×1200 = 7200`, not `6000 + 5×1200 = 12000`; for the three fully-programmatic
  systems it is **0**, and N-D is never called (previous bullet), so the token line item is `$0`, not a
  wasted reservation. Round-2 values under the same formula: `ig_lifestyle_stack` 5 → 12000 (the first
  system to actually spend the full reservation), `ig_scene_hook` 2 → 8400, `li_scene_hero` 1 → 7200,
  `ig_operator_grid` 1 → 7200, and the two partial-area logo surfaces (`li_signal_card`,
  `ig_prompt_sheet`) 1 → 7200 — a partial-area slot still counts as one diffusion-touched slot for
  budgeting. `slot_has_diffusion_surface(slot, style_system)` is exactly this table,
  looked up by `(role, style_system)` — no new logic beyond what's tabulated above. This is a
  coordination note for `RENDER_CONTRACT_SPEC.md` §7's config surface and `promptcraft`'s wiring; this
  document fixes the per-system truth table those two consume.

Multi-model test renders for the diffusion-touched surfaces tabulated above are specified in
`MULTI_MODEL_SPEC.md` (being authored in parallel — referenced here by name only).

### 2.8 Text-budget cross-check (extended round 2, ALL systems)

Every system in this document — §2.1–§2.6 and, forward-referenced, §2.9–§2.13 — must be satisfiable
under the three global ceilings: slide body ≤24 words, headline ≤12 words, diffusion text ≤2 spans/≤6
words per span on a `cover` only. Checked, not assumed:

| Ceiling | Where it's enforced in this document | Every system compliant? |
|---|---|---|
| Slide body ≤24 words | `RENDER_CONTRACT_SPEC.md`'s `instagram_feed.slots[body/prompt_quote].max_body_words: 24`; every Instagram system's `body` row in §2 states its cap verbatim | Yes — with exactly TWO named exemptions, each carrying its own tighter derived ceiling rather than an unbounded pass: `ig_prompt_sheet`'s `prompt_quote` (`prompt_quote_max_words: 50`, §2.6) and round 2's `ig_value_sheet` dense slides (`value_sheet_max_words: 220`, §2.9). No third exemption exists or is planned. |
| Headline ≤12 words | `linkedin.headline_max_words: 12` (LinkedIn systems §2.1/§2.3/§2.5/§2.12 `max_title_words: 12`); Instagram `cover.max_title_words: 10` and `body/prompt_quote/end_card.max_title_words: 8` (§2.2/§2.4/§2.6, and §2.9–§2.13's stated budgets) — every system's own stated cap is ≤10, strictly inside the 12-word ceiling | Yes — round 2 included (`ig_lifestyle_stack` ≤8, `ig_scene_hook`/`li_scene_hero` hook ≤2×≤6 kept as a creative constraint even though composited, `ig_operator_grid` ≤8). |
| ~~Diffusion text ≤2 spans/≤6 words per span, `cover` only~~ **LIFTED (round-4/5)** | The cap and its two config fields are **deleted**, not universalised: the canonical prompt embeds the complete gated `on_image_text` verbatim, exactly as `MULTI_MODEL_SPEC.md` §4.2 already lifted it for test prompts. What replaces it is not a smaller number but a **verification**: per-glyph text QA against those same strings, one retry, then the composited rung. | n/a — the binding text budgets are now the word caps in the two rows above, plus the two named exemptions. A 220-word `ig_value_sheet` slide is the library's densest render and the simulation drew its 8-entry sibling flawlessly on both models; it is nonetheless the first surface to watch in the confirmation run. |

No system required a global cap change to pass this check — all systems (the eleven of rounds 1-2 and
the eighteen round-4/5/6 entries, §2.15-§2.22) were designed inside
the two surviving ceilings (or inside one of the two named, derived exemptions); this table is the record that
the check was actually run, not a claim taken on faith.

---

### 2.9 `ig_value_sheet` — Instagram "Value Sheet" (round 2)

**Topic:** format-generic — a dense, saveable cheat-sheet (numbered prompts/tools/steps) for any topic
whose payload is a LIST, not a narrative; `topic_tag: prompt_dump_reference` (§4.1's extended
classifier — the source analysis flagged this tag as an unresolved follow-up,
`DESIGN_DECONSTRUCTION.md` §C.1; §4's round-2 rewrite resolves it). **Intent:** the reference
corpus's dense cheat-sheet slides (230–540 words) are built for **save-then-zoom** consumption, not
in-feed reading (`DESIGN_DECONSTRUCTION.md` §C.1, citing that reference's own catalog) — a consumption
model no other system serves, because the global 24-word slide-body cap makes it structurally
impossible. Rather than a cap override on an existing system, this system carries its own derived
exemption (`value_sheet_max_words: 220`, below). Dark-terminal ground on every slot (reusing
`ig_prompt_sheet`'s terminal palette) differentiates it at a glance from the cream/gradient systems
and is independently validated by the reference's own dark-card sub-format. **Explicitly rejected from
the reference:** the literal Claude.ai chat-composer mockup on the whitelabeled cover exemplar —
exactly Hard DON'T 5.4's fake-third-party-UI pattern, doubly banned since it impersonates a real
product's actual interface.

**Keys:** `register: editorial` (reused) · `archetype: dense-spec-card` (existing key,
`style_guide.yaml:123` — "Dark branded card restating the post's bullets as designed columns/panels
with numbers and arrows"; confirmed strong match, no new archetype needed) · `generation_mode:
designed_card` (reused). Destination `instagram_feed`, carousel, 5 slots. `format_class:
designed_card` (§4.1).

**Layout skeleton (5 slots, 1080×1350):**

| Slot role | Ground | Layout | Text budget | text_render_mode |
|---|---|---|---|---|
| `cover` | dark `#1E1B2E` | kicker 20–26% Y + numbered-promise headline 30–52% Y + subtext 56–62% Y | title ≤10 | `composited` — firmed, same destination-default override as §2.6's cover |
| `body` (slide 2) | dark `#1E1B2E` | category kicker top-left + "N/10" progress counter top-right + ONE dense multi-entry body zone 13–87% Y + optional progress-marker footer strip | `value_sheet_max_words: 220` (derived below) — exempt from the 24-word cap, §2.8 | `composited` |
| `prompt_quote` (slide 3) | dark `#1E1B2E` | identical shape to `body` — third dense beat, same convention as §2.2/§2.4 | same | `composited` |
| `body` (slide 4) | dark `#1E1B2E` | same skeleton, next category | same | `composited` |
| `end_card` | dark `#1E1B2E` | follow/save CTA (optional `end_card_override: artifact_close`, §3.1) | title ≤8, body ≤12 | `composited` |

**Zones (machine-readable — full `style_systems:` entry shape; §3.1 appends this block verbatim,
single source, never duplicated there):**
```yaml
ig_value_sheet:
  display_name: "Value Sheet"
  format_class: designed_card
  topic_tag: prompt_dump_reference
  destination: instagram_feed
  register: editorial
  archetype: dense-spec-card
  generation_mode: designed_card
  ground_recipe: dark_terminal            # every slot goes dark — contrast with ig_prompt_sheet, where only prompt_quote is dark
  value_sheet_max_words: 220              # derived below — second named exemption, §2.8
  type_floor: 0.0185                      # derived below — needs its own glyph-legibility re-verification, §3.5
  palette:
    ground: "#1E1B2E"
    kicker_ink: "#00A39A"
    body_ink: "#EDEAE3"
    rule: "#302B87"
  type:
    display_family: "Playfair Display Bold"          # vendored, §3.5
    display_fallback: "assets/fonts/NotoSans-Variable.ttf@700"
    body_family: "Lora Regular"                      # vendored, §3.5
    body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
  slots:
    cover:
      ground_source: programmatic         # never diffusion — a numbered-promise hook is pure typeset text
      text_render_mode: composited
      zones:
        - {name: kicker, rect_pct: [0.12, 0.20, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: center, max_lines: 1, color: "#00A39A"}
        - {name: headline, rect_pct: [0.10, 0.30, 0.80, 0.22], type_scale: 0.09, weight: Bold, align: center, max_lines: 2, color: "#FFFFFF"}
        - {name: subtext, rect_pct: [0.14, 0.56, 0.72, 0.06], type_scale: 0.026, weight: Regular, align: center, max_lines: 1, color: "#FFFFFF"}
    body:                                  # slides 2 and 4 — the dense category card
      ground_source: programmatic
      text_render_mode: composited
      footer_zone: [0.08, 0.90, 0.84, 0.04]   # optional progress-marker strip — decorative, drawn programmatically, not a `zones:` entry
      zones:
        - {name: kicker, rect_pct: [0.08, 0.06, 0.60, 0.05], type_scale: 0.022, weight: SemiBold, align: left, max_lines: 1, color: "#00A39A"}
        - {name: counter, rect_pct: [0.72, 0.06, 0.20, 0.05], type_scale: 0.020, weight: Regular, align: right, max_lines: 1, color: "#FFFFFF"}
        - {name: body, rect_pct: [0.08, 0.13, 0.84, 0.74], type_scale: 0.0185, weight: Regular, align: left, max_lines: 20, color: "#EDEAE3"}
    prompt_quote:                          # slide 3 — third dense beat, identical shape to body
      ground_source: programmatic
      text_render_mode: composited
      footer_zone: [0.08, 0.90, 0.84, 0.04]
      zones:
        - {name: kicker, rect_pct: [0.08, 0.06, 0.60, 0.05], type_scale: 0.022, weight: SemiBold, align: left, max_lines: 1, color: "#00A39A"}
        - {name: counter, rect_pct: [0.72, 0.06, 0.20, 0.05], type_scale: 0.020, weight: Regular, align: right, max_lines: 1, color: "#FFFFFF"}
        - {name: body, rect_pct: [0.08, 0.13, 0.84, 0.74], type_scale: 0.0185, weight: Regular, align: left, max_lines: 20, color: "#EDEAE3"}
    end_card:
      ground_source: programmatic
      text_render_mode: composited
      end_card_override: artifact_close    # OPTIONAL, per-asset choice, never a system default — §3.1's round-2 refinement note
      zones:
        - {name: cta, rect_pct: [0.12, 0.40, 0.76, 0.10], type_scale: 0.045, weight: SemiBold, align: center, max_lines: 2, color: "#FFFFFF"}
        - {name: subtext, rect_pct: [0.12, 0.52, 0.76, 0.08], type_scale: 0.028, weight: Regular, align: center, max_lines: 2, color: "#FFFFFF"}
```

**Palette:** ground `#1E1B2E` (reusing §2.6's terminal hex — same §6 caveat: never described with the
`hype` register's `near-black` vocabulary), kicker/category ink `#00A39A`, body ink `#EDEAE3` (warm
off-white, not pure `#FFF` — softer at dense small sizes), rule/divider `#302B87`.

**Type scale:** cover headline intended Playfair Display Bold (fallback `NotoSans-Variable.ttf@700`),
9% of canvas height. Dense body intended **Lora Regular** (fallback `NotoSans-Variable.ttf@400`) at
**`type_floor: 0.0185`** (1.85% of canvas height ≈ 25px) — genuinely new: below every other system's
floor (§2.6's own stated 2.4% "one notch below" reference). **This floor needs its OWN Czech-glyph
legibility re-verification on the vendored Lora file before ship** — `assets/fonts/README.md`'s
existing PASS was rendered at ≈8.8% of a 500px test frame and does not carry over (§3.5).

**`value_sheet_max_words: 220` — derivation** (`DESIGN_DECONSTRUCTION.md` §C.1, reproduced so the
number has an in-document source): usable body rect `[0.08, 0.13, 0.84, 0.74]` = 907×999px; at the
1.85% floor, line-height 1.2, 10 numbered entries × ~2.2 lines ≈ 660px — fits with row gaps; ~60–65
chars/line ⇒ ~20–22 words/entry × 10 entries ≈ 200–220 words. 220 is one notch below the 230-word
reference average — the same -10%-for-safety rounding §2.6 used for `prompt_quote_max_words: 50`.
Enforced at CRAFT time (N-C/N-F, the same choke point as every other cap in this document), never
discovered at `fit_text`'s `TypesetOverflowError`.

**Texture/ground:** `ground_source: programmatic` for all 5 slots, no exceptions — joins the
fully-programmatic club (§2.7): zero diffusion surface, N-D never called, zero image-generation cost.

**Text budget:** dense slides carry `value_sheet_max_words: 220` — the SECOND named exemption from the
24-word slide-body cap (§2.8), alongside `prompt_quote`'s 50; like it, derived and bounded, never an
unbounded pass. Cover/end_card budgets are the standard destination caps.

**Gibberish-proofing:** nothing is diffused anywhere in the asset; every numbered entry is composited
byte-for-byte from gated `on_image_text` strings. The RENDER prompt does not exist for this system.
The one genuinely new risk is *legibility*, not gibberish — hence the `type_floor` verification gate
above.

**Register/mapping:** `register=editorial` (reused), `archetype=dense-spec-card` (existing key, newly
exercised), `generation_mode=designed_card` (reused). No new keys, no new layout capability (the dense
multi-entry body reuses the existing checklist-as-one-zone convention).

---

### 2.10 `ig_lifestyle_stack` — Instagram "Lifestyle Stack" (round 2, photoreal)

**Topic:** format-generic tool/step listicle ("the N tools/steps that run X"); `topic_tag:
tool_stack_howto` (§4.1). **Intent:** the proven faceless photoreal winner — the reference template
produced the top-ranked slideshow across both Virlo monitors (909K views, 6.6% save rate, +42.53
weighted; `DESIGN_EXPANSION.md` §A.1). One photoreal minimalist environment per slide, one tool/step
named per slide, near-zero graphic design: the environment does the persuasion, the caption is minimal
furniture. The faceless adaptation is a *strengthening* edit, not a compromise — the reference's own
corpus analysis calls this "the strongest faceless class we can actually generate," and our version
removes the one non-faceless element (the creator's person) while keeping everything that actually won
(real-feeling minimalist environment + plain caption).

**Keys:** `register: photographic_ugc` (existing key) · `archetype: aspirational-lifestyle-scene`
(existing key, `style_guide.yaml:144`, reused) · `generation_mode: aspirational_lifestyle_scene`
(existing key, **directive AMENDED** below — the existing text already matches in spirit,
`promptcraft.py:480-487`, but does not state the faceless rule or the reserved-zone mechanics).
Destination `instagram_feed`, carousel, 5 slots. `format_class: photoreal` (§4.1).

**Amended `composition_directive` (proposed diff against the existing `aspirational_lifestyle_scene`
`ModeSpec`, `promptcraft.py:480-487` — illustrative, not executed by this document):**

```python
"aspirational_lifestyle_scene": ModeSpec(
    register="photographic_ugc",
    archetype="aspirational-lifestyle-scene",
    composition_directive=(
        "A real-feeling, minimalist, aspirational-but-plausible workspace/environment (loft office, "
        "quiet apartment desk corner, city-view workspace) shot with natural window light, "
        "phone-camera-real framing (not a studio product shot) -- the environment itself is the "
        "message. NEVER depict an identifiable person, a face, or a body positioned as the frame's "
        "subject; hands-on-keyboard, a monitor glow, a chair, a coffee cup, a shadow on the wall are "
        "all permitted, a face or full figure is not (persona policy). Reserve a plain, low-detail "
        "region per the reserved-zone fragment supplied with this brief -- keep that region free of "
        "clutter, high-contrast edges, or busy texture; the caption is composited there after "
        "generation, never rendered by you."
    ),
),
```

**Layout skeleton (5 slots, 1080×1350):**

| Slot role | Ground | Layout | Text budget | text_render_mode |
|---|---|---|---|---|
| `cover` | photoreal environment (diffusion) | two-line hook caption top-left quadrant, 20–34% Y, floats on open wall/sky (the reserved zone) | ≤2 lines, title ≤8 words | `composited` (case (b)) |
| `body` (slide 2) | photoreal environment (diffusion), same family, different room/angle | kicker (tool/step name) 18–23% Y + 2–3-line caption 24–34% Y, top-left | title ≤8, body ≤16 | `composited` |
| `prompt_quote` (slide 3) | same | third tool/step beat, identical shape to `body` — no verbatim-prompt content in this system, same convention as §2.2/§2.4 | title ≤8, body ≤16 | `composited` |
| `body` (slide 4) | same | same skeleton, next tool/step | title ≤8, body ≤16 | `composited` |
| `end_card` | photoreal environment (diffusion, shipped default; documented operator override: programmatic cream closer) | quiet closing frame, follow/save CTA top-left | title ≤8, body ≤12 | `composited` |

**Zones (machine-readable — full `style_systems:` entry shape; §3.1 appends verbatim):**
```yaml
ig_lifestyle_stack:
  display_name: "Lifestyle Stack"
  format_class: photoreal
  topic_tag: tool_stack_howto
  destination: instagram_feed
  register: photographic_ugc
  archetype: aspirational-lifestyle-scene
  generation_mode: aspirational_lifestyle_scene   # amended directive above
  ground_recipe: photoreal_environment            # NEW recipe name — a diffusion scene family, not a hex
  palette:
    caption_ink: "#FFFFFF"
    caption_ink_alt: "#1E1B2E"    # dark alternate when the reserved zone lands on a light sky/wall
  type:
    caption_family: "Montserrat SemiBold"         # sans, deliberately — Montserrat stays for non-serif-editorial systems (§3.5)
    caption_fallback: "assets/fonts/NotoSans-Variable.ttf@630"
  slots:
    cover:
      ground_source: diffusion
      text_render_mode: composited                # caption composited over the diffused photo — case (b)
      reserved_text_zone: [0.10, 0.20, 0.60, 0.14]   # == the headline zone rect below, verbatim
      zones:
        - {name: headline, rect_pct: [0.10, 0.20, 0.60, 0.14], type_scale: 0.045, weight: SemiBold, align: left, max_lines: 2, color: "#FFFFFF"}
    body:      # slides 2 and 4 — one tool/step per slide
      ground_source: diffusion
      text_render_mode: composited
      reserved_text_zone: [0.10, 0.18, 0.60, 0.16]   # bounding rect of kicker + body below
      zones:
        - {name: kicker, rect_pct: [0.10, 0.18, 0.50, 0.05], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#FFFFFF"}
        - {name: body, rect_pct: [0.10, 0.24, 0.60, 0.10], type_scale: 0.032, weight: Regular, align: left, max_lines: 3, color: "#FFFFFF"}
    prompt_quote:   # slide 3 — third tool/step beat, identical shape to body
      ground_source: diffusion
      text_render_mode: composited
      reserved_text_zone: [0.10, 0.18, 0.60, 0.16]
      zones:
        - {name: kicker, rect_pct: [0.10, 0.18, 0.50, 0.05], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#FFFFFF"}
        - {name: body, rect_pct: [0.10, 0.24, 0.60, 0.10], type_scale: 0.032, weight: Regular, align: left, max_lines: 3, color: "#FFFFFF"}
    end_card:
      ground_source: diffusion      # shipped default — an operator MAY override to programmatic cream to visually "close" the sequence
      text_render_mode: composited
      reserved_text_zone: [0.10, 0.20, 0.60, 0.18]   # bounding rect of cta + subtext below
      zones:
        - {name: cta, rect_pct: [0.10, 0.20, 0.60, 0.10], type_scale: 0.045, weight: SemiBold, align: left, max_lines: 2, color: "#FFFFFF"}
        - {name: subtext, rect_pct: [0.10, 0.32, 0.60, 0.06], type_scale: 0.026, weight: Regular, align: left, max_lines: 2, color: "#FFFFFF"}
```

**Palette:** caption ink `#FFFFFF` (plain, no card/pill/highlight treatment — minimal-effort styling
is the native signal), dark alternate `#1E1B2E` when the reserved zone lands light. No brand accent
appears on the canvas at all — deliberately: any designed element would break the "reads as content,
not ad" property this class wins on (§5.10's stand-alone test).

**Type scale:** caption intended `Montserrat SemiBold` (fallback `NotoSans-Variable.ttf@630`) —
deliberately the sans, NOT the round-2 serifs: the reference caption reads as a native phone-camera
slideshow caption, and a display serif would read as design. Cover caption 4.5% of canvas height, max
2 lines; body kicker 2.6%, body caption 3.2%, max 3 lines.

**Texture/ground:** `ground_source: diffusion` on ALL 5 slots — the library's first full-photoreal
system (§2.7). **What the N-D diffusion prompt may describe:** room type, light quality (soft window
light / golden hour / cool overcast), 2–3 concrete environment props (desk material, one device, one
personal object), camera framing (eye-level, slightly off-center, phone-camera-real — never a hero
product angle), and the reserved-zone fragment. **Never:** any person/face/figure-as-subject, any
on-image text of any kind (all captions are composited — no permitted cover spans exist in this
system), any UI/screen content, any brand or tool logo (the tool is named in the composited caption,
not depicted — a deliberate creative simplification vs. `photoreal_lifestyle_sticker`'s icon step;
with no mark requested, §2's logo policy and its QA gate simply never engage for this system).

**Text budget:** `max_title_words: 8`, `max_body_words: 16` per slide — deliberately tighter than the
destination caps: this system's thesis is "the photo does the work, the words don't have to."

**Gibberish-proofing:** zero diffusion text anywhere (case (b) universally) — the gibberish-text risk
per slot is identical to any single-diffusion-slot system, just paid 5× per asset. The residual risk
is the reserved zone coming back busier than requested: `check_ground_safe_zone` catches it and the
slot degrades to a programmatic ground (decision-logged), per the §2 convention bullet. Cost flag for
`RenderContract` budget planning: 5 diffusion calls per asset, the most expensive system in the
library (§2.7's token table).

**Register/mapping:** `register=photographic_ugc` (reused), `archetype=aspirational-lifestyle-scene`
(reused), `generation_mode=aspirational_lifestyle_scene` (existing key, amended directive). No new
keys — one amended directive.

---

### 2.11 `ig_scene_hook` — Instagram "Scene Hook" (round 2, photoreal)

**Topic:** format-generic provocative-but-defensible hook topics; `topic_tag: scene_hook_generic`
(§4.1). **Intent:** the #1-weighted item in the entire studied corpus (2.17M views, weighted 51.1;
`DESIGN_EXPANSION.md` §A.2) is a dramatic photoreal/illustrated scene with a punchy caption. B2B
adaptation keeps the *visual grammar* (cinematographic lighting, negative space, real sense of place)
and rejects the literal content (fear-bait claims, robot-apocalypse imagery, invented drama personas)
— the mood comes from lighting and composition, never from fabricated stakes. The scene device is
**hook-only** in the source corpus (every winning exemplar is a single dramatic image, never a 5-panel
drama sequence), so slides 2/4/5 revert to the library's existing programmatic dark-terminal recipe —
keeping the photoreal spend where the data shows it earns attention, and halving diffusion cost vs.
§2.10.

**Keys:** `register: photographic_ugc` (reused) · `archetype: cinematic-scene-hook` — **NEW** (the one
net-new archetype of round 2; neither `native-caption-frame` nor `aspirational-lifestyle-scene`
captures "dramatic lighting for emphasis, not neutral lifestyle-real") · `generation_mode:
cinematic_scene_hook` — **NEW**, proposed below. Destination `instagram_feed`, carousel, 5 slots.
`format_class: photoreal` (§4.1). LinkedIn sibling: `li_scene_hero` (§2.12) — same keys, single
`hero`, preserving the one-LI + one-IG pairing pattern.

**New `GENERATION_MODES` entry (proposal for `promptcraft.py`, illustrative — not executed by this
document):**

```python
"cinematic_scene_hook": ModeSpec(
    register="photographic_ugc",
    archetype="cinematic-scene-hook",
    composition_directive=(
        "A real-world B2B environment (glass-walled meeting room at dusk, server-room corridor, "
        "night skyline through an office window, a single desk lit only by monitor glow) shot with "
        "genuine cinematographic intent -- one dominant light source, visible rim/practical light, "
        "deep shadow falloff, a real sense of place and time of day. NEVER an identifiable person, "
        "invented robot/mascot imagery, or a fabricated catastrophe/drama scene -- the mood comes "
        "from lighting and composition alone, never from invented stakes or synthetic characters. "
        "Reserve a plain, low-detail region per the reserved-zone fragment supplied with this brief, "
        "placed in the frame's own natural negative space (sky, wall, shadow); the caption is "
        "composited there after generation, never rendered by you."
    ),
),
```

**Layout skeleton (5 slots, 1080×1350):**

| Slot role | Ground | Layout | Text budget | text_render_mode |
|---|---|---|---|---|
| `cover` | photoreal cinematic scene (diffusion) | bold centered hook caption in lower third, 66–80% Y (the reserved zone) | ≤2 spans, ≤6 words/span — kept as a CREATIVE constraint even though composited (§2.8) | `composited` (case (b)) |
| `body` (slide 2) | programmatic dark terminal `#1E1B2E` | kicker + headline + payoff body — reuses §2.6's terminal recipe hexes | title ≤8, body ≤24 | `composited` |
| `prompt_quote` (slide 3) | photoreal cinematic scene (diffusion) | second scene beat — bookends the payoff slides in a hook/payoff/scene/payoff/close rhythm | ≤2 spans, ≤6 words/span (same creative constraint) | `composited` |
| `body` (slide 4) | programmatic dark terminal | same skeleton as slide 2 | title ≤8, body ≤24 | `composited` |
| `end_card` | programmatic dark terminal | follow/save CTA | title ≤8, body ≤12 | `composited` |

**Zones (machine-readable — full `style_systems:` entry shape; §3.1 appends verbatim):**
```yaml
ig_scene_hook:
  display_name: "Scene Hook"
  format_class: photoreal
  topic_tag: scene_hook_generic
  destination: instagram_feed
  register: photographic_ugc
  archetype: cinematic-scene-hook          # NEW archetype — the one net-new archetype key of round 2
  generation_mode: cinematic_scene_hook    # NEW mode — proposed above
  ground_recipe: photoreal_cinematic       # NEW recipe name — a diffusion scene family, not a hex
  palette:
    caption_ink: "#FFFFFF"
    terminal_ground: "#1E1B2E"             # payoff slides reuse ig_prompt_sheet's terminal palette (§2.6)
    terminal_accent: "#00A39A"
    terminal_body_ink: "#EDEAE3"
  type:
    caption_family: "Montserrat Bold"
    caption_fallback: "assets/fonts/NotoSans-Variable.ttf@700"
    body_family: "Montserrat Regular"
    body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
  slots:
    cover:
      ground_source: diffusion
      text_render_mode: composited
      reserved_text_zone: [0.12, 0.66, 0.76, 0.14]   # == the headline zone rect below, verbatim
      zones:
        - {name: headline, rect_pct: [0.12, 0.66, 0.76, 0.14], type_scale: 0.06, weight: Bold, align: center, max_lines: 2, color: "#FFFFFF"}
    body:       # slides 2 and 4 — programmatic payoff, deliberate register break (see intent above)
      ground_source: programmatic
      text_render_mode: composited
      ground_recipe: dark_terminal
      zones:
        - {name: kicker, rect_pct: [0.12, 0.16, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#00A39A"}
        - {name: headline, rect_pct: [0.12, 0.24, 0.76, 0.16], type_scale: 0.06, weight: SemiBold, align: left, max_lines: 2, color: "#FFFFFF"}
        - {name: body, rect_pct: [0.12, 0.46, 0.76, 0.30], type_scale: 0.030, weight: Regular, align: left, max_lines: 5, color: "#EDEAE3"}
    prompt_quote:   # slide 3 — second scene beat, back to photoreal
      ground_source: diffusion
      text_render_mode: composited
      reserved_text_zone: [0.12, 0.66, 0.76, 0.14]
      zones:
        - {name: headline, rect_pct: [0.12, 0.66, 0.76, 0.14], type_scale: 0.05, weight: Bold, align: center, max_lines: 2, color: "#FFFFFF"}
    end_card:
      ground_source: programmatic
      text_render_mode: composited
      ground_recipe: dark_terminal
      zones:
        - {name: cta, rect_pct: [0.12, 0.40, 0.76, 0.10], type_scale: 0.045, weight: SemiBold, align: center, max_lines: 2, color: "#FFFFFF"}
        - {name: subtext, rect_pct: [0.12, 0.52, 0.76, 0.08], type_scale: 0.028, weight: Regular, align: center, max_lines: 2, color: "#EDEAE3"}
```

**Palette:** scene slots — plain white caption on the photograph's own negative space, no card, no
accent. Payoff slots — `#1E1B2E` ground / `#00A39A` kicker (reusing §2.6's terminal recipe hexes — one
recipe, multiple consumers) plus `#EDEAE3` body ink, shared with §2.9. §6's caveat applies twice over: describe the payoff
ground as "a dark terminal-style card," never with the `hype` register's `near-black` token, and
describe scenes as "dusk"/"night-lit"/"monitor glow," never "near-black."

**Type scale:** hook caption intended `Montserrat Bold` (fallback `NotoSans-Variable.ttf@700`), 6% of
canvas height (5% on the mid-carousel beat), max 2 lines. Payoff slides as tabulated.

**Texture/ground:** two diffusion-touched slots (`cover`, `prompt_quote` — §2.7). **What the N-D
prompt may describe:** the named environment archetype (glass meeting room / server corridor /
night-skyline office / single lit desk), one dominant light source + its color temperature,
time-of-day, 2–3 concrete props, the reserved-zone fragment. **Never:** any person, any
robot/mascot/creature, any invented statistic or claim, any on-image text (captions are composited;
this system has no diffusion-text spans), any screen/UI content beyond "monitor glow" as a light
source (glow, not chrome — an unreadable light source is not UI).

**Text budget:** scene captions ≤2 spans × ≤6 words — a creative constraint mirroring the source
pattern's punchy brevity, kept even though composited text carries no technical span limit (§2.8);
payoff slides standard ≤8/≤24.

**Gibberish-proofing:** zero diffusion text; scene slots carry the reserved-zone degrade path (§2
convention bullet); payoff slots are fully programmatic. The fabricated-drama failure class is policed
by the directive's own NEVER list plus §5.10's stand-alone test (a scene must read as a finished
photograph, not a fear-bait poster).

**Register/mapping:** `register=photographic_ugc` (reused), `archetype=cinematic-scene-hook`
(**NEW**), `generation_mode=cinematic_scene_hook` (**NEW**).

---

### 2.12 `li_scene_hero` — LinkedIn "Scene Hero" (round 2, photoreal)

**Topic:** same class as §2.11 (`topic_tag: scene_hook_generic`) — the LinkedIn single-`hero` sibling,
preserving the one-LI + one-IG pairing every round-1 intent used (§2.1/§2.2). **Intent:** identical to
§2.11's cover — one cinematic B2B environment, one short composited hook plus one qualification line;
no carousel, so no payoff slides.

**Keys:** `register: photographic_ugc` (reused) · `archetype: cinematic-scene-hook` (NEW in §2.11,
shared) · `generation_mode: cinematic_scene_hook` (NEW in §2.11, shared). Destination `linkedin`,
single `hero` slot. `format_class: photoreal` (§4.1).

**Layout skeleton (`hero` slot, 1920×1080):**

| Element | Y-band | X-band | Notes |
|---|---|---|---|
| Cinematic scene ground | full bleed | full bleed | diffusion; reserved zone below kept plain |
| Hook headline | 62–80% | 12–88% | ≤2 spans ×≤6 words (creative constraint, §2.11) |
| Qualification line | 80–88% | 12–88% | sourced/qualified per the claim gate when a number appears (`RENDER_CONTRACT_SPEC.md` §6) |
| Handle | bottom-right | inside margin | |

**Zones (machine-readable — full `style_systems:` entry shape; §3.1 appends verbatim):**
```yaml
li_scene_hero:
  display_name: "Scene Hero"
  format_class: photoreal
  topic_tag: scene_hook_generic
  destination: linkedin
  register: photographic_ugc
  archetype: cinematic-scene-hook
  generation_mode: cinematic_scene_hook
  ground_recipe: photoreal_cinematic
  palette:
    caption_ink: "#FFFFFF"
  type:
    caption_family: "Montserrat Bold"
    caption_fallback: "assets/fonts/NotoSans-Variable.ttf@700"
    body_family: "Montserrat Regular"
    body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
  slots:
    hero:
      ground_source: diffusion
      text_render_mode: composited
      reserved_text_zone: [0.12, 0.62, 0.76, 0.26]   # bounding rect of headline + qualification below
      zones:
        - {name: headline, rect_pct: [0.12, 0.62, 0.76, 0.18], type_scale: 0.07, weight: Bold, align: left, max_lines: 2, color: "#FFFFFF"}
        - {name: qualification, rect_pct: [0.12, 0.80, 0.76, 0.08], type_scale: 0.03, weight: Regular, align: left, max_lines: 1, color: "#FFFFFF"}
```

**Palette / Type scale / Texture-ground / Gibberish-proofing:** identical to §2.11's scene slots (one
recipe, two destinations); text budget `max_title_words: 12` / `max_body_words: 18` (the unchanged
`linkedin.hero` `SlotSpec`), with the ≤2×≤6 creative constraint on the hook. The single diffusion call
per asset makes this the cheapest photoreal system (§2.7).

**Register/mapping:** all three keys shared with §2.11 — no additional new keys beyond §2.11's two.

---

### 2.13 `ig_operator_grid` — Instagram "Operator Grid" (round 2, editorial-grotesque)

**Topic:** agency/playbook/framework how-to content; `topic_tag: agency_playbook_howto` (§4.1).
**Intent:** the operator-supplied editorial-grotesque carousel reference (`DESIGN_EXPANSION.md` §A.3),
formalized: off-white **grid-paper** ground (ruled both axes — structured notebook paper, deliberately
distinct from the speck-grain `paper` recipe), heavy grotesque near-black headline with ONE
accent-colored emphasis phrase, a highlighter bar, a small photoreal inset, printed-zine
masthead/footer furniture. It reads as a content format (carousel-as-mini-magazine-spread), not a
promotional format — the "more variety than Canva-like cards" answer that does NOT lean on diffusion
spend (its only diffusion surface is a ~6%-of-canvas inset).

**Keys:** `register: editorial` (reused — the inset is a minority element, same classification logic
as §2.2's screenshot inset not flipping that system photographic) · `archetype:
editorial-grotesque-grid` — **NEW** (none of the 16 existing archetypes names a grid-paper ground or a
color-emphasis-phrase headline; `editorial-carousel` is the serif/Didone family and would collide
semantically) · `generation_mode: grid_photo_inset` — **NEW**, proposed below. Destination
`instagram_feed`, carousel, 5 slots. `format_class: editorial_grotesque` (§4.1).

**Why the mode is NOT `designed_card` (deviation from `DESIGN_EXPANSION.md` §B.3, resolved here).**
The source proposal reused `designed_card`; this document instead binds a new mode because
`generation_mode`'s only consumer is N-D, and N-D runs exactly once for this system — on the photo
inset, the sole diffusion surface (§2.7). `designed_card`'s generic directive says nothing about
crafting a small photographic inset; binding the mode to the only surface it will ever describe keeps
one-mode-per-asset intact and gives the inset a real directive instead of an inherited irrelevant one.

**New `GENERATION_MODES` entry (proposal, illustrative):**

```python
"grid_photo_inset": ModeSpec(
    register="editorial",
    archetype="editorial-grotesque-grid",
    composition_directive=(
        "A small, quiet, real-feeling desk/tool close-up photograph for a rounded-corner inset card "
        "(rolled paper and drafting tools, a laptop corner closed or angled away, a notebook and pen) "
        "-- soft natural light, shallow depth of field, genuinely photographic. The inset must "
        "contain NO readable text, no screen or UI chrome, and no person. This directive governs "
        "ONLY the inset surface; the canvas's grid-paper ground, headline, highlighter bar, and all "
        "furniture are programmatic and are never described to the image model."
    ),
),
```

**Layout skeleton (5 slots, 1080×1350):**

| Slot role | Ground | Layout | Text budget | text_render_mode |
|---|---|---|---|---|
| `cover` | grid paper `#F3F1E9` (programmatic) | masthead (wordmark left, theme label right, hairline rule) + outline kicker pill + 3–4-line grotesque headline with ONE indigo emphasis phrase + amber highlighter bar + body line + micro-footnote + footer (swipe pill, page badge); optional photo inset top-right | title ≤10 (headline), highlight line ≤8 | `composited` |
| `body` (slide 2) | grid paper | masthead + kicker pill + headline + body stack + footer | title ≤8, body ≤24 | `composited` |
| `prompt_quote` (slide 3) | grid paper | third body beat, identical shape — same convention as every other system's slide 3 | title ≤8, body ≤24 | `composited` |
| `body` (slide 4) | grid paper | same skeleton | title ≤8, body ≤24 | `composited` |
| `end_card` | grid paper | follow/save CTA + footer furniture | title ≤8, body ≤12 | `composited` |

**Zones (machine-readable — full `style_systems:` entry shape; §3.1 appends verbatim):**
```yaml
ig_operator_grid:
  display_name: "Operator Grid"
  format_class: editorial_grotesque
  topic_tag: agency_playbook_howto
  destination: instagram_feed
  register: editorial
  archetype: editorial-grotesque-grid      # NEW archetype (shared with nothing else)
  generation_mode: grid_photo_inset        # NEW mode — inset-only, see rationale above
  ground_recipe: grid_paper                # NEW programmatic recipe: paper base + thin ruled grid overlay
  palette:
    ground: "#F3F1E9"
    grid_line: "#E4E0D2"                   # faint ruled grid, both axes, ~6-8% opacity equivalent
    headline_ink: "#221F1C"
    emphasis_ink: "#302B87"                # operator-locked: the reference's red emphasis maps to brand indigo (§3.6)
    highlight_bar: "#E8A63B"               # operator-locked single-purpose amber token, DESIGN_EXPANSION §A.3 option 1 (§3.6; documented zero-new-token fallback: #00A39A)
    body_ink: "#332F2B"
    footer_ink: "#6B655C"
  type:
    display_family: "Grotesque sans, heavy weight (not yet acquired -- e.g. Inter Black as the OFL-licensed pick)"
    display_fallback: "assets/fonts/NotoSans-Variable.ttf@700"
    body_family: "Montserrat Regular"
    body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
  slots:
    cover:
      ground_source: programmatic          # grid-paper ground is 100% programmatic — never diffused
      text_render_mode: composited
      logo_zone: [0.08, 0.06, 0.30, 0.04]           # masthead brand wordmark, top-left
      decorative_zone: [0.55, 0.06, 0.37, 0.04]     # masthead running theme label + hairline rule, drawn programmatically
      photo_inset:                                   # typed like §2.2's screenshot_inset, but the OPPOSITE contract — see note below
        mode: optional
        rect_pct: [0.62, 0.15, 0.30, 0.20]
        ground_source: diffusion
        corner_radius_pct: 8
        shadow_pct: 2
        fallback: omit                               # optional element: absent, not placeholdered
      zones:
        - {name: kicker, rect_pct: [0.12, 0.18, 0.50, 0.05], type_scale: 0.024, weight: SemiBold, align: left, max_lines: 1, color: "#221F1C"}   # black-outline pill drawn programmatically behind this zone
        - {name: headline, rect_pct: [0.12, 0.25, 0.48, 0.30], type_scale: 0.075, weight: Bold, align: left, max_lines: 4, color: "#221F1C"}    # narrowed to 48% w when photo_inset present; 0.60 w variant when absent. ONE run recolors to emphasis_ink at CRAFT time — rich-text dependency, flagged below
        - {name: highlight_line, rect_pct: [0.12, 0.60, 0.68, 0.06], type_scale: 0.032, weight: Bold, align: left, max_lines: 1, color: "#221F1C"}   # rendered on a solid highlight_bar rect drawn behind this zone
        - {name: body, rect_pct: [0.12, 0.70, 0.68, 0.10], type_scale: 0.026, weight: Regular, align: left, max_lines: 3, color: "#332F2B"}
        - {name: footnote, rect_pct: [0.12, 0.84, 0.68, 0.05], type_scale: 0.020, weight: Regular, align: left, max_lines: 2, color: "#6B655C"}
      footer_zone: [0.08, 0.90, 0.84, 0.06]          # hairline rule + swipe pill (left) + page-number badge (right), programmatic
    body:      # slides 2 and 4
      ground_source: programmatic
      text_render_mode: composited
      logo_zone: [0.08, 0.06, 0.30, 0.04]
      zones:
        - {name: kicker, rect_pct: [0.12, 0.18, 0.50, 0.05], type_scale: 0.024, weight: SemiBold, align: left, max_lines: 1, color: "#221F1C"}
        - {name: headline, rect_pct: [0.12, 0.25, 0.76, 0.24], type_scale: 0.065, weight: Bold, align: left, max_lines: 3, color: "#221F1C"}
        - {name: body, rect_pct: [0.12, 0.54, 0.76, 0.28], type_scale: 0.028, weight: Regular, align: left, max_lines: 6, color: "#332F2B"}
      footer_zone: [0.08, 0.90, 0.84, 0.06]
    prompt_quote:   # slide 3 — third body beat
      ground_source: programmatic
      text_render_mode: composited
      logo_zone: [0.08, 0.06, 0.30, 0.04]
      zones:
        - {name: kicker, rect_pct: [0.12, 0.18, 0.50, 0.05], type_scale: 0.024, weight: SemiBold, align: left, max_lines: 1, color: "#221F1C"}
        - {name: headline, rect_pct: [0.12, 0.25, 0.76, 0.24], type_scale: 0.065, weight: Bold, align: left, max_lines: 3, color: "#221F1C"}
        - {name: body, rect_pct: [0.12, 0.54, 0.76, 0.28], type_scale: 0.028, weight: Regular, align: left, max_lines: 6, color: "#332F2B"}
      footer_zone: [0.08, 0.90, 0.84, 0.06]
    end_card:
      ground_source: programmatic
      text_render_mode: composited
      zones:
        - {name: cta, rect_pct: [0.12, 0.40, 0.76, 0.10], type_scale: 0.045, weight: Bold, align: center, max_lines: 2, color: "#221F1C"}
        - {name: subtext, rect_pct: [0.12, 0.52, 0.76, 0.08], type_scale: 0.026, weight: Regular, align: center, max_lines: 2, color: "#332F2B"}
      footer_zone: [0.08, 0.90, 0.84, 0.06]
```

**`photo_inset` is NOT a screenshot inset.** It reuses §2.2's typed field *shape* (rect, corner
radius, shadow, fallback) but carries the OPPOSITE contract: §2.2's `screenshot_inset` is
`required_or_omit` + composited-real-asset-only (never diffused); this `photo_inset` is `optional` +
`ground_source: diffusion` (a generated text-free photograph, never a screenshot, never a real asset
dependency). The field is renamed (`photo_inset`, not `screenshot_inset`) precisely so an implementer
can never conflate the two and accidentally diffuse a "screenshot" (§5.4).

**Palette:** ground `#F3F1E9` + grid line `#E4E0D2`; headline ink `#221F1C`; **emphasis phrase
`#302B87`** (operator-locked mapping of the reference's red — §3.6); **highlighter bar `#E8A63B`**
(the one new single-purpose token, amber, black-ink text on top — §3.6, with `#00A39A` as the
documented zero-new-token fallback); body ink `#332F2B`; footer ink `#6B655C`. The two accents never
appear on the same element: indigo = in-headline emphasis only, amber = highlighter bar only.

**Type scale:** headline intended heavy grotesque (Inter Black as the OFL pick — a THIRD acquisition,
separate from §3.5's serif pair and §2.6's mono, flagged not bundled) — fallback
`NotoSans-Variable.ttf@700`. Headline 6.5–7.5% of canvas height, max 3–4 lines, tight tracking; kicker
2.4%; highlight line 3.2%; body 2.6–2.8%; footnote 2.0%.

**Rich-text dependency (flagged, not resolved — the preamble's second build dependency).** The
mid-headline emphasis phrase needs ONE run inside a single `OnImageText.title` string rendered in
`emphasis_ink` while the rest renders in `headline_ink` — every other system colors a zone uniformly.
This is a genuinely new `layout.py`/`typeset.py` capability (rich-text run styling within one zone),
shared by §3.1's `headline_split` weight-split device (one capability, two consumers). Until built,
the safe interim behavior is **omit the color swap** and render the whole headline in `headline_ink` —
never approximate it by asking diffusion to render colored text.

**Texture/ground:** `ground_source: programmatic` everywhere except the optional cover `photo_inset`
(§2.7 — 1 of 5 slots, partial-area, the smallest diffusion footprint of any diffusion-touched system).
**What the N-D prompt may describe (inset only):** one concrete desk/tool vignette, soft natural
light, shallow depth of field. **Never:** any readable text, any screen/UI, any person.

**Text budget:** headline ≤10 (cover) / ≤8 (body), body ≤24, highlight line ≤8 words, footnote ≤12 —
all inside the destination caps (§2.8).

**Gibberish-proofing:** every text element on every slot is composited; the only diffusion surface is
a deliberately text-free photograph, checked by §5.8 (no device mockups), §5.4/`ui_fidelity_ok` (no
UI), and the directive's own NO-readable-text rule. Masthead/footer furniture is programmatic
vector/text, zero diffusion.

**Register/mapping:** `register=editorial` (reused), `archetype=editorial-grotesque-grid` (**NEW**),
`generation_mode=grid_photo_inset` (**NEW**).

---

### 2.14 `li_product_render` — REJECTED (recorded, not specced)

Judged and excluded; operator-confirmed 2026-08-07. The candidate reference
(`DESIGN_EXPANSION.md` §A.4's polished product-render ad) is simultaneously the **worst-performing
item in the entire studied corpus** (weighted -9.02, vs. +42.53 for §2.10's winning class) and a
near-perfect checklist of what this document already forbids: gradient-mesh/radial-glow ground
(§5.5/§5.6), benefit-pill checkmark row (§5.2/§5.7), a fully invented device-mockup UI showing a
fabricated website (§5.4/§5.8), an invented human persona presented as real inside that UI
(`RENDER_CONTRACT_SPEC.md:62-68`), and urgency/price CTA-banner grammar (§5.9). Building it would
mean either shipping something the engine's own governance blocks on every asset, or sanitizing it
into a weaker `li_signal_card`/`ig_stat_slab` that keeps none of the reference's distinguishing moves
— the legitimate underlying need ("depict a tool/result") is already better served by those two
systems. Recorded here with the same weight as the ship decisions so nobody re-proposes it on
instinct: the performance data and the existing guardrails agree, independently.

---

### 2.15-2.22 Round-4/5/6 systems — nine shapes, eighteen entries

*Authored 2026-08-08 from `reference/OPERATOR_FAVORITES_DNA.md` (the operator's ten hand-picked
renders) plus the live round-4/5/6 prompts and outputs in `simulation/round{4,5,6}/`. Every recipe
below is a **deconstruction of a render the operator actually approved**, not a proposal — the
prompts that produced them are on disk and are the source of the token lists here.*

**Shared conventions for all eighteen entries (stated once, never repeated per system):**

- **Two entries per shape, `ig_*` and `li_*`.** The `ig_*` entry is authored in full below. **The
  `li_*` entry is a mechanical derivation, not a second recipe:** identical `format_class`,
  `register`, `archetype`, `generation_mode`, palette and type block; a **single `hero` slot** whose
  zones are the `ig_*` cover's zones re-projected onto 16:9 (the y-bands compress, the x-bands are
  unchanged — `layout.py` does this at load time from one declared rect, so the number lives once).
  This exists because stage-1 assignment (§4.1 step 5) needs a member of every class on both
  destinations; without it, LinkedIn assets would substitute to `designed_card` several times a run
  and the variety quota would quietly collapse into one class.
- **Format shapes.** Every `ig_*` entry declares both the `single` (cover only) and `carousel`
  (5-slot) slot sets; the run picks one per asset via the evidence gate (§4.1). For the illustration
  and meme shapes the carousel's slides 2-5 are **`templated_diffusion` cards in the same visual
  language**, never five separate illustrations — that is what keeps N-D at one call per asset.
- **D1 ground.** Warm cream `#F6F1E7` with the shared `paper_grain` spec, unless the row says
  cinematic-dark. No mid-gray, cold, saturated or gradient ground is any system's default.
- **D2 type.** One voice per system — editorial serif (Playfair spirit) **or** heavy grotesque —
  oversized, 30-60% of canvas, with **exactly one** emphasis token: teal `#00A39A` by default,
  italic indigo `#302B87` for serif questions, amber `#E8A63B` **only** on numerals and times.
- **D3 furniture.** `kicker_zone` (letterspaced small caps, top) and `wordmark_zone`
  (`HYPEDIGITALY`, letterspaced caps, footer) on every card-class slot. These are `LayoutRecipe`
  furniture fields, not `zones:` entries — they carry no gated `on_image_text`.
- **Accent hexes are pinned in the prompt** (§3.6, F10) and the screens-off sentence rides every
  scene/illustration prompt (F11).

---

#### 2.15 `ig_serif_statement` / `li_serif_statement` — "Serif Statement" (`format_class: serif_editorial`)

**Source:** DNA pick 10 (`round2/1_serif_statement_en`). **Intent:** the single most distilled shape
in the library — one belief, set enormous, nothing else on the canvas. It is the class default for
`serif_editorial` because it is the most topic-agnostic member: any thesis fits it.

**Keys:** `register: editorial` · `archetype: statement-card` (existing) · `generation_mode:
designed_card` (existing — no new mode). **Ground:** cream `#F6F1E7` + paper grain. **Type:** huge
high-contrast serif, left-aligned, 3 lines, near-black ink `#2B2B2B`, with **one clause in italic
deep indigo** `#302B87`; teal caps kicker; one hairline rule under the headline block.
**Text budget:** cover title ≤12 words (it is one sentence broken over three lines); carousel body
slides ≤24. **Emphasis rule:** the italic indigo clause is the single emphasis token — never a
second colour, never a highlight bar.

*Live exemplar (EN, verbatim from the picked render):* "AI won't take your job. / A company that /
uses it will." — emphasis on "uses it will."

---

#### 2.16 `ig_artifact_showcase` / `li_artifact_showcase` — "Artifact Showcase" (`format_class: artifact_showcase`, NEW class)

**Source:** DNA picks 5, 6, 7, 8 — four picks, one shape. **Intent:** D4's centrepiece rule made a
system: a tangible, rounded (20-24px), soft-shadowed object carrying **real brand marks**, with the
typography above it. This is the class that turns "we use these tools" into something that looks
made rather than listed, and it is where the manifest/fetch ladder earns its keep — *the two picks
fed real reference assets beat the verbal-guess variants of the same concept.*

**Keys:** `register: editorial` · `archetype: statement-card` / `screenshot-as-proof` depending on
device · `generation_mode: designed_card`. **Ground:** cream `#F6F1E7`, or white with a very faint
dot grid for the `node_diagram` device (pick 7). **Type:** heavy grotesque title, two lines, one teal
emphasis; regular-weight supporting line.

**`artifact_device` — the D4 library, one field, four values** (selected by topic tag, then by
within-class seeded rotation; the chosen device is a decision event):

| Device | Shape | Real-asset source |
|---|---|---|
| `browser_frame` | macOS-style chrome (traffic lights, 20-24px radius, soft shadow) around a site view; micro-text greeked | the tool's fetched `og:image` composited into the `artifact_zone` (§5.12 Tier 1) |
| `icon_row` | 3-5 tool rows, each = icon + bold name + one regular line | manifest `icon_url` bytes, or `description:` injection |
| `icon_lineup` | a single rule-spaced row of app icons — **an approved post format in its own right** ("tool lineup teaser", DNA pick 6), light warm-gray studio ground permitted here | manifest `icon_url` bytes |
| `node_diagram` | 3-5 rounded nodes left-to-right, smooth arrows, hand-drawn-feel annotation ticks, each node labelled | manifest `icon_url` bytes as node glyphs |

**Binding:** every tool depicted must be named in the asset's own copy (nominative use, §5.11) and
every tool named in the copy must appear here (LG2). `no fake software UI, no screenshots` is in the
template prompt verbatim except where an `artifact_zone` will be filled with fetched bytes.

*Live exemplars:* "The tools we deploy / most often" + 5 icon rows; "The lead handles itself." +
form → Zapier → Claude → Gmail node diagram.

---

#### 2.17 `ig_website_showcase` / `li_website_showcase` — "Website Showcase" (`format_class: website_showcase`, NEW class)

**Source:** DNA pick 3 (`round4/1_full_website`), F16. **Intent:** a **complete, polished, FICTIONAL
client website** inside a browser frame — invented business, invented brand — that reads as *"look
what AI can build"*. The most persuasive shape in the library for the agency offer, and the clearest
demonstration of the integrity line: **fictional UI is allowed illustration; a real product's UI is
Tier-1 real assets or nothing** (§5.12).

**Keys:** `register: editorial` · `archetype: screenshot-as-proof` (reused — the frame is the proof
device) · `generation_mode: website_showcase` (**NEW**). **Ground:** cream `#F6F1E7`. **Type:** teal
caps kicker + heavy grotesque headline over two lines, one teal emphasis; two calm body lines under
the frame.

**The greeking rule is what makes it safe and what makes it legible:** inside the browser frame **at
most three short strings are legible** (the fictional brand name, one nav or section label, one CTA
button); **every other line of site text is soft-blurred greeked marks**. This is not a stylistic
preference — it is why the render came back clean: small type is where diffusion models produce
gibberish, and greeking removes the surface entirely.

**New `GENERATION_MODES` entry (proposal, illustrative):**

```python
"website_showcase": ModeSpec(
    register="editorial",
    archetype="screenshot-as-proof",
    composition_directive=(
        "A large rounded browser-window frame with a subtle soft shadow, showing a COMPLETE, "
        "polished, realistic FICTIONAL client website for an invented small business -- an "
        "appetizing hero photograph, an elegant menu bar, a product-card row, one accent-coloured "
        "call-to-action button. The business, its name and its brand are INVENTED; this is never a "
        "depiction of any real company's site. At most three short strings inside the frame are "
        "legible; ALL other site text is soft-blurred greeked lines. No real product's UI, no "
        "screenshot of an actual application."
    ),
),
```

*Live exemplar:* "Firma bez webu? / Do večera to jde." over a fictional bakery site
("Pekárna U Lípy" / "Naše pečivo" / "Objednat").

---

#### 2.18 `ig_robot_caricature` / `li_robot_caricature` — "Robot Caricature" (`format_class: robot_caricature`, NEW class)

**Source:** DNA pick 2 (`round4/2_robot_caricature`), F17. **Intent:** premium editorial-cartoon
charm without a human face — the "AI colleague" idea made likeable. D5 makes the robot a **recurring
brand character**, so its description is pinned and reused verbatim across every system that shows
it (this system and §2.21's meme).

**Keys:** `register: editorial` · `archetype: statement-card` · `generation_mode: robot_caricature`
(**NEW**). **Ground:** flat cream `#F6F1E7`. **Type:** heavy grotesque headline above the character,
one teal emphasis; one regular body line below.

**PINNED CHARACTER (verbatim, one constant, every consumer interpolates it — never paraphrase):**

> *A charming retro cartoon robot with a rounded body in deep indigo (hex #302B87) and teal (hex
> #00A39A) accents, visible hand-drawn ink outlines, a friendly single-lens eye, no human face.
> Premium editorial-cartoon register in the spirit of a New-Yorker illustration — never childish
> clip-art.*

The round-6 v2 render drifted slightly from this description when a template paraphrased it; that is
the empirical argument for pinning it as a constant rather than re-writing it per prompt.

*Live exemplar:* "Kolega, který nikdy nespí." / "AI agent hlídá e-maily, schůzky i faktury."
— and note that this is the render that produced F18's missing ý, i.e. the exact defect the
per-glyph text gate exists to catch.

---

#### 2.19 `ig_anime_scene` / `li_anime_scene` — "Anime Scene" (`format_class: anime_scene`, NEW class)

**Source:** DNA pick 1 (`round4/4_anime_scene`), F17. **Intent:** hand-drawn, painterly, atmospheric
night scenes with cinematic lower-third type — the library's mood piece, and its second
cinematic-dark ground.

**Keys:** `register: photographic_ugc` (the ground is a rendered scene, not a card) · `archetype:
cinematic-scene-hook` (round-2 entry, reused) · `generation_mode: anime_scene` (**NEW**).
**Ground:** cinematic dark, teal/amber screen and lamp glow. **Type:** large cinematic display type
integrated into the lower third, white with one teal emphasis; serif is permitted here.

**PINNED MOOD (verbatim constant, same discipline as the robot):**

> *Hand-drawn anime-style illustration, painterly and atmospheric; a cozy dark room at night; any
> human character is seen strictly FROM BEHIND with the face never visible; teal and amber screen
> glow against the dark, warm practical light, detailed background art, soft glow. Any monitor shows
> only abstract glowing shapes — never readable UI.*

**Persona:** faceless-from-behind is the rule, not a preference (§5.13). No named characters, ever.

*Live exemplar:* "Zatímco spíte," / "AI pracuje."

---

#### 2.20 `ig_concept_dashboard` / `li_concept_dashboard` — "Concept Dashboard" (`format_class: concept_dashboard`, NEW class, **occasional rotation**)

**Source:** `round4/3_wild_dashboard`. **Intent:** an isometric fictional "mission control" diorama —
layered glass panels, node graphs, tiny conveyor belts moving document cards, small robot arms.
Spectacular, and deliberately **occasional**: the operator did not pick it despite its technical
quality, so it sits in the rotation reserve where Virlo evidence can promote it back (§4.1).

**Keys:** `register: editorial` · `archetype: tool-showcase` (reused) · `generation_mode:
concept_dashboard` (**NEW**). **Ground:** deep indigo `#1E1B2E` — the one documented exception to
D1's cream/cinematic-dark pair, allowed because the diorama *is* the ground.

**Two rules that are not negotiable for this system:** every panel's text is **greeked/illegible
marks** (the same mechanism that keeps §2.17 clean), and it must read as *clearly an artistic
concept, not any real software product* — stated in the directive verbatim.

**Anti-ad exemption (the only one outside `brand_promo`):** the operator relaxes **§5.6** (no
radial-glow / premium-gradient grounds) **for this class only** — the glow is the diorama's light,
not an ad tell. Recorded as `hard_dont_exemptions: [5.6]` and enforced by consistency check 11:
no other organic system may claim it.

*Live exemplar:* "Velín vaší firmy." / "Všechny procesy na jednom místě. Řídí je AI agenti."

---

#### 2.21 `ig_meme_reaction` / `li_meme_reaction` and `ig_deadpan_memo` / `li_deadpan_memo` — the meme pair (`format_class: meme_reaction` / `deadpan_memo`, NEW classes, **reserved slot**)

**Source:** `simulation/round6/` M1/M2 and the operator-validated v2 renders; F20. **Cadence:** these
two share a **reserved per-run slot** (default 1, dial 0-2), alternating by seeded rotation — they
are *not* in the occasional pool (`PLAN.md` §13 item 25). Their humour angle is topical: it comes
from the run's Virlo trends through the normal topic stage.

**`meme_reaction`** — two-panel vertical reaction meme, cream ground, thin ink divider, vintage
comic texture, heavy grotesque captions with one teal emphasis, wordmark footer.
**Canonical shape (round-6 v2, supersedes v1):** **top panel = human chaos** (a from-behind or
face-obscured cartoon human drowning in manual busywork), **bottom panel = the pinned brand robot,
serene** (leaning back, feet up, one tiny glowing checkmark). **Symmetric, time-stamped captions**
— "Your ops team at 11 PM." / "The AI agent at 11 PM." The parallel structure *is* the joke.
`generation_mode: meme_reaction` (**NEW**); the robot description is §2.18's pinned constant,
interpolated, never re-written.

**`deadpan_memo`** — satirical official-document card on cream paper: `INTERNAL MEMO` letterhead
with hairline rules, a huge editorial-serif deadpan announcement, one calm serif body line, a
slightly rotated distressed **teal rubber-stamp** device ("APPROVED BY AI"), optional gilded frame,
wordmark footer. **Second approved device variant: the RIP tombstone** — celebratory-graveyard
grammar (party hat, confetti, the robot laying a flower) for retiring a process. `generation_mode:
deadpan_memo` (**NEW**), `artifact_device: stamp | tombstone`.

**Guardrails, binding for both (F20, `PLAN.md` §13 items 23-24):**

1. **`instant_read`.** The joke lands in about **one second**, on universally-known visual grammar
   (reaction contrast, RIP tombstone). Captions are **minimal and symmetric**; the visuals carry the
   joke. **A paragraph caption on a meme is a failed meme** — N-F rubric item 18 says so explicitly.
2. **`visual_logic_coherent`.** The depicted actor must match the caption's subject. The v1 failure
   is the canonical counter-example: the *robot* panicking about *hiring a human coordinator* is
   nonsense, because the robot is not the one who would hire. N-F rubric item 17, judged before any
   render is paid for.
3. **Satire targets PROCESSES** — meetings, copy-paste work, busywork, status reports — and
   **NEVER named people, companies, or competitor tools.** This is a hard content rule, not a
   guideline, and it is why the meme classes are safe to run unattended.
4. **The claim gate applies to any factual-sounding punchline.** A joke that asserts a number is
   still asserting a number.
5. **Persona carve-out (§5.13):** cartoon humans are permitted here — strictly from behind or with
   the face obscured, never named.

*Live exemplars:* "Somewhere, an ops coordinator just felt a disturbance."; "The Monday / status
meeting / is cancelled." + "An AI agent already read the spreadsheet."

---

#### 2.22 `ig_brand_promo` / `li_brand_promo` — "Brand Promo" (`format_class: brand_promo`, NEW class, **reserved slot, PROMOTIONAL**)

**Source:** DNA pick 4 and all three `round5/` renders; F19. **Intent:** the one deliberately
promotional shape — a confident brand ad, not a cheap flyer. **Reserved slot, default 1 per run**
(dial), **outside the Virlo quota entirely**: it is brand-guideline-driven, not evidence-driven, and
it is the only class whose copy is **config, not authored** (`PLAN.md` §13 item 20).

**Keys:** `register: editorial` · `archetype: statement-card` · `generation_mode: brand_promo_card`
(**NEW**). **Palette — strict, three validated grounds:** indigo `#302B87`, dark `#1E1B2E`, or cream
`#F6F1E7`; teal `#00A39A` CTA in every case; amber `#E8A63B` permitted as a single hand-drawn
underline. **Type:** either voice — white/off-white grotesque on the two dark grounds, high-contrast
serif with italic indigo emphasis on cream. **Furniture:** letterspaced caps wordmark top, thin
hairline rule above the CTA, and a prominent **rounded pill button**.

**The CTA text is VERBATIM from config and is never paraphrased, shortened or translated on the fly:**
`"Klikněte na odkaz v popisku"` for `cs`, its configured equivalent for `en` (the ratified caption
pattern is the link-in-bio form — §7's exemplar). The service message is drawn from
`batch_composition.reserved.brand_promo.messages` by seeded rotation, seeded with the three ratified
lines ("AI audit zdarma." / "Jak zařadit AI do firmy?" / "Chcete nasadit AI agenta?") and
extensible.

**Anti-ad exemption — the point of the class.** `brand_promo` is **exempt from §5.6-§5.10** (the
anti-ad Hard DON'Ts), which remain fully binding for every organic class: a CTA pill, a price-free
offer line and conversion-shaped furniture are *correct* here and wrong everywhere else. Recorded as
`hard_dont_exemptions: [5.6, 5.7, 5.8, 5.9, 5.10]`. **§5.1-§5.5 and §5.11 still bind** — no
collages, no clip-art, no lorem ipsum, no invented third-party UI, no inaccurate marks. Those are
integrity rules; the exemption is only about ad *aesthetics*.

---

## 3. `style_guide.yaml` amendment — exact structural proposal

Everything in this section is a **proposal**; the executor applies it to the live file. Line numbers
cite the file as read for this document (`config/style_guide.yaml`, full read 2026-08-07).

### 3.1 New top-level `style_systems:` map

Insert after the `visual_registers:` block (after line 190, before `# --- brand layer ---` at line 192).
The six round-1 entries are shown in full below (identical field set, values drawn straight from §2's
tables, with the round-2 field/palette/type amendments applied in place); the five round-2 entries are
appended per the rule after the block — their full YAML lives in §2.9–§2.13, single-sourced.

```yaml
# --------------------------------------------------------- style systems ----
# W8-11: the concrete palette/type/ground/layout recipe for the eleven named
# style systems (STYLE_SYSTEMS_SPEC.md §2; six round-1 below, five round-2
# appended per the note after this block). `register`/`archetype` here MUST
# equal a key already present in `visual_registers`/`visual_archetypes`
# above (checked by RENDER_CONTRACT_SPEC.md §4 item 5's consistency check,
# extended to also index this map). `generation_mode` MUST equal a key in
# `promptcraft.GENERATION_MODES` (adding `annotated_proof_ui`,
# `cinematic_scene_hook`, `grid_photo_inset` — see §2.2/§2.11/§2.13).
# Round-2 fields on every entry: `format_class` (§4.1 quota selector);
# `max_spans` on composited slots is a LAYOUT property, not a cap (§2's
# round-2 relaxation — the 2-span cap binds only where
# text_render_mode: diffusion).

# Round-2 shared paper-grain spec (consumed by the `paper` ground recipe —
# DESIGN_DECONSTRUCTION §A.1/§B; the warmed ground hex lives per-system below):
paper_grain:
  opacity_pct: 5          # 4-6% observed in the reference
  speck_density: low
  uniform: true           # flat generated-grain look, no fiber/crumple deformation

style_systems:
  li_signal_card:
    display_name: "Signal Card"
    format_class: designed_card
    topic_tag: lead_gen_workflow
    destination: linkedin
    register: editorial
    archetype: statement-card
    generation_mode: designed_card
    ground_recipe: brand_gradient   # brand_gradient | paper | dark_terminal | solid_alternating | grid_paper | photoreal_environment | photoreal_cinematic
    palette:
      ground: ["#302B87", "#00A39A"]     # 135deg gradient
      text_primary: "#FFFFFF"
      accent: "#00A39A"
    type:
      display_family: "Montserrat SemiBold"
      display_fallback: "assets/fonts/NotoSans-Variable.ttf@630"
      body_family: "Montserrat Regular"
      body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
    slots:
      hero:
        ground_source: programmatic   # per-slot field (moved off RenderPolicy — §1); the logo_zone below is a partial-area diffusion surface under §2's round-2 logo policy
        text_render_mode: composited
        max_spans: 2                  # composited slot — layout choice, not a cap (§2 round-2 relaxation)
        logo_zone: [0.12, 0.30, 0.76, 0.12]   # diffusion-first tool marks, logo_fidelity_ok-gated, manifest-composite fallback (§2 logo policy, §5.11)
        zones:
          - {name: headline, rect_pct: [0.12, 0.44, 0.76, 0.18], type_scale: 0.11, weight: SemiBold, align: left, max_lines: 1, color: "#FFFFFF"}
          - {name: supporting_line, rect_pct: [0.12, 0.64, 0.76, 0.08], type_scale: 0.032, weight: Regular, align: left, max_lines: 1, color: "#FFFFFF"}

  ig_annotated_proof:
    display_name: "Annotated Proof"
    format_class: serif_editorial       # per DESIGN_EXPANSION §C.3's class table — §4.1
    topic_tag: lead_gen_workflow
    destination: instagram_feed
    register: editorial
    archetype: screenshot-annotated
    generation_mode: annotated_proof_ui   # NEW mode — see promptcraft.py proposal, STYLE_SYSTEMS_SPEC.md §2.2
    ground_recipe: paper                # round 2: paper recipe = warmed ground + top-level paper_grain spec
    palette:
      ground: "#F1ECE1"                 # round-2 warmed value (was #F2F0EC) — §2.2, DESIGN_DECONSTRUCTION §A.1
      headline_ink: "#302B87"
      body_ink: "#2B2B2B"
      accent: "#00A39A"        # hand-drawn annotation ink
    type:
      display_family: "Montserrat SemiBold"
      display_fallback: "assets/fonts/NotoSans-Variable.ttf@630"
      body_family: "Montserrat Regular"
      body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
    slots:
      cover:
        ground_source: diffusion   # text_render_mode=diffusion => the whole frame is one diffusion call; ground_source=programmatic is not a valid combination here (COMPOSITING_SPEC.md §3 case c)
        text_render_mode: diffusion
        max_spans: 2
        logo_zone: [0.12, 0.80, 0.30, 0.06]
        zones:
          - {name: headline, rect_pct: [0.12, 0.30, 0.76, 0.25], type_scale: 0.09, weight: SemiBold, align: center, max_lines: 2, color: "#302B87"}
      body:
        ground_source: programmatic
        text_render_mode: composited
        zones:
          - {name: kicker, rect_pct: [0.12, 0.74, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#302B87"}
          - {name: body, rect_pct: [0.12, 0.81, 0.76, 0.07], type_scale: 0.030, weight: Regular, align: left, max_lines: 3, color: "#2B2B2B"}
        screenshot_inset:
          mode: required_or_omit
          rect_pct: [0.12, 0.15, 0.76, 0.55]
          asset_key: "<topic>.screenshot.<slide_index>"
          corner_radius_pct: 4
          shadow_pct: 3
          fallback: solid_color_placeholder_tile
      prompt_quote:
        ground_source: programmatic
        text_render_mode: composited
        zones:
          - {name: kicker, rect_pct: [0.12, 0.74, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#302B87"}
          - {name: body, rect_pct: [0.12, 0.81, 0.76, 0.07], type_scale: 0.030, weight: Regular, align: left, max_lines: 3, color: "#2B2B2B"}
        screenshot_inset:
          mode: required_or_omit
          rect_pct: [0.12, 0.15, 0.76, 0.55]
          asset_key: "<topic>.screenshot.<slide_index>"
          corner_radius_pct: 4
          shadow_pct: 3
          fallback: solid_color_placeholder_tile
      end_card:
        ground_source: programmatic
        text_render_mode: composited
        zones:
          - {name: cta, rect_pct: [0.12, 0.40, 0.76, 0.10], type_scale: 0.045, weight: SemiBold, align: center, max_lines: 2, color: "#302B87"}
          - {name: subtext, rect_pct: [0.12, 0.52, 0.76, 0.08], type_scale: 0.028, weight: Regular, align: center, max_lines: 2, color: "#2B2B2B"}

  li_statement_hero:
    display_name: "Statement Hero"
    format_class: designed_card
    topic_tag: sales_agent_stat
    destination: linkedin
    register: editorial
    archetype: statement-card
    generation_mode: designed_card
    ground_recipe: brand_gradient
    palette:
      ground: ["#302B87", "#00A39A"]
      text_primary: "#FFFFFF"
    type:
      display_family: "Montserrat SemiBold"
      display_fallback: "assets/fonts/NotoSans-Variable.ttf@700"
      body_family: "Montserrat Regular"
      body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
    slots:
      hero:
        ground_source: programmatic
        text_render_mode: composited
        zones:
          - {name: eyebrow, rect_pct: [0.12, 0.18, 0.76, 0.06], type_scale: 0.024, weight: Medium, align: left, max_lines: 1, color: "#FFFFFF"}
          - {name: headline, rect_pct: [0.12, 0.26, 0.76, 0.36], type_scale: 0.36, weight: Bold, align: left, max_lines: 1, color: "#FFFFFF"}
          - {name: qualification, rect_pct: [0.12, 0.66, 0.76, 0.12], type_scale: 0.034, weight: Regular, align: left, max_lines: 2, color: "#FFFFFF"}

  ig_stat_slab:
    display_name: "Stat Slab"
    format_class: designed_card
    topic_tag: sales_agent_stat
    destination: instagram_feed
    register: editorial
    archetype: statement-card
    generation_mode: designed_card
    ground_recipe: solid_alternating
    palette:
      ground_a: "#302B87"
      ground_b: "#00A39A"
      text_primary: "#FFFFFF"
    type:
      display_family: "Montserrat SemiBold"
      display_fallback: "assets/fonts/NotoSans-Variable.ttf@700"
      body_family: "Montserrat Regular"
      body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
    slots:
      cover:
        ground_source: diffusion   # shipped default — §2.4/§2.7; non-default operator override may set this to programmatic/composited for a zero-diffusion run
        text_render_mode: diffusion
        max_spans: 2
        zones:
          - {name: headline, rect_pct: [0.12, 0.32, 0.76, 0.26], type_scale: 0.10, weight: Bold, align: center, max_lines: 2, color: "#FFFFFF"}
      body:
        ground_source: programmatic
        text_render_mode: composited
        zones:
          - {name: kicker, rect_pct: [0.12, 0.16, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#FFFFFF"}
          - {name: headline, rect_pct: [0.12, 0.26, 0.76, 0.26], type_scale: 0.26, weight: Bold, align: left, max_lines: 1, color: "#FFFFFF"}
          - {name: qualification, rect_pct: [0.12, 0.56, 0.76, 0.12], type_scale: 0.032, weight: Regular, align: left, max_lines: 2, color: "#FFFFFF"}
      prompt_quote:
        ground_source: programmatic
        text_render_mode: composited
        zones:
          - {name: kicker, rect_pct: [0.12, 0.16, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#FFFFFF"}
          - {name: headline, rect_pct: [0.12, 0.26, 0.76, 0.26], type_scale: 0.26, weight: Bold, align: left, max_lines: 1, color: "#FFFFFF"}
          - {name: qualification, rect_pct: [0.12, 0.56, 0.76, 0.12], type_scale: 0.032, weight: Regular, align: left, max_lines: 2, color: "#FFFFFF"}
      end_card:
        ground_source: programmatic
        text_render_mode: composited
        zones:
          - {name: cta, rect_pct: [0.12, 0.40, 0.76, 0.10], type_scale: 0.045, weight: SemiBold, align: center, max_lines: 2, color: "#FFFFFF"}
          - {name: subtext, rect_pct: [0.12, 0.52, 0.76, 0.08], type_scale: 0.028, weight: Regular, align: center, max_lines: 2, color: "#FFFFFF"}

  li_editorial_brief:
    display_name: "Editorial Brief"
    format_class: serif_editorial
    topic_tag: ops_assistant_founder
    destination: linkedin
    register: editorial
    archetype: editorial-carousel
    generation_mode: designed_card
    ground_recipe: paper                # round 2: warmed ground + paper_grain
    palette:
      ground: "#F1ECE1"                 # round-2 warmed value (was #F2F0EC)
      headline_ink: "#302B87"
      accent: "#00A39A"
    type:
      display_family: "Playfair Display Bold Italic"    # vendored, SIL OFL — §3.5
      display_fallback: "assets/fonts/NotoSans-Variable.ttf@630 (upright — italic-serif effect unavailable until vendoring lands)"
      body_family: "Lora Regular"                       # round-2 body sans→serif switch — vendored, SIL OFL, §3.5
      body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
      headline_split: true              # round-2 optional device: Bold Italic hero phrase + lighter qualifier in ONE zone — same rich-text-run dependency as §2.13, flagged
    slots:
      hero:
        ground_source: programmatic
        text_render_mode: composited
        max_spans: 1
        decorative_zone: [0.12, 0.14, 0.18, 0.06]
        zones:
          - {name: headline, rect_pct: [0.12, 0.24, 0.76, 0.34], type_scale: 0.08, weight: SemiBold, align: left, max_lines: 2, color: "#302B87"}
          - {name: attribution, rect_pct: [0.12, 0.62, 0.76, 0.06], type_scale: 0.026, weight: Regular, align: left, max_lines: 1, color: "#2B2B2B"}

  ig_prompt_sheet:
    display_name: "Prompt Sheet"
    format_class: designed_card         # per DESIGN_EXPANSION §C.3's class table (the dark terminal prompt card is its signature slide) — §4.1
    topic_tag: ops_assistant_founder
    destination: instagram_feed
    register: editorial
    archetype: editorial-carousel
    generation_mode: designed_card
    ground_recipe: paper   # round 2: warmed ground + paper_grain; prompt_quote slot overrides to dark_terminal — see slots block
    palette:
      ground: "#F1ECE1"                 # round-2 warmed value (was #F2F0EC)
      headline_ink: "#302B87"
      body_ink: "#2B2B2B"
      accent: "#00A39A"
      terminal_ground: "#1E1B2E"
      terminal_text: "#00A39A"
    type:
      display_family: "Playfair Display Bold Italic"    # vendored, SIL OFL — §3.5
      display_fallback: "assets/fonts/NotoSans-Variable.ttf@630 (upright)"
      body_family: "Lora Regular"                       # round-2 body sans→serif switch — §3.5
      body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
      mono_family: "JetBrains Mono or IBM Plex Mono (not yet acquired)"
      mono_fallback: "assets/fonts/NotoSans-Variable.ttf@400, +4% letter-spacing"
      headline_split: true              # round-2 optional device — same rich-text-run dependency as §2.13, flagged
    slots:
      cover:
        ground_source: programmatic   # firmed default — overrides the destination's own diffusion default for `cover` (§2.6/§2.7); the logo_zone below is a partial-area diffusion surface under §2's round-2 logo policy
        text_render_mode: composited
        max_spans: 2                  # composited slot — layout choice, not a cap (§2 round-2 relaxation); a recipe revision may raise it (e.g. kicker+headline+qualifier) without any contract change
        logo_zone: [0.12, 0.80, 0.30, 0.06]   # Claude mark, nominative use only (§3.6) — diffusion-first, logo_fidelity_ok-gated, manifest-composite fallback
        zones:
          - {name: headline, rect_pct: [0.12, 0.30, 0.76, 0.25], type_scale: 0.08, weight: SemiBold, align: center, max_lines: 2, color: "#302B87"}
      body:
        ground_source: programmatic
        text_render_mode: composited
        # Round-2 optional body-slot refinements (DESIGN_DECONSTRUCTION §B — each is a RECIPE VARIANT:
        # when exercised, the base `body` zone shrinks to the variant rect noted so zones never overlap;
        # when absent, the base recipe below applies unchanged):
        inline_artifact_card:           # bordered card + teal pill label + italic quoted artifact INSIDE a payload slide
          rect_pct: [0.12, 0.58, 0.76, 0.20]
          pill_label: true
          content_style: italic_quote   # byte-identical to a gated on_image_text string, composited
          body_rect_when_present: [0.12, 0.46, 0.76, 0.10]
        icon_zone: [0.12, 0.46, 0.08, 0.06]   # small monoline topic icon — NEW icon-asset-library dependency, flagged; body_rect narrows to [0.22, 0.46, 0.66, 0.42] when present
        checklist:
          checkbox_style: outline_square       # default — "to-do" semantics
          checkbox_style_done: filled_circle   # variant — "already-true capability" semantics, teal fill
        zones:
          - {name: eyebrow, rect_pct: [0.12, 0.16, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#302B87"}
          - {name: headline, rect_pct: [0.12, 0.24, 0.76, 0.16], type_scale: 0.07, weight: SemiBold, align: left, max_lines: 2, color: "#302B87"}
          - {name: body, rect_pct: [0.12, 0.46, 0.76, 0.42], type_scale: 0.028, weight: Regular, align: left, max_lines: 4, color: "#2B2B2B"}
      prompt_quote:
        ground_source: programmatic
        text_render_mode: composited
        ground_recipe: dark_terminal
        exempt_from_word_cap: true
        prompt_quote_max_words: 50   # derived in §2.6 from this system's own type scale — renamed from the earlier untyped "practical_word_ceiling"
        zones:
          - {name: prompt_text, rect_pct: [0.10, 0.14, 0.80, 0.72], type_scale: 0.032, weight: Regular, align: left, max_lines: 8, color: "#00A39A"}
      end_card:
        ground_source: programmatic
        text_render_mode: composited
        end_card_override: artifact_close   # round-2 OPTIONAL, per-asset choice, never a system default — 5th slot becomes another body/artifact beat instead of the follow CTA (DESIGN_DECONSTRUCTION §A.5/§C.4)
        zones:
          - {name: cta, rect_pct: [0.12, 0.40, 0.76, 0.10], type_scale: 0.045, weight: SemiBold, align: center, max_lines: 2, color: "#302B87"}
          - {name: subtext, rect_pct: [0.12, 0.52, 0.76, 0.08], type_scale: 0.028, weight: Regular, align: center, max_lines: 2, color: "#2B2B2B"}
```

**Round-2 append rule (single source per number, `RENDER_CONTRACT_SPEC.md` §5).** The five round-2
entries — `ig_value_sheet`, `ig_lifestyle_stack`, `ig_scene_hook`, `li_scene_hero`,
`ig_operator_grid` — are NOT duplicated here: their machine-readable blocks in §2.9–§2.13 are already
authored in the exact `style_systems:` entry shape (unlike §2.1–§2.6's slot-scoped zone blocks), and
the executor appends them to this map **verbatim**, after `ig_prompt_sheet`, in section order. Any
future edit to those five recipes happens in §2.9–§2.13, nowhere else.

**Round-4/5/6 append rule (same discipline, eighteen more entries).** The nine round-4/5/6 shapes in
§2.15–§2.22 append after the round-2 five, in section order, as **eighteen entries** — each shape's
`ig_*` recipe as authored, and its `li_*` twin **derived mechanically** (same class/register/
archetype/mode/palette/type, a single `hero` slot whose zones are the `ig_*` cover's rects
re-projected onto 16:9). The derivation is `layout.py`'s at load time, from one declared rect, so no
number is written twice. Library total after the append: **twenty-nine systems** — 27 organic
(`serif_editorial`, `designed_card`, `photoreal`, `editorial_grotesque`, `artifact_showcase`,
`website_showcase`, `robot_caricature`, `anime_scene`, `concept_dashboard`, `meme_reaction`,
`deadpan_memo`) + 2 promotional (`brand_promo`). **Two field additions apply to every entry**:
`hard_dont_exemptions: []` (non-empty only where §2.20/§2.22 says so — consistency check 11) and,
where D4 applies, `artifact_device:`.

**`ig_value_sheet` restyle (round-4/5, DNA anti-signal).** Its `ground_recipe` changes from
`dark_terminal` to the cream serif-editorial recipe (ground `#F6F1E7` + paper grain, body ink
`#2B2B2B`, teal kicker), and its palette block changes with it. **Everything else is unchanged** —
the zone rects, `type_floor: 0.0185`, `value_sheet_max_words: 220` and its derivation all stand, and
the `type_floor` legibility verification on the vendored Lora file remains a ship gate (§3.5). Only
the ground and ink hexes move.

### 3.2 `register:` key added to every `visual_archetypes[*]` entry

`visual_archetypes` (`style_guide.yaml:108-160`) has 16 entries; none currently carries a `register`
key. `RENDER_CONTRACT_SPEC.md` §4 check 5 requires every one to name a known `visual_registers` key.
Proposed binding (rationale: entries already consumed by a `GENERATION_MODES` `ModeSpec` inherit that
mode's own register verbatim; entries with no mode today are bound by their own ground description —
paper/flat card → `editorial`, near-black/neon → `hype`, real-photograph ground → `photographic_ugc`):

| Archetype key | Line | `register:` |
|---|---|---|
| `screenshot-as-proof` | 109 | `editorial` (bound to `live_app_ui`, `promptcraft.py:489-491`) |
| `screenshot-annotated` | 119 | `editorial` (newly bound to `annotated_proof_ui`, §2.2) |
| `statement-card` | 121 | `editorial` |
| `dense-spec-card` | 124 | `editorial` |
| `editorial-carousel` | 125 | `editorial` |
| `dark-hype-poster` | 127 | `hype` |
| `numbered-infographic` | 129 | `editorial` |
| `tool-showcase` | 131 | `hype` (dark ground + neon decor) |
| `ugc-photo-caption` | 133 | `photographic_ugc` (bound to `photoreal_lifestyle_sticker`, `promptcraft.py:456-458`) |
| `person-plus-stickers` | 135 | `photographic_ugc` (bound to `photoreal_person_ugc`, `promptcraft.py:469-471`) |
| `editorial-fashion` | 137 | `photographic_ugc` (real-photo ground even though type overlay reads "editorial") |
| `end-card` | 139 | `editorial` |
| `aspirational-lifestyle-scene` | 144 | `photographic_ugc` (bound to `aspirational_lifestyle_scene`, `promptcraft.py:480-482`) |
| `native-caption-frame` | 149 | `photographic_ugc` (bound to `native_caption_frame`, `promptcraft.py:499-501`) |
| `meme-reaction-split` | 153 | `photographic_ugc` (bound to `meme_reaction_split`, `promptcraft.py:508-510`) |
| `flat-lay-product-grid` | 157 | `photographic_ugc` (bound to `flat_lay_product_grid`, `promptcraft.py:517-519`) |

Applied as a one-line addition to each existing list entry, e.g.:

```yaml
  - key: statement-card
    register: editorial
    desc: "Big-type statement or logo-equation card (Tool + Platform = result number) on flat ground, 1-3 real logos."
```

**Round-2 additions to `visual_archetypes` itself** (new list entries, not bindings of existing ones —
each born with its `register:` key, so §4 check 5 covers them with no follow-up):

```yaml
  - key: cinematic-scene-hook
    register: photographic_ugc
    desc: "Cinematically lit real-world B2B environment (dusk meeting room, server corridor, monitor-glow desk) as full-bleed ground; short composited hook in the scene's own negative space; mood from light and composition, never invented stakes."
  - key: editorial-grotesque-grid
    register: editorial
    desc: "Off-white ruled grid-paper ground, heavy grotesque headline with one indigo emphasis phrase, amber highlighter bar, printed-zine masthead/footer furniture, optional small text-free photo inset."
```

### 3.3 Removal of the "60-90 words per slide" prose

Delete the `body_slide_template` line at `style_guide.yaml:91-93`:

```yaml
        body_slide_template: >
          eyebrow ("Step N" / "0N") + 2-line headline + 2-3 sentence body +
          checklist rows or a quoted prompt box; 60-90 words per slide
```

Replace with a structural pointer, carrying no numbers of its own (the numbers live exclusively in
`generation.render_contract.instagram_feed.slots[*]`, `RENDER_CONTRACT_SPEC.md:318-327` — this is the
single-source-per-number rule, `RENDER_CONTRACT_SPEC.md` §5):

```yaml
        body_slide_template: >
          Word/slide caps are NOT specified here — see generation.render_contract.instagram_feed.slots
          (config/themes/hypedigitaly.yaml) and STYLE_SYSTEMS_SPEC.md §2 for the per-role layout
          (eyebrow/kicker + headline + body, or checklist rows, or a quoted-prompt card) that applies
          within those caps.
```

`RENDER_CONTRACT_SPEC.md` §4 check 2 (grep for `\d+\s*-\s*\d+\s+words` in destination copy blocks) then
passes for the first time.

### 3.4 Per-destination `visual.default_archetypes` changes

**Round-2 update:** with §4's two-stage selector in place, every `linkedin`/`instagram_feed` asset now
resolves to a named `style_system` (an unmatched topic falls to its assigned format class's default
system, §4.1 step 7), so these lists are **no longer consulted on those two destinations at all**.
They remain live for `tiktok` and as the loaded-and-working fallback when a theme's config predates
`generation.format_quota` (§4.1 step 0) — which is why the round-1 addition below still ships. One
addition, justified by §2.2 newly binding `screenshot-annotated` to a mode:

```yaml
  instagram_feed:
    visual:
      default_archetypes: [editorial-carousel, numbered-infographic, tool-showcase, screenshot-annotated]
      aspect_ratio: "4:5"
```

`linkedin.visual.default_archetypes` (`style_guide.yaml:80`) is unchanged — `statement-card` already
covers both §2.1 and §2.3's archetype without needing to be added twice, and neither `editorial-carousel`
nor `screenshot-annotated` need to appear here since `li_editorial_brief` (§2.5) pins its archetype
directly rather than relying on the rotation.

### 3.5 Font vendoring task (round 2, operator-locked 2026-08-07)

Vendor two families into `assets/fonts/` — both **SIL OFL 1.1**, license file shipped alongside each,
same convention `assets/fonts/README.md` establishes:

| Family | Cuts to vendor | Role | Consumed by |
|---|---|---|---|
| **Playfair Display** | Regular, Italic, Bold, **Bold Italic** (Black Italic optional, for the `headline_split` hero phrase) | display/headlines — the italic-Didone treatment §2.5/§2.6 intend, and §2.9's cover | `li_editorial_brief`, `ig_prompt_sheet` (cream slots), `ig_value_sheet` (cover) |
| **Lora** | Regular, Italic, Bold | body serif — round 2's editorial body-text switch from sans to serif | the same three systems' body/attribution/checklist/dense-body zones |

Rules, all binding:

- **Czech-diacritics glyph verification is a ship gate.** Re-run `assets/fonts/README.md`'s exact
  corpus (`ěščřžýáíéúůďťňó / ĚŠČŘŽÝÁÍÉÚŮĎŤŇÓ`, `Kč`) on the ACQUIRED files — never assumed from
  Google Fonts' published Latin-Extended coverage. `ig_value_sheet`'s `type_floor: 0.0185`
  additionally needs its own legibility pass at that exact size on the vendored Lora file (§2.9) —
  the standard glyph test does not cover it.
- **Until both land and verify, every `*_fallback` in §3.1 stays `NotoSans-Variable.ttf`** at the
  stated weight and ships as-is — the fallbacks are the current truth, the families the intent.
- **Italic is carried by the named cut FILE** (e.g. `PlayfairDisplay-BoldItalic.ttf`), never by a zone
  field — zone `weight:` keeps driving only the variable-weight axis of whatever file is loaded (§2's
  conventions).
- **Montserrat stays the intended sans for every non-serif-editorial system** (`li_signal_card`,
  `li_statement_hero`, `ig_stat_slab`, `ig_annotated_proof`, the photoreal captions §2.10–§2.12,
  `ig_operator_grid` body) — unchanged, and still not in-repo (§0's font gap). §2.13's grotesque
  display cut (Inter Black as the OFL pick) and §2.6's mono are separate, still-open acquisitions,
  each already flagged in place.

### 3.6 Accent governance (round 2, operator-locked 2026-08-07)

- **Every template prompt PINS its accent hex, as a literal (round-4/5, F10 — binding).** With no
  hex written into the prompt the model chose coral/orange accents twice in round 2 — and coral is
  Anthropic's Claude mark, so an unpinned prompt drifts into another company's trademark by default.
  `validate_crafted_prompt` therefore requires at least one of the system's own palette hexes to
  appear literally in every submitted prompt, and rejects an accent named outside that palette.
- **D2's one-emphasis rule (round-4/5, `reference/OPERATOR_FAVORITES_DNA.md`):** exactly **one**
  emphasis token per headline. **Teal `#00A39A`** is the default; **italic indigo `#302B87`** carries
  serif emphasis; **amber `#E8A63B` is reserved for numerals and times** and may not emphasise a
  word. Two emphasis instructions in one prompt is a validation failure, not a style preference —
  every one of the ten picked renders has exactly one.
- **Generic brand accents: indigo `#302B87` and teal `#00A39A` ONLY.** No system introduces a new
  general-purpose accent, round 2 included.
- **One new single-purpose token:** `highlight_bar: "#E8A63B"` (warm amber/ochre), usable ONLY as
  `ig_operator_grid`'s highlighter-bar fill (§2.13) — `DESIGN_EXPANSION.md` §A.3's recommended
  option 1. The reference's **red** emphasis phrase maps to brand **indigo `#302B87`**
  (`emphasis_ink`), never to a new red. Documented zero-new-token fallback if the amber token is
  refused: teal `#00A39A` for the bar (a flagged expansion of teal's pill-only role) with indigo
  emphasis unchanged.
- **The coral asterisk/starburst (`#DD7A54`-family) is Anthropic's Claude product mark.** Usable ONLY
  as an accurate, nominative rendering of the real mark where the copy genuinely names Claude as the
  tool — under §2's logo policy (diffusion-first, `logo_fidelity_ok`-gated, manifest-composite
  fallback), the same governance every third-party mark gets. NEVER as a decorative motif, recurring
  brand device, or hand-inked flourish — that is an unauthorized redraw of another company's
  distinctive mark and color (`DESIGN_DECONSTRUCTION.md` §C.3, risk tier 2). Teal/indigo abstract
  marks (§2.5's `decorative_zone`) remain freely usable and are the sanctioned substitute.

---

## 4. Style-system selection — two-stage, Virlo-weighted, deterministic (round-2 REWRITE)

Round 1 selected purely by `(topic_tag, destination)` over three topic-bound pairs. Round 2 replaces
that with a **two-stage** selector: a per-RUN format mix (stage 1) assigns each asset a
`format_class`; the per-ASSET topic regex (stage 2 — round 1's classifier, kept verbatim and
extended) picks the concrete system inside that class. This is the operator-locked resolution of the
integration question `DESIGN_EXPANSION.md` §B deferred (its path (a)/(b) menu) — a third path that
uses BOTH: new topic tags for precision, plus a class quota for guaranteed variety. Everything below
is deterministic — pure functions over config, the run's Virlo visual profile, `run_date`, and the
asset list; **no LLM anywhere in the selection path** (unchanged from round 1).

`VisualPolicy.style_system` is still resolved **once per asset**, by the same function that resolves
the rest of `RenderContract` (`RENDER_CONTRACT_SPEC.md` §2's `resolve_render_contract`, called in
`stages.stage_copy`, before authoring), never re-resolved per slot or in the media stage
(`RENDER_CONTRACT_SPEC.md:124-126`, unchanged). Stage 1's run-level quota assignment happens **once
per run**, immediately before the per-asset resolution loop, in the same `stage_copy` call path; its
output (an `asset_id → format_class` map plus the reweight decision) is stashed alongside the
contracts and, on `--resume`, is **read back from `resume_state.yaml`, never re-derived**
(`RENDER_CONTRACT_SPEC.md` §8's resume rule extends to this map).

**Evidence gate — unchanged, first, absolute:** `evidence_class == "evidence-absent"` blocks ALL
image generation (locked decision 4) before either stage runs; `style_system` is moot for such an
asset. `evidence-thin` does NOT change what either stage selects — it sets the review-required flag
per the evidence posture (`FINDINGS_SYNTHESIS.md` §3), a decision event, not a different system
(round 1's step 5, verbatim).

### 4.1 Resolution algorithm

**The `format_class` field.** Every `style_systems[*]` entry carries `format_class` (§3.1), one of
exactly four values. Assignment follows `DESIGN_EXPANSION.md` §C.3's own class table; the two fuzzy
calls are fixed and documented, not evidence-driven — `ig_prompt_sheet` classes as `designed_card`
(its signature slide is the dark terminal prompt card, a designed-card device, even though its cream
slots now carry serif type) and `ig_annotated_proof` classes as `serif_editorial` (paper-ground
calm-register proof format):

| `format_class` | linkedin systems | instagram_feed systems | Class default (LI / IG) |
|---|---|---|---|
| `serif_editorial` **(elevated)** | `li_editorial_brief`, `li_serif_statement` | `ig_annotated_proof`, `ig_serif_statement` | **`li_serif_statement` / `ig_serif_statement`** — the round-4/5 default moves to the picked shape |
| `photoreal` **(elevated)** | `li_scene_hero` | `ig_scene_hook`, `ig_lifestyle_stack` | `li_scene_hero` / `ig_scene_hook` (dark-serif treatment, DNA pick 9) |
| `artifact_showcase` **(elevated, NEW)** | `li_artifact_showcase` | `ig_artifact_showcase` | `li_artifact_showcase` / `ig_artifact_showcase` |
| `website_showcase` **(elevated, NEW)** | `li_website_showcase` | `ig_website_showcase` | the same entry |
| `robot_caricature` **(elevated, NEW)** | `li_robot_caricature` | `ig_robot_caricature` | the same entry |
| `anime_scene` **(elevated, NEW)** | `li_anime_scene` | `ig_anime_scene` | the same entry |
| `designed_card` *(occasional)* | `li_signal_card`, `li_statement_hero` | `ig_stat_slab`, `ig_prompt_sheet`, `ig_value_sheet` | `li_statement_hero` / `ig_stat_slab` |
| `editorial_grotesque` *(occasional)* | `li_operator_grid` (derived twin) | `ig_operator_grid` | `ig_operator_grid` |
| `concept_dashboard` *(occasional, NEW)* | `li_concept_dashboard` | `ig_concept_dashboard` | the same entry |
| `meme_reaction` / `deadpan_memo` **(RESERVED slot, NEW)** | `li_*` twins | `ig_meme_reaction`, `ig_deadpan_memo` | not quota members — §4.1 step 1b |
| `brand_promo` **(RESERVED slot, PROMOTIONAL, NEW)** | `li_brand_promo` | `ig_brand_promo` | not a quota member — §4.1 step 1b |

**Round-4/5 note on "elevated" and "occasional".** These words are not new machinery — they describe
where a class sits in the **default quota** below. Elevated classes hold their own quota slot;
occasional classes share one rotating slot. **Nothing is deleted**: the Virlo reweight operates on
quota keys and can promote the occasional group's share, which is exactly why the unpicked classes
stay in the library rather than being cut (`reference/OPERATOR_FAVORITES_DNA.md`, selection
re-weighting). The `editorial_grotesque` row also gains a derived LinkedIn twin, closing the
"no LI member" gap that step 5 used to paper over with substitution.

Class defaults (rightmost column) are each class's most topic-agnostic member, consumed by step 7.
`ig_annotated_proof` is an admittedly weak default (screenshot-asset dependency), but its own degrade
path — placeholder tile, decision-logged per I5 — already covers the no-asset case (§2.2).
`editorial_grotesque` has NO linkedin member; step 5's destination-compatibility substitution handles
that, never an invented on-the-fly system.

**ROUND-4/5/6 AMENDMENT to stage 1 — four mechanical additions, one shape unchanged.** The algorithm
below still runs exactly as written; these ride on top of it and are all deterministic and
decision-logged.

**1a. Quota keys may name a GROUP.** A key holding `k` slots may expand to `k` **distinct** members
of a named class list, chosen by the same `sha256(run_date)` seeded rotation over the group's fixed
member order. This is how "double down on the picked shapes" is expressed without deleting anything.
**Ratified default quota (sums to the 6 organic assets):**

```
serif_editorial: 1 · photoreal: 1 · artifact_showcase: 1 · illustration: 2 · occasional: 1
  illustration = [website_showcase, robot_caricature, anime_scene]      # all elevated
  occasional   = [designed_card, editorial_grotesque, concept_dashboard]  # rotation reserve
```

A group's `n_c` / `win_rate_c` for the step-2 reweight is the **roll-up over its members' corpus
labels**, so evidence can still move a slot into or out of the reserve — a demoted class is demoted,
not deleted.

**1b. Two RESERVED slots, appended before the organic walk, consuming no quota token:**

- `reserved.brand_promo.slots_per_run` (default **1**, dial) → assets pinned to
  `format_class: brand_promo`. **Copy is config, not authored** (§2.22), so these assets skip the
  topic stage entirely.
- `reserved.meme.slots_per_run` (default **1**, dial **0-2**) → assets pinned to a meme class,
  **alternating `meme_reaction` ↔ `deadpan_memo`** by the same seeded rotation (so consecutive runs
  alternate and a 2-slot run gets one of each). Unlike brand promo these **are** topical: they run
  the normal topic stage to pick a humour angle from the run's Virlo trends.

A 6-asset organic plan therefore produces an **8-asset run** at the defaults.

**1c. The CAROUSEL GATE — `select_asset_format(asset, visual_profile, gate_cfg)`.** Instagram assets
are **`single` by default**; `carousel` is selected only when the run's Virlo corpus for the asset's
topic clears the same floor the format reweight uses:

```
n_carousel      = corpus items labelled slideshow/carousel for this topic
win_rate_carousel = fraction of those with weighted virality >= virality_strong (18)
carousel  iff  n_carousel >= min_sample (12)
           AND win_rate_carousel - win_rate_single >= win_rate_gap (0.25)
```

`evidence-thin` and `evidence-absent` **never** select `carousel`. The decision — chosen format, both
counts, both rates — is **always** a decision event, including the no-carousel case, so an operator
can see why a run shipped singles. The format feeds `resolve_render_contract` and is persisted with
the stage-1 map; on `--resume` it is **read back, never re-derived** (a carousel re-deriving as a
single mid-run would strand four paid slots).

**1d. Step 5 walks the most-constrained assets FIRST** — ascending order of compatible-token count,
ties by content-plan order. With eleven organic classes and destination-restricted members,
first-come-first-served handed universal tokens to unconstrained assets and forced avoidable
`quota_substitution` events. Deterministic, and strictly fewer substitutions.

**STAGE 1 — per-run format mix:**

```
0. Config gate: generation.format_quota absent from the theme config (a theme predating W8-11
   round 2) => the ENTIRE two-stage selector is off; round 1's (topic_tag, destination) resolution
   runs as previously specified and unmatched topics fall to the Phase-8 rotation (§3.4). This is
   the loaded-and-working degrade path, per load_theme_generation_config's optional-keys idiom
   (RENDER_CONTRACT_SPEC.md §7). Destinations outside {linkedin, instagram_feed} always use the
   Phase-8 rotation regardless (§0 scope).

1. quota = generation.format_quota (config, §4.3). Default, sized for a 6-asset run:
     {designed_card: 2, photoreal: 2, editorial_grotesque: 1, serif_editorial: 1}
   — DESIGN_EXPANSION §C.3's evidence-informed split (photoreal capped at 2/6 because every
   diffusion-touched slot is a paid, QA-gated, fail-closed surface).

2. Virlo reweight (at most ONE slot moves per run — evidence must clearly favor a class):
     For each format_class c over the run's Virlo visual-profile corpus (the same corpus
     analysis.resolve_visual_evidence already ingests; each corpus item carries a format-class
     label from the corpus classifier):
       n_c        = count of corpus items labelled c
       win_rate_c = fraction of those items with weighted virality >= 18 ("strong" on the Virlo
                    interpretation scale)
     A class is SIGNAL-BEARING iff n_c >= 12; a class below the sample floor can neither gain nor
     lose a slot (silence is not evidence).
     If, across signal-bearing classes, max(win_rate) - min(win_rate) >= 0.25 AND the min-rate
     class currently has quota >= 1: move exactly ONE slot from the min-rate class to the max-rate
     class (ties on rate: resolve by the fixed class order designed_card > photoreal >
     editorial_grotesque > serif_editorial — first-in-order gains, last-in-order loses). A class
     never drops below 0. Never more than one shift per run, however lopsided the evidence —
     quota stability IS the variety guarantee. Log the shift (or the no-shift, with all rates and
     counts) as a decision event.

3. Scale to run size: if the run's asset count N != sum(quota), scale each class count by
   N / sum(quota) and take integer counts by largest remainder, ties broken by the fixed class
   order. (N == 6 with the default quota is the identity.)

4. Rotation seed: expand the quota to an ordered token list in the fixed class order, then rotate
   it left by
     seed = int(sha256(run_date_iso)[:8], 16) % len(tokens)
   Consecutive runs (different run_date) start the class cycle at a different point — the rotation
   guarantee — while any re-run of the SAME run_date reproduces the identical assignment
   (deterministic/reproducible).

5. Assign: walk the run's assets in content-plan order; each asset consumes the FIRST remaining
   token whose class has >= 1 system for the asset's destination (the §4.1 table). If no remaining
   token is compatible (e.g. only editorial_grotesque tokens remain and the asset is linkedin),
   assign designed_card (the universal class — members on both destinations), discard one
   incompatible token, and log a quota_substitution decision event.
```

**STAGE 2 — concrete system inside the class (per asset):**

```
6. topic_tag = classify(asset.topic_text)   # asset.topic_text = headline + theme cluster label,
                                             # matched case-insensitively, first rule wins
   Regexes (deterministic, no LLM) — round 1's three, kept VERBATIM, plus four round-2 tags:
     lead_gen_workflow:      \b(n8n|apify|zapier|make\.com|web scrap\w*|workflow automation|
                              lead[- ]gen(eration)? workflow|automated prospecting)\b
     sales_agent_stat:       \b(lead scor\w*|AI sales agent|sales agent|qualif\w*|SDR agent|
                              outbound agent)\b
     ops_assistant_founder:  \b(claude|ops[- ]assistant|founder|solo founder|admin (assistant|agent)|
                              operations assistant)\b
     prompt_dump_reference:  \b(\d+ (prompts|tools|apps|templates)|prompt (pack|library|list|dump)|
                              cheat[- ]?sheet|mega[- ]?list|swipe file)\b
     tool_stack_howto:       \b((tool|app|ai) stack|apps? (i|we|to) use|run (a|your|the) (business|
                              agency) (with|on)|daily (tools|apps)|stack breakdown)\b
     scene_hook_generic:     \b(future of|what (nobody|no one) (tells|says)|the real (cost|reason)|
                              behind the scenes|hard truth|wake[- ]?up call)\b
     agency_playbook_howto:  \b(agency|playbook|blueprint|roadmap|framework|client (acquisition|
                              pipeline)|land (clients|retainers))\b
   Precedence when more than one matches: the three round-1 tags keep their round-1 order and
   outrank all four new tags; the new tags rank prompt_dump_reference > tool_stack_howto >
   scene_hook_generic > agency_playbook_howto (fixed, arbitrary, documented — not evidence-driven).
   This resolves DESIGN_DECONSTRUCTION §C.1's flagged-open prompt_dump_reference classifier gap.

7. candidates = style_systems entries where format_class == the asset's stage-1 class AND
   destination == asset.destination.
     If exactly one candidate: that system.
     Elif topic_tag is not None and some candidate's topic_tag == topic_tag: that candidate
       (at most one can match — topic_tags are unique per (format_class, destination), enforced by
       the load-time consistency check, §4 item 5 extended).
     Else: the class DEFAULT for that destination (§4.1 table) — subject to step 8's rotation.

8. Within-class rotation (the second half of the rotation guarantee): when step 7 fell through to
   the class default AND that (class, destination) has > 1 candidate, pick
     sorted(candidates)[(seed + asset_index) % len(candidates)]
   instead of the static default — consecutive runs (different seed) and consecutive same-class
   assets within one run (different asset_index) both vary the concrete system, deterministically.

9. Pin from the chosen entry, exactly as round 1's step 4 did:
     style_system            = entry key
     VisualPolicy.register   = entry.register
     VisualPolicy.archetype  = entry.archetype     # PINNED — bypasses pick_generation_mode's
                                                     # own archetype resolution (§1 note)
     VisualPolicy.mode       = entry.generation_mode
   Steps 6-9 are evidence-independent, same as round 1 (topic_tags are keyword facts about the
   copy, not about visual evidence).
```

With the class defaults in place, every `linkedin`/`instagram_feed` asset resolves to a NAMED system —
round 1's `""` unset-sentinel path survives only under step 0's config gate and for out-of-scope
destinations.

### 4.2 One system per asset — carousel series consistency

Once resolved in step 9, `style_system` is a property of the **asset**, not the slot. All 5 Instagram
slots of one carousel share the identical `(register, archetype, generation_mode, style_system)` tuple —
only `ground_source`/`text_render_mode`/layout vary **by slot role**, per that one system's own §2/§3.1
table, never by re-selecting a different system mid-carousel. This is the literal meaning of
`FINDINGS_SYNTHESIS.md` §4 item 7's "one design system per asset."

**What this means for N-E's `series_consistent` rubric** (`media_gen.py:911-914`): the existing check
(background hue family, body typeface family, handle corner, compared slide-to-cover) gains two
system-specific additions, both stated explicitly in the QA prompt alongside the existing "Intended
register" / "Intended generation mode" lines (`media_gen.py:915-918`):

- **Intended style_system** is now named in the QA call (e.g. `"Intended style_system: ig_stat_slab"`),
  so the vision model judges against that system's own recipe, not a generic editorial-card default.
- For `ig_stat_slab` specifically (§2.4), `series_consistent` must additionally verify the stated
  indigo/teal **alternation sequence** across slides (indigo, teal, indigo, teal, indigo) rather than a
  single fixed hue — the QA prompt for this one system names the expected per-slide ground color
  explicitly rather than relying on "same hue family" alone.

Round-2 system-specific `series_consistent` additions, same pattern (the QA prompt names the expected
structure per slide, never a generic "same hue family"):

- **`ig_lifestyle_stack` (§2.10):** all 5 slides share ONE environment family — same room/palette/
  light quality, different angles or rooms of the same family — never five unrelated locations.
- **`ig_scene_hook` (§2.11):** the ground-type rhythm is named per slide (scene, terminal, scene,
  terminal, terminal) — a payoff slide coming back photoreal, or vice versa, is a fail.
- **`ig_operator_grid` (§2.13):** masthead + footer furniture present on every slide, same grid
  pitch, and the highlighter bar/emphasis phrase colors match §3.6's tokens exactly.

### 4.3 Config surface — `generation.format_quota` (coordination note)

Stage 1 reads one new config key, proposed for `RENDER_CONTRACT_SPEC.md` §7's surface (that spec's
executor adds it under `generation:`, following the same optional-keys-with-safe-defaults loader
idiom, so its ABSENCE is well-defined — §4.1 step 0):

**ROUND-4/5/6: all of it moves into ONE block** — `generation.batch_composition` (`PLAN.md` §13
item 25). An operator planning a batch should read one block, and a reviewer should see the whole run
shape at a glance:

```yaml
generation:
  batch_composition:
    organic_assets: 6
    destination_split: {linkedin: 3, instagram_feed: 3}
    language_by_destination: {linkedin: en, instagram_feed: en}   # default en; cs is a supported switch
    format_quota:            # per-run variety quota, stage 1 (§4.1) — counts, not weights
      serif_editorial: 1
      photoreal: 1
      artifact_showcase: 1
      illustration: 2        # group — expands to 2 DISTINCT members by seeded rotation
      occasional: 1          # group — the rotation reserve
    format_quota_groups:
      illustration: [website_showcase, robot_caricature, anime_scene]
      occasional:   [designed_card, editorial_grotesque, concept_dashboard]
    format_quota_reweight:   # Virlo reweight mechanic (§4.1 step 2); omit to accept these defaults
      min_sample: 12         # n_c floor below which a class is not signal-bearing
      win_rate_gap: 0.25     # absolute win-rate gap that moves one slot
      virality_strong: 18    # weighted-virality threshold defining a "win"
    carousel_gate:           # §4.1 step 1c — same floor discipline, different question
      min_sample: 12
      win_rate_gap: 0.25
      virality_strong: 18
    reserved:                # appended assets; neither consumes a quota token
      brand_promo:
        slots_per_run: 1
        destinations: [instagram_feed]
        messages: [...]      # seeded with the three ratified service lines (§2.22)
        cta_text: "..."      # VERBATIM, never paraphrased
      meme:
        slots_per_run: 1     # dial 0-2
        destinations: [instagram_feed]
        classes: [meme_reaction, deadpan_memo]   # alternated by seeded rotation
```

**Absence semantics (loader idiom, `RENDER_CONTRACT_SPEC.md` §7):** no `format_quota` ⇒ the entire
two-stage selector is off and the Phase-8 rotation runs (§4.1 step 0); no `carousel_gate` ⇒ `single`
always (the conservative direction); no `reserved.*` entry ⇒ no such asset; no `batch_composition`
block at all ⇒ pre-W8-11 behaviour, so a theme predating this wave still loads.

**Cadence note.** The engine is an **invoked batch** — one invocation, one run pack, exit. Daily or
weekly scheduling is **external** (Task Scheduler / cron) and config-gated by this block; the
**posting** schedule belongs to Postiz. Nothing in this document implies an in-engine scheduler, and
none is added.

---

## 5. Hard DON'Ts as enforceable checks

Source: `FINDINGS_SYNTHESIS.md` §5's five-item list (5.1–5.5, round 1), plus round 2's five anti-ad
rules from `DESIGN_EXPANSION.md` §C.2 (5.6–5.10) and the logo-fidelity gate from the same-day logo
policy (5.11). Each becomes three things: prompt-side wording (a), a deterministic validator check
where one is mechanically possible (b), and the N-E rubric boolean it maps to (c).

**ROUND-4/5 — the exemption model (`PLAN.md` §13 item 20, invariant BP1).** Two of the rules below are
*aesthetic* rather than *integrity* rules, and exactly two systems may opt out:

| Rules | Nature | Who may be exempt |
|---|---|---|
| **5.1-5.5** (collages, clip-art, lorem ipsum, fake/invented third-party UI, gradient mesh) and **5.11** (mark fidelity) | **integrity** — they stop us shipping something false | **nobody, ever** |
| **5.6-5.10** (radial glow, benefit pills, device mockups, urgency/price/CTA-banner language, the stand-alone-content test) | **ad aesthetics** — they stop organic posts looking like ads | `brand_promo`-class systems only (§2.22) — it is *supposed* to look like an ad |
| **5.6** alone | as above | additionally `concept_dashboard` (§2.20) — the glow is the diorama's light |

Exemptions are declared as data (`style_systems[*].hard_dont_exemptions`), consulted by the checks
below, and validated by `RENDER_CONTRACT_SPEC.md` §4 **check 11**: an organic system claiming an
anti-ad exemption is a `ConfigError` naming the system and the rule. Two additional sections extend
this list: **§5.12** (tool-mark coverage and the unknown-tool ladder) and **§5.13** (the persona
depiction carve-out).

### 5.1 No flattened multi-panel collages

**(a) Prompt wording** (add to `promptcraft.SYSTEM_PROMPT`, alongside the existing PROMPT-HYGIENE block,
`promptcraft.py:119-166`): *"Render exactly ONE cohesive scene/card per image — never a grid,
split-screen, or multi-panel collage layout, unless this asset's own style system explicitly specifies
a fixed split (the only exception in this pipeline is `meme_reaction_split`'s own top/bottom two-zone
frame, named explicitly when that mode is active)."*

**(b) Deterministic check** — new function alongside `deterministic_prompt_leak_check`
(`media_gen.py:851-864`), scanning the RENDER section (never STYLE, same scoping convention as the
existing leak check) for:
```
_COLLAGE_LEAK_RE = re.compile(
    r"\b(panel grid|multi[- ]panel|four[- ]panel|three[- ]panel|grid of (images|photos|panels)|"
    r"collage|split into \d+ (panels|frames))\b", re.IGNORECASE,
)
```
Runs at the same two wiring points as `deterministic_prompt_leak_check` (pre-generation over `<<...>>`
spans AND post-QA over the vision response's free text) — a finding either blocks submission or fails
QA outright, never a silent note.

**(c) N-E rubric:** `composition_ok` (`media_gen.py:908-910`) — extend its rubric text with an explicit
"no unrequested multi-panel/collage layout" clause, mirroring `FINDINGS_SYNTHESIS.md` §4 item 6's
instruction to add this explicitly (it is currently implicit at best).

### 5.2 No clip-art icon rows

**(a)** *"Never depict a horizontal row of generic flat clip-art icons (gear, lightbulb, rocket,
checkmark-in-circle used as decoration rather than content) — every icon on the canvas is either a
named tool's accurate official logo mark (rendered under the round-2 logo policy: diffusion-first,
`logo_fidelity_ok`-gated, manifest-composite fallback — §2's logo-policy block, §5.11) or a single
small solid-color accent shape with no pictorial content."*

**(b)**
```
_CLIPART_ROW_RE = re.compile(r"\b(icon row|row of icons|clip[- ]?art|generic icons?)\b", re.IGNORECASE)
```
Same two wiring points as 5.1.

**(c)** `composition_ok` — "no orphaned or random decorative element" (`media_gen.py:908-909`) already
covers a single stray icon; extend to explicitly cover a *row* of them as a pattern, not just one.

### 5.3 No lorem ipsum / placeholder labels

This is the fa51-observed defect (`FINDINGS_SYNTHESIS.md` line 16: literal "EYEBROW TAG" and Lorem
ipsum rendered). **(a)** *"Every text string that appears on the image is one of the exact `<<...>>`
spans given to you — never a placeholder, sample, or generic structural-role label word standing in for
real content."*

**(b)** Extend `media_gen.BANNED_RENDERED_STRINGS` (`media_gen.py:813-815`, currently `("montserrat",
"didone", "semibold", "regular", "ui label", "placeholder", "lorem", "typeset", "readability")`) — same
list also drives the equivalent check inside `promptcraft.validate_crafted_prompt` (a second,
independent instance of the same vocabulary, per `RENDER_CONTRACT_SPEC.md` §5's single-source rule;
this specific string list is the one documented exception since it is consumed by two different
regexes on two different text surfaces — pre-generation prompt spans vs. post-QA free text — and both
need it, so it should move to one shared module-level constant, e.g. `hypeagent.render_contract`, and
be imported by both `media_gen.py` and `promptcraft.py` rather than duplicated):

```python
BANNED_RENDERED_STRINGS = (
    "montserrat", "didone", "semibold", "regular", "ui label", "placeholder", "lorem", "lorem ipsum",
    "typeset", "readability",
    # W8-11 additions — the fa51 defect class:
    "eyebrow", "eyebrow tag", "step n", "0n", "sample text", "your text here", "insert text",
    "insert here", "tbd", "xxxx", "dolor sit amet", "consectetur",
)
```

**(c)** `text_matches` (`media_gen.py:889-899`) — already fails on "any prominent garbled foreground
text... invented word... standing in for real text" per the existing rubric; the banned-string scan is
the deterministic backstop, not a replacement for the vision judgment.

### 5.4 No fake/invented dashboards or third-party UI

**(a)** *"When the copy names a real tool/platform, either composite ITS real captured screenshot asset
(never diffuse one) or show only its accurate official logo mark (rendered under §2's round-2 logo
policy — a mark is never screen chrome) with no invented UI around it; never ask the image model to
invent a dashboard, app screen, browser window, or generic SaaS UI it has to fabricate
pixel-for-pixel — it cannot render real UI text reliably and the failure mode is illegible garbled
text at exactly the spot a viewer looks first."* This directly extends the existing rule already coded
at `promptcraft.py:128-132` ("every decorative element... must carry SPECIFIED text content... or be
explicitly described as containing no text at all") and the existing inset caps
(`MAX_INSET_STRINGS = 6`, `MAX_INSET_STRING_WORDS = 3`, `promptcraft.py:106-107`) — this Hard DON'T adds
the missing precondition: an inset showing a *screen/dashboard* is permitted only when it is a
**composited real asset**, never a diffusion-generated one; a diffusion-generated proof visual may show
only a real logo mark or a genuinely photographic prop, never simulated software chrome.

**(b)**
```
_FAKE_UI_RE = re.compile(
    r"\b(mock(ed)?[- ]?up dashboard|fictional (app|dashboard|interface)|imaginary (screen|dashboard|UI)|"
    r"generic dashboard|placeholder (screen|interface))\b", re.IGNORECASE,
)
```
Same two wiring points as 5.1/5.2. This regex catches only the crafter's OWN wording asking for a fake
UI (an authoring-time defect); it cannot detect a diffusion model inventing UI chrome unprompted — that
class is caught only by (c).

**(c)** **New N-E boolean, `ui_fidelity_ok`** (proposed addition to `VisionQaResult`,
`media_gen.py:940-949`, and to the overall-pass computation at `media_gen.py:1074`): *"true when NO
software UI/dashboard/app-screen is depicted at all, OR when one is depicted and it is either (i) the
exact real UI of the tool named in the required text with its own accurate branding, real logo, and no
garbled chrome text, or (ii) a real, pre-captured screenshot asset (indistinguishable from an actual
product screenshot, never a stylized/invented one). False whenever the image shows an invented,
generic, or garbled-text software interface standing in for a real one."* This is a genuinely new
rubric item — none of the five existing booleans (`text_matches`, `archetype_ok`, `subject_relevant`,
`logos_ok`, `composition_ok`, `series_consistent`) map onto "is this UI real" cleanly, and the fa51
run's worst failures (`FINDINGS_SYNTHESIS.md` §5's "garbled fake-AI-UI text" Virlo finding) are
specifically this failure mode.

### 5.5 No default gradient-mesh

**(a)** *"Never use a default abstract gradient-mesh, blurred-color-blob, or generic
'AI-startup-website' iridescent background. The ground is either this asset's own style system's exact
palette hex (flat or paper texture, composited) or a genuine real-world photograph — nothing in
between, and never an abstract computer-generated blob standing in for either."*

**(b)**
```
_GRADIENT_MESH_RE = re.compile(
    r"\b(gradient mesh|abstract gradient blob|iridescent (background|blob|gradient)|holographic blob|"
    r"blurred color blob|blurry gradient)\b", re.IGNORECASE,
)
```
Same two wiring points as 5.1/5.2/5.4.

**(c)** `composition_ok` — extend its rubric text to explicitly name default-gradient-mesh grounds as a
failure, alongside "no orphaned decorative element." **Structural mitigation, stronger than the
validator:** every round-1 system in §2 sets `ground_source: programmatic` for every slot except each
system's own `cover`, eliminating the gradient-mesh risk class architecturally for those slots — the
regex is a backstop for the diffusion-touched surfaces, not the primary defense. **Round-2 amendment:**
the photoreal systems (§2.10–§2.12) and the partial-area logo/inset surfaces (§2.1/§2.6/§2.13 under
the round-2 logo policy) are the deliberate, governed exceptions whose grounds or patches ARE
diffusion surfaces — which is exactly why §5.6's radial-glow extension, §5.10's stand-alone-scene
test, and §5.11's logo gate exist: they police the surfaces this structural mitigation no longer
covers.

**§5.6–§5.10 (round 2, operator-locked): the anti-ad Hard DON'Ts.** Source: `DESIGN_EXPANSION.md`
§C.2's five data-derived rules — each traceable to a specific delta between the corpus's winning
exemplar (+42.53 weighted) and its worst (-9.02, the rejected §2.14 reference). 5.6 and 5.7 are
anti-ad-vocabulary EXTENSIONS of 5.5 and 5.2 (the SAME regex constants gain alternations — one thing,
one place, `CODING_GUIDELINES.md` §2, the convention §5.3 already set for `BANNED_RENDERED_STRINGS`);
5.8–5.10 are net-new. §5.11 is the same-day logo-policy check (§2's logo-policy block), added in the
same (a)/(b)/(c) pattern.

### 5.6 No radial-glow / "premium gradient" hero grounds

**(a) Prompt wording** (same insertion point as 5.1): *"Never build the ground as a radial glow, glowing
ring/arc, or 'premium' luminous gradient engineered to look expensive — the ground is either this style
system's exact flat/textured recipe or a genuinely real environment; nothing engineered-to-impress in
between."* (The winning corpus exemplars have flat, real grounds; the radial purple glow is the single
most visually obvious ad-tell in the corpus's worst performer.)

**(b) Deterministic check** — extend `_GRADIENT_MESH_RE` (§5.5's OWN constant, not a second regex):
```
_GRADIENT_MESH_RE = re.compile(
    r"\b(gradient mesh|abstract gradient blob|iridescent (background|blob|gradient)|holographic blob|"
    r"blurred color blob|blurry gradient|"
    r"radial glow|glowing (arc|ring|orb|halo)|premium gradient|luminous (backdrop|background))\b",
    re.IGNORECASE,
)
```
Same two wiring points as 5.1.

**(c) N-E rubric:** `composition_ok` — extend the same clause 5.5(c) added, naming radial-glow/luminous
"premium" grounds as a failure explicitly.

### 5.7 No benefit-pill / checkmark-icon-row grammar

**(a)** *"Never render a row or stack of benefit pills, feature pills, or checkmark-bulleted selling
points — the direct-response 'features list' device. A checklist exists in this library only as a
typeset content pattern inside a designed body slot (§0's slot-roles note), never as pill-shaped
graphical furniture selling the offer."*

**(b)** — extend `_CLIPART_ROW_RE` (§5.2's OWN constant):
```
_CLIPART_ROW_RE = re.compile(
    r"\b(icon row|row of icons|clip[- ]?art|generic icons?|"
    r"benefit (pills?|list|checklist)|feature pills?|checkmark (pills?|bullets?|row)|"
    r"row of check(mark)?s)\b", re.IGNORECASE,
)
```
Same two wiring points.

**(c)** `composition_ok` — extend 5.2(c)'s row-of-icons clause to name pill-shaped benefit rows as the
same failure family.

### 5.8 No device-mockup / product-render insets

**(a)** *"Never depict a 3D-angled or floating laptop/phone/tablet/browser mockup showing a rendered
'finished product' — show the REAL environment the work happens in (a desk, a room, a corridor), never a
simulated rendering of an output. A screen may appear only as an unreadable light source (monitor glow),
or as a composited real screenshot asset under §2.2's rules."* (The device mockup is the rejected
reference's single most ad-coded element and doubles as a §5.4 fake-UI violation.)

**(b) Deterministic check** — new constant, same two wiring points as 5.1/5.2/5.4:
```
_DEVICE_MOCKUP_RE = re.compile(
    r"\b((laptop|phone|tablet|macbook|iphone|device|browser) mock[- ]?up|"
    r"3d[- ](angled|perspective|rendered) (laptop|phone|device|screen)|"
    r"floating (laptop|phone|device)|"
    r"(website|app|product) (rendered|displayed|shown) (on|inside) (a|the) (laptop|phone|device|screen))\b",
    re.IGNORECASE,
)
```

**(c)** `ui_fidelity_ok` (§5.4's boolean) — extend its rubric: a device mockup whose screen shows a
rendered/invented product is `false` by definition (it is an invented UI in a bezel); `composition_ok`
additionally names "no 3D device mockup as a composition element."

### 5.9 No urgency/price/CTA-banner language baked into the image

**(a)** *"No text on the image may carry landing-page conversion grammar: prices, discounts,
countdowns, 'order now'/'sign up today'/'book a call' urgency phrasing, or scarcity claims. Image CTA
text stays in the library's established follow/save register (§7). Caption copy is governed
separately — this rule is about pixels, not captions."*

**(b) Deterministic check** — new constant. Because this failure can arrive through COMPOSITED text
(which never passes through the RENDER prompt), this check wires at **three** points, one more than
5.1's two: the gated `on_image_text` strings at CRAFT time (N-C/N-F — the primary defense, bytes known
pre-render), the `<<...>>` spans pre-generation, and the QA response's free text post-generation:
```
_AD_BANNER_RE = re.compile(
    r"(\border (now|today|in \d+ (minutes?|mins?))\b|\bbuy now\b|\blimited[- ]time\b|"
    r"\bas low as\b|[$€]\s?\d+\s?/\s?(mo|month|week)\b|\bno (credit )?card (needed|required)\b|"
    r"\bsign up (now|today)\b|\bbook a (free )?(call|demo)\b|\bact (now|fast)\b|"
    r"\b\d+\s?% off\b|\bdiscount code\b|\bdm (me|us) \S+ for\b)", re.IGNORECASE,
)
```
(The last alternation also catches the comment-gate persona pattern `DESIGN_DECONSTRUCTION.md` §C.4
already rejected on persona grounds — one regex, two rules served.)

**(c)** `composition_ok` — extend with "no price/urgency/CTA-banner furniture (badges, countdown
strips, price callouts) anywhere on the canvas"; the deterministic scan remains the primary defense for
composited surfaces.

### 5.10 The stand-alone-content test — grounds must survive text removal

**(a)** *"For any slot whose ground diffuses, describe a genuinely complete scene — real props, real
light, a real sense of place — that would read as a finished photograph even before any text composites
on top. Never describe the image as a backdrop, template, or 'space for' a message; the reserved-zone
fragment supplied with the brief is the ONLY sanctioned way to request negative space."* (This is the
structural test separating the corpus's winning lifestyle photo — still compelling with the caption
removed — from the rejected ad card, meaningless with its copy stripped.)

**(b) Deterministic check** — new constant, scanned over the RENDER section EXCLUDING the fragment
inserted by `grounds.request_reserved_zone_prompt_fragment` (that fragment's fixed wording is the one
sanctioned negative-space request and is written to avoid every alternation below — checked):
```
_TEMPLATE_BACKDROP_RE = re.compile(
    r"\b(backdrop for|background for (the )?(text|copy|headline)|"
    r"(leave|leaving) (blank|empty) (space|room) for (the )?(text|copy|headline)|"
    r"copy[- ]space|awaiting (text|copy)|template background)\b", re.IGNORECASE,
)
```

**(c) New N-E boolean, `ground_standalone_ok`** (added to `VisionQaResult` alongside §5.4's
`ui_fidelity_ok`, and to the overall-pass computation): *"Judged for slots with
`ground_source: diffusion` only (vacuously true otherwise): true when the ground image, considered with
all composited text mentally removed, still reads as finished, deliberate content — a real photograph
or scene someone would post on its own; false when it reads as an unfinished template or backdrop
awaiting a message."*

### 5.11 Logo fidelity — diffusion-first marks are QA-gated (round-2 logo policy)

Not an anti-ad rule — the enforcement arm of §2's logo-policy block, in the same (a)/(b)/(c) pattern.

**(a) Prompt wording:** *"When a logo_zone names a third-party tool, ask for that tool's exact,
accurate, official logo mark — correct glyph shape, correct brand colors, nothing stylized,
reimagined, 'inspired by,' or generic. Render the mark and nothing else in that region: no invented UI
chrome around it (§5.4), no text beyond the mark's own official wordmark."*

**(b) Deterministic check** — new constant, pre-generation over the RENDER section (an authoring-time
defect catcher; actual mark fidelity is only judgeable by vision, (c)):
```
_LOGO_INVENT_RE = re.compile(
    r"\b((stylized|reimagined|redesigned|fictional|imaginary|generic|invented|custom) "
    r"(logo|mark|wordmark|app icon)|logo (inspired by|in the style of))\b", re.IGNORECASE,
)
```
Plus a nominative-use precondition, mechanically checkable: every tool name a `logo_zone` brief names
must appear in the asset's own copy/`allowed_facts` — a mark for a tool the copy never mentions fails
governance before submission (§3.6's nominative rule, made deterministic).

**(c) New N-E boolean, `logo_fidelity_ok`** (added to `VisionQaResult` and the overall-pass
computation; NEVER skipped when the prompt names a tool logo): *"true only when every depicted
third-party mark is accurate — correct glyph shape, correct colors, no invented/garbled/approximate
variant; also false when a mark appears that no gated brief requested."* **Failure wiring (the
fallback path, §2's logo-policy block):** on `logo_fidelity_ok == false`, the engine resolves the
tool's official brand-asset URL from `assets/logos/manifest.yaml` (manifest authored during plan
execution via websearch), lazily downloads via `urllib` into `assets/logos/cache/` (first need only —
cache is permanent), composites the real mark over the SAME `logo_zone` rect, and re-runs QA once. A
second failure fails the slot closed, decision-logged. No logo binaries are ever committed — the
manifest of URLs is the only tracked artifact.

---

### 5.12 Tool marks are mandatory, and a real product is never invented (round-4/5)

Two rules, one subject: **what we are allowed to depict when the copy names somebody else's product.**
Evidence: F8 (describing a mark beats naming it, ~50% → ~95%), F13 (unaided marks for mid/long-tail
tools come back as plausible *inventions*), F14/F15 (the fetch ladder works; a pasted asset beats a
redrawn one).

**(a) Prompt wording.** *"Every tool named in this card's text must appear as its real mark — icon
row, inline chip, or diagram node — rendered from the description supplied with this brief. Never
depict a tool the text does not name. Never render an invented screenshot, dashboard or interface of
a real product; where a real product's visual is required, this brief supplies an empty artifact
region and the engine composites the real asset into it."*

**(b) Deterministic checks (two, both at craft time).**

1. **Coverage (LG2, the hard rule).** Extract tool names from the slot's gated `on_image_text`
   (manifest keys + the style-guide topic lexicon). **Every named tool must have a mark in the
   brief**, and the brief must carry that tool's manifest `description:` verbatim. A named tool with
   no mark is a `GovernFailure`.
2. **Nominative use (§5.11's existing mirror check).** A mark for a tool the copy never names fails
   the same way. Coverage and nominative use are the two directions of one rule.

**(c) The three-tier ladder for a tool with no manifest entry** — resolved by `brand_assets`, honoured
by the renderer, recorded in provenance:

| Tier | What ships | Mechanism |
|---|---|---|
| **1** (default) | name + **real logo** + **real product visual** | fetch the tool's own site: `og:image` + `apple-touch-icon`/favicon; the render leaves an `artifact_zone` empty and Pillow composites the fetched bytes into it **pixel-exact** |
| **2** | name + **real logo**, on a styled typography card — no product visual anywhere | fetched icon only |
| **3** (fail-closed) | a **clearly ILLUSTRATIVE** stylized UI + a name chip, and the prompt says so in those words | no fetched bytes available |

**The integrity line, codified (invariant LG3):** *the engine never renders a diffusion-invented
"real-looking" screenshot of a real product.* A plausible invention is worse than an obviously wrong
one, because a casual viewer cannot tell. Note precisely what this does **not** forbid: an entirely
**fictional** business's website is a whole style class (§2.17) and a fictional mission-control
diorama is another (§2.20) — invented UI is fine when nothing about it claims to be real. The rule
bites only on *real products*.

**Operational notes.** Every fetch sends a **browser User-Agent** (a bare one gets 403 from vendor
sites and from the kie result CDN, verified in round 3), is GET-only, is restricted to the tool's own
origin, and is cached permanently. An **optional** operator-override folder
(`assets/logos/override/<tool>/`) wins over everything; it is never required and its absence is not a
degrade (`PLAN.md` §13 item 22.5).

### 5.13 Persona depiction — the illustration carve-out (round-6)

The library's rule has been "no people" since W8-10. The meme and illustration classes need a
human-vs-AI contrast to be funny, so the rule is refined rather than broken:

- **No human face is ever visible. In any class. No exceptions.**
- **Cartoon humans ARE permitted** in the illustration and meme classes (§2.19, §2.21) when the
  concept requires a human-vs-AI contrast — **strictly from behind, or with the face obscured**
  (turned away, cropped, buried in paperwork).
- **No depicted character is ever named**, and no depicted character is a real person.
- **`PersonaPolicy` is untouched.** That governs who *speaks* — still institutional, still never a
  named individual. This carve-out governs who may be *drawn*. Confusing the two is how the fa51
  invented-persona defect happened, so the two rules stay explicitly separate.

Enforced at craft time by a depiction check over the RENDER brief (a human is described ⇒ the
from-behind/face-obscured clause must be present) and post-render by N-E's `subject_relevant`
rubric, which fails any visible face. Invariant **PC1**.

## 6. Register-keyed leak table

Generalizes `promptcraft._EDITORIAL_LEAK_RE` (`promptcraft.py:679`, today `didone|cream[- ]?paper|
bone/cream`, checked only in the one direction "photographic register must not contain editorial
vocabulary," `promptcraft.py:744-750`). Eight of the eleven style systems in this document bind
`register: editorial`; round 2's three photoreal systems (§2.10–§2.12) bind `photographic_ugc` — still
no NEW register anywhere in this document (`hype` and `photographic_ugc` remain exactly as
`style_guide.yaml:168-190` already defines them; `hype` stays Phase-8-only). The round-2 consequence:
the symmetric table below now actively protects in BOTH directions *within this document's own
systems*, not just against the Phase-8 rotation — a photoreal system's prompt must never carry
editorial vocabulary, and an editorial system's must never carry photographic vocabulary. The table below is symmetric: for a prompt authored under register R, none of
the OTHER registers' signature vocabulary may appear anywhere in the prompt text (STYLE or RENDER) —
this is the same invariant the existing photographic-only check relies on
(`config/style_guide.yaml`'s `photographic_ugc` register text is written so it never uses editorial
vocabulary itself, `promptcraft.py:672-678`'s comment) generalized to all three directions.

| Register | Signature vocabulary (must NOT appear when a DIFFERENT register is active) | Pattern |
|---|---|---|
| `editorial` | didone, cream paper, bone/cream, italic serif display, checkbox pill, quoted prompt box | `didone\|cream[- ]?paper\|bone/cream\|italic serif display\|checkbox pill\|quoted prompt box` (extends the existing `_EDITORIAL_LEAK_RE`, `promptcraft.py:679`) |
| `hype` | near-black ground, condensed bold caps, yellow keyword highlight, link in bio, neon decor, 3D robot/mascot | `near-black\|condensed (bold\|caps)\|yellow keyword\|link in bio\|neon decor\|3d (robot\|mascot)` |
| `photographic_ugc` | photorealistic photograph ground, sticker-style text, tiktok caption style, phone-camera framing, talking-head framing | `sticker[- ]style text\|tiktok caption style\|phone[- ]camera (selfie\|framing)\|talking[- ]head framing` |

**Wiring:** `render_contract.govern()` step 4, "register/mode coherence"
(`RENDER_CONTRACT_SPEC.md:273-275`) looks up `contract.visual.register`, and for each of the OTHER two
registers' patterns, searches the full prompt text (STYLE + RENDER) — a match is a `GovernFailure`,
same failure class as today's single-direction check. `promptcraft.validate_crafted_prompt`
(`promptcraft.py:687-751`) gains the same table-driven check in place of its current single hardcoded
regex + `register == PHOTOGRAPHIC_REGISTER` branch (`promptcraft.py:744-750`) — the function's own
`register` parameter already exists and simply looks up `LEAK_TABLE[register]`'s *complement* (every
OTHER register's patterns) instead of a single hardcoded photographic-only check.

**Style-system-specific addition:** §2.6's `ig_prompt_sheet` `prompt_quote` slot deliberately uses a
dark ground (`#1E1B2E`) while remaining `register: editorial`. Its own STYLE section text (built by
`_build_style_section`, `promptcraft.py:294-383`) must describe this ground as "a dark terminal-style
card" or equivalent — never using the `hype` register's own `near-black` vocabulary verbatim, since that
exact string is the `hype` leak pattern above and would produce a false-positive block on a
legitimately dark-but-editorial slot. This is a content-authoring constraint on the STYLE-section
builder (§2.6's own ground description), not a change to the leak table itself. **Round-2 instances of
the same constraint:** `ig_value_sheet` (§2.9) and `ig_scene_hook`'s payoff slides (§2.11) reuse the
same `#1E1B2E` ground and inherit the same rule verbatim ("dark terminal-style card," never
`near-black`); `ig_scene_hook`/`li_scene_hero`'s scene directives describe darkness as
"dusk"/"night-lit"/"monitor glow" — never the `hype` table's `near-black` token — and, being
`photographic_ugc`-registered, must also avoid the editorial row's vocabulary (no "cream paper" prose
in a scene prompt, which §2.11's directive already satisfies).

---

## 7. Hook/copy guidance per system

`FINDINGS_SYNTHESIS.md` §5's four winning hook patterns — numbered-promise, dollar/time-boxed
specificity, tutorial-promise, and a fourth pattern rewritten below (see the reframe note) — adapted
facelessly (locked decision 1: institutional voice, no invented personas) per system.

**ILLUSTRATIVE ONLY — every quoted line below is a pattern demonstration, not shippable copy.** N-C's
authoring prompt must never embed these exact sentences, and a literal string match between shipped copy
and any example below is itself a defect — it is exactly the templated, AI-average English this overhaul
exists to kill. The instruction to the copywriter is: *adapt the rhetorical pattern (numbered-promise,
dollar/time-boxed specificity, tutorial-promise, trend-observation), never reuse the wording verbatim.*
Production copy is generated fresh from the run's own brief, `allowed_facts`, and gated numbers — these
four lines per system exist only to show the SHAPE of each pattern.

**Confessional-reveal, reframed.** The original four-pattern set's "confessional-reveal" is an
institution "admitting" something it did and cannot evidence — an unverifiable, invented anecdote, the
same failure class as an invented persona (`RENDER_CONTRACT_SPEC.md:62-68`), just first-person-plural
instead of first-person-singular. Every instance below is rewritten as a **trend-observation** grounded
in the run's own viral playbook (a claim about the space/format, not about HypeDigitaly's own unverified
history) rather than an institutional confession. The same test applies to every other first-person-plural
example in this section: if a claim would need an `allowed_facts` entry to ship and none exists for it,
the line does not use "we"/"our" at all — it stays a general, sourced, or offered-artifact claim.

**`li_signal_card` / `ig_annotated_proof` (n8n + Apify lead-gen workflow):**
- Numbered-promise → *"3 signals your lead-gen stack should be scoring automatically — most agencies
  check none of them by hand anymore."*
- Dollar/time-boxed → *"n8n + Apify turned a 6-hour weekly scrape into an 11-minute automated run — the
  workflow, screenshot by screenshot."*
- Tutorial-promise → *"n8n + Apify: the lead-gen workflow — setup walkthrough."*
- Trend-observation (reframed from confessional-reveal) → *"Manual scrape-checking is the first thing
  most lead-gen teams automate away — here's the exact workflow that replaces it."* (a claim about the
  space, not an unverifiable HypeDigitaly-did-this-first claim.)

**`li_statement_hero` / `ig_stat_slab` (AI sales-agent lead scoring + stat):**
- Numbered-promise → *"1 number every AI sales agent should be reporting — and most still don't."*
- Dollar/time-boxed → *"+38% qualified-lead accuracy is the kind of swing one well-set scoring threshold
  can produce — the exact threshold, sourced in the caption."* (no "we set" — the number must be an
  `allowed_facts`/claim-gate-sourced figure if it ships at all, never an unverified first-person claim.)
- Tutorial-promise → *"AI lead scoring — the threshold-setting guide."*
- Trend-observation (reframed from confessional-reveal) → *"Most lead-scoring passes look worse than
  they need to until one threshold gets fixed — here's the number, sourced in the caption."*

**`li_editorial_brief` / `ig_prompt_sheet` (Claude ops-assistant for founders):**
- Numbered-promise → *"5 prompts that keep a founder's ops moving when run through Claude every week —
  one is below, verbatim."* (no "we run" — the offered artifact is the prompt itself, not a claimed
  internal habit.)
- Dollar/time-boxed → *"A 90-second Claude prompt now does what used to take a founder's whole Monday
  morning."*
- Tutorial-promise → *"Claude as an ops assistant — the exact prompt, setup guide."*
- Trend-observation (reframed from confessional-reveal) → *"Founders running their ops review by hand
  are the ones still losing a morning to it every week — here's the Claude prompt that replaces that
  review, exact text, no edits."*

Every rewrite above satisfies the persona policy (`RENDER_CONTRACT_SPEC.md:62-68`): speaker is
`HypeDigitaly`/`we` only where the claim is genuinely sourceable, never a first-person-singular named
individual; every claim is either (a) a general trend-observation grounded in this document's own viral
playbook (`FINDINGS_SYNTHESIS.md` §5), (b) a sourced number backed by an `allowed_facts` entry and
co-located per §6's claim-gate rule, or (c) an offered artifact (the prompt itself) — never a fabricated
personal or institutional anecdote.

**Corporate-slop ban list.** The mirror-image failure mode to an invented persona is institutional-voice
slop — a HypeDigitaly-branded claim that reads like generic marketing copy rather than an actual
sourced fact or offered artifact. The following phrases are banned in any copy this document's eleven
systems produce: `"we believe"`, `"our mission"`, `"we're proud to"` / `"we're excited to"`, `"empowering"`,
`"seamless"`, `"cutting-edge"`, `"at HypeDigitaly, we"`. **These are added to the deterministic pre-filter
regex, not just to prose guidance** — extend `copy_gen._SLOP_TELL_RE` (`copy_gen.py:964-967`, the
existing $0 regex pre-filter `humanness_prefilter` already runs before N-F, `copy_gen.py:978-1011`) with
the alternation below, in the SAME constant (one thing, one place — `CODING_GUIDELINES.md` §2), not a
second parallel regex object:
```python
_SLOP_TELL_RE = re.compile(
    r"\b(actually|quietly|in the space|drowning in|isn't just|creators are reporting|game.?chang\w*|"
    r"delve|we believe|our mission|we're (proud|excited) to|we are (proud|excited) to|empowering|"
    r"seamless|cutting-edge|at hypedigitaly,? we)\b",
    re.IGNORECASE,
)
```
(All illustrative lines above were checked against this exact extended pattern — none trip it.)

**Round-2 systems (§2.9–§2.13) reuse the same four rhetorical patterns unchanged** — no new per-system
example set is warranted, since the patterns are topic-shaped, not system-shaped. Two round-2-specific
constraints on their hooks: `ig_scene_hook`/`li_scene_hero` hooks stay inside the ≤2-span/≤6-word
creative bound (§2.11) and must be defensible statements, never fabricated-stakes drama (the §2.11
directive's NEVER list applies to the words as much as the pixels); and no on-image CTA/hook text in
ANY system may trip §5.9's `_AD_BANNER_RE` (urgency/price/conversion grammar) — that check runs on the
gated strings themselves, before any rendering.

---

### 7.1 Gold-standard caption exemplars (round-4/5/6, ratified — `PLAN.md` §13 item 24)

These four captions are the **few-shot gold standard** injected into the N-C prompt, selected by the
asset's `format_class` and language (default `en`; the `cs` set is §7's existing exemplars plus the
three ratified lines in `PLAN.md` §13 item 19.D). Like every exemplar in this document they are a
**voice-only** grounding source — never `allowed_facts`.

**Website showcase (Instagram):**
> A bakery with no website got one by dinner.
> The workflow: Claude reads your customer reviews and writes the copy. Lovable turns it into a
> working site. One evening, zero code.
> Save this for the next time an agency quotes you six weeks.
> #aitools #automation #smallbusiness

**Artifact showcase / workflow map (LinkedIn):**
> A lead came in at 2:00 AM. The reply went out at 2:01.
> Nobody woke up.
> The stack: a web form, Zapier, Claude, Gmail. Four pieces, one afternoon to set up. The lead booked
> a call before breakfast.
> Speed is the cheapest advantage left. The exact setup is in the comments.

**Meme (Instagram — short, the image carries it):**
> Somewhere, an ops coordinator just felt a disturbance.
> #aiagents #opslife

**Brand promo (Instagram):**
> Free AI audit: we map where your team loses the most hours and which two automations pay for
> themselves first. 30 minutes, no obligation.
> Click the link in bio to book.

**The rules these encode** — all of them prompt lines, and the last two deterministic caps:

1. **Hook line first.** One sentence, standing alone, that could be the whole post.
2. **Concrete specifics** — a time, a count, a named tool (D6). "2:00 AM / 2:01", "four pieces",
   "30 minutes", "six weeks". This is the copy-side partner of the slide-value gate.
3. **Zero slop vocabulary.** The existing pre-filter gains *game-changer*, *unlock*, *revolutionize*.
4. **Meme captions stay minimal** — the image carries the joke (§2.21's `instant_read`).
5. **Promo CTA is the link-in-bio pattern**, matching §2.22's verbatim on-image pill.
6. **Hashtags: ≤3 on LinkedIn, ≤5 on Instagram** — `caps["hashtag_max_count"]`, enforced at
   authoring like every other cap.

## 8. Acceptance criteria

### 8.1 Shared, all systems

- [ ] `VisualPolicy.style_system` resolves deterministically per §4.1's two-stage algorithm;
      re-running the same `run_date` + config + Virlo corpus + asset list yields the identical
      `asset_id → format_class` map and the identical per-asset `style_system`. The Virlo reweight
      decision (shift or no-shift, with all class rates and sample counts) appears in the decision
      log; a `--resume` reads the stage-1 map back from `resume_state.yaml`, never re-derives it.
- [ ] A 6-asset run under the default `generation.format_quota` (absent a logged reweight/substitution)
      delivers exactly 2 `designed_card`, 2 `photoreal`, 1 `editorial_grotesque`, 1 `serif_editorial`
      assets; a theme config WITHOUT `format_quota` runs round-1 selection unchanged (§4.1 step 0).
- [ ] Every case-(b) slot's `reserved_text_zone` equals the bounding rect of that slot's `zones:`
      entries as published in §2/§3.1, was handed to `grounds.request_reserved_zone_prompt_fragment`,
      and `check_ground_safe_zone` ran (pass, or logged programmatic-ground degrade) before
      compositing.
- [ ] Every third-party mark followed §2's logo policy: diffusion-first brief naming the exact tool,
      `logo_fidelity_ok` judged (never skipped), and — on failure — the manifest-fetch composite +
      single QA re-run, all ledger-recorded; no logo binary committed to the repo.
- [ ] `VisualPolicy.register`/`archetype`/`mode` exactly match the table in §2's "Register/mapping" line
      for that system — no silent divergence from the pinned archetype (§1 note).
- [ ] Every hex value rendered (ground, text, accent) matches §2/§3.1's palette recipe exactly — spot
      checked by pixel sample, not just prompt text.
- [ ] Type: the fallback family actually used is `NotoSans-Variable.ttf` at the weight named in §2/§3.1
      until a serif/mono font is acquired; the Czech glyph test (`assets/fonts/README.md`) still passes
      after compositing (no `.notdef` boxes) for every composited slot.
- [ ] Every slot's rendered word count is ≤ its `SlotSpec` cap (`RENDER_CONTRACT_SPEC.md:317-327`) —
      `slide_body_max_words`/`headline_max_words` from `ConstraintSet.caps`, not a system-local number —
      except `ig_prompt_sheet`'s `prompt_quote`, capped at its own derived `prompt_quote_max_words: 50`
      (§2.6) instead.
- [ ] `layout.py.resolve_layout_recipe(role, style_system)` returns the exact `zones:` list published in
      §2/§3.1 for that pair — every zone's `rect_pct` fully inside `[0,1]×[0,1]`, no two zones in the
      same slot overlapping, and every required zone name present (`cover`→`headline`, `end_card`→`cta`,
      `hero`/`body`/`prompt_quote`→ per §2's zone-contract intro).
- [ ] For any slot with `text_render_mode: diffusion`, its `ground_source` is `diffusion` (never
      `programmatic`, per `COMPOSITING_SPEC.md` §3 case c) — §2.7's diffusion-surface census matches the
      shipped `slots.*.ground_source`/`text_render_mode` values exactly, per system.
- [ ] None of the §5 Hard DON'T vocabulary (5.1–5.11's regexes) appears in any submitted prompt or in
      any QA response's free text — and 5.9's `_AD_BANNER_RE` additionally matches nothing in any
      gated `on_image_text` string (its third wiring point).
- [ ] None of §6's leak-table vocabulary for a DIFFERENT register appears anywhere in the prompt.
- [ ] For a carousel (Instagram systems only), all 5 slots share the identical `style_system` value and
      `series_consistent` passes slide-to-cover for every non-cover slide (§4.2).
- [ ] N-E's `text_matches`, `subject_relevant`, `logos_ok`, `composition_ok`, and (once added:
      `ui_fidelity_ok` §5.4, `ground_standalone_ok` §5.10, `logo_fidelity_ok` §5.11) are all `true`
      for every delivered image of this system.
- [ ] No image ships with a mismatches list — a non-empty mismatches list is never an overall pass
      (`media_gen.py:935-936`, unchanged).

**Round-4/5/6 additions (`PLAN.md` §13 items 19-25):**

- [ ] **Every delivered image's rendered text is character-identical to its gated `on_image_text`**,
      verified per glyph by N-E — and the run reports the ladder distribution (delivered at rung 1 /
      after the retry / by composited fallback / copy-only). A retry rate materially above the
      simulation's ~5% is a signal to revisit the flip, not a detail.
- [ ] Every submitted prompt contains **at least one of its own system's palette hexes as a literal**,
      and **exactly one** emphasis token (teal default · indigo-italic for serif · amber only on
      numerals/times) — §3.6, D2.
- [ ] Every scene/illustration prompt carries the screens-off sentence verbatim; no delivered scene
      shows readable UI on a monitor (F11).
- [ ] Every card-class slot carries its **caps kicker and `HYPEDIGITALY` wordmark footer** (D3), and
      its ground is warm cream or cinematic dark — no mid-gray, cold, saturated or gradient ground
      appears as any system's default (D1).
- [ ] **Every tool named in the copy has its mark rendered** and no mark appears for a tool the copy
      does not name (§5.12, LG2); every unknown tool resolved to a recorded tier, with Tier 3 output
      explicitly illustrative and **no invented "real-looking" screenshot of a real product** (LG3).
- [ ] **No human face is visible in any delivered image**; any cartoon human is from behind or
      face-obscured, and no depicted character is named (§5.13, PC1).
- [ ] The reserved **`brand_promo`** asset shipped with its CTA pill text **verbatim** from config,
      and the reserved **meme** asset shipped, alternated class against the previous run, and its
      joke reads in about a second (§2.21-§2.22, §13 items 24-25).
- [ ] `hard_dont_exemptions` appears **only** on `brand_promo` systems (§5.6-§5.10) and
      `concept_dashboard` (§5.6); consistency check 11 is green.
- [ ] The stage-1 quota resolved to `serif_editorial 1 / photoreal 1 / artifact_showcase 1 /
      illustration 2 / occasional 1` with **distinct** group members, plus the two reserved assets —
      8 assets total — and the **carousel decision** (with its counts and rates) is a decision event
      whether or not it fired.
- [ ] Every asset's language came from `batch_composition.language_by_destination` (default `en`),
      never from a model (LANG1).

### 8.2 Per-system deltas

| System | Additional checks |
|---|---|
| `li_signal_card` | Both tool marks present and accurate (`logo_fidelity_ok`, §5.11 — diffusion-first per §2's logo policy, with the manifest-composite fallback ledger-recorded on any repair); ground and every text span programmatic/composited — the `logo_zone` is the asset's ONLY diffusion surface (§2.7's corrected row). |
| `ig_annotated_proof` | Screenshot inset is either a real composited asset or absent — never a diffusion-rendered fake (verify provenance tag on the inset element); annotation marks carry no text at all; `cover.ground_source=diffusion`/`cover.text_render_mode=diffusion` is the ONLY diffusion call in the asset (§2.7). |
| `li_statement_hero` | Numeral + qualification line pass the claim gate as ONE co-located unit (`RENDER_CONTRACT_SPEC.md` §6); numeral is a gated `on_image_text` span, never sourced from `image_brief`. |
| `ig_stat_slab` | Ground color alternates indigo/teal/indigo/teal/indigo across the 5 slides exactly (§4.2's system-specific `series_consistent` addition); exactly one diffusion call per asset under the shipped default (`cover` only, §2.7) — zero if the documented non-default override is exercised. |
| `li_editorial_brief` | No pictorial icon anywhere (vector accent is a single geometric shape, checked against §5.2); attribution line never names an individual (persona-policy speaker check). |
| `ig_prompt_sheet` | `prompt_quote` slot's ground is `#1E1B2E`, never described with `hype`-register vocabulary (§6's style-system-specific note); prompt text is byte-identical (draw-then-compare, per `COMPOSITING_SPEC.md` §5 — no OCR dependency exists or is added) to the gated `on_image_text` string, `text_render_mode=composited` confirmed in the ledger (never `diffusion` for this one slot, under any fallback); rendered word count ≤ `prompt_quote_max_words: 50` (§2.6); cover Claude mark accurate + nominative (`logo_fidelity_ok`, §5.11/§3.6) — the asset's only diffusion surface. |
| `ig_value_sheet` | Ground restyled to cream serif-editorial (round-4/5 DNA anti-signal, §3.1); like every system its slots are canonical full-design renders — the round-2 "zero diffusion calls" row is void (§2.7); dense-slide rendered word count ≤ `value_sheet_max_words: 220` enforced at CRAFT time; the `type_floor: 0.0185` Czech-glyph legibility verification on the vendored Lora file is recorded BEFORE the system's first ship (§2.9/§3.5). |
| `ig_lifestyle_stack` | No face or figure-as-subject in any of the 5 diffused grounds (persona policy; §2.10's directive + N-E `subject_relevant`); all captions composited (zero diffusion text); `ground_standalone_ok` true on all 5 slots (§5.10); environment family consistent across slides (§4.2); no logo mark depicted anywhere (§2.10 — the logo policy never engages). |
| `ig_scene_hook` / `li_scene_hero` | Scene slots pass `ground_standalone_ok`; no robot/mascot/catastrophe imagery and no person (§2.11's directive NEVER list); dark payoff slides and scene prose avoid `near-black` (§6); hook stays ≤2 spans × ≤6 words even though composited (creative constraint, §2.11/§2.8); ground-type rhythm matches §4.2's stated sequence (IG only). |
| `ig_operator_grid` | The `photo_inset` (when present) is a text-free photograph — `ui_fidelity_ok` + §5.8 + the `grid_photo_inset` directive's NO-readable-text rule; headline emphasis run renders in `emphasis_ink` ONLY once the rich-text capability lands, otherwise whole-headline `headline_ink` (never a diffusion approximation — §2.13's interim rule); highlighter bar is `#E8A63B` (or the documented teal fallback), never any other hue (§3.6); masthead/footer furniture present on all 5 slides (§4.2). |
