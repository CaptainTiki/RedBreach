"""Generate the architecture lab source map from the revision 06 pieces.

One straight run: FLOOR + WALL + CEILING mirrored about the centreline, with a
RIB dropped in every 4 m. Plain W1 panels throughout - the swap-outs come
later. Flat neutral light; the lighting carrier is a ceiling swap-out and is
not decided yet.

Every solid here is a direct extrusion of a chain in architecture_lab_section,
so the map cannot disagree with the drawings. The resulting .map is then the
editable source; run with --overwrite to deliberately regenerate. Normal
rebuilds never run this.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import architecture_lab_section as S

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'RedBreach/maps/architecture_lab_01.map'
if MAP.exists() and '--overwrite' not in sys.argv:
    raise SystemExit('Map already exists. Edit it in TrenchBroom, or pass --overwrite to regenerate.')

S.check()

# --- the run ---------------------------------------------------------------
RIB_Z = [2, -2, -6, -10, -14, -18, -22]          # 4 m pitch, six bays between
Z_SOUTH = RIB_Z[0] + S.RIB_DEPTH / 2             # sealed ends sit on the end ribs
Z_NORTH = RIB_Z[-1] - S.RIB_DEPTH / 2

CHARCOAL = 'greybox/GreyCharcoal/texture_01'
PALE     = 'greybox/GreyPale/texture_01'
MEDIUM   = 'greybox/GreyMedium/texture_01'
FLOOR    = 'greybox/Dark/texture_06'
EMISSIVE = 'greybox/Emissive/texture_01'

brushes = []
counts = {}


def sub(a, b): return tuple(p - q for p, q in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def dot(a, b): return sum(p*q for p, q in zip(a, b))


def prism(poly, z0, z1, texture, name, tally):
    """Convex cross-section polygon extruded along Z. Godot metres in, Valve
    220 brush out. Map axes are (godot Z, godot X, godot Y)."""
    clean = []
    for p in poly:
        if not clean or max(abs(p[0]-clean[-1][0]), abs(p[1]-clean[-1][1])) > 1e-9:
            clean.append(p)
    if len(clean) > 1 and max(abs(clean[0][0]-clean[-1][0]), abs(clean[0][1]-clean[-1][1])) < 1e-9:
        clean.pop()
    if len(clean) < 3 or abs(z1 - z0) < 1e-9:
        return
    n = len(clean)
    pts = [(z0*32, x*32, y*32) for x, y in clean] + [(z1*32, x*32, y*32) for x, y in clean]
    faces = [list(range(n)), list(range(n, 2*n))[::-1]]
    for i in range(n):
        faces.append([i, (i+1) % n, (i+1) % n + n, i + n])
    center = tuple(sum(p[i] for p in pts)/len(pts) for i in range(3))
    lines = ['// ' + name, '{']
    for face in faces:
        a, b, c = (pts[i] for i in face[:3])
        nrm = cross(sub(b, a), sub(c, a))
        if dot(nrm, sub(a, center)) > 0:
            b, c = c, b
            nrm = cross(sub(b, a), sub(c, a))
        axis = max(range(3), key=lambda i: abs(nrm[i]))
        uv = ['[ 0 1 0 0 ] [ 0 0 -1 0 ]',
              '[ 1 0 0 0 ] [ 0 0 -1 0 ]',
              '[ 1 0 0 0 ] [ 0 -1 0 0 ]'][axis]
        tex = texture if axis == 2 else (
            'greybox/Dark/texture_01' if texture == FLOOR else texture)
        lines.append(' '.join('( ' + ' '.join(f'{v:g}' for v in p) + ' )' for p in (a, b, c))
                     + f' {tex} {uv} 0 0.03125 0.03125')
    lines.append('}')
    brushes.append('\n'.join(lines))
    counts[tally] = counts.get(tally, 0) + 1


def edge(chain, y0, y1):
    """Interior |x| of the chain segment spanning this band, at y0 and y1.
    Both chains are monotone in y, so exactly one segment covers each band."""
    ym = (y0 + y1) / 2
    for (x0, a), (x1, b) in zip(chain, chain[1:]):
        if abs(b - a) < 1e-9:
            continue
        if min(a, b) - 1e-9 <= ym <= max(a, b) + 1e-9:
            return (abs(x0 + (y0 - a)/(b - a)*(x1 - x0)),
                    abs(x0 + (y1 - a)/(b - a)*(x1 - x0)))
    return None


# Materials split by ELEMENT, not by height register. The rib is one texture
# zone from its toe to its beam; the bay is another, and the bay means the
# whole bay - wall at every height plus the ceiling between the beams, not
# just the panel. That is how a texture set would actually be authored, and
# splitting by register instead made the wall read as three unrelated bands.
# Polarity: the structure is the LIGHTER zone and the bay falls away behind
# it, which is what the references do and what lighting will reinforce - the
# frames catch the light, the recesses go dark. It also shrinks the jump down
# to the dark floor from 98 brightness points to 44.
RIB_TEX = PALE       # GreyPale, 151/255
BAY_TEX = MEDIUM     # GreyMedium, 97/255


def box(x0, x1, y0, y1, z0, z1, texture, name, tally):
    prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, texture, name, tally)


O = S.SHELL_BACK
# --- FLOOR: the walking plate, one continuous piece -------------------------
box(-S.FLOOR_HALF, S.FLOOR_HALF, S.SUBFLOOR_Y, 0, Z_NORTH, Z_SOUTH, FLOOR, 'floor plate', 'floor')
for side in (-1, 1):
    box(side*S.FLOOR_HALF, side*O, S.SUBFLOOR_Y, 0, Z_NORTH, Z_SOUTH, CHARCOAL, 'wall footing', 'floor')

# --- WALL: one solid per facet, running the whole length --------------------
wall_bands = S.bands(S.WALL, S.WALL[0][1], S.WALL[-1][1])
for y0, y1 in wall_bands:
    e = edge(S.WALL, y0, y1)
    for side in (-1, 1):
        prism([(side*O, y0), (side*e[0], y0), (side*e[1], y1), (side*O, y1)],
              Z_NORTH, Z_SOUTH, BAY_TEX, f'wall facet {y0:g}-{y1:g}', 'wall')

# --- CEILING: half soffit each side, capping the wall -----------------------
box(-O, O, S.CEIL_Y, S.CEILING_TOP, Z_NORTH, Z_SOUTH, BAY_TEX, 'ceiling slab', 'ceiling')

# --- RIB: dropped in, changing none of the three ----------------------------
rib_cuts = sorted({y for _, y in S.WALL if 0 < y < S.RIB_SOFFIT_Y})
rib_bands = S.bands(S.RIB, 0, S.RIB_SOFFIT_Y, rib_cuts)
beam_bands = S.bands(S.WALL, S.RIB_SOFFIT_Y, S.CEIL_Y)
for rz in RIB_Z:
    z0, z1 = rz - S.RIB_DEPTH/2, rz + S.RIB_DEPTH/2
    for y0, y1 in rib_bands:
        w, r = edge(S.WALL, y0, y1), edge(S.RIB, y0, y1)
        if w is None or r is None:
            continue
        for side in (-1, 1):
            prism([(side*w[0], y0), (side*r[0], y0), (side*r[1], y1), (side*w[1], y1)],
                  z0, z1, RIB_TEX, f'rib {rz:g} shaft {y0:g}-{y1:g}', 'rib')
    for y0, y1 in beam_bands:
        w = edge(S.WALL, y0, y1)
        if w is None:
            continue
        prism([(-w[0], y0), (w[0], y0), (w[1], y1), (-w[1], y1)],
              z0, z1, RIB_TEX, f'rib {rz:g} beam {y0:g}-{y1:g}', 'rib')

# --- LIGHT STRIPS -----------------------------------------------------------
# The beams hang at 3.50 and the ceiling soffit is at 3.75, so every bay
# already has a 0.25 m coffer. Nothing is cut: the strip sits 0.125 m up
# inside that existing recess, which hides it from a shallow view down the
# corridor and shows it only as you come under it.
#
# Two per bay, near the coffer edges rather than down the middle, so the wash
# rakes the wall and the chamfers have something to catch. EVERY bay gets a
# strip; the tier in S.BAY_LIGHTS decides how hard it burns, so a dead or
# flickering bay later is a word change, not a geometry change.
for bz, tier in S.BAY_LIGHTS.items():
    spec = S.LIGHT_TIERS[tier]
    for side in (-1, 1):
        x0, x1 = side * S.STRIP_X, side * (S.STRIP_X + 0.125)
        box(min(x0, x1), max(x0, x1), S.CEIL_Y - S.STRIP_INSET, S.CEIL_Y,
            bz - S.STRIP_LEN/2, bz + S.STRIP_LEN/2, spec['tex'],
            f'light strip {bz:g} {tier}', 'lights')

# --- sealed ends ------------------------------------------------------------
box(-O, O, S.SUBFLOOR_Y, S.CEILING_TOP, Z_SOUTH, Z_SOUTH + 0.25, MEDIUM, 'south bulkhead', 'ends')
box(-O, O, S.SUBFLOOR_Y, S.CEILING_TOP, Z_NORTH - 0.25, Z_NORTH, MEDIUM, 'north bulkhead', 'ends')

header = ('// Game: Red Breach\n'
          '// Format: Valve\n'
          '{\n'
          '"classname" "worldspawn"\n'
          '"_tb_def" "builtin:FuncGodot.fgd"\n'
          '"_tb_textures" "greybox/Dark;greybox/GreyCharcoal;greybox/GreyMedium;greybox/GreyPale"\n')
MAP.parent.mkdir(parents=True, exist_ok=True)
MAP.write_text(header + '\n'.join(brushes) + '\n}\n', encoding='utf-8')

run = Z_SOUTH - Z_NORTH
print(f'ARCH_LAB_BOOTSTRAP: {len(brushes)} brushes for a {run:g} m run, {len(RIB_Z)} ribs at {S.RIB_PITCH:g} m')
for k in ('floor', 'wall', 'ceiling', 'rib', 'lights', 'ends'):
    print(f'  {k:<9}{counts.get(k, 0):>4}')
print('  bay tiers: ' + ', '.join(f'{k:g}:{v}' for k, v in S.BAY_LIGHTS.items()))
print(f'  spawn faces north from (0, 0.05, {RIB_Z[0] - 1.0:g})')
print(f'  wrote {MAP.relative_to(ROOT)}')
