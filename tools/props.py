"""The prop catalogue: the single source of truth for Red Breach's placeable props.

User direction (2026-09-27): props are placed in GODOT, after a level's architecture is solid, not in TrenchBroom.
Each prop is a model built in Blender and a Godot scene wrapping it. A light prop carries its own light, editable in
the inspector. Hanging fittings have wires that can run up through the ceiling into the void above the room.

Pipeline (tools/rebuild-props.ps1):
  1. tools/build-props-blender.py, run by Blender, builds each prop here into art/props/<name>.blend (the editable
     source, outside the Godot project) and exports RedBreach/props/<category>/<name>.glb.
  2. tools/write-props.py writes the Godot side: the .glb import settings that map each material to the level's own
     look materials, the prop scenes (.tscn), the special materials and the props gallery.
  3. Godot imports, and RedBreach/tools/validate_props.gd checks every prop.

A prop listed in HAND is hand-edited in Blender: the build exports its .blend and never regenerates it.

Coordinates are Godot's, in metres: x right, y up, +z the prop's FRONT (the way it faces). Origins:
  ceiling fittings  the top of the fitting (flush against the ceiling when the wire length is 0)
  wall props        the back, at floor level (lockers, shelves) or at the mounting point (sconces)
  floor props       the floor, under the centre
  desk-top props    the desk's surface, under the centre

Materials name a look and a role ('steel/frame'), exactly as map faces do, so a prop uses the level's own materials
at the level's texel density (32 px per metre; frames and ribs at 64). 'prop/...' materials are the props' own
(written by tools/write-props.py): the lens of a light fitting is 'prop/lens', and the light prop's script makes it
glow in the light's colour, or go dark when the light is off (a dead fitting never glows).
"""
from pathlib import Path
import json
import math
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style_lab as S

ROOT = Path(__file__).resolve().parents[1]
PROJ = ROOT / 'RedBreach'
TEXTURES = PROJ / 'textures'

# Props hand-edited in Blender: the build exports art/props/<name>.blend and never regenerates it.
HAND = set()

# The props' own materials: (albedo rgb, roughness, metallic, emission rgb or None).
PROP_MATERIALS = {
    'lens': ((0.95, 0.95, 0.92), 0.4, 0.0, (1.0, 1.0, 1.0)),     # a fitting's lens: glows in its light's colour
    'lens_dead': ((0.13, 0.13, 0.14), 0.6, 0.0, None),          # the same lens with the light off
    'wire': ((0.04, 0.04, 0.045), 0.9, 0.0, None),               # cables and chains
    'rubber': ((0.07, 0.07, 0.08), 0.95, 0.0, None),             # castors, grips, pads
    'fabric': ((0.16, 0.18, 0.22), 1.0, 0.0, None),              # seat cushions
    'button_red': ((0.75, 0.08, 0.05), 0.5, 0.0, (0.6, 0.05, 0.03)),
    'button_green': ((0.1, 0.6, 0.25), 0.5, 0.0, (0.05, 0.5, 0.2)),
}
FIT = S.FIT_ROLES            # roles fitted whole to each face (door, screen, service, grate, container)


# --- parts --------------------------------------------------------------------------------------------------------
def B(mat, size, pos, rot=(0, 0, 0), node='Body'):
    """A box: size (x, y, z), centred at pos, rotated by rot (degrees about x, then y, then z)."""
    return dict(kind='box', mat=mat, size=size, pos=pos, rot=rot, node=node)


def C(mat, r0, r1, h, pos, rot=(0, 0, 0), sides=8, node='Body'):
    """A cylinder or frustum along y: radius r0 at the bottom, r1 at the top, height h, centred at pos."""
    return dict(kind='cyl', mat=mat, r0=r0, r1=r1, h=h, pos=pos, rot=rot, sides=sides, node=node)


def BAR(mat, a, b, w, node='Body'):
    """A square bar of width w from point a to point b (a strut, an arm, a brace)."""
    d = [b[i] - a[i] for i in range(3)]
    L = math.sqrt(sum(v * v for v in d))
    # Rotate the box's y axis onto d: about x first (by asin of d's z share), then about z.
    rx = math.degrees(math.asin(max(-1.0, min(1.0, d[2] / L))))
    rz = math.degrees(math.atan2(-d[0], d[1]))
    mid = tuple((a[i] + b[i]) / 2 for i in range(3))
    return dict(kind='box', mat=mat, size=(w, L, w), pos=mid, rot=(rx, 0, rz), node=node)


def WIRES(points, r=0.007):
    """Hanging wires: one per plan point (x, z) at the fitting's top, each a unit length going straight up. The light
    prop scales the Wires node to the wire length set in the inspector."""
    return [C('prop/wire', r, r, 1.0, (x, 0.5, z), sides=6, node='Wires') for x, z in points]


# --- the catalogue ------------------------------------------------------------------------------------------------
# light: the light node(s) the prop scene carries. type omni/spot; pos; rot (degrees; a spot shines along its -z);
# energy, range, color, shadow; angle for a spot. glow: an optional dim omni beside it. spin: the light sits on a
# pivot that turns (a rotating beacon). wire: the default wire length (0 = flush).
PROPS = {}

# A twin-tube fluorescent batten with a wire guard: corridors, workshops, offices.
PROPS['light_fluorescent'] = dict(
    category='lights', title='Fluorescent batten (twin tube)', mount='ceiling',
    parts=[
        B('steel/machine_body', (1.3, 0.09, 0.22), (0, -0.045, 0)),
        B('steel/frame', (0.05, 0.12, 0.25), (-0.64, -0.06, 0)), B('steel/frame', (0.05, 0.12, 0.25), (0.64, -0.06, 0)),
        C('prop/lens', 0.026, 0.026, 1.2, (0, -0.12, -0.05), rot=(0, 0, 90)),
        C('prop/lens', 0.026, 0.026, 1.2, (0, -0.12, 0.05), rot=(0, 0, 90)),
        B('steel/frame', (1.22, 0.014, 0.014), (0, -0.165, -0.095)), B('steel/frame', (1.22, 0.014, 0.014), (0, -0.165, 0.095)),
    ] + [B('steel/frame', (0.016, 0.016, 0.21), (x, -0.172, 0)) for x in (-0.4, 0.0, 0.4)] + WIRES([(-0.5, 0), (0.5, 0)]),
    light=dict(type='omni', pos=(0, -0.35, 0), energy=1.4, range=8.0, color=(0.86, 0.93, 1.0), shadow=True),
    wire=0.0)

# A high-bay halogen: a driver box, a reflector bell and a lens, hung on one wire. Tall halls, the bay, the dock.
PROPS['light_halogen'] = dict(
    category='lights', title='Halogen high-bay', mount='ceiling',
    parts=[
        B('steel/machine_body', (0.28, 0.16, 0.28), (0, -0.08, 0)),
        C('steel/frame', 0.06, 0.06, 0.08, (0, -0.2, 0)),
        C('steel/machine_top', 0.36, 0.16, 0.34, (0, -0.41, 0)),
        C('prop/lens', 0.33, 0.33, 0.02, (0, -0.59, 0)),
    ] + WIRES([(0, 0)], r=0.012),
    light=dict(type='spot', pos=(0, -0.66, 0), rot=(-90, 0, 0), energy=4.0, range=14.0, angle=55.0,
               color=(1.0, 0.86, 0.68), shadow=True),
    wire=1.0)

# A caged bulkhead light on a wall: stairwells, service corridors, machine rooms.
PROPS['light_sconce'] = dict(
    category='lights', title='Wall sconce (caged bulkhead)', mount='wall',
    parts=[
        B('steel/machine_body', (0.26, 0.34, 0.04), (0, 0, 0.02)),
        B('prop/lens', (0.18, 0.24, 0.07), (0, 0, 0.075)),
        B('steel/frame', (0.22, 0.02, 0.1), (0, 0.13, 0.07)), B('steel/frame', (0.22, 0.02, 0.1), (0, -0.13, 0.07)),
        B('steel/frame', (0.016, 0.26, 0.016), (-0.05, 0, 0.118)), B('steel/frame', (0.016, 0.26, 0.016), (0.05, 0, 0.118)),
        B('steel/frame', (0.2, 0.016, 0.016), (0, 0, 0.12)),
    ],
    light=dict(type='omni', pos=(0, 0, 0.35), energy=1.0, range=6.0, color=(1.0, 0.82, 0.6), shadow=True))

# An angled desk lamp: offices, the booth, dispatch.
PROPS['light_desk'] = dict(
    category='lights', title='Desk lamp', mount='desk',
    parts=[
        C('steel/machine_body', 0.1, 0.09, 0.03, (0, 0.015, 0)),
        BAR('steel/frame', (0, 0.03, 0.0), (0, 0.37, -0.09), 0.024),
        C('steel/machine_top', 0.022, 0.022, 0.045, (0, 0.37, -0.09), rot=(0, 0, 90)),
        BAR('steel/frame', (0, 0.37, -0.09), (0, 0.44, 0.19), 0.022),
        C('steel/machine_top', 0.07, 0.035, 0.1, (0, 0.41, 0.21)),
        C('prop/lens', 0.062, 0.062, 0.01, (0, 0.357, 0.21)),
    ],
    light=dict(type='spot', pos=(0, 0.34, 0.21), rot=(-90, 0, 0), energy=2.0, range=3.0, angle=45.0,
               color=(1.0, 0.84, 0.62), shadow=True))

# A floor uplight against the foot of a wall, washing the wall above it: corridors, walkway edges.
PROPS['light_floor'] = dict(
    category='lights', title='Floor uplight', mount='floor',
    parts=[
        B('steel/machine_body', (0.4, 0.14, 0.16), (0, 0.07, 0.08)),
        B('prop/lens', (0.34, 0.01, 0.1), (0, 0.143, 0.085)),
    ] + [B('steel/frame', (0.014, 0.014, 0.13), (x, 0.152, 0.085)) for x in (-0.11, 0.0, 0.11)],
    light=dict(type='spot', pos=(0, 0.2, 0.1), rot=(75, 0, 0), energy=1.5, range=5.0, angle=35.0,
               color=(0.86, 0.93, 1.0), shadow=True))

# A caged emergency beacon: a red dome with a turning beam. On a ceiling turn it over; on a wall, tip it forward.
PROPS['light_emergency'] = dict(
    category='lights', title='Emergency beacon', mount='any',
    parts=[
        C('steel/machine_body', 0.1, 0.1, 0.06, (0, 0.03, 0)),
        C('prop/lens', 0.085, 0.06, 0.12, (0, 0.12, 0)),
    ] + [B('steel/frame', (0.014, 0.13, 0.014), (x, 0.125, z)) for x, z in ((0.095, 0), (-0.095, 0), (0, 0.095), (0, -0.095))]
      + [B('steel/frame', (0.2, 0.014, 0.014), (0, 0.19, 0)), B('steel/frame', (0.014, 0.014, 0.2), (0, 0.19, 0))],
    light=dict(type='spot', pos=(0, 0.12, 0), rot=(0, 0, 0), energy=3.0, range=10.0, angle=25.0,
               color=(1.0, 0.16, 0.08), shadow=False),
    glow=dict(pos=(0, 0.22, 0), ratio=0.15, range=3.0),
    spin=dict(pos=(0, 0.12, 0), speed=3.5))

# The same beacon upright on a wall bracket, so its beam sweeps the room (origin: the mounting point on the wall).
_bk = (0.0, 0.0, 0.17)
PROPS['light_emergency_wall'] = dict(
    category='lights', title='Emergency beacon on a wall bracket', mount='wall',
    parts=[B('steel/frame', (0.14, 0.22, 0.02), (0, -0.07, 0.01)), B('steel/frame', (0.09, 0.03, 0.2), (0, -0.015, 0.1)),
           BAR('steel/frame', (0, -0.16, 0.02), (0, -0.03, 0.15), 0.02)]
      + [dict(part, pos=tuple(part['pos'][i] + _bk[i] for i in range(3))) for part in PROPS['light_emergency']['parts']],
    light=dict(PROPS['light_emergency']['light'], pos=(0, 0.12, 0.17)),
    glow=dict(PROPS['light_emergency']['glow'], pos=(0, 0.22, 0.17)),
    spin=dict(PROPS['light_emergency']['spin'], pos=(0, 0.12, 0.17)))

# --- furniture ----------------------------------------------------------------------------------------------------
# A swivel office chair. Its front is where the sitter faces.
_legs = []
for k in range(5):
    a = math.radians(90 + k * 72)
    _legs.append(BAR('steel/frame', (0, 0.07, 0), (0.28 * math.cos(a), 0.05, 0.28 * math.sin(a)), 0.045))
    _legs.append(B('prop/rubber', (0.05, 0.05, 0.05), (0.3 * math.cos(a), 0.025, 0.3 * math.sin(a))))
PROPS['chair_office'] = dict(
    category='furniture', title='Office chair', mount='floor',
    parts=_legs + [
        C('steel/machine_top', 0.03, 0.03, 0.34, (0, 0.24, 0)),
        B('steel/machine_body', (0.4, 0.03, 0.4), (0, 0.415, 0)),
        B('prop/fabric', (0.48, 0.08, 0.46), (0, 0.47, 0.01)),
        B('steel/frame', (0.05, 0.34, 0.04), (0, 0.6, -0.25)),
        B('prop/fabric', (0.44, 0.5, 0.07), (0, 0.8, -0.24), rot=(-8, 0, 0)),
        B('steel/frame', (0.04, 0.18, 0.04), (-0.26, 0.58, 0.0)), B('steel/frame', (0.04, 0.18, 0.04), (0.26, 0.58, 0.0)),
        B('prop/rubber', (0.06, 0.03, 0.26), (-0.26, 0.685, 0.02)), B('prop/rubber', (0.06, 0.03, 0.26), (0.26, 0.685, 0.02)),
    ],
    collision=[('box', (0.64, 1.08, 0.64), (0, 0.54, 0))])

# An office desk with a drawer pedestal. Its front is the sitter's side.
PROPS['desk_office'] = dict(
    category='furniture', title='Office desk', mount='floor',
    parts=[
        B('warm/machine_top', (1.6, 0.04, 0.8), (0, 0.74, 0)),
        B('warm/machine_body', (0.42, 0.7, 0.72), (0.56, 0.35, 0)),
        B('steel/frame', (0.05, 0.72, 0.72), (-0.76, 0.36, 0)),
        B('warm/machine_body', (1.08, 0.45, 0.02), (-0.2, 0.46, -0.37)),
    ] + [B('steel/frame', (0.38, 0.2, 0.02), (0.56, y, 0.37)) for y in (0.6, 0.37, 0.14)]
      + [B('steel/machine_top', (0.14, 0.02, 0.025), (0.56, y + 0.06, 0.39)) for y in (0.6, 0.37, 0.14)],
    collision=[('box', (1.6, 0.76, 0.8), (0, 0.38, 0))])

# A terminal: a monitor on a stand and a keyboard. Stands on a desk; its front is the user's side.
PROPS['terminal'] = dict(
    category='furniture', title='Terminal (monitor and keyboard)', mount='desk',
    parts=[
        B('steel/machine_body', (0.2, 0.02, 0.16), (0, 0.01, -0.12)),
        B('steel/frame', (0.04, 0.2, 0.03), (0, 0.12, -0.14)),
        B('steel/machine_body', (0.5, 0.34, 0.06), (0, 0.34, -0.12)),
        B('steel/screen', (0.44, 0.28, 0.01), (0, 0.34, -0.086)),
        B('steel/machine_top', (0.44, 0.025, 0.15), (0, 0.0125, 0.14)),
    ])

# A bank of three lockers against a wall.
PROPS['locker_bank'] = dict(
    category='furniture', title='Locker bank (three)', mount='wall',
    parts=[
        B('steel/frame', (1.2, 0.08, 0.46), (0, 0.04, 0.25)),
        B('steel/machine_body', (1.2, 1.92, 0.5), (0, 1.04, 0.25)),
    ] + [B('steel/service', (0.37, 1.78, 0.02), (x, 1.03, 0.51)) for x in (-0.4, 0.0, 0.4)]
      + [B('steel/machine_top', (0.03, 0.14, 0.03), (x + 0.13, 1.1, 0.535)) for x in (-0.4, 0.0, 0.4)],
    collision=[('box', (1.2, 2.0, 0.54), (0, 1.0, 0.27))])

# A four-drawer filing cabinet against a wall.
PROPS['filing_cabinet'] = dict(
    category='furniture', title='Filing cabinet', mount='wall',
    parts=[B('warm/machine_body', (0.48, 1.32, 0.62), (0, 0.66, 0.31))]
      + [B('steel/frame', (0.44, 0.28, 0.02), (0, y, 0.63)) for y in (0.2, 0.52, 0.84, 1.16)]
      + [B('steel/machine_top', (0.16, 0.03, 0.03), (0, y + 0.07, 0.655)) for y in (0.2, 0.52, 0.84, 1.16)],
    collision=[('box', (0.48, 1.32, 0.66), (0, 0.66, 0.33))])

# Industrial shelving against a wall, braced across its back.
PROPS['shelf_rack'] = dict(
    category='furniture', title='Shelf rack', mount='wall',
    parts=[B('steel/frame', (0.05, 2.0, 0.05), (x, 1.0, z)) for x in (-0.87, 0.87) for z in (0.03, 0.47)]
      + [B('steel/machine_top', (1.8, 0.03, 0.5), (0, y, 0.25)) for y in (0.1, 0.7, 1.3, 1.9)]
      + [BAR('steel/frame', (-0.84, 0.12, 0.012), (0.84, 1.88, 0.012), 0.02), BAR('steel/frame', (0.84, 0.12, 0.012), (-0.84, 1.88, 0.012), 0.02)],
    collision=[('box', (1.8, 2.0, 0.5), (0, 1.0, 0.25))])

# A metal crate with corrugated sides and framed edges.
_e = 0.9 / 2
PROPS['crate'] = dict(
    category='furniture', title='Crate', mount='floor',
    parts=[B('warm/container', (0.9, 0.9, 0.9), (0, 0.45, 0))]
      + [B('steel/frame', (0.07, 0.97, 0.07), (sx * _e, 0.45, sz * _e)) for sx in (-1, 1) for sz in (-1, 1)]
      + [B('steel/frame', (0.97, 0.07, 0.07), (0, y, sz * _e)) for y in (0.0, 0.9) for sz in (-1, 1)]
      + [B('steel/frame', (0.07, 0.07, 0.83), (sx * _e, y, 0)) for y in (0.0, 0.9) for sx in (-1, 1)],
    collision=[('box', (0.97, 0.97, 0.97), (0, 0.45, 0))])

# A 200-litre drum.
PROPS['drum'] = dict(
    category='furniture', title='Drum', mount='floor',
    parts=[C('warm/machine_body', 0.29, 0.29, 0.88, (0, 0.44, 0), sides=12)]
      + [C('steel/frame', 0.302, 0.302, 0.03, (0, y, 0), sides=12) for y in (0.03, 0.3, 0.58, 0.85)]
      + [C('steel/machine_top', 0.03, 0.03, 0.02, (0.15, 0.89, 0))],
    collision=[('cyl', 0.3, 0.9, (0, 0.45, 0))])

# A pallet: deck boards on three stringers, with bottom boards.
PROPS['pallet'] = dict(
    category='furniture', title='Pallet', mount='floor',
    parts=[B('warm/rib', (1.2, 0.02, 0.14), (0, 0.13, z)) for z in (-0.43, -0.215, 0.0, 0.215, 0.43)]
      + [B('warm/rib', (0.1, 0.1, 1.0), (x, 0.07, 0)) for x in (-0.55, 0.0, 0.55)]
      + [B('warm/rib', (1.2, 0.02, 0.14), (0, 0.01, z)) for z in (-0.43, 0.0, 0.43)],
    collision=[('box', (1.2, 0.14, 1.0), (0, 0.07, 0))])

# The operator's seat with a joystick in its right arm (the sorting booth: nothing is labelled, props tell the story).
PROPS['seat_joystick'] = dict(
    category='furniture', title='Operator seat with joystick', mount='floor',
    parts=[
        B('steel/frame', (0.4, 0.03, 0.4), (0, 0.015, 0)),
        C('steel/machine_top', 0.06, 0.06, 0.4, (0, 0.2, 0)),
        B('prop/fabric', (0.5, 0.1, 0.48), (0, 0.45, 0)),
        B('prop/fabric', (0.5, 0.62, 0.09), (0, 0.8, -0.25), rot=(-10, 0, 0)),
        B('steel/machine_body', (0.1, 0.12, 0.42), (0.3, 0.58, 0.02)),
        B('steel/machine_body', (0.1, 0.1, 0.42), (-0.3, 0.57, 0.02)),
        C('prop/rubber', 0.02, 0.015, 0.14, (0.3, 0.71, 0.1)),
        C('prop/rubber', 0.03, 0.03, 0.04, (0.3, 0.8, 0.1)),
        B('prop/button_red', (0.03, 0.012, 0.03), (0.3, 0.646, -0.05)),
    ],
    collision=[('box', (0.72, 1.12, 0.62), (0, 0.56, 0))])

# An operator's console: a sloped desk with screens and buttons, and a raised display behind.
_n = (0.0, math.cos(math.radians(20)), math.sin(math.radians(20)))
PROPS['console_operator'] = dict(
    category='furniture', title='Operator console', mount='floor',
    parts=[
        B('steel/machine_body', (1.0, 0.76, 0.5), (0, 0.38, 0)),
        B('steel/machine_top', (1.0, 0.04, 0.54), (0, 0.8, 0.02), rot=(20, 0, 0)),
        B('steel/machine_body', (1.0, 0.44, 0.08), (0, 1.02, -0.21)),
        B('steel/screen', (0.8, 0.3, 0.01), (0, 1.03, -0.166)),
    ] + [B('steel/screen', (0.3, 0.012, 0.22), (x, 0.8 + _n[1] * 0.024, 0.02 + _n[2] * 0.024 - 0.04), rot=(20, 0, 0)) for x in (-0.26, 0.26)]
      + [B(m, (0.04, 0.012, 0.04), (x, 0.8 + _n[1] * 0.024 - 0.05 * _n[2], 0.02 + _n[2] * 0.024 + 0.16), rot=(20, 0, 0))
         for x, m in ((-0.06, 'prop/button_green'), (0.0, 'prop/button_red'), (0.06, 'prop/button_green'))],
    collision=[('box', (1.0, 1.25, 0.5), (0, 0.625, 0))])

# --- the gallery room (not a prop): a showroom to judge the props in --------------------------------------------
GALLERY = dict(size=(24.0, 4.5, 16.0), wall=0.3, spawn=(0.0, 0.05, 6.5))
PROPS['gallery_room'] = dict(
    category='gallery', title='Props gallery room', mount='floor',
    parts=[
        B('steel/floor', (24.6, 0.25, 16.6), (0, -0.125, 0)),
        B('steel/ceiling', (24.6, 0.3, 16.6), (0, 4.65, 0)),
        B('concrete/wall', (24.6, 4.5, 0.3), (0, 2.25, -8.15)), B('concrete/wall', (24.6, 4.5, 0.3), (0, 2.25, 8.15)),
        B('concrete/wall', (0.3, 4.5, 16.0), (-12.15, 2.25, 0)), B('concrete/wall', (0.3, 4.5, 16.0), (12.15, 2.25, 0)),
    ],
    collision=[('box', (24.6, 0.25, 16.6), (0, -0.125, 0)), ('box', (24.6, 0.3, 16.6), (0, 4.65, 0)),
               ('box', (24.6, 4.5, 0.3), (0, 2.25, -8.15)), ('box', (24.6, 4.5, 0.3), (0, 2.25, 8.15)),
               ('box', (0.3, 4.5, 16.0), (-12.15, 2.25, 0)), ('box', (0.3, 4.5, 16.0), (12.15, 2.25, 0))])

# The gallery's arrangement: (prop, position, rotation degrees (x, y, z), property overrides).
GALLERY_PLACEMENTS = [
    # Ceiling fittings: flush, hanging, dead, flickering.
    ('light_fluorescent', (-9.0, 4.5, -3.0), (0, 0, 0), {}),
    ('light_fluorescent', (-5.5, 3.2, -3.0), (0, 0, 0), {'wire': 1.8}),
    ('light_fluorescent', (-9.0, 4.5, 2.0), (0, 0, 0), {'lit': False}),
    ('light_fluorescent', (-5.5, 3.4, 2.0), (0, 0, 0), {'wire': 1.6, 'flicker': True}),
    ('light_halogen', (-1.0, 3.2, -3.0), (0, 0, 0), {'wire': 1.8}),
    ('light_halogen', (3.0, 4.5, -3.0), (0, 0, 0), {'wire': 0.0}),
    ('light_emergency', (7.0, 4.5, -3.0), (180, 0, 0), {}),
    # The back wall: sconces, an emergency beacon and floor uplights.
    ('light_sconce', (-8.0, 2.3, -8.0), (0, 0, 0), {}),
    ('light_sconce', (-3.0, 2.3, -8.0), (0, 0, 0), {'lit': False}),
    ('light_emergency_wall', (2.0, 2.6, -8.0), (0, 0, 0), {}),
    ('light_floor', (5.0, 0.0, -8.0), (0, 0, 0), {}),
    ('light_floor', (7.0, 0.0, -8.0), (0, 0, 0), {}),
    ('light_floor', (9.0, 0.0, -8.0), (0, 0, 0), {}),
    # The room's own lighting: flush battens on a grid, as a real room would have.
    ('light_fluorescent', (-2.0, 4.5, 6.0), (0, 0, 0), {'energy': 1.0}),
    ('light_fluorescent', (4.0, 4.5, 6.0), (0, 0, 0), {'energy': 1.0}),
    ('light_fluorescent', (10.0, 4.5, 6.0), (0, 0, 0), {'energy': 1.0}),
    ('light_fluorescent', (10.0, 4.5, 0.0), (0, 90, 0), {'energy': 1.0}),
    # Fittings over the furniture, as they would be used.
    ('light_fluorescent', (-7.0, 3.1, 4.6), (0, 0, 0), {'wire': 1.4}),
    ('light_sconce', (-12.0, 2.3, 2.2), (0, 90, 0), {}),
    ('light_halogen', (5.5, 3.3, 3.3), (0, 0, 0), {'wire': 1.2, 'energy': 3.0}),
    ('light_fluorescent', (0.0, 3.2, 2.7), (0, 90, 0), {'wire': 1.3}),
    ('light_halogen', (8.0, 3.4, -6.4), (0, 0, 0), {'wire': 1.1, 'energy': 2.5}),
    # An office corner.
    ('desk_office', (-7.0, 0.0, 5.0), (0, 180, 0), {}),
    ('chair_office', (-7.0, 0.0, 4.25), (0, 0, 0), {}),
    ('terminal', (-7.2, 0.76, 5.1), (0, 180, 0), {}),
    ('light_desk', (-6.4, 0.76, 5.15), (0, 200, 0), {}),
    ('locker_bank', (-12.0, 0.0, 1.0), (0, 90, 0), {}),
    ('filing_cabinet', (-12.0, 0.0, 3.0), (0, 90, 0), {}),
    ('filing_cabinet', (-12.0, 0.0, 3.5), (0, 90, 0), {}),
    # Storage.
    ('shelf_rack', (8.0, 0.0, -8.0), (0, 0, 0), {}),
    ('crate', (8.0, 0.1, -7.5), (0, 0, 0), {}),
    ('pallet', (4.0, 0.0, 3.0), (0, 20, 0), {}),
    ('drum', (3.7, 0.14, 2.8), (0, 0, 0), {}),
    ('drum', (4.35, 0.14, 3.1), (0, 0, 0), {}),
    ('crate', (7.0, 0.0, 4.0), (0, 15, 0), {}),
    ('crate', (7.05, 0.9, 4.0), (0, 25, 0), {}),
    # The operator's booth.
    ('console_operator', (0.0, 0.0, 2.3), (0, 0, 0), {}),
    ('seat_joystick', (0.0, 0.0, 3.1), (0, 180, 0), {}),
]
# Views for the capture sheet: (label, eye, look-at).
GALLERY_VIEWS = [
    ('the gallery', (0.0, 1.7, 7.5), (0.0, 1.8, -3.0)),
    ('fluorescents: flush, hanging, dead, flickering', (-7.2, 1.6, -0.5), (-7.2, 3.6, -1.0)),
    ('halogens: hanging and flush', (1.0, 1.7, 0.5), (1.0, 3.4, -3.0)),
    ('beacon on the ceiling', (6.0, 2.6, -1.0), (7.0, 4.3, -3.0)),
    ('the back wall: sconces, bracket beacon', (-3.0, 1.7, -4.5), (-3.0, 2.0, -8.0)),
    ('floor uplights and the shelf rack', (6.5, 1.6, -4.0), (7.0, 0.8, -8.0)),
    ('office corner', (-4.6, 1.6, 2.6), (-7.3, 0.9, 4.6)),
    ('desk, chair, terminal and desk lamp', (-7.0, 1.7, 2.9), (-7.0, 0.8, 4.8)),
    ('lockers, filing cabinets, sconce', (-9.2, 1.6, 2.2), (-12.0, 1.1, 2.2)),
    ('storage: pallet, drums, crates', (5.5, 1.7, 6.3), (5.5, 0.6, 3.2)),
    ('the operator booth', (-1.6, 1.6, 5.2), (0.0, 0.8, 2.6)),
    ('seat with joystick', (1.1, 1.4, 4.0), (0.0, 0.7, 3.0)),
]


# --- geometry -----------------------------------------------------------------------------------------------------
def _rot(p, rot):
    """Rotate a point by degrees about x, then y, then z."""
    x, y, z = p
    rx, ry, rz = (math.radians(a) for a in rot)
    c, s = math.cos(rx), math.sin(rx)
    y, z = c * y - s * z, s * y + c * z
    c, s = math.cos(ry), math.sin(ry)
    x, z = c * x + s * z, -s * x + c * z
    c, s = math.cos(rz), math.sin(rz)
    x, y = c * x - s * y, s * x + c * y
    return (x, y, z)


def part_faces(part):
    """A part's faces as lists of points (prop coordinates), wound counter-clockwise seen from outside."""
    if part['kind'] == 'box':
        hx, hy, hz = (v / 2 for v in part['size'])
        c = lambda sx, sy, sz: (sx * hx, sy * hy, sz * hz)
        faces = [[c(1, -1, -1), c(1, 1, -1), c(1, 1, 1), c(1, -1, 1)], [c(-1, -1, 1), c(-1, 1, 1), c(-1, 1, -1), c(-1, -1, -1)],
                 [c(-1, 1, -1), c(-1, 1, 1), c(1, 1, 1), c(1, 1, -1)], [c(-1, -1, 1), c(-1, -1, -1), c(1, -1, -1), c(1, -1, 1)],
                 [c(-1, -1, 1), c(1, -1, 1), c(1, 1, 1), c(-1, 1, 1)], [c(1, -1, -1), c(-1, -1, -1), c(-1, 1, -1), c(1, 1, -1)]]
    else:
        n, h = part['sides'], part['h'] / 2
        ring = lambda r, y: [(r * math.cos(2 * math.pi * k / n + math.pi / n), y, r * math.sin(2 * math.pi * k / n + math.pi / n))
                             for k in range(n)]
        lo, hi = ring(part['r0'], -h), ring(part['r1'], h)
        faces = [list(reversed(hi)), list(lo)]
        faces += [[lo[k], hi[k], hi[(k + 1) % n], lo[(k + 1) % n]] for k in range(n)]
    px, py, pz = part['pos']
    out = []
    for f in faces:
        pts = [_rot(p, part['rot']) for p in f]
        out.append([(x + px, y + py, z + pz) for x, y, z in pts])
    centre = part['pos']
    for i, f in enumerate(out):                       # outward winding: flip any face whose normal points inward
        n_ = newell(f)
        fc = [sum(p[k] for p in f) / len(f) for k in range(3)]
        if sum(n_[k] * (fc[k] - centre[k]) for k in range(3)) < 0:
            out[i] = list(reversed(f))
    return out


def newell(pts):
    n = [0.0, 0.0, 0.0]
    for i in range(len(pts)):
        (x0, y0, z0), (x1, y1, z1) = pts[i], pts[(i + 1) % len(pts)]
        n[0] += (y0 - y1) * (z0 + z1)
        n[1] += (z0 - z1) * (x0 + x1)
        n[2] += (x0 - x1) * (y0 + y1)
    L = math.sqrt(sum(v * v for v in n)) or 1.0
    return [v / L for v in n]


def png_size(path):
    with open(path, 'rb') as fh:
        head = fh.read(24)
    return struct.unpack('>II', head[16:24])


def material_image(mat):
    """(texture file, metres per repeat, tint) for a material name, or (None, 1.0, None) for a prop material."""
    look_name, role = mat.split('/')
    if look_name == 'prop':
        return None, 1.0, None
    image, tint = S.look_texture(S.LOOKS[look_name][role])
    w, _ = png_size(TEXTURES / f'{image}.png')
    return TEXTURES / f'{image}.png', w * S.role_scale(f'looks/{look_name}/{role}') / 32.0, tint


def face_uvs(pts, mat):
    """Texture coordinates for a face: a box projection in prop metres at the material's density, or fitted whole to
    the face for a 'fit' role (a door, a screen, a vent). V runs up the world on walls."""
    n = newell(pts)
    ax = max(range(3), key=lambda i: abs(n[i]))
    if ax == 1:
        uv = [(p[0], p[2] if n[1] > 0 else -p[2]) for p in pts]
    elif ax == 0:
        uv = [(-p[2] if n[0] > 0 else p[2], p[1]) for p in pts]
    else:
        uv = [(p[0] if n[2] > 0 else -p[0], p[1]) for p in pts]
    role = mat.split('/')[1]
    if role in FIT:
        us, vs = [u for u, _ in uv], [v for _, v in uv]
        du, dv = (max(us) - min(us)) or 1.0, (max(vs) - min(vs)) or 1.0
        return [((u - min(us)) / du, (v - min(vs)) / dv) for u, v in uv]
    _, metres, _ = material_image(mat)
    return [(u / metres, v / metres) for u, v in uv]


def geometry(name):
    """{node: {'faces': [(points, material, uvs)]}} for a prop, in prop coordinates."""
    nodes = {}
    for part in PROPS[name]['parts']:
        for f in part_faces(part):
            nodes.setdefault(part['node'], []).append((f, part['mat'], face_uvs(f, part['mat'])))
    return nodes


def bounds(name, node=None):
    pts = [p for nd, faces in geometry(name).items() if node in (None, nd) for f, _, _ in faces for p in f]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def materials(name):
    return sorted({part['mat'] for part in PROPS[name]['parts']})


def glb_path(name):
    return PROJ / 'props' / PROPS[name]['category'] / f'{name}.glb'


def blend_path(name):
    return ROOT / 'art/props' / f'{name}.blend'


def check():
    bad = []
    for name, p in PROPS.items():
        for mat in materials(name):
            look_name, role = mat.split('/')
            if look_name == 'prop':
                if role not in PROP_MATERIALS:
                    bad.append(f'{name}: no prop material {role}')
            elif look_name not in S.LOOKS or role not in S.LOOKS[look_name]:
                bad.append(f'{name}: no look material {mat}')
        if p['category'] == 'lights':
            if 'light' not in p:
                bad.append(f'{name}: a light prop without a light')
            if not any(part['mat'] == 'prop/lens' for part in p['parts']):
                bad.append(f'{name}: a light prop without a lens')
        if 'Wires' in geometry(name) and p.get('mount') != 'ceiling':
            bad.append(f'{name}: wires on a prop that does not hang from a ceiling')
    for prop, *_ in GALLERY_PLACEMENTS:
        if prop not in PROPS:
            bad.append(f'gallery: no prop {prop}')
    return bad


if __name__ == '__main__':
    problems = check()
    for name in PROPS:
        lo, hi = bounds(name)
        print(f'{name:18} {PROPS[name]["category"]:9} {len(PROPS[name]["parts"]):3} parts  '
              f'{hi[0] - lo[0]:.2f} x {hi[1] - lo[1]:.2f} x {hi[2] - lo[2]:.2f} m  {", ".join(materials(name))}')
    print(f'PROPS_CHECK: {len(PROPS)} props; {len(problems)} problems')
    for b in problems:
        print('  ' + b)
    sys.exit(1 if problems else 0)
