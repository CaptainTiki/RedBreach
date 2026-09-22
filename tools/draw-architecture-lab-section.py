"""Draw the paper section study only. Does not generate or edit game geometry.

Revision 06: the corridor as four reusable pieces - floor, wall, ceiling and a
drop-in rib - shown assembled, exploded and in elevation. Writes the SVG;
rasterises with Inkscape when it is installed.
"""
from pathlib import Path
import html, shutil, subprocess, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import architecture_lab_section as S

S.check()
root = Path(__file__).resolve().parents[1]
W, H = 1700, 1880

BG='#111b25'; PANEL='#1b2a36'; DEEP='#15212b'; RULE='#3c4b59'
TEXT='#e5edf3'; MUTED='#a9bac9'; LINE='#9db1c1'
FLOORC='#c58f6a'; WALLC='#7fb6d9'; CEILC='#9d8fd0'; RIBC='#e8a15c'
OPEN='#ffe9b8'; CLEAR='#6fd3a8'; GLASS='#7fd6ea'

parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>']

def text(x,y,s,size=18,color=TEXT,weight='normal',anchor='start'):
    parts.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" '
                 f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(s)}</text>')

def poly(points,fill='none',stroke=LINE,width=2,close=True,dash=None,opacity=1.0):
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

def dot(x,y,r=4.5,c=TEXT):
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{BG}" stroke="{c}" stroke-width="2"/>')

def hrule(y,x0=60,x1=W-60):
    poly([(x0,y),(x1,y)],stroke=RULE,width=1,close=False)

def figure(cx,base,sc,color='#9dadb8'):
    parts.append(f'<circle cx="{cx:.1f}" cy="{base-1.62*sc:.1f}" r="{0.11*sc:.1f}" fill="{color}"/>')
    poly([(cx,base-1.5*sc),(cx,base-0.72*sc),(cx-0.22*sc,base)],stroke=color,width=3,close=False)
    poly([(cx,base-0.72*sc),(cx+0.22*sc,base)],stroke=color,width=3,close=False)
    poly([(cx-0.25*sc,base-1.32*sc),(cx+0.25*sc,base-1.32*sc)],stroke=color,width=3,close=False)

def dim_v(x,y0,y1,label,color=MUTED,side=1):
    poly([(x,y0),(x,y1)],stroke=color,width=1,close=False)
    for y in (y0,y1): poly([(x-5,y),(x+5,y)],stroke=color,width=1,close=False)
    if label: text(x+8*side,(y0+y1)/2+5,label,13,color,anchor='start' if side>0 else 'end')

def dim_h(y,x0,x1,label,color=MUTED,above=True):
    poly([(x0,y),(x1,y)],stroke=color,width=1,close=False)
    for x in (x0,x1): poly([(x,y-5),(x,y+5)],stroke=color,width=1,close=False)
    text((x0+x1)/2,y-9 if above else y+18,label,13,color,anchor='middle')

# solids, in metres, as closed cross sections
FLOOR_SOLID   = [(0,S.SUBFLOOR_Y),(S.FLOOR_HALF,S.SUBFLOOR_Y),(S.FLOOR_HALF,0),(0,0)]
WALL_SOLID    = list(S.WALL)+[(S.SHELL_BACK,S.CEIL_Y),(S.SHELL_BACK,S.SUBFLOOR_Y),(S.FLOOR_HALF,S.SUBFLOOR_Y)]
CEILING_SOLID = [(0,S.CEIL_Y),(S.SHELL_BACK,S.CEIL_Y),(S.SHELL_BACK,S.CEILING_TOP),(0,S.CEILING_TOP)]
# The closing run must include the wall's floor point, or the solid cuts
# the corner off and leaves a gap where the toe meets the floor.
RIB_SOLID     = list(S.RIB)+[(0,S.CEIL_Y)]+list(reversed(S.WALL))

# ------------------------------------------------------------------ header
text(60,58,'ARCHITECTURE LAB / REVISION 06 — FOUR PIECES',33,TEXT,'bold')
text(60,92,'A floor, a wall and a ceiling make half a corridor. Mirror them for the other half. A rib drops in every 4 m without changing any of the three.',20)
text(60,118,'Nine facets per half instead of twenty-two. Chamfers, not steps. Every vertex is a multiple of 0.125 m (4 map units at 32 u/m).',17,MUTED)

# ------------------------------------------------- A: assembled + elevation
SC=100; BASE=640; CX=440
tx=lambda q:(CX+q[0]*SC, BASE-q[1]*SC)
text(60,170,'ASSEMBLED',24,TEXT,'bold')
text(60,194,'Both halves plus a rib at a station.',16,MUTED)
for sgn in (1,-1):
    m=lambda q,sgn=sgn:(CX+sgn*q[0]*SC, BASE-q[1]*SC)
    poly([m(q) for q in FLOOR_SOLID],'#5a3f2f',FLOORC,2)
    poly([m(q) for q in WALL_SOLID],'#27455c',WALLC,2)
    poly([m(q) for q in CEILING_SOLID],'#3a3355',CEILC,2)
    poly([m(q) for q in RIB_SOLID],'#6a4f30',RIBC,2)
poly([tx((-S.LANE_HALF,0)),tx((-S.LANE_HALF,S.LANE_HEIGHT)),tx((S.LANE_HALF,S.LANE_HEIGHT)),tx((S.LANE_HALF,0))],
     stroke=CLEAR,width=2,close=False,dash='8 6')
poly([tx((-S.FLOOR_HALF,0)),tx((S.FLOOR_HALF,0))],stroke='#d8e2ea',width=5,close=False)
figure(CX,BASE,SC)
text(CX,BASE-1.84*SC,'4.0 × 3.2 clear',15,CLEAR,anchor='middle')
for p_ in (S.WALL[0], S.WALL[-1]):
    dot(CX+p_[0]*SC, BASE-p_[1]*SC, 6, TEXT)
text(CX+S.WALL[0][0]*SC+14, BASE-S.WALL[0][1]*SC+20,
     f'floor meets wall ({S.WALL[0][0]:g}, {S.WALL[0][1]:g})',13,TEXT)
text(CX+S.WALL[-1][0]*SC+14, BASE-S.WALL[-1][1]*SC-8,
     f'wall meets ceiling ({S.WALL[-1][0]:g}, {S.WALL[-1][1]:g})',13,TEXT)
dim_h(BASE+62,tx((-S.WIDEST,0))[0],tx((S.WIDEST,0))[0],'6.00 widest interior',MUTED,False)
dim_v(tx((S.WIDEST,0))[0]+46,tx((0,0))[1],tx((0,S.CEIL_Y))[1],'3.75 crown')
text(tx((S.WIDEST,0))[0]+46,tx((0,S.RIB_SOFFIT_Y))[1]-6,'3.50 rib soffit',13,RIBC)

# long elevation
ES=40; EB=490; EX=900
ey=lambda h: EB-h*ES
ex=lambda z: EX+z*ES
text(900,170,'ELEVATION — RIBS AT 4 m',24,TEXT,'bold')
text(900,194,'Four 1 m texture repeats per bay.',16,MUTED)
text(900,216,'The rib runs floor to ceiling on a battered base.',16,MUTED)
rect(EX,ey(S.CEIL_Y),12*ES,S.CEIL_Y*ES,DEEP,LINE,2)
rect(EX,ey(1.0),12*ES,1.0*ES,'#27455c',WALLC,1)
rect(EX,ey(S.CEIL_Y),12*ES,(S.CEIL_Y-S.RIB_SOFFIT_Y)*ES,'#3a3355',CEILC,1)
for z0 in (0,4,8):
    rect(ex(z0)+0.25*ES+5,ey(2.5),4*ES-0.5*ES-10,1.25*ES,'#2a3a47',WALLC,1)
    text(ex(z0)+2*ES,ey(1.76),'panel swap-out',13,MUTED,anchor='middle')
for z in (0,4,8,12):
    rect(ex(z)-0.25*ES,ey(S.RIB_SOFFIT_Y),0.5*ES,S.RIB_SOFFIT_Y*ES,'#6a4f30',RIBC,2)
    poly([(ex(z)-0.25*ES,ey(1.25)),(ex(z)+0.25*ES,ey(1.25))],stroke=RIBC,width=1,close=False,dash='4 4')
text(ex(11.6),ey(0.45),'battered base',12,RIBC,anchor='end')
text(ex(11.6),ey(2.2),'shaft',12,RIBC,anchor='end')
poly([(EX,EB),(EX+12*ES,EB)],stroke='#d8e2ea',width=5,close=False)
figure(ex(1.3),EB,ES)
dim_h(ey(S.CEIL_Y)-14,ex(0),ex(4),'4.00 pitch')
dim_v(ex(12)+26,ey(0),ey(1.0),'1.00 plinth')
text(EX,EB+26,'0',13,MUTED,anchor='middle')
text(ex(12),EB+26,'12 m',13,MUTED,anchor='middle')

nx=1420
text(nx,290,'WHAT CHANGED',18,TEXT,'bold')
for k,s in enumerate(['Chamfers replace the stepped','setbacks. Nothing sits at 45° where','it rises outward and the player could','reach it: those go to 51.34°, 56.31°','or 63.43° instead.','','The rib runs floor to ceiling. Its','toe is vertical to knee height, so','the capsule never meets a slope low.','','6.00 × 3.75. Widened 0.50 m purely','to buy the rib base a 0.50 m flare,','with the toes still 4.00 m apart.']):
    text(nx,314+k*22,s,15,MUTED if s.startswith(('setbacks','everywhere','kick','can act','at 1.00','the capsule never meets a slope low.','4.25','not a')) else TEXT)

hrule(726)

# ------------------------------------------------------ B: the three pieces
text(60,764,'HALF A CORRIDOR — THE THREE PIECES',24,TEXT,'bold')
text(60,788,'Each is a separate reusable brush. They mate at the two ringed points, so any one can be swapped for a special without touching the others.',16,MUTED)

BS=120

def slab(x0,y0,solid,col,fill):
    lo_x = min(q[0] for q in solid); lo_y = min(q[1] for q in solid)
    m = lambda q: (x0+(q[0]-lo_x)*BS, y0-(q[1]-lo_y)*BS)
    poly([m(q) for q in solid],fill,col,2)
    return m

# FLOOR
text(110,848,'FLOOR',19,FLOORC,'bold')
slab(110,912,FLOOR_SOLID,FLOORC,'#5a3f2f')
dim_h(926,110,110+2.25*BS,'2.50 half plate / 5.00 overall',FLOORC,False)
dim_v(96,912,912-0.375*BS,'0.375',FLOORC,-1)
text(110+2.25*BS+18,880,'top face is the walking surface at Y = 0',14,MUTED)
text(110+2.25*BS+18,902,'swap for grating, a hatch or a ramp',14,MUTED)

# CEILING
text(110,1022,'CEILING',19,CEILC,'bold')
slab(110,1090,CEILING_SOLID,CEILC,'#3a3355')
dim_h(1104,110,110+2.25*BS,'2.25 visible soffit / 4.50 overall',CEILC,False)
dim_h(1132,110,110+3.50*BS,'3.50 overall, capping the wall',CEILC,False)
text(110+3.25*BS+18,1054,'soffit sits at 3.75',14,MUTED)
text(110+3.25*BS+18,1076,'swap for a service run, light or hatch',14,MUTED)

text(110,1200,'The two pieces above are plain slabs. All the shape is in the wall,',15,MUTED)
text(110,1222,'which is why it is the only one of the three worth drawing large.',15,MUTED)
text(110,1258,f'Mating points: floor meets wall at ({S.WALL[0][0]:g}, {S.WALL[0][1]:g}); wall meets ceiling',15,MUTED)
text(110,1280,f'at ({S.WALL[-1][0]:g}, {S.WALL[-1][1]:g}). Both are ringed on the assembled section above.',15,MUTED)

# --- the wall, drawn large with every facet called out
WS=118; WX=760; WY=1272
wm=lambda q:(WX+(q[0]-2.0)*WS, WY-q[1]*WS)
text(640,764,'',14)
poly([wm(q) for q in WALL_SOLID],'#27455c',WALLC,2)
poly([wm(q) for q in S.WALL],'none','#dff0ff',3,False)
for p in S.WALL:
    dot(*wm(p),4,'#dff0ff')
poly([wm((2.0,0)),wm((2.25,0))],stroke='#d8e2ea',width=5,close=False)
poly([wm((2.0,0)),wm((2.0,S.LANE_HEIGHT))],stroke=CLEAR,width=2,close=False,dash='7 6')
text(wm((2.0,1.4))[0]-8,wm((2.0,1.4))[1],'lane edge',13,CLEAR,anchor='end')
fl=S.facets(S.WALL)
for i,(aa,bb,ln,ang) in enumerate(fl):
    mid=((aa[0]+bb[0])/2,(aa[1]+bb[1])/2)
    px,py=wm(mid)
    dot(px-26,py,11,WALLC); text(px-26,py+5,str(i+1),13,WALLC,'bold','middle')
text(WX-92,1300,'WALL — seven facets',19,WALLC,'bold')

tx0=1020
text(tx0,830,'THE WALL PIECE',19,WALLC,'bold')
text(tx0,854,'Panel zone 1.25 – 2.50 m is the only part that swaps.',15,MUTED)
hdr=['','facet','from','to','angle']
names=['base kick','plinth face','chamfer out','main panel','chamfer in','upper wall','ceiling chamfer']
rows=[]
for _i,(_a,_b,_l,_ang) in enumerate(S.facets(S.WALL)):
    rows.append((str(_i+1),names[_i],f'({_a[0]:g}, {_a[1]:g})',f'({_b[0]:g}, {_b[1]:g})',
                 f'{_ang:.2f}°' if _ang is not None else 'vertical'))
cols=[0,46,196,356,516]
for k,h in enumerate(hdr[1:]):
    text(tx0+cols[k+1],892,h,14,MUTED)
poly([(tx0,900),(tx0+600,900)],stroke=RULE,width=1,close=False)
for r,row in enumerate(rows):
    y=924+r*26
    dot(tx0+12,y-5,11,WALLC); text(tx0+12,y,row[0],13,WALLC,'bold','middle')
    hot = row[0] in ('1','4')
    for k,v in enumerate(row[1:]):
        text(tx0+cols[k+1],y,v,15,TEXT if hot else MUTED)
text(tx0,1132,'Facets 1 and 3 rise outward low enough that the capsule could try to',15,MUTED)
text(tx0,1153,'stand on them, so both are steeper than the 45° floor_max_angle default.',15,MUTED)
text(tx0,1174,'The 45° chamfers are all overhangs, which cannot be stood on at all.',15,MUTED)
text(tx0,1216,'Wall solids back to x = 3.50, so the piece is 0.50 – 1.25 m thick and',15,MUTED)
text(tx0,1237,'tiles against the next bay with no coplanar overlap.',15,MUTED)

hrule(1324)

# --------------------------------------------------------- C: rib + swaps
RS=95; RB=1770; RX=230
text(60,1366,'THE RIB',24,RIBC,'bold')
text(60,1390,'Five facets. Drops in without altering the wall.',16,MUTED)
rm=lambda q:(RX+q[0]*RS, RB-q[1]*RS)
poly([rm(q) for q in S.WALL],'none',WALLC,2,False,'6 5',.75)
poly([rm(q) for q in RIB_SOLID],'#6a4f30',RIBC,2)
for p in S.RIB:
    dot(*rm(p),3.5,RIBC)
dot(*rm(S.RIB[0]),7,OPEN)
text(rm(S.RIB[0])[0]+18, rm(S.RIB[0])[1]-10,'toe sits on the lane line — opposite toes ARE the 4.00 m clear width',14,OPEN)
text(rm((2.25,1.85))[0]+16, rm((2.25,1.85))[1],'shaft 0.50 proud of the panel',13,RIBC)
text(rm((2.0,3.5))[0]+16, rm((2.0,3.5))[1]-8,'beam soffit 3.50',13,RIBC)
text(rm((2.5,3.75))[0]+16, rm((2.5,3.75))[1]+4,'wall behind (dashed) — proud at every height',13,WALLC)
poly([rm((-0.1,0)),rm((3.0,0))],stroke='#d8e2ea',width=4,close=False)
text(rm((0.0,0))[0], rm((0.0,0))[1]+24,'toe is vertical to knee height, then batters 0.50 m back onto the shaft  ·  51.34°',13,MUTED)

sx=800
text(sx,1362,'PANEL SWAP-OUTS',24,WALLC,'bold')
text(sx,1386,'Each replaces the 1.25 – 2.50 m panel and nothing else, so the piece still mates.',16,MUTED)
TW,TH,TG=150,146,20
for i,(name,desc) in enumerate(S.SWAPS):
    x=sx+i*(TW+TG)
    rect(x,1406,TW,TH,PANEL,RULE,1)
    ix,iy,iw,ih=x+14,1420,TW-28,100
    rect(ix,iy,iw,ih,DEEP,LINE,1)
    rect(ix,iy+ih-24,iw,24,'#27455c',WALLC,1)
    a,b=ix+8,ix+iw-8
    if name.startswith('W1'):
        rect(a,iy+22,b-a,ih-54,'#2a3a47',WALLC,2)
    elif name.startswith('W2'):
        poly([(a,iy+22),(b,iy+22),(b-8,iy+30),(a+8,iy+30)],'#20303c',WALLC,2)
        rect(a+8,iy+30,b-a-16,ih-70,'#20303c',WALLC,2)
    elif name.startswith('W3'):
        rect(a+5,iy+24,b-a-10,ih-58,'#5c4a31',RIBC,2)
        for k in range(6):
            poly([(a+12+k*((b-a-24)/6),iy+30),(a+12+k*((b-a-24)/6),iy+ih-36)],stroke=RIBC,width=2,close=False)
    elif name.startswith('W4'):
        poly([(a,iy+22),(b,iy+22),(b-8,iy+30),(a+8,iy+30)],'#1e4a58',GLASS,2)
        rect(a+8,iy+30,b-a-16,ih-70,'#1e4a58',GLASS,2)
    else:
        rect(a+4,iy+10,b-a-8,ih-10,'#3a3524',OPEN,2)
    text(x+14,1542,name,15,TEXT,'bold')
for k,(name,desc) in enumerate(S.SWAPS):
    text(sx,1586+k*21,name,14,TEXT,'bold')
    text(sx+118,1586+k*21,desc,14,MUTED)
text(sx,1708,'Floor and ceiling swap the same way: a grating strip, a service run, a light panel, a sealed hatch.',15,MUTED)
text(sx,1730,'The corridor envelope never changes, so nothing downstream has to be re-measured.',15,MUTED)

text(60,1850,'REVISION 06 / BUILT AND LIT — one 24.5 m run, 151 brushes, 1,037 validation checks pass · corners and the circuit remain open',17,MUTED)

parts.append('</svg>')
svg = root/'docs/architecture-lab-section.svg'
svg.write_text('\n'.join(parts), encoding='utf-8')

ink = shutil.which('inkscape') or r'C:\Program Files\Inkscape\bin\inkscape.exe'
if Path(ink).exists():
    subprocess.run([ink, str(svg), '--export-type=png', '--export-filename',
                    str(root/'docs/architecture-lab-section.png'), '--export-width', str(W)],
                   check=True, capture_output=True)
    print('wrote svg + png')
else:
    print('wrote svg; Inkscape not found, export the PNG manually')
