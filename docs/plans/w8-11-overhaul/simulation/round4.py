# W8-11 simulation ROUND 4 — operator's "wilder visuals" request:
#   1) FULL realistic fictional AI-built website (not abstract blocks)
#   2) AI-agent robot caricature
#   3) complex dashboard in a wild isometric style
#   4) anime-style post
# Integrity line: rich FICTIONAL sites/dashboards are allowed illustration;
# a real product's own UI is still never invented. Characters faceless/from-behind.
import json
import time
import urllib.request
from pathlib import Path

from round2 import API_KEY, CREATE, RECORD, UA

SIM = Path(__file__).parent
GPT = "gpt-image-2-text-to-image"

CZ = (
    " Render every character EXACTLY as written, including all Czech diacritics "
    "(á č ď é ě í ň ó ř š ť ů ú ý ž). No other readable text anywhere in the image."
)
TYPO = (
    "The typography is the hero: oversized expressive display type, deliberate hierarchy, "
    "tight leading, one word emphasized in teal (hex #00A39A). Premium editorial "
    "social-first design. "
)

JOBS = [
    dict(key="1_full_website", model=GPT, folder=f"round4/{GPT}",
         input={"prompt": (
             "A clean editorial card on warm cream paper (hex #F6F1E7). " + TYPO
             + "Small caps kicker in teal: 'NOVÝ TREND'. Heavy grotesque headline over two "
             "lines: 'Firma bez webu?' / 'Do večera to jde.' Below, a large rounded "
             "browser-window frame with a subtle shadow showing a COMPLETE, polished, "
             "realistic FICTIONAL bakery website: appetizing hero photograph of fresh bread, "
             "elegant menu bar, product card row with pastry photos, a teal call-to-action "
             "button. The ONLY legible text inside the website is: 'Pekárna U Lípy', 'Naše "
             "pečivo', 'Objednat' — all other site text is soft-blurred greeked lines. Under "
             "the browser, two calm body lines: 'Claude napíše texty z vašich recenzí.' / "
             "'Lovable z nich postaví web.' Footer caps: 'HYPEDIGITALY'." + CZ),
             "aspect_ratio": "4:5", "resolution": "1K"}),
    dict(key="2_robot_caricature", model=GPT, folder=f"round4/{GPT}",
         input={"prompt": (
             "A playful editorial illustration card, flat warm cream ground (hex #F6F1E7). "
             + TYPO + "A charming cartoon robot with a rounded retro body in indigo (hex "
             "#302B87) with teal accents, sitting at a tiny desk, six arms simultaneously "
             "juggling floating icons: an envelope, a calendar page, an invoice sheet, a chat "
             "bubble, a bar chart, a coffee cup. Bold hand-drawn illustration style with "
             "visible ink outlines, NOT childish clipart — think premium New-Yorker-adjacent "
             "editorial cartoon. The robot has a friendly single-lens eye, no human face. "
             "Heavy grotesque headline above: 'Kolega, který nikdy nespí.' One body line "
             "below: 'AI agent hlídá e-maily, schůzky i faktury.' Footer caps: "
             "'HYPEDIGITALY'." + CZ),
             "aspect_ratio": "4:5", "resolution": "1K"}),
    dict(key="3_wild_dashboard", model=GPT, folder=f"round4/{GPT}",
         input={"prompt": (
             "A bold isometric 3D illustration on a deep indigo ground (hex #1E1B2E). "
             + TYPO + "A dramatic FICTIONAL 'mission control' automation command center "
             "rendered as an isometric diorama: layered floating glass panels with glowing "
             "teal (hex #00A39A) graphs, gauges and node-graphs, tiny conveyor belts moving "
             "document cards between stations, small robot arms sorting them, amber (hex "
             "#E8A63B) accent lights. Rich detail, cinematic depth, premium tech-editorial "
             "illustration — clearly an artistic concept, not any real software product. All "
             "panel text is greeked/illegible marks. Heavy white grotesque headline across "
             "the top: 'Velín vaší firmy.' One body line below in warm off-white: 'Všechny "
             "procesy na jednom místě. Řídí je AI agenti.' Footer caps: 'HYPEDIGITALY'." + CZ),
             "aspect_ratio": "4:5", "resolution": "1K"}),
    dict(key="4_anime_scene", model=GPT, folder=f"round4/{GPT}",
         input={"prompt": (
             "A hand-drawn anime-style illustration, painterly and atmospheric: a cozy dark "
             "office at night seen from behind — a character in a hoodie viewed strictly FROM "
             "BEHIND (face never visible), sitting before a large glowing monitor wall, city "
             "lights and rain beyond the window, warm desk lamp, steam rising from a mug. "
             "Cinematic anime lighting, detailed background art, soft glow. The monitors show "
             "only abstract glowing shapes, no readable UI. " + TYPO + "Large cinematic "
             "display type integrated in the lower third, two lines, white with teal "
             "emphasis: 'Zatímco spíte,' / 'AI pracuje.' Footer caps: 'HYPEDIGITALY'." + CZ),
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
    for sub in (f"round4/{GPT}", "round4/prompts"):
        (SIM / sub).mkdir(parents=True, exist_ok=True)
    for job in JOBS:
        (SIM / "round4/prompts" / f"{job['key']}.txt").write_text(job["input"]["prompt"], encoding="utf-8")

    pending = {}
    for job in JOBS:
        try:
            r = api(CREATE, {"model": job["model"], "input": job["input"]})
            task_id = (r.get("data") or {}).get("taskId")
            if r.get("code") == 200 and task_id:
                pending[task_id] = job
                print(f"CREATED {job['key']} -> {task_id}", flush=True)
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
