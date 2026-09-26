extends SceneTree
## Builds kit/kit_lab.tscn from the source map, then bakes bug navigation from
## the same geometry (larger-bug clearance: 1.0 m radius, 1.9 m height; climbs
## 0.25 m risers).
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var lab: Node3D = load("res://kit/kit_lab.tscn").instantiate()
	root.add_child(lab)
	lab.get_node("GymPlayer").set_physics_process(false)
	var geometry: FuncGodotMap = lab.get_node("Geometry")
	for child in geometry.get_children():
		geometry.remove_child(child)
		child.free()
	var result := {"complete": false, "failed": false}
	geometry.build_complete.connect(func(): result.complete = true)
	geometry.build_failed.connect(func(): result.failed = true)
	geometry.build()
	if not result.complete or result.failed or geometry.get_child_count() == 0:
		push_error("KIT_LAB_BUILD_FAILED")
		quit(1)
		return
	for node in geometry.find_children("*", "", true, false):
		node.owner = lab
	var nav := NavigationMesh.new()
	nav.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	nav.geometry_collision_mask = 1
	nav.agent_height = 1.9
	nav.agent_radius = 1.0
	nav.agent_max_climb = 0.3
	nav.agent_max_slope = 40.0
	nav.cell_size = 0.2
	nav.cell_height = 0.05
	# The whole lab interior; the Mars exterior is left out.
	nav.filter_baking_aabb = AABB(Vector3(-33.0, -0.6, -71.0), Vector3(74.0, 12.0, 75.0))
	var source := NavigationMeshSourceGeometryData3D.new()
	NavigationServer3D.parse_source_geometry_data(nav, source, geometry)
	NavigationServer3D.bake_from_source_geometry_data(nav, source)
	if nav.get_polygon_count() == 0:
		push_error("KIT_LAB_NAVIGATION_EMPTY")
		quit(1)
		return
	lab.get_node("Navigation").navigation_mesh = nav
	var packed := PackedScene.new()
	var error := packed.pack(lab)
	if error == OK:
		error = ResourceSaver.save(packed, "res://kit/kit_lab.tscn")
	print("KIT_LAB_BUILD: ", geometry.find_children("*", "CollisionShape3D", true, false).size(), " brushes; ",
		nav.get_polygon_count(), " navigation polygons; save=", error)
	quit(0 if error == OK else 1)
