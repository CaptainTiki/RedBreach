extends SceneTree
var failures: Array=[]
func _initialize() -> void:call_deferred("run")
func geometry(node: Node3D) -> Dictionary:
	var bounds: AABB;var first:=true;var triangles:=0;var materials: Dictionary={}
	for mesh: MeshInstance3D in node.get_children():
		var box: AABB=node.transform*mesh.transform*mesh.mesh.get_aabb()
		bounds=box if first else bounds.merge(box);first=false
		for surface in mesh.mesh.get_surface_count():
			var material: Material=mesh.material_override if mesh.material_override else mesh.mesh.surface_get_material(surface)
			var arrays:=mesh.mesh.surface_get_arrays(surface);var indices: PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
			var count: int=indices.size() if not indices.is_empty() else arrays[Mesh.ARRAY_VERTEX].size()
			triangles+=count/3;materials[material.resource_path]=materials.get(material.resource_path,0)+count/3
	return {"bounds":bounds,"triangles":triangles,"materials":materials}
func run() -> void:
	var world: Node3D=load("res://missions/freight/freight_blockout.tscn").instantiate();world.storage_enabled=false;root.add_child(world);world.get_node("GymPlayer").set_physics_process(false)
	var placement: Node3D=world.get_node("RouteAStyle");var bodies:=placement.find_children("*","CollisionObject3D",true,false).size();var lights:=placement.find_children("*","Light3D",true,false).size()
	placement.batch_tree(placement);var checked:=0
	for group in placement.get_children():
		for assembly in group.get_children():
			if not assembly.has_node("RenderBatch"):continue
			checked+=1;var a:=geometry(assembly.get_node("Visual"));var b:=geometry(assembly.get_node("RenderBatch"))
			if not a.bounds.position.is_equal_approx(b.bounds.position) or not a.bounds.size.is_equal_approx(b.bounds.size) or a.triangles!=b.triangles or a.materials!=b.materials:failures.append(str(assembly.get_path()))
			if assembly.get_node("RenderBatch").owner!=null:failures.append("Generated node owned/savable")
	if bodies!=placement.find_children("*","CollisionObject3D",true,false).size() or lights!=placement.find_children("*","Light3D",true,false).size():failures.append("Bodies/lights changed")
	for i in 4:await physics_frame
	var mount_count:=0;var space:=world.get_world_3d().direct_space_state
	for assembly in placement.get_node("FixtureMounts").get_children():
		for mesh: MeshInstance3D in assembly.get_node("Visual").get_children():
			var box: AABB=mesh.global_transform*mesh.mesh.get_aabb();var top:=Vector3(box.get_center().x,box.end.y,box.get_center().z)
			var ray:=PhysicsRayQueryParameters3D.create(top-Vector3.UP*.01,top+Vector3.UP*.04,1)
			if space.intersect_ray(ray).is_empty():failures.append("Mount top unsupported: "+str(top))
			mount_count+=1
	var saved: Node3D=load("res://missions/freight/route_a_furnishing.tscn").instantiate()
	for node in saved.find_children("Visual","Node3D",true,false):
		if not node.visible:failures.append("Saved source hidden")
	if not saved.find_children("RenderBatch","Node3D",true,false).is_empty():failures.append("Generated batch saved")
	saved.free()
	var report:={"assemblies_compared":checked,"source_meshes":placement.source_meshes,"render_meshes":placement.render_meshes,"unchanged_collision_bodies":bodies,"unchanged_lights":lights,"fixture_mounts_supported":mount_count,"failures":failures,"checks":"Per-assembly mesh bounds, triangle count and per-material triangles; collision/light counts; unsaved generated batches; visible editable source cuboids; physical mount support"}
	FileAccess.open("res://.godot/route_a_batch_qa.json",FileAccess.WRITE).store_string(JSON.stringify(report,"\t"));print("BATCH_QA: ",JSON.stringify(report));quit(0 if failures.is_empty() else 1)

