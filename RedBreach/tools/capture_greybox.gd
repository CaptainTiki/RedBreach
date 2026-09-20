extends SceneTree
var scene: Node3D
var player: CharacterBody3D
func _initialize() -> void: call_deferred("run")
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func capture(name: String, position: Vector3, point: Vector3) -> void:
	player.relocate(Transform3D(Basis.IDENTITY,position))
	var direction: Vector3 = point-player.camera.global_position
	player.rotation.y = atan2(-direction.x,-direction.z)
	player._pitch = atan2(direction.y,Vector2(direction.x,direction.z).length())
	player.reset_camera_interpolation()
	await ticks(5)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/greybox_"+name+".png")
func run() -> void:
	for path in ["res://gym/gym.tscn","res://combat/combat_gym.tscn","res://encounters/route_trial.tscn"]:
		scene = load(path).instantiate()
		if path.contains("route_trial"): scene.storage_enabled = false
		root.add_child(scene)
		player = scene.get_node("GymPlayer")
		player.control_override = true
		player.pistol.audio_enabled = false
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		await ticks(20)
		if path == "res://gym/gym.tscn":
			await capture("movement",Vector3(1,0.05,7),Vector3(-3,1.4,-7))
			await capture("ramp",Vector3(-1,0.05,1),Vector3(-6,1,-4))
		elif path.contains("combat_gym"):
			await capture("combat",Vector3(2,0.05,6),Vector3(-3,1.5,-16))
			await capture("arena",Vector3(25,0.05,-4),Vector3(20,1.5,-16))
		else:
			await capture("route",Vector3(0,0.05,9),Vector3(0,1.5,-20))
		scene.queue_free()
		await ticks(3)
	print("GREYBOX_CAPTURE: PASS")
	quit()
