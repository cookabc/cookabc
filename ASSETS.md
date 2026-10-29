# Profile artwork

`README.md` is the published GitHub profile. Its images live under
`assets/fancy-20261029/` (masthead) and `assets/two-projects-20261029/`
(the two project photographs).

## Source material

Artwork is composed from real screenshots of the public products:

- `two-projects-20261029/kachi.png`, `kachi-mobile.png` — Kachi, from `cookabc/Kachi`.
- `two-projects-20261029/wayseeker.png`, `wayseeker-mobile.png` — Wayseeker, from the live site at `wayseeker.vercel.app`.
- `fancy-20261029/studio-*.svg` — the studio masthead, including its mobile and dark variants.
- `ArkPixel-OFL.txt`, `ark-pixel-12px-proportional-latin.woff2` — Ark Pixel, retained for instrument annotations.

Older sets (`assets/v2/`, `assets/redesign-20261028/`,
`assets/redesign-20261029/`, and the loose `assets/*.png`) belong to retired
profile layouts and are no longer referenced by the README.

## Rules

- Desktop artwork keeps the complete original screenshot; mobile artwork shows
  a labelled crop of the same source. No product interface is invented.
- Numbers, dates and states inside the screenshots are not live data.
- Functional links stay real README links, never text drawn into an image.

## Checking

`tools/check_assets.py` validates SMIL timelines on any SVG under `assets/`,
and treats a raster-only set as valid rather than failing.
