extends SceneTree
var gym: Node3D
var player: CharacterBody3D
var door: Node3D

func _initialize() -> void:
	call_deferred("run")

func ticks(count: int) -> void:
	for i in count:
		await physics_frame
	await process_frame

func place(position: Vector3, target: Vector3) -> void:
	player.position = position
	player.velocity = Vector3.ZERO
	var direction := (target - (position + Vector3.UP * 1.65)).normalized()
	player.rotation.y = atan2(-direction.x, -direction.z)
	player.set("_pitch", asin(direction.y))
	player.reset_camera_interpolation()
	await ticks(4)

func capture(label: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://.godot/door_" + label + ".png")

func run() -> void:
	gym = load("res://gym/gym.tscn").instantiate()
	root.add_child(gym)
	player = gym.get_node("GymPlayer")
	player.control_override = true
	door = gym.get_node("DoorModule")
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await place(Vector3(2, 0.05, 7.7), Vector3(2, 1.7, 4))
	await capture("closed")
	await place(Vector3(3.5, 0.05, 5.9), Vector3(3.5, 1.35, 4.34))
	await capture("switch")
	player.try_interact()
	await ticks(60)
	await place(Vector3(2, 0.05, 7.7), Vector3(2, 1.7, 4))
	await capture("open")
	var prop := RigidBody3D.new()
	prop.freeze = true
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(0.65, 1, 0.65)
	shape.shape = box
	prop.add_child(shape)
	var mesh := MeshInstance3D.new()
	var cube := BoxMesh.new()
	cube.size = box.size
	var material := StandardMaterial3D.new()
	material.albedo_color = Color(0.9, 0.35, 0.16)
	cube.material = material
	mesh.mesh = cube
	prop.add_child(mesh)
	gym.add_child(prop)
	prop.position = Vector3(2, 0.5, 4)
	await ticks(4)
	door.request_toggle()
	await ticks(6)
	await capture("blocked")
	print("GYM_DOOR_CAPTURE: PASS")
	quit()
