# Spitter: fast ranged priority threat

Status: built and ready for playtest, included in local version `0.0.006` (Spitter). The approved arena geometry is unchanged. A second release panel selects this enemy instead of the melee bug.

## Play

Press F2 during play to open the Combat Gym, then enter the arena, approach the orange **E / SPITTER** panel on the right, and press E. The green **E / MELEE BUG** panel remains available. Only one enemy is active in an attempt. Backspace clears the encounter and lets you choose again.

The larger bug moves around cover until it can fire. Its jaws open over about 0.08 seconds, exposing a bright yellow-green throat during a **0.5-second charge**. It tracks you throughout the charge, fires at your position at release, and then closes its mouth after a short 0.1-second spit animation. The projectile has no homing and no predictive lead.

The user requested fairly fast spit that is only just dodgeable, with the intent that these enemies should be killed quickly. **35 m/s** is the initial speed: roughly 0.29 seconds over 10 metres. A straight approach is punished; a prompt sidestep or cover can save you. Judge this in play before lowering the speed. The exposed mouth rewards taking the quick shot: **two clean pistol mouth hits kill before the first spit** if landed during that first charge.

| Setting | Starting value |
|---|---|
| Health | 150 |
| Body / closed-mouth hit | 25 pistol damage; six hits to kill |
| Exposed front mouth | 3x damage; 75 per pistol hit; two hits to kill |
| Wind-up | 0.5 s |
| Spit speed / damage | 35 m/s / 20 |
| Attack range | 15 m from body origin |
| Recovery after spit animation | 1.25 s |
| Movement | 2.5 m/s |
| Physical body | Capsule, 0.75 m radius and 1.85 m height |
| Navigation clearance | 1.0 m radius, 1.9 m height; shared safe clearance for both enemies |
| Projectile collision / lifetime | Swept 0.16 m sphere; expires after 3 s |

Nonlethal weak-point hits deal extra damage but do not cancel the spit. Lethal hits interrupt it. Shell, back and closed-mouth hits receive normal damage. The green throat is hidden while closed. Green blood bursts, splatters and corpse behavior are retained; spit impacts add green residue without a lingering damage pool. Completing or failing this gym attempt clears already-fired globs, so there are no delayed hits after the result.

## Editable ownership

- `RedBreach/combat/gym_spitter.tscn`: enlarged editable primitive model, jaw pieces, glowing throat, separate body/mouth shot areas, sounds and StateChart.
- `gym_spitter.gd` extends the existing melee bug foundation for health, hit/death effects, navigation setup and reset. Its own chart follows Dormant -> Hunt -> Windup -> Spit -> Recover -> Hunt, with death/reset transitions.
- `spitter_mouth.gd` routes the mouth and body shot-area hits. Shot areas use layer 2. Regular world/body collision remains layer 1. The pistol compares the nearest solid hit with the nearest shot-area hit, preserving wall/muzzle obstruction while ignoring ordinary Area3D triggers.
- Hit areas remain outside the deforming Visual root. The mouth area follows the actual throat position; physics shapes are not flattened with the corpse. Extended legs remain cosmetic, while the larger body receives shots through an additional capsule hit area.
- `spit_projectile.tscn` / `.gd` uses swept CharacterBody3D collision instead of a point-position overlap. The shooter is excluded. No gravity/homing is applied; walls and player bodies stop the glob.
- `combat_gym.gd` selects one enemy, parks the other without collision, and clears projectiles on reset, death, completion and scene exit. `SpitterPanel` is at (26,1,-2), beside the existing panel (23,1,-2); the spawn remains (20,0.05,-16).
- Map source remains `maps/combat_01.map`. Navigation is rebaked from the same geometry with the larger clearance; the current bake has 27 polygons. Use `tools/rebuild-combat-gym.ps1 -Validate` after geometry/navigation changes; it now includes the spitter suite.

## Verification and playtest focus

45 spitter checks exercise the second panel, single-enemy selection, opening/glow/timing, actual pistol weak-point shots, two-shot interruption, six-shot body kill, shell/rear/closed-mouth handling, source cover, navigation, release-time tracking, fixed fast flight, player hit, timed sidestep, thin-wall collision, bounded lifetime, and reset/death/scene-switch cleanup. All 45 spitter checks passed both headlessly and in the rendered Forward+ game. The original 62 combat and 220 movement/door/pistol checks also passed, for 327 checks across the suites. Rendered captures cover closed/open mouth, impact, projectile, death and both panels.

Try taking the mouth shot under pressure, strafing after release, reloading during recovery, and breaking line of sight at the last moment. The model, audio and effects are prototype assets; tune pressure and readability before refining presentation.
