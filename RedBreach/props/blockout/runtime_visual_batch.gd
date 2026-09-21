extends Node3D
## Runtime rendering cache. Saved Visual cuboids stay editable; collision and lights are untouched.
## A shared mesh is built once for each prop scene, retaining separate materials and metre projection.
var _mesh_cache: Dictionary={}
var source_meshes:=0
var render_meshes:=0
func _ready() -> void:
	if Engine.is_editor_hint() or DisplayServer.get_name()=="headless" or "--no-visual-batch" in OS.get_cmdline_user_args():return
	batch_tree(self)
func batch_tree(placement: Node) -> void:
	for group in placement.get_children():
		for assembly in group.get_children():
			var source: Node3D=assembly.get_node_or_null("Visual")
			if source==null or assembly.has_node("RenderBatch"):continue
			var source_nodes:=source.get_children()
			if source_nodes.is_empty() or not source_nodes.all(func(n):return n is MeshInstance3D and n.mesh is BoxMesh):continue
			var key:=assembly.scene_file_path
			if key.is_empty():continue
			if not _mesh_cache.has(key):
				var groups: Dictionary={}
				for node: MeshInstance3D in source_nodes:
					var material: Material=node.material_override if node.material_override else node.mesh.surface_get_material(0)
					if not groups.has(material):groups[material]=[]
					groups[material].append(node)
				var meshes: Array=[]
				for material in groups:
					var tool:=SurfaceTool.new();tool.begin(Mesh.PRIMITIVE_TRIANGLES)
					for node: MeshInstance3D in groups[material]:tool.append_from(node.mesh,0,source.transform*node.transform)
					tool.set_material(material);var baked:=tool.commit()
					meshes.append({"mesh":baked,"material":material})
				_mesh_cache[key]=meshes
			var batch:=Node3D.new();batch.name="RenderBatch";assembly.add_child(batch)
			for row in _mesh_cache[key]:
				var node:=MeshInstance3D.new();node.mesh=row.mesh;node.material_override=row.material;node.set_meta("generated_blockout_batch",true);batch.add_child(node);render_meshes+=1
			source_meshes+=source_nodes.size();source.hide()
	set_meta("blockout_batch_source_meshes",source_meshes);set_meta("blockout_batch_render_meshes",render_meshes)
