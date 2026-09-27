extends Node3D
## A hinged catwalk section (rb_drawbridge). It stands up at 90° against the wall at its hinge until its event lowers
## it, and you watch it swing down flat onto the catwalk's line. The StateChart owns Raised, Lowering and Lowered (a
## reset from anywhere goes back to Raised). Origin: the middle of the hinge line at deck height, on the wall's face;
## "extends" points from the hinge to the free end.
const Parts := preload("res://interaction/kit_parts.gd")
const Progression := preload("res://interaction/progression.gd")

@export var func_godot_properties: Dictionary = {}
@export var lower_time := 2.2
@onready var chart: StateChart = $StateChart

var kit_id := "DRAWBRIDGE"
var event := "drawbridge"
var length := 4.75
var width := 1.5
var thickness := 0.25
var angle := PI / 2.0
var _t := 0.0
var _pivot: Node3D
var _rest: Basis
var _progression: Node


func _enter_tree() -> void:
	if not Engine.is_editor_hint() and not EngineDebugger.is_active():
		$StateChart.track_in_editor = false


func _ready() -> void:
	add_to_group("progression_kit")
	var p := func_godot_properties
	kit_id = str(p.get("id", kit_id))
	event = str(p.get("event", event))
	length = float(p.get("length", length))
	width = float(p.get("width", width))
	thickness = float(p.get("thickness", thickness))
	var e := Parts.plan_dir(str(p.get("extends", "-1 0")), Vector3.LEFT)
	_rest = Basis(e, Vector3.UP, e.cross(Vector3.UP))
	_build(str(p.get("look", "steel")))
	_apply()
	_connect_progression.call_deferred()


func _connect_progression() -> void:
	_progression = Progression.of(self)
	if _progression != null:
		_progression.fired.connect(func(ev: String):
			if ev == event:
				chart.send_event("lower"))
		_progression.reset_all.connect(func(): chart.send_event("reset"))


func _build(look: String) -> void:
	_pivot = Node3D.new()
	_pivot.name = "Pivot"
	add_child(_pivot)
	var deck := AnimatableBody3D.new()
	deck.name = "Deck"
	deck.sync_to_physics = false
	_pivot.add_child(deck)
	Parts.box(deck, Vector3(length, thickness, width), Vector3(length / 2.0, -thickness / 2.0, 0), Parts.material(look, "grate"), true)
	var frame := Parts.material(look, "frame")
	var posts := maxi(1, int(round(length / 1.25)))
	for side in [-1.0, 1.0]:
		var z: float = side * (width / 2.0 - 0.05)
		for i in posts + 1:
			var x := 0.1 + (length - 0.2) * i / posts
			Parts.box(deck, Vector3(0.1, 1.05, 0.1), Vector3(x, 0.525, z), frame, true)
		Parts.box(deck, Vector3(length - 0.1, 0.1, 0.1), Vector3(length / 2.0, 1.05, z), frame, true)


func _apply() -> void:
	_pivot.basis = _rest * Basis(Vector3(0, 0, 1), angle)


func state_name() -> String:
	for state in $StateChart/Hinge.get_children():
		if state is StateChartState and state.active:
			return str(state.name)
	return "Starting"


func busy() -> bool:
	return state_name() == "Lowering"


func use_done() -> bool:
	return state_name() == "Lowered"


func use_point() -> Vector3:
	return global_position


func _on_lowering_physics(delta: float) -> void:
	# It falls: slow off the stop, then quicker, like a heavy section on its hinge.
	_t = minf(1.0, _t + delta / lower_time)
	angle = PI / 2.0 * (1.0 - _t * _t)
	_apply()
	if _t >= 1.0:
		chart.send_event("landed")


func _on_state_entered(label: String) -> void:
	match label:
		"Raised":
			_t = 0.0
			angle = PI / 2.0
			_apply()
		"Lowered":
			angle = 0.0
			_apply()
