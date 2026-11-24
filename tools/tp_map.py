"""Test-point maps for bring-up: every TP on a board, top view and bottom view (as seen with the board turned over).

Reads the routed board read-only and draws the outline, the courtyards of ICs / connectors / switches / FETs, and each
test pad with its net. Output: docs/bringup/<board>_tp_{top,bottom}.svg and .png.

    python3 tools/tp_map.py            # both boards
"""
import math
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'gen'))
import sexpr  # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'bringup')
BOARDS = {
    'board_a': 'hw/board_a/cm5_carrier.kicad_pcb',
    'board_b': 'hw/board_b/q20_keyboard.kicad_pcb',
}
SHOW = ('U', 'J', 'SW', 'Q', 'Y')         # parts drawn as courtyards, for orientation
SCALE = 9.0                              # px per mm in the PNG
POWER = re.compile(r'^(VSYS|VBUS_C|CHG_IN|BAT_P|CM5_VIN|VCC|PD_LDO_3V3|SD_VDD|WL_|LCD_|BL_LEDA|DIG_3V3|USBA\d_VBUS|'
                   r'CAM[AB]_[35]V|\+3V3)')
COLOURS = {'power': '#c62828', 'gnd': '#212121', 'prog': '#1565c0', 'debug': '#2e7d32', 'signal': '#6d4c41'}
# label offsets (mm, in the drawn view) where the default (right of the pad) collides
NUDGE = {
    ('board_a', 'top'): {'TP101': (1.4, 1.5), 'TP103': (1.4, -1.3), 'TP501': (1.4, -1.0), 'TP502': (1.4, 1.0),
                         'TP109': (-1.4, 2.4)},
    ('board_a', 'bottom'): {'TP102': (1.4, -0.2), 'TP104': (1.4, -1.0), 'TP111': (1.4, 1.2), 'TP202': (1.4, -1.0),
                            'TP1005': (1.4, 1.2), 'TP301': (1.4, -1.2), 'TP302': (1.4, 0.4), 'TP303': (1.4, 1.4),
                            'TP604': (1.4, -0.8), 'TP602': (1.4, 0.2), 'TP601': (1.4, 0.9), 'TP1013': (1.4, 0.8),
                            'TP1007': (1.4, -1.0), 'TP1008': (1.4, 1.0), 'TP201': (7.0, 5.0), 'TP204': (1.4, -1.4),
                            'TP205': (-1.4, 1.6), 'TP105': (1.4, 0.6), 'TP107': (1.4, -0.6), 'TP1002': (1.4, 0.8)},
}

VERTICAL = {('board_b', 'bottom')}          # pads in a row: labels run downwards


def kind(net):
    if net == 'GND':
        return 'gnd'
    if net.startswith(('I2C_PD', 'PD_EE_WP')):
        return 'prog'
    if net.startswith('DBG_'):
        return 'debug'
    if POWER.match(net):
        return 'power'
    return 'signal'


def xform(fx, fy, rot, x, y):
    """Footprint-local point to board coordinates (KiCad: y down, angle counter-clockwise on screen)."""
    a = math.radians(rot)
    return fx + x * math.cos(a) + y * math.sin(a), fy - x * math.sin(a) + y * math.cos(a)


def load(path):
    root = sexpr.parse(open(os.path.join(ROOT, path)).read())[0]
    xs, ys = [], []
    for k in ('gr_line', 'gr_arc', 'gr_rect'):
        for g in sexpr.find_all(root, k):
            if sexpr.find(g, 'layer')[1] == 'Edge.Cuts':
                for key in ('start', 'end', 'mid'):
                    n = sexpr.find(g, key)
                    if n:
                        xs.append(float(n[1]))
                        ys.append(float(n[2]))
    outline = (min(xs), min(ys), max(xs), max(ys))
    parts, tps = [], []
    for fp in sexpr.find_all(root, 'footprint'):
        side = 'top' if sexpr.find(fp, 'layer')[1] == 'F.Cu' else 'bottom'
        at = sexpr.find(fp, 'at')
        fx, fy, rot = float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0
        ref = next(str(p[2]) for p in sexpr.find_all(fp, 'property') if p[1] == 'Reference')
        if ref.startswith('TP'):
            net = next(str(sexpr.find(p, 'net')[-1]) for p in sexpr.find_all(fp, 'pad') if sexpr.find(p, 'net'))
            tps.append(dict(ref=ref, side=side, x=fx, y=fy, net=net.split('/')[-1]))
            continue
        if not ref.startswith(SHOW) or ref.startswith('JP'):
            continue
        pts = []
        for k in ('fp_line', 'fp_rect', 'fp_poly'):
            for g in sexpr.find_all(fp, k):
                if not str(sexpr.find(g, 'layer')[1]).endswith('CrtYd'):
                    continue
                cand = [sexpr.find(g, 'start'), sexpr.find(g, 'end')]
                p = sexpr.find(g, 'pts')
                if p:
                    cand += sexpr.find_all(p, 'xy')
                if k == 'fp_rect':
                    s, e = sexpr.find(g, 'start'), sexpr.find(g, 'end')
                    cand += [['xy', s[1], e[2]], ['xy', e[1], s[2]]]
                pts += [xform(fx, fy, rot, float(c[1]), float(c[2])) for c in cand if c]
        pads = [xform(fx, fy, rot, float(sexpr.find(p, 'at')[1]), float(sexpr.find(p, 'at')[2]))
                for p in sexpr.find_all(fp, 'pad')]
        if not pts:
            continue
        box = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
        bad = [p for p in pads if not (box[0] - 0.01 <= p[0] <= box[2] + 0.01 and box[1] - 0.01 <= p[1] <= box[3] + 0.01)]
        assert not bad, f'{ref}: pad outside its courtyard, transform wrong'
        parts.append(dict(ref=ref, side=side, box=box))
    return outline, parts, tps


def svg(board, view, outline, parts, tps):
    x0, y0, x1, y1 = outline
    m = 6.0                                       # margin, mm
    W, H = (x1 - x0) + 2 * m + 22, (y1 - y0) + 2 * m + 11 + (8 if (board, view) in VERTICAL else 0)
    mx = (lambda x: x1 - x + m) if view == 'bottom' else (lambda x: x - x0 + m)
    my = lambda y: y - y0 + m + 6                  # noqa: E731
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * SCALE:.0f}" height="{H * SCALE:.0f}" '
         f'viewBox="0 0 {W:.2f} {H:.2f}" font-family="DejaVu Sans, sans-serif">',
         f'<rect width="{W:.2f}" height="{H:.2f}" fill="#ffffff"/>',
         f'<text x="{m:.2f}" y="4.0" font-size="2.6" font-weight="bold">{board.replace("_", " ").title()}: test points, '
         f'{view} side</text>',
         f'<text x="{m:.2f}" y="7.4" font-size="1.7" fill="#555">'
         f'{"seen with the board turned over: left and right are swapped against the top view" if view == "bottom" else "seen from the component side the module plugs into"}'
         f'</text>',
         f'<rect x="{m:.2f}" y="{m + 6:.2f}" width="{x1 - x0:.2f}" height="{y1 - y0:.2f}" fill="#f4f1e8" '
         f'stroke="#555" stroke-width="0.25" rx="1"/>']
    for p in parts:
        bx0, by0, bx1, by1 = p['box']
        same = p['side'] == view
        xa, xb = sorted((mx(bx0), mx(bx1)))
        o.append(f'<rect x="{xa:.2f}" y="{my(by0):.2f}" width="{xb - xa:.2f}" height="{by1 - by0:.2f}" '
                 f'fill="{"#e0dccf" if same else "none"}" stroke="{"#9e9a8e" if same else "#d6d2c6"}" '
                 f'stroke-width="0.15" {"" if same else "stroke-dasharray=\"0.6 0.4\""}/>')
        if same and (bx1 - bx0) * (by1 - by0) > 6:
            o.append(f'<text x="{(xa + xb) / 2:.2f}" y="{my((by0 + by1) / 2) + 0.5:.2f}" font-size="1.4" '
                     f'fill="#8a867a" text-anchor="middle">{p["ref"]}</text>')
    for t in tps:
        if t['side'] != view:
            continue
        c = COLOURS[kind(t['net'])]
        x, y = mx(t['x']), my(t['y'])
        dx, dy = NUDGE.get((board, view), {}).get(t['ref'], (1.4, 0.0))
        if (board, view) in VERTICAL:
            o.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.75" fill="{c}" stroke="#fff" stroke-width="0.2"/>'
                     f'<text transform="translate({x - 0.55:.2f} {y + 1.3:.2f}) rotate(90)" font-size="1.55" '
                     f'fill="{c}" paint-order="stroke" stroke="#ffffff" stroke-width="0.45">'
                     f'<tspan font-weight="bold">{t["ref"]}</tspan> {t["net"]}</text>')
            continue
        o.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.75" fill="{c}" stroke="#fff" stroke-width="0.2"/>')
        if dy:
            o.append(f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{x + dx - math.copysign(0.3, dx):.2f}" y2="{y + dy - 0.4:.2f}" '
                     f'stroke="{c}" stroke-width="0.12"/>')
        anchor = 'end' if dx < 0 else 'start'
        o.append(f'<text x="{x + dx:.2f}" y="{y + dy + 0.0:.2f}" font-size="1.55" fill="{c}" text-anchor="{anchor}" '
                 f'paint-order="stroke" stroke="#ffffff" stroke-width="0.45">'
                 f'<tspan font-weight="bold">{t["ref"]}</tspan> {t["net"]}</text>')
    ly = H - 5.2
    for i, (k, lab) in enumerate((('power', 'supply rail'), ('gnd', 'ground'), ('prog', 'EEPROM programming'),
                                  ('debug', 'debug console'), ('signal', 'signal'))):
        lx = m + (0, 20, 36, 66, 90)[i]
        o.append(f'<circle cx="{lx:.2f}" cy="{ly - 0.5:.2f}" r="0.75" fill="{COLOURS[k]}"/>'
                 f'<text x="{lx + 1.4:.2f}" y="{ly:.2f}" font-size="1.6">{lab}</text>')
    o.append(f'<text x="{m:.2f}" y="{ly + 3.0:.2f}" font-size="1.3" fill="#8a867a">'
             f'grey boxes: parts on this side; dashed: other side. tools/tp_map.py</text>')
    o.append('</svg>')
    return '\n'.join(o)


def main():
    os.makedirs(OUT, exist_ok=True)
    for board, path in BOARDS.items():
        outline, parts, tps = load(path)
        for view in ('top', 'bottom'):
            if not any(t['side'] == view for t in tps):
                continue
            f = os.path.join(OUT, f'{board}_tp_{view}')
            open(f + '.svg', 'w').write(svg(board, view, outline, parts, tps))
            subprocess.run(['rsvg-convert', '-o', f + '.png', f + '.svg'], check=True)
            print(f + '.png', sum(t['side'] == view for t in tps), 'test points')


if __name__ == '__main__':
    main()
