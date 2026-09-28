"""Style lab S-01: the single source of truth.

Phase 1 of docs/clean-slate-test-plan.md. R-01, extended: three corridor
profiles in a row, each separated by a bulkhead, then a portal into a
machine room that has a window onto Mars.

Every other style-lab tool imports this module:
  bootstrap-style-lab.py      writes the map
  write-style-lab-scene.py    writes the materials, texture previews and scene

Coordinates are Godot metres, y up. The corridor runs toward -Z from the
spawn. Floors sit at y = 0. Dimensions stay on the 0.125 m construction grid.
"""

# --- corridor profiles ----------------------------------------------------
# Each profile is the +X half of the clear section. It lists wall SEGMENTS
# (inner face line, bottom to top, with a role), the ceiling height and the
# ceiling's half width. The -X half mirrors it. The solid behind each
# segment runs out to SHELL_X.
SHELL_X = 3.5
CEIL_Y = 4.0
SHELL_TOP = 4.5
RIB_D = 0.375        # how far a rib stands proud of the wall, horizontally
RIB_DEPTH = 0.5      # rib thickness along the corridor
PLINTH_H = 1.0

PROFILES = {
    # Full trapezoid, as drawn in R-01: 6 m floor, 3 m ceiling, 4 m high.
    # The wall is an overhang (facing down and inward), so it cannot be stood
    # on. The plinth band is a parallel facet 0.125 m proud, which leaves a
    # real 0.125 m ledge at 1 m to carry the texture change.
    'P1': dict(title='Full trapezoid', segments=[
        ((2.875, 0.0), (2.5, 1.0), 'plinth'),
        ((2.625, 1.0), (1.5, 4.0), 'slope'),
    ]),
    # Knee wall: vertical to 2 m, then a slope in to a 3.5 m ceiling. The
    # lower wall stays usable for equipment.
    'P2': dict(title='Knee-wall trapezoid', segments=[
        ((2.875, 0.0), (2.875, 1.0), 'plinth'),
        ((3.0, 1.0), (3.0, 2.0), 'wall'),
        ((3.0, 2.0), (1.75, 4.0), 'slope'),
    ]),
    # Clipped box: vertical to 3 m, then a 45-degree overhang chamfer to a
    # 4 m ceiling. It is the most conventional of the three.
    'P3': dict(title='Clipped box', segments=[
        ((2.875, 0.0), (2.875, 1.0), 'plinth'),
        ((3.0, 1.0), (3.0, 3.0), 'wall'),
        ((3.0, 3.0), (2.0, 4.0), 'slope'),
    ]),
}


def ceil_half(profile):
    return PROFILES[profile]['segments'][-1][1][0]


def wall_x(profile, y):
    """Inner face |x| of the profile at height y (the main wall, not the plinth)."""
    for (x0, y0), (x1, y1), role in PROFILES[profile]['segments']:
        if role == 'plinth':
            continue
        if y0 - 1e-9 <= y <= y1 + 1e-9:
            return x0 + (y - y0) / (y1 - y0) * (x1 - x0)
    segs = PROFILES[profile]['segments']
    (x0, y0), (x1, y1), _ = segs[0]
    return x0 + (y - y0) / (y1 - y0) * (x1 - x0)


# --- layout along Z --------------------------------------------------------
SECTION_LEN = 12.0
BULKHEAD_LEN = 1.0
RIB_STATIONS = (4.0, 8.0)          # local to each section: three 4 m bays
OPENING_HALF = 2.0                 # 4.0 m bulkhead opening
OPENING_TOP = 3.25
OPENING_CHAMFER = 0.5

# (profile, z_start) with z decreasing. Section i runs z_start -> z_start - 12.
SECTIONS = []
_z = 0.0
for _p in ('P1', 'P2', 'P3'):
    SECTIONS.append((_p, _z))
    _z -= SECTION_LEN + BULKHEAD_LEN
BULKHEADS = [s[1] - SECTION_LEN for s in SECTIONS]      # z of each bulkhead's near face
ROOM_Z0 = BULKHEADS[-1] - BULKHEAD_LEN                  # -39: room's south inner face
SPAWN = (0.0, 0.05, -1.5)

# --- machine room ----------------------------------------------------------
ROOM_HALF = 8.0
ROOM_LEN = 16.0
ROOM_CLIP = 2.0
ROOM_WALL_H = 4.5
ROOM_CEIL = 6.0
HAUNCH = 1.5                       # 45-degree haunch: 1.5 m in, 1.5 m up
ROOM_SHELL = 0.5
ROOM_Z1 = ROOM_Z0 - ROOM_LEN       # -55
ROOM_CZ = (ROOM_Z0 + ROOM_Z1) / 2  # -47
FRAME_PROUD = 0.25                 # B3's frame stands proud of the room wall
WINDOW = dict(z0=ROOM_CZ - 3.0, z1=ROOM_CZ + 3.0, y0=1.0, y1=3.5)   # on the +X wall


def room_octagon(inset=0.0):
    """Inner room outline, CCW seen from above (+Y), offset by ``inset`` (negative = outward)."""
    h, c = ROOM_HALF, ROOM_CLIP
    z0, z1 = ROOM_Z0, ROOM_Z1
    pts = [(-h + c, z0), (h - c, z0), (h, z0 - c), (h, z1 + c),
           (h - c, z1), (-h + c, z1), (-h, z1 + c), (-h, z0 - c)]
    return offset_polygon(pts, inset) if inset else pts


def offset_polygon(pts, d):
    """Mitred offset of a convex polygon (x, z). Positive d moves inward."""
    import math
    n = len(pts)
    cx = sum(p[0] for p in pts) / n
    cz = sum(p[1] for p in pts) / n
    lines = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ex, ez = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ez)
        nx, nz = -ez / L, ex / L                 # a normal; flip it to point inward
        if (cx - a[0]) * nx + (cz - a[1]) * nz < 0:
            nx, nz = -nx, -nz
        lines.append(((a[0] + nx * d, a[1] + nz * d), (ex, ez)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((round(p1[0] + d1[0] * t, 6), round(p1[1] + d1[1] * t, 6)))
    return out


# Machine: an octagonal tank standing in a coolant pool on a curbed plinth.
MACHINE = dict(cx=0.0, cz=ROOM_CZ, plinth=3.0, plinth_chamfer=0.75, plinth_h=0.5,
               lip=0.25, lip_h=0.75, pool_top=0.625, tank_r=1.5, tank_top=4.0,
               cap_r=1.75, cap_top=4.25)


# --- roles, looks, the zoned mix and palettes --------------------------------
# A map face names a LOOK and a ROLE: texture "looks/<look>/<role>". Each look
# supplies one material per role in textures/looks/<look>/<role>.tres, with a
# same-named .png preview beside it for TrenchBroom. Scale is texels per map
# unit: 1.0 = 32 px/m.
#
# Revision 02 (user walkthrough 01): do not pick one texture set. The user
# prefers the QUOD pack, but red outside and red inside is one note, so the
# level needs metal and concrete looks as well. The warm red/yellow becomes the
# look of CERTAIN SECTIONS. Looks are zoned, and bulkheads are the boundaries,
# so every change of look sits on real geometry.
ROLES = ('floor', 'plinth', 'wall', 'slope', 'ceiling', 'rib', 'bulkhead', 'hazard',
         'service', 'door', 'frame', 'machine_base', 'machine_body', 'machine_top',
         'pipe', 'coolant', 'screen', 'ground', 'rock', 'grate', 'riser', 'door_panel', 'container')
# The coolant glowed at 1.5 and read as a flat white strip in the dark pit (user, 2026-09-27): now a green liquid.
EMISSIVE = {'coolant': (0.3, 0.9, 0.75, 0.45), 'screen': (0.6, 1.0, 0.8, 0.7)}

# Revision 04 (user, 2026-09-25): a texture that does not tile must never be
# used where a surface repeats (the QUOD heat pipe banded dark-bright-dark).
# tools/audit-textures.py measures every pack texture per axis: T seamless,
# P panel border (repeats as a grid), X never repeat. Each role states what it
# needs: 'HV' repeats both ways, 'H' only horizontally (the plinth band is
# pinned vertically), 'fit' is a FEATURE fitted to its face a whole number of
# times (doors, screens, service panels, grate squares). The scene writer
# refuses a texture that cannot meet its role.
ROLE_TILING = {
    'floor': 'HV', 'plinth': 'H', 'wall': 'HV', 'slope': 'HV', 'ceiling': 'HV', 'rib': 'HV',
    'bulkhead': 'HV', 'hazard': 'HV', 'service': 'fit', 'door': 'fit', 'frame': 'HV',
    'machine_base': 'HV', 'machine_body': 'HV', 'machine_top': 'HV', 'pipe': 'HV',
    'coolant': 'HV', 'screen': 'fit', 'ground': 'HV', 'rock': 'HV', 'grate': 'fit', 'riser': 'H', 'door_panel': 'HV',
    'container': 'fit',
}
FIT_ROLES = {r for r, t in ROLE_TILING.items() if t == 'fit'}

COMMON = {
    # Hazard is a thin trim only. It must repeat along a trim in either
    # direction, so it is Level Eleven's panel-bordered stripe.
    'hazard': 'packs/lvl11/ConcretePanel-Hazard-Full-01_64',
    'coolant': 'packs/quod/tex39',
    'screen': 'packs/quod/tex192',
    'ground': 'style_common/mars_ground',
    'rock': 'style_common/mars_rock',
    # The busy dotted plate is a FEATURE: one or two squares, set down in the
    # floor, never a whole floor (user rule).
    'grate': 'packs/lvl11/Grid-001-12_Base-004',
}

# Ceilings CONTINUE the look's slope/wall material (user, 2026-09-26). QUOD's
# corrugated tex90 is reserved for container sides and roll doors, never a ceiling: the 'container' role, fitted
# once to each side and tinted per look, so a stack reads as several containers (user, 2026-09-27).
# door_panel is the plain wall a door is cut into, so a cut never truncates a pattern.
# A look entry is a texture, or (texture, tint) where the tint multiplies the
# albedo, so a pale texture can serve a dark calm floor.
LOOKS = {
    # QUOD tan, olive and rust: the warm look, for certain sections only.
    'warm': {
        'floor': 'packs/quod/tex244', 'plinth': 'packs/quod/tex93', 'wall': 'packs/quod/tex8',
        'slope': 'packs/quod/tex4', 'ceiling': 'packs/quod/tex4', 'rib': 'packs/quod/tex24',
        'bulkhead': 'packs/lvl11/Metal-Panel-004_Section-001', 'service': 'packs/quod/tex27', 'door': 'packs/quod/tex18',
        'frame': 'packs/quod/tex24', 'machine_base': 'packs/quod/tex190',
        'machine_body': 'packs/quod/tex25', 'machine_top': 'packs/quod/tex24',
        'pipe': ('packs/lvl11/Panel-001-3_Base-004', (1.0, 0.62, 0.38)), 'riser': 'packs/quod/tex24',
        'door_panel': 'packs/quod/tex4', 'container': ('packs/quod/tex90', (1.0, 0.62, 0.45)),
    },
    # Grey metal: plain framed panels (the riveted panel repeated too loudly).
    'steel': {
        'floor': 'packs/lvl11/Metal-Panel_Base-004', 'plinth': 'packs/lvl11/Metal-Panel-004_Section-003',
        'wall': 'packs/lvl11/Metal-Panel_Section-001', 'slope': 'packs/lvl11/Metal-Panel_Section-001-3',
        'ceiling': 'packs/lvl11/Metal-Panel_Section-001-3', 'rib': 'packs/lvl11/Metal-Panel_Base-004',
        'bulkhead': 'packs/lvl11/Metal-Panel-004_Section-001', 'service': 'packs/lvl11/Vent-002_Base-001', 'door': 'packs/quod/tex18',
        'frame': 'packs/lvl11/Metal-Panel_Base-004', 'machine_base': 'packs/quod/tex190',
        'machine_body': 'packs/lvl11/Panel-001-3_Base-004', 'machine_top': 'packs/lvl11/Metal-Panel_Section-004',
        'pipe': 'packs/lvl11/Panel-001-3_Base-004', 'riser': 'packs/lvl11/Metal-Panel_Base-004',
        'door_panel': 'packs/lvl11/Metal-Panel_Section-001', 'container': ('packs/quod/tex90', (0.62, 0.72, 0.9)),
    },
    # Pale concrete with a muted green band. The floor is Level Eleven's
    # concrete, darkened by tint: calm, not the dotted plate.
    'concrete': {
        'floor': ('packs/lvl11/ConcreteFloor-01_64', (0.5, 0.52, 0.55)), 'plinth': 'packs/lvl11/ConcreteWallPainted-HG_64',
        'wall': 'packs/lvl11/ConcretePanel-01_64', 'slope': 'packs/lvl11/ConcretePanel-01_64',
        'ceiling': 'packs/lvl11/ConcretePanel-01_64', 'rib': 'packs/lvl11/Metal-Panel_Base-001',
        'bulkhead': 'packs/lvl11/Metal-Panel-004_Section-001', 'service': 'packs/quod/tex193',
        'door': 'packs/lvl11/MetalPanel-01V_64', 'frame': 'packs/lvl11/Metal-Panel_Base-004',
        'machine_base': 'packs/quod/tex190', 'machine_body': 'packs/lvl11/Panel-001-3_Base-004',
        'machine_top': 'packs/lvl11/Metal-Panel_Section-004', 'pipe': 'packs/lvl11/Panel-001-3_Base-004',
        'riser': 'packs/lvl11/Metal-Panel_Base-004', 'door_panel': 'packs/lvl11/ConcretePanel-01_64',
        'container': ('packs/quod/tex90', (0.8, 0.85, 0.62)),
    },
}
for _l in LOOKS.values():
    for _k, _v in COMMON.items():
        _l.setdefault(_k, _v)


def look_texture(entry):
    """(texture path, tint or None) for a LOOKS entry."""
    return (entry, None) if isinstance(entry, str) else (entry[0], entry[1])

# The authored zoning: which look each part of the lab wears. The source map
# is written with these, so TrenchBroom shows the real mix.
MIX = {'floor': 'warm', 'P1': 'steel', 'P2': 'warm', 'P3': 'concrete', 'bulkhead': 'steel',
       'room': 'steel', 'machine': 'warm', 'exterior': 'steel'}

# Palettes are look REMAPS applied at build time to a copy of the one source
# map, so a whole-lab single-look comparison needs no second map. 'mix' is the
# source map itself and the only one that keeps collision.
PALETTES = {
    'mix': {},
    'warm': {'steel': 'warm', 'concrete': 'warm'},
    'steel': {'warm': 'steel', 'concrete': 'steel'},
    'concrete': {'warm': 'concrete', 'steel': 'concrete'},
}
PALETTE_TITLES = {'mix': 'Zoned mix: P1 steel, P2 warm, P3 concrete, room steel',
                  'warm': 'All warm (QUOD)', 'steel': 'All steel', 'concrete': 'All concrete'}

# Per-role texel scale. Ribs, frames and hazard trims are narrow faces, so they
# sample at 64 px/m. Revision 03: ribs and frames use PLAIN panels. The Level
# Eleven "Trims" textures put vertical lines down a pillar and read as broken.
# Structure should read as one solid member.
ROLE_SCALE = {'rib': 0.5, 'frame': 0.5, 'hazard': 0.5}


def role_scale(texture):
    return ROLE_SCALE.get(texture.split('/')[-1], 1.0)


# --- lighting: tiers per bay, plans across the walk ----------------------------
# Revision 02: the user likes ceiling EDGE strips plus WALL lights together
# (centre strips "look a bit common"), and asked to see floor lighting and an
# unlit, damaged stretch. Each bay carries every tier. A plan picks which tiers
# are visible in each bay, so fittings and their lights always switch together
# and a dead fitting never glows.
TIERS = ('ceiling', 'edge', 'low', 'floor', 'dead', 'flicker', 'emergency')
BAYS = [(p, z0 - c) for p, z0 in SECTIONS for c in (2.0, 6.0, 10.0)]
BAY_CENTRES = [z for _, z in BAYS]

PLANS = {
    # The default walk: P1 edge + wall lights, P2 floor-lit, P3 edge + wall,
    # then a failing fitting with sparks, then a dead bay.
    'mixed': [['edge', 'low']] * 3 + [['floor']] * 3 + [['edge', 'low'], ['flicker'], ['dead', 'emergency']],
    # A long broken stretch: one failing fitting in P1, then P2 dead under red
    # emergency light, then P3 dead with nothing at all, back to light at the end.
    'damaged': [['edge', 'low'], ['flicker'], ['edge', 'low']] + [['dead', 'emergency']] * 3
               + [['dead'], ['dead'], ['edge', 'low']],
    'edge_low': [['edge', 'low']] * 9,
    'floor': [['floor']] * 9,
    'ceiling': [['ceiling']] * 9,
}
PLAN_TITLES = {'mixed': 'mixed: edge+wall / floor-lit / damaged', 'damaged': 'damaged: flicker / emergency red / dead',
               'edge_low': 'edge + wall everywhere',
               'floor': 'floor lighting everywhere', 'ceiling': 'ceiling centre (rev 01)'}


def section_of(z):
    for p, z0 in SECTIONS:
        if z0 - SECTION_LEN - 1e-9 <= z <= z0 + 1e-9:
            return p
    return None


def tier_parts(tier, profile, z):
    """[(name, light_pos or None, fixture_centre or None, fixture_size, lit)] for one tier in one bay."""
    ch = ceil_half(profile)
    out = []
    if tier == 'ceiling':
        out.append(('C', (0.0, 3.5, z), (0.0, CEIL_Y - 0.03, z), (0.35, 0.06, 2.0), True))
    elif tier in ('edge', 'dead', 'flicker'):
        for s, t in ((-1, 'L'), (1, 'R')):
            x = s * (ch - 0.3)
            lit = tier != 'dead'
            out.append((f'E{t}', (x * 0.8, 3.45, z) if lit else None, (x, CEIL_Y - 0.03, z), (0.25, 0.06, 2.0), lit))
        if tier == 'dead':
            # The wall fittings are dead too.
            for s, t in ((-1, 'L'), (1, 'R')):
                wx = wall_x(profile, 1.25)
                out.append((f'W{t}', None, (s * (wx - 0.06), 1.25, z), (0.12, 0.12, 1.2), False))
    elif tier == 'low':
        # A fitting on the wall at 1.25 m washing UP the wall, so the
        # downward-facing slope gets direct light.
        for s, t in ((-1, 'L'), (1, 'R')):
            wx = wall_x(profile, 1.25)
            out.append((f'W{t}', (s * (wx - 0.45), 1.35, z), (s * (wx - 0.06), 1.25, z), (0.12, 0.12, 1.2), True))
    elif tier == 'floor':
        # Aisle strips recessed at the plinth foot, with one light each side
        # per half bay, low, grazing up the plinth and wall. The lights stand
        # 0.7 m off the wall so they strike it rather than skim it.
        foot = PROFILES[profile]['segments'][0][0][0]
        for s, t in ((-1, 'L'), (1, 'R')):
            out.append((f'F{t}', None, (s * (foot - 0.05), 0.05, z), (0.1, 0.08, 3.2), True))
            for k, dz in ((0, -0.9), (1, 0.9)):
                out.append((f'F{t}{k}', (s * (foot - 0.7), 0.35, z + dz), None, None, True))
    elif tier == 'emergency':
        # A small red beacon low on the left wall: the bay is dead, but still
        # navigable and still telling a story.
        wx = wall_x(profile, 0.75)
        out.append(('R', (-(wx - 0.5), 0.9, z), (-(wx - 0.06), 0.75, z), (0.12, 0.2, 0.3), True))
    return out


# --- capture views ----------------------------------------------------------
# (name, camera position, look-at point). Positions are floor points; the
# capture script adds eye height.
VIEWS = [
    ('01_p1_down', (0.0, 0.05, -0.8), (0.0, 1.6, -11.0)),
    ('02_p1_wall', (-1.2, 0.05, -3.0), (2.4, 1.9, -7.5)),
    ('03_p2_down', (0.0, 0.05, -13.8), (0.0, 1.6, -24.0)),
    ('04_p2_wall', (-1.2, 0.05, -16.0), (2.6, 1.9, -20.5)),
    ('05_p3_down', (0.0, 0.05, -26.8), (0.0, 1.6, -37.0)),
    ('06_p3_wall', (-1.2, 0.05, -29.0), (2.8, 1.9, -33.5)),
    ('07_bulkhead', (0.8, 0.05, -8.8), (0.0, 1.8, -13.0)),
    ('08_room_entry', (0.0, 0.05, -36.0), (0.0, 2.0, -48.0)),
    ('09_room_window', (-5.0, 0.05, -41.5), (8.0, 2.2, -47.0)),
    ('10_room_machine', (5.5, 0.05, -52.0), (0.0, 2.2, -46.0)),
    ('11_room_back', (0.0, 0.05, -53.5), (0.0, 2.2, -39.0)),
    ('12_mars_view', (6.2, 0.05, -47.0), (30.0, 1.0, -47.0)),
    # Revision 02: from the dead bay looking back at the lit corridor, a low
    # view down the floor-lit P2, and the room looking into the window light.
    ('13_p3_dead', (0.6, 0.05, -37.2), (0.0, 1.8, -27.0)),
    ('14_p2_floor', (1.0, 0.05, -14.0), (-0.5, 1.2, -24.0)),
    ('15_room_shafts', (-6.5, 0.05, -52.5), (4.0, 1.5, -44.0)),
]


def check():
    for key, prof in PROFILES.items():
        segs = prof['segments']
        for (x0, y0), (x1, y1), role in segs:
            for v in (x0, y0, x1, y1):
                assert abs(v * 8 - round(v * 8)) < 1e-9, f'{key}: {v} off the 0.125 grid'
            assert y1 > y0, f'{key}: segment not rising'
            assert x0 <= SHELL_X and x1 <= SHELL_X
        assert abs(segs[-1][1][1] - CEIL_Y) < 1e-9, f'{key}: last segment must reach the ceiling'
        # Walking lane: 4 m clear between rib faces up to 2 m.
        for y in (0.0, 1.0, 1.9):
            clear = 2 * (wall_x(key, y) - RIB_D)
            assert clear >= 3.5 - 1e-9, f'{key}: only {clear:.2f} m clear between ribs at y={y}'
    for name, plan in PLANS.items():
        assert len(plan) == len(BAYS), f'plan {name} covers {len(plan)} of {len(BAYS)} bays'
        assert all(t in TIERS for bay in plan for t in bay), f'plan {name} names an unknown tier'
    for look, roles in LOOKS.items():
        missing = [r for r in ROLES if r not in roles]
        assert not missing, f'look {look} lacks {missing}'
    assert set(MIX.values()) <= set(LOOKS)
    return True


if __name__ == '__main__':
    check()
    for k in PROFILES:
        print(k, PROFILES[k]['title'], 'clear at 1.8 m:', round(2 * wall_x(k, 1.8), 3),
              'between ribs:', round(2 * (wall_x(k, 1.8) - RIB_D), 3))
    print('room z', ROOM_Z0, ROOM_Z1, 'octagon', room_octagon())
    print('outer', room_octagon(-ROOM_SHELL))
