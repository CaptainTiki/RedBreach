extends Node3D
## A door of any size, placed from the map (rb_door). The StateChart owns its movement (Closed, Opening, Open,
## Closing, Blocked, and a reset from anywhere back to Closed); this script checks the door's rule before asking it to
## open, and drives the leaf and the lamps. No labels: a lamp over each face is red while the door will not open for
## you, amber while it will, green when open.
##   opens  use    E from either side: an ordinary door, which closes again
##          side   E only from the side "side" points to: a release, on the far side of an objective
##          event  only a switch or lever, by event name (door 5, the cage gate)
##          start  opens on its own when the level is ready (the arrival airlock)
##   needs  progression flags it needs, e.g. "K,P"; needs_text names them for the prompt ("K=the freight card;P=power")
##   latch  once open it stays open
##   style  rise   one leaf lifts straight up into the wall (any part that clears the wall is above a ceiling)
##          slide  two leaves part sideways (gates in fences, with open room above them)
const Parts := preload("res://interaction/kit_parts.gd")
const Progression := preload("res://interaction/progression.gd")
const Use := preload("res://interaction/kit_use.gd")

@export var func_godot_properties: Dictionary = {}
@export_range(0.2, 3.0) var travel_time := 0.9
@export_flags_3d_physics var blocker_mask := 1
@onready var chart: StateChart = $StateChart

var kit_id := ""
var opens := "use"
var needs := ""
var needs_text := {}
var latch := false
var style := "rise"
var events := PackedStringArray()
var width := 2.0
var height := 2.5
var side_dir := Vector3.ZERO
var open_amount := 0.0
var _leaves: Array[AnimatableBody3D] = []
var _lamp_material: StandardMaterial3D
var _clearance: CollisionShape3D
var _progression: Node
var _deny_until := 0.0


func _func_godot_apply_properties(p: Dictionary) -> void:
	basis = Parts.facing_basis(Parts.plan_dir(str(p.get("facing", "0 1"))))


func _enter_tree() -> void:
	# As the gym door: the addon expects a connected editor debugger when tracking is enabled.
	if not Engine.is_editor_hint() and not EngineDebugger.is_active():
		$StateChart.track_in_editor = false


func _ready() -> void:
	add_to_group("progression_kit")
	var p := func_godot_properties
	kit_id = str(p.get("id", name))
	opens = str(p.get("opens", "use"))
	needs = str(p.get("needs", ""))
	latch = int(p.get("latch", 0)) == 1
	style = str(p.get("style", "rise"))
	events = str(p.get("events", kit_id)).split(",", false)
	if opens == "start" and not "start" in events:
		events.append("start")
	width = float(p.get("width", 2.0))
	height = float(p.get("height", 2.5))
	side_dir = Parts.plan_dir(str(p.get("side", "0 0")), Vector3.ZERO)
	for pair in str(p.get("needs_text", "")).split(";", false):
		var kv := pair.split("=", false, 1)
		if kv.size() == 2:
			needs_text[kv[0].strip_edges()] = kv[1].strip_edges()
	_build(str(p.get("look", "steel")))
	_update_leaves()
	_show_lamp()
	_connect_progression.call_deferred()


func _connect_progression() -> void:
	_progression = Progression.of(self)
	if _progression != null:
		_progression.fired.connect(_on_fired)
		_progression.reset_all.connect(_on_reset)
		_show_lamp()


func _build(look: String) -> void:
	var leaf_material := Parts.material(look, "door")
	var count := 2 if style == "slide" else 1
	for i in count:
		var leaf := AnimatableBody3D.new()
		leaf.sync_to_physics = false        # as the gym door: moving the leaf moves its collision at once
		leaf.set_script(Use)
		leaf.owner_kit = self
		leaf.name = "Leaf%d" % i
		add_child(leaf)
		var w := width / count
		Parts.box(leaf, Vector3(w - 0.02, height - 0.02, 0.12), Vector3(0, height / 2.0, 0), leaf_material, true)
		_leaves.append(leaf)
	_lamp_material = Parts.glow(Color(1.0, 0.55, 0.12))
	for z in [0.27, -0.27]:
		Parts.box(self, Vector3(minf(0.5, width * 0.4), 0.07, 0.04), Vector3(0, height + 0.14, z), _lamp_material)
	var area := Area3D.new()
	area.name = "Clearance"
	area.collision_layer = 0
	add_child(area)
	_clearance = CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = Vector3(width - 0.1, height - 0.1, 1.2)
	_clearance.shape = shape
	_clearance.position = Vector3(0, height / 2.0, 0)
	area.add_child(_clearance)


func _update_leaves() -> void:
	if style == "slide":
		var half := width / 4.0
		for i in _leaves.size():
			var sgn := -1.0 if i == 0 else 1.0
			_leaves[i].position = Vector3(sgn * (half + open_amount * (width / 2.0 - 0.04)), 0, 0)
	else:
		for leaf in _leaves:
			leaf.position = Vector3(0, open_amount * (height - 0.05), 0)


# --- the rule --------------------------------------------------------------------------------------------------

## Why this door will not open for someone standing where the camera is ("" when it will).
func refusal() -> String:
	match opens:
		"event", "start":
			return "Locked"
		"side":
			var viewer := _viewer()
			if (viewer - global_position).dot(side_dir) <= 0.0:
				return "Locked from this side"
	if needs != "" and _progression != null and not _progression.has_all(needs):
		var names := PackedStringArray()
		for f in _progression.missing(needs):
			names.append(needs_text.get(f, f))
		return "Needs " + " and ".join(names)
	return ""


func _viewer() -> Vector3:
	var cam := get_viewport().get_camera_3d() if is_inside_tree() else null
	return cam.global_position if cam != null else global_position


func state_name() -> String:
	for state in $StateChart/Movement.get_children():
		if state is StateChartState and state.active:
			return str(state.name)
	return "Starting"


func use_prompt() -> String:
	match state_name():
		"Closed", "Closing":
			var why := refusal()
			return why if why != "" else "E  Open"
		"Open":
			return "" if latch else "E  Close"
		"Blocked":
			return "Blocked - clear the doorway"
	return ""


func use() -> bool:
	match state_name():
		"Closed", "Closing":
			if refusal() != "":
				_deny_until = Time.get_ticks_msec() / 1000.0 + 0.5
				_show_lamp()
				return false
			chart.send_event("open_requested")
			return true
		"Open":
			if latch:
				return false
			chart.send_event("obstructed" if is_doorway_blocked() else "close_requested")
			return true
	return false


## For the route checker: nothing left to do here (the door stands open).
func use_done() -> bool:
	return state_name() == "Open"


func busy() -> bool:
	return state_name() in ["Opening", "Closing", "Blocked", "Starting"]


## Where a player stands to use it: the middle of the opening.
func use_point() -> Vector3:
	return global_position + Vector3.UP * minf(1.2, height / 2.0)


func is_doorway_blocked() -> bool:
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = _clearance.shape
	query.transform = _clearance.global_transform
	query.collision_mask = blocker_mask
	var exclude: Array[RID] = []
	for leaf in _leaves:
		exclude.append(leaf.get_rid())
	query.exclude = exclude
	for hit in get_world_3d().direct_space_state.intersect_shape(query, 32):
		if hit.collider is CharacterBody3D or hit.collider is RigidBody3D:
			return true
	return false


# --- progression ------------------------------------------------------------------------------------------------

func _on_fired(event: String) -> void:
	if event in events and state_name() in ["Closed", "Closing"]:
		chart.send_event("open_requested")
	elif event.begins_with("flag:"):
		_show_lamp()


func _on_reset() -> void:
	chart.send_event("reset")
	open_amount = 0.0
	_update_leaves()
	_show_lamp()


# --- movement (StateChart callbacks) -------------------------------------------------------------------------------

func _move_towards(target: float, delta: float) -> void:
	open_amount = move_toward(open_amount, target, delta / maxf(travel_time, 0.01))
	_update_leaves()


func _on_opening_physics(delta: float) -> void:
	_move_towards(1.0, delta)
	if open_amount >= 1.0:
		chart.send_event("fully_open")


func _on_closing_physics(delta: float) -> void:
	if is_doorway_blocked():
		chart.send_event("obstructed")
		return
	_move_towards(0.0, delta)
	if open_amount <= 0.0:
		chart.send_event("fully_closed")


func _on_blocked_physics(delta: float) -> void:
	_move_towards(1.0, delta)
	if open_amount >= 1.0 and not is_doorway_blocked():
		chart.send_event("clear")


func _on_state_entered(_label: String) -> void:
	_show_lamp()


func _physics_process(_delta: float) -> void:
	if _deny_until > 0.0 and Time.get_ticks_msec() / 1000.0 > _deny_until:
		_deny_until = 0.0
		_show_lamp()


## Red while it will not open for anyone who could reach it now (or just refused), amber closed, green open.
func _show_lamp() -> void:
	if _lamp_material == null or not is_inside_tree():
		return
	var color := Color(1.0, 0.55, 0.12)
	var state := state_name()
	if state in ["Open", "Opening"]:
		color = Color(0.15, 0.95, 0.5)
	elif _deny_until > 0.0 or opens in ["event", "start"] or (needs != "" and _progression != null and not _progression.has_all(needs)):
		color = Color(1.0, 0.12, 0.08)
	_lamp_material.albedo_color = color
	_lamp_material.emission = color
