# Freight v2 playtest 02: a faster run

**Session:** `playtests/freight_v2/2026-09-27_14-48-03`, recorded after [playtest 01](freight-v2-playtest-01.md)'s fixes
(the build still read version 0.0.017).

**Run:** a faster pass, skipping some parts. It finished in the lift at **379.8 s (6 min 20 s) over 1,235 m**, with 20
notes. The walk timer pauses while a note is typed.

As before, every fix is a generator rule, so it holds everywhere and on regeneration. To see a note on the current map:

```bash
powershell -File tools/view-playtest-note.ps1 -Session playtests/freight_v2/2026-09-27_14-48-03 -Note <n>
```

## Rules that came out of it

- **The plinth runs unbroken** (notes 1, 3, 8, 15, 16, 18, 19):
  - A **collar** in the room's plinth wraps the foot of every corridor mouth frame. It stands on the room floor on
    the frame's outer side, room face and inner side, so the band continues into the doorway.
  - Beside a flight of stairs the plinth **follows the flight's slope**. `brushkit.hull(uv_shear=...)` shears the
    texture so the painted band stays parallel to the slope.
  - At a floor step of up to 1 m along a wall (a landing's edge), the lower run's plinth **climbs at 45 degrees** to
    meet the higher one. This works whether or not the two runs are pieces of the same wall.
  - The plinth clears a mouth frame, ladder or switch only over that thing's own heights. A vent or door high
    above the floor no longer cuts the band under it.
  - A ladder on a plinthed wall stands out clear of the plinth, and the plinth runs on behind it. The ladder's new
    `step` property steps the climber off at the top in the same place as before.
- **A corridor that meets a lower room is capped** (note 2). This is the kit lab's `door_low` junction.
  - It applies where the room's ceiling is lower than the corridor's frame: C1 into Receiving, J2 into the lift
    machine room, and C2 at door 3.
  - The corridor ends in its rib frame and a plug shaped to its profile.
  - The room wall gets a door-sized hole, with a frame on the room face and a sill.
- **A threshold** carries the corridor floor through the room wall at every mouth, the opening's width (note 20).
- **Containers** (notes 4, 5, 6):
  - They stand on 0.25 m corner castings, so a stack reads as separate boxes with gaps between them.
  - Columns in a stack stand 0.25 m apart.
  - Tops and bottoms are corrugated like the sides.
- **Tall platform and stair sides are walls** (note 7). They use the room wall's material and origin, so a flight's
  side runs on from the platform's side as one surface. Step fronts keep the riser texture, and pit walls use the
  wall material too.
- **Walls** (notes 9, 11, 12, 14):
  - A wall is capped under a room stacked above only where that room's floor or walls cover the wall's whole
    thickness. A corner merely near such a room left slots up the wall.
  - A door or window is cut from every wall piece its width overlaps, so the overlook window has one frame.
  - A wall clipped out of a neighbouring room stops 1/16 m short of the neighbour's face.
- **The truck bay's sealed door is a roll door** (note 10): a corrugated curtain between jambs, with its roller
  housing above.
- **The stair room's top landing rail** runs to the wall (note 13). A rail stops only where a corridor actually
  leaves across the edge.

## The z-fight check now models func_godot's snapping

func_godot snaps every generated vertex to its `_vertex_merge_distance` of 1/32 m. A 1 cm gap between two faces
therefore closes in the build and flickers (note 14), although the map checker had passed it.
- `mapkit` now snaps face points the same way before comparing planes.
- The checker's first run under snapping found 38 flickering pairs the old check had missed.
- All of them are fixed at the rule that made them: collars stop 1/16 m short of the frame's end, riser arms are
  narrower than their risers, the roll door's jambs stop under its housing, and floors meet thresholds at the edge
  line.

## The coolant (note 17), decided

The glowing channel read as reactive goo with nothing to explain it. The user's call: **keep the coolant in the channel
and add pumps that visibly feed it into the reactors** (the big cylinders in the pit).
- Three coolant pumps stand in the channel (`COOLANT_PUMPS` in the plan).
- Each has a housing in the coolant, two guide posts and a crossbeam, and an outlet pipe. The pipe rises from the
  housing, arches over the bridge and drops into the top of the reactor opposite.
- The plunger is an `rb_machine` of the new kind `plunger`. Its head rises between the posts from walkway level to
  walkway eye level and falls back over 3 s, and the three take turns.
- A lamp in the coolant's colour brightens on each upstroke.

## Counts after the pass

- `LEAK: none, the level is sealed`
- `ZFIGHT: ... 0 VISIBLE` (with snapping modelled)
- `FREIGHT_V2_BUILD: 1606 brushes; 181 lights; 7 ladders; 30 kit pieces; 664 navigation polygons; save=0` (with the pumps)
- `MARKER_QA: 830 checks; 0 failures` (light floor min 0.371, median 1.423)
