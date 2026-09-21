from pathlib import Path
import json, math, hashlib
from html import escape
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs'
C={'bg':'#111e29','panel':'#192c3b','ink':'#eef4f5','muted':'#acc1cd','wall':'#e9d0a0','room':'#263b47','office':'#314449','work':'#304048','upper':'#4e4169','route':'#81e1bd','prop':'#7595af','stair':'#ffc775','window':'#62cde6','dim':'#708896'}
S={
'A1':{'title':'STAFF INTAKE','bounds':[62,262,114,294],'scale':12,'floor':0,'entry':[114,270],'exit':[62,288],
'rooms':[
['01','Reception',[96.125,262,114,294],3.5,[104.5,283]],
['02','Screening',[82.125,262,95.875,275.875],3.5,[89,274.8]],
['03','Administration',[62,262,81.875,275.875],3.5,[72,264]],
['04','Staff preparation',[62,276.125,95.875,294],3.5,[83,291]]],
'walls':[[[96,262],[96,270]],[[96,274],[96,294]],[[82,262],[82,266]],[[82,270],[82,276]],[[62,276],[86,276]],[[90,276],[96,276]]],
'doors':[['Reception / screening',[96,272],'x'],['Office',[82,268],'x'],['Staff preparation',[88,276],'z']],
'route':[[114,270],[104,270],[104,272],[88,272],[88,282],[74,282],[74,288],[62,288]],
'optional':[[[88,272],[88,268],[76,268]]],
'props':[],
'notes':['A staffed intake sequence, with an optional office.','Four rooms; clear proportions range from 1.01 to 1.90.','All occupied ceilings: +3.5 m above the 0 m floor.','The east entry and southwest exit stay in place.','New partitions close old gaps; thresholds remain level.','One south-facing window bay tests a shallow Mars view.'],
'foot':'The 52 x 32 m shell remains. Internal openings are 4 m; shell openings remain 6 m.'},
'A2':{'title':'INSPECTION / WALL-SIDE DESCENT','bounds':[8,184,56,242],'scale':10.5,'floor':-2,'entry':[44,242],'exit':[20,184],
'rooms':[
['01','Circuit control',[8,184,31.875,205.875],3.5,[20,188]],
['02','Pump test room',[32.125,184,56,205.875],4.5,[44,202.5]],
['03','Staff preparation',[8,206.125,31.875,223.875],3.5,[20,209.5]],
['04','Kit store',[8,224.125,31.875,242],3.5,[20,239.5]],
['05','Inspection work floor',[32.125,206.125,56,232],4.5,[44,219]]],
'walls':[[[32,184],[32,214]],[[32,218],[32,242]],[[8,206],[18,206]],[[22,206],[42,206]],[[46,206],[56,206]],[[8,224],[18,224]],[[22,224],[32,224]]],
'doors':[['Preparation / control',[20,206],'z'],['Inspection / preparation',[32,216],'x'],['Pump test room',[44,206],'z'],['Kit store',[20,224],'z']],
'route':[[44,242],[44,236],[54,236],[54,230],[54,226],[54,223],[40,223],[40,216],[20,216],[20,184]],
'optional':[[[44,223],[44,194]],[[20,216],[20,231],[17.5,231]],[[20,200],[17.5,200]]],
'props':[],
'notes':['Entry remains at (44,242), floor 0 m. Exit stays -2 m.','I1 shifts to the east wall: (54,230) to (54,226).','4 m clear stair width; 0.25 m rise / 0.5 m tread.','Upper and lower landings each reserve 4 x 2 m.','A larger upper deck provides the viewing/turning space.','Selector (16,202) and Tr1 cache (16,228) stay reachable.'],
'foot':'Inspection gains a main 24 x 26 m working bay. The platform and stair are circulation, not extra rooms.'},
'A8':{'title':'ANNEX / SEPARATED DOORWAYS','bounds':[65,184,101,242],'scale':10.5,'floor':-2,'entry':[85,184],
'rooms':[
['01','Annex intake',[65,184,101,203.875],3.5,[82,190]],
['02','Tool workshop',[65,204.125,84.875,242],4.5,[75,220]],
['03','Service stores',[85.125,204.125,101,222.875],3.5,[93,211]],
['04','Spare assemblies',[85.125,223.125,101,242],3.5,[93,237.5]]],
'walls':[[[65,204],[73,204]],[[77,204],[91,204]],[[95,204],[101,204]],[[85,204],[85,212]],[[85,216],[85,231]],[[85,235],[85,242]],[[85,223],[101,223]]],
'doors':[['Workshop',[75,204],'z'],['Stores from intake',[93,204],'z'],['Stores from workshop',[85,214],'x'],['Spare assemblies',[85,233],'x']],
'route':[[85,184],[85,196],[75,196],[75,228]],
'optional':[[[85,196],[93,196],[93,214],[75,214]],[[75,228],[75,233],[94,233]]],
'props':[],
'notes':['The north connection stays at (85,184), floor -2 m.','Replace the existing short, offset divider fragments.','A continuous T-wall has doors set back from its junction.','Two north openings have 14 m of wall between them.','Storage doors sit away from intersecting wall corners.','All four rooms are optional; no new key or reward here.'],
'foot':'A8 remains a side branch. The stores loop reconnects within the annex; it bypasses no mission gate.'}}

def prop(area,kind,x,z,w,h,tag=''):
 S[area]['props'].append({'kind':kind,'bounds':[x,z,x+w,z+h],'label':tag})
def desk(area,x,z):
 prop(area,'desk',x,z,2,.9);prop(area,'chair',x+.65,z+1.3,.65,.65)
# Actual furnishing footprints, not symbolic room-filling rectangles.
prop('A1','counter',107,277,5,1.2,'COUNTER');prop('A1','chair',109,279.2,.65,.65)
prop('A1','bench',112.8,264,.65,4);prop('A1','bench',100,289,5,.7)
prop('A1','counter',84,264.5,3,1,'CHECK');prop('A1','chair',85.3,265.6,.65,.65)
prop('A1','scanner',91,266,2,3,'SCAN');prop('A1','locker',84,262.8,6,.75)
for x,z in [(65,266),(71,266),(65,271),(71,271)]:desk('A1',x,z)
prop('A1','cabinet',78,271,2,1);prop('A1','bench',67,279,5,.7);prop('A1','bench',80,288,5,.7)
prop('A1','counter',78,279,6,1.2,'KIT');prop('A1','locker',63,290,5,.8);prop('A1','locker',91,285,.8,6)
prop('A2','console',10,185,5,1.2,'CONTROL');desk('A2',24,191)
prop('A2','selector',14.6,201.5,2.8,1,'GMa / BcD / Tr1')
prop('A2','pump',36,188,4,3,'PUMP');prop('A2','pump',46,196,4,3,'PUMP');prop('A2','pipe',53.5,188,1.5,14)
prop('A2','locker',9,209,.8,11);prop('A2','bench',12,212,4,.7);prop('A2','bench',24,220,5,.7)
prop('A2','cache',15.4,227.5,1.2,1,'Tr1');prop('A2','rack',24,237,5,1);prop('A2','crates',10,235,3,3)
prop('A2','scanner',34,228.5,4,3,'SCAN');prop('A2','desk',35,209,3,.9);prop('A2','chair',36,210.3,.65,.65)
prop('A2','bench',48,213,2.4,.8);prop('A2','bench',33,237,2.4,.8)
prop('A8','bench',68,186,6,1);prop('A8','cabinet',98,187,1,10)
prop('A8','bench',67,211,4,1);prop('A8','bench',78,225,4,1);prop('A8','machine',68,235,2,3,'LATHE')
prop('A8','rack',78,238,5,1);prop('A8','rack',86.5,207,4,1.2);prop('A8','rack',96,216,1,4)
prop('A8','machine',89,228.5,4,2,'SPARES');prop('A8','crates',96,232,3,3)
S['A2']['deck']=[38,232,56,242,0]
S['A2']['ceiling_overrides']=[{'bounds':[32,206,56,242],'ceiling_y':2.5,'reason':'4.5 m clear above the -2 m inspection floor'}, {'bounds':[38,224,56,242],'ceiling_y':3.5,'reason':'3.5 m clear above the upper entry; carry this roof over the stair and lower landing'}]
S['A1']['window_candidate']={'wall':'south','span_x':[102,110],'z':294,'sill_y':1,'head_y':2.8,'type':'shallow non-traversable exterior view'}
S['A2']['stair']={'start':[54,230],'end':[54,226],'width':4,'floor_start':0,'floor_end':-2,'upper_landing':[52,230,56,232],'lower_landing':[52,224,56,226], 'approach_clear':[50,232,56,238]}
# Lower landing is 2 m deep immediately beyond the last tread; the approach lane
# continues north to z=223, leaving a full capsule-width turn beyond its edge.
checks=[]
for key,a in S.items():
 for prop_data in a['props']:
  prop_data['height_m']={'desk':.75,'chair':.9,'counter':1.1,'scanner':2.4,'locker':2.2,'bench':.45,'cabinet':2.1,'console':1.1,'selector':1.4,'pump':2.6,'pipe':3.4,'cache':1.6,'rack':2.3,'crates':1.2,'machine':1.7}[prop_data['kind']]
  prop_data['floor_y']=a['floor']
 for i,p in enumerate(a['props']):
  for q in a['props'][i+1:]:
   b,c=p['bounds'],q['bounds']
   assert not (min(b[2],c[2])-max(b[0],c[0])>1e-6 and min(b[3],c[3])-max(b[1],c[1])>1e-6),(key,'overlapping furniture',p,q)
 for id,name,b,ceiling,label in a['rooms']:
  w,h=b[2]-b[0],b[3]-b[1];ratio=max(w,h)/min(w,h)
  assert ratio<=2.0,(key,name,ratio)
 for d in a['doors']:
  _,(x,z),axis=d
  t=z if axis=='x' else x
  corners=[a['bounds'][1],a['bounds'][3]] if axis=='x' else [a['bounds'][0],a['bounds'][2]]
  for u,v in a['walls']:
   if axis=='x' and u[1]==v[1] and min(u[0],v[0])<=x<=max(u[0],v[0]):corners.append(u[1])
   if axis=='z' and u[0]==v[0] and min(u[1],v[1])<=z<=max(u[1],v[1]):corners.append(u[0])
  clear_return=min(abs(t-c)-2-.25-.125 for c in corners)
  assert clear_return>=1,(key,d,'wall return too small',clear_return)
  assert any((x==u[0]==v[0] if axis=='x' else z==u[1]==v[1]) for u,v in a['walls'])
 for route in [a['route']]+a['optional']:
  for u,v in zip(route,route[1:]):
   assert u[0]==v[0] or u[1]==v[1],(key,u,v)
   # A 3 m clear movement ribbon must pass between furniture and partitions.
   lo=[min(u[0],v[0])-1.5,min(u[1],v[1])-1.5];hi=[max(u[0],v[0])+1.5,max(u[1],v[1])+1.5]
   for p in a['props']:
    b=p['bounds']
    overlap=min(hi[0],b[2])-max(lo[0],b[0])>1e-6 and min(hi[1],b[3])-max(lo[1],b[1])>1e-6
    assert not overlap,(key,'route vs prop',u,v,p)
   for wa,wb in a['walls']:
    b=[min(wa[0],wb[0])-.125,min(wa[1],wb[1])-.125,max(wa[0],wb[0])+.125,max(wa[1],wb[1])+.125]
    overlap=min(hi[0],b[2])-max(lo[0],b[0])>1e-6 and min(hi[1],b[3])-max(lo[1],b[1])>1e-6
    assert not overlap,(key,'route vs wall',u,v,wa,wb)
 for p in a['props']:
  b=p['bounds'];r=a['bounds'];assert r[0]<=b[0]<b[2]<=r[2] and r[1]<=b[1]<b[3]<=r[3],(key,p)
 checks.append(key+': rooms within 2:1; 3 m route ribbons clear walls/props; door returns >=1 m; no overlapping furniture')

class Sheet:
 def __init__(self,title,subtitle):
  self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1120" viewBox="0 0 1600 1120"><title>{escape(title)}</title><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0L7 3.5L0 7Z" fill="{C["route"]}"/></marker></defs>',f'<rect width="1600" height="1120" fill="{C["bg"]}"/>','<g font-family="Segoe UI,Arial,sans-serif">']
  self.text(40,51,title,28,bold=True);self.text(40,84,subtitle,17,C['muted'])
 def text(self,x,y,t,size=16,color=None,bold=False,anchor='start'):
  self.s.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{color or C["ink"]}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(str(t))}</text>')
 def rect(self,x,y,w,h,fill,stroke='none',sw=1,opacity=1):
  self.s.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>')
 def line(self,pts,color,width=2,dash='',arrow=False):
  self.s.append('<polyline points="'+' '.join(f'{x:g},{y:g}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
 def circle(self,x,y,r,fill):self.s.append(f'<circle cx="{x:g}" cy="{y:g}" r="{r}" fill="{fill}"/>')
 def panel(self,x,y,w,h,title):
  self.rect(x,y,w,h,C['panel']);self.text(x+22,y+34,title,21,bold=True)
 def save(self,name):
  self.s.append('</g></svg>');(OUT/(name+'.svg')).write_text('\n'.join(self.s),encoding='utf-8')

class Plan:
 def __init__(self,s,a,ox,oy,scale):self.s=s;self.a=a;self.ox=ox;self.oy=oy;self.scale=scale;self.x0=a['bounds'][0];self.z0=a['bounds'][1]
 def p(self,x,z):return self.ox+(x-self.x0)*self.scale,self.oy+(z-self.z0)*self.scale
 def rect(self,b,fill,stroke='none',sw=1,opacity=1):
  x,z,X,Z=b;px,py=self.p(x,z);self.s.rect(px,py,(X-x)*self.scale,(Z-z)*self.scale,fill,stroke,sw,opacity)
 def line(self,pts,color,width=2,dash='',arrow=False):self.s.line([self.p(*p) for p in pts],color,width,dash,arrow)
 def label(self,x,z,txt,size=14,color=None,bold=False):self.s.text(*self.p(x,z),txt,size,color,bold,'middle')
 def draw(self,key):
  a=self.a;b=a['bounds'];self.rect(b,C['room'],C['wall'],5)
  for id,name,bounds,ceil,pos in a['rooms']:self.rect(bounds,C['office'] if ceil==3.5 else C['work'])
  if key=='A2':
   self.rect([32.125,232,38,242],C['work']);self.rect(a['deck'][:4],C['upper'])
   st=a['stair'];self.rect(st['upper_landing'],C['upper']);self.rect(st['lower_landing'],'#515249')
   self.rect([52,226,56,230],'#665638')
   for i in range(9):self.line([[52,226+i*.5],[56,226+i*.5]],C['stair'],2)
   self.line([[38,232],[52,232]],'#c6a4f5',3,'6 4')
   self.line([[52,226],[52,230]],'#c6a4f5',3,'6 4')
   self.label(45,239,'ENTRY DECK  /  0 m',13,'#e3cbff',True)
   self.label(42,233.6,'OPEN GUARD / VIEW DOWN',10,'#e3cbff')
   self.line([[47,235],[40,223]],C['window'],2,'4 4')
   ex,ey=self.p(47,235);self.s.circle(ex,ey,4,C['window'])
  # Grid stays subtle and provides a five-metre scale reference.
  for x in range(math.ceil(self.x0/5)*5,int(b[2]),5):self.line([[x,b[1]],[x,b[3]]],'#3a4e5a',.6)
  for z in range(math.ceil(self.z0/5)*5,int(b[3]),5):self.line([[b[0],z],[b[2],z]],'#3a4e5a',.6)
  for u,v in a['walls']:self.line([u,v],C['wall'],max(3,.25*self.scale))
  # Open thresholds erase only the shell segment; no new door leaves or locks.
  for label,pt in [('ENTRY',a['entry'])]+([('EXIT',a['exit'])] if 'exit' in a else []):
   x,z=pt
   horizontal=z in (b[1],b[3])
   pts=[[x-3,z],[x+3,z]] if horizontal else [[x,z-3],[x,z+3]]
   self.line(pts,C['room'],7);self.line(pts,C['route'],2)
   px,py=self.p(x,z)
   if horizontal:self.s.text(px,py+(-14 if z==b[1] else 28),label,14,C['route'],True,'middle')
   else:self.s.text(px+(10 if x==b[2] else -10),py-11,label,14,C['route'],True,'start' if x==b[2] else 'end')
  for route in a['optional']:self.line(route,C['route'],2,'6 5',True)
  self.line(a['route'],C['route'],3,arrow=True)
  for p in a['props']:
   b=p['bounds'];kind=p['kind'];color=C['stair'] if kind in ['selector','cache'] else C['prop']
   if kind=='chair':
    x,z,X,Z=b;px,py=self.p((x+X)/2,(z+Z)/2);self.s.circle(px,py,(X-x)*self.scale/2,color)
   else:
    self.rect(b,color,'#c0d1db',.8,.88)
    mark={'desk':'D','counter':'C','scanner':'S','locker':'L','pump':'P','pipe':'V','console':'C','bench':'B','cabinet':'R','cache':'Tr1','selector':'SEL','rack':'R','crates':'BOX','machine':'M'}[kind]
    self.label((b[0]+b[2])/2,(b[1]+b[3])/2+.22,mark,9,C['bg'],True)
  for id,name,bounds,ceil,pos in a['rooms']:
   text=id+' / '+name.upper();px,py=self.p(*pos);width=len(text)*7.0+10
   self.s.rect(px-width/2,py-14,width,20,C['room'],opacity=.92)
   self.label(*pos,text,13,C['ink'],True)
  if key=='A1':
   self.line([[102,294],[110,294]],C['window'],6);self.label(106,297,'MARS VIEW BAY',12,C['window'])
  # North arrow and 10 metre scale.
  self.s.text(self.ox-42,self.oy-18,'N',15,C['ink'],True,'middle');self.s.line([(self.ox-42,self.oy+23),(self.ox-42,self.oy-6)],C['ink'],2)
  self.s.line([(self.ox-47,self.oy+2),(self.ox-42,self.oy-6),(self.ox-37,self.oy+2)],C['ink'],2)
  yy=self.oy+(a['bounds'][3]-a['bounds'][1])*self.scale+60
  self.s.line([(self.ox,yy),(self.ox+10*self.scale,yy)],C['ink'],3);self.s.text(self.ox,yy+24,'10 m / grid = 5 m',13,C['muted'])

def schedule(s,a,y):
 s.text(840,y,'ROOMS / CLEAR USABLE DIMENSIONS',19,bold=True)
 s.text(840,y+29,'Space',14,C['muted']);s.text(1095,y+29,'Approx. m',14,C['muted']);s.text(1243,y+29,'Ratio',14,C['muted']);s.text(1364,y+29,'Clear height',14,C['muted'])
 for i,(id,name,b,ceil,pos) in enumerate(a['rooms']):
  yy=y+62+i*35;w,h=b[2]-b[0],b[3]-b[1]
  s.text(840,yy,id+'  '+name,15);s.text(1095,yy,f'{w:.1f} x {h:.1f}',15);s.text(1243,yy,f'{max(w,h)/min(w,h):.2f}:1',15,C['route']);s.text(1380,yy,f'{ceil:g} m',15)
 s.text(840,y+72+len(a['rooms'])*35,'Dimensions allow for 0.25 m internal partitions.',13,C['muted'])

def section_a2(s):
 s.panel(810,128,750,410,'A2 / ENTRY, VIEW AND DESCENT (N-S SECTION)')
 def p(z,y):return 855+(242-z)*22,390-y*30
 floor=[[242,0],[230,0]]
 for i in range(1,9):floor.extend([[230-(i-1)*.5,-i*.25],[230-i*.5,-i*.25]])
 floor.append([216,-2]);s.line([p(z,y) for z,y in floor],C['stair'],3)
 s.line([p(242,3.5),p(224,3.5),p(224,2.5),p(216,2.5)],C['wall'],4)
 for z in [242,232,230,226,224,216]:
  px,_=p(z,0);s.text(px,495,str(z),12,C['muted'],anchor='middle')
 s.text(855,516,'Plan Z (m)  /  vertical scale enlarged for readability',12,C['muted'])
 for z1,z2,y,text in [(242,232,0,'UPPER DECK'),(232,230,0,'2 m'),(226,224,-2,'2 m'),(224,216,-2,'LOWER FLOOR')]:
  x,y0=p((z1+z2)/2,y);s.text(x,y0+25,text,12,C['muted'],anchor='middle')
 x,y=p(236,1.65);s.circle(x,y,6,C['window']);s.line([p(236,1.65),p(218,-2)],C['window'],2,'6 5');s.text(x-34,y-18,'EYE',12,C['window'])
 s.line([p(232,0),p(232,1.2)],'#c6a4f5',2,'3 3');s.text(1020,330,'SIDE GUARD (PROJECTED)',11,'#dcc0ff')
 s.text(880,248,'3.5 m clear above the upper entry',15,C['muted']);s.text(1170,274,'4.5 m over the work floor',15,C['muted'])
 s.text(840,190,'The landing reveals the receiving floor before the first downward step.',15,C['ink'])
 s.text(840,216,'The side guard is projected here; the stair approach stays clear. Verify in the player camera.',13,C['muted'])

for key,a in S.items():
 s=Sheet('RED BREACH / '+key+' '+a['title'],'BUILT SAMPLE F-01 / LAYOUT 06  |  Reviewed spatial plan  |  Clear routes + measured furniture')
 s.panel(35,128,745,884,'TOP DOWN / '+('FLOOR 0 m' if key=='A1' else 'FLOOR -2 m'))
 ox=108 if key=='A1' else 143 if key=='A2' else 205;oy=255 if key=='A1' else 222
 plan=Plan(s,a,ox,oy,a['scale']);plan.draw(key)
 s.text(58,929,'D desks   C counters/consoles   P pumps   S inspection equipment',13,C['muted'])
 s.text(58,953,'B benches   L lockers   R racks/cabinets   M machinery   dots: chairs',13,C['muted'])
 s.text(58,984,'Mint: suggested walk / dashed: optional access. Reserve 3 m wide travel lanes.',13,C['route'])
 if key=='A2':
  section_a2(s);schedule(s,a,590);ny=888
 else:
  s.panel(810,128,750,884,'ROOM FUNCTION AND ARCHITECTURE')
  schedule(s,a,204);ny=495
 for i,line in enumerate(a['notes']):s.text(840,ny+i*29,line,15,C['muted'])
 if key=='A1':
  s.text(840,713,'WHAT CHANGES',19,bold=True)
  for i,t in enumerate(['Lower the 8 m room ceiling to a 3.5 m occupied ceiling.','Use a screening room and a compact optional office.','Counter, workstations, lockers and benches define the jobs.','Internal doors are separated from wall junctions.','The sealed exterior window has a shallow Mars-view prototype.']):s.text(840,748+i*31,t,15,C['muted'])
  s.text(840,943,'Openings remain open in the furnishing blockout.',16,C['ink']);s.text(840,971,'Automatic pressure-door behavior is a later pass.',15,C['muted'])
 if key=='A8':
  s.text(840,713,'JUNCTION CHANGE',19,bold=True)
  # Schematic enlargement showing two spaced openings and the solid T junction.
  xx=855;yy=770
  s.line([(xx,yy),(xx+70,yy)],C['wall'],6);s.line([(xx+125,yy),(xx+395,yy)],C['wall'],6);s.line([(xx+450,yy),(xx+590,yy)],C['wall'],6)
  s.line([(xx+270,yy),(xx+270,yy+75)],C['wall'],6)
  s.text(xx+98,yy-15,'4 m',14,C['route'],anchor='middle');s.text(xx+423,yy-15,'4 m',14,C['route'],anchor='middle')
  s.text(xx+270,yy+104,'Solid wall at the junction; doors are set back on each side.',14,C['muted'],anchor='middle')
  s.text(840,946,'Workshop clear height: 4.5 m. Intake and stores: 3.5 m.',15,C['ink'])
  s.text(840,974,'No extra quest item, encounter or required detour added.',15,C['muted'])
 s.text(40,1060,a['foot'],16,C['ink'])
 s.text(40,1094,'Built in layout 06. Kenney metric greybox props; walkthrough and progression checks passed.',14,C['muted'])
 s.save('freight-furnishing-'+key.lower()+'-plan')

meta={'status':'BUILT - USER APPROVED F-01 / LAYOUT 06','revision':'F-01','baseline_layout':'05','built_layout':'06','rooms':S,'checks':checks,'partition_definition':'Wall centreline segments have butt ends at opening edges; thickness extends only perpendicular to each segment.','internal_partition_thickness_m':.25,'internal_opening_width_m':4,'internal_clear_opening_height_m':3.2,'reserved_frame_side_width_m':.25,'reserved_route_width_m':3,'shell_opening_width_m':6,'scope':'A1, A2 and A8 only; mission dependencies and exterior corridor connections retained','notes':['No final enemy or pickup distribution in this drawing.','Only A2 I1 moved; other stairs remain unchanged.','A2 upper deck and stair need the higher ceiling envelope shown in section.','Clear-height transitions must include closed bulkheads and correct stair headroom.','Paper checks do not establish collision, navigation or camera visibility.']}
(OUT/'freight-furnishing-plan.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checks':checks,'outputs':['freight-furnishing-'+k.lower()+'-plan.svg' for k in S],'room_count':sum(len(a['rooms']) for a in S.values()),'furniture_count':sum(len(a['props']) for a in S.values())},indent=2))
