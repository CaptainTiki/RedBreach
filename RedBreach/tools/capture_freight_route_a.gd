extends "res://tools/capture_freight.gd"
func run() -> void:
	mission=load("res://missions/freight/freight_blockout.tscn").instantiate();mission.storage_enabled=false;root.add_child(mission)
	player=mission.get_node("GymPlayer");player.control_override=true;player.pistol.audio_enabled=false
	Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
	await ticks(80);mission.get_node("HUD").hide()
	var shots: Array=[
		["a_admin",[79,0,268],[67,1.3,265]], ["a_prep",[88,0,280],[75,1.3,284]],
		["a_hall_intake",[44,0,279],[44,1.6,255]], ["a_inspection_entry",[48,0,235],[43,-.5,213]],
		["a_inspection_floor",[40,-2,222],[48,-.5,211]], ["a_circuit",[20,-2,203],[17,-.5,189]],
		["a_pump_test",[44,-2,203],[44,-.4,190]], ["a_kit",[20,-2,229],[25,-.5,239]],
		["a_staff",[20,-2,216],[26,-.5,209]], ["a_annex",[85,-2,194],[74,-.4,188]],
		["a_workshop",[75,-2,210],[74,-.4,234]], ["a_stores",[93,-2,211],[97,-.4,218]],
		["a_spares",[93,-2,233],[90,-.4,227]], ["a_records_entry",[73,0,142],[55,2,127]],
		["a_records_floor",[43,0,141],[28,1.5,128]], ["a_records_stair",[58,0,132],[58,4.6,117]],
		["a_records_gallery",[47,4,116],[38,1.5,136]], ["a_archive",[40,4,69],[29,5.3,75]],
		["a_archive_card",[40,4,57],[31,5.2,51]], ["a_security_hall",[121,2,105],[111,3.5,101]],
		["a_dispatch",[114,2,74],[101,3.4,61]], ["a_security",[140,2,67],[139,3.5,54]],
		["a_dispatch_exit",[142,2,84],[135,3.5,88]], ["a_watch_entry",[151,2,119],[133,3.5,123]],
		["a_watch_upper",[145,6,138],[132,7.4,133]], ["a_clearance_upper",[120,6,176],[145,1.8,185]],
		["a_clearance_low",[148,0,190],[135,1.4,194]], ["a_clearance_west",[138,0,183],[120,1.3,190]],
		["a_return",[176,0,210],[176,1.6,233]]]
	for shot in shots:
		var a: Array=shot[1];var b: Array=shot[2]
		await view(Vector3(a[0]-190,a[1]+.05,a[2]-260),Vector3(b[0]-190,b[1],b[2]-260),shot[0])
	print("FREIGHT_ROUTE_A_CAPTURE: ",shots.size()," views saved")
	quit()
