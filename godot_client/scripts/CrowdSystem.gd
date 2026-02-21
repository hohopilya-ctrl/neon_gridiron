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
			
		var pos = Vector3(x, randf_range(1, 5), z)
		var basis = Basis().rotated(Vector3.UP, randf_range(0, TAU))
		multimesh.set_instance_transform(i, Transform3D(basis, pos))
		
		# Neon color
		var color = Color(randf(), randf(), 1.0) # Bluish neon
		multimesh.set_instance_color(i, color)

func update_excitement(amount: float):
	# Make crowd pulse/shake with excitement
	pass
