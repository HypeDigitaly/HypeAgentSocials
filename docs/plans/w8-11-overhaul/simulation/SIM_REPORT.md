# W8-11 Pre-Implementation Simulation — Report (2026-08-07)

Operator-requested desk-check BEFORE plan execution: do the planned style systems,
prompts, and three-model setup actually produce good-looking images? 17 live kie.ai
renders + Pillow composites, hand-authored to emit exactly what the planned pipeline
would emit (composition directives, zone rects, palettes, and type scales lifted
verbatim from `STYLE_SYSTEMS_SPEC.md`).

**Verdict: the planned approach is CONFIRMED with real pixels. Two small amendments
folded into PLAN.md §13 item 18 (screens-off prompt wording; logo-manifest seeding).**

## What was rendered

| # | Concept (planned system) | canonical (nano-banana-2 ground + Pillow) | gpt-image-2 (full text) | nano-banana-pro (full text) |
|---|---|---|---|---|
| 1 | `ig_lifestyle_stack` cover 4:5 | ✅ clean scene, reserved zone honored, crisp composited Czech | ✅ excellent, Czech correct | ✅ excellent, Czech correct |
| 2 | `ig_scene_hook` cover 4:5 | ✅ cinematic; ⚠ faint code on monitors | ⚠ Czech correct BUT invented analytics dashboard on monitor (violates no-fake-UI) | ⚠ Czech correct; letterboxed caption band instead of in-scene negative space |
| 3 | `ig_operator_grid` cover 4:5 | ✅ after fit-to-width fix (see finding F4) | ✅ portfolio-grade, all Czech correct | ⚠ portfolio-grade BUT `AGENȚURA` — hallucinated Romanian comma-below Ț (see `zoom_agentura.png`) |
| 4 | `ig_value_sheet` body 4:5 | ✅ 1.85% Lora floor legible, all diacritics render | ✅ all 8 entries flawless | ✅ all 8 entries flawless, typography arguably better than the sim's |
| 5 | `li_scene_hero` 16:9 | ✅ strong; caption landed over furniture (zone-check case, still legible) | ✅ excellent | ✅ excellent |
| 6 | logo probe (5 real marks) | ❌ 2–3/5 (Claude = invented "C", ChatGPT tile color off, Zapier distorted) | ⚠ 3.5/5 (Zapier asterisk CORRECT, Claude = "A\" wrong colors, ChatGPT green tile) | ⚠ 3/5 (Claude = invented blue "A", Zapier = pre-2021 bolt) |

Prompts used: `prompts/`. Outputs: `canonical/`, `models/<model_string>/` (the planned
folder layout). Cost: 184 credits ≈ **$0.92** (confirmed per-image: nano-banana-2 8cr/$0.04,
gpt-image-2 6cr/$0.03 @1K, nano-banana-pro 18cr/$0.09 — exactly the §9.3 planning figures).

## Findings

- **F1 — Composited text wins on correctness.** Pillow + vendored fonts rendered Czech
  diacritics perfectly in every single case. This is the plan's canonical path; the sim
  found zero text defects on it. R3's recommended default (zero canonical diffusion
  text) is reinforced.
- **F2 — Test models are shockingly good at Czech, but not 100%.** Both rendered ~90
  words of dense diacritic-heavy Czech essentially flawlessly — the multi-model test
  track is clearly worth running. But nano-banana-pro hallucinated a Romanian `Ț` into
  display type ("AGENȚURA"), a defect subtle enough to ship past a tired human. The
  §10 promotion bar (scoreboard evidence before any config flip) is validated.
- **F3 — Logos are the weakest link everywhere.** Every model failed at least one of
  five well-known marks; all three missed Claude's. The IV-12 real-logo manifest
  fallback WILL engage in practice. Seed it before the confirmation run (amendment b).
- **F4 — fit_text/TypesetOverflowError is load-bearing.** The sim's first programmatic
  grid cover used a fixed 92px headline and overflowed into the inset and off-canvas —
  precisely the failure the render contract's shrink-to-fit + fail-closed typesetting
  prevents. Not a plan change; empirical proof the contract is needed.
- **F5 — Models decorate screens with invented UI.** Two of three scene renders put
  code/dashboards on monitors despite "no UI" prompt language. Canonical mitigation:
  explicit "screens are OFF or angled away" sentence in every photoreal template
  (amendment a); `no_ui_invented` N-E check remains the backstop.
- **F6 — Reserved-zone risk is real but handled.** The 16:9 hero's negative space
  landed on furniture; caption stayed legible only thanks to the shadow layer.
  `check_ground_safe_zone` + degrade-to-programmatic ladder is the right design.
- **F7 — nano-banana-pro layout autonomy.** Given a full-design brief it sometimes
  restructures (letterboxed caption band on #2; skipped the progress strip on #4).
  Fine for the test track (creative variance is the point); another reason canonical
  layout stays programmatic.

## Repro

```
python run_sim.py    # creates 17 kie.ai tasks, polls, downloads (needs KIE_API_KEY in repo .env)
python collect.py    # recovery poller for an interrupted run_sim (browser UA for CDN download)
python composite.py  # builds canonical finals from grounds + fonts/ (Playfair, Lora, Montserrat)
```

---

# ROUND 2 (2026-08-07, operator feedback applied)

Operator feedback on round 1: (1) plain composited captions too flat — wants expressive
model-rendered typography; (2) every tool mention must carry its logo; (3) same; (4) Czech
must sound native/colloquial; (5) logos must be correct; (6) gpt-image-2 = preferred model,
wants EN versions + more style variety. Round 2: 16 renders — 7 concepts × CS/EN on
gpt-image-2 + 2 nano-banana-pro `image_input` probes with REAL logo PNGs as references.
Outputs: `round2/`. Cost: 120 credits ≈ $0.60. One transient 500 on a nano-banana-pro
create (retried clean → success; suspect querystringed reference URLs).

## Results

| Concept (CS+EN) | gpt-image-2 verdict |
|---|---|
| 1 serif statement (cream, Playfair-spirit) | ✅✅ magazine-grade; italic indigo emphasis; CS+EN flawless |
| 2 stat hero ("10 hodin" + teal underline) | ✅✅ huge type, correct Czech |
| 3 tool stack (5 rows, logos by VERBAL description) | ✅ 5/5 marks recognizable incl. CORRECT Claude coral starburst + Make + Calendly; minor: tool name duplicated in heading+body line |
| 4 workflow map (form→Zapier→Claude→Gmail) | ✅✅ shippable as-is; all marks correct from descriptions alone |
| 5 scene hook styled (film-poster serif over cinematic scene) | ✅✅ screens-OFF instruction obeyed; amber "2:01." emphasis |
| 6 myth/reality split (torn-edge indigo/cream) | ✅ all Czech correct incl. "pětičlenném" in teal |
| 7 UGC phone (kitchen, casual bold caption) | ✅ native creator energy |

nano-banana-pro `image_input` probes: ✅✅ **faithful reproduction of the supplied real
marks** (exact Claude starburst, real Gmail M, Zapier — though it used the wordmark because
the reference file WAS the wordmark: manifest must store icon-form PNGs).

## Round-2 findings

- **F8 — Logo fidelity is a prompt-craft problem, solved two ways.** Round-1 failures came
  from naming marks without describing them. (a) gpt-image-2 + precise verbal mark
  descriptions ("Anthropic Claude coral starburst") ⇒ ~95% fidelity, all five brands
  recognizable. (b) nano-banana-pro + `image_input` reference PNGs ⇒ effectively 100%.
  ⇒ logo manifest entries need BOTH a `description:` (for prompt injection) and a `url:`
  (for reference-passing on nano-banana-pro routes / QA comparison / compositing fallback).
- **F9 — Expressive typography directives work.** "Typography is the hero… oversized display
  type… one accent word" produced consistently strong, big, positioned type on both models,
  both languages, zero Czech defects in round 2 (16/16 clean — incl. the dense tool-stack).
- **F10 — Accent governance drift.** With no hex pinned, the model picked coral/orange
  accents twice (Anthropic-adjacent). Template prompts must always pin the accent hex
  (indigo #302B87 / teal #00A39A / amber #E8A63B per system).
- **F11 — "Screens OFF or angled away" sentence fixed the invented-UI problem** (0/4 scene
  renders showed UI vs 2/3 in round 1).
- **F12 — EN renders are uniformly ≥ CS quality**; bilingual output is purely a copy/config
  question, not a rendering risk.

---

# ROUND 3 (2026-08-07, unknown-tool scenario — REAL live Virlo trend)

Source: monitor 9c96fddf trend **"Lovable AI for Website Building"** (status `new`,
first seen 2026-08-06, 1.43M views/2 videos; tactic literally pairs Claude-written copy
with Lovable site-building). Post copy derived from the trend's tactic, natural CS:
"Firma bez webu? Do večera to jde. / Claude napíše texty z vašich recenzí. Lovable z
nich postaví web." Four renders, 36 credits ≈ $0.18. Outputs: `round3/`.

Asset fetch dry-run (the runtime pipeline for an unknown tool, 3 HTTP calls): lovable.dev
HTML → og:image `https://lovable.dev/img/opengraph-image.png` (real vendor product image)
+ `apple-touch-icon.png` (real logo). WebFetch got 403; curl with browser UA worked —
the engine's fetch helper must send a browser UA.

| Render | Result |
|---|---|
| A logo GUESSED (gpt-image-2) | ✅ surprisingly correct Lovable heart+wordmark (big brand, in training data); flawless CS |
| B illustrative UI fallback (gpt-image-2) | ✅ exactly as designed: clearly stylized abstract browser mock + 'Lovable' name chip, no fake-real claim |
| C REAL assets via image_input (nano-banana-pro) | ✅✅ **the ideal**: faithful real logo + the REAL lovable.dev homepage visual (actual tagline + prompt box) in a browser frame inside a designed card; flawless CS |
| D obscure probe (Lovable/Higgsfield/Genspark/Krea unaided) | ⚠ ~2/4: Lovable ✓, Krea ≈✓ (chunky white K), Higgsfield & Genspark invented/dubious |

## Round-3 findings

- **F13 — Unaided logo fidelity follows brand fame.** Famous marks (Lovable) come out
  right; mid/long-tail (Higgsfield, Genspark) get plausible INVENTIONS — indistinguishable
  from real to a casual viewer, which is worse than obviously wrong. `logo_fidelity_ok`
  QA must compare against a fetched reference, never trust "looks like a logo".
- **F14 — The three-tier unknown-tool ladder works end-to-end:**
  Tier 1 (default): runtime fetch of real assets from the tool's own site (favicon /
  apple-touch-icon / og:image) → nano-banana-pro `image_input` (or Pillow composite) →
  name + real logo + real product visual. Fetch is ~3 HTTP calls, browser UA required.
  Tier 2: logo only (fetched) + styled typography card, no product visual.
  Tier 3 (fail-closed): clearly ILLUSTRATIVE stylized UI + name chip (render B's shape) —
  never a diffusion-invented "real-looking" screenshot of an actual product.
- **F15 — og:image re-rendering caveat.** nano-banana-pro redraws the reference visual
  faithfully (recognizable, correct text) but it is a redraw, not a pixel copy. Where
  pixel-exactness matters, composite the fetched og:image with Pillow instead; QA
  compares the render against the reference either way.

---

# ROUNDS 4-5 (2026-08-07/08 night — wilder styles + brand-promo class, operator-ratified)

Round 4 (`round4/`, 4 renders, $0.12): operator-requested wilder classes. Round 5
(`round5/`, 3 renders, $0.09): the new `brand_promo` class — HypeDigitaly service posts
with verbatim CTA "Klikněte na odkaz v popisku", generated regularly each batch,
deliberately promotional (exempt from the organic anti-ad DON'Ts).

| Render | Verdict |
|---|---|
| 4-1 full fictional website (bakery "Pekárna U Lípy") | ✅✅ complete polished site in browser frame; greeked-text trick kept small type clean; all CS correct |
| 4-2 robot caricature ("Kolega, který nikdy nespí.") | ⚠ charming premium cartoon BUT **first gpt-image-2 CS defect (~20 renders in): "ktery" lost its ý-accent** — ~5% display-type failure rate ⇒ QA gate + re-render fallback is mandatory, not optional |
| 4-3 isometric mission-control dashboard ("Velín vaší firmy.") | ✅✅ spectacular fictional diorama, panels greeked, CS correct |
| 4-4 anime night scene (character strictly from behind) | ✅✅ lofi-anime mood, faceless rule holds, serif CS flawless |
| 5-P1 "AI audit zdarma." (indigo) | ✅ CTA pill verbatim, CS flawless |
| 5-P2 "Chcete nasadit AI agenta?" (dark + amber underline) | ✅ flawless |
| 5-P3 "Jak zařadit AI do firmy?" (cream serif) | ✅ flawless (ř caron slightly detached — QA-note, passable) |

## Rounds 4-5 findings

- **F16 — Fictional-UI illustration mode works and is safe.** A COMPLETE fictional
  client website (invented business, greeked body text, ≤3 short legible strings)
  reads as "look what AI can build" without fabricating any real product's UI. Same
  for concept dashboards (all panels greeked). Integrity line holds: fictional = OK,
  real-product UI = ladder Tier 1 (real assets) or nothing.
- **F17 — Robot caricature + anime classes are viable** with the persona rules adapted:
  no named characters, no faces (single-lens robot eye / strictly-from-behind humans).
- **F18 — gpt-image-2 Czech failure rate is real (~5% of renders, display type).**
  The 4-2 defect is exactly the class the per-render text QA catches; with retry +
  composite fallback the shipped-defect probability drops to negligible.
- **F19 — brand_promo class validated.** All three service posts on strict brand
  palette with the verbatim CTA render flawlessly; cadence default 1/batch (dial).

---

# ROUND 6 (2026-08-08 — meme/satire classes, operator-requested)

Two distinct humor styles from the dominant Virlo trend theme (AI agents vs manual
busywork), EN per new default, DNA rules applied. `round6/`, 12 credits ≈ $0.06.

| Render | Verdict |
|---|---|
| M1 robot reaction meme (two-panel: panic vs smug) | ✅✅ recurring brand robot carries classic meme grammar; captions flawless, teal emphasis; vintage comic texture |
| M2 deadpan memo satire ("The Monday status meeting is cancelled." + APPROVED BY AI stamp) | ✅✅ model added a gilded museum frame that elevates the deadpan; serif flawless, distressed teal stamp |

- **F20 — Meme classes work inside the DNA.** Both keep cream grounds, single teal
  emphasis, wordmark footer, and the pinned robot character — recognizably on-brand
  while being actual memes. Guardrail codified: satire targets PROCESSES (meetings,
  busywork), never named people, companies, or competitor tools; claim gate applies
  to any factual-sounding punchline.
- **F21 — v2 after operator feedback (M1v2/M2v2): two generalized rules.**
  (a) `visual_logic_coherent` — the depicted actor must match the caption's subject
  (v1's robot panicking about hiring a human was nonsense); new N-F check for all
  illustration classes. (b) `instant_read` — memes must land in ~1s: known visual
  grammar (reaction contrast, RIP tombstone), minimal symmetric captions, visuals
  carry the joke. Carve-out codified: cartoon humans allowed from-behind/face-obscured
  when human-vs-AI contrast is the joke. Note: v2 tombstone robot drifted slightly
  from the pinned design — templates must pin the character description verbatim.
