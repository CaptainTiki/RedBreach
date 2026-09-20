# Project brief and decisions

## Agreed direction

- Title: Red Breach.
- Setting: Mars.
- Genre and style: crunchy sci-fi shooter.
- Campaign premise: aliens attack the Martian colony; the player discovers that they have been on the planet for a long time, and the campaign ultimately turns toward leaving the planet. The industrial plant is part of that setting.
- Title meaning: Red for Mars, Breach for the invasion.
- Workflow: agree on the mission walkthrough, then review a top-down spatial plan, make an enemy/pickup pass, build and playtest.
- Versioning: begin at 0.0.001 and increment the final component for every subsequent commit.

## Campaign and mission context

The agreed arc is attack on the colony, discovery of a long-established alien presence, then escape from the planet. The exact alien origin, player role, timing of the discovery and evacuation route remain open. An earlier pitch about the plant breaking into an underground site and the player being sent to contain it was provisional; it is not established canon.

The [freight-access example mission](example-mission-walkthrough.md) belongs around level 2 or 3. Players already understand movement, shooting and the general game feel. Its opening establishes location, situation and a foothold. A new alien or weapon could be introduced through play, but neither is selected yet. Do not turn this mission into the game's basic tutorial or assume that it contains the campaign's major revelation.

Aim for roughly ten minutes for a normal run by a player who knows most of the route. First-time exploration can take longer; efficient play, skipped secrets and rushed fights can finish sooner. This is a playtest target, not a forced minimum or a measured result.

Use airlocks and elevators to frame level arrivals and departures. Preserve the occupied chamber and player while closed doors conceal the level swap, with lights, sound and movement/cycling animation providing continuity. On stepping into the destination level, show its number and title as a nonblocking screen overlay and fade its alpha over about two seconds after a readable introduction. `L03 Freight Lift Repair` is an example, not a finalized number or title. Transition performance and readiness need validation when implemented.

## Initial milestone

Gym first, then the real level. The approved 2D gym plan and first playable map establish the TrenchBroom-to-Godot workflow. See first-test-plan.md and trenchbroom-workflow.md.

## Open decisions

- Player role and immediate objective.
- Alien nature and origin.
- TrenchBroom integration established: func_godot 2025.12, Valve format, 32 map units per metre (see workflow guide).
- Exact campaign ordering, mission walkthrough and spatial layout; movement/combat prototypes already supply tested starting values.
