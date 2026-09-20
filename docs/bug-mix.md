# Enemy mix / route revision 02

Status: implemented for playtesting on top of 0.0.006; uncommitted. The user requested tougher existing melee bugs, a smaller one-hit common variant, and a mixed group that tests target priority, ammunition and reloading.

## Starting values

| Enemy | Health / pistol hits | Movement and attack | Role to test |
|---|---|---|---|
| Small bug | Any positive accepted damage kills; 1 pistol hit | 55% visual size; 0.55 m capsule width / 0.605 m height; 4.5 m/s pursuit; 0.35 s wind-up; 11 m/s committed lunge for 0.16 s; 10 damage; 0.65 s recovery | Common, fragile pressure that consumes attention and individual rounds |
| Regular bug | 150 HP / 6 body hits, previously 100 HP / 4 hits | Existing 3.3 m/s pursuit, 0.55 s wind-up, 10 m/s lunge for 0.25 s, 20 damage and 0.85 s recovery | More durable advancing threat |
| Spitter | Unchanged 150 HP / 6 body hits or 2 exposed-mouth hits | Existing half-second charge and 35 m/s spit | Ranged priority target with a short weak-point opportunity |

The small variant is an inherited scene, `RedBreach/combat/gym_small_bug.tscn`, reusing the editable melee StateChart. It has its own smaller capsule and sight/attack distances; the CharacterBody root remains unit scale. Its visual scale survives death and reset. Zero/negative damage and repeat corpse hits are ignored. It does not introduce friendly fire or make decorative legs into hit targets.

## Route composition

A has two smalls. B releases one small from a vent. C keeps its single spitter. D has **three smalls, two regulars and one spitter**. E releases two smalls from a vent. This totals twelve enemies: nine preplaced and three vent spawns. The regular-only panel in F2 now releases the 150 HP regular; F3/F5 contains the mixed test.

D's best-case ammunition cost is 3 + 12 + 2 = **17 pistol hits**, or **21** using only body hits on the spitter. A full magazine holds twelve rounds, so even perfect shooting requires at least one reload. Reload remains 1.4 seconds. Small pursuit is faster than standing ADS movement (3 m/s) but slower than normal walking (5 m/s), giving the player a reason to release ADS and retreat. Misses, incomplete magazines, cover and other encounters can add pressure; this arithmetic does not establish actual difficulty or encounter duration.

All route geometry and player/weapon tuning remain unchanged. D adds three clear, navigable spawn markers and moves one regular off the edge of tall cover. The source plan reflects this. Route revision is 02, and saved configuration includes the small scene's hash; old revision 01 CSV rows are retained without rewriting their schema or results.

## Playtest questions

Repeat F3 at a natural pace. Can you read the small/regular silhouettes quickly? Does switching from a spitter mouth shot to an approaching small feel worthwhile? Does the empty magazine make you find room to retreat, or is the pack still trivial to kite? Does the small target feel satisfying to hit, especially at close range? Compare D's time, total shots and incoming damage with the earlier run; manually note reload count for now because CSV records shots but not reload events.

This experiment tests enemy roles and reload pressure before using longer levels to create duration. Health, pack composition and small movement all changed together, so revision comparisons describe the whole new mix rather than isolating the contribution of a single variable. Geometry, branches, keys and level-one construction remain separate decisions.

## Verification

**238 headless gameplay checks passed:** 64 melee/combat, 45 spitter, 27 reusable encounter, 43 route and 59 enemy-mix checks. The 59 enemy-mix checks also passed in the rendered Forward+ game. No script errors or failed checks were reported. Rendered captures were inspected for the live six-enemy approach, all three silhouettes side by side, one-shot splatter and small corpse. The dedicated bug-mix suite exercises saved six-enemy composition, spawn clearance and navigation, fractional-hit death, non-damaging hit rejection, one-shot death/splatter, small lunge timing/damage, scale/collision restoration and actual aimed pistol hits through the group. Frozen-target firing checks ammunition rules only and is not reported as human combat pacing.

## Human playtest feedback / revision 02

The user's result screenshot reported 41.72 s total, 17.27 s active, 24.45 s quiet, 175.5 m travelled, 33 shots, zero incoming damage and 5/5 encounters cleared. D lasted 11.92 s (the earlier revision 01 screenshot had D at 4.92 s). The user felt pressure but could comfortably backpedal while firing and reloading because there was ample retreat space. These are individual attempts with different composition and player familiarity, not controlled averages.

The user agreed with testing one of D's three smalls from a hatch behind the approach while keeping the total at six. Rear ambushes should have an audible grate/bug warning, sufficient separation and emergence time for a response, and one activation per encounter. A future return-trip ambush can arm a previously quiet hatch through an explicit progression event. Neither change is implemented yet. Wall/ceiling pursuit was then raised as a future small-bug capability; see [FR-003](future-refinements.md#fr-003-small-bug-wall-and-ceiling-navigation).

The first doorway-trigger proposal was rejected because the user can engage and backpedal before entering D. The user specified a blind 90-degree left reveal, an earlier trigger and a 1–2 s delayed rear burst. The corrected [rear hatch plan](rear-hatch-plan.md) records that spatial direction before implementation.

Revision 03 implementation is now built: see [the blind-corner/rear-hatch test](rear-hatch-plan.md). D retains three smalls, two regulars and one spitter, with one small moved to the rear hatch. Geometry and timing changed; compare against the new 114 m empty-route baseline. Historical revision 02 timings above remain distinct.

Revision 04 moves the five front enemies deeper into D following the user's close-doorway feedback. Composition, AI and hatch timings are unchanged; see [the placement comparison](rear-hatch-plan.md#revision-04--give-the-room-reveal-breathing-space).
