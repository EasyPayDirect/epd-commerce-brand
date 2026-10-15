"""Renders reference previews of every template with real assets and example copy.

Run: python3 templates/preview.py --general-sans <dir with GeneralSans-*.otf> --dm-mono <dir with DMMono-*.ttf>
Writes templates/previews/<family>-<format>.jpg. Previews are for review, not for publishing.
"""
import argparse, glob, io, json, os
import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, "templates")

ap = argparse.ArgumentParser()
ap.add_argument("--general-sans", required=True)
ap.add_argument("--dm-mono", required=True)
a = ap.parse_args()
GS = lambda w: os.path.join(a.general_sans, f"GeneralSans-{w}.otf")
MONO = os.path.join(a.dm_mono, "DMMono-Medium.ttf")

def font(path, px): return ImageFont.truetype(path, px)

def wrap(draw, text, f, width, track):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if measure(draw, t, f, track) <= width: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def measure(draw, t, f, track): return draw.textlength(t, font=f) + track * f.size * max(len(t) - 1, 0)

def text(draw, xy, t, f, fill, track=0.0):
    x, y = xy
    if track == 0: draw.text((x, y), t, font=f, fill=fill); return
    for ch in t:
        draw.text((x, y), ch, font=f, fill=fill); x += draw.textlength(ch, font=f) + track * f.size

def svg_white(path, h):
    s = open(path).read()
    s = s.replace("<svg", '<svg fill="#FFFFFF"', 1)
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(), output_height=h))).convert("RGBA")
    px = im.load()
    for yy in range(im.height):
        for xx in range(im.width):
            r, g, b, al = px[xx, yy]
            if al: px[xx, yy] = (255, 255, 255, al)
    return im

def paste_fit(canvas, im, box, align="center"):
    x, y, w, h = box
    im = im.copy(); im.thumbnail((w, h), Image.LANCZOS)
    ox = x if align == "left" else x + (w - im.width) // 2
    canvas.paste(im, (ox, y + (h - im.height) // 2), im)
    return im.size

def dashed(draw, box, label, f):
    x, y, w, h = box
    for i in range(x, x + w, 18): draw.line([(i, y), (min(i + 9, x + w), y)], fill=(141, 202, 255), width=2); draw.line([(i, y + h), (min(i + 9, x + w), y + h)], fill=(141, 202, 255), width=2)
    for j in range(y, y + h, 18): draw.line([(x, j), (x, min(j + 9, y + h))], fill=(141, 202, 255), width=2); draw.line([(x + w, j), (x + w, min(j + 9, y + h))], fill=(141, 202, 255), width=2)
    tw = draw.textlength(label, font=f); draw.text((x + (w - tw) / 2, y + h / 2 - f.size / 2), label, font=f, fill=(141, 202, 255))

def rounded_shot(path, w, h, r):
    im = Image.open(path).convert("RGBA"); im.thumbnail((w, h), Image.LANCZOS)
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    im.putalpha(m); return im

os.makedirs(os.path.join(T, "previews"), exist_ok=True)
logo = Image.open(os.path.join(ROOT, "assets/logos/epdc-horizontal-white.png")).convert("RGBA")
pm = ["applepay", "googlepay", "paypal", "venmo", "klarna", "afterpay"]

for spec_path in sorted(glob.glob(os.path.join(T, "*.json"))):
    spec = json.load(open(spec_path)); ex = spec["example_copy"]
    for fk, fmt in spec["formats"].items():
        W, H = fmt["canvas"]["w"], fmt["canvas"]["h"]; S = fmt["slots"]
        bgkey = list(spec["backgrounds"].keys())[0]
        bg = Image.open(os.path.join(ROOT, spec["backgrounds"][bgkey][fk])).convert("RGBA")
        c = bg.copy(); d = ImageDraw.Draw(c)
        lab = font(MONO, max(14, S["footnote"]["font_px"] if "footnote" in S else 16))
        # logo(s)
        lg = S["logo"]; paste_fit(c, logo, (lg["x"], lg["y"], lg["w"], lg["h"]), "left")
        if "partner_logo" in S:
            p = S["partner_logo"]; dashed(d, (p["x"], p["y"], p["w"], p["h"]), "PARTNER LOGO", lab)
            dx = p["x"] + p["w"] + (lg["x"] - p["x"] - p["w"]) // 2
            d.line([(dx, p["y"]), (dx, p["y"] + p["h"])], fill=(255, 255, 255, 90), width=1)
        # eyebrow
        e = S["eyebrow"]; fe = font(MONO, e["font_px"])
        text(d, (e["x"], e["y"]), ex["eyebrow"], fe, (135, 197, 255), 0.14)
        # headline
        h = S["headline"]; fh = font(GS("Medium"), h["font_px"])
        lines = [ln for part in ex["headline"].split("\n") for ln in wrap(d, part, fh, h["w"], -0.03)]
        assert len(lines) <= h["max_lines"], (spec["id"], fk, lines)
        for i, ln in enumerate(lines): text(d, (h["x"], h["y"] + i * h["font_px"] * 1.05), ln, fh, (255, 255, 255), -0.03)
        shift = int((h["max_lines"] - len(lines)) * h["font_px"] * 1.05)
        # body
        b = S["body"]; fb = font(GS("Regular"), b["font_px"])
        lines = wrap(d, ex["body"], fb, b["w"], 0)
        assert len(lines) <= b["max_lines"], (spec["id"], fk, lines)
        for i, ln in enumerate(lines): d.text((b["x"], b["y"] - shift + i * b["font_px"] * 1.35), ln, font=fb, fill=(209, 216, 231))
        shift += int((b["max_lines"] - len(lines)) * b["font_px"] * 1.35)
        # image area (flows up in stacked layouts)
        ia = dict(S["image_area"])
        if fk != "landscape": ia["y"] -= shift; ia["h"] += shift
        box = (ia["x"], ia["y"], ia["w"], ia["h"])
        if ia["kind"] == "payment-methods-row":
            n = len(pm); cols = n if fk != "landscape" else 2
            rows = (n + cols - 1) // cols
            cw, rh = ia["w"] // cols, ia["h"] // rows
            mh = int(min(rh, cw) * 0.42) if fk != "landscape" else int(rh * 0.38)
            for i, k in enumerate(pm):
                im = svg_white(os.path.join(ROOT, f"assets/payment-methods/{k}.svg"), mh)
                cx, cy = ia["x"] + (i % cols) * cw, ia["y"] + (i // cols) * rh
                paste_fit(c, im, (cx, cy, cw, rh))
        elif ia["kind"] == "screenshot":
            r = 8 if fk == "landscape" else 12
            shot = rounded_shot(os.path.join(ROOT, "assets/epd-commerce-features/the-professor/1-landscape.png"), ia["w"], ia["h"], r)
            ox = ia["x"] + (ia["w"] - shot.width) // 2; oy = ia["y"] + (ia["h"] - shot.height) // 2
            c.alpha_composite(shot, (ox, oy))
        elif ia["kind"] == "option-cards":
            gap = 24 if fk != "landscape" else 18
            vertical = fk == "landscape"
            cards = [("assets/logos/process-now-white.png", "Low-risk, lower-volume businesses.", "Approval is often same day."),
                     ("assets/logos/easy-pay-direct-white.png", "Full underwriting and white-glove service.", "Typically 1 to 3 days.")]
            fc = font(GS("Regular"), max(15, int(b["font_px"] * 0.62)))
            for i, (lp, l1, l2) in enumerate(cards):
                if vertical: cb = (ia["x"], ia["y"] + i * (ia["h"] + gap) // 2, ia["w"], (ia["h"] - gap) // 2)
                else: cb = (ia["x"] + i * (ia["w"] + gap) // 2, ia["y"], (ia["w"] - gap) // 2, ia["h"])
                x, y, w, hh = cb
                ov = Image.new("RGBA", c.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
                od.rounded_rectangle([x, y, x + w, y + hh], 16, fill=(255, 255, 255, 15), outline=(141, 202, 255, 64), width=1)
                c.alpha_composite(ov); d = ImageDraw.Draw(c)
                pad = int(hh * 0.12)
                lgh = int(hh * 0.30)
                paste_fit(c, Image.open(os.path.join(ROOT, lp)).convert("RGBA"), (x + pad, y + pad, w - 2 * pad, lgh), "left")
                ty = y + pad + lgh + int(pad * 0.8)
                for ln in wrap(d, l1, fc, w - 2 * pad, 0) + wrap(d, l2, fc, w - 2 * pad, 0):
                    d.text((x + pad, ty), ln, font=fc, fill=(209, 216, 231)); ty += int(fc.size * 1.35)
                assert ty <= y + hh, (spec["id"], fk, "card overflow")
        else:
            dashed(d, box, "OPTIONAL ILLUSTRATION AREA", lab)
        # cta
        ct = S["cta"]; fcta = font(MONO, ct["font_px"]); label = ex["cta"]
        tw = measure(d, label, fcta, 0.04); bw = int(tw + 2 * ct["padding_x"])
        d.rounded_rectangle([ct["x"], ct["y"], ct["x"] + bw, ct["y"] + ct["h"]], ct["radius"], fill=(255, 255, 255))
        asc, desc = fcta.getmetrics()
        text(d, (ct["x"] + ct["padding_x"], ct["y"] + (ct["h"] - asc) / 2 + 1), label, fcta, (0, 73, 154), 0.04)
        # footnote
        if "footnote" in S:
            fn = S["footnote"]; ff = font(GS("Regular"), fn["font_px"])
            for i, ln in enumerate(wrap(d, spec.get("footnote_text", ""), ff, fn["w"], 0)):
                d.text((fn["x"], fn["y"] + i * fn["font_px"] * 1.3), ln, font=ff, fill=(143, 160, 191))
        out = os.path.join(T, "previews", f"{spec['id']}-{fk}.jpg")
        c.convert("RGB").save(out, quality=88, optimize=True); print("wrote", os.path.relpath(out, ROOT))
