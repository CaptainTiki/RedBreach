extends SceneTree
## One-time F04 Screening authoring. Normal rebuilds preserve these saved assets.
const DIR := "res://props/blockout/f04/"
var body_mat: StandardMaterial3D
var surface_mat: StandardMaterial3D
var service_mat: StandardMaterial3D
var fixture_mat: StandardMaterial3D
var screen_mat: StandardMaterial3D
var lamp_mat: StandardMaterial3D
func _initialize() -> void: call_deferred("run")
func owned(parent: Node,node: Node,owner_root: Node,node_name: String) -> void:
	node.name=node_name;parent.add_child(node);node.owner=owner_root
func assembly(node_name: String) -> Node3D:
	var node:=Node3D.new();node.name=node_name
	owned(node,Node3D.new(),node,"Visual")
	return node
func part(node: Node3D,node_name: String,lo: Vector3,hi: Vector3,material: Material) -> void:
	assert(hi.x>lo.x and hi.y>lo.y and hi.z>lo.z,node_name)
	var mesh:=BoxMesh.new();mesh.size=hi-lo
	var visual:=MeshInstance3D.new();visual.mesh=mesh;visual.material_override=material;visual.position=(lo+hi)*0.5
	owned(node.get_node("Visual"),visual,node,node_name)
func collision(node: Node3D,node_name: String,lo: Vector3,hi: Vector3) -> void:
	if not node.has_node("Collision"):owned(node,StaticBody3D.new(),node,"Collision")
	var shape:=BoxShape3D.new();shape.size=hi-lo
	var col:=CollisionShape3D.new();col.shape=shape;col.position=(lo+hi)*0.5
	owned(node.get_node("Collision"),col,node,node_name)
func label(node: Node3D,node_name: String,value: String,at: Vector3,yaw: float,pixel_size:=0.004) -> void:
	var sign:=Label3D.new();sign.text=value;sign.font_size=40;sign.pixel_size=pixel_size;sign.position=at;sign.rotation.y=yaw;sign.modulate=Color(0.82,0.92,0.91);sign.outline_size=0
	owned(node,sign,node,node_name)
func save_asset(node: Node3D,path: String) -> PackedScene:
	var packed:=PackedScene.new();var err:=packed.pack(node)
	if err==OK:err=ResourceSaver.save(packed,path)
	assert(err==OK,"Could not save "+path)
	return ResourceLoader.load(path,"PackedScene",ResourceLoader.CACHE_MODE_REPLACE)
func monitor(node: Node3D,at: Vector3) -> void:
	part(node,"MonitorFoot",at,at+Vector3(0.4,0.04,0.25),fixture_mat)
	part(node,"MonitorStand",at+Vector3(0.17,0.04,0.07),at+Vector3(0.23,0.2,0.15),fixture_mat)
	part(node,"MonitorBody",at+Vector3(-0.13,0.17,0.02),at+Vector3(0.53,0.58,0.13),fixture_mat)
	part(node,"MonitorDisplay",at+Vector3(-0.08,0.21,0.131),at+Vector3(0.48,0.54,0.14),screen_mat)
func cabinet(node: Node3D,size: Vector3,facing: String,air: bool) -> void:
	var lo:=Vector3.ZERO;var hi:=size
	if facing=="east":hi.x-=0.04
	elif facing=="west":lo.x+=0.04
	elif facing=="south":hi.z-=0.04
	else:lo.z+=0.04
	part(node,"Housing",lo,hi,service_mat if air else body_mat)
	var along_x:=facing in ["north","south"]
	var span:=size.x if along_x else size.z
	var bays:=maxi(1,floori(span/0.8))
	for i in bays:
		var a:=Vector3(0.06,0.12,0.06);var b:=size-Vector3(0.06,0.12,0.06)
		if along_x:a.x=i*span/bays+0.06;b.x=(i+1)*span/bays-0.06
		else:a.z=i*span/bays+0.06;b.z=(i+1)*span/bays-0.06
		if facing=="east":a.x=size.x-0.025;b.x=size.x
		elif facing=="west":a.x=0;b.x=0.025
		elif facing=="south":a.z=size.z-0.025;b.z=size.z
		else:a.z=0;b.z=0.025
		if air:
			for row in 6:
				var aa:=a;var bb:=b;aa.y=0.22+row*0.31;bb.y=aa.y+0.15
				part(node,"AirSlot",aa,bb,fixture_mat)
		else:
			part(node,"DoorPanel",a,b,surface_mat)
			var aa:=a;var bb:=b;aa.y=0.95;bb.y=1.23
			if along_x:aa.x=b.x-0.13;bb.x=b.x-0.07
			else:aa.z=b.z-0.13;bb.z=b.z-0.07
			if facing=="east":aa.x=b.x+0.002;bb.x=b.x+0.012
			elif facing=="west":aa.x=a.x-0.012;bb.x=a.x-0.002
			elif facing=="south":aa.z=b.z+0.002;bb.z=b.z+0.012
			else:aa.z=a.z-0.012;bb.z=a.z-0.002
			part(node,"Handle",aa,bb,fixture_mat)
	collision(node,"Envelope",Vector3.ZERO,size)
func build_prop(ob: Dictionary) -> Node3D:
	var b: Array=ob.bounds;var size:=Vector3(b[2]-b[0],ob.top-ob.bottom,b[3]-b[1]);var id:=str(ob.id)
	var node:=assembly("ScreeningProp");node.set_meta("layout_id",id);node.set_meta("kind",ob.kind);node.set_meta("dimensions_m",size)
	if id=="s3":
		part(node,"Seat",Vector3(0,0.39,0),Vector3(size.x,0.48,size.z),surface_mat)
		part(node,"Back",Vector3(0,0.48,size.z-0.09),size,surface_mat)
		for x in [0.05,size.x-0.11]:
			for z in [0.05,size.z-0.11]:part(node,"Leg",Vector3(x,0,z),Vector3(x+0.06,0.39,z+0.06),fixture_mat)
	elif id in ["S3","S4"]:
		part(node,"Worktop",Vector3(0,size.y-0.1,0),size,surface_mat)
		part(node,"DrawerPedestal",Vector3(0.08,0,0.08),Vector3(0.7,size.y-0.1,size.z-0.08),body_mat)
		part(node,"FarSupport",Vector3(size.x-0.2,0,0.08),Vector3(size.x-0.08,size.y-0.1,size.z-0.08),body_mat)
		part(node,"Backboard",Vector3(0.2,0.25,0.08),Vector3(size.x-0.2,size.y-0.12,0.16),body_mat)
		monitor(node,Vector3(size.x*0.6,size.y,0.12))
		part(node,"Keyboard",Vector3(size.x*.48,size.y,0.55),Vector3(size.x*.75,size.y+0.04,0.77),fixture_mat)
		collision(node,"Envelope",Vector3.ZERO,size)
	elif id=="S2":
		part(node,"ConveyorBed",Vector3(0,0.7,0.1),Vector3(5,0.94,1.65),body_mat)
		part(node,"Belt",Vector3(0.02,0.94,0.22),Vector3(4.98,0.98,1.53),fixture_mat)
		for x in [0.12,4.5]:
			for z in [0.12,1.38]:part(node,"Leg",Vector3(x,0,z),Vector3(x+0.3,0.7,z+0.22),service_mat)
		part(node,"ScannerNorth",Vector3(1.7,0,0),Vector3(3.6,2.4,0.3),body_mat)
		part(node,"ScannerSouth",Vector3(1.7,0,1.45),Vector3(3.6,2.4,1.75),body_mat)
		part(node,"ScannerTop",Vector3(1.7,2.03,0.3),Vector3(3.6,2.4,1.45),body_mat)
		part(node,"Tray",Vector3(.4,.98,.45),Vector3(1.15,1.12,1.3),surface_mat)
		part(node,"Controls",Vector3(2.0,1.25,1.73),Vector3(2.9,1.6,1.749),screen_mat)
		collision(node,"Envelope",Vector3.ZERO,size)
	elif id in ["S5","S6","S7","S8"]:
		cabinet(node,size,{"S5":"north","S6":"south","S7":"west","S8":"east"}[id],id=="S7")
	elif id=="S9":
		part(node,"Housing",Vector3(.035,0,0),size,fixture_mat)
		part(node,"Readout",Vector3(0,.06,.06),Vector3(.025,size.y-.06,size.z-.06),screen_mat)
	elif ob.kind=="light":
		part(node,"Housing",Vector3.ZERO,size,fixture_mat)
		part(node,"Diffuser",Vector3(.08,-.012,.025),Vector3(size.x-.08,-.002,size.z-.025),lamp_mat)
		var light:=OmniLight3D.new();light.position=Vector3(size.x/2,-.18,size.z/2);light.light_color=Color(1,.9,.76);light.light_energy=.65;light.omni_range=7;light.shadow_enabled=true
		owned(node,light,node,"TaskLight");collision(node,"Envelope",Vector3.ZERO,size)
	else:
		part(node,"ServiceTrunk",Vector3.ZERO,size-Vector3(0,0,.035),service_mat)
		for i in 8:
			var x:=.3+i*1.5
			part(node,"VentBand",Vector3(x,.08,size.z-.025),Vector3(x+.7,size.y-.08,size.z),fixture_mat)
		collision(node,"Envelope",Vector3.ZERO,size)
	return node
func run() -> void:
	if not "--apply-f04" in OS.get_cmdline_user_args():push_error("Requires -- --apply-f04");quit(1);return
	var report: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://.godot/freight_f04_apply.json"))
	if FileAccess.get_sha256("res://maps/freight_01.map")!=report.output_sha256 or FileAccess.get_sha256("res://missions/freight/freight_blockout.tscn")!=report.original_scene_sha256:push_error("Source changed after F04 checkpoint; inspect before retrying");quit(1);return
	if ResourceLoader.exists("res://missions/freight/screening_f04.tscn"):push_error("F04 already authored; preserve subsequent edits");quit(1);return
	DirAccess.make_dir_recursive_absolute(DIR)
	body_mat=load("res://props/blockout/materials/registration_block.tres");surface_mat=load("res://props/blockout/materials/registration_surface.tres");service_mat=load("res://props/blockout/materials/registration_service.tres");fixture_mat=load("res://props/blockout/materials/registration_fixture.tres");screen_mat=load("res://props/blockout/f02/screen.tres");lamp_mat=load("res://props/blockout/f02/lamp.tres")
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json")).screening
	var placement:=Node3D.new();placement.name="ScreeningF04";placement.position=Vector3(82.125-190,0,262-260)
	owned(placement,Node3D.new(),placement,"Objects")
	var rows: Array=plan.floor_props.duplicate(true);rows.append_array(plan.overhead)
	for ob in rows:
		if str(ob.id).begins_with("R") or ob.id in ["S1a","S1b","S1h"]:continue
		var node:=build_prop(ob);var packed:=save_asset(node,DIR+("chair_s3" if ob.id=="s3" else str(ob.id).to_lower())+".tscn");node.free()
		var instance:=packed.instantiate();var b: Array=ob.bounds;instance.position=Vector3(b[0]-82.125,ob.bottom,b[1]-262)
		owned(placement.get_node("Objects"),instance,placement,str(ob.id))
	var arch:=assembly("ScanArch")
	for bounds in [[Vector3.ZERO,Vector3(1,2.8,.75)],[Vector3(0,0,3.75),Vector3(1,2.8,4.5)],[Vector3(0,2.8,0),Vector3(1,3.15,4.5)]]:
		part(arch,"Frame",bounds[0],bounds[1],body_mat);collision(arch,"Frame",bounds[0],bounds[1])
	for z in [.18,3.98]:part(arch,"StatusStrip",Vector3(1.001,.7,z),Vector3(1.013,2.15,z+.2),screen_mat)
	label(arch,"ScreeningSign","SCREENING",Vector3(1.015,2.98,2.25),PI/2,.0045)
	var packed_arch:=save_asset(arch,DIR+"scan_arch.tscn");arch.free()
	var instance:=packed_arch.instantiate();instance.position=Vector3(90.25-82.125,0,269.75-262);owned(placement.get_node("Objects"),instance,placement,"ScanArch")
	label(placement,"ExitSign","STAFF PREPARATION",Vector3(88-82.125,3.35,275.735-262),PI,.0035)
	var packed_placement:=save_asset(placement,"res://missions/freight/screening_f04.tscn");placement.free()
	var mission: Node3D=load("res://missions/freight/freight_blockout.tscn").instantiate();mission.storage_enabled=false;root.add_child(mission);mission.get_node("GymPlayer").set_physics_process(false)
	for path in ["FurnishingF01/A1Chair5","FurnishingF01/A1Light02","FurnishingF01/A1Label02"]:
		var node:=mission.get_node(path);node.get_parent().remove_child(node);node.free()
	var fresh:=packed_placement.instantiate();owned(mission,fresh,mission,"ScreeningF04")
	mission.storage_enabled=true
	var saved:=PackedScene.new();var err:=saved.pack(mission)
	if err==OK:err=ResourceSaver.save(saved,"res://missions/freight/freight_blockout.tscn")
	print("FREIGHT_F04_PROPS: save=",err," / placements=",fresh.get_node("Objects").get_child_count())
	quit(0 if err==OK else 1)
