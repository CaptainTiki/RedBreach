"""Scoped quality corrections on the built Route A source; never a rebuild step."""
from pathlib import Path
import json,re,hashlib,ast
R=Path(__file__).resolve().parents[1];P=R/'RedBreach';mp=P/'maps/freight_01.map';lp=P/'missions/freight/layout.json'
assert hashlib.sha256(mp.read_bytes()).hexdigest()=='7fcb6babf17cfe875f5ff0e79f0011b1524320a65b93d17c7083d3cc674371d0'
s=mp.read_text();raws=re.findall(r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}',s)
brushes=[r for r in raws if r.splitlines()[0] not in ['// RouteA Dispatch office canopy','// RouteA Dispatch approach canopy']];assert len(brushes)==len(raws)-2
boxes=[];ns={'brushes':brushes,'boxes':boxes};tree=ast.parse((R/'tools/bootstrap-freight-blockout.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['sub','cross','dot','box']],type_ignores=[]),'metric','exec'),ns)
ns['box']((114.5,5.5,49),(126,6,80),'greybox/GreyPale/texture_01','RouteA quality Dispatch canopy extension')
ns['box']((114.5,5.5,80),(132,6,93),'greybox/GreyPale/texture_01','RouteA quality Dispatch approach extension')
mp.write_text(s[:s.index('// floor')]+'\n'.join(brushes)+'\n}\n')
d=json.loads(lp.read_text());m=d['route_a_style'];props=m['props'];byid={o['id']:o for o in props}
def shift(id,dx=0,dy=0,dz=0):
 o=byid[id];o['bounds']=[o['bounds'][0]+dx,o['bounds'][1]+dz,o['bounds'][2]+dx,o['bounds'][3]+dz];o['bottom']+=dy;o['top']+=dy
shift('A1_047',dy=-.25,dz=.15);shift('A1_048',dy=-.25,dz=.2);shift('A1_049',dx=-.3,dy=-.25)
for id in ['A3_048','A3_049']:shift(id,dx=-.5)
for id in ['A4_104','A4_105','A4_106']:shift(id,dx=1.2)
shift('A5_018',dx=.45);shift('A_Halls_067',dx=-.3)
# Terminate trunks on each side of actual partitions rather than burying visible grilles in walls.
for id,cuts in [('A4_107',[(127.125,143.70,4.9,5.3),(144.05,153,9.4,9.8)]),('A5_019',[(129,137.82,9.4,9.8),(138.18,149,9.4,9.8)])]:
 o=byid[id];props.remove(o)
 for i,(x,X,y,Y) in enumerate(cuts):
  p=dict(o);p.update(id=id+'_'+str(i+1),bounds=[x,o['bounds'][1],X,o['bounds'][3]],bottom=y,top=Y);props.append(p)
# Earlier Screening C1 now uses the same sealed reservation language as the later rooms.
h=dict(id='Screening_C1',room='A1',center=[90,3.5,265],landing=[88.25,263.25,91.75,266.75],floor=0,aperture_m=2.5,status='SEALED RESERVATION; no active spawn or roof opening',emergence_route_paper_xz=[[90,265],[89.5,266.5],[88,268]])
m['hatches'].append(h);props.append(dict(id='Screening_C1',room='A1',kind='hatch',bounds=[88.6,263.6,91.4,266.4],bottom=3.38,top=3.5,name='Screening sealed service hatch',facing='south'))
roof_tops={'A1_H':3.75,'A2_H':1.75,'A8_H':1.75,'A7_H':8.0,'A4_H':5.8,'A5_H':10.25,'A3_H':8.25,'A6_H':10.25,'Screening_C1':3.75}
for h in m['hatches']:
 x,y,z=h['center'];base=roof_tops[h['id']]
 h.update(service_pocket_height_m=2.0,intended_enemies=['small melee','regular melee'],backing_volume_min=[x-1.5,base,z-1.5],backing_volume_max=[x+1.5,base+2,z+1.5],backing_status='Space reservation for an enclosed service pocket; existing roof remains sealed until encounter construction',staging_clearance_note='Fits current 1.1 m regular-melee collider plus margin; large body emergence test does not authorize a spitter staging fit')
m['quality_pass']='Geometry joins, side aisles, early-room consistency, backing-volume audit and render batching';m['revision']='12';m['status']='QUALITY PASS - VALIDATION PENDING';m.pop('validation',None)
d.update(revision='12',route_a_style=m)
for file in [lp,R/'docs/freight-blockout-layout.json']:
 dd=d if file==lp else json.loads(file.read_text());dd.update(revision='12',route_a_style=m)
 if 'blockout_revision' in dd:dd['blockout_revision']='12'
 file.write_text(json.dumps(dd,indent=2)+'\n')
(R/'docs/freight-route-a-style.json').write_text(json.dumps(m,indent=2)+'\n')
report=dict(map_sha256=hashlib.sha256(mp.read_bytes()).hexdigest(),old_registration_sha256=hashlib.sha256((P/'missions/freight/registration_f02.tscn').read_bytes()).hexdigest(),old_placement_sha256=hashlib.sha256((P/'missions/freight/route_a_furnishing.tscn').read_bytes()).hexdigest(),prop_count=len(props),hatches=len(m['hatches']))
(P/'.godot/freight_quality_apply.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
