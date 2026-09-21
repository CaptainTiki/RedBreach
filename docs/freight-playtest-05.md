# Freight revision 05 / human walkthrough feedback

Date: 2026-09-20. Build 0.0.009, layout revision 05, A-interiors-01. This records the user's run and architectural feedback; no new geometry was built while recording it.

## Verified result

| Measure | Result |
|---|---|
| Outcome | Complete |
| Distance | 1,958.25 m |
| Elapsed time | 296.18 s / 4 min 56 s |
| Movement | User reports holding Shift throughout |
| Route choice | BcD Maintenance crossover |
| Objectives | Records and freight cards collected; power restored; departure completed |

Evidence: the user's completion screenshot and local export `2026-09-20T15-49-46_303360_1.json` under `user://freight_walkthroughs`. The export records arrival, visits to A1/A2/A8/A3/A7/A4, both cards, Maintenance/B4/B5/B7/B6, power, S2, the lift and departure. It does not record a visit to A5/A6 on this run; this is the A-to-Maintenance route rather than the ordinary A return through those rooms.

The user estimated about 1.5 km by the Maintenance ladder. Treat that as their observation: this export contains overall distance and event times, not distance at each event. The screenshot's WALK label at completion does not establish the movement mode used throughout the run; the Shift-held report comes from the user.

Elapsed time includes interactions, exploration and pauses. This empty run is neither a pure sprint-speed benchmark nor a ten-minute populated-mission result. The earlier revision-04 run ended after the ordinary A return, used a different route and did not complete the mission; do not compare the two elapsed totals as equivalent runs.

## User assessment

- The overall route length feels good, including the approximately two-kilometre completion through the known Maintenance shortcut. The user is satisfied with the direction of the blockout.
- Several adjacent doors/openings meet on a thin edge. Give them a couple of feet or more of architectural separation. The supplied example shows the A8 Inspection Annex area.
- Some rooms feel about twice as tall as their use warrants. In the Mars pressure-envelope fiction, offices and residential/staff spaces should have lower ceilings. Large industrial volumes need a reason for their height.
- Long hallways connect the large room footprints and need not be shortened now. Develop interest through outside views, ducts, unusual pump equipment, repeated uprights, automatic compartment doors, supply crates and enemies.
- Continue blockout with desks, chairs, pumps and machinery so room function and movement can be judged together.
- Prefer stairs along room edges. A central stair is an intentional exception when the mezzanine is the focus, including the possibility of an oppressive enemy presence above.
- Provide upper and lower landings. Players should see the receiving floor before committing to a descent; a gap in opaque rails alone is insufficient guidance.

## Design follow-through

[Architecture language](architecture-language.md) records these user principles, proposed starting dimensions and a staged functional-furnishing pass. The current route remains the baseline. Exact doorway shifts, ceiling changes, stair relocation and furniture placement belong on the next revised paper plan. Enemy counts, supplies and automatic-door behavior still require their respective placement/behavior passes.

The current automated validation establishes traversability; this feedback adds architectural plausibility, eye-level visibility and room-function criteria for the next review.
