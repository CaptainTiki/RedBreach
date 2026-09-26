extends SceneTree
## Captures the freight v2 greybox into docs/freight-v2-built.png (player-eye views).
## Views come from missions/freight_v2/freight_v2_data.json, written from tools/freight_v2.py.
const CELL := Vector2i(640, 360)
var scene: Node3D
var player: CharacterBody3D

func _initialize() -> void: call_deferred("run")

func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame

func shoot(v: Array) -> Image:
	var eye: Array = v[1]
	var at: Array = v[2]
	var crouch: bool = v[3]
	var pos := Vector3(eye[0], eye[2] + 0.05, -eye[1])
	var point := Vector3(at[0], at[2], -at[1])
	if crouch:
		Input.action_press("gym_crouch")
	else:
		Input.action_release("gym_crouch")
	player.relocate(Transform3D(Basis.IDENTITY, pos))
	await ticks(20)
	var eye_pos: Vector3 = player.camera.global_position
	var direction: Vector3 = point - eye_pos
	player.rotation.y = atan2(-direction.x, -direction.z)
	player._pitch = atan2(direction.y, Vector2(direction.x, direction.z).length())
	player.reset_camera_interpolation()
	await ticks(24)
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	img.resize(CELL.x, CELL.y, Image.INTERPOLATE_BILINEAR)
	return img

func run() -> void:
	DisplayServer.window_set_size(Vector2i(1280, 720))
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight_v2/freight_v2_data.json"))
	scene = load("res://missions/freight_v2/freight_v2.tscn").instantiate()
	root.add_child(scene)
	player = scene.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	player.get_node("HUD").visible = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	# Open the doors so the walk reads as it plays.
	await ticks(30)
	for door in scene.find_children("*", "", true, false):
		if door.has_method("request_toggle") and door.state_name() == "Closed":
			door.request_toggle()
	for flicker in scene.find_children("flicker", "", true, false):
		if flicker.has_method("force"):
			flicker.force(true, true)
	await ticks(120)
	var cells := []
	for v in data.views:
		scene.get_node("CanvasLayer/Label").text = str(v[0]) if scene.has_node("CanvasLayer/Label") else ""
		cells.append(await shoot(v))
	Input.action_release("gym_crouch")
	var cols := 3
	var rows := int(ceil(cells.size() / float(cols)))
	var out := Image.create(cols * CELL.x, rows * CELL.y, false, Image.FORMAT_RGBA8)
	for i in cells.size():
		var img: Image = cells[i]
		img.convert(Image.FORMAT_RGBA8)
		out.blit_rect(img, Rect2i(Vector2i.ZERO, CELL), Vector2i((i % cols) * CELL.x, (i / cols) * CELL.y))
	out.save_png(ProjectSettings.globalize_path("res://").path_join("../docs/freight-v2-built.png").simplify_path())
	print("SHEET freight-v2-built.png ", cols, "x", rows)
	print("FREIGHT_V2_CAPTURE: PASS")
	quit()
