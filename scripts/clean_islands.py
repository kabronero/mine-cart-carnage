#!/usr/bin/env python3
"""
Remove small isolated alpha "islands" left over from background-removal.
Anything with fewer connected opaque pixels than min_size is erased.
The largest component is always kept regardless of size.

Usage: clean_islands.py input.png output.png [min_size]
"""
import sys
from collections import deque
from PIL import Image

def clean(infile, outfile, min_size=80):
    img = Image.open(infile).convert('RGBA')
    w, h = img.size
    px = img.load()
    visited = bytearray(w * h)

    def opaque(x, y):
        return px[x, y][3] >= 100

    components = []
    for y in range(h):
        for x in range(w):
            i = y * w + x
            if visited[i] or not opaque(x, y):
                visited[i] = 1
                continue
            comp = []
            q = deque([(x, y)])
            visited[i] = 1
            while q:
                cx, cy = q.popleft()
                comp.append((cx, cy))
                for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        ni = ny * w + nx
                        if not visited[ni] and opaque(nx, ny):
                            visited[ni] = 1
                            q.append((nx, ny))
            components.append(comp)

    if not components:
        img.save(outfile, 'PNG', optimize=True)
        print('  no opaque pixels to clean')
        return

    largest = max(len(c) for c in components)
    erased = 0
    erased_comps = 0
    for comp in components:
        if len(comp) < min_size and len(comp) < largest:
            for cx, cy in comp:
                px[cx, cy] = (0, 0, 0, 0)
            erased += len(comp)
            erased_comps += 1

    bbox = img.getbbox()
    if bbox:
        m = 4
        x0 = max(0, bbox[0] - m); y0 = max(0, bbox[1] - m)
        x1 = min(w, bbox[2] + m); y1 = min(h, bbox[3] + m)
        img = img.crop((x0, y0, x1, y1))

    img.save(outfile, 'PNG', optimize=True)
    print(f'  erased {erased_comps} small islands ({erased} px), largest comp: {largest}, final {img.size}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: clean_islands.py input output [min_size]')
        sys.exit(1)
    ms = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    clean(sys.argv[1], sys.argv[2], ms)
