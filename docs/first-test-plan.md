# Gym 01: plan and scope

Status: top-down plan approved by the user; first playable pass implemented.

See [the 2D plan](gym-plan.svg). This is a reusable mechanics gym. The second pass adds a switch-controlled door in the 2.0 m opening. Story beats, level progression, pickups, and enemies belong to later passes.

## Agreed first pass

- 24 x 24 m clear floor with 4 m perimeter walls and an open ceiling.
- Spawn at Godot (0, 0.05, 9), looking toward -Z.
- Movement loop: eight 0.25 m risers with 0.5 m treads, a 2 m landing, and a 1:3 ramp.
- Doorway gauges: 1.0, 1.5, and 2.0 m wide, all 2.5 m clear height.
- Cover blocks: 0.75 and 1.25 m tall.
- Three static target plates at 7, 11, and 15 m depth from the firing line. Labels are longitudinal lane depth, not diagonal shot distance.
- Player capsule: 0.6 m diameter, 1.8 m tall; eye height 1.65 m.
- Walking 5 m/s, sprinting 8 m/s, gravity 16 m/s squared, jump impulse 5.5 m/s. These are gym tuning defaults, not final Mars simulation or game design.

## Source ownership

`RedBreach/maps/gym_01.map` is the editable TrenchBroom geometry source. The map was authored from the plan before baking through func_godot.

`RedBreach/gym/gym.tscn` contains a baked, saved Geometry subtree and separately editable player, lighting, labels, and target nodes. Building Geometry replaces only its children. Keep gameplay nodes outside Geometry.

## Later modules

1. Completed: [State Charts door/switch module](gym-door-module.md) in the 2.0 m doorway.
2. Built, awaiting user playtest: [movement annex](gym-movement-plan.md) for jump distance, sprint timing, and crouch. See [implementation and test results](gym-playtest-03.md).
3. After annex playtesting, plan and perform a deliberate alteration test: relocate the existing high-jump blocks beside the long-jump lanes, rebuild, and verify old/new collision and labels.
4. Test pickups and actual weapon behavior.
5. Add a basic enemy and combat checks.
6. After gym mechanics and scale feel right, plan the first real level in 2D with story beats, encounters, routes, and items.

See [the pipeline guide](trenchbroom-workflow.md) for editing and rebuilding.
