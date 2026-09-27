# Corridor lab findings (architecture labs, 2026-09-21 to 09-22)

The architecture labs (a 24.5 m straight run, then a corner / T walk of 107.66 m) were removed in the cleanup of
2026-09-26. The kit lab now carries the corridor profiles (`tools/style_lab.py` `PROFILES`, `tools/kit_lab.py`). These
are the findings to keep. The labs themselves are in git history before the cleanup commit.

## Rhythm and length

- **One global 4 m rib beat**, measured along the centreline and never restarted after a turn. A station that falls
  inside a turn is skipped, never nudged, so the beat cannot drift. The user confirmed it: "rib beat feels good".
- **52 m is the MAXIMUM straight run, not a comfortable one.** Interrupt a long run before it gets there. Interrupters
  are wider than sight blockers:

  | Interrupter | Blocks sight | Changes movement |
  |---|---|---|
  | Corner, T, 4-way | yes | turns you |
  | Door | yes | stops you (can be locked) |
  | Fallen debris | partly | walk around |
  | Low cables, collapsed panel | no | crouch (check against `crouch_height = 1.1`) |
  | Portal bay, window, alcove | no / relieves it | no or slightly |

  The walk-around and crouch interrupters cost the player time and posture, not sightline. They are also the kit's
  first chance to tell the story: a colony under attack, a hallway something has happened in.

## Turns and junctions

- **A single turn uses the 45° leg (V4); a T or 4-way stays square (V1).** A 90° turn already bulges to 8.49 m across
  the diagonal. Chamfering every elbow of a junction opens it into a lobby: "a large lobby in between the junctions".
- **Cut each run on the bisector plane at both ends.** At 90° this gives the square corner; at 45° it gives the leg,
  with the inner and outer walls bending 2.4853 m apart (2h(√2 − 1), irrational, so snap to the grid). No mitre face
  is ever built: the two runs' wall solids overlap, and the visible edge is where their planes meet.
- **A T is a through corridor plus a branch**, not a path with a vertex, so the bisector rule does not apply.
  - The through corridor omits its wall AND its footing across the opening, or the footing z-fights the branch floor.
  - The branch lays a **threshold plate as wide as the opening**, or there is a 0.50 m hole at each jamb.
  - The jamb corners have a real void that is wide at the floor and ceiling and closed across the panel band. It is
    filled one profile band at a time, with a footprint that shrinks as the profile reaches out.
- **A junction needs a setback:** ribs pinned 6.00 m (1.5 pitches) from its centre on every arm, leaving 2.75 m of
  clear wall from jamb to rib face.

## Section and materials

- The rib's toe stands on the protected lane line, so opposite toes make a 4.00 m clear lane in a 6.00 m corridor. It
  is vertical to knee height, then battered back. A pillar that stops halfway down a wall does not read as structure.
- No walkable outward facet sits at exactly 45°: that is the `floor_max_angle` default, so it is a coin flip.
- Registers separate by geometry and shadow, not tonal contrast. A charcoal plinth on pale infill read as a black void.
- Materials split by ELEMENT (rib, bay, floor), not by height band. The structure is the lighter zone, with the bay
  falling away behind it.
- Facet count is nearly free; rib count is the cost.

## Light

- **Lit by default, off by deliberation.** Every bay has a fitting. An off bay is a broken fitting used rarely and on
  purpose (FR-006: a power cut as a mission event).
- **In an unlit bay it is the ceiling that reads wrong**: the walls still catch spill from the neighbouring bays.
  Lighting every bay at 0.62 energy raised the ceiling by a mean of 40 brightness points while the floor rose only
  about 9.
- **Ambient is the wrong lever.** At 0.16 it flattened the corridor back to greybox. Contrast comes from many local
  lights, and light range decides the spill.
- **The light node is not the fitting.** A node just under a large flat ceiling leaves it dark (grazing N·L), so drop
  the node below the soffit.
- **A fitting only needs a ceiling; a rib needs two walls.** Excluding lights wherever a rib cannot stand left the T,
  the decision point, as the darkest spot.
- Emissive materials light nothing in Godot without GI. An OFF fitting must not glow.
- Generate anything named after a tier from the table that defines it (a renamed tier once wrote zero lights).

## Brush-writing traps

- Define a face plane from three points that are really distinct. A repeated vertex gives a null normal, and the
  brush is left unbounded.
- Never let a tapering prism share a vertex between its two rings ("cannot get winding basis").
- A brush count from the generator that does not match the build's collision count means solids are being dropped.
