# F-04 / A1 furnishing and architectural sample

Status: **approved; Screening pilot built and validated as layout 09**. The user approved the drawings and implementation, then requested an in-person walkthrough and critique. Screening and its exit frame are built; Administration and Staff Preparation remain planned until the architectural pilot has been assessed. Registration remains intact.

- [Connected floor plan](freight-a1-density-plan.png) / [editable SVG](freight-a1-density-plan.svg)
- [Screening architectural sections](freight-a1-architecture-section.png) / [editable SVG](freight-a1-architecture-section.svg)
- [Placement and clearance data](freight-a1-density-plan.json)

## Intent and scope

Use the user's Doom 3 BFG Administration screenshots as the composition reference: full equipment assemblies, overhead services, useful work areas and recognizable architecture. Keep negative space purposeful: circulation, working aisles, turns, retreat and sightlines. More individual brushes are not the objective. The supplied images are design references, not assets to import.

The connected proposal replaces the earlier F-01 furnishings in Screening, Administration and Staff Preparation. Existing room shells, floors, doorway locations and mission progression remain. Registration and its accepted exterior view are preserved. Administration remains an optional in-and-out visit; the main route continues from Screening through Staff Preparation to A2 Inspection.

Screening and its exit frame are now the built architectural pilot. Walk it and assess the strength of the profile before extending that architecture. The connected drawing reserves the surrounding furnishing composition now. It does not authorize introducing new interactions or enemies.

## Three functional spaces

| Space | Composition | Reserved movement |
|---|---|---|
| Screening | Walk-through scan frame, baggage conveyor/scanner, operator desk and chair, inspection counter, lockers, supply/storage banks, cooling unit and wall display | Three-metre main and Administration routes; two-metre observation access |
| Administration | Five paired workstation assemblies with ten chairs, filing cabinets, network cabinet, archive bay, wall display and ventilation | Three-metre entry spine; two-metre workstation and archive aisles |
| Staff Preparation | Kit issue counter with staff access behind, changing/cleaning area, repair/fitting area, tool check and outbound carts/cases; partial equipment backboards define bays | Three-metre through route and changing aisle; two-metre repair/tool access |

Room floors remain at 0 m. Orange on the plan is clearance shading, not a proposed recessed floor. Preserve the accepted offsets in the main route. The scan arch is a visual prop, with 3 m clear width and 2.8 m clear height; no scan interaction or new gate is planned.

## Screening architecture pilot

- **Straight lower walls, angled upper corners.** The lining's 45-degree upper insert projects 0.55 m from the wall and begins at 2.95 m below the 3.5 m ceiling. It stops at doorway apertures.
- **Repeated ribs.** Four stations at paper Z=263.5, 267.25, 271 and 274.75: 3.75 m apart. Members are 0.25 m wide, project 0.25 m, and leave a 3.25 m ceiling underside. Legs are omitted where they would cross existing openings. At a rib, the diagonal follows the corner: its inner diagonal has a 0.8 m intercept from the original wall/ceiling corner, joining the inward faces of the leg and beam. This is a faceted lining/frame profile, not structural engineering.
- **Equipment clearance.** Storage and cooling remain below the angled upper envelope. The scanner top is 3.15 m, leaving 0.1 m below a crossing rib. Move the small east-wall display away from its rib station; slightly inset the west supply cabinet.
- **Compartment threshold.** The Screening-to-Staff-Preparation frame is centred at paper (88,276), with a 4 m clear opening, 3.2 m clear height, 0.5 m overall depth and 5 m outside width. Jambs sit outside the existing opening. No working door or pressure simulation is introduced in this sample.
- **Services and light housings.** A shallow north service trunk and workstation lights fill the overhead layer. Beam/service connections are deliberately integrated; these are not disconnected floating boxes. Coordinate duct intersections with beams when building.

The broad section cuts Screening at paper Z=263.5, through storage S6 and cooling S7. The enlarged upper-corner detail shows the lining between ribs; the broad section shows the rib following that profile. The threshold elevation shows the existing four-metre opening with its new surrounding frame.

## Materials and authoring

Carry the established Kenney readability palette: dark floor, muted green walls, pale grey ceiling, muted purple equipment with grey work surfaces/services. Give structural frames a contrasting grey so their silhouette remains legible. Orange remains available for meaningful route/step elements; the plan's orange ribbons do not require orange paint throughout A1. Preserve metre-based UVs.

Room architecture and substantial frame masses belong in the TrenchBroom map. Reusable desks, chairs, scanner, lockers and machinery should be Godot cuboid scenes outside regenerated Geometry, ready for later Blender visual replacements. Chairs and minor accessories must not create retreat-snaring collision. Keep simple blockers on substantial equipment.

Build major silhouettes, housings, frames and equipment groupings now. Defer panel seams, bolts, minor pipes, wear and final meshes. Staff rooms should show cleaner enclosed versions of the same construction; machinery areas can expose larger ribs and services later.

## Verification and walkthrough

The drawing generators check all floor-object footprints against their room bounds and one another; reserve 3 m main routes and 2 m working aisles; and check scanner/rib headroom, upper-corner clearance over Screening equipment and threshold-jamb clearance from props. The plan contains 64 floor/low-wall reservations including six rib legs, plus 29 overhead reservations. These are assembly envelopes, not a target prop count.

Both rendered drawings were visually inspected. Paper clearance checks cover the whole connected plan. Screening now additionally passes saved-scene Godot/Jolt checks: all three reserved standing ribbons; forward/reverse walking, sprinting, backpedalling and strafing; scanner/frame/rib/corner headroom; substantial equipment collision; and external prop references with metric textures. These checks do not establish enemy navigation or subjective feel. No commit or project-version increment was requested.

The complete freight suite passes **217 checks**, plus **nine greybox checks**, with zero failures. Four rendered player views were inspected: [built contact sheet](freight-screening-built.png), [entry view](freight-screening-entry.png). The saved map contains 1,229 brush collisions and 14,372 nondegenerate triangles with orthogonal one-metre texture repeats. Screening has 15 reusable prop assemblies, 109 BoxMesh components and four light sources. The operator chair has no movement collision. The original Registration scene is byte-identical to its pre-F04 snapshot.

Start a fresh F5 run and follow Registration into Screening. Review the room proportions, rib/upper-corner strength, scanner scale, equipment density and exit framing before propagating this profile. Administration and Staff Preparation still show their earlier F01 blockout beyond the pilot. Enemies and broader pickups remain a subsequent pass.

One-time application helpers are `tools/apply-freight-screening.py` and `RedBreach/tools/apply_freight_screening.gd`; both guard against replacing later edits and are excluded from normal rebuilds. Continue editing the source map and saved `screening_f04.tscn` / `props/blockout/f04/` assets directly. [Validation record](freight-screening-validation.json).


## Pilot walkthrough follow-up

The user reports that Screening looks good, with minor issues and no major blocker. They asked about the missing recessed pathway: the approved F04 floor is intentionally level, and orange plan ribbons denote clearance. Registration's lowered walking strip remains local to Registration.

The reported ceiling-duct z-fighting was confirmed: eight dark vent panels ended on the same plane as the housing. The visual housing is now 0.035 m shallower, leaving 0.01 m behind the panel backs and 0.035 m behind their front faces. The original collision envelope is unchanged. A rendered scene reload verified all eight separations and the collision dimensions; three lateral camera views were inspected in [the duct-fix preview](freight-screening-duct-fix.png). The one-time authoring source also contains the correction. No map rebuild, movement change or new gameplay was necessary.

The user also requested hatch reservations as part of architecture. [Candidate drawing](freight-screening-hatch-reservations.png) / [reservation data](freight-screening-hatch-reservations.json): ceiling C1 between ribs/lights, and wall W1 in the north equipment bay. These are alternative possibilities sharing emergence space, not a committed pair of spawns. The candidate openings are 2.5 m square with clear floor reservations; actual bug fit, backing pockets, trigger timing, navigation and enemy counts remain to be designed/validated. W1 must lead to an enclosed service pocket rather than directly outside the pressurized shell. Existing geometry has no new openings or enemies.


## Layout 10 floor follow-up

The user subsequently chose to remove Registration's depression rather than extend it through Administration. [Registration now has one continuous flat dark floor](freight-registration-flat-floor.md), with no contrasting material path. This supersedes the local-recess wording above. Screening geometry and furnishings are unchanged. The latest full validation remains 217 freight plus nine greybox checks; current map totals are 1,221 brushes and 14,276 nondegenerate metric-textured triangles.
