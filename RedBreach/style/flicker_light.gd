extends Node3D
## A failing fitting: mostly out, with stuttering bursts, and sparks on some
## bursts. It switches every OmniLight3D and fitting under it together, so a
## dark fitting never glows (FR-006). Seeded, so the pattern repeats.

@export var lit_material: Material
@export var dead_material: Material
@export var seed: int = 7
## Captures and tests freeze the state instead of racing the random timer.
var hold: bool = false

var _rng := RandomNumberGenerator.new()
var _timer: float = 0.0
var _on: bool = false
var _lights: Array[OmniLight3D] = []
var _fittings: Array[MeshInstance3D] = []
var _sparks: GPUParticles3D

func _ready() -> void:
	_rng.seed = seed
	for child in get_children():
		if child is OmniLight3D:
			_lights.append(child)
		elif child is MeshInstance3D:
			_fittings.append(child)
		elif child is GPUParticles3D:
			_sparks = child
	_apply(false)

func _process(delta: float) -> void:
	if hold or not is_visible_in_tree():
		return
	_timer -= delta
	if _timer > 0.0:
		return
	if _on:
		_apply(false)
		_timer = _rng.randf_range(0.04, 0.5) if _rng.randf() < 0.65 else _rng.randf_range(1.2, 2.8)
	else:
		_apply(true)
		_timer = _rng.randf_range(0.03, 0.18) if _rng.randf() < 0.75 else _rng.randf_range(0.5, 1.2)
		if _rng.randf() < 0.3:
			spark()

func spark() -> void:
	if _sparks:
		_sparks.restart()
		_sparks.emitting = true

## Freeze in a state, for captures: on with a fresh burst of sparks, or out.
func force(on: bool, with_sparks: bool = false) -> void:
	hold = true
	_apply(on)
	if with_sparks:
		spark()

func is_lit() -> bool:
	return _on

func _apply(on: bool) -> void:
	_on = on
	for light in _lights:
		light.visible = on
	for fitting in _fittings:
		fitting.set_surface_override_material(0, lit_material if on else dead_material)
