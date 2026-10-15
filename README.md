# EPD Commerce brand

Public brand repository for [EPD Commerce](https://epd.com). Assets, guidelines, and agent instructions live here so any human, tool, or AI agent can pull consistent brand output.

EPD Commerce is a separate brand from Easy Pay Direct. The [Easy Pay Direct brand repository](https://github.com/EasyPayDirect/brand) covers the payment processor. This repository covers the commerce platform.

## Start here

- **AI agents and the design studio:** read [AGENTS.md](AGENTS.md).
- **Names:** [data/names.json](data/names.json). **Claims:** [data/claims.json](data/claims.json).
- **Tokens, components, and assets:** [.well-known/brand-assets.json](.well-known/brand-assets.json).
- **Studio templates:** [templates/](templates/).
- **Guidelines:** [brand-guidelines/](brand-guidelines/). **Copy:** [messaging-kit/](messaging-kit/).

## Structure

```
AGENTS.md                      Start here (points to everything below)
data/
  names.json                   Authoritative names and never-use lists
  claims.json                  Approved numbers, attribution, status, review dates
.well-known/
  brand-assets.json            Tokens, components, asset library with partner-use status
templates/                     Studio template specs, 5 families x story, square, landscape
  build.py, preview.py         Generate specs and review previews
  previews/
brand-guidelines/
  01-brand-at-a-glance.md      Messaging hierarchy and lines
  02-logo-system.md
  03-capabilities.md
  04-color.md                  Colors, dark surfaces, buttons, shadows
  05-typography.md             Type by component and by graphic format
  06-voice-and-copy.md
  07-how-to-talk-about-features.md   Naming and release status
messaging-kit/
  payment-options.md           Process Now and Easy Pay Direct
  capabilities/                Transact, React, Analyze, Create
  features/                    One file per named feature
assets/
  README.md                    Usage, backgrounds, cropping, partner use for every asset
  logos/  payment-methods/  diagrams/  backgrounds/  motif/  epd-commerce-features/
```

## Using this repo with an AI agent

Point the agent at:

```
https://raw.githubusercontent.com/EasyPayDirect/epd-commerce-brand/main/AGENTS.md
```

The agent reads `AGENTS.md` first, then loads `.well-known/brand-assets.json` for structured data, then references specific guideline sections or feature files as needed.

## License

Brand assets are proprietary to Easy Pay Direct. Do not use outside authorized EPD Commerce work.
