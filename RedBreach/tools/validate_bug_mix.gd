extends SceneTree
## Functional combat checks; frozen-target shooting is not a human pacing measurement.
var trial: Node3D
var player: CharacterBody3D
var pistol: Node3D
var checks := 0
var failures: Array[String] = []
var deaths := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ", label)
	if not ok: failures.append(label)
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func aim(point: Vector3) -> void:
	var direction: Vector3 = point - player.camera.global_position
	player.rotation.y = atan2(-direction.x, -direction.z)
	player._pitch = atan2(direction.y, Vector2(direction.x, direction.z).length())
	player.reset_camera_interpolation()
func freeze_enemies() -> void:
	for encounter in trial.get_node("Encounters").get_children():
		for enemy in encounter.enemies:
			enemy.set_physics_process(false)
			enemy.audio_enabled = false
func run() -> void:
	trial = load("res://encounters/route_trial.tscn").instantiate()
	trial.storage_enabled = false
	root.add_child(trial)
	player = trial.get_node("GymPlayer")
	pistol = player.pistol
	player.control_override = true
	pistol.audio_enabled = false
	await ticks(20)
	freeze_enemies()
	var mixed: Node3D = trial.get_node("Encounters/D")
	check(mixed.enemies.size() == 5, "Mixed encounter starts with five front enemies and a pending sixth")
	trial.start_run()
	mixed.begin()
	await ticks(132)
	freeze_enemies()
	var kinds := {"small": 0, "regular": 0, "spitter": 0}
	for enemy in mixed.enemies:
		var kind: String = "spitter" if enemy.has_method("mouth_is_exposed") else ("small" if enemy.dies_to_any_hit else "regular")
		kinds[kind] += 1
	check(kinds == {"small": 3, "regular": 2, "spitter": 1}, "Saved mixed encounter contains three smalls, two regulars and one spitter")
	check(trial.route_revision == "04" and trial._configuration().small_bug_scene_sha256 == FileAccess.get_sha256("res://combat/gym_small_bug.tscn"), "Route revision and small scene fingerprint distinguish the new balance test")
	var nav_map: RID = trial.get_node("Navigation").get_navigation_map()
	for i in mixed.enemies.size():
		var enemy: CharacterBody3D = mixed.enemies[i]
		var shape: CollisionShape3D = enemy.get_node("CollisionShape3D")
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape.shape
		query.transform = shape.global_transform
		query.collision_mask = 1
		query.exclude = [enemy.get_rid()]
		check(enemy.get_world_3d().direct_space_state.intersect_shape(query).is_empty(), "Mixed spawn %d has physical clearance" % (i+1))
		var path := NavigationServer3D.map_get_path(nav_map, Vector3(20,0,-32), enemy.global_position, true)
		check(path.size() > 1 and path[-1].distance_to(enemy.global_position) < 0.6, "Mixed spawn %d connects to the approach navigation" % (i+1))
	var small: CharacterBody3D = trial.get_node("Encounters/A").enemies[0]
	var shape: CapsuleShape3D = small.get_node("CollisionShape3D").shape
	check(shape.height < 0.65 and shape.radius < 0.3 and small.scale.is_equal_approx(Vector3.ONE), "Small bug has a smaller physical hitbox without scaling its physics root")
	check(small.get_node("Brain/Behavior/Dormant").active and small.get_node("Visual").scale.is_equal_approx(Vector3.ONE * 0.55), "Small scene inherits the editable behavior chart and smaller silhouette")
	small.died.connect(func(): deaths += 1)
	trial.start_run()
	check(not small.register_hit(0.0) and not small.register_hit(-25.0) and small.health == 1.0, "Zero or negative damage cannot kill or wake a small bug")
	check(small.register_hit(0.001) and small.health == 0.0 and small.state() == "Dead", "Even a fractional positive hit wakes and kills the small bug")
	await ticks(2)
	check(deaths == 1 and not small.register_hit(25.0) and small.get_node("CollisionShape3D").disabled, "Small death emits once and removes blocking collision")
	check(not trial.get_node("Effects").splats.is_empty(), "Small death produces actual surface splatters")
	small.reset_bug()
	await ticks(2)
	check(small.health == 1.0 and small.state() == "Dormant" and small.target == null and not small.get_node("CollisionShape3D").disabled and small.get_node("Visual").scale.is_equal_approx(Vector3.ONE * 0.55), "Reset restores the small bug without inflating its corpse to regular size")
	# Real live lunge at small size, with no instant contact damage.
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(9,0.05,-38)))
	small.global_position = Vector3(11,0.05,-38)
	small.set_physics_process(true)
	small.activate(player)
	await ticks(3)
	check(small.state() == "Windup" and player.get_node("Health").health == 100, "Small attack starts with a visible warning and no contact damage")
	for i in 70:
		if small.state() == "Recover": break
		await ticks(1)
	check(small.state() == "Recover" and player.get_node("Health").health == 90, "Small committed lunge reaches the player and deals ten damage once")
	# Reset the actual route, then shoot every member of D using the real pistol ray.
	player.reset_player()
	await ticks(5)
	freeze_enemies()
	mixed = trial.get_node("Encounters/D")
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(9,0.05,-38)))
	await ticks(3)
	trial.start_run()
	# Keep away from the rear spawn until it has emerged, then freeze the target fixture.
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(6.8,0.05,-38)))
	mixed.begin()
	await ticks(132)
	freeze_enemies()
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(9,0.05,-38)))
	await ticks(3)
	var order: Array = []
	for enemy in mixed.enemies:
		if enemy.dies_to_any_hit: order.append(enemy)
	for enemy in mixed.enemies:
		if not enemy.dies_to_any_hit and not enemy.has_method("mouth_is_exposed"): order.append(enemy)
	for enemy in mixed.enemies:
		if enemy.has_method("mouth_is_exposed"): order.append(enemy)
	var shots := 0
	var reloads := 0
	for enemy in order:
		enemy.global_position = Vector3(14,0.05,-38)
		enemy.rotation.y = PI / 2.0
		var weak: bool = enemy.has_method("mouth_is_exposed")
		if weak:
			enemy.get_node("Brain").send_event("windup")
			enemy.mouth_open = 1.0
			enemy._update_mouth()
		await ticks(3)
		var needed: int = 2 if weak else (1 if enemy.dies_to_any_hit else 6)
		for i in needed:
			if pistol.magazine == 0:
				check(shots == 12 and mixed.state() == "Fighting", "A full twelve-round magazine runs out with the mixed fight still active")
				check(not pistol.fire() and pistol.request_reload() and pistol.is_reloading(), "Empty pistol cannot shoot and starts the actual reload")
				check(not pistol.fire(), "Reload prevents firing while enemies remain alive")
				await ticks(88)
				check(not pistol.is_reloading() and pistol.magazine == 12 and pistol.reserve == 48, "Reload completes and transfers twelve reserve rounds")
				reloads += 1
			var before: float = enemy.health
			var point: Vector3 = enemy.get_node("MouthHitArea").global_position if weak else enemy.global_position + Vector3.UP * enemy.sight_height
			aim(point)
			var fired: bool = pistol.fire()
			check(fired and enemy.health < before, "Real pistol shot %d hits the intended mixed enemy" % (shots+1))
			shots += 1
			await ticks(16)
		check(enemy.state() == "Dead", "Mixed enemy dies after %d intended pistol hits" % needed)
	check(shots == 17 and reloads == 1 and pistol.magazine == 7 and mixed.state() == "Cleared", "Seventeen clean hits and one reload clear the best-case mixed encounter")
	check(trial.metrics.encounters.D.count == 6 and trial.metrics.encounters.D.cleared >= 0.0 and trial.metrics.shots == 17, "Six-enemy clear and actual shot count reach route telemetry")
	player.reset_player()
	await ticks(5)
	mixed = trial.get_node("Encounters/D")
	check(mixed.enemies.size() == 5 and mixed._pending == 5 and mixed.state() == "Armed" and pistol.magazine == 12 and pistol.reserve == 60, "Full route reset restores five front enemies, one pending rear enemy and ammunition")
	for enemy in mixed.enemies:
		check(enemy.health == enemy.max_health and enemy.state() == "Dormant" and enemy.get_node("Visual").scale.is_equal_approx(Vector3.ONE * enemy.visual_scale), "Reset preserves each enemy tier's health, behavior and size")
	print("BUG_MIX_QA: ", checks - failures.size(), "/", checks, " passed")
	quit(0 if failures.is_empty() else 1)
