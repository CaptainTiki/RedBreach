@tool
extends StaticBody3D
## A climbable ladder placed in TrenchBroom (rb_ladder). The origin is the foot of the ladder face; `facing` (plan
## "dx dy") is the way the climber faces, into the ladder, and the climber steps off forward at `top`. E climbs up
## from the bottom or down from the top, through the freight player's ClimbChart.
@export var func_godot_properties: Dictionary = {}
@export var top: float = 0.0
@export var facing := Vector3(0, 0, -1)

func _func_godot_apply_properties(p: Dictionary) -> void:
	top = float(p.get("top", 0.0))
	var f := str(p.get("facing", "0 1")).split_floats(" ")
	facing = Vector3(f[0], 0.0, -f[1]).normalized()
	for child in get_children():
		remove_child(child)
		child.free()
	var h := maxf(0.5, top - position.y)
	basis = Basis.looking_at(facing, Vector3.UP)
	var shape := CollisionShape3D.new()
	shape.name = "Shape"
	var box := BoxShape3D.new()
	box.size = Vector3(0.7, h, 0.12)
	shape.shape = box
	shape.position = Vector3(0.0, h / 2.0, 0.06)
	add_child(shape)
	var visual := MeshInstance3D.new()
	visual.name = "Visual"
	var bm := BoxMesh.new()
	bm.size = Vector3(0.6, h, 0.08)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.72, 0.56, 0.2)
	mat.roughness = 0.6
	bm.material = mat
	visual.mesh = bm
	visual.position = Vector3(0.0, h / 2.0, 0.06)
	add_child(visual)

func climb_path(from: Vector3) -> Array[Vector3]:
	var base := global_position
	var bottom := base - facing * 0.45 + Vector3.UP * 0.05
	var top_c := Vector3(bottom.x, top + 0.05, bottom.z)
	var off := Vector3(base.x, top + 0.05, base.z) + facing * 0.8
	var points: Array[Vector3] = []
	if from.y < (base.y + top) / 2.0:
		points.assign([bottom, top_c, off])
	else:
		points.assign([top_c, bottom])
	return points

func start_climb(player: Node) -> bool:
	# Going up, the climber snaps onto the ladder spot first (a ladder grab), so where exactly the player stood
	# (even brushing the panel) never blocks the climb.
	if player == null or not player.has_method("begin_climb"):
		return false
	var path := climb_path(player.global_position)
	if path.size() == 3:
		player.relocate(Transform3D(player.global_basis, path[0]))
	return player.begin_climb(path)

func interact() -> bool:
	return start_climb(get_tree().get_first_node_in_group("freight_player"))

func get_interaction_prompt() -> String:
	return "E  Climb ladder"
