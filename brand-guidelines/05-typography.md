# 05 Typography

Two typefaces. Sentence case. Mono for anything technical.

## The two typefaces

**General Sans**
Headlines, body copy, UI. The workhorse font. Weights 400, 500, 600, 700. Headlines run at 500 to 600 in sentence case.

**DM Mono**
Eyebrows, labels, pills, buttons, stat numbers. Weights 400 and 500. UPPERCASE with 0.84px letter-spacing at 14px.

## Type scale

Every text role uses one of these steps. Numbers are for the site (px). Multiply by 0.75 for approximate print pt.

| Role | Font | Size / Line | Weight / Track | Where it lives |
|---|---|---|---|---|
| Display | General Sans | 56 / 60 | 600 / -1.5% | Hero headline only |
| H1 | General Sans | 40 / 46 | 600 / -1.0% | Section headlines |
| H2 | General Sans | 28 / 34 | 600 / -0.5% | Card headlines, feature titles |
| H3 | General Sans | 20 / 26 | 600 / 0 | Sub-section headlines |
| Lede | General Sans | 18 / 28 | 400 / 0 | Paragraph directly under a headline |
| Body | General Sans | 16 / 26 | 400 / 0 | Default paragraph copy |
| Body Small | General Sans | 14 / 22 | 400 / 0 | Card body, footnotes, captions |
| Micro | General Sans | 12 / 18 | 500 / 0 | Table headers, legal text |
| Eyebrow | DM Mono | 12 / 16 | 500 / +14% | Uppercase label above headlines |
| Button / CTA | General Sans | 16 / 20 | 400 / 0 | Primary CTA text (soft off-white) |
| Mono label | DM Mono | 11 / 14 | 500 / +14% | Pills, stat labels, tags |

## Rules

- Sentence case for everything except DM Mono eyebrows, pills, and buttons (which are UPPERCASE).
- No underlined text except hyperlinks in body copy.
- No italics as decoration. Italics only for actual titles of works.
- Numbers use tabular figures (`font-variant-numeric: tabular-nums`) in tables, stats, and data readouts.
- Line-height ratio is 1.15 for headlines, 1.6 for body copy. Never tighter, never looser.
- Letter-spacing is 0 by default. Mono eyebrows and pills use +14% (0.84px at 12px) for legibility at small sizes.
