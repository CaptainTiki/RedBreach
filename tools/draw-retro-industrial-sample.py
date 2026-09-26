"""Draw a paper proposal only; never edits a map or Godot scene."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
im = Image.new('RGB', (1400, 1050), '#101b25')
d = ImageDraw.Draw(im)
def font(n):
    return ImageFont.truetype('arial.ttf', n)
def text(x,y,s,n=22,c='#e8eef2'):
    d.text((x,y),s,font=font(n),fill=c)
def line(points,c='#93a8b6',w=3): d.line(points,fill=c,width=w)
text(45,28,'R-01 / RETRO INDUSTRIAL',36)
text(45,77,'Paper proposal — shape and palette only; not a Godot render',22,'#e8bd77')
text(45,133,'01  CORRIDOR SECTION',26)
# Section drawn at 80 px/metre. Floor 6m, ceiling 3m, height 4m.
poly=[(70,525),(550,525),(430,205),(190,205)]
d.polygon(poly,fill='#283c47'); line(poly+[poly[0]],'#b9c8ce',5)
# Conservative reserved rib envelope.
line([(90,525),(205,225),(415,225),(530,525)],'#e8bd77',5)
line([(170,520),(170,365),(450,365),(450,520)],'#79bfb1',2)
text(192,280,'3.5 m protected',18,'#9ed5c8')
text(215,306,'walking ribbon',18,'#9ed5c8')
# Human scale marker 1.8m.
d.ellipse((296,381,322,407),fill='#dce4e7')
line([(309,409),(309,474),(290,520)],'#dce4e7',5)
line([(309,474),(328,520)],'#dce4e7',5)
line([(287,442),(309,419),(331,442)],'#dce4e7',5)
text(245,167,'3 m ceiling',20)
text(235,540,'6 m floor',20)
text(566,349,'4 m',20)
text(65,589,'Continuous sloping walls. Flat ceiling.',20)
text(65,621,'Amber line = rib clearance envelope.',18,'#e8bd77')
text(710,133,'02  TOP-DOWN PLAN',26)
# Room 10x10m at 27 px/m, corridor 6x12, threshold .5.
cx=975; y=185; s=27
room=[(880.5,185),(1069.5,185),(1110,225.5),(1110,414.5),(1069.5,455),(880.5,455),(840,414.5),(840,225.5)]
d.polygon(room,fill='#283c47');line(room+[room[0]],'#b9c8ce',4)
d.rectangle((894,468.5,1056,792.5),fill='#283c47',outline='#b9c8ce',width=4)
d.rectangle((934.5,451,1015.5,474),fill='#283c47')
line([(934.5,455),(934.5,468.5)],'#e8bd77',5)
line([(1015.5,455),(1015.5,468.5)],'#e8bd77',5)
for yy in [522.5,630.5,738.5]:
    line([(895,yy),(913,yy)],'#e8bd77',7)
    line([(1037,yy),(1055,yy)],'#e8bd77',7)
d.rectangle((934.5,266,1015.5,374),fill='#657d72',outline='#a6b8ad',width=3)
text(942,278,'PUMP',17);text(943,308,'3 x 4',17)
text(940,335,'metres',15)
text(856,202,'10 x 10 m / ceiling 5 m',17)
text(1125,300,'1.5 m',18);text(1125,329,'corner clips',18)
text(1081,476,'3 m portal',18)
text(915,572,'12 m',22);text(914,603,'corridor',19)
text(735,670,'Ribs at',18);text(735,697,'4 m pitch',18)
text(902,809,'ENTRY / RETURN',18,'#9ed5c8')
text(45,697,'03  MATERIAL ROLES',26)
for x,col,label in [(50,'#6c8277','Painted panel'),(250,'#a7afa9','Steel frame'),(450,'#343c41','Dark floor')]:
    d.rounded_rectangle((x,747,x+170,823),radius=3,fill=col)
    text(x,839,label,18)
text(50,883,'Clean / grimy: same panel and light,',19)
text(50,912,'different prepared surface maps.',19)
text(50,970,'REVIEW TARGET: angled silhouette + substantial structure + restrained surface detail',22,'#e8bd77')
out=ROOT/'docs/retro-industrial-sample-plan.png'
im.save(out)
print(out)


