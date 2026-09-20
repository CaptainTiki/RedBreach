extends SceneTree
## Exercise the saved annex with actual player input, Jolt collision, and station results.
var gym: Node3D
var player: CharacterBody3D
var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	print("PASS: " if condition else "FAIL: ", message)
	if not condition:
		failures.append(message)

func ticks(count: int) -> void:
	for i in count:
		await physics_frame
	await process_frame

func place(location: Vector3) -> void:
	for action in ["gym_jump", "gym_crouch", "gym_sprint"]:
		Input.action_release(action)
	player.test_direction = Vector2.ZERO
	player.relocate(Transform3D(Basis.IDENTITY, location))
	await ticks(20)

func floor_height(x: float, z: float) -> float:
	var ray := PhysicsRayQueryParameters3D.create(Vector3(x, 3, z), Vector3(x, -2, z), 1, [player.get_rid()])
	var hit := gym.get_world_3d().direct_space_state.intersect_ray(ray)
	return hit.position.y if not hit.is_empty() else -100.0

func run() -> void:
	gym = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	player.control_override = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(30)
	check(InputMap.action_get_events("gym_crouch")[0].physical_keycode == KEY_CTRL, "Crouch is bound to physical Ctrl")
	check(player.get_node("PostureChart/Posture/Standing").active and not player.is_crouching(), "Editable posture State Chart starts Standing")
	check(is_equal_approx(floor_height(-48, 10.5), 0.75) and is_equal_approx(floor_height(-44, 10.5), 1.25), "Relocated high-jump blocks retain their heights beside the long-jump approaches")
	for lane in gym.get_node("MovementAnnex/JumpLanes").get_children():
		var pit_center: Vector3 = lane.global_position + Vector3(0, 0, -lane.gap_length * 0.5)
		check(absf(floor_height(pit_center.x, pit_center.z) + 1.5) < 0.01, "%s has a real 1.5 m deep pit" % lane.name)
	await place(Vector3(-10, 0.05, 8.5))
	player.test_direction = Vector2(-1, 0)
	await ticks(110)
	check(player.position.x < -18.0 and player.is_grounded(), "Walk from the original gym into the annex through the new connector")
	await check_crouch()
	await check_jumps()
	await check_runway()
	await check_existing_stations_crouched()
	for action in ["gym_jump", "gym_crouch", "gym_sprint"]:
		Input.action_release(action)
	player.reset_player()
	await ticks(2)
	check(not player.is_crouching() and player.position.distance_to(player.spawn_transform.origin) < 0.1, "R-style reset restores standing at the original spawn")
	print("GYM_ANNEX_QA: ", "PASS" if failures.is_empty() else "FAIL", " (", failures.size(), " failures)")
	quit(0 if failures.is_empty() else 1)

func check_crouch() -> void:
	await place(Vector3(-33.5, 0.05, 4))
	var standing_y := player.position.y
	Input.action_press("gym_crouch")
	await ticks(40)
	check(player.is_crouching() and is_equal_approx(player.get_node("CollisionShape3D").shape.height, 1.1), "Ctrl enters Crouched and shortens the physical capsule")
	check(absf(player.position.y - standing_y) < 0.02, "Crouching keeps the feet planted")
	check(absf(player.camera.global_position.y - player.position.y - 0.95) < 0.02, "Crouch camera settles at 0.95 m")
	Input.action_press("gym_sprint")
	var start_x := player.position.x
	player.test_direction = Vector2(1, 0)
	await ticks(30)
	check(absf(player.position.x - start_x - 1.25) < 0.08, "Crouch speed remains 2.5 m/s while Shift is held")
	player.test_direction = Vector2.ZERO
	Input.action_release("gym_sprint")
	Input.action_release("gym_crouch")
	await ticks(40)
	check(not player.is_crouching() and is_equal_approx(player.get_node("CollisionShape3D").shape.height, 1.8), "Releasing Ctrl restores the standing capsule in clear space")
	check(absf(player.camera.global_position.y - player.position.y - 1.65) < 0.02, "Standing camera returns to 1.65 m")
	await place(Vector3(-32, 0.05, -9.25))
	Input.action_press("gym_crouch")
	await ticks(20)
	player.test_direction = Vector2(1, 0)
	await ticks(120)
	check(player.position.x < -31.0 and player.is_crouching(), "1.0 m tunnel physically blocks the 1.1 m crouched player")
	await place(Vector3(-32, 0.05, -5.25))
	Input.action_press("gym_crouch")
	await ticks(20)
	player.test_direction = Vector2(1, 0)
	await ticks(70)
	check(player.position.x > -30.0 and player.position.x < -28.0, "Crouch enters the 1.25 m tunnel")
	player.test_direction = Vector2.ZERO
	Input.action_release("gym_crouch")
	await ticks(10)
	check(player.is_crouching() and not player.can_stand(), "Releasing Ctrl under the roof waits for standing clearance")
	Input.action_press("gym_jump")
	await ticks(2)
	Input.action_release("gym_jump")
	check(player.is_crouching() and absf(player.velocity.y) < 0.01 and player.position.y < 0.1, "Space cannot expand or jump the player through a low roof")
	player.test_direction = Vector2(1, 0)
	await ticks(90)
	check(player.position.x > -26.5 and not player.is_crouching(), "Player stands automatically after clearing the roof")
	await place(Vector3(-26, 0.05, -1.25))
	Input.action_press("gym_crouch")
	await ticks(20)
	player.test_direction = Vector2(-1, 0)
	await ticks(150)
	check(player.position.x < -31.5 and player.is_crouching(), "1.5 m tunnel is traversable from the opposite end")
	await place(Vector3(-33.5, 0.05, 4))
	Input.action_press("gym_crouch")
	await ticks(20)
	Input.action_press("gym_jump")
	await ticks(12)
	Input.action_release("gym_jump")
	check(not player.is_crouching() and player.position.y > 0.6, "Space stands and performs the normal jump when overhead space is clear")
	await ticks(6)
	check(not player.is_crouching(), "Holding Ctrl does not shrink the capsule in midair")
	await ticks(65)
	check(player.is_crouching(), "Held crouch applies again after landing")
	await place(Vector3(-29, 0.05, 5))
	player._pitch = atan2(0.8 - 1.65, 5.0)
	player.reset_camera_interpolation()
	await ticks(3)
	check(player.fire_probe(), "Standing probe clears the 1 m cover and hits the sightline target")
	Input.action_press("gym_crouch")
	await ticks(40)
	player._pitch = atan2(0.8 - 0.95, 5.0)
	player.reset_camera_interpolation()
	await ticks(3)
	check(not player.fire_probe(), "Crouched probe is blocked by the cover")

func check_jumps() -> void:
	for lane in gym.get_node("MovementAnnex/JumpLanes").get_children():
		for sprinting in [false, true]:
			await place(lane.get_node("ResetPoint").global_position)
			if sprinting:
				Input.action_press("gym_sprint")
			player.test_direction = Vector2(0, -1)
			for i in 130:
				if player.position.z <= -1.75:
					break
				await ticks(1)
			var passed_before: int = lane.passes
			var missed_before: int = lane.recoveries
			Input.action_press("gym_jump")
			await ticks(2)
			Input.action_release("gym_jump")
			for i in 120:
				if lane.passes > passed_before or lane.recoveries > missed_before:
					break
				await ticks(1)
			player.test_direction = Vector2.ZERO
			var expect_pass: bool = sprinting or lane.gap_length <= 3.0
			check(lane.passes > passed_before if expect_pass else lane.recoveries > missed_before, "%s %s jump %s" % [lane.name, "sprint" if sprinting else "walk", "lands and records a pass" if expect_pass else "misses and recovers locally"])
			print("JUMP_RESULT: ", lane.name, " ", lane.last_result, " position=", player.position)
			if not expect_pass:
				check(player.position.distance_to(lane.get_node("ResetPoint").global_position) < 0.2, "%s miss resets at its own approach" % lane.name)
		var passes_before: int = lane.passes
		await place(lane.global_position + Vector3(0, 0.05, -lane.gap_length - 1.0))
		await ticks(4)
		check(lane.passes == passes_before, "%s landing pad does not award a pass without a jump" % lane.name)

func check_runway() -> void:
	var runway := gym.get_node("MovementAnnex/Runway")
	for sprinting in [false, true]:
		await place(Vector3(-20, 0.05, 9))
		if sprinting:
			Input.action_press("gym_sprint")
		var before: int = runway.completed_runs
		player.test_direction = Vector2(0, -1)
		for i in 300:
			await ticks(1)
			if runway.completed_runs > before:
				break
		player.test_direction = Vector2.ZERO
		var expected := 2.5 if sprinting else 4.0
		check(runway.completed_runs == before + 1 and absf(runway.last_time - expected) < 0.03, "20 m %s time measures %.1f s" % ["sprint" if sprinting else "walk", expected])
	check(runway.best_times.has("WALK") and runway.best_times.has("SPRINT"), "Runway keeps independent walk and sprint best times")
	await place(Vector3(-23, 0.05, 4))
	player.test_direction = Vector2(1, 0)
	await ticks(40)
	check(not runway.running, "Entering the middle of the runway from the side does not start timing")
	for invalidation in ["mode", "jump", "crouch", "reverse", "side"]:
		await place(Vector3(-20, 0.05, 9))
		player.test_direction = Vector2(0, -1)
		await ticks(18)
		check(runway.running, "Runway arms a new attempt before " + invalidation + " check")
		match invalidation:
			"mode": Input.action_press("gym_sprint")
			"jump": Input.action_press("gym_jump")
			"crouch": Input.action_press("gym_crouch")
			"reverse": player.test_direction = Vector2(0, 1)
			"side": player.test_direction = Vector2(1, 0)
		await ticks(35 if invalidation == "side" else 3)
		check(not runway.running, "Runway cancels an invalid " + invalidation + " attempt")

func check_existing_stations_crouched() -> void:
	await place(Vector3(-9, 0.05, -1))
	Input.action_press("gym_crouch")
	await ticks(20)
	player.test_direction = Vector2(0, -1)
	await ticks(150)
	check(player.position.y > 1.95 and player.position.z < -6.0, "Crouched player climbs the existing stairs")
	player.test_direction = Vector2(0, 1)
	var supported := true
	for i in 150:
		await ticks(1)
		if player.position.z > -5.5 and player.position.z < -2.0:
			supported = supported and player.is_grounded()
	check(supported and player.position.y < 0.1, "Crouched stair descent retains verified support")
	await place(Vector3(-5, 2.05, -7))
	Input.action_press("gym_crouch")
	await ticks(20)
	player.test_direction = Vector2(0, 1)
	await ticks(220)
	check(player.position.z > 0.0 and player.position.y < 0.1 and player.is_grounded(), "Crouched player descends the existing ramp")
	var door := gym.get_node("DoorModule")
	door.request_toggle()
	await ticks(60)
	await place(Vector3(2, 0.05, 4))
	Input.action_press("gym_crouch")
	await ticks(20)
	door.request_toggle()
	await ticks(10)
	check(player.is_crouching() and door.state_name() == "Blocked", "Crouched player still prevents door closure")
