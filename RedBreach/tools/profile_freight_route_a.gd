extends "res://tools/capture_freight.gd"
func median(values: Array, fraction: float) -> float:
	var ordered:=values.duplicate();ordered.sort();return ordered[mini(ordered.size()-1,int(ordered.size()*fraction))]
func run() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED);Engine.max_fps=0
	mission=load("res://missions/freight/freight_blockout.tscn").instantiate();mission.storage_enabled=false;root.add_child(mission)
	player=mission.get_node("GymPlayer");player.control_override=true;player.pistol.audio_enabled=false
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE;await ticks(100)
	var rows: Array=[]
	var shots: Array=[["registration",[113,0,270],[104,1.5,275]],["admin",[79,0,268],[67,1.3,265]],["inspection",[48,0,235],[43,-.5,213]],["records",[47,4,116],[55,1.5,136]],["dispatch",[114,2,74],[101,3.4,61]],["watch",[151,2,119],[133,3.5,123]],["clearance",[120,6,176],[145,1.8,185]],["annex",[75,-2,210],[74,-.4,234]]]
	for shot in shots:
		var a: Array=shot[1];var b: Array=shot[2];await view(Vector3(a[0]-190,a[1]+.05,a[2]-260),Vector3(b[0]-190,b[1],b[2]-260),"quality_"+shot[0])
		for i in 75:await process_frame
		var frame_ms: Array=[];var draws: Array=[];var objects: Array=[];var last:=Time.get_ticks_usec()
		for i in 240:
			await process_frame;var now:=Time.get_ticks_usec();frame_ms.append((now-last)/1000.0);last=now
			draws.append(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME));objects.append(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME))
		var row: Dictionary={"view":shot[0],"frame_ms_p50":median(frame_ms,.5),"frame_ms_p95":median(frame_ms,.95),"frame_ms_p99":median(frame_ms,.99),"draw_calls_p50":median(draws,.5),"objects_p50":median(objects,.5)}
		rows.append(row);print("PROFILE_VIEW: ",JSON.stringify(row))
	var tag:="baseline"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--tag="):tag=arg.trim_prefix("--tag=")
	var output:={"viewport":[root.size.x,root.size.y],"vsync":"disabled","samples_per_view":240,"warmup_frames":75,"views":rows,"conditions":"Local rendered offscreen window, empty mission, fixed camera; not a populated combat benchmark","engine":Engine.get_version_info().string}
	FileAccess.open("res://.godot/route_a_profile_"+tag+".json",FileAccess.WRITE).store_string(JSON.stringify(output,"\t"));print("ROUTE_A_PROFILE: complete ",tag);quit()
