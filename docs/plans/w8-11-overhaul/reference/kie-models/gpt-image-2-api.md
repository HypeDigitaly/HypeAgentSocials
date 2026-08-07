# GPT Image 2 (text-to-image) — kie.ai API reference (operator-supplied, 2026-08-07)

Source: official kie.ai API documentation pasted by the operator on 2026-08-07. Authoritative for
W8-11 multi-model test-render integration. Endpoints IDENTICAL to existing integration.

## Model
- **model string (exact)**: `gpt-image-2-text-to-image`
- (An `gpt-image-2-image-to-image` sibling exists on docs.kie.ai — out of scope for W8-11.)

## Endpoints (same as existing)
- Create: `POST https://api.kie.ai/api/v1/jobs/createTask` — body `{"model": "gpt-image-2-text-to-image", "input": {...}, "callBackUrl"?: str}`
- Poll: `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=...`
- States: `waiting` | `success` | `fail`; result in `resultJson` → `{"resultUrls": [...]}`

## input object
| Param | Type | Required | Notes |
|---|---|---|---|
| `prompt` | string | yes | max 20,000 chars |
| `aspect_ratio` | string | no | `auto` (default), `1:1, 3:2, 2:3, 4:3, 3:4, 16:9, 9:16, 2:1, 1:2, 3:1, 1:3, 21:9, 9:21, 5:4, 4:5` |
| `resolution` | string | no | `1K` (default), `2K`, `4K` |

**HARD CONSTRAINT:** at `2K`/`4K` these aspect ratios are NOT supported: `5:4, 4:5, 3:1, 1:3, 9:21`.
⇒ **Instagram 4:5 renders on this model MUST pin `resolution: "1K"`.** LinkedIn 16:9 has no such limit.
No `output_format` param documented (PNG assumed); no `image_input` on the text-to-image variant.

## Price snapshot (2026-08-07, page-derived — VERIFY via creditsConsumed on first live call)
- Two SKU figures observed on the marketing page: ~$0.015/1K, $0.025/2K, $0.04/4K (3/5/8 credits)
  on one tier and ~$0.03/1K, $0.05/2K, $0.08/4K (6/10/16 credits) on another. Planning figure:
  $0.03/image at 1K; reconcile against `creditsConsumed` on first live call.

## Error codes
200 ok · 400 bad params · 401 auth · 402 insufficient credits · 404 · 422 validation · 429 rate limit · 500 internal.
