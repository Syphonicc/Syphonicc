#!/usr/bin/env python3
"""v4 preview: vortex street + a swimmer fighting his way upstream.

Writes header_v5_preview.svg. Does NOT touch the live header.svg.
"""
import math

W, H = 1000, 230
CYL_X, CYL_Y, CYL_R = 96, 115, 15
A, DUR, ROW_DY, SPIRAL_R = 120.0, 2.6, 26, 21

SWIM_X, SWIM_Y, SWIM_S = 600, 115, 1.15   # placement + scale of the swimmer

RED, RED_D = "#e03131", "#8d1616"
BLUE, BLUE_D = "#2a4a9e", "#152a63"
SKIN = "#e8b08a"


def spiral(radius, turns=2.4, pts=90, sign=1):
    d = []
    for i in range(pts + 1):
        t = i / pts
        th = sign * t * turns * 2 * math.pi
        r = radius * t
        d.append(f"{'M' if i == 0 else 'L'}{r*math.cos(th):.2f} {r*math.sin(th):.2f}")
    return "".join(d)


def envelope(x):
    if x < 150: return 0.0
    if x < 320: return (x - 150) / 170
    if x < 780: return 1.0
    if x < 960: return 1.0 - (x - 780) / 180
    return 0.0


def row(y, sign, colour, phase):
    out = []
    for i, x0 in enumerate([A * k + phase for k in range(-1, int(W / A) + 3)]):
        ks = [j / 6 for j in range(7)]
        ops = ";".join(f"{envelope(x0 + k * A):.3f}" for k in ks)
        kt = ";".join(f"{k:.4f}" for k in ks)
        out.append(f"""  <g transform="translate({x0:.1f} {y})">
    <animateTransform attributeName="transform" type="translate" additive="sum"
      from="0 0" to="{A} 0" dur="{DUR}s" repeatCount="indefinite"/>
    <g opacity="0">
      <animate attributeName="opacity" values="{ops}" keyTimes="{kt}" dur="{DUR}s" repeatCount="indefinite"/>
      <g><animateTransform attributeName="transform" type="rotate" from="0" to="{360*sign}"
           dur="{3.4 + 0.3*(i%3)}s" repeatCount="indefinite"/>
        <path d="{spiral(SPIRAL_R, sign=sign)}" fill="none" stroke="{colour}" stroke-width="2.6"
              stroke-linecap="round" opacity="0.95"/>
        <path d="{spiral(SPIRAL_R*0.55, sign=sign)}" fill="none" stroke="{colour}" stroke-width="1.5"
              stroke-linecap="round" opacity="0.55"/>
      </g></g></g>""")
    return "\n".join(out)


def droplet(x, y, dx, dy, r, dur, delay, colour="#bfe9ff", op=0.95):
    """One ballistic splash droplet, looping."""
    return (f'    <g transform="translate({x} {y})">'
            f'<circle r="{r}" fill="{colour}" opacity="0">'
            f'<animateMotion path="M0 0 q {dx*0.5:.1f} {dy:.1f} {dx:.1f} {dy*0.15+9:.1f}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;{op};{op};0" keyTimes="0;0.12;0.55;1" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
            f'</circle></g>')


def arm(phase, far=False):
    """Front-crawl arm: bent limb rotating a full turn about the shoulder.
    The hand is a red glove -- the suit covers it, so no skin."""
    grad = "url(#redFarG)" if far else "url(#redG)"
    edge = "#5e0f0f" if far else "#7a1414"
    w    = 6.6 if far else 7.6
    op   = 0.9 if far else 1.0
    return f"""      <g>
        <animateTransform attributeName="transform" type="rotate" from="{phase}" to="{phase-360}"
          dur="1.05s" repeatCount="indefinite"/>
        <path d="M0 0 Q -9 5 -15 11 T -23 19" fill="none" stroke="{edge}" stroke-width="{w+1.4}"
              stroke-linecap="round" stroke-linejoin="round" opacity="{op*0.85}"/>
        <path d="M0 0 Q -9 5 -15 11 T -23 19" fill="none" stroke="{grad}" stroke-width="{w}"
              stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>
        <path d="M-1 -1 Q -9 4 -14 10" fill="none" stroke="#ff8a8a" stroke-width="1.5"
              stroke-linecap="round" opacity="{op*0.45}"/>
        <g opacity="{op}">
          <ellipse cx="-23.5" cy="19.5" rx="{w*0.62:.1f}" ry="{w*0.52:.1f}"
                   fill="{grad}" stroke="{edge}" stroke-width="0.9"/>
          <path d="M-26 18 L-21 21 M-24 16.5 L-23 22.5" stroke="{edge}"
                stroke-width="0.6" opacity="0.8"/>
        </g>
      </g>"""


def leg(sign, far=False):
    """Flutter kick. `sign` flips the phase so the two legs scissor in true
    opposition: both start at t=0, one swinging up while the other swings down.
    (Do NOT also offset `begin` by half a period -- that cancels the flip and
    the legs end up superimposed.)"""
    amp  = 22
    vals = f"{-amp*sign};{amp*sign};{-amp*sign}"
    col  = "url(#blueFarG)" if far else "url(#blueG)"
    dcol = "#0c1a44" if far else BLUE_D
    foot = "url(#redFarG)" if far else "url(#redG)"
    w    = 6.4 if far else 7.4
    yoff = 4.0 if far else 0
    op   = 0.95 if far else 1.0
    k    = 0.90 if far else 1.0          # far leg slightly foreshortened
    return f"""      <g transform="translate(15 {2 + yoff})">
        <animateTransform attributeName="transform" type="rotate" additive="sum"
          values="{vals}" dur="0.52s" repeatCount="indefinite"
          calcMode="spline" keyTimes="0;0.5;1"
          keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
        <path d="M0 0 Q {13*k:.1f} 2 {21*k:.1f} 5 T {33*k:.1f} 9" fill="none" stroke="{col}"
              stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>
        <path d="M0 0 Q {13*k:.1f} 2 {21*k:.1f} 5 T {33*k:.1f} 9" fill="none" stroke="{dcol}"
              stroke-width="{w}" stroke-linecap="round" stroke-dasharray="1.4 6" opacity="0.55"/>
        <ellipse cx="{34*k:.1f}" cy="10" rx="5.4" ry="3.2" fill="{foot}" stroke="#5e0f0f" stroke-width="0.8" opacity="{op}"/>
      </g>"""


# ---- the swimmer, drawn facing left (upstream) -----------------------------
web_head = "".join(
    f'<path d="M-25 -2 L{-25 + 8.5*math.cos(math.radians(a)):.1f} {-2 + 8.5*math.sin(math.radians(a)):.1f}" '
    f'stroke="{RED_D}" stroke-width="0.8" opacity="0.75"/>'
    for a in (200, 250, 300, 340, 20, 70, 120, 160))

swimmer = f"""
  <g transform="translate({SWIM_X} {SWIM_Y}) scale({SWIM_S})">
    <!-- surge forward, then lose ground to the current -->
    <animateTransform attributeName="transform" type="translate" additive="sum"
      values="0 0; -18 -1; -11 1; 6 0; 0 0" keyTimes="0;0.3;0.55;0.85;1"
      dur="3.4s" repeatCount="indefinite" calcMode="spline"
      keySplines="0.2 0.7 0.3 1; 0.4 0 0.6 1; 0.4 0 0.6 1; 0.4 0 0.6 1"/>
    <g>
      <animateTransform attributeName="transform" type="translate" additive="sum"
        values="0 0; 0 -2.2; 0 0" dur="1.05s" repeatCount="indefinite"/>

      <!-- separation halo against the vortices -->
      <ellipse cx="4" cy="4" rx="54" ry="24" fill="#0d1117" opacity="0.55"/>

      <!-- far arm, behind the body -->
{arm(200, far=True)}

      <!-- far leg, behind the body -->
{leg(-1, far=True)}

      <!-- torso: shaded red over shaded blue -->
      <path d="M-16 -6 Q 2 -9 18 -4 Q 20 2 18 7 Q 2 10 -16 7 Z" fill="url(#blueG)"
            stroke="#101f4a" stroke-width="0.8"/>
      <path d="M-18 -7 Q -4 -10 6 -7 Q 8 0 6 8 Q -4 10 -18 7 Z" fill="url(#redG)"
            stroke="#6d1212" stroke-width="0.9"/>
      <!-- specular highlight along the back -->
      <path d="M-16 -6.6 Q -4 -9.2 5 -6.6" fill="none" stroke="#ff9b9b" stroke-width="1.6"
            stroke-linecap="round" opacity="0.5"/>
      <path d="M8 -5.2 Q 14 -5.2 17.4 -3.6" fill="none" stroke="#7d9cec" stroke-width="1.3"
            stroke-linecap="round" opacity="0.45"/>
      <!-- webbing -->
      <path d="M-17 -3 L5 -2 M-17 2 L5 3 M-12 -8 L-11 9 M-5 -9 L-4 9 M2 -8 L3 9"
            stroke="#6d1212" stroke-width="0.7" fill="none" opacity="0.75"/>
      <path d="M8 -6 L18 -3 M8 0 L19 1 M8 5 L18 6" stroke="#101f4a" stroke-width="0.7" opacity="0.6"/>
      <!-- chest emblem -->
      <g opacity="0.9">
        <ellipse cx="-7" cy="0.5" rx="1.5" ry="2.5" fill="#3d0808"/>
        <path d="M-8 -1 L-11 -3 M-8 0 L-11.5 0 M-8 1.5 L-11 3.5 M-8 2.5 L-9.5 5
                 M-6 -1 L-3 -3 M-6 0 L-2.5 0 M-6 1.5 L-3 3.5 M-6 2.5 L-4.5 5"
              stroke="#3d0808" stroke-width="0.55" fill="none" stroke-linecap="round"/>
      </g>

      <!-- near leg, in front -->
{leg(+1)}

      <!-- head, turned to breathe -->
      <g transform="translate(0 0)">
        <animateTransform attributeName="transform" type="rotate" values="-6 -25 -2; 4 -25 -2; -6 -25 -2"
          dur="1.05s" repeatCount="indefinite"/>
        <circle cx="-25" cy="-2" r="8.5" fill="url(#headG)"/>
        {web_head}
        <circle cx="-25" cy="-2" r="8.5" fill="none" stroke="#6d1212" stroke-width="1.1"/>
        <path d="M-30 -7.5 Q -24 -10 -19.5 -6.5" fill="none" stroke="#ff9b9b" stroke-width="1.4"
              stroke-linecap="round" opacity="0.55"/>
        <path d="M-29 -5 Q -33.4 -3 -30.2 1.2 Q -25.8 1.2 -25.8 -3.2 Z" fill="#ffffff"
              stroke="#0d0d0d" stroke-width="1"/>
        <path d="M-30.4 -4.4 Q -32.2 -3.4 -30.8 -1.6" fill="none" stroke="#9fd4ff"
              stroke-width="0.9" stroke-linecap="round" opacity="0.85"/>
      </g>

      <!-- near arm, in front -->
{arm(20)}

      <!-- bow wave at the head -->
      <path d="M-36 4 Q -30 8 -22 6" fill="none" stroke="#bfe9ff" stroke-width="1.6"
            stroke-linecap="round" opacity="0.7">
        <animate attributeName="opacity" values="0.25;0.85;0.25" dur="1.05s" repeatCount="indefinite"/>
      </path>

      <!-- splash: hand entry, kick wash, bow spray -->
{chr(10).join([
    droplet(-30, 2, -13, -16, 1.9, 0.85, 0.00),
    droplet(-28, 0, -17, -12, 1.4, 0.95, 0.18),
    droplet(-32, 3, -9, -19, 1.6, 0.80, 0.42),
    droplet(-26, 5, -15, -9, 1.2, 0.90, 0.61),
    droplet(-31, -1, -11, -21, 1.0, 1.00, 0.30),
    droplet(48, 8, 15, -13, 1.7, 0.78, 0.05),
    droplet(50, 11, 19, -9, 1.3, 0.88, 0.27),
    droplet(46, 6, 12, -17, 1.5, 0.82, 0.50),
    droplet(52, 9, 22, -6, 1.1, 0.95, 0.70),
    droplet(44, 12, 16, -11, 1.4, 0.86, 0.14),
    droplet(-6, -12, -6, -14, 1.2, 0.92, 0.36),
    droplet(2, -13, 4, -16, 1.0, 0.86, 0.66),
])}
    </g>
  </g>"""

streamlines = "\n".join(
    f'  <path d="M-40 {sy} L{W+40} {sy}" stroke="#64748b" stroke-width="1.4" fill="none" '
    f'opacity="0.30" stroke-dasharray="26 34" stroke-linecap="round">'
    f'<animate attributeName="stroke-dashoffset" from="60" to="0" dur="{1.5+0.25*k}s" '
    f'repeatCount="indefinite"/></path>'
    for k, sy in enumerate([48, 64, 166, 182]))

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
     role="img" aria-label="A vortex street with a small figure swimming upstream">
  <defs>
    <linearGradient id="redG" gradientUnits="userSpaceOnUse" x1="0" y1="-16" x2="0" y2="14">
      <stop offset="0"    stop-color="#ff6f6f"/>
      <stop offset="0.42" stop-color="#e03131"/>
      <stop offset="1"    stop-color="#8f1b1b"/>
    </linearGradient>
    <linearGradient id="redFarG" gradientUnits="userSpaceOnUse" x1="0" y1="-16" x2="0" y2="22">
      <stop offset="0"    stop-color="#b34040"/>
      <stop offset="0.5"  stop-color="#8d1616"/>
      <stop offset="1"    stop-color="#560e0e"/>
    </linearGradient>
    <linearGradient id="blueG" gradientUnits="userSpaceOnUse" x1="0" y1="-10" x2="0" y2="14">
      <stop offset="0"    stop-color="#4e74d6"/>
      <stop offset="0.5"  stop-color="#2a4a9e"/>
      <stop offset="1"    stop-color="#14265c"/>
    </linearGradient>
    <linearGradient id="blueFarG" gradientUnits="userSpaceOnUse" x1="0" y1="-8" x2="0" y2="18">
      <stop offset="0"    stop-color="#31509b"/>
      <stop offset="0.5"  stop-color="#1b3270"/>
      <stop offset="1"    stop-color="#0c1a44"/>
    </linearGradient>
    <radialGradient id="headG" gradientUnits="userSpaceOnUse" cx="-27" cy="-6" r="13">
      <stop offset="0"   stop-color="#ff7b7b"/>
      <stop offset="0.5" stop-color="#e03131"/>
      <stop offset="1"   stop-color="#8f1b1b"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="#0d1117"/>

{streamlines}

{row(CYL_Y - ROW_DY, +1, "#22d3ee", 0.0)}
{row(CYL_Y + ROW_DY, -1, "#f0a020", A/2)}

  <circle cx="{CYL_X}" cy="{CYL_Y}" r="{CYL_R}" fill="#94a3b8" stroke="#cbd5e1" stroke-width="2"/>
  <circle cx="{CYL_X}" cy="{CYL_Y}" r="{CYL_R+7}" fill="none" stroke="#22d3ee" stroke-width="1.6" opacity="0.5">
    <animate attributeName="r" values="{CYL_R+5};{CYL_R+14};{CYL_R+5}" dur="2.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.55;0;0.55" dur="2.6s" repeatCount="indefinite"/>
  </circle>
{swimmer}
</svg>
"""
open("header_v5_preview.svg", "w").write(svg)
print("wrote header_v5_preview.svg", len(svg), "bytes")
