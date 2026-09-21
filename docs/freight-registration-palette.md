# Registration blockout colour pass

> Floor treatment superseded by [layout 10: continuous flat floor](freight-registration-flat-floor.md). The recessed/orange walkway below is historical; staff-door, furniture and non-floor palette decisions remain.

Built on freight layout 08, without a commit or project-version bump. The user requested stronger separation between blockout surfaces while retaining the floor colour. Scope is the completed Registration sample: arrival/counter, waiting, staff bay and back office.

[Entry preview](freight-registration-palette-entry.png) | [Six rendered views](freight-registration-palette-built.png) | [Assignments and source audit](freight-registration-palette.json)

| Surface | Kenney assignment |
|---|---|
| Existing raised floors and staff landing | Dark/texture_06, unchanged |
| Walls and internal partitions | MutedGreen/texture_01 |
| Ceiling | GreyPale/texture_01 |
| Recessed walkway | MutedOrange/texture_06 |
| Shallow step edges | MutedOrange/texture_03 |
| Counter, seating, cabinets and equipment bodies | MutedPurple/texture_01 |
| Tops, panels, structural uprights and beams | GreyMedium/texture_03 |
| Overhead service trunks | GreyMedium/texture_01 |
| Light housings | GreyCharcoal/texture_01 |

Existing door colours, status lights, screen emission, actual lighting and exterior view remain. Material-only edits keep all prop meshes, collision, transforms and metric projection unchanged. Twenty-seven active prop assets now reference role-specific materials in `RedBreach/props/blockout/materials/`; original shared F-02 materials remain available.

Map textures are assigned in the authoritative source map. Five shared shell/ceiling brushes were divided at the existing Registration boundary so adjacent rooms retain their materials. Their combined occupied shape is identical. No doorway, floor level, route or furnishing position moved. The saved map contains 1,216 brush collisions; layout revision stays 08 with material revision registration_palette_01. Future map rebuilds preserve these source assignments and saved prop references.

Validation: rebuild/save/reload passed **199 freight checks**, and the separate greybox suite passed **9 checks**. All 14,192 baked triangles retain orthogonal one-metre texture repeats. Six rendered views were inspected. Source audit confirms all eight raised-floor upper-face records are identical, including their texture and UVs; all palette PNG hashes match their original manifest. Build, QA and rendered-capture logs are clean.

`tools/apply-registration-palette.py` records this guarded one-time application. Do not run it during normal rebuilds or use it to overwrite later TrenchBroom/prop edits.
