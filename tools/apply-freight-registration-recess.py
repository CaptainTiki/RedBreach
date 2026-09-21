"""Apply only the approved F-03 registration changes; never part of a normal rebuild."""
from pathlib import Path
import ast, hashlib, json, re, shutil, sys
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'RedBreach'
MAP=P/'maps/freight_01.map'; SNAP=P/'.godot/freight_before_f03'
BASE='07d6b5b95f8360945c0f24b030139c6d1103c3e9afe3b7b3d3c5bdeaee8ba5bc'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if '--apply-f03' not in sys.argv:raise SystemExit('Requires --apply-f03 after paper review.')
if (P/'.godot/freight_f03_apply.json').exists():raise SystemExit('F03 already applied; do not overwrite subsequent scene or metadata edits.')
if SNAP.exists():
 if '--resume-f03' not in sys.argv:raise SystemExit('Checkpoint exists; inspect before an explicit resume.')
 assert digest(SNAP/'freight_01.map')==BASE
else:
 if digest(MAP)!=BASE:raise SystemExit('Source changed; refusing to overwrite later edits.')
 SNAP.mkdir()
 for source,name in [(MAP,'freight_01.map'),(P/'missions/freight/layout.json','layout.json'),(ROOT/'docs/freight-blockout-layout.json','base.json'),(P/'missions/freight/freight_blockout.tscn','scene.tscn'),(P/'missions/freight/registration_f02.tscn','registration.tscn')]:shutil.copy2(source,SNAP/name)
plan=json.loads((ROOT/'docs/freight-registration-recess-plan.json').read_text())
assert plan['staff_door']['centre'][1]==0 and plan['recess_rectangles'][2][2]==104
brushes=[];boxes=[];ns={'brushes':brushes,'boxes':boxes}
source=ast.parse((ROOT/'tools/bootstrap-freight-blockout.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ('sub','cross','dot','box','merge_grid')],type_ignores=[]),'<metric primitives only>','exec'),ns)
box=ns['box'];merge=ns['merge_grid']
old=(SNAP/'freight_01.map').read_text();raws=re.findall(r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}',old)
assert len(raws)==1201
removed=[r for r in raws if r.splitlines()[0]=='// F01 floor 12'];assert len(removed)==1
brushes.extend(r for r in raws if r not in removed);preserved=len(brushes)
# Preserve the full floor support, carving just the top 0.25 m of the chosen strips.
box((62,-4,262),(114,-.25,294),'greybox/Dark/texture_01','F03 lower floor support')
raised={}
for ix in range(124,228):
 for iz in range(524,588):
  x,z=(ix+.5)/2,(iz+.5)/2
  lower=any(a<=x<c and b<=z<d for a,b,c,d in plan['recess_rectangles'])
  if not lower:raised[ix,iz]=0
for i,(x,z,X,Z,_) in enumerate(merge(raised)):
 box((x,-.25,z),(X,0,Z),'greybox/Dark/texture_06',f'F03 raised floor {i}')
for z,Z in [(278,278.5),(281.5,282)]:box((105.875,0,z),(106.125,3.2,Z),'greybox/Dark/texture_01','F03 staff door infill')
output=old[:old.index('// floor')]+'\n'.join(brushes)+'\n}\n'
assert MAP.read_text() in [old,output], 'Source no longer matches baseline or exact generated output'
MAP.write_text(output,encoding='utf-8')
assert all(r in MAP.read_text() for r in raws if r not in removed)
# Audit every half-metre floor cell; only the drawn lower strips can change height.
assert len(raised)+sum(any(a<=(ix+.5)/2<c and b<=(iz+.5)/2<d for a,b,c,d in plan['recess_rectangles']) for ix in range(124,228) for iz in range(524,588))==104*64
plan.update(status='BUILT SOURCE - VALIDATION PENDING',built_layout='08')
for file in [P/'missions/freight/layout.json',ROOT/'docs/freight-blockout-layout.json']:
 baseline=SNAP/('layout.json' if file.parent.name=='freight' else 'base.json')
 data=json.loads(baseline.read_text());data.update(revision='08',brushes=len(brushes),registration_recess=plan)
 if 'blockout_revision' in data:data.update(blockout_revision='08',status='F03 source applied; scene validation pending')
 reg=data['registration'];reg.update(status='F02 composition refined by approved F03',built_layout='08',main_route=plan['main_route'])
 reg['optional_routes'][0]=[[100,272],[100,290],[106,290]]
 reg['rooms'][-1][1]='Registration operations'
 for key in ['walk_points','a_walk_points']:
  if key in data:data[key]=[[100,v[1]] if v in [[104,270],[104,272]] else v for v in data[key]]
 if 'interior_paths' in data:
  for key,route in data['interior_paths'].items():data['interior_paths'][key]=[[100,v[1]] if v in [[104,270],[104,272]] else v for v in route]
 if 'samples' in data:
  for row in data['samples']:
   if any(a<row[0]+190<c and b<row[2]+260<d for a,b,c,d in plan['recess_rectangles']):row[1]=-.25
 room=data['furnishing']['rooms']['A1']
 room['route']=[[100,v[1]] if v in [[104,270],[104,272]] else v for v in room['route']]
 room['optional']=room['optional'][:1]+reg['optional_routes']
 for r in room['rooms']:
  if r[0]=='F02-04':r[1]='Registration operations';r[4]=[104,288]
 for d in room['doors']:
  if d[0]=='Staff bay':d.append(3.0)
  if d[0]=='Lounge':d[0]='Back office'
 file.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
report={'source_sha256':BASE,'output_sha256':digest(MAP),'unchanged_original_brushes':preserved,'replaced_floor_brushes':1,'added_brushes':len(brushes)-preserved,'brushes':len(brushes),'revision':'08','original_registration_sha256':digest(SNAP/'registration.tscn')}
(P/'.godot/freight_f03_apply.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
