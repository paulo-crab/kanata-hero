"""Mock 2.4: the same garden corner drawn on a FINER grid (32 px tiles instead of 16), to show the detail ceiling.

Region: the garden and its walking ring, 130x100 logical px at 16 px tiles -> 260x200 here. Same palette, same
objects, same light as Mock 2.3; only the pixel density changes. No characters: they would need redrawing at
32x48 (about four times the pixels each). DRAFT for board validation.
"""
import math
import random

import numpy as np
from PIL import Image

import base
import passes
import art_v2
import art_v4
import build_scale_test as bst
import environment as env

W, H = 260, 200
FOL, H_ = art_v2.FOL, art_v2.H
WATER = art_v4.WATER


def make_room():
    return env.Room()


def floor(r):
    r.img[:] = bst.STONE[3]
    for row in range(0, H, 64):
        r.rect(0, row, W, row + 1, bst.STONE[2])
        off = 32 if (row // 64) % 2 else 0
        for col in range(off - 64, W, 64):
            r.rect(max(col, 0), row, max(col, 0) + 1, row + 64, bst.STONE[2])
    band = r.mask(4, 0, 260, 200) & ~r.mask(20, 16, 244, 184)
    r.img[band] = bst.STONE[2]
    r.img[band & ~r.mask(5, 1, 259, 199)] = bst.STONE[1]
    inner = r.mask(19, 15, 245, 185) & ~r.mask(20, 16, 244, 184)
    r.img[inner] = bst.STONE[1]
    r.img[band & (r.y < 3)] = bst.STONE[3]


def planter_rim(r, x0, y0, x1, y1, face):
    r.cast(x0, x1, y1, rows=3)
    f = r.mask(x0, y1 - face, x1, y1)
    r.img[f] = bst.STONE[1]
    r.rect(x0, y1 - face, x1, y1 - face + 2, bst.STONE[2])
    r.rect(x0, y1 - 2, x1, y1, bst.STONE[0])
    for row_y, off in ((y1 - face + 2, 0), (y1 - face // 2 + 1, 8)):          # brick courses
        r.rect(x0, row_y + face // 2 - 3, x1, row_y + face // 2 - 2, bst.STONE[0])
        for x in range(x0 + off + 16, x1, 16):
            r.rect(x, row_y, x + 1, row_y + face // 2 - 3, bst.STONE[0])
    rim = r.mask(x0, y0, x1, y1 - face) & ~r.mask(x0 + 8, y0 + 8, x1 - 8, y1 - face - 4)
    r.img[rim] = bst.STONE[2]
    r.img[rim & (r.y < y0 + 2)] = bst.STONE[3]
    r.img[rim & (r.x < x0 + 2)] = bst.STONE[3]
    r.outline(r.mask(x0, y0, x1, y1))
    rnd = np.random.RandomState(3)
    for x in rnd.choice(range(x0 + 4, x1 - 4), 22, replace=False):                # moss
        r.img[y1 - 3, x] = art_v4.MOSS
        if rnd.rand() < 0.6:
            r.img[y1 - 4, x] = FOL[2]


def draw():
    env.W, env.H = W, H          # Room.mask reads these module globals
    try:
        return _draw()
    finally:
        env.W, env.H = 320, 192


def _draw():
    r = make_room()
    floor(r)
    x0, y0, x1, y1, face = 52, 44, 212, 156, 16
    planter_rim(r, x0, y0, x1, y1, face)
    bed = r.mask(x0 + 8, y0 + 8, x1 - 8, y1 - face - 4)
    r.img[bed] = FOL[1]
    # Water: a winding channel and pool with ripples, a lily pad cluster and a flower.
    water = np.zeros((H, W), bool)
    for t in np.linspace(0, 1, 60):
        water |= r.disc(160 + 20 * math.sin(t * 5.0), 56 + t * 60, 8 + 5 * t)
    water |= r.disc(150, 112, 18, 10)
    water &= bed
    r.img[water] = WATER[1]
    r.img[water & ~bst.shifted(water, 0, -1)] = WATER[0]
    r.img[water & (r.y % 7 == 0) & (r.x % 3 != 0)] = WATER[2]                      # wavelets
    for cx, cy, rr in ((150, 96, 7), (156, 114, 9), (140, 122, 5)):
        ring = np.abs(np.hypot(r.x - cx, (r.y - cy) * 1.7) - rr) < 0.7
        r.img[ring & water & (r.x < cx + 3)] = WATER[3]
    r.img[(np.abs(r.x - (r.y * 0.6 + 120)) < 2) & water] = WATER[2]                  # sheen band
    for lx, ly in ((146, 108), (156, 118), (136, 116)):
        pad = r.disc(lx, ly, 4.5, 3.2) & water
        r.img[pad] = FOL[3]
        r.img[pad & (r.x < lx - 1) & (r.y < ly)] = FOL[4]
        r.img[ly, lx:lx + 5] = WATER[0]
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        r.img[107 + dy, 147 + dx] = art_v4.PINK
    r.img[107, 147] = art_v2.ORANGE
    # Ground cover and shrubs back to front.
    rnd = random.Random(40)
    clip = bed & ~water
    for sx, sy, rd in ((74, 78, 11), (96, 72, 11), (190, 80, 11), (72, 110, 11), (192, 112, 11), (80, 130, 11),
                       (104, 134, 11), (186, 132, 11), (66, 94, 9), (196, 96, 9)):
        art_v4.leaves_v4(r, sx, sy, rd, int(sx * 7 + sy), count=6, spread=rd, clip=clip)
    # Rocks with moss and a crack.
    for rx, ry, rr in ((80, 122, 12), (186, 112, 9)):
        m = r.blob(rx, ry, rr, 1.0, lobes=4, amp=0.12) & bed
        bst.shade_mask(r.img, m, art_v2.ROCK, k_shadow=2, k_light=2)
        r.img[m & ~bst.shifted(m, -1, -1)] = art_v2.ROCK[3]
        r.outline(m, art_v2.ROCK[0])
        ys, xs = np.nonzero(m)
        for y, x in zip(ys, xs):
            if y <= ys.min() + 2 and (x + y) % 3:
                r.img[y, x] = art_v4.MOSS if x % 2 else FOL[3]
        r.img[ys.min() + 6: ys.min() + 11, int(np.median(xs))] = art_v2.ROCK[0]
    # Tree: textured trunk with root flare and limbs, then a canopy of many small fans.
    cx = 126
    rows = {}
    for i, y in enumerate(range(92, 136, 2)):
        rows[y] = 8 + int(i * 0.62) + (4 if y > 124 else 0)
    trunk = np.zeros((H, W), bool)
    for y, w in rows.items():
        trunk[y:y + 2, cx - w // 2: cx + (w + 1) // 2] = True
    for sgn in (-1, 1):
        for t in range(14):
            trunk[127 + t // 3: 131 + t // 3, cx + sgn * (11 + t)] = True
    bst.shade_mask(r.img, trunk, art_v2.BARK, k_shadow=3, k_light=2)
    rn = np.random.RandomState(5)
    streak = trunk & (rn.rand(H, W) < 0.2) & np.roll(trunk, 1, 0)
    r.img[streak] = art_v2.BARK[0]
    r.outline(trunk, art_v2.BARK[0])
    canopy_spots = [(92, 66, 18), (150, 56, 18), (118, 48, 20), (98, 88, 14), (130, 72, 18), (166, 70, 12), (76, 84, 12)]
    for i, (px, py, rd) in enumerate(canopy_spots):
        art_v4.leaves_v4(r, px, py, rd, 70 + i)
    for sgn in (-1, 1):                                                           # limbs show through the canopy gaps
        for t in range(14):
            x, y = cx + sgn * (6 + t), 96 - t
            r.img[y: y + 3, x] = art_v2.BARK[2] if sgn < 0 else art_v2.BARK[1]
            r.img[y + 3, x] = art_v2.BARK[0]
    # White flowers with petals, plus a yellow pair.
    for i, (fx, fy) in enumerate(((76, 134), (70, 100), (198, 126), (96, 138), (192, 100), (126, 56))):
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)):
            r.img[fy + dy, fx + dx] = art_v2.PETAL
        r.img[fy + 1, fx + 1] = art_v2.PETAL_SHADE
        r.img[fy, fx] = art_v2.ORANGE
    # Lamps at the rim corners, with a housing, a hot core and a base plate.
    for lx, ly in ((42, 36), (222, 36), (222, 156)):
        r.rect(lx - 3, ly + 2, lx + 3, ly + 20, H_("#1C2038"))
        r.rect(lx - 3, ly + 2, lx - 2, ly + 20, H_("#6A7392"))
        r.rect(lx - 5, ly + 18, lx + 5, ly + 21, H_("#3A4160"))
        head = r.mask(lx - 5, ly - 8, lx + 5, ly + 2)
        r.img[head] = H_("#FFC83D")
        r.rect(lx - 3, ly - 6, lx + 3, ly, H_("#FFF0A0"))
        r.rect(lx - 1, ly - 4, lx + 1, ly - 2, art_v4.HOT)
        r.outline(head, H_("#0E1020"))
    return r


def lit(r):
    a = r.img
    passes.slab_variation(a, seed=3, grain=False)
    objects = ~passes.floor_mask(a)
    passes.cast_shadows(a, objects, dx=8, dy=6)
    greens = np.zeros((H, W), bool)
    for col in FOL[1:]:
        greens |= np.all(a == col, axis=2)
    passes.cast_shadows(a, greens, dx=20, dy=16, mul=(0.84, 0.84, 0.90))
    # lamp glow at the doubled scale
    floor = passes.floor_mask(a)
    yy, xx = np.mgrid[0:H, 0:W]
    for lx, ly in ((42, 36), (222, 36), (222, 156)):
        d = np.hypot(xx - lx, (yy - ly) * 1.25)
        passes.tint(a, floor & (d < 52) & (d >= 24), add=(9, 6, -3))
        passes.tint(a, floor & (d < 24), add=(16, 11, -6))
    return a


if __name__ == "__main__":
    a = lit(draw())
    Image.fromarray(a).resize((W * 4, H * 4), Image.NEAREST).save("m2_4_finer_grid_garden.png")
    print("ok")
