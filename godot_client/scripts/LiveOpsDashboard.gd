extends Control

# High-end Meta-Game UI for ULTRA Phase 3.
# Displays league rankings, historical trends, and Hall of Fame.

var rankings: Array = []

func _ready():
	# UI layouting for Hall of Fame
	var panel = PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.custom_minimum_size = Vector2(800, 500)
	add_child(panel)
	
	var vbox = VBoxContainer.new()
	panel.add_child(vbox)
	
	var title = Label.new()
	title.text = "ULTRA LEAGUE HALL OF FAME"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 32)
	vbox.add_child(title)
	
	var spacer = Control.new()
	spacer.custom_minimum_size.y = 20
	vbox.add_child(spacer)
	
	# Scroll area for rankings
	var scroll = ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(scroll)
	
	var list = VBoxContainer.new()
	list.name = "RankList"
	scroll.add_child(list)
	
	# Close button
	var btn = Button.new()
	btn.text = "RETURN TO FIELD"
	btn.pressed.connect(hide)
	vbox.add_child(btn)

func update_rankings(data: Array):
	var list = find_child("RankList")
	if not list: return
	
	# Clear old
	for c in list.get_children():
		c.queue_free()
		
	# Populate new
	for entry in data:
		var item = HBoxContainer.new()
		var name = Label.new()
		name.text = entry["name"]
		name.custom_minimum_size.x = 200
		
		var elo = Label.new()
		elo.text = "ELO: " + str(entry["elo"])
		
		item.add_child(name)
		item.add_child(elo)
		list.add_child(item)

func show_dashboard():
	# Logic to switch camera to a "Hub" view and show UI
	show()
	# Request data from Python matchmaker
