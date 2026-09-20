extends SceneTree
var trial: Node3D
var player: CharacterBody3D
func _initialize() -> void: call_deferred("run")
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func aim(point: Vector3) -> void:
	var direction: Vector3 = point - player.camera.global_position
	player.rotation.y = atan2(-direction.x,-direction.z)
	player._pitch = atan2(direction.y,Vector2(direction.x,direction.z).length())
	player.reset_camera_interpolation()
func capture(label: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/bug_mix_" + label + ".png")
func run() -> void:
	trial = load("res://encounters/route_trial.tscn").instantiate()
	trial.storage_enabled = false
	root.add_child(trial)
	player = trial.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(20)
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(21,0.05,-32)))
	player.get_node("Health")._immunity = 1000
	trial.start_run()
	var mixed: Node3D = trial.get_node("Encounters/D")
	mixed.begin()
	await ticks(30)
	aim(Vector3(30,0.8,-32))
	await capture("approach")
	# Controlled comparison of the three actual scenes, separate from the live approach.
	player.reset_player()
	await ticks(5)
	mixed = trial.get_node("Encounters/D")
	for encounter in trial.get_node("Encounters").get_children():
		for enemy in encounter.enemies:
			enemy.set_physics_process(false)
			enemy.hide()
			enemy.collision_layer = 0
	var regular: CharacterBody3D = mixed.enemies[0]
	var spitter: CharacterBody3D = mixed.enemies[2]
	var small: CharacterBody3D = mixed.enemies[3]
	var enemies: Array = [small,regular,spitter]
	for i in 3:
		var enemy: CharacterBody3D = enemies[i]
		enemy.show()
		enemy.collision_layer = 1
		enemy.global_position = Vector3(-4.0 + float(i)*4.0,0.05,-8)
		enemy.rotation.y = PI
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(0,0.05,0.5)))
	trial.get_node("HUD").hide()
	player.get_node("HUD").hide()
	player.get_node("Health/HUD").hide()
	player.pistol.get_node("HUD").hide()
	aim(Vector3(0,0.7,-8))
	await ticks(10)
	await capture("sizes")
	trial.start_run()
	mixed.begin()
	aim(small.global_position + Vector3.UP * 0.4)
	if not player.pistol.fire() or small.health > 0:
		push_error("Small capture shot missed")
		quit(1)
		return
	await ticks(4)
	await capture("small_splat")
	await ticks(20)
	await capture("small_corpse")
	print("BUG_MIX_CAPTURE: PASS")
	quit()
