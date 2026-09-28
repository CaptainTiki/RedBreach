"""Draw the freight v2 2D plan: docs/freight-v2-plan.png.

Paper only; never edits a map. Every shape comes from tools/freight_v2.py, and
the drawing refuses to run while the plan's self-checks report a problem.
Colour is floor elevation: deep blue at the pump pit (-5.5), grey at the
airlock (0), amber at the archive (+4). Label positions are presentation only.
"""
from pathlib import Path
import math
import sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parent))
import freight_v2 as F

ROOT = Path(__file__).resolve().parents[1]
problems = F.check()
if problems:
    raise SystemExit('plan problems:\n' + '\n'.join(problems))

SC = 14.0
XMIN, XMAX, YMIN, YMAX = -38.0, 66.0, -30.5, 67.5
OX, OY = 24, 96
PLAN_R = OX + (XMAX - XMIN) * SC
RX = PLAN_R + 36
W, H = int(RX + 500), int(OY + (YMAX - YMIN) * SC + 90)
BG = (16, 27, 37)
EDGE, TEXT, NOTE, ACCENT = (201, 212, 218), (232, 238, 242), (159, 178, 191), (232, 189, 119)
im = Image.new('RGBA', (W, H), BG + (255,))
d = ImageDraw.Draw(im)


def font(n, bold=False):
    return ImageFont.truetype('arialbd.ttf' if bold else 'arial.ttf', n)


def P(x, y):
    return (OX + (x - XMIN) * SC, OY + (YMAX - y) * SC)


def layer():
    """Draw translucent things on their own layer, then composite."""
    over = Image.new('RGBA', im.size, (0, 0, 0, 0))
    return over, ImageDraw.Draw(over)


def flatten(over):
    global im, d
    im = Image.alpha_composite(im, over)
    d = ImageDraw.Draw(im)


def text(x, y, s, n=13, c=TEXT, anchor='la', bold=False):
    d.text((x, y), s, font=font(n, bold), fill=c, anchor=anchor)


def label(x, y, lines, anchor='m', leader=None):
    """Plan-anchored label with a dark backing so it reads over any floor colour.
    A leader is the plan point the label describes, joined by a thin line."""
    cx, cy = P(x, y)
    if leader:
        d.line([(cx, cy), P(*leader)], fill=(232, 238, 242), width=1)
    widths = [d.textlength(s, font=font(n, b)) for s, n, c, b in lines]
    hts = [n + 3 for s, n, c, b in lines]
    wmax, htot = max(widths), sum(hts)
    x0 = {'m': cx - wmax / 2, 'l': cx, 'r': cx - wmax}[anchor]
    y0 = cy - htot / 2
    over, o = layer()
    o.rounded_rectangle([x0 - 4, y0 - 2, x0 + wmax + 4, y0 + htot + 1], 3, fill=BG + (175,))
    flatten(over)
    yy = y0
    for (s, n, c, b), w, h in zip(lines, widths, hts):
        xx = {'m': cx - w / 2, 'l': cx, 'r': cx - w}[anchor]
        text(xx, yy, s, n, c, 'la', b)
        yy += h


STOPS = [(-5.5, (29, 58, 92)), (-3.0, (47, 88, 104)), (-1.5, (70, 98, 112)), (0.0, (96, 104, 114)), (1.0, (134, 118, 84)),
         (4.0, (178, 140, 58))]


def hcol(h):
    if h <= STOPS[0][0]:
        return STOPS[0][1]
    for (h0, c0), (h1, c1) in zip(STOPS, STOPS[1:]):
        if h <= h1:
            t = (h - h0) / (h1 - h0)
            return tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3))
    return STOPS[-1][1]


def hl(h):
    return '0' if abs(h) < 1e-9 else f'{h:+.2f}'.rstrip('0').rstrip('.').replace('-', '−')


def poly(pts, fill, outline=EDGE, w=2):
    q = [P(*p) for p in pts]
    if fill is not None:
        d.polygon(q, fill=fill)
    if outline is not None:
        d.line(q + [q[0]], fill=outline, width=w)


def dashed(q, fill, width=2, dash=9, gap=6, closed=False):
    q = list(q) + ([q[0]] if closed else [])
    for a, b in zip(q, q[1:]):
        L = math.dist(a, b)
        t = 0.0
        while t < L:
            t1 = min(L, t + dash)
            d.line([(a[0] + (b[0] - a[0]) * t / L, a[1] + (b[1] - a[1]) * t / L),
                    (a[0] + (b[0] - a[0]) * t1 / L, a[1] + (b[1] - a[1]) * t1 / L)], fill=fill, width=width)
            t += dash + gap


def hatch(pts, fill, step=9, width=1):
    """Diagonal hatch clipped to a polygon, via a mask."""
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).polygon([P(*p) for p in pts], fill=255)
    lines = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lines)
    for k in range(-H, W, step):
        ld.line([(k, 0), (k + H, H)], fill=fill, width=width)
    over = Image.new('RGBA', im.size, (0, 0, 0, 0))
    over.paste(lines, (0, 0), mask)
    flatten(over)


# --- title ----------------------------------------------------------------------------
text(OX, 20, f'FREIGHT ACCESS v2 / 2D PLAN, REVISION {F.REVISION:02d}', 30, TEXT, bold=True)
text(OX, 60, 'Stage 2 for review. Rooms by the recipe: walk path, blockers, vertical interest, then walls. '
     'Colour = floor elevation. North is up; grid = 5 m.', 15, ACCENT)

# 5 m grid, faint.
for gx in range(int(math.ceil(XMIN / 5)) * 5, int(XMAX) + 1, 5):
    d.line([P(gx, YMIN), P(gx, YMAX)], fill=(24, 38, 50), width=1)
for gy in range(int(math.ceil(YMIN / 5)) * 5, int(YMAX) + 1, 5):
    d.line([P(XMIN, gy), P(XMAX, gy)], fill=(24, 38, 50), width=1)

# --- corridors (under the rooms, so room walls cut them cleanly) --------------------------
for key, name, prof, path, heights, look in F.CORRIDORS:
    if prof == 'catwalk':
        continue
    wpx = int(F.corridor_width(prof) * SC)
    for a, b in zip(path, path[1:]):
        d.line([P(*a), P(*b)], fill=EDGE, width=wpx + 4)
        for e in (a, b):
            ex, ey = P(*e)
            d.rectangle([ex - wpx / 2 - 2, ey - wpx / 2 - 2, ex + wpx / 2 + 2, ey + wpx / 2 + 2], fill=EDGE)
for key, name, prof, path, heights, look in F.CORRIDORS:
    if prof == 'catwalk':
        continue
    wpx = int(F.corridor_width(prof) * SC)
    for (a, ha), (b, hb) in zip(zip(path, heights), zip(path[1:], heights[1:])):
        col = hcol((ha + hb) / 2)
        d.line([P(*a), P(*b)], fill=col, width=wpx)
        for e in (a, b):
            ex, ey = P(*e)
            d.rectangle([ex - wpx / 2, ey - wpx / 2, ex + wpx / 2, ey + wpx / 2], fill=col)
for key, name, prof, path, heights, look in F.CORRIDORS:
    wm = F.corridor_width(prof)
    for (a, ha), (b, hb) in zip(zip(path, heights), zip(path[1:], heights[1:])):
        if abs(hb - ha) < 0.01:
            continue
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        n = int(round(abs(hb - ha) / F.RISER))
        for k in range(n + 1):
            cx, cy = a[0] + ux * L * k / n, a[1] + uy * L * k / n
            d.line([P(cx - uy * wm / 2, cy + ux * wm / 2), P(cx + uy * wm / 2, cy - ux * wm / 2)], fill=(20, 30, 38), width=1)
        up = 1 if hb > ha else -1
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        tx, ty = P(mx + ux * up * 1.2, my + uy * up * 1.2)
        fx, fy = P(mx - ux * up * 1.2, my - uy * up * 1.2)
        d.line([(fx, fy), (tx, ty)], fill=ACCENT, width=2)
        d.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill=ACCENT)

for key, name, prof, path, heights, look in F.CORRIDORS:
    if prof != 'D2':
        continue
    wm = F.corridor_width(prof) / 2
    for a, b in zip(path, path[1:]):
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        k = F.DUCT_RIB_PITCH
        while k < L:
            cx, cy = a[0] + ux * k, a[1] + uy * k
            d.line([P(cx - uy * wm, cy + ux * wm), P(cx + uy * wm, cy - ux * wm)], fill=(150, 162, 170), width=1)
            k += F.DUCT_RIB_PITCH

# --- rooms, then the levels inside them ---------------------------------------------------
for key, name, pts, floor, look in F.ROOMS:
    poly(pts, hcol(floor), EDGE, 3)
for name, pts, h, kind in F.LEVELS:
    if kind in ('platform', 'pit', 'lower'):
        poly(pts, hcol(h), ACCENT if kind == 'platform' else (127, 176, 216), 2)
    elif kind == 'feature':
        poly(pts, hcol(h), (170, 180, 188), 1)
        hatch(pts, (200, 210, 216, 150), 5)
for name, pts in F.HAZARDS:
    poly(pts, (38, 150, 128), (90, 210, 180), 1)
    hatch(pts, (150, 255, 220, 120), 6)
for name, pts, h in F.BRIDGES:
    poly(pts, hcol(h), ACCENT, 2)
    x0, y0 = P(pts[0][0], pts[0][1])
    x1, y1 = P(pts[2][0], pts[2][1])
    for x in range(int(x0) + 6, int(x1), 12):
        d.line([(x, y1 + 2), (x, y0 - 2)], fill=(20, 30, 38), width=1)
# Crawls run under the floor, so they are drawn over it, dashed.
for key, name, prof, path, heights, look in F.CORRIDORS:
    if prof == 'crawl':
        q = [P(*p) for p in path]
        for a, b in zip(q, q[1:]):
            d.line([a, b], fill=hcol(heights[0]), width=int(F.corridor_width(prof) * SC))
        dashed(q, (224, 160, 96), 2, 6, 4)

# --- stairs ------------------------------------------------------------------------------
for name, pts, h0, h1, (ux, uy) in F.STAIRS:
    poly(pts, hcol((h0 + h1) / 2), ACCENT, 1)
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
    n = int(round(abs(h1 - h0) / F.RISER))
    for k in range(1, n):
        if ux:
            x = x0 + (x1 - x0) * k / n
            d.line([P(x, y0), P(x, y1)], fill=(20, 30, 38), width=1)
        else:
            y = y0 + (y1 - y0) * k / n
            d.line([P(x0, y), P(x1, y)], fill=(20, 30, 38), width=1)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = 0.4 * ((x1 - x0) if ux else (y1 - y0))
    tx, ty = P(cx + ux * half, cy + uy * half)
    fx, fy = P(cx - ux * half, cy - uy * half)
    d.line([(fx, fy), (tx, ty)], fill=ACCENT, width=2)
    d.ellipse([tx - 3.5, ty - 3.5, tx + 3.5, ty + 3.5], fill=ACCENT)

# --- openings: a gap in the wall, painted with the floor colour found either side ----------
for a, b in F.OPENINGS:
    L = math.dist(a, b)
    nx_, ny_ = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    cols = [im.getpixel(tuple(int(v) for v in P(mx + nx_ * k, my + ny_ * k)))[:3] for k in (0.7, -0.7)]
    col = tuple((cols[0][i] + cols[1][i]) // 2 for i in range(3))
    d.line([P(*a), P(*b)], fill=col, width=6)

# --- blockers (the cage is an enterable fenced room) ---------------------------------------
for room, name, pts in F.BLOCKERS:
    if name in F.ENTERABLE:
        poly(pts, None, (208, 214, 218), 2)
    elif 'transformer' in name:
        poly(pts, (40, 46, 52), (208, 214, 218), 1)
        hatch(pts, (208, 214, 218, 90), 5)
    else:
        poly(pts, (40, 46, 52), (208, 214, 218), 1)

for name, pts, clear in F.CROUCH:
    hatch(pts, (224, 160, 96, 150), 5, 2)
    dashed([P(*p) for p in pts], (224, 160, 96), 2, 6, 4, closed=True)
for name, (x, y), r, kind in F.MOVING:
    cx, cy = P(x, y)
    rp = r * SC
    d.ellipse([cx - rp, cy - rp, cx + rp, cy + rp], fill=(58, 66, 74), outline=(255, 200, 120), width=2)
    if kind == 'fan':
        for k in range(4):
            a0 = k * math.pi / 2 + 0.4
            d.polygon([(cx, cy), (cx + rp * 0.9 * math.cos(a0), cy + rp * 0.9 * math.sin(a0)),
                       (cx + rp * 0.9 * math.cos(a0 + 0.6), cy + rp * 0.9 * math.sin(a0 + 0.6))], fill=(255, 200, 120))
        continue
    d.line([(cx, cy - rp + 4), (cx, cy + rp - 4)], fill=(255, 200, 120), width=2)
    for sgn in (-1, 1):
        tip = cy + sgn * (rp - 4)
        d.polygon([(cx, tip + sgn * 2), (cx - 5, tip - sgn * 5), (cx + 5, tip - sgn * 5)], fill=(255, 200, 120))

# --- upper floors and overhead things ------------------------------------------------------
for name, pts, h, kind in F.LEVELS:
    if kind == 'upper':
        hatch(pts, hcol(h) + (220,), 7, 2)
        dashed([P(*p) for p in pts], ACCENT, 2, 8, 5, closed=True)
for name, pts in F.OVERHEAD:
    dashed([P(*p) for p in pts], (143, 163, 177), 1, 6, 5, closed=len(pts) > 2)
# Catwalks: a railed grating drawn over whatever it crosses.
for key, name, prof, path, heights, look in F.CORRIDORS:
    if prof != 'catwalk':
        continue
    hw = F.corridor_width(prof) / 2
    for a, b in zip(path, path[1:]):
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        a0, b0 = (a[0] - ux * hw, a[1] - uy * hw), (b[0] + ux * hw, b[1] + uy * hw)
        quad = [(a0[0] - uy * hw, a0[1] + ux * hw), (b0[0] - uy * hw, b0[1] + ux * hw),
                (b0[0] + uy * hw, b0[1] - ux * hw), (a0[0] + uy * hw, a0[1] - ux * hw)]
        poly(quad, hcol(heights[0]), None)
        hatch(quad, (40, 32, 20, 150), 5, 1)
        d.line([P(*quad[0]), P(*quad[1])], fill=ACCENT, width=2)
        d.line([P(*quad[3]), P(*quad[2])], fill=ACCENT, width=2)
for name, path in F.OPTIONAL:
    dashed([P(*p) for p in path], ACCENT, 3, 12, 8)


for name, pts in F.DRAWBRIDGES:
    dashed([P(*q) for q in pts], (255, 255, 255), 2, 5, 3, closed=True)
    hx, hy = P(max(q[0] for q in pts), sum(q[1] for q in pts) / len(pts))
    d.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill=(255, 255, 255))

# --- triggers: dashed red boundary plus a light hatch, so the elevation colour still reads ---
for name, pts in F.TRIGGERS:
    hatch(pts, (224, 113, 95, 70), 14, 2)
    dashed([P(*p) for p in pts], (236, 110, 90), 3, 10, 6, closed=True)

# --- the card-first route, thin and dotted ------------------------------------------------
over, o = layer()
kq = [P(*F.xy(p)) for p in F.ROUTES['knowing player, catwalk to P']]
for a, b in zip(kq, kq[1:]):
    L = math.dist(a, b)
    for k in range(int(L // 7) + 1):
        t_ = min(1, k * 7 / L) if L else 0
        x, y = a[0] + (b[0] - a[0]) * t_, a[1] + (b[1] - a[1]) * t_
        o.ellipse([x - 1.8, y - 1.8, x + 1.8, y + 1.8], fill=(255, 190, 90, 190))
rq = [P(*F.xy(p)) for p in F.ROUTES['card first, vent return']]
for a, b in zip(rq, rq[1:]):
    L = math.dist(a, b)
    for k in range(int(L // 7) + 1):
        t = min(1, k * 7 / L) if L else 0
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        o.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(255, 255, 255, 170))
flatten(over)

# --- ladders, doors, objectives, secrets, damage, screenshot moments ------------------------
for name, a, b, h0, h1 in F.DROPS:
    (ax, ay), (bx, by) = P(*a), P(*b)
    d.line([(ax, ay), (bx, by)], fill=(255, 255, 255), width=3)
    ux_, uy_ = (bx - ax) / math.dist((ax, ay), (bx, by)), (by - ay) / math.dist((ax, ay), (bx, by))
    d.polygon([(bx + ux_ * 6, by + uy_ * 6), (bx - uy_ * 6, by + ux_ * 6), (bx + uy_ * 6, by - ux_ * 6)], fill=(255, 255, 255))
for name, (x, y), h0, h1 in F.LADDERS:
    cx, cy = P(x, y)
    d.rectangle([cx - 6, cy - 10, cx + 6, cy + 10], fill=BG, outline=(255, 255, 255), width=2)
    for k in (-5, 0, 5):
        d.line([(cx - 6, cy + k), (cx + 6, cy + k)], fill=(255, 255, 255), width=1)
DOORCOL = {'airlock': (215, 162, 74), 'lock': (224, 113, 95), 'release': (121, 199, 168), 'window': (143, 211, 255),
           'lift': (255, 208, 96), 'door': (190, 198, 204), 'grill': (224, 160, 96), 'fan': (255, 200, 120)}
DOORTAG = {'Lift gate': 'LIFT: K + P', 'Cage gate': 'cage gate', 'S1': 'S1', 'S2': 'S2: card M',
           'Quarantine hold door': 'card M', 'Overlook window': 'window', 'Truck bay roll door': 'roll door',
           'Substation grill': 'grill: slide, crouch', 'Vent grille': 'vent grille',
           'Big fan': 'fan: crouch through when stopped', 'Door 3': 'door 3: raised, corridor side only',
           'Door 1': 'door 1: switch 3', 'Door 5': 'door 5: switch 2'}
for name, (x, y), kind in F.DOORS:
    cx, cy = P(x, y)
    d.rectangle([cx - 7, cy - 7, cx + 7, cy + 7], fill=DOORCOL[kind], outline=BG)
for name, (x, y) in F.LEVERS:
    cx, cy = P(x, y)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=BG, outline=(255, 200, 120), width=2)
    d.line([(cx, cy + 3), (cx + 5, cy - 7)], fill=(255, 200, 120), width=3)
for name, (x, y) in F.SECRETS:
    cx, cy = P(x, y)
    pts = [(cx + 10 * math.cos(math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.45),
            cy - 10 * math.sin(math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else 0.45)) for k in range(10)]
    d.polygon(pts, fill=(180, 140, 240), outline=BG)
for name, (x, y) in F.REWARDS:
    cx, cy = P(x, y)
    d.rectangle([cx - 7, cy - 6, cx + 7, cy + 6], fill=(214, 170, 90), outline=BG, width=2)
    d.line([(cx - 7, cy - 1), (cx + 7, cy - 1)], fill=BG, width=2)
for name, (x, y) in F.CLUES:
    cx, cy = P(x, y)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=BG, outline=(220, 226, 230), width=2)
    text(cx, cy + 1, '?', 12, (220, 226, 230), 'mm', True)
for name, (x, y) in F.DAMAGE:
    cx, cy = P(x, y)
    d.line([(cx - 8, cy - 8), (cx + 8, cy + 8)], fill=(255, 144, 64), width=4)
    d.line([(cx - 8, cy + 8), (cx + 8, cy - 8)], fill=(255, 144, 64), width=4)
for name, (x, y) in F.SHOTS:
    cx, cy = P(x, y)
    d.rounded_rectangle([cx - 9, cy - 6, cx + 9, cy + 7], 2, fill=BG, outline=(255, 255, 255), width=2)
    d.ellipse([cx - 3.5, cy - 3, cx + 3.5, cy + 4], outline=(255, 255, 255), width=1)
for name, (x, y) in F.OBJECTIVES:
    cx, cy = P(x, y)
    tag = name.split(':')[0]
    r = 12 if len(tag) == 1 else 8
    fill = (255, 208, 96) if tag in ('K', 'P') else (121, 199, 168)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=BG, width=2)
    if len(tag) == 1:
        text(cx, cy + 1, tag, 15, BG, 'mm', True)

# --- labels ------------------------------------------------------------------------------
N, S = 14, 11
SKIP_LABEL = {'LR', 'CV'}   # the cable vault is a secret under the Substation: its secret marker labels it
ROOM_LABEL = {'AL': (4.0, -25.0, 'l'), 'RC': (3.8, -12.2, 'm'), 'SB': (-4.0, 7.5, 'm'), 'DK': (-4.5, 41.7, 'm'),
              'TB': (-19.0, 50.8, 'm'), 'LG': (-19.0, 30.3, 'm'), 'PR': (36.0, 29.3, 'm'), 'SS': (39.6, 39.4, 'm'),
              'WX': (-17.5, 5.0, 'm'), 'ST': (-29.6, 13.3, 'r'), 'CU': (36.0, -2.5, 'm'), 'LL': (56.6, 20.0, 'l'),
              'QH': (59.6, 12.4, 'm'), 'FL': (22.0, 14.6, 'm'), 'PP': (18.6, 47.9, 'm'), 'SC': (-26.3, 8.0, 'r'),
              'MR': (-6.5, 63.6, 'm'), 'R3': (10.5, 65.8, 'm'), 'FC': (17.5, 57.3, 'm')}
for key, name, pts, floor, look in F.ROOMS:
    if key in SKIP_LABEL:
        continue
    x, y, a = ROOM_LABEL[key]
    label(x, y, [(name, N, TEXT, True), (f'{hl(floor)} m  ·  {look}', S, NOTE, False)], a)
COR_LABEL = {'C1': (3.8, -5.5, 'l'), 'W1': (-17.25, 18.6, 'm'), 'TR': (21.0, -5.6, 'm'), 'PG': (41.6, 33.25, 'm'),
             'EL': (55.0, 31.0, 'l'), 'AC': (26.6, 31.0, 'm'), 'CW': (-10.4, 54.7, 'r'), 'J2': (0.4, 63.3, 'm'), 'C2': (18.5, 59.3, 'm')}
SKIP_COR = {'VT', 'BG'}   # the girder crawl is a secret under the bridge: its secret marker labels it
for key, name, prof, path, heights, look in F.CORRIDORS:
    if key in SKIP_COR:
        continue
    x, y, a = COR_LABEL[key]
    span = f'{hl(heights[0])} → {hl(heights[-1])}'
    label(x, y, [(name, 12, ACCENT, True), (f'{prof}  ·  {span}', S, NOTE, False)], a)
LEVEL_LEADER = {'Archive (above the cage)': ((-28.6, 41.2, 'r'), (-27.4, 39.6))}
LEVEL_LABEL = {'Gallery': (4.6, 1.6), 'Sorting booth': (-11.2, 19.0), 'Pump pit': (40.4, 20.0), 'Gantry': (48.25, 43.3),
               'Cable trench': (38.5, 41.75), 'Archive (above the cage)': (-25.25, 32.9), 'S1 landing': (-10.5, 39.0),
               'Stairwell landing': (-27.5, 21.5), 'Stairwell top': (-24.0, 27.6), 'U-turn entry': (27.25, -3.1),
               'North lane': (39.0, 10.9), 'Stair room top landing': (12.6, 63.4)}
for name, pts, h, kind in F.LEVELS:
    if name not in LEVEL_LABEL:
        continue
    x, y = LEVEL_LABEL[name]
    short = {'Archive (above the cage)': 'Archive', 'Sorting booth': 'Booth', 'S1 landing': '', 'Stairwell landing': '',
             'Stairwell top': '', 'U-turn entry': '', 'Stair room top landing': ''}.get(name, name)
    s_ = (short + ' ' if short else '') + hl(h)
    col = ACCENT if kind != 'pit' else (159, 208, 240)
    if name in LEVEL_LEADER:
        (lx, ly, la), pt = LEVEL_LEADER[name]
        label(lx, ly, [(s_, 10, col, True), ('over the cage', 10, col, False)], la, pt)
    else:
        label(x, y, [(s_, 10, col, True)])
for name, (x, y), kind in F.DOORS:
    tag = next((v for k, v in DOORTAG.items() if name.startswith(k)), None)
    if not tag:
        continue
    off = {'S1': (1.2, 1.3, 'l'), 'S2: card M': (1.0, -1.1, 'l'), 'LIFT: K + P': (1.2, 0.9, 'l'), 'cage gate': (-4.6, 0.4, 'r'),
           'card M': (1.2, -1.2, 'l'), 'window': (-0.9, 0.0, 'r'), 'roll door': (0.9, 1.2, 'l'),
           'grill: slide, crouch': (1.0, 1.3, 'l'), 'vent grille': (-0.6, 1.4, 'r'),
           'fan: crouch through when stopped': (0.5, 3.2, 'm'), 'door 3: raised, corridor side only': (1.3, 0.9, 'l'),
           'door 1: switch 3': (-0.7, 1.2, 'r'), 'door 5: switch 2': (-0.6, 3.4, 'r')}[tag]
    far = abs(off[0]) > 3 or abs(off[1]) > 3
    label(x + off[0], y + off[1], [(tag, 10, TEXT, True)], off[2], (x, y) if far else None)
LADDER_OFF = {0: (1.2, -0.9, 'l'), 1: (-1.0, -1.0, 'r'), 2: (0.2, -1.5, 'm'), 3: (-0.1, -1.7, 'm'), 4: (-1.0, -0.2, 'r'),
              5: (-1.0, -0.8, 'r'), 6: (-0.4, -1.6, 'm')}
for i, (name, (x, y), h0, h1) in enumerate(F.LADDERS):
    ox_, oy_, a = LADDER_OFF[i]
    rungs = int(round(abs(h1 - h0) / F.RUNG))
    arrow = '↑' if h1 > h0 else '↓'
    label(x + ox_, y + oy_, [(f'{rungs} rungs {arrow}', 10, TEXT, False)], a)
CROUCH_LABEL = {'pipe bank': (-13.2, 3.4, 'r', 'pipes: crouch under (1.2 m clear)', (-17.5, 8.3))}
for name, pts, clear in F.CROUCH:
    if name in CROUCH_LABEL:
        lx, ly, la, ls, lead = CROUCH_LABEL[name]
        label(lx, ly, [(ls, 10, (224, 160, 96), True)], la, lead)
MOVING_LABEL = {'piston': (0.0, -2.3, 'm', 'piston, up and down'), 'fan': (3.8, -1.7, 'l', 'box fan, slow blades')}
for name, (x, y), r, kind in F.MOVING:
    if kind == 'fan':
        continue
    ox_, oy_, a, t = MOVING_LABEL[kind]
    label(x + ox_, y + oy_, [(t, 10, (255, 200, 120), True)], a)
for name, a, b, h0, h1 in F.DROPS:
    label(b[0] - 0.6, b[1] - 1.3, [(f'drop {h0 - h1:.2f} m'.replace('.00', ''), 10, TEXT, True)], 'r')
LEVER_LABEL = {'switch panel': (-13.2, 2.3, 'r', 'switches: 1 sparks, 2 door 5, 3 door 1', True),
               'cage switch': (-28.6, 35.8, 'r', 'cage switch: lowers (3)', True),
               'fan lever': (22.0, 52.8, 'l', 'lever: stops the fan', False)}
for name, (x, y) in F.LEVERS:
    lx, ly, la, ls, lead = LEVER_LABEL[name.split(':')[0]]
    label(lx, ly, [(ls, 10, (255, 200, 120), True)], la, (x, y) if lead else None)
for name, pts in F.DRAWBRIDGES:
    label(-15.8, 39.3, [('raised section (3)', 10, TEXT, True)])
for name, (x, y) in F.OBJECTIVES:
    if len(name.split(':')[0]) > 1:
        label(-28.6, 32.2, [('cage release', 10, (121, 199, 168), True), ('in the archive', 10, (121, 199, 168), False)],
              'r', (x, y))

# North arrow and scale bar.
nx, ny = P(-34.2, 64.0)
d.line([(nx, ny + 30), (nx, ny - 6)], fill=TEXT, width=3)
d.polygon([(nx, ny - 16), (nx - 7, ny - 2), (nx + 7, ny - 2)], fill=TEXT)
text(nx, ny + 34, 'N', 13, TEXT, 'ma', True)
sx, sy = P(-35.0, -29.0)
d.line([(sx, sy), (sx + 10 * SC, sy)], fill=TEXT, width=3)
for k in (0, 5, 10):
    d.line([(sx + k * SC, sy - 4), (sx + k * SC, sy + 4)], fill=TEXT, width=2)
text(sx, sy + 7, '10 m', 11, NOTE)

# --- right-hand panel ----------------------------------------------------------------------
y = OY


def head(s):
    global y
    text(RX, y, s, 17, ACCENT, bold=True)
    y += 27


def line(s, c=TEXT, n=13):
    global y
    text(RX, y, s, n, c)
    y += n + 6


head('KEY')
for col, s in [((255, 208, 96), 'K card and P power: the two lift requirements'), (ACCENT, 'platform or stair: the dot is the top'),
               ((127, 176, 216), 'pit or trench'), ((40, 46, 52), 'blocker (equipment, cover)'),
               ((224, 113, 95), 'locked door'), ((121, 199, 168), 'far-side release, cage release'),
               ((143, 211, 255), 'overlook window'), ((180, 140, 240), 'secret'), ((214, 170, 90), 'reward in view (ammo, armour)'),
               ((220, 226, 230), '? optional clue: they have been here a long time'), ((255, 144, 64), 'visible damage'),
               ((224, 160, 96), 'crouch under (pipes) / crouch crawl'), ((255, 200, 120), 'moving machine'),
               ((38, 150, 128), 'coolant channel (not walkable)')]:
    d.rectangle([RX, y + 2, RX + 14, y + 16], fill=col)
    text(RX + 24, y + 1, s, 13)
    y += 21
line('M: maintenance card, opens S2 and the quarantine hold')
line('white dots: card first, vent return    white box: screenshot moment')
line('white arrow: one-way drop    amber dots: knowing player, catwalk to P')
line('lever icon: the switches, the cage switch and the fan lever')
line('white dashed box on the catwalk: section (3), raised 90° until lowered')
line('red dashes: encounter trigger, spans every way in')
line('amber hatch: archive above the cage / amber dashes: crane catwalk')
line('grey dashes: crane rail and hanging container (overhead)')
line('orange dashes: crouch crawl under the floor')
y += 10
head('ELEVATION')
for h in (4.0, 1.0, 0.0, -1.5, -3.0, -5.5):
    d.rectangle([RX, y + 2, RX + 44, y + 16], fill=hcol(h))
    text(RX + 54, y + 1, f'{hl(h)} m', 13)
    y += 21
y += 10
head('THE ELEVATION STORY')
for s in ['airlock 0 → landing, 2 steps → Receiving −0.5',
          'C1 → gallery −0.5 → side stair → bay −3',
          'pipe run −3: crouch under the pipes for the ammo',
          'stairwell: 8 up, landing −1, 8 up → Logistics +1',
          'ladder, 12 rungs → archive +4; S1 stair → bay −3',
          'trench → U-turn: 2 down, round the compressor, 2 down → −4',
          'pit ladder −5.5 → crawl → ladder, 12 rungs → Substation −2.5',
          'gantry stair +1 (M, P). Two ways back:',
          '  vent: grill, crouch → air duct hallway, 2 down → filter room −3',
          '        → ladder, 12 rungs → pipe room 0 → vent → drop → dock −1.75',
          '  S2: east stairs, 20 down → lobby −4 (hold −4.5) → pump room → U-turn up',
          'catwalk: pipe bay switch 2 + cage switch; archive +4 → section (3)',
          '        → door 5 → over the bay → machine room +4 → jog',
          '        → stair room top: stair corridor, 12 down → door 3 +1 → north catwalk',
          '        or down 16 (pickups behind you) → fan chamber → crouch through the fan',
          'lift → the processing deck']:
    line(s)
y += 10
head('ROUTE CHECK')
for k, pts in F.ROUTES.items():
    L = F.route_length(pts)
    line(f'{k}: {L:.0f} m, about {L / 5:.0f} s walking with nothing in it')
vent = F.route_length([(48, 45.5)] + F.VENT_BACK)
s2 = F.route_length([(48, 45.5)] + F.TO_LOBBY + F.S2_BACK + [(10, 8), (10.75, 17.1), (10.75, 28.8), (6, 29), (0, 37.5), (0, 46)])
line(f'P to the lift: {vent:.0f} m by the vent, {s2:.0f} m by S2', NOTE)
line('The completionist takes the hold, climbs back up the east', NOTE)
line('stairs and leaves by the vent: the doubling back is designed in.', NOTE)
line('Measure the empty walk before deciding on more growth.', NOTE)
y += 10
head('SELF-CHECK')
line(f'{len(problems)} problems: stair runs, ladder rungs, doors, ladders,')
line('secrets on the plan, and routes clear of every blocker')
y += 10
head('ROOM STUDIES FIRST')
for s in ('Sorting Bay (the hub)', 'Logistics office + archive', 'Pump Room', 'Substation', 'Loading dock + lift lobby'):
    line('• ' + s)

out = ROOT / 'docs/freight-v2-plan.png'
im.convert('RGB').save(out)
print('FREIGHT_V2_PLAN:', out.relative_to(ROOT), im.size)
