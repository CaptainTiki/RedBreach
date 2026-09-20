extends Node3D
const Metrics = preload("res://encounters/route_metrics.gd")
@export var route_revision: String = "04"
@export var storage_enabled: bool = true
@export var results_directory: String = "user://route_trials"
var empty_route: bool = false
var metrics = Metrics.new()
var previous_position := Vector3.ZERO
var previous_health: float = 100.0
var last_result: Dictionary = {}
var result_text: String = ""
var export_status: String = ""
var run_id: String = ""
var configuration: Dictionary = {}
var encounter_events: Array[Dictionary] = []

func _enter_tree() -> void:
	if not EngineDebugger.is_active(): $RunChart.track_in_editor = false
func _ready() -> void:
	add_to_group("combat_gym")
	$Start.body_entered.connect(_on_start)
	$Finish.body_entered.connect(_on_finish)
	$GymPlayer/Health.died.connect(_on_death)
	$GymPlayer/Health.health_changed.connect(_on_health_changed)
	$GymPlayer.pistol.shot_fired.connect(_on_shot)
	for encounter in $Encounters.get_children():
		encounter.started.connect(_on_encounter_started)
		encounter.vent_burst.connect(_on_vent_burst)
		encounter.enemy_spawned.connect(_on_enemy_spawned)
		encounter.enemy_damaged.connect(_on_enemy_damaged)
		encounter.cleared.connect(_on_encounter_cleared)
	reset_encounter.call_deferred()
func state() -> String:
	for child in $RunChart/Run.get_children():
		if child.get("active") == true: return child.name
	return ""
func is_running() -> bool: return state() == "Running"
func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_F4:
		if is_running(): finish_run("aborted_mode_change")
		empty_route = not empty_route
		$GymPlayer.reset_player()
		get_viewport().set_input_as_handled()
func reset_encounter() -> void:
	if is_running(): finish_run("aborted_reset")
	$RunChart.send_event("reset")
	_clear_projectiles()
	$Effects.clear_effects()
	get_tree().call_group("combat_pickups", "reset_pickup")
	metrics = Metrics.new()
	encounter_events.clear()
	for encounter in $Encounters.get_children():
		encounter.prepare($GymPlayer, not empty_route, self)
		metrics.register(encounter.encounter_id, encounter.title, encounter.enemy_scenes.size())
	previous_position = $GymPlayer.global_position
	previous_health = $GymPlayer/Health.health
	result_text = ""
	export_status = ""
	_update_hud()
func _on_start(body: Node3D) -> void:
	if body == $GymPlayer: start_run()
func start_run() -> bool:
	if state() != "Ready" or not $GymPlayer.is_alive(): return false
	$RunChart.send_event("start")
	previous_position = $GymPlayer.global_position
	run_id = Time.get_datetime_string_from_system().replace(":", "-") + "_" + str(Time.get_ticks_msec())
	configuration = _configuration()
	for encounter in $Encounters.get_children(): encounter.arm()
	return true
func _on_finish(body: Node3D) -> void:
	if body == $GymPlayer and is_running():
		finish_run("complete" if empty_route or metrics.cleared_count() == $Encounters.get_child_count() else "bypassed")
func _on_death() -> void:
	if is_running(): finish_run("death")
func _on_health_changed(value: float) -> void:
	if is_running(): metrics.incoming_damage += maxf(0.0, previous_health - value)
	previous_health = value
func _on_shot(_hit: bool) -> void:
	if is_running(): metrics.shots += 1
func _on_encounter_started(encounter: Node) -> void:
	if is_running():
		metrics.mark(encounter.encounter_id, "started")
		_record_event(encounter, "started")
func _record_event(encounter: Node, event: String) -> void:
	if is_running(): encounter_events.append({"id": encounter.encounter_id, "event": event, "time": metrics.elapsed})
func _on_vent_burst(encounter: Node) -> void:
	_record_event(encounter, "vent_burst")
func _on_enemy_spawned(encounter: Node) -> void:
	if is_running():
		metrics.mark(encounter.encounter_id, "first_spawn")
		_record_event(encounter, "enemy_spawned")
func _on_enemy_damaged(encounter: Node) -> void:
	if is_running(): metrics.mark(encounter.encounter_id, "first_damage")
func _on_encounter_cleared(encounter: Node) -> void:
	if is_running():
		metrics.mark(encounter.encounter_id, "cleared")
		_record_event(encounter, "cleared")
func _physics_process(delta: float) -> void:
	if is_running():
		metrics.tick(delta, $GymPlayer.global_position - previous_position, $GymPlayer.movement_mode())
		previous_position = $GymPlayer.global_position
	_update_hud()
func _clear_projectiles() -> void:
	get_tree().call_group("combat_projectiles", "despawn")
func finish_run(outcome: String) -> void:
	if not is_running(): return
	$RunChart.send_event("finish")
	for encounter in $Encounters.get_children(): encounter.cancel()
	_clear_projectiles()
	last_result = metrics.snapshot()
	last_result["outcome"] = outcome
	last_result["mode"] = "empty" if empty_route else "combat"
	last_result["run_id"] = run_id
	last_result["configuration"] = configuration
	last_result["events"] = encounter_events.duplicate(true)
	result_text = "%s / %.2f s / %.1f m\nActive %.2f s / Quiet %.2f s\nCleared %d/%d / Shots %d / Damage %d" % [outcome.to_upper(), metrics.elapsed, metrics.distance, metrics.active_seconds, metrics.quiet_seconds, metrics.cleared_count(), 0 if empty_route else $Encounters.get_child_count(), metrics.shots, roundi(metrics.incoming_damage)]
	if not empty_route:
		for entry in metrics.encounters.values():
			var split: String = "not triggered" if entry.started < 0.0 else ("unresolved" if entry.cleared < 0.0 else "%.2f s" % (entry.cleared - entry.started))
			result_text += "\n%s: %s" % [entry.label, split]
	if storage_enabled: _save_result()
	_update_hud()
func _configuration() -> Dictionary:
	var layout: Array = []
	for encounter in $Encounters.get_children():
		var spawns: Array = []
		for marker in encounter.get_node("Spawns").get_children(): spawns.append(str(marker.global_transform))
		var scenes: Array = []
		for scene in encounter.enemy_scenes: scenes.append(scene.resource_path)
		layout.append({"id": encounter.encounter_id, "scenes": scenes, "spawns": spawns, "trigger": str(encounter.get_node("Trigger").global_transform), "cue": encounter.cue_seconds, "interval": encounter.spawn_interval, "introduction": encounter.introduction, "preplaced": encounter.preplaced_count, "burst_delay": encounter.burst_delay_seconds, "spawn_separation": encounter.minimum_spawn_distance, "trigger_size": str(encounter.get_node("Trigger/Shape").shape.size), "vent": str(encounter.get_node("Vent").global_transform)})
	return {"version": ProjectSettings.get_setting("application/config/version"), "route_revision": route_revision,
		"map_sha256": FileAccess.get_sha256("res://maps/route_01.map"), "layout": layout, "scene_sha256": FileAccess.get_sha256("res://encounters/route_trial.tscn"),
		"encounter_script_sha256": FileAccess.get_sha256("res://encounters/encounter.gd"),
		"bug_script_sha256": FileAccess.get_sha256("res://combat/gym_bug.gd"), "spitter_script_sha256": FileAccess.get_sha256("res://combat/gym_spitter.gd"),
		"bug_scene_sha256": FileAccess.get_sha256("res://combat/gym_bug.tscn"), "small_bug_scene_sha256": FileAccess.get_sha256("res://combat/gym_small_bug.tscn"), "spitter_scene_sha256": FileAccess.get_sha256("res://combat/gym_spitter.tscn"),
		"walk": $GymPlayer.walk_speed, "sprint": $GymPlayer.sprint_speed, "crouch": $GymPlayer.crouch_speed,
		"damage": $GymPlayer.pistol.damage, "shots_per_second": $GymPlayer.pistol.shots_per_second,
		"reload": $GymPlayer.pistol.reload_seconds, "magazine": $GymPlayer.pistol.magazine_capacity,
		"ads_move": $GymPlayer.pistol.ads_move_multiplier}
func _append_csv(path: String, header: Array, row: Array) -> bool:
	var exists := FileAccess.file_exists(path)
	var file := FileAccess.open(path, FileAccess.READ_WRITE if exists else FileAccess.WRITE)
	if file == null: return false
	file.seek_end()
	if not exists: file.store_csv_line(PackedStringArray(header))
	var values := PackedStringArray()
	for value in row: values.append(str(value))
	file.store_csv_line(values)
	file.flush()
	return file.get_error() == OK
func _save_result() -> void:
	if FileAccess.file_exists(results_directory) or DirAccess.make_dir_recursive_absolute(results_directory) != OK:
		export_status = "RESULT SAVE FAILED / folder unavailable"
		return
	var config_json := JSON.stringify(configuration)
	var common: Array = [run_id, last_result.mode, last_result.outcome]
	var ok := _append_csv(results_directory.path_join("runs.csv"), ["run_id","mode","outcome","elapsed_s","active_s","quiet_s","moving_s","distance_m","shots","damage","cleared","movement_modes_json","quiet_intervals_json","configuration_json"], common + [metrics.elapsed,metrics.active_seconds,metrics.quiet_seconds,metrics.moving_seconds,metrics.distance,metrics.shots,metrics.incoming_damage,metrics.cleared_count(),JSON.stringify(metrics.modes),JSON.stringify(metrics.quiet_intervals),config_json])
	if not empty_route:
		for id in metrics.encounters:
			var e: Dictionary = metrics.encounters[id]
			var duration: float = e.cleared - e.started if e.cleared >= 0.0 else -1.0
			ok = _append_csv(results_directory.path_join("encounters.csv"), ["run_id","mode","outcome","encounter_id","label","count","alert_s","first_spawn_s","first_damage_s","clear_s","duration_s"], common + [id,e.label,e.count,e.started,e.first_spawn,e.first_damage,e.cleared,duration]) and ok
	for event in encounter_events:
		ok = _append_csv(results_directory.path_join("encounter_events.csv"), ["run_id","mode","outcome","encounter_id","event","time_s"], common + [event.id,event.event,event.time]) and ok
	export_status = "Saved / " + results_directory if ok else "RESULT SAVE FAILED / check file access"
func _update_hud() -> void:
	if not is_node_ready(): return
	var mode: String = "EMPTY ROUTE" if empty_route else "COMBAT ROUTE"
	var text: String = "%s / F4 switch + reset\n" % mode
	if state() == "Finished":
		text += result_text + "\n" + export_status + "\nBackspace / repeat"
	elif is_running():
		text += "%.2f s / %.1f m\nActive %.1f s / Quiet %.1f s\nCleared %d/%d" % [metrics.elapsed,metrics.distance,metrics.active_seconds,metrics.quiet_seconds,metrics.cleared_count(),0 if empty_route else $Encounters.get_child_count()]
		for entry in metrics.encounters.values():
			if entry.started >= 0.0:
				text += "\n%s / %.2f s%s" % [entry.label, (entry.cleared if entry.cleared >= 0.0 else metrics.elapsed) - entry.started, " clear" if entry.cleared >= 0.0 else " live"]
		for encounter in $Encounters.get_children():
			if encounter.spawn_blocked: text += "\nVENT WAITING / clear its opening"
	else:
		text += "Cross START to begin\n114 m route / follow turquoise marks\nWalk 5 m/s / Sprint 8 m/s"
	$HUD/Timing.text = text
func _exit_tree() -> void:
	# Scene changes preserve an explicit aborted result instead of silently losing an attempt.
	if is_running() and storage_enabled:
		last_result = metrics.snapshot()
		last_result["outcome"] = "aborted_scene_exit"
		last_result["mode"] = "empty" if empty_route else "combat"
		_save_result()
