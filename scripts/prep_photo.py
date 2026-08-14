"""
Prepare a portrait photo for clean ASCII conversion:
  1. (optional) remove the background with rembg so the subject is isolated
  2. boost LOCAL contrast (CLAHE) so a flatly-lit face gains highlights and
     shadows -- this is what turns a dark blob into a recognizable face
  3. composite the subject onto pure white so the background reads as blank
     (white -> spaces in the ascii ramp)

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
Run once whenever the source photo changes; the ascii SVG itself is static.

    python scripts/prep_photo.py <input.jpg> [output.png]

rembg is optional -- if not installed, falls back to CLAHE-only (still great).
Install rembg for best results:  pip install rembg
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

# 1. try background removal with rembg (optional)
try:
    from rembg import remove as rembg_remove
    print("rembg available — removing background...")
    cut = rembg_remove(Image.open(INP).convert("RGBA"))
    white = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    white.paste(cut, mask=cut.split()[3])
    rgb = white.convert("RGB")
    print("background removed.")
except ImportError:
    print("rembg not installed — skipping background removal (install with: pip install rembg)")
    rgb = Image.open(INP).convert("RGB")

# 2. CLAHE on L channel for local contrast boost
lab = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2LAB)
clahe = cv2.createCLAHE(clipLimit=2.8, tileGridSize=(8, 8))
lab[:, :, 0] = clahe.apply(lab[:, :, 0])
result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

# 3. save as grayscale
Image.fromarray(result).convert("L").save(OUT)
print(f"saved {OUT}")
