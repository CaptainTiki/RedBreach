# Clean-slate test plan — from dev branch to production

Status: revision 02, 2026-09-25. **Phase 1 is complete: style lab S-01 (F9),
settled by the user after three revisions. The style sheet is in
[style-lab.md](style-lab.md#phase-1-settled-2026-09-25). Phase 2 (kit lab) is next.**
Nothing has been removed.

## Framing

The user treats everything built so far as a **dev branch**: experiments to find
what we can do and what is within our abilities. The combat labs already
answered the combat questions: ambush construction, which enemy combinations
feel good, and keeping enemies out of the player's face when a door opens.
Those findings are the **combat log**. The architecture labs answer a different
question: **what can we build that looks interesting enough to keep?** Levels
are later designed for combat by applying the combat log to whatever
architecture we settle on.

The direction is changing from Doom 3 density to **QUOD-level fidelity with
interesting geometry**. Spaces get their character from their shape (trapezoid
corridors, angled profiles, clipped corners, height changes) rather than from
object count.

**The end goal is about ten good, solid levels.** Who builds what is still an
open question, and these tests should inform it. One candidate: Claude builds
the levels, the user tweaks them, and the user does the final dressing by hand
in TrenchBroom.

### What "proofed" means

A mission we can **play from start to finish** that **looks like something we
would post to Instagram to attract wishlists**. If it doesn't look like people
want to play it, we are still searching. Passing validation, traversal or
playtest timing does not count as proof on its own.

### Order of work

Labs come first. Only after a proof passes do we write the style sheet and
decide what to keep and what to throw. The cleanup comes last. Until then, keep
a running **findings log** of what each lab taught, so that the eventual
keep/throw decisions have evidence behind them.

**Working rule, carried over from the lab:** every test exists to answer named
questions. Build only as far as those questions need, then stop.

## Lessons already paid for

These cost drivers from the Doom 3 attempt should not come back:

| Cost driver | Evidence |
|---|---|
| Prop density | Route A needed 634 prop assemblies, 350 light-mount stems and runtime batching |
| Single-use generators | Nine `apply-*` / `finish-*` scripts, each with a "never run again" warning |
| One validator per map | 1,037 checks for one straight corridor, 1,476 for the corner lab, 217 + 61 for freight |
| Special-case joins | T-jamb void fill, degenerate-winding traps, and brush counts that must be matched against collision counts |

## Questions the labs must answer

### A. Look
- A1. Which **profile family** carries the style: a full trapezoid, a straight lower wall with a sloped upper wall, or a box with clipped corners?
- A2. What **texture direction**: source, texel density, filtering (crisp or smooth), palette?
- A3. How much structure is enough: rib depth and pitch in the simpler profile?
- A4. What **presentation layer** makes a frame postable: lighting mood, fog, glow, emissive signs, decals, steam or sparks, a Mars exterior view?

### B. Shape and joins
- B1. Do turns, T junctions, corridor-to-room openings and room corners in the new profile join **without special-case fill geometry**? (Hypothesis: fewer facets mean fewer voids.)
- B2. What is the **minimum piece list** that ten levels need?
- B3. Do angled rooms (clipped corners, haunched ceilings, sloped walls) work at small, medium and hall scale?
- B4. The **interrupters**: debris to walk around, a crouch passage (against `crouch_height = 1.1`), a single step at a threshold, a door.

### C. Light
- C1. Walls that lean inward face partly **downward**. Ceiling lights hit them at a grazing angle, and Godot does no GI here. Which placement lights them: ceiling centre, ceiling edge, low lights at the foot of each rib, or uplights along the floor edge?
- C2. Does room-to-room variation between dim and lit (study 03) survive in the new profile?

### D. Technical compatibility (not fight design)
- D1. Do sloped walls cause problems for player collision, bug navigation (1.0 m / 1.9 m clearance), shot and spit rays, or surface splatters?
- D2. Where do hatches and vents fit in an angled shell?

### E. Production: can we support ten levels?
- E1. **Authoring time** per corridor metre, per room and per level, from paper to a textured and validated build. Multiplied by ten, is it realistic?
- E2. **Handoff.** Can the user open a Claude-built map in TrenchBroom, tweak it and dress it by hand, then rebuild without losing either side's work? That needs readable brushes, grouping or layers per room, and sensible naming.
- E3. Can **one generic validator**, driven by markers placed in the map, replace per-map scripts?
- E4. Frame cost with the textured, lit kit, and no runtime batching.

## Textures: suggested approach

**Recommendation: in the style lab, develop geometry and textures together.
Lay out missions in Kenney grids, then swap them to the textured kit.**

**Why texture early in the lab.** In a low-geometry style, the texture does half
the work of reading the shape. Trim strips, panel seams and hazard edges show
where a form breaks. A bare trapezoid in grid texture looks unfinished. The same
trapezoid with a panel field, a trim band and a frame texture can look done.
Judging the shapes in greybox alone would undersell them. Textures also make the
lab easier to show and judge, as the user suggested.

**Why keep Kenney for mission layout.** Laying out a mission means proving
traversal, scale and progression, and the metric grid is the right tool for
that. The Kenney grids and their one-metre UV rule stay.

**Make the swap mechanical: role materials.** Name surfaces by role, not by
image: `wall_panel`, `wall_trim`, `frame`, `floor`, `ceiling`, `hazard`,
`grate`, `light_fixture`, `door`. During layout each role points to a Kenney
grid; for the proof it points to the real texture. The kit already puts trims
and frames at known heights, so the swap should be a material change rather than
a re-texturing pass.

The lab must verify one thing for this to hold: func_godot derives UVs from the
image's pixel size. A fixed texel-density standard (for example every texture
covers exactly 1 m or 2 m of wall) is needed so that swapping the image does not
change how often it repeats.

**Candidate texture sources to compare on the same geometry:**

1. **QUOD's released texture pack.** The creator's itch.io page states CC0 1.0
   and explicitly allows commercial use. Its contents (count, resolution, and
   whether it has normal or roughness maps) are not yet verified. Downloading it
   needs the user's approval.
2. **A small texture kit generated by Claude.** About 8–12 textures built by a
   standard-library Python script: panels, seams, bolts, grime, hazard stripes,
   grates, all in one palette. The repo already reads PNGs without Pillow, and
   writing them is equally simple. This gives full control of palette and trims,
   costs nothing and is unique to the game. The quality ceiling is the unknown.
3. **A paid or third-party pack**, if the user prefers. It needs the same
   license and compatibility check before use.

The **texture style** is a decision in its own right: crisp low-resolution
(nearest filtering, retro) versus smooth mid-resolution. It changes how the
whole game reads in a screenshot. Show both.

**User direction (2026-09-25): low-res, crunchy textures.** Packs don't have to
be final. Prefer sets that suit the Mars colony narrative.

### Downloaded candidates (2026-09-25, not yet in the project)

| Pack | Contents | Terms | Fit |
|---|---|---|---|
| [QUOD textures](https://daivuk.itch.io/quod-textures), Daivuk | 88 PNGs, mostly 64 and 128 px, plus odd-sized trims and decals; colour only, no normal maps | CC0 1.0, commercial use allowed | Excellent crunch, but QUOD's own identity is strong (skull emblems, logo, olive military, flesh). Cherry-pick panels, computer banks, grates, hazard, lights, pipes and doors. |
| [Quake-like Sci-Fi 64x64](https://level-eleven-games.itch.io/quake-like-texture-pack), Level Eleven Games | 300 textures at 64 px: concrete, painted concrete with blue/red/yellow/green lower bands, hazard, metal panels and trims, grates, vents, rust, pipes | The description says CC0, but itch metadata lists CC-BY 4.0. **Credit them to satisfy both.** | Best base for an industrial colony. The painted-band walls pair naturally with plinth geometry, which suits the texture-change rule. |
| [Retro sci-fi texture pack](https://potassifier.itch.io/retro-sci-fi-texture-pack), Potassifier | 5 textures, each at 128 px and 2048 px | "Use however you want… commercial use as well" | Small. Metal plates and a hazard wall are usable. |

Not downloaded:
- [Little Martian Retro Textures Mega Bundle](https://little-martian.itch.io/retro-textures-pack): $12, 715 textures, industrial/sci-fi/tech-lab. Commercial use is allowed but **redistribution is forbidden**, which matters if the repository is ever public.
- WRAD textures by wriks: CC0, but 1024 px phototextures, not crunchy.
- Screaming Brain Studios packs: CC0, generic.

**Mixing packs needs two unifying passes:**
- **One texel density**, in pixels per metre.
- **One shared palette.** Remap every chosen texture through a Red Breach palette so different packs read as one set.

**Missing from every pack: Mars.** No pack has colony signage, section numbers,
a colony logo, red dust streaks or regolith. That bespoke layer (decals,
signage, dust variants) is where a small generated or hand-made set is needed
on top of a base pack.

**Style reference: ShotHop** (Godot boomer shooter, Syntax Error
Entertainment). It is more rectangular than our target, but its textures and
environments are good. Its one Steam screenshot shows a triangulated steel-truss
ceiling, a strong single-colour fog grade and crates. The user's own preferred
shots or video moments would give a better study.

## Steps

### Phase 1: Style lab
- Build R-01's corridor → opening → machine room, with the straight built as **three short profile variants in sequence** (full trapezoid, straight lower wall with sloped upper, clipped box). Each variant is one extruded shape, so the comparison is cheap.
- Texture it in two candidate directions, per the section above.
- Run the light-placement comparison (C1) on each profile, with brightness measured rather than asserted.
- Log authoring time.
- **Exit:** the user picks a profile family, a texture direction and a lighting approach.

### Phase 2: Kit lab
- In the chosen style, build once each: straight, 45° single turn, square T, corridor-to-room opening, door frame, small room (~10 m), medium room (~16–20 m), a hall with real subdivision, a stair with landings, a threshold step, a crouch passage and a debris obstacle.
- Build the **generic validator** alongside it: walk points and lane clearance driven by markers placed in the map, stairs checked in both directions, headroom, and brush count checked against collision count.
- Walk the existing bugs through the sloped spaces to confirm D1: navigation, shot and spit rays, splatters. This is a compatibility check, not fight design.
- Try the **handoff** (E2): the user tweaks one room in TrenchBroom, then we rebuild.
- **Exit:** the kit walks cleanly in both directions. A one-page kit sheet gives every piece's dimensions and brush count. Joins need no special-case fill. The handoff works, or we know what it needs.

### Phase 3: Postcard test (cheap gate before the expensive one)
- In the kit lab, compose **3–5 shots meant to be posted**, using the presentation layer: lighting mood, fog, glow, emissive signs, a hero machine, steam or sparks, an exterior view if possible.
- **Exit:** the user would post at least one of them. If the kit cannot produce a postable frame in a lab, a whole mission will not either. Iterate here, where it is cheap.

### Phase 4: Proof mission
- Pick a mission that can be played and completed. The subject is open; the onboarding walkthrough is one candidate, and a new short combat mission is another.
- Run the staged process: walkthrough → paper plan (including the connecting-space pass) → enemy/pickup pass using the **combat log** → Kenney layout build → swap to the textured kit → presentation pass → playtest.
- Plan **screenshot moments** into the walkthrough from the start: where the money shots are and what makes them.
- Measure authoring time per phase (E1), and do a second handoff test at level scale.
- **Exit:** it plays through, and it looks like something to post for wishlists. If not, go back to the phase whose question failed.

### Phase 5: Style sheet, keep/throw, clean house
- Write the style sheet / construction standard: profile, kit, textures, lighting, presentation, and the rules that survived.
- Build the **keep/throw ledger** from the findings log.
- Tag the dev state so nothing is lost, remove what was thrown, and rewrite AGENTS.md short around the standard.
- Decide the **build-split** for the ten levels (who builds, who tweaks, who dresses), using the E1 and E2 evidence.

## Rules for the lab phase

- **Shape over stuff.** Each room gets one dominant object that explains its function, plus a few supporting pieces. Structure is built from brushes.
- **Hand-editable output.** Anything Claude generates must be readable and editable in TrenchBroom, because the user's final dressing depends on it.
- **One validator, not one per map.**
- **Existing rules stay in force** until a lab replaces them: the architecture rules and the corridor numbers.
- **Log time and findings as we go.**
- Versioning and commit rules are unchanged: commit only on request, one version increment per commit.

## Deliberately out of scope

Wall-crawling navigation (FR-003), automatic pressure doors, final meshes,
audio (FR-004), power-loss events (FR-006) and weapon resources (FR-001) stay
deferred. The kit should leave room for them, not build them. Presentation
effects are in scope only as far as the postcard test needs them.
