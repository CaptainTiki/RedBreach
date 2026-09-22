"""Compare the two corner-lab lighting plans side by side, with measured numbers.

Playtest 2026-09-22: the user was unsure about the unlit bays because the
CEILING goes dark in an off bay, and suggested lighting every section with each
light lowered. This builds the comparison sheet from captures already taken
under each plan and measures the ceiling band rather than arguing about it.

Run the two capture passes first:

    $env:REDBREACH_LIGHT_PLAN='every_bay'; python tools/bootstrap-architecture-lab-corners.py --overwrite
    python tools/write-architecture-lab-corner-scene.py
    powershell -File tools/rebuild-architecture-lab-corners.ps1 -Capture
    (copy .godot/arch_corner_*.png into .godot/plan_every_bay/, then repeat for 'alternate')

Paper only: reads PNGs and writes a sheet. Touches no map.
"""
from pathlib import Path
import html, shutil, struct, subprocess, sys, zlib

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / 'RedBreach/.godot'
PLANS = [('alternate', 'ALTERNATE — every other bay lit, energy 1.40'),
         ('every_bay', 'EVERY BAY — all lit, energy 0.87')]
VIEWS = [
    ('02_mid_straight',  'Half way down the 52 m straight'),
    ('03_v1_approach',   'Approaching V1, the square landing'),
    ('07_v4_approach',   'Approaching V4, the 45° leg'),
    ('08_v4_in_the_leg', 'Standing in the V4 leg'),
]


# --- a minimal PNG reader, so the comparison is measured not eyeballed ------
def read_png(path):
    """(width, height, rows) for an 8-bit truecolour PNG. Stdlib only."""
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'{path.name} is not a PNG'
    pos, idat, w = 8, b'', None
    while pos < len(data):
        length, kind = struct.unpack('>I4s', data[pos:pos+8])
        body = data[pos+8:pos+8+length]
        if kind == b'IHDR':
            w, h, depth, colour = struct.unpack('>IIBB', body[:10])
            assert depth == 8 and colour in (2, 6), f'unsupported PNG {depth}/{colour}'
            channels = 3 if colour == 2 else 4
        elif kind == b'IDAT':
            idat += body
        elif kind == b'IEND':
            break
        pos += 12 + length
    raw = zlib.decompress(idat)
    stride = w * channels
    rows, prev = [], bytearray(stride)
    i = 0
    for _ in range(h):
        f = raw[i]; i += 1
        line = bytearray(raw[i:i+stride]); i += stride
        for x in range(stride):
            a = line[x - channels] if x >= channels else 0
            b = prev[x]
            c = prev[x - channels] if x >= channels else 0
            if f == 1:   line[x] = (line[x] + a) & 0xFF
            elif f == 2: line[x] = (line[x] + b) & 0xFF
            elif f == 3: line[x] = (line[x] + (a + b) // 2) & 0xFF
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else (b if pb <= pc else c))) & 0xFF
        rows.append(bytes(line)); prev = line
    return w, h, rows, channels


def mean_luma(path, box):
    """Mean perceived brightness 0-255 over a fractional (x0,y0,x1,y1) box."""
    w, h, rows, ch = read_png(path)
    x0, y0, x1, y1 = int(box[0]*w), int(box[1]*h), int(box[2]*w), int(box[3]*h)
    total, count = 0, 0
    for y in range(y0, y1, 2):
        row = rows[y]
        for x in range(x0, x1, 2):
            o = x*ch
            total += 0.2126*row[o] + 0.7152*row[o+1] + 0.0722*row[o+2]
            count += 1
    return total / max(count, 1)


# The ceiling band: the top of frame, clear of the HUD text on the left.
CEILING_BOX = (0.45, 0.02, 0.98, 0.16)
FLOOR_BOX = (0.25, 0.80, 0.75, 0.96)

measures = {}
for plan, _ in PLANS:
    for view, _ in VIEWS:
        png = SHOTS / f'plan_{plan}' / f'arch_corner_{view}.png'
        if png.exists():
            measures[(plan, view)] = (mean_luma(png, CEILING_BOX), mean_luma(png, FLOOR_BOX))

# --- the sheet --------------------------------------------------------------
CELL_W = 760
CELL_H = int(648 * CELL_W / 1152)
GAP, MARGIN = 20, 50
W = MARGIN*2 + 2*CELL_W + GAP
H = 190 + len(VIEWS)*(CELL_H + 54) + 150

BG, TEXT, MUTED, GOOD, WARN = '#111b25', '#e5edf3', '#a9bac9', '#6fd3a8', '#e8756c'
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{BG}"/>']


def text(x, y, s, size=18, color=TEXT, weight='normal', anchor='start'):
    parts.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="Segoe UI,Arial,sans-serif" '
                 f'font-size="{size}" font-weight="{weight}" fill="{color}" '
                 f'text-anchor="{anchor}">{html.escape(s)}</text>')


text(MARGIN, 56, 'CORNER LAB / LIGHTING — alternate vs every bay', 32, TEXT, 'bold')
text(MARGIN, 88, 'Playtest note: the unlit bays read wrong because the CEILING goes dark, not the wall. '
                 'Every-bay lighting doubles the fittings, so each one comes down to 0.62 of its energy.', 17, MUTED)
text(MARGIN, 114, 'Ceiling and floor figures are mean perceived brightness (0-255) measured on the same '
                  'frame region in both passes — not an impression.', 16, MUTED)

for i, (plan, label) in enumerate(PLANS):
    text(MARGIN + i*(CELL_W+GAP), 158, label, 20, TEXT, 'bold')

missing = []
for r, (view, caption) in enumerate(VIEWS):
    y = 176 + r*(CELL_H + 54)
    for i, (plan, _) in enumerate(PLANS):
        x = MARGIN + i*(CELL_W+GAP)
        png = SHOTS / f'plan_{plan}' / f'arch_corner_{view}.png'
        if png.exists():
            parts.append(f'<image x="{x}" y="{y}" width="{CELL_W}" height="{CELL_H}" '
                         f'xlink:href="{png.resolve().as_uri()}" preserveAspectRatio="xMidYMid slice"/>')
        else:
            missing.append(f'{plan}/{view}')
            parts.append(f'<rect x="{x}" y="{y}" width="{CELL_W}" height="{CELL_H}" fill="#1b2a36"/>')
        m = measures.get((plan, view))
        if m:
            base = measures.get((PLANS[0][0], view))
            delta = m[0] - base[0] if base else 0.0
            col = GOOD if (i == 0 or delta > 4) else MUTED
            text(x, y + CELL_H + 22, f'ceiling {m[0]:.1f}   floor {m[1]:.1f}', 16, col, 'bold')
            if i == 1 and base:
                text(x + 250, y + CELL_H + 22,
                     f'{delta:+.1f} on the ceiling', 16, GOOD if delta > 0 else WARN)
    text(MARGIN, y + CELL_H + 44, caption, 15, MUTED)

if measures:
    deltas = [measures[('every_bay', v)][0] - measures[('alternate', v)][0]
              for v, _ in VIEWS if ('every_bay', v) in measures and ('alternate', v) in measures]
    if deltas:
        avg = sum(deltas)/len(deltas)
        text(MARGIN, H - 96, f'Mean ceiling change across the four views: {avg:+.1f} brightness points.',
             20, GOOD if avg > 0 else WARN, 'bold')
        text(MARGIN, H - 68, 'Set the plan with REDBREACH_LIGHT_PLAN before running the bootstrap AND the scene writer — '
                             'they must agree, or the fittings and the lights end up in different places.', 15, MUTED)
text(MARGIN, H - 38, 'CORNER LAB LIGHTING COMPARISON / geometry identical in both passes, 473 brushes — only the light plan differs',
     15, MUTED)

parts.append('</svg>')
svg = ROOT / 'docs/architecture-lab-corner-lighting.svg'
svg.write_text('\n'.join(parts), encoding='utf-8')

ink = shutil.which('inkscape') or r'C:\Program Files\Inkscape\bin\inkscape.exe'
if Path(ink).exists():
    subprocess.run([ink, str(svg), '--export-type=png', '--export-filename',
                    str(ROOT / 'docs/architecture-lab-corner-lighting.png'),
                    '--export-width', str(W)], check=True, capture_output=True)
    print('wrote svg + png')
else:
    print('wrote svg; Inkscape not found')

for (plan, view), (ceil, floor) in sorted(measures.items()):
    print(f'  {plan:10} {view:18} ceiling {ceil:6.1f}   floor {floor:6.1f}')
if missing:
    print('  MISSING: ' + ', '.join(missing))
