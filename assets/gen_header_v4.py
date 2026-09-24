#!/usr/bin/env python3
"""v4 preview: vortex street + a swimmer fighting his way upstream.

Writes header_v4_preview.svg. Does NOT touch the live header.svg.
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


def arm(phase, colour, width, opacity=1.0):
    """Front-crawl arm: a bent limb rotating a full turn about the shoulder."""
    return f"""      <g>
        <animateTransform attributeName="transform" type="rotate" from="{phase}" to="{phase-360}"
          dur="1.05s" repeatCount="indefinite"/>
        <path d="M0 0 Q -9 5 -15 11 T -23 19" fill="none" stroke="{colour}" stroke-width="{width}"
              stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"/>
        <circle cx="-23" cy="19" r="{width*0.52:.1f}" fill="{SKIN}" opacity="{opacity}"/>
      </g>"""


def leg(sign, far=False):
    """Flutter kick. `sign` flips the phase so the two legs scissor in true
    opposition: both start at t=0, one swinging up while the other swings down.
    (Do NOT also offset `begin` by half a period -- that cancels the flip and
    the legs end up superimposed.)"""
    amp  = 22
    vals = f"{-amp*sign};{amp*sign};{-amp*sign}"
    col  = "#1b3270" if far else BLUE
    dcol = "#0c1a44" if far else BLUE_D
    foot = "#7d1414" if far else RED_D
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
        <ellipse cx="{34*k:.1f}" cy="10" rx="5" ry="3" fill="{foot}" opacity="{op}"/>
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
{arm(200, RED_D, 6.5, 0.85)}

      <!-- far leg, behind the body -->
{leg(-1, far=True)}

      <!-- torso: red over blue -->
      <path d="M-16 -6 Q 2 -9 18 -4 Q 20 2 18 7 Q 2 10 -16 7 Z" fill="{BLUE}"/>
      <path d="M-18 -7 Q -4 -10 6 -7 Q 8 0 6 8 Q -4 10 -18 7 Z" fill="{RED}"/>
      <path d="M-17 -3 L5 -2 M-17 2 L5 3 M-12 -8 L-11 9 M-5 -9 L-4 9 M2 -8 L3 9"
            stroke="{RED_D}" stroke-width="0.8" fill="none" opacity="0.7"/>
      <path d="M8 -6 L18 -3 M8 0 L19 1 M8 5 L18 6" stroke="{BLUE_D}" stroke-width="0.8" opacity="0.6"/>

      <!-- near leg, in front -->
{leg(+1)}

      <!-- head, turned to breathe -->
      <g transform="translate(0 0)">
        <animateTransform attributeName="transform" type="rotate" values="-6 -25 -2; 4 -25 -2; -6 -25 -2"
          dur="1.05s" repeatCount="indefinite"/>
        <circle cx="-25" cy="-2" r="8.5" fill="{RED}"/>
        {web_head}
        <circle cx="-25" cy="-2" r="8.5" fill="none" stroke="{RED_D}" stroke-width="1"/>
        <path d="M-29 -5 Q -33 -3 -30 1 Q -26 1 -26 -3 Z" fill="#ffffff" stroke="#111" stroke-width="0.9"/>
      </g>

      <!-- near arm, in front -->
{arm(20, RED, 7.5)}

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
open("header_v4_preview.svg", "w").write(svg)
print("wrote header_v4_preview.svg", len(svg), "bytes")
