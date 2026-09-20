extends Node3D
## Editable station origin is the middle of the takeoff edge; jumping goes -Z.

@export var player_path := NodePath("../../../GymPlayer")
@export var lane_name: String = "J1"
@export var gap_length: float = 2.0
@export var lane_width: float = 3.0
@export var run_up: float = 8.0
@export var landing_depth: float = 7.0
@onready var player: CharacterBody3D = get_node(player_path)
var attempts: int = 0
var passes: int = 0
var recoveries: int = 0
var last_distance: float = 0.0
var last_result: String = "Space: jump / Shift: sprint"
var _active: bool = false
var _takeoff := Vector3.ZERO
var _mode: String = "WALK"

func _ready() -> void:
	process_physics_priority = 100
	player.jumped.connect(_on_jump)
	player.relocated.connect(_on_relocated)
	$HUD/Readout.hide()

func _on_relocated() -> void:
	_active = false

func _on_jump(origin: Vector3) -> void:
	var location := to_local(origin)
	if absf(location.x) <= lane_width * 0.5 and location.z >= 0.0 and location.z <= run_up and absf(location.y) < 0.1:
		_active = true
		_takeoff = location
		_mode = player.movement_mode()
		attempts += 1
		last_result = "%s jump in progress..." % _mode

func _physics_process(_delta: float) -> void:
	var location := to_local(player.global_position)
	var within_width := absf(location.x) < lane_width * 0.5
	if within_width and location.z < 0.0 and location.z > -gap_length and location.y < -0.8:
		recoveries += 1
		last_result = "MISS / returned to approach"
		player.relocate($ResetPoint.global_transform)
		location = to_local(player.global_position)
	elif _active:
		if not within_width or location.z > run_up or location.z < -gap_length - landing_depth:
			_active = false
			last_result = "OFF LANE / try again"
		elif player.is_grounded():
			_active = false
			if location.z <= -gap_length and absf(location.y) < 0.1:
				passes += 1
				last_distance = _takeoff.z - location.z
				last_result = "PASS / %s / %.2f m travel" % [_mode, last_distance]
			else:
				last_result = "SHORT / try again"
	$HUD/Readout.visible = absf(location.x) < lane_width * 0.5 + 0.4 and location.z < run_up + 3.0 and location.z > -gap_length - landing_depth - 1.0
	$HUD/Readout.text = "%s / %.1f m GAP\n%s\n8 m approach / misses reset here" % [lane_name, gap_length, last_result]
