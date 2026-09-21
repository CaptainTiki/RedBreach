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
	await check_a_openings()
	await check_stairs()
	await check_progression()
	await check_ladder()
	await check_full_routes()
	await check_registration_floor_and_door()
	await check_furnishing()
	await check_registration()
	await check_screening()
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
	for room_id in layout.clearance_points:
		var row: Array = layout.clearance_points[room_id]
		var point := world(row[0],row[1],row[2])
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
	check(await interact_node(mission.get_node("Objectives/Records"),Vector3.BACK,4.0),"Records card is reachable and collectible with E")
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
	var reached := true
	var missed := ""
	for point in layout.walk_points:
		if not await walk_to(world(point[0],0,point[1])):
			reached = false
			missed = "toward "+str(point)+" at "+str(player.position)
			break
	check(reached,"Continuous normal route through A interiors and unchanged B with gates released: "+missed)
	await place(world(190,0.05,260))
	var reverse_a: Array = layout.a_walk_points.duplicate(true)
	reverse_a.reverse()
	reached = true
	for point in reverse_a:
		if not await walk_to(world(point[0],0,point[1])):
			reached=false
			missed="toward "+str(point)+" at "+str(player.position)
			break
	check(reached,"A-loop interiors and upper connections are reversible: "+("" if reached else missed))
	await place(world(85,-1.95,164))
	reached=true
	for point in layout.interior_paths["Annex"]:
		if not await walk_to(world(point[0],0,point[1])):reached=false;break
	check(reached,"Inspection Annex divided side route is reachable")
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

func check_a_openings() -> void:
	var shape := CapsuleShape3D.new()
	shape.radius = 0.3
	shape.height = 1.8
	var blocked: Array = []
	for portal in layout.a_portals:
		var point := world(portal[1][0],portal[2],portal[1][1])
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape=shape
		query.transform=Transform3D(Basis.IDENTITY,point+Vector3.UP)
		query.exclude=[player.get_rid()]
		query.collision_mask=1
		if not mission.get_world_3d().direct_space_state.intersect_shape(query,1).is_empty():blocked.append(portal)
	check(blocked.is_empty(),"All revised A room thresholds have standing clearance at their intended level: "+str(blocked))
	# Old entry centres must be solid, including below the raised openings.
	var sealed: Array = [
		["A1 east",114,0,278,Vector3.RIGHT], ["A1 west",62,0,278,Vector3.RIGHT],
		["A2 south",32,0,242,Vector3.BACK], ["A2 north",32,-2,184,Vector3.BACK],
		["A3 east",84,0,128,Vector3.RIGHT], ["A7 old south",35,0,81,Vector3.BACK],
		["A4 old entry",121,2,93,Vector3.BACK], ["A5 old entry",143,2,114,Vector3.BACK],
		["A5 old lower exit",143,2,144,Vector3.BACK], ["A6 old north",133,2,166,Vector3.BACK],
		["A6 old east",156,0,182,Vector3.RIGHT]]
	for entry in sealed:
		var point := world(entry[1],entry[2]+1,entry[3])
		var direction: Vector3=entry[4]
		var ray := PhysicsRayQueryParameters3D.create(point-direction,point+direction,1,[player.get_rid()])
		check(not mission.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),str(entry[0])+": superseded doorway is sealed")


func check_furnishing() -> void:
	var plan: Dictionary = layout.furnishing
	var shape := CapsuleShape3D.new()
	shape.radius=0.3;shape.height=1.8
	var space := mission.get_world_3d().direct_space_state
	for key in plan.rooms:
		var room_data: Dictionary=plan.rooms[key]
		for room in room_data.rooms:
			var p := world(room[4][0],room_data.floor,room[4][1])
			var ray := PhysicsRayQueryParameters3D.create(p+Vector3.UP*2,p+Vector3.UP*12,1,[player.get_rid()])
			var hit := space.intersect_ray(ray)
			check(not hit.is_empty() and absf(hit.position.y-(float(room_data.floor)+float(room[3])))<0.01,str(key)+" / "+str(room[1])+": ceiling matches reviewed height")
		for door in room_data.doors:
			var good := true
			var half_width: float=(float(door[3]) if door.size()>3 else 4.0)/2
			for offset in [-half_width+0.35,0.0,half_width-0.35]:
				var p := world(door[1][0],room_data.floor,door[1][1])
				if door[2]=="x":p.z+=offset
				else:p.x+=offset
				var q := PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,p+Vector3.UP);q.collision_mask=1;q.exclude=[player.get_rid()]
				good=good and space.intersect_shape(q,1).is_empty()
			check(good,str(key)+" / "+str(door[0])+": reviewed opening retains standing passage near both edges")
		for i in room_data.optional.size():
			var route: Array=room_data.optional[i]
			await place(world(route[0][0],float(room_data.floor)+0.05,route[0][1]))
			var reached := true
			var journey: Array=route.duplicate(true);var reverse: Array=route.duplicate(true);reverse.reverse();journey.append_array(reverse)
			for p in journey:
				if not await walk_to(world(p[0],0,p[1])):reached=false;break
			check(reached,str(key)+" optional furnished route "+str(i)+": walk out and back without snagging")
	# Eye samples taken before descending; collision rays must see the lower floor.
	for sample in [[47,235,40,223],[54,231,54,220]]:
		var eye:=world(sample[0],1.65,sample[1]);var target:=world(sample[2],-2.05,sample[3])
		var ray:=PhysicsRayQueryParameters3D.create(eye,target,1,[player.get_rid()]);var hit:=space.intersect_ray(ray)
		check(not hit.is_empty() and absf(hit.position.y+2)<0.02,"A2: receiving floor visible before descent from "+str(sample.slice(0,2)))
	await place(world(46,0.05,234))
	player.rotation.y=0;player.test_direction=Vector2(0,-1)
	await ticks(100)
	player.test_direction=Vector2.ZERO
	check(player.position.y>-0.1 and player.position.z>231.8-260,"A2: open deck guard prevents walking off the edge")
	var chairs:=mission.get_node("FurnishingF01").get_children().filter(func(n):return str(n.name).contains("Chair"))
	var chair_good:=chairs.size()==int(plan.get("retained_f01_chairs",7))
	for c in chairs:chair_good=chair_good and c.find_children("*","CollisionObject3D",true,false).is_empty()
	check(chair_good,"Retained F01 chairs remain visual placeholders without independent movement blockers")
	var good:=true
	for node in mission.get_node("FurnishingF01").find_children("*","MeshInstance3D",true,false):
		var material: StandardMaterial3D=node.material_override if node.material_override else node.mesh.surface_get_material(0)
		if material.albedo_texture:
			good=good and material.albedo_texture.resource_path.begins_with("res://textures/greybox/") and material.uv1_triplanar and material.uv1_scale.is_equal_approx(Vector3.ONE) and node.scale.is_equal_approx(Vector3.ONE)
	check(good,"F01 authored furniture uses local Kenney metre projection at unit scale")
	var ray:=PhysicsRayQueryParameters3D.create(world(106,1.7,292),world(106,1.7,298),1,[player.get_rid()]);var hit:=space.intersect_ray(ray)
	check(not hit.is_empty() and hit.collider.name=="PressurePane","A1: transparent window remains physically sealed")
	await place(world(106,0.05,293))
	player.rotation.y=PI;player.test_direction=Vector2(0,-1);await ticks(100);player.test_direction=Vector2.ZERO
	check(player.position.z<294.2-260,"A1: player cannot walk through the exterior window")


func check_registration() -> void:
	var f02:=mission.get_node("RegistrationF02")
	var objects:=f02.get_node("Objects")
	check(f02.scene_file_path=="res://missions/freight/registration_f02.tscn" and objects.get_child_count()==33,"F02: saved placement scene reloads with 33 reusable assemblies after the office refinement")
	var reusable:=true
	for child in objects.get_children():reusable=reusable and not child.scene_file_path.is_empty() and child.scale.is_equal_approx(Vector3.ONE)
	check(reusable and objects.get_node("F1").scene_file_path==objects.get_node("F2").scene_file_path,"F02: props retain external scene links; matching light fixtures reuse one asset")
	var metric:=true
	var cubes:=true
	var count:=0
	for node in f02.find_children("*","MeshInstance3D",true,false):
		count+=1;cubes=cubes and node.mesh is BoxMesh
		var material: StandardMaterial3D=node.material_override if node.material_override else node.mesh.surface_get_material(0)
		if material.albedo_texture:
			metric=metric and material.albedo_texture.resource_path.begins_with("res://textures/greybox/") and material.uv1_triplanar and material.uv1_scale.is_equal_approx(Vector3.ONE) and node.global_basis.get_scale().is_equal_approx(Vector3.ONE)
		else:metric=metric and material.emission_enabled
	check(cubes and count>100,"F02: complete composition uses simple cuboids / "+str(count)+" visible blocks")
	check(metric,"F02: textured props keep 1 m local Kenney projection; untextured blocks are semantic displays/lights")
	check(f02.find_children("*","OmniLight3D",true,false).size()==8,"F02: all eight drawn light housings have corresponding light sources")
	var desk:=objects.get_node("RegistrationDesk")
	var chair_safe:=true
	for col in desk.get_node("Collision").get_children():chair_safe=chair_safe and not (str(col.name).begins_with("R4") or str(col.name).begins_with("R5"))
	check(chair_safe,"F02: both staff chairs remain visual-only inside the registration assembly")
	check(f02.get_node("CandidateItem1") is Marker3D and f02.get_node("CandidateItem2") is Marker3D,"F02: two item reservations are editor markers, with no new rewards or mission dependency")
	# Sweep standing capsules down both edges of each reserved 3 m ribbon.
	var shape:=CapsuleShape3D.new();shape.radius=0.3;shape.height=1.8
	var space:=mission.get_world_3d().direct_space_state
	var paths: Array=layout.registration.optional_routes.duplicate(true);paths.append(layout.registration.main_route)
	for path_index in paths.size():
		var clear:=true
		var path: Array=paths[path_index]
		for i in range(path.size()-1):
			var a:=world(path[i][0],0,path[i][1]);var b:=world(path[i+1][0],0,path[i+1][1]);var direction: Vector3=(b-a).normalized();var side:=direction.cross(Vector3.UP)
			for j in range(ceili(a.distance_to(b))+1):
				var p: Vector3=a.move_toward(b,float(j))
				for offset in [-1.19,0.0,1.19]:
					var sample_point: Vector3=p+side*offset;sample_point.y=registration_floor(sample_point)
					var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,sample_point+Vector3.UP);q.exclude=[player.get_rid()];q.collision_mask=1
					if not space.intersect_shape(q,1).is_empty():clear=false
		check(clear,"F02 route "+str(path_index)+": floor props, door frames and ceiling masses preserve the full 3 m ribbon")
	await place(world(109,0.05,274.5))
	player.rotation.y=PI;player.test_direction=Vector2(0,-1);await ticks(90);player.test_direction=Vector2.ZERO
	check(player.position.z<276.2-260 and absf(player.position.y)<0.1,"F02: substantial registration counter blocks the actual player")
	var ray:=PhysicsRayQueryParameters3D.create(world(109,1.9,277.95),world(109,3.5,277.95),1,[player.get_rid()]);var hit:=space.intersect_ray(ray)
	check(not hit.is_empty() and hit.position.y>=2.55 and hit.position.y<=2.71,"F02: canopy and task-light collision leave standing headroom behind the counter")
	var view_ray:=PhysicsRayQueryParameters3D.create(world(113,1.65,270),world(109,0.7,276.5),1,[player.get_rid()]);hit=space.intersect_ray(view_ray)
	check(not hit.is_empty() and hit.collider==desk.get_node("Collision"),"F02: counter is visible from the east entry without a partition blocking the first view")

func registration_floor(_point: Vector3) -> float:
	return float(layout.registration_floor.floor_y)
func traverse_level_floor(target: Vector3,mode: String) -> bool:
	var remaining:=Vector2(target.x-player.position.x,target.z-player.position.z)
	var budget:=ceili(remaining.length()/5*60)+120
	while remaining.length()>0.15 and budget>0:
		var direction:=Vector3(remaining.x,0,remaining.y).normalized()
		player.rotation.y=atan2(-direction.x,-direction.z)
		player.test_direction=Vector2(0,-1)
		if mode=="backpedal":player.rotation.y+=PI;player.test_direction=Vector2(0,1)
		if mode=="strafe":player.rotation.y=atan2(-direction.z,direction.x);player.test_direction=Vector2(1,0)
		await ticks(1);budget-=1
		remaining=Vector2(target.x-player.position.x,target.z-player.position.z)
	player.test_direction=Vector2.ZERO
	await ticks(8)
	return budget>0 and absf(player.position.y-registration_floor(target))<0.06 and player.is_grounded()
func check_registration_floor_and_door() -> void:
	var door: Node3D=mission.get_node("RegistrationF02/StaffDoor")
	check(door.scene_file_path=="res://interaction/sliding_door_wide.tscn" and door.get_node("StateChart/Movement/Blocked")!=null,"F03: ordinary staff door reloads as a reusable StateChart module")
	player.reset_player();await ticks(10)
	check(door.state_name()=="Closed" and is_zero_approx(door.open_amount),"F03: Backspace reset starts the staff door closed")
	await place(world(104.6,0.04,280));player.rotation.y=-PI/2;player.test_direction=Vector2(0,-1);await ticks(65);player.test_direction=Vector2.ZERO
	check(player.position.x<106-190-0.25,"F03: closed staff door physically blocks passage")
	check(await interact_node(door.get_node("SwitchBack"),Vector3.LEFT),"F03: waiting-side E switch opens without a keycard")
	await ticks(55);check(door.state_name()=="Open","F03: staff leaves retract into their wall pockets")
	await place(world(104.5,0.04,280))
	check(await walk_to(world(109,0,280)),"F03: player walks through the open staff doorway to the desk bay")
	check(await interact_node(door.get_node("SwitchFront"),Vector3.RIGHT),"F03: desk-side E switch closes the same door")
	await ticks(55);check(door.state_name()=="Closed","F03: opposite switch closes both leaves")
	door.request_toggle();await ticks(55)
	await place(world(106,0.04,280));door.request_toggle();await ticks(8)
	check(door.state_name()=="Blocked" and door.open_amount>0.99,"F03: occupied staff doorway refuses to close")
	await place(world(104.7,0.04,280));await ticks(8);door.request_toggle();await ticks(8)
	await place(world(106,0.04,280));await ticks(55)
	check(door.state_name()=="Blocked" and door.open_amount>0.99,"F03: entering during closure reverses the staff door")
	player.reset_player();await ticks(10)
	check(door.state_name()=="Closed" and is_zero_approx(door.open_amount),"F03: reset clears an obstructed door and returns physical leaves to closed")
	# Exact floor heights verify the flattened former strips and retained landing/desk floor.
	var samples: Array=[[112,270,0],[100,275,0],[100,284,0],[104,290,0],[103,280,0],[104.5,280,0],[106,280,0],[109,280,0],[109,274,0],[100,292.5,0]]
	var good:=true
	for p in samples:
		var ray:=PhysicsRayQueryParameters3D.create(world(p[0],0.4,p[1]),world(p[0],-0.6,p[1]),1,[player.get_rid()])
		var hit:=mission.get_world_3d().direct_space_state.intersect_ray(ray)
		# The closed door touches its threshold, so sample its floor after opening below.
		if p[0]==106:continue
		good=good and not hit.is_empty() and absf(hit.position.y-float(p[2]))<0.01
	check(good,"Registration: former walking strips, work bays and staff landing share floor 0 m")
	var crossings: Array=[[[113.8,270],[111.8,270]],[[100,272],[97.4,272]],[[102.5,280],[105,280]],[[100,283],[100,285]],[[100,290],[100,292.5]],[[106,290],[108,290]],[[100.5,273],[102.5,274.5]]]
	for mode in ["walk","sprint","backpedal","strafe"]:
		var passed:=true
		if mode=="sprint":Input.action_press("gym_sprint")
		for pair in crossings:
			for reverse in [false,true]:
				var a: Array=pair[1] if reverse else pair[0];var b: Array=pair[0] if reverse else pair[1]
				var start:=world(a[0],0,a[1]);start.y=registration_floor(start)+0.04
				await place(start)
				if not await traverse_level_floor(world(b[0],0,b[1]),mode):passed=false;print("REGISTRATION_CROSSING_FAIL: ",mode," / ",a," -> ",b," / ",player.position)
		Input.action_release("gym_sprint")
		check(passed,"F03: "+mode+" crosses all seven former-step/threshold/diagonal samples on the flat floor in both directions")
	# Subsequent furnished-route checks intentionally walk through an open staff door.
	await place(world(100,0.04,280));door.request_toggle();await ticks(55)
	check(door.state_name()=="Open","F03: staff door opens again after traversal/reset tests")
	var objects:=mission.get_node("RegistrationF02/Objects")
	check(objects.get_node("O_C1").find_children("*","CollisionObject3D",true,false).is_empty() and objects.get_node("O_C2").find_children("*","CollisionObject3D",true,false).is_empty(),"F03: office chairs are visual-only, preserving retreat movement")
	check(objects.get_node("O_S1/Visual").get_child_count()==18,"F03: both server racks retain their saved housings, drawers and status displays")


func check_screening() -> void:
	var f04:=mission.get_node("ScreeningF04")
	var objects:=f04.get_node("Objects")
	check(f04.scene_file_path=="res://missions/freight/screening_f04.tscn" and objects.get_child_count()==15,"F04: saved Screening placement scene reloads with 15 external prop assemblies")
	var linked:=true
	var metric:=true
	var count:=0
	for node in objects.get_children():linked=linked and not node.scene_file_path.is_empty() and node.scale.is_equal_approx(Vector3.ONE)
	for node in f04.find_children("*","MeshInstance3D",true,false):
		count+=1
		var material: StandardMaterial3D=node.material_override
		metric=metric and node.mesh is BoxMesh and node.global_basis.get_scale().is_equal_approx(Vector3.ONE)
		if material.albedo_texture:metric=metric and material.albedo_texture.resource_path.begins_with("res://textures/greybox/") and material.uv1_triplanar and material.uv1_scale.is_equal_approx(Vector3.ONE)
		else:metric=metric and material.emission_enabled
	check(linked and metric,"F04: reusable cuboid assets preserve metre Kenney projection / "+str(count)+" blocks")
	check(objects.get_node("s3").find_children("*","CollisionObject3D",true,false).is_empty() and objects.get_node("S3").has_node("Collision") and objects.get_node("S3").scene_file_path!=objects.get_node("s3").scene_file_path,"F04: operator desk and visual-only chair remain distinct saved assets")
	check(f04.find_children("*","OmniLight3D",true,false).size()==4,"F04: all four light housings contain actual light sources")
	var shape:=CapsuleShape3D.new();shape.radius=0.3;shape.height=1.8
	var space:=mission.get_world_3d().direct_space_state
	for route in layout.screening.routes:
		var clear:=true
		var points: Array=route.points
		for i in range(points.size()-1):
			var a:=world(points[i][0],0,points[i][1]);var b:=world(points[i+1][0],0,points[i+1][1]);var side: Vector3=(b-a).normalized().cross(Vector3.UP)
			for j in range(ceili(a.distance_to(b)*2)+1):
				var at: Vector3=a.move_toward(b,j*.5)
				for offset in [-float(route.width)/2+.31,0,float(route.width)/2-.31]:
					var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+side*offset+Vector3.UP);q.collision_mask=1;q.exclude=[player.get_rid()]
					if not space.intersect_shape(q,1).is_empty():clear=false;print("F04_RIBBON_BLOCK: ",route.name," / ",at+side*offset)
		check(clear,"F04: full reserved standing ribbon / "+str(route.name))
	var journeys: Array=[[[97,272],[88,272],[88,277]],[[88,272],[88,268],[80.5,268]],[[88,272],[84.4,272]]]
	for mode in ["walk","sprint","backpedal","strafe"]:
		var good:=true
		if mode=="sprint":Input.action_press("gym_sprint")
		for route in journeys:
			for reverse in [false,true]:
				var path: Array=route.duplicate(true)
				if reverse:path.reverse()
				await place(world(path[0][0],.05,path[0][1]))
				for q in path.slice(1):
					if not await traverse_level_floor(world(q[0],0,q[1]),mode):good=false;print("F04_TRAVERSE_FAIL: ",mode," / ",q)
		Input.action_release("gym_sprint")
		check(good,"F04: "+mode+" through scanner, branch, counter approach and exit in both directions")
	var heights: Array=[[90.7,272,2.8],[88,276,3.2],[88,263.5,3.25],[89,273.5,3.5],[82.5,272,3.325]]
	for sample in heights:
		var ray:=PhysicsRayQueryParameters3D.create(world(sample[0],2.5,sample[1]),world(sample[0],4,sample[1]),1,[player.get_rid()])
		var hit:=space.intersect_ray(ray)
		check(not hit.is_empty() and absf(hit.position.y-float(sample[2]))<.015,"F04: scanner/frame/rib/ceiling/corner height at "+str(sample.slice(0,2))+" = "+str(sample[2]))
	await place(world(92,0.05,272))
	player.rotation.y=0;player.test_direction=Vector2(0,-1);await ticks(100);player.test_direction=Vector2.ZERO
	check(player.position.z>269.3-260,"F04: baggage equipment remains a substantial player blocker")
	var ray:=PhysicsRayQueryParameters3D.create(world(94,1.65,272),world(90.7,1.3,270.1),1,[player.get_rid()]);var hit:=space.intersect_ray(ray)
	check(not hit.is_empty() and hit.collider==objects.get_node("ScanArch/Collision"),"F04: scan frame is visible from the Registration approach")
