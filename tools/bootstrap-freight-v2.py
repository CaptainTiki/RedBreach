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
FACE_OFF = {}           # (room key, edge index) -> the room face's offset from the edge (outward positive)


def edge_face(key, i):
    """The room face's offset from edge i (outward positive). Along an edge the room shares with another, its wall is its
    own half inside the edge, and so is the rest of that edge's wall: the face runs flat (user, 2026-09-27)."""
    if (key, i) not in FACE_OFF:
        r = ROOMS[key]
        poly = r['poly']
        a, b = poly[i], poly[(i + 1) % len(poly)]
        open_pairs = {frozenset(p_) for p_ in F.OPEN_EDGES}
        shared = any(ov and ov[1] - ov[0] > 1e-6
                     for o in ROOMS.values() if o is not r and frozenset((key, o['key'])) not in open_pairs
                     for j in range(len(o['poly']))
                     for ov in [collinear_overlap(a, b, o['poly'][j], o['poly'][(j + 1) % len(o['poly'])])])
        FACE_OFF[(key, i)] = -F.WALL_T / 2 if shared else 0.0
    return FACE_OFF[(key, i)]


def covered_by(o, pt):
    """Whether a plan point lies in a room or in the band of its own outside walls (each edge's wall, from the edge or its
    face out to its outer face; corners not included)."""
    if P.inside(pt, o['poly']):
        return True
    poly = o['poly']
    for j in range(len(poly)):
        a, b = poly[j], poly[(j + 1) % len(poly)]
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        s = (pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy
        off = (pt[0] - a[0]) * uy - (pt[1] - a[1]) * ux
        f = edge_face(o['key'], j)
        outer = 0.25 if f < 0 else F.WALL_T
        if -1e-6 <= s <= L + 1e-6 and -1e-6 <= off <= outer + 1e-6:
            return True
    return False


def edge_open(key, a, b):
    """Whether the room edge a-b is (partly) an open edge: one space seen across a step, with no wall."""
    open_pairs = {frozenset(p_) for p_ in F.OPEN_EDGES}
    return any(ov and ov[1] - ov[0] > 1e-6
               for o in ROOMS.values() if o['key'] != key and frozenset((key, o['key'])) in open_pairs
               for j in range(len(o['poly']))
               for ov in [collinear_overlap(a, b, o['poly'][j], o['poly'][(j + 1) % len(o['poly'])])])


def shared_strips(r):
    """The strip inside every edge whose wall stands inside it (an edge the room shares, all along): a platform or ceiling
    stops short of it, or its edge face lies on the plane of the wall's end and the two flicker (the S1 landing)."""
    out = []
    poly = r['poly']
    for i in range(len(poly)):
        f = edge_face(r['key'], i)
        if f >= 0.0:
            continue
        a, b = poly[i], poly[(i + 1) % len(poly)]
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        inward = (-uy, ux)
        h = -f
        out.append(P.ccw([a, b, (b[0] + inward[0] * h, b[1] + inward[1] * h), (a[0] + inward[0] * h, a[1] + inward[1] * h)]))
    return out


def crawl_cuts(slab_lo, slab_hi):
    """Plan footprints of crawls whose clear space a floor slab would cross (the girder crawl under the pump pit's
    floor): the slab is cut there. A crawl whose ceiling IS a floor (the pipe gallery under the pump room) is not."""
    out = []
    for c in CORRS:
        if c['prof'] != 'crawl':
            continue
        hw, hc = corr_section(c['prof'])
        W, _ = corr_shell(c['prof'])
        cap = 0.25 if F.CRAWL_CAPS.get(c['key']) == 'start' else 0.0
        for k, ((pa, ha), (pb, hb)) in enumerate(zip(zip(c['path'], c['heights']), zip(c['path'][1:], c['heights'][1:]))):
            lo, hi = min(ha, hb), max(ha, hb) + hc
            if not (lo < slab_lo and slab_hi < hi):
                continue
            L = math.dist(pa, pb)
            dx, dy = (pb[0] - pa[0]) / L, (pb[1] - pa[1]) / L
            nx, ny = -dy, dx
            back = cap if k == 0 else W                   # corners overlap by the shell width, so the cut is whole
            a = (pa[0] - dx * back, pa[1] - dy * back)
            b = (pb[0] + dx * W, pb[1] + dy * W)
            out.append(P.ccw([(a[0] + nx * W, a[1] + ny * W), (b[0] + nx * W, b[1] + ny * W),
                              (b[0] - nx * W, b[1] - ny * W), (a[0] - nx * W, a[1] - ny * W)]))
    return out


def build_floor(r):
    look(r['look'])
    org = GP(r['poly'][0][0], r['poly'][0][1], r['floor'])
    worg = GP(r['poly'][0][0], r['poly'][0][1], r['floor'] - F.FLOOR_T)      # the room walls' texture origin
    holes = [P.ccw(h) for h in F.FLOOR_HATCHES.get(r['key'], [])]
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
    holes += crawl_cuts(r['floor'] - F.FLOOR_T, r['floor'])
    for part in P.subtract_all([list(p) for p in r['parts']], holes):
        prism(part, r['floor'] - F.FLOOR_T, r['floor'], top_tex(R('floor'), R('plinth')), f"{r['key']} floor",
              tally='floor', uv_origin=org)
    for lv in r['levels']:
        if lv['kind'] in ('pit', 'lower'):
            sub = [h['poly'] for h in r['hazards'] if overlap_area(h['poly'], lv['poly']) > 1e-3]
            sub += crawl_cuts(lv['h'] - F.FLOOR_T, lv['h'])
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
            # Its sides are walls (the plinth band repeated up a 4 m side, note 7), with the room walls' origin so a
            # flight beside it continues the same panels.
            for part in P.subtract_all(P.convex_parts(lv['poly']), shared_strips(r)):
                prism(part, r['floor'] - F.FLOOR_T, lv['h'], top_tex(R('floor'), R('wall')), f"{r['key']} {lv['name']}",
                      tally='platform', uv_origin=worg)
    for hz in r['hazards']:
        pit = next(lv for lv in r['levels'] if lv['kind'] == 'pit' and overlap_area(hz['poly'], lv['poly']) > 1e-3)
        bottom = pit['h'] - 0.5
        for part in P.convex_parts(hz['poly']):
            prism(part, bottom - F.FLOOR_T, bottom, top_tex(R('coolant'), R('plinth')), f"{r['key']} {hz['name']}", tally='floor')
        pit_walls(r, hz['poly'], bottom - F.FLOOR_T, pit['h'] - F.FLOOR_T, f"{r['key']} {hz['name']} wall")
    for br in r['bridges']:
        depth = 0.75 if 'crawl inside' in br['name'] else 0.5
        for part in P.convex_parts(br['poly']):
            prism(part, br['h'] - depth, br['h'], top_tex(R('grate'), R('frame')), f"{r['key']} {br['name']}", tally='deck')
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
        wall_piece(a, b, h0, h1, 'out', R('wall'), R('wall'), name, openings=cuts, origin=r['poly'][0])


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
            # Treads are floor and step fronts risers; a flight's sides are walls, in the room walls' origin, so a side
            # running on from a platform's side is one surface (note 7).
            rise, side = R('riser'), R('wall')
            tex = (lambda rise, side, fl: lambda n_, c_: fl if abs(n_[1]) > 0.5 else
                   (rise if abs(n_[0] * ux - n_[2] * uy) > 0.5 else side))(rise, side, R('floor'))
            prism([(box[0], box[2]), (box[1], box[2]), (box[1], box[3]), (box[0], box[3])], base, top,
                  tex, f"{r['key']} {st['name']} step {k}", tally='stair',
                  uv_origin=GP(r['poly'][0][0], r['poly'][0][1], r['floor'] - F.FLOOR_T))


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
    return [op for op, _ in wall_openings_k(a, b, owner_kind)]


def wall_openings_k(a, b, owner_kind):
    """wall_openings with each opening's kind: 'frame' (a corridor mouth's frame fills it), 'shell' (a corridor passing
    through), 'door', 'window', 'open' (an explicit opening) or 'fan'."""
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
            mo = mouth_for(c, pt)
            if mo is not None and not (door and door[0].startswith(F.SEALED)):
                # A mouth: the wall is cut to the frame's outline and the frame (and a door's panel) fills it. A low
                # mouth (capped) cuts only a door-sized hole.
                if door:
                    door_used.add(door[0])
                if mo['low']:
                    w, dh = F.DOOR_SIZE['door']
                    out.append(([(s - w / 2 / sin, h - F.FLOOR_T), (s + w / 2 / sin, h - F.FLOOR_T), (s + w / 2 / sin, h + dh),
                                 (s - w / 2 / sin, h + dh)], 'door'))
                    continue
                out.append(([(s + v / sin, h + hh) for v, hh in mouth_outline(c['prof'])], 'frame'))
                continue
            if door:
                door_used.add(door[0])
                if door[0].startswith(F.SEALED):
                    continue
                # The corridor's floor runs under the wall to the room face and is the threshold, so the hole starts
                # at its underside: no wall stub lies on the floor and flickers.
                w, hh = F.DOOR_SIZE[door[2]]
                b0 = h - F.FLOOR_T
                out.append(([(s - w / 2 / sin, b0), (s + w / 2 / sin, b0), (s + w / 2 / sin, h + hh), (s - w / 2 / sin, h + hh)], 'door'))
            else:
                # The junction rule: the corridor meets the room through its own profile. The wall is cut to the
                # corridor's outer shell and the corridor's pieces fill the wall's thickness up to the room face.
                W, top = corr_shell(c['prof'])
                b0 = h - F.FLOOR_T
                out.append(([(s - W / sin, b0), (s + W / sin, b0), (s + W / sin, h + top), (s - W / sin, h + top)], 'shell'))
    # Doors and windows that are not corridor mouths.
    for name, pt, kind in F.DOORS:
        if name in door_used or name.startswith(F.SEALED) or kind not in F.DOOR_SIZE:
            continue
        s = (pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy
        w, hh = F.DOOR_SIZE[kind]
        # Its width, not its centre: a window straddling the end of a shared wall is cut from both pieces (note 12).
        if abs((pt[0] - a[0]) * uy - (pt[1] - a[1]) * ux) > 0.1 or s + w / 2 < 1e-6 or s - w / 2 > L - 1e-6:
            continue
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
        out.append(([(s - w / 2, b0), (s + w / 2, b0), (s + w / 2, top), (s - w / 2, top)], 'window' if kind == 'window' else 'door'))
    # Explicit openings.
    for oa, ob, bottom, top in F.OPENING_3D:
        ov = collinear_overlap(a, b, oa, ob)
        if not ov:
            continue
        mid = ((oa[0] + ob[0]) / 2, (oa[1] + ob[1]) / 2)
        h0 = bottom if bottom is not None else door_floor(mid, normal)
        h1 = top if (top is not None and bottom is not None) else h0 + (top if top is not None else F.DEFAULT_OPENING_H)
        b0 = h0 - F.FLOOR_T if owner_kind == 'shared' and bottom is None else h0
        out.append(([(ov[0], b0), (ov[1], b0), (ov[1], h1), (ov[0], h1)], 'open'))
    # The fan: stopped, so a crouch-through hole.
    fa, fb = F.FAN_HOLE['room_edge']
    ov = collinear_overlap(a, b, fa, fb)
    if ov:
        s = (F.FAN_HOLE['centre'] - a[0]) * ux if abs(ux) > 0.5 else (F.FAN_HOLE['centre'] - a[1]) * uy
        s = abs((F.FAN_HOLE['centre'] - a[0]) / ux) if abs(ux) > 0.5 else s
        rr = F.FAN['diameter'] / 2 / math.cos(math.pi / 8)   # the octagon encloses the fan: its flat bottom is the lip
        hc = F.FAN_HOLE['floor'] + F.FAN['hub_height']
        out.append(([(s + rr * math.cos(k * math.pi / 4 + math.pi / 8), hc + rr * math.sin(k * math.pi / 4 + math.pi / 8))
                     for k in range(8)], 'fan'))
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


FOOT = 0.125            # the plinth stands this far proud of its wall: its texture change has its own geometry
MOUTH_D = 0.25          # a corridor mouth's frame stands this far proud of the room face
MOUTH_M = 0.25          # and reaches this far past the corridor's clear outline over the room wall
MOUTH_LIP = 0.15        # a box corridor's frame narrows its opening this much (a P profile's frame is its rib)
SILL_H = 0.0625         # the low sill under a mouth that carries the change of floor texture
FEET = {}               # room key -> plinth runs along its walls, joined at its corners once every wall is known
_MOUTHS = []


def meet(e_a, e_b, e_off, f_a, f_b, f_off):
    """Where e's line at offset e_off meets f's line at offset f_off, for e ending where f starts (offsets to the right
    of each wall's direction): (distance past e's end, distance past f's start, negative = before it)."""
    Le, Lf = math.dist(e_a, e_b), math.dist(f_a, f_b)
    ue = ((e_b[0] - e_a[0]) / Le, (e_b[1] - e_a[1]) / Le)
    uf = ((f_b[0] - f_a[0]) / Lf, (f_b[1] - f_a[1]) / Lf)
    ne, nf = (ue[1], -ue[0]), (uf[1], -uf[0])
    r0 = f_a[0] + nf[0] * f_off - (e_b[0] + ne[0] * e_off)
    r1 = f_a[1] + nf[1] * f_off - (e_b[1] + ne[1] * e_off)
    den = -ue[0] * uf[1] + ue[1] * uf[0]
    return (-r0 * uf[1] + r1 * uf[0]) / den, (ue[0] * r1 - ue[1] * r0) / den


def grow(poly, dist):
    """A convex polygon grown outward by dist: every edge moved out, the corners re-intersected."""
    poly = P.ccw(poly)
    n = len(poly)
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0)
        lines.append(((x0 + (y1 - y0) / L * dist, y0 - (x1 - x0) / L * dist), (x1 - x0, y1 - y0)))
    out = []
    for i in range(n):
        (pa_, u), (qa_, v) = lines[i - 1], lines[i]
        den = u[0] * v[1] - u[1] * v[0]
        if abs(den) < 1e-12:
            out.append(qa_)
            continue
        t = ((qa_[0] - pa_[0]) * v[1] - (qa_[1] - pa_[1]) * v[0]) / den
        out.append((pa_[0] + u[0] * t, pa_[1] + u[1] * t))
    return out


def x_at(chain, h):
    """x of a chain [(x, h)] rising in h, straight between its points and carried on past its ends."""
    for (x0, h0), (x1, h1) in zip(chain, chain[1:]):
        if h <= h1 or (x1, h1) == chain[-1]:
            return x1 if abs(h1 - h0) < 1e-9 else x0 + (h - h0) * (x1 - x0) / (h1 - h0)
    return chain[-1][0]


def mouth_chains(prof):
    """A corridor mouth's frame (user, 2026-09-27: a doorway shaped like the corridor's rib, a little thicker): its inner
    and outer right-hand chains [(v, h)] from under the floor up, and the heights of their flat tops."""
    ft = -F.FLOOR_T
    if prof in ('P1', 'P2'):
        main = [sg for sg in S.PROFILES[prof]['segments'] if sg[2] != 'plinth']
        foot_x = main[0][0][0] - S.RIB_D
        inner = [(foot_x, ft), (foot_x, main[0][0][1])] + [(xb - S.RIB_D, yb) for _, (xb, yb), _ in main]
        (xa, ya), (xb, yb), _ = main[0]
        x0 = xa + (0.0 - ya) * (xb - xa) / (yb - ya)
        outer = [(x0 + MOUTH_M, 0.0)] + [(x + MOUTH_M, y) for _, (x, y), _ in main]
        return inner, outer, S.CEIL_Y - S.RIB_D, S.CEIL_Y + MOUTH_M
    hw, hc = corr_section(prof)
    t, mm = (0.05, 0.1) if prof == 'crawl' else (MOUTH_LIP, MOUTH_M)      # a crawl keeps nearly all its headroom
    return [(hw - t, ft), (hw - t, hc)], [(hw + mm, ft), (hw + mm, hc)], hc - t, hc + mm


def mouth_outline(prof):
    """The frame's outer outline (v, h), convex: the hole it fills in the room wall."""
    _, outer, _, top_out = mouth_chains(prof)
    hs = sorted({-F.FLOOR_T, top_out} | {h for _, h in outer if -F.FLOOR_T < h < top_out})
    right = [(x_at(outer, h), h) for h in hs]
    return right + [(-x, h) for x, h in reversed(right)]


def mouths():
    """Every place a corridor meets a room, or a pit in a room, through the room's wall: a frame stands there."""
    if _MOUTHS:
        return _MOUTHS
    for c in CORRS:
        path, n = c['path'], len(c['path'])
        for i in range(n - 1):
            pa_, pb_ = path[i], path[i + 1]
            L = math.dist(pa_, pb_)
            d = ((pb_[0] - pa_[0]) / L, (pb_[1] - pa_[1]) / L)
            ivals = [(0.0, 1.0)] if c['prof'] == 'crawl' else outside_intervals(pa_, pb_)
            for t0, t1 in ivals:
                mid = (pa_[0] + (pb_[0] - pa_[0]) * (t0 + t1) / 2, pa_[1] + (pb_[1] - pa_[1]) * (t0 + t1) / 2)
                if c['prof'] == 'catwalk' and in_any_room(mid, 0.05):
                    continue                           # a catwalk's deck inside a room: no wall there
                for t, into in ((t0, -1), (t1, 1)):
                    if c['prof'] == 'crawl' and not ((i == 0 and t == 0.0) or (i == n - 2 and t == 1.0)):
                        continue                       # a crawl passes under rooms; only its ends are mouths
                    pe = (pa_[0] + (pb_[0] - pa_[0]) * t, pa_[1] + (pb_[1] - pa_[1]) * t)
                    beyond = (pe[0] + d[0] * into * 0.3, pe[1] + d[1] * into * 0.3)
                    hit = None
                    for key, r in ROOMS.items():
                        polys = [(r['poly'], True)] + [(lv['poly'], False) for lv in r['levels'] if lv['kind'] in ('pit', 'lower')]
                        for poly, is_room in polys:
                            if P.edge_dist(pe, poly) > 0.05 or not P.inside(beyond, poly):
                                continue
                            if not is_room and (not P.inside(pe, r['poly']) or P.edge_dist(pe, r['poly']) < 0.05):
                                continue
                            j = min(range(len(poly)), key=lambda j_: P.seg_dist(pe, poly[j_], poly[(j_ + 1) % len(poly)]))
                            hit = dict(room=r, key=key, edge=j if is_room else None, ea=poly[j], eb=poly[(j + 1) % len(poly)])
                            break
                        if hit:
                            break
                    door = door_at(pe)
                    if hit is None or (door is None and any(math.dist(dd[1], pe) < 0.6 and dd[0].startswith(F.SEALED)
                                                            for dd in F.DOORS)):
                        continue
                    el = math.dist(hit['ea'], hit['eb'])
                    e = ((hit['eb'][0] - hit['ea'][0]) / el, (hit['eb'][1] - hit['ea'][1]) / el)
                    hit.update(c=c, i=i, t=t, pt=pe, into=into, d=d, sin=max(abs(d[0] * e[1] - d[1] * e[0]), 0.2), door=door)
                    # A room lower than the corridor's frame (Receiving under C1, note 2): the corridor is capped with
                    # its rib and a plug, and the room wall gets a door-sized hole (the kit lab's door_low junction).
                    hm_ = c['heights'][i] + (c['heights'][i + 1] - c['heights'][i]) * t
                    inside_pt = (pe[0] + d[0] * into * 0.6, pe[1] + d[1] * into * 0.6)
                    hit['low'] = (c['prof'] != 'crawl' and hit['edge'] is not None
                                  and ceiling_at(hit['room'], inside_pt) < hm_ + mouth_chains(c['prof'])[3] - 1e-6)
                    _MOUTHS.append(hit)
    return _MOUTHS


def mouth_geom(mo):
    """A mouth along its corridor segment: the room face and the wall's outer face (u), the frame's span, the floor
    height, and the frame's plan footprint."""
    c = mo['c']
    pa_, pb_ = c['path'][mo['i']], c['path'][mo['i'] + 1]
    ha_, hb_ = c['heights'][mo['i']], c['heights'][mo['i'] + 1]
    L = math.dist(pa_, pb_)
    d, into = mo['d'], mo['into']
    u_end = mo['t'] * L
    face = edge_face(mo['key'], mo['edge']) if mo['edge'] is not None else 0.0
    u_face = u_end + into * (-face) / mo['sin']
    u_out = u_end - into * F.WALL_T / mo['sin']
    f_lo, f_hi = sorted((u_face + into * MOUTH_D, u_out))
    _, outer, _, top_out = mouth_chains(c['prof'])
    xo = x_at(outer, 0.0)
    nl = (-d[1], d[0])
    hm = ha_ + (hb_ - ha_) * mo['t']

    def plan_quad(ua, ub, x_):
        return P.ccw([(pa_[0] + d[0] * u + nl[0] * v, pa_[1] + d[1] * u + nl[1] * v)
                      for u, v in ((ua, -x_), (ub, -x_), (ub, x_), (ua, x_))])
    # What a room's plinth must keep clear of: the frame, or the plinth collar round its foot (it meets the collar at
    # the plinth's top), over the frame's own heights only (notes 8, 18: a vent or door above a floor keeps its plinth).
    collar = collared(mo)
    clear_foot = None
    if not mo['low']:
        if collar:
            clear_foot = plan_quad(*sorted((u_face + into * (MOUTH_D + FOOT), u_out)), x_at(outer, S.PLINTH_H) + FOOT)
        else:
            clear_foot = plan_quad(f_lo, f_hi, xo)
    return dict(a=pa_, u_end=u_end, u_face=u_face, u_out=u_out, f_lo=f_lo, f_hi=f_hi, hm=hm,
                footprint=plan_quad(f_lo, f_hi, xo), clear_foot=clear_foot, clear_h=(hm - F.FLOOR_T - 0.01, hm + top_out))


def collared(mo):
    """A frame standing on a room floor with a plinth gets a plinth collar round its foot (note 1): not a crawl's, not a
    capped one, not one in a pit, and not one high over the room's floor (the crane catwalk leaving the dock)."""
    if mo['c']['prof'] == 'crawl' or mo['low'] or mo['edge'] is None:
        return False
    pe, d, into = mo['pt'], mo['d'], mo['into']
    inside_pt = (pe[0] + d[0] * into * 0.6, pe[1] + d[1] * into * 0.6)
    c = mo['c']
    hm = c['heights'][mo['i']] + (c['heights'][mo['i'] + 1] - c['heights'][mo['i']]) * mo['t']
    return abs(level_floor(mo['room'], inside_pt) - hm) < 0.05


def mouth_for(c, pt):
    return next((mo for mo in mouths() if mo['c'] is c and math.dist(mo['pt'], pt) < 0.05), None)


def threshold(c, mo, fp, g, half):
    """The corridor's floor through the room wall, the opening's width (note 20: an open frame left a trench), from the
    wall's outer face to the room's edge line, where the room's own floor begins."""
    d = mo['d']
    t_lo, t_hi = sorted((g['u_out'], g['u_end']))
    if t_hi - t_lo < 1e-3:
        return
    floor = top_tex(R('grate'), R('frame')) if c['prof'] == 'catwalk' else top_tex(R('floor'), R('plinth'))
    hullp([fp(u, v, h) for v, h in [(-half, -F.FLOOR_T), (half, -F.FLOOR_T), (half, 0.0), (-half, 0.0)] for u in (t_lo, t_hi)],
          floor, f"{c['key']} threshold", tally='corridor', uv_origin=GP(*fp(t_lo, -1.0, 0.0)), uv_u=(d[0], 0.0, -d[1]))


def build_mouth(c, mo, a, d, u_end, hm):
    """The frame at a corridor mouth: shaped like the corridor's rib, a little thicker, standing MOUTH_D proud of the room
    face and through the wall, so no corridor texture shows in the room wall and every texture change sits on it. A low
    sill carries the change of floor. At a door a plain panel fills the rest of the frame's hole in the wall."""
    prof = c['prof']
    into = mo['into']
    nl = (-d[1], d[0])
    inner, outer, top_in, top_out = mouth_chains(prof)
    g = mouth_geom(mo)
    u_face, u_out, f_lo, f_hi = g['u_face'], g['u_out'], g['f_lo'], g['f_hi']
    door = mo['door']

    def fp(u, v, h):
        return (a[0] + d[0] * u + nl[0] * v, a[1] + d[1] * u + nl[1] * v, hm + h)

    org = GP(*fp(f_lo, -x_at(outer, 0.0), 0.0))
    rib = R('rib')
    if mo['low']:
        return build_low_mouth(c, mo, fp, inner, outer, top_in, top_out, g)
    hs = sorted({-F.FLOOR_T, top_in} | {h for _, h in inner + outer if -F.FLOOR_T < h < top_in})
    for h0, h1 in zip(hs, hs[1:]):
        for sg in (1, -1):
            quad = [(sg * x_at(inner, h0), h0), (sg * x_at(outer, h0), h0), (sg * x_at(outer, h1), h1), (sg * x_at(inner, h1), h1)]
            hullp([fp(u, v, h) for v, h in quad for u in (f_lo, f_hi)], rib, f"{c['key']} mouth frame", tally='rib', uv_origin=org)
    if top_out > top_in + 1e-6:
        quad = [(-x_at(outer, top_in), top_in), (x_at(outer, top_in), top_in), (x_at(outer, top_out), top_out),
                (-x_at(outer, top_out), top_out)]
        hullp([fp(u, v, h) for v, h in quad for u in (f_lo, f_hi)], rib, f"{c['key']} mouth frame", tally='rib', uv_origin=org)
    if prof != 'crawl':
        s_lo, s_hi = sorted((u_face + into * MOUTH_D, (u_face - into * 0.1) if door else u_out))
        if door:
            s_lo, s_hi = sorted((u_face + into * MOUTH_D, u_face))
        xs = x_at(inner, 0.0)
        hullp([fp(u, v, h) for v, h in [(-xs, -F.FLOOR_T), (xs, -F.FLOOR_T), (xs, SILL_H), (-xs, SILL_H)] for u in (s_lo, s_hi)],
              R('frame'), f"{c['key']} sill", tally='corridor', uv_origin=org)
    threshold(c, mo, fp, g, F.DOOR_SIZE[door[2]][0] / 2 if door else x_at(inner, 0.0))
    if collared(mo):
        # The room's plinth continues round the frame's foot and into the doorway (note 1): a collar FOOT proud of the
        # frame on its outer side, its room face and its inner side, as tall as the plinth, in the room's plinth. It
        # stops 1/16 m short of the frame's corridor end, so the two ends are never one plane.
        room = mo['room']
        look(room['look'])
        c_lo, c_hi = sorted((u_face + into * (MOUTH_D + FOOT), u_out + into * 0.0625))
        corg = GP(room['poly'][0][0], room['poly'][0][1], hm - F.FLOOR_T)
        for sg in (1, -1):
            quad = [(sg * (x_at(inner, -F.FLOOR_T) - FOOT), -F.FLOOR_T), (sg * (x_at(outer, -F.FLOOR_T) + FOOT), -F.FLOOR_T),
                    (sg * (x_at(outer, S.PLINTH_H) + FOOT), S.PLINTH_H), (sg * (x_at(inner, S.PLINTH_H) - FOOT), S.PLINTH_H)]
            pts = [fp(u, v, h) for v, h in quad for u in (c_lo, c_hi)]
            foot = P.ccw(list({(round(x_, 6), round(y_, 6)) for x_, y_, _ in pts}))
            # Not where a machine stands against the frame (the compressor room's pipe spine beside the trench).
            if any(len(P.intersect(foot, P.ccw(grow(b_['poly'], 0.05)))) >= 3 for b_ in room['blockers']):
                continue
            hullp(pts, R('plinth'), f"{c['key']} mouth collar", tally='rib', uv_origin=corg)
        look(c['look'])
    if door:
        # A plain panel fills the frame's opening round the door, flush with the room face on the room side and with the
        # frame's end on the corridor side: no room wall shows inside the corridor (note 22).
        w, dh = F.DOOR_SIZE[door[2]]
        if dh > top_in - 0.02:
            dh = top_in + 0.02
        hole = [(-w / 2, -F.FLOOR_T - 1.0), (w / 2, -F.FLOOR_T - 1.0), (w / 2, dh), (-w / 2, dh)]
        hs_in = sorted({-F.FLOOR_T, top_in} | {h for _, h in inner if -F.FLOOR_T < h < top_in})
        opening = [(x_at(inner, h), h) for h in hs_in]
        opening = P.ccw(opening + [(-x, h) for x, h in reversed(opening)])
        p_lo, p_hi = sorted((u_face, u_out))
        panel, jamb = R('door_panel'), R('frame')
        tex = lambda n_, c_: panel if abs(n_[0] * d[0] - n_[2] * d[1]) > 0.5 else jamb
        for part in P.subtract_all([opening], [P.ccw(hole)]):
            hullp([fp(u, v, h) for v, h in part for u in (p_lo, p_hi)], tex, f"{c['key']} door panel", tally='door', uv_origin=org)
    return min(f_lo, u_out, u_face + into * MOUTH_D), max(f_hi, u_out, u_face + into * MOUTH_D)


def build_low_mouth(c, mo, fp, inner, outer, top_in, top_out, g):
    """A corridor meeting a room lower than its frame (note 2; the kit lab's door_low): the corridor ends at the room
    wall's outer face in its rib frame and a plug shaped to its profile, the room wall gets a door-sized hole, a frame
    stands round the door on the room face, and a sill carries the change of floor."""
    into = mo['into']
    u_face, u_out = g['u_face'], g['u_out']
    rib = R('rib')
    u_back = u_out - into * S.RIB_DEPTH
    f_lo, f_hi = sorted((u_back, u_out))
    org = GP(*fp(f_lo, -x_at(outer, 0.0), 0.0))
    hs = sorted({-F.FLOOR_T, top_in} | {h for _, h in inner + outer if -F.FLOOR_T < h < top_in})
    for h0, h1 in zip(hs, hs[1:]):
        for sg in (1, -1):
            quad = [(sg * x_at(inner, h0), h0), (sg * x_at(outer, h0), h0), (sg * x_at(outer, h1), h1), (sg * x_at(inner, h1), h1)]
            hullp([fp(u, v, h) for v, h in quad for u in (f_lo, f_hi)], rib, f"{c['key']} mouth frame", tally='rib', uv_origin=org)
    quad = [(-x_at(outer, top_in), top_in), (x_at(outer, top_in), top_in), (x_at(outer, top_out), top_out),
            (-x_at(outer, top_out), top_out)]
    hullp([fp(u, v, h) for v, h in quad for u in (f_lo, f_hi)], rib, f"{c['key']} mouth frame", tally='rib', uv_origin=org)
    w, dh = F.DOOR_SIZE['door']
    hole = [(-w / 2, -F.FLOOR_T - 1.0), (w / 2, -F.FLOOR_T - 1.0), (w / 2, dh), (-w / 2, dh)]
    hs_in = sorted({-F.FLOOR_T, top_in} | {h for _, h in inner if -F.FLOOR_T < h < top_in})
    opening = [(x_at(inner, h), h) for h in hs_in]
    opening = P.ccw(opening + [(-x, h) for x, h in reversed(opening)])
    p_lo, p_hi = sorted((u_out - into * 0.25, u_out))
    d = mo['d']
    panel, jamb = R('door_panel'), R('frame')
    tex = lambda n_, c_: panel if abs(n_[0] * d[0] - n_[2] * d[1]) > 0.5 else jamb
    for part in P.subtract_all([opening], [P.ccw(hole)]):
        hullp([fp(u, v, h) for v, h in part for u in (p_lo, p_hi)], tex, f"{c['key']} plug", tally='door', uv_origin=org)
    threshold(c, mo, fp, g, w / 2)
    s_lo, s_hi = sorted((u_out - into * 0.25, u_face + into * 0.15))
    hullp([fp(u, v, h) for v, h in [(-w / 2, -F.FLOOR_T), (w / 2, -F.FLOOR_T), (w / 2, SILL_H), (-w / 2, SILL_H)]
           for u in (s_lo, s_hi)], R('frame'), f"{c['key']} sill", tally='corridor', uv_origin=org)
    # The door's frame on the room face, proud of the room's plinth.
    room = mo['room']
    look(room['look'])
    fw, fd = 0.15, 0.15
    d_lo, d_hi = sorted((u_face, u_face + into * fd))
    for poly in ([(-w / 2 - fw, -F.FLOOR_T), (-w / 2, -F.FLOOR_T), (-w / 2, dh + fw), (-w / 2 - fw, dh + fw)],
                 [(w / 2, -F.FLOOR_T), (w / 2 + fw, -F.FLOOR_T), (w / 2 + fw, dh + fw), (w / 2, dh + fw)],
                 [(-w / 2, dh), (w / 2, dh), (w / 2, dh + fw), (-w / 2, dh + fw)]):
        hullp([fp(u, v, h) for v, h in poly for u in (d_lo, d_hi)], R('frame'), f"{c['key']} door frame", tally='door')
    look(c['look'])
    return min(f_lo, d_lo), max(f_hi, d_hi)


def room_wall(a, b, h0, h1, face, outer, tex, name, openings=(), origin=None, shifts=None, tally='wall', inner_bottom=None,
              clip=(), h1b=None, uv_shear=None):
    """A room's wall along a-b between plan offsets face and outer (to the right of a->b, outward of a CCW room), h0 to
    h1, with openings (wall coordinates s, h) cut out. shifts {'a': {offset: ds}, 'b': {...}} carries each face line past
    (or short of) the wall's ends, so it meets the next wall's same face exactly. h1b makes the top slope from h1 at a to
    h1b at b (a plinth following a stair), and uv_shear keeps its texture rows parallel to that slope."""
    L = math.dist(a, b)
    if L < 0.01 or h1 - h0 < 0.01:
        return
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = uy, -ux
    sh = shifts or {}
    sa, sb = sh.get('a', {}), sh.get('b', {})
    org = GP(*origin) if origin else GP(a[0], a[1], h0)

    def shift(sd, off):
        """How far this face line runs past the end: interpolated along the joint between the face and outer lines."""
        k, kf, ko = round(off, 4), round(face, 4), round(outer, 4)
        if k in sd:
            return sd[k]
        if kf in sd and ko in sd and abs(outer - face) > 1e-9:
            return sd[kf] + (off - face) / (outer - face) * (sd[ko] - sd[kf])
        return 0.0

    layers = [(face, outer, h0)]
    if inner_bottom is not None and face < -1e-6 < outer:
        layers = [(face, 0.0, max(h0, inner_bottom)), (0.0, outer, h0)]
    offs = [face, outer, 0.0]
    s_min = min([0.0] + [shift(sa, o) for o in offs])
    s_max = L + max([0.0] + [shift(sb, o) for o in offs])

    def plan_pt(s_, h, off):
        return (a[0] + ux * s_ + nx * off, a[1] + uy * s_ + ny * off, h)

    top_b = h1 if h1b is None else h1b
    top_at = lambda s_: h1 + (top_b - h1) * s_ / L
    kw = {} if uv_shear is None else {'uv_shear': uv_shear}
    for o0, o1, lo in layers:
        if min(h1, top_b) - lo < 0.01:
            continue
        # The wall is laid out long enough for its joints, the openings cut from it, and each piece then cut by its two
        # joint planes: at each offset the piece runs from where the start joint crosses that offset to where the end
        # joint does. A piece's shape is the hull of those two slices plus any corner of it that a joint plane crosses
        # between them: a true cut, so a slanted opening edge never bends where it meets a joint (the fan's wall).
        rect = [(s_min, lo), (s_max, lo), (s_max, top_at(s_max)), (s_min, top_at(s_min))]
        holes = [P.ccw(op) for op in openings if P.intersect(rect, P.ccw(op))]
        for part in P.subtract_all([rect], holes):
            part = P.ccw(part)
            pts = []
            for off in (o0, o1):
                sl = P.clip(part, -1, 0, -shift(sa, off))               # s >= the start joint
                sl = P.clip(sl, 1, 0, L + shift(sb, off)) if sl else sl  # s <= the end joint
                if sl and len(sl) >= 3 and P.area(P.ccw(sl)) > 1e-6:
                    pts += [plan_pt(s_, h, off) for s_, h in sl]
            for s_v, h_v in part:
                for sd, base in ((sa, 0.0), (sb, L)):
                    c0, c1 = base + shift(sd, o0), base + shift(sd, o1)
                    if abs(c1 - c0) > 1e-9 and min(c0, c1) + 1e-9 < s_v < max(c0, c1) - 1e-9:
                        t = (s_v - c0) / (c1 - c0)
                        o_v = o0 + t * (o1 - o0)
                        if shift(sa, o_v) - 1e-9 <= s_v <= L + shift(sb, o_v) + 1e-9:
                            pts.append(plan_pt(s_v, h_v, o_v))
            if len(pts) < 4:
                continue
            # A piece the joints cut down to a sliver with no thickness (a slice left at one offset only) has no volume.
            xs_, ys_ = [x for x, _, _ in pts], [y for _, y, _ in pts]
            offs_ = [(x - a[0]) * nx + (y - a[1]) * ny for x, y, _ in pts]
            if max(offs_) - min(offs_) < 1e-4:
                continue
            lo_h, hi_h = min(h for _, _, h in pts), max(h for _, _, h in pts)
            if clip:
                foot = hull2d([(x, y) for x, y, _ in pts])
                rect_part = all(abs(h - lo_h) < 1e-6 or abs(h - hi_h) < 1e-6 for _, _, h in pts)
                hit = []
                for cp, vlo, vhi in clip if rect_part and len(foot) >= 3 else ():
                    if vlo >= hi_h - 1e-6 or vhi <= lo_h + 1e-6:
                        continue
                    # A wall that only touches the room's outline is left whole. The cut is grown 1/16 m, so the cut face
                    # stands behind the neighbour's own wall face: func_godot snaps vertices to 1/32 m, and a 1 cm gap
                    # snapped shut and flickered (note 14).
                    ov = P.intersect(foot, P.ccw(cp))
                    if len(ov) >= 3 and P.area(P.ccw(ov)) > 1e-4:
                        hit.append((P.ccw(grow(cp, 0.0625)), vlo, vhi))
                if hit:
                    # Out of a neighbouring room, only over that room's own height (the band above its ceiling stays).
                    cuts_h = sorted({lo_h, hi_h} | {v for _, a_, b_ in hit for v in (a_, b_) if lo_h < v < hi_h})
                    for b0, b1 in zip(cuts_h, cuts_h[1:]):
                        active = [cp for cp, a_, b_ in hit if a_ < b1 - 1e-6 and b_ > b0 + 1e-6]
                        for piece in P.subtract_all([foot], active):
                            if P.area(P.ccw(piece)) > 1e-4:
                                prism(piece, b0, b1, tex, name, tally=tally, uv_origin=org)
                    continue
            hullp(pts, tex, name, tally=tally, uv_origin=org, **kw)


def hull2d(points):
    """The convex hull of plan points, counter-clockwise."""
    pts = sorted({(round(x, 6), round(y, 6)) for x, y in points})
    if len(pts) < 3:
        return pts

    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2 and (out[-1][0] - out[-2][0]) * (q[1] - out[-2][1]) - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0]) <= 0:
                out.pop()
            out.append(q)
        return out
    lower, upper = half(pts), half(reversed(pts))
    return lower[:-1] + upper[:-1]


def pulled_ladder(lp, lo, a, b, face, floor):
    """Whether a ladder stands on this wall's face at this floor: it is then pulled out clear of the plinth, which runs on
    behind it (note 19)."""
    L = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    s = (lp[0] - a[0]) * ux + (lp[1] - a[1]) * uy
    off = (lp[0] - a[0]) * uy - (lp[1] - a[1]) * ux
    return -0.3 <= s <= L + 0.3 and abs(off - face) < 0.06 and abs(floor - lo) < 0.05


LADDER_PULL = FOOT + 0.025      # how far a ladder on a plinthed wall stands out from the wall face
STEP_DIAG = 1.0                 # floor steps up to this high along a wall get a diagonal plinth (notes 15, 16)


def add_feet(r, i, a, b, face, holes):
    """Record the plinth along a wall: FOOT proud of its face and PLINTH_H tall on the floor beside it. Beside a flight it
    follows the flight's slope, and at a small step in the floor it climbs diagonally, so the band runs unbroken (notes
    3, 15, 16). None in a coolant channel. It keeps clear of a wall switch and of a ladder that is not pulled out."""
    L = math.dist(a, b)
    if L < 0.01:
        return
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    inward = (-uy, ux)
    n_s = max(1, int(round(L / 0.25)))

    def at(s_):
        return (a[0] + ux * s_ + inward[0] * (0.3 - face), a[1] + uy * s_ + inward[1] * (0.3 - face))
    vals = []
    for k in range(n_s):
        q = at(L * (k + 0.5) / n_s)
        if not P.inside(q, r['poly']) or any(P.inside(q, hz['poly']) for hz in r['hazards']):
            vals.append(None)
            continue
        j = next((j for j, st in enumerate(r['stairs']) if P.inside(q, st['poly'])), None)
        vals.append(('s', j) if j is not None else ('f', round(level_floor(r, q), 4)))
    pieces, k0 = [], 0
    for k in range(1, n_s + 1):
        if k == n_s or vals[k] != vals[k0]:
            s0_, s1_ = L * k0 / n_s, L * k / n_s
            v = vals[k0]
            if v is None:
                pieces.append(None)
            elif v[0] == 'f':
                pieces.append([s0_, s1_, v[1], v[1]])
            else:
                st = r['stairs'][v[1]]
                pieces.append([s0_, s1_, stair_height(st, at(s0_)), stair_height(st, at(s1_))])
            k0 = k
    final = [pc for pc in pieces if pc is not None]
    # Keep clear of what is mounted on the wall and of mouth frames, over their own heights only.
    clear = []
    nx, ny = uy, -ux
    for name, lp, h0l, h1l in F.LADDERS:
        lo = min(h0l, h1l)
        if P.seg_dist(lp, a, b) < 0.6 - face and not any(pulled_ladder(lp, lo, a, b, face, fl_[2]) for fl_ in final):
            sm = (lp[0] - a[0]) * ux + (lp[1] - a[1]) * uy
            clear.append([(sm - 0.5, lo - 1.0), (sm + 0.5, lo - 1.0), (sm + 0.5, max(h0l, h1l)), (sm - 0.5, max(h0l, h1l))])
    for _, _, sp, h_sw, _, mnt, _ in F.KIT_SWITCHES:
        if mnt == 'wall' and P.seg_dist(sp, a, b) < 0.6 - face:
            sm = (sp[0] - a[0]) * ux + (sp[1] - a[1]) * uy
            clear.append([(sm - 0.5, h_sw - 1.0), (sm + 0.5, h_sw - 1.0), (sm + 0.5, h_sw + 2.5), (sm - 0.5, h_sw + 2.5)])
    strip = P.ccw([(a[0] + nx * (face - FOOT), a[1] + ny * (face - FOOT)), (b[0] + nx * (face - FOOT), b[1] + ny * (face - FOOT)),
                   (b[0] + nx * face, b[1] + ny * face), (a[0] + nx * face, a[1] + ny * face)])
    for mo in mouths():
        g = mouth_geom(mo)
        if g['clear_foot'] is None:
            continue
        ov = P.intersect(strip, g['clear_foot'])
        if ov and P.area(P.ccw(ov)) > 1e-4:
            ss = [(q[0] - a[0]) * ux + (q[1] - a[1]) * uy for q in g['clear_foot']]
            h_lo, h_hi = g['clear_h']
            clear.append([(min(ss), h_lo), (max(ss), h_lo), (max(ss), h_hi), (min(ss), h_hi)])
    for s0_, s1_, h0_, h1_ in final:
        if s1_ - s0_ < 1e-3:
            continue
        ga, gb = (a[0] + ux * s0_, a[1] + uy * s0_), (a[0] + ux * s1_, a[1] + uy * s1_)
        gh = [[(x - s0_, h) for x, h in (op if kind in ('frame', 'shell') else grow(op, FOOT))] for op, kind in holes]
        gh += [[(x - s0_, h) for x, h in op] for op in clear]
        FEET.setdefault(r['key'], []).append(dict(i=i, s=math.dist(r['poly'][i], ga), a=ga, b=gb, face=face,
                                                  floor=min(h0_, h1_), h_a=h0_, h_b=h1_, holes=gh, sa={}, sb={}))


def split_foot(g, s_cut):
    """A plinth run cut at s_cut along it: (before, after), each with its share of the holes and joints."""
    Lg = math.dist(g['a'], g['b'])
    t = s_cut / Lg
    mid = (g['a'][0] + (g['b'][0] - g['a'][0]) * t, g['a'][1] + (g['b'][1] - g['a'][1]) * t)
    h_mid = g['h_a'] + (g['h_b'] - g['h_a']) * t
    first = dict(g, b=mid, h_b=h_mid, sb={}, floor=min(g['h_a'], h_mid))
    second = dict(g, a=mid, s=g['s'] + s_cut, h_a=h_mid, sa={}, floor=min(h_mid, g['h_b']),
                  holes=[[(x - s_cut, h) for x, h in op] for op in g['holes']])
    return first, second


def ramp_feet(segs):
    """Where two flat plinth runs along one wall line meet at a small step in the floor, the lower run climbs to the
    higher at 45 degrees over the last metres before the step (notes 15, 16: no dropped band at a landing's edge),
    whether or not the two runs are pieces of the same wall."""
    out = list(segs)
    changed = True
    while changed:
        changed = False
        out.sort(key=lambda g: (g['i'], g['s']))
        for j in range(len(out) - 1):
            g, h = out[j], out[j + 1]
            if g['i'] != h['i'] or math.dist(g['b'], h['a']) > 1e-4 or abs(g['face'] - h['face']) > 1e-6:
                continue
            if abs(g['h_a'] - g['h_b']) > 1e-6 or abs(h['h_a'] - h['h_b']) > 1e-6:
                continue
            dh = h['h_a'] - g['h_b']
            if not 1e-6 < abs(dh) <= STEP_DIAG + 1e-6:
                continue
            if dh > 0:                                   # the step goes up: the end of g climbs
                Lg = math.dist(g['a'], g['b'])
                cut = max(0.0, Lg - dh)
                if cut > 1e-3:
                    first, ramp = split_foot(g, cut)
                    out[j:j + 1] = [first, ramp]
                else:
                    ramp = g
                ramp['h_a'], ramp['h_b'] = ramp['h_a'], h['h_a']
                ramp['floor'] = min(ramp['h_a'], ramp['h_b'])
            else:                                        # the step goes down: the start of h descends
                Lh = math.dist(h['a'], h['b'])
                cut = min(Lh, -dh)
                if Lh - cut > 1e-3:
                    ramp, rest = split_foot(h, cut)
                    out[j + 1:j + 2] = [ramp, rest]
                else:
                    ramp = h
                ramp['h_a'], ramp['h_b'] = g['h_b'], ramp['h_b']
                ramp['floor'] = min(ramp['h_a'], ramp['h_b'])
            changed = True
            break
    return out


def build_feet():
    """Every room's plinth, joined at its corners: each face line meets the next one's, whatever the walls behind."""
    for key in list(FEET):
        FEET[key] = ramp_feet(FEET[key])
    for key, segs in FEET.items():
        r = ROOMS[key]
        look(r['look'])
        m.group(f'{key} walls')
        segs.sort(key=lambda g: (g['i'], g['s']))
        for j, g in enumerate(segs):
            h = segs[(j + 1) % len(segs)]
            if h is g or math.dist(g['b'], h['a']) > 1e-4:
                continue
            d1 = (g['b'][0] - g['a'][0], g['b'][1] - g['a'][1])
            d2 = (h['b'][0] - h['a'][0], h['b'][1] - h['a'][1])
            if abs(d1[0] * d2[1] - d1[1] * d2[0]) < 1e-6 * math.hypot(*d1) * math.hypot(*d2):
                continue
            for og, oh in ((g['face'] - FOOT, h['face'] - FOOT), (g['face'], h['face'])):
                x, y = meet(g['a'], g['b'], og, h['a'], h['b'], oh)
                g['sb'][round(og, 4)], h['sa'][round(oh, 4)] = x, y
        poly = r['poly']
        n_p = len(poly)
        for g in segs:
            for end in ('a', 'b'):
                key_s = 'sa' if end == 'a' else 'sb'
                if g[key_s]:
                    continue
                j = g['i'] if end == 'a' else (g['i'] + 1) % n_p
                if math.dist(g[end], poly[j]) > 1e-4:
                    continue
                # The neighbouring edge at this corner: the one before (for a start) or after (for an end).
                if end == 'a':
                    na, nb = poly[(g['i'] - 1) % n_p], poly[g['i']]
                    nf = edge_face(key, (g['i'] - 1) % n_p)
                else:
                    na, nb = poly[(g['i'] + 1) % n_p], poly[(g['i'] + 2) % n_p]
                    nf = edge_face(key, (g['i'] + 1) % n_p)
                d1 = (g['b'][0] - g['a'][0], g['b'][1] - g['a'][1])
                d2 = (nb[0] - na[0], nb[1] - na[1])
                if abs(d1[0] * d2[1] - d1[1] * d2[0]) < 1e-6 * math.hypot(*d1) * math.hypot(*d2):
                    continue
                if edge_open(key, na, nb):
                    # An open edge (a step down into the next room): the plinth stops short of the floor's edge, so
                    # its end is not on the plane of the floor slab's side.
                    for og in (g['face'] - FOOT, g['face']):
                        g[key_s][round(og, 4)] = -FOOT if end == 'b' else FOOT
                    continue
                for og in (g['face'] - FOOT, g['face']):
                    if end == 'b':
                        x, _ = meet(g['a'], g['b'], og, na, nb, nf)
                        g['sb'][round(og, 4)] = x
                    else:
                        _, y = meet(na, nb, nf, g['a'], g['b'], og)
                        g['sa'][round(og, 4)] = y
        for g in segs:
            Lg = math.dist(g['a'], g['b'])
            slope = (g['h_b'] - g['h_a']) / Lg
            wdir = ((g['b'][0] - g['a'][0]) / Lg, (g['b'][1] - g['a'][1]) / Lg)
            # The texture origin: the room's corner, at the height where this piece's band meets it (on a slope, the
            # band's height carried back along the slope), so a sloped band meets the flat bands at its ends.
            cx, cy = r['poly'][0]
            oh = g['h_a'] - F.FLOOR_T + slope * ((cx - g['a'][0]) * wdir[0] + (cy - g['a'][1]) * wdir[1])
            room_wall(g['a'], g['b'], g['floor'] - F.FLOOR_T, g['h_a'] + S.PLINTH_H, g['face'] - FOOT, g['face'],
                      top_tex(R('plinth'), R('plinth')), f'{key} plinth', openings=g['holes'],
                      origin=(cx, cy, oh), shifts={'a': g['sa'], 'b': g['sb']}, h1b=g['h_b'] + S.PLINTH_H,
                      uv_shear=((wdir[0], 0.0, -wdir[1]), slope) if abs(slope) > 1e-6 else None)
    m.ungroup()


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

    # The room face's offset from each edge. A wall a room shares is its own half inside the edge, so the rest of that
    # edge stands inside by the same amount and the face runs flat along the whole edge (user, 2026-09-27: no jut where
    # a shared wall meets an exterior one).
    for key, i in edges:
        edge_face(key, i)

    # Every wall piece of every room, with its face and outer offsets: an outside wall stands from the room face out to
    # WALL_T, or, on an edge the room partly shares, to +0.25 in line with the neighbour's half; a shared half stands
    # inside its edge and a gap half outside it. Consecutive pieces meeting at a corner are joined where their face lines
    # meet and where their outer lines meet, so walls of any kind and thickness meet exactly: no notch, no jut, no
    # overlap (user, 2026-09-27: notes 5 and 19). Outside walls also chain across rooms (the dock's north wall meeting the
    # truck bay's east wall).
    pieces = {}
    for (key, i), cuts in edges.items():
        poly = ROOMS[key]['poly']
        ea, eb = poly[i], poly[(i + 1) % len(poly)]
        EL = math.dist(ea, eb)
        face = edge_face(key, i)
        for s0, s1, other, kind in cuts:
            if other is not None and kind != 'gap' and frozenset((key, other)) in open_pairs:
                continue
            a = (ea[0] + (eb[0] - ea[0]) * s0 / EL, ea[1] + (eb[1] - ea[1]) * s0 / EL)
            b = (ea[0] + (eb[0] - ea[0]) * s1 / EL, ea[1] + (eb[1] - ea[1]) * s1 / EL)
            if other is None:
                f_o = (face, 0.25 if face < 0 else F.WALL_T)
            elif kind == 'gap':
                f_o = (0.0, F.WALL_T / 2)
            else:
                f_o = (-F.WALL_T / 2, 0.0)
            pieces[(key, i, round(s0, 6))] = dict(key=key, i=i, s0=s0, a=a, b=b, face=f_o[0], outer=f_o[1],
                                                  ext=other is None, sa={}, sb={})

    def join(e, f):
        d1 = (e['b'][0] - e['a'][0], e['b'][1] - e['a'][1])
        d2 = (f['b'][0] - f['a'][0], f['b'][1] - f['a'][1])
        th = math.atan2(d1[0] * d2[1] - d1[1] * d2[0], d1[0] * d2[0] + d1[1] * d2[1])
        if not math.radians(1) < abs(th) < math.radians(170):
            return
        x, y = meet(e['a'], e['b'], e['face'], f['a'], f['b'], f['face'])
        e['sb'][round(e['face'], 4)], f['sa'][round(f['face'], 4)] = x, y
        # A half wall's outer face is its edge line: it ends at its own corner, never past it into the next room's wall
        # (the pump room's east half at the hold's corner); the other piece's outer face meets that line.
        x, y = meet(e['a'], e['b'], e['outer'], f['a'], f['b'], f['outer'])
        e['sb'][round(e['outer'], 4)] = 0.0 if e['outer'] <= 1e-9 else x
        f['sa'][round(f['outer'], 4)] = 0.0 if f['outer'] <= 1e-9 else y

    by_room = {}
    for pc in pieces.values():
        by_room.setdefault(pc['key'], []).append(pc)
    followed = set()
    for key, pcs in by_room.items():
        pcs.sort(key=lambda pc: (pc['i'], pc['s0']))
        for j, e in enumerate(pcs):
            f = pcs[(j + 1) % len(pcs)]
            if f is not e and math.dist(e['b'], f['a']) < 1e-4:
                join(e, f)
                followed.add(id(e))
    start_at = {}
    for pc in pieces.values():
        if pc['ext']:
            start_at.setdefault((round(pc['a'][0], 4), round(pc['a'][1], 4)), []).append(pc)
    for e in pieces.values():
        if not e['ext'] or id(e) in followed:
            continue
        nxt = [f for f in start_at.get((round(e['b'][0], 4), round(e['b'][1], 4)), []) if f is not e and f['key'] != e['key']]
        if nxt:
            join(e, nxt[0])
    joints = pieces
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

    # A crawl running along under a wall: the wall stands on the crawl's roof, so its underside never lies on the crawl's
    # ceiling and flickers (the pipe gallery under the pump room's west wall, playtest 2026-09-27 note 10).
    crawl_roofs = []
    for c in CORRS:
        if c['prof'] == 'crawl':
            Wc, topc = corr_shell(c['prof'])
            for (pa, ha), (pb, hb) in zip(zip(c['path'], c['heights']), zip(c['path'][1:], c['heights'][1:])):
                if abs(ha - hb) < 1e-6:
                    crawl_roofs.append((pa, pb, Wc, ha + topc))

    def on_crawl(q, ux, uy, lo, hi):
        for qa, qb, Wc, roof in crawl_roofs:
            dx, dy = qb[0] - qa[0], qb[1] - qa[1]
            Ls = math.hypot(dx, dy)
            if Ls < 1e-6 or abs(ux * dy - uy * dx) > 1e-6 * Ls:
                continue
            if P.seg_dist(q, qa, qb) < Wc + F.WALL_T / 2 - 1e-6 and lo < roof - 1e-6 and roof < hi - 1e-6:
                return roof
        return None

    for (key, i), cuts in edges.items():
        r = ROOMS[key]
        poly = r['poly']
        ea, eb = poly[i], poly[(i + 1) % len(poly)]
        EL = math.dist(ea, eb)
        face = FACE_OFF[(key, i)]
        # One texture origin for the whole room, its first corner at its floor, so panel lines run level round every
        # wall whatever floor each edge stands on (playtest 2026-09-27 notes 6, 11, 16, 18).
        org = (poly[0][0], poly[0][1], r['floor'] - F.FLOOR_T)
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
                e = joints[(key, i, round(s0, 6))]
                # Other rooms at about this floor: an outside wall is clipped out of them (the pump room's wall in the
                # compressor room's corner, note 5). A room far above or below is airspace the wall may stand in.
                clip = [(pt_, lowest(o) - F.FLOOR_T, ceiling_max(o) + F.CEIL_T) for o in ROOMS.values()
                        if o is not r and overlap_area(o['poly'], r['poly']) < 1e-3 for pt_ in o['parts']]
                # What overlaps the wall's own footprint sets its top, 0.25 m at a time. A room stacked across the
                # edge caps it (the booth notch under Logistics) or, lying under this room, raises it to its roof
                # (Logistics' east wall stands to the Sorting Bay's ceiling, and faces the bay in the bay's look). A side
                # opening is left to the corridor.
                n_s = max(1, int(round(L / 0.25)))
                sig = []
                for k in range(n_s):
                    t = (k + 0.5) / n_s
                    q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                    if any(ov and ov[0] - 1e-6 <= (q[0] - oa[0]) * (ob[0] - oa[0]) / math.dist(oa, ob) + (q[1] - oa[1]) * (ob[1] - oa[1]) / math.dist(oa, ob) <= ov[1] + 1e-6
                           for oa, ob in sides for ov in [collinear_overlap(oa, ob, a, b)]):
                        sig.append((None, None, None))
                        continue
                    q_in = (q[0] + inward[0] * 0.3, q[1] + inward[1] * 0.3)
                    q_wall = (q[0] - inward[0] * F.WALL_T / 2, q[1] - inward[1] * F.WALL_T / 2)
                    if in_shell(q_wall, ux, uy, bottom, ceil_in + F.CEIL_T):
                        sig.append((None, None, None))
                        continue
                    top = ceil_in + F.CEIL_T
                    over = None
                    for o in ROOMS.values():
                        if o is r:
                            continue
                        # A room stacked above caps the wall over its floor AND under its own walls' footprint.
                        in_o = P.inside(q_wall, o['poly'])
                        near = lambda q_: P.inside(q_, o['poly']) or P.edge_dist(q_, o['poly']) < F.WALL_T - 1e-6
                        # Only where that room's floor or its own walls cover this wall's whole thickness (the booth
                        # under Logistics): a corner merely near it left slots up the wall (notes 9, 11).
                        pf = (q[0] - inward[0] * (face + 0.02), q[1] - inward[1] * (face + 0.02))
                        po = (q[0] - inward[0] * (e['outer'] - 0.02), q[1] - inward[1] * (e['outer'] - 0.02))
                        if covered_by(o, pf) and covered_by(o, po) and o['floor'] - F.FLOOR_T > bottom + 0.5:
                            top = min(top, o['floor'] - F.FLOOR_T)
                        elif in_o:
                            top = max(top, ceiling_at(o, q_wall) + F.CEIL_T)
                            over = o['key']
                    roof = on_crawl(q_wall, ux, uy, bottom, top)
                    sig.append((round(top, 4), round(roof if roof is not None else bottom, 4), over))
                m.group(f'{key} walls')
                runs, k0 = [], 0
                for k in range(1, n_s + 1):
                    if k == n_s or sig[k] != sig[k0]:
                        runs.append([k0, k, sig[k0]])
                        k0 = k
                # A sharp corner cuts a face line back; an end run shorter than that (the bit of wall that would have
                # stood in the neighbouring room) is taken into the next run.
                need_a = max([0.0] + list(e['sa'].values())) + 0.01
                need_b = max([0.0] + [-v for v in e['sb'].values()]) + 0.01
                for end, need in ((0, need_a), (-1, need_b)):
                    while len(runs) > 1 and (runs[end][1] - runs[end][0]) * L / n_s < need and runs[end + (1 if end == 0 else -1)][2][0] is not None:
                        nb = runs[end + (1 if end == 0 else -1)]
                        if end == 0:
                            nb[0] = runs[0][0]
                            runs.pop(0)
                        else:
                            nb[1] = runs[-1][1]
                            runs.pop()
                for k0, k, (top, bot, over) in runs:
                    if top is None:
                        continue
                    pa = (a[0] + (b[0] - a[0]) * k0 / n_s, a[1] + (b[1] - a[1]) * k0 / n_s)
                    pb = (a[0] + (b[0] - a[0]) * k / n_s, a[1] + (b[1] - a[1]) * k / n_s)
                    tex = R('wall')
                    if over is not None:
                        tout, onx, ony = f"looks/{ROOMS[over]['look']}/wall", uy, -ux
                        tex = (lambda tin, tout, onx, ony: lambda n_, c_: tout if n_[0] * onx - n_[2] * ony > 0.5 else tin)(tex, tout, onx, ony)
                    ops = wall_openings_k(pa, pb, 'room')
                    room_wall(pa, pb, bot, top, face, e['outer'], tex, f'{key} wall', openings=[op for op, _ in ops],
                              origin=org, shifts={'a': e['sa'] if k0 == 0 else {}, 'b': e['sb'] if k == n_s else {}},
                              inner_bottom=floor_in, clip=clip)
                    add_feet(r, i, pa, pb, face, ops)
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
                hf, ho, holes = 0.0, F.WALL_T / 2, wall_openings_k(a, b, 'room') + wall_openings_k(ao, bo, 'room')
            else:
                hf, ho, holes = -F.WALL_T / 2, 0.0, wall_openings_k(a, b, 'shared')
            pc = joints[(key, i, round(s0, 6))]
            room_wall(a, b, floor_in - F.FLOOR_T, ceil_in + F.CEIL_T, hf, ho, R('wall'), f'{key} wall',
                      openings=[op for op, _ in holes], origin=org, shifts={'a': pc['sa'], 'b': pc['sb']})
            add_feet(r, i, a, b, hf, holes)
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


RAIL_DROP = 0.6          # a drop at least this high gets a rail


def blocker_top(r, pt):
    """The top of the blocker standing at a plan point (inf for one that reaches the ceiling), or None."""
    for b_ in r['blockers']:
        if b_['name'] in F.ENTERABLE or not P.inside(pt, b_['poly']):
            continue
        h = blocker_height(b_['name'])
        if h == 'ceiling':
            return float('inf')
        c_ = (sum(q[0] for q in b_['poly']) / len(b_['poly']), sum(q[1] for q in b_['poly']) / len(b_['poly']))
        return level_floor(r, c_) + h
    return None


def edge_rails(r):
    """Rails wherever a platform, deck, pit or stair edge drops RAIL_DROP or more to the floor beside it, inside the room
    (or across an open edge to the next room). No rail where a wall, a blocker or a stair closes the edge, where a
    ladder or a corridor (the catwalk) leaves it, or at the dock edges between rooms, which stay open."""
    open_pairs = {frozenset(p_) for p_ in F.OPEN_EDGES}
    ladders = [lp for _, lp, _, _ in F.LADDERS]
    high_corrs = [(c, pa, pb, ha) for c in CORRS for (pa, ha), (pb, hb) in zip(zip(c['path'], c['heights']),
                                                                               zip(c['path'][1:], c['heights'][1:]))]

    def height_at(pt):
        """Floor height at a plan point in this room (decks counted), or an open neighbour's; None for a wall."""
        if P.inside(pt, r['poly']) and P.edge_dist(pt, r['poly']) > 0.05:
            deck = level_floor(r, pt, decks=True)
            bt = blocker_top(r, pt)
            if bt is not None and bt > deck - 0.05:
                return None                       # a blocker closes this side (not one standing under a deck)
            for br in r['bridges']:
                if P.inside(pt, br['poly']):
                    return br['h']                # a bridge carries the floor across (the pump bridge over the pit)
            return level_floor(r, pt, decks=True)
        for o in ROOMS.values():
            if o is not r and frozenset((r['key'], o['key'])) in open_pairs and P.inside(pt, o['poly']):
                return level_floor(o, pt, decks=True)
        return None

    polys = [lv['poly'] for lv in r['levels'] if lv['kind'] in ('platform', 'deck', 'pit')]
    polys += [st['poly'] for st in r['stairs']]
    for poly in polys:
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            L = math.dist(a, b)
            ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            inward = (-uy, ux)
            steps = max(1, int(L / 0.25))
            run = []                                # (point on the high side, its height) while the edge needs a rail

            def flush():
                if len(run) >= 2:
                    (p0, h0), (p1, h1) = run[0], run[-1]
                    rail(p0[0], p0[1], p1[0], p1[1], h0, h1, f"{r['key']} edge rail")
                run.clear()

            for k in range(steps + 1):
                t = k / steps
                q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                qi = (q[0] + inward[0] * 0.15, q[1] + inward[1] * 0.15)
                qo = (q[0] - inward[0] * 0.3, q[1] - inward[1] * 0.3)
                hi, ho = height_at(qi), height_at(qo)
                bo = blocker_top(r, qo)
                if ho is None and bo is not None and hi is not None and bo < hi - RAIL_DROP + 1e-6:
                    ho = bo                                 # a drop onto a machine's top: a rail, as over any drop
                blocked = hi is None or ho is None or abs(hi - ho) < RAIL_DROP \
                    or any(math.dist(q, lp) < 1.0 for lp in ladders)
                if not blocked:
                    top = max(hi, ho)
                    # Only where a corridor leaves across the edge (the floor beyond is the corridor's): a corridor that
                    # meets the room beside the edge (the jog corridor at the stair room's landing) leaves no gap.
                    blocked = any(P.seg_dist(qo, pa, pb) < corr_section(c['prof'])[0] + 0.05 and abs(ha - top) < 0.4
                                  for c, pa, pb, ha in high_corrs)
                if blocked:
                    flush()
                    continue
                side = 1.0 if hi > ho else -1.0     # the rail stands on the high side, 0.1 m in from the edge
                run.append(((q[0] + inward[0] * 0.1 * side, q[1] + inward[1] * 0.1 * side), max(hi, ho)))
            flush()


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


CONTAINER_LOOKS = ('concrete', 'warm', 'steel')


def container_tex(lk, lx, ly):
    """A container's faces: corrugated all round (its top and bottom too, note 6), the door at each end."""
    side, end = f'looks/{lk}/container', f'looks/{lk}/door'
    return lambda n_, c_: side if abs(n_[1]) > 0.5 else (end if abs(n_[0] * lx - n_[2] * ly) > 0.5 else side)


CASTING = 0.25          # a container's corner castings: it stands this high on them, and stacks leave this gap


def container_block(r, poly, bottom, top, tag):
    """Freight containers (user, 2026-09-27): a stack is several containers, not one block, each in a colour of its own,
    and the top row's last one is pulled out a metre toward the room, so the stack is not a box."""
    xs, ys = [p_[0] for p_ in poly], [p_[1] for p_ in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    along_x = (x1 - x0) >= (y1 - y0)
    lx, ly = (1.0, 0.0) if along_x else (0.0, 1.0)
    l0, l1 = (x0, x1) if along_x else (y0, y1)
    w0, w1 = (y0, y1) if along_x else (x0, x1)
    n_w = max(1, int(round((w1 - w0) / 2.2)))
    rows = max(1, int(round((top - bottom) / 2.6)))
    hrow = (top - bottom) / rows
    gap = CASTING                                  # stacks side by side stand apart (note 5)
    cw = (w1 - w0 - gap * (n_w - 1)) / n_w
    cx = sum(p_[0] for p_ in r['poly']) / len(r['poly'])
    cy = sum(p_[1] for p_ in r['poly']) / len(r['poly'])
    pull = 1.0 if ((cx if along_x else cy) > (l0 + l1) / 2) else -1.0
    seed = int(abs((x0 + x1) * 7 + (y0 + y1) * 13))
    k = 0
    def plan_rect(a0, a1, b0, b1):
        return P.ccw([(b0, a0), (b1, a0), (b1, a1), (b0, a1)] if along_x else [(a0, b0), (a1, b0), (a1, b1), (a0, b1)])

    for row in range(rows):
        for col in range(n_w):
            a0 = w0 + (cw + gap) * col
            a1 = a0 + cw
            b0, b1 = l0, l1
            if rows > 1 and row == rows - 1 and col == n_w - 1:
                b0, b1 = b0 + pull, b1 + pull
            lk = CONTAINER_LOOKS[(seed + k) % len(CONTAINER_LOOKS)]
            z0 = bottom + row * hrow
            # On four corner castings, so a stack reads as boxes with gaps between them (note 4).
            prism(plan_rect(a0, a1, b0, b1), z0 + CASTING, z0 + hrow, container_tex(lk, lx, ly), tag, tally='blocker')
            c_ = 0.3
            for ca0, ca1 in ((a0, a0 + c_), (a1 - c_, a1)):
                for cb0, cb1 in ((b0, b0 + c_), (b1 - c_, b1)):
                    prism(plan_rect(ca0, ca1, cb0, cb1), z0, z0 + CASTING, f'looks/{lk}/frame', tag + ' casting',
                          tally='blocker')
            k += 1


def hollow_blocker(poly, bottom, top, open_dir, tex, tag, t=0.15):
    """A blocker with a crawl inside (the conveyor platform): a lid and three sides, open at the end open_dir faces."""
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    prism(P.ccw([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), top - t, top, tex, tag + ' lid', tally='blocker')
    ox, oy = open_dir
    walls = []
    if ox == 0:
        walls += [(x0, y0, x0 + t, y1), (x1 - t, y0, x1, y1)]
        walls.append((x0, y0, x1, y0 + t) if oy > 0 else (x0, y1 - t, x1, y1))
    else:
        walls += [(x0, y0, x1, y0 + t), (x0, y1 - t, x1, y1)]
        walls.append((x0, y0 + t, x0 + t, y1 - t) if ox > 0 else (x1 - t, y0 + t, x1, y1 - t))
    for a0, b0, a1, b1 in walls:
        prism(P.ccw([(a0, b0), (a1, b0), (a1, b1), (a0, b1)]), bottom, top - t, tex, tag + ' side', tally='blocker')


def drawer_cabinet(poly, bottom, top, tex, tag):
    """The archive's drawer bank: a cabinet against the wall with one drawer niche in its front, which the drawer (an
    rb_door) closes. The niche is 0.6 m wide, 0.5 m tall, 0.45 m deep, its floor 0.6 m up."""
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)       # the front is x1, facing east
    cy = (y0 + y1) / 2
    n0, n1 = bottom + 0.6, bottom + 1.1
    back = x1 - 0.45
    for (a0, b0, a1, b1, h0, h1) in [(x0, y0, x1, y1, bottom, n0), (x0, y0, x1, y1, n1, top),
                                     (x0, y0, x1, cy - 0.3, n0, n1), (x0, cy + 0.3, x1, y1, n0, n1),
                                     (x0, cy - 0.3, back, cy + 0.3, n0, n1)]:
        prism(P.ccw([(a0, b0), (a1, b0), (a1, b1), (a0, b1)]), h0, h1, tex, tag, tally='blocker')


def build_blockers(r):
    look(r['look'])
    for bl in r['blockers']:
        poly, name = bl['poly'], bl['name']
        c = (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
        base = level_floor(r, c)
        on = next((lv for lv in r['levels'] if lv['name'] == F.BLOCKER_ON.get(next((k for k in F.BLOCKER_ON if k in name), ''))), None)
        if on is not None:
            base = on['h']                        # it stands on a raised level (the drawer bank in the archive)
        h = blocker_height(name)
        top = under_deck(r, poly, ceiling_at(r, c) if h == 'ceiling' else base + h) if on is None else base + h
        # Stood on the lowest floor under it (a machine at a step reaches the lower floor), never sunk through a slab.
        bottom = base if on is not None else \
            min([base] + [level_floor(r, (q[0] + (c[0] - q[0]) * 0.02, q[1] + (c[1] - q[1]) * 0.02)) for q in poly])
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
        if name in F.HOLLOW:
            hollow_blocker(poly, bottom, top, F.HOLLOW[name], tex, tag)
            continue
        if 'container' in name and 'ammo' not in name:
            container_block(r, poly, bottom, top, tag)
            continue
        if name == 'drawer bank':
            drawer_cabinet(poly, bottom, top, tex, tag)
            continue
        prism(poly, bottom, top, tex, tag, tally='blocker')
        if 'riser turning' in name:
            # The pipe turns into the wall at 2.3-2.7 m.
            east = 'east' in name
            x_wall = max(p[0] for p in r['poly']) if east else min(p[0] for p in r['poly'])
            x0 = c[0] if east else x_wall
            x1 = x_wall if east else c[0]
            prism([(x0, c[1] - 0.25), (x1, c[1] - 0.25), (x1, c[1] + 0.25), (x0, c[1] + 0.25)], base + 2.3, base + 2.9,
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
            top = ceiling_at(r, (x, y))
            prism(octo, top - F.PISTON['housing_depth'], top, R('pipe'), f"{r['key']} piston housing", tally='blocker')


def crossings(poly, y):
    """x where a horizontal line at y crosses a polygon's edges."""
    out = []
    for i in range(len(poly)):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
        if (y0 - y) * (y1 - y) < 0 or (y0 == y and y1 != y):
            out.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
    return out


def build_crane(r):
    """The overhead crane over the Sorting Bay: roof beams across the bay on the 4 m beat, running wall to wall under the
    ceiling, the rail under them, the trolley, and the container hanging on four cables from a spreader. All of it is
    overhead and out of reach."""
    (rx, ry0), (_, ry1) = next(pts for name, pts in F.OVERHEAD if name == 'crane rail')
    if not P.inside((rx, (ry0 + ry1) / 2), r['poly']):
        return
    cr = F.CRANE
    b0, b1 = cr['beam']
    hw = cr['beam_w'] / 2
    rooms = [r] + [o for o in ROOMS.values() if o is not r and P.inside((rx, ry1 + hw), o['poly'])]

    def span(y):
        """The beam's west and east ends on the line y: the room's walls, or where the ceiling drops below the beam."""
        room = next(o for o in rooms if P.inside((rx, y), o['poly']))
        xs = crossings(room['poly'], y)
        west, east = max(x for x in xs if x < rx), min(x for x in xs if x > rx)
        x = rx
        while x > west and ceiling_at(room, (x - 0.25, y)) >= b1 - 1e-6:
            x -= 0.25
        west = max(west, x)
        x = rx
        while x < east and ceiling_at(room, (x + 0.25, y)) >= b1 - 1e-6:
            x += 0.25
        return west, min(east, x)

    frame = top_tex(R('frame'), R('frame'))
    y = ry0
    while y <= ry1 + 1e-6:
        (wa, ea), (wb, eb) = span(y - hw), span(y + hw)
        w, e = max(wa, wb), min(ea, eb)
        prism(P.ccw([(w, y - hw), (e, y - hw), (e, y + hw), (w, y + hw)]), b0, b1, frame, f"{r['key']} crane beam",
              tally='crane')
        y += cr['pitch']
    r0, r1 = cr['rail']
    rw = cr['rail_w'] / 2
    prism(P.ccw([(rx - rw, ry0 - hw), (rx + rw, ry0 - hw), (rx + rw, ry1 + hw), (rx - rw, ry1 + hw)]), r0, r1, frame,
          f"{r['key']} crane rail", tally='crane')
    cont = next(poly for name, poly in F.OVERHEAD if name == 'hanging container')
    xs, ys = [q[0] for q in cont], [q[1] for q in cont]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cy = (y0 + y1) / 2
    t0, t1 = cr['trolley']
    prism(P.ccw([(rx - 0.45, cy - 1.2), (rx + 0.45, cy - 1.2), (rx + 0.45, cy + 1.2), (rx - 0.45, cy + 1.2)]), t0, t1,
          frame, f"{r['key']} crane trolley", tally='crane')
    c0, c1 = cr['container']
    prism(cont, c0, c1, container_tex('steel', 0.0, 1.0), f"{r['key']} hanging container", tally='crane')
    sp = c1 + cr['spreader']
    prism(P.ccw([(x0 + 0.15, y0 + 0.3), (x1 - 0.15, y0 + 0.3), (x1 - 0.15, y1 - 0.3), (x0 + 0.15, y1 - 0.3)]), c1, sp,
          frame, f"{r['key']} crane spreader", tally='crane')
    k = cr['cable'] / 2
    for cx in (rx - 0.3, rx + 0.3):
        for yy in (cy - 0.9, cy + 0.9):
            prism(P.ccw([(cx - k, yy - k), (cx + k, yy - k), (cx + k, yy + k), (cx - k, yy + k)]), sp, t0, R('frame'),
                  f"{r['key']} crane cable", tally='crane')


def build_patches(r):
    """Old burrows sealed with poured concrete (clues): a rough patch standing a little proud of a wall or a floor, in the
    concrete look, so its texture change has its own geometry."""
    ks = [1.0, 0.86, 0.95, 0.8, 0.97, 0.88, 1.0, 0.83, 0.92]
    for clue, (cx, cy), normal, h, rad, proud in F.PATCHES:
        if not P.inside(clue, r['poly']):
            continue
        ring = [(rad * k * math.cos(2 * math.pi * i / 9 + 0.3), rad * k * math.sin(2 * math.pi * i / 9 + 0.3))
                for i, k in enumerate(ks)]
        look('concrete')
        # Poured: the face is a little smaller than the base, so the edge slopes like a trowelled mound. Newer, paler
        # concrete than what it patches, one panel of it: the texture starts at the patch's corner, so no seam crosses it.
        if normal is None:
            pts = [(cx + u * f, cy + v * f, hh) for u, v in ring for hh, f in ((h, 1.0), (h + proud, 0.88))]
            org = GP(cx - rad, cy - rad, h)
        else:
            nx, ny = normal
            tx, ty = ny, -nx
            pts = [(cx + tx * u * f + nx * d, cy + ty * u * f + ny * d, h + v * f) for u, v in ring
                   for d, f in ((0.0, 1.0), (proud, 0.88))]
            org = GP(cx - abs(tx) * rad, cy - abs(ty) * rad, h - rad)
        hullp(pts, R('wall'), f"{r['key']} sealed burrow patch", tally='patch', uv_origin=org)
        look(r['look'])


def build_coolant_pumps(r):
    """The coolant pumps in the pump pit's channel (user, 2026-09-27): a housing standing in the coolant, two guide posts
    and a crossbeam for the plunger's head (the plunger itself is an rb_machine), and an outlet pipe rising from the
    housing, arching over the bridge and dropping into the top of the reactor opposite."""
    cp = F.COOLANT_PUMPS
    y = cp['y']
    if not P.inside((cp['xs'][0], y), r['poly']):
        return
    hx, hy = cp['half']
    h0, h1 = cp['housing']
    body = top_tex(R('machine_top'), R('machine_body'))
    for x in cp['xs']:
        prism(P.ccw([(x - hx, y - hy), (x + hx, y - hy), (x + hx, y + hy), (x - hx, y + hy)]), h0, h1, body,
              f"{r['key']} coolant pump housing", tally='blocker')
        pw = cp['post_w'] / 2
        b0, b1 = cp['beam']
        for sx in (-1, 1):
            px = x + sx * cp['posts']
            prism(P.ccw([(px - pw, y - pw), (px + pw, y - pw), (px + pw, y + pw), (px - pw, y + pw)]), h1, b0, R('frame'),
                  f"{r['key']} coolant pump post", tally='blocker')
        prism(P.ccw([(x - cp['posts'] - 0.12, y - 0.12), (x + cp['posts'] + 0.12, y - 0.12), (x + cp['posts'] + 0.12, y + 0.12),
                     (x - cp['posts'] - 0.12, y + 0.12)]), b0, b1, R('frame'), f"{r['key']} coolant pump beam", tally='blocker')
        # The outlet: up from the housing, north over the bridge, down into the reactor's top.
        reactor = next(b_ for b_ in r['blockers'] if b_['name'] == 'pump' and P.inside((x, cp['reactor_y']), b_['poly']))
        rc = (sum(q[0] for q in reactor['poly']) / len(reactor['poly']), sum(q[1] for q in reactor['poly']) / len(reactor['poly']))
        r_top = level_floor(r, rc) + blocker_height('pump')
        px, pr = x + cp['pipe_dx'], cp['pipe_r']
        p0, p1 = cp['pipe_h']
        ring = lambda cx, cy: [(cx + pr * math.cos(k * math.pi / 4 + math.pi / 8), cy + pr * math.sin(k * math.pi / 4 + math.pi / 8))
                               for k in range(8)]
        prism(ring(px, y), h1 - 0.1, p1 - 0.05, R('pipe'), f"{r['key']} coolant pipe riser", tally='blocker')
        prism(P.ccw([(px - pr, y - pr), (px + pr, y - pr), (px + pr, cp['reactor_y'] + pr), (px - pr, cp['reactor_y'] + pr)]),
              p0, p1, R('pipe'), f"{r['key']} coolant pipe", tally='blocker')
        prism(ring(px, cp['reactor_y']), r_top - 0.1, p1 - 0.05, R('pipe'), f"{r['key']} coolant pipe drop", tally='blocker')


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
        side = rule.get('side')
        if 'at' in rule:
            name, centre, normal, h0, owner = prefix, rule['at'], rule['facing'], rule['floor'], ROOMS[rule['room']]
            kind, leaf_h = None, rule['height']
        else:
            name, door_pt, kind = next(d for d in F.DOORS if d[0].startswith(prefix))
            centre, normal, h0, leaf_h, owner = door_placement(door_pt, kind, side)
        needs = rule.get('needs', '')
        props = {'origin': origin(centre[0], centre[1], h0), 'id': rule['id'], 'opens': rule['opens'], 'needs': needs,
                 'needs_text': ';'.join(f'{f}={F.FLAG_TEXT[f]}' for f in needs.split(',') if f),
                 'side': fmt(side) if side else '0 0', 'latch': rule.get('latch', 0),
                 'events': rule.get('events', rule['id']), 'style': rule.get('style', 'rise'),
                 'width': B._fmt(rule['width'] if kind is None else F.DOOR_SIZE[kind][0]),
                 'height': B._fmt(round(leaf_h, 4)), 'facing': fmt(normal), 'look': owner['look'], 'label': name,
                 'lamp_depth': B._fmt(rule.get('lamp_depth', 0.27))}
        m.entity('rb_door', props, group=f"{owner['key']} {owner['name']}")
        count += 1
    for sid, name, sp, h, facing, mount, what in F.KIT_SWITCHES:
        room = room_at((sp[0] + facing[0] * 0.3, sp[1] + facing[1] * 0.3))
        props = {'origin': origin(sp[0], sp[1], h), 'id': sid, 'sends': what.get('sends', ''), 'sets': what.get('sets', ''),
                 'once': what.get('once', 1), 'effect': what.get('effect', ''), 'mount': mount,
                 'notice': what.get('notice', ''), 'facing': fmt(facing), 'look': room['look'], 'label': name}
        if 'prompt' in what:
            props['prompt'] = what['prompt']
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
    for name, (x, y), rad, kind in F.MOVING:
        if kind != 'piston':
            continue
        room = room_at((x, y))
        machine = next(b for b in room['blockers'] if P.inside((x, y), b['poly']))
        top = level_floor(room, (x, y)) + blocker_height(machine['name'])
        pi = F.PISTON
        m.entity('rb_machine', {'origin': origin(x, y, top), 'id': 'PISTON', 'kind': 'piston',
                                'radius': B._fmt(pi['radius']), 'stroke': B._fmt(pi['stroke']),
                                'period': B._fmt(pi['period']),
                                'housing': B._fmt(round(ceiling_at(room, (x, y)) - pi['housing_depth'] - top, 4)),
                                'ceiling': B._fmt(round(ceiling_at(room, (x, y)) - top, 4)),
                                'look': room['look']}, group=f"{room['key']} {room['name']}")
        count += 1
    cp = F.COOLANT_PUMPS
    for k, x in enumerate(cp['xs']):
        room = room_at((x, cp['y']))
        m.entity('rb_machine', {'origin': origin(x, cp['y'], cp['housing'][1]), 'id': f'COOLANT_PUMP{k + 1}', 'kind': 'plunger',
                                'low': B._fmt(cp['low']), 'stroke': B._fmt(cp['stroke']), 'period': B._fmt(cp['period']),
                                'phase': B._fmt(round(k / len(cp['xs']), 4)), 'facing': '0 1', 'look': room['look']},
                 group=f"{room['key']} {room['name']}")
        count += 1
    for k, (name, pt) in enumerate(F.DAMAGE):
        c, pa, pb, ha, hb = next((c, pa, pb, ha, hb) for c in CORRS
                                 for (pa, ha), (pb, hb) in zip(zip(c['path'], c['heights']), zip(c['path'][1:], c['heights'][1:]))
                                 if P.seg_dist(pt, pa, pb) < 0.5)
        L = math.dist(pa, pb)
        t = ((pt[0] - pa[0]) * (pb[0] - pa[0]) + (pt[1] - pa[1]) * (pb[1] - pa[1])) / (L * L)
        h = ha + (hb - ha) * t + corr_section(c['prof'])[1]
        m.entity('rb_machine', {'origin': origin(pt[0], pt[1], h), 'id': f'FITTING{k + 1}', 'kind': 'fitting',
                                # It hangs across the corridor, so the approach sees its length, not its end.
                                'facing': fmt(((pb[1] - pa[1]) / L, -(pb[0] - pa[0]) / L)), 'look': c['look']},
                 group=f"{c['key']} {c['name']}")
        count += 1
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
        # On a wall with a plinth, the ladder stands out clear of it and the plinth runs on behind (note 19); it steps
        # the climber off at the top to the same place as before.
        pull = 0.0
        if any(pulled_ladder((x, y), lo, g['a'], g['b'], g['face'], g['floor']) for segs in FEET.values() for g in segs):
            pull = LADDER_PULL
        x, y = x - fx * pull, y - fy * pull
        o = B.to_map(G(x, lo, y))
        m.entity('rb_ladder', {'origin': ' '.join(B._fmt(v) for v in o), 'top': B._fmt(hi), 'facing': f'{fx} {fy}',
                               'step': B._fmt(0.8 + pull), 'label': name}, group=f'{key} {ROOMS[key]["name"]}')


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
            # Where the corridor meets a room (a door or an open mouth) its walls, ceiling and ribs stop at the wall's
            # outer face; only the floor runs on under the wall to the room face, as the threshold, and a frame shaped
            # like the corridor's rib fills the wall and stands proud of the room face.
            ends = [None, None]
            mid_in = prof == 'catwalk' and in_any_room((a[0] + d[0] * (u0 + u1) / 2, a[1] + d[1] * (u0 + u1) / 2), 0.05)
            if not mid_in:
                ends = [mouth_for(c, (a[0] + d[0] * L * t_end, a[1] + d[1] * L * t_end)) for t_end in (t0, t1)]
            trims = [F.WALL_T / mo['sin'] if mo is not None else 0.0 for mo in ends]
            wu0, wu1 = u0 + trims[0], u1 - trims[1]
            for k_end, mo in enumerate(ends):
                if mo is not None:
                    u_end = u0 if k_end == 0 else u1
                    lo_, hi_ = build_mouth(c, mo, a, d, u_end, ha + (hb - ha) * u_end / L)
                    c.setdefault('cuts', []).append((s0[i] + lo_ - 0.25, s0[i] + hi_ + 0.25))

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
            ox, oy, _ = pt(u0, -1.0, 0.0)
            org = GP(ox, oy, min(heights))
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
                    while k * F.DUCT_RIB_PITCH < (u1 - u0) - 1.0:
                        u = u0 + k * F.DUCT_RIB_PITCH
                        for poly in ([(hw_clear - 0.06, 0.0), (hw_clear, 0.0), (hw_clear, h_clear), (hw_clear - 0.06, h_clear)],
                                     [(-hw_clear, 0.0), (-hw_clear + 0.06, 0.0), (-hw_clear + 0.06, h_clear), (-hw_clear, h_clear)],
                                     [(-hw_clear, h_clear - 0.06), (hw_clear, h_clear - 0.06), (hw_clear, h_clear), (-hw_clear, h_clear)]):
                            hullp([pt(uu, v, h) for v, h in poly for uu in (u - 0.05, u + 0.05)], R('frame'),
                                  f"{c['key']} rib", tally='rib')
                        k += 1
    # A crawl that ends against nothing (the girder's west end in the pit) is closed with a cap.
    if F.CRAWL_CAPS.get(c['key']) == 'start':
        (pa, ha), (pb, _) = (path[0], heights[0]), (path[1], heights[1])
        L = math.dist(pa, pb)
        dx, dy = (pb[0] - pa[0]) / L, (pb[1] - pa[1]) / L
        W, top = corr_shell(prof)
        nx, ny = -dy, dx
        a0, a1 = (pa[0] - dx * 0.25, pa[1] - dy * 0.25), pa
        prism(P.ccw([(a0[0] + nx * W, a0[1] + ny * W), (a1[0] + nx * W, a1[1] + ny * W), (a1[0] - nx * W, a1[1] - ny * W),
                     (a0[0] - nx * W, a0[1] - ny * W)]), ha - F.FLOOR_T, ha + top, R('wall'), f"{c['key']} end cap",
              tally='corridor')
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
def window_frames():
    """A frame round every window (user, 2026-09-27: the wall's pattern stopped dead at the cut): a 0.15 m border
    standing proud of both faces and 5 cm into the opening, so the change at the opening sits on geometry."""
    for name, pt, kind in F.DOORS:
        if kind != 'window':
            continue
        hit = next(((k, j) for k, r in ROOMS.items() for j in range(len(r['poly']))
                    if P.seg_dist(pt, r['poly'][j], r['poly'][(j + 1) % len(r['poly'])]) < 0.1), None)
        if hit is None:
            continue
        key, i = hit
        r = ROOMS[key]
        a, b = r['poly'][i], r['poly'][(i + 1) % len(r['poly'])]
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        nx, ny = uy, -ux
        w, hh = F.DOOR_SIZE[kind]
        h0 = door_floor(pt, (nx, ny)) + F.WINDOW_SILL
        h1 = h0 + hh
        sc = (pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy
        o0, o1 = edge_face(key, i) - 0.1, F.WALL_T + 0.1
        fr, inset = 0.15, 0.05
        bars = [(sc - w / 2 - fr, sc - w / 2 + inset, h0 - fr, h1 + fr), (sc + w / 2 - inset, sc + w / 2 + fr, h0 - fr, h1 + fr),
                (sc - w / 2 + inset, sc + w / 2 - inset, h1 - inset, h1 + fr), (sc - w / 2 + inset, sc + w / 2 - inset, h0 - fr, h0 + inset)]
        look(r['look'])
        m.group(f'{key} walls')
        for s0_, s1_, lo, hi in bars:
            quad = [(a[0] + ux * s_ + nx * o, a[1] + uy * s_ + ny * o) for s_, o in ((s0_, o0), (s1_, o0), (s1_, o1), (s0_, o1))]
            prism(P.ccw(quad), lo, hi, R('frame'), f'{key} window frame', tally='wall')
        m.ungroup()


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
        if 'roll door' in name:
            # A roll door (note 10): a corrugated curtain in a frame, with the roller's housing over it.
            j = min(range(len(poly)), key=lambda j_: P.seg_dist(pt, poly[j_], poly[(j_ + 1) % len(poly)]))
            f0 = -edge_face(key, j)                                  # the room face, inward from the edge line

            def slab(s0_, s1_, d0, d1, h0_, h1_, tex_, nm):
                q = [(pt[0] + ux * s_ + inward[0] * d_, pt[1] + uy * s_ + inward[1] * d_)
                     for s_, d_ in ((s0_, d0), (s1_, d0), (s1_, d1), (s0_, d1))]
                prism(P.ccw(q), h0_, h1_, tex_, nm, tally='door')
            curtain = lambda n_, c_: R('container') if abs(n_[0] * inward[0] - n_[2] * inward[1]) > 0.5 else R('frame')
            slab(-w / 2, w / 2, f0, f0 + 0.1, fl, fl + hh, curtain, f'{name} (sealed) curtain')
            for sg in (-1, 1):
                slab(sg * w / 2, sg * (w / 2 + 0.3), f0, f0 + 0.3, fl, fl + hh, R('frame'), f'{name} (sealed) jamb')
            slab(-w / 2 - 0.3, w / 2 + 0.3, f0, f0 + 0.5, fl + hh, fl + hh + 0.6, R('machine_body'), f'{name} (sealed) housing')
            m.ungroup()
            continue
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
    if not samples:
        # A room too small for the sampling grid (the cable vault) still gets one light, at its middle.
        cx = sum(p_[0] for p_ in r['poly']) / len(r['poly'])
        cy = sum(p_[1] for p_ in r['poly']) / len(r['poly'])
        top = ceiling_at(r, (cx, cy))
        # A room's full energy blows out walls a metre away: a small room gets a small light.
        return [(cx, cy, r['floor'] + min(3.6, top - r['floor'] - 0.4))], energy * 0.3, 5.0, shadow
    overhead = [poly for name, poly in F.OVERHEAD if name == 'hanging container']
    candidates = [i for i, sm in enumerate(samples)
                  if not any(P.inside((sm[0], sm[1]), o) or P.edge_dist((sm[0], sm[1]), o) < 0.75 for o in overhead)]
    uncovered = set(range(len(samples)))
    placed = []
    while uncovered:
        best = max(candidates, key=lambda i: len(cover[i] & uncovered))
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
    for name, (x, y), h, energy, rng, key in F.SOFT_LIGHTS:
        owner = ROOMS.get(key) or next(c for c in CORRS if c['key'] == key)
        count += light_entity(x, y, h, energy, rng, False, f"{owner['key']} {owner['name']}")
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
        moved = False
        while s < total:
            acc = 0.0
            for (p, hp), (q, hq) in zip(zip(c['path'], c['heights']), zip(c['path'][1:], c['heights'][1:])):
                L = math.dist(p, q)
                if acc + L >= s:
                    t = (s - acc) / L
                    x, y, h = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, hp + (hq - hp) * t
                    break
                acc += L
            if any(math.dist((x, y), dd) < 1.5 for _, dd in F.DAMAGE) and not moved:
                # The torn-loose fitting hangs here, dead: its light moves 2 m on down the corridor instead.
                s += 2.0
                moved = True
                continue
            moved = False
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
    for name, pts in list(F.ROUTES.items()) + list(F.SECRET_ROUTES.items()):
        rname = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
        oneway = 1 if name in F.SECRET_ROUTES or any(F.xy(p) == (10.8, 45.75) for p in pts) else 0
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
    edge_rails(r)
    for _, pts in F.RAILINGS:
        if P.inside(pts[0], r['poly']) or P.edge_dist(pts[0], r['poly']) < 0.05:
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                cx_, cy_ = sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)
                ia = (xa + math.copysign(0.1, cx_ - xa), ya + math.copysign(0.1, cy_ - ya))   # 0.1 m inside the enclosure
                ib = (xb + math.copysign(0.1, cx_ - xb), yb + math.copysign(0.1, cy_ - yb))
                h_ = level_floor(r, ((xa + xb) / 2 + (0.3 if cx_ > (xa + xb) / 2 else -0.3), (ya + yb) / 2 + (0.3 if cy_ > (ya + yb) / 2 else -0.3)))
                rail(ia[0], ia[1], ib[0], ib[1], h_, h_, f"{r['key']} railing")
    build_crane(r)
    build_patches(r)
    build_coolant_pumps(r)
    m.ungroup()
build_walls()
build_feet()
for c in CORRS:
    build_corridor(c)
sealed_doors()
window_frames()
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
