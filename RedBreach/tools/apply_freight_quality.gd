extends "res://tools/apply_freight_route_a.gd"
const QUALITY_DIR := "res://props/blockout/quality/"
func save_placement(n: Node3D,path: String) -> PackedScene:
	var p:=PackedScene.new();assert(p.pack(n)==OK);assert(ResourceSaver.save(p,path)==OK)
	return ResourceLoader.load(path,"PackedScene",ResourceLoader.CACHE_MODE_REPLACE)
func run() -> void:
	if not "--apply-quality" in OS.get_cmdline_user_args():push_error("One-time quality pass; requires -- --apply-quality");quit(1);return
	var report: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://.godot/freight_quality_apply.json"))
	if FileAccess.get_sha256("res://maps/freight_01.map")!=report.map_sha256 or FileAccess.get_sha256("res://missions/freight/registration_f02.tscn")!=report.old_registration_sha256 or FileAccess.get_sha256("res://missions/freight/route_a_furnishing.tscn")!=report.old_placement_sha256:push_error("Checkpoint changed; preserve subsequent edits");quit(1);return
	DirAccess.make_dir_recursive_absolute(QUALITY_DIR)
	body_mat=load("res://props/blockout/materials/registration_block.tres");surface_mat=load("res://props/blockout/materials/registration_surface.tres");service_mat=load("res://props/blockout/materials/registration_service.tres");fixture_mat=load("res://props/blockout/materials/registration_fixture.tres");screen_mat=load("res://props/blockout/f02/screen.tres");lamp_mat=load("res://props/blockout/f02/lamp.tres")
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json")).route_a_style
	var placement: Node3D=load("res://missions/freight/route_a_furnishing.tscn").instantiate()
	var ids: Dictionary={}
	for o in plan.props:ids[o.id]=o
	for group in placement.get_children():
		if group is Label3D or group.name=="HatchReservations":continue
		for n in group.get_children():
			if not ids.has(str(n.name)):group.remove_child(n);n.free()
	for o in plan.props:
		var parent: Node3D=placement.get_node(o.room);var n: Node3D=parent.get_node_or_null(o.id)
		if n==null:
			var source:=route_prop(o);var packed:=save_asset(source,QUALITY_DIR+str(o.id).to_lower()+".tscn");source.free();n=packed.instantiate()
			n.set_meta("layout_id",o.id);n.set_meta("purpose",o.name);owned(parent,n,placement,o.id)
		n.position=Vector3(o.bounds[0]-190,o.bottom,o.bounds[1]-260)
	for h in plan.hatches:
		var parent:=placement.get_node("HatchReservations");var n: Marker3D=parent.get_node_or_null(h.id)
		if n==null:n=Marker3D.new();owned(parent,n,placement,h.id)
		n.position=Vector3(h.center[0]-190,h.floor,h.center[2]-260);n.set_meta("reservation",h)
	placement.set_meta("quality_layout",12)
	# Headless build/QA leaves the sources visible; gameplay alone uses the render cache.
	placement.set_script(load("res://props/blockout/runtime_visual_batch.gd"))
	var registration: Node3D=load("res://missions/freight/registration_f02.tscn").instantiate()
	registration.get_node("Objects/H2").position.z+=.25
	registration.get_node("Objects/Noticeboard").position.z+=.235
	var old: Node3D=registration.get_node("Objects/H3");var at:=old.position+Vector3(.2,0,0);old.get_parent().remove_child(old);old.free()
	var trunk:=assembly("SplitServiceTrunk");trunk.set_meta("kind","waiting service trunk");trunk.set_meta("dimensions_m",Vector3(.7,.4,8.9))
	for b in [[0.0,1.35],[1.65,8.9]]:
		part(trunk,"Trunk",Vector3(0,0,b[0]),Vector3(.7,.4,b[1]),service_mat);collision(trunk,"Trunk",Vector3(0,0,b[0]),Vector3(.7,.4,b[1]))
	var packed_trunk:=save_asset(trunk,QUALITY_DIR+"registration_split_trunk.tscn");trunk.free();var fresh:=packed_trunk.instantiate();fresh.position=at;fresh.set_meta("layout_id","H3");owned(registration.get_node("Objects"),fresh,registration,"H3")
	var world: Node3D=load("res://missions/freight/freight_blockout.tscn").instantiate();world.storage_enabled=false;root.add_child(world)
	var player: CharacterBody3D=world.get_node("GymPlayer");player.set_physics_process(false);player.pistol.audio_enabled=false
	for key in ["RegistrationF02","RouteAStyle"]:
		var original:=world.get_node(key);world.remove_child(original);original.free()
	world.add_child(placement);world.add_child(registration)
	for i in 5:await physics_frame
	# Mount the previously floating light housings to the nearest real overhead surface.
	var space:=world.get_world_3d().direct_space_state;var mount_sets: Dictionary={};var examined: Dictionary={};var mounts:=0;var gaps: Array=[]
	for key in ["RegistrationF02","ScreeningF04","RouteAStyle"]:
		for light in world.get_node(key).find_children("*","OmniLight3D",true,false):
			var prop: Node=light.get_parent()
			while prop!=world and not prop.has_node("Visual"):prop=prop.get_parent()
			if prop==world or examined.has(prop):continue
			examined[prop]=true
			var ext: AABB;var first:=true
			for mesh in prop.get_node("Visual").get_children():
				if not mesh is MeshInstance3D or not mesh.mesh is BoxMesh:continue
				var b: AABB=mesh.global_transform*mesh.mesh.get_aabb()
				ext=b if first else ext.merge(b);first=false
			if first:continue
			var group: String=key if key!="RouteAStyle" else str(prop.get_parent().name)
			if not mount_sets.has(group):mount_sets[group]=assembly("FixtureMounts")
			for fraction in [.3,.7]:
				var xx: float=ext.position.x+ext.size.x*fraction;var zz:=ext.position.z+ext.size.z/2;var top:=ext.end.y
				var exclude: Array[RID]=[player.get_rid()]
				for body in prop.find_children("*","CollisionObject3D",true,false):exclude.append(body.get_rid())
				var ray:=PhysicsRayQueryParameters3D.create(Vector3(xx,top+.005,zz),Vector3(xx,top+2,zz),1,exclude);var hit:=space.intersect_ray(ray)
				if hit.is_empty():gaps.append(str(prop.get_path()));continue
				var height: float=hit.position.y-top
				if height<.01:continue
				part(mount_sets[group],"Mount",Vector3(xx-.03,top,zz-.03),Vector3(xx+.03,hit.position.y,zz+.03),fixture_mat);mounts+=1
	owned(placement,Node3D.new(),placement,"FixtureMounts")
	for group in mount_sets:
		var source: Node3D=mount_sets[group];var packed:=save_asset(source,QUALITY_DIR+"mounts_"+str(group).to_lower()+".tscn");source.free();var n:=packed.instantiate();owned(placement.get_node("FixtureMounts"),n,placement,str(group))
	placement.set_meta("fixture_mount_count",mounts)
	save_placement(registration,"res://missions/freight/registration_f02.tscn")
	save_placement(placement,"res://missions/freight/route_a_furnishing.tscn")
	print("FREIGHT_QUALITY_AUTHOR: ",plan.props.size()," props; ",plan.hatches.size()," hatches; ",mounts," fixture mounts; unresolved=",gaps)
	FileAccess.open("res://.godot/quality_mounts.json",FileAccess.WRITE).store_string(JSON.stringify({"mounts":mounts,"unresolved":gaps}))
	quit()
