# Combat Gym: scope and firing tests

Status: the first pistol, reload, ADS, recoil, and damageable targets are built and validated in the existing approved target lane. The larger Combat Gym remains a planning brief and needs its top-down spatial plan before new geometry is built. See [pistol test notes](pistol-gym.md).

## Proposed build order

1. Built, ready for user playtest: one semi-automatic hitscan pistol, magazine/reserve ammunition, reload, firing feedback, targets with health, and hip-fire/ADS comparison tests. See [pistol notes](pistol-gym.md).
2. Player survival: incoming damage, health/ammo pickups, death, and reset.
3. Repeatable encounter: one enemy using StateCharts for detection, approach, attack, and death, with cover for sightline tests.

The spatial plan should mark firing positions, near/mid/far targets, a lateral movement strip, cover, pickups, the encounter space, and safe reset positions. Story beats and level progression follow once this loop is proven.

## Requested ADS behavior

- Narrow the camera FOV slightly while aiming.
- Bring the weapon sights onto the center of the screen, using a smooth transition from the hip-fire pose.
- Slow player movement while aiming.
- Reduce camera kick and recoil-induced aim drift compared with hip fire.

Treat camera kick and accumulated aim drift as separate tuning controls. The sight/reticle must represent the actual shot direction throughout recoil and ADS transitions. A visual reticle movement alone must not pretend that the aim changed; recoil changes to actual aim must affect subsequent shots consistently.

Future consolidation of ADS and normal weapon stats into per-weapon resources is recorded in [Future Refinements, FR-001](future-refinements.md#fr-001-per-weapon-configuration-resources). That refactor is deferred until weapon refinement.

## Starting values to playtest

These are proposed initial settings, not fixed requirements. The current movement camera has an 80-degree FOV, standing walk speed is 5 m/s, and crouch speed is 2.5 m/s.

| Setting | Hip fire | ADS proposal |
|---|---|---|
| Input | Release right mouse | Hold right mouse |
| Camera FOV | 80 degrees | 70 degrees |
| Weapon pose | Lowered/offset firing pose | Sights aligned to screen center |
| Transition | Return smoothly | Approximately 0.18 seconds |
| Standing movement | 5 m/s walk | 60% of walk speed: 3 m/s |
| Crouched movement | 2.5 m/s | 60% of crouch speed: 1.5 m/s |
| Camera kick | Baseline weapon tuning | Start at 50% of hip-fire kick |
| Aim drift from recoil | Baseline weapon tuning | Start at 50% of hip-fire drift |

While ADS is active, sprint must not override the aiming speed. Apply the ADS movement multiplier to the current posture's base speed; do not repeatedly multiply an already-modified speed. Exiting ADS restores the appropriate movement mode. Keep values exposed for tuning in the gym. Use StateCharts for the relevant weapon/aim transitions, without duplicating the existing posture state machine.

## Firing comparisons and acceptance checks

- Shoot the same near, medium, and far targets from the same marked firing point in both modes. Compare single shots and repeated fire, including recovery after firing stops.
- Confirm ADS narrows FOV, centers the sights, reduces movement speed, and reduces both camera kick and actual recoil drift. ADS should retain perceptible recoil.
- Confirm shots hit where the sight indicates while stationary, strafing, crouched, entering/exiting ADS, and recovering from recoil. Check weapon/sight alignment and shot obstruction near cover.
- Check repeated ADS presses and interrupted transitions. Sprint, crouch, reload, empty ammunition, death/reset, and mouse release must not leave a stuck FOV, weapon pose, recoil offset, or speed penalty.
- Keep mouse aiming responsive while the weapon and FOV blend. Any sensitivity scaling should be explicit and tunable, and assessed separately from recoil reduction.
- Compare scoped values with measured results; preserve the existing movement, door, and alteration checks when weapon handling is implemented.

The first pistol pass is included in local version `0.0.004` (Weapons). The remaining modules are planned work; no push is included.
