extends CharacterBody3D
## Temporary scale-test controller. Game movement and weapon behavior are still open.
signal jumped(origin: Vector3)
signal relocated

@export var gym_title: String = "GYM 01 + ANNEX"

@export var crouch_height: float = 1.1
@export var crouch_eye_height: float = 0.95
@export var crouch_speed: float = 2.5
@export_range(1.0, 30.0) var crouch_camera_smoothing: float = 12.0

@export var walk_speed: float = 5.0
@export var sprint_speed: float = 8.0
@export var jump_speed: float = 5.5
@export var gravity: float = 16.0
@export var mouse_sensitivity: float = 0.002
@export var step_height: float = 0.3
@export_range(0.5, 4.0) var interaction_distance: float = 2.0
## Rate at which the eye catches up after a discrete stair rise/drop (per second).
@export_range(1.0, 30.0) var stair_camera_smoothing: float = 14.0

@onready var camera: Camera3D = $Camera3D
@onready var status: Label = $HUD/Status
@onready var pistol = $Camera3D/Pistol
var spawn_transform: Transform3D
var hit_count: int = 0
var control_override: bool = false
var test_direction := Vector2.ZERO
var _interaction_requested: bool = false
var _snapped_to_step: bool = false
var _eye_height: float = 1.65
var _previous_eye_height: float = 1.65
var _target_eye_height: float = 1.65
var _standing_eye_height: float = 1.65
var _standing_shape: CapsuleShape3D
var _standing_visual_height: float = 2.0
var _pitch: float = 0.0
var _previous_position := Vector3.ZERO
var _current_position := Vector3.ZERO
var _previous_eye_offset: float = 0.0
var _eye_offset: float = 0.0

func _enter_tree() -> void:
	if not Engine.is_editor_hint() and not EngineDebugger.is_active():
		$PostureChart.track_in_editor = false

func _ready() -> void:
	# Per-player copies: changing stance must never resize another instance.
	$CollisionShape3D.shape = $CollisionShape3D.shape.duplicate()
	_standing_shape = $CollisionShape3D.shape.duplicate()
	$MeshInstance3D.mesh = $MeshInstance3D.mesh.duplicate()
	_standing_visual_height = $MeshInstance3D.mesh.height
	spawn_transform = global_transform
	_eye_height = camera.position.y
	_standing_eye_height = _eye_height
	_target_eye_height = _eye_height
	_pitch = camera.rotation.x
	# Use the camera's world transform so the parent cannot bypass smoothing.
	camera.top_level = true
	camera.physics_interpolation_mode = Node.PHYSICS_INTERPOLATION_MODE_OFF
	floor_constant_speed = true
	reset_camera_interpolation()
	$HUD/Build.text = "Build: " + str(ProjectSettings.get_setting("application/config/version", ""))
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func is_alive() -> bool:
	return $Health.is_alive()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_F1 or event.physical_keycode == KEY_F2:
			get_tree().call_deferred("change_scene_to_file", "res://gym/gym.tscn" if event.physical_keycode == KEY_F1 else "res://combat/combat_gym.tscn")
			return
	if not is_alive():
		if event.is_action_pressed("gym_reset"):
			reset_player()
		elif event.is_action_pressed("gym_release_mouse"):
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		return
	if event.is_action_pressed("gym_interact") and (control_override or Input.mouse_mode == Input.MOUSE_MODE_CAPTURED):
		_interaction_requested = true
	if event.is_action_pressed("gym_release_mouse"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		pistol.update_controls(false)
	if event.is_action_pressed("gym_reload") and (control_override or Input.mouse_mode == Input.MOUSE_MODE_CAPTURED):
		pistol.request_reload()
	if event.is_action_pressed("gym_reset"):
		reset_player()
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sensitivity)
		_pitch = clampf(_pitch - event.relative.y * mouse_sensitivity, -1.45, 1.45)
		_update_camera_aim()
	if event.is_action_pressed("gym_fire"):
		if not control_override and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		else:
			pistol.fire()

func _update_camera_aim() -> void:
	# Keep mouse look immediate; only movement is interpolated.
	var recoil: Vector2 = pistol.aim_offset()
	camera.global_basis = global_basis * Basis(Vector3.UP, recoil.y) * Basis(Vector3.RIGHT, clampf(_pitch + recoil.x, -1.5, 1.5))

func _process(_delta: float) -> void:
	var fraction := Engine.get_physics_interpolation_fraction()
	camera.global_position = _previous_position.lerp(_current_position, fraction)
	camera.global_position.y += lerpf(_previous_eye_height, _eye_height, fraction) + lerpf(_previous_eye_offset, _eye_offset, fraction)
	_update_camera_aim()

func reset_camera_interpolation() -> void:
	_previous_eye_height = _eye_height
	_previous_position = global_position
	_current_position = global_position
	_previous_eye_offset = 0.0
	_eye_offset = 0.0
	camera.global_position = global_position + Vector3.UP * _eye_height
	_update_camera_aim()

func reset_player() -> void:
	$Health.reset_health()
	relocate(spawn_transform)
	pistol.reset_weapon()
	hit_count = 0
	get_tree().call_group("gym_targets", "reset_target")
	get_tree().call_group("combat_gym", "reset_encounter")

func relocate(destination: Transform3D) -> void:
	# All recovery destinations are authored with full standing clearance.
	_interaction_requested = false
	_snapped_to_step = false
	pistol.cancel_handling()
	global_transform = destination
	velocity = Vector3.ZERO
	_pitch = 0.0
	$PostureChart.send_event("stand_requested")
	_eye_height = _standing_eye_height
	_target_eye_height = _standing_eye_height
	reset_camera_interpolation()
	relocated.emit()

func is_crouching() -> bool:
	return $PostureChart/Posture/Crouched.active

func movement_mode() -> String:
	if pistol.is_ads():
		return "CROUCH ADS" if is_crouching() else "ADS"
	if is_crouching():
		return "CROUCH"
	return "SPRINT" if Input.is_action_pressed("gym_sprint") else "WALK"

func can_stand() -> bool:
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = _standing_shape
	query.transform = global_transform.translated(Vector3.UP * (_standing_shape.height * 0.5 + safe_margin * 2.0))
	query.collision_mask = collision_mask
	query.exclude = [get_rid()]
	return get_world_3d().direct_space_state.intersect_shape(query, 1).is_empty()

func _on_standing_entered() -> void:
	_set_posture_shape(_standing_shape.height, _standing_eye_height, _standing_visual_height)

func _on_crouched_entered() -> void:
	_set_posture_shape(crouch_height, crouch_eye_height, crouch_height)

func _set_posture_shape(height: float, eye: float, visual_height: float) -> void:
	$CollisionShape3D.shape.height = height
	$CollisionShape3D.position.y = height * 0.5
	$MeshInstance3D.mesh.height = visual_height
	$MeshInstance3D.position.y = visual_height * 0.5
	_target_eye_height = eye

func _update_posture(grounded: bool, jump_requested: bool, controls_active: bool) -> void:
	if not grounded or not controls_active:
		return
	if is_crouching():
		if (not Input.is_action_pressed("gym_crouch") or jump_requested) and can_stand():
			$PostureChart.send_event("stand_requested")
	elif Input.is_action_pressed("gym_crouch") and not jump_requested:
		$PostureChart.send_event("crouch_requested")

func fire_probe() -> bool:
	var start := camera.global_position
	var end := start - camera.global_basis.z * 50.0
	var query := PhysicsRayQueryParameters3D.create(start, end, 1, [get_rid()])
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if not hit.is_empty() and hit.collider.has_method("register_hit"):
		hit.collider.register_hit()
		hit_count += 1
		return true
	return false

func interaction_target() -> Node:
	var start := camera.global_position
	var query := PhysicsRayQueryParameters3D.create(start, start - camera.global_basis.z * interaction_distance, 1, [get_rid()])
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if not hit.is_empty() and hit.collider.has_method("interact") and hit.collider.has_method("get_interaction_prompt"):
		return hit.collider
	return null

func try_interact() -> bool:
	if not is_alive():
		return false
	var target := interaction_target()
	return target.interact() if target != null else false

func _update_interaction() -> void:
	if _interaction_requested:
		try_interact()
		_interaction_requested = false
	var target: Node = interaction_target() if is_alive() and (control_override or Input.mouse_mode == Input.MOUSE_MODE_CAPTURED) else null
	$HUD/Interaction.text = target.get_interaction_prompt() if target != null else ""

func _physics_process(delta: float) -> void:
	_previous_eye_height = _eye_height
	_previous_position = _current_position
	_previous_eye_offset = _eye_offset
	var before := global_position
	var was_grounded := is_grounded()
	var controls_active := is_alive() and (control_override or Input.mouse_mode == Input.MOUSE_MODE_CAPTURED)
	var jump_requested := Input.is_action_just_pressed("gym_jump") and controls_active
	_update_posture(was_grounded, jump_requested, controls_active)
	pistol.update_controls(controls_active)
	var axis := test_direction if control_override else Input.get_vector("gym_left", "gym_right", "gym_forward", "gym_back")
	if not controls_active:
		axis = Vector2.ZERO
	var speed := crouch_speed if is_crouching() else (sprint_speed if Input.is_action_pressed("gym_sprint") else walk_speed)
	if pistol.is_ads():
		speed = (crouch_speed if is_crouching() else walk_speed) * pistol.ads_move_multiplier
	var direction := global_basis * Vector3(axis.x, 0.0, axis.y)
	velocity.x = direction.x * speed
	velocity.z = direction.z * speed
	if not was_grounded:
		velocity.y -= gravity * delta
	elif jump_requested and not is_crouching():
		velocity.y = jump_speed
		jumped.emit(global_position)
	else:
		velocity.y = 0.0
	var jumping := velocity.y > 0.0
	var step_rise := _try_step(Vector3(velocity.x, 0.0, velocity.z) * delta)
	move_and_slide()
	_snapped_to_step = false
	if was_grounded and not jumping and step_rise == 0.0:
		_snap_down_step()
	# Counteract only discrete stair movement. Jump arcs and slopes stay responsive.
	_eye_offset -= step_rise
	var height_change := global_position.y - before.y
	if was_grounded and is_grounded() and height_change < -0.06:
		_eye_offset -= height_change
	_eye_offset = clampf(_eye_offset, -step_height * 2.0, step_height)
	_eye_offset *= exp(-stair_camera_smoothing * delta)
	_eye_height = lerpf(_eye_height, _target_eye_height, 1.0 - exp(-crouch_camera_smoothing * delta))
	_current_position = global_position
	if global_position.y < -10.0:
		reset_player()
	_update_interaction()
	status.text = "%s / %s / Hits: %d\nWASD move   Shift sprint   Ctrl crouch   Space jump\nLMB fire   RMB aim   R reload   E use\nEsc release mouse   Backspace reset\nF1 movement gym   F2 combat gym" % [gym_title, movement_mode(), hit_count]

func is_grounded() -> bool:
	# A capsule can touch a stair corner with a steep normal even though there is
	# a flat tread directly below. Count only a verified downward step as support.
	return is_on_floor() or _snapped_to_step

func _snap_down_step() -> void:
	if is_on_floor():
		return
	# Require a walkable tread within one step, so real ledges still cause a fall.
	var query := PhysicsRayQueryParameters3D.create(global_position + Vector3.UP * safe_margin,
		global_position - Vector3.UP * step_height, collision_mask, [get_rid()])
	var tread := get_world_3d().direct_space_state.intersect_ray(query)
	if tread.is_empty() or tread.normal.dot(Vector3.UP) < 0.99:
		return
	var collision := KinematicCollision3D.new()
	if not test_move(global_transform, Vector3.DOWN * step_height, collision):
		return
	var travel := collision.get_travel()
	if travel.y >= 0.0:
		return
	# Sweep the whole capsule to the contact, never teleport through the riser.
	global_position += travel
	velocity.y = 0.0
	apply_floor_snap()
	_snapped_to_step = true

func _try_step(motion: Vector3) -> float:
	floor_snap_length = 0.35
	if not is_grounded() or velocity.y > 0.0 or motion.length_squared() < 0.000001:
		return 0.0
	var obstacle := KinematicCollision3D.new()
	if not test_move(global_transform, motion, obstacle):
		return 0.0
	if obstacle.get_normal().dot(Vector3.UP) >= cos(floor_max_angle):
		return 0.0
	var lift := Vector3.UP * step_height
	if test_move(global_transform, lift):
		return 0.0
	var raised := global_transform.translated(lift)
	if test_move(raised, motion):
		return 0.0
	# A stair needs a nearly level tread. Slopes must use move_and_slide + snap,
	# otherwise this look-ahead probe repeatedly lifts the capsule off the ramp.
	var ahead := global_position + motion.normalized() * (0.3 + motion.length())
	var query := PhysicsRayQueryParameters3D.create(ahead + lift, ahead - Vector3.UP * 0.02, collision_mask, [get_rid()])
	var tread := get_world_3d().direct_space_state.intersect_ray(query)
	if tread.is_empty() or tread.normal.dot(Vector3.UP) < 0.99:
		return 0.0
	var rise: float = tread.position.y - global_position.y
	if rise > 0.01 and rise <= step_height:
		global_position.y += rise + 0.001
		# Do not snap back to the lower floor before moving onto the tread.
		floor_snap_length = 0.0
		return rise + 0.001
	return 0.0
