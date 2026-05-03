#!/usr/bin/env python3
"""
Erase static wheels from a cart sprite by clearing two circular regions.
Output is the cart with empty wheel wells (transparent) so we can overlay
rotating wheel sprites at runtime.

Usage: erase_wheels.py input.png output.png cx1_frac cy_frac r_frac cx2_frac
"""
import sys
from PIL import Image

def erase(infile, outfile, cx1f, cy1f, r1f, cx2f, cy2f, r2f):
    img = Image.open(infile).convert('RGBA')
    w, h = img.size
    px = img.load()
    centers = [(int(cx1f * w), int(cy1f * h), int(r1f * w)),
               (int(cx2f * w), int(cy2f * h), int(r2f * w))]
    for cx, cy, r in centers:
        r2 = r * r
        for y in range(max(0, cy - r), min(h, cy + r + 1)):
            for x in range(max(0, cx - r), min(w, cx + r + 1)):
                dx, dy = x - cx, y - cy
                if dx*dx + dy*dy <= r2:
                    px[x, y] = (0, 0, 0, 0)
    img.save(outfile, 'PNG', optimize=True)
    print(f'  erased wheel circles, saved {outfile}')

if __name__ == '__main__':
    a = sys.argv
    if len(a) < 9:
        print('Usage: erase_wheels.py in out cx1 cy1 r1 cx2 cy2 r2')
        sys.exit(1)
    erase(a[1], a[2], float(a[3]), float(a[4]), float(a[5]),
                       float(a[6]), float(a[7]), float(a[8]))
