# Bundled fonts — OD-10 deliverable

*Written 2026-08-06. Governing text: `ARCHITECTURE_PLAN.md` §17.2 Phase 0 ("The pinned FFmpeg version installed on the target platform with fonts bundled and Czech glyph coverage verified — OD-10").*

## What is bundled

| File | What | License |
|---|---|---|
| `NotoSans-Variable.ttf` | Noto Sans, variable font (weight + width axes), full Czech/Latin-Extended coverage | SIL OFL 1.1 (`OFL.txt`, bundled as required) |
| `czech_glyph_test.txt` | The glyph test corpus: both pangram cases, the full diacritic set `ěščřžýáíéúůďťňó / ĚŠČŘŽÝÁÍÉÚŮĎŤŇÓ`, `Kč`, em-dash, Czech low-99 quotation marks | — |
| `czech_glyph_test.png` | The rendered evidence, produced by FFmpeg `drawtext` with the bundled font on 2026-08-06 — **all glyphs render, zero .notdef boxes** | — |

## Verification verdict (2026-08-06)

**PASS.** Czech glyph coverage is complete in the bundled font as rendered by the pinned FFmpeg's drawtext on the target platform (Windows 11). Evidence: `czech_glyph_test.png`.

## Two findings the assembly engine must respect (found during this test, not theoretical)

1. **Literal newlines render as visible .notdef boxes.** In the pinned FFmpeg build, a `\n` inside a `drawtext` `textfile` is drawn as a missing-glyph box at the end of each line rather than acting only as a line break. Multi-line on-screen text must therefore be composed as **one drawtext invocation per line** (or via libass/ASS subtitles, which handle line breaks correctly) — never by feeding raw multi-line text to a single drawtext. This constrains §4.4/§8's overlay composition.
2. **CRLF is a glyph too.** Text files written with Windows line endings put a `\r` box at every line end. Any text handed to FFmpeg must be **UTF-8, LF-normalized, no BOM**. The engine's overlay writer must normalize line endings before composition.

Both findings will re-verify automatically every time the glyph test is re-run (it must be re-run after any FFmpeg upgrade — see `../../config/ffmpeg_pin.yaml`).

## Re-running the test

```
ffmpeg -y -f lavfi -i color=white:s=1400x500 \
  -vf "drawtext=fontfile=assets/fonts/NotoSans-Variable.ttf:textfile=<one line per invocation>:fontsize=44:fontcolor=black:x=50:y=<per line>" \
  -frames:v 1 assets/fonts/czech_glyph_test.png
```

Inspect the output for missing-glyph boxes. A failed test blocks any FFmpeg or font change from landing.
