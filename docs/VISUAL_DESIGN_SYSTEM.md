# Visual Design System (Neon Sanctum)

CardForge now ships with a cinematic visual layer designed for strong first impression and operational readability.

## Art assets
Generated with FAL image generation and saved locally:
- `apps/web/assets/hero-bg.png` (hero command sanctum)
- `apps/web/assets/nebula-bg.png` (ambient data nebula)
- `apps/web/assets/card-overlay.png` (ornamental card texture)

## Design language
- Pure dark background with neon cyan/magenta highlights
- Glassmorphism control panels
- High-contrast glowing CTA buttons
- Metallic neon card borders with animated atmosphere
- Chart panels embedded directly in each dataset card

## Why this matters for agents
- Better visual salience for key state changes
- Immediate differentiation of card categories and status blocks
- Improved scan-speed in high-cardinality decks

## Safe customization points
- Color tokens: `apps/web/styles.css` (`--accent`, `--accent2`, `--accent3`)
- Background layering: `.bg-hero`, `.bg-nebula`, `.bg-vignette`
- Card frame intensity: `.card-overlay` opacity and `.card::after` gradient

## Regenerating visuals
If you want fresh style packs:
1. Generate new images with `image_generate` (or ComfyUI workflow).
2. Replace files in `apps/web/assets/` with same names.
3. Keep dimensions high-res (recommended 1920px+ width).
4. Refresh browser cache.
