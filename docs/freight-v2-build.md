# Freight access v2: G-01 greybox (stage 3, whole level first)

Status: **G-01 built and validated**, 2026-09-26, from plan revision 08
([freight-v2-plan.md](freight-v2-plan.md)). The user chose to build the whole
level before the room studies, on the condition that a single room can be
adjusted without rebuilding everything (see "Editing one room").

**F11** opens it from any gym or lab (or open
`RedBreach/missions/freight_v2/freight_v2.tscn`).
- A timer starts when you first move, and stops at the lift gate, so the
  empty walk can be measured.
- **P** switches presentation (off / subtle).
- **Backspace** returns you to the airlock and resets the timer.
- **E** climbs a ladder, up from the bottom or down from the top.

![Player-eye views](freight-v2-built.png)

## Files and commands

| File | Role |
|---|---|
| `tools/freight_v2.py` | The plan: the single source of truth, including the 3D build data at its end (ceilings, blocker heights, door sizes, ladder facings, lighting, capture views). |
| `tools/bootstrap-freight-v2.py` | **One-time** generator of `RedBreach/maps/freight_v2_01.map`. It refuses to overwrite; `--overwrite` regenerates everything; `--room KEY` regenerates one room in place. Never part of a rebuild. |
| `tools/polykit.py` | 2D polygon kit: convex decomposition and convex subtraction (walls with openings, floors with pits). |
| `RedBreach/maps/freight_v2_01.map` | **The editable source** (TrenchBroom) once generated. |
| `tools/write-freight-v2-scene.py` | Writes the scene shell: environment, navigation node, level script, player with its climb chart, capture views. Rewriting it clears the built geometry, so rebuild after it. |
| `tools/rebuild-freight-v2.ps1 -Validate` | Import, build, bake navigation, then run the marker validator. |
| `RedBreach/tools/build_freight_v2.gd` | Builds the map, bakes navigation and keeps only the navigation reachable from the route markers (the bake also finds the tops of ceilings). |
| `RedBreach/tools/capture_freight_v2.gd` | The 27-view sheet `docs/freight-v2-built.png` (run without `--headless`). |
| `RedBreach/mapping/fgd/rb_light.*`, `rb_ladder.*` | New map entities: an omni light, and a climbable ladder that uses the freight player's ClimbChart. |

**Expected counts on any machine** (after `--import`):
- `FREIGHT_V2_BUILD: 1002 brushes; 174 lights; 5 ladders; 671 navigation polygons; save=0`
- `MARKER_QA: 631 checks; 0 failures`

## What G-01 is

A walkable empty greybox of the whole plan, in the settled style: looks per
room, P1/P2 trapezoid corridors with ribs on the 4 m beat, and the light
floor.
- **Rooms:** floors, with pits, lanes and shafts cut out.
- **Walls:** exterior walls stand outward. A wall shared by two rooms is one
  centred wall. Where a room sits stacked over another (the booth notch
  under Logistics), the lower room's wall stops under the upper floor.
- **Openings:** cut from the plan. Corridor mouths take the corridor's own
  profile (the junction rule). Doors and windows are sized by kind, and the
  explicit openings include the fan hole.
- **Ceilings:** per room, with a bulkhead where two heights meet (Logistics).
- **Levels and stairs:** solid platforms, thin decks (the gantry U, the
  archive, the stair room's top landing), stairs solid down to the floor,
  and the bridge with rails.
- **Blockers:** simple solids at plan heights. Risers turn into the walls,
  and the piston rises to the ceiling.
- **Corridors:** P1/P2 kit profiles; S3 service stairs; the D2 duct with
  tiny ribs every 2 m; the crawls; the catwalk, as a railed deck with walls
  only where it leaves a room.
- **Ladders:** five, as `rb_ladder` entities. E climbs them, and the climber
  snaps onto the ladder going up.
- **Lights:** 174 `rb_light` entities.
  - Room lights are placed by coverage: every walkable metre, including decks
    and the space under them, is lit in line of sight.
  - Measured: minimum 0.41, 10th percentile 0.80, median 1.41. The floor is
    0.35 and nothing is waived.
- **Route markers:** 502 across five routes, walked by the real player:
  - card first, vent return
  - power first, S2 return (both ways)
  - the east completionist
  - the knowing player by the catwalk
  - the catwalk explorer through the fan

  Routes with the vent drop are one way.

**Not in G-01** (the progression and detail passes):
- Doors are open holes, apart from the sealed airlock, roll door and lift.
- No switches, locks, the cage release or card logic.
- The fan is its stopped hole, with no blades.
- The catwalk section (3) is down.
- The secret interiors (the bridge girder crawl, the cable vault, the
  conveyor crawl) and the crane rail with its hanging container are not
  built.
- There are no rails on stairs and platform edges, and no props.

## Editing one room (the user's condition)

- **Every room is its own TrenchBroom group**, named by its plan key (for
  example `PR Pump Room`). Its floor, ceiling, levels, stairs, blockers,
  lights and ladder are all in that group.
- **Corridors** are their own groups (`W1 Pipe run`, and so on).
- **Walls:** a room's outer walls are `PR walls`. A wall shared by two rooms
  is its own group, `CU|PR walls`.
- **Hand edits are surgical.** Isolate a group in TrenchBroom, edit it and
  rebuild. func_godot rebuilds the whole map each time, but the map file is
  the source, so nothing outside the group changes.
- **Regenerating one room from the plan:** after changing a room in
  `freight_v2.py`, run:

  `python tools/bootstrap-freight-v2.py --room PR`

  It swaps only the groups starting with `PR` and the shared walls naming
  it, keeping every other group and its hand edits.
  - Tested: a hand edit in Receiving survived a Pump Room regeneration.
  - Brush, light and ladder counts were unchanged.
- **The one rule:** rooms only meet at their openings. As long as an
  opening keeps its position, size and floor height, no neighbour changes.
  Moving an opening is a two-room edit: the room, and the room or corridor
  on the other side.

## Findings from the build

- **Corridors can open off a side.** The pipe bay's mouth needed the pipe
  run's own side wall cut below the opening top, not only the room's wall.
- **Stacked floors need tags.** On a point with two floors (the gantry over
  the substation floor), a route point needs its tag, or it takes the floor
  below. Points exactly on a polygon edge are ambiguous.
- **Stairs below the floor.** A flight that descends below its room floor
  (the U-turn's far steps into the lane) needs the floor cut from under it.
  Otherwise a 0.25 m step becomes a 0.5 m ledge. Every flight is now solid
  down to the room floor.
- **Ladders:** a climber brushing the ladder panel failed the "can stand"
  check. Snapping onto the ladder spot going up fixes it, and matches how
  ladders usually work in games.
- **The fan octagon must enclose the circle.** Otherwise its flat bottom sits
  0.36 m up, over the 0.3 m step, instead of on the 0.25 m lip.
- **Validator changes:**
  - Players derived from the gym player are accepted.
  - A "climb" posture uses the nearest ladder.
  - `oneway` routes are walked forward only.
  - Shapes and meshes owned by scripted entities (ladders) are not counted as
    brushes.
