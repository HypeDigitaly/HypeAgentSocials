# W8-11 simulation ROUND 3 — the unknown-tool scenario, from a REAL live Virlo trend:
# "Lovable AI for Website Building" (new, 2026-08-06, 1.43M views). Tests the three
# treatment tiers for a tool with no logo/screenshot on file, plus an unaided
# obscure-logo probe. Desk-check only.
import json
import time
import urllib.request
from pathlib import Path

from round2 import API_KEY, CREATE, RECORD, UA

SIM = Path(__file__).parent

GPT = "gpt-image-2-text-to-image"
NBP = "nano-banana-pro"

LOVABLE_LOGO = "https://lovable.dev/apple-touch-icon.png"          # REAL vendor asset
LOVABLE_SHOT = "https://lovable.dev/img/opengraph-image.png"       # REAL vendor product image

CZ = (
    " Render every character EXACTLY as written, including all Czech diacritics "
    "(á č ď é ě í ň ó ř š ť ů ú ý ž). No other text anywhere in the image."
)
TYPO = (
    "The typography is the hero of the composition: oversized expressive display type "
    "with deliberate hierarchy, tight leading, mixed weights, one word emphasized in "
    "teal (hex #00A39A). Premium editorial social-first design. "
)

# Shared post copy — natural spoken Czech, built from the trend's actual tactic
# (Claude writes site copy from the business's reviews; Lovable builds the site).
COPY = (
    "Small letterspaced caps kicker in teal (hex #00A39A): 'NOVÝ TREND'. Heavy grotesque "
    "headline over two lines: 'Firma bez webu?' / 'Do večera to jde.' Below, two calm "
    "body lines in regular weight: 'Claude napíše texty z vašich recenzí.' / 'Lovable z "
    "nich postaví web.' Footer caps: 'HYPEDIGITALY'. "
)

JOBS = [
    dict(key="A_logo_guessed", model=GPT, folder=f"round3/{GPT}",
         input={"prompt": (
             "A clean editorial spotlight card on warm cream paper (hex #F6F1E7). " + TYPO + COPY
             + "Above the headline, the OFFICIAL Lovable app logo at a generous size. Flat "
               "design, no gradients." + CZ),
             "aspect_ratio": "4:5", "resolution": "1K"}),
    dict(key="B_illustrative_ui", model=GPT, folder=f"round3/{GPT}",
         input={"prompt": (
             "A clean editorial spotlight card on warm cream paper (hex #F6F1E7). " + TYPO + COPY
             + "Between headline and body, a rounded browser-window card containing a clearly "
               "STYLIZED, simplified illustration of a website-builder interface: abstract "
               "grey/teal content blocks, a sidebar of plain rectangles, NO readable UI text, "
               "obviously an illustration rather than a real screenshot. On the browser "
               "window's title bar a simple name chip reading 'Lovable'. Flat design, no "
               "gradients." + CZ),
             "aspect_ratio": "4:5", "resolution": "1K"}),
    dict(key="C_real_assets_refs", model=NBP, folder=f"round3/{NBP}",
         input={"prompt": (
             "A clean editorial spotlight card on warm cream paper (hex #F6F1E7). " + TYPO + COPY
             + "Reference image 1 is the REAL official Lovable app icon — place it above the "
               "headline at a generous size, faithfully reproduced. Reference image 2 is a REAL "
               "image from lovable.dev — display it between headline and body inside a "
               "rounded browser-window frame with a subtle shadow, keeping its content "
               "unaltered and recognizable. Flat design, no gradients." + CZ),
             "image_input": [LOVABLE_LOGO, LOVABLE_SHOT],
             "aspect_ratio": "4:5", "resolution": "1K", "output_format": "png"}),
    dict(key="D_obscure_logo_probe", model=GPT, folder=f"round3/{GPT}",
         input={"prompt": (
             "A clean, evenly lit, light warm-gray studio background. A single horizontal row "
             "of four official application icons, evenly spaced, each in its native rounded "
             "app-icon shape with a soft drop shadow: the official Lovable logo, the official "
             "Higgsfield logo, the official Genspark logo, and the official Krea logo. Render "
             "each brand mark accurately. Under each icon a small centered label in a neutral "
             "gray sans-serif, exactly: 'Lovable', 'Higgsfield', 'Genspark', 'Krea'. No other "
             "text."),
             "aspect_ratio": "4:5", "resolution": "1K"}),
]


def api(url, body=None):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "User-Agent": UA},
        method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def main() -> None:
    for sub in (f"round3/{GPT}", f"round3/{NBP}", "round3/prompts"):
        (SIM / sub).mkdir(parents=True, exist_ok=True)
    for job in JOBS:
        (SIM / "round3/prompts" / f"{job['model']}__{job['key']}.txt").write_text(
            job["input"]["prompt"], encoding="utf-8")

    pending = {}
    for job in JOBS:
        try:
            r = api(CREATE, {"model": job["model"], "input": job["input"]})
            task_id = (r.get("data") or {}).get("taskId")
            if r.get("code") == 200 and task_id:
                pending[task_id] = job
                print(f"CREATED {job['model']} {job['key']} -> {task_id}", flush=True)
            else:
                print(f"CREATE-FAIL {job['key']}: code={r.get('code')} msg={r.get('msg')}", flush=True)
        except Exception as exc:
            print(f"CREATE-ERROR {job['key']}: {exc}", flush=True)
        time.sleep(1)

    total = 0.0
    deadline = time.time() + 480
    while pending and time.time() < deadline:
        time.sleep(12)
        for task_id in list(pending):
            job = pending[task_id]
            try:
                data = (api(f"{RECORD}?taskId={task_id}").get("data") or {})
            except Exception as exc:
                print(f"POLL-ERROR {job['key']}: {exc}", flush=True)
                continue
            state = data.get("state")
            if state == "success":
                urls = json.loads(data.get("resultJson") or "{}").get("resultUrls") or []
                total += float(data.get("creditsConsumed") or 0)
                if urls:
                    out = SIM / job["folder"] / f"{job['key']}.png"
                    req = urllib.request.Request(urls[0], headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=120) as resp:
                        out.write_bytes(resp.read())
                    print(f"DONE {job['key']} credits={data.get('creditsConsumed')}", flush=True)
                del pending[task_id]
            elif state == "fail":
                print(f"FAILED {job['key']}: {data.get('failCode')} {data.get('failMsg')}", flush=True)
                del pending[task_id]
    for _, job in pending.items():
        print(f"TIMEOUT {job['key']}", flush=True)
    print(f"TOTAL-CREDITS {total}", flush=True)


if __name__ == "__main__":
    main()
