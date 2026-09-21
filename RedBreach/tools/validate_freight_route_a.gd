extends "res://tools/validate_freight.gd"
## Focused validation for the complete Route A furnishing pass.
func run() -> void:
	layout=JSON.parse_string(FileAccess.get_file_as_string("res://missions/freight/layout.json"))
	mission=load("res://missions/freight/freight_blockout.tscn").instantiate();mission.storage_enabled=false;root.add_child(mission)
	player=mission.get_node("GymPlayer");player.control_override=true;player.pistol.audio_enabled=false
	await ticks(50)
	var root_a:=mission.get_node("RouteAStyle")
	var plan: Dictionary=layout.route_a_style
	var metric:=true;var cubes:=true;var chair_clear:=true;var blocks:=0
	for node in root_a.find_children("*","MeshInstance3D",true,false):
		blocks+=1;cubes=cubes and node.mesh is BoxMesh
		var mat: StandardMaterial3D=node.material_override
		metric=metric and node.global_basis.get_scale().is_equal_approx(Vector3.ONE)
		if mat.albedo_texture:metric=metric and mat.albedo_texture.resource_path.begins_with("res://textures/greybox/") and mat.uv1_triplanar and mat.uv1_scale.is_equal_approx(Vector3.ONE)
	check(metric and cubes,"Route A: "+str(blocks)+" cuboids retain measured Kenney textures and unit placement scales")
	var space:=mission.get_world_3d().direct_space_state
	var floor_good:=true;var floor_notes: Array=[];var assembly_count:=0
	for group in root_a.get_children():
		if group is Label3D or group.name=="HatchReservations":continue
		for ob in group.get_children():
			if not ob.has_meta("layout_id"):continue
			assembly_count+=1
			if ob.get_meta("kind","")=="chair":chair_clear=chair_clear and ob.find_children("*","CollisionObject3D",true,false).is_empty()
	for o in plan.props:
		var node: Node3D=root_a.get_node(str(o.room)+"/"+str(o.id))
		floor_good=floor_good and not node.scene_file_path.is_empty()
		if o.kind in ["light","duct","display","hatch"]:continue
		var b: Array=o.bounds;var p:=world((b[0]+b[2])/2,o.bottom,(b[1]+b[3])/2)
		var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.025,p-Vector3.UP*.1,1,[player.get_rid()]);var hit:=space.intersect_ray(ray)
		if hit.is_empty() or absf(hit.position.y-o.bottom)>.035:floor_good=false;floor_notes.append(o.id)
	check(assembly_count==plan.props.size() and floor_good,"Route A: all "+str(assembly_count)+" external assemblies reload; floor props are supported at the intended elevation: "+str(floor_notes))
	check(chair_clear,"Route A: chair visuals add no separate retreat blockers")
	# A large enemy-sized cylinder validates emergence space, rather than just a player-centre point.
	var shape:=CylinderShape3D.new();shape.radius=1.0;shape.height=2.1
	for h in plan.hatches:
		var good:=true;var notes: Array=[]
		for dx in [-.45,0,.45]:
			for dz in [-.45,0,.45]:
				var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform.origin=world(h.center[0]+dx,h.floor+1.1,h.center[2]+dz);q.collision_mask=1;q.exclude=[player.get_rid()]
				if not space.intersect_shape(q,1).is_empty():good=false
		check(good,str(h.id)+": 3.5 m landing reserves large-enemy body clearance")
		var route: Array=h.emergence_route_paper_xz
		for i in route.size()-1:
			var a:=Vector2(route[i][0],route[i][1]);var b:=Vector2(route[i+1][0],route[i+1][1]);var count:=ceili(a.distance_to(b)/.4)
			for j in count+1:
				var v:=a.lerp(b,float(j)/maxi(1,count));var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform.origin=world(v.x,h.floor+1.1,v.y);q.collision_mask=1;q.exclude=[player.get_rid()]
				var hits:=space.intersect_shape(q,1)
				if not hits.is_empty():good=false;notes.append(str(v)+" "+str(hits[0].collider.get_path()));break
		check(good,str(h.id)+": emergence connects to the walking route for a 2 m wide body: "+str(notes))
		var pocket_shape:=BoxShape3D.new();var lo: Array=h.backing_volume_min;var hi: Array=h.backing_volume_max
		pocket_shape.size=Vector3(hi[0]-lo[0]-.04,hi[1]-lo[1]-.04,hi[2]-lo[2]-.04)
		var pocket_query:=PhysicsShapeQueryParameters3D.new();pocket_query.shape=pocket_shape;pocket_query.transform.origin=world((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2);pocket_query.collision_mask=1;pocket_query.exclude=[player.get_rid()]
		check(space.intersect_shape(pocket_query,1).is_empty(),str(h.id)+": reserved backing volume avoids existing occupied structure")
		var ray:=PhysicsRayQueryParameters3D.create(world(h.center[0],h.floor+2.2,h.center[2]),world(h.center[0],h.center[1]+.2,h.center[2]),1,[player.get_rid()]);var hit:=space.intersect_ray(ray)
		check(not hit.is_empty() and hit.position.y>=h.center[1]-.13,str(h.id)+": closed ceiling reservation is sealed and the vertical drop is unobstructed")
	# New overhead profiles retain full player access at the old frame edges; main route/gates/stairs live in validate_freight.
	var sh:=CapsuleShape3D.new();sh.radius=.3;sh.height=1.8
	var routes: Array=[]
	for route in layout.screening.routes:routes.append(route)
	for route in plan.working_routes:routes.append(route)
	for route in routes:
		var good:=true
		for i in route.points.size()-1:
			var a:=Vector2(route.points[i][0],route.points[i][1]);var b:=Vector2(route.points[i+1][0],route.points[i+1][1]);var dir: Vector2=(b-a).normalized();var normal:=Vector2(-dir.y,dir.x);var count:=ceili(a.distance_to(b)/.5)
			for j in count+1:
				for off in [-float(route.width)/2+.31,0,float(route.width)/2-.31]:
					var v: Vector2=a.lerp(b,float(j)/maxi(1,count))+normal*off
					var q:=PhysicsShapeQueryParameters3D.new();q.shape=sh;q.transform.origin=world(v.x,1.0,v.y);q.collision_mask=1;q.exclude=[player.get_rid()]
					if not space.intersect_shape(q,1).is_empty():good=false
		check(good,"A1 full-width working aisle: "+str(route.name))
	for route in plan.quality_walks:
		var points: Array=route.points;await place(world(points[0][0],route.floor+.05,points[0][1]));var good:=true;var journey:=points.duplicate(true);var reverse:=points.duplicate(true);reverse.reverse();journey.append_array(reverse)
		for p in journey:
			if not await walk_to(world(p[0],route.floor,p[1])):
				print("AISLE_BLOCK: ",route.name," target=",p," at=",player.position+Vector3(190,0,260));good=false;break
		check(good,"Side aisle out and back: "+str(route.name))
	print("FREIGHT_ROUTE_A_QA: ",checks," checks; ",failures.size()," failures")
	quit(0 if failures.is_empty() else 1)
