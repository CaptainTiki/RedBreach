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

## Adding future entries

Give each idea the next stable identifier (FR-002, FR-003, and so on), a short title, status, a reason to revisit it, the intended change, and a practical completion check. Keep uncertain details marked as open. When an item enters active work or is completed, update its status and link the relevant plan or implementation notes.
