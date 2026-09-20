extends "res://interaction/sliding_door.gd"
@export var gate_id: String = "D2"
@export var caption: String = "RECORDS ACCESS"
var latched: bool = false
func _ready() -> void:
	super()
	$TitleFront.text = caption
	$TitleBack.text = caption
func mission() -> Node:
	return get_tree().get_first_node_in_group("freight_mission")
func _update_leaves() -> void:
	left_leaf.position.x = -0.75 - open_amount * leaf_travel
	right_leaf.position.x = 0.75 + open_amount * leaf_travel
func interaction_prompt() -> String:
	var owner_mission := mission()
	if owner_mission == null: return ""
	return owner_mission.gate_prompt(self)
func request_toggle() -> bool:
	var owner_mission := mission()
	return owner_mission.use_gate(self) if owner_mission != null else false
func release() -> void:
	latched = true
	if state_name() in ["Closed", "Closing"]: chart.send_event("open_requested")
func set_circuit_open(enabled: bool) -> void:
	latched = enabled
	if enabled:
		if state_name() in ["Closed", "Closing"]: chart.send_event("open_requested")
	elif state_name() == "Open":
		chart.send_event("obstructed" if is_doorway_blocked() else "close_requested")
func reset_gate() -> void:
	latched = false
	chart.send_event("reset")
func _on_state_entered(label: String) -> void:
	if label == "Closed":
		open_amount = 0.0
		_update_leaves()
	super(label)
