"""Generate the architecture lab CORNER map from the revision 06 pieces.

One continuous walk that answers both open questions in a single build:

    a 52 m straight   the repetition test - how long may a run be?
    V1 SQUARE         a hard 90, mitred
    V4 LEG            straight, slice, a full bay at 45, slice, straight

No rib sits at any plan bend. That was the user's call once the measurement
showed a legal chamfer can never hold a full bay: rather than crowd two ribs
into a short face, leave the bend clear and let the rib rhythm line up across
the turn instead. The wall solids simply OVERLAP at each bend, so no mitre face
is ever built - the visible edge is where the two wall planes intersect, and
that edge lands on the grid even when a mitre face would not have.

Every solid is an extrusion of a chain in architecture_lab_section, so the map
cannot disagree with the drawings. The .map is then the editable source; run
with --overwrite to deliberately regenerate. Normal rebuilds never run this.
"""
from pathlib import Path
import math, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import architecture_lab_section as S
import architecture_lab_corner as C

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'RedBreach/maps/architecture_lab_corners_01.map'
if MAP.exists() and '--overwrite' not in sys.argv:
    raise SystemExit('Map already exists. Edit it in TrenchBroom, or pass --overwrite to regenerate.')

S.check()
C.check()

CHARCOAL = 'greybox/GreyCharcoal/texture_01'
PALE     = 'greybox/GreyPale/texture_01'
MEDIUM   = 'greybox/GreyMedium/texture_01'
FLOOR    = 'greybox/Dark/texture_06'
FLOOR_SIDE = 'greybox/Dark/texture_01'
RIB_TEX, BAY_TEX = PALE, MEDIUM

brushes, counts = [], {}


def sub(a, b): return tuple(p - q for p, q in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def dot(a, b): return sum(p*q for p, q in zip(a, b))
def norm2(v):
    l = math.hypot(v[0], v[1])
    return (v[0]/l, v[1]/l)


def emit(ring_a, ring_b, texture, name, tally):
    """Brush from two matching rings of godot-metre (X, Y, Z) points.

    The rings need not be parallel - that is what lets a run be cut off on a
    mitre plane at each end - but the solid must stay convex.
    Map axes are (godot Z, godot X, godot Y), as everywhere else in this project.
    """
    n = len(ring_a)
    if n < 3:
        return
    pts = [(p[2]*32, p[0]*32, p[1]*32) for p in ring_a] + \
          [(p[2]*32, p[0]*32, p[1]*32) for p in ring_b]
    # degenerate guard: a zero-length run writes nothing rather than a bad brush
    if max(abs(a - b) for p, q in zip(ring_a, ring_b) for a, b in zip(p, q)) < 1e-9:
        return
    faces = [list(range(n)), list(range(n, 2*n))[::-1]]
    for i in range(n):
        faces.append([i, (i+1) % n, (i+1) % n + n, i + n])
    centre = tuple(sum(p[i] for p in pts)/len(pts) for i in range(3))
    lines = ['// ' + name, '{']
    for face in faces:
        # Pick three points that actually define a plane. A side quad can carry
        # a repeated vertex - the jamb fills share their outer corner between
        # both rings, so that edge has zero length - and taking face[:3] blindly
        # then yields a null normal. Skipping the face instead leaves the brush
        # unbounded, which is what 'cannot get winding basis' means downstream.
        tri = None
        for i in range(len(face)):
            a, b, c = (pts[face[(i+k) % len(face)]] for k in range(3))
            if max(abs(v) for v in cross(sub(b, a), sub(c, a))) > 1e-9:
                tri = (a, b, c)
                break
        if tri is None:
            continue                       # genuinely degenerate face
        a, b, c = tri
        nrm = cross(sub(b, a), sub(c, a))
        if dot(nrm, sub(a, centre)) > 0:
            b, c = c, b
            nrm = cross(sub(b, a), sub(c, a))
        # nrm is in MAP space: (godotZ, godotX, godotY)
        gz, gx, gy = nrm
        horizontal = abs(gy) >= max(abs(gx), abs(gz))
        if horizontal:
            u, v = (1, 0, 0), (0, -1, 0)
            tex = texture
        else:
            # Unit tangent along the wall, so a 45 degree plan face keeps metric
            # UVs instead of being stretched by root two.
            l = math.hypot(gx, gz)
            u, v = (gx/l, -gz/l, 0.0), (0.0, 0.0, -1.0)
            tex = FLOOR_SIDE if texture == FLOOR else texture
        us = '[ ' + ' '.join(f'{c_:g}' for c_ in u) + ' 0 ]'
        vs = '[ ' + ' '.join(f'{c_:g}' for c_ in v) + ' 0 ]'
        lines.append(' '.join('( ' + ' '.join(f'{val:g}' for val in p) + ' )' for p in (a, b, c))
                     + f' {tex} {us} {vs} 0 0.03125 0.03125')
    lines.append('}')
    brushes.append('\n'.join(lines))
    counts[tally] = counts.get(tally, 0) + 1


# --- centreline paths and their mitre planes -------------------------------

def planes_for(path):
    """A vertical cutting plane at every vertex: perpendicular at the two ends,
    bisecting at every interior vertex. Returns [(point, normal), ...]."""
    dirs = [norm2((b[0]-a[0], b[1]-a[1])) for a, b in zip(path, path[1:])]
    out = [(path[0], dirs[0])]
    for i in range(1, len(path)-1):
        a, b = dirs[i-1], dirs[i]
        out.append((path[i], norm2((a[0]+b[0], a[1]+b[1]))))
    out.append((path[-1], dirs[-1]))
    return out


def run(path, seg, section, texture, name, tally, t0=None, t1=None):
    """Extrude a convex section polygon [(s, y), ...] along segment `seg`.

    s is metres left/right of the centreline, y is height. The ends are cut on
    the mitre planes at the segment's two vertices, which is exactly what makes
    the inside of a turn bend before the outside without anyone computing it.
    Passing t0/t1 overrides an end with a plain perpendicular cut at that
    distance along the segment.
    """
    p = planes_for(path)
    a, b = path[seg], path[seg+1]
    d = norm2((b[0]-a[0], b[1]-a[1]))
    nrm = (d[1], -d[0])                     # right of travel
    ends = []
    for which, plane in ((0, p[seg]), (1, p[seg+1])):
        fixed = t0 if which == 0 else t1
        ring = []
        for s, y in section:
            base = (a[0] + s*nrm[0], a[1] + s*nrm[1])
            if fixed is not None:
                t = fixed
            else:
                pp, pn = plane
                denom = dot((d[0], d[1], 0), (pn[0], pn[1], 0))
                t = ((pp[0]-base[0])*pn[0] + (pp[1]-base[1])*pn[1]) / denom
            ring.append((base[0] + t*d[0], y, base[1] + t*d[1]))
        ends.append(ring)
    emit(ends[0], ends[1], texture, name, tally)


def edge(chain, y0, y1):
    ym = (y0 + y1) / 2
    for (x0, aa), (x1, bb) in zip(chain, chain[1:]):
        if abs(bb - aa) < 1e-9:
            continue
        if min(aa, bb) - 1e-9 <= ym <= max(aa, bb) + 1e-9:
            return (abs(x0 + (y0-aa)/(bb-aa)*(x1-x0)), abs(x0 + (y1-aa)/(bb-aa)*(x1-x0)))
    return None


O = S.SHELL_BACK
WALL_BANDS = S.bands(S.WALL, S.WALL[0][1], S.WALL[-1][1])
RIB_CUTS = sorted({y for _, y in S.WALL if 0 < y < S.RIB_SOFFIT_Y})
RIB_BANDS = S.bands(S.RIB, 0, S.RIB_SOFFIT_Y, RIB_CUTS)
BEAM_BANDS = S.bands(S.WALL, S.RIB_SOFFIT_Y, S.CEIL_Y)


def corridor(path, tag, openings=(), skip=()):
    """Floor, both walls and ceiling along a whole centreline path.

    `openings` are (seg, side, t0, t1) spans where THAT side's wall and footing
    are simply not built - how a branch gets through. The footing has to go too,
    not only the wall: it is charcoal and sits at floor level, so leaving it
    under the branch's dark floor plate would z-fight across the threshold.
    `skip` names (seg, element) pairs to leave out entirely.
    """
    def gap(seg, side):
        for oseg, oside, t0, t1 in openings:
            if oseg == seg and abs(oside - side) < 1e-9:
                return (t0, t1)
        return None

    def sided(seg, section, texture, name, tally, side):
        """One run, or two with a hole bitten out of the middle."""
        g = gap(seg, side)
        if g is None:
            run(path, seg, section, texture, name, tally)
        else:
            run(path, seg, section, texture, name + ' before', tally, t1=g[0])
            run(path, seg, section, texture, name + ' after', tally, t0=g[1])

    for seg in range(len(path)-1):
        if (seg, 'floor') not in skip:
            run(path, seg, [(-S.FLOOR_HALF, S.SUBFLOOR_Y), (S.FLOOR_HALF, S.SUBFLOOR_Y),
                            (S.FLOOR_HALF, 0.0), (-S.FLOOR_HALF, 0.0)],
                FLOOR, f'{tag} floor {seg}', 'floor')
        for side in (-1, 1):
            sided(seg, [(side*S.FLOOR_HALF, S.SUBFLOOR_Y), (side*O, S.SUBFLOOR_Y),
                        (side*O, 0.0), (side*S.FLOOR_HALF, 0.0)],
                  CHARCOAL, f'{tag} footing {seg}', 'floor', side)
        for y0, y1 in WALL_BANDS:
            e = edge(S.WALL, y0, y1)
            for side in (-1, 1):
                sided(seg, [(side*O, y0), (side*e[0], y0), (side*e[1], y1), (side*O, y1)],
                      BAY_TEX, f'{tag} wall {seg} {y0:g}-{y1:g}', 'wall', side)
        if (seg, 'ceiling') not in skip:
            run(path, seg, [(-O, S.CEIL_Y), (O, S.CEIL_Y), (O, S.CEILING_TOP), (-O, S.CEILING_TOP)],
                BAY_TEX, f'{tag} ceiling {seg}', 'ceiling')


# --- jamb corner fills -----------------------------------------------------
# A T has no mitre, so the through wall is cut SQUARE at the opening and the
# branch wall starts SQUARE at the wall line. Wherever the profile is inboard
# of WIDEST, neither solid reaches the pocket corner between them and there is
# a real void: 0.50 m square at the floor, 0.75 m at the ceiling, pinching to
# nothing at the panel band where the profile is at its widest. That funnel
# shape - wide at both extremes, closed in the middle - is exactly what the
# user outlined.
#
# V1 never has it because its two walls are cut on the bisector and meet on
# that plane. This gives the jamb the same resolution by filling the void.
#
# Two earlier attempts are recorded in AGENTS.md as failures: a full-height
# flat (the wall sat flush with it and it read as a pseudo pillar) and a box
# bounded by a vertical plane at each band's innermost reach (it protruded into
# the corridor, because the real face slopes out past that plane). The fill has
# to be bounded by the profile itself, which is what this does.
def jamb_fill(tc, sx, bc, sz, tag):
    """Fill the pocket-corner void at one T jamb.

    `tc`/`sx` are the through corridor's centreline X and the side its opening
    is on; `bc`/`sz` are the branch centreline Z and which jamb. The rectangle
    shrinks as the profile reaches out, so the fill's faces follow the profile
    rather than cutting across it.
    """
    # The void closes exactly at WIDEST, so a band that reaches it tapers to a
    # POINT and the solid becomes a pyramid, which func_godot drops. Clamp the
    # taper to an eighth of a grid unit: still a real prism, and a 1.6 cm
    # sliver at the panel that nothing can see.
    tip = C.WIDE - S.GRID / 8.0

    # The fill runs out to the shell back so it joins both wall solids. That
    # outer corner must NOT be identical in the band's two rings: a shared
    # vertex gives the prism a zero-length edge, one side face collapses to a
    # triangle, and func_godot cannot resolve it - "cannot get winding basis".
    # Sloping it by a tenth of a millimetre per metre keeps every vertex
    # distinct. It is behind the wall face, so nothing can ever see it.
    def rect(e):
        e = min(e, tip)
        back = O + e * 1e-4
        return [(tc + sx*e,     bc + sz*back),
                (tc + sx*back,  bc + sz*back),
                (tc + sx*back,  bc + sz*e),
                (tc + sx*e,     bc + sz*e)]

    for (x0, y0), (x1, y1) in zip(S.WALL, S.WALL[1:]):
        if abs(y1 - y0) < 1e-9:
            continue
        if x0 >= C.WIDE - 1e-9 and x1 >= C.WIDE - 1e-9:
            continue                       # profile is at its widest: no void
        a, b = rect(x0), rect(x1)
        emit([(x, y0, z) for x, z in a], [(x, y1, z) for x, z in b],
             BAY_TEX, f'{tag} jamb fill {y0:g}-{y1:g}', 'wall')


def branch(path, tag, wall_start):
    """A branch corridor whose WALLS begin at the through corridor's wall line.

    Its floor and ceiling run back past that line and overlap the through
    corridor, which is what keeps one continuous dark floor plate across the
    threshold - no texture change, so no supporting geometry is owed.
    """
    back = -(O + 0.5)
    # The threshold plate is as wide as the OPENING, not as wide as a corridor
    # floor. The through corridor's footing is cut back over the full opening
    # (2 x WIDE) but a floor plate is only 2 x FLOOR_HALF, so a 0.5 m strip at
    # each jamb had nothing in it at all - a hole in the floor, which is what
    # the dark notch in the corner was.
    run(path, 0, [(-C.WIDE, S.SUBFLOOR_Y), (C.WIDE, S.SUBFLOOR_Y),
                  (C.WIDE, 0.0), (-C.WIDE, 0.0)],
        FLOOR, f'{tag} threshold plate', 'floor', t0=back, t1=wall_start)
    run(path, 0, [(-S.FLOOR_HALF, S.SUBFLOOR_Y), (S.FLOOR_HALF, S.SUBFLOOR_Y),
                  (S.FLOOR_HALF, 0.0), (-S.FLOOR_HALF, 0.0)],
        FLOOR, f'{tag} floor', 'floor', t0=wall_start)
    run(path, 0, [(-O, S.CEIL_Y), (O, S.CEIL_Y), (O, S.CEILING_TOP), (-O, S.CEILING_TOP)],
        BAY_TEX, f'{tag} ceiling', 'ceiling', t0=back)
    for side in (-1, 1):
        run(path, 0, [(side*S.FLOOR_HALF, S.SUBFLOOR_Y), (side*O, S.SUBFLOOR_Y),
                      (side*O, 0.0), (side*S.FLOOR_HALF, 0.0)],
            CHARCOAL, f'{tag} footing', 'floor', t0=wall_start)
    for y0, y1 in WALL_BANDS:
        e = edge(S.WALL, y0, y1)
        for side in (-1, 1):
            run(path, 0, [(side*O, y0), (side*e[0], y0), (side*e[1], y1), (side*O, y1)],
                BAY_TEX, f'{tag} wall {y0:g}-{y1:g}', 'wall', t0=wall_start)


def rib(path, seg, t, tag):
    """A rib at distance t along a segment, perpendicular to that segment."""
    half = S.RIB_DEPTH/2
    for y0, y1 in RIB_BANDS:
        w, r = edge(S.WALL, y0, y1), edge(S.RIB, y0, y1)
        if w is None or r is None:
            continue
        for side in (-1, 1):
            run(path, seg, [(side*w[0], y0), (side*r[0], y0), (side*r[1], y1), (side*w[1], y1)],
                RIB_TEX, f'{tag} rib shaft', 'rib', t0=t-half, t1=t+half)
    for y0, y1 in BEAM_BANDS:
        w = edge(S.WALL, y0, y1)
        if w is None:
            continue
        run(path, seg, [(-w[0], y0), (w[0], y0), (w[1], y1), (-w[1], y1)],
            RIB_TEX, f'{tag} rib beam', 'rib', t0=t-half, t1=t+half)


def strip(path, seg, t, tier, tag):
    spec = S.LIGHT_TIERS[tier]
    for side in (-1, 1):
        s0, s1 = side*S.STRIP_X, side*(S.STRIP_X + 0.125)
        run(path, seg, [(min(s0, s1), S.CEIL_Y - S.STRIP_INSET), (max(s0, s1), S.CEIL_Y - S.STRIP_INSET),
                        (max(s0, s1), S.CEIL_Y), (min(s0, s1), S.CEIL_Y)],
            spec['tex'], f'{tag} strip {tier}', 'lights',
            t0=t - S.STRIP_LEN/2, t1=t + S.STRIP_LEN/2)


def bulkhead(path, seg, t, inward, tag):
    """Seal an open end with a slab just outside it."""
    run(path, seg, [(-O, S.SUBFLOOR_Y), (O, S.SUBFLOOR_Y), (O, S.CEILING_TOP), (-O, S.CEILING_TOP)],
        MEDIUM, f'{tag} bulkhead', 'ends',
        t0=t, t1=t + (0.25 if inward > 0 else -0.25))


# --- the walk ---------------------------------------------------------------
# The path, the rib rhythm and the bay tiers all live in architecture_lab_corner
# so this generator and the scene writer cannot disagree about where anything
# is. A 90 degree vertex gives V1 outright - the mitre puts a square outer
# corner and a square inner elbow exactly where the paper study drew them. Two
# 45 degree vertices give V4, and because each end of a run is cut on the
# bisector, the inside of the turn bends before the outside all by itself: no
# one has to work out the 2.485 m offset, it falls out of the mitre.
PATH = C.WALK_PATH
seglen, cum, TOTAL = C.walk_metrics()

# The T: the through corridor omits its wall across the opening, and the branch
# supplies its own walls from that line outward.
T_SEG, T_SIDE, T_T0, T_T1 = C.t_opening()
THRU_EXCL, BRANCH_EXCL = C.t_exclusions()
THRU_PINS, BRANCH_START = C.t_pins()
BRANCH = C.t_branch_path()

corridor(PATH, 'run', openings=[(T_SEG, T_SIDE, T_T0, T_T1)])
branch(BRANCH, 'tee', wall_start=C.WIDE)

# V1's outer corner: a 90 degree interior corner, where the two mitred wall
# profiles cross. The through corridor runs +Z on X = 0 and the exit runs +X on
# Z = 52, so the solid lies at -X and +Z of that vertex.
# Both jambs of the T. V1 and V4 need nothing - their bisector cuts already
# make the two profiles meet.


# The T's two jamb corners. The through corridor's centreline is X = 24 and the
# branch's is Z = 30; the solid is on the far side of each from the opening.
for jamb_sz in (+1, -1):
    jamb_fill(C.T_AT[0], -T_SIDE, C.T_AT[1], jamb_sz, f'tee {jamb_sz:+d}')

placed, skipped = C.rib_stations_walk(exclude=THRU_EXCL, pins=THRU_PINS)
for d, seg, t in placed:
    rib(PATH, seg, t, f'{d:g}m')

lights = C.light_stations_walk(rib_exclude=THRU_EXCL, rib_pins=THRU_PINS)
for mid, seg, t, tier in lights:
    strip(PATH, seg, t, tier, f'{mid:g}m')

b_placed, b_skipped = C.rib_stations_walk(BRANCH, BRANCH_EXCL, start=BRANCH_START)
for d, seg, t in b_placed:
    rib(BRANCH, seg, t, f'tee {d:g}m')

b_lights = C.light_stations_walk(BRANCH, BRANCH_EXCL, BRANCH_EXCL, rib_start=BRANCH_START)
for mid, seg, t, tier in b_lights:
    strip(BRANCH, seg, t, tier, f'tee {mid:g}m')
lights = lights + b_lights
placed = placed + b_placed

bulkhead(PATH, 0, 0.0, -1, 'start')
bulkhead(PATH, len(PATH)-2, seglen[-1], +1, 'end')
bulkhead(BRANCH, 0, C.T_LENGTH, +1, 'tee end')

HEADER_LINES = [
    '// Game: Red Breach',
    '// Format: Valve',
    '{',
    '"classname" "worldspawn"',
    '"_tb_def" "builtin:FuncGodot.fgd"',
    '"_tb_textures" "greybox/Dark;greybox/GreyCharcoal;greybox/GreyMedium;greybox/GreyPale;greybox/Emissive"',
]
EOL = chr(10)
MAP.parent.mkdir(parents=True, exist_ok=True)
MAP.write_text(EOL.join(HEADER_LINES + brushes + ['}', '']), encoding='utf-8')

lit = sum(1 for *_, t in lights if C.light_energy(t) > 0)
print(f'ARCH_CORNER_BOOTSTRAP: {len(brushes)} brushes, {TOTAL:.2f} m walk')
for k in ('floor', 'wall', 'ceiling', 'rib', 'lights', 'ends'):
    print(f'  {k:<9}{counts.get(k, 0):>4}')
print(f'  straight before the first corner: {cum[1]:.2f} m')
for i, nm in C.WALK_CORNERS.items():
    print(f'  {nm:<12} {math.degrees(C.turn_at(i)):.0f} deg at {PATH[i]}, '
          f'clearance {C.turn_clearance(i):.3f} m, path {cum[i]:.2f} m')
print(f'  ribs placed {len(placed)}, skipped {[f"{x:g}" for x in skipped]}')
print(f'  T at {C.T_AT}, branch {C.T_LENGTH:g} m, opening t {T_T0:g}..{T_T1:g} side {T_SIDE:+.0f}')
print(f'  branch ribs {len(b_placed)}, branch bays {len(b_lights)}')
print(f'  bays {len(lights)}, lit {lit}, plan {C.LIGHT_PLAN}')
print(f'  spawn faces +Z from (0, 0.05, {PATH[0][1] + 1.0:g})')
print(f'  wrote {MAP.relative_to(ROOT)}')
