extends SceneTree
## Verify this intentional source edit, traversal, and two build/save/reload cycles.
var gym: Node3D
var player: CharacterBody3D
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

func place(location: Vector3) -> void:
	Input.action_release("gym_jump")
	Input.action_release("gym_crouch")
	Input.action_release("gym_sprint")
	player.test_direction = Vector2.ZERO
	player.relocate(Transform3D(Basis.IDENTITY, location))
	await ticks(20)

func ray(start: Vector3, end: Vector3) -> Dictionary:
	return gym.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start, end, 1, [player.get_rid()]))

func floor_height(x: float, z: float) -> float:
	var hit := ray(Vector3(x, 3, z), Vector3(x, -1, z))
	return hit.position.y if not hit.is_empty() else -100.0

func verify_layout(phase: String) -> void:
	var old_clear := true
	for x in [-0.9, 0.0, 0.9]:
		for z in [-0.9, -0.5, -0.1, -3.9, -3.5, -3.1]:
			old_clear = old_clear and absf(floor_height(x, z)) < 0.01
	check(old_clear, phase + ": both old block footprints are clear floor")
	for data in [[-48.0, 0.75, "CoverLow"], [-44.0, 1.25, "CoverHigh"]]:
		var x: float = data[0]
		var height: float = data[1]
		var right_size := absf(floor_height(x, 10.5) - height) < 0.01
		for offset in [Vector3(-2, 0, 0), Vector3(2, 0, 0), Vector3(0, 0, -1), Vector3(0, 0, 1)]:
			var center := Vector3(x, height * 0.5, 10.5)
			var hit := ray(center + offset, center)
			var expected: Vector3 = center + offset * 0.5
			right_size = right_size and not hit.is_empty() and hit.position.distance_to(expected) < 0.01
		check(right_size, "%s: %s keeps its 2 x 1 m footprint and %.2f m height" % [phase, data[2], height])
		var label: Label3D = gym.get_node("Labels/" + data[2])
		check(label.global_position.distance_to(Vector3(x, height + 0.25, 10.1)) < 0.01 and label.global_basis.z.dot(Vector3.FORWARD) > 0.99, phase + ": " + data[2] + " label faces the approaches at its new location")
	check(gym.get_node("Geometry").find_children("*", "CollisionShape3D", true, false).size() == 69, phase + ": brush collision count stays 69")
	check(gym.has_node("DoorModule") and gym.get_node("Targets").get_child_count() == 3 and gym.get_node("MovementAnnex/JumpLanes").get_child_count() == 4, phase + ": authored door, targets, and jump stations survive")
	var clear_routes := true
	for x in [-50.0, -48.0, -46.0, -44.0, -42.0, -38.0, -34.0, -30.0, -26.0, -22.0, -18.0]:
		for z in [6.1, 8.0, 9.9]:
			clear_routes = clear_routes and absf(floor_height(x, z)) < 0.01
	check(clear_routes and absf(floor_height(-46, 10.5)) < 0.01 and absf(floor_height(-48, 11.5)) < 0.01, phase + ": staging route, 2 m block gap, and rear clearance stay open")

func run() -> void:
	var source := FileAccess.get_file_as_string("res://maps/gym_01.map")
	var saved_scene := FileAccess.get_file_as_string("res://gym/gym.tscn")
	gym = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	player.control_override = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(30)
	verify_layout("Saved gym")
	await place(Vector3(0, 0.05, 1))
	player.test_direction = Vector2(0, -1)
	await ticks(72)
	check(player.position.z < -4.5 and player.position.y < 0.1, "Player walks through both old block locations without ghost collision")
	await place(Vector3(-20, 0.05, 8))
	player.test_direction = Vector2(-1, 0)
	await ticks(348)
	check(player.position.x < -48.5 and player.position.y < 0.1, "Player crosses staging from runway to the jump stations")
	await place(Vector3(-48, 0.05, 9.1))
	Input.action_press("gym_jump")
	player.test_direction = Vector2(0, 1)
	await ticks(2)
	Input.action_release("gym_jump")
	for i in 35:
		if player.position.z >= 10.35:
			break
		await ticks(1)
	player.test_direction = Vector2.ZERO
	await ticks(50)
	check(absf(player.position.y - 0.75) < 0.03 and player.is_grounded(), "Normal jump reaches the relocated 0.75 m block")
	await place(Vector3(-44, 0.05, 9.1))
	Input.action_press("gym_jump")
	player.test_direction = Vector2(0, 1)
	await ticks(2)
	Input.action_release("gym_jump")
	await ticks(70)
	player.test_direction = Vector2.ZERO
	check(player.position.z < 10.0 and player.position.y < 0.1, "The 1.25 m block still cannot be mounted directly from the floor")
	await place(Vector3(-47.5, 0.8, 10.5))
	Input.action_press("gym_jump")
	player.test_direction = Vector2(1, 0)
	await ticks(2)
	Input.action_release("gym_jump")
	for i in 65:
		if player.position.x >= -44.6:
			break
		await ticks(1)
	player.test_direction = Vector2.ZERO
	await ticks(40)
	check(absf(player.position.y - 1.25) < 0.03 and player.is_grounded(), "Player can still jump from the low block onto the high block")
	for attempt in range(2):
		await place(Vector3(0, 0.05, 9))
		player.set_physics_process(false)
		var geometry: FuncGodotMap = gym.get_node("Geometry")
		geometry.build()
		await ticks(3)
		for node in geometry.find_children("*", "", true, false):
			node.owner = gym
		var packed := PackedScene.new()
		var packed_ok := packed.pack(gym) == OK
		var path := "res://.godot/gym_alteration_roundtrip_%d.tscn" % attempt
		var saved_ok := ResourceSaver.save(packed, path) == OK
		check(packed_ok and saved_ok, "Altered source builds and saves on cycle %d" % (attempt + 1))
		root.remove_child(gym)
		gym.free()
		gym = (load(path) as PackedScene).instantiate()
		root.add_child(gym)
		player = gym.get_node("GymPlayer")
		player.control_override = true
		player.set_physics_process(false)
		await ticks(3)
		verify_layout("Build/save/reload %d" % (attempt + 1))
	check(FileAccess.get_file_as_string("res://maps/gym_01.map") == source and FileAccess.get_file_as_string("res://gym/gym.tscn") == saved_scene, "Round-trip QA leaves the canonical map and saved scene unchanged")
	print("GYM_ALTERATION_QA: ", "PASS" if failures.is_empty() else "FAIL", " (", failures.size(), " failures)")
	quit(0 if failures.is_empty() else 1)
