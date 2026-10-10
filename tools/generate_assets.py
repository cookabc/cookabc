#!/usr/bin/env python3
"""Generate the profile SVG assets (dark + light) from the Ark Pixel font.

All geometry is deterministic (fixed seed, no randomized hash ids), so
re-running reproduces the same bytes. Font: Ark Pixel 12px proportional
Latin, OFL (assets/ArkPixel-OFL.txt).
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

    bars = []
    bx = 640.0
    while bx < 838:
        h0 = rand.randint(28, 138)
        seq = [h0] + [rand.randint(28, 138) for _ in range(4)] + [h0]
        dur = rand.choice([1.4, 1.7, 2.0, 2.3])
        col = rand.choice([p["cyan"], p["teal"], p["violet"]])
        kt = 'keyTimes="0;.2;.4;.6;.8;1" calcMode="discrete"'
        anim = (f'<animate attributeName="height" values="{";".join(map(str, seq))}" {kt} '
                f'dur="{dur}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y" values="{";".join(str(210 - h) for h in seq)}" {kt} '
                f'dur="{dur}s" repeatCount="indefinite"/>')
        bars.append(f'<rect x="{bx:.0f}" y="{210 - h0}" width="14" height="{h0}" fill="{col}">{anim}</rect>')
        bars.append(f'<rect x="{bx:.0f}" y="210" width="14" height="3" fill="{p["border"]}"/>')
        bx += 20

    stars = []
    for i, (sx, sy) in enumerate([(604, 36), (668, 22), (726, 50), (792, 28),
                                  (852, 58), (630, 78), (700, 92), (824, 88)]):
        col = [p["cyan"], p["amber"], p["violet"], p["teal"]][i % 4]
        stars.append(
            f'<rect x="{sx}" y="{sy}" width="5" height="5" fill="{col}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;.25;.5;.75;1" '
            f'calcMode="discrete" dur="{1.8 + (i % 4) * 0.45}s" begin="{i * 0.5}s" '
            f'repeatCount="indefinite"/></rect>')

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
<g clip-path="url(#tw)">{''.join(stars)}</g>
<path d="{word}" fill="{p["text"]}"/>
<rect class="cur" x="{wend + 14:.0f}" y="68" width="16" height="64" fill="{p["cyan"]}"/>
<rect x="56" y="168" width="12" height="22" fill="{p["cyan"]}">
  <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.49;.5;.99;1" calcMode="discrete" dur="1.1s" repeatCount="indefinite"/>
</rect>
{''.join(groups)}
{''.join(bars)}
</svg>'''
    with open(f"{OUT}/banner-{tag}.svg", "w") as f:
        f.write(svg)


# ---------------------------------------------------------------- section headers
HEADERS = [
    ("hdr-menubar", "ON THE MENU BAR"),
    ("hdr-browser", "IN THE BROWSER"),
    ("hdr-editor", "IN THE EDITOR"),
    ("hdr-activity", "STACK & ACTIVITY"),
]


def header(p: dict, tag: str, name: str, text: str) -> None:
    S = 3.0
    tx = 30
    w = tx + meas(text, S)
    W = int(w + 84)
    dots = "".join(
        f'<rect x="{w + 22 + i * 12:.0f}" y="24" width="6" height="6" fill="{p["cyan"]}" opacity="0">'
        f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;.2;.4;.6;.8;1"'
        f' calcMode="discrete" dur="1.8s" begin="{i * 0.3:.1f}s" repeatCount="indefinite"/></rect>'
        for i in range(5))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="48" viewBox="0 0 {W} 48" role="img" aria-label="{escape(text.title())}">
<rect x="10" y="19" width="16" height="16" fill="{p["cyan"]}"/>
<rect x="7" y="16" width="16" height="16" fill="{p["text"]}" opacity="0.18"/>
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
        for name, text in HEADERS:
            header(p, tag, name, text)
        footer(p, tag)
    print("assets regenerated")
