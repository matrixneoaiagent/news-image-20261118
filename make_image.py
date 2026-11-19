"""Render the make.fun "news image" entry as a deterministic 1024x1024 PNG.

Draws a near-black "world news" front page for Wednesday 18 November 2026:
a bold header, then a 3x2 grid of six saturated panels, each with a flat
white icon and a short label. Rendered at 2048x2048 and downscaled to
1024x1024 with LANCZOS so edges and text stay smooth.

Deterministic by construction: fixed colours, fixed geometry, fixed text,
no randomness, no clock, no network and no external image files. Only system
TrueType fonts (bold sans) are used -- no emoji fonts.

Run:  /home/kozak/AI/crypto-wallet/.venv/bin/python make_image.py
Writes ``entry.png`` (the committed image) and ``thumb256.png`` (a helper
256px contact-sheet preview for checking readability).
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY = os.path.join(HERE, "entry.png")
THUMB = os.path.join(HERE, "thumb256.png")

CANVAS = 2048
FINAL = 1024

# Palette ---------------------------------------------------------------
BG = (10, 14, 19)            # #0A0E13 near-black
WHITE = (255, 255, 255)
AMBER_RULE = (245, 158, 11)  # #F59E0B thick rule
AMBER_TEXT = (251, 191, 36)  # #FBBF24 header date

PANELS = [
    # title,              secondary,           colour (#hex),  icon id
    ("APEC SUMMIT",     "SHENZHEN, CHINA",   (30, 64, 175),   "summit"),   # #1E40AF
    ("GAZA",            "TANKS CROSS LINE",  (185, 28, 28),   "tank"),     # #B91C1C
    ("EU \u20ac45BN LOAN", "FOR UKRAINE",    (91, 33, 182),   "euro"),     # #5B21B6
    ("CARACAS VISIT",   "HEGSETH, VENEZUELA", (4, 120, 87),   "flags"),    # #047857
    ("ANTHROPIC IPO",   "$83 A SHARE",       (180, 83, 9),    "chip"),     # #B45309
    ("VOYAGER 1",       "ONE LIGHT-DAY OUT", (14, 116, 144),  "voyager"),  # #0E7490
]

# Fonts -----------------------------------------------------------------
_FONT_BOLD_CANDIDATES = [
    "/nix/store/vhl6cimg440y598c9hbvk8mnhc52xq59-dejavu-fonts-2.37/share/fonts/truetype/DejaVuSans-Bold.ttf",
    "/nix/store/aajylscf24q8gdgmkp1qmrrysfs09sbs-liberation-fonts-2.1.5/share/fonts/truetype/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

_FONT_BOLD = None
for _cand in _FONT_BOLD_CANDIDATES:
    if os.path.isfile(_cand):
        _FONT_BOLD = _cand
        break
if _FONT_BOLD is None:
    raise SystemExit("no bold sans font found")

_font_cache = {}


def font(size):
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(_FONT_BOLD, size)
    return _font_cache[size]


def blend(colour, t):
    """Mix a colour toward white by fraction t (0..1)."""
    return tuple(int(c + (255 - c) * t) for c in colour)


# Layout (2048 coordinate space) ---------------------------------------
TOP = 88
BOTTOM = 88
HEADER_CY = 270          # vertical centre of the header text line
RULE_Y = 388             # top edge of the amber rule
RULE_H = 22              # thickness of the amber rule
GRID_TOP = 438
GAP = 20

GRID_BOTTOM = CANVAS - BOTTOM
GRID_H = GRID_BOTTOM - GRID_TOP
PANEL_H = (GRID_H - GAP) // 2

_grid_width = CANVAS - 2 * TOP
PANEL_W = (_grid_width - 2 * GAP) // 3
GRID_LEFT = (CANVAS - (3 * PANEL_W + 2 * GAP)) // 2


def panel_rect(row, col):
    x0 = GRID_LEFT + col * (PANEL_W + GAP)
    y0 = GRID_TOP + row * (PANEL_H + GAP)
    return (x0, y0, x0 + PANEL_W, y0 + PANEL_H)


# Text helpers ----------------------------------------------------------
def text_w(draw, text, size):
    return draw.textlength(text, font=font(size))


def fit(draw, text, target_w, max_size, min_size=16):
    if text_w(draw, text, max_size) <= target_w:
        return max_size
    lo, hi = min_size, max_size
    best = min_size
    while lo <= hi:
        mid = (lo + hi) // 2
        if text_w(draw, text, mid) <= target_w:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def mm(draw, text, size, x, y, fill):
    draw.text((x, y), text, font=font(size), fill=fill, anchor="mm")


# Icons -----------------------------------------------------------------
def icon_summit(d, cx, cy, s):
    spacing = 150 * s
    base_w = 140 * s
    top_w = 84 * s
    ph = 150 * s
    top_y = cy - 20 * s
    bot_y = top_y + ph
    for x in (cx - spacing, cx, cx + spacing):
        d.polygon(
            [
                (x - top_w / 2, top_y),
                (x + top_w / 2, top_y),
                (x + base_w / 2, bot_y),
                (x - base_w / 2, bot_y),
            ],
            fill=WHITE,
        )
        stem_top = top_y - 88 * s
        d.line([(x, top_y), (x, stem_top)], fill=WHITE, width=int(15 * s))
        r = 20 * s
        d.ellipse([x - r, stem_top - r, x + r, stem_top + r], fill=WHITE)


def icon_tank(d, cx, cy, s):
    # dashed boundary line the tank is crossing
    lx = cx - 80 * s
    y = cy - 150 * s
    while y < cy + 150 * s:
        d.line([(lx, y), (lx, y + 24 * s)], fill=WHITE, width=int(16 * s))
        y += 24 * s + 18 * s
    # tracks
    tr_w = 250 * s
    tr_h = 56 * s
    tr_x0 = cx - 60 * s
    tr_y0 = cy + 60 * s
    d.rounded_rectangle(
        [tr_x0, tr_y0, tr_x0 + tr_w, tr_y0 + tr_h], radius=int(14 * s), fill=WHITE
    )
    # hull
    d.polygon(
        [
            (tr_x0 + 26 * s, tr_y0),
            (tr_x0 + tr_w - 20 * s, tr_y0),
            (tr_x0 + tr_w - 84 * s, cy - 12 * s),
            (tr_x0 + 48 * s, cy - 12 * s),
        ],
        fill=WHITE,
    )
    # turret
    d.rounded_rectangle(
        [cx + 8 * s, cy - 62 * s, cx + 112 * s, cy - 12 * s],
        radius=int(12 * s),
        fill=WHITE,
    )
    # barrel
    d.rectangle(
        [cx + 112 * s, cy - 46 * s, cx + 112 * s + 170 * s, cy - 30 * s],
        fill=WHITE,
    )


def icon_euro(d, cx, cy, s):
    d.text((cx - 120 * s, cy), "\u20ac", font=font(int(200 * s)), fill=WHITE, anchor="mm")
    sh_w = 92 * s
    sh_cx = cx + 135 * s
    sh_top = cy - 125 * s
    sh_bot = cy + 145 * s
    d.polygon(
        [
            (sh_cx - sh_w, sh_top),
            (sh_cx + sh_w, sh_top),
            (sh_cx + sh_w, sh_bot - 58 * s),
            (sh_cx, sh_bot),
            (sh_cx - sh_w, sh_bot - 58 * s),
        ],
        fill=WHITE,
    )


def _flag(d, x, y, w, h, kind, s):
    if kind == "usa":
        stripes = 7
        for i in range(stripes):
            c = (185, 28, 28) if i % 2 == 0 else WHITE
            d.rectangle(
                [x, y + i * h / stripes, x + w, y + (i + 1) * h / stripes], fill=c
            )
        d.rectangle([x, y, x + w * 0.45, y + h * 0.55], fill=(30, 64, 175))
        for i in range(3):
            for j in range(2):
                sx = x + w * 0.10 + i * w * 0.12
                sy = y + h * 0.10 + j * h * 0.20
                r = 2.4 * s
                d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    else:  # venezuela: yellow / blue / red + arc of stars
        d.rectangle([x, y, x + w, y + h / 3], fill=(255, 205, 0))
        d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 80, 180))
        d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(206, 17, 38))
        n = 8
        for i in range(n):
            t = i / (n - 1)
            ang = math.pi * (1 - t)
            sx = x + w / 2 + (w * 0.30) * math.cos(ang)
            sy = y + h / 2 - (h * 0.16) * math.sin(ang)
            r = 3.4 * s
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)


def icon_flags(d, cx, cy, s):
    fw = 150 * s
    fh = 102 * s
    for fx, kind in ((cx - 92 * s, "usa"), (cx + 112 * s, "ven")):
        d.line([(fx, cy - 112 * s), (fx, cy + 100 * s)], fill=WHITE, width=int(11 * s))
        _flag(d, fx, cy - 112 * s, fw, fh, kind, s)


def icon_chip(d, cx, cy, s, panel):
    cw = 200 * s
    d.rounded_rectangle(
        [cx - cw / 2, cy - cw / 2, cx + cw / 2, cy + cw / 2],
        radius=int(24 * s),
        fill=WHITE,
    )
    pw = 26 * s
    ph = 20 * s
    for i in (-1, 0, 1):
        ox = i * 52 * s
        d.rectangle([cx + ox - pw / 2, cy - cw / 2 - ph, cx + ox + pw / 2, cy - cw / 2], fill=WHITE)
        d.rectangle([cx + ox - pw / 2, cy + cw / 2, cx + ox + pw / 2, cy + cw / 2 + ph], fill=WHITE)
        oy = i * 52 * s
        d.rectangle([cx - cw / 2 - ph, cy + oy - pw / 2, cx - cw / 2, cy + oy + pw / 2], fill=WHITE)
        d.rectangle([cx + cw / 2, cy + oy - pw / 2, cx + cw / 2 + ph, cy + oy + pw / 2], fill=WHITE)
    # rising arrow to the upper right, clear of the chip
    ax0, ay0 = cx + 55 * s, cy - 55 * s
    ax1, ay1 = cx + 165 * s, cy - 165 * s
    d.line([(ax0, ay0), (ax1, ay1)], fill=WHITE, width=int(30 * s))
    ang = math.atan2(ay1 - ay0, ax1 - ax0)
    hw = 46 * s
    p2 = (ax1 - hw * math.cos(ang - 0.6), ay1 - hw * math.sin(ang - 0.6))
    p3 = (ax1 - hw * math.cos(ang + 0.6), ay1 - hw * math.sin(ang + 0.6))
    d.polygon([(ax1, ay1), p2, p3], fill=WHITE)


def icon_voyager(d, cx, cy, s):
    # tiny Earth, far away on the left
    ex = cx - 152 * s
    ey = cy + 14 * s
    er = 22 * s
    d.ellipse([ex - er, ey - er, ex + er, ey + er], outline=WHITE, width=int(8 * s))
    d.ellipse([ex - 6 * s, ey - 8 * s, ex + 8 * s, ey + 6 * s], fill=WHITE)
    # dashed signal path from Earth back to the dish
    x = ex + er + 8 * s
    xend = cx - 80 * s
    while x < xend:
        d.line([(x, ey), (x + 16 * s, ey)], fill=WHITE, width=int(6 * s))
        x += 16 * s + 10 * s
    # dish bowl (concave side facing the Earth)
    dish_cx = cx - 8 * s
    dish_cy = cy + 14 * s
    r = 82 * s
    d.pieslice(
        [dish_cx - r, dish_cy - r, dish_cx + r, dish_cy + r],
        start=90,
        end=270,
        fill=WHITE,
    )
    # feed horn in front of the bowl
    d.ellipse(
        [dish_cx - r - 28 * s, dish_cy - 12 * s, dish_cx - r - 6 * s, dish_cy + 12 * s],
        fill=WHITE,
    )
    # spacecraft bus behind the dish
    d.rounded_rectangle(
        [dish_cx + 8 * s, dish_cy - 36 * s, dish_cx + 92 * s, dish_cy + 50 * s],
        radius=int(15 * s),
        fill=WHITE,
    )
    # instrument boom pointing up-right
    d.line(
        [(dish_cx + 50 * s, dish_cy - 36 * s), (dish_cx + 128 * s, dish_cy - 140 * s)],
        fill=WHITE,
        width=int(11 * s),
    )
    d.line(
        [(dish_cx + 128 * s, dish_cy - 140 * s), (dish_cx + 158 * s, dish_cy - 126 * s)],
        fill=WHITE,
        width=int(9 * s),
    )


ICONS = {
    "summit": icon_summit,
    "tank": icon_tank,
    "euro": icon_euro,
    "flags": icon_flags,
    "chip": icon_chip,
    "voyager": icon_voyager,
}


# Render ----------------------------------------------------------------
def main():
    img = Image.new("RGB", (CANVAS, CANVAS), BG)
    d = ImageDraw.Draw(img)

    # --- header ---
    date_size = fit(d, "WED 18 NOV 2026", int(_grid_width * 0.44), 200)
    date_w = text_w(d, "WED 18 NOV 2026", date_size)
    title_size = fit(d, "WORLD NEWS", _grid_width - date_w - 60, 260)
    d.text((GRID_LEFT, HEADER_CY), "WORLD NEWS", font=font(title_size), fill=WHITE, anchor="lm")
    d.text((GRID_LEFT + _grid_width, HEADER_CY), "WED 18 NOV 2026", font=font(date_size), fill=AMBER_TEXT, anchor="rm")
    d.rectangle(
        [GRID_LEFT, RULE_Y, GRID_LEFT + _grid_width, RULE_Y + RULE_H],
        fill=AMBER_RULE,
    )

    # --- six panels ---
    pad = 16
    main_size = min(fit(d, t, PANEL_W - 2 * pad, 150) for t, _, _, _ in PANELS)
    sec_size = min(fit(d, t, PANEL_W - 2 * pad, 86) for _, t, _, _ in PANELS)

    for idx, (title, secondary, colour, icon_id) in enumerate(PANELS):
        row, col = divmod(idx, 3)
        x0, y0, x1, y1 = panel_rect(row, col)
        d.rectangle([x0, y0, x1, y1], fill=colour)

        cx = (x0 + x1) // 2
        cy = y0 + int(PANEL_H * 0.34)
        s = PANEL_W / 610.0

        icon = ICONS[icon_id]
        if icon_id == "chip":
            icon(d, cx, cy, s, colour)
        else:
            icon(d, cx, cy, s)

        mm(d, title, main_size, cx, y0 + int(PANEL_H * 0.70), WHITE)
        mm(d, secondary, sec_size, cx, y0 + int(PANEL_H * 0.86), blend(colour, 0.60))

    # --- downscale and save ---
    out = img.resize((FINAL, FINAL), Image.LANCZOS)
    out.save(ENTRY, format="PNG")

    thumb = img.resize((256, 256), Image.LANCZOS)
    thumb.save(THUMB, format="PNG")
    print("wrote", ENTRY, "and", THUMB)


if __name__ == "__main__":
    main()
