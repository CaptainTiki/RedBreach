extends CharacterBody3D
signal died
signal alerted
signal damaged(amount: float)
@export var max_health: float = 150.0
@export var dies_to_any_hit: bool = false
@export var display_name: String = "BUG"
@export var visual_scale: float = 1.0
@export var sight_height: float = 0.7
@export var attack_start_distance: float = 3.0
@export var attack_reach: float = 1.45
@export var move_speed: float = 3.3
@export var attack_damage: float = 20.0
@export var windup_seconds: float = 0.55
@export var lunge_speed: float = 10.0
@export var lunge_seconds: float = 0.25
@export var recovery_seconds: float = 0.85
@export var audio_enabled: bool = true
var health: float = 150.0
var target: CharacterBody3D
var _spawn: Transform3D
var _clock: float = 0.0
var _path_clock: float = 0.0
var _walk_phase: float = 0.0
var _hit_flash: float = 0.0
var _attack_spent := false
var _lunge_direction := Vector3.ZERO

func _enter_tree() -> void:
	if not EngineDebugger.is_active():
		$Brain.track_in_editor = false

func _ready() -> void:
	_spawn = global_transform
	$Visual.scale = Vector3.ONE * visual_scale
	health = max_health
	$Readout.text = display_name + " / DORMANT"

func state() -> String:
	for node in $Brain/Behavior.get_children():
		if node.get("active") == true:
			return node.name
	return ""

func activate(player: CharacterBody3D) -> bool:
	if state() != "Dormant" or not player.is_alive():
		return false
	target = player
	$Agent.target_position = target.global_position
	_path_clock = 0.0
	$Brain.send_event("alert")
	alerted.emit()
	return true

func can_see_target() -> bool:
	if not is_instance_valid(target) or not target.is_alive():
		return false
	var start := global_position + Vector3.UP * sight_height
	var finish := target.global_position + Vector3.UP * 0.65
	var hit := get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start, finish, 1, [get_rid()]))
	return not hit.is_empty() and hit.collider == target

func sense_waiting_target() -> void:
	if state() == "Dormant" and is_instance_valid(target) and target.is_alive():
		if global_position.distance_to(target.global_position) <= 18.0 and can_see_target(): activate(target)

func receive_shot(damage: float, point: Vector3, normal: Vector3, direction: Vector3) -> bool:
	if health <= 0.0 or damage <= 0.0: return false
	if state() == "Dormant":
		if not is_instance_valid(target) or not activate(target): return false
	var previous_health := health
	health = 0.0 if dies_to_any_hit else maxf(0.0, health - damage)
	damaged.emit(previous_health - health)
	_hit_flash = 0.13
	var excluded: Array[RID] = [get_rid()]
	if is_instance_valid(target):
		excluded.append(target.get_rid())
	get_tree().call_group("combat_effects", "spawn_bug_hit", point, normal, direction, excluded, health <= 0.0)
	if audio_enabled and DisplayServer.get_name() != "headless":
		$HitSound.play()
	if health <= 0.0:
		$Brain.send_event("die")
	return true

func register_hit(damage: float = 25.0) -> bool:
	return receive_shot(damage, global_position + Vector3.UP * sight_height, Vector3.UP, Vector3.DOWN)

func reset_bug() -> void:
	health = max_health
	target = null
	velocity = Vector3.ZERO
	_clock = 0.0
	_hit_flash = 0.0
	_attack_spent = false
	$Brain.send_event("reset")
	global_transform = _spawn
	$Visual.scale = Vector3.ONE * visual_scale
	$Visual.rotation = Vector3.ZERO
	collision_layer = 1
	$CollisionShape3D.set_deferred("disabled", false)
	$Readout.text = display_name + " / DORMANT"

func _on_windup_entered() -> void:
	_clock = windup_seconds
	velocity = Vector3.ZERO
	_lunge_direction = (target.global_position - global_position).normalized()
	_lunge_direction.y = 0.0
	_lunge_direction = _lunge_direction.normalized()
	rotation.y = atan2(-_lunge_direction.x, -_lunge_direction.z)
	if audio_enabled and DisplayServer.get_name() != "headless":
		$AttackSound.play()

func _on_lunge_entered() -> void:
	_clock = lunge_seconds
	_attack_spent = false

func _on_recover_entered() -> void:
	_clock = recovery_seconds
	velocity = Vector3.ZERO

func _on_dead_entered() -> void:
	$Visual/Warning.hide()
	velocity = Vector3.ZERO
	collision_layer = 0
	$CollisionShape3D.set_deferred("disabled", true)
	$Visual.scale = Vector3(visual_scale, visual_scale * 0.25, visual_scale)
	$Visual.rotation.z = 0.2
	$Readout.text = display_name + " / DOWN"
	died.emit()

func _physics_process(delta: float) -> void:
	sense_waiting_target()
	var current := state()
	if current == "Dead" or current == "Dormant":
		return
	if not is_instance_valid(target) or not target.is_alive():
		velocity = Vector3.ZERO
		return
	_clock -= delta
	_path_clock -= delta
	velocity.x = 0.0
	velocity.z = 0.0
	if current == "Hunt":
		if can_see_target() and global_position.distance_to(target.global_position) < attack_start_distance:
			$Brain.send_event("windup")
		else:
			if NavigationServer3D.map_get_iteration_id($Agent.get_navigation_map()) > 0:
				if _path_clock <= 0.0:
					$Agent.target_position = target.global_position
					_path_clock = 0.2
				var next: Vector3 = $Agent.get_next_path_position()
				var direction := (next - global_position)
				direction.y = 0.0
				if direction.length() > 0.08:
					direction = direction.normalized()
					velocity.x = direction.x * move_speed
					velocity.z = direction.z * move_speed
					rotation.y = lerp_angle(rotation.y, atan2(-direction.x, -direction.z), minf(1.0, delta * 8.0))
	elif current == "Windup" and _clock <= 0.0:
		$Brain.send_event("lunge")
	elif current == "Lunge":
		velocity.x = _lunge_direction.x * lunge_speed
		velocity.z = _lunge_direction.z * lunge_speed
		if not _attack_spent and global_position.distance_to(target.global_position) < attack_reach and can_see_target():
			_attack_spent = true
			target.get_node("Health").take_damage(attack_damage)
		if _clock <= 0.0:
			$Brain.send_event("recover")
	elif current == "Recover" and _clock <= 0.0:
		$Brain.send_event("hunt")
	velocity.y = 0.0 if is_on_floor() else velocity.y - 16.0 * delta
	move_and_slide()

func _process(delta: float) -> void:
	_hit_flash = maxf(0.0, _hit_flash - delta)
	var current := state()
	if current == "Dead":
		return
	_walk_phase += delta * (14.0 if velocity.length() > 0.5 else 2.0)
	$Visual.position.y = sin(_walk_phase) * 0.025 * visual_scale
	for i in $Visual/Legs.get_child_count():
		var leg: Node3D = $Visual/Legs.get_child(i)
		leg.rotation.z = sin(_walk_phase + float(i) * PI) * (0.16 if velocity.length() > 0.5 else 0.035)
	$Visual/Carapace.scale = Vector3.ONE * (1.1 if _hit_flash > 0.0 else 1.0)
	$Visual/Warning.visible = current == "Windup"
	$Readout.text = "LUNGE!" if current == "Windup" else ("%s / %d HP" % [display_name, ceili(health)] if current != "Dormant" else display_name + " / DORMANT")
