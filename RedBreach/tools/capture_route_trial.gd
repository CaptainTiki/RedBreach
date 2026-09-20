extends SceneTree
var trial: Node3D
var player: CharacterBody3D
func _initialize() -> void: call_deferred("run")
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func aim(point: Vector3) -> void:
	var direction: Vector3 = point-player.camera.global_position
	player.rotation.y = atan2(-direction.x,-direction.z)
	player._pitch = atan2(direction.y,Vector2(direction.x,direction.z).length())
	player.reset_camera_interpolation()
func capture(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/route_"+name+".png")
func run() -> void:
	trial = load("res://encounters/route_trial.tscn").instantiate()
	trial.storage_enabled = false
	root.add_child(trial)
	player = trial.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(20)
	await capture("start")
	var overview := Camera3D.new()
	trial.add_child(overview)
	overview.position = Vector3(16,65,-12)
	overview.look_at(Vector3(16,0,-12),Vector3.FORWARD)
	overview.projection = Camera3D.PROJECTION_ORTHOGONAL
	overview.size = 62
	overview.current = true
	trial.get_node("HUD").hide()
	player.get_node("HUD").hide()
	player.pistol.get_node("HUD").hide()
	player.get_node("Health/HUD").hide()
	await ticks(3)
	await capture("overview")
	overview.queue_free()
	player.camera.current = true
	trial.get_node("HUD").show()
	player.get_node("HUD").show()
	player.pistol.get_node("HUD").show()
	player.get_node("Health/HUD").show()
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(0,0.05,-16)))
	aim(Vector3(-4.7,1,-20))
	await ticks(3)
	await capture("vent_closed")
	trial.start_run()
	trial.get_node("Encounters/B").begin()
	await ticks(27)
	aim(Vector3(-3.8,1,-20))
	await capture("vent_open")
	player.get_node("Health").invulnerability_seconds = 1000
	player.get_node("Health")._immunity = 1000
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(23,0.05,-32)))
	await ticks(10)
	aim(Vector3(32,1,-33))
	await capture("mixed")
	trial.finish_run("bypassed")
	await capture("results")
	print("ROUTE_CAPTURE: PASS")
	quit()
