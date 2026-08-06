# R4 — Právní revize architektonického plánu (Wave 4)

**Recenzent:** R4 (právní / GDPR / AI Act / české právo)
**Datum:** 2026-08-06
**Předmět:** `docs/architecture/ARCHITECTURE_PLAN.md` (Stage 4), `DECISION_LOG.md`, `RISK_LOG.md`
**Důkazní základ:** VÝHRADNĚ `docs/research/C7_legal_compliance.md` (retrieval 2026-08-06). Žádný nový webový výzkum nebyl proveden. Kde C7 nemá důkaz, je to v nálezu výslovně označeno jako **mezera důkazního balíčku**, nikoli jako zjištěné právo.
**Rozsah čtení:** §2 (sběr, do-not-scrape, retence), §3.2–3.5, §4.3–4.5, §5 celé, §6.3–6.10, §7 celé, §10.4 (knoby), §11, §12.1–12.3, §14 celé, §15, §16, §17, Appendix A; ostatní skimováno.

---

## 0. Souhrn v jedné stránce

Plán je právně **nadprůměrně poctivý** — v několika bodech jde nad rámec C7 (do-not-scrape list má 10 položek proti 7 v C7; zákaz hudby přes router a zákaz platformních trending zvuků C7 vůbec neřešil; poznámka o ztrátě indemnifikace při nákupu přes resellera je správná a nikde nezametená). Extract-first úložiště, LIA a privacy notice jako **blokující** Phase-0 artefakty, vypálený disclosure jako nosná kontrola, per-asset provenance record a oddělené potvrzení AI-labelu jsou implementace C7, nikoli jeho parafráze.

Přesto plán **není připraven pro Stage 5 bez oprav**. Pět nálezů má blokující charakter a všech pět má stejný půdorys: *deklarace existuje, ale není zadrátovaná do jediného vynucovacího bodu, na který se plán sám odvolává.* Nejzávažnější je úplná absence režimu podob a hlasů osob (C7 §2.7 = blocker), přestože `motion class` v §5.3 obsahuje hodnotu **"talking human"** a v1 nikde neříká, že avataři/lidští presentéři jsou vyloučeni.

| Závažnost | Počet |
|---|---|
| **blocker** | 5 |
| **major** | 9 |
| **minor** | 7 |
| **celkem** | 21 |

---

## 1. Nálezy — BLOCKER

### [BLOCKER] B-1 · Podoby a hlasy osob: gate z C7 §2.7 v plánu vůbec neexistuje

**Právní základ:** zákon č. 89/2012 Sb., občanský zákoník — ochrana osobnosti, svolení k užití podobizny a zvukového záznamu projevů osobní povahy; zákonné výjimky jen pro úřední, vědecké, umělecké a zpravodajské účely (C7 §2.7; C7 sám tuto citaci vede v **Medium confidence** a žádá ověření proti primárnímu textu). Kumulativně čl. 50 odst. 2 a 4 písm. a) nařízení (EU) 2024/1689 a čl. 3 bod 60 (definice deep fake).

**Dotčené místo:** `ARCHITECTURE_PLAN.md` §5.3 (osa *Motion class* = "talking human"), §5.2 (`person-generation policy class`), §5.6 (odmítnutí "named real people"), §4.8 + §10.4 (knob "text-to-speech provider and **voice identity** per language"), §12.2 (obsah packu).

**Popis:** V celém dokumentu (372 KB) se **nevyskytuje ani jednou** slovo *likeness*, *podobizna*, *personality*, *avatar*, *deepfake*, ani *consent* ve smyslu souhlasu osoby. C7 §2.7 přitom formuluje dva konkrétní architektonické požadavky, oba v rozhodovací tabulce jako "decisions unblocked":

1. per-asset **příznak** "wholly synthetic, no real-person basis" vs. "modeled on a real identifiable person";
2. **uložený, rozsahově omezený záznam souhlasu** (účel, doba, platformy, odvolatelnost) jako podmínka publish-ready, plus samostatná HR/právní výjimka pro zaměstnance.

Plán místo toho má pouze `person policy` (no-people / adults-only / region-restricted) a odmítání "named real people" na úrovni routy. To je **content policy poskytovatele modelu, nikoli kontrola osobnostních práv**: pokryje odmítnutí vygenerovat Elona Muska, nepokryje (a) zaměstnance HypeDigitaly jako "founder avatara", (b) licencovaného stock herce, (c) klonovaný hlas v ElevenLabs. Knob "voice identity per language" nikde nerozlišuje licencovaný katalogový hlas od klonu reálné osoby. Zároveň v1 avatary **nevylučuje** — `motion class: talking human` je plnohodnotná osa směrovacího kontraktu a §4.2/§4.8 recepty ji nezakazují. Plán tedy není ani "avataři v1 nejsou", ani "avataři mají gate"; je ve třetím, nejhorším stavu — mlčí.

**Riziko:** zdržení se zásahu, odstranění následku a přiměřené zadostiučinění (i peněžité) podle OZ; u zaměstnance navíc pracovněprávní spor; kumulativně sankce podle AI Act (až 15 mil. EUR / 3 % obratu) a platformní enforcement (YouTube výslovně jmenuje "digital face replacement" jako spouštěč, C7 §2.5).

**Požadovaná náprava:**
1. Buď (a) do §5.3 doplnit tvrdé pravidlo *v1 nevytváří ani nepoužívá synteticky vytvořeného či upraveného lidského presentéra ani klonovaný hlas; `motion class: talking human` je v v1 vypnutá hodnota* — a zapsat to jako rozhodnutí do `DECISION_LOG.md`; **nebo** (b) implementovat celý gate z C7 §2.7.
2. Při volbě (b): povinný per-asset příznak `person-basis ∈ {wholly-synthetic, real-identifiable-person}` odvozený **nekonfigurovatelně** ze vstupů generace (referenční fotografie, voice-clone ID), a při hodnotě `real-identifiable-person` povinný odkaz na záznam souhlasu s rozsahem, dobou a platformami; chybějící odkaz = tvrdý blok publish-ready, ne varování.
3. Pro TTS: registr rout musí u každého hlasu nést `voice-basis ∈ {licensed-catalog, cloned-real-person}` a doklad licence; klonovaný hlas bez souhlasu = zakázaná routa.
4. Doplnit do §16 řádek "souhlas se zaměstnaneckou podobiznou / hlasem — samostatné podepsané ujednání, HR", pokud se varianta (b) kdy otevře.

**severity: blocker | section: §5.2/§5.3/§4.8 (media provider + routing contract) | claim: plan has no likeness/voice-consent gate and no wholly-synthetic-vs-real-person flag, while `motion class: talking human` and a free-form TTS "voice identity" knob keep synthetic presenters in v1 scope | required change: either explicitly disable synthetic human presenters and voice clones for v1 in a logged decision, or implement C7 §2.7's per-asset person-basis flag plus a scope-limited consent record as a hard publish-gate precondition, and add a `voice-basis` field to the model registry**

---

### [BLOCKER] B-2 · AI-content class je konfigurovatelný knob tématu — nosná kontrola čl. 50 se dá vypnout konfigurací, a její default nepokrývá generovaný zvuk

**Právní základ:** čl. 50 odst. 2 nařízení (EU) 2024/1689 — povinnost označení se vztahuje na syntetický **audio**, obraz, video *i* text; čl. 50 odst. 5 — sdělení nejpozději při první expozici. Účinnost 2026-08-02, sankce do 15 mil. EUR / 3 % obratu (C7 §2.4, ledger 27).

**Dotčené místo:** `ARCHITECTURE_PLAN.md` §3.3 (řádek 500: "One internal per-asset AI-content class drives every disclosure obligation"), §3.5 (řádek 529, výčet knobů) a zejména **§10.4 tabulka knobů**: *"AI-content class defaults and the AI-label-required flag | Which asset types are classed none, assisted or realistic-synthetic, driving both the burned-in disclosure and the manual platform-native label | **Default: Realistic-synthetic for generated video and imagery**"*.

**Popis:** Dvě samostatné vady v jednom poli.

*(i) Konfigurovatelnost.* Pole, které pohání jedinou nosnou kontrolu compliance, je uvedeno jako **per-theme knob s defaultem**, tedy něco, co autor tématu může přenastavit. Tím se z tvrdé právní podmínky stává nastavení. Plán si přitom sám v §5.3 stanoví test umístění konfigurace ("if changing it would require touching more than one theme at once, it is global") a ve W3-01 pravidlo, že vše, co může *spend, publish or relax a threshold*, defaultuje na bezpečnou hodnotu. AI-content class oba testy nesplňuje: relaxuje compliance práh a je per-theme.

*(ii) Default pokrývá jen video a obraz.* Default zní "realistic-synthetic **for generated video and imagery**". Vynechává generovaný **zvuk** — a to trefuje přesně český výchozí recept **CS-B** (§4.5, §4.8): *"naše vlastní typografie, česká TTS nebo titulky plus hudební podklad, a **žádný generativní video model v celé smyčce**"*. Asset, jehož jediným AI prvkem je syntetický hlas, se pod tímto defaultem legitimně klasifikuje jako `none`/`assisted` — a vypálený disclosure se nespustí. Jde o **výchozí produkční cestu pro celý český výstupní set**, tedy o největší objem assetů v pipeline. Čl. 50 odst. 2 přitom syntetické audio jmenuje výslovně.

**Požadovaná náprava:**
1. AI-content class **odstranit z per-theme knobů** a přesunout na engine level jako **odvozené** pole: hodnota se počítá z generačního záznamu (renderovala generativní routa pixely? renderovala TTS/hudební routa zvuk?), nikoli z konfigurace. Konfigurace smí třídu jen zpřísnit, nikdy zmírnit (monotónní pravidlo, stejné jako u hard excludes v §6.3).
2. Default a odvozovací pravidlo přeformulovat na *"realistic-synthetic pro každý asset, jehož jakákoli obrazová, zvuková nebo pohybová složka byla vygenerována modelem — **včetně syntetického hlasu**"*.
3. Do §17 Phase 3 doplnit akceptační kritérium: *asset s TTS hlasem a bez jediného generativního video klipu nese vypálený disclosure*.

**severity: blocker | section: §3.3 + §10.4 (AI-content class knob) | claim: the field driving the load-bearing Art. 50 control is a per-theme configuration knob whose default ("realistic-synthetic for generated video and imagery") omits AI-generated audio, so the Czech default recipe CS-B — TTS voice, no generative video model — can legally class as non-synthetic and skip the burned-in disclosure | required change: make AI-content class an engine-level field derived from the generation record (config may only tighten, never relax), extend the derivation to synthetic speech and music, and add a Phase-3 acceptance test for a TTS-only asset**

---

### [BLOCKER] B-3 · Rung 3 (local-only staging) obchází publish gate konstrukčně — platformní AI-labely se na garantované cestě nevynucují

**Právní základ:** smluvní (nikoli zákonná) rovina — TikTok AIGC disclosure, YouTube "altered or synthetic content" (automatická detekce od května 2026, sankce až odebrání a suspendace v Partner Programu), Meta "AI Info" (C7 §2.5). Sekundárně čl. 50 odst. 4 AI Act u assetů typu deep fake.

**Dotčené místo:** `ARCHITECTURE_PLAN.md` §7.2 (žebřík, rung 3), §7.4 (jediný vynucovací bod), §7.7 (potvrzení labelu), §17 Phase 6.

**Popis:** §7.4 definuje publish gate jako *"Before any distribution-prep call reaches the publishing bridge…"* — gate visí na volání mostu. Rung 3 je definován jako *"local-only staging … **with no call to the publishing bridge at all**"*. Publish gate se tedy na rungu 3 **nespouští vůbec**, včetně kontroly zaznamenaného potvrzení AI-labelu podle §7.7.

To by byl teoretický problém, kdyby byl rung 3 okrajový. Není. §7.2 a §7.4 mu dávají tři role: (a) garantovaná podlaha nezávislá na dostupnosti mostu; (b) cesta pro **každou destinaci, kterou operátor nepřipojil**; (c) — a to je nejostřejší — *"for any run where the publish gate (§7.4) **blocks a destination outright**"*. Poslední role znamená, že když gate zablokuje, obsah stejně skončí v packu ve formě připravené k ručnímu vložení. Operátor pak publikuje **ručně, mimo gate**, přesně na těch platformách, které mají vlastní labelovací mechaniku. A protože OP-2 zatím nechává rung 1 neověřený, plán sám v §7.8 říká, že *"rungy 2 a 3 jsou stejně nosné, ne jen teoretické"*.

Poctivě: **vypálený disclosure tím ohrožen není** — ten je podmínkou stavu publish-ready už na úrovni assembly/packagingu (§4.4, Phase 3), takže expozice podle čl. 50 zůstává krytá. Poškozeno je (a) tvrzení F-4/D-23 o *jediném* fail-closed vynucovacím bodě, které v tomto scénáři neplatí, a (b) celá vrstva platformních smluvních labelů, u nichž W2-05 identifikuje jako hlavní failure mode právě to, že je zaneprázdněný operátor přeskočí.

**Požadovaná náprava:**
1. Přesunout AI-label acknowledgement z publish gate na **packaging**: žádný asset s `AI-content class ≠ none` se nedostane do rungu 3 bez vytištěného, samostatně odškrtávaného řádku "platform-native label required for: TikTok / YouTube / Meta / LinkedIn (per-post line)" v samotném souboru určeném k ručnímu vložení.
2. §7.4 přeformulovat: gate je *"před jakoukoli přípravou obsahu k distribuci"*, ne *"před voláním mostu"*.
3. Do §17 Phase 6 doplnit akceptační kritérium: *asset, kterému gate zablokuje destinaci, dorazí do rungu 3 s viditelným, nezaškrtnutým label-checklistem — nikoli jako čistý text k vložení*.

**severity: blocker | section: §7.2 rung 3 vs §7.4 publish gate | claim: rung 3 (local-only staging for manual paste) makes no call to the publishing bridge and therefore never triggers the publish gate, so the separately-recorded AI-label acknowledgement (§7.7, W2-05) is silently skipped on the one path that is always available and is explicitly the destination for gate-blocked content | required change: move the AI-label acknowledgement to packaging so it travels with the rung-3 artefact as an unchecked per-platform checklist, restate §7.4's trigger as "before any distribution preparation" rather than "before any bridge call", and add a Phase-6 acceptance test for a gate-blocked asset reaching rung 3**

---

### [BLOCKER] B-4 · Provenance / license snapshot je v D-20 označen za podmínku publish gate, ale mezi kontrolami §7.4 chybí

**Právní základ:** C7 §2.8 — *"An asset missing this record should fail the 'ready to publish' gate — **treat as a hard block, not a warning**"*, protože u routerů této třídy (OpenRouter eff. 2026-07-29, Replicate eff. 2026-04-01, oba fetchnuty přímo) drží upstream poskytovatel modelu **práva třetí osoby oprávněné ze smlouvy** a může vymáhat přímo proti zákazníkovi, zatímco router se své odpovědnosti zříká.

**Dotčené místo:** `DECISION_LOG.md` D-20 ("Per-asset provenance record **is a publish-gate precondition**") vs. `ARCHITECTURE_PLAN.md` §7.4 bod 3, §11.3 (fail-closed triggers), §12.2 (obsah packu), Appendix A (výčet kontrol gate).

**Popis:** §7.4 vyjmenovává, co publish gate kontroluje: (1) destinace v allowlistu aktivního režimu, (2) destinace skutečně připojena, (3) zaznamenaný stav lidského schválení, (4) potvrzení AI-labelu u assetů vyžadujících disclosure. **Úplnost provenance recordu mezi nimi není.** Stejný výčet se opakuje v Appendix A (řádek 2331) — opět bez provenance. §11.3 mezi fail-closed triggery provenance rovněž nejmenuje. §12.2 provenance record do packu ukládá, ale uložení není kontrola.

Plán tedy sbírá přesně ty čtyři položky, které C7 §2.8 požaduje (delivered route identity + version, timestamp, snapshot licenčních podmínek k okamžiku generace, transaction id) a správně je řeší **po dokončení**, ne při submitu (D-20, W2-03) — to je silné. Chybí poslední článek: nikde není napsáno, že *neúplný záznam blokuje*. Za běhu to znamená, že asset po tiché substituci modelu (W2-03), u kterého se rights class nepodařilo dořešit, projde.

Druhá, tíže opravitelná vrstva: §5.2 registr nese `license class` a `last-verified date`. **Třída není snapshot.** A protože C7 §2.8 celý postoj staví na tom, že *"the weakest link is always the specific upstream model"*, snapshot pořízený z routerovy vlastní stránky nedokládá **upstream** grant. Plán nemá pravidlo, co dělat, když upstream podmínky nelze získat — což je přesně situace, kterou C7 ledger ř. 35 dokumentuje u samotného Kie.

**Požadovaná náprava:**
1. Doplnit do §7.4 pátou kontrolu a do §11.3 pátý fail-closed trigger: *provenance record kompletní (všechny čtyři položky) a `rights class` delivered routy je v allowlistu rights-class pro cílovou destinaci*; jinak fail-closed pro daný asset.
2. Registr rout (§5.2) rozšířit o **dvě** licenční pole: reprezentace routeru a **URL + datum vlastních podmínek upstream poskytovatele modelu**. Kde upstream není ověřitelný, `rights class` **defaultuje na nejpřísnější hodnotu** (`reseller-uninsured`, případně `forbidden`) — nikoli na hodnotu deklarovanou routerem.
3. Do §17 Phase 3 doplnit akceptační kritérium: *asset s uměle poškozeným provenance recordem nedosáhne publish-ready*.

**severity: blocker | section: §7.4 + §11.3 vs DECISION_LOG D-20 | claim: D-20 records the per-asset provenance/licence snapshot as a publish-gate precondition, but §7.4's enumerated gate checks, §11.3's fail-closed triggers and Appendix A's replay all omit it, so C7 §2.8's "hard block, not a warning" is not implemented at the single enforcement point; separately, the registry stores a licence *class* and the router's own representation rather than an upstream-model licence snapshot | required change: add provenance completeness and delivered-route rights-class as an explicit publish-gate check and fail-closed trigger, add an upstream-provider terms URL+date field to the model registry, default rights class to the most restrictive value when the upstream terms are unverifiable, and add a Phase-3 negative test**

---

### [BLOCKER] B-5 · Trvalá retence doslovných výňatků a odkazů v run packu popírá vlastní extract-first pravidlo a znemožňuje výmaz

**Právní základ:** čl. 5 odst. 1 písm. c) a e), čl. 17 a čl. 21 GDPR; C7 §2.6 (*"default to a short, bounded retention window for verbatim raw text … keep de-identified derived signals … indefinitely **instead of** the original text/username"*) a stanovisko ÚOOÚ citované v C7: *"veřejnost údajů neznamená možnost jejich dalšího bezmezného zpracování"*.

**Dotčené místo:** `ARCHITECTURE_PLAN.md` §2.6 (tabulka artefaktů, řádek *Provenance snapshot*), §12.2 (obsah packu, odrážka "source links and extraction notes for every signal"), §17 Phase 1 (akceptační kritérium výmazu).

**Popis:** §2.6 stanoví čtyři retenční okna (raw payload 30 dní, normalizovaný záznam 90 dní, request log 12 měsíců, curated-inbox verbatim 30 dní s hashovanými klíči) — to je poctivá implementace C7. Pátý řádek ji ale ruší:

> **Provenance snapshot | Always, permanent with the pack | Canonical link, *the minimal quoted excerpt that triggered candidacy*, retrieval time, method | Retained with the run pack**

a odůvodnění zní: *"it carries links and excerpts, not payloads, precisely so pack retention does not fight source-data retention"*. To je **věcně chybná úvaha**: z hlediska GDPR nerozhoduje velikost. Doslovný výňatek Redditího komentáře plus jeho kanonický permalink je přímý ukazatel na identifikovatelnou fyzickou osobu a je jím i po 30 dnech, kdy má být verbatim text z curated inboxu smazán. §12.2 to ještě rozšiřuje: pack navíc trvale nese *"source links and extraction notes for **every signal** that fed the topic"*. Výsledek: architektura, která si nastavila 30denní okno na doslovný text, si zároveň ukládá ten samý doslovný text natrvalo v jiném souboru.

Druhá polovina nálezu: §2.6 slibuje *"targeted deletion by canonical key from day one"* a Phase 1 to testuje jako *"targeted deletion by canonical key works on a real stored record"*. Nikde ale není řečeno, že mazání **dosáhne do archivovaných run packů**. Pack je popsán jako statický soubor ve složce běhu (§12.1, R-29). Bez indexu pack → kanonický klíč není námitka podle čl. 21 ani výmaz podle čl. 17 vykonatelný — a to je přesně ten scénář, kvůli kterému C7 §2.6 doporučuje strukturované dotazovatelné záznamy místo monolitů.

**Požadovaná náprava:**
1. Rozdělit provenance snapshot na dvě části: **trvalou** (kanonický klíč = hash, zdroj, metoda, čas, doména — bez doslovného textu a bez přímého permalinku na uživatelský příspěvek) a **časově omezenou** (doslovný výňatek + permalink), na stejném 30denním hodinovém strojku jako curated-inbox verbatim; po expiraci se v packu nahradí zástupným textem "výňatek expiroval, kanonický klíč X".
2. Zavést **index run pack → kanonické klíče**, aby cílené mazání dosáhlo i do archivovaných packů; §17 Phase 1 rozšířit o akceptační kritérium *"cílené mazání odstraní záznam i z již zabaleného, archivovaného packu"*.
3. Odstranit z §2.6 odůvodnění "links and excerpts, not payloads" — je to nesprávný právní test a v auditu by se obrátil proti nám.

**severity: blocker | section: §2.6 (artifact table, provenance snapshot row) + §12.2 | claim: the provenance snapshot is retained permanently with the run pack and explicitly contains the verbatim quoted excerpt and the canonical link, plus §12.2 keeps per-signal source links forever — which nullifies the 30-day verbatim window set three rows above and leaves Art. 17/21 unexecutable because targeted deletion has no stated path into archived packs | required change: split the provenance snapshot into a permanent de-identified part and a 30-day verbatim/permalink part, add a run-pack → canonical-key index so targeted deletion reaches archived packs, extend the Phase-1 acceptance test accordingly, and delete the "links and excerpts, not payloads" justification**

---

## 2. Nálezy — MAJOR

### [MAJOR] M-1 · Chybí filtrace zvláštních kategorií údajů, kterou C7 §2.6 výslovně požaduje

**Právní základ:** čl. 9 GDPR; pokyny EDPB k web scrapingu v kontextu generativní AI, podle C7 přijaté 2026-07-07 (C7 vede přesné číslo pokynu jako **neověřené** — viz M-9): scrapovaný sociální obsah *"can residually capture special-category data (political opinion, health, sexual orientation implied by community/subreddit context)"* a očekává se **filtrace před sběrem i po něm**.

**Dotčené místo:** §2.7 (binary veto list), §2.6 (design consequences).

**Popis:** Veto list v §2.7 obsahuje: *legal and claim-risk topics, competitor disparagement, high-severity controversy, detected manipulation, prompt-injection phrasing*. To je **brand-risk filtr, ne filtr podle čl. 9**. Jde o odlišnou logiku: subreddit o duševním zdraví nebo komunita definovaná zdravotním stavem či sexuální orientací nemusí být "high-severity controversy" a přesto z něj uložený výňatek nese údaj podle čl. 9. Zpracování takového údaje bez výjimky podle čl. 9 odst. 2 je zakázané — oprávněný zájem podle čl. 6 odst. 1 písm. f) sám o sobě nestačí. C7 tuto filtraci jmenuje v rámci nálezu se závažností **blocker (without a documented LIA)** a plán z něj implementoval LIA i privacy notice, ale filtraci ne.

**Náprava:** doplnit do §2.6 pátý design consequence a do §2.7 samostatnou vetovou třídu: **zdrojová a obsahová filtrace zvláštních kategorií** — (a) deny-list zdrojů/komunit definovaných charakteristikou podle čl. 9, uplatněný před sběrem, (b) deterministická lexikální kontrola nad uloženým výňatkem po sběru, se selháním do "nesbírat / smazat", nikoli do "označit". Rozhodnutí zapsat do `DECISION_LOG.md`, protože jde o obsahovou politiku, ne o technický detail.

**severity: major | section: §2.6 + §2.7 (veto list) | claim: the binary veto list is a brand-risk filter and contains no Art. 9 special-category exclusion, although C7 §2.6 explicitly requires pre- and post-collection filtering because community context can residually carry health, political-opinion or sexual-orientation data that legitimate interest alone cannot lawfully cover | required change: add a source-level deny-list for communities defined by an Art. 9 characteristic applied before collection, plus a deterministic post-collection check over stored excerpts, both failing to "do not store / delete" rather than to "flag"**

---

### [MAJOR] M-2 · Výjimka podle čl. 50 odst. 4 je v §3.3 prohlášena za splněnou "by design", ale plán nikde nezaznamenává, kdo nese redakční odpovědnost

**Právní základ:** čl. 50 odst. 4 písm. b) nařízení (EU) 2024/1689 — povinnost odpadá u textu, který *"prošel procesem lidského přezkumu nebo redakční kontroly **a fyzická nebo právnická osoba nese redakční odpovědnost**"* (citováno v C7 §2.4). C7 zároveň řadí rozsah této výjimky mezi **odložená rozhodnutí vyžadující kvalifikovaného poradce**.

**Dotčené místo:** §3.3, řádek Blog: *"the text limb of the transparency obligation has a human-editorial-review carve-out **our workflow satisfies by design**"*; §11.4 (review-decision store).

**Popis:** Dvě vady. Za prvé **tón**: C7 tuto výjimku popisuje jako nepotvrzenou a jako otevřenou otázku pro poradce; plán ji uvádí jako splněnou konstatováním. To je přesně ředění právního závěru, které mám hledat. Za druhé **substance**: výjimka má dvě podmínky, ne jednu. Plán splňuje první (lidský přezkum je povinný a zaznamenaný v review-decision store), ale review-decision store podle §11.4 drží *"one reason-coded approve/reject/partial decision per asset, keyed by run id and asset id"* — **nedrží identitu osoby**, která rozhodnutí učinila, ani prohlášení o redakční odpovědnosti. U jednoho operátora to působí formalisticky; při obhajobě před dozorem je to rozdíl mezi doložitelnou a nedoložitelnou výjimkou, a v okamžiku, kdy přibude druhý operátor nebo druhý tenant, je to rozdíl podstatný.

**Náprava:** (1) přeformulovat buňku v §3.3 na *"pracovní posouzení je, že náš workflow splňuje výjimku podle čl. 50 odst. 4 písm. b); rozsah výjimky je otevřená otázka pro kvalifikovaného poradce (C7, odložená rozhodnutí)"*; (2) doplnit do review-decision store pole **identita schvalující osoby** a per-asset příznak `editorial-responsibility-held-by`; (3) přidat řádek do §16 (viz M-9).

**severity: major | section: §3.3 (Blog row, AI-label mechanics) + §11.4 | claim: the plan asserts the Art. 50(4) human-editorial-review carve-out is "satisfied by design", although C7 flags its scope as an unresolved question for qualified counsel, and the review-decision store records only a reason-coded decision per asset — not the identity of the natural or legal person holding editorial responsibility, which is the carve-out's second, independent condition | required change: downgrade the §3.3 wording to a working assessment with a named counsel dependency, and add an approver-identity plus `editorial-responsibility-held-by` field to the review-decision store**

---

### [MAJOR] M-3 · Text, umístění a trvání vypáleného disclosure jsou per-theme knob bez engine-level minima

**Právní základ:** čl. 50 odst. 5 nařízení (EU) 2024/1689 — sdělení musí být poskytnuto *"jasným a rozlišitelným způsobem **nejpozději v okamžiku první interakce nebo expozice**"* a musí splňovat **požadavky na přístupnost** (C7 §2.4).

**Dotčené místo:** §10.4: *"Disclosure overlay text and placement per language | The exact burned-in wording and where it sits | Per language; mandatory | §4.4, §14.6"*; §4.4 (poslední odrážka); §14.6.

**Popis:** Plán správně stanoví, **že** disclosure musí být vypálený, a učiní z toho podmínku publish-ready. Nestanoví ale **jak vypadá**: chybí minimální doba zobrazení, umístění v čase (§4.4 rozebírá umístění CTA a end-cardu do detailu sekund, disclosure neumisťuje vůbec), minimální velikost/kontrast, chování v safe-boxu, jazyk (cs/en), a **slyšitelný ekvivalent u audio-nesoucích assetů**. Přístupnost podle čl. 50 odst. 5 není zmíněna nikde v dokumentu. Za současného znění lze knob nastavit na šedý osmibodový text na end-cardu v poslední půlsekundě a plán je formálně splněn, zatímco "nejpozději při první expozici" splněno není.

Argument pro umístění je vnitřní: podle testu v §5.3 patří na engine level cokoli, co by se jinak měnilo ve více tématech naráz; podle W3-01 vše, co může relaxovat práh, musí defaultovat bezpečně. Minimální podoba disclosure obojímu vyhovuje.

**Náprava:** do §4.4 doplnit **engine-level podlahu** (mandát, ne knob): disclosure viditelný **od první sekundy** assetu, po celou dobu nebo minimálně po definovaný nezkrátitelný interval, uvnitř univerzálního safe-boxu, s minimálním poměrem výšky písma k výšce rámu a minimálním kontrastem; slyšitelné oznámení u assetů, kde je nosným kanálem zvuk; znění v jazyce assetu. Per-theme knob smí podlahu pouze **zpřísnit**. Do §17 Phase 3 doplnit měřený akceptační test (stejné povahy jako už existující loudness gate).

**severity: major | section: §4.4 + §10.4 (disclosure overlay knob) | claim: the burned-in disclosure's wording, placement, duration, contrast and audible equivalent are a per-theme knob with no engine-level minimum, and Art. 50(5)'s "at the latest at the time of first exposure" plus its accessibility requirement appear nowhere, so a compliant-looking configuration can still fail the article | required change: define an engine-level, non-relaxable disclosure floor in §4.4 (visible from the first second, minimum duration, minimum type-height ratio and contrast, inside the safe box, audible equivalent for audio-led assets, language of the asset) that themes may only tighten, and add a measured Phase-3 acceptance test alongside the existing loudness gate**

---

### [MAJOR] M-4 · Obrazové assety nemají pojmenovaný krok vypálení disclosure ani kontrolní bod v revizi

**Právní základ:** čl. 50 odst. 2 nařízení (EU) 2024/1689 — obraz je samostatně jmenovaná modalita.

**Dotčené místo:** §4.4 (assembly = video stage), §3.2 (produkované typy assetů), §3.5 (tabulka hloubky revize), §12.2.

**Popis:** §14.6 deklaruje disclosure *"applied during assembly"* pro video, obraz i zvuk. §4.4 ale popisuje assembly jako video stage (stitching klipů či slidů, titulky, ducking, loudness, safe zones, end card). §3.2 přitom produkuje i **čistě obrazové assety**: feed stills 1080×1350, Instagram carousel, LinkedIn document carousel jako PDF (5–15 slidů), blogové hero a doprovodné vizuály. Pro ty není nikde pojmenován renderovací/kompozitní krok, ve kterém by se overlay vypálil. Potvrzuje to §3.5: kontrolní položka *"burned-in disclosure present"* je uvedena **pouze u řádku Short video / Reel / Short / slideshow** — u řádků Carousel a Blog article chybí. U document carouselu (PDF) je navíc otázka, na kterých stranách má disclosure být; při "první expozici" to musí být minimálně první strana.

**Náprava:** (1) v §4.4 (nebo novém §4.4a) pojmenovat kompozitní krok pro statické assety a přiřadit mu vypálení disclosure a podpis C2PA po finálním exportu, symetricky s videem; (2) doplnit "burned-in disclosure present" do řádků Carousel/document carousel a Blog article v §3.5; (3) u vícestránkových assetů stanovit disclosure na první straně/slidu a na koncovém.

**severity: major | section: §4.4 + §3.5 (review depth table) | claim: the burned-in-disclosure step is described only inside the video assembly stage, while §3.2 also produces image-only assets (feed stills, Instagram carousels, LinkedIn document carousels, blog hero and supporting visuals) that have no named compositing step, and §3.5 lists "burned-in disclosure present" only in the video row | required change: name a static-asset compositing stage that applies the disclosure overlay and signs C2PA after final export, add the disclosure checkpoint to the carousel and blog rows of §3.5, and require the disclosure on the first and final slide of multi-page assets**

---

### [MAJOR] M-5 · OD-17 slučuje dva různé právní problémy a plánuje právní čtení až po zkušebním provozu a po prvním výdaji

**Právní základ:** C7 §2.3 (Google) — třetí strana prodávající SERP/Trends data *"has itself accepted Google's ToS risk on your behalf — **that is a documented vendor-risk decision to make explicitly if pursued, not a default-safe shortcut**"*, na pozadí žaloby Google vs. SerpApi z roku 2026 (C7 ledger ř. 23) a Google ToS účinných 2026-07-30 (ř. 20, přímý fetch). C7 §2.4 rule-one analogie: transport nepere metodu.

**Dotčené místo:** §2.4 (rule one), §16 OD-17, `RISK_LOG.md` W2-18, `DECISION_LOG.md` W2.5-3 (Virlo Starter $49/mo + DataForSEO ~$10–15/mo).

**Popis:** Dvě vady.

*(i) Sloučení.* OD-17 mluví o "derived-analytics vendors ... (Virlo class)" jako o jedné třídě. Právně to jedna třída není. **Virlo** prodává odvozené analytiky z TikTok/IG/YT, kde podle W2-18 neexistuje žádný licenční program — problém je neznámý upstream. **DataForSEO** prodává SERP/Trends data, kde upstream **je** znám (Google), jeho ToS byly přímo staženy a jeho porušování je předmětem aktivního sporu. To je jiná rizikovka: nejde o "nevíme, odkud to mají", ale o "víme, odkud to mají, a víme, že to protistrana žaluje". Plán navíc DataForSEO adoptoval jako *default bez uživatelského gate* (`DECISION_LOG.md`, ř. 46).

*(ii) Načasování.* OD-17 určuje rozhodovací bod jako *"Operator plus counsel, **before any vendor subscription renews beyond the trial**"*. To je po zkušebním týdnu, tedy až poté, co už data tekla do pipeline a peníze odešly. Zároveň §2.4 rule one podmiňuje přijatelnost MCP zdroje tím, že vendor prodává analytiky *"under terms that permit pipeline use"* — ale nikde v plánu (ani v Phase 0) není úkol **přečíst podmínky vendora a ověřit, že pipeline use skutečně povolují**. Phase 0 čte ToS routeru; ToS vendorů ne.

**Náprava:** (1) rozdělit OD-17 na **OD-17a (Virlo / neznámý upstream)** a **OD-17b (DataForSEO / známý upstream v aktivním sporu)** a posoudit každý samostatně; (2) přesunout právní čtení **před** první kredit­ový výdaj, tj. do Phase 0, se stejným statusem jako manuální stažení ToS routeru; (3) doplnit do Phase 0 deliverable: *"podmínky každého licencovaného vendora staženy, datovány a ověřeny v bodu 'povoluje pipeline/derivativní použití a další zpracování zákazníkem'; výsledek zaznamenán ve vendor rosteru vedle last-verified/recheck-by"*; (4) v §2.4 nahradit tvrzení *"under terms that permit pipeline use"* povinností to doložit, ne předpokládat.

**severity: major | section: §2.4 rule one + §16 OD-17 | claim: OD-17 merges an unknown-upstream vendor (Virlo) with a known-upstream, actively-litigated one (DataForSEO/Google SERP), and schedules the legal reading only "before any subscription renews beyond the trial" — i.e. after the trial has already ingested data and spent money — while §2.4's premise that the vendors sell analytics "under terms that permit pipeline use" is nowhere verified | required change: split OD-17 into two decisions, move the legal reading into Phase 0 with the same status as the manual router-ToS pull, and add a Phase-0 deliverable requiring each licensed vendor's terms to be retrieved, dated and checked for a pipeline/derivative-use permission recorded in the vendor roster**

---

### [MAJOR] M-6 · Rozpoznatelnost reklamy jako reklamy (C7 §2.9, závažnost major) nemá v claim-gate žádnou kontrolu

**Právní základ:** podle C7 §2.9 zákon č. 40/1995 Sb., o regulaci reklamy — požadavek, aby reklama byla zřetelně rozpoznatelná a nebyla skryta jako jiný obsah. **Pozor:** C7 tuto citaci sám vede jako **low-medium confidence / recheck**, protože primární text nebyl dostupný. Nález proto zní "chybí kontrola", nikoli "porušujeme konkrétní paragraf".

**Dotčené místo:** §6.7 třída 10 (Required-statement), §6.3 F-N (Compliance obligations), §10.4 knob "Compliance obligations", §5.8.

**Popis:** Plán implementoval **druhou** odrážku C7 §2.9 (klamavá a neověřitelná tvrzení) vzorně: jedenáct kontrolních tříd, pět z nich nesmí být vypnuto právě proto, že jejich selhání je právní expozice, a per-asset claim-check log je výslovně označen za regulatorní důkazní stopu (§6.7, ř. 1038). **První** odrážku neimplementoval. Třída 10 vyjmenovává *"affiliate or discount disclosure, entity disclosure, AI-content labelling"* — affiliate disclosure tedy existuje, ale:

- nikde není definován **katalog povinných prohlášení** (jaké přesné znění, v jakém jazyce, pro kterou destinaci, kdo jej udržuje); knob "Compliance obligations" je jen enablement flag;
- nikde není mapování na **platformní nástroje pro placenou spolupráci / branded content** (Meta branded content, TikTok branded-content toggle, YouTube "paid promotion"), přestože §3.3 obdobné mapování pro AI-labely pečlivě vede;
- §5.8 zmiňuje pro pozdější placenou fázi "separate mandatory ad-disclosure control", ale míní tím **AI disclosure v reklamě**, ne rozpoznatelnost reklamy.

Pro čistě organický obsah na vlastních účtech značky je reálné riziko nízké. Riziko vzniká přesně tam, kde plán sám říká, že vzniká: *"The affiliate arrangement in the real strategy triggers this"* (§6.7, jazykové specifikum třídy 10).

**Náprava:** (1) rozšířit třídu 10 o podtřídu **rozpoznatelnost komerčního sdělení** s katalogem povinných formulací per (jazyk × destinace × typ vztahu: vlastní / affiliate / placená spolupráce); (2) doplnit do §3.3 sloupec nebo poznámku s platformní mechanikou paid-partnership per destinace, symetricky k AI-labelům; (3) přidat do §16 řádek "ověřit primární text zákona o regulaci reklamy a zákona o ochraně spotřebitele" (viz M-9).

**severity: major | section: §6.7 check class 10 + §3.3 | claim: C7 §2.9's first bullet — advertising must be recognisable as advertising — has no control anywhere; check class 10 names affiliate disclosure but no catalogue defines the mandatory wording per language and destination, and unlike the AI-label mechanics there is no mapping to platform paid-partnership/branded-content controls | required change: extend class 10 with a commercial-communication-recognisability sub-class backed by a per-language, per-destination, per-relationship statement catalogue, add a paid-partnership mechanics column to §3.3, and log the Czech statute confirmation as an open item**

---

### [MAJOR] M-7 · Příjemci a předávání osobních údajů: čl. 28 a hlava V GDPR nejsou v plánu vůbec, a Phase 0 nespecifikuje obsah privacy notice

**Právní základ:** čl. 13 odst. 1 písm. e) a f), čl. 28, čl. 44–49 GDPR. **Mezera důkazního balíčku:** C7 tuto oblast neřeší vůbec (žádný z 37 řádků ledgeru se netýká zpracovatelských smluv ani mezinárodního předávání). Nález proto formuluji jako *neposouzenou oblast s povinným krokem*, nikoli jako zjištěné porušení.

**Dotčené místo:** §2.8 (kolektovaný text vstupuje do ranking/spin/copy promptů), §5 (router, TTS), §2.3 (MCP vendoři), §17 Phase 0 (deliverable "published privacy notice").

**Popis:** Textové vyhledávání napříč celým plánem vrací **nulu** pro *processor*, *sub-processor*, *DPA*, *third country*, *SCC*, *Data Privacy Framework*, *data subject*, *special category*. Přitom §2.8 explicitně říká, že *"All collected text will later sit inside ranking, spin and copy prompts"* — a §2.6 stejně explicitně říká, že tento text **je osobní údaj**. Osobní údaje tedy prokazatelně opouštějí systém směrem k LLM poskytovateli, k media routeru (Kie), k TTS poskytovateli (ElevenLabs / Azure) a k MCP vendorům. Plán o těchto tocích neříká, kdo je v jaké roli, ani kde fyzicky končí.

Druhá polovina: Phase 0 má jako deliverable *"the published privacy notice produced as a company artefact"* a jako gate pouze *"Both privacy artefacts exist"*. Existence ale není obsah. Privacy notice musí podle čl. 13 nést mimo jiné **kategorie příjemců** a **informaci o předávání do třetích zemí včetně záruk** — což nelze sepsat, dokud výše uvedená mapa toků neexistuje.

**Náprava:** (1) doplnit do §2.6 (nebo nové §2.6a) **mapu příjemců**: pro každého externího poskytovatele, kterému může projít text pocházející ze sběru, uvést roli (zpracovatel / samostatný správce), zda existuje zpracovatelská smlouva, a zda jde o předání mimo EHP; (2) rozšířit Phase-0 akceptační kritérium z "artefakty existují" na "privacy notice obsahuje kategorie příjemců a informaci o předávání, a mapa příjemců je odsouhlasena"; (3) jako levnou technickou mitigaci zvážit **redakci autorských identifikátorů a permalinků z promptů** — do promptu má jít téma a výňatek, ne uživatelské jméno; (4) předložit poradci jako samostatnou otázku, protože C7 k ní nemá důkaz.

**severity: major | section: §2.6 + §2.8 + §17 Phase 0 | claim: collected personal data demonstrably leaves the system into LLM, media-router, TTS and MCP-vendor calls, yet the plan contains no processor/controller mapping, no processing-agreement position and no third-country-transfer position (zero occurrences of processor, DPA, SCC, third country), while Phase 0 gates only on the privacy notice "existing" rather than on its Art. 13 mandatory content; C7 provides no evidence on this area at all | required change: add a recipient map covering every external provider that can receive collected text (role, processing agreement, EEA/third country), upgrade the Phase-0 acceptance criterion to cover the notice's recipient and transfer sections, redact author handles and permalinks from prompt payloads, and refer the area to counsel as an evidence gap**

---

### [MAJOR] M-8 · "Reddit Pro" je jiná mitigace než ta, kterou C7 posoudil, a jeho podmínky nikdo neplánuje přečíst

**Právní základ:** C7 §2.1, možnost 3 — schválená mitigace zní: *"an operator reads Reddit **in an ordinary browser session** and manually writes summaries/observations"*, a to výslovně proto, že Redditova omezení míří na *automated/bulk/commercializing use of its data feed*. Responsible Builder Policy zakazuje *"sell, license, share, or otherwise commercialize Reddit data without express written approval"* (C7 §2.1, Medium confidence, přímý fetch blokován).

**Dotčené místo:** §2.3 (řádek Reddit: *"Reddit's own free business tool plus manual thread curation"*), `DECISION_LOG.md` W2.5-2 a D-09, §17 Phase 0.

**Popis:** Plán i DECISION_LOG zavádějí **Reddit Pro** — Redditův vlastní byznysový analytický nástroj. C7 tento produkt nikde nezmiňuje a neposoudil ho. Rozdíl není kosmetický: čtení veřejné stránky prohlížečem a **odběr odvozených analytik z byznysového nástroje s vlastními podmínkami** jsou dvě různé právní situace. Reddit Pro je pravděpodobně v pořádku — je to produkt určený firmám a jeho komerční užívání je jeho zamýšlené použití — ale to je domněnka, ne doklad, a plán ji nikde nevyslovuje ani neověřuje.

Nekonzistence je zřetelná ve srovnání: u routeru plán zaujal správný postoj *"terms unread → manual browser pull is a build-sign-off prerequisite"* (W2-12, R-27, Phase 0). U Reddit Pro, kde je právní posouzení C7 rovněž neúplné, stejný krok chybí.

**Náprava:** doplnit do Phase 0 deliverable a akceptačního kritéria: *"podmínky Reddit Pro (a případné podmínky Reddit User Agreement pro byznysový účet) staženy ručně v prohlížeči, datovány a přečteny v bodě: povoluje se komerční využití odvozených výstupů nástroje mimo Reddit"* — stejnou formou jako u ToS routeru. Zároveň v §2.3 explicitně napsat, že se z Reddit Pro **neexportují** data hromadně a že výstupem je operátorova poznámka.

**severity: major | section: §2.3 (Reddit row) + §17 Phase 0 | claim: the plan's Reddit mitigation is "Reddit Pro plus manual thread curation", but C7's assessed and approved mitigation was reading Reddit in an ordinary browser session; Reddit Pro is a separate product with its own terms that C7 never evaluated and that Phase 0 does not schedule anyone to read, unlike the router's ToS | required change: add a Phase-0 deliverable and acceptance criterion requiring a manual browser pull and dated reading of Reddit Pro's terms on the specific question of commercial use of the tool's derived outputs outside Reddit, and state in §2.3 that no bulk export from Reddit Pro occurs**

---

### [MAJOR] M-9 · Tři ze čtyř otevřených právních otázek C7 se do §16/§17 nedostaly

**Dotčené místo:** §16.2 (tabulka otevřených rozhodnutí), §16.3 (odložená s triggerem), §17 Phase 0.

**Popis:** C7 uzavírá osmi odloženými položkami. Kontrola jedna po druhé:

| C7 odložená položka | Stav v plánu |
|---|---|
| Placený komerční Reddit API kontrakt | ✅ §16.3, trigger = více platících tenantů |
| Automatizované X reads | ✅ §16.3, trigger = 4 týdny dat |
| **Rozsah výjimky čl. 50 odst. 4 u syntetického presentéra (deepfake limb)** | ❌ **chybí** v §16 i §17; §3.3 navíc tvrdí opak (viz M-2) |
| Ruční stažení ToS Kie.ai | ✅ Phase 0 deliverable + akceptační kritérium + R-27 |
| Existence licencovaného Reddit agregátora | ✅ implicitně vyřešeno — plán o něj nestaví |
| **Ověření primárního textu zák. 40/1995 Sb. a 634/1992 Sb.** | ❌ **chybí**; plán cituje "Czech consumer-protection law" dvakrát bez čísel a ověření neplánuje |
| Znovuotevření oficiální Google SERP/Trends API | ⚠️ částečně — §16.3 má "paid demand-axis upgrade" po 8 týdnech, ale to je kvalitativní, ne právní recheck |
| Přesný počet dní retence | ✅ OD-15, volba (a) s paralelním potvrzením poradcem |
| **Ověření čísla/data pokynu EDPB k web scrapingu** | ❌ **chybí**; přitom LIA (Phase 0) se o tyto pokyny bude opírat |

Tři chybějící položky spojuje to, že jsou to přesně ty, které C7 označil za nutné potvrdit **kvalifikovaným poradcem nebo proti primárnímu textu**. Plán si ponechal ty, které lze vyřešit vlastní silou.

**Náprava:** doplnit do §16.2 tři řádky se stejnou strukturou jako ostatní (možnosti / doporučení / kdo a kdy):
- **OD-24** — rozsah výjimky čl. 50 odst. 4 u syntetického presentéra: rozhodne poradce; do rozhodnutí platí "označovat vždy, nadměrné označení není sankcionováno" (C7 §2.4).
- **OD-25** — potvrzení primárního textu zák. 40/1995 Sb. a 634/1992 Sb. proti Sbírce zákonů: rozhodne poradce před spuštěním Phase 6; váže na M-6.
- **OD-26** — ověření identifikace pokynů EDPB k web scrapingu proti registru EDPB: **před** finalizací LIA v Phase 0, protože LIA je na nich postavena.

**severity: major | section: §16.2 + §17 Phase 0 | claim: of C7's deferred legal items, three are absent from both §16 and §17 — the Art. 50(4) carve-out scope for synthetic presenters, primary-text confirmation of the two Czech statutes, and verification of the EDPB web-scraping guideline reference — and these are precisely the items C7 marked as requiring qualified counsel or a primary-source check | required change: add OD-24, OD-25 and OD-26 to §16.2 with named decision points, and make OD-26 a Phase-0 prerequisite because the LIA rests on that guidance**

---

## 3. Nálezy — MINOR

### [MINOR] m-1 · Hashování autorských identifikátorů není specifikováno a napětí mezi minimalizací a vykonatelností námitky není vyřešeno

§2.6 říká *"minimised or hashed where needed for dedupe, never retained in clear text long-term"* a tabulka u curated-inbox verbatim uvádí *"hashed author keys"*. Nikde není řečeno (a) že hash je **pseudonymizace, nikoli anonymizace** — recitál 26 GDPR, což C7 §2.6 sám cituje; (b) že musí být **deterministický a reprodukovatelný**, jinak nelze námitku podle čl. 21 od konkrétní osoby vyřešit přehashováním jejího uživatelského jména; (c) že prostý hash uživatelského jména je slovníkově prolomitelný, takže má být klíčovaný (HMAC se samostatně drženým tajemstvím, jehož smazání je samo o sobě mitigací).

**severity: minor | section: §2.6 (author-handle handling) | claim: hashing of author handles is stated without specifying that it is pseudonymisation rather than anonymisation, that it must be deterministic so an Art. 21 objection can be resolved by re-hashing the handle, or that a bare hash of a low-entropy public username is dictionary-reversible | required change: specify a keyed, deterministic HMAC over author handles with the key held separately and its deletion documented as a mitigation, and state explicitly that hashed records remain personal data**

### [MINOR] m-2 · Výjimkový mechanismus pro Playwright nemá schvalovatele, kritéria ani povinnost záznamu

§2.4 ponechává Playwright jako *"a per-source, explicitly-approved future exception mechanism … entering through the method-evaluation gate"*. Kdo schvaluje, proti čemu se posuzuje (přečtené ToS? robots.txt? absence anti-bot obrany?) a kam se výsledek zapisuje, není nikde. Je to jediné místo, kde lze jinak velmi silný do-not-scrape postoj (§2.5, 10 položek, závazný ve všech režimech, včetně poctivě zaznamenaného protiargumentu z US judikatury) tiše zvrátit.

**severity: minor | section: §2.4 rule two (Playwright exception) | claim: the per-source Playwright exception mechanism names no approver, no assessment criteria and no logging obligation, leaving the only reversible point in an otherwise strong do-not-scrape posture undefined | required change: require that any exception be granted only against a dated reading of the source's terms and robots file plus evidence of no anti-bot defence, and be recorded as a numbered decision in DECISION_LOG.md**

### [MINOR] m-3 · Přijetí podmínek Meta Ad Library API není zaznamenaným artefaktem Phase 0

C7 §2.3 uvádí, že přístup k API vyžaduje **jak** ověření totožnosti vládním dokladem, **tak** přijetí Ad Library API terms jako podmínku přístupu. Phase 0 správně plánuje ověření totožnosti a evidenci expirace tokenu (W2-15, R-05), ale přijaté podmínky nikde neuchovává ani nedatuje.

**severity: minor | section: §17 Phase 0 (ad-library onboarding) | claim: Phase 0 covers the ID verification and token expiry for the Meta Ad Library API but not the acceptance of the Ad Library API terms, which C7 §2.3 names as a separate condition of access | required change: add the accepted Ad Library API terms, dated and stored, to the Phase-0 deliverables alongside the verification confirmation**

### [MINOR] m-4 · Kodex chování AI Office k transparentnosti a standardizovaná unijní ikona "AI" v plánu chybí

C7 §2.4 uvádí Code of Practice on Transparency of AI-Generated Content jako dobrovolný, ale zakládající **domněnku shody** pro signatáře, s vyvíjenou standardizovanou unijní ikonou "AI" a modalitně specifickým označováním, a označuje jeho status za **časově citlivý s naléhavým recheckem k 2026-09-01**. Plán jej nezmiňuje ani v §14.6, ani v tabulce "co shnije nejdřív" v §0.3. Pokud kodex ikonu standardizuje, změní se přesně to, co M-3 žádá definovat.

**severity: minor | section: §14.6 + §0.3 (fact-rot table) | claim: the AI Office Code of Practice on Transparency of AI-Generated Content and its forthcoming standardised EU "AI" label icon are absent from the plan, although C7 flags them as time-sensitive with a 2026-09-01 recheck and they carry a presumption-of-conformity benefit | required change: add the Code of Practice and the standardised icon to §14.6 and to the §0.3 fact-rot table with a dated recheck, and note that adopting the standard icon would replace the theme-level disclosure wording**

### [MINOR] m-5 · "Omnibus" — v C7 pro něj není žádný důkaz; postoj plánu je i tak správný

Zadání této revize žádá posouzení "časování Omnibus". **C7 neobsahuje o žádném zjednodušujícím/omnibusovém balíčku EU ani jednu zmínku** — ani v těle, ani v ledgeru (37 řádků), ani v seznamu zdrojů. Nemám tedy důkaz, na jehož základě bych mohl posuzovat, zda a jak se posouvá účinnost čl. 50, a **odmítám o tom spekulovat**. Zaznamenávám: postoj plánu (plnit od 2026-08-02, C7 §2.4 + Cooley alert z 2026-08-03, přímý fetch) je z hlediska rizika správný bez ohledu na jakýkoli projednávaný odklad; jediná jednosměrná chyba by byla spoléhat na odklad, který nenastane. Jediné odkladné ustanovení, které C7 doloženě uvádí, je **grace period do 2026-12-02 pro už uvedené generativní systémy** — na nový systém HypeAgentSocials nedopadá.

**severity: minor | section: §0.3 (fact-rot table) | claim: the review mandate asks about an EU "Omnibus" timing question for which C7 contains no evidence whatsoever, so it cannot be assessed; the plan's comply-from-2026-08-02 posture is risk-correct regardless, and C7's only documented grace period (to 2026-12-02) applies to generative systems already on the market, not to this one | required change: add a dated recheck row to §0.3 for any EU simplification package affecting Art. 50 timing, with an explicit standing rule that no expected postponement may relax the burned-in disclosure control before it is in force**

### [MINOR] m-6 · Obsah LIA není specifikován, přestože C7 zakazuje plošné posouzení

Phase 0 požaduje, aby LIA "existovala", a gate ověřuje jen existenci. C7 §2.6 přitom cituje požadavek na **case-by-case třídílný test** (účel / nezbytnost / vyvážení) s výslovným *"there are no blanket legitimate interest assessments for this purpose"*. Bez určení, na jaké účely a jaké kategorie zdrojů se LIA vztahuje, hrozí, že vznikne jeden obecný dokument — tedy přesně to, co pokyny vylučují. Souvisí i s tím, že §2.3 obsahuje zdroje s velmi odlišnými profily (Hacker News komentáře vs. Bluesky vs. operátorovy Redditové poznámky).

**severity: minor | section: §17 Phase 0 (LIA deliverable) | claim: Phase 0 gates only on the LIA "existing", although C7 §2.6 requires a case-by-case three-part assessment and explicitly rules out blanket assessments, and the source portfolio spans very different processing profiles | required change: specify the LIA's required shape — per purpose and per source family, with the purpose, necessity and balancing tests and the Art. 21 objection route stated — and gate Phase 0 on that shape rather than on existence**

### [MINOR] m-7 · Plán nikde nejmenuje ÚOOÚ ani cestu pro námitku a žádost subjektu údajů

§2.6 odkazuje na české stanovisko formulací *"The Czech supervisory authority's own guidance is quoted by C7"*, bez pojmenování úřadu. Privacy notice musí dozorový úřad jmenovat, stejně jako kontaktní bod a způsob uplatnění práv; plán, který je jinak precizní v pojmenování mechanismů, tady zůstává obecný.

**severity: minor | section: §2.6 | claim: the plan never names Úřad pro ochranu osobních údajů as the supervisory authority, nor a contact point or route by which a data subject exercises an objection or erasure request, although §2.6 relies on that authority's guidance | required change: name ÚOOÚ in §2.6, and require the published privacy notice to state the contact point, the objection/erasure route and the right to lodge a complaint with ÚOOÚ**

---

## 4. Co plán dělá právně dobře (aby oprava nic z toho nerozbila)

Zaznamenávám výslovně, protože při opravách blockerů je snadné to poškodit:

1. **Do-not-scrape list (§2.5) je přísnější než C7.** C7 dodal 7 položek; plán jich má 10 a přidává třídy, které C7 neřešil (recenzní platformy typu G2, jakákoli login wall včetně "půjčených" cookies, jakákoli anti-bot výzva jako "ne", robots-disallowed cesty). Věta *"Absence from this list is not permission"* je správná konstrukce. Poctivé zaznamenání protiargumentu z US judikatury bez toho, aby se z něj udělala výmluva, je přesně ten postoj, který u auditu obstojí.
2. **Playwright mimo sběrnou cestu (D-12)** implementuje C7 §2.3 v plném rozsahu, včetně toho, že žádný degradovaný stupeň nikdy nesestupuje ke scrapingu (§2.5, R-01, R-02).
3. **Hudba (§4.4, §5.2, D-13):** zákaz routeru pro publikované assety s odůvodněním "žádné oficiální upstream API, každá routa neoficiální, upstream v aktivním sporu", plus zákaz platformních trending zvuků pro master asset a požadavek licencované hudby. **C7 tuto oblast neřešil vůbec** — plán zde jde nad rámec důkazního balíčku správným směrem.
4. **Ztráta indemnifikace při nákupu přes resellera (§5.1)** je pojmenována, ne zameten.
5. **Rozdělení čtení a publikace na X (§7.5, F-2)** je právně čisté a odpovídá C7 §2.2.
6. **Claim gate jako regulatorní důkazní stopa (§6.7):** jedenáct tříd, pět nevypnutelných *"because those are the classes whose failure is a legal exposure rather than a quality miss"*, dvojí průchod kolem přepisujícího voice gate (D-16), kontrola on-image textu a mluvených linek. Věta v §6.4 o tom, že publikovaná chybná cena je *"potentially a consumer-protection matter under Czech law — which gives the never-invent rule independent legal force"*, je přesně to propojení, které C7 §2.9 požaduje.
7. **Script-lock + nulové claim tokeny v mluveném slově u neobsluhovaných běhů (§6.8, §14.5)** je silnější kontrola, než jakou C7 vyžadoval.
8. **LIA a privacy notice jako blokující Phase-0 gate** (§17: *"Do not start Phase 1 until … the two company privacy artefacts exist"*) — plán je nemohl vygenerovat a správně to říká.
9. **Ruční stažení ToS routeru jako podmínka zahájení buildu (R-27, Phase 0)** implementuje C7 ledger ř. 35 přesně.
10. **Rozhodnutí per-asset provenance record řešit až po dokončení generace (D-20, W2-03)** je právně nejchytřejší detail celého plánu: bez něj by license snapshot jmenoval model, který asset nevyrenderoval.

---

## 5. Doporučené pořadí nápravy

1. **B-1** (podoby a hlasy) — nejlevnější řešení je jednořádkové rozhodnutí "v1 nemá lidského presentéra ani klonovaný hlas". Udělat první, protože rozhodne, jestli je potřeba celý gate.
2. **B-2** (AI-content class jako odvozené engine-level pole) — dopadá na největší objem assetů (celý český set) a je čistě strukturální změna.
3. **B-4** (provenance jako kontrola gate) — dvě věty do §7.4 a §11.3 plus dvě pole do registru.
4. **B-3** (rung 3 a label checklist) — přesun potvrzení z gate do packaging.
5. **B-5** (retence výňatků, index pack → klíč) — nejdražší na retrofit, proto **musí být před Phase 1**, ne po ní.
6. **M-9, M-5, M-8, m-3** — všechny míří do Phase 0; udělat v jedné dávce.
7. **M-1, M-3, M-4** — Phase 1 a Phase 3.
8. **M-2, M-6, M-7** — před Phase 6 (distribuce), protože do té doby nic neopouští systém.
9. Zbylé minory průběžně.

---

## 6. Soulad s PRD / zadáním

- **Sekce:** `HypeAgentSocials_InstructionsAssignment.md` bod 14 (legal/ethical collection), bod 4 sekce "Scraping / automation design concerns" (robots/ToS/legal/ethical constraints + do-not-scrape list), bod 15 (rizika).
- **Konflikty:** žádné. Plán zadání v této části **překračuje** — zadání žádá pokrytí ToS rizik a do-not-scrape list, plán dodává obojí plus posouzení, které browser automation z v1 vyřazuje úplně.
- **Navrhovaný amendment zadání:** **NE.**
- **Navrhované amendmenty plánu:** ano, 21 (viz výše). Navíc doporučuji zapsat do `DECISION_LOG.md` dvě nová rozhodnutí (person-basis politika z B-1; AI-content class jako odvozené pole z B-2) a do `RISK_LOG.md` řádek k B-3, protože jde o zjištěnou díru v F-4/D-23, tedy v jednom z původních výzkumných flagů.

---

## 7. Mrtvý kód / paralelní implementace v právně citlivých místech

Repozitář je ve fázi návrhu, kód neexistuje. Kontroloval jsem paralelní *deklarace* téže odpovědnosti, protože ty se do kódu propíší:

- **Publish gate ve dvou verzích** — §7.4 (4 kontroly) a Appendix A ř. 2331 (tytéž 4 kontroly), obojí bez provenance, zatímco `DECISION_LOG.md` D-20 tvrdí 5. Buď sjednotit na 5, nebo D-20 opravit. Toto je jediná skutečná dvojkolejnost s právním dopadem (B-4).
- **W2-08 vs. W2-08a** — mitigace nahrazena, originál ponechán s explicitní poznámkou o supersedenci (§15.4, RISK_LOG ř. 68). To je **správně** provedeno a nejde o nález.
- **Retence doslovného textu ve dvou režimech** — 30 dní (§2.6 curated-inbox) vs. trvale (§2.6 provenance snapshot, §12.2). To **je** paralelní implementace téže odpovědnosti a je to obsahem B-5.

---

## 8. Disclaimer

Tento audit je **odborná rešerše a auditní doporučení, nikoli závazné právní stanovisko advokáta zapsaného v České advokátní komoře**. Vychází výhradně z důkazního balíčku C7 ze dne 2026-08-06; nezávisle jsem neověřoval žádný primární pramen a nemám k tomu v tomto běhu přístup. C7 sám označuje několik nosných citací za **Medium** či **Low-Medium confidence** s blokovaným přímým načtením — zejména Redditovu Responsible Builder Policy, text občanského zákoníku k ochraně osobnosti, a obě česká reklamní/spotřebitelská ustanovení (zák. 40/1995 Sb. a 634/1992 Sb.). Tyto tři okruhy je nutné ověřit proti primárnímu textu, než se na ně kdokoli spolehne. Před podpisem smluv s vendory, před finalizací LIA či privacy notice, před uvedením jakéhokoli syntetického presentéra a před podáním vůči ÚOOÚ konzultujte s licencovaným advokátem, u AI Act ideálně s poradcem specializovaným na nařízení 2024/1689.

---

## 9. Jednoduché shrnutí (bez právničiny)

Plán je poctivější, než bývá zvykem — nevymýšlí si přístup k datům, která nejsou dostupná, a u AI značení dělá tu správnou věc: štítek se vypaluje přímo do videa, protože metadata platformy při nahrání zahodí. Pět věcí ale zatím drží jen na papíře:

1. Nikde není napsáno, co se stane, když ve videu vystoupí **člověk** — skutečný nebo vygenerovaný. Přitom "mluvící člověk" je v plánu povolená volba. Buď to zakázat, nebo doplnit režim souhlasu.
2. Přepínač, který určuje, jestli je asset "AI obsah", si může každé téma **přenastavit** — a jeho výchozí hodnota zapomíná na **AI hlas**. Právě český výchozí recept AI hlas používá a generované video ne. Takže by českým videím štítek nemusel naskočit vůbec.
3. Když se něco pokazí a obsah jde "ruční cestou" (operátor si ho zkopíruje a vloží sám), **přeskočí se kontrolní bod**, který má hlídat platformní AI štítky. A ruční cesta je zároveň záložní cesta pro všechno.
4. Slíbený "rodný list" každého vygenerovaného obrázku a videa (který model ho udělal a pod jakou licencí) se sice ukládá, ale **nikdo ho nekontroluje**, než se asset označí za připravený.
5. Systém si na jednom místě slíbí, že doslovné citace z internetu smaže po 30 dnech — a na jiném místě si je uloží **navždy** do složky běhu. Pokud pak někdo požádá o výmaz, nemáme jak se k nim dostat.

Nic z toho nejsou pochybení, se kterými by se nedalo hnout před začátkem stavby. Naopak: čtyři z pěti jsou dnes změna několika vět, zatímco po Phase 1 už to bude přepis.

---

## 10. Verdikt

# **PO OPRAVÁCH** (conditionally ready)

Plán **není** ve stavu "přepracovat" — jeho právní kostra je v pořádku a v několika bodech nadstandardní. Zároveň **není** připraven pro Stage 5 tak, jak je: pět blockerů se dotýká osobnostních práv, nosné kontroly podle čl. 50 AI Act, jediného vynucovacího bodu publikace, obhajitelnosti práv k assetům a vykonatelnosti výmazu.

**Podmínka postupu do Stage 5:** vyřešit **B-1 až B-5** a **M-9** (doplnění tří chybějících poradenských položek do §16). Zbylé majory jsou vázány na fázové brány (M-1/M-3/M-4 před Phase 3, M-2/M-6/M-7 před Phase 6, M-5/M-8 do Phase 0) a nemusí blokovat Stage 5, pokud jsou v §16/§17 zapsané s rozhodovacím bodem. Minory do backlogu.

**severity: — | section: overall verdict | claim: the plan's legal skeleton is sound and in several places exceeds the C7 evidence pack, but five blocker-class gaps (likeness/voice regime, configurable AI-content class, publish-gate bypass via rung 3, unenforced provenance precondition, permanent verbatim retention) mean it is not Stage-5 ready as written | required change: resolve B-1 through B-5 and M-9 before Stage 5; carry the remaining majors as dated open decisions bound to their phase gates**
