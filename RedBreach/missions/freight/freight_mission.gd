extends Node3D
@export var storage_enabled: bool = true
@export var results_directory: String = "user://freight_walkthroughs"
var records_card := false
var freight_card := false
var power_restored := false
var secret_collected := false
var selected_code := ""
var elapsed := 0.0
var distance := 0.0
var previous_position := Vector3.ZERO
var visited: Dictionary = {}
var event_log: Array[Dictionary] = []
var message_seconds := 0.0
var title_seconds := 0.0
var arrival_seconds := 0.0
var current_room := "Arrival airlock"
var last_result: Dictionary = {}
var save_status := ""
var run_serial: int = 0
var _circuit_waiting_close := false
var layout: Dictionary = {}
@onready var player = $GymPlayer
func _enter_tree() -> void:
	add_to_group("freight_mission")
	add_to_group("combat_gym")
	if not EngineDebugger.is_active():
		$RunChart.track_in_editor = false
		$CircuitChart.track_in_editor = false
func _ready() -> void:
	layout = JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json"))
	player.camera.far = 500.0
	previous_position = player.global_position
	reset_encounter.call_deferred()
func run_state() -> String:
	for state in $RunChart/Run.get_children():
		if state is StateChartState and state.active: return str(state.name)
	return "Arrival"
func notice(text: String) -> void:
	$HUD/Notice.text = text
	message_seconds = 3.0
func record(event: String) -> void:
	event_log.append({"event":event,"seconds":snappedf(elapsed,0.01)})
func reset_encounter() -> void:
	if run_state() == "Running" and elapsed > 0.0: save_run("reset")
	run_serial += 1
	records_card = false
	freight_card = false
	power_restored = false
	secret_collected = false
	elapsed = 0.0
	distance = 0.0
	visited.clear()
	event_log.clear()
	last_result.clear()
	save_status = ""
	arrival_seconds = 0.0
	title_seconds = 0.0
	message_seconds = 0.0
	previous_position = player.global_position
	for gate in $Gates.get_children(): gate.reset_gate()
	$RegistrationF02/StaffDoor.reset_door()
	$RunChart.send_event("reset")
	$CircuitChart.send_event("off")
	set_circuit("")
	refresh_items()
func set_circuit(code: String) -> void:
	selected_code = code
	if not is_node_ready(): return
	$Gates/BcD.set_circuit_open(code == "BcD")
	_circuit_waiting_close = code != "BcD"
	$Ladder/Visual.visible = code == "BcD"
	$Cache/Cover.position.y = 2.1 if code == "Tr1" else 0.8
	$Cache/Cover/CollisionShape3D.set_deferred("disabled", code == "Tr1")
	for button in $Selector.get_children():
		var lamp: MeshInstance3D = button.get_node("Lamp")
		lamp.visible = button.action == code
	refresh_items()
func _on_circuit_entered(code: String) -> void:
	set_circuit(code)
func use_prompt(action: String) -> String:
	match action:
		"records": return "Records card collected" if records_card else "E  Take Records card"
		"freight": return "Freight clearance collected" if freight_card else "E  Take freight-lift card"
		"power": return "Auxiliary feed online" if power_restored else "E  Restore freight power"
		"GMa", "BcD", "Tr1": return action + (" / selected" if selected_code == action else " / E select")
		"secret": return "Cache empty" if secret_collected else ("E  Take health" if selected_code == "Tr1" else "Tr1 / sealed")
		"ladder_low", "ladder_high": return "E  Climb ladder" if selected_code == "BcD" else "BcD / ladder retracted"
		"depart":
			if run_state() == "Complete": return "Walkthrough complete / Backspace repeat"
			return "E  Depart" if freight_card and power_restored else "Freight clearance + auxiliary power required"
	return ""
func use_action(action: String) -> bool:
	match action:
		"records":
			if records_card: return false
			records_card = true
			notice("Records access acquired")
		"freight":
			if freight_card: return false
			freight_card = true
			notice("Freight clearance acquired")
		"power":
			if power_restored: return false
			power_restored = true
			notice("Freight auxiliary power restored")
		"GMa", "BcD", "Tr1":
			if selected_code == action: return false
			$CircuitChart.send_event(action)
			if action == "GMa":
				$Selector/GMa/Sparks.restart()
				$Selector/GMa/Sparks.emitting = true
		"secret":
			if selected_code != "Tr1" or secret_collected: return false
			if not player.get_node("Health").heal(25.0):
				notice("Health full")
				return false
			secret_collected = true
		"ladder_low", "ladder_high":
			if selected_code != "BcD": return false
			var path: Array[Vector3] = []
			if action == "ladder_low": path = [Vector3(-41.6,2.05,-198),Vector3(-41.6,6.05,-198),Vector3(-35,6.05,-198)]
			else: path = [Vector3(-40,6.05,-198),Vector3(-41.6,6.05,-198),Vector3(-41.6,2.05,-198),Vector3(-43,2.05,-198)]
			return player.begin_climb(path)
		"depart":
			if not freight_card or not power_restored or run_state() != "Running": return false
			$RunChart.send_event("finish")
			$Gates/Lift.set_circuit_open(false)
			record("depart")
			save_run("complete")
			notice("Traversal complete")
			return true
		_:
			return false
	record(action)
	refresh_items()
	return true
func refresh_items() -> void:
	if not is_node_ready(): return
	for data in [["Objectives/Records",records_card],["Objectives/Freight",freight_card],["Cache/Health",secret_collected or selected_code != "Tr1"]]:
		var item: StaticBody3D = get_node(data[0])
		item.visible = not data[1]
		item.set_deferred("collision_layer",0 if data[1] else 1)
func gate_prompt(gate: Node3D) -> String:
	if gate.latched: return "Passage released"
	match gate.gate_id:
		"D1": return "Sealed / use the service passage"
		"D2": return "E  Unlock Records access" if records_card else "Records card required"
		"D4", "S1", "S2": return "E  Release passage" if gate.to_local(player.global_position).z < 0.0 else "Release from the other side"
		"BcD": return "BcD / circuit controlled"
		"Arrival": return "Airlock cycling..."
		"Lift": return "E  Open freight lift" if freight_card and power_restored else "Freight clearance + auxiliary power required"
	return ""
func use_gate(gate: Node3D) -> bool:
	if gate.latched: return false
	var allowed: bool = (gate.gate_id == "D2" and records_card) or (gate.gate_id == "Lift" and freight_card and power_restored)
	if gate.gate_id in ["D4","S1","S2"]: allowed = gate.to_local(player.global_position).z < 0.0
	if not allowed:
		notice(gate_prompt(gate))
		return false
	gate.release()
	record("released_"+gate.gate_id)
	return true
func _physics_process(delta: float) -> void:
	if run_state() == "Arrival":
		arrival_seconds += delta
		if arrival_seconds > 0.75:
			$Gates/Arrival.release()
			$RunChart.send_event("ready")
	if run_state() == "Ready" and player.position.z < 62.5:
		$RunChart.send_event("start")
		title_seconds = 3.5
		previous_position = player.global_position
		record("arrival")
	if run_state() == "Running":
		elapsed += delta
		distance += player.global_position.distance_to(previous_position)
	previous_position = player.global_position
	if _circuit_waiting_close and $Gates/BcD.state_name() == "Open":
		$Gates/BcD.set_circuit_open(false)
		_circuit_waiting_close = false
	if run_state() == "Complete" and $Gates/Lift.state_name() == "Open":
		$Gates/Lift.set_circuit_open(false)
	update_location()
	update_hud(delta)
func update_location() -> void:
	var xz := Vector2(player.position.x+190,player.position.z+260)
	for id in layout.get("rooms",{}):
		var room: Array = layout.rooms[id]
		if absf(xz.x-float(room[0]))<=float(room[2])*0.5 and absf(xz.y-float(room[1]))<=float(room[3])*0.5:
			current_room = str(id)+" / "+str(room[4]).replace("|"," ")
			if run_state() == "Running" and not visited.has(id):
				visited[id] = snappedf(elapsed,0.01)
				record("entered_"+str(id))
			return
	current_room = "Service passage"
func update_hud(delta: float) -> void:
	message_seconds = maxf(0,message_seconds-delta)
	title_seconds = maxf(0,title_seconds-delta)
	$HUD/Notice.visible = message_seconds > 0
	$HUD/ArrivalTitle.modulate.a = clampf(title_seconds/2.0,0,1)
	var state_label: String = "COMPLETE" if run_state() == "Complete" else "EMPTY WALKTHROUGH"
	$HUD/Progress.text = "%s / %.1f s / %.0f m\n%s / Height %+.1f m\nRecords %s   Freight %s   Power %s" % [state_label,elapsed,distance,current_room,player.position.y,"YES" if records_card else "--","YES" if freight_card else "--","ON" if power_restored else "--"]
	if run_state() == "Complete": $HUD/Progress.text += "\n"+save_status+"\nBackspace / repeat"
func save_run(outcome: String) -> void:
	last_result = {"outcome":outcome,"revision":str(layout.get("revision","unknown")),"version":ProjectSettings.get_setting("application/config/version"),"elapsed_s":elapsed,"distance_m":distance,"visited":visited.duplicate(),"events":event_log.duplicate(true),"records":records_card,"freight":freight_card,"power":power_restored,"selector":selected_code,"map_sha256":FileAccess.get_sha256("res://maps/freight_01.map")}
	if not storage_enabled:
		save_status = "QA / storage disabled"
		return
	if DirAccess.make_dir_recursive_absolute(results_directory) != OK:
		save_status = "Result save failed / folder unavailable"
		return
	var filename := Time.get_datetime_string_from_system().replace(":","-")+"_"+str(Time.get_ticks_msec())+"_"+str(run_serial)+".json"
	var file := FileAccess.open(results_directory.path_join(filename),FileAccess.WRITE)
	if file == null:
		save_status = "Result save failed / file unavailable"
		return
	file.store_string(JSON.stringify(last_result,"\t"))
	file.flush()
	save_status = "Saved / "+results_directory if file.get_error() == OK else "Result save failed"
func _exit_tree() -> void:
	if is_node_ready() and run_state() == "Running" and storage_enabled: save_run("scene_exit")
