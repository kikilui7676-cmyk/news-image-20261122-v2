#!/usr/bin/env python3
"""Draw the v2 front page: the world news of Sunday 22 November 2026 in one image.

Canvas 1024x1024. Design priority is legibility at ~300 px wide: very large
bold headlines, one-line captions, bold simple pictograms, high contrast.
Run:  python3 render.py   ->  writes entry.png next to this file.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

W = H = 1024
MARGIN = 28
CW = W - 2 * MARGIN  # content width

BG = (248, 244, 236)
INK = (18, 18, 18)
RED = (168, 0, 27)
NAVY = (20, 46, 74)
GOLD = (196, 138, 0)
PANEL_BG = (255, 255, 255)
PANEL_LINE = (178, 168, 148)
LEAD_BG = (243, 233, 210)
GREY = (92, 88, 80)

WARNINGS = []


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def bold(size):
    return font("DejaVuSans-Bold.ttf", size)


def regular(size):
    return font("DejaVuSans.ttf", size)


def serif_bold(size):
    return font("DejaVuSerif-Bold.ttf", size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def check(draw, s, f, max_w, where):
    w = text_w(draw, s, f)
    if w > max_w:
        WARNINGS.append(f"OVERFLOW {where}: {s!r} is {w:.0f}px > {max_w}px")


# --------------------------------------------------------------------------
# Pictograms. Each draws inside box (x, y, s, s), bold strokes, simple shapes.
# --------------------------------------------------------------------------

def icon_globe_crack(d, x, y, s):
    r = s // 2 - 3
    cx, cy = x + s // 2, y + s // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=5)
    d.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=NAVY, width=3)
    d.line([cx - r, cy, cx + r, cy], fill=NAVY, width=3)
    # jagged red crack down the middle
    pts = [(cx + 2, cy - r + 2), (cx - 7, cy - r // 3), (cx + 6, cy + 2),
           (cx - 6, cy + r // 3), (cx + 2, cy + r - 2)]
    d.line(pts, fill=RED, width=6, joint="curve")


def icon_missile(d, x, y, s):
    # diagonal missile, nose up-right
    body = [(x + 14, y + s - 14), (x + s - 30, y + 16), (x + s - 14, y + 30),
            (x + 30, y + s - 14)]
    d.polygon(body, fill=NAVY)
    d.polygon([(x + s - 30, y + 16), (x + s - 8, y + 8), (x + s - 14, y + 30)],
              fill=RED)
    # fins
    d.polygon([(x + 14, y + s - 14), (x + 6, y + s - 30), (x + 26, y + s - 26)],
              fill=RED)
    d.polygon([(x + 14, y + s - 14), (x + 30, y + s - 6), (x + 26, y + s - 26)],
              fill=RED)
    # exhaust streaks
    d.line([x + 2, y + s - 10, x + 10, y + s - 2], fill=RED, width=4)
    d.line([x + 10, y + s - 2, x + 18, y + s - 10], fill=RED, width=4)


def icon_ship(d, x, y, s):
    hull = [(x + 6, y + s - 26), (x + s - 6, y + s - 26), (x + s - 16, y + s - 10),
            (x + 16, y + s - 10)]
    d.polygon(hull, fill=NAVY)
    d.rectangle([x + 20, y + s - 40, x + 44, y + s - 26], fill=NAVY)
    d.rectangle([x + 48, y + s - 48, x + 56, y + s - 26], fill=NAVY)
    # drone above: X quadcopter
    cx, cy = x + s - 22, y + 12
    d.line([cx - 10, cy - 8, cx + 10, cy + 8], fill=RED, width=4)
    d.line([cx - 10, cy + 8, cx + 10, cy - 8], fill=RED, width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    # waves
    for i in range(3):
        wx = x + 10 + i * 20
        d.arc([wx, y + s - 8, wx + 16, y + s + 4], 180, 360, fill=NAVY, width=3)


def icon_flame(d, x, y, s):
    cx = x + s // 2
    outer = [(cx, y + 4), (cx + 16, y + 26), (cx + 20, y + 42),
             (cx + 12, y + s - 6), (cx - 12, y + s - 6), (cx - 20, y + 42),
             (cx - 14, y + 24)]
    d.polygon(outer, fill=(214, 84, 0))
    inner = [(cx, y + 26), (cx + 9, y + 42), (cx + 6, y + s - 8),
             (cx - 6, y + s - 8), (cx - 9, y + 42)]
    d.polygon(inner, fill=GOLD)


def icon_scales(d, x, y, s):
    cx = x + s // 2
    top = y + 10
    d.line([cx, top, cx, y + s - 14], fill=INK, width=5)
    d.line([x + 10, top, x + s - 10, top], fill=INK, width=5)
    d.ellipse([cx - 5, top - 5, cx + 5, top + 5], fill=INK)
    for px in (x + 10, x + s - 10):
        d.line([px, top, px - 9, top + 22], fill=INK, width=3)
        d.line([px, top, px + 9, top + 22], fill=INK, width=3)
        d.arc([px - 13, top + 14, px + 13, top + 34], 0, 180, fill=INK, width=4)
    d.line([x + 14, y + s - 10, x + s - 14, y + s - 10], fill=INK, width=5)


def icon_building(d, x, y, s):
    bx, bw = x + 10, s - 20
    d.rectangle([bx, y + 6, bx + bw, y + s - 4], outline=INK, width=5)
    for r in range(3):
        for c in range(2):
            wx = bx + 7 + c * 15
            wy = y + 13 + r * 14
            d.rectangle([wx, wy, wx + 9, wy + 8], fill=INK)
    # red burst at top-right corner
    cx, cy = bx + bw + 2, y + 8
    for ang in range(0, 360, 45):
        dx = int(11 * math.cos(math.radians(ang)))
        dy = int(11 * math.sin(math.radians(ang)))
        d.line([cx, cy, cx + dx, cy + dy], fill=RED, width=4)


def icon_boat(d, x, y, s):
    hull = [(x + 8, y + s - 30), (x + s - 8, y + s - 30), (x + s - 18, y + s - 14),
            (x + 18, y + s - 14)]
    d.polygon(hull, fill=NAVY)
    mast_x = x + s // 2
    d.line([mast_x, y + s - 30, mast_x, y + 10], fill=INK, width=4)
    d.polygon([(mast_x + 3, y + 13), (mast_x + 3, y + s - 32), (mast_x + 24, y + s - 32)],
              fill=GOLD)
    for i in range(3):
        wx = x + 8 + i * 20
        d.arc([wx, y + s - 10, wx + 16, y + s + 2], 180, 360, fill=NAVY, width=3)


def icon_badge(d, x, y, s):
    cx = x + s // 2
    shield = [(cx, y + s - 6), (x + 10, y + s - 20), (x + 10, y + 10),
              (cx, y + 4), (x + s - 10, y + 10), (x + s - 10, y + s - 20)]
    d.polygon(shield, outline=NAVY, width=5)
    # star
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = 15 if i % 2 == 0 else 6
        pts.append((cx + r * math.cos(ang), y + 28 + r * math.sin(ang)))
    d.polygon(pts, fill=RED)


def icon_factory(d, x, y, s):
    base_y = y + s - 4
    d.rectangle([x + 4, base_y - 24, x + s - 4, base_y], outline=INK, width=5)
    # sawtooth roof
    for i in range(3):
        tx = x + 8 + i * 13
        d.polygon([(tx, base_y - 24), (tx + 6, base_y - 35), (tx + 6, base_y - 24)],
                  fill=INK)
    # chimney + one smoke ring, all inside the box
    d.rectangle([x + s - 20, base_y - 42, x + s - 11, base_y - 24], fill=INK)
    d.ellipse([x + s - 24, base_y - 54, x + s - 8, base_y - 40], outline=GREY, width=3)


def icon_rings(d, x, y, s):
    cy = y + s // 2
    d.ellipse([x + 3, cy - 17, x + 35, cy + 17], outline=(30, 80, 160), width=5)
    d.ellipse([x + s - 35, cy - 17, x + s - 3, cy + 17], outline=GOLD, width=5)


def icon_castle(d, x, y, s):
    cx = x + s // 2
    def px(frac):
        return int(s * frac)
    # stacked pagoda roofs, proportional to s
    d.polygon([(cx - px(0.40), y + px(0.34)), (cx + px(0.40), y + px(0.34)),
               (cx + px(0.22), y + px(0.12)), (cx - px(0.22), y + px(0.12))],
              fill=RED)
    d.rectangle([cx - px(0.20), y + px(0.34), cx + px(0.20), y + px(0.50)], fill=INK)
    d.polygon([(cx - px(0.46), y + px(0.70)), (cx + px(0.46), y + px(0.70)),
               (cx + px(0.25), y + px(0.50)), (cx - px(0.25), y + px(0.50))],
              fill=RED)
    d.rectangle([cx - px(0.25), y + px(0.70), cx + px(0.25), y + px(0.94)], fill=INK)


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------

def panel(d, x, y, w, h, icon, headline, caption):
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=PANEL_BG,
                        outline=PANEL_LINE, width=2)
    icon(d, x + 14, y + 12, 58)
    hf = bold(27)
    lines = wrap(d, headline, hf, w - 84 - 12)
    if len(lines) > 3:
        WARNINGS.append(f"HEADLINE>3 lines: {headline!r} -> {lines}")
    ty = y + 14
    for ln in lines:
        check(d, ln, hf, w - 84 - 12, "headline")
        d.text((x + 84, ty), ln, font=hf, fill=INK)
        ty += 33
    cf = regular(20)
    check(d, caption, cf, w - 28, "caption")
    d.text((x + 14, y + h - 32), caption, font=cf, fill=(60, 56, 50))


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # frame
    d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=3)
    d.rectangle([17, 17, W - 18, H - 18], outline=INK, width=1)

    # masthead
    mf = serif_bold(56)
    title = "THE WORLD IN ONE IMAGE"
    check(d, title, mf, CW, "masthead")
    d.text(((W - text_w(d, title, mf)) / 2, 22), title, font=mf, fill=INK)
    d.line([MARGIN, 94, W - MARGIN, 94], fill=INK, width=4)
    d.line([MARGIN, 101, W - MARGIN, 101], fill=INK, width=1)

    # date band
    d.rectangle([MARGIN, 110, W - MARGIN, 158], fill=(12, 12, 12))
    df = bold(36)
    date = "SUNDAY 22 NOVEMBER 2026"
    check(d, date, df, CW, "date")
    d.text(((W - text_w(d, date, df)) / 2, 115), date, font=df, fill=(255, 255, 255))

    # lead panel
    ly, lh = 170, 176
    d.rounded_rectangle([MARGIN, ly, W - MARGIN, ly + lh], radius=12, fill=LEAD_BG,
                        outline=PANEL_LINE, width=2)
    icon_globe_crack(d, MARGIN + 26, ly + 22, 132)
    tx = MARGIN + 186
    kf = bold(22)
    kicker = "LEAD STORY — ANTALYA, TURKEY"
    check(d, kicker, kf, W - MARGIN - tx - 16, "kicker")
    d.text((tx, ly + 14), kicker, font=kf, fill=RED)
    hf = bold(49)
    for i, ln in enumerate(["COP31 CLIMATE TALKS", "END WITHOUT A DEAL"]):
        check(d, ln, hf, W - MARGIN - tx - 16, "lead headline")
        d.text((tx, ly + 46 + i * 55), ln, font=hf, fill=INK)
    cf = regular(22)
    cap = "Nearly 200 countries split over fossil fuels and finance."
    check(d, cap, cf, W - MARGIN - tx - 16, "lead caption")
    d.text((tx, ly + lh - 30), cap, font=cf, fill=(60, 56, 50))

    # 3x3 grid
    gx, gy = MARGIN, 360
    gap = 14
    pw = (CW - 2 * gap) // 3
    ph = 170
    stories = [
        (icon_missile, "RUSSIAN MISSILES IN POLAND", "NATO calls it a violation"),
        (icon_ship, "SEA DRONES HIT WARSHIP", "Russian ship hit at Benghazi"),
        (icon_flame, "IRAN ATTACK INJURES TWO IN BAHRAIN", "Tankers struck near Hormuz"),
        (icon_scales, "ICJ: MYANMAR GENOCIDE RULING", "Genocide of the Rohingya"),
        (icon_building, "FIVE KILLED IN UKRAINE STRIKES", "Kyiv flats; hometown hit"),
        (icon_boat, "FUNERAL BOAT CAPSIZES", "Nigeria: at least 24 dead"),
        (icon_badge, "CARTEL LEADER CAPTURED", "El Chapo Isidro; 11 dead"),
        (icon_factory, "SEARCH FOR 34 MISSING", "Indonesia candy factory fire"),
        (icon_rings, "BRITAIN & EU: CLOSER TIES", "Major post-Brexit pact"),
    ]
    for i, (icon, head, cap) in enumerate(stories):
        r, c = divmod(i, 3)
        panel(d, gx + c * (pw + gap), gy + r * (ph + gap), pw, ph, icon, head, cap)

    # culture strip
    sy = gy + 3 * ph + 2 * gap + 14
    sh = H - MARGIN - sy
    d.rounded_rectangle([MARGIN, sy, W - MARGIN, sy + sh], radius=10, fill=PANEL_BG,
                        outline=PANEL_LINE, width=2)
    icon_castle(d, MARGIN + 14, sy + 8, sh - 16)
    bf = bold(23)
    part1 = "CULTURE — SHURI CASTLE HALL RESTORED IN OKINAWA"
    check(d, part1, bf, CW - 90, "culture")
    d.text((MARGIN + 84, sy + 12), part1, font=bf, fill=INK)
    rf = regular(20)
    part2 = "Main hall celebrated again, seven years after the fire"
    check(d, part2, rf, CW - 90, "culture sub")
    d.text((MARGIN + 84, sy + 46), part2, font=rf, fill=(60, 56, 50))

    if WARNINGS:
        print("WARNINGS:")
        for wmsg in WARNINGS:
            print(" ", wmsg)
    else:
        print("no overflow warnings")

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
