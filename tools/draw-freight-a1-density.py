"""F-04 paper plan for the remaining A1 rooms; does not write playable geometry."""
from pathlib import Path
from html import escape
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs'
rooms={'screening':[82.125,262,95.875,275.875],'admin':[62,262,81.875,275.875],'prep':[62,276.125,95.875,294]}
props=[];overhead=[];routes=[]
def add(room,id,name,b,top,kind='equipment',bottom=0):
 row={'room':room,'id':id,'name':name,'bounds':b,'bottom':bottom,'top':top,'kind':kind}
 (overhead if bottom>=2.4 else props).append(row)
def route(room,name,points,width,main=False):routes.append({'room':room,'name':name,'points':points,'width':width,'main':main})
# SCREENING: visible staff station and baggage examination flank the through lane.
route('screening','Main / registration to staff prep',[[96,272],[88,272],[88,276]],3,True)
route('screening','Administration branch',[[88,272],[88,268],[82,268]],3)
route('screening','Observation station',[[88,272],[84.4,272]],2)
add('screening','S1a','Scan arch / north post',[90.25,269.75,91.25,270.5],2.8,'scanner')
add('screening','S1b','Scan arch / south post',[90.25,273.5,91.25,274.25],2.8,'scanner')
add('screening','S1h','Scan arch / overhead',[90.25,269.75,91.25,274.25],3.15,'scanner',2.8)
add('screening','S2','Baggage scanner and conveyor',[90,267.5,95,269.25],2.4,'scanner')
add('screening','S3','Screening operator desk',[84.4,264.4,87.2,265.4],.9,'desk')
add('screening','s3','Operator chair',[85.5,265.55,86.15,266.2],.9,'chair')
add('screening','S4','Observation / inspection counter',[83.8,273.8,85.8,275.2],1.1,'desk')
add('screening','S5','Personal storage bank',[91.5,275.0,95.2,275.75],2.2,'storage')
add('screening','S6','Records and equipment storage',[83.0,262.25,88.6,263.05],2.2,'storage')
add('screening','S7','Scan electronics / cooling',[94.1,262.8,95.5,265.7],2.5,'service')
add('screening','S8','Inspection supply cabinet',[82.5,271.4,83.2,275.2],2.2,'storage')
add('screening','S9','Wall status display',[95.58,268.6,95.8,269.8],2.1,'display',1.1)
# ADMINISTRATION: five desk pods, paired chairs, archive bay and service aisles.
route('admin','Office spine',[[82,268],[65,268]],3)
for x in [68.8,76]:route('admin','Workstation aisle',[[x,264.4],[x,273.4]],2)
route('admin','Archive access',[[76,273],[79.5,273]],2)
for i,b in enumerate([[64,263.6,67,265.4],[71,263.6,74,265.4],[78,263.6,80.6,265.2],[64,270.5,67,272.3],[71,270.5,74,272.3]],1):
 add('admin','A'+str(i),'Paired workstations',b,.75,'desk')
 for j in range(2):
  x=b[0]+.45+j*1.25;z=b[3]+.15
  add('admin',f'a{i}{j}', 'Desk chair',[x,z,x+.65,z+.65],.9,'chair')
add('admin','A6','West filing cabinets',[62.25,262.5,63.15,265.8],2.2,'storage')
add('admin','A7','Network cabinet',[80.75,262.8,81.55,265.8],2.4,'service')
add('admin','A8','Archive north bank',[78.8,270.8,80.8,271.7],2.2,'storage')
add('admin','A9','Archive south bank',[78.8,274.4,80.8,275.3],2.2,'storage')
add('admin','A10','Records wall cabinets',[64,274.8,74.2,275.65],2.2,'storage')
add('admin','A11','Air handling',[62.25,270.5,63.15,273],2.3,'service')
add('admin','A12','Wall readout',[62.13,267,62.4,268.9],2.1,'display',1.1)
# STAFF PREP: connected functional bays, with partial equipment backboards.
route('prep','Main / screening to Inspection',[[88,276],[88,282],[74,282],[74,288],[62,288]],3,True)
route('prep','Locker and cleaning aisle',[[88,282],[88,291],[93,291]],3)
route('prep','Repair workbench access',[[88,288.5],[80,288.5]],2)
route('prep','Tool bay access',[[74,282],[65,282],[65,285]],2)
add('prep','P1','Kit issue counter',[76.5,279.1,84.5,280.1],1.1,'desk')
add('prep','P2','Kit issue storage wall',[76.5,276.4,84.8,277.15],2.3,'storage')
add('prep','P3','Changing / north lockers',[90.5,276.4,95.1,277.3],2.2,'storage')
add('prep','P4','Changing bench',[90.5,279.2,92.5,280],.45,'bench')
add('prep','P5','Suit cleaning and air unit',[94.5,279,95.55,284.2],2.5,'service')
add('prep','P6','PPE issue cabinets',[90.3,281.2,93,282.7],2.2,'storage')
add('prep','P7','Changing bench',[90.5,286.2,93,287],.45,'bench')
add('prep','P8','East service lockers',[94.9,286.3,95.65,289],2.2,'storage')
add('prep','P9','South changing lockers',[85.1,293.05,94.5,293.8],2.2,'storage')
add('prep','P10','Equipment repair bench',[78,285.3,83,286.5],1.0,'desk')
add('prep','p10','Repair stool',[79.3,286.7,79.95,287.35],.7,'chair')
add('prep','P11','Equipment fitting bench',[78.2,290.3,82.4,291],.45,'bench')
add('prep','P12','Spare kit lockers',[76.5,292.8,84.8,293.8],2.2,'storage')
add('prep','P13','Tool cabinets',[63,276.8,68,277.8],2.2,'storage')
add('prep','P14','Outbound tool check bench',[64,279.6,68,280.8],.9,'desk')
add('prep','P15','Equipment cart bay',[69.5,277,71.8,280.5],1.4,'equipment')
add('prep','P16','Utility cabinets',[62.25,279.7,63.1,284.4],2.2,'service')
add('prep','P17','Prepared equipment carts',[68.4,284.3,71.3,285.8],1.2,'equipment')
add('prep','P18','Outbound cases',[64,292.6,68.5,293.7],1.4,'equipment')
add('prep','P19','Tool/supply rack',[69.5,290.5,71.8,293.5],2.2,'storage')
add('prep','P20','Outbound trolley',[66,290.5,68.5,291.5],1.1,'equipment')
for id,b in [('B1',[85.8,284.2,86.1,287.1]),('B2',[85.8,289.9,86.1,292.3]),('B3',[75.75,284.2,76,285.8]),('B4',[75.75,289.9,76,292.3])]:add('prep',id,'Equipment backboard / partial bay divider',b,2.4,'backboard')
# Overhead density stays useful: ducts, fixture housings and beams, all with height labels.
for room,id,b in [('screening','D-S',[82.875,262.15,95.125,262.75]),('admin','D-A',[62.4,262.15,81.5,262.75]),('prep','D-P1',[62.4,276.25,85,276.85]),('prep','D-P2',[95.0,277,95.6,293.4])]:add(room,id,'Ceiling service trunk',b,3.4,'duct',2.95)
for room,centres in [('screening',[(85.5,264.8),(92.5,268),(92.5,272),(87.5,274)]),('admin',[(65.5,264.5),(72.5,264.5),(79.2,264.5),(65.5,271.4),(72.5,271.4),(79.4,273)]),('prep',[(65.5,279.9),(72,283.4),(80.5,279.6),(80.5,285.8),(91.5,278.2),(91.5,286.7),(87.8,291.8)])]:
 for i,(x,z) in enumerate(centres,1):add(room,f'L{room[0]}{i}','Task light housing',[x-1.1,z-.12,x+1.1,z+.12],3.12,'light',2.95)
for room,id,b in [('admin','T-A',[73.9,262.2,74.2,275.7]),('prep','T-P1',[62.4,284,95.5,284.25]),('prep','T-P2',[62.4,290,95.5,290.25])]:add(room,id,'Ceiling beam',b,3.5,'beam',3.22)


# Architectural sample: four shallow ribs. Side legs stop at existing openings.
for i,z in enumerate([263.5,267.25,271,274.75],1):
 add('screening',f'R{i}H','Structural rib / ceiling',[82.125,z-.125,95.875,z+.125],3.5,'beam',3.25)
 if not 266 <= z <= 270:
  add('screening',f'R{i}W','Structural rib / west leg',[82.125,z-.125,82.375,z+.125],3.25,'service')
 if not 270 <= z <= 274:
  add('screening',f'R{i}E','Structural rib / east leg',[95.625,z-.125,95.875,z+.125],3.25,'service')
architecture={'status':'BUILT SCREENING - USER WALKTHROUGH NEXT', 'sample':'Screening ribs and upper corners; Screening/Staff Preparation threshold', 'rib_stations_z':[263.5,267.25,271,274.75], 'rib_width':.25, 'rib_projection':.25, 'rib_underside':3.25, 'rib_corner_intercept':.8, 'upper_corner':{'rise':.55,'projection':.55,'starts_at_height':2.95,'interrupt_at_doorways':True}, 'threshold':{'centre':[88,276],'clear_width':4,'clear_height':3.2,'frame_outside_width':5,'depth':.5,'side_leg_bounds':[[85.5,275.75,86,276.25],[90,275.75,90.5,276.25]],'door_behaviour':'No new working door in this sample'}, 'scanner_top':3.15, 'reference':'freight-a1-architecture-section.svg'}

def overlap(a,b):return min(a[2],b[2])-max(a[0],b[0])>1e-6 and min(a[3],b[3])-max(a[1],b[1])>1e-6
for r in routes:
 for u,v in zip(r['points'],r['points'][1:]):
  assert u[0]==v[0] or u[1]==v[1]
  w=r['width']/2;b=[min(u[0],v[0])-w,min(u[1],v[1])-w,max(u[0],v[0])+w,max(u[1],v[1])+w]
  for p in props:
   if p['room']==r['room']:assert not overlap(b,p['bounds']),(r['room'],r['name'],p['id'])
for i,p in enumerate(props):
 b=p['bounds'];r=rooms[p['room']];assert r[0]<=b[0]<b[2]<=r[2] and r[1]<=b[1]<b[3]<=r[3],p['id']
 for q in props[i+1:]:
  if p['room']==q['room']:assert not (overlap(b,q['bounds']) and min(p['top'],q['top'])>max(p['bottom'],q['bottom'])),(p['id'],q['id'])
checks=['Three-metre main/through routes clear every floor prop and backboard','Two-metre staff/working aisles clear the drawn floor props','All new footprints fit their existing rooms and do not overlap','Scan arch reserves 3.0 m clear width and 2.8 m clear height','Floors stay at 0 m and ceiling slabs at 3.5 m; ribs leave 3.25 m and the threshold 3.2 m clear']
plan={'revision':'F-04','status':'PAPER REVIEW - NOT BUILT','source_layout':'08','source_map_sha256':hashlib.sha256((ROOT/'RedBreach/maps/freight_01.map').read_bytes()).hexdigest(),'architecture':architecture,'rooms':rooms,'floor':0,'ceiling':3.5,'routes':routes,'floor_props':props,'overhead':overhead,'checks':checks,'replace':'Earlier F01 furnishings inside these three rooms only','preserve':['Registration and exterior view','existing room shells and openings','main mission route and optional Administration visit','keys, gates and accepted level length','movement settings'],'references':['references/doom3-administration/registration.png','references/doom3-administration/work-area.png','references/doom3-administration/return-catwalk.png'],'notes':['Monitors, handles and tray boxes belong to their desk/equipment assemblies; do not scatter floor clutter','Scanning and suit-cleaning equipment are visual blockout props, not new interaction mechanics','Orange ribbons in this drawing reserve clearance; all these floors are level','Enemy and broader pickup placement remain a later pass']}
# Preserve approval/build evidence when redrawing this same reviewed arrangement.
previous=json.loads((OUT/'freight-a1-density-plan.json').read_text()) if (OUT/'freight-a1-density-plan.json').exists() else {}
for key in ['status','built_layout','built_rooms','pending_rooms','validation','source_layout','source_map_sha256']:
 if key in previous:plan[key]=previous[key]
(OUT/'freight-a1-density-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
C={'bg':'#101c28','panel':'#1a2c3c','ink':'#edf4fa','muted':'#adc1d0','room':'#2a3440','wall':'#81b59e','prop':'#85649f','storage':'#725383','service':'#75818c','desk':'#9077a6','chair':'#a6a1b7','scanner':'#b3976c','route':'#e2b373','over':'#a1b5c3','light':'#ffe5a8','display':'#60d3d7','bench':'#9c86b0','backboard':'#81b59e'}
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1370" viewBox="0 0 1800 1370"><title>Red Breach F-04 Screening Administration Staff Preparation</title><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0L7 3.5L0 7Z" fill="#e2b373"/></marker></defs><rect width="1800" height="1370" fill="#101c28"/><g font-family="Segoe UI,Arial,sans-serif">']
def text(x,y,t,size=17,color='ink',bold=False,anchor='start'):s.append(f'<text x="{x:g}" y="{y:g}" fill="{C.get(color,color)}" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(str(t))}</text>')
def rect(x,y,w,h,color,stroke='none',sw=1,opacity=1,dash=''):s.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{C.get(color,color)}" stroke="{C.get(stroke,stroke)}" stroke-width="{sw}" opacity="{opacity}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def line(points,color,sw=2,dash='',arrow=False):s.append('<polyline points="'+' '.join(f'{x:g},{y:g}' for x,y in points)+f'" fill="none" stroke="{C.get(color,color)}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
def panel(x,y,w,h,title):rect(x,y,w,h,'panel');text(x+22,y+36,title,22,bold=True)
text(36,49,'RED BREACH / A1 DENSITY PASS / F-04',30,bold=True)
text(36,83,'APPROVED  |  Screening built first → Administration + Staff Preparation planned',19,'muted')
panel(36,117,950,1120,'CONNECTED PLAN / EXISTING SHELL AND DOORS')
ox,oy,scale=106,213,24
pt=lambda x,z:(ox+(x-62)*scale,oy+(z-262)*scale)
def box(b,color,stroke='none',sw=1,opacity=1,dash=''):
 x,y=pt(b[0],b[1]);rect(x,y,(b[2]-b[0])*scale,(b[3]-b[1])*scale,color,stroke,sw,opacity,dash)
def path(points,*args,**kwargs):line([pt(*p) for p in points],*args,**kwargs)
for room,b in rooms.items():box(b,'room','wall',4)
for x in range(65,96,5):path([[x,262],[x,294]],'#3c4651',.7)
for z in range(265,294,5):path([[62,z],[96,z]],'#3c4651',.7)
for r in routes:
 for a,b in zip(r['points'],r['points'][1:]):
  w=r['width']/2;box([min(a[0],b[0])-w,min(a[1],b[1])-w,max(a[0],b[0])+w,max(a[1],b[1])+w],'route',opacity=.11)
# Openings remain in their reviewed positions; erase shell strokes at the aperture.
for a,b in [([96,270],[96,274]),([82,266],[82,270]),([86,276],[90,276]),([62,285],[62,291])]:path([a,b],'room',9);path([a,b],'route',2)
for p in props:
 box(p['bounds'],p['kind'] if p['kind'] in C else 'prop','#c6b7d4',.75)

for p in overhead:
 if p['kind']=='light':box(p['bounds'],'light',opacity=.9)
 else:box(p['bounds'],'none','over',1.5,opacity=.8,dash='5 4')
for b in architecture['threshold']['side_leg_bounds']:box(b,'wall')
box([85.5,275.75,90.5,276.25],'none','over',1.5,dash='5 4')
for p in props:
 if p['kind'] not in ['chair','display'] and not p['id'].startswith('R'):
  b=p['bounds'];x,y=pt((b[0]+b[2])/2,(b[1]+b[3])/2);text(x,y+4,p['id'],12,'bg',True,'middle')
for r in routes:path(r['points'],'route',2.5 if r['main'] else 1.5,'' if r['main'] else '5 4',True)
text(*pt(71.8,261.15),'ADMINISTRATION',18,bold=True,anchor='middle')
text(*pt(89,261.15),'SCREENING',18,bold=True,anchor='middle')
text(*pt(79,295.25),'STAFF PREPARATION',20,bold=True,anchor='middle')
text(942,pt(96,272)[1]-22,'FROM',13,'route',True,anchor='middle');text(942,pt(96,272)[1]-4,'REGISTRATION',12,'route',True,anchor='middle')
text(93,pt(62,288)[1]-17,'TO A2',13,'route',True,anchor='end');text(93,pt(62,288)[1]+2,'INSPECTION',12,'route',True,anchor='end')
text(58,1068,'Solid orange: main route, 3 m clear.',17,'route',True)
text(58,1098,'Dashed orange: optional visits and working aisles (2–3 m).',16,'muted')
text(58,1128,'Dashed grey: overhead structure/services. Yellow: light housings.',16,'muted')
text(58,1167,'All floors stay at 0 m. Orange is clearance shading, not a new recess.',16)
text(58,1196,'Furniture, cabinets and equipment define bays; floor clutter stays controlled.',15,'muted')
# Functional schedules describe whole assemblies rather than modelling tiny details.
panel(1010,117,754,239,'SCREENING / A CHECKPOINT YOU CAN READ')
for j,t in enumerate(['S1  Walk-through scan frame: 3 m wide, 2.8 m high inside.','S2  Baggage conveyor and scanner beside the walking lane.','S3–4  Operator station and observation / examination counter.','S5–8  Lockers, storage, cooling and inspection supplies.','S9  Wall readout; task lights, ducts and repeated structural ribs.']):text(1032,179+j*32,t,16)
panel(1010,375,754,247,'ADMINISTRATION / A WORKING OFFICE')
for j,t in enumerate(['A1–5  Five paired desk pods, monitors and ten chair blocks.','A6–10  Filing, network cabinet and a distinct archive bay.','A11–12  Air unit and wall display.','A 3 m entry spine connects to 2 m working aisles.','Optional branch: visit and return through the same opening.']):text(1032,440+j*32,t,16)
panel(1010,641,754,262,'STAFF PREPARATION / THREE EQUIPPED BAYS')
for j,t in enumerate(['P1–2  Kit issue counter with staff space and storage behind.','P3–9  Changing benches, lockers and suit-cleaning equipment.','P10–12  Repair/fitting bench, seat and spare kit.','P13–20  Tool check, carts, supplies and outbound cases.','B1–4  Partial equipment backboards separate the work bays.','The 3 m route stays continuous through the offsets to A2.']):text(1032,702+j*31,t,16)
panel(1010,922,754,315,'SCREENING SECTION / KEEP THE PASSAGE GENEROUS')
# View along travel axis: two posts and one overhead box, no gate leaf.
origin_x,floor_y,k=1130,1191,57
line([(1090,floor_y),(1684,floor_y)],'muted',2)
line([(1090,floor_y-3.5*k),(1684,floor_y-3.5*k)],'over',2,'6 4')
rect(origin_x,floor_y-2.8*k,.75*k,2.8*k,'scanner')
rect(origin_x+3.75*k,floor_y-2.8*k,.75*k,2.8*k,'scanner')
rect(origin_x,floor_y-3.15*k,4.5*k,.35*k,'scanner')
rect(origin_x+2*k,floor_y-1.8*k,.6*k,1.8*k,'service')
text(origin_x+2.25*k,floor_y-2.35*k,'3 m clear',17,'route',True,'middle')
text(1447,1035,'Ceiling: 3.5 m',17,'muted');text(1447,1070,'Arch opening: 2.8 m',17);text(1447,1105,'Standing figure: 1.8 m',16,'muted');text(1447,1150,'Visual prop only;',16);text(1447,1177,'no new scan mechanic.',16,'muted')
text(36,1290,'DENSITY GOAL: composed equipment, work areas and overhead structure; open floor has a circulation or working purpose.',18,bold=True)
text(36,1323,'F-04: Screening pilot built as layout 09. Administration and Staff Preparation remain planned. Registration is preserved.',17,'muted')
s.append('</g></svg>');(OUT/'freight-a1-density-plan.svg').write_text('\n'.join(s),encoding='utf-8')
print(json.dumps({'status':plan['status'],'floor_prop_envelopes':len(props),'overhead_envelopes':len(overhead),'checks':checks}))
