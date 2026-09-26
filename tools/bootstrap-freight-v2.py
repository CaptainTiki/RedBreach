"""Generate the freight v2 G-01 greybox map from tools/freight_v2.py.

    python tools/bootstrap-freight-v2.py                 # refuses to overwrite an existing map
    python tools/bootstrap-freight-v2.py --overwrite     # regenerate the whole level
    python tools/bootstrap-freight-v2.py --room PR       # regenerate ONE room's groups in the existing map

Once written, the .map is the editable source (TrenchBroom). This bootstrap is
never part of a normal rebuild. Every room and corridor is its own TrenchBroom
group, named by its plan key, and its lights and ladders belong to that group,
so a room can be isolated and edited by hand without touching the rest. Walls
between two rooms are their own group ("KEY|KEY walls"). --room KEY swaps only
the groups whose names start with KEY (and the shared walls that name it),
keeping every other group, hand edits included.

Plan coordinates (x east, y north) map to Godot as (x, height, -y).
"""
from pathlib import Path
import json
import math
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brushkit as B
import freight_v2 as F
import polykit as P
import style_lab as S

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'RedBreach/maps/freight_v2_01.map'
ROOM_ARG = sys.argv[sys.argv.index('--room') + 1] if '--room' in sys.argv else None
if MAP.exists() and '--overwrite' not in sys.argv and ROOM_ARG is None:
    raise SystemExit('Map already exists. Edit it in TrenchBroom, pass --room KEY to regenerate one room, '
                     'or --overwrite to regenerate everything.')
problems = F.check()
if problems:
    raise SystemExit('plan problems:\n' + '\n'.join(problems))
S.check()
CATALOG = json.loads((ROOT / 'docs/texture-catalog.json').read_text(encoding='utf-8'))
EMISSIVE = 'greybox/Emissive/texture_01'


def tex_size(texture):
    if not texture.startswith('looks/'):
        return (64, 64)
    _, look_name, role = texture.split('/')
    image, _ = S.look_texture(S.LOOKS[look_name][role])
    return CATALOG[image]['size']


def is_feature(texture):
    return texture.startswith('looks/') and texture.split('/')[2] in S.FIT_ROLES


m = B.Map(textures=[f'looks/{k}' for k in S.LOOKS] + ['greybox/Emissive'], tex_size=tex_size, fit=is_feature)
LOOK = 'steel'


def look(name):
    global LOOK
    LOOK = name


def R(role):
    return f'looks/{LOOK}/{role}'


def G(x, h, y):
    return (x, h, -y)


def GP(x, y, h):
    return (x, h, -y)


def hullp(pts, tex, name, **kw):
    return m.hull([G(x, h, y) for x, y, h in pts], tex, name, scale=S.role_scale, **kw)


def prism(poly, h0, h1, tex, name, **kw):
    if h1 - h0 < 1e-4:
        return False
    return hullp([(x, y, h) for x, y in poly for h in (h0, h1)], tex, name, **kw)


def top_tex(top, side):
    return lambda n, c: top if n[1] > 0.5 else side


def bottom_tex(bottom, side):
    return lambda n, c: bottom if n[1] < -0.5 else side


# ================================================================================
# Plan data, prepared
# ================================================================================
ROOMS = {}
for key, name, poly, floor, lk in F.ROOMS:
    ROOMS[key] = dict(key=key, name=name, poly=P.ccw(poly), floor=floor, look=lk, parts=P.convex_parts(poly),
                      levels=[], stairs=[], blockers=[], hazards=[], bridges=[])


def overlap_area(pa, pb):
    return sum(P.area(P.ccw(P.intersect(a, b))) for a in P.convex_parts(pa) for b in P.convex_parts(pb) if P.intersect(a, b))


def owner(poly, h, lower):
    """The room a level belongs to: the most overlap among rooms below it (or above it, for pits)."""
    best, best_a = None, 0
    for key, r in ROOMS.items():
        if lower and not r['floor'] > h:
            continue
        if not lower and not r['floor'] <= h + 1e-6:
            continue
        a = overlap_area(poly, r['poly'])
        if a > best_a + 1e-6:
            best, best_a = key, a
    return best


for name, poly, h, kind in F.LEVELS:
    kind3 = 'deck' if name in F.DECKS or kind == 'upper' else kind
    lower = kind in ('pit', 'lower')
    key = owner(poly, h, lower)
    ROOMS[key]['levels'].append(dict(name=name, poly=P.ccw(poly), h=h, kind=kind3))
for name, poly, h0, h1, up in F.STAIRS:
    c = (sum(p[0] for p in poly) / 4, sum(p[1] for p in poly) / 4)
    # The room containing it whose floor is nearest the stair's range (the booth notch sits under Logistics).
    key = min((k for k, r in ROOMS.items() if P.inside(c, r['poly'])),
              key=lambda k: 0.0 if min(h0, h1) - 0.6 <= ROOMS[k]['floor'] <= max(h0, h1) + 0.01 else abs(ROOMS[k]['floor'] - min(h0, h1)))
    ROOMS[key]['stairs'].append(dict(name=name, poly=P.ccw(poly), lo=min(h0, h1), hi=max(h0, h1), up=up))
for room, name, poly in F.BLOCKERS:
    ROOMS[room]['blockers'].append(dict(name=name, poly=P.ccw(poly)))
for name, poly in F.HAZARDS:
    ROOMS[owner(poly, -99, True) or 'PR']['hazards'].append(dict(name=name, poly=P.ccw(poly)))
for name, poly, h in F.BRIDGES:
    ROOMS[owner(poly, h, False)]['bridges'].append(dict(name=name, poly=P.ccw(poly), h=h))


def level_floor(r, pt, decks=False):
    """The floor under a plan point inside room r: its levels (pits, platforms) and stairs; decks only if asked."""
    h = r['floor']
    for lv in r['levels']:
        if lv['kind'] == 'deck' and not decks:
            continue
        if P.inside(pt, lv['poly']):
            h = lv['h']
    for st in r['stairs']:
        if P.inside(pt, st['poly']):
            h = stair_height(st, pt)
    return h


def stair_height(st, pt):
    xs, ys = [p[0] for p in st['poly']], [p[1] for p in st['poly']]
    ux, uy = st['up']
    if ux:
        t = (pt[0] - min(xs)) / (max(xs) - min(xs))
        t = t if ux > 0 else 1 - t
    else:
        t = (pt[1] - min(ys)) / (max(ys) - min(ys))
        t = t if uy > 0 else 1 - t
    return st['lo'] + (st['hi'] - st['lo']) * max(0.0, min(1.0, t))


def lowest(r):
    return min([r['floor']] + [lv['h'] for lv in r['levels']] + [lv['h'] - 0.5 for lv in r['levels'] if lv['kind'] == 'pit'
                                                                  and any(P.overlap_1d(0, 1, 0, 1) for _ in [0])])


def room_bottom(r):
    lo = min([r['floor']] + [lv['h'] for lv in r['levels']] + [st['lo'] for st in r['stairs']])
    if r['hazards']:
        lo = min(lo, min(lv['h'] for lv in r['levels'] if lv['kind'] == 'pit') - 0.5)
    return lo - F.FLOOR_T


def ceiling_at(r, pt):
    c = F.CEILINGS[r['key']]
    if isinstance(c, (int, float)):
        return c
    for poly, h in c:
        if P.inside(pt, poly) or P.edge_dist(pt, poly) < 1e-6:
            return h
    return c[-1][1]


def ceiling_max(r):
    c = F.CEILINGS[r['key']]
    return c if isinstance(c, (int, float)) else max(h for _, h in c)


# Corridors, with their segment frames.
CORRS = []
for key, name, prof, path, heights, lk in F.CORRIDORS:
    CORRS.append(dict(key=key, name=name, prof=prof, path=path, heights=heights, look=lk))


def corr_section(prof):
    """(clear half width, clear height)."""
    if prof in ('P1', 'P2'):
        return S.PROFILES[prof]['segments'][0][0][0], S.CEIL_Y
    w, h = F.PROFILE_BOX[prof]
    return w / 2, h


def profile_section(prof):
    """The corridor's clear outline (v, h), convex: the main wall line carried down to the floor and up to the ceiling."""
    main = [sg for sg in S.PROFILES[prof]['segments'] if sg[2] != 'plinth']
    (xa, ya), (xb, yb), _ = main[0]
    x0 = xa + (0.0 - ya) * (xb - xa) / (yb - ya)
    right = [(x0, 0.0)] + [sg[1] for sg in main]
    return [(-x, y) for x, y in right] + [(x, y) for x, y in reversed(right)]


def in_any_room(pt, margin=0.0):
    return any(P.inside(pt, r['poly']) and P.edge_dist(pt, r['poly']) > margin for r in ROOMS.values())


# ================================================================================
# Floors, levels, stairs, ceilings
# ================================================================================
def build_floor(r):
    look(r['look'])
    org = GP(r['poly'][0][0], r['poly'][0][1], r['floor'])
    holes = []
    for lv in r['levels']:
        if lv['kind'] in ('pit', 'lower'):
            holes += P.convex_parts(lv['poly'])
    for name, shaft in F.LADDER_SHAFT.items():
        if overlap_area(shaft, r['poly']) > 1e-3:
            holes.append(P.ccw(shaft))
    # A flight that descends below the room floor (into a lower lane) needs the floor cut from under it.
    for st in r['stairs']:
        if st['lo'] < r['floor'] - 1e-6:
            holes.append(P.ccw(st['poly']))
    for part in P.subtract_all([list(p) for p in r['parts']], holes):
        prism(part, r['floor'] - F.FLOOR_T, r['floor'], top_tex(R('floor'), R('plinth')), f"{r['key']} floor",
              tally='floor', uv_origin=org)
    for lv in r['levels']:
        if lv['kind'] in ('pit', 'lower'):
            sub = [h['poly'] for h in r['hazards'] if overlap_area(h['poly'], lv['poly']) > 1e-3]
            for part in P.subtract_all(P.convex_parts(lv['poly']), sub):
                prism(part, lv['h'] - F.FLOOR_T, lv['h'], top_tex(R('floor'), R('plinth')), f"{r['key']} {lv['name']} floor",
                      tally='floor', uv_origin=org)
            if lv['kind'] == 'pit':
                pit_walls(r, lv['poly'], lv['h'] - F.FLOOR_T, r['floor'], f"{r['key']} {lv['name']} wall")
        elif lv['kind'] == 'deck':
            for part in P.convex_parts(lv['poly']):
                prism(part, lv['h'] - F.DECK_T, lv['h'], top_tex(R('floor'), R('frame')), f"{r['key']} {lv['name']} deck",
                      tally='deck', uv_origin=org)
        elif lv['kind'] == 'feature':
            for part in P.convex_parts(lv['poly']):
                prism(part, r['floor'], lv['h'], top_tex(R('grate'), R('frame')), f"{r['key']} {lv['name']}", tally='floor')
        else:  # a solid platform, from the floor up
            for part in P.convex_parts(lv['poly']):
                prism(part, r['floor'] - F.FLOOR_T, lv['h'], top_tex(R('floor'), R('plinth')), f"{r['key']} {lv['name']}",
                      tally='platform', uv_origin=org)
    for hz in r['hazards']:
        pit = next(lv for lv in r['levels'] if lv['kind'] == 'pit' and overlap_area(hz['poly'], lv['poly']) > 1e-3)
        bottom = pit['h'] - 0.5
        for part in P.convex_parts(hz['poly']):
            prism(part, bottom - F.FLOOR_T, bottom, top_tex(R('coolant'), R('plinth')), f"{r['key']} {hz['name']}", tally='floor')
        pit_walls(r, hz['poly'], bottom - F.FLOOR_T, pit['h'], f"{r['key']} {hz['name']} wall", within=pit['poly'])
    for br in r['bridges']:
        for part in P.convex_parts(br['poly']):
            prism(part, br['h'] - 0.5, br['h'], top_tex(R('grate'), R('frame')), f"{r['key']} {br['name']}", tally='deck')
        xs, ys = [p[0] for p in br['poly']], [p[1] for p in br['poly']]
        for y in (min(ys) + 0.05, max(ys) - 0.05):
            rail(min(xs), y, max(xs), y, br['h'], br['h'], f"{r['key']} bridge rail")


def pit_walls(r, poly, h0, h1, name, within=None):
    """Walls round a sunken area, along its edges that are not the room's own walls, standing under the floor around it."""
    look(r['look'])
    boundary = within or r['poly']
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if P.edge_dist(mid, boundary) < 0.05:
            continue
        wall_piece(a, b, h0, h1, 'out', R('plinth'), R('plinth'), name, openings=wall_openings(a, b, 'pit'))


def build_stairs(r):
    look(r['look'])
    for st in r['stairs']:
        n = int(round((st['hi'] - st['lo']) / F.RISER))
        xs, ys = [p[0] for p in st['poly']], [p[1] for p in st['poly']]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        ux, uy = st['up']
        base = min(st['lo'], r['floor']) - F.FLOOR_T      # solid down to the floor: no gap under a flight
        for k in range(n):
            t0, t1 = k / n, (k + 1) / n
            if ux > 0:
                box = (x0 + (x1 - x0) * t0, x0 + (x1 - x0) * t1, y0, y1)
            elif ux < 0:
                box = (x1 - (x1 - x0) * t1, x1 - (x1 - x0) * t0, y0, y1)
            elif uy > 0:
                box = (x0, x1, y0 + (y1 - y0) * t0, y0 + (y1 - y0) * t1)
            else:
                box = (x0, x1, y1 - (y1 - y0) * t1, y1 - (y1 - y0) * t0)
            top = st['lo'] + (k + 1) * F.RISER
            prism([(box[0], box[2]), (box[1], box[2]), (box[1], box[3]), (box[0], box[3])], base, top,
                  top_tex(R('floor'), R('riser')), f"{r['key']} {st['name']} step {k}", tally='stair')


def build_ceiling(r):
    look(r['look'])
    above = [o['poly'] for o in ROOMS.values() if o is not r and o['floor'] > r['floor'] + 1e-6
             and overlap_area(o['poly'], r['poly']) > 1e-3]
    holes = []
    for poly in above:
        holes += P.convex_parts(poly)
    c = F.CEILINGS[r['key']]
    regions = [(None, c)] if isinstance(c, (int, float)) else c
    for part in P.subtract_all([list(p) for p in r['parts']], holes):
        for region, h in regions:
            piece = part if region is None else P.intersect(part, P.ccw(region))
            if piece and P.area(P.ccw(piece)) > P.AREA_EPS:
                prism(piece, h, h + F.CEIL_T, bottom_tex(R('ceiling'), R('wall')), f"{r['key']} ceiling", tally='ceiling')
    # Where two ceiling heights meet inside a room, a bulkhead closes the gap.
    if not isinstance(c, (int, float)):
        for (pa, ha), (pb, hb) in [(x, y) for i, x in enumerate(c) for y in c[i + 1:]]:
            ea = list(zip(P.ccw(pa), P.ccw(pa)[1:] + P.ccw(pa)[:1]))
            eb = list(zip(P.ccw(pb), P.ccw(pb)[1:] + P.ccw(pb)[:1]))
            for a, b in ea:
                for cc, dd in eb:
                    shared = collinear_overlap(a, b, cc, dd)
                    if shared:
                        s0, s1 = shared
                        L = math.dist(a, b)
                        pa0 = (a[0] + (b[0] - a[0]) * s0 / L, a[1] + (b[1] - a[1]) * s0 / L)
                        pa1 = (a[0] + (b[0] - a[0]) * s1 / L, a[1] + (b[1] - a[1]) * s1 / L)
                        mid = ((pa0[0] + pa1[0]) / 2, (pa0[1] + pa1[1]) / 2)
                        if P.inside(mid, r['poly']) and P.edge_dist(mid, r['poly']) > 0.05:
                            wall_piece(pa0, pa1, min(ha, hb), max(ha, hb) + F.CEIL_T, 'centre', R('wall'), R('wall'),
                                       f"{r['key']} ceiling bulkhead")


def collinear_overlap(a, b, c, d):
    """Overlap of segment c-d along a-b, as distances from a, when the two are collinear."""
    L = math.dist(a, b)
    if L < 1e-9:
        return None
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    for p in (c, d):
        if abs((p[0] - a[0]) * uy - (p[1] - a[1]) * ux) > 1e-6:
            return None
    tc = (c[0] - a[0]) * ux + (c[1] - a[1]) * uy
    td = (d[0] - a[0]) * ux + (d[1] - a[1]) * uy
    return P.overlap_1d(0, L, tc, td)


# ================================================================================
# Walls, with openings
# ================================================================================
def door_floor(pt, normal):
    """The floor height a door stands on: the higher floor either side of the wall at pt."""
    hs = []
    for sgn in (1, -1):
        q = (pt[0] + normal[0] * 0.45 * sgn, pt[1] + normal[1] * 0.45 * sgn)
        for r in ROOMS.values():
            if P.inside(q, r['poly']):
                hs.append(level_floor(r, q))
    return max(hs) if hs else 0.0


def wall_openings(a, b, owner_kind):
    """Openings (convex polygons in wall coordinates (s, h)) along the wall line a-b."""
    L = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    normal = (uy, -ux)
    out = []
    door_used = set()
    # Corridor crossings.
    for c in CORRS:
        for (p, hp), (q, hq) in zip(zip(c['path'], c['heights']), zip(c['path'][1:], c['heights'][1:])):
            hit = seg_intersection(a, b, p, q)
            if hit is None:
                continue
            s, t = hit
            if s < -1e-6 or s > L + 1e-6:
                continue
            pt = (a[0] + ux * s, a[1] + uy * s)
            h = hp + (hq - hp) * t
            dx, dy = q[0] - p[0], q[1] - p[1]
            sin = abs(ux * dy - uy * dx) / math.hypot(dx, dy)
            if sin < 0.2:
                continue
            door = next((d for d in F.DOORS if math.dist(d[1], pt) < 0.6 and d[2] in F.DOOR_SIZE), None)
            if door:
                door_used.add(door[0])
                if door[0].startswith(F.SEALED):
                    continue
                w, hh = F.DOOR_SIZE[door[2]]
                out.append([(s - w / 2 / sin, h), (s + w / 2 / sin, h), (s + w / 2 / sin, h + hh), (s - w / 2 / sin, h + hh)])
            elif c['prof'] in ('P1', 'P2'):
                out.append([(s + v / sin, h + hh) for v, hh in profile_section(c['prof'])])
            else:
                hw, hh = corr_section(c['prof'])
                out.append([(s - hw / sin, h), (s + hw / sin, h), (s + hw / sin, h + hh), (s - hw / sin, h + hh)])
    # Doors and windows that are not corridor mouths.
    for name, pt, kind in F.DOORS:
        if name in door_used or name.startswith(F.SEALED) or kind not in F.DOOR_SIZE:
            continue
        if P.seg_dist(pt, a, b) > 0.1:
            continue
        s = (pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy
        w, hh = F.DOOR_SIZE[kind]
        h0 = door_floor(pt, normal)
        if kind == 'window':
            h0 += F.WINDOW_SILL
        out.append([(s - w / 2, h0), (s + w / 2, h0), (s + w / 2, h0 + hh), (s - w / 2, h0 + hh)])
    # Explicit openings.
    for oa, ob, bottom, top in F.OPENING_3D:
        ov = collinear_overlap(a, b, oa, ob)
        if not ov:
            continue
        mid = ((oa[0] + ob[0]) / 2, (oa[1] + ob[1]) / 2)
        h0 = bottom if bottom is not None else door_floor(mid, normal)
        h1 = top if (top is not None and bottom is not None) else h0 + (top if top is not None else F.DEFAULT_OPENING_H)
        out.append([(ov[0], h0), (ov[1], h0), (ov[1], h1), (ov[0], h1)])
    # The fan: stopped, so a crouch-through hole.
    fa, fb = F.FAN_HOLE['room_edge']
    ov = collinear_overlap(a, b, fa, fb)
    if ov:
        s = (F.FAN_HOLE['centre'] - a[0]) * ux if abs(ux) > 0.5 else (F.FAN_HOLE['centre'] - a[1]) * uy
        s = abs((F.FAN_HOLE['centre'] - a[0]) / ux) if abs(ux) > 0.5 else s
        rr = F.FAN['diameter'] / 2 / math.cos(math.pi / 8)   # the octagon encloses the fan: its flat bottom is the lip
        hc = F.FAN_HOLE['floor'] + F.FAN['hub_height']
        out.append([(s + rr * math.cos(k * math.pi / 4 + math.pi / 8), hc + rr * math.sin(k * math.pi / 4 + math.pi / 8))
                    for k in range(8)])
    return out


def seg_intersection(a, b, p, q):
    """(s along a-b in metres, t in 0..1 along p-q) where the lines cross within p-q, or None."""
    L = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    dx, dy = q[0] - p[0], q[1] - p[1]
    den = ux * dy - uy * dx
    if abs(den) < 1e-9:
        return None
    t = ((a[1] - p[1]) * ux - (a[0] - p[0]) * uy) / den
    if t < -1e-6 or t > 1 + 1e-6:
        return None
    s = (p[0] + dx * t - a[0]) * ux + (p[1] + dy * t - a[1]) * uy
    return s, max(0.0, min(1.0, t))


def wall_piece(a, b, h0, h1, side, tex_low, tex_high, name, openings=(), band=None, origin=None):
    """A wall along a-b from h0 to h1 with openings cut out. side: 'out' (right of a->b, i.e. outside a CCW room),
    'centre' (straddling the line) or 'in'. band: the height where tex_low gives way to tex_high."""
    L = math.dist(a, b)
    if L < 0.01 or h1 - h0 < 0.01:
        return
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = uy, -ux                       # right of a->b
    o0, o1 = {'out': (0.0, F.WALL_T), 'centre': (-F.WALL_T / 2, F.WALL_T / 2), 'in': (-F.WALL_T, 0.0)}[side]
    rect = [(0.0, h0), (L, h0), (L, h1), (0.0, h1)]
    bands = [(h0, h1, tex_high)]
    if band is not None and h0 < band < h1:
        bands = [(h0, band, tex_low), (band, h1, tex_high)]
    holes = []
    for op in openings:
        c = P.ccw(op)
        if P.intersect(rect, c):
            holes.append(c)
    org = origin or a
    for lo, hi, tex in bands:
        piece_rect = [(0.0, lo), (L, lo), (L, hi), (0.0, hi)]
        for part in P.subtract_all([piece_rect], holes):
            pts = []
            for s, h in part:
                x, y = a[0] + ux * s, a[1] + uy * s
                for off in (o0, o1):
                    pts.append((x + nx * off, y + ny * off, h))
            hullp(pts, tex, name, tally='wall', uv_origin=GP(org[0], org[1], h0))


def build_walls():
    """Every room edge: exterior (outward), shared (one centred wall per pair) or open (a riser and a bulkhead)."""
    pieces = []  # (room_key, a, b, other_key or None)
    for key, r in ROOMS.items():
        poly = r['poly']
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            L = math.dist(a, b)
            cuts = [(0.0, L, None)]
            for ok, o in ROOMS.items():
                if ok == key:
                    continue
                op = o['poly']
                for j in range(len(op)):
                    ov = collinear_overlap(a, b, op[j], op[(j + 1) % len(op)])
                    if ov:
                        new = []
                        for s0, s1, other in cuts:
                            if other is not None:
                                new.append((s0, s1, other))
                                continue
                            lo, hi = max(s0, ov[0]), min(s1, ov[1])
                            if hi - lo < 1e-6:
                                new.append((s0, s1, other))
                                continue
                            if lo - s0 > 1e-6:
                                new.append((s0, lo, None))
                            new.append((lo, hi, ok))
                            if s1 - hi > 1e-6:
                                new.append((hi, s1, None))
                        cuts = new
            for s0, s1, other in cuts:
                pa = (a[0] + (b[0] - a[0]) * s0 / L, a[1] + (b[1] - a[1]) * s0 / L)
                pb = (a[0] + (b[0] - a[0]) * s1 / L, a[1] + (b[1] - a[1]) * s1 / L)
                pieces.append((key, pa, pb, other))
    open_pairs = {frozenset(p) for p in F.OPEN_EDGES}
    for key, a, b, other in pieces:
        r = ROOMS[key]
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        inward = (-uy, ux)
        samples = [(a[0] + (b[0] - a[0]) * t + inward[0] * 0.3, a[1] + (b[1] - a[1]) * t + inward[1] * 0.3)
                   for t in (0.15, 0.5, 0.85)]
        floor_in = min(level_floor(r, q) for q in samples)
        ceil_in = max(ceiling_at(r, q) for q in samples)
        look(r['look'])
        if other is None:
            bottom, top = floor_in - F.FLOOR_T, ceil_in + F.CEIL_T
            # A room stacked above this wall's outside caps it (the booth notch under Logistics).
            for q in samples:
                qo = (q[0] - inward[0] * 0.6, q[1] - inward[1] * 0.6)
                for o in ROOMS.values():
                    if o is not r and P.inside(qo, o['poly']) and o['floor'] - F.FLOOR_T > bottom + 0.5:
                        top = min(top, o['floor'] - F.FLOOR_T)
            m.group(f'{key} walls')
            wall_piece(a, b, bottom, top, 'out', R('plinth'), R('wall'), f'{key} wall',
                       openings=wall_openings(a, b, 'room'), band=floor_in + S.PLINTH_H, origin=r['poly'][0])
            continue
        if key > other:
            continue  # shared pieces are built once, from the first key
        o = ROOMS[other]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        qo = (mid[0] - inward[0] * 0.3, mid[1] - inward[1] * 0.3)
        floor_o = level_floor(o, qo)
        ceil_o = ceiling_at(o, qo)
        name = f'{key}|{other} walls'
        m.group(name)
        if frozenset((key, other)) in open_pairs:
            hi_r, lo_f, hi_f = (r, floor_o, floor_in) if floor_in > floor_o else (o, floor_in, floor_o)
            side = 'in' if hi_r is r else 'out'
            look(hi_r['look'])
            wall_piece(a, b, lo_f - F.FLOOR_T, hi_f - F.FLOOR_T, side, R('plinth'), R('plinth'), f'{key}|{other} edge')
            if abs(ceil_in - ceil_o) > 1e-6:
                wall_piece(a, b, min(ceil_in, ceil_o), max(ceil_in, ceil_o) + F.CEIL_T, 'centre', R('wall'), R('wall'),
                           f'{key}|{other} bulkhead')
            continue
        bottom = min(floor_in, floor_o) - F.FLOOR_T
        top = max(ceil_in, ceil_o) + F.CEIL_T
        wall_piece(a, b, bottom, top, 'centre', R('plinth'), R('wall'), f'{key}|{other} wall',
                   openings=wall_openings(a, b, 'shared'), band=min(floor_in, floor_o) + S.PLINTH_H, origin=r['poly'][0])
    m.ungroup()


# ================================================================================
# Blockers, rails, ladders
# ================================================================================
def blocker_height(name):
    for kw, h in F.BLOCKER_H:
        if kw in name:
            return h
    return 1.0


def rail(x0, y0, x1, y1, h0, h1, name):
    """An open rail: posts every 2 m and a top rail."""
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 0.2:
        return
    k = max(1, int(L // 2))
    for j in range(k + 1):
        t = j / k
        px, py, ph = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, h0 + (h1 - h0) * t
        prism([(px - 0.05, py - 0.05), (px + 0.05, py - 0.05), (px + 0.05, py + 0.05), (px - 0.05, py + 0.05)],
              ph, ph + 1.05, R('frame'), f'{name} post', tally='rail')
    nx, ny = -(y1 - y0) / L * 0.05, (x1 - x0) / L * 0.05
    hullp([(x0 + nx * s, y0 + ny * s, h0 + dh) for s in (-1, 1) for dh in (1.0, 1.1)]
          + [(x1 + nx * s, y1 + ny * s, h1 + dh) for s in (-1, 1) for dh in (1.0, 1.1)], R('frame'), f'{name} top', tally='rail')


def build_blockers(r):
    look(r['look'])
    bottom = room_bottom(r)
    for bl in r['blockers']:
        poly, name = bl['poly'], bl['name']
        c = (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
        base = level_floor(r, c)
        h = blocker_height(name)
        top = ceiling_at(r, c) if h == 'ceiling' else base + h
        tag = f"{r['key']} {name}"
        if name in F.ENTERABLE:
            # A fenced cage with its gate open (G-01): thin fence walls, a gap at the gate.
            gate = next(d for d in F.DOORS if d[0].startswith('Cage gate'))[1]
            n = len(poly)
            for i in range(n):
                a, b = poly[i], poly[(i + 1) % n]
                ops = []
                if P.seg_dist(gate, a, b) < 0.1:
                    L = math.dist(a, b)
                    s = ((gate[0] - a[0]) * (b[0] - a[0]) + (gate[1] - a[1]) * (b[1] - a[1])) / L
                    ops.append([(s - 0.7, base), (s + 0.7, base), (s + 0.7, base + 2.4), (s - 0.7, base + 2.4)])
                if P.edge_dist(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), r['poly']) < 0.05:
                    continue      # the room's own wall
                wall_piece(a, b, base, top, 'in', R('frame'), R('frame'), tag, openings=ops)
            continue
        if 'burst' in name or 'quarantine' in name or 'container' in name:
            tex = top_tex(R('machine_top'), R('door'))
        else:
            tex = top_tex(R('machine_top'), R('machine_body'))
        prism(poly, bottom, top, tex, tag, tally='blocker')
        if 'riser turning' in name:
            # The pipe turns into the wall at 2.3-2.7 m.
            east = 'east' in name
            x_wall = max(p[0] for p in r['poly']) if east else min(p[0] for p in r['poly'])
            x0 = c[0] if east else x_wall
            x1 = x_wall if east else c[0]
            prism([(x0, c[1] - 0.3), (x1, c[1] - 0.3), (x1, c[1] + 0.3), (x0, c[1] + 0.3)], base + 2.3, base + 2.9,
                  R('pipe'), f'{tag} arm', tally='blocker')
    for name, poly, clear in F.CROUCH:
        if overlap_area(poly, r['poly']) > 1e-3 and 'grill' not in name:
            base = level_floor(r, (sum(p[0] for p in poly) / 4, sum(p[1] for p in poly) / 4))
            prism(P.ccw(poly), base + clear, base + clear + 1.2, R('pipe'), f"{r['key']} {name}", tally='blocker')
    for name, (x, y), rad, kind in F.MOVING:
        if kind == 'piston' and P.inside((x, y), r['poly']):
            base = level_floor(r, (x, y))
            octo = [(x + rad * 0.6 * math.cos(k * math.pi / 4 + math.pi / 8), y + rad * 0.6 * math.sin(k * math.pi / 4 + math.pi / 8))
                    for k in range(8)]
            prism(octo, base + 3.0, ceiling_at(r, (x, y)), R('pipe'), f"{r['key']} piston", tally='blocker')


def ladder_entities():
    for name, (x, y), h0, h1 in F.LADDERS:
        if name not in F.LADDER_FACING:
            continue
        fx, fy = F.LADDER_FACING[name]
        lo, hi = min(h0, h1), max(h0, h1)
        climber = (x - fx * 0.45, y - fy * 0.45)
        key = min((k for k, r in ROOMS.items() if P.inside(climber, r['poly'])), key=lambda k: abs(ROOMS[k]['floor'] - lo))
        if name in F.LADDER_SHAFT:
            shaft_walls(name, F.LADDER_SHAFT[name], lo, hi, key)
        o = B.to_map(G(x, lo, y))
        m.entity('rb_ladder', {'origin': ' '.join(B._fmt(v) for v in o), 'top': B._fmt(hi), 'facing': f'{fx} {fy}',
                               'label': name}, group=f'{key} {ROOMS[key]["name"]}')


def shaft_walls(name, rect, lo, hi, key):
    """A ladder shaft from a crawl up through a floor: three walls and a lintel over the crawl mouth."""
    look(ROOMS[key]['look'])
    xs, ys = [p[0] for p in rect], [p[1] for p in rect]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    t = 0.25
    m.group(f'{key} {ROOMS[key]["name"]}')
    prism([(x0 - t, y1), (x1 + t, y1), (x1 + t, y1 + t), (x0 - t, y1 + t)], lo - F.FLOOR_T, hi, R('wall'), f'{name} shaft', tally='shaft')
    prism([(x0 - t, y0), (x0, y0), (x0, y1), (x0 - t, y1)], lo - F.FLOOR_T, hi, R('wall'), f'{name} shaft', tally='shaft')
    prism([(x1, y0), (x1 + t, y0), (x1 + t, y1), (x1, y1)], lo - F.FLOOR_T, hi, R('wall'), f'{name} shaft', tally='shaft')
    crawl_top = lo + F.PROFILE_BOX['crawl'][1]
    prism([(x0 - t, y0 - t), (x1 + t, y0 - t), (x1 + t, y0), (x0 - t, y0)], crawl_top, hi, R('wall'), f'{name} shaft', tally='shaft')
    prism([(x0, y0 - t), (x1, y0 - t), (x1, y1), (x0, y1)], lo - F.FLOOR_T, lo, top_tex(R('floor'), R('plinth')),
          f'{name} shaft floor', tally='shaft')
    m.ungroup()


# ================================================================================
# Corridors
# ================================================================================
def outside_intervals(p, q):
    """Parameter intervals of p-q (0..1) that lie outside every room."""
    L = math.dist(p, q)
    n = max(4, int(L / 0.1))
    ts = [k / n for k in range(n + 1)]
    flags = []
    for t in ts:
        pt = (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
        flags.append(not any(P.inside(pt, r['poly']) and P.edge_dist(pt, r['poly']) > 1e-6 for r in ROOMS.values()))
    out, start = [], None
    for t, f in zip(ts, flags):
        if f and start is None:
            start = t
        if not f and start is not None:
            out.append((start, t))
            start = None
    if start is not None:
        out.append((start, 1.0))
    return [(a, b) for a, b in out if (b - a) * L > 0.05]


def build_corridor(c):
    look(c['look'])
    prof, path, heights = c['prof'], c['path'], c['heights']
    n = len(path)
    m.group(f"{c['key']} {c['name']}")
    stacked = prof in ('crawl', 'catwalk')
    dirs, lens = [], []
    for i in range(n - 1):
        dx, dy = path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]
        L = math.hypot(dx, dy)
        dirs.append((dx / L, dy / L)); lens.append(L)
    turn = [0.0] * n
    for i in range(1, n - 1):
        a, b = dirs[i - 1], dirs[i]
        turn[i] = math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1])
    s0 = [0.0]
    for L in lens:
        s0.append(s0[-1] + L)
    hw_clear, h_clear = corr_section(prof)
    W = S.SHELL_X if prof in ('P1', 'P2') else hw_clear + (0.25 if prof == 'crawl' else F.WALL_T)
    for i in range(n - 1):
        d = dirs[i]
        nl = (-d[1], d[0])
        a = path[i]
        ha, hb = heights[i], heights[i + 1]
        L = lens[i]
        ivals = [(0.0, 1.0)] if stacked else outside_intervals(path[i], path[i + 1])
        for t0, t1 in ivals:
            mitre_in = math.tan(turn[i] / 2) if t0 < 1e-6 and i > 0 else 0.0
            mitre_out = math.tan(turn[i + 1] / 2) if t1 > 1 - 1e-6 and i + 1 < n - 1 else 0.0

            def pt(u, v, h):
                x = a[0] + d[0] * u + nl[0] * v
                y = a[1] + d[1] * u + nl[1] * v
                return (x, y, ha + (hb - ha) * u / L + h)

            u0, u1 = t0 * L, t1 * L

            def piece(poly, tex, name, span=None, **kw):
                ua_, ub_, mi, mo = span if span else (u0, u1, mitre_in, mitre_out)
                pts = []
                for v, h in poly:
                    pts += [pt(ua_ + v * mi, v, h), pt(ub_ - v * mo, v, h)]
                hullp(pts, tex, name, **kw)

            # Rooms that open off the corridor's SIDE (the pipe bay): cut that side's wall below the opening top.
            cuts = []
            for oa, ob, bottom, otop in F.OPENING_3D:
                ex, ey = ob[0] - oa[0], ob[1] - oa[1]
                if abs(ex * d[1] - ey * d[0]) > 1e-6 * math.hypot(ex, ey):
                    continue
                v = (oa[0] - a[0]) * nl[0] + (oa[1] - a[1]) * nl[1]
                if not hw_clear - 0.3 <= abs(v) <= W + 0.3:
                    continue
                pa = (oa[0] - a[0]) * d[0] + (oa[1] - a[1]) * d[1]
                pb = (ob[0] - a[0]) * d[0] + (ob[1] - a[1]) * d[1]
                lo_u, hi_u = max(min(pa, pb), u0), min(max(pa, pb), u1)
                if hi_u - lo_u > 1e-6:
                    top_rel = (otop - bottom) if (otop is not None and bottom is not None) else (otop if otop is not None else F.DEFAULT_OPENING_H)
                    cuts.append((lo_u, hi_u, 1 if v > 0 else -1, top_rel))
            bounds = sorted({u0, u1} | {x for cu in cuts for x in cu[:2]})
            spans = []
            for sa, sb in zip(bounds, bounds[1:]):
                active = {cu[2]: cu[3] for cu in cuts if cu[0] <= sa + 1e-6 and cu[1] >= sb - 1e-6}
                spans.append((sa, sb, mitre_in if abs(sa - u0) < 1e-9 else 0.0, mitre_out if abs(sb - u1) < 1e-9 else 0.0, active))
            if cuts:
                c.setdefault('cuts', []).extend((s0[i] + lo_, s0[i] + hi_) for lo_, hi_, _, _ in cuts)

            def side_wall(poly, side, tex, name, **kw):
                for sa, sb, mi, mo, active in spans:
                    q = poly
                    if side in active:
                        q = P.clip(P.ccw(poly), 0, -1, -active[side])
                        if not q or P.area(P.ccw(q)) < P.AREA_EPS:
                            continue
                    piece(q, tex, name, span=(sa, sb, mi, mo), **kw)

            run_u = GP(d[0], d[1], 0.0)
            run_u = (d[0], 0.0, -d[1])
            flight = abs(hb - ha) > 1e-6
            org = GP(*pt(u0, -1.0, 0.0))
            if prof == 'catwalk':
                inside_room = in_any_room(((a[0] + d[0] * (u0 + u1) / 2), (a[1] + d[1] * (u0 + u1) / 2)), 0.05)
                piece([(-hw_clear, -0.25), (hw_clear, -0.25), (hw_clear, 0.0), (-hw_clear, 0.0)],
                      top_tex(R('grate'), R('frame')), f"{c['key']} deck", tally='catwalk')
                if inside_room:
                    for side in (1, -1):
                        v = side * (hw_clear - 0.05)
                        # Mitred like the walls: the inner rail stops short of a bend, the outer one runs on to meet.
                        p0, p1 = pt(u0 + v * mitre_in, v, 0.0), pt(u1 - v * mitre_out, v, 0.0)
                        rail(p0[0], p0[1], p1[0], p1[1], p0[2], p1[2], f"{c['key']} rail")
                    continue
            if not flight:
                piece([(-W, -F.FLOOR_T), (W, -F.FLOOR_T), (W, 0.0), (-W, 0.0)], top_tex(R('floor'), R('plinth')),
                      f"{c['key']} floor", tally='corridor', uv_origin=org, uv_u=run_u)
            else:
                risers = int(round(abs(hb - ha) / F.RISER))
                lo = min(ha, hb)
                for k in range(risers):
                    if hb > ha:
                        ua, ub, top = u0 + (u1 - u0) * k / risers, u0 + (u1 - u0) * (k + 1) / risers, ha + (k + 1) * F.RISER
                    else:
                        ua, ub, top = u0 + (u1 - u0) * k / risers, u0 + (u1 - u0) * (k + 1) / risers, ha - k * F.RISER
                    corners = []
                    for u in (ua, ub):
                        for v in (-W, W):
                            x = a[0] + d[0] * u + nl[0] * v
                            y = a[1] + d[1] * u + nl[1] * v
                            corners += [(x, y, lo - F.FLOOR_T), (x, y, top)]
                    hullp(corners, top_tex(R('floor'), R('riser')), f"{c['key']} step {k}", tally='stair')
            top_h = max(0.0, abs(hb - ha)) if flight else 0.0
            if prof in ('P1', 'P2'):
                for side in (1, -1):
                    for (xa, ya), (xb, yb), role in S.PROFILES[prof]['segments']:
                        poly = [(side * xa, ya), (side * W, ya), (side * W, yb), (side * xb, yb)]
                        side_wall(poly, side, R(role), f"{c['key']} {role}", tally='corridor', uv_origin=org)
                piece([(-W, S.CEIL_Y), (W, S.CEIL_Y), (W, S.SHELL_TOP), (-W, S.SHELL_TOP)], R('ceiling'),
                      f"{c['key']} ceiling", tally='corridor', uv_origin=org, uv_u=run_u)
            else:
                # Box section. On a flight the walls and ceiling rise with the steps (the frame slopes them).
                wt = W - hw_clear
                lift = abs(hb - ha) if (flight and hb < ha) else 0.0
                for side in (1, -1):
                    side_wall([(side * hw_clear, -F.FLOOR_T - lift), (side * W, -F.FLOOR_T - lift), (side * W, h_clear + wt),
                               (side * hw_clear, h_clear + wt)], side, R('wall'), f"{c['key']} wall", tally='corridor', uv_origin=org)
                piece([(-W, h_clear), (W, h_clear), (W, h_clear + wt), (-W, h_clear + wt)], bottom_tex(R('ceiling'), R('wall')),
                      f"{c['key']} ceiling", tally='corridor', uv_origin=org, uv_u=run_u)
                if prof == 'D2':
                    k = 1
                    while k * F.DUCT_RIB_PITCH < (u1 - u0) - 0.3:
                        u = u0 + k * F.DUCT_RIB_PITCH
                        for poly in ([(hw_clear - 0.06, 0.0), (hw_clear, 0.0), (hw_clear, h_clear), (hw_clear - 0.06, h_clear)],
                                     [(-hw_clear, 0.0), (-hw_clear + 0.06, 0.0), (-hw_clear + 0.06, h_clear), (-hw_clear, h_clear)],
                                     [(-hw_clear, h_clear - 0.06), (hw_clear, h_clear - 0.06), (hw_clear, h_clear), (-hw_clear, h_clear)]):
                            hullp([pt(uu, v, h) for v, h in poly for uu in (u - 0.05, u + 0.05)], R('frame'),
                                  f"{c['key']} rib", tally='rib')
                        k += 1
    # P1/P2 ribs on a 4 m beat, clear of bends and of room interiors.
    if prof in ('P1', 'P2'):
        main = [sg for sg in S.PROFILES[prof]['segments'] if sg[2] != 'plinth']
        foot_x = main[0][0][0] - S.RIB_D
        plinth_top = main[0][0][1]
        ch = S.ceil_half(prof)
        st = 2.0
        while st < s0[-1] - 0.5:
            i = max(j for j in range(n - 1) if s0[j] <= st + 1e-9)
            u = st - s0[i]
            near_bend = any(abs(st - s0[j]) < 2.2 for j in range(1, n - 1))
            d = dirs[i]
            nl = (-d[1], d[0])
            a = path[i]
            cpt = (a[0] + d[0] * u, a[1] + d[1] * u)
            in_cut = any(lo_ - 0.5 <= st <= hi_ + 0.5 for lo_, hi_ in c.get('cuts', []))
            if not near_bend and not in_cut and not in_any_room(cpt, 0.05) and abs(heights[i] - heights[i + 1]) < 1e-6:
                h = heights[i]

                def rp(uu, v, hh):
                    return (a[0] + d[0] * uu + nl[0] * v, a[1] + d[1] * uu + nl[1] * v, h + hh)
                ur = (u - S.RIB_DEPTH / 2, u + S.RIB_DEPTH / 2)
                for side in (1, -1):
                    hullp([rp(uu, v, hh) for v, hh in [(side * foot_x, -0.25), (side * S.SHELL_X, -0.25), (side * S.SHELL_X, plinth_top),
                                                       (side * foot_x, plinth_top)] for uu in ur], R('rib'), f"{c['key']} rib", tally='rib')
                    for (xa, ya), (xb, yb), role in main:
                        hullp([rp(uu, v, hh) for v, hh in [(side * (xa - S.RIB_D), ya), (side * xa, ya), (side * xb, yb),
                                                           (side * (xb - S.RIB_D), yb)] for uu in ur], R('rib'), f"{c['key']} rib", tally='rib')
                hullp([rp(uu, v, hh) for v, hh in [(-ch, S.CEIL_Y - S.RIB_D), (ch, S.CEIL_Y - S.RIB_D), (ch, S.CEIL_Y), (-ch, S.CEIL_Y)]
                       for uu in ur], R('rib'), f"{c['key']} rib beam", tally='rib')
            st += 4.0
    m.ungroup()


# ================================================================================
# Sealed doors, lights, markers
# ================================================================================
def sealed_doors():
    for name, pt, kind in F.DOORS:
        if not name.startswith(F.SEALED) or name.startswith(('Cage gate', 'Lift gate')):
            continue
        key = next((k for k, r in ROOMS.items() if P.edge_dist(pt, r['poly']) < 0.1), None)
        if key is None:
            continue
        r = ROOMS[key]
        look(r['look'])
        poly = r['poly']
        a, b = min(zip(poly, poly[1:] + poly[:1]), key=lambda e: P.seg_dist(pt, e[0], e[1]))
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        w, hh = F.DOOR_SIZE[kind]
        if 'roll door' in name:
            w, hh = 4.0, 3.5
        inward = (-uy, ux)
        fl = level_floor(r, (pt[0] + inward[0] * 0.5, pt[1] + inward[1] * 0.5))
        m.group(f'{key} {r["name"]}')
        prism([(pt[0] - ux * w / 2, pt[1] - uy * w / 2), (pt[0] + ux * w / 2, pt[1] + uy * w / 2),
               (pt[0] + ux * w / 2 + inward[0] * 0.08, pt[1] + uy * w / 2 + inward[1] * 0.08),
               (pt[0] - ux * w / 2 + inward[0] * 0.08, pt[1] - uy * w / 2 + inward[1] * 0.08)], fl, fl + hh,
              lambda n_, c_: R('door'), f'{name} (sealed)', tally='door')
        m.ungroup()


def light_entity(x, y, h, energy, rng, shadow, group):
    o = B.to_map(G(x, h, y))
    m.entity('rb_light', {'origin': ' '.join(B._fmt(v) for v in o), 'energy': B._fmt(energy), 'range': B._fmt(rng),
                          'shadow': 1 if shadow else 0}, group=group)
    return 1


def los_clear(a, b, r, tall):
    """Plan line of sight inside room r, not through a tall blocker."""
    for t in (0.2, 0.4, 0.6, 0.8):
        q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        if not P.inside(q, r['poly']):
            return False
    for poly in tall:
        if P.inside(a, poly) or P.inside(b, poly):
            return False
        for e0, e1 in zip(poly, poly[1:] + poly[:1]):
            if seg_cross(a, b, e0, e1):
                return False
    return True


def seg_cross(a, b, c, d):
    def o(p, q, r_):
        return (q[0] - p[0]) * (r_[1] - p[1]) - (q[1] - p[1]) * (r_[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0


def room_lights(r):
    """Cover every walkable metre of a room with light: sample the floor (and decks, and the space under decks),
    then place lights greedily where they reach the most unlit samples in line of sight (the light floor rule)."""
    spacing, energy, rng, shadow = F.LIGHT_ROOM
    reach = F.LIGHT_REACH
    blockers = [b['poly'] for b in r['blockers'] if b['name'] not in F.ENTERABLE]
    tall = [b['poly'] for b in r['blockers'] if b['name'] not in F.ENTERABLE
            and (blocker_height(b['name']) == 'ceiling' or blocker_height(b['name']) >= 1.5)]
    xs, ys = [p[0] for p in r['poly']], [p[1] for p in r['poly']]
    samples = []
    x = math.floor(min(xs)) + 0.5
    while x < max(xs):
        y = math.floor(min(ys)) + 0.5
        while y < max(ys):
            pt = (x, y)
            if P.inside(pt, r['poly']) and P.edge_dist(pt, r['poly']) > 0.3 and not any(P.inside(pt, b) for b in blockers):
                fl = level_floor(r, pt)
                ceil = ceiling_at(r, pt)
                decks = [lv for lv in r['levels'] if lv['kind'] == 'deck' and P.inside(pt, lv['poly'])]
                if decks:
                    dk = decks[0]['h']
                    samples.append((x, y, fl, 'floor', dk - F.DECK_T))
                    samples.append((x, y, dk, 'deck', ceil))
                else:
                    samples.append((x, y, fl, 'floor', ceil))
            y += 1.0
        x += 1.0
    cover = []
    for i, si in enumerate(samples):
        cov = set()
        for j, sj in enumerate(samples):
            if sj[3] != si[3] or abs(sj[2] - si[2]) > 2.0:
                continue
            if (sj[0] - si[0]) ** 2 + (sj[1] - si[1]) ** 2 > reach * reach:
                continue
            if i == j or los_clear((si[0], si[1]), (sj[0], sj[1]), r, tall):
                cov.add(j)
        cover.append(cov)
    uncovered = set(range(len(samples)))
    placed = []
    while uncovered:
        best = max(range(len(samples)), key=lambda i: len(cover[i] & uncovered))
        gain = cover[best] & uncovered
        if not gain:
            break
        placed.append(samples[best])
        uncovered -= gain
    out = []
    for x, y, fl, layer, top in placed:
        h = fl + min(3.6 if layer == 'floor' else 3.0, top - fl - 0.4)
        out.append((x, y, h))
    return out, energy, rng, shadow


def build_lights():
    count = 0
    for key, r in ROOMS.items():
        group = f'{key} {r["name"]}'
        lights, energy, rng, shadow = room_lights(r)
        for x, y, h in lights:
            count += light_entity(x, y, h, energy, rng, shadow, group)
    for c in CORRS:
        spacing, energy, rng, shadow = F.LIGHT_CORRIDOR[c['prof']]
        hw, hc = corr_section(c['prof'])
        group = f"{c['key']} {c['name']}"
        total = sum(math.dist(p, q) for p, q in zip(c['path'], c['path'][1:]))
        s = min(spacing / 2, total / 2)
        while s < total:
            acc = 0.0
            for (p, hp), (q, hq) in zip(zip(c['path'], c['heights']), zip(c['path'][1:], c['heights'][1:])):
                L = math.dist(p, q)
                if acc + L >= s:
                    t = (s - acc) / L
                    x, y, h = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, hp + (hq - hp) * t
                    break
                acc += L
            if c['prof'] == 'catwalk' or not in_any_room((x, y), 0.3):
                hh = 2.2 if c['prof'] == 'catwalk' else hc - 0.4
                count += light_entity(x, y, h + hh, energy, rng, shadow, group)
            s += spacing
    return count


def floor_candidates(pt):
    out = []
    for key, r in ROOMS.items():
        if P.inside(pt, r['poly']) or P.edge_dist(pt, r['poly']) < 0.05:
            out.append((level_floor(r, pt), 'room:' + key))
            for lv in r['levels']:
                if lv['kind'] == 'deck' and P.inside(pt, lv['poly']):
                    out.append((lv['h'], 'deck:' + lv['name']))
            for br in r['bridges']:
                if P.inside(pt, br['poly']):
                    out.append((br['h'], 'bridge'))
    for c in CORRS:
        hw, _ = corr_section(c['prof'])
        for (p, hp), (q, hq) in zip(zip(c['path'], c['heights']), zip(c['path'][1:], c['heights'][1:])):
            L = math.dist(p, q)
            t_raw = ((pt[0] - p[0]) * (q[0] - p[0]) + (pt[1] - p[1]) * (q[1] - p[1])) / (L * L)
            # Only segments the point projects onto: past a segment's end belongs to the next one.
            if -0.02 <= t_raw <= 1.02 and P.seg_dist(pt, p, q) <= hw + 0.05:
                t = max(0.0, min(1.0, t_raw))
                out.append((hp + (hq - hp) * t, 'corr:' + c['prof'] + ':' + c['key']))
    return out


def route_heights(pts):
    """Heights and postures along a plan route: continuity picks between stacked floors; tags force them."""
    out, prev = [], 0.0
    for p in pts:
        xy = (p[0], p[1])
        tag = p[2] if len(p) > 2 else ''
        cands = floor_candidates(xy)
        if tag == 'lb' or tag == 'lt':
            ld = min(F.LADDERS, key=lambda l: math.dist(l[1], xy))
            h = min(ld[2], ld[3]) if tag == 'lb' else max(ld[2], ld[3])
        else:
            want = {'archive': 'deck:Archive', 'gantry': 'deck:Gantry', 'catwalk': 'corr:catwalk', 'crawl': 'corr:crawl'}.get(tag)
            pool = [c for c in cands if want and c[1].startswith(want)] or cands
            if not pool:
                raise SystemExit(f'route point {p} is off every floor')
            h = min(pool, key=lambda c: abs(c[0] - prev))[0]
        posture = 'crouch' if tag in ('crouch', 'crawl') else 'stand'
        if out and abs(h - prev) > 0.45:
            for name, lp, h0, h1 in F.LADDERS:
                if name in F.LADDER_FACING and min(math.dist(lp, xy), math.dist(lp, (out[-1][0], out[-1][1]))) < 1.8 \
                        and abs(min(h, prev) - min(h0, h1)) < 0.3 and abs(max(h, prev) - max(h0, h1)) < 0.3:
                    posture = 'climb'
        out.append((xy[0], xy[1], h, posture))
        prev = h
    return out


def route_markers():
    count = 0
    for name, pts in F.ROUTES.items():
        rname = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
        oneway = 1 if any(F.xy(p) == (10.8, 45.75) for p in pts) else 0
        for i, (x, y, h, posture) in enumerate(route_heights(pts)):
            o = B.to_map(G(x, h, y))
            m.entity('rb_route', {'origin': ' '.join(B._fmt(v) for v in o), 'route': rname, 'index': i, 'posture': posture,
                                  'oneway': oneway}, group='Markers')
            count += 1
    return count


# ================================================================================
# Build
# ================================================================================
for key, r in ROOMS.items():
    m.group(f'{key} {r["name"]}')
    build_floor(r)
    m.group(f'{key} {r["name"]}')
    build_stairs(r)
    build_ceiling(r)
    m.group(f'{key} {r["name"]}')
    build_blockers(r)
    m.ungroup()
build_walls()
for c in CORRS:
    build_corridor(c)
sealed_doors()
ladder_entities()
m.group('Markers')
m.box(-30.5, -30.25, -0.2, 0.0, 29.75, 30.0, 'clip', 'marker anchor', tally='misc')
m.ungroup()
lights = build_lights()
markers = route_markers()
if lights == 0:
    raise SystemExit('no lights written')
text = m.text('Freight access v2, G-01 greybox. Generated by tools/bootstrap-freight-v2.py from tools/freight_v2.py; '
              'now the editable source.')


def split_blocks(t):
    """Top-level { } blocks of a map file, with their text."""
    blocks, depth, start = [], 0, None
    for i, ch in enumerate(t):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                blocks.append(t[start:i + 1])
    return blocks


if ROOM_ARG:
    # Surgical: swap only this room's groups (and shared walls naming it) in the existing map.
    old = MAP.read_text(encoding='utf-8')
    new_blocks = split_blocks(text)
    old_blocks = split_blocks(old)

    def gname(b):
        mm = re.search(r'"_tb_name" "([^"]*)"', b)
        return mm.group(1) if mm else None

    def gid(b):
        mm = re.search(r'"_tb_id" "(\d+)"', b)
        return int(mm.group(1)) if mm else None

    def mine(name):
        return name is not None and (name.startswith(ROOM_ARG + ' ') or re.match(rf'^(\w+\|)?{ROOM_ARG}(\|\w+)? walls$', name)
                                     is not None and ROOM_ARG in name.split(' ')[0].split('|'))
    drop_ids = {gid(b) for b in old_blocks if mine(gname(b))}
    keep = [b for b in old_blocks if not mine(gname(b)) and not any(f'"_tb_group" "{i}"' in b for i in drop_ids)]
    next_id = max([gid(b) or 0 for b in old_blocks] + [0]) + 1
    add, remap = [], {}
    for b in new_blocks:
        if mine(gname(b)):
            remap[gid(b)] = next_id
            add.append(re.sub(r'"_tb_id" "\d+"', f'"_tb_id" "{next_id}"', b))
            next_id += 1
    for b in new_blocks:
        mm = re.search(r'"_tb_group" "(\d+)"', b)
        if mm and int(mm.group(1)) in remap:
            add.append(b.replace(f'"_tb_group" "{mm.group(1)}"', f'"_tb_group" "{remap[int(mm.group(1))]}"'))
    if not add:
        raise SystemExit(f'no groups named for room {ROOM_ARG}')
    header = old[:old.index('{')]
    MAP.write_text(header + '\n'.join(keep + add) + '\n', encoding='utf-8')
    print(f'FREIGHT_V2_MAP: room {ROOM_ARG}: replaced {len(drop_ids)} groups with {len(remap)} -> {MAP.relative_to(ROOT)}')
else:
    MAP.parent.mkdir(parents=True, exist_ok=True)
    MAP.write_text(text, encoding='utf-8')
    print(f'FREIGHT_V2_MAP: {m.count} brushes, {lights} lights, {markers} route markers, {len(m.groups)} groups '
          f'-> {MAP.relative_to(ROOT)}')
    print('  ' + ', '.join(f'{k} {v}' for k, v in sorted(m.tally.items())))
