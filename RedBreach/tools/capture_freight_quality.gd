extends "res://tools/capture_freight.gd"
func run() -> void:
	mission=load("res://missions/freight/freight_blockout.tscn").instantiate();mission.storage_enabled=false;root.add_child(mission)
	player=mission.get_node("GymPlayer");player.control_override=true;player.pistol.audio_enabled=false;Input.mouse_mode=Input.MOUSE_MODE_VISIBLE;await ticks(80);mission.get_node("HUD").hide()
	var shots: Array=[["q_registration",[113,0,270],[103,2.6,275]],["q_waiting",[104,0,280],[104,1.5,276]],["q_screening",[88,0,272],[90,3.3,265.1]],["q_prep",[88,0,285],[85,3.2,290]],["q_dispatch",[142,2,77],[144,6,67]],["q_records",[78,0,142],[75,3.8,132]]]
	for shot in shots:
		var a: Array=shot[1];var b: Array=shot[2];await view(Vector3(a[0]-190,a[1]+.05,a[2]-260),Vector3(b[0]-190,b[1],b[2]-260),shot[0])
	print("QUALITY_CAPTURE: ",shots.size()," views");quit()
