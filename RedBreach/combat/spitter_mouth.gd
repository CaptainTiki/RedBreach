extends Area3D
## Shot-only layer 2. The shell receives ordinary damage when the jaws are closed.
@export var weak_point: bool = true
@export var enemy_path: NodePath = NodePath("../../..")
@onready var spitter = get_node(enemy_path)
func is_weak_point() -> bool:
	return weak_point and spitter.mouth_is_exposed()
func receive_shot(damage: float, point: Vector3, normal: Vector3, direction: Vector3) -> bool:
	return spitter.receive_mouth_shot(damage, point, normal, direction) if weak_point else spitter.receive_shot(damage, point, normal, direction)
