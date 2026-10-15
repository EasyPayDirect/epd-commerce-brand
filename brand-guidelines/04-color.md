# 04 Color, backgrounds, and buttons

Navy, white, and blue. Values below are measured from the live epd.com site. Machine-readable tokens are in `.well-known/brand-assets.json`.

## Page and surfaces

| Role | Value | Use |
|---|---|---|
| Page | `#FFFFFF` | The page itself is always white |
| Pale | `#EBEDF6` | Light section or card fill |
| Tint | `#F5F7FC` | Subtle card interiors |
| Border | `#E2E8F0` | Card edges, table rules |

## Dark sections

Dark sections are **rounded panels on the white page**, not full-bleed bands that fade into white.

| Token | Value |
|---|---|
| Dark gradient | `linear-gradient(100deg, #002B55 0%, #001D3B 55%, #000E20 100%)` |
| Optional highlight | `radial-gradient(60% 80% at 78% 45%, rgba(40,120,220,.28), transparent 70%)` layered on top |
| Panel radius | 20px |
| Panel inset | 24 to 34px from the page edge on desktop |

Rules:

- Never fade a dark section to white. The old `#003C7E → #6A9BD1 → #FFFFFF` hero gradient is retired.
- The highlight is optional and sits behind imagery or diagrams, never behind body text.
- For graphics, use the ready-made files in `assets/backgrounds/`.

## Social gradient

Brighter gradient used on social and partner graphics (see `assets/examples/`).

| Token | Value |
|---|---|
| Social gradient | `linear-gradient(135deg, #004A9C 0%, #003C7E 45%, #001D3B 100%)` (top left to bottom right) |
| Glow | `radial-gradient(circle at 90% 5%, rgba(0,104,222,.75), rgba(0,87,194,0) 75%)` layered on top |
| Files | `assets/backgrounds/social-gradient-{story,square,landscape}.png` |

White cards (`#FFFFFF`, 32px radius at story size) can sit on the social gradient to hold detailed content.

## Text colors

| Role | On light | On dark |
|---|---|---|
| Headline | `#000000` to `#0E1422` | `#FFFFFF` |
| Headline accent (second line) | `#0056BB` | `#8DCAFF` |
| Body | `#4A5878` | `#D1D8E7` |
| Strong body | `#0E1422` | `#EBEDF6` |
| Eyebrow | `#0056BB` | `#87C5FF` |
| Muted | `#64748B` | `#8FA0BF` |

## Blues

| Role | Hex | Use |
|---|---|---|
| Button blue | `#00499A` | Primary button fill on light, primary button text on dark, secondary button outline on light |
| Link blue | `#0056BB` | Text links, eyebrows, link CTAs |
| Link hover / brand navy | `#003C7E` | Hover state for links |
| Sky accent | `#8DCAFF` / `#87C5FF` | Headline accents and eyebrows on dark only |

## Buttons

All buttons use DM Mono 500, uppercase, 14px, 0.42px letter-spacing, and a 4px radius.

| Button | On light | On dark |
|---|---|---|
| **Primary** | `#00499A` fill, white text | White fill, `#00499A` text |
| **Secondary** | Transparent, 1px `#00499A` outline, `#00499A` text | Transparent, 1px white outline, white text |
| **Text link CTA** | `#0056BB` text, hover `#003C7E`, with → | `#87C5FF` text, with → |
| **Nav CTA** | Not used | Outline style inside the dark nav pill ("GET ACCESS") |

Rules:

- One primary button per view. A secondary may sit next to it.
- No pill-shaped (fully rounded) buttons. No gradient fills.
- Known site inconsistency: the beta form submit uses `#0056BB` with an 8px radius. The standard is `#00499A` with 4px.

## Shadows

Shadows are used selectively, not banned.

| Use | Value |
|---|---|
| Elevated cards and diagrams on light | `0 24px 60px -24px rgba(0,30,80,.35), 0 6px 20px -10px rgba(0,30,80,.18)` |
| Small cards on light | `0 8px 24px -14px rgba(20,30,60,.18)` |
| Nav pill | Soft dark shadow under the pill |

Never use shadows on text or logos. Never use glows, bevels, or colored outer glows.

## Semantic colors (in-product and diagrams only)

| Role | Hex | Use |
|---|---|---|
| Status green | `#3DDC73` | "Ready," "live," and success dots in product UI and diagrams |
| Up delta | `#0E9F5A` | Positive change in charts |
| Error | `#B91C1C` | Errors |

Green never appears as a general marketing accent.

## Retired

- Capability accent colors (purple `#7C3AED`, orange `#EA580C`, emerald `#0E9F5A` as a capability color). Do not use in marketing or partner graphics.
- `#006EE8` as the CTA color. Use `#00499A`.
- `#D1D8E7` as primary button text. Primary buttons use white text on light and `#00499A` text on dark.
