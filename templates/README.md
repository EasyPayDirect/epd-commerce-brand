# Studio templates

Specs for the EPD Commerce design studio. Each family comes in four formats:

| Format | Size | Safe area |
|---|---|---|
| Story | 1080 × 1920 | 96px sides, 250px top, 280px bottom (clear of platform UI) |
| Portrait (4:5 feed) | 1080 × 1350 | 80px all sides. Uses story line counts at smaller type sizes. |
| Square | 1080 × 1080 | 80px all sides |
| Landscape | 1200 × 628 | 64px sides, 56px top and bottom. Text left, image right. |

## Families

| File | Family | Image area | AI illustration |
|---|---|---|---|
| [payments-benefit.json](payments-benefit.json) | Payments benefit | Real payment-method marks | No |
| [product-spotlight.json](product-spotlight.json) | Product spotlight | Real product screenshot | No |
| [two-payment-options.json](two-payment-options.json) | Two payment options | Process Now and Easy Pay Direct cards | No |
| [problem-solution.json](problem-solution.json) | Problem and solution | Optional illustration | Yes |
| [partner-introduction.json](partner-introduction.json) | Partner introduction | Optional illustration, co-branded logos | Yes |

Previews with example copy are in [previews/](previews/). They are for review, not for publishing. Finished, approved examples are in [../assets/examples/](../assets/examples/).

## Who controls what

**The template controls:** logo file and placement, fonts, type sizes, colors, background, layout, spacing, and CTA style.

**AI may:**

- Suggest eyebrow, headline, and body copy from approved facts only (`data/claims.json`, `data/names.json`, `messaging-kit/`).
- Adapt wording for the selected audience within each slot's `max_chars` and `max_lines`.
- Pick a CTA label from the template's `approved_labels`.
- Generate an optional illustration, only inside the image area of families that allow it.

**AI may not:** change the layout or styling, add unapproved numbers, draw or alter logos, payment-method marks, screenshots, or UI, use em dashes, or name banking partners.

## Reading a spec

- `formats.<format>.slots` gives each element's box in px: `x`, `y`, `w`, `h`. Text slots also give `font_px`, `max_lines`, and `max_chars`.
- `flow`: eyebrow, headline, and body flow top down. Unused lines collapse, and the image area moves up and grows. Logo, CTA, and footnote stay fixed.
- `copy_sources` lists the files AI must draw copy from.

## Editing

Edit the tables in `build.py`, then run:

```
python3 templates/build.py
python3 templates/preview.py --general-sans <folder with GeneralSans-*.otf> --dm-mono <folder with DMMono-*.ttf>
```

`build.py` checks that text fits above the CTA and that the example copy fits every format. `preview.py` checks that example copy wraps within each slot.
