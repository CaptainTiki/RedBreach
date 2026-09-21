extends SceneTree
func _initialize() -> void:call_deferred("run")
func v3(v: Vector3) -> Array:return [v.x,v.y,v.z]
func run() -> void:
	var m: Node3D=load("res://missions/freight/freight_blockout.tscn").instantiate();m.storage_enabled=false;root.add_child(m);m.get_node("GymPlayer").set_physics_process(false)
	var rows: Array=[]
	for key in ["RegistrationF02","ScreeningF04","RouteAStyle"]:
		var node: Node3D=m.get_node(key)
		for mesh in node.find_children("*","MeshInstance3D",true,false):
			if not mesh.mesh is BoxMesh:continue
			var box: AABB=mesh.global_transform*mesh.mesh.get_aabb();var mat: Material=mesh.material_override
			var assembly: Node=mesh
			while assembly!=node and assembly.scene_file_path.is_empty():assembly=assembly.get_parent()
			rows.append({"node":str(mesh.get_path()),"assembly":str(assembly.get_path()),"asset":assembly.scene_file_path,"lo":v3(box.position),"hi":v3(box.end),"material":mat.resource_path if mat else ""})
	FileAccess.open("res://.godot/route_a_mesh_audit.json",FileAccess.WRITE).store_string(JSON.stringify(rows));print("MESH_AUDIT: ",rows.size()," boxes");quit()
