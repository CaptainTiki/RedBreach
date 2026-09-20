# Pistol: first firing test

Status: built and validated; ready for user playtesting. Included in local version `0.0.004` (Weapons). The user selected a pistol as the first weapon, including the previously agreed ADS behavior. This pass uses the target lane from the approved [original gym plan](gym-plan.svg); no new room or source-map edit is needed.

## Existing test layout

The original firing line is at Z = 6. Target centers are (6, 1.4, -1), (7.6, 1.4, -5), and (9.2, 1.4, -9), giving longitudinal depths of 7, 11, and 15 m. Stand in line with each target to compare hip fire and ADS. The annex's 1 m cover and target remain available for the standing/crouched shot-obstruction comparison. Backspace returns to the original spawn and replenishes the test supplies.

## Initial tuning

| Property | Starting value |
|---|---|
| Fire mode | Semi-automatic; one shot per left-click press |
| Damage / range | 25 damage / 50 m |
| Rate limit | 4 shots per second |
| Magazine / reserve | 12 rounds / 60 rounds |
| Reload | 1.4 seconds, preserving remaining ammunition |
| ADS | Hold right mouse; 80 to 70 degree FOV over 0.18 seconds |
| ADS movement | 60% of the current posture's base speed; sprint cannot override it |
| ADS recoil | 50% of hip-fire camera kick and aim drift |
| Targets | 100 HP; four hits to down; recover after 2 seconds |

Controls: left click fires, right mouse aims, R reloads, and Backspace resets the gym. E still uses switches; Escape releases the mouse. The first click after releasing the mouse recaptures it without firing.

The pistol is an editable blockout model with iron sights, slide movement, muzzle flash, procedural test audio, ammo display, and hit feedback. Handling and aiming use editable StateCharts. ADS/recoil values are exposed on the pistol scene for this prototype; the per-weapon resource refactor remains deferred under [FR-001](future-refinements.md#fr-001-per-weapon-configuration-resources).

This pass establishes the pistol and damageable test plates. Player damage/death, pickups, enemy behavior, and the expanded combat-area layout remain subsequent Combat Gym work.

## Validation and playtest

`tools/rebuild-gym.ps1 -Validate` passed all 220 checks: 30 baseline gym, 22 movement, 32 door, 58 annex, 32 alteration, and 46 pistol checks. The pistol's 46 checks also passed using Forward+ / D3D12, including front/rear iron-sight alignment against the actual viewport. The separate rendered movement checks passed, including immediate mouse aim. Hip-fire, ADS, and reload captures were rendered and inspected.

Checks cover actual fire input, rate limiting, no automatic repeat while held, target damage/recovery, full/partial/empty magazines and reserves, reload timing and interruptions, standing/crouched ADS speeds, sprint restoration, recoil reduction/recovery, all three target depths, cover and muzzle obstruction, mouse recapture, runway measurement cancellation, and gym reset. The source map is unchanged by the pistol pass; it retains the previously tested two-block relocation.

For a fresh playtest, press F5 and use the original three target plates. Compare hip-fire clicks with aimed clicks, fire quickly to judge recoil, empty the magazine, and reload both full and partial magazines. Try strafing and crouching while aiming, then compare shots over the annex cover. Backspace refills the test pistol and resets targets.

The blockout model, sounds, and timings are placeholders for judging handling. Audio files are procedurally generated local WAVs, with no external asset dependency. The renderer/test tools mute audio while checking behavior; the game enables it for the user's feel test.

Implementation: `RedBreach/weapons/gym_pistol.tscn` / `.gd`, `RedBreach/gym/target.gd`, and the existing player controller. Handling has Ready/Reloading states; aiming has Hip/ADS states. A partial reload preserves ammunition, and releasing the mouse prevents aiming. The muzzle is checked for nearby obstruction even when the camera can see the target.

Evidence remains under ignored `RedBreach/.godot/`: `pistol_qa.log`, `pistol_rendered_qa.log`, `motion_rendered_pistol.log`, `pistol_capture.log`, and `pistol_hip.png`, `pistol_ads.png`, `pistol_reload.png`.
