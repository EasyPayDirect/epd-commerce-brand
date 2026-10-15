# AGENTS.md: EPD Commerce brand

Read this first. It points to the files that hold the rules. If two files disagree, the `data/` files win.

## Load order

1. `data/names.json`: every brand, option, capability, and feature name, plus never-use lists.
2. `data/claims.json`: every approved number with attribution, status, and required qualifiers.
3. `.well-known/brand-assets.json`: colors, surfaces, components, fonts, and the asset library with partner-use status.
4. `templates/`: studio template specs (story, square, landscape) for five families.
5. `messaging-kit/`: approved copy. `payment-options.md`, `capabilities/`, `features/`.
6. `brand-guidelines/`: human-readable guidelines.

## Rules that never change

1. **Two brands.** EPD Commerce is the platform. Easy Pay Direct is the processor. Never write "EPD" alone to mean Easy Pay Direct.
2. **Lead with payments.** Accept payments, then the two processing options, then the tools. AI-first lines are for AI-focused audiences only.
3. **Exact names only.** Use `data/names.json` and the names in the product UI. The Professor, never The Data Professor.
4. **Approved claims only.** If a number is not approved in `data/claims.json`, do not use it. Keep its attribution and qualifier.
5. **No em dashes.** Use commas, periods, or parentheses.
6. **Sentence case.** DM Mono eyebrows, labels, and buttons are uppercase.
7. **Never name banking partners.** Say "one of our banking partners."
8. **Release status.** Present tense only after a confirmed release. See `brand-guidelines/07-how-to-talk-about-features.md`.

## Generating images

1. Start from a template in `templates/`. The template controls logo, type, colors, layout, and CTA.
2. Composite real files from `assets/`. Never generate or redraw logos, payment marks, diagrams, screenshots, or UI.
3. AI illustrations only inside a template's image area, in families that allow them, with no text, logos, or UI.
4. Use backgrounds from `assets/backgrounds/`. Dark sections never fade to white.
5. Check each asset's `partner_use` before using it in partner graphics.

## Writing copy

1. Open the relevant file in `messaging-kit/` before writing about a feature, capability, or processing option.
2. If a feature has no file, or its status is `planned`, do not mention it.
3. Follow `brand-guidelines/06-voice-and-copy.md`.

## Blog body images

Approved screenshots live in `assets/epd-commerce-features/<slug>/`, indexed by the `images:` block in each `messaging-kit/features/<slug>.md`.

1. No `images:` block means no approved screenshots. Run the blog text-only.
2. `images.hero` goes at the top. `images.gallery` entries go where their `placement` says: `after-what-it-does`, `after-how-it-works`, `after-how-to-talk`, or `sidebar` (float right, 40% width).
3. Orientation: `landscape` full width with caption below, `portrait` sidebar only, `square` centered at 60% width.
4. Every image gets its alt text from the manifest.
5. Maximum 1 hero and 3 body images, spread evenly, never inside the intro paragraph.
6. Never generate synthetic screenshots.
