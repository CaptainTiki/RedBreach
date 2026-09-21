"""Follow-up to the new Route A pass: visual inspection and clearance corrections."""
from pathlib import Path
import ast,collections,json,math,re,hashlib
R=Path(__file__).resolve().parents[1];P=R/'RedBreach';mp=P/'maps/freight_01.map';lp=P/'missions/freight/layout.json'
d=json.loads(lp.read_text());plan=d['route_a_style'];s=mp.read_text();pattern=r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}';raws=re.findall(pattern,s)
assert not any('// RouteA finishing' in r for r in raws),'Already finished; preserve later edits'
pr=r'\( ([^()]*) \)'
def bounds(raw):
 ps=[list(map(float,v.split())) for v in re.findall(pr,raw)]
 return [min(p[1] for p in ps)/32+190,min(p[2] for p in ps)/32,min(p[0] for p in ps)/32+260],[max(p[1] for p in ps)/32+190,max(p[2] for p in ps)/32,max(p[0] for p in ps)/32+260]
def inside(b,x,z,pad=0):return b[0]-pad<=x<=b[2]+pad and b[1]-pad<=z<=b[3]+pad
def overlap(a,b,pad=0):return a[0]<b[2]+pad and a[2]>b[0]-pad and a[1]<b[3]+pad and a[3]>b[1]-pad
brushes=[];boxes=[];ns={'brushes':brushes,'boxes':boxes,'math':math}
tree=ast.parse((R/'tools/bootstrap-freight-blockout.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['sub','cross','dot','box']],type_ignores=[]),'metric','exec'),ns)
tree=ast.parse((R/'tools/apply-freight-screening.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prism'],type_ignores=[]),'corner','exec'),ns)
box=ns['box'];prism=ns['prism'];W='greybox/MutedGreen/texture_01';C='greybox/GreyPale/texture_01';T='greybox/GreyMedium/texture_03'
roomrect={k:[v[0]-v[2]/2,v[1]-v[3]/2,v[0]+v[2]/2,v[1]+v[3]/2] for k,v in d['rooms'].items()}
doors=[]
for r in d['furnishing']['rooms'].values():
 for door in r['doors']:
  x,z=door[1];w=float(door[3]) if len(door)>3 else 4
  doors.append([x-.7,z-w/2-.1,x+.7,z+w/2+.1] if door[2]=='x' else [x-w/2-.1,z-.7,x+w/2+.1,z+.7])
removed=[]
for raw in raws:
 n=raw.splitlines()[0];a,b=bounds(raw);x=(a[0]+b[0])/2;z=(a[2]+b[2])/2
 if 'RouteA' in n and 'wall rib' in n and any(overlap([a[0],a[2],b[0],b[2]],q) for q in doors):removed.append(n);continue
 if n=='// A gallery guard':
  # Open physical rail assemblies retain their tested outer boundaries while revealing the room below.
  sx=b[0]-a[0];sz=b[2]-a[2];longx=sx>sz;length=max(sx,sz);count=math.ceil(length/1.75)
  for off in [.5,1.1]:box((a[0],a[1]+off,a[2]),(b[0],a[1]+off+.08,b[2]),T,'RouteA finishing open gallery rail')
  for i in range(count+1):
   t=i/count
   if longx:
    xx=a[0]+(sx-.1)*t;box((xx,a[1],a[2]),(xx+.1,b[1],b[2]),T,'RouteA finishing gallery post')
   else:
    zz=a[2]+(sz-.1)*t;box((a[0],a[1],zz),(b[0],b[1],zz+.1),T,'RouteA finishing gallery post')
  continue
 if n.startswith('// wall') and any(inside(roomrect['A'+str(i)],x,z,.51) for i in range(1,9)) and not inside([81.875,261.5,114.51,294.51],x,z):
  raw=re.sub(r'greybox/[^\s]+',W,raw)
 brushes.append(raw)
# Selectively lower single-level working zones; keep the ladder and occupied upper routes tall.
canopies=[([20,120,46,146],3.5),([126,49,144,80],5.5),([132,80,154,93],5.5)]
for b,y in canopies:box((b[0],y,b[1]),(b[2],y+.3,b[3]),C,'RouteA finishing office canopy')
box((143.75,5.5,49),(144,10,80),W,'RouteA finishing ladder service bulkhead')
# Correct props that intruded into pre-descent sightlines.
plan['props']=[o for o in plan['props'] if o['id']!='A2_066' and not (o['room']=='A6' and o['bottom']==6 and o['bounds'][1]>=178.4 and o['bounds'][3]<=180)]
for h in plan['hatches']:
 if h['room']=='A4':h['center'][1]=5.5
for o in plan['props']:
 if o['room']=='A4' and o['kind']=='hatch':o['bottom']=5.38;o['top']=5.5
for zone in plan['zones']:
 if zone['id'] in ['A4_East','A4_Exit']:zone['ceiling']=5.5
plan['local_canopies']=[dict(bounds=b,ceiling=y) for b,y in canopies]
solids=[(r.splitlines()[0],*bounds(r)) for r in brushes]
def ceiling_at(x,z,f,default):
 tops=[a[1] for n,a,b in solids if a[1]>f+2.5 and inside([a[0],a[2],b[0],b[2]],x,z,.001)]
 return min([default]+tops)
def solid_at(x,y,z):return any(a[0]-.001<=x<=b[0]+.001 and a[1]-.001<=y<=b[1]+.001 and a[2]-.001<=z<=b[2]+.001 for n,a,b in solids)
# Move light housings down with the actual local roof. They must be attached, never floating above a canopy.
for o in plan['props']:
 if o['kind']!='light' or o['room']=='A_Halls':continue
 b=o['bounds'];x=(b[0]+b[2])/2;z=(b[1]+b[3])/2
 f=next((q['floor'] for q in plan['zones'] if q['room']==o['room'] and inside(q['bounds'],x,z) and q['floor']<o['bottom'] and q['ceiling']>=o['bottom']-.4),d['heights'][o['room']])
 c=ceiling_at(x,z,f,o['top']+.4)
 if o['top']>c-.1:o['bottom']=c-.32;o['top']=c-.16
# New angled upper corners connect to real side walls, leaving door apertures untouched.
for zone in plan['zones']:
 x,z,X,Z=zone['bounds'];f=zone['floor'];c=zone['ceiling']
 if zone['id']=='A4_East':X=144
 # Local segments avoid spanning an aperture or a roof-height change.
 for side,xx,sign in [('west',x,1),('east',X,-1)]:
  for i in range(math.ceil((Z-z)/2)):
   zz=z+i*2;ZZ=min(zz+2,Z)
   if ZZ-zz<.05:continue
   if not all(solid_at(xx,f+1,v) for v in [zz+.02,(zz+ZZ)/2,ZZ-.02]):continue
   c0=ceiling_at(xx+sign*.3,(zz+ZZ)/2,f,c)
   if any(overlap([min(xx,xx+sign*.5),zz,max(xx,xx+sign*.5),ZZ],h['landing'],.2) for h in plan['hatches']):continue
   prism([(xx,c0),(xx+sign*.45,c0),(xx,c0-.45)],zz,ZZ,C,'RouteA finishing upper corner '+zone['id'])
 # A shallow suspended beam rhythm on larger bays. Perimeter supports already exist.
 for zz in [z+6+i*8 for i in range(max(0,int((Z-z-6)//8)+1))]:
  if zz>Z-1:continue
  if any(overlap([x,zz-.125,X,zz+.125],h['landing'],.4) for h in plan['hatches']):continue
  # Split spans at canopy and upper-floor boundaries to preserve headroom.
  cuts=sorted(set([x,X]+[v for v in [46,56,60,74,126,127,130,144,150] if x<v<X]))
  for xx,XX in zip(cuts,cuts[1:]):
   cc=ceiling_at((xx+XX)/2,zz,f,c)
   if cc-f<2.9:continue
   # QA height samples remain on plain ceiling between structural bays.
   if any(abs(zz-q['sample'][1])<.4 and xx<=q['sample'][0]<=XX for q in plan['zones']):continue
   box((xx,cc-.22,zz-.125),(XX,cc,zz+.125),T,'RouteA finishing ceiling rib '+zone['id'])
# Keep old source material faces entirely outside this scope; fingers and floor levels unchanged.
mp.write_text(s[:s.index('// floor')]+'\n'.join(brushes)+'\n}\n')
d['brushes']=len(brushes)
for file in [lp,R/'docs/freight-blockout-layout.json']:
 dd=d if file==lp else json.loads(file.read_text());dd['brushes']=len(brushes);dd['route_a_style']=plan;file.write_text(json.dumps(dd,indent=2)+'\n')
(R/'docs/freight-route-a-style.json').write_text(json.dumps(plan,indent=2)+'\n')
rp=P/'.godot/freight_route_a_apply.json';r=json.loads(rp.read_text());r.update(output_sha256=hashlib.sha256(mp.read_bytes()).hexdigest(),brushes=len(brushes),prop_assemblies=len(plan['props']),finishing_removed_door_ribs=removed);rp.write_text(json.dumps(r,indent=2)+'\n')
print('Finishing:',len(brushes),'brushes;',len(plan['props']),'props; removed doorway ribs',len(removed))
