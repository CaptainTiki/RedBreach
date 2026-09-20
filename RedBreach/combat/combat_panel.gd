extends StaticBody3D
@export_enum("Melee bug", "Spitter") var enemy_kind: int = 0
func get_interaction_prompt() -> String:
	var name_text := "spitter" if enemy_kind == 1 else "melee bug"
	return "E / release " + name_text if get_parent().state() == "Ready" else "Backspace / reset encounter"
func interact() -> bool:
	return get_parent().start_encounter(enemy_kind)
