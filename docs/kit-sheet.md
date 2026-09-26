# Kit sheet: K-01 first pass

The one-page output of Phase 2 ([plan](kit-lab-plan.md), [built views](kit-lab-built.png)).
Built 2026-09-25, refined 2026-09-26, and validated; the user called it a success after the final texture pass. **F10** opens `RedBreach/kit/kit_lab.tscn`.
Nothing here is final until the user has walked it.

## Pieces

Brush counts come from the TrenchBroom groups in `maps/kit_lab_01.map`.

| Piece | Dimensions | Brushes | Notes |
|---|---|---:|---|
| **P1 corridor** (signature) | 6 m floor, 3 m ceiling, 4 m high. Ribs every ~4 m, 0.375 m proud, 0.5 m deep | ~16 per 11 m | **The rib foot drops straight down**, flush with the rib above; 4.5 m clear between rib feet |
| **P2 corridor** (secondary) | 6 m floor, vertical to 2 m, slopes in to a 3.5 m ceiling | ~22 per 16 m | The rib is vertical from floor to 2 m, then follows the slope |
| **45° turn** | Two 45° mitres on the bisector, 5.66 m diagonal leg, one rib in the leg | shared with its run | **Mitres cleanly in P1 and P2; no fill geometry.** Fittings stay ≥ 2.2 m from a bend |
| **Stair (in a P2 run)** | 12 × 0.25 m risers on 0.5 m treads, 2 m landings; walls and ceiling follow the flight | ~60 for a 3 m rise | Steps span the shell; ribs on the flight bed into the steps |
| **Corridor-to-room junction** | The room wall is **cut to the corridor's own profile**. The corridor runs through it to the room's inner face, and **its rib stands at the room face** (0.25 m proud) as the connection, with a 0.0625 m sill under the rib that carries any floor-texture change | ~13 per junction | Replaces the 7 � 4.5 m bulkhead slab (user, 2026-09-26). Variants: **open**; **door** (a panel shaped to the profile holds the door, flush with the room wall); **door_low** (for a room lower than the corridor: a door-sized hole in the room wall, with the corridor ending in its rib and a plug shaped to the profile) |
| **Bulkhead** | 1 m deep, 7 m � 4.5 m frame | 6 | Kept only for a **profile-to-profile** change inside a corridor (the style lab). Never at a room |
| **Junction hub** | 14 m octagon, 3.5 m clips, 4.5 m walls, 1 m haunch to a 5.5 m ceiling; ports are its four square faces | 27 + a junction per port | **Replaces the T and the 4-way.** Each 7 m square face takes one corridor junction |
| **Debris walk-around** | A fallen rib and two slumped panels plus rubble over 4 m of one side; **2.4 m lane** kept | 10 | Leaves stumps where the rib stood |
| **Crouch collapse** | 3 m long, **2.0 × 1.4 m** clear: a standing player is blocked, a crouched one passes, the larger bugs cannot follow | 3 | Dead bay under a red emergency beacon |
| **Threshold step** | +0.25 m, just inside a door | — | Part of R1 |
| **Sealed hatch** | 2.5 m aperture, 0.25 m frame ring, grate plate. Fits in a ceiling (including P1's 3 m ceiling), on a knee wall or in a floor | 5 | Reservation only |

**Rooms are composed, not kit.** H1 (a 24 × 32 m knee-wall nave with a catwalk
and an edge stair) and R1 (a control room shaped by its console row and
window) are records of those rooms, not templates.

## Rules this pass confirmed

1. **Corridors meet rooms through their own profile.** The room wall is cut to
   fit and the rib is the frame. Bulkheads only change one profile to another
   inside a corridor. The look changes at the junction rib and sill.
2. **Mitre on the bisector.** Wall solids are cut on the bisector at every
   bend. The trapezoid needs nothing extra.
3. **Rib feet are vertical.** They are never offset like a plinth.
4. **Lights are per bay**, and never in a mitre. Damage is a lighting state:
   flicker, dead, emergency.
5. **Validation is markers**, not a script per map (see below).

## Validation: one generic validator

`tools/validate_markers.gd` reads markers placed in the map. Marker
definitions live in `mapping/fgd/`, and TrenchBroom reads
`tools/trenchbroom/RedBreach/RedBreach.fgd`.

- **`rb_route`:** the real player walks each route forward and back, standing
  or crouched, up and down stairs and through doors.
- **`rb_probe`:** stand_clear, crouch_only and headroom checks.
- **`rb_nav`:** bug navigation pairs that must connect or must be blocked.
- **Always checked:** brush count against collision count, and no
  default-texture surfaces.

**K-01: 115 checks, 0 failures**, including the light floor. That covers 2 routes with 30 waypoints, 14
probes and 4 navigation pairs:
- hub to the hall floor: connects
- the hall floor to the catwalk, by the stair: connects
- round the debris: connects
- through the collapse: **blocked**

Two probes needed moving during the build, and both lessons are worth keeping:
- **Put a probe on a tread's top, not inside a step.**
- **A standing capsule on a 0.5 m tread always touches the next riser.** Check
  stairs by walking them and with headroom probes, not with stand_clear.

## The light floor ("no darker than")

User rule, 2026-09-25: set a minimum brightness and go darker **only on
purpose**, for hiding places or broken lights.

**How it is measured:**
- The generic validator samples every walkable point of the navigation mesh
  (about every 1.2 m) at bug height, 1.0 m.
- At each point it adds up the light that reaches it: Godot's omni falloff
  for each light, blocked by geometry when the light casts shadows, plus the
  sun and ambient.
- **The floor is 0.35.** For calibration: ambient alone is 0.074, the K-01
  median is 1.40, and the corner under the catwalk that the user called too
  dark measured **0.11**.
- **To go darker on purpose, place an `rb_dark` marker** with a radius and a
  reason. K-01 has two: the fallen-rib stretch (failing and dead fittings) and
  the collapse (a dead bay under an emergency beacon).

**Applied to K-01:**
- Fittings under the catwalk deck every ~6 m.
- Two north-wall fittings.
- A light at the stair foot.

The lab's minimum outside the dark zones rose from 0.11 to above 0.35, and the
10th percentile is 0.62.

## Texture choice and alignment

User feedback, 2026-09-25: the problems were texture choice and alignment, not
geometry.
- A texture that does not tile was used where the surface repeats: the heat
  pipes ran dark to bright and repeated.
- The busy dotted plate covered whole floors.
- The seams did not line up with the architecture.
- The stair risers wore floor plate.
- The QUOD bulkhead carried a hazard band.

**The tiling catalogue.** `tools/audit-textures.py` measures every pack
texture on each axis and writes `docs/texture-catalog.json` and
`docs/texture-catalog.png`. The classes are:
- **T:** seamless.
- **P:** a panel border, so it repeats as a grid.
- **X:** never repeat. That means a gradient, a mismatched edge, or content
  such as a hazard band or an emblem.

Of 393 textures, 287 tile both ways, 72 one way and 34 are features. Two
manual overrides record what the numbers cannot see: `FEATURES`, for painted
bands and emblems, and `PANELS`, for bevels that were checked by eye.

**Roles declare their tiling.** `style_lab.ROLE_TILING` states what each role
needs: `HV`, `H` (the plinth band, which is pinned vertically) or `fit` (a
feature: doors, screens, service panels, grate squares). The scene writer
**refuses to build** if a role's texture cannot meet it. Putting the old heat
pipe back is rejected (`warm/pipe needs HV but packs/quod/tex45 is TX`).

**Alignment.** brushkit places a texture origin per brush, so seams sit on
geometry:
- **Corridor floors and ceilings** are centred on the run, a whole tile either
  side, and follow its direction through turns.
- **Corridor walls** start their panels at a rib station and at each segment's
  bottom edge.
- **Bulkheads** start at the frame's outer edge.
- **Room walls** start at their own corner and bottom edge.
- **Feature faces** are fitted a whole number of times, starting at their
  edges.

**Choices changed:**

| Before | After |
|---|---|
| Heat pipes: QUOD orange gradient (TX) | A tileable dark ribbed panel, warm-tinted in the warm look |
| Bulkhead: QUOD tex238 with its hazard band | Level Eleven's plain riveted panel, in every look |
| Steel walls: riveted panel, repeating loudly | A plain framed panel |
| Concrete floor: the dotted plate | Level Eleven concrete, darkened by a material tint |
| Dotted plate as a whole floor | **A feature only**: one 2 m square recessed 0.125 m at the hub centre, and a pair of squares beside each hall tank. The texture changes where the floor steps down |
| Stair risers: floor plate | A `riser` role; treads stay floor |
| Hazard: a small QUOD stripe that broke on vertical trims | Level Eleven's panel stripe, tiling both ways on trims |
| Screen emission 1.6 | 0.7 (it bloomed white at close range) |

**Final pass, 2026-09-26 (user):**
- **Ceilings continue the look's own slope and wall material:** plain tan in
  warm, concrete in concrete, the framed steel panel in steel. QUOD's
  corrugated tex90 read wrong overhead. It is reserved for **container sides
  and roll doors**.
- **A door is cut into a plain `door_panel`**, so the cut never truncates a
  patterned texture (the warm riveted strip did).
- **A room shares one texture origin across all its walls** (the hall uses its
  corner). Junction wall pieces and door panels use it too, so a pattern runs
  straight across a cut instead of restarting at it.

Tints are part of a look entry: `(texture, (r, g, b))` multiplies the albedo,
so a pale texture can make a calm dark floor.

## Texture packs (next)

User, 2026-09-26: organise textures as **packs by area function** ("admin
pack", "machinery pack", "residential"), chosen to fit the story, not by
material. The mechanism already exists: a pack is a named role-to-texture set
(today's `LOOKS`), with tiling enforced per role. Warm, steel and concrete get
recast as function packs once the story says which areas the levels need.
Residential needs curating from scratch.

## Production data (E1)

| Stage | Claude time |
|---|---|
| Paper plan (module, drawing, notes) | ~15 min |
| Marker FGD and generic validator | ~10 min |
| Map generator, scene, build, navigation, first validated capture | ~10 min |
| Two fix rounds: sliver haunch faces, probe placement, bay lights at bends, hall brightness | ~5 min |

407 brushes and 14 pieces in about 20 minutes of build time after approval.
The same caveats as Phase 1 apply: the pipeline is reused, and this is not a
level with progression and encounters. **Handoff (E2) is not tested yet**:
the user edits a piece in TrenchBroom and we rebuild.

## Known first-pass issues

- The steel look reads dark in the arrival room and the hub; the concrete and warm looks read well.
- The console screens in R1 bloom white at close range (the shared `screen` emission of 1.6).
- The stair treads are dark and hard to read on the way up. Nosing trims would help.
- The layout drawing still shows R1 as an octagon. The built R1 is a 7 × 8 m room with its window corners clipped.
