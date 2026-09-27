extends SceneTree
## Drives the PlaytestNotes autoload as a player would: a Z mark, then a Q note typed and submitted, checks the session
## it wrote and deletes it. Run WITHOUT --headless (the autoload is silent headless).

func _initialize() -> void:
	call_deferred("run")

func key(code: Key, unicode := 0) -> void:
	for pressed in [true, false]:
		var e := InputEventKey.new()
		e.physical_keycode = code
		e.keycode = code
		e.unicode = unicode
		e.pressed = pressed
		Input.parse_input_event(e)
		await process_frame

func run() -> void:
	var notes := root.get_node_or_null("PlaytestNotes")
	if notes == null:
		print("PLAYTEST_TEST: FAIL no PlaytestNotes autoload")
		quit(1)
		return
	change_scene_to_file("res://missions/freight_v2/freight_v2.tscn")
	for i in 20:
		await process_frame
	var level := current_scene
	level.get_node("GymPlayer").set_physics_process(false)
	var cam := Camera3D.new()
	level.add_child(cam)
	cam.current = true
	# The secret closet, looking up at its ceiling beside door 1 (plan (-23.5, 9.5), eye 1.6 m over the -3 floor).
	cam.global_position = Vector3(-23.5, -1.4, -9.5)
	cam.look_at(Vector3(-23.5, 0.0, -9.9), Vector3.FORWARD)
	for i in 5:
		await process_frame
	await key(KEY_Z)
	for i in 10:
		await process_frame
	# The sorting bay, looking at its north wall.
	cam.global_position = Vector3(0.0, -1.4, -30.0)
	cam.look_at(Vector3(4.0, -1.0, -40.0), Vector3.UP)
	for i in 5:
		await process_frame
	await key(KEY_Q)
	for i in 10:
		await process_frame
	for ch in "test note: seam here":
		await key(OS.find_keycode_from_string(ch.to_upper()) if ch != " " and ch != ":" else (KEY_SPACE if ch == " " else KEY_COLON), ch.unicode_at(0))
	await key(KEY_ENTER)
	for i in 10:
		await process_frame
	# Two notes after the session line, one text file and nothing else, each note carrying the camera's transform; then
	# the test removes its own session (pass "-- keep" to leave it for tools/view-playtest-note.ps1).
	var dir: String = notes._dir
	var lines := FileAccess.get_file_as_string(dir.path_join("notes.jsonl")).strip_edges().split("\n")
	var ok := lines.size() == 3 and DirAccess.get_files_at(dir).size() == 1 and not paused and "seam here" in lines[2]
	for i in [1, 2]:
		var rec = JSON.parse_string(lines[i]) if lines.size() > i else null
		ok = ok and rec is Dictionary and rec.camera is Dictionary and rec.camera.rotation_deg.size() == 3 and rec.has("viewport")
	if not "keep" in OS.get_cmdline_user_args():
		for f in DirAccess.get_files_at(dir):
			DirAccess.remove_absolute(dir.path_join(f))
		DirAccess.remove_absolute(dir)
	print("PLAYTEST_TEST: ", "PASS" if ok else "FAIL", " (", lines.size(), " lines)")
	quit(0 if ok else 1)
