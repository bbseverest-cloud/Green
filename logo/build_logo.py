"""Build the logo SVGs (lettering converted to outlines, so no fonts are needed to open them).

  pip install fonttools brotli
  python3 logo/build_logo.py <fraunces.woff2> <plus-jakarta-sans.woff2>

Font files: Google Fonts Latin subsets of Fraunces (opsz 9..144, wght 600) and Plus Jakarta Sans (wght 800).
"""
import sys, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = pathlib.Path(__file__).parent
NAME = "Everest"
TAGLINE = "GREEN · SMART · SUSTAINABLE SPACES"

FOREST, GREEN, LEAF, MINT, WHITE = "#1b4d36", "#2f8a57", "#7cc38f", "#e1f1e6", "#ffffff"


def load(path, axes):
    f = TTFont(path)
    if "fvar" in f:
        present = {a.axisTag for a in f["fvar"].axes}
        f = instancer.instantiateVariableFont(f, {k: v for k, v in axes.items() if k in present})
    return f


def text_path(font, text, size, x=0.0, y=0.0, tracking=0.0):
    """Return (svg path d, advance width) for text set at `size` px with baseline at y."""
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    s = size / upm
    hmtx = font["hmtx"]
    pen = SVGPathPen(gs)
    cx = x
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None:
            continue
        tp = TransformPen(pen, (s, 0, 0, -s, cx, y))
        gs[g].draw(tp)
        cx += hmtx[g][0] * s + tracking
    return pen.getCommands(), cx - x - tracking


def mark(fill_leaf="url(#leafGrad)", cut=WHITE, cradle=LEAF, defs=True):
    """The symbol on a 100 x 100 grid: leaf, roof/peak cut, circuit vein, cradling smile."""
    d = ""
    if defs:
        d += (f'<defs><linearGradient id="leafGrad" x1="0" y1="0" x2="0.6" y2="1">'
              f'<stop offset="0" stop-color="{LEAF}"/><stop offset=".55" stop-color="{GREEN}"/>'
              f'<stop offset="1" stop-color="{FOREST}"/></linearGradient></defs>')
    d += (
        # leaf
        f'<path d="M50 6 C74 22 84 44 78 62 C73 76 62 84 50 86 C38 84 27 76 22 62 C16 44 26 22 50 6 Z" fill="{fill_leaf}"/>'
        # home: roof (also the Everest peak) and walls cut into the leaf
        f'<path d="M30 53 L50 34 L70 53" fill="none" stroke="{cut}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M37 50 V69 H63 V50" fill="none" stroke="{cut}" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>'
        # smart node inside the home, with signal arcs
        f'<circle cx="50" cy="60" r="3.8" fill="{cut}"/>'
        f'<path d="M43.5 53.5 A9 9 0 0 1 56.5 53.5" fill="none" stroke="{cut}" stroke-width="3" stroke-linecap="round"/>'
        # the leaf's vein continues below as a circuit trace ending in a node
        f'<path d="M50 69 V77" fill="none" stroke="{cut}" stroke-width="3.6" stroke-linecap="round"/>'
        f'<circle cx="50" cy="79.5" r="3" fill="{cut}"/>'
        # cradling smile: delight and care
        f'<path d="M16 80 C30 98 70 98 84 80" fill="none" stroke="{cradle}" stroke-width="6" stroke-linecap="round"/>'
    )
    return d


def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{rect}{body}</svg>\n'


def main(fraunces_path, jakarta_path):
    serif = load(fraunces_path, {"wght": 600, "opsz": 144})
    sans = load(jakarta_path, {"wght": 800})

    def lockup_h(name_col, tag_col, **mk):
        # icon 100 tall at x=0; wordmark to its right
        name_d, name_w = text_path(serif, NAME, 92, x=124, y=66, tracking=-1.5)
        tag_d, tag_w = text_path(sans, TAGLINE, 15.5, x=127, y=98, tracking=3.1)
        w = int(124 + max(name_w, tag_w + 3) + 8)
        body = (f'<g>{mark(**mk)}</g>'
                f'<path d="{name_d}" fill="{name_col}"/><path d="{tag_d}" fill="{tag_col}"/>')
        return w, 104, body

    def lockup_v(name_col, tag_col, **mk):
        name_d, name_w = text_path(serif, NAME, 88, x=0, y=0, tracking=-1.5)
        tag_d, tag_w = text_path(sans, TAGLINE, 15, x=0, y=0, tracking=3.0)
        w = int(max(name_w, tag_w) + 20)
        cx = w / 2
        body = (f'<g transform="translate({cx - 60} 0) scale(1.2)">{mark(**mk)}</g>'
                f'<path transform="translate({cx - name_w / 2} 196)" d="{name_d}" fill="{name_col}"/>'
                f'<path transform="translate({cx - tag_w / 2} 232)" d="{tag_d}" fill="{tag_col}"/>')
        return w, 244, body

    files = {}
    # primary: full colour on white
    w, h, b = lockup_h(FOREST, GREEN)
    files["everest-logo-horizontal.svg"] = svg(w, h, b)
    w, h, b = lockup_v(FOREST, GREEN)
    files["everest-logo-stacked.svg"] = svg(w, h, b)
    files["everest-icon.svg"] = svg(100, 100, mark())
    # reversed: on forest green
    rev = dict(fill_leaf=LEAF, cut=FOREST, cradle=MINT, defs=False)
    w, h, b = lockup_h(WHITE, "#bfe8c9", **rev)
    files["everest-logo-horizontal-reversed.svg"] = svg(w, h, b)
    # one colour (for stamps, embroidery, single-ink print)
    mono = dict(fill_leaf=FOREST, cut=WHITE, cradle=FOREST, defs=False)
    w, h, b = lockup_h(FOREST, FOREST, **mono)
    files["everest-logo-horizontal-mono.svg"] = svg(w, h, b)
    # app / social avatar: icon on a rounded mint tile
    files["everest-avatar.svg"] = svg(400, 400, f'<rect width="400" height="400" rx="88" fill="{MINT}"/>'
                                      f'<g transform="translate(70 62) scale(2.6)">{mark()}</g>')
    for n, s in files.items():
        (OUT / n).write_text(s)
        print("wrote", n)


if __name__ == "__main__":
    main(*sys.argv[1:3])
