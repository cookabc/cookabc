# Profile artwork

`README.md` is the published GitHub profile. Every image it shows lives under
`assets/curated-four-20261029/`.

## Source material

Artwork is composed from real screenshots of the public products:

- `kachi.png`, `kachi-mobile.png` — Kachi, from `cookabc/Kachi`.
- `wayseeker.png`, `wayseeker-mobile.png` — Wayseeker, from the live site at `wayseeker.vercel.app`.
- `museum.png`, `museum-mobile.png` — Paper Mechanical Museum, from `cookabc/paper-mechanical-museum`.
- `flow.png`, `flow-mobile.png` — Financial Sankey Studio, from `cookabc/financial-sankey`.
- `cabinet-*.svg` — the studio masthead, including its mobile and dark variants.
- `ArkPixel-OFL.txt`, `ark-pixel-12px-proportional-latin.woff2` — Ark Pixel, retained for instrument annotations.

## Rules

- Desktop artwork keeps the complete original screenshot; mobile artwork shows
  a labelled crop of the same source. No product interface is invented.
- Screenshots show each product in its English interface, captured at 1500px wide
  (430px on phones) so the profile renders them sharply at full width.
- The Financial Sankey chart's node labels come from the sample statement, which
  is Chinese-authored data rather than interface copy; the chrome around it is English.
- Numbers, dates and states inside the screenshots are not live data.
- Functional links stay real README links, never text drawn into an image.

## Checking

Run `python3 tools/check_assets.py` and `python3 -m unittest discover -s tests -v`.
The check validates both published README editions, local image references, alt
text, explicit anchors, matching bilingual destinations, PNG dimensions and SVG
animation timelines (including non-finite values). It also rejects executable SVG
content. Static SVGs and raster-only image sets are supported. No rendering or
Python packages are needed; screenshots still need visual review on GitHub.

## Font licence

The font file `assets/ark-pixel-12px-proportional-latin.woff2` is Ark Pixel 12px
proportional Latin by TakWolf. It is **not** covered by this repository's MIT
licence; it is licensed under the SIL Open Font License, Version 1.1. The full
text is in `assets/ArkPixel-OFL.txt` and must travel with the font file.

