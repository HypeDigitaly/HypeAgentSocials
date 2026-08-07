# DESIGN_EXPANSION.md — new photoreal/editorial style systems (visual-format reference, W8-11)

*Written 2026-08-07. Source images: all files in this directory (viewed directly — hex values below are
visual estimates from those pixels, treat as "close enough to design against," re-sample before locking
a token). Source data: `CATALOG.md` in this directory (Virlo niche-monitor research, 1,509 video rows +
380 slideshow rows, weighted-virality ranked). Companion docs read in full: `../aisimplified23/
DESIGN_DECONSTRUCTION.md` (serif/paper editorial reference — establishes the zone-format convention and
the precedent for shipping a new system, `ig_value_sheet`, alongside the original six) and
`../../STYLE_SYSTEMS_SPEC.md` §0-§8 (canvas conventions, the six live systems, Hard DON'Ts, persona
policy, diffusion-surface census, resolver algorithm). Every convention below — `rect_pct` basis, zone
naming, `ground_source`/`text_render_mode` vocabulary, register/archetype/generation_mode axes — is used
in the exact shape those two documents already fixed; nothing here invents a new mechanism, only new
`style_systems[*]` entries (and, where noted, new `GENERATION_MODES` keys reusing the register machinery
`promptcraft.py` already ships for the TikTok Phase-8 rotation).

**Operator context (the reversal this document executes on).** An earlier restriction against
photorealistic AI-generated scenes is REVERSED: photoreal is now a first-class, governed post format,
explicitly requested to sit alongside — not replace — the six designed "Canva-like" card systems, and
the brief explicitly asks for MORE visual variety than a single card register can produce. Nothing below
relaxes the engine's hard text-integrity, no-fake-UI, or no-invented-persona rules (§0 below restates
them as constraints every new system must satisfy); it only adds new *ground* registers those rules can
be applied to.

---

## 0. Engine constraints restated (binding on every system proposed below)

1. **Text integrity.** Dense/exact text is ALWAYS `text_render_mode: composited` (Pillow, real fonts,
   Czech diacritics). Diffusion may render text ONLY as short in-scene spans, `≤2 spans × ≤6 words`, and
   only on `cover`/hook-equivalent slots (`RENDER_CONTRACT_SPEC.md`'s `diffusion_text_max_spans`/
   `diffusion_text_max_words_per_span`). Diffusion CAN generate a full photoreal scene ground with a
   **reserved text zone** (`COMPOSITING_SPEC.md` §"Case (b)", `grounds.request_reserved_zone_prompt_
   fragment` + `check_ground_safe_zone`) onto which the compositor lays exact, gated text after the image
   downloads — this is the mechanism every photoreal system below actually uses for its caption.
2. **No fake/invented UI.** Real captured screenshots or none (`STYLE_SYSTEMS_SPEC.md` §5.4). None of the
   systems below use a screenshot inset; flagged explicitly per-system where a reference exemplar had one
   and it's being deliberately dropped.
3. **No invented humans presented as real people.** Faceless institutional brand voice
   (`RENDER_CONTRACT_SPEC.md`'s `PersonaPolicy`, `mode: "institutional"`). Photoreal scenes may show
   environments, objects, hands, silhouettes, reflections, shadows — never an identifiable fake persona
   *presented as the speaker*. This is the single largest edit every reference class below needs, since
   two of the three photoreal exemplar classes (`aitools_guy`, most `photoreal-caption_*`) are literally
   UGC selfie/lifestyle content with a real creator's face in frame. §A.1/§A.2 name the edit precisely.
4. **Brand.** Indigo `#302B87`, teal `#00A39A`, cream `#F2F0EC`, dark `#1E1B2E`. Serif: Playfair Display
   (display) + Lora (body) — per `DESIGN_DECONSTRUCTION.md` §C.2, not yet acquired in-repo; fallback
   `NotoSans-Variable.ttf` as every existing system already states. Sans: Montserrat (fallback: same).
5. **Canvas.** LinkedIn `1920×1080` (16:9, single `hero` slot), Instagram `1080×1350` (4:5, 5-slot
   carousel: `cover, body, prompt_quote, body, end_card`). `margin_percent = 12` safe zone, all systems,
   no exceptions. `rect_pct` = fraction of the FULL canvas, per `STYLE_SYSTEMS_SPEC.md` §2's own
   convention.

---

## A. Deconstruction of each new reference class

### A.1 `aitools_guy` photoreal-lifestyle panels (TOP priority — 909K views, 6.6% save rate, +42.53 weighted)

**Files:** `aitools-guy_01_panel0.webp` (full-res panel), `aitools-guy_01_thumb.jpg`, `aitools-guy_02_
thumb.jpg`.

**Anatomy.** A single full-bleed photoreal photograph *is* the entire canvas — no card, no border, no
color block. The photograph itself is deliberately unremarkable: a sunlit minimalist loft (exposed
concrete floor, cream sofa, moving boxes still stacked, an iMac on a bare wood table) or a Dubai
penthouse with a floor-to-ceiling skyline view. Nothing in the frame is staged like an ad — it reads like
someone's actual apartment mid-move, shot on a real camera (visible rig: tripod + camera clamped to the
monitor, cast shadow of the subject on the wall). **Composition:** subject occupies roughly the right
third to right half of the frame, small relative to the room (never a tight portrait crop) — the
*environment*, not the person, is the visual subject. Caption sits in the **top-left quadrant**, roughly
y:22–35% of a 1792×2400 (≈4:5.36, close enough to our 4:5) canvas, left-aligned, tight against nothing
(floats on open wall/sky), two lines: a heavier first line + lighter continuation, e.g. "5 apps I use to
run my" / "entire business." — plain white, bold-but-not-heavy sans (visually close to Montserrat
SemiBold/Bold, not a display face), soft/negligible drop shadow, no card, no color block behind it. No
handle, no logo, no CTA on the cover panel. Subsequent panels (per `CATALOG.md` §2, same template
re-run) keep the same recipe: one tool per panel, 2–4 lines of plain white caption, different lifestyle
photo per panel (loft → different rooms/angles).

**What the caption layer does.** It is the ONLY graphic-design element in the entire asset. It never
competes with the photo for attention (small, top-corner, high-legibility color choice against a plain
sky/wall region — i.e., the creator instinctively picked a **safe zone** the way our reserved-zone
mechanism formalizes). It reads exactly like a native phone-camera slideshow caption, not a marketing
overlay.

**Native vs. ad.** Feels native because: (1) the photo is not "designed" at all — no vignette, no color
grade, no gradient, nothing that signals "this is an ad"; (2) the caption is minimal-effort, plain-white,
no pill/card/highlight treatment; (3) the environment itself carries an aspirational-but-plausible signal
(a real loft, a real skyline) rather than a stock-photo gloss; (4) zero CTA, zero urgency language, zero
benefit-checklist grammar anywhere in the visible panel.

**Faceless adaptation (constraint 3, §0).** The reference literally is a person's UGC photo-diary. Our
adaptation keeps the room/desk/environment (the actual persuasive content — "look at this real, plausible
workspace") and removes the identifiable human: hands on a keyboard, a monitor glow, a chair pulled out,
a coffee cup and notebook, a shadow on the wall — never a face, never a body positioned as "the speaker."
This is a **strengthening** edit, not a compromise: `CATALOG.md` §4 insight 2 already notes this is "the
strongest faceless class we can actually generate" — our version removes the one non-faceless element the
original happens to have and keeps everything that actually won (real-feeling minimalist environment +
plain caption).

### A.2 AI-photoreal cinematic scene + caption-overlay class (`_classify_ig_aimaster.jpg` + `photoreal-caption_01..03`, #1-weighted item in the whole corpus at 2.17M views / ws 51.1)

**Files:** `_classify_ig_aimaster.jpg` (@aimaster.labs, the #1 item), `photoreal-caption_01.jpg`
(@rizq.matters, desert listicle), `photoreal-caption_02.jpg` / `_03.jpg` (UGC desk scenes, faces
present — excluded as direct templates, kept for the caption-overlay technique only).

**Two distinct sub-registers inside this one catalog class — worth separating explicitly:**

1. **Dramatic AI-illustrated scene (`_classify_ig_aimaster.jpg`).** Not photoreal in the literal sense —
   it's a stylized, saturated digital illustration/render: a man clutching his head in the foreground
   (back to camera, faceless from this angle — useful precedent), flanked by glowing robot arms, a
   burning-orange city skyline, lightning, floating papers, "FIRED!" signage. Palette: deep indigo/navy
   night sky (~`#0D1240`–`#1A1550`), hot orange/red rim-light and lightning (~`#FF6A1A`–`#FFB347`),
   electric blue robot-arm accents (~`#2E9CFF`). Caption "YOU WILL BE JOBLESS!" is baked in at the very
   top, bold condensed sans, blue-to-white gradient fill, tight to the top edge, cropped by the frame —
   reads as diffusion-rendered in-scene text (short, ≤4 words, exactly within our diffusion-text span
   cap). This is a **hype-register** scene (dramatic lighting, high saturation, emotional stakes), not
   editorial — instructive but NOT the register we adapt for B2B (see below).
2. **Genuine photoreal scene + plain caption (`photoreal-caption_01.jpg`, the desert/camel-caravan
   image).** A real-feeling night desert photograph — dark navy sky with visible stars, warm firelit
   camel caravan silhouettes on a dune ridge, small lantern glow-points along the trail. Caption sits
   dead-center, y≈27–36% of frame, three centered lines, plain white sans (no drop-shadow card, minimal
   soft shadow only), text is the ONLY graphic element — the photograph itself needed zero UI/design
   treatment because it already reads as intentional, atmospheric content.

**What the caption layer does.** In both sub-registers, caption text sits in a pre-composed **negative
space** the photograph (or illustration) was shot/generated to leave open — sky, wall, dark negative
space between elements — never on top of visual complexity. This is the exact reserved-zone mechanism
§0.1 describes, just executed by a human photographer's/generator's instinct rather than a declared rect.

**B2B adaptation.** Reject the literal "drama + shock stat" content (fear-bait "YOU WILL BE JOBLESS",
invented robot-apocalypse imagery) — it's off-brand for an institutional B2B voice and courts the same
unverifiable-claim problem `RENDER_CONTRACT_SPEC.md`'s claim gate already exists to block. Keep the
*visual grammar*: high-production-value, moody/dramatic (not garish) office/tech/workspace environments —
a glass-walled conference room at dusk, a server-room corridor with cool blue practicals, a desk lit by a
single monitor glow at night, a city skyline through an office window — lit and composed with real
cinematographic intent (rim light, practicals, negative space), paired with a short, bold, factual/
provocative-but-defensible hook line composited into the reserved zone. No robots, no fake drama personas,
no invented "AI will replace you" claims — the drama comes from lighting and composition, not from
fabricated stakes.

### A.3 `10xoperator` editorial-grotesque carousel (`10xoperator_ig-carousel_screenshot.png`, operator-supplied)

**Full anatomy, deconstructed from the screenshot (slide 1 of the carousel "How to build an AI agency
that lands real clients"):**

- **Ground:** off-white/warm-paper (`~#F3F1E9`) with a **faint pale-gray grid** printed across the entire
  canvas (thin ruled lines, both axes, ~40–50px pitch at carousel scale — a "graph paper"/notebook
  texture, NOT the speck-grain the aisimplified23 reference uses; a distinct, structured-paper subtype).
  Zero photographic ground on the cover/body slides; the grid is 100% programmatic.
- **Header furniture:** top row, two small-caps grotesque labels — brand wordmark left ("10XOPERATOR"),
  a right-aligned running theme label ("STAYING AHEAD WITH AI") — separated by a full-width thin black
  hairline rule directly beneath. Reads as a printed-zine masthead, not a social template.
- **Kicker pill:** black-outline (no fill), rounded-rect pill, small-caps grotesque, e.g. "AI AGENCY
  BLUEPRINT" — sits above the headline, left-aligned.
- **Headline:** very large (~9–11% of canvas height per line), heavy grotesque sans (visually close to a
  black-weight Helvetica Now/Neue Haas Grotesk cut — tight tracking, no serif, no italic), set in 3 short
  lines, **one phrase in the line recolored to a saturated accent red** ("that lands", mid-sentence) while
  the rest stays near-black — this is the system's single most distinctive device: *typographic* emphasis
  via one color-swapped phrase inside an otherwise monochrome headline, never bold/italic/underline for
  emphasis (contrast with aisimplified23's all-typographic-no-color emphasis logic, §DESIGN_
  DECONSTRUCTION.md A.2 — this system does the opposite: color IS the emphasis channel).
- **Small photoreal inset:** a rounded-square (~8–10% corner radius) photograph — desk flat-lay, rolled
  blueprint + drafting tools — positioned top-right, roughly 30% of canvas width, with a small
  rotated/marker-script red label ("3-step plan") floating just above-right of it like a sticky note
  annotation. This is the ONE photographic surface on an otherwise 100%-typographic canvas — small,
  supporting, never the dominant element.
- **Yellow highlighter bar:** a solid, saturated yellow (`~#F5D833`) rectangle, black bold text set
  directly on top (no card border, no shadow — reads exactly like a highlighter dragged over a printed
  page), holding one short restated-value sentence ("A beginner-friendly 3-step roadmap."). Distinct from
  a "callout box" — it's flush/full-bleed-within-margin, sharp corners, pure highlighter-marker metaphor.
- **Body copy:** a two-sentence line beneath the highlighter bar, mixed-weight (regular lead-in + one bold
  clause), grotesque sans, left-aligned, generous line-height.
- **Micro-caption:** small gray italic line near the bottom ("Framework for creators / freelancers
  stepping into AI services...") — a footnote-register aside, smallest type on the slide.
- **Footer furniture:** thin hairline rule, then a footer row mirroring the header: black-outline pill
  button bottom-left ("SWIPE »»»"), solid yellow circular page-number badge bottom-right ("1").

**Why it feels native, not ad.** Zero gradient, zero drop shadow beyond the barest lift on the inset photo,
zero benefit-checklist/pill-icon grammar, zero CTA banner, zero 3D device mockup. The grid-paper ground +
grotesque type + red/yellow accent reads as an editorial/zine or Bauhaus-poster register — a *content
format* (carousel-as-mini-magazine-spread) rather than a *promotional* format. The single photo is
support material (evidence of "a real plan exists"), not a hero product shot.

**Accent-color mapping to our palette.** The reference's red-for-emphasis + yellow-for-highlight pairing
is a strong, proven two-accent system but neither hex is in our brand palette. Recommend: **keep the
highlighter-bar role assigned to a warm accent, not brand teal** — teal-on-cream already carries a
*different* semantic in our library (checkbox/pill accent in `ig_prompt_sheet`/`ig_annotated_proof`,
§6's register-keyed leak table) and reusing it here would blur that signal. Two options, ranked:
1. **Recommended:** introduce one **new, single-purpose accent** — a warm ochre/amber (`#E8A63B`-family,
   sits comfortably adjacent to teal on the color wheel without reading as "brand teal gone wrong") for
   the highlighter bar, and use **brand indigo `#302B87`** (not red) for the one-phrase headline
   emphasis — indigo is saturated enough to read as "emphasis" against near-black body ink and requires
   zero new hex approval. This keeps the system on-brand with exactly one net-new token.
2. **Fallback (zero new tokens):** brand teal `#00A39A` for the highlighter bar (dark ink on teal is
   legible; a genuine departure from teal's current pill-only role, flagged as a deliberate register
   expansion, not an oversight) + indigo for the headline emphasis phrase. Zero new hex, but spends
   teal's "distinct accent" equity across two systems.
Recommend option 1 to the brand owner as a one-line follow-up decision; §B.3 below specs the system with
option 1 as the default, option 2 noted as the zero-new-token fallback.

### A.4 `launch.automation` product-render ad (`launch-automation_06_website-offer.jpg`) — and why it underperforms

**Anatomy.** Full-bleed radial purple/violet gradient ground (light lavender core fading to deep violet
edges) with a faint dotted-grid overlay and two glowing arc/ring lines — the exact "abstract
gradient-mesh / generic AI-startup-website iridescent background" our own `STYLE_SYSTEMS_SPEC.md` §5.5
Hard DON'T already names and forbids. Condensed heavy-weight sans headline, top phrase flat black
("LEAD GENERATING"), bottom phrase a vertical purple-to-violet gradient fill ("INSURANCE AGENT
WEBSITES") with a swash underline. Below: an "AS LOW AS $33/mo" price callout in oversized digits. Three
white rounded-rect **benefit pills**, each with a filled purple circular checkmark icon — a clip-art-icon
row in spirit (§5.2 Hard DON'T's "checkmark-in-circle used as decoration" is named verbatim). A
3D-perspective laptop mockup renders a **fake, fully invented insurance-broker website** inside its
screen — nav bar, a stock-photo headshot of "John Nightingale, Licensed Insurance Broker," star ratings,
a "Book a Free Call" button — i.e., simultaneously a fake invented UI (§5.4) AND an invented human
presented as a real person (our persona policy, §0.3) *inside* the invented UI, doubling the violation.
Bottom: a dark-purple CTA banner, stopwatch icon, "ORDER IN 5 MINUTES — NO CARD NEEDED — SEE IT FIRST!"

**Why it underperforms (per `CATALOG.md` §1/§4).** 1,907 views, weighted score **-9.02** — the single
worst-performing item in the entire studied set alongside the designed typography title card
(`target_ig-reel_riseinstitute.jpg`, also negative). `CATALOG.md` §4 insight 3 states it plainly:
"Designed cards read as ads; photoreal reads as content." Every element on this card is drawn from
*direct-response landing-page grammar* (radial glow hero, gradient headline, benefit-pill checklist, 3D
device mockup, urgency CTA banner, price-anchor callout) transplanted unmodified onto a social feed — it
signals "advertisement" before a viewer reads a single word, triggering the same scroll-past reflex as a
banner ad. Contrast directly with A.1: the winning template has *zero* of these grammar elements — no
gradient, no benefit pills, no device mockup, no urgency banner, no price callout — it looks like content
because it borrows nothing from ad design at all. (Note: the account's 41% like-rate on this specific post
suggests possible paid/boosted distribution per `CATALOG.md` §1 — even *reach*-assisted, the organic
engagement signal is still the worst in the corpus, reinforcing rather than undercutting the verdict.)

**Verdict for our library:** do not build this as a style system (see §B.4 for the one-paragraph
judgment) — every one of its defining moves is something our existing Hard DON'Ts (§5.1–§5.5) already
forbid, or something the persona policy forbids, or something the data itself says loses. It is the
single cleanest real-world confirmation that our existing guardrails are pointed at the right target.

### A.5 Motion-graphics / flowchart class (`motion-graphics_01.jpg`, `target_yt-short_strucxal.jpg`) — video, out of scope, recorded for W8-12

**Anatomy (from `target_yt-short_strucxal.jpg`, the clean exemplar — `motion-graphics_01.jpg` is
actually a screen-recording+talking-head thumbnail per re-inspection, kept in the folder as a labeling
artifact, not a second flowchart example).** Pure white ground, centered brand mark (an orange 12-spoke
starburst — visually close to, but not, the Claude asterisk mark; a generic "AI/spark" glyph in this
context), a plain sans headline naming the system ("Claude AI Sales Research System"), then a genuine
node-and-arrow flowchart: colored category header bars (teal "Data Sources & Ingesting," purple
"Research Director," etc.), small icon-labeled process boxes, directional arrows, a bottom row of
real tool-logo strip (HubSpot, LinkedIn, Google, Yelp, Indeed) — i.e., an actual information-design
diagram, not a decorative graphic. `CATALOG.md` §4's own classification confirms this is
`animation_motion_graphics` format — **it is a still frame of an animated explainer video**, not a
static image asset; `bg: solid_color`, `fg: illustrated_subject`, captions on.

**Why out of scope now, recorded for later.** `w8-11-plan-decisions.md` already locks "tiktok
kept-but-disabled" and video generation is not this workstream's deliverable — this class only exists as
a *rendered video frame*, and our engine's image pipeline (Pillow compositing + Nano Banana 2 stills) has
no motion/animation output today. It is genuinely a strong, high-legibility B2B format (a real flowchart
explaining a real system beats both photoreal drama and a designed stat card for "explain how this
actually works" content) — flagged explicitly as a **W8-12 candidate**: a static single-frame "systems
diagram" style system (white ground, colored category bars, icon-labeled process nodes, real tool-logo
strip) is directly buildable with our EXISTING programmatic-card machinery (no diffusion, no video) and
would be a near-zero-marginal-cost seventh/eighth system — but it is a distinct enough proposal (new node/
arrow layout primitive, not a zone-of-text primitive) that it deserves its own short spec rather than
being folded into this document's four B proposals.

---

## B. Proposed NEW style systems

All four below bind `register` per-slot as already established (`editorial` for the grid-paper system,
`photographic_ugc` for the three photoreal systems — reusing the register `style_guide.yaml` already
defines and `promptcraft.py`'s Phase-8 TikTok modes already exercise, now formalized as named,
IG/LinkedIn-eligible `style_systems[*]` entries with full zone contracts, per the same "propose a new
entry, same shape as existing ones" pattern `DESIGN_DECONSTRUCTION.md` §C.1 used for `ig_value_sheet`).

**Integration note, flagged not resolved by this document (same honesty standard as `DESIGN_
DECONSTRUCTION.md` §C.1's own `prompt_dump_reference` flag):** `STYLE_SYSTEMS_SPEC.md` §4.1's resolver
binds `style_system` off a fixed 3-topic regex classifier (`lead_gen_workflow` / `sales_agent_stat` /
`ops_assistant_founder`). None of the four systems below are topic-specific the way those three are —
they are general-purpose *format* choices applicable to almost any topic in this theme. Two integration
paths, either workable, decision deferred to whoever owns `RENDER_CONTRACT_SPEC.md` §2's resolver:
(a) add new `topic_tag` values as the classifier's own follow-up (e.g. `tool_stack_howto`,
`scene_hook_generic`, `agency_playbook_howto`) so these systems get pinned deterministically like the
existing six; or (b) promote them into the Phase-8 dynamic-inspiration rotation
(`_candidate_modes_from_visual_profile`, `promptcraft.py:563-580`) as new `GENERATION_MODES` entries,
extending that rotation's `photographic_ugc`/`editorial` register modes — already built and TikTok-tested
— to the `instagram_feed`/`linkedin` destinations they currently don't serve. Path (b) is less work
(reuses the exact `ModeSpec` machinery and even some near-identical `composition_directive` text already
in `promptcraft.py:456-522`, see the per-system notes below) and is the recommended default; path (a) is
listed because it's how the rest of this document's sibling systems work and an executor may prefer
consistency over reuse.

### B.1 `ig_lifestyle_stack` — the aitools_guy photoreal lifestyle listicle (5-slot carousel, IG)

**Intent:** the proven 6.6%-save faceless winner (§A.1). One photoreal minimalist environment per slide,
one tool/step named per slide, near-zero graphic design — the environment does the work, the caption is
minimal furniture.

**Keys:** `register: photographic_ugc` (existing key) · `archetype: aspirational-lifestyle-scene`
(existing key, `style_guide.yaml:144`, already bound to `aspirational_lifestyle_scene` — reused, not a
new archetype) · `generation_mode: aspirational_lifestyle_scene` **reused where its directive already
matches** ("luxury, aspirational real-world environment... does the persuasion visually... minimal
on-image text: at most one short line" — `promptcraft.py:480-487`), **amended** below for the
faceless/reserved-zone/multi-line specifics this system needs that the existing mode text doesn't state.
Destination `instagram_feed`, carousel, 5 slots.

**Amended `composition_directive` (proposed diff against the existing `aspirational_lifestyle_scene`
`ModeSpec`, `promptcraft.py:480-487`):**
```
"A real-feeling, minimalist, aspirational-but-plausible workspace/environment (loft office, quiet
apartment desk corner, city-view workspace) shot with natural window light, phone-camera-real framing
(not a studio product shot) -- the environment itself is the message. NEVER depict an identifiable
person, a face, or a body positioned as the frame's subject; hands-on-keyboard, a monitor glow, a
chair, a coffee cup, a shadow are all permitted, a face or full figure is not (persona policy). Reserve
a plain, low-detail region in the upper-left quadrant of the frame for a two-line caption to be added
after generation -- keep that region free of clutter, high-contrast edges, or busy texture."
```

**Zones (canvas 1080×1350):**
```yaml
ig_lifestyle_stack:
  display_name: "Lifestyle Stack"
  topic_tag: tool_stack_howto              # NEW — not in the existing 3-tag classifier, see integration note above
  destination: instagram_feed
  register: photographic_ugc
  archetype: aspirational-lifestyle-scene
  generation_mode: aspirational_lifestyle_scene   # amended directive, see above
  ground_recipe: photoreal_environment
  palette:
    caption_ink: "#FFFFFF"
    caption_ink_alt: "#1E1B2E"    # optional dark alternate when the reserved zone lands on a light sky/wall
  type:
    caption_family: "Montserrat SemiBold"
    caption_fallback: "assets/fonts/NotoSans-Variable.ttf@630"
  slots:
    cover:
      ground_source: diffusion
      text_render_mode: composited        # composited caption over a diffused photo ground — COMPOSITING_SPEC.md Case (b)
      zones:
        - {name: headline, rect_pct: [0.10, 0.20, 0.60, 0.14], type_scale: 0.045, weight: SemiBold, align: left, max_lines: 2, color: "#FFFFFF"}
    body:      # slides 2 and 4 — one tool/step per slide, same shape
      ground_source: diffusion
      text_render_mode: composited
      zones:
        - {name: kicker, rect_pct: [0.10, 0.18, 0.50, 0.05], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#FFFFFF"}
        - {name: body, rect_pct: [0.10, 0.24, 0.60, 0.10], type_scale: 0.032, weight: Regular, align: left, max_lines: 3, color: "#FFFFFF"}
    prompt_quote:   # slide 3 — third tool/step beat, identical shape to body (no verbatim-prompt content in this system, same convention as ig_annotated_proof §2.2 / ig_stat_slab §2.4)
      ground_source: diffusion
      text_render_mode: composited
      zones:
        - {name: kicker, rect_pct: [0.10, 0.18, 0.50, 0.05], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#FFFFFF"}
        - {name: body, rect_pct: [0.10, 0.24, 0.60, 0.10], type_scale: 0.032, weight: Regular, align: left, max_lines: 3, color: "#FFFFFF"}
    end_card:
      ground_source: diffusion            # same environment family, quiet closing frame — an operator MAY override to programmatic/cream to visually "close" the photoreal sequence; shipped default keeps the environment for series consistency
      text_render_mode: composited
      zones:
        - {name: cta, rect_pct: [0.10, 0.20, 0.60, 0.10], type_scale: 0.045, weight: SemiBold, align: left, max_lines: 2, color: "#FFFFFF"}
        - {name: subtext, rect_pct: [0.10, 0.32, 0.60, 0.06], type_scale: 0.026, weight: Regular, align: left, max_lines: 2, color: "#FFFFFF"}
```

**Text budgets:** `max_title_words: 8`, `max_body_words: 16` per slide (reference average is ~10-20
words/panel including the tool name) — deliberately thin, this system's whole thesis is "the photo does
the work, the words don't have to."

**N-D prompt implications.** Ask for: room type, light quality (soft window light / golden hour / cool
overcast), 2-3 concrete environment props (desk material, one device, one personal object), camera
framing (eye-level, slightly off-center, phone-camera-real, NOT a hero product angle), and the reserved
caption-zone directive verbatim. Never ask for: a person, a face, any on-image text beyond what the
reserved-zone mechanism composites, any brand logo (the tool being discussed is named in the caption
text, not depicted as an app icon — a deliberate simplification vs. the existing `photoreal_lifestyle_
sticker` mode's icon-composite step, dropped here because it adds a real-logo-asset dependency this
system doesn't need to win).

**Diffusion-surface census row:** `cover` diffusion, `body`×2 diffusion, `prompt_quote` diffusion,
`end_card` diffusion (default) — **all 5 slots diffusion-touched**, the first system in the library where
that's true; every slot's `text_render_mode` stays `composited` throughout (case (b) universally), so the
gibberish-text risk is identical to any single-diffusion-slot system, just paid 5× instead of 1×. Flag
this cost property explicitly for `RenderContract` budget planning, same as `ig_stat_slab`'s own flagged
cost property (§2.4).

**Gibberish-proofing.** Zero on-image diffusion text anywhere (all captions composited). The only
non-text visual risk is the reserved-zone safe-zone check itself (`check_ground_safe_zone`) failing on a
busier-than-requested generated photo — same fallback-to-programmatic-ground behavior every other
diffusion slot in the library already has (`COMPOSITING_SPEC.md` "Panel item G").

### B.2 `ig_scene_hook` / `li_scene_hero` — cinematic photoreal scene + bold caption (the 2.17M-view class, B2B-adapted)

**Intent:** the #1-weighted item in the whole corpus (§A.2) is a photoreal/illustrated dramatic scene with
a punchy caption. Adapted for B2B: a moody, cinematographically-lit office/tech environment (never a fake
drama persona, never an invented catastrophe claim) with a bold, short, composited hook.

**Keys:** `register: photographic_ugc` · `archetype: native-caption-frame` (existing key,
`style_guide.yaml:149`, already bound to `native_caption_frame`) for the IG single-slot-feel version, OR
`aspirational-lifestyle-scene` for a moodier take — **recommend a NEW archetype, `cinematic-scene-hook`**,
since neither existing archetype's directive captures "dramatic lighting for emphasis, not neutral
lifestyle-real" — flagged as the one net-new archetype key this document proposes (mirrors `ig_annotated_
proof`'s single new `generation_mode` in the original six, §2.2). `generation_mode: cinematic_scene_hook`
— **NEW**, proposed below. Destination: both — `ig_scene_hook` is IG carousel (5 slots, hook-led, then a
programmatic payoff), `li_scene_hero` is the LinkedIn single-`hero` sibling (matching the pattern every
other topic in the six-system set already uses, one LI + one IG per intent, §2.1/§2.2's pairing).

**New `GENERATION_MODES` entry (proposal, illustrative):**
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
        "Reserve a plain, low-detail region for a short (<=2 spans, <=6 words each) caption to be "
        "added after generation, positioned in the frame's own natural negative space (sky, wall, "
        "shadow) rather than a fixed corner."
    ),
),
```

**Zones — `ig_scene_hook` (canvas 1080×1350):**
```yaml
ig_scene_hook:
  display_name: "Scene Hook"
  topic_tag: scene_hook_generic            # NEW, see integration note
  destination: instagram_feed
  register: photographic_ugc
  archetype: cinematic-scene-hook          # NEW
  generation_mode: cinematic_scene_hook    # NEW
  ground_recipe: photoreal_cinematic
  palette:
    caption_ink: "#FFFFFF"
  slots:
    cover:
      ground_source: diffusion
      text_render_mode: composited
      zones:
        - {name: headline, rect_pct: [0.12, 0.66, 0.76, 0.14], type_scale: 0.06, weight: Bold, align: center, max_lines: 2, color: "#FFFFFF"}
    body:       # slides 2, 4 — payoff steps switch to a PROGRAMMATIC cream/dark card (deliberate register break, see note below)
      ground_source: programmatic
      text_render_mode: composited
      ground_recipe: dark_terminal
      zones:
        - {name: kicker, rect_pct: [0.12, 0.16, 0.76, 0.06], type_scale: 0.026, weight: SemiBold, align: left, max_lines: 1, color: "#00A39A"}
        - {name: headline, rect_pct: [0.12, 0.24, 0.76, 0.16], type_scale: 0.06, weight: SemiBold, align: left, max_lines: 2, color: "#FFFFFF"}
        - {name: body, rect_pct: [0.12, 0.46, 0.76, 0.30], type_scale: 0.030, weight: Regular, align: left, max_lines: 5, color: "#EDEAE3"}
    prompt_quote:   # slide 3 — a second scene beat, back to photoreal (bookends the programmatic payoff slides — hook / payoff / scene / payoff / close rhythm)
      ground_source: diffusion
      text_render_mode: composited
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
**Why `body`/`end_card` switch to programmatic dark-terminal instead of staying photoreal for all 5
slots (unlike `ig_lifestyle_stack`, §B.1):** the scene-hook class's own reference (§A.2) is a
**hook-only** device in the source corpus — every winning exemplar is a single dramatic image, never a
5-panel drama sequence (that would be visually exhausting and dilutes the one-shot impact that makes the
class work). This system keeps the photoreal spend where the data shows it earns attention (cover +
one mid-carousel scene beat) and reverts to the library's existing programmatic dark-terminal recipe
(reused from `ig_prompt_sheet` §2.6, same hex `#1E1B2E`/`#00A39A`) for the substantive payoff content —
also halving this system's diffusion spend vs. `ig_lifestyle_stack`.

**`li_scene_hero` (LinkedIn single `hero`, 1920×1080):**
```yaml
li_scene_hero:
  display_name: "Scene Hero"
  topic_tag: scene_hook_generic
  destination: linkedin
  register: photographic_ugc
  archetype: cinematic-scene-hook
  generation_mode: cinematic_scene_hook
  ground_recipe: photoreal_cinematic
  slots:
    hero:
      ground_source: diffusion
      text_render_mode: composited
      zones:
        - {name: headline, rect_pct: [0.12, 0.62, 0.76, 0.18], type_scale: 0.07, weight: Bold, align: left, max_lines: 2, color: "#FFFFFF"}
        - {name: qualification, rect_pct: [0.12, 0.80, 0.76, 0.08], type_scale: 0.03, weight: Regular, align: left, max_lines: 1, color: "#FFFFFF"}
```

**Text budgets:** cover/hero headline `≤2 spans × ≤6 words` (matches the diffusion cap even though this
is `composited`, for visual consistency with the source pattern's punchy brevity — not a hard technical
requirement since composited text has no span limit, but a deliberate creative constraint per this
system's own "the drama IS the message" thesis); payoff `body` slides ≤24 words as standard.

**N-D prompt implications.** Ask for: named environment archetype (glass meeting room / server corridor /
night-skyline office / single lit desk), one dominant light source + its color temperature, time-of-day,
2-3 concrete props, and the reserved-zone directive. Never ask for: any person, any robot/mascot/creature,
any invented statistic or claim depicted as on-image text beyond the gated hook span, any screen/UI
content.

**Diffusion-surface census row (IG):** `cover` diffusion, `body`×2 programmatic, `prompt_quote` diffusion,
`end_card` programmatic — **2 of 5 slots diffusion-touched.** (LI): `hero` diffusion — 1 of 1.

### B.3 `ig_operator_grid` — the 10xoperator editorial-grotesque system

**Intent:** the operator-supplied editorial-grotesque carousel (§A.3), formalized. Off-white grid-paper
ground (programmatic), grotesque black headline with one accent-colored emphasis phrase, a highlighter
bar, a small photoreal inset (diffusion-generated, never a screenshot), header/footer masthead furniture,
swipe pill, page-number badge.

**Keys:** `register: editorial` (this is a typographic/paper-ground register with one small photographic
inset, not a photographic register — the inset is a minority element, same classification logic as
`ig_annotated_proof`'s screenshot inset not flipping that whole system to `photographic_ugc`) ·
**archetype: NEW, `editorial-grotesque-grid`** — none of the 16 existing archetypes name a grid-paper
ground or a color-emphasis-phrase headline device; closest existing (`editorial-carousel`) is the
serif/Didone family and would collide semantically if reused. `generation_mode: designed_card` (reused —
the mode's own generic directive already covers "the existing designed typographic-card composition,"
§1's note on why `designed_card` needs no per-archetype variant). Destination `instagram_feed`, carousel,
5 slots.

**Zones (canvas 1080×1350):**
```yaml
ig_operator_grid:
  display_name: "Operator Grid"
  topic_tag: agency_playbook_howto         # NEW, see integration note
  destination: instagram_feed
  register: editorial
  archetype: editorial-grotesque-grid      # NEW
  generation_mode: designed_card
  ground_recipe: grid_paper                # NEW ground recipe — programmatic: paper base + thin ruled grid overlay, distinct from the existing `paper` recipe's speck-grain
  palette:
    ground: "#F3F1E9"
    grid_line: "#E4E0D2"                   # faint ruled grid, ~6-8% opacity equivalent
    headline_ink: "#221F1C"
    emphasis_ink: "#302B87"                # brand indigo — recommended emphasis color, see §A.3's mapping discussion (option 1)
    highlight_bar: "#E8A63B"                # NEW single-purpose accent (amber/ochre) — recommended, see §A.3 option 1; fallback "#00A39A" per option 2 if no new token is approved
    body_ink: "#332F2B"
    footer_ink: "#6B655C"
  type:
    display_family: "Grotesque sans, heavy weight (not yet acquired -- e.g. Neue Haas Grotesk Display Black / Inter Black as an OFL-licensed substitute)"
    display_fallback: "assets/fonts/NotoSans-Variable.ttf@700"
    body_family: "Montserrat Regular"
    body_fallback: "assets/fonts/NotoSans-Variable.ttf@400"
  slots:
    cover:
      ground_source: programmatic          # grid-paper ground is 100% programmatic — never diffused
      text_render_mode: composited
      logo_zone: [0.08, 0.06, 0.30, 0.04]           # masthead brand wordmark, top-left
      decorative_zone: [0.55, 0.06, 0.37, 0.04]     # masthead running theme label, top-right, + hairline rule below (drawn programmatically)
      screenshot_inset:                              # NOT a screenshot — a diffusion-generated small photo, see note below; field reused for its typed rect/asset shape only
        mode: optional
        rect_pct: [0.62, 0.15, 0.30, 0.20]
        ground_source: diffusion
        corner_radius_pct: 8
        shadow_pct: 2
        fallback: solid_color_placeholder_tile
      zones:
        - {name: kicker, rect_pct: [0.12, 0.18, 0.50, 0.05], type_scale: 0.024, weight: SemiBold, align: left, max_lines: 1, color: "#221F1C"}   # black-outline pill label, drawn as a pill background programmatically
        - {name: headline, rect_pct: [0.12, 0.25, 0.60, 0.30], type_scale: 0.075, weight: Bold, align: left, max_lines: 4, color: "#221F1C"}    # ONE run inside this zone's text is recolored to emphasis_ink at CRAFT time -- a compositing-level rich-text feature, not a second zone (flagged below)
        - {name: highlight_line, rect_pct: [0.12, 0.60, 0.68, 0.06], type_scale: 0.032, weight: Bold, align: left, max_lines: 1, color: "#221F1C"}   # rendered on a solid highlight_bar rect drawn behind this zone
        - {name: body, rect_pct: [0.12, 0.70, 0.68, 0.10], type_scale: 0.026, weight: Regular, align: left, max_lines: 3, color: "#332F2B"}
        - {name: footnote, rect_pct: [0.12, 0.84, 0.68, 0.05], type_scale: 0.020, weight: Regular, align: left, max_lines: 2, color: "#6B655C"}
      footer_zone: [0.08, 0.90, 0.84, 0.06]          # hairline rule + swipe pill (left) + page-number badge (right), drawn programmatically, not `zones:`
    body:      # slides 2, 4 — masthead + headline + body persist, highlight_line/inset optional per-slide
      ground_source: programmatic
      text_render_mode: composited
      logo_zone: [0.08, 0.06, 0.30, 0.04]
      zones:
        - {name: kicker, rect_pct: [0.12, 0.18, 0.50, 0.05], type_scale: 0.024, weight: SemiBold, align: left, max_lines: 1, color: "#221F1C"}
        - {name: headline, rect_pct: [0.12, 0.25, 0.76, 0.24], type_scale: 0.065, weight: Bold, align: left, max_lines: 3, color: "#221F1C"}
        - {name: body, rect_pct: [0.12, 0.54, 0.76, 0.28], type_scale: 0.028, weight: Regular, align: left, max_lines: 6, color: "#332F2B"}
      footer_zone: [0.08, 0.90, 0.84, 0.06]
    prompt_quote:   # slide 3 — reused as a third body beat, same convention as every other system's slide-3 (§2.2/§2.4/B.1/B.2)
      ground_source: programmatic
      text_render_mode: composited
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

**Flagged, not resolved by this document:** the mid-headline emphasis-phrase color swap
(`{name: headline}` zone above) needs one word/phrase inside a single `OnImageText.title` string to
render in `emphasis_ink` while the rest renders in `headline_ink` — every other system in the library
colors an entire zone uniformly. This is a genuinely new `layout.py`/`typeset.py` capability (rich-text
run coloring within one zone), not a config value; flagged the same way `DESIGN_DECONSTRUCTION.md` §C.1
flagged `value_sheet_max_words`' own new capability needs. Until built, the safe interim behavior is
**omit the color-swap** and render the whole headline in `headline_ink` (loses the reference's signature
device but stays byte-correct and gibberish-free) — never approximate it by asking diffusion to render
colored text.

**N-D prompt implications (inset only — this is the system's ONLY diffusion surface).** The inset is a
small, quiet, real-feeling desk/tool/workspace close-up photo (rolled paper + drafting tools, a laptop
corner, a notebook and pen) — genuinely photographic, never a screenshot, never containing any readable
text or UI chrome (the reference's own inset is text-free). Ask for: one concrete desk/tool vignette,
soft natural light, shallow depth of field. Never ask for: any readable text, any screen/UI, any person.
**This is explicitly NOT a screenshot inset** despite reusing `ig_annotated_proof`'s typed `screenshot_
inset` field shape for its rect/corner-radius/fallback convenience — the field's `mode` and `ground_
source` here are `optional`/`diffusion`, the opposite of `ig_annotated_proof`'s `required_or_omit`/
composited-real-asset-only rule (§2.2) — naming this distinction explicitly so an implementer never
conflates the two and accidentally diffuses a "screenshot."

**Diffusion-surface census row:** `cover` diffusion (inset only — headline/body/ground all programmatic),
`body`×2 programmatic, `prompt_quote` programmatic, `end_card` programmatic — **1 of 5 slots
diffusion-touched, and even that slot's diffusion surface is a small inset, not the full ground** (a
genuinely lower diffusion footprint than any other system in §B, including the original six's `ig_
annotated_proof`/`ig_stat_slab`, since those diffuse the FULL cover ground while this system diffuses
only ~6% of the cover's canvas area).

### B.4 `li_product_render` — judged and excluded

**Not proposed.** §A.4 already lays out the evidence: the reference exemplar (`launch-automation_06_
website-offer.jpg`) is simultaneously the worst-performing item in the entire studied corpus (weighted
-9.02, `CATALOG.md` §1/§4) and a near-perfect checklist of things our OWN pre-existing Hard DON'Ts already
forbid — gradient-mesh ground (§5.5), clip-art benefit-pill icon row (§5.2), a fully invented device-mockup
UI (§5.4), and an invented human "broker" persona presented as real (persona policy) — plus a
direct-response CTA-banner/urgency grammar this document's own anti-ad rules (§C.2 below) name as the
signal that most reliably reads as "advertisement" rather than "content." Building a style system around
this reference would mean either (a) shipping something the engine's own guardrails already block outright
(pointless — it would fail governance on every asset), or (b) "sanitizing" it into a generic product-shot
card that keeps none of the reference's actual distinguishing moves and is therefore not really this
reference at all, just a weaker `li_signal_card`/`ig_stat_slab` (§2.1/§2.4) with a laptop icon — in which
case the two systems we already have cover the legitimate underlying need ("depict a tool/result") better
than a new one would. No new system; the data and the existing guardrails agree, independently, that this
is not a format to add.

---

## C. Library-wide guidance

### C.1 Updated diffusion-surface census — ALL systems (existing 6 + `ig_value_sheet` + these 4 new)

| System | `cover`/`hero` | `body`×2 | `prompt_quote` | `end_card` | Diffusion-touched slots | Register |
|---|---|---|---|---|---|---|
| `li_signal_card` | n/a (hero only) | — | — | — | **0 — fully programmatic** | editorial |
| `ig_annotated_proof` | diffusion | programmatic | programmatic | programmatic | **1 / 5** | editorial |
| `li_statement_hero` | n/a (hero only) | — | — | — | **0 — fully programmatic** | editorial |
| `ig_stat_slab` | diffusion (text only, ground flat) | programmatic | programmatic | programmatic | **1 / 5** (0/5 under documented override) | editorial |
| `li_editorial_brief` | n/a (hero only) | — | — | — | **0 — fully programmatic** | editorial |
| `ig_prompt_sheet` | programmatic (firmed) | programmatic | programmatic | programmatic | **0 — fully programmatic** | editorial |
| `ig_value_sheet` *(proposed, `DESIGN_DECONSTRUCTION.md` §C.1)* | programmatic | programmatic | programmatic | programmatic | **0 — fully programmatic** | editorial |
| `ig_lifestyle_stack` **(NEW, §B.1)** | diffusion | diffusion ×2 | diffusion | diffusion | **5 / 5 — full-photoreal system** | photographic_ugc |
| `ig_scene_hook` **(NEW, §B.2)** | diffusion | programmatic ×2 | diffusion | programmatic | **2 / 5** | photographic_ugc |
| `li_scene_hero` **(NEW, §B.2)** | n/a (hero only) | — | — | — | **1 / 1 — diffusion** | photographic_ugc |
| `ig_operator_grid` **(NEW, §B.3)** | diffusion (small inset only) | programmatic | programmatic | programmatic | **1 / 5 (partial-area)** | editorial |

**What this changes about the library's overall diffusion profile.** Today (six systems + `ig_value_
sheet`): 7 systems, 2 with any diffusion surface, both capped at exactly 1 touched slot — the library is
overwhelmingly programmatic by construction. Adding the four §B systems: 11 systems total, 5 with a
diffusion surface, and for the first time a system (`ig_lifestyle_stack`) that is diffusion-touched on
**every** slot — a genuinely new cost/risk shape that N-D's per-asset token budgeting (§2.7's `slot_has_
diffusion_surface` formula) and `RenderContract` budget planning must account for explicitly, not
silently amortize into the existing "usually 0 or 1 diffusion slot" assumption.

### C.2 Anti-ad principles — five enforceable rules, extracted from the data (§A.1 vs §A.4)

The data draws a sharp, consistent line: `aitools_guy`'s quiet lifestyle panels (+42.53 weighted, 6.6%
saves) and `ig_operator_grid`'s reference (a genuine editorial format, operator-supplied because it reads
as content) win; `launch.automation`'s polished promo card (-9.02, worst in corpus) and the designed
typography title card (also negative, `CATALOG.md` §4 insight 3) lose. Five rules, each directly
traceable to a specific delta between the winning and losing exemplars:

1. **No radial glow / gradient-mesh hero grounds on a photoreal or editorial system.** The losing card's
   entire background is a purple radial glow; every winning exemplar's ground is either a flat, real
   environment or a flat, textured paper — nothing "engineered to look premium." (Already codified as
   Hard DON'T 5.5; restated here because it's the single most visually obvious ad-tell in the loser.)
2. **No benefit-pill / checkmark-icon-row grammar, ever, in a photoreal or editorial-grotesque system.**
   The loser's three checkmark pills are the textbook direct-response "features list" device; no winning
   exemplar in the entire studied set (across all format classes, not just this document's four) uses
   this pattern. (Already codified as Hard DON'T 5.2; restated for the same reason.)
3. **No device-mockup / product-render insets.** A 3D-angled laptop/phone showing a rendered "finished
   product" is the loser's single most ad-coded element (and doubles as a fake-UI violation, §5.4). Every
   photoreal system in §B instead shows the REAL environment the work happens in (a desk, a room, a
   corridor) — never a rendered simulation of an output.
4. **No urgency/price/CTA-banner language baked into the image.** "ORDER IN 5 MINUTES — NO CARD NEEDED,"
   "AS LOW AS $33/mo" are landing-page conversion copy, not social content — they read as an ad the
   instant they're legible, independent of the visual design around them. None of the four new systems'
   `end_card` zones use price, countdown, or "order now" language; CTA text stays in the existing
   library's already-established "Follow for more..." register (§7's hook/copy guidance pattern).
5. **The photograph (or paper texture) must be able to stand alone with zero text and still look like
   deliberate content, not a template waiting for copy.** This is the structural test that separates
   `aitools_guy`'s loft photo (still a compelling, real-feeling image with the caption removed) from the
   loser's laptop-mockup ad (meaningless, obviously unfinished-looking with the copy stripped out).
   Practically: N-D's RENDER prompt for any photoreal `ground_source: diffusion` slot in §B must describe
   a genuinely complete scene (real props, real light, real sense of place) that would read as a finished
   photograph even before any text composites on top — never a "backdrop" awaiting a sales message.

### C.3 Variety guidance — per-run mix for a 6-asset run

Given the catalog's own ranking (photoreal-scene-with-caption is the strongest faceless class available,
`CATALOG.md` §4 insight 2; designed cards are the weakest observed class, insight 3; screen-recording/
tutorial — out of this document's scope, no static-image equivalent — is the reliable B2B workhorse,
insight 4) and the operator's explicit ask for MORE variety than an all-designed-card rotation, recommend
this default distribution for a 6-asset run (mix of IG carousels + LinkedIn heroes across a week/theme):

| Class | Count / 6 | Systems drawn from | Rationale |
|---|---:|---|---|
| Designed card (existing 6 + `ig_value_sheet`) | 2 | `li_signal_card`, `li_statement_hero`, `ig_stat_slab`, `ig_prompt_sheet`, `ig_value_sheet` | The library's proven, zero/low-diffusion-risk backbone — keeps cost and gibberish-risk low for the majority-programmatic share of output, and several of these topics (n8n/Apify, sales-agent stat) are genuinely better served by a stat/logo card than a scene. |
| Photoreal lifestyle/scene (`ig_lifestyle_stack`, `ig_scene_hook`, `li_scene_hero`) | 2 | — | Directly answers the operator's reversal — this is the highest-upside, data-validated new class (§A.1/A.2's virality numbers). Cap at 2/6 (not more) because every diffusion-touched slot is a paid, QA-gated, fail-closed-fallback-eligible surface (`w8-11-plan-decisions.md`'s fail-closed lock) — more photoreal volume raises the run's total generation cost and failure-surface faster than the designed-card share does. |
| Editorial-grotesque (`ig_operator_grid`) | 1 | — | A genuinely distinct visual register (grid-paper + grotesque type) from both the serif-editorial systems and the photoreal systems — one slot in the mix keeps the run from reading as "two visual languages," and its diffusion footprint is the smallest of any new system (§B.3, partial-inset only), so it's cheap variety. |
| Existing serif-editorial (`li_editorial_brief`, `ig_annotated_proof`) | 1 | — | Keeps the calm/premium/high-trust register represented — not every asset should read as "dramatic scene" or "loud grid," and this is the register `visual_registers.editorial.mood` already targets for topics that call for restraint (ops-assistant/founder-trust content). |

Net: **3/6 photographic-or-photoreal-adjacent (2 new photoreal + grid's 1 partial inset), 3/6
fully-or-mostly programmatic** — roughly a 50/50 split between "designed" and "photoreal-forward" registers
at the run level, which is the concrete operationalization of "more visual variety than designed cards" the
brief asks for, without abandoning the low-cost/low-risk programmatic systems that still win for
stat/proof-led topics. This ratio is a starting recommendation, not a locked rule — an executor should
revisit it once real cost-per-asset and QA-pass-rate data exist for the four new systems specifically
(none of the four has shipped yet, so this split is evidence-informed extrapolation from the reference
corpus, not this engine's own production numbers).

---

## D. Verdict — top 5 highest-impact additions ranked

1. **Ship `ig_lifestyle_stack` (§B.1).** The single most directly evidenced addition in this document —
   the exact template that produced the #1-ranked slideshow item across BOTH Virlo monitors (909K views,
   6.6% save rate, +42.53 weighted, top-5-in-corpus territory) — adapted with one clean edit (remove the
   identifiable person, keep the environment) that strengthens rather than compromises the win condition.
2. **Ship `ig_scene_hook` / `li_scene_hero` (§B.2).** The literal #1-weighted item in the entire 1,271-video
   scored corpus (2.17M views, ws 51.1) is this class; a B2B-safe adaptation (real dramatic environments,
   no invented drama/robots/personas) is the highest-ceiling new format this document proposes, and its
   2-of-5-diffusion-slot design keeps the cost/risk lower than `ig_lifestyle_stack`'s full-photoreal spend.
3. **Ship `ig_operator_grid` (§B.3).** Operator-supplied reference, cheapest diffusion footprint of any
   new system (a partial inset, not a full ground), and the only new system that adds a genuinely distinct
   *typographic* register (grid-paper + grotesque + color-emphasis) rather than another photographic one —
   directly answers "more variety than Canva-like cards" without leaning on diffusion spend to do it.
4. **Formalize the anti-ad rules (§C.2) as a fifth/sixth Hard DON'T-style check**, alongside the existing
   §5.1-§5.5 — two of the five rules (no benefit-pill rows, no gradient-mesh) are already codified for
   other reasons, but "no device-mockup insets" and "no urgency/price CTA-banner language baked into the
   image" are net-new, directly evidenced by the worst-performing item in the whole studied corpus, and
   cheap to wire into the same `_FAKE_UI_RE`/`_GRADIENT_MESH_RE` deterministic-regex + N-E-rubric pattern
   §5 already establishes.
5. **Explicitly reject `li_product_render` (§B.4)** — not a build item, but a decision worth recording
   with the same weight as the four ship recommendations: it closes off a plausible-sounding "we should
   also do polished product ads" direction with hard evidence (worst-performing item in the corpus,
   triple Hard-DON'T violation) before anyone builds it on instinct alone.
