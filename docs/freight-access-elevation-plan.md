# Freight access / built elevation pass 05

Current layout 06: the approved [F-01 sample](freight-furnishing-plan.md) supersedes A1/A2/A8 internal partitions, ceilings and furnishing, and replaces I1 with the east-wall stair from (54,230) to (54,226), floor 0 to -2. Their external portals and the remaining A-01 layout are unchanged.
Status: revision 05 is built. The [reviewed A-01 interiors and upper-floor drawings](freight-a-interior-plan.md) supersede the revision-04 whole-level drawing for A. B and Maintenance retain revision-04 geometry. See [play and rebuild instructions](freight-blockout.md); enemies and supplies follow the empty-walk review.

- [Height drawing and schematic side profiles](freight-access-route-plan.png)
- [Editable elevation drawing](freight-access-route-plan.svg)
- [Approved top-down reference with gate and selector notes](freight-access-route-plan-approved-topdown.svg)
- [Route, objective and dimension schedule](freight-access-route-plan.md)

## The experience

**Security:** leave the hub at ground level, descend 2 m into Inspection and climb back to Records through the side detour. Climb Records to the +4 m gallery and Supervisor suite, collect R, then return downstairs to door 2. Climb to +2 m Dispatch and collect K. Watch climbs from +2 to +6 m, then its upper passage leads to Clearance, where three flights descend to the hub floor. The optional Inspection Annex shares the lower Inspection level.

**Power:** descend 2 m beyond Machine Access into the pump/service area. Either approach climbs back to ground level before door 4, so the red detour and Cooling Gallery still meet. Generator and Relay stay at ground level. Stairs inside Power Control's entrance rise 2 m onto its control floor; the return corridor descends to the hub before S2.

**Maintenance:** its floor is +6 m relative to the hub. The BcD-controlled ladder rises 4 m from Security's +2 m floor. Inside the Generator Hall, three fixed stair flights descend from +6 m to ground level, with landings between them. This makes the crossover feel overhead and gives a high arrival view into the hall. The fixed stairs can be climbed in reverse; the existing BcD gate still governs crossing into Security.

These height changes give spaces a physical identity: low work floors, raised offices/control, and overhead servicing. Stair approaches and landings can support later combat choices, but exact enemy positions and sightlines remain for the next pass.

## Rooms as height transitions

User direction: consider a mezzanine and stairs within any room where they improve the space. A player can enter on an upper walkway, read the working floor below, descend through the room and leave through a lower doorway; the reverse approach can climb from the floor to an upper exit. Use this selectively to create different arrivals, views and combat relationships across the mission.

The floor labels on the route drawing name each room's main floor. They allow additional internal levels. For future room-detail changes, draw each entrance/exit height, the mezzanine footprint, stairs, landings and the open view between levels. A room can perform a height transition currently reserved in its approach corridor, provided the connecting door heights, required gates and return paths still work. Update the stair schedule and drawing together when choosing that relocation.

Built room transitions:

- **A2 Inspection:** an entry platform at 0 m leads down I1 to the -2 m working floor.
- **B2 Pump Floor:** climb T7 from the -2 m machinery floor to a 0 m exit mezzanine inside the room before heading toward B3.
- **A3/A7 Records:** climb R1a/R1b from 0 to +4 m, then enter the elevated Supervisor suite.
- **A5 Watch:** climb G1a/G1b from +2 to +6 m and cross the divided upper floor.
- **A6 Clearance Office:** enter at +6 m from Watch and descend O1a/O1b/O1c inside to the 0 m return floor.
- **B4 Generator Hall:** the +6 m Maintenance arrival opens onto a mezzanine above the hall, connected by three stair flights.
- **B6 Power Control:** a lower 0 m entry climbs to the +2 m control floor.

The drawing and stair schedule now match these built transitions. The low 2 m entry/exit platforms are solid plinths; the +6 m B4 deck has usable space below. Plan the sightlines, access beneath walkways, cover, retreat and enemy pursuit together with the mezzanine. Required cards and controls must remain on the intended route, and a high view must not inadvertently bypass a locked gate.

## Floor schedule

All heights are metres relative to the hub floor, Y = 0. Values describe the main usable floor, not the ceiling. The drawing's gold room labels show these heights; footprint dimensions remain in the route notes and approved top-down reference.

| Floor height | Rooms / junctions |
|---|---|
| -2 m | A2 Inspection, A8 Annex, B2 Pump Floor, C1 Pump Service; J0, JT and JB0 |
| 0 m | Arrival airlock, Receiving, hub, freight lift, A1, A3, A6, B1, B3, C2, B4, B5, B7; JA and JB |
| +2 m | A4 Security Dispatch, A5 Watch Gallery, B6 Power Control |
| +4 m | A3 gallery and A7 Supervisor suite |
| +6 m | A5 upper Watch floor, A6 Clearance mezzanine, Maintenance Workshop and upper service connection |

B6 has a short lower entry at Y=0 before its internal stairs; its main floor and objective P are at +2 m. B4 has the +6 m Maintenance landing and descending stair structure above its main Y=0 floor. These are deliberate split-level room details, not mismatched doorway heights.

## Built stair schedule

Use the gym's tested starting profile: **0.25 m risers, 0.5 m treads**. A 2 m change uses eight risers and reserves a 4 m horizontal flight, plus a 2 m level landing at each end: **8 m overall**. Reserve **4 m clear stair width** within the ordinary 6 m corridors, with solid sides/guards around the change in floor height. Shared intermediate landings are 2 m long. Turning landings need enough clear width for the route, rather than tapering at a corner.

Each coordinate pair below is (X,Z) in metres. Endpoints mark the flight itself; landings extend beyond them along the same straight path. The direction shown follows the ordinary outward/return route. Arrows on the drawing always point UP, even on flights normally descended.

| ID | Position / connection | Flight start -> end (X,Z) | Floor change |
|---|---|---|---|
| I1 | Inside A2, entry platform -> work floor | (44,228) -> (44,224) | 0 -> -2 m |
| T2 | Closed front approach to door 1 | (52,158) -> (52,154) | -2 -> 0 m |
| T3 | Red Inspection -> Records detour | (97,151) -> (97,147) | -2 -> 0 m |
| T4 | After door 2, before A4 | (121,111) -> (121,107) | 0 -> +2 m |
| R1a | A3 lower Records stair | (58,128) -> (58,124) | 0 -> +2 m |
| R1b | A3 upper Records stair | (58,122) -> (58,118) | +2 -> +4 m |
| G1a | A5 lower Watch stair | (145,120) -> (145,124) | +2 -> +4 m |
| G1b | A5 upper Watch stair | (145,126) -> (145,130) | +4 -> +6 m |
| O1a | A6 upper descent | (130,176) -> (134,176) | +6 -> +4 m |
| O1b | A6 middle descent | (136,176) -> (140,176) | +4 -> +2 m |
| O1c | A6 lower descent | (142,176) -> (146,176) | +2 -> 0 m |
| T6 | Beyond B1, before the Power fork | (342,262) -> (342,258) | 0 -> -2 m |
| T7 | Inside B2, work floor -> exit mezzanine | (342,186) -> (342,182) | -2 -> 0 m |
| T8 | C1 -> C2 red service route | (300,180) -> (300,176) | -2 -> 0 m |
| T9 | Inside B6's entrance | (242,180) -> (242,184) | 0 -> +2 m |
| T10 | B6 -> hub return, before S2 | (204,222) -> (204,226) | +2 -> 0 m |
| T11a | Inside B4, upper descent | (227,52) -> (231,52) | +6 -> +4 m |
| T11b | Inside B4, middle descent | (233,52) -> (237,52) | +4 -> +2 m |
| T11c | Inside B4, lower descent | (239,52) -> (243,52) | +2 -> 0 m |
| L1 | BcD ladder in A4 | (148.4,62), vertical | +2 -> +6 m |

T11 reserves 20 m overall along X=225..245 at Z=52, including its two intermediate landings and both end landings. Its 4 m width fits inside B4's reviewed footprint. T9 reserves the B6 entry strip along X=242, Z=178..186; the room's north threshold starts at Y=0 and reaches the upper floor at the landing. Keep the stepped strip clear of props and the power control interaction.

T2 serves the deliberately blocked approach and stops on the level platform before door 1. T7 serves the optional B2/B3 route. The ordinary known route uses I1, T3, Records R1a/R1b in both directions, T4, G1a/G1b, O1a/O1b/O1c, T6, T8, T9 and T10.

## Connections and gates

- Doors 1, 2 and 4 have Y=0 on both sides. Door 2 is before the climb into A4, preserving the Records-card requirement.
- S1 and S2 meet the hub at Y=0. T10 finishes well before S2. The freight lift and its threshold stay at Y=0.
- A4's freight card K stays on the raised floor, before choosing Maintenance or A5/A6. Records card R stays in A7 at ground level. P is on B6's raised control floor.
- A2's selector and Tr1 cache move with its -2 m floor; their behavior is unchanged. Both ends of the upper Maintenance gate are +6 m. Its ladder and gate remain controlled by BcD.
- All ordinary stair routes are reversible. No jump, forced drop or new progression condition is added.

## Checks and walkthrough validation

Paper checks passed for every connection's start/end height, every stair's rise/run and landing lengths, level door thresholds, and return loops closing at hub height. The existing progression checks also pass for all 5,826 reachable interaction states. The 2D room/corridor checks still pass. Those paper checks establish route coherence. The built scene also passes collision/continuous traversal, stair, ladder and progression checks described in the blockout notes; enemy navigation is not yet implemented here.

During blockout, reserve at least 3 m clear headroom above stair nosings and landings, and check the actual ceiling/underside geometry along the full climb. Keep the approved gates effective from raised viewpoints and prevent the inactive Maintenance connection from being bypassed by a jump or nearby prop. Place guards and walls where needed without obscuring the route itself. Check player walking, sprinting, ADS retreat, turning on landings and bug pursuit using the existing gym movement tuning. The E-use ladder is implemented and checked in both directions with the real player capsule. Bug pursuit remains deferred to the enemy/navigation pass.

The earlier 1,956 m ordinary-route and 1,314 m BcD estimates describe revision 04 only. Revision 05 adds the reviewed A interior routes; its paper A trace is approximately 1,314 m hub to hub, excluding Annex, exploration and combat. These estimates are not new timing results. Stairs and ladder movement must be measured in the empty traversal test; the ten-minute populated target remains unchanged. No artificial wait or movement slowdown is added to reach it.


## Registration refinement / layout 08

The approved [F-03c registration plan](freight-registration-recess-plan.md) introduces local circulation strips at -0.25 m inside A1. Work bays, the staff-door landing and desk area remain at 0 m. The staff strip ends two metres before its door; the office entrance stays on the lower strip. Shell connections, Screening, the exterior window and all other mission heights retain their prior elevations.
