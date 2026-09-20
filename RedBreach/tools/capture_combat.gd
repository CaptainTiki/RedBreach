extends SceneTree
var gym: Node3D
var player: CharacterBody3D
var bug: CharacterBody3D
func _initialize() -> void: call_deferred("run")
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func aim(point: Vector3) -> void:
	var direction: Vector3 = point - player.camera.global_position
	player.rotation.y = atan2(-direction.x,-direction.z)
	player._pitch = atan2(direction.y,Vector2(direction.x,direction.z).length())
	player.reset_camera_interpolation()
func shot(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/combat_"+name+".png")
func run() -> void:
	gym = load("res://combat/combat_gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	bug = gym.get_node("Bug")
	player.control_override = true
	player.pistol.audio_enabled = false
	bug.audio_enabled = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(20)
	await shot("spawn")
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(0,0.05,0)))
	await ticks(20)
	aim(Vector3(0,1.65,-20))
	Input.action_press("gym_aim")
	await ticks(20)
	await shot("range")
	Input.action_release("gym_aim")
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(25,0.05,-9)))
	bug.global_position = Vector3(25,0.05,-14)
	bug.set_physics_process(false)
	gym.start_encounter()
	await ticks(20)
	bug.rotation.y = PI
	aim(bug.global_position + Vector3.UP * 0.65)
	await shot("bug")
	player.pistol.fire()
	await ticks(4)
	await shot("hit")
	await ticks(20)
	for i in 2:
		aim(bug.global_position + Vector3.UP * 0.7)
		player.pistol.fire()
		await ticks(20)
	aim(bug.global_position + Vector3.UP * 0.7)
	player.pistol.fire()
	await ticks(5)
	await shot("splat")
	await ticks(45)
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(25,0.05,-11)))
	await ticks(10)
	aim(bug.global_position)
	await shot("corpse")
	print("COMBAT_CAPTURE: PASS")
	quit()
