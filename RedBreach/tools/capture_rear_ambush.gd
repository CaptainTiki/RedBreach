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
	root.get_texture().get_image().save_png("res://.godot/rear_ambush_" + label + ".png")
func run() -> void:
	trial = load("res://encounters/route_trial.tscn").instantiate()
	trial.storage_enabled = false
	root.add_child(trial)
	player = trial.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(20)
	for encounter in trial.get_node("Encounters").get_children():
		for enemy in encounter.enemies: enemy.set_physics_process(false)
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(12,0.05,-38)))
	aim(Vector3(20,1.3,-38))
	await ticks(3)
	await capture("hidden")
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(18,0.05,-31.5)))
	aim(Vector3(30,0.9,-32))
	await ticks(3)
	await capture("reveal")
	player.relocate(Transform3D(Basis.IDENTITY,Vector3(17,0.05,-38)))
	aim(Vector3(10,0.85,-41))
	await ticks(3)
	await capture("rear_closed")
	trial.start_run()
	var mixed: Node3D = trial.get_node("Encounters/D")
	mixed.begin()
	await ticks(133)
	await capture("rear_open")
	print("REAR_AMBUSH_CAPTURE: PASS / burst=",mixed.get_node("Vent").burst_count," / enemies=",mixed.enemies.size())
	quit()
