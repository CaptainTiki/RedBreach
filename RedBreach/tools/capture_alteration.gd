extends SceneTree
var gym: Node3D
var player: CharacterBody3D

func _initialize() -> void:
	call_deferred("run")

func ticks(count: int) -> void:
	for i in count:
		await physics_frame
	await process_frame

func capture(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/alteration_" + name + ".png")

func run() -> void:
	gym = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	player.control_override = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(30)
	player.relocate(Transform3D(Basis(Vector3.UP, PI), Vector3(-46, 0.05, 6.5)))
	player._pitch = -0.15
	player.reset_camera_interpolation()
	await ticks(30)
	await capture("high_jump")
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(0, 0.05, 2)))
	player._pitch = -0.3
	player.reset_camera_interpolation()
	await ticks(30)
	await capture("old_sites")
	player.get_node("HUD").hide()
	var overview := Camera3D.new()
	gym.add_child(overview)
	overview.position = Vector3(-28, 30, 25)
	overview.look_at(Vector3(-34, 0, -2))
	overview.fov = 65.0
	overview.current = true
	await capture("overview")
	print("ALTERATION_CAPTURE: PASS")
	quit()
