extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	if not "--apply-route-a-finishing" in OS.get_cmdline_user_args():push_error("Historical one-time helper; edit the current source scene instead");quit(1);return
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json")).route_a_style
	var placement: Node3D=load("res://missions/freight/route_a_furnishing.tscn").instantiate()
	if placement.has_meta("route_a_finish_version"):push_error("Finishing already applied; preserve later edits");quit(1);return
	placement.set_meta("route_a_finish_version",1)
	var ids: Dictionary={}
	for o in plan.props:ids[o.id]=o
	for group in placement.get_children():
		if group is Label3D:continue
		if group.name=="HatchReservations":
			for marker in group.get_children():
				for h in plan.hatches:
					if str(marker.name)==h.id:marker.set_meta("reservation",h)
			continue
		for node in group.get_children():
			var id:=str(node.name)
			if not ids.has(id):group.remove_child(node);node.free();continue
			var o: Dictionary=ids[id];node.position=Vector3(o.bounds[0]-190,o.bottom,o.bounds[1]-260)
	var packed:=PackedScene.new();var err:=packed.pack(placement)
	if err==OK:err=ResourceSaver.save(packed,"res://missions/freight/route_a_furnishing.tscn")
	print("ROUTE_A_REFINEMENT: save=",err);quit(err)
