# W8-11 simulation ROUND 6 — operator request: 2 distinct polarizing/meme-satire
# styles (humor from Virlo trend themes: AI agents vs manual busywork). EN default.
# Satire targets processes, never named people/competitors. DNA rules applied.
import json
import time
import urllib.request
from pathlib import Path

from round2 import API_KEY, CREATE, RECORD, UA

SIM = Path(__file__).parent
GPT = "gpt-image-2-text-to-image"

EN = " Render every word EXACTLY as written. No other readable text anywhere in the image."

JOBS = [
    dict(key="M1_robot_reaction_meme", model=GPT, folder=f"round6/{GPT}",
         input={"prompt": (
             "A two-panel vertical reaction meme as a premium editorial cartoon, warm cream "
             "paper ground (hex #F6F1E7), thin ink divider between panels. Recurring brand "
             "character: a charming retro cartoon robot, rounded indigo body (hex #302B87), "
             "teal accents (hex #00A39A), visible ink outlines, single-lens eye, no human "
             "face. TOP PANEL: the robot recoiling in comic horror, surrounded by flying "
             "paper sheets and sticky notes, tiny sweat drops; heavy grotesque caption above "
             "it: 'Hiring a fifth coordinator to copy-paste between apps.' BOTTOM PANEL: the "
             "same robot leaning back smugly in an office chair, feet on the desk, one arm "
             "sipping coffee, a tiny glowing checkmark floating; caption: 'One AI agent "
             "doing it while everyone sleeps.' — with 'while everyone sleeps.' emphasized in "
             "teal. Bold hand-drawn editorial-cartoon style, NOT childish clipart. Small "
             "letterspaced caps footer: 'HYPEDIGITALY'." + EN),
             "aspect_ratio": "4:5", "resolution": "1K"}),
    dict(key="M2_deadpan_memo", model=GPT, folder=f"round6/{GPT}",
         input={"prompt": (
             "A deadpan satirical corporate memo as a premium editorial card: warm cream "
             "paper (hex #F6F1E7) with subtle grain, styled like an official framed company "
             "document. Top: small letterspaced caps 'INTERNAL MEMO' with thin hairline "
             "rules above and below. Center: huge high-contrast editorial serif headline "
             "(Playfair spirit), near-black ink, three lines: 'The Monday' / 'status meeting' "
             "/ 'is cancelled.' Below, one calm serif body line: 'An AI agent already read "
             "the spreadsheet.' A slightly rotated teal (hex #00A39A) rubber-stamp imprint "
             "reading 'APPROVED BY AI' with distressed stamp texture, overlapping the "
             "headline's corner. Small letterspaced caps footer: 'HYPEDIGITALY'. Dry, "
             "official, funny — premium magazine satire, no clipart." + EN),
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
    for sub in (f"round6/{GPT}", "round6/prompts"):
        (SIM / sub).mkdir(parents=True, exist_ok=True)
    for job in JOBS:
        (SIM / "round6/prompts" / f"{job['key']}.txt").write_text(job["input"]["prompt"], encoding="utf-8")

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
    deadline = time.time() + 420
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
