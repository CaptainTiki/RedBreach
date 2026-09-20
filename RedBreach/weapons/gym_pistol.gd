extends Node3D
## Gym prototype. Consolidation into per-weapon resources is deferred in FR-001.
signal shot_fired(hit_target: bool)

@export var damage: float = 25.0
@export var shot_range: float = 50.0
@export var shots_per_second: float = 4.0
@export var magazine_capacity: int = 12
@export var reserve_capacity: int = 60
@export var reload_seconds: float = 1.4
@export var ads_fov: float = 70.0
@export var ads_seconds: float = 0.18
@export var ads_move_multiplier: float = 0.6
@export var hip_position := Vector3(0.24, -0.22, -0.48)
@export var ads_position := Vector3(0, -0.105, -0.4)
@export var kick_degrees: float = 1.2
@export var drift_degrees: float = 0.35
@export var ads_recoil_multiplier: float = 0.5
@export var audio_enabled: bool = true

@onready var camera: Camera3D = get_parent()
@onready var player: CharacterBody3D = camera.get_parent()
var magazine: int = 12
var reserve: int = 60
var shot_count: int = 0
var dry_fire_count: int = 0
var last_hit: Dictionary = {}
var camera_kick := Vector2.ZERO
var aim_drift := Vector2.ZERO
var ads_blend: float = 0.0
var _base_fov: float = 80.0
var _cooldown: float = 0.0
var _flash_time: float = 0.0
var _hit_time: float = 0.0
var _dry_time: float = 0.0
var _weapon_kick: float = 0.0
var _reload_blend: float = 0.0
var _rng := RandomNumberGenerator.new()

func _enter_tree() -> void:
	if not Engine.is_editor_hint() and not EngineDebugger.is_active():
		$HandlingChart.track_in_editor = false
		$AimChart.track_in_editor = false

func _ready() -> void:
	_base_fov = camera.fov
	magazine = magazine_capacity
	reserve = reserve_capacity
	_rng.randomize()
	$Pose.position = hip_position
	$Pose/Recoil/MuzzleFlash.hide()
	$HUD/HitMarker.hide()
	_refresh_hud()

func is_ads() -> bool:
	return $AimChart/Aim/ADS.active

func is_reloading() -> bool:
	return $HandlingChart/Handling/Reloading.active

func update_controls(controls_active: bool) -> void:
	var aiming: bool = controls_active and player.is_alive() and Input.is_action_pressed("gym_aim") and not is_reloading()
	if aiming != is_ads():
		$AimChart.send_event("aim" if aiming else "hip")

func aim_offset() -> Vector2:
	return camera_kick + aim_drift

func fire() -> bool:
	# One call per input press: holding the mouse does not repeat shots.
	if not player.is_alive() or not $HandlingChart/Handling/Ready.active or _cooldown > 0.0001:
		return false
	_cooldown = 1.0 / maxf(shots_per_second, 0.1)
	if magazine <= 0:
		dry_fire_count += 1
		_dry_time = 0.6
		_play_sound($DrySound)
		_refresh_hud()
		return false
	magazine -= 1
	shot_count += 1
	last_hit = trace_shot()
	var hit_target := false
	if not last_hit.is_empty() and last_hit.collider.has_method("receive_shot"):
		hit_target = last_hit.collider.receive_shot(damage, last_hit.position, last_hit.normal, -camera.global_basis.z)
	elif not last_hit.is_empty() and last_hit.collider.has_method("register_hit"):
		hit_target = last_hit.collider.register_hit(damage)
	if not last_hit.is_empty() and not last_hit.collider.has_method("receive_shot"):
		get_tree().call_group("combat_effects", "spawn_impact", last_hit.position, last_hit.normal)
	if hit_target:
		player.hit_count += 1
		_hit_time = 0.12
	var strength := ads_recoil_multiplier if is_ads() else 1.0
	camera_kick += Vector2(deg_to_rad(kick_degrees), deg_to_rad(_rng.randf_range(-0.22, 0.22))) * strength
	aim_drift += Vector2(deg_to_rad(drift_degrees), deg_to_rad(_rng.randf_range(-0.12, 0.12))) * strength
	aim_drift = aim_drift.limit_length(deg_to_rad(6.0))
	_weapon_kick = strength
	_flash_time = 0.045
	player._update_camera_aim()
	_play_sound($ShotSound)
	_refresh_hud()
	shot_fired.emit(hit_target)
	return true

func _ray(start: Vector3, end: Vector3) -> Dictionary:
	return get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start, end, 1, [player.get_rid()]))

func trace_shot() -> Dictionary:
	var origin := camera.global_position
	var end := origin - camera.global_basis.z * shot_range
	var sight_hit := _ray(origin, end)
	if not sight_hit.is_empty():
		end = sight_hit.position
	var muzzle: Vector3 = $Pose/Recoil/Muzzle.global_position
	# A visible target is not shootable if a nearby solid blocks the muzzle.
	var near_hit := _ray(origin, muzzle)
	if not near_hit.is_empty():
		return near_hit
	var muzzle_hit := _ray(muzzle, end + (end - muzzle).normalized() * 0.01)
	return muzzle_hit if not muzzle_hit.is_empty() else sight_hit

func request_reload() -> bool:
	if not player.is_alive() or not $HandlingChart/Handling/Ready.active or magazine >= magazine_capacity or reserve <= 0:
		return false
	$HandlingChart.send_event("reload")
	return true

func _on_reload_entered() -> void:
	$AimChart.send_event("hip")
	$ReloadTimer.start(reload_seconds)
	_play_sound($ReloadSound)
	_refresh_hud()

func _on_reload_timeout() -> void:
	if not is_reloading():
		return
	var amount := mini(magazine_capacity - magazine, reserve)
	magazine += amount
	reserve -= amount
	$HandlingChart.send_event("ready")
	_refresh_hud()

func cancel_handling() -> void:
	$ReloadTimer.stop()
	$HandlingChart.send_event("ready")
	$AimChart.send_event("hip")
	camera_kick = Vector2.ZERO
	aim_drift = Vector2.ZERO
	ads_blend = 0.0
	_reload_blend = 0.0
	_weapon_kick = 0.0
	_flash_time = 0.0
	_hit_time = 0.0
	_dry_time = 0.0
	_cooldown = 0.0
	camera.fov = _base_fov
	$Pose.position = hip_position
	$Pose.rotation = Vector3.ZERO
	$Pose/Recoil.position = Vector3.ZERO
	$Pose/Recoil.rotation = Vector3.ZERO
	$Pose/Recoil/Slide.position.z = -0.105
	$Pose/Recoil/MuzzleFlash.hide()
	$HUD/HitMarker.hide()
	_refresh_hud()

func add_ammo(amount: int) -> bool:
	if amount <= 0 or reserve >= reserve_capacity:
		return false
	reserve = mini(reserve_capacity, reserve + amount)
	_refresh_hud()
	return true

func reset_weapon() -> void:
	cancel_handling()
	magazine = magazine_capacity
	reserve = reserve_capacity
	shot_count = 0
	dry_fire_count = 0
	last_hit = {}
	_refresh_hud()

func _physics_process(delta: float) -> void:
	_cooldown = maxf(0.0, _cooldown - delta)
	_flash_time = maxf(0.0, _flash_time - delta)
	_hit_time = maxf(0.0, _hit_time - delta)
	_dry_time = maxf(0.0, _dry_time - delta)
	_refresh_hud()

func _process(delta: float) -> void:
	ads_blend = move_toward(ads_blend, 1.0 if is_ads() else 0.0, delta / maxf(ads_seconds, 0.01))
	var eased := smoothstep(0.0, 1.0, ads_blend)
	camera.fov = lerpf(_base_fov, ads_fov, eased)
	_reload_blend = lerpf(_reload_blend, 1.0 if is_reloading() else 0.0, 1.0 - exp(-14.0 * delta))
	$Pose.position = hip_position.lerp(ads_position, eased) + Vector3(0, -0.16, 0.06) * _reload_blend
	$Pose.rotation = Vector3(-0.35, 0, -0.5) * _reload_blend
	camera_kick *= exp(-18.0 * delta)
	aim_drift *= exp(-4.0 * delta)
	_weapon_kick *= exp(-20.0 * delta)
	$Pose/Recoil.position.z = 0.045 * _weapon_kick
	$Pose/Recoil.rotation.x = deg_to_rad(5.0) * _weapon_kick
	$Pose/Recoil/Slide.position.z = -0.105 + 0.035 * _weapon_kick
	$Pose/Recoil/MuzzleFlash.visible = _flash_time > 0.0
	$HUD/HitMarker.visible = _hit_time > 0.0
	# The iron sights become the reticle once the ADS transition has settled.
	player.get_node("HUD/Crosshair").visible = player.is_alive() and ads_blend < 0.95

func _refresh_hud() -> void:
	var handling := "RELOADING" if is_reloading() else ("ADS" if is_ads() else "HIP FIRE")
	if _dry_time > 0.0:
		handling = "EMPTY / PRESS R" if reserve > 0 else "NO AMMO / BACKSPACE RESET"
	$HUD/Ammo.text = "PISTOL  %02d / %02d\n%s" % [magazine, reserve, handling]

func _play_sound(sound: AudioStreamPlayer) -> void:
	if audio_enabled and DisplayServer.get_name() != "headless":
		sound.play()
