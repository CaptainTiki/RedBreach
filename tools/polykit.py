"""Small 2D polygon kit for turning plan polygons into convex brushes.

Brushes must be convex, but rooms, pits and walls with openings are not. This
module decomposes simple polygons into convex pieces and subtracts convex
holes from convex pieces, so any plan shape (or wall elevation with door and
corridor cut-outs) becomes a list of convex polygons ready to extrude.

Polygons are lists of (x, y) tuples. Everything is exact enough for a
0.125 m grid; tiny slivers (area below AREA_EPS) are dropped.
"""
import math

EPS = 1e-9
AREA_EPS = 1e-4


def area(poly):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1])) / 2


def ccw(poly):
    """The polygon in counter-clockwise order, with repeated points removed."""
    out = []
    for p in poly:
        if not out or math.dist(p, out[-1]) > 1e-9:
            out.append((float(p[0]), float(p[1])))
    if len(out) > 1 and math.dist(out[0], out[-1]) <= 1e-9:
        out.pop()
    return out if area(out) >= 0 else out[::-1]


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def is_convex(poly):
    n = len(poly)
    return n >= 3 and all(cross(poly[i], poly[(i + 1) % n], poly[(i + 2) % n]) >= -1e-9 for i in range(n))


def clean(poly):
    """Drop collinear and duplicate points."""
    pts = [p for i, p in enumerate(poly) if math.dist(p, poly[i - 1]) > 1e-7]
    changed = True
    while changed and len(pts) > 3:
        changed = False
        for i in range(len(pts)):
            if abs(cross(pts[i - 1], pts[i], pts[(i + 1) % len(pts)])) < 1e-9:
                pts.pop(i)
                changed = True
                break
    return pts


def clip(poly, a, b, c):
    """Keep the part of a convex polygon with a*x + b*y <= c (Sutherland-Hodgman)."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fp <= EPS:
            out.append(p)
        if (fp < -EPS < fq) or (fq < -EPS < fp):
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return clean(out) if len(out) >= 3 else []


def edges_halfplanes(convex):
    """Inside half-planes (a, b, c) of a CCW convex polygon: a*x + b*y <= c."""
    hp = []
    n = len(convex)
    for i in range(n):
        p, q = convex[i], convex[(i + 1) % n]
        # Inside is to the left of p->q; the outward normal is (dy, -dx).
        a, b = q[1] - p[1], -(q[0] - p[0])
        hp.append((a, b, a * p[0] + b * p[1]))
    return hp


def intersect(p, c):
    """Convex p intersected with convex c."""
    out = list(p)
    for a, b, d in edges_halfplanes(ccw(c)):
        out = clip(out, a, b, d)
        if not out:
            return []
    return out


def subtract(p, c):
    """Convex p minus convex c, as a list of convex pieces."""
    c = ccw(c)
    if not intersect(p, c) or abs(area(intersect(p, c))) < AREA_EPS:
        return [p]
    pieces = []
    rest = list(p)
    for a, b, d in edges_halfplanes(c):
        outside = clip(rest, -a, -b, -d)
        if outside and area(ccw(outside)) > AREA_EPS:
            pieces.append(ccw(outside))
        rest = clip(rest, a, b, d)
        if not rest:
            break
    return pieces


def subtract_all(pieces, holes):
    """Convex pieces minus convex holes."""
    for h in holes:
        out = []
        for p in pieces:
            out += subtract(p, h)
        pieces = out
    return [p for p in pieces if area(ccw(p)) > AREA_EPS]


def _point_in_triangle(p, a, b, c):
    return cross(a, b, p) >= -1e-12 and cross(b, c, p) >= -1e-12 and cross(c, a, p) >= -1e-12


def triangulate(poly):
    """Ear clipping of a simple CCW polygon."""
    pts = ccw(clean(ccw(poly)))
    idx = list(range(len(pts)))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        n = len(idx)
        for k in range(n):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % n]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if cross(a, b, c) <= 1e-12:
                continue
            if any(_point_in_triangle(pts[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append([i0, i1, i2])
            idx.pop(k)
            break
        else:
            raise ValueError('triangulate: no ear found (self-intersecting polygon?)')
    tris.append(idx[:])
    return pts, tris


def convex_parts(poly):
    """Hertel-Mehlhorn: triangulate, then merge neighbours while the union stays convex."""
    p = ccw(clean(ccw(poly)))
    if is_convex(p):
        return [p]
    pts, tris = triangulate(p)
    parts = [list(t) for t in tris]
    merged = True
    while merged:
        merged = False
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                a, b = parts[i], parts[j]
                shared = [(a[k], a[(k + 1) % len(a)]) for k in range(len(a))
                          if (a[(k + 1) % len(a)], a[k]) in [(b[m], b[(m + 1) % len(b)]) for m in range(len(b))]]
                if not shared:
                    continue
                u, v = shared[0]
                ka = a.index(u)
                kb = b.index(v)
                # Walk a from v round to u, then b from u round to v.
                seq = a[ka + 1:] + a[:ka + 1]            # starts at v, ends at u
                ib = b.index(u)
                tail = b[ib + 1:] + b[:ib + 1]           # starts after u, ends at u
                tail = tail[:tail.index(v)]              # up to before v
                cand = seq + tail
                poly_c = [pts[k] for k in cand]
                if is_convex(poly_c):
                    parts[i] = cand
                    parts.pop(j)
                    merged = True
                    break
            if merged:
                break
    return [clean([pts[k] for k in part]) for part in parts]


def offset_segment(a, b, d):
    """The segment a-b shifted by d to its left."""
    L = math.dist(a, b)
    nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
    return (a[0] + nx * d, a[1] + ny * d), (b[0] + nx * d, b[1] + ny * d)


def inside(pt, poly):
    x, y = pt
    c = False
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
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


def overlap_1d(a0, a1, b0, b1):
    lo, hi = max(min(a0, a1), min(b0, b1)), min(max(a0, a1), max(b0, b1))
    return (lo, hi) if hi - lo > 1e-6 else None


if __name__ == '__main__':
    # Self-test: an L decomposes into convex pieces of the same total area, and a
    # square minus a centred hole keeps the ring's area.
    L = [(0, 0), (4, 0), (4, 1), (1, 1), (1, 3), (0, 3)]
    parts = convex_parts(L)
    assert all(is_convex(ccw(p)) for p in parts)
    assert abs(sum(area(ccw(p)) for p in parts) - area(ccw(L))) < 1e-9
    ring = subtract_all([[(0, 0), (4, 0), (4, 4), (0, 4)]], [[(1, 1), (3, 1), (3, 3), (1, 3)]])
    assert abs(sum(area(ccw(p)) for p in ring) - 12) < 1e-9
    zig = [(-29, 10), (-22.5, 10), (-22.5, 16.5), (-26, 16.5), (-26, 20.5), (-22.5, 20.5), (-22.5, 28.5), (-25.5, 28.5),
           (-25.5, 22.5), (-29, 22.5)]
    parts = convex_parts(zig)
    assert abs(sum(area(ccw(p)) for p in parts) - area(ccw(zig))) < 1e-9, parts
    print('POLYKIT: ok;', len(parts), 'pieces for the stairwell zigzag')
