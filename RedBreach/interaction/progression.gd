extends Node
## A level's progression: its flags (cards taken, power restored) and events (switches, levers), in one place.
## The progression kit (door_kit, switch_kit, pickup_kit, fan_kit, drawbridge_kit) finds it by group and listens.
## reset() puts the whole level back as it started (the player's Backspace): flags cleared, doors shut, the fan
## running, the drawbridge up. The "start" event fires a moment after the level starts or resets (the airlock opens).

signal fired(event: String)
signal reset_all

@export var start_delay := 1.0
var flags := {}
var _start_timer: SceneTreeTimer

func _ready() -> void:
	add_to_group("progression")
	_schedule_start()

func has_flag(flag: String) -> bool:
	return flags.get(flag, false)

## Every flag in a comma list, e.g. "K,P". An empty list is always met.
func has_all(needs: String) -> bool:
	for f in needs.split(",", false):
		if not has_flag(f.strip_edges()):
			return false
	return true

func missing(needs: String) -> PackedStringArray:
	var out := PackedStringArray()
	for f in needs.split(",", false):
		if not has_flag(f.strip_edges()):
			out.append(f.strip_edges())
	return out

func set_flag(flag: String) -> void:
	if not has_flag(flag):
		flags[flag] = true
		fired.emit("flag:" + flag)

func send(event: String) -> void:
	for e in event.split(",", false):
		fired.emit(e.strip_edges())

func reset() -> void:
	flags.clear()
	reset_all.emit()
	_schedule_start()

func _schedule_start() -> void:
	_start_timer = get_tree().create_timer(start_delay, false)
	var timer := _start_timer
	timer.timeout.connect(func():
		if timer == _start_timer:
			send("start"))

## The progression a kit node belongs to (the first in the tree), or null in a level without one.
static func of(node: Node) -> Node:
	return node.get_tree().get_first_node_in_group("progression") if node.is_inside_tree() else null
