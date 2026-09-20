extends Area3D
@export_enum("Health", "Ammo") var kind: int = 0
@export var amount: int = 25
var available := true
var _phase := 0.0

func _ready() -> void:
	add_to_group("combat_pickups")
	body_entered.connect(try_collect)
	$Label.text = "+%d %s" % [amount, "HEALTH" if kind == 0 else "AMMO"]
	var material := StandardMaterial3D.new()
	material.albedo_color = Color(0.9, 0.2, 0.23) if kind == 0 else Color(0.95, 0.68, 0.16)
	$Visual.material_override = material

func try_collect(body: Node3D) -> bool:
	if not available or not body.has_method("is_alive") or not body.is_alive():
		return false
	var accepted: bool = body.get_node("Health").heal(amount) if kind == 0 else body.pistol.add_ammo(amount)
	if accepted:
		available = false
		hide()
	return accepted

func reset_pickup() -> void:
	available = true
	show()

func _process(delta: float) -> void:
	_phase += delta
	$Visual.rotation.y += delta
	$Visual.position.y = 0.55 + sin(_phase * 2.0) * 0.08
