"""Rich finish: the shared drawing code (RICH_FINISH_SPEC.md sections 1 to 3).

Promoted from the reference implementation in ../rich-finish/ (art_v2.py, art_v4.py). Kits and
gate1/environment.py call it; nothing copies the mock scripts. Everything here draws onto an
env.Room (needs r.img, r.x, r.y, r.rect, r.mask, r.outline, r.cast, r.edge) with hard pixels and
flat steps, light from the upper left.

Leaf fans take a district foliage ramp (4 steps, shadow -> light) and add the district's edge
and tip tones (palettes/district_palettes.py FOLIAGE_EXTRA), so every district keeps its own
greens and gains the five-tone fan.
"""
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "palettes"))
import district_palettes as dp  # noqa: E402


def hx(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.uint8)


# Blue planters, mulch and accents (RICH_EXTRAS in district_palettes.py)
POT = [hx(h) for h in dp.RICH_EXTRAS["planter"]]
POT_LIP = hx(dp.RICH_EXTRAS["planter_lip"][0])
POT_BOLT = hx(dp.RICH_EXTRAS["planter_bolt"][0])
MULCH = [hx(h) for h in dp.RICH_EXTRAS["mulch"]]  # soil, mulch, orange fleck


def fan_palette(ramp):
    """[edge, t1, t2, t3, t4, tip] for a 4-step foliage ramp of RGB triples."""
    key = tuple(int(v) for v in ramp[0])
    for d, pal in dp.DISTRICTS.items():
        if tuple(int(v) for v in hx(pal["foliage"][0])) == key:
            ex = dp.FOLIAGE_EXTRA[d]
            return [hx(ex["edge"])] + [hx(h) for h in pal["foliage"]] + [hx(ex["tip"])]
    # an unknown ramp (a clipped or tinted variant): derive a tip and an edge
    lift = lambda c, k: np.clip(c.astype(int) + k, 0, 255).astype(np.uint8)  # noqa: E731
    return [lift(ramp[0], -22)] + [np.asarray(c, np.uint8) for c in ramp] + [lift(ramp[3], 40)]


def _shift4(m):
    out = np.zeros_like(m)
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    out[1:, :] |= m[:-1, :]
    out[:-1, :] |= m[1:, :]
    return out


def fan(r, cx, cy, rad, seed, P, count=5, spread=None, clip=None, tone_shift=0):
    """A fan of count + 2 pointed leaves: dark edge, five tones lit from the upper left, a vein, painter's order."""
    if rad > 7:  # large canopies are several smaller fans
        rnd0 = random.Random(seed * 7 + 1)
        whole = np.zeros(r.img.shape[:2], bool)
        for k in range(5):
            a0 = 2 * math.pi * k / 5 + rnd0.uniform(-0.4, 0.4)
            dist = rad * (0.0 if k == 0 else 0.62)
            whole |= fan(r, cx + math.cos(a0) * dist, cy + math.sin(a0) * dist * 0.8, rad * 0.58,
                         seed * 11 + k, P, count=5, clip=clip)
        return whole
    rnd = random.Random(seed)
    spread = spread or rad * 0.9
    n = count + 2
    leaves = []
    for i in range(n):
        ang = 2 * math.pi * i / n + rnd.uniform(-0.18, 0.18)
        d = spread * rnd.uniform(0.0, 0.28)
        leaves.append((cy + math.sin(ang) * d * 0.8, cx + math.cos(ang) * d, ang, rad * rnd.uniform(0.95, 1.25)))
    leaves.sort()
    X, Y = r.x, r.y
    whole = np.zeros(r.img.shape[:2], bool)
    for py, px, ang, L in leaves:
        ca, sa = math.cos(ang), math.sin(ang)
        u = (X - px) * ca + (Y - py) * sa
        v = -(X - px) * sa + (Y - py) * ca
        t = np.clip(u / L, 0, 1)
        W = L * 0.36
        m = (u >= 0) & (u <= L) & (np.abs(v) <= W * np.sin(np.pi * t) ** 0.75 + 0.35)
        if clip is not None:
            m &= clip
        if not m.any():
            continue
        lit = ((X - px) * -0.7 + (Y - py) * -0.7) / max(L, 1)
        ring = r.edge(m)
        tone = np.full(m.shape, 3)
        tone[lit > 0.05] = 4
        tone[(lit > 0.45) | (t > 0.82)] = 5
        tone[lit < -0.25] = 2
        tone[lit < -0.6] = 1
        vein = m & (np.abs(v) < 0.5) & (t > 0.18) & (t < 0.72)
        tone = np.maximum(1, tone - tone_shift)
        for k in range(1, 6):
            r.img[m & (tone == k)] = P[k]
        r.img[vein] = P[2]
        outside = _shift4(m) & ~m
        if clip is not None:
            outside &= clip
        r.img[outside & ~whole] = P[0]       # dark edge against what lies behind
        r.img[ring & (lit < 0.3)] = P[1]     # shaded edge, no hard ring on the lit side
        whole |= m
    return whole


def sparkles(r, mask, seed, P):
    """Sun catching leaf tips: a third of the upper-left edge pixels (x + y divisible by 3, so the pattern moves
    with the plant by whole 3 px steps, as the desk-front occluders require) become the tip tone."""
    edge = mask & ~np.roll(np.roll(mask, 1, 0), 1, 1)
    r.img[edge & ((r.x.astype(int) + r.y.astype(int)) % 3 == 0)] = P[5]


def leaves(r, cx, cy, rad, seed, ramp, count=5, spread=None, clip=None):
    """Two layers (a shaded back layer, then the lit front layer) with sparkle tips. Returns the leaf mask."""
    P = fan_palette(ramp)
    if rad > 7:  # large canopy: seven smaller fans, each with a back and a front layer
        rnd = random.Random(seed * 13 + 5)
        whole = np.zeros(r.img.shape[:2], bool)
        for k in range(7):
            a0 = 2 * math.pi * k / 7 + rnd.uniform(-0.4, 0.4)
            dist = rad * (0.0 if k == 0 else 0.68)
            fx, fy = cx + math.cos(a0) * dist, cy + math.sin(a0) * dist * 0.8
            whole |= fan(r, fx, fy, rad * 0.5, seed * 11 + k, P, count=5, clip=clip, tone_shift=1)
            whole |= fan(r, fx - 0.8, fy - 0.8, rad * 0.46, seed * 17 + k, P, count=5, clip=clip)
        sparkles(r, whole, seed, P)
        return whole
    back = fan(r, cx + 0.6, cy + 0.6, rad * 0.9, seed + 91, P, count=count, spread=spread, clip=clip, tone_shift=1)
    front = fan(r, cx, cy, rad, seed, P, count=count + 1, spread=spread, clip=clip)
    sparkles(r, front, seed, P)
    return back | front


def planter(r, x, y, seed, ramp):
    """Blue planter: lit lip, shaded right side and base, a metal band with two bolts, orange mulch, a leaf fan."""
    r.cast(x, x + 12, y + 12)
    pot = r.mask(x, y + 4, x + 12, y + 12)
    r.img[pot] = POT[1]
    r.rect(x, y + 4, x + 12, y + 6, POT[2])
    r.rect(x + 1, y + 4, x + 11, y + 5, POT_LIP)
    r.rect(x, y + 4, x + 1, y + 12, POT[2])
    r.rect(x + 11, y + 6, x + 12, y + 12, POT[0])
    r.rect(x, y + 11, x + 12, y + 12, POT[0])
    r.rect(x + 1, y + 8, x + 11, y + 9, POT[0])
    for bx in (x + 2, x + 9):
        r.img[y + 7, bx] = POT_BOLT
    r.outline(pot)
    r.rect(x + 2, y + 5, x + 10, y + 6, MULCH[1])
    r.img[y + 5, x + 4] = MULCH[2]
    r.img[y + 5, x + 7] = MULCH[2]
    leaves(r, x + 6, y + 1, 6.5, seed, ramp, count=6, spread=6)


def extend(m):
    """Complete an exact-hex recolour map (UPPER hex -> UPPER hex) for the rich-finish sprites: the Orientation
    leaf-fan edge and tip tones follow the destination foliage ramp, and the planter, mulch, rock, moss and flower
    colours pass through unchanged. Returns a new dict; existing entries win."""
    out = dict(m)
    O = dp.DISTRICTS["orientation"]["foliage"]
    if all(h.upper() in m for h in O):
        P = fan_palette([hx(m[h.upper()]) for h in O])
        ex = dp.FOLIAGE_EXTRA["orientation"]
        out.setdefault(ex["edge"].upper(), "#%02X%02X%02X" % tuple(P[0]))
        out.setdefault(ex["tip"].upper(), "#%02X%02X%02X" % tuple(P[5]))
    for steps in dp.RICH_EXTRAS.values():
        for h in steps:
            out.setdefault(h.upper(), h.upper())
    return out


# ------------------------------------------------------------------ garden parts (RICH_FINISH_SPEC.md section 3)

ROCKS = [hx(h) for h in dp.RICH_EXTRAS["rocks"]]
MOSS = hx(dp.RICH_EXTRAS["moss"][0])
PETAL_SHADE, PETAL = [hx(h) for h in dp.RICH_EXTRAS["petals"]]
ORANGE, PINK, YELLOW = [hx(h) for h in dp.RICH_EXTRAS["flower_accents"]]
FOLIAGE_EDGE = hx(dp.FOLIAGE_EXTRA["orientation"]["edge"])  # canopy shadow on the bed: dark green, never navy


def rock(r, cx, cy, rr, bed, bst):
    """Grey rock, shaded from the upper left, a moss cap and a one-pixel crack."""
    m = r.blob(cx, cy, rr, 1.0, lobes=4, amp=0.12) & bed
    bst.shade_mask(r.img, m, ROCKS, k_shadow=1, k_light=1)
    r.img[m & ~bst.shifted(m, -1, -1)] = ROCKS[3]
    r.outline(m, ROCKS[0])
    gx, gy = cx - 6, cy - 6  # the moss pattern counts columns from the rock's own box
    ys, xs = np.nonzero(m[gy:gy + 12, gx:gx + 12] & np.all(r.img[gy:gy + 12, gx:gx + 12] != ROCKS[0], axis=2))
    if len(ys):
        top = ys.min()
        green = hx(dp.DISTRICTS["orientation"]["foliage"][2])
        for y, x in zip(ys, xs):
            if y == top or (y == top + 1 and (x + y) % 2 == 0):
                r.img[gy + y, gx + x] = MOSS if x % 2 == 0 else green
        mid = int(np.median(xs))
        for k in range(3):
            r.img[gy + top + 3 + k, gx + mid - 1 + k // 2] = ROCKS[0]


def pond_detail(r, water, glass):
    """Ripple arcs on the lit side, a sheen band and one lily flower on the water mask."""
    yy, xx = np.mgrid[0:r.img.shape[0], 0:r.img.shape[1]]
    w = water.copy()
    w[:, :118] = False
    w[:, 172:] = False
    w[:80] = False
    w[130:] = False
    for cx, cy, rr in ((150, 100, 4), (154, 112, 5), (146, 118, 3)):
        ring = np.abs(np.hypot(xx - cx, (yy - cy) * 1.6) - rr) < 0.6
        r.img[ring & w & (xx < cx + 2)] = glass[3]
    r.img[w & (np.abs(xx - yy * 0.6 - 62) < 1.2)] = glass[2]
    for x, y in ((143, 110), (144, 110), (144, 109)):
        r.img[y, x] = PINK
    r.img[111, 144] = ORANGE


def trunk(r, wood, bst):
    """Root flare, roots creeping along the bed, bark streaks, a lit left edge and two limbs."""
    cx = 133
    rows = {96: 4, 98: 4, 100: 5, 102: 5, 104: 6, 106: 6, 108: 7, 110: 8, 112: 10, 114: 12}
    m = np.zeros(r.img.shape[:2], bool)
    for y, w in rows.items():
        m[y:y + 2, cx - w // 2: cx + (w + 1) // 2] = True
    for dx in (-1, 1):
        for t in range(5):
            m[113 + t // 2, cx + dx * (6 + t)] = True
            m[114 + t // 2, cx + dx * (6 + t)] = True
    bst.shade_mask(r.img, m, wood, k_shadow=2, k_light=1)
    r.outline(m, wood[0])
    a = r.img
    bark = np.zeros(a.shape[:2], bool)
    for col in wood:
        bark |= np.all(a == col, axis=2)
    bark[:, :120] = False
    bark[:, 150:] = False
    rnd = np.random.RandomState(5)
    streak = bark & (rnd.rand(*bark.shape) < 0.16) & np.roll(bark, 1, 0)
    a[streak] = wood[0]
    lit = bark & ~np.roll(bark, 1, 1)
    a[lit & np.all(a == wood[2], axis=2)] = wood[3]
    for sx in (-1, 1):  # limbs that show through the canopy
        for t in range(7):
            x, y = 133 + sx * (3 + t), 100 - t
            a[y:y + 2, x] = wood[2] if sx < 0 else wood[1]
            a[y + 2, x] = wood[0]


def grass_tufts(r, bed, dark, light, seed=4, n=14):
    """Three-blade grass tufts on the dark bed."""
    rnd = random.Random(seed)
    ys, xs = np.nonzero(bed)
    for _ in range(n):
        i = rnd.randrange(len(ys))
        x, y = int(xs[i]), int(ys[i])
        if tuple(r.img[y, x]) in [tuple(c) for c in dark]:
            for dx, h in ((-1, 2), (0, 3), (1, 2)):
                for k in range(h):
                    if 0 <= y - k < r.img.shape[0]:
                        r.img[y - k, x + dx] = light[0] if k < h - 1 else light[1]


def flower(r, x, y, pair=False):
    """White flower with an orange centre; every second one carries a pair of yellow dots."""
    r.img[y - 1, x] = PETAL
    r.img[y + 1, x] = PETAL_SHADE
    r.img[y, x - 1] = PETAL
    r.img[y, x + 1] = PETAL_SHADE
    r.img[y, x] = ORANGE
    if pair:
        r.img[y - 1, x - 1] = YELLOW
        r.img[y - 1, x + 1] = YELLOW


# ------------------------------------------------------------------ light passes (RICH_FINISH_SPEC.md section 4)
# Applied to a finished 320x192 frame, after the room is drawn and recoloured and before the floating markers.
# Every pass adds or multiplies by a constant on a mask, so each result is a flat colour step.

WALL_Y = 34  # first floor row below the north wall


def _tint(a, mask, mul=(1, 1, 1), add=(0, 0, 0)):
    f = a[mask].astype(np.float32) * np.array(mul, np.float32) + np.array(add, np.float32)
    a[mask] = np.clip(f, 0, 255).astype(np.uint8)


def _shift(m, dx, dy):
    out = np.zeros_like(m)
    h, w = m.shape
    ys, xs = slice(max(0, dy), min(h, h + dy)), slice(max(0, dx), min(w, w + dx))
    yo, xo = slice(max(0, -dy), min(h, h - dy)), slice(max(0, -dx), min(w, w - dx))
    out[ys, xs] = m[yo, xo]
    return out


def floor_mask(a, floor):
    """Pixels of the plain floor, joints and inlay band; `floor` = [fill, joint, inlay] RGB triples."""
    m = np.zeros(a.shape[:2], bool)
    for c in floor:
        m |= np.all(a == np.asarray(c, np.uint8), axis=2)
    m[:WALL_Y] = False
    return m


def slab_variation(a, floor, seed=3):
    """28% of the 32 px running-bond slabs drop a step, 22% rise one; 1.8% of floor pixels get a wear speck."""
    rnd = np.random.RandomState(seed)
    f = np.all(a == np.asarray(floor[0], np.uint8), axis=2)
    f[:WALL_Y] = False
    for row in range(0, 192, 32):
        off = 16 if (row // 32) % 2 else 0
        for col in range(off - 32, 320, 32):
            m = np.zeros_like(f)
            m[max(0, row + 1):row + 32, max(0, col + 1):col + 32] = True
            m &= f
            roll = rnd.rand()
            if roll < 0.28:
                _tint(a, m, add=(-7, -9, -12))
            elif roll < 0.5:
                _tint(a, m, add=(5, 5, 4))
    g = floor_mask(a, floor)
    _tint(a, g & (rnd.rand(*g.shape) < 0.018), add=(-14, -16, -20))


def cast_shadows(a, objects, floor, dx=4, dy=3, mul=(0.80, 0.78, 0.86)):
    """A flat shadow patch on the floor, offset away from the upper-left light, from every object pixel."""
    fl = floor_mask(a, floor)
    obj = objects & ~fl
    obj[:WALL_Y] = False
    sh = _shift(obj, dx, dy) & _shift(obj, dx // 2, dy // 2) & fl
    _tint(a, sh, mul=mul)


def lamp_glow(a, lamps, floor, glow_pixel, r_out=26, r_in=12, add_out=(9, 6, -3), add_in=(16, 11, -6)):
    """Two hard-edged warm steps on the floor around each lamp (ellipse, vertical stretch 1.25)."""
    fl = floor_mask(a, floor) | np.all(a == np.asarray(glow_pixel, np.uint8), axis=2)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    for cx, cy in lamps:
        d = np.hypot(xx - cx, (yy - cy) * 1.25)
        _tint(a, fl & (d < r_out) & (d >= r_in), add=add_out)
        _tint(a, fl & (d < r_in), add=add_in)


def light_shafts(a, windows, floor, slope=0.5, y_end=150, add=(11, 9, 2), add_core=(9, 7, 1)):
    """Diagonal bands from the north windows, two flat steps; windows = [(x, width)]."""
    fl = floor_mask(a, floor)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    for x0, w in windows:
        sx = (yy - WALL_Y) * slope
        band = (xx >= x0 + sx) & (xx < x0 + w + sx) & (yy < y_end)
        core = (xx >= x0 + sx + w * 0.25) & (xx < x0 + w * 0.75 + sx) & (yy < y_end)
        _tint(a, fl & band, add=add)
        _tint(a, fl & core, add=add_core)


def light_room(a, floor, lamps, windows, glow_pixel, canopy=None, no_shadow_from_x=292, rug=None):
    """The whole light stage in spec order. `canopy` = (box, green colours) for the tree's larger shadow;
    `rug` = a (y0, y1, x0, x1) box whose pixels cast no shadow. Modifies and returns a."""
    slab_variation(a, floor)
    fl = floor_mask(a, floor)
    objects = ~fl
    objects[:, no_shadow_from_x:] = False
    if rug is not None:
        y0, y1, x0, x1 = rug
        objects[y0:y1, x0:x1] = False
    cast_shadows(a, objects, floor)
    if canopy is not None:
        (y0, y1, x0, x1), greens = canopy
        g = np.zeros(a.shape[:2], bool)
        for c in greens:
            g |= np.all(a == np.asarray(c, np.uint8), axis=2)
        box = np.zeros_like(g)
        box[y0:y1, x0:x1] = True
        cast_shadows(a, g & box, floor, dx=10, dy=8, mul=(0.84, 0.84, 0.90))
    lamp_glow(a, lamps, floor, glow_pixel)
    light_shafts(a, windows, floor)
    return a


def light_orientation(a, bst):
    """The reference light for the Orientation review room (Mock 2.1): five lamps, three north windows,
    the tree's canopy shadow, and no shadow from the east wall mass or the rug at the doorway."""
    floor = [bst.STONE[3], bst.STONE[2], bst.STONE[1]]
    fol = [hx(h) for h in dp.FOLIAGE_TONES]
    return light_room(a, floor, [(x, y - 1) for x, y in ((92, 72), (180, 72), (180, 130), (284, 52), (284, 126))],
                      [(38, 26), (212, 26), (244, 26)], bst.BRASS[3], canopy=((56, 136, 90, 182), fol[1:]),
                      rug=(76, 106, 260, 292))
