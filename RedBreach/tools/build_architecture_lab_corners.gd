extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var resource: PackedScene = load("res://architecture/architecture_lab_corners.tscn")
	if resource == null:
		push_error("ARCH_CORNER_BUILD_FAILED: scene missing")
		quit(1)
		return
	var scene: Node3D = resource.instantiate()
	root.add_child(scene)
	scene.get_node("GymPlayer").set_physics_process(false)
	var geometry: FuncGodotMap = scene.get_node("Geometry")
	var result := {"complete": false, "failed": false}
	geometry.build_complete.connect(func(): result.complete = true)
	geometry.build_failed.connect(func(): result.failed = true)
	geometry.build()
	if not result.complete or result.failed or geometry.get_child_count() == 0:
		push_error("ARCH_CORNER_BUILD_FAILED")
		quit(1)
		return
	for child in geometry.find_children("*", "", true, false): child.owner = scene
	var packed := PackedScene.new()
	var error := packed.pack(scene)
	if error == OK: error = ResourceSaver.save(packed, "res://architecture/architecture_lab_corners.tscn")
	print("ARCH_CORNER_BUILD: ", geometry.find_children("*", "CollisionShape3D", true, false).size(), " brushes; save=", error)
	quit(0 if error == OK else 1)
