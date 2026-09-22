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
	root.get_texture().get_image().save_png("res://.godot/arch_corner_" + name + ".png")
func run() -> void:
	scene = load("res://architecture/architecture_lab_corners.tscn").instantiate()
	root.add_child(scene)
	player = scene.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await ticks(20)
	# The repetition test: 52 m of identical kit, nothing in it.
	await capture("01_long_straight", Vector3(0, 0.05, 2.0), Vector3(0, 1.6, 44))
	# Half way down it - is the rhythm still telling you anything?
	await capture("02_mid_straight", Vector3(1.2, 0.05, 26.0), Vector3(-0.8, 1.55, 50))
	# Approaching V1. The square landing should read as a full stop.
	await capture("03_v1_approach", Vector3(0, 0.05, 44.0), Vector3(0, 1.6, 55))
	# Standing in the V1 landing, looking down the exit corridor.
	await capture("04_v1_exit", Vector3(0, 0.05, 50.0), Vector3(14, 1.6, 52))
	# The V1 outer corner - the dead square pocket, with no rib on it.
	await capture("05_v1_outer_corner", Vector3(1.0, 0.05, 50.0), Vector3(-3.0, 1.5, 55.5))
	# Looking back through V1: does the rib rhythm line up across the turn?
	await capture("06_v1_looking_back", Vector3(12.0, 0.05, 52.0), Vector3(0, 1.6, 44))
	# Approaching V4 along the exit of V1.
	await capture("07_v4_approach", Vector3(14.0, 0.05, 52.0), Vector3(24, 1.6, 42))
	# Inside the 45 degree leg itself, with a rib standing in it.
	await capture("08_v4_in_the_leg", Vector3(21.0, 0.05, 51.0), Vector3(24, 1.6, 42))
	# Out of V4 and looking back up the diagonal.
	await capture("09_v4_looking_back", Vector3(24.0, 0.05, 40.0), Vector3(14, 1.6, 52))
	# Low beside a rib in the leg: the battered base on a 45 degree wall.
	await capture("10_v4_rib_base", Vector3(21.6, 0.05, 50.4), Vector3(23.4, 0.45, 49.0))
	# The T. It is square on purpose: chamfering two elbows would open the
	# middle and turn a decision point into a lobby.
	await capture("11_t_approach", Vector3(24.0, 0.05, 40.0), Vector3(24, 1.6, 22))
	# Standing in the junction, looking down the branch.
	await capture("12_t_branch", Vector3(24.0, 0.05, 30.0), Vector3(38, 1.6, 30))
	# The choice: straight on, or turn. Both legs visible at once.
	await capture("13_t_choice", Vector3(23.0, 0.05, 34.0), Vector3(26, 1.55, 26))
	# The jamb and the branch's first rib, 0.75 m apart - is that crowded?
	await capture("14_t_jamb", Vector3(25.5, 0.05, 31.8), Vector3(29.5, 1.4, 28.5))
	# Looking back into the junction from inside the branch.
	await capture("15_t_looking_back", Vector3(36.0, 0.05, 30.0), Vector3(22, 1.6, 30))
	# Close on the corners themselves - the earlier framings were too far back
	# to show what is actually happening where two profiles meet.
	await capture("16_v1_corner_close", Vector3(-1.2, 0.05, 53.0), Vector3(-2.9, 1.2, 54.9))
	await capture("17_v1_corner_low", Vector3(-1.4, 0.05, 53.4), Vector3(-2.9, 0.35, 54.9))
	await capture("18_v1_corner_high", Vector3(-1.4, 0.05, 53.4), Vector3(-2.9, 3.4, 54.9))
	await capture("19_t_jamb_close", Vector3(25.8, 0.05, 30.2), Vector3(26.9, 1.2, 27.2))
	# The user's own camera, reported from the editor: position (23.89, 30.72),
	# rotation.y = -41.4 deg. Looking from inside the junction at the jamb where
	# the branch Ts into the original hallway.
	await capture("20_user_view", Vector3(23.89, 0.05, 30.72), Vector3(27.20, 1.55, 26.97))
	print("ARCH_CORNER_CAPTURE: PASS")
	quit()
