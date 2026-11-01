# Profile artwork

`README.md` and `README.zh-CN.md` are the published GitHub profile. Every image
they show lives under `assets/proof-20261101/`, in four editions: desktop and
phone, light and dark.

## Rebuilding

```bash
npm install && npx playwright install chromium   # once
node tools/capture.mjs                            # live sites → .capture/
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/render.py                  # .capture/ → assets/proof-20261101/
```

`render.py` deletes and rewrites the whole artwork folder, so a run always
matches the code.

## Source material

- `*-proof-*.svg`: typeset sheets. Every word on them comes from the products.
  Kachi uses the rally / selloff concept and trick from
  `content/packs/t1-finance-news/en-US/course.json`, plus pairs and counts
  from all six packs. Wayseeker uses prescription 3u1xmp, copied from the live
  site's Markdown export.
- `*-screens-*.png`: unretouched captures of the live sites, made by
  `tools/capture.mjs` at 1440 px (desktop) and 390 px (phone). They are scaled
  and framed, never redrawn.
- `masthead-*.svg`: the name sheet, with the profile's only animation.

## Rules

- Two inks: plate A (blue) and plate B (red), plus their overprint. Only the
  captured screens bring in any other colour.
- Type is converted to outlines at build time, so the SVGs do not depend on
  fonts installed on the viewer's machine.
- Numbers, dates and states in the screens are a snapshot of capture day, not
  live data.
- Real links stay in the Markdown; none are drawn into an image.

## Checking

Run `python3 tools/check_assets.py` and `python3 -m unittest discover -s tests -v`.
The checker validates both README editions, local image references, alt text,
explicit anchors, matching bilingual destinations, PNG dimensions and SVG
animation timelines. It also rejects executable SVG content.

## Font licences

None of these fonts is covered by this repository's MIT licence. All are under
the SIL Open Font License 1.1.

- `assets/ark-pixel-12px-proportional-latin.woff2`: Ark Pixel by TakWolf. Full
  text in `assets/ArkPixel-OFL.txt`.
- `tools/fonts/archivo-latin.woff2`: Archivo by the Archivo Project Authors
  (Omnibus-Type).
- `tools/fonts/bricolage-grotesque-latin.woff2`: Bricolage Grotesque by the
  Bricolage Grotesque Project Authors.

The build only reads these fonts to draw outlines; no font file ships inside
the artwork.
