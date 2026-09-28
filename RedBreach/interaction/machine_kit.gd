extends Node3D
## Moving machinery placed from the map (rb_machine). It changes nothing in progression; it moves so the level is not
## a still picture. There is no collision: every moving part is overhead or on top of a machine, out of reach.
##   kind  piston   a piston rising and falling through a housing at the ceiling, with a lamp that pumps with it.
##                  Origin: the centre of the machine's top. The housing is map geometry; "housing" is the height of
##                  its underside above the origin.
##         fitting  a light fitting torn loose, hanging from its cable: dead, not glowing, sparking from the break.
##                  Origin: the ceiling point it hangs from; "facing" is the way it hangs along the corridor.
##         plunger  a coolant pump's plunger rising out of its housing between the housing's guide posts and falling
##                  back, with a lamp in the coolant's colour that brightens on each push. Origin: the centre of the
##                  housing's top (map geometry, with the posts and the outlet pipe); "low" is the head's height above
##                  it at the bottom of the stroke, "phase" (0-1) offsets the cycle so a row of pumps takes turns.
## Plain loops, no states: neither piece has a transition to own. Seeded, so captures and tests repeat.
const Parts := preload("res://interaction/kit_parts.gd")

@export var func_godot_properties: Dictionary = {}
var kind := "piston"
var period := 2.4
var stroke := 0.9
var low := 0.7
var hold := false                      ## captures freeze the motion
var _t := 0.0
var _moving: Node3D
var _lamp: StandardMaterial3D
var _lamp_light: OmniLight3D
var _sparks: CPUParticles3D
var _flash: OmniLight3D
var _flash_time := 0.0
var _next_spark := 0.6
var _rng := RandomNumberGenerator.new()
var _hang := 0.0


func _func_godot_apply_properties(p: Dictionary) -> void:
	basis = Parts.facing_basis(Parts.plan_dir(str(p.get("facing", "0 1"))))


func _ready() -> void:
	add_to_group("progression_kit")      # its runtime parts are never saved into the level scene
	var p := func_godot_properties
	kind = str(p.get("kind", kind))
	period = float(p.get("period", period))
	stroke = float(p.get("stroke", stroke))
	low = float(p.get("low", low))
	_t = float(p.get("phase", 0.0)) * period
	_rng.seed = hash(str(p.get("id", name)))
	var look := str(p.get("look", "steel"))
	if kind == "fitting":
		_build_fitting(look)
	elif kind == "plunger":
		_build_plunger(look)
	else:
		_build_piston(look, float(p.get("radius", 0.55)), float(p.get("housing", 1.7)), float(p.get("ceiling", 2.8)))


func _build_piston(look: String, radius: float, housing: float, ceiling: float) -> void:
	var body := Parts.material(look, "machine_body")
	var steel := Parts.material(look, "frame")
	# The gland on the machine's top the rod slides through.
	_cylinder(self, radius * 0.8, 0.14, Vector3(0, 0.07, 0), body)
	# The moving part: the piston body, its top always inside the housing (just under the ceiling at the top of the
	# stroke), and the rod under it, always inside the gland.
	_moving = Node3D.new()
	add_child(_moving)
	var length := ceiling - 0.35 - stroke
	if 0.3 + length <= housing:
		push_warning("machine_kit: the piston leaves its housing; deepen the housing or shorten the stroke")
	_cylinder(_moving, radius, length, Vector3(0, 0.3 + length / 2, 0), steel)
	_cylinder(_moving, radius * 0.28, 0.5 + stroke + 0.3, Vector3(0, 0.3 - (0.5 + stroke + 0.3) / 2, 0), steel)
	_cylinder(_moving, radius * 1.04, 0.08, Vector3(0, 0.34, 0), body)        # a collar, so the stroke reads
	# The pumping lamp: on the gland, brightest as the piston comes down.
	_lamp = Parts.glow(Color(1.0, 0.55, 0.15), 0.5)
	Parts.box(self, Vector3(0.12, 0.06, 0.12), Vector3(0, 0.17, radius * 0.8), _lamp)
	Parts.box(self, Vector3(0.12, 0.06, 0.12), Vector3(0, 0.17, -radius * 0.8), _lamp)
	_lamp_light = OmniLight3D.new()
	_lamp_light.light_color = Color(1.0, 0.6, 0.25)
	_lamp_light.omni_range = 3.5
	_lamp_light.shadow_enabled = false
	_lamp_light.position = Vector3(0, 0.3, 0)
	add_child(_lamp_light)
	_apply_piston()


func _build_plunger(look: String) -> void:
	var body := Parts.material(look, "machine_body")
	var steel := Parts.material(look, "frame")
	# The gland on the housing's top the rod slides through, with the lamp on its front.
	_cylinder(self, 0.28, 0.16, Vector3(0, 0.08, 0), body)
	_lamp = Parts.glow(Color(0.3, 0.9, 0.75), 0.4)
	Parts.box(self, Vector3(0.16, 0.08, 0.05), Vector3(0, 0.1, 0.3), _lamp)
	Parts.box(self, Vector3(0.16, 0.08, 0.05), Vector3(0, 0.1, -0.3), _lamp)
	_lamp_light = OmniLight3D.new()
	_lamp_light.light_color = Color(0.35, 0.95, 0.8)
	_lamp_light.omni_range = 3.0
	_lamp_light.shadow_enabled = false
	_lamp_light.position = Vector3(0, 0.3, 0)
	add_child(_lamp_light)
	# The moving part: the crosshead between the guide posts, and the rod under it, always inside the gland.
	_moving = Node3D.new()
	add_child(_moving)
	Parts.box(_moving, Vector3(1.0, 0.3, 0.5), Vector3(0, 0, 0), steel)
	Parts.box(_moving, Vector3(0.7, 0.12, 0.36), Vector3(0, 0.21, 0), body)
	var rod := low + 0.4
	_cylinder(_moving, 0.14, rod, Vector3(0, -rod / 2.0, 0), steel)
	_apply_plunger()


func _build_fitting(look: String) -> void:
	var body := Parts.material(look, "machine_body")
	var dead := StandardMaterial3D.new()                # the diffuser, dark: a dead fitting never glows
	dead.albedo_color = Color(0.16, 0.16, 0.17)
	var wire := StandardMaterial3D.new()
	wire.albedo_color = Color(0.05, 0.05, 0.05)
	# The bracket it still hangs from, and the torn one at the other end.
	Parts.box(self, Vector3(0.2, 0.03, 0.12), Vector3(0, -0.015, 0), body)
	Parts.box(self, Vector3(0.2, 0.03, 0.12), Vector3(0, -0.015, 1.2), body)
	Parts.box(self, Vector3(0.012, 0.55, 0.012), Vector3(0, -0.275, 0), wire)     # the cable
	# The broken wires hanging from the torn bracket: the sparks come from here.
	Parts.box(self, Vector3(0.01, 0.34, 0.01), Vector3(0.03, -0.2, 1.2), wire, false, Vector3(0.25, 0, 0))
	Parts.box(self, Vector3(0.01, 0.26, 0.01), Vector3(-0.03, -0.16, 1.18), wire, false, Vector3(-0.15, 0, 0.2))
	# The fitting, hanging from the cable's end by one end.
	_moving = Node3D.new()
	_moving.position = Vector3(0, -0.55, 0)
	add_child(_moving)
	Parts.box(_moving, Vector3(0.24, 0.1, 1.2), Vector3(0, 0, 0.6), body)
	Parts.box(_moving, Vector3(0.18, 0.02, 1.1), Vector3(0, -0.055, 0.6), dead)
	_sparks = CPUParticles3D.new()
	_sparks.emitting = false
	_sparks.one_shot = true
	_sparks.amount = 36
	_sparks.lifetime = 0.7
	_sparks.explosiveness = 0.95
	_sparks.direction = Vector3(0, -1, 0)
	_sparks.spread = 70.0
	_sparks.initial_velocity_min = 1.0
	_sparks.initial_velocity_max = 3.0
	_sparks.gravity = Vector3(0, -9.8, 0)
	var dot := SphereMesh.new()
	dot.radius = 0.012
	dot.height = 0.024
	dot.material = Parts.glow(Color(1.0, 0.8, 0.35), 4.0)
	_sparks.mesh = dot
	_sparks.position = Vector3(0, -0.36, 1.2)
	add_child(_sparks)
	_flash = OmniLight3D.new()
	_flash.light_color = Color(1.0, 0.8, 0.45)
	_flash.omni_range = 4.5
	_flash.light_energy = 0.0
	_flash.shadow_enabled = false
	_flash.position = _sparks.position
	add_child(_flash)
	_hang = deg_to_rad(58.0)
	_apply_fitting()


## An eight-sided cylinder, the crunchy look of the map's octagonal prisms.
func _cylinder(parent: Node3D, r: float, h: float, at: Vector3, mat: Material) -> void:
	var mi := MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = r
	cm.bottom_radius = r
	cm.height = h
	cm.radial_segments = 8
	cm.rings = 1
	mi.mesh = cm
	mi.material_override = mat
	mi.position = at
	parent.add_child(mi)


func _process(delta: float) -> void:
	if hold:
		return
	_t += delta
	if kind == "fitting":
		_apply_fitting()
		_next_spark -= delta
		if _next_spark <= 0.0:
			spark()
			_next_spark = _rng.randf_range(0.12, 0.3) if _rng.randf() < 0.35 else _rng.randf_range(1.0, 3.2)
		_flash_time = maxf(0.0, _flash_time - delta)
		_flash.light_energy = 2.2 if _flash_time > 0.0 else 0.0
	elif kind == "plunger":
		_apply_plunger()
	else:
		_apply_piston()


func _apply_plunger() -> void:
	var s := 0.5 - 0.5 * cos(TAU * _t / period)          # 0 down, 1 up
	_moving.position.y = low + stroke * s
	# The push is the upstroke, driving coolant up the outlet pipe: the lamp brightens with it.
	_lamp.emission_energy_multiplier = 0.3 + 2.4 * s
	_lamp_light.light_energy = 0.1 + 0.5 * s


func _apply_piston() -> void:
	var s := 0.5 - 0.5 * cos(TAU * _t / period)          # 0 down, 1 up
	_moving.position.y = stroke * s
	var glow := 1.0 - s
	_lamp.emission_energy_multiplier = 0.3 + 2.2 * glow
	_lamp_light.light_energy = 0.15 + 0.6 * glow


func _apply_fitting() -> void:
	# A slow sway on its cable.
	_moving.rotation = Vector3(_hang + deg_to_rad(1.5) * sin(_t * 1.7), deg_to_rad(2.0) * sin(_t * 0.9), 0.0)


## A burst of sparks from the break, with a short flash.
func spark() -> void:
	if _sparks == null:
		return
	_sparks.restart()
	_sparks.emitting = true
	_flash_time = 0.08


## Freeze for a capture: the piston at a point of its stroke, the fitting with a fresh burst of sparks.
func force(at: float = 0.5, with_sparks: bool = true) -> void:
	hold = true
	_t = at * period
	if kind == "fitting":
		_apply_fitting()
		if with_sparks:
			spark()
			_flash.light_energy = 2.2
	elif kind == "plunger":
		_apply_plunger()
	else:
		_apply_piston()
