"""Build Red Breach's props in Blender from the catalogue (tools/props.py).

Run by Blender, never by plain Python (tools/rebuild-props.ps1 does this):
    blender --background --factory-startup --python tools/build-props-blender.py [-- name name ...]

For each prop it writes art/props/<name>.blend, the editable source (outside the Godot project, so Godot never tries
to import it), and exports RedBreach/props/<category>/<name>.glb. Every object's origin is the prop's origin; the
'Wires' object is a unit length going up, which the light prop scales. Faces are flat shaded, with the catalogue's
texture coordinates, and each material is named after its look and role ('steel/frame'), which the Godot import maps
to the level's own material. In Blender the materials show the real textures, so a hand edit looks right.

A prop listed in props.HAND is hand-edited: its .blend is exported as it is and never regenerated.
"""
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import props as PR  # noqa: E402

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
NAMES = ARGS or list(PR.PROPS)


def to_blender(p):
    """Godot (x right, y up, z front) to Blender (x right, y back, z up); the glTF export maps it back."""
    x, y, z = p
    return (x, -z, y)


def material(name):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    if mat.node_tree is None:               # Blender 5 materials have their node tree already; older ones need asking
        mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    image, _, tint = PR.material_image(name)
    if image is not None:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(image), check_existing=True)
        tex.interpolation = 'Closest'
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        rgb, rough, metal, emit = PR.PROP_MATERIALS[name.split('/')[1]]
        bsdf.inputs['Base Color'].default_value = (*rgb, 1.0)
        bsdf.inputs['Roughness'].default_value = rough
        bsdf.inputs['Metallic'].default_value = metal
        if emit is not None:
            bsdf.inputs['Emission Color'].default_value = (*emit, 1.0)
            bsdf.inputs['Emission Strength'].default_value = 1.0
    return mat


def build(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0      # no .blend1 backups beside the sources
    geo = PR.geometry(name)
    objects = []
    for node, faces in geo.items():
        verts, polys, uvs, mats = [], [], [], []
        names = sorted({m for _, m, _ in faces})
        for pts, mat, uv in faces:
            base = len(verts)
            verts += [to_blender(p) for p in pts]
            polys.append(list(range(base, base + len(pts))))
            uvs.append(uv)
            mats.append(names.index(mat))
        mesh = bpy.data.meshes.new(node)
        mesh.from_pydata(verts, [], polys)
        mesh.update()
        layer = mesh.uv_layers.new(name='UVMap')
        for poly, uv, mi in zip(mesh.polygons, uvs, mats):
            poly.material_index = mi
            poly.use_smooth = False
            for li, (u, v) in zip(poly.loop_indices, uv):
                layer.data[li].uv = (u, v)
        for m in names:
            mesh.materials.append(material(m))
        obj = bpy.data.objects.new(node, mesh)
        bpy.context.scene.collection.objects.link(obj)
        objects.append(obj)
    blend = PR.blend_path(name)
    blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), relative_remap=True)
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except RuntimeError:
        pass
    return objects


def export(name):
    glb = PR.glb_path(name)
    glb.parent.mkdir(parents=True, exist_ok=True)
    kw = dict(filepath=str(glb), export_format='GLB', export_yup=True, export_apply=False, export_materials='EXPORT',
              export_cameras=False, export_lights=False, export_extras=False)
    try:
        bpy.ops.export_scene.gltf(export_image_format='NONE', **kw)
    except TypeError:
        bpy.ops.export_scene.gltf(**kw)


for name in NAMES:
    if name in PR.HAND:
        bpy.ops.wm.open_mainfile(filepath=str(PR.blend_path(name)))
        print(f'PROP {name}: hand-edited, exported from its .blend')
    else:
        build(name)
        print(f'PROP {name}: built')
    export(name)
print(f'PROPS_BLENDER: {len(NAMES)} props exported')
