from pathlib import Path
from html import escape
import json
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'docs/freight-a1-density-plan.json').read_text())
A=P['architecture']
assert A['rib_underside'] > A['scanner_top']
assert A['upper_corner']['starts_at_height'] > max(p['top'] for p in P['floor_props'] if p['room']=='screening' and not p['id'].startswith('R'))
# Threshold jambs sit outside the 3 m reserved route and surrounding furniture.
for b in A['threshold']['side_leg_bounds']:
 for p in P['floor_props']:
  q=p['bounds'];assert min(b[2],q[2])-max(b[0],q[0])<=1e-6 or min(b[3],q[3])-max(b[1],q[1])<=1e-6,p['id']
C={'bg':'#101c28','panel':'#1a2c3c','ink':'#edf4fa','muted':'#adc1d0','wall':'#81b59e','prop':'#85649f','service':'#8795a0','light':'#ffe5a8','route':'#e2b373'}
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1220" viewBox="0 0 1800 1220"><title>Red Breach Screening architecture sample F04</title><rect width="1800" height="1220" fill="#101c28"/><g font-family="Segoe UI,Arial,sans-serif">']
def text(x,y,t,size=18,color='ink',bold=False,anchor='start'):
 s.append(f'<text x="{x}" y="{y}" fill="{C.get(color,color)}" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(t)}</text>')
def rect(x,y,w,h,c,stroke='none',sw=1):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C.get(c,c)}" stroke="{C.get(stroke,stroke)}" stroke-width="{sw}"/>')
def poly(points,c,stroke='none',sw=1):s.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{C.get(c,c)}" stroke="{C.get(stroke,stroke)}" stroke-width="{sw}"/>')
def line(points,c='muted',sw=2,dash=''):s.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{C.get(c,c)}" stroke-width="{sw}" stroke-dasharray="{dash}"/>')
def panel(x,y,w,h,t):rect(x,y,w,h,'panel');text(x+24,y+38,t,23,bold=True)
text(36,48,'RED BREACH / PRESSURIZED COLONY LANGUAGE',30,bold=True)
text(36,82,'F-04 / BUILT LAYOUT 09  |  Screening architectural sample  |  Ready for player walkthrough',19,'muted')
panel(36,110,1728,470,'A / SCREENING CROSS-SECTION — THROUGH THE NORTH EQUIPMENT BAY')
x0,y0,k=168,488,80
x=lambda u:x0+u*k
y=lambda h:y0-h*k
# Shell, straight lower walls, 0.55 m upper corner inserts, 0.25 m rib projection.
rect(x(0),y(3.5),13.75*k,3.5*k,'#293540','wall',4)
poly([(x(0),y(3.5)),(x(.8),y(3.5)),(x(0),y(2.7))],'wall')
poly([(x(13.75),y(3.5)),(x(12.95),y(3.5)),(x(13.75),y(2.7))],'wall')
rect(x(.25),y(3.5),13.25*k,.25*k,'wall')
rect(x(0),y(3.25),.25*k,3.25*k,'wall')
rect(x(13.5),y(3.25),.25*k,3.25*k,'wall')
# Exact equipment cut at paper Z=263.5: S6 storage and S7 cooling.
rect(x(.875),y(2.2),5.6*k,2.2*k,'prop','muted')
for q in range(1,6):line([(x(.875+q*.9),y(2.2)),(x(.875+q*.9),y(0))],'#baacc8',1)
text(x(3.675),y(1.05),'S6 / STORAGE',18,bold=True,anchor='middle')
rect(x(11.975),y(2.5),1.4*k,2.5*k,'service')
for h in [.5,.8,1.1,1.4,1.7]:line([(x(12.1),y(h)),(x(13.2),y(h))],'#4e616d',3)
text(x(12.675),y(.15),'S7',16,'bg',True,'middle')
# Scale figure in the equipment working space.
rect(x(8.1),y(1.45),.5*k,1.45*k,'#b8c9d0');s.append(f'<circle cx="{x(8.35)}" cy="{y(1.65)}" r="{.15*k}" fill="#b8c9d0"/>')
text(x(8.35),y0+28,'1.8 m figure',16,'muted',anchor='middle')
line([(x(0),y0+42),(x(13.75),y0+42)],'route')
text(x(6.875),y0+68,'13.75 m existing room width / no room-shell enlargement',18,'route',True,'middle')
for j,t in enumerate(['Ceiling slab: 3.50 m','Rib underside: 3.25 m','Upper corner begins: 2.95 m','Lower walls stay vertical.','Ribs follow the corner profile.','Structural colour is illustrative;','use the Kenney blockout palette.']):text(1320,236+j*39,t,17,'ink' if j<3 else 'muted',j<3)
panel(36,604,826,500,'B / SCREENING → STAFF PREPARATION')
fx,fy,kk=205,1028,82
rect(fx,fy-3.5*kk,5*kk,3.5*kk,'wall')
rect(fx+.5*kk,fy-3.2*kk,4*kk,3.2*kk,'#293540')
line([(fx+.5*kk,fy+18),(fx+4.5*kk,fy+18)],'route')
text(fx+2.5*kk,fy+45,'4.0 m clear — existing opening width',18,'route',True,'middle')
text(60,681,'Deep frame reads as a compartment boundary.',19)
text(60,715,'0.50 m overall depth; 3.20 m clear headroom.',18,'muted')
text(fx+2.5*kk,fy-1.6*kk,'OPEN PASSAGE',21,bold=True,anchor='middle')
text(fx+2.5*kk,fy-1.2*kk,'Door behaviour remains a later design.',16,'muted',anchor='middle')
panel(886,604,878,500,'C / UPPER-CORNER PROFILE + BAY RHYTHM')
# Enlarged corner at true 1:1 horizontal/vertical scale.
ox,oy,ks=950,728,235
rect(ox,oy,1.05*ks,1.05*ks,'#293540')
line([(ox,oy+1.05*ks),(ox,oy),(ox+1.05*ks,oy)],'wall',6)
poly([(ox,oy),(ox+.55*ks,oy),(ox,oy+.55*ks)],'service')
line([(ox+.55*ks,oy+6),(ox+.55*ks,oy+.55*ks),(ox+6,oy+.55*ks)],'route',1.5,'5 4')
text(ox+.58*ks,oy+.30*ks,'0.55 m',16,'route')
text(ox+.12*ks,oy+.77*ks,'45° upper insert',16)
for j,t in enumerate(['Four rib stations:','3.75 / 3.75 / 3.75 m apart.','Each rib: 0.25 m wide/deep.','Interrupt legs and corner inserts','at existing doorway apertures.','Service trunk occupies the north bay;','light housings mark the workstations.']):text(1240,762+j*34,t,17,'ink' if j<3 else 'muted',j==0)
text(910,1022,'This is the visible interior lining and frame language.',18,bold=True)
text(910,1054,'It suggests a sealed outer shell; it is not a pressure-vessel design.',16,'muted')
text(36,1156,'BUILD NOW: major frames, upper corners, services, light housings and full equipment compositions.',20,bold=True)
text(36,1190,'LATER: panel seams, bolts, small pipes, wear and final meshes. Preserve the 3 m route and 2 m working aisles.',18,'muted')
s.append('</g></svg>')
(ROOT/'docs/freight-a1-architecture-section.svg').write_text('\n'.join(s),encoding='utf-8')
print('Architectural section generated; rib/scanner headroom, upper-corner equipment clearance and jamb footprints checked.')
