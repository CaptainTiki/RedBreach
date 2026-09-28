"""Read a Valve 220 .map back: entities, brushes with their // names and TrenchBroom groups, and face polygons.

The z-fight check and the playtest note reader both work from the map AS EDITED (including hand edits in
TrenchBroom), never from what a generator meant to write.

    import mapkit
    m = mapkit.load('RedBreach/maps/freight_v2_01.map')
    for b in m.brushes: b.name, b.group, b.faces (each face: n, d, texture, pts)

Coordinates: map units (32 per metre) on map axes (godot z, godot x, godot y). plan() and from_godot() convert.
"""
import math
import re

UNITS = 32.0
_FACE = re.compile(r'\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)\s*'
                   r'\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)\s*'
                   r'\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)\s*(\S+)')
_KV = re.compile(r'"([^"]*)"\s+"([^"]*)"')


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def norm(a):
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n) if n > 1e-12 else (0.0, 0.0, 0.0)


def plan(p):
    """Map units -> plan metres (x east, y north, h up)."""
    return (p[1] / UNITS, -p[0] / UNITS, p[2] / UNITS)


def from_godot(g):
    """Godot metres (x, y up, z) -> map units."""
    return (g[2] * UNITS, g[0] * UNITS, g[1] * UNITS)


def godot_dir_to_map(v):
    return (v[2], v[0], v[1])


class Face:
    __slots__ = ('n', 'd', 'texture', 'pts', 'brush', 'uv')

    def __init__(self, n, d, texture):
        self.n, self.d, self.texture, self.pts, self.brush, self.uv = n, d, texture, [], None, ''

    def area(self):
        """In square metres."""
        s = (0.0, 0.0, 0.0)
        for i in range(len(self.pts)):
            s = add(s, cross(self.pts[i], self.pts[(i + 1) % len(self.pts)]))
        return abs(dot(s, self.n)) / 2 / UNITS ** 2

    def contains(self, p, tol=0.5):
        """p (map units) lies on this face's polygon, within tol units of its plane."""
        if abs(dot(self.n, p) - self.d) > tol or len(self.pts) < 3:
            return False
        for i in range(len(self.pts)):
            a, b = self.pts[i], self.pts[(i + 1) % len(self.pts)]
            if dot(cross(sub(b, a), sub(p, a)), self.n) < -tol * math.dist(a, b):
                return False
        return True


class Brush:
    __slots__ = ('index', 'name', 'group', 'entity', 'faces', 'lo', 'hi')

    def contains(self, p, eps=0.01):
        """p strictly inside the solid (by eps map units)."""
        return all(dot(f.n, p) - f.d < -eps for f in self.faces)


class MapData:
    def __init__(self):
        self.entities = []   # dicts of key/values, with '_brushes' (list of Brush)
        self.brushes = []

    def points(self, classname):
        """Origins (map units) of point entities of one class."""
        out = []
        for e in self.entities:
            if e.get('classname') == classname and 'origin' in e:
                out.append(tuple(float(v) for v in e['origin'].split()))
        return out

    def faces_at(self, p, tol=1.0):
        """Every brush face whose polygon passes through p (map units)."""
        return [f for b in self.brushes
                if b.lo[0] - tol <= p[0] <= b.hi[0] + tol and b.lo[1] - tol <= p[1] <= b.hi[1] + tol
                and b.lo[2] - tol <= p[2] <= b.hi[2] + tol
                for f in b.faces if f.contains(p, tol)]


def _polygon(face, faces):
    """The face's polygon: a huge square on its plane, clipped by every other plane of the brush."""
    n = face.n
    ref = (0.0, 0.0, 1.0) if abs(n[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = norm(cross(ref, n))
    v = cross(n, u)
    c = mul(n, face.d)
    big = 1e5
    poly = [add(c, add(mul(u, su * big), mul(v, sv * big))) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for other in faces:
        if other is face:
            continue
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            fa, fb = dot(other.n, a) - other.d, dot(other.n, b) - other.d
            if fa <= 1e-6:
                out.append(a)
            if (fa < -1e-6 < fb) or (fb < -1e-6 < fa):
                out.append(add(a, mul(sub(b, a), fa / (fa - fb))))
        poly = out
        if len(poly) < 3:
            return []
    # Drop points closer than a hundredth of a unit (repeated by clipping through a vertex).
    clean = []
    for p in poly:
        if not clean or math.dist(p, clean[-1]) > 0.01:
            clean.append(p)
    if len(clean) > 1 and math.dist(clean[0], clean[-1]) <= 0.01:
        clean.pop()
    return clean if len(clean) >= 3 else []


SNAP = 1.0          # map units: func_godot's default _vertex_merge_distance of 0.03125 m


def load(path):
    m = MapData()
    groups = {}
    entity = None
    brush_faces = None
    name = None
    depth = 0
    with open(path, encoding='utf-8') as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            if line.startswith('//'):
                if depth == 1:
                    name = line[2:].strip()
                continue
            if line == '{':
                depth += 1
                if depth == 1:
                    entity = {'_brushes': []}
                    name = None
                elif depth == 2:
                    brush_faces = []
                continue
            if line == '}':
                if depth == 2:
                    b = Brush()
                    b.index, b.name, b.entity, b.faces = len(m.brushes), name, entity, brush_faces
                    entity['_brushes'].append(b)
                    m.brushes.append(b)
                    name = None
                elif depth == 1:
                    m.entities.append(entity)
                    if entity.get('_tb_type') in ('_tb_group', '_tb_layer'):
                        groups[entity.get('_tb_id')] = entity.get('_tb_name', '')
                depth -= 1
                continue
            if depth == 1:
                kv = _KV.match(line)
                if kv:
                    entity[kv.group(1)] = kv.group(2)
            elif depth == 2:
                f = _FACE.match(line)
                if f:
                    v = [float(x) for x in f.groups()[:9]]
                    p1, p2, p3 = tuple(v[0:3]), tuple(v[3:6]), tuple(v[6:9])
                    n = norm(cross(sub(p3, p1), sub(p2, p1)))
                    face = Face(n, dot(n, p1), f.group(10))
                    face.uv = line[f.end():].strip()          # the texture's axes, offsets, rotation and scale
                    brush_faces.append(face)
    for b in m.brushes:
        e = b.entity
        if e.get('_tb_type') in ('_tb_group', '_tb_layer'):
            b.group = e.get('_tb_name', '')
        elif '_tb_group' in e:
            b.group = groups.get(e['_tb_group'], e['_tb_group'])
        else:
            b.group = e.get('classname', '')
        for f in b.faces:
            f.brush = b
            f.pts = _polygon(f, b.faces)
            if f.pts and SNAP:
                # func_godot snaps every generated vertex to its merge distance (1/32 m, one map unit): offsets finer
                # than that vanish in the build, so two faces a centimetre apart there ARE coplanar.
                f.pts = [tuple(round(v / SNAP) * SNAP for v in p) for p in f.pts]
                f.d = sum(dot(f.n, p) for p in f.pts) / len(f.pts)
        b.faces = [f for f in b.faces if f.pts]
        pts = [p for f in b.faces for p in f.pts] or [(0.0, 0.0, 0.0)]
        b.lo = tuple(min(p[i] for p in pts) for i in range(3))
        b.hi = tuple(max(p[i] for p in pts) for i in range(3))
    return m
