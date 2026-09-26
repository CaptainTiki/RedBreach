# Kit lab K-01: Phase 2 paper plan

Status: **built and validated as a first pass**, 2026-09-25. **F10** opens it. Results: [kit-sheet.md](kit-sheet.md), [kit-lab-built.png](kit-lab-built.png). This is Phase
2 of the [clean-slate test plan](clean-slate-test-plan.md), in the settled
Phase 1 style ([style-lab.md](style-lab.md#phase-1-settled-2026-09-25)).

Drawing: [kit-lab-plan.png](kit-lab-plan.png), a plan view plus sections for
P1/P2, the crouch collapse, the hall and the stair. All numbers come from
`tools/kit_lab.py`, which the drawing reads and the build will read.

## User notes on approval

1. **Rib feet come straight down.** A rib must not copy the wall's plinth by
   stepping out at the foot the way a wall footing does. That leaves a jagged
   notch where the plinth offset meets the slope. From the floor, the rib's
   inner face rises **vertically, flush with the rib above**, until it meets the
   rib's line over the plinth (1 m), then follows the wall. It reads as one
   member standing on the floor. A more inventive foot (a shoe or a pedestal)
   can be tried later.
2. **Rooms are not a shape.** Build out what is in a room (equipment,
   circulation, the work it does) and let that define the perimeter and wall
   shape. H1's knee-wall nave is fine **for this hall only**. It is not a rule
   that halls are knee-wall naves, and the kit does not include a stock room
   shape. The same applies to R1: its desks and window come first, and its
   walls follow them.

## Purpose

Build every piece that ten levels need, once each, in the settled style, and
prove that:
- the pieces **join cleanly** (B1)
- they **scale** from an office to a hall (B3)
- the **interrupters** work (B4)
- the **bugs can use** the angled spaces (D1/D2)
- **one validator** can check any map (E3)
- you can **edit** what I build (E2)

The output is a **one-page kit sheet**: each piece's dimensions, brush count,
rules and authoring time.

## The walk

A loop with one spur, about 130 m round, plus a 22 m spur:

> A0 arrival > C1 (P1) > **J1 hub** > C5 (P2) > T2 turn > **S1 stair up 3 m** >
> catwalk (the hall is seen from above first) > hall stair down > hall floor >
> wide door > C3 past **D1 debris** > **T1 turn** > C2 > hub.
>
> Spur: hub > C4 (P2) > **X1 crouch collapse** > personnel door > **R1 control room**.

## Pieces

| Piece | What it is | Question it answers |
|---|---|---|
| **A0** arrival | 6 × 6 m vestibule, 3.5 m ceiling, sealed airlock door | Quiet arrival convention |
| **C1–C5** corridors | P1 (signature) and P2 (secondary), ribs on the 4 m beat | Straight modules in both profiles |
| **J1** hub | 14 m octagon (3.5 m clips), 5 m ceiling with haunch, four bulkhead ports | **Replaces the T and the 4-way.** Corridors plug into a small room through bulkheads, so no jamb voids, and it reads as a pressure hub |
| **T1 / T2** turns | 90° as two 45° mitres with a short diagonal leg (the approved V4 rule), in P1 and in P2 | Does a trapezoid mitre cleanly on the bisector? |
| **S1** stair | P2 corridor, 2 m landing + 12 risers × 0.25 m on 0.5 m treads + 2 m landing, rising 3 m | Stairs in the kit. The top landing looks into the hall |
| **H1** hall | 24 × 32 m **knee-wall nave**: vertical walls to 6 m, slopes to a 16 m-wide ceiling at 10 m, portal-frame ribs every 8 m. Catwalk at +3 m round the south and east walls, an edge stair down on the east wall, two warm machinery islands with 4 m clear round them | Hall scale; a room that is a height transition |
| **R1** control room | 10 m octagon, office-height 3.5 m ceiling, floor +0.25 m (a threshold step), window onto Mars | Small scale, personnel door, threshold step |
| **D1** debris | A fallen rib and panels across the north side of C3, over 4 m. A **2.4 m lane** stays clear | Walk-around interrupter. The lane is wide enough for a large bug |
| **X1** collapse | 3 m of C4 collapsed to a **2.0 × 1.4 m** gap | Crouch interrupter: a standing player (1.8 m) is blocked, crouched (1.1 m) passes. **The larger bugs (1.9 m) cannot follow** |
| **Doors** | The existing wide door (3.0 × 3.16 m) at the hall and personnel door (2.0 × 2.46 m) at R1, set in bulkheads | Door modules inside the kit's frames |
| **Hatches** | Sealed reservations: ceiling in P1 (only 3 m wide), wall on P2's knee wall, floor in the hall, ceiling in the hub | Where hatches fit in angled shells (D2) |

## Style

**Looks:**
- **steel:** arrival, hub, east branch
- **concrete:** north branch, hall shell
- **warm:** west branch, R1, hall machinery

**Lighting:**
- **Corridors:** the standard ceiling edges plus wall lights.
- **Interrupters carry the damage:** D1 gets a flicker with sparks and a dead
  bay; X1 is dead under a red emergency beacon.
- **Hall:** high-bay fittings on the portal frames and floor strips along the
  catwalk edge.
- **Presentation:** subtle.

## Validation: one validator, driven by markers

Validation is by **marker entities in the map** instead of per-map scripts. A
small Red Breach FGD adds point classes that you can move in TrenchBroom:

- `rb_route`: ordered waypoints with a posture (stand or crouch). Routes are
  walked forward and back, and stairs are climbed and descended.
- `rb_probe`: clearance checks: standing clear, crouch-only (standing must be
  blocked here), minimum headroom, sealed.
- `rb_nav`: bug navigation pairs. **Must connect:** hub to hall floor, round
  D1. **Must fail:** through X1 for the 1.9 m agent. **Must climb:** S1.

One `validate_markers.gd` reads them from any built scene. The kit lab is its
first user; later levels get it for free. It also checks brush count against
collision count and that no surface falls back to a default texture.

## Bugs (technical, not fight design)

- Navigation is baked for the lab, as in the combat gym.
- A lab key releases a melee bug or a spitter near the player, to watch them
  chase through trapezoids, round debris and up stairs, and to see shots and
  splatter on sloped walls.
- Fight design stays with the combat log.

## Build order and time log

1. Red Breach FGD and the marker validator.
2. Corridors, hub and turns.
3. Stair and hall.
4. R1, D1 and X1.
5. Doors, lighting and navigation.
6. Captures and the kit sheet.

Authoring time is logged per step for E1. The handoff test (E2) follows: you
edit one piece in TrenchBroom and we rebuild.

## Decisions for the user

1. **Hub instead of T and 4-way junctions.** Corridors meet at octagonal hubs
   through bulkheads. *Recommendation: yes. It sidesteps the jamb-void problem
   from the corridor lab and gives each junction a place.*
2. **The hall as a knee-wall nave (P2 scaled up).** *Recommendation: P2.
   Vertical walls to 6 m carry a catwalk; a scaled P1 would lean over it.* The
   signature P1 stays the corridor.
3. **A crouch passage that the larger bugs cannot follow.** *Recommendation:
   keep it as a design tool, for escape routes and shortcuts where only small
   bugs can pursue.*
4. **Anything to add or drop?** Examples: a vent crawl, reusing the Phase 1
   machine room as the medium room, a second window.
