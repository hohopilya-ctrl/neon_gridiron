extends Node

# Post-Processing Pipeline Configuration for Godot 4.6
# Enables Bloom, Tonemapping, and Color Grading for the ULTRA aesthetic.

func setup_environment(world_env: WorldEnvironment):
	if not world_env: return
	
	var env = world_env.environment
	if not env:
		env = Environment.new()
		world_env.environment = env
		
	# 1. Bloom Settings (High intensity for Neon)
	env.glow_enabled = true
	env.glow_intensity = 0.8
	env.glow_strength = 1.0
	env.glow_bloom = 0.5
	env.glow_blend_mode = Environment.GLOW_BLEND_MODE_ADDITIVE
	
	# 2. Tonemapping (Filmic look)
	env.tonemap_mode = Environment.TONEMAP_FILMIC
	env.tonemap_exposure = 1.2
	env.tonemap_white = 6.0
	
	# 3. Fog and Sky (Deep atmosphere)
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.02, 0.02, 0.05)
	
	# 4. Color Grading (Cyberpunk Teal/Pink shift)
	env.adjustment_enabled = true
	env.adjustment_brightness = 1.1
	env.adjustment_contrast = 1.2
	env.adjustment_saturation = 1.3
	
	print("ULTRA Post-Processing Pipeline: ACTIVE")
