extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var resource: PackedScene = load("res://missions/freight/freight_blockout.tscn")
	if resource == null:
		quit(1)
		return
	var scene: Node3D = resource.instantiate()
	scene.storage_enabled = false
	root.add_child(scene)
	scene.get_node("GymPlayer").set_physics_process(false)
	var geometry: FuncGodotMap = scene.get_node("Geometry")
	var result := {"complete":false,"failed":false}
	geometry.build_complete.connect(func():result.complete = true)
	geometry.build_failed.connect(func():result.failed = true)
	geometry.build()
	if not result.complete or result.failed or geometry.get_child_count() == 0:
		push_error("FREIGHT_BUILD_FAILED")
		quit(1)
		return
	for child in geometry.find_children("*","",true,false):child.owner = scene
	# Packed authored state remains reusable: runtime QA/storage overrides are not saved.
	scene.storage_enabled = true
	var packed := PackedScene.new()
	var error := packed.pack(scene)
	if error == OK:error = ResourceSaver.save(packed,"res://missions/freight/freight_blockout.tscn")
	print("FREIGHT_BUILD: ",geometry.find_children("*","CollisionShape3D",true,false).size()," brushes; save=",error)
	quit(0 if error == OK else 1)
