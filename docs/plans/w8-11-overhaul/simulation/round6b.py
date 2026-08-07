# Round 6b — operator feedback on the meme pair: (1) top panel must be a HUMAN
# (from behind / face obscured — persona rule carve-out for cartoon classes) so the
# human-vs-agent contrast makes sense; captions minimal + symmetric for 1-second
# readability. (2) memo joke must be instant — switch to RIP-tombstone grammar.
import json
import time
import urllib.request
from pathlib import Path

from round2 import API_KEY, CREATE, RECORD, UA

SIM = Path(__file__).parent
GPT = "gpt-image-2-text-to-image"

EN = " Render every word EXACTLY as written. No other readable text anywhere in the image."

JOBS = [
    dict(key="M1v2_human_vs_agent", model=GPT, folder=f"round6/{GPT}",
         input={"prompt": (
             "A two-panel vertical comparison meme as a premium editorial cartoon, warm "
             "cream paper ground (hex #F6F1E7), thin ink divider. TOP PANEL, caption in "
             "heavy grotesque: 'Your ops team at 11 PM.' — a cartoon HUMAN office worker "
             "seen strictly FROM BEHIND (face never visible), hunched over a desk lit by a "
             "harsh monitor glare, hair disheveled, surrounded by chaos: toppling paper "
             "stacks, sticky notes everywhere, three cold coffee cups, a tangled phone "
             "cord. Frantic energy, ink outlines. BOTTOM PANEL, caption: 'The AI agent at "
             "11 PM.' — the recurring brand robot (rounded indigo body hex #302B87, teal "
             "accents hex #00A39A, single-lens eye, ink outlines) leaning back serenely in "
             "an office chair, feet on a TIDY desk, sipping tea, a small lamp glowing "
             "warmly, one neat stack of finished documents with a teal checkmark. The "
             "humor is the perfect symmetry of the two captions and the total contrast of "
             "the scenes. Vintage comic texture, NOT childish clipart. Small letterspaced "
             "caps footer: 'HYPEDIGITALY'." + EN),
             "aspect_ratio": "4:5", "resolution": "1K"}),
    dict(key="M2v2_rip_tombstone", model=GPT, folder=f"round6/{GPT}",
         input={"prompt": (
             "A satirical cartoon gravestone scene, instantly readable at first glance: a "
             "sunny, cheerful little hill with green grass and flowers under a bright sky "
             "— festive confetti falling. Center: a classic rounded stone tombstone with "
             "engraved serif text: 'R.I.P.' large at top, below it 'THE MONDAY' / 'STATUS "
             "MEETING' / '2004 – 2026', and at the bottom in smaller italic: 'An AI agent "
             "read the spreadsheet.' A tiny party hat sits crookedly on top of the stone. "
             "Beside the grave, the recurring brand robot (rounded indigo body hex "
             "#302B87, teal accents hex #00A39A, single-lens eye, ink outlines) solemnly "
             "lays a single flower while holding a small teal balloon. Premium editorial "
             "cartoon style, warm palette on cream (hex #F6F1E7) sky tint, ink outlines, "
             "vintage texture. Small letterspaced caps footer: 'HYPEDIGITALY'." + EN),
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
    pending = {}
    for job in JOBS:
        (SIM / "round6/prompts" / f"{job['key']}.txt").write_text(job["input"]["prompt"], encoding="utf-8")
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
