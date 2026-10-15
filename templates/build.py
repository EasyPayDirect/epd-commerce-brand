"""Generates the studio template specs in this folder.

Run: python3 templates/build.py
Writes templates/<family>.json. Edit the tables below, not the JSON.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

FORMATS = {
    "story":     {"w": 1080, "h": 1920, "margin_x": 96, "safe_top": 250, "safe_bottom": 280, "layout": "stack",
                  "logo_h": 80, "gap": 40,
                  "type": {"eyebrow": 28, "headline": 96, "body": 40, "cta": 30, "footnote": 24},
                  "cta_h": 96, "radius": 8},
    "square":    {"w": 1080, "h": 1080, "margin_x": 80, "safe_top": 80, "safe_bottom": 80, "layout": "stack",
                  "logo_h": 60, "gap": 28,
                  "type": {"eyebrow": 24, "headline": 76, "body": 34, "cta": 26, "footnote": 20},
                  "cta_h": 80, "radius": 8},
    "landscape": {"w": 1200, "h": 628, "margin_x": 64, "safe_top": 56, "safe_bottom": 56, "layout": "split",
                  "logo_h": 40, "gap": 18, "text_col": 0.50,
                  "type": {"eyebrow": 18, "headline": 56, "body": 26, "cta": 20, "footnote": 15},
                  "cta_h": 56, "radius": 6},
}

LH = {"eyebrow": 1.2, "headline": 1.05, "body": 1.35, "cta": 1.0, "footnote": 1.3}
# average glyph width as a share of font size, measured on General Sans and DM Mono with template tracking
GLYPH = {"eyebrow": 0.74, "headline": 0.48, "body": 0.47, "cta": 0.66, "footnote": 0.47}

CTA_LABELS = ["GET ACCESS", "SEE PAYMENT OPTIONS", "LEARN MORE"]
PARTNER_CTA_LABELS = ["GET STARTED", "GET ACCESS", "LEARN MORE"]
QUALIFIER = "All applications subject to review. Approval is not guaranteed."

COMMON_AI = {
    "may": [
        "Suggest eyebrow, headline, and body copy using only approved facts from data/claims.json, data/names.json, and messaging-kit/.",
        "Adapt wording for the selected audience within the text limits.",
        "Pick a CTA label from the approved list.",
    ],
    "may_not": [
        "Change the layout, fonts, type sizes, colors, logo, or logo placement.",
        "Add numbers or claims that are not approved in data/claims.json.",
        "Draw, redraw, or alter logos, payment-method marks, product screenshots, or UI.",
        "Use em dashes.",
        "Name banking partners.",
    ],
}

ILLUSTRATION_RULES = [
    "Optional. Generated only inside the illustration area.",
    "Abstract or scene imagery only. No text, numbers, logos, payment-method marks, card brands, UI, dashboards, or screenshots.",
    "Navy, white, and blue palette. No people facing the camera with readable faces in partner graphics.",
    "Never overlaps the headline, body, CTA, logo, or qualifier.",
]

FAMILIES = {
    "payments-benefit": {
        "title": "Payments benefit",
        "purpose": "One payment benefit for a business owner: accept payments on an existing website, the ways buyers can pay, or fast setup.",
        "background": ["dark-gradient", "dark-gradient-highlight"],
        "lines": {"headline": {"story": 4, "square": 3, "landscape": 3}, "body": {"story": 3, "square": 2, "landscape": 2}},
        "image_area": {"kind": "payment-methods-row", "source": "assets/payment-methods/",
                       "rules": ["Real marks only, from assets/payment-methods/. Never generated.",
                                 "Shown in white or single-color on dark, evenly spaced, equal optical height.",
                                 "Show 4 to 8 methods. Never alter, recolor beyond each brand's allowed single-color version, or crop a mark.",
                                 "Partner use pending official brand-owner marks. See assets/payment-methods/SOURCES.md."]},
        "illustration": False,
        "qualifier": "required if approval timing or the $25K figure appears",
        "copy_sources": ["messaging-kit/capabilities/01-transact.md", "messaging-kit/payment-options.md"],
        "example": {"eyebrow": "ACCEPT PAYMENTS", "headline": "Take payments on the website you already have.",
                    "body": "Cards, Apple Pay, Google Pay, PayPal, Venmo, ACH, and buy now, pay later.", "cta": "GET ACCESS"},
    },
    "product-spotlight": {
        "title": "Product spotlight",
        "purpose": "One named feature, what it does, and a real product screenshot.",
        "background": ["dark-gradient", "white"],
        "lines": {"headline": {"story": 3, "square": 2, "landscape": 3}, "body": {"story": 2, "square": 1, "landscape": 2}},
        "image_area": {"kind": "screenshot", "source": "assets/epd-commerce-features/<slug>/",
                       "rules": ["Real screenshot from the feature's images block only. Never generated or redrawn.",
                                 "Scale to fit, keep aspect ratio. Crop only to a whole panel or card, never through text or numbers.",
                                 "12px corner radius (story and square), 8px (landscape). Shadow allowed: elevated card shadow from 04-color.md.",
                                 "Numbers in screenshots are sample data. Never repeat them in the headline or body."]},
        "illustration": False,
        "qualifier": "not required",
        "copy_sources": ["messaging-kit/features/<slug>.md", "data/names.json"],
        "rules_extra": ["Eyebrow is the feature name exactly as in data/names.json, for example THE PROFESSOR.",
                        "Only features with status shipped or beta. Beta features show (beta) in the body."],
        "example": {"eyebrow": "THE PROFESSOR", "headline": "Chat with your data.",
                    "body": "Let The Professor take action.", "cta": "LEARN MORE"},
    },
    "two-payment-options": {
        "title": "Two payment options",
        "purpose": "Explain Process Now and Easy Pay Direct side by side, built on the Foundation section.",
        "background": ["dark-gradient-highlight"],
        "lines": {"headline": {"story": 3, "square": 3, "landscape": 3}, "body": {"story": 2, "square": 1, "landscape": 2}},
        "image_area": {"kind": "option-cards", "source": "assets/logos/process-now-white.png, assets/logos/easy-pay-direct-white.png",
                       "rules": ["Two equal cards, Process Now first. Each card: option logo or name, one fit line, one timing line.",
                                 "Card copy is fixed. Process Now: 'Low-risk, lower-volume businesses. Approval is often same day.' Easy Pay Direct: 'Full underwriting and white-glove service. Typically 1 to 3 days.'",
                                 "Card fill rgba(255,255,255,.06), 1px rgba(141,202,255,.25) border, 16px radius.",
                                 "The Foundation diagram (assets/diagrams/foundation-diagram.png) may replace the cards in landscape only, once approved for partner use."]},
        "illustration": False,
        "qualifier": "always required",
        "fixed_copy": {"headline_default": "Same platform. Same dashboard. Same catalog.",
                       "headline_line_breaks": "One sentence per line, in every format.",
                       "body_default": "Process Now or Easy Pay Direct. Your choice."},
        "copy_sources": ["messaging-kit/payment-options.md", "data/claims.json"],
        "example": {"eyebrow": "TWO WAYS TO PROCESS", "headline": "Same platform.\nSame dashboard.\nSame catalog.",
                    "body": "Process Now or Easy Pay Direct. Your choice.", "cta": "SEE PAYMENT OPTIONS"},
    },
    "problem-solution": {
        "title": "Problem and solution",
        "purpose": "Name a real business problem, then the EPD Commerce answer.",
        "background": ["dark-gradient", "dark-gradient-highlight"],
        "lines": {"headline": {"story": 3, "square": 2, "landscape": 3}, "body": {"story": 3, "square": 2, "landscape": 2}},
        "image_area": {"kind": "illustration", "source": "AI-generated, optional",
                       "rules": ILLUSTRATION_RULES},
        "illustration": True,
        "qualifier": "required if approval timing or the $25K figure appears",
        "slots_extra": {"problem": "Replaces the eyebrow: one short problem statement in DM Mono uppercase, sky accent color. Max 40 characters."},
        "copy_sources": ["messaging-kit/capabilities/", "messaging-kit/features/"],
        "example": {"eyebrow": "FAILED PAYMENTS COST YOU", "headline": "Recover failed payments automatically.",
                    "body": "Revenue Recovery retries soft declines and sends branded emails.", "cta": "LEARN MORE"},
    },
    "partner-introduction": {
        "title": "Partner introduction",
        "purpose": "A partner introduces EPD Commerce to their audience with one partner link.",
        "background": ["dark-gradient", "dark-gradient-highlight"],
        "lines": {"headline": {"story": 3, "square": 2, "landscape": 3}, "body": {"story": 3, "square": 2, "landscape": 2}},
        "image_area": {"kind": "illustration", "source": "AI-generated, optional",
                       "rules": ILLUSTRATION_RULES},
        "illustration": True,
        "qualifier": "always required",
        "co_brand": {"rules": ["Partner logo left, 1px rgba(255,255,255,.35) vertical divider, EPD Commerce logo right.",
                               "Partner logo height never exceeds the EPD Commerce logo height. Partner supplies a white or single-color version.",
                               "No 'powered by' or 'official partner' language unless approved.",
                               "Partner link is the only CTA destination. The EPD Commerce team helps each business choose a processing option."]},
        "copy_sources": ["messaging-kit/payment-options.md", "messaging-kit/capabilities/"],
        "example": {"eyebrow": "A PARTNER INTRODUCTION", "headline": "Accept payments from humans and agents.",
                    "body": "One link. We'll help each business find the right processing option.", "cta": "GET STARTED"},
    },
}


def text_box(fmt, role, x, y, width, lines):
    size = fmt["type"][role]
    h = math.ceil(lines * size * LH[role])
    cpl = int(width / (size * GLYPH[role]))
    return {"x": x, "y": y, "w": width, "h": h, "font_px": size, "max_lines": lines,
            "max_chars": int(cpl * lines * 0.9)}


def build(fam_key, fam, fkey, fmt):
    W, H = fmt["w"], fmt["h"]
    mx, top, bottom, gap = fmt["margin_x"], fmt["safe_top"], fmt["safe_bottom"], fmt["gap"]
    safe = {"x": mx, "y": top, "w": W - 2 * mx, "h": H - top - bottom}
    hl = fam["lines"]["headline"][fkey]; bl = fam["lines"]["body"][fkey]
    slots = {}
    logo_w = int(fmt["logo_h"] * 3.55)
    if fam_key == "partner-introduction":
        slots["partner_logo"] = {"x": mx, "y": top, "w": logo_w, "h": fmt["logo_h"], "fit": "contain, left aligned"}
        slots["logo"] = {"x": mx + logo_w + 2 * gap + 1, "y": top, "w": logo_w, "h": fmt["logo_h"],
                         "asset": "assets/logos/epdc-horizontal-white.png"}
    else:
        slots["logo"] = {"x": mx, "y": top, "w": logo_w, "h": fmt["logo_h"], "asset": "assets/logos/epdc-horizontal-white.png"}

    fn_lines = 2 if fkey != "landscape" else 1
    has_fn = fam["qualifier"] != "not required"
    if fmt["layout"] == "stack":
        colw = W - 2 * mx
        y = top + fmt["logo_h"] + gap * 2
        for role, lines in (("eyebrow", 1), ("headline", hl), ("body", bl)):
            b = text_box(fmt, role, mx, y, colw, lines); slots[role] = b; y += b["h"] + gap
        fn = text_box(fmt, "footnote", mx, 0, colw, fn_lines)
        fn["y"] = H - bottom - fn["h"]
        cta_y = (fn["y"] - gap if has_fn else H - bottom) - fmt["cta_h"]
        img_y = y + gap
        img_h = cta_y - gap * 2 - img_y
        slots["image_area"] = {"x": mx, "y": img_y, "w": colw, "h": img_h}
        slots["cta"] = {"x": mx, "y": cta_y, "w": None, "h": fmt["cta_h"], "font_px": fmt["type"]["cta"]}
        if has_fn: slots["footnote"] = fn
    else:
        colw = int((W - 2 * mx) * fmt["text_col"])
        y = top + fmt["logo_h"] + gap * 2
        for role, lines in (("eyebrow", 1), ("headline", hl), ("body", bl)):
            b = text_box(fmt, role, mx, y, colw, lines); slots[role] = b; y += b["h"] + gap
        fn = text_box(fmt, "footnote", mx, 0, colw, fn_lines); fn["y"] = H - bottom - fn["h"]
        cta_y = (fn["y"] - gap if has_fn else H - bottom) - fmt["cta_h"]
        slots["cta"] = {"x": mx, "y": cta_y, "w": None, "h": fmt["cta_h"], "font_px": fmt["type"]["cta"]}
        if has_fn: slots["footnote"] = fn
        ix = mx + colw + 40
        slots["image_area"] = {"x": ix, "y": top, "w": W - mx - ix, "h": H - top - bottom}
    # sanity: text column must end above the CTA
    assert slots["body"]["y"] + slots["body"]["h"] <= slots["cta"]["y"] - gap, (fam_key, fkey)
    if fmt["layout"] == "stack":
        assert slots["image_area"]["h"] >= 100, (fam_key, fkey, slots["image_area"]["h"])
    slots["image_area"].update({"kind": fam["image_area"]["kind"], "optional": fam["illustration"]})
    slots["cta"].update({"padding_x": int(fmt["cta_h"] * 0.42), "radius": fmt["radius"]})
    return {"canvas": {"w": W, "h": H}, "safe_area": safe, "slots": slots}


def main():
    for key, fam in FAMILIES.items():
        spec = {
            "_generated_by": "templates/build.py. Edit the script, then rerun.",
            "id": key, "title": fam["title"], "purpose": fam["purpose"], "version": "1.0", "updated": "2026-10-15",
            "backgrounds": {b: {f: f"assets/backgrounds/{b}-{f}.png" for f in FORMATS} if b != "white" else "#FFFFFF" for b in fam["background"]},
            "type": {
                "eyebrow": "DM Mono 500, uppercase, 0.14em tracking. #87C5FF on dark, #0056BB on light.",
                "headline": "General Sans 500, sentence case, -0.03em tracking, line height 1.05. White on dark, #0E1422 on light. Optional second-line accent #8DCAFF on dark.",
                "body": "General Sans 400, line height 1.35. #D1D8E7 on dark, #4A5878 on light.",
                "cta": "DM Mono 500, uppercase, 0.04em tracking.",
                "footnote": "General Sans 400, line height 1.3. #8FA0BF on dark, #64748B on light.",
            },
            "flow": "Slots give the maximum box for each element. Eyebrow, headline, and body flow top down: unused lines collapse, and the image area moves up and grows to fill the space. Logo, CTA, and footnote stay fixed.",
            "logo": {"placement": "Top left of the safe area. Never moved, resized, or recolored by AI.",
                     "on_dark": "assets/logos/epdc-horizontal-white.png",
                     "on_light": "assets/logos/epdc-horizontal-navy-on-light.png",
                     "clearspace": "Height of the diamond on all sides."},
            "cta": {"treatment": "Primary button. On dark: white fill, #00499A text. On light: #00499A fill, white text. No shadow, no gradient, no pill shape.",
                    "approved_labels": PARTNER_CTA_LABELS if key == "partner-introduction" else CTA_LABELS,
                    "rule": "Add labels only with marketing approval."},
            "qualifier": {"when": fam["qualifier"], "text": QUALIFIER, "slot": "footnote"},
            "image_area": fam["image_area"],
            "copy_sources": fam["copy_sources"],
            "ai": COMMON_AI,
            "example_copy": fam["example"],
            "formats": {f: build(key, fam, f, FORMATS[f]) for f in FORMATS},
        }
        for extra in ("fixed_copy", "co_brand", "slots_extra", "rules_extra"):
            if extra in fam: spec[extra] = fam[extra]
        # the example copy must fit every format
        for f, v in spec["formats"].items():
            for role in ("eyebrow", "headline", "body"):
                lim = v["slots"][role]["max_chars"]
                assert len(fam["example"][role]) <= lim, (key, f, role, len(fam["example"][role]), lim)
        with open(os.path.join(HERE, f"{key}.json"), "w") as fh:
            json.dump(spec, fh, indent=2); fh.write("\n")
        print("wrote", key)


if __name__ == "__main__":
    main()
