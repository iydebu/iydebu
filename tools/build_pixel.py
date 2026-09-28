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


# ---------------------------------------------------------------- hero
def hero():
    W, H = 840, 300
    rnd = random.Random(7)
    b, css = [], []
    b.append(f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>')
    b.append(f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="url(#dots)"/>')
    # drifting gliders
    gens, cell, step = life_glider(), 8, 0.3
    css.append("@keyframes ph{0%{opacity:1}25%{opacity:0}100%{opacity:0}}")
    css.append(f".ph{{opacity:0;animation:ph {4 * step}s step-end infinite}}")
    b.append('<g clip-path="url(#inner)">')
    for gi in range(9):
        x0, y0 = rnd.randrange(-200, W - 80), rnd.randrange(-160, H - 120)
        dist = 36
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
    # arcade HUD
    b.append(text("1UP", 40, 24, 2, C["red"], attrs=' class="bl"'))
    b.append(text(P["handle"], 40, 44, 2, C["text"]))
    b.append(text("HI-SCORE", W / 2, 24, 2, C["red"], "middle"))
    b.append(text("999999", W / 2, 44, 2, C["text"], "middle"))
    b.append(text("STAGE", W - 40, 24, 2, C["red"], "end"))
    b.append(text("UE5", W - 40, 44, 2, C["text"], "end"))
    # title with hard-stop gradient and drop shadow
    name, sc = P["name"], 5
    b.append(text(name, W / 2 + sc, 88 + sc, sc, C["teal_d"], "middle"))
    b.append(text(name, W / 2, 88, sc, "url(#tg)", "middle"))
    # rotating taglines
    tl = P["taglines"]
    per = 3
    css.append(f"@keyframes tl{{0%{{opacity:1}}{100 / len(tl):.2f}%{{opacity:0}}100%{{opacity:0}}}}")
    for k, line in enumerate(tl):
        delay = ((len(tl) - k) % len(tl)) * per
        b.append(text(line, W / 2, 152, 3, C["mint"], "middle",
                      f' style="opacity:0;animation:tl {per * len(tl)}s step-end infinite;animation-delay:-{delay}s"'))
    b.append(text("▶ PRESS START", W / 2, 204, 2, C["yellow"], "middle", ' class="bl"'))
    # ground + runner
    gy = H - 48
    b.append(f'<rect x="4" y="{gy}" width="{W - 8}" height="4" fill="{C["teal"]}"/>')
    b.append(f'<rect x="4" y="{gy + 4}" width="{W - 8}" height="{H - gy - 8}" fill="url(#brick)"/>')
    css.append("@keyframes run{from{transform:translateX(-40px)}to{transform:translateX(880px)}}"
               ".run{animation:run 16s linear infinite}"
               "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}"
               ".fa{animation:fa .36s step-end infinite}.fb{opacity:0;animation:fb .36s step-end infinite}")
    b.append(f'<g clip-path="url(#inner)"><g class="run">'
             f'{sprite(RUN_A, RPAL, 0, gy - 30, 3, FA)}'
             f'{sprite(RUN_B, RPAL, 0, gy - 30, 3, FB)}</g></g>')
    # coins on the ground line
    for cx in (140, 300, 540, 700):
        b.append(sprite(ICONS["coin"], IPAL, cx, gy - 40, 2, ' class="bl"'))
    b.append(frame(0, 0, W, H, C["teal"], "none", 4))
    defs = (f'<pattern id="dots" width="12" height="12" patternUnits="userSpaceOnUse">'
            f'<rect width="2" height="2" fill="#12282b"/></pattern>'
            f'<pattern id="brick" width="32" height="16" patternUnits="userSpaceOnUse">'
            f'<rect width="32" height="16" fill="{C["panel"]}"/>'
            f'<path d="M0 0h32v2H0zM0 8h32v2H0zM0 0h2v8H0zM16 8h2v8h-2z" fill="{C["line"]}"/></pattern>'
            f'<linearGradient id="tg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset=".5" stop-color="{C["teal_l"]}"/><stop offset=".5" stop-color="{C["teal"]}"/></linearGradient>'
            f'<clipPath id="inner"><rect x="4" y="4" width="{W - 8}" height="{H - 8}"/></clipPath>')
    save("hero.svg", svg(W, H, "".join(b), "".join(css), defs))


# ---------------------------------------------------------------- section header
def header(num, title, icon, fname):
    W, H = 840, 64
    b = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>',
         f'<rect x="0" y="6" width="{W}" height="{H - 12}" fill="{C["panel"]}"/>',
         f'<rect x="0" y="6" width="8" height="{H - 12}" fill="{C["teal"]}"/>',
         f'<rect x="0" y="{H - 10}" width="{W}" height="4" fill="{C["teal_d"]}"/>',
         sprite(ICONS[icon], IPAL, 24, 16, 4),
         text(title, 76, 22, 3, C["text"])]
    x = 76 + tw(title, 3) + 20
    b.append(f'<path d="{"".join(f"M{i} 30h4v4h-4z" for i in range(x, W - 110, 12))}" fill="{C["line"]}"/>')
    b.append(text("▶", W - 92, 25, 2, C["yellow"], attrs=' class="bl"'))
    b.append(text(f"{num:02d}", W - 32, 22, 3, C["teal"], "end"))
    save(fname, svg(W, H, "".join(b), scan=False))


# ---------------------------------------------------------------- player card
def card():
    W, H = 840, 392
    b, css = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>'], []
    b.append(frame(0, 0, W, H, C["teal"], C["panel"], 4, C["line"]))
    b.append(f'<rect x="24" y="0" width="{tw("PLAYER 1", 2) + 24}" height="26" fill="{C["teal"]}"/>')
    b.append(text("PLAYER 1", 36, 6, 2, C["ink"]))
    # portrait
    b.append(frame(28, 44, 164, 164, C["line"], C["panel2"], 4))
    b.append(f'<rect x="32" y="48" width="156" height="156" fill="url(#dots2)"/>')
    b.append(sprite(AVATAR, APAL, 38, 54, 9))
    b.append(text(P["handle"] + " · LV " + str(datetime.date.today().year - 2021 + 20), 110, 220, 2, C["teal"], "middle"))
    # stat rows
    x, y = 224, 48
    for lab, val in P["card"]:
        b.append(text(lab, x, y, 2, C["dim"]))
        b.append(text(val, x + 84, y, 2, C["text"]))
        y += 28
    # HP / MP / XP bars
    bars = [("HP", C["red"], 10, "FULL"), ("MP", C["blue"], 8, "COFFEE"), ("XP", C["teal"], 7, "NEXT LV")]
    y = 170
    for i, (lab, col, fill, note) in enumerate(bars):
        b.append(text(lab, x, y + 3, 2, col))
        for s in range(10):
            sx = x + 36 + s * 34
            if s < fill:
                d = i * 0.25 + s * 0.06
                b.append(f'<g style="animation:pop .1s steps(1,end) {d:.2f}s both">'
                         f'<rect x="{sx}" y="{y}" width="30" height="18" fill="{col}"/>'
                         f'<rect x="{sx}" y="{y}" width="30" height="4" fill="{mix(col, "#ffffff", .45)}"/>'
                         f'<rect x="{sx}" y="{y + 14}" width="30" height="4" fill="{mix(col, "#000000", .35)}"/></g>')
            else:
                b.append(f'<rect x="{sx + 1}" y="{y + 1}" width="28" height="16" fill="{C["panel2"]}" '
                         f'stroke="{C["line"]}" stroke-width="2"/>')
        b.append(text(note, x + 36 + 340 + 12, y + 3, 2, C["dim"]))
        y += 28
    # dialog box with typewriter text
    dx, dy, dw = 24, 262, W - 48
    lines = P["dialog"]
    dh = 36 + 22 * len(lines)
    b.append(frame(dx, dy, dw, dh, C["text"], C["ink"], 4))
    b.append(f'<rect x="{dx + 20}" y="{dy - 10}" width="{tw("DEBU", 2) + 20}" height="22" fill="{C["ink"]}"/>')
    b.append(text("DEBU", dx + 30, dy - 4, 2, C["teal"]))
    b.append(f'<clipPath id="dlg"><rect x="{dx + 4}" y="{dy + 4}" width="{dw - 8}" height="{dh - 8}"/></clipPath>')
    t0, cps = 1.0, 0.04
    covers = []
    for i, ln in enumerate(lines):
        ly = dy + 22 + i * 22
        b.append(text(ln, dx + 24, ly, 2, C["text"]))
        cw = tw(ln, 2) + 14
        dur = len(ln) * cps
        css.append(f"@keyframes tw{i}{{to{{transform:translateX({cw}px)}}}}")
        covers.append(f'<rect x="{dx + 20}" y="{ly - 2}" width="{cw}" height="18" fill="{C["ink"]}" '
                      f'style="animation:tw{i} {dur:.2f}s steps({len(ln)},end) {t0:.2f}s forwards"/>')
        t0 += dur + 0.15
    b.append(f'<g clip-path="url(#dlg)">{"".join(covers)}</g>')
    b.append(f'<g style="animation:pop .1s steps(1,end) {t0:.2f}s both">'
             f'{text("▼", dx + dw - 36, dy + dh - 24, 2, C["yellow"], attrs=BL)}</g>')
    defs = (f'<pattern id="dots2" width="8" height="8" patternUnits="userSpaceOnUse">'
            f'<rect width="2" height="2" fill="{C["line"]}"/></pattern>')
    save("card.svg", svg(W, H, "".join(b), "".join(css), defs))


# ---------------------------------------------------------------- skill tree
def skills():
    rows = P["skills"]
    W, H = 840, 32 + 42 * len(rows)
    b = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>', frame(0, 0, W, H, C["line"], C["panel"], 4)]
    for r, (lab, lv) in enumerate(rows):
        y = 20 + r * 42
        b.append(text(lab, 32, y + 4, 2, C["text"]))
        for s in range(10):
            sx = 180 + s * 50
            if s < lv:
                col = C["yellow"] if lv >= 9 else C["teal"]
                d = r * 0.12 + s * 0.07
                b.append(f'<g style="animation:pop .1s steps(1,end) {d:.2f}s both">'
                         f'<rect x="{sx}" y="{y}" width="44" height="22" fill="{col}"/>'
                         f'<rect x="{sx}" y="{y}" width="44" height="4" fill="{mix(col, "#ffffff", .5)}"/>'
                         f'<rect x="{sx}" y="{y + 18}" width="44" height="4" fill="{mix(col, "#000000", .35)}"/></g>')
            else:
                b.append(f'<rect x="{sx + 1}" y="{y + 1}" width="42" height="20" fill="{C["panel2"]}" '
                         f'stroke="{C["line"]}" stroke-width="2"/>')
        b.append(text(f"LV {lv}", W - 36, y + 4, 2, C["yellow"] if lv >= 9 else C["teal"], "end"))
    save("skills.svg", svg(W, H, "".join(b)))


# ---------------------------------------------------------------- quest log
def quests():
    rows = P["quests"]
    W, H = 840, 24 + 64 * len(rows)
    b = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>', frame(0, 0, W, H, C["line"], C["panel"], 4)]
    tagc = {"MAIN": C["yellow"], "SIDE": C["blue"], "DONE": C["teal"]}
    for r, (state, tag, title, sub) in enumerate(rows):
        y = 16 + r * 64
        if r:
            b.append(f'<path d="{"".join(f"M{i} {y - 6}h4v2h-4z" for i in range(24, W - 24, 8))}" fill="{C["line"]}"/>')
        mcol = {"active": C["yellow"], "todo": C["gray"], "done": C["teal"]}[state]
        glyph = {"active": "!", "todo": "?", "done": "✓"}[state]
        b.append(frame(24, y + 4, 40, 40, mcol, C["ink"], 4))
        b.append(text(glyph, 44, y + 13, 3, mcol, "middle", ' class="bl"' if state == "active" else ""))
        tc = tagc[tag]
        b.append(f'<rect x="80" y="{y + 6}" width="{tw(tag, 2) + 16}" height="22" fill="{tc}"/>')
        b.append(text(tag, 88, y + 10, 2, C["ink"]))
        done = state == "done"
        b.append(text(title, 160, y + 6, 3, C["dim"] if done else C["text"]))
        if done:
            b.append(f'<rect x="156" y="{y + 15}" width="{tw(title, 3) + 8}" height="3" fill="{C["dim"]}"/>')
        b.append(text(sub, 160, y + 34, 2, C["dim"]))
    save("quests.svg", svg(W, H, "".join(b)))


# ---------------------------------------------------------------- inventory
def inventory():
    cats = P["inventory"]
    sw, sh, gap, cols = 188, 48, 8, 4
    body, y = [], 20
    for cat, items in cats:
        body.append(text(cat, 32, y, 2, C["teal"]))
        body.append(f'<rect x="{32 + tw(cat, 2) + 12}" y="{y + 6}" width="{840 - 64 - tw(cat, 2) - 12}" height="2" fill="{C["line"]}"/>')
        y += 24
        for i, (name, rar) in enumerate(items):
            sx = 32 + (i % cols) * (sw + gap)
            sy = y + (i // cols) * (sh + gap)
            col = RARITY[rar][1]
            body.append(frame(sx, sy, sw, sh, col, C["panel2"], 3))
            body.append(f'<rect x="{sx + 3}" y="{sy + 3}" width="{sw - 6}" height="3" fill="{mix(col, C["panel2"], .6)}"/>')
            body.append(text(name, sx + sw / 2, sy + 17, 2, C["text"], "middle"))
            body.append(f'<rect x="{sx + sw - 13}" y="{sy + 7}" width="6" height="6" fill="{col}"'
                        f'{BL if rar == "L" else ""}/>')
        y += ((len(items) + cols - 1) // cols) * (sh + gap) + 14
    lx = 32
    for key in "LERC":
        lab, col = RARITY[key]
        body.append(f'<rect x="{lx}" y="{y + 2}" width="10" height="10" fill="{col}"/>')
        body.append(text(lab, lx + 18, y, 2, C["dim"]))
        lx += 18 + tw(lab, 2) + 36
    W, H = 840, y + 36
    b = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>', frame(0, 0, W, H, C["line"], C["panel"], 4)] + body
    save("inventory.svg", svg(W, H, "".join(b)))


# ---------------------------------------------------------------- buttons
def button(label, col, fname, fg="#ffffff"):
    W, H = tw(label, 2) + 44, 44
    hi, lo = mix(col, "#ffffff", .35), mix(col, "#000000", .4)
    b = [f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="{col}"/>',
         f'<rect x="4" y="4" width="{W - 8}" height="4" fill="{hi}"/>',
         f'<rect x="4" y="{H - 10}" width="{W - 8}" height="6" fill="{lo}"/>',
         frame(0, 0, W, H, C["ink"], "none", 2)]
    shadow = C["ink"] if fg == "#ffffff" else mix(col, "#ffffff", .5)
    b.append(text(label, W / 2 + 2, 15, 2, shadow, "middle"))
    b.append(text(label, W / 2, 13, 2, fg, "middle"))
    save(fname, svg(W, H, "".join(b), scan=False))


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


# ---------------------------------------------------------------- rig + footer
def rig():
    lines = P["rig"]["lines"]
    W, H = 840, 60 + 30 * len(lines) + 30
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
    b.append(text("POWER LEVEL: OVER 9000", x, y + 4, 2, C["yellow"], attrs=' class="bl"'))
    save("rig.svg", svg(W, H, "".join(b)))


def footer():
    W, H = 840, 220
    b, css = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>'], []
    b.append(text("THANKS FOR PLAYING", W / 2 + 4, 34 + 4, 4, C["teal_d"], "middle"))
    b.append(text("THANKS FOR PLAYING", W / 2, 34, 4, C["teal_l"], "middle"))
    cx = W / 2 - tw("CONTINUE? 9", 3) / 2
    b.append(text("CONTINUE?", cx, 96, 3, C["text"]))
    css.append("@keyframes cd{0%{opacity:1}10%{opacity:0}100%{opacity:0}}")
    dx = cx + tw("CONTINUE? ", 3) + 3
    for i, dgt in enumerate("9876543210"):
        b.append(text(dgt, dx, 96, 3, C["yellow"], attrs=f' style="opacity:0;animation:cd 10s step-end infinite;'
                                                         f'animation-delay:-{(10 - i) % 10}s"'))
    b.append(text("INSERT COIN", W / 2, 148, 2, C["yellow"], "middle", ' class="bl"'))
    b.append(text("(C) " + P["handle"] + " · MADE WITH PIXELS", W / 2, 184, 2, C["dim"], "middle"))
    for sx in (120, 690):
        b.append(sprite(ICONS["star"], IPAL, sx, 90, 3, ' class="bl"'))
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
    b.append(text("PLAYER STATS", 32, 24, 2, C["teal"]))
    b.append(text("SINCE " + since, 400, 24, 2, C["dim"], "end"))
    y = 56
    for lab, val in rows:
        b.append(text(lab, 32, y, 2, C["dim"]))
        b.append(text(str(val), 400, y, 2, C["yellow"] if "STREAK" in lab else C["text"], "end"))
        y += 26
    lx = 440
    b.append(f'<rect x="420" y="20" width="2" height="{y - 24}" fill="{C["line"]}"/>')
    b.append(text("TOP LANGUAGES", lx, 24, 2, C["teal"]))
    ly = 56
    for i, (nm, (size, col)) in enumerate(top):
        pct = size * 100 / total
        b.append(text(nm[:14], lx, ly, 2, C["text"]))
        b.append(text(f"{pct:.0f}%", W - 32, ly, 2, C["dim"], "end"))
        segs = max(1, round(pct / 5))
        for s in range(20):
            on = s < segs
            fill = col if on else C["panel2"]
            st = f' style="animation:pop .1s steps(1,end) {i * 0.1 + s * 0.03:.2f}s both"' if on else ""
            b.append(f'<rect x="{lx + s * 18}" y="{ly + 18}" width="14" height="6" fill="{fill}"{st}/>')
        ly += 34
    # contribution heatmap (pixel calendar)
    hy = max(y, ly) + 10
    b.append(text("QUEST HISTORY - LAST 12 MONTHS", 32, hy, 2, C["teal"]))
    b.append(text("UPDATED " + datetime.date.today().isoformat(), W - 32, hy, 2, C["dim"], "end"))
    hy += 26
    peak = max((d["contributionCount"] for d in days), default=1) or 1
    shades = [C["panel2"], "#0e4f4a", "#0f766e", C["teal"], C["teal_l"]]
    weeks = cc["contributionCalendar"]["weeks"][-53:]
    cell, step = 11, 14
    ox = (W - len(weeks) * step + 3) / 2
    per = {k: [] for k in range(5)}
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            dow = datetime.date.fromisoformat(d["date"]).isoweekday() % 7
            c = d["contributionCount"]
            lvl = 0 if not c else min(4, 1 + int(3 * c / peak + 0.5))
            per[lvl].append(f"M{n(ox + wi * step)} {hy + dow * step}h{cell}v{cell}h-{cell}z")
    for lvl, ds in per.items():
        if ds:
            b.append(f'<path d="{"".join(ds)}" fill="{shades[lvl]}"/>')
    H = hy + 7 * step + 20
    body = f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>' + frame(0, 0, W, H, C["line"], C["panel"], 4) + "".join(b)
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
    hero()
    card()
    for i, (title, icon, fn) in enumerate([("QUEST LOG", "scroll", "h-quests.svg"),
                                           ("SKILL TREE", "sword", "h-skills.svg"),
                                           ("INVENTORY", "chest", "h-inventory.svg"),
                                           ("PLAYER STATS", "heart", "h-stats.svg"),
                                           ("ARCADE", "joy", "h-arcade.svg"),
                                           ("SAVE POINT", "floppy", "h-social.svg"),
                                           ("COIN SHOP", "coin", "h-donate.svg"),
                                           ("BIG BOY", "pc", "h-rig.svg")], 1):
        header(i, title, icon, fn)
    quests()
    skills()
    inventory()
    rig()
    footer()
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
