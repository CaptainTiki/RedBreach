# Example mission / restore freight access

Status: the user authorized an empty blockout after reviewing the route and height direction. [Built revision 04](freight-blockout.md) is ready to walk, with the [updated plan](freight-access-route-plan.md) and [floor/stair schedule](freight-access-elevation-plan.md). Progression is unchanged: fixed door 1, Records card at 3 for door 2, and freight card in A4 before the Maintenance/A5-A6 choice. Enemy/pickup planning will follow this scale and traversal review.

## Agreed design stages

1. **Mission walkthrough:** agree on the goal, required actions, information given to the player, objective dependencies, return journeys and completion. Describe what happens in plain steps before choosing dimensions.
2. **Spatial paper plan:** arrange those steps as a coherent top-down layout. Show connections, keys, gates, shortcut directions, landmarks and what the player can see or understand at each decision. Trace every allowed completion order to check that no required item sits behind its own gate.
3. **Enemies and pickups:** place encounters, ambush cues, retreat space and resources on the reviewed layout. Account for movement speed, reloads, sightlines and expected travel. Revisit affected spatial decisions if this pass exposes a problem.
4. **Build:** block out the reviewed plan and implement its required interactions. Walk the empty layout first to check scale, traversal and progression, then populate the planned encounters and pickups.
5. **Playtest and revise:** compare first-time navigation with a familiar run. Record travel, search/decision time, encounters and returns; revise the relevant earlier stage when needed.

The current authorization brings the empty traversal/progression check forward, before the enemy/pickup pass. The populated build still follows that review. The exit lift currently ends the walkthrough; persistent cabin loading into another level remains a later implementation.

## Campaign role and feel

This mission is provisionally level 2 or 3 in the campaign: aliens attack the colony, evidence reveals that they have been here for a long time, and the larger goal becomes leaving the planet. This mission's exact relationship to the discovery is still open. Restoring freight access is an early obstacle along that larger journey; do not assign a major revelation or final evacuation event without another story decision.

The player already understands movement, shooting and the game's feel. Assume that competence in the walkthrough and later encounters. A new alien or weapon may be introduced here, but that is optional and currently undecided.

Arrive through an airlock into a mostly quiet Receiving room. Give the player a foothold: time to look around, recognize where they arrived and choose the onward route before the first attack. Environmental tension and distant signs of trouble can establish mood. Progress into hallways and rooms where occupied encounters and triggered arrivals can develop pressure; exact enemy types, counts and placements belong to the later pass.

## Pacing target

Target **about ten minutes for an ordinary run by a player familiar with most of the route**. First-time players may take longer to explore and understand the space. A player skipping secrets and rushing fights can finish faster. Optional discoveries must not become mandatory merely to reach the timing target.

The current walkthrough defines objectives, not ten minutes of proven content. Develop each required branch as a sequence with useful decisions, varied spaces, encounters and a payoff when its spatial and combat passes are reviewed. Use tested movement speeds and real encounter observations. Track playable mission time separately from hardware-dependent loading waits; do not lengthen chambers or add empty travel solely to fill the clock. Validate the target across several familiar-player runs after construction.

## Mission goal

Restore access to the freight lift and reach the processing deck of the Mars industrial plant. The player arrives from the preceding level through an airlock into Receiving. A service hub offers access to Security and Auxiliary Power. The freight lift needs an access card AND restored auxiliary power.

## Approved route walkthrough / built revision 04

This example takes Security first. Power-first must also work; the branch letters are references, not an enforced order.

1. **Complete the arrival airlock cycle.** Keep the player and chamber present. Open the destination door once Receiving is ready.
2. **Establish a quiet foothold.** Step into Receiving and show the mission title once. Let the player orient themselves before pressure begins in the onward halls and rooms.
3. **Find the freight lift in the service hub.** Its display names two missing requirements: freight clearance K and auxiliary power P. Identify the Security and Power routes here.
4. **Enter Security through Staff Intake and Inspection.** In A2 the optional three-button circuit selector offers GMa, BcD and Tr1. No selection is required for the ordinary mission; see the shortcut below.
5. **Detour around the locked Records entrance.** Door 1 stays locked. The red side passage reaches the junction at door 2. The Inspection Annex is an optional branch off that detour.
6. **Find the Records card.** Door 2 requires R. Turn into Records A3, go north to the supervisor room at 3/A7, collect R and return. The card is accessible before its locked gate.
7. **Collect clearance before choosing the return.** Open door 2 and collect the separate freight card K in Security Dispatch A4, visibly before the route split. Either continue through Watch Gallery A5 and Clearance Office A6, release S1 and return to the hub, or take the enabled BcD Maintenance passage directly to B4. A5/A6 are now the longer return route, with no required objective left behind.
8. **Explore the Power branch.** Machine Access B1 leads to a choice. B2 -> B3 reaches door 4's locked east face; newcomers can backtrack from that discovery. The red C1/C2 service route reaches its west-side release. A familiar player can choose that detour immediately.
9. **Restore the feed.** Release door 4 from the west if desired, then continue through Generator Hall B4, Relay Gallery B5 and Power Control B6. Restore P, release S2 from the Power side and return to the hub. Neither the red route nor P requires a card. B7 is an optional service room off B5.
10. **Activate and board the freight lift.** K AND P permit departure. Preserve the occupied cabin while closed doors, light, sound and travel animation cover the level swap. Open only when the next destination is ready. Stepping out displays that destination's title.

### Optional circuit shortcut

In A2, exactly one of **GMa**, **BcD**, **Tr1** can remain selected. Initially all are off. GMa sparks and supplies no useful output. BcD deploys the ladder in A4 and opens an upper service connection through Maintenance to B4, with a fixed descent into the generator hall. Tr1 opens a local health hatch in A2, and closes BcD again. Matching BcD and Tr1 labels at their destinations let the player learn the circuit. From the switch, the remote ladder response is neither visible nor audible; only its selected lamp gives local feedback.

Trying GMa -> BcD -> Tr1 leaves the secret open and the shortcut closed. A knowing player can collect the secret, then reselect BcD. The health does not respawn when the circuit changes. No selector choice blocks normal completion. With K collected at its A4 entrance, the crossover skips A5/A6 and the hub revisit; approaching it in reverse from B4 can also bypass R/door 2 and reach door 4's release. K and P remain mandatory. B2/B3 become optional on the familiar red service route; their later content should reward exploring them without requiring every player to visit.

## Elevation through the walkthrough

The user wants the walk to feel three-dimensional. The built Security route descends from the hub into Inspection (-2 m), returns to Records at ground level, rises to Security/Watch (+2 m), then descends on the ordinary return. The Power branch descends into its pump/service spaces (-2 m), climbs toward Cooling/Generator at ground level, rises inside Power Control (+2 m), and returns down to the hub. Maintenance runs overhead at +6 m, reached by the BcD ladder and fixed stairs into Generator Hall.

See the [elevation pass](freight-access-elevation-plan.md) for stair placements, floor labels, landing reservations and checks that the loops meet. The heights provide room identity, changing views and future combat choices. Gate dependencies and both required lift objectives remain as described above.

## Airlock and elevator transition intent

- Use a reusable occupied chamber at level boundaries. Keep the player, chamber floor, walls, doors and presentation alive throughout the transition, preserving the player's health, ammunition and intended campaign state.
- Close and secure the departing-side doors before unloading anything the player can see or stand on. Both sides remain closed during the level swap; lights, sound and airlock-cycle or elevator-travel animation maintain continuity.
- Prepare the destination while that presentation continues. The next door opens only after the destination is ready for safe play, including its geometry, collision and required gameplay systems. A longer load extends the closed-chamber cycle rather than exposing an unfinished room. Smoothness is a requirement to test, not yet a performance guarantee.
- A trigger just outside the destination doorway shows a floating, nonblocking screen title, for example **L03 Freight Lift Repair**. The displayed text belongs to the destination level. Exact numbering and wording remain provisional.
- Allow the title a readable appearance/brief hold, then animate its alpha to zero over approximately **two seconds**. Controls remain available. Show it once per arrival; repeatedly stepping across the threshold must not replay it. Exact entrance motion and hold duration remain presentation details.
- For this walkthrough, use an incoming airlock and an outgoing freight lift. Other levels may use either chamber type at either end. The empty blockout includes these chambers and the arrival title; cross-level loading remains deferred until a destination level exists.

## Progression rules for the spatial pass

- Both required branches are accessible from the first hub visit. Their entry routes must remain readable when shortcuts are still closed.
- Card and power are persistent requirements, not consumed on a failed lift interaction. Finding one does not close the route to the other.
- If Power is completed first, the lift reports that access clearance is still needed; the Security branch and its return then complete the same mission.
- S1/S2 open from their objective side and stay open. Door 4 releases only from its west/red/B4 side and stays open. BcD follows the A2 selector instead. The original approach routes remain usable; shortcut discovery cannot trap the player.
- Optional exploration can be skipped without preventing completion. The user-requested Records card, doors 1/2/4 and three-button selector are now recorded here and in the current route plan. Further progression additions require updating the walkthrough.
- The paper plan must show the player's view of the problem: where the blocked lift and its requirements become understandable, how branch destinations are identified, and when return connections become recognizable.

The ten-minute familiar-player target is agreed direction. Room dimensions are now built; drawn centreline route lengths remain estimates to compare with walkthrough recordings; encounter counts, supply amounts, optional weapon/alien introduction, exact level number and story clues remain undecided. Use the tested movement and combat behavior when those later passes are designed.

## Spatial and elevation revision 04

See [the drawing](freight-access-route-plan.png) and [spatial notes](freight-access-route-plan.md). The main footprint is retained with the user's added side rooms, forced Records detour, separate local keycard, Power-side return latch and selector-controlled upper crossover. The user confirmed the separate card interpretation. The notes trace normal and knowledgeable routes, identify optional spaces and check progression states. The user approved those top-down connections. The drawing now matches the built stairs, mezzanines and floor heights. Empty traversal checks pass; the ten-minute target still needs populated playtests.
