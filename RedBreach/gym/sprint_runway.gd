extends Node3D
## Origin is the start plane; finish is distance metres along local -Z.

@export var player_path := NodePath("../../GymPlayer")
@export var distance: float = 20.0
@export var lane_width: float = 4.0
@export var approach_length: float = 2.0
@onready var player: CharacterBody3D = get_node(player_path)
var best_times: Dictionary = {}
var last_time: float = 0.0
var completed_runs: int = 0
var last_result: String = "Enter from the south / walk or sprint"
var running: bool = false
var _armed: bool = false
var _previous := Vector3.ZERO
var _clock: float = 0.0
var _started_at: float = 0.0
var _mode: String = "WALK"

func _ready() -> void:
	process_physics_priority = 100
	_previous = to_local(player.global_position)
	player.relocated.connect(_on_relocated)
	$HUD/Readout.hide()

func _on_relocated() -> void:
	if running:
		last_result = "RESET / enter from the south"
	running = false
	_armed = false
	_previous = to_local(player.global_position)

func _inside_width(location: Vector3) -> bool:
	return absf(location.x) <= lane_width * 0.5 - 0.3

func _physics_process(delta: float) -> void:
	var tick_start := _clock
	_clock += delta
	var location := to_local(player.global_position)
	var inside := _inside_width(location)
	var mode: String = player.movement_mode()
	var valid_posture: bool = player.is_grounded() and not player.is_crouching() and absf(location.y) < 0.1 and mode in ["WALK", "SPRINT"]
	if running:
		if not inside or not valid_posture or mode != _mode or location.z > _previous.z + 0.001:
			running = false
			_armed = false
			last_result = "CANCELLED / keep one mode and stay in lane"
		elif _previous.z > -distance and location.z <= -distance:
			var fraction := clampf((_previous.z + distance) / (_previous.z - location.z), 0.0, 1.0)
			last_time = tick_start + delta * fraction - _started_at
			completed_runs += 1
			best_times[_mode] = minf(last_time, float(best_times.get(_mode, INF)))
			last_result = "%s / %.2f s / best %.2f s" % [_mode, last_time, best_times[_mode]]
			running = false
			_armed = false
	else:
		if not inside or not valid_posture:
			_armed = false
		elif location.z > 0.1 and location.z <= approach_length:
			_armed = true
		elif _armed and _inside_width(_previous) and _previous.z >= 0.0 and location.z < 0.0:
			var fraction := clampf(_previous.z / (_previous.z - location.z), 0.0, 1.0)
			_started_at = tick_start + delta * fraction
			_mode = mode
			running = true
			_armed = false
	_previous = location
	var message := "%s / %.2f s" % [_mode, _clock - _started_at] if running else last_result
	$HUD/Readout.visible = absf(location.x) < lane_width * 0.5 + 0.8 and location.z <= approach_length + 1.0 and location.z >= -distance - 2.5
	$HUD/Readout.text = "20 m RUN / %s\n%s\nWalk and sprint have separate best times" % ["TIMING" if running else "READY", message]
	$Board.text = message + "\nWALK / SPRINT"
