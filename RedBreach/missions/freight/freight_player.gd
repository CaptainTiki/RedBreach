extends "res://player/gym_player.gd"
var climb_points: Array[Vector3] = []
var climb_index: int = 0
@export var climb_speed: float = 2.0
func _enter_tree() -> void:
	super()
	if not EngineDebugger.is_active(): $ClimbChart.track_in_editor = false
func climbing() -> bool:
	return $ClimbChart/Movement/Climbing.active
func begin_climb(points: Array[Vector3]) -> bool:
	if climbing() or not is_alive() or not can_stand(): return false
	climb_points = points
	climb_index = 0
	velocity = Vector3.ZERO
	pistol.cancel_handling()
	_interaction_requested = false
	$PostureChart.send_event("stand_requested")
	$ClimbChart.send_event("climb")
	return true
func relocate(destination: Transform3D) -> void:
	if has_node("ClimbChart"): $ClimbChart.send_event("done")
	climb_points.clear()
	super(destination)
func _physics_process(delta: float) -> void:
	if not climbing():
		super(delta)
		return
	_previous_position = _current_position
	_previous_eye_height = _eye_height
	_previous_eye_offset = 0.0
	_eye_offset = 0.0
	_interaction_requested = false
	pistol.update_controls(false)
	if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED and not control_override: return
	if climb_index >= climb_points.size():
		$ClimbChart.send_event("done")
		reset_camera_interpolation()
		return
	var target := climb_points[climb_index]
	var motion := global_position.direction_to(target) * minf(climb_speed * delta, global_position.distance_to(target))
	var collision := move_and_collide(motion)
	_current_position = global_position
	if collision != null:
		$ClimbChart.send_event("done")
		get_tree().get_first_node_in_group("freight_mission").notice("Ladder blocked / clear the landing")
	elif global_position.distance_to(target) < 0.015:
		climb_index += 1
	status.text = "FREIGHT ACCESS / LADDER\nEsc pause   Backspace reset"
	$HUD/Interaction.text = "Climbing..."
