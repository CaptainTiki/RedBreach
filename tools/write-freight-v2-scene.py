"""Write the freight v2 G-01 scene (RedBreach/missions/freight_v2/freight_v2.tscn).

Everything that belongs to a room lives in the MAP (lights and ladders are map entities), so this scene only holds
what the whole level shares: the environment, navigation (baked by the build), the level script and the player
with its climb chart. Rewriting it never touches a room.

    python tools/write-freight-v2-scene.py
    powershell -File tools/rebuild-freight-v2.ps1 -Validate
"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import freight_v2 as F

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'RedBreach/missions/freight_v2/freight_v2.tscn'

scene = '''[gd_scene format=3]

[ext_resource type="Script" path="res://addons/func_godot/src/map/func_godot_map.gd" id="map"]
[ext_resource type="Resource" path="res://mapping/freight_v2_map_settings.tres" id="settings"]
[ext_resource type="PackedScene" path="res://player/gym_player.tscn" id="player"]
[ext_resource type="Script" path="res://missions/freight_v2/freight_player.gd" id="player_script"]
[ext_resource type="Script" path="res://missions/freight_v2/freight_v2.gd" id="level"]
[ext_resource type="Script" path="res://addons/godot_state_charts/state_chart.gd" id="chart"]
[ext_resource type="Script" path="res://addons/godot_state_charts/compound_state.gd" id="compound"]
[ext_resource type="Script" path="res://addons/godot_state_charts/atomic_state.gd" id="atomic"]
[ext_resource type="Script" path="res://addons/godot_state_charts/transition.gd" id="transition"]

[sub_resource type="Environment" id="env_off"]
background_mode = 1
background_color = Color(0.02, 0.02, 0.025, 1)
ambient_light_source = 2
ambient_light_color = Color(0.55, 0.62, 0.76, 1)
ambient_light_energy = 0.12
reflected_light_source = 1
tonemap_mode = 2

[sub_resource type="Environment" id="env_subtle"]
background_mode = 1
background_color = Color(0.02, 0.02, 0.025, 1)
ambient_light_source = 2
ambient_light_color = Color(0.55, 0.62, 0.76, 1)
ambient_light_energy = 0.12
reflected_light_source = 1
tonemap_mode = 3
ssao_enabled = true
ssao_radius = 0.8
ssao_intensity = 2.2
ssao_light_affect = 0.15
glow_enabled = true
glow_intensity = 0.7
glow_strength = 1.0
glow_bloom = 0.02
glow_blend_mode = 1
glow_hdr_threshold = 1.1
volumetric_fog_enabled = true
volumetric_fog_density = 0.012
volumetric_fog_albedo = Color(0.45, 0.48, 0.52, 1)
volumetric_fog_length = 64.0
volumetric_fog_ambient_inject = 0.02
adjustment_enabled = true
adjustment_contrast = 1.08
adjustment_saturation = 1.12

[node name="FreightV2" type="Node3D"]
script = ExtResource("level")
env_levels = [SubResource("env_off"), SubResource("env_subtle")]

[node name="Geometry" type="Node3D" parent="."]
script = ExtResource("map")
local_map_file = "res://maps/freight_v2_01.map"
map_settings = ExtResource("settings")

[node name="Navigation" type="NavigationRegion3D" parent="."]

[node name="Environment" type="WorldEnvironment" parent="."]
environment = SubResource("env_subtle")

[node name="GymPlayer" parent="." groups=["freight_player"] instance=ExtResource("player")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.05, 25)
floor_constant_speed = true
floor_snap_length = 0.35
script = ExtResource("player_script")
gym_title = "FREIGHT V2 G-01"

[node name="ClimbChart" type="Node" parent="GymPlayer"]
script = ExtResource("chart")

[node name="Movement" type="Node" parent="GymPlayer/ClimbChart"]
process_mode = 4
script = ExtResource("compound")
initial_state = NodePath("Grounded")

[node name="Grounded" type="Node" parent="GymPlayer/ClimbChart/Movement"]
process_mode = 4
script = ExtResource("atomic")

[node name="Climbing" type="Node" parent="GymPlayer/ClimbChart/Movement"]
process_mode = 4
script = ExtResource("atomic")

[node name="Transition0" type="Node" parent="GymPlayer/ClimbChart/Movement"]
script = ExtResource("transition")
to = NodePath("../Climbing")
event = &"climb"
delay_in_seconds = "0.0"

[node name="Transition1" type="Node" parent="GymPlayer/ClimbChart/Movement"]
script = ExtResource("transition")
to = NodePath("../Grounded")
event = &"done"
delay_in_seconds = "0.0"
'''
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_bytes(scene.encode('utf-8'))
(OUT.parent / 'freight_v2_data.json').write_text(json.dumps({'views': F.VIEWS_3D}, indent=1), encoding='utf-8')
print('FREIGHT_V2_SCENE:', OUT.relative_to(ROOT))
