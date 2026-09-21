"""F-02 reception composition: built layout 07 record. Never edits the playable map."""
from pathlib import Path
from html import escape
import json,math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs'
C={'bg':'#101c28','panel':'#1a2c3c','room':'#283d49','wall':'#e2c28e','ink':'#f0f4f7','muted':'#afc1cd','prop':'#708fa8','route':'#79e0b8','over':'#bba0e6','light':'#ffe296','window':'#6cd9e8','item':'#e8b786'}
bounds=[96.125,262,114,294]
rooms=[['01','Arrival / registration front',[96.125,262,114,275.875]],['02','Waiting bay',[96.125,276.125,105.875,283.875]],['03','Registration staff bay',[106.125,276.125,114,283.875]],['04','Window lounge',[96.125,284.125,114,294]]]
walls=[[[96.125,276],[98,276]],[[102,276],[106,276]],[[106,276],[106,278]],[[106,282],[106,284]],[[96.125,284],[98,284]],[[102,284],[114,284]]]
route=[[114,270],[104,270],[104,272],[96,272]]
optional=[[[104,272],[100,272],[100,290],[106,290]],[[100,280],[109,280]],[[104,272],[109,272],[109,274.5]]]
props=[];over=[]
def prop(id,kind,b,h,group):props.append({'id':id,'kind':kind,'bounds':b,'height':h,'group':group,'floor':0})
prop('E1','equipment cabinets',[97,262.3,101,263.3],2.4,'entry')
prop('E2','wall cabinets',[105,262.3,110,263.3],2.4,'entry')
prop('E3','information kiosk',[97,265,99,266.4],1.5,'entry')
prop('E4','check terminal',[103,265,105,266],1.2,'entry')
prop('E5','equipment housing',[111.6,263.5,113.4,265.5],2.4,'entry')
prop('R1','registration counter front',[106.125,276.4,113.5,277.4],1.1,'registration')
prop('R2','counter return',[106.125,277.4,107.125,277.8],1.1,'registration')
prop('R3','counter return',[112.5,277.4,113.5,280.5],1.1,'registration')
prop('R4','staff chair',[108,277.65,108.65,278.3],.9,'registration')
prop('R5','staff chair',[110.6,277.65,111.25,278.3],.9,'registration')
prop('R6','staff back counter',[107.4,282.7,112.9,283.8],1.1,'registration')
prop('R7','supply cabinet',[112.95,280.8,113.75,283.8],2.2,'registration')
prop('W1','waiting seats',[96.8,276.6,97.6,281.2],.9,'waiting')
prop('W2','queue rail',[102.7,276.6,102.8,277.8],1.1,'waiting')
prop('W3','service cabinet',[102.6,282.65,105.6,283.7],2.2,'waiting')
prop('L1','lounge seats',[96.8,286,97.6,291.2],.9,'lounge')
prop('L2','lounge seats',[104,284.7,108,285.5],.9,'lounge')
prop('L3','lounge seats',[112.8,286,113.6,289.8],.9,'lounge')
prop('L4','low table',[109,288,110.2,289.2],.5,'lounge')
prop('L5','supply vending placeholder',[111.2,291.2,112.6,292.3],2,'lounge')
prop('L6','wall service housing',[98.5,292.9,100.3,293.7],2.2,'lounge')
# Near-wall uprights occupy equipment margins, not the full-width shell doors.
for i,(x,z) in enumerate([(96.2,267),(113.55,275),(96.2,283),(113.55,290),(101.4,262.15),(110.4,262.15)]):prop('U'+str(i+1),'structural upright',[x,z,x+.32,z+.65],3.5,'architecture')
over=[{'id':'H1','kind':'registration canopy','bounds':[106.25,275.75,113.75,278.4],'bottom':2.7,'top':3.35},
{'id':'H2','kind':'north service trunk','bounds':[96.6,262.6,113.4,263.4],'bottom':3.05,'top':3.45},
{'id':'H3','kind':'waiting service trunk','bounds':[96.4,274.5,97.1,283.4],'bottom':3.05,'top':3.45},
{'id':'H4','kind':'lounge service trunk','bounds':[96.6,292.4,113.4,293.1],'bottom':3.05,'top':3.45}]
for i,z in enumerate([267,271.5,287]):over.append({'id':'B'+str(i+1),'kind':'beam','bounds':[96.45,z,113.65,z+.28],'bottom':3.25,'top':3.5})
for i,(x,z) in enumerate([(100,264.5),(107,267.8),(109,276.15),(109,277.8),(99.2,279),(109.2,281.5),(101,287.5),(108,291.5)]):over.append({'id':'F'+str(i+1),'kind':'light housing','bounds':[x,z,x+2.2,z+.24],'bottom':2.95 if z not in [276.15,277.8] else 2.55,'top':3.12 if z not in [276.15,277.8] else 2.7})
# All parts remain cuboids: monitor and noticeboard blocks have no interactive behavior.
details=[{'kind':'counter monitor','bounds':[107.6,276.6,108.5,276.85],'bottom':1.1,'top':1.65}, {'kind':'counter monitor','bounds':[110.4,276.6,111.3,276.85],'bottom':1.1,'top':1.65}, {'kind':'registration sign','bounds':[108,275.8,111.5,276.0],'bottom':2.1,'top':2.6}, {'kind':'noticeboard','bounds':[102.5,283.9,105.2,284.02],'bottom':1.1,'top':2.1}]
checks=[]
for id,name,b in rooms:
 w=b[2]-b[0];h=b[3]-b[1];assert max(w,h)/min(w,h)<2;checks.append(name+': ratio '+format(max(w,h)/min(w,h),'.2f'))
def overlap(a,b):return min(a[2],b[2])-max(a[0],b[0])>1e-6 and min(a[3],b[3])-max(a[1],b[1])>1e-6
wall_boxes=[]
for (x,z),(X,Z) in walls:wall_boxes.append([min(x,X)-(.125 if x==X else 0),min(z,Z)-(.125 if z==Z else 0),max(x,X)+(.125 if x==X else 0),max(z,Z)+(.125 if z==Z else 0)])
for path in [route]+optional:
 for a,b in zip(path,path[1:]):
  assert a[0]==b[0] or a[1]==b[1]
  ribbon=[min(a[0],b[0])-1.5,min(a[1],b[1])-1.5,max(a[0],b[0])+1.5,max(a[1],b[1])+1.5]
  for p in props:assert not overlap(ribbon,p['bounds']),(a,b,p['id'])
  for w in wall_boxes:assert not overlap(ribbon,w),(a,b,w)
checks.append('All drawn floor paths reserve 3 m clear ribbons through 4 m new openings.')
for i,a in enumerate(props):
 b=a['bounds'];assert bounds[0]<=b[0]<b[2]<=bounds[2] and bounds[1]<=b[1]<b[3]<=bounds[3]
 for other in props[i+1:]:assert not overlap(b,other['bounds']),(a['id'],other['id'])
checks.append('Floor-object bounds and separation checked; at least 1 m wall return beyond the screening frame.')
assert 276-.125-274-.25>=1

# Paper work only: preserve current map identity as a traceable baseline.
import hashlib
meta={'revision':'F-02','status':'BUILT - APPROVED F-02 / LAYOUT 07','built_layout':'07','baseline_layout':'06','baseline_map_sha256':'d52b1691839324628b713be998456d5393febba39741fdee319a1b89c899f446','bounds':bounds,'ceiling':3.5,'rooms':rooms,'walls':walls,'main_route':route,'optional_routes':optional,'floor_objects':props,'overhead_objects':over,'detail_blocks':details,'candidate_items':[{'at':[108.1,282.8],'intent':'possible optional pickup on staff back counter; no item type/count assigned'},{'at':[111.6,291.7],'intent':'possible cabinet pickup in window lounge; no item type/count assigned'}],'checks':checks,'unchanged':['shell portals','main A1 route','screening/office/staff-prep rooms','A2/A8 and other departments','keys and gates'],'notes':['Cuboid silhouette/placement pass only. No fine paneling, final art or populated encounters.','All four functional bays retain floor 0 and ceiling 3.5 m; canopies/services create local lower overhead planes.','No return catwalk is added in this proposal; record it as a later route-planning principle.']}
(OUT/'freight-registration-plan.json').write_text(json.dumps(meta,indent=2)+'\n')
# Vector plan and cuboid assembly elevation; never a rendered-game claim.
s=[]
def text(x,y,t,size=17,color='ink',weight=400,anchor='start'):s.append(f'<text x="{x:g}" y="{y:g}" fill="{C.get(color,color)}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(t))}</text>')
def rect(x,y,w,h,fill,stroke='none',sw=1,dash=''):s.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def line(pts,color,width=2,dash='',arrow=False):s.append('<polyline points="'+' '.join(f'{x:g},{y:g}' for x,y in pts)+f'" fill="none" stroke="{C.get(color,color)}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
s.append('<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="1280" viewBox="0 0 1700 1280"><title>Red Breach F-02 Registration Composition</title><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0L7 3.5L0 7Z" fill="#79e0b8"/></marker></defs>')
rect(0,0,1700,1280,'bg');s.append('<g font-family="Segoe UI,Arial,sans-serif">')
text(38,48,'RED BREACH / A1 REGISTRATION / F-02',29,weight=700)
text(38,80,'BUILT / LAYOUT 07  |  Approved functional bays + complete cuboid composition  |  Walkthrough ready',18,'muted')
rect(35,110,655,1010,'panel');text(57,146,'GROUND PLAN / EXISTING RECEPTION ENVELOPE',20,weight=700)
ox,oy,scale=150,185,24
p=lambda x,z:(ox+(x-bounds[0])*scale,oy+(z-bounds[1])*scale)
def footprint(b,color,stroke='none',sw=1,dash=''):
 x,y=p(b[0],b[1]);rect(x,y,(b[2]-b[0])*scale,(b[3]-b[1])*scale,color,stroke,sw,dash)
def pline(pts,*a,**kw):line([p(*v) for v in pts],*a,**kw)
for id,name,b in rooms:footprint(b,'room')
for x in range(98,115,2):pline([[x,262],[x,294]],'#3c505d',.6)
for z in range(262,295,2):pline([[bounds[0],z],[114,z]],'#3c505d',.6)
footprint(bounds,'none','wall',4)
# Existing main thresholds: east 6 m; west 4 m.
pline([[114,267],[114,273]],'room',7);pline([[114,267],[114,273]],'route',2)
pline([[96.125,270],[96.125,274]],'room',7);pline([[96.125,270],[96.125,274]],'route',2)
for a,b in walls:pline([a,b],'wall',6)
for ob in over:
 if ob['kind']=='light housing':footprint(ob['bounds'],'light')
 else:footprint(ob['bounds'],'none','over',1.5,'6 4')
for ob in props:
 footprint(ob['bounds'],'prop','#b5c6d2',.7);b=ob['bounds'];x,y=p((b[0]+b[2])/2,(b[1]+b[3])/2)
 if ob['group']!='architecture':text(x,y+4,ob['id'],10,'bg',700,'middle')
for path in optional:pline(path,'route',2,'6 4',True)
pline(route,'route',3,arrow=True)
for x,z,id in [(103,269,'01'),(99,282,'02'),(110,281.4,'03'),(105,288,'04')]:
 xx,yy=p(x,z);rect(xx-17,yy-14,34,24,'panel');text(xx,yy+4,id,17,'ink',700,'middle')
pline([[102,294],[110,294]],'window',6)
for x,z in [(108.1,282.8),(111.6,291.7)]:
 xx,yy=p(x,z);s.append(f'<circle cx="{xx:g}" cy="{yy:g}" r="7" fill="{C["item"]}"/>')
text(600,p(114,270)[1]-18,'FROM HUB',13,'route',700)
text(132,p(96,272)[1]-15,'TO SCREENING',12,'route',700,'end')
text(360,975,'Existing sealed Mars-view window',15,'window',anchor='middle')
text(80,181,'N ↑',18,'muted',700)
line([(150,989),(270,989)],'ink',3);text(150,1013,'5 m / grid = 2 m',14,'muted')
text(57,1053,'Solid mint: existing onward route. Dashed: optional bays.',15,'muted')
text(57,1079,'Purple dashed: overhead masses. Yellow: light housings.',15,'muted')
text(57,1104,'Orange dots: possible pickup locations, not assigned items.',15,'muted')
# Main visual shows why the counter needs a full vertical composition.
rect(720,110,945,476,'panel');text(744,146,'REGISTRATION ASSEMBLY / FRONT ELEVATION',21,weight=700)
text(744,176,'Every shape is a simple box. Sizes below are our proposal, not measurements of Doom 3.',15,'muted')
ex,fy,k=790,508,94
xy=lambda x,y:(ex+x*k,fy-y*k)
def elev(x,y,w,h,color,stroke='none'):
 a,b=xy(x,y+h);rect(a,b,w*k,h*k,color,stroke)
elev(0,0,8.6,3.5,'room','wall');elev(0,3.05,8.6,.45,'over')
elev(.3,2.7,8,.5,'prop','over');elev(.5,2.54,2,.16,'light');elev(5.8,2.54,2,.16,'light')
elev(2.7,2.1,3.4,.5,'prop');text(*xy(4.4,2.29),'REGISTRATION',16,'ink',700,'middle')
elev(.6,0,.55,3.05,'prop');elev(7.7,0,.55,3.05,'prop')
elev(.85,0,6.9,1.1,'prop','ink');elev(.65,1.02,7.3,.12,'wall');elev(2,1.14,.9,.55,'prop','ink');elev(5.1,1.14,.9,.55,'prop','ink')
# Human scale marker, diagrammatic only.
elev(8.05,0,.32,1.75,'route')
text(1535,516,'1.75 m',13,'route');text(744,550,'Counter 1.1 m · canopy underside 2.7 m · room ceiling 3.5 m',17,'muted')
# Four functional zones and authoring responsibilities.
rect(720,610,945,510,'panel');text(744,648,'SMALLER SPACES, COMPLETE LAYERS',21,weight=700)
for i,(id,name,b) in enumerate(rooms):
 w,h=b[2]-b[0],b[3]-b[1];yy=683+i*34
 text(745,yy,id+'  '+name,17);text(1270,yy,f'{w:.1f} × {h:.1f} m',17,'muted');text(1505,yy,f'{max(w,h)/min(w,h):.2f}:1',17,'route')
text(744,845,'Entry: kiosks, equipment banks, uprights, beams and real light housings.',17)
text(744,875,'Desk: three counter blocks, chairs, screens, sign, canopy and task lights.',17)
text(744,905,'Waiting + lounge: seat groups, queue rail, cabinets and wall services.',17)
text(744,950,'AUTHORING SPLIT',17,'wall',700)
text(744,980,'TrenchBroom: room shell, partitions, landings and route-defining structure.',16,'muted')
text(744,1008,'Godot prop scenes: reusable cube assemblies with simple collision.',16,'muted')
text(744,1036,'Blender later: replace prop visuals inside those scenes; keep placement.',16,'muted')
text(744,1080,'Readable retreat space stays clear. Detail density lives around it.',17,'route')
# Route-return idea remains a separate future diagram, not an implied connection.
rect(35,1140,1630,106,'panel')
text(58,1172,'LATER LAYOUT TOOL: SEE A PLACE → TRAVEL THROUGH OTHER ROOMS → RETURN ABOVE IT',19,weight=700)
text(58,1204,'The catwalk has no direct stair from the room below. It reconnects the player visually with earlier space.',17,'muted')
text(58,1230,'Not added to this sample: it needs a reviewed upper route and taller section. Main mission gates remain intact.',16,'muted')
s.append('</g></svg>');(OUT/'freight-registration-plan.svg').write_text('\n'.join(s),encoding='utf-8')
print(json.dumps({'paper_checks':checks,'floor_object_envelopes':len(props),'overhead_envelopes':len(over),'detail_blocks':len(details),'gameplay_files_changed':False}))
