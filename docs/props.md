# Props

**Status:** first draft, 2026-09-27. There are 19 catalogue entries: 7 light props, 11 furniture props and the gallery
room. Nothing is placed in a level yet.

## The user's rules

**Props are placed in Godot, not TrenchBroom, after a level's architecture is solid.** Placement is hard to judge in
TrenchBroom, because a point entity shows no facing or footprint. TrenchBroom keeps:
- the architecture
- the big machines that shape a room (containers, reactors, conveyors, pump housings)
- the progression kit

**A light is a prop:** a Godot scene with an imported fitting and its light as a child, edited in the inspector.
- The types are fluorescent, halogen, wall sconce, desk lamp, floor light and emergency light.
- A hanging fitting's wires run up through the ceiling into the void above the room. It can also sit flush against
  the ceiling.

## How to use them

**See them:** press **F12** anywhere in the game to open the gallery (`res://props/props_gallery.tscn`). Every prop is
there, lit as it would be used, in the freight level's environment. The sheet `docs/props-gallery.png` has 12 views.

**Place them in the freight level:** open `res://missions/freight_v2/freight_v2_props.tscn` and drag props in from
`res://props/lights/` and `res://props/furniture/`.
- The level instances that scene as `Props`.
- The scene writer creates it once, empty, and never writes it again, so placed props survive every rebuild.
- Placed lights count toward the light floor check like any others.
- When light props take over from the map's `rb_light` entities, those entities come out of the generator room by
  room. Until then the level keeps its current lighting.

**Tune a light:** select it and use the inspector. For anything else, right-click the prop and choose Editable
Children to reach the light node itself.

| Setting | What it does |
|---|---|
| `lit` | Off makes a dead fitting: the light is out and the lens is dark. A dead fitting never glows. |
| `color` | The light's colour; the lens glows in it. |
| `energy`, `light_range`, `shadows` | The light's own settings. |
| `wire` | Length of the hanging wires above the fitting. 0 is flush against the ceiling. |
| `flicker` | A failing fitting: mostly out, with stuttering bursts. Runs in the game only. |
| `spin_speed` | A beacon's turning beam, in radians per second. Runs in the game only. |
| `glow_ratio` | A beacon dome's dim glow, as a share of the energy. |

**Conventions:**
- **Front:** a prop's front is its +Z, the way it faces: the sitter's side of a desk, the face of a locker, a sconce
  facing out of its wall.
- **Origins:**
  - ceiling fittings: the top of the fitting (the ceiling)
  - wall props: the back at floor level, or the mounting point for a sconce or beacon bracket
  - floor props: the floor
  - desk-top props (terminal, desk lamp): the desk's surface
- **Collision:** furniture is a `StaticBody3D` on layer 1 with box or cylinder collision. Light props have none.

## The props

| Prop | Kind | Notes |
|---|---|---|
| `light_fluorescent` | ceiling | Twin-tube batten with a wire guard. Two wires. Omni light, cool. |
| `light_halogen` | ceiling | High-bay: driver box, reflector bell, lens, one wire. Downward spot (55 degrees), warm, shadows. |
| `light_sconce` | wall | Caged bulkhead. Omni light, warm. |
| `light_desk` | desk | Angled arm lamp. Small downward spot. |
| `light_floor` | floor | Uplight at the foot of a wall, washing it. Spot tipped toward the wall. |
| `light_emergency` | ceiling or on top of equipment | Caged red dome with a turning beam. Turn it over for a ceiling. |
| `light_emergency_wall` | wall | The same beacon upright on a wall bracket, so its beam sweeps the room. |
| `chair_office` | floor | Five-star swivel chair. |
| `desk_office` | floor | Desk with a drawer pedestal. |
| `terminal` | desk | Monitor on a stand, with a keyboard. |
| `locker_bank` | wall | Three lockers. |
| `filing_cabinet` | wall | Four drawers. |
| `shelf_rack` | wall | Four shelves, braced across the back. |
| `crate` | floor | Corrugated sides, framed edges. |
| `drum` | floor | 200 litres, with rings. |
| `pallet` | floor | Deck boards on three stringers. |
| `seat_joystick` | floor | The booth's operator seat, with a joystick and a button in its arm. Nothing is labelled; props tell the story. |
| `console_operator` | floor | Sloped desk with screens and buttons, and a raised display. |

## The pipeline

`tools/props.py` is the single source of truth. Each prop is a list of parts:
- boxes, frusta, and bars between two points
- each part names a look and a role (`steel/frame`) exactly as map faces do, so a prop uses the level's own materials
  at the level's density: 32 px per metre, and 64 for frames and ribs
- `prop/...` materials are the props' own: the lens, a dead lens, wire, rubber, fabric and lit buttons

Texture coordinates are a box projection in prop metres. A 'fit' role (a door, screen, vent or container side) is
fitted whole to each face.

`python tools/props.py` prints each prop's size and checks the catalogue.

```bash
powershell -File tools/rebuild-props.ps1 -Validate -Capture
```

The rebuild runs five steps:
1. **Blender** builds each model with `tools/build-props-blender.py`.
   - The source is `art/props/<name>.blend`, outside the Godot project so Godot never tries to import it. Its
     materials show the real textures.
   - The export is `RedBreach/props/<category>/<name>.glb`.
2. **Godot** imports the new models.
3. **`tools/write-props.py`** writes the Godot side:
   - each model's import settings, mapping every Blender material to the level's own material (or the props' own)
     with no LODs
   - the prop scenes (`.tscn`)
   - the prop materials
   - the gallery and `props_data.json`
4. **Godot** imports again, with the material mapping.
5. **`validate_props.gd`** runs 153 checks:
   - every surface uses its external material
   - each model's size and origin match the catalogue
   - furniture collision
   - lights: off means dark, on means glowing, energy reaches the light, and the wires follow their length
   - the gallery

   **`capture_props.gd`** writes the sheet.

**Machine setup:** set `REDBREACH_BLENDER` once per machine, like `REDBREACH_GODOT`:
`setx REDBREACH_BLENDER "C:\path\to\blender.exe"`. The desktop's Steam Blender (5.2) is the fallback.

**Hand edits:** to refine a prop by hand in Blender, add its name to `HAND` in `tools/props.py`. From then on the
build exports its `.blend` as it is and never regenerates it.

## Findings

- **A `.tscn` Transform3D writes its basis row by row** (x_axis.x, y_axis.x, z_axis.x, ...), not axis by axis. Writing
  the axes turned every rotation inside out: the halogens shone up and the lockers faced their walls.
  `write-props.py`'s `transform()` writes rows.
- **Godot's glTF import maps materials by name** through `_subresources` → `materials` → `use_external/path`.
  Godot rewrites the file in its own order, which is harmless. `write-props.py` edits the file Godot writes, then
  forces a reimport by deleting the imported copies.
- **Blender writes its log to stderr.** With `$ErrorActionPreference = 'Stop'`, PowerShell treats that as a failure,
  so the rebuild collects Blender's output with 'Continue'.

## Next

- Place light props in freight room by room, and retire each room's `rb_light` entities from the generator as it goes.
- Replace the plain blocker boxes (desk rows, lockers, the booth's console and seats) with furniture where the look
  pass calls for it.
- Before the enemy pass, bake furniture collision into the navigation.
