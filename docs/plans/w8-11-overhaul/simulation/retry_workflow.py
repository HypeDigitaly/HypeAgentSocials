# Retry the failed nano-banana-pro workflow_map_cs_refs with query-string-free
# reference URLs (the ?utm_... suffix is the suspected 500 trigger).
import json
import time
import urllib.request
from pathlib import Path

from round2 import API_KEY, CREATE, RECORD, UA, CONCEPTS, NBP_REF_NOTE

SIM = Path(__file__).parent

REFS = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Zapier_logo.svg/960px-Zapier_logo.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Claude_AI_symbol.svg/960px-Claude_AI_symbol.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Gmail_icon_%282020%29.svg/960px-Gmail_icon_%282020%29.svg.png",
]


def api(url, body=None):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "User-Agent": UA},
        method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


r = api(CREATE, {"model": "nano-banana-pro", "input": {
    "prompt": CONCEPTS[3][1]["cs"] + NBP_REF_NOTE + "1 Zapier, 2 Claude, 3 Gmail.",
    "image_input": REFS, "aspect_ratio": "4:5", "resolution": "1K", "output_format": "png"}})
task_id = (r.get("data") or {}).get("taskId")
print("created", task_id, r.get("code"), r.get("msg"), flush=True)

deadline = time.time() + 420
while task_id and time.time() < deadline:
    time.sleep(12)
    data = api(f"{RECORD}?taskId={task_id}").get("data") or {}
    state = data.get("state")
    if state == "success":
        urls = json.loads(data.get("resultJson") or "{}").get("resultUrls") or []
        if urls:
            out = SIM / "round2/nano-banana-pro/4_workflow_map_cs_refs.png"
            req = urllib.request.Request(urls[0], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                out.write_bytes(resp.read())
            print("DONE credits=", data.get("creditsConsumed"), flush=True)
        break
    if state == "fail":
        print("FAILED", data.get("failCode"), data.get("failMsg"), flush=True)
        break
