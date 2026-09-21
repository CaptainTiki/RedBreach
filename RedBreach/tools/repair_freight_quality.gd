extends "res://tools/apply_freight_quality.gd"
func run() -> void:
	if not "--repair-mounts" in OS.get_cmdline_user_args():quit(1);return
	fixture_mat=load("res://props/blockout/materials/registration_fixture.tres")
	var world: Node3D=load("res://missions/freight/freight_blockout.tscn").instantiate();world.storage_enabled=false;root.add_child(world)
	var player: CharacterBody3D=world.get_node("GymPlayer");player.set_physics_process(false)
	var placement: Node3D=world.get_node("RouteAStyle")
	if placement.has_meta("quality_mount_revision"):push_error("Mount correction already applied");quit(1);return
	for id in ["A3_061","A3_062"]:placement.get_node("A3/"+id).position.x+=1
	var old:=placement.get_node("FixtureMounts");placement.remove_child(old);old.free()
	for i in 4:await physics_frame
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

	placement.set_meta("quality_mount_revision",1)
	save_placement(placement,"res://missions/freight/route_a_furnishing.tscn")
	FileAccess.open("res://.godot/quality_mounts.json",FileAccess.WRITE).store_string(JSON.stringify({"mounts":mounts,"unresolved":gaps}))
	print("QUALITY_MOUNTS: ",mounts,"; unresolved=",gaps);quit()
