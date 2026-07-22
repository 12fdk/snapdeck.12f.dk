#!/usr/bin/env python3
"""Generate a blog post's images: the 1200x630 cover/OG card, and inline photos.

Not part of a build step (there isn't one) — a helper the weekly blog job and
you both call. Output goes to images/blog/ as .png and .webp.

    # Cover from a ComfyUI photo: crop to 1200x630, brand scrim, title on top
    python3 tools/make-og-image.py cover <slug> "<Title>" "<tag>" --bg photo.png

    # Cover with no photo — the original indigo→purple gradient card
    python3 tools/make-og-image.py cover <slug> "<Title>" "<tag>"

    # An inline article photo: images/blog/<slug>-1.png|webp, no text on it
    python3 tools/make-og-image.py inline <slug> 1 photo.png

The cover carries the title because that is what a link preview shows in
Messages, Slack and X — a bare photograph there tells nobody what the post is.
Inline photos stay clean.

Requires Pillow. Fonts are vendored in tools/fonts/ so a container and a laptop
produce the same output.
"""

import argparse
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1200, 630
INLINE_W, INLINE_H = 1200, 675
INDIGO = (79, 70, 229)
PURPLE = (124, 58, 237)
GOLD = (251, 191, 36)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "images", "blog")

FONT_CANDIDATES = [
    os.path.join(HERE, "fonts", "Inter-{w}.ttf"),
    "/Users/robert/Git/home-stories.12f.dk/src/assets/Inter-{w}.ttf",
    "/System/Library/Fonts/Supplemental/Arial {w}.ttf",
    "/Library/Fonts/Arial {w}.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans{dv}.ttf",
]


def font(weight, size):
    for tmpl in FONT_CANDIDATES:
        path = tmpl.format(w=weight, dv="-Bold" if weight == "Bold" else "")
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


def fit(path, width, height):
    """Center-crop a photo to exactly width x height, covering the frame."""
    img = Image.open(path).convert("RGB")
    scale = max(width / img.width, height / img.height)
    img = img.resize((max(width, round(img.width * scale)),
                      max(height, round(img.height * scale))), Image.LANCZOS)
    left = (img.width - width) // 2
    top = (img.height - height) // 2
    return img.crop((left, top, left + width, top + height))


SCRIM = (13, 11, 32)          # near-black indigo — reads as shadow, not as a colour wash


def photo_base(bg_path):
    """A ComfyUI photo with a scrim under the title, so it still looks like a photo.

    The temptation is to flood the frame with brand colour; that turns every
    cover into the same purple rectangle and throws away the reason for
    generating a photograph at all. So: the top two-thirds stay essentially
    untouched, and a soft shadow ramps up over the bottom where the title sits,
    with a slight extra lean to the left edge for the first words of each line.
    """
    img = ImageEnhance.Color(fit(bg_path, W, H)).enhance(0.95)

    # Vertical ramp: clear until ~30% down, near-opaque at the bottom.
    vertical = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vertical)
    for y in range(H):
        t = max(0.0, (y / H - 0.30) / 0.70)
        vd.line([(0, y), (W, y)], fill=round(238 * (t ** 1.5)))

    # Horizontal ramp: full strength on the left, easing off to the right so the
    # photograph survives on the side the eye reads as "the picture".
    horizontal = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(horizontal)
    for x in range(W):
        hd.line([(x, 0), (x, H)], fill=round(255 - 55 * (x / W)))

    mask = ImageChops.multiply(vertical, horizontal).filter(ImageFilter.GaussianBlur(28))
    return Image.composite(Image.new("RGB", (W, H), SCRIM), img, mask)


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


def save(img, slug, suffix=""):
    out_dir = os.path.normpath(OUT_DIR)
    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, f"{slug}{suffix}.png")
    img.save(png, optimize=True)
    img.save(os.path.join(out_dir, f"{slug}{suffix}.webp"), quality=86, method=6)
    print("wrote", png, "(+ .webp)")


def make_cover(slug, title, tag, bg=None):
    img = photo_base(bg) if bg else gradient()
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
        if bg:                                   # a little shadow to hold it off the photo
            draw.text((margin + 2, y + 3), line, font=title_font, fill=(10, 6, 34))
        draw.text((margin, y), line, font=title_font, fill=(255, 255, 255))
        y += line_h

    # Footer wordmark
    draw.text((margin, H - margin - 40), "snapdeck.12f.dk", font=font("Regular", 30),
              fill=(255, 255, 255))
    save(img, slug)


def make_inline(slug, number, photo):
    save(fit(photo, INLINE_W, INLINE_H), slug, f"-{number}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)

    c = sub.add_parser("cover", help="1200x630 cover / OG card")
    c.add_argument("slug")
    c.add_argument("title")
    c.add_argument("tag")
    c.add_argument("--bg", help="photo to use as the background (e.g. from comfy-gen)")

    i = sub.add_parser("inline", help="1200x675 in-article photo, no text")
    i.add_argument("slug")
    i.add_argument("number", type=int)
    i.add_argument("photo")

    a = ap.parse_args()
    if a.mode == "cover":
        if a.bg and not os.path.exists(a.bg):
            sys.exit(f"background image not found: {a.bg}")
        make_cover(a.slug, a.title, a.tag, a.bg)
    else:
        if not os.path.exists(a.photo):
            sys.exit(f"photo not found: {a.photo}")
        make_inline(a.slug, a.number, a.photo)


if __name__ == "__main__":
    main()
