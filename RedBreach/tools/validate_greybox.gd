extends SceneTree
var failures: Array[String] = []
var checks := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ",label)
	if not ok: failures.append(label)
func run() -> void:
	for path in ["res://gym/gym.tscn","res://combat/combat_gym.tscn","res://encounters/route_trial.tscn"]:
		var scene: Node3D = load(path).instantiate()
		if path.contains("route_trial"): scene.storage_enabled = false
		root.add_child(scene)
		scene.get_node("GymPlayer").set_physics_process(false)
		var surfaces := 0
		var triangles := 0
		var good_materials := true
		var good_metrics := true
		var max_error: float = 0.0
		for node in scene.get_node("Geometry").find_children("*","MeshInstance3D",true,false):
			var mesh: Mesh = node.mesh
			for surface in mesh.get_surface_count():
				surfaces += 1
				var material: StandardMaterial3D = mesh.surface_get_material(surface)
				good_materials = good_materials and material != null and material.albedo_texture != null and material.albedo_texture.resource_path.begins_with("res://textures/greybox/") and not material.albedo_texture.resource_path.contains("/Light/")
				var arrays := mesh.surface_get_arrays(surface)
				var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
				var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
				var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
				for i in range(0,indices.size(),3):
					var a := indices[i]
					var b := indices[i+1]
					var c := indices[i+2]
					var e1: Vector3 = node.global_basis * (vertices[b]-vertices[a])
					var e2: Vector3 = node.global_basis * (vertices[c]-vertices[a])
					var uv1 := uvs[b]-uvs[a]
					var uv2 := uvs[c]-uvs[a]
					var determinant: float = uv1.x*uv2.y-uv1.y*uv2.x
					if e1.cross(e2).length() < 0.000001: continue
					triangles += 1
					if absf(determinant) < 0.0000001:
						good_metrics = false
						continue
					var du := (e1*uv2.y-e2*uv1.y)/determinant
					var dv := (e2*uv1.x-e1*uv2.x)/determinant
					max_error = maxf(max_error,maxf(absf(du.length()-1.0),absf(dv.length()-1.0)))
					good_metrics = good_metrics and absf(du.length()-1.0)<0.001 and absf(dv.length()-1.0)<0.001 and absf(du.normalized().dot(dv.normalized()))<0.001
		check(surfaces > 0 and good_materials,path + ": every baked surface uses the Kenney palette")
		check(triangles > 0 and good_metrics,path + ": all baked triangles have orthogonal 1 m UV repeats, including slopes")
		print("GRID_MEASUREMENT: ",path," / ",triangles," triangles / max repeat error ",max_error," m")
		scene.queue_free()
		await process_frame
	for data in [["res://interaction/sliding_door.tscn","LeftLeaf/Mesh"],["res://interaction/sliding_door.tscn","SwitchFront/Mesh"],["res://encounters/vent.tscn","Grate/Slat0"]]:
		var packed: PackedScene = load(data[0])
		var node: Node = packed.instantiate()
		var mesh: MeshInstance3D = node.get_node_or_null(data[1])
		if mesh == null:
			check(false, "Missing authored prop: " + str(data))
			node.free()
			continue
		var material: StandardMaterial3D = mesh.mesh.material
		check(material.albedo_texture != null and material.albedo_texture.resource_path.contains("greybox") and material.uv1_triplanar and not material.uv1_world_triplanar and material.uv1_scale == Vector3.ONE,data[0]+" "+data[1]+": prop texture measures metres and moves with the prop")
		node.free()
	print("GREYBOX_QA: ",checks," checks; ",failures.size()," failures")
	quit(0 if failures.is_empty() else 1)
