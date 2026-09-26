"""Write the kit lab scene (RedBreach/kit/kit_lab.tscn) from tools/kit_lab.py.

Everything outside Geometry is authored here: the settled environment (the
subtle presentation), the sun and Mars dust, every light and fitting, doors
in their frames, the navigation region (baked by the build) and the player.

    python tools/write-kit-lab-scene.py
    powershell -File tools/rebuild-kit-lab.ps1 -Validate -Capture
"""
from pathlib import Path
import json
import math
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_lab as K
import style_lab as S

ROOT = Path(__file__).resolve().parents[1]
PROJ = ROOT / 'RedBreach'
OUT = PROJ / 'kit/kit_lab.tscn'


def G(x, h, y):
    return (x, h, -y)


def tf(pos, basis=None):
    if basis is None:
        return f'Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f})'
    x, y, z = basis
    return ('Transform3D(' + ', '.join(f'{v:.6f}' for v in (x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2]))
            + f', {pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f})')


def run_basis(d):
    """Local frame of a corridor heading d (plan): X right, Y up, Z back."""
    right = (d[1], 0.0, d[0])
    back = (-d[0], 0.0, d[1])
    return right, (0.0, 1.0, 0.0), back


def basis_looking(d):
    dx, dy, dz = d
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    f = (-dx / L, -dy / L, -dz / L)
    x = (f[2], 0.0, -f[0])
    xl = math.hypot(x[0], x[2]); x = (x[0] / xl, 0.0, x[2] / xl)
    y = (f[1] * x[2] - f[2] * x[1], f[2] * x[0] - f[0] * x[2], f[0] * x[1] - f[1] * x[0])
    return x, y, f


nodes, subs, meshes = [], [], {}
lights = 0
LIGHT = (0.86, 0.93, 1.0)
EMERGENCY = (1.0, 0.16, 0.1)
TIER = {'edge': (0.75, 8.0), 'low': (0.6, 6.0), 'flicker': (0.8, 8.0), 'dead': (0.0, 0.0), 'emergency': (0.6, 7.0),
        'floor': (1.0, 6.0), 'ceiling': (1.25, 9.0)}


def mesh(size):
    key = 'box_' + '_'.join(f'{v:g}'.replace('.', 'p') for v in size)
    if key not in meshes:
        meshes[key] = True
        subs.append(f'[sub_resource type="BoxMesh" id="{key}"]\nsize = Vector3({size[0]}, {size[1]}, {size[2]})\n')
    return key


def node(text):
    nodes.append(text)


def omni(parent, name, pos, col, energy, rng, shadow=True):
    global lights
    lights += 1
    node(f'[node name="{name}" type="OmniLight3D" parent="{parent}"]\ntransform = {tf(pos)}\n'
         f'light_color = Color({col[0]}, {col[1]}, {col[2]}, 1)\nlight_energy = {energy}\n'
         f'shadow_enabled = {"true" if shadow else "false"}\nomni_range = {rng}\nomni_attenuation = 1.2\n')


def fitting(parent, name, pos, size, material, basis=None):
    node(f'[node name="{name}" type="MeshInstance3D" parent="{parent}"]\ntransform = {tf(pos, basis)}\n'
         f'mesh = SubResource("{mesh(size)}")\nsurface_material_override/0 = SubResource("{material}")\ncast_shadow = 0\n')


# --- corridor bays --------------------------------------------------------------
def run_geometry(key):
    spec = K.RUNS[key]
    path, heights = spec['path'], spec['heights']
    lens, dirs = [], []
    for i in range(len(path) - 1):
        dx, dy = path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]
        L = math.hypot(dx, dy)
        lens.append(L); dirs.append((dx / L, dy / L))
    s0 = [0.0]
    for L in lens:
        s0.append(s0[-1] + L)

    def at(s):
        i = max(j for j in range(len(lens)) if s0[j] <= s + 1e-9)
        u = s - s0[i]
        t = u / lens[i]
        x = path[i][0] + dirs[i][0] * u
        y = path[i][1] + dirs[i][1] * u
        h = heights[i] + (heights[i + 1] - heights[i]) * t
        return (x, y, h), dirs[i]
    return at, s0[-1]


def bay_tiers(key, s_mid, s_lo, s_hi):
    if key == 'North' and s_lo <= K.RUNS['North']['fallen'] + 1e-6 <= s_hi:
        return ['flicker']
    if key == 'North' and s_lo > K.RUNS['North']['fallen'] + 1e-6:
        return ['dead']
    if key == 'C4':
        at, _ = run_geometry('C4')
        x = at(s_mid)[0][0]
        if K.X1['x0'] - 1.0 <= x <= K.X1['x1'] + 1.0:
            return ['dead', 'emergency']
    return ['edge', 'low']


node('[node name="Bays" type="Node3D" parent="Lighting"]\n')
bay_index = 0
for key, spec in K.RUNS.items():
    at, total = run_geometry(key)
    stops = [0.0] + sorted(spec['ribs'] + ([spec['fallen']] if 'fallen' in spec else [])) + [total]
    prof = spec['profile']
    # Bends: interior vertices where the heading turns (collinear stair
    # vertices only change slope). A fitting sits on a straight wall, never in
    # a mitre, so a bay that straddles a bend lights from its longer straight side.
    path = spec['path']
    bends, acc = [], 0.0
    for i in range(1, len(path) - 1):
        acc += math.dist(path[i - 1], path[i])
        a = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
        b = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
        if abs(a[0] * b[1] - a[1] * b[0]) > 1e-6:
            bends.append(acc)
    for lo, hi in zip(stops, stops[1:]):
        if hi - lo < 1.5:
            continue
        mid = (lo + hi) / 2
        near = [sb for sb in bends if abs(sb - mid) < 2.2]
        if near:
            sb = near[0]
            options = [c for c in (sb - 2.2, sb + 2.2) if lo + 0.6 <= c <= hi - 0.6]
            if not options:
                continue
            mid = max(options, key=lambda c: (hi - sb) if c > sb else (sb - lo))
        (x, y, h), d = at(mid)
        right, up, back = run_basis(d)
        bay = f'Lighting/Bays/{key}_{bay_index}'
        node(f'[node name="{key}_{bay_index}" type="Node3D" parent="Lighting/Bays"]\n')
        tiers = bay_tiers(key, mid, lo, hi)
        for tier in tiers:
            extra = ''
            if tier == 'flicker':
                extra = ('script = ExtResource("flicker")\nlit_material = SubResource("fitting")\n'
                         f'dead_material = SubResource("fitting_dead")\nseed = {31 + bay_index}\n')
            node(f'[node name="{tier}" type="Node3D" parent="{bay}"]\n{extra}')
            energy, rng = TIER[tier]
            for name, lp, fp, size, lit in S.tier_parts(tier, prof, 0.0):
                def place(p):
                    return (x + right[0] * p[0] + back[0] * p[2], h + p[1], -y + right[2] * p[0] + back[2] * p[2])
                if lp is not None and energy > 0:
                    omni(f'{bay}/{tier}', name, place(lp), EMERGENCY if tier == 'emergency' else LIGHT, energy, rng,
                         shadow=tier != 'floor')
                if fp is not None:
                    mat = ('fitting_red' if tier == 'emergency' else 'fitting') if lit else 'fitting_dead'
                    fitting(f'{bay}/{tier}', f'{name}_fitting', place(fp), size, mat, (right, up, back))
            if tier == 'flicker':
                ch = S.ceil_half(prof)
                p = (-(ch - 0.3), S.CEIL_Y - 0.1, 0.6)
                pos = (x + right[0] * p[0] + back[0] * p[2], h + p[1], -y + right[2] * p[0] + back[2] * p[2])
                node(f'[node name="Sparks" type="GPUParticles3D" parent="{bay}/{tier}"]\ntransform = {tf(pos)}\nemitting = false\n'
                     'amount = 28\nlifetime = 0.9\none_shot = true\nexplosiveness = 0.85\nlocal_coords = false\n'
                     'process_material = SubResource("spark_process")\ndraw_pass_1 = SubResource("spark_mesh")\n')
        bay_index += 1

# --- rooms ----------------------------------------------------------------------------
node('[node name="Rooms" type="Node3D" parent="Lighting"]\n')
# A0: two low fittings.
for i, y in enumerate((-1.2, 1.2)):
    fitting('Lighting/Rooms', f'A0_fit{i}', G(0.0, K.A0['ceil'] - 0.03, y), (2.0, 0.06, 0.3), 'fitting')
    omni('Lighting/Rooms', f'A0_{i}', G(0.0, K.A0['ceil'] - 0.4, y), LIGHT, 1.1, 7.0)
# Hub: a fitting on each clipped face's haunch, lights inside it.
hc = (K.HUB['cx'], K.HUB['cy'])
for i, ang in enumerate((45, 135, 225, 315)):
    a = math.radians(ang)
    fx, fy = hc[0] + math.cos(a) * 5.2, hc[1] + math.sin(a) * 5.2
    fitting('Lighting/Rooms', f'Hub_fit{i}', G(fx, 5.0, fy), (0.6, 0.08, 0.6), 'fitting')
    omni('Lighting/Rooms', f'Hub_{i}', G(hc[0] + math.cos(a) * 4.0, 4.4, hc[1] + math.sin(a) * 4.0), LIGHT, 1.6, 11.0)
# Hall: high-bay fittings under every portal frame, wash lights under the catwalk,
# coolant glow at the tanks.
Hh = K.HALL
hcx = (Hh['x0'] + Hh['x1']) / 2
for fy in Hh['frames']:
    for j, dx in enumerate((-4.0, 4.0)):
        fitting('Lighting/Rooms', f'Hall_fit_{fy:.0f}_{j}', G(hcx + dx, Hh['ceil'] - Hh['frame_d'] - 0.05, fy), (1.2, 0.1, 0.4), 'fitting')
        omni('Lighting/Rooms', f'Hall_{fy:.0f}_{j}', G(hcx + dx, Hh['ceil'] - 1.4, fy), LIGHT, 3.4, 18.0)
    # Wash fittings on each frame foot at 4.5 m, lighting the knee walls and floor.
    for j, x in enumerate((Hh['x0'] + Hh['frame_d'] + 0.1, Hh['x1'] - Hh['frame_d'] - 0.1)):
        fitting('Lighting/Rooms', f'Hall_wash_fit_{fy:.0f}_{j}', G(x, 4.5, fy), (0.12, 0.8, 0.5), 'fitting')
        omni('Lighting/Rooms', f'Hall_wash_{fy:.0f}_{j}', G(x + (0.9 if j == 0 else -0.9), 4.3, fy), LIGHT, 1.2, 11.0)
# Under the catwalk: fittings on the deck's underside every ~6 m, so the
# space below meets the light floor (it measured 0.11 before; floor 0.35).
under = [(23.0, Hh['y0'] + 1.5), (29.5, Hh['y0'] + 1.5), (36.0, Hh['y0'] + 1.5)] +         [(Hh['x1'] - 1.5, y) for y in (42.5, 48.5, 54.5, 60.5)]
for i, (x, y) in enumerate(under):
    along_x = y < Hh['y0'] + 2.0
    fitting('Lighting/Rooms', f'HallUnder_fit{i}', G(x, K.CATWALK['level'] - 0.33, y), (1.2, 0.05, 0.2) if along_x else (0.2, 0.05, 1.2), 'fitting')
    omni('Lighting/Rooms', f'HallUnder_{i}', G(x, K.CATWALK['level'] - 0.6, y), LIGHT, 0.9, 7.0, shadow=False)
# The north end beyond the last frame, and the stair foot: fittings on the north wall.
for i, x in enumerate((22.0, 34.0)):
    fitting('Lighting/Rooms', f'HallNorth_fit{i}', G(x, 4.5, Hh['y1'] - 0.08), (0.8, 0.12, 0.12), 'fitting')
    omni('Lighting/Rooms', f'HallNorth_{i}', G(x, 4.2, Hh['y1'] - 1.0), LIGHT, 1.4, 12.0)
# The stair foot, tucked beside the flight on the east wall.
fitting('Lighting/Rooms', 'HallStairFoot_fit', G(Hh['x1'] - 0.08, 1.6, Hh['y1'] - 1.2), (0.12, 0.12, 0.8), 'fitting')
omni('Lighting/Rooms', 'HallStairFoot', G(Hh['x1'] - 1.0, 1.5, Hh['y1'] - 1.2), LIGHT, 0.8, 6.0, shadow=False)
for i, (x, y) in enumerate(((26.0, Hh['y0'] + 3.0), (34.0, Hh['y0'] + 3.0))):
    fitting('Lighting/Rooms', f'Catwalk_strip_{i}', G(x, K.CATWALK['level'] + 0.02, y - 0.1), (6.0, 0.04, 0.08), 'fitting')
fitting('Lighting/Rooms', 'Catwalk_strip_e', G(Hh['x1'] - 3.0 + 0.1, K.CATWALK['level'] + 0.02, 51.0), (0.08, 0.04, 18.0), 'fitting')
omni('Lighting/Rooms', 'Catwalk_0', G(34.0, K.CATWALK['level'] + 0.5, Hh['y0'] + 1.5), LIGHT, 0.6, 6.0, shadow=False)
omni('Lighting/Rooms', 'Catwalk_1', G(Hh['x1'] - 1.5, K.CATWALK['level'] + 0.5, 56.0), LIGHT, 0.6, 6.0, shadow=False)
for i, (tx, ty) in enumerate(K.HALL_TANKS):
    omni('Lighting/Rooms', f'Coolant_{i}', G(tx - 2.8, 1.2, ty), (0.35, 1.0, 0.8), 0.8, 6.0, shadow=False)
# R1: two office fittings and the console glow.
Rr = K.R1
for i, y in enumerate((21.5, 24.5)):
    fitting('Lighting/Rooms', f'R1_fit{i}', G(-27.5, Rr['floor'] + Rr['ceil'] - 0.03, y), (1.6, 0.06, 0.3), 'fitting')
    omni('Lighting/Rooms', f'R1_{i}', G(-27.5, Rr['floor'] + Rr['ceil'] - 0.5, y), (1.0, 0.92, 0.82), 0.8, 7.0)
omni('Lighting/Rooms', 'R1_screens', G(Rr['consoles'][0] + 0.9, Rr['floor'] + 1.4, 23.0), (0.55, 1.0, 0.75), 0.45, 3.5, shadow=False)

# --- doors ------------------------------------------------------------------------------
door_nodes = []
for name, c, d, floor, kind, run_key, end in K.JUNCTIONS:
    if not kind.startswith('door'):
        continue
    door_kind = kind.split(':')[1]
    # A door sits mid-way through the room wall: in the profile-shaped panel
    # (door) or in the room's own wall (door_low, on the room's raised floor).
    fl = K.R1['floor'] if kind.startswith('door_low') else floor
    zc = (d[0], 0.0, -d[1])
    xc = (zc[2], 0.0, -zc[0])
    pos = G(c[0] - d[0] * K.ROOM_WALL / 2, fl, c[1] - d[1] * K.ROOM_WALL / 2)
    scene = 'door_wide' if door_kind == 'wide' else 'door'
    safe = name.replace(' ', '_')
    door_nodes.append(f'[node name="{safe}" parent="Doors" instance=ExtResource("{scene}")]\ntransform = {tf(pos, (xc, (0, 1, 0), zc))}\n')

# --- write ------------------------------------------------------------------------------
sun = basis_looking((1.0, -0.42, 0.18))
dust_x0, dust_x1 = -110.0, Rr['x0'] - 0.6
header = f'''[gd_scene format=3]

[ext_resource type="Script" path="res://addons/func_godot/src/map/func_godot_map.gd" id="map"]
[ext_resource type="Resource" path="res://mapping/kit_lab_map_settings.tres" id="settings"]
[ext_resource type="PackedScene" path="res://player/gym_player.tscn" id="player"]
[ext_resource type="Script" path="res://kit/kit_lab.gd" id="lab"]
[ext_resource type="Script" path="res://style/flicker_light.gd" id="flicker"]
[ext_resource type="PackedScene" path="res://interaction/sliding_door.tscn" id="door"]
[ext_resource type="PackedScene" path="res://interaction/sliding_door_wide.tscn" id="door_wide"]

[sub_resource type="ProceduralSkyMaterial" id="mars_sky"]
sky_top_color = Color(0.36, 0.22, 0.15, 1)
sky_horizon_color = Color(0.78, 0.55, 0.38, 1)
sky_curve = 0.12
ground_bottom_color = Color(0.22, 0.12, 0.08, 1)
ground_horizon_color = Color(0.7, 0.47, 0.33, 1)
sun_angle_max = 12.0
sun_curve = 0.08

[sub_resource type="Sky" id="sky"]
sky_material = SubResource("mars_sky")

[sub_resource type="Environment" id="env_off"]
background_mode = 2
sky = SubResource("sky")
ambient_light_source = 2
ambient_light_color = Color(0.55, 0.62, 0.76, 1)
ambient_light_energy = 0.12
reflected_light_source = 1
tonemap_mode = 2

[sub_resource type="Environment" id="env_subtle"]
background_mode = 2
sky = SubResource("sky")
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
fog_enabled = true
fog_mode = 1
fog_light_color = Color(0.58, 0.4, 0.29, 1)
fog_density = 1.0
fog_sky_affect = 0.0
fog_depth_begin = 60.0
fog_depth_end = 400.0
volumetric_fog_enabled = true
volumetric_fog_density = 0.012
volumetric_fog_albedo = Color(0.45, 0.48, 0.52, 1)
volumetric_fog_length = 64.0
volumetric_fog_ambient_inject = 0.02
adjustment_enabled = true
adjustment_contrast = 1.08
adjustment_saturation = 1.12

[sub_resource type="FogMaterial" id="mars_dust"]
density = 0.008
albedo = Color(0.95, 0.72, 0.52, 1)
emission = Color(0.025, 0.012, 0.006, 1)
height_falloff = 0.06
edge_fade = 0.15

[sub_resource type="StandardMaterial3D" id="fitting"]
shading_mode = 0
albedo_color = Color(0.92, 0.97, 1, 1)
emission_enabled = true
emission = Color(0.92, 0.97, 1, 1)
emission_energy_multiplier = 4.0

[sub_resource type="StandardMaterial3D" id="fitting_red"]
shading_mode = 0
albedo_color = Color(1, 0.2, 0.12, 1)
emission_enabled = true
emission = Color(1, 0.12, 0.06, 1)
emission_energy_multiplier = 3.0

[sub_resource type="StandardMaterial3D" id="fitting_dead"]
albedo_color = Color(0.16, 0.17, 0.18, 1)
roughness = 0.6
metallic_specular = 0.6

[sub_resource type="ParticleProcessMaterial" id="spark_process"]
direction = Vector3(0.3, -1, 0)
spread = 55.0
initial_velocity_min = 1.2
initial_velocity_max = 3.2
gravity = Vector3(0, -9.8, 0)
scale_min = 0.6
scale_max = 1.2

[sub_resource type="StandardMaterial3D" id="spark_material"]
shading_mode = 0
albedo_color = Color(1, 0.72, 0.3, 1)
emission_enabled = true
emission = Color(1, 0.62, 0.2, 1)
emission_energy_multiplier = 8.0

[sub_resource type="BoxMesh" id="spark_mesh"]
material = SubResource("spark_material")
size = Vector3(0.025, 0.025, 0.06)

'''
body = f'''[node name="KitLab" type="Node3D"]
script = ExtResource("lab")
env_levels = [SubResource("env_off"), SubResource("env_subtle")]

[node name="Geometry" type="Node3D" parent="."]
script = ExtResource("map")
local_map_file = "res://maps/kit_lab_01.map"
map_settings = ExtResource("settings")

[node name="Navigation" type="NavigationRegion3D" parent="."]

[node name="Environment" type="WorldEnvironment" parent="."]
environment = SubResource("env_subtle")

[node name="Sun" type="DirectionalLight3D" parent="."]
transform = {tf((0, 30, -23), sun)}
light_color = Color(1, 0.74, 0.52, 1)
light_energy = 1.7
shadow_enabled = true
directional_shadow_max_distance = 120.0
light_volumetric_fog_energy = 0.7

[node name="MarsDust" type="FogVolume" parent="."]
transform = {tf(((dust_x0 + dust_x1) / 2, 18.0, -25.0))}
size = Vector3({dust_x1 - dust_x0:.2f}, 44.0, 120.0)
shape = 3
material = SubResource("mars_dust")

[node name="Doors" type="Node3D" parent="."]

[node name="Lighting" type="Node3D" parent="."]

'''
player = f'''[node name="GymPlayer" parent="." instance=ExtResource("player")]
transform = {tf(G(0.0, 0.05, -1.0))}
gym_title = "KIT LAB K-01"
'''
if lights == 0:
    raise SystemExit('no lights written')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(header + '\n'.join(subs) + '\n' + body + '\n'.join(door_nodes) + '\n' + '\n'.join(nodes) + '\n' + player,
               encoding='utf-8')
(PROJ / 'kit/kit_lab_data.json').write_text(json.dumps({'views': K.VIEWS}, indent=1), encoding='utf-8')
print(f'KIT_LAB_SCENE: {lights} lights, {bay_index} corridor bays, {len(door_nodes)} doors')
