extends RefCounted
## Physics-time measurements: encounter windows may overlap; the run union never double counts.
var elapsed: float = 0.0
var active_seconds: float = 0.0
var quiet_seconds: float = 0.0
var moving_seconds: float = 0.0
var distance: float = 0.0
var modes: Dictionary = {}
var quiet_intervals: Array = []
var _was_quiet: bool = false
var encounters: Dictionary = {}
var shots: int = 0
var incoming_damage: float = 0.0

func tick(delta: float, displacement: Vector3, mode: String) -> void:
	elapsed += delta
	var travelled := Vector2(displacement.x, displacement.z).length()
	distance += travelled
	if travelled > 0.001:
		moving_seconds += delta
	modes[mode] = float(modes.get(mode, 0.0)) + delta
	var fighting := false
	for entry in encounters.values():
		if entry.started >= 0.0 and entry.cleared < 0.0:
			fighting = true
	if fighting:
		active_seconds += delta
		_was_quiet = false
	else:
		quiet_seconds += delta
		if not _was_quiet: quiet_intervals.append({"start": elapsed - delta, "end": elapsed})
		else: quiet_intervals[-1].end = elapsed
		_was_quiet = true

func register(id: String, label: String, count: int) -> void:
	encounters[id] = {"label": label, "count": count, "started": -1.0, "first_spawn": -1.0, "first_damage": -1.0, "cleared": -1.0}

func mark(id: String, event: String) -> void:
	if encounters.has(id) and float(encounters[id][event]) < 0.0:
		encounters[id][event] = elapsed

func cleared_count() -> int:
	var count := 0
	for entry in encounters.values():
		if entry.cleared >= 0.0: count += 1
	return count

func snapshot() -> Dictionary:
	return {"elapsed": elapsed, "active_seconds": active_seconds, "quiet_seconds": quiet_seconds,
		"moving_seconds": moving_seconds, "distance": distance, "modes": modes.duplicate(true),
		"encounters": encounters.duplicate(true), "quiet_intervals": quiet_intervals.duplicate(true), "shots": shots, "incoming_damage": incoming_damage}
