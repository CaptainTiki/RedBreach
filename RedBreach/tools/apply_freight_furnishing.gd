## One-time companion to apply-freight-furnishing.py. Not part of normal rebuilds.
## Saves editable chairs, lighting and the approved sealed window view outside Geometry.
extends SceneTree
var scene: Node3D
var furnishings: Node3D
var dark: StandardMaterial3D
func _initialize() -> void:call_deferred("run")
func world(x: float,y: float,z: float) -> Vector3:return Vector3(x-190,y,z-260)
func attach(parent: Node,node: Node,name_text: String) -> void:
	node.name=name_text
	parent.add_child(node)
	node.owner=scene
func metric(texture: String,tint:=Color.WHITE) -> StandardMaterial3D:
	var m:=StandardMaterial3D.new()
	m.albedo_texture=load("res://textures/greybox/"+texture+".png")
	m.albedo_color=tint
	m.uv1_triplanar=true
	m.uv1_scale=Vector3.ONE
	m.texture_filter=BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	m.roughness=0.85
	return m
func mesh_box(parent: Node,name_text: String,p: Vector3,size: Vector3,m: Material) -> MeshInstance3D:
	var mesh:=BoxMesh.new();mesh.size=size
	var node:=MeshInstance3D.new();node.mesh=mesh;node.material_override=m;node.position=p
	attach(parent,node,name_text)
	return node
func remove_node(path: String) -> void:
	var node:=scene.get_node_or_null(path)
	if node:node.get_parent().remove_child(node);node.free()
func run() -> void:
	if not "--apply-f01" in OS.get_cmdline_user_args():
		push_error("One-time authoring helper: requires explicit -- --apply-f01. Normal rebuilds must not run this script.")
		quit(1)
		return
	scene=load("res://missions/freight/freight_blockout.tscn").instantiate()
	scene.storage_enabled=false
	root.add_child(scene)
	scene.get_node("GymPlayer").set_physics_process(false)
	remove_node("FurnishingF01")
	furnishings=Node3D.new();attach(scene,furnishings,"FurnishingF01")
	dark=metric("Dark/texture_06")
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json")).furnishing
	for key in plan.rooms:
		var data: Dictionary=plan.rooms[key]
		for i in data.props.size():
			var p: Dictionary=data.props[i]
			if p.kind!="chair":continue
			var chair:=Node3D.new();attach(furnishings,chair,str(key)+"Chair"+str(i))
			var b: Array=p.bounds
			chair.position=world((b[0]+b[2])/2,p.floor_y,(b[1]+b[3])/2)
			mesh_box(chair,"Seat",Vector3(0,0.43,0),Vector3(0.58,0.09,0.58),dark)
			mesh_box(chair,"Back",Vector3(0,0.7,0.27),Vector3(0.58,0.4,0.09),dark)
			for x in [-0.23,0.23]:
				for z in [-0.23,0.23]:mesh_box(chair,"Leg",Vector3(x,0.2,z),Vector3(0.06,0.4,0.06),dark)
		remove_node("Labels/Room"+str(key))
		remove_node("Lights/Room"+str(key))
		for room in data.rooms:
			var b: Array=room[2]
			var p:=world((b[0]+b[2])/2,float(data.floor)+float(room[3])-0.65,(b[1]+b[3])/2)
			var light:=OmniLight3D.new();light.position=p;light.omni_range=25;light.omni_attenuation=0.5;light.light_energy=1.2;light.light_color=Color(0.8,0.87,0.95)
			attach(furnishings,light,str(key)+"Light"+str(room[0]))
			var label:=Label3D.new();label.text=str(key)+" / "+str(room[1]).to_upper();label.font_size=34;label.pixel_size=0.009;label.outline_size=5;label.billboard=BaseMaterial3D.BILLBOARD_ENABLED
			label.modulate=Color(0.8,0.9,0.95);label.position=world(room[4][0],float(data.floor)+2.65,room[4][1])
			attach(furnishings,label,str(key)+"Label"+str(room[0]))
	remove_node("Lights/IntakeEast");remove_node("Lights/InspectionNorth");remove_node("Labels/MezzA2")
	var deck_light:=OmniLight3D.new();deck_light.position=world(48,2.8,235);deck_light.omni_range=23;deck_light.light_energy=1.2
	attach(furnishings,deck_light,"EntryDeckLight")
	# Sealed pressure window: transparent pane blocks bodies/rays. The view contains
	# local depth and parallax but no playable exterior or connection to other rooms.
	var window:=Node3D.new();attach(furnishings,window,"IntakeWindow")
	var glass:=StandardMaterial3D.new();glass.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA;glass.albedo_color=Color(0.5,0.7,0.78,0.1);glass.roughness=0.25
	var pane:=StaticBody3D.new();pane.position=world(106,1.9,294.18);attach(window,pane,"PressurePane")
	mesh_box(pane,"Glass",Vector3.ZERO,Vector3(8,1.8,0.05),glass)
	var collision:=CollisionShape3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(8,1.8,0.08);collision.shape=shape;attach(pane,collision,"CollisionShape3D")
	for x in [102,104.66,107.33,110]:mesh_box(window,"Mullion",world(x,1.9,294.08),Vector3(0.1,1.8,0.16),dark)
	var rust:=metric("Dark/texture_06",Color(0.9,0.42,0.25))
	var sky:=StandardMaterial3D.new();sky.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;sky.albedo_color=Color(0.32,0.16,0.105)
	mesh_box(window,"DistantDust",world(106,2.5,310),Vector3(40,18,0.2),sky)
	mesh_box(window,"WestDust",world(86,2.5,302),Vector3(0.2,18,16),sky)
	mesh_box(window,"EastDust",world(126,2.5,302),Vector3(0.2,18,16),sky)
	mesh_box(window,"Ground",world(106,-0.8,302),Vector3(40,0.3,16),rust)
	for row in [[99.0,304.0,2.6],[105.0,307.0,3.8],[113.0,306.0,2.8],[120.0,305.0,3.0]]:
		var rock:=PrismMesh.new();rock.size=Vector3(7,row[2],4)
		var node:=MeshInstance3D.new();node.mesh=rock;node.material_override=rust;node.position=world(row[0],-0.65+row[2]/2,row[1]);attach(window,node,"LowRidge")
	mesh_box(window,"PlantHousing",world(114,0.8,300),Vector3(2.5,3,3),dark)
	mesh_box(window,"UtilityRun",world(110,0.4,298),Vector3(10,0.35,0.35),dark)
	for x in [105,111,115]:mesh_box(window,"PipeSupport",world(x,-0.1,298),Vector3(0.2,1.2,0.4),dark)
	var light:=OmniLight3D.new();light.position=world(106,5,299);light.omni_range=30;light.light_energy=2;light.light_color=Color(1,0.65,0.4);attach(window,light,"ExteriorLight")
	scene.storage_enabled=true
	var packed:=PackedScene.new();var err:=packed.pack(scene)
	if err==OK:err=ResourceSaver.save(packed,"res://missions/freight/freight_blockout.tscn")
	print("FREIGHT_F01_AUTHORED: save=",err)
	quit(0 if err==OK else 1)
