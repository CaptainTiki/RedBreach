extends SceneTree
## Generic, marker-driven validator for ANY built map scene.
##
##   godot --headless --path RedBreach --script res://tools/validate_markers.gd -- res://kit/kit_lab.tscn
##
## It reads validation markers placed in TrenchBroom (see mapping/fgd/ and
## tools/trenchbroom/RedBreach/RedBreach.fgd) from the built scene:
##   rb_route  waypoints walked in index order, forward then back, standing or
##             crouched, climbing and descending stairs with the real player;
##             posture "climb" takes the nearest ladder (rb_ladder) with the
##             player's own climb; oneway=1 routes are walked forward only
##   rb_probe  stand_clear / crouch_only / headroom
##   rb_nav    bug navigation pairs: connect or blocked
##   rb_dark   a deliberately dark zone: the light floor is waived within radius
## It also checks every FuncGodotMap with collision: brush count equals
## collision count, and no surface fell back to the default texture; and the
## LIGHT FLOOR: no walkable point is darker than LIGHT_MIN unless an rb_dark
## zone says it is meant to be.
## A map gets validation by placing markers, not by writing a script.

const STEP := 1.0 / 120.0
## The light floor (user rule, 2026-09-25): "no darker than" by default; go
## darker only on purpose (hiding places, broken lights). Measured as scalar
## illuminance at bug height (1.0 m): every light that reaches the point with
## Godot's omni falloff, occluded by geometry when the light casts shadows,
## plus ambient. Calibrated in docs/kit-sheet.md.
const LIGHT_MIN := 0.35
const LIGHT_HEIGHT := 1.0
const SAMPLE_SPACING := 1.2
var scene: Node
var player: CharacterBody3D
var checks := 0
var failures := 0

func _initialize() -> void: call_deferred("run")

func expect(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		print("FAIL: ", message)

func props(marker: Node) -> Dictionary:
	return marker.get("func_godot_properties") if marker.get("func_godot_properties") != null else {}

func map_brush_count(path: String) -> int:
	var lines := FileAccess.get_file_as_string(path).split("\n")
	var brushes := 0
	for i in lines.size() - 1:
		if lines[i].strip_edges() == "{" and not lines[i + 1].strip_edges().begins_with("\""):
			brushes += 1
	return brushes

func capsule_clear(space: PhysicsDirectSpaceState3D, foot: Vector3, height: float) -> bool:
	var shape := CapsuleShape3D.new()
	shape.radius = 0.3
	shape.height = height
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = shape
	q.transform = Transform3D(Basis.IDENTITY, foot + Vector3.UP * (height / 2.0 + 0.04))
	q.exclude = [player.get_rid()]
	return space.intersect_shape(q, 1).is_empty()

func walk_leg(target: Vector3, crouch: bool, label: String, y_lo: float, y_hi: float) -> bool:
	if crouch:
		Input.action_press("gym_crouch")
	else:
		Input.action_release("gym_crouch")
	var start := player.global_position
	var budget := int((Vector2(start.x, start.z).distance_to(Vector2(target.x, target.z)) / (2.5 if crouch else 5.0) * 3.0 + 3.0) / STEP)
	for i in budget:
		var to := target - player.global_position
		var flat := Vector2(to.x, to.z)
		if flat.length() < 0.45 and absf(to.y) < 0.45:
			player.test_direction = Vector2.ZERO
			return true
		player.rotation.y = atan2(-flat.x, -flat.y)
		player.test_direction = Vector2(0, -1)
		await physics_frame
		var y := player.global_position.y
		if y > y_hi + 0.35 or y < y_lo - 0.6:
			player.test_direction = Vector2.ZERO
			expect(false, "%s left its height band at %v (allowed %.2f..%.2f)" % [label, player.global_position, y_lo, y_hi])
			return false
	player.test_direction = Vector2.ZERO
	expect(false, "%s stalled at %v short of %v" % [label, player.global_position, target])
	return false

## Inside a progression kit piece (a door's leaf, a switch, the fan): its runtime parts are not map brushes.
func in_kit(node: Node, stop: Node) -> bool:
	var n := node.get_parent()
	while n != null and n != stop:
		if n.is_in_group("progression_kit"):
			return true
		n = n.get_parent()
	return false


## A progression kit piece (door, switch, card, fan, drawbridge) by its id.
func find_kit(id: String) -> Node:
	for node in scene.get_tree().get_nodes_in_group("progression_kit"):
		if str(node.get("kit_id")) == id:
			return node
	return null


## Put the player's eye (the camera kit pieces judge sides from) over a foot position.
func put_eye(foot: Vector3) -> void:
	player.relocate(Transform3D(Basis.IDENTITY, foot + Vector3.UP * 0.05))
	player.camera.global_position = foot + Vector3.UP * 1.6


## Wait until nothing in the kit is moving (a door opening, the fan spinning down, the section lowering).
func settle(limit: float = 20.0) -> void:
	for i in int(limit / STEP):
		var busy := false
		for node in scene.get_tree().get_nodes_in_group("progression_kit"):
			if node.has_method("busy") and node.busy():
				busy = true
				break
		if not busy and i > 10:
			return
		await physics_frame


## Use kit pieces on arriving at a route marker, as the player would: within reach, from where the player stands.
func use_kits(ids: String, label: String) -> bool:
	for id in ids.split(",", false):
		var kit := find_kit(id)
		if kit == null:
			expect(false, "%s: no kit piece %s" % [label, id])
			return false
		var reach: Vector3 = kit.use_point() - (player.global_position + Vector3.UP * 1.4)
		if Vector2(reach.x, reach.z).length() > 2.6 or absf(reach.y) > 2.8:
			expect(false, "%s: %s is out of reach (%.1f m) from %v" % [label, id, reach.length(), player.global_position])
			return false
		var used: bool = kit.use() or kit.use_done()
		expect(used, "%s: %s would not work from %v (%s)" % [label, id, player.global_position,
			kit.use_prompt() if kit.has_method("use_prompt") else ""])
		if not used:
			return false
		await settle()
	return true


func climb_leg(a: Vector3, b: Vector3, label: String) -> bool:
	Input.action_release("gym_crouch")
	var ladder: Node3D = null
	var best := 1e9
	for node in scene.find_children("*", "StaticBody3D", true, false):
		if node.has_method("climb_path"):
			var d := Vector2(node.global_position.x - a.x, node.global_position.z - a.z).length()
			if d < best:
				best = d
				ladder = node
	if ladder == null or best > 2.5 or not player.has_method("begin_climb"):
		expect(false, "%s: no ladder within reach of %v" % [label, a])
		return false
	for i in 6:
		await physics_frame
	if not ladder.start_climb(player):
		expect(false, "%s: the climb would not start at %v" % [label, player.global_position])
		return false
	for i in int(30.0 / STEP):
		await physics_frame
		if not player.climbing():
			break
	if player.climbing():
		expect(false, "%s: still climbing at %v" % [label, player.global_position])
		return false
	return await walk_leg(b, false, label + " (off the ladder)", minf(player.global_position.y, b.y), maxf(player.global_position.y, b.y))

func run() -> void:
	var args := OS.get_cmdline_user_args()
	var path: String = args[0] if args.size() > 0 else "res://kit/kit_lab.tscn"
	scene = load(path).instantiate()
	root.add_child(scene)
	for node in scene.find_children("*", "CharacterBody3D", true, false):
		# The gym player, or a mission player derived from it.
		if node.get_script() and "test_direction" in node and node.has_method("relocate"):
			player = node
	if player == null:
		print("FAIL: no GymPlayer in ", path)
		quit(1)
		return
	player.set_physics_process(false)
	player.pistol.audio_enabled = false
	for i in 4:
		await physics_frame
	var space := player.get_world_3d().direct_space_state

	# Geometry: every FuncGodotMap with collision matches its source map.
	for map_node in scene.find_children("*", "", true, false):
		if not map_node is FuncGodotMap:
			continue
		# Brush geometry only: entities with their own scripts (ladders) bring their own shapes and meshes.
		var shapes := 0
		for shape in map_node.find_children("*", "CollisionShape3D", true, false):
			if shape.get_parent().get_script() == null and not in_kit(shape, map_node):
				shapes += 1
		if shapes > 0 and map_node.local_map_file != "":
			var brushes := map_brush_count(map_node.local_map_file)
			expect(shapes == brushes, "%s: %d collision shapes for %d brushes" % [map_node.name, shapes, brushes])
		for mesh_instance in map_node.find_children("*", "MeshInstance3D", true, false):
			if mesh_instance.get_parent().get_script() != null or in_kit(mesh_instance, map_node):
				continue
			var mesh: Mesh = mesh_instance.mesh
			for s in mesh.get_surface_count():
				var m := mesh.surface_get_material(s)
				var ok: bool = m is StandardMaterial3D and m.albedo_texture != null \
					and not m.albedo_texture.resource_path.contains("default_texture")
				expect(ok, "%s surface %s has no real material" % [map_node.name, mesh.surface_get_name(s)])

	var routes := {}
	var oneways := {}
	var navs := {}
	var probes := []
	var darks := []
	for marker in scene.find_children("*", "Marker3D", true, false):
		var p := props(marker)
		match str(p.get("classname", "")):
			"rb_route":
				routes.get_or_add(str(p.get("route", "main")), []).append([int(p.get("index", 0)), marker.global_position, str(p.get("posture", "stand")), str(p.get("use", ""))])
				if int(p.get("oneway", 0)) == 1:
					oneways[str(p.get("route", "main"))] = true
			"rb_probe":
				probes.append([str(p.get("kind", "stand_clear")), float(p.get("min", 0.0)), marker.global_position, str(p.get("id", ""))])
			"rb_nav":
				navs.get_or_add(str(p.get("pair", "")), {})[str(p.get("end", "a"))] = [marker.global_position, str(p.get("expect", "connect"))]
			"rb_dark":
				darks.append([marker.global_position, float(p.get("radius", 4.0)), str(p.get("reason", ""))])
	print("MARKERS: %d routes, %d probes, %d nav pairs" % [routes.size(), probes.size(), navs.size()])
	expect(routes.size() + probes.size() + navs.size() > 0, "no validation markers found in " + path)

	# Probes.
	for probe in probes:
		var kind: String = probe[0]
		var at: Vector3 = probe[2]
		match kind:
			"stand_clear":
				expect(capsule_clear(space, at, 1.8), "stand_clear blocked at %v" % at)
			"crouch_only":
				expect(not capsule_clear(space, at, 1.8), "crouch_only: a standing player fits at %v" % at)
				expect(capsule_clear(space, at, 1.1), "crouch_only: a crouched player is blocked at %v" % at)
			"headroom":
				var q := PhysicsRayQueryParameters3D.create(at + Vector3.UP * 0.1, at + Vector3.UP * 30.0)
				q.exclude = [player.get_rid()]
				var hit := space.intersect_ray(q)
				var clear: float = (hit.position.y - at.y) if not hit.is_empty() else 999.0
				expect(clear >= probe[1], "headroom %.2f < %.2f at %v" % [clear, probe[1], at])
			"refuse":
				# At level start this kit piece must not open for a player standing here (a lock, a card, a side).
				var kit := find_kit(probe[3])
				if kit == null:
					expect(false, "refuse probe: no kit piece %s" % probe[3])
				else:
					put_eye(at)
					expect(not kit.use(), "refuse: %s opened for a player at %v at level start" % [probe[3], at])
			"blocked_crouch":
				expect(not capsule_clear(space, at, 1.1), "blocked_crouch: a crouched player fits at %v at level start" % at)
			_:
				expect(false, "unknown probe kind %s at %v" % [kind, at])

	# A level with progression (doors with rules, switches, cards) is walked as a player plays it: each route
	# starts from a reset level and uses its kit pieces where the route says. Otherwise doors are opened first:
	# door behaviour has its own validator, and here a door only needs to let the player through.
	var progression: Node = scene.get_tree().get_first_node_in_group("progression")
	var doors := 0
	for door in ([] if progression != null else scene.find_children("*", "", true, false)):
		if door.has_method("request_toggle") and door.has_method("state_name"):
			for i in 30:
				if door.state_name() != "Starting":
					break
				await physics_frame
			if door.state_name() == "Closed":
				door.request_toggle()
				doors += 1
	for i in 150:
		await physics_frame
	if doors > 0:
		print("DOORS: opened %d" % doors)

	# Routes, walked by the real player: forward, then back.
	player.set_physics_process(true)
	player.control_override = true
	for route_name in routes:
		var points: Array = routes[route_name]
		points.sort_custom(func(a, b): return a[0] < b[0])
		for direction in ["forward", "back"]:
			if direction == "back" and oneways.get(route_name, false):
				continue
			var seq: Array = points if direction == "forward" else points.duplicate()
			if direction == "back":
				seq.reverse()
			if progression != null and direction == "forward":
				# A fresh level: doors shut, cards back, switches up; the airlock opens when the level is ready.
				if scene.has_method("reset_encounter"):
					scene.reset_encounter()
				else:
					progression.reset()
			player.relocate(Transform3D(Basis.IDENTITY, seq[0][1] + Vector3.UP * 0.05))
			for i in 6:
				await physics_frame
			if progression != null and direction == "forward":
				for i in int((progression.start_delay + 0.3) / STEP):
					await physics_frame
				await settle()
				if seq[0][3] != "" and not await use_kits(seq[0][3], "route %s at its start" % route_name):
					continue
			var route_ok := true
			for i in range(1, seq.size()):
				var a: Vector3 = seq[i - 1][1]
				var b: Vector3 = seq[i][1]
				var crouch: bool = seq[i][2] == "crouch" or seq[i - 1][2] == "crouch"
				var label := "route %s %s leg %d->%d" % [route_name, direction, seq[i - 1][0], seq[i][0]]
				var ok: bool
				# A climb marker is the point AFTER the ladder, walking forward.
				if (direction == "forward" and seq[i][2] == "climb") or (direction == "back" and seq[i - 1][2] == "climb"):
					ok = await climb_leg(a, b, label)
				else:
					ok = await walk_leg(b, crouch, label, minf(a.y, b.y), maxf(a.y, b.y))
				expect(ok, label)
				if not ok:
					route_ok = false
					break
				if direction == "forward" and seq[i][3] != "":
					if not await use_kits(seq[i][3], label):
						route_ok = false
						break
			# A route of a level with progression ends where the level says it is finished (freight v2: in the lift).
			if progression != null and direction == "forward" and route_ok and scene.has_method("playtest_stats") and "finish" in scene:
				var end: Vector3 = seq[seq.size() - 1][1]
				if Vector2(end.x, -end.z).distance_to(scene.finish) < 2.5:
					for i in 10:
						await physics_frame
					expect(scene.playtest_stats().get("finished", false), "route %s reached the end but the level did not finish" % route_name)
	Input.action_release("gym_crouch")
	player.control_override = false

	# Navigation pairs.
	if navs.size() > 0:
		var map_rid := player.get_world_3d().navigation_map
		for i in 10:
			await physics_frame
		expect(NavigationServer3D.map_get_regions(map_rid).size() > 0, "rb_nav markers present but no navigation is baked")
		for pair in navs:
			var ends: Dictionary = navs[pair]
			if not (ends.has("a") and ends.has("b")):
				expect(false, "nav pair %s needs ends a and b" % pair)
				continue
			var a: Vector3 = ends["a"][0]
			var b: Vector3 = ends["b"][0]
			var want: String = ends["a"][1]
			var path_points := NavigationServer3D.map_get_path(map_rid, a, b, true)
			var reached := path_points.size() > 0 and path_points[path_points.size() - 1].distance_to(b) < 1.0
			if want == "connect":
				expect(reached, "nav %s should connect but ends at %s" % [pair, path_points[path_points.size() - 1] if path_points.size() > 0 else "nothing"])
			else:
				expect(not reached, "nav %s should be blocked but connects" % pair)

	# The light floor.
	await light_floor(space, darks)

	print("MARKER_QA: %d checks; %d failures" % [checks, failures])
	quit(0 if failures == 0 else 1)


func omni_attenuation(distance: float, light_range: float, decay: float) -> float:
	# Godot 4's omni falloff (scene_forward_lights_inc.glsl).
	var nd := distance / light_range
	nd *= nd
	nd *= nd
	nd = maxf(1.0 - nd, 0.0)
	nd *= nd
	return nd * pow(maxf(distance, 0.0001), -decay)

func luminance(c: Color) -> float:
	return 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b

func illuminance(space: PhysicsDirectSpaceState3D, at: Vector3, omnis: Array, suns: Array, ambient: float) -> float:
	var total := ambient
	for light in omnis:
		var lp: Vector3 = light.global_position
		var dist := at.distance_to(lp)
		if dist >= light.omni_range:
			continue
		if light.shadow_enabled:
			var q := PhysicsRayQueryParameters3D.create(at, lp)
			q.exclude = [player.get_rid()]
			if not space.intersect_ray(q).is_empty():
				continue
		total += light.light_energy * luminance(light.light_color) * omni_attenuation(dist, light.omni_range, light.omni_attenuation)
	for sun in suns:
		var q := PhysicsRayQueryParameters3D.create(at, at + sun.global_basis.z * 200.0)
		q.exclude = [player.get_rid()]
		if space.intersect_ray(q).is_empty():
			total += sun.light_energy * luminance(sun.light_color)
	return total

func light_floor(space: PhysicsDirectSpaceState3D, darks: Array) -> void:
	var region: NavigationRegion3D = null
	for node in scene.find_children("*", "NavigationRegion3D", true, false):
		region = node
	if region == null or region.navigation_mesh == null:
		print("LIGHT: no navigation mesh to sample; light floor skipped")
		return
	var omnis := []
	var suns := []
	for light in scene.find_children("*", "Light3D", true, false):
		if not light.is_visible_in_tree() or light.light_energy <= 0.0:
			continue
		if light is OmniLight3D:
			omnis.append(light)
		elif light is DirectionalLight3D:
			suns.append(light)
	var ambient := 0.0
	for env_node in scene.find_children("*", "WorldEnvironment", true, false):
		var env: Environment = env_node.environment
		if env and env.ambient_light_source == Environment.AMBIENT_SOURCE_COLOR:
			ambient = env.ambient_light_energy * luminance(env.ambient_light_color)
	# Sample every navigation polygon on a grid: where the player and the bugs walk.
	var mesh := region.navigation_mesh
	var verts := mesh.get_vertices()
	var points: Array[Vector3] = []
	for pi in mesh.get_polygon_count():
		var poly := mesh.get_polygon(pi)
		for k in range(1, poly.size() - 1):
			var a: Vector3 = region.global_transform * verts[poly[0]]
			var b: Vector3 = region.global_transform * verts[poly[k]]
			var c: Vector3 = region.global_transform * verts[poly[k + 1]]
			var area := (b - a).cross(c - a).length() / 2.0
			var n := maxi(1, int(ceil(sqrt(area) / SAMPLE_SPACING)))
			for i in n:
				for j in n - i:
					var u := (i + 1.0 / 3.0) / n
					var v := (j + 1.0 / 3.0) / n
					points.append(a + (b - a) * u + (c - a) * v)
	var dark_points := []
	var values: Array[float] = []
	var waived := 0
	for p in points:
		var at := p + Vector3.UP * LIGHT_HEIGHT
		var e := illuminance(space, at, omnis, suns, ambient)
		values.append(e)
		if e >= LIGHT_MIN:
			continue
		var in_dark := false
		for d in darks:
			if Vector2(p.x, p.z).distance_to(Vector2(d[0].x, d[0].z)) <= d[1] and absf(p.y - d[0].y) < 2.5:
				in_dark = true
		if in_dark:
			waived += 1
		else:
			dark_points.append([e, p])
	values.sort()
	var median: float = values[values.size() / 2] if values.size() > 0 else 0.0
	print("LIGHT: %d walkable samples; ambient %.3f; min %.3f, 10th percentile %.3f, median %.3f; floor %.2f; %d waived by rb_dark" % [
		points.size(), ambient, values[0] if values.size() > 0 else 0.0,
		values[values.size() / 10] if values.size() > 0 else 0.0, median, LIGHT_MIN, waived])
	dark_points.sort_custom(func(x, y): return x[0] < y[0])
	for i in mini(8, dark_points.size()):
		print("  too dark: %.3f at %v" % [dark_points[i][0], dark_points[i][1]])
	expect(dark_points.is_empty(), "%d walkable points are darker than the light floor %.2f with no rb_dark zone" % [dark_points.size(), LIGHT_MIN])
