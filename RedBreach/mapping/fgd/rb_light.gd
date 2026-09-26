@tool
extends OmniLight3D
## A light placed in TrenchBroom (rb_light). Lights live in the map, inside their room's group, so editing or
## regenerating one room moves its lights with it. Keys: energy, range (m), shadow (0/1), color ("r g b").
@export var func_godot_properties: Dictionary = {}

func _func_godot_apply_properties(p: Dictionary) -> void:
	light_energy = float(p.get("energy", 1.0))
	omni_range = float(p.get("range", 10.0))
	shadow_enabled = int(p.get("shadow", 1)) == 1
	omni_attenuation = 1.2
	var c := str(p.get("color", "0.86 0.93 1")).split_floats(" ")
	if c.size() >= 3:
		light_color = Color(c[0], c[1], c[2])
