# Red Breach architecture language

Standing design rules from the user, gathered from the first freight mission's walkthroughs (2026-09-20 on), the
labs and freight v2. They guide every paper plan and blockout. Values labelled proposed are starting points for
review. These are game-space guidelines, not real-world construction standards.

## Colony identity

Design a working, pressurized industrial colony on Mars. Rooms should communicate their function through proportions, equipment, circulation and connections. Staff spaces feel different from machinery halls. An unusually tall volume needs a visible reason: large equipment, overhead handling, occupied upper floors or a deliberately important overlook.

## Rules established by the user

### Doorways have room around them

Avoid perpendicular door openings that meet at the same thin wall tip or edge. Give each opening a solid wall return, frame depth and clear approach. A T-junction itself can be useful; frame its branches deliberately, with doors set back from the junction or a small shared lobby.

Proposed starting dimension: aim for at least **1 m of solid wall beyond a doorway frame before an adjoining opening or corner**, increasing it where doors, readers or movement need more space. Check the outside of the frame, not just opening centre coordinates. Maintain clear passage through the opening and room for its motor/pocket. Do not narrow the tested gates to create the return without explicitly reviewing that change.

### Every room owns its walls — no shared wall brushes

User rule, 2026-09-22: a room's walls belong to that room. Minimum **0.25 m
thick per side**, so **0.5 m of solid between any two interior spaces**. Two
rooms never share one wall brush.

**Why:** a shared wall can only carry one material. Separate walls let each
room texture its own side, and leave depth for trim, a projecting rib or a
service box to stand proud of the surface without punching into the
neighbouring room. Sharing also reads cramped.

**How to apply:** when drawing or building, inset each space 0.25 m from its
plan boundary; adjacent spaces then automatically leave the required 0.5 m.
0.25 m = 8 map units and 0.5 m = 16 at 32 units/metre, so both stay on the
0.125 m construction increment used everywhere else. Exterior shell walls can
be thicker. This is a minimum, not a target — widen where services, ribs or
recesses need the depth.

### A room's contents define its shape

User rule, 2026-09-25: never define rooms by a stock shape ("halls are
knee-wall naves", "rooms are octagons"). First build out what is in the room:
its equipment, the work it does, its circulation and its sightlines. Then let
those define the perimeter and the wall shape. A shape that worked in one room
is a record of that room, not a template. Corridors and junction pieces are
kit; rooms are composed.

### No darker than the light floor

User rule, 2026-09-25: by default every walkable space meets a minimum
brightness. Go darker only on purpose, for a hiding place or broken lights,
and mark it with an `rb_dark` zone in the map. The generic validator measures
this (scalar illuminance at bug height across the navigation mesh, floor 0.35;
see `kit-sheet.md`), so dark corners are found by the checks rather than on a
walkthrough. Undersides of catwalks, stair feet and the far ends of halls are
the usual offenders.

### Textures: tile where it repeats, feature where it does not, seams on geometry

User rules, 2026-09-25:
- **A texture that does not tile must never be used where a surface
  repeats.** A heat pipe that runs dark to bright and then repeats reads as
  broken. Each texture's tiling is measured (`tools/audit-textures.py`), each
  role declares what it needs, and the build refuses a mismatch.
- **Busy textures are features, not covers.** Use one or two squares of the
  dotted grate as a highlight, with an elevation change where the texture
  changes, rather than laying it over a whole floor.
- **Seams belong on geometry.** Texture panels start at corners, segment
  edges and rib stations, floors are centred on the corridor and follow it,
  and features are fitted whole to their face.

### A corridor meets a room through its own profile

User rule, 2026-09-26: no flat accent slab around a corridor opening. Cut the
room wall to the corridor's profile, run the corridor to the room's inner
face, and let the corridor's rib stand at the room face as the connection. A
door fills the opening with a panel shaped to the profile. A room lower than
the corridor gets a door-sized hole, and the corridor ends in its rib. A
change of look happens at that rib and a low sill.

### Vertical interest is a running elevation story

User rule, 2026-09-26: vertical interest is not only big stairs and
mezzanines. One or two steps down into a room count. So do a staircase, and a
ladder into a well with a hidden secret. The elevation changes accumulate
along the route as a story the player feels, for example:

> Walk into a room and take 2 steps down. Walk forward round a machine and
> come back the way you came, 2 more steps down. The next corridor carries a
> 4-step drop. In the next room a 10-rung ladder goes up, and now you are at +6.

Plan every room and connector with its entry and exit elevation, and keep a
running tally along the walkthrough so the net change is deliberate. Small
changes make texture changes legal (a step is geometry) and give fights
height differences without mezzanines.

### Damage is visible, and triggers cannot be missed

User rules, 2026-09-26:
- **Damage must be seen**, not just a dark bay: a fitting hangs torn loose on
  its cable, dead and not emissive, with sparks flashing from the break.
- **An encounter trigger must be impossible to miss.** Size it so every path
  into its space crosses it (a whole room floor, or the full width of every
  entrance), so it can neither be skipped nor fired late from an unexpected
  angle.

### Stairs have a width and a reason; filler rooms carry one idea

User rules, 2026-09-26 (freight v2 plan, revision 01 review):
- **A flight is 3 m wide, 3.5 m at most**, in a stairwell or along a room
  side that wraps it. A stair never fills the full 6 m width of a corridor;
  that read as massive next to every other stair. One or two steps may still
  span a room or a corridor.
- **No stair without a reason.** A stair that exists only as an alternative
  nobody needs should go. Give its landing a room, a reward or the only way
  on.
- **Filler rooms** sit between the big rooms, each carrying one idea:
  - a hallway with an extension where pipes cross at crouch height, with a
    reward in view beyond them
  - a U-turn round a moving machine
  
  They are how a level grows, instead of long empty corridors.
- **One crouch, then run** (freight v2 revision 03 notes). A crouch is an
  entry, into a duct or under a pipe bank to a reward, never a toll repeated
  along a path: a second crouch in the same passage only adds time. After
  the crouch, a duct hallway is bare steel siding with basically zero detail,
  only a tiny rib at every 2 m join.
- **No labels in the game** (freight v2 revision 07 notes). A room's job is
  read from its props, such as a seat with a console or a seat with a
  joystick, never from a sign saying "crane operator". Plan names are for
  the plan only.
- **Motion in the walls.** Moving machinery is cheap interest: a piston, a
  slow box fan, and small spinning bits and pumps set into the walls of
  ordinary rooms.

### Rib feet come straight down

User rule, 2026-09-25: a structural rib does not step out at its foot the way
a wall plinth does. Copying the plinth offset leaves a jagged notch. The rib's
inner face drops vertically to the floor, flush with the rib above, so the
member reads as one piece standing on the floor.

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

These are candidates, not a universal ceiling flattening operation. Include door frame and header depth when lowering the ceiling around a doorway. Review ceiling changes in section alongside slabs, stair headroom and the actual standing capsule. Decorative ducts and beams must not silently consume the required clearance.

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

## Functional furnishing

Block rooms out with primitive desks, chairs, counters, cabinets, racks, pumps, machinery, ducts and supply-container shapes, in the look textures. Give them actual dimensions and simplified collision appropriate to traversal. Final asset selection and small decorative details can follow later.

Start with the work the room performs, then place its equipment and staff access. Consider entry views, ways around equipment, retreat space and where combat might occur. Mark likely supply and encounter locations on paper while arranging the furniture; actual ammunition quantities and enemy deployment remain a separate balancing pass.

Keep primary routes, stair landings and readers usable. Avoid a repeated slalom of crates placed solely to consume walking time. Chairs and small floor clutter should not snag the player's retreat; decide deliberately which pieces are movement blockers and which are visual placeholders. Preserve useful empty floor around future encounters and enough space for the larger bugs.

## Rules carried from the first freight mission

The first freight mission (layouts 06 to 12) was replaced by freight v2 and removed in the cleanup of 2026-09-26. Its
build records are in git history. These are the rules it established.

### Complete compositions, not scattered props

Design a focal assembly together with its working space and supporting architecture: a registration desk comes with
staff space, terminals, storage, a canopy and task lighting. Reserve walk and retreat routes through occupied
surroundings. Staff, industrial and service spaces should read differently even before final materials. (The later
QUOD direction puts shape over prop count; the composition rule still holds.)

Authoring workflow: TrenchBroom for room and route architecture, reusable Godot scenes for simple prop assemblies, and
Blender meshes later for refined repeatable furniture and equipment, keeping placement, units and useful collision.

Return the player to a familiar room from another elevation after travelling through other rooms (FR-005). A direct
stair inside that room is optional.

### The pressurized-colony profile

Block the major architecture in early, because it takes up space and affects sightlines:
- ribs
- substantial compartment frames
- angled upper corners
- service trunks
- visible light housings

Fine trim, panel seams, bolts, small pipes, wear and finished meshes come later. Keep straight lower walls where
furniture needs them; an outer pressure shell does not require every internal partition to slope. Staff areas
conceal more services, and industrial areas expose heavier framing.

Detail rules from the quality pass:
- Split ducts at partitions or ceiling-height changes.
- Mount suspended light housings to real overhead structure.
- Keep furniture out of secondary crossover routes.
- Physically offset competing trim faces, or make true butt joints: never coplanar faces.

### Reserve bug-entry hatches during blockout

Preserve places for large bug-entry hatches in ceilings, selected walls and suitable floors while composing each
space. Encounter tuning can come later; the physical entry points cannot wait until every surface is full of
cabinets, ducts or lights.

Reserve the whole emergence arrangement on the room plan:
- the aperture and its grate travel
- the sealed service or staging space behind it
- an unobstructed drop or emergence volume
- landing space
- an enemy-sized route into the fight

Size these for the largest intended bug, then validate its real collider and navigation. Check above, below and
behind against adjoining rooms, upper routes and the pressure envelope. A hatch opens into an enclosed service space,
never straight onto Mars.

- **Ceiling hatches** go between ribs and fixtures, above useful landing space.
- **Wall hatches** need a real service pocket behind them and room in front.
- **Floor hatches** sit beside the main route, with a flush closed surface. Never put one on the only retreat path or
  on a stair or door landing.

Small ventilation slots are not automatically large enemy entrances. The encounter lessons (triggers that account for
engaging from outside and backing away, response time, a hatch cue, deferred emergence, cancellation on
reset/death/exit) are in [combat-gym.md](combat-gym.md#bug-roster-and-lessons-from-the-encounter-route-trial).

### Texture transitions require geometry

User rule: a change in texture must be supported by actual geometry: a raised or lowered surface, a border brush,
trim or a physical three-dimensional seam. An uninterrupted flat floor uses one continuous material. Colour alone must
not introduce an arbitrary seam, and a painted walkway strip is not a substitute for a real level change (the user
rejected exactly that). Save height changes for purposeful platforms, stairs and mezzanines.
