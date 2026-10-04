"""Build dc/dc-home.html (English), dc/dc-home-hi.html (Hindi) and dc/dc-home-or.html (Odia):
an isometric Indian town house running on solar DC, plus a section view.

  python3 dc/build_dc_home.py            # all three languages
  python3 dc/build_dc_home.py hi         # one language

World axes (metres): x = east, y = north, z = up. The view looks from the south-east, so the
south and east faces of everything are visible, south-facing solar panels show their glass, and
the east entrance with its sliding gate faces the viewer.
"""
import math, pathlib, sys

from dc_home_text import TEXT

HERE = pathlib.Path(__file__).parent
LANG = "en"


def t(key):
    return TEXT[LANG][key]


def ff():
    """svg font stack: Latin first, then the script of the current language"""
    return {"en": "Plus Jakarta Sans,Arial", "hi": "Plus Jakarta Sans,Noto Sans Devanagari,Arial",
            "or": "Plus Jakarta Sans,Noto Sans Oriya,Arial"}[LANG]


def ls(v):
    """letter-spacing breaks Indic shaping, so only English gets it"""
    return v if LANG == "en" else "0"
S = 30.0                       # px per metre
C30, S30 = math.cos(math.radians(30)), 0.5
parts = []                     # iso scene svg fragments, in painter's order (far to near)
pts_seen = []


def P(x, y, z=0.0):
    sx = (x + y) * C30 * S
    sy = (x - y) * S30 * S - z * S
    pts_seen.append((sx, sy))
    return sx, sy


def poly(pts, fill, stroke="none", sw=1.0, extra=""):
    d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (P(*p) for p in pts))
    parts.append(f'<polygon points="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>')


def line(p1, p2, stroke, sw=2.0, extra=""):
    (a, b), (c, d) = P(*p1), P(*p2)
    parts.append(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" {extra}/>')


def box(x0, x1, y0, y1, z0, z1, top, south, east, stroke="rgba(60,30,10,.35)"):
    poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top, stroke, .8)
    poly([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], south, stroke, .8)
    poly([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], east, stroke, .8)


def south_rect(x0, x1, y, z0, z1, fill, stroke="none", sw=1):
    poly([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], fill, stroke, sw)


def east_rect(x, y0, y1, z0, z1, fill, stroke="none", sw=1):
    poly([(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)], fill, stroke, sw)


def glow(x, y, z, r=18):
    a, b = P(x, y, z)
    parts.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{r}" fill="url(#glow)"/><circle cx="{a:.1f}" cy="{b:.1f}" r="{r * .22:.1f}" fill="#fff4c2"/>')


def badge(x, y, z, n, dx=0, dy=-34):
    a, b = P(x, y, z)
    parts.append(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{a + dx:.1f}" y2="{b + dy + 14:.1f}" stroke="#3b2a20" stroke-width="1.6"/>'
                 f'<circle cx="{a:.1f}" cy="{b:.1f}" r="3.5" fill="#3b2a20"/>'
                 f'<circle cx="{a + dx:.1f}" cy="{b + dy:.1f}" r="15" fill="#1b4d36" stroke="#fff" stroke-width="2.5"/>'
                 f'<text x="{a + dx:.1f}" y="{b + dy + 5:.1f}" text-anchor="middle" font-family="{ff()}" font-size="14" font-weight="800" fill="#fff">{n}</text>')


def ground_text(x, y, text, size=15, fill="#7a5233", along="x"):
    a, b = P(x, y, 0)
    ang = 30 if along == "x" else -30
    parts.append(f'<text transform="translate({a:.1f} {b:.1f}) rotate({ang}) skewX({-ang})" text-anchor="middle" font-family="{ff()}" font-size="{size}" font-weight="800" letter-spacing="{ls(3)}" fill="{fill}">{text}</text>')


def pillar(x, y, h=1.9, lamp=True):
    box(x - .28, x + .28, y - .28, y + .28, 0, h, "#e9c79c", "#b0603a", "#8f4c2d")
    box(x - .34, x + .34, y - .34, y + .34, h, h + .12, "#f1d5ad", "#c7845a", "#a86a45")
    if lamp:
        box(x - .16, x + .16, y - .16, y + .16, h + .12, h + .5, "#fff1c4", "#f7d27a", "#e6b85c")
        box(x - .22, x + .22, y - .22, y + .22, h + .5, h + .58, "#4a3426", "#3b2a20", "#2e2018")
        glow(x, y, h + .32, 22)


def tree(x, y, h=4.2, r=2.0):
    line((x, y, 0), (x, y, h * .62), "#6b4a2f", 7)
    for dx, dy, dz, rr, col in [(-.6, .3, h * .78, r * .8, "#6f8240"), (.7, -.2, h * .8, r * .75, "#7d8f4a"),
                                (0, 0, h, r * .9, "#859a52"), (.2, .6, h * .9, r * .7, "#6a7c3c")]:
        a, b = P(x + dx, y + dy, dz)
        parts.append(f'<ellipse cx="{a:.1f}" cy="{b:.1f}" rx="{rr * S * .9:.1f}" ry="{rr * S * .62:.1f}" fill="{col}" opacity=".96"/>')


def potted(x, y, s=1.0, plant="#6f8a3e"):
    box(x - .25 * s, x + .25 * s, y - .25 * s, y + .25 * s, 0, .45 * s, "#c46a3e", "#b05a32", "#91482a")
    a, b = P(x, y, .45 * s + .35 * s)
    parts.append(f'<ellipse cx="{a:.1f}" cy="{b:.1f}" rx="{14 * s:.1f}" ry="{11 * s:.1f}" fill="{plant}"/>')


def build_iso():
    # ---------- ground ----------
    poly([(-12, -9, 0), (26, -9, 0), (26, 22, 0), (-12, 22, 0)], "#efe2c8")
    poly([(17.4, -9, 0), (23, -9, 0), (23, 22, 0), (17.4, 22, 0)], "#93836f")          # road on the east
    for yy in range(-8, 22, 3):
        poly([(20.05, yy, 0), (20.35, yy, 0), (20.35, yy + 1.4, 0), (20.05, yy + 1.4, 0)], "#e8dcc4")
    poly([(17.0, -9, 0), (17.4, -9, 0), (17.4, 22, 0), (17.0, 22, 0)], "#cdb592")    # kerb
    poly([(-3, -4, 0), (17, -4, 0), (17, 12, 0), (-3, 12, 0)], "#e4cfa9")             # plot
    poly([(1, 2, 0.01), (13.4, 2, 0.01), (13.4, 9.5, 0.01), (1, 9.5, 0.01)], "#d6bd94")  # paved surround
    poly([(12, 4.4, .01), (17, 4.4, .01), (17, 7.2, .01), (12, 7.2, .01)], "#cfb187")   # driveway to the gate

    # ---------- neighbours (far north and west) ----------
    for (x0, x1, y0, y1, h, cs) in [(-2, 4, 15, 19, 3.6, ("#f2e1c6", "#e0bf98", "#cfa97f")),
                                    (5, 11, 15.5, 19, 4.6, ("#f4e5cd", "#e6c7a0", "#d3b088")),
                                    (12, 16.5, 15, 19, 3.4, ("#f0dcbf", "#dfb991", "#cba27a")),
                                    (-11, -6.5, 6, 11, 3.6, ("#f2e1c6", "#e0bf98", "#cfa97f"))]:
        box(x0, x1, y0, y1, 0, h, *cs)
        for k in range(int((x1 - x0) // 2)):
            south_rect(x0 + .7 + k * 2, x0 + 1.5 + k * 2, y0, h * .4, h * .4 + 1.0, "#b78b66")

    # ---------- far boundary walls (north, west) ----------
    box(-3, 17, 11.75, 12, 0, 1.5, "#e1b892", "#b5643a", "#94512f")
    box(-3, -2.75, -4, 12, 0, 1.5, "#e1b892", "#b5643a", "#94512f")
    pillar(-3, 12); pillar(17, 12)

    # ---------- house ----------
    X0, X1, Y0, Y1, H = 1.0, 12.0, 2.0, 9.5, 6.6
    F1 = 3.3                                   # first-floor level
    box(X0 - .15, X1 + .15, Y0 - .15, Y1 + .15, 0, .45, "#b9895f", "#8c4a2b", "#733b22")      # plinth
    # first-floor balcony on the north side (back part, mostly hidden behind the house)
    box(8.0, 12.0, Y1, Y1 + 1.25, F1 - .06, F1 + .22, "#e8cfa8", "#b7835a", "#9c6b45")
    box(8.0, 8.15, Y1, Y1 + 1.1, F1 + .22, F1 + 1.15, "#f3d9b1", "#c46a3e", "#a85a35")
    box(8.0, 12.0, Y1 + 1.1, Y1 + 1.25, F1 + .22, F1 + 1.15, "#f3d9b1", "#c46a3e", "#a85a35")
    box(X0, X1, Y0, Y1, .45, H, "#efd2a6", "#d99a5b", "#b97a45")                              # walls
    # south windows with chajja (sunshade) and lit glass
    for wx, zb in ((2.0, 0), (5.4, 0), (8.8, 0), (2.0, F1), (5.4, F1), (8.8, F1)):
        south_rect(wx - .1, wx + 1.5, Y0, zb + 1.05, zb + 2.45, "#6b4226")
        south_rect(wx, wx + 1.4, Y0, zb + 1.15, zb + 2.35, "#f4d58e")
        line((wx + .7, Y0, zb + 1.15), (wx + .7, Y0, zb + 2.35), "#6b4226", 2)
        box(wx - .3, wx + 1.7, Y0 - .55, Y0, zb + 2.62, zb + 2.75, "#e8c79e", "#b7835a", "#9c6b45")
    # floor band between the storeys
    south_rect(X0, X1, Y0, F1 - .02, F1 + .16, "#c07f48")
    east_rect(X1, Y0, Y1, F1 - .02, F1 + .16, "#a06a3c")
    # first-floor east windows
    for wy in (4.6, 6.9):
        east_rect(X1, wy - .1, wy + 1.3, F1 + 1.05, F1 + 2.45, "#6b4226"); east_rect(X1, wy, wy + 1.2, F1 + 1.15, F1 + 2.35, "#f4d58e")
        box(X1, X1 + .5, wy - .3, wy + 1.5, F1 + 2.62, F1 + 2.75, "#e8c79e", "#b7835a", "#9c6b45")
    # north balcony wraps the north-east corner: door from the upper bedroom on the east wall
    east_rect(X1, 8.95, 9.45, F1 + .22, F1 + 2.55, "#6b4226"); east_rect(X1, 9.02, 9.38, F1 + .3, F1 + 2.47, "#f4d58e")
    glow(X1 + .03, 8.72, F1 + 2.35, 16)
    BX = X1 + 1.25
    box(X1, BX, 8.8, Y1 + 1.25, F1 - .06, F1 + .22, "#e8cfa8", "#b7835a", "#9c6b45")                 # slab
    box(X1, BX, Y1 + 1.1, Y1 + 1.25, F1 + .22, F1 + 1.15, "#f3d9b1", "#c46a3e", "#a85a35")           # north parapet
    a, b = P(X1 + .6, Y1 + .5, F1 + 1.35)
    parts.append(f'<ellipse cx="{a:.1f}" cy="{b:.1f}" rx="17" ry="12" fill="#6f8a3e"/><ellipse cx="{a + 8:.1f}" cy="{b - 6:.1f}" rx="10" ry="8" fill="#7f9a48"/>')
    box(X1, BX, 8.8, 8.95, F1 + .22, F1 + 1.15, "#f3d9b1", "#c46a3e", "#a85a35")                     # south end
    box(BX - .15, BX, 8.95, Y1 + 1.1, F1 + .22, F1 + 1.15, "#f3d9b1", "#c46a3e", "#a85a35")          # east parapet
    box(BX - .2, BX + .05, 8.75, Y1 + 1.3, F1 + 1.15, F1 + 1.25, "#f7e2c0", "#d8a274", "#bf8a5e")    # coping
    box(X1 - .05, BX + .05, 8.75, 8.97, F1 + 1.15, F1 + 1.25, "#f7e2c0", "#d8a274", "#bf8a5e")
    for k in range(5):
        yy = 9.15 + k * .4
        east_rect(BX, yy, yy + .18, F1 + .5, F1 + .9, "#8c4a2b")
    for k in range(3):
        xx = X1 + .2 + k * .36
        south_rect(xx, xx + .18, 8.8, F1 + .5, F1 + .9, "#8c4a2b")
    # east face: main entrance door, window, porch and steps
    east_rect(X1, 4.45, 5.95, .45, 2.75, "#6b4226")
    east_rect(X1, 4.6, 5.8, .45, 2.65, "#8a5530")
    for zz in (.9, 1.6, 2.3):
        line((X1, 4.7, zz), (X1, 5.7, zz), "#6b4226", 1.6)
    east_rect(X1, 7.2, 8.6, 1.05, 2.45, "#6b4226"); east_rect(X1, 7.3, 8.5, 1.15, 2.35, "#f4d58e")
    glow(X1 + .05, 4.15, 2.35, 16)
    box(X1, X1 + 1.3, 4.1, 6.3, 2.95, 3.08, "#ead0a8", "#b7835a", "#9c6b45")                    # porch canopy
    box(X1, X1 + 1.5, 4.2, 6.2, 0, .15, "#d8c2a0", "#a98d6c", "#8f7558")                       # step 1
    box(X1, X1 + 1.0, 4.2, 6.2, .15, .3, "#e2cdaa", "#b39674", "#977c5e")                      # step 2
    # roof terrace
    box(X0, X1, Y0, Y1, H, H + .18, "#cbb595", "#c18a54", "#a87444")
    # far parapets (north, west)
    box(X0, X1, Y1 - .2, Y1, H + .18, H + 1.0, "#efd2a6", "#d39457", "#b07240")
    box(X0, X0 + .2, Y0, Y1, H + .18, H + 1.0, "#efd2a6", "#d39457", "#b07240")
    # stair room (mumty) with water tank
    box(X0 + .2, 4.4, 6.4, Y1 - .2, H + .18, H + 2.7, "#efd2a6", "#cf8f52", "#a96d3d")
    south_rect(2.3, 3.3, 6.4, H + .2, H + 2.2, "#6b4226")
    box(X0 + .1, 4.5, 6.3, Y1 - .1, H + 2.7, H + 2.85, "#ead0a8", "#b7835a", "#9c6b45")
    cx, cy, cz = 2.8, 8.0, H + 2.85
    a, b = P(cx, cy, cz); a2, b2 = P(cx, cy, cz + 1.2)
    rx, ry = .85 * S * 1.22, .85 * S * .7
    parts.append(f'<path d="M{a - rx:.1f} {b:.1f} V{b2:.1f} A{rx:.1f} {ry:.1f} 0 0 1 {a + rx:.1f} {b2:.1f} V{b:.1f} A{rx:.1f} {ry:.1f} 0 0 1 {a - rx:.1f} {b:.1f} Z" fill="#2f2f2f"/>'
                 f'<ellipse cx="{a2:.1f}" cy="{b2:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#474747"/>'
                 f'<ellipse cx="{a2:.1f}" cy="{b2 - 2:.1f}" rx="{rx * .35:.1f}" ry="{ry * .35:.1f}" fill="#2a2a2a"/>')
    # DC conduit from the panels down to the utility (west of the stair room)
    line((4.6, 6.3, H + .2), (4.6, 6.3, H + 1.0), "#d93025", 3); line((4.75, 6.3, H + .2), (4.75, 6.3, H + 1.0), "#2b2b2b", 3)

    # solar panel rows, tilted to face south, drawn north (far) to south (near)
    for y0 in (7.0, 4.6, 2.3):
        xa, xb, d, zl, zh = 5.0, 11.4, 1.7, H + .55, H + 1.55
        if y0 == 7.0:
            xa = 5.0
        for xx in (xa + .2, xb - .2):
            line((xx, y0 + .1, H + .18), (xx, y0 + .1, zl), "#5a6570", 3)
            line((xx, y0 + d - .1, H + .18), (xx, y0 + d - .1, zh), "#5a6570", 3)
        poly([(xa, y0, zl), (xb, y0, zl), (xb, y0 + d, zh), (xa, y0 + d, zh)], "#22426a", "#8ea4bd", 1.6)
        n = 8
        for k in range(1, n):
            xx = xa + (xb - xa) * k / n
            line((xx, y0, zl), (xx, y0 + d, zh), "#6c8fb8", 1.1)
        line((xa, y0 + d / 2, (zl + zh) / 2), (xb, y0 + d / 2, (zl + zh) / 2), "#6c8fb8", 1.1)
        # sheen
        poly([(xa + .3, y0 + .15, zl + .09), (xa + 1.6, y0 + .15, zl + .09), (xa + 1.0, y0 + d - .2, zh - .12), (xa + .1, y0 + d - .2, zh - .12)], "rgba(255,255,255,.12)")
    # near parapets (south, east) drawn after the panels
    box(X0, X1, Y0, Y0 + .2, H + .18, H + 1.0, "#f3d9b1", "#dc9e5f", "#b97a45")
    box(X1 - .2, X1, Y0, Y1, H + .18, H + 1.0, "#f3d9b1", "#dc9e5f", "#b97a45")
    # parapet jaali band (south)
    for k in range(18):
        xx = X0 + .4 + k * .58
        south_rect(xx, xx + .28, Y0, H + .45, H + .75, "#b5743f")

    # ---------- courtyard ----------
    # tulsi planter in front (south) courtyard
    box(6.2, 7.0, -1.0, -.2, 0, .9, "#f0d8b4", "#c96f43", "#a85a35")
    a, b = P(6.6, -.6, 1.35)
    parts.append(f'<ellipse cx="{a:.1f}" cy="{b:.1f}" rx="16" ry="12" fill="#5f7f38"/>')
    potted(13.6, 3.7); potted(13.6, 6.8, 1.0, "#7a9a44")
    # rangoli in front of the steps
    a, b = P(14.3, 5.2, .02)
    parts.append(f'<g transform="translate({a:.1f} {b:.1f}) scale(1 .58) rotate(45)"><circle r="20" fill="#e2573b"/><circle r="15" fill="#f2b632"/><circle r="10" fill="#2f8a57"/><circle r="5" fill="#ffffff"/></g>')
    # compass rose on the ground
    a, b = P(1.2, -7.4, .02)
    nx, ny = C30 * S * 1.6, -S30 * S * 1.6      # +y (north) on screen
    ex, ey = C30 * S * 1.6, S30 * S * 1.6       # +x (east) on screen
    parts.append(f'<g font-family="{ff()}" font-weight="800" font-size="15">'
                 f'<ellipse cx="{a:.1f}" cy="{b:.1f}" rx="{S * 1.9:.1f}" ry="{S * 1.1:.1f}" fill="#f5ead6" stroke="#7a5233" stroke-width="1.5"/>'
                 f'<polygon points="{a + nx:.1f},{b + ny:.1f} {a + ny * .18:.1f},{b - nx * .18:.1f} {a - ny * .18:.1f},{b + nx * .18:.1f}" fill="#c0392b"/>'
                 f'<line x1="{a - nx:.1f}" y1="{b - ny:.1f}" x2="{a:.1f}" y2="{b:.1f}" stroke="#7a5233" stroke-width="2"/>'
                 f'<line x1="{a - ex:.1f}" y1="{b - ey:.1f}" x2="{a + ex:.1f}" y2="{b + ey:.1f}" stroke="#7a5233" stroke-width="2"/>'
                 f'<text x="{a + nx + 12:.1f}" y="{b + ny - 4:.1f}" fill="#c0392b">{t("N")}</text>'
                 f'<text x="{a - nx - 14:.1f}" y="{b - ny + 14:.1f}" fill="#7a5233">{t("S")}</text>'
                 f'<text x="{a + ex + 8:.1f}" y="{b + ey + 12:.1f}" fill="#7a5233">{t("E")}</text>'
                 f'<text x="{a - ex - 18:.1f}" y="{b - ey + 2:.1f}" fill="#7a5233">{t("W")}</text></g>')

    # ---------- sliding gate with motor (inside the east wall) ----------
    line((16.35, -2.6, .02), (16.35, 7.9, .02), "#5a4a3c", 3)                                   # rail
    gy0, gy1 = 1.6, 5.8                                                                          # half-open gate
    poly([(16.35, gy0, .12), (16.35, gy1, .12), (16.35, gy1, 1.55), (16.35, gy0, 1.55)], "rgba(59,42,32,.08)")
    line((16.35, gy0, .12), (16.35, gy1, .12), "#3b2a20", 4); line((16.35, gy0, 1.55), (16.35, gy1, 1.55), "#3b2a20", 4)
    line((16.35, gy0, .85), (16.35, gy1, .85), "#3b2a20", 2.5)
    k = 0
    yy = gy0
    while yy <= gy1 + 1e-6:
        line((16.35, yy, .12), (16.35, yy, 1.55), "#3b2a20", 2.4)
        a, b = P(16.35, yy, 1.62)
        parts.append(f'<path d="M{a - 3:.1f} {b + 3:.1f} L{a:.1f} {b - 6:.1f} L{a + 3:.1f} {b + 3:.1f} Z" fill="#3b2a20"/>')
        yy += .35
    box(15.6, 16.15, 6.25, 7.05, 0, .62, "#7d9aa6", "#4f6d7a", "#3f5965")                      # motor
    a, b = P(15.88, 6.65, .66)
    parts.append(f'<text x="{a:.1f}" y="{b - 4:.1f}" text-anchor="middle" font-family="{ff()}" font-size="11" font-weight="800" fill="#2e4550">M</text>')

    tree(-1.2, -1.6, 4.4, 2.0)
    # ---------- near boundary walls (south, east) with gate opening ----------
    box(-3, 17, -4, -3.75, 0, 1.5, "#e1b892", "#b5643a", "#94512f")
    for k in range(13):                                                                          # brick courses (south)
        line((-3, -4, .2 + k * .1), (17, -4, .2 + k * .1), "rgba(120,50,20,.18)", .8)
    box(16.75, 17, -4, 1.4, 0, 1.5, "#e1b892", "#b5643a", "#94512f")
    box(16.75, 17, 8.2, 12, 0, 1.5, "#e1b892", "#b5643a", "#94512f")
    pillar(-3, -4); pillar(6.5, -4); pillar(17, -4); pillar(17, 1.4); pillar(17, 8.2)

    # ---------- ground labels ----------
    ground_text(8.5, -5.4, t("south"), 20, "#8b5a34", "x")
    ground_text(18.6, 4.6, t("east_entrance"), 16, "#f3e7d3", "y")

    # ---------- callout badges ----------
    badge(8.2, 4.6, H + 1.6, 1, 10, -46)        # solar panels
    badge(2.8, 8.0, H + 4.2, 2, -10, -34)       # water tank / stair room
    badge(X1, 5.2, 2.9, 3, 30, -40)             # entrance door
    badge(17, -4, 2.45, 4, 0, -40)              # boundary wall light
    badge(16.35, 3.7, 1.7, 5, 30, -40)          # sliding gate
    badge(X1 + 1.25, 10.0, F1 + 1.0, 9, 42, -16)    # north balcony
    badge(15.88, 6.65, .7, 6, 34, -14)          # gate motor
    badge(X1 + .05, 4.15, 2.4, 7, 34, 10)       # door light
    badge(4.68, 6.3, H + .7, 8, -40, -14)       # DC conduit


def build_svg():
    build_iso()
    xs = [p[0] for p in pts_seen]; ys = [p[1] for p in pts_seen]
    # crop to the plot and its near surroundings
    x0, x1 = P(-5, -8.5)[0] - 10, P(22, 13)[0]
    y0, y1 = P(-3, 17, 4.6)[1] - 170, P(19, -8)[1]
    del pts_seen[:]
    w, h = x1 - x0, y1 - y0
    sun_x, sun_y = x0 + 130, y0 + 110
    sky = (f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#sky)"/>'
           f'<g transform="translate({sun_x:.1f} {sun_y:.1f})"><circle r="44" fill="#f7b733"/><circle r="64" fill="#f7b733" opacity=".18"/>'
           + "".join(f'<line x1="{math.cos(a) * 54:.1f}" y1="{math.sin(a) * 54:.1f}" x2="{math.cos(a) * 74:.1f}" y2="{math.sin(a) * 74:.1f}" stroke="#f0a020" stroke-width="5" stroke-linecap="round"/>' for a in [i * math.pi / 6 for i in range(12)])
           + f'<text y="104" text-anchor="middle" font-family="{ff()}" font-size="17" font-weight="800" fill="#a25a1c">{t("sun")}</text></g>')
    defs = ('<defs><radialGradient id="glow"><stop offset="0" stop-color="#ffe9a0" stop-opacity=".95"/><stop offset=".45" stop-color="#ffd36b" stop-opacity=".45"/><stop offset="1" stop-color="#ffd36b" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbe3c3"/><stop offset=".55" stop-color="#fdf3e4"/><stop offset="1" stop-color="#f6ead6"/></linearGradient>'
            '<marker id="ah" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#a25a1c"/></marker></defs>')
    # sunlight arrow towards the panels
    pa, pb = P(8.0, 2.3, 7.5)
    arrow = (f'<path d="M{sun_x + 70:.1f} {sun_y + 40:.1f} Q{(sun_x + pa) / 2:.1f} {sun_y - 10:.1f} {pa - 30:.1f} {pb - 50:.1f}" fill="none" stroke="#a25a1c" stroke-width="2.5" stroke-dasharray="7 7" marker-end="url(#ah)"/>'
             f'<text x="{sun_x + 100:.1f}" y="{sun_y - 34:.1f}" font-family="{ff()}" font-size="17" font-weight="800" fill="#a25a1c">{t("panels_face")}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">{defs}{sky}{"".join(parts)}{arrow}</svg>'


# ---------------------------------------------------------------------------------------------
# Section view: everything inside runs on DC
# ---------------------------------------------------------------------------------------------
def section_svg():
    """Two-storey section, looking west (south on the left). The ground floor is drawn in local
    coordinates and shifted down one storey; the first floor and roof use the global frame."""
    W, Hh = 1840, 840
    G = 276                                    # one storey, in px
    gy = 470                                   # local ground line used by the ground-floor drawing
    L, R, top = 200, 1500, 190                 # first-floor ceiling sits under the roof slab at `top`
    g = []
    a = g.append
    FONT = f'font-family="{ff()}"'
    a('<defs><radialGradient id="g2"><stop offset="0" stop-color="#ffe9a0" stop-opacity=".9"/><stop offset="1" stop-color="#ffd36b" stop-opacity="0"/></radialGradient>'
      '<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe7a3" stop-opacity=".75"/><stop offset="1" stop-color="#ffe7a3" stop-opacity="0"/></linearGradient></defs>')
    a(f'<rect width="{W}" height="{Hh}" fill="#fdf6ea"/>')
    a(f'<rect y="{gy + G}" width="{W}" height="{Hh - gy - G}" fill="#e4cfa9"/>')
    a('<g transform="translate(70 70)"><circle r="30" fill="#f7b733"/>' + "".join(f'<line x1="{math.cos(t) * 38:.1f}" y1="{math.sin(t) * 38:.1f}" x2="{math.cos(t) * 52:.1f}" y2="{math.sin(t) * 52:.1f}" stroke="#f0a020" stroke-width="4" stroke-linecap="round"/>' for t in [i * math.pi / 6 for i in range(12)]) + '</g>')
    a(f'<text x="70" y="150" text-anchor="middle" {FONT} font-size="15" font-weight="800" fill="#a25a1c">{t("south")}</text>')
    a(f'<text x="{W - 60}" y="150" text-anchor="middle" {FONT} font-size="15" font-weight="800" fill="#7a5233">{t("north")}</text>')

    # ---------- shell: two storeys, floor slab, roof, balcony ----------
    a(f'<rect x="{L - 10}" y="{gy + G - 26}" width="{R - L + 20}" height="26" fill="#8c4a2b"/>')                       # plinth
    a(f'<rect x="{L}" y="{top}" width="{R - L}" height="{gy + G - 26 - top}" fill="#f6e3c6" stroke="#b97a45" stroke-width="10"/>')
    a(f'<rect x="{L - 10}" y="{top - 22}" width="{R - L + 20}" height="22" fill="#c18a54"/>')                          # roof slab
    a(f'<rect x="{L - 10}" y="{top - 70}" width="16" height="50" fill="#dc9e5f"/><rect x="{R - 6}" y="{top - 70}" width="16" height="50" fill="#dc9e5f"/>')
    a(f'<rect x="{L - 10}" y="{gy - 26}" width="{R - L + 170}" height="22" fill="#c18a54"/>')                           # first-floor slab + north balcony
    # north balcony: railing, plant, door from the north bedroom and a DC wall light
    for k in range(6):
        a(f'<rect x="{R + 14 + k * 26}" y="{gy - 26 - 60}" width="6" height="60" fill="#8a5530"/>')
    a(f'<rect x="{R + 10}" y="{gy - 26 - 66}" width="150" height="8" rx="3" fill="#6b4226"/>')
    a(f'<rect x="{R + 90}" y="{gy - 26 - 32}" width="30" height="32" fill="#c46a3e"/><ellipse cx="{R + 105}" cy="{gy - 26 - 38}" rx="22" ry="16" fill="#6f8a3e"/>')
    a(f'<rect x="{R - 5}" y="{gy - 26 - 150}" width="10" height="150" fill="#8a5530"/>')
    a(f'<rect x="{R + 8}" y="{top + 100}" width="22" height="16" rx="4" fill="#fff1c4" stroke="#e6b800" stroke-width="2"/><circle cx="{R + 19}" cy="{top + 108}" r="34" fill="url(#g2)"/>')
    a(f'<path d="M1300 214 H{R + 14} V{top + 100}" fill="none" stroke="#d93025" stroke-width="2.5"/><path d="M1290 224 H{R + 22} V{top + 100}" fill="none" stroke="#2b2b2b" stroke-width="2.5"/>')
    a(f'<text x="{R + 85}" y="{gy - 26 - 80}" text-anchor="middle" {FONT} font-size="13" font-weight="800" fill="#7a5233">{t("north_balcony")}</text>')

    # ---------- roof: stair room, tank, south-facing panels ----------
    a(f'<rect x="1390" y="{top - 22 - 100}" width="{R - 1390}" height="100" fill="#efd2a6" stroke="#b97a45" stroke-width="6"/>')
    a(f'<rect x="1405" y="{top - 22 - 150}" width="80" height="48" rx="10" fill="#2f2f2f"/>')
    a(f'<text x="1445" y="{top - 22 - 120}" text-anchor="middle" {FONT} font-size="11" font-weight="700" fill="#cfcfcf">{t("tank")}</text>')
    for x in (260, 600, 940):
        a(f'<line x1="{x + 20}" y1="{top - 22}" x2="{x + 20}" y2="{top - 52}" stroke="#5a6570" stroke-width="5"/>'
          f'<line x1="{x + 250}" y1="{top - 22}" x2="{x + 250}" y2="{top - 120}" stroke="#5a6570" stroke-width="5"/>'
          f'<polygon points="{x},{top - 46} {x + 270},{top - 126} {x + 276},{top - 112} {x + 6},{top - 32}" fill="#22426a" stroke="#8ea4bd" stroke-width="2"/>')
    a(f'<text x="735" y="{top - 140}" text-anchor="middle" {FONT} font-size="15" font-weight="800" fill="#22426a">{t("panels_tilted")}</text>')

    # ---------- shared drawing helpers (local coordinates: ceiling bus at 214/224, floor at gy - 26) ----------
    def drop(x, y2):
        a(f'<path d="M{x} 214 V{y2}" stroke="#d93025" stroke-width="2.5"/><path d="M{x + 7} 224 V{y2}" stroke="#2b2b2b" stroke-width="2.5"/>')

    def led(x):
        drop(x, 236)
        a(f'<polygon points="{x - 140},{gy - 30} {x + 147},{gy - 30} {x + 22},242 {x - 15},242" fill="url(#beam)"/>'
          f'<rect x="{x - 22}" y="234" width="51" height="10" rx="4" fill="#e6b800"/>')

    def fan(x):
        drop(x, 262)
        a(f'<rect x="{x - 2}" y="236" width="10" height="28" fill="#0fa3b1"/>'
          f'<ellipse cx="{x + 3}" cy="268" rx="70" ry="7" fill="#0fa3b1" opacity=".85"/><circle cx="{x + 3}" cy="268" r="12" fill="#0b7f8a"/>')

    def panel(x, y, col, w=26, h=36):
        a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#fff" stroke="{col}" stroke-width="2.5"/>')

    def touch(x, y):
        drop(x + 14, y); panel(x, y, "#8a4fd8")
        a(f'<circle cx="{x + 13}" cy="{y + 12}" r="5" fill="#8a4fd8"/><rect x="{x + 5}" y="{y + 24}" width="16" height="4" rx="2" fill="#8a4fd8"/>')

    def switch(x, y):
        drop(x + 14, y); panel(x, y, "#607d8b")
        a(f'<rect x="{x + 6}" y="{y + 6}" width="6" height="12" rx="1" fill="#607d8b"/><rect x="{x + 14}" y="{y + 20}" width="6" height="12" rx="1" fill="#607d8b"/>')

    def socket(x, y):
        drop(x + 14, y); panel(x, y, "#e0447b", 26, 26)
        a(f'<rect x="{x + 6}" y="{y + 8}" width="14" height="4" rx="2" fill="#e0447b"/><circle cx="{x + 9}" cy="{y + 18}" r="2" fill="#e0447b"/><circle cx="{x + 17}" cy="{y + 18}" r="2" fill="#e0447b"/>')

    def bed(x, w=180):
        fl = gy - 26
        a(f'<rect x="{x}" y="{fl - 40}" width="{w}" height="40" rx="6" fill="#d9b48a"/><rect x="{x}" y="{fl - 52}" width="36" height="16" rx="5" fill="#f1e3cf"/>'
          f'<rect x="{x - 8}" y="{fl - 78}" width="10" height="78" rx="3" fill="#a86a45"/>')

    def desk_laptop(x):
        fl = gy - 26
        a(f'<rect x="{x}" y="{fl - 74}" width="150" height="10" fill="#a86a45"/><rect x="{x + 10}" y="{fl - 64}" width="8" height="64" fill="#a86a45"/><rect x="{x + 132}" y="{fl - 64}" width="8" height="64" fill="#a86a45"/>'
          f'<rect x="{x + 50}" y="{fl - 108}" width="56" height="34" rx="3" fill="#3f6f9a" stroke="#2b2b2b" stroke-width="3"/><rect x="{x + 42}" y="{fl - 76}" width="72" height="4" fill="#2b2b2b"/>')

    def room_labels(names):
        xs = [(L + 620) / 2, (620 + 1000) / 2, (1000 + 1290) / 2, (1290 + R) / 2]
        for name, cx in zip(names, xs):
            a(f'<text x="{cx}" y="{gy - 8}" text-anchor="middle" {FONT} font-size="14" font-weight="800" letter-spacing="{ls(2)}" fill="#f6e3c6">{name}</text>')

    def partitions():
        for x in (620, 1000, 1290):
            a(f'<rect x="{x - 6}" y="{top}" width="12" height="{gy - 26 - top}" fill="#d9a066"/>')

    # ================= FIRST FLOOR (global frame) =================
    partitions()
    room_labels([t("bedroom"), t("family_room"), t("staircase"), t("bedroom")])
    # riser from the DC board below, then the first-floor ceiling bus
    a(f'<path d="M1300 {214 + G} V214 H230" fill="none" stroke="#d93025" stroke-width="3.5"/><path d="M1290 {224 + G} V224 H230" fill="none" stroke="#2b2b2b" stroke-width="3.5"/>')
    # bedroom with balcony door
    led(330); fan(470); switch(546, 330); socket(580, 380); bed(380)
    # family room
    led(740); fan(880); touch(636, 330); socket(946, 372); desk_laptop(830)
    a(f'<path d="M959 {372 + 13} C930 {372 + 23} 930 {gy - 26 - 90} 940 {gy - 26 - 80}" fill="none" stroke="#e0447b" stroke-width="2.5"/>')
    # staircase (centre-north) with the DC riser alongside
    steps = " ".join(f"L{1020 + i * 24} {gy - 26 - i * 23} L{1020 + (i + 1) * 24} {gy - 26 - i * 23}" for i in range(10))
    a(f'<path d="M1020 {gy - 26} {steps} L{1020 + 10 * 24} {gy - 26} Z" fill="#d9a066" opacity=".75"/>')
    led(1080)
    a(f'<text x="1278" y="{top + 72}" text-anchor="end" {FONT} font-size="12" font-weight="700" fill="#b07a4c">{t("riser_1")}</text><text x="1278" y="{top + 88}" text-anchor="end" {FONT} font-size="12" font-weight="700" fill="#b07a4c">{t("riser_2")}</text>')
    # north bedroom opening onto the north balcony
    a(f'<path d="M1300 214 H1480" stroke="#d93025" stroke-width="3.5"/><path d="M1300 224 H1480" stroke="#2b2b2b" stroke-width="3.5"/>')
    led(1350); fan(1420); touch(1440, 330); socket(1444, 384); bed(1350, 110)

    # ================= GROUND FLOOR (local frame, shifted down one storey) =================
    a(f'<g transform="translate(0 {G})">')
    partitions()
    room_labels([t("living_room"), t("bedroom"), t("kitchen"), t("dc_utility")])
    ux = 1310

    def dev(x, y, w, h, col, label, sub=""):
        a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{col}" stroke-width="3"/>'
          f'<text x="{x + w / 2}" y="{y + h / 2 + (0 if sub else 5)}" text-anchor="middle" {FONT} font-size="13" font-weight="800" fill="{col}">{label}</text>'
          + (f'<text x="{x + w / 2}" y="{y + h / 2 + 16}" text-anchor="middle" {FONT} font-size="11" font-weight="600" fill="#7a6a5a">{sub}</text>' if sub else ""))
    dev(ux, 214, 170, 52, "#e4572e", "MPPT", t("charge_controller"))
    dev(ux, 282, 170, 70, "#2e9e4f", t("battery"), t("with_bms"))
    dev(ux, 368, 170, 58, "#1565c0", t("dc_board"), t("distribution"))
    a('<path d="M1395 266 V282 M1395 352 V368" stroke="#d93025" stroke-width="4"/><path d="M1405 266 V282 M1405 352 V368" stroke="#2b2b2b" stroke-width="4"/>')
    a(f'<path d="M{ux} 396 H1300 V214 H230" fill="none" stroke="#d93025" stroke-width="3.5"/>'
      f'<path d="M{ux} 406 H1290 V224 H230" fill="none" stroke="#2b2b2b" stroke-width="3.5"/>')
    # living room
    led(330); fan(470)
    drop(260, 300)
    a(f'<rect x="230" y="300" width="130" height="78" rx="6" fill="#2b2b2b"/><rect x="236" y="306" width="118" height="66" rx="3" fill="#3f6f9a"/>'
      f'<rect x="250" y="{gy - 26 - 50}" width="110" height="50" fill="#a86a45"/>')
    touch(546, 330); socket(580, 380)
    a(f'<rect x="420" y="{gy - 26 - 60}" width="150" height="60" rx="14" fill="#c98e63"/><rect x="410" y="{gy - 26 - 34}" width="170" height="34" rx="10" fill="#b5743f"/>')
    # bedroom
    led(740); fan(880); switch(636, 330); socket(946, 372); desk_laptop(830); bed(670, 120)
    a(f'<path d="M959 385 C930 395 930 {gy - 26 - 90} 940 {gy - 26 - 80}" fill="none" stroke="#e0447b" stroke-width="2.5"/>')
    # kitchen
    led(1110)
    drop(1240, 300)
    a(f'<rect x="1196" y="300" width="74" height="{gy - 26 - 300}" rx="8" fill="#e8eef1" stroke="#5c6bc0" stroke-width="3"/><line x1="1196" y1="350" x2="1270" y2="350" stroke="#5c6bc0" stroke-width="2.5"/><rect x="1258" y="318" width="5" height="22" rx="2" fill="#5c6bc0"/><rect x="1258" y="362" width="5" height="30" rx="2" fill="#5c6bc0"/>')
    a(f'<rect x="1020" y="{gy - 26 - 60}" width="160" height="60" fill="#b5743f"/><rect x="1014" y="{gy - 26 - 66}" width="172" height="8" fill="#8c5a3a"/>')
    drop(1060, 268)
    a('<circle cx="1063" cy="284" r="16" fill="#fff" stroke="#0fa3b1" stroke-width="3"/><path d="M1063 272 V296 M1051 284 H1075" stroke="#0fa3b1" stroke-width="3"/>')
    # outdoor DC loads: boundary light and gate motor
    a(f'<path d="M1480 396 H{R + 40} V{gy - 190} H{R + 92} M{R + 40} {gy - 190} V{gy - 30} H{R + 200}" fill="none" stroke="#d93025" stroke-width="3"/>'
      f'<path d="M1480 406 H{R + 50} V{gy - 182} H{R + 92} M{R + 50} {gy - 182} V{gy - 22} H{R + 200}" fill="none" stroke="#2b2b2b" stroke-width="3"/>')
    bx = R + 90
    a(f'<rect x="{bx}" y="{gy - 110}" width="170" height="110" fill="#b5643a"/><rect x="{bx - 6}" y="{gy - 118}" width="182" height="10" fill="#e1b892"/>')
    a(f'<rect x="{bx + 6}" y="{gy - 180}" width="28" height="62" fill="#b0603a"/><rect x="{bx + 2}" y="{gy - 200}" width="36" height="20" rx="4" fill="#fff1c4" stroke="#e6b800" stroke-width="2"/><circle cx="{bx + 20}" cy="{gy - 190}" r="38" fill="url(#g2)"/>')
    a(f'<rect x="{bx + 110}" y="{gy - 48}" width="52" height="40" rx="6" fill="#4f6d7a"/><text x="{bx + 136}" y="{gy - 22}" text-anchor="middle" {FONT} font-size="15" font-weight="800" fill="#fff">M</text>')
    a(f'<text x="{bx + 85}" y="{gy + 30}" text-anchor="middle" {FONT} font-size="13" font-weight="800" fill="#7a5233">{t("boundary_gate")}</text>')
    a('</g>')

    # PV down-conductors from the roof through the stair core to the MPPT on the ground floor
    a(f'<path d="M1216 {top - 112} H1322 V{214 + G - 20} H1395 V{214 + G}" fill="none" stroke="#d93025" stroke-width="4"/>'
      f'<path d="M1216 {top - 102} H1312 V{214 + G - 10} H1405 V{214 + G}" fill="none" stroke="#2b2b2b" stroke-width="4"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hh}" width="{W}" height="{Hh}">{"".join(g)}</svg>'




KEY_COLOURS = ["#f39c12", "#e4572e", "#2e9e4f", "#1565c0", "#e6b800", "#0fa3b1", "#8a4fd8", "#607d8b",
               "#e0447b", "#5c6bc0", "#4f6d7a", "#b5643a"]


def page():
    iso = build_svg()
    sec = section_svg()
    legend = "".join(f'<li><span class="n">{n}</span><div><b>{h}</b><p>{d}</p></div></li>' for n, (h, d) in enumerate(t("legend"), 1))
    keys = "".join(f'<span><i style="background:{c}"></i>{k}</span>' for c, k in zip(KEY_COLOURS, t("inside")))
    script = {"en": "", "hi": "Noto Sans Devanagari", "or": "Noto Sans Oriya"}[LANG]
    serif = {"en": "", "hi": "Noto Serif Devanagari", "or": "Noto Serif Oriya"}[LANG]
    fonts = "" if LANG == "en" else f"&family={script.replace(' ', '+')}:wght@400;600;700;800&family={serif.replace(' ', '+')}:wght@500;600"
    indic = "" if LANG == "en" else f'''
  body {{ font-family: "Plus Jakarta Sans", "{script}", Arial, sans-serif; }}
  .display {{ font-family: "Fraunces", "{serif}", Georgia, serif; }}
  em {{ font-style: normal !important; }}
  .eyebrow {{ letter-spacing: 0; }}
  .lead, ol p {{ line-height: 1.6; }}'''
    return f'''<!DOCTYPE html>
<html lang="{LANG}"><head><meta charset="utf-8"><title>{t("title")}</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;1,9..144,500&family=Plus+Jakarta+Sans:wght@400;600;700;800{fonts}&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ width: 2000px; background: #ffffff; font-family: "Plus Jakarta Sans", Arial, sans-serif; color: #2b2118; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .display {{ font-family: "Fraunces", Georgia, serif; }}
  header {{ display: flex; align-items: center; gap: 40px; padding: 40px 70px 26px; border-bottom: 2px solid #efe4d4; }}
  header img {{ height: 96px; }}
  .eyebrow {{ font-size: 17px; font-weight: 800; letter-spacing: .2em; text-transform: uppercase; color: #b5643a; }}
  h1 {{ font-size: 60px; line-height: 1.04; font-weight: 600; margin-top: 6px; }}
  h1 em {{ font-style: italic; font-weight: 500; color: #2e9e4f; }}
  .lead {{ font-size: 21px; color: #6d5a49; margin-top: 10px; max-width: 1150px; line-height: 1.5; }}
  .top {{ display: grid; grid-template-columns: 1fr 470px; gap: 30px; padding: 26px 70px 0; align-items: start; }}
  .scene {{ border-radius: 28px; overflow: hidden; border: 2px solid #efe4d4; }}
  .scene svg {{ display: block; width: 100%; height: auto; }}
  ol {{ list-style: none; display: grid; gap: 14px; }}
  ol li {{ display: flex; gap: 14px; align-items: flex-start; }}
  .n {{ flex: none; width: 34px; height: 34px; border-radius: 50%; background: #1b4d36; color: #fff; font-weight: 800; display: grid; place-items: center; font-size: 16px; }}
  ol b {{ font-size: 19px; }}
  ol p {{ font-size: 15.5px; color: #6d5a49; line-height: 1.45; margin-top: 2px; }}
  .side h2, .sec h2 {{ font-size: 32px; font-weight: 600; margin-bottom: 16px; }}
  .side h2 em, .sec h2 em {{ font-style: italic; font-weight: 500; color: #b5643a; }}
  .sec {{ padding: 34px 70px 0; }}
  .sec .frame {{ border-radius: 28px; overflow: hidden; border: 2px solid #efe4d4; }}
  .sec svg {{ display: block; width: 100%; height: auto; }}
  .keys {{ display: flex; flex-wrap: wrap; gap: 10px 22px; margin-top: 18px; }}
  .keys span {{ display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; color: #4a3a2d; }}
  .keys i {{ width: 16px; height: 16px; border-radius: 4px; }}
  .enq {{ margin-top: 36px; background: #1b4d36; color: #fff; padding: 30px 70px; display: flex; align-items: center; gap: 40px; }}
  .enq h2 {{ font-size: 34px; font-weight: 600; flex: 1; line-height: 1.2; }}
  .enq h2 em {{ color: #f2c75c; font-style: italic; font-weight: 500; }}
  .enq .c {{ font-size: 21px; font-weight: 700; line-height: 1.7; }}
  .enq .c a {{ color: #fff; text-decoration: none; }}
  .enq .c small {{ color: #bfe8c9; font-size: 14px; letter-spacing: .1em; margin-left: 6px; }}
  .enq img {{ height: 110px; }}{indic}
</style></head><body>
<header>
  <img src="../logo/div/div-logo-horizontal-two-tone.svg" alt="Div (दिव्)">
  <div>
    <div class="eyebrow">{t("eyebrow")}</div>
    <h1 class="display">{t("h1")}</h1>
    <p class="lead">{t("lead")}</p>
  </div>
</header>
<div class="top">
  <div class="scene">{iso}</div>
  <div class="side"><h2 class="display">{t("see")}</h2><ol>{legend}</ol></div>
</div>
<div class="sec">
  <h2 class="display">{t("inside_h")}</h2>
  <div class="frame">{sec}</div>
  <div class="keys">{keys}<span><i style="background:linear-gradient(#d93025 50%,#2b2b2b 50%)"></i>{t("wiring")}</span></div>
</div>
<section class="enq">
  <h2 class="display">{t("enquiry")}</h2>
  <div class="c">Ameet Vikram Kothaari<small>IGBC AP</small><br>
    <a href="mailto:green@everestcomputer.com?subject=Enquiry%3A%20Solar%20DC%20home">green@everestcomputer.com</a><br>
    <a href="https://wa.me/918093066161">{t("whatsapp")} +91-8093066161</a></div>
  <img src="../logo/div/div-logo-stacked-on-dark-two-tone.svg" alt="Div (दिव्)">
</section>
</body></html>
'''


if __name__ == "__main__":
    for LANG in sys.argv[1:] or list(TEXT):
        out = HERE / ("dc-home.html" if LANG == "en" else f"dc-home-{LANG}.html")
        out.write_text(page())
        print("wrote", out)
