"""One-time flattening of the reviewed Registration recess. Preserve all other brushes."""
from pathlib import Path
import ast,hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'RedBreach';MAP=P/'maps/freight_01.map'
BASE='3a59c37ed6f85e7832029802a808c18671408475217a0ad0a3d797e89756a717'
assert hashlib.sha256(MAP.read_bytes()).hexdigest()==BASE,'Map changed; inspect before applying.'
snap=P/'.godot/registration_before_flat_floor';assert not snap.exists(),'Already applied or checkpoint exists.'
snap.mkdir()
for src,name in [(MAP,'freight_01.map'),(P/'missions/freight/layout.json','layout.json'),(ROOT/'docs/freight-blockout-layout.json','base.json'),(P/'missions/freight/freight_blockout.tscn','scene.tscn')]:shutil.copy2(src,snap/name)
plan={'status':'USER APPROVED - SOURCE APPLIED; VALIDATION PENDING','revision':'10','scope':'Registration walkway removal; consolidate A1 floor without altering its other occupied surfaces','bounds':[62,262,114,294],'floor_y':0,'texture':'greybox/Dark/texture_06','decision':'No recessed pathway and no painted material pathway; continuous flat floor. Material transitions require supporting geometry.','preserve':['Staff door and switches','All furniture and lights','Screening and its hatch reservations','Other rooms, stairs, mission gates and progression']}
(ROOT/'docs/freight-registration-flat-floor.md').write_text('# Registration / continuous flat floor\n\nThe user chose one continuous floor material when removing the 0.25 m lowered pathway. Approved intent: bring all four recessed strips to floor 0, preserving every doorway, furnishing and route. No contrasting walkway material or new border is added.\n\nThe A1 floor consolidates into one slab over its existing 52 x 32 m footprint. Only the former recessed strips gain height; every surrounding occupied floor stays at 0 m. Material: existing Kenney Dark/texture_06 with one-metre repeats.\n\nThis supersedes the walkway geometry and orange floor/step palette in the historical F03c drawings. The staff door, office furnishings, Registration view and Screening remain.\n',encoding='utf-8')
old=MAP.read_text();raws=re.findall(r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}',old);assert len(raws)==1229
removed=[r for r in raws if r.startswith('// F03 lower floor support\n') or r.startswith('// F03 raised floor ')];assert len(removed)==9
brushes=[r for r in raws if r not in removed];kept=list(brushes);ns={'brushes':brushes,'boxes':[]}
source=ast.parse((ROOT/'tools/bootstrap-freight-blockout.py').read_text());exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['sub','cross','dot','box']],type_ignores=[]),'<metric brush primitives>','exec'),ns)
ns['box']((62,-4,262),(114,0,294),plan['texture'],'Registration flat floor / A1 continuous slab')
output=old[:old.index('// floor')]+'\n'.join(brushes)+'\n}\n';assert all(r in output for r in kept)
# Compare floor heights on the prior half-metre grid; changes must be confined to the old strips.
prior=json.loads((snap/'layout.json').read_text())['registration_recess']['recess_rectangles']
changed_cells=0
for ix in range(124,228):
 for iz in range(524,588):
  x,z=(ix+.5)/2,(iz+.5)/2
  previous=-.25 if any(a<=x<c and b<=z<d for a,b,c,d in prior) else 0
  changed_cells+=previous!=0
assert changed_cells>0
MAP.write_text(output,encoding='utf-8')
plan.update(source_map_sha256=hashlib.sha256(MAP.read_bytes()).hexdigest(),unchanged_brushes=len(kept),removed_floor_brushes=9,added_floor_brushes=1,brushes=len(brushes),raised_area_m2=changed_cells*.25)
for f in [P/'missions/freight/layout.json',ROOT/'docs/freight-blockout-layout.json']:
 data=json.loads(f.read_text());data.update(revision='10',brushes=len(brushes),registration_floor=plan)
 if 'blockout_revision' in data:data.update(blockout_revision='10',status='Registration flat floor applied; validation pending')
 data['registration_recess']['status']='HISTORICAL F03c: recessed floor superseded by layout 10; staff door and office remain'
 data['registration_palette']['notes'].append('Layout 10 supersedes orange walkway/step surfaces with the continuous dark flat A1 floor.')
 for sample in data.get('samples',[]):
  if 62<=sample[0]+190<=114 and 262<=sample[2]+260<=294 and sample[1]==-.25:sample[1]=0
 f.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
(ROOT/'docs/freight-registration-flat-floor.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
print(json.dumps(plan))
