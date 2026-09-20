extends SceneTree
var player: CharacterBody3D
var pistol: Node3D

func _initialize() -> void:
	call_deferred("run")

func ticks(count: int) -> void:
	for i in count:
		await physics_frame
	await process_frame

func capture(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/pistol_" + name + ".png")

func run() -> void:
	var gym: Node3D = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	pistol = player.get_node("Camera3D/Pistol")
	pistol.audio_enabled = false
	player.control_override = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(6, 0.05, 6)))
	await ticks(30)
	player._pitch = atan2(1.4 - player.camera.global_position.y, 7.0)
	player.reset_camera_interpolation()
	await capture("hip")
	Input.action_press("gym_aim")
	await ticks(30)
	await capture("ads")
	pistol.fire()
	await ticks(20)
	pistol.request_reload()
	await ticks(12)
	await capture("reload")
	Input.action_release("gym_aim")
	print("PISTOL_CAPTURE: PASS")
	quit()
