"""Generate the kit lab K-01 source map from tools/kit_lab.py.

    python tools/bootstrap-kit-lab.py [--overwrite]

Once written, the .map is the editable source (TrenchBroom). This bootstrap
is never part of a normal rebuild, and it refuses to overwrite an existing map
unless --overwrite is passed. Every piece is its own TrenchBroom group so it
can be moved or edited by hand.

Plan coordinates (x east, y north) map to Godot as (x, height, -y).
"""
from pathlib import Path
import math
import random
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import brushkit as B
import kit_lab as K
import style_lab as S

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'RedBreach/maps/kit_lab_01.map'
if MAP.exists() and '--overwrite' not in sys.argv:
    raise SystemExit('Map already exists. Edit it in TrenchBroom, or pass --overwrite to regenerate.')
K.check()
S.check()

import json
CATALOG = json.loads((ROOT / 'docs/texture-catalog.json').read_text())


def tex_size(texture):
    _, look_name, role = texture.split('/')
    image, _ = S.look_texture(S.LOOKS[look_name][role])
    return CATALOG[image]['size']


def is_feature(texture):
    return texture.startswith('looks/') and texture.split('/')[2] in S.FIT_ROLES


def tile_m(role):
    """One texture repeat of ROLE in the current look, in metres."""
    return tex_size(R(role))[0] * S.ROLE_SCALE.get(role, 1.0) / 32.0


def GP(x, y, h):
    """Plan point -> Godot point, for texture origins."""
    return (x, h, -y)


def GD(dx, dy):
    """Plan direction -> Godot direction."""
    return (dx, 0.0, -dy)


# Texture alignment (user rule, 2026-09-25): seams sit on geometry. Floors and
# ceilings are centred on a corridor and follow it; wall panels start at a rib
# station and at each segment's bottom edge; rooms start at their corners.
m = B.Map(textures=[f'looks/{k}' for k in S.LOOKS], tex_size=tex_size, fit=is_feature)
LOOK = 'steel'
SC = S.role_scale
W = S.SHELL_X


def R(role):
    return f'looks/{LOOK}/{role}'


def look(name):
    global LOOK
    LOOK = name


def G(x, h, y):
    """Plan (x, y) at height h -> Godot (x, h, -y)."""
    return (x, h, -y)


def hullp(pts, tex, name, **kw):
    """Hull of plan points (x, y, h)."""
    return m.hull([G(x, h, y) for x, y, h in pts], tex, name, scale=SC, **kw)


def boxp(x0, x1, y0, y1, h0, h1, tex, name, **kw):
    return hullp([(x, y, h) for x in (x0, x1) for y in (y0, y1) for h in (h0, h1)], tex, name, **kw)


def clip_poly(poly, half_planes):
    """Sutherland-Hodgman: keep points with a*x + b*y <= c for each (a, b, c)."""
    out = list(poly)
    for a, b, c in half_planes:
        if not out:
            break
        src, out = out, []
        for i, p in enumerate(src):
            q = src[(i + 1) % len(src)]
            fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
            if fp <= 1e-9:
                out.append(p)
            if (fp < -1e-9 < fq) or (fq < -1e-9 < fp):
                t = fp / (fp - fq)
                out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


# --- corridor runs ------------------------------------------------------------
def run(key):
    spec = K.RUNS[key]
    look(spec['look'])
    prof = spec['profile']
    segs = S.PROFILES[prof]['segments']
    ch = S.ceil_half(prof)
    path, heights = spec['path'], spec['heights']
    n = len(path)
    stair = spec.get('stair')
    m.group(f'Run {key} ({prof}, {LOOK})')

    dirs, lens = [], []
    for i in range(n - 1):
        dx, dy = path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]
        L = math.hypot(dx, dy)
        dirs.append((dx / L, dy / L)); lens.append(L)
    turn = [0.0] * n                       # signed turn at each vertex, CCW positive
    for i in range(1, n - 1):
        a, b = dirs[i - 1], dirs[i]
        turn[i] = math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1])
    s0 = [0.0]
    for L in lens:
        s0.append(s0[-1] + L)

    def frame(i):
        d = dirs[i]
        nl = (-d[1], d[0])                 # plan left
        a = path[i]
        ha, hb = heights[i], heights[i + 1]
        L = lens[i]
        t_in, t_out = math.tan(turn[i] / 2), math.tan(turn[i + 1] / 2)

        def pt(u, v, h):
            x = a[0] + d[0] * u + nl[0] * v
            y = a[1] + d[1] * u + nl[1] * v
            return (x, y, ha + (hb - ha) * u / L + h)

        def ends(v):
            return v * t_in, L - v * t_out
        return pt, ends, L

    def prism(i, poly, tex, name, u_range=None, **kw):
        pt, ends, L = frame(i)
        pts = []
        for v, h in poly:
            u0, u1 = ends(v) if u_range is None else u_range
            pts += [pt(u0, v, h), pt(u1, v, h)]
        hullp(pts, tex, name, **kw)

    for i in range(n - 1):
        flight = stair is not None and i == stair[0]
        pt, ends, L = frame(i)
        run_u = GD(*dirs[i])
        # The first rib station in this segment is the U origin for its walls,
        # so panel seams fall behind ribs on the 4 m beat.
        in_seg = [st - s0[i] for st in spec['ribs'] if s0[i] <= st < s0[i] + L]
        u_org = in_seg[0] if in_seg else 0.0
        # Floor: a slab, except on the flight, where steps carry the floor.
        # Centred: a whole tile either side of the centreline.
        if not flight:
            fo = pt(0.0, -tile_m('floor') / 2, 0.0)
            prism(i, [(-W, -0.5), (W, -0.5), (W, 0.0), (-W, 0.0)], R('floor'), f'{key} floor {i}', tally='shell',
                  uv_origin=GP(*fo), uv_u=run_u)
        co = pt(0.0, -tile_m('ceiling') / 2, S.CEIL_Y)
        prism(i, [(-W, S.CEIL_Y), (W, S.CEIL_Y), (W, S.SHELL_TOP), (-W, S.SHELL_TOP)], R('ceiling'), f'{key} ceiling {i}',
              tally='shell', uv_origin=GP(*co), uv_u=run_u)
        for side in (1, -1):
            for (xa, ya), (xb, yb), role in segs:
                poly = [(side * xa, ya), (side * W, ya), (side * W, yb), (side * xb, yb)]
                org = pt(u_org, side * xa, ya)
                kw = {'uv_origin': GP(*org)}
                if role == 'plinth':
                    foot = pt(0, side * xa, 0)
                    kw['anchor'] = (GP(*foot), 64.0)
                prism(i, poly, R(role), f'{key} {role} {i}', tally='shell', **kw)
        if flight:
            # Steps: each a solid block from the lower landing's floor to its
            # tread, full shell width so the walls always sit on something.
            risers = int(round((heights[i + 1] - heights[i]) / K.RISER))
            for k in range(risers):
                u0, u1 = k * K.TREAD, (k + 1) * K.TREAD
                top = heights[i] + (k + 1) * K.RISER
                corners = []
                for u in (u0, u1):
                    for v in (-W, W):
                        x = path[i][0] + dirs[i][0] * u - dirs[i][1] * v
                        y = path[i][1] + dirs[i][1] * u + dirs[i][0] * v
                        corners += [(x, y, heights[i] - 0.5), (x, y, top)]
                # Treads are floor; risers and step ends are the riser texture.
                tread_org = GP(*pt(0.0, -tile_m('floor') / 2, 0.0))
                hullp(corners, lambda n_, c_: R('floor') if n_[1] > 0.5 else R('riser'), f'{key} step {k}',
                      tally='stair', uv_origin=tread_org, uv_u=GD(*dirs[i]))
        if heights[i] > 0 and not flight:
            # A raised landing stands on solid fill down to the ground.
            prism(i, [(-W, -0.5 - heights[i]), (W, -0.5 - heights[i]), (W, -0.5), (-W, -0.5)], R('floor'), f'{key} landing fill {i}', tally='stair')

    # Ribs. The foot drops straight to the floor, flush with the rib above:
    # its inner face is the first above-plinth segment's start, less RIB_D.
    main = [sg for sg in segs if sg[2] != 'plinth']
    foot_x = main[0][0][0] - S.RIB_D
    plinth_top = main[0][0][1]
    fallen = spec.get('fallen')
    stations = list(spec['ribs']) + ([fallen] if fallen else [])
    for st in stations:
        i = max(j for j in range(n - 1) if s0[j] <= st + 1e-9)
        u = st - s0[i]
        pt, ends, L = frame(i)
        if st == fallen:
            continue                      # built as debris instead
        ur = (u - S.RIB_DEPTH / 2, u + S.RIB_DEPTH / 2)
        rorg = GP(*pt(ur[0], 0.0, 0.0))
        for side in (1, -1):
            prism(i, [(side * foot_x, -0.25), (side * W, -0.25), (side * W, plinth_top), (side * foot_x, plinth_top)],
                  R('rib'), f'{key} rib foot {st:.1f}', u_range=ur, tally='rib', uv_origin=rorg)
            for (xa, ya), (xb, yb), role in main:
                prism(i, [(side * (xa - S.RIB_D), ya), (side * xa, ya), (side * xb, yb), (side * (xb - S.RIB_D), yb)],
                      R('rib'), f'{key} rib {st:.1f}', u_range=ur, tally='rib', uv_origin=rorg)
        prism(i, [(-ch, S.CEIL_Y - S.RIB_D), (ch, S.CEIL_Y - S.RIB_D), (ch, S.CEIL_Y), (-ch, S.CEIL_Y)],
              R('rib'), f'{key} rib beam {st:.1f}', u_range=ur, tally='rib', uv_origin=rorg)
    m.ungroup()
    return frame, s0, dirs


# --- bulkheads and door frames -------------------------------------------------
def bulkhead(name, c, d, floor, kind):
    """c: centre of the frame's ROOM-side plane (plan); d: unit plan direction into the room."""
    d = (float(d[0]), float(d[1]))
    nl = (-d[1], d[0])
    door = kind in K.DOOR_OPENING
    if door:
        oh, ot = K.DOOR_OPENING[kind]
        ck = 0.0
        u0, u1 = -K.DOOR_DEPTH, 0.0
    else:
        oh, ot, ck = S.OPENING_HALF, S.OPENING_TOP, S.OPENING_CHAMFER
        u0, u1 = -S.BULKHEAD_LEN, S.FRAME_PROUD

    def P(u, v, h):
        return (c[0] + d[0] * u + nl[0] * v, c[1] + d[1] * u + nl[1] * v, floor + h)

    def tex(n, cen):
        nd = n[0] * d[0] + n[2] * -d[1]
        if abs(nd) > 0.5:
            return R('bulkhead')
        x, h, y = cen[0], cen[1] - floor, -cen[2]
        v = (x - c[0]) * nl[0] + (y - c[1]) * nl[1]
        return R('frame') if abs(v) <= oh + 1e-3 and h <= ot + 1e-3 else R('bulkhead')

    borg = GP(*P(u1, -W, 0.0))

    def piece(poly, nm):
        hullp([P(u, v, h) for v, h in poly for u in (u0, u1)], tex, f'{name} {nm}', tally='bulkhead', uv_origin=borg)
    m.group(name)
    for s in (1, -1):
        piece([(s * oh, 0), (s * W, 0), (s * W, S.SHELL_TOP), (s * oh, S.SHELL_TOP)], 'jamb')
        if ck > 0:
            piece([(s * oh, ot - ck), (s * oh, ot), (s * (oh - ck), ot)], 'chamfer')
    piece([(-oh, ot), (oh, ot), (oh, S.SHELL_TOP), (-oh, S.SHELL_TOP)], 'lintel')
    # Floor under the frame, so the opening has a floor at every height.
    hullp([P(u, v, h) for v in (-W, W) for h in (-0.5 - floor, 0.0) for u in (u0, u1)], R('floor'), f'{name} sill',
          tally='bulkhead', uv_origin=GP(*P(u1, -tile_m('floor') / 2, 0.0)), uv_u=GD(*d))
    m.ungroup()


# --- corridor-to-room junctions ---------------------------------------------------
# User, 2026-09-26: no flat accent slab where a corridor meets a room. The room
# wall is cut to the corridor's own profile, and the corridor's rib stands at
# the room face as the connection.
JUNCTION_ROOM = {  # room look, half width of the room wall face, wall height, room texture origin (plan) or None
    'A0 port': ('steel', 4.0, 4.5, None), 'Hub S': ('steel', 3.5, 4.5, None), 'Hub N': ('steel', 3.5, 4.5, None),
    'Hub E': ('steel', 3.5, 4.5, None), 'Hub W': ('steel', 3.5, 4.5, None),
    'Hall upper': ('concrete', 3.5, 4.5, (K.HALL['x0'], K.HALL['y0'])),
    'Hall floor door': ('concrete', 3.5, 4.5, (K.HALL['x0'], K.HALL['y0'])),
    'R1 door': ('warm', 3.5, K.R1['floor'] + K.R1['ceil'], None),
}


def profile_section(prof):
    """The corridor's clear outline (v, h), convex: the main wall line carried
    down to the floor, up to the ceiling, mirrored."""
    main = [sg for sg in S.PROFILES[prof]['segments'] if sg[2] != 'plinth']
    (xa, ya), (xb, yb), _ = main[0]
    x0 = xa + (0.0 - ya) * (xb - xa) / (yb - ya)
    right = [(x0, 0.0)] + [sg[1] for sg in main]
    return [(-x, y) for x, y in right] + [(x, y) for x, y in reversed(right)], right


def junction(name, c, d, floor, kind, run_key, end):
    spec = K.RUNS[run_key]
    prof = spec['profile']
    room_look, hw, wall_h, room_origin = JUNCTION_ROOM[name]
    d = (float(d[0]), float(d[1]))
    nl = (-d[1], d[0])
    section, right = profile_section(prof)
    door_kind = kind.split(':')[1] if ':' in kind else None
    low = kind.startswith('door_low')

    def P(u, v, h):
        return (c[0] + d[0] * u + nl[0] * v, c[1] + d[1] * u + nl[1] * v, floor + h)

    def slab(poly, u0, u1, tex, nm, **kw):
        hullp([P(u, v, h) for v, h in poly for u in (u0, u1)], tex, f'{name} {nm}', tally='junction', **kw)

    m.group(f'Junction {name} ({kind})')
    # 1. The room wall, cut to fit.
    look(room_look)
    # The room's own texture origin, so its wall pattern runs straight across
    # the cut (a hall shares one corner for all its walls).
    corner = GP(room_origin[0], room_origin[1], 0.0) if room_origin else GP(*P(0.0, -hw, 0.0))
    if low:
        # The room is lower than the corridor: a door-sized hole only.
        dh, dt = K.DOOR_OPENING[door_kind]
        rf = K.R1['floor']
        for poly in ([(-hw, 0.0), (-dh, 0.0), (-dh, wall_h), (-hw, wall_h)], [(dh, 0.0), (hw, 0.0), (hw, wall_h), (dh, wall_h)],
                     [(-dh, rf + dt), (dh, rf + dt), (dh, wall_h), (-dh, wall_h)]):
            slab(poly, -K.ROOM_WALL, 0.0, R('wall'), 'room wall', uv_origin=corner)
        for poly in ([(-hw, rf), (-dh, rf), (-dh, rf + S.PLINTH_H), (-hw, rf + S.PLINTH_H)],
                     [(dh, rf), (hw, rf), (hw, rf + S.PLINTH_H), (dh, rf + S.PLINTH_H)]):
            slab(poly, 0.0, 0.125, R('plinth'), 'room band', anchor=(GP(*P(0.0, -hw, rf)), 64.0))
    else:
        left = [(-x, y) for x, y in right]
        for (va, ha), (vb, hb) in zip(left, left[1:]):
            slab([(-hw, ha), (va, ha), (vb, hb), (-hw, hb)], -K.ROOM_WALL, 0.0, R('wall'), 'room wall', uv_origin=corner)
            slab([(hw, ha), (-va, ha), (-vb, hb), (hw, hb)], -K.ROOM_WALL, 0.0, R('wall'), 'room wall', uv_origin=corner)
        top = right[-1][1]
        if wall_h > top + 1e-6:
            slab([(-hw, top), (hw, top), (hw, wall_h), (-hw, wall_h)], -K.ROOM_WALL, 0.0, R('wall'), 'room wall over', uv_origin=corner)
        # The room's plinth band runs up to the opening's edge.
        for sgn in (-1, 1):
            band = clip_poly([(sgn * hw, 0.0), (sgn * right[0][0], 0.0), (sgn * right[0][0], S.PLINTH_H), (sgn * hw, S.PLINTH_H)],
                             [(0, 1, S.PLINTH_H)])
            slab(band, 0.0, 0.125, R('plinth'), 'room band', anchor=(GP(*P(0.0, -hw, 0.0)), 64.0))
    # 2. The connecting rib, in the corridor's look, standing at the room face
    # (or at the corridor's end, for a low room).
    look(spec['look'])
    segs = S.PROFILES[prof]['segments']
    main = [sg for sg in segs if sg[2] != 'plinth']
    foot_x = main[0][0][0] - S.RIB_D
    plinth_top = main[0][0][1]
    ch = S.ceil_half(prof)
    ur = (-1.0, -0.5) if low else (-S.RIB_DEPTH / 2, S.RIB_DEPTH / 2)
    rorg = GP(*P(ur[0], 0.0, 0.0))
    for sgn in (1, -1):
        slab([(sgn * foot_x, -0.25), (sgn * W, -0.25), (sgn * W, plinth_top), (sgn * foot_x, plinth_top)], *ur,
             R('rib'), 'rib foot', uv_origin=rorg)
        for (xa, ya), (xb, yb), role in main:
            slab([(sgn * (xa - S.RIB_D), ya), (sgn * xa, ya), (sgn * xb, yb), (sgn * (xb - S.RIB_D), yb)], *ur,
                 R('rib'), 'rib', uv_origin=rorg)
    slab([(-ch, S.CEIL_Y - S.RIB_D), (ch, S.CEIL_Y - S.RIB_D), (ch, S.CEIL_Y), (-ch, S.CEIL_Y)], *ur, R('rib'), 'rib beam', uv_origin=rorg)
    # 3. A low sill between the rib feet, over the room wall's thickness: any
    # change of floor texture happens on it.
    su = (-1.0, -0.5) if low else (-K.ROOM_WALL, S.RIB_DEPTH / 2)
    slab([(-foot_x, 0.0), (foot_x, 0.0), (foot_x, K.SILL_H), (-foot_x, K.SILL_H)], *su, R('frame'), 'sill', uv_origin=rorg)
    # 4. A door: a panel shaped to the corridor's profile holds it.
    if door_kind:
        dh, dt = K.DOOR_OPENING[door_kind]
        if low:
            dt = K.R1['floor'] + dt
            pu = (-0.75, -0.5)
        else:
            pu = (-K.ROOM_WALL, 0.0)
        # The panel is in the room's look (it IS the room wall, cut for the door)
        # and uses the plain door_panel role, so the cut never truncates a pattern.
        look(room_look if not low else spec['look'])
        panel_tex = lambda n_, c_: R('door_panel') if abs(n_[0] * d[0] - n_[2] * d[1]) > 0.5 else R('frame')
        for part in ([(0, -1, -dt)], [(0, 1, dt), (1, 0, -dh)], [(0, 1, dt), (-1, 0, -dh)]):
            piece = clip_poly(section, part)
            if len(piece) >= 3:
                slab(piece, *pu, panel_tex, 'door panel', uv_origin=corner if not low else GP(*P(pu[1], -right[0][0], 0.0)))
    m.ungroup()


# --- rooms ------------------------------------------------------------------------
def octagon(cx, cy, flats, clip):
    h = flats / 2
    return [(cx - h + clip, cy - h), (cx + h - clip, cy - h), (cx + h, cy - h + clip), (cx + h, cy + h - clip),
            (cx + h - clip, cy + h), (cx - h + clip, cy + h), (cx - h, cy + h - clip), (cx - h, cy - h + clip)]


def plan_prism(poly, h0, h1, tex, name, **kw):
    hullp([(x, y, h) for x, y in poly for h in (h0, h1)], tex, name, **kw)


def wall_piece(a, b, oa, ob, h0, h1, tex, name, tally='room', origin=None):
    """origin: the plan point where this wall's panels start (defaults to its corner a)."""
    o = origin or a
    hullp([(p[0], p[1], h) for p in (a, b, oa, ob) for h in (h0, h1)], tex, name, tally=tally, uv_origin=GP(o[0], o[1], h0))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def room_ring(inner, outer, top_inset, wall_h, ceil_h, floor, name, skip_edges=(), band=True, windows=(), haunch=True):
    """Walls, plinth band and 45-degree haunch around a convex plan polygon.
    skip_edges: edge indices left open for ports (bulkheads supply them).
    windows: {edge: (t0, t1, sill, head)} openings along an edge."""
    top = S.offset_polygon(inner, top_inset)
    band_poly = S.offset_polygon(inner, 0.125)
    n = len(inner)
    for i in range(n):
        a, b, oa, ob = inner[i], inner[(i + 1) % n], outer[i], outer[(i + 1) % n]
        ta, tb = top[i], top[(i + 1) % n]
        if haunch:
          hullp([(a[0], a[1], floor + wall_h), (b[0], b[1], floor + wall_h), (oa[0], oa[1], floor + wall_h),
               (ob[0], ob[1], floor + wall_h), (oa[0], oa[1], floor + ceil_h), (ob[0], ob[1], floor + ceil_h),
               (ta[0], ta[1], floor + ceil_h), (tb[0], tb[1], floor + ceil_h)], R('slope'), f'{name} haunch {i}', tally='room')
        if i in skip_edges:
            continue
        spans = [(0.0, 1.0, 0.0, wall_h)]
        win = dict(windows).get(i)
        if win:
            t0, t1, sill, head = win
            spans = [(0.0, t0, 0.0, wall_h), (t1, 1.0, 0.0, wall_h), (t0, t1, 0.0, sill), (t0, t1, head, wall_h)]
        for ta_, tb_, h0, h1 in spans:
            pa, pb, qa, qb = lerp(a, b, ta_), lerp(a, b, tb_), lerp(oa, ob, ta_), lerp(oa, ob, tb_)
            role = 'frame' if win and (ta_, tb_) == (win[0], win[1]) else None
            if h0 < S.PLINTH_H:
                wall_piece(pa, pb, qa, qb, floor + h0, floor + min(h1, S.PLINTH_H), R(role or 'plinth'), f'{name} plinth {i}')
            if h1 > S.PLINTH_H:
                wall_piece(pa, pb, qa, qb, floor + max(h0, S.PLINTH_H), floor + h1, R(role or 'wall'), f'{name} wall {i}')
        if band:
            ba, bb = band_poly[i], band_poly[(i + 1) % n]
            if win:
                t0, t1 = win[0], win[1]
                for ta_, tb_ in ((0.0, t0), (t1, 1.0)):
                    wall_piece(lerp(ba, bb, ta_), lerp(ba, bb, tb_), lerp(a, b, ta_), lerp(a, b, tb_),
                               floor, floor + S.PLINTH_H, R('plinth'), f'{name} band {i}')
                if win[2] >= S.PLINTH_H:
                    wall_piece(lerp(ba, bb, t0), lerp(ba, bb, t1), lerp(a, b, t0), lerp(a, b, t1),
                               floor, floor + S.PLINTH_H, R('plinth'), f'{name} band {i}')
            else:
                wall_piece(ba, bb, a, b, floor, floor + S.PLINTH_H, R('plinth'), f'{name} band {i}')


def hatch_ring(x, y, h, face, name):
    """A sealed hatch reservation: a frame ring round a grate plate. face =
    'ceiling' (ring hangs below h) or 'floor' (ring stands on h)."""
    a, r = K.HATCH_APERTURE / 2, K.HATCH_RING
    d = 0.0625
    h0, h1 = (h - d, h) if face == 'ceiling' else (h, h + d)
    for x0, x1, y0, y1 in ((x - a - r, x + a + r, y - a - r, y - a), (x - a - r, x + a + r, y + a, y + a + r),
                           (x - a - r, x - a, y - a, y + a), (x + a, x + a + r, y - a, y + a)):
        boxp(x0, x1, y0, y1, h0, h1, R('frame'), f'{name} ring', tally='hatch')
    ph0, ph1 = (h - d * 0.5, h) if face == 'ceiling' else (h, h + d * 0.5)
    boxp(x - a, x + a, y - a, y + a, ph0, ph1, R('service'), f'{name} grate', tally='hatch')


# ================================================================================
# A0 arrival
look(K.A0['look'])
m.group('A0 arrival')
a0 = [(K.A0['x0'], K.A0['y0']), (K.A0['x1'], K.A0['y0']), (K.A0['x1'], K.A0['y1']), (K.A0['x0'], K.A0['y1'])]
a0o = S.offset_polygon(a0, -0.5)
plan_prism(a0o, -0.5, 0.0, R('floor'), 'A0 floor', tally='room', uv_origin=GP(-tile_m('floor') / 2, 0.0, 0.0))
plan_prism(a0o, K.A0['ceil'], K.A0['ceil'] + 0.5, R('ceiling'), 'A0 ceiling', tally='room')
for i in range(4):
    a, b, oa, ob = a0[i], a0[(i + 1) % 4], a0o[i], a0o[(i + 1) % 4]
    if i == 2:
        continue                           # north side: the A0 port bulkhead
    wall_piece(a, b, oa, ob, 0, S.PLINTH_H, R('plinth'), 'A0 plinth')
    wall_piece(a, b, oa, ob, S.PLINTH_H, K.A0['ceil'], R('wall'), 'A0 wall')
# The sealed airlock door on the south wall.
boxp(-1.5, 1.5, K.A0['y0'], K.A0['y0'] + 0.125, 0.0, 3.0,
     lambda n, c: R('door') if abs(n[2]) > 0.5 else R('frame'), 'A0 airlock door', tally='detail')
m.ungroup()

# Corridors.
frames = {k: run(k) for k in K.RUNS}
for spec in K.JUNCTIONS:
    junction(*spec)

# J1 hub.
look(K.HUB['look'])
m.group('J1 hub')
hub = octagon(K.HUB['cx'], K.HUB['cy'], K.HUB['flats'], K.HUB['clip'])
hubo = S.offset_polygon(hub, -0.5)
# The hub floor is centred on the hub, with ONE square of the dotted grate set
# 0.125 m down at its centre: a feature, not a cover (user rule).
GR = K.GRATE_DEPTH
hub_origin = GP(K.HUB['cx'] - tile_m('floor') / 2, K.HUB['cy'] - tile_m('floor') / 2, 0.0)
gx0, gx1 = K.HUB['cx'] - 1.0, K.HUB['cx'] + 1.0
gy0, gy1 = K.HUB['cy'] - 1.0, K.HUB['cy'] + 1.0
floor_tex = lambda n_, c_: R('floor') if n_[1] > 0.5 else R('frame')
for part in ([(1, 0, gx0)], [(-1, 0, -gx1)], [(-1, 0, -gx0), (1, 0, gx1), (0, 1, gy0)], [(-1, 0, -gx0), (1, 0, gx1), (0, -1, -gy1)]):
    piece = clip_poly(hubo, part)
    if len(piece) >= 3:
        plan_prism(piece, -0.5, 0.0, floor_tex, 'hub floor', tally='room', uv_origin=hub_origin)
plan_prism([(gx0, gy0), (gx1, gy0), (gx1, gy1), (gx0, gy1)], -0.5, -GR, R('grate'), 'hub grate', tally='room')
HUB_WALL, HUB_CEIL = 4.5, 5.5
plan_prism(hubo, HUB_CEIL, HUB_CEIL + 0.5, R('ceiling'), 'hub ceiling', tally='room')
room_ring(hub, hubo, 1.0, HUB_WALL, HUB_CEIL, 0.0, 'hub', skip_edges=(0, 2, 4, 6))
hatch_ring(0.0, K.HUB['cy'], HUB_CEIL, 'ceiling', 'hub hatch')
m.ungroup()

# H1 hall: a knee-wall nave. This hall's shape, not a template.
Hh = K.HALL
look(Hh['look'])
m.group('H1 hall shell')
hx0, hx1, hy0, hy1 = Hh['x0'], Hh['x1'], Hh['y0'], Hh['y1']
cx = (hx0 + hx1) / 2
section = [(hx0, 0.0), (hx1, 0.0), (hx1, Hh['knee']), (cx + Hh['ceil_half'], Hh['ceil']), (cx - Hh['ceil_half'], Hh['ceil']),
           (hx0, Hh['knee'])]
# Hall floor from its corner, with two grate squares recessed beside each tank.
hall_origin = GP(hx0, hy0, 0.0)
holes = [(tx - 4.6, tx - 2.6, ty - 2.0, ty + 2.0) for tx, ty in K.HALL_TANKS]
xs = sorted({hx0 - 0.5, hx1 + 0.5} | {h[0] for h in holes} | {h[1] for h in holes})
for xa_, xb_ in zip(xs, xs[1:]):
    cuts = sorted([h for h in holes if h[0] <= xa_ + 1e-6 and h[1] >= xb_ - 1e-6], key=lambda h: h[2])
    y = hy0 - 0.5
    for h in cuts + [None]:
        y_end = h[2] if h else hy1 + 0.5
        if y_end - y > 1e-6:
            boxp(xa_, xb_, y, y_end, -0.5, 0.0, lambda n_, c_: R('floor') if n_[1] > 0.5 else R('frame'),
                 'hall floor', tally='hall', uv_origin=hall_origin)
        if h:
            boxp(h[0], h[1], h[2], h[3], -0.5, -GR, R('grate'), 'hall grate', tally='hall')
            y = h[3]
boxp(cx - Hh['ceil_half'] - 0.5, cx + Hh['ceil_half'] + 0.5, hy0 - 0.5, hy1 + 0.5, Hh['ceil'], Hh['ceil'] + 0.5,
     R('ceiling'), 'hall ceiling', tally='hall', uv_origin=hall_origin)
door_y = Hh['floor_door'][1]
for side, xw, xo in ((-1, hx0, hx0 - 0.5), (1, hx1, hx1 + 0.5)):
    spans = [(hy0, hy1)] if side > 0 else [(hy0, door_y - W), (door_y + W, hy1)]
    for y0, y1 in spans:
        boxp(min(xw, xo), max(xw, xo), y0, y1, 0.0, S.PLINTH_H, R('plinth'), 'hall knee plinth', tally='hall', uv_origin=hall_origin)
        boxp(min(xw, xo), max(xw, xo), y0, y1, S.PLINTH_H, Hh['knee'], R('wall'), 'hall knee wall', tally='hall', uv_origin=hall_origin)
        bx = xw - side * 0.125
        boxp(min(xw, bx), max(xw, bx), y0, y1, 0.0, S.PLINTH_H, R('plinth'), 'hall band', tally='hall', uv_origin=hall_origin)
    if side < 0:
        boxp(xo, xw, door_y - W, door_y + W, S.SHELL_TOP, Hh['knee'], R('wall'), 'hall wall over door', tally='hall', uv_origin=hall_origin)
    # Slope from the knee to the ceiling edge, the full length.
    sx = cx + side * Hh['ceil_half']
    hullp([(p[0], y, p[1]) for p in ((xw, Hh['knee']), (xo, Hh['knee']), (xo, Hh['ceil'] + 0.5), (sx, Hh['ceil']),
                                         (sx, Hh['ceil'] + 0.5)) for y in (hy0 - 0.5, hy1 + 0.5)], R('slope'), 'hall slope', tally='hall', uv_origin=hall_origin)
# End walls: the section, split round the upper bulkhead in the south wall.
up_x = Hh['upper_door'][1]
for yw, yo, south in ((hy0, hy0 - 0.5, True), (hy1, hy1 + 0.5, False)):
    boxes = [(hx0 - 0.5, hx1 + 0.5, -0.5, Hh['ceil'] + 0.5)]
    if south:
        boxes = [(hx0 - 0.5, up_x - W, -0.5, Hh['ceil'] + 0.5), (up_x + W, hx1 + 0.5, -0.5, Hh['ceil'] + 0.5),
                 (up_x - W, up_x + W, -0.5, K.CATWALK['level']), (up_x - W, up_x + W, K.CATWALK['level'] + S.SHELL_TOP, Hh['ceil'] + 0.5)]
    wide_section = [(hx0 - 0.5, -0.5), (hx1 + 0.5, -0.5), (hx1 + 0.5, Hh['knee']), (cx + Hh['ceil_half'] + 0.5, Hh['ceil'] + 0.5),
                    (cx - Hh['ceil_half'] - 0.5, Hh['ceil'] + 0.5), (hx0 - 0.5, Hh['knee'])]
    for bx0, bx1, bh0, bh1 in boxes:
        piece = clip_poly(wide_section, [(-1, 0, -bx0), (1, 0, bx1), (0, -1, -bh0), (0, 1, bh1)])
        if len(piece) >= 3:
            hullp([(x, y, h) for x, h in piece for y in (min(yw, yo), max(yw, yo))],
                  lambda n, c, yw=yw: R('plinth') if c[1] < S.PLINTH_H else R('wall'), 'hall end wall', tally='hall', uv_origin=hall_origin)
m.ungroup()

m.group('H1 hall structure')
fd = Hh['frame_d']
for fy in Hh['frames']:
    for side in (-1, 1):
        xw = hx0 if side < 0 else hx1
        # Foot: straight down, flush with the knee-wall rib above.
        hullp([(x, y, h) for x in (xw, xw - side * fd) for y in (fy - fd / 2, fy + fd / 2) for h in (-0.25, Hh['knee'])],
              R('rib'), 'hall frame foot', tally='hall')
        sx = cx + side * Hh['ceil_half']
        hullp([(x, y, h) for x, h in ((xw, Hh['knee']), (xw - side * fd, Hh['knee']), (sx, Hh['ceil']),
                                          (sx - side * fd, Hh['ceil'] - fd)) for y in (fy - fd / 2, fy + fd / 2)],
              R('rib'), 'hall frame slope', tally='hall')
    boxp(cx - Hh['ceil_half'], cx + Hh['ceil_half'], fy - fd / 2, fy + fd / 2, Hh['ceil'] - fd, Hh['ceil'], R('rib'), 'hall frame beam', tally='hall')
m.ungroup()

m.group('H1 catwalk and stair')
cl = K.CATWALK['level']
deck = 0.3
boxp(22.0, hx1, hy0, hy0 + 3.0, cl - deck, cl, R('floor'), 'catwalk south deck', tally='hall')
boxp(hx1 - 3.0, hx1, hy0 + 3.0, K.HALL_STAIR['y0'], cl - deck, cl, R('floor'), 'catwalk east deck', tally='hall')
for px, py in ((22.2, hy0 + 2.8), (hx1 - 2.8, hy0 + 2.8), (hx1 - 2.8, 50.0), (hx1 - 2.8, 58.0), (hx1 - 2.8, K.HALL_STAIR['y0'] - 0.2)):
    boxp(px - 0.2, px + 0.2, py - 0.2, py + 0.2, 0.0, cl - deck, R('frame'), 'catwalk column', tally='hall')


def rail(x0, y0, x1, y1, h0, h1, name):
    """An open rail: posts every 2 m and a top rail, from (x0,y0,h0) to (x1,y1,h1)."""
    L = math.hypot(x1 - x0, y1 - y0)
    k = max(1, int(L // 2))
    for j in range(k + 1):
        t = j / k
        px, py, ph = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, h0 + (h1 - h0) * t
        boxp(px - 0.05, px + 0.05, py - 0.05, py + 0.05, ph, ph + 1.05, R('frame'), f'{name} post', tally='rail')
    nx, ny = -(y1 - y0) / L * 0.05, (x1 - x0) / L * 0.05
    hullp([(x0 + nx * s, y0 + ny * s, h0 + dh) for s in (-1, 1) for dh in (1.0, 1.1)]
          + [(x1 + nx * s, y1 + ny * s, h1 + dh) for s in (-1, 1) for dh in (1.0, 1.1)], R('frame'), f'{name} top', tally='rail')


rail(22.0, hy0 + 3.0, hx1 - 3.0, hy0 + 3.0, cl, cl, 'catwalk south rail')
rail(22.0, hy0 + 0.1, 22.0, hy0 + 3.0, cl, cl, 'catwalk end rail')
rail(hx1 - 3.0, hy0 + 3.0, hx1 - 3.0, K.HALL_STAIR['y0'], cl, cl, 'catwalk east rail')
# The edge stair down the east wall, north from the catwalk to the floor.
st = K.HALL_STAIR
for k in range(K.S1_RISERS - 1):
    y0, y1 = st['y0'] + k * K.TREAD, st['y0'] + (k + 1) * K.TREAD
    boxp(hx1 - st['width'], hx1, y0, y1, 0.0, cl - (k + 1) * K.RISER, R('floor'), f'hall step {k}', tally='stair')
rail(hx1 - st['width'], st['y0'], hx1 - st['width'], st['y1'] - K.TREAD, cl, K.RISER, 'hall stair rail')
m.ungroup()

look(Hh['machine_look'])
m.group('H1 machinery')


def reg_oct(cx_, cy_, r):
    return [(cx_ + r * math.cos(k * math.pi / 4 + math.pi / 8), cy_ + r * math.sin(k * math.pi / 4 + math.pi / 8)) for k in range(8)]


for tx, ty in K.HALL_TANKS:
    plan_prism(reg_oct(tx, ty, 2.6), 0.0, 0.5, R('machine_base'), 'tank plinth', tally='machine')
    tank = reg_oct(tx, ty, 2.0)
    plan_prism(tank, 0.5, 5.5, R('machine_body'), 'tank', tally='machine')
    plan_prism(reg_oct(tx, ty, 2.25), 5.5, 5.8, R('machine_top'), 'tank cap', tally='machine')
    for k in range(0, 8, 2):
        a, b = tank[k], tank[(k + 1) % 8]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ux, uy = (b[0] - a[0]), (b[1] - a[1])
        L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
        nx, ny = mx - tx, my - ty
        nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
        hullp([(mx + ux * s + nx * o, my + uy * s + ny * o, h) for s in (-0.25, 0.25) for o in (-0.02, 0.07) for h in (1.5, 4.5)],
              R('coolant'), 'tank glow slot', tally='machine')
    for px in (-0.8, 0.8):
        boxp(tx + px - 0.3, tx + px + 0.3, ty - 0.3, ty + 0.3, 5.8, Hh['ceil'], R('pipe'), 'tank riser', tally='machine')
look(Hh['look'])
hatch_ring(*K.HALL_FLOOR_HATCH, 0.0, 'floor', 'hall floor hatch')
m.ungroup()

# R1 control room: composed from its contents.
Rr = K.R1
look(Rr['look'])
m.group('R1 control room')
r1 = [(Rr['x0'] + Rr['clip'], Rr['y0']), (Rr['x1'], Rr['y0']), (Rr['x1'], Rr['y1']), (Rr['x0'] + Rr['clip'], Rr['y1']),
      (Rr['x0'], Rr['y1'] - Rr['clip']), (Rr['x0'], Rr['y0'] + Rr['clip'])]
r1o = S.offset_polygon(r1, -0.5)
fl = Rr['floor']
plan_prism(r1o, -0.5, fl, R('floor'), 'R1 floor', tally='room', uv_origin=GP(Rr['x0'], Rr['y0'], fl))
plan_prism(r1o, fl + Rr['ceil'], fl + Rr['ceil'] + 0.5, R('ceiling'), 'R1 ceiling', tally='room')
wy0, wy1 = Rr['window_span']
wedge = 4                                      # the west edge: (x0, y1-clip) -> (x0, y0+clip)
ya, yb = r1[4][1], r1[5][1]
t0, t1 = (ya - wy1) / (ya - yb), (ya - wy0) / (ya - yb)
# An office: flat low ceiling, no haunch.
room_ring(r1, r1o, 0.5, Rr['ceil'], Rr['ceil'], fl, 'R1', skip_edges=(1,),
          windows=[(wedge, (t0, t1, Rr['sill'], Rr['head']))], haunch=False)
# Glass: a clip brush in the window.
boxp(Rr['x0'] - 0.4, Rr['x0'] - 0.3, wy0, wy1, fl + Rr['sill'], fl + Rr['head'], 'clip', 'R1 window glass (clip)', tally='detail')
# Console row facing the window: desks with sloped screens.
cxw, cy0, cy1 = Rr['consoles']
for k in range(3):
    y0 = cy0 + k * (cy1 - cy0) / 3 + 0.1
    y1 = cy0 + (k + 1) * (cy1 - cy0) / 3 - 0.1
    hullp([(cxw - 0.45, y, fl) for y in (y0, y1)] + [(cxw + 0.45, y, fl) for y in (y0, y1)]
          + [(cxw - 0.45, y, fl + 0.95) for y in (y0, y1)] + [(cxw + 0.45, y, fl + 1.2) for y in (y0, y1)],
          lambda n, c: R('screen') if n[1] > 0.5 else R('machine_body'), 'R1 console', tally='detail')
m.ungroup()

# D1 debris: the North run's rib at x = 10 has fallen across the north side.
look(K.RUNS['North']['look'])
m.group('D1 fallen rib and panels')
fx, fy = K.D1_FALL['station_x'], K.D1_FALL['y']
# The fallen rib: a long member lying diagonally from the north wall foot out
# toward the lane, resting on rubble.
hullp([(fx - 1.6 + dx, fy + 2.7 + dy, h) for dx, dy in ((0, 0), (0.45, -0.15)) for h in (0.0, 0.45)]
      + [(fx + 1.9 + dx, fy + 0.45 + dy, h) for dx, dy in ((0, 0), (0.45, -0.15)) for h in (0.9, 1.35)],
      R('rib'), 'fallen rib', tally='debris')
# Two ceiling panels slumped against the north wall.
hullp([(fx - 1.8, fy + 2.9, 0.0), (fx - 0.2, fy + 2.9, 0.0), (fx - 1.8, fy + 1.7, 0.0), (fx - 0.2, fy + 1.7, 0.0),
       (fx - 1.8, fy + 2.9, 2.2), (fx - 0.2, fy + 2.9, 2.0), (fx - 1.8, fy + 2.75, 2.2), (fx - 0.2, fy + 2.75, 2.0)],
      R('ceiling'), 'slumped panel', tally='debris')
hullp([(fx + 0.2, fy + 2.9, 0.0), (fx + 1.9, fy + 2.9, 0.0), (fx + 0.2, fy + 1.3, 0.0), (fx + 1.9, fy + 1.5, 0.0),
       (fx + 0.2, fy + 1.45, 0.12), (fx + 1.9, fy + 1.65, 0.12), (fx + 0.2, fy + 2.9, 1.1), (fx + 1.9, fy + 2.9, 1.3)],
      R('ceiling'), 'fallen panel', tally='debris')
rng = random.Random(11)
for k, (rx, ry, r, h) in enumerate(((fx - 0.9, fy + 1.3, 0.55, 0.5), (fx + 0.8, fy + 0.9, 0.45, 0.4), (fx + 2.4, fy + 1.9, 0.6, 0.55),
                                    (fx - 2.3, fy + 1.9, 0.5, 0.45), (fx + 0.1, fy + 1.9, 0.4, 0.35))):
    pts = []
    for j in range(7):
        ang = j / 7 * math.tau + rng.uniform(-0.3, 0.3)
        rr = r * rng.uniform(0.7, 1.05)
        pts.append((rx + math.cos(ang) * rr, ry + math.sin(ang) * rr, 0.0))
        pts.append((rx + math.cos(ang + 0.4) * rr * 0.5, ry + math.sin(ang + 0.4) * rr * 0.5, h * rng.uniform(0.7, 1.0)))
    hullp(pts, R('plinth'), f'rubble {k}', tally='debris')
# The stumps left where the rib stood: both feet broken off at knee height.
for side in (1, -1):
    y_in = fy + side * (S.PROFILES['P1']['segments'][1][0][0] - S.RIB_D)
    y_out = fy + side * W
    boxp(fx - 0.25, fx + 0.25, min(y_in, y_out), max(y_in, y_out), -0.25, 0.7 if side > 0 else 0.45, R('rib'), 'rib stump', tally='debris')
m.ungroup()

# X1 collapse: 3 m of C4 slumped to a 2.0 x 1.4 m gap.
look(K.RUNS['C4']['look'])
m.group('X1 collapse')
xa, xb = K.X1['x0'], K.X1['x1']
cy_ = K.C4['y']
hw, ch_ = K.X1['clear_w'] / 2, K.X1['clear_h']
for side in (1, -1):
    # Slumped wall masses from each side, leaving the 2 m gap.
    hullp([(x, cy_ + side * v, h) for x in (xa, xb) for v, h in ((hw, 0.0), (hw, ch_), (1.9, 2.6), (W, 2.1), (W, 0.0))],
          R('plinth'), 'slumped wall', tally='debris')
# The fallen ceiling slab bridging the gap at 1.4 m.
hullp([(x, cy_ + v, h) for x in (xa - 0.2, xb + 0.3) for v in (-1.7, 1.6) for h in (ch_, ch_ + 0.3)]
      + [(xa - 0.2, cy_ + 1.6, ch_ + 0.55)], R('ceiling'), 'fallen slab', tally='debris')
m.ungroup()

# Mars outside R1's window.
look('steel')
m.group('Mars exterior (west)')
boxp(-110.0, Rr['x0'] - 0.5, -30.0, 80.0, -2.0, -1.5, R('ground'), 'regolith', tally='exterior')
rng = random.Random(5)
for k, (rx, ry, r, h) in enumerate(((-44, 18, 1.8, 1.4), (-52, 30, 2.6, 2.2), (-61, 12, 3.5, 3.0), (-75, 26, 7.0, 6.5),
                                    (-40, 28, 0.9, 0.7), (-58, 40, 4.0, 3.2))):
    pts = []
    for j in range(9):
        ang = j / 9 * math.tau + rng.uniform(-0.25, 0.25)
        rr = r * rng.uniform(0.7, 1.1)
        pts.append((rx + math.cos(ang) * rr, ry + math.sin(ang) * rr, -1.8))
        pts.append((rx + math.cos(ang + 0.3) * rr * 0.5, ry + math.sin(ang + 0.3) * rr * 0.5, -1.5 + h * rng.uniform(0.6, 1.0)))
    hullp(pts, R('rock'), f'rock {k}', tally='exterior')
m.ungroup()

# Validation markers.
for route, pts in K.ROUTES.items():
    for i, (x, y, h, posture) in enumerate(pts):
        o = B.to_map(G(x, h, y))
        m.entity('rb_route', {'origin': ' '.join(B._fmt(v) for v in o), 'route': route, 'index': i, 'posture': posture})
for kind, mn, (x, y, h) in K.PROBES:
    o = B.to_map(G(x, h, y))
    m.entity('rb_probe', {'origin': ' '.join(B._fmt(v) for v in o), 'kind': kind, 'min': mn})
for pair, expect, a, b in K.NAV_PAIRS:
    for end, (x, y, h) in (('a', a), ('b', b)):
        o = B.to_map(G(x, h, y))
        m.entity('rb_nav', {'origin': ' '.join(B._fmt(v) for v in o), 'pair': pair, 'end': end, 'expect': expect})

for (x, y, h), radius, reason in K.DARK_ZONES:
    o = B.to_map(G(x, h, y))
    m.entity('rb_dark', {'origin': ' '.join(B._fmt(v) for v in o), 'radius': radius, 'reason': reason})

MAP.parent.mkdir(parents=True, exist_ok=True)
MAP.write_text(m.text('Kit lab K-01. Generated by tools/bootstrap-kit-lab.py; now the editable source.'), encoding='utf-8')
print(f'KIT_LAB_MAP: {m.count} brushes, {len(m.entities)} markers -> {MAP.relative_to(ROOT)}')
print('  ' + ', '.join(f'{k} {v}' for k, v in sorted(m.tally.items())))
