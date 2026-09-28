# Freight v2 playtest 01: the completionist run

**Session:** `playtests/freight_v2/2026-09-27_12-16-32` (version 0.0.017, detail pass 1 built).

**Run:** the user's first completionist run, pinning notes along the way. The user thinks they reached every place at
least once.

**Result:** finished in the lift at **519.1 s (8 min 39 s) over 1,781 m**, with 24 notes. The game pauses while a note
is typed and the walk timer pauses with it, so this is walking and looking time. It is empty traversal, not a combat
timing. A completionist run with no enemies is already close to the brief's ten minutes for a familiar run.

The notes are fixed in the generator, so they hold on any regeneration. To see a note's view on the current map:

```bash
powershell -File tools/view-playtest-note.ps1 -Session playtests/freight_v2/2026-09-27_12-16-32 -Note <n>
```

## Rules that came out of it

These now apply to every room and corridor, not only where they were pinned.

- **A corridor meets a room through a frame** (notes 1, 12, 13, 14, 17):
  - The frame is shaped like the corridor's rib, a little thicker. It stands 0.25 m proud of the room face and runs
    through the wall to the wall's outer face, so no corridor texture shows in the room wall.
  - A 6 cm sill under it carries the change of floor texture.
  - For a box corridor the frame narrows the opening by 0.15 m; a crawl's frame only by 5 cm.
  - At a door, a plain panel fills the frame's opening around the door, flush with the room face.
  - Where a corridor ends at a pit or lower lane inside a room, the frame stands there too.
- **The plinth is a real foot** (notes 2, 6):
  - It stands 0.125 m proud of the wall and is 1 m tall on the floor beside it, so the band's texture change has
    its own geometry.
  - It joins at every corner, steps where the floor steps, and stops at stairs, coolant, ladders, wall switches and
    frames.
- **A room's walls are flush all round** (notes 5, 19):
  - A wall a room shares is its own half inside the edge. The rest of that edge now stands inside by the same half,
    so there is no 0.25 m jut where a shared wall meets an outside one.
  - Every pair of wall pieces meeting at a corner is joined where their faces meet and where their outer faces meet,
    whatever kind or thickness they are.
  - An outside wall is cut out of any neighbouring room it would stand in, over that room's height only.
- **Texture lines run level** (notes 6, 11, 16, 18, 21):
  - A room's walls share one texture origin, its first corner at its floor, whatever floor each edge stands on.
  - A corridor's walls share one height, its lowest floor, so panel lines run level past its steps.
- **Windows have frames** (note 4): a 0.15 m border proud of both faces and 5 cm into the opening.
- **Containers are several boxes** (note 3):
  - Each stacked container is its own box in its own colour.
  - The top row's last container is pulled a metre toward the room.
  - Each box has corrugated sides (QUOD tex90, the new `container` role, tinted per look) and its door on each end.
  - The crane's hanging container uses the same kit.

## One-off changes

| Note | Change |
|---|---|
| 7 | The compressor is a 4 × 3.5 m machine inside a railed enclosure at its old footprint (open to the spine). The piston is 1.7 m across, and its whole stroke is in view from both lanes. |
| 8 | The coolant's glow is lowered from 1.5 to 0.45 and a little greener: a liquid, not a white strip. |
| 9 | A soft unshadowed light (0.18) sits in the girder crawl. **F** toggles a flashlight on the player's camera (a spot, 18 m, off by default; F is the usual key, so it is not on the HUD). |
| 10 | The pump room's west wall now stands on the pipe gallery's roof, not on its ceiling. |
| 15 | The stair room's north-west corner is square: the jog corridor runs straight in, with no diagonal stub. |
| 20 | The big fan turns at 6 rad/s (it was 1.4). The lever throws sparks and a flash at once, then two more bursts while it visibly slows, then it settles blade-up. |
| 22 | The door 3 frame runs the full wall depth; its door panel fills the frame's opening. |
| 23, 24 | The gantry rail no longer breaks over the transformer cages, because a machine under a deck does not close the deck's edge. The rail runs the catwalk's full length, and the cage tops are 2.5 m below. |

**Not taken from note 24:** raising the ceiling so the player can jump over the rail and drop down. The rail is now
continuous, and 1.1 m is above the 0.95 m jump. If the user wants the drop, a lower rail section or a broken rail over
one cage would do it, and the ladder and stairs remain the only way back up.

**Also found while checking:** the torn fitting's dead corridor light is moved 2 m along the corridor rather than
removed, which kept the light floor.

## Tooling

- `check-map-zfight.py` no longer reports two coplanar faces with the same material and the same texture projection.
  They draw the same texels, so nothing flickers. The plinth corners rely on this.
- The generator writes window frames, mouth frames, sills, door panels, plinths and railings into their rooms' groups.
  `--room KEY` still regenerates one room in place.

## Counts after the pass

- `LEAK: none, the level is sealed`
- `ZFIGHT: ... 0 VISIBLE`
- `FREIGHT_V2_BUILD: 1470 brushes; 181 lights; 7 ladders; 27 kit pieces; 669 navigation polygons; save=0`
- `MARKER_QA: 830 checks; 0 failures` (light floor min 0.402, median 1.424)

The other labs still pass after the shared look and player changes:
- style lab: 306 checks
- kit lab: 117 checks
- movement and combat gyms
