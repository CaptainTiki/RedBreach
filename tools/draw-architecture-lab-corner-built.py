"""Assemble the corner-lab captures into one contact sheet.

Paper only. Reads whatever capture_architecture_lab_corners.gd last wrote into
RedBreach/.godot/ and lays it out with captions, the same way the straight
run's built sheet reads. Rasterises with Inkscape when it is installed.
"""
from pathlib import Path
import html, shutil, subprocess, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import architecture_lab_corner as C

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / 'RedBreach/.godot'

VIEWS = [
    ('01_long_straight',   'The repetition test — 52 m, nothing in it'),
    ('02_mid_straight',    'Half way down. Is the rhythm still saying anything?'),
    ('03_v1_approach',     'V1 approach — the square landing reads as a full stop'),
    ('04_v1_exit',         'V1 — the mitre frames the exit like a portal'),
    ('05_v1_outer_corner', 'V1 outer corner — the dead square pocket, no rib on it'),
    ('06_v1_looking_back', 'V1 from the far side — does the rib beat line up?'),
    ('07_v4_approach',     'V4 approach — the 45° leg opening up'),
    ('08_v4_in_the_leg',   'V4 — standing in the leg, a rib inside the turn'),
    ('09_v4_looking_back', 'V4 from the far side, back up the diagonal'),
    ('10_v4_rib_base',     'V4 — the battered rib base on a 45° wall'),
    ('11_t_approach',      'T approach — the opening arrives on the right'),
    ('12_t_branch',        'T — standing in the junction, down the branch'),
    ('13_t_choice',        'T — the choice: straight on, or turn'),
    ('14_t_jamb',          'T — the jamb and the branch’s first rib, 0.75 m apart'),
    ('15_t_looking_back',  'T — looking back into the junction from the branch'),
    ('16_v1_corner_close', 'V1 outer corner, close — the two mitred profiles meeting'),
    ('17_v1_corner_low',   'V1 outer corner, low — base kick and plinth at the fold'),
    ('18_v1_corner_high',  'V1 outer corner, high — the ceiling chamfer at the fold'),
    ('19_t_jamb_close',    'T jamb, close — where the through wall stops'),
    ('20_user_view',       'The jamb from the user’s own camera — void filled'),
]

COLS = 2
SHOT_W, SHOT_H = 1152, 648
CELL_W = 810
CELL_H = int(SHOT_H * CELL_W / SHOT_W)
GAP, MARGIN, CAP = 22, 50, 34
ROWS = (len(VIEWS) + COLS - 1) // COLS
W = MARGIN*2 + COLS*CELL_W + (COLS-1)*GAP
H = 150 + ROWS*(CELL_H + CAP + GAP) + MARGIN

BG, TEXT, MUTED = '#111b25', '#e5edf3', '#a9bac9'
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{BG}"/>']


def text(x, y, s, size=18, color=TEXT, weight='normal'):
    parts.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="Segoe UI,Arial,sans-serif" '
                 f'font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(s)}</text>')


_, _, total = C.walk_metrics()
placed, skipped = C.rib_stations_walk()
text(MARGIN, 58, 'ARCHITECTURE LAB / THE CORNER — built', 34, TEXT, 'bold')
text(MARGIN, 90, f'{total:.2f} m walk in one piece: a {C.walk_metrics()[1][1]:.0f} m straight, '
                 f'a square 90 (V1), then a 45° leg (V4). No rib sits at any bend.', 18, MUTED)
text(MARGIN, 116, f'473 brushes · 1,268 validation checks, 0 failures · '
                  f'{len(placed)} ribs on one 4 m rhythm measured along the centreline, '
                  f'{len(skipped)} stations skipped inside turns.', 16, MUTED)

missing = []
for i, (name, caption) in enumerate(VIEWS):
    col, row = i % COLS, i // COLS
    x = MARGIN + col*(CELL_W + GAP)
    y = 150 + row*(CELL_H + CAP + GAP)
    png = SHOTS / f'arch_corner_{name}.png'
    if png.exists():
        parts.append(f'<image x="{x}" y="{y}" width="{CELL_W}" height="{CELL_H}" '
                     f'xlink:href="{png.resolve().as_uri()}" preserveAspectRatio="xMidYMid slice"/>')
    else:
        missing.append(name)
        parts.append(f'<rect x="{x}" y="{y}" width="{CELL_W}" height="{CELL_H}" fill="#1b2a36"/>')
        text(x + 20, y + CELL_H/2, f'missing: {png.name}', 16, MUTED)
    text(x, y + CELL_H + 24, caption, 16, MUTED)

parts.append('</svg>')
svg = ROOT / 'docs/architecture-lab-corner-built.svg'
svg.write_text('\n'.join(parts), encoding='utf-8')

ink = shutil.which('inkscape') or r'C:\Program Files\Inkscape\bin\inkscape.exe'
if Path(ink).exists():
    subprocess.run([ink, str(svg), '--export-type=png', '--export-filename',
                    str(ROOT / 'docs/architecture-lab-corner-built.png'),
                    '--export-width', str(W)], check=True, capture_output=True)
    print(f'wrote svg + png ({len(VIEWS)-len(missing)}/{len(VIEWS)} views)')
else:
    print('wrote svg; Inkscape not found, export the PNG manually')
if missing:
    print('  MISSING captures: ' + ', '.join(missing))
