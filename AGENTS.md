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
- Track deferred improvements in `docs/future-refinements.md`. Read relevant entries when refining a system; these notes do not expand the active task unless the user brings them into scope.
- Do not choose a TrenchBroom import plugin, map format, or asset pack without investigating compatibility with the existing Godot project.
- Validate changed project settings and scenes with the installed compatible Godot version when available; report any validation limitations.

## Current gym workflow
- The approved first gym plan is `docs/gym-plan.svg`; the built movement annex follows `docs/gym-movement-plan.md`. Scope is recorded in `docs/first-test-plan.md`.
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
- Standing/crouched posture belongs to GymPlayer's editable PostureChart. Safe standing checks the full standing capsule; low headroom keeps the player crouched.
- `RedBreach/gym/movement_annex.tscn` is an authored sibling of Geometry with lane origins, recovery points, runway measurements, and labels. Move these with their source-map brushes when relocating a station. See `docs/gym-playtest-03.md`.
- The high-jump blocks are relocated beside the long-jump approaches: low center (-48, 0.375, 10.5), high center (-44, 0.625, 10.5). See `docs/gym-alteration-plan.md` for the current layout and pipeline results. The combined validation includes repeated alteration build/save/reload checks.

## Blockout materials

- Prefer the supplied plain Kenney grids under `RedBreach/textures/greybox`; see `docs/blockout-textures.md` for texture scale.
- Keep planned/tested opening dimensions. Use door/window diagrams only when their proportions match; do not reshape gameplay spaces to fit them.

## Current pistol prototype

- The first weapon is the semi-automatic pistol in `RedBreach/weapons/gym_pistol.tscn`, attached to GymPlayer's Camera3D. See `docs/pistol-gym.md` for tuning, scope, and validation.
- LMB fires, RMB holds ADS, R reloads, and Backspace resets/refills the gym. Preserve the click-to-recapture behavior after Escape.
- Keep Ready/Reloading and Hip/ADS transitions in the pistol's editable StateCharts. Instance ammo/cooldowns/recoil are runtime state; per-weapon resource consolidation remains deferred in Future Refinements FR-001.
- Camera kick and aim drift affect the actual aim used for shooting. Preserve sight alignment, immediate mouse response, and muzzle obstruction checks.
- Runway measurements accept only ordinary WALK/SPRINT modes; ADS must cancel or prevent a timed run.
- The combined rebuild validation includes pistol checks. Use the actual camera viewport for projected sight alignment, since a headless window can have different dimensions.

## Current combat gym

- F5 launches `RedBreach/combat/combat_gym.tscn`; F1/F2 switch between movement/combat gyms. The user approved `docs/combat-gym-plan.svg` before this separate layout was built. Read `docs/combat-gym.md` before extending it.
- Edit combat geometry in `RedBreach/maps/combat_01.map`; run `tools/rebuild-combat-gym.ps1 -Validate` to rebuild and save both Geometry and navigation. Navigation is baked from the static source geometry, clipped to the arena. Preserve authored siblings.
- Bug behavior, player life, and encounter transitions each belong to their editable StateCharts. One panel-released bug, a committed telegraphed lunge, and a resettable encounter are the current scope.
- Preserve real hit-point feedback, shot/attack obstruction, bounded surface splatters, useful-only pickups, death input restrictions, and complete Backspace reset. Extended bug legs are visual placeholders; body collision receives damage.
- Shared player/weapon changes require the original gym validation as well as combat checks. New geometry must still follow the plan-first rule.
