extends SceneTree
## Rebuild only the Geometry node; authored siblings survive every rebuild.

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var scene: PackedScene = load("res://gym/gym.tscn")
	var gym := scene.instantiate()
	root.add_child(gym)
	gym.get_node("GymPlayer").set_physics_process(false)
	var geometry: FuncGodotMap = gym.get_node("Geometry")
	var status := {"complete": false, "failed": false}
	geometry.build_complete.connect(func(): status.complete = true)
	geometry.build_failed.connect(func(): status.failed = true)
	geometry.build()
	if not status.complete or status.failed or geometry.get_child_count() == 0:
		push_error("GYM_BUILD_FAILED")
		quit(1)
		return
	# Assign owners for builds outside the Godot editor.
	for node in geometry.find_children("*", "", true, false):
		node.owner = gym
	var packed := PackedScene.new()
	var error := packed.pack(gym)
	if error == OK:
		error = ResourceSaver.save(packed, "res://gym/gym.tscn")
	if error != OK:
		push_error("Failed to save gym: %s" % error_string(error))
		quit(1)
		return
	print("GYM_BUILD_SAVED: res://gym/gym.tscn")
	quit()
