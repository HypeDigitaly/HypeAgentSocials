# Canonical-path compositor for the W8-11 simulation. Implements the spec's zone
# geometry with Pillow: photoreal grounds get composited captions; ig_operator_grid
# and ig_value_sheet are built fully programmatically. Desk-check only.
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIM = Path(__file__).parent
CANON = SIM / "canonical"
FONTS = SIM / "fonts"

W, H = 1080, 1350


def font(name: str, wght: int, size: int) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONTS / f"{name}.ttf"), size)
    f.set_variation_by_axes([wght])
    return f


def cover_fit(img: Image.Image, w: int, h: int) -> Image.Image:
    scale = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((left, top, left + w, top + h))


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tracked_text(draw, xy, text, fnt, fill, tracking=5.0):
    """Letterspaced small-caps furniture rows. Draws char-by-char (whitespace is
    advanced, never drawn -- some variable-font instances tofu the space glyph)."""
    x, y = xy
    for ch in text:
        if ch.isspace():
            x += fnt.size * 0.45 + tracking
            continue
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def tracked_width(draw, text, fnt, tracking=5.0):
    w = 0.0
    for ch in text:
        w += (fnt.size * 0.45 if ch.isspace() else draw.textlength(ch, font=fnt)) + tracking
    return w


def composited_caption(ground_name, out_name, lines, *, size_pct, wght, zone, align,
                       canvas=(W, H)):
    src = CANON / ground_name
    if not src.exists():
        print(f"SKIP {out_name} (missing {ground_name})")
        return
    cw, ch = canvas
    base = cover_fit(Image.open(src).convert("RGB"), cw, ch).convert("RGBA")
    fnt = font("Montserrat", wght, round(ch * size_pct))
    x0, y0, zw, zh = zone[0] * cw, zone[1] * ch, zone[2] * cw, zone[3] * ch
    line_h = round(ch * size_pct * 1.25)

    # soft 40%-black shadow layer for legibility on photo grounds (spec: plain ink, no pill)
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    mdraw = ImageDraw.Draw(base)
    y = y0
    for line in lines:
        x = x0 + (zw - mdraw.textlength(line, font=fnt)) / 2 if align == "center" else x0
        sdraw.text((x + 2, y + 3), line, font=fnt, fill=(0, 0, 0, 110))
        y += line_h
    base = Image.alpha_composite(base, shadow.filter(ImageFilter.GaussianBlur(4)))

    draw = ImageDraw.Draw(base)
    y = y0
    for line in lines:
        x = x0 + (zw - draw.textlength(line, font=fnt)) / 2 if align == "center" else x0
        draw.text((x, y), line, font=fnt, fill="#FFFFFF")
        y += line_h
    base.convert("RGB").save(CANON / out_name)
    print(f"BUILT {out_name}")


def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0], img.size[1]], radius=radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def build_operator_grid():
    img = Image.new("RGB", (W, H), "#F3F1E9")
    draw = ImageDraw.Draw(img)
    for x in range(0, W, 54):
        draw.line([(x, 0), (x, H)], fill="#E4E0D2", width=1)
    for y in range(0, H, 54):
        draw.line([(0, y), (W, y)], fill="#E4E0D2", width=1)

    ink, indigo, amber = "#221F1C", "#302B87", "#E8A63B"
    body_ink, footer_ink = "#332F2B", "#6B655C"

    mast = font("Montserrat", 700, 26)
    tracked_text(draw, (86, 78), "HYPEDIGITALY", mast, ink)
    label_w = tracked_width(draw, "AI PROVOZ", mast)
    tracked_text(draw, (W - 86 - label_w, 78), "AI PROVOZ", mast, ink)
    draw.line([(86, 132), (W - 86, 132)], fill=footer_ink, width=2)

    pill_f = font("Montserrat", 600, 24)
    pw = tracked_width(draw, "PLAYBOOK 03", pill_f, 4)
    draw.rounded_rectangle([86, 180, 86 + pw + 44, 234], radius=27, outline=ink, width=2)
    tracked_text(draw, (108, 194), "PLAYBOOK 03", pill_f, ink, 4)

    # headline rows with per-row available width (row 1 sits beside the photo
    # inset) and global shrink-to-fit -- the sim equivalent of the plan's
    # fit_text contract; a fixed size overflowed on the first attempt.
    inset_w, inset_y0, inset_y1 = 220, 156, 376
    rows = [
        ("Agentura, která", [("Agentura, která", ink)], W - 2 * 86 - inset_w - 28),
        ("odpovídá do pěti minut,", [("odpovídá ", ink), ("do pěti minut", indigo), (",", ink)], W - 2 * 86),
        ("vyhrává.", [("vyhrává.", ink)], W - 2 * 86),
    ]
    size = 96
    while size > 40:
        head = font("Montserrat", 850, size)
        if all(draw.textlength(text, font=head) <= max_w for text, _, max_w in rows):
            break
        size -= 2
    head = font("Montserrat", 850, size)
    line_h = round(size * 1.18)
    y = 300
    bar_w = draw.textlength("vyhrává.", font=head)
    draw.rectangle([80, y + 2 * line_h + round(size * 0.22), 80 + bar_w + 28, y + 2 * line_h + round(size * 1.08)], fill=amber)
    for _, parts, _ in rows:
        x = 86
        for text, color in parts:
            draw.text((x, y), text, font=head, fill=color)
            x += draw.textlength(text, font=head)
        y += line_h

    body_f = font("Montserrat", 400, 30)
    draw.text((86, y + 42), "Postup, který používáme u klientů od prvního dne.", font=body_f, fill=body_ink)

    inset_src = CANON / "3_grid_inset_ground.png"
    if inset_src.exists():
        inset = rounded(cover_fit(Image.open(inset_src).convert("RGB"), inset_w, inset_y1 - inset_y0), 24)
        img.paste(inset, (W - 86 - inset_w, inset_y0), inset)
        draw = ImageDraw.Draw(img)

    foot_f = font("Montserrat", 600, 24)
    ft = "Posunout →"
    fw = draw.textlength(ft, font=foot_f)
    draw.rounded_rectangle([86, H - 130, 86 + fw + 48, H - 76], radius=27, outline=footer_ink, width=2)
    draw.text((110, H - 117), ft, font=foot_f, fill=footer_ink)
    badge = "1/5"
    draw.text((W - 86 - draw.textlength(badge, font=foot_f), H - 117), badge, font=foot_f, fill=footer_ink)

    img.save(CANON / "3_operator_grid_cover_FINAL.png")
    print("BUILT 3_operator_grid_cover_FINAL.png")


def build_value_sheet():
    img = Image.new("RGB", (W, H), "#1E1B2E")
    draw = ImageDraw.Draw(img)
    teal, off_white, indigo = "#00A39A", "#EDEAE3", "#302B87"

    kick_f = font("Lora", 600, round(H * 0.022))
    tracked_text(draw, (round(W * 0.08), round(H * 0.06)), "KATEGORIE 02 · AUTOMATIZACE", kick_f, teal, 3)
    cnt_f = font("Lora", 400, round(H * 0.020))
    cnt = "4/10"
    draw.text((round(W * 0.92) - draw.textlength(cnt, font=cnt_f), round(H * 0.06)), cnt, font=cnt_f, fill="#FFFFFF")
    draw.line([(round(W * 0.08), round(H * 0.105)), (round(W * 0.92), round(H * 0.105))], fill=indigo, width=2)

    from run_sim import VALUE_SHEET_ENTRIES
    body_f = font("Lora", 400, round(H * 0.0185))  # the spec's 1.85% type floor, ~25px
    x0, y = round(W * 0.08), round(H * 0.13)
    max_w = round(W * 0.84)
    line_h = round(H * 0.0185 * 1.2)
    for entry in VALUE_SHEET_ENTRIES:
        for line in wrap(draw, entry, body_f, max_w):
            draw.text((x0, y), line, font=body_f, fill=off_white)
            y += line_h
        y += round(line_h * 0.9)

    seg_w = round(W * 0.84 / 10) - 6
    for i in range(10):
        x = round(W * 0.08) + i * (seg_w + 6)
        draw.rectangle([x, round(H * 0.90), x + seg_w, round(H * 0.905)], fill=teal if i < 4 else "#3A3552")

    img.save(CANON / "4_value_sheet_body_FINAL.png")
    print("BUILT 4_value_sheet_body_FINAL.png")


if __name__ == "__main__":
    composited_caption("1_lifestyle_cover_ground.png", "1_lifestyle_cover_FINAL.png",
                       ["5 nástrojů, které zvládnou", "vaše ráno za vás"],
                       size_pct=0.045, wght=630, zone=(0.10, 0.20, 0.60, 0.14), align="left")
    composited_caption("2_scene_hook_ground.png", "2_scene_hook_cover_FINAL.png",
                       ["Zatímco spíte,", "AI pracuje."],
                       size_pct=0.052, wght=700, zone=(0.10, 0.66, 0.80, 0.14), align="center")
    composited_caption("5_li_hero_ground.png", "5_li_hero_FINAL.png",
                       ["Automatizace nepropouští.", "Uvolňuje kapacitu."],
                       size_pct=0.055, wght=700, zone=(0.10, 0.64, 0.80, 0.18), align="center",
                       canvas=(1920, 1080))
    build_operator_grid()
    build_value_sheet()
