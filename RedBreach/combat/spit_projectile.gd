extends CharacterBody3D
## A swept sphere prevents a fast glob from skipping a thin wall or player.
@export var speed: float = 35.0
@export var damage: float = 20.0
@export var lifetime: float = 3.0
var _age: float = 0.0
var _resolved := false
var _source: CharacterBody3D
func _ready() -> void:
	add_to_group("combat_projectiles")
func launch(shooter: CharacterBody3D, direction: Vector3) -> void:
	_source = shooter
	add_collision_exception_with(shooter)
	velocity = direction.normalized() * speed
func despawn() -> void:
	_resolved = true
	set_physics_process(false)
	queue_free()
func _physics_process(delta: float) -> void:
	if _resolved:
		return
	_age += delta
	if _age >= lifetime:
		despawn()
		return
	var collision := move_and_collide(velocity * delta)
	if collision == null:
		return
	_resolved = true
	var body: Object = collision.get_collider()
	var hits_player: bool = body is Node and body.has_node("Health") and body.has_method("is_alive")
	var excluded: Array[RID] = []
	if is_instance_valid(_source):
		excluded.append(_source.get_rid())
	if hits_player:
		excluded.append(body.get_rid())
		body.get_node("Health").take_damage(damage)
	get_tree().call_group("combat_effects", "spawn_spit_impact", collision.get_position(), collision.get_normal(), excluded, hits_player)
	despawn()
