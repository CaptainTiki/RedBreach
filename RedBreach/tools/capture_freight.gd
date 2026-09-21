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
	if "--screening-only" in OS.get_cmdline_user_args():
		mission.get_node("HUD").hide()
		await view(Vector3(94.5-190,0.05,272-260),Vector3(86-190,1.65,270-260),"f04_entry")
		await view(Vector3(88-190,0.05,272-260),Vector3(87-190,1.65,263-260),"f04_equipment")
		await view(Vector3(84.4-190,0.05,272-260),Vector3(93-190,1.9,271-260),"f04_reverse")
		await view(Vector3(88-190,0.05,272.8-260),Vector3(88-190,1.7,278-260),"f04_exit")
		print("FREIGHT_CAPTURE_F04: PASS")
		quit();return
	if "--registration-only" in OS.get_cmdline_user_args():
		mission.get_node("HUD").hide()
		await view(Vector3(-76.3,0.05,10),Vector3(-86,0.6,15),"f03_entry")
		await view(Vector3(-90,0.05,12),Vector3(-90,0.1,28),"f03_spine")
		await view(Vector3(-89,0.05,20),Vector3(-83,1.0,20),"f03_staff_closed")
		mission.get_node("RegistrationF02/StaffDoor").request_toggle()
		await ticks(60)
		await view(Vector3(-87,0.05,20),Vector3(-79,1.0,18.5),"f03_staff_open")
		await view(Vector3(-90,0.05,25.3),Vector3(-81,1.1,28),"f03_office")
		await view(Vector3(-84,0.05,30),Vector3(-84,1.5,37),"f03_window")
		print("FREIGHT_CAPTURE_F03: PASS")
		quit();return
	await view(Vector3(0,0.05,68),Vector3(0,1,42),"arrival")
	mission.get_node("HUD").hide()
	await view(Vector3(0,0.05,15),Vector3(0,1.8,-36),"hub")
	await view(Vector3(-143,0.05,-25),Vector3(-150,-1.0,-37),"inspection")
	await view(Vector3(-77,0.05,10),Vector3(-81,1.6,17),"intake")
	await view(Vector3(-83,0.05,11),Vector3(-80,1.6,17),"registration")
	await view(Vector3(-90,0.05,13),Vector3(-89,1.6,21),"waiting")
	await view(Vector3(-81,0.05,20),Vector3(-79,1.1,16.5),"staff_counter")
	await view(Vector3(-90,0.05,27),Vector3(-81,1.5,32),"lounge")
	await view(Vector3(-81,0.05,10),Vector3(-84,1.5,4),"entry_equipment")
	await view(Vector3(-111,0.05,8),Vector3(-122,0.9,8),"office")
	await view(Vector3(-84,0.05,30),Vector3(-83,1.6,42),"window")
	await view(Vector3(-136,0.05,-29),Vector3(-136,-1.1,-39),"stair_head")
	await view(Vector3(-146,-1.95,-57),Vector3(-146,0.1,-69),"pump_room")
	await view(Vector3(-105,-1.95,-63),Vector3(-105,0.2,-49),"annex")
	await view(Vector3(-115,-1.95,-38),Vector3(-115,-0.3,-25),"workshop")
	await view(Vector3(-132,0.05,-126),Vector3(-132,4.8,-145),"records_stairs")
	await view(Vector3(-111,4.05,-124),Vector3(-139,1.6,-129),"records_gallery")
	await view(Vector3(-45,2.05,-142),Vector3(-45,6.8,-125),"watch_stairs")
	await view(Vector3(-58,6.05,-122),Vector3(-45,6.8,-123),"watch_upper")
	await view(Vector3(-70,6.05,-85),Vector3(-44,1.6,-84),"clearance")
	await view(Vector3(152,-1.95,-45),Vector3(152,1.0,-81),"pumps")
	await view(Vector3(35.5,6.05,-208),Vector3(58,1.2,-208),"generator")
	await view(Vector3(51,2.05,-68),Vector3(69,3.2,-77),"control")
	print("FREIGHT_CAPTURE: PASS")
	quit()
