# Freight access v2: the walkthrough in words

Status: **stage 1 approved with notes**, 2026-09-26 ("sounds amazing"). The user's notes are folded in below. **Stage 2, the 2D plan, is at revision 08:** [freight-v2-plan.md](freight-v2-plan.md) and `freight-v2-plan.png`, from `tools/freight_v2.py`. The user's revision 01 review added two filler rooms and a reason for the east stairs, and narrowed every stair. The user's sketch on revision 02 added the vent way back on the east, and their revision 03 notes made its corridor a bare duct and moved the fan. Their revision 04 sketch rerouted the crane catwalk through pass-through rooms to the pipe room's big fan, and their revision 05 sketch added the stair corridor and door 3 and moved the stair room's flight. Their revision 06 notes raised door 3 onto a Substation catwalk, made the fan a crouch-through, and replaced the booth panel with the pipe bay switches and the cage switch. Their revision 07 notes swapped switches 2 and 3 and settled the booth. This text matches revision 08. **Stage 3, the G-01 greybox of the whole level, is built and validated:** [freight-v2-build.md](freight-v2-build.md).

This mission replaces the freight blockout's floor plan entirely. The old plan
put an administration and security department behind a freight elevator, and
its rooms were huge halls with nothing in them. This one keeps the mission's
logic, which the user has already walked and liked for length. It rebuilds
every space as part of a **freight terminal**, using the rules the labs
established:
- the room recipe
- the junction rule
- the light floor
- the running elevation story
- texture choice and alignment

**Kept from the old mission:**
- The freight lift needs a **freight clearance card (K) AND auxiliary power
  (P)**, taken in either order.
- There are two branches from a hub, a far-side release that opens a
  shortcut, an optional secret or shortcut for knowing players, a quiet
  arrival, and the airlock and lift transitions.
- Pacing target: about ten minutes on a familiar run.

**Thrown away:** the floor plan, the room list, the admin and security
department, the enormous halls and every old dimension.

## Premise

Level 2 or 3. The player, colony security, arrives by airlock at the
**Freight Terminal**, the plant's goods-in level, to take the freight lift down
to the processing deck. The terminal took the first attack. The lift is dead:
its clearance lock has been reset and the auxiliary substation that feeds it
has tripped.

The discovery that the aliens have been here a long time is **not** this
mission's reveal. This level can hold optional clues for the attentive (old
sealed burrows in the pump pit, a container manifest with years-old
"quarantine" stamps). Nothing here states the reveal.

## Objective graph

```
Arrival -> Receiving -> Sorting Bay (hub: sees the dead lift and what it needs)
   |-- west: pipe run -> stairwell -> Logistics (K; archive holds the cage release) -- S1 --> bay
   |-- east: trench -> compressor U-turn -> Pump Room -> pit -> crawl -> Substation (P, card M)
   |           two ways back:
   |           vent: grill -> air duct hallway -> filter room -> ladder -> pipe room -> vent -> drop onto the dock
   |           S2:   east stairs -> lobby: card M opens S2 (back into the Pump Room) and the quarantine hold
   +-- north: Freight Lift, needs K AND P
Knowing player: pipe bay switch 2 + cage switch -> archive -> section (3) -> door 5 -> crane catwalk
   -> lift machine room -> jog corridor -> stair room
   -> along the stair corridor -> door 3 -> north catwalk -> P -> the vent way to the lift
   (or down the stair room -> fan chamber (lever stops the fan) -> crouch through the fan -> pipe room)
```

**Rules:**
- **K and P are both required, in either order.** Neither is behind its own lock.
- **Each branch ends in a far-side release** (S1 west, S2 east) that makes the
  way back short. A release opens from its objective side and stays open.
  S1 opens from Logistics once K is taken. S2, the Pump Room's east door,
  opens from the east stair lobby with **card M**, found beside P. M also
  opens the quarantine hold.
- **No stair without a reason** (user, revision 01 review). Every stair leads
  somewhere the player needs or wants to go.
- **Filler rooms** sit between the big rooms. Each has one idea: a machine,
  pipes, a crouch, a reward in view.
- **More than one way back** where it adds a place. The vent way is one way
  only (a drop), so it can never become a way in.
- **One crouch, then run.** A crouch is an entry (into a duct, under a pipe
  bank to a reward), never a toll repeated along a path. Extra crouches only
  add time.
- **Motion in the walls.** Beyond the compressor and the fan, small spinning
  bits and pumps can be set into the walls of other rooms during the detail
  pass.
- **Optional rooms and secrets** never gate completion.

## The locations

Each location lists its purpose, walk path, blockers, vertical move, secret,
wall idea, look and combat intent. Elevations are relative to the airlock
floor at 0. The walls are described last, as the recipe says.

The **five room studies** (marked ★) get built and walked on their own before
the level is composed. The remaining locations are connectors and small rooms
that grow from them.

### 0. Arrival airlock (0.0)
- **Purpose:** the occupied chamber cycles, and the far door opens once the
  level is ready.
- **Path:** straight through.
- **Look:** steel, with hazard trims round the door.
- **Combat:** none.
- **Later:** this becomes the standard reusable airlock (octagonal interior,
  level console, air-state floor light, cycle beacon, sound, the door
  sequence). See **FR-007**. The first build uses a plain chamber.

### 1. Receiving (−0.5)
- **Purpose:** a quiet foothold. The mission title shows here. The player
  orients before any pressure.
- **Path:** in from the airlock onto a **small landing**, then **two steps
  down** onto the floor, across the room and out north into C1. A second line
  runs round the parcel racks to a small side office.
- **Blockers:**
  - a decontamination arch just past the steps, which you walk through (a
    laser sweep comes later)
  - **a receiving desk with computer gear:** terminals, a scale readout and
    a label printer
  - a flush cargo-scale plate: a grate feature square one sill up, walked
    over rather than round
  - two parcel racks that make a short aisle
  - an abandoned pallet jack
- **Vertical:** the two steps down, and a raised scale-reader desk behind a
  half-height counter.
- **Secret:** none. It's the foothold.
- **Walls:** they wrap the racks tightly on the west side. A glazed booth pushes
  out on the east for the side office. The ceiling is lower (3.5 m) because
  this is a personnel room.
- **Look:** steel, with a warm office corner.
- **Combat:** none. Distant sounds from the bay only.

### 2. C1: Receiving to the bay (−0.5)
- **Purpose:** a P1 corridor, 11 m. Through the far junction the player
  glimpses the **lit freight lift cage** at the far end of the bay beyond: the
  landmark and the goal, seen early.
- **Path:** straight. The P1 ribs are on the 4 m beat. Mid-corridor, one
  fitting has **torn loose and hangs** from its cable. It's dead, not glowing,
  and **sparks flash** from the break. That's the first sight of damage.
  **Damage must always be visible like this**, never just a dark bay.
- **Vertical:** level. It ends on a **gallery landing** at the bay's south
  wall.

### 3. ★ Sorting Bay: the hub (gallery −0.5, floor −3.0, dock −1.75)
- **Purpose:** the heart of the level. From the gallery, the player sees the
  whole bay and the dead lift at the north end, with its display showing the
  **two missing requirements (K, P)**. Both branch entrances are identifiable
  from here: the pipe run in the west wall, and the service trench in the
  east wall beside the gallery.
- **Path:**
  - **Gallery to floor:** from the C1 landing, the player walks west along
    the gallery to a side stair on the west wall that goes **down 2.5 m**
    (10 risers) to the bay floor, beside the pipe run's mouth.
  - **The main line** crosses the floor north towards the dock, weaving
    through the conveyor lines.
  - **West** exits through the pipe run to the stairwell and Logistics.
    **East** exits through the trench to the compressor room.
  - **North:** a 3.5 m flight of five steps rises **1.25 m** onto the loading
    dock, where the lift waits.
- **Blockers:**
  - **Two conveyor lines** crossing east–west at waist height, with gaps where
    you can cross. They set the rhythm of the floor and give cover.
  - **Container stacks** (the corrugated texture belongs here), including one
    cracked open **from the inside**.
  - A glazed **sorting booth** raised 1.5 m in the west notch, tucked
    under the Logistics floor, with a six-riser side stair on its east face.
    Inside, at the glass over the conveyors, are **a seat with a console and
    a seat with a joystick**. It only has to look the part: nothing in the
    game is labelled, and props tell the story.
  - An **overhead crane** on a rail, with a container hanging from it.
- **Vertical:** the gallery, the floor, the dock, the booth, and the crane rail
  high above. Sightlines run between them.
- **Secret:** a **crawlspace inside the conveyor platform** (the south
  line's east half), entered through a maintenance gap: ammo. Both conveyor
  lines leave 2.5 m gaps at the ends and in the middle, so bugs can flank
  as well as the player.
- **Walls:** a long bay, its length following the conveyor. It bulges east
  at the trench mouth and notches west where the booth stands. The
  north end is the dock face. Portal frames on the 4 m beat carry the crane
  rail. **It is not a rectangle.** The dock, the booth bay and the trench mouth
  each push the perimeter.
- **Look:** freight: concrete floor, corrugated containers, steel structure,
  hazard trims on the dock edge.
- **Combat:** the first real fight, with arrivals from the cracked container
  and the trench. Cover comes from the conveyors and containers, and the
  gallery is a fall-back. **The trigger is the whole bay floor**, so no route
  into the bay can miss it or set it off at a different time. The lift
  display is readable from the gallery before the player steps down.

### 4. Pipe run west (−3.0), a filler
- **Purpose:** the first **filler**: a short P2 corridor out of the bay's
  west wall that is not just a corridor. It is a hallway with an extension.
- **The extension (the pipe bay):** a side bay off the south wall with a
  bank of pipes running straight through it at crouch height, **1.2 m clear
  underneath**. Looking under the pipes you see the far side, where an
  **ammo container** sits against the back wall. Crouch under to reach it.
  It is a reward in plain view, not a secret.
- **The switch panel** (user, revision 06 notes): three switches on the back
  wall beside the ammo, behind the pipes, as in the original freight design.
  - **Switch 1** sparks and does nothing.
  - **Switch 2** opens **door 5**, high in Logistics' east wall, where the
    crane catwalk leaves for the bay (21). You hear only a distant clunk.
  - **Switch 3**, the last one: you hear a door nearby. **Door 1** in the
    stairwell's ground landing opens onto the secret closet (5).
  - Switch 3 is last on purpose (user, revision 07 notes). A player who stops
    once the catwalk door has clunked open may never find the closet.
- **Path:** 10.5 m, level, from the bay to the west stairwell.
- **Look:** steel service corridor. The pipes carry the machinery colour
  into the admin side.

### 5. West stairwell (−3.0 → +1.0)
- **Purpose:** the climb to Logistics, in its own stairwell. Revision 01
  used a 6 m-wide stair corridor here, and the user called it massive. Every
  flight in the level is now **3 m wide** (3.5 m at most) inside a stairwell
  that wraps it.
- **Path:** in from the pipe run onto a ground landing, then **8 risers up**
  along the west wall, a turning landing at −1, **8 risers up** along the
  east wall, and a top landing at +1 with a door east into Logistics.
- **Walls:** they wrap the two flights and their landings in a zigzag. The
  space beside each flight is solid, not a void.
- **Vertical:** the view up the stairwell from the ground landing, and down
  it from the turning landing.
- **Secret:** **door 1** in the ground landing's south wall, opened by switch
  3 in the pipe bay, leads to a small **secret closet** with armour and
  health on its shelves.

### 6. ★ Logistics office (+1.0; archive +4.0)
- **Purpose:** freight dispatch, and **the card K**. K is in the dispatch
  supervisor's cage: a caged office inside the room with a locked gate.
- **Path:**
  - In through the **west door** from the stairwell, into the aisle between
    two desk rows, then along an **L-shaped** office that wraps the
    **overlook window above the Sorting Bay**. The bay floor is 4 m below.
  - Between desk rows to the cage, which is locked.
  - The cage release is up in the archive: a **ladder of 12 rungs up 3 m** in
    the north corner.
- **Blockers:**
  - desk rows with terminals, a dispatch counter along the window, lockers
  - the supervisor's cage
  - a toppled filing cabinet partly blocking one aisle
- **Vertical:** the ladder up to the archive at +4.0. From the archive, the
  cage roof is visible below through grating.
- **Archive (the Records role):** tight rolling-shelf stacks that make a
  **small maze** (four aisles, one blocked by fallen shelving), with the cage
  release at the end.
- **Secret:** in the archive, a locked drawer bank with health. It opens with
  a desk code seen on a note in the office.
- **Walls:** the L follows the overlook window. The inner corner is filled
  by the cage, and the archive sits on top of the cage's back office. There
  are low ceilings over the desks (3.5 m) and a double-height slot at the
  ladder.
- **Look:** the admin subset: warm tan office, a dark carpet-plate floor.
- **Cage switch:** inside the cage, beside K, a switch **lowers the raised
  catwalk section (3)**. Hinged at door 5, it stands at 90° against
  Logistics' east wall high above the desks, and you watch it swing down. The
  archive lever still opens the cage.
- **Combat:** a mid-sized fight among the desks, which triggers when the cage
  opens. Bugs come through the overlook window from the bay side.

### 7. S1 release and the return west (+1.0 → −3.0)
- **Purpose:** with K collected, a door beside the cage (**S1**) opens from
  this side onto a **3 m service stair straight down the bay's west wall**.
  The way back is 20 seconds instead of retracing the stairwell and the pipe
  run.

### 8. Service trench east (−3.0)
- **Purpose:** the connector towards power. It leaves the bay's south-east
  corner, jogs south and runs east, level, into the compressor room. The
  steps down moved into the compressor room, where they make a story.
- **Its identity (not a tumour):** one whole wall of **pipes running its
  length** in a recess, with a valve wheel station half way. The pipes lead
  the eye on.

### 9. Compressor U-turn (−3.0 → −4.0), a filler
- **Purpose:** the second **filler**, and literally a U-turn round a
  machine. A big **air compressor** fills the middle of the room. Its
  **piston rises and falls** through a housing to the ceiling, the one moving
  thing in the level so far, with its sound and a pumping light.
- **Path:** in from the trench onto an entry landing (−3.0), **two steps
  down** to the south lane (−3.5), east along the machine, round its far end,
  **two more steps down** (−4.0), and back west along the north lane to the
  door into the Pump Room. This is the user's example sequence: two steps
  down, round a machine, back the way you came, two more down.
- **Blockers:** the compressor, and a **pipe manifold wall** (the spine) from
  the west wall to the machine, which makes it a real U: you cannot cut
  across the west end.
- **Walls:** they wrap the U. The corners at the far end are chamfered round
  the turn.
- **Look:** machinery: steel, dark pipes, the pumping light.
- **Combat:** none planned in this pass. On the way back it is a natural spot
  for a return ambush (the enemy pass decides).

### 10. ★ Pump Room (walkway −4.0, pit −5.5)
- **Purpose:** the plant's coolant pumps. You pass through on the way to
  power. The **east door (S2)** is locked, with a wired-glass window showing
  a stair lobby beyond: the easy way back, not yet yours.
- **Path:**
  - In from the compressor room onto the south side of a **walkway ring**
    round a sunken pit where **three big pumps** stand.
  - Across the pit on a **catwalk bridge** to the east door, which is locked.
  - The real way on: **down a ladder into the pit** (1.5 m), past the pumps,
    and out through a low pipe gallery on the pit's north side.
- **Blockers:** the three pumps and their pipework, rising from the pit to the
  ceiling and into the wall. The ring rail. Valve stands.
- **Vertical:**
  - The pit is below the walkway.
  - **The bridge is a box girder with a maintenance crawl inside, reached
    by a short ladder beside the locked east door: the ammo secret** (the
    user's example). The newcomer's dead end rewards the curious.
  - The pit's south strip, beside the bridge, is a glowing coolant channel
    that cannot be walked on.
  - The pipe gallery leaves the pit on the north.
- **Clue (optional):** in the pit wall, an old sealed burrow behind a
  concrete patch.
- **Walls:** the room bulges round the pit. The walkway ring decides the inner
  perimeter, the pumps' pipes push niches into the north wall, and the pit
  corners are chamfered. The ceiling is tall because the pumps are tall.
- **Look:** machinery: steel, dark pipes, coolant glow in the pit.
- **Combat:** bugs climb out of the pit onto the ring. The bridge is the
  exposed crossing. The trigger spans the whole south walkway, the only way
  in on a first visit.

### 11. Pipe gallery (−5.5 → −2.5)
- **Purpose:** a low, **crouch-then-climb** connector. It starts as a
  pipe crawl (crouch, 1.1 m) and ends at a **ladder of 12 rungs up 3 m**.
- **The only way to power on a first visit.** The larger bugs cannot follow
  through the crawl.

### 12. ★ Substation (floor −2.5, gantry +1.0)
- **Purpose:** auxiliary power, **P**, and the **maintenance card M**. A
  **row of transformer cages**, a **cable trench** down the middle (grate
  feature squares over it), and the **restore switch on a gantry**.
- **Path:**
  - Up out of the pipe gallery onto the floor.
  - Along the cage row, past the cable trench.
  - Up a **side stair (3.5 m wide)** onto the gantry. Its corner holds a
    small control booth with **card M** on the desk.
  - Along the gantry to the switch. Restoring power: **the substation lights
    come on bank by bank** and the lift display in the bay updates.
  - **Two ways out:** the grill low in the west wall (the vent way), or the
    gantry's east end to the **east stairs** (the hold and S2).
- **The gantry is a U** (revision 07). A **north catwalk** runs along the
  north wall above the cage row and the alley behind it. It joins the east
  arm to **raised door 3** in the north-west corner.
  - A **ladder of 14 rungs** drops from the catwalk to the floor near the
    grill.
  - Arriving by door 3, you walk the catwalk to P and take the ladder down to
    the vent way.
- **Blockers:** transformer cages (fenced, and you see through them), the
  trench, and a fallen cable tray you step over.
- **Vertical:** floor, trench, the U gantry and its ladder.
- **Secret:** along the alley behind the cage row, then down a ladder into a
  cable vault behind the last cage: armour or health.
- **Walls:** a long room shaped by the cage row. It is taller on the cage side
  and lower where the gantry runs, and the trench drives its centre line.
- **Look:** machinery, dimmed before the restore and lit after.
- **Combat:** the power fight. Restoring power is the trigger. The gantry
  gives a height advantage, and the cages give cover.

### 13. Substation grill and the air duct hallway (−2.5 → −3.0)
- **Purpose:** the start of **the vent way back**, the second way out of the
  Substation (user sketch, revision 03). It is another path, not
  necessarily a quicker one.
- **Path:**
  - A **grill low in the Substation's west wall**. Interact to slide it open
    and **crouch through** (1.2 m clear).
  - Behind it is an **air duct hallway** running south beside the pipe room:
    cramped, 2 m wide, and you run it after the one crouch.
  - Two steps down at the far end into the filter room.
- **Look:** bare metal siding and basically zero detail, only a **tiny rib
  every 2 m** where the steel sheets join (user, revision 03 notes). It is a
  new narrow duct profile for the kit.

### 14. Filter room (−3.0), a filler
- **Purpose:** the plant's air filtration. The idea is the **filter banks**:
  big ribbed housings along the south wall, and a **blower** that pushes the
  north wall out into a niche.
- **Path:** in at the north-east corner, west along the aisle between the
  filter banks and the blower, and out at the north-west into the ladder
  room.
- **Clue (optional):** the filters are clogged with old organic matter.
  Years of it.
- **Walls:** they wrap the banks and the blower. The corners are chamfered and
  the north wall jogs round the blower.
- **Look:** machinery steel, with the low hum of the blower.

### 15. Ladder room and the pipe room (−3.0 → 0.0), a filler
- **Ladder room:** a small room off the filter room. A **ladder of 12 rungs
  up 3 m** goes through a hatch into the pipe room.
- **Pipe room:** its purpose is the pipes (user sketch).
  - **Pipes come up out of the floor, turn and run into the walls.** Three
    turn east, two turn west, and one big riser goes straight up through the
    ceiling.
  - **A pipe rack runs the length of the room** along the east wall.
  - The route weaves between the risers and round a valve manifold towards
    the north end.
  - **A big fan**, 3 m across with three blades, is set **centred in the
    north wall** between the chamfered corners. **Its blades turn slowly**
    with light behind them, and you see it just before you crouch into the
    vent in the north-west corner: a screenshot moment. From this side it
    only turns. It is stopped from the fan chamber behind it (25).
- **Walls:** they wrap the pipes. The chamfered corners are where the pipes
  turn into the walls.
- **Look:** machinery, dark pipes and moving fan light.

### 16. The vent and the drop (0.0 → −1.75)
- **Purpose:** the end of the vent way.
  - A **short vent duct** (crouch) leads west from the pipe room to a
    grille high in the dock's east wall.
  - Open the grille and **drop 1.75 m onto the dock**, beside the lift.
  - It is **one way**: nothing climbs back up.
- **Why it matters:** from P to the lift it is 114 m by the vent and 167 m by
  S2. More importantly, it is another path. A **completionist doubles back**:
  down the east stairs for the quarantine hold, back up the stairs, then out
  by the vent.

### 17. East stairs and the stair lobby (+1.0 → −4.0)
- **Purpose:** the stairs now have a reason. The user's rule: **a stair
  that nobody needs should not exist**. From the gantry's east end, a **3 m
  service stair drops 5 m** (10 risers, a landing, 10 risers) to a small
  lobby at the Pump Room's level.
- **The lobby has two locked doors, and card M opens both.**
  - **S2**, the Pump Room's east door, seen locked from the bridge: the easy
    way back.
  - **The quarantine hold** to the south: a room you could not know about
    until now.
- **Why the player comes this way:** the stairs are the only way to the
  quarantine hold, and S2 is the way back to the Pump Room and the bay. The
  vent way is the other exit from the Substation.

### 18. Quarantine hold (−4.0 → −4.5), optional
- **Purpose:** a reward room and the level's strongest optional clue.
  Freight that was held in quarantine, and never released.
- **Path:** in from the lobby onto a landing, **two steps down** into the
  hold, along the aisles between the containers to a **supply cage** at the
  far wall (armour and ammo).
- **Blockers:** two sealed quarantine containers, and a third **burst open
  from the inside long ago**: the edges are old and corroded, not fresh.
  The supply cage.
- **Clues (optional):** quarantine stamps years old, and a burrow in the
  floor patched with concrete long ago. Nothing states what they mean.
- **Look:** freight concrete, corrugated containers, one cold light.
- **Combat:** none planned. The enemy pass may put something in the burst
  container's shadow.

### 19. S2 and the return east (−4.0 → −3.0)
- **Purpose:** through S2 back into the Pump Room, across the bridge, and
  back through the compressor U-turn (two steps up, round the machine, two
  steps up) and the trench to the bay. From the bay, the dock steps lead to
  the lift. Revision 01's separate S2 corridor to the dock is gone: the east
  release is now the Pump Room's own door.

### 20. ★ Freight lift lobby and loading dock (dock −1.75, truck bay −3.0)
- **Purpose:** the exit. The **lift cage** is the focal point. The lobby wraps
  round its gate, with the display, a call panel and freight gates.
- **Path:** up the **dock steps** from the bay (a 3.5 m flight of five
  risers), along the dock to the lift gate. The **dock edge drops 1.25 m to a
  truck bay** on one side, with a stair down.
- **Blockers:** loading-dock bollards, a stack of pallets, a parked cargo
  hauler in the truck bay (cover). The truck bay's sealed roll door is where
  the final hold's bugs break in.
- **Vertical:** the dock edge, the truck bay below, and the lift shaft going
  down.
- **Walls:** the lobby wraps the lift. The dock edge is open to the bay. The
  truck bay has its own lower roof.
- **Look:** freight, with hazard trims on the dock edge, the only large use
  of hazard, and only as edge trim.
- **Combat:** the final hold. When K and P are both set, the lift is called
  and takes some seconds to arrive, and bugs arrive from the truck bay and
  the bay.

### 21. Crane catwalk (+4.0), the knowing player's way east
- **Purpose:** a high way from the west to the Substation, rerouted by the
  user's sketches on revisions 04 and 05. It skips the trench, the U-turn,
  the Pump Room and the crawl ("the hubbub"), and passes through its own
  rooms instead.
- **Light on enemies** (user): the northern route is fast in time even where
  it is not much shorter in metres.
- **Mechanical movement, not a lock** (user, revision 06 notes).
  - A first-time player who finds the shortcut is welcome to skip the east
    side. It takes two things:
    - **Switch 2** in the pipe bay opens **door 5**.
    - **The cage switch** lowers **section (3)**, the catwalk's last 5 m
      before door 5, from 90° to flat.
  - Without either, the catwalk ends at a gap or at a shut door. The booth's
    crane panel is gone.
- **Path:** out of the archive at +4, over the Logistics desks, across
  section (3) and through **door 5** in Logistics' east wall. Then high over
  the bay's north end, and **north out of the bay** over the dock's west end
  into the lift machine room.
- **Look:** a railed steel grating with the bay 7 m below: a view of the hub
  from above.

### 22. Lift machine room (+4.0), a pass-through
- **Purpose:** the freight lift's machinery, beside the top of its shaft.
  You enter from the catwalk and walk straight through, east.
- **Blockers:** on your left as you walk, two **hydraulic pumps** and a
  control cabinet. They stand dead until power is restored.
- **Walls:** they wrap the pumps. The north-east corner is chamfered round
  the second pump.

### 23. Jog corridor (+4.0)
- **Purpose:** a short 3 m service corridor with **one jog** in it, so it
  never reads as a long straight (user sketch).

### 24. Stair room (+4.0 → 0.0), the fork
- **Purpose:** the catwalk route's choice point. It is a top landing with two
  ways on:
  - **Along:** straight on from the landing into the stair corridor (25), the
    fast way to P.
  - **Down:** a **16-riser flight** along the room's **east** wall to the
    floor.
- **At the bottom of the flight you turn left and go straight out** through
  the door to the fan chamber (26).
- **The pickups are behind you to the right**, under the top landing, at the
  end of the room's west strip. You only find them if you turn right and go
  and explore (user, revision 05 sketch). With the flight on the west wall,
  as in revision 05, they were in view as you left the stair.
- **Walls:** they wrap the flight, the floor strip beside it and the landing.
  The jog corridor was moved north to meet the landing.

### 25. Stair corridor and door 3 (+4.0 → +1.0)
- **Purpose:** the shortcut into the Substation (user sketch). From the
  stair room's top landing it runs east, then turns 45° south-east to
  **door 3** in the Substation's north-west corner.
- **Vertical:** **one 12-riser flight** down 3 m in the east leg.
- **Door 3 is raised** (+1, user) and opens onto the Substation's new
  **north catwalk** (12).
- **Door 3 opens only from the corridor side**, then stays open. On a first
  visit from below it is a locked door high in the Substation's corner.
- **Distance:** from K to P it is 108 m this way, against 215 m down through
  the fan and along the duct.

### 26. Fan chamber and the big fan (0.0)
- **Purpose:** the back of the pipe room's **big fan**, **3 m across**,
  with its drive and a **lever**. It is a small chamber (user: no huge
  rooms). You reach it through the door at the foot of the stair room's
  flight.
- **The moment:** pull the lever and the fan **spins down and stops, one
  blade pointing up**.
  - Between the two lower blades there is a gap about 1.1 m wide at the top
    of a crouching player (1.35 m), and the hub clears it.
  - **Step over the 0.25 m lip and crouch through the blades** into the pipe
    room.
  - `freight_v2.check()` verifies this geometry.
- **One way:** from the pipe room the fan is only a spinning disc, solid
  while it runs, and there is no lever on that side. Once stopped it stays
  stopped, so after that the catwalk rooms connect both ways.
- **It is the explorer's branch now.** The fast way to P is the stair
  corridor. The fan route is for the pickups and the fan moment, and it
  reaches the pipe room, the vent and the lift.
- **Behaviour:** running, spinning down and stopped belong to the fan's
  StateChart. Its collision is solid while it turns, and becomes the stopped
  blades once it stops.

## The elevation story (a running tally)

| Step | Where | Change | Height |
|---|---|---|---:|
| 1 | Airlock → Receiving | landing, two steps down | −0.5 |
| 2 | C1 → gallery | level | −0.5 |
| 3 | Gallery → bay floor | side stair, 10 risers down | −3.0 |
| 4 | Pipe run | level; crouch under the pipes for the ammo | −3.0 |
| 5 | West stairwell | 8 up, landing at −1, 8 up | +1.0 |
| 6 | Logistics → archive | ladder, 12 rungs | +4.0 |
| 7 | S1 service stair | 16 risers down to the bay | −3.0 |
| 8 | Trench → compressor U-turn | two steps down, round the machine, two more down | −4.0 |
| 9 | Pump pit | ladder, 6 rungs down | −5.5 |
| 10 | Pipe gallery | crouch crawl, then ladder, 12 rungs up | −2.5 |
| 11 | Substation gantry | side stair, 14 risers up | +1.0 |
| 12a | Vent way: grill, air duct hallway | crouch through, two steps down | −3.0 |
| 12b | Vent way: ladder room → pipe room | ladder, 12 rungs up | 0.0 |
| 12c | Vent way: vent → dock | crouch, then drop 1.75 m | −1.75 |
| 13 | Or the east stairs | 10 down, landing, 10 down | −4.0 |
| 14 | Quarantine hold (optional) | two steps down | −4.5 |
| 15 | S2 → Pump Room → U-turn → trench | two steps up, round the machine, two steps up | −3.0 |
| 16 | Dock steps | five up | −1.75 |
| 17 | The lift | down to the processing deck | — |
| K1 | Knowing player: archive → crane catwalk | level, high over the bay | +4.0 |
| K2 | Lift machine room → jog corridor | level | +4.0 |
| K3 | Stair corridor → raised door 3 → north catwalk | 12 down | +1.0 |
| K3a | North catwalk → ladder → Substation floor | ladder, 14 rungs down | −2.5 |
| K4 | Or the stair room | 16 risers down; the pickups behind you, to the right | 0.0 |
| K5 | Fan chamber → through the stopped fan | step over a 0.25 m lip | 0.0 |

The biggest swing is the Logistics archive at +4.0 against the pump pit at
−5.5. That 9.5 m is felt through ladders and stairs, and the hub is seen from
the gallery, the overlook window and the crane catwalk.

## Routes to check in the 2D plan

1. **Card first, vent return:** receiving → bay → pipe run → stairwell → K
   → S1 → trench → U-turn → Pump Room → crawl → M, P → grill → filter room
   → pipe room → vent → drop → lift.
2. **Power first, S2 return:** receiving → bay → trench → U-turn → Pump Room
   → crawl → M, P → east stairs → hold → S2 → U-turn → bay → pipe run →
   stairwell → K → S1 → lift.
3. **Completionist:** card first, then after P down the east stairs to the
   hold, back up the stairs, and out by the vent.
4. **Knowing player, catwalk to P (362 m):** receiving → bay → pipe run
   (switch 2) → stairwell → archive lever → K and the cage switch → back up
   to the archive → section (3) → door 5 → crane catwalk
   → lift machine room → jog → stair room → along the stair corridor → door 3
   → north catwalk → P → the vent way → lift. It skips the trench, the U-turn,
   the Pump Room and the crawl.
5. **Catwalk explorer (482 m):** the same, plus switch 3 and the secret
   closet, then down the stair room (the pickups behind you) → fan chamber →
   lever → crouch through the fan → pipe room → filter room → duct → grill →
   M, P → the vent way → lift.
6. **Newcomer mistakes:** trying the Pump Room's east door (locked, a window
   shows the stair lobby; the pit ladder is the way on, and the bridge-crawl
   secret is beside the door), and trying the lift early (the display
   explains what's missing).

## Screenshot moments (the postcard test, planned in)

1. The gallery reveal of the Sorting Bay: conveyors, containers, the crane,
   and the lit lift cage at the far end.
2. The Logistics overlook: a warm office in the foreground, the industrial bay
   below.
3. The compressor round the U: the piston pumping, pipes and the pumping light.
4. The pipe room's box fan in the north wall, light behind its slow blades,
   just before the vent.
5. The pump pit from the bridge: coolant glow, pipes rising into darkness.
6. Power restored: the substation lights coming on bank by bank.
7. The lift doors closing on the dock.
8. The big fan spinning down and stopping, then the crouch through its blades.
9. Section (3) of the catwalk swinging down from 90°, seen from the cage.

## Texture pack this level produces

**Freight & Processing**, with an **office subset**:
- concrete floors
- corrugated container sides and roll doors
- steel structure
- hazard only on dock edges and door trims
- machinery pipes and pumps
- the warm tan office set for Logistics

## Open questions for the user

1. **The five room studies:** Sorting Bay, Logistics (with its archive), Pump
   Room, Substation, Lift Lobby. Should the compressor U-turn or the pipe
   room replace one?
2. **Duration:** revision 08 measures 436 m (card first by the vent), 514 m
   (power first by S2), 535 m (the east completionist), 362 m (the knowing
   player) and 482 m (the catwalk explorer). Measure it on the empty walk.

**Decided:**
- No new enemy or weapon for this level yet (user, revision 03 notes).
- One big fan you crouch through (user, revision 06 notes).
- Skipping the east side through the catwalk on a first run is welcome.
- The archive lever opens the cage.
- The switch chain (user, revision 07 notes):
  - Switch 1 sparks.
  - Switch 2 opens the distant door 5.
  - Switch 3 opens the nearby secret door 1.
  - The cage switch lowers section (3). Its hinge side does not matter; it is
    drawn at door 5.
- The sorting booth stays, as a booth that looks the part.
