#!/usr/bin/env python3
"""Block model of the half-apple shell (docs/enclosure/ENCLOSURE.md, E7, E8, E11, E12): the outside shape with every
edge rounded, the parts inside it, clearance checks, and a printable mock-up.

usage: enclosure_apple.py OUT_DIR
       (needs build123d, shapely, numpy, pillow; reads docs/enclosure/model/apple_outline.json from
        tools/apple_outline.py and board_*_envelope.json from tools/board_envelopes.py)

Writes to OUT_DIR (VERSION below, now v2):
  apple_v2.step          the shell (solid block) with Board A, Board B, battery, display, keyboard placeholder,
                         keyboard cable, rear camera and the front camera's space inside
  apple_v2_mockup.stl    printable, front face down, no supports
  apple_v2_view_*.png    pictures

v1 (2026-11-20): rear camera in the middle of the back (E9), front camera mark above the screen (E10).
v2 (2026-11-21): rear camera high on the centre line (E11), front camera between the screen and the keyboard (E12),
                 battery against the back wall, keyboard FFC modelled.

Frame: mm. X = x' (from Board A's left edge, seen from the front), Y = -y' (up), Z out of the front: the back plane
is Z = 0, the front face Z = T. Board A and the battery sit behind the display, Board B and the keyboard below it.

What this is: the outside shape and the layout, checked. The shell is a solid block: no walls, split line, bosses,
display or keyboard openings yet. Recesses only mark where things are. Values marked NOT MEASURED or UNVERIFIED in
mechanical_inputs.md stay so here (the CM5 height, the gap under the Q20 keyboard).
"""
import json
import math
import os
import sys

import numpy as np
import shapely
from build123d import (Axis, Box, Circle, Color, Compound, Cylinder, Edge, Face, Location, Pos, Rectangle,
                       RectangleRounded, Vector, Wire, export_step, export_stl, extrude, fillet)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enclosure_model import render  # noqa: E402  (the z-buffer renderer of the swivel model)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
MODEL = os.path.join(ROOT, 'docs', 'enclosure', 'model')

# ---- parameters: ENCLOSURE.md E7-E10, mechanical_inputs.md ----
T = 20.0             # thickness without the camera bump (E7)
R_FRONT = 2.5        # front edge radius
R_BACK = 10.0        # back edge radius (the sketch's side view)
WALL = 2.0           # wall for the clearance check (E6: at least 1.6)
DISP = (85.99, 84.0, 3.76)        # display module: 85.99 wide (its tails leave toward the device's left), 84 tall
DISP_Y0 = 3.06                    # y' of the display's top edge (sketch)
SPREADER = 6.1                    # display back to Board A's top face: CM5 4.6 (UNVERIFIED) + pad and plate
Z_A_TOP = T - DISP[2] - SPREADER  # Board A top face (CM5 side, toward the display)
KBD_H = 3.0                       # Q20 keyboard thickness: about 2.5 measured by the user, 3.0 used (2026-11-20)
KBD = (70.0, 40.0)                # Q20 keyboard outline, measured by the user (2026-11-20)
KBD_ON_B = (2.0, 5.7)             # its top-left on Board B (board coords): centred, 5.7 mm below the top edge, as in
                                  # the BBQ20KBD reference model (research/dl/kbd/bbq20kbd_hw/bbq20_keyboard_full.step)
KB_X0, KB_Y0 = (95.0 - 74.0) / 2, 95.2      # Board B's top-left corner, front view (sketch)
Z_B_TOP = T - KBD_H - 0.8                   # Board B front face: the keyboard sits at J201's 0.8 mm stack height
                                            # (ASSUMED; the BBQ20KBD reference has 3 mm of foam tape under it)
BATT = (65.0, 85.0, 8.0)                    # upright: 65 wide, 85 tall (E7)
BATT_X0, BATT_Y0 = 15.0, 66.9
CLR = 0.3                                   # clearance between parts stacked in depth
VERSION = 'v2'
CAM = 32.0                                  # rear camera board (Radxa 13M 214)
CAM_STACK = (1.0, 6.38, 1.6, 1.5)           # window, lens, board, parts on the back of the board
BUMP_HALF, BUMP_CORNER = 20.0, 8.0          # bump outline 40 x 40, corner R 8 (holds the board with 0.5 + 2.0)
CAM_Y = 26.5                                # y' of the rear camera centre (E11): the highest spot on the centre line
                                            # where the bump, with its R 2 blend and 1 mm to spare, stays on the flat
                                            # back (inside the R 10 back edge); None = the middle of the back (E9)
FFC_W, FFC_T = 6.5, 0.3                     # keyboard FFC, 12P 0.5 mm: width (n + 1) x pitch and thickness, typical
                                            # values, UNVERIFIED (no cable chosen)
FCAM_HEAD = 7.5                             # front camera (E12): side of the square lens-head space; no module chosen
FCAM_WINDOW = 1.0                           # its window in the 2 mm front wall, as for the rear camera
USBA_X = (14.5, 32.7)                       # J402, J401 centres (x'), mouths 3.0 mm past Board A's edge
USBA_POCKET = (16.0, 8.5)                   # opening for a plug body (UNVERIFIED typical size), E8 rubber lids
USBC_Y = 76.0                               # placeholder: the extension's socket, right side below Board A (E8)
BUTTONS_Y = (10.5, 17.0, 23.5)              # VOL-, VOL+, POWER on the left side (y')
MIC = (12.5, 17.2)                          # microphone sound port on the back (x', y')
STEM_W, STEM_T, LEAF_T = 4.0, 4.5, 3.5      # stem width and depth, leaf depth (flush with the front: a cut apple)


def ypt(p):
    """(x', y') -> (X, Y)"""
    return (p[0], -p[1])


def spline_face(poly, step=1.0):
    """shapely polygon (X, Y) -> a build123d face bounded by one smooth closed spline"""
    ring = shapely.LineString(poly.exterior.coords)
    n = max(24, int(ring.length / step))
    pts = [ring.interpolate(ring.length * i / n) for i in range(n)]
    e = Edge.make_spline([Vector(p.x, p.y, 0) for p in pts], periodic=True)
    return Face(Wire([e]))


def prism(poly, z0, z1, step=1.0):
    return Pos(0, 0, z0) * extrude(spline_face(poly, step), z1 - z0, dir=(0, 0, 1))   # +Z whatever the winding


def rounded_prism(poly, z0, z1, r_bottom, r_top, step=1.0):
    s = prism(poly, z0, z1, step)
    if r_top > 0:
        s = fillet(s.edges().group_by(Axis.Z)[-1], radius=r_top)
    if r_bottom > 0:
        s = fillet(s.edges().group_by(Axis.Z)[0], radius=r_bottom)
    return s


def solid_of(face, z0, z1):
    return Pos(0, 0, z0) * extrude(face, z1 - z0, dir=(0, 0, 1))


def face_rrect(cx, cy, w, h, r):
    return Pos(cx, cy) * RectangleRounded(w, h, r)


def face_circle(cx, cy, r):
    return Pos(cx, cy) * Circle(r)


def face_keyboard():
    """the Q20 keyboard's outline: 70 x 40 (user), corners R 1 at the top and R 5 at the bottom, where the bottom
    key row is rounded (corner radii estimated from the BBQ20KBD photo, not measured)"""
    x0, y0 = KB_X0 + KBD_ON_B[0], KB_Y0 + KBD_ON_B[1]
    f = Pos(x0 + KBD[0] / 2, -(y0 + KBD[1] / 2)) * Rectangle(*KBD)
    f = fillet(f.vertices().group_by(Axis.Y)[-1], radius=1.0)
    return fillet(f.vertices().group_by(Axis.Y)[0], radius=5.0)


def rrect(x0, y0, x1, y1, r):
    return shapely.box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=32)


def box(x0, y0, z0, x1, y1, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def load(name):
    return json.load(open(os.path.join(MODEL, name)))


# ---------------- edges: find the sharp ones and round them ----------------
def edge_faces(solid):
    out = []
    faces = solid.faces()
    for e in solid.edges():
        adj = [f for f in faces if any(e.wrapped.IsSame(fe.wrapped) for fe in f.edges())]
        out.append((e, adj))
    return out


def sharp_edges(solid, min_angle=10.0, bbox=None):
    """edges where the surface turns by more than min_angle degrees, as (edge, angle, convex)"""
    res = []
    for e, adj in edge_faces(solid):
        if len(adj) != 2:
            continue
        p = e.position_at(0.5)
        if bbox and not (bbox[0] <= p.X <= bbox[3] and bbox[1] <= p.Y <= bbox[4] and bbox[2] <= p.Z <= bbox[5]):
            continue
        try:
            n1, n2 = adj[0].normal_at(p), adj[1].normal_at(p)
        except Exception:
            continue
        ang = math.degrees(math.acos(max(-1.0, min(1.0, n1.dot(n2)))))
        if ang < min_angle:
            continue
        # convex or concave: step 0.05 mm into each face, square to the edge; the midpoint of the two points lies in
        # the material at a convex edge and in the open at a concave one
        et = e.tangent_at(0.5)
        steps = []
        for f, n in zip(adj, (n1, n2)):
            t = n.cross(et)
            t = t.normalized() if t.length > 1e-9 else t
            a, b = p + t * 0.05, p - t * 0.05
            steps.append(a if f.distance_to(a) < f.distance_to(b) else b)
        convex = solid.is_inside((steps[0] + steps[1]) * 0.5)
        res.append((e, ang, convex))
    return res


def round_sharp(solid, radius, bbox=None, what=''):
    """fillet the convex sharp edges (inside bbox) with radius, smaller if OCC refuses"""
    edges = [e for e, a, cv in sharp_edges(solid, bbox=bbox) if cv]
    if not edges:
        return solid
    for r in (radius, radius * 0.6, radius * 0.35):
        try:
            out = fillet(edges, radius=r)
            if out.is_valid:
                if r != radius:
                    print(f'  {what}: rounded with R {r:.2f} instead of {radius}')
                return out
        except Exception:
            pass
    # one edge at a time (OCC carries a fillet along edges that meet tangentially), largest radius that works
    done, used = 0, set()
    for r in (radius, radius * 0.6, radius * 0.35):
        for e0 in [e for e, a, cv in sharp_edges(solid, bbox=bbox) if cv]:
            try:
                out = fillet([e0], radius=r)
                if out.is_valid:
                    solid, done = out, done + 1
                    used.add(round(r, 2))
            except Exception:
                pass
    left = [e for e, a, cv in sharp_edges(solid, bbox=bbox) if cv]
    print(f'  {what}: rounded edge by edge (R {sorted(used, reverse=True)})' +
          (f', {len(left)} edge(s) NOT ROUNDED' if left else ''))
    return solid


def bb(shape, pad=1.0):
    b = shape.bounding_box()
    return (b.min.X - pad, b.min.Y - pad, b.min.Z - pad, b.max.X + pad, b.max.Y + pad, b.max.Z + pad)


# ---------------- the parts inside ----------------
def board_a():
    d = load('board_a_envelope.json')
    th = d['thickness']
    z0 = Z_A_TOP - th
    # board coords (x right, y down, top face) -> front view: turned 180 degrees, x' = 95 - x, y' = 65 - y
    outer = shapely.Polygon([(95.0 - x, -(65.0 - y)) for x, y in d['outline'][0]['outer']]).buffer(0)
    parts = [Pos(0, 0, z0) * extrude(Face(Wire.make_polygon([Vector(x, y, 0) for x, y in outer.exterior.coords[:-1]],
                                                             close=True)), th, dir=(0, 0, 1))]
    boxes = []
    for p in d['parts']:
        h = p['h'] or 0.0
        if h <= 0.05 or p['x1'] - p['x0'] < 0.01 or p['y1'] - p['y0'] < 0.01:
            continue
        xa, xb = 95.0 - p['x1'], 95.0 - p['x0']
        ya, yb = -(65.0 - p['y0']), -(65.0 - p['y1'])
        if p['side'] == 'T':
            zz = (Z_A_TOP - (p['sink'] or 0.0), Z_A_TOP + h)
        else:
            zz = (z0 - h, z0)
        boxes.append((p['ref'], (xa, ya, zz[0], xb, yb, zz[1])))
    return parts, boxes


def board_b():
    d = load('board_b_envelope.json')
    th = d['thickness']
    z0 = Z_B_TOP - th
    o = d['outline'][0]
    outer = shapely.Polygon([(KB_X0 + x, -(KB_Y0 + y)) for x, y in o['outer']]).buffer(0)
    parts = [Pos(0, 0, z0) * extrude(Face(Wire.make_polygon([Vector(x, y, 0) for x, y in outer.exterior.coords[:-1]],
                                                             close=True)), th, dir=(0, 0, 1))]
    boxes = []
    for p in d['parts']:
        h = p['h'] or 0.0
        if h <= 0.05 or p['x1'] - p['x0'] < 0.01 or p['y1'] - p['y0'] < 0.01:
            continue
        xa, xb = KB_X0 + p['x0'], KB_X0 + p['x1']
        ya, yb = -(KB_Y0 + p['y1']), -(KB_Y0 + p['y0'])
        zz = (Z_B_TOP, Z_B_TOP + h) if p['side'] == 'T' else (z0 - h, z0)
        boxes.append((p['ref'], (xa, ya, zz[0], xb, yb, zz[1])))
    return parts, boxes, outer


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    ap = load('apple_outline.json')
    outline = shapely.Polygon([ypt(p) for p in ap['outline']])
    ymin, ymax = -outline.bounds[3], -outline.bounds[1]           # y' range
    print(f'outline {outline.bounds[2] - outline.bounds[0]:.1f} x {ymax - ymin:.1f} mm, thickness {T}')

    # ---- parts ----
    a_parts, a_boxes = board_a()
    b_parts, b_boxes, b_outline = board_b()
    batt_x1, batt_y1 = BATT_X0 + BATT[0], BATT_Y0 + BATT[1]
    batt_plan = shapely.box(BATT_X0, -batt_y1, batt_x1, -BATT_Y0)
    # the inside of the 2 mm walls, for the battery's position and the checks
    inner_poly = outline.buffer(-WALL, quad_segs=32)
    inner = rounded_prism(inner_poly, WALL, T - WALL, R_BACK - WALL, max(R_FRONT - WALL, 0.0), step=1.5)
    safe = inner_poly.buffer(-(R_BACK - WALL))
    # battery: as far back as the back wall and its R 10 edge allow. Nothing sits behind it any more (the rear camera
    # moved up behind Board A, E11), and this leaves the most depth in front of it for the keyboard cable and the
    # front camera (E12)
    over = [bx for ref, bx in b_boxes if bx[5] <= Z_B_TOP - 2.0 + 1e-6 and batt_plan.intersects(shapely.box(*bx[0:2], *bx[3:5]))]
    z_batt_limit = min([bx[2] for bx in over] + [Z_B_TOP - 2.0]) - CLR       # under Board B's lowest back part
    z_batt_back = WALL + CLR
    while z_batt_back + BATT[2] < z_batt_limit and \
            (box(BATT_X0, -batt_y1, z_batt_back, batt_x1, -BATT_Y0, z_batt_back + BATT[2]) - inner).volume > 1e-3:
        z_batt_back = round(z_batt_back + 0.1, 2)
    z_batt_front = z_batt_back + BATT[2]
    if z_batt_front > z_batt_limit + 1e-6:
        print(f'  BATTERY DOES NOT FIT: its front Z {z_batt_front:.2f} is past Board B\'s back parts ({z_batt_limit:.2f})')
    battery = box(BATT_X0, -batt_y1, z_batt_back, batt_x1, -BATT_Y0, z_batt_front)
    dx0 = 47.5 - DISP[0] / 2
    display = box(dx0, -(DISP_Y0 + DISP[1]), T - DISP[2], dx0 + DISP[0], -DISP_Y0, T)
    keyboard = solid_of(face_keyboard(), T - KBD_H, T)
    # rear camera: centred on the back (E9); behind whatever is deepest under it
    cam_y = CAM_Y if CAM_Y is not None else (ymin + ymax) / 2
    cam_plan = shapely.box(47.5 - CAM / 2, -(cam_y + CAM / 2), 47.5 + CAM / 2, -(cam_y - CAM / 2))
    under = [z_batt_back] if cam_plan.intersects(batt_plan) else []
    under += [bx[2] for ref, bx in a_boxes if cam_plan.intersects(shapely.box(bx[0], bx[1], bx[3], bx[4]))]
    under += [Z_A_TOP - 1.2]
    z_cam_top = min(under) - CLR                                  # back of the camera's parts
    z_cam_out = z_cam_top - sum(CAM_STACK)                        # outer face of the window = bump face
    bump_h = -z_cam_out
    zc = z_cam_out + CAM_STACK[0]
    cx, cyY = 47.5, -cam_y
    camera = [box(cx - 4.25, cyY - 4.25, zc, cx + 4.25, cyY + 4.25, zc + CAM_STACK[1]),
              box(cx - CAM / 2, cyY - CAM / 2, zc + CAM_STACK[1], cx + CAM / 2, cyY + CAM / 2, zc + CAM_STACK[1] + CAM_STACK[2]),
              box(cx - CAM / 2 + 2, cyY - CAM / 2 + 2, zc + CAM_STACK[1] + CAM_STACK[2], cx + CAM / 2 - 2, cyY + CAM / 2 - 2, z_cam_top)]
    under_refs = sorted({ref for ref, bx in a_boxes if cam_plan.intersects(shapely.box(bx[0], bx[1], bx[3], bx[4]))
                         and bx[2] <= min(under) + 1e-6})
    bump_plan = rrect(cx - BUMP_HALF, cyY - BUMP_HALF, cx + BUMP_HALF, cyY + BUMP_HALF, BUMP_CORNER)
    flat_margin = outline.buffer(-R_BACK).exterior.distance(bump_plan) if outline.buffer(-R_BACK).contains(bump_plan) else 0.0

    # keyboard FFC, Board A J1001 to Board B J101 (both at x' 47.5-48): from J1001's mouth over the battery's top
    # front edge, then straight to J101's mouth; at half each connector's height (the slot heights are not
    # dimensioned: UNVERIFIED)
    j1001 = next(bx for ref, bx in a_boxes if ref == 'J1001')
    j101 = next(bx for ref, bx in b_boxes if ref == 'J101')
    f0 = (-j1001[1], (j1001[2] + j1001[5]) / 2)            # (y', Z) of the J1001 mouth (its edge toward the keyboard)
    f1 = (-j101[4], (j101[2] + j101[5]) / 2)               # J101's mouth (its edge toward Board B's top edge)
    fk = (BATT_Y0, max(z_batt_front + CLR + FFC_T / 2, f0[1]))      # over the battery's top front edge
    ffc_path = [f0, fk, f1]
    ffc_x = ((j1001[0] + j1001[3]) / 2 + (j101[0] + j101[3]) / 2) / 2

    def ffc_z(yv):
        return float(np.interp(yv, [p[0] for p in ffc_path], [p[1] for p in ffc_path]))
    ffc_sec = shapely.LineString([(-yv, zv) for yv, zv in ffc_path]).buffer(FFC_T / 2, cap_style='flat', join_style='mitre')
    ffc = extrude(Face(Wire.make_polygon([Vector(ffc_x - FFC_W / 2, a, b) for a, b in ffc_sec.exterior.coords[:-1]],
                                         close=True)), FFC_W, dir=(1, 0, 0))
    ffc_len = sum(math.dist(p, q) for p, q in zip(ffc_path, ffc_path[1:]))
    nz = math.cos(math.atan2(f1[1] - fk[1], f1[0] - fk[0]))       # for the half thickness measured along Z
    # front camera (E12): the lens head goes between the display's bottom edge and Board B's top edge, in front of
    # the FFC, centred on the device; this is the space for it, no module is chosen
    fc_y0, fc_y1 = DISP_Y0 + DISP[1] + CLR, KB_Y0 - CLR
    fc_y = (fc_y0 + fc_y1) / 2
    fc_z0 = max(ffc_z(fc_y0), ffc_z(fc_y1)) + FFC_T / 2 / nz + CLR
    fc_z1 = T - FCAM_WINDOW
    fcam = box(47.5 - FCAM_HEAD / 2, -fc_y1, fc_z0, 47.5 + FCAM_HEAD / 2, -fc_y0, fc_z1)
    print(f'Board A: top face Z {Z_A_TOP:.2f}; Board B: front face Z {Z_B_TOP:.2f}; '
          f'battery Z {z_batt_back:.2f}..{z_batt_front:.2f} (Board B\'s back parts allow up to {z_batt_limit:.2f})')
    print(f'rear camera centre y\' {cam_y:.2f}: behind {"the battery" if cam_plan.intersects(batt_plan) else "Board A"} '
          f'({", ".join(under_refs)} deepest under it), bump {bump_h:.2f} mm; the bump stands {flat_margin:.1f} mm '
          f'inside the flat back')
    print(f'keyboard FFC: x\' {ffc_x:.1f}, from y\' {f0[0]:.1f} Z {f0[1]:.2f} (J1001) over the battery\'s top edge '
          f'(y\' {fk[0]:.1f} Z {fk[1]:.2f}) to y\' {f1[0]:.1f} Z {f1[1]:.2f} (J101), {ffc_len:.1f} mm connector to connector')
    print(f'front camera space: lens centre y\' {fc_y:.2f}; y\' {fc_y0:.2f}..{fc_y1:.2f} ({fc_y1 - fc_y0:.2f} tall), '
          f'Z {fc_z0:.2f}..{fc_z1:.2f} ({fc_z1 - fc_z0:.2f} deep in front of the FFC); '
          f'away from the FFC (more than {FFC_W / 2 + CLR:.2f} mm to the side of x\' {ffc_x:.1f}) it may reach back to '
          f'Z {z_batt_front + CLR:.2f} ({fc_z1 - z_batt_front - CLR:.2f} deep)')

    # ---- the shell: outer shape ----
    print('building the shell ...')
    body = rounded_prism(outline, 0.0, T, R_BACK, R_FRONT, step=1.5)
    # rear camera bump: rounded square, edge R 3, blended into the back
    bump = solid_of(face_rrect(cx, cyY, 2 * BUMP_HALF, 2 * BUMP_HALF, BUMP_CORNER), -bump_h, 1.0)
    bump = fillet(bump.edges().group_by(Axis.Z)[0], radius=3.0)
    body = body + bump
    try:
        junction = [e for e, a, cv in sharp_edges(body, bbox=bb(bump, 0.5)) if not cv]
        body = fillet(junction, radius=2.0) if junction else body
    except Exception:
        print('  bump: the junction with the back stays unblended')
    # stem and leaf, flush with the front face (the apple is cut through its stem)
    st = ap['stem']
    p0, p1 = np.array(ypt(st['p0'])), np.array(ypt(st['p1']))
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    stem_poly = shapely.LineString([tuple(p0 - d * 4.0), tuple(p1)]).buffer(STEM_W / 2, quad_segs=32)
    stem = rounded_prism(stem_poly, T - STEM_T, T, 1.8, 1.8, step=0.5)
    # leaf: the traced leaf is convex, so its convex hull (with a round joint on the stem) smooths away the tracing
    # noise; the tips are rounded to R 2, more than the R 1.2 edge round
    joint = shapely.Point(tuple(p0 + d * ((21.0 - p0[1]) / d[1]))).buffer(2.4)      # on the stem at y' -21
    leaf_poly = shapely.MultiPoint([ypt(p) for p in ap['leaf']] + list(joint.exterior.coords)).convex_hull
    leaf_poly = leaf_poly.buffer(-2.0, quad_segs=32).buffer(2.0, quad_segs=32)
    leaf = rounded_prism(leaf_poly, T - LEAF_T, T, 1.2, 1.2, step=0.5)
    body = body + stem + leaf
    print('  outer shape done')

    # ---- marks: recesses and pockets, each rim rounded ----
    def front_recess(face, depth=0.6, r=0.5, what=''):
        nonlocal body
        tool = solid_of(face, T - depth, T + 1.0)
        body = body - tool
        body = round_sharp(body, r, bbox=bb(tool), what=what)

    front_recess(face_rrect(47.5, -(DISP_Y0 + DISP[1] / 2), DISP[0], DISP[1], 1.5), what='display mark')
    front_recess(face_keyboard(), what='keyboard mark')
    # front camera: lens position only (E12, module not chosen), centred on its space between the screen and the keys
    front_recess(face_circle(47.5, -fc_y, 2.0), what='front camera mark')
    # back: lens window on the bump, microphone port
    lens = solid_of(face_circle(cx, cyY, 5.0), -bump_h - 1.0, -bump_h + 1.0)
    body = round_sharp(body - lens, 0.8, bbox=bb(lens), what='lens window')
    mic = solid_of(face_circle(MIC[0], -MIC[1], 1.0), -1.0, 0.6)
    body = round_sharp(body - mic, 0.4, bbox=bb(mic), what='microphone port')
    # USB-A: pockets for the plug bodies, from outside down to the receptacle mouths (y' -3.0), E8
    z_usba = Z_A_TOP + (4.33 - 2.89) / 2
    for xu in USBA_X:
        w, h = USBA_POCKET
        tool = box(xu - w / 2, 3.0, z_usba - h / 2, xu + w / 2, 40.0, z_usba + h / 2)
        tool = fillet(tool.edges().filter_by(Axis.Y), radius=2.0)
        body = round_sharp(body - tool, 1.0, bbox=bb(tool), what=f'USB-A x\' {xu}')

    # USB-C (placeholder until the cable is bought) and the three buttons: rounded slots 1-1.5 mm deep in the sides
    def side_x(yv, right):
        row = outline.intersection(shapely.LineString([(-500, -yv), (500, -yv)]))
        return row.bounds[2] if right else row.bounds[0]

    def side_slot(right, yv, z, ln, wd, depth, what):
        nonlocal body
        xs = side_x(yv, right)
        x0, x1 = (xs - depth, xs + 5.0) if right else (xs - 5.0, xs + depth)
        tool = box(x0, -yv - (ln - wd) / 2, z - wd / 2, x1, -yv + (ln - wd) / 2, z + wd / 2)
        for sgn in (-1, 1):
            tool = tool + Pos((x0 + x1) / 2, -yv + sgn * (ln - wd) / 2, z) * Cylinder(wd / 2, x1 - x0, rotation=(0, 90, 0))
        body = round_sharp(body - tool, 0.5, bbox=bb(tool), what=what)

    for yv in BUTTONS_Y:
        side_slot(False, yv, Z_A_TOP + 1.65, 5.0, 3.2, 1.0, f'button y\' {yv}')
    side_slot(True, USBC_Y, 10.0, 9.5, 4.0, 1.5, 'USB-C mark')
    print(f'shell: valid {body.is_valid}, volume {body.volume / 1000:.0f} cm3')

    # ---- checks ----
    print('checks:')
    sh = sharp_edges(body)
    convex = [(e, a) for e, a, cv in sh if cv]
    concave = [(e, a) for e, a, cv in sh if not cv]
    print(f'  sharp convex edges (surface turns > 10 degrees): {len(convex)}'
          + ''.join(f'\n    at ({e.position_at(0.5).X:.1f}, {-e.position_at(0.5).Y:.1f}, {e.position_at(0.5).Z:.1f}) '
                    f'{a:.0f} deg' for e, a in convex[:20]))
    print(f'  inside corners left unblended (not sharp to the touch): {len(concave)}')
    # parts inside the walls: the inner envelope (built with the parts) is the same shape inset by WALL
    worst = []

    def outside_volume(name, x0, y0, z0, x1, y1, z1):
        plan = shapely.box(x0, y0, x1, y1)
        if z0 >= WALL - 1e-6 and z1 <= T - WALL + 1e-6 and safe.contains(plan):
            return 0.0
        v = (box(x0, y0, z0, x1, y1, z1) - inner).volume
        if v > 1e-3:
            worst.append((name, v))
        return v

    for ref, bx in a_boxes:
        outside_volume(f'Board A {ref}', *bx)
    for ref, bx in b_boxes:
        outside_volume(f'Board B {ref}', *bx)
    for name, shp in (('Board A', a_parts[0]), ('Board B', b_parts[0]), ('battery', battery)):
        v = (shp - inner).volume
        if v > 1e-3:
            worst.append((name, v))
    print(f'  parts reaching into the {WALL} mm walls: {len(worst)}'
          + ''.join(f'\n    {n}: {v:.2f} mm3' for n, v in worst))
    # front parts: inside the outer shape, and how much face is left round them
    for name, shp, poly in (('display', display, rrect(dx0, -(DISP_Y0 + DISP[1]), dx0 + DISP[0], -DISP_Y0, 0.01)),
                            ('keyboard', keyboard, shapely.box(KB_X0 + KBD_ON_B[0], -(KB_Y0 + KBD_ON_B[1] + KBD[1]),
                                                               KB_X0 + KBD_ON_B[0] + KBD[0], -(KB_Y0 + KBD_ON_B[1])))):
        margin = outline.exterior.distance(poly)
        print(f'  {name}: closest to the outside edge {margin:.1f} mm (front edge radius {R_FRONT})')
    # parts against each other
    a_shapes = [box(*bx) for ref, bx in a_boxes]
    b_shapes = [box(*bx) for ref, bx in b_boxes]
    pairs = [('display vs Board A parts', [display], a_shapes),
             ('battery vs Board A', [battery], a_shapes + a_parts),
             ('battery vs Board B', [battery], b_shapes + b_parts),
             ('rear camera vs battery and Board A', camera, [battery] + a_shapes + a_parts),
             ('keyboard vs Board B parts', [keyboard], [s for (ref, bx), s in zip(b_boxes, b_shapes) if bx[2] >= Z_B_TOP - 1e-6 and ref != 'J201']),
             ('keyboard FFC vs battery, display, both boards', [ffc],
              [battery, display] + a_parts + b_parts + [s for (ref, bx), s in zip(a_boxes + b_boxes, a_shapes + b_shapes)
                                                        if ref not in ('J1001', 'J101')]),
             ('front camera space vs FFC, battery, display, both boards', [fcam],
              [ffc, battery, display] + a_parts + b_parts + a_shapes + b_shapes)]
    for name, A_, B_ in pairs:
        v = 0.0
        for s1 in A_:
            b1 = s1.bounding_box()
            for s2 in B_:
                b2 = s2.bounding_box()
                if b1.min.X < b2.max.X and b2.min.X < b1.max.X and b1.min.Y < b2.max.Y and b2.min.Y < b1.max.Y \
                        and b1.min.Z < b2.max.Z and b2.min.Z < b1.max.Z:
                    v += (s1 & s2).volume
        print(f'  {name}: overlap {v:.3f} mm3')
    # gaps worth knowing
    tall = max((bx for ref, bx in a_boxes), key=lambda bx: bx[5])
    print(f'  display back to the tallest Board A part: {T - DISP[2] - tall[5]:.2f} mm')
    print(f'  band between the screen and the keys: y\' {DISP_Y0 + DISP[1]:.2f}..{KB_Y0 + KBD_ON_B[1]:.2f} '
          f'({KB_Y0 + KBD_ON_B[1] - DISP_Y0 - DISP[1]:.1f} mm), front camera mark at y\' {fc_y:.2f}')
    notch_y = -max(y for x, y in outline.exterior.coords if abs(x - 47.5) < 0.8)       # y' of the notch bottom
    print(f'  rear bump top edge y\' {cam_y - BUMP_HALF:.1f}: {cam_y - BUMP_HALF - notch_y:.1f} mm below the stem notch; '
          f'bump bottom edge y\' {cam_y + BUMP_HALF:.1f}, {ymax - cam_y - BUMP_HALF:.1f} mm above the bottom')

    # ---- files ----
    def named(shape, label, rgb, alpha=1.0):
        s = shape.moved(Location())
        s.label, s.color = label, Color(*[v / 255 for v in rgb], alpha)
        return s
    kids = [named(body, f'shell (block, {VERSION})', (124, 179, 66), 0.5),
            named(Compound(a_parts + a_shapes), 'Board A (part envelopes)', (40, 120, 60)),
            named(Compound(b_parts + b_shapes), 'Board B (part envelopes)', (40, 120, 60)),
            named(battery, 'battery 85 x 65 x 8', (70, 110, 200)),
            named(display, 'display', (20, 20, 30)),
            named(keyboard, 'Q20 keyboard 70 x 40 x 3', (60, 60, 60)),
            named(ffc, 'keyboard FFC 12P 0.5 mm (straight run, UNVERIFIED width)', (230, 140, 40)),
            named(Compound(camera), 'rear camera 13M 214', (200, 160, 40)),
            named(fcam, 'front camera space (no module chosen)', (220, 60, 60), 0.6)]
    export_step(Compound(children=kids, label=f'PocketZen half-apple shell, block model {VERSION}'),
                os.path.join(out, f'apple_{VERSION}.step'))
    mock = body.rotate(Axis.X, 180)
    b = mock.bounding_box()
    mock = mock.moved(Location((-b.min.X, -b.min.Y, -b.min.Z)))
    export_stl(mock, os.path.join(out, f'apple_{VERSION}_mockup.stl'), tolerance=0.05, angular_tolerance=0.15)
    bm = mock.bounding_box()
    print(f'mock-up: {bm.size.X:.1f} x {bm.size.Y:.1f} x {bm.size.Z:.1f} mm on the bed (front face down), '
          f'{body.volume / 1000:.0f} cm3 solid')

    # ---- pictures ----
    shell = (150, 196, 100)
    inner_items = [(s, (40, 120, 60)) for s in a_parts + a_shapes + b_parts + b_shapes] + \
                  [(battery, (70, 110, 200)), (keyboard, (70, 70, 70)), (ffc, (230, 140, 40)), (fcam, (220, 60, 60))] + \
                  [(s, (200, 160, 40)) for s in camera]
    # the band from the front, display and keyboard left out: the FFC behind the front camera's space
    band_items = [(s, (40, 120, 60)) for s in a_parts + a_shapes + b_parts + b_shapes] + \
                 [(battery, (70, 110, 200)), (ffc, (230, 140, 40)), (fcam, (220, 60, 60))]
    views = [('front', 0, 0, 'Front: display and keyboard marked, front camera between them'),
             ('front_three_quarter', -30, 20, 'Front, three-quarter view'),
             ('back', 180, 0, 'Back: rear camera bump high on the centre line, microphone port at the upper right'),
             ('back_three_quarter', 150, 20, 'Back, three-quarter view'),
             ('side', -90, 0, 'Right side: flat front, R 10 back edge, camera bump'),
             ('top', 0, 89, 'From the top: the two USB-A pockets, stem and leaf'),
             ('inside', 180, 0, 'Inside, from the back, shell left out: Board A, battery, Board B, rear camera'),
             ('inside_front', -35, 25, 'Inside from the front, shell, display and keyboard left out: '
                                       'front camera space (red) over the keyboard FFC (orange)')]
    for name, az, el, title in views:
        items = {'inside': inner_items, 'inside_front': band_items}.get(name, [(body, shell)])
        render(items, az, el, os.path.join(out, f'apple_{VERSION}_view_{name}.png'), title=title)
    print('written to', out)


if __name__ == '__main__':
    main()
