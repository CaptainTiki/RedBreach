extends SceneTree
## Build source brushes, then bake bug navigation from the same saved geometry.
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var gym: Node3D = load("res://encounters/route_trial.tscn").instantiate()
	root.add_child(gym)
	gym.get_node("GymPlayer").set_physics_process(false)
	var geometry: FuncGodotMap = gym.get_node("Geometry")
	var result := {"complete": false, "failed": false}
	geometry.build_complete.connect(func(): result.complete = true)
	geometry.build_failed.connect(func(): result.failed = true)
	geometry.build()
	if not result.complete or result.failed or geometry.get_child_count() == 0:
		push_error("ROUTE_BUILD_FAILED")
		quit(1)
		return
	for node in geometry.find_children("*", "", true, false):
		node.owner = gym
	var nav := NavigationMesh.new()
	nav.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	nav.geometry_collision_mask = 1
	nav.agent_height = 1.9
	nav.agent_radius = 1.0
	nav.agent_max_climb = 0.2
	nav.cell_size = 0.2
	nav.cell_height = 0.1
	nav.filter_baking_aabb = AABB(Vector3(-7, -0.5, -43), Vector3(46, 4.5, 56))
	var source := NavigationMeshSourceGeometryData3D.new()
	NavigationServer3D.parse_source_geometry_data(nav, source, geometry)
	NavigationServer3D.bake_from_source_geometry_data(nav, source)
	if nav.get_polygon_count() == 0:
		push_error("ROUTE_NAVIGATION_EMPTY")
		quit(1)
		return
	gym.get_node("Navigation").navigation_mesh = nav
	var packed := PackedScene.new()
	var error := packed.pack(gym)
	if error == OK:
		error = ResourceSaver.save(packed, "res://encounters/route_trial.tscn")
	print("ROUTE_BUILD_SAVED: ", geometry.find_children("*", "CollisionShape3D", true, false).size(), " brushes; ", nav.get_polygon_count(), " navigation polygons; error=", error)
	quit(0 if error == OK else 1)
