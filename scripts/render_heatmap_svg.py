#!/usr/bin/env python3
"""
Render data/contributions.json (produced by fetch_contributions.py) as a proper
GitHub-style contribution heatmap SVG: a grid of rounded, colored boxes in the
classic 53-week x 7-day calendar, revealed with a diagonal cell-by-cell
animation (plays on load then freezes -- no looping), a Less->More legend,
and a real stats footer.

Run by .github/workflows/update-profile-art.yml after fetch_contributions.py.

Usage:
    python scripts/render_heatmap_svg.py [input.json] [output.svg]
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(__file__)
IN_PATH  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "contrib-heatmap.svg")

# GitHub green ramp: empty -> level 5 neon
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP  = 3
STEP = CELL + GAP
PAD  = 22
LEFT_LABEL_W = 30
TOP_LABEL_H  = 20
TITLEBAR_H   = 30

BG     = "#0a0e14"
BG2    = "#0d1420"
FRAME  = "#1f6feb"
MUTED  = "#7d8590"
TEXT   = "#e6edf3"
ACCENT = "#22d3ee"
GREEN  = "#39d353"
GOLD   = "#f2cc60"

# diagonal cell-by-cell reveal timing
COL_T  = 0.018
ROW_T  = 0.045
CELL_DUR = 0.42


def level_for(count):
    if count == 0: return 0
    if count <= 5:  return 1
    if count <= 15: return 2
    if count <= 30: return 3
    if count <= 50: return 4
    return 5


def build_grid(days):
    first = datetime.date.fromisoformat(days[0]["date"])
    lead_pad = (first.weekday() + 1) % 7  # sunday=0
    grid = []
    col = [None] * lead_pad
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        while len(col) < weekday:
            col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"])))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        while len(col) < 7:
            col.append(None)
        grid.append(col)
    return grid


def render(data):
    days   = data["days"]
    grid   = build_grid(days)
    n_cols = len(grid)
    art_w  = n_cols * STEP
    art_h  = 7 * STEP

    # month labels
    month_labels = []
    seen_months  = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key  = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                month_labels.append((ci, date.strftime("%b")))
            break

    canvas_w = PAD + LEFT_LABEL_W + art_w + PAD
    stats_h  = 88
    canvas_h = TITLEBAR_H + TOP_LABEL_H + art_h + stats_h + PAD

    # CSS keyframes for cell reveal
    css = f"""
@keyframes cell {{
  0%   {{ opacity: 0; transform: translateY(-6px); }}
  60%  {{ opacity: 1; transform: translateY(1px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}"""

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'width="{canvas_w}" height="{canvas_h}" '
               f'viewBox="0 0 {canvas_w} {canvas_h}">')
    out.append(f'<style>{css}</style>')

    # background
    out.append(f'<rect width="{canvas_w}" height="{canvas_h}" fill="{BG}"/>')
    out.append(f'<rect x="1" y="1" width="{canvas_w-2}" height="{canvas_h-2}" '
               f'rx="8" fill="{BG2}" stroke="{FRAME}" stroke-width="1.5"/>')

    # title bar
    TB = TITLEBAR_H
    out.append(f'<rect x="1" y="1" width="{canvas_w-2}" height="{TB}" rx="8" fill="{FRAME}" opacity="0.25"/>')
    out.append(f'<circle cx="18" cy="{TB//2+1}" r="5" fill="#ff5f57"/>')
    out.append(f'<circle cx="33" cy="{TB//2+1}" r="5" fill="#febc2e"/>')
    out.append(f'<circle cx="48" cy="{TB//2+1}" r="5" fill="#28c840"/>')
    username = data.get("username", "divye07")
    out.append(f'<text x="{canvas_w//2}" y="{TB//2+5}" text-anchor="middle" '
               f'font-family="monospace" font-size="11" fill="{MUTED}">@{username} — contribution graph</text>')

    ART_X = PAD + LEFT_LABEL_W
    ART_Y = TITLEBAR_H + TOP_LABEL_H

    # weekday labels
    for ri, label in enumerate(["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]):
        if ri % 2 == 1:
            y = ART_Y + ri * STEP + CELL // 2 + 4
            out.append(f'<text x="{PAD + LEFT_LABEL_W - 4}" y="{y}" '
                       f'text-anchor="end" font-family="monospace" font-size="9" fill="{MUTED}">{label}</text>')

    # month labels
    for ci, label in month_labels:
        x = ART_X + ci * STEP
        out.append(f'<text x="{x}" y="{ART_Y - 6}" '
                   f'font-family="monospace" font-size="9" fill="{MUTED}">{label}</text>')

    # cells
    for ci, column in enumerate(grid):
        for ri, cell in enumerate(column):
            x = ART_X + ci * STEP
            y = ART_Y + ri * STEP
            if cell is None:
                out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                           f'rx="2" fill="{PALETTE[0]}" opacity="0.3"/>')
                continue
            date_str, count, level = cell
            color = PALETTE[level]
            delay = ci * COL_T + ri * ROW_T
            anim  = f'animation: cell {CELL_DUR}s ease-out {delay:.3f}s both;'
            title = f'{count} contribution{"s" if count != 1 else ""} on {date_str}'
            out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                       f'rx="2" fill="{color}" style="{anim}">'
                       f'<title>{title}</title></rect>')

    # stats footer
    SF_Y = TITLEBAR_H + TOP_LABEL_H + art_h + 14
    total         = data.get("total", 0)
    best_day      = data.get("best_day", "—")
    best_count    = data.get("best_count", 0)
    cur_streak    = data.get("current_streak", 0)
    longest       = data.get("longest_streak", 0)
    fetched_at    = data.get("fetched_at", "")[:10]

    col_w = canvas_w // 4
    stats = [
        ("Total", f"{total:,}", GREEN),
        ("Best Day", f"{best_count} ({best_day})", GOLD),
        (f"Current Streak", f"{cur_streak} days", ACCENT),
        ("Longest Streak", f"{longest} days", ACCENT),
    ]
    for i, (label, value, color) in enumerate(stats):
        sx = col_w * i + col_w // 2
        out.append(f'<text x="{sx}" y="{SF_Y + 10}" text-anchor="middle" '
                   f'font-family="monospace" font-size="9" fill="{MUTED}">{label}</text>')
        out.append(f'<text x="{sx}" y="{SF_Y + 26}" text-anchor="middle" '
                   f'font-family="monospace" font-size="12" fill="{color}" font-weight="bold">{value}</text>')

    # legend
    LG_Y = SF_Y + 50
    out.append(f'<text x="{ART_X}" y="{LG_Y}" font-family="monospace" font-size="9" fill="{MUTED}">Less</text>')
    for li, col in enumerate(PALETTE):
        lx = ART_X + 32 + li * (CELL + 2)
        out.append(f'<rect x="{lx}" y="{LG_Y - 9}" width="{CELL}" height="{CELL}" rx="2" fill="{col}"/>')
    out.append(f'<text x="{ART_X + 32 + len(PALETTE)*(CELL+2) + 4}" y="{LG_Y}" '
               f'font-family="monospace" font-size="9" fill="{MUTED}">More</text>')

    out.append(f'<text x="{canvas_w - PAD}" y="{LG_Y}" text-anchor="end" '
               f'font-family="monospace" font-size="8" fill="{MUTED}" opacity="0.5">updated {fetched_at}</text>')

    out.append('</svg>')
    return "\n".join(out)


def main():
    if not os.path.exists(IN_PATH):
        print(f"input not found: {IN_PATH}", file=sys.stderr)
        print("run fetch_contributions.py first", file=sys.stderr)
        sys.exit(1)

    with open(IN_PATH) as f:
        data = json.load(f)

    svg = render(data)
    os.makedirs(os.path.dirname(os.path.abspath(OUT_PATH)), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    main()
