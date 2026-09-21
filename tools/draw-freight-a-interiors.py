from pathlib import Path
from html import escape
import json, math, hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'
base=json.loads((OUT/'freight-blockout-layout.json').read_text())
rooms={k:v for k,v in base['rooms'].items() if k.startswith('A') or k in ('H','M')}
C={'bg':'#101d28','panel':'#172b39','ink':'#e1ebf0','muted':'#a6bdcc','grid':'#29404d','wall':'#e5cf9b','route':'#7bddc2','upper':'#c5a7ff','stair':'#ffce74','gate':'#ff9986','room':'#304039','void':'#11212c'}
# Proposed paper geometry. All coordinates use the existing plan frame (X,Z metres).
links={
'H-A1':[[190,260],[190,252],[132,252],[132,270],[114,270]],
'A1-A2':[[62,288],[44,288],[44,242]],
'A2-J0':[[20,184],[20,172],[52,172],[52,164]],
'blocked-D1':[[52,164],[52,146]],
'bypass':[[52,164],[85,164],[97,164],[97,128]],
'annex':[[85,164],[85,184]],
'JA-A3':[[97,128],[90,128],[90,136],[84,136]],
'JA-A4':[[97,128],[121,128],[121,101],[101,101],[101,93]],
'A3-A7':[[35,110],[35,98],[49,98],[49,81]],
'A4-A5':[[143,93],[143,102],[151,102],[151,114]],
'A5-A6':[[132,144],[132,154],[120,154],[120,166]],
'A6-H':[[156,190],[176,190],[176,260],[190,260]],
'BcD':[[148.4,62],[166,62],[184,62],[184,52]],
}
paths={
'A1':[[114,270],[104,270],[104,282],[90,282],[90,288],[62,288]],
'A2':[[44,242],[44,224],[26,224],[26,204],[20,204],[20,184]],
'A3-low':[[84,136],[72,136],[72,142],[54,142],[54,132],[58,132],[58,128]],
'A3-up':[[58,118],[58,116],[35,116],[35,110]],
'A7':[[49,81],[49,69],[40,69],[40,57],[31,57],[31,51]],
'A4':[[101,93],[101,84],[112,84],[112,74],[124,74],[124,67],[140,67]],
'A4-exit':[[140,67],[142,67],[142,84],[143,84],[143,93]],
'A4-ladder':[[140,67],[148.4,67],[148.4,62]],
'A5-low':[[151,114],[151,120],[145,120]],
'A5-up':[[145,130],[145,138],[132,138],[132,144]],
'A6-up':[[120,166],[120,176],[130,176]],
'A6-low':[[146,176],[148,176],[148,190],[156,190]],
'A8':[[85,184],[85,196],[90,196],[90,206],[73,206],[73,228]],
}
# Layer-specific solid partitions; openings are gaps between segments.
walls={
'A1':[[[96,262],[96,280]],[[96,284],[96,294]],[[62,274],[72,274]],[[76,274],[96,274]]],
'A2':[[[8,212],[24,212]],[[28,212],[56,212]],[[32,184],[32,206]]],
'A3-low':[[[70,110],[70,138]],[[46,120],[46,136]]],
'A3-up':[],
'A7':[[[22,63],[38,63]],[[42,63],[62,63]]],
'A4':[[[88,80],[110,80]],[[114,80],[140,80]],[[144,80],[154,80]],[[132,80],[132,93]],[[126,49],[126,63]],[[126,71],[126,80]]],
'A5-low':[],
'A5-up':[[[138,130],[138,136]],[[138,140],[138,144]]],
'A6-low':[[[110,184],[136,184]],[[140,184],[144,184]],[[130,186],[130,198]]],
'A6-up':[],
'A8':[[[65,204],[88,204]],[[92,204],[101,204]],[[88,208],[88,242]]],
}
# Eight risers per flight; two metre shared landings between adjoining flights.
stairs=[
['I1','A2',[44,228],[44,224],0,-2],
['R1a','A3',[58,128],[58,124],0,2],['R1b','A3',[58,122],[58,118],2,4],
['G1a','A5',[145,120],[145,124],2,4],['G1b','A5',[145,126],[145,130],4,6],
['O1a','A6',[130,176],[134,176],6,4],['O1b','A6',[136,176],[140,176],4,2],['O1c','A6',[142,176],[146,176],2,0],
['T2','hall',[52,158],[52,154],-2,0],['T3','hall',[97,151],[97,147],-2,0],['T4','hall',[121,111],[121,107],0,2],
]
decks={
'A2':[[38,228,50,242,0]],
'A3':[[20,110,84,118,4],[20,118,56,120,4],[60,118,84,120,4],[74,120,84,140,4]],
'A5':[[128,130,150,144,6]],
'A6':[[110,166,130,180,6]],
}
# (room, doorway centre, threshold height). All door centres have 3 m to either jamb.
portals=[['A1',[114,270],0],['A1',[62,288],0],['A2',[44,242],0],['A2',[20,184],-2],['A3',[84,136],0],['A3',[35,110],4],['A3',[52,146],0],['A7',[49,81],4],['A4',[101,93],2],['A4',[143,93],2],['A5',[151,114],2],['A5',[132,144],6],['A6',[120,166],6],['A6',[156,190],0],['A8',[85,184],-2]]

# Paper checks: route axis alignment, walking lines vs partitions and portal bounds.
checks=[]
for name,pts in {**links,**paths}.items():
 assert all(a[0]==b[0] or a[1]==b[1] for a,b in zip(pts,pts[1:])),name
checks.append('Every proposed route is rectilinear.')
def cross(a,b,c,d):
 if a[0]==b[0] and c[1]==d[1]:return min(c[0],d[0])<=a[0]<=max(c[0],d[0]) and min(a[1],b[1])<=c[1]<=max(a[1],b[1])
 if a[1]==b[1] and c[0]==d[0]:return cross(c,d,a,b)
 return False
for name,pts in paths.items():
 wk='A4' if name.startswith('A4') else name
 for a,b in zip(pts,pts[1:]):
  for c,d in walls.get(wk,[]):assert not cross(a,b,c,d),(name,a,b,c,d)
checks.append('Room route centrelines pass through partition openings on the correct floor.')
for name,room,a,b,ya,yb in stairs:
 assert math.dist(a,b)==4 and abs(ya-yb)==2,name
 if room!='hall':
  x,z,w,h,*_=rooms[room]
  for px,pz in (a,b):assert x-w/2+2<=px<=x+w/2-2 and z-h/2+2<=pz<=z+h/2-2,name
checks.append('Every new 2 m stair flight fits its room and has a 4 m horizontal run; landings are drawn.')
for key,px,pz in [('A3',58,119),('A5',145,129),('A6',131,176)]:
 assert not any(x0<px<x1 and z0<pz<z1 for x0,z0,x1,z1,y in decks[key]),(key,'deck blocks stair opening')
checks.append('Upper deck footprints leave the stair-head openings clear.')
for room,(px,pz),height in portals:
 x,z,w,h,*_=rooms[room];xmin,xmax=x-w/2,x+w/2;zmin,zmax=z-h/2,z+h/2
 assert ((px in (xmin,xmax) and zmin+3<=pz<=zmax-3) or (pz in (zmin,zmax) and xmin+3<=px<=xmax-3)),room
checks.append('Every proposed 6 m room threshold fits inside its original footprint.')
# Corridor strips must not cut into an unrelated room. End contacts with their own rooms are allowed.
allowed={'H-A1':['H','A1'],'A1-A2':['A1','A2'],'A2-J0':['A2'],'blocked-D1':['A3'],'bypass':[],'annex':['A8'],'JA-A3':['A3'],'JA-A4':['A4'],'A3-A7':['A3','A7'],'A4-A5':['A4','A5'],'A5-A6':['A5','A6'],'A6-H':['A6','H'],'BcD':['A4','M']}
for name,pts in links.items():
 for key,(x,z,w,h,*_) in rooms.items():
  if key in allowed[name]:continue
  for a,b in zip(pts,pts[1:]):
   r=2 if name=='BcD' else 3
   overlap=min(max(a[0],b[0])+r,x+w/2)-max(min(a[0],b[0])-r,x-w/2)>0.01 and min(max(a[1],b[1])+r,z+h/2)-max(min(a[1],b[1])-r,z-h/2)>0.01
   assert not overlap,(name,key,a,b)
checks.append('Proposed corridor footprints avoid unrelated rooms.')

def length(pts):return sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
# A required, no-annex, no-Maintenance route. Shared outbound/card-return pieces counted twice.
security_trace=sum(length(links[k]) for k in ['H-A1','A1-A2','A2-J0','bypass','JA-A4','A4-A5','A5-A6','A6-H'])
security_trace+=sum(length(paths[k]) for k in ['A1','A2','A4','A4-exit','A5-low','A5-up','A6-up','A6-low'])
security_trace+=2*sum(length(x) for x in [links['JA-A3'],paths['A3-low'],[[58,128],[58,118]],paths['A3-up'],links['A3-A7'],paths['A7']])
security_trace+=10+16 # G1 and O1 flights plus their intermediate landings.
meta={'status':'REVIEWED - BUILT IN BLOCKOUT 05','revision':'A-interiors-01','rooms':rooms,'links':links,'paths':paths,'partitions':walls,'stairs':stairs,'decks':decks,'portals':portals,'records_card':[31,4,51],'freight_card':[112,2,74],'selector':[16,-2,202],'cache':[16,-2,228],'ladder':[148.4,2,62],'ceilings':{'A3':8,'A7':10,'A5':10,'A6':10},'paper_checks':checks,'security_trace_horizontal_m':round(security_trace,1)}
(OUT/'freight-a-interior-plan.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')

class Sheet:
 def __init__(self,w,h,title,subtitle):
  self.w=w;self.h=h
  self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><title>{escape(title)}</title><defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{C["grid"]}" stroke-width=".7"/></pattern>']
  for k in ['route','upper','stair']:self.s.append(f'<marker id="{k}" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0L7 3.5L0 7Z" fill="{C[k]}"/></marker>')
  self.s+=['</defs>',f'<rect width="{w}" height="{h}" fill="{C["bg"]}"/>','<g font-family="Segoe UI,Arial,sans-serif">']
  self.text(40,54,title,30,bold=True);self.text(40,91,subtitle,19,C['muted'])
 def text(self,x,y,t,size=16,color=None,bold=False,anchor='start'):
  self.s.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{color or C["ink"]}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(str(t))}</text>')
 def lines(self,x,y,lines,size=18,color=None,dy=27):
  for i,t in enumerate(lines):self.text(x,y+i*dy,t,size,color)
 def rect(self,x,y,w,h,fill,stroke='none',sw=1,dash=None):
  self.s.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def line(self,pts,color,width=2,dash=None,arrow=None):
  self.s.append('<polyline points="'+' '.join(f'{x:g},{y:g}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+(f' marker-end="url(#{arrow})"' if arrow else '')+'/>')
 def circle(self,x,y,t,color=None,r=15):
  self.s.append(f'<circle cx="{x:g}" cy="{y:g}" r="{r}" fill="{color or C["stair"]}" stroke="{C["bg"]}" stroke-width="2"/>');self.text(x,y+5,t,15,C['bg'],True,'middle')
 def panel(self,x,y,w,h,title):
  self.rect(x,y,w,h,C['panel'],C['grid'],2);self.text(x+22,y+37,title,23,bold=True)
 def save(self,name):
  self.s+=['</g></svg>'];(OUT/(name+'.svg')).write_text('\n'.join(self.s),encoding='utf-8')

class Plan:
 def __init__(self,s,x,y,scale,x0=0,z0=0):self.s=s;self.x=x;self.y=y;self.scale=scale;self.x0=x0;self.z0=z0
 def p(self,x,z):return self.x+(x-self.x0)*self.scale,self.y+(z-self.z0)*self.scale
 def box(self,b,fill,stroke=None,sw=2,dash=None):
  x0,z0,x1,z1=b;px,py=self.p(x0,z0);self.s.rect(px,py,(x1-x0)*self.scale,(z1-z0)*self.scale,fill,stroke or C['wall'],sw,dash)
 def poly(self,pts,color=None,width=2,dash=None,arrow=None):self.s.line([self.p(*v) for v in pts],color or C['route'],width,dash,arrow)
 def text(self,x,z,t,size=15,color=None,bold=False,anchor='start'):self.s.text(*self.p(x,z),t,size,color,bold,anchor)
 def room(self,k,fill=None,ghost=False):
  x,z,w,h,*_=rooms[k];self.box([x-w/2,z-h/2,x+w/2,z+h/2],fill or C['room'],C['muted'] if ghost else C['wall'],1.5 if ghost else 2,'5 5' if ghost else None)
 def parts(self,key):
  for a,b in walls.get(key,[]):self.poly([a,b],C['wall'],4)
 def door(self,p,width=6,color=None):
  px,pz=p;room=next((r for k,r in rooms.items() if abs(abs(px-r[0])-r[2]/2)<.01 and abs(pz-r[1])<=r[3]/2),None)
  pts=[[px,pz-width/2],[px,pz+width/2]] if room else [[px-width/2,pz],[px+width/2,pz]]
  self.poly(pts,color or C['route'],5)
 def stairs(self,st,tag=True):
  name,room,a,b,ya,yb=st;dx=(b[0]-a[0])/4;dz=(b[1]-a[1])/4
  for i in range(9):
   x=a[0]+dx*i*.5;z=a[1]+dz*i*.5;self.poly([[x-dz*2,z+dx*2],[x+dz*2,z-dx*2]],C['stair'],1.5)
  lo,hi=(a,b) if ya<yb else (b,a);self.poly([lo,hi],C['stair'],2,arrow='stair')
  if tag:self.text((a[0]+b[0])/2+3,(a[1]+b[1])/2,name,13,C['stair'],True)
 def badge(self,x,z,t,color=None):self.s.circle(*self.p(x,z),t,color)

def draw_shell(p,k,layer='mixed'):
 p.room(k)
 if layer=='mixed':
  for d in decks.get(k,[]):p.box(d[:4],'#3d3950',C['upper'],1.5,'5 4')
 for room,point,height in portals:
  if room==k:p.door(point,color=C['upper'] if height>=4 else C['route'])

def section(s,x,y,width,labels,levels,title):
 s.text(x,y,title,20,bold=True);basey=y+115
 pts=[(x+30+i*(width-60)/(len(levels)-1),basey-h*11) for i,h in enumerate(levels)]
 s.line([(x,basey),(x+width,basey)],C['grid'],1,'4 4');s.line(pts,C['stair'],3)
 for (px,py),label,h in zip(pts,labels,levels):
  s.text(px,py-12,f'{h:+g} m',15,C['stair'],True,'middle');s.text(px,basey+28,label,14,C['muted'],False,'middle')

# Sheet 1: shared world footprint and all connections.
s=Sheet(1960,1510,'RED BREACH / A LOOP INTERIORS','BUILT A-01 / BLOCKOUT 05   /   Existing footprint, revised interiors and doorway positions')
s.panel(35,125,1035,1320,'A / SECURITY ROUTE');p=Plan(s,65,180,4.5,0,30)
for name,pts in links.items():p.poly(pts,C['grid'],(4 if name=='BcD' else 6)*4.5+3);p.poly(pts,C['void'],(4 if name=='BcD' else 6)*4.5)
for k in rooms:draw_shell(p,k)
for name,pts in links.items():p.poly(pts,C['upper'] if name in ('A3-A7','A5-A6','BcD') else C['route'],2.5,'7 5' if name=='BcD' else None)
for k in ['A1','A2','A3-low','A7','A4','A5-up','A6-low','A8']:p.parts(k)
for k,pts in paths.items():p.poly(pts,C['upper'] if k.endswith('-up') or k=='A7' else C['route'],2)
for st in stairs:p.stairs(st,st[0] in ('I1','R1a','G1a','O1a','T3','T4'))
for k,(x,z,w,h,title,kind) in rooms.items():
 height={'A1':'0','A2':'0 / -2','A3':'0 / +4','A4':'+2','A5':'+2 / +6','A6':'+6 / 0','A7':'+4','A8':'-2','H':'0','M':'+6'}[k]
 p.text(x-w/2+2,z-h/2+4,k+'  '+height+' m',15,C['ink'],True)
# Labels use open floor space; full room names appear in the sidebar.
for x,z,t in [(81,291,'STAFF'),(14,237,'INSPECTION'),(24,141,'ARCHIVE'),(90,76,'LOBBY'),(90,239,'ANNEX'),(170,272,'SERVICE HUB')]:p.text(x,z,t,12,C['muted'])
p.badge(31,51,'R');p.badge(112,74,'K');p.badge(52,147,'1',C['gate']);p.badge(109,128,'2',C['gate'])
p.poly([[176-3,237],[176+3,237]],C['route'],5);p.text(178,235,'S1',16,C['route'],True)
p.poly([[166,59],[166,65]],C['upper'],5);p.text(166,69,'BcD',14,C['upper'],True)
p.poly([[148.4,62],[154,62]],C['upper'],3,'3 3');p.text(147,57,'L',15,C['upper'],True)
p.badge(16,202,'S',C['upper']);p.badge(16,228,'+',C['upper'])
p.text(180,295,'FROM HUB',16,C['route'],True)
p.poly([[8,302],[28,302]],C['muted'],3);p.text(8,308,'20 m  /  north up',14,C['muted'])
s.panel(1100,125,825,1320,'WHAT CHANGES ON THIS WALK')
notes=[('01  STAFF / INSPECTION',['A1 becomes reception, screening and staff rooms.','Opposing doorways move toward different corners.','A2 gets a longer entry deck and divided inspection bays.']),('02  RECORDS / SUPERVISOR',['Enter A3 below an upper walkway. Climb 4 m.','Follow the upper passage into A7 and take Records R.','Return downstairs to door 2. Card stays before its lock.']),('03  SECURITY / THE ROUTE CHOICE',['A4 splits into a lobby, dispatch and an exit vestibule.','Freight K sits on the approach before the routes divide.','BcD retains its separate ladder up to Maintenance.']),('04  WATCH / CLEARANCE RETURN',['Climb from A5 +2 m to a usable +6 m watch floor.','Cross an upper dogleg into A6, then descend 6 m','through the office block to the hub return.']),('05  READABLE TURNS',['Door offsets and partitions interrupt through-views.','Keep the existing branch junctions and return gate S1.','A8 stays optional; B and its progression are unchanged.'])]
y=210
for title,lines in notes:
 s.text(1130,y,title,22,C['stair'],True);s.lines(1130,y+32,lines,19,dy=29);y+=155
s.text(1130,1015,'ROUTE HEIGHTS / metres above the hub',21,bold=True)
section(s,1130,1055,740,['Hub','A2','A3','A7','A3','A4','A5','A6','Hub'],[0,-2,0,4,0,2,6,0,0],'')
s.lines(1130,1260,['Mint: lower route   /   Purple: upstairs route','Gold stair arrows point UP; footprints are to scale.','R = Records card   K = freight card   S = selector','Separate detail sheets show each floor without overlap.'],18,C['muted'],29)
s.text(40,1482,'Reviewed A-01 interiors are built in blockout 05. Walk the revised spaces before the enemy and supply pass.',19,C['muted'])
s.save('freight-a-interior-plan')

# Sheet 2: split floor plans for the Records visit.
s=Sheet(1840,1160,'A3 + A7 / RECORDS AND SUPERVISOR','BUILT A-01 / BLOCKOUT 05   /   Same X-Z alignment in both panels   /   Lower archive + upstairs card visit')
s.panel(35,125,865,960,'LOWER / A3 archive at 0 m');s.panel(925,125,880,960,'UPPER / walkway and A7 at +4 m')
l=Plan(s,100,195,7,15,35);u=Plan(s,990,195,7,15,35)
l.room('A3');l.parts('A3-low');l.door([84,136]);l.poly(links['JA-A3'],C['route'],3);l.poly(paths['A3-low'],C['route'],3,arrow='route')
for d in decks['A3']:l.box(d[:4],'none',C['upper'],1.5,'5 5')
for st in stairs:
 if st[1]=='A3':l.stairs(st,False)
l.text(27,135,'ARCHIVE',18,bold=True);l.text(25,143,'0 m',16,C['stair']);l.text(60,130,'R1',16,C['stair'],True);l.badge(52,147,'1',C['gate']);l.text(60,151,'Fixed sealed door',15,C['gate'])
s.lines(68,220,['1  Enter at the southeast corner, under the upper walkway.','2  The archive partition turns you around its south end.','3  Climb two flights to the north walkway (+4 m).','4  Follow the offset corridor to A7; collect R in its office.','5  Retrace the stairs and leave toward door 2.'],20,dy=37)
section(s,78,440,750,['Archive','Landing','Walkway','A7 / R'],[0,2,4,4],'SECTION / usable upper floor above the archive')
s.lines(78,650,['Upper deck: +4 m; underside at least 3.6 m above archive.','Archive ceiling: +8 m. A7 ceiling at +10 m.','Full-height archive partitions meet the deck where it overlaps.'],17,C['muted'],27)
u.room('A3',C['void'],True)
for d in decks['A3']:u.box(d[:4],'#403953',C['upper'],2)
u.room('A7','#403953');u.parts('A7');u.door([35,110],color=C['upper']);u.door([49,81],color=C['upper']);u.poly(links['A3-A7'],C['upper'],6*7);u.poly(links['A3-A7'],C['void'],6*7-3);u.poly(links['A3-A7'],C['upper'],3)
u.poly(paths['A3-up'],C['upper'],3);u.poly(paths['A7'],C['upper'],3,arrow='upper')
for st in stairs:
 if st[1]=='A3':u.stairs(st,False)
u.badge(31,51,'R');u.text(45,49,'SUPERVISOR',17,bold=True);u.text(44,55,'+4 m',16,C['stair']);u.text(24,75,'ADMIN / WAITING',16,C['muted']);u.text(49,91,'+4 m passage',15,C['upper']);u.text(23,115,'UPPER WALKWAY',14,C['upper'],True);u.text(26,137,'OPEN TO ARCHIVE BELOW',16,C['muted']);u.text(62,127,'R1',16,C['stair'],True)
s.text(40,1120,'No new lock. R remains in A7 and opens door 2. The upstairs visit is reversible; no mandatory jump or drop.',20,C['muted'])
s.save('freight-a-records-detail')

# Sheet 3: Security choice and both levels of the Gallery/Office return.
s=Sheet(1980,1210,'A4 + A5 + A6 / DISPATCH AND THE UPPER RETURN','BUILT A-01 / BLOCKOUT 05   /   Freight card before the split   /   Watch Gallery +6 m leads down through Clearance')
for x,w,title in [(35,630,'A4 / DISPATCH AT +2 m'),(690,620,'A5-A6 / LOWER FLOORS'),(1335,610,'A5-A6 / UPPER AT +6 m')]:s.panel(x,125,w,900,title)
a=Plan(s,65,235,8,86,47);a.room('A4');a.parts('A4')
for point in [[101,93],[143,93]]:a.door(point)
for k in ['A4','A4-exit','A4-ladder']:a.poly(paths[k],C['route'],3)
a.badge(112,74,'K');a.text(92,87,'LOBBY',16,bold=True);a.text(92,62,'DISPATCH',16,bold=True);a.text(134,77,'EXIT',15,C['muted']);a.text(150,56,'LADDER',13,C['upper'],True,anchor='end');a.poly([[148.4,62],[157,62]],C['upper'],3,'5 4',arrow='upper');a.text(129,59,'BcD to +6 m',14,C['upper']);a.text(95,98,'FROM DOOR 2',15,C['route']);a.text(132,103,'TO A5',15,C['route'])
s.lines(65,755,['The lobby feeds into Dispatch past K.','A partition separates the exit vestibule from','the lobby, so it is reached through Dispatch.','','The ordinary route leaves toward A5.','Maintenance keeps its existing ladder and gate;','A5 has no connection across to that upper tunnel.'],18,C['muted'],29)
for sheetx,upper in [(745,False),(1380,True)]:
 p=Plan(s,sheetx,220,7,108,111)
 for k in ['A5','A6']:p.room(k,C['void'] if upper else C['room'],upper)
 if upper:
  for k in ['A5','A6']:
   for d in decks[k]:p.box(d[:4],'#403953',C['upper'],2)
  p.parts('A5-up');p.poly(links['A5-A6'],C['upper'],42);p.poly(links['A5-A6'],C['void'],39);p.poly(links['A5-A6'],C['upper'],3)
  p.poly(paths['A5-up'],C['upper'],3);p.poly(paths['A6-up'],C['upper'],3)
  p.door([132,144],color=C['upper']);p.door([120,166],color=C['upper'])
  p.text(111,187,'OPEN TO OFFICES',15,C['muted']);p.text(111,192,'BELOW',15,C['muted']);p.text(130,141,'WATCH +6',14,C['upper'],True);p.text(111,170,'A6 +6',15,C['upper'],True)
 else:
  p.parts('A6-low');p.poly(links['A4-A5'][-2:],C['route'],3);p.poly(paths['A5-low'],C['route'],3);p.poly(paths['A6-low'],C['route'],3)
  p.door([151,114]);p.door([156,190]);p.poly([[156,190],[167,190]],C['route'],3,arrow='route')
  for k in ['A5','A6']:
   for d in decks[k]:p.box(d[:4],'none',C['upper'],1.5,'5 5')
  p.text(130,117,'A5 +2 m',17,bold=True);p.text(131,141,'DECK ABOVE',13,C['muted']);p.text(112,181,'A6 / 0 m',16,bold=True);p.text(111,195,'RETURN OFFICES',14,C['muted']);p.text(158,195,'S1',16,C['route'],True)
 for st in stairs:
  if st[1] in ('A5','A6'):p.stairs(st,False)
 p.text(148,127,'G1',14,C['stair'],True);p.text(139,173,'O1',14,C['stair'],True)
s.lines(720,912,['G1: two 2 m flights, +2 to +6 m.','O1: three 2 m flights, +6 to 0 m.','Both stairs are reversible; no floor-level bypass.'],18,C['muted'],29)
s.lines(1365,912,['A5 and A6 ceilings: +10 m.','Upper routes have 4 m headroom.','Rails guard the open edges and stair landings.'],18,C['muted'],29)
section(s,75,1060,1790,['A4 / K','A5 entry','Watch floor','A6 upper','Landing','Landing','A6 / S1'],[2,2,6,6,4,2,0],'SECTION / the longer return becomes a sustained upper route')
s.save('freight-a-return-detail')
print(json.dumps({'checks':checks,'security_trace_horizontal_m':round(security_trace,1),'outputs':['freight-a-interior-plan','freight-a-records-detail','freight-a-return-detail']},indent=2))
