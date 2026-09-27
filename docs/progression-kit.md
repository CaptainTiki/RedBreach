# Progression kit

Reusable doors, switches, cards and moving set-pieces for any level, placed as map entities so they live in their
room's TrenchBroom group and move with it. Built for freight v2 (G-02). The scripts are in `RedBreach/interaction/`.

## The pieces

| Entity | What it is | Behaviour |
|---|---|---|
| `rb_door` (`door_kit.tscn`) | A door of any size. `rise`: one leaf lifts into the wall. `slide`: two leaves part (gates in fences). | StateChart: Closed, Opening, Open, Closing, Blocked, plus a reset from anywhere. |
| `rb_switch` (`switch_kit.gd`) | A wall panel or a console post with a handle and a lamp. | Sends events, sets flags, or only sparks. |
| `rb_pickup` (`pickup_kit.gd`) | A glowing card on a plinth. | E takes it and sets its flag. |
| `rb_fan` (`fan_kit.tscn`) | Blades in a round wall hole. | StateChart: Running, SpinningDown, Stopped. Solid while turning; at rest one blade points up. |
| `rb_drawbridge` (`drawbridge_kit.tscn`) | A hinged catwalk section with rails. | StateChart: Raised, Lowering, Lowered. |

A level holds one `Progression` node (`progression.gd`). It keeps the flags (cards taken, power) and fires events
(switches, levers), and every kit piece finds it by group. A `start` event fires a second after the level starts or
resets, which opens the arrival airlock. Backspace calls the level's `reset_encounter()`, which calls
`Progression.reset()`: doors shut, cards go back, switches go up, the fan runs and the section rises.

## A door's rule

| Property | Values |
|---|---|
| `opens` | `use`: E from either side. `side`: E only from the side `side` points to (a release). `event`: only a switch or lever. `start`: opens when the level is ready. |
| `needs` | Flags, e.g. `K,P`. `needs_text` names them for the prompt: "Needs the freight clearance card and power". |
| `latch` | 1: once open it stays open. |
| `events` | The events that open it (default: its id). |

There are no labels (a user rule). A lamp over each face shows the state:
- **red** while the door will not open for anyone who could reach it now
- **amber** while it is closed and usable
- **green** when open

The only words are the interaction prompt at the crosshair, such as "E  Open" or "Locked from this side".

## Checking a level with progression

The marker validator (`validate_markers.gd`) sees the `Progression` node and walks each route as a player would:
1. It resets the level before each route.
2. It waits for the start event.
3. On arriving at a route marker, it uses the kit pieces the marker's `use` names (for example `K` or `SW2,SW3`). It
   first checks that each piece is within reach, then calls exactly what the player's E calls.
4. It waits until nothing is moving.
5. It checks that the level reports finished at the route's end.

Probes:
- `refuse`: at level start, the kit piece `id` must refuse a player standing on the probe.
- `blocked_crouch`: at level start, a crouching player must not fit on the probe (the fan's closed hole).

Build notes:
- A kit piece's runtime parts are never saved in the scene; the build saves only the entity.
- Its collision is ignored while the navigation is baked, so bugs path through doorways.
- Moving parts use `sync_to_physics = false`, as the gym door does. Otherwise the collision stays behind while the
  mesh moves.

## Freight v2's progression

The plan owns all of it (`tools/freight_v2.py`: `DOOR_RULES`, `KIT_SWITCHES`, `KIT_PICKUPS`, `KIT_FAN`,
`KIT_DRAWBRIDGE`, `ROUTE_ACTIONS`, `REFUSALS`), and `check()` verifies it:
- every rule names a door
- every event has a listener
- every flag a door needs is set by something
- every action is on a route
- every route ends in the lift

| Piece | Rule |
|---|---|
| Airlock door | Opens when the level is ready. |
| Logistics west door | Ordinary door. |
| Cage gate | The archive lever (RELEASE) opens it. |
| S1 | From Logistics, with K. |
| S2 | From the east lobby, with M. |
| Quarantine hold | From the lobby, with M. |
| Substation grill | Slides open from either side. |
| Vent grille | From the vent side (the drop is one way). |
| Door 1 | Switch 3 opens it. |
| Door 5 | Switch 2 opens it (a distant clunk). |
| Door 3 | From the stair corridor side only. |
| Lift gate | From the dock, with K and P. The finish is inside the lift. |

- **Switches:**
  - pipe bay switch 1 sparks
  - switch 2 opens door 5
  - switch 3 opens door 1
  - the archive lever opens the cage
  - the cage switch lowers the catwalk section
  - P restores power
  - the fan lever stops the fan
- **Cards:** K in the supervisor cage, M in the gantry booth.

Two geometry changes came with it:
- **The lift cage is walk-in.** It has a fence with a 3 × 3.2 m gate, and the level finishes inside it.
- **Logistics has a 9.5 m ceiling pocket** over the catwalk section, which stands 4.75 m tall on its hinge.
