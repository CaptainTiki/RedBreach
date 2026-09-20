# Gym playtest 01: movement and scale

## User findings

- All three doorways are passable. The 1.0 m opening feels very snug; 1.5 m and 2.0 m feel better. Favor the wider options when planning normal circulation; retain 1.0 m as the tight-clearance test.
- Stairs originally pushed the camera upward instantly at each riser and felt jarring.
- The ramp also felt jittery.
- All three stationary targets are easy to hit and correctly register hits. This validates hit detection, not combat difficulty.
- The 0.75 m cover can be jumped over. The 1.25 m cover cannot be reached directly from the floor, but can be reached from the 0.75 m cover.

## Response

Keep the gym geometry, doorway sizes, targets, and jump tuning. At a 5.5 m/s jump impulse and 16 m/s squared gravity, the idealized jump rise is about 0.95 m; the cover behavior fits that tuning. There is no mantle mechanic.

Fix movement presentation:

- The stair helper now rejects walkable slope contacts and requires a nearly level tread. Previously it repeatedly lifted the body off the ramp.
- Slopes use CharacterBody3D sliding and floor snapping with constant floor speed.
- The camera uses independent world-space position interpolation between physics snapshots. Mouse look stays immediate.
- Discrete stair rises and large downward floor snaps produce a temporary eye offset that settles exponentially. Normal jump arcs are preserved.
- `Stair Camera Smoothing` on GymPlayer controls the catch-up rate, initially 14 per second. Lower values soften the climb with more lag; higher values catch up faster.
- Reset/respawn clears the camera history immediately.

## Evidence

At a fixed 120 rendered updates per second / 60 physics ticks:

- Before: stair camera jumps reached 0.251 m in one frame. After: maximum upward stair camera movement was about 0.035 m per frame.
- Before: ramp view repeatedly rose about 0.112 m and dropped about 0.009 m, with frequent loss of floor contact. After: ramp interior remained grounded, with a steady approximately 0.013 m rise per rendered frame and no downward oscillation during ascent.
- Added motion checks cover uphill/downhill contact, camera updates between physics ticks, stair ascent/descent, eye lag, and resetting camera history.
- Added hit checks for all three target plates.

Run `tools/rebuild-gym.ps1 -Validate` for the full baseline and motion checks. Logs remain under `RedBreach/.godot/`.

Next playtest: stop the running game and press F5 again, then walk and sprint up/down both the stairs and ramp. The remaining question is whether the chosen smoothing feels comfortable, not just whether traversal succeeds.

Reference: [Godot manual camera interpolation](https://docs.godotengine.org/en/stable/tutorials/physics/interpolation/advanced_physics_interpolation.html).

Validation after the movement fix: 30 baseline gym checks and 12 rendered motion/input checks passed (42 total). The 11 motion checks that do not require mouse capture also passed headlessly. Ramp ascent/descent stayed grounded; the rendered test confirmed immediate mouse aiming. No movement or target settings were increased. No commit was made; project version is still 0.0.001.
