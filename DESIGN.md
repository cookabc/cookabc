---
name: "cookabc"
description: "Extracted visual system for the software workbench"
colors:
  background: "#fcfcfd"
  text: "#1c2024"
  border: "#d9d9e0"
  indigo-ink: "#3a5bc7"
  teal-ink: "#008573"
  iris-ink: "#5753c6"
  background-dark: "#111113"
  text-dark: "#edeef0"
  border-dark: "#363a3f"
  indigo-ink-dark: "#9eb1ff"
  teal-ink-dark: "#0bd8b6"
  iris-ink-dark: "#b1a9ff"
typography:
  display:
    fontFamily: "Space Grotesk"
    fontSize: "48px"
    fontWeight: 700
  row-label:
    fontFamily: "Space Grotesk"
    fontSize: "40px"
    fontWeight: 600
  row-body:
    fontFamily: "Space Grotesk"
    fontSize: "40px"
    fontWeight: 500
spacing:
  diagram-inset: "32px"
  row-pitch: "68px"
components:
  diagram:
    width: "900px"
    height: "330px"
    backgroundColor: "{colors.background}"
    textColor: "{colors.text}"
---

# Design System: cookabc

## Overview

**Creative North Star: "The Software Workbench"**

A compact directory uses generous outlined lettering, quiet rules, and three factual rows. Native Markdown provides the destinations and optional detail. The design boundary ends at the authored SVG and Markdown structure: GitHub controls page typography, chrome, link states, disclosure styling, and responsive behavior.

This is a scan of code and local artwork captures, not a separate visual comp or verification of a hosted GitHub page.

**Key Characteristics:**

- Outlined lettering
- Three factual rows
- Light and dark artwork
- Host-native navigation

## Colors

### Primary

Indigo step 11 identifies the first row.

### Secondary

Teal step 11 identifies the second row.

### Tertiary

Iris step 11 identifies the third row.

### Neutral

Slate steps 1, 6, and 12 provide the field, rules, and primary lettering. The dark tokens are exact counterparts from tools/radix-palette.json. Unused fill entries are not promoted into tokens. No intermediate ramps are invented.

**The Semantic Step Rule.** Use exact Radix values at their implemented semantic role; original raster content is outside the authored UI palette.

## Typography

The generator converts Space Grotesk into path outlines, avoiding a viewer font dependency. The font and OFL are vendored in tools/fonts. Frontmatter sizes are SVG coordinate sizes, not native GitHub CSS. At a 288px displayed width, 40px source row text becomes 12.8px; the source heading becomes 15.36px. The reviewed narrow captures retain readable lettering.

## Layout

The artwork has a 900 × 330 viewBox, a title baseline at y=76, and row starts at y=112 with 68-unit pitch. Labels start at x=32; body text starts at 200. The generator rejects text extending past x=870. Picture sources select light or dark artwork. Narrow display proportionally scales the same composition.

## Elevation & Depth

Flat artwork. Whitespace and row rules establish grouping. The authored SVG has no shadows, gradients, blur, or motion.

## Shapes

A rectangular field and horizontal rules use 0.5-unit SVG strokes. Image scaling scales those strokes too. No card radii or pills are introduced.

## Components

### Directory and native links

The sidecar references the existing light and dark SVG files without duplicating glyph paths. The studio diagram links as a whole to the playable site; the personal diagram is an orientation image with destinations in Markdown. Use native links and details/summary for optional content; do not reconstruct GitHub styling.

### Evidence and provenance

Sources: tools/generate_assets.py, tools/radix-palette.json, the active README, and the light/dark SVG pair. Local light, dark, light-narrow, and dark-narrow review captures were inspected. They cover artwork, not the full GitHub page. .impeccable/asset-provenance.json records original repository assets, hashes, and explicit source-repository URLs for remote previews where used. No new AI raster assets were introduced. Radix MIT attribution is in tools/radix.LICENSE. This document makes no live-deployment claim.

## Do's and Don'ts

### Do:

- Do use Radix steps 1–2 for backgrounds, 3–5 for interactive surfaces, 6–8 for boundaries, 9–10 for solid fills, and 11–12 for readable ink.
- Do preserve original assets and consult .impeccable/asset-provenance.json before changing imagery.
- Do regenerate both SVG themes and preserve title, description, and Markdown alt text.
- Do preserve the readable narrow-display type size.

### Don't:

- Don't add decorative shadows, middle-dot separators, or redundant explanatory UI copy.
- Don't treat screenshot colors or embedded text as UI design tokens.
- Don't claim control over GitHub's native font sizes, borders, hover states, or page chrome.
- Don't add scripted UI to a static GitHub profile.
