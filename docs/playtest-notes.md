# Playtest notes

Leave notes during a run, then Claude reads them and changes the level. It works in every scene with a 3D camera
(the `PlaytestNotes` autoload, `RedBreach/playtest/playtest_notes.gd`). It is silent in headless runs, so validators
never trigger it.

## In game

| Key | What it does |
|---|---|
| **Q** | Note. Shoots a ray from the crosshair, marks the spot with a numbered pink pin, pauses the game and opens a text box. **Enter** saves, **Esc** cancels. |
| **Z** | Quick z-fight mark. The same record without the text box (the note reads `z-fight`). Aim at the flicker and tap Z. |

- **The run timer stays paused while you type**, so a run with notes still gives a near-real time.
- **Pins stay in the level** for the rest of the session, so you can see what you have already noted.
- **Freight v2 also logs its lift finish** (time and distance), and a restart when you press Backspace mid-run.

## Where it goes

Each run, from the first note, writes one small text file (a note is one line, well under a kilobyte):

`playtests/<scene>/<date_time>/notes.jsonl`

- It sits at the workspace root, outside the Godot project.
- In an exported build it falls back to `user://playtests`.
- **There are no screenshots** (user, 2026-09-26: they took too much space). Each note keeps the camera's transform
  instead, and the view is rendered again on demand (below).

Each note records the following:
- the text
- the run time and distance, where the level offers them
- the camera's position, rotation (degrees, Godot's YXZ order) and field of view, and the window size
- the player's position and rotation
- the hit point, its surface normal and facing, and its distance
- the collider and the collision shape. func_godot names it `entity_0_brush_N_collision_shape`, and N is the brush's
  index in the `.map` file.

The session line records the build version and the map file's MD5, so a later reader can tell whether the map has
changed since the run.

## Reading a session

```
python tools/read-playtest-notes.py            # the newest session
python tools/read-playtest-notes.py --all      # every session
python tools/read-playtest-notes.py playtests/freight_v2/<date_time>
```

For every note it prints:
- the text, and the room or corridor the player was in (from the plan, for freight v2)
- every brush face at the hit point in the map **as it is now**, with the brush's `//` name and TrenchBroom group
- when two brushes have a face on that plane facing the same way: **Z-FIGHT**, and which two brushes they are

**To see what the player saw:**

```
powershell -File tools/view-playtest-note.ps1 [-Session <folder>] [-Note <n>]
```

It loads the note's scene, puts a camera at the recorded transform, field of view and window size, and hides the HUD.
It draws a thin pink crosshair on the aim point and saves `RedBreach/.godot/playtest_views/<scene>/<date_time>/note_NNN.png`,
which git ignores. With no session it takes the newest; with no note, all of them. It renders the map **as it is
now**, so after a fix the same note shows whether the fix worked. The first notes, made before transforms were
recorded, are posed from their camera position and look direction.

`RedBreach/tools/test_playtest_notes.gd` drives the autoload with real key events (a Z mark, then a typed Q note),
checks the session it wrote and deletes it. Run it without `--headless`.

## The automatic check: leaks and z-fighting

`tools/check-map-zfight.py <map>` finds most z-fighting without a run. `tools/rebuild-freight-v2.ps1 -Validate` runs
it on every rebuild.

**How it works:**
1. It reads the map as edited (`tools/mapkit.py`), so it covers TrenchBroom edits too.
2. It voxelises the solids at 0.25 m, thickened by half a cell so hairline contacts seal.
3. It floods the air from the route markers.
4. A pair of coplanar, same-facing, overlapping faces of different brushes is reported only when the space in front
   of it is that reachable air.

The undersides of stacked slabs and the outsides of walls are hidden, so they never count.

**Leaks:** if the air reaches the edge of the map, the level has a hole. The check then works like Quake's pointfile:
1. It prints the shortest way out.
2. It plugs that route and traces again, so every hole is listed.

A leak fails the rebuild.

Freight v2 before and after the first pass: **1,122 visible z-fighting pairs (1,605 m²) and 35 leaks**, down to
**none of either**. The generator rules that fixed them are in
[freight-v2-build.md](freight-v2-build.md#z-fighting-and-leaks-pass-1).

**The check can miss what a player finds.** The user's first Z mark (the S1 landing against the end of the
Logistics/Sorting Bay wall, at the dock edge) was one the check had missed. The thickened grid had swallowed the air
in front of a face tucked into a four-room corner. The check now decides "seen" by walking out from the face through
the true geometry until it reaches flooded air. A point touching any brush counts as solid, so the walk cannot slip
through the seam between a wall's plinth band and the band above it.
