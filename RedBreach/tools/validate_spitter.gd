extends SceneTree
var gym: Node3D
var player: CharacterBody3D
var spitter: CharacterBody3D
var pistol: Node3D
var health: Node
var failures: Array[String] = []
var checks: int = 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ",label)
	if not ok: failures.append(label)
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func aim(point: Vector3) -> void:
	var direction: Vector3 = point - player.camera.global_position
	player.rotation.y = atan2(-direction.x,-direction.z)
	player._pitch = atan2(direction.y,Vector2(direction.x,direction.z).length())
	player.reset_camera_interpolation()
func fresh(player_point: Vector3 = Vector3(25,0.05,-3), enemy_point: Vector3 = Vector3(25,0.05,-16)) -> void:
	Input.action_release("gym_aim")
	player.test_direction = Vector2.ZERO
	player.reset_player()
	player.relocate(Transform3D(Basis.IDENTITY,player_point))
	spitter.global_position = enemy_point
	spitter.set_physics_process(true)
	gym.start_encounter(1)
	await ticks(2)
func wait_state(wanted: String, limit: int = 360) -> bool:
	for i in limit:
		if spitter.state() == wanted: return true
		await ticks(1)
	return false
func wait_spit(limit: int = 90) -> bool:
	for i in limit:
		if spitter.spit_count > 0: return true
		await ticks(1)
	return false
func mouth_point() -> Vector3:
	return spitter.get_node("MouthHitArea").global_position
func shot_mouth() -> bool:
	aim(mouth_point())
	return pistol.fire()
func run() -> void:
	gym = load("res://combat/combat_gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	spitter = gym.get_node("Spitter")
	pistol = player.pistol
	health = player.get_node("Health")
	player.control_override = true
	pistol.audio_enabled = false
	spitter.audio_enabled = false
	gym.get_node("Bug").audio_enabled = false
	await ticks(15)
	check(not spitter.visible and spitter.collision_layer == 0 and spitter.get_node("MouthHitArea").collision_layer == 0,"Unselected spitter is hidden and cannot block or receive shots")
	check(spitter.get_node("CollisionShape3D").shape.height > gym.get_node("Bug/CollisionShape3D").shape.height * 1.5,"Spitter is substantially larger than the melee bug")
	check(is_equal_approx(spitter.windup_seconds,0.5) and is_equal_approx(spitter.spit_speed,35.0),"Spitter has a half-second wind-up and fast 35 m/s spit")
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(26,0.05,-3.4)))
	await ticks(3)
	aim(gym.get_node("SpitterPanel").global_position)
	check(player.try_interact() and gym.active_enemy == spitter and gym.state() == "Fighting","Second E-use panel releases the spitter")
	check(spitter.visible and not gym.get_node("Bug").visible and gym.get_node("Bug").collision_layer == 0,"Selecting the spitter parks the melee bug; exactly one enemy fights")
	check(not gym.start_encounter() and not gym.start_encounter(1),"Neither panel can start a second enemy during a fight")
	# Start close enough for a ranged attack; verify timing before the projectile exists.
	await fresh()
	check(await wait_state("Windup"),"Spitter winds up at ranged distance")
	var remaining: float = spitter._clock
	await ticks(5)
	check(spitter.mouth_is_exposed() and spitter.get_node("Visual/Mouth/Throat").visible,"Jaws open and reveal the glowing weak point during charge")
	check(spitter.get_node("Visual/Mouth/UpperJaw").position.y > 0.3 and spitter.get_node("Visual/Mouth/LowerJaw").position.y < -0.3,"Upper and lower jaws visibly separate")
	var glow: StandardMaterial3D = spitter.get_node("Visual/Mouth/Throat").mesh.material
	check(glow.albedo_color.g >= 0.95 and glow.albedo_color.r > 0.7 and glow.albedo_color.b < 0.1,"Mouth is bright yellow-green")
	await ticks(18)
	check(spitter.spit_count == 0 and get_nodes_in_group("combat_projectiles").is_empty(),"No projectile is released early during wind-up")
	var waited: int = 23
	while spitter.spit_count == 0 and waited < 40:
		await ticks(1)
		waited += 1
	check(waited / 60.0 >= remaining - 0.025 and waited / 60.0 <= remaining + 0.035,"Projectile release occurs at approximately 0.5 seconds")
	check(get_nodes_in_group("combat_projectiles").size() == 1,"One charge releases exactly one glob")
	var glob: CharacterBody3D = get_nodes_in_group("combat_projectiles")[0]
	check(is_equal_approx(glob.velocity.length(),35.0),"Live projectile travels at 35 m/s")
	var committed: Vector3 = glob.velocity
	player.test_direction = Vector2(1,0)
	await ticks(4)
	check(is_instance_valid(glob) and glob.velocity.is_equal_approx(committed),"Spit does not home after release")
	player.test_direction = Vector2.ZERO
	# Two accurate shots fit inside the mouth-opening warning window.
	await fresh()
	await ticks(6)
	check(shot_mouth() and spitter.health == 75 and spitter.weak_hit_count == 1,"An actual pistol mouth hit deals triple damage: 75")
	await ticks(16)
	check(shot_mouth() and spitter.health == 0 and spitter.weak_hit_count == 2,"Two accurate pistol hits kill through the exposed mouth")
	check(spitter.spit_count == 0 and gym.state() == "Cleared","Fast weak-point kill interrupts the first spit")
	check(spitter.get_node("MouthHitArea").collision_layer == 0 and spitter.get_node("BodyHitArea").collision_layer == 0,"Death disables both spitter shot areas")
	check(gym.get_node("Effects").splats.size() >= 2,"Spitter death keeps green hit and death splatters")
	# A closed mouth and a back/side body shot do not get the bonus.
	await fresh()
	check(await wait_state("Recover"),"Spitter recovers after firing")
	spitter.set_physics_process(false)
	gym._clear_projectiles()
	check(not spitter.mouth_is_exposed() and not spitter.get_node("Visual/Mouth/Throat").visible,"Recovery closes the jaws and hides the weak point")
	check(shot_mouth() and spitter.health == 125 and spitter.weak_hit_count == 0,"Closed-mouth shot deals only normal 25 damage")
	await fresh()
	await ticks(6)
	spitter.set_physics_process(false)
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(25,0.05,-19)))
	await ticks(3)
	check(shot_mouth() and spitter.health == 125 and spitter.weak_hit_count == 0,"Rear shot hits the body before the exposed mouth")
	await fresh()
	await ticks(6)
	spitter.set_physics_process(false)
	aim(mouth_point() + Vector3.UP * 0.34)
	check(pistol.fire() and spitter.health == 125 and spitter.weak_hit_count == 0,"A shot above the glowing throat hits shell without a weak-point bonus")
	await fresh()
	spitter.set_physics_process(false)
	spitter.mouth_open = 0.0
	spitter._update_mouth()
	for i in 6:
		shot_mouth()
		await ticks(16)
	check(spitter.health == 0 and spitter.weak_hit_count == 0 and pistol.magazine == 6,"Six ordinary pistol hits kill the 150 HP spitter")
	# Cover blocks weak-point shots, wind-up starts and muzzle release.
	await fresh(Vector3(20,0.05,-8),Vector3(20,0.05,-14))
	spitter.set_physics_process(false)
	spitter.rotation.y = PI
	await ticks(2)
	check(not spitter.can_see_target(),"Tall cover blocks spitter detection")
	shot_mouth()
	check(spitter.health == 150,"Cover stops a shot before the mouth or body hit areas")
	spitter.get_node("Brain").send_event("windup")
	spitter.get_node("Brain").send_event("spit")
	check(spitter.spit_count == 0,"Spit release is cancelled when cover blocks the target")
	# Navigation clearance is baked for the larger body.
	await fresh(Vector3(20,0.05,-3),Vector3(20,0.05,-16))
	var lateral: float = 0.0
	for i in 300:
		await ticks(1)
		lateral = maxf(lateral,absf(spitter.position.x - 20.0))
		if spitter.state() == "Windup": break
	check(lateral > 2.5 and spitter.state() == "Windup","Larger spitter routes around cover to gain a firing line")
	# Fast pressure: stationary player gets hit, a late strafe can just evade it.
	await fresh()
	check(await wait_spit(),"Live ranged attack launches toward the player")
	spitter.set_physics_process(false)
	await ticks(28)
	check(health.health == 80,"Fast spit deals 20 damage to a stationary player")
	check(get_nodes_in_group("combat_projectiles").is_empty(),"Player impact consumes the projectile once")
	check(gym.get_node("Effects").splats.size() > 0,"Spit impact leaves visible green residue")
	await fresh()
	await wait_spit()
	spitter.set_physics_process(false)
	await ticks(8)
	player.test_direction = Vector2(1,0)
	await ticks(25)
	player.test_direction = Vector2.ZERO
	check(health.health == 100,"A committed sidestep shortly after release can dodge the fast glob")
	await fresh()
	await ticks(12)
	player.test_direction = Vector2(1,0)
	await wait_spit()
	var aimed_glob: CharacterBody3D = get_nodes_in_group("combat_projectiles")[0]
	var to_player: Vector3 = player.get_node("CollisionShape3D").global_position - aimed_glob.global_position
	check(aimed_glob.velocity.normalized().dot(to_player.normalized()) > 0.999,"Spitter tracks the player during charge and aims at the position at release")
	player.test_direction = Vector2.ZERO
	# Swept collision catches a thin wall even when movement per tick exceeds its thickness.
	await fresh()
	spitter.set_physics_process(false)
	var blocker := StaticBody3D.new()
	var shape_node := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = Vector3(3,3,0.04)
	shape_node.shape = shape
	blocker.add_child(shape_node)
	gym.add_child(blocker)
	blocker.position = Vector3(25,1.5,-8)
	var test_glob: CharacterBody3D = load("res://combat/spit_projectile.tscn").instantiate()
	gym.add_child(test_glob)
	test_glob.position = Vector3(25,0.9,-10)
	test_glob.launch(spitter,Vector3.BACK)
	await ticks(12)
	check(not is_instance_valid(test_glob) and health.health == 100,"Swept fast glob hits a 4 cm wall instead of tunnelling through")
	blocker.queue_free()
	await fresh()
	await wait_spit()
	player.reset_player()
	await ticks(3)
	check(get_nodes_in_group("combat_projectiles").is_empty() and not spitter.visible and spitter.state() == "Dormant","Reset removes in-flight acid and restores dormant selection")
	check(spitter.health == 150 and spitter.weak_hit_count == 0 and spitter.mouth_open == 0,"Reset restores spitter health, mouth pose and counters")
	await fresh()
	await wait_spit()
	health.take_damage(100)
	await ticks(3)
	check(gym.state() == "Failed" and get_nodes_in_group("combat_projectiles").is_empty() and not spitter.mouth_is_exposed(),"Player death cancels outstanding acid and closes the mouth")
	await fresh()
	await wait_spit()
	spitter.receive_shot(150,spitter.position+Vector3.UP,Vector3.UP,Vector3.DOWN)
	await ticks(2)
	check(gym.state() == "Cleared" and get_nodes_in_group("combat_projectiles").is_empty(),"Killing the spitter clears outstanding acid for the completed test")
	player.reset_player()
	await ticks(3)
	check(gym.get_node("Bug").visible and not spitter.visible and gym.state() == "Ready","Original melee encounter remains the reset default")
	# Ordinary overlapping triggers cannot intercept bullets after adding shot-only areas.
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(-4,0.05,0)))
	var trigger := Area3D.new()
	var trigger_shape := CollisionShape3D.new()
	var trigger_box := BoxShape3D.new()
	trigger_box.size = Vector3(3,3,0.5)
	trigger_shape.shape = trigger_box
	trigger.add_child(trigger_shape)
	gym.add_child(trigger)
	trigger.position = Vector3(-4,1.5,-3)
	await ticks(3)
	aim(gym.get_node("Targets/Target1").global_position)
	check(pistol.fire() and gym.get_node("Targets/Target1").health == 75,"Ordinary layer-1 Area3D triggers do not block weapon rays")
	trigger.queue_free()
	await ticks(2)
	# Misses have a finite lifetime, and leaving the gym clears active projectiles.
	var expiring: CharacterBody3D = load("res://combat/spit_projectile.tscn").instantiate()
	expiring.lifetime = 0.1
	gym.add_child(expiring)
	expiring.position = Vector3(25,5,-5)
	expiring.launch(spitter,Vector3.UP)
	await ticks(8)
	check(not is_instance_valid(expiring),"Missed globs expire instead of accumulating outside the arena")
	await fresh()
	await wait_spit()
	current_scene = gym
	var selection := InputEventKey.new()
	selection.physical_keycode = KEY_F1
	selection.pressed = true
	player._unhandled_input(selection)
	await ticks(8)
	check(current_scene.has_node("MovementAnnex") and get_nodes_in_group("combat_projectiles").is_empty(),"Changing gyms removes all in-flight acid")
	print("SPITTER_QA: ",checks-failures.size(),"/",checks," passed")
	quit(0 if failures.is_empty() else 1)
