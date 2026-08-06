# Run Trace Log — specification (W8-5)

*Written 2026-08-07 from the operator's requirement: "super detailed log file for each and every run of the entire flow so that we can see how the latest run of this entire app went step by step for debugging — with timestamps, platforms / APIs called, inputs, outputs, etc." Registered as decision W8-5; Phase-1 deliverable and acceptance item. Complements — never replaces — the run ledger, scorecards and digest (§8, §11, §12 of `ARCHITECTURE_PLAN.md`): the ledger and digest say what a run concluded; the trace says what it did, in order, with evidence.*

## 1. What every run produces

```
logs/
  runs/
    <run_id>/                  # run_id = pinned run-date + short uid, e.g. 2026-08-10_a3f2
      trace.jsonl              # machine trace — append-only, one JSON event per line
      trace.md                 # human rendering, generated at run end (or on crash, from whatever trace.jsonl holds)
  latest -> runs/<run_id>      # pointer file (Windows: latest.txt containing the path) — "how did the LATEST run go"
```

- `trace.jsonl` is **append-only and written as events happen**, never buffered until run end — a crashed run's trace ends at the crash line, which is exactly the debugging value.
- `trace.md` is a rendering of the JSONL (grouped by stage, with a timing waterfall and an API-call table). If the run died before rendering, a `render-trace` utility regenerates it from the JSONL.
- The run ledger entry for the run carries the trace path; the digest links it.

## 2. Event schema (trace.jsonl)

Every line:

```json
{
  "ts": "2026-08-10T03:14:07.412+02:00",   // ISO 8601, milliseconds, explicit offset
  "run_id": "2026-08-10_a3f2",
  "seq": 141,                               // monotonic per run — gap = lost write, detectable
  "stage": "collection",                    // canonical stage name from the plan's stage order
  "event": "api_call",                      // see event types below
  "detail": { ... }                         // per-type payload, below
}
```

**Event types and their `detail` payloads:**

| event | detail carries |
|---|---|
| `run_start` | mode (interactive/scheduled), theme, config fingerprint (hash of resolved config), engine version/commit, caps in force |
| `stage_start` / `stage_end` | stage name; on end: outcome (ok / degraded / failed-closed), duration_ms, items in/out counts |
| `api_call` | `platform` (virlo / notion / kie / postiz / dataforseo / gnews / youtube / meta_adlib / elevenlabs / smtp / …), `endpoint`, `method`, `request` (**redacted** — full parameters minus secrets and minus embedded third-party personal data; bodies over 2 KB summarised with byte count + hash), `attempt` (1..n), `purpose` (one plain-English line: "poll niche monitor for weekly cycle") |
| `api_response` | matching `seq_of_call`, `status` (HTTP or vendor code), `latency_ms`, `bytes`, `ids_returned` (vendor object ids), `cost` (credits / tokens / money, when the vendor reports or the ledger computes it), `outcome_class` (ok / transient / permanent-auth / permanent-endpoint — §6.2's failure taxonomy), `response_summary` (key fields only, same redaction rules) |
| `gate_verdict` | gate name (spin / claim-pass-1 / voice / claim-pass-2 / platform / prohibited-outcome / overlay / publish), asset id, verdict, the specific failing span or rule when failed, regeneration counter state |
| `artifact_write` | path (repo-relative), kind (scorecard / pack / master / draft / digest), bytes, sha256 |
| `spend` | wallet (media / text), expected vs ledger-recorded amount, balance-delta when observable (§5.4, W2-02) |
| `degrade` | which named degrade condition fired (§6.5 / §11.3 vocabulary, verbatim), what it caused |
| `decision` | any operator-visible decision the engine took alone (fallback chosen, cap hit, skip-overlap), with the rule that authorised it |
| `error` | class, message, stack hash (full stack to a sidecar file, not the trace), whether retried, final disposition |
| `run_end` | exit class (the §11 taxonomy verbatim), totals: duration, API calls per platform, spend per wallet, items per stage, degrades count |

**Answering "what were the inputs and outputs" without bloating the trace:** every stage's `stage_end` carries `input_refs` / `output_refs` — paths + sha256 of the actual artifacts (research store items, scorecards, packs). The trace points at the data; the data itself lives where the plan already puts it. A debugging session is: open `trace.md`, find the step, follow the ref.

## 3. Redaction rules (hard, non-optional)

1. **Secrets never appear** — no Authorization headers, tokens, keys, or cookie material, in either request or response logging. The logger redacts by allowlist (named safe fields), not by blocklist.
2. **Author handles and permalinks are redacted from logged request payloads** exactly as they are from prompt payloads (R4-M7) — the trace must not become a shadow store of who-said-what.
3. **Verbatim third-party text is not embedded in the trace.** The trace stores the canonical key + hash of collected items; the text lives in the research artifact store under its own 30-day expiry (§2.6). Otherwise the trace would silently outlive the retention rule it sits beside. (This is why `request`/`response_summary` carry ids and hashes, not content.)
4. Trace retention: **90 days** (aligned with de-identified signals), then the run directory's traces are deleted; `trace.md` summaries MAY be kept longer since they carry no third-party content by construction.

## 4. Debug ergonomics

- `TRACE_LEVEL=debug` env flag adds `api_call.request_raw_bytes`-style extra fields for a single supervised run — never the default, never in scheduled mode.
- Czech text in logs is UTF-8 end to end; the Phase-5 acceptance item "Czech characters survive the console and the log files" applies to the trace explicitly.
- Every event's `seq` is monotonic; `render-trace` flags sequence gaps ("events lost here") instead of hiding them.
- The waterfall in `trace.md` shows per-stage wall-clock alongside per-API cumulative latency — the two numbers that answer "why was last night's run slow."

## 5. Phase-1 acceptance (added to the phase gate by W8-5)

A Phase-1 run is not accepted until: **(a)** its `trace.jsonl` reconstructs the complete external-call sequence (platform, endpoint, status, latency, cost) without reading the code; **(b)** a deliberately killed run leaves a truncated-but-valid trace whose last line is the true last action; **(c)** the redaction rules hold on inspection of a real trace (no secret, no handle, no embedded third-party text); **(d)** `trace.md` for the latest run is reachable from the digest in one step.
