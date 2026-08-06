# Notion Knowledge-Base Inventory — Second Brain (HypeDigitaly)

Written 2026-08-07 from a live authenticated read; page ids verified.

Scope: pages NOT covered by the earlier mapping pass (O firmě, Co nabízíme, Ceny a nabídky, Důkazy a reference, Pro AI agenty, Second Brain home, Čísla a sliby were already mapped and are not re-inventoried here).

Workspace roots:
- **Rozcestník** (top dashboard): `e49ddb91-8433-8229-a7ed-012a6e916b02` — contains the Second Brain hub + the "Projekty / Projects" database.
- **Second Brain** (knowledge hub): `3b3ddb91-8433-81fd-8195-d082cd98f4d6` — all pages below are its children.

---

## 1. Page map (this pass)

| Page | ID | Stable key (`page_id` in metadata) |
|---|---|---|
| Logo a vzhled značky | `3b3ddb91-8433-810e-b3f7-ebeef02c1c67` | `hd.hub.brand` |
| Plné texty (FULL CORPUS) | `3b3ddb91-8433-81c3-bc5d-fed017c9f53f` | `hd.corpus.root` |
| — Web hypedigitaly.ai (plné texty) | `3b3ddb91-8433-8153-8c83-ceed208f0f26` | `hd.corpus.web` |
| — PDF ceníky (plné texty) | `3b3ddb91-8433-81f2-acd2-f09f6ace300d` | `hd.corpus.pdf` |
| Texty, články, materiály | `3b3ddb91-8433-8136-9ad7-c0f702965dd8` | `hd.hub.content` |
| HypeLead v2 — Social marketing materiály | `3b3ddb91-8433-8148-9921-d736d8ee9034` | `hd.hub.hypelead_social` |
| Jak u nás pracujeme | `3b3ddb91-8433-810c-bc97-c0bf4fa87062` | `hd.hub.ops` |
| Prvních 15 minut | `3b3ddb91-8433-8196-86e7-cb9f9ed46aaa` | `hd.hub.onboarding` |
| Cesty podle role | `3b3ddb91-8433-8196-ba16-d19ec56ce8d3` | `hd.hub.roles` |
| Projekty / Projects (DB) | `486978c6-584b-4078-a965-ba7a6554b96c` (data source `collection://9c2963f7-4f30-4de1-8b42-a4911d89c2cc`) | — |
| HypeLead current pricing (Čísla a sliby row) | `3b3ddb91-8433-81dd-a938-c98158eba982` | claim: `HypeLead current pricing`, stav `schváleno`, chování AI `citovat` |

All hub pages carry `last_verified: 2026-08-05` and the FULL CORPUS snapshot date is **2026-08-05**.

---

## 2. Brand-asset / file inventory (F-M visual baseline)

### 2.1 HypeDigitaly corporate brand — page "Logo a vzhled značky" (`hd.hub.brand`)

**Zip packages (Notion attachments, full kit ≈143 files):**

| File | Contents | Notes |
|---|---|---|
| `HypeDigitaly_Brand_Core.zip` (attachment `b5c60a87-018b-4a3c-a233-48490814cd6c`) | 15 SVG vectors, 300ppi PNG exports, favicons, brand PDF, Montserrat fonts (18 TTF + OFL.txt) | **Primary package** |
| `HypeDigitaly_Brand_Extras.zip` (attachment `cc2648d4-28c7-4fc4-87e4-41e4d9a6b07c`) | JPEG, GIF animation, FB profile pic, cover page, mockups, svgtopng folder | svgtopng flagged redundant |
| `HypeDigitaly_Brand_AI_Masters.zip` (attachment `a2b2746c-1f3a-4a1a-b676-1328fe01492c`) | Illustrator `.ai` masters (krivky) | WIP masters need approval before public use |

**Brand guide PDF:** `Logo_HD_design.pdf` (attachment `c29bbee8-7402-4578-badd-75c06b368570`) — 19-page image-based brand board, 2022. Text-extract page exists in corpus but has little text (image PDF).

**Individual logo files (uploaded directly to the page):**

| File | What it is | Recommended use (per page table) |
|---|---|---|
| `HD_color_black.svg` / `HD_color_black@300x.png` | horizontal color + black text | light backgrounds (the de-facto primary) |
| `HD_Color_white.svg` / `HD_Color_white@300x.png` | horizontal color + white text | dark backgrounds |
| `HD_Color_logo.svg` / `HD_Color_logo@300x.png` | color symbol only | icon use |
| `HD_black.svg` | mono black | |
| `HD_white.svg` | mono white | |
| `HD_color_black_vertikal.svg` | stacked color + black | |
| `HD_Color_white_vertikal.svg` | stacked color + white | |
| `favicon.ico`, `favicon2.png` | favicon candidates | canonical favicon = OPEN question |
| `OFL.txt` | Montserrat font license | fonts themselves inside Core.zip |

**Brand facts:** primary gradient (2022 příručka) **#302B87 → #00A39A** (SVG exports have near-but-not-identical hex — open); typeface **Montserrat** SemiBold + Regular (web may also use **Geist** — unresolved); public CDN `https://hypedigitaly.ai/assets/images/`; web source repo `https://github.com/HypeDigitaly/hypedigitaly-web-2`.

**Explicitly NOT final/public:** `* - kopie*` files, `*_resized_pdf*`, the whole `svgtopng\` folder, unapproved AI masters.

**Open questions recorded on the page (do not invent answers):** (1) which lockup is official primary, (2) PDF vs SVG hex, (3) Montserrat vs Geist for digital, (4) canonical favicon.

### 2.2 HypeLead v2 product brand — page "HypeLead v2 — Social marketing materiály" (`hd.hub.hypelead_social`)

PNG export pack from GitHub `erikcermak/LeadAgent` → `prd/design-system/mocks/social/exports` (git = source of truth; Notion = download galleries). Subpages + counts:

| Subpage | ID | Category | Files |
|---|---|---|---|
| 01 — Loga a wordmark | `3b3ddb91-8433-8183-892e-c5184672650b` (`hd.asset.hypelead_logos`) | `app-icon-512x512.png`, `logo-avatar-1024x1024.png`, `logo-avatar-plain-1024x1024.png`, `logo-disc-1024x1024.png`, `logo-disc-plain-1024x1024.png`, `wordmark-dark-1600x400.png`, `wordmark-light-1600x400.png` | 7 (verified) |
| 02 — Feature karty (feat) | `3b3ddb91-8433-81b3-844e-e08d32acf139` | `feat-*` product-marketing cards, 1080×1080 / 1080×1350 | (uploaded earlier; count not stated) |
| 03 — Lead magnet / claims (lm) | `3b3ddb91-8433-8197-afac-d1d90274abb2` | `lm-*` organic-post claims, 1080×1080 / 1080×1350 | 10 |
| 04 — Post templates | `3b3ddb91-8433-81d5-9edc-c7766df7ba49` | `post-*` square / portrait / story | 7 |
| 05 — Platform covers | `3b3ddb91-8433-81fe-8988-d364a81a7661` | `facebook-*`, `linkedin-*`, `link-landscape-*` covers / OG | 4 |
| 06 — LinkedIn banner varianty | `3b3ddb91-8433-81cb-a1b9-df169801b895` | `linkedin-banner-*`, `linkedin-company-banner-*` A/B sets | 28 (+2 HTML base64) |
| 07 — Hi-res @2x a @4x | `3b3ddb91-8433-81c7-ac5c-ed0cdb9cdc4a` | 2× and 4× pixel-density duplicates | 80 (40 @2x + 40 @4x) |

Upload total for sections 03–07: **129 files** (per the page's own status table, 2026-08-05).

---

## 3. FULL CORPUS coverage map (`hd.corpus.root`, snapshot 2026-08-05)

**48 web pages scraped, 7+ PDF sources extracted.** Sources: `https://hypedigitaly.ai` sitemap (public pages only) + marketing pricing PDFs + HypeLead flyer HTML. Excluded: `/admin/*`, `/testing/*`, invoices, contracts, NDAs, client offers, lead lists, credentials.

### 3.1 Web (`hd.corpus.web`) — each subpage = one URL cluster, CS+EN, full scrape as **attached .md file**

| Corpus page | ID | Covers | Language |
|---|---|---|---|
| FULL TEXT Web — Home | `3b3ddb91-8433-8138-920c-d831af77a578` | `/` | CS + EN (`corpus-web-home.md`) |
| FULL TEXT Web — Chatbot | `3b3ddb91-8433-81c3-8ca1-cbe497920ed0` | `/chatbot` incl. public-sector pricing table (inline extract on page) | CS + EN |
| FULL TEXT Web — HypeLead | `3b3ddb91-8433-81ee-a35e-fa144d007136` | `/hypelead`, `/hypelead-cenik`, onboarding, `hypelead-cenik-flyer.html`; app = hypelead.ai | CS + EN |
| FULL TEXT Web — Služby part 1 | `3b3ddb91-8433-81c4-ab2c-e6ce3efdf94c` | services, AI agent, profit systems, automation, audit | CS + EN |
| FULL TEXT Web — Služby part 2 | `3b3ddb91-8433-8197-aa6d-d0824d6b5231` | remaining service pages | CS + EN |
| FULL TEXT Web — Blog | `3b3ddb91-8433-8139-8c87-d4764763f4e8` | blog index + both posts | CS + EN |
| FULL TEXT Web — Kontakt & legal | `3b3ddb91-8433-8132-8b66-ebd52af4ea02` | contact + legal pages | CS + EN |

**Engine-relevant caveat:** the full scrape text lives in **attached `.md` files**, not inline Notion blocks. These attachments were uploaded by a different integration, so the current MCP connection **cannot download them** (`object_not_found` on `download-attachment`); an engine must either read the inline "Agent extract" blocks, use S3 signed URLs from a fetched page, or scrape the live site (corpus rule: live URL is canonical anyway).

### 3.2 PDF (`hd.corpus.pdf`) — inline full text on subpages

| Corpus page | ID | Status |
|---|---|---|
| [current] HypeLead DFY flyer EN — full text | `3b3ddb91-8433-816f-a685-cb6b8dc7709d` | 🟢 current |
| [current] HypeLead DFY flyer CS — full text | `3b3ddb91-8433-815e-888a-f32be5af234c` | 🟢 current (full inline Czech copy incl. plans, "Jak to funguje", GDPR line) |
| FULL TEXT PDF — CURRENT HypeLead DFY | `3b3ddb91-8433-818b-b97e-dc8ff733b397` | 🟢 aggregate CS+EN + agent plan table (START €249 / PREMIUM €6,000 / FULL €10,500 / SCALE €18,000, min. 3 months) |
| [historical] AI Asistent Cenová nabídka — full text | `3b3ddb91-8433-81b7-bb07-d0a6d50a7540` | 🟡 historical (10k/25k/60k Kč tiers; current B2B tiers are 5 000/14 990/34 990 Kč per Ceny hub) |
| [historical] AI Asistent (file labeled nový ceník) — full text | `3b3ddb91-8433-8183-a8f2-e0b1fa6f9feb` | 🟡 historical |
| [historical] AI Obchodní tým Cenová nabídka — full text | `3b3ddb91-8433-815a-ac64-d4f24761d0af` | 🟡 historical |
| [historical] Cenová nabídka AI Obchodní tým (alt) — full text | `3b3ddb91-8433-8192-989d-e04a97d53fc8` | 🟡 historical |
| FULL TEXT PDF — HISTORICAL pricing flyers | `3b3ddb91-8433-812c-9c4c-cfb2eb2f5e53` | 🟡 aggregate |
| [brand] Logo_HD_design.pdf — extracted text | `3b3ddb91-8433-8132-970b-c09ff64cfa19` | image PDF, little text |

**Corpus rules for AI (stated on the pages):** prefer 🟢 + live URL for prices; 🟡 only with a warning; if live web differs from corpus → treat as UNKNOWN and verify live; chatbot page may still mention RAGus but **current runtime for new bots = HypeAgent (hypeagent.ai)**.

---

## 4. Texty, články, materiály (`hd.hub.content`)

- **Blog: only 2 published posts** (both CS+EN, live on the web):
  1. "Proč 90 % AI projektů selhává? Kompletní průvodce přípravou dat pro AI" — `hypedigitaly.ai/blog/proc-jsou-data-dulezita-pro-ai-kompletni-pruvodce` — published 28. 12. 2025.
  2. "Případová studie: 5 regionů ČR (Leden–Červenec 2025)" — `hypedigitaly.ai/blog/pripadova-studie-5-kraju-cr` — published 15. 7. 2025.
- **Newsletter:** a public-administration newsletter exists but lives in the marketing process (Brevo etc.) — **no archive in Notion**.
- **Flyers/sales PDFs:** current + historical pricing PDFs are attachments on "Ceny a nabídky" (already mapped); 🟢/🟡 state governed there.
- HypeLead v2 social pack cross-referenced (section 2.2).

## 5. Jak u nás pracujeme (`hd.hub.ops`)

- Client delivery model (public on web): **Discovery → Audit → Strategie → Delivery**.
- Live tasks in **HypeDigitaly Projects** teamspace + Projekty DB; Second Brain = company truth, not a task tracker.
- SOP for updating the Second Brain: find hub → edit plain Czech → add "Odkud to víme" (source+date) → set 🟢🟡🔴 on money/platform facts → update Seznam stránek / Čísla a sliby → `last_verified` = today.
- Tools (names only, no credentials): Notion, HypeAgent, (legacy RAGus), Voiceflow, Netlify web, Brevo/Resend (per project), GitHub. Web repo: `HypeDigitaly/hypedigitaly-web-2`.

## 6. Prvních 15 minut / Cesty podle role (skim — facts not already captured)

- HypeDigitaly s.r.o. = AI agency: chatbots, automation, HypeLead, websites.
- Prices may be quoted to clients **only** from "Ceny a nabídky" and only 🟢 items.
- Public-sector chatbots run on **HypeAgent (hypeagent.ai)**, not legacy RAGus.
- Key people referenced: Erik, Pavel (area owners).
- Cesty podle role: role paths only (Obchod / Delivery / Marketing) — no new facts.

## 7. Projekty / Projects database (Rozcestník)

Schema: Projekt (title), Status (🟢 Běží / 🟡 Pauza / 🔵 Příprava / ✅ Hotovo), Klient, Aktuální fáze, Co se teď děje, Odkaz na projekt, Poslední update, Tým.

**Current rows (2 projects; names/statuses only, per confidentiality rule):**

| Projekt | Status | Client type | Fáze | Last update |
|---|---|---|---|---|
| HypeLead v2 | 🟢 Běží | internal product (HypeDigitaly) | Testování enriche | 2026-07-24 |
| Nuvaro | 🟢 Běží | external client | Testing fáze | 2026-07-24 |

**Rozcestník structure:** top-level dashboard → Second Brain hub + Projekty/Projects DB (single table view "Default view").

## 8. HypeLead current pricing (Čísla a sliby row `3b3ddb91-8433-81dd-a938-c98158eba982`)

- Stav **schváleno**, chování AI **citovat**, ověřeno 2026-08-05. Canonical source: `https://hypedigitaly.ai/hypelead` (+ `?lang=en`) + official DFY flyer PDF on Ceny a nabídky.
- Plans (EN flyer, excl. VAT): START DIY €249/mo + €3,000 setup (1,500 firms/mo); PREMIUM DFY €6,000 + €3,500 (5,000); FULL DFY €10,500 + €4,000 (10,000); SCALE DFY €18,000 + €5,000 (15,000). Minimum 3 months. Older HypeLead PDFs = historical, not current.

---

## 9. Gaps & observations (what the engine will miss)

1. **No social-post archive for HypeDigitaly.** No LinkedIn/Facebook/X post history anywhere in Notion — the HypeLead v2 pack is *templates/mockups*, not published posts. The engine has no historical social voice to learn from; only web/blog/flyer copy.
2. **Only 2 blog posts total.** Czech long-form exemplar pool is thin (2 articles + web pages + 1 CS flyer). No EN-only original content — EN is always a translation of CS.
3. **FULL CORPUS web text is attachment-locked for this MCP integration.** `corpus-web-*.md` attachments return `object_not_found` on download (uploaded by another integration). Engine must use live URLs (which the corpus itself declares canonical) or the inline "Agent extract" blocks.
4. **Brand primary is officially undecided.** Four open questions on the brand page (primary lockup, final hex, Montserrat vs Geist, canonical favicon). F-M baseline should treat `HD_color_black` + gradient #302B87→#00A39A + Montserrat as working default and flag it as operator-unconfirmed.
5. **No HypeLead *corporate* logo kit distinct from the v2 social pack** — HypeLead visual identity exists only as PNG exports (no SVG/vector masters in Notion; vectors live in the LeadAgent GitHub repo, if at all).
6. **Newsletter content absent** — referenced (Brevo) but zero issues archived in Notion.
7. **No case-study pages beyond the one blog case study**; testimonials referenced (regional IT leads on historical flyer) but full quotes live on the flyer/Důkazy page, not as standalone assets.
8. **Photography/team imagery absent** — no people photos, office shots, or product-in-context images anywhere in the brand pages; visual pool = logos, social templates, mockups, GIF animation.
9. **Historical pricing hazard well-labeled** — 🟡 pages exist with obsolete prices (AI Asistent 10k/25k/60k; older HypeLead flyers). Engine must respect 🟢-only rule (matches hd.hub.* traffic-light convention).
10. **Projects DB is sparse** (2 rows, both 🟢) and holds a client name; treat "Nuvaro"/client field as internal-only, not content material.
