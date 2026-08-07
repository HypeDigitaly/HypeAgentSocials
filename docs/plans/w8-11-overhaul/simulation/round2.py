# W8-11 simulation ROUND 2 — operator feedback applied:
#   1) styled model-rendered typography (big, expressive, integrated)
#   2) logos accompany every tool mention
#   3) natural colloquial Czech + English versions of every concept
#   4) nano-banana-pro image_input test: real logo PNGs as references
# gpt-image-2 is the primary (operator's round-1 pick). Desk-check only.
import json
import sys
import time
import urllib.request
from pathlib import Path

SIM = Path(__file__).parent
REPO = SIM.parents[3]
R2 = SIM / "round2"

API_KEY = None
for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
    if line.startswith("KIE_API_KEY="):
        API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
if not API_KEY:
    sys.exit("KIE_API_KEY not found in .env")

CREATE = "https://api.kie.ai/api/v1/jobs/createTask"
RECORD = "https://api.kie.ai/api/v1/jobs/recordInfo"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

GPT = "gpt-image-2-text-to-image"
NBP = "nano-banana-pro"

LOGO_REFS = {
    "chatgpt": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/960px-ChatGPT_logo.svg.png",
    "claude": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Claude_AI_symbol.svg/960px-Claude_AI_symbol.svg.png",
    "notion": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Notion-logo.svg/960px-Notion-logo.svg.png",
    "zapier": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Zapier_logo.svg/960px-Zapier_logo.svg.png",
    "gmail": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Gmail_icon_%282020%29.svg/960px-Gmail_icon_%282020%29.svg.png",
}

CZ = (
    " Render every character EXACTLY as written, including all Czech diacritics "
    "(á č ď é ě í ň ó ř š ť ů ú ý ž). No other text anywhere in the image."
)
EN = " Render every word EXACTLY as written. No other text anywhere in the image."

TYPO = (
    "The typography is the hero of the composition: oversized expressive display type "
    "with deliberate hierarchy, tight leading, mixed weights, and one word or phrase "
    "emphasized in the accent color. Premium editorial social-first design — never a "
    "small plain flat caption. "
)

CONCEPTS: list[tuple[str, dict[str, str]]] = [
    ("1_serif_statement", {
        "cs": "A minimalist editorial statement card on warm cream paper (hex #F6F1E7) with a subtle "
              "paper-grain texture. " + TYPO + "A huge high-contrast modern serif headline (in the "
              "spirit of Playfair Display), left-aligned, filling most of the canvas over three "
              "lines: 'AI vám práci nevezme.' / 'Vezme vám ji firma,' / 'která ji umí použít.' — set "
              "the phrase 'která ji umí použít.' in italic deep indigo (hex #302B87), the rest in "
              "near-black ink. Small letterspaced caps kicker above in teal (hex #00A39A): "
              "'HYPEDIGITALY'. One thin hairline rule under the headline block. Flat premium "
              "magazine-cover feel, no gradients, no glow." + CZ,
        "en": "A minimalist editorial statement card on warm cream paper (hex #F6F1E7) with a subtle "
              "paper-grain texture. " + TYPO + "A huge high-contrast modern serif headline (in the "
              "spirit of Playfair Display), left-aligned, filling most of the canvas over three "
              "lines: 'AI won't take your job.' / 'A company that' / 'uses it will.' — set 'uses it "
              "will.' in italic deep indigo (hex #302B87), the rest in near-black ink. Small "
              "letterspaced caps kicker above in teal (hex #00A39A): 'HYPEDIGITALY'. One thin "
              "hairline rule under the headline block. Flat premium magazine-cover feel, no "
              "gradients, no glow." + EN,
    }),
    ("2_stat_hero", {
        "cs": "A flat dark premium stat card, solid ground hex #1E1B2E, no gradients, no glow. "
              + TYPO + "A gigantic extra-bold grotesque number-and-word block '10 hodin' in pure "
              "white filling the upper two thirds, with 'hodin' underlined by a thick teal (hex "
              "#00A39A) hand-drawn-feel stroke. Below, one calm line in a lighter weight, warm "
              "off-white (hex #EDEAE3): 'Tolik času týdně šetří našim klientům automatizace.' Tiny "
              "letterspaced caps footer: 'HYPEDIGITALY'." + CZ,
        "en": "A flat dark premium stat card, solid ground hex #1E1B2E, no gradients, no glow. "
              + TYPO + "A gigantic extra-bold grotesque number-and-word block '10 hours' in pure "
              "white filling the upper two thirds, with 'hours' underlined by a thick teal (hex "
              "#00A39A) hand-drawn-feel stroke. Below, one calm line in a lighter weight, warm "
              "off-white (hex #EDEAE3): 'That is what automation saves our clients every week.' "
              "Tiny letterspaced caps footer: 'HYPEDIGITALY'." + EN,
    }),
    ("3_tool_stack", {
        "cs": "A clean light editorial list card on soft warm paper (hex #F6F1E7). " + TYPO
              + "Heavy grotesque title over two lines: 'Nástroje, které u klientů' / 'nasazujeme "
              "nejčastěji'. Below, five generously spaced rows; each row shows the tool's REAL "
              "official app icon on the left (render each brand mark accurately: OpenAI ChatGPT "
              "knot; Make purple asterisk-like mark; Anthropic Claude coral starburst; Notion "
              "black-and-white N cube; Calendly blue C badge), then the tool name in bold and one "
              "short line in regular weight: "
              "'ChatGPT — první nápady, rychlá rešerše, první verze textů.' / "
              "'Make — scénáře naklikáte, kód neřešíte.' / "
              "'Claude — delší texty a podklady, umí dobře česky.' / "
              "'Notion — úkoly, zápisky a wiki na jednom místě.' / "
              "'Calendly — klient si schůzku naklikne sám.' "
              "Footer caps: 'HYPEDIGITALY'. Flat design, no gradients." + CZ,
        "en": "A clean light editorial list card on soft warm paper (hex #F6F1E7). " + TYPO
              + "Heavy grotesque title over two lines: 'The tools we deploy' / 'most often'. Below, "
              "five generously spaced rows; each row shows the tool's REAL official app icon on the "
              "left (render each brand mark accurately: OpenAI ChatGPT knot; Make purple "
              "asterisk-like mark; Anthropic Claude coral starburst; Notion black-and-white N cube; "
              "Calendly blue C badge), then the tool name in bold and one short line in regular "
              "weight: "
              "'ChatGPT — first drafts and quick research.' / "
              "'Make — click your scenarios together, skip the code.' / "
              "'Claude — long-form docs and briefs with nuance.' / "
              "'Notion — tasks, notes and wiki in one place.' / "
              "'Calendly — clients book their own slot.' "
              "Footer caps: 'HYPEDIGITALY'. Flat design, no gradients." + EN,
    }),
    ("4_workflow_map", {
        "cs": "A clean automation-workflow diagram on white paper with a very faint dot grid. "
              + TYPO + "Heavy grotesque title: 'Poptávka se vyřídí sama.' Subtitle in regular "
              "weight: 'Nikdo z týmu na ni nemusel sáhnout.' The diagram: four rounded-rectangle "
              "nodes connected left-to-right by smooth arrows with small hand-drawn-feel annotation "
              "ticks. Node 1: a simple form icon, label 'Webový formulář'. Node 2: the REAL "
              "official Zapier orange asterisk logo, label 'Zapier'. Node 3: the REAL official "
              "Anthropic Claude coral starburst logo, label 'Claude'. Node 4: the REAL official "
              "Gmail multicolor M envelope logo, label 'Gmail — odpověď klientovi'. Flat, no "
              "gradients, no fake software UI, no screenshots." + CZ,
        "en": "A clean automation-workflow diagram on white paper with a very faint dot grid. "
              + TYPO + "Heavy grotesque title: 'The lead handles itself.' Subtitle in regular "
              "weight: 'No one on the team had to touch it.' The diagram: four rounded-rectangle "
              "nodes connected left-to-right by smooth arrows with small hand-drawn-feel annotation "
              "ticks. Node 1: a simple form icon, label 'Web form'. Node 2: the REAL official "
              "Zapier orange asterisk logo, label 'Zapier'. Node 3: the REAL official Anthropic "
              "Claude coral starburst logo, label 'Claude'. Node 4: the REAL official Gmail "
              "multicolor M envelope logo, label 'Gmail — reply to the client'. Flat, no gradients, "
              "no fake software UI, no screenshots." + EN,
    }),
    ("5_scene_hook_styled", {
        "cs": "A real-world cinematic B2B scene: a single desk in a dark office at night, city "
              "skyline through the window, one dominant warm practical light, deep shadow falloff. "
              "Every screen and monitor in the frame is OFF (dark glass) or angled away — never "
              "render any UI content. No people. " + TYPO + "Large cinematic display type "
              "integrated into the scene's lower negative space, two lines, white with one warm "
              "amber (hex #E8A63B) emphasis: 'Poptávka přišla ve dvě ráno.' / 'Odpověď odešla ve "
              "2:01.' — emphasize '2:01' in amber. The type interacts with the scene's light, "
              "premium film-poster feel." + CZ,
        "en": "A real-world cinematic B2B scene: a single desk in a dark office at night, city "
              "skyline through the window, one dominant warm practical light, deep shadow falloff. "
              "Every screen and monitor in the frame is OFF (dark glass) or angled away — never "
              "render any UI content. No people. " + TYPO + "Large cinematic display type "
              "integrated into the scene's lower negative space, two lines, white with one warm "
              "amber (hex #E8A63B) emphasis: 'The lead came in at 2 a.m.' / 'The reply went out at "
              "2:01.' — emphasize '2:01' in amber. The type interacts with the scene's light, "
              "premium film-poster feel." + EN,
    }),
    ("6_myth_bust", {
        "cs": "A bold split editorial card. Top half: solid deep indigo (hex #302B87) with huge "
              "white grotesque type: 'Mýtus: AI se vyplatí' / 'jen velkým firmám.' Bottom half: "
              "warm cream (hex #F6F1E7) with huge near-black type: 'Realita: Největší rozdíl' / "
              "'udělá v pětičlenném týmu.' — with 'pětičlenném' emphasized in teal (hex #00A39A). "
              + TYPO + "A thin horizontal tear-edge divider between the halves. Flat, no gradients, "
              "no icons." + CZ,
        "en": "A bold split editorial card. Top half: solid deep indigo (hex #302B87) with huge "
              "white grotesque type: 'Myth: AI only pays off' / 'for big companies.' Bottom half: "
              "warm cream (hex #F6F1E7) with huge near-black type: 'Reality: it matters most' / "
              "'in a five-person team.' — with 'five-person' emphasized in teal (hex #00A39A). "
              + TYPO + "A thin horizontal tear-edge divider between the halves. Flat, no gradients, "
              "no icons." + CZ,
    }),
    ("7_ugc_phone", {
        "cs": "A vertical phone-camera photo, authentic UGC feel with slightly imperfect framing: a "
              "kitchen table in soft morning light with a closed laptop, a paper to-do list with "
              "handwritten-style scribbles (illegible), and a cup of coffee. No people, no screens "
              "with content. " + TYPO + "A large casual bold sans-serif caption across the upper "
              "third, white with a subtle soft shadow, two lines: 'Pondělí bez ručního přepisování "
              "tabulek.' / 'Zvykli jsme si rychle.' Native creator-post energy, not an ad." + CZ,
        "en": "A vertical phone-camera photo, authentic UGC feel with slightly imperfect framing: a "
              "kitchen table in soft morning light with a closed laptop, a paper to-do list with "
              "handwritten-style scribbles (illegible), and a cup of coffee. No people, no screens "
              "with content. " + TYPO + "A large casual bold sans-serif caption across the upper "
              "third, white with a subtle soft shadow, two lines: 'Monday without manual "
              "spreadsheet work.' / 'We got used to that fast.' Native creator-post energy, not an "
              "ad." + EN,
    }),
]

JOBS: list[dict] = []
for key, langs in CONCEPTS:
    for lang, prompt in langs.items():
        JOBS.append(dict(
            key=f"{key}_{lang}", model=GPT, folder=f"round2/{GPT}",
            input={"prompt": prompt, "aspect_ratio": "4:5", "resolution": "1K"},
        ))

# nano-banana-pro image_input probes: the REAL logo files as references.
NBP_REF_NOTE = (
    " Reference images supplied with this request are the REAL official logos to use, in "
    "this order: "
)
JOBS.append(dict(
    key="3_tool_stack_cs_refs", model=NBP, folder=f"round2/{NBP}",
    input={
        "prompt": CONCEPTS[2][1]["cs"].replace(
            "render each brand mark accurately: OpenAI ChatGPT knot; Make purple "
            "asterisk-like mark; Anthropic Claude coral starburst; Notion black-and-white N cube; "
            "Calendly blue C badge",
            "use the supplied reference images for the marks, drawn faithfully",
        ).replace(
            "'Make — scénáře naklikáte, kód neřešíte.' / ",
            "'Zapier — propojí aplikace, které spolu neumí mluvit.' / ",
        ).replace(
            "'Calendly — klient si schůzku naklikne sám.' ",
            "",
        ).replace("five generously spaced rows", "four generously spaced rows")
        + NBP_REF_NOTE + "1 ChatGPT, 2 Claude, 3 Notion, 4 Zapier.",
        "image_input": [LOGO_REFS["chatgpt"], LOGO_REFS["claude"], LOGO_REFS["notion"], LOGO_REFS["zapier"]],
        "aspect_ratio": "4:5", "resolution": "1K", "output_format": "png",
    },
))
JOBS.append(dict(
    key="4_workflow_map_cs_refs", model=NBP, folder=f"round2/{NBP}",
    input={
        "prompt": CONCEPTS[3][1]["cs"] + NBP_REF_NOTE + "1 Zapier, 2 Claude, 3 Gmail.",
        "image_input": [LOGO_REFS["zapier"], LOGO_REFS["claude"], LOGO_REFS["gmail"]],
        "aspect_ratio": "4:5", "resolution": "1K", "output_format": "png",
    },
))


def api(url: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "User-Agent": UA},
        method="POST" if body else "GET",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def download(url: str, out: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        out.write_bytes(resp.read())


def main() -> None:
    for sub in (f"round2/{GPT}", f"round2/{NBP}", "round2/prompts"):
        (SIM / sub).mkdir(parents=True, exist_ok=True)
    for job in JOBS:
        (SIM / "round2/prompts" / f"{job['model']}__{job['key']}.txt").write_text(
            job["input"]["prompt"], encoding="utf-8")

    pending: dict[str, dict] = {}
    for job in JOBS:
        try:
            r = api(CREATE, {"model": job["model"], "input": job["input"]})
            task_id = (r.get("data") or {}).get("taskId")
            if r.get("code") == 200 and task_id:
                pending[task_id] = job
                print(f"CREATED {job['model']} {job['key']} -> {task_id}", flush=True)
            else:
                print(f"CREATE-FAIL {job['model']} {job['key']}: code={r.get('code')} msg={r.get('msg')}", flush=True)
        except Exception as exc:
            print(f"CREATE-ERROR {job['model']} {job['key']}: {exc}", flush=True)
        time.sleep(1)

    total_credits = 0.0
    deadline = time.time() + 600
    while pending and time.time() < deadline:
        time.sleep(12)
        for task_id in list(pending):
            job = pending[task_id]
            try:
                payload = api(f"{RECORD}?taskId={task_id}")
            except Exception as exc:
                print(f"POLL-ERROR {job['key']}: {exc}", flush=True)
                continue
            data = payload.get("data") or {}
            state = data.get("state")
            if state == "success":
                urls = json.loads(data.get("resultJson") or "{}").get("resultUrls") or []
                credits = float(data.get("creditsConsumed") or 0)
                total_credits += credits
                if urls:
                    out = SIM / job["folder"] / f"{job['key']}.png"
                    try:
                        download(urls[0], out)
                        print(f"DONE {job['model']} {job['key']} credits={credits}", flush=True)
                    except Exception as exc:
                        print(f"DL-ERROR {job['key']}: {exc} url={urls[0]}", flush=True)
                else:
                    print(f"DONE-NO-URL {job['model']} {job['key']}", flush=True)
                del pending[task_id]
            elif state == "fail":
                print(f"FAILED {job['model']} {job['key']}: {data.get('failCode')} {data.get('failMsg')}", flush=True)
                del pending[task_id]
    for task_id, job in pending.items():
        print(f"TIMEOUT {job['model']} {job['key']} ({task_id})", flush=True)
    print(f"TOTAL-CREDITS {total_credits}", flush=True)


if __name__ == "__main__":
    main()
