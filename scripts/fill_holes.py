#!/usr/bin/env python3
"""
Close small interior "holes" in sprites where the BG-removal punched a tiny
gap inside the subject. Flood-fill from corners marks the real BG; any
transparent pixel NOT reachable from outside is an interior hole → re-fill
with the average of its surrounding opaque pixels.
"""
import sys
from collections import deque
from PIL import Image

def fill(infile, outfile):
    img = Image.open(infile).convert('RGBA')
    w, h = img.size
    px = img.load()
    outside = bytearray(w * h)
    queue = deque()

    def trans(x, y):
        return px[x, y][3] < 100

    # Seed all border transparent pixels as "outside"
    for x in range(w):
        for y in (0, h-1):
            if trans(x, y) and not outside[y*w+x]:
                outside[y*w+x] = 1
                queue.append((x, y))
    for y in range(h):
        for x in (0, w-1):
            if trans(x, y) and not outside[y*w+x]:
                outside[y*w+x] = 1
                queue.append((x, y))

    while queue:
        cx, cy = queue.popleft()
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
            nx, ny = cx+dx, cy+dy
            if 0 <= nx < w and 0 <= ny < h:
                ni = ny*w+nx
                if not outside[ni] and trans(nx, ny):
                    outside[ni] = 1
                    queue.append((nx, ny))

    # Fill holes (transparent pixels not reachable from outside)
    filled = 0
    for y in range(h):
        for x in range(w):
            if trans(x, y) and not outside[y*w+x]:
                rs = gs = bs = n = 0
                for ddy in range(-3, 4):
                    for ddx in range(-3, 4):
                        nx, ny = x+ddx, y+ddy
                        if 0 <= nx < w and 0 <= ny < h:
                            r, g, b, a = px[nx, ny]
                            if a >= 100:
                                rs += r; gs += g; bs += b; n += 1
                if n > 0:
                    px[x, y] = (rs//n, gs//n, bs//n, 255)
                    filled += 1

    img.save(outfile, 'PNG', optimize=True)
    print(f'  filled {filled} interior holes')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: fill_holes.py input output')
        sys.exit(1)
    fill(sys.argv[1], sys.argv[2])
