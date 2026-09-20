extends Node3D
## Bounded world-space effects. Mesh splats work in the gym without decal textures.
@export var max_splats: int = 64
@export var max_droplets: int = 160
var splats: Array[MeshInstance3D] = []
var droplets: Array[Dictionary] = []
var _rng := RandomNumberGenerator.new()
var _blood: StandardMaterial3D
var _spark: StandardMaterial3D
var _drop_mesh: SphereMesh

func _ready() -> void:
	add_to_group("combat_effects")
	_rng.randomize()
	_blood = StandardMaterial3D.new()
	_blood.albedo_color = Color(0.47, 0.75, 0.065)
	_blood.roughness = 0.38
	_blood.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_spark = StandardMaterial3D.new()
	_spark.albedo_color = Color(1, 0.66, 0.18)
	_spark.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_drop_mesh = SphereMesh.new()
	_drop_mesh.radius = 0.045
	_drop_mesh.height = 0.09
	_drop_mesh.radial_segments = 6
	_drop_mesh.rings = 3

func clear_effects() -> void:
	for node in splats:
		node.queue_free()
	for drop in droplets:
		drop.node.queue_free()
	splats.clear()
	droplets.clear()

func spawn_impact(point: Vector3, normal: Vector3) -> void:
	_burst(point + normal * 0.025, normal, 5, false)

func spawn_spit_impact(point: Vector3, normal: Vector3, exclude: Array[RID], hit_player: bool) -> void:
	_burst(point + normal * 0.03, normal, 12, true)
	if hit_player:
		var floor_hit := _cast(point + Vector3.UP * 0.1, point + Vector3.DOWN * 4.0, exclude)
		if not floor_hit.is_empty():
			_splat(floor_hit.position, floor_hit.normal, 0.3)
	else:
		_splat(point, normal, 0.3)

func spawn_bug_hit(point: Vector3, normal: Vector3, direction: Vector3, exclude: Array[RID], lethal: bool) -> void:
	_burst(point + normal * 0.06, normal, 40 if lethal else 13, true)
	var floor_hit := _cast(point + Vector3.UP * 0.2, point + Vector3.DOWN * 6.0, exclude)
	if not floor_hit.is_empty():
		_splat(floor_hit.position, floor_hit.normal, 0.85 if lethal else 0.22)
	var back := _cast(point + direction * 0.15, point + direction * 6.0, exclude)
	if not back.is_empty() and (floor_hit.is_empty() or back.position.distance_to(floor_hit.position) > 0.4):
		_splat(back.position, back.normal, 0.55 if lethal else 0.25)

func _cast(start: Vector3, end: Vector3, exclude: Array[RID]) -> Dictionary:
	return get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start, end, 1, exclude))

func _burst(point: Vector3, normal: Vector3, count: int, blood: bool) -> void:
	for i in count:
		while droplets.size() >= max_droplets:
			droplets.pop_front().node.queue_free()
		var node := MeshInstance3D.new()
		node.mesh = _drop_mesh
		node.material_override = _blood if blood else _spark
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(node)
		node.global_position = point
		node.scale = Vector3.ONE * _rng.randf_range(0.5, 1.8)
		var spray := Vector3(_rng.randf_range(-1.0, 1.0), _rng.randf_range(0.0, 1.5), _rng.randf_range(-1.0, 1.0))
		droplets.append({"node": node, "velocity": (spray + normal * 0.5) * _rng.randf_range(1.0, 3.5), "life": 0.65 if blood else 0.18})

func _splat(point: Vector3, normal: Vector3, radius: float) -> void:
	while splats.size() >= max_splats:
		splats.pop_front().queue_free()
	var mesh := ImmediateMesh.new()
	mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	var points: Array[Vector3] = []
	for i in 14:
		var angle := TAU * float(i) / 14.0
		points.append(Vector3(cos(angle), 0, sin(angle)) * radius * _rng.randf_range(0.55, 1.2))
	for i in 14:
		mesh.surface_add_vertex(Vector3.ZERO)
		mesh.surface_add_vertex(points[i])
		mesh.surface_add_vertex(points[(i + 1) % 14])
	mesh.surface_end()
	var node := MeshInstance3D.new()
	node.mesh = mesh
	var mat: StandardMaterial3D = _blood.duplicate()
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.albedo_color *= _rng.randf_range(0.65, 0.95)
	node.material_override = mat
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	var tangent := normal.cross(Vector3.FORWARD).normalized()
	if tangent.length_squared() < 0.1:
		tangent = normal.cross(Vector3.RIGHT).normalized()
	node.global_transform = Transform3D(Basis(tangent, normal, tangent.cross(normal)).orthonormalized(), point + normal * _rng.randf_range(0.009, 0.015))
	splats.append(node)

func _physics_process(delta: float) -> void:
	for i in range(droplets.size() - 1, -1, -1):
		var drop: Dictionary = droplets[i]
		drop.life -= delta
		if drop.life <= 0.0:
			drop.node.queue_free()
			droplets.remove_at(i)
			continue
		drop.velocity.y -= 9.0 * delta
		drop.node.position += drop.velocity * delta
		drop.node.scale *= 1.0 - delta * 0.6
