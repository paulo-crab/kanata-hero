"""Detail mocks: richer foliage, tree, pond, rocks and planters ('organic'), plus material detail
(wood grain, brick joints, bevelled slabs, monitor content, lamp housings). No new objects are added;
every change is more drawing on things the room already contains. DRAFTS for board validation."""
import math
import random

import numpy as np

import build_scale_test as bst
import art_v2
from art_v2 import FOL, H, leaves_v2

SPARK = FOL[5]
WATER = [H(x) for x in ("#0F3550", "#1D7396", "#3CBAD6", "#A8F0EE")]
PINK = H("#F7B6C8")
MOSS = H("#4E8F2E")
SCREEN_TXT = H("#D8FAF8")
HOT = H("#FFF8D0")


# ----------------------------------------------------------------------------- organic

def leaves_v4(r, cx, cy, rad, seed, ramp=None, count=5, spread=None, clip=None):
    """Two layers of leaves (a shaded back layer, then the lit front layer), sparkle tips on the lit edge."""
    if rad > 7:
        rnd = random.Random(seed * 13 + 5)
        whole = np.zeros(r.img.shape[:2], bool)
        for k in range(7):
            a0 = 2 * math.pi * k / 7 + rnd.uniform(-0.4, 0.4)
            dist = rad * (0.0 if k == 0 else 0.68)
            fx, fy = cx + math.cos(a0) * dist, cy + math.sin(a0) * dist * 0.8
            whole |= leaves_v2(r, fx, fy, rad * 0.5, seed * 11 + k, count=5, clip=clip, tone_shift=1)
            whole |= leaves_v2(r, fx - 0.8, fy - 0.8, rad * 0.46, seed * 17 + k, count=5, clip=clip)
        add_sparkles(r, whole, seed)
        return whole
    back = leaves_v2(r, cx + 0.6, cy + 0.6, rad * 0.9, seed + 91, count=count, spread=spread, clip=clip, tone_shift=1)
    front = leaves_v2(r, cx, cy, rad, seed, count=count + 1, spread=spread, clip=clip)
    whole = back | front
    add_sparkles(r, front, seed)
    return whole


def add_sparkles(r, mask, seed):
    """Sun catching leaf tips: single FOL[5] pixels on the upper-left edge of lit leaves, a few per cluster."""
    rnd = np.random.RandomState(seed % 1000)
    edge = mask & ~np.roll(np.roll(mask, 1, 0), 1, 1)
    lit = edge & np.all(np.isin(r.img, [FOL[4], FOL[3]]), axis=2).all(axis=2) if False else edge
    sel = lit & (rnd.rand(*mask.shape) < 0.30)
    r.img[sel] = SPARK


def pot_v4(r, x, y, seed):
    """Planter with rim highlight, corner bolts, visible orange mulch, and a fuller leaf fan."""
    r.cast(x, x + 12, y + 12)
    pot = r.mask(x, y + 4, x + 12, y + 12)
    r.img[pot] = art_v2.POT[1]
    r.rect(x, y + 4, x + 12, y + 6, art_v2.POT[2])
    r.rect(x + 1, y + 4, x + 11, y + 5, H("#6F92C4"))              # lit top lip
    r.rect(x, y + 4, x + 1, y + 12, art_v2.POT[2])
    r.rect(x + 11, y + 6, x + 12, y + 12, art_v2.POT[0])            # shaded right side
    r.rect(x, y + 11, x + 12, y + 12, art_v2.POT[0])
    r.rect(x + 1, y + 8, x + 11, y + 9, art_v2.POT[0])              # metal band
    for bx in (x + 2, x + 9):
        r.img[y + 7, bx] = H("#8FB0DA")                               # bolts
    r.outline(pot)
    r.rect(x + 2, y + 5, x + 10, y + 6, H("#9A5A22"))               # orange mulch, as in 08's planters
    r.img[y + 5, x + 4] = H("#E8892B"); r.img[y + 5, x + 7] = H("#E8892B")
    leaves_v4(r, x + 6, y + 1, 6.5, seed, count=6, spread=6)


def grass_tufts(r, bed, rnd_seed=4, n=14):
    rnd = random.Random(rnd_seed)
    ys, xs = np.nonzero(bed)
    for _ in range(n):
        i = rnd.randrange(len(ys)); x, y = int(xs[i]), int(ys[i])
        if tuple(r.img[y, x]) in [tuple(FOL[0]), tuple(FOL[1])]:
            for dx, h in ((-1, 2), (0, 3), (1, 2)):
                for k in range(h):
                    if 0 <= y - k < r.img.shape[0]:
                        r.img[y - k, x + dx] = FOL[3] if k < h - 1 else FOL[4]


def tree_detail(room):
    """Bark streaks, a lit left edge and two limbs that disappear into the canopy."""
    a = room.img
    bark = np.zeros(a.shape[:2], bool)
    for col in art_v2.BARK:
        bark |= np.all(a == col, axis=2)
    bark[:, :120] = False; bark[:, 150:] = False
    rnd = np.random.RandomState(5)
    streak = bark & (rnd.rand(*bark.shape) < 0.16) & (np.roll(bark, 1, 0))
    a[streak] = art_v2.BARK[0]
    lit = bark & ~np.roll(bark, 1, 1)
    a[lit & np.all(a == art_v2.BARK[2], axis=2)] = art_v2.BARK[3]
    for sx in (-1, 1):                                              # limbs
        for t in range(7):
            x, y = 133 + sx * (3 + t), 100 - t
            a[y:y + 2, x] = art_v2.BARK[2] if sx < 0 else art_v2.BARK[1]
            a[y + 2, x] = art_v2.BARK[0]


def pond_detail(room):
    """Ripple arcs, one lily flower and a bright reflection band on the water."""
    a = room.img
    water = np.zeros(a.shape[:2], bool)
    for col in WATER:
        water |= np.all(a == col, axis=2)
    water[:, :118] = False; water[:, 172:] = False; water[:80] = False; water[130:] = False
    rnd = np.random.RandomState(8)
    for cx, cy, rr in ((150, 100, 4), (154, 112, 5), (146, 118, 3)):
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        ring = np.abs(np.hypot(xx - cx, (yy - cy) * 1.6) - rr) < 0.6
        a[ring & water & (xx < cx + 2)] = WATER[3]
    sheen = water & (np.abs((np.mgrid[0:a.shape[0], 0:a.shape[1]][1]) - (np.mgrid[0:a.shape[0], 0:a.shape[1]][0]) * 0.6 - 62) < 1.2)
    a[sheen] = WATER[2]
    a[110, 143] = PINK; a[110, 144] = PINK; a[109, 144] = PINK; a[111, 144] = art_v2.ORANGE


def rock_detail(room):
    a = room.img
    for cx, cy in ((111, 113), (161, 108)):
        box = (slice(cy - 6, cy + 6), slice(cx - 6, cx + 6))
        sub = a[box]
        rock = np.all(np.isin(sub, np.array(art_v2.ROCK)), axis=2) if False else np.zeros(sub.shape[:2], bool)
        for col in art_v2.ROCK[1:]:
            rock |= np.all(sub == col, axis=2)
        ys, xs = np.nonzero(rock)
        if len(ys) == 0:
            continue
        top = ys.min()
        for y, x in zip(ys, xs):
            if y == top or (y == top + 1 and (x + y) % 2 == 0):
                sub[y, x] = MOSS if x % 2 == 0 else FOL[3]            # moss cap
        mid = int(np.median(xs))
        for k in range(3):
            if 0 <= top + 3 + k < sub.shape[0]:
                sub[top + 3 + k, mid - 1 + k // 2] = art_v2.ROCK[0]     # crack


def flowers_v4(room, spots):
    for i, (x, y) in enumerate(spots):
        art_v2.flower(room, x, y)
        if i % 2:
            room.img[y - 1, x - 1] = H("#FFD84A"); room.img[y - 1, x + 1] = H("#FFD84A")


# ----------------------------------------------------------------------------- materials

def late_masks(a):
    """Masks for the details applied at the very end, found on the finished (remapped) frame."""
    out = {}
    joint = np.all(a == np.array(bst.STONE[2], np.uint8), axis=2)
    floorish = np.zeros(a.shape[:2], bool)
    for c in (bst.STONE[3], bst.STONE[2]):
        floorish |= np.all(a == np.array(c, np.uint8), axis=2)
    floorish[:34] = False
    base = np.all(a == np.array(bst.STONE[3], np.uint8), axis=2); base[:34] = False
    out["bevel_hi"] = base & (np.roll(joint, 1, 0) | np.roll(joint, 1, 1))     # just inside the top and left joints
    out["bevel_lo"] = base & (np.roll(joint, -1, 0) | np.roll(joint, -1, 1))   # just inside the bottom and right joints
    wood = np.all(a == art_v2.H("#B8671F"), axis=2)
    rnd = np.random.RandomState(12)
    grain = np.zeros_like(wood)
    for y in range(wood.shape[0]):
        x = 0
        while x < wood.shape[1]:
            if rnd.rand() < 0.07:
                grain[y, x:x + rnd.randint(3, 7)] = True
                x += 8
            x += 2
    out["wood_grain"] = wood & grain
    out["wood_light"] = wood & np.roll(~wood, 1, 0)                              # lit edge on wood tops
    return out


def apply_late(a, masks):
    def tint(m, add):
        f = a[m].astype(np.int16) + np.array(add, np.int16)
        a[m] = np.clip(f, 0, 255).astype(np.uint8)
    tint(masks["bevel_hi"], (7, 7, 6))
    tint(masks["bevel_lo"], (-9, -10, -10))
    tint(masks["wood_grain"], (-26, -24, -14))
    tint(masks["wood_light"], (22, 20, 14))


def monitors_and_keys(room):
    """Monitor content lines, keyboards and a glowing screen edge on the two desks."""
    a = room.img
    for x0, y0 in ((16, 78), (246, 46)):
        sx, sy = x0 + 10, y0 - 4
        for i, (off, ln) in enumerate(((1, 8), (3, 6), (5, 9), (7, 5))):
            a[sy + off, sx + 1: sx + 1 + ln] = SCREEN_TXT if i % 2 == 0 else WATER[3]
        a[sy - 1, sx: sx + 12] = WATER[3]                                         # screen glow edge
        for k in range(0, 11, 2):                                                  # key caps
            a[y0 + 8, x0 + 10 + k] = H("#6A7392")
            a[y0 + 9, x0 + 11 + k] = H("#3A4160")
        a[y0 + 4, x0 + 26: x0 + 30] = H("#C9CEDA")                                 # paper corner
        a[y0 + 5, x0 + 26: x0 + 29] = H("#8C93A6")


def lamp_detail(room, lamps):
    a = room.img
    for cx, cy in lamps:
        a[cy - 1: cy + 1, cx: cx + 1] = HOT                                       # white-hot core
        a[cy + 9, cx - 2: cx + 3] = H("#3A4160")                                   # base plate
        a[cy + 8, cx - 1: cx + 2] = H("#6A7392")
        a[cy + 2: cy + 8, cx] = H("#6A7392")                                       # lit pole edge


def rim_bricks(room):
    """Brick joints and moss on the garden rim's front face."""
    a = room.img
    for y in (128, 131):
        a[y, 96:176] = np.where(np.all(a[y, 96:176] == art_v2.H("#968A85"), axis=1)[:, None], np.array(bst.STONE[0], np.uint8), a[y, 96:176])
    for y, off in ((126, 0), (129, 8)):
        for x in range(96 + off, 176, 16):
            if tuple(a[y, x]) == tuple(bst.STONE[1]):
                a[y: y + 2, x] = bst.STONE[0]
    rnd = np.random.RandomState(3)
    for x in rnd.choice(range(98, 174), 12, replace=False):
        a[133, x] = MOSS
        if rnd.rand() < 0.5:
            a[132, x] = FOL[2]


def wall_detail(room):
    """Panel seams and a darker wainscot band on the north wall, a lit cornice on the east wall."""
    a = room.img
    wall = np.all(a == np.array(bst.STONE[1], np.uint8), axis=2)
    wall[:, 292:] = False; wall[31:] = False
    for x in (24, 72, 120, 200, 232, 276):
        m = wall.copy(); m[:, :x] = False; m[:, x + 1:] = False
        a[m] = bst.STONE[0]
    band = wall.copy(); band[:22] = False
    a[band] = (a[band].astype(np.float32) * 0.9).astype(np.uint8)
    a[22, :292][wall[22, :292]] = np.array(bst.STONE[2], np.uint8)
