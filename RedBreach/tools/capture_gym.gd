extends SceneTree

func _initialize() -> void:
	call_deferred("capture")

func capture() -> void:
	var gym: Node3D = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	gym.get_node("GymPlayer")._physics_process(0.0)
	gym.get_node("GymPlayer").set_physics_process(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/gym_player_view.png")
	gym.get_node("GymPlayer/HUD").hide()
	var overview := Camera3D.new()
	gym.add_child(overview)
	overview.position = Vector3(20, 24, 27)
	overview.look_at(Vector3(0, 0, -1))
	overview.fov = 55.0
	overview.current = true
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/gym_overview.png")
	print("GYM_CAPTURE: PASS")
	quit()
