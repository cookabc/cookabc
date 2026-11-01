---
name: cookabc profile
description: A two-plate risograph proof. Blue keeps, red strikes.
colors:
  paper: "#f5f3ee"
  plate-a: "#0068b4"
  plate-b: "#f04e5e"
  overprint: "#002042"
  dark-paper: "#0f1114"
  dark-plate-a: "#3f9bff"
  dark-plate-b: "#ff5b6c"
  dark-key: "#ece6dc"
typography:
  display: "Archivo, wdth 62, wght 900 (outlined)"
  pair: "Bricolage Grotesque, wdth 78, wght 800, opsz 96 (Kachi's own display face)"
  label: "Archivo, wdth 72, wght 800"
  text: "Archivo, wdth 88, wght 500"
  annotation: "Ark Pixel 12px proportional"
---

# Design system: cookabc profile

## North star: the proof sheet

Both featured products are about telling two things apart. Kachi pairs a word
with its twin; Wayseeker pairs a habit with the tool that replaces it. So the
profile is printed in exactly two inks, like a risograph proof:

- **Plate A, blue:** what you keep. That is the first twin and the replacing tool.
- **Plate B, red:** what you strike, or the other side. That is the second twin,
  the strike-through over a habit, and Kachi's slash.
- **Overprint:** where the plates cross. On white stock, multiply gives a
  near-black navy, which also sets body text and rules. On black stock, two
  light inks would screen to lavender, so a third key plate in paper white
  sits on top instead.

No other colour appears, except inside the unretouched screen captures.

## Sheets

Every image is a trimmed sheet with crop marks and a printer's slug across the
top. The slug names the plate and the sheet (PLATE A · WAYSEEKER, Rx No.
3u1xmp). Ark Pixel is the slug voice, the hand of the person running the press.

1. **Masthead:** `cookabc` across the full measure, printed once per plate and
   offset a few pixels. A registration target and the colour bar are real
   printer's furniture, not decoration.
2. **Proof A, Wayseeker:** the site's own question as a headline, then
   prescription 3u1xmp. Each habit is set in ink and struck in red, and an arrow
   leads to the tool in blue.
3. **Proof B, Kachi:** one pair at poster scale (rally in blue, a red slash,
   selloff in red), the trick, and a specimen line of more pairs.
4. **Screens:** live captures, desktop and phone side by side, each framed by
   two hairlines out of register.

## Motion

There is one moment: on load, the masthead's two plates arrive from opposite
corners and land almost in register (1.8 s, expo-out). With reduced motion,
the sheet shows the landed state. Nothing else moves.

## Responsive

Each sheet has an 800 px phone edition, picked with `<picture>` at 600 px and
below. Phone sheets restack instead of shrinking: the pair goes on two lines,
the prescription moves the tool above its habit, and slug type grows to 30 px
so it reads at about 0.45x.

## Don’t

- Add a third colour, gradients, or shadows.
- Put text in an image that the README should carry as a link.
- Show any project other than Kachi and Wayseeker without updating PRODUCT.md.
