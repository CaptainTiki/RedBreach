"""Draw the room scale comparison sheet. Paper only; touches no map.

Puts every freight room, the revision-06 corridor and an estimated Doom 3 room
envelope on ONE scale, because the room question turned out to be a question
about size rather than about vocabulary.

Honesty about sources, which matters here:
  MEASURED   every Red Breach figure, read from docs/freight-blockout-layout.json
             and tools/architecture_lab_section.py
  PUBLISHED  the generic blockout metrics, from The Level Design Book
  ESTIMATED  the Doom 3 room envelope, read off the two reference screenshots
             in docs/references/doom3-administration/ against the door and
             human figures in them. It is a visual interpretation, not a
             measurement of the game, and it is drawn as a band not a number.
"""
from pathlib import Path
import html, json, math, shutil, subprocess, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import architecture_lab_section as S

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = json.loads((ROOT / 'docs/freight-blockout-layout.json').read_text(encoding='utf-8'))

rooms = []
for name, r in LAYOUT['rooms'].items():
    rooms.append({'name': name, 'w': r[2], 'h': r[3], 'label': r[4],
                  'floor': LAYOUT.get('floor_heights', {}).get(name)})
rooms.sort(key=lambda r: -(r['w'] * r['h']))

# Estimated from the reference screenshots, deliberately as a RANGE.
D3_MIN, D3_MAX = 8.0, 16.0

W, H = 1700, 1270
BG='#111b25'; PANEL='#1b2a36'; DEEP='#15212b'; RULE='#3c4b59'
TEXT='#e5edf3'; MUTED='#a9bac9'
OURS='#7fb6d9'; D3='#e8a15c'; WARN='#e8756c'; GOOD='#6fd3a8'; SIGHT='#ffe9b8'

parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>']

def text(x,y,s,size=18,color=TEXT,weight='normal',anchor='start'):
    parts.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" '
                 f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(s)}</text>')

def rect(x,y,w,h,fill='none',stroke='none',width=1,opacity=1.0,rx=0,dash=None):
    da=f'stroke-dasharray="{dash}" ' if dash else ''
    parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{width}" {da}opacity="{opacity}"/>')

def poly(points,fill='none',stroke=MUTED,width=2,close=True,dash=None,opacity=1.0):
    d='M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in points)+(' Z' if close else '')
    da=f'stroke-dasharray="{dash}" ' if dash else ''
    parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {da}opacity="{opacity}"/>')

def hrule(y,x0=60,x1=W-60):
    poly([(x0,y),(x1,y)],stroke=RULE,width=1,close=False)

def wrap(s,n):
    out=[];cur=''
    for w_ in s.split():
        if len(cur)+len(w_)+1>n: out.append(cur); cur=w_
        else: cur=(cur+' '+w_).strip()
    if cur: out.append(cur)
    return out

text(60,58,'ROOMS — SCALE COMPARISON BEFORE ANY DESIGN', 34, TEXT, 'bold')
text(60,90,'Every Red Breach figure is measured. The Doom 3 envelope is a visual estimate off the reference screenshots, drawn as a band rather than a number.',17,MUTED)

# ---------------------------------------------------------------- the plan comparison
PX, PY = 60, 140
SC = 3.05                       # pixels per metre
text(PX, PY-14, 'ALL 22 FREIGHT ROOMS, THE CORRIDOR AND AN ESTIMATED DOOM 3 ROOM — ONE SCALE', 21, TEXT, 'bold')

x, y, rowh = PX, PY + 20, 0
for r in rooms:
    w, h = r['w']*SC, r['h']*SC
    if x + w > W - 380:
        x = PX; y += rowh + 16; rowh = 0
    rect(x, y, w, h, '#22323f', OURS, 1.4)
    if w > 52 and h > 28:
        text(x+6, y+16, r['name'], 13, TEXT, 'bold')
        text(x+6, y+31, f"{r['w']:g}x{r['h']:g}", 11, MUTED)
    x += w + 14
    rowh = max(rowh, h)
plan_bottom = y + rowh

# the corridor, and the Doom 3 band, against the same scale
bx = W - 350
rect(bx-14, PY+6, 300, 268, PANEL, RULE, 1, rx=6)
text(bx, PY+32, 'AT THE SAME SCALE', 16, TEXT, 'bold')
cw = 2*S.WIDEST*SC
rect(bx, PY+48, cw, 52*SC, '#22323f', GOOD, 1.6)
text(bx+cw+12, PY+64, 'our corridor', 13, GOOD, 'bold')
text(bx+cw+12, PY+82, f'{2*S.WIDEST:.2f} m wide', 12, MUTED)
text(bx+cw+12, PY+98, 'x 52 m max run', 12, MUTED)
d3x = bx + cw + 12
rect(d3x, PY+124, D3_MAX*SC, D3_MAX*SC, 'none', D3, 1.6, dash='5 4')
rect(d3x, PY+124, D3_MIN*SC, D3_MIN*SC, 'none', D3, 1.6, dash='5 4')
text(d3x, PY+124+D3_MAX*SC+20, 'Doom 3 room, estimated', 13, D3, 'bold')
text(d3x, PY+124+D3_MAX*SC+36, f'{D3_MIN:g}-{D3_MAX:g} m across', 12, MUTED)

# ---------------------------------------------------------------- the numbers
NY = plan_bottom + 46
hrule(NY-26)
text(60, NY, 'WHAT THE NUMBERS SAY', 24, TEXT, 'bold')

areas = sorted(r['w']*r['h'] for r in rooms)
med = areas[len(areas)//2]
ratios = [max(r['w'],r['h'])/min(r['w'],r['h']) for r in rooms]
cells = [
    ('Freight rooms', f'{len(rooms)}', 'measured', OURS),
    ('Median room', f'{med:,.0f} m\u00b2', 'about 40 x 39 m', OURS),
    ('Largest', f'{max(areas):,.0f} m\u00b2', 'B4, 72 x 48 m', WARN),
    ('Worst proportion', f'{max(ratios):.2f}:1', 'rule is 2:1 \u2014 all pass', GOOD),
    ('Our corridor', f'{2*S.WIDEST:.2f} m', f'crown {S.CEIL_Y:.2f} m', OURS),
    ('Generic standard', '1.5-2.0 m', 'Level Design Book', MUTED),
    ('Doom 3 rooms', '~90%', 'corridors or very small rooms', D3),
    ('Estimated D3 room', f'{D3_MIN:g}-{D3_MAX:g} m', 'visual, not measured', D3),
]
cx, cy = 60, NY + 26
for i, (k, v, note, col) in enumerate(cells):
    col_i, row_i = i % 4, i // 4
    px_, py_ = cx + col_i*400, cy + row_i*86
    rect(px_-10, py_-4, 380, 74, PANEL, RULE, 1, rx=5)
    text(px_, py_+20, k, 14, MUTED, 'bold')
    text(px_, py_+46, v, 24, col, 'bold')
    text(px_+130, py_+46, note, 13, MUTED)

# ---------------------------------------------------------------- findings
FY = cy + 2*86 + 34
hrule(FY-22)
text(60, FY, 'THREE THINGS THIS SETTLES BEFORE WE DRAW ANYTHING', 24, TEXT, 'bold')
MED = f'{med:,.0f} m²'
notes = [
 ("Doom 3's room language is a SMALL-room language.",
  "Roughly ninety per cent of Doom 3 is corridor or very small room, and it has a known reputation for "
  "little height variation. Our median freight room is around {MED} \u2014 an order of magnitude past "
  "anything in the reference. We can borrow its VOCABULARY and must not borrow its room STRATEGY."),
 ("So the borrowed vocabulary is the part below 2.50 m.",
  "Both reference shots show the same four moves: uprights at a rhythm dividing the wall into bays, "
  "equipment set inside a bay rather than stuck on a flat wall, a floor plinth with a chamfered edge "
  "defining a zone, and a ceiling mass centred on the thing below it. All of that is our corridor's "
  "lower register already."),
 ("The real question is not the wall. It is the 40 m span.",
  "A 6.00 m corridor opening into a 50 m room is a scale jump of nearly ten to one, and a 3.75 m crown "
  "cannot carry it. `architecture-language.md` already names the answer \u2014 local ceiling planes, "
  "service voids, enclosed pods inside a larger envelope \u2014 which is subdivision, not a bigger ceiling."),
 ("A room wall is long enough to need the repetition rule too.",
  "B4 has a 72 m wall and A4 a 66 m one, against a 52 m ceiling proven by walking it. Whatever replaces "
  "the rib rhythm inside a room has to answer the same question the corridor did, and the "
  "'structural bay' the language already names is the obvious candidate."),
]
ny = FY + 30
for i, (head, body) in enumerate(notes):
    bx_ = 60 + (i % 2)*810
    by_ = ny + (i // 2)*124
    rect(bx_-12, by_-22, 786, 112, PANEL, RULE, 1, rx=5)
    text(bx_, by_, head, 17, TEXT, 'bold')
    for j, l in enumerate(wrap(body.replace("{MED}", MED), 98)[:4]):
        text(bx_, by_+24+j*20, l, 14, MUTED)

text(60, H-34, 'ROOM SCALE COMPARISON / paper only \u00b7 Red Breach figures measured from the freight layout and the section module \u00b7 '
                'Doom 3 envelope estimated from the reference screenshots, not measured from the game', 15, MUTED)

parts.append('</svg>')
svg = ROOT/'docs/room-scale-comparison.svg'
svg.write_text('\n'.join(parts), encoding='utf-8')
ink = shutil.which('inkscape') or r'C:\Program Files\Inkscape\bin\inkscape.exe'
if Path(ink).exists():
    subprocess.run([ink, str(svg), '--export-type=png', '--export-filename',
                    str(ROOT/'docs/room-scale-comparison.png'), '--export-width', str(W)],
                   check=True, capture_output=True)
    print('wrote svg + png')
else:
    print('wrote svg; Inkscape not found')
print(f'  {len(rooms)} rooms, median {med:,.0f} m2, largest {max(areas):,.0f} m2, worst ratio {max(ratios):.2f}:1')
