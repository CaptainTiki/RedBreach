"""Measure which pack textures can tile, and in which directions.

    python tools/audit-textures.py

Writes docs/texture-catalog.json (read by the scene writers, which refuse a
non-tiling texture in a role that repeats) and docs/texture-catalog.png (a
contact sheet: green = tiles both ways, amber = one way, red = a feature that
is used once and never repeated).

User rule, 2026-09-25: textures that do not tile must not be used where a
surface repeats. The QUOD heat pipe (dark to bright, then repeat) was the case
that made this a rule.

A texture tiles along an axis when:
  SEAM  the jump across the wrap (last column -> first column) is no bigger
        than the texture's own typical neighbouring-column difference, and
  DRIFT the mean brightness does not drift across the texture: the first and
        last quarters along that axis match, so a repeat does not band.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / 'RedBreach/textures'
FOLDERS = ['packs/quod', 'packs/lvl11', 'packs/potassifier', 'style_common']
SEAM_RATIO = 2.2      # wrap jump allowed, in multiples of the typical internal step
DRIFT_LIMIT = 0.12    # max mean-brightness difference between opposite quarters (0-1)


def lum(px):
    r, g, b = px[:3]
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def measure(path):
    im = Image.open(path).convert('RGBA')
    w, h = im.size
    px = im.load()
    L = [[lum(px[x, y]) for x in range(w)] for y in range(h)]
    alpha = sum(1 for y in range(h) for x in range(w) if px[x, y][3] < 128) / (w * h)

    def col(x): return [L[y][x] for y in range(h)]
    def row(y): return L[y]
    def diff(a, b): return sum(abs(p - q) for p, q in zip(a, b)) / len(a)

    inner_h = sum(diff(col(x), col(x + 1)) for x in range(w - 1)) / max(1, w - 1)
    inner_v = sum(diff(row(y), row(y + 1)) for y in range(h - 1)) / max(1, h - 1)
    seam_h = diff(col(w - 1), col(0))
    seam_v = diff(row(h - 1), row(0))
    q = max(1, w // 4)
    drift_h = abs(sum(sum(L[y][x] for x in range(q)) for y in range(h)) / (q * h)
                  - sum(sum(L[y][x] for x in range(w - q, w)) for y in range(h)) / (q * h))
    q = max(1, h // 4)
    drift_v = abs(sum(sum(L[y]) for y in range(q)) / (q * w) - sum(sum(L[y]) for y in range(h - q, h)) / (q * w))
    # Edge steps: how sharply each edge line differs from the line inside it.
    # A bordered PANEL has a designed border, so its wrap seam is no bigger
    # than its own border step and repeats as a panel grid.
    # A bevel is a highlight on one edge and a shadow on the other, so the
    # wrap seam of a bevelled panel is the SUM of its two border steps.
    step_h = diff(col(0), col(1)) + diff(col(w - 1), col(w - 2))
    step_v = diff(row(0), row(1)) + diff(row(h - 1), row(h - 2))

    def cls(seam, inner, step, drift):
        if drift > DRIFT_LIMIT:
            return 'X'                     # a gradient: repeating it bands
        if seam <= max(inner * SEAM_RATIO, 0.04):
            return 'T'                     # seamless (a jump under 4% is invisible)
        if seam <= step * 1.25 + 0.03:
            return 'P'                     # a panel border: repeats as a grid
        return 'X'
    class_h = cls(seam_h, inner_h, step_h, drift_h)
    class_v = cls(seam_v, inner_v, step_v, drift_v)
    tiles_h, tiles_v = class_h != 'X', class_v != 'X'
    return dict(size=[w, h], tiles_h=tiles_h, tiles_v=tiles_v, class_h=class_h, class_v=class_v,
                seam_h=round(seam_h, 4), seam_v=round(seam_v, 4),
                inner_h=round(inner_h, 4), inner_v=round(inner_v, 4), drift_h=round(drift_h, 4), drift_v=round(drift_v, 4),
                transparent=round(alpha, 3))


# Content the numbers cannot see: a hazard band or a single emblem painted
# into a panel repeats as a stripe. These are features, never repeated.
FEATURES = {'packs/quod/tex238': 'hazard band along the bottom', 'packs/quod/tex43': 'hazard band along the bottom',
            'packs/quod/tex84': 'hazard band', 'packs/quod/tex18': 'door with an emblem', 'packs/quod/tex9': 'door and hatch',
            'packs/quod/tex64': 'door and knobs', 'packs/quod/tex40': 'EXIT sign', 'packs/quod/tex75': 'logo',
            'packs/quod/tex97': 'memorial', 'packs/quod/tex23': 'skull emblem', 'packs/quod/tex82': 'skull emblem',
            'packs/quod/tex91': 'skull emblem', 'packs/quod/tex92': 'skull emblem', 'packs/quod/tex188': 'skull emblem',
            'packs/quod/tex228': 'skull emblem', 'packs/quod/tex241': 'computer', 'packs/lvl11/MetalPanel-01V_64': 'numbered door'}
# Checked by eye in a 2x2 tiled preview: the numbers call these X, but the
# wrap reads as a designed panel edge.
PANELS = {'packs/quod/tex8': 'bevelled panel rows'}
catalog = {}
for folder in FOLDERS:
    for png in sorted((TEX / folder).glob('*.png')):
        key = f'{folder}/{png.stem}'
        catalog[key] = measure(png)
        if key in PANELS:
            catalog[key].update(tiles_h=True, tiles_v=True, class_h='P', class_v='P', panel=PANELS[key])
        if key in FEATURES:
            catalog[key].update(tiles_h=False, tiles_v=False, class_h='X', class_v='X', feature=FEATURES[key])

(ROOT / 'docs/texture-catalog.json').write_text(json.dumps(catalog, indent=1), encoding='utf-8')
both = sum(1 for c in catalog.values() if c['tiles_h'] and c['tiles_v'])
one = sum(1 for c in catalog.values() if c['tiles_h'] != c['tiles_v'])
none = sum(1 for c in catalog.values() if not c['tiles_h'] and not c['tiles_v'])
print(f'TEXTURE_CATALOG: {len(catalog)} textures; {both} tile both ways, {one} one way, {none} features (no tiling)')

# Contact sheet, grouped by pack, bordered by tiling class.
cell, pad, label = 72, 6, 14
cols = 24
names = list(catalog)
rows = (len(names) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (cell + pad) + pad, rows * (cell + label + pad) + pad + 40), '#101b25')
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('arial.ttf', 11)
    big = ImageFont.truetype('arial.ttf', 16)
except OSError:
    font = big = ImageFont.load_default()
d.text((pad, 8), 'Per axis (H, V): T seamless, P panel border (repeats as a grid), X never repeat.  green: both repeat   amber: one way   red: feature, use once', font=big, fill='#e8eef2')
for i, name in enumerate(names):
    c = catalog[name]
    x = pad + (i % cols) * (cell + pad)
    y = 40 + pad + (i // cols) * (cell + label + pad)
    im = Image.open(TEX / f'{name}.png').convert('RGB')
    s = min(cell / im.width, cell / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.NEAREST)
    sheet.paste(im, (x, y))
    colr = '#4caf7d' if c['tiles_h'] and c['tiles_v'] else ('#e0a33a' if c['tiles_h'] or c['tiles_v'] else '#e05a4a')
    d.rectangle([x - 2, y - 2, x + cell + 1, y + cell + 1], outline=colr, width=2)
    tag = c['class_h'] + c['class_v']
    d.text((x, y + cell + 2), f'{name.split("/")[-1][:12]} {tag}', font=font, fill='#c9d4da')
sheet.save(ROOT / 'docs/texture-catalog.png')
