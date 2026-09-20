"""Bootstrap the reviewed freight blockout. The resulting .map is the editable source.
Run with --overwrite only to deliberately regenerate; normal rebuilds never run this.
"""
from pathlib import Path
import json, math, sys
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'RedBreach'
MAP=P/'maps/freight_01.map'
if MAP.exists() and '--overwrite' not in sys.argv:raise SystemExit('Map already exists. Edit it in TrenchBroom, or explicitly pass --overwrite to regenerate.')
m=json.loads((ROOT/'docs/freight-blockout-layout.json').read_text())
rooms=m['rooms'];edges=m['edges'];heights=m['floor_heights'];stairs=m['stair_flights']
# Half-metre plan cells merge into ordinary rectangular Valve 220 brushes.
cells={};ceilings={}
def paint(x0,z0,x1,z1,y,ceiling=None):
 for ix in range(round(x0*2),round(x1*2)):
  for iz in range(round(z0*2),round(z1*2)):
   cells[ix,iz]=y
   ceilings[ix,iz]=max(ceilings.get((ix,iz),-100),ceiling if ceiling is not None else y+4.5)
for k,(x,z,w,h,_,_) in rooms.items():
 y=heights[k]; ceiling=10 if k=='B4' else y+(4 if k in ('IN','OUT','M') else 8)
 paint(x-w/2,z-h/2,x+w/2,z+h/2,y,ceiling)
for mezz in m['mezzanines']:paint(*mezz['bounds'],mezz['floor'],heights[mezz['room']]+8)
def chain(point,e):
 d=0
 for a,b in zip(e['points'],e['points'][1:]):
  if min(a[0],b[0])<=point[0]<=max(a[0],b[0]) and min(a[1],b[1])<=point[1]<=max(a[1],b[1]):return d+abs(point[0]-a[0])+abs(point[1]-a[1])
  d+=abs(b[0]-a[0])+abs(b[1]-a[1])
 raise ValueError(point)
def level(d,e):
 y=heights[e['a']]
 for _,a,b,st,en,ya,yb in stairs:
  if (a,b)!=(e['a'],e['b']):continue
  ds=chain(st,e);de=chain(en,e)
  if d>=de:y=yb
  elif d>=ds:return ya+math.copysign(.25*min(8,math.floor((d-ds)/.5)+1),yb-ya)
 return y
for e in edges:
 if e['kind']=='optional':continue
 d=0;r=e['width']/2
 for a,b in zip(e['points'],e['points'][1:]):
  n=abs(b[0]-a[0])+abs(b[1]-a[1]);dx=0 if a[0]==b[0] else (1 if b[0]>a[0] else -1);dz=0 if a[1]==b[1] else (1 if b[1]>a[1] else -1)
  for ix in range(round((min(a[0],b[0])-r)*2),round((max(a[0],b[0])+r)*2)):
   for iz in range(round((min(a[1],b[1])-r)*2),round((max(a[1],b[1])+r)*2)):
    x=(ix+.5)/2;z=(iz+.5)/2
    # End caps join bends and room centres. Their floor follows the adjacent segment.
    t=max(0,min(n,(x-a[0])*dx+(z-a[1])*dz));y=level(d+t,e)
    cells[ix,iz]=y;ceilings[ix,iz]=max(ceilings.get((ix,iz),-100),max(heights[e['a']],heights[e['b']])+4.5)
  d+=n
# The bridges join upper openings in the room walls. Internal platforms remain slabs.
paint(154,60,167,64,6,10)
paint(201,50,214,54,6,10)
brushes=[];boxes=[]
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def box(lo,hi,texture,name):
 if any(b-a<=0 for a,b in zip(lo,hi)):raise ValueError((lo,hi,name))
 # Input remains in the paper frame; actual Godot origin is the hub.
 x,y,z=lo;X,Y,Z=hi;x-=190;X-=190;z-=260;Z-=260
 points=[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)]
 pts=[(p[2]*32,p[0]*32,p[1]*32) for p in points];center=tuple(sum(p[i] for p in pts)/8 for i in range(3))
 lines=['// '+name,'{']
 for face in [(0,1,2),(4,7,6),(0,4,5),(3,2,6),(0,3,7),(1,5,6)]:
  a,b,c=[pts[i] for i in face[:3]];n=cross(sub(b,a),sub(c,a))
  if dot(n,sub(a,center))>0:b,c=c,b
  axis=max(range(3),key=lambda i:abs(n[i]))
  uv=['[ 0 1 0 0 ] [ 0 0 -1 0 ]','[ 1 0 0 0 ] [ 0 0 -1 0 ]','[ 1 0 0 0 ] [ 0 -1 0 0 ]'][axis]
  tex=texture if axis==2 else ('greybox/Dark/texture_01' if texture=='greybox/Dark/texture_06' else texture)
  lines.append(' '.join('( '+' '.join(f'{v:g}' for v in p)+' )' for p in (a,b,c))+f' {tex} {uv} 0 0.03125 0.03125')
 lines.append('}');brushes.append('\n'.join(lines));boxes.append({'lo':[x,y,z],'hi':[X,Y,Z],'name':name})
def merge_grid(data):
 pending=dict(data)
 while pending:
  ix,iz=min(pending);v=pending[ix,iz];ex=ix+1
  while pending.get((ex,iz))==v:ex+=1
  ez=iz+1
  while all(pending.get((xx,ez))==v for xx in range(ix,ex)):ez+=1
  for xx in range(ix,ex):
   for zz in range(iz,ez):del pending[xx,zz]
  yield ix/2,iz/2,ex/2,ez/2,v
for i,(x0,z0,x1,z1,y) in enumerate(merge_grid(cells)):
 box((x0,-4,z0),(x1,y,z1),'greybox/Dark/texture_06',f'floor {i} / Y {y:g}')
for i,(x0,z0,x1,z1,y) in enumerate(merge_grid(ceilings)):
 box((x0,y,z0),(x1,y+.25,z1),'greybox/Dark/texture_01',f'ceiling {i}')
# Outer shell is the boundary of the connected room/corridor footprint.
segments={}
for (ix,iz),floor in cells.items():
 for dx,dz,axis,line,start in [(-1,0,'x',ix/2,iz/2),(1,0,'x',(ix+1)/2,iz/2),(0,-1,'z',iz/2,ix/2),(0,1,'z',(iz+1)/2,ix/2)]:
  if (ix+dx,iz+dz) not in cells:
   key=(axis,line,dx or dz,ceilings[ix,iz]);segments.setdefault(key,[]).append(start)
for (axis,line,sign,top),values in segments.items():
 values=sorted(values);lo=prev=values[0]
 for v in values[1:]+[None]:
  if v is not None and abs(v-prev-.5)<.001:prev=v;continue
  a,b=lo,prev+.5
  crosslo,crosshi=(line-.5,line) if sign<0 else (line,line+.5)
  if axis=='x':box((crosslo,-4,a),(crosshi,top+.25,b),'greybox/Dark/texture_01','wall')
  else:box((a,-4,crosslo),(b,top+.25,crosshi),'greybox/Dark/texture_01','wall')
  if v is not None:lo=prev=v
# Close vertical bulkheads wherever a tall room meets a lower corridor ceiling.
# Without these, the upper gap would look out above the corridor roof into the void.
ceiling_edges={}
for (ix,iz),y in ceilings.items():
 for dx,dz,axis,line,start in [(1,0,'x',(ix+1)/2,iz/2),(0,1,'z',(iz+1)/2,ix/2)]:
  other=ceilings.get((ix+dx,iz+dz))
  if other is not None and other!=y:
   ceiling_edges.setdefault((axis,line,min(y,other),max(y,other)),[]).append(start)
for (axis,line,bottom,top),values in ceiling_edges.items():
 values=sorted(values);lo=prev=values[0]
 for value in values[1:]+[None]:
  if value is not None and abs(value-prev-.5)<.001:prev=value;continue
  a,b=lo,prev+.5
  if axis=='x':box((line-.125,bottom,a),(line+.125,top+.25,b),'greybox/Dark/texture_01','ceiling bulkhead')
  else:box((a,bottom,line-.125),(b,top+.25,line+.125),'greybox/Dark/texture_01','ceiling bulkhead')
  if value is not None:lo=prev=value

# Raised ledges: solid low plinths on the 2 m mezzanines, and a true overhead B4 deck.
for name,x0,z0,x1,z1,y in [('Ladder landing',149,60,154,64,6),('Generator mezzanine',214,47,227,57,6)]:
 box((x0,y-.25,z0),(x1,y,z1),'greybox/Dark/texture_06',name)
# Fixed three-flight stair from the Generator mezzanine.
for name,a,b,st,en,ya,yb in stairs:
 if a!='M':continue
 for i in range(8):
  x=st[0]+i*.5;level_y=ya-(i+1)*.25
  if level_y>0:box((x,0,50),(x+.5,level_y,54),'greybox/Orange/texture_01',name+' step '+str(i+1))
 for x0,x1,yy in [(225,227,6),(231,233,4),(237,239,2)]:
  if name=='T11a':box((x0,0,50),(x1,yy,54),'greybox/Dark/texture_06','Generator stair landing')
# High solid guards on overhead deck edges protect route gates from unintended jumps.
for lo,hi in [((149,6,59.8),(154,7.4,60)),((149,6,64),(154,7.4,64.2)),((148.8,6,60),(149,7.4,61)),((148.8,6,63),(149,7.4,64)),((214,6,46.8),(227,7.4,47)),((214,6,57),(227,7.4,57.2)),((227,6,47),(227.2,7.4,50)),((227,6,54),(227.2,7.4,57))]:box(lo,hi,'greybox/Dark/texture_01','mezzanine guard')
# Mezzanine front guards leave a six-metre stair opening. Low platforms are solid below.
for mz in m['mezzanines']:
 x0,z0,x1,z1=mz['bounds'];y=mz['floor'];cx=32 if mz['room']=='A2' else (133 if mz['room']=='A6' else 342)
 z=z0 if mz['room']=='A2' else z1
 for xa,xb in [(x0,cx-3),(cx+3,x1)]:
  if xb>xa:box((xa,y,z-.1),(xb,y+1.25,z+.1),'greybox/Dark/texture_01',mz['room']+' mezzanine guard')
 for x in (x0,x1):box((x-.1,y,z0),(x+.1,y+1.25,z1),'greybox/Dark/texture_01',mz['room']+' side guard')
# Gate aperture frames are authored in the map; moving leaves are separate scene nodes.
gates=[('D1',52,147,0,False,6),('D2',109,128,0,True,6),('D4',287,125,0,True,6),('S1',176,237,0,False,6),('S2',204,237,0,False,6),('Lift',190,228,0,False,6),('Arrival',190,323.5,0,False,6),('BcD',166,62,6,True,4)]
for name,x,z,y,alongx,width in gates:
 def gatebox(u0,u1,v0,v1,h0,h1):
  lo=(x+v0,y+h0,z+u0) if alongx else (x+u0,y+h0,z+v0)
  hi=(x+v1,y+h1,z+u1) if alongx else (x+u1,y+h1,z+v1)
  box(lo,hi,'greybox/Orange/texture_01',name+' frame')
 for u0,u1 in [(-width/2,-1.5),(1.5,width/2)]:gatebox(u0,u1,-.25,.25,0,4)
 gatebox(-1.5,1.5,-.25,.25,3.2,ceilings.get((round(x*2),round(z*2)),y+4.5)-y)
MAP.write_text('// Game: Red Breach\n// Format: Valve\n{\n"classname" "worldspawn"\n"_tb_def" "builtin:FuncGodot.fgd"\n"_tb_textures" "greybox/Dark;greybox/Green;greybox/Orange;greybox/Purple;greybox/Red"\n'+'\n'.join(brushes)+'\n}\n',encoding='utf-8')
# QA itinerary samples actual floor heights, excluding the special upper bridge.
samples=[]
for e in edges:
 if e['kind']=='optional':continue
 d=0
 for a,b in zip(e['points'],e['points'][1:]):
  n=abs(b[0]-a[0])+abs(b[1]-a[1]);dx=(b[0]-a[0])/max(n,1);dz=(b[1]-a[1])/max(n,1)
  for i in range(math.ceil(n)):
   t=min(n,i+.5);x=a[0]+dx*t;z=a[1]+dz*t
   samples.append([x-190,level(d+t,e),z-260])
  d+=n
(P/'missions/freight/layout.json').write_text(json.dumps({'rooms':rooms,'heights':heights,'stairs':stairs,'gates':gates,'samples':samples,'revision':'04','edges':edges,'normal_route':m['normal_route'],'brushes':len(brushes),'origin':[190,260]},indent=2),encoding='utf-8')
(P/'.godot/freight_boxes.json').write_text(json.dumps(boxes),encoding='utf-8')
print(f'FREIGHT_MAP: {len(brushes)} brushes; {len(cells)} floor cells; {len(samples)} route samples')

