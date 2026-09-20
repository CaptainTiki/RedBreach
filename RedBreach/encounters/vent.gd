extends Node3D
## Cosmetic debris cannot obstruct movement, bullets, or navigation.
@export var audio_enabled: bool = true
var _tween: Tween
var burst_count: int = 0
func burst() -> void:
	if burst_count > 0: return
	burst_count += 1
	if audio_enabled and DisplayServer.get_name() != "headless": $Sound.play()
	_tween = create_tween().set_parallel(true)
	_tween.tween_property($Grate, "position", Vector3(1.1, -0.95, 1.6), 0.32).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_tween.tween_property($Grate, "rotation", Vector3(-1.35, 0.3, 0.4), 0.32)
func reset_vent() -> void:
	if is_instance_valid(_tween): _tween.kill()
	$Sound.stop()
	$Grate.position = Vector3.ZERO
	$Grate.rotation = Vector3.ZERO
	burst_count = 0
