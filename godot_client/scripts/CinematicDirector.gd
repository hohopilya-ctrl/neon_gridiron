extends Camera3D

# AI Cinematic Director for Neon Gridiron ULTRA
# Automatically chooses the best camera angle based on match intensity and ball position.

enum Mode { TV_PAN, PLAYER_FOLLOW, OVERHEAD, CINEMATIC_ACTION }
var current_mode = Mode.TV_PAN

var ball: Node3D
var players: Array[Node3D] = []
var target_pos: Vector3
var target_rot: Vector3

func _ready():
	# Wait for NetworkSync to spawn ball and players
	await get_tree().create_timer(1.0).timeout
	ball = get_tree().root.find_child("Ball", true, false)
	
	# Initial setup
	position = Vector3(0, 30, 20)
	look_at(Vector3.ZERO)

func _process(delta):
	if randf() < 0.002: # Occasional mode switch
		_switch_mode()
		
	match current_mode:
		Mode.TV_PAN:
			_mode_tv_pan(delta)
		Mode.PLAYER_FOLLOW:
			_mode_player_follow(delta)
		Mode.OVERHEAD:
			_mode_overhead(delta)
		Mode.CINEMATIC_ACTION:
			_mode_action(delta)

func _switch_mode():
	current_mode = Mode.values().pick_random()
	print("Cinematic Director: Switched to ", Mode.keys()[current_mode])

func _mode_tv_pan(delta):
	# Classic TV Side Pan
	var ball_pos = Vector3.ZERO
	if ball: ball_pos = ball.global_position
	
	target_pos = Vector3(ball_pos.x * 0.5, 20, 35)
	position = position.lerp(target_pos, delta * 2.0)
	_look_at_smoothed(ball_pos, delta)

func _mode_player_follow(delta):
	# Follow a random active player
	# (Logic to find a player near ball)
	var ball_pos = Vector3.ZERO
	if ball: ball_pos = ball.global_position
	
	target_pos = ball_pos + Vector3(0, 8, 12)
	position = position.lerp(target_pos, delta * 3.0)
	_look_at_smoothed(ball_pos, delta)

func _mode_overhead(delta):
	# Tactical overhead view
	target_pos = Vector3(0, 45, 0)
	position = position.lerp(target_pos, delta * 1.0)
	rotation_degrees = rotation_degrees.lerp(Vector3(-90, 0, 0), delta * 2.0)

func _mode_action(delta):
	# Extreme low-angle action shot
	var ball_pos = Vector3.ZERO
	if ball: ball_pos = ball.global_position
	
	target_pos = ball_pos + Vector3(5, 2, 5)
	position = position.lerp(target_pos, delta * 5.0)
	_look_at_smoothed(ball_pos, delta)

func _look_at_smoothed(target: Vector3, delta: float):
	var current_quat = Quaternion(basis)
	var target_dir = (target - global_position).normalized()
	if target_dir.length() > 0:
		var target_quat = Quaternion(Transform3D().looking_at(target).basis)
		basis = Basis(current_quat.slerp(target_quat, delta * 4.0))
