# Nano Banana Pro — kie.ai API reference (operator-supplied, 2026-08-07)

Source: official kie.ai API documentation pasted by the operator on 2026-08-07. Authoritative for
W8-11 multi-model test-render integration. Endpoints are IDENTICAL to the existing nano-banana-2
integration (`media_gen.py` KieClient) — only the model string and input params differ.

## Model
- **model string (exact)**: `nano-banana-pro`
- Powered by Gemini 3.0 Pro. Marketing page claims: improved text rendering — spacing, alignment,
  character stability, "accurate localization" (relevant: Czech diacritics test target).

## Endpoints (same as existing)
- Create: `POST https://api.kie.ai/api/v1/jobs/createTask` — body `{"model": "nano-banana-pro", "input": {...}, "callBackUrl"?: str}`
- Poll: `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=...`
- States: `waiting` | `success` | `fail`; result in `resultJson` → `{"resultUrls": [...]}`
- Auth: `Authorization: Bearer <API_KEY>`

## input object
| Param | Type | Required | Notes |
|---|---|---|---|
| `prompt` | string | yes | max 20,000 chars |
| `image_input` | array of URLs | no | up to 8 reference images, ≤30MB each, jpeg/png/webp — **capability: can pass real logo/screenshot references** |
| `aspect_ratio` | string | no | `1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, auto` — default `1:1`. **Both our destinations supported: 16:9 (linkedin), 4:5 (instagram_feed), at any resolution** |
| `resolution` | string | no | `1K` (default), `2K`, `4K` |
| `output_format` | string | no | `png` (default), `jpg` |

## Price snapshot (2026-08-07, page-derived — VERIFY via creditsConsumed on first live call)
- ~$0.09/image at 1K–2K (≈18 credits @ $0.005), ~$0.12/image at 4K (≈24 credits).
  (Page also showed $0.082/1K-2K and $0.134 figures on other SKUs/top-up tiers — treat $0.09 as
  planning figure, reconcile against `creditsConsumed` exactly as the ledger already does for
  nano-banana-2.)

## Error codes
200 ok · 400 bad params · 401 auth · 402 insufficient credits · 404 · 422 validation · 429 rate limit · 500 internal.
