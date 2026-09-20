extends Node3D
## The StateChart owns behavior; these callbacks drive the physical leaves and feedback.

@export_range(0.2, 3.0) var travel_time: float = 0.8
@export var leaf_travel: float = 1.05
@export_flags_3d_physics var blocker_mask: int = 1
@onready var chart: StateChart = $StateChart
@onready var left_leaf: AnimatableBody3D = $LeftLeaf
@onready var right_leaf: AnimatableBody3D = $RightLeaf
@onready var clearance: CollisionShape3D = $Clearance/CollisionShape3D
var open_amount: float = 0.0
var _indicator_material: StandardMaterial3D

func _enter_tree() -> void:
	# The addon expects a connected editor debugger when tracking is enabled.
	# Keep tracking for F5/editor runs, while standalone runs and QA stay quiet.
	if not Engine.is_editor_hint() and not EngineDebugger.is_active():
		$StateChart.track_in_editor = false
func _ready() -> void:
	_indicator_material = StandardMaterial3D.new()
	_indicator_material.emission_enabled = true
	_indicator_material.emission_energy_multiplier = 1.2
	for lamp in [$IndicatorFront, $IndicatorBack, $SwitchFront/Lamp, $SwitchBack/Lamp]:
		lamp.material_override = _indicator_material
	_update_leaves()

func state_name() -> String:
	for state in $StateChart/Movement.get_children():
		if state is StateChartState and state.active:
			return str(state.name)
	return "Starting"

func interaction_prompt() -> String:
	match state_name():
		"Closed": return "E  Open door"
		"Open": return "E  Close door"
		"Closing": return "E  Reopen door"
		"Opening": return "Opening..."
		"Blocked": return "Blocked - clear the doorway"
	return "Starting..."

func request_toggle() -> bool:
	match state_name():
		"Closed", "Closing": chart.send_event("open_requested")
		"Open": chart.send_event("obstructed" if is_doorway_blocked() else "close_requested")
		_: return false
	return true

func is_doorway_blocked() -> bool:
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = clearance.shape
	query.transform = clearance.global_transform
	query.collision_mask = blocker_mask
	query.exclude = [left_leaf.get_rid(), right_leaf.get_rid()]
	for hit in get_world_3d().direct_space_state.intersect_shape(query, 32):
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:
			return true
	return false

func _update_leaves() -> void:
	left_leaf.position.x = -0.5 - open_amount * leaf_travel
	right_leaf.position.x = 0.5 + open_amount * leaf_travel

func _move_towards(target: float, delta: float) -> void:
	open_amount = move_toward(open_amount, target, delta / maxf(travel_time, 0.01))
	_update_leaves()

func _on_opening_physics(delta: float) -> void:
	_move_towards(1.0, delta)
	if open_amount >= 1.0:
		chart.send_event("fully_open")

func _on_closing_physics(delta: float) -> void:
	if is_doorway_blocked():
		chart.send_event("obstructed")
		return
	_move_towards(0.0, delta)
	if open_amount <= 0.0:
		chart.send_event("fully_closed")

func _on_blocked_physics(delta: float) -> void:
	_move_towards(1.0, delta)
	if open_amount >= 1.0 and not is_doorway_blocked():
		chart.send_event("clear")

func _on_state_entered(label: String) -> void:
	var color := Color(1.0, 0.55, 0.12)
	match label:
		"Open": color = Color(0.15, 0.95, 0.65)
		"Opening", "Closing": color = Color(1.0, 0.85, 0.2)
		"Blocked": color = Color(1.0, 0.15, 0.08)
	_indicator_material.albedo_color = color
	_indicator_material.emission = color
	var message := label.to_upper()
	if label == "Blocked":
		message = "BLOCKED / CLEAR DOORWAY"
	$StatusFront.text = message
	$StatusBack.text = message
