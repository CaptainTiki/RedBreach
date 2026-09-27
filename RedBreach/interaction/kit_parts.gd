extends RefCounted
## Building blocks for the progression kit's runtime geometry: boxes in a look's materials.
## "Fit" roles (door, screen, grate) show their texture once per face, as the map does; tiled roles (frame,
## machine_body, hazard) repeat at the map's 32 px per metre in the part's own space, so a moving part does not swim.

const LOOK_PATH := "res://textures/looks/%s/%s.tres"
const FIT := ["door", "screen", "grate", "service"]
static var _cache := {}


static func material(look: String, role: String) -> Material:
	var key := look + "/" + role
	if _cache.has(key):
		return _cache[key]
	var path := LOOK_PATH % [look, role]
	if not ResourceLoader.exists(path):
		path = LOOK_PATH % ["steel", role]
	var m: StandardMaterial3D = (load(path) as StandardMaterial3D).duplicate()
	if role in FIT:
		m.uv1_scale = Vector3(3, 2, 1)       # a BoxMesh lays its six faces out 3 x 2; this fits the texture per face
	else:
		var tex := m.albedo_texture
		m.uv1_triplanar = true
		m.uv1_scale = Vector3.ONE * (32.0 / (tex.get_width() if tex != null else 64))
	_cache[key] = m
	return m


## A lamp or glowing card: flat colour that glows a little (a lamp, not a light source).
static func glow(color: Color, energy := 1.6) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.emission_enabled = true
	m.emission = color
	m.emission_energy_multiplier = energy
	return m


## A box mesh under parent at a local position; solid=true adds a matching box collision beside it (parent must then
## be a CollisionObject3D: a body, a moving leaf, a switch).
static func box(parent: Node3D, size: Vector3, at: Vector3, mat: Material, solid := false,
		rotation := Vector3.ZERO) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = at
	mi.rotation = rotation
	parent.add_child(mi)
	if solid:
		var cs := CollisionShape3D.new()
		var bs := BoxShape3D.new()
		bs.size = size
		cs.shape = bs
		cs.position = at
		cs.rotation = rotation
		parent.add_child(cs)
	return mi


## Plan direction "dx dy" (x east, y north) as a Godot direction (x, 0, -y).
static func plan_dir(text: String, fallback := Vector3.BACK) -> Vector3:
	var v := text.split_floats(" ")
	if v.size() < 2 or Vector2(v[0], v[1]).length() < 1e-6:
		return fallback
	return Vector3(v[0], 0.0, -v[1]).normalized()


## A basis whose local Z faces the given direction, X along the wall, Y up.
static func facing_basis(f: Vector3) -> Basis:
	return Basis(Vector3.UP.cross(f).normalized(), Vector3.UP, f)


## Show a short line on the level's HUD (the lift time, a distant clunk), when the level offers one.
static func notice(node: Node, text: String) -> void:
	if text == "" or not node.is_inside_tree():
		return
	var level := node.get_tree().get_first_node_in_group("level")
	if level != null and level.has_method("notice"):
		level.notice(text)
