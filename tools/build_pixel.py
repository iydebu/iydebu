#!/usr/bin/env python3
"""iydebu.com-themed pixel GitHub profile generator for iydebu/iydebu (stdlib only).

    python tools/build_pixel.py             build every static SVG into Img/pixel/
    python tools/build_pixel.py stats OUT   live PLAYER STATS svg (GitHub GraphQL)

Text/links/skills live in tools/profile.json - edit that, rerun, commit.
GitHub strips CSS and web fonts from README HTML, so every letter here is drawn
from a 5x7 bitmap font as SVG paths; animation is CSS inside each SVG.
"""
import datetime
import json
import math
import os
import random
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Img", "pixel")
P = json.load(open(os.path.join(ROOT, "tools", "profile.json"), encoding="utf-8"))

# iydebu.com palette (site/style.css :root + js/art.js meadow)
C = dict(ink="#1a1a2e", paper="#fffbee", teal="#14b8a6", teal_dk="#0e8f81", teal_hi="#5eead4",
         gold="#ffd54a", gold_dk="#d9a520", red="#e0474c", white="#ffffff", line="#e6dcc0",
         well="#ece3c8", dim="#7a7466", purple="#8b5cf6", blue="#3b82f6", gray="#94a3b8")
RARITY = {"L": ("LEGENDARY", C["gold"]), "E": ("EPIC", C["purple"]),
          "R": ("RARE", C["blue"]), "C": ("COMMON", C["gray"])}

# ---------------------------------------------------------------- 5x7 font
_F = r"""
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


def nrect(x, y, w, h, fill, c=4, attrs=""):
    """Rectangle with square-notched corners: the pixel-art version of the site's rounded cards."""
    return (f'<path d="M{n(x + c)} {n(y)}h{n(w - 2 * c)}v{c}h{c}v{n(h - 2 * c)}h{-c}v{c}h{n(-(w - 2 * c))}'
            f'v{-c}h{-c}v{n(-(h - 2 * c))}h{c}z" fill="{fill}"{attrs}/>')


def bold(s, x, y, sc, fill, anchor="start", attrs=""):
    """Faux-bold pixel text: the same glyphs drawn twice, one pixel apart."""
    return text(s, x, y, sc, fill, anchor, attrs) + text(s, x + max(1, sc // 2), y, sc, fill, anchor, attrs)


BASE_CSS = ("@keyframes bl{0%{opacity:1}50%{opacity:0}}.bl{animation:bl 1s step-end infinite}"
            "@keyframes pop{from{opacity:0}to{opacity:1}}")
BL = ' class="bl"'
FA, FB = ' class="fa"', ' class="fb"'


def svg(w, h, body, css="", defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'shape-rendering="crispEdges"><style>{BASE_CSS}{css}</style><defs>{defs}</defs>{body}</svg>')


def save(name, data):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    print(f"  {name:36s} {len(data) / 1024:6.1f} KB")


def fit(s, width, sc, where):
    """Warn when a line would run past its box (only visible at render time otherwise)."""
    if tw(s, sc) > width:
        print(f"  ! {where}: '{s}' is {tw(s, sc)}px, box is {width}px - shorten it in profile.json")
    return s


# ---------------------------------------------------------------- sprites
ICONS = {
    "heart": ["........", ".rr..rr.", "rwrrrrrr", "rrrrrrrr", "rrrrrrrr", ".rrrrrr.", "..rrrr..", "...rr..."],
    "sword": ["......gw", ".....gwg", "....gwg.", ".y.gwg..", "..ygg...", "..yy....", ".b..y...", "b......."],
    "chest": ["........", ".bbbbbb.", "bbbbbbbb", "yyyyyyyy", "bbbyybbb", "bbbkkbbb", "bbbbbbbb", "........"],
    "scroll": ["yyyyyyy.", ".wwwwwy.", ".wkkkkw.", ".wwwwww.", ".wkkkww.", ".wwwwww.", ".yyyyyyy", "........"],
    "joy": ["...rr...", "..rrrr..", "...rr...", "...gg...", "...gg...", ".tttttt.", "tttttttt", "TTTTTTTT"],
    "floppy": ["ttttttt.", "twwwwgtt", "twwwwgtt", "tttttttt", "tTTTTTTt", "tTwwwwTt", "tTwwwwTt", "tttttttt"],
    "coin": ["..yyyy..", ".yyyyyy.", "yyyYYyyy", "yyYyyyyy", "yyyYYyyy", "yyyyyYyy", ".yYYYyy.", "..yyyy.."],
    "pc": ["gggggggg", "gTTTTTTg", "gTttwtTg", "gTtttTTg", "gTTTTTTg", "gggggggg", "...gg...", ".gggggg."],
    "star": ["...yy...", "...yy...", "yyyyyyyy", ".yyyyyy.", "..yyyy..", ".yy..yy.", ".y....y.", "........"],
}
IPAL = {"r": C["red"], "w": "#ffffff", "g": "#64748b", "y": C["gold"], "Y": C["gold_dk"], "b": "#8b5a2b",
        "k": C["ink"], "t": C["teal"], "T": C["teal_dk"]}

AVATAR = ["....kkkkkkkk....", "...khhhhhhhhk...", "..khhhhhhhhhhk..", "..khhhhhhhhhhk..",
          "..khhsshhhsshk..", "..khssssssshhk..", "..kswwsssswwsk..", "..kswesssswesk..",
          "..kssssddssssk..", "..kssssssssssk..", "...kssseesssk...", "....kssssssk....",
          "...kTTkrrkTTk...", "..kTTTTrrTTTTk..", ".kTTTTTttTTTTTk.", ".kTTTTTttTTTTTk."]
APAL = {"k": C["ink"], "h": "#1f1a17", "s": "#c68a5e", "d": "#9c6644", "w": "#ffffff",
        "e": C["ink"], "t": C["teal_hi"], "T": C["teal"], "r": C["red"]}

# the site's player: dark hair, teal shirt, red scarf
RUN_TOP = ["..hhhh..", ".hhhhhs.", ".hhssss.", "..ssss..", ".rrtttt.", "s.tttt.s", "..tttt.."]
RUN_A = RUN_TOP + ["..k..k..", ".k....k.", "kk....kk"]
RUN_B = RUN_TOP + ["...kk...", "...kk...", "..kkkk.."]
RPAL = {"h": "#1f1a17", "s": "#c68a5e", "t": C["teal"], "r": C["red"], "k": C["ink"]}


def hsh(*a):
    """Stable 0..1 hash (same art every build)."""
    v = 0
    for x in a:
        v = (v * 1_000_003 + int(x) * 7919 + 12345) & 0xFFFFFFFF
    v ^= v >> 13
    v = (v * 0x5BD1E995) & 0xFFFFFFFF
    v ^= v >> 15
    return (v & 0xFFFF) / 0xFFFF


def disc(cx, cy, r, px=4):
    """Pixel circle as one path: rows of a px grid."""
    d = []
    y = -r
    while y < r:
        mid = y + px / 2
        if abs(mid) < r:
            hw = round(math.sqrt(r * r - mid * mid) / px) * px
            if hw:
                d.append(f"M{n(cx - hw)} {n(cy + y)}h{n(2 * hw)}v{px}h{n(-2 * hw)}z")
        y += px
    return "".join(d)


def columns(x0, x1, top, bottom, px=4):
    """Filled heightfield: one column per px, from top(x) down to bottom."""
    d = []
    for x in range(x0, x1, px):
        t = top(x)
        if t < bottom:
            d.append(f"M{x} {n(t)}h{px}v{n(bottom - t)}h{-px}z")
    return "".join(d)


def q(v, px=4):
    return round(v / px) * px


# ---------------------------------------------------------------- shared panel bits
def card_box(W, H, fill=None):
    """The site's info card: cream paper, dark navy border, chunky bottom shadow. H includes the shadow."""
    ch = H - SH
    return (nrect(0, SH, W, ch, C["ink"], 6, ' opacity=".45"') + nrect(0, 0, W, ch, C["ink"], 6)
            + nrect(4, 4, W - 8, ch - 8, fill or C["paper"], 4))


def header(x, tag, title):
    """Small teal tag + bold navy title, like #card .tag / #card h2 on the site."""
    return text(tag, x, 16, 1, C["teal_dk"]) + bold(title, x, 28, 2, C["ink"])


TOP = 56  # first content row under a header
SH = 6    # card shadow depth


# ---------------------------------------------------------------- hero: the site's title screen
def hero():
    W, H, gy = 840, 300, 252
    b, css = [], []
    sky = ["#3d8fdc", "#4c9ee4", "#5caceb", "#6fbaf0", "#83c7f3", "#98d3f5", "#afdef6", "#c6e8f6", "#dcf1f3"]
    defs = []
    # dithered sky: solid bands, each fading into the next with a checker strip
    bh = gy / len(sky)
    for i, col in enumerate(sky):
        y0 = round(i * bh)
        b.append(f'<rect x="0" y="{y0}" width="{W}" height="{round((i + 1) * bh) - y0}" fill="{col}"/>')
        if i + 1 < len(sky):
            defs.append(f'<pattern id="ck{i}" width="8" height="8" patternUnits="userSpaceOnUse">'
                        f'<path d="M0 0h4v4H0zM4 4h4v4H4z" fill="{sky[i + 1]}"/></pattern>')
            b.append(f'<rect x="0" y="{round((i + 1) * bh) - 8}" width="{W}" height="8" fill="url(#ck{i})"/>')
    # dithered sun with halo
    sx, sy = 690, 52
    defs.append('<pattern id="sp" width="8" height="8" patternUnits="userSpaceOnUse">'
                '<path d="M0 0h4v4H0z" fill="#fff6cf"/></pattern>'
                '<pattern id="sc" width="8" height="8" patternUnits="userSpaceOnUse">'
                '<path d="M0 0h4v4H0zM4 4h4v4H4z" fill="#fff6cf"/></pattern>')
    b.append(f'<path d="{disc(sx, sy, 64)}" fill="url(#sp)"/>')
    b.append(f'<path d="{disc(sx, sy, 50)}" fill="url(#sc)"/>')
    b.append(f'<path d="{disc(sx, sy, 40)}" fill="#f6f7de"/>')
    b.append(f'<path d="{disc(sx, sy, 32)}" fill="#fff6cf"/>')
    b.append(f'<path d="{disc(sx, sy, 22)}" fill="#fff1bd"/>')
    b.append(f'<path d="{disc(sx, sy, 16)}" fill="#fffbe8"/>')
    # snowy mountains
    peaks = [(40, 96), (170, 70), (310, 104), (450, 78), (590, 100), (740, 66), (860, 92)]

    def mtop(x):
        return q(min(py + abs(x + 2 - px) * 0.78 for px, py in peaks) + hsh(x, 1) * 4)

    def near_peak(x):
        return min(peaks, key=lambda p: p[1] + abs(x + 2 - p[0]) * 0.78)

    b.append(f'<path d="{columns(0, W, mtop, 200)}" fill="#9dbde0"/>')
    shade = columns(0, W, lambda x: mtop(x) if x > near_peak(x)[0] else 999, 200)
    b.append(f'<path d="{shade}" fill="#8aaed6"/>')
    snow = []
    for x in range(0, W, 4):
        px_, py_ = near_peak(x)
        t, line = mtop(x), q(py_ + 18 + hsh(x, 2) * 8)
        if t < line:
            snow.append(f"M{x} {t}h4v{line - t}h-4z")
    b.append(f'<path d="{"".join(snow)}" fill="#f5f9ff"/>')
    b.append(f'<rect x="0" y="156" width="{W}" height="44" fill="#b9d5ee" opacity=".55"/>')
    # clouds: white puffs with a blue underside
    for cx, cy, s in [(92, 118, 1.0), (268, 104, 1.2), (560, 128, 0.9), (800, 112, 1.1)]:
        puffs = [(-30 * s, 6, 14 * s), (-10 * s, -2, 20 * s), (14 * s, 0, 18 * s), (34 * s, 6, 13 * s)]
        b.append(f'<path d="{"".join(disc(q(cx + dx), q(cy + dy + 4), r) for dx, dy, r in puffs)}" fill="#d3e8f6"/>')
        b.append(f'<path d="{"".join(disc(q(cx + dx), q(cy + dy), r) for dx, dy, r in puffs)}" fill="#ffffff"/>')
    # birds
    for bx, by in [(560, 70), (578, 62), (592, 74)]:
        b.append(f'<path d="M{bx} {by}h2v2h-2zM{bx + 2} {by + 2}h2v2h-2zM{bx + 4} {by}h2v2h-2z" fill="#34506e"/>')

    # far hills + small trees
    def far(x):
        return q(186 - 16 * math.sin(x / 95 + 1) - 8 * math.sin(x / 37))

    trees_far = []
    for x in range(12, W, 58):
        tx = q(x + hsh(x, 3) * 20)
        trees_far.append(disc(tx, far(tx) - 4, 10))
    b.append(f'<path d="{"".join(trees_far)}" fill="#7bbf9a"/>')
    b.append(f'<path d="{columns(0, W, far, gy)}" fill="#8ac9a7"/>')
    b.append(f'<path d="{columns(0, W, far, gy)}" fill="none"/>')
    b.append(f'<path d="{"".join(f"M{x} {far(x)}h4v4h-4z" for x in range(0, W, 4))}" fill="#bfe8cf"/>')

    # near hills + round trees
    def near(x):
        return q(222 - 18 * math.sin(x / 120 + 2) - 7 * math.sin(x / 43))

    b.append(f'<path d="{columns(0, W, near, gy)}" fill="#5dab58"/>')
    b.append(f'<path d="{"".join(f"M{x} {near(x)}h4v4h-4z" for x in range(0, W, 4))}" fill="#8fd67a"/>')
    trunks, outl, leaf, hi = [], [], [], []
    for x in [24, 84, 150, 196, 660, 712, 772, 818]:
        tx, r = q(x + hsh(x, 5) * 8), 12 + q(hsh(x, 6) * 8)
        base = near(tx) + 8
        cy = base - 14 - r
        trunks.append(f"M{tx - 2} {cy}h4v{base - cy}h-4z")
        outl.append(disc(tx, cy, r + 4))
        leaf.append(disc(tx, cy, r))
        hi.append(disc(tx - 4, cy - 4, r // 2 + 2))
    b.append(f'<path d="{"".join(trunks)}" fill="#5a3f25"/>')
    b.append(f'<path d="{"".join(outl)}" fill="#2d6e3a"/>')
    b.append(f'<path d="{"".join(leaf)}" fill="#50a04d"/>')
    b.append(f'<path d="{"".join(hi)}" fill="#72c563"/>')

    # grass + dirt ground
    b.append(f'<rect x="0" y="{gy}" width="{W}" height="{H - gy}" fill="#87562a"/>')
    b.append(f'<rect x="0" y="{gy + 28}" width="{W}" height="{H - gy - 28}" fill="#6b4322"/>')
    b.append(f'<rect x="0" y="{gy}" width="{W}" height="12" fill="#5bb23f"/>')
    b.append(f'<rect x="0" y="{gy}" width="{W}" height="4" fill="#8fdc5a"/>')
    tuft = "".join(f"M{x} {gy - 4}h4v4h-4z" for x in range(0, W, 4) if hsh(x, 7) < 0.35)
    drip = "".join(f"M{x} {gy + 12}h4v4h-4z" for x in range(0, W, 4) if hsh(x, 8) < 0.5)
    b.append(f'<path d="{tuft}" fill="#6cc24a"/><path d="{drip}" fill="#3f8f32"/>')
    spk = "".join(f"M{q(hsh(i, 9) * W)} {gy + 18 + q(hsh(i, 10) * (H - gy - 22))}h4v4h-4z" for i in range(70))
    dk = "".join(f"M{q(hsh(i, 11) * W)} {gy + 18 + q(hsh(i, 12) * (H - gy - 22))}h4v4h-4z" for i in range(50))
    peb = "".join(f"M{q(hsh(i, 13) * W)} {gy + 20 + q(hsh(i, 14) * (H - gy - 26))}h8v4h-8z" for i in range(14))
    b.append(f'<path d="{spk}" fill="#a8774a"/><path d="{dk}" fill="#55331a"/><path d="{peb}" fill="#9b8f82"/>')
    for i, pc in enumerate(["#ffffff", "#ff8fb1", "#b39dff", "#ffd54a", "#ff7a59", "#ffffff"]):
        fx = q(40 + i * 139 + hsh(i, 15) * 60)
        b.append(f'<path d="M{fx} {gy - 8}h4v4h-4zM{fx - 4} {gy - 4}h12v0z" fill="{pc}"/>'
                 f'<rect x="{fx}" y="{gy - 4}" width="4" height="4" fill="#3f9a3a"/>')
    # runner + coins
    css.append("@keyframes run{from{transform:translateX(-40px)}to{transform:translateX(880px)}}"
               ".run{animation:run 14s linear infinite}"
               "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}"
               ".fa{animation:fa .36s step-end infinite}.fb{opacity:0;animation:fb .36s step-end infinite}"
               "@keyframes bob{50%{transform:translateY(-4px)}}.bob{animation:bob 1.2s steps(2,end) infinite}")
    for cx in (96, 140, 700, 744):
        b.append(f'<g class="bob">{sprite(ICONS["coin"], IPAL, cx, gy - 44, 2)}</g>')
    b.append(f'<g class="run">{sprite(RUN_A, RPAL, 0, gy - 30, 3, FA)}{sprite(RUN_B, RPAL, 0, gy - 30, 3, FB)}</g>')

    # title box (dark, teal border) with the DEBU logo and two cartridges
    bx, by, bw, bh2 = 214, 16, 412, 232
    b.append(nrect(bx - 2, by - 2, bw + 4, bh2 + 4, C["ink"], 8))
    b.append(nrect(bx, by, bw, bh2, C["teal"], 8))
    b.append(nrect(bx + 4, by + 4, bw - 8, bh2 - 8, "#101b20", 6, ' opacity=".96"'))
    mx, logo, sc = W / 2, P["logo"], 8
    ly = by + 18
    for ox, oy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-3, -3), (3, 3), (-3, 3), (3, -3)]:
        b.append(text(logo, mx + ox + 5, ly + oy + 5, sc, C["ink"], "middle"))
    b.append(text(logo, mx + 5, ly + 5, sc, C["teal"], "middle"))
    for ox, oy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
        b.append(text(logo, mx + ox, ly + oy, sc, C["ink"], "middle"))
    b.append(text(logo, mx, ly, sc, "url(#lg)", "middle"))
    defs.append(f'<linearGradient id="lg" x1="0" y1="0" x2="0" y2="1"><stop offset=".45" stop-color="#ffe790"/>'
                f'<stop offset=".45" stop-color="{C["gold"]}"/></linearGradient>')
    b.append(bold(P["name"], mx, by + 90, 2, "#ffffff", "middle"))
    tl, per = P["taglines"], 3
    css.append(f"@keyframes tl{{0%{{opacity:1}}{100 / len(tl):.2f}%{{opacity:0}}100%{{opacity:0}}}}")
    for k, line in enumerate(tl):
        fit(line, bw - 40, 2, "hero tagline")
        delay = ((len(tl) - k) % len(tl)) * per
        b.append(text(line, mx, by + 112, 2, "#cfd8dc", "middle",
                      f' style="opacity:0;animation:tl {per * len(tl)}s step-end infinite;animation-delay:-{delay}s"'))
    b.append(text("HOW DO YOU WANT TO SEE MY WORK?", mx, by + 136, 1, C["teal_hi"], "middle"))
    cw, chh, cy = (bw - 24 * 2 - 16) // 2, 54, by + 150
    for i, (lab, sub, col) in enumerate(P["cartridges"]):
        cx = bx + 24 + i * (cw + 16)
        b.append(cartridge(cx, cy, cw, chh, lab, sub, C[col]))
    b.append(text("CLICK TO VISIT IYDEBU.COM", mx, by + bh2 - 20, 1, "#8fa3a8", "middle", BL))
    b.append(frame(0, 0, W, H, C["ink"], "none", 4))
    save("hero.svg", svg(W, H, "".join(b), "".join(css), "".join(defs)))


def cartridge(x, y, w, h, label, sub, col):
    """Game-cartridge button: coloured shell, navy outline, grip ridges, chunky bottom shadow."""
    s = [nrect(x, y + 4, w, h, "#000000", 4, ' opacity=".45"'),
         nrect(x, y, w, h, C["ink"], 4),
         nrect(x + 3, y + 3, w - 6, h - 6, col, 3),
         f'<rect x="{x + 3}" y="{y + 3}" width="{w - 6}" height="3" fill="{mix(col, "#ffffff", .45)}"/>',
         f'<rect x="{x + 3}" y="{y + h - 7}" width="{w - 6}" height="4" fill="{mix(col, "#000000", .25)}"/>']
    for k in range(3):  # grip ridges on the top edge
        s.append(f'<rect x="{x + w - 30 + k * 8}" y="{y + 6}" width="4" height="8" fill="{mix(col, C["ink"], .35)}"/>')
    s.append(bold(fit(label, w - 20, 2, "cartridge"), x + w / 2, y + 14, 2, C["ink"], "middle"))
    s.append(text(fit(sub, w - 16, 1, "cartridge"), x + w / 2, y + 34, 1, mix(col, C["ink"], .7), "middle"))
    return "".join(s)


# ---------------------------------------------------------------- section divider (small)
def divider(title, icon, fname):
    W, H = 840, 34
    pw = tw(title, 2) + 50
    b = [nrect(0, 5, pw, 28, "#000000", 4, ' opacity=".35"'), nrect(0, 1, pw, 28, C["teal"], 4),
         nrect(2, 3, pw - 4, 24, C["ink"], 3), sprite(ICONS[icon], IPAL, 10, 7, 2),
         bold(title, 34, 8, 2, "#ffffff")]
    b.append(f'<path d="{"".join(f"M{i} 14h4v4h-4z" for i in range(pw + 12, W - 4, 12))}" fill="{C["teal"]}"/>')
    save(fname, svg(W, H, "".join(b)))


# ---------------------------------------------------------------- player card
def card():
    W = 840
    b, css = [], []
    b.append(header(24, "PLAYER 1 · IN 10 SECONDS", P["name"]))
    # portrait: the player in front of the site sky
    px, py = 24, TOP
    b.append(nrect(px, py, 120, 120, C["ink"], 4))
    b.append(f'<rect x="{px + 4}" y="{py + 4}" width="112" height="112" fill="#83c7f3"/>')
    b.append(f'<rect x="{px + 4}" y="{py + 88}" width="112" height="28" fill="#5dab58"/>')
    b.append(f'<rect x="{px + 4}" y="{py + 88}" width="112" height="4" fill="#8fdc5a"/>')
    b.append(sprite(AVATAR, APAL, px + 4, py + 4, 7))
    # info rows
    x, y = 164, TOP + 4
    for lab, val in P["card"]:
        b.append(text(lab, x, y, 2, C["teal_dk"]))
        b.append(text(fit(val, 548 - 20 - (x + 84), 2, "card row"), x + 84, y, 2, C["ink"]))
        y += 28
    # site stats, right column
    sx0 = 550
    b.append(f'<rect x="{sx0 - 16}" y="{TOP}" width="2" height="120" fill="{C["line"]}"/>')
    for i, (num, lab) in enumerate(P["card_stats"]):
        sy = TOP + 2 + i * 42
        lx = sx0 + tw(num, 3) + 14
        b.append(text(num, sx0 + 2, sy + 2, 3, C["gold"]))
        b.append(bold(num, sx0, sy, 3, C["ink"]))
        b.append(text(fit(lab, W - 24 - lx, 2, "card stat"), lx, sy + 4, 2, C["dim"]))
    # dialog box with typewriter text (navy, like the site's title box)
    lines = P["dialog"]
    dx, dy, dw = 24, TOP + 144, W - 48
    dh = 30 + 22 * len(lines)
    H = dy + dh + 20 + SH
    b.append(nrect(dx, dy, dw, dh, C["teal"], 6))
    b.append(nrect(dx + 4, dy + 4, dw - 8, dh - 8, C["ink"], 4))
    b.append(nrect(dx + 20, dy - 12, tw("DEBU", 2) + 24, 24, C["gold"], 3))
    b.append(bold("DEBU", dx + 32, dy - 5, 2, C["ink"]))
    b.append(f'<clipPath id="dlg"><rect x="{dx + 4}" y="{dy + 12}" width="{dw - 8}" height="{dh - 16}"/></clipPath>')
    t0, cps = 1.0, 0.035
    covers = []
    for i, ln in enumerate(lines):
        ly = dy + 20 + i * 22
        fit(ln, dw - 44, 2, "dialog")
        b.append(text(ln, dx + 22, ly, 2, C["teal_hi"] if "PARTNER" in ln else "#ffffff"))
        cw = tw(ln, 2) + 14
        dur = len(ln) * cps
        css.append(f"@keyframes tw{i}{{to{{transform:translateX({cw}px)}}}}")
        covers.append(f'<rect x="{dx + 18}" y="{ly - 2}" width="{cw}" height="18" fill="{C["ink"]}" '
                      f'style="animation:tw{i} {dur:.2f}s steps({len(ln)},end) {t0:.2f}s forwards"/>')
        t0 += dur + 0.15
    b.append(f'<g clip-path="url(#dlg)">{"".join(covers)}</g>')
    b.append(f'<g style="animation:pop .1s steps(1,end) {t0:.2f}s both">'
             f'{text("▼", dx + dw - 30, dy + dh - 22, 2, C["gold"], attrs=BL)}</g>')
    save("card.svg", svg(W, H, card_box(W, H) + "".join(b), "".join(css)))


# ---------------------------------------------------------------- quest log + skill tree (two columns)
def log():
    W, qs, sk = 840, P["quests"], P["skills"]
    step = 26
    H = TOP + max(len(qs), len(sk)) * step + 10 + SH
    b = [card_box(W, H), header(24, "QUEST LOG", "SHIPPED + BUILDING"), header(440, "SKILL TREE", "LEVELS"),
         f'<rect x="420" y="{TOP - 4}" width="2" height="{H - TOP - 14 - SH}" fill="{C["line"]}"/>']
    tagc = {"SHIP": C["gold"], "WORK": C["teal"], "OWN": C["red"]}
    for r, (state, tag, title, _sub) in enumerate(qs):
        title = title if len(title) <= 28 else title[:27] + "."  # left column fits 28 chars
        y = TOP + r * step
        mcol = {"active": C["gold"], "done": C["teal"]}[state]
        glyph = {"active": "!", "done": "✓"}[state]
        b.append(nrect(24, y - 3, 20, 20, C["ink"], 2))
        b.append(text(glyph, 34, y, 2, mcol, "middle", BL if state == "active" else ""))
        b.append(f'<rect x="52" y="{y - 1}" width="4" height="16" fill="{tagc[tag]}"/>')
        b.append(text(title, 64, y, 2, C["ink"]))
    for r, (lab, lv) in enumerate(sk):
        y = TOP + r * step
        col = C["gold"] if lv >= 9 else C["teal"]
        b.append(text(fit(lab, 124, 2, "skill"), 440, y, 2, C["ink"]))
        for s in range(10):
            sx = 572 + s * 18
            if s < lv:
                d = r * 0.12 + s * 0.07
                b.append(f'<g style="animation:pop .1s steps(1,end) {d:.2f}s both">'
                         f'<rect x="{sx}" y="{y - 1}" width="16" height="16" fill="{C["ink"]}"/>'
                         f'<rect x="{sx + 2}" y="{y + 1}" width="12" height="12" fill="{col}"/>'
                         f'<rect x="{sx + 2}" y="{y + 1}" width="12" height="3" fill="{mix(col, "#ffffff", .5)}"/></g>')
            else:
                b.append(f'<rect x="{sx}" y="{y - 1}" width="16" height="16" fill="{C["well"]}"/>')
        b.append(text(f"LV {lv}", W - 24, y, 2, C["teal_dk"] if lv < 9 else C["red"], "end"))
    b.append(text("! IN PROGRESS", 440 - 24, 16, 1, C["dim"], "end"))
    save("log.svg", svg(W, H, "".join(b)))


# ---------------------------------------------------------------- inventory (flowing chips)
def inventory():
    W, lx, cx0, right, ch, gx, gy = 840, 24, 148, 816, 28, 6, 6
    body, y = [], TOP
    for cat, items in P["inventory"]:
        body.append(text(cat, lx, y + 7, 2, C["teal_dk"]))
        x = cx0
        for name, rar in items:
            w = tw(name, 2) + 24
            if x + w > right:
                x, y = cx0, y + ch + gy
            col = RARITY[rar][1]
            body.append(nrect(x, y, w, ch, C["ink"], 3))
            body.append(f'<rect x="{x + 3}" y="{y + ch - 5}" width="{w - 6}" height="2" fill="{col}"/>')
            body.append(text(name, x + 12, y + 7, 2, "#ffffff"))
            body.append(f'<rect x="{x + w - 8}" y="{y + 5}" width="3" height="3" fill="{col}"{BL if rar == "L" else ""}/>')
            x += w + gx
        y += ch + gy + 4
    lx2 = right
    for key in "CREL":
        lab, col = RARITY[key]
        lx2 -= tw(lab, 1)
        body.append(text(lab, lx2, 28, 1, C["dim"]))
        lx2 -= 12
        body.append(f'<rect x="{lx2}" y="{28}" width="8" height="8" fill="{col}"/>')
        lx2 -= 16
    H = y + 10 + SH
    save("inventory.svg", svg(W, H, card_box(W, H) + header(24, "INVENTORY", "TOOLS I USE") + "".join(body)))


# ---------------------------------------------------------------- buttons
def button(label, col, fname, fg=None):
    """Site button: gold / teal / white fill, navy outline and text, dark bottom shadow."""
    W, H = tw(label, 2) + 28, 34
    fg = fg or C["ink"]
    b = [nrect(0, 4, W, 30, "#000000", 4, ' opacity=".4"'), nrect(0, 0, W, 30, C["ink"], 4),
         nrect(2, 2, W - 4, 26, col, 3),
         f'<rect x="4" y="3" width="{W - 8}" height="2" fill="{mix(col, "#ffffff", .5)}"/>',
         f'<rect x="4" y="24" width="{W - 8}" height="3" fill="{mix(col, "#000000", .18)}"/>',
         bold(label, W / 2, 8, 2, fg, "middle")]
    save(fname, svg(W, H, "".join(b)))


def slug(s):
    out = "".join(c if c.isalnum() else "-" for c in s.lower())
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


# ---------------------------------------------------------------- rig + footer
def rig():
    lines = P["rig"]["lines"]
    W, H = 840, TOP + 30 * len(lines) + 44 + SH
    b = [card_box(W, H), header(24, "C:\\> SYSTEM.INFO", "BIG BOY")]
    b.append(nrect(40, TOP, 128, 128, C["ink"], 4))
    b.append(sprite(ICONS["pc"], {**IPAL, "g": "#cbd5e1"}, 48, TOP + 8, 14))
    x, y = 200, TOP + 4
    for k, v in lines:
        b.append(text(k, x, y, 2, C["teal_dk"]))
        lx = x + tw(k, 2) + 10
        rx = W - 40 - tw(v, 2) - 10
        b.append(f'<path d="{"".join(f"M{i} {y + 10}h2v2h-2z" for i in range(lx, rx, 8))}" fill="{C["line"]}"/>')
        b.append(text(v, W - 40, y, 2, C["ink"], "end"))
        y += 30
    b.append(bold("POWER LEVEL: OVER 9000", x, y + 2, 2, C["red"], attrs=BL))
    save("rig.svg", svg(W, H, "".join(b)))


def footer():
    """The site's ground strip: grass on top, dirt below, credits written in the dirt."""
    W, H = 840, 104
    b, css = [], []
    b.append(nrect(0, 0, W, H, C["ink"], 6))
    b.append(nrect(4, 4, W - 8, H - 8, "#87562a", 4))
    b.append(f'<rect x="4" y="66" width="{W - 8}" height="{H - 70}" fill="#6b4322"/>')
    b.append(f'<rect x="8" y="4" width="{W - 16}" height="12" fill="#5bb23f"/>')
    b.append(f'<rect x="8" y="4" width="{W - 16}" height="4" fill="#8fdc5a"/>')
    drip = "".join(f"M{x} 16h4v4h-4z" for x in range(8, W - 8, 4) if hsh(x, 8) < 0.5)
    spk = "".join(f"M{q(8 + hsh(i, 21) * (W - 24))} {q(24 + hsh(i, 22) * 70)}h4v4h-4z" for i in range(40))
    b.append(f'<path d="{drip}" fill="#3f8f32"/><path d="{spk}" fill="#a8774a"/>')
    t = "THANKS FOR PLAYING"
    b.append(text(t, W / 2 + 3, 28 + 3, 3, C["ink"], "middle"))
    b.append(bold(t, W / 2, 28, 3, C["gold"], "middle"))
    line = "CONTINUE? 9 · INSERT COIN"
    x0 = W / 2 - tw(line, 2) / 2
    b.append(text("CONTINUE?", x0, 58, 2, "#ffffff"))
    css.append("@keyframes cd{0%{opacity:1}10%{opacity:0}100%{opacity:0}}")
    for i, dgt in enumerate("9876543210"):
        b.append(text(dgt, x0 + 10 * 12, 58, 2, C["gold"], attrs=f' style="opacity:0;animation:cd 10s step-end infinite;'
                                                                  f'animation-delay:-{(10 - i) % 10}s"'))
    b.append(text("·", x0 + 12 * 12, 58, 2, "#e6c9a0"))
    b.append(text("INSERT COIN", x0 + 14 * 12, 58, 2, C["gold"], attrs=BL))
    b.append(text("(C) " + P["handle"] + " · MADE WITH PIXELS, WITH AI AS A PARTNER", W / 2, 82, 1, "#f1dcbc", "middle"))
    for sx in (140, 684):
        b.append(sprite(ICONS["star"], IPAL, sx, 26, 2, BL))
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
    b = [header(24, "PLAYER STATS · SINCE " + since, "GITHUB"), header(440, "TOP LANGUAGES", "BY CODE SIZE")]
    y = TOP
    for lab, val in rows:
        b.append(text(lab, 24, y, 2, C["teal_dk"]))
        b.append(text(str(val), 400, y, 2, C["red"] if "STREAK" in lab else C["ink"], "end"))
        y += 22
    b.append(f'<rect x="420" y="{TOP - 4}" width="2" height="{y - TOP}" fill="{C["line"]}"/>')
    lx, ly = 440, TOP
    for i, (nm, (size, col)) in enumerate(top):
        pct = size * 100 / total
        b.append(text(nm[:10], lx, ly, 2, C["ink"]))
        b.append(text(f"{pct:.0f}%", W - 24, ly, 2, C["dim"], "end"))
        segs = max(1, round(pct / 5))
        for s in range(20):
            on = s < segs
            fill = col if on else C["well"]
            st = f' style="animation:pop .1s steps(1,end) {i * 0.1 + s * 0.03:.2f}s both"' if on else ""
            b.append(f'<rect x="{lx + 128 + s * 10}" y="{ly + 1}" width="8" height="12" fill="{fill}"{st}/>')
        ly += 26
    # the contribution calendar is drawn by the snake image right under this panel, so it is not repeated here
    H = max(y, ly) + 8 + SH
    data = svg(W, H, card_box(W, H) + "".join(b))
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
    for title, icon, fn in [("SHIPPED ON STEAM", "star", "d-steam.svg"), ("ARCADE", "joy", "d-arcade.svg"),
                            ("SAVE POINT", "floppy", "d-social.svg"), ("COIN SHOP", "coin", "d-donate.svg")]:
        divider(title, icon, fn)
    for lab, _url, col in P["socials"] + P["donate"] + P["steam"]:
        button(lab, C[col], f"btn-{slug(lab)}.svg")
    button("▶ PLAY DIREWOLF", C["gold"], "btn-play.svg")
    button("▶ WATCH TRAILER", C["red"], "btn-trailer.svg", "#ffffff")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "stats":
        stats_or_keep(sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT, "stats-preview.svg"))
    else:
        build_all()
