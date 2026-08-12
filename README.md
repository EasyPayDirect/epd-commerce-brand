# EPD Commerce brand

Public brand repository for [EPD Commerce](https://epd.com). Assets, guidelines, and agent instructions live here so any human, tool, or AI agent can pull consistent brand output.

EPD Commerce is a separate brand from Easy Pay Direct. The [Easy Pay Direct brand repository](https://github.com/EasyPayDirect/brand) covers the payment processor. This repository covers the commerce platform.

## Start here

- **AI agents and design tools:** read [AGENTS.md](AGENTS.md).
- **Machine-readable manifest:** [.well-known/brand-assets.json](.well-known/brand-assets.json).
- **Human-readable guidelines:** [brand-guidelines/](brand-guidelines/).
- **Feature copy:** [messaging-kit/](messaging-kit/).

## Structure

```
.well-known/
  brand-assets.json          Machine-readable manifest of colors, fonts, logos, motif, taglines
AGENTS.md                    Quick-start instructions for AI agents
brand-guidelines/            7 sections of the styled brand guide, as markdown
  01-brand-at-a-glance.md
  02-logo-system.md
  03-pillars-naming.md
  04-color.md
  05-typography.md
  06-voice-and-copy.md
  07-how-to-talk-about-features.md
messaging-kit/               Feature and pillar copy (updates independently of brand guide)
  pillars/
  features/
assets/
  logos/                     Horizontal and stacked lockups in SVG and PNG
  motif/                     Cascading diamond motif in SVG and PNG
```

## Using this repo with an AI agent

Point the agent at:

```
https://raw.githubusercontent.com/EasyPayDirect/epd-commerce-brand/main/AGENTS.md
```

The agent reads `AGENTS.md` first, then loads `.well-known/brand-assets.json` for structured data, then references specific guideline sections or feature files as needed.

## License

Brand assets are proprietary to Easy Pay Direct. Do not use outside authorized EPD Commerce work.
