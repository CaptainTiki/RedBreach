extends SceneTree
## Scoped one-time F-03 authoring; normal rebuilds preserve these assets.
const DIR := "res://props/blockout/f03/"
var dark: StandardMaterial3D
var panel: StandardMaterial3D
var screen: StandardMaterial3D
var plan: Dictionary
var assets: Dictionary = {}
func _initialize() -> void:call_deferred("run")
func owned(parent: Node,node: Node,owner_root: Node,node_name: String) -> void:
	node.name=node_name;parent.add_child(node);node.owner=owner_root
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
func chair(node: Node3D,origin: Vector3,size: Vector3,prefix: String) -> void:
	part(node,prefix+"Seat",origin+Vector3(0,0.39,0),origin+Vector3(size.x,0.48,size.z),panel,false)
	part(node,prefix+"Back",origin+Vector3(0,0.48,size.z-0.09),origin+size,panel,false)
	for x in [0.05,size.x-0.11]:
		for z in [0.05,size.z-0.11]:part(node,prefix+"Leg",origin+Vector3(x,0,z),origin+Vector3(x+0.06,0.39,z+0.06),dark,false)
func save_asset(node: Node3D,path: String) -> PackedScene:
	var packed:=PackedScene.new();var err:=packed.pack(node)
	if err==OK:err=ResourceSaver.save(packed,path)
	assert(err==OK,"Could not save "+path)
	return ResourceLoader.load(path,"PackedScene",ResourceLoader.CACHE_MODE_REPLACE)
func collider(node: Node3D,size: Vector3) -> void:
	owned(node,StaticBody3D.new(),node,"Collision")
	var col:=CollisionShape3D.new();var shape:=BoxShape3D.new();shape.size=size;col.shape=shape;col.position=size/2
	owned(node.get_node("Collision"),col,node,"Envelope")
func cabinet(node: Node3D,size: Vector3,facing: String,kind: String) -> void:
	var lo:=Vector3.ZERO;var hi:=size
	if facing=="east":hi.x-=0.035
	elif facing=="west":lo.x+=0.035
	elif facing=="south":hi.z-=0.035
	else:lo.z+=0.035
	part(node,"Housing",lo,hi,dark,false)
	var n:=6 if kind=="air" else (4 if kind=="server" else 3)
	for i in n:
		var y:=0.15+i*(size.y-0.3)/n;var Y:=y+(size.y-0.3)/n-0.065
		var a:=Vector3(0.08,y,0.08);var b:=Vector3(size.x-0.08,Y,size.z-0.08)
		if facing=="east":a.x=size.x-0.02;b.x=size.x
		elif facing=="west":a.x=0;b.x=0.02
		elif facing=="south":a.z=size.z-0.02;b.z=size.z
		else:a.z=0;b.z=0.02
		part(node,"Vent" if kind=="air" else "Drawer",a,b,panel,false)
		if kind=="server":
			a=Vector3(-0.003,y+0.06,0.15);b=Vector3(0.01,y+0.11,0.38)
			part(node,"Status",a,b,screen,false)
func asset_for(ob: Dictionary) -> PackedScene:
	var b: Array=ob.bounds;var size:=Vector3(b[2]-b[0],ob.top-ob.bottom,b[3]-b[1])
	var id:=str(ob.id);var key:=id
	if id.begins_with("C"):key="chair"
	if assets.has(key):return assets[key]
	var node:=assembly("OfficeProp");node.set_meta("kind",ob.kind);node.set_meta("dimensions_m",size)
	if id.begins_with("C"):
		chair(node,Vector3.ZERO,size,"Chair")
	elif id.begins_with("D"):
		part(node,"Worktop",Vector3(0,size.y-0.1,0),size,panel,false)
		part(node,"DrawerPedestal",Vector3(0.1,0,0.08),Vector3(0.65,size.y-0.1,size.z-0.08),dark,false)
		for z in [0.08,size.z-0.18]:part(node,"Leg",Vector3(size.x-0.2,0,z),Vector3(size.x-0.1,size.y-0.1,z+0.1),dark,false)
		collider(node,size)
	elif id=="S1":
		for i in 2:
			var rack:=assembly("ServerRack");cabinet(rack,Vector3(size.x,size.y,1.45),"west","server")
			for child in rack.get_node("Visual").get_children():
				child.owner=null;rack.get_node("Visual").remove_child(child);child.position.z+=i*1.65;owned(node.get_node("Visual"),child,node,"Rack"+str(i)+str(child.name))
			rack.free()
		collider(node,size)
	elif id.begins_with("F") or id.begins_with("A"):
		var facing: String={"F1":"east","F2":"south","F3":"west","A1":"east","A2":"north"}[id]
		cabinet(node,size,facing,"air" if id.begins_with("A") else "filing");collider(node,size)
	elif id.begins_with("M"):
		part(node,"Foot",Vector3(0.15,0,0.04),Vector3(size.x-0.15,0.04,size.z-0.01),dark,false)
		part(node,"Stand",Vector3(size.x/2-0.04,0.04,0.09),Vector3(size.x/2+0.04,0.18,0.17),dark,false)
		part(node,"Display",Vector3(0,0.14,0.05),Vector3(size.x,size.y,size.z-0.03),panel,false)
		part(node,"Screen",Vector3(0.04,0.18,size.z-0.025),Vector3(size.x-0.04,size.y-0.04,size.z-0.01),screen,false)
	else:
		part(node,"Housing",Vector3.ZERO,size,panel,false)
		if id=="T1":part(node,"Readout",Vector3(0.05,0.05,size.z+0.002),Vector3(size.x-0.05,size.y-0.05,size.z+0.012),screen,false)
		else:part(node,"Readout",Vector3(-0.012,0.05,0.05),Vector3(-0.002,size.y-0.05,size.z-0.05),screen,false)
	var packed:=save_asset(node,DIR+key.to_lower()+".tscn");assets[key]=packed;node.free();return packed
func run() -> void:
	if not "--apply-f03" in OS.get_cmdline_user_args():push_error("Requires -- --apply-f03");quit(1);return
	var state: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://.godot/freight_f03_apply.json"))
	if FileAccess.get_sha256("res://maps/freight_01.map")!=state.output_sha256:push_error("Source map changed after F03 application");quit(1);return
	if FileAccess.get_sha256("res://missions/freight/registration_f02.tscn")!=state.original_registration_sha256:push_error("Registration scene changed; refusing to replace edits");quit(1);return
	plan=JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json")).registration_recess
	DirAccess.make_dir_recursive_absolute(DIR)
	dark=load("res://props/blockout/f02/dark.tres");panel=load("res://props/blockout/f02/panel.tres");screen=load("res://props/blockout/f02/screen.tres")
	var placement: Node3D=load("res://missions/freight/registration_f02.tscn").instantiate()
	for id in ["L1","L2","L3","L4","L5","L6"]:
		var node:=placement.get_node("Objects/"+id);node.get_parent().remove_child(node);node.free()
	for ob in plan.office_props:
		var instance:=asset_for(ob).instantiate();var b: Array=ob.bounds
		instance.position=Vector3(b[0]-96.125,ob.bottom,b[1]-262);instance.set_meta("layout_id","O_"+str(ob.id))
		owned(placement.get_node("Objects"),instance,placement,"O_"+str(ob.id))
	var door: Node3D=load("res://interaction/sliding_door_wide.tscn").instantiate()
	door.position=Vector3(106-96.125,0,280-262);door.rotation.y=PI/2;owned(placement,door,placement,"StaffDoor")
	placement.get_node("CandidateItem2").position=Vector3(109.8-96.125,0.78,287.5-262)
	placement.get_node("CandidateItem2").set_meta("design_note","Possible later item on registration office desk; no active pickup")
	var packed:=PackedScene.new();var err:=packed.pack(placement)
	if err==OK:err=ResourceSaver.save(packed,"res://missions/freight/registration_f02.tscn")
	print("FREIGHT_F03_PROPS: save=",err," / placements=",placement.get_node("Objects").get_child_count())
	placement.free();quit(0 if err==OK else 1)
