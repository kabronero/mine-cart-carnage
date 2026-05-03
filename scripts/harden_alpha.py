#!/usr/bin/env python3
"""
Make alpha channel binary: any pixel below threshold → fully transparent,
any pixel above → fully opaque. Kills white halos from JPEG edge fringe
that survive the Vision background-removal pass.
"""
import sys
from PIL import Image

def harden(infile, outfile, thresh=180):
    img = Image.open(infile).convert('RGBA')
    w, h = img.size
    px = img.load()
    changed = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < thresh:
                px[x, y] = (0, 0, 0, 0)
                changed += 1
            elif a < 255:
                px[x, y] = (r, g, b, 255)
                changed += 1
    bbox = img.getbbox()
    if bbox:
        margin = 4
        x0 = max(0, bbox[0] - margin); y0 = max(0, bbox[1] - margin)
        x1 = min(w, bbox[2] + margin); y1 = min(h, bbox[3] + margin)
        img = img.crop((x0, y0, x1, y1))
    img.save(outfile, 'PNG', optimize=True)
    print(f'  hardened {changed} pixels, final size {img.size}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: harden_alpha.py input output [threshold]')
        sys.exit(1)
    t = int(sys.argv[3]) if len(sys.argv) > 3 else 180
    harden(sys.argv[1], sys.argv[2], t)
