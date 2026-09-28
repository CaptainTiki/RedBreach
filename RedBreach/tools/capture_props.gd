extends SceneTree
## Renders the props gallery (F12) into docs/props-gallery.png: the views in props/props_data.json, three to a row.
## Run without --headless. Flickering fittings are frozen on so the sheet shows them.
const CELL := Vector2i(640, 360)


func _initialize() -> void:
	call_deferred("run")


func run() -> void:
	DisplayServer.window_set_size(Vector2i(1280, 720))
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://props/props_data.json"))
	var gallery: Node = (load("res://props/props_gallery.tscn") as PackedScene).instantiate()
	root.add_child(gallery)
	gallery.get_node("GymPlayer").free()          # the sheet is the props, not the HUD
	for n in gallery.find_children("*", "", true, false):
		if n.get("hold") != null and n.get("flicker") != null:
			n.set("hold", true)
	var cam := Camera3D.new()
	cam.fov = 75
	gallery.add_child(cam)
	cam.current = true
	for i in 60:
		await process_frame
	var cells := []
	for v in data.views:
		cam.global_position = Vector3(v[1][0], v[1][1], v[1][2])
		cam.look_at(Vector3(v[2][0], v[2][1], v[2][2]), Vector3.UP)
		for i in 8:
			await process_frame
		await RenderingServer.frame_post_draw
		var img := root.get_texture().get_image()
		img.resize(CELL.x, CELL.y, Image.INTERPOLATE_BILINEAR)
		img.convert(Image.FORMAT_RGBA8)
		cells.append(img)
	var rows := int(ceil(cells.size() / 3.0))
	var out := Image.create(3 * CELL.x, rows * CELL.y, false, Image.FORMAT_RGBA8)
	for i in cells.size():
		out.blit_rect(cells[i], Rect2i(Vector2i.ZERO, CELL), Vector2i((i % 3) * CELL.x, (i / 3) * CELL.y))
	out.save_png(ProjectSettings.globalize_path("res://").path_join("../docs/props-gallery.png").simplify_path())
	print("PROPS_CAPTURE: PASS (%d views)" % cells.size())
	quit()
