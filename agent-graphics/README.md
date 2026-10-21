# Create an EPD Commerce graphic with your own agent

**Who this is for:** partners using the "Create with your own AI agent" prompt on epd.com. The rules in this folder apply only to this workflow. EPD Commerce staff and internal tools follow the root `AGENTS.md` and are not limited by them.

Read the repository's root `AGENTS.md` first for names, claims, and brand rules. This workflow adds partner-specific steps and restrictions on top; it never loosens the brand rules.

## 1. Capability check, before asking for a brief

You must be able to:

- Read public repo files and download authentic assets.
- Generate a new illustration using the supplied material/style reference.
- Execute code, install the renderer's dependency through your environment's approved package tooling, and export a downloadable PNG.
- Inspect the final image.

If any required capability is unavailable, explain which capability is missing and stop. Do not pretend to generate an image, use stock artwork, draw an approximate substitute, or silently deliver a no-generation layout.

Agent names do not guarantee capabilities. Check the actual enabled tools. Never ask for a partner's GitHub credentials to read public files.

## 2. Ask for the brief

Collect:

1. What should the graphic promote, and who is the audience?
2. Where will it appear? Square feed (1080×1080), story (1080×1920), or landscape/link-preview/blog-header (1200×628)?
3. Optional: business name, supplied business logo, and partner referral link.

Ask follow-up questions only for missing material. Never infer a business logo or invent an endorsement.

## 3. Verify messaging and permissions

Read current `data/names.json`, `data/claims.json`, `.well-known/brand-assets.json`, relevant `messaging-kit/` files, and the chosen template.

Use only features with `status: shipped` and approved claims with their attribution. Do not promote beta, in-development, or planned features in partner graphics. If a requested assertion cannot be verified, explain and suggest supported wording. Keep EPD Commerce and Easy Pay Direct distinct. Assets marked `pending` or `no` are not available for partner graphics.

## 4. Choose a supported illustration layout

The standalone renderer implements the public repo's `partner-introduction` and `problem-solution` families. Both allow AI illustrations. Use square, story, or landscape at native size. Do not stretch or crop a completed graphic to get another format.

The repo's other families have different image rules. Never put AI illustrations into a screenshot or payment-logo-only family. This renderer intentionally does not implement those families.

For a different format or family, do not invent an "approved" template. Explain the unsupported request and offer one of the supported formats.

## 5. Generate the illustration only

Read `ILLUSTRATION.md`. Download the reference (`vendor/assets/glass-reference.png`) before invoking generation. Generate a new subject that relates to the verified message. Save a transparent PNG such as `work/illustration.png`.

Only illustration pixels may be AI-generated. Logo, text, background, motif, and partner logo are composed separately from authentic files. No generated UI, numbers, payment marks, or text.

The bundled `glass-reference.png` is a material reference, not an output to repeatedly reuse. Its clock/card subject is not the subject of every new image.

## 6. Render

Work in an ordinary local/hosted copy; do not push changes upstream. Node.js 20.3+ is required. Install this directory's `sharp` dependency using your environment's approved package manager.

**Fonts.** General Sans is the brand typeface. Its license does not allow it to be stored in this repository, so download it yourself from [Fontshare](https://www.fontshare.com/fonts/general-sans) (direct download: `https://api.fontshare.com/v2/fonts/download/general-sans`). Put `GeneralSans-Regular.otf` and `GeneralSans-Medium.otf` in `agent-graphics/fonts-local/`. If you cannot download it, the renderer uses DM Sans, the approved fallback, and says so in its output notes. DM Mono is included.

Copy `examples/introduction-square.json` into a work directory and update it with verified copy and the illustration's relative path. Paths in a recipe are relative to that recipe file.

```sh
node render.mjs /absolute/path/to/work/recipe.json /absolute/path/to/work/graphic.png
node --test render.test.mjs
```

For story or landscape, use the corresponding example. A recipe's `family` selects the template; `format` selects the native output dimensions. A supplied partner logo is contained without stretching, and only supported co-branding slots may be used. Supply a white/single-color logo for the dark background.

The recipe can retain a `referralLink` for handoff. It is not a clickable destination inside a PNG and is not automatically posted anywhere.

Do not shrink text below the template's fixed type size to force it to fit. Shorten copy when validation fails.

## 7. Inspect and deliver

Inspect the PNG at full size and at a realistic phone preview. Check:

- Correct dimensions, no clipped logo or text, clear logo/headline spacing.
- The subject is relevant and the reference style is consistent.
- No tiny unreadable copy or unintended checkerboard/background box.
- No misleading claims, fake UI, or unapproved partner assets.
- Correct supplied partner logo, if requested.
- Headline/body leave the story UI safe zones clear.

Deliver the PNG, editable JSON recipe, generated illustration, and referral link/caption placement notes. Identify the template and approved message sources used. Do not post or publish.

## Repository permissions

Read/download only. Do not push commits, open pull requests, request write access, or modify remote files. A local working copy and local output files are expected.

## Maintainer notes

The renderer reads templates, the logo, the motif, and backgrounds directly from this repository (`templates/`, `assets/`). There are no copies to keep in sync. `vendor/` holds only the DM Sans and DM Mono font files with their licenses, and the glass material reference.

The generation tool is deliberately not hardcoded to an AI vendor. The partner's agent generates the illustration using its own enabled tools. Rendering has no network calls and needs no secrets.
