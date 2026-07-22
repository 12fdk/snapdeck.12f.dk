#!/usr/bin/env python3
"""Generate a blog OG / featured image: brand gradient + big title.

Not part of the site build (there isn't one) — a one-off helper you run when
adding a blog post. Output goes to images/blog/<slug>.png and .webp.

    python3 tools/make-og-image.py <slug> "<Title>" "<tag>"

Requires Pillow and the Inter font files (falls back to any bold system font).
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
INDIGO = (79, 70, 229)
PURPLE = (124, 58, 237)
GOLD = (251, 191, 36)

FONT_CANDIDATES = [
    "/Users/robert/Git/home-stories.12f.dk/src/assets/Inter-{w}.ttf",
    "/System/Library/Fonts/Supplemental/Arial {w}.ttf",
    "/Library/Fonts/Arial {w}.ttf",
]


def font(weight, size):
    for tmpl in FONT_CANDIDATES:
        path = tmpl.format(w=weight)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def gradient():
    """Diagonal indigo → purple with a soft gold glow bottom-right."""
    base = Image.new("RGB", (W, H))
    px = base.load()
    for y in range(H):
        for x in range(0, W, 4):
            t = (x / W + y / H) / 2
            c = tuple(round(INDIGO[i] + (PURPLE[i] - INDIGO[i]) * t) for i in range(3))
            for dx in range(4):
                if x + dx < W:
                    px[x + dx, y] = c

    glow = Image.new("RGB", (W, H), GOLD)
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((W - 520, H - 380, W + 320, H + 320), fill=110)
    mask = mask.filter(ImageFilter.GaussianBlur(150))

    light = Image.new("RGB", (W, H), (255, 255, 255))
    lmask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(lmask).ellipse((-300, -420, 620, 300), fill=40)
    lmask = lmask.filter(ImageFilter.GaussianBlur(140))

    base = Image.composite(glow, base, mask)
    return Image.composite(light, base, lmask)


def wrap(draw, text, fnt, max_width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def make(slug, title, tag):
    img = gradient()
    draw = ImageDraw.Draw(img)
    margin = 84

    # Tag chip
    chip_font = font("Bold", 26)
    label = tag.upper()
    tw = draw.textlength(label, font=chip_font)
    draw.rounded_rectangle((margin, margin, margin + tw + 52, margin + 56), 28, fill=GOLD)
    draw.text((margin + 26, margin + 13), label, font=chip_font, fill=(58, 36, 0))

    # Title, sized down until it fits in four lines
    for size in (78, 70, 62, 56):
        title_font = font("Bold", size)
        lines = wrap(draw, title, title_font, W - margin * 2)
        if len(lines) <= 4:
            break

    line_h = size * 1.22
    y = H - margin - 66 - line_h * len(lines)
    for line in lines:
        draw.text((margin, y), line, font=title_font, fill=(255, 255, 255))
        y += line_h

    # Footer wordmark
    draw.text((margin, H - margin - 40), "snapdeck.12f.dk", font=font("Regular", 30),
              fill=(255, 255, 255, 220))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "images", "blog")
    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, f"{slug}.png")
    img.save(png, optimize=True)
    img.save(os.path.join(out_dir, f"{slug}.webp"), quality=86, method=6)
    print("wrote", os.path.normpath(png), "(+ .webp)")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    make(*sys.argv[1:4])
