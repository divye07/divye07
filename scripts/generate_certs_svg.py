#!/usr/bin/env python3
"""
Generate an aesthetically pleasing, dark-terminal styled 'Certifications' SVG card.
Matches the GitHub dark theme (#0d1117 / #161b22) and cyan (#22d3ee) / green (#39d353) accents.

Usage:
    python scripts/generate_certs_svg.py [output.svg]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "certs.svg")

W = 880
H = 340

CERTS = [
    {
        "title": "Professional ML Engineer",
        "spec": "GCP MLOps & Architecture",
        "issuer": "Google Cloud",
        "accent": "#4285f4",
        "icon": '<path fill="#4285F4" d="M12 4C7.58 4 4 7.58 4 12c0 2.97 1.62 5.56 4.02 6.94l1.24-2.15C7.9 15.82 7 14.02 7 12c0-2.76 2.24-5 5-5s5 2.24 5 5c0 2.02-.9 3.82-2.26 4.79l1.24 2.15C18.38 17.56 20 14.97 20 12c0-4.42-3.58-8-8-8z"/>',
        "badge": "GCP Certified"
    },
    {
        "title": "TensorFlow Developer",
        "spec": "Deep Learning & Vision Models",
        "issuer": "DeepLearning.AI",
        "accent": "#ff6f00",
        "icon": '<path fill="#FF6F00" d="M12 2L4 6.5v9L12 20l8-4.5v-9L12 2zm0 2.3l5.5 3.1-2.5 1.4-3-1.7v7.8l-2 1.1V8.7l-3 1.7-2.5-1.4L12 4.3z"/>',
        "badge": "DeepLearning.AI"
    },
    {
        "title": "Deep Learning Specialty",
        "spec": "NVIDIA DLI Computing",
        "issuer": "NVIDIA DLI",
        "accent": "#76b900",
        "icon": '<path fill="#76B900" d="M12 5c-3.87 0-7 3.13-7 7s3.13 7 7 7 7-3.13 7-7-3.13-7-7-7zm0 11.5c-2.48 0-4.5-2.02-4.5-4.5s2.02-4.5 4.5-4.5 4.5 2.02 4.5 4.5-2.02 4.5-4.5 4.5z"/>',
        "badge": "NVIDIA Certified"
    },
    {
        "title": "GitHub Foundations",
        "spec": "Core Git, CI & Collaboration",
        "issuer": "GitHub Certified",
        "accent": "#22d3ee",
        "icon": '<path fill="#22D3EE" d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/>',
        "badge": "Verified"
    },
    {
        "title": "GitHub Actions Certified",
        "spec": "Workflow Automation & CI/CD",
        "issuer": "GitHub Certified",
        "accent": "#39d353",
        "icon": '<path fill="#39D353" d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm1 14.5h-2v-2h2zm0-4h-2V7h2z"/>',
        "badge": "Verified"
    },
    {
        "title": "Advanced Security",
        "spec": "Code Security & Vuln Analysis",
        "issuer": "GitHub Certified",
        "accent": "#bc8cff",
        "icon": '<path fill="#BC8CFF" d="M12 2L4 5v6.09c0 5.05 3.41 9.76 8 10.91 4.59-1.15 8-5.86 8-10.91V5l-8-3zm0 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>',
        "badge": "Verified"
    }
]

cards_svg = []
col_w = 264
row_h = 114
start_x = 24
start_y = 68
gap_x = 16
gap_y = 14

for idx, c in enumerate(CERTS):
    col = idx % 3
    row = idx // 3
    x = start_x + col * (col_w + gap_x)
    y = start_y + row * (row_h + gap_y)

    card = f"""
    <!-- Card {idx+1}: {c['title']} -->
    <g transform="translate({x}, {y})">
      <!-- Card background -->
      <rect width="{col_w}" height="{row_h}" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
      <rect width="{col_w}" height="{row_h}" rx="6" fill="{c['accent']}" fill-opacity="0.04"/>
      
      <!-- Top Accent Line -->
      <path d="M 6 1 L {col_w-6} 1" stroke="{c['accent']}" stroke-width="2" stroke-opacity="0.8" stroke-linecap="round"/>

      <!-- Icon Container -->
      <rect x="14" y="14" width="28" height="28" rx="4" fill="#161b22" stroke="{c['accent']}" stroke-opacity="0.3" stroke-width="1"/>
      <g transform="translate(16, 16)">
        {c['icon']}
      </g>

      <!-- Badge status pill -->
      <rect x="{col_w - 92}" y="14" width="78" height="18" rx="9" fill="#161b22" stroke="{c['accent']}" stroke-opacity="0.4" stroke-width="1"/>
      <text x="{col_w - 53}" y="26" text-anchor="middle" font-family="'Fira Code', monospace" font-size="9" font-weight="bold" fill="{c['accent']}">{c['badge']}</text>

      <!-- Text -->
      <text x="14" y="60" font-family="'Fira Code', monospace" font-size="11.5" font-weight="bold" fill="#e6edf3">{c['title']}</text>
      <text x="14" y="78" font-family="'Fira Code', monospace" font-size="9.5" fill="#7d8590">{c['spec']}</text>
      <text x="14" y="96" font-family="'Fira Code', monospace" font-size="9.5" font-weight="bold" fill="{c['accent']}">{c['issuer']}</text>
    </g>"""
    cards_svg.append(card)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <linearGradient id="certGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1f6feb" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#39d353" stop-opacity="0.04"/>
    </linearGradient>
    <linearGradient id="certBorder" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#4285f4" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#22d3ee" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#39d353" stop-opacity="0.8"/>
    </linearGradient>
  </defs>

  <style>
    .title {{ font: 12px "Fira Code", monospace; fill: #7d8590; }}
  </style>

  <!-- Container -->
  <rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="9" fill="#161b22" stroke="#30363d" stroke-width="1.2"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="9" fill="url(#certGrad)"/>

  <!-- Top highlight border bar -->
  <path d="M 10 1 L {W-10} 1" stroke="url(#certBorder)" stroke-width="2" stroke-linecap="round"/>

  <!-- Title bar -->
  <rect x="1" y="1" width="{W-2}" height="34" rx="9" fill="#21262d" opacity="0.6"/>
  <circle cx="20" cy="18" r="5" fill="#ff5f57"/>
  <circle cx="36" cy="18" r="5" fill="#febc2e"/>
  <circle cx="52" cy="18" r="5" fill="#28c840"/>
  <text x="{W//2}" y="22" text-anchor="middle" class="title">divye@github — gcloud / gh verify --credentials</text>

  <!-- Cards -->
  {''.join(cards_svg)}

  <!-- Footer status bar -->
  <text x="24" y="324" font-family="'Fira Code', monospace" font-size="10" fill="#545d68">
    status: 6/6 verified credentials loaded &amp; active
  </text>
  <text x="{W - 24}" y="324" text-anchor="end" font-family="'Fira Code', monospace" font-size="10" fill="#22d3ee">
    Google Cloud • GitHub • DeepLearning.AI • NVIDIA DLI
  </text>
</svg>"""

os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"saved {OUT}")
