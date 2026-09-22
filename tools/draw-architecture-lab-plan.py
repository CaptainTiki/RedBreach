"""Draw the paper study only. Does not generate or edit game geometry.

Revision 05: rhythm, bay insert kit and circuit plan. The full section with
every facet dimensioned lives on the companion sheet drawn by
draw-architecture-lab-section.py. Rasterises with Inkscape when installed.
"""
from pathlib import Path
import html, shutil, subprocess

root = Path(__file__).resolve().parents[1]
W, H = 1700, 2060

BG='#111b25'; PANEL='#1b2a36'; DEEP='#15212b'; RULE='#3c4b59'
TEXT='#e5edf3'; MUTED='#a9bac9'; LINE='#9db1c1'
STRUCT='#7fb6d9'; INFILL='#8fa3b3'; PLINTH='#5d7386'
ACCENT='#e8a15c'; MARS='#d4663f'; GLASS='#7fd6ea'; OPEN='#ffe9b8'; CLEAR='#6fd3a8'

parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>']

def text(x,y,s,size=18,color=TEXT,weight='normal',anchor='start'):
    parts.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" '
                 f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(s)}</text>')

def path(points,fill='none',stroke=LINE,width=2,close=False,dash=None,opacity=1.0):
    d='M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in points)+(' Z' if close else '')
    da=f'stroke-dasharray="{dash}" ' if dash else ''
    parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {da}'
                 f'opacity="{opacity}" stroke-linejoin="miter"/>')

def rect(x,y,w,h,fill='none',stroke='none',width=1,dash=None,opacity=1.0):
    if w<0: x,w = x+w,-w
    if h<0: y,h = y+h,-h
    da=f'stroke-dasharray="{dash}" ' if dash else ''
    parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{width}" {da}opacity="{opacity}"/>')

def hrule(y,x0=60,x1=W-60):
    path([(x0,y),(x1,y)],stroke=RULE,width=1)

def figure(cx,base,sc,color='#9dadb8'):
    parts.append(f'<circle cx="{cx:.1f}" cy="{base-1.62*sc:.1f}" r="{0.11*sc:.1f}" fill="{color}"/>')
    path([(cx,base-1.5*sc),(cx,base-0.72*sc),(cx-0.22*sc,base)],stroke=color,width=3)
    path([(cx,base-0.72*sc),(cx+0.22*sc,base)],stroke=color,width=3)
    path([(cx-0.25*sc,base-1.32*sc),(cx+0.25*sc,base-1.32*sc)],stroke=color,width=3)

def chip(x,y,color,label,detail):
    rect(x,y-14,16,16,color)
    text(x+26,y,label,17,TEXT,'bold')
    text(x+26+len(label)*9.6+16,y,detail,16,MUTED)

def marker(n,x,y,color=TEXT):
    parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="11" fill="{BG}" stroke="{color}" stroke-width="2"/>')
    text(x,y+5,str(n),14,color,'bold','middle')

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import architecture_lab_section as S

S.check()
mirror = S.mirror
SHELL = S.full_shell()
RIB_HALF = list(S.RIB) + [(0, S.CEIL_Y)] + list(reversed(S.WALL))
HW = S.SHELL_BACK          # 3.25 m half footprint, wall solids included
GLAZE = 3.50               # window reveal reaches this far out

# ------------------------------------------------------------------ header
text(60,58,'ARCHITECTURE LAB / REVISION 06 — RHYTHM, KIT AND CIRCUIT',33,TEXT,'bold')
text(60,92,'Four reusable pieces plus swap-outs. The circuit below is provisional \u2014 the section is what is being signed off first.',20)
text(60,118,'All dimensions in metres on a 0.125 m grid (4 map units at 32 u/m). Colour identifies construction, not final materials.',17,MUTED)

chip(60,162,PLINTH,'R1  PLINTH','0 – 1.25 m  ·  base kick, plinth, chamfer out')
chip(650,162,INFILL,'R2  PANEL','1.25 – 2.50 m  ·  eye level, the only zone that swaps')
chip(1230,162,STRUCT,'R3  UPPER','2.50 – 3.75 m  ·  chamfer, upper wall, ceiling')

# -------------------------------------------------------- section thumbnail
SC=66; BASE=540
cx=430
tx=lambda q:(cx+q[0]*SC, BASE-q[1]*SC)
text(60,206,'THE SECTION, IN BRIEF',22,TEXT,'bold')
text(60,230,'Nine facets per half, in three reusable pieces. See architecture-lab-section.png for every dimension.',16,MUTED)
path([tx(q) for q in SHELL], PANEL, LINE, 2, True)
for sgn in (-1,1):
    path([(cx+sgn*q[0]*SC, BASE-q[1]*SC) for q in RIB_HALF], '#2c4e66', STRUCT, 2, True)
    path([(cx+sgn*q[0]*SC, BASE-q[1]*SC) for q in
          list(S.WALL[:4])+[(S.WALL[3][0],0)]],'#3b4c5c',PLINTH,2,True)
path([tx((-2,0)),tx((-2,3.2)),tx((2,3.2)),tx((2,0))],stroke=CLEAR,width=2,dash='8 6')
path([tx((-2.25,0)),tx((2.25,0))],stroke='#c5d0d9',width=5)
figure(cx,BASE,SC)
text(cx,BASE-1.80*SC,'4.0 × 3.2 clear',14,CLEAR,anchor='middle')

sx0=790
for k,line in enumerate([
  ('Widest interior 5.50 m \u00b7 crown 3.75 m \u00b7 rib beam soffit 3.50 m.',TEXT),
  ('Two angles only: 45\u00b0 chamfers, and one 63.43\u00b0 base kick.',TEXT),
  ('The kick is the single facet the player can stand on, so it is the',MUTED),
  ('only one that has to beat the floor_max_angle default.',MUTED),
  ('',TEXT),
  ('FLOOR, WALL and CEILING are three separate reusable brushes.',TEXT),
  ('Mirror them for the far half. Any one can be swapped for a',MUTED),
  ('special without touching the other two.',MUTED),
  ('',TEXT),
  ('The RIB drops in every 4 m \u2014 four 1 m texture repeats \u2014 and',TEXT),
  ('runs floor to ceiling; opposite toes define the 4.00 m clear lane.',MUTED),
  ('',TEXT),
  ('The circuit below still carries revision 05 routing. Its numbers',MUTED),
  ('are provisional until the section is signed off.',MUTED)]):
    text(sx0,258+k*24,line[0],16,line[1])

hrule(566)

# --------------------------------------------------------------- elevation
ES=44; EB=840; EX=140
ey=lambda h: EB-h*ES
ex=lambda z: EX+(-z)*ES
text(60,604,'SPINE / WEST WALL ELEVATION — provisional routing at 4.0 m pitch',24,TEXT,'bold')
text(60,628,'Ribs every 4.0 m \u2014 four 1 m texture repeats. The panel between them is what changes, not the section.',16,MUTED)

rect(EX,ey(4.25),21*ES,4.25*ES,DEEP,LINE,2)
rect(EX,ey(1.25),21*ES,1.25*ES,'#3b4c5c',PLINTH,1)
rect(EX,ey(4.25),21*ES,0.625*ES,'#2c4e66',STRUCT,1)
ribs=[0,-3,-6,-9,-15,-18,-21]
bays=[(0,-3,'panel'),(-3,-6,'equipment'),(-6,-9,'recess'),(-9,-15,'portal'),(-15,-18,'grille'),(-18,-21,'panel')]
for b0,b1,kind in bays:
    x0,x1=ex(b0)+0.25*ES, ex(b1)-0.25*ES
    w=x1-x0
    if kind=='portal':
        oL,oR=ex(-10),ex(-14)
        rect(oL,ey(3.2),oR-oL,3.2*ES,'#3a3524',OPEN,2)
        text((oL+oR)/2,ey(2.0),'4.0 × 3.2 T OPENING',15,OPEN,'bold','middle')
        text((oL+oR)/2,ey(1.6),'to west branch',14,MUTED,anchor='middle')
        rect(x0,ey(2.75),oL-x0,1.5*ES,'#2a3a47',INFILL,1)
        rect(oR,ey(2.75),x1-oR,1.5*ES,'#2a3a47',INFILL,1)
    elif kind=='recess':
        rect(x0,ey(2.375),w,2.375*ES,'#24473d',CLEAR,2)
        text((x0+x1)/2,ey(1.1),'ALCOVE',14,CLEAR,'bold','middle')
    else:
        rect(x0,ey(2.75),w,1.5*ES,'#2a3a47',INFILL,1)
        if kind=='equipment':
            rect(x0+10,ey(2.4),w-20,0.85*ES,'#6a4f30',ACCENT,2)
            for k in range(3):
                rect(x0+18+k*((w-36)/3),ey(2.25),(w-52)/3,0.5*ES,'#8a6437',ACCENT,1)
        if kind=='grille':
            rect(x0+10,ey(2.55),w-20,1.1*ES,'#5c4a31',ACCENT,2)
            for k in range(9):
                path([(x0+18+k*((w-36)/9),ey(2.5)),(x0+18+k*((w-36)/9),ey(1.4))],stroke=ACCENT,width=3)
    if kind in ('panel','grille'):
        rect(x0+6,ey(4.0),w-12,9,OPEN,'none')          # light in the trough reveal
for r in ribs:
    rect(ex(r)-0.25*ES,ey(4.25),0.5*ES,3.0*ES,'#2c4e66',STRUCT,2)
path([(ex(-12)-0.25*ES,ey(4.25)),(ex(-12)-0.25*ES,ey(1.25)),(ex(-12)+0.25*ES,ey(1.25)),(ex(-12)+0.25*ES,ey(4.25))],
     'none',STRUCT,2,False,'5 6',.6)
text(ex(-12),ey(4.25)-32,'rib suppressed',13,MUTED,anchor='middle')
rect(ex(-15.5),ey(4.25)-5,2.0*ES,0.625*ES+5,'none',ACCENT,2,'6 5')
text(ex(-16.5),ey(4.25)-14,'2.0 × 2.0 CEILING HATCH RESERVED',13,ACCENT,'bold','middle')
path([(EX,EB),(EX+21*ES,EB)],stroke='#c5d0d9',width=5)
figure(ex(-1.5),EB,ES)
for z in (0,-3,-6,-9,-12,-15,-18,-21):
    text(ex(z),EB+22,f'{z}',13,MUTED,anchor='middle')
text(ex(-10.5),EB+44,'Z (metres, north is negative)',14,MUTED,anchor='middle')

nx=1140
text(nx,664,'WHY 4.0 m PITCH',18,STRUCT,'bold')
for k,s in enumerate(['One rib every four 1 m texture repeats, so the rib',
                      'always lands on a texture seam.']):
    text(nx,688+k*22,s,15)
text(nx,746,'WHY A 3.75 m CROWN',18,STRUCT,'bold')
for k,s in enumerate(['6.00 wide, but the walking lane is still 4.00.',
                      'Rib beam soffit 3.50 clears the 3.2 envelope by 0.30.']):
    text(nx,770+k*22,s,15)
text(nx,828,'LIGHT IS STILL OPEN',18,OPEN,'bold')
for k,s in enumerate(['Deferred until the section is signed off. The ceiling',
                      'piece is the obvious carrier, as a swap-out.']):
    text(nx,852+k*22,s,15)

hrule(906)

# --------------------------------------------------------------------- kit
text(60,942,'BAY INSERT KIT — the section never changes, the bay does',24,TEXT,'bold')
text(60,966,'Swap-outs replace the 1.25 – 2.50 m panel zone only, so the floor, ceiling and rib pieces are untouched.',16,MUTED)

KW,KG=245,12; KX=110; KY=986; KH=160
kit=[('PANEL',INFILL,'Flat panel behind the rib plane.','The quiet default. Cheapest bay.'),
     ('GRILLE',ACCENT,'Louvres set 0.125 m deeper.','Honest home for a wall hatch.'),
     ('EQUIPMENT',ACCENT,'Cabinets inside the panel zone.','Never crosses the rib plane.'),
     ('RECESS',CLEAR,'Full depth to floor, 0.50 m.','Standing cover. Plinth stops.'),
     ('WINDOW',GLASS,'Sill 1.25, head 2.50, chamfered reveal.','Glazing 0.75 m outboard.'),
     ('DOOR',OPEN,'2.00 × 2.46 DoorModule, centred.','Ribs are the wall returns.')]
for i,(name,col,l1,l2) in enumerate(kit):
    x=KX+i*(KW+KG)
    rect(x,KY,KW,KH,PANEL,RULE,1)
    text(x+12,KY+25,name,18,col,'bold')
    ix,iy,iw,ih=x+14,KY+38,KW-28,76
    rect(ix,iy,iw,ih,DEEP,LINE,1)
    rect(ix,iy,14,ih,'#2c4e66',STRUCT,1); rect(ix+iw-14,iy,14,ih,'#2c4e66',STRUCT,1)
    a,b=ix+16,ix+iw-16
    if name=='PANEL':
        rect(a+6,iy+13,(b-a)-12,ih-34,'#2a3a47',INFILL,2)
    elif name=='GRILLE':
        rect(a+6,iy+11,(b-a)-12,ih-32,'#5c4a31',ACCENT,2)
        for k in range(8): path([(a+14+k*((b-a-28)/8),iy+17),(a+14+k*((b-a-28)/8),iy+ih-24)],stroke=ACCENT,width=2)
    elif name=='EQUIPMENT':
        rect(a+4,iy+ih-42,(b-a)-8,28,'#6a4f30',ACCENT,2)
        rect(a+18,iy+13,(b-a)-56,21,'#8a6437',ACCENT,1)
    elif name=='RECESS':
        rect(a,iy+7,(b-a),ih-7,'#24473d',CLEAR,2)
        figure(x+KW/2,iy+ih,30,CLEAR)
    elif name=='WINDOW':
        rect(a+6,iy+15,(b-a)-12,ih-42,'#1e4a58',GLASS,2)
        parts.append(f'<circle cx="{x+KW/2:.0f}" cy="{iy+34:.0f}" r="9" fill="{MARS}" opacity="0.9"/>')
    else:
        rect(a+16,iy+9,(b-a)-32,ih-9,'#3a3524',OPEN,2)
        path([((a+b)/2,iy+9),((a+b)/2,iy+ih)],stroke=OPEN,width=2,dash='5 4')
    rect(ix,iy+ih-9,iw,9,'#3b4c5c',PLINTH,1)
    text(x+12,KY+132,l1,14)
    text(x+12,KY+150,l2,14,MUTED)

PY_=KY+KH+16
rect(KX,PY_,KW*6+KG*5,116,PANEL,RULE,1)
text(KX+16,PY_+28,'PORTAL BAY',19,OPEN,'bold')
text(KX+16,PY_+52,'Two bays merged',15,MUTED)
text(KX+16,PY_+70,'by dropping one rib.',15,MUTED)
px0=KX+190; pxs=46
rect(px0,PY_+30,5.5*pxs,42,DEEP,LINE,1)
rect(px0,PY_+30,0.5*pxs,42,'#2c4e66',STRUCT,1); rect(px0+5.0*pxs,PY_+30,0.5*pxs,42,'#2c4e66',STRUCT,1)
rect(px0+0.75*pxs,PY_+30,4.0*pxs,42,'#3a3524',OPEN,2)
text(px0+2.75*pxs,PY_+57,'4.00 opening',14,OPEN,'bold','middle')
text(px0,PY_+94,'5.50 m clear between flanking ribs  ·  0.75 bay + 0.50 rib = 1.25 m return each side',15,MUTED)
text(px0+5.5*pxs+40,PY_+30,'This is the systemic win: the rib rhythm satisfies the project’s “1 m of solid wall beyond a frame”',16)
text(px0+5.5*pxs+40,PY_+52,'rule automatically, at every opening, without anyone measuring it. Single-bay doors serve side',16)
text(px0+5.5*pxs+40,PY_+74,'rooms; portal bays carry main routes and junctions. It also gives openings a visible hierarchy.',16)

hrule(1298)

# -------------------------------------------------------------------- plan
PS=16; PX0=110; PZ0=1350
sx=lambda x: PX0+(x+15)*PS
sz=lambda z: PZ0+(z+31)*PS
text(60,1334,'CIRCUIT PLAN — one walk that exercises every part of the kit',24,TEXT,'bold')
for k,(c,lab) in enumerate([(STRUCT,'rib / structure'),(INFILL,'bay infill'),(PLINTH,'plinth'),
                            (ACCENT,'service insert'),(CLEAR,'clear lane / alcove'),
                            (GLASS,'glazing'),(OPEN,'opening'),(MARS,'exterior volume')]):
    cxl=60+k*196
    rect(cxl,1350,13,13,c); text(cxl+20,1362,lab,14,MUTED)

rect(sx(2),sz(-31),(15.25-2)*PS,(-21-GLAZE+31)*PS,'#3a2018',MARS,2,'7 6')
rect(sx(15.5),sz(-31),(21-15.5)*PS,(-16+31)*PS,'#3a2018',MARS,2,'7 6')
for cxp,cyp,wp,hp in [(5.0,-27.2,3.4,.6),(9.8,-26.8,2.0,1.4),(18.2,-24.5,1.6,2.4),(18.4,-19.5,1.0,3.0)]:
    rect(sx(cxp-wp/2),sz(cyp-hp/2),wp*PS,hp*PS,'#6b3a29',MARS,1)
parts.append(f'<circle cx="{sx(13):.0f}" cy="{sz(-29):.0f}" r="8" fill="{MARS}"/>')
for ax,az in [(5.5,-26.2),(8.0,-26.2)]:
    path([(sx(ax),sz(az-0.7)),(sx(ax),sz(az+1.0))],stroke=MARS,width=2)
    path([(sx(ax)-4,sz(az+0.5)),(sx(ax),sz(az+1.0)),(sx(ax)+4,sz(az+0.5))],stroke=MARS,width=2)

def shell(x0,x1,z0,z1):
    rect(sx(x0),sz(z0),(x1-x0)*PS,(z1-z0)*PS,PANEL,LINE,2)
shell(-HW,HW,-24.25,3)
shell(-HW,15.25,-24.25,-17.75)
shell(-9.25,0,-15.25,-8.75)
rect(sx(-10.25),sz(-8.75),5.25*PS,5*PS,DEEP,LINE,2,'6 5')

rect(sx(-2.25),sz(-24.25),4.5*PS,(24.25+3)*PS,'#233543')
rect(sx(-2.25),sz(-23.25),(15.25+2.25)*PS,4.5*PS,'#233543')
rect(sx(-9.25),sz(-14.25),9.25*PS,4.5*PS,'#233543')
rect(sx(-HW),sz(-8.75),1.0*PS,2.5*PS,'#24473d',CLEAR,2)
rect(sx(2.25),sz(-20.75),1.0*PS,2.5*PS,'#24473d',CLEAR,2)
path([(sx(0),sz(3)),(sx(0),sz(-21))],stroke=CLEAR,width=1,dash='9 7',opacity=.7)
path([(sx(-9.25),sz(-12)),(sx(0),sz(-12))],stroke=CLEAR,width=1,dash='9 7',opacity=.7)
path([(sx(0),sz(-21)),(sx(15.25),sz(-21))],stroke=CLEAR,width=1,dash='9 7',opacity=.7)

for z in (0,-4,-8,-16,-20): rect(sx(-HW),sz(z-0.25),2*HW*PS,0.5*PS,'#2c4e66',STRUCT,1)
for x in (4,8,12): rect(sx(x-0.25),sz(-24.25),0.5*PS,2*HW*PS,'#2c4e66',STRUCT,1)
for x in (-4,-8): rect(sx(x-0.25),sz(-15.25),0.5*PS,2*HW*PS,'#2c4e66',STRUCT,1)
path([(sx(HW),sz(-17.75)),(sx(HW),sz(-19.4)),(sx(1.6),sz(-17.75))],'#2c4e66',STRUCT,2,True)
path([(sx(-HW),sz(-24.25)),(sx(-HW),sz(-22.6)),(sx(-1.6),sz(-24.25))],'none',STRUCT,2,False,'5 4')

rect(sx(-HW),sz(-14),0.5*PS,4*PS,'#3a3524',OPEN,2)
rect(sx(-6.5),sz(-8.75),2*PS,0.5*PS,'#3a3524',OPEN,2)
rect(sx(4.25),sz(-21-GLAZE),3.5*PS,0.25*PS,'#1e4a58',GLASS,2)
rect(sx(8.25),sz(-21-GLAZE),3.5*PS,0.25*PS,'#1e4a58',GLASS,2)
rect(sx(15.25),sz(-23),0.25*PS,4*PS,'#1e4a58',GLASS,2)
rect(sx(-1),sz(-17.5),2*PS,2*PS,'none',ACCENT,2,'5 4')
for z0,z1,xw in [(-4.25,-7.75,-HW),(-16.25,-19.75,-HW),(-8.25,-11.75,2.75)]:
    rect(sx(xw),sz(z0),0.5*PS,(z1-z0)*PS,ACCENT,'none',0,None,.9)
rect(sx(-7.75),sz(-15.25),3.5*PS,0.5*PS,ACCENT,'none',0,None,.9)
for x0,x1 in [(4.25,7.75),(8.25,11.75)]:
    rect(sx(x0),sz(-18.25),(x1-x0)*PS,0.5*PS,ACCENT,'none',0,None,.9)

figure(sx(0),sz(2.4),14,CLEAR)
for n,mx_,mz_ in [(1,0,0.6),(2,-2.9,-7.5),(3,-2.6,-12),(4,-7.5,-9.5),(5,0,-16.5),
                  (6,2.1,-20.0),(7,5.0,-24.2),(8,14.2,-21.0),(9,18.6,-28.6)]:
    marker(n,sx(mx_),sz(mz_),CLEAR if n in (1,2) else TEXT)

mx=790
text(mx,1354,'KEY',20,TEXT,'bold')
for k,s in enumerate(['Spawn. The spine, ribs every 4 m.',
     'Alcove bay — the section gives ground below 2 m.',
     'Portal bay carrying the 4.0 × 3.2 T opening.',
     'West branch, ending in a door bay + stub.',
     'Sealed 2.0 × 2.0 ceiling hatch, between ribs, clear of light.',
     'Corner — mitre outside, solid rib block inside.',
     'Two window bays, outboard side only.',
     '6 m portal bay ending in a 4.0 × 2.0 viewport.',
     'Mars exterior: sealed, not traversable, one raking light.']):
    marker(k+1,mx+12,1382+k*26,MUTED)
    text(mx+32,1387+k*26,s,16)

text(mx,1622,'THE WALK',20,TEXT,'bold')
for k,(s_,c) in enumerate([('Spawn, then north up the spine — the bays teach the rhythm',TEXT),
      ('before anything unusual happens. The alcove is the first time',TEXT),
      ('section gives ground. Judge it as cover, not decoration.',MUTED),
      ('',TEXT),
      ('The T is a portal bay in the same rhythm: its flanking ribs',TEXT),
      ('are the wall returns, for free.',MUTED),
      ('',TEXT),
      ('The corner is the real test — the chamfers have to mitre — so',TEXT),
      ('the knee gets a mitre outside and a solid rib block inside.',TEXT),
      ('The end viewport is the one deliberate rule break.',MUTED)]):
    text(mx,1650+k*23,s_,16,c)

text(60,1898,'BUILD ORDER — each stage is walkable and answers exactly one question',19,STRUCT,'bold')
for k,s in enumerate([
  '1   Spine only, panel bays throughout, flat neutral light.',
  '2   Inserts, portal bay, T, corner, door bay.',
  '3   Trough reveal lighting, alternating bays.',
  '4   Mars volume, window bays, end viewport.']):
    text(60,1924+k*23,s,16)
for k,s in enumerate([
  'Does the 4.0 m rhythm read, and is 5.50 × 3.75 the right size?',
  'Does the kit hold together, and does the corner actually resolve?',
  'Do the panel swap-outs carry enough interest on their own?',
  'Does the red light do the work — is a glimpse of Mars enough?']):
    text(620,1924+k*23,s,16,MUTED)

text(60,2040,'REVISION 06 / circuit routing provisional · the revision 05 stage 1 build is superseded · section detail in architecture-lab-section.png',17,MUTED)

parts.append('</svg>')
svg = root/'docs/architecture-lab-plan.svg'
svg.write_text('\n'.join(parts), encoding='utf-8')

ink = shutil.which('inkscape') or r'C:\Program Files\Inkscape\bin\inkscape.exe'
if Path(ink).exists():
    subprocess.run([ink, str(svg), '--export-type=png', '--export-filename',
                    str(root/'docs/architecture-lab-plan.png'), '--export-width', str(W)],
                   check=True, capture_output=True)
    print('wrote svg + png')
else:
    print('wrote svg; Inkscape not found, export the PNG manually')
