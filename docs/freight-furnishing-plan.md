# Freight furnishing sample F-01

Status: **approved by the user and built as layout 06**. This sample follows the revision-05 walkthrough and room-proportion rule. It develops A1 Staff Intake, A2 Inspection and the A8 Annex junction. Project version remains 0.0.009; no commit was requested.

## Review sheets

- [A1 Staff Intake](freight-furnishing-a1-plan.png) / [editable SVG](freight-furnishing-a1-plan.svg)
- [A2 Inspection and stair section](freight-furnishing-a2-plan.png) / [editable SVG](freight-furnishing-a2-plan.svg)
- [A8 Annex doorway correction](freight-furnishing-a8-plan.png) / [editable SVG](freight-furnishing-a8-plan.svg)
- [Dimensions and furnishing data](freight-furnishing-plan.json)

Mint lines show a suggested walk; dashed mint lines show optional access. They reserve a three-metre-wide clear lane. Blue footprints show actual furniture/machinery sizes; small circles are chairs. Purple is the upper entry deck and its open edge guard. The faint grid is five metres. All coordinates remain in the original plan frame; north is decreasing Z.

## A1 / a staffed intake department

The outer 52 x 32 m footprint and its east entry at (114,270) / west exit at (62,288) remain. Divide it into reception, screening, an administration office and staff preparation. The ordinary walk passes reception, screening and preparation; the office is an optional offshoot. Furniture includes the intake/check counters, an inspection unit, workstations, chairs, lockers, benches and kit storage.

All four rooms have 3.5 m clear ceilings above the 0 m floor, replacing the old 8 m volume. Their clear length-to-width ratios are approximately 1.01-1.90. The approved window on the south reception wall spans X=102..110, with sill Y=1 and head Y=2.8. Its exterior is a shallow, non-traversable Mars/plant view with a collision-sealed transparent pane, window mullions, low ridge forms and utility machinery. The southern exterior is clear of neighbouring playable departments. No outdoor route is proposed.

The screening/preparation door is separated from the reception/screening door by a solid return at their corner. Internal openings are four metres wide and reserve 3.2 m clear height, plus header/frame space. Existing six-metre shell thresholds remain.

## A2 / inspection, control and a visible descent

The outer 48 x 58 m footprint and connections stay in place: enter at (44,242), floor 0; leave at (20,184), floor -2. The main walk descends beside the east wall, crosses the working inspection floor, passes staff preparation and enters circuit control. The pump test room and kit store are optional rooms reached through separate openings.

The selector remains at (16,-2,202), and Tr1's cache at (16,-2,228). Their approach spaces remain usable. No new key, gate, mandatory pickup or selector behavior is introduced.

Built I1 change:

| Feature | Plan geometry |
|---|---|
| Entry deck | X=38..56, Z=232..242; floor Y=0 |
| Upper landing | X=52..56, Z=230..232; floor Y=0 |
| Stair flight | Centre (54,230) -> (54,226); Y=0 -> -2 |
| Stair profile | 4 m clear width, eight 0.25 m risers, 0.5 m treads |
| Lower landing | X=52..56, Z=224..226; floor Y=-2 |
| Approach/turn area | Clear upper deck area X=50..56, Z=232..238; lower route continues to Z=223 before turning |

The stair is against the east wall. Use an open guard along the deck edge and exposed stair side, retaining fall protection while allowing a view onto the lower floor. The top-down dotted sightline and N-S side diagram illustrate that intent. The side guard is projected into the section for explanation; it does not cross the stair approach. Verify the view from the actual camera before the first downward step after building.

Control, preparation and kit storage have 3.5 m clear ceilings above floor -2, so their ceiling datum is +1.5. The pump room and normal inspection working bay have 4.5 m clear ceilings (datum +2.5). Over the entry and stair, X=38..56 / Z=224..242, keep the ceiling at +3.5: this gives 3.5 m above the raised entry and 5.5 m above the lower landing. Close the ceiling transitions with bulkheads and check stair headroom. The taller volume is local to the height transition.

The inspection floor's principal working bay is approximately 24 x 26 m; its southwest service recess continues beside the solid entry platform. The platform and stair are circulation spaces. All five resulting rooms have clear proportions within approximately 1.08-1.35; no long narrow room is hidden behind the parent footprint's dimensions.

## A8 / distinct openings around a solid junction

The 36 x 58 m shell and north entry at (85,184), floor -2, remain. Replace the old short, offset divider pieces with a continuous partition and four spaces: intake, tool workshop, service stores and spare assemblies. The workshop's clear ratio is about 1.91; the other rooms range from 1.18 to 1.81.

The two north-facing internal openings are centred at (75,204) and (93,204), each four metres wide. Fourteen metres of solid wall separate their opening edges, with the T-wall connection at X=85 inside that solid section. Storage access from the workshop occurs at (85,214) and (85,233), clear of the wall intersections. The northern store makes an optional local loop; it bypasses no mission requirement.

Intake and stores have 3.5 m clear ceilings; the tool workshop has 4.5 m. Workbenches, racks, a small machine and spare assemblies establish room function. A8 remains optional; this sheet does not assign a new reward.

## Construction intent for this sample

Keep Kenney metric grids, current movement tuning and the existing objective logic. This pass uses simple measured props: approximately 0.75 m desks, 0.45 m benches, 2.1-2.3 m cabinets/racks, 2.6 m pump bodies and appropriately taller service runs. Exact footprints/heights are in the JSON. Use simple blocking collision for substantial equipment; chairs are visual placeholders with their space reserved, avoiding small independent movement blockers around the workstations.

Wall data uses centreline segments with butt ends at opening edges. Apply 0.25 m thickness perpendicular to each segment so a four-metre opening remains four metres clear. Reserve 0.25 m beside openings for frame width. Do not expand wall ends into the labelled opening. A1's tightest corner retains more than one metre of solid return beyond this allowance.

The furnishing pass leaves these openings passable. Automatic pressure-door behavior, final enemies/ammunition and final art remain subsequent passes. Their eventual placement should use these working spaces and clear lanes. A3-A7, the B branch, the hub, Maintenance and arrival/departure are outside this sample's geometry changes.

## Paper checks and build review

The drawing generator checked all 13 room proportions against 2:1, three-metre-wide suggested paths against furniture and wall thickness, internal doorway returns against a one-metre minimum, furniture overlap, rectilinear routes and prop bounds. It contains 50 furniture/machinery footprints. These are paper checks; they do not establish engine collision, pursuit navigation or camera visibility.

The user approved the connected room sequence, furnishings, lower ceiling palette, A2 landing and A8 doorway separation. Source map and authored nodes are now updated, baked, saved and reloaded. Human feel still needs this sample walkthrough; keep playtest results separate from automated validation.


## Built sample and checks

The saved map contains 1,193 brushes. **157 checks passed, zero failures**, covering the full mission route, A reverse, all 19 stairs in both directions, six optional furnished out-and-back paths, all 13 ceiling zones, 11 internal opening clearances, two views onto A2's receiving floor before descent, the open deck guard and sealed window. Existing card, selector/cache, ladder, gate and completion behavior also passes. All 13,916 nondegenerate baked triangles retain orthogonal 1 m Kenney repeats; authored textured props use local metre projection and unit scale. No script/engine errors or warnings were reported by this build, QA or rendered capture.

Fifty planned footprints comprise 48 new furniture/machinery placements and reservations for the existing selector/cache. Eight chairs have no independent collider. Desks and benches have tops and supports; racks have open shelves; inspection units, pump bodies and service runs use simple measured brush forms. Their silhouettes and density remain blockout choices for the user to judge.

The source audit compared every brush fragment outside the approved room interiors/window opening: all 863 preserved fragments retain their dimensions and six face textures. Other A rooms, B, the hub, Maintenance and arrival/lift geometry remain unchanged. Shared player, weapons and addons were not edited. Normal rebuilding preserves editable authored nodes outside Geometry. The two F-01 application scripts are one-time helpers and must not replace subsequent TrenchBroom edits.

Player-eye renders were inspected for intake, office, the window, upper landing, stair head, pumps and both Annex rooms. The old oversized Inspection label was removed. See [built sample views](freight-furnishing-built.png). This is geometry/readability evidence, not populated combat timing or enemy-navigation validation.

For the next human walk, use F5/F6 and focus on A1's ceiling/furniture scale, seeing the lower floor before A2's descent, movement around the optional pump/store rooms, and the separated A8 doorways. The broader furnishing rollout and enemy/pickup pass follow that feedback.
