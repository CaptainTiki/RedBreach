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

The [latest playtest notes](docs/gym-playtest-02.md) cover confirmed door behavior and stair descent. [Blockout texture notes](docs/blockout-textures.md) record the supplied Kenney grids and their map scale.

The [movement annex](docs/gym-movement-plan.md) is built and ready for playtesting. From spawn, turn left through the new west opening. Test the 2/3/4/5 m jump gaps, 20 m timed runway, and crouch tunnels. Hold Ctrl to crouch; failed gap attempts return to that lane, while R returns to the original spawn. See [annex playtest notes](docs/gym-playtest-03.md) for checks and measured results.

After the annex playtest, move the existing high-jump blocks beside the jump lanes as a deliberate TrenchBroom alteration test. Their original positions are retained for now. The annex is saved in local version `0.0.003` (Movement Gym).
