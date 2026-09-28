"""Write the Godot side of Red Breach's props from the catalogue (tools/props.py).

    python tools/write-props.py          (tools/rebuild-props.ps1 runs it after Blender)

  RedBreach/props/materials/<name>.tres       the props' own materials (lens, lens_dead, wire, rubber, fabric, ...)
  RedBreach/props/<category>/<name>.glb.import   import settings: each Blender material is mapped to the level's own
                                               look material (textures/looks/<look>/<role>.tres) or a prop material
  RedBreach/props/<category>/<name>.tscn      the prop: the imported model, with its light(s) (a PropLight) or its
                                               collision (a StaticBody3D)
  RedBreach/props/props_gallery.tscn          the showroom (F12): every prop, lit, with the player
  RedBreach/props/props_data.json             bounds, placements and views for the checks and the capture
Nothing here is edited by hand: change the catalogue and rebuild.
"""
from pathlib import Path
import json
import math
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import props as PR

PROJ = PR.PROJ
PROPS_DIR = PROJ / 'props'


def res(path):
    return 'res://' + Path(path).relative_to(PROJ).as_posix()


def node_name(name):
    return ''.join(w.capitalize() for w in name.split('_'))


def f(v):
    return f'{v:.6g}'


def transform(pos, rot=(0, 0, 0)):
    """A .tscn Transform3D. Its basis is written ROW by row (x_axis.x, y_axis.x, z_axis.x, ...), not axis by axis."""
    xa, ya, za = PR._rot((1, 0, 0), rot), PR._rot((0, 1, 0), rot), PR._rot((0, 0, 1), rot)
    nums = [v for i in range(3) for v in (xa[i], ya[i], za[i])] + list(pos)
    return 'Transform3D(' + ', '.join(f(round(v, 6) + 0.0) for v in nums) + ')'


def color(rgb):
    return 'Color(' + ', '.join(f(c) for c in rgb) + ', 1)'


# --- materials ------------------------------------------------------------------------------------------------------
def write_materials():
    out = PROPS_DIR / 'materials'
    out.mkdir(parents=True, exist_ok=True)
    for name, (rgb, rough, metal, emit) in PR.PROP_MATERIALS.items():
        lines = ['[gd_resource type="StandardMaterial3D" format=3]', '', '[resource]', f'resource_name = "prop/{name}"',
                 f'albedo_color = {color(rgb)}', f'roughness = {f(rough)}', f'metallic = {f(metal)}']
        if emit is not None:
            lines += ['emission_enabled = true', f'emission = {color(emit)}',
                      f'emission_energy_multiplier = {f(2.0 if name == "lens" else 1.2)}']
        (out / f'{name}.tres').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def material_res(mat):
    look_name, role = mat.split('/')
    if look_name == 'prop':
        return f'res://props/materials/{role}.tres'
    return f'res://textures/looks/{look_name}/{role}.tres'


# --- import settings --------------------------------------------------------------------------------------------------
def write_import(name):
    """Map every material of the model to its external material, and keep the model whole (no LODs: the crunchy
    shapes are the look). Keeps whatever else Godot wrote there."""
    glb = PR.glb_path(name)
    imp = glb.with_name(glb.name + '.import')
    sub = ',\n'.join(f'"{m}": {{\n"use_external/enabled": true,\n"use_external/path": "{material_res(m)}",\n'
                     f'"use_external/fallback_path": "{material_res(m)}"\n}}' for m in PR.materials(name))
    subresources = '_subresources={\n"materials": {\n' + sub + '\n}\n}'
    if imp.exists():
        text = imp.read_text(encoding='utf-8')
        if '_subresources={}' in text:
            text = text.replace('_subresources={}', subresources)
        else:
            text = re.sub(r'_subresources=\{.*?\n\}(?=\n[a-z])', lambda _: subresources, text, flags=re.S)
        if '_subresources=' not in text:
            text = text.rstrip('\n') + '\n' + subresources + '\n'
        text = text.replace('meshes/generate_lods=true', 'meshes/generate_lods=false')
    else:
        text = ('[remap]\n\nimporter="scene"\nimporter_version=1\ntype="PackedScene"\n\n[deps]\n\n'
                f'source_file="{res(glb)}"\n\n[params]\n\nmeshes/generate_lods=false\n{subresources}\n')
    imp.write_text(text, encoding='utf-8')


# --- prop scenes ------------------------------------------------------------------------------------------------------
def write_scene(name):
    p = PR.PROPS[name]
    glb = PR.glb_path(name)
    out = glb.with_suffix('.tscn')
    lines = ['[gd_scene format=3]', '']
    lines.append(f'[ext_resource type="PackedScene" path="{res(glb)}" id="model"]')
    light = p.get('light')
    if light:
        lines.append('[ext_resource type="Script" path="res://props/prop_light.gd" id="script"]')
    lines.append('')
    shapes = p.get('collision', [])
    for k, (kind, *spec) in enumerate(shapes):
        if kind == 'box':
            size, _ = spec
            lines += [f'[sub_resource type="BoxShape3D" id="shape{k}"]', f'size = Vector3({", ".join(f(v) for v in size)})', '']
        else:
            r, h, _ = spec
            lines += [f'[sub_resource type="CylinderShape3D" id="shape{k}"]', f'radius = {f(r)}', f'height = {f(h)}', '']
    root = node_name(name)
    if light:
        lines += [f'[node name="{root}" type="Node3D"]', 'script = ExtResource("script")',
                  f'color = {color(light["color"])}', f'energy = {f(light["energy"])}',
                  f'light_range = {f(light["range"])}', f'shadows = {"true" if light["shadow"] else "false"}',
                  f'wire = {f(p.get("wire", 0.0))}']
        if 'spin' in p:
            lines.append(f'spin_speed = {f(p["spin"]["speed"])}')
        if 'glow' in p:
            lines.append(f'glow_ratio = {f(p["glow"]["ratio"])}')
    else:
        lines += [f'[node name="{root}" type="StaticBody3D"]']
    lines += ['', '[node name="Model" parent="." instance=ExtResource("model")]', '']
    if light:
        parent = '.'
        if 'spin' in p:
            lines += ['[node name="Spin" type="Node3D" parent="."]', f'transform = {transform(p["spin"]["pos"])}', '']
            parent = 'Spin'
            lpos = [light['pos'][i] - p['spin']['pos'][i] for i in range(3)]
        else:
            lpos = light['pos']
        kind = 'SpotLight3D' if light['type'] == 'spot' else 'OmniLight3D'
        lines += [f'[node name="Light" type="{kind}" parent="{parent}"]', f'transform = {transform(lpos, light.get("rot", (0, 0, 0)))}',
                  f'light_color = {color(light["color"])}', f'light_energy = {f(light["energy"])}',
                  f'shadow_enabled = {"true" if light["shadow"] else "false"}']
        if kind == 'SpotLight3D':
            lines += [f'spot_range = {f(light["range"])}', f'spot_angle = {f(light["angle"])}', 'spot_attenuation = 1.2']
        else:
            lines += [f'omni_range = {f(light["range"])}']
        lines.append('')
        if 'glow' in p:
            g = p['glow']
            lines += ['[node name="Glow" type="OmniLight3D" parent="."]', f'transform = {transform(g["pos"])}',
                      f'light_color = {color(light["color"])}', f'light_energy = {f(light["energy"] * g["ratio"])}',
                      f'omni_range = {f(g["range"])}', '']
    for k, (kind, *spec) in enumerate(shapes):
        pos = spec[-1]
        lines += [f'[node name="Collision{k}" type="CollisionShape3D" parent="."]', f'transform = {transform(pos)}',
                  f'shape = SubResource("shape{k}")', '']
    out.write_text('\n'.join(lines), encoding='utf-8')
    return out


# --- the gallery ------------------------------------------------------------------------------------------------------
def write_gallery():
    used = ['gallery_room'] + sorted({pl[0] for pl in PR.GALLERY_PLACEMENTS})
    ids = {n: f'p{k}' for k, n in enumerate(used)}
    lines = ['[gd_scene format=3]', '', '[ext_resource type="PackedScene" path="res://player/gym_player.tscn" id="player"]']
    for n in used:
        lines.append(f'[ext_resource type="PackedScene" path="{res(PR.glb_path(n).with_suffix(".tscn"))}" id="{ids[n]}"]')
    lines += ['', '[sub_resource type="Environment" id="env"]', 'background_mode = 1',
              'background_color = Color(0.02, 0.02, 0.025, 1)', 'ambient_light_source = 2',
              'ambient_light_color = Color(0.55, 0.62, 0.76, 1)', 'ambient_light_energy = 0.12', 'reflected_light_source = 1',
              'tonemap_mode = 3', 'ssao_enabled = true', 'ssao_radius = 0.8', 'ssao_intensity = 2.2', 'ssao_light_affect = 0.15',
              'glow_enabled = true', 'glow_intensity = 0.7', 'glow_strength = 1.0', 'glow_bloom = 0.02', 'glow_blend_mode = 1',
              'glow_hdr_threshold = 1.1', 'volumetric_fog_enabled = true', 'volumetric_fog_density = 0.012',
              'volumetric_fog_albedo = Color(0.45, 0.48, 0.52, 1)', 'volumetric_fog_length = 64.0',
              'volumetric_fog_ambient_inject = 0.02', 'adjustment_enabled = true', 'adjustment_contrast = 1.08',
              'adjustment_saturation = 1.12', '',
              '[node name="PropsGallery" type="Node3D"]', '',
              '[node name="Environment" type="WorldEnvironment" parent="."]', 'environment = SubResource("env")', '',
              f'[node name="Room" parent="." instance=ExtResource("{ids["gallery_room"]}")]', '',
              '[node name="Props" type="Node3D" parent="."]', '']
    counts = {}
    for prop, pos, rot, overrides in PR.GALLERY_PLACEMENTS:
        counts[prop] = counts.get(prop, 0) + 1
        lines += [f'[node name="{node_name(prop)}{counts[prop]}" parent="Props" instance=ExtResource("{ids[prop]}")]',
                  f'transform = {transform(pos, rot)}']
        for k, v in overrides.items():
            lines.append(f'{k} = {"true" if v is True else "false" if v is False else f(v)}')
        lines.append('')
    sx, sy, sz = PR.GALLERY['spawn']
    lines += ['[node name="GymPlayer" parent="." instance=ExtResource("player")]',
              f'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {f(sx)}, {f(sy)}, {f(sz)})', 'gym_title = "PROPS GALLERY"', '']
    (PROPS_DIR / 'props_gallery.tscn').write_text('\n'.join(lines), encoding='utf-8')


def write_data():
    data = {'props': {}, 'placements': [[p, list(pos), list(rot), ov] for p, pos, rot, ov in PR.GALLERY_PLACEMENTS],
            'views': [[n, list(e), list(a)] for n, e, a in PR.GALLERY_VIEWS]}
    for name, p in PR.PROPS.items():
        lo, hi = PR.bounds(name, 'Body')
        data['props'][name] = {'scene': res(PR.glb_path(name).with_suffix('.tscn')), 'category': p['category'],
                               'title': p['title'], 'body_lo': lo, 'body_hi': hi, 'light': 'light' in p,
                               'wires': 'Wires' in PR.geometry(name), 'collision': len(p.get('collision', [])),
                               'materials': [material_res(m) for m in PR.materials(name)]}
    (PROPS_DIR / 'props_data.json').write_text(json.dumps(data, indent=1), encoding='utf-8')


if __name__ == '__main__':
    problems = PR.check()
    if problems:
        raise SystemExit('PROPS_CHECK:\n  ' + '\n  '.join(problems))
    missing = [n for n in PR.PROPS if not PR.glb_path(n).exists()]
    if missing:
        raise SystemExit('no model yet for ' + ', '.join(missing) + ': run the Blender build first')
    write_materials()
    for name in PR.PROPS:
        write_import(name)
        write_scene(name)
    write_gallery()
    write_data()
    print(f'PROPS_WRITE: {len(PR.PROPS)} props, {len(PR.PROP_MATERIALS)} prop materials, the gallery '
          f'({len(PR.GALLERY_PLACEMENTS)} placements)')
