extends SceneTree
var gym: Node3D
var player: CharacterBody3D
var spitter: CharacterBody3D
func _initialize() -> void: call_deferred("run")
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func aim(point: Vector3) -> void:
	var direction: Vector3 = point - player.camera.global_position
	player.rotation.y = atan2(-direction.x,-direction.z)
	player._pitch = atan2(direction.y,Vector2(direction.x,direction.z).length())
	player.reset_camera_interpolation()
func capture(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/spitter_"+name+".png")
func setup_enemy() -> void:
	player.reset_player()
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(25,0.05,-7)))
	spitter.global_position = Vector3(25,0.05,-14)
	spitter.rotation.y = PI
	spitter.set_physics_process(false)
	gym.start_encounter(1)
	await ticks(20)
	aim(spitter.get_node("MouthHitArea").global_position)
func run() -> void:
	gym = load("res://combat/combat_gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	spitter = gym.get_node("Spitter")
	player.control_override = true
	player.pistol.audio_enabled = false
	spitter.audio_enabled = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(20)
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(24.5,0.05,0)))
	await ticks(5)
	aim(Vector3(24.5,1.6,-2))
	await capture("panels")
	await setup_enemy()
	await capture("closed")
	spitter.set_physics_process(true)
	await ticks(8)
	spitter.set_physics_process(false)
	aim(spitter.get_node("MouthHitArea").global_position)
	await capture("open")
	player.pistol.fire()
	await ticks(4)
	await capture("weak_hit")
	await ticks(16)
	aim(spitter.get_node("MouthHitArea").global_position)
	player.pistol.fire()
	await ticks(4)
	await capture("death")
	await setup_enemy()
	spitter.set_physics_process(true)
	while spitter.spit_count == 0:
		await ticks(1)
	await ticks(2)
	await capture("projectile")
	print("SPITTER_CAPTURE: PASS")
	quit()
