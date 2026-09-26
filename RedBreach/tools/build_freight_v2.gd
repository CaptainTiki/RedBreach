extends SceneTree
## Builds missions/freight_v2/freight_v2.tscn from the source map, then bakes bug navigation from the same geometry
## (larger-bug clearance: 1.0 m radius, 1.9 m height; climbs 0.25 m risers).
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var level: Node3D = load("res://missions/freight_v2/freight_v2.tscn").instantiate()
	root.add_child(level)
	level.get_node("GymPlayer").set_physics_process(false)
	var geometry: FuncGodotMap = level.get_node("Geometry")
	for child in geometry.get_children():
		geometry.remove_child(child)
		child.free()
	var result := {"complete": false, "failed": false}
	geometry.build_complete.connect(func(): result.complete = true)
	geometry.build_failed.connect(func(): result.failed = true)
	geometry.build()
	if not result.complete or result.failed or geometry.get_child_count() == 0:
		push_error("FREIGHT_V2_BUILD_FAILED")
		quit(1)
		return
	for node in geometry.find_children("*", "", true, false):
		node.owner = level
	var nav := NavigationMesh.new()
	nav.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	nav.geometry_collision_mask = 1
	nav.agent_height = 1.9
	nav.agent_radius = 1.0
	nav.agent_max_climb = 0.3
	nav.agent_max_slope = 40.0
	nav.cell_size = 0.2
	nav.cell_height = 0.05
	# The whole level: plan x -32..66, y -30..66 (Godot z = -y), heights -7..9.
	nav.filter_baking_aabb = AABB(Vector3(-32.0, -7.0, -66.0), Vector3(98.0, 16.0, 97.0))
	var source := NavigationMeshSourceGeometryData3D.new()
	NavigationServer3D.parse_source_geometry_data(nav, source, geometry)
	NavigationServer3D.bake_from_source_geometry_data(nav, source)
	if nav.get_polygon_count() == 0:
		push_error("FREIGHT_V2_NAVIGATION_EMPTY")
		quit(1)
		return
	# Keep only the navigation the level can reach: flood from the route markers over polygons that share vertices.
	# The bake also finds the tops of ceilings and roofs, which nothing walks on.
	nav = reachable(nav, geometry)
	level.get_node("Navigation").navigation_mesh = nav
	var lights := geometry.find_children("*", "OmniLight3D", true, false).size()
	var ladders := 0
	for node in geometry.find_children("*", "StaticBody3D", true, false):
		if node.has_method("climb_path"):
			ladders += 1
	var packed := PackedScene.new()
	var error := packed.pack(level)
	if error == OK:
		error = ResourceSaver.save(packed, "res://missions/freight_v2/freight_v2.tscn")
	print("FREIGHT_V2_BUILD: ", geometry.find_children("*", "CollisionShape3D", true, false).size() - ladders, " brushes; ",
		lights, " lights; ", ladders, " ladders; ", nav.get_polygon_count(), " navigation polygons; save=", error)
	quit(0 if error == OK else 1)

func reachable(nav: NavigationMesh, geometry: Node) -> NavigationMesh:
	var verts := nav.get_vertices()
	var polys: Array = []
	for i in nav.get_polygon_count():
		polys.append(nav.get_polygon(i))
	# Vertices can be duplicated between polygons; weld them by position.
	var key_of := {}
	var weld := PackedInt32Array()
	weld.resize(verts.size())
	for i in verts.size():
		var k := Vector3i(roundi(verts[i].x * 20.0), roundi(verts[i].y * 20.0), roundi(verts[i].z * 20.0))
		if not key_of.has(k):
			key_of[k] = key_of.size()
		weld[i] = key_of[k]
	var by_vertex := {}
	for pi in polys.size():
		for vi in polys[pi]:
			by_vertex.get_or_add(weld[vi], []).append(pi)
	var seeds: Array[Vector3] = []
	for marker in geometry.find_children("*", "Marker3D", true, false):
		var p = marker.get("func_godot_properties")
		if p != null and str(p.get("classname", "")) == "rb_route":
			seeds.append(marker.global_position)
	var keep := {}
	var queue: Array = []
	for seed in seeds:
		var best := -1
		var best_d := 1.5
		for pi in polys.size():
			var c := Vector3.ZERO
			for vi in polys[pi]:
				c += verts[vi]
			c /= polys[pi].size()
			var d := Vector2(c.x - seed.x, c.z - seed.z).length() + absf(c.y - seed.y) * 2.0
			if d < best_d:
				best_d = d
				best = pi
		if best >= 0 and not keep.has(best):
			keep[best] = true
			queue.append(best)
	while not queue.is_empty():
		var pi: int = queue.pop_back()
		for vi in polys[pi]:
			for other in by_vertex[weld[vi]]:
				if not keep.has(other):
					keep[other] = true
					queue.append(other)
	var out := NavigationMesh.new()
	out.agent_height = nav.agent_height
	out.agent_radius = nav.agent_radius
	out.agent_max_climb = nav.agent_max_climb
	out.agent_max_slope = nav.agent_max_slope
	out.cell_size = nav.cell_size
	out.cell_height = nav.cell_height
	out.set_vertices(verts)
	for pi in polys.size():
		if keep.has(pi):
			out.add_polygon(polys[pi])
	print("FREIGHT_V2_NAV: kept %d of %d polygons reachable from %d route markers" % [out.get_polygon_count(), polys.size(), seeds.size()])
	return out
