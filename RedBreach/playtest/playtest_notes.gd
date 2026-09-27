extends Node
## Playtest notes (autoload "PlaytestNotes"): aim at something, press a key, and it is logged with everything needed to
## find it again in the map. Works in every scene with a 3D camera; does nothing headless.
##   Q  note: shoots a ray, marks the spot, pauses, and asks for a line of text (Enter saves, Esc cancels)
##   Z  quick z-fight mark: the same record without the text box (note "z-fight")
## Each session writes one small text file, <workspace>/playtests/<scene>/<date_time>/notes.jsonl, where the workspace
## is the folder above the Godot project. No screenshots: each note keeps the camera's transform and field of view, so
## tools/view-playtest-note.ps1 can put a camera back there and render the view on demand.
## tools/read-playtest-notes.py turns a session into a report: hit point, brush and TrenchBroom group, room, text.

const RAY_LENGTH := 200.0

var _dir := ""
var _file := ""
var _scene: Node = null
var _count := 0
var _pending := {}
var _layer: CanvasLayer
var _panel: PanelContainer
var _title: Label
var _edit: LineEdit
var _toast: Label
var _toast_time := 0.0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	if DisplayServer.get_name() == "headless":
		set_process_input(false)
		return
	_layer = CanvasLayer.new()
	_layer.layer = 100
	add_child(_layer)
	_toast = Label.new()
	_toast.add_theme_font_size_override("font_size", 18)
	_toast.add_theme_color_override("font_color", Color(1.0, 0.85, 0.3))
	_toast.add_theme_color_override("font_outline_color", Color.BLACK)
	_toast.add_theme_constant_override("outline_size", 6)
	_toast.anchor_top = 1.0
	_toast.anchor_bottom = 1.0
	_toast.offset_left = 16
	_toast.offset_top = -120
	_layer.add_child(_toast)
	_panel = PanelContainer.new()
	_panel.anchor_left = 0.2
	_panel.anchor_right = 0.8
	_panel.anchor_top = 0.72
	_panel.anchor_bottom = 0.72
	var box := VBoxContainer.new()
	_title = Label.new()
	_title.add_theme_font_size_override("font_size", 16)
	_edit = LineEdit.new()
	_edit.placeholder_text = "What is wrong here? (Enter saves, Esc cancels)"
	_edit.add_theme_font_size_override("font_size", 20)
	_edit.text_submitted.connect(_submit)
	box.add_child(_title)
	box.add_child(_edit)
	_panel.add_child(box)
	_panel.visible = false
	_layer.add_child(_panel)

func _process(delta: float) -> void:
	if _toast_time > 0.0:
		_toast_time -= delta
		if _toast_time <= 0.0:
			_toast.text = ""

func _input(event: InputEvent) -> void:
	if not (event is InputEventKey) or not event.pressed or event.echo:
		return
	if _panel.visible:
		if event.physical_keycode == KEY_ESCAPE:
			get_viewport().set_input_as_handled()
			_cancel()
		return
	if event.physical_keycode == KEY_Q or event.physical_keycode == KEY_Z:
		var camera := get_viewport().get_camera_3d()
		if camera == null or get_tree().current_scene == null:
			return
		get_viewport().set_input_as_handled()
		_mark(camera, event.physical_keycode == KEY_Z)

func _mark(camera: Camera3D, quick: bool) -> void:
	var from := camera.global_position
	var dir := -camera.global_basis.z
	var query := PhysicsRayQueryParameters3D.create(from, from + dir * RAY_LENGTH, 1)
	var exclude: Array[RID] = []
	var node: Node = camera
	while node != null:
		if node is CollisionObject3D:
			exclude.append(node.get_rid())
		node = node.get_parent()
	query.exclude = exclude
	var hit := camera.get_world_3d().direct_space_state.intersect_ray(query)
	var scene := get_tree().current_scene
	_count += 1
	var record := {
		"type": "note", "n": _count, "time": Time.get_datetime_string_from_system(), "scene": scene.scene_file_path,
		"camera": {"position": _v(from), "rotation_deg": _deg(camera.global_rotation), "fov": snappedf(camera.fov, 0.01)},
		"viewport": [get_viewport().get_visible_rect().size.x, get_viewport().get_visible_rect().size.y],
		"look": _v(dir), "plan_camera": _plan(from),
	}
	var player := _player_of(camera)
	if player:
		record["player"] = {"position": _v(player.global_position), "rotation_deg": _deg(player.global_rotation)}
		record["plan_player"] = _plan(player.global_position)
	if scene.has_method("playtest_stats"):
		record["run"] = scene.playtest_stats()
	var marker_at := from + dir * 3.0
	if hit.is_empty():
		record["hit"] = null
	else:
		marker_at = hit.position
		var collider: Object = hit.collider
		var info := {"point": _v(hit.position), "plan": _plan(hit.position), "normal": _v(hit.normal),
			"facing": _facing(hit.normal), "distance": snappedf(from.distance_to(hit.position), 0.01)}
		if collider is Node:
			info["collider"] = str(scene.get_path_to(collider))
			if collider is CollisionObject3D and hit.shape >= 0:
				var owner_id: int = collider.shape_find_owner(hit.shape)
				var shape_node = collider.shape_owner_get_owner(owner_id)
				if shape_node is Node:
					info["shape"] = str(shape_node.name)
		record["hit"] = info
	var marker := _marker(scene, marker_at, hit.get("normal", -dir), _count)
	_pending = {"record": record, "marker": marker}
	if quick:
		_save("z-fight")
		return
	get_tree().paused = true
	_title.text = "Note #%d  %s" % [_count, _where(record)]
	_edit.text = ""
	_panel.visible = true
	_edit.grab_focus()

func _submit(text: String) -> void:
	_panel.visible = false
	_edit.release_focus()
	_save(text.strip_edges() if text.strip_edges() != "" else "(no text)")

func _cancel() -> void:
	_panel.visible = false
	_edit.release_focus()
	if _pending.has("marker") and is_instance_valid(_pending.marker):
		_pending.marker.queue_free()
	_pending = {}
	_count -= 1
	get_tree().paused = false
	_show("Note cancelled")

func _save(text: String) -> void:
	var record: Dictionary = _pending.record
	record["note"] = text
	if not _open_session():
		get_tree().paused = false
		return
	_append(record)
	_pending = {}
	get_tree().paused = false
	_show("Note #%d saved: %s" % [record.n, text])

## Log a level event (a finish, a restart) into the open session. A finish opens one if needed.
func event(kind: String, data: Dictionary = {}) -> void:
	if DisplayServer.get_name() == "headless":
		return
	if _file == "" or _scene != get_tree().current_scene:
		if kind != "finish":
			return
	if not _open_session():
		return
	var record := {"type": kind, "time": Time.get_datetime_string_from_system()}
	record.merge(data)
	_append(record)

func _open_session() -> bool:
	var scene := get_tree().current_scene
	if _file != "" and _scene == scene:
		return true
	_scene = scene
	var stamp := Time.get_datetime_string_from_system().replace(":", "-").replace("T", "_")
	var name := scene.scene_file_path.get_file().get_basename() if scene.scene_file_path != "" else "scene"
	var base := "user://playtests"
	if OS.has_feature("editor"):
		base = ProjectSettings.globalize_path("res://").trim_suffix("/").get_base_dir().path_join("playtests")
	_dir = base.path_join(name).path_join(stamp)
	if DirAccess.make_dir_recursive_absolute(_dir) != OK:
		_show("Could not create %s" % _dir)
		_file = ""
		return false
	_file = _dir.path_join("notes.jsonl")
	var header := {"type": "session", "scene": scene.scene_file_path, "started": Time.get_datetime_string_from_system(),
		"version": str(ProjectSettings.get_setting("application/config/version", "")), "maps": []}
	for node in scene.find_children("*", "Node3D", true, false):
		if "local_map_file" in node and str(node.local_map_file) != "":
			var path := str(node.local_map_file)
			header.maps.append({"path": path, "md5": FileAccess.get_md5(path)})
	_append(header)
	print("PLAYTEST_NOTES: ", _dir)
	return true

func _append(record: Dictionary) -> void:
	var f := FileAccess.open(_file, FileAccess.READ_WRITE) if FileAccess.file_exists(_file) else FileAccess.open(_file, FileAccess.WRITE)
	if f == null:
		_show("Could not write %s" % _file)
		return
	f.seek_end()
	f.store_line(JSON.stringify(record))
	f.close()

func _marker(scene: Node, at: Vector3, normal: Vector3, n: int) -> Node3D:
	var root := scene.get_node_or_null("PlaytestNoteMarkers") as Node3D
	if root == null:
		root = Node3D.new()
		root.name = "PlaytestNoteMarkers"
		scene.add_child(root)
	var mark := Node3D.new()
	root.add_child(mark)
	mark.global_position = at
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = Color(1.0, 0.1, 0.8)
	mat.no_depth_test = true
	mat.render_priority = 10
	var dot := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.03
	sphere.height = 0.06
	sphere.material = mat
	dot.mesh = sphere
	mark.add_child(dot)
	var stick := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 0.012
	cyl.bottom_radius = 0.012
	cyl.height = 0.35
	cyl.material = mat
	stick.mesh = cyl
	mark.add_child(stick)
	var up := normal.normalized() if normal.length() > 0.01 else Vector3.UP
	stick.global_basis = Basis(Quaternion(Vector3.UP, up))
	stick.global_position = at + up * 0.175
	var label := Label3D.new()
	label.text = "#%d" % n
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	label.fixed_size = true
	label.pixel_size = 0.0015
	label.font_size = 28
	label.outline_size = 8
	label.modulate = Color(1.0, 0.4, 0.9)
	label.position = up * 0.45
	mark.add_child(label)
	return mark

func _player_of(camera: Camera3D) -> Node3D:
	var node: Node = camera
	while node != null:
		if node is CharacterBody3D:
			return node
		node = node.get_parent()
	return null

func _where(record: Dictionary) -> String:
	if record.hit == null:
		return "(nothing hit)"
	var p: Array = record.hit.plan
	return "hit %s face at plan (%.2f, %.2f, h %.2f), %.1f m away" % [record.hit.facing, p[0], p[1], p[2], record.hit.distance]

func _show(text: String) -> void:
	print("PLAYTEST_NOTES: ", text)
	_toast.text = text
	_toast_time = 4.0

static func _deg(r: Vector3) -> Array:
	return [snappedf(rad_to_deg(r.x), 0.01), snappedf(rad_to_deg(r.y), 0.01), snappedf(rad_to_deg(r.z), 0.01)]

static func _v(v: Vector3) -> Array:
	return [snappedf(v.x, 0.001), snappedf(v.y, 0.001), snappedf(v.z, 0.001)]

## Plan metres (x east, y north, h up), the convention of the level plans: Godot (x, h, -y).
static func _plan(v: Vector3) -> Array:
	return [snappedf(v.x, 0.001), snappedf(-v.z, 0.001), snappedf(v.y, 0.001)]

static func _facing(n: Vector3) -> String:
	if n.y > 0.7:
		return "up"
	if n.y < -0.7:
		return "down"
	var x := n.x
	var y := -n.z
	if absf(x) > absf(y):
		return "east" if x > 0 else "west"
	return "north" if y > 0 else "south"
