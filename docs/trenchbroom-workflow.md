# TrenchBroom / Godot workflow

## Verified local tools

- Godot 4.7.2 stable (Steam), Forward+ / D3D12, Jolt Physics.
- TrenchBroom 2025.4 at `D:\TrenchBroom\TrenchBroom.exe`.
- func_godot 2025.12 and Godot State Charts 0.22.5, both enabled.
- Mapping format: Valve 220; scale: 32 map units per Godot metre.
- Grid textures are 128 x 128 pixels at 0.25 UV scale, giving a 1 m major grid and 0.25 m subdivisions.
- Coordinate conversion used by func_godot: Godot `(X,Y,Z) = map (Y,Z,X) / 32`. The plan's north is Godot -Z, corresponding to map -X.

## Play

Open `RedBreach/project.godot` and press F5. Main scene: `res://gym/gym.tscn`.

- WASD: walk; Shift: sprint; Space: jump.
- Mouse: look; left click: hitscan probe with target hit feedback; E: use an aimed switch within 2 m.
- Escape: release mouse; click: recapture; R: reset to spawn.

The probe is a test tool. There is no weapon/ammo system or enemy AI yet. State Charts drives the [door/switch module](gym-door-module.md) in the 2.0 m doorway. Open it before testing that clearance.

## Edit the map

1. Open `RedBreach/maps/gym_01.map` in TrenchBroom using the **Red Breach** game and **Valve** format.
2. Game path: `D:\Godot\REPOs\RedBreach\RedBreach`. Material collection: `gym`.
3. Edit the brushes and save the map.
4. In Godot, open `gym/gym.tscn`, select **Geometry**, and press **Build Map** in the Inspector.
5. Save the scene and press F5.

A `.map` reimport alone does not rebuild the saved scene. Explicitly build and save Geometry. Changes to generated Geometry children will be replaced at the next build. Keep the source map and baked scene together in commits.

Alternatively, from the repository root run `./tools/rebuild-gym.ps1`. Add `-Validate` to run the baseline gym checks. Pass `-GodotPath` if the editor executable is elsewhere. Save any open Godot scene edits before running the command, then reload the scene if prompted.

## Configuration sources

- `RedBreach/mapping/red_breach_game_config.tres`: game definition.
- `RedBreach/mapping/red_breach_map_settings.tres`: map build settings.
- `tools/trenchbroom/RedBreach/`: exported portable GameConfig, FGD, and icon.
- Local installed definition: `%APPDATA%/TrenchBroom/games/RedBreach/`.
- Local game path: `%APPDATA%/TrenchBroom/Preferences.json`, key `Games/Red Breach/Path`.
- Local func_godot paths: `%APPDATA%/Godot/app_userdata/RedBreach/func_godot_config.json`.

Machine-specific settings are outside Git. To move to another computer, copy the exported definition folder into TrenchBroom's user `games` folder and set the Red Breach game path to the nested Godot project. The project resources use relative paths. The installed addon source is unmodified.

Export fresh configuration with Godot's `--headless --path <Godot-project-folder> --script res://tools/export_trenchbroom.gd`, then copy the three exported files into the local definition folder. The export script uses the installed func_godot exporter; revisit its internal `_build_class_text` call if upgrading the addon.

Official reference: [func_godot map editor configuration](https://func-godot.github.io/func_godot_docs/FuncGodot%20Manual/pages/guide_map_editor_config.html).

## Validation

`res://tools/validate_gym.gd` runs on the saved scene with Jolt. It checks floor/wall dimensions, saved brush collision, three doorways, stair climbing, ramp ascent/descent, wall blocking, target hits, respawn, and repeated builds.

It also raises the floor in a temporary map copy, rebuilds, saves, and reloads the changed collision. The canonical map stays unchanged. Tests describe this baseline gym; update expectations when intentionally changing its layout.

Logs and rendered captures live in ignored `RedBreach/.godot/`: `gym_build.log`, `gym_qa.log`, `gym_capture.log`, `gym_player_view.png`, and `gym_overview.png`.

## Initial validation result

First gym pass: **26 checks passed, 0 failures** in Godot 4.7.2 with Jolt. This includes saved brush collision, dimensions, Shift/Space bindings, sprint speed, jump and landing, stair climbing, ramp ascent/descent, door clearances, wall blocking, target feedback, respawn, repeated rebuilds, and an edited-source build/save/reload round trip.

Forward+ / D3D12 player-view and overview captures were rendered and inspected. TrenchBroom 2025.4 loaded the editable map and its FGD without reported errors. Build, QA, and capture logs contained no script errors or warnings.

This verifies the initial gym baseline; subjective movement feel still needs the user's playtest. Version remains 0.0.001 because no commit has been made.

## Movement follow-up

See [gym playtest 01](gym-playtest-01.md) for the user's scale findings and the stair/ramp fix. The validation command now also runs `validate_motion.gd` at a fixed 120 fps to catch ramp contact and camera continuity regressions. It also checks all three target plates. Camera smoothing changes need a fresh run of the game to initialize the independent camera.

## Door module

`RedBreach/interaction/sliding_door.tscn` is a reusable authored scene outside Geometry. Its StateChart node owns the five behavior states. See [door module notes](gym-door-module.md) for controls, placement, state flow, and validation. The combined validation command includes `validate_door.gd`.
