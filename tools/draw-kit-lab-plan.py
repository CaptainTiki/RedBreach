"""Draw the K-01 kit lab paper plan: docs/kit-lab-plan.png.

A paper proposal only; it never edits a map or scene. Every number comes from
tools/kit_lab.py (and the profiles from tools/style_lab.py), so the drawing
cannot disagree with the plan module.
"""
from pathlib import Path
import math
import sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_lab as K
import style_lab as S

ROOT = Path(__file__).resolve().parents[1]
W, H = 1960, 1180
im = Image.new('RGB', (W, H), '#101b25')
d = ImageDraw.Draw(im)
LOOK = {'steel': '#4f6272', 'concrete': '#7f8a92', 'warm': '#9c7445'}
EDGE, TEXT, NOTE, ACCENT, GOOD, BAD = '#c9d4da', '#e8eef2', '#9fb2bf', '#e8bd77', '#79c7a8', '#e0715f'


def font(n):
    return ImageFont.truetype('arial.ttf', n)


def text(x, y, s, n=18, c=TEXT, anchor='la'):
    d.text((x, y), s, font=font(n), fill=c, anchor=anchor)


K.check()
text(40, 26, 'K-01 / KIT LAB', 34)
text(40, 70, 'Paper plan for review. Phase 2 of the clean-slate test plan, in the settled Phase 1 style. Nothing is built.', 19, ACCENT)

# --- plan view ---------------------------------------------------------------
SC = 11.0
XMIN, YMAX = -37.0, 76.0
OX, OY = 40, 110


def P(x, y):
    return (OX + (x - XMIN) * SC, OY + (YMAX - y) * SC)


def poly(pts, fill, outline=EDGE, w=2):
    q = [P(*p) for p in pts]
    d.polygon(q, fill=fill)
    d.line(q + [q[0]], fill=outline, width=w)


def octagon(cx, cy, flats, clip):
    h = flats / 2
    return [(cx - h + clip, cy - h), (cx + h - clip, cy - h), (cx + h, cy - h + clip), (cx + h, cy + h - clip),
            (cx + h - clip, cy + h), (cx - h + clip, cy + h), (cx - h, cy + h - clip), (cx - h, cy - h + clip)]


def band(path, width, fill):
    """A corridor footprint: a thick polyline, 6 m wide at plan scale, with an outline."""
    pts = [P(*p) for p in path]
    d.line(pts, fill=EDGE, width=int(width * SC) + 4, joint='curve')
    d.line(pts, fill=fill, width=int(width * SC), joint='curve')


def bulkhead_bar(x, y, horizontal):
    a, b = ((x - 3.5, y), (x + 3.5, y)) if horizontal else ((x, y - 3.5), (x, y + 3.5))
    d.line([P(*a), P(*b)], fill='#1b252e', width=int(K.BULKHEAD * SC))
    d.line([P(x - 2, y) if horizontal else P(x, y - 2), P(x + 2, y) if horizontal else P(x, y + 2)],
           fill='#c8a060', width=3)


def label(x, y, s, n=15, c=TEXT):
    text(*P(x, y), s, n, c, anchor='mm')


# Corridors first so rooms draw over their ends.
band([(0, K.C1['y0']), (0, K.C1['y1'] + 1)], 6, LOOK['steel'])
band([(0, K.C2['y0'] - 1), (0, K.C2['y1']), K.T1['b'], (K.C3['x1'] + 1, K.C3['y'])], 6, LOOK['concrete'])
band([(K.C5['x0'] - 1, K.C5['y']), (K.C5['x1'], K.C5['y']), K.T2['b'], (K.S1['x'], K.S1['y1'] + 1)], 6, LOOK['steel'])
band([(K.C4['x0'] - 1, K.C4['y']), (K.C4['x1'] + 1, K.C4['y'])], 6, LOOK['warm'])

# Rooms.
poly([(K.A0['x0'], K.A0['y0']), (K.A0['x1'], K.A0['y0']), (K.A0['x1'], K.A0['y1']), (K.A0['x0'], K.A0['y1'])], LOOK['steel'])
poly(octagon(K.HUB['cx'], K.HUB['cy'], K.HUB['flats'], K.HUB['clip']), LOOK['steel'])
poly(octagon(K.R1['cx'], K.R1['cy'], K.R1['flats'], K.R1['clip']), LOOK['warm'])
hx0, hx1, hy0, hy1 = K.HALL['x0'], K.HALL['x1'], K.HALL['y0'], K.HALL['y1']
poly([(hx0, hy0), (hx1, hy0), (hx1, hy1), (hx0, hy1)], LOOK['concrete'])
# Hall: knee-wall slopes drawn as the ceiling outline, portal frames, catwalk, stair, tanks.
cw = (hx1 - hx0) / 2 - K.HALL['ceil_half']
d.rectangle([P(hx0 + cw, hy1), P(hx1 - cw, hy0)], outline='#a9b3b9', width=1)
for fy in K.HALL['frames']:
    d.line([P(hx0, fy), P(hx1, fy)], fill='#2b3740', width=5)
cat = K.CATWALK
d.rectangle([P(22.0, hy0 + cat['width']), P(hx1, hy0)], fill='#5d6a73', outline=ACCENT, width=2)
d.rectangle([P(hx1 - cat['width'], 62.0), P(hx1, hy0)], fill='#5d6a73', outline=ACCENT, width=2)
st = K.HALL_STAIR
d.rectangle([P(hx1 - st['width'], st['y1']), P(hx1, st['y0'])], fill='#6e7a82', outline=ACCENT, width=2)
for k in range(K.S1_RISERS + 1):
    yy = st['y0'] + k * K.TREAD
    d.line([P(hx1 - st['width'], yy), P(hx1, yy)], fill='#2b3740', width=1)
for tx, ty in K.HALL_TANKS:
    r = 2.0
    d.ellipse([P(tx - r, ty + r), P(tx + r, ty - r)], fill=LOOK['warm'], outline='#6fd9c1', width=3)
label((hx0 + hx1) / 2, hy1 + 3.2, 'H1  KNEE-WALL HALL  24 x 32 m, walls 6 m, ceiling 10 m', 14)
label(34.5, 40.4, 'catwalk +3.0', 13, ACCENT)
text(*P(hx1 - 3.3, 66.0), 'stair down', 13, ACCENT, anchor='rm')
# Stair S1 steps.
for k in range(K.S1_RISERS + 1):
    yy = K.S1['y0'] + K.LANDING + k * K.TREAD
    d.line([P(K.S1['x'] - 2, yy), P(K.S1['x'] + 2, yy)], fill='#1b252e', width=1)
label(K.S1['x'] + 5.4, 32.0, 'S1 stair', 14)
label(K.S1['x'] + 5.4, 30.4, '0 -> +3.0 m', 12, ACCENT)
# Debris D1 on the north side of C3.
rng = [(K.D1['x0'], K.C3['y'] + 0.4), (K.D1['x0'] + 1.2, K.C3['y'] + 2.9), (K.D1['x1'] - 0.6, K.C3['y'] + 3.0),
       (K.D1['x1'], K.C3['y'] + 1.0), (K.D1['x1'] - 1.6, K.C3['y'] + 0.2)]
poly(rng, '#3a3027', '#e0a060', 2)
d.line([P(K.D1['x0'] + 0.5, K.C3['y'] + 2.2), P(K.D1['x1'] - 0.3, K.C3['y'] - 0.1)], fill='#d0d6da', width=5)
label((K.D1['x0'] + K.D1['x1']) / 2 + 1.5, K.C3['y'] - 4.4, 'D1 fallen rib + panels', 13, '#e0a060')
label((K.D1['x0'] + K.D1['x1']) / 2 + 1.5, K.C3['y'] - 5.8, 'lane 2.4 m kept', 12, NOTE)
# Collapse X1 in C4.
d.rectangle([P(K.X1['x0'], K.C4['y'] + 3), P(K.X1['x1'], K.C4['y'] - 3)], fill='#2a2522', outline='#e0a060', width=2)
d.rectangle([P(K.X1['x0'], K.C4['y'] + 1), P(K.X1['x1'], K.C4['y'] - 1)], fill='#5a4a3c')
label((K.X1['x0'] + K.X1['x1']) / 2, K.C4['y'] + 5.6, 'X1 collapse', 13, '#e0a060')
label((K.X1['x0'] + K.X1['x1']) / 2, K.C4['y'] + 4.2, '2.0 x 1.4 m crouch', 12, NOTE)
# Bulkheads.
bulkhead_bar(0, K.C1['y1'] + 0.5, True)
bulkhead_bar(0, K.C2['y0'] - 0.5, True)
bulkhead_bar(K.C5['x0'] - 0.5, K.C5['y'], False)
bulkhead_bar(K.C4['x1'] + 0.5, K.C4['y'], False)
bulkhead_bar(K.C4['x0'] - 0.5, K.C4['y'], False)
bulkhead_bar(K.C3['x1'] + 0.5, K.C3['y'], False)
bulkhead_bar(K.S1['x'], K.S1['y1'] + 0.5, True)
# Doors.
for x, y, s in ((hx0, K.C3['y'], 'wide door'), (K.C4['x0'] - 1.0, K.C4['y'], 'door')):
    cx, cy = P(x, y)
    d.rectangle([cx - 5, cy - 16, cx + 5, cy + 16], fill='#d7a24a')
    text(cx, cy - 22, s, 12, '#d7a24a', anchor='md')
# Window on R1.
wx, wy = P(K.R1['cx'] - K.R1['flats'] / 2, K.R1['cy'])
d.line([(wx, wy - 22), (wx, wy + 22)], fill='#ffb070', width=6)
# Hatches.
for kind, where, (x, y) in K.HATCHES:
    cx, cy = P(x, y)
    d.rectangle([cx - 9, cy - 9, cx + 9, cy + 9], outline='#b48cf0', width=2)
    text(cx, cy, 'H', 12, '#b48cf0', anchor='mm')
# Labels.
label(0, 0, 'A0 arrival', 14)
label(0, -1.8, 'sealed airlock', 11, NOTE)
label(0, 9, 'C1  P1', 14)
label(0, 26.6, 'J1 HUB', 15)
label(0, 19.4, '14 m octagon, 4 ports', 11, NOTE)
label(0, 36, 'C2 P1', 13)
label(-5.2, 44.5, 'T1 45 deg', 13)
label(K.C3['x0'] + 2.4, K.C3['y'] + 4.2, 'C3 P1', 13)
label(17, 26.6, 'C5  P2', 14)
label(29.5, 24.2, 'T2', 13)
label(-11.5, 18.6, 'C4  P2', 14)
label(-30, 23.8, 'R1 control', 14)
label(-30, 22.0, '10 m, +0.25 step', 11, NOTE)
label(-30, 20.4, '3.5 m ceiling', 11, NOTE)
label(-37.0 + 1.5, 23, 'W', 12, '#ffb070')
# North arrow and scale bar.
nx, ny = P(-34, 66)
d.line([(nx, ny + 30), (nx, ny - 10)], fill=TEXT, width=3)
d.polygon([(nx, ny - 18), (nx - 7, ny - 4), (nx + 7, ny - 4)], fill=TEXT)
text(nx, ny + 36, 'N', 14, TEXT, anchor='ma')
sx, sy = P(-34, 58)
d.line([(sx, sy), (sx + 10 * SC, sy)], fill=TEXT, width=3)
text(sx, sy + 8, '10 m', 12, NOTE)
# Route.
route = [(0, 1), (0, 12), (4, 23), (20, 23), (30, 31), (30, 39.5), (38.5, 50), (38.5, 66), (28, 64), (20, 46),
         (10, 44.2), (2, 44), (0, 34), (0, 27)]
d.line([P(*p) for p in route], fill='#79c7a8', width=2)
for i, p in enumerate(route[::2]):
    cx, cy = P(*p)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill='#79c7a8')
    text(cx, cy, str(i + 1), 11, '#101b25', anchor='mm')
text(OX, OY + 895, 'Green: the loop  A0 > C1 > hub > C5 > T2 > S1 up > catwalk (the hall seen from above first) > hall stair down > floor >', 14, GOOD)
text(OX, OY + 915, 'wide door > C3 past D1 > T1 > C2 > hub.  Spur: hub > C4 > crouch X1 > door > R1.   H = sealed hatch reservation.', 14, GOOD)
text(OX, OY + 941, 'Looks: steel = arrival, hub and east branch;  concrete = north branch and hall shell;  warm = west branch, R1 and hall machinery.', 14, NOTE)

# --- sections (right-hand side) ----------------------------------------------
RX = 960


def section_frame(x, y, title):
    text(x, y, title, 18)


def profile_section(ox, oy, key, s, title):
    section_frame(ox, oy - 34, title)
    segs = S.PROFILES[key]['segments']
    pts = [(0, 0)]
    for (xa, ya), (xb, yb), role in segs:
        if role == 'plinth':
            continue
        pts += [(xa, ya), (xb, yb)]
    right = [(x, y) for x, y in pts[1:]]
    outline = [(-x, y) for x, y in right] + list(reversed(right))
    q = [(ox + x * s, oy + (S.CEIL_Y - y) * s) for x, y in [(-3, 0)] + outline + [(3, 0)]]
    d.polygon(q, fill='#283c47')
    d.line(q + [q[0]], fill=EDGE, width=3)
    person(ox, oy + S.CEIL_Y * s, s, STAND=True)
    text(ox, oy + S.CEIL_Y * s + 8, f'{2 * S.wall_x(key, 1.8):.2f} m clear at 1.8 m', 12, NOTE, anchor='ma')


def person(cx, floor_y, s, STAND=True, color='#dce4e7', h=None):
    h = h or (K.STAND_H if STAND else K.CROUCH_H)
    r = K.CAPSULE_R * s
    d.rounded_rectangle([cx - r, floor_y - h * s, cx + r, floor_y], radius=int(r), outline=color, width=3)


# P1 and P2 at 26 px/m.
profile_section(RX + 110, 150, 'P1', 26, 'P1 signature')
profile_section(RX + 330, 150, 'P2', 26, 'P2 secondary')

# X1 crouch passage, P2 section at 26 px/m.
ox, oy, s = RX + 590, 150, 26
section_frame(ox - 80, oy - 34, 'X1 collapse section')
q = [(ox + x * s, oy + (S.CEIL_Y - y) * s) for x, y in [(-3, 0), (-3, 2), (-1.75, 4), (1.75, 4), (3, 2), (3, 0)]]
d.polygon(q, fill='#283c47'); d.line(q + [q[0]], fill=EDGE, width=3)
fy = oy + S.CEIL_Y * s
d.polygon([(ox - 3 * s, fy), (ox - 1 * s, fy), (ox - 1 * s, fy - 1.4 * s), (ox - 1.9 * s, fy - 2.6 * s), (ox - 3 * s, fy - 2.0 * s)], fill='#5a4a3c', outline='#e0a060')
d.polygon([(ox + 3 * s, fy), (ox + 1 * s, fy), (ox + 1 * s, fy - 1.4 * s), (ox + 2.1 * s, fy - 2.4 * s), (ox + 3 * s, fy - 2.0 * s)], fill='#5a4a3c', outline='#e0a060')
d.rectangle([ox - 1.6 * s, fy - 1.75 * s, ox + 1.6 * s, fy - 1.4 * s], fill='#6b5a48', outline='#e0a060')
person(ox - 0.4 * s, fy, s, STAND=False, color=GOOD)
text(ox, fy + 8, '2.0 x 1.4 m clear', 12, NOTE, anchor='ma')
text(ox, fy + 24, 'crouch 1.1 passes, stand 1.8 blocked', 12, NOTE, anchor='ma')
text(ox, fy + 40, 'the larger bugs (1.9 m) cannot follow', 12, ACCENT, anchor='ma')

# Hall cross-section at 16 px/m.
ox, oy, s = RX + 200, 440, 16
section_frame(RX, oy - 34, 'H1 hall cross-section (west -> east)')
hw = (hx1 - hx0) / 2
q = [(ox + x * s, oy + (K.HALL['ceil'] - y) * s) for x, y in
     [(-hw, 0), (-hw, K.HALL['knee']), (-K.HALL['ceil_half'], K.HALL['ceil']), (K.HALL['ceil_half'], K.HALL['ceil']),
      (hw, K.HALL['knee']), (hw, 0)]]
d.polygon(q, fill='#283c47'); d.line(q + [q[0]], fill=EDGE, width=3)
fy = oy + K.HALL['ceil'] * s
cy = fy - K.CATWALK['level'] * s
d.rectangle([ox + (hw - K.CATWALK['width']) * s, cy, ox + hw * s, cy + 0.3 * s], fill='#8a969c')
d.line([(ox + (hw - K.CATWALK['width']) * s, cy), (ox + (hw - K.CATWALK['width']) * s, cy - 1.1 * s)], fill=ACCENT, width=2)
person(ox + (hw - 1.4) * s, cy, s)
tx = ox + (28.0 - (hx0 + hx1) / 2) * s
d.rectangle([tx - 2 * s, fy - 5 * s, tx + 2 * s, fy], fill=LOOK['warm'], outline='#6fd9c1', width=2)
d.rectangle([tx - 3 * s, fy - 0.5 * s, tx + 3 * s, fy], fill='#3a4046')
person(ox - 8 * s, fy, s)
text(ox, fy + 8, '24 m floor; vertical knee walls to 6 m carry the catwalk; slopes in to a 16 m ceiling at 10 m', 12, NOTE, anchor='ma')
text(ox + hw * s + 10, cy - 12, 'catwalk +3.0, 3 m wide, open rail', 12, ACCENT)
text(ox + hw * s + 10, fy - K.HALL['knee'] * s, 'knee 6 m', 12, NOTE)
text(ox + K.HALL['ceil_half'] * s + 10, oy - 6, 'ceiling 10 m', 12, NOTE)

# S1 stair long-section at 18 px/m.
ox, oy, s = RX + 40, 720, 18
section_frame(RX, oy - 34, 'S1 stair long-section (south -> north)')
floor = oy + 5 * s
x = ox
pts = [(x, floor)]
x += K.LANDING * s; pts.append((x, floor))
for k in range(K.S1_RISERS):
    y = floor - (k + 1) * K.RISER * s
    pts += [(x, y), (x + K.TREAD * s, y)]
    x += K.TREAD * s
pts.append((x + K.LANDING * s, floor - K.S1['rise'] * s))
x_end = x + K.LANDING * s
d.line(pts, fill=EDGE, width=3)
d.rectangle([x_end, floor - K.S1['rise'] * s - 3.25 * s, x_end + K.BULKHEAD * s, floor - K.S1['rise'] * s], outline='#c8a060', width=2)
person(ox + 1.0 * s, floor, s)
person(x_end - 1.0 * s, floor - K.S1['rise'] * s, s)
text(ox, floor + 10, f'2 m landing, {K.S1_RISERS} risers x 0.25 m on 0.5 m treads ({K.S1_FLIGHT:g} m), 2 m landing, bulkhead onto the catwalk', 12, NOTE)
text(ox, floor + 26, 'P2 corridor: stair 4 m wide between guards. The top landing looks through the bulkhead into the hall.', 12, NOTE)

# Questions and notes.
qx, qy = RX, 860
text(qx, qy, 'WHAT EACH PIECE ANSWERS', 18, ACCENT)
notes = [
    'B1 joins: T1/T2 test the trapezoid mitre on the bisector; J1 replaces the T and 4-way with bulkhead ports.',
    'B3 scale: R1 small (office, low ceiling), H1 hall (height transition, catwalk). Medium = the Phase 1 machine room.',
    'B4 interrupters: D1 walk-around, X1 crouch, doors at H1 and R1, a threshold step at R1.',
    'D1/D2 bugs: navigation baked; paths must route round D1, fail through X1, climb S1. Four sealed hatch reservations.',
    'E2 handoff: every piece is its own TrenchBroom group; you edit one, we rebuild.',
    'E3 validator: route and probe MARKERS placed in the map drive one generic validator for every map.',
    'Output: a one-page kit sheet (dimensions, brush counts, rules) and authoring time per piece.',
]
for i, n in enumerate(notes):
    text(qx, qy + 30 + i * 22, n, 13, TEXT)

out = ROOT / 'docs/kit-lab-plan.png'
im.save(out)
print('KIT_LAB_PLAN:', out.relative_to(ROOT))
