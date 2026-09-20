extends "res://combat/gym_bug.gd"
## Shares health, navigation, hit/death effects and reset foundations with the melee bug.
const SPIT = preload("res://combat/spit_projectile.tscn")
@export var spit_range: float = 15.0
@export var spit_speed: float = 35.0
@export var mouth_damage_multiplier: float = 3.0
var mouth_open: float = 0.0
var spit_count: int = 0
var weak_hit_count: int = 0
var _weak_feedback: float = 0.0

func _ready() -> void:
	super._ready()
	_update_mouth()
	$Readout.text = "SPITTER / DORMANT"

func mouth_is_exposed() -> bool:
	return health > 0.0 and visible and state() in ["Windup", "Spit"] and mouth_open > 0.95

func receive_mouth_shot(damage: float, point: Vector3, normal: Vector3, direction: Vector3) -> bool:
	# Only the visibly open, front-facing throat earns bonus damage.
	var weak := mouth_is_exposed() and direction.dot(-global_basis.z) < -0.3
	var accepted := receive_shot(damage * (mouth_damage_multiplier if weak else 1.0), point, normal, direction)
	if accepted and weak:
		weak_hit_count += 1
		_weak_feedback = 0.3
	return accepted

func _face_target() -> void:
	var direction: Vector3 = target.global_position - global_position
	rotation.y = atan2(-direction.x, -direction.z)

func _target_point() -> Vector3:
	return target.get_node("CollisionShape3D").global_position

func can_see_target() -> bool:
	if not is_instance_valid(target) or not target.is_alive():
		return false
	var query := PhysicsRayQueryParameters3D.create(global_position + Vector3.UP * 1.05, _target_point(), 1, [get_rid()])
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	return not hit.is_empty() and hit.collider == target

func _on_windup_entered() -> void:
	_clock = windup_seconds
	velocity = Vector3.ZERO
	mouth_open = 0.0
	_face_target()
	if audio_enabled and DisplayServer.get_name() != "headless":
		$AttackSound.play()

func _on_spit_entered() -> void:
	_clock = 0.1
	mouth_open = 1.0
	_update_mouth()
	if not can_see_target():
		return
	_face_target()
	var origin: Vector3 = $Visual/Mouth/Muzzle.global_position
	var near_query := PhysicsRayQueryParameters3D.create(global_position + Vector3.UP * 1.05, origin, 1, [get_rid()])
	if not get_world_3d().direct_space_state.intersect_ray(near_query).is_empty():
		return
	var glob: CharacterBody3D = SPIT.instantiate()
	glob.speed = spit_speed
	glob.damage = attack_damage
	get_parent().add_child(glob)
	glob.global_position = origin
	glob.launch(self, _target_point() - origin)
	spit_count += 1
	if audio_enabled and DisplayServer.get_name() != "headless":
		$SpitSound.play()

func _on_recover_entered() -> void:
	super._on_recover_entered()
	mouth_open = 0.0
	_update_mouth()

func _on_dead_entered() -> void:
	mouth_open = 0.0
	$MouthHitArea.collision_layer = 0
	$BodyHitArea.collision_layer = 0
	_update_mouth()
	super._on_dead_entered()
	$Readout.text = "SPITTER / DOWN"

func reset_bug() -> void:
	super.reset_bug()
	spit_count = 0
	weak_hit_count = 0
	_weak_feedback = 0.0
	mouth_open = 0.0
	$MouthHitArea.collision_layer = 2
	$BodyHitArea.collision_layer = 2
	_update_mouth()
	$Readout.text = "SPITTER / DORMANT"

func _physics_process(delta: float) -> void:
	sense_waiting_target()
	var current := state()
	if current in ["Dead", "Dormant"]:
		return
	if not is_instance_valid(target) or not target.is_alive():
		velocity = Vector3.ZERO
		mouth_open = 0.0
		_update_mouth()
		return
	_clock -= delta
	_path_clock -= delta
	velocity.x = 0.0
	velocity.z = 0.0
	if current == "Hunt":
		if can_see_target() and global_position.distance_to(target.global_position) <= spit_range:
			$Brain.send_event("windup")
		elif NavigationServer3D.map_get_iteration_id($Agent.get_navigation_map()) > 0:
			if _path_clock <= 0.0:
				$Agent.target_position = target.global_position
				_path_clock = 0.2
			var next: Vector3 = $Agent.get_next_path_position()
			var direction := next - global_position
			direction.y = 0.0
			if direction.length() > 0.08:
				direction = direction.normalized()
				velocity.x = direction.x * move_speed
				velocity.z = direction.z * move_speed
				rotation.y = lerp_angle(rotation.y, atan2(-direction.x,-direction.z), minf(1.0,delta*6.0))
	elif current == "Windup":
		_face_target()
		mouth_open = minf(1.0, mouth_open + delta / 0.08)
		if _clock <= 0.0:
			$Brain.send_event("spit")
	elif current == "Spit" and _clock <= 0.0:
		$Brain.send_event("recover")
	elif current == "Recover" and _clock <= 0.0:
		$Brain.send_event("hunt")
	_update_mouth()
	velocity.y = 0.0 if is_on_floor() else velocity.y - 16.0 * delta
	move_and_slide()

func _update_mouth() -> void:
	# Physics hit areas stay outside the visual corpse transform; Jolt spheres cannot flatten.
	$MouthHitArea.global_transform = Transform3D(global_basis, $Visual/Mouth/Throat.global_position)
	$BodyHitArea.position.y = 0.925 + $Visual.position.y
	$Visual/Mouth/UpperJaw.position.y = 0.12 + mouth_open * 0.25
	$Visual/Mouth/LowerJaw.position.y = -0.12 - mouth_open * 0.25
	$Visual/Mouth/Throat.visible = mouth_open > 0.95 and health > 0.0
	$Visual/Mouth/Throat.scale.y = maxf(0.01, mouth_open * 0.75)

func _process(delta: float) -> void:
	_hit_flash = maxf(0.0, _hit_flash - delta)
	_weak_feedback = maxf(0.0, _weak_feedback - delta)
	if state() == "Dead":
		return
	_walk_phase += delta * (10.0 if velocity.length() > 0.5 else 1.5)
	# Physics updates keep the mouth hit area aligned with this small body motion.
	$Visual.position.y = sin(_walk_phase) * 0.02
	for i in $Visual/Legs.get_child_count():
		$Visual/Legs.get_child(i).rotation.z = sin(_walk_phase + float(i)*PI) * (0.12 if velocity.length() > 0.5 else 0.025)
	$Visual/Carapace.scale = Vector3.ONE * (1.08 if _hit_flash > 0.0 else 1.0)
	$Visual/Warning.hide()
	$Readout.modulate = Color(0.85,1,0.15) if mouth_is_exposed() or _weak_feedback > 0.0 else Color.WHITE
	$Readout.text = "SPITTER / DORMANT" if state() == "Dormant" else ("WEAK HIT / %d HP" % ceili(health) if _weak_feedback > 0.0 else "SPITTER / %d HP" % ceili(health))
