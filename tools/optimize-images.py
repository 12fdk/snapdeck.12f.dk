#!/usr/bin/env python3
"""optimize-images.py — make a WebP sibling for every blog image.

The covers and inline photos come out of ComfyUI as 1200px PNGs, which for a
photograph means 700–950 KB each. That was fine when the blog had one post and
is not fine now: /blog/ was shipping 7.2 MB of cover images, and every post page
had an ~800 KB PNG as its LCP element with `fetchpriority="high"` on it.

So each `images/blog/<name>.png` gets an `<name>.webp` beside it, and the pages
serve the WebP through a <picture> element with the PNG as the fallback source.
The PNG stays on disk on purpose — it is the fallback, and it is what og:image
and the JSON-LD `image` property point at, because social and search scrapers
are the one audience where PNG compatibility still matters more than bytes.

    python3 tools/optimize-images.py            # convert anything missing
    python3 tools/optimize-images.py --check    # report what is missing, write nothing
    python3 tools/optimize-images.py --force    # re-encode everything

Kept out of build.py deliberately: build.py is stdlib-only so it runs
identically on a laptop and inside the Hermes container, and this needs an image
encoder. build.py only *checks* that the WebP exists and tells you to run this.

Encoder: Pillow if it is importable, otherwise the `cwebp` binary. If neither is
available the script says so and exits non-zero rather than half-doing the job.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG_IMAGES = ROOT / "images" / "blog"

# 82 is the knee of the curve for these photographs: visually indistinguishable
# from the PNG at full width, and roughly a 10x saving. Method 6 is the slowest
# and smallest setting, which is the right trade for a build-time step.
QUALITY = 82
METHOD = 6


def encode_pillow(src: Path, dst: Path) -> bool:
    try:
        from PIL import Image
    except ImportError:
        return False
    with Image.open(src) as im:
        # Photographs from ComfyUI are RGB; drop any alpha channel that a
        # pipeline change might introduce so the WebP stays in the smaller mode.
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        im.save(dst, "WEBP", quality=QUALITY, method=METHOD)
    return True


def encode_cwebp(src: Path, dst: Path) -> bool:
    if not shutil.which("cwebp"):
        return False
    subprocess.run(["cwebp", "-quiet", "-q", str(QUALITY), "-m", str(METHOD),
                    str(src), "-o", str(dst)], check=True)
    return True


def encode(src: Path, dst: Path) -> None:
    if encode_pillow(src, dst):
        return
    if encode_cwebp(src, dst):
        return
    raise SystemExit(
        "ERROR  no WebP encoder available — install Pillow (`pip install Pillow`) "
        "or the cwebp binary (`brew install webp`) and run this again.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="report missing or stale WebP files; write nothing")
    ap.add_argument("--force", action="store_true",
                    help="re-encode even when the WebP already exists")
    args = ap.parse_args()

    if not BLOG_IMAGES.is_dir():
        print(f"ERROR  {BLOG_IMAGES.relative_to(ROOT)} does not exist", file=sys.stderr)
        return 1

    pngs = sorted(BLOG_IMAGES.glob("*.png"))
    if not pngs:
        print("nothing to do — no PNGs in images/blog/")
        return 0

    missing, saved_from, saved_to = [], 0, 0
    for src in pngs:
        dst = src.with_suffix(".webp")
        # Stale counts as missing: a regenerated cover must not keep serving the
        # old WebP to every visitor while the PNG quietly changes underneath it.
        stale = dst.exists() and dst.stat().st_mtime < src.stat().st_mtime
        if dst.exists() and not stale and not args.force:
            continue
        missing.append(src.name)
        if args.check:
            continue
        encode(src, dst)
        before, after = src.stat().st_size, dst.stat().st_size
        saved_from += before
        saved_to += after
        print(f"  {src.name:52s} {before // 1024:5d} KB → {after // 1024:4d} KB"
              f"  ({100 - after * 100 // before:2d}% smaller)")

    if args.check:
        if missing:
            print(f"MISSING  {len(missing)} WebP file(s): {', '.join(missing)}",
                  file=sys.stderr)
            print("Run: python3 tools/optimize-images.py", file=sys.stderr)
            return 1
        print(f"IMAGES OK — {len(pngs)} PNG(s), all have a current WebP sibling")
        return 0

    if not missing:
        print(f"IMAGES OK — {len(pngs)} PNG(s), all WebP siblings already current")
        return 0

    print(f"IMAGES OK — encoded {len(missing)} file(s), "
          f"{saved_from // 1024} KB → {saved_to // 1024} KB "
          f"({100 - saved_to * 100 // saved_from}% smaller)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
