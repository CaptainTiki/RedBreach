# Rear hatch test / revision 04 / deeper front group

Status: built, validated and accepted by the user as sufficient for this concept after the revision 04 playtest. Remaining ambush-audio readability work is deferred to [FR-004](future-refinements.md#fr-004-distinct-bug-alert-and-ambush-audio). The hatch belongs to D even when the player approaches and backpedals without entering the room. The earlier doorway-trigger proposal is superseded. The top-down plan was revised before changing the map; source drawing is [rear-hatch-plan.svg](rear-hatch-plan.svg).

## Spatial intent

Keep rooms C, D and E in place. Replace the straight connector with a short offset approach: east out of C, right into a short southbound leg, then **left to see D**. The full-width trigger is crossed before the room sightline. A delayed hatch then bursts behind-left relative to the player facing east into D. Backpedalling west reaches the bend's wall; retreat remains possible by changing direction through the connector. Strafe movement is still available; geometry does not force a camera rotation, while aiming at the rear threat does.

The total stays three smalls, two regulars and one spitter. Five begin in D; the small formerly at (25,-28) moves to the hatch. No wall-crawling or enemy/weapon/movement tuning changes.

## Coordinates (Godot X/Z metres)

- C and D retain their existing room bounds and cover. Close C's old east opening at Z=-35..-29; its replacement is X=6, Z=-40..-36.
- Upper approach: X=6..20, Z=-40..-36, 4 m wide.
- Southbound leg: X=16..20, Z=-36..-29, 4 m wide.
- Final connection: X=20..22, Z=-33..-29, 4 m clear. The north inner wall extends to Z=-33 to block the diagonal sightline found during validation. D retains its room bounds.
- Full-width trigger: approximately X=14, Z=-40..-36, before any damaging sightline to the room. Validate across the width, including corner hugging, rather than only at the marked centerline.
- Rear recess: X=8.5..11.5, Z=-42..-40; 3 m wide by 2 m deep. Grille at (10,1,-41.7), facing +Z; emergence at (10,0.05,-40.8).
- Supplies move with the connector: health (9,-37), ammo (12,-37). Existing amounts remain.
- Revision 04 D positions: regulars (32.5,-38), (35.5,-34.5); smalls (35.5,-38), (36,-30); spitter (36,-26.5). The front group is in the far half of the existing room. The rear small stays at (10,-40.8).
- Marked centerline: (0,6) -> (0,-38) -> (18,-38) -> (18,-31) -> (30,-31) -> (30,2). Length 114 m, 12 m more than revision 02. Geometric walk/sprint baselines are 22.8 s / 14.25 s; measure actual traversal after rebuilding.

## Sequence

Crossing the approach trigger starts D and a **1.75 s pre-burst delay**. The player continues and turns left toward the room; after that delay the rear grate breaks audibly. The small emerges **0.35 s after the burst**, preserving the existing vent presentation and visible small-bug attack wind-up. These are separate timings. Walking, sprinting, ADS or pausing can change how they line up with the reveal; the sequence never waits for the player to enter D or look in a particular direction. Immediate retreat does not cancel it.

D owns one editable StateChart and one six-enemy clear condition. Its preplaced front group and delayed rear spawn form one encounter. A waiting-for-burst state makes the delay explicit. Count pending rear enemies when deciding whether the encounter is clear. Re-entry never duplicates the wave. Clearance and at least 3 m player separation defer an occupied spawn. Reset, empty mode, death and scene exit cancel all pending work.

Record trigger/start, burst, actual emergence and clear events. Keep existing CSV schemas intact; supplementary event timing may use a separate CSV. Revision 03 isolates this experiment from revision 02 results, but both geometry and timing changed, so total-duration comparisons need the new empty traversal baseline. Project version stays 0.0.006 until a commit is requested.

## Required verification

1. Player camera cannot see a room enemy from the pre-trigger approach or C, including across the width and through corner gaps. Rebuild real collision and test standing/crouched views and body hit areas.
2. Actual movement crosses the trigger before the first room enemy can be shot. See a bug, immediately backpedal, and confirm the hatch opens/spawns without ever entering D.
3. Waiting 1.75 s precedes the burst; another 0.35 s precedes emergence. Delay persists through retreat, while cancellation clears it on reset/death/exit.
4. Five front kills cannot clear D while its sixth enemy remains pending. Six kills clear D once. The route still has five encounters and twelve enemies total.
5. All spawned bugs can navigate the new bends and rear recess. Player has room to escape, cover remains, metric Kenney textures stay aligned, and reloading/ADS/movement retain their tested values.
6. Empty walk/sprint traverse the marked 114 m route. Export burst and emergence times, with QA output separate from user playtests. Inspect the hidden approach, left reveal, rear hatch and rendered gameplay.

## Revision 03 verification history

The saved map contains 63 brushes and 113 navigation polygons. The 4 m final entry includes an extended inner wall: the initial 6 m opening allowed a diagonal shot past the bend, which the full-width ray sweep detected and the extension closed. 26,100 sample rays now find no room-body sightline from C or before capsule contact with the trigger.

In actual controller movement, a front enemy first became shootable about 1.55 s after the trigger while walking (player still X<22, outside D). Burst delay is set to 1.75 s: measured 1.767 s at 60 Hz, followed by 0.367 s to emergence for the configured 0.35 s cue. Sprint revealed the front about 1.12 s after triggering; the ADS test about 1.80 s. Slowing or stopping can make the hatch fire before the room reveal; this remains a spatially triggered sequence, not a camera-dependent script. Immediate retreat still produced one rear small and kept D active.

The 26-check rear suite passes alongside existing encounters, route traversal, real pistol/reload mix and metric Kenney validation: 170 headless checks. Repeat in the rendered game for physics/render parity; controlled rendered approach/reveal/hatch views are kept under `.godot/rear_ambush_*.png`. Human testing is still needed to judge the directional sound and pressure while aiming and reloading. Automated kills are not encounter-duration evidence.

Next playtest: F3/F5, approach D naturally, shoot from the corner and retreat without entering. Listen for the hatch behind-left, address the small, then re-engage the room. Try a second pass holding ADS on the approach. Note whether the cue was understandable and whether retreat required a useful decision. All results stay local; version is still 0.0.006.

## Revision 04 / give the room reveal breathing space

User feedback: D's front enemies were already at the opening on the reveal. The hatch was anticipated because the player knew the test, but the combined front/rear pressure felt at the devious end. Move the front enemies deeper into D and repeat. Keep all geometry, six-enemy composition, trigger, 1.75 s burst delay, 0.35 s emergence cue and enemy/weapon/movement tuning unchanged.

The five placements above are all at least 10.5 m east of D's west entry plane before activation. Enemies still wake at the approach trigger and advance during the reveal; inspect their live positions, not only dormant marker distances. Route revision becomes 04 to distinguish placement-only comparisons; project version remains 0.0.006 until a requested commit.

The supplied revision 03 screenshot reports 52.17 s total, 26.50 s active, 25.67 s quiet, 226.2 m travelled, 35 shots, 50 incoming damage and 5/5 cleared. D lasted 19.33 s; A 1.82, B 1.03, C 3.03, E 1.28 s. HUD final health was 70; incoming damage is cumulative and can differ from net health after pickups. These are one player's attempt, not controlled averages.

A matched live walking probe of revision 03 found the nearest front enemy only 4.28 m away at first sight, already just outside the room. Its first melee wind-up began 0.55 s later while the player stood still. Use that same approach to check the deeper group before the next human playtest. The probe leaves front enemies active and freezes the rear small only for measuring the front response interval; it is not encounter-duration evidence.

Revision 04 result: the same live walking approach first revealed a front bug 1.75 s after the trigger, with the nearest front enemy **9.70 m** away instead of 4.28 m. Standing at that first sighting, the earliest front melee wind-up was **1.95 s later**, instead of 0.55 s. The spitter released its first projectile after about 0.58 s in the revised setup; ranged pressure remains. Rendering and headless movement produced the same results. The player can reduce the gap by pushing forward, and lingering before the reveal lets enemies approach; the change is distance, not an enforced grace period.

All 134 applicable checks passed: 59 enemy-mix, 26 rear-ambush and 49 route checks. Spawn clearance, navigation, hidden approach, delayed rear small, pending-enemy clear condition and reset remain valid. The live reveal image is `.godot/d_reveal_revision_04.png`. No source-map, geometry, trigger, hatch or weapon/AI edits were needed. Relaunch F5 for the next natural playtest; keep revision 03 and 04 CSV results separate.

## Revision 04 human playtest / concept accepted

The user reported that the deeper front placements felt better. The hatch ting was audible, and they could turn to engage the rear bug, then backpedal away from D successfully. They consider this sufficient to prove the concept. Retain this placement and sequence; no further encounter adjustment was requested.

The remaining issue is the missing or insufficiently readable bug awareness screech. For the audio pass, the ambush tell must be distinct from normal pursuit sounds so players recognize a new, nearby danger. This is recorded in [FR-004](future-refinements.md#fr-004-distinct-bug-alert-and-ambush-audio); no sound or gameplay implementation changes accompany this note.

The supplied screenshot records build 0.0.006, 53.88 s total, 27.80 s active, 26.08 s quiet, 226.3 m travelled, 41 shots, 20 cumulative incoming damage and 5/5 encounters cleared. Splits: A 1.52 s; B 6.25 s; C 9.32 s; D 15.52 s; E 1.45 s. Final HUD health is 100 after the run. Encounter splits can overlap and must not be summed as total active time. Preserve this as an individual revision 04 attempt, not a controlled average or a target duration.
