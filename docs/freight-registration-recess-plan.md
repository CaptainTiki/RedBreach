# F-03c / Registration walkway and back office

> Floor treatment superseded by [layout 10: continuous flat floor](freight-registration-flat-floor.md). The recessed/orange walkway below is historical; staff-door, furniture and non-floor palette decisions remain.

Status: **approved and built as freight layout 08**. Project version remains 0.0.009; no commit was requested.

[As-built plan](freight-registration-recess-plan.png) | [Editable drawing](freight-registration-recess-plan.svg) | [Dimensions](freight-registration-recess-plan.json) | [Player-eye views](freight-registration-recess-built.png)

## User direction and final choice

The user likes F-02's registration arrival, exterior view and lighting. They requested a shallow circulation-level change, enclosed staff access and a back office instead of the sparse window lounge. Their [redlined route](references/f03-walkway-annotation.png) simplified the proposal to straight runs and square turns. They then [flagged the staff chairs](references/f03-staff-branch-feedback.png), delegated the choice to shorten or narrow that branch, and explicitly authorized construction.

The built choice **ends the recessed staff branch two metres before the door**. The landing, doorway and desk bay remain at floor 0, keeping the step away from chairs. The long strip continues through waiting and the office entrance at -0.25 m, with a short perpendicular office branch. Four rectangular strips define the floor, with no additional counter spur.

## Walk and floor levels

Enter from the hub, step down 0.25 m, walk straight and turn into the long strip. Step up from its side toward Screening, or follow it through waiting to Registration Operations. The staff branch leads to its level landing and door. Continue on the lower floor through the office entrance and turn into its short branch; step onto the surrounding floor to reach desks or the window.

Strips are three metres wide. The drop is eight map units at 32 units/metre, matching existing stair risers and two 0.125 m Kenney fine squares. Raised floors retain their original metre grid; the lower strip uses a contrasting dark Kenney grid. No character-controller settings changed.

The staff door is three metres clear and 3.2 m high, with half-metre infills in the old four-metre slot. Both E switches operate it without a card. The shared StateChart owns movement and blockage; reset closes it. Leaves retract inside the side walls. Readers are clear of counter/storage. Existing keyed freight-gate files are unchanged.

## Registration Operations

Six lounge assemblies are replaced by fourteen placements: two desks, two visual-only chairs, three storage banks, a two-server-rack assembly, two air-handling units, two monitors and two wall readouts. The room stays approximately 17.9 x 9.9 m (1.81:1). Tall equipment remains clear of the central window view.

Reusable cuboid assets have Visual subtrees for later Blender replacements and simple collision for substantial furniture. Chairs/readouts avoid movement blockers. The inactive second item marker now sits on the office desk; no new reward or encounter was added.

The original registration desk, small waiting area, overhead services, window/glazing, outside diorama and lighting remain. Screening retains its F-01 blockout; the rest of the mission is outside this pass.

## Editable sources

Architecture is in `RedBreach/maps/freight_01.map`. One A1 floor brush is replaced by a lower support slab and raised sections; two infill brushes frame the door. All other 1,200 brushes are preserved literally, including UV axes. Floor height and collision outside the approved lower strips are preserved.

`RedBreach/missions/freight/registration_f02.tscn` keeps its scene identity and nineteen retained assemblies, adds fourteen office placements and instances StaffDoor outside Geometry. New assets are in `RedBreach/props/blockout/f03/`; both chairs share one asset. `RedBreach/interaction/sliding_door_wide.tscn` uses the shared door motor/StateChart with three-metre leaf spacing and a reset pose.

The ordinary rebuild remains `tools/rebuild-freight-blockout.ps1 -Validate`. The F-03 Python/Godot application helpers are guarded one-time authoring steps, never normal rebuild operations or a way to overwrite later edits.

## Validation

Build/save/reload passed **199 freight checks, zero failures**, including the full mission route/A reverse, all nineteen stair flights in both directions and existing progression. New checks cover exact floor levels; walking, sprinting, backpedalling and strafing across seven step/threshold/diagonal samples both ways; staff-door collision, both E switches, blockage/reversal/reset; saved props, route clearance and headroom.

All 14,192 baked triangles retain orthogonal one-metre Kenney repeats. The separate greybox suite passed nine checks. Six rendered views were inspected: entry, long strip, door closed/open, office and window. Final build, QA, preservation audit and capture reported no errors or warnings. Initial asset generation emitted temporary-owner warnings; saved rack parts passed reload checks, and the helper now clears ownership before reparenting.

The preservation audit confirms nineteen original assembly references/transforms, all eight light transforms/settings and byte-identical keyed gate scene/script files. These are automated and visual checks; human feel awaits the user's walkthrough.


The subsequent [Registration colour pass](freight-registration-palette.md) improves material separation while keeping this layout and its raised-floor colour. Current materials are visible in [the six-view preview](freight-registration-palette-built.png). Five shared brushes were divided solely for local material boundaries; occupied geometry is unchanged.
