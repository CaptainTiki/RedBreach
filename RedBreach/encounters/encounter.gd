extends Node3D
signal started(encounter: Node)
signal enemy_spawned(encounter: Node)
signal vent_burst(encounter: Node)
signal enemy_damaged(encounter: Node)
signal cleared(encounter: Node)
@export var encounter_id: String = "encounter"
@export var title: String = "Encounter"
@export_enum("Preplaced", "Vent", "Mixed") var introduction: int = 0
@export var enemy_scenes: Array[PackedScene] = []
@export var preplaced_count: int = 0
@export var burst_delay_seconds: float = 0.0
@export var minimum_spawn_distance: float = 0.0
@export var cue_seconds: float = 0.35
@export var spawn_interval: float = 0.25
var enemies: Array[CharacterBody3D] = []
var run: Node
var player: CharacterBody3D
var enabled: bool = false
var _pending: int = 0
var _clock: float = 0.0
var spawn_blocked: bool = false
var _starting: bool = false

func _enter_tree() -> void:
	if not EngineDebugger.is_active(): $Chart.track_in_editor = false
func _ready() -> void:
	$Trigger.body_entered.connect(_on_body_entered)
	$Vent.visible = introduction != 0
func state() -> String:
	for child in $Chart/Encounter.get_children():
		if child.get("active") == true: return child.name
	return ""
func prepare(target: CharacterBody3D, with_enemies: bool, controller: Node) -> void:
	cancel()
	for enemy in enemies:
		if is_instance_valid(enemy):
			enemy.collision_layer = 0
			enemy.get_node("CollisionShape3D").disabled = true
			enemy.queue_free()
	enemies.clear()
	run = controller
	player = target
	enabled = with_enemies
	_pending = 0
	_clock = 0.0
	spawn_blocked = false
	$Vent.reset_vent()
	$Chart.send_event("reset")
	# Room enemies are physically present before the run, then armed at the start line.
	if enabled:
		var initial: int = enemy_scenes.size() if introduction == 0 else (clampi(preplaced_count, 0, enemy_scenes.size()) if introduction == 2 else 0)
		for i in initial: _spawn(i, false)
		_pending = initial
func arm() -> void:
	if introduction != 1 and enabled:
		for enemy in enemies: enemy.target = player
func _on_body_entered(body: Node3D) -> void:
	if body == player and introduction != 0: begin.call_deferred()
func begin() -> bool:
	if not enabled or state() != "Armed" or not is_instance_valid(player) or not player.is_alive(): return false
	if not is_instance_valid(run) or not run.is_running(): return false
	if _pending < enemy_scenes.size():
		$Chart.send_event("delay" if burst_delay_seconds > 0.0 else "introduce")
		_clock = burst_delay_seconds
	else:
		$Chart.send_event("fight")
	started.emit(self)
	if state() == "Introducing": _burst_vent()
	_starting = true
	for enemy in enemies: enemy.activate(player)
	_starting = false
	return true
func _burst_vent() -> void:
	$Vent.burst()
	_clock = cue_seconds
	vent_burst.emit(self)
func _spawn(index: int, check_clearance: bool) -> bool:
	var markers := $Spawns.get_children()
	if index >= markers.size() or index >= enemy_scenes.size(): return false
	var marker: Node3D = markers[index]
	if check_clearance:
		if marker.global_position.distance_to(player.global_position) < minimum_spawn_distance: return false
		var query := PhysicsShapeQueryParameters3D.new()
		var capsule := CapsuleShape3D.new()
		capsule.radius = 0.8
		capsule.height = 1.9
		query.shape = capsule
		query.transform = Transform3D(Basis.IDENTITY, marker.global_position + Vector3.UP * 1.0)
		query.collision_mask = 1
		if not get_world_3d().direct_space_state.intersect_shape(query).is_empty(): return false
	var enemy: CharacterBody3D = enemy_scenes[index].instantiate()
	enemy.transform = $Enemies.global_transform.affine_inverse() * marker.global_transform
	$Enemies.add_child(enemy)
	enemy.died.connect(_on_enemy_died)
	enemy.alerted.connect(_on_enemy_alerted)
	enemy.damaged.connect(_on_enemy_damaged)
	enemies.append(enemy)
	if check_clearance:
		enemy.activate.call_deferred(player)
		enemy_spawned.emit(self)
	return true
func _on_enemy_alerted() -> void:
	if not _starting and introduction != 1 and state() == "Armed": begin()
func _on_enemy_damaged(_amount: float) -> void:
	enemy_damaged.emit(self)
func _on_enemy_died() -> void:
	if state() != "Fighting" or _pending < enemy_scenes.size(): return
	for enemy in enemies:
		if is_instance_valid(enemy) and enemy.health > 0.0: return
	$Chart.send_event("clear")
	cleared.emit(self)
func cancel() -> void:
	enabled = false
	if is_inside_tree(): $Chart.send_event("cancel")
	for enemy in enemies:
		if is_instance_valid(enemy):
			enemy.target = null
			enemy.velocity = Vector3.ZERO
func _physics_process(delta: float) -> void:
	if not enabled or introduction == 0 or state() not in ["WaitingBurst", "Introducing", "Fighting"]: return
	if not player.is_alive(): return
	_clock -= delta
	if _clock > 0.0 or _pending >= enemy_scenes.size(): return
	if state() == "WaitingBurst":
		$Chart.send_event("introduce")
		_burst_vent()
		return
	spawn_blocked = not _spawn(_pending, true)
	if spawn_blocked:
		_clock = 0.1
		return
	_pending += 1
	_clock = spawn_interval
	if state() == "Introducing": $Chart.send_event("fight")
