extends StaticBody3D

@export var max_health: float = 100.0
@export var recovery_seconds: float = 2.0
var health: float = 100.0
var hit_count: int = 0
var flash: Tween
var _recovery: float = 0.0
var _label: String = "TARGET"

func _ready() -> void:
	add_to_group("gym_targets")
	# Repeated map saves must not append another copy of the runtime readout.
	_label = $Readout.text.get_slice("\n", 0)
	reset_target()

func reset_target() -> void:
	if flash:
		flash.kill()
	health = max_health
	hit_count = 0
	_recovery = 0.0
	$Plate.scale = Vector3.ONE
	$Plate.transparency = 0.0
	_refresh()

func register_hit(damage: float = 0.0) -> bool:
	if health <= 0.0:
		return false
	hit_count += 1
	health = maxf(0.0, health - maxf(0.0, damage))
	if flash:
		flash.kill()
	$Plate.scale = Vector3.ONE * 0.88
	flash = create_tween()
	flash.tween_property($Plate, "scale", Vector3.ONE, 0.18)
	if health <= 0.0:
		_recovery = recovery_seconds
		$Plate.transparency = 0.7
	_refresh()
	return true

func _physics_process(delta: float) -> void:
	if _recovery <= 0.0:
		return
	_recovery = maxf(0.0, _recovery - delta)
	if _recovery <= 0.0:
		health = max_health
		$Plate.transparency = 0.0
		_refresh()

func _refresh() -> void:
	$Readout.text = _label + ("\nDOWN / resetting" if health <= 0.0 else "\n%d HP" % roundi(health))
