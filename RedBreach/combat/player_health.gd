extends Node
signal died
signal health_changed(value: float)
@export var max_health: float = 100.0
@export var invulnerability_seconds: float = 0.35
var health: float = 100.0
var _immunity: float = 0.0
var _flash: float = 0.0
@onready var player = get_parent()

func _enter_tree() -> void:
	if not EngineDebugger.is_active():
		$LifeChart.track_in_editor = false

func _ready() -> void:
	health = max_health
	refresh()

func is_alive() -> bool:
	return health > 0.0

func take_damage(amount: float) -> bool:
	if amount <= 0.0 or not is_alive() or _immunity > 0.0:
		return false
	health = maxf(0.0, health - amount)
	_immunity = invulnerability_seconds
	_flash = 0.55
	health_changed.emit(health)
	if health <= 0.0:
		$LifeChart.send_event("die")
	refresh()
	return true

func heal(amount: float) -> bool:
	if amount <= 0.0 or not is_alive() or health >= max_health:
		return false
	health = minf(max_health, health + amount)
	health_changed.emit(health)
	refresh()
	return true

func reset_health() -> void:
	health = max_health
	_immunity = 0.0
	_flash = 0.0
	$LifeChart.send_event("revive")
	health_changed.emit(health)
	refresh()

func _on_dead_entered() -> void:
	player.velocity = Vector3.ZERO
	player.pistol.cancel_handling()
	player._interaction_requested = false
	died.emit()

func _process(delta: float) -> void:
	_immunity = maxf(0.0, _immunity - delta)
	_flash = maxf(0.0, _flash - delta)
	refresh()

func refresh() -> void:
	$HUD/Health.text = "HEALTH  %03d" % ceili(health)
	$HUD/Health.modulate = Color(1, 0.35, 0.25) if health <= 30 else Color(0.8, 1, 0.9)
	$HUD/Damage.color.a = _flash * 0.35
	$HUD/Death.visible = not is_alive()
