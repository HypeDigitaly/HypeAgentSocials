# W8-11 simulation ROUND 5 — brand-promo class (operator request): HypeDigitaly
# service posts with explicit CTA "Klikněte na odkaz v popisku", generated
# regularly with every batch. Deliberately promotional — exempt from the
# anti-ad DON'Ts that govern organic classes. Brand palette strict.
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
    "The typography is the hero: oversized expressive display type, deliberate "
    "hierarchy, tight leading. Premium editorial design — a confident brand ad, "
    "not a cheap flyer. "
)
CTA = (
    "At the bottom, a prominent rounded pill button in teal (hex #00A39A) with white "
    "bold text: 'Klikněte na odkaz v popisku'. "
)

JOBS = [
    dict(key="P1_ai_audit", model=GPT, folder=f"round5/{GPT}",
         input={"prompt": (
             "A bold brand promo card, solid deep indigo ground (hex #302B87), flat, no "
             "gradients. " + TYPO + "Top: small letterspaced caps wordmark 'HYPEDIGITALY' in "
             "white. Huge white grotesque headline: 'AI audit' with the word 'zdarma.' below "
             "it in teal (hex #00A39A). One calm body line in white: 'Zjistíme, kde vám AI "
             "ušetří nejvíc času.' " + CTA + "A thin white hairline rule above the button."
             + CZ),
             "aspect_ratio": "4:5", "resolution": "1K"}),
    dict(key="P2_ai_agent", model=GPT, folder=f"round5/{GPT}",
         input={"prompt": (
             "A bold brand promo card, solid near-black ground (hex #1E1B2E), flat. " + TYPO
             + "Top: small letterspaced caps wordmark 'HYPEDIGITALY' in warm off-white. Huge "
             "white grotesque headline over two lines: 'Chcete nasadit' / 'AI agenta?' — with "
             "'AI agenta?' in teal (hex #00A39A). One calm body line in warm off-white (hex "
             "#EDEAE3): 'Postavíme ho na míru vašim procesům.' A subtle amber (hex #E8A63B) "
             "hand-drawn underline under the word 'nasadit'. " + CTA + CZ),
             "aspect_ratio": "4:5", "resolution": "1K"}),
    dict(key="P3_ai_do_firmy", model=GPT, folder=f"round5/{GPT}",
         input={"prompt": (
             "An elegant brand promo card on warm cream paper (hex #F6F1E7) with subtle "
             "paper grain. " + TYPO + "Top: small letterspaced caps wordmark 'HYPEDIGITALY' "
             "in teal. Huge high-contrast serif headline (Playfair-Display spirit) in "
             "near-black ink over two lines: 'Jak zařadit AI' / 'do firmy?' — with 'do "
             "firmy?' in italic deep indigo (hex #302B87). One calm body line: 'Projdeme to "
             "s vámi krok za krokem.' " + CTA + CZ),
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
    for sub in (f"round5/{GPT}", "round5/prompts"):
        (SIM / sub).mkdir(parents=True, exist_ok=True)
    for job in JOBS:
        (SIM / "round5/prompts" / f"{job['key']}.txt").write_text(job["input"]["prompt"], encoding="utf-8")

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
