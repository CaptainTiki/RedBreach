"""Brush-writing kit for Red Breach TrenchBroom maps (Valve 220 format).

Every brush is the convex hull of a point set, given in Godot metres as
(x, y, z) with y up. Writing uses the project convention of 32 map units per
metre, with map axes (godot z, godot x, godot y).

The kit is meant to be reusable beyond the style lab:

- ``hull(points, tex)`` accepts any convex point set. Faces are found by plane
  enumeration, so wedges, mitred ends and sloped walls need no special cases.
- ``tex`` is either a texture name or ``fn(normal, centre) -> name``, both in
  Godot coordinates, so a single brush can put a hazard reveal on its
  opening faces and a frame texture on its caps.
- UVs follow ``docs/blockout-textures.md``: anchored to the world origin, with
  unit tangent axes, including on slopes. On a wall, U runs horizontally to the
  viewer's right and V runs down the face. A floor or ceiling uses the world X/Z
  axes.
- Brushes can be collected into TrenchBroom groups, which func_godot merges
  back into worldspawn. The groups only exist to make hand-editing easier.

Scale: at ``scale=1.0`` one texel covers one map unit, which is 32 px/m (the
same density Quake uses). A 64 px texture therefore spans 2 m.
"""
from itertools import combinations
import math

UNITS = 32
EPS = 1e-6


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _len(a): return math.sqrt(_dot(a, a))
def _norm(a):
    n = _len(a)
    return (a[0] / n, a[1] / n, a[2] / n)


def to_map(p):
    """Godot metres (x, y-up, z) -> map units (godot z, godot x, godot y)."""
    return (p[2] * UNITS, p[0] * UNITS, p[1] * UNITS)


def map_to_godot_dir(v):
    return (v[1], v[2], v[0])


def _fmt(v):
    r = round(v, 4)
    if abs(r - round(r)) < 1e-9:
        return str(int(round(r)))
    return f'{r:.4f}'.rstrip('0').rstrip('.')


class Map:
    def __init__(self, textures=()):
        self.world = []           # brush strings in worldspawn
        self.groups = []          # (name, [brush strings])
        self.entities = []        # raw entity strings
        self.textures = list(textures)
        self._group = None
        self.count = 0
        self.tally = {}

    # --- grouping -----------------------------------------------------------
    def group(self, name):
        self._group = (name, [])
        self.groups.append(self._group)
        return self

    def ungroup(self):
        self._group = None

    # --- brushes ------------------------------------------------------------
    def hull(self, points, tex, name='', scale=1.0, offset=(0, 0), anchor=None, tally='misc'):
        """Convex hull of ``points`` (Godot metres). Returns True if written.

        ``anchor=(godot_point, texel_v)`` shifts V on every face so the texture
        row ``texel_v`` lands on that point. It is how a painted band inside a
        texture is pinned to a plinth foot on a slope."""
        pts = []
        for p in points:
            q = to_map(p)
            if not any(_len(_sub(q, r)) < 1e-4 for r in pts):
                pts.append(q)
        if len(pts) < 4:
            raise ValueError(f'brush {name!r}: fewer than four distinct points')
        centre = tuple(sum(p[i] for p in pts) / len(pts) for i in range(3))
        planes = []
        for a, b, c in combinations(pts, 3):
            n = _cross(_sub(b, a), _sub(c, a))
            if _len(n) < 1e-6:
                continue
            n = _norm(n)
            d = _dot(n, a)
            side = [_dot(n, p) - d for p in pts]
            if all(s <= 1e-4 for s in side):
                pass
            elif all(s >= -1e-4 for s in side):
                n = (-n[0], -n[1], -n[2]); d = -d
            else:
                continue
            if any(_dot(n, m) > 1 - 1e-7 and abs(d - e) < 1e-3 for m, e in planes):
                continue
            planes.append((n, d))
        if len(planes) < 4:
            raise ValueError(f'brush {name!r}: degenerate hull ({len(planes)} planes)')
        lines = [f'// {name}' if name else '// brush', '{']
        for n, d in planes:
            on = [p for p in pts if abs(_dot(n, p) - d) < 1e-3]
            fc = tuple(sum(p[i] for p in on) / len(on) for i in range(3))
            # In-plane basis, then sort points by angle so the three chosen
            # points are well spread and never collinear.
            ref = (0, 0, 1) if abs(n[2]) < 0.9 else (1, 0, 0)
            e1 = _norm(_cross(n, ref)); e2 = _cross(n, e1)
            on.sort(key=lambda p: math.atan2(_dot(_sub(p, fc), e2), _dot(_sub(p, fc), e1)))
            m = len(on)
            a, b, c = on[0], on[m // 3], on[(2 * m) // 3]
            if _len(_cross(_sub(b, a), _sub(c, a))) < 1e-3:
                raise ValueError(f'brush {name!r}: collinear face points')
            # Project convention (see the lab bootstraps): cross(b-a, c-a) points
            # INTO the brush.
            if _dot(_cross(_sub(b, a), _sub(c, a)), _sub(centre, a)) < 0:
                b, c = c, b
            gn = map_to_godot_dir(n)
            gc = map_to_godot_dir(tuple(v / UNITS for v in fc))
            texture = tex(gn, gc) if callable(tex) else tex
            u, v = _uv_axes(n)
            s = scale(texture) if callable(scale) else scale
            ox, oy = offset
            if anchor is not None:
                ap = to_map(anchor[0])
                oy = anchor[1] - _dot(ap, v) / s
            lines.append(' '.join('( ' + ' '.join(_fmt(k) for k in p) + ' )' for p in (a, b, c))
                         + f' {texture} [ {_fmt(u[0])} {_fmt(u[1])} {_fmt(u[2])} {_fmt(ox)} ]'
                         + f' [ {_fmt(v[0])} {_fmt(v[1])} {_fmt(v[2])} {_fmt(oy)} ] 0 {_fmt(s)} {_fmt(s)}')
        lines.append('}')
        text = '\n'.join(lines)
        (self._group[1] if self._group else self.world).append(text)
        self.count += 1
        self.tally[tally] = self.tally.get(tally, 0) + 1
        return True

    def box(self, x0, x1, y0, y1, z0, z1, tex, name='', **kw):
        xs, ys, zs = sorted((x0, x1)), sorted((y0, y1)), sorted((z0, z1))
        return self.hull([(x, y, z) for x in xs for y in ys for z in zs], tex, name, **kw)

    def prism_z(self, poly, z0, z1, tex, name='', **kw):
        """Cross-section polygon in the XY plane, extruded along Godot Z."""
        return self.hull([(x, y, z) for x, y in poly for z in (z0, z1)], tex, name, **kw)

    def prism_y(self, poly, y0, y1, tex, name='', **kw):
        """Plan polygon in the XZ plane, extruded vertically."""
        return self.hull([(x, y, z) for x, z in poly for y in (y0, y1)], tex, name, **kw)

    def entity(self, classname, props):
        body = ['{', f'"classname" "{classname}"'] + [f'"{k}" "{v}"' for k, v in props.items()] + ['}']
        self.entities.append('\n'.join(body))

    # --- output -------------------------------------------------------------
    def text(self, header=''):
        out = ['// Game: Red Breach', '// Format: Valve']
        if header:
            out += ['// ' + line for line in header.splitlines()]
        out += ['{', '"classname" "worldspawn"', '"_tb_def" "builtin:FuncGodot.fgd"']
        if self.textures:
            out.append(f'"_tb_textures" "{";".join(self.textures)}"')
        out += self.world
        out.append('}')
        for i, (name, brushes) in enumerate(self.groups, start=1):
            if not brushes:
                continue
            out += ['{', '"classname" "func_group"', '"_tb_type" "_tb_group"',
                    f'"_tb_name" "{name}"', f'"_tb_id" "{i}"']
            out += brushes
            out.append('}')
        out += self.entities
        return '\n'.join(out) + '\n'


def _uv_axes(n):
    """Unit U/V axes in map coordinates for a face with outward normal n."""
    if abs(n[2]) > 0.75:
        return (1, 0, 0), (0, -1, 0)
    up = (0, 0, 1)
    view = (-n[0], -n[1], -n[2])
    u = _cross(view, up)
    u = _norm(u)
    v = _norm(_cross(u, n))
    if v[2] > 0:
        v = (-v[0], -v[1], -v[2])
    return u, v
