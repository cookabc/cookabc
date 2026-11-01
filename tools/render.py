#!/usr/bin/env python3
"""Render the profile artwork: a two-plate risograph proof.

Every colour on the sheet is one of two inks, or the overprint where they
cross. Type is converted to outlines so the SVGs look the same everywhere and
carry no font files. Screens are composed from real captures in .capture/
(run `node tools/capture.mjs` first).

    python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
    .venv/bin/python tools/render.py
"""

import io
import json
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "proof-20261101"
CAPTURE = ROOT / ".capture"
FONTS = ROOT / "tools" / "fonts"
PIXEL_FONT = ROOT / "assets" / "ark-pixel-12px-proportional-latin.woff2"

# ---------------------------------------------------------------- inks


def hexrgb(value):
    return tuple(int(value[i : i + 2], 16) for i in (1, 3, 5))


def rgbhex(rgb):
    return "#" + "".join(f"{round(c):02x}" for c in rgb)


def multiply(a, b):
    return rgbhex([x * y / 255 for x, y in zip(hexrgb(a), hexrgb(b))])


def screen(a, b):
    return rgbhex([255 - (255 - x) * (255 - y) / 255 for x, y in zip(hexrgb(a), hexrgb(b))])


# Light: riso Blue and Bright Red on uncoated white; ink = their overprint.
# Dark: the same two plates screen-printed on black stock.
THEMES = {
    "light": {"paper": "#f5f3ee", "a": "#0068b4", "b": "#f04e5e", "blend": "multiply"},
    "dark": {"paper": "#0f1114", "a": "#3f9bff", "b": "#ff5b6c", "blend": "screen"},
}
for t in THEMES.values():
    mix = multiply if t["blend"] == "multiply" else screen
    t["ab"] = mix(t["a"], t["b"])
    # Hairlines and slugs: the overprint, thinned on the paper.
    t["rule"] = t["ab"]
# Body text: the overprint on white stock; on black stock a warm paper white,
# because two light inks overprinted read lavender, not black.
THEMES["light"]["ink"] = THEMES["light"]["ab"]
THEMES["dark"]["ink"] = "#ece6dc"
# Two light inks screened together on black go lavender, so the dark sheet
# carries a third, key plate in paper white over the overlap instead.
THEMES["dark"]["ab"] = "#ece6dc"
THEMES["dark"]["key"] = True
THEMES["dark"]["rule"] = "#5d5a63"


# ---------------------------------------------------------------- type


def _face(path):
    font = TTFont(path)
    font.flavor = None
    data = io.BytesIO()
    font.save(data)
    return hb.Face(data.getvalue()), data.getvalue()


class Type:
    """A shaped, outlined voice: one font file at one variation instance."""

    def __init__(self, path, variations=None, tracking=0.0):
        self.face, self.blob = _face(path)
        self.font = hb.Font(self.face)
        if variations:
            self.font.set_variations(variations)
        self.upem = self.face.upem
        self.tracking = tracking
        cmap = TTFont(io.BytesIO(self.blob)).getBestCmap()
        self.cmap = cmap

    def _shape(self, text):
        missing = [c for c in text if ord(c) not in self.cmap and not c.isspace()]
        if missing:
            raise SystemExit(f"glyphs missing for {missing!r} in {text!r}")
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf)
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, size):
        _, pos = self._shape(text)
        adv = sum(p.x_advance for p in pos) + self.tracking * self.upem * len(pos)
        return adv * size / self.upem

    def path(self, text, size, x, y, anchor="start"):
        if anchor != "start":
            w = self.width(text, size)
            x -= w if anchor == "end" else w / 2
        infos, pos = self._shape(text)
        scale = size / self.upem
        pen = SVGPathPen(None, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        cursor = 0.0
        for info, p in zip(infos, pos):
            gx = x + (cursor + p.x_offset) * scale
            gy = y - p.y_offset * scale
            self.font.draw_glyph_with_pen(
                info.codepoint, TransformPen(pen, (scale, 0, 0, -scale, gx, gy))
            )
            cursor += p.x_advance + self.tracking * self.upem
        return pen.getCommands()

    def wrap(self, text, size, width):
        words, lines, line = text.split(" "), [], ""
        for word in words:
            trial = f"{line} {word}".strip()
            if line and self.width(trial, size) > width:
                lines.append(line)
                line = word
            else:
                line = trial
        return lines + [line]


DISPLAY = Type(FONTS / "archivo-latin.woff2", {"wdth": 62, "wght": 900})
LABEL = Type(FONTS / "archivo-latin.woff2", {"wdth": 72, "wght": 800}, tracking=0.02)
TEXT = Type(FONTS / "archivo-latin.woff2", {"wdth": 88, "wght": 500})
PAIR = Type(FONTS / "bricolage-grotesque-latin.woff2", {"wdth": 78, "wght": 800, "opsz": 96})
PIXEL = Type(PIXEL_FONT)


# ---------------------------------------------------------------- sheet furniture


class Sheet:
    def __init__(self, width, height, theme, title, desc):
        self.w, self.h, self.t = width, height, THEMES[theme]
        self.title, self.desc = title, desc
        self.style, self.body = [], []
        # Phone sheets render at ~0.45x, so their small type is set larger.
        self.slug = 24 if width >= 1600 else 30

    def add(self, markup):
        self.body.append(markup)

    def fill(self, d, ink, extra=""):
        if d:
            self.add(f'<path d="{d}" fill="{self.t[ink]}"{extra}/>')

    def rule(self, x1, y1, x2, y2, ink="rule", width=1.5, extra=""):
        self.add(
            f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" stroke="{self.t[ink]}" '
            f'stroke-width="{width}" fill="none"{extra}/>'
        )

    def crops(self, inset=34, length=22):
        """Crop marks at the four trim corners, off the live area."""
        w, h, i, n = self.w, self.h, inset, length
        for cx, sx in ((i, -1), (w - i, 1)):
            for cy, sy in ((i, -1), (h - i, 1)):
                self.rule(cx + sx * 6, cy, cx + sx * (6 + n), cy, width=1)
                self.rule(cx, cy + sy * 6, cx, cy + sy * (6 + n), width=1)

    def target(self, x, y, r=11):
        """A registration target: both plates, so misregistration shows."""
        for ink, dx, dy in (("a", -1.2, -0.8), ("b", 1.2, 0.8)):
            stroke = f'stroke="{self.t[ink]}" stroke-width="1.4" fill="none"'
            self.add(
                f'<g style="mix-blend-mode:{self.t["blend"]}">'
                f'<circle cx="{x + dx:.1f}" cy="{y + dy:.1f}" r="{r}" {stroke}/>'
                f'<path d="M{x + dx - r - 7:.1f} {y + dy:.1f}h{2 * r + 14}M{x + dx:.1f} {y + dy - r - 7:.1f}v{2 * r + 14}" {stroke}/></g>'
            )

    def swatches(self, x, y, size=18, gap=6, labels=True):
        """Colour bar: plate A, plate B, and their overprint."""
        for i, ink in enumerate(("a", "b", "ab")):
            sx = x + i * (size + gap + (34 if labels else 0))
            self.add(f'<rect x="{sx}" y="{y}" width="{size}" height="{size}" fill="{self.t[ink]}"/>')
            if labels:
                self.fill(PIXEL.path(("A", "B", "A+B")[i], 12, sx + size + 6, y + size - 4), "ink")

    def finish(self, bottom):
        self.h = round(bottom)
        self.crops()

    def svg(self):
        style = "".join(self.style)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{self.title}</title><desc id="desc">{self.desc}</desc>\n'
            + (f"<style>{style}</style>\n" if style else "")
            + f'<rect width="{self.w}" height="{self.h}" fill="{self.t["paper"]}"/>\n'
            + "\n".join(self.body)
            + "\n</svg>\n"
        )


def write(name, markup):
    (OUT / name).write_text(markup, encoding="utf-8")


# ---------------------------------------------------------------- masthead

# The one animated moment: the two plates arrive from opposite sides and land
# a hair out of register. Reduced motion shows the landed state.
MOTION = (
    ".plate{animation:register 1.8s cubic-bezier(.16,1,.3,1) .25s both}"
    ".plate-b{animation-name:register-b}"
    "@keyframes register{from{transform:translate(-26px,-12px)}to{transform:translate(0,0)}}"
    "@keyframes register-b{from{transform:translate(26px,12px)}to{transform:translate(0,0)}}"
    "@media (prefers-reduced-motion:reduce){.plate,.plate-b{animation:none}}"
)

MARGIN = 70


def slug(s, left, right=None, right_ink="ink"):
    """Printer's slug: what this sheet is (left) and its number (right)."""
    s.fill(PIXEL.path(left, s.slug, MARGIN, 92), "ink")
    if right:
        s.fill(PIXEL.path(right, s.slug, s.w - MARGIN, 92, "end"), right_ink)
    s.rule(MARGIN, 114, s.w - MARGIN, 114, width=1)
    return 114


def two_plates(s, d, offset=3, animate=False):
    """Print one outline on both plates, offset, overprinting where they meet."""
    for ink, cls, sign in (("a", "plate", -1), ("b", "plate plate-b", 1)):
        inner = f'<path d="{d}" fill="{s.t[ink]}" transform="translate({sign * offset} {sign * offset * 0.6:.1f})"/>'
        if animate:
            inner = f'<g class="{cls}">{inner}</g>'
        s.add(f'<g style="mix-blend-mode:{s.t["blend"]}">{inner}</g>')
    if s.t.get("key"):
        s.add(f'<path d="{d}" fill="{s.t["ab"]}"/>')


def masthead(theme, mobile=False):
    w = 800 if mobile else 1600
    s = Sheet(
        w,
        0,
        theme,
        "cookabc — two tools for telling things apart",
        "The name cookabc printed in two inks, blue and red, a few pixels out of register so the "
        "overprint shows. On load the two plates slide in from opposite sides and land almost "
        "together. Beneath: two tools for telling things apart.",
    )
    s.style.append(MOTION)
    if mobile:
        top = slug(s, "TWO-PLATE PROOF", "2026·11")
    else:
        top = slug(s, "COOKABC · TWO-PLATE PROOF", None)
        s.swatches(w - MARGIN - 196, 74)
    size = (w - 2 * MARGIN) / DISPLAY.width("cookabc", 1)
    baseline = top + 30 + size * 0.74
    two_plates(s, DISPLAY.path("cookabc", size, MARGIN, baseline), offset=4 if not mobile else 3, animate=True)
    y = baseline + (52 if not mobile else 44)
    s.rule(MARGIN, y, w - MARGIN, y, ink="ink", width=2)
    if mobile:
        s.fill(LABEL.path("TWO TOOLS FOR TELLING", 40, MARGIN, y + 62), "ink")
        s.fill(LABEL.path("THINGS APART.", 40, MARGIN, y + 108), "ink")
        s.fill(PIXEL.path("两件帮你分清事物的小工具", s.slug, MARGIN, y + 160), "a")
        s.target(w - MARGIN - 18, y + 96)
        bottom = y + 220
    else:
        s.fill(LABEL.path("TWO TOOLS FOR TELLING THINGS APART.", 42, MARGIN, y + 66), "ink")
        s.fill(PIXEL.path("两件帮你分清事物的小工具", s.slug, w - MARGIN - 70, y + 60, "end"), "a")
        s.target(w - MARGIN - 18, y + 50)
        bottom = y + 130
    s.finish(bottom)
    write(f"masthead{'-mobile' if mobile else ''}-{theme}.svg", s.svg())


# ---------------------------------------------------------------- proof A: Wayseeker

# Prescription No. 3u1xmp, copied from the live site's Markdown export.
PRESCRIPTION = [
    ("A", "FIND A DIRECTION", "generic “delight” decks with no concrete reference", "NEAL.FUN"),
    ("B", "BUILD A VISUAL LANGUAGE", "vague redesign chats", "IMPECCABLE"),
    ("C", "MAKE IT MOVE", "“add a little bounce” without a target", "60FPS"),
    ("D", "STUDY THE REAL THING", "guessing funnel steps from memory", "MOBBIN"),
    ("E", "FINISH AND SHARE", "fighting export pipelines for agent-built slides", "MAGIC SLIDE"),
]


def arrow(s, x1, x2, y, ink="a"):
    s.add(
        f'<path d="M{x1:.1f} {y:.1f}H{x2 - 2:.1f}M{x2 - 13:.1f} {y - 9:.1f}L{x2:.1f} {y:.1f}L{x2 - 13:.1f} {y + 9:.1f}" '
        f'stroke="{s.t[ink]}" stroke-width="2.6" fill="none" stroke-linecap="square"/>'
    )


def code_disc(s, x, y, letter, r=21):
    s.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{s.t["ink"]}" stroke-width="1.8"/>')
    s.fill(LABEL.path(letter, r * 1.1, x, y + r * 0.4, "middle"), "ink")


def struck(s, text, size, x, y):
    """A habit: set in ink, struck once by plate B."""
    s.fill(TEXT.path(text, size, x, y), "ink")
    width = TEXT.width(text, size)
    s.add(
        f'<path d="M{x - 3:.1f} {y - size * 0.3:.1f}H{x + width + 3:.1f}" stroke="{s.t["b"]}" '
        f'stroke-width="{max(2.5, size * 0.1):.1f}" style="mix-blend-mode:{s.t["blend"]}"/>'
    )
    return width


def wayseeker(theme, mobile=False):
    desc = (
        "Wayseeker prescription No. 3u1xmp. Under the question What are you settling for?, five "
        "habits are struck out in red, each replaced by a tool printed in blue: "
        + "; ".join(f"{h} → {t.title()}" for _, _, h, t in PRESCRIPTION)
        + "."
    )
    w = 800 if mobile else 1600
    s = Sheet(w, 0, theme, "Wayseeker — what are you settling for?", desc)
    top = slug(s, "PLATE A · WAYSEEKER", "Rx No. 3u1xmp", right_ink="b")
    if mobile:
        size = (w - 2 * MARGIN) / DISPLAY.width("SETTLING FOR?", 1)
        y = top + 26 + size * 0.74
        two_plates(s, DISPLAY.path("WHAT ARE YOU", size, MARGIN, y), 2)
        y += size * 0.92
        two_plates(s, DISPLAY.path("SETTLING FOR?", size, MARGIN, y), 2)
    else:
        size = (w - 2 * MARGIN) / DISPLAY.width("WHAT ARE YOU SETTLING FOR?", 1)
        y = top + 26 + size * 0.74
        two_plates(s, DISPLAY.path("WHAT ARE YOU SETTLING FOR?", size, MARGIN, y), 3)
    y += 44
    s.rule(MARGIN, y, w - MARGIN, y, ink="ink", width=2)
    y += 20
    for code, stage, habit, tool in PRESCRIPTION:
        if mobile:
            code_disc(s, MARGIN + 21, y + 40, code)
            x = MARGIN + 66
            s.fill(PIXEL.path(stage, s.slug, x, y + 34), "ink")
            s.fill(DISPLAY.path(tool, 64, x, y + 96), "a")
            yy = y + 140
            for line in TEXT.wrap(habit, 34, w - MARGIN - x):
                struck(s, line, 34, x, yy)
                yy += 44
            y = yy + 4
        else:
            code_disc(s, MARGIN + 21, y + 44, code)
            x = MARGIN + 66
            s.fill(PIXEL.path(stage, s.slug, x, y + 34), "ink")
            hw = struck(s, habit, 32, x, y + 74)
            tw = DISPLAY.width(tool, 72)
            arrow(s, x + hw + 30, w - MARGIN - tw - 28, y + 63)
            s.fill(DISPLAY.path(tool, 72, w - MARGIN, y + 86, "end"), "a")
            y += 112
        s.rule(MARGIN, y, w - MARGIN, y, width=1, extra=' stroke-dasharray="3 6"')
        y += 8
    y += 44
    s.fill(PIXEL.path("29 HABITS · 29 DRAWERS · 5 COLUMNS", s.slug, MARGIN, y), "ink")
    if mobile:
        s.fill(PIXEL.path("COPY AS MARKDOWN FOR YOUR AGENT", s.slug, MARGIN, y + 36), "ink")
        y += 36
    else:
        s.fill(PIXEL.path("COPY AS MARKDOWN FOR YOUR AGENT", s.slug, w - MARGIN, y, "end"), "ink")
    s.finish(y + 64)
    write(f"wayseeker-proof{'-mobile' if mobile else ''}-{theme}.svg", s.svg())


# ---------------------------------------------------------------- proof B: Kachi

KACHI_TRICK = "A rally is buyers pushing prices up; a selloff is sellers pushing them down."
KACHI_PAIRS = [
    ("slump", "rebound"),
    ("beat", "miss"),
    ("revenue", "earnings"),
    ("coupon", "yield"),
    ("hawkish", "dovish"),
    ("capex", "opex"),
    ("in-sample", "out-of-sample"),
    ("hedge", "pledge"),
]


def slash(s, x, base, size):
    """Kachi's own mark between twins: a red stroke leaning forward."""
    s.add(
        f'<path d="M{x:.1f} {base + size * 0.04:.1f}L{x + size * 0.2:.1f} {base - size * 0.66:.1f}" '
        f'stroke="{s.t["b"]}" stroke-width="{size * 0.085:.1f}" stroke-linecap="round" '
        f'style="mix-blend-mode:{s.t["blend"]}"/>'
    )


def kachi(theme, mobile=False):
    desc = (
        "Kachi: the pair rally / selloff set large, rally in blue and selloff in red. "
        f"The trick: {KACHI_TRICK} More pairs from the course: "
        + ", ".join(f"{a} / {b}" for a, b in KACHI_PAIRS)
        + ". 6 levels, 238 concepts, 145 confusion pairs, 125 lessons, 1,697 prompts."
    )
    w = 800 if mobile else 1600
    s = Sheet(w, 0, theme, "Kachi — rally / selloff", desc)
    top = slug(s, "PLATE B · KACHI", "FIRST PAIR · OPPOSITES")
    if mobile:
        size = (w - 2 * MARGIN) / PAIR.width("selloff", 1)
        base = top + 20 + size * 0.74
        s.fill(PAIR.path("rally", size, MARGIN, base), "a")
        slash(s, MARGIN + PAIR.width("rally", size) + size * 0.1, base, size)
        base += size * 0.86
        s.fill(PAIR.path("selloff", size, MARGIN, base), "b")
    else:
        gap = 0.42
        size = (w - 2 * MARGIN) / (PAIR.width("rally", 1) + PAIR.width("selloff", 1) + gap)
        base = top + 20 + size * 0.74
        aw = PAIR.width("rally", size)
        s.fill(PAIR.path("rally", size, MARGIN, base), "a")
        slash(s, MARGIN + aw + size * gap * 0.25, base, size)
        s.fill(PAIR.path("selloff", size, w - MARGIN, base, "end"), "b")
    y = base + size * 0.28 + 10
    s.rule(MARGIN, y, w - MARGIN, y, ink="ink", width=2)
    y += 54
    s.fill(PIXEL.path("THE TRICK", s.slug, MARGIN, y - 6), "b")
    indent = 0 if mobile else 190
    if mobile:
        y += 44
    trick = 34 if not mobile else 40
    for line in TEXT.wrap(KACHI_TRICK, trick, w - 2 * MARGIN - indent):
        s.fill(TEXT.path(line, trick, MARGIN + indent, y), "ink")
        y += trick * 1.3
    y += 10
    s.rule(MARGIN, y, w - MARGIN, y, width=1, extra=' stroke-dasharray="3 6"')
    y += 56
    x, size2 = MARGIN, (36 if not mobile else 44)
    for first, second in KACHI_PAIRS:
        piece = PAIR.width(f"{first} / {second}", size2)
        if x > MARGIN and x + piece > w - MARGIN:
            x, y = MARGIN, y + 54
        s.fill(PAIR.path(first, size2, x, y), "a")
        sx = x + PAIR.width(first + " ", size2)
        s.fill(PAIR.path("/", size2, sx, y), "b")
        s.fill(PAIR.path(second, size2, sx + PAIR.width("/ ", size2), y), "b")
        x += piece + 44
    y += 40
    s.rule(MARGIN, y, w - MARGIN, y, width=1)
    y += 48
    if mobile:
        s.fill(PIXEL.path("6 LEVELS · 238 CONCEPTS · 145 PAIRS", s.slug, MARGIN, y), "ink")
        s.fill(PIXEL.path("125 LESSONS · 1,697 PROMPTS", s.slug, MARGIN, y + 36), "ink")
        y += 36
    else:
        s.fill(PIXEL.path("6 LEVELS · 238 CONCEPTS · 145 PAIRS · 125 LESSONS · 1,697 PROMPTS", s.slug, MARGIN, y), "ink")
        s.swatches(w - MARGIN - 196, y - 18)
    s.finish(y + 64)
    write(f"kachi-proof{'-mobile' if mobile else ''}-{theme}.svg", s.svg())


# ---------------------------------------------------------------- screens (raster)


def pixel_font(size):
    return ImageFont.truetype(io.BytesIO(PIXEL.blob), size)


def plate_frame(canvas, box, theme, offset=5):
    """Two hairline frames, one per plate, out of register by a few pixels."""
    t = THEMES[theme]
    x0, y0, x1, y1 = box
    layer = Image.new("RGB", canvas.size, t["paper"])
    draw = ImageDraw.Draw(layer)
    draw.rectangle((x0 - offset, y0 - offset, x1 - offset, y1 - offset), outline=t["a"], width=3)
    draw.rectangle((x0 + offset, y0 + offset, x1 + offset, y1 + offset), outline=t["b"], width=3)
    blend = ImageChops.multiply if t["blend"] == "multiply" else ImageChops.screen
    paper = Image.new("RGB", canvas.size, t["paper"])
    # Composite only the frame strokes, keeping what is already on the canvas.
    mask = ImageChops.difference(layer, paper).convert("L").point(lambda v: 255 if v else 0)
    if t["blend"] == "multiply":
        mixed = blend(canvas, layer)
    else:
        mixed = blend(canvas, ImageChops.subtract(layer, paper))
    canvas.paste(mixed, mask=mask)


def crop_marks(draw, size, theme, inset=34, n=22):
    w, h = size
    ink = THEMES[theme]["rule"]
    for cx, sx in ((inset, -1), (w - inset, 1)):
        for cy, sy in ((inset, -1), (h - inset, 1)):
            draw.line((cx + sx * 6, cy, cx + sx * (6 + n), cy), fill=ink, width=1)
            draw.line((cx, cy + sy * 6, cx, cy + sy * (6 + n)), fill=ink, width=1)


def screens(name, host, theme, mobile=False):
    """Unretouched captures, framed by both plates. Desktop and phone sit apart."""
    t = THEMES[theme]
    desktop = Image.open(CAPTURE / f"{name}-desktop.png").convert("RGB")
    phone = Image.open(CAPTURE / f"{name}-phone.png").convert("RGB")
    margin, top = 70, 136
    if mobile:
        W = 800
        font = pixel_font(24)
        ph_w = 440
        ph = phone.resize((ph_w, round(phone.height * ph_w / phone.width)), Image.LANCZOS)
        H = top + ph.height + 130
        canvas = Image.new("RGB", (W, H), t["paper"])
        x, y = (W - ph_w) // 2, top
        canvas.paste(ph, (x, y))
        plate_frame(canvas, (x, y, x + ph_w, y + ph.height), theme)
        draw = ImageDraw.Draw(canvas)
        draw.text((margin, 72), host.upper(), font=font, fill=t["ink"])
        draw.text((margin, y + ph.height + 44), "PHONE · 390 PX · 2026-11-01", font=font, fill=t["ink"])
    else:
        W = 1600
        font = pixel_font(24)
        gap = 64
        # Same height for both, filling the live width between the margins.
        ratio_d = desktop.width / desktop.height
        ratio_p = phone.width / phone.height
        h = round((W - 2 * margin - gap) / (ratio_d + ratio_p))
        dk = desktop.resize((round(h * ratio_d), h), Image.LANCZOS)
        ph = phone.resize((W - 2 * margin - gap - dk.width, h), Image.LANCZOS)
        H = top + h + 130
        canvas = Image.new("RGB", (W, H), t["paper"])
        canvas.paste(dk, (margin, top))
        plate_frame(canvas, (margin, top, margin + dk.width, top + h), theme)
        px = margin + dk.width + gap
        canvas.paste(ph, (px, top))
        plate_frame(canvas, (px, top, px + ph.width, top + h), theme)
        draw = ImageDraw.Draw(canvas)
        draw.text((margin, 72), host.upper(), font=font, fill=t["ink"])
        draw.text((margin, top + h + 44), "DESKTOP · 1440 PX", font=font, fill=t["ink"])
        label = "PHONE · 390 PX"
        draw.text((px, top + h + 44), label, font=font, fill=t["ink"])
        right = "UNRETOUCHED · 2026-11-01"
        draw.text((W - margin - draw.textlength(right, font=font), 72), right, font=font, fill=t["ink"])
    crop_marks(draw, canvas.size, theme)
    out = OUT / f"{name}-screens{'-mobile' if mobile else ''}-{theme}.png"
    canvas.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(out, optimize=True)
    return out


# ---------------------------------------------------------------- run


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.iterdir():
        old.unlink()
    for theme in THEMES:
        for mobile in (False, True):
            masthead(theme, mobile)
            wayseeker(theme, mobile)
            kachi(theme, mobile)
            screens("wayseeker", "wayseeker.vercel.app", theme, mobile)
            screens("kachi", "kachi-game.vercel.app", theme, mobile)
    summary = {p.name: p.stat().st_size for p in sorted(OUT.iterdir())}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
