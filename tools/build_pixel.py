#!/usr/bin/env python3
"""Pixel-retro GitHub profile generator for iydebu/iydebu (stdlib only).

    python tools/build_pixel.py             build every static SVG into Img/pixel/
    python tools/build_pixel.py stats OUT   live PLAYER STATS svg (GitHub GraphQL)

Text/links/skills live in tools/profile.json - edit that, rerun, commit.
GitHub strips CSS and web fonts from README HTML, so every letter here is drawn
from a 5x7 bitmap font as SVG paths; animation is CSS inside each SVG.
"""
import datetime
import json
import os
import random
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Img", "pixel")
P = json.load(open(os.path.join(ROOT, "tools", "profile.json"), encoding="utf-8"))

C = dict(bg="#0b1416", panel="#0f1f22", panel2="#132a2e", line="#1d3f42",
         teal="#14b8a6", teal_d="#0f766e", teal_l="#5eead4", mint="#99f6e4",
         text="#d7f5ef", dim="#5f8a86", yellow="#fbbf24", red="#f43f5e",
         purple="#a855f7", blue="#3b82f6", gray="#94a3b8", ink="#05090a")
RARITY = {"L": ("LEGENDARY", C["yellow"]), "E": ("EPIC", C["purple"]),
          "R": ("RARE", C["blue"]), "C": ("COMMON", C["gray"])}

# ---------------------------------------------------------------- 5x7 font
_F = """
A .###. #...# #...# ##### #...# #...# #...#
B ####. #...# #...# ####. #...# #...# ####.
C .###. #...# #.... #.... #.... #...# .###.
D ####. #...# #...# #...# #...# #...# ####.
E ##### #.... #.... ####. #.... #.... #####
F ##### #.... #.... ####. #.... #.... #....
G .###. #...# #.... #.### #...# #...# .####
H #...# #...# #...# ##### #...# #...# #...#
I .###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.
J ..### ...#. ...#. ...#. ...#. #..#. .##..
K #...# #..#. #.#.. ##... #.#.. #..#. #...#
L #.... #.... #.... #.... #.... #.... #####
M #...# ##.## #.#.# #.#.# #...# #...# #...#
N #...# #...# ##..# #.#.# #..## #...# #...#
O .###. #...# #...# #...# #...# #...# .###.
P ####. #...# #...# ####. #.... #.... #....
Q .###. #...# #...# #...# #.#.# #..#. .##.#
R ####. #...# #...# ####. #.#.. #..#. #...#
S .#### #.... #.... .###. ....# ....# ####.
T ##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..
U #...# #...# #...# #...# #...# #...# .###.
V #...# #...# #...# #...# #...# .#.#. ..#..
W #...# #...# #...# #.#.# #.#.# #.#.# .#.#.
X #...# #...# .#.#. ..#.. .#.#. #...# #...#
Y #...# #...# .#.#. ..#.. ..#.. ..#.. ..#..
Z ##### ....# ...#. ..#.. .#... #.... #####
0 .###. #...# #..## #.#.# ##..# #...# .###.
1 ..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.
2 .###. #...# ....# ...#. ..#.. .#... #####
3 ##### ...#. ..#.. ...#. ....# #...# .###.
4 ...#. ..##. .#.#. #..#. ##### ...#. ...#.
5 ##### #.... ####. ....# ....# #...# .###.
6 ..##. .#... #.... ####. #...# #...# .###.
7 ##### ....# ...#. ..#.. .#... .#... .#...
8 .###. #...# #...# .###. #...# #...# .###.
9 .###. #...# #...# .#### ....# ...#. .##..
. ..... ..... ..... ..... ..... ..... ..#..
, ..... ..... ..... ..... ..... ..#.. .#...
: ..... ..... ..#.. ..... ..... ..#.. .....
- ..... ..... ..... .###. ..... ..... .....
_ ..... ..... ..... ..... ..... ..... #####
/ ....# ....# ...#. ..#.. .#... #.... #....
\ #.... #.... .#... ..#.. ...#. ....# ....#
' ..#.. ..#.. ..... ..... ..... ..... .....
! ..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..
? .###. #...# ....# ...#. ..#.. ..... ..#..
# .#.#. .#.#. ##### .#.#. ##### .#.#. .#.#.
@ .###. #...# #.### #.#.# #.### #.... .####
+ ..... ..#.. ..#.. ##### ..#.. ..#.. .....
& .##.. #..#. #.#.. .#... #.#.# #..#. .##.#
( ...#. ..#.. .#... .#... .#... ..#.. ...#.
) .#... ..#.. ...#. ...#. ...#. ..#.. .#...
[ .###. .#... .#... .#... .#... .#... .###.
] .###. ...#. ...#. ...#. ...#. ...#. .###.
> .#... ..#.. ...#. ....# ...#. ..#.. .#...
< ...#. ..#.. .#... #.... .#... ..#.. ...#.
| ..#.. ..#.. ..#.. ..#.. ..#.. ..#.. ..#..
% ##... ##..# ...#. ..#.. .#... #..## ...##
$ ..#.. .#### #.#.. .###. ..#.# ####. ..#..
= ..... ..... ##### ..... ##### ..... .....
* ..... #.#.# .###. ##### .###. #.#.# .....
· ..... ..... ..... ..#.. ..... ..... .....
▶ #.... ##... ###.. ####. ###.. ##... #....
▼ ..... ##### .###. ..#.. ..... ..... .....
♥ ..... ##.## ##### ##### .###. ..#.. .....
₹ ##### ...#. ##### ..#.. ##... ..#.. ...##
✓ ..... ....# ...#. #.#.. .#... ..... .....
∞ ..... ..... .#.#. #.#.# .#.#. ..... .....
"""
FONT = {" ": ["....."] * 7}
for _ln in _F.strip().splitlines():
    _ch, *_rows = _ln.split(" ")
    assert len(_rows) == 7 and all(len(r) == 5 for r in _rows), _ln
    FONT[_ch] = _rows


def n(v):
    v = round(v, 2)
    return str(int(v)) if v == int(v) else str(v)


def tw(s, sc):
    return len(s) * 6 * sc - sc


def runs(rows, ch, x, y, sc):
    d = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] == ch:
                c0 = c
                while c < len(row) and row[c] == ch:
                    c += 1
                w = (c - c0) * sc
                d.append(f"M{n(x + c0 * sc)} {n(y + r * sc)}h{n(w)}v{n(sc)}h{n(-w)}z")
            else:
                c += 1
    return "".join(d)


def text(s, x, y, sc, fill, anchor="start", attrs=""):
    s = s.upper()
    if anchor == "middle":
        x -= tw(s, sc) / 2
    elif anchor == "end":
        x -= tw(s, sc)
    x = round(x)
    d = []
    for i, ch in enumerate(s):
        if ch not in FONT:
            print(f"  ! no glyph for {ch!r}, using '?'")
        d.append(runs(FONT.get(ch, FONT["?"]), "#", x + i * 6 * sc, y, sc))
    return f'<path d="{"".join(d)}" fill="{fill}"{attrs}/>'


def sprite(rows, pal, x, y, sc, attrs=""):
    out = [f'<path d="{runs(rows, k, x, y, sc)}" fill="{col}"/>' for k, col in pal.items()
           if any(k in r for r in rows)]
    return f'<g{attrs}>{"".join(out)}</g>'


def mix(a, b, t):
    a, b = int(a[1:], 16), int(b[1:], 16)
    ch = [round(((a >> s) & 255) * (1 - t) + ((b >> s) & 255) * t) for s in (16, 8, 0)]
    return "#%02x%02x%02x" % tuple(ch)


def frame(x, y, w, h, col, fill, t=4, inner=None):
    s = (f'<rect x="{x + t}" y="{y + t}" width="{w - 2 * t}" height="{h - 2 * t}" fill="{fill}"/>'
         f'<path d="M{x + t} {y}h{w - 2 * t}v{t}h{-(w - 2 * t)}z'
         f'M{x + t} {y + h - t}h{w - 2 * t}v{t}h{-(w - 2 * t)}z'
         f'M{x} {y + t}h{t}v{h - 2 * t}h{-t}z'
         f'M{x + w - t} {y + t}h{t}v{h - 2 * t}h{-t}z" fill="{col}"/>')
    if inner:  # 2px inner rule, like an old console dialog
        i = t + 3
        s += (f'<rect x="{x + i}" y="{y + i}" width="{w - 2 * i}" height="{h - 2 * i}" '
              f'fill="none" stroke="{inner}" stroke-width="2"/>')
    return s


BASE_CSS = ("@keyframes bl{0%{opacity:1}50%{opacity:0}}.bl{animation:bl 1s step-end infinite}"
            "@keyframes pop{from{opacity:0}to{opacity:1}}")
BL = ' class="bl"'
FA, FB = ' class="fa"', ' class="fb"'
SCAN = ('<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="2" fill="#000" opacity=".18"/></pattern>')


def svg(w, h, body, css="", defs="", scan=True):
    over = f'<rect width="{w}" height="{h}" fill="url(#scan)" pointer-events="none"/>' if scan else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'shape-rendering="crispEdges"><style>{BASE_CSS}{css}</style><defs>{SCAN}{defs}</defs>'
            f'{body}{over}</svg>')


def save(name, data):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    print(f"  {name:28s} {len(data) / 1024:6.1f} KB")


# ---------------------------------------------------------------- sprites
ICONS = {
    "heart": ["........", ".rr..rr.", "rwrrrrrr", "rrrrrrrr", "rrrrrrrr", ".rrrrrr.", "..rrrr..", "...rr..."],
    "sword": ["......gw", ".....gwg", "....gwg.", ".y.gwg..", "..ygg...", "..yy....", ".b..y...", "b......."],
    "chest": ["........", ".bbbbbb.", "bbbbbbbb", "yyyyyyyy", "bbbyybbb", "bbbkkbbb", "bbbbbbbb", "........"],
    "scroll": ["yyyyyyy.", ".wwwwwy.", ".wkkkkw.", ".wwwwww.", ".wkkkww.", ".wwwwww.", ".yyyyyyy", "........"],
    "joy": ["...rr...", "..rrrr..", "...rr...", "...gg...", "...gg...", ".tttttt.", "tttttttt", "TTTTTTTT"],
    "floppy": ["ttttttt.", "twwwwgtt", "twwwwgtt", "tttttttt", "tTTTTTTt", "tTwwwwTt", "tTwwwwTt", "tttttttt"],
    "coin": ["..yyyy..", ".yyyyyy.", "yyykkkyy", "yykyyyyy", "yyykkyyy", "yyyyykyy", ".ykkkyy.", "..yyyy.."],
    "pc": ["gggggggg", "gTTTTTTg", "gTttwtTg", "gTtttTTg", "gTTTTTTg", "gggggggg", "...gg...", ".gggggg."],
    "star": ["...yy...", "...yy...", "yyyyyyyy", ".yyyyyy.", "..yyyy..", ".yy..yy.", ".y....y.", "........"],
}
IPAL = {"r": C["red"], "w": "#ecfeff", "g": "#64748b", "y": C["yellow"], "b": "#8b5a2b",
        "k": C["ink"], "t": C["teal"], "T": C["teal_d"]}

AVATAR = ["....kkkkkkkk....", "...khhhhhhhhk...", "..khhhhhhhhhhk..", "..khhhhhhhhhhk..",
          "..khhsshhhsshk..", "..khssssssshhk..", "..kswwsssswwsk..", "..kswesssswesk..",
          "..kssssddssssk..", "..kssssssssssk..", "...kssseesssk...", "....kssssssk....",
          "...kTTkddkTTk...", "..kTTTTttTTTTk..", ".kTTTTTttTTTTTk.", ".kTTTTTttTTTTTk."]
APAL = {"k": C["ink"], "h": "#1f1a17", "s": "#c68a5e", "d": "#9c6644", "w": "#ecfeff",
        "e": C["ink"], "t": C["teal_l"], "T": C["teal_d"]}

RUN_TOP = ["..hhhh..", ".hhhhhs.", ".hhssss.", "..ssss..", ".tttttt.", "s.tttt.s", "..tttt.."]
RUN_A = RUN_TOP + ["..k..k..", ".k....k.", "ww....ww"]
RUN_B = RUN_TOP + ["...kk...", "...kk...", "..wwww.."]
RPAL = {"h": "#1f1a17", "s": "#c68a5e", "t": C["teal"], "k": "#334155", "w": "#ecfeff"}


def life_glider():
    """Four real Game-of-Life glider generations (the portfolio wallpaper motif)."""
    cells = {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    gens = []
    for _ in range(4):
        gens.append(sorted(cells))
        nb = {}
        for x, y in cells:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx or dy:
                        nb[(x + dx, y + dy)] = nb.get((x + dx, y + dy), 0) + 1
        cells = {c for c, k in nb.items() if k == 3 or (k == 2 and c in cells)}
    assert sorted((x - 1, y - 1) for x, y in cells) == gens[0]  # period 4, drift (+1,+1)
    return gens


# ---------------------------------------------------------------- shared panel bits
def tab(x, title, icon=None):
    """Teal title tab sitting on a panel's top edge (replaces the old full-width header images)."""
    pad = 22 if icon else 0
    s = f'<rect x="{x}" y="0" width="{tw(title, 2) + 24 + pad}" height="26" fill="{C["teal"]}"/>'
    if icon:
        s += f'<rect x="{x + 6}" y="3" width="20" height="20" fill="{C["ink"]}"/>' + sprite(ICONS[icon], IPAL, x + 8, 5, 2)
    return s + text(title, x + 12 + pad, 6, 2, C["ink"])


def panel(W, H, col=None):
    return f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>' + frame(0, 0, W, H, col or C["line"], C["panel"], 4)


# ---------------------------------------------------------------- hero
def hero():
    W, H = 840, 170
    rnd = random.Random(7)
    b, css = [], []
    b.append(f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>')
    b.append(f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="url(#dots)"/>')
    # drifting Game-of-Life gliders (portfolio wallpaper motif)
    gens, cell, step = life_glider(), 8, 0.3
    css.append("@keyframes ph{0%{opacity:1}25%{opacity:0}100%{opacity:0}}")
    css.append(f".ph{{opacity:0;animation:ph {4 * step}s step-end infinite}}")
    b.append('<g clip-path="url(#inner)">')
    for gi in range(7):
        x0, y0 = rnd.randrange(-200, W - 80), rnd.randrange(-200, H - 60)
        dist = 30
        dur = dist * 4 * step
        css.append(f"@keyframes gl{gi}{{to{{transform:translate({dist * cell}px,{dist * cell}px)}}}}")
        css.append(f".gl{gi}{{animation:gl{gi} {dur}s steps({dist},end) infinite;"
                   f"animation-delay:-{rnd.uniform(0, dur):.1f}s}}")
        ph = []
        for k, g in enumerate(gens):
            d = "".join(f"M{x * cell} {y * cell}h{cell - 1}v{cell - 1}h{-(cell - 1)}z" for x, y in g)
            ph.append(f'<path class="ph" style="animation-delay:-{((4 - k) % 4) * step:.1f}s" d="{d}"/>')
        b.append(f'<g transform="translate({x0} {y0})"><g class="gl{gi}" fill="#123e3b">{"".join(ph)}</g></g>')
    b.append("</g>")
    # one-line arcade HUD
    hy = 14
    b.append(text("1UP", 24, hy, 2, C["red"], attrs=BL))
    b.append(text(P["handle"], 24 + 4 * 12, hy, 2, C["text"]))
    s1, s2 = "HI-SCORE ", "999999"
    x0 = W / 2 - tw(s1 + s2, 2) / 2
    b.append(text(s1, x0, hy, 2, C["red"]))
    b.append(text(s2, x0 + len(s1) * 12, hy, 2, C["text"]))
    b.append(text("UE5", W - 24, hy, 2, C["text"], "end"))
    b.append(text("STAGE", W - 24 - 4 * 12, hy, 2, C["red"], "end"))
    # title with hard-stop gradient and drop shadow
    name, sc = P["name"], 4
    b.append(text(name, W / 2 + sc, 42 + sc, sc, C["teal_d"], "middle"))
    b.append(text(name, W / 2, 42, sc, "url(#tg)", "middle"))
    # rotating taglines
    tl, per = P["taglines"], 3
    css.append(f"@keyframes tl{{0%{{opacity:1}}{100 / len(tl):.2f}%{{opacity:0}}100%{{opacity:0}}}}")
    for k, line in enumerate(tl):
        delay = ((len(tl) - k) % len(tl)) * per
        b.append(text(line, W / 2, 86, 2, C["mint"], "middle",
                      f' style="opacity:0;animation:tl {per * len(tl)}s step-end infinite;animation-delay:-{delay}s"'))
    b.append(text("▶ PRESS START", W / 2, 108, 2, C["yellow"], "middle", BL))
    # ground + runner
    gy = H - 30
    b.append(f'<rect x="4" y="{gy}" width="{W - 8}" height="4" fill="{C["teal"]}"/>')
    b.append(f'<rect x="4" y="{gy + 4}" width="{W - 8}" height="{H - gy - 8}" fill="url(#brick)"/>')
    css.append("@keyframes run{from{transform:translateX(-40px)}to{transform:translateX(880px)}}"
               ".run{animation:run 16s linear infinite}"
               "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}"
               ".fa{animation:fa .36s step-end infinite}.fb{opacity:0;animation:fb .36s step-end infinite}")
    b.append(f'<g clip-path="url(#inner)"><g class="run">'
             f'{sprite(RUN_A, RPAL, 0, gy - 20, 2, FA)}'
             f'{sprite(RUN_B, RPAL, 0, gy - 20, 2, FB)}</g></g>')
    for cx in (140, 280, 560, 700):
        b.append(sprite(ICONS["coin"], IPAL, cx, gy - 20, 2, BL))
    b.append(frame(0, 0, W, H, C["teal"], "none", 4))
    defs = (f'<pattern id="dots" width="12" height="12" patternUnits="userSpaceOnUse">'
            f'<rect width="2" height="2" fill="#12282b"/></pattern>'
            f'<pattern id="brick" width="32" height="12" patternUnits="userSpaceOnUse">'
            f'<rect width="32" height="12" fill="{C["panel"]}"/>'
            f'<path d="M0 0h32v2H0zM0 6h32v2H0zM0 0h2v6H0zM16 6h2v6h-2z" fill="{C["line"]}"/></pattern>'
            f'<linearGradient id="tg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset=".5" stop-color="{C["teal_l"]}"/><stop offset=".5" stop-color="{C["teal"]}"/></linearGradient>'
            f'<clipPath id="inner"><rect x="4" y="4" width="{W - 8}" height="{H - 8}"/></clipPath>')
    save("hero.svg", svg(W, H, "".join(b), "".join(css), defs))


# ---------------------------------------------------------------- section divider (small)
def divider(title, icon, fname):
    W, H = 840, 32
    b = [f'<rect x="0" y="4" width="{W}" height="24" fill="{C["panel"]}"/>',
         f'<rect x="0" y="4" width="4" height="24" fill="{C["teal"]}"/>',
         sprite(ICONS[icon], IPAL, 14, 8, 2),
         text(title, 40, 9, 2, C["text"])]
    x = 40 + tw(title, 2) + 16
    b.append(f'<path d="{"".join(f"M{i} 15h2v2h-2z" for i in range(x, W - 16, 8))}" fill="{C["line"]}"/>')
    save(fname, svg(W, H, "".join(b), scan=False))


# ---------------------------------------------------------------- player card
def card():
    W = 840
    b, css = [], []
    # portrait
    b.append(frame(24, 38, 120, 120, C["line"], C["panel2"], 4))
    b.append(f'<rect x="28" y="42" width="112" height="112" fill="url(#dots2)"/>')
    b.append(sprite(AVATAR, APAL, 28, 42, 7))
    b.append(text("LV " + str(datetime.date.today().year - 2021 + 20), 84, 168, 2, C["teal"], "middle"))
    # info rows
    x, y = 164, 40
    for lab, val in P["card"]:
        b.append(text(lab, x, y, 2, C["dim"]))
        b.append(text(val, x + 84, y, 2, C["text"]))
        y += 22
    # HP / MP / XP bars, right column
    bx = 548
    bars = [("HP", C["red"], 10, "FULL"), ("MP", C["blue"], 8, "COFFEE"), ("XP", C["teal"], 7, "NEXT LV")]
    for i, (lab, col, fill, note) in enumerate(bars):
        y = 40 + i * 24
        b.append(text(lab, bx, y, 2, col))
        for s in range(10):
            sx = bx + 32 + s * 14
            if s < fill:
                d = i * 0.25 + s * 0.06
                b.append(f'<g style="animation:pop .1s steps(1,end) {d:.2f}s both">'
                         f'<rect x="{sx}" y="{y}" width="12" height="14" fill="{col}"/>'
                         f'<rect x="{sx}" y="{y}" width="12" height="3" fill="{mix(col, "#ffffff", .45)}"/>'
                         f'<rect x="{sx}" y="{y + 11}" width="12" height="3" fill="{mix(col, "#000000", .35)}"/></g>')
            else:
                b.append(f'<rect x="{sx + 1}" y="{y + 1}" width="10" height="12" fill="{C["panel2"]}" '
                         f'stroke="{C["line"]}" stroke-width="2"/>')
        b.append(text(note, bx + 32 + 140 + 6, y, 2, C["dim"]))
    # dialog box with typewriter text
    lines = P["dialog"]
    dx, dy, dw = 164, 136, W - 164 - 24
    dh = 32 + 22 * len(lines)
    H = dy + dh + 20
    b.append(frame(dx, dy, dw, dh, C["text"], C["ink"], 4))
    b.append(f'<rect x="{dx + 20}" y="{dy - 10}" width="{tw("DEBU", 2) + 20}" height="22" fill="{C["ink"]}"/>')
    b.append(text("DEBU", dx + 30, dy - 4, 2, C["teal"]))
    b.append(f'<clipPath id="dlg"><rect x="{dx + 4}" y="{dy + 4}" width="{dw - 8}" height="{dh - 8}"/></clipPath>')
    t0, cps = 1.0, 0.04
    covers = []
    for i, ln in enumerate(lines):
        ly = dy + 20 + i * 22
        b.append(text(ln, dx + 22, ly, 2, C["text"]))
        cw = tw(ln, 2) + 14
        dur = len(ln) * cps
        css.append(f"@keyframes tw{i}{{to{{transform:translateX({cw}px)}}}}")
        covers.append(f'<rect x="{dx + 18}" y="{ly - 2}" width="{cw}" height="18" fill="{C["ink"]}" '
                      f'style="animation:tw{i} {dur:.2f}s steps({len(ln)},end) {t0:.2f}s forwards"/>')
        t0 += dur + 0.15
    b.append(f'<g clip-path="url(#dlg)">{"".join(covers)}</g>')
    b.append(f'<g style="animation:pop .1s steps(1,end) {t0:.2f}s both">'
             f'{text("▼", dx + dw - 30, dy + dh - 22, 2, C["yellow"], attrs=BL)}</g>')
    defs = (f'<pattern id="dots2" width="8" height="8" patternUnits="userSpaceOnUse">'
            f'<rect width="2" height="2" fill="{C["line"]}"/></pattern>')
    body = (f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>' + frame(0, 0, W, H, C["teal"], C["panel"], 4, C["line"])
            + tab(24, "PLAYER 1") + "".join(b))
    save("card.svg", svg(W, H, body, "".join(css), defs))


# ---------------------------------------------------------------- quest log + skill tree (two columns)
def log():
    W, qs, sk = 840, P["quests"], P["skills"]
    top, step = 40, 26
    H = top + max(len(qs), len(sk)) * step + 6
    b = [panel(W, H), tab(24, "QUEST LOG", "scroll"), tab(440, "SKILL TREE", "sword"),
         f'<rect x="420" y="36" width="2" height="{H - 48}" fill="{C["line"]}"/>']
    tagc = {"MAIN": C["yellow"], "SIDE": C["blue"], "DONE": C["teal"]}
    for r, (state, tag, title, _sub) in enumerate(qs):
        title = title if len(title) <= 28 else title[:27] + "."  # left column fits 28 chars
        y = top + r * step
        mcol = {"active": C["yellow"], "todo": C["gray"], "done": C["teal"]}[state]
        glyph = {"active": "!", "todo": "?", "done": "✓"}[state]
        b.append(frame(24, y - 3, 20, 20, mcol, C["ink"], 2))
        b.append(text(glyph, 34, y, 2, mcol, "middle", BL if state == "active" else ""))
        b.append(f'<rect x="52" y="{y}" width="4" height="14" fill="{tagc[tag]}"/>')
        done = state == "done"
        b.append(text(title, 64, y, 2, C["dim"] if done else C["text"]))
        if done:
            b.append(f'<rect x="62" y="{y + 6}" width="{tw(title, 2) + 4}" height="2" fill="{C["dim"]}"/>')
    for r, (lab, lv) in enumerate(sk):
        y = top + r * step
        col = C["yellow"] if lv >= 9 else C["teal"]
        b.append(text(lab, 440, y, 2, C["text"]))
        for s in range(10):
            sx = 556 + s * 20
            if s < lv:
                d = r * 0.12 + s * 0.07
                b.append(f'<g style="animation:pop .1s steps(1,end) {d:.2f}s both">'
                         f'<rect x="{sx}" y="{y}" width="16" height="14" fill="{col}"/>'
                         f'<rect x="{sx}" y="{y}" width="16" height="3" fill="{mix(col, "#ffffff", .5)}"/>'
                         f'<rect x="{sx}" y="{y + 11}" width="16" height="3" fill="{mix(col, "#000000", .35)}"/></g>')
            else:
                b.append(f'<rect x="{sx + 1}" y="{y + 1}" width="14" height="12" fill="{C["panel2"]}" '
                         f'stroke="{C["line"]}" stroke-width="2"/>')
        b.append(text(f"LV {lv}", W - 24, y, 2, col, "end"))
    save("log.svg", svg(W, H, "".join(b)))


# ---------------------------------------------------------------- inventory (flowing chips)
def inventory():
    W, lx, cx0, right, ch, gx, gy = 840, 24, 168, 816, 28, 6, 6
    body, y = [], 40
    for cat, items in P["inventory"]:
        body.append(text(cat, lx, y + 7, 2, C["teal"]))
        x = cx0
        for name, rar in items:
            w = tw(name, 2) + 24
            if x + w > right:
                x, y = cx0, y + ch + gy
            col = RARITY[rar][1]
            body.append(frame(x, y, w, ch, col, C["panel2"], 2))
            body.append(f'<rect x="{x + 2}" y="{y + 2}" width="{w - 4}" height="2" fill="{mix(col, C["panel2"], .6)}"/>')
            body.append(text(name, x + 12, y + 7, 2, C["text"]))
            body.append(f'<rect x="{x + w - 7}" y="{y + 4}" width="3" height="3" fill="{col}"{BL if rar == "L" else ""}/>')
            x += w + gx
        y += ch + gy + 4
    # legend, top right beside the tab
    lx2 = right
    for key in "CREL":
        lab, col = RARITY[key]
        lx2 -= tw(lab, 2)
        body.append(text(lab, lx2, 8, 2, C["dim"]))
        lx2 -= 16
        body.append(f'<rect x="{lx2}" y="10" width="10" height="10" fill="{col}"/>')
        lx2 -= 20
    H = y + 6
    save("inventory.svg", svg(W, H, panel(W, H) + tab(24, "INVENTORY", "chest") + "".join(body)))


# ---------------------------------------------------------------- buttons
def button(label, col, fname, fg="#ffffff"):
    W, H = tw(label, 2) + 20, 32
    hi, lo = mix(col, "#ffffff", .35), mix(col, "#000000", .4)
    b = [f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="{col}"/>',
         f'<rect x="4" y="4" width="{W - 8}" height="2" fill="{hi}"/>',
         f'<rect x="4" y="{H - 8}" width="{W - 8}" height="4" fill="{lo}"/>',
         frame(0, 0, W, H, C["ink"], "none", 2)]
    shadow = C["ink"] if fg == "#ffffff" else mix(col, "#ffffff", .5)
    b.append(text(label, W / 2 + 2, 9, 2, shadow, "middle"))
    b.append(text(label, W / 2, 8, 2, fg, "middle"))
    save(fname, svg(W, H, "".join(b), scan=False))


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


# ---------------------------------------------------------------- rig + footer
def rig():
    lines = P["rig"]["lines"]
    W, H = 840, 60 + 30 * len(lines) + 56
    b = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>', frame(0, 0, W, H, C["line"], C["ink"], 4, C["panel2"])]
    b.append(sprite(ICONS["pc"], IPAL, 40, 40, 14))
    x, y = 200, 36
    b.append(text("C:\\> SYSTEM.INFO", x, y, 2, C["teal"]))
    y += 34
    for k, v in lines:
        b.append(text(k, x, y, 2, C["dim"]))
        lx = x + tw(k, 2) + 10
        rx = W - 40 - tw(v, 2) - 10
        b.append(f'<path d="{"".join(f"M{i} {y + 10}h2v2h-2z" for i in range(lx, rx, 8))}" fill="{C["line"]}"/>')
        b.append(text(v, W - 40, y, 2, C["text"], "end"))
        y += 30
    b.append(text("POWER LEVEL: OVER 9000", x, y + 4, 2, C["yellow"], attrs=BL))
    save("rig.svg", svg(W, H, "".join(b)))


def footer():
    W, H = 840, 92
    b, css = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>'], []
    b.append(text("THANKS FOR PLAYING", W / 2 + 3, 10 + 3, 3, C["teal_d"], "middle"))
    b.append(text("THANKS FOR PLAYING", W / 2, 10, 3, C["teal_l"], "middle"))
    line = "CONTINUE? 9 · INSERT COIN"
    x0 = W / 2 - tw(line, 2) / 2
    b.append(text("CONTINUE?", x0, 44, 2, C["text"]))
    css.append("@keyframes cd{0%{opacity:1}10%{opacity:0}100%{opacity:0}}")
    for i, dgt in enumerate("9876543210"):
        b.append(text(dgt, x0 + 10 * 12, 44, 2, C["yellow"], attrs=f' style="opacity:0;animation:cd 10s step-end infinite;'
                                                                    f'animation-delay:-{(10 - i) % 10}s"'))
    b.append(text("·", x0 + 12 * 12, 44, 2, C["dim"]))
    b.append(text("INSERT COIN", x0 + 14 * 12, 44, 2, C["yellow"], attrs=BL))
    b.append(text("(C) " + P["handle"] + " · MADE WITH PIXELS", W / 2, 70, 2, C["dim"], "middle"))
    for sx in (150, 674):
        b.append(sprite(ICONS["star"], IPAL, sx, 12, 2, BL))
    save("footer.svg", svg(W, H, "".join(b), "".join(css)))


# ---------------------------------------------------------------- live stats
Q = """query($login:String!){user(login:$login){createdAt followers{totalCount}
 pullRequests{totalCount} issues{totalCount}
 repositories(ownerAffiliations:OWNER,isFork:false,first:100,orderBy:{field:PUSHED_AT,direction:DESC}){
  totalCount nodes{stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}
 contributionsCollection{totalCommitContributions restrictedContributionsCount
  contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def token():
    for k in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def fetch():
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": Q, "variables": {"login": P["login"]}}).encode(),
                                 headers={"Authorization": "bearer " + token(), "User-Agent": "iydebu-pixel"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]["user"]


def stats(out):
    u = fetch()
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    cur = best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        best = max(best, run)
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"]:
            cur += 1
        elif i:  # today may still be empty
            break
    langs = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            nm = e["node"]["name"]
            langs.setdefault(nm, [0, e["node"]["color"] or C["gray"]])[0] += e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    total = sum(v[0] for _, v in top) or 1
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    since = u["createdAt"][:4]
    rows = [("CONTRIBUTIONS 1Y", cc["contributionCalendar"]["totalContributions"]),
            ("COMMITS 1Y", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
            ("PULL REQUESTS", u["pullRequests"]["totalCount"]),
            ("REPOSITORIES", u["repositories"]["totalCount"]),
            ("STARS EARNED", stars),
            ("FOLLOWERS", u["followers"]["totalCount"]),
            ("CURRENT STREAK", f"{cur} D"),
            ("BEST STREAK 1Y", f"{best} D")]
    W = 840
    b = []
    b.append(text("SINCE " + since, 400, 8, 2, C["dim"], "end"))
    y = 40
    for lab, val in rows:
        b.append(text(lab, 24, y, 2, C["dim"]))
        b.append(text(str(val), 400, y, 2, C["yellow"] if "STREAK" in lab else C["text"], "end"))
        y += 22
    lx = 440
    b.append(f'<rect x="420" y="36" width="2" height="{y - 40}" fill="{C["line"]}"/>')
    b.append(tab(lx, "TOP LANGUAGES"))
    ly = 40
    for i, (nm, (size, col)) in enumerate(top):
        pct = size * 100 / total
        b.append(text(nm[:10], lx, ly, 2, C["text"]))
        b.append(text(f"{pct:.0f}%", W - 24, ly, 2, C["dim"], "end"))
        segs = max(1, round(pct / 5))
        for s in range(20):
            on = s < segs
            fill = col if on else C["panel2"]
            st = f' style="animation:pop .1s steps(1,end) {i * 0.1 + s * 0.03:.2f}s both"' if on else ""
            b.append(f'<rect x="{lx + 128 + s * 10}" y="{ly + 2}" width="8" height="10" fill="{fill}"{st}/>')
        ly += 26
    # the contribution calendar is drawn by the snake image right under this panel, so it is not repeated here
    H = max(y, ly) + 4
    body = panel(W, H) + tab(24, "PLAYER STATS", "heart") + "".join(b)
    data = svg(W, H, body)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(data)
    print(f"  stats -> {out} ({len(data) / 1024:.1f} KB): {rows} top={[k for k, _ in top]}")


def stats_or_keep(out):
    """Actions fallback: if the API call fails, re-publish yesterday's file so the image never 404s."""
    try:
        stats(out)
    except Exception as e:  # noqa: BLE001
        print("  stats fetch failed:", e)
        url = f"https://raw.githubusercontent.com/{P['login']}/{P['login']}/output/pixel-stats.svg"
        urllib.request.urlretrieve(url, out)
        print("  kept previous", url)


# ---------------------------------------------------------------- main
def build_all():
    print("building", OUT)
    for f in os.listdir(OUT):  # drop images the README no longer uses
        if f.endswith(".svg") and (f.startswith(("h-", "btn-")) or f in ("quests.svg", "skills.svg")):
            os.remove(os.path.join(OUT, f))
    hero()
    card()
    log()
    inventory()
    rig()
    footer()
    for title, icon, fn in [("ARCADE", "joy", "d-arcade.svg"), ("SAVE POINT", "floppy", "d-social.svg"),
                            ("COIN SHOP", "coin", "d-donate.svg")]:
        divider(title, icon, fn)
    for lab, _url, col in P["socials"] + P["donate"]:
        dark = col in (C["yellow"], "#fbbf24")
        button(lab, col, f"btn-{slug(lab)}.svg", C["ink"] if dark else "#ffffff")
    button("▶ PLAY DIREWOLF", C["yellow"], "btn-play.svg", C["ink"])
    button("▶ WATCH TRAILER", C["red"], "btn-trailer.svg")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "stats":
        stats_or_keep(sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT, "stats-preview.svg"))
    else:
        build_all()
