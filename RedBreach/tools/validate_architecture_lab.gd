extends SceneTree
var checks := 0
var failures: Array[String] = []
const Z_SOUTH := 2.25
const Z_NORTH := -22.25
const RIB_Z := [2, -2, -6, -10, -14, -18, -22]
func _initialize() -> void: call_deferred("run")
func expect(condition: bool, message: String) -> void:
	checks += 1
	if not condition: failures.append(message)
func run() -> void:
	var scene: Node3D = load("res://architecture/architecture_lab.tscn").instantiate()
	root.add_child(scene)
	var player: CharacterBody3D = scene.get_node("GymPlayer")
	player.set_physics_process(false)
	await physics_frame
	await physics_frame
	var space := scene.get_world_3d().direct_space_state
	var skip: Array[RID] = [player.get_rid()]

	# 1. The protected 4.0 x 3.2 lane is clear for the whole run. The rib toes
	#    sit exactly on the lane line, so the probe is a hair under 4.0 to test
	#    intrusion rather than tangency.
	var lane := BoxShape3D.new()
	lane.size = Vector3(3.98, 3.18, 0.2)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = lane
	query.collision_mask = 0xFFFFFFFF
	query.exclude = [player.get_rid()]
	var z := Z_SOUTH - 0.3
	while z >= Z_NORTH + 0.3:
		query.transform = Transform3D(Basis.IDENTITY, Vector3(0, 1.6, z))
		expect(space.intersect_shape(query, 1).is_empty(), "lane obstructed at z=%.2f" % z)
		z -= 0.25

	# 2. One continuous flat floor at Y = 0 down the walking lane.
	for xi in range(-7, 8):
		var x := xi * 0.25
		z = Z_SOUTH - 0.5
		while z >= Z_NORTH + 0.5:
			var down := PhysicsRayQueryParameters3D.create(Vector3(x, 3.0, z), Vector3(x, -1.0, z), 0xFFFFFFFF, skip)
			var hit := space.intersect_ray(down)
			expect(not hit.is_empty() and absf(hit.position.y) < 0.001,
				"floor not at Y=0 at (%.2f, %.2f)" % [x, z])
			z -= 1.0

	# 3. Nothing the capsule meets below 2 m may be a walkable slope. The rib
	#    toe must read as a vertical wall at knee height, and the wall base
	#    kick must beat floor_max_angle with margin.
	var limit := player.floor_max_angle
	for side in [-1.0, 1.0]:
		for rz in RIB_Z:
			for probe_y in [0.15, 0.30, 0.45]:
				var from := Vector3(side * 1.5, probe_y, float(rz))
				var to := Vector3(side * 2.4, probe_y, float(rz))
				var toe := space.intersect_ray(PhysicsRayQueryParameters3D.create(from, to, 0xFFFFFFFF, skip))
				expect(not toe.is_empty(), "no rib toe at z=%d y=%.2f" % [rz, probe_y])
				if not toe.is_empty():
					var slope := acos(clampf(toe.normal.dot(Vector3.UP), -1.0, 1.0))
					expect(slope > deg_to_rad(88.0),
						"rib toe at z=%d y=%.2f is %.1f deg, not vertical" % [rz, probe_y, rad_to_deg(slope)])
		for bay_z in [0, -4, -8, -12, -16, -20]:
			var mid := float(bay_z) - 2.0
			var kick := space.intersect_ray(PhysicsRayQueryParameters3D.create(
				Vector3(side * 2.0, 0.25, mid), Vector3(side * 3.2, 0.25, mid), 0xFFFFFFFF, skip))
			expect(not kick.is_empty(), "no wall base kick at z=%.1f" % mid)
			if not kick.is_empty():
				var slope2 := acos(clampf(kick.normal.dot(Vector3.UP), -1.0, 1.0))
				expect(slope2 > limit + deg_to_rad(3.0),
					"wall kick at z=%.1f is %.2f deg, not clear of the %.2f deg limit"
					% [mid, rad_to_deg(slope2), rad_to_deg(limit)])

	# 4. Rib beam soffits clear the protected head height across the lane.
	for rz in RIB_Z:
		for xi in range(-7, 8):
			var x2 := xi * 0.25
			var up := PhysicsRayQueryParameters3D.create(Vector3(x2, 1.6, float(rz)), Vector3(x2, 6.0, float(rz)), 0xFFFFFFFF, skip)
			var ceil_hit := space.intersect_ray(up)
			expect(not ceil_hit.is_empty() and ceil_hit.position.y >= 3.5 - 0.001,
				"rib soffit at z=%d x=%.2f is %.3f, below 3.50" % [rz, x2, ceil_hit.get("position", Vector3.ZERO).y])

	# 5. Both ends are sealed.
	for probe in [Vector3(0, 1.6, Z_SOUTH + 0.4), Vector3(0, 1.6, Z_NORTH - 0.4)]:
		var seal := PhysicsRayQueryParameters3D.create(Vector3(0, 1.6, -10), probe, 0xFFFFFFFF, skip)
		expect(not space.intersect_ray(seal).is_empty(), "end not sealed toward %v" % probe)

	# 6. The player walks the run and sprints back without snagging, and does
	#    not end up standing on anything at the rib bases.
	player.set_physics_process(true)
	player.control_override = true
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(0, 0.05, 1.0)))
	await physics_frame
	for i in range(1200):
		player.velocity = Vector3(0, player.velocity.y, -6.0)
		player.move_and_slide()
		await physics_frame
		expect_quiet(absf(player.global_position.y) < 0.35,
			"forward walk left the floor at z=%.2f y=%.2f" % [player.global_position.z, player.global_position.y])
		if player.global_position.z < Z_NORTH + 1.5: break
	expect(player.global_position.z < Z_NORTH + 1.5,
		"forward walk stalled at z=%.2f" % player.global_position.z)
	# Plain sprint back down the lane must complete.
	for i in range(1200):
		player.velocity = Vector3(0, player.velocity.y, 9.0)
		player.move_and_slide()
		await physics_frame
		expect_quiet(absf(player.global_position.y) < 0.35,
			"sprint back climbed to y=%.2f at z=%.2f" % [player.global_position.y, player.global_position.z])
		if player.global_position.z > Z_SOUTH - 1.5: break
	expect(player.global_position.z > Z_SOUTH - 1.5,
		"sprint back stalled at z=%.2f" % player.global_position.z)

	# Jamming into the wall must never LIFT the player. Being stopped by a rib
	# is correct - the shaft stands 0.5 m proud, so a player who drifts into a
	# bay meets the next pillar face on. Only the climb is a failure.
	var highest := 0.0
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(0, 0.05, Z_SOUTH - 1.0)))
	await physics_frame
	for i in range(900):
		player.velocity = Vector3(6.0, player.velocity.y, -6.0)
		player.move_and_slide()
		await physics_frame
		highest = maxf(highest, player.global_position.y)
	expect(highest < 0.35, "jamming into the wall climbed to y=%.3f" % highest)
	expect(player.global_position.x < 2.75,
		"player reached x=%.2f, past the rib shaft" % player.global_position.x)

	for message in failures: print("FAIL: ", message)
	print("ARCH_LAB_QA: %d checks; %d failures" % [checks, failures.size()])
	quit(0 if failures.is_empty() else 1)
var quiet_seen := {}
func expect_quiet(condition: bool, message: String) -> void:
	checks += 1
	if not condition and not quiet_seen.has(message.substr(0, 24)):
		quiet_seen[message.substr(0, 24)] = true
		failures.append(message)
