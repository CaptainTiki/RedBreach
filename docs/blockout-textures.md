# Unified Kenney blockout textures

Movement, Combat Gym and Encounter Route Test now use the supplied Kenney greybox sheets for architectural surfaces, platforms, stairs, ramps, covers, door panels/frames, switch housings, target plates, the arena gate and vent grates. Status lights, route/timing marks, text, enemies, weapons and effects retain their readable gameplay colours.

The supplied assets remain unchanged: 78 PNGs across Dark, Light, Green, Orange, Purple and Red. Original generated `textures/gym` files remain available as historical assets, but no active gym architecture references them. The source pack is [Kenney Prototype Textures](https://kenney.nl/assets/prototype-textures).

## Current measurement convention

**A full 1024 x 1024 texture repeat is 1 x 1 metre.** This agrees with the explicit `1 x 1 meter` text printed on the coloured sheets. The earlier 2 m repeat convention was incorrect for that label and is superseded everywhere by this pass.

- Full repeat: **1 m**.
- Half-texture divisions: **0.5 m**.
- Fine divisions at 128 pixel intervals: **0.125 m (12.5 cm)**.
- TrenchBroom Valve 220 face scale: **0.03125 on both axes**, at 32 map units/metre.
- Calculation: `1024 pixels * 0.03125 map units/pixel / 32 map units/metre = 1 metre`.
- The resolution text `1024 x 1024` gives pixel dimensions; the separate printed metre label determines the intended physical repeat.

Brush texture axes are orthonormal and anchored to map origin, with zero shifts. Cardinal surfaces line up on the world grid. The ramp's texture axes lie in its sloped face, so repeats measure actual surface distance instead of a shortened horizontal projection. Do not use Fit to stretch a single repeat over an arbitrarily sized brush. Texture-locking a move may change grid phase; realign to this convention when metre alignment is required.

Authored primitive props use local triplanar mapping at scale `(1,1,1)`, so one repeat is one metre independent of the default box UV atlas. It stays attached to moving door leaves. Keep metric props at unit node scale and edit mesh dimensions; scaled visual target hit reactions are feedback, not measurement references. Godot documents [local and world triplanar mapping](https://docs.godotengine.org/en/stable/tutorials/3d/standard_material_3d.html#uv1-and-uv2).

The portable and installed Red Breach TrenchBroom definitions both default new faces to 0.03125. Restart TrenchBroom to reload its game definition. Existing faces retain their authored settings; the three source maps have all been converted explicitly.

## Palette

| Use | Supplied texture |
|---|---|
| Neutral walls | Dark/texture_01 |
| Neutral floor surfaces | Dark/texture_06, with center crosses |
| Jump stations and high-jump blocks | Purple/texture_03 |
| Runway, return route, ramp and door panels | Green/texture_01 or texture_03 |
| Stairs, opening frames, cover and crouch tests | Orange/texture_01 or texture_03 |
| Target plates | Red/texture_03 |
| Vent metal and switch housing | Dark/texture_06 or texture_01 |

The former Light/texture_01 walls were using the pack, but the fine grid washed out against the near-white sheet. The Dark sheets make the grid readable under the existing lighting. The melee release panel is green and the spitter panel orange; the spitter's mouth remains its bright yellow-green weak point.

Mipmaps are enabled on used sheets, with the existing crisp mipmapped filter. Preserve Godot-generated import settings and texture paths. The map material root remains `res://textures`; paths are `greybox/<Color>/texture_NN`. Door/window diagram sheets are not used to establish opening sizes. Preserve tested clearances.

## Validation and rebuild

All **863 map faces** retain exactly the same plane coordinates as before the material pass. Collision counts remain 69 movement / 22 combat / 53 route; navigation remains 27 combat / 100 route polygons. Existing gameplay validation passed all 397 checks during the pass. The final one-metre correction changes only texture projection.

`res://tools/validate_greybox.gd` checks all saved architectural surfaces and derives physical distances from their actual mesh vertices and UVs. Across **1,724 baked triangles**, both UV directions measure one metre per repeat and are orthogonal, including the ramp. Nine checks pass, including local metre projection on the door, switch housing and vent. Maximum floating-point repeat error was under 0.000001 m. Rendered movement, ramp, combat and route captures were inspected at the final scale.

Use the normal rebuild tool for the affected map. After a material/UV pass, also run Godot headlessly with `--script res://tools/validate_greybox.gd` and an explicit `.godot` log file, then inspect `capture_greybox.gd` rendered views. Do not edit baked Geometry materials alone; those edits would be replaced by the next map build.
