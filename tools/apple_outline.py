#!/usr/bin/env python3
"""Trace the half-apple outline (enclosure decision E7) from the user's to-scale sketch and write it in device
coordinates for tools/enclosure_apple.py.

usage: apple_outline.py [SKETCH.png [OUT.json]]
       defaults: docs/enclosure/img/half_apple_sketch.png -> docs/enclosure/model/apple_outline.json
       (needs numpy, pillow, shapely)

Device frame, front view, mm: x' from Board A's left edge, y' down from Board A's device-top edge (the frame of
docs/enclosure/mechanical_inputs.md). The scale comes from Board A's grey dashed outline in the sketch (95.0 mm wide).

Steps:
1. The body's outer edge (stem and leaf excluded) is found by rays from a point on the centre line, then made exactly
   symmetric about the centre line and centred on Board A (x' 47.5), as the sketch intends.
2. Corners are rounded so the shell can have no sharp edges: convex parts to at least RC (larger than the back's edge
   radius, or the back fillet cannot be made), concave ones (the stem notch, the bottom dimple) to RV.
3. The stem (a brown line) and the leaf (a closed shape) are traced as well.
"""
import json
import math
import os
import sys

import numpy as np
import shapely
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RC = 12.0          # minimum convex radius of the outline, mm (the back edge is rounded with R 10)
RV = 5.0           # concave corners (stem notch, bottom dimple), mm
STEP = 1.5         # spacing of the output points, mm
CX = 47.5          # the centre line: Board A's centre


def main():
    sketch = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'docs/enclosure/img/half_apple_sketch.png')
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'docs/enclosure/model/apple_outline.json')
    im = np.asarray(Image.open(sketch).convert('RGBA')).astype(int)
    H, W, _ = im.shape
    r, g, b, a = (im[..., k] for k in range(4))
    front = np.zeros((H, W), bool)
    front[:, :int(W * 0.55)] = True                      # the front view; the side view and labels are to the right
    ink = (a > 128) & ~((r > 235) & (g > 235) & (b > 235))
    # 1. scale from Board A's dashed outline (mid-grey dashes): the two side lines and the top line
    grey = (abs(r - g) < 8) & (abs(g - b) < 8) & (r > 110) & (r < 160) & (a > 128) & front
    cols, rows = grey.sum(0), grey.sum(1)
    xs, ys = np.where(cols > 150)[0], np.where(rows > 150)[0]
    ax0, ax1 = xs[xs < W * 0.3].mean(), xs[xs > W * 0.3].mean()
    ay0 = ys.mean()
    px = (ax1 - ax0) / 95.0
    print(f'scale {px:.3f} px/mm from Board A (x {ax0:.1f}-{ax1:.1f} px, top y {ay0:.1f} px)')

    def dev(x, y):
        return (x - ax0) / px, (y - ay0) / px

    brown = (r > g + 20) & (g > b + 20) & (r < 140) & ink & front
    # the body: everything drawn in the front view below the leaf, minus the stem
    # top of the left lobe (no stem or leaf on that side): the highest drawn pixel over x' 0-40
    lobe_top = min(np.where(ink[:, x])[0].min() for x in range(int(ax0), int(ax0 + 40 * px)) if ink[:, x].any())
    body = ink & front & ~brown
    body[:lobe_top - 2, :] = False

    def trace(mask, cx, cy, n=1440):
        pts = []
        for k in range(n):
            t = 2 * math.pi * k / n
            dx, dy = math.cos(t), math.sin(t)
            s = 0.0
            while True:
                x, y = int(round(cx + s * dx)), int(round(cy + s * dy))
                if not (0 <= x < W and 0 <= y < H) or not mask[y, x]:
                    break
                s += 0.5
            pts.append((cx + (s - 0.5) * dx, cy + (s - 0.5) * dy))
        return pts

    cy = ay0 + 70 * px
    raw = [dev(x, y) for x, y in trace(body, (ax0 + ax1) / 2, cy)]
    xa = (min(p[0] for p in raw) + max(p[0] for p in raw)) / 2                 # the sketch's own centre line
    raw = [dev(x, y) for x, y in trace(body, ax0 + xa * px, cy)]             # rays from a point on it
    print(f'sketch centre line at x\' {xa:.2f} (Board A centre {CX})')
    # symmetric: average each ray with its mirror image (rays k and n/2 - k mirror about the vertical)
    n = len(raw)
    oy = (cy - ay0) / px
    rad = [math.hypot(x - xa, y - oy) for x, y in raw]
    sym = []
    for k in range(n):
        t = 2 * math.pi * k / n
        rr = (rad[k] + rad[(n // 2 - k) % n]) / 2
        sym.append((CX + rr * math.cos(t), oy + rr * math.sin(t)))
    asym = max(abs(rad[k] - rad[(n // 2 - k) % n]) for k in range(n))
    print(f'largest left / right difference in the sketch: {asym:.2f} mm (removed by averaging)')
    poly = shapely.Polygon(sym).buffer(0)
    rounded = poly.buffer(-RC, quad_segs=32).buffer(RC, quad_segs=32).buffer(RV, quad_segs=32).buffer(-RV, quad_segs=32)
    # resample the right half at even spacing from the top of the centre line to the bottom, then mirror it
    ring = shapely.LineString(rounded.exterior.coords)
    big = 1000.0
    half = rounded.intersection(shapely.box(CX, -big, CX + big, big))
    cut = shapely.LineString([(CX, -big), (CX, big)])
    ends = sorted([p for p in shapely.get_parts(ring.intersection(cut))], key=lambda p: p.y)
    y_top, y_bot = ends[0].y, ends[-1].y
    right = [p for p in shapely.LineString(half.exterior.coords).coords]
    hl = shapely.LineString(half.exterior.coords)
    # walk the half's boundary from the top axis point to the bottom axis point along the outside (x > CX side)
    d0, d1 = hl.project(shapely.Point(CX, y_top)), hl.project(shapely.Point(CX, y_bot))
    L = hl.length
    seg_a = (d1 - d0) % L
    seg_b = (d0 - d1) % L
    # the outside path is the one that does not run down the centre line (the centre line part is y_bot - y_top long)
    if abs(seg_a - (y_bot - y_top)) < abs(seg_b - (y_bot - y_top)):
        d0, d1, length = d1, d0, seg_b
        reverse = True
    else:
        length, reverse = seg_a, False
    m = max(2, int(round(length / STEP)))
    path = [hl.interpolate((d0 + length * i / m) % L) for i in range(m + 1)]
    if reverse:
        path = path[::-1]
    rpts = [(p.x, p.y) for p in path]                       # top axis point -> right side -> bottom axis point
    if rpts[0][1] > rpts[-1][1]:
        rpts = rpts[::-1]
    rpts[0] = (CX, rpts[0][1])
    rpts[-1] = (CX, rpts[-1][1])
    lpts = [(2 * CX - x, y) for x, y in reversed(rpts[1:-1])]
    outline = rpts + lpts                                   # clockwise in the front view (y' down)
    shp = shapely.Polygon(outline)
    bx0, by0, bx1, by1 = shp.bounds
    print(f'outline: x\' {bx0:.1f} .. {bx1:.1f}, y\' {by0:.1f} .. {by1:.1f}  ->  {bx1 - bx0:.1f} x {by1 - by0:.1f} mm, '
          f'{len(outline)} points; notch bottom y\' {y_top:.1f}, dimple top y\' {y_bot:.1f}')
    print(f'area change from rounding: {(rounded.area - poly.area):+.0f} mm2 of {poly.area:.0f}')

    # 3. stem: principal axis of the brown pixels
    yy, xx = np.where(brown)
    P = np.array([dev(x, y) for x, y in zip(xx, yy)])
    c = P.mean(0)
    u, s_, vt = np.linalg.svd(P - c, full_matrices=False)
    d = vt[0]
    proj = (P - c) @ d
    perp = (P - c) @ vt[1]
    e0, e1 = c + d * proj.min(), c + d * proj.max()
    stem = {'p0': [round(v, 2) for v in (e0 if e0[1] > e1[1] else e1)],          # lower end (in the notch)
            'p1': [round(v, 2) for v in (e1 if e0[1] > e1[1] else e0)],          # upper end
            'width': round(float(perp.max() - perp.min()), 2)}
    print(f'stem: from {stem["p0"]} to {stem["p1"]}, {stem["width"]} mm wide in the sketch')
    # leaf: drawn shapes above the body, right of the stem
    leaf_mask = ink & front & ~brown
    leaf_mask[lobe_top - 2:, :] = False
    sx = ax0 + max(stem['p0'][0], stem['p1'][0]) * px
    leaf_mask[:, :int(sx) + 2] = False
    ly, lx = np.where(leaf_mask)
    lc = (lx.mean(), ly.mean())
    leaf_raw = [dev(x, y) for x, y in trace(leaf_mask, *lc, n=720)]
    leaf = shapely.Polygon(leaf_raw).buffer(0).simplify(0.1)
    lb = leaf.bounds
    print(f'leaf: x\' {lb[0]:.1f} .. {lb[2]:.1f}, y\' {lb[1]:.1f} .. {lb[3]:.1f}, area {leaf.area:.0f} mm2')
    json.dump({'source': os.path.relpath(sketch, ROOT), 'px_per_mm': round(px, 4), 'centre_x': CX,
               'sketch_centre_x': round(xa, 3), 'round_convex_min': RC, 'round_concave': RV,
               'outline': [[round(x, 3), round(y, 3)] for x, y in outline],
               'stem': stem, 'leaf': [[round(x, 3), round(y, 3)] for x, y in leaf.exterior.coords[:-1]]},
              open(out, 'w'), indent=0)
    print('written', out)


if __name__ == '__main__':
    main()
