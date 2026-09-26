"""Generate the style lab source map from tools/style_lab.py.

    python tools/bootstrap-style-lab.py [--overwrite]

Once written, the .map is the editable source (TrenchBroom). This bootstrap
is never part of a normal rebuild, and it refuses to overwrite an existing map
unless --overwrite is passed.

Every face names a LOOK and a ROLE ("looks/<look>/<role>"). The map is
written with the authored zoning (style_lab.MIX). Single-look comparison
palettes are remapped copies built at build time, never separate maps.
"""
from pathlib import Path
import math
import random
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brushkit as K
import style_lab as S

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'RedBreach/maps/style_lab_01.map'
if MAP.exists() and '--overwrite' not in sys.argv:
    raise SystemExit('Map already exists. Edit it in TrenchBroom, or pass --overwrite to regenerate.')
S.check()

LOOK = 'steel'


def R(name):
    return f'looks/{LOOK}/{name}'


def look(part):
    global LOOK
    LOOK = S.MIX[part]


m = K.Map(textures=[f'looks/{k}' for k in S.LOOKS])
SC = S.role_scale
W = S.SHELL_X


def mirror(poly):
    return [(-x, y) for x, y in poly]


# --- corridor sections ------------------------------------------------------
def section(profile, z0):
    z1 = z0 - S.SECTION_LEN
    look(profile)
    m.group(f'{profile} {S.PROFILES[profile]["title"]} ({LOOK})')
    segs = S.PROFILES[profile]['segments']
    ch = S.ceil_half(profile)
    # Ceiling slab over the whole shell width; only the clear part is seen.
    m.box(-W, W, S.CEIL_Y, S.SHELL_TOP, z1, z0, R('ceiling'), f'{profile} ceiling', scale=SC, tally='shell')
    for side in (1, -1):
        for (xa, ya), (xb, yb), role in segs:
            poly = [(xa, ya), (W, ya), (W, yb), (xb, yb)]
            if side < 0:
                poly = mirror(poly)
            kw = {}
            if role == 'plinth':
                # Anchor the painted lower half of a 2 m texture to the plinth
                # foot, so the band fills the plinth even on a slope.
                kw['anchor'] = ((side * xa, 0.0, z0), 64.0)
            m.prism_z(poly, z1, z0, R(role), f'{profile} {role} {"R" if side > 0 else "L"}',
                      scale=SC, tally='shell', **kw)
        # Ribs: per segment, a band between the wall line and a copy set
        # RIB_D inward, plus a beam under the ceiling.
        for st in S.RIB_STATIONS:
            zr = z0 - st
            for (xa, ya), (xb, yb), role in segs:
                poly = [(xa - S.RIB_D, ya), (xa, ya), (xb, yb), (xb - S.RIB_D, yb)]
                if side < 0:
                    poly = mirror(poly)
                m.prism_z(poly, zr - S.RIB_DEPTH / 2, zr + S.RIB_DEPTH / 2, R('rib'),
                          f'{profile} rib {st:g}', scale=SC, tally='rib')
    for st in S.RIB_STATIONS:
        zr = z0 - st
        m.box(-ch, ch, S.CEIL_Y - S.RIB_D, S.CEIL_Y, zr - S.RIB_DEPTH / 2, zr + S.RIB_DEPTH / 2,
              R('rib'), f'{profile} rib beam {st:g}', scale=SC, tally='rib')
    # Service panel in the middle bay on the left: 0.125 m proud of the main
    # wall segment, framed by its own edges.
    main = [s for s in segs if s[2] != 'plinth'][0]
    (xa, ya), (xb, yb), _ = main
    ylo, yhi = max(ya, 1.25), min(yb, 2.75)
    if yhi - ylo >= 0.75:
        f = lambda y: xa + (y - ya) / (yb - ya) * (xb - xa)
        poly = mirror([(f(ylo) - 0.125, ylo), (f(ylo) + 0.01, ylo), (f(yhi) + 0.01, yhi), (f(yhi) - 0.125, yhi)])
        zc = z0 - 6.0

        def service_tex(n, c, nx=-1):
            # The face looking into the corridor gets the service texture; the
            # thin edges read as a frame.
            return R('service') if n[0] > 0.5 else R('frame')
        m.prism_z(poly, zc - 1.5, zc + 1.5, service_tex, f'{profile} service panel', scale=SC, tally='detail')
    m.ungroup()


def bulkhead(zn, name, depth=S.BULKHEAD_LEN, extra=0.0, hazard_trim=False):
    """A thick frame between sections. zn is the near (+Z) face. ``extra``
    extends the far side, so B3 stands proud of the room wall."""
    zf = zn - depth - extra
    oh, ot, ck = S.OPENING_HALF, S.OPENING_TOP, S.OPENING_CHAMFER

    def tex(n, c):
        if abs(n[2]) > 0.5:
            return R('bulkhead')
        inside = abs(c[0]) <= oh + 1e-3 and c[1] <= ot + 1e-3
        return R('frame') if inside else R('bulkhead')
    look('bulkhead')
    m.group(name)
    for s in (1, -1):
        m.box(s * oh, s * W, 0, S.SHELL_TOP, zf, zn, tex, f'{name} jamb', scale=SC, tally='bulkhead')
        wedge = [(s * oh, ot - ck), (s * oh, ot), (s * (oh - ck), ot)]
        m.prism_z(wedge, zf, zn, tex, f'{name} chamfer', scale=SC, tally='bulkhead')
    m.box(-oh, oh, ot, S.SHELL_TOP, zf, zn, tex, f'{name} lintel', scale=SC, tally='bulkhead')
    if hazard_trim:
        # A thin warning edge round the opening on both faces: 0.25 m wide,
        # 0.0625 m proud. Hazard is a trim, never a surface.
        t, d = 0.25, 0.0625
        for zface, sgn in ((zn, 1), (zf, -1)):
            za, zb = zface, zface + sgn * d
            for s in (1, -1):
                m.box(s * oh, s * (oh + t), 0.0, ot - ck, za, zb, R('hazard'), f'{name} hazard jamb', scale=SC, tally='bulkhead')
            m.box(-(oh - ck), oh - ck, ot, ot + t, za, zb, R('hazard'), f'{name} hazard head', scale=SC, tally='bulkhead')
    m.ungroup()


# Floor: one continuous plate from the start door to the room portal.
look('floor')
m.group('Corridor floor')
m.box(-W, W, -0.5, 0.0, S.ROOM_Z0 - S.FRAME_PROUD, 0.5, R('floor'), 'corridor floor', scale=SC, tally='shell')
m.ungroup()

# Start: a sealed end wall with a door panel behind the spawn.
look('bulkhead')
m.group('Start door')
m.box(-W, W, 0.0, S.SHELL_TOP, 0.0, 0.5, R('bulkhead'), 'start end wall', scale=SC, tally='shell')
m.box(-1.5, 1.5, 0.0, 3.0, -0.125, 0.0,
      lambda n, c: R('door') if n[2] > 0.5 else R('frame'), 'start door panel', scale=SC, tally='detail')
m.ungroup()

for p, z0 in S.SECTIONS:
    section(p, z0)
for i, zb in enumerate(S.BULKHEADS[:-1]):
    bulkhead(zb, f'Bulkhead B{i + 1}')
bulkhead(S.BULKHEADS[-1], 'Bulkhead B3 portal', extra=S.FRAME_PROUD, hazard_trim=True)

# --- machine room -------------------------------------------------------------
inner = S.room_octagon()
outer = S.room_octagon(-S.ROOM_SHELL)
top = S.room_octagon(S.HAUNCH)
n = len(inner)
m.group('Machine room shell')
look('floor')
m.prism_y(outer, -0.5, 0.0, R('floor'), 'room floor', scale=SC, tally='room')
look('room')
m.prism_y(outer, S.ROOM_CEIL, S.ROOM_CEIL + 0.5, R('ceiling'), 'room ceiling', scale=SC, tally='room')

oh, ot = S.OPENING_HALF, S.OPENING_TOP
win = S.WINDOW


def wall_piece(a, b, oa, ob, y0, y1, tex, name):
    m.hull([(a[0], y, a[1]) for y in (y0, y1)] + [(b[0], y, b[1]) for y in (y0, y1)]
           + [(oa[0], y, oa[1]) for y in (y0, y1)] + [(ob[0], y, ob[1]) for y in (y0, y1)],
           tex, name, scale=SC, tally='room')


def lerp2(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def window_tex(n, c):
    inside = (c[0] > S.ROOM_HALF - 0.01 and win['z0'] - 1e-3 <= c[2] <= win['z1'] + 1e-3
              and win['y0'] - 1e-3 <= c[1] <= win['y1'] + 1e-3)
    return R('frame') if inside else (R('wall') if c[1] > S.PLINTH_H else R('plinth'))


for i in range(n):
    a, b = inner[i], inner[(i + 1) % n]
    oa, ob = outer[i], outer[(i + 1) % n]
    ta, tb = top[i], top[(i + 1) % n]
    # Haunch: from the wall head in to the ceiling at 45 degrees, mitred on
    # the bisectors so neighbouring haunches meet cleanly.
    m.hull([(a[0], S.ROOM_WALL_H, a[1]), (b[0], S.ROOM_WALL_H, b[1]),
            (oa[0], S.ROOM_WALL_H, oa[1]), (ob[0], S.ROOM_WALL_H, ob[1]),
            (oa[0], S.ROOM_CEIL, oa[1]), (ob[0], S.ROOM_CEIL, ob[1]),
            (ta[0], S.ROOM_CEIL, ta[1]), (tb[0], S.ROOM_CEIL, tb[1])],
           R('slope'), f'room haunch {i}', scale=SC, tally='room')
    south = abs(a[1] - S.ROOM_Z0) < 1e-6 and abs(b[1] - S.ROOM_Z0) < 1e-6
    east = abs(a[0] - S.ROOM_HALF) < 1e-6 and abs(b[0] - S.ROOM_HALF) < 1e-6
    if south:
        # The B3 frame fills |x| <= SHELL_X; the room wall runs either side of it.
        for s, (p, q, op, oq) in ((-1, (a, (-W, a[1]), oa, (-W, oa[1]))), (1, ((W, a[1]), b, (W, ob[1]), ob))):
            for y0, y1, role in ((0, S.PLINTH_H, 'plinth'), (S.PLINTH_H, S.ROOM_WALL_H, 'wall')):
                wall_piece(p, q, op, oq, y0, y1, R(role), f'room south {role}')
        wall_piece((-W, a[1]), (W, a[1]), (-W, oa[1]), (W, oa[1]), S.SHELL_TOP, S.ROOM_WALL_H, R('wall'), 'room south over portal') if S.SHELL_TOP < S.ROOM_WALL_H else None
        continue
    if east:
        # a -> b runs from z0-clip down to z1+clip. Split around the window.
        za, zb = a[1], b[1]
        t0 = (za - win['z1']) / (za - zb)
        t1 = (za - win['z0']) / (za - zb)
        w0, w1 = lerp2(a, b, t0), lerp2(a, b, t1)
        o0, o1 = lerp2(oa, ob, t0), lerp2(oa, ob, t1)
        o0 = (ob[0], w0[1]); o1 = (ob[0], w1[1])
        for p, q, op, oq in ((a, w0, oa, o0), (w1, b, o1, ob)):
            wall_piece(p, q, op, oq, 0, S.PLINTH_H, R('plinth'), 'room east plinth')
            wall_piece(p, q, op, oq, S.PLINTH_H, S.ROOM_WALL_H, R('wall'), 'room east pier')
        wall_piece(w0, w1, o0, o1, 0, S.PLINTH_H, window_tex, 'room east sill')
        wall_piece(w0, w1, o0, o1, win['y1'], S.ROOM_WALL_H, window_tex, 'room east lintel')
        continue
    wall_piece(a, b, oa, ob, 0, S.PLINTH_H, R('plinth'), f'room plinth {i}')
    wall_piece(a, b, oa, ob, S.PLINTH_H, S.ROOM_WALL_H, R('wall'), f'room wall {i}')
m.ungroup()

# Plinth band inside the room: 0.125 proud of the wall so the texture change
# sits on a real step.
m.group('Machine room plinth band')
band = S.room_octagon(0.125)
for i in range(n):
    a, b = band[i], band[(i + 1) % n]
    ia, ib = inner[i], inner[(i + 1) % n]
    if abs(ia[1] - S.ROOM_Z0) < 1e-6 and abs(ib[1] - S.ROOM_Z0) < 1e-6:
        # Skip across the portal frame.
        for p, q, ip, iq in (((a[0], a[1]), (-W - 0.01, a[1]), ia, (-W - 0.01, ia[1])),
                             ((W + 0.01, b[1]), b, (W + 0.01, ib[1]), ib)):
            m.hull([(p[0], y, p[1]) for y in (0, S.PLINTH_H)] + [(q[0], y, q[1]) for y in (0, S.PLINTH_H)]
                   + [(ip[0], y, ip[1]) for y in (0, S.PLINTH_H)] + [(iq[0], y, iq[1]) for y in (0, S.PLINTH_H)],
                   R('plinth'), 'room plinth band', scale=SC, tally='room')
        continue
    if abs(ia[0] - S.ROOM_HALF) < 1e-6 and abs(ib[0] - S.ROOM_HALF) < 1e-6:
        # Under the window the band continues as the sill's face.
        pass
    m.hull([(a[0], y, a[1]) for y in (0, S.PLINTH_H)] + [(b[0], y, b[1]) for y in (0, S.PLINTH_H)]
           + [(ia[0], y, ia[1]) for y in (0, S.PLINTH_H)] + [(ib[0], y, ib[1]) for y in (0, S.PLINTH_H)],
           R('plinth'), 'room plinth band', scale=SC, tally='room')
m.ungroup()

# Window frame (proud of the wall), glass (clip) and the view outside.
m.group('Window onto Mars')
x0, x1 = S.ROOM_HALF - 0.125 - 0.25, S.ROOM_HALF - 0.125
fz0, fz1 = win['z0'] - 0.25, win['z1'] + 0.25
m.box(x0, x1, win['y0'] - 0.25, win['y0'], fz0, fz1, R('frame'), 'window sill frame', scale=SC, tally='detail')
m.box(x0, x1, win['y1'], win['y1'] + 0.25, fz0, fz1, R('frame'), 'window head frame', scale=SC, tally='detail')
for zz in ((fz0, win['z0']), (win['z1'], fz1)):
    m.box(x0, x1, win['y0'], win['y1'], zz[0], zz[1], R('frame'), 'window post', scale=SC, tally='detail')
m.box(S.ROOM_HALF + 0.125, S.ROOM_HALF + 0.25, win['y0'], win['y1'], win['z0'], win['z1'], 'clip', 'window glass (clip)', tally='detail')
m.ungroup()

look('exterior')
m.group('Mars exterior')
m.box(S.ROOM_HALF + S.ROOM_SHELL, 140, -2.0, -1.5, -150, 40, R('ground'), 'regolith plain', tally='exterior')
m.box(-40, S.ROOM_HALF + S.ROOM_SHELL, -2.0, -1.5, -150, -56, R('ground'), 'regolith behind', tally='exterior')
rng = random.Random(7)


def rock(cx, cz, r, h, name, sink=-1.5):
    pts = []
    for k in range(9):
        ang = k / 9 * math.tau + rng.uniform(-0.25, 0.25)
        rr = r * rng.uniform(0.7, 1.1)
        pts.append((cx + math.cos(ang) * rr, sink - 0.3, cz + math.sin(ang) * rr))
        rr2 = rr * rng.uniform(0.35, 0.7)
        pts.append((cx + math.cos(ang + 0.3) * rr2, sink + h * rng.uniform(0.6, 1.0), cz + math.sin(ang + 0.3) * rr2))
    m.hull(pts, R('rock'), name, tally='exterior')


for k, (cx, cz, r, h) in enumerate([(18, -40, 1.6, 1.4), (23, -52, 2.4, 2.0), (31, -45, 1.2, 0.9),
                                     (40, -60, 4.0, 3.5), (47, -33, 3.2, 2.2), (60, -48, 6.5, 6.0),
                                     (15, -58, 1.0, 0.7), (26, -36, 0.8, 0.6)]):
    rock(cx, cz, r, h, f'rock {k}')
# A distant mesa: a flat-topped mass with a talus apron, big enough to read as landform.
m.hull([(95, -1.5, -20), (95, -1.5, -85), (125, -1.5, -95), (125, -1.5, -10),
        (104, 16, -30), (104, 16, -72), (118, 16, -76), (118, 16, -26)], R('rock'), 'mesa', tally='exterior')
m.hull([(80, -1.6, -35), (80, -1.6, -62), (98, 5, -64), (98, 5, -33), (98, -1.6, -30), (98, -1.6, -66)],
       R('rock'), 'mesa talus', tally='exterior')
m.ungroup()

# --- machine ------------------------------------------------------------------
M = S.MACHINE
cx, cz = M['cx'], M['cz']


def octagon(r, chamfer):
    return [(cx - r + chamfer, cz - r), (cx + r - chamfer, cz - r), (cx + r, cz - r + chamfer),
            (cx + r, cz + r - chamfer), (cx + r - chamfer, cz + r), (cx - r + chamfer, cz + r),
            (cx - r, cz + r - chamfer), (cx - r, cz - r + chamfer)]


def reg_oct(r):
    return [(cx + r * math.cos(k * math.pi / 4 + math.pi / 8), cz + r * math.sin(k * math.pi / 4 + math.pi / 8))
            for k in range(8)]


look('machine')
m.group('Machine')
pl = octagon(M['plinth'], M['plinth_chamfer'])
m.prism_y(pl, 0.0, M['plinth_h'], R('machine_base'),
          'machine plinth', scale=SC, tally='machine')
# Curb lip around the pool: eight pieces between the plinth edge and a 0.25 inset.
lip_in = S.offset_polygon(pl, M['lip'])
for i in range(8):
    a, b, ia, ib = pl[i], pl[(i + 1) % 8], lip_in[i], lip_in[(i + 1) % 8]
    m.hull([(p[0], y, p[1]) for p in (a, b, ia, ib) for y in (M['plinth_h'], M['lip_h'])],
           lambda n, c: R('machine_top') if n[1] > 0.5 else R('hazard'), 'machine curb', scale=SC, tally='machine')
m.prism_y(lip_in, M['plinth_h'], M['pool_top'], R('coolant'), 'coolant pool', scale=SC, tally='machine')
tank = reg_oct(M['tank_r'])
m.prism_y(tank, M['plinth_h'], M['tank_top'], R('machine_body'), 'tank', scale=SC, tally='machine')
m.prism_y(reg_oct(M['cap_r']), M['tank_top'], M['cap_top'], R('machine_top'), 'tank cap', scale=SC, tally='machine')
# Glow slots on alternate faces of the tank: thin emissive panels, 0.0625 proud.
for k in range(0, 8, 2):
    a, b = tank[k], tank[(k + 1) % 8]
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    dx, dz = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L
    nx, nz = (mid[0] - cx), (mid[1] - cz)
    nl = math.hypot(nx, nz); nx, nz = nx / nl, nz / nl
    pts = []
    for s in (-0.2, 0.2):
        for off in (-0.02, 0.0625):
            pts += [(mid[0] + ux * s + nx * off, y, mid[1] + uz * s + nz * off) for y in (1.25, 3.5)]
    m.hull(pts, R('coolant'), f'tank glow slot {k}', scale=SC, tally='machine')
# Service pipes: two risers to the ceiling and one overhead run to the north wall.
for px in (-0.75, 0.75):
    m.box(px - 0.25, px + 0.25, M['cap_top'], S.ROOM_CEIL, cz - 0.25, cz + 0.25, R('pipe'), 'riser', scale=SC, tally='machine')
m.box(-0.25, 0.25, 3.0, 3.5, S.ROOM_Z1, cz - M['tank_r'] + 0.1, R('pipe'), 'overhead run', scale=SC, tally='machine')
# Two control desks facing the tank, with sloped emissive screens.
for s in (-1, 1):
    x = s * 5.0
    desk = [(x - 0.5, 0.0, cz - 1.2), (x + 0.5, 0.0, cz - 1.2), (x - 0.5, 0.0, cz + 1.2), (x + 0.5, 0.0, cz + 1.2)]
    hi_x, lo_x = (x + 0.5 * s, x - 0.5 * s)
    desk += [(hi_x, 1.25, cz - 1.2), (hi_x, 1.25, cz + 1.2), (lo_x, 0.95, cz - 1.2), (lo_x, 0.95, cz + 1.2)]

    def desk_tex(n, c, s=s):
        return R('screen') if n[1] > 0.5 else R('machine_body')
    m.hull(desk, desk_tex, 'control desk', scale=SC, tally='machine')
m.ungroup()

MAP.parent.mkdir(parents=True, exist_ok=True)
MAP.write_text(m.text('Style lab S-01. Generated by tools/bootstrap-style-lab.py; now the editable source.'),
               encoding='utf-8')
print(f'STYLE_LAB_MAP: {m.count} brushes -> {MAP.relative_to(ROOT)}')
print('  ' + ', '.join(f'{k} {v}' for k, v in sorted(m.tally.items())))
