"""
Onboarding / security induction floor plan (docs/onboarding-walkthrough.md).

Revision 03. Revision 02 was rejected on three counts, all fair:
  1. Too much dead space -- rooms floating in black with corridors bridging
     gaps, nothing like the packed footprint of admin.map.
  2. Rooms were labelled rectangles. Drawing a box and writing RECEPTION in it
     is exactly the habit the Doom 3 study was meant to break: the box becomes
     "the play area" instead of a composed space.
  3. Corridors were stamped overlapping rectangles rather than drawn.

This pass drafts it properly:
  * The building is a SOLID BLOCK and every space is carved out of it, so wall
    thickness is real and neighbours share walls. There is no void between
    rooms, only structure.
  * Every space carries its actual fixtures -- desks, lockers, benches, stalls,
    shelving, machinery -- so the room is designed, not reserved.
  * Two rooms are pass-throughs on the critical path (Lockers, Machinery),
    per the Doom 3 habit of routing circulation through working spaces.

Still a draft for discussion. Verticality, lighting and encounter placement
are deliberately absent -- they come after the footprint is agreed.
"""
from pathlib import Path
from html import escape
from math import hypot

ROOT = Path(__file__).resolve().parents[1]

C = {
    'bg': '#0b1218',
    'solid': '#233240',        # the structural mass everything is carved from
    'solid_edge': '#324656',
    'floor': '#c8923c',        # public / occupied rooms
    'floor_back': '#a8687e',   # back-of-house
    'floor_corr': '#3f7fb0',   # circulation
    'fixture': '#6b4a1f',
    'fixture_back': '#5d3040',
    'fixture_corr': '#25567a',
    'ink': '#edf4fa',
    'muted': '#8aa2b2',
    'label': '#1b1205',
    'route': '#ffd88a',
    'tbd': '#e06a6a',
}

WALL = 0.35          # internal wall thickness, metres
ENV_W, ENV_H = 38.0, 24.5
K = 26               # px per metre
OX, OY = 56, 116

S = []


def mx(v):
    return round(OX + v * K, 2)


def my(v):
    return round(OY + v * K, 2)


def text(x, y, t, size=14, color='ink', bold=False, anchor='start', italic=False, opacity=1.0):
    S.append(
        f'<text x="{x}" y="{y}" fill="{C.get(color, color)}" font-size="{size}" '
        f'font-weight="{700 if bold else 400}" text-anchor="{anchor}" '
        f'font-style="{"italic" if italic else "normal"}" opacity="{opacity}">{escape(t)}</text>'
    )


def px_rect(x, y, w, h, fill, stroke='none', sw=1, rx=0, opacity=1.0):
    S.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{C.get(fill, fill)}" '
        f'stroke="{C.get(stroke, stroke)}" stroke-width="{sw}" opacity="{opacity}"/>'
    )


def m_rect(x0, y0, x1, y1, fill, stroke='none', sw=1, rx=0, opacity=1.0):
    px_rect(mx(x0), my(y0), (x1 - x0) * K, (y1 - y0) * K, fill, stroke, sw, rx, opacity)


# ---------------------------------------------------------------- the plan --
# Every space is (x0, y0, x1, y1) in metres, pre-inset. Adjacent spaces share
# an edge value; the WALL inset on each side is what becomes the wall between.

SPACES = {
    # --- entry sequence, west -------------------------------------------
    'AIRLOCK':    (1.5, 10.0, 6.5, 15.5),
    'ARRIVAL':    (6.5, 9.0, 13.5, 15.5),
    'RECEPTION':  (13.5, 8.5, 23.2, 16.0),
    'BACK OFFICE': (13.5, 16.0, 18.0, 20.5),
    # --- north-west ------------------------------------------------------
    'COMMS':      (6.5, 3.5, 13.5, 9.0),
    'SUPPLY':     (1.5, 3.5, 6.5, 10.0),
    'RECORDS':    (13.5, 0.8, 18.0, 3.5),
    # --- north circulation, jogged ---------------------------------------
    'G1':         (18.0, 3.5, 22.0, 8.5),
    'G2':         (18.0, 0.8, 27.0, 3.5),
    'G3':         (24.0, 3.5, 27.0, 9.0),
    'G4':         (24.0, 9.0, 29.5, 12.0),
    # --- north-east ------------------------------------------------------
    'ARMORY':     (27.0, 0.8, 36.5, 9.0),
    'RANGE':      (29.5, 9.0, 36.5, 14.5),
    'LOCKERS':    (24.0, 12.0, 28.5, 16.5),
    'DISPATCH':   (28.5, 14.5, 36.5, 21.0),
    # --- south -----------------------------------------------------------
    'MACHINERY':  (21.5, 16.5, 28.5, 23.0),
    'PLANT':      (28.5, 21.0, 36.5, 23.8),
    'STORE':      (18.0, 17.0, 21.5, 20.5),
    'BREAK ROOM': (8.0, 16.5, 13.5, 21.5),
    'BATH':       (1.0, 16.0, 5.0, 20.0),
    'CLOSET':     (1.0, 20.0, 5.0, 22.5),
    # --- south circulation, jogged ---------------------------------------
    'P1':         (18.0, 20.5, 21.5, 23.5),
    'P2':         (13.5, 21.5, 18.0, 24.0),
    'P3':         (8.0, 21.5, 13.5, 24.0),
    'P4':         (5.0, 21.5, 8.0, 24.0),
    'P5':         (5.0, 15.5, 8.0, 21.5),
}

CORRIDORS = {'G1', 'G2', 'G3', 'G4', 'P1', 'P2', 'P3', 'P4', 'P5'}
BACK_OF_HOUSE = {'MACHINERY', 'BREAK ROOM', 'BATH', 'CLOSET', 'STORE', 'SUPPLY', 'LOCKERS',
                 'RECORDS', 'PLANT'}

# doors: ('v'|'h', wall coordinate, centre along the wall)
DOORS = [
    ('v', 6.5, 12.7),    # airlock -> arrival
    ('v', 13.5, 12.0),   # arrival -> reception
    ('h', 9.0, 10.0),    # arrival -> comms
    ('v', 6.5, 6.0),     # comms -> supply
    ('h', 10.0, 4.0),    # supply -> airlock
    ('v', 18.0, 6.0),    # reception -> G1  (via north wall of reception)
    ('h', 8.5, 20.0),    # reception -> G1
    ('h', 3.5, 20.0),    # G1 -> G2
    ('h', 3.5, 15.7),    # G2 -> records
    ('v', 24.0, 2.2),    # G2 -> G3 region
    ('v', 27.0, 6.0),    # G3 -> armory
    ('h', 9.0, 28.2),    # G4 -> armory
    ('h', 9.0, 33.0),    # armory -> range
    ('h', 12.0, 26.2),   # G4 -> lockers
    ('v', 28.5, 15.5),   # lockers -> dispatch
    ('v', 28.5, 19.0),   # dispatch -> machinery
    ('v', 28.5, 22.0),   # machinery -> plant (sealed service room)
    ('v', 21.5, 21.8),   # machinery -> P1
    ('v', 18.0, 19.0),   # P1 -> store
    ('h', 20.5, 15.7),   # back office -> P2 region
    ('v', 13.5, 18.2),   # reception back office -> break room side
    ('v', 13.5, 22.7),   # P2 -> P3
    ('h', 21.5, 10.7),   # P3 -> break room
    ('v', 8.0, 22.7),    # P3 -> P4
    ('v', 5.0, 18.0),    # P5 -> bath
    ('v', 5.0, 21.2),    # P4 -> closet
    ('h', 15.5, 6.5),    # P5 -> airlock/arrival threshold
]


def check_overlaps():
    items = list(SPACES.items())
    for i, (n1, a) in enumerate(items):
        assert a[2] > a[0] and a[3] > a[1], f'{n1} has non-positive extent'
        for n2, b in items[i + 1:]:
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            assert ox <= 1e-9 or oy <= 1e-9, f'{n1} overlaps {n2}'


def floor_colour(name):
    if name in CORRIDORS:
        return 'floor_corr'
    if name in BACK_OF_HOUSE:
        return 'floor_back'
    return 'floor'


def fixture_colour(name):
    if name in CORRIDORS:
        return 'fixture_corr'
    if name in BACK_OF_HOUSE:
        return 'fixture_back'
    return 'fixture'


def draw_floors():
    for name, (x0, y0, x1, y1) in SPACES.items():
        h = WALL / 2
        m_rect(x0 + h, y0 + h, x1 - h, y1 - h, floor_colour(name))


def draw_doors():
    half = 0.65
    for kind, coord, centre in DOORS:
        pad = WALL / 2 + 0.02
        if kind == 'v':
            m_rect(coord - pad, centre - half, coord + pad, centre + half, 'floor_corr')
        else:
            m_rect(centre - half, coord - pad, centre + half, coord + pad, 'floor_corr')


def fx(x0, y0, x1, y1, room, rx=1):
    m_rect(x0, y0, x1, y1, fixture_colour(room), rx=rx)


def chair(cx, cy, room, r=0.32):
    S.append(f'<circle cx="{mx(cx)}" cy="{my(cy)}" r="{r * K}" fill="{C[fixture_colour(room)]}"/>')


def shelf_rows(x0, y0, x1, y1, room, n=3, horizontal=True):
    if horizontal:
        step = (y1 - y0) / n
        for i in range(n):
            fx(x0, y0 + i * step, x1, y0 + i * step + step * 0.45, room)
    else:
        step = (x1 - x0) / n
        for i in range(n):
            fx(x0 + i * step, y0, x0 + i * step + step * 0.45, y1, room)


def draw_fixtures():
    # RECEPTION -- desk with staff side, waiting chairs, terminals
    fx(15.0, 9.4, 20.8, 10.5, 'RECEPTION')            # counter
    fx(15.0, 10.5, 16.2, 12.6, 'RECEPTION')           # return leg of desk
    chair(17.0, 11.3, 'RECEPTION'); chair(18.4, 11.3, 'RECEPTION')   # staff side
    for cx_ in (15.6, 16.9, 18.2, 19.5):
        chair(cx_, 14.9, 'RECEPTION')                 # waiting row
    fx(20.4, 12.6, 21.5, 15.3, 'RECEPTION')           # side cabinet run
    fx(14.1, 13.6, 14.9, 15.4, 'RECEPTION')           # planter / kiosk

    # ARRIVAL -- bench, notice board, the step up into reception
    fx(7.2, 14.2, 10.6, 14.9, 'ARRIVAL')              # bench
    fx(12.4, 9.5, 13.2, 11.4, 'ARRIVAL')              # notice board
    S.append(f'<line x1="{mx(13.2)}" y1="{my(9.4)}" x2="{mx(13.2)}" y2="{my(15.2)}" '
             f'stroke="{C["route"]}" stroke-width="2" stroke-dasharray="5 4" opacity="0.75"/>')
    text(mx(12.9), my(13.0), 'step up', 10, 'route', italic=True, anchor='middle')

    # COMMS -- radio rack, bench, charging shelf
    shelf_rows(7.0, 4.0, 8.4, 8.6, 'COMMS', n=3)
    fx(9.2, 4.0, 12.9, 4.9, 'COMMS')
    fx(12.2, 6.0, 13.2, 8.6, 'COMMS')

    # SUPPLY -- shelving aisles
    shelf_rows(2.0, 4.2, 6.0, 9.6, 'SUPPLY', n=3)

    # RECORDS -- cabinet rows
    shelf_rows(14.0, 1.3, 17.6, 3.1, 'RECORDS', n=2)

    # ARMORY -- weapon lockers along two walls, issue counter, work bench
    shelf_rows(27.6, 1.3, 36.0, 2.6, 'ARMORY', n=6, horizontal=False)
    fx(27.6, 6.6, 32.4, 7.7, 'ARMORY')                # issue counter
    fx(34.6, 3.6, 36.0, 7.8, 'ARMORY')                # bench run
    chair(33.4, 7.0, 'ARMORY')

    # RANGE -- firing line, lane dividers, targets, cover block
    S.append(f'<line x1="{mx(31.2)}" y1="{my(9.4)}" x2="{mx(31.2)}" y2="{my(14.1)}" '
             f'stroke="{C["route"]}" stroke-width="2" stroke-dasharray="4 4" opacity="0.8"/>')
    text(mx(31.0), my(14.0), 'firing line', 10, 'route', italic=True, anchor='end')
    for yy in (10.2, 11.6, 13.0):
        fx(35.3, yy, 36.1, yy + 0.7, 'RANGE')         # targets downrange
    fx(32.6, 12.6, 33.8, 13.9, 'RANGE')               # cover block to duck behind
    text(mx(33.2), my(14.35), 'cover', 9, 'label', anchor='middle')

    # LOCKERS -- pass-through changing room
    shelf_rows(24.4, 12.5, 25.6, 16.1, 'LOCKERS', n=2)
    shelf_rows(27.0, 12.5, 28.2, 16.1, 'LOCKERS', n=2)
    fx(25.9, 14.0, 26.8, 15.6, 'LOCKERS')             # bench between banks

    # DISPATCH -- desk, board, chairs
    fx(30.0, 15.2, 35.6, 16.3, 'DISPATCH')
    chair(31.6, 17.1, 'DISPATCH'); chair(33.2, 17.1, 'DISPATCH')
    fx(29.0, 18.6, 30.0, 20.6, 'DISPATCH')            # map/board
    fx(33.4, 19.2, 36.1, 20.6, 'DISPATCH')            # cabinets

    # MACHINERY -- masses the player threads between
    fx(22.2, 17.2, 24.3, 19.2, 'MACHINERY')
    fx(26.0, 17.2, 28.1, 18.6, 'MACHINERY')
    fx(22.2, 21.0, 24.0, 22.6, 'MACHINERY')
    fx(25.6, 20.4, 28.1, 22.6, 'MACHINERY')
    S.append(f'<circle cx="{mx(25.0)}" cy="{my(19.9)}" r="{0.75 * K}" fill="none" '
             f'stroke="{C["fixture_back"]}" stroke-width="3"/>')

    # STORE
    shelf_rows(18.5, 17.5, 21.1, 20.1, 'STORE', n=2)

    # PLANT -- tanks and a pipe run; a service room, not a fight space
    for i in range(3):
        S.append(f'<circle cx="{mx(30.2 + i * 2.1)}" cy="{my(22.6)}" r="{0.72 * K}" fill="none" '
                 f'stroke="{C["fixture_back"]}" stroke-width="3"/>')
    fx(29.0, 21.3, 36.0, 21.9, 'PLANT')

    # BREAK ROOM -- table, chairs, counter, lockers
    fx(9.9, 18.4, 12.0, 19.9, 'BREAK ROOM')
    for cx_, cy_ in ((9.4, 18.8), (9.4, 19.6), (12.5, 18.8), (12.5, 19.6)):
        chair(cx_, cy_, 'BREAK ROOM')
    fx(8.5, 16.9, 12.9, 17.7, 'BREAK ROOM')           # counter
    shelf_rows(8.5, 20.4, 10.2, 21.2, 'BREAK ROOM', n=2, horizontal=False)

    # BATH -- stalls and basins
    for i in range(2):
        fx(1.4 + i * 1.5, 16.4, 1.4 + i * 1.5 + 1.2, 18.0, 'BATH')
    fx(1.4, 19.0, 4.6, 19.7, 'BATH')

    # CLOSET
    shelf_rows(1.4, 20.4, 4.6, 22.1, 'CLOSET', n=2)


ROUTE = [
    (4.0, 12.7), (10.0, 12.7), (16.0, 12.2), (20.0, 11.0), (20.0, 6.0),
    (20.0, 2.2), (25.5, 2.2), (25.5, 6.2), (29.0, 7.6), (33.5, 6.0),
    (30.5, 8.2), (26.2, 10.4), (26.2, 14.4), (29.8, 15.6), (32.4, 18.4),
    (27.0, 19.4), (23.2, 21.4), (19.8, 21.9), (15.7, 22.7), (10.7, 22.7),
    (6.5, 22.7), (6.5, 17.4), (5.4, 14.6), (4.0, 13.4),
]

# the range is a dead-end spur off the armory: walked in and back out
RANGE_SPUR = [(33.5, 8.4), (33.0, 12.4)]


def draw_route():
    pts = ' '.join(f'{mx(x)},{my(y)}' for x, y in ROUTE)
    S.append(f'<polyline points="{pts}" fill="none" stroke="{C["route"]}" stroke-width="2.2" '
             f'stroke-dasharray="7 5" opacity="0.85" stroke-linejoin="round"/>')
    spur = ' '.join(f'{mx(x)},{my(y)}' for x, y in RANGE_SPUR)
    S.append(f'<polyline points="{spur}" fill="none" stroke="{C["route"]}" stroke-width="2.2" '
             f'stroke-dasharray="3 4" opacity="0.7" stroke-linejoin="round"/>')
    text(mx(33.9), my(10.6), 'spur, in and back', 9, 'route', italic=True)


def route_length():
    loop = sum(hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(ROUTE, ROUTE[1:]))
    spur = sum(hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(RANGE_SPUR, RANGE_SPUR[1:]))
    return loop + 2 * spur


def draw_labels():
    small = {'BATH', 'CLOSET', 'STORE', 'RECORDS', 'G1', 'G2', 'G3', 'G4',
             'P1', 'P2', 'P3', 'P4', 'P5'}
    for name, (x0, y0, x1, y1) in SPACES.items():
        if name in CORRIDORS:
            continue
        cx_ = (x0 + x1) / 2
        ty = y0 + 0.95
        size = 10 if name in small else 12.5
        w_px = (len(name) * size * 0.62) + 10
        px_rect(mx(cx_) - w_px / 2, my(ty) - size + 1, w_px, size + 5,
                floor_colour(name), rx=3, opacity=0.82)
        text(mx(cx_), my(ty), name, size, 'label', True, 'middle')
    for name in ('G2', 'P3'):
        x0, y0, x1, y1 = SPACES[name]
        text(mx((x0 + x1) / 2), my((y0 + y1) / 2 + 0.15), 'corridor', 10, '#cfe6f7', anchor='middle', italic=True)


def main():
    check_overlaps()

    px_rect(0, 0, 1220, 860, 'bg')
    text(36, 42, 'RED BREACH / ONBOARDING — SECURITY INDUCTION, REVISION 03', 23, 'ink', True)
    text(36, 66, 'Drafted from a solid block: spaces are carved out, walls are real thickness and shared. Every room is composed, not reserved.', 13, 'muted')
    text(36, 88, 'Draft for discussion. Verticality, lighting and encounters deliberately not on this drawing yet.', 13, 'muted', italic=True)

    m_rect(0, 0, ENV_W, ENV_H, 'solid', 'solid_edge', 2)
    draw_floors()
    draw_doors()
    draw_fixtures()
    draw_route()
    draw_labels()

    floor_area = sum((x1 - x0 - WALL) * (y1 - y0 - WALL) for x0, y0, x1, y1 in SPACES.values())
    env_area = ENV_W * ENV_H
    rl = route_length()

    ly = 800
    for i, (col, lab) in enumerate([
        ('floor', 'occupied room'), ('floor_back', 'back of house'),
        ('floor_corr', 'circulation'), ('solid', 'structure / wall mass'),
    ]):
        px_rect(36 + i * 190, ly, 18, 13, col, 'solid_edge', 1)
        text(60 + i * 190, ly + 12, lab, 12, 'muted')
    text(36 + 4 * 190, ly + 12, 'gold dashed = walked route', 12, 'route')

    text(36, 762, f'{len(SPACES) - len(CORRIDORS)} rooms + {len(CORRIDORS)} corridor legs in a {ENV_W:.0f} x {ENV_H:.0f} m block  •  '
                  f'{floor_area:.0f} m² of floor = {100 * floor_area / env_area:.0f}% of the footprint built '
                  f'(admin.map ground story, for comparison: 1,664 m²)', 13, 'ink')
    text(36, 784, f'Route through the loop ≈ {rl:.0f} m → roughly {rl / 5:.0f} s of pure walking at 5 m/s. '
                  f'Room time (sign-in, armory, range, dispatch) is on top of that.', 13, 'muted')

    out = ROOT / 'docs' / 'onboarding-plan.svg'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="1220" height="860" viewBox="0 0 1220 860">'
           '<title>Red Breach onboarding floor plan, revision 03</title>' + ''.join(S) + '</svg>')
    out.write_text(svg, encoding='utf-8')
    print(f'wrote {out}')
    print(f'{floor_area:.0f} m2 floor / {env_area:.0f} m2 envelope = {100 * floor_area / env_area:.0f}%')
    print(f'route {rl:.0f} m -> {rl / 5:.0f} s walking')


if __name__ == '__main__':
    main()
