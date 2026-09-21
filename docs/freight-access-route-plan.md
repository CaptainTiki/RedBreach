# Freight access / route baseline 04, A interior revision 05

Status: the route and objective rules below remain the baseline. **A now uses the built [A-01 interior plan](freight-a-interior-plan.md)**, including moved thresholds, upstairs Records and the Watch/Clearance upper return. The whole-level SVG/PNG remain the revision-04 baseline; consult the A drawings for its current interior geometry. See [play and rebuild instructions](freight-blockout.md) and the [built floor/stair schedule](freight-access-elevation-plan.md). Cards, gates, the selector and Maintenance traversal work. Enemies and broader pickup placement remain a later pass.

- [Rendered paper plan](freight-access-route-plan.png)
- [Editable elevation drawing](freight-access-route-plan.svg)
- [Approved top-down reference and selector notes](freight-access-route-plan-approved-topdown.svg)
- [Floor heights, stairs and landings](freight-access-elevation-plan.md)
- [Mission sequence and transition requirements](example-mission-walkthrough.md)

## The four numbered changes

1. **Blocked Records entrance.** Door 1 at the south entrance to A3 is permanently locked for this mission. From A2, follow the red passage east and north around it. It arrives at the junction just west of door 2. A8 Inspection Annex is a side room off this bypass, following the user's drawing; entering it is not required to traverse the bypass.
2. **Records-card gate.** Door 2 bars the east/north passage toward A4 Security Dispatch. Its west-side approach remains connected to A3 Records Work Floor. The player can turn into Records without passing the locked door.
3. **Card before lock.** Head north from A3 to A7 Records Supervisor, collect the Records card R, then return through A3 to door 2. R opens door 2 persistently; it is not consumed. A4 contains the separate freight-lift card K, before the choice of Maintenance or the A5/A6 return. Use visibly distinct names/readers for the two cards in the later presentation pass.
4. **Power-side latch.** Approaching B3 from B2 reaches the closed east face of door 4. It cannot be released from that side. Backtrack through B2 to the junction north of B1, then take the red service route through C1 and C2. That route joins the west side of door 4 and the route to B4. Its manual release is on this west side. Once released, door 4 stays open in both directions; no timed closing or relocking. B4 also connects to the west-side release, so a player arriving through Maintenance can open it too. There is no artificial requirement to have visited C1/C2 first.

The red side room west of B5 is retained as B7 Relay Service. A8 and B7 have no assigned mandatory item or reward yet. Their contents belong to the later pass. C1/C2 names describe proposed service spaces, not additional objectives.

## Walkthrough through the revised plan

1. Arrive through the southern airlock. Step into mostly quiet Receiving; show the destination title once, then fade it. Continue to the service hub.
2. See the freight lift and its two requirements: freight clearance K AND restored auxiliary feed P. Security and Auxiliary Power can be tackled in either order.
3. On the Security branch, pass A1 Staff Intake and A2 Inspection Floor. Door 1 blocks the direct entrance into Records. Take the red detour to the junction at door 2.
4. Door 2 requires R. Turn into A3, visit the supervisor room at 3/A7 and return with R. Open door 2 and enter A4 Security Dispatch.
5. Take freight card K in A4. Place its pickup visibly before the route choice. Continue through A5 and A6, release S1 and return to the hub; or, if BcD was enabled, cross Maintenance directly into B4. A5/A6 now form the longer return, with no mandatory objective left behind when taking Maintenance.
6. From the hub, the Power branch begins at B1. The apparent main route through B2 and B3 encounters the locked east face of door 4. A newcomer can discover this and backtrack. A player who knows the layout can choose the red C1/C2 service detour at the junction immediately.
7. Reach door 4's west side. Release it to connect back to B3 if desired; opening it is not required to continue north to B4. Continue through B4, B5 and B6 to restore P.
8. Release S2 from the Power side and return to the hub. With K and P complete, board the freight lift and preserve the occupied cabin during the concealed transition.

All ordinary open passages are bidirectional. Neither branch consumes or removes progress from the other. S1/S2 are manual releases from the branch side, independent of keycards and electrical supply, and stay open after use. The original approach routes remain available.

## A2 circuit selector / optional knowledge shortcut

The blockout places all three buttons in A2, with the Tr1 health hatch in that same room so the secret has a local visible result. BcD operates remotely in A4/M. This local cache remains optional.

| Selected code | Local response | A4 ladder / Maintenance gate | Tr1 health hatch |
|---|---|---|---|
| None initially | All indicators off | Closed / retracted | Closed |
| GMa | Sparks, faulty circuit | Closed / retracted | Closed |
| BcD | Selected indicator glows | Ladder deployed; upper passage open | Closed |
| Tr1 | Selected indicator glows; hatch opens | Closed / retracted again | Open |

Only one button remains selected. Pressing another replaces the selection; pressing the already selected button leaves the state unchanged. No timeout or random selection. A collected health pickup stays collected when buttons are toggled; changing the circuit cannot refill it. The walkthrough placeholder restores 25 health when useful. The hatch is a reachable cache, not a chamber that can trap the player when closed.

Label the ladder circuit and Maintenance door **BcD**, and label the health hatch **Tr1**, matching the buttons exactly. From the A2 panel, the remote BcD effect is out of view and earshot: no global confirmation popup, map marker or carried remote motor sound. The local selected lamp confirms the input. The codes at the actual destinations provide the clue.

The user's example sequence GMa -> BcD -> Tr1 ends with the secret hatch open and Maintenance closed. An attentive or familiar player can collect the health, then deliberately select BcD again before leaving. This is learned route knowledge; the secret and shortcut are not mutually exclusive over the whole run.

BcD deploys a ladder in A4 into an **upper service tunnel** leading through Maintenance. The matching Maintenance-side gate closes access when inactive. A fixed descent at B4 gives a safe route back to the main deck. Dashed purple lines show this elevated route rather than an open floor-level doorway through Security's wall. Built elevation revision 04 places A4 at +2 m and Maintenance at +6 m: a 4 m controlled ladder rises from A4, and three fixed 2 m stair flights descend inside B4 to ground level. See the elevation schedule for landing reservations. Saved-scene headroom, climbing and continuous traversal have been checked; subjective feel needs the walkthrough. Route-distance estimates measure horizontal travel only.

The ordinary mission can be finished with the selector untouched, GMa selected or Tr1 selected. No required item is hidden in Maintenance. BcD remains an optional route advantage. Because it is bidirectional, enabling it in A2 and later approaching from B4 can bypass the Records card and door 2 entirely. This is shown explicitly as a shortcut consequence for review. It cannot bypass K in A4 or P in B6. The shortest measured BcD route actually takes R normally, claims K, then crosses from A4 to B4; skipping R through the reverse route does not automatically make a faster run.

## Exploration versus familiar routing

The added gates create problems the player can understand and revisit: a closed entrance, a named card reader, a card found on an accessible branch, and a latch visibly released from the other side. The revised geometry should support first-time wrong turns without closing the route behind the player.

B2/B3 now form an optional exploration loop once the red Power detour is known. A8 and B7 are also optional side rooms. We should make their later content worth finding while allowing efficient players to skip it. Do not quietly require clearing those rooms to force their travel into the ten-minute target.

The existing campaign role stays unchanged: an early mission around level 2 or 3 for a player who understands combat, with a quiet arrival foothold. Exact story clues, new enemy/weapon introduction, encounters and resource amounts remain undecided.

## Dimensions and measured travel

The main footprint and original room sizes are preserved. Coordinates are X/Z metres, north up (-Z), east right (+X); this is a planning frame that can be recentered. Most passages are 6 m clear, Receiving to hub is 8 m, and the upper Maintenance link is 4 m. The airlock is 6 x 8 m; freight cabin is 10 x 12 m. Large working areas remain scale proposals, not proven room sizes.

| Drawn route | Distance | Walk at 5 m/s | Sprint at 8 m/s |
|---|---:|---:|---:|
| Known ordinary route; return to hub after each objective | 1956 m | 6.52 min | 4.08 min |
| Security loop, including Records card and return | 1038 m | 3.46 min | 2.16 min |
| Power loop via red service detour and return | 808 m | 2.69 min | 1.68 min |
| Known BcD crossover route | 1314 m | 4.38 min | 2.74 min |
| Ordinary route plus one probe of doors 1 and 4 | 2346 m | 7.82 min | 4.89 min |

The ordinary route takes Security first in the drawing; the Power-first order has the same drawn distance. The BcD comparison starts with the selector off and includes visiting A2 to select it. Its sequence is Security -> R -> K in A4 -> Maintenance -> B4/B5/B6 -> P -> hub -> lift. It skips A5/A6 and the outward Power approach.

At this scale the crossover saves 642 m, about 128 seconds walking. Actual mission-time savings still depend on combat and exploration. Probing door 1 adds 34 m; going from the B1/B2 fork to door 4's east face and back adds 356 m. These two example wrong turns together add 390 m, about 78 seconds walking, before search or decision pauses. They are examples, not assumptions about every newcomer.

Distances follow drawn corridor centrelines through room centers. They are neither shortest physical paths nor player recordings. Corner cutting may shorten them; combat movement and exploration add distance. Vertical stair/ladder travel, climbing time, interaction, reading, combat, stops and loading are excluded. Built revision 04 adds floor changes without altering these horizontal estimates. **About ten minutes on a normal familiar-player run remains a playtest target.** The drawing alone cannot establish that duration. Assess whether these long walking routes and large spaces feel appropriate during empty traversal, then measure populated runs rather than padding travel or assuming fights supply a fixed remainder.

## Paper validation

The revised graph checks passed:

- Both ordinary objective orders complete the mission without Maintenance.
- R is reachable through A3/A7 before crossing door 2. Door 1 stays closed.
- With BcD unavailable, omitting R blocks Security as intended; with BcD enabled, the reverse crossover can bypass R.
- The east/B3 side cannot release door 4. The west/red/B4 side can; the release persists. The blocked approach still permits backtracking.
- Selector outputs are exclusive. Tr1 closes BcD; the secret pickup does not respawn on a circuit change.
- All reachable combinations of location, inventory, released gates, selector and collected-secret state retain a completion path. The check starts with the selector off and permits switching only in A2.
- Neither K nor P can be omitted, even with every optional connection available. Checking the lift early consumes nothing.
- Room rectangles and corridor footprints do not overlap unrelated rooms. These are 2D planning checks. Built collision, continuous traversal, ladder safety and gate interactions also pass the freight checks; subjective sightlines/readability and enemy navigation need the next playtest/pass.

No game geometry, runtime interaction or enemy placement was changed for this revision.

## Coordinate schedule

Room centers and sizes in metres. Numbered gate 3 is the card room A7, not a third locked door.

| ID | Center X, Z | Size X x Z | Proposed name |
|---|---|---|---|
| IN | 190, 328 | 6 x 8 | AIRLOCK |
| R | 190, 301 | 40 x 24 | RECEIVING |
| H | 190, 260 | 52 x 40 | SERVICE HUB |
| OUT | 190, 218 | 10 x 12 | LIFT |
| A1 | 88, 278 | 52 x 32 | STAFF INTAKE |
| A2 | 32, 213 | 48 x 58 | INSPECTION FLOOR |
| A3 | 52, 128 | 64 x 36 | RECORDS WORK FLOOR |
| A4 | 121, 71 | 66 x 44 | SECURITY DISPATCH |
| A5 | 143, 129 | 30 x 30 | WATCH GALLERY |
| A6 | 133, 182 | 46 x 32 | CLEARANCE OFFICE |
| A7 | 42, 61 | 40 x 40 | RECORDS SUPERVISOR |
| A8 | 83, 213 | 36 x 58 | INSPECTION ANNEX |
| B1 | 286, 278 | 56 x 36 | MACHINE ACCESS |
| B2 | 342, 207 | 52 x 62 | COOLANT PUMP FLOOR |
| B3 | 322, 125 | 64 x 38 | COOLING GALLERY |
| B4 | 250, 62 | 72 x 48 | AUXILIARY GENERATOR HALL |
| B5 | 228, 132 | 28 x 36 | RELAY GALLERY |
| B6 | 242, 194 | 48 x 32 | POWER CONTROL |
| B7 | 191, 130 | 30 x 42 | RELAY SERVICE |
| C1 | 286, 208 | 32 x 30 | PUMP SERVICE |
| C2 | 266, 150 | 28 x 26 | VALVE SERVICE |
| M | 184, 52 | 34 x 28 | MAINT. WORKSHOP |

| Gate / marker | X, Z | Rule |
|---|---|---|
| Door 1 | 52, 147 | Fixed closed |
| Door 2 | 109, 128 | Records card R |
| Card 3 / R | In A7 | Opens door 2 |
| Freight card K | In A4, before the route choice | Lift clearance; collect before Maintenance or A5/A6 |
| Door 4 | 287, 125 | Release on west side; stays open |
| S1 | 176, 237 | Release from A6 side |
| S2 | 204, 237 | Release from B6 side |
| Exit gate | 190, 228 | K AND P |
| Circuit selector | In A2 | GMa / BcD / Tr1, one active |
| Tr1 hatch | In A2 | Optional health cache |
| BcD ladder / gate | A4 / west Maintenance entrance | Upper passage only while BcD selected |

Junctions: J0 (52,164), JT (85,164), JA (97,128), JB0 (342,248), JB (266,125). They are connection points, not additional rooms. The added left bypass is J0 -> JT -> (97,164) -> JA; JT branches south to A8. The added right bypass is JB0 -> (286,248) -> C1 -> (300,208) -> (300,158) -> (266,158) -> C2 -> JB. Ordinary connections, openings and labels remain editable in the SVG.

The empty blockout is ready to walk. Review scale, height changes and route clarity, then mark enemies, cues, retreat choices and pickups on the combined plan before populating it.
