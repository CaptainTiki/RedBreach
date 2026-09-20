extends Node3D
var attempts: int = 0
var elapsed: float = 0.0

func _enter_tree() -> void:
	if not EngineDebugger.is_active():
		$EncounterChart.track_in_editor = false

func _ready() -> void:
	add_to_group("combat_gym")
	$Bug.died.connect(_on_bug_died)
	$GymPlayer/Health.died.connect(_on_player_died)
	update_readout()

func state() -> String:
	for node in $EncounterChart/Encounter.get_children():
		if node.get("active") == true:
			return node.name
	return ""

func start_encounter() -> bool:
	if state() != "Ready" or not $GymPlayer.is_alive():
		return false
	var point: Vector3 = $GymPlayer.global_position
	# Entire capsule must be inside; never close a gate on the player.
	if point.z > -1.0 or point.z < -19.0 or point.x < 11.0 or point.x > 29.0:
		return false
	if not $Bug.activate($GymPlayer):
		return false
	$EncounterChart.send_event("start")
	set_gate(true)
	attempts += 1
	elapsed = 0.0
	update_readout()
	return true

func set_gate(closed: bool) -> void:
	$Gate/Mesh.visible = closed
	$Gate/CollisionShape3D.set_deferred("disabled", not closed)

func _on_bug_died() -> void:
	if state() == "Fighting":
		$EncounterChart.send_event("clear")
		set_gate(false)
		update_readout()

func _on_player_died() -> void:
	if state() == "Fighting":
		$EncounterChart.send_event("fail")
		set_gate(false)
		update_readout()

func reset_encounter() -> void:
	$EncounterChart.send_event("reset")
	$Bug.reset_bug()
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
		"Fighting": $HUD/Encounter.text = "CONTAINMENT LIVE  /  %.1f s" % elapsed
		"Cleared": $HUD/Encounter.text = "BUG DOWN  /  %.1f s\nBackspace / fresh attempt" % elapsed
		"Failed": $HUD/Encounter.text = "CONTAINMENT FAILED"
		_: $HUD/Encounter.text = "RANGE LEFT  /  BUG ARENA RIGHT"
