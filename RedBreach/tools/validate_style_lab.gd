extends SceneTree
## Style lab S-01 checks. Numbers come from style/style_lab_data.json, which is
## generated from tools/style_lab.py, so the checks cannot drift from the map.
var scene: Node3D
var player: CharacterBody3D
var data: Dictionary
var checks := 0
var failures := 0

func _initialize() -> void: call_deferred("run")

func expect(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		print("FAIL: ", message)

func map_brush_count(path: String) -> int:
	var lines := FileAccess.get_file_as_string(path).split("\n")
	var brushes := 0
	for i in lines.size() - 1:
		if lines[i].strip_edges() == "{" and not lines[i + 1].strip_edges().begins_with("\""):
			brushes += 1
	return brushes

func ray(space: PhysicsDirectSpaceState3D, a: Vector3, b: Vector3) -> Dictionary:
	var q := PhysicsRayQueryParameters3D.create(a, b)
	q.exclude = [player.get_rid()]
	return space.intersect_ray(q)

func walk_to(target: Vector2, speed: float, label: String) -> bool:
	for i in range(2400):
		var here := Vector2(player.global_position.x, player.global_position.z)
		var to := target - here
		if to.length() < 0.4:
			return true
		var v := to.normalized() * speed
		player.velocity = Vector3(v.x, player.velocity.y, v.y)
		player.move_and_slide()
		await physics_frame
		if absf(player.global_position.y) > 0.35:
			expect(false, "%s left the floor at %v" % [label, player.global_position])
			return false
	expect(false, "%s stalled at %v short of %v" % [label, player.global_position, target])
	return false

func run() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string("res://style/style_lab_data.json"))
	scene = load("res://style/style_lab.tscn").instantiate()
	root.add_child(scene)
	player = scene.get_node("GymPlayer")
	player.set_physics_process(false)
	player.pistol.audio_enabled = false
	await physics_frame
	await physics_frame
	var space := player.get_world_3d().direct_space_state

	# 1. Every brush in the source map arrives as collision in the zoned mix,
	#    and the single-look palettes carry none, so they never double up.
	var brushes := map_brush_count("res://maps/style_lab_01.map")
	var palettes: Array = data.palettes
	for entry in palettes:
		var shapes := scene.get_node("Geometry_" + entry[0]).find_children("*", "CollisionShape3D", true, false).size()
		if entry[1].is_empty():
			expect(brushes > 100 and shapes == brushes, "%s has %d collision shapes for %d brushes" % [entry[0], shapes, brushes])
		else:
			expect(shapes == 0, "%s still has %d collision shapes" % [entry[0], shapes])

	# 2. No surface fell back to func_godot's default texture, and each
	#    single-look palette really wears only its look: the remap reached
	#    every face.
	for entry in palettes:
		var geometry_name: String = "Geometry_" + entry[0]
		var only := ""
		if not entry[1].is_empty():
			only = "/looks/%s/" % entry[1].values()[0]
		var surfaces := 0
		for mesh_instance in scene.get_node(geometry_name).find_children("*", "MeshInstance3D", true, false):
			var mesh: Mesh = mesh_instance.mesh
			for s in mesh.get_surface_count():
				surfaces += 1
				var material := mesh.surface_get_material(s)
				var ok: bool = material is StandardMaterial3D and material.albedo_texture != null \
					and not material.albedo_texture.resource_path.contains("default_texture")
				expect(ok, "%s surface %d (%s) has no look material" % [geometry_name, s, mesh.surface_get_name(s)])
				if only != "" and material:
					expect(material.resource_path.contains(only), "%s wears %s" % [geometry_name, material.resource_path])
		expect(surfaces >= 15, "%s has only %d surfaces" % [geometry_name, surfaces])

	# 2b. Lighting: every bay carries every tier. In the default plan the dead
	#     bay has no light and no glowing fitting, and every other bay is lit.
	var plan: Array = data.plans[0][1]
	for b in plan.size():
		var lit_lights := 0
		for tier in data.tiers:
			var node := scene.get_node_or_null("Lighting/Bays/Bay%d/%s" % [b, tier])
			expect(node != null, "bay %d lacks tier %s" % [b, tier])
			if node == null or not tier in plan[b] or tier in ["flicker", "emergency"]:
				continue
			lit_lights += node.find_children("*", "OmniLight3D", false, false).size()
			if tier == "dead":
				for fitting in node.find_children("*", "MeshInstance3D", false, false):
					var m: Material = fitting.get_surface_override_material(0)
					expect(m is StandardMaterial3D and not m.emission_enabled, "dead fitting %s glows" % fitting.name)
		if "dead" in plan[b]:
			expect(lit_lights == 0, "dead bay %d has %d lights" % [b, lit_lights])
		elif not "flicker" in plan[b]:
			expect(lit_lights > 0, "bay %d is unlit in the default plan" % b)
	var flicker := scene.get_node("Lighting/Bays/Bay7/flicker")
	flicker.force(false)
	for light in flicker.find_children("*", "OmniLight3D", false, false):
		expect(not light.visible, "flicker light %s stays on when out" % light.name)

	# 3. Lane clearance: a standing capsule fits at the centre and 1.5 m either
	#    side, every 0.5 m, through all three profiles and their bulkheads.
	var capsule: CapsuleShape3D = player.get_node("CollisionShape3D").shape
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.exclude = [player.get_rid()]
	var lane_hits := 0
	var z := -1.0
	while z > data.room.z0 + 0.5:
		for x in [-1.5, 0.0, 1.5]:
			query.transform = Transform3D(Basis.IDENTITY, Vector3(x, capsule.height / 2.0 + 0.06, z))
			if not space.intersect_shape(query, 1).is_empty():
				lane_hits += 1
				if lane_hits <= 5:
					print("FAIL: capsule blocked at x=%.1f z=%.2f" % [x, z])
		z -= 0.5
	expect(lane_hits == 0, "%d blocked lane samples" % lane_hits)

	# 4. Headroom in every bay: at least 3.5 m on the centreline (under the rib
	#    beams) and 2.2 m at the lane edges.
	for section in data.sections:
		for bay in [2.0, 6.0, 10.0]:
			var bz: float = section[1] - bay
			for x in [0.0, -1.5, 1.5]:
				var hit := ray(space, Vector3(x, 0.2, bz), Vector3(x, 8.0, bz))
				var need := 3.5 if x == 0.0 else 2.2
				expect(not hit.is_empty() and hit.position.y >= need,
					"%s bay %.0f x=%.1f headroom %.2f < %.1f" % [section[0], bay, x, hit.get("position", Vector3.ZERO).y, need])
		for st in data.rib_stations:
			var rz: float = section[1] - st
			var hit := ray(space, Vector3(0, 0.2, rz), Vector3(0, 8.0, rz))
			expect(not hit.is_empty() and hit.position.y >= 3.5, "%s rib beam at %.1f is at %.2f" % [section[0], st, hit.get("position", Vector3.ZERO).y])

	# 5. The walk: spawn to the room at walking pace, sprint back, never
	#    lifted by a slope, rib toe or plinth ledge.
	player.set_physics_process(true)
	player.control_override = true
	var spawn := Vector3(data.spawn[0], data.spawn[1], data.spawn[2])
	player.relocate(Transform3D(Basis.IDENTITY, spawn))
	await physics_frame
	var room_front := Vector2(0.0, data.room.z0 - 2.5)
	expect(await walk_to(room_front, 5.0, "walk in"), "walk in")
	expect(await walk_to(Vector2(spawn.x, spawn.z), 8.0, "sprint back"), "sprint back")
	# Along the lane edges the walk must complete. Hugging the wall, the first
	# rib stops the player: ribs stand proud and the bays are shelter, not a
	# running lane (the corridor lab's rule). Being stopped is correct. Being
	# LIFTED by a slope, rib toe or plinth ledge is the failure.
	for x in [-1.5, 1.5]:
		player.relocate(Transform3D(Basis.IDENTITY, Vector3(x, 0.05, -1.5)))
		await physics_frame
		expect(await walk_to(Vector2(x, data.room.z0 + 1.5), 5.0, "lane-edge walk x=%.1f" % x), "lane-edge walk x=%.1f" % x)
	for x in [-2.1, 2.1]:
		player.relocate(Transform3D(Basis.IDENTITY, Vector3(x, 0.05, -1.5)))
		await physics_frame
		var highest := 0.0
		for i in 240:
			player.velocity = Vector3(x * 0.4, player.velocity.y, -5.0)
			player.move_and_slide()
			await physics_frame
			highest = maxf(highest, player.global_position.y)
		expect(highest < 0.35, "jamming along the wall at x=%.1f lifted the player to %.2f" % [x, highest])
		expect(player.global_position.z < -3.0, "wall-side walk at x=%.1f never reached the first rib" % x)

	# 6. A lap of the machine room, between the desks and the walls.
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(0.0, 0.05, data.room.z0 - 2.5)))
	await physics_frame
	for p in data.room_loop:
		expect(await walk_to(Vector2(p[0], p[1]), 5.0, "room lap"), "room lap to %s" % [p])

	# 7. The window is glazed (clip) and the room is otherwise sealed.
	var glass := ray(space, Vector3(6.5, 2.2, data.room.cz), Vector3(12.0, 2.2, data.room.cz))
	expect(not glass.is_empty() and glass.position.x > 8.0 and glass.position.x < 8.3,
		"window glass not found where expected: %s" % [glass.get("position", "none")])
	var origin := Vector3(0.0, 2.5, data.room.z0 - 3.0)
	for i in 24:
		var a := TAU * i / 24.0
		if sin(a) > 0.95:
			continue    # straight back out through the portal, the intended opening
		var hit := ray(space, origin, origin + Vector3(cos(a), 0.0, sin(a)) * 20.0)
		expect(not hit.is_empty(), "room open toward angle %d" % i)
	for p in [Vector3(0, 1, data.room.z0 - 1.0), Vector3(-6, 1, data.room.cz), Vector3(6, 1, data.room.z1 + 1.0)]:
		var up := ray(space, p, p + Vector3.UP * 12.0)
		expect(not up.is_empty() and up.position.y <= data.room.ceil + 0.01, "room roof open above %v" % p)

	print("STYLE_LAB_QA: %d checks; %d failures" % [checks, failures])
	quit(0 if failures == 0 else 1)
