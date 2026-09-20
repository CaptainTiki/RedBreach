# Red Breach agent instructions

## Project
- Red Breach is a crunchy sci-fi shooter set at an industrial plant on Mars during an alien takeover.
- Workspace root: this folder. Godot project: `RedBreach/project.godot`.
- Keep shared instructions and documentation at the workspace root, outside the Godot project.
- Preserve the existing nested project folder unless the user requests restructuring.

## Version every commit
- The starting project version is `0.0.001`, stored in `RedBreach/project.godot` as `application/config/version`.
- The first commit containing this setup establishes `0.0.001`. Each subsequent commit increments the final numeric component by one: `0.0.002`, `0.0.003`, etc.
- Use at least three digits for that component; after `0.0.999`, use `0.0.1000`.
- Include the version change in the same commit as the work. Increment once per commit, not once per file or editing session.
- Before committing, verify the staged scope and version against the previous committed project version.

## Plan levels before building
- Plan each level on paper first as a top-down 2D spatial layout before constructing it in TrenchBroom or Godot.
- Record rooms and zones, routes and connections, story beats, objectives, encounters, items, keys, and locked gates.
- Preserve the plan or its transcription in `docs/` and resolve spatial intent with the user before 3D blockout.
- Begin with a small TrenchBroom pipeline test, then validate traversal and scale before expanding.

## Scope and validation
- Keep the initial experiment small and editable. Document pipeline choices and findings.
- Do not choose a TrenchBroom import plugin, map format, or asset pack without investigating compatibility with the existing Godot project.
- Validate changed project settings and scenes with the installed compatible Godot version when available; report any validation limitations.

## Current gym workflow
- The approved first gym plan is `docs/gym-plan.svg`; scope is recorded in `docs/first-test-plan.md`.
- Edit geometry in `RedBreach/maps/gym_01.map`. Bake it into `RedBreach/gym/gym.tscn` with func_godot.
- Keep authored gameplay nodes outside the Geometry subtree, whose children are replaced by Build Map.
- Read `docs/trenchbroom-workflow.md` before changing the map pipeline. Preserve both installed addons.
- Run `tools/rebuild-gym.ps1 -Validate` after geometry or movement changes; update baseline expectations only for intentional layout changes.

## Interactions
- The 2.0 m gym opening contains an authored `DoorModule` instance from `RedBreach/interaction/sliding_door.tscn`, outside Geometry.
- Keep the door's behavior transitions in its StateChart. Use state signals for motor and feedback code; do not duplicate the state machine in the player or switches.
- E interaction uses a 2 m camera ray stopped by solid geometry. Door blocker detection covers CharacterBody3D and RigidBody3D on its configured mask.
- The combined rebuild validation now includes door checks. See `docs/gym-door-module.md` before extending this module.

## Movement support

- Movement ground checks use GymPlayer's `is_grounded()` to include verified stair-corner support; native slope snapping remains enabled. See `docs/gym-playtest-02.md`.

## Blockout materials

- Prefer the supplied plain Kenney grids under `RedBreach/textures/greybox`; see `docs/blockout-textures.md` for texture scale.
- Keep planned/tested opening dimensions. Use door/window diagrams only when their proportions match; do not reshape gameplay spaces to fit them.
