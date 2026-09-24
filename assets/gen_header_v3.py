#!/usr/bin/env python3
"""Animated von Karman vortex street banner (v3: art only, no text).

Transparent background, mid-tone palette so it reads on GitHub light *and* dark.
Animation is pure SMIL + SVG CSS: no JS, which GitHub would strip anyway.
"""
import math

W, H = 1000, 200
CYL_X, CYL_Y, CYL_R = 96, 100, 15
A = 120.0                 # streamwise vortex spacing within one row
DUR = 2.6                 # seconds for a vortex to advect one spacing
ROW_DY = 26               # half-separation of the two counter-rotating rows
SPIRAL_R = 21


def spiral(radius, turns=2.4, pts=90, sign=1):
    d = []
    for i in range(pts + 1):
        t = i / pts
        th = sign * t * turns * 2 * math.pi
        r = radius * t
        x, y = r * math.cos(th), r * math.sin(th)
        d.append(f"{'M' if i == 0 else 'L'}{x:.2f} {y:.2f}")
    return "".join(d)


def envelope(x):
    """Fade vortices in behind the cylinder and out before the right edge."""
    if x < 150:
        return 0.0
    if x < 320:
        return (x - 150) / 170
    if x < 780:
        return 1.0
    if x < 960:
        return 1.0 - (x - 780) / 180
    return 0.0


def row(y, sign, colour, phase):
    """One row of co-rotating vortices, marching right in lockstep."""
    out = []
    xs = [A * i + phase for i in range(-1, int(W / A) + 3)]
    for i, x0 in enumerate(xs):
        # opacity sampled along this vortex's own travel, so the fade is
        # a function of screen position rather than of identity
        ks = [j / 6 for j in range(7)]
        ops = [f"{envelope(x0 + k * A):.3f}" for k in ks]
        out.append(f"""  <g transform="translate({x0:.1f} {y})">
    <animateTransform attributeName="transform" type="translate" additive="sum"
      from="0 0" to="{A} 0" dur="{DUR}s" repeatCount="indefinite"/>
    <g opacity="0">
      <animate attributeName="opacity" values="{';'.join(ops)}"
        keyTimes="{';'.join(f'{k:.4f}' for k in ks)}"
        dur="{DUR}s" repeatCount="indefinite"/>
      <g>
        <animateTransform attributeName="transform" type="rotate"
          from="0" to="{360 * sign}" dur="{3.4 + 0.3 * (i % 3)}s"
          repeatCount="indefinite"/>
        <path d="{spiral(SPIRAL_R, sign=sign)}" fill="none" stroke="{colour}"
          stroke-width="2.6" stroke-linecap="round" opacity="0.95"/>
        <path d="{spiral(SPIRAL_R * 0.55, sign=sign)}" fill="none" stroke="{colour}"
          stroke-width="1.5" stroke-linecap="round" opacity="0.55"/>
      </g>
    </g>
  </g>""")
    return "\n".join(out)


streamlines = []
for k, sy in enumerate([40, 56, 144, 160]):
    streamlines.append(
        f'  <path d="M-40 {sy} L{W + 40} {sy}" stroke="#64748b" stroke-width="1.4" '
        f'fill="none" opacity="0.22" stroke-dasharray="26 34" stroke-linecap="round">'
        f'<animate attributeName="stroke-dashoffset" from="60" to="0" '
        f'dur="{1.5 + 0.25 * k}s" repeatCount="indefinite"/></path>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     width="{W}" height="{H}" role="img"
     aria-label="Suvam Samanta - animated von Karman vortex street">
  <title>Suvam Samanta - computational fluid dynamics and machine learning</title>
  <defs>
    <linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#22d3ee"/>
      <stop offset="45%"  stop-color="#818cf8"/>
      <stop offset="100%" stop-color="#fb7185"/>
    </linearGradient>
    <linearGradient id="cylGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e2e8f0"/>
      <stop offset="100%" stop-color="#64748b"/>
    </linearGradient>
  </defs>

  <rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="#0d1117"/>

{chr(10).join(streamlines)}

{row(CYL_Y - ROW_DY, +1, "#22d3ee", 0.0)}
{row(CYL_Y + ROW_DY, -1, "#f0a020", A / 2)}

  <circle cx="{CYL_X}" cy="{CYL_Y}" r="{CYL_R}" fill="url(#cylGrad)"
          stroke="#94a3b8" stroke-width="2"/>
  <circle cx="{CYL_X}" cy="{CYL_Y}" r="{CYL_R + 7}" fill="none" stroke="#22d3ee"
          stroke-width="1.6" opacity="0.5">
    <animate attributeName="r" values="{CYL_R + 5};{CYL_R + 14};{CYL_R + 5}"
             dur="2.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.55;0;0.55" dur="2.6s"
             repeatCount="indefinite"/>
  </circle>

</svg>
"""

with open("/home/syphonic/WORK/Syphonicc/assets/header.svg", "w") as f:
    f.write(svg)
print("wrote header.svg v3", len(svg), "bytes")
