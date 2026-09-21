"""One-time Route A continuation, explicitly authorized without another paper review.
Source checkpoints prevent overwriting subsequent TrenchBroom edits. Not a rebuild step.
"""
from pathlib import Path
import ast,collections,hashlib,json,math,re,shutil,sys
R=Path(__file__).resolve().parents[1];P=R/'RedBreach';M=P/'maps/freight_01.map'
BASE='d991a1c705f8a4584dbfad2757e8a42166cc6a5c8323ef5dcb62a324d6edd5ae'
S=P/'.godot/freight_before_route_a';STATE=P/'.godot/freight_route_a_apply.json'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert '--apply-route-a' in sys.argv
assert digest(M)==BASE,'Map changed; inspect before applying'
assert not S.exists(),'Checkpoint already exists; do not overwrite authored work'
S.mkdir()
for src,n in [(M,'map'),(P/'missions/freight/layout.json','layout'),(R/'docs/freight-blockout-layout.json','base'),(P/'missions/freight/freight_blockout.tscn','scene')]:shutil.copy2(src,S/n)
d=json.loads((S/'layout').read_text());old=(S/'map').read_text();pattern=r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}'
raws=re.findall(pattern,old);assert len(raws)==1221
brushes=[];boxes=[];ns={'brushes':brushes,'boxes':boxes}
tree=ast.parse((R/'tools/bootstrap-freight-blockout.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['sub','cross','dot','box']],type_ignores=[]),'<metric primitives>','exec'),ns)
box=ns['box'];pr=r'\( ([^()]*) \)'
def bounds(raw):
 ps=[list(map(float,v.split())) for v in re.findall(pr,raw)]
 return [min(p[1] for p in ps)/32+190,min(p[2] for p in ps)/32,min(p[0] for p in ps)/32+260],[max(p[1] for p in ps)/32+190,max(p[2] for p in ps)/32,max(p[0] for p in ps)/32+260]
def inside(b,x,z,pad=0):return b[0]-pad<=x<=b[2]+pad and b[1]-pad<=z<=b[3]+pad
roomrect={k:[v[0]-v[2]/2,v[1]-v[3]/2,v[0]+v[2]/2,v[1]+v[3]/2] for k,v in d['rooms'].items()}
# Outer shells and corridor segments are the scope; accepted F02/F04 interiors remain exact.
def protected(x,z):return inside([95.875,261.5,114.5,294.5],x,z) or inside([81.875,261.5,95.875,276],x,z)
edges=[e for e in d['edges'] if e['kind']=='security' or (e['a']=='A4' and e['b']=='M')]
regions=[[*roomrect['A'+str(i)]] for i in range(1,9)]
for e in edges:
 for a,b in zip(e['points'],e['points'][1:]):
  w=e['width']/2+.5;regions.append([min(a[0],b[0])-w,min(a[1],b[1])-w,max(a[0],b[0])+w,max(a[1],b[1])+w])
def scope(x,z):
 if protected(x,z):return False
 if inside(roomrect['H'],x,z) or inside(roomrect['M'],x,z):return False
 return any(inside(b,x,z) for b in regions)
def cut(raw,axis,v0,v1):
 a,b=bounds(raw);ma=[1,2,0][axis];o=[190,0,260][axis]
 def change(m):
  p=list(map(float,m[1].split()));q=p[ma]/32+o
  assert min(abs(q-a[axis]),abs(q-b[axis]))<1e-5
  p[ma]=((v0 if abs(q-a[axis])<1e-5 else v1)-o)*32
  return '( '+' '.join(f'{q:g}' for q in p)+' )'
 return re.sub(pr,change,raw)
def split(raw,axis,v):
 a,b=bounds(raw)
 return [cut(raw,axis,a[axis],v),cut(raw,axis,v,b[axis])] if a[axis]+.0001<v<b[axis]-.0001 else [raw]
W='greybox/MutedGreen/texture_01';C='greybox/GreyPale/texture_01';T='greybox/GreyMedium/texture_03'
removed=[];preserved=[];changed=0
for raw in raws:
 name=raw.splitlines()[0];a,b=bounds(raw)
 if re.match(r'// A[128] F01 (desk|cabinet|bench|counter|locker|console|pump|pipe|rack|crates|scanner) \d+',name):removed.append(raw);continue
 architectural=(name.startswith('// wall') or 'partition' in name or name.startswith('// ceiling') or name.startswith('// F01 ceiling'))
 if not architectural:brushes.append(raw);preserved.append(raw);continue
 # Exact splits only at scope boundaries. No modification to outside-A surfaces.
 parts=[raw]
 for axis,vals in [(0,[62,81.875,95.875,114.5,164,167]),(2,[49,81,93,240,261.5,276,294.5])]:
  for v in vals:parts=[r for p in parts for r in split(p,axis,v)]
 output=[];any_change=False
 for p in parts:
  lo,hi=bounds(p);x=(lo[0]+hi[0])/2;z=(lo[2]+hi[2])/2
  if not scope(x,z):output.append(p);continue
  lines=p.splitlines()
  for i,line in enumerate(lines):
   if not line.startswith('('):continue
   pts=[list(map(float,q.split())) for q in re.findall(pr,line)]
   horizontal=max(q[2] for q in pts)-min(q[2] for q in pts)<1e-5
   tex=C if horizontal and 'ceiling' in name and 'bulkhead' not in name else W
   lines[i]=re.sub(r'greybox/[^\s]+',tex,line,count=1)
  # Human-scale ceilings for the single-level Records card archive and west Dispatch.
  if name.startswith('// ceiling') and 'bulkhead' not in name and ((inside(roomrect['A7'],x,z) and lo[1]==10) or (88<=lo[0] and hi[0]<=126 and 49<=lo[2] and hi[2]<=93 and lo[1]==10)):
   newheight=7.5 if inside(roomrect['A7'],x,z) else 5.5
   p='\n'.join(lines);p=cut(p,1,newheight,newheight+.5);lines=p.splitlines()
  q='\n'.join(lines);any_change|=q!=p;output.append(q)
 if any_change:brushes.extend(output);changed+=1
 else:brushes.append(raw);preserved.append(raw)
# Additional west Dispatch ceiling cells close at the existing partition; east ladder stays tall.
box((88,5.5,49),(126,6,80),C,'RouteA Dispatch office canopy')
box((88,5.5,80),(132,6,93),C,'RouteA Dispatch approach canopy')
# Record source solids before new structural work for placement clearance.
solids=[(r.splitlines()[0],*bounds(r)) for r in brushes]
props=[];hatches=[];skipped=[]
# Existing explicit routes reserve 3m, work aisles 2m. The geometry tests walk both directions.
lanes=[]
for route in d['interior_paths'].values():
 for a,b in zip(route,route[1:]):lanes.append((a,b,1.5))
for rd in d['furnishing']['rooms'].values():
 for route in rd['optional']:
  for a,b in zip(route,route[1:]):lanes.append((a,b,1.5))
a1=json.loads((R/'docs/freight-a1-density-plan.json').read_text())
for r in a1['routes']:
 for a,b in zip(r['points'],r['points'][1:]):lanes.append((a,b,r['width']/2))
for a,b in [([140,67],[148.4,67]),([148.4,67],[148.4,62]),([112,74],[114,74]),([16,200],[20,200]),([16,228],[20,231])]:lanes.append((a,b,1.6))
for p in d['clearance_points'].values():lanes.append(([p[0],p[2]],[p[0],p[2]],.6))
def overlap(a,b,pad=0):return a[0]<b[2]+pad and a[2]>b[0]-pad and a[1]<b[3]+pad and a[3]>b[1]-pad
def lane_hit(rect,extra=0):
 for a,b,w in lanes:
  if overlap(rect,[min(a[0],b[0])-w-extra,min(a[1],b[1])-w-extra,max(a[0],b[0])+w+extra,max(a[1],b[1])+w+extra]):return True
 return False
# Keep a full stair approach and sight cone, with generous physical landing clearances.
exclusions=[([48,221,56,239],-2,4),([54,116,62,133],0,8),([141,117,149,134],2,10),([127,172,150,181],0,10),([146,58,154,70],2,10),([12,198,20,204],-2,1),([13,225,19,232],-2,1),([28,48,35,56],4,7),([109,71,116,77],2,5)]
# room-key, function, bounds, floor, ceiling. Mezzanines are separate working zones.
zones=[]
for k in ['A1','A2','A8']:
 for rr in d['furnishing']['rooms'][k]['rooms']:
  if k=='A1' and rr[0] not in ['03','04']:continue
  zones.append(dict(id=k+'_'+rr[0],room=k,title=rr[1],bounds=rr[2],floor=d['heights'][k],ceiling=d['heights'][k]+rr[3],sample=rr[4]))
zones += [dict(id=i,room=k,title=t,bounds=b,floor=f,ceiling=c,sample=s) for i,k,t,b,f,c,s in [
 ('A3_Floor','A3','Records processing',[20,120,70,146],0,8,[30,140]),('A3_Stacks','A3','Records machine aisle',[70.125,120,84,146],0,8,[79,142]),('A3_Upper','A3','Archive transfer gallery',[20,110,84,118],4,8,[46,115]),
 ('A7_South','A7','Document retrieval',[22,63.125,62,81],4,7.5,[28,75]),('A7_North','A7','Secure records',[22,41,62,62.875],4,7.5,[45,45]),
 ('A4_West','A4','Freight dispatch',[88,49,125.875,79.875],2,5.5,[98,58]),('A4_South','A4','Dispatch reception gallery',[88,80.125,131.875,93],2,5.5,[96,88]),('A4_East','A4','Security operations',[126.125,49,154,79.875],2,10,[136,56]),('A4_Exit','A4','Watch handover',[132.125,80.125,154,93],2,10,[136,88]),
 ('A5_Low','A5','Surveillance equipment',[128,114,158,129.8],2,10,[133,120]),('A5_Upper','A5','Watch gallery',[128,130,150,144],6,10,[135,133]),
 ('A6_Upper','A6','Supervisor overlook',[110,166,130,180],6,10,[113,169]),('A6_West','A6','Clearance work office',[110,184.125,129.875,198],0,3.5,[119,195]),('A6_East','A6','Exit processing',[130.125,184.125,156,198],0,3.5,[140,194]),('A6_Low','A6','Office systems',[110,166,127,183.8],0,3.5,[116,170])]]
# Local low ceilings under/away from upper circulation. Physical faces terminate on existing walls.
for b in [[110,184.125,129.875,198],[130.125,184.125,156,198],[110,166,127,180]]:box((b[0],3.5,b[1]),(b[2],3.8,b[3]),C,'RouteA Clearance office ceiling')
# floor/ceiling and wall obstruction from original authoritative brushes.
def fits(rect,y,h,spacing=.25):
 if lane_hit(rect):return False
 if any(y<v and y+h>u and overlap(rect,b) for b,u,v in exclusions):return False
 if any(overlap(rect,h['landing'],.3) for h in hatches):return False
 for n,a,b in solids:
  if a[1]<y+h-.01 and b[1]>y+.04 and overlap(rect,[a[0],a[2],b[0],b[2]],.15):return False
 if any(p['bottom']<y+h and p['top']>y and p['kind'] not in ['light','duct','display','chair'] and overlap(rect,p['bounds'],spacing) for p in props):return False
 # Four floor corners must land on the chosen floor, not a stair or a void.
 for x,z in [(rect[0],rect[1]),(rect[2],rect[1]),(rect[0],rect[3]),(rect[2],rect[3])]:
  if not any(abs(b[1]-y)<.02 and inside([a[0],a[2],b[0],b[2]],x,z,.01) for n,a,b in solids):return False
 return True
serial=collections.Counter()
def add(room,kind,b,y,h,name='',facing='south',force=False):
 if not force and not fits(b,y,h):skipped.append((room,kind,b));return None
 serial[room]+=1
 p=dict(id=f'{room}_{serial[room]:03}',room=room,kind=kind,bounds=b,bottom=y,top=y+h,name=name or kind.title(),facing=facing)
 props.append(p);return p
# Candidate closed ceiling hatches have a protected landing outside the primary route.
for room,x,z,f,c in [('A1',92,282,0,3.5),('A2',27,198,-2,1.5),('A8',97,201,-2,1.5),('A3',64,139,0,8),('A7',57,57,4,7.5),('A4',135,74,2,10),('A5',154,137,2,10),('A6',151,182,0,10)]:
 b=[x-1.75,z-1.75,x+1.75,z+1.75]
 if fits(b,f,2.8,0):
  hatches.append(dict(id=room+'_H',room=room,center=[x,c,z],landing=b,floor=f,aperture_m=2.5,service_pocket_height_m=1.5,status='SEALED RESERVATION; no spawn, cut or open-state collision'))
 else:print('HATCH NEEDS REPOSITION',room,x,z)
# Approved Admin/Prep compositions, excluding architecture handled in the source map.
for ob in a1['floor_props']+a1['overhead']:
 if ob['room'] not in ['admin','prep']:continue
 kind=ob['kind'];b=ob['bounds']
 if kind=='beam':box((b[0],ob['bottom'],b[1]),(b[2],ob['top'],b[3]),T,'RouteA '+ob['id']);continue
 # Hatch reservation supersedes props occupying its landing volume.
 if ob['bottom']<2.8 and any(overlap(b,h['landing'],.15) for h in hatches):continue
 add('A1',kind,b,ob['bottom'],ob['top']-ob['bottom'],ob['name'],force=True)
# Staff workstations: clear low islands with paired terminals, seats and task lights.
def workstation(room,x,z,y,w=4,h=.78):
 p=add(room,'desk',[x,z,x+w,z+1.8],y,h,'Paired workstations')
 if p:
  for xx in [x+.6,x+w-1.25]:add(room,'chair',[xx,z+2,xx+.65,z+2.65],y,.9,force=True)
  return True
 return False
# Deliberate functional clusters inside each existing compartment. Rejected positions stay clear.
for room,y,rows in [
 ('A2',-2,[(10,189),(24,190),(24,195),(10,208),(24,208),(24,219),(34,208),(34,214),(47,210)]),
 ('A8',-2,[(67,187),(76,187),(87,187),(67,198)]),
 ('A3',0,[(23,124),(23,131),(23,138),(35,124),(35,131),(35,138),(49,136),(60,137)]),
 ('A7',4,[(25,67),(35,72),(52,66),(25,43),(35,43),(45,43),(51,51)]),
 ('A4',2,[(91,52),(101,52),(111,52),(91,60),(101,60),(111,60),(91,69),(101,69),(114,67),(129,52),(138,52),(146,73),(91,86),(119,86),(133,86),(146,86)]),
 ('A5',6,[(129,131),(140,131)]),
 ('A6',6,[(111,168),(123,168)]),
 ('A6',0,[(112,168),(120,168),(112,178),(112,187),(121,187),(112,193),(132,187),(141,193),(132,193)])]:
 for x,z in rows:workstation(room,x,z,y)
# Industrial inspection/test islands, repair benches, and substantial equipment groups.
for room,y,kind,items in [
 ('A2',-2,'pump',[(35,188,5,4),(46,188,5,4),(46,197,5,4)]),
 ('A2',-2,'machine',[(34,227,4,4),(45,215,5,4),(24,229,5,3)]),
 ('A8',-2,'machine',[(67,207,4,4),(67,218,4,5),(67,231,4,5),(79,222,4,5),(89,226,5,4),(96,227,3,4)]),
 ('A8',-2,'desk',[(78,208,5,2),(78,234,5,2)]),
 ('A3',0,'server',[(61,122,5,3),(61,130,5,3),(76,123,5,3),(76,137,5,3)]),
 ('A5',2,'server',[(130,116,6,2),(130,123,6,2),(152,124,4,2)]),
 ('A6',0,'server',[(112,180,5,2),(121,180,5,2)])]:
 for x,z,w,depth in items:add(room,kind,[x,z,x+w,z+depth],y,.9 if kind=='desk' else 2.5,'Test equipment' if kind=='pump' else 'Service assembly')
# Archive shelving islands form aisles, not a succession of empty large rooms.
for room,y,rows in [('A3',0,[(23,121),(23,128),(23,135),(35,121),(35,128),(35,135)]),('A7',4,[(25,59),(44,59),(25,77),(34,77),(52,76),(45,47),(53,47)]),('A8',-2,[(86.5,207),(96,207),(87,217),(96,217),(87,238),(94,238)]),('A2',-2,[(10,227),(24,227),(10,236),(24,236)])]:
 for x,z in rows:add(room,'rack',[x,z,x+5,z+1.1],y,2.4,'Archive / parts shelves')
# Perimeter furniture is paired with circulation bays. 3m service gaps between banks.
for zone in zones:
 if zone['room']=='A1':continue
 x,z,X,Z=zone['bounds'];f=zone['floor'];c=zone['ceiling'];room=zone['room'];industrial=room in ['A2','A8']
 for side in ['north','south','west','east']:
  span=(X-x) if side in ['north','south'] else (Z-z)
  count=max(1,int((span-4)//7))
  for i in range(count):
   t=2+i*7
   if side=='north':b=[x+t,z+.45,min(x+t+4.5,X-1),z+1.5];facing='south'
   elif side=='south':b=[x+t,Z-1.5,min(x+t+4.5,X-1),Z-.45];facing='north'
   elif side=='west':b=[x+.45,z+t,x+1.5,min(z+t+4.5,Z-1)];facing='east'
   else:b=[X-1.5,z+t,X-.45,min(z+t+4.5,Z-1)];facing='west'
   if min(b[2]-b[0],b[3]-b[1])<.5:continue
   kind=['storage','server','air'][i%3] if not industrial else ['rack','air','storage'][i%3]
   add(room,kind,b,f,2.4,'Environmental services' if kind=='air' else 'Equipment bank',facing)
 # Light fixtures and bounded service runs read as a complete overhead composition.
 for xx in [x+4+i*7 for i in range(max(1,int((X-x-4)//7)))]:
  for zz in [z+4+i*8 for i in range(max(1,int((Z-z-4)//8)))]:
   lb=[xx-1.1,zz-.15,xx+1.1,zz+.15]
   if any(overlap(lb,h['landing'],.4) for h in hatches):continue
   if math.dist([xx,zz],zone['sample'])<1.5:continue
   # Avoid lights suspended inside upper floor slabs; resolve true overhead from the source.
   tops=[a[1] for n,a,b in solids if a[1]>f+2.7 and inside([a[0],a[2],b[0],b[2]],xx,zz)]
   actual=min(tops+[c]);lh=actual-.32
   add(room,'light',lb,lh,.16,'Task lighting',force=True)
 # Perimeter ducts remain above standing height with a physical gap from their mounting ceiling.
 db=[x+1,z+.65,X-1,z+1.15]
 if not any(overlap(db,h['landing'],.3) for h in hatches):add(room,'duct',db,c-.6,.4,'Ventilation trunk',force=True)
# Structural ribs are embedded in existing walls; skips at portals and working apertures.
def solid_at(x,y,z):return any(a[0]-.001<=x<=b[0]+.001 and a[1]-.001<=y<=b[1]+.001 and a[2]-.001<=z<=b[2]+.001 for n,a,b in solids)
# Use source wall faces for supports to avoid floating uprights at openings.
for zone in zones:
 x,z,X,Z=zone['bounds'];f=zone['floor'];c=zone['ceiling']
 for side in ['west','east','north','south']:
  span=(Z-z) if side in ['west','east'] else (X-x)
  for i in range(1,max(2,int(span/6))):
   t=i*span/max(2,int(span/6))
   xx=(x if side=='west' else X) if side in ['west','east'] else x+t
   zz=(z if side=='north' else Z) if side in ['north','south'] else z+t
   if not solid_at(xx,f+1,zz):continue
   a=[xx,f,zz];b=[xx,c,zz]
   if side in ['west','east']:
    a[0]=xx if side=='west' else xx-.22;b[0]=xx+.22 if side=='west' else xx;a[2]-=.12;b[2]+=.12
   else:a[0]-=.12;b[0]+=.12;a[2]=zz if side=='north' else zz-.22;b[2]=zz+.22 if side=='north' else zz
   if lane_hit([a[0],a[2],b[0],b[2]],.0):continue
   if any(overlap([a[0],a[2],b[0],b[2]],p['bounds'],.02) and p['bottom']<f+2 for p in props):continue
   # Only stretch to actual roof, not through a mezzanine.
   roofs=[u[1] for n,u,v in solids if u[1]>f+2.5 and inside([u[0],u[2],v[0],v[2]],(a[0]+b[0])/2,(a[2]+b[2])/2)]
   b[1]=min([c]+roofs);box(a,b,T,'RouteA '+zone['id']+' wall rib')
# Corridor frames: station only where both sidewalls and a level floor/ceiling exist.
corridor_count=0
for edge in edges:
 for a,b in zip(edge['points'],edge['points'][1:]):
  length=math.dist(a,b)
  if length<10:continue
  dx=(b[0]-a[0])/length;dz=(b[1]-a[1])/length;nx=-dz;nz=dx;half=edge['width']/2
  for distance in range(5,int(length)-3,8):
   x=a[0]+dx*distance;z=a[1]+dz*distance
   if any(inside(bb,x,z,1) for bb in roomrect.values()):continue
   if not scope(x,z):continue
   floor=[v[1] for n,u,v in solids if n.startswith('// floor') and inside([u[0],u[2],v[0],v[2]],x,z)]
   if not floor:continue
   f=max(floor);roof=[u[1] for n,u,v in solids if 'ceiling' in n and u[1]>f+2 and inside([u[0],u[2],v[0],v[2]],x,z)]
   if not roof:continue
   c=min(roof)
   if not all(solid_at(x+nx*s*half,f+1,z+nz*s*half) for s in [-1,1]):continue
   # Level only; no placement across stair landings, readers or release switches.
   if any(math.dist([x,z],[g[1],g[2]])<4 for g in d['gates']):continue
   if any(math.dist([x,z],s[3])<5 or math.dist([x,z],s[4])<5 for s in d['stairs']):continue
   for sign in [-1,1]:
    xx=x+nx*sign*(half-.13);zz=z+nz*sign*(half-.13)
    sx=.26 if nx else .35;sz=.26 if nz else .35
    box((xx-sx/2,f,zz-sz/2),(xx+sx/2,c,zz+sz/2),T,'RouteA corridor rib')
   sx=edge['width'] if nx else .35;sz=edge['width'] if nz else .35
   box((x-sx/2,c-.25,z-sz/2),(x+sx/2,c,z+sz/2),T,'RouteA corridor overhead')
   add('A_Halls','light',[x-1,z-.13,x+1,z+.13],c-.44,.16,'Compartment light',force=True)
   # Alternating side service boxes remain outside the protected centre 3m lane.
   if corridor_count%2==0:
    xx=x+nx*(half-.55)+dx*2;zz=z+nz*(half-.55)+dz*2
    sx=.55 if nx else 1.6;sz=.55 if nz else 1.6
    bb=[xx-sx/2,zz-sz/2,xx+sx/2,zz+sz/2]
    if fits(bb,f,2.3,.1):add('A_Halls','air',bb,f,2.3,'Air recirculation', 'west' if nx>0 else 'east' if nx<0 else 'north' if nz>0 else 'south')
   corridor_count+=1
# All hatch reservations remain sealed. The closed grate is an authored placeholder under the intact roof.
for h in hatches:
 x,c,z=h['center'];add(h['room'],'hatch',[x-1.4,z-1.4,x+1.4,z+1.4],c-.12,.12,h['id']+' SERVICE HATCH',force=True)
# Update former F01 metadata to reflect superseded furnishing, keeping route/ceiling contracts.
for k,rd in d['furnishing']['rooms'].items():
 rd['props']=[p for p in rd['props'] if p['kind'] in ['selector','cache']]
d['furnishing']['retained_f01_chairs']=0
# F04 planned desks now occupy this old vertical QA sample; test actual open office aisle.
d['furnishing']['rooms']['A1']['rooms'][1][4]=[68.8,268]
manifest=dict(revision='11',status='BUILT - VALIDATION PENDING',paper_review='Explicitly waived by user for the rest of admin / all Route A',zones=zones,props=props,hatches=hatches,corridor_bays=corridor_count,protected_route_width_m=3,notes=['One continuous dark floor at each existing elevation','Closed hatch placeholders reserve later enclosed service pockets; no active spawn','Registration and Screening preserved','Route B, hub, arrival/lift and Maintenance destination remain unchanged'])
M.write_text(old[:old.index('// floor')]+'\n'.join(brushes)+'\n}\n',encoding='utf-8')
d.update(revision='11',brushes=len(brushes),route_a_style=manifest)
(P/'missions/freight/layout.json').write_text(json.dumps(d,indent=2)+'\n')
base=json.loads((S/'base').read_text());base.update(revision='11',blockout_revision='11',brushes=len(brushes),status='Route A architecture and furnishing - validation pending',route_a_style=manifest,furnishing=d['furnishing']);(R/'docs/freight-blockout-layout.json').write_text(json.dumps(base,indent=2)+'\n')
(R/'docs/freight-route-a-style.json').write_text(json.dumps(manifest,indent=2)+'\n')
report=dict(source_sha256=BASE,output_sha256=digest(M),original_scene_sha256=digest(S/'scene'),brushes=len(brushes),removed_old_furniture_brushes=len(removed),palette_changed_source_brushes=changed,unchanged_source_brushes=len(preserved),prop_assemblies=len(props),by_room=dict(collections.Counter(p['room'] for p in props)),by_kind=dict(collections.Counter(p['kind'] for p in props)),hatches=len(hatches),corridor_bays=corridor_count)
STATE.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
