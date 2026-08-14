"""
Render "DIVYE" as an extruded 3D wordmark rasterized to ASCII, and emit it as
an SVG that animates on GitHub (SMIL only).

Pipeline: draw the word with a bold TTF -> threshold to a mask -> extrude the
mask along +z into a surface voxel shell -> rotate / project each frame ->
z-buffer splat into a character grid.

Modes:
  rock   -- oscillates +/-11 deg around rest pose, forever (wired into README)
  once   -- one full 360 deg turn, then freezes
  spin   -- continuous 360 deg turntable
  static -- frozen frame, no animation

Font priority (cross-platform):
  1. WORDMARK_FONT env var override
  2. DejaVu Sans Bold (Ubuntu CI: apt install fonts-dejavu-core)
  3. Arial Bold (Windows)
  4. Any TTF found in common system paths

Usage:
    python scripts/make_wordmark_svg.py [--mode rock|once|spin|static]
"""
import argparse
import html
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- geometry / grid -------------------------------------------------------
COLS = int(os.environ.get("WORDMARK_COLS", 50))
ROWS = 35              # character grid rows for rendering frames
ROW_MARGIN = int(os.environ.get("WORDMARK_ROW_MARGIN", 5))
CELL_W = 9.0
CELL_H = 15.5

# Font resolution: try multiple paths for cross-platform support
def _find_font():
    override = os.environ.get("WORDMARK_FONT")
    if override:
        return override, 0
    candidates = [
        # Linux (Ubuntu CI)
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 0),
        ("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf", 0),
        # Windows
        ("C:/Windows/Fonts/arialbd.ttf", 0),
        ("C:/Windows/Fonts/verdanab.ttf", 0),
        ("C:/Windows/Fonts/calibrib.ttf", 0),
        # macOS
        ("/System/Library/Fonts/Futura.ttc", 2),
        ("/Library/Fonts/Arial Bold.ttf", 0),
    ]
    for path, idx in candidates:
        if os.path.exists(path):
            return path, idx
    # last resort: PIL default
    return None, 0

FONT_PATH, FONT_INDEX = _find_font()
TEXT = os.environ.get("WORDMARK_TEXT", "DIVYE")

MASK_H = 300
TRACKING = 0.14
LINE_GAP = 1.20
DEPTH_FRAC = 0.34
TILT_DEG = float(os.environ.get("WORDMARK_TILT", 4.0))
CAM_DIST = 6.0
FOCAL = 4.15
FIT = 0.92

RAMP = " .`:-=+*csS#%@"
LIGHT = np.array([-0.15, -0.45, -1.00])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
AMBIENT = 0.22
FOG = 0.34
FOG_SPAN = 0.55

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"

PAD = 18
TITLEBAR_H = 28


# ---------------------------------------------------------------- voxel shell
def build_shell():
    probe = TEXT.replace("\n", "")
    font_size = MASK_H
    if FONT_PATH:
        for _ in range(40):
            try:
                font = ImageFont.truetype(FONT_PATH, font_size, index=FONT_INDEX)
            except Exception:
                font = ImageFont.load_default()
                break
            l, t, r, b = font.getbbox(probe)
            if b - t <= MASK_H:
                break
            font_size = int(font_size * 0.92)
    else:
        font = ImageFont.load_default()
        t = 0

    try:
        l, t, r, b = font.getbbox(probe)
    except Exception:
        t, b = 0, MASK_H

    h = b - t
    track = int(round(TRACKING * font_size))
    lines_txt = TEXT.split("\n")
    line_h = int(round(h * LINE_GAP))

    def line_w(s):
        try:
            return sum(font.getlength(c) for c in s) + track * (len(s) - 1)
        except Exception:
            return len(s) * font_size * 0.6

    total_w = int(round(max(line_w(s) for s in lines_txt))) + 8
    total_h = line_h * (len(lines_txt) - 1) + h + 8
    img = Image.new("L", (total_w, total_h), 0)
    d = ImageDraw.Draw(img)
    for li, s in enumerate(lines_txt):
        pen = 4.0 + (total_w - 8 - line_w(s)) / 2.0
        base = -t + 4 + li * line_h
        for ch in s:
            d.text((pen, base), ch, font=font, fill=255)
            try:
                pen += font.getlength(ch) + track
            except Exception:
                pen += font_size * 0.6 + track
    mask = np.array(img) > 127
    xs_any = np.nonzero(mask.any(0))[0]
    ys_any = np.nonzero(mask.any(1))[0]
    mask = mask[ys_any[0]:ys_any[-1]+1, xs_any[0]:xs_any[-1]+1]

    H, W = mask.shape
    depth = max(4, int(round(H * DEPTH_FRAC)))
    cy, cx = np.nonzero(mask)

    pts, nrm = [], []
    front = np.stack([cx, cy, np.full_like(cx, -1)], axis=1).astype(float)
    pts.append(front); nrm.append(np.tile([0., 0., -1.], (len(cx), 1)))

    back = np.stack([cx, cy, np.full_like(cx, depth)], axis=1).astype(float)
    pts.append(back); nrm.append(np.tile([0., 0., 1.], (len(cx), 1)))

    for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
        ny, nx = cy+dy, cx+dx
        valid = (ny>=0)&(ny<H)&(nx>=0)&(nx<W)
        edge = valid & ~mask[np.clip(ny,0,H-1), np.clip(nx,0,W-1)]
        ey, ex = cy[edge], cx[edge]
        for z in range(depth):
            wall = np.stack([ex, ey, np.full_like(ex, z)], axis=1).astype(float)
            pts.append(wall)
            nrm.append(np.tile([float(-dx), float(-dy), 0.], (len(ex), 1)))

    pts = np.concatenate(pts)
    nrm = np.concatenate(nrm)

    pts[:, 0] = (pts[:, 0] - W/2) / max(W, H)
    pts[:, 1] = (pts[:, 1] - H/2) / max(W, H)
    pts[:, 2] = (pts[:, 2] - depth/2) / max(W, H)

    return pts, nrm, W/max(W,H), H/max(W,H)


def render_frame(pts, nrm, yaw_deg, tilt_deg=TILT_DEG):
    yaw = math.radians(yaw_deg)
    tilt = math.radians(tilt_deg)
    Ry = np.array([[math.cos(yaw), 0, math.sin(yaw)],
                   [0, 1, 0],
                   [-math.sin(yaw), 0, math.cos(yaw)]])
    Rx = np.array([[1, 0, 0],
                   [0, math.cos(tilt), -math.sin(tilt)],
                   [0, math.sin(tilt), math.cos(tilt)]])
    R = Rx @ Ry
    rp = pts @ R.T
    rn = nrm @ R.T

    cam = np.array([0., 0., -CAM_DIST])
    rel = rp - cam
    d = rel[:, 2]
    d = np.where(d < 0.01, 0.01, d)
    px_ = FOCAL * rel[:, 0] / d
    py_ = FOCAL * rel[:, 1] / d

    fog = np.clip(rp[:, 2] / FOG_SPAN, 0, 1) * FOG
    diff = np.clip(-np.einsum('ij,j->i', rn, LIGHT), 0, 1)
    bright = np.clip(AMBIENT + diff * (1 - AMBIENT) - fog, 0, 1)

    return px_, py_, bright, rp[:, 2]


def project_to_grid(px_, py_, bright, zvals, cols, rows):
    if len(px_) == 0 or rows == 0 or cols == 0:
        return [[" "] * cols for _ in range(rows)]
    x_min, x_max = px_.min(), px_.max()
    y_min, y_max = py_.min(), py_.max()
    span = max(x_max - x_min, y_max - y_min, 1e-6)
    scale = FIT * min(cols, rows) / span

    cx0, cy0 = cols / 2.0, rows / 2.0
    aspect = CELL_H / CELL_W
    gx_f = (px_ - (x_min + x_max) / 2) * scale + cx0
    gy_f = (py_ - (y_min + y_max) / 2) * scale / aspect + cy0
    gx = np.clip(gx_f.astype(int), 0, cols - 1)
    gy = np.clip(gy_f.astype(int), 0, rows - 1)

    zbuf = np.full((rows, cols), np.inf)
    cbuf = np.full((rows, cols), 0.0)
    for i in range(len(gx)):
        r, c = int(gy[i]), int(gx[i])
        if 0 <= r < rows and 0 <= c < cols:
            z = zvals[i]
            if z < zbuf[r, c]:
                zbuf[r, c] = z
                cbuf[r, c] = bright[i]

    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if zbuf[r, c] == np.inf:
                row.append(" ")
            else:
                b = cbuf[r, c]
                idx = int(b * (len(RAMP) - 1) + 0.5)
                idx = max(1, min(len(RAMP) - 1, idx))
                row.append(RAMP[idx])
        grid.append(row)
    return grid


def trim_grid(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    top, bottom = 0, rows
    for i, row in enumerate(grid):
        if any(c != " " for c in row):
            top = i; break
    for i in range(rows-1, -1, -1):
        if any(c != " " for c in grid[i]):
            bottom = i+1; break
    left, right = cols, 0
    for row in grid[top:bottom]:
        for j, c in enumerate(row):
            if c != " ":
                left = min(left, j)
                right = max(right, j+1)
    if left >= right:
        return grid, 0
    return [row[left:right] for row in grid[top:bottom]], left


def make_svg(mode="rock"):
    pts, nrm, W_norm, H_norm = build_shell()

    if mode == "static":
        yaws = [0.0]
    elif mode == "rock":
        N = 24
        half = N // 2
        yaws = [11 * math.sin(math.pi * i / half) for i in range(N)]
    elif mode == "once":
        N = 36
        yaws = [i * 360/N for i in range(N)] + [0.0]
    else:  # spin
        N = 36
        yaws = [i * 360/N for i in range(N)]

    # render all frames to get consistent grid size
    frames_data = []
    all_grids = []
    for yaw in yaws:
        px_, py_, bright, zvals = render_frame(pts, nrm, yaw)
        grid = project_to_grid(px_, py_, bright, zvals, COLS, ROWS)
        frames_data.append((px_, py_, bright, zvals))
        all_grids.append(grid)

    # trim consistently: use union bounding box
    min_top, max_bottom, min_left, max_right = ROWS, 0, COLS, 0
    for grid in all_grids:
        rows = len(grid)
        for i, row in enumerate(grid):
            if any(c != " " for c in row):
                min_top = min(min_top, i)
                break
        for i in range(rows-1, -1, -1):
            if any(c != " " for c in grid[i]):
                max_bottom = max(max_bottom, i+1)
                break
        for row in grid:
            for j, c in enumerate(row):
                if c != " ":
                    min_left = min(min_left, j)
                    max_right = max(max_right, j+1)

    art_rows_count = max_bottom - min_top + ROW_MARGIN * 2
    art_cols_count = max_right - min_left

    ART_W = art_cols_count * CELL_W
    ART_H = art_rows_count * CELL_H
    CANVAS_W = int(ART_W + PAD * 2)
    CANVAS_H = int(TITLEBAR_H + ART_H + PAD)

    WIPE_DUR = 0.8
    FRAME_DUR = 0.06 if mode in ("once", "spin") else 0.12
    total_anim = WIPE_DUR + len(yaws) * FRAME_DUR
    repeat = "indefinite" if mode in ("rock", "spin") else "1"

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{CANVAS_W}" height="{CANVAS_H}" '
                 f'viewBox="0 0 {CANVAS_W} {CANVAS_H}">')

    lines.append("<defs>")
    lines.append(f'<clipPath id="wipe">'
                 f'<rect x="0" y="0" height="{CANVAS_H}" width="0">'
                 f'<animate attributeName="width" values="0;{CANVAS_W}" '
                 f'keyTimes="0;1" calcMode="linear" '
                 f'begin="0s" dur="{WIPE_DUR}s" fill="freeze"/>'
                 f'</rect>'
                 f'</clipPath>')
    lines.append("</defs>")

    lines.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" fill="{BG}"/>')
    lines.append(f'<rect x="1" y="1" width="{CANVAS_W-2}" height="{CANVAS_H-2}" '
                 f'rx="6" fill="{BG2}" stroke="{FRAME}" stroke-width="1"/>')

    TB = TITLEBAR_H
    lines.append(f'<rect x="1" y="1" width="{CANVAS_W-2}" height="{TB}" rx="6" fill="{FRAME}" opacity="0.5"/>')
    lines.append(f'<circle cx="18" cy="{TB//2+1}" r="5" fill="#ff5f57"/>')
    lines.append(f'<circle cx="33" cy="{TB//2+1}" r="5" fill="#febc2e"/>')
    lines.append(f'<circle cx="48" cy="{TB//2+1}" r="5" fill="#28c840"/>')
    lines.append(f'<text x="{CANVAS_W//2}" y="{TB//2+5}" text-anchor="middle" '
                 f'font-family="monospace" font-size="11" fill="{TITLE_TEXT}">divye@github — wordmark</text>')

    ART_Y = TITLEBAR_H + ROW_MARGIN * CELL_H

    lines.append('<g clip-path="url(#wipe)">')
    for fi, grid in enumerate(all_grids):
        t_start = WIPE_DUR + fi * FRAME_DUR
        t_end = t_start + FRAME_DUR
        key_times = []
        key_vals = []
        if fi == 0:
            key_times = ["0", f"{WIPE_DUR/total_anim:.4f}", f"{t_end/total_anim:.4f}", "1"]
            key_vals = ["0", "1", "1", "0"]
        elif fi == len(all_grids) - 1:
            key_times = ["0", f"{t_start/total_anim:.4f}", "1"]
            key_vals = ["0", "1", "1"]
        else:
            key_times = ["0", f"{t_start/total_anim:.4f}", f"{t_end/total_anim:.4f}", "1"]
            key_vals = ["0", "1", "1", "0"]

        opacity_anim = (f'<animate attributeName="opacity" '
                        f'values="{";".join(key_vals)}" '
                        f'keyTimes="{";".join(key_times)}" '
                        f'dur="{total_anim}s" repeatCount="{repeat}"/>')

        lines.append(f'<g opacity="0">{opacity_anim}')
        for r in range(min_top, max_bottom):
            row_chars = grid[r][min_left:max_right]
            row_str = "".join(row_chars)
            y = ART_Y + (r - min_top) * CELL_H
            lines.append(f'<text x="{PAD}" y="{y:.1f}" '
                         f'font-family="monospace" font-size="{int(CELL_H-1)}" '
                         f'fill="{INK}" xml:space="preserve" '
                         f'dominant-baseline="hanging">{html.escape(row_str)}</text>')
        lines.append('</g>')
    lines.append('</g>')
    lines.append('</svg>')

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="rock", choices=["rock","once","spin","static"])
    parser.add_argument("--out", default=os.path.join(HERE, "..", "wordmark.svg"))
    args = parser.parse_args()

    svg = make_svg(args.mode)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"saved {args.out}")
