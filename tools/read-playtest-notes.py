"""Read a playtest notes session (written in game by the PlaytestNotes autoload: Q note, Z z-fight mark).

For every note: the text, when in the run it was made, where the player stood and which room that is, what the ray
hit, and - from the map as it is now - every brush face at the hit point, with its // name and TrenchBroom group.
Two same-facing faces of different brushes at the point is z-fighting, and says which two brushes to fix.

    python tools/read-playtest-notes.py                  # the newest session
    python tools/read-playtest-notes.py playtests/freight_v2/2026-09-26_20-15-02
    python tools/read-playtest-notes.py --all            # every session, oldest first

There are no screenshots: each note keeps the camera's transform and field of view. To see what the player saw (the map
as it is now), render it: tools/view-playtest-note.ps1 [-Session <folder>] [-Note <n>].
"""
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapkit as K
import polykit as P

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'RedBreach'


def plan_rooms(scene):
    """Plan rooms for scenes that have a plan module, for 'which room' answers."""
    if 'freight_v2' in scene:
        import freight_v2 as F
        rooms = [(k, n, poly, fl) for k, n, poly, fl, _ in F.ROOMS]
        corridors = [(k, n, path) for k, n, _, path, _, _ in F.CORRIDORS]
        return rooms, corridors
    return [], []


def where(pt, rooms, corridors):
    if pt is None:
        return ''
    x, y, h = pt
    inside = [(k, n, fl) for k, n, poly, fl in rooms if P.inside((x, y), P.ccw(poly))]
    if inside:
        k, n, _ = min(inside, key=lambda r: abs(r[2] - h) if r[2] <= h + 0.5 else 99 + r[2])
        return f'{k} {n}'
    best = None
    for k, n, path in corridors:
        for a, b in zip(path, path[1:]):
            d = P.seg_dist((x, y), a, b)
            if d < 4 and (best is None or d < best[0]):
                best = (d, f'{k} {n}')
    return best[1] if best else 'outside the plan'


def faces_report(m, hit):
    """Brush faces through the hit point, and whether two of them fight."""
    p = K.from_godot(hit['point'])
    n = K.godot_dir_to_map(hit['normal'])
    faces = m.faces_at(p, tol=1.0)
    lines = []
    same = [f for f in faces if K.dot(f.n, n) > 0.99]
    for f in sorted(faces, key=lambda f: -K.dot(f.n, n)):
        tag = 'facing the ray' if K.dot(f.n, n) > 0.99 else ('back to back' if K.dot(f.n, n) < -0.99 else 'edge')
        lines.append(f'      brush {f.brush.index}: {f.brush.name} [{f.brush.group}] {f.texture} ({tag})')
    fight = len({f.brush.index for f in same}) >= 2
    return lines, fight


def session_report(folder):
    rows = [json.loads(line) for line in (folder / 'notes.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    head = next((r for r in rows if r.get('type') == 'session'), {})
    scene = head.get('scene', '')
    print(f'== {folder.relative_to(ROOT) if folder.is_relative_to(ROOT) else folder}  {scene}  v{head.get("version", "?")}  '
          f'started {head.get("started", "?")}')
    maps = []
    for mp in head.get('maps', []):
        path = PROJECT / mp['path'].replace('res://', '')
        now = hashlib.md5(path.read_bytes()).hexdigest() if path.exists() else None
        changed = now != mp.get('md5')
        print(f'   map {mp["path"]}' + ('  (CHANGED since this run: brush numbers may have moved)' if changed else ''))
        if path.exists():
            maps.append(K.load(path))
    rooms, corridors = plan_rooms(scene)
    fights = 0
    notes = [r for r in rows if r.get('type') == 'note']
    for r in rows:
        kind = r.get('type')
        if kind in ('finish', 'restart'):
            print(f'   -- {kind} at {r.get("elapsed", "?")} s, {r.get("distance", "?")} m')
            continue
        if kind != 'note':
            continue
        run = r.get('run') or {}
        t = f'{run.get("elapsed", 0):.0f} s' if run else ''
        print(f'\n#{r["n"]} {t}  "{r.get("note", "")}"')
        at = r.get('plan_player') or r.get('plan_camera')
        print(f'   {"player" if r.get("plan_player") else "camera"} at plan ({at[0]:.2f}, {at[1]:.2f}, h {at[2]:.2f}) '
              f'in {where(at, rooms, corridors)}')
        cam = r.get('camera')
        if isinstance(cam, dict):
            px, py, pz = cam['position']
            rx, ry, rz = cam['rotation_deg']
            print(f'   camera at ({px:.2f}, {py:.2f}, {pz:.2f}), rotation ({rx:.1f}, {ry:.1f}, {rz:.1f}) deg, fov {cam.get("fov", "?")}')
        hit = r.get('hit')
        if not hit:
            print('   the ray hit nothing')
            continue
        x, y, h = hit['plan']
        nx, ny, nh = hit['normal'][0], -hit['normal'][2], hit['normal'][1]
        front = (x + nx * 0.1, y + ny * 0.1, h + nh * 0.1)      # the side of the face the player saw
        print(f'   hit {hit["facing"]} face at plan ({x:.2f}, {y:.2f}, h {h:.2f}), {hit["distance"]} m away, '
              f'in {where(front, rooms, corridors)}; {hit.get("shape", "")}')
        for m in maps:
            lines, fight = faces_report(m, hit)
            if fight:
                fights += 1
                print('   Z-FIGHT: two brushes have a face on this plane, facing the same way:')
            print('\n'.join(lines) if lines else '      no brush face at this point (an entity or a moving part?)')
    print(f'\n   {len(notes)} notes, {fights} confirmed z-fights. To see a note: '
          f'powershell -File tools/view-playtest-note.ps1 -Session "{folder}" -Note <n>')


def main():
    base = ROOT / 'playtests'
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sessions = sorted((p.parent for p in base.glob('*/*/notes.jsonl')), key=lambda p: p.name)
    if args:
        sessions = [Path(args[0]).resolve()]
    elif '--all' not in sys.argv:
        sessions = sessions[-1:]
    if not sessions:
        print(f'No sessions under {base}. In game: Q makes a note, Z marks z-fighting.')
        return
    for folder in sessions:
        session_report(folder)


if __name__ == '__main__':
    main()
