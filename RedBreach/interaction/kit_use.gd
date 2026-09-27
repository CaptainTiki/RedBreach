extends CollisionObject3D
## A usable part of a kit piece (a door leaf, a switch panel, a card): the player's E ray finds it and it hands the
## use to its owner, which decides what happens and what the prompt says.
var owner_kit: Node

func get_interaction_prompt() -> String:
	return owner_kit.use_prompt() if owner_kit != null else ""

func interact() -> bool:
	return owner_kit.use() if owner_kit != null else false
