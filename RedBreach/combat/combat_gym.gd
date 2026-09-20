extends Node3D
var attempts: int = 0
var elapsed: float = 0.0
var active_enemy: CharacterBody3D
var active_enemy_name: String = "BUG"

func _enter_tree() -> void:
	if not EngineDebugger.is_active():
		$EncounterChart.track_in_editor = false

func _ready() -> void:
	add_to_group("combat_gym")
	$Bug.died.connect(_on_bug_died)
	$Spitter.died.connect(_on_bug_died)
	active_enemy = $Bug
	_set_enemy_enabled($Spitter, false)
	$GymPlayer/Health.died.connect(_on_player_died)
	update_readout()

func state() -> String:
	for node in $EncounterChart/Encounter.get_children():
		if node.get("active") == true:
			return node.name
	return ""

func start_encounter(enemy_kind: int = 0) -> bool:
	if state() != "Ready" or not $GymPlayer.is_alive():
		return false
	var point: Vector3 = $GymPlayer.global_position
	# Entire capsule must be inside; never close a gate on the player.
	if point.z > -1.0 or point.z < -19.0 or point.x < 11.0 or point.x > 29.0:
		return false
	active_enemy = $Spitter if enemy_kind == 1 else $Bug
	active_enemy_name = "SPITTER" if enemy_kind == 1 else "BUG"
	_set_enemy_enabled($Bug, enemy_kind != 1)
	_set_enemy_enabled($Spitter, enemy_kind == 1)
	if not active_enemy.activate($GymPlayer):
		return false
	$EncounterChart.send_event("start")
	set_gate(true)
	attempts += 1
	elapsed = 0.0
	update_readout()
	return true

func _set_enemy_enabled(enemy: CharacterBody3D, enabled: bool) -> void:
	enemy.visible = enabled
	enemy.process_mode = Node.PROCESS_MODE_INHERIT if enabled else Node.PROCESS_MODE_DISABLED
	enemy.collision_layer = 1 if enabled else 0
	enemy.get_node("CollisionShape3D").set_deferred("disabled", not enabled)
	for hit_area in enemy.find_children("*", "Area3D", true, false):
		hit_area.collision_layer = 2 if enabled else 0

func _clear_projectiles() -> void:
	get_tree().call_group("combat_projectiles", "despawn")

func set_gate(closed: bool) -> void:
	$Gate/Mesh.visible = closed
	$Gate/CollisionShape3D.set_deferred("disabled", not closed)

func _on_bug_died() -> void:
	_clear_projectiles()
	if state() == "Fighting":
		$EncounterChart.send_event("clear")
		set_gate(false)
		update_readout()

func _on_player_died() -> void:
	_clear_projectiles()
	if state() == "Fighting":
		$EncounterChart.send_event("fail")
		set_gate(false)
		update_readout()

func reset_encounter() -> void:
	$EncounterChart.send_event("reset")
	$Bug.reset_bug()
	$Spitter.reset_bug()
	_set_enemy_enabled($Bug, true)
	_set_enemy_enabled($Spitter, false)
	active_enemy = $Bug
	active_enemy_name = "BUG"
	_clear_projectiles()
	$Effects.clear_effects()
	get_tree().call_group("combat_pickups", "reset_pickup")
	set_gate(false)
	elapsed = 0.0
	update_readout()

func _process(delta: float) -> void:
	if state() == "Fighting":
		elapsed += delta
	update_readout()

func update_readout() -> void:
	match state():
		"Fighting": $HUD/Encounter.text = "%s LIVE  /  %.1f s" % [active_enemy_name, elapsed]
		"Cleared": $HUD/Encounter.text = "%s DOWN  /  %.1f s\nBackspace / fresh attempt" % [active_enemy_name, elapsed]
		"Failed": $HUD/Encounter.text = "CONTAINMENT FAILED"
		_: $HUD/Encounter.text = "RANGE LEFT  /  BUG ARENA RIGHT"
