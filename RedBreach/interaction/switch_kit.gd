extends StaticBody3D
## A switch or lever placed from the map (rb_switch). E uses it: it sends events (a door opens, the fan stops, the
## catwalk section lowers), sets progression flags (power), or only sparks (the pipe bay's switch 1). A once-only switch
## stays thrown until Backspace resets the level. No labels: its lamp goes from red to green when thrown.
##   mount  wall  a panel on the wall the entity stands against, facing "facing"
##          post  a free-standing console facing "facing"
##          flat  a sheet lying on a surface (a note on a desk): read it once
const Parts := preload("res://interaction/kit_parts.gd")
const Progression := preload("res://interaction/progression.gd")

@export var func_godot_properties: Dictionary = {}
var kit_id := ""
var sends := ""
var sets := ""
var once := true
var effect := ""
var notice_text := ""
var prompt := "E  Use"
var _used := false
var _handle: MeshInstance3D
var _lamp_material: StandardMaterial3D
var _progression: Node
var _sparks: CPUParticles3D
var _flash: OmniLight3D
var _flash_time := 0.0
var _panel_height := 1.2


func _func_godot_apply_properties(p: Dictionary) -> void:
	basis = Parts.facing_basis(Parts.plan_dir(str(p.get("facing", "0 1"))))


func _ready() -> void:
	add_to_group("progression_kit")
	var p := func_godot_properties
	kit_id = str(p.get("id", name))
	sends = str(p.get("sends", ""))
	sets = str(p.get("sets", ""))
	once = int(p.get("once", 1)) == 1
	effect = str(p.get("effect", ""))
	notice_text = str(p.get("notice", ""))
	prompt = str(p.get("prompt", "E  Use"))
	_build(str(p.get("mount", "wall")), str(p.get("look", "steel")))
	_connect_progression.call_deferred()


func _connect_progression() -> void:
	_progression = Progression.of(self)
	if _progression != null:
		_progression.reset_all.connect(_on_reset)


func _build(mount: String, look: String) -> void:
	var body := Parts.material(look, "machine_body")
	var screen := Parts.material(look, "screen")
	var h := _panel_height
	if mount == "flat":
		# A clipboard with a sheet on it. A bare sheet sat too close to the surface under it and vanished into it.
		var paper := StandardMaterial3D.new()
		paper.albedo_color = Color(0.62, 0.6, 0.54)
		Parts.box(self, Vector3(0.24, 0.012, 0.33), Vector3(0, 0.006, 0), body)
		Parts.box(self, Vector3(0.2, 0.004, 0.28), Vector3(0, 0.014, 0.01), paper)
		Parts.box(self, Vector3(0.1, 0.01, 0.03), Vector3(0, 0.017, -0.14), screen)
		var cs := CollisionShape3D.new()        # a little thicker than the board, so the crosshair finds it
		var bs := BoxShape3D.new()
		bs.size = Vector3(0.24, 0.06, 0.33)
		cs.shape = bs
		cs.position = Vector3(0, 0.03, 0)
		add_child(cs)
		_panel_height = 0.0
		return
	if mount == "post":
		# A console: a body 1 m tall, its sloped top panel facing the user.
		Parts.box(self, Vector3(0.5, 1.0, 0.4), Vector3(0, 0.5, 0), body, true)
		Parts.box(self, Vector3(0.44, 0.04, 0.34), Vector3(0, 1.02, 0.02), screen, false, Vector3(deg_to_rad(-25), 0, 0))
		h = 1.05
	else:
		# A panel on the wall face; the entity stands on the wall's face line.
		Parts.box(self, Vector3(0.42, 0.56, 0.08), Vector3(0, h, 0.04), body, true)
		Parts.box(self, Vector3(0.3, 0.3, 0.02), Vector3(0, h + 0.05, 0.085), screen)
	_handle = Parts.box(self, Vector3(0.06, 0.24, 0.06), Vector3(0, h - 0.12, 0.2 if mount == "post" else 0.14), Parts.material(look, "hazard"))
	_lamp_material = Parts.glow(Color(1.0, 0.12, 0.08))
	Parts.box(self, Vector3(0.08, 0.05, 0.03), Vector3(0.15, h + 0.24 if mount == "wall" else 1.1, 0.1 if mount == "wall" else 0.2), _lamp_material)
	_panel_height = h
	if effect == "spark":
		_sparks = CPUParticles3D.new()
		_sparks.emitting = false
		_sparks.one_shot = true
		_sparks.amount = 28
		_sparks.lifetime = 0.55
		_sparks.explosiveness = 0.9
		_sparks.direction = Vector3(0, 0.4, 1)
		_sparks.spread = 60.0
		_sparks.initial_velocity_min = 1.5
		_sparks.initial_velocity_max = 3.5
		_sparks.gravity = Vector3(0, -9.8, 0)
		var dot := SphereMesh.new()
		dot.radius = 0.012
		dot.height = 0.024
		dot.material = Parts.glow(Color(1.0, 0.8, 0.35), 4.0)
		_sparks.mesh = dot
		_sparks.position = Vector3(0, h + 0.05, 0.12)
		add_child(_sparks)
		_flash = OmniLight3D.new()
		_flash.light_color = Color(1.0, 0.8, 0.4)
		_flash.omni_range = 3.0
		_flash.light_energy = 0.0
		_flash.position = _sparks.position
		add_child(_flash)


func get_interaction_prompt() -> String:
	return use_prompt()


func interact() -> bool:
	return use()


func use_prompt() -> String:
	return "" if once and _used else prompt


func use() -> bool:
	if once and _used:
		return false
	_used = true
	if _sparks != null:
		_sparks.restart()
		_sparks.emitting = true
		_flash_time = 0.18
	if once and _handle != null:
		_handle.rotation.x = deg_to_rad(70)
		_lamp_material.albedo_color = Color(0.15, 0.95, 0.5)
		_lamp_material.emission = _lamp_material.albedo_color
	if _progression != null:
		for f in sets.split(",", false):
			_progression.set_flag(f.strip_edges())
		if sends != "":
			_progression.send(sends)
	Parts.notice(self, notice_text)
	return true


func use_done() -> bool:
	return once and _used


func busy() -> bool:
	return false


func use_point() -> Vector3:
	return global_position + Vector3.UP * _panel_height


func _process(delta: float) -> void:
	if _flash != null:
		_flash_time = maxf(0.0, _flash_time - delta)
		_flash.light_energy = 3.0 if _flash_time > 0.0 else 0.0


func _on_reset() -> void:
	_used = false
	if _handle == null:
		return
	_handle.rotation.x = 0.0
	_lamp_material.albedo_color = Color(1.0, 0.12, 0.08)
	_lamp_material.emission = _lamp_material.albedo_color
