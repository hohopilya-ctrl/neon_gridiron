extends Camera3D

@export var ball_path: NodePath = "../Ball"
@export var player_root: NodePath = ".."
@export var smooth_speed: float = 5.0
@export var zoom_speed: float = 2.0
@export var lead_factor: float = 0.5
@export var min_zoom: float = 20.0
@export var max_zoom: float = 45.0

var ball: Node3D

func _ready():
	ball = get_node_or_null(ball_path)
	
func _process(delta):
	if not ball: 
		ball = get_node_or_null(ball_path)
		return
		
	# 1. Calculate Target Position (Ball centered + Lead)
	var ball_vel = ball.get_meta("velocity", Vector3.ZERO) if ball.has_meta("velocity") else Vector3.ZERO
	var target_pos = ball.global_position + (ball_vel * lead_factor)
	target_pos.y = position.y # Keep height constant for now
	
	# 2. Dynamic Zoom (based on ball speed and player spread)
	var speed_zoom = ball_vel.length() * 0.5
	var target_y = clamp(min_zoom + speed_zoom, min_zoom, max_zoom)
	
	# 3. Smooth Lerp
	global_position.x = lerp(global_position.x, target_pos.x, smooth_speed * delta)
	global_position.z = lerp(global_position.z, target_pos.z, smooth_speed * delta)
	position.y = lerp(position.y, target_y, zoom_speed * delta)
	
	# 4. Stay within arena bounds (60x40 meters area centered at 0,0)
	# Physics is currently 0-60, 0-40. NetworkSync maps it to -30 to 30, -20 to 20.
	global_position.x = clamp(global_position.x, -25.0, 25.0)
	global_position.z = clamp(global_position.z, -15.0, 15.0)
	
	# Look at ball slightly
	var look_target = ball.global_position
	look_target.y = 0
	# look_at(look_target, Vector3.UP) # Uncomment for more dynamic feel, but can be nauseating
