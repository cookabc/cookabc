#!/usr/bin/env python3
"""Rebuild accessible SVG diagrams with Space Grotesk outlines.
Requires fonttools (`python3 -m pip install fonttools`). Font and OFL license
are vendored under tools/fonts; no external request is needed when rebuilding.
"""
from pathlib import Path
import json
from html import escape
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
ROOT = Path(__file__).resolve().parents[1]
COLORS = json.loads((ROOT / "tools/radix-palette.json").read_text())
FONTS = {weight: instantiateVariableFont(TTFont(ROOT / "tools/fonts/SpaceGrotesk.ttf"), {"wght": weight}) for weight in (500, 600, 700)}
TITLE = 'Small tools. Real work.'
ROWS = (('Mac', 'Vitals / AI Toolbox / Framelet'), ('Web', 'Kachi / App Universe / Inspector'), ('Editor', 'Python / npm Dependencies'))
DEST = 'assets/workbench'
BODY_X = 200

def lettering(text, x, y, size, weight, color):
    font = FONTS[weight]
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    parts, cursor = [], 0
    for char in text:
        name = cmap[ord(char)]
        glyph = glyphs[name]
        pen = SVGPathPen(glyphs)
        glyph.draw(pen)
        parts.append(f'<path transform="translate({cursor:g} 0)" d="{pen.getCommands()}"/>')
        cursor += glyph.width
    if x + cursor * scale > 870:
        raise ValueError(f"Text exceeds the diagram: {text}")
    return f'<g fill="{color}" transform="translate({x} {y}) scale({scale:g} {-scale:g})">' + "".join(parts) + "</g>"

for theme, palette in COLORS.items():
    description = "; ".join(f"{label}: {text}" for label, text in ROWS)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="330" viewBox="0 0 900 330" role="img" aria-labelledby="title description"><title id="title">{escape(TITLE)}</title><desc id="description">{escape(description)}</desc><rect width="900" height="330" fill="{palette["background"]}"/>'
    svg += lettering(TITLE, 32, 76, 48, 700, palette["text"])
    for index, (label, text) in enumerate(ROWS):
        y = 112 + index * 68
        svg += f'<path d="M32 {y}H868" stroke="{palette["border"]}" stroke-width=".5"/>'
        svg += lettering(label, 32, y + 45, 40, 600, palette["accents"][index])
        svg += lettering(text, BODY_X, y + 45, 40, 500, palette["text"])
    (ROOT / f"{DEST}-{theme}.svg").write_text(svg + "</svg>")
