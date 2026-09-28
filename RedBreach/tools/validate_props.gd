extends SceneTree
## Checks every prop against the catalogue (props/props_data.json, written by tools/write-props.py from tools/props.py):
##   - the model imported, and every surface uses its external material (the level's look materials or the props' own),
##     none left embedded from the .glb
##   - the model's size and placement match the catalogue (its Body bounds)
##   - furniture is a StaticBody3D on layer 1 with its collision
##   - a light prop has its light; switched off, the light is out and the lens dark; switched on, the lens glows; its
##     wires follow the wire length and hide at 0
##   - the gallery holds every placement, and the player
## Prints PROPS_QA: N checks; M failures.
var checks := 0
var failures := 0


func _initialize() -> void:
	call_deferred("run")


func check(ok: bool, label: String) -> void:
	checks += 1
	if ok:
		print("PASS: ", label)
	else:
		failures += 1
		print("FAIL: ", label)


func model_meshes(prop: Node) -> Array:
	var model := prop.get_node_or_null("Model")
	return [] if model == null else model.find_children("*", "MeshInstance3D", true, false)


func body_aabb(prop: Node3D) -> AABB:
	for mi in model_meshes(prop):
		if mi.name == "Body":
			return (prop.global_transform.affine_inverse() * mi.global_transform) * (mi as MeshInstance3D).get_aabb()
	return AABB()


func run() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://props/props_data.json"))
	for name in data.props:
		var d: Dictionary = data.props[name]
		var packed := load(d.scene) as PackedScene
		check(packed != null, "%s: its scene loads" % name)
		if packed == null:
			continue
		var prop: Node3D = packed.instantiate()
		root.add_child(prop)
		await process_frame
		var meshes := model_meshes(prop)
		check(meshes.size() >= 1, "%s: the model imported (%d meshes)" % [name, meshes.size()])
		var bad := []
		var used := {}
		for mi in meshes:
			var mesh: Mesh = (mi as MeshInstance3D).mesh
			for i in mesh.get_surface_count():
				var m := mesh.surface_get_material(i)
				var path := "" if m == null else m.resource_path
				used[path] = true
				if not (path.begins_with("res://textures/looks/") or path.begins_with("res://props/materials/")):
					bad.append("%s/%d=%s" % [mi.name, i, path if path != "" else "<embedded>"])
		check(bad.is_empty(), "%s: every surface uses its external material %s" % [name, str(bad) if bad else ""])
		var want := {}
		for p in d.materials:
			want[p] = true
		check(used.keys().all(func(p): return want.has(p)) and want.keys().all(func(p): return used.has(p)),
			"%s: the materials are the catalogue's (%d)" % [name, want.size()])
		var box := body_aabb(prop)
		var lo := Vector3(d.body_lo[0], d.body_lo[1], d.body_lo[2])
		var hi := Vector3(d.body_hi[0], d.body_hi[1], d.body_hi[2])
		check(box.position.distance_to(lo) < 0.01 and box.end.distance_to(hi) < 0.01,
			"%s: the model's size and origin match the catalogue (%s to %s)" % [name, box.position, box.end])
		if d.light:
			var light := prop.find_child("Light", true, false) as Light3D
			check(light != null, "%s: carries its light" % name)
			prop.set("lit", false)
			check(light != null and not light.visible and not prop.call("lens_glowing"), "%s: switched off, the light is out and the lens dark" % name)
			prop.set("lit", true)
			check(light != null and light.visible and prop.call("lens_glowing"), "%s: switched on, the lens glows" % name)
			prop.set("energy", 2.5)
			check(light != null and is_equal_approx(light.light_energy, 2.5), "%s: the inspector's energy reaches the light" % name)
			if d.wires:
				var wires := prop.get_node("Model/Wires") as Node3D
				prop.set("wire", 2.0)
				check(wires.visible and is_equal_approx(wires.scale.y, 2.0), "%s: the wires follow the wire length" % name)
				prop.set("wire", 0.0)
				check(not wires.visible, "%s: no wires when flush" % name)
		elif d.category != "gallery" or d.collision > 0:
			var body := prop as StaticBody3D
			check(body != null and (body.collision_layer & 1) != 0, "%s: a static body on layer 1" % name)
			var shapes := prop.find_children("*", "CollisionShape3D", false, false)
			check(shapes.size() == int(d.collision), "%s: its collision (%d shapes)" % [name, shapes.size()])
		prop.queue_free()
		await process_frame
	var gallery: Node = (load("res://props/props_gallery.tscn") as PackedScene).instantiate()
	root.add_child(gallery)
	await process_frame
	check(gallery.get_node("Props").get_child_count() == data.placements.size(), "gallery: every placement (%d)" % data.placements.size())
	check(gallery.has_node("GymPlayer"), "gallery: the player")
	print("PROPS_QA: %d checks; %d failures" % [checks, failures])
	quit(0 if failures == 0 else 1)
