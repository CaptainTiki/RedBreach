"""One-time F-02 map application. Normal rebuilds never generate or replace source maps."""
from pathlib import Path
import ast,json,re,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'RedBreach';MAP=P/'maps/freight_01.map'
BASE='d52b1691839324628b713be998456d5393febba39741fdee319a1b89c899f446'
SNAP=P/'.godot/freight_before_f02';STATE=P/'.godot/freight_f02_apply.json'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if digest(MAP)!=BASE:
 if '--revise-generated' not in sys.argv or not STATE.exists() or digest(MAP)!=json.loads(STATE.read_text())['output_sha256']:raise SystemExit('Source changed; refusing to overwrite subsequent map edits.')
if not SNAP.exists():
 SNAP.mkdir()
 for source,name in [(MAP,'freight_01.map'),(P/'missions/freight/layout.json','layout.json'),(ROOT/'docs/freight-blockout-layout.json','base.json'),(P/'missions/freight/freight_blockout.tscn','scene.tscn')]:shutil.copy2(source,SNAP/name)
assert digest(SNAP/'freight_01.map')==BASE
plan=json.loads((ROOT/'docs/freight-registration-plan.json').read_text());plan.update(status='BUILT - APPROVED F-02 / LAYOUT 07',built_layout='07')
brushes=[];boxes=[];ns={'brushes':brushes,'boxes':boxes}
source=ast.parse((ROOT/'tools/bootstrap-freight-blockout.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ('sub','cross','dot','box')],type_ignores=[]),'<metric brush primitives>','exec'),ns);box=ns['box']
old=(SNAP/'freight_01.map').read_text();raws=re.findall(r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}',old)
assert len(raws)==1193
removed=[]
for raw in raws:
 name=raw.splitlines()[0][3:]
 if name in ['A1 F01 counter 0','A1 F01 bench 2','A1 F01 bench 3']:removed.append(raw)
 else:brushes.append(raw)
assert len(removed)==10,len(removed)
preserved=len(brushes)
for a,b in plan['walls']:
 x,z=min(a[0],b[0]),min(a[1],b[1]);X,Z=max(a[0],b[0]),max(a[1],b[1])
 if x==X:x-=.125;X+=.125
 else:z-=.125;Z+=.125
 box((x,0,z),(X,3.5,Z),'greybox/Dark/texture_01','F02 partition')
for x,z,axis in [(100,276,'z'),(106,280,'x'),(100,284,'z')]:
 if axis=='z':box((x-2,3.2,z-.125),(x+2,3.5,z+.125),'greybox/Dark/texture_01','F02 header')
 else:box((x-.125,3.2,z-2),(x+.125,3.5,z+2),'greybox/Dark/texture_01','F02 header')
for p in plan['floor_objects']+plan['overhead_objects']:
 if p['kind'] not in ['structural upright','beam']:continue
 x,z,X,Z=p['bounds'];lo=p.get('bottom',0);hi=p.get('top',p.get('height'))
 box((x,lo,z),(X,hi,Z),'greybox/Dark/texture_06','F02 '+p['id']+' '+p['kind'])
# Preserve every unaffected original brush literally, including texture axes.
assert brushes[:preserved]==[raw for raw in raws if raw not in removed]
MAP.write_text(old[:old.index('// floor')]+'\n'.join(brushes)+'\n}\n',encoding='utf-8')
layout=json.loads((SNAP/'layout.json').read_text());layout.update(revision='07',registration=plan,brushes=len(brushes))
# Replace only the superseded Reception check; the other three A1 rooms remain.
old_rooms=layout['furnishing']['rooms']['A1']['rooms']
points=[[104,269],[100,282],[110,281],[104,289]]
layout['furnishing']['rooms']['A1']['rooms']=[r for r in old_rooms if r[0]!='01']+[[f'F02-{r[0]}',r[1],r[2],3.5,point] for r,point in zip(plan['rooms'],points)]
layout['furnishing']['rooms']['A1']['doors'] += [['Waiting',[100,276],'z'],['Staff bay',[106,280],'x'],['Lounge',[100,284],'z']]
layout['furnishing']['rooms']['A1']['optional'] += plan['optional_routes']
layout['furnishing']['rooms']['A1']['props']=[p for i,p in enumerate(layout['furnishing']['rooms']['A1']['props']) if i not in [0,1,2,3]]
layout['furnishing']['status']='F01 baseline, superseded in Reception by registration F02'
(P/'missions/freight/layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf-8')
built=json.loads((SNAP/'base.json').read_text());built.update(revision='07',blockout_revision='07',registration=plan,brushes=len(brushes),status='BUILT - approved F02 reception; F01 elsewhere')
(ROOT/'docs/freight-blockout-layout.json').write_text(json.dumps(built,indent=2)+'\n',encoding='utf-8')
report={'source_sha256':BASE,'output_sha256':digest(MAP),'removed_reception_prop_brushes':len(removed),'unchanged_original_brushes':preserved,'added_architecture_brushes':len(brushes)-preserved,'brushes':len(brushes),'revision':'07'}
STATE.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
