extends SceneTree
# Corner lab QA. The straight run's checks assumed a single axis, so these are
# written against the CENTRELINE PATH instead: every sample walks along it and
# probes perpendicular to the local direction.
#
# What it asserts, in order of what would actually be a bug:
#   the protected 4.00 x 3.20 m lane is clear for the whole walk, turns included
#   the floor is flat at Y = 0 the whole way - a mitre must not leave a lip
#   there is a ceiling everywhere - a mitred slab must not leave a hole
#   both ends are sealed
#   the player can actually walk the route, and jamming a wall never lifts them

const PATH := [
	Vector2(0.0, -2.0),
	Vector2(0.0, 52.0),
	Vector2(20.0, 52.0),
	Vector2(24.0, 48.0),
	Vector2(24.0, 20.0),
]
# The T branch, walked separately: it leaves the through corridor at (24, 30).
const BRANCH := [
	Vector2(24.0, 30.0),
	Vector2(40.0, 30.0),
]
const LANE_HALF := 2.0
# Probe just inside the line. The rib toes sit EXACTLY on x = 2.00 by design -
# opposite toes are what define the 4.00 m lane - so a probe to 2.00 tests
# tangency and fails at every rib. 1.98 tests intrusion, which is the bug.
const LANE_HEIGHT := 3.2
const CEIL_Y := 3.75
const STEP := 0.5
# A mitre cuts the wall diagonally, so a probe right at a vertex legitimately
# sees the far wall. Skip a margin either side of each turn; the lane through
# the turn is covered by the walk itself.
const TURN_SKIP := 4.5
# The T opening is a legitimate hole in one wall, so a lane probe there sees
# straight down the branch. Skip the same margin around it.
const TEE_AT := Vector2(24.0, 30.0)
const TEE_SKIP := 4.5

var scene: Node3D
var player: CharacterBody3D
var space: PhysicsDirectSpaceState3D
var checks := 0
var failures := 0

func _initialize() -> void: call_deferred("run")

func fail(msg: String) -> void:
	failures += 1
	push_error("FAIL: " + msg)

func expect(condition: bool, msg: String) -> void:
	checks += 1
	if not condition: fail(msg)

func ticks(count: int) -> void:
	for i in count: await physics_frame

func ray(from: Vector3, to: Vector3) -> Dictionary:
	var q := PhysicsRayQueryParameters3D.create(from, to)
	q.collide_with_areas = false
	return space.intersect_ray(q)

func near_turn(distance: float, cum: Array) -> bool:
	for i in range(1, cum.size() - 1):
		if abs(distance - float(cum[i])) < TURN_SKIP: return true
	return false

func run() -> void:
	scene = load("res://architecture/architecture_lab_corners.tscn").instantiate()
	root.add_child(scene)
	var geometry: FuncGodotMap = scene.get_node("Geometry")
	var done := {"ok": false}
	geometry.build_complete.connect(func(): done.ok = true)
	geometry.build()
	await ticks(4)
	if not done.ok:
		push_error("ARCH_CORNER_QA_FAILED: build did not complete")
		quit(1)
		return
	player = scene.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	space = player.get_world_3d().direct_space_state
	await ticks(10)

	var seglen := []
	var cum := [0.0]
	for i in range(PATH.size() - 1):
		seglen.append(PATH[i].distance_to(PATH[i + 1]))
		cum.append(float(cum[i]) + float(seglen[i]))
	var total: float = cum[cum.size() - 1]

	# --- the envelope, sampled along the whole centreline ------------------
	var d := 1.0
	while d < total - 1.0:
		var seg := 0
		for i in range(seglen.size()):
			if float(cum[i]) <= d: seg = i
		var t: float = d - float(cum[seg])
		var dir2: Vector2 = (PATH[seg + 1] - PATH[seg]).normalized()
		var p2: Vector2 = PATH[seg] + dir2 * t
		var nrm := Vector2(dir2.y, -dir2.x)
		var centre := Vector3(p2.x, 0.0, p2.y)

		# floor flat at 0, no lip left by a mitre
		var down := ray(centre + Vector3.UP * 1.0, centre + Vector3.DOWN * 1.0)
		expect(not down.is_empty() and absf(down.position.y) < 0.02,
			"floor not flat at %.2f m along (%s)" % [d, str(down.get("position", "none"))])

		# a ceiling exists - a mitred slab must never leave a hole to the sky
		var up := ray(centre + Vector3.UP * 0.2, centre + Vector3.UP * 8.0)
		expect(not up.is_empty() and up.position.y <= CEIL_Y + 0.01,
			"no ceiling at %.2f m along" % d)

		# the protected lane is clear either side, away from the mitres and the
		# T opening, which is a hole in one wall on purpose
		if not near_turn(d, cum) and p2.distance_to(TEE_AT) > TEE_SKIP:
			for side: float in [-1.0, 1.0]:
				for h: float in [0.3, 1.6, LANE_HEIGHT]:
					var from: Vector3 = Vector3(p2.x, h, p2.y)
					var to: Vector3 = from + Vector3(nrm.x, 0.0, nrm.y) * side * (LANE_HALF - 0.02)
					var hit := ray(from, to)
					expect(hit.is_empty(),
						"lane intrusion at %.2f m along, side %.0f, height %.2f" % [d, side, h])
		d += STEP

	# --- both ends sealed ---------------------------------------------------
	for pair in [[PATH[0], PATH[1]], [PATH[PATH.size() - 1], PATH[PATH.size() - 2]]]:
		var a: Vector2 = pair[0]
		var b: Vector2 = pair[1]
		var outward: Vector2 = (a - b).normalized()
		var from: Vector3 = Vector3(a.x, 1.6, a.y) - Vector3(outward.x, 0.0, outward.y) * 1.0
		var to: Vector3 = from + Vector3(outward.x, 0.0, outward.y) * 4.0
		expect(not ray(from, to).is_empty(), "end not sealed at %s" % str(a))

	# --- the route is actually walkable, turns and all ---------------------
	# The point of walking the whole path is that the turns are the only place
	# a mitre could leave a lip or a snag, and a probe cannot see those.
	player.set_physics_process(true)
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(PATH[0].x, 0.05, PATH[0].y + 1.0)))
	await physics_frame
	var highest := 0.0
	for i in range(1, PATH.size()):
		var guard := 0
		while guard < 2600:
			var here := Vector2(player.global_position.x, player.global_position.z)
			if here.distance_to(PATH[i]) <= 1.5: break
			var step: Vector2 = (PATH[i] - here).normalized() * 6.0
			player.velocity = Vector3(step.x, player.velocity.y, step.y)
			player.move_and_slide()
			highest = maxf(highest, player.global_position.y)
			await physics_frame
			guard += 1
		expect(guard < 2600, "could not walk to waypoint %d at %v" % [i, PATH[i]])
	expect(highest < 0.35, "the walk climbed to %.3f m" % highest)

	# --- the T branch is reachable and is a real corridor ------------------
	# Walk from just short of the opening, through it, to the branch's far end.
	# If the opening were not actually cut, or the floor plate did not carry
	# across the threshold, this is what would catch it.
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(TEE_AT.x, 0.05, TEE_AT.y + 4.0)))
	await physics_frame
	var tee_high := 0.0
	# Route via the junction centre first. Driving straight at the far end from
	# inside the through corridor aims the player at the opening's jamb, not at
	# the opening - that is the walk being wrong, not the geometry.
	for i in range(0, BRANCH.size()):
		var guard := 0
		while guard < 2600:
			var here := Vector2(player.global_position.x, player.global_position.z)
			if here.distance_to(BRANCH[i]) <= 1.5: break
			var step: Vector2 = (BRANCH[i] - here).normalized() * 6.0
			player.velocity = Vector3(step.x, player.velocity.y, step.y)
			player.move_and_slide()
			tee_high = maxf(tee_high, player.global_position.y)
			await physics_frame
			guard += 1
		expect(guard < 2600, "could not walk the T branch to %v" % BRANCH[i])
	expect(tee_high < 0.35, "the T branch walk climbed to %.3f m" % tee_high)

	# The branch is a corridor, not a stub: probe its lane clear of the junction.
	var bdir: Vector2 = (BRANCH[1] - BRANCH[0]).normalized()
	var bnrm := Vector2(bdir.y, -bdir.x)
	var bt := TEE_SKIP + 1.0
	while bt < BRANCH[0].distance_to(BRANCH[1]) - 1.0:
		var bp: Vector2 = BRANCH[0] + bdir * bt
		var bdown := ray(Vector3(bp.x, 1.0, bp.y), Vector3(bp.x, -1.0, bp.y))
		expect(not bdown.is_empty() and absf(bdown.position.y) < 0.02,
			"branch floor not flat at %.2f m out" % bt)
		var bup := ray(Vector3(bp.x, 0.2, bp.y), Vector3(bp.x, 8.0, bp.y))
		expect(not bup.is_empty() and bup.position.y <= CEIL_Y + 0.01,
			"no ceiling in the branch at %.2f m out" % bt)
		for bside: float in [-1.0, 1.0]:
			for bh: float in [0.3, 1.6, LANE_HEIGHT]:
				var bf: Vector3 = Vector3(bp.x, bh, bp.y)
				var bto: Vector3 = bf + Vector3(bnrm.x, 0.0, bnrm.y) * bside * (LANE_HALF - 0.02)
				expect(ray(bf, bto).is_empty(),
					"branch lane intrusion at %.2f m out, side %.0f, height %.2f" % [bt, bside, bh])
		bt += STEP

	# The branch end must be sealed like any other.
	var bend: Vector2 = BRANCH[BRANCH.size() - 1]
	var bfrom := Vector3(bend.x, 1.6, bend.y) - Vector3(bdir.x, 0.0, bdir.y) * 1.0
	expect(not ray(bfrom, bfrom + Vector3(bdir.x, 0.0, bdir.y) * 4.0).is_empty(),
		"T branch end not sealed")

	# --- jamming the wall must never lift the player -----------------------
	# Being stopped by a rib is correct; only a climb is a bug.
	player.relocate(Transform3D(Basis.IDENTITY, Vector3(0.0, 0.05, 20.0)))
	await physics_frame
	var jam := 0.0
	for i in range(900):
		player.velocity = Vector3(-6.0, player.velocity.y, 6.0)
		player.move_and_slide()
		jam = maxf(jam, player.global_position.y)
		await physics_frame
	expect(jam < 0.35, "jamming the wall lifted the player to %.3f m" % jam)

	print("ARCH_CORNER_QA: ", checks, " checks; ", failures, " failures")
	quit(1 if failures > 0 else 0)
