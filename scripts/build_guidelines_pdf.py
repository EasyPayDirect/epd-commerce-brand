"""Build the EPD Commerce Brand Guidelines PDF from this repo.

Text comes from brand-guidelines/*.md, messaging-kit/, data/names.json and
data/claims.json. Visuals come from assets/ and templates/previews/. Rerun this
script after any repo change so the PDF never drifts from the repo.

    python3 scripts/build_guidelines_pdf.py [--fonts <dir with GeneralSans-*.ttf>]

General Sans is not committed (license). The script looks in --fonts,
fonts-local/, agent-graphics/fonts-local/, then falls back to DM Sans.
Output: docs/epd-commerce-brand-guidelines.pdf
"""
import argparse
import datetime as dt
import io
import json
import re
from pathlib import Path

import cairosvg
from PIL import Image as PILImage
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "assets"
OUT = ROOT / "docs" / "epd-commerce-brand-guidelines.pdf"
TODAY = dt.date.today().isoformat()
VERSION = "V3"

# ---------------------------------------------------------------- tokens (04-color.md)
INK = HexColor("#0E1422")
BODY = HexColor("#4A5878")
MUTED = HexColor("#64748B")
LINK = HexColor("#0056BB")
BUTTON = HexColor("#00499A")
NAVY = HexColor("#003C7E")
PALE = HexColor("#EBEDF6")
TINT = HexColor("#F5F7FC")
BORDER = HexColor("#E2E8F0")
WHITE = HexColor("#FFFFFF")
SKY = HexColor("#8DCAFF")
SKY_EYE = HexColor("#87C5FF")
DARK_BODY = HexColor("#D1D8E7")
DARK_STOPS = [HexColor("#002B55"), HexColor("#001D3B"), HexColor("#000E20")]
SOCIAL_STOPS = [HexColor("#004A9C"), HexColor("#003C7E"), HexColor("#001D3B")]

PAGE_W, PAGE_H = letter
M = 0.75 * inch
CW = PAGE_W - 2 * M


# ---------------------------------------------------------------- fonts
def register_fonts(extra):
    cands = [Path(extra)] if extra else []
    cands += [ROOT / "fonts-local", ROOT / "agent-graphics" / "fonts-local",
              Path("/tmp/gs/GeneralSans_Complete/Fonts/WEB/fonts")]
    gs = next((d for d in cands if (d / "GeneralSans-Regular.ttf").exists()), None)
    mono = next((d for d in cands + [Path("/tmp/epd-fonts")] if (d / "DMMono-Medium.ttf").exists()), None)
    if gs:
        pdfmetrics.registerFont(TTFont("Sans", str(gs / "GeneralSans-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("Sans-Medium", str(gs / "GeneralSans-Medium.ttf")))
        pdfmetrics.registerFont(TTFont("Sans-Semibold", str(gs / "GeneralSans-Semibold.ttf")))
    else:
        d = mono
        pdfmetrics.registerFont(TTFont("Sans", str(d / "DMSans-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("Sans-Medium", str(d / "DMSans-Medium.ttf")))
        pdfmetrics.registerFont(TTFont("Sans-Semibold", str(d / "DMSans-Bold.ttf")))
    arrow = next((Path(p) for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                                     "/usr/share/fonts/dejavu/DejaVuSans.ttf"] if Path(p).exists()), None)
    pdfmetrics.registerFont(TTFont("Arrow", str(arrow)))
    pdfmetrics.registerFont(TTFont("Mono", str(mono / "DMMono-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Mono-Medium", str(mono / "DMMono-Medium.ttf")))
    from reportlab.lib.fonts import addMapping
    addMapping("Sans", 0, 0, "Sans"); addMapping("Sans", 1, 0, "Sans-Semibold")
    addMapping("Sans", 0, 1, "Sans"); addMapping("Sans", 1, 1, "Sans-Semibold")
    return bool(gs)


# ---------------------------------------------------------------- styles
def st(name, **kw):
    base = dict(fontName="Sans", fontSize=10, leading=15, textColor=BODY)
    base.update(kw)
    return ParagraphStyle(name, **base)


S = {}


def build_styles():
    S["eyebrow"] = st("eyebrow", fontName="Mono-Medium", fontSize=8.5, leading=12, textColor=LINK, spaceAfter=6)
    S["h1"] = st("h1", fontName="Sans-Medium", fontSize=30, leading=34, textColor=INK, spaceAfter=10)
    S["h2"] = st("h2", fontName="Sans-Medium", fontSize=16, leading=20, textColor=INK, spaceBefore=14, spaceAfter=6)
    S["h3"] = st("h3", fontName="Sans-Medium", fontSize=11.5, leading=15, textColor=INK, spaceBefore=6, spaceAfter=3)
    S["lede"] = st("lede", fontSize=12, leading=18, spaceAfter=8)
    S["body"] = st("body", spaceAfter=6)
    S["bullet"] = st("bullet", leftIndent=12, bulletIndent=0, spaceAfter=4)
    S["small"] = st("small", fontSize=8.5, leading=12.5, textColor=MUTED)
    S["cell"] = st("cell", fontSize=8.5, leading=12)
    S["cell_b"] = st("cell_b", fontName="Sans-Medium", fontSize=8.5, leading=12, textColor=INK)
    S["th"] = st("th", fontName="Mono-Medium", fontSize=7, leading=10, textColor=INK)
    S["cap"] = st("cap", fontName="Mono", fontSize=7, leading=10, textColor=MUTED, spaceBefore=4)
    S["d_eye"] = st("d_eye", fontName="Mono-Medium", fontSize=9, leading=12, textColor=SKY_EYE, spaceAfter=10)
    S["d_title"] = st("d_title", fontName="Sans-Medium", fontSize=44, leading=48, textColor=WHITE, spaceAfter=12)
    S["d_sub"] = st("d_sub", fontSize=13, leading=19, textColor=DARK_BODY)


# ---------------------------------------------------------------- markdown helpers
def inline(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<font name='Sans-Medium' color='#0E1422'>\1</font>", t)
    t = re.sub(r"`([^`]+)`", r"<font name='Mono' size='0.92em' color='#0E1422'>\1</font>", t)
    t = t.replace("size='0.92em'", "")
    t = t.replace("\u2192", "<font name='Arrow'>\u2192</font>")
    return t


def strip_front(text):
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    return text


def md_sections(path):
    """{heading: [blocks]} for '## ' sections; key '' holds the intro."""
    text = strip_front(Path(path).read_text())
    secs, cur, buf = {}, "", []
    for line in text.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            secs[cur] = buf; cur, buf = line[3:].strip(), []
        else:
            buf.append(line)
    secs[cur] = buf
    return {k: parse_blocks(v) for k, v in secs.items()}


def parse_blocks(lines):
    blocks, i = [], 0
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1; continue
        if l.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            blocks.append(("code", "\n".join(lines[i + 1:j]))); i = j + 1; continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append(("table", rows)); continue
        if re.match(r"^\s*[-*] ", l):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*] ", lines[i]):
                items.append(re.sub(r"^\s*[-*] ", "", lines[i])); i += 1
            blocks.append(("ul", items)); continue
        if re.match(r"^\d+\. ", l):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i])); i += 1
            blocks.append(("ol", items)); continue
        if l.startswith("### "):
            blocks.append(("h3", l[4:])); i += 1; continue
        para = [l]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(\||[-*] |\d+\. |#|```)", lines[i]):
            para.append(lines[i]); i += 1
        blocks.append(("p", " ".join(para)))
    return blocks


def table(rows, widths=None, head=True, first_bold=True, font=8.5):
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    cell = st("c", fontSize=font, leading=font * 1.42)
    cellb = st("cb", fontName="Sans-Medium", fontSize=font, leading=font * 1.42, textColor=INK)
    data = []
    for ri, r in enumerate(rows):
        if head and ri == 0:
            data.append([Paragraph(inline(c).upper(), S["th"]) for c in r])
        else:
            data.append([Paragraph(inline(c), cellb if (first_bold and ci == 0) else cell) for ci, c in enumerate(r)])
    if widths is None:
        widths = [CW / ncol] * ncol
    else:
        tot = sum(widths); widths = [CW * w / tot for w in widths]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    sty = [("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDER),
           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
           ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7)]
    if head:
        sty += [("BACKGROUND", (0, 0), (-1, 0), PALE), ("LINEBELOW", (0, 0), (-1, 0), 0, PALE)]
    t.setStyle(TableStyle(sty))
    return t


def render_blocks(blocks, widths=None, skip_tables=False):
    out = []
    for kind, val in blocks:
        if kind == "p":
            out.append(Paragraph(inline(val), S["body"]))
        elif kind == "h3":
            out.append(Paragraph(inline(val), S["h3"]))
        elif kind in ("ul", "ol"):
            for n, it in enumerate(val, 1):
                b = f"{n}." if kind == "ol" else "\u2022"
                out.append(Paragraph(inline(it), S["bullet"], bulletText=b))
            out.append(Spacer(1, 4))
        elif kind == "table" and not skip_tables:
            out.append(table(val, widths)); out.append(Spacer(1, 8))
        elif kind == "code":
            out.append(Paragraph(inline(val).replace("\n", "<br/>"),
                                 st("code", fontName="Mono", fontSize=8, leading=12, textColor=INK,
                                    backColor=TINT, borderPadding=8, spaceBefore=6, spaceAfter=12)))
    return out


# ---------------------------------------------------------------- image helpers
_CACHE = Path("/tmp/epdc-guidelines-cache"); _CACHE.mkdir(exist_ok=True)


def svg_png(svg, width_px=1600):
    out = _CACHE / (Path(svg).stem + f"-{width_px}.png")
    if not out.exists():
        cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=width_px)
    return out


def img(path, w=None, h=None):
    path = Path(path)
    if path.suffix == ".svg":
        path = svg_png(path)
    iw, ih = PILImage.open(path).size
    if w and not h:
        h = w * ih / iw
    elif h and not w:
        w = h * iw / ih
    elif w and h:
        r = min(w / iw, h / ih); w, h = iw * r, ih * r
    return Image(str(path), width=w, height=h)


def gradient_rect(c, x, y, w, h, stops, angle_deg=100, radius=14, highlight=False):
    import math
    p = c.beginPath(); p.roundRect(x, y, w, h, radius)
    c.saveState(); c.clipPath(p, stroke=0, fill=0)
    a = math.radians(angle_deg - 90)  # CSS angle: 90deg = left to right
    cx, cy = x + w / 2, y + h / 2
    L = abs(w * math.cos(a)) + abs(h * math.sin(a))
    dx, dy = math.cos(a) * L / 2, -math.sin(a) * L / 2
    c.linearGradient(cx - dx, cy - dy, cx + dx, cy + dy, stops, positions=[0, .55, 1] if len(stops) == 3 else None,
                     extend=True)
    if highlight:
        src = A / "backgrounds" / ("dark-gradient-highlight-portrait.png" if h > w else "dark-gradient-highlight-landscape.png")
        iw, ih = PILImage.open(src).size
        r = max(w / iw, h / ih); dw, dh = iw * r, ih * r
        c.drawImage(ImageReader(str(src)), x + (w - dw) / 2, y + (h - dh) / 2, dw, dh)
    c.restoreState()


class Panel(Flowable):
    """Rounded dark-gradient panel (04-color.md) holding arbitrary drawing."""

    def __init__(self, w, h, draw=None, stops=DARK_STOPS, angle=100, highlight=False, radius=12):
        super().__init__(); self.width, self.height = w, h
        self.draw_fn, self.stops, self.angle, self.hl, self.r = draw, stops, angle, highlight, radius

    def draw(self):
        gradient_rect(self.canv, 0, 0, self.width, self.height, self.stops, self.angle, self.r, self.hl)
        if self.draw_fn:
            self.draw_fn(self.canv, self.width, self.height)


class Box(Flowable):
    def __init__(self, w, h, fill, draw=None, stroke=None, radius=8):
        super().__init__(); self.width, self.height = w, h
        self.fill, self.draw_fn, self.stroke, self.r = fill, draw, stroke, radius

    def draw(self):
        c = self.canv
        c.setFillColor(self.fill)
        if self.stroke:
            c.setStrokeColor(self.stroke); c.setLineWidth(.6)
        c.roundRect(0, 0, self.width, self.height, self.r, stroke=1 if self.stroke else 0, fill=1)
        if self.draw_fn:
            self.draw_fn(c, self.width, self.height)


def draw_img(c, path, x, y, w=None, h=None, anchor="sw"):
    path = Path(path)
    if path.suffix == ".svg":
        path = svg_png(path)
    iw, ih = PILImage.open(path).size
    if w and h:
        r = min(w / iw, h / ih); dw, dh = iw * r, ih * r
    elif w:
        dw, dh = w, w * ih / iw
    else:
        dw, dh = h * iw / ih, h
    if anchor == "c":
        x, y = x - dw / 2, y - dh / 2
    c.drawImage(ImageReader(str(path)), x, y, dw, dh, mask="auto")
    return dw, dh


def button(c, x, y, label, fill=None, text=WHITE, outline=None, fs=8.5):
    tw = pdfmetrics.stringWidth(label, "Mono-Medium", fs)
    w, h = tw + 26, fs + 13
    if fill is not None:
        c.setFillColor(fill)
    if outline is not None:
        c.setStrokeColor(outline); c.setLineWidth(.8)
    c.roundRect(x, y, w, h, 2.4, stroke=1 if outline is not None else 0, fill=1 if fill is not None else 0)
    c.setFillColor(text); c.setFont("Mono-Medium", fs)
    c.drawString(x + 13, y + 6.6, label)
    return w


def grid(cells, cols, gap=10, widths=None):
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    rows[-1] += [""] * (cols - len(rows[-1]))
    cw = widths or [(CW - gap * (cols - 1)) / cols + gap] * cols
    t = Table(rows, colWidths=cw, hAlign="LEFT")
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), gap), ("TOPPADDING", (0, 0), (-1, -1), 0),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), gap)]))
    return t


def captioned(flow, cap, w):
    t = Table([[flow], [Paragraph(cap, S["cap"])]], colWidths=[w])
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return t


def framed(path, w, h, bg=TINT):
    """Image centered in a light frame of fixed size."""
    def d(c, W, H):
        draw_img(c, path, W / 2, H / 2, w=W - 12, h=H - 12, anchor="c")
    return Box(w, h, bg, d, stroke=BORDER, radius=6)


# ---------------------------------------------------------------- page chrome
STATE = {"div": ("", "", "")}


class SetDivider(Flowable):
    def __init__(self, *a):
        super().__init__(); self.a = a; self.width = self.height = 0

    def draw(self):
        STATE["div"] = self.a


def chrome(c, doc):
    c.saveState()
    c.setFont("Mono-Medium", 7); c.setFillColor(MUTED)
    c.drawString(M, PAGE_H - 0.5 * inch, "EPD COMMERCE / BRAND GUIDELINES")
    c.drawRightString(PAGE_W - M, PAGE_H - 0.5 * inch, f"{VERSION} / {TODAY}")
    c.setStrokeColor(BORDER); c.setLineWidth(.5)
    c.line(M, PAGE_H - 0.58 * inch, PAGE_W - M, PAGE_H - 0.58 * inch)
    c.drawString(M, 0.45 * inch, "epd.com")
    c.drawRightString(PAGE_W - M, 0.45 * inch, str(doc.page))
    c.restoreState()


def big_panel(c, hl=True):
    inset = 18
    gradient_rect(c, inset, inset, PAGE_W - 2 * inset, PAGE_H - 2 * inset, DARK_STOPS, 100, 20, hl)
    # motif, pasted from assets/motif/hero-diamonds.png, low on the right
    c.saveState()
    p = c.beginPath(); p.roundRect(inset, inset, PAGE_W - 2 * inset, PAGE_H - 2 * inset, 20)
    c.clipPath(p, stroke=0, fill=0)
    draw_img(c, A / "motif" / "hero-diamonds.png", PAGE_W - 330, -40, w=420)
    c.restoreState()


def cover_page(c, doc):
    big_panel(c)
    draw_img(c, A / "logos" / "epdc-horizontal-white.png", 0.85 * inch, PAGE_H - 1.25 * inch, w=150)
    c.setFont("Mono-Medium", 8); c.setFillColor(SKY_EYE)
    c.drawString(0.85 * inch, PAGE_H - 3.0 * inch, f"BRAND GUIDELINES / {VERSION} / {TODAY}")
    c.setFont("Sans-Medium", 58); c.setFillColor(WHITE)
    c.drawString(0.82 * inch, PAGE_H - 3.95 * inch, "Brand")
    c.setFillColor(SKY)
    c.drawString(0.82 * inch, PAGE_H - 4.75 * inch, "guidelines.")
    tf = c.beginText(0.85 * inch, PAGE_H - 5.35 * inch)
    tf.setFont("Sans", 13); tf.setFillColor(DARK_BODY); tf.setLeading(19)
    for ln in ["How EPD Commerce looks, sounds, and talks about", "payments, processing options, and features."]:
        tf.textLine(ln)
    c.drawText(tf)
    c.setFont("Mono", 7); c.setFillColor(HexColor("#8FA0BF"))
    c.drawString(0.85 * inch, 0.75 * inch, "SOURCE OF TRUTH: GITHUB.COM/EASYPAYDIRECT/EPD-COMMERCE-BRAND")
    c.drawString(0.85 * inch, 0.6 * inch, "POWERED BY EASY PAY DIRECT. EPD COMMERCE IS A DBA OF EASY PAY DIRECT LLC.")


def divider_page(c, doc):
    big_panel(c)
    num, title, sub = STATE["div"]
    x = 0.85 * inch
    c.setFont("Mono-Medium", 9); c.setFillColor(SKY_EYE)
    c.drawString(x, PAGE_H / 2 + 70, f"SECTION {num}")
    tp = Paragraph(title, S["d_title"]); tw, th = tp.wrap(5.6 * inch, 300)
    tp.drawOn(c, x - 2, PAGE_H / 2 + 62 - 12 - th)
    p = Paragraph(sub, S["d_sub"]); w, h = p.wrap(4.6 * inch, 200)
    p.drawOn(c, x, PAGE_H / 2 + 62 - 12 - th - 14 - h)
    c.setFont("Mono", 7); c.setFillColor(HexColor("#8FA0BF"))
    c.drawString(x, 0.6 * inch, "EPD COMMERCE / BRAND GUIDELINES")
    c.drawRightString(PAGE_W - x, 0.6 * inch, str(doc.page))


def back_page(c, doc):
    big_panel(c)
    x = 0.85 * inch
    draw_img(c, A / "logos" / "epdc-horizontal-white.png", x, PAGE_H - 1.25 * inch, w=150)
    c.setFont("Mono-Medium", 9); c.setFillColor(SKY_EYE)
    c.drawString(x, PAGE_H / 2 + 80, "QUESTIONS")
    c.setFont("Sans-Medium", 44); c.setFillColor(WHITE)
    c.drawString(x - 2, PAGE_H / 2 + 30, "When in doubt,")
    c.setFillColor(SKY); c.drawString(x - 2, PAGE_H / 2 - 18, "check the repo.")
    p = Paragraph(
        "This PDF is generated from the EPD Commerce brand repository. If anything here disagrees with "
        "the repo, the repo wins, and inside the repo the <font name='Mono'>data/</font> files win. "
        "Ask the marketing team before using anything that is not in the repo.", S["d_sub"])
    w, h = p.wrap(5.0 * inch, 300); p.drawOn(c, x, PAGE_H / 2 - 50 - h)
    c.setFont("Mono-Medium", 9); c.setFillColor(SKY_EYE)
    c.drawString(x, 1.35 * inch, "GITHUB.COM/EASYPAYDIRECT/EPD-COMMERCE-BRAND")
    c.drawString(x, 1.15 * inch, "EPD.COM")
    c.setFont("Mono", 7); c.setFillColor(HexColor("#8FA0BF"))
    c.drawString(x, 0.6 * inch, f"PUBLISHED {TODAY}")


def divider(story, num, title, sub):
    story += [SetDivider(num, title, sub), NextPageTemplate("divider"), PageBreak(),
              Spacer(1, 1), NextPageTemplate("content"), PageBreak()]


def page_head(story, eyebrow, title, lede=None, new_page=True):
    if new_page:
        story.append(PageBreak())
    story.append(Paragraph(eyebrow.upper(), S["eyebrow"]))
    story.append(Paragraph(title, S["h1"]))
    if lede:
        story.append(Paragraph(inline(lede), S["lede"]))
    story.append(Spacer(1, 6))


# ---------------------------------------------------------------- content
def load():
    g = {p.stem[:2]: md_sections(p) for p in sorted((ROOT / "brand-guidelines").glob("*.md"))}
    names = json.loads((ROOT / "data" / "names.json").read_text())
    claims = json.loads((ROOT / "data" / "claims.json").read_text())
    feats = []
    for p in sorted((ROOT / "messaging-kit" / "features").glob("*.md")):
        fm = p.read_text().split("---")[1]
        meta = {}
        for k in ("canonical_spelling", "capability", "status", "one_liner"):
            m = re.search(rf"^{k}:\s*\"?(.+?)\"?\s*$", fm, re.M)
            meta[k] = m.group(1) if m else ""
        meta["slug"] = p.stem
        feats.append(meta)
    caps = []
    for p in sorted((ROOT / "messaging-kit" / "capabilities").glob("*.md"),
                    key=lambda p: int(re.search(r"^order:\s*(\d+)", p.read_text(), re.M).group(1)) if p.stem != "README" else 99):
        if p.stem == "README":
            continue
        txt = p.read_text(); fm = txt.split("---")[1]
        name = re.search(r"^capability:\s*(.+)$", fm, re.M).group(1).strip()
        prom = re.search(r"^promise:\s*\"(.+)\"", fm, re.M).group(1)
        body = strip_front(txt).split("## ", 2)[2] if txt.count("## ") >= 2 else ""
        first = next((l for l in body.splitlines()[1:] if l.strip() and not l.startswith("-")), "")
        caps.append((name, prom, first))
    po = md_sections(ROOT / "messaging-kit" / "payment-options.md")
    return g, names, claims, feats, caps, po


def build(story, g, names, claims, feats, caps, po):
    # ---------- contents
    story.append(NextPageTemplate("content")); story.append(PageBreak())
    story.append(Paragraph("CONTENTS", S["eyebrow"]))
    story.append(Paragraph("What's inside.", S["h1"]))
    story.append(Spacer(1, 10))
    toc = [("01", "Brand at a glance", "What EPD Commerce is, the messaging hierarchy, lines, trust anchors"),
           ("02", "Logo system", "Lockups, files, clearspace, misuse"),
           ("03", "Capabilities", "Create, Analyze, React, Transact"),
           ("04", "Processing options", "Process Now, Easy Pay Direct, payment methods"),
           ("05", "Color and buttons", "Surfaces, dark panels, gradients, buttons, shadows"),
           ("06", "Typography", "Website components and social graphic sizes"),
           ("07", "Voice and copy", "How we sound, do and don't, names"),
           ("08", "Features", "Release status and approved feature copy"),
           ("09", "Making graphics", "Templates, backgrounds, and the composite rule")]
    rows = [[Paragraph(n, st("tn", fontName="Mono-Medium", fontSize=9, textColor=LINK)),
             Paragraph(t, st("tt", fontName="Sans-Medium", fontSize=13, leading=17, textColor=INK)),
             Paragraph(d, S["small"])] for n, t, d in toc]
    t = Table(rows, colWidths=[0.5 * inch, 2.7 * inch, CW - 3.2 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, -1), .5, BORDER),
                           ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(t)
    story.append(Spacer(1, 22))
    note = Table([[Paragraph(
        "<font name='Sans-Medium' color='#0E1422'>The repo is the source of truth.</font> This PDF is generated "
        "from <font name='Mono'>github.com/EasyPayDirect/epd-commerce-brand</font>. Names live in "
        "<font name='Mono'>data/names.json</font>, numbers in <font name='Mono'>data/claims.json</font>, and "
        "approved copy in <font name='Mono'>messaging-kit/</font>. If two sources disagree, the data files win.",
        S["body"])]], colWidths=[CW])
    note.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINT), ("BOX", (0, 0), (-1, -1), .5, BORDER),
                              ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                              ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.append(note)

    # ================================================= 01 BRAND AT A GLANCE
    s = g["01"]
    divider(story, "01", "Brand at a glance.", "What EPD Commerce is, how to lead, and the lines and numbers you can use.")
    story.append(Paragraph("BRAND AT A GLANCE", S["eyebrow"]))
    story.append(Paragraph("What EPD Commerce is.", S["h1"]))
    for k, v in s["What EPD Commerce is"]:
        story.append(Paragraph(inline(v), S["lede"] if not story[-1].__class__ is Paragraph or True else S["body"]))
    story.append(Spacer(1, 6))
    story.append(img(A / "diagrams" / "foundation-section.png", w=CW))
    story.append(Paragraph("assets/diagrams/foundation-section.png, the foundation section on epd.com.", S["cap"]))

    page_head(story, "Brand at a glance", "Messaging hierarchy.")
    mh = s["Messaging hierarchy"]
    story.append(Paragraph(inline(mh[0][1]), S["lede"]))
    ol = next(v for k, v in mh if k == "ol")
    cards = []
    for n, it in enumerate(ol, 1):
        title, rest = re.match(r"\*\*(.+?)\*\*\s*(.*)", it).groups()
        rest = re.sub(r"\s*See `[^`]+`\.?", "", rest)
        inner = [Paragraph(f"0{n}", st("n", fontName="Mono-Medium", fontSize=9, textColor=LINK, spaceAfter=4)),
                 Paragraph(title, st("t", fontName="Sans-Medium", fontSize=14, leading=18, textColor=INK, spaceAfter=4)),
                 Paragraph(inline(rest), S["cell"])]
        cards.append(inner)
    ct = Table([cards], colWidths=[CW / 3] * 3)
    ct.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, -1), TINT),
                            ("LINEAFTER", (0, 0), (1, 0), 6, WHITE), ("BOX", (0, 0), (-1, -1), .5, BORDER),
                            ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                            ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 14)]))
    story.append(ct)
    story.append(Spacer(1, 10))
    for k, v in mh:
        if k == "p" and v != mh[0][1]:
            story.append(Paragraph(inline(v), S["body"]))
    story.append(Paragraph("Lines", S["h2"]))
    lines = s["Lines"]
    for k, v in lines:
        if k == "p":
            m = re.match(r"\*\*(.+?)\*\*\s*(.*)", v)
            if m and m.group(2) and not m.group(2).startswith("("):
                story.append(Paragraph(m.group(1).upper().rstrip(":"), st("le", fontName="Mono-Medium", fontSize=7.5,
                                                                          textColor=LINK, spaceBefore=6, spaceAfter=3)))
                story.append(Paragraph(inline(m.group(2)), st("big", fontName="Sans-Medium", fontSize=17, leading=22,
                                                              textColor=INK, spaceAfter=6)))
            else:
                lab = re.sub(r"\*\*|:", "", v).replace("(", "/ ").replace(")", "").upper()
                story.append(Paragraph(lab, st("le2", fontName="Mono-Medium", fontSize=7.5, textColor=LINK,
                                               spaceBefore=8, spaceAfter=3)))
        elif k == "ul":
            for it in v:
                story.append(Paragraph(inline(it), S["bullet"], bulletText="\u2022"))

    page_head(story, "Brand at a glance", "Two brands. One team.")
    for blk in render_blocks(s["The two brand names"]):
        story.append(blk)
    story.append(Spacer(1, 6))
    story.append(table([["", "EPD Commerce", "Easy Pay Direct"]] + [
        ["Role", next(b for b in names["brands"] if b["canonical"] == "EPD Commerce")["role"],
         next(b for b in names["brands"] if b["canonical"] == "Easy Pay Direct")["role"]],
        ["Never write", ", ".join(next(b for b in names["brands"] if b["canonical"] == "EPD Commerce")["never"]),
         ", ".join(next(b for b in names["brands"] if b["canonical"] == "Easy Pay Direct")["never"])],
    ], widths=[1.1, 2.7, 2.7]))
    story.append(Paragraph("Trust anchors", S["h2"]))
    story.append(Paragraph(inline(s["Trust anchors"][0][1].split(":")[0] + "."), S["body"]))
    appr = [c for c in claims["claims"] if c["status"] == "approved" and c["attribution"] == "Easy Pay Direct"
            and c["id"].startswith("epd-") and "approval" not in c["id"]]

    def stat(c):
        disp = c["display"]
        m = re.match(r"^(\S+)\s+(.*)$", disp)
        big, small = (m.group(1), m.group(2)) if m and not disp.startswith("Billions") else (disp.split()[0], " ".join(disp.split()[1:]))
        return [Paragraph(big, st("sb", fontName="Sans-Medium", fontSize=24, leading=28, textColor=NAVY)),
                Paragraph(small.upper(), st("ss", fontName="Mono-Medium", fontSize=7, leading=10, textColor=MUTED))]
    stt = Table([[stat(c) for c in appr]], colWidths=[CW / len(appr)] * len(appr))
    stt.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), .5, BORDER), ("INNERGRID", (0, 0), (-1, -1), .5, BORDER),
                             ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                             ("LEFTPADDING", (0, 0), (-1, -1), 12)]))
    story.append(stt)
    story.append(Paragraph("Always attributed to Easy Pay Direct. Never shown as EPD Commerce numbers.", S["cap"]))
    page_head(story, "Brand at a glance", "Every claim and its status.",
              "Use approved claims only, with their attribution and soft words. Pending and retired claims never appear in public copy.")
    rows = [["Claim", "Attribution", "Status"]]
    order = {"approved": 0, "pending": 1, "retired": 2}
    for c in sorted(claims["claims"], key=lambda c: order.get(c["status"], 9)):
        rows.append([c["display"], c["attribution"], c["status"].capitalize() +
                     (" (do not use)" if c["status"] != "approved" else "")])
    story.append(table(rows, widths=[3, 2, 1.6], font=8))

    # ================================================= 02 LOGO
    s = g["02"]
    divider(story, "02", "Logo system.", "The diamond mark and the italic COMMERCE wordmark, and how to use them.")
    story.append(Paragraph("LOGO SYSTEM", S["eyebrow"]))
    story.append(Paragraph("The primary lockup.", S["h1"]))
    story.append(Paragraph(inline(s["The primary lockup"][0][1]), S["lede"]))
    story.append(Panel(CW, 1.9 * inch, lambda c, w, h: draw_img(c, A / "logos" / "epdc-horizontal.svg", w / 2, h / 2,
                                                                  w=2.9 * inch, anchor="c")))
    story.append(Paragraph("On dark: epdc-horizontal.svg / epdc-horizontal-white.png", S["cap"]))
    story.append(Spacer(1, 10))
    story.append(Box(CW, 1.9 * inch, WHITE, lambda c, w, h: draw_img(
        c, A / "logos" / "epdc-horizontal-navy.svg", w / 2, h / 2, w=2.9 * inch, anchor="c"), stroke=BORDER, radius=12))
    story.append(Paragraph("On light: epdc-horizontal-navy.svg / epdc-horizontal-navy-on-light.png", S["cap"]))
    story.append(Paragraph("Writing the name", S["h2"]))
    story += render_blocks(s["Writing the name"])

    page_head(story, "Logo system", "Every logo file.")
    cw3 = (CW - 20) / 3
    cells = [
        captioned(Panel(cw3, 1.0 * inch, lambda c, w, h: draw_img(c, A / "logos" / "epdc-mark-on-dark.svg", w / 2, h / 2, h=.62 * inch, anchor="c")), "epdc-mark-on-dark.svg", cw3),
        captioned(Box(cw3, 1.25 * inch, WHITE, lambda c, w, h: draw_img(c, A / "logos" / "epdc-mark-on-light.svg", w / 2, h / 2, h=.62 * inch, anchor="c"), stroke=BORDER), "epdc-mark-on-light.svg", cw3),
        captioned(Box(cw3, 1.25 * inch, WHITE, lambda c, w, h: draw_img(c, A / "logos" / "epdc-stacked.png", w / 2, h / 2, h=.78 * inch, anchor="c"), stroke=BORDER), "epdc-stacked.png", cw3),
        captioned(Box(cw3, 1.25 * inch, NAVY, lambda c, w, h: draw_img(c, A / "logos" / "epdc-horizontal-on-navy.png", w / 2, h / 2, w=w - 4, anchor="c")), "epdc-horizontal-on-navy.png (solid tile)", cw3),
        captioned(Panel(cw3, 1.0 * inch, lambda c, w, h: draw_img(c, A / "logos" / "process-now-white.png", w / 2, h / 2, w=1.25 * inch, anchor="c")), "process-now-white.png", cw3),
        captioned(Panel(cw3, 1.0 * inch, lambda c, w, h: draw_img(c, A / "logos" / "easy-pay-direct-white.png", w / 2, h / 2, w=1.35 * inch, anchor="c")), "easy-pay-direct-white.png", cw3),
    ]
    story.append(grid(cells, 3))
    for k, v in s["Files"]:
        if k == "p":
            story.append(Paragraph(inline(v), S["body"]))
    story.append(Spacer(1, 4))
    story.append(table(next(v for k, v in s["Files"] if k == "table"), widths=[2.7, 2.6, 1.5], font=7.2))

    page_head(story, "Logo system", "Clearspace and misuse.")

    def clear(c, w, h):
        lw = 2.6 * inch
        dw, dh = draw_img(c, A / "logos" / "epdc-horizontal-navy.svg", w / 2, h / 2, w=lw, anchor="c")
        x0, y0 = w / 2 - dw / 2, h / 2 - dh / 2
        pad = dh * .95
        c.setStrokeColor(LINK); c.setDash(3, 3); c.setLineWidth(.7)
        c.rect(x0 - pad, y0 - pad, dw + 2 * pad, dh + 2 * pad)
        c.setDash(); c.setFont("Mono-Medium", 7); c.setFillColor(LINK)
        for (x, y) in [(w / 2, y0 + dh + pad / 2), (w / 2, y0 - pad / 2), (x0 - pad / 2, h / 2), (x0 + dw + pad / 2, h / 2)]:
            c.drawCentredString(x, y - 2.5, "X")
    story.append(Box(CW, 2.0 * inch, TINT, clear, stroke=BORDER, radius=12))
    story.append(Paragraph("X = the height of the diamond mark.", S["cap"]))
    story.append(Spacer(1, 6))
    story += render_blocks(s["Clearspace and minimum size"])
    story.append(Paragraph("What not to do", S["h2"]))
    story += render_blocks(s["What not to do"])

    # ================================================= 03 CAPABILITIES
    s = g["03"]
    divider(story, "03", "Capabilities.", "Four names, always with their promise. CART is the default order.")
    story.append(Paragraph("CAPABILITIES", S["eyebrow"]))
    story.append(Paragraph("Create, Analyze, React, Transact.", S["h1"]))
    story.append(Paragraph(inline(s[""][0][1]), S["lede"]))
    cards = []
    cw2 = (CW - 10) / 2
    for n, (name, prom, first) in enumerate(caps, 1):
        inner = [Paragraph(f"0{n}", st("cn", fontName="Mono-Medium", fontSize=8, textColor=LINK, spaceAfter=4)),
                 Paragraph(name, st("cnm", fontName="Sans-Medium", fontSize=18, leading=22, textColor=INK, spaceAfter=3)),
                 Paragraph(inline(prom), st("cp", fontName="Sans-Medium", fontSize=10, leading=14, textColor=LINK, spaceAfter=5)),
                 Paragraph(inline(first), S["cell"])]
        t = Table([[inner]], colWidths=[cw2])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINT), ("BOX", (0, 0), (-1, -1), .5, BORDER),
                               ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                               ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 14)]))
        cards.append(t)
    story.append(grid(cards, 2))
    story.append(Paragraph("Rules", S["h2"]))
    story += render_blocks(s["Rules"])

    # ================================================= 04 PROCESSING OPTIONS
    divider(story, "04", "Processing options.", inline(po[""][0][1]))
    story.append(Paragraph("PROCESSING OPTIONS", S["eyebrow"]))
    story.append(Paragraph("Same platform. Same dashboard. Same catalog.", S["h1"]))
    story.append(table(next(v for k, v in po["The two processing options"] if k == "table"), widths=[1.2, 2.6, 2.7], font=8))
    for k, v in po["The two processing options"]:
        if k == "p":
            story.append(Paragraph(inline(v), S["body"]))
    story.append(Paragraph("Timing and fit language", S["h2"]))
    story += render_blocks([b for b in po["Timing and fit language"] if b[0] == "ul"])
    story.append(Paragraph("Processing options vs payment methods", S["h2"]))
    story += render_blocks(po["Processing options vs payment methods"])
    marks = ["applepay.svg", "googlepay.svg", "paypal.svg", "venmo.svg", "splitit.png", "klarna.svg", "afterpay.svg", "sezzle.svg"]
    mw = (CW - 7 * 6) / 8
    cells = [framed(A / "payment-methods" / m, mw, .42 * inch, WHITE) for m in marks]
    story.append(grid(cells, 8, gap=6, widths=[mw + 6] * 8))
    story.append(Paragraph("Real marks from assets/payment-methods/. Never redraw them.", S["cap"]))

    page_head(story, "Processing options", "How to talk about them.")
    left = []
    for sec in ("Moving between options", "Partners: one link for both options", "Naming"):
        left.append(Paragraph(sec.replace(": one", ", one"), S["h3"]))
        for blk in po[sec]:
            if blk[0] == "p":
                left.append(Paragraph(inline(blk[1]), S["cell"])); left.append(Spacer(1, 3))
            elif blk[0] == "ul":
                for it in blk[1]:
                    left.append(Paragraph(inline(it), st("cbul", fontSize=8.5, leading=12, leftIndent=10), bulletText="\u2022"))
                left.append(Spacer(1, 3))
        left.append(Spacer(1, 6))
    ew = 1.45 * inch
    capst = st("capsm", fontName="Mono", fontSize=6.3, leading=9, textColor=MUTED, spaceBefore=4)
    right = Table([[img(A / "examples" / "story-process-now.png", w=ew), img(A / "examples" / "story-easy-pay-direct.png", w=ew)],
                   [Paragraph("story-process-now.png", capst), Paragraph("story-easy-pay-direct.png", capst)]],
                  colWidths=[ew + 8, ew + 8])
    right.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                               ("TOPPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    t = Table([[left, [right, Spacer(1, 6), Paragraph("Approved examples. Each names its option and uses the real logo.", S["small"])]]],
              colWidths=[CW - 2 * ew - 30, 2 * ew + 30])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (0, 0), 18)]))
    story.append(t)

    # ================================================= 05 COLOR
    s = g["04"]
    divider(story, "05", "Color and buttons.", "Navy, white, and blue. Values measured from the live epd.com site.")
    story.append(Paragraph("COLOR", S["eyebrow"]))
    story.append(Paragraph("A white page with navy panels.", S["h1"]))
    story.append(Paragraph("Page and surfaces", S["h2"]))
    surf = next(v for k, v in s["Page and surfaces"] if k == "table")[1:]
    sw = (CW - 30) / 4

    def swatch(hexv, name, use):
        def d(c, w, h):
            pass
        b = Box(sw, .8 * inch, HexColor(hexv.strip("`")), None, stroke=BORDER, radius=6)
        return [b, Paragraph(f"<font name='Sans-Medium' color='#0E1422'>{name}</font>  <font name='Mono' size='7.5'>{hexv.strip('`')}</font>",
                             st("swn", fontSize=9, leading=13, spaceBefore=5)), Paragraph(inline(use), S["small"])]
    story.append(grid([swatch(r[1], r[0], r[2]) for r in surf], 4))
    story.append(Paragraph("Dark sections", S["h2"]))
    story.append(Paragraph(inline(s["Dark sections"][0][1]), S["body"]))

    def dark_demo(c, w, h):
        c.setFont("Mono-Medium", 7.5); c.setFillColor(SKY_EYE); c.drawString(22, h - 30, "DARK GRADIENT, 100DEG")
        c.setFont("Sans-Medium", 20); c.setFillColor(WHITE); c.drawString(22, h - 58, "#002B55 to #001D3B")
        c.setFillColor(SKY); c.drawString(22, h - 82, "to #000E20.")
    two = Table([[Panel(CW * .58, 1.55 * inch, dark_demo, highlight=True, radius=14),
                  img(A / "backgrounds" / "social-gradient-landscape.png", w=CW * .38)]],
                colWidths=[CW * .62, CW * .38])
    two.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(two)
    story.append(Paragraph("Left: dark section panel with optional highlight. Right: social gradient, assets/backgrounds/social-gradient-landscape.png.", S["cap"]))
    story.append(Spacer(1, 6))
    story += render_blocks([b for b in s["Dark sections"] if b[0] in ("ul",)])

    page_head(story, "Color", "Gradient tokens and text.")
    story.append(Paragraph("Dark section tokens", S["h3"]))
    story.append(table(next(v for k, v in s["Dark sections"] if k == "table"), widths=[1.4, 5.1], font=7.6))
    story.append(Paragraph("Social gradient tokens", S["h3"]))
    story.append(table(next(v for k, v in s["Social gradient"] if k == "table"), widths=[1.4, 5.1], font=7.6))
    story += [Paragraph(inline(v), S["small"]) for k, v in s["Social gradient"] if k == "p" and v.startswith("White")]
    story.append(Paragraph("Text colors", S["h2"]))
    story.append(table(next(v for k, v in s["Text colors"] if k == "table"), widths=[2.2, 2.1, 2.1]))
    page_head(story, "Color", "Blues and semantic colors.")
    story.append(Paragraph("Blues", S["h2"]))
    blues = next(v for k, v in s["Blues"] if k == "table")[1:]
    cells = []
    for r in blues:
        hx = r[1].strip("`").split(" / ")[0].strip("`")
        cells.append([Box(sw, .6 * inch, HexColor(hx), radius=6),
                      Paragraph(f"<font name='Sans-Medium' color='#0E1422'>{r[0]}</font>", st("bn", fontSize=9, leading=12, spaceBefore=5)),
                      Paragraph(inline(r[1]), st("bh", fontName="Mono", fontSize=7.5, leading=10, textColor=MUTED)),
                      Paragraph(inline(r[2]), S["small"])])
    story.append(grid(cells, 4))
    story.append(Paragraph("Semantic colors (in-product and diagrams only)", S["h2"]))
    story.append(table(next(v for k, v in s["Semantic colors (in-product and diagrams only)"] if k == "table"), widths=[1.4, 1, 4.1]))
    story += [Paragraph(inline(v), S["body"]) for k, v in s["Semantic colors (in-product and diagrams only)"] if k == "p"]
    story.append(Paragraph("Retired", S["h2"]))
    story += render_blocks(s["Retired"])

    page_head(story, "Buttons", "Buttons and shadows.")
    story.append(Paragraph(inline(s["Buttons"][0][1]), S["lede"]))
    bw = (CW - 12) / 2

    def light_btns(c, w, h):
        x = 20; y = h / 2 + 2
        x += button(c, x, y, "GET ACCESS", fill=BUTTON, text=WHITE) + 10
        button(c, x, y, "TALK TO SALES", outline=BUTTON, text=BUTTON)
        c.setFont("Mono-Medium", 8.5); c.setFillColor(LINK); c.drawString(20, y - 22, "LEARN MORE"); c.setFont("Arrow", 8.5); c.drawString(20 + pdfmetrics.stringWidth("LEARN MORE ", "Mono-Medium", 8.5), y - 22, "\u2192")

    def dark_btns(c, w, h):
        x = 20; y = h / 2 + 2
        x += button(c, x, y, "GET ACCESS", fill=WHITE, text=BUTTON) + 10
        button(c, x, y, "TALK TO SALES", outline=WHITE, text=WHITE)
        c.setFont("Mono-Medium", 8.5); c.setFillColor(SKY_EYE); c.drawString(20, y - 22, "LEARN MORE"); c.setFont("Arrow", 8.5); c.drawString(20 + pdfmetrics.stringWidth("LEARN MORE ", "Mono-Medium", 8.5), y - 22, "\u2192")
    bt = Table([[Box(bw, 1.0 * inch, WHITE, light_btns, stroke=BORDER, radius=12), Panel(bw, 1.0 * inch, dark_btns)],
                [Paragraph("On light", S["cap"]), Paragraph("On dark", S["cap"])]], colWidths=[bw + 12, bw])
    bt.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    story.append(bt)
    story.append(Paragraph("Example labels only. Use the approved labels in each template.", S["cap"]))
    story.append(Spacer(1, 6))
    story.append(table(next(v for k, v in s["Buttons"] if k == "table"), widths=[1.2, 2.7, 2.6]))
    story += render_blocks([b for b in s["Buttons"] if b[0] == "ul"])
    story.append(Paragraph("Shadows", S["h2"]))
    story.append(Paragraph(inline(s["Shadows"][0][1]), S["body"]))
    story.append(table(next(v for k, v in s["Shadows"] if k == "table"), widths=[2, 4.5], font=7.6))
    story += [Paragraph(inline(v), S["body"]) for k, v in s["Shadows"][1:] if k == "p"]

    # ================================================= 06 TYPE
    s = g["05"]
    divider(story, "06", "Typography.", "General Sans for headlines and body. DM Mono for eyebrows, labels, and buttons.")
    story.append(Paragraph("TYPOGRAPHY", S["eyebrow"]))
    story.append(Paragraph("Two typefaces.", S["h1"]))
    story.append(Paragraph(inline(s[""][0][1]), S["lede"]))

    def spec(font, name, use, dark):
        def d(c, w, h):
            c.setFillColor(WHITE if dark else INK); c.setFont(font, 64); c.drawString(20, h - 86, "Aa")
            c.setFont("Sans-Medium", 13); c.drawString(20, 34, name)
            c.setFont("Mono-Medium", 7); c.setFillColor(SKY_EYE if dark else LINK); c.drawString(20, 18, use)
        return Panel(bw, 1.9 * inch, d) if dark else Box(bw, 1.9 * inch, TINT, d, stroke=BORDER, radius=12)
    ts = Table([[spec("Sans-Medium", "General Sans", "HEADLINES AND BODY", True),
                 spec("Mono-Medium", "DM Mono", "EYEBROWS, LABELS, BUTTONS", False)]], colWidths=[bw + 12, bw])
    ts.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(ts)
    story.append(Spacer(1, 6))
    story.append(Paragraph(inline(s[""][1][1]), S["small"]))
    story.append(Paragraph("Rules", S["h2"]))
    story += render_blocks(s["Rules"])

    page_head(story, "Typography", "Website components.", "Measured from the live epd.com site.")
    story.append(table(next(v for k, v in s["Website components"] if k == "table"),
                       widths=[1.6, .95, 1.45, .55, 1.0, 1.5], font=7.4))
    story += [Paragraph(inline(v), S["small"]) for k, v in s["Website components"] if k == "p" and "Measured" not in v]
    page_head(story, "Typography", "Social and partner graphics.")
    story.append(Paragraph(inline(s["Social and partner graphics"][0][1]), S["body"]))
    story.append(Spacer(1, 4))
    story.append(table(next(v for k, v in s["Social and partner graphics"] if k == "table"),
                       widths=[2.6, 1, 1, 1, 1], font=7.4))

    # ================================================= 07 VOICE
    s = g["06"]
    divider(story, "07", "Voice and copy.", inline(s[""][0][1]))
    story.append(Paragraph("VOICE AND COPY", S["eyebrow"]))
    story.append(Paragraph("How we sound.", S["h1"]))
    story.append(Paragraph(inline(s["How we sound"][0][1]), S["lede"]))
    story.append(Paragraph("Lead with payments", S["h3"]))
    story.append(Paragraph(inline(s["Lead with payments"][0][1].split(" See ")[0]), S["body"]))
    story.append(Paragraph("Contrast framing", S["h3"]))
    story += render_blocks(s["Contrast framing"])
    do = next(v for k, v in s["Do"] if k == "ul"); dont = next(v for k, v in s["Don't"] if k == "ul")
    n = max(len(do), len(dont))
    rows = [[Paragraph("DO", st("dh", fontName="Mono-Medium", fontSize=8, textColor=WHITE)),
             Paragraph("DON'T", st("dh2", fontName="Mono-Medium", fontSize=8, textColor=WHITE))]]
    for i in range(n):
        rows.append([Paragraph(inline(do[i]) if i < len(do) else "", S["cell"]),
                     Paragraph(inline(dont[i]) if i < len(dont) else "", S["cell"])])
    t = Table(rows, colWidths=[CW / 2] * 2)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), NAVY), ("BACKGROUND", (1, 0), (1, 0), HexColor("#B91C1C")),
                           ("LINEBELOW", (0, 1), (-1, -1), .5, BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    story.append(Spacer(1, 6)); story.append(t)

    page_head(story, "Voice and copy", "Names, exactly.", inline(names["_about"].split(". ")[0] + "."))
    rows = [["Use", "Never"]]
    for grp in ("brands", "processing_options", "features"):
        for b in names[grp]:
            if b.get("never"):
                rows.append([b["canonical"], ", ".join(b["never"])])
    story.append(table(rows, widths=[1.8, 4.7], font=7.3))
    story.append(Paragraph("Approved terms", S["h2"]))
    rows = [["Term", "Scope", "Meaning"]] + [[t["canonical"], t.get("scope", ""), t.get("meaning", "")] for t in names["approved_terms"]]
    story.append(table(rows, widths=[1.5, 1.3, 3.7], font=7.3))
    story.append(Paragraph(inline("Never name banking partners. Say \u201cone of our banking partners.\u201d"), S["small"]))

    # ================================================= 08 FEATURES
    s = g["07"]
    divider(story, "08", "Features.", "Feature names are proper nouns. Present tense only after a confirmed release.")
    story.append(Paragraph("FEATURES", S["eyebrow"]))
    story.append(Paragraph("How to talk about features.", S["h1"]))
    story += render_blocks(s["The rules"])
    story.append(Paragraph("Release status", S["h2"]))
    story.append(table(next(v for k, v in s["Release status"] if k == "table"), widths=[1.2, 2.6, 2.7]))
    story += [Paragraph(inline(v), S["small"]) for k, v in s["Release status"] if k == "p" and "four values" not in v]

    page_head(story, "Features", "Approved feature copy.", "Shipped features with approved copy and screenshots in the repo. Use the one-liner as written.")
    shots = {"ai-product-landing-pages": "1-landscape.png", "revenue-recovery": "1-landscape.png",
             "the-professor": "3-landscape.png", "custom-fields": "1-landscape.png"}
    fcells = []
    fw = (CW - 10) / 2
    for f in sorted(feats, key=lambda f: [c[0] for c in caps].index(f["capability"]) if f["capability"] in [c[0] for c in caps] else 9):
        shot = A / "epd-commerce-features" / f["slug"] / shots.get(f["slug"], "1-landscape.png")
        inner = [framed(shot, fw - 24, 1.45 * inch, TINT), Spacer(1, 8),
                 Paragraph(f"{f['capability'].upper()} / {f['status'].upper()}", st("fs", fontName="Mono-Medium", fontSize=7, textColor=LINK, spaceAfter=3)),
                 Paragraph(f["canonical_spelling"], st("fn", fontName="Sans-Medium", fontSize=14, leading=18, textColor=INK, spaceAfter=3)),
                 Paragraph(inline(f["one_liner"]), S["cell"])]
        t = Table([[inner]], colWidths=[fw])
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), .5, BORDER), ("LEFTPADDING", (0, 0), (-1, -1), 12),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 12),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 12)]))
        fcells.append(t)
    story.append(grid(fcells, 2))
    story.append(Paragraph("Screenshots from assets/epd-commerce-features/. Never generate synthetic screenshots, and never reuse demo numbers as claims.", S["cap"]))

    # ================================================= 09 GRAPHICS
    divider(story, "09", "Making graphics.", "Start from a template. Composite real files. Never redraw logos, marks, or UI.")
    agents = md_sections(ROOT / "AGENTS.md")
    story.append(Paragraph("MAKING GRAPHICS", S["eyebrow"]))
    story.append(Paragraph("Templates and the composite rule.", S["h1"]))
    story += render_blocks(agents["Generating images"])
    tr = md_sections(ROOT / "templates" / "README.md")
    story.append(Paragraph("Formats", S["h2"]))
    story.append(table(next(v for k, v in tr[""] if k == "table"), widths=[1.4, 1.1, 4], font=8))
    story.append(Paragraph("Backgrounds", S["h2"]))
    bgs = ["dark-gradient-square.png", "dark-gradient-highlight-square.png", "social-gradient-square.png"]
    bw3 = (CW - 20) / 3
    story.append(grid([captioned(img(A / "backgrounds" / b, w=bw3, h=1.05 * inch), b, bw3) for b in bgs], 3))

    page_head(story, "Making graphics", "Five template families.", inline(tr[""][1][1]) if len(tr[""]) > 1 and tr[""][1][0] == "p" else None)
    fam = next(v for k, v in tr["Families"] if k == "table")[1:]
    pw = (CW - 20) / 3
    cells = []
    for r in fam:
        key = re.search(r"\(([\w-]+)\.json\)", r[0]).group(1)
        prev = ROOT / "templates" / "previews" / f"{key}-portrait.jpg"
        cells.append([img(prev, w=pw), Paragraph(r[1], st("fam", fontName="Sans-Medium", fontSize=10, leading=13, textColor=INK, spaceBefore=5)),
                      Paragraph(f"Image area: {inline(r[2])}. AI illustration: {r[3]}.", S["small"])])
    story.append(grid(cells, 3))
    story.append(Paragraph("Previews from templates/previews/ show example copy for review, not for publishing.", S["cap"]))

    page_head(story, "Making graphics", "Who controls what.")
    story += render_blocks(tr["Who controls what"])
    story.append(Paragraph("Partner graphics", S["h2"]))
    story += render_blocks(agents["Partner graphics (separate workflow)"])

    story.append(NextPageTemplate("back")); story.append(PageBreak()); story.append(Spacer(1, 1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fonts"); ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    gs = register_fonts(a.fonts); build_styles()
    if not gs:
        print("WARNING: General Sans not found, using DM Sans fallback")
    doc = BaseDocTemplate(a.out, pagesize=letter, title="EPD Commerce Brand Guidelines", author="EPD Commerce",
                          subject="Brand guidelines generated from github.com/EasyPayDirect/epd-commerce-brand")
    content = Frame(M, 0.8 * inch, CW, PAGE_H - 0.8 * inch - 0.85 * inch, id="c", leftPadding=0, rightPadding=0,
                    topPadding=0, bottomPadding=0)
    full = Frame(M, M, CW, PAGE_H - 2 * M, id="f")
    doc.addPageTemplates([PageTemplate("cover", [full], onPage=cover_page),
                          PageTemplate("content", [content], onPage=chrome),
                          PageTemplate("divider", [full], onPage=divider_page),
                          PageTemplate("back", [full], onPage=back_page)])
    story = [Spacer(1, 1)]
    build(story, *load())
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)
    print("Built", a.out)


if __name__ == "__main__":
    main()
