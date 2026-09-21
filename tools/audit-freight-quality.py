"""Read-only audit of source brush joints and saved prop cuboid envelopes."""
from pathlib import Path
import json,re,math,collections,itertools
P=Path('RedBreach');s=(P/'maps/freight_01.map').read_text();raws=re.findall(r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}',s);pr=r'\( ([^()]*) \)'
def sub(a,b):return [a[i]-b[i] for i in range(3)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def intersection(a,b,c,d):return [min(b[i],d[i])-max(a[i],c[i]) for i in range(3)]
brushes=[];faces=collections.defaultdict(list)
for idx,raw in enumerate(raws):
 points=[[float(v) for v in q.split()] for q in re.findall(pr,raw)];ps=[[p[1]/32,p[2]/32,p[0]/32] for p in points];lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)];center=[(lo[i]+hi[i])/2 for i in range(3)];planes=[]
 for line in raw.splitlines()[2:-1]:
  q=[[float(v) for v in p.split()] for p in re.findall(pr,line)];p=[[a[1]/32,a[2]/32,a[0]/32] for a in q];n=cross(sub(p[1],p[0]),sub(p[2],p[0]));length=math.sqrt(dot(n,n));n=[v/length for v in n]
  if dot(n,sub(p[0],center))<0:n=[-v for v in n]
  plane=dot(n,p[0]);planes.append((n,plane))
  ax=next((i for i in range(3) if abs(n[i])>.9999),None)
  if ax is not None:
   key=(ax,round(n[ax]),round(p[0][ax],5));other=[i for i in range(3) if i!=ax]
   faces[key].append((idx,[lo[other[0]],lo[other[1]],hi[other[0]],hi[other[1]]],raw.splitlines()[0],line.rsplit(')',1)[1].strip()))
 brushes.append(dict(id=idx,name=raw.splitlines()[0],lo=lo,hi=hi,planes=planes))
mesh=json.loads((P/'.godot/route_a_mesh_audit.json').read_text());clashes=[]
for m in mesh:
 for b in brushes:
  pen=intersection(m['lo'],m['hi'],b['lo'],b['hi'])
  if min(pen)<=.004:continue
  separated=False
  for n,d in b['planes']:
   nearest=[m['lo'][i] if n[i]>=0 else m['hi'][i] for i in range(3)]
   if dot(n,nearest)>d-.004:separated=True;break
  if not separated:clashes.append(dict(node=m['node'],brush=b['name'],brush_id=b['id'],penetration=pen,lo=m['lo'],hi=m['hi']))
duplicate=[]
for key,items in faces.items():
 for a,b in itertools.combinations(items,2):
  if a[0]==b[0]:continue
  u=min(a[1][2],b[1][2])-max(a[1][0],b[1][0]);v=min(a[1][3],b[1][3])-max(a[1][1],b[1][1])
  if u>.005 and v>.005 and (a[2].startswith('// RouteA') or b[2].startswith('// RouteA')):duplicate.append(dict(plane=key,a=a,b=b,area=u*v))
# In a spatial bucket, detect visible intersections between separate furniture/light/duct assemblies.
bins=collections.defaultdict(list)
for i,m in enumerate(mesh):
 a=m['lo'];b=m['hi']
 for x in range(math.floor(a[0]/4),math.floor(b[0]/4)+1):
  for y in range(math.floor(a[1]/4),math.floor(b[1]/4)+1):
   for z in range(math.floor(a[2]/4),math.floor(b[2]/4)+1):bins[x,y,z].append(i)
pairs=set();prop_clashes=[]
for ids in bins.values():
 for i,j in itertools.combinations(ids,2):
  if (i,j) in pairs:continue
  pairs.add((i,j));a=mesh[i];b=mesh[j]
  if a['assembly']==b['assembly']:continue
  pen=intersection(a['lo'],a['hi'],b['lo'],b['hi'])
  if min(pen)>.004:prop_clashes.append(dict(a=a['node'],b=b['node'],penetration=pen))
# Only coplanar faces exposed to air can cause visible surface fighting. Ignore buried joints.
def contains(brush,p,epsilon=0):
 return all(brush['lo'][i]-epsilon<=p[i]<=brush['hi'][i]+epsilon for i in range(3)) and all(dot(n,p)<=d+epsilon for n,d in brush['planes'])
exposed=[]
for item in duplicate:
 ax,sign,plane=item['plane'];other=[i for i in range(3) if i!=ax];a=item['a'][1];b=item['b'][1]
 lo=[max(a[i],b[i]) for i in range(2)];hi=[min(a[i+2],b[i+2]) for i in range(2)];visible=False
 for u,v in [(0.25,.25),(.75,.25),(.5,.5),(.25,.75),(.75,.75)]:
  p=[0,0,0];p[ax]=plane;p[other[0]]=lo[0]+(hi[0]-lo[0])*u;p[other[1]]=lo[1]+(hi[1]-lo[1])*v
  if not contains(brushes[item['a'][0]],p,1e-5) or not contains(brushes[item['b'][0]],p,1e-5):continue
  p[ax]+=sign*.015
  if not any(contains(br,p,-1e-6) for br in brushes):visible=True;break
 if visible:exposed.append(item)
conflicting=[q for q in exposed if q['a'][3]!=q['b'][3]]
print('EXPOSED FINISH CONFLICTS',len(conflicting));print('EXPOSED COPLANAR',len(exposed));print('\n'.join(str((q['a'][0],q['a'][2],q['b'][0],q['b'][2],round(q['area'],4))) for q in exposed[:35]))
report=dict(prop_vs_architecture=clashes,coplanar_map_faces=duplicate,exposed_coplanar_map_faces=exposed,prop_vs_prop=prop_clashes,exposed_finish_conflicts=conflicting)
(P/'.godot/route_a_geometry_audit.json').write_text(json.dumps(report,indent=2))
print('PROP/MAP',len(clashes));print('\n'.join(str((k,v)) for k,v in collections.Counter((c['node'].split('/')[-3],c['brush']) for c in clashes).most_common(40)))
print('COPLANAR',len(duplicate));print('\n'.join(str((x['a'][2],x['b'][2],round(x['area'],3))) for x in sorted(duplicate,key=lambda x:x['area'],reverse=True)[:25]))
print('PROP/PROP',len(prop_clashes));print(json.dumps(prop_clashes[:25],indent=1))
