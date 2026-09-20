# Gym playtest 02: door confirmation and stair descent

## Confirmed by the user

- The door refuses to close when the player occupies the threshold.
- Entering during closing interrupts closure.
- Both switches control the same door: open on one side, close on the other.
- The ramp fix feels good and stair ascent is working well.
- Descending stairs still skips between treads, as horizontal movement outruns the fall.
- The gym/controller baseline was committed as `0.0.001` (`ca1e179`, Gym and Character Controller). The stair-helper commit advances this to `0.0.002`.

## Descent fix

Keep the existing capsule and native `floor_snap_length = 0.35`. Native floor snapping already handles the ramp. At certain stair corners, the capsule's rounded bottom reports a contact steeper than the floor-angle limit; native snapping then loses floor contact. A longer snap is not a substitute for a valid floor contact.

The user selected a small stair-contact helper after comparing the options with a smooth collision ramp over the stairs.

- Only try a downward step if movement started supported, no jump is in progress, and the ascent helper did not lift the player this tick.
- Require a nearly horizontal tread directly below, within the existing 0.30 m step height.
- Sweep the entire capsule down to collision, then let Godot apply its native floor snap.
- Remember that verified stair support for the next tick, so gravity and jumping remain consistent while crossing the rounded corner. Recheck support each tick and clear it on reset.
- Preserve the existing camera smoothing, capsule dimensions, slope limits, speeds, jump impulse, and gravity.

For gameplay ground checks, use the controller's `is_grounded()`. Godot's `is_on_floor()` alone can be false at the verified stair corners. Validation logs report both native floor contact (`airborne`) and controller support (`unsupported`), rather than hiding that distinction.

Reference: [Godot CharacterBody3D floor snapping and collision normals](https://docs.godotengine.org/en/stable/classes/class_characterbody3d.html).

## Validation

At 60 Hz physics and 120 rendered updates per second:

- Before: 74 of 84 sampled stair-descent frames lacked native floor contact, producing long unsupported falls over multiple treads.
- After: all 84 descent samples have verified support. Fourteen samples cross rounded corners using the helper; native floor contact handles the remainder.
- Walking and sprinting both retain support across six starting offsets, exercising different alignments with the stair corners.
- Walking descent's largest camera drop decreased from about 0.044 m to 0.027 m per rendered update; sprint descent remains below 0.050 m.
- Jumping directly from a corner immediately leaves support and retains its full rise. Landing works normally.
- Walking off the 2 m landing releases support and falls under gravity instead of snapping down.
- Ramp contact, stair ascent, reset, door interactions, hit targets, and source-map rebuild checks pass.

Run `tools/rebuild-gym.ps1 -Validate`. This pass runs 30 baseline gym checks, 22 motion checks, and 32 door checks. All 84 checks passed. A Forward+ / D3D12 motion run passed all 23 checks, including immediate mouse look, for 85 distinct checks total. No script errors were reported. The rebuild matched the saved geometry and authored nodes exactly after normalizing generated IDs; the original IDs were retained to avoid unrelated scene changes.

Stop the running game and press F5 again. Walk and sprint down the full staircase, jump partway down, and walk off the back of the landing. Subjective descent feel still needs the user's playtest.

This change is recorded as version `0.0.002`, with commit subject `Stair Helper` and no description. The commit stays local; no push was requested.
