#!/usr/bin/env python3
"""
Find approximate wheel positions in a cart sprite by scanning the bottom
half for dark circular blobs. Outputs (x_center, y_center, radius) for
each wheel detected, in image coordinates (also as fractions of size).
"""
import sys
from PIL import Image

def find_wheels(path):
    img = Image.open(path).convert('RGBA')
    w, h = img.size
    # Scan bottom 50% for "very dark" pixels (wheel ironwork)
    px = img.load()
    dark = []
    y_start = int(h * 0.45)
    for y in range(y_start, h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 200 and max(r, g, b) < 50:
                dark.append((x, y))
    if not dark:
        print('  no dark pixels found')
        return
    # Cluster horizontally — find left and right wheel centers
    xs = [d[0] for d in dark]
    ys = [d[1] for d in dark]
    mid_x = (min(xs) + max(xs)) // 2
    left = [(x, y) for x, y in dark if x < mid_x]
    right = [(x, y) for x, y in dark if x >= mid_x]
    def centroid(pts):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        cx = sum(xs) // len(xs); cy = sum(ys) // len(ys)
        radius = max(max(xs)-cx, cx-min(xs), max(ys)-cy, cy-min(ys))
        return (cx, cy, radius)
    print(f'  size: {w}x{h}')
    if left:
        cx, cy, r = centroid(left)
        print(f'  LEFT  wheel: center=({cx},{cy}) r={r}  | frac=({cx/w:.3f},{cy/h:.3f}) rfrac={r/w:.3f}')
    if right:
        cx, cy, r = centroid(right)
        print(f'  RIGHT wheel: center=({cx},{cy}) r={r}  | frac=({cx/w:.3f},{cy/h:.3f}) rfrac={r/w:.3f}')

if __name__ == '__main__':
    for f in sys.argv[1:]:
        print(f'== {f} ==')
        find_wheels(f)
