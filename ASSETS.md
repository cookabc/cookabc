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

Older sets from retired profile layouts have been removed rather than left to
rot; git history still holds them.

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

`tools/check_assets.py` validates SMIL timelines on any SVG under `assets/`,
and treats a raster-only set as valid rather than failing.
