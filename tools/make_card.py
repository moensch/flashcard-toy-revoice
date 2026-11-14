"""Printable replacement cards with their codes: an A4 PDF at true size, 600 dpi.

Usage: python3 tools/make_card.py OUT [--510] [FRONT_NUMBER ...]

--510 switches to the 510-word version's codes and text look (card size not yet measured).

Writes OUT.pdf and OUT-preview.png with up to two cards (edit CARDS below to add your
own words and pictures). Each card is front + back side by side: cut, fold on the
dashed line, glue back to back. Print at 100% and check the 50 mm line; print the
marks in true black (laser toner), as colour inks may be invisible to the IR sensors.
Needs Pillow (pip install pillow). See docs/barcode.md.
"""
import sys
from PIL import Image, ImageDraw, ImageFont
from card_code import WEIGHTS, WEIGHTS_510, encode

DPI = 600
mm = lambda v: round(v * DPI / 25.4)
W, H = 59, 88          # card mm
STRIP = 8.5            # white code strip height, mm
ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(size_mm):
    try:
        return ImageFont.truetype(ARIAL, mm(size_mm))
    except OSError:
        return ImageFont.load_default(mm(size_mm))

COLORS = {"Foods": ((240, 170, 90), (255, 241, 214)), "Fruits": ((235, 120, 140), (255, 230, 235))}


def circle(d, x, y, r, **kw):
    d.ellipse([x - r, y - r, x + r, y + r], **kw)


def draw_chocolate(d, cx, cy, s):
    w, h = s * 0.9, s * 1.2
    d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=s * 0.1, fill=(95, 55, 30))
    for i in range(2):
        for j in range(4):
            x, y = cx - w + s * 0.1 + i * w, cy - h + s * 0.1 + j * h / 2
            d.rounded_rectangle([x, y, x + w - s * 0.2, y + h / 2 - s * 0.2], radius=s * 0.06, fill=(125, 75, 40))
    # wrapper over the bottom half
    d.rectangle([cx - w - s * 0.05, cy + h * 0.15, cx + w + s * 0.05, cy + h + s * 0.05], fill=(200, 40, 50))
    d.rectangle([cx - w - s * 0.05, cy + h * 0.15, cx + w + s * 0.05, cy + h * 0.25], fill=(230, 190, 60))
    circle(d, cx, cy + h * 0.62, s * 0.25, fill=(230, 190, 60))


def draw_lollipop(d, cx, cy, s):
    d.rounded_rectangle([cx - s * 0.07, cy, cx + s * 0.07, cy + s * 1.3], radius=s * 0.05, fill=(240, 235, 225))
    cy -= s * 0.3
    rings = [(230, 60, 90), (255, 255, 255), (80, 170, 230), (255, 255, 255), (250, 200, 60), (255, 255, 255)]
    for k, r in enumerate([0.85, 0.72, 0.6, 0.47, 0.34, 0.2]):
        circle(d, cx, cy, s * r, fill=rings[k])
    d.polygon([(cx - s * 0.12, cy + s * 0.95), (cx + s * 0.12, cy + s * 0.95), (cx, cy + s * 0.8)], fill=(240, 235, 225))
    circle(d, cx - s * 0.4, cy - s * 0.4, s * 0.1, fill=(255, 255, 255))


def draw_strawberry(d, cx, cy, s):
    cy += s * 0.1
    d.polygon([(cx - s * 0.85, cy - s * 0.55), (cx + s * 0.85, cy - s * 0.55), (cx + s * 0.6, cy + s * 0.4),
               (cx, cy + s * 1.05), (cx - s * 0.6, cy + s * 0.4)], fill=(220, 40, 50))
    circle(d, cx - s * 0.45, cy - s * 0.45, s * 0.42, fill=(220, 40, 50))
    circle(d, cx + s * 0.45, cy - s * 0.45, s * 0.42, fill=(220, 40, 50))
    for px, py in [(-0.5, -0.3), (0, -0.4), (0.5, -0.3), (-0.3, 0.1), (0.25, 0.1), (0, 0.5), (-0.55, 0.05), (0.55, 0.05)]:
        d.ellipse([cx + px * s - s * 0.04, cy + py * s - s * 0.07, cx + px * s + s * 0.04, cy + py * s + s * 0.07],
                  fill=(255, 225, 120))
    green = (60, 150, 60)
    for a in (-0.6, -0.3, 0.3, 0.6):
        d.polygon([(cx, cy - s * 0.85), (cx + a * s, cy - s * 0.95), (cx + a * s * 0.6, cy - s * 0.65)], fill=green)
    d.polygon([(cx - s * 0.25, cy - s * 0.75), (cx + s * 0.25, cy - s * 0.75), (cx, cy - s * 1.05)], fill=green)
    d.rectangle([cx - s * 0.05, cy - s * 1.3, cx + s * 0.05, cy - s * 0.95], fill=(90, 120, 50))


def draw_grape(d, cx, cy, s):
    d.rectangle([cx - s * 0.05, cy - s * 1.25, cx + s * 0.05, cy - s * 0.8], fill=(110, 80, 50))
    d.polygon([(cx + s * 0.05, cy - s * 1.0), (cx + s * 0.8, cy - s * 1.25), (cx + s * 0.4, cy - s * 0.75)], fill=(70, 150, 60))
    r = s * 0.24
    for row, n in enumerate([4, 3, 4, 3, 2, 1]):
        for k in range(n):
            x = cx + (k - (n - 1) / 2) * r * 1.8
            y = cy - s * 0.7 + row * r * 1.6
            circle(d, x, y, r, fill=(110, 50, 140))
            circle(d, x - r * 0.35, y - r * 0.35, r * 0.25, fill=(170, 120, 200))


# Text look of each version: (label pill, label text, word)
STYLES = {"224": ("white", (150, 150, 150), "black"),
          "510": ((255, 248, 228), (40, 40, 40), (35, 50, 75))}
style = STYLES["224"]


def face(cat, n, word, picture):
    BG, PANEL = COLORS[cat]
    img = Image.new("RGB", (mm(W), mm(H)), BG)
    d = ImageDraw.Draw(img)
    # category pill + number
    d.rounded_rectangle([mm(13), mm(3.5), mm(46), mm(9.5)], radius=mm(3), fill=style[0])
    d.text((mm(29.5), mm(6.5)), cat, font=font(3.6), fill=style[1], anchor="mm")
    d.text((mm(55), mm(5.5)), str(n), font=font(3.2), fill="white", anchor="rm")
    d.text((mm(29.5), mm(16.5)), word, font=font(6.5), fill=style[2], anchor="mm")
    # picture panel
    d.rounded_rectangle([mm(8), mm(24), mm(51), mm(H - STRIP - 4)], radius=mm(2.5), fill=PANEL)
    picture(d, mm(29.5), mm(24 + (H - STRIP - 28) / 2), mm(12))
    # code strip: code for the number on the OTHER side
    other = n + 1 if n % 2 else n - 1
    d.rectangle([0, mm(H - STRIP), mm(W), mm(H)], fill="white")
    slot = W / 11
    for i, on in enumerate(encode(other, weights)):
        if on == "1":
            d.rectangle([mm(i * slot), mm(H - STRIP), mm((i + 1) * slot) - 1, mm(H)], fill="black")
    return img


CARDS = [("Foods", 65, "chocolate", draw_chocolate, 66, "lollipop", draw_lollipop),
         ("Fruits", 91, "strawberry", draw_strawberry, 92, "grape", draw_grape)]
out, args = sys.argv[1], sys.argv[2:]
weights = WEIGHTS
if args and args[0] == "--510":
    weights, style, args = WEIGHTS_510, STYLES["510"], args[1:]
if args:                                           # optional: only the cards with these front numbers
    CARDS = [c for c in CARDS if str(c[1]) in args]

# A4 page: each card as front + back side by side, sharing the fold line, like a book spread
page = Image.new("RGB", (mm(210), mm(297)), "white")
d = ImageDraw.Draw(page)
grey = (160, 160, 160)
t = font(3.5)
x0 = mm(210 / 2 - W)
for k, (cat, n1, w1, p1, n2, w2, p2) in enumerate(CARDS):
    y0 = mm(40 + k * (H + 12))
    page.paste(face(cat, n1, w1, p1), (x0, y0))
    page.paste(face(cat, n2, w2, p2), (x0 + mm(W), y0))
    d.rectangle([x0, y0, x0 + mm(2 * W), y0 + mm(H)], outline=grey, width=3)        # cut line
    for y in range(y0, y0 + mm(H), mm(3)):                                          # dashed fold
        d.line([x0 + mm(W), y, x0 + mm(W), y + mm(1.5)], fill=(90, 90, 90), width=4)
d.text((mm(105), mm(22)), "Cut along the outer line, fold on the dashed line, glue back to back.",
       font=t, fill="black", anchor="mm")
d.text((mm(105), mm(28)), "Print at 100% / actual size (no 'fit to page'). Card = 59 x 88 mm.",
       font=t, fill="black", anchor="mm")
# 50 mm scale check
ys = mm(40 + 2 * (H + 12) + 6)
d.line([mm(80), ys, mm(130), ys], fill="black", width=6)
for x in (80, 130):
    d.line([mm(x), ys - mm(2), mm(x), ys + mm(2)], fill="black", width=6)
d.text((mm(105), ys + mm(6)), "this line must measure exactly 50 mm", font=t, fill="black", anchor="mm")

page.save(out + ".pdf", resolution=DPI)
page.crop((x0 - mm(5), mm(35), x0 + mm(2 * W + 5), mm(40 + 2 * (H + 12)))).resize((1200, 1800)).save(out + "-preview.png")
