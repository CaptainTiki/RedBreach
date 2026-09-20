extends StaticBody3D
@export var action: String = "records"
func mission() -> Node:
	return get_tree().get_first_node_in_group("freight_mission")
func get_interaction_prompt() -> String:
	var controller := mission()
	return controller.use_prompt(action) if controller != null else ""
func interact() -> bool:
	var controller := mission()
	return controller.use_action(action) if controller != null else false
