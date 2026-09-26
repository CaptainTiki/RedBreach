"""Write everything the style lab needs apart from the map:

- textures/style_common/mars_ground.png and mars_rock.png: small 64 px
  crunchy textures, generated here with the standard library only
- a material per look and role: textures/looks/<look>/<role>.tres, with a
  same-named .png preview beside it for TrenchBroom
- .import files for the pack textures that keep them LOSSLESS, so crunchy
  pixels are not smeared by VRAM compression
- mapping/style_lab_map_settings.tres
- the scene: style/style_lab.tscn, with one Geometry node per palette (the
  zoned mix keeps collision; single-look palettes are visual only), every
  lighting tier in every bay, the room lights, the sun and three presentation
  environments

    python tools/write-style-lab-scene.py
    powershell -File tools/rebuild-style-lab.ps1 -Validate -Capture

Lights and fixtures sit outside Geometry, so a rebuild never touches them.
"""
from pathlib import Path
import math
import random
import shutil
import struct
import sys
import json
import zlib
sys.path.insert(0, str(Path(__file__).resolve().parent))
import style_lab as S

ROOT = Path(__file__).resolve().parents[1]
PROJ = ROOT / 'RedBreach'
TEX = PROJ / 'textures'


# --- tiny PNG writer --------------------------------------------------------
def write_png(path, w, h, pixels):
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    raw = b''.join(b'\x00' + bytes(v for px in pixels[y * w:(y + 1) * w] for v in px) for y in range(h))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def value_noise(size, cells, rng):
    g = [[rng.random() for _ in range(cells)] for _ in range(cells)]
    out = []
    for y in range(size):
        for x in range(size):
            fx, fy = x / size * cells, y / size * cells
            x0, y0 = int(fx), int(fy)
            tx, ty = fx - x0, fy - y0
            tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
            a = g[y0 % cells][x0 % cells]; b = g[y0 % cells][(x0 + 1) % cells]
            c = g[(y0 + 1) % cells][x0 % cells]; d = g[(y0 + 1) % cells][(x0 + 1) % cells]
            out.append((a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty)
    return out


def ramp(t, stops):
    t = max(0.0, min(1.0, t))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            k = (t - t0) / (t1 - t0)
            return tuple(int(round((c0[i] + (c1[i] - c0[i]) * k))) for i in range(3))
    return stops[-1][1]


def mars_textures():
    rng = random.Random(1976)
    n = 64
    # Regolith: fine dust with scattered pebbles, tileable, quantised a little
    # so it reads as pixel art rather than photo noise.
    a, b, c = value_noise(n, 4, rng), value_noise(n, 8, rng), value_noise(n, 16, rng)
    stops = [(0.0, (74, 34, 20)), (0.35, (122, 58, 32)), (0.65, (158, 82, 46)), (1.0, (196, 118, 72))]
    px = []
    for i in range(n * n):
        v = 0.5 * a[i] + 0.3 * b[i] + 0.2 * c[i]
        v = round(v * 7) / 7
        if rng.random() < 0.035:
            v -= 0.25
        px.append(ramp(v, stops))
    for _ in range(14):
        cx, cy, r = rng.randrange(n), rng.randrange(n), rng.choice((1, 1, 2))
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    x, y = (cx + dx) % n, (cy + dy) % n
                    shade = 0.28 if dy < 0 else 0.12
                    px[y * n + x] = ramp(shade + 0.1 * rng.random(), stops)
    write_png(TEX / 'style_common/mars_ground.png', n, n, px)
    # Rock: layered strata with noise-broken edges and dark cracks.
    a, b = value_noise(n, 4, rng), value_noise(n, 16, rng)
    stops = [(0.0, (58, 26, 18)), (0.4, (104, 48, 30)), (0.7, (142, 72, 44)), (1.0, (176, 104, 70))]
    px = []
    for y in range(n):
        for x in range(n):
            i = y * n + x
            band = 0.5 + 0.5 * math.sin((y + a[i] * 9) / n * math.tau * 4)
            v = 0.55 * band + 0.3 * b[i] + 0.15 * a[i]
            v = round(v * 6) / 6
            px.append(ramp(v, stops))
    for _ in range(5):
        x, y = rng.randrange(n), rng.randrange(n)
        for _ in range(rng.randrange(8, 20)):
            px[(y % n) * n + (x % n)] = (40, 18, 12)
            x += rng.choice((-1, 0, 1)); y += 1
    write_png(TEX / 'style_common/mars_rock.png', n, n, px)


# --- import settings ----------------------------------------------------------
IMPORT = '''[remap]

importer="texture"
type="CompressedTexture2D"

[deps]

source_file="res://{path}"

[params]

compress/mode=0
mipmaps/generate=true
detect_3d/compress_to=0
'''


def lossless_imports():
    written = 0
    for folder in ('packs', 'style_common', 'looks'):
        for png in (TEX / folder).rglob('*.png'):
            imp = png.with_suffix('.png.import')
            if imp.exists():
                continue
            imp.write_text(IMPORT.format(path=png.relative_to(PROJ).as_posix()), encoding='utf-8')
            written += 1
    return written


# --- materials ------------------------------------------------------------------
def material(set_name, role, image, tint=None):
    lines = ['[gd_resource type="StandardMaterial3D" load_steps=2 format=3]', '',
             f'[ext_resource type="Texture2D" path="res://textures/{image}.png" id="1"]', '',
             '[resource]', f'resource_name = "{set_name} {role}"',
             'albedo_texture = ExtResource("1")']
    if tint:
        lines.append(f'albedo_color = Color({tint[0]}, {tint[1]}, {tint[2]}, 1)')
    if role in ('ground', 'rock'):
        lines += ['roughness = 1.0', 'metallic_specular = 0.15']
    else:
        lines += ['roughness = 0.8', 'metallic_specular = 0.35']
    if role in S.EMISSIVE:
        r, g, b, e = S.EMISSIVE[role]
        lines += ['emission_enabled = true', f'emission = Color({r}, {g}, {b}, 1)',
                  f'emission_energy_multiplier = {e}', 'emission_texture = ExtResource("1")']
    lines += ['texture_filter = 4', '']
    path = TEX / set_name / f'{role}.tres'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines), encoding='utf-8')


def map_settings(set_name):
    (PROJ / 'mapping' / f'style_lab_{set_name}_settings.tres').write_text(f'''[gd_resource type="Resource" script_class="FuncGodotMapSettings" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/func_godot/src/map/func_godot_map_settings.gd" id="1"]

[resource]
script = ExtResource("1")
inverse_scale_factor = 32.0
base_texture_dir = "res://textures"
base_material_dir = "res://textures/{set_name}"
save_generated_materials = false
''', encoding='utf-8')


# --- scene ------------------------------------------------------------------------
def basis_looking(d):
    """Columns of a basis whose -Z points along d (for DirectionalLight3D)."""
    dx, dy, dz = d
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    f = (-dx / L, -dy / L, -dz / L)             # +Z axis = -direction
    up = (0, 1, 0)
    x = (up[1] * f[2] - up[2] * f[1], up[2] * f[0] - up[0] * f[2], up[0] * f[1] - up[1] * f[0])
    xl = math.sqrt(sum(v * v for v in x)); x = tuple(v / xl for v in x)
    y = (f[1] * x[2] - f[2] * x[1], f[2] * x[0] - f[0] * x[2], f[0] * x[1] - f[1] * x[0])
    return x, y, f


def tf(pos, basis=None):
    if basis is None:
        return f'Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f})'
    x, y, z = basis
    return ('Transform3D(' + ', '.join(f'{v:.6f}' for v in (x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2]))
            + f', {pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f})')


CORRIDOR_LIGHT = (0.86, 0.93, 1.0)
# (energy, range) per tier. Floor lights are many, low and short.
TIER_LIGHT = {'ceiling': (1.25, 9.0), 'edge': (0.75, 8.0), 'low': (0.6, 6.0), 'floor': (1.0, 6.0),
              'flicker': (0.8, 8.0), 'dead': (0.0, 0.0), 'emergency': (0.6, 7.0)}
EMERGENCY_LIGHT = (1.0, 0.16, 0.1)
# Revision 03: the yellow dust belongs OUTSIDE. Inside, the volumetric fog is
# neutral and dark, and only a box-shaped FogVolume over the exterior is warm.
# It starts just outside the window glass so the room air stays clean.
_DX0, _DX1 = S.ROOM_HALF + S.ROOM_SHELL + 0.1, 140.0
DUST_CENTRE = ((_DX0 + _DX1) / 2, 18.0, -55.0)
DUST_SIZE = (_DX1 - _DX0, 44.0, 190.0)
PRESENTATION = ('off', 'subtle', 'strong')


def write_scene():
    nodes = []
    subs = []
    meshes = {}

    def fixture_mesh(size):
        key = 'box_' + '_'.join(f'{v:g}'.replace('.', 'p') for v in size)
        if key not in meshes:
            meshes[key] = True
            subs.append(f'[sub_resource type="BoxMesh" id="{key}"]\nsize = Vector3({size[0]}, {size[1]}, {size[2]})\n')
        return key

    nodes.append('[node name="Bays" type="Node3D" parent="Lighting"]\n')
    default_plan = S.PLANS['mixed']
    lights = 0
    for i, (profile, z) in enumerate(S.BAYS):
        bay = f'Lighting/Bays/Bay{i}'
        nodes.append(f'[node name="Bay{i}" type="Node3D" parent="Lighting/Bays"]\n')
        for tier in S.TIERS:
            visible = 'true' if tier in default_plan[i] else 'false'
            extra = ''
            if tier == 'flicker':
                extra = ('script = ExtResource("flicker")\nlit_material = SubResource("fitting")\n'
                         f'dead_material = SubResource("fitting_dead")\nseed = {17 + i}\n')
            nodes.append(f'[node name="{tier}" type="Node3D" parent="{bay}"]\nvisible = {visible}\n{extra}')
            energy, rng = TIER_LIGHT[tier]
            for name, lp, fp, size, lit in S.tier_parts(tier, profile, z):
                if lp is not None and energy > 0:
                    lights += 1
                    shadow = 'false' if tier == 'floor' else 'true'
                    nodes.append(f'[node name="{name}" type="OmniLight3D" parent="{bay}/{tier}"]\n'
                                 f'transform = {tf(lp)}\nlight_color = Color({CORRIDOR_LIGHT[0]}, {CORRIDOR_LIGHT[1]}, {CORRIDOR_LIGHT[2]}, 1)\n'
                                 f'light_energy = {energy}\nshadow_enabled = {shadow}\nomni_range = {rng}\nomni_attenuation = 1.2\n')
                if fp is not None:
                    mat = ('fitting_red' if tier == 'emergency' else 'fitting') if lit else 'fitting_dead'
                    nodes.append(f'[node name="{name}_fitting" type="MeshInstance3D" parent="{bay}/{tier}"]\n'
                                 f'transform = {tf(fp)}\nmesh = SubResource("{fixture_mesh(size)}")\n'
                                 f'surface_material_override/0 = SubResource("{mat}")\ncast_shadow = 0\n')
            if tier == 'flicker':
                sx = -(S.ceil_half(profile) - 0.3)
                nodes.append(f'[node name="Sparks" type="GPUParticles3D" parent="{bay}/{tier}"]\n'
                             f'transform = {tf((sx, S.CEIL_Y - 0.1, z + 0.6))}\nemitting = false\namount = 28\n'
                             'lifetime = 0.9\none_shot = true\nexplosiveness = 0.85\nlocal_coords = false\n'
                             'process_material = SubResource("spark_process")\ndraw_pass_1 = SubResource("spark_mesh")\n')
    # Room lights: four high fittings on the haunches, coolant glow around the
    # tank, and a faint wash from each desk screen.
    room = []
    for i, (x, z) in enumerate(((-5.5, S.ROOM_Z0 - 2.5), (5.5, S.ROOM_Z0 - 2.5), (-5.5, S.ROOM_Z1 + 2.5), (5.5, S.ROOM_Z1 + 2.5))):
        room.append((f'High{i}', (x * 0.9, 5.0, z), (0.86, 0.93, 1.0), 1.6, 13.0, True, (x, 5.55, z), (0.8, 0.08, 0.8)))
    for i, (dx, dz) in enumerate(((0, 2.2), (0, -2.2), (2.2, 0), (-2.2, 0))):
        room.append((f'Coolant{i}', (dx, 0.95, S.ROOM_CZ + dz), (0.35, 1.0, 0.8), 0.9, 6.0, False, None, None))
    for i, x in enumerate((-4.4, 4.4)):
        room.append((f'Screen{i}', (x, 1.4, S.ROOM_CZ), (0.55, 1.0, 0.75), 0.45, 3.0, False, None, None))
    for name, lp, col, e, rng, shadow, fp, size in room:
        lights += 1
        nodes.append(f'[node name="{name}" type="OmniLight3D" parent="Lighting/Room"]\n'
                     f'transform = {tf(lp)}\nlight_color = Color({col[0]}, {col[1]}, {col[2]}, 1)\n'
                     f'light_energy = {e}\nshadow_enabled = {"true" if shadow else "false"}\nomni_range = {rng}\n')
        if fp:
            nodes.append(f'[node name="{name}_fitting" type="MeshInstance3D" parent="Lighting/Room"]\n'
                         f'transform = {tf(fp)}\nmesh = SubResource("{fixture_mesh(size)}")\n'
                         'surface_material_override/0 = SubResource("fitting")\ncast_shadow = 0\n')

    sun = basis_looking((-1.0, -0.42, -0.18))
    header = ['[gd_scene format=3]', '',
              '[ext_resource type="Script" path="res://addons/func_godot/src/map/func_godot_map.gd" id="map"]',
              '[ext_resource type="Resource" path="res://mapping/style_lab_map_settings.tres" id="settings"]',
              '[ext_resource type="PackedScene" path="res://player/gym_player.tscn" id="player"]',
              '[ext_resource type="Script" path="res://style/style_lab.gd" id="lab"]',
              '[ext_resource type="Script" path="res://style/flicker_light.gd" id="flicker"]', '']
    env_common = '''background_mode = 2
sky = SubResource("sky")
ambient_light_source = 2
ambient_light_color = Color(0.55, 0.62, 0.76, 1)
ambient_light_energy = 0.12
reflected_light_source = 1
'''
    env = f'''[sub_resource type="ProceduralSkyMaterial" id="mars_sky"]
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
{env_common}tonemap_mode = 2

[sub_resource type="Environment" id="env_subtle"]
{env_common}tonemap_mode = 3
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

[sub_resource type="Environment" id="env_strong"]
{env_common}tonemap_mode = 3
tonemap_exposure = 1.05
ssao_enabled = true
ssao_radius = 0.9
ssao_intensity = 2.8
ssao_light_affect = 0.2
glow_enabled = true
glow_intensity = 0.95
glow_strength = 1.1
glow_bloom = 0.05
glow_blend_mode = 1
glow_hdr_threshold = 1.0
fog_enabled = true
fog_mode = 1
fog_light_color = Color(0.58, 0.4, 0.29, 1)
fog_density = 1.0
fog_sky_affect = 0.0
fog_depth_begin = 50.0
fog_depth_end = 300.0
volumetric_fog_enabled = true
volumetric_fog_density = 0.03
volumetric_fog_albedo = Color(0.4, 0.43, 0.48, 1)
volumetric_fog_length = 64.0
volumetric_fog_ambient_inject = 0.04
volumetric_fog_anisotropy = 0.5
adjustment_enabled = true
adjustment_contrast = 1.15
adjustment_saturation = 1.2

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
    geometry = ''
    for i, palette in enumerate(S.PALETTES):
        geometry += (f'[node name="Geometry_{palette}" type="Node3D" parent="."]\n'
                     + ('' if i == 0 else 'visible = false\n')
                     + 'script = ExtResource("map")\nlocal_map_file = "res://maps/style_lab_01.map"\n'
                     'map_settings = ExtResource("settings")\n\n')
    body = [f'''[node name="StyleLab" type="Node3D"]
script = ExtResource("lab")
env_levels = [SubResource("env_off"), SubResource("env_subtle"), SubResource("env_strong")]

{geometry}[node name="Environment" type="WorldEnvironment" parent="."]
environment = SubResource("env_subtle")

[node name="Sun" type="DirectionalLight3D" parent="."]
transform = {tf((0, 30, -47), sun)}
light_color = Color(1, 0.74, 0.52, 1)
light_energy = 1.7
shadow_enabled = true
directional_shadow_max_distance = 90.0
light_volumetric_fog_energy = 0.7

[node name="MarsDust" type="FogVolume" parent="."]
transform = {tf(DUST_CENTRE)}
size = Vector3({DUST_SIZE[0]}, {DUST_SIZE[1]}, {DUST_SIZE[2]})
shape = 3
material = SubResource("mars_dust")

[node name="Lighting" type="Node3D" parent="."]

[node name="Room" type="Node3D" parent="Lighting"]
''']
    body += nodes
    body.append(f'''[node name="GymPlayer" parent="." instance=ExtResource("player")]
transform = {tf(S.SPAWN)}
gym_title = "STYLE LAB S-01 rev 02"
''')
    text = '\n'.join(header) + env + '\n' + '\n'.join(subs) + '\n' + '\n'.join(body)
    out = PROJ / 'style/style_lab.tscn'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')
    return lights


if __name__ == '__main__':
    S.check()
    mars_textures()
    # Revision 01's per-set folders are superseded by looks.
    for old in (TEX / 'style_a', TEX / 'style_b', TEX / 'role'):
        if old.exists():
            shutil.rmtree(old)
    for old in (PROJ / 'mapping').glob('style_lab_style_*_settings.tres'):
        old.unlink()
    # Refuse a texture that cannot meet its role's tiling (docs/texture-catalog.json,
    # written by tools/audit-textures.py).
    catalog = json.loads((ROOT / 'docs/texture-catalog.json').read_text())
    problems = []
    for look_name, roles in S.LOOKS.items():
        for role, entry in roles.items():
            image, tint = S.look_texture(entry)
            if not (TEX / f'{image}.png').exists():
                raise SystemExit(f'{look_name}/{role}: no texture {image}.png')
            need, c = S.ROLE_TILING[role], catalog.get(image)
            if c is None:
                problems.append(f'{look_name}/{role}: {image} is not in the texture catalog')
            elif (need == 'HV' and not (c['tiles_h'] and c['tiles_v'])) or (need == 'H' and not c['tiles_h']):
                problems.append(f'{look_name}/{role} needs {need} but {image} is {c["class_h"]}{c["class_v"]}')
    if problems:
        raise SystemExit('TEXTURE TILING:\n  ' + '\n  '.join(problems))
    for look_name, roles in S.LOOKS.items():
        for role, entry in roles.items():
            image, tint = S.look_texture(entry)
            material(f'looks/{look_name}', role, image, tint)
            # TrenchBroom preview beside the material (func_godot prefers the .tres).
            shutil.copyfile(TEX / f'{image}.png', TEX / 'looks' / look_name / f'{role}.png')
    (PROJ / 'mapping' / 'style_lab_map_settings.tres').write_text('''[gd_resource type="Resource" script_class="FuncGodotMapSettings" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/func_godot/src/map/func_godot_map_settings.gd" id="1"]

[resource]
script = ExtResource("1")
inverse_scale_factor = 32.0
base_texture_dir = "res://textures"
base_material_dir = "res://textures"
save_generated_materials = false
''', encoding='utf-8')
    # Views, palettes, plans and probes for the build, capture and validation
    # scripts, so they read the same numbers as the map instead of a copy.
    (PROJ / 'style/style_lab_data.json').write_text(json.dumps({
        'views': S.VIEWS, 'spawn': S.SPAWN,
        'palettes': [[k, v] for k, v in S.PALETTES.items()], 'palette_titles': S.PALETTE_TITLES,
        'tiers': list(S.TIERS), 'plans': [[k, v] for k, v in S.PLANS.items()], 'plan_titles': S.PLAN_TITLES,
        'presentation': list(PRESENTATION), 'bays': [[p, z] for p, z in S.BAYS],
        'sections': [[p, z0] for p, z0 in S.SECTIONS], 'section_len': S.SECTION_LEN,
        'rib_stations': list(S.RIB_STATIONS), 'rib_d': S.RIB_D, 'ceil_y': S.CEIL_Y,
        'room': {'z0': S.ROOM_Z0, 'z1': S.ROOM_Z1, 'cz': S.ROOM_CZ, 'half': S.ROOM_HALF, 'ceil': S.ROOM_CEIL},
        'window': S.WINDOW,
        'room_loop': [[0.0, S.ROOM_Z0 - 2.5], [6.7, S.ROOM_Z0 - 2.5], [6.7, S.ROOM_Z1 + 2.5],
                      [-6.7, S.ROOM_Z1 + 2.5], [-6.7, S.ROOM_Z0 - 2.5], [0.0, S.ROOM_Z0 - 2.5]],
    }, indent=1), encoding='utf-8')
    imports = lossless_imports()
    lights = write_scene()
    if lights == 0:
        raise SystemExit('no lights written')
    print(f'STYLE_LAB_SCENE: {len(S.LOOKS)} looks x {len(S.ROLES)} roles; {len(S.PALETTES)} palettes; '
          f'{len(S.PLANS)} light plans; {lights} lights; {imports} new lossless imports')
