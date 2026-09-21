# Registration / continuous flat floor

The user chose one continuous floor material when removing the 0.25 m lowered pathway. Approved intent: bring all four recessed strips to floor 0, preserving every doorway, furnishing and route. No contrasting walkway material or new border is added.

The A1 floor consolidates into one slab over its existing 52 x 32 m footprint. Only the former recessed strips gain height; every surrounding occupied floor stays at 0 m. Material: existing Kenney Dark/texture_06 with one-metre repeats.

This supersedes the walkway geometry and orange floor/step palette in the historical F03c drawings. The staff door, office furnishings, Registration view and Screening remain.


Status: **built and validated as layout 10**. [Six rendered views](freight-registration-flat-floor.png) were inspected. All 217 freight checks and nine greybox checks pass, including flat-floor samples, walking/sprinting/backpedalling/strafing, staff-door obstruction/reversal/reset and mission progression. The map has 1,221 brush collisions and 14,276 nondegenerate triangles with accurate one-metre repeats.

The source edit replaces nine floor-support/raised-section brushes with one slab, preserving the other 1,220 brushes exactly. No furniture, door, light or Screening asset moves. The existing step test routes now verify continuous floor at 0 m. Historical F03c floor and palette drawings remain as development records; this document is the current floor intent. Project version remains 0.0.009; no commit was requested.

User material rule: support a change in texture with actual geometry—a rise, drop, border brush, trim or physical seam. A flat uninterrupted floor uses one material. Do not add a contrasting route stripe simply to replace the removed trench.
