extends SceneTree
var scene: Node3D
var player: CharacterBody3D
func _initialize() -> void: call_deferred("run")
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func capture(name: String, position: Vector3, point: Vector3) -> void:
	player.relocate(Transform3D(Basis.IDENTITY, position))
	var direction: Vector3 = point - player.camera.global_position
	player.rotation.y = atan2(-direction.x, -direction.z)
	player._pitch = atan2(direction.y, Vector2(direction.x, direction.z).length())
	player.reset_camera_interpolation()
	await ticks(5)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/arch_lab_" + name + ".png")
func run() -> void:
	scene = load("res://architecture/architecture_lab.tscn").instantiate()
	root.add_child(scene)
	player = scene.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(20)
	# Down the run from the south end: the rhythm test.
	await capture("01_down_the_run", Vector3(0, 0.05, 1.0), Vector3(0, 1.6, -22))
	# Off-centre at walking eye line - the view the player actually has.
	await capture("02_offset_eye_line", Vector3(1.3, 0.05, -1.0), Vector3(-1.0, 1.55, -20))
	# Standing in a bay, square on to the wall: does the build-up read at 1 m?
	await capture("03_wall_at_a_bay", Vector3(0, 0.05, -4.0), Vector3(-3.0, 1.5, -4.0))
	# Beside a rib, low, looking along it: the battered base and its toe.
	await capture("04_rib_base", Vector3(-0.6, 0.05, -4.5), Vector3(-2.4, 0.45, -6.2))
	# Under a rib looking up: the beam crossing the ceiling.
	await capture("05_under_a_rib", Vector3(0, 0.05, -8.0), Vector3(0, 3.6, -11.0))
	# Looking back from the north end.
	await capture("06_looking_back", Vector3(0, 0.05, -20.0), Vector3(0, 1.6, 2))
	print("ARCH_LAB_CAPTURE: PASS")
	quit()
