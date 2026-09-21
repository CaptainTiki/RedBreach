"""One-time approved F04 Screening pilot. Never part of normal map rebuilds."""
from pathlib import Path
import ast,hashlib,json,math,re,shutil,sys
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'RedBreach';MAP=P/'maps/freight_01.map'
BASE='60f09581dbac8628c1f141f1cecc5fd3df5b9bfe006f1045faf481e6500a5baf'
SNAP=P/'.godot/freight_before_f04';STATE=P/'.godot/freight_f04_apply.json'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if '--apply-f04' not in sys.argv:raise SystemExit('Requires explicit --apply-f04 after paper review.')
assert digest(MAP)==BASE,'Source changed; refusing to replace later map edits.'
assert not SNAP.exists() and not STATE.exists(),'Application checkpoint exists; inspect instead of rerunning.'
plan=json.loads((ROOT/'docs/freight-a1-density-plan.json').read_text())
SNAP.mkdir()
for source,name in [(MAP,'freight_01.map'),(P/'missions/freight/freight_blockout.tscn','scene.tscn'),(P/'missions/freight/layout.json','layout.json'),(ROOT/'docs/freight-blockout-layout.json','base.json'),(P/'missions/freight/registration_f02.tscn','registration.tscn')]:shutil.copy2(source,SNAP/name)
old=MAP.read_text();pat=r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}';raws=re.findall(pat,old);assert len(raws)==1216
brushes=[];boxes=[];ns={'brushes':brushes,'boxes':boxes}
source=ast.parse((ROOT/'tools/bootstrap-freight-blockout.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['sub','cross','dot','box']],type_ignores=[]),'<metric brush primitives>','exec'),ns)
box=ns['box'];sub=ns['sub'];cross=ns['cross'];dot=ns['dot'];point_re=r'\( ([^()]*) \)'
def bounds(raw):
 ps=[list(map(float,v.split())) for v in re.findall(point_re,raw)]
 return [min(v[1] for v in ps)/32+190,min(v[2] for v in ps)/32,min(v[0] for v in ps)/32+260],[max(v[1] for v in ps)/32+190,max(v[2] for v in ps)/32,max(v[0] for v in ps)/32+260]
def cut(raw,axis,lo_value,hi_value):
 lo,hi=bounds(raw);mapaxis=[1,2,0][axis];origin=[190,0,260][axis]
 def point(m):
  v=list(map(float,m[1].split()));q=v[mapaxis]/32+origin
  assert abs(q-lo[axis])<1e-5 or abs(q-hi[axis])<1e-5
  v[mapaxis]=((lo_value if abs(q-lo[axis])<1e-5 else hi_value)-origin)*32
  return '( '+' '.join(f'{n:g}' for n in v)+' )'
 return re.sub(point_re,point,raw)
def split(raw,axis,at):
 lo,hi=bounds(raw)
 return [cut(raw,axis,lo[axis],at),cut(raw,axis,at,hi[axis])] if lo[axis]<at<hi[axis] else [raw]
WALL='greybox/MutedGreen/texture_01';CEIL='greybox/GreyPale/texture_01';RIB='greybox/GreyMedium/texture_03'
removed=[];modified=[];preserved=[]
for raw in raws:
 name=raw.splitlines()[0];lo,hi=bounds(raw)
 remove=name in ['// A1 F01 counter 4','// A1 F01 scanner 6','// A1 F01 locker 7','// A1 F01 header Staff preparation'] or (name=='// A1 F01 frame' and lo[2]>275 and hi[2]<277)
 if remove:removed.append(raw);continue
 # Subdivide only shared surfaces requiring a local palette boundary.
 candidate=(name=='// F01 ceiling 4 / neighbour' or (name.startswith('// wall') and lo[2]==261.5 and hi[2]==262 and lo[0]<96) or (name=='// A1 F01 partition' and (lo[0] in [81.875,95.875] or lo[2]==275.875)))
 parts=[raw]
 if candidate:
  for axis,at in [(0,82.125),(0,95.875),(2,262),(2,275.875)]:parts=[q for p in parts for q in split(p,axis,at)]
 changed=False
 for part in parts:
  a,b=bounds(part);lines=part.splitlines()
  for i,line in enumerate(lines):
   if not line.startswith('('):continue
   ps=[[v[1]/32+190,v[2]/32,v[0]/32+260] for v in [list(map(float,q.split())) for q in re.findall(point_re,line)]]
   axes=[j for j in range(3) if max(v[j] for v in ps)-min(v[j] for v in ps)<1e-6];assert len(axes)==1
   ax=axes[0];plane=ps[0][ax];texture=None
   if ax==1 and plane==3.5 and a[0]>=82.125 and b[0]<=95.875 and a[2]>=262 and b[2]<=275.875 and name.startswith('// F01 ceiling 4'):texture=CEIL
   if ax==0 and plane in [82.125,95.875] and a[2]>=262 and b[2]<=275.875 and name=='// A1 F01 partition':texture=WALL
   if ax==2 and plane in [262,275.875] and a[0]>=82.125 and b[0]<=95.875 and (name.startswith('// wall') or name=='// A1 F01 partition'):texture=WALL
   if texture:
    updated=re.sub(r'greybox/[^\s]+',texture,line,count=1);changed|=updated!=line;lines[i]=updated
  edited='\n'.join(lines)
  if len(parts)>1:edited=edited.replace(name,name+' / F04 material section',1)
  brushes.append(edited)
 if changed or len(parts)>1:modified.append(name)
 else:preserved.append(raw)
assert len(removed)==21,len(removed)
assert all(r in brushes for r in preserved)
basecount=len(brushes)
def prism(xy,z0,z1,material,name):
 # Convex triangular X/Y profile extruded along paper Z, with unit tangent UV axes.
 verts=[(x,y,z) for z in [z0,z1] for x,y in xy]
 pts=[((z-260)*32,(x-190)*32,y*32) for x,y,z in verts]
 centre=tuple(sum(p[i] for p in pts)/6 for i in range(3));lines=['// '+name,'{']
 for ids in [(0,1,2),(3,5,4),(0,3,4),(1,4,5),(2,5,3)]:
  a,b,c=[pts[i] for i in ids];n=cross(sub(b,a),sub(c,a))
  if dot(n,sub(a,centre))>0:b,c=c,b
  nn=[q/math.sqrt(dot(n,n)) for q in n]
  if abs(nn[0])>.999:u=[0,1,0];v=[0,0,-1]
  elif abs(nn[1])>.999:u=[1,0,0];v=[0,0,-1]
  elif abs(nn[2])>.999:u=[1,0,0];v=[0,-1,0]
  else:u=[1,0,0];v=[0,nn[2],-nn[1]]
  assert abs(dot(nn,u))<1e-6 and abs(dot(nn,v))<1e-6 and abs(dot(v,v)-1)<1e-6
  uv='[ '+' '.join(f'{q:.9g}' for q in u)+' 0 ] [ '+' '.join(f'{q:.9g}' for q in v)+' 0 ]'
  lines.append(' '.join('( '+' '.join(f'{q:g}' for q in p)+' )' for p in [a,b,c])+f' {material} {uv} 0 0.03125 0.03125')
 brushes.append('\n'.join(lines+['}']))
for side,x,sign,intervals in [('west',82.125,1,[(262,266),(270,275.875)]),('east',95.875,-1,[(262,270),(274,275.875)])]:
 for z,Z in intervals:prism([(x,3.5),(x+sign*.55,3.5),(x,2.95)],z,Z,CEIL,'F04 Screening upper corner '+side)
for ob in plan['floor_props']+plan['overhead']:
 if ob['room']!='screening' or not ob['id'].startswith('R'):continue
 b=ob['bounds'];box((b[0],ob['bottom'],b[1]),(b[2],ob['top'],b[3]),RIB,'F04 '+ob['id']+' Screening rib')
for z in plan['architecture']['rib_stations_z']:
 for side,x,sign,opening in [('west',82.125,1,(266,270)),('east',95.875,-1,(270,274))]:
  if opening[0]<=z<=opening[1]:continue
  prism([(x,3.5),(x+sign*.8,3.5),(x,2.7)],z-.125,z+.125,RIB,'F04 Screening rib knee '+side)
for a,b in [((85.5,0,275.75),(86,3.5,276.25)),((90,0,275.75),(90.5,3.5,276.25)),((86,3.2,275.75),(90,3.5,276.25))]:box(a,b,RIB,'F04 Screening exit frame')
MAP.write_text(old[:old.index('// floor')]+'\n'.join(brushes)+'\n}\n',encoding='utf-8')
assert all(r in MAP.read_text() for r in preserved)
pilot={**plan,'status':'BUILT SCREENING SOURCE - VALIDATION PENDING','built_rooms':['screening'],'pending_rooms':['admin','prep'],'built_layout':'09','routes':[r for r in plan['routes'] if r['room']=='screening'],'floor_props':[p for p in plan['floor_props'] if p['room']=='screening'],'overhead':[p for p in plan['overhead'] if p['room']=='screening']}
for file in [P/'missions/freight/layout.json',ROOT/'docs/freight-blockout-layout.json']:
 data=json.loads(file.read_text());data.update(revision='09',brushes=len(brushes),screening=pilot)
 if 'blockout_revision' in data:data.update(blockout_revision='09',status='F04 Screening pilot applied; validation pending')
 room=data['furnishing']['rooms']['A1'];room['props']=[p for p in room['props'] if not (82.125<=p['bounds'][0] and p['bounds'][2]<=95.875 and p['bounds'][1]>=262 and p['bounds'][3]<=275.875)]
 for r in room['rooms']:
  if r[0]=='02':r[4]=[89,273.5]
 data['furnishing']['retained_f01_chairs']=6
 file.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
report={'source_sha256':BASE,'output_sha256':digest(MAP),'removed_brushes':len(removed),'unchanged_brushes':len(preserved),'palette_boundary_sources':modified,'new_architecture_brushes':len(brushes)-basecount,'brushes':len(brushes),'original_scene_sha256':digest(SNAP/'scene.tscn'),'registration_sha256':digest(SNAP/'registration.tscn'),'revision':'09'}
STATE.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
