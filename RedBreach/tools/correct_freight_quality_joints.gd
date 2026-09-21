extends "res://tools/apply_freight_quality.gd"
func run() -> void:
	if not "--correct-joints" in OS.get_cmdline_user_args():quit(1);return
	var p: Node3D=load("res://missions/freight/route_a_furnishing.tscn").instantiate()
	if p.has_meta("quality_joints_revision"):push_error("Already corrected");quit(1);return
	p.get_node("A1/Screening_C1").position.z+=.1
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json")).route_a_style
	for h in plan.hatches:
		var marker: Marker3D=p.get_node("HatchReservations/"+str(h.id));marker.position=Vector3(h.center[0]-190,h.floor,h.center[2]-260);marker.set_meta("reservation",h)
	p.set_meta("quality_joints_revision",1);save_placement(p,"res://missions/freight/route_a_furnishing.tscn")
	var r: Node3D=load("res://missions/freight/registration_f02.tscn").instantiate();r.get_node("Objects/Noticeboard").position=Vector3(102.5-96.125,1.1,276.14-262);save_placement(r,"res://missions/freight/registration_f02.tscn")
	print("QUALITY_JOINTS: saved");quit()
