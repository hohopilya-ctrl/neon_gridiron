extends Node3D

@export var crowd_size: int = 1500
@export var stands_offset: float = 2.0

func _ready():
	var multimesh_inst = MultiMeshInstance3D.new()
	var multimesh = MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.use_colors = true
	multimesh.mesh = BoxMesh.new()
	(multimesh.mesh as BoxMesh).size = Vector3(0.3, 0.4, 0.1)
	
	multimesh.instance_count = crowd_size
	multimesh_inst.multimesh = multimesh
	add_child(multimesh_inst)
	
	for i in range(crowd_size):
		var x = randf_range(-40, 40)
		var z = randf_range(-30, 30)
		
		# Place only in stands (outside the 60x40 field, centered at 0,0)
		# Field is -30 to 30, -20 to 20
		if abs(x) < 32 and abs(z) < 22:
			# Shift outside
			if randf() > 0.5: x = sign(x) * randf_range(32, 40)
			else: z = sign(z) * randf_range(22, 30)
	# Generate rows of "spectators" (simple cubes/quads for performance)
	for x in range(20):
		for z in range(2):
			_spawn_spectator(Vector3(-35, 2, -20 + x * 2), Color(0.1, 0.4, 1.0)) # Blue side
			_spawn_spectator(Vector3(35, 2, -20 + x * 2), Color(1.0, 0.2, 0.4))  # Red side

func _spawn_spectator(pos: Vector3, color: Color):
	var mesh = BoxMesh.new()
	mesh.size = Vector3(0.5, 0.8, 0.5)
	var inst = MeshInstance3D.new()
	inst.mesh = mesh
	var mat = StandardMaterial3D.new()
	mat.albedo_color = Color(0.1, 0.1, 0.1) # Base dark
	mat.emission_enabled = true
	mat.emission = color * 0.2
	inst.set_surface_override_material(0, mat)
	add_child(inst)
	inst.global_position = pos
	crowd_members.append(inst)

func update_excitement(val: float):
	excitement = clamp(excitement + val, 0.0, 1.0)

func _process(delta):
	excitement = lerp(excitement, 0.0, delta * 0.5)
	for i in range(crowd_members.size()):
		var member = crowd_members[i]
		# Jump based on excitement
		var jump = sin(TIME * 10.0 + i) * excitement * 0.5
		member.position.y = 2.0 + max(0.0, jump)
		
		# Glow based on excitement
		var mat = member.get_surface_override_material(0)
		mat.emission_energy_multiplier = 0.2 + excitement * 5.0
# Make crowd pulse/shake with excitement
	pass
