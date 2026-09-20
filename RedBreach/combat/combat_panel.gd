extends StaticBody3D
func get_interaction_prompt() -> String:
	return "E / release one bug" if get_parent().state() == "Ready" else "Backspace / reset encounter"
func interact() -> bool:
	return get_parent().start_encounter()
