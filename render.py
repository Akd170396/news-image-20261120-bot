#!/usr/bin/env python3
"""Dense newspaper-style infographic: the world news of 20 November 2026.

Round 2 design: 40 sourced stories (4 big, 12 medium, 24 one-liners),
a UTC timeline strip, per-story source labels, region colour coding and a
DATE CHECK footer. Pure PIL, fully deterministic, no network.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 227)
INK = (26, 26, 26)
FADED = (92, 86, 72)
RULE = (26, 26, 26)
CARD = (252, 249, 240)

REGION = {
    "ASIA": (192, 57, 43),
    "EUROPE": (36, 113, 163),
    "MIDDLE EAST": (202, 111, 30),
    "AMERICAS": (30, 132, 73),
    "AFRICA": (125, 60, 152),
    "OCEANIA": (20, 143, 119),
    "GLOBAL": (97, 106, 107),
    "SCIENCE": (21, 101, 140),
}

SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, font, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


# ---------------- icons (simple hand-drawn shapes inside a circle) --------

def icon_flags(d, cx, cy, r, ink):
    for i, dx in enumerate((-16, 0, 16)):
        x = cx + dx
        d.line([(x, cy + 14), (x, cy - 14)], fill=ink, width=2)
        d.polygon([(x, cy - 14), (x + 11, cy - 10), (x, cy - 6)], fill=ink)


def icon_scales(d, cx, cy, r, ink):
    d.line([(cx, cy - 15), (cx, cy + 13)], fill=ink, width=2)
    d.line([(cx - 16, cy - 11), (cx + 16, cy - 11)], fill=ink, width=2)
    d.line([(cx - 7, cy + 15), (cx + 7, cy + 15)], fill=ink, width=2)
    for sx in (cx - 16, cx + 16):
        d.line([(sx, cy - 11), (sx - 6, cy + 2)], fill=ink, width=1)
        d.line([(sx, cy - 11), (sx + 6, cy + 2)], fill=ink, width=1)
        d.arc([sx - 7, cy - 2, sx + 7, cy + 8], 0, 180, fill=ink, width=2)


def icon_chart(d, cx, cy, r, ink):
    base = cy + 13
    for i, h in enumerate((9, 15, 22)):
        x = cx - 16 + i * 11
        d.rectangle([x, base - h, x + 7, base], fill=ink)
    d.line([(cx - 17, cy + 2), (cx - 5, cy - 5), (cx + 4, cy - 2), (cx + 16, cy - 14)],
           fill=ink, width=2)
    d.polygon([(cx + 16, cy - 15), (cx + 9, cy - 13), (cx + 15, cy - 7)], fill=ink)


def icon_tower(d, cx, cy, r, ink):
    d.rectangle([cx - 9, cy - 16, cx + 9, cy + 15], outline=ink, width=2)
    for wy in range(cy - 10, cy + 12, 7):
        for wx in (cx - 5, cx + 2):
            d.rectangle([wx, wy, wx + 3, wy + 3], fill=ink)
    d.arc([cx - 20, cy - 20, cx + 6, cy + 2], 200, 320, fill=ink, width=2)
    d.ellipse([cx - 21, cy - 13, cx - 17, cy - 9], fill=ink)


ICONS = {"flags": icon_flags, "scales": icon_scales,
         "chart": icon_chart, "tower": icon_tower}

# ---------------- story data (all 20 Nov 2026, any time zone) -------------

BIG = [
    dict(region="ASIA", place="SHENZHEN, CHINA", icon="flags",
         head="Trump, Xi and Putin hold first three-way summit",
         sub="The US, Chinese and Russian leaders signed a four-point "
             "\u201cDeclaration toward Peace\u201d on nuclear risk and UN reform.",
         src="NBC \u00b7 One Turn"),
    dict(region="EUROPE", place="THE HAGUE, NETHERLANDS", icon="scales",
         head="World Court: Myanmar committed genocide",
         sub="The ICJ ruled Myanmar committed genocide against the Rohingya "
             "\u2014 its first such finding against a state.",
         src="UN News \u00b7 ICJ"),
    dict(region="AMERICAS", place="NEW YORK, USA", icon="chart",
         head="Anthropic closes +17% in record Nasdaq debut",
         sub="Shares ended their first session at $97.17, 17% above the $83 "
             "offer price, even as Wall Street slid.",
         src="Forbes \u00b7 CBC"),
    dict(region="MIDDLE EAST", place="RIYADH, SAUDI ARABIA", icon="tower",
         head="Houthi missile damages PIF tower in Riyadh",
         sub="Missiles hit the capital's financial district, damaging the "
             "Public Investment Fund tower and nearby buildings.",
         src="News.Az \u00b7 APA"),
]

MEDIUM = [
    ("ASIA", "ODISHA, INDIA", "Cyclone Akvan makes landfall near Gopalpur",
     "Severe cyclonic storm crossed the coast; ~300,000 evacuated, gusts to 110 km/h.", "IMD"),
    ("GLOBAL", "MARKETS", "Stocks slide: Nikkei -4.8%, S&P down a 5th day",
     "AI valuation doubts after Anthropic's debut; SoftBank fell over 16% in Tokyo.", "Reuters"),
    ("EUROPE", "KERCH STRAIT, CRIMEA", "Ukraine hits Crimea Bridge a third time",
     "Rail traffic halted; Putin vowed a \u201cfar more painful\u201d response.", "One Turn"),
    ("MIDDLE EAST", "NUSEIRAT, GAZA", "Israeli forces cross Yellow Line in Gaza",
     "First such incursion into central Gaza since the ceasefire took hold.", "One Turn"),
    ("MIDDLE EAST", "STRAIT OF HORMUZ", "Tanker ablaze after hitting mine in Hormuz",
     "Iran war enters its ninth month as attacks on shipping intensify.", "CBS \u00b7 Reuters"),
    ("GLOBAL", "ANTALYA, TURKEY", "COP31 draft drops fossil-fuel phase-out",
     "Negotiators stripped the call to end fossil fuel use from the slimmed text.", "One Turn"),
    ("AFRICA", "KENYA", "Kenya discharges its last Ebola patient",
     "Outbreak ends 37 days after the first case was confirmed.", "One Turn"),
    ("ASIA", "TOKYO, JAPAN", "13,000 protest Takaichi policies at the Diet",
     "Crowds opposed constitutional revision and military expansion.", "IANS"),
    ("AMERICAS", "CALIFORNIA, USA", "California subpoenas Nvidia over China chips",
     "AG Bonta probes whether advanced chips or data reached China.", "IANS"),
    ("AMERICAS", "SAN SALVADOR, EL SALVADOR", "Bukele registers for a third term",
     "President files for 2027 after constitutional changes allowed it.", "One Turn"),
    ("AMERICAS", "WASHINGTON, USA", "US ground stop as House forces Epstein vote",
     "Telecom failure halted flights; discharge petition hit 218 signatures.", "Nexus Europa"),
    ("EUROPE", "MOSCOW, RUSSIA", "Kushner and Witkoff arrive for Putin talks",
     "US envoys in Moscow after consultations with Kyiv and Europe.", "Nexus Europa"),
]

ALSO = [
    ("ASIA", "Mongolian president Kh\u00fcrels\u00fckh resigns", "One Turn"),
    ("GLOBAL", "UN secretary-general race stalls after eight votes", "One Turn"),
    ("ASIA", "Violence in Bangladesh ahead of Hasina's planned return", "One Turn"),
    ("MIDDLE EAST", "Iraq orders Iran-backed militia out of Jurf al-Nasr", "One Turn"),
    ("EUROPE", "Denmark ratifies Greenland security deal with US", "One Turn"),
    ("ASIA", "IAEA: North Korea expanding uranium enrichment", "One Turn"),
    ("AFRICA", "Drone strike kills 10 at Sudan gold mine", "One Turn"),
    ("AFRICA", "Dozens missing as migrant boat sinks off Senegal", "One Turn"),
    ("EUROPE", "UK pledges 1,000+ drones for Ukraine in \u00a3260m package", "AppiSToS"),
    ("AMERICAS", "White House fires cyber director after outage week", "One Turn"),
    ("GLOBAL", "US sanctions Comancheros and \u2019Ndrangheta", "AppiSToS"),
    ("AMERICAS", "Trump posthumously pardons baseball star Pete Rose", "AppiSToS"),
    ("ASIA", "Japan core inflation hits 2026 high at 2.2%", "News Media House"),
    ("GLOBAL", "Gold at 14-month low near $3,685", "Argus"),
    ("GLOBAL", "IMF warns global debt to near 100% of GDP", "One Turn"),
    ("AMERICAS", "US Senate passes energy permitting overhaul 62\u201333", "One Turn"),
    ("AFRICA", "Malawi fuel crisis triggers queues and violence", "News Media House"),
    ("EUROPE", "Bulgaria: hackers stole 62m pages of govt documents", "APEX"),
    ("GLOBAL", "\u201cHuman\u201d named Cambridge Word of the Year 2026", "APEX"),
    ("GLOBAL", "Van Gogh canvas sells for $190.4 million", "APEX"),
    ("GLOBAL", "GTA 6 launch tops $1.8bn, est. 19m copies", "GameSpot"),
    ("SCIENCE", "Voyager 1 now one light-day from Earth", "NASA"),
    ("OCEANIA", "Nicholls 113* as NZ reach 243/5 vs India", "Jagran Josh"),
    ("SCIENCE", "BepiColombo arrives at Mercury after eight years", "BBC"),
]

TIMELINE = [
    ("02:30", "Trump pardons Pete Rose"),
    ("03:36", "13,000 protest in Tokyo"),
    ("03:43", "US sanctions crime syndicates"),
    ("05:39", "Cyclone Xavier bulletin 39"),
    ("06:15", "UK \u00a3260m drones for Ukraine"),
    ("07:00", "US ground stop; envoys in Moscow"),
]

DATE_CHECK = (
    "DATE CHECK \u2014 deliberately left out (broke before 20 Nov): Anthropic IPO priced at "
    "$83 on 18 Nov \u2014 only the debut close is today's story \u00b7 Hegseth's surprise Caracas "
    "visit, announced 18 Nov \u00b7 Manila Quad summit, 17 Nov (P-8/P-3C drill set for 2027). "
    "Everything above happened, or was first reported, on 20 November 2026 in at least one "
    "time zone. Sources named on every story."
)

# ---------------- drawing ---------------------------------------------------

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
MX = 28                      # side margin
CW = W - 2 * MX              # content width

# masthead
d.line([(MX, 16), (MX + CW, 16)], fill=RULE, width=3)
kick = "FRIDAY \u00b7 ALL TIMES UTC \u00b7 ONE IMAGE, ONE DAY"
kf = F(SANS_B, 13)
d.text((MX, 24), kick, font=kf, fill=INK)
rtext = "No. 20 \u00b7 DAILY EDITION"
d.text((MX + CW - d.textlength(rtext, font=kf), 24), rtext, font=kf, fill=INK)

mast = F(SERIF_B, 88)
title = "20 November 2026"
tw = d.textlength(title, font=mast)
d.text(((W - tw) / 2, 44), title, font=mast, fill=INK)

sub_f = F(SANS_B, 14)
sub = "THE WORLD IN ONE DAY \u2014 40 SOURCED STORIES, A UTC TIMELINE AND A DATE CHECK"
sw = d.textlength(sub, font=sub_f)
d.text(((W - sw) / 2, 140), sub, font=sub_f, fill=FADED)
d.line([(MX, 162), (MX + CW, 162)], fill=RULE, width=2)
d.line([(MX, 167), (MX + CW, 167)], fill=RULE, width=1)

# timeline strip
ty = 176
d.text((MX, ty), "THE DAY IN UTC", font=F(SANS_B, 13), fill=INK)
d.text((MX + 130, ty), "wire times as reported", font=F(SANS, 11), fill=FADED)
slot_w = CW / len(TIMELINE)
sy = ty + 22
d.line([(MX, sy + 6), (MX + CW, sy + 6)], fill=FADED, width=1)
for i, (tm, lab) in enumerate(TIMELINE):
    x = MX + i * slot_w
    d.ellipse([x + 2, sy + 2, x + 10, sy + 10], fill=INK)
    d.text((x + 14, sy - 4), tm, font=F(SANS_B, 12), fill=INK)
    for j, ln in enumerate(wrap(d, lab, F(SANS, 10), slot_w - 18)[:2]):
        d.text((x + 14, sy + 14 + j * 12), ln, font=F(SANS, 10), fill=INK)

# big stories
by = 252
d.text((MX, by), "TOP STORIES", font=F(SANS_B, 14), fill=INK)
d.line([(MX, by + 20), (MX + CW, by + 20)], fill=RULE, width=1)
cell_w, cell_h, gap = (CW - 16) // 2, 118, 8
gy = by + 28
for i, s in enumerate(BIG):
    x = MX + (i % 2) * (cell_w + 16)
    y = gy + (i // 2) * (cell_h + gap)
    d.rectangle([x, y, x + cell_w, y + cell_h], fill=CARD, outline=(205, 196, 172), width=1)
    col = REGION[s["region"]]
    d.rectangle([x, y, x + 6, y + cell_h], fill=col)
    cx, cy, r = x + 46, y + cell_h // 2, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=2)
    ICONS[s["icon"]](d, cx, cy, r, col)
    tx = x + 88
    d.text((tx, y + 10), f"{s['region']} \u00b7 {s['place']}", font=F(SANS_B, 10.5), fill=col)
    hy = draw_lines(d, wrap(d, s["head"], F(SERIF_B, 18), cell_w - 100)[:2],
                    tx, y + 26, F(SERIF_B, 18), INK, 21)
    sy2 = draw_lines(d, wrap(d, s["sub"], F(SANS, 11.5), cell_w - 100)[:2],
                     tx, hy + 2, F(SANS, 11.5), (60, 56, 48), 14)
    d.text((tx, y + cell_h - 18), s["src"].upper(), font=F(SANS_B, 9.5), fill=FADED)

# medium stories
my = gy + 2 * cell_h + gap + 14
d.text((MX, my), "MORE OF THE DAY", font=F(SANS_B, 14), fill=INK)
d.line([(MX, my + 20), (MX + CW, my + 20)], fill=RULE, width=1)
row_h = 34
ry = my + 28
for i, (region, place, head, sub, src) in enumerate(MEDIUM):
    x = MX + (i % 2) * (cell_w + 16)
    y = ry + (i // 2) * row_h
    col = REGION[region]
    d.rectangle([x, y + 2, x + 5, y + row_h - 6], fill=col)
    d.text((x + 12, y), head, font=F(SANS_B, 13.5), fill=INK)
    subline = f"{place} \u00b7 {src.upper()} \u2014 {sub}"
    sf = F(SANS, 9.5)
    if d.textlength(subline, font=sf) > cell_w - 16:
        while d.textlength(subline + "\u2026", font=sf) > cell_w - 16 and len(subline) > 20:
            subline = subline.rsplit(" ", 1)[0]
        subline += "\u2026"
    d.text((x + 12, y + 18), subline, font=sf, fill=(60, 56, 48))

# also-on one-liners
ay = ry + 6 * row_h + 10
d.text((MX, ay), "ALSO ON 20 NOVEMBER", font=F(SANS_B, 14), fill=INK)
d.line([(MX, ay + 20), (MX + CW, ay + 20)], fill=RULE, width=1)
ly = ay + 27
line_h = 12
for i, (region, head, src) in enumerate(ALSO):
    x = MX + (i % 2) * (cell_w + 16)
    y = ly + (i // 2) * line_h
    col = REGION[region]
    d.ellipse([x, y + 3, x + 6, y + 9], fill=col)
    txt = f"{head} ({src})"
    fnt = F(SANS, 10.5)
    while d.textlength(txt, font=fnt) > cell_w - 14 and len(txt) > 10:
        txt = txt[:-2]
    d.text((x + 11, y), txt, font=fnt, fill=INK)

# date-check footer
fy = ly + 12 * line_h + 10
d.rectangle([MX, fy, MX + CW, H - 18], outline=RULE, width=1)
flines = wrap(d, DATE_CHECK, F(SANS, 10), CW - 24)
draw_lines(d, flines[:3], MX + 12, fy + 8, F(SANS, 10), INK, 13)

img.save("entry.png")
print("wrote entry.png", img.size)
