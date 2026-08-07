# DESIGN_DECONSTRUCTION.md — @aisimplified23 vs. our six style systems

*Written 2026-08-07. Source images: all 15 JPGs in this directory (viewed directly, hex values below are
visual estimates from those pixels, not a color-picker sample — treat as "close enough to design against,"
re-sample from source before locking a palette token). Source data: `CATALOG.md` in this directory.
Target spec: `../../STYLE_SYSTEMS_SPEC.md` §0-§2 (read in full for this document).*

**Scoping note (important — read before anything else in this file).** Of the 15 images, 4 are **not**
this creator's own design system: `60-claude-prompts_cover.jpg` and `36-free-prompts_cover.jpg` carry
third-party watermarks (`@leadgenman`, "Mobile Editing Club" — `CATALOG.md` §5's own note) and are
whitelabel reposts in a completely different visual language (dark chat-UI mockup; bold condensed sans +
real face photography). They are analyzed below only as **anti-patterns** to explicitly reject. The
**native aisimplified23 system** — the one worth deconstructing — is the 11 remaining images:
`start-a-business_s1..s9` (full carousel, native system's best-performing post), `master-claude-skills_
cover.jpg` + `_s2.jpg`, `linkedin-roast-skill_cover.jpg`, and `5-prompts-content_cover.jpg`. All of §A
below describes that 11-image native system unless explicitly marked "whitelabel outlier."

---

## A. The creator's design system, precisely

### A.1 Palette (visual estimates)

| Surface | Hex (est.) | Notes |
|---|---|---|
| Paper ground (all light slides) | `#F1ECE1` | warm bone/oatmeal, NOT neutral gray-cream — warmer/yellower than our `#F2F0EC`. Fine, uniform, low-opacity speck-noise grain across 100% of the ground (looks like a generated grain filter at ~4-6% opacity, not a photographed paper texture — too regular/uniform to be a photo scan). |
| Headline ink | `#221F1C` | near-black warm charcoal, not pure `#000`. |
| Body ink | `#332F2B` | dark warm gray, one step lighter than headline ink — a real two-step ink hierarchy, not one flat "text color." |
| Accent teal/mint (pills, checkbox outline, rules) | `#4CC2B6` | saturated cyan-teal, fills the "Steal this prompt:" / "Files:" / "Cowork prompt template:" pill labels solid, with italic serif text in white/near-black on top. |
| Pale mint tint (one solid callout box only, `s4`) | `#B9F1EA` | a lighter tint of the same teal, used exactly once in the reviewed set as a filled pull-quote block — not a recurring surface. |
| Coral/orange (Claude mark only — see §A.4 and §C on trademark risk) | `#DD7A54` | muted terracotta-orange, not neon. Appears as a 3D beveled app-icon tile (with drop shadow) on `start-a-business_s1` and as a bare hand-inked asterisk/starburst mark (no box) on `master-claude-skills_cover` and `linkedin-roast-skill_cover`. |
| Dark ground, native cover 1 (`5-prompts-content_cover.jpg`) | `#382F2A` | deep warm mocha/umber — a dark *variant of the same paper family* (warm, not cool), not our indigo-black. |
| Dark ground, whitelabel outlier (`60-claude-prompts_cover.jpg`, not native — see scoping note) | `#221E1B` | near-black warm brown; excluded from adoption, listed for completeness only. |

**Discipline worth naming explicitly: the two accents never coexist on one slide.** Across the native
11-image set, coral appears **only** on hook/cover slides (and only as the Claude mark itself); teal
appears **only** on payload slides (checkboxes, pill labels, rules). They are role-segregated, not
layered — coral = "this is the hook," teal = "this is the payoff." No slide in the native set uses both.

### A.2 Typography

**Two-family-by-role, but really one perceptual family (a serif, always).** Everything — headline,
body paragraph, checklist rows, card labels, kicker — is set in **serif** type. Sans-serif appears
nowhere in the native system. This is the single largest typographic delta from our current spec, which
keeps `body_family: Montserrat Regular` (sans) even inside the two serif-branded systems (see §B).

- **Display headline** (hook slides, step headlines): **Bold Italic**, high thick-thin stroke contrast,
  ball/bracketed terminals — visually a Didone/transitional display cut (closest OFL match: **Playfair
  Display Bold Italic**, see §C). Used for the "hero phrase" of every headline.
- **The two-weight-within-one-headline device.** Nearly every headline splits into a heavier lead phrase
  (Bold Italic, larger) and a lighter qualifying continuation (smaller, either Roman or a lighter-weight
  Italic — e.g. `s1`: "**How To Use / Claude To**" (Bold Italic) → "Start A Business…" (lighter, upright);
  `linkedin-roast-skill_cover`: "**5 Claude / Prompts**" (Bold Italic) → "To Roast Your LinkedIn" (lighter,
  upright); `master-claude-skills_cover`: "**How To Master / Claude Skills**" (Bold Italic) → "A Complete
  Guide" (lighter italic)). This creates a hierarchy *inside a single headline zone* without a second
  headline zone — efficient, and it reads as "spoken emphasis," not a template.
- **Body paragraph / checklist rows**: Roman (upright) serif, Regular weight, moderate contrast — reads
  legibly at small size (unlike a Bold Italic Didone would at this size).
- **Emphasis logic is 100% typographic, never color or case:** italic = (a) headline drama, or (b) a
  quotable/reusable artifact (prompt text, file names inside the "Files:" card, the UI-path pill labels).
  Bold roman = a lead-in category word inside a checklist row (e.g. "**Strategy Project:** positioning,
  research…"). Never underlines body text, never all-caps for emphasis, never a color highlight.
- **Casing is not rigidly systematized** — Title Case on steps 1-4 ("Validate Your Idea Before You Build
  Anything…", "Build A Project For Each Function"), drifting to sentence case on steps 6-9 ("Graduate to
  Cowork to produce real documents", "Set up a daily business brief"). This reads as human-typed, not
  mail-merged — see §A.6.
- **Kicker** ("Step 1", "Step 2"…): tiny, plain Roman serif, not bold, not a pill/badge — the most
  minimal-effort element on the slide, which is itself a restraint signal.

**Size hierarchy, % of 1350px canvas height (matches our existing convention closely — see §B):**

| Element | Est. size (% of height) | Line-height | Notes |
|---|---|---|---|
| Cover headline | ~8-10%/line | ~1.05-1.1 | tight, punchy |
| Step headline (2 lines) | ~7-9%/line | ~1.1-1.15 | slightly smaller than cover |
| Kicker ("Step N") | ~2.2-2.6% | 1.0 | plain, unstyled |
| Body paragraph | ~2.6-3.0% | ~1.3-1.4 | readability-tuned |
| Checklist row / card label | ~2.6-2.8% | ~1.3 | |

These numbers land almost exactly inside our spec's existing `type_scale` values (0.026-0.032 body,
0.07-0.09 headline) — **the numeric scale is already well-calibrated; the gap is font family, not size.**

### A.3 Texture & grounds

Flat paper-cream ground with a uniform low-opacity speck/grain overlay (not a photographed texture —
too regular). No vignette, no drop shadow on the ground itself. Cards (checklist rows, comparison-card
halves, the 2×3 icon grid) sit on the paper as flat, matte "paper cards": rounded corners (moderate
radius, not full-pill except the pill labels themselves), a hairline border ~1px in a slightly darker
tan (~`#E4DFD3`), little-to-no drop shadow — deliberately flat/matte, not skeuomorphic-glossy. Pill
labels (teal fill) carry a small, subtle lift shadow (~2-3px offset, low opacity), consistent with our
spec's existing `shadow_pct: 3` convention.

### A.4 Iconography

- **Coral 3D asterisk / starburst (the Claude mark — see §C trademark flag):** two forms observed — (a)
  the literal Claude app icon: rounded-square coral tile, diagonal bevel gradient, drop shadow, white
  12-spoke asterisk inside, used once on `s1`; (b) a bare hand-inked asterisk/starburst (no box), spokes
  *not* perfectly radially uniform — a genuinely imperfect, hand-drawn quality — used as a small flourish
  on two other covers.
- **Hand-drawn monoline icons** (lightbulb+bolt, browser+gear, folder+upload-arrow, browser+code, notepad
  +pencil-check, and 6 more in the 2×3 grid on `s5`): single-weight black outline, ~2-3px stroke, loose/
  slightly naive linework — reads as a quick pen sketch, not a polished icon-font glyph. Always placed
  either to the immediate left of an intro paragraph (single icon per slide, ~60-90px) or centered above a
  short caption (only in the 2×3 grid). **Every icon in the whole 9-slide carousel is the same monoline
  family — never mixed with a different icon style.**
- **Checkbox glyphs:** teal outline rounded-square, **unchecked/empty**, is the default "to-do" state
  across most slides. On `s8` (the "use Claude Code to build" step) the same rows instead use a **solid
  filled teal circle-checkmark** — a deliberate semantic shift ("this list is already-true capabilities,"
  not "things to do"). A small, high-craft detail.
- **Arrows:** a thin right-arrow (→) glyph appears *only* inside the UI-path breadcrumb ("Settings →
  Connectors → Browse → Add") — never used as a generic decorative directional element elsewhere.
- **Underlines:** used exactly twice in the reviewed set — under the "Without Skills" / "With Skills"
  column headers, and as a divider rule between the closing analogy lines. Never under body copy.
- **What never appears (native system):** no human faces, no photography of any kind, no clip-art icon
  *rows* (icons are always single, always the one monoline style), no gradient-mesh/blob backgrounds, no
  heavy skeuomorphism, no more-than-3-hue palette per slide (neutral paper/ink + exactly one accent).

### A.5 Layout anatomy per slide role

**Hook slide.** Extremely generous whitespace — roughly 55-65% of the canvas is empty paper. Icon +
headline block occupies a Y-band of roughly 22-70% (`s1`) or is pulled toward vertical center with even
more top/bottom air (`master-claude-skills_cover`, ~30%+ margin each side). Left-aligned (not centered),
left margin ≈8% of width (tighter than our spec's 12% safe zone — flag in §B). No CTA, no handle, no
watermark on native covers. The trailing ellipsis ("…") on the headline is the only "keep going" signal.

**Guide/step payload slide (70-85 words).** Never columns for prose — a vertical stack from a **fixed
kit of ~7 parts** (kicker, 2-line headline, optional icon+intro-paragraph, optional bordered "artifact
card" [prompt quote / file list / UI-path breadcrumb], optional 3-row checklist, optional 2×3 icon grid,
optional two-column comparison, optional solid-tint pull-quote box). Any one slide draws **3-4 of those 7
parts, never all of them** — that restraint, not any columnar trick, is what makes 70-85 words feel
spacious rather than crammed. True columns appear only twice in the whole reviewed set: the 2×3
icon-caption grid (`s5`, parallel enumerable items) and the Without/With two-column comparison
(`master-claude-skills_s2`, parallel enumerable items) — never for general prose.

**Dense cheat-sheet slide (230-540 words) — not pixel-verified in this download; described from
`CATALOG.md` §2B/§4 only, flagged honestly.** 6-10 numbered/categorized prompt cards per slide on a dark
card-UI ground, category header + "N/10" progress counter, persistent footer progress markers
("attract → convert → retain → operate"), occasional "SWIPE" nudge. Explicitly built for save-then-zoom
consumption, not in-feed reading (`CATALOG.md` §4).

**Closing reference-table slide.** `s9` (the actual final slide of the 9-slide, best-performing carousel)
confirms `CATALOG.md`'s claim precisely: the closer is **not** a CTA. It reuses the exact same
"artifact card" component (teal pill label + italic quoted prompt) as the final beat — no follow/like/
share graphic at all. This directly contradicts our `end_card` slot's universal "Follow for more…"
pattern — flagged as a gap in §C.

### A.6 The "handwriting" details — why this reads premium, not template

1. Two-accent-color discipline, never mixed on one slide (§A.1).
2. Total icon-style consistency across an entire 9-slide carousel — one monoline family, no exceptions.
3. Whitespace as the dominant visual weight, even on "dense" payload slides.
4. Subtle grain keeps flat digital cards from reading sterile.
5. **Genuine micro-inconsistencies read as human, not mail-merge:** casing drifts Title Case → sentence
   case slide-to-slide; the hand-inked asterisk's spokes are not uniform length; the checkbox glyph
   itself changes meaning (outline→filled) for exactly one thematically "done" step. These are the kind
   of imperfections a rigid template generator would never produce, and they are precisely what makes
   this deck feel authored rather than assembled.
6. The two-weight-per-headline device (§A.2) creates hierarchy without a second zone.
7. The "artifact card" is always visually distinct (border + pill label), never blends into body copy —
   typographically pre-flagging "this part is the payoff, screenshot this."

---

## B. Mapping onto our six style systems — concrete deltas

### `li_editorial_brief` / `ig_prompt_sheet` (both already cream+serif — closest match, most deltas)

**Validates as-is:**
- Cream paper ground family (`#F2F0EC` region), single teal accent, `editorial-carousel`'s own written
  description ("cream/bone paper texture, italic Didone serif headlines, teal accent checkboxes, quoted
  prompt boxes," `style_guide.yaml:126`) is now near-verbatim image-confirmed — strong validation the
  archetype prose was accurate even before any reference existed.
- The existing `type_scale` numbers (§A.2 table above) — no size changes needed, only family.
- The `prompt_quote` slot's *concept* (a visually distinct, bordered quoted-artifact treatment) is
  validated in spirit.

**Change — concrete proposals:**

```yaml
# palette nudge — warmer bone, closer to the observed ground
paper_ground_warm: "#F1ECE1"          # optional alternate/refined value alongside existing #F2F0EC

# grain, currently unspecified beyond "paper texture"
paper_grain:
  opacity_pct: 5                       # 4-6% observed
  speck_density: low
  uniform: true                        # no fiber/crumple deformation — a flat generated-grain look

# body typeface — the single biggest fidelity gap: reference is all-serif, our spec keeps body sans
body_family: "<acquired serif> Roman"  # was: Montserrat Regular — see §C font pick
body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"   # unchanged until acquisition lands

# two-weight-within-one-headline device — needs a family with Bold Italic + a lighter Italic/Roman cut
headline_split: true                   # hero phrase Bold Italic, qualifier phrase lighter weight, same zone

# NEW optional sub-zone on the `body` slot recipe — reference embeds a compact artifact card
# (bordered box + teal pill label + italic quote/file-name) INSIDE every payload slide, alongside its
# checklist rows — our spec today reserves that entire treatment for one dedicated `prompt_quote` slide.
inline_artifact_card:                  # optional, body slot only, not required every slide
  rect_pct: [0.12, 0.58, 0.76, 0.20]
  pill_label: true                     # teal-filled pill, e.g. "Steal this prompt:" / "Files:"
  content_style: italic_quote          # italic serif, quoted content, byte-identical to gated string

# checkbox glyph, currently prose-only ("✓ + short line") — formalize the two observed states
checklist:
  checkbox_style: outline_square       # default — "to-do" semantics
  checkbox_style_done: filled_circle   # optional variant — "already-true capability" semantics, teal fill

# NEW optional icon slot — reference always pairs a small monoline topic icon with the intro paragraph
icon_zone: [0.12, 0.24, 0.08, 0.06]    # small, ~8% width square, body slot only — new asset-library dependency (flagged)

# end_card override — the reference's best carousel skips the CTA entirely
end_card_override: artifact_close      # optional: 5th slot becomes another body/artifact beat instead of "Follow for more" — per-asset choice, not a system default (see §C)
```

- **Cover `max_spans` reconsideration.** `ig_prompt_sheet`'s cover is already firmed to
  `text_render_mode: composited` (§2.6), yet still inherits `max_spans: 2` — a constraint whose entire
  rationale is diffusion-model text-legibility risk (`diffusion_text_max_spans=2`). A composited cover has
  **zero** gibberish risk regardless of span count. The reference's richest native cover-adjacent slides
  (kicker + headline + qualifier, sometimes + a small artifact element) prove a 3-4-span composited hook
  reads well and is exactly what a fully-typeset cover *should* be allowed to do. Propose: for any slot
  where `text_render_mode: composited`, `max_spans` is a layout choice (however many zones the recipe
  defines), not a hard-capped-at-2 rule — the 2-span cap stays exactly as-is for `diffusion` slots only.

### Other four systems (`li_signal_card`, `ig_annotated_proof`, `li_statement_hero`, `ig_stat_slab`)

No material deltas. These are brand-gradient / solid-slab / screenshot-annotated systems in a register
the reference doesn't touch at all — the reference's entire sampled corpus lives in what we call
`editorial`; it has no gradient-card, dark-hype, or photographic-UGC equivalent to compare against. Keep
as specified.

---

## C. Gaps — what our spec cannot produce today

### C.1 New style system: `ig_value_sheet` — the dense cheat-sheet format

Our global `slide body ≤24 words` ceiling makes the reference's 230-540-word payload slides structurally
impossible today. That density is not a mistake to fix — `CATALOG.md` §4 is explicit that these slides
are **saved, then zoomed**, not read in-feed; the consumption model is different from every other slide
role we spec, and it deserves its own system rather than a cap override on an existing one.

**Word-allowance rationale.** Anchor the ceiling on the *higher-fidelity* sub-format (60-prompts,
~230 words/slide, native-quality per `CATALOG.md` §2B) rather than the 540-word outlier (36-prompts,
whitelabeled in 2 of 3 samples, lower design fidelity). At this system's own type floor (below), a
1080×1350 body rect fits ~10 short numbered entries before overflow — derivation:

- Usable body rect: `x:[0.08,0.92]` (84% w = 907px) × `y:[0.13,0.87]` (74% h = 999px).
- Target: 9-10 entries, ~2 lines wrap each, matching the 60-prompts sub-format's per-entry density.
- At `type_scale: 0.0185` (~25px), line-height 1.2, 10 rows × ~2.2 avg lines × 30px ≈ 660px — fits with
  room for row gaps inside the 999px rect.
- ~60-65 chars/line at 907px width ⇒ ~20-22 words/entry (2-line wrap) × 10 entries ≈ 200-220 words.
- **`value_sheet_max_words: 220`** — one notch below the 230-word reference average, same -10%-for-safety
  rounding logic `STYLE_SYSTEMS_SPEC.md` §2.6 already uses for `prompt_quote_max_words`.
- **`type_floor: 0.0185`** (1.85% of canvas height) — genuinely new: below every existing system's floor
  (§2.6's own stated 2.4% "one notch below" reference). **This needs its own Czech-glyph legibility
  re-verification before shipping** — `assets/fonts/README.md`'s existing pass was rendered at
  `fontsize=44` in a 500px test frame (≈8.8% of that frame), nowhere near this proposed floor; do not
  assume the existing PASS carries over to 1.85%-of-height text.
- Fully exempt from `slide_body_max_words` the same way `ig_prompt_sheet`'s `prompt_quote` is exempt
  (`RENDER_CONTRACT_SPEC.md:325`) — but with this system's own derived ceiling, never unbounded.

**Grid recipe.** Category kicker (top-left, small) + "N/10" progress counter (top-right) + one
multi-line `body` zone holding all numbered entries (same "checklist-as-one-zone" convention every
existing system already uses for multi-row content — no new `layout.py` capability required) + an
optional non-text `footer_zone` progress-marker strip for multi-slide series continuity.

**Ground.** Dark-terminal (`#1E1B2E`, reusing `ig_prompt_sheet`'s existing terminal palette) rather than
paper-cream — this differentiates the system from the five cream/gradient-branded systems already
specified, and is independently validated by the reference's own dark-card cheat-sheet sub-format.
**Explicitly do NOT** copy the reference's literal Claude.ai chat-composer mockup ("Opus 4.6 Extended"
toolbar, send button) seen on the whitelabeled `60-claude-prompts_cover.jpg` — that is exactly the
fake-third-party-UI pattern Hard DON'T 5.4 already forbids, doubly so here since it impersonates a real
product's actual interface.

**Zones (machine-readable, same shape as `STYLE_SYSTEMS_SPEC.md` §2, canvas 1080×1350):**

```yaml
ig_value_sheet:
  display_name: "Value Sheet"
  topic_tag: prompt_dump_reference        # NEW tag — not covered by the existing three-topic classifier (§4.1); flagged as a follow-up, not resolved by this document
  destination: instagram_feed
  register: editorial
  archetype: dense-spec-card              # existing key, style_guide.yaml:123 — "Dark branded card restating the post's bullets as designed columns/panels with numbers and arrows." Confirmed strong match, no new archetype needed.
  generation_mode: designed_card
  ground_recipe: dark_terminal            # every slot goes dark — contrast with ig_prompt_sheet, where only prompt_quote is dark
  value_sheet_max_words: 220              # derived above
  type_floor: 0.0185                      # derived above — needs its own glyph-legibility re-verification, see above
  palette:
    ground: "#1E1B2E"
    kicker_ink: "#00A39A"
    body_ink: "#EDEAE3"
    rule: "#302B87"
  slots:
    cover:
      ground_source: programmatic         # never diffusion — a numbered-promise hook is pure typeset text; keeps this system in the fully-programmatic club (zero diffusion surface, matching ig_prompt_sheet)
      text_render_mode: composited
      zones:
        - {name: kicker, rect_pct: [0.12, 0.20, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: center, max_lines: 1, color: "#00A39A"}
        - {name: headline, rect_pct: [0.10, 0.30, 0.80, 0.22], type_scale: 0.09, weight: Bold, align: center, max_lines: 2, color: "#FFFFFF"}
        - {name: subtext, rect_pct: [0.14, 0.56, 0.72, 0.06], type_scale: 0.026, weight: Regular, align: center, max_lines: 1, color: "#FFFFFF"}
    body:                                  # slides 2 and 4 — the dense category card; prompt_quote (slide 3) reuses this identical shape as a third dense beat, same convention as ig_annotated_proof/ig_stat_slab §2.2/§2.4
      ground_source: programmatic
      text_render_mode: composited
      footer_zone: [0.08, 0.90, 0.84, 0.04]   # optional progress-marker strip — non-text-primary decorative row, drawn programmatically, not a `zones:` entry, same convention as decorative_zone
      zones:
        - {name: kicker, rect_pct: [0.08, 0.06, 0.60, 0.05], type_scale: 0.022, weight: SemiBold, align: left, max_lines: 1, color: "#00A39A"}
        - {name: counter, rect_pct: [0.72, 0.06, 0.20, 0.05], type_scale: 0.020, weight: Regular, align: right, max_lines: 1, color: "#FFFFFF"}
        - {name: body, rect_pct: [0.08, 0.13, 0.84, 0.74], type_scale: 0.0185, weight: Regular, align: left, max_lines: 20, color: "#EDEAE3"}
    end_card:
      ground_source: programmatic
      text_render_mode: composited
      zones:
        - {name: cta, rect_pct: [0.12, 0.40, 0.76, 0.10], type_scale: 0.045, weight: SemiBold, align: center, max_lines: 2, color: "#FFFFFF"}
        - {name: subtext, rect_pct: [0.12, 0.52, 0.76, 0.08], type_scale: 0.028, weight: Regular, align: center, max_lines: 2, color: "#FFFFFF"}
```

Fully programmatic, zero diffusion surface — matches the `li_signal_card` / `li_statement_hero` /
`li_editorial_brief` / `ig_prompt_sheet` "fully programmatic" club (§2.7); once shipped, 5 of 7 systems
carry zero image-generation calls.

### C.2 Serif font acquisition — pick

**Recommendation: Playfair Display (SIL OFL 1.1).** It is the closest visual match to the reference's
signature move — the Bold Italic, high-contrast, ball-terminal display headline used identically across
every native cover and step headline in the set (§A.2) — and since our spec uses the serif *only* for
headline-scale text (6-11% of canvas height, never body-scale under the current spec), Playfair Display's
known weakness at small sizes (its high stroke contrast gets spindly below ~14px) is a non-issue for that
use case. It ships Regular/Italic/Bold/Black cuts across Roman and Italic — enough to build the
two-weight-within-one-headline device (§A.2) natively (Black Italic hero phrase + Regular Italic or
Roman qualifier, no synthetic bolding). Per Google Fonts' published language-coverage list, Playfair
Display supports Latin Extended, which includes the Czech diacritic set — **verify against the exact
`assets/fonts/README.md` corpus** (`ěščřžýáíéúůďťňó / ĚŠČŘŽÝÁÍÉÚŮĎŤŇÓ`, `Kč`) before shipping, the same
glyph-verification protocol already gates `NotoSans-Variable.ttf`; do not assume coverage without
re-running that exact test on the acquired file.

If §B's recommended body-family change (serif Roman body text, not sans) is adopted, **Playfair Display
alone is the wrong body font** (too high-contrast/spindly at ~2.6-3% canvas height). Pair it with **Lora**
(also SIL OFL, also full Italic + Bold Italic, moderate contrast, strong small-size legibility, broad
Latin Extended/Czech coverage, widely used for CE-language body text) as the body companion — same
transitional-serif family feel, calmer contrast, does not clash. This is a two-family serif system
(Playfair Display display / Lora body), not a compromise pick — it mirrors how the reference itself
likely uses a display cut for headlines and a separate, calmer text-serif for paragraphs (the two show
visibly different contrast levels in the source images, §A.2). Runner-up if a single, quieter family is
preferred everywhere: **EB Garamond** (also OFL, also broad diacritic coverage) — more "calm, high-trust"
per our own `visual_registers.editorial.mood` (`style_guide.yaml:167`) but noticeably less dramatic than
the reference's actual headline treatment.

### C.3 The accent-color question — coral vs. brand teal/indigo

**Recommendation: do not adopt coral as a generic brand accent. Keep indigo `#302B87` / teal `#00A39A`
as the only brand accent pair.** The coral 3D asterisk/starburst *is* Anthropic's Claude product mark
(the literal app-icon glyph, reproduced faithfully on `start-a-business_s1`, and a hand-inked variant of
the same mark on two other native covers). Two distinct risk tiers:

1. **Using the real Claude logo/icon to nominatively depict the actual product** (e.g., a slide literally
   about "how to use Claude") is the same class of use our own `li_signal_card` already governs for
   third-party tool logos — composited from a real static asset, never diffused/redrawn, never distorted
   — acceptable *only* under that same governance, and only when the content genuinely names Claude as
   the tool in question.
2. **Inventing a generic coral-asterisk/starburst decorative motif independent of actually depicting
   Claude** — i.e., adopting "a coral 3D sunburst mark" as *our own* recurring brand device the way this
   creator does — is the move to avoid. It reads as an unauthorized redraw of another company's
   distinctive mark and color, and risks implying affiliation/endorsement HypeDigitaly doesn't have. This
   is a real trademark-adjacent concern, not a style preference, and should be named as such to whoever
   owns brand risk.

Note this does **not** forbid abstract bursts/asterisks as a category — `li_editorial_brief`'s existing
`decorative_zone` ("a single deliberate line/shape, teal," never pictorial per §5.2's row-of-icons ban)
already accommodates a single abstract geometric mark in the brand's own teal, which is a fine, distinct
motif on its own terms. The line is: teal/indigo abstract marks = ours to use freely; a coral
asterisk/sunburst specifically = reserved for actual, composited Claude-product references only.

### C.4 Everything else the reference does that our spec forbids or misses

- **Comment-gate CTA on the hook slide** ("Comment '60' and I'll DM you all 60 prompts for free," on the
  whitelabeled `60-claude-prompts_cover.jpg`). This implies a first-person creator persona ("I'll DM
  you") — directly conflicts with the locked faceless/institutional-voice decision
  (`RENDER_CONTRACT_SPEC.md:62-68`). **Correctly already forbidden — flagged here only as confirmation
  the reference contains a pattern we should explicitly NOT adopt, not as something missing from spec.**
- **Fake Claude.ai chat-composer UI mockup** (same cover: "Opus 4.6 Extended" toolbar + send button). This
  is precisely Hard DON'T 5.4's "no fake/invented dashboards or third-party UI" — good real-world
  confirmation that DON'T is well-justified, and a second, independent reason (beyond §C.3) not to
  imitate this specific cover's device, since it's also a whitelabeled asset, not the creator's own
  native system (§ scoping note).
- **No CTA on the best-performing carousel's closer at all** (§A.5) — our `end_card` slot mandates a
  follow/save CTA on every one of the six systems. Propose the `end_card_override: artifact_close` field
  already listed under §B's `ig_prompt_sheet`/`li_editorial_brief` deltas, extended to `ig_value_sheet`
  too: an optional per-asset choice (not a system default) to end on the densest artifact instead of a
  CTA, for assets where a content calendar doesn't need that particular save to also carry a follow ask.
- **Left margin ≈8%**, tighter than our universal 12% safe zone (§A.5) — worth a note, not necessarily a
  change: our wider margin is a deliberate cross-format safe-zone choice (`DEFAULT_MARGIN_PERCENT`,
  `promptcraft.py:104`) and shouldn't be loosened just to chase one reference's tighter rag; flagged for
  awareness only.
- **Hook slides never use diffusion at all in the native set** — every cover is flat paper/dark ground +
  typeset text. This validates `ig_prompt_sheet`'s firmed-composited-cover default (§2.6) as the right
  call for the editorial register generally, and supports §B's `max_spans` relaxation proposal for
  composited covers specifically.

---

## D. Verdict

Adopt this reference **heavily** for the `editorial` register specifically (`li_editorial_brief` +
`ig_prompt_sheet`, and the new `ig_value_sheet`) — it is, in effect, a live, save-rate-proven instance of
what our own `visual_registers.editorial` prose already described sight-unseen, and it closes real,
previously-unverified gaps (grain treatment, icon language, artifact-card construction, the
two-weight-headline device). Adopt it **selectively everywhere else**: reject its comment-gate CTA
persona pattern and its fake-product-UI mockup outright (both already correctly forbidden by locked
decisions), and treat its coral Claude-mark usage as a governed, nominative-only exception rather than a
brand accent to imitate. The five highest-impact changes, ranked:

1. **Acquire Playfair Display (+ Lora as body companion)** and change `li_editorial_brief`/
   `ig_prompt_sheet`'s `body_family` from Montserrat/sans to the acquired serif's Roman cut — the single
   biggest fidelity unlock; the "editorial" register cannot look like its own name until this ships.
2. **Ship `ig_value_sheet`** (dense-spec-card archetype, `value_sheet_max_words: 220`, `type_floor: 0.0185`
   with re-verified Czech glyph legibility, dark-terminal ground, zero diffusion surface) — this alone
   unlocks an entire winning content class our 24-word cap makes structurally impossible today.
3. **Add the `inline_artifact_card` + optional `icon_zone` to `body` slots, and formalize
   `checkbox_style` (outline default / filled-circle "done" variant)** — closes the density/craft gap
   between our current "one checklist OR one quote" body and the reference's richer "icon + paragraph +
   checklist + card" body, with no new system required.
4. **Lock the accent-color governance**: teal/indigo only as generic brand accent; coral/Claude-mark
   usage permitted only as a real, composited, nominative logo reference under the same rule
   `li_signal_card` already applies to third-party logos — never as an invented decorative motif.
5. **Relax `max_spans` for `text_render_mode: composited` covers** (currently inherits the diffusion-only
   2-span cap with no diffusion risk to justify it) — lets a fully-typeset editorial hook carry a
   kicker+headline+qualifier the way the reference's best covers do, while explicitly rejecting the two
   reference patterns that shouldn't come along for the ride (comment-gate persona CTA, fake product-UI
   mockup).
