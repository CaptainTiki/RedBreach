extends "res://tools/apply_freight_screening.gd"
## One-time Route A authoring. Ordinary rebuilds preserve these external scene instances.
const ASSET_DIR := "res://props/blockout/route_a/"
func route_prop(ob: Dictionary) -> Node3D:
	var b: Array=ob.bounds
	var size:=Vector3(b[2]-b[0],ob.top-ob.bottom,b[3]-b[1])
	var n:=assembly("BlockoutAssembly")
	var kind:=str(ob.kind)
	n.set_meta("kind",kind);n.set_meta("dimensions_m",size)
	if kind=="chair":
		part(n,"Seat",Vector3(0,.39,0),Vector3(size.x,.48,size.z),surface_mat)
		part(n,"Back",Vector3(0,.48,size.z-.09),size,surface_mat)
		for x in [.05,size.x-.11]:
			for z in [.05,size.z-.11]:part(n,"Leg",Vector3(x,0,z),Vector3(x+.06,.39,z+.06),fixture_mat)
	elif kind=="desk":
		part(n,"Worktop",Vector3(0,size.y-.1,0),size,surface_mat)
		part(n,"DrawerPedestal",Vector3(.08,0,.08),Vector3(.65,size.y-.1,size.z-.08),body_mat)
		part(n,"FarSupport",Vector3(size.x-.2,0,.08),Vector3(size.x-.08,size.y-.1,size.z-.08),body_mat)
		part(n,"Backboard",Vector3(.2,.2,.06),Vector3(size.x-.2,size.y-.12,.16),body_mat)
		for x in ([size.x*.22,size.x*.72] if size.x>=3 else [size.x*.5]):
			monitor(n,Vector3(x-.2,size.y,.16))
			part(n,"Keyboard",Vector3(x-.35,size.y,.65),Vector3(x+.35,size.y+.04,.86),fixture_mat)
		collision(n,"Envelope",Vector3.ZERO,size)
	elif kind in ["storage","service","air","server"]:
		cabinet(n,size,str(ob.facing),kind in ["service","air"])
		if kind=="server":
			var face:=str(ob.facing)
			var along:=face in ["south","north"]
			var count:=maxi(1,floori((size.x if along else size.z)/.8))
			for i in count:
				var a:=Vector3(.1,1.5,.1);var v:=Vector3(.35,1.63,.35)
				if along:
					a.x=.15+i*(size.x/count);v.x=a.x+.24;a.z=size.z+.013 if face=="south" else -.025;v.z=a.z+.012
				else:
					a.z=.15+i*(size.z/count);v.z=a.z+.24;a.x=size.x+.013 if face=="east" else -.025;v.x=a.x+.012
				part(n,"StatusReadout",a,v,screen_mat)
	elif kind=="rack":
		for y in [0.0,.75,1.5,size.y-.12]:part(n,"Shelf",Vector3(0,y,0),Vector3(size.x,y+.1,size.z),surface_mat)
		for x in [0.0,size.x-.1]:
			for z in [0.0,size.z-.1]:part(n,"Upright",Vector3(x,0,z),Vector3(x+.1,size.y,z+.1),body_mat)
		var along:=size.x>size.z
		var count:=maxi(1,floori((size.x if along else size.z)/.9))
		for row in 3:
			for i in count:
				var a:=Vector3(.17,row*.75+.12,.17);var v:=Vector3(size.x-.17,row*.75+.57,size.z-.17)
				if along:a.x=.15+i*size.x/count;v.x=a.x+size.x/count-.28
				else:a.z=.15+i*size.z/count;v.z=a.z+size.z/count-.28
				part(n,"StoredCase",a,v,body_mat)
		collision(n,"Envelope",Vector3.ZERO,size)
	elif kind in ["pump","machine","equipment"]:
		part(n,"Plinth",Vector3.ZERO,Vector3(size.x,.2,size.z),fixture_mat)
		part(n,"MachineHousing",Vector3(.15,.2,.15),Vector3(size.x-.15,size.y-.2,size.z-.15),body_mat)
		part(n,"UpperHousing",Vector3(.25,size.y-.2,.25),Vector3(size.x-.25,size.y,size.z-.25),service_mat)
		part(n,"ControlPanel",Vector3(.3,size.y*.45,size.z-.14),Vector3(size.x-.3,size.y*.67,size.z-.11),screen_mat)
		if kind=="pump":
			for x in [.3,size.x-.7]:part(n,"PipeRiser",Vector3(x,.4,.02),Vector3(x+.35,size.y-.25,.4),surface_mat)
		collision(n,"Envelope",Vector3.ZERO,size)
	elif kind=="bench":
		part(n,"Seat",Vector3(0,size.y-.1,0),size,surface_mat)
		for x in [.15,size.x-.35]:part(n,"Support",Vector3(x,0,.1),Vector3(x+.2,size.y-.1,size.z-.1),body_mat)
		collision(n,"Envelope",Vector3.ZERO,size)
	elif kind=="light":
		part(n,"Housing",Vector3.ZERO,size,fixture_mat)
		part(n,"Diffuser",Vector3(.06,-.012,.025),Vector3(size.x-.06,-.002,size.z-.025),lamp_mat)
		var light:=OmniLight3D.new();light.position=Vector3(size.x/2,-.18,size.z/2)
		light.light_color=Color(.9,.94,1);light.light_energy=.5;light.omni_range=10;light.omni_attenuation=.65;light.shadow_enabled=false
		light.distance_fade_enabled=true;light.distance_fade_begin=55;light.distance_fade_length=15
		owned(n,light,n,"TaskLight");collision(n,"Envelope",Vector3.ZERO,size)
	elif kind=="duct":
		part(n,"Trunk",Vector3.ZERO,size,service_mat)
		var along:=size.x>=size.z;var length:=size.x if along else size.z
		for i in maxi(1,int(length/2)):
			var a:=Vector3(.15,-.025,.1);var v:=Vector3(size.x-.15,-.01,size.z-.1)
			if along:a.x=.2+i*2;v.x=minf(a.x+.7,size.x-.1)
			else:a.z=.2+i*2;v.z=minf(a.z+.7,size.z-.1)
			part(n,"VentSlot",a,v,fixture_mat)
		collision(n,"Envelope",Vector3.ZERO,size)
	elif kind=="hatch":
		part(n,"SealedBacking",Vector3(.15,.04,.15),Vector3(size.x-.15,size.y,size.z-.15),fixture_mat)
		for a in [[Vector3.ZERO,Vector3(.15,size.y,size.z)],[Vector3(size.x-.15,0,0),size],[Vector3(.15,0,0),Vector3(size.x-.15,size.y,.15)],[Vector3(.15,0,size.z-.15),Vector3(size.x-.15,size.y,size.z)]]:part(n,"Frame",a[0],a[1],surface_mat)
		for i in 7:part(n,"GrateBar",Vector3(.15,0,.26+i*.35),Vector3(size.x-.15,.025,.35+i*.35),service_mat)
		collision(n,"SealedEnvelope",Vector3.ZERO,size)
	elif kind=="display":
		part(n,"Housing",Vector3(.035,0,0),size,fixture_mat)
		part(n,"Readout",Vector3(0,.06,.06),Vector3(.025,size.y-.06,size.z-.06),screen_mat)
	else:
		part(n,"Panel",Vector3.ZERO,size,body_mat);collision(n,"Envelope",Vector3.ZERO,size)
	return n
func run() -> void:
	if not "--apply-route-a" in OS.get_cmdline_user_args():push_error("Requires -- --apply-route-a");quit(1);return
	var report: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://.godot/freight_route_a_apply.json"))
	if FileAccess.get_sha256("res://maps/freight_01.map")!=report.output_sha256 or FileAccess.get_sha256("res://missions/freight/freight_blockout.tscn")!=report.original_scene_sha256:push_error("Source changed after Route A checkpoint");quit(1);return
	if ResourceLoader.exists("res://missions/freight/route_a_furnishing.tscn"):push_error("Already authored; preserve subsequent edits");quit(1);return
	DirAccess.make_dir_recursive_absolute(ASSET_DIR)
	body_mat=load("res://props/blockout/materials/registration_block.tres");surface_mat=load("res://props/blockout/materials/registration_surface.tres");service_mat=load("res://props/blockout/materials/registration_service.tres");fixture_mat=load("res://props/blockout/materials/registration_fixture.tres");screen_mat=load("res://props/blockout/f02/screen.tres");lamp_mat=load("res://props/blockout/f02/lamp.tres")
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json")).route_a_style
	var placement:=Node3D.new();placement.name="RouteAStyle"
	var cache: Dictionary={}
	for ob in plan.props:
		if not placement.has_node(ob.room):owned(placement,Node3D.new(),placement,ob.room)
		var b: Array=ob.bounds;var size:=Vector3(b[2]-b[0],ob.top-ob.bottom,b[3]-b[1])
		var key:=str(ob.kind)+"_"+str(size)+"_"+str(ob.facing)
		if not cache.has(key):
			var asset:=route_prop(ob);cache[key]=save_asset(asset,ASSET_DIR+str(ob.kind)+"_"+key.md5_text().left(10)+".tscn");asset.free()
		var instance: Node3D=cache[key].instantiate();instance.position=Vector3(b[0]-190,ob.bottom,b[1]-260)
		instance.set_meta("layout_id",ob.id);instance.set_meta("purpose",ob.name)
		owned(placement.get_node(ob.room),instance,placement,ob.id)
	owned(placement,Node3D.new(),placement,"HatchReservations")
	for h in plan.hatches:
		var marker:=Marker3D.new();marker.position=Vector3(h.center[0]-190,h.floor,h.center[2]-260)
		marker.set_meta("reservation",h);owned(placement.get_node("HatchReservations"),marker,placement,h.id)
	for zone in plan.zones:
		var b: Array=zone.bounds
		# Mounted departmental labels are kept small; existing navigation labels remain.
		label(placement,"ZoneSign",str(zone.title).to_upper(),Vector3((b[0]+b[2])/2-190,zone.floor+2.65,b[1]+.035-260),0,.005)
	var packed_placement:=save_asset(placement,"res://missions/freight/route_a_furnishing.tscn");placement.free()
	var mission: Node3D=load("res://missions/freight/freight_blockout.tscn").instantiate();mission.storage_enabled=false;root.add_child(mission);mission.get_node("GymPlayer").set_physics_process(false)
	for n in mission.get_node("FurnishingF01").get_children():
		var s:=str(n.name)
		if s.contains("Chair") or s.begins_with("A2Light") or s.begins_with("A8Light") or s in ["A1Light03","A1Light04"]:
			n.get_parent().remove_child(n);n.free()
	for n in mission.get_node("Lights").get_children():
		if str(n.name) in ["RoomA3","RoomA4","RoomA5","RoomA6","RoomA7"]:n.light_energy=.4
	var fresh:=packed_placement.instantiate();owned(mission,fresh,mission,"RouteAStyle")
	mission.storage_enabled=true
	var saved:=PackedScene.new();var err:=saved.pack(mission)
	if err==OK:err=ResourceSaver.save(saved,"res://missions/freight/freight_blockout.tscn")
	print("FREIGHT_ROUTE_A_AUTHORED: save=",err," / props=",plan.props.size()," / reusable assets=",cache.size())
	quit(0 if err==OK else 1)
