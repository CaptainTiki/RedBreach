"""One-time, source-hash-guarded application of the reviewed A-01 paper plan.

Normal rebuilds read the .map and never run this file. --revise-generated is only
for revising this application before any subsequent TrenchBroom source edits.
"""
from pathlib import Path
import ast, hashlib, json, math, re, shutil, sys

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'RedBreach'
MAP = P / 'maps/freight_01.map'
SNAP = P / '.godot/freight_before_a01'
BASE_HASH = '5a8e01f843a2b90758a6c006f6eb3590dbeee15254df5e1b52966c4dc68b9198'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
state = P / '.godot/freight_a01_apply.json'
if digest(MAP) != BASE_HASH:
    if '--revise-generated' not in sys.argv or not state.exists() or digest(MAP) != json.loads(state.read_text())['output_sha256']:
        raise SystemExit('Source changed. Refusing to replace TrenchBroom edits. Normal rebuilds never run this helper.')
if not SNAP.exists():
    SNAP.mkdir()
    for src, name in [(MAP, 'freight_01.map'), (ROOT/'docs/freight-blockout-layout.json', 'base.json'),
                      (P/'missions/freight/layout.json', 'layout.json'), (P/'missions/freight/freight_blockout.tscn', 'scene.tscn')]:
        shutil.copy2(src, SNAP/name)
assert digest(SNAP/'freight_01.map') == BASE_HASH
base = json.loads((SNAP/'base.json').read_text(encoding='utf-8'))
old_layout = json.loads((SNAP/'layout.json').read_text(encoding='utf-8'))
plan = json.loads((ROOT/'docs/freight-a-interior-plan.json').read_text(encoding='utf-8'))
bootstrap = (ROOT/'tools/bootstrap-freight-blockout.py').read_text(encoding='utf-8')
prefix = bootstrap.split('brushes=[];boxes=[]')[0]
prefix = '\n'.join(line for line in prefix.splitlines() if not line.startswith('if MAP.exists()'))
prefix = prefix.replace("ROOT/'docs/freight-blockout-layout.json'", "ROOT/'RedBreach/.godot/freight_before_a01/base.json'")
ns = {'__file__': str(ROOT/'tools/bootstrap-freight-blockout.py')}
exec(prefix, ns)
cells, ceilings = dict(ns['cells']), dict(ns['ceilings'])
brushes, boxes = [], []
ns.update(brushes=brushes, boxes=boxes)
defs = [node for node in ast.parse(bootstrap).body if isinstance(node, ast.FunctionDef) and node.name in ('sub','cross','dot','box','merge_grid')]
exec(compile(ast.Module(body=defs, type_ignores=[]), '<brush primitives>', 'exec'), ns)
box, merge_grid = ns['box'], ns['merge_grid']
dark, wall, orange = 'greybox/Dark/texture_06', 'greybox/Dark/texture_01', 'greybox/Orange/texture_01'
# Two disjoint authoring regions cover A and its moved Clearance connector.
# All original brush volume outside these regions is retained.
cuts = [(-100, 0, 164, 300), (164, 170, 180, 200)]
def inside(x,z): return any(a <= x < c and b <= z < d for a,b,c,d in cuts)
for key in list(cells):
    if inside((key[0]+.5)/2, (key[1]+.5)/2):
        del cells[key]; del ceilings[key]
heights = dict(old_layout['heights']); heights['A7'] = 4
room_bounds = {}
for k, (x,z,w,h,*_) in base['rooms'].items(): room_bounds[k] = (x-w/2,z-h/2,x+w/2,z+h/2)
def in_room(x,z): return any(a<=x<c and b<=z<d for a,b,c,d in room_bounds.values())
def paint(x0,z0,x1,z1,y,ceiling):
    for ix in range(round(x0*2), round(x1*2)):
        for iz in range(round(z0*2), round(z1*2)):
            cells[ix,iz] = y; ceilings[ix,iz] = ceiling
for k in [f'A{i}' for i in range(1,9)]:
    paint(*room_bounds[k], heights[k], plan['ceilings'].get(k, heights[k]+8))
# The ordinary corridors end at the room walls. Upper openings do not overwrite
# lower floors inside a room; their adjoining floor brushes seal the wall below.
link_y = {'H-A1':0,'A1-A2':0,'A2-J0':-2,'blocked-D1':-2,'bypass':-2,'annex':-2,'JA-A3':0,'JA-A4':0,'A3-A7':4,'A4-A5':2,'A5-A6':6,'A6-H':0}
link_stairs = {'blocked-D1': plan['stairs'][8], 'bypass':plan['stairs'][9], 'JA-A4':plan['stairs'][10]}
def chain(pt, points):
    d=0
    for a,b in zip(points, points[1:]):
        if min(a[0],b[0])<=pt[0]<=max(a[0],b[0]) and min(a[1],b[1])<=pt[1]<=max(a[1],b[1]): return d+abs(pt[0]-a[0])+abs(pt[1]-a[1])
        d += abs(b[0]-a[0])+abs(b[1]-a[1])
    raise ValueError(pt)
def hall_level(name, d):
    y = link_y[name]
    if name in link_stairs:
        _,_,a,b,ya,yb = link_stairs[name]
        st,en = chain(a,plan['links'][name]),chain(b,plan['links'][name])
        if d>=en: return yb
        if d>=st: return ya + math.copysign(.25*min(8,math.floor((d-st)/.5)+1),yb-ya)
    return y
for name,y in link_y.items():
    pts=plan['links'][name]; dist=0
    high=max(y, link_stairs.get(name,[0,0,0,0,y,y])[-1]); top=high+4.5
    for a,b in zip(pts,pts[1:]):
        n=abs(b[0]-a[0])+abs(b[1]-a[1]); dx=(b[0]-a[0])/n; dz=(b[1]-a[1])/n
        for ix in range(round((min(a[0],b[0])-3)*2),round((max(a[0],b[0])+3)*2)):
            for iz in range(round((min(a[1],b[1])-3)*2),round((max(a[1],b[1])+3)*2)):
                x,z=(ix+.5)/2,(iz+.5)/2
                if not inside(x,z) or in_room(x,z): continue
                t=max(0,min(n,(x-a[0])*dx+(z-a[1])*dz))
                cells[ix,iz]=hall_level(name,dist+t);ceilings[ix,iz]=top
        dist+=n
paint(154,60,164,64,6,10)
# Inspection has a solid raised entry. Other upstairs routes are real slabs.
paint(38,228,50,242,0,6)
# Ordinary room stairs are built as raised cells with a landing at each end.
# Keep their deck surface separate from the lower-floor cells for usable space below.
stair_cells={}
for name,room,a,b,ya,yb in plan['stairs'][:8]:
    dx=(b[0]-a[0])/4;dz=(b[1]-a[1])/4
    for i in range(-4,12):
        y=ya if i<0 else yb if i>=8 else ya+math.copysign((i+1)*.25,yb-ya)
        cx=a[0]+dx*(i+.5)*.5;cz=a[1]+dz*(i+.5)*.5
        x0,x1=(cx-.25,cx+.25) if dx else (cx-2,cx+2)
        z0,z1=(cz-.25,cz+.25) if dz else (cz-2,cz+2)
        for ix in range(round(x0*2),round(x1*2)):
            for iz in range(round(z0*2),round(z1*2)):
                # Overlapping flat end landings agree by construction.
                stair_cells[ix,iz]=(y,heights[room],name)
                if room=='A2': cells[ix,iz]=y
for i,(x0,z0,x1,z1,y) in enumerate(merge_grid(cells)):
    box((x0,-4,z0),(x1,y,z1),dark,f'floor {i} / Y {y:g}')
for i,(x0,z0,x1,z1,y) in enumerate(merge_grid(ceilings)):
    box((x0,y,z0),(x1,y+.25,z1),wall,f'ceiling {i}')
def runs(values):
    vals=sorted(set(values));lo=prev=vals[0]
    for v in vals[1:]+[None]:
        if v is not None and abs(v-prev-.5)<.001:prev=v;continue
        yield lo,prev+.5
        if v is not None:lo=prev=v
segments={}; ceiling_edges={}
for (ix,iz),floor in cells.items():
    for dx,dz,axis,line,start in [(-1,0,'x',ix/2,iz/2),(1,0,'x',(ix+1)/2,iz/2),(0,-1,'z',iz/2,ix/2),(0,1,'z',(iz+1)/2,ix/2)]:
        if (ix+dx,iz+dz) not in cells:segments.setdefault((axis,line,dx or dz,ceilings[ix,iz]),[]).append(start)
        elif dx+dz==1 and ceilings[ix,iz]!=ceilings[ix+dx,iz+dz]:
            yy,oy=ceilings[ix,iz],ceilings[ix+dx,iz+dz]
            ceiling_edges.setdefault((axis,line,min(yy,oy),max(yy,oy)),[]).append(start)
for (axis,line,sign,top),values in segments.items():
    for a,b in runs(values):
        lo,hi=(line-.5,line) if sign<0 else (line,line+.5)
        if axis=='x':box((lo,-4,a),(hi,top+.25,b),wall,'wall')
        else:box((a,-4,lo),(b,top+.25,hi),wall,'wall')
for (axis,line,bottom,top),values in ceiling_edges.items():
    for a,b in runs(values):
        if axis=='x':box((line-.125,bottom,a),(line+.125,top+.25,b),wall,'ceiling bulkhead')
        else:box((a,bottom,line-.125),(b,top+.25,line+.125),wall,'ceiling bulkhead')
for room,decks in plan['decks'].items():
    if room=='A2':continue
    for x0,z0,x1,z1,y in decks:box((x0,y-.4,z0),(x1,y,z1),dark,room+' upper slab')
for x0,z0,x1,z1,(y,base_y,name) in merge_grid(stair_cells):
    if y>base_y and not name.startswith('I1'):box((x0,base_y,z0),(x1,y,z1),orange,name+' stair / landing')
for room,parts in plan['partitions'].items():
    main=room.split('-')[0];bottom=heights[main];top=plan['ceilings'].get(main,bottom+8)
    if room=='A5-up':bottom=6
    if room=='A3-low':top=3.6
    for a,b in parts:
        box((min(a[0],b[0])-.125,bottom,min(a[1],b[1])-.125),(max(a[0],b[0])+.125,top,max(a[1],b[1])+.125),wall,room+' partition')
# Guards on exposed deck edges; openings match the stair heads and portals.
guards=[
    (38,228,42,228,0),(46,228,50,228,0),(38,228,38,242,0),(50,228,50,242,0),
    (20,120,56,120,4),(60,120,74,120,4),(74,120,74,140,4),(74,140,84,140,4),
    (128,130,143,130,6),(147,130,150,130,6),(150,130,150,144,6),
    (110,180,130,180,6),(130,166,130,174,6),(130,178,130,180,6)]
for x,z,X,Z,y in guards:box((min(x,X)-.1,y,min(z,Z)-.1),(max(x,X)+.1,y+1.2,max(z,Z)+.1),wall,'A gallery guard')
# Stepped stair guards follow the treads, including the intermediate landings.
for name,room,a,b,ya,yb in plan['stairs'][:8]:
    dx=(b[0]-a[0])/4;dz=(b[1]-a[1])/4
    # End rails at the terminal tread so landing turns stay clear.
    for i in range(1 if name=='G1a' else 0,8 if name in ('R1b','G1b','O1c') else 12):
        y=yb if i>=8 else ya+math.copysign((i+1)*.25,yb-ya)
        if room=='A2' and y<=-2:continue
        cx=a[0]+dx*(i+.5)*.5;cz=a[1]+dz*(i+.5)*.5
        for sign in [-1,1]:
            x=cx+dz*sign*2.1;z=cz-dx*sign*2.1
            box((x-(.25 if dx else .1),y,z-(.25 if dz else .1)),(x+(.25 if dx else .1),y+1.2,z+(.25 if dz else .1)),wall,name+' stair guard')
# Retain the existing ladder geometry and A-side gate frames exactly.
oldtext=(SNAP/'freight_01.map').read_text(encoding='utf-8')
oldbrushes=re.findall(r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}',oldtext)
assert len(oldbrushes)==605,len(oldbrushes)
def parse(raw):
    points=[tuple(map(float,p.split())) for p in re.findall(r'\( ([^()]*) \)',raw)]
    lo=[min(p[1] for p in points)/32+190,min(p[2] for p in points)/32,min(p[0] for p in points)/32+260]
    hi=[max(p[1] for p in points)/32+190,max(p[2] for p in points)/32,max(p[0] for p in points)/32+260]
    tex=re.search(r'\) (greybox/\S+) ',raw).group(1)
    return lo,hi,tex,raw.splitlines()[0][3:]
def intersect(lo,hi,cut):
    a,b,c,d=cut
    l=[max(lo[0],a),lo[1],max(lo[2],b)];h=[min(hi[0],c),hi[1],min(hi[2],d)]
    return (l,h) if all(l[i]<h[i]-1e-6 for i in range(3)) else None
def subtract(lo,hi,cut):
    inter=intersect(lo,hi,cut)
    if inter is None:return [(lo,hi)]
    l,h=inter;out=[]
    if lo[0]<l[0]:out.append((lo[:],[l[0],hi[1],hi[2]]))
    if h[0]<hi[0]:out.append(([h[0],lo[1],lo[2]],hi[:]))
    if lo[2]<l[2]:out.append(([l[0],lo[1],lo[2]],[h[0],hi[1],l[2]]))
    if h[2]<hi[2]:out.append(([l[0],lo[1],h[2]],[h[0],hi[1],hi[2]]))
    return out
for raw in oldbrushes:
    lo,hi,tex,name=parse(raw)
    if name in ['Ladder landing','mezzanine guard','D1 frame','D2 frame'] and lo[0]<164:
        box(lo,hi,tex,name)
newbrushes=list(brushes);brushes.clear();boxes.clear()
outside_original=[];outside_written=[]
for raw in oldbrushes:
    lo,hi,tex,name=parse(raw);parts=[(lo,hi)]
    for cut in cuts:parts=[sub for l,h in parts for sub in subtract(l,h,cut)]
    outside_original.extend((l,h,tex) for l,h in parts)
    if parts==[(lo,hi)]:
        brushes.append(raw);boxes.append({'lo':[lo[0]-190,lo[1],lo[2]-260],'hi':[hi[0]-190,hi[1],hi[2]-260],'name':name})
    else:
        for l,h in parts:box(l,h,tex,name+' / preserved outside A')
    outside_written.extend((l,h,tex) for l,h in parts)
preserved_count=len(brushes)
for raw in newbrushes:
    lo,hi,tex,name=parse(raw)
    for cut in cuts:
        part=intersect(lo,hi,cut)
        if part:box(*part,tex,name)
assert outside_original==outside_written
MAP.write_text(oldtext[:oldtext.index('// floor')]+ '\n'.join(brushes)+'\n}\n',encoding='utf-8')
# Detailed walk coordinates replace centre-to-centre assumptions inside A rooms.
L,Q=plan['links'],plan['paths']
record_route=L['JA-A3']+Q['A3-low']+[[58,124],[58,122],[58,118]]+Q['A3-up']+L['A3-A7']+Q['A7'][:-1]+[[31,53]]
a_route=L['H-A1']+Q['A1']+L['A1-A2']+Q['A2']+L['A2-J0']+L['bypass']+record_route+list(reversed(record_route))+L['JA-A4']
# Pass the freight pedestal with clear space, then return to the reviewed line.
a_route+=Q['A4'][:3]+[[112,76],[114,76],[114,74]]+Q['A4'][4:]+Q['A4-exit']+L['A4-A5']+[[151,114],[151,119],[145,119],[145,120]]+[[145,124],[145,126],[145,130]]+Q['A5-up']+L['A5-A6']+Q['A6-up']+[[134,176],[136,176],[140,176],[142,176],[146,176]]+Q['A6-low']+L['A6-H']
def dedup(points):return [p for i,p in enumerate(points) if i==0 or p!=points[i-1]]
a_route=dedup(a_route)
routes={ 'A':a_route,'Records branch':dedup(record_route),'Annex':dedup(L['annex']+Q['A8']) }
normal=[[190,328],[190,301]]+a_route
b_route=old_layout['normal_route'][old_layout['normal_route'].index('B1')-1:]
for a,b in zip(b_route,b_route[1:]):
    e=next(e for e in old_layout['edges'] if (e['a'],e['b']) in [(a,b),(b,a)])
    normal+=e['points'] if e['a']==a else list(reversed(e['points']))
layout=dict(old_layout)
layout.update(revision='05',a_interior_revision='A-interiors-01',heights=heights,brushes=len(brushes),walk_points=dedup(normal),a_walk_points=a_route,interior_paths=routes)
layout['stairs']=[s for s in old_layout['stairs'] if not s[0] in ['T1','T2','T3','T4','T5']]+[[n,r,r,a,b,ya,yb] for n,r,a,b,ya,yb in plan['stairs']]
# Samples from protected geometry are unchanged. New path samples use the intended
# floor/slab/stair surface and are checked independently against baked collision.
layout['samples']=[p for p in old_layout['samples'] if not inside(p[0]+190,p[2]+260)]
def sample_y(x,z,upper=False):
    y=cells[math.floor(x*2),math.floor(z*2)]
    if (math.floor(x*2),math.floor(z*2)) in stair_cells:y=stair_cells[math.floor(x*2),math.floor(z*2)][0]
    if upper:
        for room,decks in plan['decks'].items():
            for a,b,c,d,yy in decks:
                if a<=x<c and b<=z<d:y=max(y,yy)
    return y
for name,pts in {**L,**Q}.items():
    if name=='BcD':continue
    for a,b in zip(pts,pts[1:]):
        n=abs(b[0]-a[0])+abs(b[1]-a[1])
        if not n:continue
        for i in range(math.ceil(n)):
            t=min(n,i+.5);x=a[0]+(b[0]-a[0])*t/n;z=a[1]+(b[1]-a[1])*t/n
            if not inside(x,z):continue
            upper=name.endswith('-up') or name in ['A3-A7','A5-A6']
            layout['samples'].append([x-190,sample_y(x,z,upper),z-260])
layout['clearance_points']={k:[r[0],heights[k],r[1]] for k,r in layout['rooms'].items()}
layout['clearance_points'].update({'A2':[20,-2,204],'A3':[54,0,142],'A4':[112,2,84],'A5':[151,2,120],'A6':[148,0,190],'A7':[49,4,69], 'A3 gallery':[35,4,116],'A3 below gallery':[78,0,132], 'A5 upper':[132,6,138],'A5 below gallery':[132,2,138],'A6 upper':[120,6,176],'A6 below gallery':[120,0,176]})
layout['a_portals']=plan['portals']
layout['edges']=[e for e in old_layout['edges'] if not any(k.startswith('A') or k in ('J0','JT','JA') for k in (e['a'],e['b']))]
connections={'H-A1':('H','A1',None),'A1-A2':('A1','A2',None),'A2-J0':('A2','J0',None),'blocked-D1':('J0','A3','1'),'bypass':('J0','JA',None),'annex':('JT','A8',None),'JA-A3':('JA','A3',None),'JA-A4':('JA','A4','2'),'A3-A7':('A3','A7',None),'A4-A5':('A4','A5',None),'A5-A6':('A5','A6',None),'A6-H':('A6','H','S1'),'BcD':('A4','M','BcD')}
for name,(a,b,gate) in connections.items():
    points=plan['links'][name]
    layout['edges'].append({'a':a,'b':b,'points':points,'kind':'optional' if name=='BcD' else 'security','width':4 if name=='BcD' else 6,'gate':gate,'length':sum(abs(v[0]-u[0])+abs(v[1]-u[1]) for u,v in zip(points,points[1:])),'note':'A portal-to-portal corridor; room interiors and landing turns use walk_points'})
bypass_edge=next(e for e in layout['edges'] if e['a']=='J0' and e['b']=='JA')
layout['edges'].remove(bypass_edge)
for a,b,pts in [('J0','JT',bypass_edge['points'][:2]),('JT','JA',bypass_edge['points'][1:])]:
    layout['edges'].append({**bypass_edge,'a':a,'b':b,'points':pts,'length':sum(abs(v[0]-u[0])+abs(v[1]-u[1]) for u,v in zip(pts,pts[1:]))})
(P/'missions/freight/layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf-8')
(P/'.godot/freight_boxes.json').write_text(json.dumps(boxes),encoding='utf-8')
# Retain the baseline explicitly: the original bootstrap no longer describes A.
built=dict(base);built.update(revision='05',floor_heights=heights,stair_flights=layout['stairs'],a_interiors=plan,walk_points=layout['walk_points'],brushes=len(brushes),edges=layout['edges'],normal_route=layout['normal_route'])
built['mezzanines']=[m for m in base['mezzanines'] if not m['room'].startswith('A')]+[{'room':room,'bounds':d[:4],'floor':d[4],'type':'solid plinth' if room=='A2' else 'overhead slab'} for room,decks in plan['decks'].items() for d in decks]
built['blockout_revision']='05'
built['baseline_04_distances']={k:built.pop(k) for k in ('normal_length','security_length','short_length','probe1','probe4') if k in built}
built['status']='BUILT - A-01 interiors; use authoritative map for subsequent edits'
(ROOT/'docs/freight-blockout-layout.json').write_text(json.dumps(built,indent=2)+'\n',encoding='utf-8')
report={'source_sha256':BASE_HASH,'output_sha256':digest(MAP),'preserved_outside_brush_fragments':preserved_count,'outside_a_volume_unchanged':True,'brushes':len(brushes),'revision':'05'}
state.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
