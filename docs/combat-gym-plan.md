# Combat Gym 01 spatial plan

Status: approved by the user on 2026-09-19. Built as a separate map and scene; see [implementation and playtest notes](combat-gym.md).

See [top-down plan](combat-gym-plan.svg). Separate scene and source map; the movement gym remains available. North is Godot -Z; all positions are in metres, floor Y=0.

| Space | X bounds | Z bounds | Purpose |
|---|---|---|---|
| Precision range | -8 to 8 | -34 to 4 | 10/20/30 m shooting from individual marked pads at Z=0; 12 m strafe strip |
| Safe staging | -8 to 30 | 4 to 10 | Spawn (4,0,7), refill supplies, no live enemy |
| Entry corridor | 18 to 22 | 0 to 4 | Four-metre gate separating combat from staging |
| Encounter arena | 10 to 30 | -20 to 0 | One bug, cover, pickups, start panel |

Range plates: X=-4/Z=-10, X=0/Z=-20, X=4/Z=-30. Widths 0.8/0.6/0.4 m encourage accurate shots at progressively smaller apparent targets. Each distance is measured from its own pad directly south at the same X. Cover at X=-7..-5, Z=-3..-2, height 1.1 m, supports crouch and muzzle-obstruction comparisons without blocking the pads.

Arena: bug spawn (20,0,-16), entry position (20,0,-2), E start panel (23,1,-2). Tall cover X=18..22/Z=-12..-10, height 2.2 m breaks line of sight; low cover X=12..15/Z=-5..-4, height 1.1 m tests crouched exposure. Health pickup near (14,0,-15), ammo near (27,0,-6); staging holds both supplies too. Clear paths on both sides of tall cover support navigation and kiting.

Story beat: quarantine test bay, first contact, bug pursuit and a readable wind-up/lunge, then containment cleared. No keys/objective chain yet. The start panel closes the entry gate only with the player fully inside, releases one bug, and reopens after the kill or death. Killing the bug does not immediately respawn it. Use Backspace for a fresh attempt with restored resources and clean effects.

First-pass scope: health/damage/death/reset; health and ammo pickups; editable StateChart-driven bug; obstacle navigation and line-of-sight attacks; hitscan hit-position feedback; green hit bursts, death burst, floor/wall splatters and a corpse. Primitive bug/model/effects are deliberate prototypes. Per-weapon resources stay deferred.

Acceptance: saved TrenchBroom source builds repeatedly; range hits at all three distances; walls stop shots, detection and attacks; bug navigates either side of cover; lunge can be dodged; death disables player fire/movement; pickups apply only when useful; reset clears every encounter state and effect; original movement/door/pistol tests still pass.

Spitter extension: a second authored release panel at (26,1,-2) selects the larger ranged enemy at the existing spawn. One enemy per attempt remains the rule. No source brushes, cover positions, routes or dimensions change; navigation clearance is enlarged for this body. See [spitter notes](spitter.md).
