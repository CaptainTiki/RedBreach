# Architecture study 03 — rhythm of change

2026-09-22. The user's own in-game walkthrough notes from Doom 3 (not
`admin.map` read as text this time — actually playing it), recorded before any
new lab geometry exists. These are direct observations, not measurements; no
Red Breach geometry changed.

## The finding

Study 02 found the room-size mismatch. Study 02's structural pass (junction
splitting) found the corridor-length mismatch. This pass names the thing
underneath both of them:

> **The constant in Doom 3 isn't small rooms, short corridors, machinery, or
> steps individually. It's the rate at which *something* changes.**

Walking it, almost nothing stays the same for long: lighting level, floor
height, what the walls are doing, whether you're upright or ducking. The user's
own summary is the cleanest statement of it — *"the biggest thing that stayed
the same would be the amount of changes from 1 thing to another."*

That reframes small rooms and short corridors as two symptoms of one cause,
not two separate rules to apply. A room only *needs* to be small if it's
carrying one change; ours are large because each one is asked to hold its
whole department's worth of sameness.

## What the user noticed, itemized

### Lighting varies room to room

Lit rooms and dimmer ones (not dark — dim), alternating. Not a single
consistent light level applied uniformly and not a horror-dark/lit binary
either — a working building's actual variation in fixture density and fitting
type. `FR-006`'s power-loss work already treats light level as a legible
signal; this extends it to *authored* variation, not just outage.

### Near-universal small verticality

The user's list: a step up into an admin desk, a catwalk overlooking a lobby,
a ladder up a floor mid-hallway, a single step up or down entering a room from
a hallway. Almost no room was flat-floor-to-flat-floor with its neighbors.

This is a different scale of thing from `architecture-language.md`'s stair
rules (edge-hugging stairs, landings that reveal the destination) and from
FR-005 (upper catwalk return views) — those are about *the* stair, the one
big vertical move in a sequence. This is smaller and constant: a threshold
riser, a half-step, a plinth under one desk. Almost every room has *some*
elevation change even when it has no stair at all.

### Texture changes have a physical reason — confirmed, not just ruled

`architecture-language.md` already states this as a rule (a material change
needs a raised/lowered surface, a border brush, trim, or a seam — not colour
alone), decided after the Registration recess debate. Walking Doom 3 shows
it's not a stylistic preference id imposed on themselves — the step-up/step-
down verticality above *is* what most of their texture transitions are riding
on. The rule and the observation are the same mechanism seen from two sides.

### Wall machinery is active, not decorative

Not flush service panels — things pumping, spinning, or audibly running,
usually built as a mass that projects into the room enough that the player
routes around it. `architecture-language.md` already names "service recess"
and "machinery island," but as placed equipment. Add motion and sound to the
vocabulary: a service element should be doing something you can see and hear,
and it should cost the player a step, not just visual interest.

### Crawlspaces

Not yet in any Red Breach document. Low openings the player ducks through —
a distinct traversal beat, different from a door or a stair. Worth testing as
its own vocabulary item rather than folding it into hatches (which are
enemy-entry features per `architecture-language.md`'s bug-hatch section, a
different purpose even if the geometry rhymes).

## Vocabulary to add to the vocabulary tables

*(Extends the tables in `architecture-language.md` and study 01 — same
format.)*

| Element | Intended feeling / role | Brush or prop treatment |
|---|---|---|
| Threshold riser | Marks a room's entry as a distinct event even with no stair | Single step, 1-2 risers, up or down, at or near the doorway |
| Local plinth | Gives one workstation/feature its own footing | Low platform under a desk, console, or machine, edged so it reads as deliberate |
| Active service mass | A wall stops being a wall and starts being a thing | Projecting equipment with implied motion/sound, routed around, not flush |
| Crawlspace | A third traversal state besides walk and stair | Low, short, connects two spaces or shortcuts a loop; test clearance against the standing capsule and crouch height |
| Lighting variation | Rooms read as individually lit, not one uniform wash | Vary fixture density/type per room; keep "dim" distinct from "dark" (no unlit bay unless it's meant to read as broken, per FR-006) |

## The structural rule: unprogrammed space is the level

Recorded 2026-09-22 after the revision 03 plan failed on exactly this point.
It is the single easiest finding to lose, because every instinct in level
planning pulls the other way.

**Doom 3 is connective tissue punctuated by programmed rooms. It is not
programmed rooms joined by corridors.**

The user's count of the admin floor: roughly **9 rooms carrying story beats**,
and roughly **12 further spaces that have no reason to exist except that they
make the journey interesting.** The second group is the larger one, and study
02's measurements agree — of admin's ground story, **79% of the walkable floor
is below room scale** and only 21% reads as a proper room. Only 7 spaces in
the whole building are wide enough to classify as rooms at all; the largest is
142 m².

An unprogrammed space has a *shape* idea, not a *function*:

- a corridor that widens into a bay with pipes running through it
- a pump room: three pumps, a walkway around them, two doors
- a chamber with a railing, a step down, and two ways out
- a bend that swells into a room and narrows back into a bend
- a space you cross diagonally because the equipment makes you

None of these can be derived from a walkthrough, because a walkthrough only
knows about beats. They have to be added deliberately, as their own pass,
*after* the beats are placed and *before* the plan is called finished.

### How this went wrong in revision 03

The plan gave every space a job — reception, comms, armory, range, dispatch,
records, supply, store, lockers, break room, bath, closet, machinery, plant.
Every one justifiable from [the walkthrough](onboarding-walkthrough.md). The
result measured **82% room / 18% connective**, almost the exact inverse of the
reference, at 620 m² against admin's 1,664 m².

A space-allocation brief is the wrong tool. It produces a building that is
correct and dead. The freight mission is the same error at larger scale.

### The working ratio

Treat the beats as roughly a fifth of the level by area, and budget the rest
for spaces that carry no story at all. When a plan cannot reach that ratio, the
fix is never to enlarge the programmed rooms — it is to add more unprogrammed
space between them.

## A candidate rule to test in the new lab

Not yet adopted — a hypothesis to check when the new lab gets built:

> **Nothing should go unchanged for more than N meters/seconds** — light
> level, floor height, what the wall is doing, or footing (standing/ducking).
> Pick N empirically once the lab is walkable; the Doom 3 corridor-run numbers
> from study 02 (median 3.3 m between junctions, 90th percentile 16.1 m)
> are a starting reference, not a target to hit exactly.

This is the same shape as the existing 4 m rib pitch and 2:1 room-proportion
rules — a numeric register the level can be audited against — but for *change*
instead of *dimension*.

## Next

Build the new lab (separate from freight, tied to the game's actual onboarding
/ sign-in sequence per the user's plan) as the test bed for this rule plus the
study 02 density/corridor findings together. Use this document's itemized list
as the walkthrough checklist: does every room have a lighting identity, a
verticality reason, at least one active service element, and does circulation
change (turn, step, width, or light) on the same rough interval Doom 3 does?
If the combined language doesn't survive being walked at our movement speed
and combat pacing, that failure gets recorded here before any freight
remodeling is attempted, per the user's fallback plan.
