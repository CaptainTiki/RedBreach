"""Regenerate the architecture lab CORNER scene from the corner module.

Light nodes are placed from C.light_stations_walk(), the same call the map
generator uses for the emissive strips, so a fitting and its light can never
end up in different places. Run this after changing the path, a tier or a
lighting constant, then rebuild:

    python tools/write-architecture-lab-corner-scene.py
    powershell -File tools/rebuild-architecture-lab-corners.ps1 -Validate -Capture

Lights live under Lighting, a sibling of Geometry, so a rebuild never wipes them.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import architecture_lab_section as S
import architecture_lab_corner as C

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / 'RedBreach/architecture/architecture_lab_corners.tscn'

# Same environment as the straight run, so the corner is judged against a
# corridor the user has already accepted rather than against new lighting.
AMBIENT = 0.13
FILL = 0.18

NODE = '\n'.join([
    '[node name="{name}" type="OmniLight3D" parent="Lighting"]',
    'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x:.4f}, {y}, {z:.4f})',
    'light_color = Color(1, 0.94, 0.84, 1)',
    'light_energy = {energy}',
    'shadow_enabled = {shadow}',
    'omni_range = {rng}',
    '', '',
])


def light_nodes():
    """Driven by the tier table, never by hardcoded tier names - keying off
    names silently wrote zero lights in this lab once already."""
    thru_excl, branch_excl = C.t_exclusions()
    thru_pins, branch_start = C.t_pins()
    stations = [(m, sg, t, tr, C.WALK_PATH)
                for m, sg, t, tr in C.light_stations_walk(rib_exclude=thru_excl, rib_pins=thru_pins)]
    branch = C.t_branch_path()
    stations += [(m, sg, t, tr, branch)
                 for m, sg, t, tr in C.light_stations_walk(branch, branch_excl, branch_excl,
                                                          rib_start=branch_start)]
    out = []
    for mid, seg, t, tier, path in stations:
        spec = S.LIGHT_TIERS[tier]
        energy = C.light_energy(tier)
        if energy <= 0.0:
            continue
        for side, tag in ((-1, 'L'), (1, 'R')):
            x, z = C.world(seg, t, side * (S.STRIP_X + 0.0625), path)
            tee = 'T' if path is not C.WALK_PATH else ''
            out.append(NODE.format(name=f'Bay{tee}{mid:.0f}{tag}', x=x, y=S.STRIP_LIGHT_Y, z=z,
                                   energy=round(energy, 3),
                                   shadow='true' if spec['shadow'] else 'false',
                                   rng=spec['range']))
    if not out:
        raise SystemExit('no lights generated - tier names out of step with LIGHT_TIERS')
    return out


nodes = light_nodes()
spawn_z = C.WALK_PATH[0][1] + 1.0
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

[node name="ArchitectureLabCorners" type="Node3D"]

[node name="Geometry" type="Node3D" parent="."]
script = ExtResource("map")
local_map_file = "res://maps/architecture_lab_corners_01.map"
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
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.05, {spawn_z:g})
floor_constant_speed = true
floor_snap_length = 0.35
''', encoding='utf-8')

_, _, total = C.walk_metrics()
print(f'ARCH_CORNER_SCENE: {len(nodes)} lights at y={S.STRIP_LIGHT_Y}, ambient {AMBIENT}, plan {C.LIGHT_PLAN} (energy x{C.LIGHT_PLANS[C.LIGHT_PLAN]["energy_scale"]:g})')
print(f'  walk {total:.2f} m, spawn at z={spawn_z:g}')
print(f'  wrote {SCENE.relative_to(ROOT)}')
