# Retro industrial sample R-01 — proposed, not built

Review drawing: `retro-industrial-sample-plan.png`. This is a separate architecture-lab study; existing maps remain unchanged pending review.

## Spatial proposal

- Straight corridor: 12 m long, true four-sided trapezoidal clear section, 6 m floor width, 3 m ceiling width, 4 m height. Walls slope inward continuously. These are clear shell dimensions, not outside brush dimensions.
- Three substantial rib frames at corridor stations 2, 6 and 10 m. Reserve 0.25 m inward horizontal projection per side and 0.25 m beneath the ceiling; 0.25 m longitudinal thickness. Minimum clear width at 2 m height is 4 m; preserve a centered 3.5 m walking ribbon. Slopes are overhead-facing walls, not climbable floor ramps.
- A 0.5 m deep transition separates corridor and room: each owns its 0.25 m wall. Portal clear opening 3 m wide x 3 m high, bevelled frame, open for this visual test. No automatic door behavior.
- Machinery room: 10 x 10 m clear bounding footprint, 1.5 m clipped corners, 5 m ceiling. A centered 3 x 4 m cooling/pump assembly, about 2.5 m tall, establishes function and leaves 3.5 m side aisles and 3 m front/rear clearances before fixtures. Room corners use sloping ceiling haunches; keep the central overhead volume for equipment.
- Floor level stays at zero. One continuous dark floor material. Each texture-zone boundary uses a real frame, seam or border. Weathering within one material can vary without introducing another architectural zone.
- No mission, encounter, pickup, key or locked-gate progression in this isolated visual sample. Walk in, circle the machine, return. No ceiling hatch in this test.

## Small material shortlist

These are material roles, not approved or already downloaded assets. QUOD's released PNG set is a candidate reference/source: https://daivuk.itch.io/quod-textures (creator lists CC0). Check the actual pack before selecting an image. Its normal/roughness maps have not been verified; do not assume they are included or derive height blindly from colour.

1. Muted green painted steel infill: same panel design in clean and grimy variants. Clean paint roughness about 0.35–0.5; dirt about 0.75–0.95, subject to lit review. Paint and grime are nonmetallic; use a mask for exposed metallic steel. Dirt collects around seams; subtle normal detail for dents/pitting.
2. Lighter neutral steel rib/frame: broad bevelled geometry and a restrained brushed finish. Keep all faces of each structural element in one material family.
3. Dark nonslip floor: subtle fine relief, high roughness, continuous across the sample. No painted walkway.

The drawing's swatches indicate colour intent only, not final texture images or rendered PBR materials. Compare clean/grimy treatments on the same geometry under identical fixed lighting, using editor-selected saved material variants. Do not alter lighting to flatter either version.

## Authoring and review

All textures/maps are prepared offline and saved to disk. TrenchBroom displays base-colour textures with authored UVs. Inspect existing func_godot material mapping before configuring the sample. Godot uses saved editable materials, generated-in-editor Geometry, and authored props/lights outside Geometry. No runtime generation or runtime batching in this sample. Normal maps add surface response, not silhouette or collision.

Before construction, review the drawing and shape. Then check player capsule clearance, rib/portal joins, metric UV scale and saved prop references; build/save/reload using compatible Godot. Capture matching player-eye views of corridor, portal, room and material detail and display images directly in the conversation for remote review. No commit or application version change for this proposal.
