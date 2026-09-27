extends SceneTree
## Renders what the player saw at a playtest note: loads the note's scene, puts a camera at the recorded transform and
## field of view (the window at the recorded size), hides the HUD, draws a thin crosshair on the aim point and saves a
## PNG. Run WITHOUT --headless, through tools/view-playtest-note.ps1:
##   -- <session folder> <note number | all> <output folder>
## Views render the map as it is NOW, so after a fix the same note shows whether the fix worked.

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 3:
		print("VIEW_NOTE: FAIL usage: -- <session folder> <note number | all> <output folder>")
		quit(1)
		return
	var folder := args[0]
	var rows: Array = []
	for line in FileAccess.get_file_as_string(folder.path_join("notes.jsonl")).split("\n"):
		if line.strip_edges() != "":
			rows.append(JSON.parse_string(line))
	var head: Dictionary = rows.filter(func(r): return r.get("type") == "session").front()
	var notes := rows.filter(func(r): return r.get("type") == "note" and (args[1] == "all" or int(r.n) == int(args[1])))
	if notes.is_empty():
		print("VIEW_NOTE: FAIL no note ", args[1], " in ", folder)
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(args[2])
	change_scene_to_file(head.scene)
	for i in 10:
		await process_frame
	var level := current_scene
	# The player stands still and its HUD goes; only the level's own geometry and lights remain.
	for node in level.find_children("*", "CharacterBody3D", true, false):
		node.process_mode = Node.PROCESS_MODE_DISABLED
	for node in level.find_children("*", "CanvasLayer", true, false):
		node.visible = false
	var cam := Camera3D.new()
	level.add_child(cam)
	cam.current = true
	var layer := CanvasLayer.new()
	level.add_child(layer)
	for rect in [Rect2(-9, -0.5, 6, 1), Rect2(3, -0.5, 6, 1), Rect2(-0.5, -9, 1, 6), Rect2(-0.5, 3, 1, 6)]:
		var line := ColorRect.new()
		line.color = Color(1.0, 0.2, 0.8)
		line.anchor_left = 0.5
		line.anchor_right = 0.5
		line.anchor_top = 0.5
		line.anchor_bottom = 0.5
		line.offset_left = rect.position.x
		line.offset_top = rect.position.y
		line.offset_right = rect.end.x
		line.offset_bottom = rect.end.y
		layer.add_child(line)
	for note in notes:
		var size: Array = note.get("viewport", [1920, 1080])
		DisplayServer.window_set_size(Vector2i(int(size[0]), int(size[1])))
		if note.camera is Dictionary:
			var c: Dictionary = note.camera
			var r: Array = c.rotation_deg
			cam.global_transform = Transform3D(Basis.from_euler(Vector3(deg_to_rad(r[0]), deg_to_rad(r[1]), deg_to_rad(r[2]))),
				Vector3(c.position[0], c.position[1], c.position[2]))
			cam.fov = float(c.get("fov", 75.0))
		else:
			# The first notes (before transforms were recorded) kept the camera position and look direction only.
			var at := Vector3(note.camera[0], note.camera[1], note.camera[2])
			cam.global_position = at
			cam.look_at(at + Vector3(note.look[0], note.look[1], note.look[2]), Vector3.UP)
		for i in 8:
			await process_frame
		await RenderingServer.frame_post_draw
		var out: String = args[2].path_join("note_%03d.png" % int(note.n))
		get_root().get_texture().get_image().save_png(out)
		print("VIEW_NOTE: #", int(note.n), " ", out)
	quit(0)
