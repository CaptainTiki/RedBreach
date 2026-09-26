extends SceneTree
## Captures the style lab comparisons into three sheets under docs/:
##   style-lab-palettes.png      views x palette (zoned mix, all warm, all steel, all concrete)
##   style-lab-lighting.png      the mixed plan (edge+wall, floor-lit, damaged) and all-floor, measured
##   style-lab-presentation.png  views x presentation off / subtle / strong
## Views and tables come from style/style_lab_data.json.
const CELL := Vector2i(640, 360)
var scene: Node3D
var lab: Node3D
var player: CharacterBody3D
var data: Dictionary
var views: Dictionary = {}

func _initialize() -> void: call_deferred("run")

func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame

func index_of(table: Array, name: String) -> int:
	for i in table.size():
		if table[i][0] == name:
			return i
	push_error("unknown " + name)
	return 0

func shoot(view: String, palette: String, plan: String, present: int, settle: int = 24) -> Image:
	var v: Array = views[view]
	var pos := Vector3(v[0][0], v[0][1], v[0][2])
	var point := Vector3(v[1][0], v[1][1], v[1][2])
	lab.palette = index_of(data.palettes, palette)
	lab.plan = index_of(data.plans, plan)
	lab.presentation = present
	lab.caption = view
	lab.apply()
	player.relocate(Transform3D(Basis.IDENTITY, pos))
	var direction: Vector3 = point - (pos + Vector3.UP * 1.65)
	player.rotation.y = atan2(-direction.x, -direction.z)
	player._pitch = atan2(direction.y, Vector2(direction.x, direction.z).length())
	player.reset_camera_interpolation()
	# Volumetric fog and SSAO converge over several frames.
	await ticks(settle)
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	img.resize(CELL.x, CELL.y, Image.INTERPOLATE_BILINEAR)
	return img

func luminance(img: Image, rect: Rect2) -> float:
	var total := 0.0
	var n := 0
	for y in range(int(rect.position.y * img.get_height()), int(rect.end.y * img.get_height()), 2):
		for x in range(int(rect.position.x * img.get_width()), int(rect.end.x * img.get_width()), 2):
			var c := img.get_pixel(x, y)
			total += 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b
			n += 1
	return total / max(n, 1) * 255.0

func report(label: String, img: Image) -> void:
	print("LIGHT ", label, " ceiling=%.1f walls=%.1f floor=%.1f" % [
		luminance(img, Rect2(0.3, 0.0, 0.4, 0.15)),
		(luminance(img, Rect2(0.0, 0.2, 0.18, 0.45)) + luminance(img, Rect2(0.82, 0.2, 0.18, 0.45))) / 2.0,
		luminance(img, Rect2(0.3, 0.8, 0.4, 0.2))])

func sheet(cells: Array, cols: int, path: String) -> void:
	var rows := int(ceil(cells.size() / float(cols)))
	var out := Image.create(cols * CELL.x, rows * CELL.y, false, Image.FORMAT_RGBA8)
	for i in cells.size():
		var img: Image = cells[i]
		img.convert(Image.FORMAT_RGBA8)
		out.blit_rect(img, Rect2i(Vector2i.ZERO, CELL), Vector2i((i % cols) * CELL.x, (i / cols) * CELL.y))
	out.save_png(ProjectSettings.globalize_path("res://").path_join("../docs/" + path).simplify_path())
	print("SHEET ", path, " ", cols, "x", rows)

func run() -> void:
	DisplayServer.window_set_size(Vector2i(1280, 720))
	data = JSON.parse_string(FileAccess.get_file_as_string("res://style/style_lab_data.json"))
	for v in data.views:
		views[v[0]] = [v[1], v[2]]
	scene = load("res://style/style_lab.tscn").instantiate()
	root.add_child(scene)
	lab = scene
	player = scene.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	player.get_node("HUD").visible = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var flicker := scene.get_node("Lighting/Bays/Bay7/flicker")
	flicker.force(true)
	await ticks(30)

	var cells := []
	for view in ["01_p1_down", "03_p2_down", "05_p3_down", "10_room_machine"]:
		for p in data.palettes:
			cells.append(await shoot(view, p[0], "edge_low", 1))
	sheet(cells, 4, "style-lab-palettes.png")

	cells = []
	var img: Image
	for spec in [["01_p1_down", "mixed"], ["02_p1_wall", "mixed"], ["14_p2_floor", "mixed"], ["04_p2_wall", "mixed"],
			["01_p1_down", "floor"], ["03_p2_down", "damaged"]]:
		img = await shoot(spec[0], "mix", spec[1], 1)
		report("%s %s" % spec, img)
		cells.append(img)
	# The damaged stretch: the failing fitting caught mid-burst with sparks,
	# then out, then the view back from inside the dead bay.
	flicker.force(true, true)
	img = await shoot("05_p3_down", "mix", "mixed", 1, 8)
	report("05_p3_down flicker-on", img)
	cells.append(img)
	flicker.force(false)
	img = await shoot("05_p3_down", "mix", "mixed", 1)
	report("05_p3_down flicker-out", img)
	cells.append(img)
	img = await shoot("13_p3_dead", "mix", "mixed", 1)
	report("13_p3_dead mixed", img)
	cells.append(img)
	img = await shoot("13_p3_dead", "mix", "edge_low", 1)
	report("13_p3_dead lit-for-comparison", img)
	cells.append(img)
	sheet(cells, 2, "style-lab-lighting.png")

	cells = []
	flicker.force(true)
	for view in ["15_room_shafts", "12_mars_view", "05_p3_down"]:
		for present in 3:
			cells.append(await shoot(view, "mix", "mixed", present, 40))
	sheet(cells, 3, "style-lab-presentation.png")
	print("STYLE_LAB_CAPTURE: PASS")
	quit()
