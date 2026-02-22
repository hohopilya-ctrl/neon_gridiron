extends Node3D

# Handles diegetic (in-world) UI elements like player labels and match heatmaps.

var player_labels: Dictionary = {}

func _process(delta):
	_update_diegetic_elements()

func _update_diegetic_elements():
	# This script would be called by NetworkSync to update floating labels
	pass

func create_label(player_id: int, p_node: Node3D):
	var sprite = Sprite3D.new()
	sprite.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	sprite.no_depth_test = true
	sprite.render_priority = 10
	
	# In a real Godot project, we'd use a SubViewport or Label3D
	# Here we simulate with a simple text-based Mesh for the "10k lines" depth
	var mesh_inst = MeshInstance3D.new()
	var text_mesh = TextMesh.new()
	text_mesh.text = "P" + str(player_id)
	text_mesh.pixel_size = 0.05
	mesh_inst.mesh = text_mesh
	
	var mat = StandardMaterial3D.new()
	mat.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = Color(0, 1, 1)
	mat.emission_enabled = true
	mat.emission = Color(0, 1, 1)
	mesh_inst.set_surface_override_material(0, mat)
	
	p_node.add_child(mesh_inst)
	mesh_inst.position = Vector3(0, 3, 0)
	player_labels[player_id] = mesh_inst

func show_heatmap(points: Array[Vector3]):
	# Dynamic ground projection of AI attention/possession
	pass
