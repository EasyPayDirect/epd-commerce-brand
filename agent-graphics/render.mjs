import sharp from "sharp";
import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
// Templates and brand assets are read from the brand repository root, never from a copy.
const ROOT = path.resolve(HERE, "..");
const TEMPLATES = Object.freeze({
  "partner-introduction": path.join(ROOT, "templates/partner-introduction.json"),
  "problem-solution": path.join(ROOT, "templates/problem-solution.json"),
});
const LOGO_FILE = path.join(ROOT, "assets/logos/epdc-horizontal-white.png");
const MOTIF_FILE = path.join(ROOT, "assets/motif/side-diamonds.svg");

// General Sans is the brand typeface. Its license does not allow redistribution, so it is
// not stored here. If GeneralSans-Regular.otf and GeneralSans-Medium.otf are placed in
// fonts-local/ (see README), they are used. Otherwise DM Sans, the approved fallback, is used.
const LOCAL_FONTS = path.join(HERE, "fonts-local");
const GS_REGULAR = path.join(LOCAL_FONTS, "GeneralSans-Regular.otf");
const GS_MEDIUM = path.join(LOCAL_FONTS, "GeneralSans-Medium.otf");
const HAS_GENERAL_SANS = existsSync(GS_REGULAR) && existsSync(GS_MEDIUM);
const MONO_FILE = path.join(HERE, "vendor/fonts/DM-Mono.ttf");
function sansFont(weight) {
  if (HAS_GENERAL_SANS) return { file: weight >= 500 ? GS_MEDIUM : GS_REGULAR, family: "General Sans" };
  return { file: path.join(HERE, "vendor/fonts/DM-Sans.ttf"), family: "DM Sans" };
}
function fontFor(role, weight) {
  if (role === "eyebrow" || role === "problem" || role === "cta") return { file: MONO_FILE, family: "DM Mono" };
  return sansFont(weight);
}
const FORMAT_ALIASES = Object.freeze({
  story: "story",
  "1080x1920": "story",
  story1080x1920: "story",
  square: "square",
  "1080x1080": "square",
  square1080x1080: "square",
  landscape: "landscape",
  "1200x628": "landscape",
  landscape1200x628: "landscape",
});
const PROHIBITED = /\b(?:beta|basis theory|nmi|maverick|pillars?|powered\s+by|official\s+partner)\b/i;

export function escapeMarkup(value) {
  return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}

export function validateCopy(value, field = "copy") {
  if (typeof value !== "string") throw new Error(`Invalid ${field}: expected text.`);
  if (value.includes("—")) throw new Error(`Invalid ${field}: em dashes are not permitted.`);
  if (PROHIBITED.test(value)) throw new Error(`Invalid ${field}: contains prohibited beta, internal/vendor, or unapproved partner wording.`);
}

function failAsset(label, file, cause) {
  const err = new Error(`Invalid asset for ${label}: ${file}${cause ? ` (${cause.message})` : ""}`);
  err.code = "invalidasset";
  return err;
}

async function readPng(file, label) {
  try {
    const bytes = await readFile(file);
    const metadata = await sharp(bytes, { limitInputPixels: 40_000_000 }).metadata();
    if (metadata.format !== "png" || !metadata.width || !metadata.height) {
      throw new Error("expected a readable PNG");
    }
    return { bytes, metadata };
  } catch (error) {
    throw failAsset(label, file, error);
  }
}

async function imageHasUsableAlpha(file) {
  const { bytes, metadata } = await readPng(file, "illustration");
  if (!metadata.hasAlpha || metadata.channels !== 4) {
    const error = new Error("illustration PNG must contain a real alpha channel");
    error.code = "alphaopaque";
    throw error;
  }
  const trimmed = await sharp(bytes).trim({ background: "#00000000", threshold: 8 }).png().toBuffer();
  const { data, info } = await sharp(trimmed).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  let min = 255;
  let max = 0;
  let nonEmpty = false;
  let transparent = 0;
  for (let i = 3; i < data.length; i += info.channels) {
    min = Math.min(min, data[i]);
    max = Math.max(max, data[i]);
    if (data[i] > 0) nonEmpty = true;
    if (data[i] < 20) transparent++;
  }
  if (!nonEmpty) throw failAsset("illustration", file, new Error("image is fully transparent"));
  if (min === 255 || max === 0 || transparent / (info.width * info.height) < 0.03) {
    const error = new Error("illustration alpha is opaque; provide a transparent PNG");
    error.code = "alphaopaque";
    throw error;
  }
  return { bytes: trimmed, metadata };
}

function formatKey(recipe) {
  const raw = recipe.format ?? recipe.size;
  const key = FORMAT_ALIASES[raw];
  if (!key) throw new Error(`Unsupported format "${raw ?? ""}". Use story1080x1920, square1080x1080, or landscape1200x628.`);
  return key;
}

function lineHeight(slot, role) {
  if (role === "headline") return slot.font_px * 1.05;
  if (role === "body") return slot.font_px * 1.35;
  if (role === "eyebrow" || role === "problem") return slot.h;
  return slot.font_px * 1.3;
}

async function renderTextLine(text, fontFile, fontFamily, size, spacing, color = "#FFFFFF", weight = 400) {
  const markup = `<span foreground="${color}" letter_spacing="${Math.round(spacing * 1024)}" weight="${weight}">${escapeMarkup(text)}</span>`;
  return sharp({
    text: {
      text: markup,
      font: `${fontFamily} ${size}`,
      fontfile: fontFile,
      rgba: true,
      dpi: 72,
      wrap: "none",
    },
  }).png().toBuffer();
}

async function measureLines(value, slot, role) {
  const text = value.trim();
  if (!text) return [];
  validateCopy(text, role);
  const maxChars = slot.max_chars ?? Infinity;
  const charCount = [...text].length;
  if (charCount > maxChars) {
    throw new Error(`Oversized ${role}: ${charCount} characters exceeds the template limit of ${maxChars}.`);
  }
  const weight = role === "body" ? 400 : 500;
  const { file: fontFile, family: fontFamily } = fontFor(role, weight);
  const tracking = role === "eyebrow" || role === "problem" ? 0.14 : role === "headline" ? -0.03 : 0;
  const spacing = slot.font_px * tracking;
  const words = text.split(/\s+/);
  const lines = [];
  let current = "";
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    const bytes = await renderTextLine(candidate, fontFile, fontFamily, slot.font_px, spacing, "#FFFFFF", weight);
    const meta = await sharp(bytes).metadata();
    if (meta.width > slot.w) {
      if (!current) throw new Error(`Oversized ${role}: a word cannot fit at the fixed ${slot.font_px}px type size.`);
      lines.push(current);
      current = word;
      const wordBytes = await renderTextLine(word, fontFile, fontFamily, slot.font_px, spacing, "#FFFFFF", weight);
      const wordMeta = await sharp(wordBytes).metadata();
      if (wordMeta.width > slot.w) throw new Error(`Oversized ${role}: a word cannot fit at the fixed ${slot.font_px}px type size.`);
    } else {
      current = candidate;
    }
  }
  if (current) lines.push(current);
  if (lines.length > slot.max_lines) {
    throw new Error(`Oversized ${role}: wraps to ${lines.length} lines; template maximum is ${slot.max_lines}.`);
  }
  const height = lines.length ? Math.ceil(lineHeight(slot, role) * lines.length) : 0;
  if (height > slot.h) {
    throw new Error(`Oversized ${role}: rendered text needs ${height}px but its template slot is ${slot.h}px high.`);
  }
  const rendered = [];
  for (const line of lines) {
    const bytes = await renderTextLine(line, fontFile, fontFamily, slot.font_px, spacing, "#FFFFFF", weight);
    const meta = await sharp(bytes).metadata();
    if (meta.width > slot.w || meta.height > lineHeight(slot, role)) {
      throw new Error(`Oversized ${role}: text does not fit its fixed-size template slot.`);
    }
    rendered.push({ text: line, bytes, width: meta.width, height: meta.height });
  }
  return rendered;
}

function normalizeRecipe(recipe, template, format) {
  if (recipe.family !== template.id) throw new Error(`Unsupported family "${recipe.family}".`);
  if (!template.formats[format]) throw new Error(`Unsupported format "${format}".`);
  if (recipe.background && !template.backgrounds[recipe.background]) {
    throw new Error(`Unsupported background "${recipe.background}" for ${template.id}.`);
  }
  if (recipe.motif !== undefined && typeof recipe.motif !== "boolean") {
    throw new Error("Invalid motif: use true or false.");
  }
  const modes = template.formats[format].logo_modes;
  if (!modes) throw new Error(`Unsupported family for partner graphics: ${template.id} has no logo modes.`);
  const logoMode = recipe.logo ?? (recipe.partnerLogo ? "co-brand" : "epd-only");
  if (!modes[logoMode]) {
    throw new Error(`Invalid logo "${logoMode}". Use one of: ${Object.keys(modes).join(", ")}.`);
  }
  if (logoMode !== "epd-only" && !recipe.partnerLogo) {
    throw new Error(`Logo mode "${logoMode}" needs partnerLogo: a transparent PNG supplied by the business.`);
  }
  if (logoMode === "epd-only" && recipe.partnerLogo) {
    throw new Error('partnerLogo was supplied but logo is "epd-only". Use "co-brand" or "partner-only".');
  }
  const approved = template.cta.approved_labels;
  if (!approved.includes(recipe.cta)) {
    throw new Error(`Invalid CTA "${recipe.cta}". Choose an exact approved label: ${approved.join(", ")}.`);
  }
  if (!recipe.copy || typeof recipe.copy !== "object" || Array.isArray(recipe.copy)) {
    throw new Error("Invalid recipe: copy must be an object.");
  }
  return { ...template.formats[format], format, logoMode, logoLayout: modes[logoMode] };
}

async function fitImage(bytes, box) {
  const contained = await sharp(bytes, { limitInputPixels: 40_000_000 }).rotate()
    .resize(box.w, box.h, { fit: "inside" }).png().toBuffer();
  const metadata = await sharp(contained).metadata();
  return {
    bytes: contained,
    left: box.x + Math.floor((box.w - metadata.width) / 2),
    top: box.y + Math.floor((box.h - metadata.height) / 2),
    width: metadata.width,
    height: metadata.height,
  };
}

/**
 * Compose a local, deterministic partner graphic. Recipe asset paths resolve
 * from recipePath; bundled templates and assets resolve from this module.
 */
export async function composeGraphic(recipe, { recipePath, illustrationPath } = {}) {
  if (!recipe || typeof recipe !== "object") throw new Error("Invalid recipe: expected a JSON object.");
  if (typeof recipe.illustration !== "string" || !recipe.illustration.trim()) {
    throw new Error("A generated illustration PNG is required. Supply recipe.illustration; no image-free fallback is available.");
  }
  const templatePath = TEMPLATES[recipe.family];
  if (!templatePath) throw new Error(`Unsupported family "${recipe.family}". Use partner-introduction or problem-solution.`);
  const template = JSON.parse(await readFile(templatePath, "utf8"));
  const format = formatKey(recipe);
  const layout = normalizeRecipe(recipe, template, format);
  const slots = layout.slots;
  const copy = recipe.copy;

  const eyebrowSlot = slots.eyebrow;
  let eyebrowValue = typeof copy.eyebrow === "string" ? copy.eyebrow.toUpperCase() : copy.eyebrow ?? "";
  let eyebrowRole = "eyebrow";
  if (copy.problem !== undefined) {
    if (recipe.family !== "problem-solution") throw new Error("Unsupported problem copy: only problem-solution supports a problem statement.");
    if (copy.eyebrow) throw new Error("Use either copy.problem or copy.eyebrow, not both.");
    eyebrowValue = copy.problem.toUpperCase();
    eyebrowRole = "problem";
  }
  if (eyebrowRole === "problem") {
    eyebrowSlot.max_chars = Math.min(40, eyebrowSlot.max_chars);
  }

  const eyebrow = await measureLines(eyebrowValue, eyebrowSlot, eyebrowRole);
  const headline = await measureLines(copy.headline, slots.headline, "headline");
  const body = await measureLines(copy.body, slots.body, "body");
  if (!headline.length) throw new Error("Invalid headline: required copy must not be empty.");
  if (!body.length) throw new Error("Invalid body: required copy must not be empty.");

  const backgroundName = recipe.background ?? "social-gradient";
  const backgroundEntry = template.backgrounds[backgroundName];
  const backgroundFile = path.join(ROOT, backgroundEntry[format]);
  const background = await readPng(backgroundFile, `${backgroundName} ${format} background`);
  const { w: canvasW, h: canvasH } = layout.canvas;
  if (background.metadata.width !== canvasW || background.metadata.height !== canvasH) {
    throw failAsset("background", backgroundFile, new Error(`expected ${canvasW}x${canvasH}, got ${background.metadata.width}x${background.metadata.height}`));
  }
  const layers = [];
  if (recipe.motif === true) {
    const motifFile = MOTIF_FILE;
    let motifBuffer;
    try {
      motifBuffer = await readFile(motifFile);
    } catch (error) {
      throw failAsset("motif", motifFile, error);
    }
    const side = Math.round(canvasH * 0.58);
    const motif = await sharp(motifBuffer).resize({ width: side, height: side, fit: "inside" }).png().toBuffer();
    const faded = await sharp(motif).ensureAlpha()
      .linear([1, 1, 1, 0.2], [0, 0, 0, 0]).png().toBuffer();
    layers.push({ input: faded, left: canvasW - side, top: Math.max(0, canvasH - side), blend: "over" });
  }

  const lay = layout.logoLayout;
  let epdLogo = null;
  if (lay.logo) {
    const logoAsset = await readPng(LOGO_FILE, "EPD Commerce logo");
    epdLogo = await fitImage(logoAsset.bytes, lay.logo);
    layers.push({ input: epdLogo.bytes, left: lay.logo.x, top: epdLogo.top });
  }

  if (lay.partner_logo) {
    if (typeof recipe.partnerLogo !== "string") {
      throw new Error("Invalid partnerLogo path: expected a file path string.");
    }
    if (!recipePath && !path.isAbsolute(recipe.partnerLogo)) {
      throw new Error("Invalid partnerLogo path: recipePath is required to resolve relative asset paths.");
    }
    const partnerFile = path.isAbsolute(recipe.partnerLogo)
      ? recipe.partnerLogo
      : path.resolve(path.dirname(recipePath), recipe.partnerLogo);
    const partner = await readPng(partnerFile, "partner logo");
    if (!partner.metadata.hasAlpha) {
      const error = new Error("partner logo must be a transparent PNG");
      error.code = "alphaopaque";
      throw error;
    }
    const box = lay.partner_logo;
    // In co-brand the partner logo never exceeds the EPD Commerce logo height.
    const maxH = epdLogo ? Math.min(box.h, epdLogo.height) : box.h;
    const partnerFit = await fitImage(partner.bytes, { ...box, h: maxH });
    layers.push({ input: partnerFit.bytes, left: box.x, top: box.y + Math.floor((box.h - partnerFit.height) / 2) });
    if (lay.divider_x !== undefined && epdLogo) {
      const divider = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1" height="${epdLogo.height}"><rect width="1" height="${epdLogo.height}" fill="#FFFFFF" fill-opacity=".35"/></svg>`);
      layers.push({ input: divider, left: lay.divider_x, top: epdLogo.top });
    }
  }

  const eyebrowUnused = Math.max(0, eyebrowSlot.h - Math.ceil(eyebrow.length ? lineHeight(eyebrowSlot, eyebrowRole) * eyebrow.length : 0));
  const headlineY = slots.headline.y - eyebrowUnused;
  const headlineUnused = Math.max(0, slots.headline.h - Math.ceil(lineHeight(slots.headline, "headline") * headline.length));
  const bodyY = slots.body.y - eyebrowUnused - headlineUnused;
  const bodyUnused = Math.max(0, slots.body.h - Math.ceil(lineHeight(slots.body, "body") * body.length));
  const shift = eyebrowUnused + headlineUnused + bodyUnused;

  async function addLines(lines, slot, y, role) {
    const step = lineHeight(slot, role);
    const ink = role === "eyebrow" || role === "problem" ? "#87C5FF" : role === "headline" ? "#FFFFFF" : "#D1D8E7";
    for (let i = 0; i < lines.length; i += 1) {
      const line = lines[i];
      const weight = role === "body" ? 400 : 500;
      const { file: fontPath, family } = fontFor(role, weight);
      const tracking = role === "eyebrow" || role === "problem" ? 0.14 : role === "headline" ? -0.03 : 0;
      const spacing = slot.font_px * tracking;
      const input = await renderTextLine(line.text, fontPath, family, slot.font_px, spacing, ink, weight);
      layers.push({ input, left: slot.x, top: Math.round(y + i * step) });
    }
  }
  await addLines(eyebrow, eyebrowSlot, eyebrowSlot.y, eyebrowRole);
  await addLines(headline, slots.headline, headlineY, "headline");
  await addLines(body, slots.body, bodyY, "body");

  if (slots.image_area && recipe.illustration) {
    if (typeof recipe.illustration !== "string") {
      throw new Error("Invalid illustration path: expected a file path string.");
    }
    if (!recipePath && !path.isAbsolute(recipe.illustration)) {
      throw new Error("Invalid illustration path: recipePath is required to resolve relative asset paths.");
    }
    const imageFile = illustrationPath ?? (path.isAbsolute(recipe.illustration)
      ? recipe.illustration
      : path.resolve(path.dirname(recipePath), recipe.illustration));
    const visual = await imageHasUsableAlpha(imageFile);
    const imageSlot = slots.image_area;
    const isLandscape = format === "landscape";
    const box = {
      x: imageSlot.x,
      y: isLandscape ? imageSlot.y : imageSlot.y - shift,
      w: imageSlot.w,
      h: isLandscape ? imageSlot.h : imageSlot.h + shift,
    };
    const fitted = await fitImage(visual.bytes, box);
    layers.push({ input: fitted.bytes, left: fitted.left, top: fitted.top });
  } else if (recipe.illustration) {
    throw new Error(`Unsupported illustration placement for ${format}.`);
  }

  const ctaSlot = slots.cta;
  const ctaFont = MONO_FILE;
  const ctaLabel = recipe.cta;
  const ctaLine = await renderTextLine(ctaLabel, ctaFont, "DM Mono", ctaSlot.font_px, ctaSlot.font_px * 0.04, "#00499A", 500);
  const ctaMeta = await sharp(ctaLine).metadata();
  const ctaW = ctaMeta.width + ctaSlot.padding_x * 2;
  if (ctaW > canvasW - ctaSlot.x) throw new Error("Oversized CTA: approved label does not fit the fixed CTA treatment.");
  const ctaFill = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${ctaW}" height="${ctaSlot.h}"><rect width="${ctaW}" height="${ctaSlot.h}" rx="${ctaSlot.radius}" fill="#FFFFFF"/></svg>`);
  layers.push({ input: ctaFill, left: ctaSlot.x, top: ctaSlot.y });
  layers.push({ input: ctaLine, left: ctaSlot.x + ctaSlot.padding_x, top: ctaSlot.y + Math.floor((ctaSlot.h - ctaMeta.height) / 2) });

  const result = await sharp(background.bytes).composite(layers).png().toBuffer();
  return {
    png: result,
    notes: {
      family: template.id,
      format,
      dimensions: `${canvasW}x${canvasH}`,
      fonts: HAS_GENERAL_SANS ? "General Sans with DM Mono" : "DM Sans (approved fallback for General Sans) with DM Mono",
      logo: layout.logoMode,
      referralLink: recipe.referralLink ?? null,
      reminder: "PNG graphics are not clickable. Referral links are handoff notes only; nothing is posted or sent.",
    },
  };
}

export async function renderRecipeFile(recipeFile, outputFile) {
  const recipePath = path.resolve(recipeFile);
  let recipe;
  try {
    recipe = JSON.parse(await readFile(recipePath, "utf8"));
  } catch (error) {
    throw new Error(`Cannot read recipe JSON at ${recipePath}: ${error.message}`);
  }
  const { png, notes } = await composeGraphic(recipe, { recipePath });
  await sharp(png).toFile(path.resolve(outputFile));
  return notes;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [, , recipeFile, outputFile] = process.argv;
  if (!recipeFile || !outputFile) {
    console.error("Usage: node render.mjs recipe.json output.png");
    process.exitCode = 2;
  } else {
    try {
      const notes = await renderRecipeFile(recipeFile, outputFile);
      console.log(`Rendered ${notes.family} ${notes.format} (${notes.dimensions}) to ${path.resolve(outputFile)}`);
      if (notes.referralLink) console.log(`Referral link handoff note only: ${notes.referralLink}`);
    } catch (error) {
      console.error(error.message);
      process.exitCode = 1;
    }
  }
}
