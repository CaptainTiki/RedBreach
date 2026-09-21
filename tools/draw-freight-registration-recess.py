"""F-03c as-built drawing: simple recessed route and registration back office."""
from pathlib import Path
from html import escape
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs'
base=json.loads((OUT/'freight-registration-plan.json').read_text())
# User redline: four rectangular strips, with no notches or raised islands.
# The staff branch ends before its door; the office entrance stays on the lower floor.
recess=[[98.5,268.5,113,271.5],[98.5,270,101.5,291.5],[100,278.5,104,281.5],[100,288.5,107.5,291.5]]
main_route=[[114,270],[100,270],[100,272],[96,272]]
recess_outline=[[98.5,268.5],[113,268.5],[113,271.5],[101.5,271.5],[101.5,278.5],[104,278.5],[104,281.5],[101.5,281.5],[101.5,288.5],[107.5,288.5],[107.5,291.5],[98.5,291.5],[98.5,268.5]]
props=[]
def add(id,kind,b,h,lo=0):props.append({'id':id,'kind':kind,'bounds':b,'bottom':lo,'top':lo+h})
add('D1','supervisor workstation',[103,285.0,106,286.2],.75)
add('C1','chair',[104.15,286.45,104.8,287.1],.9)
add('D2','registration workstation',[108.2,287,110.6,288.2],.75)
add('C2','chair',[109.3,288.45,109.95,289.1],.9)
add('F1','filing cabinets',[96.6,285,97.8,287.8],2.1)
add('F2','filing / archive cabinets',[107,284.4,110.2,285.2],2.1)
add('F3','supply cabinets',[111.75,291,113.6,292.25],2.1)
add('S1','two server rack envelopes',[112.35,285.1,113.65,288.2],2.4)
add('A1','air circulation unit',[96.6,289,97.9,291],2.2)
add('A2','air filter / service unit',[98.5,292.9,100.3,293.7],2.2)
add('T1','wall status readout',[103,284.15,105.4,284.35],.8,1.3)
add('T2','wall terminal',[113.7,288.7,113.95,289.7],.9,1.1)
add('M1','desk monitor',[103.5,285.15,104.4,285.4],.5,.75)
add('M2','desk monitor',[108.55,287.15,109.45,287.4],.5,.75)
office_route=[[100,284],[100,290],[106,290]]
def overlap(a,b):return min(a[2],b[2])-max(a[0],b[0])>1e-7 and min(a[3],b[3])-max(a[1],b[1])>1e-7
# Parent-on-desk monitors are intentional; other 3D overlaps are not.
for i,p in enumerate(props):
 for q in props[i+1:]:
  if p['id'].startswith('M') or q['id'].startswith('M'):continue
  assert not (overlap(p['bounds'],q['bounds']) and min(p['top'],q['top'])>max(p['bottom'],q['bottom'])),(p['id'],q['id'])
for a,b in zip(office_route,office_route[1:]):
 r=[min(a[0],b[0])-1.5,min(a[1],b[1])-1.5,max(a[0],b[0])+1.5,max(a[1],b[1])+1.5]
 for p in props:assert not overlap(r,p['bounds']),(p['id'],r)
# Recess patches may run under overhead service trunks, never under floor furniture.
for r in recess:
 for p in base['floor_objects']:
  if p['group']=='lounge':continue
  assert not overlap(r,p['bounds']),(r,p['id'])
plan={'revision':'F-03c','status':'BUILT - APPROVED F-03c / LAYOUT 08','built_layout':'08','baseline_layout':'07','baseline_map_sha256':'07d6b5b95f8360945c0f24b030139c6d1103c3e9afe3b7b3d3c5bdeaee8ba5bc','bounds':base['bounds'],'floor_levels':{'corridor_and_work_bays':0,'recessed_walkway':-.25},'recess_rectangles':recess,'recess_outline':recess_outline,'main_route':main_route,'reference':'references/f03-walkway-annotation.png','route_width_m':3,'step_height_m':.25,'ceiling_y':3.5,'landings':[{'name':'hub arrival','bounds':[113,267,114,273],'floor':0},{'name':'screening approach','bounds':[96.125,270,98.5,274],'floor':0},{'name':'staff door approach','bounds':[104,278.5,108,281.5],'floor':0},{'name':'back-office threshold','bounds':[98.5,282,101.5,286],'floor':-.25}],'staff_door':{'centre':[106,0,280],'wall_axis':'x','opening_width_m':3,'opening_height_m':3.2,'head_y':3.2,'header_infill_m':0,'existing_slot_width_m':4,'side_infill_m':.5,'behavior':'unlocked E-use both sides; existing StateChart and obstruction behavior; reset closed; no key requirement'},'office_bounds':[96.125,284.125,114,294],'office_route':office_route,'office_props':props,'preserve':['entry view and registration assembly','small waiting bay','window, glass, outside diorama','existing lighting and fixtures','screening and other departments','mission keys and route dependencies'],'checks':['0.25 m = 8 map units at 32 units/metre; same as existing stair risers','Recess avoids all retained floor furniture','Back-office route reserves 3 m ribbons clear of equipment','Four-metre staff slot receives 0.5 m side infills for a 3 m door','Staff branch stops 2 m before the level door; the office entrance retains its continuous lower floor','Window-room footprint remains 17.875 x 9.875 m, ratio 1.81:1'],'notes':['Built and validated: walking, sprinting, backpedalling and strafing cross the step samples both ways; human feel awaits playtest','Four straight rectangular strips follow the user redline; raised work bays retain their existing elevations','Supervision/registration operations replaces the lounge use; no new gameplay reward or secret']}
(OUT/'freight-registration-recess-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
C={'bg':'#101c28','panel':'#1a2c3c','room':'#283d49','wall':'#e2c28e','ink':'#f0f4f7','muted':'#afc1cd','prop':'#708fa8','route':'#79e0b8','over':'#bba0e6','light':'#ffe296','window':'#6cd9e8','lower':'#244f69','edge':'#6cadde','door':'#dfac71'}
s=[]
def text(x,y,t,size=17,color='ink',weight=400,anchor='start'):s.append(f'<text x="{x:g}" y="{y:g}" fill="{C.get(color,color)}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(t))}</text>')
def rect(x,y,w,h,fill,stroke='none',sw=1,dash=''):s.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def line(points,color,width=2,dash='',arrow=False):s.append('<polyline points="'+' '.join(f'{x:g},{y:g}' for x,y in points)+f'" fill="none" stroke="{C.get(color,color)}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
s.append('<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="1320" viewBox="0 0 1700 1320"><title>Red Breach F-03 Recessed Registration Walkway and Back Office</title><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0L7 3.5L0 7Z" fill="#79e0b8"/></marker></defs>');rect(0,0,1700,1320,'bg');s.append('<g font-family="Segoe UI,Arial,sans-serif">')
text(38,48,'RED BREACH / REGISTRATION REFINEMENT / F-03c',29,weight=700)
text(38,80,'BUILT / LAYOUT 08  |  Simple lower walkway; the staff branch ends before the door',18,'muted')
rect(35,112,655,1120,'panel');text(57,149,'REGISTRATION / FLOOR LEVELS AND ROUTE',20,weight=700)
def draw_plan(origin,scale,zoom=False):
 ox,oy=origin;b=plan['office_bounds'] if zoom else base['bounds'];x0,z0=b[:2]
 def p(x,z):return ox+(x-x0)*scale,oy+(z-z0)*scale
 def box(bb,color,stroke='none',sw=1):
  x,y=p(bb[0],bb[1]);rect(x,y,(bb[2]-bb[0])*scale,(bb[3]-bb[1])*scale,color,stroke,sw)
 def path(points,*args,**kwargs):line([p(*pt) for pt in points],*args,**kwargs)
 box(b,'room','wall',4)
 if not zoom:
  for r in recess:box(r,'lower')
  path(recess_outline,'edge',3)
  for w in base['walls']:path(w,'wall',6)
  path([[114,267],[114,273]],'room',7);path([[114,267],[114,273]],'route',2)
  path([[96.125,270],[96.125,274]],'room',7);path([[96.125,270],[96.125,274]],'route',2)
  for ob in base['floor_objects']:
   if ob['group']=='lounge':continue
   box(ob['bounds'],'prop','#b5c6d2',.6)
  # Staff wall infills and actual three-metre door.
  path([[106,278],[106,278.5]],'wall',8);path([[106,281.5],[106,282]],'wall',8)
  path([[106,278.5],[106,281.5]],'door',6)
  for points in [main_route,[[100,272],[100,290],[106,290]],[[100,280],[110,280]]]:path(points,'route',2,'5 4',True)
  for x,z,label in [(108,269,'−0.25'),(100,277.8,'−0.25'),(110,283.1,'STAFF BAY / 0'),(105,287.6,'OFFICE / 0')]:text(*p(x,z),label,12,'ink',700,'middle')
  xx,yy=p(109.6,273.5);text(xx,yy,'REGISTRATION',13,'ink',700,'middle')
  xx,yy=p(105,279.6);text(xx,yy,'UP / 0',10,'edge',700,'middle')
  xx,yy=p(103.5,289.5);text(xx,yy,'-0.25',10,'edge',700,'middle')
 else:
  for r in recess:
   clipped=[max(r[0],b[0]),max(r[1],b[1]),min(r[2],b[2]),min(r[3],b[3])]
   if clipped[2]>clipped[0] and clipped[3]>clipped[1]:box(clipped,'lower')
  path([[98,284.125],[102,284.125]],'room',7);path([[98,284.125],[102,284.125]],'route',2)
  path(office_route,'route',2,'5 4',True)
 for ob in props:
  color='window' if ob['id'].startswith(('T','M')) else 'prop'
  box(ob['bounds'],color,'#b5c6d2',.6)
  if not ob['id'].startswith(('C','M','T')):
   bb=ob['bounds'];xx,yy=p((bb[0]+bb[2])/2,(bb[1]+bb[3])/2);text(xx,yy+4,ob['id'],13 if zoom else 9,'bg',700,'middle')
 path([[102,294],[110,294]],'window',6)
 return p
p=draw_plan((150,185),24)
text(605,p(114,270)[1]-18,'FROM HUB',13,'route',700);text(132,p(96.125,272)[1]-18,'SCREENING',12,'route',700,'end')
text(132,p(96.125,272)[1]+2,'still floor 0',11,'muted',400,'end')
text(360,977,'Exterior view, glazing and lighting retained',14,'window',anchor='middle')
text(58,1024,'Blue floor = 3 m-wide route at −0.25 m.',18,'edge',700)
text(58,1057,'Work bays and furniture remain at their current 0 m level.',15,'muted')
text(58,1085,'Straight entry, one long spine, two square side branches.',15,'muted')
text(58,1113,'Staff branch stops before the door; office strip continues.',15,'muted')
text(58,1156,'0.25 m = 8 map units; same rise as our existing stairs.',16,'ink')
text(58,1185,'Movement checks pass, including diagonal and reverse crossings.',14,'muted')
# Enlarged office furniture plan.
rect(720,112,945,550,'panel');text(744,149,'THE WINDOW ROOM BECOMES REGISTRATION OPERATIONS',20,weight=700)
text(744,178,'Equipment bays stay at 0 m; the simple walkway continues through at -0.25 m.',15,'muted')
q=draw_plan((855,220),37,True)
text(1210,206,'ENTRY FROM WAITING',13,'route',700,'middle')
text(1200,611,'Keep the view across the window clear of tall equipment.',16,'window',anchor='middle')
text(744,641,'D = desk  ·  F = filing/storage  ·  S = servers  ·  A = air unit  ·  cyan = readouts',15,'muted')
# Height profile is intentionally exaggerated to show the single step.
rect(720,686,945,265,'panel');text(744,724,'STAFF BRANCH / STEP UP BEFORE THE DOOR',20,weight=700)
text(744,751,'Floor profile only; the vertical difference is exaggerated for clarity.',14,'muted')
line([(780,815),(910,815),(910,870),(1240,870),(1240,815),(1580,815)],'edge',4)
line([(1430,778),(1430,815)],'door',6)
text(790,798,'Arrival 0',15,'ink');text(1050,899,'Walkway −0.25 m',17,'edge',700)
text(1195,930,'2 m level approach; desk floor stays at 0 m',15,'ink');text(1365,770,'STAFF DOOR',14,'door',700)
text(744,774,'Recess ends early, keeping the step edge away from staff chairs.',15,'muted')
rect(720,975,945,257,'panel');text(744,1013,'STAFF ACCESS + BACK-OFFICE FUNCTION',20,weight=700)
text(744,1048,'The staff door and desk bay stay on the existing 0 m floor.',17)
text(744,1077,'Unlocked E-use on both sides; retain our tested obstruction behavior.',16,'muted')
text(744,1113,'Two desks/readouts, three storage banks, two server-rack envelopes,',17)
text(744,1142,'two air-handling units and wall terminals replace the sparse lounge.',17)
text(744,1180,'The small waiting area stays. No new card, objective or reward is added.',16,'muted')
text(38,1285,'BUILT F-03c / 199 freight checks + 9 texture checks passed. Screening retains its F-01 blockout.',17,'muted')
s.append('</g></svg>');(OUT/'freight-registration-recess-plan.svg').write_text('\n'.join(s),encoding='utf-8')
print(json.dumps({'status':plan['status'],'checks':plan['checks'],'office_envelopes':len(props),'built_layout':'08'}))
