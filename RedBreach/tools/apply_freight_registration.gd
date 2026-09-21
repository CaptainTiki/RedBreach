## One-time authoring of the approved F-02 prop assets and placement scene.
## Normal map rebuilds preserve these saved scenes; they never call this script.
extends SceneTree
const DIR := "res://props/blockout/f02/"
var dark: StandardMaterial3D
var panel: StandardMaterial3D
var screen: StandardMaterial3D
var lamp: StandardMaterial3D
var plan: Dictionary
var generated_assets: Dictionary = {}
func _initialize() -> void:call_deferred("run")
func owned(parent: Node,node: Node,owner_root: Node,node_name: String) -> void:
	node.name=node_name;parent.add_child(node);node.owner=owner_root
func metric(path: String,tint: Color) -> StandardMaterial3D:
	var m:=StandardMaterial3D.new();m.albedo_texture=load("res://textures/greybox/"+path+".png");m.albedo_color=tint
	m.uv1_triplanar=true;m.uv1_scale=Vector3.ONE;m.roughness=0.85;m.texture_filter=BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	return m
func glow(color: Color,energy: float) -> StandardMaterial3D:
	var m:=StandardMaterial3D.new();m.albedo_color=color;m.emission_enabled=true;m.emission=color;m.emission_energy_multiplier=energy
	return m
func assembly(name_text: String) -> Node3D:
	var node:=Node3D.new();node.name=name_text
	owned(node,Node3D.new(),node,"Visual")
	owned(node,Node3D.new(),node,"Lights")
	return node
func part(node: Node3D,name_text: String,lo: Vector3,hi: Vector3,material: Material,solid:=true) -> void:
	var mesh:=BoxMesh.new();mesh.size=hi-lo
	var visual:=MeshInstance3D.new();visual.mesh=mesh;visual.material_override=material;visual.position=(lo+hi)*0.5
	owned(node.get_node("Visual"),visual,node,name_text)
	if solid:
		if not node.has_node("Collision"):owned(node,StaticBody3D.new(),node,"Collision")
		var shape:=BoxShape3D.new();shape.size=hi-lo
		var collision:=CollisionShape3D.new();collision.shape=shape;collision.position=visual.position
		owned(node.get_node("Collision"),collision,node,name_text)
func text_sign(node: Node3D,text: String,position: Vector3,pixel_size: float) -> void:
	var label:=Label3D.new();label.text=text;label.position=position;label.font_size=36;label.pixel_size=pixel_size;label.outline_size=4;label.modulate=Color(0.8,0.94,0.94);label.rotation.y=PI
	owned(node.get_node("Visual"),label,node,"SignText")
func chair(node: Node3D,origin: Vector3,size: Vector3,prefix: String) -> void:
	part(node,prefix+"Seat",origin+Vector3(0,0.39,0),origin+Vector3(size.x,0.48,size.z),panel,false)
	part(node,prefix+"Back",origin+Vector3(0,0.48,size.z-0.09),origin+size,panel,false)
	for x in [0.05,size.x-0.11]:
		for z in [0.05,size.z-0.11]:part(node,prefix+"Leg",origin+Vector3(x,0,z),origin+Vector3(x+0.06,0.39,z+0.06),dark,false)
func fixture(node: Node3D,origin: Vector3,size: Vector3,prefix: String) -> void:
	part(node,prefix+"Housing",origin+Vector3(0,0.03,0),origin+size,dark)
	part(node,prefix+"Diffuser",origin+Vector3(0.09,0,0.025),origin+Vector3(size.x-0.09,0.03,size.z-0.025),lamp,false)
	var light:=OmniLight3D.new();light.position=origin+Vector3(size.x/2,-0.2,size.z/2);light.omni_range=10;light.omni_attenuation=1.1;light.light_energy=1.35;light.light_color=Color(1,0.88,0.68)
	owned(node.get_node("Lights"),light,node,prefix+"Light")
func solid_shape(node: Node3D,kind: String,lo: Vector3,size: Vector3,prefix: String) -> void:
	var hi:=lo+size
	if kind.contains("chair"):
		chair(node,lo,size,prefix);return
	if kind.contains("seats"):
		# A single simple blocker; individual seats are visual boxes, not floor clutter.
		var along_x:=size.x>size.z
		var count:=maxi(1,floori(maxf(size.x,size.z)/0.85))
		for i in count:
			var start:=lo;var end:=hi
			if along_x:start.x+=i*size.x/count+0.035;end.x=lo.x+(i+1)*size.x/count-0.035
			else:start.z+=i*size.z/count+0.035;end.z=lo.z+(i+1)*size.z/count-0.035
			part(node,prefix+"Seat",Vector3(start.x,lo.y+0.4,start.z),Vector3(end.x,lo.y+0.5,end.z),panel,false)
			if along_x:part(node,prefix+"Back",Vector3(start.x,lo.y+0.5,hi.z-0.12),Vector3(end.x,hi.y,hi.z),dark,false)
			else:part(node,prefix+"Back",Vector3(lo.x,lo.y+0.5,start.z),Vector3(lo.x+0.12,hi.y,end.z),dark,false)
		part(node,prefix+"Pedestal",lo+Vector3(0.12,0,0.12),Vector3(hi.x-0.12,lo.y+0.4,hi.z-0.12),dark,false)
		if not node.has_node("Collision"):owned(node,StaticBody3D.new(),node,"Collision")
		var shape:=BoxShape3D.new();shape.size=size;var col:=CollisionShape3D.new();col.shape=shape;col.position=lo+size/2;owned(node.get_node("Collision"),col,node,prefix)
	elif kind=="queue rail":
		part(node,prefix+"Top",lo+Vector3(0,size.y-0.08,0),hi,dark)
		for z in [lo.z,hi.z-0.1]:part(node,prefix+"Post",Vector3(lo.x,lo.y,z),Vector3(hi.x,hi.y-0.08,z+0.1),dark)
	elif kind.contains("counter") or kind=="low table":
		part(node,prefix+"Base",lo+Vector3(0.06,0,0.06),hi-Vector3(0.06,0.12,0.06),dark)
		part(node,prefix+"Top",Vector3(lo.x,hi.y-0.12,lo.z),hi,panel)
	elif kind.contains("kiosk") or kind.contains("terminal"):
		part(node,prefix+"Base",lo+Vector3(0.1,0,0.12),Vector3(hi.x-0.1,lo.y+size.y*0.55,hi.z-0.12),dark)
		part(node,prefix+"Housing",Vector3(lo.x,lo.y+size.y*0.55,lo.z+0.025),hi,panel)
		part(node,prefix+"Screen",Vector3(lo.x+0.15,lo.y+size.y*0.68,lo.z),Vector3(hi.x-0.15,hi.y-0.12,lo.z+0.015),screen,false)
	elif kind.contains("cabinet") or kind.contains("housing") or kind.contains("vending"):
		# Face blocks sit ahead of the shell, within the same reserved footprint.
		# Coincident surfaces flicker, even when both are simple placeholder cubes.
		if size.x>=size.z:part(node,prefix+"Shell",lo,hi-Vector3(0,0,0.035),dark)
		else:part(node,prefix+"Shell",lo+Vector3(0.035,0,0),hi,dark)
		if size.x>=size.z:
			var count:=maxi(1,floori(size.x/0.9))
			for i in count:
				var x:=lo.x+i*size.x/count+0.07
				part(node,prefix+"Face",Vector3(x,lo.y+0.15,hi.z-0.02),Vector3(lo.x+(i+1)*size.x/count-0.07,hi.y-0.15,hi.z),panel,false)
		else:
			part(node,prefix+"Face",lo+Vector3(0,0.15,0.1),Vector3(lo.x+0.02,hi.y-0.15,hi.z-0.1),panel,false)
	else:part(node,prefix,lo,hi,dark)
func save_asset(node: Node3D,path: String) -> PackedScene:
	var packed:=PackedScene.new();var err:=packed.pack(node)
	if err==OK:err=ResourceSaver.save(packed,path)
	assert(err==OK,"Could not save "+path)
	return ResourceLoader.load(path,"PackedScene",ResourceLoader.CACHE_MODE_REPLACE)
func asset_for(ob: Dictionary) -> PackedScene:
	var b: Array=ob.bounds
	var lo_y:=float(ob.get("bottom",0));var hi_y:=float(ob.get("top",ob.get("height",0)))
	var size:=Vector3(b[2]-b[0],hi_y-lo_y,b[3]-b[1])
	var filename:=str(ob.kind).replace(" ","_")+"_%0.3f_%0.3f_%0.3f"%[size.x,size.y,size.z]
	filename=filename.replace(".","p")+".tscn"
	if generated_assets.has(filename):return generated_assets[filename]
	if ResourceLoader.exists(DIR+filename) and not "--revise-generated" in OS.get_cmdline_user_args():return load(DIR+filename)
	var node:=assembly("BlockoutProp");node.set_meta("kind",ob.kind);node.set_meta("dimensions_m",size)
	if ob.kind=="light housing":fixture(node,Vector3.ZERO,size,"Fixture")
	else:solid_shape(node,ob.kind,Vector3.ZERO,size,"Part")
	var result:=save_asset(node,DIR+filename);generated_assets[filename]=result;node.free();return result
func run() -> void:
	if not "--apply-f02" in OS.get_cmdline_user_args():push_error("One-time helper requires -- --apply-f02");quit(1);return
	var expected: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://.godot/freight_f02_apply.json"))
	if FileAccess.get_sha256("res://maps/freight_01.map")!=expected.output_sha256:push_error("Map changed after F02; refusing a stale application");quit(1);return
	if ResourceLoader.exists("res://missions/freight/registration_f02.tscn") and not "--revise-generated" in OS.get_cmdline_user_args():push_error("Existing F02 assets require explicit --revise-generated");quit(1);return
	plan=JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json")).registration
	DirAccess.make_dir_recursive_absolute(DIR)
	dark=metric("Dark/texture_01",Color(0.88,0.94,1.0));panel=metric("Dark/texture_06",Color(1.2,1.25,1.3))
	screen=glow(Color(0.1,0.38,0.4),0.6);lamp=glow(Color(1,0.87,0.64),1.4)
	for entry in [[dark,"dark"],[panel,"panel"],[screen,"screen"],[lamp,"lamp"]]:ResourceSaver.save(entry[0],DIR+entry[1]+".tres")
	dark=load(DIR+"dark.tres");panel=load(DIR+"panel.tres");screen=load(DIR+"screen.tres");lamp=load(DIR+"lamp.tres")
	var placement:=Node3D.new();placement.name="RegistrationF02";placement.position=Vector3(96.125-190,0,262-260)
	var objects:=Node3D.new();owned(placement,objects,placement,"Objects")
	var desk:=assembly("RegistrationDesk");var desk_origin:=Vector3(106.125,0,274.125)
	var all: Array=plan.floor_objects.duplicate(true);all.append_array(plan.overhead_objects)
	for ob in all:
		if ob.kind in ["structural upright","beam"]:continue
		var b: Array=ob.bounds;var lo_y:=float(ob.get("bottom",0));var hi_y:=float(ob.get("top",ob.get("height",0)))
		var pos:=Vector3(b[0],lo_y,b[1]);var size:=Vector3(b[2]-b[0],hi_y-lo_y,b[3]-b[1])
		if str(ob.id).begins_with("R") or ob.id in ["H1","F3","F4"]:
			if ob.kind=="light housing":fixture(desk,pos-desk_origin,size,ob.id)
			else:solid_shape(desk,ob.kind,pos-desk_origin,size,ob.id)
		else:
			var instance:=asset_for(ob).instantiate();instance.position=pos-Vector3(96.125,0,262);instance.set_meta("layout_id",ob.id)
			owned(objects,instance,placement,ob.id)
	for i in plan.detail_blocks.size():
		var ob: Dictionary=plan.detail_blocks[i];var b: Array=ob.bounds
		var pos:=Vector3(b[0],ob.bottom,b[1]);var size:=Vector3(b[2]-b[0],ob.top-ob.bottom,b[3]-b[1])
		if ob.kind=="noticeboard":
			var notice:=assembly("Noticeboard");part(notice,"Board",Vector3.ZERO,size,panel,false)
			var instance:=save_asset(notice,DIR+"noticeboard.tscn").instantiate();instance.position=pos-Vector3(96.125,0,262);owned(objects,instance,placement,"Noticeboard");notice.free()
		else:
			part(desk,"Detail"+str(i),pos-desk_origin,pos-desk_origin+size,panel,false)
			if ob.kind=="counter monitor":part(desk,"Display"+str(i),pos-desk_origin+Vector3(0.05,0.05,-0.002),pos-desk_origin+Vector3(size.x-0.05,size.y-0.05,0.014),screen,false)
			if ob.kind=="registration sign":text_sign(desk,"REGISTRATION",pos-desk_origin+Vector3(size.x/2,size.y/2,-0.012),0.008)
	var desk_instance:=save_asset(desk,DIR+"registration_desk.tscn").instantiate();desk_instance.position=desk_origin-Vector3(96.125,0,262);owned(objects,desk_instance,placement,"RegistrationDesk");desk.free()
	# Empty markers are reservations, not active pickups or rewards.
	for i in plan.candidate_items.size():
		var ob: Dictionary=plan.candidate_items[i];var marker:=Marker3D.new();marker.position=Vector3(ob.at[0]-96.125,1.15 if i==0 else 0.8,ob.at[1]-262);marker.set_meta("design_note",ob.intent);owned(placement,marker,placement,"CandidateItem"+str(i+1))
	var packed_placement:=save_asset(placement,"res://missions/freight/registration_f02.tscn");placement.free()
	var mission: Node3D=load("res://missions/freight/freight_blockout.tscn").instantiate();mission.storage_enabled=false;root.add_child(mission);mission.get_node("GymPlayer").set_physics_process(false)
	for path in ["RegistrationF02","FurnishingF01/A1Chair1","FurnishingF01/A1Light01","FurnishingF01/A1Label01"]:
		var node:=mission.get_node_or_null(path)
		if node:node.get_parent().remove_child(node);node.free()
	var fresh:=packed_placement.instantiate();owned(mission,fresh,mission,"RegistrationF02")
	mission.storage_enabled=true
	var saved:=PackedScene.new();var err:=saved.pack(mission)
	if err==OK:err=ResourceSaver.save(saved,"res://missions/freight/freight_blockout.tscn")
	print("FREIGHT_F02_PROPS: save=",err," / placements=",fresh.get_node("Objects").get_child_count())
	quit(0 if err==OK else 1)
