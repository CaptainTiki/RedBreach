extends SceneTree
## Run with --fixed-fps 120: samples the real rendered camera between 60 Hz physics ticks.
var player: CharacterBody3D
var phase := ""
var samples: Array[Dictionary] = []
var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("run")

func _process(_delta: float) -> bool:
	if is_instance_valid(player) and not phase.is_empty():
		samples.append({"phase": phase, "body": player.position, "eye": player.camera.global_position, "floor": player.is_on_floor()})
	return false

func ticks(count: int) -> void:
	for i in count:
		await physics_frame
	await process_frame

func place(location: Vector3) -> void:
	phase = ""
	player.test_direction = Vector2.ZERO
	player.position = location
	player.rotation = Vector3.ZERO
	player.velocity = Vector3.ZERO
	player.reset_camera_interpolation()
	await ticks(20)

func check(condition: bool, message: String) -> void:
	print("PASS: " if condition else "FAIL: ", message)
	if not condition:
		failures.append(message)

func motion_summary(label: String, min_z: float, max_z: float) -> Dictionary:
	var result := {"frames": 0, "airborne": 0, "max_rise": 0.0, "max_drop": 0.0, "max_lag": 0.0, "moving_frames": 0}
	var previous: Dictionary = {}
	for row in samples:
		if row.phase != label or row.body.z <= min_z or row.body.z >= max_z:
			continue
		result.frames += 1
		if not row.floor:
			result.airborne += 1
		result.max_lag = maxf(result.max_lag, absf(row.eye.y - row.body.y - 1.65))
		if not previous.is_empty():
			var rise: float = row.eye.y - previous.eye.y
			result.max_rise = maxf(result.max_rise, rise)
			result.max_drop = minf(result.max_drop, rise)
			if absf(row.eye.z - previous.eye.z) > 0.0001:
				result.moving_frames += 1
		previous = row
	print(label, ": ", result)
	return result

func run() -> void:
	var gym: Node3D = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	player.control_override = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await place(Vector3(-5, 0.05, 1))
	phase = "ramp_up"
	player.test_direction = Vector2(0, -1)
	await ticks(105)
	check(player.position.y > 1.95 and player.position.z < -6.0, "Ramp still reaches landing")
	var ramp := motion_summary(phase, -5.0, -1.0)
	check(ramp.frames > 70 and ramp.airborne == 0, "Continuous floor contact on ramp interior")
	check(ramp.max_drop > -0.001 and ramp.max_rise < 0.02, "Ramp view rises steadily without lift/drop cycles")
	check(ramp.moving_frames > ramp.frames * 0.9, "Camera moves on render frames between physics ticks")
	phase = "ramp_down"
	player.test_direction = Vector2(0, 1)
	await ticks(105)
	var ramp_down := motion_summary(phase, -5.0, -1.0)
	check(ramp_down.airborne == 0 and ramp_down.max_rise < 0.001, "Downhill motion stays grounded and monotonic")
	await place(Vector3(-9, 0.05, -1))
	phase = "stairs_up"
	player.test_direction = Vector2(0, -1)
	await ticks(75)
	var stairs := motion_summary(phase, -6.0, -2.0)
	check(player.position.y > 1.95 and player.position.z < -6.0, "Stair smoothing preserves traversal")
	check(stairs.frames > 60 and stairs.max_rise < 0.06, "Camera spreads 0.25 m stair pops over multiple frames")
	check(stairs.max_lag < 0.5, "Stair camera stays near eye height")
	phase = "stairs_down"
	player.test_direction = Vector2(0, 1)
	await ticks(80)
	var downstairs := motion_summary(phase, -5.5, -2.0)
	check(player.position.y < 0.1 and player.position.z > -2.0, "Descend the complete stair flight")
	check(downstairs.max_drop > -0.06, "Descending stairs has no single-frame eye drops")
	phase = ""
	player.reset_player()
	check(player.camera.global_position.distance_to(player.position + Vector3.UP * 1.65) < 0.001, "Reset snaps the camera without dragging across the gym")
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		var previous_aim: Vector3 = player.camera.global_basis.z
		var look := InputEventMouseMotion.new()
		look.relative = Vector2(80, -30)
		player._unhandled_input(look)
		check(player.camera.global_basis.z.angle_to(previous_aim) > 0.1, "Mouse look changes camera aim immediately, before the next frame")
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	print("GYM_MOTION_QA: ", "PASS" if failures.is_empty() else "FAIL", " (", failures.size(), " failures)")
	quit(0 if failures.is_empty() else 1)
