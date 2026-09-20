# Freight access / empty walkthrough 04

The reviewed route is built and ready for the first scale, height and progression walkthrough. This is an early-campaign level 2/3 example. The roughly ten-minute target applies to a later normal populated run; this empty walk is a measurement, not a duration guarantee.

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
3. Height changes: A2 entry mezzanine, A6 upper arrival, B2 exit mezzanine, B4 overhead deck/descent and B6 raised controls.
4. Returns: compare the ordinary Security return with the enabled Maintenance route, and try the main stairs in reverse.

The HUD reports elapsed time, distance, current room, height and objective state. Completion, reset and scene exit save separate JSON results under `user://freight_walkthroughs` (normally `%APPDATA%/Godot/app_userdata/RedBreach/freight_walkthroughs`). Results include room visit times, objective/gate events, layout revision, version and source-map hash. QA disables storage. First-time exploration and a familiar route should be kept separate when interpreting timings.

## Editable sources

- Map: `RedBreach/maps/freight_01.map`, Valve 220, 32 map units/metre.
- Saved scene: `RedBreach/missions/freight/freight_blockout.tscn`; authored interactions remain outside Geometry.
- Rebuild: `tools/rebuild-freight-blockout.ps1 -Validate` builds, saves, reloads and checks the map. Save editor edits before rebuilding and reload the scene afterward.
- Layout record: `docs/freight-blockout-layout.json`; validation/room metadata: `RedBreach/missions/freight/layout.json`.
- Paper drawing: [current plan](freight-access-route-plan.png), [editable SVG](freight-access-route-plan.svg), [elevations](freight-access-elevation-plan.md).

The source map is authoritative for future TrenchBroom edits. `tools/bootstrap-freight-blockout.py` generated the initial brushes; it refuses to overwrite an existing map unless explicitly asked. The normal rebuild never runs it. Update authored gates, labels, objectives and metadata when intentionally moving their geometry.

Plan coordinates use the hub at (190,260). Godot positions subtract (190,260) from plan X/Z; Y is floor height. T1 moved into A2 at (32,236)->(32,232), T5 into A6 at (133,172)->(133,176), and T7 into B2 at (342,186)->(342,182). The ladder climbs beside its landing at (148.4,62), not through the slab. The selector is near (24,222), with the Tr1 cache at (44,219).

Low 2 m mezzanines are solid raised platforms. B4's +6 m Maintenance deck has usable space beneath. Ordinary doors have a 3 m clear opening and 3.2 m clearance. Stairs retain 0.25 m rise / 0.5 m tread. Kenney dark grids cover neutral architecture with 1 m repeats and 0.125 m fine squares; orange identifies gates/stairs and green the door leaves.

## Validation

The saved map contains 605 brush collisions. Final rebuild/save/reload validation passed **88 checks with zero failures** and no engine/script errors. The freight checks cover sampled floor heights, standing clearance, all 13 stair flights in both directions, continuous normal/upper routes, both ladder directions, camera-ray interactions, required cards/power, one-sided releases, selector exclusivity, useful-only cache, reset and completion. Baked UV projection is checked against 1 m Kenney repeats. The shared movement gym and 64-check combat suite also passed after adding the F6 shortcut. Player-eye captures were rendered and inspected.

These are automated collision/progression checks, not human feel or encounter timing. Enemy navigation, pursuit on mezzanines, combat sightlines and resource balance need the later populated pass. Current blockout lighting, labels and controls are functional placeholders.
