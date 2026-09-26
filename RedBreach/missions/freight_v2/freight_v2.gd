extends Node3D
## Freight access v2, G-01 greybox: the empty walk.
## The timer starts when you first move and stops when you reach the lift, so the empty walk can be measured.
##   P  presentation off / subtle;  Backspace  back to the airlock (resets the timer)

@export var env_levels: Array[Environment] = []
@export var presentation: int = 1
## Plan point (x east, y north) of the lift gate; reaching it stops the timer.
@export var finish := Vector2(0.0, 46.0)

var _label: Label
var _notice: Label
var _notice_time := 0.0
var _started := false
var _finished := false
var _elapsed := 0.0
var _distance := 0.0
var _last := Vector3.ZERO

func _ready() -> void:
	add_to_group("freight_mission")
	add_to_group("combat_gym")
	var layer := CanvasLayer.new()
	layer.name = "CanvasLayer"
	layer.layer = 10
	_label = _make_label(Vector2(16, 12), 18)
	_notice = _make_label(Vector2(16, 44), 20)
	_label.name = "Label"
	_notice.name = "Notice"
	layer.add_child(_label)
	layer.add_child(_notice)
	add_child(layer)
	_last = $GymPlayer.global_position
	apply()

func _make_label(at: Vector2, size: int) -> Label:
	var l := Label.new()
	l.position = at
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_outline_color", Color.BLACK)
	l.add_theme_constant_override("outline_size", 6)
	return l

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_P:
		presentation = (presentation + 1) % env_levels.size()
		apply()

func _physics_process(delta: float) -> void:
	var at: Vector3 = $GymPlayer.global_position
	var step := Vector2(at.x - _last.x, at.z - _last.z).length()
	_last = at
	if not _started and step > 0.01:
		_started = true
	if _started and not _finished:
		_elapsed += delta
		if step < 3.0:
			_distance += step
		if Vector2(at.x, -at.z).distance_to(finish) < 2.5:
			_finished = true
			notice("Lift reached: %.1f s, %.0f m" % [_elapsed, _distance])
	if _notice_time > 0.0:
		_notice_time -= delta
		if _notice_time <= 0.0:
			_notice.text = ""
	_label.text = "FREIGHT V2 G-01 | %s %.1f s  %.0f m | presentation: %s   [P present  Backspace restart]" % [
		"FINISHED" if _finished else "time", _elapsed, _distance, ["off", "subtle"][presentation]]

func notice(text: String) -> void:
	print("NOTICE: ", text)
	_notice.text = text
	_notice_time = 4.0

func reset_encounter() -> void:
	_started = false
	_finished = false
	_elapsed = 0.0
	_distance = 0.0
	_last = $GymPlayer.global_position

func apply() -> void:
	$Environment.environment = env_levels[presentation]
