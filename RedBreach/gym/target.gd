extends StaticBody3D

var hit_count: int = 0
var flash: Tween

func register_hit() -> void:
	hit_count += 1
	if flash:
		flash.kill()
	$Plate.scale = Vector3.ONE * 0.88
	flash = create_tween()
	flash.tween_property($Plate, "scale", Vector3.ONE, 0.18)
	$Readout.text = "HIT %d" % hit_count
