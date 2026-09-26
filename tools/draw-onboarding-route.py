"""
Onboarding route graph -- revision 04, stage 1: the journey only.

Method: route-first, not function-first. Placing functions first fixes the
distances between them, and those distances are the whole budget for
connective tissue -- which is why revisions 01-03 came out 82% programmed room
/ 18% connective, the inverse of admin.map's 21/79.

Revision 04b: the first route measured correctly and still looked wrong. Every
direction change came from one helper that always emitted the same symmetric
S-bend, so the whole route was a single bend shape repeated sixty times.
Turn counts and run lengths are blind to that. So bends are now a VOCABULARY
chosen per situation -- corner, asymmetric dogleg, 45 chamfer, switchback,
short jink, and crossings that change the space without turning at all --
and the report counts the shapes, not just the turns.

Reference, study 02 (docs/architecture-reference-study-02-rooms.md):
  admin.map ground story corridor skeleton .... 235 m
  runs between junctions ...................... 89, median 3.3 m,
                                                90th pct 16.1 m, max 29.1 m
"""
from pathlib import Path
from collections import Counter
from html import escape
from math import hypot, cos, sin, radians
from statistics import median

ROOT = Path(__file__).resolve().parents[1]

C = {
    'bg': '#0b1218', 'grid': '#16222c', 'ink': '#edf4fa', 'muted': '#8aa2b2',
    'main': '#e2b373', 'stub': '#9fb8c8', 'beat': '#ffd88a',
    'note': '#c98aa0', 'junction': '#e06a6a', 'cross': '#7fc4a8',
}


class Turtle:
    """A walked route authored as moves. Heading is degrees, 0 = east,
    positive = clockwise on screen (y grows downward, as the plan is drawn).
    Angles are free, so 45-degree work is available."""

    def __init__(self, x, y, heading=0.0, z=0.0):
        self.x, self.y, self.a, self.z = x, y, heading, z
        self.paths = [[(x, y, z)]]
        self.beats, self.notes, self.turns = [], [], []
        self.marks, self.runs, self.checkpoints = {}, [], []
        self.bends = Counter()
        self.verticals = []      # (x0,y0,x1,y1,dz,kind) for drawing
        self.junctions_declared = []
        self.vlabels = []
        self._since_turn = 0.0

    # -- primitives ------------------------------------------------------
    def fwd(self, n, dz=0.0):
        self.x += n * cos(radians(self.a))
        self.y += n * sin(radians(self.a))
        self.z += dz
        self.paths[-1].append((self.x, self.y, self.z))
        self._since_turn += n
        return self

    # -- elevation -------------------------------------------------------
    # Two kinds, per study 03: STRUCTURAL changes that buy over/under
    # clearance, and TEXTURAL ones that just keep the floor from being flat.

    def step(self, dz, label=None):
        """A riser or two. Textural -- too small to clear anything, but it is
        what most of Doom 3's texture transitions ride on."""
        self.z += dz
        self.paths[-1].append((self.x, self.y, self.z))
        self.verticals.append((self.x, self.y, self.x, self.y, dz, 'step'))
        if label:
            self.vlabels.append(label)
        return self

    def stair(self, run, dz, label=None):
        """A flight. Structural: this is how a leg gets out of another leg's
        way. Keep the pitch between about 25 and 35 degrees."""
        x0, y0 = self.x, self.y
        self.fwd(run, dz)
        self.verticals.append((x0, y0, self.x, self.y, dz, 'stair'))
        if label:
            self.vlabels.append(label)
        return self

    def ramp(self, run, dz, label=None):
        """Shallower than a stair; only viable for small drops at this scale
        (2.25 m at 1:10 would be 22 m of ramp)."""
        x0, y0 = self.x, self.y
        self.fwd(run, dz)
        self.verticals.append((x0, y0, self.x, self.y, dz, 'ramp'))
        if label:
            self.vlabels.append(label)
        return self

    def ladder(self, dz, label=None):
        """Straight up or down, no horizontal travel. Cheap height in a tight
        space -- a metre or two at a time, the way Doom 3 does it."""
        self.z += dz
        self.paths[-1].append((self.x, self.y, self.z))
        self.verticals.append((self.x, self.y, self.x, self.y, dz, 'ladder'))
        if label:
            self.vlabels.append(label)
        return self

    def crawl(self, run, dz=0.0, label=None):
        """A duck-under. Uses the crouch the controller already has, and reads
        as a third traversal state beside walking and stairs."""
        x0, y0 = self.x, self.y
        self.fwd(run, dz)
        self.verticals.append((x0, y0, self.x, self.y, dz, 'crawl'))
        if label:
            self.vlabels.append(label)
        return self

    def cross_up(self, label, run, dz):
        """A ROOM that carries height: walk in, climb inside it, leave by
        another door higher (or lower) than you came in. The level change is
        the room's business, not a corridor's."""
        self.bends['room with a level change'] += 1
        self.note(label, 0.7, -2.6, cross=True)
        x0, y0 = self.x, self.y
        self.fwd(run, dz)
        self.verticals.append((x0, y0, self.x, self.y, dz, 'room'))
        return self

    def pitch(self, run, dz):
        from math import degrees, atan2
        return degrees(atan2(abs(dz), run))

    def turn(self, deg):
        if self._since_turn > 1e-6:
            self.runs.append(self._since_turn)
            self._since_turn = 0.0
        self.turns.append((self.x, self.y, deg))
        self.a += deg
        return self

    # -- the bend vocabulary ---------------------------------------------
    # Each one is a different SHAPE, not the same shape with new numbers.

    def corner(self, deg=90):
        """A plain L. The corridor simply goes another way."""
        self.bends['corner'] += 1
        return self.turn(deg)

    def dogleg(self, across, deg=90, kind='dogleg'):
        """Step sideways and carry on. `across` is the offset; the runs either
        side are written explicitly by the caller, so no two are alike."""
        self.bends[kind] += 1
        self.turn(deg).fwd(across).turn(-deg)
        return self

    def chamfer(self, across, deg=45):
        """A soft bend: two 45s instead of a square corner."""
        self.bends['chamfer'] += 1
        self.turn(deg).fwd(across).turn(-deg)
        return self

    def bend45(self, deg=45):
        """A single 45 -- the corridor just leans off true and stays there."""
        self.bends['bend45'] += 1
        return self.turn(deg)

    def switchback(self, gap, deg=90):
        """Doubles back. Two turns the same way."""
        self.bends['switchback'] += 1
        self.turn(deg).fwd(gap).turn(deg)
        return self

    def jink(self, across, run, deg=90):
        """A brief nudge: offset, a short run, straight back. Tighter and
        more abrupt than a dogleg."""
        self.bends['jink'] += 1
        self.turn(deg).fwd(across).turn(-deg).fwd(run).turn(-deg).fwd(across).turn(deg)
        return self

    # -- crossings: the space changes, the direction does not -------------
    def cross(self, label, n, dx=0.0, dy=0.0):
        """Pass straight through a space. No turn -- the interruption is the
        room itself, not a bend."""
        self.bends['crossing'] += 1
        self.note(label, dx, dy, cross=True)
        return self.fwd(n)

    def cross_diag(self, label, a, b, deg=45, dx=0.0, dy=0.0):
        """Enter a space by one wall and leave by an adjacent one."""
        self.bends['diagonal crossing'] += 1
        self.note(label, dx, dy, cross=True)
        self.turn(deg).fwd(a).turn(-deg).fwd(b)
        return self

    # -- annotation ------------------------------------------------------
    def beat(self, label, dx=0.0, dy=0.0):
        self.beats.append((self.x + dx, self.y + dy, label))
        return self

    def note(self, label, dx=0.0, dy=0.0, cross=False, kind=None):
        self.notes.append((self.x + dx, self.y + dy, label,
                           kind or ('cross' if cross else 'space')))
        return self

    # -- branching -------------------------------------------------------
    def cp(self, name):
        """Checkpoint: record where and which way we are pointing, so band
        transitions can be verified instead of traced by hand."""
        self.checkpoints.append((name, self.x, self.y, self.a % 360, self.z))
        return self

    def junction(self, x, y, label):
        """Declare that two legs meeting here is intentional. Only legitimate
        when every arm leads somewhere -- otherwise it is a leg that exists
        solely to lengthen the walk."""
        self.junctions_declared.append((x, y, label))
        self.note(label, 1.4, 2.6)
        return self

    def mark(self, name):
        self.marks[name] = (self.x, self.y, self.a, self.z)
        return self

    def jump(self, name, heading):
        self.end()
        self.x, self.y, _, self.z = self.marks[name]
        self.a = heading
        self.paths.append([(self.x, self.y, self.z)])
        return self

    def end(self):
        if self._since_turn > 1e-6:
            self.runs.append(self._since_turn)
            self._since_turn = 0.0
        return self

    def length(self):
        return sum(hypot(b[0] - a[0], b[1] - a[1])
                   for p in self.paths for a, b in zip(p, p[1:]))


def journey():
    """Read this like a walkthrough. Every bend names its own shape, and no
    two consecutive bends use the same one."""
    t = Turtle(4.0, 19.0, 0)
    t.beat('AIRLOCK  in / out', -2.4, -1.8)

    # --- out of the lock: tight, squared, institutional --------------------
    t.fwd(5)
    t.beat('ARRIVAL', -0.6, 2.8)
    t.dogleg(3.5).fwd(3)
    t.note('pipe bay: ceiling drops,\nservice run crosses overhead', 1.2, 3.2)
    t.corner(-90).fwd(11)
    t.jink(2.0, 3.0, -90)          # a nudge round something unseen
    t.fwd(4).corner(90)

    t.cp('band 1 start')
    # --- band one, east across the front. Public, calmer geometry ---------
    t.fwd(5)
    t.beat('RECEPTION  sign-in', -2.4, -2.8)
    t.fwd(3)
    t.step(-0.40)                  # textural: the railing/step-down chamber
    t.note('junction chamber: railing,\nstep down, three ways out', 0.8, 1.7)
    t.mark('j_comms')
    t.chamfer(4.5).fwd(5)
    t.step(0.40)                   # and back up out of it
    t.cross_diag('PUMP ROOM, entered at a corner:\nthree pumps, walkway, two doors',
                 5.0, 4.0, 45, 0.8, -3.2)
    t.bend45(-45).fwd(5).bend45(45)   # lean off true, then straighten again
    t.note('long bay, floor grating — the first\nplace you can see any distance', 0.8, 1.8)
    t.fwd(12)                       # long run one
    t.dogleg(2.5, -90).fwd(3)
    t.corner(90)
    t.ladder(-1.90, 'service ladder down\nbeside the tanks')
    t.step(-0.60, 'sunken bay, two risers down')
    t.fwd(2.0)
    t.cross_up('PLANT ROOM: in one door, down\nits internal steps, out the far side', 3.5, -1.80)
    t.stair(3.0, -0.70, 'last short flight')
    t.corner(90)

    t.cp('band 2 start')
    # --- band two, back west. Working spaces, tighter and more awkward ----
    t.fwd(9)
    t.note('narrow squeeze between\ntwo equipment banks', -7.5, 1.8)
    t.jink(1.8, 2.5, 90).fwd(10)
    t.beat('ARMORY', -1.6, -2.6)
    t.mark('j_range')
    t.fwd(5).dogleg(4.0, 90)
    t.fwd(17)                       # long run two, the working spine
    t.note('junction with nothing in it,\nthree ways out', -7.0, 1.8)
    t.turn(-90)
    t.stair(2.6, 1.30, 'short flight off the working floor')
    t.cross_up('SWITCH ROOM: cabinets both sides,\nsteps up through the middle', 3.0, 1.10)
    t.ladder(1.20, 'ladder to the landing')
    t.crawl(2.4, 0.45, 'crawlspace off the landing —\nduck through, comes out higher')
    t.stair(1.6, 0.95, 'final risers')
    t.turn(-90)
    t.bends['switchback'] += 1

    t.cp('band 3 start')
    # --- band three, east again. Service side: leaning, diagonal ----------
    t.fwd(8).chamfer(5.0, -45)
    t.cross('service crossing — equipment\nleaves one lane open', 7.0, 0.8, 1.8)
    t.bend45(45).fwd(5).bend45(-45)
    t.fwd(17)                       # long run three
    t.dogleg(3.0, 90).fwd(5)
    t.beat('DISPATCH  assignment', -2.6, -2.8)
    t.corner(90)
    t.step(-0.45, 'threshold drop')
    t.ramp(4.0, -1.15, 'service ramp, trolley width')
    t.cross_up('SWITCHGEAR ROOM: walk in level,\nleave down the far corner steps', 3.2, -1.65)
    t.fwd(1.5)
    t.stair(2.8, -1.75, 'flight into back of house')
    t.corner(90)

    t.cp('band 4 start')
    # --- band four, the back-of-house return. Irregular, unlovely ---------
    t.fwd(5).jink(2.2, 3.5, -90)
    t.cross('machinery crossing:\nstep up, cross, step down', 6.0, -7.5, -2.4)
    t.dogleg(3.0, -90).fwd(4)
    t.beat('LOCKERS  suit up', -2.4, 2.8)
    t.fwd(12)                       # the third long one
    t.note('grille floor over a service void', -7.5, -2.2)
    t.chamfer(3.5, 45).fwd(5)
    t.jink(1.6, 2.0, 90)
    t.note('last dogleg before the lock', -6.5, 2.6)

    t.cp('return leg start')
    # --- north, back to the lock -------------------------------------------
    # Front-loaded on purpose: the ladder costs no plan distance and buys most
    # of the separation immediately, so the gentler slices that follow happen
    # after this leg has already cleared the one below it.
    t.dogleg(4.0, -90)
    t.ladder(2.60, 'tall ladder straight out\nof the back corridor')
    t.fwd(2.0)
    t.cross_up('PUMP GALLERY: cross it on a walkway,\nsteps at the far end', 3.5, 1.10)
    t.crawl(2.0, 0.30, 'low duct crossing')
    t.stair(2.0, 1.00, 'last flight into the lobby')
    t.fwd(0.6)
    t.corner(90).fwd(19.0)   # long run north up the west side, back to the lock
    t.cp('route end')
    t.end()

    # --- declared junctions -------------------------------------------------
    # Both sit in the lobby hub by the lock, and both pass the all-arms test:
    # north to Reception, south to Arrival and the lock, east along the service
    # band, west to the washroom/store pod. No arm exists only to add distance.
    t.junction(13.4, 17.6, 'lobby hub: four ways,\nall of them go somewhere')
    t.junction(5.2, 22.9, 'second approach into\nthe lock lobby')

    # --- stubs --------------------------------------------------------------
    t.jump('j_comms', -90).fwd(5.5)
    t.beat('COMMS  radio', -1.6, -1.8)
    t.end()

    t.jump('j_range', 90).fwd(6).corner(-90).fwd(5)
    t.beat('RANGE', -1.4, 2.8)
    t.end()

    return t


# ------------------------------------------------------------------ draw --
K, OX, OY = 15.5, 60, 130
S = []


def fit_view(t, box=(60, 124, 1176, 630)):
    global K, OX, OY
    pts = ([p for path in t.paths for p in path]
           + [(x, y) for x, y, _ in t.beats]
           + [(x, y) for x, y, _, _ in t.notes])
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    pad = 3.0
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    bx0, by0, bx1, by1 = box
    K = min((bx1 - bx0) / (x1 - x0), (by1 - by0) / (y1 - y0))
    OX = bx0 - x0 * K + ((bx1 - bx0) - (x1 - x0) * K) / 2
    OY = by0 - y0 * K + ((by1 - by0) - (y1 - y0) * K) / 2
    return x0, y0, x1, y1


def mx(v):
    return round(OX + v * K, 2)


def my(v):
    return round(OY + v * K, 2)


def text(x, y, s, size=13, color='ink', bold=False, anchor='start', italic=False):
    S.append(f'<text x="{x}" y="{y}" fill="{C.get(color, color)}" font-size="{size}" '
             f'font-weight="{700 if bold else 400}" text-anchor="{anchor}" '
             f'font-style="{"italic" if italic else "normal"}">{escape(s)}</text>')


def _seg_dist(p, q, r, s):
    """Minimum distance between 2D segments pq and rs."""
    def clamp(v):
        return max(0.0, min(1.0, v))

    def pt_seg(pt, a, b):
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        if L2 < 1e-12:
            return hypot(pt[0] - ax, pt[1] - ay)
        u = clamp(((pt[0] - ax) * dx + (pt[1] - ay) * dy) / L2)
        return hypot(pt[0] - (ax + u * dx), pt[1] - (ay + u * dy))

    d1 = (q[0] - p[0], q[1] - p[1])
    d2 = (s[0] - r[0], s[1] - r[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) > 1e-12:                      # non-parallel: check for a true crossing
        t1 = ((r[0] - p[0]) * d2[1] - (r[1] - p[1]) * d2[0]) / den
        t2 = ((r[0] - p[0]) * d1[1] - (r[1] - p[1]) * d1[0]) / den
        if 0 <= t1 <= 1 and 0 <= t2 <= 1:
            return 0.0
    return min(pt_seg(p, r, s), pt_seg(q, r, s), pt_seg(r, p, q), pt_seg(s, p, q))


def conflicts(t, near=5.0, skip=3):
    """Places the route runs into or too close beside itself in plan.

    `near` is the centreline separation below which two corridors cannot both
    exist at the same level: a 3 m corridor plus 0.25 m walls each side needs
    ~3.5 m, and anything under ~5 m leaves no room for a wall build-up or a
    room between them. Neighbouring segments of the same path are skipped."""
    # arc position of each segment along its own path: two stretches that are
    # close in WALKING distance cannot conflict, they are the same corridor
    # bending. Segment-index skipping got this wrong once the vertical chains
    # started inserting many short segments.
    segs = []
    for pi, path in enumerate(t.paths):
        arc = 0.0
        for si in range(len(path) - 1):
            a, b = path[si], path[si + 1]
            segs.append((pi, si, a, b, arc))
            arc += hypot(b[0] - a[0], b[1] - a[1])
    def shares_end(a, b, c, d):
        """A stub leaving the main route, or the loop closing at the airlock,
        touches legitimately -- that is a junction, not a conflict."""
        return any(hypot(p[0] - q[0], p[1] - q[1]) < 0.75
                   for p in (a, b) for q in (c, d))

    def collinear(a, b, c, d, tol=1.0):
        """Two stretches of the SAME corridor either side of a jink are
        collinear and merely separated along their shared line. The segment
        distance test reads that as a 2 m gap; it is not a conflict."""
        ax, ay = a[0], a[1]
        dx, dy = b[0] - ax, b[1] - ay
        L = hypot(dx, dy)
        if L < 1e-9:
            return False
        nx, ny = -dy / L, dx / L        # unit normal of A's line
        return all(abs((q[0] - ax) * nx + (q[1] - ay) * ny) < tol for q in (c, d))

    out = []
    for i in range(len(segs)):
        pi, si, a, b, arc_i = segs[i]
        for j in range(i + 1, len(segs)):
            pj, sj, c, d, arc_j = segs[j]
            if pi == pj and abs(arc_i - arc_j) < 16.0:
                continue
            if shares_end(a, b, c, d) or collinear(a, b, c, d):
                continue
            gap = _seg_dist(a[:2], b[:2], c[:2], d[:2])
            if gap < near:
                mid = ((a[0] + b[0] + c[0] + d[0]) / 4, (a[1] + b[1] + c[1] + d[1]) / 4)
                dz = abs(((a[2] + b[2]) / 2) - ((c[2] + d[2]) / 2))
                out.append((gap, mid, (pi, si), (pj, sj), dz))
    out.sort(key=lambda r: r[0])
    # collapse clusters so one physical conflict is reported once
    merged = []
    for rec in out:
        mid = rec[1]
        if any(hypot(mid[0] - m[1][0], mid[1] - m[1][1]) < 6 for m in merged):
            continue
        merged.append(rec)
    return merged


# corridor clear height (3.5-4.0 m per architecture-language.md) plus floor
# structure. Below this, two corridors cannot pass over one another.
FLOOR_TO_FLOOR = 4.5


def is_declared(t, mid, within=7.0):
    return any(hypot(mid[0] - jx, mid[1] - jy) < within
               for jx, jy, _ in t.junctions_declared)


def unresolved(t):
    """Genuinely broken: too close to coexist at one level, not separated
    vertically, and not a declared junction. 3.5 m is the hard floor -- two
    3 m corridors plus the 0.25-per-room wall rule."""
    return [c for c in conflicts(t)
            if c[4] < FLOOR_TO_FLOOR - 0.01
            and c[0] < 3.0          # 2.5 m corridors + 0.5 m of wall
            and not is_declared(t, c[1])]


def main():
    t = journey()
    L, runs = t.length(), [r for r in t.runs if r > 0.01]
    angles = Counter(abs(int(round(d))) for _, _, d in t.turns)

    W, H = 1240, 1010
    S.append(f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>')
    vx0, vy0, vx1, vy1 = fit_view(t)
    for gx in range(int(vx0 // 5) * 5, int(vx1 // 5 + 1) * 5 + 1, 5):
        S.append(f'<line x1="{mx(gx)}" y1="{my(vy0)}" x2="{mx(gx)}" y2="{my(vy1)}" stroke="{C["grid"]}" stroke-width="1"/>')
    for gy in range(int(vy0 // 5) * 5, int(vy1 // 5 + 1) * 5 + 1, 5):
        S.append(f'<line x1="{mx(vx0)}" y1="{my(gy)}" x2="{mx(vx1)}" y2="{my(gy)}" stroke="{C["grid"]}" stroke-width="1"/>')

    text(36, 44, 'RED BREACH / ONBOARDING — REVISION 04, STAGE 1: THE JOURNEY', 22, 'ink', True)
    text(36, 68, 'Walked centreline only. Bends are chosen from a vocabulary — corner, dogleg, chamfer, switchback, jink, room crossing — rather than one repeated S-bend.', 13, 'muted')
    text(36, 90, 'Gold = entry level (0.00). Blue = working level (-5.00). Everything on the plan is a symbol; the legend below says what each one is.', 13, 'muted', italic=True)
    text(W - 36, 112, f'{vx1 - vx0:.0f} x {vy1 - vy0:.0f} m  •  5 m grid', 12, 'muted', anchor='end')

    # route drawn per segment so elevation can be read off the colour
    for i, p in enumerate(t.paths):
        stub = i > 0
        for a, b in zip(p, p[1:]):
            zmid = (a[2] + b[2]) / 2
            climbing = abs(a[2] - b[2]) > 0.05 and hypot(b[0] - a[0], b[1] - a[1]) > 0.5
            if climbing:
                col, w = '#ffffff', 4.0
            elif zmid < -2.5:
                col, w = '#6d9bc9', 3.0          # lower level
            else:
                col, w = C['main'], 3.0          # entry level
            S.append(f'<line x1="{mx(a[0])}" y1="{my(a[1])}" x2="{mx(b[0])}" y2="{my(b[1])}" '
                     f'stroke="{col}" stroke-width="{w if not stub else w - 1}" stroke-linecap="round" '
                     f'stroke-dasharray="{"5 4" if stub else ""}" opacity="{0.85 if stub else 1}"/>')

    V_GLYPH = {'stair': '▤', 'ladder': '≣', 'crawl': '⌣',
               'ramp': '◢', 'room': '◫', 'step': '─'}
    V_COL = {'stair': '#ffffff', 'ladder': '#9fd8ff', 'crawl': '#c6a0ff',
             'ramp': '#ffd08a', 'room': '#7fc4a8', 'step': '#ffd88a'}

    # vertical elements: a small glyph plus its rise, numbered into the legend
    vindex = []
    for x0, y0, x1, y1, dz, kind in t.verticals:
        n = len(vindex) + 1
        cx_, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
        col = V_COL[kind]
        S.append(f'<rect x="{mx(cx_) - 8}" y="{my(cy_) - 8}" width="16" height="16" rx="3" '
                 f'fill="{C["bg"]}" stroke="{col}" stroke-width="1.6"/>')
        text(mx(cx_), my(cy_) + 4.5, V_GLYPH[kind], 11, col, True, 'middle')
        text(mx(cx_) + 12, my(cy_) - 5, f'V{n}', 9, col, True)
        text(mx(cx_) + 12, my(cy_) + 6, f'{dz:+.1f}', 9, 'muted')
        vindex.append((n, kind, dz, t.vlabels[n - 1] if n <= len(t.vlabels) else ''))

    for x, y, d in t.turns:
        S.append(f'<circle cx="{mx(x)}" cy="{my(y)}" r="{2.0 if abs(d) >= 90 else 3.0}" '
                 f'fill="{C["junction"] if abs(d) >= 90 else "none"}" '
                 f'stroke="{C["junction"]}" stroke-width="1.2" opacity="0.75"/>')

    # connective spaces: numbered rings only, described in the legend
    sindex = []
    for x, y, label, kind in t.notes:
        if kind == 'vertical':
            continue
        n = len(sindex) + 1
        col = C['cross'] if kind == 'cross' else C['note']
        S.append(f'<circle cx="{mx(x)}" cy="{my(y)}" r="7.5" fill="{C["bg"]}" stroke="{col}" stroke-width="1.8"/>')
        text(mx(x), my(y) + 3.5, str(n), 9, col, True, 'middle')
        sindex.append((n, kind, label))

    for gap, (cxm, cym), _, _, dz in conflicts(t):
        if dz >= FLOOR_TO_FLOOR - 0.01:
            col, mark = '#5fcf9e', 'U'
        elif is_declared(t, (cxm, cym)):
            col, mark = '#ffb347', 'J'
        elif gap >= 3.0:
            col, mark = '#c9b45f', 'P'
        else:
            col, mark = '#ff5a5a', 'X'
        S.append(f'<circle cx="{mx(cxm)}" cy="{my(cym)}" r="12" fill="none" stroke="{col}" '
                 f'stroke-width="2.2" stroke-dasharray="3 3"/>')
        text(mx(cxm), my(cym) + 3.5, mark, 9, col, True, 'middle')

    for i, (x, y, label) in enumerate(t.beats, 1):
        S.append(f'<circle cx="{mx(x)}" cy="{my(y)}" r="10" fill="{C["beat"]}"/>')
        text(mx(x), my(y) + 4.5, str(i), 12, '#1b1205', True, 'middle')

    # ------------------------------------------------------------ legend --
    ly = 660
    S.append(f'<line x1="36" y1="{ly - 14}" x2="{W - 36}" y2="{ly - 14}" stroke="#223040" stroke-width="1"/>')

    def head(x, y, s_):
        text(x, y, s_, 12, 'ink', True)

    head(36, ly + 6, 'STORY BEATS')
    for i, (_, _, label) in enumerate(t.beats, 1):
        S.append(f'<circle cx="44" cy="{ly + 22 + (i - 1) * 17}" r="7" fill="{C["beat"]}"/>')
        text(44, ly + 26 + (i - 1) * 17, str(i), 9, '#1b1205', True, 'middle')
        text(58, ly + 26 + (i - 1) * 17, label, 11, 'muted')

    head(268, ly + 6, 'CONNECTIVE SPACES  (no function, shape only)')
    for n, kind, label in sindex:
        col = C['cross'] if kind == 'cross' else C['note']
        row = (n - 1) % 8
        colx = 268 + ((n - 1) // 8) * 300
        yy = ly + 26 + row * 17
        S.append(f'<circle cx="{colx + 7}" cy="{yy - 4}" r="6.5" fill="none" stroke="{col}" stroke-width="1.5"/>')
        text(colx + 7, yy, str(n), 8.5, col, True, 'middle')
        text(colx + 20, yy, label.replace('\n', ' '), 10.5, 'muted')

    head(W - 372, ly + 6, 'VERTICAL')
    for n, kind, dz, label in vindex:
        row = (n - 1) % 9
        colx = W - 372 + ((n - 1) // 9) * 176
        yy = ly + 26 + row * 17
        text(colx, yy, f'{V_GLYPH[kind]} V{n}', 10, V_COL[kind], True)
        text(colx + 42, yy, f'{dz:+.2f} m  {kind}', 10, 'muted')

    head(36, ly + 178, 'SYMBOLS')
    keys = [('▤', '#ffffff', 'stair'), ('≣', '#9fd8ff', 'ladder'),
            ('⌣', '#c6a0ff', 'crawlspace'), ('◢', '#ffd08a', 'ramp'),
            ('◫', '#7fc4a8', 'room carries the level change'),
            ('─', '#ffd88a', 'textural step'),
            ('U', '#5fcf9e', 'conflict cleared by over/under'),
            ('J', '#ffb347', 'intentional junction'),
            ('P', '#c9b45f', 'pinch - neck both to 2.5 m')]
    for i, (g, col, lab) in enumerate(keys):
        x = 36 + (i % 5) * 232
        y = ly + 198 + (i // 5) * 18
        text(x, y, g, 11, col, True)
        text(x + 16, y, lab, 10.5, 'muted')

    head(36, ly + 244, 'MEASURED AGAINST admin.map (study 02)')
    rows = [
        ('walked route', f'{L:.0f} m', '235 m'), ('turns', f'{len(t.turns)}', '153'),
        ('straight runs', f'{len(runs)}', '89'), ('median run', f'{median(runs):.1f} m', '3.3 m'),
        ('longest run', f'{max(runs):.0f} m', '29.1 m'), ('story beats', f'{len(t.beats)}', '~9'),
        ('connective spaces', f'{len(sindex)}', '~12'),
        ('conflicts / unresolved', f'{len(conflicts(t))} / {len(unresolved(t))}', ''),
    ]
    for i, (k, mine, ref) in enumerate(rows):
        x = 36 + (i % 4) * 292
        y = ly + 268 + (i // 4) * 36
        text(x, y, k, 10.5, 'muted')
        text(x, y + 15, mine, 13, 'ink', True)
        if ref:
            text(x + 66, y + 15, f'vs {ref}', 10, 'muted')

    out = ROOT / 'docs' / 'onboarding-route.svg'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<title>Red Breach onboarding route graph, revision 04</title>' + ''.join(S) + '</svg>')
    out.write_text(svg, encoding='utf-8')
    print(f'wrote {out}')
    print(f'route {L:.0f} m | {len(t.turns)} turns | runs {len(runs)}, median {median(runs):.1f} m, max {max(runs):.0f} m')
    print(f'angles: {dict(sorted(angles.items()))}')
    print(f'bends : {dict(t.bends)}')
    print(f'extent {vx1 - vx0:.0f} x {vy1 - vy0:.0f} m')
    for n, x, y, a, z in t.checkpoints:
        print(f'  {n:<18} ({x:6.1f},{y:6.1f}) heading {a:5.0f}  z {z:+5.2f}')
    ax, ay, _ = t.beats[0][0], t.beats[0][1], None
    ex, ey = t.checkpoints[-1][1], t.checkpoints[-1][2]
    print(f'  closure gap to airlock: {hypot(ex-ax, ey-ay):.1f} m')
    cs = conflicts(t)
    bad = unresolved(t)
    print(f'\nplan conflicts: {len(cs)}   still unresolved after elevation: {len(bad)}')
    for gap, mid, A, B, dz in cs:
        kind = 'CROSSES' if gap < 0.01 else f'{gap:4.1f} m apart'
        if dz >= FLOOR_TO_FLOOR - 0.01:
            verdict = 'ok - over/under'
        elif is_declared(t, mid):
            verdict = 'ok - declared junction'
        elif gap >= 3.5:
            verdict = 'tight - legal at 3.0 m corridor width'
        elif gap >= 3.0:
            verdict = 'PINCH - build both at 2.5 m width'
        else:
            verdict = 'IMPOSSIBLE at one level'
        print(f'  at ({mid[0]:5.1f},{mid[1]:5.1f})  {kind:>14}  dz {dz:4.2f}  {verdict}')
    print('\nvertical elements')
    for x0, y0, x1, y1, dz, kind in t.verticals:
        if kind == 'step':
            continue
        run = hypot(x1 - x0, y1 - y0)
        print(f'  {kind:<6} run {run:4.1f} m  rise {dz:+5.2f} m  pitch {t.pitch(run, dz):4.1f} deg')
    print(f'  textural steps: {sum(1 for v in t.verticals if v[5] == "step")}')


if __name__ == '__main__':
    main()
