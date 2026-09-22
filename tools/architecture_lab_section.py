"""Single source of truth for the architecture lab corridor section.

Revision 06. The corridor is four reusable pieces, not one carved profile:

    FLOOR   half plate, centre to wall foot
    WALL    floor edge up to the ceiling spring
    CEILING half soffit, wall top to centre
    RIB     a pilaster on a battered base, floor to ceiling

Half a corridor is FLOOR + WALL + CEILING. Mirror it for the other side.
The RIB drops in at each station without changing any of the three.

Coordinates are (horizontal distance from corridor centre, height) in metres,
RIGHT side, so the chains read left-to-right as you look at the drawing.
Every value is a multiple of 0.125 m = 4 map units at 32 units/metre.

Transitions are chamfered rather than stepped: 45 degrees everywhere the
player cannot stand, and steeper where they can, which keeps the geometry
clear of Godot's floor_max_angle default.
"""
import math

GRID = 0.125

LANE_HALF = 2.0            # protected movement envelope
LANE_HEIGHT = 3.2
FLOOR_HALF = 2.50          # half the walking plate: 5.00 m overall
CEIL_HALF = 2.25           # half the flat soffit: 4.50 m overall
CEIL_Y = 3.75
WIDEST = 3.00              # 6.00 m widest interior
RIB_SOFFIT_Y = 3.5
RIB_SOFFIT_HALF = 2.25
RIB_PITCH = 4.0            # one rib every four 1 m texture repeats
RIB_DEPTH = 0.5            # so 3.5 m of clear bay between ribs
KNEE = 0.5                 # where the rib toe stops being vertical
SHELL_BACK = 3.50          # outer face of the wall solids
SUBFLOOR_Y = -0.375
CEILING_TOP = 4.25

# --- the three pieces of half a corridor ----------------------------------
FLOOR = [(0.0, 0.0), (FLOOR_HALF, 0.0)]

WALL = [
    (2.50, 0.000),   # meets the floor plate
    (2.75, 0.500),   # base kick            63.43, the one the player can touch
    (2.75, 0.875),   # plinth face
    (3.00, 1.250),   # chamfer out          56.31, steeper than the 45 default
    (3.00, 2.500),   # main panel, 1.25 m tall, spans eye height
    (2.75, 2.750),   # chamfer in           45
    (2.75, 3.250),   # upper wall
    (2.25, 3.750),   # ceiling chamfer      45
]

CEILING = [(CEIL_HALF, CEIL_Y), (0.0, CEIL_Y)]

# --- the rib --------------------------------------------------------------
# It runs to the floor on a battered base. The toe sits exactly on the
# protected lane line, so the clear width between opposite toes IS the 4.00 m
# lane - the pillars define it rather than being placed near it. The corridor
# was widened 0.50 m overall purely to buy the base its 0.50 m flare.
#
# The toe is VERTICAL to knee height and the batter starts above it, so the
# only thing the player capsule meets below 0.50 m is a wall face. The batter
# itself is 51.34 deg, still clear of the 45 deg floor_max_angle default.
# Flare divided by rise IS the angle, so a wide flare and a low foot are in
# direct conflict: going flatter to lower the foot is exactly what would make
# the capsule treat it as a walkable slope.
RIB = [
    (2.00, 0.000),   # toe, on the lane line
    (2.00, 0.500),   # toe face, vertical to knee height
    (2.50, 1.125),   # battered base             51.34
    (2.50, 3.250),   # shaft face
    (2.25, 3.500),   # chamfer                   45
    (0.0,  3.500),   # beam soffit, half
]

# --- the run's lighting plan ----------------------------------------------
# Every bay carries a fitting. What changes per bay is whether that fitting is
# ON, and an OFF fitting must not use an emissive material - a strip that
# glows while its bay stays dark reads as a mistake, because a fixture that is
# emitting should be lighting something.
#
#   lit   emissive strip + a shadowed light
#   off   dark fitting, no light at all - the bay is lit only by spill
#
# Contrast between the two is managed with light RANGE rather than ambient.
# Raising ambient lifts everything and flattens the corridor straight back to
# a greybox; a long range lets the working fittings spill into their
# neighbours, which softens the falloff and throws rib-beam shadows across the
# dark bays into the bargain.
BAY_LIGHTS = {0: 'lit', -4: 'off', -8: 'lit', -12: 'off', -16: 'lit', -20: 'off'}
LIGHT_TIERS = {
    'lit': {'tex': 'greybox/Emissive/texture_01', 'energy': 1.40, 'shadow': True,  'range': 13.0},
    'off': {'tex': 'greybox/GreyCharcoal/texture_01', 'energy': 0.0, 'shadow': False, 'range': 0.0},
}
STRIP_X = 1.75          # inboard edge of the strip; 0.125 wide
STRIP_LEN = 2.0         # short, in a 3.5 m bay
STRIP_INSET = 0.125     # how far up inside the coffer the face sits

# Height of the light node itself, which is NOT the height of the fitting.
# Sitting it just under the soffit left the ceiling in shadow: light striking a
# large flat plane from 0.17 m below hits it at a grazing angle and N.L
# collapses a short distance away. Dropping the node improves that angle across
# the whole ceiling for free. Emissive materials do not illuminate anything in
# Godot without GI, so the strip is cosmetic and every photon comes from here.
STRIP_LIGHT_Y = 3.375


# Panel-zone swap-outs. Each replaces WALL facet 4 (the 1.25 - 2.50 m panel)
# and nothing else, so the piece still mates with the same neighbours.
PANEL_LO, PANEL_HI = 1.250, 2.500
SWAPS = [
    ('W1 PLAIN',    'Flat panel. The default and the cheapest.'),
    ('W2 RECESSED', 'Panel set back 0.125 m behind a 45 chamfered reveal.'),
    ('W3 LOUVRE',   'Recessed field with slats. Honest home for a wall hatch.'),
    ('W4 WINDOW',   'Panel becomes glazing on a chamfered reveal.'),
    ('W5 PORTAL',   'Panel zone opens full height; needs a rib either side.'),
]


def mirror(chain):
    return [(-x, y) for x, y in reversed(chain)]


def half_shell():
    """FLOOR + WALL + CEILING assembled, centre floor round to centre soffit."""
    out = list(FLOOR)
    for p in WALL:
        if p != out[-1]:
            out.append(p)
    for p in CEILING:
        if p != out[-1]:
            out.append(p)
    return out


def full_shell():
    half = half_shell()
    return mirror(half) + half[1:]


def x_at(chain, y):
    best = None
    for (x0, y0), (x1, y1) in zip(chain, chain[1:]):
        if min(y0, y1) - 1e-9 <= y <= max(y0, y1) + 1e-9 and abs(y1 - y0) > 1e-9:
            v = abs(x0 + (y - y0) / (y1 - y0) * (x1 - x0))
            best = v if best is None else min(best, v)
    return best


def facets(chain):
    """(a, b, length, angle from horizontal or None when axis aligned)."""
    out = []
    for a, b in zip(chain, chain[1:]):
        dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
        ang = math.degrees(math.atan2(dy, dx)) if dx > 1e-9 and dy > 1e-9 else None
        out.append((a, b, math.hypot(dx, dy), ang))
    return out


def bands(chain, y_lo, y_hi, extra_cuts=()):
    cuts = {y_lo, y_hi}
    cuts |= {y for _, y in chain if y_lo < y < y_hi}
    cuts |= {y for y in extra_cuts if y_lo < y < y_hi}
    ys = sorted(cuts)
    return list(zip(ys, ys[1:]))


def check():
    problems = []

    for name, chain in (('wall', WALL), ('rib', RIB), ('floor', FLOOR), ('ceiling', CEILING)):
        for x, y in chain:
            for v in (x, y):
                if abs(v / GRID - round(v / GRID)) > 1e-9:
                    problems.append(f'{name}: {v} is off the {GRID} m grid')

    # The pieces have to mate, or they are not pieces.
    if FLOOR[-1] != WALL[0]:
        problems.append('floor plate does not meet the wall foot')
    if WALL[-1] != CEILING[0]:
        problems.append('wall top does not meet the ceiling soffit')
    if abs(CEILING[-1][0]) > 1e-9:
        problems.append('ceiling does not reach the centreline')

    # The rib stands on the floor, on the lane line, vertical to knee height.
    if RIB[0] != (LANE_HALF, 0.0):
        problems.append('rib toe does not sit on the protected lane line')
    if abs(RIB[1][0] - RIB[0][0]) > 1e-9:
        problems.append('rib toe is not vertical off the floor')
    if RIB[1][1] < KNEE - 1e-9:
        problems.append(f'rib toe stops being vertical below knee height ({KNEE} m)')
    if RIB[2][0] <= RIB[0][0] + 1e-9:
        problems.append('rib base does not batter back onto the shaft')

    # Any outward-rising facet low enough to stand on must beat floor_max_angle
    # with margin. 45 degrees exactly is the engine default, so it is a coin flip.
    for name, chain in (('wall', WALL), ('rib', RIB)):
        for a, b, _, ang in facets(chain):
            if ang is None:
                continue
            rising_outward = (b[0] > a[0]) == (b[1] > a[1])
            if rising_outward and a[1] < 2.0 and ang <= 48.0:
                problems.append(f'{name} facet {a}->{b} is {ang:.2f} deg; the capsule may walk it')

    # Nothing intrudes on the protected envelope.
    y = 0.0
    while y <= LANE_HEIGHT + 1e-9:
        for name, chain in (('wall', WALL), ('rib', RIB)):
            v = x_at(chain, y)
            if v is not None and v < LANE_HALF - 1e-9:
                problems.append(f'{name} at y={y:.4f} reaches x={v:.4f}, inside the lane')
        y += GRID / 4
    if RIB_SOFFIT_Y < LANE_HEIGHT + 0.25:
        problems.append('rib beam soffit leaves under 0.25 m over the protected head height')

    # The rib must sit proud of the wall everywhere above the floor line.
    y = GRID / 4
    while y <= RIB_SOFFIT_Y + 1e-9:
        w, r = x_at(WALL, y), x_at(RIB, y)
        if w is not None and r is not None and r > w - GRID + 1e-9:
            problems.append(f'rib projects only {w - r:+.4f} m at y={y:.4f}')
        y += GRID / 4

    if problems:
        raise SystemExit('SECTION CHECK FAILED:\n  ' + '\n  '.join(problems))
    return True


if __name__ == '__main__':
    check()
    half = half_shell()
    print(f'HALF CORRIDOR: {len(facets(half))} facets '
          f'(floor {len(facets(FLOOR))}, wall {len(facets(WALL))}, ceiling {len(facets(CEILING))})')
    print(f'RIB:           {len(facets(RIB))} facets, standing on the floor at x={RIB[0][0]}')
    angs = sorted({round(a, 2) for chain in (WALL, RIB) for *_, a in facets(chain) if a is not None})
    print(f'sloped facets at {angs}')
    print()
    print(f'widest interior      {2*WIDEST:.2f} m')
    print(f'walking plate        {2*FLOOR_HALF:.2f} m')
    print(f'flat soffit          {2*CEIL_HALF:.2f} m at {CEIL_Y} m')
    print(f'clear between toes   {2*RIB[0][0]:.2f} m  (the protected lane)')
    print(f'rib beam soffit      {RIB_SOFFIT_Y} m -> {RIB_SOFFIT_Y - LANE_HEIGHT:.3f} m over head height')
    print(f'wall at y={LANE_HEIGHT}        x={x_at(WALL, LANE_HEIGHT):.4f}')
    print(f'rib  at y={LANE_HEIGHT}        x={x_at(RIB, LANE_HEIGHT):.4f}')
    print(f'panel pocket depth   {x_at(WALL, 1.8) - x_at(RIB, 1.8):.3f} m at eye height')
    print(f'rib pitch            {RIB_PITCH} m ({RIB_PITCH:.0f} texture repeats), {RIB_DEPTH} m deep')
    a, b = RIB[1], RIB[2]
    ang = math.degrees(math.atan2(b[1]-a[1], b[0]-a[0]))
    print(f'\nrib toe vertical     floor to {a[1]:.2f} m (knee)')
    print(f'rib base batter      {a[1]:.2f} -> {b[1]:.3f} m, flare {b[0]-a[0]:.3f} m, {ang:.2f} deg')
    print(f'margin over the 45 deg floor_max_angle default: {ang-45:.2f} deg')
    print('\nsection check passed')
