#!/usr/bin/env python3
"""Render the 20 November 2026 world-news infographic (1024x1024 PNG).

Drawn from scratch with PIL only. Deterministic: no randomness, no clock,
no network -- every run writes the same bytes to entry.png.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

BG = (13, 27, 44)          # deep navy
PANEL = (22, 42, 66)       # card fill
PANEL_EDGE = (52, 84, 120)
INK = (240, 244, 248)      # near-white text
MUTED = (168, 188, 208)    # sub-line text
GOLD = (245, 197, 66)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_BOLD = os.path.join(FONT_DIR, "liberation", "LiberationSerif-Bold.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "dejavu", "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "dejavu", "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap using measured text widths."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons

def icon_flags(draw, cx, cy, r, color):
    """Three small flags on poles (the three-way summit)."""
    pole_h = r * 1.15
    for i, dx in enumerate((-r * 0.62, 0, r * 0.62)):
        x = cx + dx
        top = cy - pole_h / 2
        draw.line([x, top, x, cy + pole_h / 2], fill=color, width=4)
        fw = r * 0.52
        fh = r * 0.34
        draw.polygon(
            [(x, top), (x + fw, top + fh / 2), (x, top + fh)],
            fill=color,
        )


def icon_cyclone(draw, cx, cy, r, color):
    """Spiral storm swirl."""
    pts = []
    steps = 90
    for i in range(steps + 1):
        t = i / steps
        ang = t * math.pi * 4.4
        rad = r * 0.12 + t * r * 0.78
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.line(pts, fill=color, width=6, joint="curve")
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=color)


def icon_chart(draw, cx, cy, r, color):
    """Rising market arrow over bars."""
    base = cy + r * 0.62
    heights = [0.35, 0.55, 0.45, 0.8]
    bw = r * 0.3
    x = cx - r * 0.85
    for hfrac in heights:
        h = r * 1.2 * hfrac
        draw.rectangle([x, base - h, x + bw, base], fill=color)
        x += bw + r * 0.18
    draw.line(
        [cx - r * 0.9, cy + r * 0.1, cx - r * 0.25, cy - r * 0.25,
         cx + r * 0.2, cy - r * 0.05, cx + r * 0.85, cy - r * 0.7],
        fill=(255, 255, 255), width=6, joint="curve",
    )
    ax, ay = cx + r * 0.85, cy - r * 0.7
    draw.polygon([(ax, ay), (ax - 16, ay + 2), (ax - 4, ay + 16)], fill=(255, 255, 255))


def icon_scales(draw, cx, cy, r, color):
    """Scales of justice."""
    top = cy - r * 0.75
    draw.line([cx, top, cx, cy + r * 0.55], fill=color, width=5)
    draw.ellipse([cx - 7, top - 7, cx + 7, top + 7], fill=color)
    beam_y = top + r * 0.18
    draw.line([cx - r * 0.8, beam_y, cx + r * 0.8, beam_y], fill=color, width=5)
    for sx in (cx - r * 0.8, cx + r * 0.8):
        pan_y = beam_y + r * 0.52
        draw.line([sx, beam_y, sx - r * 0.28, pan_y], fill=color, width=3)
        draw.line([sx, beam_y, sx + r * 0.28, pan_y], fill=color, width=3)
        draw.arc([sx - r * 0.3, pan_y - r * 0.12, sx + r * 0.3, pan_y + r * 0.22],
                 start=0, end=180, fill=color, width=5)
    draw.line([cx - r * 0.42, cy + r * 0.68, cx + r * 0.42, cy + r * 0.68],
              fill=color, width=6)


def icon_controller(draw, cx, cy, r, color):
    """Game controller."""
    w, h = r * 1.7, r * 1.05
    x0, y0 = cx - w / 2, cy - h / 2
    draw.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(h * 0.42),
                           outline=color, width=6)
    # d-pad
    dx, dy = x0 + w * 0.26, cy
    draw.line([dx - 12, dy, dx + 12, dy], fill=color, width=6)
    draw.line([dx, dy - 12, dx, dy + 12], fill=color, width=6)
    # buttons
    for bx, by in ((0.72, -0.18), (0.84, 0.02), (0.72, 0.2), (0.6, 0.0)):
        px, py = x0 + w * bx, cy + h * by
        draw.ellipse([px - 6, py - 6, px + 6, py + 6], fill=color)


def icon_satellite(draw, cx, cy, r, color):
    """Space probe with a dish and signal arcs."""
    # body
    draw.rounded_rectangle([cx - r * 0.32, cy - r * 0.18, cx + r * 0.32, cy + r * 0.3],
                           radius=6, fill=color)
    # dish
    draw.pieslice([cx - r * 0.55, cy - r * 0.95, cx + r * 0.55, cy + r * 0.15],
                  start=20, end=160, fill=color)
    draw.line([cx, cy - r * 0.4, cx, cy - r * 0.18], fill=color, width=5)
    # boom + antenna
    draw.line([cx + r * 0.32, cy + r * 0.06, cx + r * 0.85, cy + r * 0.5],
              fill=color, width=4)
    draw.ellipse([cx + r * 0.8, cy + r * 0.45, cx + r * 0.92, cy + r * 0.57], fill=color)
    # signal arcs
    for rr in (0.62, 0.82):
        draw.arc([cx - r * rr, cy - r * 0.4 - r * rr, cx + r * rr, cy - r * 0.4 + r * rr],
                 start=225, end=315, fill=(255, 255, 255), width=4)


ICONS = {
    "flags": icon_flags,
    "cyclone": icon_cyclone,
    "chart": icon_chart,
    "scales": icon_scales,
    "controller": icon_controller,
    "satellite": icon_satellite,
}

# ---------------------------------------------------------------- stories

STORIES = [
    {
        "icon": "flags",
        "accent": (96, 165, 250),
        "kicker": "WORLD POLITICS · SHENZHEN, CHINA",
        "headline": "Trump, Xi, Putin: first summit",
        "sub": "Nuclear arms control tops the APEC agenda.",
    },
    {
        "icon": "cyclone",
        "accent": (45, 212, 191),
        "kicker": "WEATHER · ODISHA, INDIA",
        "headline": "Cyclone Akvan makes landfall",
        "sub": "Near Gopalpur: 300,000 evacuated, gusts to 110 km/h.",
    },
    {
        "icon": "chart",
        "accent": (74, 222, 128),
        "kicker": "BUSINESS · NEW YORK",
        "headline": "Anthropic IPO: record $81B, +17%",
        "sub": "Biggest listing ever; valued near $1.75 trillion.",
    },
    {
        "icon": "scales",
        "accent": (251, 191, 36),
        "kicker": "INTERNATIONAL LAW · THE HAGUE",
        "headline": "World court: Myanmar genocide",
        "sub": "ICJ's first genocide verdict against a state (2017 Rohingya crackdown).",
    },
    {
        "icon": "controller",
        "accent": (244, 114, 182),
        "kicker": "ENTERTAINMENT · GAMING",
        "headline": "GTA 6 launch tops $1.8 billion",
        "sub": "An estimated 19 million copies — a record debut.",
    },
    {
        "icon": "satellite",
        "accent": (167, 139, 250),
        "kicker": "SCIENCE · DEEP SPACE",
        "headline": "Voyager 1 now one light-day away",
        "sub": "First object 16 billion miles out; signal takes 24 hours.",
    },
]

FOOTER = "Sources: Reuters · The Hindu · NASA · UN News · GameSpot · Fast Company"


def draw_card(draw, x, y, w, h, story):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18,
                           fill=PANEL, outline=PANEL_EDGE, width=2)
    # accent bar
    draw.rounded_rectangle([x, y + 14, x + 10, y + h - 14], radius=5,
                           fill=story["accent"])
    # icon disc
    disc_r = 46
    dcx, dcy = x + 66, y + 66
    draw.ellipse([dcx - disc_r, dcy - disc_r, dcx + disc_r, dcy + disc_r],
                 fill=(10, 20, 34), outline=story["accent"], width=3)
    ICONS[story["icon"]](draw, dcx, dcy, 30, story["accent"])

    text_x = x + 128
    text_w = w - 128 - 22
    f_head = font(SANS_BOLD, 29)
    f_sub = font(SANS, 20)

    # shrink the kicker font until it fits the card width
    kicker_size = 20
    f_kicker = font(SANS_BOLD, kicker_size)
    while draw.textlength(story["kicker"], font=f_kicker) > text_w and kicker_size > 14:
        kicker_size -= 1
        f_kicker = font(SANS_BOLD, kicker_size)

    ty = y + 20
    draw.text((text_x, ty), story["kicker"], font=f_kicker, fill=story["accent"])
    ty += 28
    for line in wrap(draw, story["headline"], f_head, text_w)[:2]:
        draw.text((text_x, ty), line, font=f_head, fill=INK)
        ty += 36
    ty += 2
    for line in wrap(draw, story["sub"], f_sub, text_w)[:3]:
        draw.text((text_x, ty), line, font=f_sub, fill=MUTED)
        ty += 26


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # top hairline band
    draw.rectangle([0, 0, W, 10], fill=GOLD)

    # masthead
    f_kicker = font(SANS_BOLD, 26)
    kick = "THE WORLD IN ONE DAY · FRIDAY"
    kw = draw.textlength(kick, font=f_kicker)
    draw.text(((W - kw) / 2, 34), kick, font=f_kicker, fill=GOLD)

    f_date = font(SERIF_BOLD, 96)
    date = "20 NOVEMBER 2026"
    dw = draw.textlength(date, font=f_date)
    draw.text(((W - dw) / 2, 72), date, font=f_date, fill=INK)

    draw.rectangle([36, 196, W - 36, 200], fill=GOLD)

    # story grid: 2 columns x 3 rows
    margin, gap_x, gap_y = 36, 20, 18
    card_w = (W - 2 * margin - gap_x) // 2
    grid_top, grid_bottom = 222, 934
    card_h = (grid_bottom - grid_top - 2 * gap_y) // 3
    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        cx = margin + col * (card_w + gap_x)
        cy = grid_top + row * (card_h + gap_y)
        draw_card(draw, cx, cy, card_w, card_h, story)

    # footer
    f_foot = font(SANS, 20)
    fw = draw.textlength(FOOTER, font=f_foot)
    draw.text(((W - fw) / 2, 954), FOOTER, font=f_foot, fill=MUTED)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG", optimize=False)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
