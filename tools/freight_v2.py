"""Freight access v2: the 2D plan, as data. Single source of truth.

Stage 2 of docs/freight-v2-walkthrough.md, plan revision 08. Plan metres:
x east, y NORTH. Heights are floor elevations relative to the airlock floor
(0). The drawing (tools/draw-freight-v2-plan.py) reads this module; the 3D
build will too. Run it to print route lengths and the self-check.

Rooms follow the recipe: the walk paths and blockers were placed first, then
each perimeter was drawn to wrap them. The perimeters are not rectangles
drawn first.

Revision 02 (user review of revision 01): stairs are 3 m flights in their own
stairwells, never the full 6 m width of a corridor; filler rooms sit between
the big rooms (the pipe run, the compressor U-turn); the east stairs lead to a
room of their own, and one keycard opens that room and the easy way back.

Revision 03 (user sketch on revision 02): more density on the east, the west
stays as it is. A grill in the substation's west wall slides open; crouch
through into an access corridor, down to a filter room, up a ladder in a small
room into a pipe room (pipes out of the floor and into the walls, a rack the
length of the room, a slow box fan in the wall), then a vent that opens high in
the dock wall, where you drop down. It is another way back, one way only.

Revision 04 (user notes on revision 03): the box fan moves to the pipe room's
north wall, centred between the chamfered corners, so it is seen just before
the vent. The access corridor becomes an air duct hallway: one crouch through
the grill, then a cramped run down bare steel siding with a tiny rib at every
2 m join. The second crouch (the fallen cable tray) and the duct's sparking
fitting are removed: extra crouches only add time.

Revision 05 (user sketch on revision 04): the crane catwalk is rerouted. From
the archive it crosses over the bay, then turns north out of the bay into pass-
through rooms: the lift machine room (pumps on the left), a corridor with a jog,
a stair room going down (the pickup is behind you at the bottom), and the fan
chamber. A lever there stops the pipe room's big fan, and you walk through its
blades into the pipe room. The fan is only stoppable from the chamber side.

Revision 06 (user sketch on revision 05): from the stair room's top landing a
stair corridor runs east, then south-east, down to door 3 in the substation's
north-west corner; the door opens only from the corridor side. That makes the
catwalk a real shortcut to P. The stair room's flight moves to its east side:
at the bottom you turn left straight out to the fan chamber, and the pickups
under the landing are behind you to the right, found only by exploring. The jog
corridor moves north to meet the new top landing. The northern route is light
on enemies, so it is fast in time even where it is not shorter in metres.

Revision 07 (user notes on revision 06):
- Door 3 is raised (+1) and opens onto a new catwalk along the substation's
  north wall, joining the gantry into a U; a ladder drops from it to the floor.
  The stair corridor now needs a single 12-riser flight.
- The fan is a 3 m fan you CROUCH through when stopped: a smaller fan chamber.
- The booth crane panel is gone. Finding the shortcut on a first run is fine,
  but it takes mechanical movement: three switches in the pipe bay (1 sparks,
  2 opens door 1 to a secret closet, 3 opens door 5 high in Logistics' east
  wall), and a switch in the cage lowers the raised catwalk section (3) from
  90 degrees so you can walk it to door 5. The archive lever still opens the
  cage.

Revision 08 (user notes on revision 07): switches 2 and 3 swap. Switch 2 opens
the distant door 5 for the catwalk; switch 3, the last one, opens the nearby
secret door 1, so a player who stops after the catwalk door may never find the
closet. The hinge side of section (3) does not matter. The sorting booth stays
as a booth that looks the part: a seat with a console and a seat with a
joystick at the glass. Nothing in the game is labelled; props tell the story.
"""
import math


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def octagon(cx, cy, flats, clip):
    h = flats / 2
    return [(cx - h + clip, cy - h), (cx + h - clip, cy - h), (cx + h, cy - h + clip), (cx + h, cy + h - clip),
            (cx + h - clip, cy + h), (cx - h + clip, cy + h), (cx - h, cy + h - clip), (cx - h, cy - h + clip)]


def reg_poly(cx, cy, r, n=8):
    return [(cx + r * math.cos(k * math.tau / n + math.pi / n), cy + r * math.sin(k * math.tau / n + math.pi / n)) for k in range(n)]


REVISION = 8

# --- rooms: (key, name, inner perimeter, floor, look) ----------------------------
ROOMS = [
    ('AL', 'Arrival airlock', octagon(0.0, -25.0, 6.0, 1.5), 0.0, 'steel'),
    ('RC', 'Receiving', [(-7, -22), (7, -22), (7, -18.5), (10, -18.5), (10, -13), (7, -13), (7, -11), (-5, -11), (-7, -13)], -0.5, 'steel'),
    ('SB', 'Sorting Bay', [(-10, 0), (10, 0), (12, 2), (12, 3), (14, 3.5), (14, 9.5), (12, 10), (12, 40), (-12, 40), (-12, 27),
                           (-14, 26), (-14, 19), (-12, 18), (-12, 2)], -3.0, 'concrete'),
    ('DK', 'Loading dock and lift lobby', [(-12, 40), (12, 40), (12, 47.5), (7, 47.5), (7, 52), (4, 55), (-4, 55), (-7, 52), (-7, 47.5),
                                           (-12, 47.5)], -1.75, 'concrete'),
    ('TB', 'Truck bay', [(-26, 40), (-12, 40), (-12, 54), (-24, 54), (-26, 52)], -3.0, 'concrete'),
    # West filler: the pipe run's side bay. Pipes cross it at crouch height; the ammo is seen beneath them.
    ('SC', 'Secret closet', [(-26, 6), (-21.5, 6), (-21, 6.5), (-21, 10), (-26, 10)], -3.0, 'steel'),
    ('WX', 'Pipe bay', [(-20.5, 10.5), (-20.5, 7.5), (-19.5, 6.5), (-15.5, 6.5), (-14.5, 7.5), (-14.5, 10.5)], -3.0, 'steel'),
    # The west stairwell wraps its two 3 m flights: ground landing, flight, turning landing, flight, top landing.
    ('ST', 'West stairwell', [(-29, 10), (-22.5, 10), (-22.5, 16.5), (-26, 16.5), (-26, 20.5), (-22.5, 20.5), (-22.5, 28.5),
                              (-25.5, 28.5), (-25.5, 22.5), (-29, 22.5)], -3.0, 'steel'),
    ('LG', 'Logistics office', [(-22.5, 22), (-12, 22), (-12, 40), (-28, 40), (-28, 33.5), (-26.5, 32), (-22.5, 32)], 1.0, 'warm'),
    # East filler: a U round the compressor. A spine wall from the west wall to the machine makes it a real U.
    ('CU', 'Compressor U-turn', [(26, -4), (44, -4), (47, -1), (47, 9), (44, 12), (33, 12), (33, 7.5), (26, 7.5)], -3.5, 'steel'),
    ('PR', 'Pump Room', [(30, 15), (33, 12), (47, 12), (50, 15), (50, 28), (47, 31), (44, 31), (44, 32.5), (36, 32.5), (36, 31),
                         (33, 31), (30, 28)], -4.0, 'steel'),
    ('SS', 'Substation', [(30, 34), (50, 34), (50, 52), (47, 55), (33, 55), (30, 52)], -2.5, 'steel'),
    # East middle (revision 03): filter room, ladder room, pipe room. Contents first, walls wrapped round them.
    ('FL', 'Filter room', [(14, 17.5), (15, 16.5), (28.5, 16.5), (29.5, 17.5), (29.5, 25), (24, 25), (24, 27), (19, 27), (19, 25),
                           (14, 25)], -3.0, 'steel'),
    ('LR', 'Ladder room', [(14, 25), (19, 25), (19, 27.5), (18, 28.5), (14, 28.5)], -3.0, 'steel'),
    ('PP', 'Pipe room', [(14, 28.5), (20, 28.5), (24, 32.5), (24, 48), (21, 51), (15, 51), (14, 50)], 0.0, 'steel'),
    # Catwalk route (revision 05): pass-through rooms north of the dock, then the fan chamber behind the pipe room.
    ('MR', 'Lift machine room', [(-11, 55.5), (-2, 55.5), (-2, 59.5), (-4, 62), (-11, 62)], 4.0, 'steel'),
    ('R3', 'Stair room', [(7.5, 51), (13.5, 51), (13.5, 64), (7.5, 64)], 0.0, 'steel'),   # square NW corner: the jog
                                                                                       # corridor runs straight in
    ('FC', 'Fan chamber', [(13.5, 51), (20.5, 51), (21.5, 52), (21.5, 55), (20.5, 56), (13.5, 56)], 0.0, 'steel'),
    # The foot of the east stairs: two keyed doors, the easy way back (S2) and the quarantine hold.
    ('LL', 'East stair lobby', [(50, 15), (56, 15), (56, 22.5), (54, 24.5), (51, 24.5), (50, 23.5)], -4.0, 'steel'),
    ('CV', 'Cable vault (secret)', rect(44.5, 52.25, 48.0, 53.75), -5.0, 'steel'),
    ('QH', 'Quarantine hold', [(50, -2), (61, -2), (64, 1), (64, 12), (61, 15), (50, 15)], -4.5, 'concrete'),
]

# Raised or sunken areas inside rooms: (name, poly, height, kind: platform / pit / lower / upper / feature)
LEVELS = [
    ('RC landing', rect(-2.5, -22, 2.5, -20.5), 0.0, 'platform'),
    ('Gallery', rect(-12, 0, 8, 3.5), -0.5, 'platform'),
    ('Sorting booth', rect(-13.5, 20, -10.5, 25), -1.5, 'platform'),
    ('Booth landing', rect(-10.5, 20, -9, 22), -1.5, 'platform'),
    ('S1 landing', rect(-12, 38, -9, 40), 1.0, 'platform'),
    ('Cargo scale (flush plate, grate feature)', rect(-1.5, -16.5, 1.5, -14.0), -0.4375, 'feature'),
    ('Stairwell landing', rect(-29, 20.5, -22.5, 22.5), -1.0, 'platform'),
    ('Stairwell top', rect(-25.5, 26.5, -22.5, 28.5), 1.0, 'platform'),
    ('U-turn entry', rect(26, -4, 28.5, 2), -3.0, 'platform'),
    ('North lane', [(42, 3), (47, 3), (47, 9), (44, 12), (33, 12), (33, 7.5), (42, 7.5)], -4.0, 'lower'),
    ('Pump pit', rect(34, 15, 46, 27), -5.5, 'pit'),
    ('Gantry', [(43, 34), (50, 34), (50, 52), (47, 55), (33, 55), (31, 53), (32.5, 51.5), (34, 53), (46.5, 53), (46.5, 37.5),
                (43, 37.5)], 1.0, 'platform'),
    ('Cable trench', rect(32, 41, 45, 42.5), -2.75, 'pit'),
    ('Hold landing', rect(50, 12, 56, 15), -4.0, 'platform'),
    ('Stair room top landing', rect(7.5, 61, 13.5, 64), 4.0, 'platform'),
    ('Archive (above the cage)', [(-26.5, 32), (-22.5, 32), (-22.5, 40), (-28, 40), (-28, 33.5)], 4.0, 'upper'),
]

# --- corridors: (key, name, profile, path, heights per vertex, look) ----------------
# P1 / P2 are the 6 m kit corridors; S3 is a 3 m service stair; D2 a 2 m bare steel duct hallway
# (a tiny rib at every 2 m join); catwalk a 1.5 m railed grating, drawn over what it crosses;
# crawl is a 1.1 m crouch pipe.
CORRIDORS = [
    ('C1', 'Receiving to the bay', 'P1', [(0, -11), (0, 0)], [-0.5, -0.5], 'steel'),
    ('W1', 'Pipe run', 'P2', [(-12, 13.5), (-22.5, 13.5)], [-3, -3], 'steel'),
    ('TR', 'Service trench', 'P2', [(12, 6.5), (20, 6.5), (20, -0.5), (26, -0.5)], [-3, -3, -3, -3], 'steel'),
    ('AC', 'Air duct hallway', 'D2', [(30, 46.5), (27, 46.5), (27, 27), (27, 26), (27, 25)], [-2.5, -2.5, -2.5, -3, -3], 'steel'),
    ('VT', 'Vent to the dock', 'crawl', [(14, 45.75), (12, 45.75)], [0, 0], 'steel'),
    ('CW', 'Crane catwalk', 'catwalk', [(-22.5, 37.5), (-9.25, 37.5), (-9.25, 55.5)], [4, 4, 4], 'steel'),
    ('J2', 'Jog corridor', 'S3', [(-2, 58), (1.5, 58), (6, 62.5), (7.5, 62.5)], [4, 4, 4, 4], 'steel'),
    # Revision 07: the stair corridor from the stair room's top landing down one 12-riser flight to raised door 3 (+1).
    ('C2', 'Stair corridor to the substation', 'S3', [(13.5, 62.5), (15.5, 62.5), (21.5, 62.5), (23.5, 62.5), (32, 54)],
     [4, 4, 1, 1, 1], 'steel'),
    ('BG', 'Bridge girder crawl (secret)', 'crawl', [(34.25, 18.0), (47.5, 18.0), (47.5, 19.25)], [-6.25, -6.25, -6.25], 'steel'),
    ('PG', 'Pipe gallery (crouch)', 'crawl', [(40, 27), (40, 32), (33, 32), (33, 34.6)], [-5.5, -5.5, -5.5, -5.5], 'steel'),
    ('EL', 'East stairs', 'S3', [(50, 41), (52.5, 41), (52.5, 38), (52.5, 33), (52.5, 31), (52.5, 26), (52.5, 24)],
     [1, 1, 1, -1.5, -1.5, -4, -4], 'steel'),
]

# --- stairs and ladders ------------------------------------------------------------
# Stairs: (name, footprint rect, from height, to height, direction of travel UP as (dx, dy))
STAIRS = [
    ('Receiving steps', rect(-2.5, -20.5, 2.5, -19.5), 0.0, -0.5, (0, -1)),
    ('Gallery stair', rect(-12, 3.5, -9, 8.5), -0.5, -3.0, (0, -1)),
    ('Booth steps', rect(-10.5, 22, -9, 25), -3.0, -1.5, (0, -1)),
    ('S1 service stair', rect(-12, 30, -9, 38), -3.0, 1.0, (0, 1)),
    ('Dock steps', rect(-1.75, 37.5, 1.75, 40), -3.0, -1.75, (0, 1)),
    ('Truck bay stair', rect(-14.5, 44, -12, 46), -1.75, -3.0, (1, 0)),
    ('Stairwell flight 1', rect(-29, 16.5, -26, 20.5), -3.0, -1.0, (0, 1)),
    ('Stairwell flight 2', rect(-25.5, 22.5, -22.5, 26.5), -1.0, 1.0, (0, 1)),
    ('U-turn entry steps', rect(28.5, -4, 29.5, 2), -3.0, -3.5, (-1, 0)),
    ('U-turn far steps', rect(42, 2, 47, 3), -3.5, -4.0, (0, -1)),
    ('Gantry stair', rect(36, 34, 43, 37.5), -2.5, 1.0, (1, 0)),
    ('Hold steps', rect(50, 11, 56, 12), -4.0, -4.5, (0, 1)),
    ('Stair room flight', rect(10.5, 53, 13.5, 61), 0.0, 4.0, (0, 1)),
]
# Ladders: (name, plan point, from height, to height)
LADDERS = [
    ('Archive ladder (12 rungs)', (-22.35, 39.1), 1.0, 4.0),
    ('Pit ladder', (34.0, 21.0), -4.0, -5.5),
    ('Bridge crawl ladder (secret)', (47.5, 20.75), -6.25, -4.0),   # down a hatch in the east walkway to the girder crawl
    ('Pipe gallery ladder (12 rungs)', (33.0, 36.1), -5.5, -2.5),
    ('Cable vault ladder (secret)', (44.5, 53.0), -5.0, -2.5),       # down a hatch in the alley behind the cage row
    ('Gantry ladder (14 rungs)', (34.0, 52.95), 1.0, -2.5),
    ('Ladder room ladder (12 rungs)', (15.5, 28.25), -3.0, 0.0),
]

# --- blockers: (room, name, poly) ---------------------------------------------------
BLOCKERS = [
    ('RC', 'decon arch', rect(-2.4, -18.9, -1.9, -18.3)), ('RC', 'decon arch', rect(1.9, -18.9, 2.4, -18.3)),
    ('RC', 'parcel rack', rect(-6.5, -20.5, -5.2, -13.5)), ('RC', 'parcel rack', rect(-4.2, -20.5, -2.9, -15.5)),
    ('RC', 'receiving desk + terminals', rect(3.0, -16.0, 6.5, -14.5)),
    ('RC', 'office desk', rect(8.2, -17.5, 9.6, -14.5)), ('RC', 'pallet jack', rect(4.0, -21.4, 5.2, -20.4)),
    ('SB', 'conveyor', rect(-9.5, 16.5, -3.5, 17.7)), ('SB', 'conveyor platform (crawl inside)', rect(-1.0, 16.5, 9.5, 17.7)),
    ('SB', 'conveyor', rect(-8.5, 27.0, 2.5, 28.2)), ('SB', 'conveyor', rect(5.0, 27.0, 9.5, 28.2)),
    ('SB', 'containers (one cracked open)', rect(-7.0, 19.0, -4.5, 25.0)),
    ('SB', 'container stack', rect(7.5, 30.0, 11.5, 36.0)),
    ('SB', 'container stack', rect(5.5, 19.5, 9.0, 25.0)),
    ('SB', 'booth console along the glass', rect(-11.3, 22.4, -10.6, 24.8)),
    ('SB', 'booth seats: one at a console, one with a joystick', rect(-12.6, 22.6, -11.8, 24.6)),
    ('DK', 'lift cage', rect(-3, 47.5, 3, 53.5)), ('DK', 'pallets', rect(8.0, 41.0, 10.0, 43.0)),
    ('TB', 'cargo hauler', rect(-22, 44, -16, 47.5)),
    ('LG', 'dispatch counter', rect(-13.8, 23.0, -12.8, 31.0)),
    ('LG', 'desk row', rect(-21, 25.0, -15.5, 26.0)), ('LG', 'desk row', rect(-21, 28.0, -15.5, 29.0)),
    ('LG', 'desk row', rect(-21, 34.5, -15.5, 35.5)), ('LG', 'lockers', rect(-21.2, 39.3, -18.2, 40.0)),
    ('LG', 'toppled cabinet', rect(-18.0, 31.2, -15.8, 31.9)),
    ('LG', 'supervisor cage', rect(-28, 34, -24, 40)),
    ('WX', 'ammo container', rect(-18.4, 6.9, -16.6, 7.7)),
    ('SC', 'closet shelves', rect(-25.6, 6.4, -24.6, 9.6)),
    ('LG', 'drawer bank', rect(-28.0, 38.2, -27.4, 39.8)),
    ('CU', 'spine: pipe manifold wall', rect(26, 2, 34, 7.5)),
    ('CU', 'air compressor', rect(36, 3.0, 40, 6.5)),   # railed round at its old footprint (user: see the piston)
    ('PR', 'pump', reg_poly(37, 23, 1.6)), ('PR', 'pump', reg_poly(40, 23, 1.6)), ('PR', 'pump', reg_poly(43, 23, 1.6)),
    ('PR', 'valve stand', rect(32.5, 13.2, 33.5, 14.2)), ('PR', 'valve stand', rect(46.5, 28.5, 47.5, 29.5)),
    ('SS', 'transformer cage', rect(35.0, 48.5, 38.3, 52.0)), ('SS', 'transformer cage', rect(38.7, 48.5, 42.0, 52.0)),
    ('SS', 'transformer cage', rect(42.4, 48.5, 45.7, 52.0)), ('SS', 'transformer cage', rect(46.1, 48.5, 49.4, 52.0)),
    ('SS', 'fallen cable tray', rect(37.5, 45.0, 40.0, 45.4)),
    ('QH', 'quarantine container', rect(51.5, 1.0, 54.0, 7.0)), ('QH', 'quarantine container', rect(56.5, 1.0, 59.0, 7.0)),
    ('QH', 'container burst open long ago', rect(61.0, 3.5, 63.5, 9.5)),
    ('QH', 'supply cage', rect(56.5, -1.8, 60.5, -0.2)),
    ('FL', 'filter bank', rect(15, 17, 21, 19.5)), ('FL', 'filter bank', rect(22.5, 17, 28.5, 19.5)),
    ('FL', 'blower', rect(19.5, 22.5, 23.5, 26.5)),
    ('PP', 'pipe rack, the length of the room', rect(22.5, 33.5, 24, 47.5)),
    ('PP', 'riser, up through the ceiling', reg_poly(18.5, 31.5, 0.45)),
    ('PP', 'riser turning east into the wall', reg_poly(21, 36.5, 0.35)),
    ('PP', 'riser turning east into the wall', reg_poly(21, 37.7, 0.35)),
    ('PP', 'riser turning east into the wall', reg_poly(21, 38.9, 0.35)),
    ('PP', 'riser turning west into the wall', reg_poly(15.2, 40.5, 0.35)),
    ('PP', 'riser turning west into the wall', reg_poly(15.2, 41.7, 0.35)),
    ('PP', 'valve manifold', rect(18, 43, 21, 44.5)),
    ('MR', 'hydraulic pump', rect(-9.5, 59.5, -7.5, 61.5)), ('MR', 'hydraulic pump', rect(-6.5, 59.5, -4.5, 61.5)),
    ('MR', 'control cabinet', rect(-10.8, 58.0, -10.2, 61.0)),
]
# Things the player crouches UNDER (not blockers): (name, poly, clear height)
CROUCH = [('pipe bank', rect(-20.5, 8.3, -14.5, 9.7), 1.2),
          ('substation grill', rect(29.6, 45.9, 30.4, 47.1), 1.2)]
# One-way drops: (name, from, to, from height, to height)
DROPS = [('vent grille out, drop onto the dock', (12, 45.75), (10.8, 45.75), 0.0, -1.75)]
# Moving machinery: (name, centre, radius, kind)
MOVING = [('compressor piston, rising and falling', (38.0, 4.75), 2.0, 'piston'),
          ('big fan in the pipe room north wall: 3 m, three blades, stops blade-up', (18.0, 51.0), 1.5, 'fan')]
# The fan you crouch through once stopped (user: a crouch is fine, rooms stay small). Checked in check().
FAN = {'diameter': 3.0, 'blades': 3, 'hub_height': 1.75, 'hub_radius': 0.3, 'blade_width': 0.3, 'lip': 0.25}
# Hinged catwalk sections: (name, poly). Raised 90 degrees until a switch lowers them.
DRAWBRIDGES = [('raised catwalk section (3): hinged at door 5, lowered by the cage switch', rect(-17, 36.75, -12, 38.25))]
# Levers and panels: (name, point)
LEVERS = [('switch panel: 1 sparks, 2 opens door 5 (distant), 3 opens door 1 (nearby)', (-19.4, 7.1)),
          ('cage switch: lowers the raised catwalk section (3)', (-27.5, 35.2)),
          ('fan lever: the big fan spins down and stops', (20.8, 52.8))]
# Overhead things (drawn dashed): the crane rail and its hanging container.
OVERHEAD = [
    ('crane rail', [(0, 4), (0, 40)]),
    ('hanging container', rect(-1.25, 19.0, 1.25, 25.0)),
]
# Heights of the overhead things (absolute). Roof beams cross the bay on the 4 m beat and carry the rail; the trolley
# runs under the rail, and the container hangs on four cables from a spreader, 4 m over the bay floor.
CRANE = dict(beam=(6.9, 7.5), beam_w=0.4, pitch=4.0, rail=(6.4, 6.9), rail_w=0.3, trolley=(5.9, 6.4),
             container=(1.0, 3.6), spreader=0.15, cable=0.06)
# Old burrows sealed with poured concrete (the clues): (clue, centre on the surface, the wall's plan normal or None
# for a floor, centre height (a wall) or floor height, radius, how far it stands proud).
PATCHES = [((45.4, 26.0), (46.0, 26.0), (-1, 0), -4.75, 0.6, 0.08),
           ((60.0, 11.0), (60.0, 11.0), None, -4.5, 0.95, 0.05)]
# The compressor's piston: its radius, stroke and cycle, and the housing's depth under the ceiling. The compressor
# is low (2.2 m) so the piston's stroke happens at eye level from both lanes of the U.
PISTON = dict(radius=0.85, stroke=0.9, period=2.4, housing_depth=1.1)
# Rails standing on their own (not at a drop): the compressor's enclosure, open to the spine on its west side.
RAILINGS = [('compressor enclosure', [(34, 2.0), (42, 2.0), (42, 7.5), (34, 7.5)])]
# Soft lights for dark places the player should still read (user: the girder crawl, with the flashlight):
# (name, plan point, height, energy, range, corridor or room key)
SOFT_LIGHTS = [('girder crawl, by its ladder', (47.5, 18.6), -5.4, 0.18, 4.0, 'BG')]
BRIDGES = [('Pump bridge (box girder, crawl inside)', rect(34, 17.0, 46, 19.0), -4.0)]
# Not walkable: coolant channel south of the bridge (the glow in the pit).
HAZARDS = [('Coolant channel', rect(34, 15, 46, 16.5))]
# Coolant pumps standing in the channel (user, 2026-09-27): each draws from the coolant and drives it up an outlet pipe
# that arches over the bridge into the top of the reactor opposite. A plunger (an rb_machine) rises from the housing
# to the walkway's eye level and falls back; the three take turns. Heights are absolute; the reactor is the 'pump'
# blocker at the same x.
COOLANT_PUMPS = dict(xs=(37.0, 40.0, 43.0), y=15.75, half=(1.0, 0.6), housing=(-6.1, -4.9), low=0.7, stroke=1.7,
                     period=3.0, posts=0.62, post_w=0.14, beam=(-1.9, -1.7), pipe_dx=0.8, pipe_r=0.16, pipe_h=(-1.0, -0.7),
                     reactor_y=23.0)

# --- openings, doors, gates and releases -----------------------------------------------
# Open junctions between spaces, drawn as gaps in the walls: (a, b)
OPENINGS = [
    ((-2.5, -11), (2.5, -11)), ((-2.5, 0), (2.5, 0)),                  # C1 ends
    ((-12, 10.75), (-12, 16.25)), ((-22.5, 10.75), (-22.5, 16.25)),    # pipe run ends
    ((-20.2, 10.5), (-14.8, 10.5)),                                    # pipe bay mouth
    ((14, 3.75), (14, 9.25)), ((26, -3.25), (26, 2.25)),               # trench ends
    ((34, 12), (38, 12)),                                              # U-turn into the pump room
    ((50, 39.75), (50, 42.25)), ((51.25, 24.5), (53.75, 24.5)),        # east stairs ends
    ((-1.75, 40), (1.75, 40)), ((-12, 44.25), (-12, 45.75)),                 # dock steps, truck bay stair
    ((25.75, 25), (28.25, 25)), ((15.5, 25), (17.5, 25)),                 # access corridor, ladder room doorway
    ((14, 45.1), (14, 46.4)),                                              # vent mouth in the pipe room
    ((-10, 55.5), (-8.5, 55.5)), ((-2, 56.25), (-2, 58.75)),               # catwalk into the machine room, jog out
    ((7.5, 61.25), (7.5, 63.75)), ((13.5, 51.25), (13.5, 52.75)),          # jog into the stair room, out to the fan chamber
    ((13.5, 61.25), (13.5, 63.75)),                                        # top landing into the stair corridor
]
# (name, point, kind) kind: airlock / lock / release / gate / window / lift / door
DOORS = [
    ('Airlock (previous level)', (0, -28), 'airlock'), ('Airlock door', (0, -22), 'airlock'),
    ('Lift gate: needs K + P', (0, 47.5), 'lift'),
    ('Logistics west door', (-22.5, 27.5), 'door'),
    ('Cage gate (released from the archive)', (-24, 37.0), 'lock'),
    ('S1: opens from Logistics once K is taken', (-12, 39), 'release'),
    ('S2: the pump room east door, card M from the lobby side', (50, 17.5), 'release'),
    ('Quarantine hold door: card M', (53, 15), 'release'),
    ('Overlook window', (-12, 26.5), 'window'),
    ('Substation grill: slide open, crouch through', (30, 46.5), 'grill'),
    ('Vent grille: open it, drop onto the dock', (12, 45.75), 'grill'),
    ('Door 1: the secret closet, opened by switch 3 (you hear it nearby)', (-23.5, 10), 'release'),
    ('Door 5: high in Logistics east wall, opened by switch 2 (a distant clunk)', (-12, 37.5), 'release'),
    ('Big fan: the lever stops it, walk through the blades (chamber side only)', (18, 51), 'fan'),
    ('Door 3: raised onto the north catwalk, opens only from the stair corridor', (32, 54), 'release'),
    ('Truck bay roll door: sealed, breached in the final hold', (-26, 46), 'lock'),
]
# --- encounter triggers: they span EVERY path into their space (user rule) ------------
# Area triggers only; the cage, the power restore and the lift call are event triggers.
TRIGGERS = [
    ('Bay fight: the whole bay floor', rect(-12, 3.5, 12, 37.5)),
    ('Pump fight: the full south band, the only first-visit way in', rect(33, 12, 47, 15)),
]
# The lift requirements, the release that guards K, and the card that opens the east stairs' doors.
OBJECTIVES = [
    ('K: freight clearance card, in the supervisor cage', (-26.0, 37.0)),
    ('P: auxiliary power restore switch, end of the gantry', (48.0, 45.5)),
    ('M: maintenance card, gantry control booth', (48.5, 35.5)),
    ('Release: opens the cage gate, far end of the archive maze', (-26.0, 33.5)),
]
SECRETS = [
    ('ammo: crawl inside the conveyor platform', (4.0, 17.1)),
    ('health: archive drawer bank (desk code)', (-27.65, 39.0)),
    ('armour and health: the closet behind door 1', (-23.2, 7.8)),
    ('ammo: crawl inside the pump bridge', (40.0, 18.0)),
    ('armour: cable vault behind the last cage', (47.3, 53.0)),
]
# Designed-in rewards the player can see (not secrets).
REWARDS = [
    ('ammo container, seen beneath the pipes', (-17.5, 7.3)),
    ('armour and ammo, supply cage', (58.5, -1.0)),
    ('pickups under the top landing: behind you to the right at the bottom', (9.0, 62.3)),
]
# Optional story clues: the aliens have been here a long time. Nothing states it.
CLUES = [
    ('sealed burrow behind a concrete patch in the pit wall', (45.4, 26.0)),
    ('quarantine stamps, years old', (55.2, 4.0)),
    ('floor burrow patched long ago', (60.0, 11.0)),
    ('filters clogged with old organic matter', (18.0, 18.2)),
]
DAMAGE = [('hanging fitting, sparks', (0.0, -5.5))]
SHOTS = [
    ('gallery reveal', (-4.0, 2.2)), ('office overlook', (-14.0, 32.0)), ('compressor round the U', (44.5, 0.0)),
    ('pit from the bridge', (36.5, 17.5)), ('power on', (47.0, 44.5)), ('lift doors', (0.0, 44.0)),
    ('the fan, just before the vent', (20.5, 46.0)),
]
OPTIONAL = []

# --- routes, for length estimates ---------------------------------------------------------
# A third element tags a point off the ground floor (archive, cage, crawl) or crouched (crouch);
# tagged legs skip the blocker test.
START = [(0, -25), (0, -21), (0, -11), (0, 2), (-10.5, 2), (-10.5, 10.5)]
WEST = [(-12, 13.5), (-17.5, 12), (-17.5, 10.8), (-17.5, 8.0, 'crouch'), (-17.5, 10.8), (-22.5, 13.5), (-27.5, 14.5),
        (-27.5, 20.5), (-24, 21.5), (-24, 27.5), (-22.5, 27.5), (-20, 27), (-14.6, 27), (-14.6, 33), (-20, 33), (-22, 33.3),
        (-21.9, 36.5), (-21.9, 39.1), (-23.2, 39.1, 'archive'), (-25, 37.5, 'archive'), (-26, 33.5, 'archive'),
        (-23.2, 39.1, 'archive'), (-21.9, 39.1), (-23.5, 37), (-26, 37, 'cage'),
        (-23.5, 37), (-23.2, 36), (-18, 36.5), (-13.3, 39), (-12, 39), (-10.5, 39), (-10.5, 29.3)]
S1_TO_TRENCH = [(-10.25, 26), (-3, 26), (-2.25, 21), (-2.25, 15), (10, 8)]
# Bay -> trench -> U-turn -> pump room -> pit -> crawl -> substation -> gantry: M, then P.
EAST_IN = [(14, 6.5), (20, 6.5), (20, -0.5), (26, -0.5), (27.5, -1), (29, -1), (43, -1), (44.5, 1), (44.5, 4.3), (44.5, 9.5),
           (36, 9.8), (36, 12), (36, 13.5), (32, 16), (33.4, 21), (34.45, 21), (35.5, 25.8), (40, 25.8),
           (40, 32, 'crawl'), (33, 32, 'crawl'), (33, 35.65, 'lb'), (33, 36.9), (35.5, 35.8), (43.4, 35.8, 'gantry'), (48.5, 35.5, 'gantry'), (48, 37, 'gantry'), (48, 45.5, 'gantry')]
TO_LOBBY = [(48, 41, 'gantry'), (50, 41), (52.5, 41), (52.5, 24), (53, 18)]
HOLD = [(53, 16.4), (53, 15), (53, 11.5), (55.25, 8.5), (55.25, 0.4), (58.5, 0.4), (55.25, 0.4), (55.25, 8.5), (53, 11.5), (53, 15),
        (53, 18)]
LOBBY_UP = [(52.5, 24), (52.5, 41), (50, 41), (48, 41, 'gantry')]
# The S2 return: through the pump room, the U-turn and the trench to the bay.
S2_BACK = [(52, 17.5), (51.2, 17.5), (50, 17.5), (48, 18.0), (36, 18.0), (32, 17.5), (32, 16), (36, 13.5), (36, 12), (36, 9.8), (44.5, 9.5),
           (44.5, 4.3), (44.5, 1), (43, -1), (29, -1), (27.5, -1), (26, -0.5), (20, -0.5), (20, 6.5), (14, 6.5)]
# The vent return (revision 03): grill, access corridor, filter room, ladder room, pipe room, vent, drop, lift.
VENT_BACK = [(48, 37, 'gantry'), (43.4, 35.8, 'gantry'), (35.5, 35.8), (33, 38), (31, 46.5), (30, 46.5, 'crouch'), (27, 46.5), (27, 27), (27, 25),
             (27, 21), (17, 21), (16.5, 24), (16.5, 26.5), (15.5, 27.75), (15.5, 29.2), (17.5, 32), (18, 39), (16.8, 42.5),
             (15.5, 45.75), (14, 45.75, 'crawl'), (12, 45.75, 'crawl'), (10.8, 45.75), (0, 46)]
# Revision 07: the pipe bay switches (under the pipes) and the cage switch open the catwalk way.
SWITCHES = [(-19.2, 7.6, 'crouch'), (-17.5, 8.0, 'crouch')]
W_SW = WEST[:4] + SWITCHES + WEST[4:]
CLOSET = [(-22.5, 13.5), (-23.5, 11.5), (-23.5, 10), (-23.2, 7.8), (-23.5, 10), (-23.5, 11.5)]
W_EXPLORE = WEST[:4] + SWITCHES + WEST[4:6] + CLOSET + WEST[6:]
CAGE_SWITCH = [(-27.3, 35.4, 'cage'), (-26, 37, 'cage')]


def to_k(west):
    """The west route as far as K, with the cage switch flipped while inside the cage."""
    k = west.index((-26, 37, 'cage'))
    return west[:k + 1] + CAGE_SWITCH + [(-23.5, 37)]


# The catwalk way: back up to the archive, over the lowered section and through door 5, over the bay, north through the
# pass-through rooms to the stair room's top landing. From there, along the stair corridor to door 3 or down to the fan.
CATWALK_IN = [(-21.9, 38.2), (-21.9, 39.1), (-23.2, 39.1, 'archive'), (-22.5, 37.5, 'catwalk'), (-9.25, 37.5, 'catwalk'), (-9.25, 55.5, 'catwalk'),
              (-9.25, 57.6), (-2, 58), (1.5, 58), (6, 62.5), (7.5, 62.5), (9, 62.5)]
# Along the stair corridor, through raised door 3 onto the north catwalk, along it to P, back and down the ladder to
# the grill: then the vent way to the lift.
TO_SUBSTATION = [(12.5, 62.5), (13.5, 62.5), (15.5, 62.5), (21.5, 62.5), (23.5, 62.5), (30.9, 55.1), (32, 54), (33.5, 54, 'gantry'),
                 (46, 54, 'gantry'), (48.2, 52, 'gantry'), (48, 48, 'gantry'), (48, 45.5, 'gantry'), (48, 48, 'gantry'),
                 (48.2, 52, 'gantry'), (46, 54, 'gantry'), (35, 54, 'gantry'), (34.0, 53.75, 'gantry'), (34.0, 52.5),
                 (31.5, 47)] + VENT_BACK[4:]
# Or down the stair (east side): the pickups behind you to the right, out to the fan chamber, the lever, crouch through
# the stopped fan, through the pipe room, down the ladder, along the duct, through the grill, up the gantry to M and P.
FAN_TO_P = [(12, 62), (12, 61), (12, 53), (12, 52), (9, 53), (9, 62.3), (9, 53), (12, 52), (13.5, 52), (20.8, 52.8),
            (18, 52.3), (18, 50.5, 'crouch'), (17.2, 47.2), (16.5, 45.8), (16.8, 42.5), (18, 39), (17.5, 32), (15.5, 29.2),
            (15.5, 27.75), (16.5, 26.5), (16.5, 24), (17, 21), (27, 21), (27, 25), (27, 27), (27, 46.5), (28.8, 46.5), (30, 46.5, 'crouch'),
            (31, 46.5), (33, 38), (35.5, 35.8), (43.4, 35.8, 'gantry'), (48.5, 35.5, 'gantry'), (48, 37, 'gantry'),
            (48, 45.5, 'gantry')]
# Every route ends in the lift: through its gate (K and P) to the finish inside.
IN_LIFT = [(0, 50.5)]
ROUTES = {
    'card first, vent return': START + WEST + S1_TO_TRENCH + EAST_IN + VENT_BACK + IN_LIFT,
    'power first, S2 return': START + [(10, 8)] + EAST_IN + TO_LOBBY + HOLD + S2_BACK + [(10, 8), (-10.5, 10.5)] + WEST
                              + [(0, 36.8), (0, 46)] + IN_LIFT,
    'completionist, east': START + WEST + S1_TO_TRENCH + EAST_IN + TO_LOBBY + HOLD + LOBBY_UP + VENT_BACK + IN_LIFT,
    'knowing player, catwalk to P': START + to_k(W_SW) + CATWALK_IN + TO_SUBSTATION + IN_LIFT,
    'catwalk explorer': START + to_k(W_EXPLORE) + CATWALK_IN + FAN_TO_P + VENT_BACK + IN_LIFT,
}
FINISH = IN_LIFT[0]
_W = list(WEST)
_W.insert(_W.index((-20, 27)) + 1, (-17.0, 26.8))                                 # read the note on the desk
_W.insert(_W.index((-25, 37.5, 'archive')) + 1, (-26.3, 39.0, 'archive'))         # open the drawer bank with its code
SECRET_WEST = _W[:4] + SWITCHES + _W[4:6] + CLOSET + _W[6:]
CONVEYOR_CRAWL = [(10.5, 12.0), (10.6, 17.1), (9.2, 17.1, 'crouch'), (4.0, 17.1, 'crouch'), (9.2, 17.1, 'crouch'),
                  (10.6, 17.1), (10.5, 12.0), (-10.5, 10.5)]
GIRDER_CRAWL = [(47.5, 13.5), (49.0, 21.55), (47.5, 21.55), (47.5, 20.3, 'lb'), (47.5, 19.25, 'crawl'),
                (47.5, 18.0, 'crawl'), (40.0, 18.0, 'crawl'), (47.5, 18.0, 'crawl'), (47.5, 19.25, 'crawl'),
                (47.5, 20.3, 'lb'), (47.5, 21.55), (49.0, 21.55), (48.5, 27.5), (35.5, 28.5), (33.0, 27.5), (32.5, 21)]
CABLE_VAULT = [(31.5, 38), (31.5, 47), (32.5, 53.9), (43.7, 53.9), (43.7, 53.0), (44.95, 53.0, 'lb'), (47.3, 53.0)]
SECRET_ROUTES = {
    'secrets': START + CONVEYOR_CRAWL + SECRET_WEST + S1_TO_TRENCH + EAST_IN[:EAST_IN.index((36, 13.5)) + 1]
               + GIRDER_CRAWL + EAST_IN[EAST_IN.index((33.4, 21)):EAST_IN.index((33, 36.9)) + 1] + CABLE_VAULT,
}

# ================================================================================
# Progression (G-02): what opens what. Read by the 3D build (map entities) and the route checker.
# ================================================================================
# Names the prompts give the flags ("Needs the freight card and power").
FLAG_TEXT = {'K': 'the freight clearance card', 'P': 'power', 'M': 'the maintenance card', 'CODE': 'the drawer code'}
# Door rules, by the start of the door's name in DOORS:
#   opens  use (E either side) / side (E only from the side 'side' points to) / event (a switch only) / start (level ready)
#   needs  flags; latch: stays open; style: rise (up into the wall) or slide (two leaves apart: gates in fences)
DOOR_RULES = [
    ('Airlock door', dict(id='AIRLOCK', opens='start', latch=1)),
    ('Logistics west door', dict(id='LGW', opens='use')),
    ('Cage gate', dict(id='CAGE', opens='event', events='cage', latch=1, style='slide')),
    ('S1:', dict(id='S1', opens='side', side=(-1, 0), needs='K', latch=1)),
    ('S2:', dict(id='S2', opens='side', side=(1, 0), needs='M', latch=1)),
    ('Quarantine hold door', dict(id='HOLD', opens='side', side=(0, 1), needs='M', latch=1)),
    ('Substation grill', dict(id='GRILL', opens='use', latch=1)),
    ('Vent grille', dict(id='VENT', opens='side', side=(1, 0), latch=1)),
    ('Door 1:', dict(id='D1', opens='event', events='door1', latch=1)),
    ('Door 5:', dict(id='D5', opens='event', events='door5', latch=1)),
    ('Door 3:', dict(id='D3', opens='side', side=(-0.7071, 0.7071), latch=1)),
    ('Lift gate', dict(id='LIFT', opens='side', side=(0, -1), needs='K,P', latch=1, style='slide')),
    # Not a room door: the drawer in the archive's drawer bank, placed on the cabinet's front at its niche.
    ('(archive drawer)', dict(id='DRAWER', at=(-27.4, 39.0), floor=4.6, facing=(1, 0), width=0.6, height=0.5, room='LG',
                              opens='use', needs='CODE', latch=1, style='slide', lamp_depth=0.07)),
]
# Switches and levers: (id, name, plan point on the wall face or floor, floor height, facing, mount, what it does).
KIT_SWITCHES = [
    ('SW1', 'pipe bay switch 1: sparks', (-19.1, 6.5), -3.0, (0, 1), 'wall', dict(effect='spark', once=0)),
    ('SW2', 'pipe bay switch 2: door 5, a distant clunk', (-18.6, 6.5), -3.0, (0, 1), 'wall',
     dict(sends='door5', notice='A distant clunk.')),
    ('SW3', 'pipe bay switch 3: door 1, nearby', (-18.1, 6.5), -3.0, (0, 1), 'wall',
     dict(sends='door1', notice='A door opens nearby.')),
    ('RELEASE', 'archive lever: the cage gate', (-25.6, 32.0), 4.0, (0, 1), 'wall', dict(sends='cage')),
    ('CAGE_SW', 'cage switch: lowers the raised catwalk section (3)', (-28.0, 35.2), 1.0, (1, 0), 'wall',
     dict(sends='drawbridge')),
    ('P', 'P: auxiliary power restore, end of the gantry', (49.2, 45.5), 1.0, (-1, 0), 'post',
     dict(sets='P', sends='power', notice='Auxiliary power restored.')),
    ('FAN_LEVER', 'fan lever: the big fan spins down and stops', (21.5, 53.0), 0.0, (-1, 0), 'wall', dict(sends='fan_stop')),
    ('NOTE', 'a note on a dispatch desk: the drawer code', (-17.0, 25.5), 1.8, (0, 1), 'flat',
     dict(sets='CODE', notice='A note on the desk: DRAWER 4 1 7.', prompt='E  Read')),
]
# Cards: (id, name, plan point, floor height, flag, colour)
KIT_PICKUPS = [
    ('K', 'K: freight clearance card, in the supervisor cage', (-27.0, 38.6), 1.0, 'K', (1.0, 0.7, 0.2)),
    ('M', 'M: maintenance card, the gantry control booth', (49.3, 34.8), 1.0, 'M', (0.2, 0.85, 1.0)),
]
# The big fan in the pipe room's north wall (hub centre), and the hinged catwalk section at door 5.
KIT_FAN = dict(id='FAN', point=(18.0, 51.0), floor=0.0, facing=(0, 1), event='fan_stop')
KIT_DRAWBRIDGE = dict(id='DRAWBRIDGE', hinge=(-12.25, 37.5), height=4.0, extends=(-1, 0), length=4.75, width=1.5,
                      event='drawbridge')
# What the route checker does at a route point (the first time a route reaches it): use these kit pieces, in order.
ROUTE_ACTIONS = {
    (-24, 27.5): 'LGW', (-26, 33.5): 'RELEASE', (-26, 37): 'K', (-27.3, 35.4): 'CAGE_SW', (-19.2, 7.6): 'SW2,SW3',
    (-13.3, 39): 'S1', (48.5, 35.5): 'M', (48, 45.5): 'P', (31, 46.5): 'GRILL', (28.8, 46.5): 'GRILL',
    (14, 45.75): 'VENT', (30.9, 55.1): 'D3', (53, 16.4): 'HOLD', (51.2, 17.5): 'S2', (20.8, 52.8): 'FAN_LEVER',
    (0, 46): 'LIFT', (-17.0, 26.8): 'NOTE', (-26.3, 39.0): 'DRAWER',
}
# At level start these must refuse the player standing here: (kit id, plan point, tag).
REFUSALS = [
    ('S1', (-13.3, 39), None),              # no K yet
    ('S2', (48.5, 17.5), None),             # the pump room side, and no M
    ('HOLD', (53, 16.4), None),             # no M
    ('D3', (33.5, 54), 'gantry'),           # the substation side of door 3
    ('CAGE', (-23.0, 37.0), None),          # only the archive lever opens it
    ('LIFT', (0, 46), None),                # no K, no P
]
# At level start the running fan closes its hole: a crouching player cannot pass (plan point, floor height).
FAN_BLOCKED = ((18.0, 51.0), 0.0)


# ================================================================================
# 3D build data (G-01 greybox). Read by tools/bootstrap-freight-v2.py; not drawn.
# ================================================================================
FLOOR_T, WALL_T, CEIL_T = 0.25, 0.5, 0.5
# Absolute ceiling heights. A list gives (region, height) pairs; the first region containing a point wins.
CEILINGS = {
    'AL': 3.5, 'RC': 3.0, 'SB': 7.5, 'DK': 7.5, 'TB': 3.0, 'SC': -0.5, 'WX': 0.0, 'ST': 4.0,
    'LG': [(rect(-17.5, 36.5, -12, 38.5), 9.5), (rect(-28, 32, -12, 40), 7.5), (rect(-22.5, 22, -12, 32), 4.5)],
    'CU': 1.5, 'PR': 3.0, 'SS': 4.5, 'FL': 0.5, 'LR': 2.75, 'PP': 4.0, 'MR': 7.5, 'R3': 7.0, 'FC': 3.5,
    'LL': -0.5, 'QH': 0.0, 'CV': -2.75,
}
# Levels built as thin decks on the open space below (the rest are solid platforms).
DECKS = {'Gantry', 'Archive (above the cage)', 'Stair room top landing'}
DECK_T = 0.3
# Boundaries between rooms that stay open (a dock edge, not a wall).
OPEN_EDGES = [('SB', 'DK'), ('DK', 'TB')]
# Clear sections per corridor profile: (clear width, clear height). P1/P2 come from the style lab's profiles.
PROFILE_BOX = {'S3': (3.0, 3.0), 'D2': (2.0, 2.3), 'crawl': (1.5, 1.25), 'catwalk': (1.5, 2.6)}
# Blocker heights above the floor they stand on, first keyword match wins; 'ceiling' runs to the room's ceiling.
BLOCKER_H = [
    ('decon arch', 2.6), ('parcel rack', 2.2), ('receiving desk', 1.0), ('office desk', 0.8), ('pallet jack', 0.4),
    ('conveyor platform', 1.4), ('conveyor', 1.0), ('container stack', 5.2), ('quarantine container', 2.6),
    ('burst open', 2.6), ('containers', 2.6), ('booth console', 1.0), ('booth seats', 0.5), ('lift cage', 3.6),
    ('pallets', 1.2), ('cargo hauler', 2.6), ('dispatch counter', 1.1), ('desk row', 0.8), ('lockers', 2.0),
    ('toppled cabinet', 0.7), ('drawer bank', 1.3), ('supervisor cage', 3.0), ('ammo container', 0.6), ('closet shelves', 2.0),
    ('spine', 3.2), ('air compressor', 2.2), ('hydraulic pump', 1.8), ('pump', 3.5), ('valve stand', 1.2),
    ('transformer cage', 2.5), ('fallen cable tray', 0.25), ('supply cage', 2.2), ('filter bank', 2.6), ('blower', 2.8),
    ('pipe rack', 1.5), ('up through the ceiling', 'ceiling'), ('riser', 2.7), ('valve manifold', 1.4),
    ('control cabinet', 2.0),
]
# Door openings by kind: (width, height). Sealed doors get a panel, not a hole.
DOOR_SIZE = {'airlock': (2.0, 2.5), 'door': (2.0, 2.5), 'release': (2.0, 2.5), 'lock': (2.0, 2.5), 'lift': (3.0, 3.2),
             'grill': (1.2, 1.2), 'window': (4.0, 1.2)}
WINDOW_SILL = 1.0
SEALED = ('Airlock (previous level)', 'Truck bay roll door', 'Lift gate', 'Cage gate')
# Explicit openings that are not corridor mouths: (a, b, bottom, top) absolute; None heights mean
# floor + DEFAULT_OPENING_H at that point.
DEFAULT_OPENING_H = 3.0
OPENING_3D = [
    ((-20.2, 10.5), (-14.8, 10.5), None, None),          # pipe bay mouth off the pipe run
    ((34, 12), (38, 12), None, None),                     # U-turn into the pump room
    ((15.5, 25), (17.5, 25), None, 2.5),                  # filter room into the ladder room (2.5 m clear)
    ((14.9, 28.5), (16.1, 28.5), 0.0, 2.4),               # the ladder's top: ladder room into the pipe room
    ((13.5, 51.25), (13.5, 52.75), None, 2.5),            # stair room foot into the fan chamber
]
# The fan in the pipe room's north wall: G-01 builds it stopped, as a crouch-through hole.
FAN_HOLE = {'room_edge': ((21, 51), (15, 51)), 'centre': 18.0, 'floor': 0.0}
# Ladders in 3D: the direction the climber faces (into the ladder). Secret ladders wait for their interiors.
LADDER_FACING = {
    'Archive ladder (12 rungs)': (-1, 0), 'Pit ladder': (-1, 0), 'Pipe gallery ladder (12 rungs)': (0, 1),
    'Gantry ladder (14 rungs)': (0, 1), 'Ladder room ladder (12 rungs)': (0, 1),
    'Bridge crawl ladder (secret)': (0, 1), 'Cable vault ladder (secret)': (-1, 0),
}
LADDER_SHAFT = {'Pipe gallery ladder (12 rungs)': rect(32.25, 34.6, 33.75, 36.1),
                'Bridge crawl ladder (secret)': rect(46.75, 19.25, 48.25, 20.75)}
# Crawl corridors closed at an end that meets nothing (the girder's west end, in the pit).
CRAWL_CAPS = {'BG': 'start'}
# Holes in a room's floor where a ladder comes up from a room below (the cable vault's hatch in the alley).
FLOOR_HATCHES = {'SS': [rect(44.5, 52.35, 46.0, 53.65)]}
# Blockers with a walk-in space: the open end's plan direction (the conveyor platform, crawled from its east end).
HOLLOW = {'conveyor platform (crawl inside)': (1, 0)}
# Blockers standing on a raised level rather than the room floor.
BLOCKER_ON = {'drawer bank': 'Archive (above the cage)'}
# Lighting for the greybox: (spacing m, energy, range m, shadows) per kind of space.
LIGHT_ROOM = (6.5, 2.2, 13.0, True)
# A room light covers walkable samples within this plan radius, in line of sight (2.2 energy at ~3.6 m keeps 0.35).
LIGHT_REACH = 4.5
LIGHT_CORRIDOR = {'P1': (4.0, 0.9, 9.0, False), 'P2': (4.0, 0.9, 9.0, False), 'S3': (4.5, 0.8, 7.0, False),
                  'D2': (4.0, 0.55, 5.0, False), 'crawl': (4.0, 0.45, 4.0, False), 'catwalk': (5.0, 0.8, 8.0, False)}


# Player-eye capture views for the greybox sheet: (name, eye (x, y, floor h), look-at (x, y, h), crouch).
VIEWS_3D = [
    ('01 airlock', (0, -26.5, 0), (0, -12, 1.6), False),
    ('02 receiving', (-1, -20.8, 0), (4, -12, 1.2), False),
    ('03 C1 to the bay', (0, -10, -0.5), (0, 1, 1.0), False),
    ('04 gallery reveal', (-4, 2.2, -0.5), (0, 30, -1.5), False),
    ('05 bay floor', (-8, 12, -3), (5, 35, 0), False),
    ('06 pipe run', (-13, 13.5, -3), (-22, 13.5, -2), False),
    ('07 pipe bay', (-17.5, 11.5, -3), (-17.5, 7, -2.5), False),
    ('08 west stairwell', (-27.5, 12, -3), (-27.5, 21, -0.5), False),
    ('09 logistics', (-21, 23.5, 1), (-14, 36, 2), False),
    ('10 archive', (-23.5, 39, 4), (-26, 33, 4), False),
    ('11 catwalk over the bay', (-10.5, 37.5, 4), (5, 20, -1), False),
    ('12 service trench', (13, 6.5, -3), (20, -0.5, -2), False),
    ('13 compressor U-turn', (29.5, -1, -3.5), (44, 2, -2), False),
    ('14 pump room', (36, 13.5, -4), (40, 23, -4), False),
    ('15 pump pit', (35.5, 20, -5.5), (40, 26, -4.5), False),
    ('16 substation', (33, 37, -2.5), (45, 45, 0), False),
    ('17 gantry', (44, 35.8, 1), (48, 50, 0), False),
    ('18 air duct hallway', (27, 45, -2.5), (27, 30, -2), False),
    ('19 filter room', (27, 23.5, -3), (17, 21, -2), False),
    ('20 pipe room', (17, 30, 0), (18, 50, 1.5), False),
    ('21 vent drop', (13.5, 45.75, 0), (5, 45.75, -1.5), True),
    ('22 dock and lift', (0, 41, -1.75), (0, 52, 0), False),
    ('23 lift machine room', (-9, 57, 4), (-2, 58, 5), False),
    ('24 stair room', (9, 62.5, 4), (12, 53, 1), False),
    ('25 fan chamber', (15, 54, 0), (18, 51, 1.5), False),
    ('26 east stairs', (52.5, 40, 1), (52.5, 26, -3), False),
    ('27 quarantine hold', (53, 13, -4), (58, 2, -3), False),
]


def xy(p):
    return (p[0], p[1])


def route_length(points):
    return sum(math.dist(xy(a), xy(b)) for a, b in zip(points, points[1:]))


def inside(pt, poly):
    x, y = pt
    c = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    L2 = (bx - ax) ** 2 + (by - ay) ** 2
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay)) / L2))
    return math.dist(p, (ax + t * (bx - ax), ay + t * (by - ay)))


def edge_dist(pt, poly):
    return min(seg_dist(pt, a, b) for a, b in zip(poly, poly[1:] + poly[:1]))


def segs_cross(a, b, c, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0


def corridor_width(prof):
    return {'P1': 6.0, 'P2': 6.0, 'S3': 3.0, 'D2': 2.0, 'catwalk': 1.5, 'crawl': 1.5}[prof]


DUCT_RIB_PITCH = 2.0  # D2: a tiny rib where the steel sheets join


def walkable(pt, tol=0.0):
    """Is a plan point on some floor: a room, a level, a bridge or a corridor band?"""
    for key, name, poly, floor, look in ROOMS:
        if inside(pt, poly) or edge_dist(pt, poly) <= tol:
            return True
    for name, poly, h, kind in LEVELS:
        if inside(pt, poly):
            return True
    for key, name, prof, path, heights, look in CORRIDORS:
        if any(seg_dist(pt, a, b) <= corridor_width(prof) / 2 + tol for a, b in zip(path, path[1:])):
            return True
    return False


RISER, TREAD, RUNG, PLAYER_R = 0.25, 0.5, 0.25, 0.3
DROP_MAX = 2.0
CROUCH_H, STAIR_MAX_W, STEP_H = 1.1, 3.5, 0.3
ENTERABLE = {'supervisor cage': 'Cage gate', 'lift cage': 'Lift gate'}   # walk-in blockers and the gate in their fence


def check():
    """Self-checks: returns a list of problems (empty when the plan is consistent)."""
    bad = []
    names = {r[0]: r for r in ROOMS}
    for room, name, poly in BLOCKERS:
        if room not in names:
            bad.append(f'blocker {name} in unknown room {room}')
        elif not all(inside(q, names[room][2]) or edge_dist(q, names[room][2]) < 1e-6 for q in poly):
            bad.append(f'blocker {name} pokes out of {room}')
    for key, name, prof, path, heights, look in CORRIDORS:
        if len(path) != len(heights):
            bad.append(f'{key}: {len(path)} points, {len(heights)} heights')
            continue
        for (a, ha), (b, hb) in zip(zip(path, heights), zip(path[1:], heights[1:])):
            run, rise = math.dist(a, b), abs(hb - ha)
            if rise and run + 1e-6 < rise / RISER * TREAD:
                bad.append(f'{key}: {rise} m rise needs {rise / RISER * TREAD} m of run, has {run:.2f}')
            # User rule (revision 02): a flight is never the full width of a 6 m corridor.
            if rise > 2 * RISER and corridor_width(prof) > STAIR_MAX_W:
                bad.append(f'{key}: a {rise} m flight {corridor_width(prof)} m wide; stairs are {STAIR_MAX_W} m at most')
    for name, poly, h0, h1, (ux, uy) in STAIRS:
        xs, ys = [q[0] for q in poly], [q[1] for q in poly]
        run = (max(xs) - min(xs)) if ux else (max(ys) - min(ys))
        width = (max(ys) - min(ys)) if ux else (max(xs) - min(xs))
        need = abs(h1 - h0) / RISER * TREAD
        if run + 1e-6 < need:
            bad.append(f'stair {name}: {abs(h1 - h0)} m rise needs {need} m of run, has {run}')
        if abs(h1 - h0) > 2 * RISER and width > STAIR_MAX_W + 1e-6:
            bad.append(f'stair {name}: {width} m wide; flights are {STAIR_MAX_W} m at most')
        if not all(walkable(q, 1e-6) for q in poly):
            bad.append(f'stair {name} leaves the floor plan')
    for name, pt, h0, h1 in LADDERS:
        rungs = abs(h1 - h0) / RUNG
        if abs(rungs - round(rungs)) > 1e-6:
            bad.append(f'ladder {name}: {abs(h1 - h0)} m is not whole rungs')
        if not walkable(pt):
            bad.append(f'ladder {name} at {pt} is outside every room and corridor')
    for name, poly, clear in CROUCH:
        if clear < CROUCH_H + 0.05:
            bad.append(f'crouch {name}: {clear} m clear does not pass a {CROUCH_H} m crouch')
    # The stopped fan: blade up, so the gap below the hub spans +-(180 / blades) degrees about straight down.
    crouch_top = FAN['lip'] + CROUCH_H
    half = math.pi / FAN['blades']
    gap = 2 * (FAN['hub_height'] - crouch_top) * math.tan(half) - FAN['blade_width']
    if FAN['lip'] > STEP_H:
        bad.append(f"fan: a {FAN['lip']} m lip is more than a {STEP_H} m step")
    if crouch_top > FAN['hub_height'] - FAN['hub_radius']:
        bad.append(f'fan: a crouching player ({crouch_top:.2f} m) hits the hub')
    if gap < 2 * PLAYER_R + 0.1:
        bad.append(f'fan: the stopped gap is {gap:.2f} m at crouch height; a crouching player needs {2 * PLAYER_R + 0.1:.1f}')
    if abs(FAN['hub_height'] - FAN['diameter'] / 2 - FAN['lip']) > 1e-6:
        bad.append('fan: the disc must sit on its lip')
    for name, poly in DRAWBRIDGES:
        cw = [c for c in CORRIDORS if c[2] == 'catwalk']
        if not all(any(seg_dist(q, a, b) <= corridor_width('catwalk') / 2 + 1e-6 for c in cw for a, b in zip(c[3], c[3][1:]))
                   for q in poly):
            bad.append(f'drawbridge {name} is not on a catwalk')
    for name, a, b, h0, h1 in DROPS:
        if not 0 < h0 - h1 <= DROP_MAX:
            bad.append(f'drop {name}: {h0 - h1} m; drops are one-way and at most {DROP_MAX} m')
        if not (walkable(a) and walkable(b)):
            bad.append(f'drop {name} does not start and land on the plan')
    for group, items in (('lever', LEVERS), ('secret', SECRETS), ('reward', REWARDS), ('clue', CLUES), ('damage', DAMAGE), ('shot', SHOTS),
                         ('objective', OBJECTIVES)):
        for name, pt in items:
            if not walkable(pt):
                bad.append(f'{group} {name} at {pt} is outside every room and corridor')
    for name, pt, kind in DOORS:
        if not walkable(pt, 0.05):
            bad.append(f'door {name} at {pt} is not on a room or corridor')
    for a, b in OPENINGS:
        if not walkable(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), 0.05):
            bad.append(f'opening {a}-{b} is not on a room or corridor')
    for k, pts in ROUTES.items():
        for p in pts:
            if len(p) == 2 and not walkable(p, 0.05):
                bad.append(f'route {k}: {p} is off the floor plan')
        for a, b in zip(pts, pts[1:]):
            if len(a) == 3 or len(b) == 3:
                continue
            for room, name, poly in BLOCKERS:
                if name in ENTERABLE:
                    continue
                edges = list(zip(poly, poly[1:] + poly[:1]))
                hit = inside(xy(a), poly) or inside(xy(b), poly) or any(segs_cross(a, b, c, d) for c, d in edges)
                close = min(seg_dist(q, a, b) for q in poly) < PLAYER_R or any(
                    seg_dist(xy(e), c, d) < PLAYER_R for e in (a, b) for c, d in edges)
                if hit or close:
                    bad.append(f'route {k}: {xy(a)} -> {xy(b)} runs through {name}')
    names = [d[0] for d in DOORS]
    ids = set()
    for prefix, rule in DOOR_RULES:
        if 'at' not in rule and not any(n.startswith(prefix) for n in names):
            bad.append(f'door rule {prefix} names no door')
        ids.add(rule['id'])
    events = {r.get('events', r['id']) for _, r in DOOR_RULES} | {'start', 'fan_stop', 'drawbridge', 'power'}
    for sid, name, pt, h, facing, mount, what in KIT_SWITCHES:
        ids.add(sid)
        for e in what.get('sends', '').split(','):
            if e and e not in events:
                bad.append(f'switch {sid} sends {e}, which nothing listens for')
    for kid, name, pt, h, flag, colour in KIT_PICKUPS:
        ids.add(kid)
        if not walkable(pt):
            bad.append(f'card {kid} at {pt} is not in a room')
    needed = {f for _, r in DOOR_RULES for f in r.get('needs', '').split(',') if f}
    given = {w.get('sets', '') for *_, w in KIT_SWITCHES} | {k[4] for k in KIT_PICKUPS}
    for f in needed - given:
        bad.append(f'flag {f} is needed by a door but nothing sets it')
    for pt, acts in ROUTE_ACTIONS.items():
        for a in acts.split(','):
            if a not in ids:
                bad.append(f'route action {a} at {pt} names no door, switch or card')
        if not any(xy(q) == pt for pts in list(ROUTES.values()) + list(SECRET_ROUTES.values()) for q in pts):
            bad.append(f'route action at {pt} is on no route')
    for kid, pt, tag in REFUSALS:
        if kid not in ids:
            bad.append(f'refusal {kid} names no door')
    for k, pts in ROUTES.items():
        if xy(pts[-1]) != FINISH:
            bad.append(f'route {k} does not end in the lift')
    for name, pt in SECRETS:
        if not any(math.dist(xy(q), pt) < 1.6 for pts in SECRET_ROUTES.values() for q in pts):
            bad.append(f'secret {name} is not on the secrets route')
    return bad


if __name__ == '__main__':
    problems = check()
    for m in problems:
        print('PLAN PROBLEM:', m)
    for k, pts in ROUTES.items():
        L = route_length(pts)
        print(f'{k}: {L:.0f} m; walking {L / 5.0:.0f} s, sprinting {L / 8.0:.0f} s')
    print(f'FREIGHT_V2_CHECK: revision {REVISION}; {len(problems)} problems')
