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


def corr_shell(prof):
    """(half width, top above the floor) of a corridor's OUTER shell: what it fills where it passes through a wall."""
    if prof in ('P1', 'P2'):
        return S.SHELL_X, S.SHELL_TOP
    hw, h = corr_section(prof)
    wt = 0.25 if prof == 'crawl' else F.WALL_T
    return hw + wt, h + wt


def door_at(pt):
    """The door (not sealed) standing where a corridor meets a room, if any."""
    d = next((d for d in F.DOORS if math.dist(d[1], pt) < 0.6 and d[2] in F.DOOR_SIZE), None)
    return d if d and not d[0].startswith(F.SEALED) else None


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
def shared_strips(r):
    """This room's own half of every wall it shares with another room (open edges have none): the strip a platform or
    ceiling must stop short of, or its edge face lies on the plane of the wall's end and the two flicker (the S1 landing)."""
    open_pairs = {frozenset(p_) for p_ in F.OPEN_EDGES}
    out = []
    poly = r['poly']
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        inward = (-uy, ux)
        for o in ROOMS.values():
            if o is r or frozenset((r['key'], o['key'])) in open_pairs:
                continue
            op = o['poly']
            for j in range(len(op)):
                ov = collinear_overlap(a, b, op[j], op[(j + 1) % len(op)])
                if ov and ov[1] - ov[0] > 1e-6:
                    p0 = (a[0] + ux * ov[0], a[1] + uy * ov[0])
                    p1 = (a[0] + ux * ov[1], a[1] + uy * ov[1])
                    h = F.WALL_T / 2
                    out.append(P.ccw([p0, p1, (p1[0] + inward[0] * h, p1[1] + inward[1] * h),
                                      (p0[0] + inward[0] * h, p0[1] + inward[1] * h)]))
    return out


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
            pit_walls(r, lv['poly'], lv['h'] - F.FLOOR_T, r['floor'] - F.FLOOR_T, f"{r['key']} {lv['name']} wall")
        elif lv['kind'] == 'deck':
            for part in P.convex_parts(lv['poly']):
                prism(part, lv['h'] - F.DECK_T, lv['h'], top_tex(R('floor'), R('frame')), f"{r['key']} {lv['name']} deck",
                      tally='deck', uv_origin=org)
        elif lv['kind'] == 'feature':
            for part in P.convex_parts(lv['poly']):
                prism(part, r['floor'], lv['h'], top_tex(R('grate'), R('frame')), f"{r['key']} {lv['name']}", tally='floor')
        else:  # a solid platform, from the floor up, stopping at the face of a wall it shares with another room
            for part in P.subtract_all(P.convex_parts(lv['poly']), shared_strips(r)):
                prism(part, r['floor'] - F.FLOOR_T, lv['h'], top_tex(R('floor'), R('plinth')), f"{r['key']} {lv['name']}",
                      tally='platform', uv_origin=org)
    for hz in r['hazards']:
        pit = next(lv for lv in r['levels'] if lv['kind'] == 'pit' and overlap_area(hz['poly'], lv['poly']) > 1e-3)
        bottom = pit['h'] - 0.5
        for part in P.convex_parts(hz['poly']):
            prism(part, bottom - F.FLOOR_T, bottom, top_tex(R('coolant'), R('plinth')), f"{r['key']} {hz['name']}", tally='floor')
        pit_walls(r, hz['poly'], bottom - F.FLOOR_T, pit['h'] - F.FLOOR_T, f"{r['key']} {hz['name']} wall")
    for br in r['bridges']:
        for part in P.convex_parts(br['poly']):
            prism(part, br['h'] - 0.5, br['h'], top_tex(R('grate'), R('frame')), f"{r['key']} {br['name']}", tally='deck')
        xs, ys = [p[0] for p in br['poly']], [p[1] for p in br['poly']]
        for y in (min(ys) + 0.05, max(ys) - 0.05):
            rail(min(xs), y, max(xs), y, br['h'], br['h'], f"{r['key']} bridge rail")


def pit_walls(r, poly, h0, h1, name):
    """Walls round a sunken area (a pit, a lower lane, a channel in a pit floor), along its edges that are not the
    room's own walls. They stand under the floor around it and stop at that floor's underside (h1): the floor slab
    finishes the step, so no wall face lies on the floor and flickers. A stair against an edge keeps its way down."""
    look(r['look'])
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if P.edge_dist(mid, r['poly']) < 0.05:
            continue
        cuts = wall_openings(a, b, 'pit')
        for st in r['stairs']:
            sp = st['poly']
            for j in range(len(sp)):
                ov = collinear_overlap(a, b, sp[j], sp[(j + 1) % len(sp)])
                if ov and ov[1] - ov[0] > 1e-6:
                    cuts.append([(ov[0], h0 - 1), (ov[1], h0 - 1), (ov[1], h1 + 1), (ov[0], h1 + 1)])
        wall_piece(a, b, h0, h1, 'out', R('plinth'), R('plinth'), name, openings=cuts)


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
    holes += shared_strips(r)     # the shared walls rise past the ceiling: it stops at their face, like a platform
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
                            wall_piece(pa0, pa1, min(ha, hb) + F.CEIL_T, max(ha, hb) + F.CEIL_T, 'centre', R('wall'), R('wall'),
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
def door_ceilings(pt, normal):
    """The ceiling heights either side of a wall at pt."""
    hs = []
    for sgn in (1, -1):
        q = (pt[0] + normal[0] * 0.45 * sgn, pt[1] + normal[1] * 0.45 * sgn)
        for r in ROOMS.values():
            if P.inside(q, r['poly']):
                hs.append(ceiling_at(r, q))
    return hs


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
                # The corridor's floor runs under the wall to the room face and is the threshold, so the hole starts
                # at its underside: no wall stub lies on the floor and flickers.
                w, hh = F.DOOR_SIZE[door[2]]
                b0 = h - F.FLOOR_T
                out.append([(s - w / 2 / sin, b0), (s + w / 2 / sin, b0), (s + w / 2 / sin, h + hh), (s - w / 2 / sin, h + hh)])
            else:
                # The junction rule: the corridor meets the room through its own profile. The wall is cut to the
                # corridor's outer shell and the corridor's pieces fill the wall's thickness up to the room face.
                W, top = corr_shell(c['prof'])
                b0 = h - F.FLOOR_T
                out.append([(s - W / sin, b0), (s + W / sin, b0), (s + W / sin, h + top), (s - W / sin, h + top)])
    # Doors and windows that are not corridor mouths.
    for name, pt, kind in F.DOORS:
        if name in door_used or name.startswith(F.SEALED) or kind not in F.DOOR_SIZE:
            continue
        if P.seg_dist(pt, a, b) > 0.1:
            continue
        s = (pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy
        w, hh = F.DOOR_SIZE[kind]
        h0 = door_floor(pt, normal)
        b0 = h0 - F.FLOOR_T if owner_kind == 'shared' and kind != 'window' else h0   # both floors run to the line
        top = h0 + hh
        if kind == 'window':
            h0 += F.WINDOW_SILL
            b0 = h0
            top = h0 + hh
        # A door as tall as the room beside it would put its lintel's underside on that ceiling's underside (they
        # flicker); the opening then runs up through the ceiling slab, and the ceiling meets the door flush.
        for c in door_ceilings(pt, normal):
            if abs(top - c) < 0.01:
                top = c + F.CEIL_T
        out.append([(s - w / 2, b0), (s + w / 2, b0), (s + w / 2, top), (s - w / 2, top)])
    # Explicit openings.
    for oa, ob, bottom, top in F.OPENING_3D:
        ov = collinear_overlap(a, b, oa, ob)
        if not ov:
            continue
        mid = ((oa[0] + ob[0]) / 2, (oa[1] + ob[1]) / 2)
        h0 = bottom if bottom is not None else door_floor(mid, normal)
        h1 = top if (top is not None and bottom is not None) else h0 + (top if top is not None else F.DEFAULT_OPENING_H)
        b0 = h0 - F.FLOOR_T if owner_kind == 'shared' and bottom is None else h0
        out.append([(ov[0], b0), (ov[1], b0), (ov[1], h1), (ov[0], h1)])
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


def wall_piece(a, b, h0, h1, side, tex_low, tex_high, name, openings=(), band=None, origin=None, mitre=(0.0, 0.0)):
    """A wall along a-b from h0 to h1 with openings cut out. side: 'out' (right of a->b, i.e. outside a CCW room),
    'centre' (straddling the line), 'in', or a room's own half of a wall it shares ('in_half', 'out_half'). band: the height where tex_low gives way to tex_high. mitre: tan of half
    the turn at a and at b; the wall's far face runs on (or stops short) by that much per metre of thickness, so two
    walls meet on the corner's bisector instead of leaving a notch or overlapping."""
    L = math.dist(a, b)
    if L < 0.01 or h1 - h0 < 0.01:
        return
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = uy, -ux                       # right of a->b
    o0, o1 = {'out': (0.0, F.WALL_T), 'centre': (-F.WALL_T / 2, F.WALL_T / 2), 'in': (-F.WALL_T, 0.0),
              'in_half': (-F.WALL_T / 2, 0.0), 'out_half': (0.0, F.WALL_T / 2)}[side]
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
                for off in (o0, o1):
                    sm = s - off * mitre[0] if abs(s) < 1e-6 else (s + off * mitre[1] if abs(s - L) < 1e-6 else s)
                    x, y = a[0] + ux * sm, a[1] + uy * sm
                    pts.append((x + nx * off, y + ny * off, h))
            hullp(pts, tex, name, tally='wall', uv_origin=GP(org[0], org[1], h0))


def edge_span(r, a, b, inward, off=0.3):
    """Lowest floor and highest ceiling along a room edge, sampled every 0.25 m just inside it. Never above the room's
    base floor: a stair or platform against a wall must not lift the wall off the floor, or the level leaks under it."""
    L = math.dist(a, b)
    n = max(2, int(L / 0.25))
    lo, hi = r['floor'], -1e9
    for i in range(n + 1):
        t = min(max(i / n, 0.02), 0.98)
        q = (a[0] + (b[0] - a[0]) * t + inward[0] * off, a[1] + (b[1] - a[1]) * t + inward[1] * off)
        h = level_floor(r, q)
        if any(P.inside(q, hz['poly']) for hz in r['hazards']):
            h -= 0.5
        lo = min(lo, h)
        hi = max(hi, ceiling_at(r, q))
    return lo, hi


def turn_tan(poly, i):
    """tan of half the turn at vertex i (positive at a convex corner of a CCW polygon)."""
    a, b, c = poly[i - 1], poly[i], poly[(i + 1) % len(poly)]
    d1 = (b[0] - a[0], b[1] - a[1])
    d2 = (c[0] - b[0], c[1] - b[1])
    return math.tan(math.atan2(d1[0] * d2[1] - d1[1] * d2[0], d1[0] * d2[0] + d1[1] * d2[1]) / 2)


def gap_overlap(a, b, c, d):
    """Overlap along a-b of an edge c-d of another room that faces it exactly one wall thickness outside it."""
    L = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = uy, -ux                                   # outward (right of a->b)
    for q in (c, d):
        if abs((q[0] - a[0]) * nx + (q[1] - a[1]) * ny - F.WALL_T) > 1e-6:
            return None
    if (d[0] - c[0]) * ux + (d[1] - c[1]) * uy >= 0:
        return None
    tc = (c[0] - a[0]) * ux + (c[1] - a[1]) * uy
    td = (d[0] - a[0]) * ux + (d[1] - a[1]) * uy
    return P.overlap_1d(0, L, tc, td)


def side_openings():
    """Room openings that a corridor passes ALONG (the pipe bay off the pipe run): the corridor's shell closes them."""
    out = []
    for oa, ob, bottom, otop in F.OPENING_3D:
        ex, ey = ob[0] - oa[0], ob[1] - oa[1]
        for c in CORRS:
            hw, _ = corr_section(c['prof'])
            W, _ = corr_shell(c['prof'])
            for pa, pb in zip(c['path'], c['path'][1:]):
                dx, dy = pb[0] - pa[0], pb[1] - pa[1]
                Lc = math.hypot(dx, dy)
                if abs(ex * dy - ey * dx) > 1e-6 * math.hypot(ex, ey) * Lc:
                    continue
                v = abs((oa[0] - pa[0]) * -dy / Lc + (oa[1] - pa[1]) * dx / Lc)
                if hw - 0.3 <= v <= W + 0.3:
                    out.append((oa, ob))
    return out


def build_walls():
    """Every room edge: exterior (outward), shared (one centred wall per pair), gap (two rooms exactly one wall apart:
    one wall fills the gap) or open (a riser and a bulkhead). Exterior walls meeting at a corner are mitred, so an
    inside corner is not two overlapping walls whose faces flicker."""
    edges = {}   # (key, i) -> list of (s0, s1, other, kind)
    for key, r in ROOMS.items():
        poly = r['poly']
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            L = math.dist(a, b)
            cuts = [(0.0, L, None, 'ext')]
            for ok, o in ROOMS.items():
                if ok == key:
                    continue
                op = o['poly']
                for j in range(len(op)):
                    c, d = op[j], op[(j + 1) % len(op)]
                    kind, ov = 'shared', collinear_overlap(a, b, c, d)
                    if not ov:
                        kind, ov = 'gap', gap_overlap(a, b, c, d)
                    if not ov:
                        continue
                    new = []
                    for s0, s1, other, k in cuts:
                        lo, hi = max(s0, ov[0]), min(s1, ov[1])
                        if other is not None or hi - lo < 1e-6:
                            new.append((s0, s1, other, k))
                            continue
                        if lo - s0 > 1e-6:
                            new.append((s0, lo, None, 'ext'))
                        new.append((lo, hi, ok, kind))
                        if s1 - hi > 1e-6:
                            new.append((hi, s1, None, 'ext'))
                    cuts = new
            edges[(key, i)] = cuts
    sides = side_openings()
    open_pairs = {frozenset(p) for p in F.OPEN_EDGES}

    # Exterior pieces meeting end to start are mitred as one chain, within a room (its corners) or across two
    # (the dock's north wall meeting the truck bay's east wall): no overlapping walls, no notch.
    ext = []
    for (key, i), cuts in edges.items():
        poly = ROOMS[key]['poly']
        ea, eb = poly[i], poly[(i + 1) % len(poly)]
        EL = math.dist(ea, eb)
        for s0, s1, other, kind in cuts:
            if other is None:
                a = (ea[0] + (eb[0] - ea[0]) * s0 / EL, ea[1] + (eb[1] - ea[1]) * s0 / EL)
                b = (ea[0] + (eb[0] - ea[0]) * s1 / EL, ea[1] + (eb[1] - ea[1]) * s1 / EL)
                ext.append(dict(key=key, i=i, s0=s0, a=a, b=b, m=[0.0, 0.0]))
    start_at = {}
    for e in ext:
        start_at.setdefault((round(e['a'][0], 4), round(e['a'][1], 4)), []).append(e)
    for e in ext:
        nxt = [f for f in start_at.get((round(e['b'][0], 4), round(e['b'][1], 4)), []) if f is not e]
        if not nxt:
            continue
        f = next((f for f in nxt if f['key'] == e['key']), nxt[0])
        d1 = (e['b'][0] - e['a'][0], e['b'][1] - e['a'][1])
        d2 = (f['b'][0] - f['a'][0], f['b'][1] - f['a'][1])
        th = math.atan2(d1[0] * d2[1] - d1[1] * d2[0], d1[0] * d2[0] + d1[1] * d2[1])
        if abs(th) < math.radians(170):
            e['m'][1] = f['m'][0] = math.tan(th / 2)
    mitres = {(e['key'], e['i'], round(e['s0'], 6)): e['m'] for e in ext}
    # Corridor shells that run ALONG a wall line (not through it): a room wall inside one is the corridor's.
    shells = []
    for c in CORRS:
        W, top = corr_shell(c['prof'])
        for (pa, ha), (pb, hb) in zip(zip(c['path'], c['heights']), zip(c['path'][1:], c['heights'][1:])):
            for t0, t1 in ([(0.0, 1.0)] if c['prof'] == 'crawl' else outside_intervals(pa, pb)):
                qa = (pa[0] + (pb[0] - pa[0]) * t0, pa[1] + (pb[1] - pa[1]) * t0)
                qb = (pa[0] + (pb[0] - pa[0]) * t1, pa[1] + (pb[1] - pa[1]) * t1)
                shells.append((qa, qb, W, min(ha, hb) - F.FLOOR_T, max(ha, hb) + top))

    def in_shell(q, ux, uy, lo, hi):
        for qa, qb, W, s_lo, s_hi in shells:
            dx, dy = qb[0] - qa[0], qb[1] - qa[1]
            Ls = math.hypot(dx, dy)
            if Ls < 1e-6 or abs(ux * dy - uy * dx) > 1e-6 * Ls:
                continue      # only a corridor parallel to the wall
            t = ((q[0] - qa[0]) * dx + (q[1] - qa[1]) * dy) / Ls ** 2
            if 0.0 <= t <= 1.0 and P.seg_dist(q, qa, qb) < W - 0.01 and s_lo <= lo + 1e-6 and hi <= s_hi + 1e-6:
                return True
        return False

    for (key, i), cuts in edges.items():
        r = ROOMS[key]
        poly = r['poly']
        ea, eb = poly[i], poly[(i + 1) % len(poly)]
        EL = math.dist(ea, eb)
        for s0, s1, other, kind in cuts:
            a = (ea[0] + (eb[0] - ea[0]) * s0 / EL, ea[1] + (eb[1] - ea[1]) * s0 / EL)
            b = (ea[0] + (eb[0] - ea[0]) * s1 / EL, ea[1] + (eb[1] - ea[1]) * s1 / EL)
            L = math.dist(a, b)
            ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            inward = (-uy, ux)
            floor_in, ceil_in = edge_span(r, a, b, inward)
            look(r['look'])
            if other is None:
                bottom = floor_in - F.FLOOR_T
                m_a, m_b = mitres[(key, i, round(s0, 6))]
                # What overlaps the wall's own footprint sets its top, 0.25 m at a time. A room stacked across the
                # edge caps it (the booth notch under Logistics) or, lying under this room, raises it to its roof
                # (Logistics' east wall stands to the Sorting Bay's ceiling). A side opening is left to the corridor.
                n_s = max(1, int(round(L / 0.25)))
                tops = []
                for k in range(n_s):
                    t = (k + 0.5) / n_s
                    q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                    if any(ov and ov[0] - 1e-6 <= (q[0] - oa[0]) * (ob[0] - oa[0]) / math.dist(oa, ob) + (q[1] - oa[1]) * (ob[1] - oa[1]) / math.dist(oa, ob) <= ov[1] + 1e-6
                           for oa, ob in sides for ov in [collinear_overlap(oa, ob, a, b)]):
                        tops.append(None)
                        continue
                    q_in = (q[0] + inward[0] * 0.3, q[1] + inward[1] * 0.3)
                    q_wall = (q[0] - inward[0] * F.WALL_T / 2, q[1] - inward[1] * F.WALL_T / 2)
                    if in_shell(q_wall, ux, uy, bottom, ceil_in + F.CEIL_T):
                        tops.append(None)
                        continue
                    top = ceil_in + F.CEIL_T
                    for o in ROOMS.values():
                        if o is r:
                            continue
                        # A room stacked above caps the wall over its floor AND under its own walls' footprint.
                        in_o = P.inside(q_wall, o['poly'])
                        near = lambda q_: P.inside(q_, o['poly']) or P.edge_dist(q_, o['poly']) < F.WALL_T - 1e-6
                        if near(q_wall) and near(q_in) and o['floor'] - F.FLOOR_T > bottom + 0.5:
                            top = min(top, o['floor'] - F.FLOOR_T)
                        elif in_o:
                            top = max(top, ceiling_at(o, q_wall) + F.CEIL_T)
                    tops.append(round(top, 4))
                m.group(f'{key} walls')
                runs, k0 = [], 0
                for k in range(1, n_s + 1):
                    if k == n_s or tops[k] != tops[k0]:
                        runs.append([k0, k, tops[k0]])
                        k0 = k
                # A sharp corner's mitre cuts the far face back by -m * WALL_T; an end run shorter than that (the bit
                # of wall that would have stood in the neighbouring room) is taken into the next run.
                for end, m_ in ((0, m_a), (-1, m_b)):
                    need = max(0.0, -m_) * F.WALL_T + 0.01
                    while len(runs) > 1 and (runs[end][1] - runs[end][0]) * L / n_s < need and runs[end + (1 if end == 0 else -1)][2] is not None:
                        nb = runs[end + (1 if end == 0 else -1)]
                        if end == 0:
                            nb[0] = runs[0][0]
                            runs.pop(0)
                        else:
                            nb[1] = runs[-1][1]
                            runs.pop()
                for k0, k, top in runs:
                    if top is None:
                        continue
                    pa = (a[0] + (b[0] - a[0]) * k0 / n_s, a[1] + (b[1] - a[1]) * k0 / n_s)
                    pb = (a[0] + (b[0] - a[0]) * k / n_s, a[1] + (b[1] - a[1]) * k / n_s)
                    wall_piece(pa, pb, bottom, top, 'out', R('plinth'), R('wall'), f'{key} wall',
                               openings=wall_openings(pa, pb, 'room'), band=floor_in + S.PLINTH_H,
                               origin=r['poly'][0], mitre=(m_a if k0 == 0 else 0.0, m_b if k == n_s else 0.0))
                continue
            o = ROOMS[other]
            if kind != 'gap' and frozenset((key, other)) in open_pairs:
                if key > other:
                    continue  # an open edge (one space seen across a step) is built once, from the first key
                m.group(f'{key}|{other} walls')
                floor_o, ceil_o = edge_span(o, a, b, (-inward[0], -inward[1]))
                hi_r, lo_f, hi_f = (r, floor_o, floor_in) if floor_in > floor_o else (o, floor_in, floor_o)
                side = 'in' if hi_r is r else 'out'
                look(hi_r['look'])
                wall_piece(a, b, lo_f - F.FLOOR_T, hi_f - F.FLOOR_T, side, R('plinth'), R('plinth'), f'{key}|{other} edge')
                if abs(ceil_in - ceil_o) > 1e-6:
                    wall_piece(a, b, min(ceil_in, ceil_o) + F.CEIL_T, max(ceil_in, ceil_o) + F.CEIL_T, 'centre', R('wall'),
                               R('wall'), f'{key}|{other} bulkhead')
                continue
            # Every room owns its walls (user rule): its own 0.25 m half of a wall it shares with a neighbour (inside
            # its edge) or of a wall-thick gap (outside its edge), in its own look, from its own floor to its own
            # ceiling. Each room builds its half from its own side, so the two halves carry two looks and a room
            # regenerated alone (--room) never touches its neighbour's half.
            m.group(f'{key} walls')
            if kind == 'gap':
                ao = (a[0] - inward[0] * F.WALL_T, a[1] - inward[1] * F.WALL_T)
                bo = (b[0] - inward[0] * F.WALL_T, b[1] - inward[1] * F.WALL_T)
                side, holes = 'out_half', wall_openings(a, b, 'room') + wall_openings(ao, bo, 'room')
            else:
                side, holes = 'in_half', wall_openings(a, b, 'shared')
            wall_piece(a, b, floor_in - F.FLOOR_T, ceil_in + F.CEIL_T, side, R('plinth'), R('wall'), f'{key} wall',
                       openings=holes, band=floor_in + S.PLINTH_H, origin=r['poly'][0])
    m.ungroup()


# ================================================================================
# Blockers, rails, ladders
# ================================================================================
def blocker_height(name):
    for kw, h in F.BLOCKER_H:
        if kw in name:
            return h
    return 1.0


RAIL_POSTS = set()


def rail(x0, y0, x1, y1, h0, h1, name):
    """An open rail: posts every 2 m and a top rail. Two rails meeting at a bend share their corner post."""
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 0.2:
        return
    k = max(1, int(L // 2))
    for j in range(k + 1):
        t = j / k
        px, py, ph = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, h0 + (h1 - h0) * t
        spot = (round(px, 1), round(py, 1), round(ph, 1))
        if any(math.dist(spot, q) < 0.15 for q in RAIL_POSTS):
            continue
        RAIL_POSTS.add(spot)
        prism([(px - 0.05, py - 0.05), (px + 0.05, py - 0.05), (px + 0.05, py + 0.05), (px - 0.05, py + 0.05)],
              ph, ph + 1.05, R('frame'), f'{name} post', tally='rail')
    nx, ny = -(y1 - y0) / L * 0.05, (x1 - x0) / L * 0.05
    hullp([(x0 + nx * s, y0 + ny * s, h0 + dh) for s in (-1, 1) for dh in (1.0, 1.1)]
          + [(x1 + nx * s, y1 + ny * s, h1 + dh) for s in (-1, 1) for dh in (1.0, 1.1)], R('frame'), f'{name} top', tally='rail')


def under_deck(r, poly, top):
    """A deck over part of this footprint caps anything rising into it at the deck's underside."""
    for lv in r['levels']:
        if lv['kind'] == 'deck' and overlap_area(lv['poly'], poly) > 1e-3 and top > lv['h'] - F.DECK_T:
            top = min(top, lv['h'] - F.DECK_T)
    return top


def build_blockers(r):
    look(r['look'])
    for bl in r['blockers']:
        poly, name = bl['poly'], bl['name']
        c = (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
        base = level_floor(r, c)
        h = blocker_height(name)
        top = under_deck(r, poly, ceiling_at(r, c) if h == 'ceiling' else base + h)
        # Stood on the lowest floor under it (a machine at a step reaches the lower floor), never sunk through a slab.
        bottom = min([base] + [level_floor(r, (q[0] + (c[0] - q[0]) * 0.02, q[1] + (c[1] - q[1]) * 0.02)) for q in poly])
        tag = f"{r['key']} {name}"
        if name in F.ENTERABLE:
            # A fenced walk-in cage (the supervisor cage, the lift): thin fence walls with a gap where its gate's door
            # kit stands (rb_door, placed by kit_entities).
            gate_name, gate, gate_kind = next(d for d in F.DOORS if d[0].startswith(F.ENTERABLE[name]))
            gw, gh = F.DOOR_SIZE[gate_kind]
            n = len(poly)
            for i in range(n):
                a, b = poly[i], poly[(i + 1) % n]
                ops = []
                if P.seg_dist(gate, a, b) < 0.1:
                    L = math.dist(a, b)
                    s = ((gate[0] - a[0]) * (b[0] - a[0]) + (gate[1] - a[1]) * (b[1] - a[1])) / L
                    ops.append([(s - gw / 2, base - 1), (s + gw / 2, base - 1), (s + gw / 2, base + gh), (s - gw / 2, base + gh)])
                if P.edge_dist(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), r['poly']) < 0.05:
                    continue      # the room's own wall
                # Mitred where two fence walls meet, so a corner is not two overlapping walls.
                own = [P.edge_dist(((poly[k][0] + poly[(k + 1) % n][0]) / 2, (poly[k][1] + poly[(k + 1) % n][1]) / 2), r['poly']) < 0.05
                       for k in range(n)]
                wall_piece(a, b, base, top, 'in', R('frame'), R('frame'), tag, openings=ops,
                           mitre=(0.0 if own[i - 1] else turn_tan(poly, i), 0.0 if own[(i + 1) % n] else turn_tan(poly, (i + 1) % n)))
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


def drawbridge_span(a, d, L):
    """The span (u from a, along direction d) of a corridor segment that the drawbridge covers, or None."""
    db = F.KIT_DRAWBRIDGE
    hx, hy = db['hinge']
    ex, ey = db['extends']
    far = (hx + ex * db['length'], hy + ey * db['length'])
    ends = []
    for q in (db['hinge'], far):
        u = (q[0] - a[0]) * d[0] + (q[1] - a[1]) * d[1]
        off = abs((q[0] - a[0]) * -d[1] + (q[1] - a[1]) * d[0])
        if off > db['width'] / 2 or u < -0.01 or u > L + 0.01:
            return None
        ends.append(u)
    return (min(ends), max(ends))


def room_at(pt, margin=0.25):
    """The room whose floor holds a plan point, looking a little inward from a wall face."""
    return next((r for r in ROOMS.values() if P.inside(pt, r['poly'])), None)


def door_placement(door_pt, kind, side=None):
    """Where a door's kit stands: the wall's centre line at the door, the wall's normal, the floor it stands on, the
    leaf height, and the owning room (for a shared wall, the room on the side it opens from)."""
    w, hh = F.DOOR_SIZE[kind]
    # A gate in a walk-in cage's fence: the fence stands inside the cage's edge.
    for room in ROOMS.values():
        for bl in room['blockers']:
            if bl['name'] in F.ENTERABLE and P.edge_dist(door_pt, bl['poly']) < 0.1:
                poly = bl['poly']
                a, b = min(zip(poly, poly[1:] + poly[:1]), key=lambda e: P.seg_dist(door_pt, e[0], e[1]))
                L = math.dist(a, b)
                ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                centre = (door_pt[0] - uy * F.WALL_T / 2, door_pt[1] + ux * F.WALL_T / 2)
                return centre, (uy, -ux), level_floor(room, centre), hh, room
    edges = [(r, a, b) for r in ROOMS.values() for a, b in zip(r['poly'], r['poly'][1:] + r['poly'][:1])
             if P.seg_dist(door_pt, a, b) < 0.1]
    r, a, b = edges[0]
    L = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    normal = (uy, -ux)
    shared = len({e[0]['key'] for e in edges}) > 1
    centre = door_pt if shared else (door_pt[0] + normal[0] * F.WALL_T / 2, door_pt[1] + normal[1] * F.WALL_T / 2)
    owner = r
    if side is not None:
        owner = room_at((door_pt[0] + side[0] * 0.6, door_pt[1] + side[1] * 0.6)) or r
    # A corridor meeting the room here: the door stands on the corridor's floor.
    for c in CORRS:
        for (p, hp), (q, hq) in zip(zip(c['path'], c['heights']), zip(c['path'][1:], c['heights'][1:])):
            if P.seg_dist(door_pt, p, q) < 0.6:
                seg = math.dist(p, q)
                t = max(0.0, min(1.0, ((door_pt[0] - p[0]) * (q[0] - p[0]) + (door_pt[1] - p[1]) * (q[1] - p[1])) / seg ** 2))
                return centre, normal, hp + (hq - hp) * t, hh, owner
    h0 = door_floor(door_pt, normal)
    top = h0 + hh
    for ceil in door_ceilings(door_pt, normal):
        if abs(top - ceil) < 0.01:
            top = ceil + F.CEIL_T          # the opening runs up through that ceiling slab: so does the leaf
    return centre, normal, h0, top - h0, owner


def kit_entities():
    """The progression kit (G-02), placed from the plan: doors, switches, cards, the fan and the drawbridge. Each sits
    in its room's group, so a room regenerated alone keeps its own."""
    def fmt(v):
        return f'{B._fmt(v[0])} {B._fmt(v[1])}'

    def origin(x, y, h):
        return ' '.join(B._fmt(v) for v in B.to_map(G(x, h, y)))

    count = 0
    for prefix, rule in F.DOOR_RULES:
        name, door_pt, kind = next(d for d in F.DOORS if d[0].startswith(prefix))
        side = rule.get('side')
        centre, normal, h0, leaf_h, owner = door_placement(door_pt, kind, side)
        needs = rule.get('needs', '')
        props = {'origin': origin(centre[0], centre[1], h0), 'id': rule['id'], 'opens': rule['opens'], 'needs': needs,
                 'needs_text': ';'.join(f'{f}={F.FLAG_TEXT[f]}' for f in needs.split(',') if f),
                 'side': fmt(side) if side else '0 0', 'latch': rule.get('latch', 0),
                 'events': rule.get('events', rule['id']), 'style': rule.get('style', 'rise'),
                 'width': B._fmt(F.DOOR_SIZE[kind][0]), 'height': B._fmt(round(leaf_h, 4)), 'facing': fmt(normal),
                 'look': owner['look'], 'label': name}
        m.entity('rb_door', props, group=f"{owner['key']} {owner['name']}")
        count += 1
    for sid, name, sp, h, facing, mount, what in F.KIT_SWITCHES:
        room = room_at((sp[0] + facing[0] * 0.3, sp[1] + facing[1] * 0.3))
        props = {'origin': origin(sp[0], sp[1], h), 'id': sid, 'sends': what.get('sends', ''), 'sets': what.get('sets', ''),
                 'once': what.get('once', 1), 'effect': what.get('effect', ''), 'mount': mount,
                 'notice': what.get('notice', ''), 'facing': fmt(facing), 'look': room['look'], 'label': name}
        m.entity('rb_switch', props, group=f"{room['key']} {room['name']}")
        count += 1
    for kid, name, kp, h, flag, colour in F.KIT_PICKUPS:
        room = room_at(kp)
        props = {'origin': origin(kp[0], kp[1], h), 'id': kid, 'flag': flag, 'color': ' '.join(B._fmt(c) for c in colour),
                 'notice': name.split(':')[1].split(',')[0].strip().capitalize() + '.', 'look': room['look'], 'label': name}
        m.entity('rb_pickup', props, group=f"{room['key']} {room['name']}")
        count += 1
    fan = F.KIT_FAN
    room = ROOMS['PP']
    m.entity('rb_fan', {'origin': origin(fan['point'][0], fan['point'][1], fan['floor'] + F.FAN['hub_height']),
                        'id': fan['id'], 'event': fan['event'], 'diameter': B._fmt(F.FAN['diameter']),
                        'blades': F.FAN['blades'], 'hub_radius': B._fmt(F.FAN['hub_radius']),
                        'blade_width': B._fmt(F.FAN['blade_width']), 'facing': fmt(fan['facing']), 'look': room['look']},
             group=f"{room['key']} {room['name']}")
    db = F.KIT_DRAWBRIDGE
    room = room_at((db['hinge'][0] + db['extends'][0], db['hinge'][1] + db['extends'][1]))
    m.entity('rb_drawbridge', {'origin': origin(db['hinge'][0], db['hinge'][1], db['height']), 'id': db['id'],
                               'event': db['event'], 'length': B._fmt(db['length']), 'width': B._fmt(db['width']),
                               'extends': fmt(db['extends']), 'look': room['look']},
             group=f"{room['key']} {room['name']}")
    return count + 2


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
    top = hi - F.FLOOR_T            # the floor round the hole finishes the shaft
    prism([(x0 - t, y1), (x1 + t, y1), (x1 + t, y1 + t), (x0 - t, y1 + t)], lo - F.FLOOR_T, top, R('wall'), f'{name} shaft', tally='shaft')
    prism([(x0 - t, y0), (x0, y0), (x0, y1), (x0 - t, y1)], lo - F.FLOOR_T, top, R('wall'), f'{name} shaft', tally='shaft')
    prism([(x1, y0), (x1 + t, y0), (x1 + t, y1), (x1, y1)], lo - F.FLOOR_T, top, R('wall'), f'{name} shaft', tally='shaft')
    crawl_top = lo + F.PROFILE_BOX['crawl'][1]
    prism([(x0 - t, y0 - t), (x1 + t, y0 - t), (x1 + t, y0), (x0 - t, y0)], crawl_top + 0.25, top, R('wall'), f'{name} shaft',
          tally='shaft')
    prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], lo - F.FLOOR_T, lo, top_tex(R('floor'), R('plinth')),
          f'{name} shaft floor', tally='shaft')
    m.ungroup()


# ================================================================================
# Corridors
# ================================================================================
def outside_intervals(p, q):
    """Parameter intervals of p-q (0..1) that lie outside every room. Each 0.1 m step is judged by its midpoint, so a
    point on a wall two rooms share is never "outside"; the switch points are then found exactly by bisection."""
    L = math.dist(p, q)
    n = max(4, int(L / 0.1))

    def out(t):
        pt = (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
        return not any(P.inside(pt, r['poly']) and P.edge_dist(pt, r['poly']) > 1e-6 for r in ROOMS.values())

    def switch(t0, t1):
        f0 = out(t0)
        for _ in range(40):
            tm = (t0 + t1) / 2
            if out(tm) == f0:
                t0 = tm
            else:
                t1 = tm
        t = (t0 + t1) / 2
        return round(t * n) / n if abs(t * n - round(t * n)) < 1e-6 else t

    mids = [(k + 0.5) / n for k in range(n)]
    flags = [out(t) for t in mids]
    res, start = [], (0.0 if flags[0] else None)
    for k in range(1, n):
        if flags[k] != flags[k - 1]:
            t = switch(mids[k - 1], mids[k])
            if flags[k]:
                start = t
            else:
                res.append((start, t))
                start = None
    if start is not None:
        res.append((start, 1.0))
    return [(a, b) for a, b in res if (b - a) * L > 0.05]


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
        ivals = [(0.0, 1.0)] if prof == 'crawl' else outside_intervals(path[i], path[i + 1])
        if prof == 'catwalk':
            cuts_t = sorted({0.0, 1.0} | {t for iv in ivals for t in iv})
            ivals = list(zip(cuts_t, cuts_t[1:]))
        for t0, t1 in ivals:
            mitre_in = math.tan(turn[i] / 2) if t0 < 1e-6 and i > 0 else 0.0
            mitre_out = math.tan(turn[i + 1] / 2) if t1 > 1 - 1e-6 and i + 1 < n - 1 else 0.0

            def pt(u, v, h):
                x = a[0] + d[0] * u + nl[0] * v
                y = a[1] + d[1] * u + nl[1] * v
                return (x, y, ha + (hb - ha) * u / L + h)

            u0, u1 = t0 * L, t1 * L
            # Where the corridor meets a room at a DOOR, its walls, ceiling and ribs stop at the wall's outer face (the
            # door is a hole in the room wall); only the floor runs on under it to the room face, as the threshold.
            trims = []
            for t_end in (t0, t1):
                pe = (a[0] + d[0] * L * t_end, a[1] + d[1] * L * t_end)
                room = next((r for r in ROOMS.values() if P.edge_dist(pe, r['poly']) < 0.05), None)
                trim = 0.0
                if room is not None and door_at(pe):
                    ea, eb = min(zip(room['poly'], room['poly'][1:] + room['poly'][:1]), key=lambda e: P.seg_dist(pe, e[0], e[1]))
                    el = math.dist(ea, eb)
                    sin_e = abs(d[0] * (eb[1] - ea[1]) - d[1] * (eb[0] - ea[0])) / el
                    trim = F.WALL_T / max(sin_e, 0.2)
                trims.append(trim)
            wu0, wu1 = u0 + trims[0], u1 - trims[1]

            def piece(poly, tex, name, span=None, **kw):
                ua_, ub_, mi, mo = span if span else (wu0, wu1, mitre_in, mitre_out)
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
                    cuts.append((lo_u, hi_u, 1 if v > 0 else -1, top_rel, abs(v)))
            bounds = sorted({wu0, wu1} | {x for cu in cuts for x in cu[:2] if wu0 < x < wu1})
            spans = []
            for sa, sb in zip(bounds, bounds[1:]):
                active = {cu[2]: (cu[3], cu[4]) for cu in cuts if cu[0] <= sa + 1e-6 and cu[1] >= sb - 1e-6}
                spans.append((sa, sb, mitre_in if abs(sa - wu0) < 1e-9 else 0.0, mitre_out if abs(sb - wu1) < 1e-9 else 0.0, active))
            if cuts:
                c.setdefault('cuts', []).extend((s0[i] + lo_, s0[i] + hi_) for lo_, hi_, *_ in cuts)

            def side_wall(poly, side, tex, name, **kw):
                for sa, sb, mi, mo, active in spans:
                    q = poly
                    if side in active:
                        # Above the side opening only, and no further out than the room's edge.
                        q = P.clip(P.ccw(poly), 0, -1, -active[side][0])
                        q = P.clip(q, side, 0, active[side][1]) if q else q
                        if not q or P.area(P.ccw(q)) < P.AREA_EPS:
                            continue
                    piece(q, tex, name, span=(sa, sb, mi, mo), **kw)

            def across(poly, tex, name, full=False, **kw):
                """A full-width piece (floor, ceiling), clipped at the edge of a room that opens off either side."""
                sp = list(spans)
                if full and sp:
                    # The floor runs on under a door's wall to the room face (the threshold).
                    sp[0] = (u0,) + sp[0][1:]
                    sp[-1] = sp[-1][:1] + (u1,) + sp[-1][2:]
                for sa, sb, mi, mo, active in sp:
                    q = P.ccw(poly)
                    for side, (_, v_edge) in active.items():
                        q = P.clip(q, side, 0, v_edge) if q else q
                    if q and P.area(P.ccw(q)) >= P.AREA_EPS:
                        piece(q, tex, name, span=(sa, sb, mi, mo), **kw)

            run_u = GP(d[0], d[1], 0.0)
            run_u = (d[0], 0.0, -d[1])
            flight = abs(hb - ha) > 1e-6
            org = GP(*pt(u0, -1.0, 0.0))
            if prof == 'catwalk':
                inside_room = in_any_room(((a[0] + d[0] * (u0 + u1) / 2), (a[1] + d[1] * (u0 + u1) / 2)), 0.05)
                if inside_room:
                    # The drawbridge (a kit entity) is the catwalk over its own span: leave that span empty.
                    runs = [(u0, u1)]
                    gap = drawbridge_span(a, d, L)
                    if gap and gap[0] < u1 and gap[1] > u0:
                        runs = [(ua, ub) for ua, ub in ((u0, max(u0, gap[0])), (min(u1, gap[1]), u1)) if ub - ua > 0.05]
                    for ua, ub in runs:
                        mi = mitre_in if abs(ua - u0) < 1e-9 else 0.0
                        mo = mitre_out if abs(ub - u1) < 1e-9 else 0.0
                        piece([(-hw_clear, -0.25), (hw_clear, -0.25), (hw_clear, 0.0), (-hw_clear, 0.0)],
                              top_tex(R('grate'), R('frame')), f"{c['key']} deck", span=(ua, ub, mi, mo), tally='catwalk')
                        for side in (1, -1):
                            v = side * (hw_clear - 0.05)
                            # Mitred like the walls: the inner rail stops short of a bend, the outer one runs on to meet.
                            p0, p1 = pt(ua + v * mi, v, 0.0), pt(ub - v * mo, v, 0.0)
                            rail(p0[0], p0[1], p1[0], p1[1], p0[2], p1[2], f"{c['key']} rail")
                    continue
            for k_end, t_end in enumerate((t0, t1)):
                if trims[k_end] <= 0.0:
                    continue
                pe = (a[0] + d[0] * L * t_end, a[1] + d[1] * L * t_end)
                door = door_at(pe)
                room = next(r_ for r_ in ROOMS.values() if P.edge_dist(pe, r_['poly']) < 0.05)
                ea, eb = min(zip(room['poly'], room['poly'][1:] + room['poly'][:1]), key=lambda e: P.seg_dist(pe, e[0], e[1]))
                el = math.dist(ea, eb)
                e = ((eb[0] - ea[0]) / el, (eb[1] - ea[1]) / el)
                n_out = (e[1], -e[0])                           # outward of the room's CCW edge
                w_along = F.DOOR_SIZE[door[2]][0] / 2 / (F.WALL_T / trims[k_end])
                hh_ = ha + (hb - ha) * t_end
                quad = [(pe[0] + e[0] * sg * w_along + n_out[0] * o, pe[1] + e[1] * sg * w_along + n_out[1] * o)
                        for sg, o in ((-1, 0.0), (1, 0.0), (1, F.WALL_T), (-1, F.WALL_T))]
                prism(P.ccw(quad), hh_ - F.FLOOR_T, hh_, top_tex(R('floor'), R('plinth')), f"{c['key']} threshold", tally='corridor')
            if not flight:
                across([(-W, -F.FLOOR_T), (W, -F.FLOOR_T), (W, 0.0), (-W, 0.0)],
                      top_tex(R('grate'), R('frame')) if prof == 'catwalk' else top_tex(R('floor'), R('plinth')),
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
                across([(-W, S.CEIL_Y), (W, S.CEIL_Y), (W, S.SHELL_TOP), (-W, S.SHELL_TOP)], R('ceiling'),
                       f"{c['key']} ceiling", tally='corridor', uv_origin=org, uv_u=run_u)
            else:
                # Box section. On a flight the walls and ceiling rise with the steps (the frame slopes them).
                wt = W - hw_clear
                lift = abs(hb - ha) if (flight and hb < ha) else 0.0
                # A crawl passing under a room whose floor underside is the crawl's ceiling height uses that floor as
                # its ceiling (the pipe gallery under the pump room): its walls stop there and the slab is left out.
                roofs = [r_ for r_ in ROOMS.values() if prof == 'crawl' and not flight
                         and abs(r_['floor'] - F.FLOOR_T - (ha + h_clear)) < 0.01]
                wall_top = h_clear
                foot = -F.FLOOR_T - lift if flight else 0.0      # on the flat the floor slab runs under the walls
                for side in (1, -1):
                    side_wall([(side * hw_clear, foot), (side * W, foot), (side * W, wall_top),
                               (side * hw_clear, wall_top)], side, R('wall'), f"{c['key']} wall", tally='corridor', uv_origin=org)
                if roofs:
                    foot = [pt(wu0 + v * mitre_in, v, 0.0)[:2] for v in (-W,)] + [pt(wu1 - v * mitre_out, v, 0.0)[:2] for v in (-W, W)] \
                        + [pt(wu0 + v * mitre_in, v, 0.0)[:2] for v in (W,)]
                    holes = [q for r_ in roofs for q in r_['parts']]
                    for part in P.subtract_all([P.ccw(foot)], holes):
                        prism(part, ha + h_clear, ha + h_clear + wt, bottom_tex(R('ceiling'), R('wall')), f"{c['key']} ceiling",
                              tally='corridor')
                else:
                    across([(-W, h_clear), (W, h_clear), (W, h_clear + wt), (-W, h_clear + wt)], bottom_tex(R('ceiling'), R('wall')),
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
                (xa_, ya_), (xb_, yb_), _ = main[-1]
                inner = lambda y_: (xa_ - S.RIB_D) + (y_ - ya_) * (xb_ - xa_) / (yb_ - ya_)
                lo_b, hi_b = inner(S.CEIL_Y - S.RIB_D), inner(S.CEIL_Y)
                hullp([rp(uu, v, hh) for v, hh in [(-lo_b, S.CEIL_Y - S.RIB_D), (lo_b, S.CEIL_Y - S.RIB_D), (hi_b, S.CEIL_Y),
                                                   (-hi_b, S.CEIL_Y)] for uu in ur], R('rib'), f"{c['key']} rib beam", tally='rib')
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


def los_clear(a, b, r, tall, fences=()):
    """Plan line of sight inside room r, not through a tall blocker, nor across a walk-in cage's fence (the gate is
    taken as shut, so a light never counts on seeing through it)."""
    for t in (0.2, 0.4, 0.6, 0.8):
        q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        if not P.inside(q, r['poly']):
            return False
    for poly in fences:
        for e0, e1 in zip(poly, poly[1:] + poly[:1]):
            if seg_cross(a, b, e0, e1):
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
    fences = [b['poly'] for b in r['blockers'] if b['name'] in F.ENTERABLE and blocker_height(b['name']) >= 1.5]
    tall = [b['poly'] for b in r['blockers'] if b['name'] not in F.ENTERABLE
            and (blocker_height(b['name']) == 'ceiling' or blocker_height(b['name']) >= 1.5)]
    xs, ys = [p[0] for p in r['poly']], [p[1] for p in r['poly']]
    samples = []
    x = math.floor(min(xs)) + 0.5
    while x < max(xs):
        y = math.floor(min(ys)) + 0.5
        while y < max(ys):
            pt = (x, y)
            # Clear of walk-in cages' fences too (they stand 0.5 m inside the outline): a light in a fence lights nothing.
            in_fence = any(P.edge_dist(pt, f) < (F.WALL_T + 0.3 if P.inside(pt, f) else 0.3)
                           for f in (b['poly'] for b in r['blockers'] if b['name'] in F.ENTERABLE))
            clear = P.edge_dist(pt, r['poly']) > 0.3 and not in_fence and not any(P.inside(pt, b) for b in blockers)
            if P.inside(pt, r['poly']) and clear:
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
            if i == j or los_clear((si[0], si[1]), (sj[0], sj[1]), r, tall, fences):
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
        done = set()
        for i, (x, y, h, posture) in enumerate(route_heights(pts)):
            o = B.to_map(G(x, h, y))
            props = {'origin': ' '.join(B._fmt(v) for v in o), 'route': rname, 'index': i, 'posture': posture,
                     'oneway': oneway}
            act = F.ROUTE_ACTIONS.get((x, y))
            if act and (x, y) not in done:
                props['use'] = act             # the route checker uses these kit pieces here, as the player would
                done.add((x, y))
            m.entity('rb_route', props, group='Markers')
            count += 1
    # At level start these must refuse the player standing here, and the running fan must close its hole.
    for kid, rp, tag in F.REFUSALS:
        x, y, h, _ = route_heights([rp + ((tag,) if tag else ())])[0]
        m.entity('rb_probe', {'origin': ' '.join(B._fmt(v) for v in B.to_map(G(x, h, y))), 'kind': 'refuse', 'id': kid},
                 group='Markers')
        count += 1
    (fx, fy), fh = F.FAN_BLOCKED
    m.entity('rb_probe', {'origin': ' '.join(B._fmt(v) for v in B.to_map(G(fx, fh + 0.05, fy))), 'kind': 'blocked_crouch'},
             group='Markers')
    return count + 1


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
kits = kit_entities()
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
    print(f'FREIGHT_V2_MAP: {m.count} brushes, {lights} lights, {kits} kit pieces, {markers} markers, {len(m.groups)} groups '
          f'-> {MAP.relative_to(ROOT)}')
    print('  ' + ', '.join(f'{k} {v}' for k, v in sorted(m.tally.items())))
