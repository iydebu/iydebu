#!/usr/bin/env python3
"""Minimal pixel GitHub profile images for iydebu/iydebu (stdlib only).

    python tools/build_pixel.py             header-dark.svg + header-light.svg into Img/
    python tools/build_pixel.py stats DIR   live stats-dark.svg + stats-light.svg (GitHub GraphQL)

Colours are GitHub's own (Primer) plus one teal accent; backgrounds are transparent and
README.md swaps dark/light files with <picture>. Text lives in tools/profile.json.
GitHub strips web fonts from README images, so letters are a 5x7 bitmap font drawn as SVG paths.
"""
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, "tools", "profile.json"), encoding="utf-8"))

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


# GitHub's own palette (Primer): each image is built twice and README swaps them with <picture>
THEMES = {
    "dark": dict(fg="#e6edf3", muted="#7d8590", border="#30363d", well="#21262d"),
    "light": dict(fg="#1f2328", muted="#59636e", border="#d1d9e0", well="#eff2f5"),
}
ACCENT = "#14b8a6"  # iydebu teal, the one accent colour


def n(v):
    v = round(v, 2)
    return str(int(v)) if v == int(v) else str(v)


def tw(s, sc):
    return len(s) * 6 * sc - sc


def runs(rows, x, y, sc):
    d = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] == "#":
                c0 = c
                while c < len(row) and row[c] == "#":
                    c += 1
                w = (c - c0) * sc
                d.append(f"M{n(x + c0 * sc)} {n(y + r * sc)}h{n(w)}v{n(sc)}h{n(-w)}z")
            else:
                c += 1
    return "".join(d)


def text(s, x, y, sc, fill, anchor="start", attrs=""):
    s = s.upper()
    if anchor == "end":
        x -= tw(s, sc)
    x = round(x)
    for ch in s:
        if ch not in FONT:
            print(f"  ! no glyph for {ch!r}, using '?'")
    d = "".join(runs(FONT.get(ch, FONT["?"]), x + i * 6 * sc, y, sc) for i, ch in enumerate(s))
    return f'<path d="{d}" fill="{fill}"{attrs}/>'


def svg(w, h, body, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'shape-rendering="crispEdges"><style>{css}</style>{body}</svg>')


def write(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    print(f"  {path:40s} {len(data) / 1024:5.1f} KB")


# ---------------------------------------------------------------- header
def header(t):
    """Pixel wordmark + one line. Transparent, so it sits on GitHub's own page colour."""
    logo, sc = P["logo"], 8
    sub = f'{P["name"]} · {P["role"]}'
    W = max(tw(logo, sc) + 16 + 40, tw(sub, 2)) + 4
    H = 8 * sc + 40
    css = "@keyframes bl{0%{opacity:1}50%{opacity:0}}.bl{animation:bl 1.1s step-end infinite}"
    body = (text(logo, 0, 0, sc, t["fg"])
            + f'<rect class="bl" x="{tw(logo, sc) + 16}" y="{6 * sc}" width="40" height="{sc}" fill="{ACCENT}"/>'
            + text(sub, 0, 8 * sc + 18, 2, t["muted"]))
    return svg(W, H, body, css)


# ---------------------------------------------------------------- live stats
Q = """query($login:String!){user(login:$login){createdAt
 repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100,orderBy:{field:PUSHED_AT,direction:DESC}){
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
                                 headers={"Authorization": "bearer " + token(), "User-Agent": "iydebu-profile"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]["user"]


def summarize(u):
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
            langs.setdefault(e["node"]["name"], [0, e["node"]["color"] or "#8b949e"])[0] += e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:5]
    total = sum(v[0] for v in langs.values()) or 1
    rows = [("CONTRIBUTIONS 1Y", cc["contributionCalendar"]["totalContributions"]),
            ("COMMITS 1Y", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
            ("PUBLIC REPOS", u["repositories"]["totalCount"]),
            ("STARS", sum(r["stargazerCount"] for r in u["repositories"]["nodes"])),
            ("CURRENT STREAK", f"{cur} D"),
            ("BEST STREAK 1Y", f"{best} D")]
    return rows, [(nm, size * 100 / total, col) for nm, (size, col) in top], u["createdAt"][:4]


def stats_svg(t, rows, top, since):
    W, top_y, step = 840, 56, 24
    H = top_y + max(len(rows), len(top)) * step + 16
    b = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="none" stroke="{t["border"]}" '
         f'shape-rendering="geometricPrecision"/>',
         text("GITHUB STATS", 24, 22, 2, t["fg"]), text("SINCE " + since, 396, 22, 2, t["muted"], "end"),
         text("TOP LANGUAGES", 444, 22, 2, t["fg"]),
         f'<rect x="420" y="20" width="1" height="{H - 40}" fill="{t["border"]}"/>']
    for i, (lab, val) in enumerate(rows):
        y = top_y + i * step
        b.append(text(lab, 24, y, 2, t["muted"]))
        b.append(text(str(val), 396, y, 2, ACCENT if "STREAK" in lab else t["fg"], "end"))
    for i, (nm, pct, col) in enumerate(top):
        y = top_y + i * step
        b.append(text(nm[:11], 444, y, 2, t["fg"]))
        bx, bw = 592, 176
        b.append(f'<rect x="{bx}" y="{y + 3}" width="{bw}" height="8" fill="{t["well"]}"/>')
        b.append(f'<rect x="{bx}" y="{y + 3}" width="{max(2, round(bw * pct / 100))}" height="8" fill="{col}"/>')
        b.append(text(f"{pct:.0f}%", W - 24, y, 2, t["muted"], "end"))
    return svg(W, H, "".join(b))


def stats(out_dir):
    rows, top, since = summarize(fetch())
    for name, t in THEMES.items():
        write(os.path.join(out_dir, f"stats-{name}.svg"), stats_svg(t, rows, top, since))
    print("  ", rows, [(k, round(p)) for k, p, _ in top])


def stats_or_keep(out_dir):
    """Actions fallback: if the API call fails, re-publish yesterday's files so the images never 404."""
    try:
        stats(out_dir)
    except Exception as e:  # noqa: BLE001
        print("  stats fetch failed:", e)
        os.makedirs(out_dir, exist_ok=True)
        for name in THEMES:
            url = f"https://raw.githubusercontent.com/{P['login']}/{P['login']}/output/stats-{name}.svg"
            try:
                urllib.request.urlretrieve(url, os.path.join(out_dir, f"stats-{name}.svg"))
                print("  kept previous", url)
            except Exception as e2:  # noqa: BLE001 - first run has nothing to keep
                print("  no previous file either:", e2)
                sys.exit(1)


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "stats":
        stats_or_keep(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "Img", "preview"))
    else:
        print("building", os.path.join(ROOT, "Img"))
        for name, t in THEMES.items():
            write(os.path.join(ROOT, "Img", f"header-{name}.svg"), header(t))
