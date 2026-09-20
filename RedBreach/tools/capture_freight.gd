extends SceneTree
var mission: Node3D
var player: CharacterBody3D
func _initialize() -> void:call_deferred("run")
func ticks(count: int) -> void:
	for i in count:await physics_frame
	await process_frame
func view(location: Vector3,target: Vector3,name: String) -> void:
	player.relocate(Transform3D(Basis.IDENTITY,location))
	await ticks(8)
	var d: Vector3 = target-player.camera.global_position
	player.rotation.y = atan2(-d.x,-d.z)
	player._pitch = atan2(d.y,Vector2(d.x,d.z).length())
	player.reset_camera_interpolation()
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/freight_"+name+".png")
func run() -> void:
	mission = load("res://missions/freight/freight_blockout.tscn").instantiate()
	mission.storage_enabled = false
	root.add_child(mission)
	player = mission.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(100)
	await view(Vector3(0,0.05,68),Vector3(0,1,42),"arrival")
	mission.get_node("HUD").hide()
	await view(Vector3(0,0.05,15),Vector3(0,1.8,-36),"hub")
	await view(Vector3(-158,0.05,-21),Vector3(-158,-1.0,-32),"inspection")
	await view(Vector3(152,-1.95,-45),Vector3(152,1.0,-81),"pumps")
	await view(Vector3(35.5,6.05,-208),Vector3(58,1.2,-208),"generator")
	await view(Vector3(51,2.05,-68),Vector3(69,3.2,-77),"control")
	print("FREIGHT_CAPTURE: PASS")
	quit()
