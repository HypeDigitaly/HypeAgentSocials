# W8-11 pre-implementation simulation: renders the planned style systems on all
# three models (canonical nano-banana-2 grounds + gpt-image-2 / nano-banana-pro
# full text-in-image) using hand-authored prompts lifted from STYLE_SYSTEMS_SPEC.md
# composition directives. Desk-check only — not engine code.
import json
import sys
import time
import urllib.request
from pathlib import Path

SIM = Path(__file__).parent
REPO = SIM.parents[3]

API_KEY = None
for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
    if line.startswith("KIE_API_KEY="):
        API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
if not API_KEY:
    sys.exit("KIE_API_KEY not found in .env")

CREATE = "https://api.kie.ai/api/v1/jobs/createTask"
RECORD = "https://api.kie.ai/api/v1/jobs/recordInfo"

NO_TEXT = (
    "Do not render any text, letters, numbers, words, watermarks, logos, or UI "
    "elements anywhere in the image."
)

# --- Scene descriptions (shared between canonical ground and test full renders) ---
SCENE_LIFESTYLE = (
    "A real-feeling, minimalist, aspirational-but-plausible quiet apartment desk corner "
    "in soft morning window light, phone-camera-real framing, eye-level and slightly "
    "off-center — not a studio product shot; the environment itself is the message. "
    "A light oak desk, a laptop with its screen angled away from the camera, a ceramic "
    "coffee cup, an open paper notebook. No person, no face, no body anywhere in the "
    "frame. The upper-left area of the image (from 10% to 70% of the width, from 20% to "
    "34% of the height) is a plain open wall in soft shadow — keep that region free of "
    "clutter, high-contrast edges, or busy texture."
)
SCENE_HOOK = (
    "A real-world B2B environment shot with genuine cinematographic intent: a single desk "
    "lit only by monitor glow, a night city skyline visible through the office window "
    "behind it. One dominant light source, visible rim light, deep shadow falloff, a real "
    "sense of place and late hour. No person, no robot or mascot imagery, no fabricated "
    "drama — the mood comes from lighting and composition alone. The lower third of the "
    "frame (from 66% to 80% of the height, horizontally centered) is natural negative "
    "space in deep shadow — keep it plain and low-detail."
)
SCENE_LI_HERO = (
    "A glass-walled meeting room at dusk, city skyline beyond, shot with genuine "
    "cinematographic intent: one dominant warm interior light source, cool blue exterior "
    "light, visible rim light on the glass edges, deep shadow falloff, a real sense of "
    "place and time of day. Empty chairs, no person anywhere. The lower portion of the "
    "frame (from 62% to 82% of the height, horizontally centered) is natural negative "
    "space in shadow — keep it plain and low-detail."
)
SCENE_GRID_INSET = (
    "A small, quiet, real-feeling desk close-up photograph: an open paper notebook and a "
    "pen, with rolled paper and drafting tools beside them. Soft natural light, shallow "
    "depth of field, genuinely photographic. No readable text, no screen or UI chrome, "
    "no person."
)
SCENE_LOGOS = (
    "A clean, evenly lit, light warm-gray studio background. A single horizontal row of "
    "five official application icons, evenly spaced, each in its native rounded app-icon "
    "shape with a soft drop shadow: the OpenAI ChatGPT logo, the Anthropic Claude logo, "
    "the Google Gemini logo, the Notion logo, and the Zapier logo. Render each brand mark "
    "accurately — correct official colors, correct proportions, correct symbol geometry."
)

# --- Czech copy (voice-correct, faceless, claim-safe) ---
TXT_LIFESTYLE = "5 nástrojů, které zvládnou\nvaše ráno za vás"
TXT_HOOK = "Zatímco spíte,\nAI pracuje."
TXT_LI_HERO = "Automatizace nepropouští.\nUvolňuje kapacitu."

VALUE_SHEET_ENTRIES = [
    "1. Zapier — propojí formuláře, tabulky a e-maily bez psaní kódu.",
    "2. Make — vizuální scénáře pro opakované procesy a přenos dat.",
    "3. n8n — automatizace na vlastním serveru, plná kontrola nad daty.",
    "4. Claude — příprava podkladů, souhrnů a odpovědí v češtině.",
    "5. Notion AI — zápisky ze schůzek převede na úkoly během vteřin.",
    "6. Airtable — databáze klientů propojená s formuláři a reporty.",
    "7. Calendly — plánování schůzek bez zbytečných e-mailů tam a zpět.",
    "8. Loom — krátká videa místo dlouhých porad a vysvětlování.",
]

GRID_TEXT_SPEC = (
    "The canvas is a light warm paper ground (hex #F3F1E9) covered by a faint ruled grid "
    "in both axes (hex #E4E0D2, thin lines). Top masthead row: the word 'HYPEDIGITALY' "
    "small caps left, the label 'AI PROVOZ' small caps right, a thin hairline rule under "
    "both. Below it a small outlined pill reading 'PLAYBOOK 03'. Main headline in a very "
    "heavy black grotesque sans-serif (ink hex #221F1C), three lines, large: 'Agentura, "
    "která odpovídá do pěti minut, vyhrává.' — render the phrase 'do pěti minut' in "
    "indigo (hex #302B87) and paint an amber highlighter bar (hex #E8A63B) behind the "
    "word 'vyhrává.'. Below the headline one body line in a regular sans-serif: 'Postup, "
    "který používáme u klientů od prvního dne.' In the top-right corner a small "
    "rounded-corner photo inset card: " + SCENE_GRID_INSET + " Footer: a small pill "
    "reading 'Posunout →' bottom-left and a page badge '1/5' bottom-right. Render all "
    "Czech text EXACTLY as written, including every diacritic mark (á, č, ě, í, ř, ů, ý, ž)."
)

VALUE_SHEET_SPEC = (
    "A dark editorial reference card, ground hex #1E1B2E, flat, no gradients, no glow. "
    "Top-left kicker in teal (hex #00A39A), small caps: 'KATEGORIE 02 · AUTOMATIZACE'. "
    "Top-right counter in white: '4/10'. Below, filling the card, a dense numbered list "
    "set in a warm off-white serif (hex #EDEAE3), small text size, generous line spacing, "
    "left-aligned, one entry per line pair:\n"
    + "\n".join(VALUE_SHEET_ENTRIES)
    + "\nA thin indigo rule (hex #302B87) under the kicker. No other decoration, no "
    "icons, no images. Render all Czech text EXACTLY as written, including every "
    "diacritic mark (á, č, ě, í, ř, š, ů, ý, ž)."
)

def caption_clause(zone_desc: str, font_desc: str, text: str) -> str:
    lines = text.split("\n")
    quoted = " on the first line and ".join(f"'{ln}'" for ln in lines)
    return (
        f" Composite a caption {zone_desc}, set in {font_desc}, pure white (hex #FFFFFF): "
        f"{quoted} on the second line. Render the Czech text EXACTLY as written, "
        "including every diacritic mark. No other text anywhere in the image."
    )

JOBS = [
    # --- canonical grounds (nano-banana-2, model ships today; NO text anywhere) ---
    dict(key="1_lifestyle_cover_ground", model="nano-banana-2", folder="canonical",
         input={"prompt": SCENE_LIFESTYLE + " " + NO_TEXT, "output_format": "png", "aspect_ratio": "4:5"}),
    dict(key="2_scene_hook_ground", model="nano-banana-2", folder="canonical",
         input={"prompt": SCENE_HOOK + " " + NO_TEXT, "output_format": "png", "aspect_ratio": "4:5"}),
    dict(key="5_li_hero_ground", model="nano-banana-2", folder="canonical",
         input={"prompt": SCENE_LI_HERO + " " + NO_TEXT, "output_format": "png", "aspect_ratio": "16:9"}),
    dict(key="3_grid_inset_ground", model="nano-banana-2", folder="canonical",
         input={"prompt": SCENE_GRID_INSET + " " + NO_TEXT, "output_format": "png", "aspect_ratio": "1:1"}),
    dict(key="6_logo_probe", model="nano-banana-2", folder="canonical",
         input={"prompt": SCENE_LOGOS + " No other text or objects in the image.", "output_format": "png", "aspect_ratio": "4:5"}),
]

for model, folder, extra in [
    ("gpt-image-2-text-to-image", "models/gpt-image-2-text-to-image", {"resolution": "1K"}),
    ("nano-banana-pro", "models/nano-banana-pro", {"resolution": "1K", "output_format": "png"}),
]:
    JOBS += [
        dict(key="1_lifestyle_cover", model=model, folder=folder,
             input={"prompt": SCENE_LIFESTYLE + caption_clause(
                 "in the reserved plain-wall region in the upper-left (left-aligned, two lines)",
                 "a clean geometric sans-serif of semi-bold weight (similar to Montserrat SemiBold)",
                 TXT_LIFESTYLE), "aspect_ratio": "4:5", **extra}),
        dict(key="2_scene_hook_cover", model=model, folder=folder,
             input={"prompt": SCENE_HOOK + caption_clause(
                 "bold and centered in the lower-third negative space (two short lines)",
                 "a bold clean geometric sans-serif (similar to Montserrat Bold)",
                 TXT_HOOK), "aspect_ratio": "4:5", **extra}),
        dict(key="3_operator_grid_cover", model=model, folder=folder,
             input={"prompt": GRID_TEXT_SPEC, "aspect_ratio": "4:5", **extra}),
        dict(key="4_value_sheet_body", model=model, folder=folder,
             input={"prompt": VALUE_SHEET_SPEC, "aspect_ratio": "4:5", **extra}),
        dict(key="5_li_hero", model=model, folder=folder,
             input={"prompt": SCENE_LI_HERO + caption_clause(
                 "bold and centered in the lower negative space (two lines)",
                 "a bold clean geometric sans-serif (similar to Montserrat Bold)",
                 TXT_LI_HERO), "aspect_ratio": "16:9", **extra}),
        dict(key="6_logo_probe", model=model, folder=folder,
             input={"prompt": SCENE_LOGOS + (
                 " Under each icon a small centered label in a neutral gray sans-serif, "
                 "one per icon, exactly: 'ChatGPT', 'Claude', 'Gemini', 'Notion', "
                 "'Zapier'. No other text."), "aspect_ratio": "4:5", **extra}),
    ]


def api(url: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST" if body else "GET",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def main() -> None:
    for job in JOBS:
        (SIM / "prompts" / f"{job['folder'].replace('models/', '')}__{job['key']}.txt".replace("/", "_")).write_text(
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

    deadline = time.time() + 600
    total_credits = 0.0
    while pending and time.time() < deadline:
        time.sleep(12)
        for task_id in list(pending):
            job = pending[task_id]
            try:
                r = api(f"{RECORD}?taskId={task_id}")
            except Exception as exc:
                print(f"POLL-ERROR {job['key']}: {exc}", flush=True)
                continue
            data = r.get("data") or {}
            state = data.get("state")
            if state == "success":
                urls = json.loads(data.get("resultJson") or "{}").get("resultUrls") or []
                credits = data.get("creditsConsumed") or 0
                total_credits += float(credits)
                if urls:
                    out = SIM / job["folder"] / f"{job['key']}.png"
                    with urllib.request.urlopen(urls[0], timeout=120) as img:
                        out.write_bytes(img.read())
                    print(f"DONE {job['model']} {job['key']} credits={credits} -> {out.name}", flush=True)
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
