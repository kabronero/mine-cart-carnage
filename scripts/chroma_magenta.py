#!/usr/bin/env python3
"""
Chroma-key pure magenta (#FF00FF) backgrounds out of an image. Reliable for
sprites generated with explicit "solid magenta background" prompts — no AI
guessing what is/isn't subject.

Tolerance: pixels within `tol` of pure magenta in BOTH R-G and B-G channels
become transparent. R should be high, G should be low, B should be high.
"""
import sys
from PIL import Image

def is_magenta(r, g, b, tol=60):
    return r > 180 and b > 180 and g < 100 and (r - g) > tol and (b - g) > tol

def chroma(infile, outfile, tol=60):
    img = Image.open(infile).convert('RGBA')
    w, h = img.size
    px = img.load()
    transp = 0
    for y in range(h):
        for x in range(w):
            r, g, b, _ = px[x, y]
            if is_magenta(r, g, b, tol):
                px[x, y] = (0, 0, 0, 0)
                transp += 1
    bbox = img.getbbox()
    if bbox:
        m = 6
        x0 = max(0, bbox[0] - m); y0 = max(0, bbox[1] - m)
        x1 = min(w, bbox[2] + m); y1 = min(h, bbox[3] + m)
        img = img.crop((x0, y0, x1, y1))
    img.save(outfile, 'PNG', optimize=True)
    print(f'  removed {transp} magenta pixels, final {img.size}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: chroma_magenta.py input output [tol]')
        sys.exit(1)
    t = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    chroma(sys.argv[1], sys.argv[2], t)
