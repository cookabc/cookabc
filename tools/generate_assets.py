#!/usr/bin/env python3
"""Generate the profile SVG assets (dark + light) from the Ark Pixel font.

All geometry is deterministic (fixed seed, no randomized hash ids), so
re-running reproduces the same bytes. Font: Ark Pixel 12px proportional
Latin, OFL (assets/ArkPixel-OFL.txt).

The banner's right half used to be an abstract bar chart — a generic
"analytics" motif that says nothing about the person. It is now a pixel
desk: a menu bar with a live CPU sparkline, a terminal window whose
prompt types itself, and a small stack of finished apps on a shelf.
The point of the picture is to be *about* the work, not to decorate it.
"""
import random
from xml.sax.saxutils import escape
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

FONT_PATH = "assets/ark-pixel-12px-proportional-latin.woff2"
OUT = "assets"

FONT = TTFont(FONT_PATH)
GLYPHS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
UPM = FONT["head"].unitsPerEm  # 1200 -> 100 units per 12px-grid cell

DARK = dict(
    bg="#0E1322", border="#2A3550", text="#E8ECF5", sub="#8CA0C4",
    cyan="#35D0E0", teal="#58C4A5", violet="#8B7CF6", amber="#F5B856",
)
LIGHT = dict(
    bg="#F6F4EE", border="#D8D2C4", text="#232A3A", sub="#5C6880",
    cyan="#0891B2", teal="#0E9F82", violet="#6D5BD0", amber="#C77800",
)


def scale_for(font_px: float) -> float:
    return font_px * 12.0 / UPM


def _glyph(ch: str):
    return GLYPHS[CMAP[ord(ch)]] if ord(ch) in CMAP else None


def _advance(ch: str, sc: float) -> float:
    g = _glyph(ch)
    if g is not None:
        return g.width * sc
    return (4.0 if ch == " " else 6.0) * sc  # fallback advance, grid px


def text_path(s: str, font_px: float, x: float, baseline: float) -> str:
    """SVG path d for s set in Ark Pixel; y-down, baseline at `baseline`."""
    sc = scale_for(font_px)
    parts, cx = [], x
    for ch in s:
        g = _glyph(ch)
        if g is not None:
            pen = SVGPathPen(GLYPHS)
            g.draw(TransformPen(pen, Transform(sc, 0, 0, -sc, cx, baseline)))
            d = pen.getCommands()
            if d:
                parts.append(d)
        cx += _advance(ch, sc)
    return " ".join(parts)


def meas(s: str, font_px: float) -> float:
    return sum(_advance(c, scale_for(font_px)) for c in s)


# ---------------------------------------------------------------- banner
PHRASES = [
    "menu bar apps in Swift",
    "dev tools in TypeScript",
    "local-first, pixel-clean, MIT",
    "the rest is still in the oven",
]
MONO_W = 0.6  # advance of the monospace typing line, em ratio
FS = 17.0


T_TYPE, T_HOLD, T_DEL = 0.055, 1.25, 0.028  # per-char type / hold / per-char delete


def phrase_active(n: int) -> float:
    return n * T_TYPE + T_HOLD + n * T_DEL


def typing_anim(idx: int, n: int, width: float, t0: float, total: float) -> str:
    """SMIL width animation for phrase idx's clip rect.

    Every phrase shares the same `total` cycle so the loops stay in sync:
    idle (width 0) -> type -> hold -> delete -> idle until the cycle ends.
    """
    step = width / n
    t_type_end, t_hold_end = t0 + n * T_TYPE, t0 + n * T_TYPE + T_HOLD
    times, values = [], []
    if t0 > 0:  # leading idle; a duplicated first keyTime would be invalid
        times.append(0.0)
        values.append("0")
    times.append(t0)
    values.append("0")
    for k in range(1, n + 1):
        times.append(t0 + k * T_TYPE)
        values.append(f"{step * k:.1f}")
    times.append(t_hold_end)
    values.append(f"{width:.1f}")
    for k in range(n - 1, -1, -1):
        times.append(t_hold_end + (n - k) * T_DEL)
        values.append(f"{step * k:.1f}")
    kt = ";".join(f"{min(t, total) / total:.4f}" for t in times)
    return (f'<animate attributeName="width" values="{";".join(values)}" '
            f'keyTimes="{kt}" calcMode="discrete" dur="{total:.2f}s" '
            f'repeatCount="indefinite"/>')


def banner(p: dict, tag: str) -> None:
    W, H, c = 900, 260, 14
    rand = random.Random(42)

    # ── The desk: a menu bar across the top, a terminal, and a shelf of
    #    finished apps. Everything here is a thing the profile actually
    #    ships, drawn in the same 4px grid as the wordmark.
    #
    #    The vertical budget is fixed — 260px tall, and the frame's inner
    #    edge is at 246:
    #       28 …  72   menu bar, with the live CPU curve
    #       80 … 188   the terminal window
    #      198 … 234   the shelf of finished apps
    #      234        the shelf itself
    desk = []

    # Menu bar strip along the top of the right half.
    desk.append(f'<rect x="596" y="28" width="290" height="44" fill="{p["border"]}" opacity="0.45"/>')

    # A small app glyph in the menu bar — the Vitals status item.
    desk.append(f'<rect x="604" y="40" width="8" height="8" fill="{p["teal"]}"/>')

    # The live CPU sparkline: a curve of bars rising from a baseline, the
    # way the Vitals menu bar item draws it. The bars are tall enough to
    # read as a graph — a row of 5px stubs just looks like dashes.
    pts = [7, 11, 9, 15, 12, 19, 14, 22, 16, 20, 13, 18, 16, 24, 18, 28, 20, 26, 17, 30]
    step = 13
    baseline = 68
    spark = []
    for i, v in enumerate(pts):
        x = 622 + i * step
        spark.append(
            f'<rect x="{x}" y="{baseline - v}" width="9" height="{v}" fill="{p["cyan"]}" '
            f'opacity="{0.4 + 0.6 * (i / (len(pts) - 1)):.2f}"/>'
        )
    desk.append(f'<g>{"".join(spark)}</g>')
    desk.append(f'<rect x="620" y="{baseline}" width="268" height="2" fill="{p["border"]}"/>')

    # The terminal window: a titled bar, a prompt, and a cursor.
    tx, ty, tw, th = 604, 80, 268, 108
    desk.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="{p["bg"]}" stroke="{p["border"]}" stroke-width="2"/>')
    desk.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="16" fill="{p["border"]}" opacity="0.6"/>')
    for i, col in enumerate([p["cyan"], p["amber"], p["teal"]]):
        desk.append(f'<rect x="{tx + 6 + i * 11}" y="{ty + 5}" width="6" height="6" fill="{col}"/>')
    desk.append(
        f'<path d="{text_path("terminal", 2.0, tx + 48, ty + 12)}" fill="{p["sub"]}" opacity="0.85"/>'
    )
    # Three prompt lines, typed on one after another.
    lines = ["$ swift build", "$ pnpm test", "$ git push"]
    for i, line in enumerate(lines):
        x = tx + 10
        y = ty + 36 + i * 22
        col = [p["teal"], p["teal"], p["cyan"]][i]
        desk.append(f'<path d="{text_path(line, 2.0, x, y)}" fill="{col}"/>')
        cursor_w = meas(line, 2.0) + 4
        desk.append(
            f'<rect x="{x + cursor_w:.0f}" y="{y - 8}" width="7" height="10" fill="{p["amber"]}">'
            f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.45;.5;.95;1" '
            f'calcMode="discrete" dur="1.1s" begin="{0.3 * i:.1f}s" repeatCount="indefinite"/></rect>'
        )

    # The shelf: three finished apps as small windows on a stand.
    shelf_y = 234
    desk.append(f'<rect x="596" y="{shelf_y}" width="290" height="4" fill="{p["border"]}"/>')
    apps = [
        # (x, w, colour, window height, bars)
        (606, 76, p["violet"], 36, 2),
        (700, 80, p["teal"], 30, 2),
        (798, 74, p["amber"], 36, 2),
    ]
    for i, (ax, aw, col, ah, rows) in enumerate(apps):
        ay = shelf_y - ah
        desk.append(
            f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="{p["bg"]}" '
            f'stroke="{p["border"]}" stroke-width="2"/>'
        )
        desk.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="9" fill="{col}"/>')
        # Inside: a couple of content lines that blink, as if it is live.
        for r in range(rows):
            ry = ay + 17 + r * 10
            w = aw - 18 - (r * 6)
            desk.append(
                f'<rect x="{ax + 9}" y="{ry}" width="{w}" height="4" fill="{col}" opacity="0.55">'
                f'<animate attributeName="opacity" values="0.25;0.25;0.7;0.7;0.25" '
                f'keyTimes="0;.2;.4;.6;.8" calcMode="discrete" dur="{1.4 + i * 0.35:.2f}s" '
                f'begin="{0.25 * i:.2f}s" repeatCount="indefinite"/></rect>'
            )

    # A tiny sleeping cat on the shelf, because the desk is a desk.
    cx, cy = 884, shelf_y - 4
    desk.append(f'<rect x="{cx - 9}" y="{cy - 15}" width="18" height="12" fill="{p["violet"]}" opacity="0.85"/>')
    desk.append(f'<rect x="{cx - 9}" y="{cy - 19}" width="5" height="5" fill="{p["violet"]}" opacity="0.85"/>')
    desk.append(f'<rect x="{cx + 4}" y="{cy - 19}" width="5" height="5" fill="{p["violet"]}" opacity="0.85"/>')
    desk.append(
        f'<rect x="{cx + 3}" y="{cy - 10}" width="2" height="2" fill="{p["bg"]}">'
        f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.55;.6;.95;1" '
        f'calcMode="discrete" dur="2.6s" repeatCount="indefinite"/></rect>'
    )

    stars = []

    groups = []
    cw = FS * MONO_W
    cycle = sum(phrase_active(len(ph)) for ph in PHRASES)
    t0 = 0.0
    for i, ph in enumerate(PHRASES):
        anim = typing_anim(i, len(ph), len(ph) * cw, t0, cycle)
        t0 += phrase_active(len(ph))
        groups.append(
            f'<g clip-path="url(#tp{i})">'
            f'<clipPath id="tp{i}"><rect x="92" y="168" width="0" height="26">{anim}</rect></clipPath>'
            f'<text x="92" y="188" font-family="ui-monospace,Menlo,monospace" font-size="{FS}" '
            f'fill="{p["sub"]}">{escape(ph)}</text></g>')

    word = text_path("cookabc", 8, 56, 128)
    wend = 56 + meas("cookabc", 8)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="cookabc - small, finished tools for the Mac and the editor">
<!-- wordmark set in Ark Pixel 12 (OFL, assets/ArkPixel-OFL.txt); regenerate with tools/generate_assets.py -->
<style>.cur{{animation:b 1.1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}</style>
<defs><clipPath id="tw"><rect width="{W}" height="{H}"/></clipPath></defs>
<path d="M {c},1 H {W - c} L {W - 1},{c} V {H - c} L {W - c},{H - 1} H {c} L 1,{H - c} V {c} Z"
      fill="{p["bg"]}" stroke="{p["border"]}" stroke-width="2"/>
<g clip-path="url(#tw)">{"".join(stars)}</g>
<path d="{word}" fill="{p["text"]}"/>
<rect class="cur" x="{wend + 14:.0f}" y="68" width="16" height="64" fill="{p["cyan"]}"/>
<rect x="56" y="168" width="12" height="22" fill="{p["cyan"]}">
  <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.49;.5;.99;1" calcMode="discrete" dur="1.1s" repeatCount="indefinite"/>
</rect>
{"".join(groups)}
{"".join(desk)}
</svg>'''
    with open(f"{OUT}/banner-{tag}.svg", "w") as f:
        f.write(svg)


# ---------------------------------------------------------------- section headers
# Each section gets an icon that says what the section is about, rather
# than the same square for all four. The icon animates on its own clock.
HEADERS = [
    ("hdr-menubar", "ON THE MENU BAR", "menubar"),
    ("hdr-browser", "IN THE BROWSER", "browser"),
    ("hdr-editor", "IN THE EDITOR", "editor"),
    ("hdr-activity", "STACK & ACTIVITY", "activity"),
]


def header_icon(p: dict, kind: str) -> str:
    """A 16×16 pixel mark for the section, drawn on the same 4px grid."""
    c = p["cyan"]
    if kind == "menubar":
        # A menu bar: a strip with one live status item.
        return (
            f'<rect x="7" y="18" width="18" height="14" fill="{p["text"]}" opacity="0.2"/>'
            f'<rect x="7" y="18" width="18" height="4" fill="{p["text"]}" opacity="0.45"/>'
            f'<rect x="9" y="20" width="5" height="1" fill="{c}"/>'
            f'<rect x="19" y="24" width="4" height="6" fill="{c}"/>'
            f'<rect x="19" y="24" width="4" height="6" fill="{c}" opacity="0.4">'
            f'<animate attributeName="height" values="6;2;6;4;6" keyTimes="0;.25;.5;.75;1" '
            f'calcMode="discrete" dur="2.2s" repeatCount="indefinite"/></rect>'
        )
    if kind == "browser":
        # A browser window with a loading bar that fills and empties.
        return (
            f'<rect x="7" y="16" width="18" height="16" fill="{p["text"]}" opacity="0.2"/>'
            f'<rect x="7" y="16" width="18" height="4" fill="{p["text"]}" opacity="0.45"/>'
            f'<rect x="9" y="24" width="14" height="2" fill="{c}">'
            f'<animate attributeName="width" values="2;14;2;14;2" keyTimes="0;.25;.5;.75;1" '
            f'calcMode="discrete" dur="2.6s" repeatCount="indefinite"/></rect>'
        )
    if kind == "editor":
        # A code caret that blinks.
        return (
            f'<rect x="7" y="16" width="18" height="16" fill="{p["text"]}" opacity="0.2"/>'
            f'<path d="M13 20 L9 24 L13 28" fill="none" stroke="{c}" stroke-width="2"/>'
            f'<path d="M19 20 L23 24 L19 28" fill="none" stroke="{c}" stroke-width="2"/>'
            f'<rect x="15" y="22" width="2" height="5" fill="{c}">'
            f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.45;.5;.95;1" '
            f'calcMode="discrete" dur="1.1s" repeatCount="indefinite"/></rect>'
        )
    # activity: a stack of bars, like the commit graph.
    return (
        f'<rect x="7" y="16" width="18" height="16" fill="{p["text"]}" opacity="0.2"/>'
        f'<rect x="9" y="25" width="4" height="5" fill="{c}"/>'
        f'<rect x="14" y="21" width="4" height="9" fill="{c}"/>'
        f'<rect x="19" y="18" width="4" height="12" fill="{c}">'
        f'<animate attributeName="height" values="12;6;12;9;12" keyTimes="0;.25;.5;.75;1" '
        f'calcMode="discrete" dur="1.8s" repeatCount="indefinite"/></rect>'
    )


def header(p: dict, tag: str, name: str, text: str, kind: str) -> None:
    S = 3.0
    tx = 34
    w = tx + meas(text, S)
    W = int(w + 84)
    dots = "".join(
        f'<rect x="{w + 22 + i * 12:.0f}" y="24" width="6" height="6" fill="{p["cyan"]}" opacity="0">'
        f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;.2;.4;.6;.8;1"'
        f' calcMode="discrete" dur="1.8s" begin="{i * 0.3:.1f}s" repeatCount="indefinite"/></rect>'
        for i in range(5))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="48" viewBox="0 0 {W} 48" role="img" aria-label="{escape(text.title())}">
{header_icon(p, kind)}
<path d="{text_path(text, S, tx, 37)}" fill="{p["text"]}"/>
{dots}
</svg>'''
    with open(f"{OUT}/{name}-{tag}.svg", "w") as f:
        f.write(svg)


# ---------------------------------------------------------------- footer
def footer(p: dict, tag: str) -> None:
    S = 2.0
    text = "THE REST IS PRIVATE OR STILL IN THE OVEN"
    tw = meas(text, S)
    W, x0 = 900, (900 - tw) / 2
    flank = lambda dx, i, back: (
        f'<rect x="{x0 + dx + (i if dx > 0 else -i) * 14:.0f}" y="28" width="6" height="6" '
        f'fill="{p["sub"]}" opacity="0"><animate attributeName="opacity" values="0;0;1;0;0" '
        f'keyTimes="0;.2;.4;.6;.8;1" calcMode="discrete" dur="1.5s" begin="{((3 - i) if back else i) * 0.3:.1f}s" '
        f'repeatCount="indefinite"/></rect>')
    left = "".join(flank(-30, i, True) for i in range(4))
    right = "".join(flank(tw + 24, i, False) for i in range(4))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="60" viewBox="0 0 {W} 60" role="img" aria-label="the rest is private or still in the oven">
{left}{right}
<path d="{text_path(text, S, x0, 38)}" fill="{p["sub"]}"/>
</svg>'''
    with open(f"{OUT}/footer-{tag}.svg", "w") as f:
        f.write(svg)


if __name__ == "__main__":
    for p, tag in ((DARK, "dark"), (LIGHT, "light")):
        banner(p, tag)
        for name, text, kind in HEADERS:
            header(p, tag, name, text, kind)
        footer(p, tag)
    print("assets regenerated")
