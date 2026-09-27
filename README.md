# Red Breach

A crunchy sci-fi shooter set at an industrial plant on Mars during an alien takeover.

## Workspace

- `AGENTS.md`: project instructions and development rules.
- `docs/`: premise, decisions, level plans and build records. Start with the [project brief](docs/project-brief.md)
  and the [architecture language](docs/architecture-language.md).
- `tools/`: plan, generator, drawing and check scripts (Python 3), and the `rebuild-*.ps1` build and validation scripts.
- `playtests/`: notes left during runs (Q in game); see [playtest notes](docs/playtest-notes.md).
- [Future refinements](docs/future-refinements.md): ideas and improvements to revisit.
- `RedBreach/project.godot`: the Godot 4.7 project.

Open `RedBreach/project.godot` in Godot. The version starts at `0.0.001`, and every commit increments the final
component; see `AGENTS.md`.

## Play

F5 runs the main scene, **freight v2** ([build record](docs/freight-v2-build.md),
[walkthrough](docs/freight-v2-walkthrough.md)). From any level:

| Key | Opens |
|---|---|
| F1 | Movement gym: jumps, runway, crouch tunnels, the door module ([first test plan](docs/first-test-plan.md)) |
| F2 | Combat gym: the melee bug, the spitter and pickups ([combat gym](docs/combat-gym.md)) |
| F9 | Style lab: looks, palettes, lighting and presentation ([style lab](docs/style-lab.md)) |
| F10 | Kit lab: corridor profiles, junctions, doors and a hall ([kit sheet](docs/kit-sheet.md)) |
| F11 | Freight v2 |

WASD moves, Shift sprints, Ctrl crouches, Space jumps, LMB fires, RMB aims, R reloads and E uses. Backspace resets,
and Esc releases the mouse. **Q** leaves a playtest note and **Z** marks z-fighting.

## Build

Edit maps in TrenchBroom ([workflow](docs/trenchbroom-workflow.md)), then rebuild and validate with the matching
script, for example `tools/rebuild-freight-v2.ps1 -Validate`. Levels are planned on paper first: a walkthrough, then a
top-down 2D plan, then the 3D build.
