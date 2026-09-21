# Red Breach architecture language

Working design rules from the user's revision-05 freight walkthrough, 2026-09-20. These guide the next paper and blockout pass. Rules reflect the user's design direction. Values explicitly labelled proposed remain starting points for review; these are game-space guidelines, not real-world construction standards or changes already made to the map.

## Colony identity

Design a working, pressurized industrial colony on Mars. Rooms should communicate their function through proportions, equipment, circulation and connections. Staff spaces feel different from machinery halls. An unusually tall volume needs a visible reason: large equipment, overhead handling, occupied upper floors or a deliberately important overlook.

The freight route's overall length is acceptable to the user. Develop its interior architecture and content while retaining the branching journey. Measure the populated result later; the accepted empty shortcut run does not establish a ten-minute combat duration. See [the playtest record](freight-playtest-05.md).

## Rules established by the user

### Doorways have room around them

Avoid perpendicular door openings that meet at the same thin wall tip or edge. Give each opening a solid wall return, frame depth and clear approach. A T-junction itself can be useful; frame its branches deliberately, with doors set back from the junction or a small shared lobby. The reported A8 junction is an audit starting point, not the only location to check.

Proposed starting dimension: aim for at least **1 m of solid wall beyond a doorway frame before an adjoining opening or corner**, increasing it where doors, readers or movement need more space. Check the outside of the frame, not just opening centre coordinates. Maintain clear passage through the opening and room for its motor/pocket. Do not narrow the tested gates to create the return without explicitly reviewing that change.

### Rooms have room-like proportions

User rule: a room should normally be no more than **two to three times as long as it is wide**. Aim for **2:1 or less**, allowing up to **3:1** for a deliberately elongated room. Measure the clear usable interior, with length as the longer dimension and width as the shorter dimension.

Apply this to **every resulting room after subdivision**, not just the original department footprint. A well-proportioned outer shell can still produce narrow leftover strips that function as corridors. For irregular plans, assess the distinct usable spaces and narrow extensions individually rather than letting a wide adjoining area disguise a long passage.

A **10 m x 50 m space is 5:1**: treat it as a hallway or other linear circulation space. To make it rooms, widen or shorten it, or divide it into genuinely distinct spaces with proper thresholds and circulation. Furniture alone does not turn the long strip into a well-proportioned room.

### Height follows room function

Office, residential and staff spaces should have lower ceilings than large plant rooms. Footprint size alone does not justify a cathedral-height ceiling. Use local ceiling planes, service voids and enclosed office pods inside larger volumes where appropriate; upper rooms can retain their reviewed floor elevations.

Proposed clear-height palette, measured from each occupied floor to the lowest overhead obstruction:

| Space | Initial blockout target | Design reason |
|---|---|---|
| Offices, dispatch rooms, staff and living spaces | Around 3.5 m | Bring the room back to human scale; revisit toward 3 m only with compatible doorway/header geometry |
| Ordinary circulation | Around 3.5-4 m | Readable routes and personnel access |
| Freight/service corridors | Around 4-4.5 m where needed | Equipment clearance, overhead services and a distinct industrial role |
| Machinery halls | Around 5-8 m, or taller for a specific feature | Size to the pump, crane, process equipment or occupied upper level |

These are candidates, not a universal ceiling flattening operation. Existing freight gates have 3.2 m clear apertures; include frame/header depth when lowering their surrounding ceilings. Review ceiling changes in section alongside slabs, stair headroom and the actual standing capsule. Decorative ducts and beams must not silently consume the required clearance.

### Stairs belong to the room's edges by default

Prefer stairs against a side wall or along a mezzanine edge. Give the main floor a usable centre and reserve a sensible approach to the flight. A central stair is a deliberate exception when the mezzanine is the focal point: an important destination, strong architectural feature or an intimidating enemy reveal above the player.

Do not move every existing stair mechanically to the nearest wall. Draw the approach, upper route, lower route and sightline together, preserve objective access, and review the revised arrangement before building it.

### Stair landings must reveal the destination

Provide level upper and lower landings, plus landings between flights. The existing two-metre landing reservation is a starting point; enlarge a turning/viewing landing when needed. Keep doors, furniture and rails out of the turn.

From the upper approach, a player at normal eye height should recognize the stair flight and see a meaningful portion of the receiving floor **before stepping onto the descent**. A gap in an otherwise opaque guard does not establish this. Arrange the approach angle, overlook and guard shape together. Use an offset reveal, open railing or a view beside the flight where appropriate. Keep fall protection and avoid creating a jump bypass of a required gate.

Check the reverse view too: the lower approach should reveal the stair and its destination. Approaching at sprint speed and retreating through the landing both matter. Collision QA establishes physical traversal; player-eye inspection establishes readability.

## A useful architectural vocabulary

Use a small set of repeated elements with different combinations and proportions. Each should have a clear role.

| Element | Purpose in the level |
|---|---|
| Wall return / recessed doorway | Separates openings and gives a door believable thickness |
| Vestibule / small junction lobby | Allows an arrival, a turn and a decision before another threshold |
| Pressure bulkhead / door bay | Marks a compartment boundary and breaks the corridor into recognizable sections |
| Structural bay | Uprights, ceiling beams and service runs create a repeatable rhythm; use selected bays as landmarks |
| Service recess | Places valves, cabinets, small pumps or optional supplies beside the travel lane |
| Office pod | A lower enclosed ceiling and useful workstation layout inside a larger plant envelope |
| Overlook landing | Reveals the destination floor and nearby threats before the descent |
| Machinery island | Establishes room function, cover and a route around equipment, with service access |
| Exterior-view bay | Provides a Mars landmark and a moment of orientation between enclosed spaces |

For exterior windows, a shallow non-traversable view with terrain/plant silhouettes, sky and lighting is a suitable first prototype. Plan its apparent exterior against the surrounding rooms and floors so it does not look through another occupied department. A full outdoor traversal area is unnecessary for that view. The exact rendering method is undecided.

Automatic doors can express pressure compartments without making every passage an E-use stop. Reserve slower airlock cycles for meaningful pressure transitions or level transitions. Pressure-door behavior still needs a separate design: sensor range at sprint speed, opening clearance, obstruction protection, enemy passage and navigation, and failure states. Their presence does not imply a pressure simulation in this blockout pass.

## Continue with functional furnishing

The next pass should include primitive desks, chairs, counters, cabinets, racks, pumps, machinery, ducts and supply-container shapes using the existing Kenney metric textures. Give them actual dimensions and simplified collision appropriate to traversal. Final asset selection and small decorative details can follow later.

Start with the work the room performs, then place its equipment and staff access. Consider entry views, ways around equipment, retreat space and where combat might occur. Mark likely supply and encounter locations on paper while arranging the furniture; actual ammunition quantities and enemy deployment remain a separate balancing pass.

Keep primary routes, stair landings and readers usable. Avoid a repeated slalom of crates placed solely to consume walking time. Chairs and small floor clutter should not snag the player's retreat; decide deliberately which pieces are movement blockers and which are visual placeholders. Preserve useful empty floor around future encounters and enough space for the larger bugs.

## Next blockout sequence

1. Audit A for meeting doorway edges, elongated rooms (including every subdivision), unjustified tall staff-room ceilings, central stairs and hidden descents. Mark candidate corrections on the existing top-down and section drawings.
2. Draw a representative connected sample through A1 Staff Intake and A2 Inspection, with a targeted A8 junction correction. Show each room's clear length/width ratio, furniture footprints, wall returns, clear ceilings, stair landing views and travel lanes. This is a proposed sample scope for discussion, not an instruction to relocate unreviewed geometry now.
3. Build and walk that reviewed sample using simple props. Check that reception reads as reception, inspection reads as a work area, and the room can still support movement and retreat.
4. Apply the successful language through the remaining A rooms and develop the corresponding machinery/service vocabulary for B. Preserve the Records/freight card dependencies and the Maintenance choice.
5. Complete the enemy and pickup pass against the furnished geometry, then test a familiar combat run and a first-time exploratory run separately.

Record intentional exceptions with their gameplay purpose. The aim is a consistent architectural language that supports the shooter, with exceptions that players can read.


## Approved sample / layout 06

The user approved the [F-01 plans](freight-furnishing-plan.md), now built in A1/A2/A8. Their 3.5 m staff ceilings, 4.5 m work areas, four-metre internal openings with solid returns, wall-side Inspection stair, open landing guard and functional furniture are the first concrete application. Other rooms still need their own reviewed spatial pass; these values are not an instruction to flatten or subdivide the whole mission. The shallow sealed A1 window supplies the first local exterior-view prototype. Evaluate this sample in play before broadening the vocabulary.


## Density and complete room composition / user reference follow-up

The user judged the F-01 brush shapes useful but the furnishing density far too low. Their Doom 3 BFG Administration screenshots establish a stronger target: smaller perceived rooms with complete layers of registration furniture, railings, light housings, overhead equipment, wall services and structural framing. Block the full composition in cuboids now so later meshes and pickups have planned places. Do not treat a few isolated desks or an increased brush count alone as completion.

Design a focal assembly, its working space and its supporting architecture together. A registration desk includes staff space, terminals, storage, canopy/signage and task lighting. Reserve walk/retreat routes through occupied surroundings. Keep differences between staff, industrial and service spaces readable without relying on final materials.

Use a mixed authoring workflow: TrenchBroom for room/route architecture, reusable Godot scenes for simple prop assemblies, and Blender meshes for refined repeatable furniture and equipment. Replacement should preserve placement, units and useful collision. Fine surface detail comes later. The user approved [F-02 registration](freight-registration-plan.md), now built as layout 07 in A1 reception. The other areas retain their preceding layout; use this sample walkthrough to judge density before expanding.

The user's upper-catwalk example adds a routing principle: return visually to a familiar room from another elevation after travelling through other rooms. A direct stair inside that room is optional, not required. This is a future planning tool, not authorization to add an unplanned catwalk to the current low-ceiling reception.


## Historical Registration circulation refinement / F-03c floor superseded

The user likes the built F-02 entry, outside view and lighting. They request a shallow circulation-level change, enclosed staff access and a functional registration back office instead of the sparse window lounge. The [built F-03c plan](freight-registration-recess-plan.md) records lowering the walking strip by 0.25 m while keeping work bays and fixtures at their current elevations. Preserve level space before doors; a shallow level change should clarify circulation without causing retreat snags. The user then simplified the walkway in F-03b: straight entry, one long spine, short perpendicular staff and office branches. The user then flagged the staff chairs beside the step and authorized a practical adjustment: the built staff branch stops two metres before its door, leaving the doorway and desk floor at 0 m. The office entrance stays on the continuous lower strip. This is a local user-directed layout, not a new requirement to recess every room. Screening remains at its earlier F-01 blockout.


## Pressurized-colony profile / built F-04 Screening pilot

The user approved establishing the major architectural language before extending the furnishing pass. Represent ribs, substantial compartment frames, angled upper corners, service trunks and visible light housings in blockout now: they consume space and affect sightlines. Fine trim, panel seams, bolts, small pipes, wear and finished meshes can follow later. Keep straight lower walls where furniture needs them. An outer pressure shell does not require every internal office partition to slope.

Use repeated structural bays and purposeful service connections, with equipment fitted into the composition. Preserve circulation, working access, turning and retreat space. The user's Doom 3 Administration references remain the density/composition goal. Staff areas can conceal more services; industrial areas expose heavier framing. Window views and sealed arrival transitions provide Mars context.

[F-04's approved connected plan and architectural section](freight-a1-density-plan.md) now have Screening built as the first pilot, with Administration and Staff Preparation planned as the connected continuation. Walk and critique the Screening profile before extending it. Its repeated ribs, upper corners and compartment frame passed geometry/traversal checks and rendered inspection; the user's subjective assessment is next. Registration remains the accepted density and colour sample.


## Reserve bug-entry hatches during blockout

The user liked the Screening pilot but identified a missing architectural requirement: preserve places for large bug-entry hatches in ceilings, selected walls and suitable floors while composing each space. Encounter tuning can remain later; its physical entry points cannot be left until every surface is filled with cabinets, ducts or lights.

Reserve the whole emergence arrangement on the room plan: aperture and grate travel, sealed service/staging space behind it, an unobstructed drop/emergence volume, landing space and an enemy-sized route into the fight. Size these for the largest intended bug, then validate its real collider and navigation. A clear player route alone is not sufficient. Check above, below and behind against adjoining rooms, upper routes and the colony's pressure envelope. Hatches should connect to enclosed service spaces, not accidentally open a pressurized room directly onto Mars.

Ceiling candidates belong between structural ribs and fixtures, above useful landing space. Wall candidates need a genuine backing service pocket and room in front of them. Floor candidates should be beside the principal route, with a flush closed surface and a deliberate open-state treatment; do not turn the only retreat path or a stair/door landing into an unavoidable pit. Small ventilation slots are not automatically large enemy entrances.

Retain the rear-hatch experiment's lessons when encounters are authored: approach triggers must account for engaging from outside a room and backing away; reserve response time, a hatch cue and a distinct nearby ambush screech (FR-004). Occupied emergence must defer safely, and reset/death/exit must cancel pending spawns. These are encounter requirements, not new spawning behavior in the current empty walkthrough.

[Screening's first reservations](freight-screening-hatch-reservations.png) show ceiling C1 and north-wall W1 as alternatives in one service bay. Their aperture/landing footprints avoid current props; W1 still needs a backing pocket designed before any cut. No hatch, enemy or trigger is built by this drawing. The orange clearance ribbons in the original F04 drawing were not recessed-floor proposals: Screening remains level; the subsequent layout-10 decision also removes Registration's local lowered walkway.


## Texture transitions require geometry / current floor decision

User rule: a change in texture must be supported by actual geometry: a raised or lowered surface, a border brush, trim or a physical three-dimensional seam. An uninterrupted coplanar floor uses one continuous material. Colour alone should not introduce an arbitrary seam across that surface.

The user rejected replacing Registration's recessed path with a contrasting material strip. [Layout 10](freight-registration-flat-floor.md) removes the 0.25 m depression and its orange floor/step materials, bringing the former strips to 0 m under the existing dark floor texture. Registration and Screening now share the level-floor treatment. The furniture, door and back office remain. Use the established ribs, upper corners, compartment frames and service runs for the architectural theme; reserve height changes for purposeful platforms, stairs and mezzanines.
