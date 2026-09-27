extends StaticBody3D
## A card placed from the map (rb_pickup), lying on a small plinth: E takes it and sets its progression flag (K, M).
## Backspace puts it back. It glows in its own colour so it reads from across a room without a label.
const Parts := preload("res://interaction/kit_parts.gd")
const Progression := preload("res://interaction/progression.gd")

@export var func_godot_properties: Dictionary = {}
var kit_id := ""
var flag := ""
var notice_text := ""
var prompt := "E  Take"
var _taken := false
var _card: MeshInstance3D
var _progression: Node
var _t := 0.0


func _ready() -> void:
	add_to_group("progression_kit")
	var p := func_godot_properties
	kit_id = str(p.get("id", name))
	flag = str(p.get("flag", kit_id))
	notice_text = str(p.get("notice", ""))
	prompt = str(p.get("prompt", "E  Take"))
	var look := str(p.get("look", "steel"))
	var c := str(p.get("color", "1 0.7 0.2")).split_floats(" ")
	Parts.box(self, Vector3(0.42, 0.9, 0.42), Vector3(0, 0.45, 0), Parts.material(look, "machine_body"), true)
	Parts.box(self, Vector3(0.46, 0.04, 0.46), Vector3(0, 0.92, 0), Parts.material(look, "machine_top"))
	_card = Parts.box(self, Vector3(0.16, 0.012, 0.1), Vector3(0, 1.0, 0), Parts.glow(Color(c[0], c[1], c[2]), 2.5))
	_connect_progression.call_deferred()


func _connect_progression() -> void:
	_progression = Progression.of(self)
	if _progression != null:
		_progression.reset_all.connect(_on_reset)


func get_interaction_prompt() -> String:
	return use_prompt()


func interact() -> bool:
	return use()


func use_prompt() -> String:
	return "" if _taken else prompt


func use() -> bool:
	if _taken:
		return false
	_taken = true
	_card.visible = false
	if _progression != null:
		_progression.set_flag(flag)
	Parts.notice(self, notice_text)
	return true


func use_done() -> bool:
	return _taken


func busy() -> bool:
	return false


func use_point() -> Vector3:
	return global_position + Vector3.UP


func _process(delta: float) -> void:
	if not _taken:
		_t += delta
		_card.position.y = 1.0 + 0.03 * sin(_t * 2.0)
		_card.rotation.y = _t * 0.8


func _on_reset() -> void:
	_taken = false
	_card.visible = true
