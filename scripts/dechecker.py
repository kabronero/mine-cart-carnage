#!/usr/bin/env python3
"""
Convert a Gemini-generated sprite (with painted checker fake transparency)
into a real PNG with alpha channel.

Strategy:
  1. Sample corners to learn the brightness range of the checker squares.
  2. Any pixel that is (a) low-saturation (i.e. grayscale-ish) AND
     (b) inside that brightness range → transparent.
     This catches the checker AND its JPEG compression artifacts in one go,
     while preserving black outlines (pure black) and saturated sprite colors.
  3. Crop to the bounding box of remaining opaque pixels with a small margin.

Usage:
  dechecker.py input.png output.png [--sat 20] [--bright-pad 25]
"""
import sys
from PIL import Image

def detect_brightness_range(img, sample_size=80, step=2):
    """Return (min_brightness, max_brightness) of checker pixels in corners."""
    w, h = img.size
    corners = [(0, 0), (w - sample_size, 0),
               (0, h - sample_size), (w - sample_size, h - sample_size)]
    brights = []
    for cx, cy in corners:
        for x in range(cx, cx + sample_size, step):
            for y in range(cy, cy + sample_size, step):
                if 0 <= x < w and 0 <= y < h:
                    px = img.getpixel((x, y))[:3]
                    # Only consider near-grayscale (the checker is grays)
                    if max(px) - min(px) < 20:
                        brights.append(sum(px) // 3)
    if not brights:
        return (0, 255)
    return (min(brights), max(brights))

def chroma_key(infile, outfile, sat_tol=20, bright_pad=25):
    img = Image.open(infile).convert('RGBA')
    w, h = img.size
    bmin, bmax = detect_brightness_range(img)
    bmin = max(0, bmin - bright_pad)
    bmax = min(255, bmax + bright_pad)
    print(f'  Checker brightness: [{bmin}-{bmax}], sat-tol={sat_tol}')

    # Pure black gets a special exception (preserves outlines)
    BLACK_THRESH = 15

    pixels = img.load()
    transp = 0
    for y in range(h):
        for x in range(w):
            r, g, b, _ = pixels[x, y]
            avg = (r + g + b) // 3
            sat = max(r, g, b) - min(r, g, b)
            if sat < sat_tol and bmin <= avg <= bmax and avg > BLACK_THRESH:
                pixels[x, y] = (0, 0, 0, 0)
                transp += 1

    # Crop to actual sprite bbox + small margin
    bbox = img.getbbox()
    if bbox:
        margin = 8
        x0, y0, x1, y1 = bbox
        x0 = max(0, x0 - margin); y0 = max(0, y0 - margin)
        x1 = min(w, x1 + margin); y1 = min(h, y1 + margin)
        img = img.crop((x0, y0, x1, y1))

    img.save(outfile, 'PNG', optimize=True)
    pct = 100 * transp / (w * h)
    print(f'  Transparent: {pct:.1f}% | Final size: {img.size}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: dechecker.py input output [--sat N] [--bright-pad N]')
        sys.exit(1)
    sat_tol = 20
    bright_pad = 25
    args = sys.argv[3:]
    if '--sat' in args: sat_tol = int(args[args.index('--sat') + 1])
    if '--bright-pad' in args: bright_pad = int(args[args.index('--bright-pad') + 1])
    chroma_key(sys.argv[1], sys.argv[2], sat_tol=sat_tol, bright_pad=bright_pad)
