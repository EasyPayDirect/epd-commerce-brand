# 05 Typography

Two typefaces: **General Sans** for headlines and body, **DM Mono** for eyebrows, labels, and buttons. Sentence case everywhere except DM Mono text, which is uppercase.

Fallbacks: General Sans → DM Sans, Inter, system-ui. DM Mono → JetBrains Mono, Menlo.

## Website components

Measured from the live epd.com site.

| Component | Font | Size / line height | Weight | Tracking | Color |
|---|---|---|---|---|---|
| Hero headline | General Sans | 38 / 1.12 (34 tablet, 30 mobile) | 500 | -0.025em | White on dark |
| Feature section headline (dark) | General Sans | 60 / 0.98 | 540 | -0.052em | White, second line `#8DCAFF` |
| Section headline (light) | General Sans | 40 / 1.15 | 500 | -1px | `#000000` to `#0E1422` |
| Card headline | General Sans | 22 to 28 / 1.2 | 500 | -0.01em | |
| Lede | General Sans | 18 / 1.55 | 400 | 0 | `#D1D8E7` on dark, `#4A5878` on light |
| Body | General Sans | 16 / 1.6 | 400 | 0 | Same as lede |
| Small body | General Sans | 14 / 1.5 | 400 | 0 | |
| Eyebrow | DM Mono | 12 to 14 / 1.2 | 500 | 0.12em to 0.16em | `#0056BB` on light, `#87C5FF` on dark |
| Label / pill | DM Mono | 11 to 12 / 1.2 | 500 | 0.08em | |
| Button | DM Mono | 14 / 1 | 500 | 0.42px (0.03em) | See `04-color.md` |
| Text link CTA | DM Mono | 14 / 1 | 500 | 0.06em | `#0056BB`, hover `#003C7E` |

Eyebrows may start with a short 24px horizontal rule in the same color, as in the site's "THE FOUNDATION" eyebrow. Draw the rule as a line. Never type it as a dash character.

## Social and partner graphics

Sizes are in px at the template's native size. Template-specific limits are in `templates/`.

| Element | Story 1080×1920 | Square 1080×1080 | Landscape 1200×628 |
|---|---|---|---|
| Headline (General Sans 500, -0.03em, lh 1.05) | 96 | 76 | 56 |
| Headline max lines | 4 | 3 | 2 |
| Subhead / body (General Sans 400, lh 1.35) | 40 | 34 | 26 |
| Body max lines | 4 | 3 | 2 |
| Eyebrow (DM Mono 500, 0.14em, uppercase) | 28 | 24 | 18 |
| CTA (DM Mono 500, 0.04em, uppercase) | 30 | 26 | 20 |
| Footnote / qualifier (General Sans 400) | 24 | 20 | 15 |
| Minimum text size anywhere | 24 | 20 | 15 |

## Rules

- Sentence case for headlines and body. DM Mono eyebrows, labels, and buttons are uppercase.
- No Title Case. No all-caps General Sans.
- One headline accent per layout at most (the second line in `#8DCAFF` on dark or `#0056BB` on light).
- No italics as decoration. No underlines except body hyperlinks.
- Tabular figures for stats and tables (`font-variant-numeric: tabular-nums`).
- Never letterspace General Sans positively.
