#!/usr/bin/env python3
"""Generate an animated GitHub-streak SVG (squares light up one by one).
Works standalone; designed to run in a GitHub Action daily to stay live.
Usage: python generate_streak_svg.py [username] [output.svg]
"""
import sys
import json
import os
import datetime
import urllib.request

USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_PROFILE_USER", "divye07")
OUT  = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "streak.svg")


def get_data(user):
    url = f"https://github-contributions-api.jogruber.de/v4/{user}?y=last"
    try:
        with urllib.request.urlopen(url, timeout=25) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contrib.json")
        if os.path.exists(here):
            print("API failed (%s); using local contrib.json" % e)
            return json.load(open(here))
        raise


data     = get_data(USER)
contribs = data["contributions"]
total    = data["total"].get("lastYear", sum(c["count"] for c in contribs))

# ---- layout ----
CELL, GAP, RAD, LEFT, TOP = 13, 3, 2.5, 34, 24
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
FLASH  = "#b4ffaa"
GRAY   = "#7d8590"
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

n  = len(contribs)
NW = (n + 6) // 7
W  = LEFT + NW * (CELL + GAP) + 6
H  = TOP + 7 * (CELL + GAP) + 22

# timing (seconds)
REVEAL, DUR = 3.6, 0.55
maxorder = (NW - 1) + 6 * 0.55

rects, labels = [], []
sd     = datetime.date.fromisoformat(contribs[0]["date"])
last_m = None
for wk in range(NW):
    d = sd + datetime.timedelta(days=wk * 7)
    if d.month != last_m:
        last_m = d.month
        labels.append(f'<text class="lbl" x="{LEFT + wk*(CELL+GAP)}" y="{TOP-8}">{MONTHS[d.month-1]}</text>')

for name, r in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
    labels.append(f'<text class="lbl" x="2" y="{TOP + r*(CELL+GAP) + CELL - 2}">{name}</text>')

today = datetime.date.today()
for i, c in enumerate(contribs):
    wk  = i // 7
    day = i % 7
    lv  = min(4, c["count"] // 4) if c["count"] else 0
    x   = LEFT + wk * (CELL + GAP)
    y   = TOP  + day * (CELL + GAP)
    order = wk + day * 0.55
    delay = REVEAL * order / max(maxorder, 1)
    anim  = (f'<animate attributeName="fill" '
             f'values="{FLASH};{COLORS[lv]}" '
             f'dur="{DUR}s" begin="{delay:.3f}s" fill="freeze"/>')
    date_str = c["date"]
    title = f'{c["count"]} contribution{"s" if c["count"] != 1 else ""} on {date_str}'
    rects.append(
        f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RAD}" '
        f'fill="{COLORS[0]}">'
        f'{anim}'
        f'<title>{title}</title>'
        f'</rect>'
    )

# footer stats
cur_streak, longest_streak = 0, 0
run = 0
for c in reversed(contribs):
    if c["count"] > 0:
        run += 1
    else:
        if cur_streak == 0:
            cur_streak = 0  # already broke
        break
    if cur_streak == 0:
        cur_streak = run
run2 = 0
for c in contribs:
    if c["count"] > 0:
        run2 += 1
        longest_streak = max(longest_streak, run2)
    else:
        run2 = 0

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}"
     viewBox="0 0 {W:.0f} {H:.0f}" style="background:#0d1117;border-radius:6px">
<style>
  .lbl{{font:10px monospace;fill:{GRAY}}}
  .stat-v{{font:bold 14px monospace;fill:#e6edf3}}
  .stat-l{{font:9px monospace;fill:{GRAY}}}
</style>
{"".join(labels)}
{"".join(rects)}
<!-- footer -->
<text class="stat-l" x="{LEFT}" y="{H-8}">Total {total:,} contributions in the last year</text>
</svg>"""

os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"saved {OUT}  ({n} days, total={total})")
