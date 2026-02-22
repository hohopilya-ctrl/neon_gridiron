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
	
	# Initialize Phase 23 Visuals
	var pp = load("res://scripts/PostProcessing.gd").new()
	pp.setup_environment(world_env)
	
	var dui = Node3D.new()
	dui.name = "DiegeticUI"
	dui.set_script(load("res://scripts/DiegeticUI.gd"))
	add_child(dui)
	
	var director = Camera3D.new()
	director.name = "CinematicDirector"
	director.set_script(load("res://scripts/CinematicDirector.gd"))
	add_child(director)
	director.make_current()
	
	var tv = Node3D.new()
	tv.name = "ThoughtVisualizer"
	tv.set_script(load("res://scripts/ThoughtVisualizer.gd"))
	add_child(tv)

	_create_billboard("BoardLeft", Vector3(-35, 5, 0), Vector3(0, 90, 0))
	_create_billboard("BoardRight", Vector3(35, 5, 0), Vector3(0, -90, 0))

func _update_billboards(state: Dictionary):
	var lb_text = "N E O N   U L T R A\n"
	if state.has("s"):
		lb_text += "%d  VS  %d\n" % [int(state["s"][0]), int(state["s"][1])]
	
	if state.has("t"):
		lb_text += "TICK: %d" % int(state["t"])
		
	var b1 = get_node_or_null("BoardLeft")
	if b1: b1.mesh.text = lb_text
	var b2 = get_node_or_null("BoardRight")
	if b2: b2.mesh.text = lb_text

func _create_billboard(bname: String, pos: Vector3, rot: Vector3):
	var mesh_inst = MeshInstance3D.new()
	mesh_inst.name = bname
	var text_mesh = TextMesh.new()
	text_mesh.text = "ULTRA"
	text_mesh.pixel_size = 0.08
	text_mesh.depth = 0.1
	mesh_inst.mesh = text_mesh
	
	var mat = StandardMaterial3D.new()
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = Color(0, 1, 1, 0.5)
	mat.emission_enabled = true
	mat.emission = Color(0, 0.8, 1.0)
	mat.emission_energy_multiplier = 2.0
	mat.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
	mesh_inst.set_surface_override_material(0, mat)
	
	add_child(mesh_inst)
	mesh_inst.global_position = pos
	mesh_inst.global_rotation_degrees = rot

var state_buffer: Array = []
var buffer_max_size: int = 5
var lerp_time: float = 0.0
var tick_rate: float = 1.0 / 60.0

func _process(delta):
	var label = get_node_or_null("DebugLabel")
	
	# 1. Receiver: Collect packets into buffer
	while udp.get_available_packet_count() > 0:
		packet_count += 1
		var pkt = udp.get_packet()
		var state = MsgPack.unpack(pkt)
		if state != null and typeof(state) == TYPE_DICTIONARY:
			state_buffer.append(state)
			if state_buffer.size() > buffer_max_size:
				state_buffer.remove_at(0)
			if label: label.text = "Packets Recv: %d | Buffer: %d" % [packet_count, state_buffer.size()]

	# 2. Replay: Smoothly interpolate between states
	if state_buffer.size() >= 2:
		lerp_time += delta
		var t = lerp_time / tick_rate
		
		if t >= 1.0:
			state_buffer.remove_at(0)
			lerp_time = 0.0
			t = 0.0
			
		if state_buffer.size() >= 2:
			_interpolate_visuals(state_buffer[0], state_buffer[1], t)

func _interpolate_visuals(s1: Dictionary, s2: Dictionary, t: float):
	# Interpolate Ball
	if ball and s1.has("b") and s2.has("b"):
		var p1 = _raw_to_vec3(s1["b"]["p"])
		var p2 = _raw_to_vec3(s2["b"]["p"])
		ball.global_position = p1.lerp(p2, t)
		
	# Interpolate Players
	if s1.has("p") and s2.has("p"):
		var p1_list = s1["p"]
		var p2_list = s2["p"]
		for i in range(min(p1_list.size(), p2_list.size(), players.size())):
			var v1 = _raw_to_vec3(p1_list[i]["p"])
			var v2 = _raw_to_vec3(p2_list[i]["p"])
			players[i].global_position = v1.lerp(v2, t)
			
			# Stamina Bar
			var sbar = players[i].get_node_or_null("StaminaBar")
			if sbar and p1_list[i].has("stm"):
				var stm_val = max(0.01, float(p1_list[i]["stm"]))
				sbar.scale.x = stm_val
				
			# Diegetic UI Update (Phase 23)
			var dui = get_node_or_null("DiegeticUI")
			if dui and not players[i].has_node("LabelMesh"):
				dui.create_label(i, players[i])

	# 3. Explainability Overlays (Phase 26)
	if s1.has("o"):
		var overlays = s1["o"]
		var tv = get_node_or_null("ThoughtVisualizer")
		if tv and overlays.has("attn") and overlays.has("v"):
			tv.update_thoughts(players, overlays["attn"], float(overlays["v"]))

	# Handle discreet UI elements (Score, Tick) from the latest state
	_update_ui(s1)

func _raw_to_vec3(raw) -> Vector3:
	return Vector3(
		float(raw[0]) / 10.0 - 30.0,
		0.0,
		float(raw[1]) / 10.0 - 20.0
	)

func _update_ui(state: Dictionary):
	_update_billboards(state)
	if state.has("s"):
		var blue = get_node_or_null("HUD/HBoxContainer/ScoreBlue")
		var red = get_node_or_null("HUD/HBoxContainer/ScoreRed")
		if blue and red:
			blue.text = "BLUE: %d" % int(state["s"][0])
			red.text = "%d :RED" % int(state["s"][1])
	# ... (remaining HUD updates)

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
			
	if state.has("t"):
		var tlabel = get_node_or_null("HUD/TimeLabel")
		if tlabel:
			var total_seconds = int(state["t"] / 60.0)
			var m = total_seconds / 60
			var s = total_seconds % 60
			tlabel.text = "%02d:%02d" % [m, s]
			
	# Update Shader uniform and Dynamic Lights
	if state.has("b"):
		var b_pos_raw = state["b"]["p"]
		var field_mesh = get_node_or_null("../Pitch")
		if field_mesh and field_mesh.material_override is ShaderMaterial:
			var uv_ball = Vector2(float(b_pos_raw[0]) / 600.0, float(b_pos_raw[1]) / 400.0)
			field_mesh.material_override.set_shader_parameter("ball_pos", uv_ball)

	# Update Player Auras/Lights
	if state.has("p"):
		var p_list = state["p"]
		for i in range(min(p_list.size(), players.size())):
			var p_node = players[i]
			var light = p_node.get_node_or_null("PulseLight")
			if not light:
				light = OmniLight3D.new()
				light.name = "PulseLight"
				light.omni_range = 8.0
				light.light_energy = 2.0
				light.light_color = Color(0.2, 0.8, 1.0) if i < 7 else Color(1.0, 0.3, 0.5)
				p_node.add_child(light)
			
	if state.has("m"):
		var crowd = get_node_or_null("CrowdSystem")
		if crowd and state["m"].has("mood"):
			crowd.update_excitement(float(state["m"]["mood"]))
			
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
