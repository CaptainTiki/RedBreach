extends "res://interaction/sliding_door.gd"
## Three-metre ordinary door; shared StateChart retains all interaction behavior.
func _update_leaves() -> void:
	left_leaf.position.x = -0.75 - open_amount * leaf_travel
	right_leaf.position.x = 0.75 + open_amount * leaf_travel
func reset_door() -> void:
	chart.send_event("reset")
func _on_state_entered(label: String) -> void:
	if label == "Closed":
		open_amount = 0.0
		_update_leaves()
	super(label)
