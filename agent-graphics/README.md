# Create an EPD Commerce graphic with your own agent

**Who this is for:** partners using the "Create with your own AI agent" prompt on epd.com. The rules in this folder apply only to this workflow. EPD Commerce staff and internal tools follow the root `AGENTS.md` and are not limited by them.

Read the repository's root `AGENTS.md` first for names, claims, and brand rules. This workflow adds partner-specific steps and restrictions on top; it never loosens the brand rules.

## Start here

If you were given only this file's link, everything you need is in the public repository:

- Repository: https://github.com/EasyPayDirect/epd-commerce-brand
- Raw files: `https://raw.githubusercontent.com/EasyPayDirect/epd-commerce-brand/main/<path>`, for example [AGENTS.md](https://raw.githubusercontent.com/EasyPayDirect/epd-commerce-brand/main/AGENTS.md)
- To render, clone or download the repository into your own working directory: `git clone https://github.com/EasyPayDirect/epd-commerce-brand.git`. No token or account is needed.

Then follow the steps below in order. Do not skip the questions in step 2; ask them before you generate anything.

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

1. **Who are you trying to reach with this graphic?** For example business coaches, course creators, ecommerce brands, or agencies. Do not ask the user what part of EPD Commerce to promote. Most people will not know. You choose the message.
2. **Where will you post it?** Offer these sizes:
   - Instagram or Facebook feed post, 4:5 portrait (1080×1350). Recommend this for feed posts.
   - Instagram or Facebook story, or Reel cover (1080×1920)
   - Square post (1080×1080)
   - LinkedIn, X, link preview, or banner (1200×628)
3. **Optional:** your business name, a logo file (transparent PNG), whether you want your logo next to ours or instead of ours, and your partner referral link.

After the answers, pick the message yourself from the approved sources in step 3, based on what that audience cares about. Show the user the headline, body, and CTA you plan to use in one short message and ask if they want changes before you generate the illustration. Offer one or two alternative angles if useful (for example, accepting payments on their current site, subscriptions for recurring clients, or recovering failed payments).

If the user asks for a size not listed, explain the four supported sizes and offer the closest one. Never stretch or crop a finished graphic into another size.

Ask these in one short message. If the user's request already answers some, ask only for what is missing. Never infer a business logo or invent an endorsement.

## 3. Verify messaging and permissions

Read current `data/names.json`, `data/claims.json`, `.well-known/brand-assets.json`, relevant `messaging-kit/` files, and the chosen template.

Use only features with `status: shipped` and approved claims with their attribution. Do not promote beta, in-development, or planned features in partner graphics. If a requested assertion cannot be verified, explain and suggest supported wording. Keep EPD Commerce and Easy Pay Direct distinct. Assets marked `pending` or `no` are not available for partner graphics.

## 4. Choose a supported illustration layout

The standalone renderer implements the public repo's `partner-introduction` and `problem-solution` families. Both allow AI illustrations. Use portrait, story, square, or landscape at native size. Do not stretch or crop a completed graphic to get another format.

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

For story or landscape, use the corresponding example. For portrait, copy any example and set `"format": "portrait1080x1350"`. A recipe's `family` selects the template; `format` selects the native output dimensions. Supply a white or single-color transparent PNG logo for the dark background. It is contained without stretching.

**Logo options.** Set `logo` in the recipe to match what the user asks for:

| `logo` | Result | Needs `partnerLogo` |
|---|---|---|
| `epd-only` | EPD Commerce logo only | No |
| `co-brand` | Business logo, divider, EPD Commerce logo | Yes |
| `partner-only` | Business logo replaces the EPD Commerce logo | Yes |

If `logo` is omitted, the renderer uses `co-brand` when `partnerLogo` is supplied and `epd-only` otherwise. Use `partner-only` when the user asks to use only their logo or to remove the EPD Commerce logo. All three options work in both families and all formats. In `co-brand`, the business logo is never taller than the EPD Commerce logo.

The recipe can retain a `referralLink` for handoff. It is not a clickable destination inside a PNG and is not automatically posted anywhere.

Do not shrink text below the template's fixed type size to force it to fit. Shorten copy when validation fails.

## 7. Inspect and deliver

Inspect the PNG at full size and at a realistic phone preview. Check:

- Correct dimensions, no clipped logo or text, clear logo/headline spacing.
- The subject is relevant and the reference style is consistent.
- No tiny unreadable copy or unintended checkerboard/background box.
- No misleading claims, fake UI, or unapproved partner assets.
- Correct supplied partner logo and the logo option the user asked for.
- Headline/body leave the story UI safe zones clear.

Deliver the PNG, editable JSON recipe, generated illustration, and referral link/caption placement notes. Identify the template and approved message sources used. Do not post or publish.

## Repository permissions

Read/download only. Do not push commits, open pull requests, request write access, or modify remote files. A local working copy and local output files are expected.

## Maintainer notes

The renderer reads templates, the logo, the motif, and backgrounds directly from this repository (`templates/`, `assets/`). There are no copies to keep in sync. `vendor/` holds only the DM Sans and DM Mono font files with their licenses, and the glass material reference.

The generation tool is deliberately not hardcoded to an AI vendor. The partner's agent generates the illustration using its own enabled tools. Rendering has no network calls and needs no secrets.
