# Recovery collector for run_sim.py's batch: polls the already-created task IDs
# and downloads results with a browser User-Agent (the bare-urllib UA gets 403
# from the result CDN).
import json
import time
import urllib.request
from pathlib import Path

from run_sim import API_KEY, RECORD

SIM = Path(__file__).parent

TASKS = {
    "3673cff7acc86ccc1d00c34bb120f408": ("canonical", "1_lifestyle_cover_ground"),
    "476e56b534b08f32b3e002ee838b3347": ("canonical", "2_scene_hook_ground"),
    "884fd107aea2db3a87860b6d9a0d973b": ("canonical", "5_li_hero_ground"),
    "c1bd4ea2cefd031eb220d98f9fb669e1": ("canonical", "3_grid_inset_ground"),
    "a954c24919342c2bc7c2bdd357329547": ("canonical", "6_logo_probe"),
    "6d7a933ac166aa1c8677888ec30518d5": ("models/gpt-image-2-text-to-image", "1_lifestyle_cover"),
    "ddb9de47fcb8506a2f71d4895fdd06a1": ("models/gpt-image-2-text-to-image", "2_scene_hook_cover"),
    "7d285a00897c71ac6671c0a3d72bee2a": ("models/gpt-image-2-text-to-image", "3_operator_grid_cover"),
    "b22ac87b26158f53345be53ea7214402": ("models/gpt-image-2-text-to-image", "4_value_sheet_body"),
    "09efdf3fc1530c543736d6b18a33e079": ("models/gpt-image-2-text-to-image", "5_li_hero"),
    "9b2b15a7f18332a003d68a533c556d16": ("models/gpt-image-2-text-to-image", "6_logo_probe"),
    "aee51f6dbe8af031c616dbb39c5a322a": ("models/nano-banana-pro", "1_lifestyle_cover"),
    "d1e477531ad09ba3cb37f250883eb851": ("models/nano-banana-pro", "2_scene_hook_cover"),
    "6ebff8d2b4273ed156775673a9fee141": ("models/nano-banana-pro", "3_operator_grid_cover"),
    "6d54c084ee35655a08c161e43a253783": ("models/nano-banana-pro", "4_value_sheet_body"),
    "7cdaae916149052622db87d5b33ea95f": ("models/nano-banana-pro", "5_li_hero"),
    "25591bac54d2f86a73590880f19718fc": ("models/nano-banana-pro", "6_logo_probe"),
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def get(url: str, auth: bool) -> bytes:
    headers = {"User-Agent": UA}
    if auth:
        headers["Authorization"] = f"Bearer {API_KEY}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as resp:
        return resp.read()


def main() -> None:
    pending = dict(TASKS)
    total_credits = 0.0
    deadline = time.time() + 600
    while pending and time.time() < deadline:
        for task_id in list(pending):
            folder, key = pending[task_id]
            try:
                payload = json.loads(get(f"{RECORD}?taskId={task_id}", auth=True))
            except Exception as exc:
                print(f"POLL-ERROR {key}: {exc}", flush=True)
                continue
            data = payload.get("data") or {}
            state = data.get("state")
            if state == "success":
                urls = json.loads(data.get("resultJson") or "{}").get("resultUrls") or []
                credits = float(data.get("creditsConsumed") or 0)
                total_credits += credits
                if urls:
                    out = SIM / folder / f"{key}.png"
                    out.write_bytes(get(urls[0], auth=False))
                    print(f"DONE {folder}/{key} credits={credits}", flush=True)
                else:
                    print(f"DONE-NO-URL {folder}/{key}", flush=True)
                del pending[task_id]
            elif state == "fail":
                print(f"FAILED {folder}/{key}: {data.get('failCode')} {data.get('failMsg')}", flush=True)
                del pending[task_id]
        if pending:
            time.sleep(12)
    for task_id, (folder, key) in pending.items():
        print(f"TIMEOUT {folder}/{key} ({task_id})", flush=True)
    print(f"TOTAL-CREDITS {total_credits}", flush=True)


if __name__ == "__main__":
    main()
