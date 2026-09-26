@tool
extends Marker3D
## A validation marker placed in TrenchBroom (rb_route, rb_probe, rb_nav).
## func_godot copies the entity's key/value pairs into func_godot_properties;
## tools/validate_markers.gd reads them from any built scene.
@export var func_godot_properties: Dictionary = {}
