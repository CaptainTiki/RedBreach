"""One-time application of approved furnishing F-01 to revision 05.
Never called by a normal rebuild. Refuses later source edits, including TB edits.
"""
from pathlib import Path
import ast, hashlib, json, math, re, shutil, sys
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'RedBreach'; MAP=P/'maps/freight_01.map'
BASE='22697d1c29e5be5e29ab7cc2f6cc0cde54dd1e6fc8e9396367835f9da530a841'
SNAP=P/'.godot/freight_before_f01'; STATE=P/'.godot/freight_f01_apply.json'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if digest(MAP)!=BASE:
    if '--revise-generated' not in sys.argv or not STATE.exists() or digest(MAP)!=json.loads(STATE.read_text())['output_sha256']:
        raise SystemExit('Source changed: refusing to overwrite later map edits.')
if not SNAP.exists():
    SNAP.mkdir()
    for src,name in [(MAP,'freight_01.map'),(P/'missions/freight/layout.json','layout.json'),(P/'missions/freight/freight_blockout.tscn','scene.tscn'),(ROOT/'docs/freight-blockout-layout.json','base.json')]:shutil.copy2(src,SNAP/name)
assert digest(SNAP/'freight_01.map')==BASE
plan=json.loads((ROOT/'docs/freight-furnishing-plan.json').read_text()); rooms=plan['rooms']
brushes=[]; boxes=[]
ns={'brushes':brushes,'boxes':boxes}
source=ast.parse((ROOT/'tools/bootstrap-freight-blockout.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ('sub','cross','dot','box','merge_grid')],type_ignores=[]),'<box primitives>','exec'),ns)
box,merge=ns['box'],ns['merge_grid']
D='greybox/Dark/texture_06'; W='greybox/Dark/texture_01'; O='greybox/Orange/texture_01'
cuts=[([s['bounds'][0],-100,s['bounds'][1]],[s['bounds'][2],100,s['bounds'][3]]) for s in rooms.values()]
cuts.append(([102,1,294],[110,2.8,294.6]))
def parse(raw):
    pts=[tuple(map(float,p.split())) for p in re.findall(r'\( ([^()]*) \)',raw)]
    lo=[min(p[1] for p in pts)/32+190,min(p[2] for p in pts)/32,min(p[0] for p in pts)/32+260]
    hi=[max(p[1] for p in pts)/32+190,max(p[2] for p in pts)/32,max(p[0] for p in pts)/32+260]
    return lo,hi,re.search(r'\) (greybox/\S+) ',raw).group(1),raw.splitlines()[0][3:]
def subtract(lo,hi,cut):
    l=[max(lo[i],cut[0][i]) for i in range(3)];h=[min(hi[i],cut[1][i]) for i in range(3)]
    if any(l[i]>=h[i]-1e-6 for i in range(3)):return [(lo,hi)]
    a=list(lo);b=list(hi);out=[]
    for i in range(3):
        if a[i]<l[i]:c=b.copy();c[i]=l[i];out.append((a.copy(),c));a[i]=l[i]
        if h[i]<b[i]:c=a.copy();c[i]=h[i];out.append((c,b.copy()));b[i]=h[i]
    return out
old=(SNAP/'freight_01.map').read_text();raws=re.findall(r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}',old)
assert len(raws)==896
for raw in raws:
    lo,hi,tex,name=parse(raw);parts=[(lo,hi)]
    for cut in cuts:parts=[p for l,h in parts for p in subtract(l,h,cut)]
    if parts==[(lo,hi)]:brushes.append(raw)
    else:
        for l,h in parts:box(l,h,tex,name+' / outside F01')
preserved=len(brushes)
floors={};roofs={}
def paint(dst,bounds,y):
    a,b,c,d=bounds
    for ix in range(round(a*2),round(c*2)):
        for iz in range(round(b*2),round(d*2)):dst[ix,iz]=y
for k,s in rooms.items():
    paint(floors,s['bounds'],s['floor'])
    paint(roofs,s['bounds'],s['floor']+3.5)
    for _,name,b,h,_ in s['rooms']:
        # Partition centrelines fall on the half-metre ceiling grid.
        paint(roofs,[round(v*2)/2 for v in b],s['floor']+h)
    for override in s.get('ceiling_overrides',[]):paint(roofs,override['bounds'],override['ceiling_y'])
paint(floors,[38,232,56,242],0);paint(floors,[52,230,56,232],0)
for i in range(8):paint(floors,[52,229.5-i*.5,56,230-i*.5],-(i+1)*.25)
for i,(a,b,c,d,y) in enumerate(merge(floors)):box((a,-4,b),(c,y,d),D,f'F01 floor {i}')
for i,(a,b,c,d,y) in enumerate(merge(roofs)):box((a,y,b),(c,y+.25,d),W,f'F01 ceiling {i}')
def roof(x,z):return roofs.get((math.floor(x*2),math.floor(z*2)))
# Seal all roof-height transitions, including shell thresholds to old corridors.
# Group roof boundary half-metre segments into long bulkheads.
edges={}
for (ix,iz),y in roofs.items():
    for dx,dz,axis,line,start in [(-1,0,'x',ix/2,iz/2),(1,0,'x',(ix+1)/2,iz/2),(0,-1,'z',iz/2,ix/2),(0,1,'z',(iz+1)/2,ix/2)]:
        ny=roofs.get((ix+dx,iz+dz))
        if ny is None:edges.setdefault((axis,line,y,8,dx or dz),[]).append(start)
        elif dx+dz==1 and ny!=y:edges.setdefault((axis,line,min(y,ny),max(y,ny),0),[]).append(start)
for (axis,line,low,high,sign),values in edges.items():
    vals=sorted(values);a=prev=vals[0]
    for v in vals[1:]+[None]:
        if v is not None and abs(v-prev-.5)<.001:prev=v;continue
        # Boundary seal stays inside the approved footprint.
        l=line-.125 if sign>=0 else line;h=line if sign>0 else line+.125
        if axis=='x':box((l,low,a),(h,high+.25,prev+.5),W,'F01 ceiling bulkhead')
        else:box((a,low,l),(prev+.5,high+.25,h),W,'F01 ceiling bulkhead')
        if v is not None:a=prev=v
for k,s in rooms.items():
    y=s['floor']
    for a,b in s['walls']:
        x,z=min(a[0],b[0]),min(a[1],b[1]);X,Z=max(a[0],b[0]),max(a[1],b[1])
        top=max(roofs[ix,iz] for ix,iz in roofs if x-.6<ix/2<X+.6 and z-.6<iz/2<Z+.6)
        if x==X:x-=.125;X+=.125
        else:z-=.125;Z+=.125
        box((x,y,z),(X,top,Z),W,k+' F01 partition')
    for name,(x,z),axis in s['doors']:
        top=max(roof(x-.3,z-.3) or 0,roof(x+.3,z+.3) or 0)
        lo=(x-.125,y+3.2,z-2) if axis=='x' else (x-2,y+3.2,z-.125)
        hi=(x+.125,top,z+2) if axis=='x' else (x+2,top,z+.125)
        if top>y+3.2:box(lo,hi,W,k+' F01 header '+name)
        # Flush frame strips occupy wall, leaving all four metres clear.
        for sign in [-1,1]:
            if axis=='x':box((x-.16,y,z+sign*2.125-.125),(x+.16,y+3.2,z+sign*2.125+.125),D,k+' F01 frame')
            else:box((x+sign*2.125-.125,y,z-.16),(x+sign*2.125+.125,y+3.2,z+.16),D,k+' F01 frame')
    for i,p in enumerate(s['props']):
        kind=p['kind'];a,b,c,d=p['bounds'];h=p['height_m'];name=f'{k} F01 {kind} {i}'
        if kind in ('chair','selector','cache'):continue
        def piece(x,z,X,Z,low,high,tex=D):box((x,y+low,z),(X,y+high,Z),tex,name)
        if kind in ('desk','bench','counter','console'):
            piece(a,b,c,d,h-.12,h)
            # Two substantial pedestals, kept within the reserved footprint.
            if c-a>d-b:
                piece(a+.08,b+.06,a+.38,d-.06,0,h-.12);piece(c-.38,b+.06,c-.08,d-.06,0,h-.12)
            else:
                piece(a+.06,b+.08,c-.06,b+.38,0,h-.12);piece(a+.06,d-.38,c-.06,d-.08,0,h-.12)
            if kind in ('counter','console'):piece(a+.1,b+.1,c-.1,b+.22,.15,h-.12)
        elif kind in ('locker','cabinet'):
            piece(a,b,c,d,0,h,W)
            n=max(1,round(max(c-a,d-b)/.8))
            for j in range(n):
                if c-a>d-b:
                    xx=a+(j+.5)*(c-a)/n;piece(xx-.035,d,xx+.035,d+.015,h*.45,h*.65)
                else:
                    zz=b+(j+.5)*(d-b)/n;piece(c,zz-.035,c+.015,zz+.035,h*.45,h*.65)
        elif kind=='rack':
            for yy in [0,.75,1.5,h-.1]:piece(a,b,c,d,yy,yy+.1)
            for xx in [a,c-.12]:
                for zz in [b,d-.12]:piece(xx,zz,xx+.12,zz+.12,0,h)
        elif kind in ('pump','machine'):
            piece(a,b,c,d,0,.25)
            piece(a+.3,b+.35,c-.3,d-.35,.25,h-.25)
            piece(a+.55,b+.1,c-.55,b+.35,.45,h-.55,W)
            piece(a+.45,b+.45,c-.45,d-.45,h-.25,h)
        elif kind=='pipe':
            # Service header and vertical risers in the same approved envelope.
            piece(a,b,c,d,h-.4,h)
            for zz in [b,b+(d-b)/2,d-.4]:piece(a+.35,zz,c-.35,zz+.4,0,h-.4)
        elif kind=='scanner':
            piece(a,b,c,d,0,.3);piece(a,b,a+.3,d,.3,h);piece(c-.3,b,c,d,.3,h);piece(a+.3,b,c-.3,d,h-.35,h)
            piece(a+.3,b+.25,c-.3,d-.25,.7,.85)
        else:
            piece(a,b,c,d,0,h)
# Open guards: slim continuous bars + posts retain collision and reveal the floor.
def guard(a,b,ya,yb,label):
    length=math.dist(a,b);n=math.ceil(length/1.75)
    for i in range(n+1):
        t=i/n;x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t;y=ya+(yb-ya)*t
        box((x-.045,y,z-.045),(x+.045,y+1.15,z+.045),D,label+' post')
    # Stepped short horizontal bars for the stair guard, flat long rails elsewhere.
    segs=8 if ya!=yb else 1
    for i in range(segs):
        t=i/segs;u=(i+1)/segs;y=ya+(yb-ya)*(t+u)/2
        x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t;X=a[0]+(b[0]-a[0])*u;Z=a[1]+(b[1]-a[1])*u
        for off in [.55,1.1]:box((min(x,X)-.035,y+off,min(z,Z)-.035),(max(x,X)+.035,y+off+.06,max(z,Z)+.035),D,label+' rail')
guard((38,231.94),(51.94,231.94),0,0,'F01 deck north')
guard((37.94,232),(37.94,241.94),0,0,'F01 deck west')
guard((51.94,230),(51.94,232),0,0,'F01 upper landing')
guard((51.94,226),(51.94,230),-2,0,'F01 stair guard')
MAP.write_text(old[:old.index('// floor')]+'\n'.join(brushes)+'\n}\n',encoding='utf-8')
layout=json.loads((SNAP/'layout.json').read_text())
def in_sample(x,z):return any(s['bounds'][0]<=x<=s['bounds'][2] and s['bounds'][1]<=z<=s['bounds'][3] for s in rooms.values())
def replace_path(points,k):
    s=rooms[k];a=points.index(s['entry']);b=points.index(s['exit'],a+1)
    return points[:a]+s['route']+points[b+1:]
for key in ('walk_points','a_walk_points'):
    for k in ('A1','A2'):layout[key]=replace_path(layout[key],k)
layout['interior_paths']['A']=layout['a_walk_points'];layout['interior_paths']['Annex']=[[85,164]]+rooms['A8']['route']
for st in layout['stairs']:
    if st[0]=='I1':st[3:]=[[54,230],[54,226],0,-2]
layout['samples']=[p for p in layout['samples'] if not in_sample(p[0]+190,p[2]+260)]
for k,s in rooms.items():
    for route in [s['route']]+s['optional']:
        for a,b in zip(route,route[1:]):
            n=math.dist(a,b)
            for j in range(math.ceil(n)):
                t=min((j+.5)/n,1);x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t
                y=floors.get((math.floor(x*2),math.floor(z*2)),s['floor'])
                layout['samples'].append([x-190,y,z-260])
layout['clearance_points'].update(A1=[104,0,272],A2=[20,-2,204],A8=[85,-2,196])
layout.update(revision='06',furnishing_revision='F-01',brushes=len(brushes),furnishing=plan)
(P/'missions/freight/layout.json').write_text(json.dumps(layout,indent=2)+'\n')
built=json.loads((SNAP/'base.json').read_text());built.update(revision='06',blockout_revision='06',status='BUILT - approved F-01 sample',furnishing=plan,walk_points=layout['walk_points'],stair_flights=layout['stairs'],brushes=len(brushes))
built['mezzanines']=[m for m in built['mezzanines'] if m['room']!='A2']+[{'room':'A2','bounds':[38,232,56,242],'floor':0,'type':'solid plinth'}]
(ROOT/'docs/freight-blockout-layout.json').write_text(json.dumps(built,indent=2)+'\n')
report={'source_sha256':BASE,'output_sha256':digest(MAP),'preserved_fragments':preserved,'brushes':len(brushes),'revision':'06','cut_volumes':cuts}
STATE.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
