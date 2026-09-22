# Future Refinements

A living list of ideas, cleanup, and improvements to revisit after the prototypes prove the gameplay. Record useful decisions here so they survive between sessions without expanding the current task.

Items in this document are deferred unless explicitly brought into the active plan. Prototype code can stay simple while we test feel; document the intended refinement instead of stopping the gym work to redesign everything.

## FR-001: Per-weapon configuration resources

**Status:** Agreed future direction; deferred.

**Revisit:** When refining the weapon system after the first Combat Gym pass, ideally before adding a second weapon with different handling.

**Intent:** Each weapon should carry its own tuning in a Godot resource (`weapon.tres`, or a named asset such as `pistol.tres`). The shared weapon behavior reads the equipped weapon's settings. ADS handling belongs alongside the normal weapon stats, so different weapons can aim, move, fire, and reload differently without adding weapon-specific constants to the player controller.

### Configuration to keep together

| Area | Per-weapon settings |
|---|---|
| Firing | Damage, range, and fire rate, with an explicit unit such as rounds per minute |
| Ammunition | Magazine capacity and maximum reserve ammo as separate limits |
| Reload | Reload duration in seconds |
| Normal recoil | Camera kick, recoil-induced aim drift, and recovery tuning |
| ADS view | FOV amount or zoom setting |
| ADS transition | Time to enter and leave ADS, in seconds; separate from movement speed |
| Weapon placement | Hip-fire and ADS positions and rotations, aligning the sights with the actual aim |
| ADS movement | Movement speed multiplier, applied to the current standing/crouched base speed |
| ADS recoil | Per-weapon camera-kick and aim-drift reductions or overrides |

The values in the [Combat Gym scope](combat-gym-scope.md) are initial playtest values, not universal settings for every weapon. During refinement, decide whether ADS stores a target FOV or an adjustment relative to the player's normal FOV, and use that convention consistently.

### Implementation boundaries for that refinement

- Keep weapon configuration in the resource and shared firing/ADS behavior in reusable code. StateCharts continues to own the relevant behavior transitions.
- Keep live state on the weapon instance: current ammo, reload progress, cooldowns, and current recoil offsets. Firing or reloading must not mutate a shared configuration asset.
- Changing weapons must apply the new weapon's settings and clear temporary FOV, pose, recoil, and movement effects from the previous weapon.
- Player preferences such as normal FOV and mouse sensitivity remain player settings; the weapon supplies its aiming adjustments.

### How we will know it is done

Two weapons with noticeably different handling can use the same behavior code, with their differences defined in their resources. Editing one resource changes only that weapon's tuning. Equipping, aiming, firing, reloading, and switching restores the appropriate settings without stale offsets or accumulated movement penalties. Repeat the Combat Gym comparisons to confirm that the sights, actual shot direction, recoil, and movement remain consistent.

This entry records the intended design. It does not request an immediate refactor or introduce a weapon resource into the project yet.

## FR-002: Bug presentation and impact refinement

**Status:** Deferred until the first combat playtest gives us useful feel feedback.

**Intent:** Replace the primitive six-legged bug and flattened corpse with authored animation and a death reaction. Revisit limb hit areas alongside the final silhouette; the current body capsule is the damage target. Tune the attack cue, hit sound, green droplets and surface splatters together so shots and impending attacks remain readable at combat distances.

**Completion check:** Players can read a wind-up, distinguish a hit from a kill, and predict which visible parts receive damage. Preserve the dodgeable committed lunge, cover obstruction, bounded effects, and complete reset checks. This entry does not authorize importing an asset pack or changing the current weapon architecture.

## FR-003: Small-bug wall and ceiling navigation

**Status:** Future capability under discussion; no runtime implementation yet. The user explicitly wants reliable pathfinding for future levels, whether graph-based or mesh-based, rather than a solution tied to the current gym.

**Intent:** Small bugs pursue the player over connected floors, walls and ceilings, creating pressure from multiple surfaces while the player retreats. They retain their one-hit role. The system should cope with branching rooms, corners, obstructions, closed doors and changing player position, and survive the TrenchBroom alteration pipeline.

### Proposed architecture to investigate

- Generate shared navigation data from simplified, explicitly crawlable level surfaces when the map is built. Preserve surface orientation and available body clearance. Avoid dense sampling of decorative triangles or requiring designers to hand-place every route. Exclude inaccessible/hidden brush faces, disconnected surfaces and gaps that cannot be crossed.
- Prefer a graph of connected surface patches with valid transition boundaries, plus smooth movement within patches. A* can select a route over that graph. Sparse waypoints can support special transitions, vents and authored hints, but a trail of the player's previous floor positions cannot be the primary navigation system for ceiling pursuit or alternate routes.
- Godot's AStar3D can provide the graph search; it does not automatically generate walkable surfaces, test body clearance or produce surface-constrained smoothing. Those are separate engineering requirements. Evaluate this against multiple oriented native navigation maps with a higher-level connection graph before selecting the implementation. Retain native ground navigation where it remains appropriate.
- Give the crawler a surface-following movement controller: adhesion, body/hitbox orientation, smooth inside/outside corner transitions, collision-safe movement and recovery from lost contact. Paths and their smoothing must stay on reachable surfaces instead of cutting through solids or bridging arbitrary gaps. Keep movement/attack/death transitions in editable StateCharts.
- Pursuit should select reachable attack positions relative to the player. A ceiling bug cannot simply target the player's feet through open air. Descending, dropping and lunging need explicit, readable actions and legal paths. A killed ceiling crawler should detach and fall rather than remain glued overhead.
- Doors and gameplay blockers change relevant connections; near-neighbor separation handles other bugs without pushing them off the surface. Navigation debug views should show connected patches, rejected clearance, chosen paths and failed transitions.

### Cost and workflow

This is a substantial reusable navigation/movement feature. Runtime overhead is expected to be manageable with a shared precomputed graph, compact surfaces, bounded and staggered path requests, and local contact checks, but this is an engineering expectation rather than a benchmark. Pathfinding, crowd separation, physics/contact checks and animation should be profiled separately. Do not scan or rebuild the whole level for each bug every frame. Scope the first system to static level architecture plus supported dynamic blockers; moving crawlable machinery and deforming terrain are separate future requirements.

Rebuilding a TrenchBroom map must also rebuild/validate crawler navigation, flag stale geometry, and preserve designer annotations for special routes where possible. Bake diagnostics and predictable editing matter as much as a successful chase in one room.

### Completion evidence before wider rollout

Use the proposed architecture in a small reviewed navigation test layout first: floor-to-wall-to-ceiling and back, inner and outer corners, a doorway, an obstacle with two alternative routes, and an unreachable area. Require pursuit after the player changes rooms or reverses direction; rerouting or explicit stopping at blocked doors; collision-safe separation; correct shots and falling death on every orientation; and full reset. Move a wall in TrenchBroom and rebuild to prove the paths follow the edited geometry. Profile representative groups (for example 6, 20 and 50 crawlers) without treating those counts as promised performance targets.

This test should exercise the intended reusable system. No level geometry, wall-crawling code or navigation replacement is authorized by this design note alone.

### Technical references checked

- [Godot 3D navigation overview](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_introduction_3d.html): graph pathfinding versus movement within mesh-defined areas.
- [AStar3D](https://docs.godotengine.org/en/stable/classes/class_astar3d.html): connected weighted points in 3D; graph construction belongs to the caller.
- [Navigation map orientation](https://docs.godotengine.org/en/stable/classes/class_navigationserver3d.html#class-navigationserver3d-method-map-set-up) and [current region implementation](https://github.com/godotengine/godot/blob/master/modules/navigation_3d/nav_region_3d.cpp): each native map has an up direction; current upstream code reports regions rotated 90 degrees or more away from it. This is a reason to investigate the backend, not a claim that arbitrary-surface navigation is impossible in Godot.
- [NavigationAgents](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationagents.html): movement is supplied by game code; avoidance is separate from pathfinding and does not inherently know the collision world or navigation surface.

## FR-004: Distinct bug alert and ambush audio

**Status:** Agreed audio-pass refinement; deferred. The user accepted the revision 04 rear-ambush concept after moving D's front enemies deeper into the room. This records future audio work, not a request to change the current prototype.

**Why revisit:** The player could hear the hatch's metallic ting, turn to engage the rear bug and backpedal away from D successfully. The missing or insufficiently readable bug screech left the hatch as the recognizable tell. The player should be able to recognize a newly revealed nearby threat without already knowing an ambush is coming.

**Intent:** Give bugs an audible initial awareness/engagement screech, and make the ambush tell recognizably distinct from ordinary pursuit or "I'm walking toward you" sounds. An ambush screech should communicate a new, close threat that deserves attention while the player is facing another fight. Preserve the hatch cue as supporting information; the bug vocalization must carry its own meaning.

- Differentiate the ambush vocal's character and rhythm from routine pursuit chatter and attack wind-ups; do not rely only on making the same sound louder.
- Place the tell at the actual bug/emergence location so direction and distance help the player locate danger behind or beside them. Align it with detection or emergence, not remote encounter arming before the bug appears.
- Keep the initial alert readable through gunfire, reloads, hatch noise and other bugs. Control repetition and overlapping vocals so ordinary pursuit does not drown out a new ambush tell.
- Exact sounds, mixing and trigger details remain for the audio pass. Preserve the approved encounter spacing and response opportunity while evaluating the cues.

**Completion check:** On a first encounter with the ambush, a player looking toward D can distinguish the nearby ambush screech from routine pursuit, recognize its direction and turn to respond without prior knowledge of the hatch. Check this while firing/reloading with multiple active bugs, and confirm repeated pursuit sounds do not falsely signal another ambush.

Source: [revision 04 accepted playtest](rear-hatch-plan.md#revision-04-human-playtest--concept-accepted). Coordinate this with [FR-002 bug presentation](#fr-002-bug-presentation-and-impact-refinement).

## FR-005: Return views through upper routes

**Status:** User-proposed level-design principle; deferred to a suitable spatial plan.

Use the same room more than once from different positions or heights. The player first sees a catwalk from below, travels through other rooms, and later returns on that catwalk. The user explicitly notes that the upper route need not be accessible by stairs from the lower room. Their supplied Doom 3 BFG reference illustrates the intended visual reconnection.

Plan the upper entrance, exit, elevation and sightlines on paper together with the surrounding rooms. Preserve card/gate dependencies and check jump/drop bypasses. Give the upper return a purpose: route progress, orientation, a changed encounter angle or a visible consequence of an earlier action. Do not add an isolated decorative balcony and claim it is a working loop.

**Completion check:** The player can recognize the earlier room from the upper route, understand how the journey reconnects, and traverse both intended approaches without breaking progression. Review combat crossfire and enemy access in the later populated pass. F-02 reception does not implement this feature; its current 3.5 m ceiling cannot accept a usable upper floor.

## FR-006: Power loss as a mission event

**Status:** User-proposed; deferred until the mission redress needs it.

The corridor kit now lights **every** bay by default, so an unlit bay is no
longer a rhythm — it is a deliberate statement that something is wrong. The user
proposed making that statement dynamic rather than authored: **the bugs cut the
power and the hallway lights go out during play.**

The kit is already shaped for it. `S.LIGHT_TIERS` pairs a fitting material with
a light, and `C.LIGHT_PLANS` selects which bays use which tier, so going dark is
a material swap plus disabling the OmniLight3D nodes — no geometry edit at all.
The lab already proved the one-word change works; this is the same change made
at runtime.

- Swap the emissive fitting material for the dark one and disable that bay's
  lights together. An **off fitting must never glow** — a strip that emits while
  its bay stays dark reads as a mistake, and that rule does not relax just
  because the change is dynamic.
- Keep one or two bays **flickering** rather than fully out, with sparks. A
  corridor that is uniformly dark is less legible than one that is intermittently
  lit, and the flicker is what tells the player the outage is damage rather than
  a design choice.
- Decide what the player can still see by. Emissive materials do not illuminate
  anything in Godot without GI, so a blackout with the OmniLights off is a true
  blackout — some other source has to carry it, or the encounter has to assume
  the player cannot see.
- The event belongs in a StateChart like every other behaviour transition, and
  the restored state must be reachable so a corridor is not permanently dark
  after a reset.

**Completion check:** Power can be cut and restored during a mission; affected
bays swap fitting material and lose their lights together with no geometry
rebuild; one or two bays flicker with sparks rather than going fully dark; the
player can still navigate or is deliberately meant not to; and a mission reset
returns the corridor to its lit state.

Source: corner playtest 01, [architecture-lab-corner-playtest.md](architecture-lab-corner-playtest.md).
Relates to [FR-004 distinct bug alert and ambush audio](#fr-004-distinct-bug-alert-and-ambush-audio)
— a blackout and an ambush cue arriving together must not mask each other.

## Adding future entries

Give each idea the next stable identifier (FR-006, FR-007, and so on), a short title, status, a reason to revisit it, the intended change, and a practical completion check. Keep uncertain details marked as open. When an item enters active work or is completed, update its status and link the relevant plan or implementation notes.
