# Operator Favorites — Design DNA (2026-08-08)

The operator hand-picked 10 favorites from the 44 simulation renders as ground truth for
"double down on these styles." This document deconstructs them meticulously and codifies
the shared DNA as binding style-direction for W8-11 template prompts and selection weights.

## The 10 picks

| # | File | Class |
|---|---|---|
| 1 | round4/4_anime_scene | anime night scene, serif lower-third type |
| 2 | round4/2_robot_caricature | editorial-cartoon robot, cream ground |
| 3 | round4/1_full_website | fictional-website showcase (bakery), cream + grotesque |
| 4 | round5/P3_ai_do_firmy | serif brand promo, cream, indigo italic + teal CTA |
| 5 | round3/C_real_assets_refs | tool spotlight w/ REAL logo + REAL screenshot, cream |
| 6 | round3/D_obscure_logo_probe | app-icon lineup row, light warm-gray studio |
| 7 | round2/4_workflow_map_cs_refs | node diagram w/ real marks, white + dot grid |
| 8 | round2/3_tool_stack_cs_refs | logo list card, cream, real marks |
| 9 | round2/5_scene_hook_styled_cs | cinematic photoreal + editorial serif, amber number |
| 10 | round2/1_serif_statement_en | giant Didone serif statement, cream, indigo italic |

## What they share (the DNA)

### D1 — Ground: warm cream paper, or cinematic dark. Nothing in between.
7/10 sit on warm cream/ivory (#F6F1E7 family) or light warm-gray studio; 2/10 are
cinematic-dark night scenes (anime, scene hook); 1 is white+dot-grid (workflow). ZERO
picks use mid-gray, cold, saturated, or gradient grounds. The dark `ig_value_sheet`
and the glowy isometric dashboard were NOT picked despite technical quality.
⇒ RULE: organic default ground = warm cream `#F6F1E7` with subtle paper grain;
secondary = cinematic-dark scene with lower-third type; kill everything else as default.

### D2 — Typography: two voices only, always oversized, exactly ONE color emphasis.
(a) Huge high-contrast editorial serif (Playfair/Didone spirit) — picks 1, 4, 9, 10 —
often mixing roman + italic in one headline, italic carrying the brand-indigo emphasis.
(b) Heavy geometric grotesque — picks 2, 3, 5, 7, 8 — tight leading, near-black ink.
Every single pick has EXACTLY ONE emphasized word/phrase in a brand color: teal
("nespí.", "jde.", "Do večera", "AI"), indigo italic ("do firmy?", "uses it will."),
amber strictly for numbers/times ("2:01."), plus one orange outlier ("sama." — governance:
map to amber or teal in production). Type occupies 30–60% of canvas.
⇒ RULE: serif_editorial OR heavy_grotesque per system, never a third voice; mandatory
single-emphasis token per headline: teal default · indigo-italic for serif questions ·
amber reserved for numerals/times.

### D3 — Brand furniture on every card: kicker + wordmark.
Letterspaced small-caps kicker top ("NOVÝ TREND" / "HYPEDIGITALY") and the HYPEDIGITALY
wordmark footer appear on 8/10 picks. This is the recognizability engine across a feed.
⇒ RULE: every card-class post carries caps kicker (teal or ink) + wordmark footer
(letterspaced caps; the two-tone HYPE/DIGITALY cut seen in picks 3 & 5 is approved).

### D4 — The centerpiece "artifact": a real-feeling object, rounded, soft-shadowed.
Picks 3, 5, 6, 7, 8 center a tangible artifact: macOS-style browser frame (traffic
lights, ~20–24px radius, soft shadow), app-icon row, or node diagram — always with
REAL brand marks (the two picks with reference-fed real logos beat the verbal-guess
variants of the SAME concept — authenticity is visible). Icon lineup (pick 6) is itself
an approved post format ("tool lineup teaser"), production version uses manifest icons.
⇒ RULE: artifact device library = {browser_frame, icon_row, icon_lineup, node_diagram};
rounded 20–24px, soft shadow, real marks via manifest/fetch ladder, greeked micro-text.

### D5 — Illustration charm without faces.
Robot (indigo body, teal props, ink outlines, single lens eye) and anime (from-behind,
teal/amber screen glow against dark) both picked. Brand-tinted characters, zero human
faces, zero named personas. These become RECURRING brand characters — same robot design
language and same anime mood each time (template prompts pin the description).

### D6 — Copy: concrete beats clever.
The picked hooks carry specifics: "Do večera to jde." / "2:01." / "nikdy nespí." /
counts and times. Natural spoken Czech (or English), zero corporate abstractions.

## What was NOT picked (anti-signal, equally binding)
- Plain flat composited captions (round-1 style) — 0 picks ⇒ styled-type flip confirmed.
- Dark dense list card (`ig_value_sheet` dark) — restyle onto cream serif editorial.
- Glowy isometric dashboard, stat hero, myth-bust split, UGC kitchen — none picked ⇒
  demote to occasional-rotation weight, NOT deleted (variety reserve).
- Verbal-guess logo variants when a reference-fed sibling existed ⇒ prefer real marks.

## Selection re-weighting (stage-1 quota bias, "double down")
Elevated default weight: serif_statement / serif brand-promo shape · website_showcase ·
tool_stack (real marks) · workflow_map · scene_hook_styled (dark serif) · robot_caricature
· anime_scene · icon_lineup. Demoted to occasional: concept_dashboard, stat_hero,
myth_bust, ugc_phone, dark value_sheet. Virlo win-rate reweighting still applies on top —
evidence can promote a demoted class back.
