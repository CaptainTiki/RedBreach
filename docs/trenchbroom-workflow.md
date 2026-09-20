# TrenchBroom / Godot workflow

## Verified local tools

- Godot 4.7.2 stable (Steam), Forward+ / D3D12, Jolt Physics.
- TrenchBroom 2025.4 at `D:\TrenchBroom\TrenchBroom.exe`.
- func_godot 2025.12 and Godot State Charts 0.22.5, both enabled.
- Mapping format: Valve 220; scale: 32 map units per Godot metre.
- Original gym grids are 128 x 128 pixels at 0.25 UV scale, giving a 1 m major grid and 0.25 m subdivisions. The annex uses plain Kenney grids at 0.0625 scale: 2 m texture repeats and 0.25 m fine squares; see [texture notes](blockout-textures.md).
- Coordinate conversion used by func_godot: Godot `(X,Y,Z) = map (Y,Z,X) / 32`. The plan's north is Godot -Z, corresponding to map -X.

## Play

Open `RedBreach/project.godot` and press F5. Main scene: `res://combat/combat_gym.tscn`. F1 opens the movement gym; F2 opens the combat gym. See [combat build and playtest instructions](combat-gym.md).

- WASD: walk; Shift: sprint; Space: jump; hold Ctrl: crouch.
- Mouse: look; left click: fire the pistol; hold right mouse: ADS; R: reload; E: use an aimed switch within 2 m.
- Escape: release mouse; click: recapture without firing; Backspace: reset to spawn and refill the pistol/targets.

The [prototype pistol](pistol-gym.md) provides semi-automatic hitscan fire, ammunition/reload, ADS, and recoil. Targets have health and recover after two seconds. The separate Combat Gym now adds the first bug, player damage/death, pickups, and splatter feedback. The original diagnostic `fire_probe()` remains available to the older geometry/sightline checks; normal left-click input uses the pistol. State Charts drives the [door/switch module](gym-door-module.md) in the 2.0 m doorway. Open it before testing that clearance.

## Edit the map

1. Open `RedBreach/maps/gym_01.map` in TrenchBroom using the **Red Breach** game and **Valve** format.
2. Game path: `D:\Godot\REPOs\RedBreach\RedBreach`. Material collections: `gym`, `greybox/Dark`, `greybox/Light`, `greybox/Green`, `greybox/Purple`, and `greybox/Orange`.
3. Edit the brushes and save the map.
4. In Godot, open `gym/gym.tscn`, select **Geometry**, and press **Build Map** in the Inspector.
5. Save the scene and press F5.

A `.map` reimport alone does not rebuild the saved scene. Explicitly build and save Geometry. Changes to generated Geometry children will be replaced at the next build. Keep the source map and baked scene together in commits.

Alternatively, from the repository root run `./tools/rebuild-gym.ps1`. Add `-Validate` to run the gym, movement, door, annex, alteration, and pistol checks. Pass `-GodotPath` if the editor executable is elsewhere. Save any open Godot scene edits before running the command, then reload the scene if prompted.

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

## Movement annex and alteration test

The saved gym now contains 69 brush collisions, including the west annex. Its authored `MovementAnnex` instance stays outside Geometry. Jump lane and runway coordinates are relative to editable station roots; reset points and signs are children of those roots. The full validation command includes 58 annex checks and 32 alteration checks. See [playtest 03](gym-playtest-03.md).

The user accepted the annex and requested the alteration exercise. The two high-jump blocks have now moved beside the long-jump approaches; see [the current plan and results](gym-alteration-plan.md). Source editing, func_godot rebuilding, collision, and saved-scene reload passed. The TrenchBroom UI round trip remains untested because the computer-use runtime failed to start. For future station moves, use this workflow:

1. Mark the intended destination on the 2D plan, preserving approaches and return routes.
2. In TrenchBroom, move the two existing block brushes and save the map. Retain their heights.
3. In Godot, move `Labels/CoverLow` and `Labels/CoverHigh` to match. These original blocks have no reset/measurement triggers; other stations do, so move their authored station roots too when applicable.
4. Rebuild Geometry, save, and reload the scene. Verify the old positions are clear, the new positions have the expected collision/heights, and labels agree.
5. Update intentional coordinate expectations in validation and run `tools/rebuild-gym.ps1 -Validate`. Playtest access to both jump types and repeat the source build to prove the alteration persists.

Moving a solid block is a small change. Moving a pit lane or doorway also requires editing the surrounding floor or wall opening, since those voids are assembled from solid brushes. Gameplay placement is currently a separate Godot edit; it is not automatically moved by TrenchBroom.
