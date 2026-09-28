@tool
class_name PropLight
extends Node3D
## A light prop: a fitting modelled in Blender (the Model child, imported from its .glb) carrying its own light.
## Everything worth tuning is on this node, so a placed light is edited in the inspector without opening its scene:
##   lit          off = a dead fitting: the light is out and the lens is dark (a dead fitting never glows).
##   color        the light's colour; the lens glows in it.
##   energy, light_range, shadows   the light's own settings.
##   wire         the hanging wires above the fitting (0 = flush against the ceiling). Run them up through the
##                ceiling into the void above the room when the fitting hangs.
##   flicker      a failing fitting: mostly out, with stuttering bursts (in the game, not the editor).
##   spin_speed   a beacon's turning beam, radians per second (in the game; 0 = still).
## For anything else, right-click the placed prop and choose Editable Children to reach the light node itself.
## Written by tools/write-props.py from the catalogue in tools/props.py.

const LENS := "res://props/materials/lens.tres"
const DEAD := preload("res://props/materials/lens_dead.tres")

@export var lit := true:
	set(v):
		lit = v
		_apply()
@export_color_no_alpha var color := Color(1, 1, 1):
	set(v):
		color = v
		_lens_mat = null
		_apply()
@export_range(0.0, 16.0, 0.05) var energy := 1.0:
	set(v):
		energy = v
		_apply()
@export_range(0.5, 40.0, 0.5) var light_range := 8.0:
	set(v):
		light_range = v
		_apply()
@export var shadows := true:
	set(v):
		shadows = v
		_apply()
@export_range(0.0, 8.0, 0.05) var wire := 0.0:
	set(v):
		wire = v
		_apply()
@export var flicker := false:
	set(v):
		flicker = v
		_on = true
		_apply()
@export var spin_speed := 0.0
## A dim glow beside the main light (a beacon's dome), as a share of its energy.
@export_range(0.0, 1.0, 0.01) var glow_ratio := 0.15:
	set(v):
		glow_ratio = v
		_apply()

var hold := false                      ## captures and tests freeze a flicker
var _on := true
var _lens_mat: StandardMaterial3D
var _timer := 0.0
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.seed = hash(str(global_position)) if is_inside_tree() else 7
	_apply()


func _apply() -> void:
	if not is_node_ready():
		return
	var on := lit and _on
	for l in _lights():
		var main := l.name == "Light"
		l.light_color = color
		l.visible = on
		l.light_energy = energy if main else energy * glow_ratio
		if main:
			l.shadow_enabled = shadows
			if l is OmniLight3D:
				(l as OmniLight3D).omni_range = light_range
			elif l is SpotLight3D:
				(l as SpotLight3D).spot_range = light_range
	var w := get_node_or_null("Model/Wires") as Node3D
	if w != null:
		w.visible = wire > 0.001
		w.scale = Vector3(1.0, maxf(wire, 0.001), 1.0)
	_set_lens(on)


func _lights() -> Array[Light3D]:
	var out: Array[Light3D] = []
	for n in find_children("*", "Light3D", true, false):
		out.append(n as Light3D)
	return out


## The lens glows in the light's colour while it is on, and is dark when it is off.
func _set_lens(on: bool) -> void:
	var mat: Material = DEAD
	if on:
		if _lens_mat == null:
			_lens_mat = (load(LENS) as StandardMaterial3D).duplicate()
			_lens_mat.albedo_color = color.lerp(Color.WHITE, 0.6)
			_lens_mat.emission = color
		mat = _lens_mat
	var model := get_node_or_null("Model")
	if model == null:
		return
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = (mi as MeshInstance3D).mesh
		if mesh == null:
			continue
		for i in mesh.get_surface_count():
			var m := mesh.surface_get_material(i)
			if m != null and m.resource_path == LENS:
				(mi as MeshInstance3D).set_surface_override_material(i, mat)


## Whether the lens is showing the glowing material (for the prop checks).
func lens_glowing() -> bool:
	var model := get_node_or_null("Model")
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = (mi as MeshInstance3D).mesh
		for i in mesh.get_surface_count():
			var m := mesh.surface_get_material(i)
			if m != null and m.resource_path == LENS:
				var o := (mi as MeshInstance3D).get_surface_override_material(i) as StandardMaterial3D
				return o != null and o.emission_enabled
	return false


func _process(delta: float) -> void:
	if Engine.is_editor_hint() or hold:
		return
	if spin_speed != 0.0:
		var spin := get_node_or_null("Spin") as Node3D
		if spin != null:
			spin.rotate_object_local(Vector3.UP, spin_speed * delta)
	if flicker and lit:
		_timer -= delta
		if _timer > 0.0:
			return
		_on = not _on
		if _on:
			_timer = _rng.randf_range(0.03, 0.18) if _rng.randf() < 0.75 else _rng.randf_range(0.5, 1.2)
		else:
			_timer = _rng.randf_range(0.04, 0.5) if _rng.randf() < 0.65 else _rng.randf_range(1.2, 2.8)
		_apply()
