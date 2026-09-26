extends SceneTree
## Builds style/style_lab.tscn. The zoned mix is built from the source map
## and keeps collision. Each single-look palette is built from a remapped copy
## of that same map (looks/<from>/ -> looks/<to>/), written under .godot/, and
## keeps visuals only. A palette is a build-time remap, never a second map.
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var resource: PackedScene = load("res://style/style_lab.tscn")
	if resource == null:
		push_error("STYLE_LAB_BUILD_FAILED: scene missing")
		quit(1)
		return
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://style/style_lab_data.json"))
	var source := FileAccess.get_file_as_string("res://maps/style_lab_01.map")
	var scene: Node3D = resource.instantiate()
	root.add_child(scene)
	scene.get_node("GymPlayer").set_physics_process(false)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://.godot/style_lab"))
	var counts := []
	for entry in data.palettes:
		var palette_name: String = entry[0]
		var remap: Dictionary = entry[1]
		var geometry: FuncGodotMap = scene.get_node("Geometry_" + palette_name)
		for child in geometry.get_children():
			geometry.remove_child(child)
			child.free()
		if not remap.is_empty():
			var text := source
			for from in remap:
				text = text.replace("looks/%s/" % from, "looks/%s/" % remap[from])
			var path := ProjectSettings.globalize_path("res://.godot/style_lab/%s.map" % palette_name)
			var file := FileAccess.open(path, FileAccess.WRITE)
			file.store_string(text)
			file.close()
			geometry.global_map_file = path
		var result := {"complete": false, "failed": false}
		geometry.build_complete.connect(func(): result.complete = true)
		geometry.build_failed.connect(func(): result.failed = true)
		geometry.build()
		# Never save a machine-specific absolute path into the scene.
		geometry.global_map_file = ""
		if not result.complete or result.failed or geometry.get_child_count() == 0:
			push_error("STYLE_LAB_BUILD_FAILED: " + palette_name)
			quit(1)
			return
		var shapes := geometry.find_children("*", "CollisionShape3D", true, false)
		counts.append(shapes.size())
		if not remap.is_empty():
			for shape in shapes:
				shape.get_parent().remove_child(shape)
				shape.free()
			for body in geometry.find_children("*", "StaticBody3D", true, false):
				body.collision_layer = 0
		for child in geometry.find_children("*", "", true, false): child.owner = scene
	var packed := PackedScene.new()
	var error := packed.pack(scene)
	if error == OK: error = ResourceSaver.save(packed, "res://style/style_lab.tscn")
	print("STYLE_LAB_BUILD: ", counts[0], " brushes; ", counts.size() - 1, " visual-only palettes; save=", error)
	quit(0 if error == OK else 1)
