"""Single source of truth for the architecture lab CORNER study.

Revision 06 turned the corridor into four reusable pieces. This module turns a
corner with them. It imports the section rather than restating it, so the plan
and the section cannot disagree - the same rule the section module already has.

Three variants, all a 90 degree left-to-south turn:

    V1 SQUARE   hard 90. Square landing, corridor continues at right angles.
    V2 OUTER    the outer corner is chamfered at 45 so the pocket is not square.
    V3 BOTH     outer corner AND inner elbow chamfered - the walk space itself
                turns through two 45 bends with a short diagonal leg between.

PLAN COORDINATES, metres. Corridor A approaches heading +X with its centreline
on Z = 0. Corridor B leaves heading +Z with its centreline on X = 0. So the
junction sits at the origin, the OUTER corner of the turn is +X / -Z and the
INNER elbow is -X / +Z. That matches the user's sketch: arm in from the left,
arm out to the bottom, chamfer on the top-right.

Two corner words, used precisely throughout:

    OUTER CORNER  the 90 degree pocket you swing wide around. Walls meet at an
                  interior angle of 90. Chamfering it ADDS wall and SHRINKS the
                  turn.
    INNER ELBOW   the 270 degree corner you clip. Chamfering it REMOVES wall and
                  OPENS the turn. This is the one carrying the rib that crowds
                  the racing line.
"""
import math
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import architecture_lab_section as S

GRID = S.GRID

# Plan half-widths, all taken from the section. The corridor is not one width:
# which line matters depends on the height you measure at.
LANE = S.LANE_HALF      # 2.00  protected lane / where the rib toe stands
PLATE = S.FLOOR_HALF    # 2.50  floor plate edge
WIDE = S.WIDEST         # 3.00  widest interior, the panel zone at 1.25 - 2.50

RIB_DEPTH = S.RIB_DEPTH     # 0.50, along the corridor
RIB_PITCH = S.RIB_PITCH     # 4.00

# How far of each corridor the study draws either side of the junction.
ARM = 12.0


# --- the variants ---------------------------------------------------------
# c = outer chamfer, measured along each wall from the square corner.
# d = inner elbow chamfer, same measurement.
#
# c is capped by the lane: the outer chamfer face is the line X - Z = 2*WIDE - c,
# and the outer lane corner (+LANE, -LANE) sits on X - Z = 2*LANE. The chamfer
# reaches the lane when 2*WIDE - c = 2*LANE, so c_max = 2*(WIDE - LANE) = 2.00.
C_MAX = 2.0 * (WIDE - LANE)

VARIANTS = {
    'V1': {'name': 'SQUARE',  'c': 0.0,  'd': 0.0,
           'blurb': 'Hard 90. Square landing, corridor continues at right angles.'},
    'V2': {'name': 'OUTER',   'c': 1.5,  'd': 0.0,
           'blurb': 'Outer corner chamfered at 45. The pocket stops being square.'},
    'V3': {'name': 'BOTH',    'c': 1.5,  'd': 1.5,
           'blurb': 'Outer corner and elbow both chamfered; a short 45 leg between.'},
}


def outer_chain(h, c, arm=ARM):
    """Wall line the long way round the turn, at plan half-width h."""
    if c <= 0:
        return [(-arm, -h), (h, -h), (h, arm)]
    return [(-arm, -h), (h - c, -h), (h, -h + c), (h, arm)]


def inner_chain(h, d, arm=ARM):
    """Wall line around the elbow, at plan half-width h."""
    if d <= 0:
        return [(-arm, h), (-h, h), (-h, arm)]
    return [(-arm, h), (-h - d, h), (-h, h + d), (-h, arm)]


def walk_polygon(h, c, d, arm=ARM):
    """The enclosed walkable region at half-width h, as one closed loop."""
    return outer_chain(h, c, arm) + list(reversed(inner_chain(h, d, arm)))


# --- metrics --------------------------------------------------------------

def diagonal_clear(c, d, h=WIDE):
    """Perpendicular width of the turn measured across the diagonal.

    The outer chamfer face lies on X - Z = 2h - c and the inner elbow face on
    X - Z = -2h - d, so the clear distance between them is the gap between two
    parallel 45 degree lines.
    """
    return (4.0 * h + d - c) / math.sqrt(2.0)


def bulge(c, d, h=WIDE):
    """How much wider the turn is than the straight corridor, as a fraction."""
    return diagonal_clear(c, d, h) / (2.0 * h) - 1.0


def elbow_toe(d):
    """Plan position of the rib toe at the inner elbow.

    With no chamfer the elbow rib toe lands on the lane corner (-LANE, +LANE)
    and is the thing a player clips turning tight. Chamfering the elbow pulls
    that structure back along the diagonal.
    """
    if d <= 0:
        return (-LANE, LANE)
    # The chamfered elbow face carries the rib; its toe sits LANE from the
    # corridor centreline measured perpendicular to the 45 degree face.
    back = d / 2.0
    return (-LANE - back, LANE + back)


def racing_line(c, d):
    """Length of the tightest legal path through the turn, elbow toe to exit.

    Measured between the two points where the lane leaves the straight: from
    (-LANE - 4, ...) style entry is not needed, only the turn itself, so this
    is the path hugging the inner boundary from the entry lane line to the exit
    lane line.
    """
    ex, ez = elbow_toe(d)
    entry = (-LANE - 4.0, -0.0)
    # Path: straight in along the lane, round the elbow toe, straight out.
    a = math.hypot(ex - entry[0], ez - entry[1])
    exit_pt = (0.0, LANE + 4.0)
    b = math.hypot(exit_pt[0] - ex, exit_pt[1] - ez)
    return a + b


def sight_depth(distance_back, c, d, h=WIDE):
    """How far down the exit corridor the far wall is visible.

    The eye is on the approach centreline `distance_back` west of the junction
    centre. The inner elbow is what occludes, so the limiting ray grazes it and
    runs on to the far wall of the exit corridor at X = +h.

    Returns the Z depth at which visibility of the far wall stops, or None when
    the eye is too far back to see any of it.
    """
    if d <= 0:
        gx, gz = -h, h
    else:
        gx, gz = -h - d, h    # the near lip of the chamfer is what grazes first
    ex = -distance_back
    dx, dz = gx - ex, gz
    if dx <= 1e-9:
        return None
    t = (h - ex) / dx
    if t <= 0:
        return None
    return dz * t


# --- how long the 45 degree leg has to be -------------------------------
# Raised by the user: a rib at each end of a chamfer only works if the chamfer
# is long enough to hold them. Too short and the ribs collide; a little longer
# and they clear but read as crowded against the 3.50 m bay used everywhere
# else. Both thresholds fall straight out of the rib depth and pitch.
CLEAR_BAY = RIB_PITCH - RIB_DEPTH        # 3.50 m, the rhythm everywhere else
C_COLLIDE = RIB_DEPTH / math.sqrt(2.0)   # chamfer at which the two ribs touch
C_FULL_BAY = RIB_PITCH / math.sqrt(2.0)  # chamfer that gives a full 3.50 m bay


def chamfer_face(c):
    """Length of the 45 degree face produced by a chamfer of size c."""
    return c * math.sqrt(2.0)


def chamfer_bay(c):
    """Clear run on that face once a rib sits at each end."""
    return chamfer_face(c) - RIB_DEPTH


# A genuine 45 degree LEG - straight, slice, run at 45, slice, straight - is a
# different construction from a chamfer, and it is the user's proposal for
# getting a full bay into the turn. Its governing number is how far apart the
# two walls bend, because the inside of a turn always bends before the outside:
#
#     offset = 2 * h * (sqrt(2) - 1)
#
# That is irrational for every h, so a constant-width 45 degree turn CANNOT put
# all of its vertices on the 0.125 m grid. Snapping to grid costs about a
# centimetre of width, which is invisible; it is recorded here so nobody spends
# an afternoon hunting for the exact number.
def leg_bend_offset(h=WIDE):
    """How far apart, along the approach, the two walls of a 45 turn bend."""
    return 2.0 * h * (math.sqrt(2.0) - 1.0)


def leg_width(offset, h=WIDE):
    """Clear width of the diagonal leg for a given (grid-snapped) bend offset."""
    return (offset + 2.0 * h) / math.sqrt(2.0)


LEG_OFFSET_EXACT = leg_bend_offset()          # 2.4853 m, off grid
LEG_OFFSET = 2.5                              # grid-snapped, 20 x 0.125
LEG_WIDTH = leg_width(LEG_OFFSET)             # 6.0104 m, 1 cm over nominal


def leg_chains(h, m, arm=ARM):
    """Wall lines for a 45 degree LEG whose centreline bends m from the origin.

    Returns (outer, inner). The inner wall bends h*(sqrt2-1) BEFORE the
    centreline and the outer the same distance after it, which is where the
    2*h*(sqrt2-1) separation comes from.
    """
    k = h * (math.sqrt(2.0) - 1.0)
    outer = [(-arm, -h), (-m + k, -h), (h, m - k), (h, arm)]
    inner = [(-arm, h), (-m - k, h), (-h, m + k), (-h, arm)]
    return outer, inner


def wall_bends(c, d):
    """(number of plan direction changes, the mitre half-angles they need)."""
    bends = []
    if c > 0:
        bends += [22.5, 22.5]     # two 45 degree turns on the outer wall
    else:
        bends += [45.0]           # one 90 degree turn
    if d > 0:
        bends += [22.5, 22.5]
    else:
        bends += [45.0]
    return len(bends), bends


def rib_stations(c, d):
    """Where a rib has to stand in the junction.

    A rib at every plan direction change is what removes the 22.5 degree mitre
    problem entirely: the orthogonal wall dies into one rib face and the
    chamfer wall into the next, and the rib stands 0.50 m proud so the joint is
    never seen. It is also structurally honest - a column at every corner.
    """
    out = []
    if c <= 0:
        out.append(('outer corner', (WIDE, -WIDE), 'L-shaped, mitred at 45'))
    else:
        out.append(('outer chamfer, north end', (WIDE - c, -WIDE), 'two faces at 135'))
        out.append(('outer chamfer, east end', (WIDE, -WIDE + c), 'two faces at 135'))
    if d <= 0:
        out.append(('inner elbow', (-WIDE, WIDE), 'solid block, toe on the lane corner'))
    else:
        out.append(('elbow chamfer, west end', (-WIDE - d, WIDE), 'two faces at 135'))
        out.append(('elbow chamfer, south end', (-WIDE, WIDE + d), 'two faces at 135'))
    return out


def metrics(key):
    v = VARIANTS[key]
    c, d = v['c'], v['d']
    n_bends, angles = wall_bends(c, d)
    return {
        'key': key,
        'name': v['name'],
        'c': c,
        'd': d,
        'diagonal': diagonal_clear(c, d),
        'bulge': bulge(c, d),
        'elbow_toe': elbow_toe(d),
        'racing': racing_line(c, d),
        'bends': n_bends,
        'mitres': sorted(set(angles)),
        'ribs': len(rib_stations(c, d)),
        'sight_8': sight_depth(8.0, c, d),
        'sight_12': sight_depth(12.0, c, d),
        'on_grid': all(abs(x / GRID - round(x / GRID)) < 1e-9 for x in (c, d)),
    }


def check():
    problems = []
    S.check()

    for key, v in VARIANTS.items():
        c, d = v['c'], v['d']
        for label, val in (('c', c), ('d', d)):
            if abs(val / GRID - round(val / GRID)) > 1e-9:
                problems.append(f'{key}: {label}={val} is off the {GRID} m grid')
        if c > C_MAX + 1e-9:
            problems.append(f'{key}: outer chamfer {c} exceeds {C_MAX} and cuts the lane corner')

        # Every variant must still carry the protected lane round the turn.
        if diagonal_clear(c, d) < 2 * LANE - 1e-9:
            problems.append(f'{key}: diagonal clear {diagonal_clear(c, d):.3f} is under the {2*LANE} m lane')

        # The elbow rib must never stand inside the lane.
        ex, ez = elbow_toe(d)
        if -ex < LANE - 1e-9 or ez < LANE - 1e-9:
            problems.append(f'{key}: elbow rib toe {ex, ez} intrudes on the lane')

        # A 45 degree plan chamfer keeps its endpoints on the grid; anything
        # else does not, and that is the whole reason 45 was chosen.
        if c > 0 and abs((WIDE - c) / GRID - round((WIDE - c) / GRID)) > 1e-9:
            problems.append(f'{key}: outer chamfer start is off grid')
        if d > 0 and abs((WIDE + d) / GRID - round((WIDE + d) / GRID)) > 1e-9:
            problems.append(f'{key}: elbow chamfer end is off grid')

    if problems:
        raise SystemExit('CORNER CHECK FAILED:\n  ' + '\n  '.join(problems))
    return True


# --- the repetition test --------------------------------------------------
# A separate question from the corner: how much straight corridor can a player
# take before the rhythm goes numb? The answer has to be a NUMBER, because it
# becomes a level-design rule - beyond this length, something must interrupt.
#
# The built lab run is 24.5 m, which is six bays. This lays out a long run in
# the same kit with marked decision points, so the walk can be judged rather
# than guessed.
REPEAT_RUN = 52.0                      # thirteen 4 m bays
REPEAT_MARKS = [12.0, 20.0, 28.0, 36.0, 44.0, 52.0]
INTERRUPTS = [
    ('CORNER',  'Full sight block. Resets the view completely.'),
    ('T',       'Sight block plus a choice. Most expensive.'),
    ('DOOR',    'Sight block that can be locked. Also a pacing gate.'),
    ('PORTAL',  'Two bays merged. Widens without turning; a soft break.'),
    ('WINDOW',  'Relieves sight instead of blocking it.'),
    ('ALCOVE',  'Ground given at one bay. Cover and width.'),
]


if __name__ == '__main__':
    check()
    print(f'lane {2*LANE:.2f}  plate {2*PLATE:.2f}  widest {2*WIDE:.2f} m')
    print(f'outer chamfer cap  c_max = {C_MAX:.2f} m (beyond it the chamfer cuts the lane corner)\n')
    hdr = f"{'':4} {'name':7} {'c':>5} {'d':>5} {'diag':>6} {'bulge':>7} {'racing':>7} {'ribs':>5} {'mitres':>12}"
    print(hdr)
    print('-' * len(hdr))
    for key in VARIANTS:
        m = metrics(key)
        mit = '/'.join(f'{a:g}' for a in m['mitres'])
        print(f"{m['key']:4} {m['name']:7} {m['c']:5.2f} {m['d']:5.2f} {m['diagonal']:6.2f} "
              f"{m['bulge']*100:6.1f}% {m['racing']:7.2f} {m['ribs']:5d} {mit:>12}")
    print()
    for key in VARIANTS:
        m = metrics(key)
        print(f"{key} sight depth down the exit: {m['sight_8']:.1f} m from 8 m back, "
              f"{m['sight_12']:.1f} m from 12 m back")
    print('\ncorner check passed')


# --- the built walk --------------------------------------------------------
# One centreline carrying both open experiments: a long straight for the
# repetition test, then a square 90 (V1), then a 45 degree leg (V4).
#
# This lives in the module, not in the generator, because the map generator AND
# the scene writer both need the same rib and light stations. The lab has been
# bitten once by a helper that recomputed something the table already knew.
WALK_PATH = [
    (0.0, -2.0),      # sealed start
    (0.0, 52.0),      # V1  - one 90 degree vertex, the square landing
    (20.0, 52.0),     # V4  - first 45 degree vertex
    (24.0, 48.0),     # V4  - second 45 degree vertex
    (24.0, 20.0),     # sealed end, 10 m past the T so it reads as a through route
]
WALK_CORNERS = {1: 'V1 SQUARE', 2: 'V4 LEG in', 3: 'V4 LEG out'}

# The T. Playtest 01: a junction is SQUARE, because chamfering two elbows opens
# the middle and turns a decision point into a lobby. A T has two inner elbows
# and no outer corner, so the bisector rule that built V1 and V4 does not apply
# here - a bisector needs exactly two directions and this has three. The branch
# is therefore its own corridor whose walls start at the through corridor's wall
# line, and the through corridor simply omits its wall across the opening.
T_AT = (24.0, 30.0)         # on the last segment, which runs -Z
T_DIR = (1.0, 0.0)          # the branch heads +X
T_LENGTH = 16.0             # out to X = 40, sealed


# How far from a junction centre the first rib stands, on EVERY arm.
# 1.5 pitches. Chosen because it is what the V1 corner already does - its
# skipped stations leave ribs exactly 6.00 m either side of the vertex, and the
# user walked that and said the beat felt right - and because it is the average
# of what the T was doing unaided (5.66 m and 6.34 m on the through arms).
# It leaves 2.75 m of clear wall between the opening jamb and the rib face.
JUNCTION_SETBACK = 1.5 * RIB_PITCH


def t_centre_distance():
    """Path distance along the through corridor to the junction centre."""
    seg, _, t0, t1 = t_opening()
    _, cum, _ = walk_metrics()
    return cum[seg] + (t0 + t1) / 2.0


def t_pins():
    """(through pins, branch first-station) giving every arm the same setback."""
    c = t_centre_distance()
    return [c - JUNCTION_SETBACK, c + JUNCTION_SETBACK], JUNCTION_SETBACK


def t_exclusions():
    """(through spans, branch spans) where no rib or fitting may stand.

    On the through corridor that is the opening itself, widened by the rib
    depth. On the branch it is everything inboard of the through corridor's
    wall line, which is inside the junction rather than in the branch.
    """
    c = t_centre_distance()
    guard = JUNCTION_SETBACK + RIB_PITCH / 2.0
    return ([(c - guard, c + guard)], [(0.0, WIDE + RIB_DEPTH)])


def t_branch_path():
    """Centreline of the branch, from the through corridor's centreline out."""
    return [T_AT, (T_AT[0] + T_DIR[0]*T_LENGTH, T_AT[1] + T_DIR[1]*T_LENGTH)]


def t_opening():
    """(segment, signed offset, t0, t1) of the hole in the through wall.

    The branch is WIDE either side of its centreline, so the opening spans that
    much of the through corridor, and it is on whichever side the branch leaves.
    """
    path = WALK_PATH
    seg = len(path) - 2
    a, b = path[seg], path[seg+1]
    d = _unit((b[0]-a[0], b[1]-a[1]))
    nrm = (d[1], -d[0])                     # right of travel, matching run()
    t_at = (T_AT[0]-a[0])*d[0] + (T_AT[1]-a[1])*d[1]
    side = 1.0 if (T_DIR[0]*nrm[0] + T_DIR[1]*nrm[1]) > 0 else -1.0
    return seg, side, t_at - WIDE, t_at + WIDE


def _unit(v):
    l = math.hypot(v[0], v[1])
    return (v[0]/l, v[1]/l)


def walk_metrics(path=None):
    path = path or WALK_PATH
    seglen = [math.dist(a, b) for a, b in zip(path, path[1:])]
    cum = [0.0]
    for L in seglen:
        cum.append(cum[-1] + L)
    return seglen, cum, cum[-1]


def seg_dirs(path=None):
    path = path or WALK_PATH
    return [_unit((b[0]-a[0], b[1]-a[1])) for a, b in zip(path, path[1:])]


def turn_at(i, path=None):
    """Interior turn angle in radians at vertex i; 0 at the two ends."""
    path = path or WALK_PATH
    if i in (0, len(path)-1):
        return 0.0
    d = seg_dirs(path)
    a, b = d[i-1], d[i]
    return math.acos(max(-1.0, min(1.0, a[0]*b[0] + a[1]*b[1])))


def turn_clearance(i, path=None):
    """How far from a vertex a rib must stay.

    A mitred end cuts the wall diagonally, reaching SHELL_BACK*tan(half the
    turn) back along each segment, so a rib inside that would poke through the
    cut. Zero at the sealed ends, which are cut square.
    """
    path = path or WALK_PATH
    if i in (0, len(path)-1):
        return 0.0
    return S.SHELL_BACK * math.tan(turn_at(i, path)/2) + RIB_DEPTH


def world(seg, t, s, path=None):
    """(X, Z) in godot metres for a point t along segment `seg`, s to its right."""
    path = path or WALK_PATH
    a, b = path[seg], path[seg+1]
    d = _unit((b[0]-a[0], b[1]-a[1]))
    n = (d[1], -d[0])
    return (a[0] + t*d[0] + s*n[0], a[1] + t*d[1] + s*n[1])


def _locate(d, path=None):
    path = path or WALK_PATH
    seglen, cum, _ = walk_metrics(path)
    seg = max(i for i in range(len(seglen)) if cum[i] <= d + 1e-9)
    return min(seg, len(seglen)-1), d - cum[min(seg, len(seglen)-1)]


def _excluded(d, exclude):
    return any(lo <= d <= hi for lo, hi in exclude)


def rib_stations_walk(path=None, exclude=(), pins=(), start=None):
    """Ribs on ONE global rhythm measured along the centreline, so the beat
    carries across every turn rather than restarting after it. Returns
    (placed, skipped); a station inside a turn is skipped, not nudged.

    `exclude` is spans of path distance where a rib cannot stand at all - the
    T's opening, where one of the two walls it would need is simply not there.
    """
    path = path or WALK_PATH
    _, cum, total = walk_metrics(path)
    placed, skipped = [], []
    d = RIB_PITCH if start is None else start
    while d < total:
        if (min(abs(d - cum[i]) - turn_clearance(i, path) for i in range(len(path))) < 0
                or _excluded(d, exclude)):
            skipped.append(d)
        else:
            seg, t = _locate(d, path)
            placed.append((d, seg, t))
        d += RIB_PITCH
    # Pinned stations are placed regardless of the beat. They exist so every arm
    # of a junction shows the SAME distance from the opening to its first rib -
    # the beat cannot deliver that on its own, because a junction does not land
    # on it.
    for d in pins:
        if 0.0 < d < total:
            seg, t = _locate(d, path)
            placed.append((d, seg, t))
    placed.sort()
    return placed, skipped


# Playtest 2026-09-22: the user walked it and was "a little sketch" on the unlit
# bays - the CEILING goes dark in an off bay, which is what reads wrong rather
# than the wall. Their suggestion was to light every section and lower each
# light to compensate. Both plans are kept so the comparison can be re-run
# rather than argued about.
#
# energy_scale exists because doubling the number of fittings roughly doubles
# the illumination: a 13 m range against a 4 m pitch already spills a bay and a
# half either side, so every-bay lighting has to come down or it blows out.
LIGHT_PLANS = {
    'alternate': {'cycle': ['lit', 'off'], 'energy_scale': 1.00},
    'every_bay': {'cycle': ['lit'],        'energy_scale': 0.62},
}
# Playtest 01 settled it: LIT BY DEFAULT, OFF BY DELIBERATION. An off bay stops
# being a rhythm and becomes what it was always meant to be - a broken fitting,
# used rarely and on purpose. See FR-006 for making that dynamic in a mission.
LIGHT_PLAN = os.environ.get('REDBREACH_LIGHT_PLAN', 'every_bay')
if LIGHT_PLAN not in LIGHT_PLANS:
    raise SystemExit(f'unknown REDBREACH_LIGHT_PLAN {LIGHT_PLAN!r}; '
                     f'expected one of {sorted(LIGHT_PLANS)}')


def light_energy(tier):
    """Tier energy after the active plan's scale. Read from the tier table."""
    return S.LIGHT_TIERS[tier]['energy'] * LIGHT_PLANS[LIGHT_PLAN]['energy_scale']


def light_stations_walk(path=None, rib_exclude=(), light_exclude=(),
                        rib_pins=(), rib_start=None):
    """One fitting per bay, at the bay's midpoint. The tier cycles through the
    active plan, whose names are checked against S.LIGHT_TIERS - never through
    hardcoded names, which is how this lab once generated zero lights."""
    path = path or WALK_PATH
    _, _, total = walk_metrics(path)
    # A rib needs two walls; a FITTING only needs a ceiling. Excluding lights
    # wherever a rib could not stand left the T junction - the decision point,
    # and the place a player most needs to read - as the darkest spot in the
    # whole corridor. The two exclusions are therefore separate.
    placed, _ = rib_stations_walk(path, rib_exclude, rib_pins, rib_start)
    cycle = LIGHT_PLANS[LIGHT_PLAN]['cycle']
    unknown = [t for t in cycle if t not in S.LIGHT_TIERS]
    if unknown:
        raise SystemExit(f'light plan {LIGHT_PLAN!r} names tiers not in LIGHT_TIERS: {unknown}')
    edges = [0.0] + [p[0] for p in placed] + [total]
    out = []
    for i, (d0, d1) in enumerate(zip(edges, edges[1:])):
        if d1 - d0 < S.STRIP_LEN + 0.5:
            continue
        mid = (d0 + d1) / 2
        if _excluded(mid, light_exclude):
            continue
        seg, t = _locate(mid, path)
        out.append((mid, seg, t, cycle[i % len(cycle)]))
    if not any(light_energy(tier) > 0 for *_, tier in out):
        raise SystemExit('no lit bays generated - tier names out of step with LIGHT_TIERS')
    return out
