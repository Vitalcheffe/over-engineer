# Template System — Usage

## What this is

A reusable template for Amine's portfolio + project sites. One canonical HTML structure, four named visual identities ("vibes"), eight accent swaps per vibe ("colorways"). Inspired by [archify](https://github.com/tt-a1i/archify)'s preset system.

The complaint was "très très basique" — competent but lifeless. The fix is **intentional identity**: each vibe is a complete design DNA (typography + material + motion + composition), and the colorway is a single accent swap, never a theming exercise.

## Open the showcase

Open `index.html` in this folder. It shows all 4 vibes on the same content side by side, plus the 3 project pages with the same vibe but different colorways.

## Files

```
template/
├── index.html                              ← showcase (start here)
├── over-engineer/index.html                ← portfolio (field-journal + navy)
├── over-engineer-traffic/index.html        ← project (field-journal + amber)
├── over-engineer-flocking/index.html       ← project (field-journal + emerald)
├── over-engineer-raindrops/index.html      ← project (field-journal + sky)
├── showcase-console/index.html             ← vibe demo (console + vermilion)
├── showcase-atlas/index.html               ← vibe demo (atlas + sky)
├── showcase-dispatch/index.html            ← vibe demo (dispatch + vermilion)
├── showcase-field-journal-light/index.html ← light theme variant
└── _source/                                ← source template + build script
    ├── DESIGN.md                           ← creative North Star + named rules
    ├── base.html                           ← canonical structure
    ├── styles/{base,vibes,colorways}.css  ← token sets
    ├── scripts/build.mjs                   ← Node renderer
    └── content/*.json                      ← content for each rendered page
```

## Build a new site

```bash
cd _source
node scripts/build.mjs content/<name>.json <vibe> <colorway> <theme> <out.html>
```

- **vibe**: `field-journal` · `console` · `atlas` · `dispatch`
- **colorway**: `navy` · `vermilion` · `emerald` · `amber` · `sky` · `rose` · `violet` · `graphite`
- **theme**: `light` · `dark`

Output is a single self-contained HTML file (~50kb). Ship anywhere — no build step, no JS framework.

## The 4 vibes

| Vibe | For | DNA |
|---|---|---|
| **field-journal** | over-engineer projects, math/physics modeling | Paper, ruled lines, vermilion ink, Syne display |
| **console** | ML, systems, agent runs | Terminal dark, scanlines, JetBrains Mono everywhere, blinking cursor |
| **atlas** | aero, infra, cartographic | Blueprint grid, drafting corner brackets, Space Grotesk + Inter |
| **dispatch** | case studies, startup, reportage | Magazine, drop caps, Playfair display, editorial red |

## The 8 colorways

Each colorway swaps exactly ONE accent color. The accent is used for:
- filet top on card hover
- reading progress bar
- external link hover
- stat value (the key metric)
- eyebrow dot pulse ring

Nothing else changes. Background, body text, hierarchy — all stay identical. **One accent per page, never two.**

## Design discipline (read DESIGN.md before editing)

- **Vibe Parity Rule**: same vibe ⇒ same typography, motion, composition. Different colorways allowed.
- **Colorway Identity Rule**: colorway is an accent, not a theme. Semantic meaning comes from content.
- **Flat-at-Rest Rule**: no shadows by default. Borders + tone define structure.
- **Motion Budget Rule**: 3 signatures max — reveal on scroll, card hover, one vibe atmosphere.
- **Anti-Cliché Rule**: no glassmorphism, no gradient text, no icon packs, no "Trusted by", no 3-card equal-height features.

## To extend

1. **New project page** — copy `content/over-engineer-traffic.json`, edit, build with `field-journal` + chosen colorway.
2. **New vibe** — add a `[data-vibe="name"]` block in `vibes.css` with full token set. Update `build.mjs` FONT_URLS + FAVICONS. Update `DESIGN.md` table.
3. **New colorway** — add a `[data-colorway="name"]` block in `colorways.css` with `--accent` + `--btn-primary-fg` for both themes. Add to `build.mjs` COLORWAYS array.
