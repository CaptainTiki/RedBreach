# F-02 / A1 registration composition

Status: **approved by the user and built as layout 07 / F-02**. The other F-01 rooms retain their prior layout. This is a focused response to the user's Doom 3 BFG Administration references and feedback that the first furnishing sample is much too sparse.

[Plan and registration elevation](freight-registration-plan.png) Â· [Editable drawing](freight-registration-plan.svg) Â· [Dimensions and placement data](freight-registration-plan.json)

## What the references change

The user wants the entire room composition represented in simple boxes now: registration desk, rails, lighting fixtures, wall equipment, overhead machinery and the structures enclosing them. Shape, density and placement should establish where later props and items belong. Fine trim, screws, carved panels and finished models are not the current task.

The supplied screenshots show several layers at once. The desk has an overhead mass, signage, terminals, a staff station and surrounding architecture. The work area combines railings, equipment and ceiling services. The later catwalk creates a second view of previously visited space after travelling through other rooms. These are observations from the user-supplied images, not measured dimensions or a claim about every route in that game.

Local references: [registration](references/doom3-administration/registration.png), [work area](references/doom3-administration/work-area.png), [return catwalk](references/doom3-administration/return-catwalk.png). These are user-provided Doom 3 BFG screenshots for design discussion, not game assets for Red Breach.

## A focused, denser sample

Develop the current A1 reception envelope first. It is almost 18 x 32 m, so simply adding a few freestanding desks leaves a very large empty volume. Retain its shell, the six-metre east entry at (114,270), the four-metre screening opening at (96,272), floor 0, ceiling 3.5 m, and the existing south window.

Divide the envelope into four functional bays:

| Bay | Clear dimensions | Role |
|---|---|---|
| Arrival / registration front | 17.9 x 13.9 m | First view of counter, information kiosks, equipment banks and onward screening route |
| Waiting | 9.8 x 7.8 m | Seats, short queue rail, storage, staff access and passage to the lounge |
| Registration staff bay | 7.9 x 7.8 m | Counter enclosure, two work positions, staff back counter and supply storage |
| Window lounge | 17.9 x 9.9 m | Seating groups, table, a cabinet/vending placeholder and the exterior view |

These are functional subdivisions: the registration front remains open above its counter. Do not pretend it is a sealed room or add a functioning security gate. New partitions are 0.25 m thick; new floor openings are four metres wide. The first cross-partition is at Z=276, preserving approximately two metres between it and the existing screening opening's end. Door ends use butt joints; frame allowance must not consume the clear aperture. Current main circulation remains unchanged. Optional branches reach the desk, staff area and lounge.

The drawing reserves three-metre-wide walking ribbons, including turns, against floor objects and walls. All four bay proportions are under 2:1. This is a paper clearance check, not Godot collision or enemy-navigation evidence.

## Block every layer with boxes

- Registration: a long front counter and two returns, two chair envelopes, two monitor blocks, rear work/storage surface, tall supply cabinet, hanging sign and a broad canopy with task-light housings. Counter is 1.1 m high; canopy underside is 2.7 m. Monitor/sign details stay over the desk rather than intruding into the walking lane.
- Entry: information/check kiosks, equipment cabinets, structural uprights and visible light fixtures. Their positions make the route read as a staffed intake point.
- Waiting/lounge: bench or linked-seat envelopes, a short queue rail, table and wall service/storage blocks. Keep the window sightline useful and circulation legible.
- Overhead: service trunks, shallow beams, canopy and eight light-housing envelopes. These establish the eventual occupied volume and lighting locations. A fixture needs a visible box housing as well as a light source. The drawing uses dashed purple outlines for overhead masses.

The schedule currently contains 27 floor-object envelopes, 15 overhead envelopes and four monitor/sign/detail blocks. These are placement reservations, not a required triangle count or an invitation to fill the remaining floor indiscriminately. For example, a linked-seat envelope can contain several simple seat blocks. Give each assembly a function and a readable silhouette.

Two orange markers reserve **possible** future item surfaces: the staff back counter and a lounge cabinet. They create optional reasons to investigate these spaces; they assign no ammunition amount, health reward or mandatory quest item. The required route still leads directly to screening. Broader pickups and encounters remain a later pass.

## Authoring and replacement

Use TrenchBroom for room-defining architecture: floors, walls, openings, slabs, stairs, landings and structural masses that shape routes. Use reusable Godot scenes for the registration assembly, chairs, desks, equipment units and light fixtures. A placeholder prop scene may contain only BoxMesh parts and one simplified collision body. Save those scenes outside the regenerated Geometry subtree.

Finished furniture and equipment should generally become Blender-authored meshes. Keep the Godot wrapper's placement, origin, metre scale, interaction anchors and collision contract while replacing its visual child. Repeated rails and modular fixtures can also become mesh modules. Do not force complex furniture into hundreds of permanent map brushes; equally, do not model final props before their footprints work in the level.

Maintain Kenney metric textures for opaque blockout geometry. Use minimal semantic emissive light strips/screens. Chairs and small decorative pieces should not add separate retreat-snaring collision; substantial desks/cabinets still need simple reliable blockers.

## Visual return routes

Record the user's catwalk example as a future level-design tool: show an upper route from below, take the player through other rooms, then bring them onto that route with a new view of a familiar space. The catwalk does not need a direct stair from the room below. Check both directions of visibility and preserve gates/keys so a jump cannot bypass progression.

This F-02 sample adds no catwalk. It would need a separately reviewed upper connection and a taller room section; inserting it into the existing 3.5 m reception would be inappropriate. The idea belongs in subsequent A/B routing decisions where the height and path can support it.

## Review and implementation boundary

The user approved this arrangement. The new internal partitions and the registration footprint have been built from the schedule. Simple prop scenes sit outside generated Geometry; the map was baked, saved and reloaded. Judge this sample in a human walkthrough before extending the same density elsewhere.


## Built sources and editable props

- `RedBreach/maps/freight_01.map` holds the six new partitions, three headers, six uprights and three beams. Only ten superseded reception furniture brushes were removed; all 1,183 other original brushes remain literally unchanged. The saved map now has 1,201 brushes.
- `RedBreach/missions/freight/registration_f02.tscn` is the saved placement scene, instanced as RegistrationF02 beside Geometry. It contains 25 assembly instances referencing 20 reusable prop scenes under `RedBreach/props/blockout/f02/`. Matching ceiling fixtures share an asset.
- `registration_desk.tscn` includes the counter pieces, visual-only chairs, canopy, monitors, sign, rear storage and two task lights. Each prop asset has a Visual subtree for later mesh replacement, separate simple collision where needed, and actual light nodes where specified. All 122 visible prop parts are cuboids; structural map brushes add the room framing.
- Four shared materials retain Kenney local metre projection for opaque geometry and semantic emission for screens/light strips. Root and visual scales remain one. CandidateItem1/2 are editor-only placement markers, not active pickups.

The normal rebuild only reads the map and preserves these external scene instances. `tools/apply-freight-registration.py` and `RedBreach/tools/apply_freight_registration.gd` are one-time application helpers; they are guarded and must not replace subsequent map/prop edits. The ordinary workflow remains `tools/rebuild-freight-blockout.ps1 -Validate`.

For this walkthrough, approach from the hub and inspect the registration view, optional staff access, seating and the window lounge. Check whether the added structure gives enough density while leaving useful movement space. The required route still exits toward Screening; no new mission objective, enemy or reward was added. The project version stays 0.0.009 because this work has not been committed.

[Built player-eye views](freight-registration-built.png)


## Validation / layout 07

The final rebuild/save/reload passed **180 checks with zero failures**. This includes the complete mission route and A reverse, all 19 stair flights in both directions, cards/power/selector/cache/ladder/gates, retained F-01 routes and the new optional reception paths. Four reception paths also passed standing-capsule checks down both edges of their three-metre ribbons. The real player is blocked by the counter; its first view from the east entry is clear; canopy/task-light collision preserves standing headroom.

Scene checks confirm all 25 external assembly references, shared matching fixture assets, 122 cuboid visuals, eight corresponding light sources, visual-only staff chairs and two inactive pickup reservation markers. All 14,012 nondegenerate map triangles retain orthogonal 1 m Kenney repeats; F-02 textured meshes use local metric projection at unit scale. The separate greybox suite passed all nine checks.

Six player-eye views were inspected. Coplanar cabinet and kiosk faces found in the first render were separated within their reserved footprints, eliminating the visible flickering. The final build, QA and rendered capture finished without reported errors or warnings. The independent source audit confirms the 1,183 protected brushes are identical, including face texture axes. These are automated geometry/progression results, not a human density judgement or combat-navigation result.


## User walkthrough / built F-03 follow-up

The user likes the arrival view, exterior window and lighting. Their next request is a 0.25 m circulation-level distinction, a door enclosing the staff entrance, and supervisor/back-office furniture replacing the sparse window lounge. [F-03c](freight-registration-recess-plan.md) is now built as layout 08 and supersedes this historical F-02 record for the floor, staff door and back-office furnishing. Screening was outside F-02 and retains its F-01 blockout.
