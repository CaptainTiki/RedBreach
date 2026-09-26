"""Kit lab K-01: paper-plan geometry, the single source of truth for Phase 2.

Phase 2 of docs/clean-slate-test-plan.md, in the Phase 1 style
(docs/style-lab.md, "Phase 1 settled"). This module holds the PLAN: piece
list, layout, heights and the questions each piece answers. The drawing
(tools/draw-kit-lab-plan.py) reads it now; the bootstrap will read it once the
plan is approved.

Plan coordinates are metres with x east and y NORTH. The build maps them to
Godot as (x, height, -y). Floors are at 0 unless a piece says otherwise.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import style_lab as S

# --- tested dimensions that bind the kit ------------------------------------
CAPSULE_R, STAND_H, CROUCH_H = 0.3, 1.8, 1.1     # gym_player.tscn / .gd
BUG_NAV_R, BUG_NAV_H = 1.0, 1.9                  # the larger bugs' navigation clearance
RISER, TREAD, LANDING = 0.25, 0.5, 2.0           # the freight stair schedule
DOOR = {'personnel': (2.0, 2.46), 'wide': (3.0, 3.16)}   # interaction/sliding_door*.tscn openings
CROUCH_CLEAR = 1.4                               # blocks a 1.8 m stand; passes a 1.1 m crouch with margin

# --- pieces -----------------------------------------------------------------
# Each piece names the plan question it answers (clean-slate-test-plan.md).
PIECES = {
    'A0': dict(name='Arrival vestibule', kind='room', q='quiet arrival; sealed airlock door'),
    'C1': dict(name='P1 straight', kind='corridor', profile='P1', q='signature corridor, 12 m module'),
    'J1': dict(name='Junction hub', kind='hub', q='B1: T and 4-way replaced by an octagon with bulkhead ports'),
    'C2': dict(name='P1 north', kind='corridor', profile='P1', q='approach to the turn'),
    'T1': dict(name='P1 45-degree turn', kind='turn', profile='P1', q='B1: trapezoid mitre on the bisector, no fill'),
    'C3': dict(name='P1 east with debris', kind='corridor', profile='P1', q='B4: walk-around interrupter'),
    'D1': dict(name='Fallen rib and panels', kind='interrupter', q='B4: forces a detour; bug-sized lane kept'),
    'H1': dict(name='Knee-wall hall', kind='hall', q='B3: hall scale; room as a height transition'),
    'C5': dict(name='P2 east', kind='corridor', profile='P2', q='secondary profile, 16 m'),
    'T2': dict(name='P2 45-degree turn', kind='turn', profile='P2', q='B1: knee-wall mitre'),
    'S1': dict(name='P2 stair, +3 m', kind='stair', profile='P2', q='stairs in the kit: landings and a reveal'),
    'C4': dict(name='P2 west with crouch passage', kind='corridor', profile='P2', q='B4: crouch interrupter'),
    'X1': dict(name='Collapsed section', kind='interrupter', q='B4: 1.4 m clear; stand blocked, crouch passes'),
    'R1': dict(name='Small control room', kind='room', q='B3: small scale; personnel door; threshold step'),
}

# --- layout (plan metres, x east / y north) -----------------------------------
# 8 x 6 x 4.5 m: tall enough for a full P1 corridor to open into it.
A0 = dict(x0=-4.0, x1=4.0, y0=-3.0, y1=3.0, ceil=4.5, look='steel')
C1 = dict(axis='y', x=0.0, y0=3.0, y1=15.0, look='steel')
HUB = dict(cx=0.0, cy=23.0, flats=14.0, clip=3.5, ceil=5.0, look='steel',
           ports={'S': (0.0, 16.0), 'N': (0.0, 30.0), 'E': (7.0, 23.0), 'W': (-7.0, 23.0)})
BULKHEAD = S.BULKHEAD_LEN
# North branch: P1 north, a 45-degree leg, then east into the hall's floor door.
C2 = dict(axis='y', x=0.0, y0=31.0, y1=42.0, look='concrete')
T1 = dict(a=(0.0, 42.0), b=(4.0, 46.0), look='concrete')       # centreline of the 45-degree leg
C3 = dict(axis='x', y=46.0, x0=4.0, x1=15.0, look='concrete')
D1 = dict(x0=8.0, x1=12.0, side='north', clear_lane=2.4)      # debris fills the north side
# East branch: P2 east, a 45-degree leg north, then the stair up to the catwalk.
C5 = dict(axis='x', y=23.0, x0=8.0, x1=26.0, look='steel')
T2 = dict(a=(26.0, 23.0), b=(30.0, 27.0), look='steel')
S1 = dict(axis='y', x=30.0, y0=27.0, rise=3.0, look='steel')  # landing, flight, landing, bulkhead
S1_RISERS = int(round(S1['rise'] / RISER))
S1_FLIGHT = S1_RISERS * TREAD
S1['y1'] = S1['y0'] + LANDING + S1_FLIGHT + LANDING         # 27 -> 37, then the hall's bulkhead
# Hall: a knee-wall nave. Vertical walls to 6 m carry the catwalk; slopes
# above, in to a 10 m ceiling. Portal-frame ribs every 8 m.
# H1's shape is THIS hall's, derived from what it holds (catwalk on the
# vertical knee walls, tall machinery). It is not a template for halls.
HALL = dict(x0=16.0, x1=40.0, y0=38.0, y1=70.0, knee=6.0, ceil=10.0, ceil_half=8.0,
            frames=(44.0, 52.0, 60.0), frame_d=0.6, look='concrete', machine_look='warm',
            floor_door=('W', 46.0, 'wide'), upper_door=('S', 30.0))
CATWALK = dict(level=3.0, width=3.0, runs=[('S', 22.0, 40.0), ('E', 38.0, 62.0)])
HALL_STAIR = dict(x=38.5, y0=62.0, y1=62.0 + S1_FLIGHT, width=3.0)   # east wall, down to the NE floor
HALL_TANKS = [(28.0, 50.0), (28.0, 58.0)]                       # warm machinery islands, 4 m clear round
HALL_FLOOR_HATCH = (21.0, 58.0)
# West branch: P2 west through a collapsed section to a small control room.
C4 = dict(axis='x', y=23.0, x0=-24.0, x1=-8.0, look='warm')
X1 = dict(x0=-17.0, x1=-14.0, clear_w=2.0, clear_h=CROUCH_CLEAR)
# R1 is composed from its contents: a console row facing a 5 m Mars window,
# standing room behind, a personnel door opposite. Its walls follow that:
# 8 m deep and 7 m wide, with the two window corners clipped to frame the view.
R1 = dict(cx=-28.5, cy=23.0, flats=7.0, clip=1.0, x0=-32.5, x1=-24.5, y0=19.5, y1=26.5,
          floor=RISER, ceil=3.5, look='warm', door=('E', 'personnel'), window='W',
          window_span=(21.0, 25.0), sill=1.0, head=2.75, consoles=(-31.4, 20.5, 25.5))

# Sealed hatch reservations (question D2), paper only.
HATCHES = [('ceiling', 'C2', (0.0, 37.0)), ('wall', 'C5', (18.0, 23.0 - 3.0)), ('floor', 'H1', HALL_FLOOR_HATCH),
           ('ceiling', 'J1', (0.0, 23.0))]
HATCH_APERTURE, HATCH_RING = 2.5, 0.25
# The dotted grate is a feature set 0.125 m down, never a whole floor (user rule).
GRATE_DEPTH = 0.125

# --- build data -------------------------------------------------------------
# Corridor RUNS as plan polylines. Interior vertices are mitred on the
# bisector (the approved V4 rule); collinear vertices only change the floor
# slope, which is how the stair's landings and flight are expressed. Ribs sit
# at distances along the run, never inside a bend. Rib feet drop straight to
# the floor, flush with the rib above (user rule).
RUNS = {
    # Runs now reach the room's INNER face: the room wall is cut to the
    # corridor's profile and the corridor passes through it (user, 2026-09-26).
    'C1': dict(profile='P1', look='steel', path=[(0.0, 3.0), (0.0, 16.0)], heights=[0, 0], ribs=[4.5, 8.5]),
    'North': dict(profile='P1', look='concrete', path=[(0.0, 30.0), (0.0, 42.0), (4.0, 46.0), (16.0, 46.0)],
                  heights=[0, 0, 0, 0], ribs=[5.0, 9.0, 12.0 + 2.8284, 17.657 + 2.0],
                  fallen=17.657 + 6.0),
    'East': dict(profile='P2', look='steel',
                 path=[(7.0, 23.0), (26.0, 23.0), (30.0, 27.0), (30.0, 29.0), (30.0, 35.0), (30.0, 38.0)],
                 heights=[0, 0, 0, 0, 3.0, 3.0], ribs=[5.0, 9.0, 13.0, 17.0, 19.0 + 2.8284, 24.657 + 4.0, 24.657 + 8.0],
                 stair=(3, 4)),
    'C4': dict(profile='P2', look='warm', path=[(-7.0, 23.0), (-24.0, 23.0)], heights=[0, 0], ribs=[5.0, 13.0]),
}
# Corridor-to-room JUNCTIONS (user, 2026-09-26: no flat accent slab). The room
# wall is cut to the corridor's own profile and the corridor's RIB stands at
# the room face as the connection, with a low sill under it that carries any
# floor-texture change.
#   open                the profile opening, framed by the rib
#   door:<kind>         a profile-shaped panel in the opening holds the door
#   door_low:<kind>     the room is lower than the corridor: the room wall
#                       gets a door-sized hole (and the door); the corridor
#                       ends in its rib and a profile-shaped plug
# (name, plan point on the room's INNER face, unit direction into the room,
#  floor height, kind, run, which end of the run)
JUNCTIONS = [
    ('A0 port', (0.0, 3.0), (0, -1), 0.0, 'open', 'C1', 'start'),
    ('Hub S', (0.0, 16.0), (0, 1), 0.0, 'open', 'C1', 'end'),
    ('Hub N', (0.0, 30.0), (0, -1), 0.0, 'open', 'North', 'start'),
    ('Hub E', (7.0, 23.0), (-1, 0), 0.0, 'open', 'East', 'start'),
    ('Hub W', (-7.0, 23.0), (1, 0), 0.0, 'open', 'C4', 'start'),
    ('Hall upper', (30.0, 38.0), (0, 1), 3.0, 'open', 'East', 'end'),
    ('Hall floor door', (16.0, 46.0), (1, 0), 0.0, 'door:wide', 'North', 'end'),
    ('R1 door', (-24.5, 23.0), (-1, 0), 0.0, 'door_low:personnel', 'C4', 'end'),
]
SILL_H = 0.0625
ROOM_WALL = 0.5
DOOR_OPENING = {'personnel': (1.0, 2.5), 'wide': (1.5, 3.2)}   # half width, height
DOOR_DEPTH = 0.5
# D1 debris: the rib at 'fallen' lies across the north side of C3.
D1_FALL = dict(station_x=10.0, y=46.0)
# X1: 3 m of C4 slumped to a 2.0 x 1.4 m gap.

# --- validation markers (read by tools/validate_markers.gd) -----------------
# (x, y, height) plan points. Routes are walked by the real player.
ROUTES = {
    'loop': [(0, 0, 0, 'stand'), (0, 9.5, 0, 'stand'), (0, 20.0, 0, 'stand'), (4.0, 23.0, 0, 'stand'),
             (17.0, 23.0, 0, 'stand'), (28.0, 25.0, 0, 'stand'), (30.0, 28.0, 0, 'stand'), (30.0, 36.0, 3.0, 'stand'),
             (30.0, 39.5, 3.0, 'stand'), (38.4, 39.5, 3.0, 'stand'), (38.4, 61.0, 3.0, 'stand'),
             (38.4, 69.0, 0, 'stand'), (33.0, 66.0, 0, 'stand'), (22.0, 55.0, 0, 'stand'), (18.5, 46.0, 0, 'stand'),
             (13.0, 44.3, 0, 'stand'), (7.0, 44.3, 0, 'stand'), (2.2, 44.0, 0, 'stand'), (0.0, 40.0, 0, 'stand'),
             (0.0, 33.0, 0, 'stand'), (0.0, 25.5, 0, 'stand')],
    'spur': [(-4.0, 23.0, 0, 'stand'), (-12.5, 23.0, 0, 'stand'), (-13.5, 23.0, 0, 'crouch'),
             (-15.5, 23.0, 0, 'crouch'), (-17.5, 23.0, 0, 'crouch'), (-19.5, 23.0, 0, 'stand'),
             (-23.0, 23.0, 0, 'stand'), (-26.5, 23.0, RISER, 'stand'), (-29.5, 23.0, RISER, 'stand')],
}
PROBES = [('stand_clear', 0, (0, 9.5, 0)), ('stand_clear', 0, (0, 23.0, 0)), ('stand_clear', 0, (17.0, 23.0, 0)),
          ('stand_clear', 0, (30.0, 36.0, 3.0)), ('stand_clear', 0, (38.4, 50.0, 3.0)), ('stand_clear', 0, (24.0, 64.0, 0)),
          ('stand_clear', 0, (10.0, 44.3, 0)), ('stand_clear', 0, (-11.0, 23.0, 0)), ('stand_clear', 0, (-28.5, 23.0, RISER)),
          ('crouch_only', 0, (-15.5, 23.0, 0)),
          ('headroom', 2.2, (30.0, 32.25, 1.75)), ('headroom', 2.4, (38.4, 50.0, 0)), ('headroom', 5.0, (0, 23.0, 0)),
          ('headroom', 3.2, (-28.5, 23.0, RISER)), ('headroom', 3.5, (0, 9.5, 0))]
# Deliberately dark zones (rb_dark): the light floor is waived here, on purpose.
DARK_ZONES = [((11.0, 46.0, 0.0), 5.0, 'fallen rib: failing and dead fittings'),
              ((-15.5, 23.0, 0.0), 4.5, 'collapse: dead bay under an emergency beacon')]

# Capture views: (name, plan eye point (x, y, floor height), plan look-at (x, y, height), crouch).
VIEWS = [
    ('01_arrival', (0.0, -1.5, 0.0), (0.0, 14.0, 1.6), False),
    ('02_rib_feet_p1', (-1.3, 5.2, 0.0), (2.6, 7.6, 0.55), False),
    ('03_hub', (0.0, 18.2, 0.0), (0.0, 30.0, 2.2), False),
    ('04_hub_diagonal', (-2.0, 20.0, 0.0), (5.5, 28.5, 2.4), False),
    ('05_turn_approach', (0.0, 33.0, 0.0), (3.0, 45.5, 1.6), False),
    ('06_turn_leg', (-0.6, 41.0, 0.0), (8.0, 46.0, 1.4), False),
    ('07_debris', (5.2, 44.6, 0.0), (11.0, 47.2, 0.8), False),
    ('08_c5_p2', (9.0, 23.0, 0.0), (25.0, 23.0, 1.6), False),
    ('09_stair_up', (30.0, 27.6, 0.0), (30.0, 37.0, 3.6), False),
    ('10_landing_reveal', (30.0, 36.4, 3.0), (30.0, 56.0, 1.2), False),
    ('11_catwalk_overlook', (38.4, 47.0, 3.0), (24.0, 58.0, 0.0), False),
    ('12_hall_floor', (19.0, 40.0, 0.0), (32.0, 62.0, 3.0), False),
    ('13_hall_stair', (32.5, 68.8, 0.0), (38.4, 62.0, 3.6), False),
    ('14_collapse_approach', (-9.5, 23.0, 0.0), (-16.0, 23.0, 1.0), False),
    ('15_crouch_inside', (-13.8, 23.0, 0.0), (-20.0, 23.0, 0.8), True),
    ('16_r1_console', (-25.6, 23.0, RISER), (-32.0, 23.0, 1.6), False),
    ('17_r1_window', (-29.8, 21.4, RISER), (-40.0, 25.5, 0.2), False),
    ('18_rib_feet_p2', (10.6, 22.2, 0.0), (12.1, 20.3, 0.5), False),
    ('19_hub_port', (-2.5, 23.0, 0.0), (7.0, 23.0, 2.0), False),
    ('20_hall_door_inside', (22.5, 46.8, 0.0), (16.0, 46.0, 1.8), False),
    ('21_r1_door_corridor', (-19.8, 23.0, 0.0), (-24.2, 23.0, 1.5), False),
    ('22_catwalk_entry', (35.0, 40.2, 3.0), (30.0, 38.0, 5.0), False),
    ('23_a0_port', (0.0, -2.2, 0.0), (0.0, 3.0, 2.0), False),
    ('24_hub_from_corridor', (0.0, 11.5, 0.0), (0.0, 20.0, 2.0), False),
]

NAV_PAIRS = [('hub_to_hall_floor', 'connect', (0, 23.0, 0), (24.0, 64.0, 0)),
             ('hall_floor_to_catwalk', 'connect', (33.0, 68.0, 0), (38.4, 50.0, 3.0)),
             ('hub_to_r1_through_collapse', 'blocked', (-4.0, 23.0, 0), (-28.5, 23.0, RISER)),
             ('hub_to_c3_round_debris', 'connect', (0, 33.0, 0), (13.0, 44.3, 0))]

# Lighting per the settled style sheet; the interrupters carry the damage.
LIGHTING = {
    'corridors': 'ceiling-edge strips + wall lights',
    'D1 debris': 'flicker with sparks over the fall; one dead bay',
    'X1 collapse': 'dead, red emergency beacon',
    'H1 hall': 'high-bay fittings on the portal frames; floor strips on the catwalk edge',
    'S1 stair': 'wall lights on each landing',
    'R1 room': 'low office fittings; the window',
}

LOOP = ['A0', 'C1', 'J1', 'C5', 'T2', 'S1', 'H1 catwalk', 'H1 stair', 'H1 floor', 'C3', 'D1', 'T1', 'C2', 'J1']
SPUR = ['J1', 'C4', 'X1', 'R1']


def check():
    assert S1_RISERS * RISER == S1['rise']
    assert X1['clear_h'] - CROUCH_H >= 0.25 and X1['clear_h'] < STAND_H, 'crouch passage must block standing'
    assert D1['clear_lane'] >= 2 * BUG_NAV_R, 'debris must leave a bug-sized lane'
    assert HALL['y1'] - HALL['y0'] <= 2 * (HALL['x1'] - HALL['x0']), 'hall proportion'
    for d in DOOR.values():
        assert d[0] < 2 * S.OPENING_HALF and d[1] < S.OPENING_TOP + 0.01
    return True


if __name__ == '__main__':
    check()
    print('S1:', S1_RISERS, 'risers,', S1_FLIGHT, 'm flight, y', S1['y0'], '->', S1['y1'])
    print('loop:', ' > '.join(LOOP))
