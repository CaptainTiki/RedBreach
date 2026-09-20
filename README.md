# Red Breach

A crunchy sci-fi shooter set at an industrial plant on Mars during an alien takeover.

## Workspace

- `AGENTS.md`: project instructions and development rules.
- `docs/`: premise, decisions, and level planning.
- `RedBreach/project.godot`: the existing Godot project.

Open this repository root in Codex. Open `RedBreach/project.godot` in Godot.

The initial project version is `0.0.001`. Every subsequent commit increments the final version component by one; see `AGENTS.md` for the convention.

Plan levels on paper as top-down 2D layouts with story beats, objectives, encounters, and items before building them in 3D. Start with a small TrenchBroom integration test.

## Test gym

Press F5 in Godot to play the first gym. See the [approved top-down plan](docs/gym-plan.svg), [gym scope](docs/first-test-plan.md), and [TrenchBroom workflow](docs/trenchbroom-workflow.md).

The editable map is `RedBreach/maps/gym_01.map`; the playable saved scene is `RedBreach/gym/gym.tscn`.

The 2.0 m doorway now has a [State Charts door and two switches](docs/gym-door-module.md). Aim at a switch within 2 m and press E.
