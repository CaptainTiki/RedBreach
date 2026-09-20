# Encounter route test / revision 04

Status: built from the user-approved [top-down plan](encounter-route-plan.svg). Uncommitted on top of 0.0.006 (Spitter). This is a pacing experiment before level one. The user accepted the revision 04 rear-ambush concept; distinct ambush screeches are deferred to the audio pass in [FR-004](future-refinements.md#fr-004-distinct-bug-alert-and-ambush-audio).

## Play

F5 starts the route test; F3 returns to a fresh route from either gym. F1 retains movement and F2 retains the original Combat Gym. F4 switches between combat and empty-route modes and resets. Backspace repeats the current mode with fresh health, ammunition, pickups, enemies, vents, and timers. Escape releases the mouse but does not pause the run.

Follow the turquoise floor marks north, around the offset connector, then south. The final turn into D is left; the approach trigger is before the room sightline. Crossing the start line starts the clock; crossing the finish line ends the attempt. The finish is labelled **bypassed** if any encounter is unresolved or untriggered. There are no force-close arena doors; pushing through can overlap encounters. Death, reset, mode change and scene exit get explicit result labels, rather than looking like completed runs. A finished run stops enemies and clears projectiles; Backspace begins a fresh attempt.

| Zone | Contents |
|---|---|
| A / first room | Two small bugs already present |
| B / northbound hallway | Trigger bursts a side vent; one small bug emerges |
| C / northwest room | One preplaced spitter and tall cover |
| Connector | Optional +25 health and +24 ammo |
| D / corner + rear | Five room enemies: two smalls, two regulars and one spitter. A sixth small emerges behind from the connector hatch. Two room cover blocks remain. |
| E / southbound hallway | Trigger bursts a side vent; two small bugs emerge, staggered |

Eight bugs are preplaced and four arrive through vents: eight smalls, two regulars and two spitters overall. Preplaced groups alert on visible player within 18 m or a damaging shot after the run starts. Their first shot is not discarded. A group can notice you from the approach corridor if sightlines permit. B/E vent grates fly off immediately; first emergence follows after 0.35 s, with 0.25 s between enemies. D crosses its full-width approach trigger before room visibility: wait 1.75 s, burst the rear hatch, then wait 0.35 s for the small. Its front group activates at the trigger. Retreating without entering D does not cancel the rear sequence. The rear spawn also requires at least 3 m separation from the player. Occupied spawn markers retry rather than placing an enemy inside a body. Debris is cosmetic and cannot obstruct the player, bullets, or navigation. No vent can fire twice in one attempt.

## Revision 04: deeper front group

The user found the revision 03 front group already at the doorway when rounding the corner. The hatch was expected because the player knew the experiment, but the combined pressure felt devious. Revision 04 moves only the five front spawn markers deeper into D; see [the current coordinates and playtest record](rear-hatch-plan.md). The 114 m geometry, cover, trigger, rear small, hatch timing and all combat tuning are unchanged. The matched live walking check increases nearest-front-enemy separation at first visibility from 4.28 m to 9.70 m; first melee wind-up after that sighting changes from 0.55 s to 1.95 s when standing still. These are controlled front-response measurements, not promised human reaction time or encounter duration.

The revision 04 human playtest was accepted as sufficient for the concept: the player heard the hatch, turned to engage and could retreat from D. The supplied result was 53.88 s total, D 15.52 s, 41 shots and 20 incoming damage, with 5/5 cleared. See the [complete playtest record](rear-hatch-plan.md#revision-04-human-playtest--concept-accepted). Preserve the current setup while the distinct ambush vocal cue remains deferred.

## Revision 03 history: blind corner and rear pressure

The user could comfortably backpedal through D in revision 02. Their correction was to trigger before the room sightline, then turn left toward the fight while a delayed hatch opens behind-left. The [detailed plan](rear-hatch-plan.md) records the built geometry, timing and checks. The first implementation exposed a diagonal sightline; extending the inner wall by 2 m closed it. D keeps the same total six enemies; one small moves from the room to the rear hatch. Walking, sprinting and ADS align the cue differently, but all cross the trigger before spotting a room enemy. No room-entry requirement or repeat wave.

## Revision 02 history: enemy roles and reload pressure

The user requested a common small variant killed by any damaging hit, tougher regular melee bugs, and a mixed fight with three smalls, two regulars and one spitter. [Enemy tuning and playtest notes](bug-mix.md) record this change. In revision 02, route geometry, player speed and pistol tuning were unchanged. D has three additional spawn markers, and its northeast regular marker moves from (33, -36) to (34, -37) to clear the tall cover. Revision 01 results remain valid historical data for the original composition; do not combine them with revision 02 averages.

## What to compare

1. Press F4 for an empty route. Walk once, then repeat holding sprint. These establish your own traversal baselines, including real turning and route choices.
2. Switch to combat. Play naturally three times; compare encounter splits, quiet gaps, damage and ammunition use.
3. Try pushing forward before a fight is finished. See whether pressure carries into the next section. A bypass is a useful result, clearly labelled.
4. Change one trigger position, enemy count, or distance at a time and repeat. Keep movement and weapon tuning fixed while comparing route layouts.

The marked centreline is now 114 m, 12 m longer than revisions 01/02. With the established 5 m/s walk and 8 m/s sprint, ideal values are 22.8 and 14.25 s. Automated controller traversal measured **22.73 s walking** (113.58 m within physical trigger boundaries) and **14.23 s sprinting** (113.73 m). This verifies geometry and movement; it does not predict human combat duration. Automated combat checks use accelerated kills to verify encounter completion and must not be interpreted as playtest pacing results.

## Timers and local records

The HUD shows elapsed time, distance travelled, active/quiet time, cleared encounters, and live/final encounter splits. The final readout adds shots and incoming damage. No time estimate is fabricated from enemy count.

- A room split begins at its first alert or damaging shot; D begins at its pre-sightline approach trigger. A vent split begins at trigger activation, so its cue and stagger are included. The split ends when its last enemy dies and no spawns are pending.
- Per-encounter events include alert, first delayed spawn (vent or mixed encounter), first enemy damage and final kill. A value of -1 in CSV means the event did not occur; preplaced rooms intentionally have no first-spawn timestamp within the timed run.
- Active time is the union of all encounter intervals. Overlapping fights count once in the run total; do not add individual fight durations to estimate total combat time.
- Quiet time includes stationary pauses, reloads and pickup collection when no encounter is active. It is not pure walking time. Each quiet interval is saved separately; actual moving time and horizontal distance are also measured. Movement-mode time includes time spent stationary in that mode.
- Local files are `user://route_trials/runs.csv` and `encounters.csv`, plus `encounter_events.csv` for each start, burst, individual emergence and clear event. On this machine, Godot user data is normally `%APPDATA%/Godot/app_userdata/RedBreach/route_trials`. Run IDs connect the three files. Existing runs/encounters CSV schemas stay unchanged. Failed exports are shown on the HUD.
- Records include project version, route revision, source map/scene hashes, enemy source hashes, encounter placements/composition, trigger size, introduction type, preplaced count, burst delay, spawn separation, vent placement, encounter script hash, cue settings, and movement/weapon tuning. CSV embeds JSON for configuration, movement modes and quiet intervals. Comparisons should use matching settings. Test exports go to ignored `.godot/route_qa_exports`, separate from playtest records.

The project remains at 0.0.006 until a commit is requested. Reusing a version during local experiments is why the result also records source hashes and layout data.

## Editing and rebuilding

Geometry is `RedBreach/maps/route_01.map`, editable in TrenchBroom using the existing Valve 220 definition and 32 units/metre. Saved scene: `RedBreach/encounters/route_trial.tscn`. The map has 63 brushes and saved navigation currently has 113 polygons, using the existing 1.0 m clearance for the larger spitter. Run `tools/rebuild-route-trial.ps1 -Validate` after a geometry change; it rebuilds Geometry, bakes navigation, saves and validates the scene. Map reimport alone does not rebuild it.

`Encounters/A..E`, start/finish triggers, pickups and route marks are authored siblings of Geometry. Move those Godot nodes to match TrenchBroom edits. Each encounter instance exposes enemy scenes, spawn markers, trigger volume, introduction type, preplaced count, pre-burst delay, minimum player separation, post-burst cue delay and stagger. To add an enemy, add both a scene entry and a corresponding spawn marker with physical clearance. Increment `route_revision` for deliberate layout/composition experiments.

Reusable scenes/scripts live in `RedBreach/encounters/`: `encounter.tscn` owns an editable Armed / WaitingBurst / Introducing / Fighting / Cleared / Cancelled StateChart; `vent.tscn` owns the visual burst and original short metallic cue. The run owns a Ready / Running / Finished StateChart. Enemy behavior remains in the existing enemy charts. Shared enemy changes add opt-in sight/shot awakening and alert/damage signals; the panel-driven Combat Gym stays dormant until released.

## Validation

Revision 04 placement-only validation: all 59 enemy-mix checks, 26 rear-ambush checks and 49 route checks passed (134 total). This includes physical spawn clearance, navigation from every marker, pre-trigger sightline obstruction, retreat without room entry, complete reset and six-enemy clearing. The live reveal probe also matched in the rendered game, and its image was inspected. Geometry and materials did not change, so this placement pass does not rebuild the map or replace the earlier geometry validation.

Revision 03: the route rebuild includes 27 encounter checks, 49 route checks, 59 enemy-mix checks, 26 rear-ambush checks and 9 metric texture checks (170 headless checks). The new rear suite also runs in the rendered Forward+ game. It casts 26,100 geometry rays across C and the full pre-trigger corridor at crouch, standing and jump heights toward room-body samples: zero unobstructed rays. Actual controller movement reveals a bug only after the trigger, then retreats without entering D; the hatch still bursts and spawns once. It also verifies sprint/ADS approaches, reset during both delays, death, empty mode, pending-sixth clear prevention, proximity retry, actual navigation through the bends and event CSV export. Controlled rendered views of the hidden approach, room reveal and hatch emergence were inspected. See the rear-hatch plan for measured cue timing.

Revision 02: 43 route checks, 27 encounter checks, 59 new enemy-mix checks, 64 melee/combat checks and 45 spitter checks passed (238 total). The new 59-check mix suite also passed in the rendered game, including a real 17-hit clear with one reload. See [enemy mix verification](bug-mix.md).

Original revision 01 validation: **397 headless checks passed:** 327 existing gym checks plus 27 encounter checks and 43 route checks. All 43 route checks also passed in the rendered Forward+ game. Both route builds produced 53 brushes and 100 navigation polygons; logs contained no script errors, failures or warnings. Rendered captures were inspected, including the readable vent opening and grate release.

The route suite checks saved brush collision/navigation, real controller walk/sprint traversal, all five real trigger/alert encounters, single-instance enemies (nine in revision 01, twelve in revision 02), ordered timings, navigation through both corners and out of a vent, shots/damage, completion versus bypass/death/abort, resets during pending spawns, mode switching, CSV round-trip and visible export failure. The reusable encounter suite exercises re-entry, staggered enemies, blocked spawn retry, cancellation, preplaced wake-on-sight/shot, overlapping timers and individual quiet gaps. Existing movement, door, weapon, melee and spitter checks are also run for shared-code regressions. Rendered screenshots cover the overview, start, closed/open vent, mixed room and result readout.

Enemy art, final animation, patrol/search and per-weapon resources remain deferred. This test supplies the evidence for future level length and encounter spacing.
