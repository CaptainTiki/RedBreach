extends SceneTree
var gym: Node3D
var player: CharacterBody3D
var bug: CharacterBody3D
var pistol: Node3D
var health: Node
var failures: Array[String] = []
var checks: int = 0
func _initialize() -> void:
	call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ", label)
	if not ok: failures.append(label)
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func place(point: Vector3) -> void:
	Input.action_release("gym_aim")
	player.test_direction = Vector2.ZERO
	player.relocate(Transform3D(Basis.IDENTITY, point))
	await ticks(3)
func aim(point: Vector3) -> void:
	var direction: Vector3 = point - player.camera.global_position
	player.rotation.y = atan2(-direction.x, -direction.z)
	player._pitch = atan2(direction.y, Vector2(direction.x, direction.z).length())
	player.reset_camera_interpolation()
func ray(a: Vector3, b: Vector3) -> Dictionary:
	return player.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(a,b,1,[player.get_rid()]))
func run() -> void:
	gym = load("res://combat/combat_gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	bug = gym.get_node("Bug")
	pistol = player.pistol
	health = player.get_node("Health")
	pistol.audio_enabled = false
	bug.audio_enabled = false
	player.control_override = true
	await ticks(20)
	check(gym.get_node("Geometry").find_children("*","CollisionShape3D",true,false).size() == 22, "Saved source map has 22 solid brushes")
	check(gym.get_node("Navigation").navigation_mesh.get_polygon_count() > 0, "Saved encounter navigation is baked")
	check(gym.state() == "Ready" and bug.state() == "Dormant" and player.is_alive(), "Encounter, bug and player start Ready / Dormant / Alive")
	for point in [Vector3(-4,0,0),Vector3(0,0,0),Vector3(4,0,0),Vector3(20,0,2),Vector3(20,0,-3),Vector3(4,0,7)]:
		var floor_hit := ray(point + Vector3.UP, point + Vector3.DOWN)
		check(not floor_hit.is_empty() and absf(floor_hit.position.y) < 0.01, "Continuous floor at " + str(point))
	check(not gym.start_encounter(), "Safe staging cannot release a bug or close the gate")
	for mode in [false, true]:
		for i in 3:
			var plate: Node3D = gym.get_node("Targets/Target%d" % (i+1))
			await place(Vector3(plate.position.x,0.05,0))
			pistol.reset_weapon()
			plate.reset_target()
			if mode: Input.action_press("gym_aim")
			await ticks(20)
			aim(plate.global_position)
			check(pistol.fire() and plate.health == 75, "%s hits %d m plate from its marked pad" % ["ADS" if mode else "Hip fire", (i+1)*10])
			Input.action_release("gym_aim")
	check(gym.get_node("Effects").droplets.size() > 0, "Plate impacts produce visible sparks")
	await place(Vector3(23,0.05,-0.8))
	check(not gym.start_encounter(), "Gate refuses to close on a player in its threshold")
	await place(Vector3(23,0.05,-3.4))
	aim(gym.get_node("StartPanel").global_position)
	check(player.try_interact() and gym.state() == "Fighting", "E-use ray starts the fight from inside the arena")
	await ticks(2)
	check(not gym.get_node("Gate/CollisionShape3D").disabled and bug.state() == "Hunt", "Release closes gate and alerts the bug")
	check(not gym.start_encounter() and gym.attempts == 1, "Repeated start cannot duplicate encounters")
	# Tall cover blocks both a shot and the attack line of sight.
	bug.set_physics_process(false)
	bug.global_position = Vector3(20,0.05,-13.3)
	await place(Vector3(20,0.05,-8.5))
	pistol.reset_weapon()
	aim(bug.global_position + Vector3.UP * 0.65)
	check(not bug.can_see_target(), "Tall cover blocks bug sightline")
	pistol.fire()
	check(bug.health == 100, "Tall cover blocks real pistol damage to the bug")
	# Path following must go around the obstacle, not stall or cut through it.
	gym.reset_encounter()
	await place(Vector3(20,0.05,-3))
	bug.set_physics_process(true)
	gym.start_encounter()
	var lateral: float = 0.0
	var saw_windup := false
	for i in 420:
		await ticks(1)
		lateral = maxf(lateral, absf(bug.position.x - 20.0))
		if bug.state() == "Windup":
			saw_windup = true
			break
	check(lateral > 2.5 and saw_windup, "Bug navigates around tall cover and reaches attack range")
	check(health.health == 100, "Approach and visible wind-up do not deal contact damage")
	var attack_axis: Vector3 = bug._lunge_direction
	var before_dodge: Vector3 = player.position
	await place(before_dodge + Vector3(attack_axis.z,0,-attack_axis.x) * 4.0)
	await ticks(55)
	check(health.health == 100, "Sidestepping the committed lunge avoids damage")
	# Stationary player can be damaged once per attack, then receives recovery time.
	gym.reset_encounter()
	await place(Vector3(25,0.05,-12))
	bug.global_position = Vector3(25,0.05,-14.6)
	gym.start_encounter()
	var saw_recover := false
	for i in 100:
		await ticks(1)
		if bug.state() == "Recover":
			saw_recover = true
			break
	check(saw_recover and health.health == 80, "One lunge deals 20 damage then enters recovery")
	bug.set_physics_process(false)
	var med := gym.get_node("Pickups/ArenaHealth")
	check(med.try_collect(player) and health.health == 100 and not med.available, "Health pickup heals up to the cap and consumes once")
	check(not med.try_collect(player), "Consumed pickup cannot be collected again")
	med.reset_pickup()
	check(not med.try_collect(player) and med.available, "Full-health player leaves a health pickup available")
	var ammo := gym.get_node("Pickups/ArenaAmmo")
	check(not ammo.try_collect(player) and ammo.available, "Full ammo leaves ammunition available")
	pistol.reserve = 50
	check(ammo.try_collect(player) and pistol.reserve == 60, "Ammunition pickup caps reserve at 60")
	# Kill by four actual aimed pistol shots, producing world-space blood and a corpse.
	gym.reset_encounter()
	await place(Vector3(25,0.05,-10))
	bug.global_position = Vector3(25,0.05,-16)
	gym.start_encounter()
	pistol.reset_weapon()
	await ticks(2) # Synchronize the relocated bug collider before firing.
	for i in 4:
		aim(bug.global_position + Vector3.UP * 0.7)
		check(pistol.fire() and bug.health == float(75-i*25), "Pistol shot %d damages the live bug" % (i+1))
		await ticks(16)
	check(bug.state() == "Dead" and gym.state() == "Cleared", "Fourth shot kills the bug and clears the encounter")
	check(bug.collision_layer == 0 and bug.get_node("CollisionShape3D").disabled, "Dead bug has no blocking collision")
	check(bug.get_node("Visual").scale.y < 0.3 and not bug.get_node("Visual/Warning").visible, "Death leaves a flattened corpse with no attack indicator")
	check(gym.get_node("Gate/CollisionShape3D").disabled, "Killing the bug reopens the gate")
	check(gym.get_node("Effects").splats.size() >= 4, "Hits and death leave persistent surface splatters")
	var count: int = gym.get_node("Effects").splats.size()
	check(not bug.register_hit(25) and gym.get_node("Effects").splats.size() == count, "Corpse hits cannot create repeated deaths or blood")
	# Death interrupts ADS and reload, rejects new fire, and Backspace restores everything.
	player.reset_player()
	await ticks(5)
	await place(Vector3(25,0.05,-12))
	gym.start_encounter()
	Input.action_press("gym_aim")
	await ticks(20)
	pistol.magazine = 1
	pistol.request_reload()
	check(health.take_damage(100) and not player.is_alive(), "Lethal damage kills the player")
	await ticks(2)
	check(health.get_node("LifeChart/Life/Dead").active and gym.state() == "Failed", "Life and encounter StateCharts enter Dead / Failed")
	check(not pistol.fire() and not pistol.request_reload() and not pistol.is_ads() and not pistol.is_reloading(), "Death cancels handling and prevents firing, reload and ADS")
	check(not med.try_collect(player) and not ammo.try_collect(player), "Dead players cannot collect supplies")
	var dead_position: Vector3 = player.position
	player.test_direction = Vector2(1,0)
	await ticks(15)
	check(player.position.distance_to(dead_position) < 0.01, "Death disables movement even with held input")
	var reset := InputEventKey.new()
	reset.physical_keycode = KEY_BACKSPACE
	reset.pressed = true
	player._unhandled_input(reset)
	Input.action_release("gym_aim")
	player.test_direction = Vector2.ZERO
	await ticks(5)
	check(health.health == 100 and health.get_node("LifeChart/Life/Alive").active, "Backspace restores health and Alive state")
	check(pistol.magazine == 12 and pistol.reserve == 60 and is_equal_approx(player.camera.fov,80.0), "Backspace restores ammo and normal camera handling")
	check(gym.state() == "Ready" and bug.state() == "Dormant" and bug.health == 100, "Backspace resets the fight and bug")
	check(gym.get_node("Effects").splats.is_empty() and gym.get_node("Effects").droplets.is_empty(), "Reset removes all persistent and transient effects")
	check(med.available and ammo.available and gym.get_node("Gate/CollisionShape3D").disabled, "Reset restores supplies and opens gate")
	check(player.position.distance_to(player.spawn_transform.origin) < 0.1, "Reset returns to the safe bay")
	# Collect using actual Area3D overlap, not only a direct helper call.
	health.take_damage(25)
	await place(med.global_position + Vector3.UP * 0.05)
	await ticks(3)
	check(health.health == 100 and not med.available, "Walking onto a pickup applies it through Area3D detection")
	# A wall introduced after wind-up still prevents the committed attack.
	player.reset_player()
	await place(Vector3(25,0.05,-12))
	bug.global_position = Vector3(25,0.05,-14.6)
	bug.set_physics_process(true)
	gym.start_encounter()
	await ticks(3)
	check(bug.state() == "Windup", "Close bug telegraphs before lunging")
	var blocker := StaticBody3D.new()
	var collider := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(4,3,0.25)
	collider.shape = box
	blocker.add_child(collider)
	gym.add_child(blocker)
	blocker.position = Vector3(25,1.5,-13.1)
	await ticks(55)
	check(health.health == 100, "Solid cover interrupts a lunge without damage through the wall")
	blocker.queue_free()
	player.reset_player()
	await ticks(3)
	await place(Vector3(25,0.05,-12))
	bug.global_position = Vector3(25,0.05,-14.6)
	gym.start_encounter()
	await ticks(3)
	player.reset_player()
	await ticks(75)
	check(bug.state() == "Dormant" and health.health == 100 and gym.state() == "Ready", "Reset during wind-up cancels the pending attack")
	var cover := ray(Vector3(20,3,-11),Vector3(20,0,-11))
	check(not cover.is_empty() and absf(cover.position.y - 2.2) < 0.001, "Tall cover retains its exact 2.2 metre height")
	var low := ray(Vector3(13,3,-4.5),Vector3(13,0,-4.5))
	check(not low.is_empty() and absf(low.position.y - 1.1) < 0.001, "Low cover retains its exact 1.1 metre height")
	var fx := gym.get_node("Effects")
	for i in 80: fx._splat(Vector3(20,0,-5),Vector3.UP,0.1)
	for i in 40: fx.spawn_impact(Vector3(20,1,-5),Vector3.UP)
	check(fx.splats.size() == fx.max_splats and fx.droplets.size() <= fx.max_droplets, "Effects remain bounded during repeated fire")
	fx.clear_effects()
	await ticks(2)
	# Exercise the actual gym selection input and ensure no old encounter survives.
	current_scene = gym
	var selection := InputEventKey.new()
	selection.physical_keycode = KEY_F1
	selection.pressed = true
	player._unhandled_input(selection)
	await ticks(8)
	check(current_scene.has_node("MovementAnnex") and get_nodes_in_group("combat_gym").is_empty(), "F1 opens movement gym and removes the old encounter")
	selection.physical_keycode = KEY_F2
	current_scene.get_node("GymPlayer")._unhandled_input(selection)
	await ticks(8)
	check(current_scene.has_node("Bug") and get_nodes_in_group("combat_gym").size() == 1 and current_scene.state() == "Ready", "F2 opens a fresh combat gym without duplicate players or encounters")
	print("COMBAT_QA: ", checks - failures.size(), "/", checks, " passed")
	quit(0 if failures.is_empty() else 1)
