extends SceneTree
## Reload the saved scene and exercise actual Jolt collision and player movement.

var failures: Array[String] = []
var gym: Node3D
var player: CharacterBody3D

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	if condition:
		print("PASS: ", message)
	else:
		failures.append(message)
		push_error("FAIL: " + message)

func ticks(count: int) -> void:
	for i in count:
		await physics_frame
	await process_frame

func teleport(location: Vector3) -> void:
	player.global_position = location
	player.rotation = Vector3.ZERO
	player.velocity = Vector3.ZERO
	player.test_direction = Vector2.ZERO
	player.reset_camera_interpolation()
	await ticks(20)

func ray(start: Vector3, end: Vector3) -> Dictionary:
	return gym.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start, end, 1, [player.get_rid()]))

func run() -> void:
	gym = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	player.control_override = true
	await ticks(30)
	check(player.is_on_floor() and absf(player.position.y) < 0.08, "Saved scene has a solid floor at spawn")
	check(gym.get_node("Geometry").find_children("*", "CollisionShape3D", true, false).size() == 26, "All 26 brush collision shapes survive save/reload")
	check(InputMap.action_get_events("gym_sprint")[0].physical_keycode == KEY_SHIFT, "Sprint is bound to physical Shift")
	check(InputMap.action_get_events("gym_jump")[0].physical_keycode == KEY_SPACE, "Jump is bound to physical Space")
	await teleport(Vector3(0, 0.05, 9))
	player.test_direction = Vector2(1, 0)
	await ticks(30)
	var walk_distance: float = player.position.x
	await teleport(Vector3(0, 0.05, 9))
	Input.action_press("gym_sprint")
	player.test_direction = Vector2(1, 0)
	await ticks(30)
	Input.action_release("gym_sprint")
	check(player.position.x > walk_distance * 1.4, "Sprint moves faster than walk")
	await teleport(Vector3(0, 0.05, 9))
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	Input.action_press("gym_jump")
	await ticks(12)
	Input.action_release("gym_jump")
	check(player.position.y > 0.6, "Jump leaves the floor")
	await ticks(60)
	check(player.is_on_floor() and player.position.y < 0.1, "Jump lands on the floor")
	var floor_hit := ray(Vector3(3, 2, 8), Vector3(3, -1, 8))
	check(not floor_hit.is_empty() and absf(floor_hit.position.y) < 0.01, "Floor scale and height")
	var wall_hit := ray(Vector3(0, 1, 9), Vector3(20, 1, 9))
	check(not wall_hit.is_empty() and absf(wall_hit.position.x - 12.0) < 0.02, "24 m clear interior width")
	var ramp_hit := ray(Vector3(-5, 4, -3), Vector3(-5, -1, -3))
	check(not ramp_hit.is_empty() and absf(ramp_hit.position.y - 1.0) < 0.02, "Ramp midpoint height is 1 m")
	gym.get_node("DoorModule").request_toggle()
	await ticks(60)
	for entry in [Vector2(-8, 1), Vector2(-3, 1.5), Vector2(2, 2)]:
		await teleport(Vector3(entry.x, 0.05, 6))
		player.test_direction = Vector2(0, -1)
		await ticks(42)
		check(player.position.z < 3.0, "%s m doorway is traversable" % entry.y)
	await teleport(Vector3(-9, 0.05, -1))
	player.test_direction = Vector2(0, -1)
	await ticks(72)
	print("Stair end: ", player.position)
	check(player.position.z < -6.0 and player.position.y > 1.95, "Climb all eight 0.25 m stairs without jumping")
	await teleport(Vector3(-5, 0.05, 1))
	player.test_direction = Vector2(0, -1)
	await ticks(102)
	print("Ramp end: ", player.position)
	check(player.position.z < -6.0 and player.position.y > 1.95, "Walk up the 1:3 ramp")
	player.test_direction = Vector2(0, 1)
	await ticks(102)
	check(player.position.z > 0.0 and player.position.y < 0.1, "Walk down the ramp with floor contact")
	await teleport(Vector3(10, 0.05, 8))
	player.test_direction = Vector2(1, 0)
	await ticks(50)
	check(player.position.x < 11.75, "Perimeter wall stops the player")
	await teleport(Vector3(6, 0.05, 6))
	check(player.fire_probe(), "Probe hits the nearest target")
	check(gym.get_node("Targets/Target1").hit_count == 1, "Target receives hit feedback")
	for target_data in [[7.6, "Target2"], [9.2, "Target3"]]:
		await teleport(Vector3(target_data[0], 0.05, 6))
		check(player.fire_probe(), "Probe hits " + target_data[1])
		check(gym.get_node("Targets/" + target_data[1]).hit_count == 1, target_data[1] + " receives hit feedback")
	player.position = Vector3(0, -11, 0)
	await ticks(3)
	check(player.position.distance_to(player.spawn_transform.origin) < 0.1, "Fall recovery returns to spawn")
	var geometry: FuncGodotMap = gym.get_node("Geometry")
	var before := geometry.find_children("*", "CollisionShape3D", true, false).size()
	geometry.build()
	await ticks(3)
	check(geometry.find_children("*", "CollisionShape3D", true, false).size() == before, "Second build does not duplicate geometry")
	check(gym.has_node("GymPlayer") and gym.get_node("Targets").get_child_count() == 3, "Rebuild preserves gameplay siblings")
	# Change the floor in a temporary source-map copy, build, save, and reload it.
	var source := FileAccess.get_file_as_string("res://maps/gym_01.map")
	var floor_start := source.find("// 24m clear floor")
	var floor_end := source.find("}", floor_start)
	var floor_brush := source.substr(floor_start, floor_end - floor_start)
	var vertices := RegEx.new()
	vertices.compile("\\( (-?[0-9.]+) (-?[0-9.]+) 0 \\)")
	var raised_brush := vertices.sub(floor_brush, "( $1 $2 16 )", true)
	var edited_source := source.substr(0, floor_start) + raised_brush + source.substr(floor_end)
	var probe_path := "res://.godot/gym_rebuild_probe.map"
	var probe_file := FileAccess.open(probe_path, FileAccess.WRITE)
	probe_file.store_string(edited_source)
	probe_file.close()
	player.set_physics_process(false)
	geometry.global_map_file = ProjectSettings.globalize_path(probe_path)
	geometry.build()
	await ticks(3)
	var raised_hit := ray(Vector3(3, 2, 8), Vector3(3, -1, 8))
	check(not raised_hit.is_empty() and absf(raised_hit.position.y - 0.5) < 0.02, "Edited map source changes floor collision to 0.5 m")
	for node in geometry.find_children("*", "", true, false):
		node.owner = gym
	var probe_scene := PackedScene.new()
	var pack_result := probe_scene.pack(gym)
	var save_result := ResourceSaver.save(probe_scene, "res://.godot/gym_rebuild_probe.tscn")
	check(pack_result == OK and save_result == OK, "Edited build serializes successfully")
	root.remove_child(gym)
	gym.free()
	gym = load("res://.godot/gym_rebuild_probe.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	player.set_physics_process(false)
	await ticks(3)
	var reload_hit := ray(Vector3(3, 2, 8), Vector3(3, -1, 8))
	check(not reload_hit.is_empty() and absf(reload_hit.position.y - 0.5) < 0.02, "Edited floor survives saved-scene reload")
	check(FileAccess.get_file_as_string("res://maps/gym_01.map") == source, "Canonical editable map is unchanged by QA")
	print("GYM_QA: ", "PASS" if failures.is_empty() else "FAIL", " (", failures.size(), " failures)")
	quit(0 if failures.is_empty() else 1)
