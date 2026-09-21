"""One-time Registration colour assignments. Shape, UV axes and gameplay stay fixed."""
from pathlib import Path
import re,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'RedBreach';MAP=P/'maps/freight_01.map'
BASE='6f031b110d945367f216e9b1a4ee4719a66ba0950083c63740005d37978f7586'
assert hashlib.sha256(MAP.read_bytes()).hexdigest()==BASE,'Source changed; review before applying this one-time palette.'
SNAP=P/'.godot/registration_before_palette'
assert not SNAP.exists(),'Palette already applied or checkpoint exists; inspect before retrying.'
SNAP.mkdir();shutil.copy2(MAP,SNAP/'freight_01.map')
for f in ['missions/freight/freight_blockout.tscn','missions/freight/registration_f02.tscn','missions/freight/layout.json']:
 dst=SNAP/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/f,dst)
old=MAP.read_text();pattern=r'(?m)^// [^\n]*\n\{\n(?:\(.*\n)+\}';raws=re.findall(pattern,old)
assert len(raws)==1211
point_re=r'\( ([^()]*) \)'
def bounds(raw):
 pts=[tuple(map(float,v.split())) for v in re.findall(point_re,raw)]
 return [min(v[1] for v in pts)/32+190,min(v[2] for v in pts)/32,min(v[0] for v in pts)/32+260],[max(v[1] for v in pts)/32+190,max(v[2] for v in pts)/32,max(v[0] for v in pts)/32+260]
def part(raw,xlo,xhi,suffix):
 lo,hi=bounds(raw)
 def point(m):
  v=list(map(float,m[1].split()));x=v[1]/32+190
  assert abs(x-lo[0])<1e-6 or abs(x-hi[0])<1e-6
  v[1]=((xlo if abs(x-lo[0])<1e-6 else xhi)-190)*32
  return '( '+' '.join(f'{n:g}' for n in v)+' )'
 return re.sub(point_re,point,raw).replace(raw.splitlines()[0],raw.splitlines()[0]+' / '+suffix,1)
def material(line,texture):return re.sub(r'greybox/[^\s]+',texture,line,count=1)
WALL='greybox/MutedGreen/texture_01';CEILING='greybox/GreyPale/texture_01';STRUCTURE='greybox/GreyMedium/texture_03';WALK='greybox/MutedOrange/texture_06'
split_names={'// wall','// wall / outside F01','// F01 ceiling 4','// F01 ceiling bulkhead'}
result=[];split_count=0;painted_faces=0;unchanged=0
for raw in raws:
 lo,hi=bounds(raw);name=raw.splitlines()[0]
 split=(name in split_names and lo[0]<96.125<hi[0] and lo[2]>=261.5 and hi[2]<=294.5 and ((lo[2]<=262<=hi[2]) or (lo[2]<=294<=hi[2]) or name=='// F01 ceiling 4'))
 parts=[raw]
 if split:
  parts=[part(raw,lo[0],96.125,'neighbour'),part(raw,96.125,hi[0],'registration')];split_count+=1
  a,A=bounds(parts[0]);b,B=bounds(parts[1]);assert A[0]==b[0] and a==lo and B==hi
 for piece in parts:
  lo,hi=bounds(piece);lines=piece.splitlines();changed=False
  for i,line in enumerate(lines):
   if not line.startswith('('):continue
   pts=[list(map(float,m.split())) for m in re.findall(point_re,line)]
   pts=[[v[1]/32+190,v[2]/32,v[0]/32+260] for v in pts]
   axes=[a for a in range(3) if max(v[a] for v in pts)-min(v[a] for v in pts)<1e-6];assert len(axes)==1
   axis=axes[0];plane=pts[0][axis];texture=None
   if name.startswith('// F02 partition') or name.startswith('// F02 header') or name.startswith('// F03 staff door infill'):texture=WALL
   elif name.startswith('// F02 U') or name.startswith('// F02 B'):texture=STRUCTURE
   elif name=='// F03 lower floor support' and axis==1 and plane==-.25:texture=WALK
   elif name.startswith('// F03 raised floor') and axis!=1:
    # Only edge planes adjoining the recess; all upward floor faces retain Dark/06.
    if (axis==0 and plane in [98.5,101.5,104,107.5,113]) or (axis==2 and plane in [268.5,271.5,278.5,281.5,288.5,291.5]):texture='greybox/MutedOrange/texture_03'
   elif lo[0]>=96.125 and lo[2]>=261.5 and hi[2]<=294.5:
    if name in ['// F01 ceiling 4','// F01 ceiling bulkhead'] and axis==1 and plane==3.5:texture=CEILING
    elif name.startswith('// wall') and ((axis==2 and plane in [262,294]) or (axis==0 and plane==114)):texture=WALL
   if name in ['// A1 F01 partition','// A1 F01 header Reception / screening'] and axis==0 and abs(plane-96.125)<.0001:texture=WALL
   if name=='// A1 F01 frame' and hi[0]>96 and axis==0 and abs(plane-hi[0])<.0001:texture=STRUCTURE
   if texture:
    lines[i]=material(line,texture);changed|=lines[i]!=line;painted_faces+=lines[i]!=line
  result.append('\n'.join(lines))
  if not changed and not split:unchanged+=1
# Every unsplit plane/axis/shift/scale is identical; only the texture token changes.
def without_material(s):return re.sub(r'greybox/[^\s]+','TEXTURE',s)
idx=0
for raw in raws:
 lo,hi=bounds(raw);name=raw.splitlines()[0]
 if result[idx].splitlines()[0].endswith('/ neighbour'):
  assert without_material(result[idx])==without_material(part(raw,lo[0],96.125,'neighbour'))
  assert without_material(result[idx+1])==without_material(part(raw,96.125,hi[0],'registration'));idx+=2
 else:assert without_material(raw)==without_material(result[idx]);idx+=1
MAP.write_text(old[:old.index('// floor')]+'\n'.join(result)+'\n}\n',encoding='utf-8')
material_dir=P/'props/blockout/materials';material_dir.mkdir(exist_ok=True)
roles={'registration_block':'MutedPurple/texture_01','registration_surface':'GreyMedium/texture_03','registration_service':'GreyMedium/texture_01','registration_fixture':'GreyCharcoal/texture_01'}
for name,texture in roles.items():
 assert (P/'textures/greybox'/f'{texture}.png').exists()
 path=material_dir/f'{name}.tres';assert not path.exists()
 path.write_text('[gd_resource type="StandardMaterial3D" format=3]\n\n[ext_resource type="Texture2D" path="res://textures/greybox/'+texture+'.png" id="1_texture"]\n\n[resource]\nalbedo_texture = ExtResource("1_texture")\nroughness = 0.85\nuv1_triplanar = true\nuv1_scale = Vector3(1, 1, 1)\ntexture_filter = 2\n',encoding='utf-8')
placement=(P/'missions/freight/registration_f02.tscn').read_text()
refs=set(re.findall(r'path="(res://props/blockout/f0[23]/[^\"]+\.tscn)"',placement))
prop_changes=[]
for resource in sorted(refs):
 file=P/resource.removeprefix('res://');source=file.read_text();dest=SNAP/resource.removeprefix('res://');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest)
 role='registration_block'
 if 'service_trunk' in file.name:role='registration_service'
 if file.name.startswith('light_housing'):role='registration_fixture'
 edited=source.replace('res://props/blockout/f02/dark.tres','res://props/blockout/materials/'+role+'.tres').replace('res://props/blockout/f02/panel.tres','res://props/blockout/materials/registration_surface.tres')
 # Only resource paths change: meshes, collision, lights and placement are untouched.
 assert re.sub(r'res://props/blockout/(?:f02|materials)/[^\"]+\.tres','MATERIAL',source)==re.sub(r'res://props/blockout/(?:f02|materials)/[^\"]+\.tres','MATERIAL',edited)
 file.write_text(edited,encoding='utf-8');prop_changes.append(resource)
report={'scope':'A1 registration, waiting, staff and back office','material_revision':'registration_palette_01','geometry_revision':'08','source_sha256':BASE,'output_sha256':hashlib.sha256(MAP.read_bytes()).hexdigest(),'brushes_before':len(raws),'brushes_after':len(result),'material_boundary_splits':split_count,'painted_faces':painted_faces,'unchanged_brushes':unchanged,'prop_assets_recoloured':len(prop_changes),'palette':{'raised_floor':'Dark/texture_06 (unchanged)','walls':'MutedGreen/texture_01','ceiling':'GreyPale/texture_01','walkway':'MutedOrange/texture_06','step_edges':'MutedOrange/texture_03','props':'MutedPurple/texture_01','tops_panels_structure':'GreyMedium/texture_03','overhead_services':'GreyMedium/texture_01','fixture_housings':'GreyCharcoal/texture_01'},'notes':['Shared shell/ceiling brushes divided at the existing room boundary for local materials; occupied geometry and UV scale unchanged.','Original PNGs, floor surfaces, lights, screens and gameplay unchanged.']}
for file in [P/'missions/freight/layout.json',ROOT/'docs/freight-blockout-layout.json']:
 data=json.loads(file.read_text());data['brushes']=len(result);data['registration_palette']=report;file.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
(ROOT/'docs/freight-registration-palette.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(P/'.godot/registration_palette_apply.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
