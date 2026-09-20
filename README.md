# Red Breach

A crunchy sci-fi shooter set at an industrial plant on Mars during an alien takeover.

## Workspace

- `AGENTS.md`: project instructions and development rules.
- `docs/`: premise, decisions, and level planning.
- [Future Refinements](docs/future-refinements.md): ideas and improvements to revisit after prototyping.
- `RedBreach/project.godot`: the existing Godot project.

Open this repository root in Codex. Open `RedBreach/project.godot` in Godot.

The initial project version is `0.0.001`. Every subsequent commit increments the final version component by one; see `AGENTS.md` for the convention.

Plan levels on paper as top-down 2D layouts with story beats, objectives, encounters, and items before building them in 3D. Start with a small TrenchBroom integration test.

## Test gym

Press F5 in Godot to play the [Combat Gym](docs/combat-gym.md): a 10/20/30 m precision range and the first bug encounter. Press F1 for the movement gym or F2 for a fresh combat gym. See the [approved top-down plan](docs/gym-plan.svg), [gym scope](docs/first-test-plan.md), and [TrenchBroom workflow](docs/trenchbroom-workflow.md).

The editable map is `RedBreach/maps/gym_01.map`; the playable saved scene is `RedBreach/gym/gym.tscn`.

The 2.0 m doorway now has a [State Charts door and two switches](docs/gym-door-module.md). Aim at a switch within 2 m and press E.

The [door/stair playtest notes](docs/gym-playtest-02.md) cover confirmed door behavior and stair descent. [Blockout texture notes](docs/blockout-textures.md) record the supplied Kenney grids and their map scale.

The [movement annex](docs/gym-movement-plan.md) has passed the user's first playtest. From spawn, turn left through the new west opening. Test the 2/3/4/5 m jump gaps, 20 m timed runway, and crouch tunnels. Hold Ctrl to crouch; failed gap attempts return to that lane, while Backspace returns to the original spawn. See [annex playtest notes](docs/gym-playtest-03.md) for checks and measured results.

The high-jump blocks now sit along the south wall opposite the long-jump approaches. The [alteration plan and results](docs/gym-alteration-plan.md) record verified source edits, collision, labels, and repeated build/save/reload. The TrenchBroom UI step remains untested because desktop control could not start. The relocation is included with the pistol in local version `0.0.004` (Weapons).

The [first pistol](docs/pistol-gym.md) is playable in the existing target lane: left click fires, hold right mouse for ADS, R reloads, and Backspace resets/refills the gym. Targets have health and recover automatically. The [approved Combat Gym layout](docs/combat-gym-plan.svg) is now built as a separate map: player damage/death, useful-only pickups, a StateCharts bug with a dodgeable lunge, and green hit/death splatters. See the [playtest route and build instructions](docs/combat-gym.md).

The [larger spitter](docs/spitter.md) is available from the yellow-green arena panel. Its half-second mouth-opening wind-up exposes a weak point, and its fast 35 m/s spit makes it a priority target. Two mouth hits or six body hits kill it.
