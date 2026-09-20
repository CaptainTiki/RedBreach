extends SceneTree
var trial: Node3D
var player: CharacterBody3D
var checks := 0
var failures: Array[String] = []
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ",label)
	if not ok: failures.append(label)
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func walk_to(point: Vector2, kill_enemies: bool = false) -> bool:
	for i in 1200:
		var offset := point - Vector2(player.position.x,player.position.z)
		if offset.length() < 0.12:
			player.test_direction = Vector2.ZERO
			return true
		player.rotation.y = 0
		player.test_direction = offset.normalized()
		if kill_enemies:
			for encounter in trial.get_node("Encounters").get_children():
				for enemy in encounter.enemies:
					if enemy.health > 0.0 and enemy.state() != "Dormant": enemy.register_hit(1000)
		await ticks(1)
	player.test_direction = Vector2.ZERO
	return false
func empty_pass(sprint: bool) -> Dictionary:
	trial.empty_route = true
	player.reset_player()
	await ticks(5)
	if sprint: Input.action_press("gym_sprint")
	else: Input.action_release("gym_sprint")
	for point in [Vector2(0,-38),Vector2(18,-38),Vector2(18,-31),Vector2(30,-31),Vector2(30,3)]:
		check(await walk_to(point),"%s route reaches %s" % ["Sprint" if sprint else "Walk",point])
	await ticks(3)
	check(trial.state() == "Finished" and trial.last_result.outcome == "complete", "Actual finish trigger completes empty route")
	Input.action_release("gym_sprint")
	return trial.last_result.duplicate(true)
func run() -> void:
	trial = load("res://encounters/route_trial.tscn").instantiate()
	trial.storage_enabled = false
	root.add_child(trial)
	player = trial.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	await ticks(20)
	check(trial.state() == "Ready", "Saved route loads ready")
	check(trial.get_node("Geometry").find_children("*","CollisionShape3D",true,false).size() == 63, "Route has 63 saved source brush colliders")
	check(trial.get_node("Navigation").navigation_mesh.get_polygon_count() > 0, "Route navigation is saved and baked")
	check(trial.get_node("Encounters").get_child_count() == 5, "Three rooms and two vent encounters are authored")
	var preplaced := 0
	for encounter in trial.get_node("Encounters").get_children(): preplaced += encounter.enemies.size()
	check(preplaced == 8, "Eight room enemies exist before entering route; four vent enemies wait")
	check(is_equal_approx(player.walk_speed,5.0) and is_equal_approx(player.sprint_speed,8.0), "Established movement speeds are preserved")
	var walked := await empty_pass(false)
	print("MEASURED_EMPTY_WALK: ",walked.elapsed," seconds / ",walked.distance," metres")
	check(absf(walked.elapsed - 22.8) < 0.4 and absf(walked.distance-114.0) < 1.2, "Actual empty walk agrees with the 114 m route baseline")
	check(walked.active_seconds == 0.0 and is_equal_approx(walked.quiet_seconds,walked.elapsed), "Empty mode has no artificial combat time")
	var sprinted := await empty_pass(true)
	print("MEASURED_EMPTY_SPRINT: ",sprinted.elapsed," seconds / ",sprinted.distance," metres")
	check(absf(sprinted.elapsed-14.25) < 0.4 and sprinted.elapsed < walked.elapsed, "Actual empty sprint agrees with movement speed")
	trial.empty_route = false
	player.reset_player()
	await ticks(5)
	player.get_node("Health").invulnerability_seconds = 1000
	for point in [Vector2(0,-38),Vector2(18,-38),Vector2(18,-31),Vector2(30,-31),Vector2(30,3)]:
		check(await walk_to(point,true),"Combat route traverses " + str(point))
	await ticks(3)
	check(trial.state() == "Finished" and trial.last_result.outcome == "complete" and trial.metrics.cleared_count() == 5, "Real trigger route can clear all five encounters and finish")
	var count := 0
	for encounter in trial.get_node("Encounters").get_children(): count += encounter.enemies.size()
	check(count == 12, "All twelve enemies instantiate exactly once across the route")
	check(trial.metrics.encounters.B.first_spawn >= trial.metrics.encounters.B.started + 0.3, "Vent cue delay is included in the encounter split")
	check(trial.metrics.encounters.A.first_damage >= trial.metrics.encounters.A.started and trial.metrics.encounters.A.cleared >= trial.metrics.encounters.A.first_damage, "Room alert, first damage and clear timestamps are ordered")
	check(is_equal_approx(trial.metrics.elapsed,trial.metrics.active_seconds+trial.metrics.quiet_seconds), "Full route partitions elapsed time without double counting")
	# Nav paths must link the rooms, vent recesses, and both corners.
	var map: RID = trial.get_node("Navigation").get_navigation_map()
	for point in [Vector3(-3.8,0,-20),Vector3(-3,0,-35),Vector3(35,0,-29),Vector3(33.8,0,-16)]:
		var path := NavigationServer3D.map_get_path(map,Vector3(0,0,6),point,true)
		check(path.size() > 1 and path[-1].distance_to(point) < 1.0, "Navigation reaches enemy position " + str(point))
	player.reset_player()
	await ticks(5)
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(0,0.05,-14)))
	trial.start_run()
	trial.get_node("Encounters/B").begin()
	await ticks(28)
	var vent_enemy: CharacterBody3D = trial.get_node("Encounters/B").enemies[0]
	var emergence: Vector3 = vent_enemy.global_position
	await ticks(60)
	check(vent_enemy.global_position.distance_to(emergence) > 1.0 and vent_enemy.position.x > -2.8, "Spawned bug physically exits the vent recess using baked navigation")
	player.reset_player()
	await ticks(5)
	trial.start_run()
	player.pistol.fire()
	player.get_node("Health").take_damage(20)
	await ticks(3)
	check(trial.metrics.shots == 1 and trial.metrics.incoming_damage == 20, "Real pistol and health signals record shots and damage")
	trial._on_finish(player)
	check(trial.last_result.outcome == "bypassed", "Finishing without clears is labelled bypassed")
	player.reset_player()
	await ticks(5)
	trial.start_run()
	player.get_node("Health").take_damage(1000)
	await ticks(3)
	check(trial.last_result.outcome == "death" and trial.state() == "Finished", "Death ends and labels the run")
	check(get_nodes_in_group("combat_projectiles").is_empty(), "Death clears projectiles")
	player.reset_player()
	await ticks(5)
	trial.start_run()
	trial.get_node("Encounters/B").begin()
	player.reset_player()
	await ticks(40)
	check(trial.state() == "Ready" and trial.metrics.elapsed == 0.0 and trial.get_node("Encounters/B").enemies.is_empty(), "Reset during vent cue cancels delayed spawn and timer")
	check(trial.last_result.outcome == "aborted_reset", "Reset preserves explicit aborted result")
	var key := InputEventKey.new()
	key.physical_keycode = KEY_F4
	key.pressed = true
	trial._unhandled_input(key)
	await ticks(3)
	check(trial.empty_route and trial.state() == "Ready", "F4 changes mode and resets safely")
	# Export test uses ignored QA files, separate from the user's playtest records.
	trial.storage_enabled = true
	trial.results_directory = "res://.godot/route_qa_exports/" + str(Time.get_ticks_msec())
	trial.start_run()
	await ticks(4)
	trial.finish_run("complete")
	var file := FileAccess.open(trial.results_directory.path_join("runs.csv"),FileAccess.READ)
	check(file != null, "Run CSV is created locally")
	if file != null:
		var header := file.get_csv_line()
		var values := file.get_csv_line()
		check(header.size() == values.size() and JSON.parse_string(values[-1]) is Dictionary, "CSV escaping preserves the configuration JSON")
	check(trial.export_status.begins_with("Saved"), "Successful export is shown")
	trial.results_directory = "res://project.godot"
	player.reset_player()
	await ticks(3)
	trial.start_run()
	trial.finish_run("complete")
	check(trial.export_status.begins_with("RESULT SAVE FAILED"), "Unwritable export is reported rather than silently lost")
	trial.results_directory = "res://.godot/route_exit_qa/" + str(Time.get_ticks_msec())
	player.reset_player()
	await ticks(3)
	trial.start_run()
	await ticks(3)
	var exit_csv: String = trial.results_directory.path_join("runs.csv")
	trial.queue_free()
	await ticks(3)
	check(FileAccess.file_exists(exit_csv), "Scene exit records an aborted attempt")
	if FileAccess.file_exists(exit_csv):
		var exit_file := FileAccess.open(exit_csv,FileAccess.READ)
		exit_file.get_csv_line()
		check(exit_file.get_csv_line()[2] == "aborted_scene_exit", "Scene exit does not masquerade as completion")
	print("ROUTE_QA: ",checks," checks; ",failures.size()," failures")
	quit(0 if failures.is_empty() else 1)
