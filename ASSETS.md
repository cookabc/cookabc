# Local Observatory assets

`README.md` is the published GitHub profile. `preview-v2.html` is its complete visual study, including navigation and links that are supplied as text in the README.

## Source material

- `assets/vitals.png`: Vitals product screenshot from `cookabc/vitals/docs/images/overview.png`.
- `assets/kachi.png`: Kachi product screenshot from `cookabc/Kachi/docs/images/home.png`.
- `assets/app-universe-current.png`: current App Universe screenshot from `031_app-universe/docs/images/home.png`.
- Agent Inspector artwork uses `033_zcode-inspector/docs/images/all-tools.png`, the actual local archive.
- `assets/v2/fonts/bricolage.ttf` and `bricolage-OFL.txt`: Bricolage Grotesque from `google/fonts/ofl/bricolagegrotesque`.
- Ark Pixel is retained for instrument annotations under `assets/ArkPixel-OFL.txt`.

## Publication artwork

`tools/export_v2.mjs` renders `preview-v2.html` into the files under `assets/v2/` using the zero-dependency CDP helper from `033_zcode-inspector`. Run it with Node 24.22.1. It starts its own local servers, waits for image decoding, and uses unique page URLs to prevent navigation-cache mixing.

- `observatory-hero-{light,dark}{,-mobile}.svg`: static first frame plus one native SMIL scanning line, with a static reduced-motion alternative.
- `observatory-{observe,record,understand}-*.webp`: responsive scene artwork. Observe has light and dark variants; Record and Understand keep their material surfaces in both themes.
- Mobile artwork is composed at 390 CSS pixels and exported at 2x resolution.
- Functional links remain real README links, not text pretending to be buttons inside an image.

The `LOCAL` lettering in Record is decorative and hidden from accessibility APIs in the HTML study. No transient session counts or live metrics are presented as personal achievements.

`tools/check_assets.py` validates SVG syntax and SMIL timelines recursively.
