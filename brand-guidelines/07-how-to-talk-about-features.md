# 07 How to talk about features

The rules for referring to any named EPD Commerce feature. For what a feature is and does, see `messaging-kit/features/`. For exact names, see `data/names.json`.

## The rules

1. **Feature names are proper nouns.** Capitalize them wherever they appear. "Revenue Recovery," not "revenue recovery." "The Professor," not "the professor."
2. **Use the exact canonical spelling** from `data/names.json`. Do not shorten, translate, or abbreviate. Use the names exactly as they appear in the platform UI.
3. **Do not invent capabilities.** Only describe what the feature file says the feature does.
4. **Attribute agentic behavior specifically.** "The Professor creates a subscription from a plain-English request." "Order Rescue recovers failed one-time orders." Not "our AI handles it."
5. **Do not rename features** to sound more marketing-friendly.
6. **Do not use a feature name as a verb.**
7. **Introduce a feature with what it does, not with its capability name.** The capability name is optional context and, if used, follows the rules in `03-capabilities.md`.

## Release status

Every feature file has a `status` field with one of four values.

| Status | Meaning | How to write about it |
|---|---|---|
| `shipped` | Released and generally available | Present tense |
| `beta` | Released to some or all accounts as a beta | Present tense, always labeled "(beta)" |
| `in-development` | Being built, no confirmed release | Future tense, "coming soon," no dates |
| `planned` | On the roadmap | Do not mention publicly |

Use present tense only after the release is confirmed. A target date or release window is not a confirmed release.

## What each feature file contains

- `canonical_spelling` and `aliases_incorrect`
- `capability` (Transact, React, Analyze, or Create)
- `status` (see above)
- `one_liner`
- `images` (approved screenshots, if any)
- What it is, how it works, and how to talk about it
