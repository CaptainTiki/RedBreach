# Blockout textures

The user supplied Kenney's prototype textures in `RedBreach/textures/greybox/`: 78 PNGs across Dark, Light, Green, Orange, Purple, and Red, with 13 variants per color. They are already part of the committed project.

Prefer the plain grid/checker variants for future blockout work. Keep geometry sized by the approved level plan and tested player clearances. Use door/window diagrams only when an opening intentionally matches the diagram; do not resize gameplay openings to fit an image.

## Useful verified variants

- `texture_01.png`: fine grid.
- `texture_03.png`: fine grid with diagonal guides.
- `texture_05.png`: fine grid with center crosses.
- `texture_06.png`: larger checker squares with borders.
- `texture_07.png`: larger checker squares.
- `texture_08.png`: larger checker squares with center crosses.
- `texture_09.png`: stair diagram.
- `texture_10.png`: door diagram.
- `texture_11.png`: window diagram.

## Scale in this project

The inspected textures are 1024 x 1024 pixels. A printed `1024 x 1024` label describes image resolution; it does not establish meters. Our map conversion remains 32 map units per meter.

For the plain grids, use a full texture repeat of **2 m**, with **0.25 m fine squares** and **1 m half-texture squares**:

- In TrenchBroom, set both face texture scales to **0.0625** for these 1024 px images.
- Calculation: `1024 * 0.0625 / 32 = 2 m` per full repeat.
- The existing gym textures are 128 px at scale 0.25, so their full repeat is 1 m. Do not copy that face scale onto the larger Kenney files: it would make a full repeat 8 m.
- Keep horizontal and vertical scales equal. Check against a known 1 m brush before a broad material pass.

The current gym retains its existing materials in this movement pass. Apply these conventions when we choose the next blockout texture pass. The func_godot base texture directory already points at `res://textures`; preserve the `greybox/<Color>/texture_NN` paths when selecting materials.
