extends SceneTree
class TrialStub extends Node3D:
	var running := true
	func is_running() -> bool: return running
var checks := 0
var failures: Array[String] = []
var arena: Node3D
var player: CharacterBody3D
var encounter: Node3D
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ", label)
	if not ok: failures.append(label)
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func place(point: Vector3) -> void:
	player.relocate(Transform3D(Basis.IDENTITY, point))
	await ticks(3)
func run() -> void:
	check(load("res://encounters/route_trial.gd") != null, "Route controller compiles")
	var metrics = load("res://encounters/route_metrics.gd").new()
	metrics.register("a","A",2)
	metrics.register("b","B",1)
	metrics.tick(1.0,Vector3(5,0,0),"WALK")
	metrics.mark("a","started")
	metrics.tick(2.0,Vector3(16,0,0),"SPRINT")
	metrics.mark("b","started")
	metrics.tick(1.0,Vector3.ZERO,"ADS")
	metrics.mark("a","cleared")
	metrics.tick(2.0,Vector3.ZERO,"WALK")
	metrics.mark("b","cleared")
	metrics.tick(1.0,Vector3(5,0,0),"WALK")
	check(is_equal_approx(metrics.elapsed,7.0) and is_equal_approx(metrics.active_seconds,5.0), "Overlapping fights count once in total active time")
	check(is_equal_approx(metrics.quiet_seconds,2.0) and is_equal_approx(metrics.active_seconds + metrics.quiet_seconds,metrics.elapsed), "Quiet and active intervals partition total time")
	check(is_equal_approx(metrics.distance,26.0) and is_equal_approx(metrics.moving_seconds,4.0), "Actual horizontal distance and moving time exclude stationary pauses")
	check(metrics.quiet_intervals.size() == 2 and metrics.quiet_intervals[0].end == 1.0 and metrics.quiet_intervals[1].start == 6.0, "Individual quiet gaps are retained for pacing comparison")
	check(metrics.cleared_count() == 2 and metrics.modes.ADS == 1.0, "Encounter clears and movement modes remain separate")
	metrics.mark("a","started")
	check(metrics.encounters.a.started == 1.0, "Repeated events cannot overwrite first timestamps")
	arena = load("res://combat/combat_gym.tscn").instantiate()
	root.add_child(arena)
	player = arena.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	arena._set_enemy_enabled(arena.get_node("Bug"),false)
	arena._set_enemy_enabled(arena.get_node("Spitter"),false)
	var controller := TrialStub.new()
	arena.add_child(controller)
	encounter = load("res://encounters/encounter.tscn").instantiate()
	encounter.introduction = 1
	encounter.enemy_scenes.assign([load("res://combat/gym_bug.tscn"),load("res://combat/gym_bug.tscn")])
	controller.add_child(encounter)
	encounter.get_node("Vent").audio_enabled = false
	encounter.get_node("Vent").position = Vector3(29,1,-10)
	encounter.get_node("Trigger").position = Vector3(24,0,-4)
	for point in [Vector3(25,0.05,-10),Vector3(25,0.05,-14)]:
		var marker := Marker3D.new()
		marker.position = point
		encounter.get_node("Spawns").add_child(marker)
	await ticks(15)
	encounter.prepare(player,true,controller)
	await ticks(2)
	check(encounter.state() == "Armed" and encounter.enemies.is_empty(), "Vent is armed without enemies before its trigger")
	controller.running = false
	check(not encounter.begin(), "Encounter refuses to start outside a timed run")
	controller.running = true
	await place(Vector3(24,0.05,-4))
	check(encounter.state() == "Introducing" and encounter.get_node("Vent").burst_count == 1, "Player entering real trigger bursts vent once")
	check(not encounter.begin(), "Re-entry cannot duplicate the introduction")
	await ticks(9)
	check(encounter.enemies.is_empty(), "Enemies wait for the grate cue")
	await ticks(18)
	check(encounter.enemies.size() >= 1 and encounter.get_node("Vent/Grate").position.z > 1.0, "Grate visibly leaves the opening before first emergence")
	if not encounter.enemies.is_empty():
		encounter.enemies[0].register_hit(1000)
	check(encounter.state() == "Fighting", "Killing first spawn cannot clear the pending second enemy")
	await ticks(20)
	check(encounter.enemies.size() == 2, "Second bug emerges after its stagger")
	if encounter.enemies.size() == 2: encounter.enemies[1].register_hit(1000)
	await ticks(2)
	check(encounter.state() == "Cleared", "Only all spawned enemies dead clears encounter")
	encounter.prepare(player,true,controller)
	await place(Vector3(25,0.05,-10))
	check(encounter.get_node("Vent").burst_count == 0 and encounter.get_node("Vent/Grate").position == Vector3.ZERO, "Reset restores grate and trigger")
	encounter.begin()
	await ticks(30)
	check(encounter.spawn_blocked and encounter.enemies.is_empty(), "Occupied spawn retries instead of placing a bug inside the player")
	await place(Vector3(27,0.05,-5))
	await ticks(12)
	check(encounter.enemies.size() >= 1, "Moving clear permits a pending spawn")
	encounter.prepare(player,true,controller)
	await ticks(2)
	encounter.begin()
	encounter.cancel()
	await ticks(45)
	check(encounter.enemies.is_empty() and encounter.state() == "Cancelled", "Cancellation prevents delayed enemies appearing after a run ends")
	encounter.prepare(player,false,controller)
	check(not encounter.begin() and encounter.enemies.is_empty(), "Empty route disables vent encounters")
	encounter.introduction = 0
	await place(Vector3(25,0.05,-4))
	encounter.prepare(player,true,controller)
	await ticks(3)
	check(encounter.enemies.size() == 2 and encounter.enemies[0].state() == "Dormant", "Room enemies physically exist before arming")
	encounter.arm()
	await ticks(3)
	check(encounter.state() == "Fighting" and encounter.enemies[0].state() != "Dormant" and encounter.enemies[1].state() != "Dormant", "Line of sight alerts the preplaced group")
	for enemy in encounter.enemies: enemy.register_hit(1000)
	await ticks(2)
	check(encounter.state() == "Cleared", "Preplaced group clears after both kills")
	encounter.prepare(player,true,controller)
	await ticks(3)
	encounter.arm()
	# Damage must wake an armed dormant target immediately, even before its next sensing tick.
	check(encounter.enemies[0].register_hit(25) and encounter.enemies[0].health == 125, "First shot wakes and damages a preplaced enemy instead of being swallowed")
	check(encounter.state() == "Fighting", "Shot-triggered wake starts the encounter timer")
	encounter.prepare(player,false,controller)
	await ticks(3)
	check(encounter.enemies.is_empty(), "Empty route also removes preplaced enemies")
	print("ENCOUNTER_QA: ",checks," checks; ",failures.size()," failures")
	arena.queue_free()
	await ticks(3)
	quit(0 if failures.is_empty() else 1)
