extends SceneTree
## Exercise real pistol input, aiming, ammunition, recoil, and Jolt obstruction.
var gym: Node3D
var player: CharacterBody3D
var pistol: Node3D
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
	for action in ["gym_aim", "gym_crouch", "gym_sprint", "gym_fire"]:
		Input.action_release(action)
	player.control_override = true
	player.test_direction = Vector2.ZERO
	player.relocate(Transform3D(Basis.IDENTITY, location))
	pistol.reset_weapon()
	await ticks(25)

func aim_at(point: Vector3) -> void:
	var offset: Vector3 = point - player.camera.global_position
	player.rotation.y = atan2(-offset.x, -offset.z)
	player._pitch = atan2(offset.y, Vector2(offset.x, offset.z).length())
	player.reset_camera_interpolation()

func mouse_press() -> void:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = true
	player._unhandled_input(event)

func run() -> void:
	gym = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	pistol = player.get_node("Camera3D/Pistol")
	pistol.audio_enabled = false
	await place(Vector3(6, 0.05, 6))
	var target := gym.get_node("Targets/Target1")
	target.reset_target()
	check(InputMap.action_get_events("gym_aim")[0].button_index == MOUSE_BUTTON_RIGHT and InputMap.action_get_events("gym_reload")[0].physical_keycode == KEY_R and InputMap.action_get_events("gym_reset")[0].physical_keycode == KEY_BACKSPACE, "RMB aims, R reloads, and Backspace resets")
	check(pistol.magazine == 12 and pistol.reserve == 60, "Pistol starts with a 12-round magazine and 60 reserve")
	check(pistol.get_node("HandlingChart/Handling/Ready").active and pistol.get_node("AimChart/Aim/Hip").active, "Editable handling and aiming charts start Ready and Hip")
	Input.action_press("gym_fire")
	mouse_press()
	check(pistol.shot_count == 1 and pistol.magazine == 11 and target.health == 75, "A fire press consumes one round and deals 25 damage")
	check(not pistol.fire() and pistol.magazine == 11, "Fire-rate limit rejects a second immediate shot")
	await ticks(35)
	check(pistol.shot_count == 1, "Holding fire does not repeat a semi-automatic shot")
	Input.action_release("gym_fire")
	for i in 3:
		pistol.fire()
		await ticks(16)
	check(target.health == 0 and target.hit_count == 4, "Four pistol hits down a 100 HP test plate")
	await ticks(125)
	check(target.health == 100, "Downed test plate recovers for another attempt")
	check(pistol.request_reload() and pistol.is_reloading(), "Partial magazine enters the Reloading state")
	check(not pistol.request_reload() and not pistol.fire(), "Reload cannot restart itself or fire a shot")
	await ticks(45)
	check(pistol.magazine == 8 and pistol.reserve == 60, "Ammo does not transfer before reload duration elapses")
	await ticks(45)
	check(pistol.magazine == 12 and pistol.reserve == 56 and not pistol.is_reloading(), "Reload transfers only the missing rounds")
	check(not pistol.request_reload(), "Full magazine cannot consume reserve by reloading")
	for i in 12:
		pistol.fire()
		await ticks(16)
	var shots_before: int = pistol.shot_count
	check(pistol.magazine == 0 and not pistol.fire() and pistol.shot_count == shots_before and pistol.dry_fire_count == 1, "Empty magazine dry-fires without damage or negative ammo")
	pistol.reserve = 3
	pistol.request_reload()
	await ticks(90)
	check(pistol.magazine == 3 and pistol.reserve == 0, "Reload handles a reserve smaller than a full magazine")
	check(not pistol.request_reload(), "No-reserve reload is rejected")
	await check_ads()
	await check_hits_and_cover()
	await check_recoil()
	await check_runway()
	Input.action_release("gym_aim")
	pistol.magazine = 2
	pistol.request_reload()
	var reset := InputEventKey.new()
	reset.physical_keycode = KEY_BACKSPACE
	reset.pressed = true
	player._unhandled_input(reset)
	await ticks(20)
	check(pistol.magazine == 12 and pistol.reserve == 60 and not pistol.is_reloading() and not pistol.is_ads(), "Backspace cancels handling and replenishes the test pistol")
	check(player.position.distance_to(player.spawn_transform.origin) < 0.1 and is_equal_approx(player.camera.fov, 80.0) and pistol.aim_offset().length() < 0.001, "Reset restores spawn, FOV, and neutral recoil")
	check(target.health == 100 and target.hit_count == 0, "Reset restores target health and hit counts")
	print("GYM_PISTOL_QA: ", "PASS" if failures.is_empty() else "FAIL", " (", failures.size(), " failures)")
	quit(0 if failures.is_empty() else 1)

func check_ads() -> void:
	await place(Vector3(0, 0.05, 9))
	Input.action_press("gym_aim")
	await ticks(20)
	check(pistol.is_ads() and is_equal_approx(player.camera.fov, 70.0), "Held ADS reaches the 70-degree FOV")
	check(pistol.get_node("Pose").position.distance_to(pistol.ads_position) < 0.001, "ADS centers the authored weapon pose")
	var front: Node3D = pistol.get_node("Pose/Recoil/FrontSight")
	var screen: Vector2 = player.camera.unproject_position(front.to_global(Vector3(0, 0.01, 0)))
	print("SIGHT_ALIGNMENT: screen=", screen, " viewport=", player.camera.get_viewport().get_visible_rect(), " window=", root.size, " local=", player.camera.to_local(front.to_global(Vector3(0, 0.01, 0))))
	check(screen.distance_to(player.camera.get_viewport().get_visible_rect().get_center()) < 1.0 and not player.get_node("HUD/Crosshair").visible, "Front sight tip aligns with actual screen center in ADS")
	var left: Node3D = pistol.get_node("Pose/Recoil/RearSightLeft")
	var right: Node3D = pistol.get_node("Pose/Recoil/RearSightRight")
	var left_screen: Vector2 = player.camera.unproject_position(left.to_global(Vector3(0, 0.017, 0)))
	var right_screen: Vector2 = player.camera.unproject_position(right.to_global(Vector3(0, 0.017, 0)))
	check(absf(left_screen.y - screen.y) < 1.0 and absf(right_screen.y - screen.y) < 1.0 and left_screen.x < screen.x and right_screen.x > screen.x, "Rear sight tops bracket the front sight at the same aim height")
	Input.action_press("gym_sprint")
	player.test_direction = Vector2(1, 0)
	var start_x: float = player.position.x
	await ticks(30)
	check(absf(player.position.x - start_x - 1.5) < 0.08, "ADS moves at 3 m/s even while sprint is held")
	player.test_direction = Vector2.ZERO
	Input.action_press("gym_crouch")
	await ticks(20)
	start_x = player.position.x
	player.test_direction = Vector2(1, 0)
	await ticks(30)
	check(player.is_crouching() and absf(player.position.x - start_x - 0.75) < 0.08, "Crouched ADS moves at 1.5 m/s")
	player.test_direction = Vector2.ZERO
	Input.action_release("gym_crouch")
	Input.action_release("gym_aim")
	await ticks(20)
	check(not pistol.is_ads() and is_equal_approx(player.camera.fov, 80.0) and player.get_node("HUD/Crosshair").visible, "Releasing ADS restores FOV and the hip-fire reticle")
	start_x = player.position.x
	player.test_direction = Vector2(1, 0)
	await ticks(30)
	check(absf(player.position.x - start_x - 4.0) < 0.08, "Releasing ADS restores held sprint without a leftover speed penalty")
	player.test_direction = Vector2.ZERO
	Input.action_release("gym_sprint")
	Input.action_press("gym_aim")
	await ticks(20)
	pistol.fire()
	pistol.request_reload()
	await ticks(20)
	check(pistol.is_reloading() and not pistol.is_ads() and is_equal_approx(player.camera.fov, 80.0), "Reload lowers ADS and restores normal FOV")
	await ticks(90)
	check(not pistol.is_reloading() and pistol.is_ads() and is_equal_approx(player.camera.fov, 70.0), "Still-held ADS returns after reload finishes")
	for i in 5:
		Input.action_release("gym_aim")
		await ticks(2)
		Input.action_press("gym_aim")
		await ticks(2)
	Input.action_release("gym_aim")
	await ticks(20)
	check(is_equal_approx(player.camera.fov, 80.0) and pistol.ads_blend == 0.0, "Interrupted ADS transitions return cleanly to hip fire")
	player.control_override = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	Input.action_press("gym_aim")
	await ticks(20)
	var shots_before: int = pistol.shot_count
	mouse_press()
	check(pistol.shot_count == shots_before, "First click after mouse release only recaptures the mouse")
	Input.action_release("gym_aim")
	player.control_override = true

func check_hits_and_cover() -> void:
	for target_name in ["Target1", "Target2", "Target3"]:
		var target: Node3D = gym.get_node("Targets/" + target_name)
		for ads in [false, true]:
			await place(Vector3(target.position.x, 0.05, 6))
			target.reset_target()
			if ads:
				Input.action_press("gym_aim")
				await ticks(20)
			aim_at(target.global_position)
			pistol.fire()
			check(target.health == 75, "%s shot aligns with %s" % ["ADS" if ads else "Hip-fire", target_name])
	var cover_target: Node3D = gym.get_node("MovementAnnex/CoverTarget")
	await place(Vector3(-29, 0.05, 5))
	cover_target.reset_target()
	aim_at(cover_target.global_position)
	pistol.fire()
	check(cover_target.health == 75, "Standing pistol shot clears the 1 m cover")
	Input.action_press("gym_crouch")
	Input.action_press("gym_aim")
	await ticks(40)
	aim_at(cover_target.global_position)
	pistol.fire()
	check(cover_target.health == 75, "Crouched ADS shot is stopped by cover")
	await place(Vector3(6, 0.05, 6))
	var target: Node3D = gym.get_node("Targets/Target1")
	target.reset_target()
	aim_at(target.global_position)
	var blocker := StaticBody3D.new()
	var shape_node := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = Vector3.ONE * 0.08
	shape_node.shape = shape
	blocker.add_child(shape_node)
	gym.add_child(blocker)
	blocker.global_position = pistol.get_node("Pose/Recoil/Muzzle").global_position
	await ticks(3)
	pistol.fire()
	check(target.health == 100 and pistol.last_hit.get("collider") == blocker, "Blocked muzzle cannot shoot through a nearby solid despite a clear sightline")
	blocker.queue_free()
	await ticks(3)

func check_recoil() -> void:
	await place(Vector3(6, 0.05, 6))
	pistol.fire()
	var hip_kick: float = pistol.camera_kick.x
	var hip_drift: float = pistol.aim_drift.x
	check(hip_kick > 0.0 and hip_drift > 0.0 and player.camera.global_basis.z.y < 0.0, "Firing changes both camera kick and actual aim")
	await ticks(120)
	check(pistol.aim_offset().length() < 0.0001, "Recoil recovers without permanent aim drift")
	pistol.reset_weapon()
	Input.action_press("gym_aim")
	await ticks(20)
	pistol.fire()
	check(absf(pistol.camera_kick.x / hip_kick - 0.5) < 0.01 and absf(pistol.aim_drift.x / hip_drift - 0.5) < 0.01, "ADS independently halves camera kick and aim drift")
	Input.action_release("gym_aim")

func check_runway() -> void:
	var runway := gym.get_node("MovementAnnex/Runway")
	await place(Vector3(-20, 0.05, 9))
	player.test_direction = Vector2(0, -1)
	await ticks(18)
	check(runway.running, "Runway still starts an ordinary walking attempt")
	Input.action_press("gym_aim")
	await ticks(3)
	check(not runway.running, "Entering ADS cancels the ordinary walk/sprint measurement")
	await place(Vector3(-20, 0.05, 9))
	Input.action_press("gym_aim")
	player.test_direction = Vector2(0, -1)
	await ticks(35)
	check(not runway.running, "ADS cannot start a misleading walk/sprint runway record")
	player.test_direction = Vector2.ZERO
	Input.action_release("gym_aim")
