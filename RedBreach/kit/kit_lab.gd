extends Node3D
## Kit lab K-01 controls.
##   P  presentation off / subtle (the settled standard)
##   B  release a melee bug ahead of you;  N  release a spitter
##      (a technical check of bugs in angled spaces, not fight design)

@export var env_levels: Array[Environment] = []
@export var presentation: int = 1

var _bugs: Array[Node] = []
var _label: Label

func _ready() -> void:
	var layer := CanvasLayer.new()
	layer.name = "CanvasLayer"
	layer.layer = 10
	_label = Label.new()
	_label.name = "Label"
	_label.position = Vector2(16, 12)
	_label.add_theme_font_size_override("font_size", 18)
	_label.add_theme_color_override("font_outline_color", Color.BLACK)
	_label.add_theme_constant_override("outline_size", 6)
	layer.add_child(_label)
	add_child(layer)
	apply()

func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.physical_keycode:
		KEY_P:
			presentation = (presentation + 1) % env_levels.size()
			apply()
		KEY_B: release("res://combat/gym_bug.tscn")
		KEY_N: release("res://combat/gym_spitter.tscn")

func release(path: String) -> void:
	var player: CharacterBody3D = $GymPlayer
	for bug in _bugs:
		if is_instance_valid(bug):
			bug.queue_free()
	_bugs.clear()
	var ahead := player.global_position - player.global_basis.z * 9.0
	var map_rid := get_world_3d().navigation_map
	var at := NavigationServer3D.map_get_closest_point(map_rid, ahead)
	var bug: Node3D = load(path).instantiate()
	add_child(bug)
	bug.global_position = at + Vector3.UP * 0.1
	_bugs.append(bug)
	if bug.has_method("activate"):
		bug.call_deferred("activate", player)

func apply() -> void:
	$Environment.environment = env_levels[presentation]
	_label.text = "KIT LAB K-01 | presentation: %s   [P present  B bug  N spitter]" % ["off", "subtle"][presentation]
