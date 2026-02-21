extends Node3D

var udp := PacketPeerUDP.new()
var players: Array[Node3D] = []
var ball: Node3D
var packet_count: int = 0
var world_env: WorldEnvironment

func _ready():
	var err = udp.bind(4242)
	if err == OK:
		print("UDP listening on port 4242")
	else:
		print("UDP Bind Error: ", err)
	
	var label = Label.new()
	label.name = "DebugLabel"
	label.text = "Waiting for UDP on port 4242..."
	label.position = Vector2(20, 20)
	add_child(label)
	
	# We are a child of Arena, so other nodes are our siblings, accessed with "../"
	ball = get_node_or_null("../Ball")
	for i in range(14):
		var p = get_node_or_null("../Player_" + str(i))
		if p:
			players.append(p)
			
			# Create a particle system for dashing
			var pfx = GPUParticles3D.new()
			pfx.name = "DashParticles"
			pfx.emitting = false
			pfx.amount = 40
			pfx.lifetime = 0.6
			pfx.one_shot = true
			pfx.explosiveness = 0.9
			
			var process_mat = ParticleProcessMaterial.new()
			process_mat.direction = Vector3(0, 1, 0)
			process_mat.spread = 180.0
			process_mat.initial_velocity_min = 2.0
			process_mat.initial_velocity_max = 5.0
			process_mat.gravity = Vector3(0, -3.0, 0)
			process_mat.scale_min = 0.05
			process_mat.scale_max = 0.15
			process_mat.color = Color(1.0, 1.0, 1.0, 0.8)
			
			pfx.process_material = process_mat
			
			var quad = QuadMesh.new()
			var mat = StandardMaterial3D.new()
			mat.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
			mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			mat.emission_enabled = true
			mat.emission_energy_multiplier = 2.0
			
			if i < 7: # Team 0 (Blue)
				mat.albedo_color = Color(0.2, 0.8, 1.0, 0.8)
				mat.emission = Color(0.1, 0.5, 1.0)
			else:     # Team 1 (Red)
				mat.albedo_color = Color(1.0, 0.3, 0.5, 0.8)
				mat.emission = Color(1.0, 0.1, 0.2)
				
			quad.material = mat
			pfx.draw_pass_1 = quad
			
			p.add_child(pfx)
			
			var stam_mesh = QuadMesh.new()
			stam_mesh.size = Vector2(2.5, 0.3)
			var stam_node = MeshInstance3D.new()
			stam_node.name = "StaminaBar"
			stam_node.mesh = stam_mesh
			stam_node.position = Vector3(0, 2.5, 0)
			
			var smat = StandardMaterial3D.new()
			smat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
			smat.albedo_color = Color(0.2, 1.0, 0.2)
			smat.emission_enabled = true
			smat.emission = Color(0, 1, 0)
			stam_node.material_override = smat.duplicate()
			p.add_child(stam_node)
			
			# Motion Trail
			var trail = GPUParticles3D.new()
			trail.name = "MotionTrail"
			trail.amount = 50
			trail.lifetime = 0.5
			var tmat = ParticleProcessMaterial.new()
			tmat.gravity = Vector3(0, 0, 0)
			tmat.initial_velocity_min = 0.0
			tmat.initial_velocity_max = 0.0
			tmat.scale_min = 0.5
			tmat.scale_max = 0.8
			tmat.color = Color(0, 0.5, 1, 0.3) if i < 7 else Color(1, 0, 0.2, 0.3)
			trail.process_material = tmat
			
			var t_quad = QuadMesh.new()
			var t_mat = StandardMaterial3D.new()
			t_mat.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
			t_mat.vertex_color_use_as_albedo = true
			t_mat.albedo_color = Color(1, 1, 1, 0.5)
			t_mat.billboard_mode = StandardMaterial3D.BILLBOARD_PARTICLES
			t_quad.material = t_mat
			trail.draw_pass_1 = t_quad
			
			p.add_child(trail)
	var hud = CanvasLayer.new()
	hud.name = "HUD"
	add_child(hud)
	
	var top_bar = ColorRect.new()
	top_bar.color = Color(0, 0, 0, 0.6)
	top_bar.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top_bar.custom_minimum_size.y = 50
	hud.add_child(top_bar)
	
	var hbox = HBoxContainer.new()
	hbox.name = "HBoxContainer"
	hbox.set_anchors_preset(Control.PRESET_TOP_WIDE)
	hbox.custom_minimum_size.y = 50
	hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	hbox.add_theme_constant_override("separation", 200)
	hud.add_child(hbox)
	
	var score_b = Label.new()
	score_b.name = "ScoreBlue"
	score_b.text = "BLUE: 0"
	score_b.add_theme_font_size_override("font_size", 24)
	score_b.add_theme_color_override("font_color", Color(0.2, 0.8, 1))
	score_b.add_theme_color_override("font_outline_color", Color(0, 0.2, 0.5))
	score_b.add_theme_constant_override("outline_size", 4)
	hbox.add_child(score_b)
	
	var time_label = Label.new()
	time_label.name = "TimeLabel"
	time_label.text = "03:00"
	time_label.add_theme_font_size_override("font_size", 28)
	time_label.add_theme_color_override("font_color", Color(1, 0.9, 0.2))
	time_label.add_theme_color_override("font_outline_color", Color(1, 0.4, 0))
	time_label.add_theme_constant_override("outline_size", 4)
	hbox.add_child(time_label)
	
	var score_r = Label.new()
	score_r.name = "ScoreRed"
	score_r.text = "0 :RED"
	score_r.add_theme_font_size_override("font_size", 24)
	score_r.add_theme_color_override("font_color", Color(1, 0.3, 0.5))
	score_r.add_theme_color_override("font_outline_color", Color(0.5, 0, 0.1))
	score_r.add_theme_constant_override("outline_size", 4)
	hbox.add_child(score_r)
	
	var spec_label = Label.new()
	spec_label.name = "SpecLabel"
	spec_label.text = "SPECTACLE: 0.0"
	spec_label.position = Vector2(20, 60)
	spec_label.add_theme_font_size_override("font_size", 20)
	hud.add_child(spec_label)
	
	# Initial camera setup
	var cam = get_node_or_null("TVCamera")
	if not cam:
		cam = Camera3D.new()
		cam.name = "TVCamera"
		cam.set_script(load("res://scripts/TVCamera.gd"))
		add_child(cam)
		cam.position = Vector3(0, 30, 15)
		cam.rotation_degrees = Vector3(-60, 0, 0)
		cam.make_current()
		
	world_env = get_node_or_null("../WorldEnvironment")
	
	# Create Crowd (Phase 18)
	var crowd = Node3D.new()
	crowd.name = "CrowdSystem"
	crowd.set_script(load("res://scripts/CrowdSystem.gd"))
	add_child(crowd)
	
	# Create Stadium Billboards (Phase 18)
	_create_billboard("BoardLeft", Vector3(-35, 5, 0), Vector3(0, 90, 0))
	_create_billboard("BoardRight", Vector3(35, 5, 0), Vector3(0, -90, 0))

func _create_billboard(bname: String, pos: Vector3, rot: Vector3):
	var mesh_inst = MeshInstance3D.new()
	mesh_inst.name = bname
	var text_mesh = TextMesh.new()
	text_mesh.text = "PRO LEAGUE"
	text_mesh.pixel_size = 0.05
	mesh_inst.mesh = text_mesh
	
	var mat = StandardMaterial3D.new()
	mat.emission_enabled = true
	mat.emission = Color(0, 1, 1)
	mat.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	mesh_inst.set_surface_override_material(0, mat)
	
	add_child(mesh_inst)
	mesh_inst.global_position = pos
	mesh_inst.global_rotation_degrees = rot

func _process(delta):
	var label = get_node_or_null("DebugLabel")
	while udp.get_available_packet_count() > 0:
		packet_count += 1
		var pkt = udp.get_packet()
		var json_str = pkt.get_string_from_utf8()
		var state = JSON.parse_string(json_str)
		if state != null and typeof(state) == TYPE_DICTIONARY:
			if label: label.text = "Packets Recv: %d | Status: OK" % packet_count
			_update_visuals(state)
		else:
			if label: label.text = "Packets: %d | Parse Error: %s" % [packet_count, json_str.substr(0, 30)]

func _update_visuals(state: Dictionary):
	# Support v2.0.0 schema
	if not state.has("v") or state["v"] != "2.0.0":
		return
		
	# 1. Ball Update
	if ball and state.has("b"):
		var b_data = state["b"]
		var target_pos = Vector3(
			float(b_data["p"][0]) / 10.0 - 30.0,
			0.5,
			float(b_data["p"][1]) / 10.0 - 20.0
		)
		# Smooth interpolation
		ball.global_position = ball.global_position.lerp(target_pos, 0.4)
		
		var trail = ball.get_node_or_null("MotionTrail")
		if trail:
			var spin = float(b_data.get("s", 0.0))
			trail.emitting = true
			
	# 2. Players Update
	if state.has("p"):
		var p_list = state["p"]
		for i in range(min(p_list.size(), players.size())):
			var p_node = players[i]
			var p_data = p_list[i]
			
			var target_pos = Vector3(
				float(p_data["p"][0]) / 10.0 - 30.0,
				0.0,
				float(p_data["p"][1]) / 10.0 - 20.0
			)
			p_node.global_position = p_node.global_position.lerp(target_pos, 0.5)
			
			# Stamina Bar
			var sbar = p_node.get_node_or_null("StaminaBar")
			if sbar and p_data.has("stm"):
				var stm_val = max(0.01, float(p_data["stm"]))
				sbar.scale.x = stm_val
				
	# 3. HUD Updates
	if state.has("s"):
		var blue = get_node_or_null("HUD/HBoxContainer/ScoreBlue")
		var red = get_node_or_null("HUD/HBoxContainer/ScoreRed")
		if blue and red:
			blue.text = "BLUE: %d" % int(state["s"][0])
			red.text = "%d :RED" % int(state["s"][1])
			
	if state.has("t"):
		var tlabel = get_node_or_null("HUD/TimeLabel")
		if tlabel:
			var total_seconds = int(state["t"] / 60.0) # tick to seconds
			tlabel.text = "%02d:%02d" % [total_seconds / 60, total_seconds % 60]

	# 4. Handle Events
	if state.has("e"):
		for event in state["e"]:
			if event["t"] == "GOAL":
				_on_goal_scored()
			elif event["t"] == "KICK":
				# Maybe trigger a small kick effect
				pass
						
	if state.has("score"):
		var blue = get_node_or_null("HUD/HBoxContainer/ScoreBlue")
		var red = get_node_or_null("HUD/HBoxContainer/ScoreRed")
		if blue and red:
			blue.text = "BLUE: %d" % int(state["score"][0])
			red.text = "%d :RED" % int(state["score"][1])
			
			if int(state["score"][0]) + int(state["score"][1]) > last_total_score:
				_on_goal_scored()
				last_total_score = int(state["score"][0]) + int(state["score"][1])
			
	if state.has("time"):
		var tlabel = get_node_or_null("HUD/HBoxContainer/TimeLabel")
		if tlabel:
			var total_seconds = int(state["time"])
			var m = total_seconds / 60
			var s = total_seconds % 60
			tlabel.text = "%02d:%02d" % [m, s]
			
	if state.has("spec"):
		var slabel = get_node_or_null("HUD/SpecLabel")
		if slabel:
			slabel.text = "SPECTACLE: %.1f" % float(state["spec"])
			
	if state.has("lb"):
		var lb = state["lb"]
		var lb_text = ""
		for entry in lb:
			lb_text += "%s: %.0f\n" % [entry["name"], entry["val"]]
		
		var b1 = get_node_or_null("BoardLeft")
		if b1: b1.mesh.text = lb_text
		var b2 = get_node_or_null("BoardRight")
		if b2: b2.mesh.text = lb_text

var last_total_score = 0
func _on_goal_scored():
	# Simple slow-mo VFX
	Engine.time_scale = 0.3
	
	# Strobe Effect (Phase 17)
	if world_env:
		var env = world_env.environment
		env.background_energy_multiplier = 5.0
		await get_tree().create_timer(0.2).timeout
		env.background_energy_multiplier = 1.0
		
	# Crowd Excitement (Phase 18)
	var crowd = get_node_or_null("CrowdSystem")
	if crowd:
		crowd.update_excitement(1.0)
		
	await get_tree().create_timer(0.3).timeout
	Engine.time_scale = 1.0
