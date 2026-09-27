extends Node3D
## Style lab S-01 controls. Only the comparison switches live here; the
## geometry, lighting tiers and environments are authored in the scene, and
## the palette and plan tables come from style/style_lab_data.json (written by
## tools/write-style-lab-scene.py from tools/style_lab.py).
##   T  palette: the zoned mix, or the whole lab in one look (warm / steel / concrete)
##   L  lighting plan: mixed (edge+wall / floor-lit / damaged), edge+wall, floor, ceiling centre
##   P  presentation: off / subtle / strong (fog, glow, grade, SSAO)

@export var env_levels: Array[Environment] = []
@export var palette: int = 0
@export var plan: int = 0
@export var presentation: int = 1

var caption: String = ""
var data: Dictionary
var _label: Label

func _ready() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string("res://style/style_lab_data.json"))
	var layer := CanvasLayer.new()
	layer.layer = 10
	_label = Label.new()
	_label.position = Vector2(24, 52)
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
		KEY_T: palette = (palette + 1) % data.palettes.size()
		KEY_L: plan = (plan + 1) % data.plans.size()
		KEY_P: presentation = (presentation + 1) % env_levels.size()
		_: return
	apply()

func apply() -> void:
	for i in data.palettes.size():
		get_node("Geometry_" + data.palettes[i][0]).visible = i == palette
	var tiers_by_bay: Array = data.plans[plan][1]
	for b in tiers_by_bay.size():
		for tier in data.tiers:
			get_node("Lighting/Bays/Bay%d/%s" % [b, tier]).visible = tier in tiers_by_bay[b]
	$Environment.environment = env_levels[presentation]
	_label.text = "%s%s | light: %s | presentation: %s   [T palette  L lights  P present]" % [
		(caption + "  ") if caption != "" else "",
		data.palette_titles[data.palettes[palette][0]],
		data.plan_titles[data.plans[plan][0]],
		data.presentation[presentation]]
