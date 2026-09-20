# Gym playtest 03: movement annex

Status: built and validated on 2026-09-19; the user subsequently accepted the gym playtest. The [alteration follow-up](gym-alteration-plan.md) records the requested high-jump relocation. The notes below describe the Movement Gym implementation before that move. Built from local commit `104fae9` (Stair Helper), version `0.0.002`. Saved as version `0.0.003` in the local Movement Gym commit, with no push.

## Built from the approved plan

The [west annex plan](gym-movement-plan.md) is implemented: four horizontal jump gaps, a measured runway, three crouch clearances, and a cover/probe target. Enter through the new west opening beside the original spawn. The original 0.75/1.25 m high-jump blocks remain where they were; relocating them is the next deliberate alteration exercise after this annex is tested.

Geometry lives in `RedBreach/maps/gym_01.map` and is baked into `RedBreach/gym/gym.tscn`. The map now has 69 convex brushes. Of the original 26 brushes, 25 remain unchanged; the west wall became two segments around the connector. All existing gym stations retain their positions.

`RedBreach/gym/movement_annex.tscn` contains editable station origins, reset points, markings, signs, and the cover target outside the generated Geometry subtree. The annex uses plain Kenney grids at 0.25 m fine-grid scale.

## Controls and station behavior

- Hold Ctrl to crouch: body height 1.10 m, eye height 0.95 m, speed 2.5 m/s. Feet stay fixed and the camera lowers smoothly. Shift does not override crouch speed.
- Release Ctrl to stand when the full standing capsule has clearance. Under a roof, remain crouched and stand automatically on exit. Space from crouch stands and jumps only when there is headroom. Posture changes happen on the ground.
- Jump lanes have 2/3/4/5 m gaps and 8 m approaches. A scored attempt requires a jump from the approach onto the matching pad; the readout shows takeoff mode and forward travel. A pit miss returns to the same lane with velocity/camera history reset. R still returns to the main spawn.
- Walk or sprint north along the 20 m runway. It keeps separate session best times. Side entry does not start timing; changing mode, jumping, crouching, leaving the lane, or reversing cancels the run. Return to the approach to retry. Sprint remains unlimited.

Standing/crouched transitions are owned by the editable `GymPlayer/PostureChart`. Standing clearance uses a full capsule shape query against the player's collision mask, excluding the player. Reference: [Godot PhysicsDirectSpaceState3D.intersect_shape](https://docs.godotengine.org/en/stable/classes/class_physicsdirectspacestate3d.html#class-physicsdirectspacestate3d-method-intersect-shape).

## Automated results

The combined `tools/rebuild-gym.ps1 -Validate` run passed: 30 baseline gym checks, 22 movement checks, 32 door checks, and 58 annex checks (142 total; zero failures). This includes saved collision, repeated builds, and the existing edited-source build/save/reload test. A separate rendered movement run passed 23 checks, including immediate mouse aim. Forward+ / D3D12 captures of the overview, entry, jump lane, crouched tunnel, and runway finish were rendered and visually inspected.

| Measurement | Walking | Sprinting |
|---|---:|---:|
| 2 m gap | Pass | Pass |
| 3 m gap | Pass | Pass |
| 4 m gap | Miss; local recovery | Pass |
| 5 m gap | Miss; local recovery | Pass |
| Recorded forward jump travel in successful test attempts | 3.58 m | 5.73 m |
| 20 m runway | 4.00 s | 2.50 s |

Jump results use controlled takeoff positions and the current discrete controller. They establish behavior, not comfortable level-design limits. Human takeoff timing and capsule edge contact still need playtesting.

The 1.00 m tunnel blocks the crouched player. The 1.25/1.50 m tunnels permit crouched passage and prevent standing inside. Tests cover release under a roof, jumping with blocked/clear headroom, both travel directions, crouch speed, camera height, airborne posture, cover visibility/probe obstruction, crouched stair/ramp traversal, door blocking, and reset. Runway tests also cover invalid attempts and repeat arming; walking onto a jump pad does not award a jump.

Logs and screenshots remain under ignored `RedBreach/.godot/`: `annex_qa.log`, `annex_capture.log`, `motion_rendered_annex.log`, and `annex_*.png`. The expanded source has been baked by func_godot and tested in Godot; opening this expanded revision in the TrenchBroom UI remains part of the forthcoming alteration exercise.

## User playtest

1. Start a fresh game with F5. Turn left at spawn and enter the annex.
2. Try all four gaps walking and sprinting. Check takeoff readability, landing comfort, and whether misses return you to a useful retry position.
3. Run the timed strip in both modes; confirm the displayed result and retry route feel clear.
4. Hold Ctrl through the two taller tunnels. Release it inside, keep moving, and confirm standing waits until the exit. The 1 m tunnel should block you.
5. Crouch behind the 1 m cover and compare the target sightline/probe with standing. Revisit stairs, ramp, and door while crouched.
6. Record feel issues before relocating the high-jump blocks. Mark their destination on the plan, then follow the [alteration workflow](trenchbroom-workflow.md#movement-annex-and-alteration-test).
