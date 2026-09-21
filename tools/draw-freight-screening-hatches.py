"""Paper-only hatch reservations; reads the approved F04 furniture without changing it."""
from pathlib import Path
from html import escape
import json
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs';plan=json.loads((D/'freight-a1-density-plan.json').read_text());hatches=json.loads((D/'freight-screening-hatch-reservations.json').read_text())
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="940" viewBox="0 0 1500 940"><rect width="1500" height="940" fill="#101c28"/><g font-family="Segoe UI,Arial,sans-serif">']
def text(x,y,t,size=18,c='#edf4fa',bold=False):s.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{c}" font-weight="{700 if bold else 400}">{escape(t)}</text>')
def rect(x,y,w,h,fill,stroke='none',dash='',opacity=1):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-dasharray="{dash}" opacity="{opacity}"/>')
ox,oy,k=80,210,43
pt=lambda x,z:(ox+(x-82.125)*k,oy+(z-262)*k)
def box(b,fill,stroke='none',dash='',opacity=1):
 x,y=pt(b[0],b[1]);rect(x,y,(b[2]-b[0])*k,(b[3]-b[1])*k,fill,stroke,dash,opacity)
def line(points,c,width=2,dash=''):
 s.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{c}" stroke-width="{width}" stroke-dasharray="{dash}"/>')
text(36,48,'SCREENING / RESERVE BUG ENTRY SPACE NOW',29,bold=True)
text(36,82,'Paper candidates only — no holes, triggers or enemies have been added.',19,'#adc1d0')
rect(36,114,682,739,'#1a2c3c');text(58,153,'EXISTING FURNISHED ROOM + RESERVATIONS',19,bold=True)
box(plan['rooms']['screening'],'#293540','#81b59e')
for p in plan['floor_props']:
 if p['room']=='screening':box(p['bounds'],'#85649f' if not p['id'].startswith('R') else '#8795a0')
for p in plan['overhead']:
 if p['room']=='screening':box(p['bounds'],'none','#a1b5c3','4 4',.65)
for r in plan['routes']:
 if r['room']=='screening':line([pt(*p) for p in r['points']],'#e2b373',3,'5 4')
for a,b in [([95.875,270],[95.875,274]),([82.125,266],[82.125,270]),([86,275.875],[90,275.875])]:line([pt(*a),pt(*b)],'#e2b373',5)
for h in hatches['candidates']:
 box(h['landing_bounds_xz'],'#59cbd0','#59cbd0','7 5',.22)
 if h['surface']=='ceiling':
  box(h['opening_bounds_xz'],'none','#ec879e','8 4');x,y=pt(88.55,265.6);text(x,y,'C1',22,'#ffb6c7',True)
 else:
  a,b=h['opening_span_x'];line([pt(a,262),pt(b,262)],'#ec879e',7);x,y=pt(a,261.65);text(x,y,'W1',22,'#ffb6c7',True)
text(80,829,'Pink: possible openings. Cyan: reserved emergence floor.',16,'#adc1d0')
rect(742,114,722,739,'#1a2c3c')
text(766,158,'C1 / CEILING SERVICE HATCH',23,'#ffb6c7',True)
for i,t in enumerate(['2.5 × 2.5 m opening, between ribs and fixtures.','Keep a 3 × 3 m landing / emergence area below.','Reserve an overhead service pocket before cutting.','Drop emergence does not require ceiling-crawling AI.']):text(766,199+i*32,t,18)
text(766,365,'W1 / NORTH WALL SERVICE HATCH',23,'#ffb6c7',True)
for i,t in enumerate(['2.5 × 2.5 m opening beside the storage bank.','Keep the floor in front free of equipment.','A backing service pocket still needs spatial planning.','These are alternatives in one bay, not a paired ambush.']):text(766,406+i*32,t,18)
text(766,573,'RESERVE THE ENCOUNTER, NOT JUST THE GRATE',21,bold=True)
for i,t in enumerate(['Opening + hidden staging + clear landing + escape route.','Check the largest intended bug and its navigation.','Keep a readable hatch cue and distinct ambush screech.','Defer emergence if the player or another bug occupies it.','Floor hatches belong beside routes; keep retreat usable.','Enemy counts, trigger timing and hatch choice come later.']):text(766,614+i*32,t,17,'#adc1d0')
text(36,901,'Screening and Registration now share a level floor. Texture changes need a physical edge or seam.',20,bold=True)
s.append('</g></svg>');(D/'freight-screening-hatch-reservations.svg').write_text('\n'.join(s),encoding='utf-8')
print('Hatch reservation drawing saved.')
