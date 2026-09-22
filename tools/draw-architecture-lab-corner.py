"""Draw the paper corner study only. Does not generate or edit game geometry.

Three 90 degree corner variants in plan, plus the repetition test that decides
how long a straight run may be. Imports both the section and the corner module
so the drawing cannot disagree with either. Writes the SVG; rasterises with
Inkscape when it is installed.
"""
from pathlib import Path
import html, shutil, subprocess, sys, math
sys.path.insert(0, str(Path(__file__).resolve().parent))
import architecture_lab_section as S
import architecture_lab_corner as C

S.check()
C.check()
root = Path(__file__).resolve().parents[1]
W, H = 1700, 2030

BG='#111b25'; PANEL='#1b2a36'; DEEP='#15212b'; RULE='#3c4b59'
TEXT='#e5edf3'; MUTED='#a9bac9'; LINE='#9db1c1'
WALLC='#7fb6d9'; RIBC='#e8a15c'; CLEAR='#6fd3a8'; PLATEC='#8595a4'
WARN='#e8756c'; GOOD='#6fd3a8'; SIGHT='#ffe9b8'

# Plan cell geometry is needed for the clip paths, so it is declared before any
# drawing happens and the preamble is emitted exactly once, in document order:
# svg -> defs -> background -> content.
PX0, PY0 = 74, 250          # PY0 = top of the plan area itself
CELLW, GAP = 500, 26
PLAN = 448                  # the plan area is square
SC = PLAN/18.0              # 18 m across
VIEW_X = (-11.0, 7.0)
VIEW_Z = (-7.0, 11.0)

clips = '\n'.join(
    f'<clipPath id="pc{i}"><rect x="{PX0 + i*(CELLW+GAP)}" y="{PY0}" '
    f'width="{PLAN}" height="{PLAN}"/></clipPath>' for i in range(3))

parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<defs>{clips}</defs>',
       f'<rect width="{W}" height="{H}" fill="{BG}"/>']

def text(x,y,s,size=18,color=TEXT,weight='normal',anchor='start'):
    parts.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" '
                 f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(s)}</text>')

def poly(points,fill='none',stroke=LINE,width=2,close=True,dash=None,opacity=1.0,clip=None):
    d='M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in points)+(' Z' if close else '')
    da=f'stroke-dasharray="{dash}" ' if dash else ''
    cp=f'clip-path="url(#{clip})" ' if clip else ''
    parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {da}{cp}'
                 f'opacity="{opacity}" stroke-linejoin="miter"/>')

def rect(x,y,w,h,fill='none',stroke='none',width=1,dash=None,opacity=1.0,rx=0,clip=None):
    if w<0: x,w = x+w,-w
    if h<0: y,h = y+h,-h
    da=f'stroke-dasharray="{dash}" ' if dash else ''
    cp=f'clip-path="url(#{clip})" ' if clip else ''
    parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{width}" {da}{cp}opacity="{opacity}"/>')

def dot(x,y,r=4.5,c=TEXT,fill=BG):
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{c}" stroke-width="2"/>')

def circ(x,y,r,fill,opacity=1.0,clip=None):
    cp=f'clip-path="url(#{clip})" ' if clip else ''
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" {cp}opacity="{opacity}"/>')

def hrule(y,x0=60,x1=W-60):
    poly([(x0,y),(x1,y)],stroke=RULE,width=1,close=False)

def wrap(s,n):
    out=[];cur=''
    for w_ in s.split():
        if len(cur)+len(w_)+1>n: out.append(cur); cur=w_
        else: cur=(cur+' '+w_).strip()
    if cur: out.append(cur)
    return out

# ---------------------------------------------------------------- header
text(60,60,'ARCHITECTURE LAB / THE CORNER — three variants in plan',34,TEXT,'bold')
text(60,92,'Revision 06 kit, turned through 90 degrees. Paper only: this script writes no map.',18,MUTED)
text(60,118,'Plan view. Corridor A enters from the left, corridor B leaves at the bottom. '
            'OUTER corner top-right, INNER elbow bottom-left — matching the sketch.',16,MUTED)

lx=60; ly=148
for label,col,desc in (('WIDEST',WALLC,f'{2*C.WIDE:.2f} m'),('PLATE',PLATEC,f'{2*C.PLATE:.2f} m'),
                       ('LANE',CLEAR,f'{2*C.LANE:.2f} m'),('RIB',RIBC,'0.50 m proud')):
    rect(lx,ly-11,13,13,col,'none')
    text(lx+20,ly,label,14,TEXT,'bold'); text(lx+20+len(label)*9+10,ly,desc,14,MUTED)
    lx += 20+len(label)*9+10+len(desc)*8+40
hrule(ly+20)

# ---------------------------------------------------------------- the plans
def mk(ox,oy):
    def f(x,z):
        return (ox + (x - VIEW_X[0])*SC, oy + (z - VIEW_Z[0])*SC)
    return f

NUMH = 86
for i,key in enumerate(C.VARIANTS):
    v = C.VARIANTS[key]; m = C.metrics(key)
    c, d = v['c'], v['d']
    ox = PX0 + i*(CELLW+GAP); oy = PY0
    cl = f'pc{i}'
    P = mk(ox,oy)

    rect(ox-14,oy-60,CELLW,PLAN+60+NUMH+14,PANEL,RULE,1,rx=6)
    text(ox,oy-34,f"{key}  {v['name']}",22,TEXT,'bold')
    for j,l in enumerate(wrap(v['blurb'],64)):
        text(ox,oy-12+j*17,l,13,MUTED)

    # solid ground, then the walkable region cut out of it
    rect(ox,oy,PLAN,PLAN,DEEP,'none',clip=cl)
    poly([P(x,z) for x,z in C.walk_polygon(C.WIDE,c,d,arm=16.0)],'#22323f','none',0,clip=cl)
    poly([P(x,z) for x,z in C.walk_polygon(C.PLATE,c,d,arm=16.0)],'none',PLATEC,1.3,dash='5 4',clip=cl)
    poly([P(x,z) for x,z in C.walk_polygon(C.LANE,c,d,arm=16.0)],'none',CLEAR,1.5,dash='7 5',clip=cl)
    poly([P(x,z) for x,z in C.outer_chain(C.WIDE,c,arm=16.0)],'none',WALLC,2.6,close=False,clip=cl)
    poly([P(x,z) for x,z in C.inner_chain(C.WIDE,d,arm=16.0)],'none',WALLC,2.6,close=False,clip=cl)

    # ribs on the straights
    for step in range(1,4):
        xs = -C.WIDE - step*C.RIB_PITCH
        for side in (-1,1):
            poly([P(xs-C.RIB_DEPTH/2, side*C.WIDE),P(xs+C.RIB_DEPTH/2, side*C.WIDE),
                  P(xs+C.RIB_DEPTH/2, side*C.LANE),P(xs-C.RIB_DEPTH/2, side*C.LANE)],
                 RIBC,'none',0,opacity=0.85,clip=cl)
    for step in range(1,3):
        zs = C.WIDE + step*C.RIB_PITCH
        for side in (-1,1):
            poly([P(side*C.WIDE, zs-C.RIB_DEPTH/2),P(side*C.WIDE, zs+C.RIB_DEPTH/2),
                  P(side*C.LANE, zs+C.RIB_DEPTH/2),P(side*C.LANE, zs-C.RIB_DEPTH/2)],
                 RIBC,'none',0,opacity=0.85,clip=cl)

    # the diagonal clear measurement, drawn on the common perpendicular
    k_out = 2*C.WIDE - c; k_in = -2*C.WIDE - d
    pA = P(k_out/2.0, -k_out/2.0); pB = P(k_in/2.0, -k_in/2.0)
    poly([pA,pB],'none',SIGHT,1.8,close=False,dash='6 4',clip=cl)
    mxp = ((pA[0]+pB[0])/2, (pA[1]+pB[1])/2)
    text(mxp[0]+12,mxp[1]-6,f"{m['diagonal']:.2f} m",16,SIGHT,'bold')
    text(mxp[0]+12,mxp[1]+12,'across the turn',12,MUTED)

    # junction ribs, one at every plan direction change
    for nm,(rx,rz),how in C.rib_stations(c,d):
        px,pz = P(rx,rz); circ(px,pz,9,RIBC,0.95,clip=cl)

    # the elbow toe — what actually crowds the racing line
    ex,ez = m['elbow_toe']; pe = P(ex,ez)
    dot(pe[0],pe[1],6,WARN,BG)
    text(pe[0]-14,pe[1]+6,'elbow toe',12,WARN,'bold',anchor='end')

    po = P(C.WIDE, -C.WIDE)
    text(po[0]-10,po[1]-14,'OUTER',12,MUTED,'bold',anchor='end')
    pi_ = P(-C.WIDE, C.WIDE)
    text(pi_[0]+10,pi_[1]+22,'INNER ELBOW',12,MUTED,'bold')

    # approach and exit arrows
    aP=P(-10.4,0); bP=P(-8.8,0)
    poly([aP,bP],'none',CLEAR,2,close=False,clip=cl)
    poly([(bP[0],bP[1]),(bP[0]-9,bP[1]-6),(bP[0]-9,bP[1]+6)],CLEAR,'none',0,clip=cl)
    aQ=P(0,8.6); bQ=P(0,10.2)
    poly([aQ,bQ],'none',CLEAR,2,close=False,clip=cl)
    poly([(bQ[0],bQ[1]),(bQ[0]-6,bQ[1]-9),(bQ[0]+6,bQ[1]-9)],CLEAR,'none',0,clip=cl)

    # numbers
    ty = oy + PLAN + 12
    rect(ox,ty,PLAN,NUMH-8,DEEP,RULE,1,rx=4)
    text(ox+12,ty+22,f"chamfers   outer {c:.2f} m · elbow {d:.2f} m",14,TEXT)
    text(ox+12,ty+44,f"turn {m['bulge']*100:.0f}% wider than the corridor",14,
         GOOD if m['bulge']<0.30 else WARN)
    text(ox+12,ty+65,f"plan mitres {'/'.join(f'{a:g}' for a in m['mitres'])}°  ·  {m['ribs']} junction ribs",14,
         GOOD if 22.5 not in m['mitres'] else WARN)
    text(ox+268,ty+44,f"racing line {m['racing']:.2f} m",14,TEXT)
    text(ox+268,ty+65,f"sees {m['sight_8']:.1f} m down exit",14,SIGHT)

# ---------------------------------------------------------------- table
TY = PY0 + PLAN + NUMH + 58
hrule(TY-30)
text(60,TY,'WHAT THE THREE ACTUALLY TRADE',24,TEXT,'bold')
text(60,TY+24,'Every number is computed by tools/architecture_lab_corner.py from the section module, not measured off the drawing.',15,MUTED)

cols=[(60,'VARIANT'),(232,'OUTER c'),(352,'ELBOW d'),(474,'TURN WIDTH'),(624,'BULGE'),
      (734,'RACING LINE'),(886,'SEES DOWN EXIT'),(1092,'PLAN MITRES'),(1244,'JUNCTION RIBS'),(1420,'GRID SAFE')]
ry=TY+56
for x,lab in cols: text(x,ry,lab,13,MUTED,'bold')
poly([(60,ry+10),(W-60,ry+10)],stroke=RULE,width=1,close=False)
ry+=34
for key in C.VARIANTS:
    m=C.metrics(key); v=C.VARIANTS[key]
    vals=[f"{key}  {v['name']}",f"{m['c']:.2f} m",f"{m['d']:.2f} m",f"{m['diagonal']:.2f} m",
          f"{m['bulge']*100:.0f}%",f"{m['racing']:.2f} m",f"{m['sight_8']:.1f} m from 8 m back",
          '/'.join(f'{a:g}' for a in m['mitres'])+'°',str(m['ribs']),'yes' if m['on_grid'] else 'NO']
    for (x,_),s in zip(cols,vals):
        col=TEXT
        if s.endswith('%'): col = GOOD if m['bulge']<0.30 else WARN
        if s.startswith('22.5'): col = WARN
        text(x,ry,s,15,col,'bold' if x==60 else 'normal')
    ry+=32

# ---------------------------------------------------------------- findings
FY = ry + 26
hrule(FY-16)
text(60,FY+12,'FOUR THINGS THE GEOMETRY SETTLES',24,TEXT,'bold')

notes=[
 ('The corner does not crowd — it BULGES.',
  f'A hard 90 opens to {C.diagonal_clear(0,0):.2f} m across the diagonal against a {2*C.WIDE:.2f} m corridor — {C.bulge(0,0)*100:.0f}% wider at the turn. '
  'The worry was the inside getting tight; the measurement says the opposite. What crowds the turn is not the wall, it is the RIB standing on the elbow.'),
 ('The elbow chamfer is the opposite — it is ALL play.',
  f'V3 shortens the racing line to {C.metrics("V3")["racing"]:.2f} m and opens the exit view from {C.metrics("V1")["sight_8"]:.1f} m to {C.metrics("V3")["sight_8"]:.1f} m, seen from 8 m back. '
  'It moves better and hides far less. A corner meant to work as a sight blocker should NOT have its elbow chamfered.'),
 ('The outer chamfer is a LOOKS decision, not a PLAY decision.',
  f'V2 changes nothing a player can feel: same racing line ({C.metrics("V2")["racing"]:.2f} m), same sightline ({C.metrics("V2")["sight_8"]:.1f} m). '
  f'It shrinks the bulge from {C.bulge(0,0)*100:.0f}% to {C.bulge(1.5,0)*100:.0f}% and stops the pocket reading as a dead square. Judge it by eye, not by stopwatch.'),
 ('A rib at every bend removes the 22.5° mitre problem.',
  'A 45° plan chamfer meeting an orthogonal wall needs a 22.5° mitre, and 22.5° will not land on the 0.125 m grid. Put a rib at each end of every chamfer instead: '
  'the straight wall dies into one rib face and the chamfer into the next, and the rib stands 0.50 m proud so the joint is never seen.'),
]
ny=FY+44
for i,(head,body) in enumerate(notes):
    bx = 60 + (i%2)*810
    by = ny + (i//2)*104
    rect(bx-12,by-24,786,92,PANEL,RULE,1,rx=5)
    text(bx,by-2,head,17,TEXT,'bold')
    for j,l in enumerate(wrap(body,100)[:3]): text(bx,by+22+j*20,l,14,MUTED)

# ------------------------------------------------- how long must the leg be
LY = ny + 232
hrule(LY-32)
text(60,LY,'HOW LONG MUST THE 45° LEG BE?  — a rib at each end only works if there is room for them',24,TEXT,'bold')
for j,l in enumerate(wrap(
    'Raised by the user, and it holds. Too short and the two ribs collide; a little longer and they clear but read as crowded '
    f'against the {C.CLEAR_BAY:.2f} m bay used everywhere else. Both thresholds fall straight out of the rib depth and pitch.',152)):
    text(60,LY+24+j*21,l,15,MUTED)

# the chamfer ladder
gx0, gy0 = 60, LY+82
GW, GH = 940, 206
rect(gx0,gy0,GW,GH,PANEL,RULE,1,rx=5)
cmax_draw = 3.2
def cx(c): return gx0 + 118 + (c/cmax_draw)*(GW-172)
bar_y = gy0+52
text(gx0+14,gy0+24,'chamfer size c  →  clear run left between the two ribs',15,TEXT,'bold')
# zones
for lo,hi,col,lab in ((0.0,C.C_COLLIDE,WARN,'RIBS COLLIDE'),
                      (C.C_COLLIDE,C.C_FULL_BAY,'#c8913f','CLEAR, BUT CROWDED'),
                      (C.C_FULL_BAY,cmax_draw,GOOD,'FULL BAY')):
    rect(cx(lo),bar_y,cx(hi)-cx(lo),34,col,'none',opacity=0.30)
    if cx(hi)-cx(lo) > 70:
        text((cx(lo)+cx(hi))/2,bar_y+22,lab,12,col,'bold',anchor='middle')
# the lane cap, which is the whole point
poly([(cx(C.C_MAX),bar_y-16),(cx(C.C_MAX),bar_y+52)],'none',SIGHT,2.2,close=False)
text(cx(C.C_MAX),bar_y-22,f'LANE CAP {C.C_MAX:.2f} m',13,SIGHT,'bold',anchor='middle')
poly([(cx(C.C_FULL_BAY),bar_y-16),(cx(C.C_FULL_BAY),bar_y+52)],'none',GOOD,2,close=False,dash='5 4')
text(cx(C.C_FULL_BAY),bar_y+70,f'full bay needs {C.C_FULL_BAY:.2f} m',13,GOOD,'bold',anchor='middle')
for c in (0.0,1.0,2.0,3.0):
    text(cx(c),bar_y+50,f'{c:.0f}',12,MUTED,anchor='middle')

ry_ = gy0+124
text(gx0+14,ry_,'c',13,MUTED,'bold'); text(gx0+74,ry_,'45° face',13,MUTED,'bold')
text(gx0+184,ry_,'clear bay',13,MUTED,'bold'); text(gx0+304,ry_,'of normal',13,MUTED,'bold')
ry_+=22
for c in (1.0,1.5,C.C_MAX):
    bay = C.chamfer_bay(c); pct = bay/C.CLEAR_BAY*100
    col = WARN if pct < 90 else GOOD
    text(gx0+14,ry_,f'{c:.2f} m',13,TEXT)
    text(gx0+74,ry_,f'{C.chamfer_face(c):.2f} m',13,TEXT)
    text(gx0+184,ry_,f'{bay:.2f} m',13,TEXT)
    text(gx0+304,ry_,f'{pct:.0f}%',13,col,'bold')
    if abs(c-C.C_MAX)<1e-9: text(gx0+374,ry_,'← the most chamfer the lane allows, and still a third short',13,SIGHT)
    ry_+=20

# the verdict box
vx = gx0+GW+26
rect(vx,gy0,W-60-vx,GH,PANEL,RULE,1,rx=5)
text(vx+16,gy0+26,'A plain chamfer can never hold a full bay.',17,WARN,'bold')
for j,l in enumerate(wrap(
    f'A full {C.CLEAR_BAY:.2f} m bay needs c = {C.C_FULL_BAY:.2f} m, but the lane caps c at {C.C_MAX:.2f} m. '
    f'The best legal chamfer is {C.chamfer_bay(C.C_MAX)/C.CLEAR_BAY*100:.0f}% of a normal bay. The prediction was right — so stop chamfering the corner '
    'and make the 45° run a piece of corridor in its own right: straight, slice, a full bay at 45°, slice, straight.',78)):
    text(vx+16,gy0+54+j*20,l,14,MUTED)
for j,l in enumerate(wrap(
    f'Cost: the junction grows. The two walls bend {C.LEG_OFFSET_EXACT:.3f} m apart — and that is irrational, '
    f'so a true 45° turn cannot be fully on-grid. Snapping to {C.LEG_OFFSET:.3f} m costs {abs(C.LEG_WIDTH-2*C.WIDE)*100:.1f} cm of width, which is invisible.',76)):
    text(vx+16,gy0+150+j*20,l,13,SIGHT)

# ---------------------------------------------------------------- repetition test
RY = LY + 352
hrule(RY-32)
text(60,RY,'THE REPETITION TEST — how long may a straight run be?',24,TEXT,'bold')
for j,l in enumerate(wrap(
    f'A separate question from the corner, and the answer has to be a NUMBER, because it becomes a rule: beyond this length, something must interrupt. '
    f'The built lab run is 24.5 m — six bays — and has never felt long. This lays out {C.REPEAT_RUN:.0f} m of the same kit with nothing in it.',150)):
    text(60,RY+24+j*22,l,15,MUTED)

rx0, ry0 = 60, RY+80
RSC = (W-200)/C.REPEAT_RUN
rect(rx0,ry0,C.REPEAT_RUN*RSC,60,DEEP,RULE,1)
nbays = int(C.REPEAT_RUN/C.RIB_PITCH)
for b in range(nbays+1):
    rect(rx0+b*C.RIB_PITCH*RSC-3,ry0,6,60,RIBC,'none',opacity=0.85)
for mk_ in C.REPEAT_MARKS:
    x = rx0 + mk_*RSC
    poly([(x,ry0-8),(x,ry0+68)],'none',SIGHT,1.3,close=False,dash='4 4')
    text(x,ry0+84,f'{mk_:.0f} m',13,SIGHT,anchor='middle')
text(rx0+4,ry0-14,f'{nbays} bays at {C.RIB_PITCH:.0f} m — identical panels, alternating lit/off, no interruption of any kind',14,MUTED)
text(rx0,ry0+114,'Walk it in both directions and mark the bay where the rhythm stops giving you new information. That bay number × 4 m is the rule.',15,TEXT)
text(rx0,ry0+136,'Run it once with the lighting alternation ON and once with every bay lit — a repeating light pattern may be doing more of the work than the geometry.',15,MUTED)

text(rx0,ry0+176,'WHAT MAY INTERRUPT A RUN, most expensive first:',16,TEXT,'bold')
ix = rx0
for nm,desc in C.INTERRUPTS:
    text(ix,ry0+204,nm,15,RIBC,'bold')
    for j,l in enumerate(wrap(desc,30)[:2]): text(ix,ry0+226+j*18,l,13,MUTED)
    ix += 256

text(60,H-34,f'CORNER STUDY / PAPER ONLY — generated from tools/architecture_lab_corner.py, which imports the revision 06 section · '
             f'outer chamfer capped at {C.C_MAX:.2f} m before it cuts the lane corner · nothing here is built',15,MUTED)

parts.append('</svg>')
svg = root/'docs/architecture-lab-corner.svg'
svg.write_text('\n'.join(parts), encoding='utf-8')

ink = shutil.which('inkscape') or r'C:\Program Files\Inkscape\bin\inkscape.exe'
if Path(ink).exists():
    subprocess.run([ink, str(svg), '--export-type=png', '--export-filename',
                    str(root/'docs/architecture-lab-corner.png'), '--export-width', str(W)],
                   check=True, capture_output=True)
    print('wrote svg + png')
else:
    print('wrote svg; Inkscape not found, export the PNG manually')
