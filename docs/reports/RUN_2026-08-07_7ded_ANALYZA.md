# Analýza běhu 2026-08-07_7ded — co přesně se stalo, krok za krokem

*Napsáno 2026-08-07 na žádost operátora („obrázky i copy jsou hrozné — chci vidět přesně,
co šlo do Virlo, jaké prompty šly do generování obrázků, a přehledný souhrn"). Všechna
tvrzení níže jsou rekonstruovaná z artefaktů běhu, ne z paměti: `trace.jsonl`,
`logs/artifacts/raw/`, `copy_requests/`, `copy_responses/`, `pack/media/*.provenance.yaml`.*

---

## 1. Celý tok v jednom obrázku

```
Virlo (2 GET čtení, zdarma)          4 free zdroje (HN, Google News EN+CS, HF, PH)
   │                                     │
   ▼                                     ▼
normalizace signálů  ──►  ranking (DETERMINISTICKÝ – žádné LLM, jen keyword overlap)
   │
   ▼
spin (DETERMINISTICKÝ – žádné LLM: ICP/pain/offer/CTA z překryvu klíčových slov)
   │
   ▼
copy briefy → PAUZA → copy psal Claude RUČNĚ jako operátor (žádné LLM API)
   │
   ▼
claim gate (deterministický) → 1× blokace („treat") → oprava → pass
   │
   ▼
Kie nano-banana (NEJLEVNĚJŠÍ draft model, $0.02/obrázek)
prompt = můj ručně psaný image_brief + tvrdé zákazy (žádní lidé/text/loga/produkt)
   │
   ▼
2 hotové PNG — headline se do obrázku NIKDY nevypálil (overlay odložen na později)
```

**Klíčové zjištění: v celém běhu nebyl použit ŽÁDNÝ jazykový model** kromě obrazového
modelu na úplném konci. Výběr témat, „spin", brand-fit skóre — všechno jsou
deterministické heuristiky z Fáze 1 (v scorecardu označené
`fit_method: phase1-deterministic-heuristic (no model judgment)`). Copy a obrazové
brief-y psal Claude ručně v roli operátora. To je přesně to, co bylo v plánu kampaně
(W8-7 roadmapa, „interactive-file provider = cesta cílového testu"), ale je to zároveň
hlavní příčina nízké kvality.

---

## 2. Co PŘESNĚ šlo do Virlo a co se z něj vzalo

### Odesláno (běh 2026-08-07_7d0a, seq 16 a 18 v trace — běh 7ded už jen četl z cache):
1. `GET https://api.virlo.ai/v1/trends/digest` — bez parametrů (globální digest).
2. `GET https://api.virlo.ai/v1/agents/9c96fddf-…` — čtení TVÉHO existujícího monitoru
   „AI Trends Tracker". Do Virlo se neposílal žádný obsah — monitor byl nakonfigurován
   už 2026-08-06 s těmito parametry (z raw payloadu):
   - keywords: `claude ai lead generation, ai tools lead generation, claude code lead
     gen, ai agent lead generation, free claude ai leads, automated lead generation ai,
     ai lead generation strategy, claude ai for business, ai sales lead generation,
     b2b lead generation ai`
   - intent: *„I want to find trending videos on AI, claude, lead generation, AI
     agents, AI tools."* · 3 platformy · english_only · kadence: neděle

### Co Virlo vrátilo (raw: `logs/artifacts/raw/2026-08-07_7d0a/virlo/agent_*.bin`):
Bohatou analýzu — 6+ témat, každé s:
- `name` (např. „Claude AI for Automated Lead Generation & Sales", confidence 0.95, 33 videí)
- **`tactics`** — konkrétní virální taktiky („Demonstrating Claude AI for lead generation
  without scraping", „Automating B2B lead generation with AI SDRs", …)
- **`why_it_works`** — proč to funguje („Users are drawn to the promise of automating
  the tedious parts of lead generation…")
- plus `viral_tactics`, `top_10_breakdown`, `connecting_thread`, `timing_analysis`,
  `key_highlight` na úrovni celého monitoru

### Co z toho pipeline SKUTEČNĚ použila:
**Jen `name` + `confidence` + `video_count`.** ← **HLAVNÍ PŘÍČINA č. 1.**
`tactics`, `why_it_works`, `viral_tactics`, `top_10_breakdown` — celé bohatství, kvůli
kterému Virlo platíme — se zahodilo při normalizaci na „signál" (titulek + metriky).
Copy brief pak obsahoval jen holý název tématu, takže text neměl z čeho čerpat úhel,
hook ani formát, který na TikToku/Shorts reálně funguje.

---

## 3. Jak vznikly obrázky — přesné prompty

Prompt = **ručně napsaný `image_brief`** (psal Claude jako operátor, NE model) + pevně
injektované zákazy. Doslovné znění (sha256 sedí na trace: `061a48aa…` / `c95ea969…`):

**LinkedIn (b996…, téma „AI Tools for Lead Generation"):**
> A clean, modern abstract illustration of a funnel concept rendered as flowing streams
> of light converging toward a single bright point, deep indigo-to-teal gradient palette
> on a dark background, soft glow, minimal geometric shapes suggesting data and
> connection, professional B2B mood, no people, no text, no lettering, no logos, no
> screenshots, no product interfaces or dashboards. **Constraints: no people, no human
> figures, no faces, no hands; no text, no lettering, no words, no captions, no
> typography of any kind; no logos, no brand marks; no product screenshots, no app UI,
> no dashboards, no software interfaces.**

**Instagram (036f…, téma „Claude AI for Productivity"):**
> A bright, minimal flat-design illustration of an organised desk seen from above: a
> notebook, a warm cup of coffee, and gentle abstract light rays suggesting ideas being
> sorted into tidy stacks, indigo and teal accent palette on a light background, calm
> productive mood, square composition, no people, no hands, no text, no lettering, no
> logos, no screens with readable interfaces. **Constraints: (stejný blok zákazů)**

Model: `google/nano-banana` (Gemini 2.5 Flash Image) — **nejlevnější draft route**
($0.02/obrázek), zvolený záměrně pro cílový test za pár centů.

### Proč obrázky působí genericky a „nesouvisí" s copy — příčiny č. 2–4:
2. **Headline se do obrázku nikdy nedostal.** Návrh M4 záměrně odložil overlay
   (text + logo se mají skládat AŽ post-generací přes FFmpeg, §4.4a — bezpečnostní
   důvod: text vypálený modelem by obešel claim gate). Takže obrázek je zatím jen
   „pozadí bez sdělení" — spojení s copy je čistě tématické (trychtýř = leady,
   stůl = produktivita).
3. **Tvrdé zákazy dělají svou práci až moc dobře:** žádní lidé, žádný text, žádné logo,
   žádný produkt ⇒ zbývá abstraktní ilustrace. To je správná POJISTKA, ale bez
   overlay vrstvy a bez šablon je výsledek stock-fotka.
4. **Nepoužily se brandové šablony.** V Notionu leží HypeLead v2 social pack
   (129 souborů šablon postů!) a HD brand kit — pipeline je zatím vůbec nezapojila.

### Proč je copy slabé — příčina č. 5:
Psal ho Claude ručně, bez LLM, **bez využití voice-exemplárů** (v briefu byly odkazy na
korpus, ale nebyly použity) a **bez Virlo taktik** (viz č. 1). Výsledek: korektní,
bezpečný, generický LinkedIn text bez hooku.

---

## 4. Kde je „přehledný souhrn" pro KAŽDÝ běh (existující místa)

| Otázka | Kde to najdeš |
|---|---|
| Co běh dělal, krok za krokem, s časy | `logs/runs/<run_id>/trace.md` (lidsky čitelné) / `trace.jsonl` (úplné) |
| Souhrn výsledku za 2 minuty | `logs/runs/<run_id>/pack/digest.md` |
| Poslední běh | `logs/latest.txt` |
| Co přesně vrátil Virlo (surová data) | `logs/artifacts/raw/<run_id>/virlo/*.bin` (30denní retence) |
| Co dostal copywriter (kompletní brief) | `logs/runs/<run_id>/copy_requests/*.yaml` |
| Co copywriter odevzdal | `logs/runs/<run_id>/copy_responses/*.yaml` |
| Přesný prompt na obrázek | brief (`image_brief`) + konstanta v `media_gen.py`; sha v trace |
| Cena, model, checksum, task id | `pack/media/*.provenance.yaml` + spend ledger v `logs/state/engine.db` |

**Mezera, kterou tahle analýza odhalila:** trace záměrně neukládá plné TEXTY promptů
(jen hash+délku — pravidlo redakce §3). Pro obrazové prompty, které NEJSOU cizí obsah,
je to zbytečně přísné — plný prompt patří do provenance souboru u obrázku. → oprava níže.

---

## 5. Nápravný plán (v pořadí podle dopadu na kvalitu)

1. **Prošít Virlo inteligenci do copy briefů** — `tactics`, `why_it_works`,
   `viral_tactics` a `key_highlight` musí jít do `copy_requests/*.yaml` jako
   „viral playbook" sekce. Malá změna (virlo.py ukládá, copy_gen.py přikládá).
2. **LLM do smyčky** — copy, image brief i judge půjdou přes skutečný model
   (slot `openai-compatible-http` je hotový; chybí JEN API klíč od operátora).
   Bez toho zůstává copy ruční práce bez kalibrace.
3. **Overlay vrstva (§4.4a)** — headline + HD/HypeLead logo vypálit do obrázku
   post-generací (FFmpeg 8.1 je pinovaný, Noto Sans bundlovaný, CZ glyfy ověřené).
   Tohle je ten chybějící most mezi obrázkem a copy.
4. **Zapojit brandové šablony** z Notionu (HypeLead social pack, HD brand kit) —
   generovat jen pozadí/ilustraci DO šablony, ne celý post.
5. **Plné prompty do provenance** (drobnost, viz §4 výše).
6. Zvážit vyšší route (Nano Banana 2) pro finální vizuály — draft tier zůstane
   na iterace.

*Body 1, 3, 5 jsou čistě inženýrské a bez nákladů. Bod 2 čeká na klíč od operátora.
Bod 4 chce rozhodnout formát šablon (PNG šablony vs. FFmpeg kompozice).*
