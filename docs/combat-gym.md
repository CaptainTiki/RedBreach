# Combat Gym 01: first bug

Status: built from the user-approved [top-down layout](combat-gym-plan.svg); ready for feel testing. The first melee pass is included in local version `0.0.005` (Combat Gym). The [fast spitter extension](spitter.md) is included in local version `0.0.006` (Spitter).

## Playtest route

Open the Godot project and press F5. The combat gym is now the main scene. F1 opens the existing movement gym; F2 opens a fresh combat gym.

1. Walk ahead into the precision range. Use the turquoise 10/20/30 m pads; each pad lines up with its own plate. Compare hip fire, ADS, deliberate single shots, repeated shots, and lateral movement. Plates are 0.8/0.6/0.4 m wide and recover two seconds after being downed.
2. Return to staging and turn right to the arena entrance. Pickups in staging and inside the arena apply on contact only when useful: red health, gold ammunition.
3. Enter fully and approach the turquoise release panel on the right. Aim within 2 m and press E at the turquoise MELEE BUG panel, or use the yellow-green SPITTER panel beside it for the [larger ranged enemy](spitter.md). The gate closes and exactly one selected bug is alerted. It routes around cover toward you.
4. Look for the yellow ring and LUNGE readout. The bug pauses for 0.55 seconds, then lunges along its committed direction. Sidestep, retreat, fire, or break its line of sight. A hit deals 20 damage; you have 100 health.
5. Four body hits from the pistol kill its 100 HP. Hits spray green droplets; death produces a larger burst, surface splatters, and a flattened corpse. The gate reopens. There is no automatic replacement bug.
6. Backspace restores the safe spawn, health, ammo, targets, bug, pickups, and gate, and clears blood/effects. Death cancels firing, movement, ADS, reload and pickup collection until reset.

Controls remain WASD, Shift sprint, Ctrl crouch, Space jump, LMB semi-auto fire, RMB hold ADS, R reload, E use, Escape release mouse. The first click after Escape only recaptures the mouse. Escape releases the mouse; it does not pause the encounter.

## Starting encounter settings

| Setting | Value |
|---|---|
| Player / bug health | 100 / 100 |
| Pistol body damage | 25 |
| Bug pursuit speed | 3.3 m/s |
| Wind-up | 0.55 s |
| Lunge | 10 m/s for 0.25 s, direction locked before launch |
| Recovery | 0.85 s |
| Attack damage | 20, at most once per lunge, with line of sight |
| Health pickup | 50 in staging; 25 in arena |
| Ammo pickup | 36 in staging; 24 in arena; 60 reserve cap |
| Persistent / transient effect limits | 64 splats / 160 droplets |

Judge shot readability, time to kill, whether the wind-up is visible, how easy it is to keep distance, reload pressure, cover usability, and whether green hit/death feedback is sufficient. Weapon settings remain provisional; resource consolidation is deferred in [FR-001](future-refinements.md).

## Editable sources and state ownership

- Geometry: `RedBreach/maps/combat_01.map` (Valve 220, 32 units/metre). The approved layout has 22 brushes. Plain Kenney grids repeat at 2 m with 0.25 m subdivisions.
- Saved scene: `RedBreach/combat/combat_gym.tscn`. Gameplay, pickups, gate, labels, effects and navigation stay outside Geometry. Targets and firing pads are separate authored nodes, so move them with source geometry where needed.
- Bug: `combat/gym_bug.tscn` and `.gd`. Behavior chart: Dormant -> Hunt -> Windup -> Lunge -> Recover -> Hunt, plus Dead and reset transitions. The panel explicitly alerts the bug; this gym does not yet simulate ambient patrol or searching after losing the player. Navigation handles pursuit around geometry; line of sight gates starting an attack and applying its damage.
- Player health: `combat/player_health.tscn` and `.gd`, with Alive/Dead chart.
- Encounter chart: Ready/Fighting/Cleared/Failed. Gate closure requires the entire player to be inside the arena. Gate reopens after bug death or player death.
- Effects use the actual shot impact position and normal, raycast nearby floor/wall surfaces, and exclude player/bug bodies. Mesh splatters persist until reset or FIFO eviction at the cap. Droplets expire; neither effects nor corpses block movement/shots.
- The bug uses a body capsule for collision/damage; extended legs are visual placeholders. Meshes, movement animation, impact sounds and effects are first-pass prototypes, with no imported enemy asset pack.

## Rebuild and verification

From the repository root run `./tools/rebuild-combat-gym.ps1 -Validate`. It rebuilds Geometry from the source map, bakes navigation from the resulting static collision geometry inside the arena bounds, saves the scene, and tests the saved result, including the spitter. Use this after editing the combat map in TrenchBroom. Building Geometry alone in the inspector does not refresh navigation; run the combined command afterward.

Navigation uses Godot's [source-geometry parsing and navigation bake](https://docs.godotengine.org/en/latest/classes/class_navigationserver3d.html#class-navigationserver3d-method-parse-source-geometry-data). The shared bake now allows for the larger spitter and currently contains 27 polygons. Navigation is saved, not rebaked during play.

Validation: 62 combat checks passed, including accurate real shots in hip/ADS at all three distances, cover blocking sight and shots, pursuit around cover, a dodgeable lunge, blocked attacks, four-shot kill, persistent/bounded effects, automatic pickup collection, death/handling interruption, reset during wind-up, and F1/F2 scene switching. The original 220 movement, door, alteration and pistol checks passed. The combat source was rebuilt repeatedly and loaded from disk for validation. All 62 combat checks also passed in the rendered Forward+ game, and range/bug/hit/death captures were inspected; logs/captures live in ignored `RedBreach/.godot/combat_*`.

No combat TrenchBroom UI round trip has been performed by the agent. The map is authored directly in the same verified Valve 220 format and uses the existing game definition.
