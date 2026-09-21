# F-02 blockout prop assets

These are editable Godot scenes made from six-sided boxes, not final art. The saved placement is `missions/freight/registration_f02.tscn`, instanced outside the map's generated Geometry. The reviewed plan is `docs/freight-registration-plan.md` at the repository root.

Use the existing scene instances and dimensioned variants to reuse a prop. Edit mesh/shape dimensions; do not scale the root, because the Kenney material repeat is one metre. Generic variants use local metres and an origin at the footprint corner on the supporting surface. The compound registration asset retains its own saved reference origin; preserve its placement when replacing it.

Each asset separates `Visual`, simple `Collision` (when needed), and `Lights`. Replace Visual with Blender-authored meshes at the same metre scale and origin. Keep the collision and any needed anchors/lights until the refined shape is deliberately reviewed. Chairs inside RegistrationDesk are visual-only; its counters and cabinets are solid. The two possible pickup markers belong to the placement scene, not to functional inventory code.

Dark and panel materials use supplied Kenney textures with local metric projection. Screen/lamp materials are semantic emissive placeholders. Floors, walls and structural framing remain in the source map. Normal map rebuilds must never rerun the one-time prop generator or discard these external scene references.
