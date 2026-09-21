# Freight access / empty walkthrough 12

Route A now carries the accepted Registration/Screening language through Administration, Staff Preparation, Inspection, the optional Annex, Records, Security, Watch, Clearance and their corridors. The user explicitly waived another paper review for this continuation. [Use the guided Route A walkthrough](freight-route-a-walkthrough.md). Layout 12 retains the continuous flat dark floors and the existing route, objectives, stairs and shortcut. Application version remains 0.0.010. The [Route A quality pass](freight-route-a-quality-pass.md) corrects earlier services/fixtures, opens the Clearance office crossover and adds runtime render batching.

This is an early-campaign level 2/3 example. The roughly ten-minute target applies to a later normal populated run; the empty walk measures traversal, not final mission duration.

## Play

Open `RedBreach/project.godot` and press **F5**. **F6** returns to freight from any gym. The arrival airlock opens automatically; stepping into Receiving starts the timer and destination-title fade.

- **E:** use a nearby card, reader, button, control or ladder. Look at its interaction target; the existing reach is 2 m.
- **WASD / Shift / Space / Ctrl:** existing walk, sprint, jump and crouch. Movement tuning is unchanged.
- **Backspace:** reset the player, cards, doors, circuit, secret, ladder and walkthrough measurements.
- **F1 / F2 / F3:** movement gym, combat gym and encounter route. F4 still changes the encounter route's empty/combat mode there.

Security contains the Records-card detour and the freight card in A4. Power has the optional B2/B3 dead-end discovery and C1/C2 bypass. S1/S2 release from their branch sides. The lift needs freight clearance and restored power; use its cabin console to finish the test. The three A2 selector codes and upper BcD route work as planned. Use E at either end of the deployed ladder to climb.

The lift closes and records completion. There is no destination level or cross-level streaming yet. The Tr1 cache has a useful-only 25-health placeholder; enemies, encounters, ammunition distribution and final rewards await the next pass.

## What to judge on this walk

1. Room and hallway scale: which stretches feel purposeful, and which feel too empty or long?
2. Navigation: can you identify a gate's requirement and find its alternate route, objective or release?
3. Height changes: A2 entry platform, A3/A7 upstairs Records visit, A5 upper Watch floor, A6 six-metre descent, plus the existing B transitions.
4. Returns: compare the ordinary Security return with the enabled Maintenance route, and try the main stairs in reverse.

The HUD reports elapsed time, distance, current room, height and objective state. Completion, reset and scene exit save separate JSON results under `user://freight_walkthroughs` (normally `%APPDATA%/Godot/app_userdata/RedBreach/freight_walkthroughs`). Results include room visit times, objective/gate events, layout revision, version and source-map hash. QA disables storage. First-time exploration and a familiar route should be kept separate when interpreting timings.

## Editable sources

- Map: `RedBreach/maps/freight_01.map`, Valve 220, 32 map units/metre.
- Saved scene: `RedBreach/missions/freight/freight_blockout.tscn`; authored interactions remain outside Geometry.
- Rebuild: `tools/rebuild-freight-blockout.ps1 -Validate` builds, saves, reloads and checks the map. Save editor edits before rebuilding and reload the scene afterward.
- Layout record: `docs/freight-blockout-layout.json`; validation/room metadata: `RedBreach/missions/freight/layout.json`.
- Built continuation: [Route A record and walkthrough](freight-route-a-walkthrough.md); [placement data](freight-route-a-style.json).
- Historical paper drawings: [F-01 sample](freight-furnishing-plan.md), [A-01 baseline interiors](freight-a-interior-plan.md), [revision-04 whole-level baseline](freight-access-route-plan.png), [current elevations](freight-access-elevation-plan.md).

The source map is authoritative for future TrenchBroom edits. `tools/bootstrap-freight-blockout.py` generated the initial brushes; it refuses to overwrite an existing map unless explicitly asked. The normal rebuild never runs it. Update authored gates, labels, objectives and metadata when intentionally moving their geometry.

Plan coordinates use the hub at (190,260). Godot positions subtract (190,260) from plan X/Z; Y is floor height. [The A-01 record](freight-a-interior-plan.md) gives all moved doorways, interior stairs and card/selector positions. Records is now upstairs at +4 m; Watch rises to +6 m, and Clearance descends from +6 m to the hub floor. The BcD ladder and its destination remain in place.

The A2 entry platform remains a solid plinth. A3, A5 and A6 have true upper slabs with usable lower floors; B4 retains its overhead Maintenance deck. Ordinary gate apertures retain their 3 m width and 3.2 m clearance. Stairs retain 0.25 m rise / 0.5 m tread. Kenney dark grids cover neutral architecture with 1 m repeats and 0.125 m fine squares; orange identifies gates and the larger stairs.

The one-time `tools/apply-freight-a-interiors.py` application is source-hash guarded and is never called by normal rebuilds. The historical revision-04 bootstrap refuses the newer layout metadata. Continue editing the map directly in TrenchBroom.

## Validation

The saved map contains **2,178 brush collisions**. Rebuild/save/reload validation passed **217 freight checks and 38 Route A checks**, plus **nine shared greybox checks**, with zero failures. All 24,380 baked triangles passed the measured Kenney UV check. Validation covers the complete normal route, A in reverse, 19 stair flights in both directions, openings, gallery clearances, card/gate/selector/ladder behavior, reset and completion. The new pass checks supported prop placements, full-width A1 work aisles and eight hatch landing/emergence reservations using a 2 m wide body. Twenty-nine rendered player-eye views were inspected. Human walkthrough and populated combat review remain next.

The F-02 source audit confirms that all 1,183 original brushes outside the ten replaced reception furniture brushes remain literally unchanged. Eighteen new map brushes provide approved partitions, headers, uprights and beams. Props are external scene instances preserved by the normal rebuild. Shared movement, pistol, combat and addon files are unchanged in this pass. This revision completed build, headless QA and rendered capture without reported errors or warnings.

These are automated collision/progression checks, not human feel or encounter timing. Enemy navigation, pursuit on mezzanines, combat sightlines and resource balance need the later populated pass. Current blockout lighting, labels and controls are functional placeholders.

## Human review and next pass

The user's [revision-05 walkthrough](freight-playtest-05.md) completed through Maintenance in 296.18 s over 1,958.25 m, with Shift held according to their report. They accepted the route length and overall direction, and requested more believable doorway separation, room-specific ceiling heights, side-positioned stairs with visible lower destinations, and functional furniture/machinery blockout.

Use [Architecture language](architecture-language.md) for the resulting principles. The F-01 plans were reviewed and approved; their built sample now lets the user judge circulation and room function before extending the language to other rooms or making the enemy/pickup pass. The ten-minute populated target remains unmeasured.


The representative furnishing pass is [built as F-01](freight-furnishing-plan.md), with separate A1/A2/A8 sheets, an Inspection stair section and player-eye views. These supersede the revision-05 interior details in those three rooms only. Offices/staff spaces have 3.5 m ceilings; pump/workshop areas use 4.5 m, with a local higher envelope over the raised Inspection entry.


Current A1 reception is superseded by [F-02 registration](freight-registration-plan.md). Its approved bays, complete counter assembly, overhead/light housings and wall equipment use 25 reusable assembly instances. For later visual replacements, keep the saved scene placement and collision while replacing each asset's Visual subtree with Blender meshes. No extra mission dependency or actual pickup has been added.


Registration historically gained [F-03c / layout 08](freight-registration-recess-plan.md): a simple 0.25 m recessed walkway, staff door with a level approach, and furnished back office. Nineteen F-02 assemblies and all eight lights remain; six lounge assemblies are replaced by fourteen office placements. The second inactive item marker moves onto an office desk. F-03 preserves 1,200 prior brushes and replaces only the A1 floor brush, adding revised floor sections and two door infills. Other interiors and keyed gates retain their behavior.


The subsequent [Registration colour pass](freight-registration-palette.md) improves material separation while keeping this layout and its raised-floor colour. Current materials are visible in [the six-view preview](freight-registration-palette-built.png). Five shared brushes were divided solely for local material boundaries; occupied geometry is unchanged.


The [approved F-04 connected plan](freight-a1-density-plan.md) is built in Screening first, as layout 09. Its repeated ribs, angled upper corners, scanner/equipment and compartment frame are ready for critique in a fresh run. Administration and Staff Preparation remain planned. Validation: 217 freight checks and nine greybox checks pass; [four rendered views](freight-screening-built.png) were inspected.


Current revision is **10**: [Registration's continuous flat floor](freight-registration-flat-floor.md) supersedes the recessed orange walkway. The source map and saved scene contain 1,221 brush collisions. All 217 freight and nine greybox checks pass, with six Registration views inspected. The user requires a physical level change or border/seam wherever textures change; no contrasting flat pathway replaces the recess.
