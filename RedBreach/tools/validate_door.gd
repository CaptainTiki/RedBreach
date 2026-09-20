extends SceneTree
## Exercises the saved gym, real physics, player aim/range, and the addon state graph.
var gym: Node3D
var player: CharacterBody3D
var door: Node3D
var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("run")

func ticks(count: int) -> void:
	for i in count:
		await physics_frame
	await process_frame

func check(condition: bool, message: String) -> void:
	print("PASS: " if condition else "FAIL: ", message)
	if not condition:
		failures.append(message)

func place(position: Vector3, look_target: Vector3) -> void:
	player.test_direction = Vector2.ZERO
	player.global_position = position
	player.velocity = Vector3.ZERO
	var direction := (look_target - (position + Vector3.UP * 1.65)).normalized()
	player.rotation.y = atan2(-direction.x, -direction.z)
	player.set("_pitch", asin(direction.y))
	player.reset_camera_interpolation()
	await ticks(3)

func use_switch() -> void:
	var key := InputEventKey.new()
	key.physical_keycode = KEY_E
	key.pressed = true
	player._unhandled_input(key)
	await ticks(2)

func panel_ray() -> Dictionary:
	return gym.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(2, 1, 5), Vector3(2, 1, 3), 1, [player.get_rid()]))

func blocker(rigid: bool = false) -> PhysicsBody3D:
	var body: PhysicsBody3D
	if rigid:
		var crate := RigidBody3D.new()
		crate.freeze = true
		body = crate
	else:
		body = CharacterBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(0.6, 1.8, 0.6)
	shape.shape = box
	body.add_child(shape)
	gym.add_child(body)
	body.global_position = Vector3(2, 0.9, 4)
	return body

func run() -> void:
	gym = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	player.control_override = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	door = gym.get_node("DoorModule")
	await ticks(5)
	check(door.get_node("StateChart") is StateChart and door.state_name() == "Closed", "Saved instance starts in the addon Closed state")
	check(InputMap.action_get_events("gym_interact")[0].physical_keycode == KEY_E, "Interaction is bound to physical E")
	check(not panel_ray().is_empty(), "Closed leaves block the opening")
	await place(Vector3(2, 0.05, 6), Vector3(2, 1.65, 3))
	player.test_direction = Vector2(0, -1)
	await ticks(35)
	check(player.position.z > 4.35, "Player cannot walk through the closed door")
	await place(Vector3(3.5, 0.05, 8), Vector3(3.5, 1.35, 4.34))
	check(player.interaction_target() == null and not player.try_interact(), "Out-of-range switch cannot be used")
	await place(Vector3(3.5, 0.05, 6), Vector3(3.5, 1.35, 4.34))
	check(player.interaction_target() == door.get_node("SwitchFront"), "Front switch can be targeted within 2 m")
	check(player.get_node("HUD/Interaction").text.contains("Open door"), "Context prompt describes opening")
	var occluder := StaticBody3D.new()
	var occluder_shape := CollisionShape3D.new()
	var occluder_box := BoxShape3D.new()
	occluder_box.size = Vector3(0.7, 0.7, 0.1)
	occluder_shape.shape = occluder_box
	occluder.add_child(occluder_shape)
	gym.add_child(occluder)
	occluder.position = Vector3(3.5, 1.5, 5)
	await ticks(3)
	check(player.interaction_target() == null and not player.try_interact(), "Solid geometry prevents using a switch through a wall")
	occluder.queue_free()
	await ticks(3)
	await use_switch()
	check(door.state_name() == "Opening" and door.open_amount > 0.0, "E starts opening through the state chart")
	check(not door.request_toggle() and door.state_name() == "Opening", "Repeated requests do not restart or cancel opening")
	await ticks(60)
	check(door.state_name() == "Open" and is_equal_approx(door.open_amount, 1.0), "Opening reaches the fully Open state")
	check(panel_ray().is_empty(), "Open leaves clear the passage")
	check(player.get_node("HUD/Interaction").text.contains("Close door"), "Switch prompt updates to closing")
	await place(Vector3(2, 0.05, 6), Vector3(2, 1.65, 3))
	player.test_direction = Vector2(0, -1)
	await ticks(42)
	check(player.position.z < 3.0, "Player traverses the open 2 m doorway")
	await place(Vector3(3.5, 0.05, 2), Vector3(3.5, 1.35, 3.66))
	check(player.interaction_target() == door.get_node("SwitchBack"), "The rear switch is usable from the other side")
	await use_switch()
	check(door.state_name() == "Closing", "Rear switch requests closure")
	await ticks(60)
	check(door.state_name() == "Closed" and not panel_ray().is_empty(), "Closing restores solid collision")
	await use_switch()
	await ticks(60)
	await use_switch()
	await ticks(10)
	var part_closed: float = door.open_amount
	await use_switch()
	check(door.state_name() == "Opening" and door.open_amount >= part_closed, "A second press safely reverses a closing door")
	await ticks(60)
	var stand_in := blocker()
	await ticks(3)
	await use_switch()
	check(door.state_name() == "Blocked" and door.open_amount > 0.99, "An occupied doorway refuses to close")
	check(door.get_node("StatusBack").text.contains("BLOCKED"), "Blocked feedback appears on both sides")
	await ticks(40)
	check(door.state_name() == "Blocked" and not door.request_toggle(), "Blocked door remains open despite repeated requests")
	stand_in.queue_free()
	await ticks(4)
	check(door.state_name() == "Open", "Clearing the doorway returns to Open")
	await ticks(70)
	check(door.state_name() == "Open", "The door does not automatically retry closure")
	await use_switch()
	await ticks(12)
	var before_block: float = door.open_amount
	stand_in = blocker()
	await ticks(3)
	check(door.state_name() == "Blocked" and door.open_amount >= before_block - 0.03, "A new obstruction during closing triggers reopening")
	await ticks(60)
	check(door.open_amount > 0.99 and stand_in.position.distance_to(Vector3(2, 0.9, 4)) < 0.001, "Door fully reopens without displacing the blocker")
	stand_in.queue_free()
	await ticks(4)
	var crate := blocker(true)
	await ticks(3)
	await use_switch()
	check(door.state_name() == "Blocked", "Rigid-body props also prevent closure")
	crate.queue_free()
	await ticks(4)
	await place(Vector3(3.5, 0.05, 6), Vector3(3.5, 1.35, 4.34))
	await use_switch()
	await ticks(6)
	await place(Vector3(2, 0.05, 5.5), Vector3(2, 1.65, 3))
	Input.action_press("gym_sprint")
	player.test_direction = Vector2(0, -1)
	await ticks(32)
	Input.action_release("gym_sprint")
	check(player.position.z < 3.0, "A sprinting player is not trapped by the closing leaves")
	await ticks(50)
	check(door.state_name() == "Open", "Door stays open after the player clears it")
	await place(Vector3(3.5, 0.05, 6), Vector3(3.5, 1.35, 4.34))
	var active_count := 0
	for state in door.get_node("StateChart/Movement").get_children():
		if state is StateChartState and state.active:
			active_count += 1
	check(active_count == 1, "Exactly one door state is active")
	var second: Node3D = load("res://interaction/sliding_door.tscn").instantiate()
	gym.add_child(second)
	second.position = Vector3(8, 0, 8)
	await ticks(4)
	check(second.state_name() == "Closed" and door.state_name() == "Open", "Reusable door instances have independent state")
	second.queue_free()
	gym.get_node("Geometry").build()
	await ticks(3)
	check(door.get_parent() == gym and door.state_name() == "Open", "Map rebuild preserves the door instance and state graph")
	await use_switch()
	await ticks(60)
	check(door.state_name() == "Closed", "Door still operates after map rebuild")
	print("GYM_DOOR_QA: ", "PASS" if failures.is_empty() else "FAIL", " (", failures.size(), " failures)")
	quit(0 if failures.is_empty() else 1)
