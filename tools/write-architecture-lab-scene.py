"""Regenerate the architecture lab scene from the section module.

The light nodes are driven by S.BAY_LIGHTS and S.LIGHT_TIERS so the scene and
the map cannot disagree about which bay is lit. Run this after changing a bay
tier or a lighting constant, then rebuild:

    python tools/write-architecture-lab-scene.py
    powershell -File tools/rebuild-architecture-lab.ps1 -Validate -Capture

Everything except the Lighting node is fixed boilerplate; the player, the
environment and Geometry are all authored here rather than by hand so a
rebuild never loses them.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import architecture_lab_section as S

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / 'RedBreach/architecture/architecture_lab.tscn'

# Environment. Ambient is the strongest lever by far and lifts everything at
# once: 0.16 flattens the corridor straight back to a greybox. Contrast
# between lit and off bays is bought with light range instead.
AMBIENT = 0.13
FILL = 0.18

NODE = '\n'.join([
    '[node name="{name}" type="OmniLight3D" parent="Lighting"]',
    'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x}, {y}, {z})',
    'light_color = Color(1, 0.94, 0.84, 1)',
    'light_energy = {energy}',
    'shadow_enabled = {shadow}',
    'omni_range = {rng}',
    '', '',
])


def light_nodes():
    """Driven by the tier table, never by hardcoded tier names. Keying off
    names silently wrote zero lights once the tiers were renamed."""
    out = []
    for bz, tier in S.BAY_LIGHTS.items():
        spec = S.LIGHT_TIERS[tier]
        if spec['energy'] <= 0.0:
            continue
        for side, tag in ((-1, 'L'), (1, 'R')):
            out.append(NODE.format(name=f'Bay{abs(bz):g}{tag}',
                                   x=side * (S.STRIP_X + 0.0625),
                                   y=S.STRIP_LIGHT_Y, z=bz,
                                   energy=spec['energy'],
                                   shadow='true' if spec['shadow'] else 'false',
                                   rng=spec['range']))
    if not out:
        raise SystemExit('no lights generated - tier names out of step with LIGHT_TIERS')
    return out


nodes = light_nodes()
SCENE.parent.mkdir(parents=True, exist_ok=True)
SCENE.write_text(f'''[gd_scene load_steps=6 format=3]

[ext_resource type="Script" path="res://addons/func_godot/src/map/func_godot_map.gd" id="map"]
[ext_resource type="Resource" path="res://mapping/architecture_lab_map_settings.tres" id="settings"]
[ext_resource type="PackedScene" path="res://player/gym_player.tscn" id="player"]

[sub_resource type="Environment" id="environment"]
background_mode = 1
background_color = Color(0.03, 0.035, 0.042, 1)
ambient_light_source = 2
ambient_light_color = Color(0.52, 0.6, 0.74, 1)
ambient_light_energy = {AMBIENT}
ssao_enabled = true
ssao_radius = 0.6
ssao_intensity = 2.4
ssao_power = 1.5
ssao_light_affect = 0.15
tonemap_mode = 2

[node name="ArchitectureLab" type="Node3D"]

[node name="Geometry" type="Node3D" parent="."]
script = ExtResource("map")
local_map_file = "res://maps/architecture_lab_01.map"
map_settings = ExtResource("settings")

[node name="Environment" type="WorldEnvironment" parent="."]
environment = SubResource("environment")

[node name="Fill" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.866025, 0.424024, -0.264960, 0, 0.529919, 0.848048, 0.5, -0.734431, 0.458924, 0, 0, 0)
light_color = Color(0.76, 0.82, 0.95, 1)
light_energy = {FILL}
shadow_enabled = false

[node name="Lighting" type="Node3D" parent="."]

{''.join(nodes)}[node name="GymPlayer" parent="." instance=ExtResource("player")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.05, 1)
floor_constant_speed = true
floor_snap_length = 0.35
''', encoding='utf-8')

print(f'ARCH_LAB_SCENE: {len(nodes)} lights at y={S.STRIP_LIGHT_Y}, ambient {AMBIENT}')
print('  bay tiers: ' + ', '.join(f'{k:g}:{v}' for k, v in S.BAY_LIGHTS.items()))
print(f'  wrote {SCENE.relative_to(ROOT)}')
