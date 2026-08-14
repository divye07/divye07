#!/usr/bin/env python3
"""
Generate an aesthetically pleasing, dark-terminal styled 'About Me' SVG card.
Matches the GitHub dark theme (#0d1117 / #161b22) and cyan (#22d3ee) / green (#39d353) accents.

Usage:
    python scripts/generate_about_svg.py [output.svg]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "about-me.svg")

W = 880
H = 340

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <linearGradient id="aboutGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1f6feb" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#22d3ee" stop-opacity="0.05"/>
    </linearGradient>
    <linearGradient id="borderGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1f6feb" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#22d3ee" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#39d353" stop-opacity="0.8"/>
    </linearGradient>
    <linearGradient id="badgeGlow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#1f6feb" stop-opacity="0.1"/>
    </linearGradient>
  </defs>

  <style>
    .title {{ font: 12px "Fira Code", monospace; fill: #7d8590; }}
    .prompt-user {{ font: bold 13px "Fira Code", monospace; fill: #39d353; }}
    .prompt-host {{ font: bold 13px "Fira Code", monospace; fill: #7d8590; }}
    .prompt-cmd {{ font: 13px "Fira Code", monospace; fill: #e6edf3; }}
    .key {{ font: bold 12px "Fira Code", monospace; fill: #22d3ee; }}
    .val {{ font: 12px "Fira Code", monospace; fill: #c9d1d9; }}
    .val-highlight {{ font: bold 12px "Fira Code", monospace; fill: #ffffff; }}
    .val-accent {{ font: 12px "Fira Code", monospace; fill: #39d353; }}
    .val-yellow {{ font: 12px "Fira Code", monospace; fill: #f2cc60; }}
    .val-purple {{ font: 12px "Fira Code", monospace; fill: #bc8cff; }}
    .comment {{ font: 11px "Fira Code", monospace; fill: #545d68; font-style: italic; }}
    .tag {{ font: 10px "Fira Code", monospace; fill: #22d3ee; }}
    .blink {{
      animation: blink 1s step-end infinite;
    }}
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0; }}
    }}
  </style>

  <!-- Container -->
  <rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="9" fill="#161b22" stroke="#30363d" stroke-width="1.2"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="9" fill="url(#aboutGrad)"/>

  <!-- Top highlight border bar -->
  <path d="M 10 1 L {W-10} 1" stroke="url(#borderGlow)" stroke-width="2" stroke-linecap="round"/>

  <!-- Title bar -->
  <rect x="1" y="1" width="{W-2}" height="34" rx="9" fill="#21262d" opacity="0.6"/>
  <circle cx="20" cy="18" r="5" fill="#ff5f57"/>
  <circle cx="36" cy="18" r="5" fill="#febc2e"/>
  <circle cx="52" cy="18" r="5" fill="#28c840"/>
  <text x="{W//2}" y="22" text-anchor="middle" class="title">divye@github — bash — about_me.json</text>

  <!-- Terminal Command -->
  <text x="24" y="60">
    <tspan class="prompt-user">divye</tspan><tspan class="prompt-host">@</tspan><tspan class="prompt-user">workstation</tspan><tspan class="prompt-host">:~$</tspan> <tspan class="prompt-cmd">cat &lt;&lt; 'EOF' &gt; profile.json</tspan>
  </text>

  <!-- Left Column (Structured Info) -->
  <!-- Box 1: Core Profile -->
  <rect x="24" y="78" width="400" height="236" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
  
  <text x="40" y="104" class="key">role<tspan class="val">:</tspan></text>
  <text x="145" y="104" class="val-highlight">"ML Research Engineer"</text>

  <text x="40" y="132" class="key">company<tspan class="val">:</tspan></text>
  <text x="145" y="132" class="val-accent">"@ HiFy Club"</text>

  <text x="40" y="160" class="key">focus<tspan class="val">:</tspan></text>
  <text x="145" y="160" class="val">["Computer Vision", "MLOps"]</text>

  <text x="40" y="188" class="key">systems<tspan class="val">:</tspan></text>
  <text x="145" y="188" class="val">"Keypoints • Seg • Detection"</text>

  <text x="40" y="216" class="key">cloud<tspan class="val">:</tspan></text>
  <text x="145" y="216" class="val-purple">"GCP Cloud Run (Scale-to-0 GPU)"</text>

  <text x="40" y="244" class="key">passions<tspan class="val">:</tspan></text>
  <text x="145" y="244" class="val-yellow">"F1 Freak 🏎️ &amp; Go-Karting 🏁"</text>

  <text x="40" y="272" class="key">contact<tspan class="val">:</tspan></text>
  <text x="145" y="272" class="val">"divye.prakash07@gmail.com"</text>

  <text x="40" y="298" class="comment">// Open to deep learning &amp; deployment collabs</text>

  <!-- Right Column (Engineering Highlights / Specs) -->
  <rect x="440" y="78" width="416" height="236" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>

  <!-- Subheader -->
  <text x="456" y="104" class="prompt-user">⚡ Production Engineering Stack</text>

  <!-- Card 1: Vision Models -->
  <rect x="456" y="118" width="384" height="42" rx="4" fill="#161b22" stroke="#22d3ee" stroke-opacity="0.3" stroke-width="1"/>
  <text x="468" y="136" class="key">👁️ Vision Pipelines</text>
  <text x="468" y="151" class="val" font-size="11">Camera movement detection, court/net keypoint AI</text>

  <!-- Card 2: MLOps & Cloud -->
  <rect x="456" y="168" width="384" height="42" rx="4" fill="#161b22" stroke="#39d353" stroke-opacity="0.3" stroke-width="1"/>
  <text x="468" y="186" class="val-accent">🚀 Cloud &amp; GPU Deployments</text>
  <text x="468" y="201" class="val" font-size="11">Google Cloud Platform • Scale-to-Zero GPU • Docker</text>

  <!-- Card 3: Research & Systems -->
  <rect x="456" y="218" width="384" height="42" rx="4" fill="#161b22" stroke="#f2cc60" stroke-opacity="0.3" stroke-width="1"/>
  <text x="468" y="236" class="val-yellow">🧠 DL Architectures</text>
  <text x="468" y="251" class="val" font-size="11">TensorFlow, PyTorch, Custom Vision Inference</text>

  <!-- Terminal footer line with prompt and blinking cursor -->
  <text x="456" y="292" class="prompt-host">divye@workstation:~$ <tspan class="val-highlight">EOF</tspan></text>
  <rect x="620" y="280" width="8" height="15" fill="#22d3ee" class="blink"/>
</svg>"""

os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"saved {OUT}")
