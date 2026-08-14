"""
Convert a portrait photo into a CLEAN, monochrome ASCII-art SVG that "types"
itself in like a terminal, then holds.

Monochrome is deliberate -- per-character rainbow color is what makes ASCII
portraits look noisy. One fill color + a good density ramp + high contrast reads
as neat and legible.

GitHub renders SVGs embedded via <img> and runs their SMIL animations there (JS
does not run). Each row is revealed with a left-to-right clip wipe plus a small
block cursor riding the wipe edge, staggered top -> bottom.

Usage:
    python scripts/make_ascii_svg.py [input.png] [output.svg]
"""
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "divye-ascii.svg")

COLS = 100
ROWS = 53
CELL_W = 8
CELL_H = 15
RAMP = " .`:-=+*cs#%@"   # bright(sparse) -> dark(dense)

CONTRAST = 1.05
BRIGHTNESS = 1.0
GAMMA = 1.18
SHARPEN = False
WHITE_FLOOR = 0.80

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"

ROW_DUR = 0.11
STAGGER = 0.11

# ---- 1. sample the image ---------------------------------------------------
im = Image.open(SRC).convert("L")
if SHARPEN:
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))
im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
im = ImageEnhance.Contrast(im).enhance(CONTRAST)
im = im.resize((COLS, ROWS), Image.LANCZOS)
px = im.load()

STATIC = bool(os.environ.get("STATIC"))

rows_txt = []
for y in range(ROWS):
    chars = []
    for x in range(COLS):
        lum = px[x, y] / 255.0
        lum = pow(lum, GAMMA)
        if lum >= WHITE_FLOOR:
            chars.append(" ")
            continue
        idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
        idx = max(0, min(len(RAMP) - 1, idx))
        chars.append(RAMP[idx])
    rows_txt.append("".join(chars))

# ---- 2. build SVG ----------------------------------------------------------
def fmt_time(t):
    return f"{t:.3f}s"

lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'xmlns:xlink="http://www.w3.org/1999/xlink" '
             f'width="{CANVAS_W}" height="{CANVAS_H}" '
             f'viewBox="0 0 {CANVAS_W} {CANVAS_H}">')

# ---- defs ------------------------------------------------------------------
lines.append("<defs>")
for r in range(ROWS):
    cw = ART_W
    t_start = r * STAGGER
    t_end = t_start + ROW_DUR
    if STATIC:
        lines.append(f'<clipPath id="cr{r}"><rect x="0" y="0" width="{cw}" height="{CELL_H}"/></clipPath>')
    else:
        lines.append(
            f'<clipPath id="cr{r}">'
            f'<rect x="0" y="0" height="{CELL_H}" width="0">'
            f'<animate attributeName="width" values="0;{cw}" '
            f'keyTimes="0;1" calcMode="linear" '
            f'begin="{fmt_time(t_start)}" dur="{fmt_time(ROW_DUR)}" '
            f'fill="freeze"/>'
            f'</rect>'
            f'</clipPath>'
        )
lines.append("</defs>")

# background
lines.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" fill="{BG}"/>')
lines.append(f'<rect x="1" y="1" width="{CANVAS_W-2}" height="{CANVAS_H-2}" rx="6" fill="{BG2}" stroke="{FRAME}" stroke-width="1"/>')

# title bar
TB = TITLEBAR_H
lines.append(f'<rect x="1" y="1" width="{CANVAS_W-2}" height="{TB}" rx="6" fill="{FRAME}" opacity="0.5"/>')
lines.append(f'<circle cx="18" cy="{TB//2+1}" r="5" fill="#ff5f57"/>')
lines.append(f'<circle cx="33" cy="{TB//2+1}" r="5" fill="#febc2e"/>')
lines.append(f'<circle cx="48" cy="{TB//2+1}" r="5" fill="#28c840"/>')
lines.append(f'<text x="{CANVAS_W//2}" y="{TB//2+5}" text-anchor="middle" '
             f'font-family="monospace" font-size="11" fill="{TITLE_TEXT}">divye@github — ascii-portrait</text>')

# art rows
ART_Y = TITLEBAR_H + PAD // 2
for r, row in enumerate(rows_txt):
    y = ART_Y + r * CELL_H
    lines.append(f'<g clip-path="url(#cr{r})" transform="translate({PAD},{y})">')
    lines.append(f'<text font-family="monospace" font-size="{CELL_H-2}px" '
                 f'fill="{INK}" xml:space="preserve" '
                 f'dominant-baseline="hanging">{html.escape(row)}</text>')
    lines.append('</g>')

# status bar
SB_Y = TITLEBAR_H + ART_H + PAD // 2 + CELL_H // 2
lines.append(f'<text x="{PAD}" y="{SB_Y + ART_H//ROWS//2 + 6}" '
             f'font-family="monospace" font-size="10" fill="{TITLE_TEXT}">'
             f'divye@github:~ $ whoami  →  Computer Vision Engineer</text>')

lines.append("</svg>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"saved {OUT}  ({COLS}×{ROWS} chars)")
