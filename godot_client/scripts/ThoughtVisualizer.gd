extends Node3D

# ULTRA Neural Explainability Viewer
# Renders 'thought' overlays like attention lines and value heatmaps.

var attention_lines: Array[MeshInstance3D] = []
var value_heatmap: MeshInstance3D

func _ready():
	_setup_heatmap()

func _setup_heatmap():
	var plane = PlaneMesh.new()
	plane.size = Vector2(60, 40)
	value_heatmap = MeshInstance3D.new()
	value_heatmap.mesh = plane
	value_heatmap.position.y = 0.05
	
	var mat = StandardMaterial3D.new()
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = Color(1, 1, 1, 0.2)
	mat.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	value_heatmap.set_surface_override_material(0, mat)
	add_child(value_heatmap)

func update_thoughts(players: Array, attn_data: Array, value: float):
	# 1. Update Heatmap color based on Value (Win Probability)
	# value range ~ -1.0 to 1.0 (ActorCritic output)
	var win_prob = clamp((value + 1.0) / 2.0, 0.0, 1.0)
	var mat = value_heatmap.get_surface_override_material(0)
	mat.albedo_color = Color(1.0 - win_prob, win_prob, 0.1, 0.2) # Red to Green
	
	# 2. Update Attention Lines
	_clear_lines()
	# attn_data is [14, 14] matrix
	for i in range(attn_data.size()):
		for j in range(attn_data[i].size()):
			if attn_data[i][j] > 0.5: # Strong attention link
				_draw_attention_line(players[i].global_position, players[j].global_position)

func _draw_attention_line(from: Vector3, to: Vector3):
	var mesh_inst = MeshInstance3D.new()
	var immediate_mesh = ImmediateMesh.new()
	mesh_inst.mesh = immediate_mesh
	
	var mat = StandardMaterial3D.new()
	mat.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = Color(0, 1, 1, 0.5)
	mat.no_depth_test = true
	
	immediate_mesh.surface_begin(Mesh.PRIMITIVE_LINES, mat)
	immediate_mesh.surface_add_vertex(from + Vector3(0, 1, 0))
	immediate_mesh.surface_add_vertex(to + Vector3(0, 1, 0))
	immediate_mesh.surface_end()
	
	add_child(mesh_inst)
	attention_lines.append(mesh_inst)

func _clear_lines():
	for line in attention_lines:
		line.queue_free()
	attention_lines.clear()
