# EPD Commerce feature images

Product screenshots and UI captures of shipped EPD Commerce features. Use them when writing about EPD Commerce on either site (easypaydirect.com or epd.com).

## Structure

```
assets/epd-commerce-features/
  {feature-slug}/
    1-landscape.png
    2-portrait.png
    3-square.png
```

Filenames tell you the orientation without opening the file:

- `{n}-landscape.png` — aspect > 1.4:1. Body hero, full-width placement.
- `{n}-portrait.png` — aspect < 0.8:1. Sidebar or side-of-paragraph. Never full-width.
- `{n}-square.png` — 0.8:1 to 1.4:1. Center, 60% width, no text wrap.

## Where the metadata lives

Alt text, captions, and placement rules live in the messaging kit:

```
messaging-kit/features/{feature-slug}.md
```

That file has an `images:` frontmatter block that maps each file here to its intended placement, caption, and alt text. This folder mirrors the raw files only. The manifest is the source of truth.

## Currently shipped

- `the-professor/` — plain-English data queries with charts and summaries
- `custom-fields/` — merchant-defined product fields
- `ai-product-landing-pages/` — AI-generated product landing pages

## How the release bot uses these

When Asana marks a feature "released," the bot:

1. Reads the feature name, slugifies it (`The Professor` → `the-professor`)
2. Looks up `messaging-kit/features/{slug}.md` in the EPD Commerce brand repo for canonical copy and the image manifest
3. Loads the raw images from `assets/epd-commerce-features/{slug}/` in whichever repo it's publishing from (Easy Pay Direct repo for easypaydirect.com posts, EPD Commerce repo for epd.com posts)
4. Places them in the blog body per the placement rules in the manifest

## Adding a new feature's images

1. Create `assets/epd-commerce-features/{slug}/` in **both** repos (this repo and the Easy Pay Direct repo).
2. Drop the raw screenshots in. Name them `{n}-{orientation}.png` where orientation is determined by aspect ratio.
3. Update `messaging-kit/features/{slug}.md` in the EPD Commerce repo with the `images:` frontmatter block pointing at the new files.
4. Commit and push both repos.
