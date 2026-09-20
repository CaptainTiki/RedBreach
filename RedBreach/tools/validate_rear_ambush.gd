extends SceneTree
var trial: Node3D
var player: CharacterBody3D
var mixed: Node3D
var checks := 0
var failures: Array[String] = []
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ", label)
	if not ok: failures.append(label)
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func reset() -> void:
	player.test_direction = Vector2.ZERO
	player.reset_player()
	await ticks(5)
	player.get_node("Health")._immunity = 1000
func freeze_front() -> void:
	for i in mini(5, mixed.enemies.size()): mixed.enemies[i].set_physics_process(false)
func position_at(point: Vector3) -> void:
	player.relocate(Transform3D(Basis.IDENTITY, point))
func event_time(kind: String) -> float:
	for event in trial.encounter_events:
		if event.id == "D" and event.event == kind: return event.time
	return -1.0
func event_count(kind: String) -> int:
	var count := 0
	for event in trial.encounter_events:
		if event.id == "D" and event.event == kind: count += 1
	return count
func visible_front() -> bool:
	for i in mini(5, mixed.enemies.size()):
		var enemy: CharacterBody3D = mixed.enemies[i]
		for offset in [Vector3(0,0.65,0), Vector3(0,1.0,0), Vector3(0.5,0.65,0), Vector3(-0.5,0.65,0)]:
			var ray := PhysicsRayQueryParameters3D.create(player.camera.global_position, enemy.global_position + offset, 1, [player.get_rid()])
			var hit := player.get_world_3d().direct_space_state.intersect_ray(ray)
			if not hit.is_empty() and hit.collider == enemy: return true
	return false
func move_to(point: Vector2, stop_on_sight: bool = false) -> bool:
	for i in 600:
		if stop_on_sight and visible_front():
			player.test_direction = Vector2.ZERO
			return true
		var offset := point - Vector2(player.position.x, player.position.z)
		if offset.length() < 0.1:
			player.test_direction = Vector2.ZERO
			return not stop_on_sight
		player.rotation.y = 0
		player.test_direction = offset.normalized()
		await ticks(1)
	player.test_direction = Vector2.ZERO
	return false
func verify_hidden_approach() -> void:
	var excluded: Array[RID] = [player.get_rid()]
	for encounter in trial.get_node("Encounters").get_children():
		for enemy in encounter.enemies: excluded.append(enemy.get_rid())
	var origins: Array[Vector3] = []
	for x in range(14):
		for z in range(7):
			for height in [1.0,1.62,2.8]: origins.append(Vector3(6.0 + x * 0.57,height,-39.65 + z * 0.55))
	for x in range(12):
		for z in range(16):
			for height in [1.0,1.62,2.8]: origins.append(Vector3(-5.5+x,height,-39.5+z))
	var leaks := 0
	var rays := 0
	for origin in origins:
		for enemy in mixed.enemies:
			for offset in [Vector3(0,0.3,0),Vector3(0,1.4,0),Vector3(0.65,0.7,0),Vector3(-0.65,0.7,0),Vector3(0,0.7,0.65),Vector3(0,0.7,-0.65)]:
				var ray := PhysicsRayQueryParameters3D.create(origin, enemy.global_position + offset, 1, excluded)
				rays += 1
				if player.get_world_3d().direct_space_state.intersect_ray(ray).is_empty():
					leaks += 1
					if leaks < 4: print("SIGHTLINE_LEAK: ", origin, " -> ", enemy.global_position + offset)
	print("PRETRIGGER_RAYS: ", rays, " / leaks: ", leaks)
	check(leaks == 0,"C and the full pre-trigger approach hide every room body at crouch, standing and jump heights")
func run() -> void:
	trial = load("res://encounters/route_trial.tscn").instantiate()
	trial.storage_enabled = false
	root.add_child(trial)
	player = trial.get_node("GymPlayer")
	mixed = trial.get_node("Encounters/D")
	player.control_override = true
	player.pistol.audio_enabled = false
	await ticks(20)
	check(mixed.enemies.size() == 5 and mixed._pending == 5 and mixed.state() == "Armed","D starts with five room enemies and exactly one pending rear small")
	await verify_hidden_approach()
	position_at(Vector3(12,0.05,-38))
	trial.start_run()
	await ticks(30)
	check(mixed.state() == "Armed" and not visible_front(),"Waiting before the corner cannot alert or shoot D")
	player.get_node("Health")._immunity = 1000
	var seen := await move_to(Vector2(18,-38),true)
	if not seen: seen = await move_to(Vector2(18,-32),true)
	print("FIRST_VISIBLE: ", player.position, " time=",trial.metrics.elapsed," start=",event_time("started"))
	check(seen and player.position.x < 22 and event_time("started") >= 0,"Actual approach crosses the trigger before a room bug is shootable, without entering D")
	check(await move_to(Vector2(18,-38)) and await move_to(Vector2(6.8,-38)),"Immediate retreat turns through the bend back toward C")
	await ticks(20)
	check(mixed.get_node("Vent").burst_count == 1 and mixed.enemies.size() == 6,"Rear hatch bursts and spawns even though the player never enters D")
	var delay := event_time("vent_burst") - event_time("started")
	var cue := event_time("enemy_spawned") - event_time("vent_burst")
	print("REAR_TIMING: delay=",delay," cue=",cue)
	check(absf(delay-1.75) < 0.04 and absf(cue-0.35) < 0.04,"Burst waits 1.75 seconds, then emergence waits another 0.35 seconds")
	check(mixed.state() == "Fighting" and trial.metrics.encounters.D.cleared < 0,"The rear bug is part of the still-active D encounter")
	await move_to(Vector2(15,-38))
	await move_to(Vector2(6.8,-38))
	check(event_count("started") == 1 and event_count("enemy_spawned") == 1,"Recrossing the trigger cannot duplicate the encounter or rear spawn")
	await reset()
	freeze_front()
	position_at(Vector3(6.8,0.05,-38))
	trial.start_run()
	mixed.begin()
	for enemy in mixed.enemies: enemy.register_hit(1000)
	await ticks(60)
	check(mixed.state() == "WaitingBurst" and mixed.get_node("Vent").burst_count == 0,"Five early front kills cannot clear D or skip the delayed burst")
	await ticks(70)
	check(mixed.enemies.size() == 6 and mixed.state() == "Fighting","Pending sixth enemy still emerges after the room is cleared")
	mixed.enemies[5].register_hit(1000)
	check(mixed.state() == "Cleared" and event_count("cleared") == 1,"Killing the rear small clears the six-enemy encounter exactly once")
	trial.storage_enabled = true
	trial.results_directory = "res://.godot/rear_ambush_qa_exports/" + str(Time.get_ticks_msec())
	trial.finish_run("qa")
	var events := FileAccess.open(trial.results_directory.path_join("encounter_events.csv"),FileAccess.READ)
	var saved: Array[String] = []
	if events != null:
		var header := events.get_csv_line()
		check(header.size() == 6,"Supplementary event CSV has a separate stable schema")
		while not events.eof_reached():
			var row := events.get_csv_line()
			if row.size() == 6 and row[3] == "D": saved.append(row[4])
	check(saved == ["started","vent_burst","enemy_spawned","cleared"],"Export preserves ordered start, burst, emergence and clear times for D")
	trial.storage_enabled = false
	for wait in [30,110]:
		await reset()
		freeze_front()
		trial.start_run()
		mixed.begin()
		await ticks(wait)
		await reset()
		await ticks(130)
		check(mixed.state() == "Armed" and mixed.enemies.size() == 5 and mixed.get_node("Vent").burst_count == 0,"Reset cancels pending work during " + ("pre-burst delay" if wait == 30 else "post-burst cue"))
	await reset()
	freeze_front()
	trial.start_run()
	mixed.begin()
	await ticks(30)
	player.get_node("Health")._immunity = 0
	player.get_node("Health").take_damage(1000)
	await ticks(140)
	check(trial.last_result.outcome == "death" and mixed.enemies.size() == 5 and mixed.get_node("Vent").burst_count == 0,"Death cancels the delayed hatch")
	await reset()
	freeze_front()
	position_at(Vector3(10,0.05,-39))
	trial.start_run()
	mixed.begin()
	await ticks(150)
	check(mixed.spawn_blocked and mixed.enemies.size() == 5,"A player close to the rear opening defers emergence instead of receiving a point-blank spawn")
	position_at(Vector3(18,0.05,-32))
	await ticks(15)
	check(mixed.enemies.size() == 6 and not mixed.spawn_blocked,"Moving away releases the pending rear small")
	var rear: CharacterBody3D = mixed.enemies[5]
	await ticks(270)
	print("REAR_NAV_END: ",rear.position)
	check(rear.position.distance_to(player.position) < 2.8,"Rear small physically leaves its recess and follows both bends to the player")
	await reset()
	freeze_front()
	position_at(Vector3(6.8,0.05,-38))
	trial.start_run()
	mixed.begin()
	await ticks(135)
	for i in range(1,6): mixed.enemies[i].set_physics_process(false)
	var regular: CharacterBody3D = mixed.enemies[0]
	regular.set_physics_process(true)
	await ticks(500)
	print("REGULAR_NAV_END: ",regular.position)
	check(regular.position.distance_to(player.position) < 3.0,"A front regular can chase a retreating player through the corner connector")
	for mode in ["sprint", "ADS"]:
		await reset()
		position_at(Vector3(12,0.05,-38))
		trial.start_run()
		Input.action_press("gym_sprint" if mode == "sprint" else "gym_aim")
		await ticks(3)
		var spotted := await move_to(Vector2(18,-38),true)
		if not spotted: spotted = await move_to(Vector2(18,-31),true)
		Input.action_release("gym_sprint")
		Input.action_release("gym_aim")
		print("REVEAL_",mode,": ",trial.metrics.elapsed-event_time("started")," seconds after trigger")
		check(spotted and event_time("started") >= 0 and player.position.x < 22, mode + " also triggers the rear sequence before first room sight")
		await ticks(150)
		check(mixed.get_node("Vent").burst_count == 1 and mixed.enemies.size() == 6,mode + " pause after reveal still produces exactly one rear small")
	trial.empty_route = true
	await reset()
	trial.start_run()
	position_at(Vector3(14,0.05,-38))
	await ticks(150)
	check(mixed.enemies.is_empty() and mixed.get_node("Vent").burst_count == 0,"Empty traversal disables both the front group and delayed rear hatch")
	trial.queue_free()
	await ticks(3)
	print("REAR_AMBUSH_QA: ",checks," checks; ",failures.size()," failures")
	quit(0 if failures.is_empty() else 1)
