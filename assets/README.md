# Assets

Real files only. Never generate, redraw, or alter logos, marks, diagrams, or screenshots. The machine-readable version of this table is the `assets` block in `.well-known/brand-assets.json`.

Partner use: **approved** = partners may use inside studio templates. **pending** = EPD Commerce use only for now. **no** = never in partner graphics.

| Asset | Use | Backgrounds | Cropping | Partner use |
|---|---|---|---|---|
| `logos/epdc-horizontal-white.png` | Primary lockup on dark (transparent) | Dark | Never | approved |
| `logos/epdc-horizontal-navy-on-light.png` | Primary lockup on light | White, pale | Never | approved |
| `logos/epdc-horizontal-on-navy.png` | Lockup on a solid navy tile | Any, as a tile | Never | approved |
| `logos/epdc-horizontal.svg` | Source vector | Dark | Never | approved |
| `logos/epdc-stacked.png` | Square and vertical spaces | White, pale | Never | approved |
| `logos/epdc-mark-on-dark.svg` | Diamond mark alone (white diamond) | Dark | Never | approved |
| `logos/epdc-mark-on-light.svg` | Diamond mark alone (navy diamond) | White, pale | Never | approved |
| `logos/process-now-white.png` | Process Now, only where the two options are explained | Dark | Never | approved |
| `logos/easy-pay-direct-white.png` | Easy Pay Direct, only where the two options are explained | Dark | Never | approved |
| `payment-methods/` | Ways buyers can pay. See `SOURCES.md`. | Dark (white), light (brand color) | Never | pending |
| `diagrams/foundation-diagram.png` | One platform over Process Now and Easy Pay Direct. Qualifier required. | Dark | Never through a card | approved |
| `diagrams/foundation-section.png` | Full Foundation section artwork. Qualifier required. | n/a | Use whole | approved |
| `diagrams/foundation-section.svg` | Source vector (needs General Sans and DM Mono installed) | n/a | n/a | no |
| `epd-commerce-features/<slug>/` | Product screenshots | Dark, white | Whole panels only, never through text or numbers | approved |
| `backgrounds/dark-gradient-*.png` | Template backgrounds, story, square, landscape | n/a | Native size | approved |
| `backgrounds/dark-gradient-highlight-*.png` | Same, with soft blue highlight behind imagery | n/a | Native size | approved |
| `motif/hero-diamonds.svg`, `motif/side-diamonds.svg` | Decorative diamond motif | Dark | May bleed off an edge, never behind body text | approved |

## Notes

- The Foundation artwork is marketing artwork, not a product screenshot. It shows "Often same day", so any graphic using it must include "All applications subject to review. Approval is not guaranteed."
- Backgrounds are rendered from the site's dark section CSS: `linear-gradient(100deg, #002B55 0%, #001D3B 55%, #000E20 100%)`, with the highlight variant adding `radial-gradient(60% 80% at 78% 45%, rgba(40,120,220,.28), transparent 70%)`.
- Numbers in screenshots are sample data. Never reuse them as claims.
