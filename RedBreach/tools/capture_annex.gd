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
	root.get_texture().get_image().save_png("res://.godot/annex_" + name + ".png")

func place(position: Vector3) -> void:
	Input.action_release("gym_crouch")
	Input.action_release("gym_sprint")
	player.test_direction = Vector2.ZERO
	player.relocate(Transform3D(Basis.IDENTITY, position))
	await ticks(30)

func run() -> void:
	gym = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	player.control_override = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(30)
	player.get_node("HUD").hide()
	var overview := Camera3D.new()
	gym.add_child(overview)
	overview.position = Vector3(-28, 30, 25)
	overview.look_at(Vector3(-34, 0, -2))
	overview.fov = 65.0
	overview.current = true
	await capture("overview")
	player.get_node("HUD").show()
	player.camera.current = true
	await place(Vector3(-17.5, 0.05, 8.5))
	player.rotation.y = 1.0
	player.reset_camera_interpolation()
	await capture("entry")
	await place(Vector3(-36.5, 0.05, 2.5))
	await capture("jump")
	await place(Vector3(-32, 0.05, -5.25))
	Input.action_press("gym_crouch")
	await ticks(30)
	player.test_direction = Vector2(1, 0)
	await ticks(70)
	player.test_direction = Vector2.ZERO
	Input.action_release("gym_crouch")
	player.rotation.y = -PI * 0.5
	player.reset_camera_interpolation()
	await ticks(10)
	await capture("crouch")
	await place(Vector3(-20, 0.05, 9))
	Input.action_press("gym_sprint")
	player.test_direction = Vector2(0, -1)
	var runway := gym.get_node("MovementAnnex/Runway")
	for i in 250:
		await ticks(1)
		if runway.completed_runs > 0:
			break
	player.test_direction = Vector2.ZERO
	Input.action_release("gym_sprint")
	await capture("timing")
	print("ANNEX_CAPTURE: PASS")
	quit()
