import test from "node:test";
import assert from "node:assert/strict";
import sharp from "sharp";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { composeGraphic, escapeMarkup, renderRecipeFile } from "./render.mjs";

let tempDir;
let illustration;
let partnerLogo;

test.before(async () => {
  tempDir = await mkdtemp(path.join(os.tmpdir(), "epdc-graphics-test-"));
  const rgbaFixture = Buffer.from(
    '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="40"><ellipse cx="40" cy="20" rx="30" ry="15" fill="#ec4400"/></svg>',
  );
  illustration = path.join(tempDir, "illustration.png");
  await sharp(rgbaFixture).png().toFile(illustration);
  partnerLogo = path.join(tempDir, "partner.png");
  await sharp(Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="20"><rect width="80" height="20" fill="#ffffff"/></svg>'))
    .png().toFile(partnerLogo);
});

test.after(async () => {
  await rm(tempDir, { recursive: true, force: true });
});

function recipe(family, format) {
  const common = {
    family,
    format,
    illustration,
    background: "social-gradient",
    motif: false,
    copy: {
      eyebrow: family === "partner-introduction" ? "A PARTNER INTRODUCTION" : "PAYMENT RETRIES",
      headline: family === "partner-introduction" ? "Accept payments from humans and agents." : "Recover failed payments automatically.",
      body: family === "partner-introduction"
        ? "One link. We'll help each business find the right processing option."
        : "Revenue Recovery retries soft declines and sends branded emails.",
    },
    cta: family === "partner-introduction" ? "GET STARTED" : "LEARN MORE",
  };
  return common;
}

test("renders exact native dimensions for all six supported family/format combinations", async () => {
  const dimensions = {
    story1080x1920: [1080, 1920],
    square1080x1080: [1080, 1080],
    landscape1200x628: [1200, 628],
  };
  for (const family of ["partner-introduction", "problem-solution"]) {
    for (const format of Object.keys(dimensions)) {
      const { png, notes } = await composeGraphic(recipe(family, format));
      const metadata = await sharp(png).metadata();
      assert.deepEqual([metadata.width, metadata.height], dimensions[format], `${family} ${format}`);
      assert.equal(metadata.format, "png");
      assert.equal(notes.family, family);
      assert.match(notes.fonts, /(General Sans|DM Sans \(approved fallback)/);
    }
  }
});

test("supports transparent illustration and supported partner co-branding", async () => {
  const coBranded = recipe("partner-introduction", "square1080x1080");
  coBranded.partnerLogo = partnerLogo;
  coBranded.illustration = illustration;
  const { png } = await composeGraphic(coBranded);
  const meta = await sharp(png).metadata();
  assert.equal(meta.width, 1080);
  assert.equal(meta.height, 1080);

  const { data, info } = await sharp(png).raw().toBuffer({ resolveWithObject: true });
  const orange = [];
  for (let y = 0; y < info.height; y += 1) {
    for (let x = 0; x < info.width; x += 1) {
      const i = (y * info.width + x) * info.channels;
      if (data[i] > 180 && data[i + 1] < 100 && data[i + 2] < 80) orange.push([x, y]);
    }
  }
  assert.ok(orange.length > 100, "fixture artwork is present in rendered image");
  const xs = orange.map(([x]) => x);
  const ys = orange.map(([, y]) => y);
  const width = Math.max(...xs) - Math.min(...xs);
  const height = Math.max(...ys) - Math.min(...ys);
  assert.ok(width / height > 1.8 && width / height < 2.2, "illustration remains contained without stretch/crop");
});

test("rejects unsupported families, formats, CTA labels, and co-brand combinations", async () => {
  await assert.rejects(composeGraphic({ ...recipe("not-a-template", "square1080x1080") }), /Unsupported family/);
  await assert.rejects(composeGraphic(recipe("partner-introduction", "feed1080x1350")), /Unsupported format/);
  const badCta = recipe("partner-introduction", "square1080x1080");
  badCta.cta = "CONTACT US";
  await assert.rejects(composeGraphic(badCta), /Invalid CTA/);
  const badMode = recipe("problem-solution", "square1080x1080");
  badMode.logo = "partner-large";
  await assert.rejects(composeGraphic(badMode), /Invalid logo/);
  const missingPartner = recipe("problem-solution", "square1080x1080");
  missingPartner.logo = "partner-only";
  await assert.rejects(composeGraphic(missingPartner), /needs partnerLogo/);
  const conflicting = recipe("partner-introduction", "square1080x1080");
  conflicting.logo = "epd-only";
  conflicting.partnerLogo = partnerLogo;
  await assert.rejects(composeGraphic(conflicting), /epd-only/);
  const wrongFamilyProblem = recipe("partner-introduction", "square1080x1080");
  wrongFamilyProblem.copy.problem = "PAYMENTS FAIL";
  await assert.rejects(composeGraphic(wrongFamilyProblem), /only problem-solution/);
});

test("rejects oversized copy, em dashes, beta/prohibited terms, and escaped markup safely", async () => {
  const tooLong = recipe("partner-introduction", "square1080x1080");
  tooLong.copy.headline = "A".repeat(46);
  await assert.rejects(composeGraphic(tooLong), /Oversized headline/);
  const dash = recipe("partner-introduction", "square1080x1080");
  dash.copy.body = "We help businesses — with payments.";
  await assert.rejects(composeGraphic(dash), /em dashes/);
  const beta = recipe("partner-introduction", "square1080x1080");
  beta.copy.body = "This beta helps merchants.";
  await assert.rejects(composeGraphic(beta), /prohibited beta/);
  const partnerClaim = recipe("partner-introduction", "square1080x1080");
  partnerClaim.copy.body = "We are an official partner.";
  await assert.rejects(composeGraphic(partnerClaim), /unapproved partner wording/);
  assert.equal(escapeMarkup('<&"\' >'), "&lt;&amp;&quot;&apos; &gt;");
});

test("rejects missing, corrupt, and opaque illustrations with actionable asset errors", async () => {
  const noIllustration = recipe("partner-introduction", "square1080x1080");
  delete noIllustration.illustration;
  await assert.rejects(composeGraphic(noIllustration), /generated illustration PNG is required/);
  const missing = recipe("partner-introduction", "square1080x1080");
  missing.illustration = path.join(tempDir, "missing.png");
  await assert.rejects(composeGraphic(missing), /Invalid asset for illustration/);

  const corruptFile = path.join(tempDir, "corrupt.png");
  await writeFile(corruptFile, "not a PNG");
  const corrupt = recipe("partner-introduction", "square1080x1080");
  corrupt.illustration = corruptFile;
  await assert.rejects(composeGraphic(corrupt), /Invalid asset for illustration/);

  const opaqueFile = path.join(tempDir, "opaque.png");
  await sharp({ create: { width: 32, height: 24, channels: 3, background: "#224466" } }).png().toFile(opaqueFile);
  const opaque = recipe("partner-introduction", "square1080x1080");
  opaque.illustration = opaqueFile;
  await assert.rejects(composeGraphic(opaque), (error) => error.code === "alphaopaque" && /alpha channel/.test(error.message));

  const boxedFile = path.join(tempDir, "boxed.png");
  await sharp({ create: { width: 32, height: 24, channels: 4, background: "#ffffff" } })
    .extend({ top: 5, bottom: 5, left: 5, right: 5, background: "#00000000" }).png().toFile(boxedFile);
  const boxed = recipe("partner-introduction", "square1080x1080");
  boxed.illustration = boxedFile;
  await assert.rejects(composeGraphic(boxed), /alpha is opaque/);
});

test("recipe-relative asset paths are resolved against the recipe file, not the current directory", async () => {
  const recipeDir = path.join(tempDir, "recipes");
  await mkdir(recipeDir);
  const recipeFile = path.join(recipeDir, "one.json");
  const assetFile = path.join(recipeDir, "figure.png");
  await writeFile(assetFile, await readFile(illustration));
  const input = recipe("partner-introduction", "square1080x1080");
  input.illustration = "./figure.png";
  await writeFile(recipeFile, JSON.stringify(input));
  const { png } = await composeGraphic(input, { recipePath: recipeFile });
  assert.equal((await sharp(png).metadata()).width, 1080);
});

test("CLI file renderer writes PNG while preserving recipe data and optional motif behavior", async () => {
  const recipeFile = path.join(tempDir, "cli-recipe.json");
  const outputFile = path.join(tempDir, "cli-output.png");
  const input = recipe("partner-introduction", "square1080x1080");
  input.illustration = "./illustration.png";
  input.motif = true;
  input.referralLink = "https://example.test/referral";
  const original = JSON.stringify(input);
  await writeFile(recipeFile, original);
  const notes = await renderRecipeFile(recipeFile, outputFile);
  assert.equal((await sharp(outputFile).metadata()).format, "png");
  assert.equal((await sharp(outputFile).metadata()).width, 1080);
  assert.equal(notes.referralLink, input.referralLink);
  assert.equal(await readFile(recipeFile, "utf8"), original);
});

test("supports epd-only, co-brand, and partner-only logos in both families", async () => {
  for (const family of ["partner-introduction", "problem-solution"]) {
    for (const format of ["story1080x1920", "square1080x1080", "landscape1200x628"]) {
      for (const logo of ["epd-only", "co-brand", "partner-only"]) {
        const r = recipe(family, format);
        r.logo = logo;
        if (logo !== "epd-only") r.partnerLogo = partnerLogo;
        const { png, notes } = await composeGraphic(r);
        assert.equal(notes.logo, logo);
        assert.ok(png.length > 1000);
      }
    }
  }
  const defaulted = recipe("problem-solution", "square1080x1080");
  defaulted.partnerLogo = partnerLogo;
  assert.equal((await composeGraphic(defaulted)).notes.logo, "co-brand");
});
