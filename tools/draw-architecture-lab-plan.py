"""Draw the paper study only. Does not generate or edit game geometry."""
from pathlib import Path
import html
root = Path(__file__).resolve().parents[1]
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1320" viewBox="0 0 1600 1320"><rect width="1600" height="1320" fill="#111b25"/>']
def text(x,y,s,size=18,color='#e5edf3'):
    parts.append(f'<text x="{x}" y="{y}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" fill="{color}">{html.escape(s)}</text>')
def path(points,fill='none',stroke='#9db1c1',width=2,close=False,dash=False):
    d='M'+' L'.join(f'{x},{y}' for x,y in points)+(' Z' if close else '')
    parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '+('stroke-dasharray="7 5" ' if dash else '')+'/>')
def rect(x,y,w,h,fill,stroke='none'):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>')
text(45,49,'ARCHITECTURE LAB / SHAPE STUDY 03',32)
text(45,82,'Same 4 m movement envelope. Three different wall constructions. All proposed dimensions in metres.',19)
text(45,116,'Profiles first: solid shell → sloped base → service volume → internal frame. Colour identifies geometry, not final materials.',17,'#a9bac9')
profiles=[
 [(-2.25,0),(-3,0.75),(-3,3.75),(-1.75,5),(1.75,5),(3,3.75),(3,0.75),(2.25,0)],
 [(-2.25,0),(-3.25,1),(-3.25,2.75),(-2.75,2.75),(-2.75,4),(-1.75,4),(-1.75,5),(1.75,5),(1.75,4),(2.75,4),(2.75,2.75),(3.25,2.75),(3.25,1),(2.25,0)],
 [(-2.25,0),(-3.25,1),(-3.25,3.25),(-2,4.5),(2,4.5),(3.25,3.25),(3.25,1),(2.25,0)]
]
colors=['#7ed6bf','#efbb75','#8dc5f2']
titles=['A / SUSPENDED SERVICE SPINE','B / STEPPED SERVICE GALLERY','C / BUTTRESSED WINDOW BAY']
subs=['Faceted shell + hanging spine + forked supports.','Wall steps inward beneath a raised ceiling spine.','Splayed base; deep windows; broad knee braces.']
for i,p in enumerate(profiles):
    cx=270+i*530; sc=56; by=485
    tx=lambda q:(cx+q[0]*sc,by-q[1]*sc)
    text(cx-225,161,titles[i],21,colors[i]);text(cx-225,189,subs[i],16)
    path([tx(q) for q in p], '#1b2a36',colors[i],3,True)
    # Internal rib section, explicitly broken into polygonal brush-like pieces.
    if i==0:
        inner=[(-2,0),(-2.7,.85),(-2.7,3.6),(-1.6,4.7),(1.6,4.7),(2.7,3.6),(2.7,.85),(2,0)]
        for j in range(len(p)-1):path([tx(p[j]),tx(p[j+1]),tx(inner[j+1]),tx(inner[j])],'#35594f',colors[i],1,True)
        for sign in [-1,1]:path([tx((sign*2.8,3.1)),tx((sign*2.35,3.1)),tx((sign*2.35,3.7)),tx((sign*2.8,3.7))],'#95643b','#f0b46e',2,True)
        # Angled hangers connect the rib shoulders to a longitudinal faceted trunk.
        for sign in [-1,1]:
            path([tx((sign*1.75,4.55)),tx((sign*.8,3.85)),tx((sign*.8,4.1)),tx((sign*1.6,4.7))],'#48645d',colors[i],2,True)
        path([tx(q) for q in [(-.8,4.1),(.8,4.1),(.8,3.65),(.55,3.4),(-.55,3.4),(-.8,3.65)]],'#95643b','#f0b46e',2,True)
        for sign in [-1,1]:
            path([tx((sign*.78,3.65)),tx((sign*.55,3.42))],stroke='#ecf6ce',width=5)
    elif i==1:
        for sign in [-1,1]:
            path([tx((sign*2,0)),tx((sign*2.5,0.65)),tx((sign*2.5,3.2)),tx((sign*1.6,3.75)),tx((sign*1.6,4)),tx((sign*2.85,3.5)),tx((sign*2.85,.65)),tx((sign*2.3,0))],'#665035',colors[i],2,True)
            path([tx((sign*2.8,2.85)),tx((sign*2.05,2.85)),tx((sign*2.05,3.45)),tx((sign*2.8,3.45))],'#95643b','#f0b46e',2,True)
        rect(cx-1.6*sc,by-4.75*sc,3.2*sc,.25*sc,'#665035',colors[i])
    else:
        rect(cx-1.55*sc,by-4.35*sc,3.1*sc,.30*sc,'#39546a',colors[i])
        for sign in [-1,1]:
            path([tx((sign*2,0)),tx((sign*2.7,1)),tx((sign*2.7,3)),tx((sign*1.55,4.05)),tx((sign*1.55,4.35)),tx((sign*3,3.1)),tx((sign*3,1)),tx((sign*2.4,0))],'#39546a',colors[i],2,True)
            path([tx((sign*3.25,1.25)),tx((sign*3.8,1.25)),tx((sign*3.8,3)),tx((sign*3.25,3))],'none','#b4e8fc',3)
            path([tx((sign*2.85,3.5)),tx((sign*2.25,3.5)),tx((sign*2,3.75)),tx((sign*2.6,3.75))],'#95643b','#f0b46e',2,True)
    path([tx((-2,0)),tx((-2,3.2)),tx((2,3.2)),tx((2,0))],stroke='#b7c5cf',dash=True)
    path([tx((-2.25,0)),tx((2.25,0))],stroke='#c5d0d9',width=5)
    text(cx-89,by-125,'4 m × 3.2 m clear',16)
    # Neutral scale figure schematic.
    parts.append(f'<circle cx="{cx}" cy="{by-94}" r="8" fill="#9dadb8"/>')
    path([(cx,by-85),(cx,by-40),(cx-12,by)],stroke='#9dadb8',width=4)
    path([(cx,by-40),(cx+12,by)],stroke='#9dadb8',width=4)
    text(cx-225,516,['1.6 m-wide faceted trunk; underside at 3.4 m.','1 m sloped base + vertical wall + two real setbacks.','1 m splayed base; 1.25 m upper shoulder.'][i],16)
    text(cx-225,541,['Forked hangers at ribs / paired inset light housings.','6.5 m widest shell / 5 m crown / separate columns.','6.5 m widest shell / 4.5 m crown / 0.55 m reveal.'][i],16)
path([(45,571),(1555,571)],stroke='#3c4b59')
text(45,608,'A / SIDE WALL + SUSPENDED CENTRE SPINE',24)
# longitudinal elevation - y proportional, four-metre bay
rect(65,651,485,251,'#1b2a36','#758a9b')
path([(65,902),(100,865),(515,865),(550,902)],'#35594f','#7ed6bf',2,True)
path([(65,651),(100,688),(515,688),(550,651)],'#35594f','#7ed6bf',2,True)
rect(105,716,405,111,'#15212b','#7ed6bf')
rect(65,651,35,251,'#48645d','#7ed6bf');rect(515,651,35,251,'#48645d','#7ed6bf')
rect(100,689,415,24,'#95643b','#efbb75')
for x in [145,300,455]:rect(x,684,11,35,'#688278')
rect(140,835,315,18,'#33443d','#7ed6bf')
rect(65,732,485,39,'#95643b','#efbb75')
for x in [65,515]:
    path([(x,668),(x+35,668),(x+35,746),(x,746)],'#48645d','#7ed6bf',2,True)
for x in [125,325]:rect(x,765,150,6,'#ecf6ce')
text(77,929,'Side elevation / spine in foreground; wall infill behind',16)
text(605,665,'01  SHELL PLANES',19,'#7ed6bf');text(605,692,'Separate floor, lower wedges, wall slabs, upper wedges and roof.',17)
text(605,731,'02  SUSPENDED SPINE',19,'#efbb75');text(605,758,'Chamfered trunk, real end caps and two inset light channels.',17)
text(605,797,'03  FORKED SUPPORTS',19,'#8dc5f2');text(605,824,'Angled brush hangers connect each rib to the central trunk.',17)
text(605,863,'04  RECESSED INFILL',19);text(605,890,'Set backing behind the frame. Add real lips to vents and windows.',17)
text(605,923,'Judge silhouette and shadow under neutral light before adding small detail.',17,'#a9bac9')
path([(45,952),(1555,952)],stroke='#3c4b59')
text(45,990,'PLAN / SAME THREE OUT-AND-BACK TESTS',23)
for i in range(3):
    x=70+i*150
    rect(x,1015,100,180,'#1b2a36',colors[i]);rect(x+22,1015,56,180,'#243643')
    for y in [1020,1060,1105,1150]:
        rect(x+12,y,10,6,colors[i]);rect(x+78,y,10,6,colors[i])
    text(x+41,1052,chr(65+i),20,colors[i])
rect(50,1195,450,65,'#243643','#9db1c1');text(98,1234,'Shared gallery / widened to 24 × 6 m',17)
text(575,1030,'16 m sample lengths; centres 8 m apart; clear lanes remain 4 m.',18)
text(575,1064,'Extra wall depth sits outside the lanes. C’s scenery sits to the east.',18)
text(575,1098,'B reserves a sealed overhead hatch between ribs; services stay beside it.',18)
text(575,1146,'Images supplied by you guide geometry, not shader imitation.',18,'#a9bac9')
text(575,1180,'A: hanging spine   B: stepped bays   C: window buttresses',18,'#a9bac9')
text(575,1214,'Sketches show profiles at ribs; infill and continuous ducting sit behind.',18,'#a9bac9')
text(45,1293,'REVISION 03 / paper geometry study only · no game-map edits · actual construction and clearance checks follow review',17,'#a9bac9')
parts.append('</svg>')
(root/'docs/architecture-lab-plan.svg').write_text('\n'.join(parts),encoding='utf-8')
