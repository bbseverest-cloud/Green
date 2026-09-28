"""Build the Div (दिव्) logo set as SVG, with all lettering converted to outlines.

  pip install fonttools brotli uharfbuzz
  python3 logo/build_div_logo.py <tiro-devanagari-sanskrit-devanagari.woff2> <tiro-devanagari-sanskrit-latin.woff2>

Font: Tiro Devanagari Sanskrit (Google Fonts, SIL Open Font License). HarfBuzz shapes the Devanagari
so the ि matra is reordered before द and the halant sits correctly under व.
"""
import io, sys, pathlib
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

OUT = pathlib.Path(__file__).parent / "div"
NAME_DEVA = "दिव्"
NAME_LATIN = "DIV"
TAGLINE = "SHINE · ILLUMINE · RADIATE"

# colour schemes: (vessel & lettering, light: flame & rays, tagline, background)
SCHEMES = {
    "two-tone":          ("#1b4d36", "#e3a21a", "#2f8a57", None),
    "green":             ("#1b4d36", "#1b4d36", "#1b4d36", None),
    "gold":              ("#b9780f", "#b9780f", "#b9780f", None),
    "black":             ("#141414", "#141414", "#141414", None),
    "reversed-two-tone": ("#ffffff", "#f2b938", "#bfe8c9", "#1b4d36"),
    "reversed-white":    ("#ffffff", "#ffffff", "#ffffff", "#1b4d36"),
}


class Face:
    def __init__(self, path):
        self.tt = TTFont(path)
        self.tt.flavor = None
        buf = io.BytesIO()
        self.tt.save(buf)
        self.hbfont = hb.Font(hb.Face(buf.getvalue()))
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upm = self.tt["head"].unitsPerEm

    def shape(self, text, size, tracking=0.0):
        """Return (svg path d, (xmin, ymin, xmax, ymax)) with the baseline at y=0 and origin at x=0."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {})
        s = size / self.upm
        pen = SVGPathPen(self.gs)
        bpen = BoundsPen(self.gs)
        x = 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = self.order[info.codepoint]
            t = (s, 0, 0, -s, x + pos.x_offset * s, -pos.y_offset * s)
            self.gs[name].draw(TransformPen(pen, t))
            self.gs[name].draw(TransformPen(bpen, t))
            x += pos.x_advance * s + (tracking if pos.x_advance else 0)
        return pen.getCommands(), bpen.bounds


def ellipse(cx, cy, rx, ry):
    return f"M{cx - rx} {cy} A{rx} {ry} 0 1 0 {cx + rx} {cy} A{rx} {ry} 0 1 0 {cx - rx} {cy} Z"


# shading for the moulded lamp (None = single colour, mouldings separated by thin gaps instead)
SHADES = {
    "two-tone": dict(rim="#3f8d65", well="#0f2f21", lip="#1b4d36", top="#27654a", bot="#123a2a",
                     hi="#5aa57e", bead="#3f8d65", base="#1b4d36"),
    "reversed-two-tone": dict(rim="#ffffff", well="#1b4d36", lip="#d3ecdc", top="#f4fbf6", bot="#c9e6d3",
                              hi="#ffffff", bead="#ffffff", base="#d3ecdc"),
}


def mark(ink, light, shade=None, uid="d"):
    """Diya on a 100 x 100 grid: flame (shine), moulded lamp (illumine), rays (radiate)."""
    import math
    rays = []
    cx, cy = 50, 43
    for ang in (180, 212, 244, 296, 328, 360):
        a = math.radians(ang)
        r1, r2 = 25, 34
        rays.append(f"M{cx + r1 * math.cos(a):.2f} {cy + r1 * math.sin(a):.2f} L{cx + r2 * math.cos(a):.2f} {cy + r2 * math.sin(a):.2f}")
    ray_svg = f'<path d="{" ".join(rays)}" fill="none" stroke="{light}" stroke-width="4.6" stroke-linecap="round"/>'
    flame = (f'<path fill-rule="evenodd" fill="{light}" d="M50 12 C60 25 66 36 66 45 C66 54 59 60 50 60 C41 60 34 54 34 45 C34 36 40 25 50 12 Z '
             f'M50 33 C54 39 56.5 43 56.5 47 C56.5 51 53.5 54 50 54 C46.5 54 43.5 51 43.5 47 C43.5 43 46 39 50 33 Z"/>')
    rim_ring = f'{ellipse(50, 61, 40, 7)} {ellipse(50, 61.6, 33, 4.4)}'
    base = "M32 97.6 C32 95.8 39 95.2 50 95.2 C61 95.2 68 95.8 68 97.6 C68 99 61 99.5 50 99.5 C39 99.5 32 99 32 97.6 Z"
    neck = "M42.5 86.5 H57.5 L55.5 93 H44.5 Z"
    if shade:
        sh = shade
        return (
            f'<defs><linearGradient id="{uid}Body" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{sh["top"]}"/><stop offset="1" stop-color="{sh["bot"]}"/></linearGradient></defs>'
            + ray_svg
            # top moulding: rim face with the oil well, the flame rising from the well, then the rim's front lip
            + f'<path fill-rule="evenodd" fill="{sh["rim"]}" d="{rim_ring}"/>'
            + f'<path fill="{sh["well"]}" d="{ellipse(50, 61.6, 33, 4.4)}"/>'
            + flame
            + f'<path fill="{sh["lip"]}" d="M10 61 A40 7 0 0 0 90 61 L90 64.6 A40 7 0 0 1 10 64.6 Z"/>'
            # neck, then bowl
            + f'<path fill="{sh["bot"]}" d="{neck}"/>'
            + f'<path fill="url(#{uid}Body)" d="M11.6 64.6 C13 80 30 88.6 50 88.6 C70 88.6 87 80 88.4 64.6 A38.4 7 0 0 1 11.6 64.6 Z"/>'
            + f'<path d="M21 72 C24 79 30 83.5 37 85.5" fill="none" stroke="{sh["hi"]}" stroke-width="2" stroke-linecap="round" opacity=".55"/>'
            # bottom moulding: bead ring and base plate
            + f'<path fill="{sh["bead"]}" d="{ellipse(50, 93, 12.5, 2.4)}"/>'
            + f'<path fill="{sh["base"]}" d="{base}"/>'
        )
    # single colour: the same mouldings, separated by thin gaps
    return (
        ray_svg
        + f'<path fill-rule="evenodd" fill="{ink}" d="{rim_ring}"/>'
        + flame
        + f'<path fill="{ink}" d="M10 62.8 A40 7 0 0 0 90 62.8 L90 65.6 A40 7 0 0 1 10 65.6 Z"/>'
        + f'<path fill="{ink}" d="{neck}"/>'
        + f'<path fill="{ink}" d="M12.4 67.4 C14 81 30.5 88.6 50 88.6 C69.5 88.6 86 81 87.6 67.4 A37.6 7 0 0 1 12.4 67.4 Z"/>'
        + f'<path fill="{ink}" d="{ellipse(50, 93.2, 12.5, 2)}"/>'
        + f'<path fill="{ink}" d="{base}"/>'
    )


def svg(w, h, body, bg=None, pad_radius=0):
    rect = f'<rect width="{w}" height="{h}" rx="{pad_radius}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">{rect}{body}</svg>\n'


def main(deva_path, latin_path):
    deva, latin = Face(deva_path), Face(latin_path)
    OUT.mkdir(exist_ok=True)

    name_d, nb = deva.shape(NAME_DEVA, 150)
    lat_d, lb = latin.shape(NAME_LATIN, 26, tracking=14)
    tag_d, tb = latin.shape(TAGLINE, 15, tracking=4.2)
    name_w = nb[2] - nb[0]
    written = []

    name_h = nb[3] - nb[1]                 # full height of दिव् including the ि loop and the halant
    lat_w, tag_w = lb[2] - lb[0], tb[2] - tb[0]
    cap_h = -lb[1]                          # height of DIV above its baseline

    for key, (ink, light, tagc, bg) in SCHEMES.items():
        pad = 34 if bg else 14
        # ---- horizontal: mark | दिव् with DIV + tagline beneath, the text block centred on the mark
        M = 200
        gap_line = 26                       # space between the Devanagari and the DIV line
        block_h = name_h + gap_line + cap_h
        top = pad + max(0, (M - block_h) / 2)
        mark_top = pad + max(0, (block_h - M) / 2)
        tx = pad + M + 26
        name_base = top - nb[1]
        line_base = top + name_h + gap_line + cap_h
        sub_w = lat_w + 22 + tag_w
        W = tx + max(nb[2] - nb[0], sub_w) + pad
        H = max(M, block_h) + 2 * pad
        body = (f'<g transform="translate({pad} {mark_top:.1f}) scale({M / 100})">{mark(ink, light, SHADES.get(key), "h")}</g>'
                f'<path transform="translate({tx - nb[0]:.1f} {name_base:.1f})" d="{name_d}" fill="{ink}"/>'
                f'<path transform="translate({tx - lb[0] + 4:.1f} {line_base:.1f})" d="{lat_d}" fill="{ink}"/>'
                f'<path transform="translate({tx - tb[0] + 4 + lat_w + 22:.1f} {line_base - 1:.1f})" d="{tag_d}" fill="{tagc}"/>')
        f = f"div-logo-horizontal-{key}.svg"
        (OUT / f).write_text(svg(W, H, body, bg, 28 if bg else 0)); written.append(f)

        # ---- stacked: mark above दिव्, DIV and tagline centred beneath
        M2 = 180
        W = max(name_w, tag_w, M2) + 2 * pad + 20
        cx = W / 2
        name_top = pad + M2 + 22
        name_base = name_top - nb[1]
        lat_base = name_top + name_h + 30 + cap_h
        tag_base = lat_base + 34
        body = (f'<g transform="translate({cx - M2 / 2:.1f} {pad}) scale({M2 / 100})">{mark(ink, light, SHADES.get(key), "s")}</g>'
                f'<path transform="translate({cx - nb[0] - name_w / 2:.1f} {name_base:.1f})" d="{name_d}" fill="{ink}"/>'
                f'<path transform="translate({cx - lb[0] - lat_w / 2:.1f} {lat_base:.1f})" d="{lat_d}" fill="{ink}"/>'
                f'<path transform="translate({cx - tb[0] - tag_w / 2:.1f} {tag_base:.1f})" d="{tag_d}" fill="{tagc}"/>')
        H = tag_base + tb[3] + pad
        f = f"div-logo-stacked-{key}.svg"
        (OUT / f).write_text(svg(W, H, body, bg, 28 if bg else 0)); written.append(f)

        # ---- icon
        f = f"div-icon-{key}.svg"
        if bg:
            (OUT / f).write_text(svg(100, 100, f'<g transform="translate(10 6) scale(.8)">{mark(ink, light, SHADES.get(key), "i")}</g>', bg, 22))
        else:
            (OUT / f).write_text(svg(100, 100, mark(ink, light, SHADES.get(key), 'i')))
        written.append(f)

    # profile picture: two-tone mark on a soft cream tile
    (OUT / "div-avatar.svg").write_text(svg(400, 400, f'<g transform="translate(60 50) scale(2.8)">{mark("#1b4d36", "#e3a21a", SHADES["two-tone"], "a")}</g>', "#fbf5e6", 88))
    written.append("div-avatar.svg")
    print("\n".join(written))


if __name__ == "__main__":
    main(*sys.argv[1:3])
