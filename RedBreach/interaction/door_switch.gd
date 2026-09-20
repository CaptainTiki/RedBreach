extends StaticBody3D
## A switch can target any door exposing request_toggle and interaction_prompt.
@export_node_path("Node3D") var door_path: NodePath = NodePath("..")
@onready var door: Node = get_node(door_path)

func get_interaction_prompt() -> String:
	return door.interaction_prompt()

func interact() -> bool:
	return door.request_toggle()
