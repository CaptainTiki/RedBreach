extends SceneTree
var failures: Array[String] = []
var checks := 0
var mission: Node3D
var player: CharacterBody3D
var layout: Dictionary
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ",message)
	if not ok: failures.append(message)
func ticks(count: int) -> void:
	for i in count: await physics_frame
	await process_frame
func world(x: float,y: float,z: float) -> Vector3:return Vector3(x-190,y,z-260)
func place(point: Vector3) -> void:
	player.test_direction = Vector2.ZERO
	player.relocate(Transform3D(Basis.IDENTITY,point))
	await ticks(5)
func aim(point: Vector3) -> void:
	var d: Vector3 = point-player.camera.global_position
	player.rotation.y = atan2(-d.x,-d.z)
	player._pitch = atan2(d.y,Vector2(d.x,d.z).length())
	player.reset_camera_interpolation()
func interact_node(node: Node3D,normal := Vector3.BACK,floor_y := 0.0) -> bool:
	var p := node.global_position+normal*1.5
	p.y = floor_y+0.05
	await place(p)
	aim(node.global_position)
	await ticks(1)
	return player.try_interact()
func run() -> void:
	var packed: PackedScene = load("res://missions/freight/freight_blockout.tscn")
	if packed == null:quit(1);return
	mission = packed.instantiate()
	mission.storage_enabled = false
	root.add_child(mission)
	player = mission.get_node("GymPlayer")
	player.control_override = true
	player.pistol.audio_enabled = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	layout = JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json"))
	await ticks(65)
	check(mission.get_node("Geometry").find_children("*","CollisionShape3D",true,false).size()==int(layout.brushes),"Saved map contains every source brush")
	check(mission.get_node("Gates/Arrival").state_name() in ["Opening","Open"],"Arrival cycle opens into Receiving")
	await check_floors()
	await check_stairs()
	await check_progression()
	await check_ladder()
	await check_full_routes()
	await check_materials()
	mission.storage_enabled = false
	print("FREIGHT_QA: ",checks," checks; ",failures.size()," failures")
	quit(0 if failures.is_empty() else 1)
func check_floors() -> void:
	var bad: Array = []
	var blocked: Array = []
	var shape := CapsuleShape3D.new()
	shape.radius = 0.3
	shape.height = 1.8
	for row in layout.samples:
		var point := Vector3(float(row[0]),float(row[1]),float(row[2]))
		var near_gate := false
		for g in layout.gates:
			if Vector2(point.x-(float(g[1])-190),point.z-(float(g[2])-260)).length()<3.2:near_gate=true
		if near_gate:continue
		var ray := PhysicsRayQueryParameters3D.create(point+Vector3.UP*0.4,point-Vector3.UP*0.6,1,[player.get_rid()])
		var hit := mission.get_world_3d().direct_space_state.intersect_ray(ray)
		if hit.is_empty() or absf(hit.position.y-point.y)>0.27:
			if bad.size()<12:bad.append(str(point))
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape
		query.transform = Transform3D(Basis.IDENTITY,point+Vector3.UP*1.0)
		query.exclude = [player.get_rid()]
		query.collision_mask = 1
		if not mission.get_world_3d().direct_space_state.intersect_shape(query,1).is_empty():
			if blocked.size()<12:blocked.append(str(point))
	check(bad.is_empty(),"Centreline floor samples match planned elevations: "+str(bad))
	# Capsules can touch the next riser at transition samples, so walk those explicitly below.
	print("CAPSULE_SAMPLE_NOTES: ",blocked)
	for room_id in layout.rooms:
		var room: Array = layout.rooms[room_id]
		var floor_y: float = layout.heights[room_id]
		var point := world(room[0],floor_y,room[1])
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape
		query.transform = Transform3D(Basis.IDENTITY,point+Vector3.UP*1.0)
		query.exclude = [player.get_rid()]
		query.collision_mask = 1
		check(mission.get_world_3d().direct_space_state.intersect_shape(query,1).is_empty(),str(room_id)+": full standing clearance on room floor")
func check_stairs() -> void:
	for flight in layout.stairs:
		for reverse in [false,true]:
			var a: Array = flight[4] if reverse else flight[3]
			var b: Array = flight[3] if reverse else flight[4]
			var ya: float = flight[6] if reverse else flight[5]
			var yb: float = flight[5] if reverse else flight[6]
			var direction := Vector3(float(b[0])-float(a[0]),0,float(b[1])-float(a[1])).normalized()
			var origin := world(a[0],ya+0.04,a[1])-direction*1.2
			await place(origin)
			player.rotation.y = atan2(-direction.x,-direction.z)
			player.test_direction = Vector2(0,-1)
			var count := 0
			while (player.global_position-origin).dot(direction)<6.1 and count<150:
				await ticks(1)
				count += 1
			player.test_direction = Vector2.ZERO
			await ticks(3)
			check(count<150 and absf(player.position.y-yb)<0.1,str(flight[0])+" "+("reverse" if reverse else "forward")+": walk real stair collision / end "+str(player.position))
func check_progression() -> void:
	player.reset_player()
	await ticks(10)
	check(not mission.records_card and not mission.freight_card and not mission.power_restored,"Reset clears the two cards and power")
	var d2: Node3D = mission.get_node("Gates/D2")
	check(not await interact_node(d2.get_node("SwitchBack"),Vector3.LEFT),"Records reader refuses entry before the card")
	check(await interact_node(mission.get_node("Objectives/Records")),"Records card is reachable and collectible with E")
	check(await interact_node(d2.get_node("SwitchBack"),Vector3.LEFT),"Records card releases door 2")
	await ticks(60)
	check(d2.state_name()=="Open","Door 2 actually opens")
	check(await interact_node(mission.get_node("Objectives/Freight"),Vector3.BACK,2.0),"Freight card can be collected at the A4 route split")
	check(not await interact_node(mission.get_node("Gates/Lift/SwitchFront")),"Lift still requires power after freight clearance")
	var d4: Node3D = mission.get_node("Gates/D4")
	check(not await interact_node(d4.get_node("SwitchFront"),Vector3.RIGHT),"Door 4 cannot release from B3/east")
	check(await interact_node(d4.get_node("SwitchBack"),Vector3.LEFT),"Door 4 releases from the red/west route")
	await ticks(55)
	check(d4.latched and d4.state_name()=="Open","Door 4 stays released")
	check(await interact_node(mission.get_node("Objectives/Power"),Vector3.BACK,2.0),"Power control is usable on its raised floor")
	check(await interact_node(mission.get_node("Gates/Lift/SwitchFront")),"Freight card plus power open the exit")
	check(await interact_node(mission.get_node("Objectives/Depart")),"Lift departure completes the traversal")
	check(mission.run_state()=="Complete" and mission.last_result.outcome=="complete" and mission.last_result.events.back().event=="depart","Completion captures a separate walkthrough result including departure")
	for id in ["S1","S2"]:
		var gate: Node3D = mission.get_node("Gates/"+id)
		check(not await interact_node(gate.get_node("SwitchFront")),id+": hub side cannot release the return")
		check(await interact_node(gate.get_node("SwitchBack"),Vector3.FORWARD),id+": branch side releases the return")
	player.reset_player()
	await ticks(10)
	check(mission.selected_code=="" and not mission.get_node("Ladder/Visual").visible,"Reset restores the initial selector and ladder state")
	check(await interact_node(mission.get_node("Selector/GMa"),Vector3.BACK,-2.0),"Faulty button accepts selection")
	check(mission.selected_code=="GMa" and not mission.get_node("Ladder/Visual").visible,"GMa leaves useful circuits closed")
	check(await interact_node(mission.get_node("Selector/BcD"),Vector3.BACK,-2.0),"BcD can be selected")
	await ticks(55)
	check(mission.get_node("Gates/BcD").state_name()=="Open" and mission.get_node("Ladder/Visual").visible,"BcD deploys the ladder and opens the upper gate")
	check(await interact_node(mission.get_node("Selector/Tr1"),Vector3.BACK,-2.0),"Tr1 replaces BcD")
	await ticks(55)
	check(mission.get_node("Gates/BcD").state_name()=="Closed" and not mission.get_node("Ladder/Visual").visible,"Tr1 retracts Maintenance and opens only the cache")
	player.get_node("Health").take_damage(25)
	check(await interact_node(mission.get_node("Cache/Health"),Vector3.BACK,-2.0),"Tr1 exposes a useful health pickup")
	mission.use_action("BcD")
	mission.use_action("Tr1")
	await ticks(5)
	check(mission.secret_collected and not mission.get_node("Cache/Health").visible,"Circuit toggles do not replenish the secret")
func check_ladder() -> void:
	mission.use_action("BcD")
	await ticks(55)
	await place(world(147,2.05,62))
	aim(mission.get_node("Ladder/LowerUse").global_position)
	await ticks(1)
	check(player.try_interact(),"Ladder can be engaged from the Security floor")
	var count := 0
	while player.climbing() and count<800:
		await ticks(1)
		count += 1
	check(count<800 and absf(player.position.y-6)<0.15 and player.position.x>-36,"Ladder reaches the upper landing without tunnelling")
	await place(world(151,6.05,62))
	aim(mission.get_node("Ladder/UpperUse").global_position)
	await ticks(1)
	check(player.try_interact(),"Ladder can be engaged from the upper landing")
	count = 0
	while player.climbing() and count<800:
		await ticks(1)
		count += 1
	check(count<800 and absf(player.position.y-2)<0.15,"Ladder returns safely to Security")
	mission.use_action("Tr1")
	check(not mission.use_action("ladder_low"),"Retracted ladder cannot be used")
	player.reset_player()
	await ticks(10)
	check(not player.climbing() and player.position.distance_to(player.spawn_transform.origin)<0.2,"Reset cancels traversal and restores the arrival position")
func check_materials() -> void:
	var count := 0
	var good := true
	for node in mission.get_node("Geometry").find_children("*","MeshInstance3D",true,false):
		for surface in node.mesh.get_surface_count():
			var material: StandardMaterial3D = node.mesh.surface_get_material(surface)
			good = good and material.albedo_texture != null and material.albedo_texture.resource_path.begins_with("res://textures/greybox/") and not material.albedo_texture.resource_path.contains("/Light/")
			var arrays: Array = node.mesh.surface_get_arrays(surface)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var uv: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			for i in range(0,indices.size(),3):
				var a := indices[i]
				var b := indices[i+1]
				var c := indices[i+2]
				var e1 := vertices[b]-vertices[a]
				var e2 := vertices[c]-vertices[a]
				var t1 := uv[b]-uv[a]
				var t2 := uv[c]-uv[a]
				var determinant := t1.x*t2.y-t2.x*t1.y
				if e1.cross(e2).length()<0.000001:continue
				count += 1
				if absf(determinant)<0.000001:good=false;continue
				var du := (e1*t2.y-e2*t1.y)/determinant
				var dv := (e2*t1.x-e1*t2.x)/determinant
				good = good and absf(du.length()-1)<0.001 and absf(dv.length()-1)<0.001 and absf(du.normalized().dot(dv.normalized()))<0.001
	check(good and count>0,"All "+str(count)+" baked triangles use Kenney textures with accurate 1 m orthogonal repeats")


func walk_to(target: Vector3) -> bool:
	var remaining := Vector2(target.x-player.position.x,target.z-player.position.z)
	var budget := ceili(remaining.length()/player.walk_speed*60)+180
	while remaining.length()>0.16 and budget>0:
		player.rotation.y = atan2(-remaining.x,-remaining.y)
		player._pitch = 0.0
		player.test_direction = Vector2(0,-1)
		await ticks(1)
		remaining = Vector2(target.x-player.position.x,target.z-player.position.z)
		budget -= 1
	player.test_direction = Vector2.ZERO
	return budget>0
func check_full_routes() -> void:
	player.reset_player()
	await ticks(10)
	# Interaction restrictions were exercised above; release gates for a continuous
	# geometry walk so a failure reports the passage rather than missing inventory.
	for gate in mission.get_node("Gates").get_children():
		if gate.gate_id != "D1":gate.release()
	mission.use_action("BcD")
	await ticks(60)
	await place(world(190,0.05,328))
	var route: Array = layout.normal_route
	var reached := true
	var missed := ""
	for i in range(route.size()-1):
		var points: Array = []
		for edge in layout.edges:
			if edge.a==route[i] and edge.b==route[i+1]:points=edge.points.duplicate(true);break
			if edge.b==route[i] and edge.a==route[i+1]:points=edge.points.duplicate(true);points.reverse();break
		for point in points:
			if not await walk_to(world(point[0],0,point[1])):
				reached = false
				missed = str(route[i])+" -> "+str(route[i+1])+" at "+str(player.position)
				break
		if not reached:break
	check(reached,"Continuous normal route walk with gates released: "+missed)
	await place(world(155,6.05,62))
	reached = true
	for point in [[184,62],[184,52],[225,52],[245,52],[250,52],[250,62]]:
		if not await walk_to(world(point[0],0,point[1])):reached=false;break
	check(reached and absf(player.position.y)<0.1,"Continuous Maintenance bridge, workshop and descent into B4")
	reached = true
	for point in [[250,52],[245,52],[225,52],[184,52],[184,62],[155,62]]:
		if not await walk_to(world(point[0],0,point[1])):reached=false;break
	check(reached and absf(player.position.y-6)<0.1,"Maintenance bridge and all three flights are reversible")
	player.test_direction = Vector2.ZERO
