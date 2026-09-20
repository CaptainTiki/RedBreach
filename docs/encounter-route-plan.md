# Encounter route test / revision 04

Status: top-down layout approved by the user and built; see [playtest instructions and measurements](encounter-route-test.md). This is a timing experiment, not level one.

## Question and fixed controls

How long do fights take, how much time separates them, and how much does combat add to a fixed route? Preserve the current player and pistol tuning: walk 5 m/s, sprint 8 m/s, crouch 2.5 m/s, standing ADS 3 m/s; pistol 25 damage, maximum 4 shots/s, 12-round magazine and 1.4 s reload. The marked centreline from start (0,6) via (0,-38), (18,-38), (18,-31), (30,-31) to finish (30,2) is 114 m: ideal uninterrupted walk 22.8 s or sprint 14.25 s. These are geometric baselines, not predictions of actual play time; turning, aiming, detours, and pauses are measured.

## Current route (Godot X/Z metres; north is -Z)

| Zone | Bounds X / Z | Encounter |
|---|---|---|
| Start bay | -4..4 / 0..12 | Spawn (0,9); timed start line Z=6 |
| A: occupied room | -6..6 / -12..0 | Two preplaced small bugs |
| B: vent hall | -3..3 / -24..-12 | Cross Z=-14: grate bursts, one small bug emerges ahead |
| C: occupied room | -6..6 / -40..-24 | One preplaced spitter; tall cover; turn east |
| Bent connector | Upper: X6..20/Z-40..-36; leg: X16..20/Z-36..-29; entry: X20..22/Z-33..-29 | Trigger at X14 before D sightline; rear hatch at (10,-41.7); optional +25 health / +24 ammo |
| D: occupied room | 22..38 / -40..-24 | Two small bugs, two regular bugs and one spitter preplaced deeper in the eastern half; one further small from the rear hatch; two cover blocks |
| E: vent hall | 27..33 / -24..-8 | Cross Z=-22: grate bursts, two small bugs emerge ahead, staggered |
| Finish bay | 24..36 / -8..4 | Finish line Z=2; results |

Original room openings are 6 m wide; the revised C-to-D connector and final entry are 4 m clear, with open-top walls 4 m high. Vent mouths are 2.4 m wide, near floor level, in shallow side recesses. Spawn markers remain navigable and at least 2 m apart. The route includes an offset connector ending in a left turn into D; no keys, locked gates, jump requirements, story tasks, or forced arena doors. A few cover blocks break shots and provide decisions; the first pass stays compact.

## Reusable encounters

Each encounter owns an editable StateChart (armed, waiting for burst, introducing, fighting, cleared, cancelled), trigger volume, enemy scenes/markers and optional vent. Room enemies exist before approach and wake on sight or being shot. D is a mixed encounter: crossing its pre-sightline trigger activates the front five and commits the rear sequence, bursting after 1.75 s and emerging after a further 0.35 s. The pending sixth blocks clearing until it is spawned and killed; a 3 m separation prevents point-blank rear spawns. See [the detailed rear-hatch plan](rear-hatch-plan.md) for coordinates and verification. Crossing a hall trigger starts a one-shot vent cue, throws the grate clear, then releases one or two enemies. No invisible blocking grate debris; prevent spawning inside the player or another body and retry if occupied. Re-entry must not duplicate enemies. Reset restores grates, enemies, triggers, health, ammo, pickups and effects. Death stops the run and cancels pending spawns.

## Measurement contract

- F3 opens the route trial; F4 switches empty-route/combat mode and resets. Backspace repeats the chosen mode. F1/F2 retain the existing gyms.
- Start and finish are spatial triggers. End records complete, bypassed encounters, or death; reset/scene exit during a run records an aborted attempt.
- Each encounter records trigger/alert time, first spawn, first damage, last kill, cue delay, and trigger-to-clear duration. Preplaced enemies start their encounter clock on alert or damage, not on loading the scene.
- The run records total elapsed time, horizontal distance, moving time, movement-mode time, shots, incoming damage, cleared encounters, and time with any active encounter versus time with none. Overlapping fights count once in the overall combat interval; individual encounter durations can overlap and must not be added to infer total.
- Time without an active encounter includes pauses and pickups; it is not labelled pure walking time. Empty-route runs give the useful travel baseline. No automatic deduction of an unrelated best baseline from another run.
- Results stay visible and append to local CSV files under Godot user data. Include version, route revision, mode, encounter counts and current tuning so results from different setups can be distinguished. Report export failure visibly; no fabricated timings.

## Playtest order

1. Empty route walking, then sprinting: learn the route and record traversal.
2. Combat route at a natural pace; repeat at least three times, inspecting each encounter split and quiet interval.
3. Try pushing past a fight: record overlapping pressure and distinguish a bypass from a complete clear.
4. Move one trigger or change one enemy count, increment route revision, repeat. For this revision both the connector geometry and spawn timing changed, so establish a fresh empty baseline and keep earlier results separate.

We are gathering evidence, not promising a 5-10 minute level. Art, enemy animation polish, patrol/search, and weapon-resource consolidation remain deferred.
