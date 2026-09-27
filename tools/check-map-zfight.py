"""Find z-fighting in a map: faces of DIFFERENT brushes that lie on the same plane, face the same way, overlap, and
can be seen by the player.

Coplanar overlaps are everywhere in a generated map, but most are hidden: the undersides of stacked slabs, the
outsides of exterior walls, faces buried in another solid. So the check first works out where the player can be:
it voxelises the solids at 0.25 m and floods the air from the route markers (rb_route; else info_player_start).
An overlap counts only where the space just in front of it is that reachable air.

    python tools/check-map-zfight.py RedBreach/maps/freight_v2_01.map
    python tools/check-map-zfight.py <map> --limit 80 --json playtests/zfight.json

Reads the map as edited (see mapkit), so it covers hand edits as well as generated brushes.
"""
from pathlib import Path
import json
import math
import re
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapkit as K
import polykit as P

CELL = 8.0            # 0.25 m in map units
GROW = 4.0            # solids are thickened by half a cell, so a hairline contact (two walls meeting at a corner) seals
PLANE_TOL = 0.128     # 4 mm: nearer than this counts as the same plane (it still flickers)
MIN_AREA = 0.01       # m2
FREE, SOLID, AIR = 0, 1, 2
_RUN = re.compile(rb'\x00+')
_BLOCK = re.compile(rb'[^\x00]')


class Grid:
    def __init__(self, brushes, pad=16.0):
        lo = [min(b.lo[i] for b in brushes) - pad for i in range(3)]
        hi = [max(b.hi[i] for b in brushes) + pad for i in range(3)]
        self.o = [math.floor(v / CELL) * CELL for v in lo]
        self.n = [int(math.ceil((hi[i] - self.o[i]) / CELL)) for i in range(3)]
        nx, ny, nz = self.n
        self.state = bytearray(nx * ny * nz)

    def index(self, p):
        i = [int(math.floor((p[a] - self.o[a]) / CELL)) for a in range(3)]
        if not all(0 <= i[a] < self.n[a] for a in range(3)):
            return -1
        return (i[2] * self.n[1] + i[1]) * self.n[0] + i[0]

    def at(self, p):
        k = self.index(p)
        return SOLID if k < 0 else self.state[k]

    def rasterise(self, b):
        """Mark cells whose centre is inside the brush, a row along x at a time."""
        nx, ny, nz = self.n
        ox, oy, oz = self.o
        j0 = max(0, int(math.floor((b.lo[1] - GROW - oy) / CELL)))
        j1 = min(ny - 1, int(math.floor((b.hi[1] + GROW - oy) / CELL)))
        k0 = max(0, int(math.floor((b.lo[2] - GROW - oz) / CELL)))
        k1 = min(nz - 1, int(math.floor((b.hi[2] + GROW - oz) / CELL)))
        planes = [(f.n[0], f.n[1], f.n[2], f.d + GROW) for f in b.faces]
        for k in range(k0, k1 + 1):
            zc = oz + (k + 0.5) * CELL
            for j in range(j0, j1 + 1):
                yc = oy + (j + 0.5) * CELL
                xl, xh = -1e18, 1e18
                for a, bb, c, d in planes:
                    rhs = d - bb * yc - c * zc
                    if abs(a) < 1e-9:
                        if rhs < 0:
                            xl, xh = 1, 0
                            break
                    elif a > 0:
                        xh = min(xh, rhs / a)
                    else:
                        xl = max(xl, rhs / a)
                if xl > xh:
                    continue
                i0 = max(0, int(math.ceil((xl - ox) / CELL - 0.5)))
                i1 = min(nx - 1, int(math.floor((xh - ox) / CELL - 0.5)))
                if i1 >= i0:
                    row = (k * ny + j) * nx
                    self.state[row + i0:row + i1 + 1] = b'\x01' * (i1 - i0 + 1)

    def flood(self, seeds):
        """Span flood fill of the free cells reachable from the seeds (6-connected)."""
        nx, ny, nz = self.n
        s = self.state
        stack = [k for k in (self.index(p) for p in seeds) if k >= 0 and s[k] == FREE]
        filled = 0
        while stack:
            idx = stack.pop()
            if s[idx] != FREE:
                continue
            row = idx - idx % nx
            end = row + nx
            m = _BLOCK.search(s, idx, end)
            r = (m.start() if m else end) - 1
            l = max(row - 1, s.rfind(b'\x01', row, idx), s.rfind(b'\x02', row, idx)) + 1
            s[l:r + 1] = b'\x02' * (r - l + 1)
            filled += r - l + 1
            k, j = divmod(row // nx, ny)
            for nj, nk in ((j - 1, k), (j + 1, k), (j, k - 1), (j, k + 1)):
                if 0 <= nj < ny and 0 <= nk < nz:
                    nrow = (nk * ny + nj) * nx
                    for run in _RUN.finditer(s, nrow + (l - row), nrow + (r - row) + 1):
                        stack.append(run.start())
        return filled


    def leak(self, seeds):
        """Like Quake's pointfile: the shortest free path from a seed to the outside of the grid, as a list of cell
        indices from the seed outward, or None when the level is sealed. Call before flood()."""
        from array import array
        from collections import deque
        nx, ny, nz = self.n
        s = self.state
        parent = array('i', [-1]) * len(s)
        queue = deque()
        for p in seeds:
            k = self.index(p)
            if k >= 0 and s[k] == FREE and parent[k] == -1:
                parent[k] = k
                queue.append(k)
        while queue:
            k = queue.popleft()
            i = k % nx
            j = (k // nx) % ny
            z = k // (nx * ny)
            if i in (0, nx - 1) or j in (0, ny - 1) or z in (0, nz - 1):
                path = [k]
                while parent[path[-1]] != path[-1]:
                    path.append(parent[path[-1]])
                return path[::-1]
            for d, ok in ((1, i < nx - 1), (-1, i > 0), (nx, j < ny - 1), (-nx, j > 0),
                          (nx * ny, z < nz - 1), (-nx * ny, z > 0)):
                q = k + d
                if ok and s[q] == FREE and parent[q] == -1:
                    parent[q] = k
                    queue.append(q)
        return None


    def centre(self, c):
        nx, ny = self.n[0], self.n[1]
        return K.plan((self.o[0] + (c % nx + 0.5) * CELL, self.o[1] + ((c // nx) % ny + 0.5) * CELL,
                       self.o[2] + (c // (nx * ny) + 0.5) * CELL))

    def plug(self, path, reach=4, skip=2):
        """Fill a tube round a leak path (not its first cells, by the seed) so the next trace finds another hole."""
        nx, ny, nz = self.n
        for c in path[skip:]:
            ci, cj, cz = c % nx, (c // nx) % ny, c // (nx * ny)
            for z in range(max(0, cz - reach), min(nz, cz + reach + 1)):
                for j in range(max(0, cj - reach), min(ny, cj + reach + 1)):
                    row = (z * ny + j) * nx
                    for i in range(max(0, ci - reach), min(nx, ci + reach + 1)):
                        if self.state[row + i] == FREE:
                            self.state[row + i] = SOLID


def facing(n):
    x, y, h = n[1], -n[0], n[2]
    if h > 0.7:
        return 'up'
    if h < -0.7:
        return 'down'
    return {(1, 0): 'east', (-1, 0): 'west', (0, 1): 'north', (0, -1): 'south'}.get(
        (round(x), round(y)), f'({x:.2f}, {y:.2f}, {h:.2f})')


def main():
    import argparse
    ap = argparse.ArgumentParser(description='Visible z-fighting in a .map')
    ap.add_argument('map', nargs='?', default='RedBreach/maps/freight_v2_01.map')
    ap.add_argument('--limit', type=int, default=40)
    ap.add_argument('--json')
    ap.add_argument('--leaks', type=int, default=25, help='trace at most this many leaks')
    opts = ap.parse_args()
    path = Path(opts.map)
    limit = opts.limit
    t0 = time.time()
    m = K.load(path)
    brushes = [b for b in m.brushes if b.faces]
    grid = Grid(brushes)
    for b in brushes:
        grid.rasterise(b)
    tr = time.time()
    seeds = [K.add(p, (0, 0, 32)) for p in m.points('rb_route')] or [K.add(p, (0, 0, 32)) for p in m.points('info_player_start')]
    # Leaks: trace a way out, plug it, trace again, so every hole is listed and the air flood stays inside.
    leaks = []
    while len(leaks) < opts.leaks:
        cells = grid.leak(seeds)
        if not cells:
            break
        trail = [grid.centre(c) for c in cells]
        # Keep the corners of the trail, so it reads as a route out through the hole.
        pts = [trail[0]]
        for a, b, c in zip(trail, trail[1:], trail[2:]):
            if any(abs((b[i] - a[i]) - (c[i] - b[i])) > 1e-6 for i in range(3)):
                pts.append(b)
        pts.append(trail[-1])
        leaks.append([[round(v, 2) for v in q] for q in pts])
        print(f'LEAK {len(leaks)}: from ({pts[0][0]:.2f}, {pts[0][1]:.2f}, h {pts[0][2]:.2f}), {len(cells) * 0.25:.1f} m out: '
              + ' -> '.join(f'({x:.2f}, {y:.2f}, h {h:.2f})' for x, y, h in pts[1:9]) + (' ...' if len(pts) > 9 else ''))
        grid.plug(cells)
    if not leaks:
        print('LEAK: none, the level is sealed')
    air = grid.flood(seeds)
    t1 = time.time()
    # Spatial hash of brushes, 4 m buckets, for the "buried in a solid" test.
    bucket = {}
    for b in brushes:
        for x in range(int(b.lo[0] // 128), int(b.hi[0] // 128) + 1):
            for y in range(int(b.lo[1] // 128), int(b.hi[1] // 128) + 1):
                for z in range(int(b.lo[2] // 128), int(b.hi[2] // 128) + 1):
                    bucket.setdefault((x, y, z), []).append(b)

    def buried(p):
        """Inside a brush or touching one (within 0.5 units): a point on the seam between two stacked brushes (a wall's
        plinth band and the band above it) is inside neither, and a walk must not slip through the wall along it."""
        for b in bucket.get((int(p[0] // 128), int(p[1] // 128), int(p[2] // 128)), ()):
            if b.contains(p, -0.5):
                return True
        return False

    def visible(p, n):
        """Walk out from the face in the TRUE geometry (exact point-in-brush, no thickening) until the walk reaches the
        flooded air: seen. Hitting a solid first (a face buried in, or right behind, another brush): hidden. The grid is
        thickened to seal hairline contacts, which would otherwise hide a face tucked into a corner (the S1 landing)."""
        for t in (1.6, 5.6, 9.6, 13.6, 17.6, 21.6, 25.6, 29.6):      # 0.05 m to 0.925 m, every 0.125 m
            q = K.add(p, K.mul(n, t))
            if buried(q):
                return False
            if t > 8.0 and grid.at(q) == AIR:
                return True
        return False

    by_normal = {}
    for b in brushes:
        for f in b.faces:
            by_normal.setdefault(tuple(round(v, 3) for v in f.n), []).append(f)
    hits = []
    pairs = 0
    for key, fs in by_normal.items():
        fs.sort(key=lambda f: f.d)
        ax = max(range(3), key=lambda i: abs(key[i]))
        keep = [i for i in range(3) if i != ax]
        flat = {id(f): P.ccw([(p[keep[0]], p[keep[1]]) for p in f.pts]) for f in fs}
        box = {id(f): (min(p[keep[0]] for p in f.pts), max(p[keep[0]] for p in f.pts),
                       min(p[keep[1]] for p in f.pts), max(p[keep[1]] for p in f.pts)) for f in fs}
        for i, a in enumerate(fs):
            ba = box[id(a)]
            for b in fs[i + 1:]:
                if b.d - a.d > PLANE_TOL:
                    break
                if a.brush is b.brush:
                    continue
                bb = box[id(b)]
                if bb[0] >= ba[1] or ba[0] >= bb[1] or bb[2] >= ba[3] or ba[2] >= bb[3]:
                    continue
                inter = P.intersect(flat[id(a)], flat[id(b)])
                if len(inter) < 3:
                    continue
                area = abs(P.area(inter)) / abs(a.n[ax]) / K.UNITS ** 2
                if area < MIN_AREA:
                    continue
                pairs += 1
                cx = sum(q[0] for q in inter) / len(inter)
                cy = sum(q[1] for q in inter) / len(inter)
                samples = [(cx, cy)] + [(cx + (q[0] - cx) * 0.75, cy + (q[1] - cy) * 0.75) for q in inter[:12]]
                seen = 0
                for sx, sy in samples:
                    p3 = [0.0, 0.0, 0.0]
                    p3[keep[0]], p3[keep[1]] = sx, sy
                    p3[ax] = (a.d - a.n[keep[0]] * sx - a.n[keep[1]] * sy) / a.n[ax]
                    seen += visible(tuple(p3), a.n)
                if seen:
                    c3 = [0.0, 0.0, 0.0]
                    c3[keep[0]], c3[keep[1]] = cx, cy
                    c3[ax] = (a.d - a.n[keep[0]] * cx - a.n[keep[1]] * cy) / a.n[ax]
                    hits.append({'area': round(area * seen / len(samples), 2),
                                 'at': [round(v, 2) for v in K.plan(c3)], 'facing': facing(a.n),
                                 'gap_mm': round((b.d - a.d) / K.UNITS * 1000, 1),
                                 'a': {'brush': a.brush.index, 'name': a.brush.name, 'group': a.brush.group, 'texture': a.texture},
                                 'b': {'brush': b.brush.index, 'name': b.brush.name, 'group': b.brush.group, 'texture': b.texture}})
    hits.sort(key=lambda h: -h['area'])
    t2 = time.time()
    print(f'ZFIGHT: {path.name}: {len(brushes)} brushes; air {air * 0.015625:.0f} m3 from {len(seeds)} seeds; '
          f'{pairs} coplanar overlaps, {len(hits)} VISIBLE, {sum(h["area"] for h in hits):.1f} m2 '
          f'({tr - t0:.1f} s voxels, {t1 - tr:.1f} s flood, {t2 - t1:.1f} s faces)')
    # Which kinds of brush fight each other: the generator bugs, largest first.
    kinds = {}
    for h in hits:
        ka = re.sub(r'^\S+\s', '', h['a']['name'] or '?')
        kb = re.sub(r'^\S+\s', '', h['b']['name'] or '?')
        k = ' / '.join(sorted((ka, kb)))
        e = kinds.setdefault(k, [0, 0.0])
        e[0] += 1
        e[1] += h['area']
    print('  by kind (count, m2):')
    for k, (c, a) in sorted(kinds.items(), key=lambda kv: -kv[1][1])[:25]:
        print(f'    {c:4d} {a:7.1f}  {k}')
    print(f'  largest {min(limit, len(hits))}:')
    for h in hits[:limit]:
        x, y, z = h['at']
        gap = f' gap {h["gap_mm"]} mm' if h['gap_mm'] else ''
        print(f'    {h["area"]:6.2f} m2 {h["facing"]:>5} at plan ({x:.2f}, {y:.2f}, h {z:.2f}){gap}: '
              f'{h["a"]["name"]} [{h["a"]["group"]}] / {h["b"]["name"]} [{h["b"]["group"]}]')
    if opts.json:
        Path(opts.json).parent.mkdir(parents=True, exist_ok=True)
        Path(opts.json).write_text(json.dumps({'leaks': leaks, 'zfight': hits}, indent=1), encoding='utf-8', newline='\n')
        print('  written', opts.json)


if __name__ == '__main__':
    main()
