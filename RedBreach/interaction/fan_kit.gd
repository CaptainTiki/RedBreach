extends Node3D
## The big fan (rb_fan): blades turning in a round hole in a wall. The StateChart owns Running, SpinningDown and
## Stopped (a reset from anywhere goes back to Running). While it turns, a solid disc closes the hole: from the pipe room
## it is only a spinning disc. Its stop event (the fan chamber's lever) spins it down, and it comes to rest one blade up,
## where a crouching player fits between the two lower blades. Origin: the hub centre; "facing" is the disc's normal.
const Parts := preload("res://interaction/kit_parts.gd")
const Progression := preload("res://interaction/progression.gd")

@export var func_godot_properties: Dictionary = {}
@export var run_speed := 6.0          ## rad/s (user, 2026-09-27: it turned too slowly to read as running)
@export var spin_down := 1.6          ## rad/s per second while it spins down: the slowing is plain to see
@export var settle_speed := 0.35      ## the last, slow turn to blade-up
@onready var chart: StateChart = $StateChart

var kit_id := "FAN"
var stop_event := "fan_stop"
var radius := 1.5
var blades := 3
var hub_radius := 0.3
var blade_width := 0.3
var angle := 0.0
var speed := 0.0
var _target := INF
var _rotor: AnimatableBody3D
var _disc: CollisionShape3D
var _progression: Node
var _sparks: CPUParticles3D
var _flash: OmniLight3D
var _bursts := 0                      ## spark bursts still to come as it spins down
var _burst_time := 0.0
var _flash_time := 0.0


func _func_godot_apply_properties(p: Dictionary) -> void:
	basis = Parts.facing_basis(Parts.plan_dir(str(p.get("facing", "0 1"))))


func _enter_tree() -> void:
	if not Engine.is_editor_hint() and not EngineDebugger.is_active():
		$StateChart.track_in_editor = false


func _ready() -> void:
	add_to_group("progression_kit")
	var p := func_godot_properties
	kit_id = str(p.get("id", kit_id))
	stop_event = str(p.get("event", stop_event))
	radius = float(p.get("diameter", 3.0)) / 2.0
	blades = int(p.get("blades", 3))
	hub_radius = float(p.get("hub_radius", 0.3))
	blade_width = float(p.get("blade_width", 0.3))
	_build(str(p.get("look", "steel")))
	speed = run_speed
	_apply()
	_connect_progression.call_deferred()


func _connect_progression() -> void:
	_progression = Progression.of(self)
	if _progression != null:
		_progression.fired.connect(func(event: String):
			if event == stop_event:
				chart.send_event("stop"))
		_progression.reset_all.connect(func(): chart.send_event("reset"))


func _build(look: String) -> void:
	_rotor = AnimatableBody3D.new()
	_rotor.name = "Rotor"
	_rotor.sync_to_physics = false
	add_child(_rotor)
	var blade := Parts.material(look, "frame")
	var hub := Parts.material(look, "machine_top")
	var length := radius - hub_radius - 0.05
	for k in blades:
		var a := k * TAU / blades
		var r := hub_radius + length / 2.0
		Parts.box(_rotor, Vector3(length, blade_width, 0.08), Vector3(cos(a) * r, sin(a) * r, 0), blade, true, Vector3(0, 0, a))
	var hub_mesh := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = hub_radius
	cyl.bottom_radius = hub_radius
	cyl.height = 0.3
	hub_mesh.mesh = cyl
	hub_mesh.material_override = hub
	hub_mesh.rotation.x = PI / 2
	_rotor.add_child(hub_mesh)
	var hub_shape := CollisionShape3D.new()
	var hs := CylinderShape3D.new()
	hs.radius = hub_radius
	hs.height = 0.3
	hub_shape.shape = hs
	hub_shape.rotation.x = PI / 2
	_rotor.add_child(hub_shape)
	# The disc: solid while the blades turn.
	var disc_body := StaticBody3D.new()
	disc_body.name = "Disc"
	add_child(disc_body)
	_disc = CollisionShape3D.new()
	var ds := CylinderShape3D.new()
	ds.radius = radius
	ds.height = 0.12
	_disc.shape = ds
	_disc.rotation.x = PI / 2
	disc_body.add_child(_disc)
	# Sparks from the hub the moment the lever cuts the drive (user, 2026-09-27: feedback at once, then the slowing).
	_sparks = CPUParticles3D.new()
	_sparks.emitting = false
	_sparks.one_shot = true
	_sparks.amount = 48
	_sparks.lifetime = 0.8
	_sparks.explosiveness = 0.9
	_sparks.direction = Vector3(0, 0, 1)
	_sparks.spread = 180.0
	_sparks.initial_velocity_min = 1.5
	_sparks.initial_velocity_max = 4.0
	_sparks.gravity = Vector3(0, -9.8, 0)
	var dot := SphereMesh.new()
	dot.radius = 0.015
	dot.height = 0.03
	dot.material = Parts.glow(Color(1.0, 0.8, 0.35), 4.0)
	_sparks.mesh = dot
	add_child(_sparks)
	_flash = OmniLight3D.new()
	_flash.light_color = Color(1.0, 0.8, 0.45)
	_flash.omni_range = 5.0
	_flash.light_energy = 0.0
	_flash.shadow_enabled = false
	add_child(_flash)


func _apply() -> void:
	_rotor.rotation = Vector3(0, 0, angle)


## The next angle at or after a, where one blade points straight up.
func _next_blade_up(a: float) -> float:
	var step := TAU / blades
	return PI / 2.0 + ceil((a - PI / 2.0) / step) * step


func state_name() -> String:
	for state in $StateChart/Motion.get_children():
		if state is StateChartState and state.active:
			return str(state.name)
	return "Starting"


func busy() -> bool:
	return state_name() == "SpinningDown"


func use_done() -> bool:
	return state_name() == "Stopped"


func use_point() -> Vector3:
	return global_position


func _on_running_physics(delta: float) -> void:
	angle = fmod(angle + run_speed * delta, TAU)
	_apply()


func _burst() -> void:
	_sparks.restart()
	_sparks.emitting = true
	_flash_time = 0.1


func _process(delta: float) -> void:
	if _flash == null:
		return
	_flash_time = maxf(0.0, _flash_time - delta)
	_flash.light_energy = 2.5 if _flash_time > 0.0 else 0.0


func _on_spinning_down_physics(delta: float) -> void:
	if _bursts > 0:
		_burst_time -= delta
		if _burst_time <= 0.0:
			_burst()
			_bursts -= 1
			_burst_time = 0.45
	speed = maxf(settle_speed, speed - spin_down * delta)
	if speed <= settle_speed and _target == INF:
		_target = _next_blade_up(angle + 0.05)
	var next := angle + speed * delta
	if next >= _target:
		angle = fmod(_target, TAU)
		_target = INF
		_apply()
		chart.send_event("settled")
		return
	angle = next
	_apply()


func _on_state_entered(label: String) -> void:
	match label:
		"Running":
			speed = run_speed
			_target = INF
			_bursts = 0
			_disc.set_deferred("disabled", false)
		"SpinningDown":
			speed = run_speed
			_target = INF
			_burst()
			_bursts = 2
			_burst_time = 0.45
		"Stopped":
			_disc.set_deferred("disabled", true)
