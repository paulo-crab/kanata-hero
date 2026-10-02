"""Gate 1 review room, drawn to the finish of reference 08 at 16 px.

Replaces the scale-test placeholder environment (STYLE_BIBLE section 8 allows
replacing it). Same layout in cells so the review composition is unchanged:
garden ring in the centre, printer terminal in the north alcove, Records door
in the east wall at the end of a two-cell route. Palette pixels only
(STYLE_BIBLE section 3): no blending, no gradients, stepped light.
"""
import math
import random

import numpy as np

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
import build_scale_test as bst  # noqa: E402
import rich_finish  # noqa: E402

INK, STONE, GLASS, WOOD, GREEN, BRASS, CORAL = bst.INK, bst.STONE, bst.GLASS, bst.WOOD, bst.GREEN, bst.BRASS, bst.CORAL
shifted, shade_mask = bst.shifted, bst.shade_mask
W, H = 320, 192  # a little taller than the 180 view so bottom props are whole


class Room:
    def __init__(self):
        self.img = np.zeros((H, W, 3), np.uint8)
        yy, xx = np.mgrid[0:H, 0:W]
        self.x, self.y = xx + 0.5, yy + 0.5

    def rect(self, x0, y0, x1, y1, c):
        self.img[max(0, y0):y1, max(0, x0):x1] = c

    def mask(self, x0, y0, x1, y1):
        m = np.zeros((H, W), bool)
        m[max(0, y0):y1, max(0, x0):x1] = True
        return m

    def disc(self, cx, cy, rx, ry=None):
        ry = ry or rx
        return ((self.x - cx) / rx) ** 2 + ((self.y - cy) / ry) ** 2 <= 1

    def blob(self, cx, cy, r, phase, lobes=6, amp=0.16):
        dx, dy = self.x - cx, self.y - cy
        rr = r * (1 + amp * np.sin(lobes * np.arctan2(dy, dx) + phase))
        return dx * dx + dy * dy <= rr * rr

    def edge(self, m):
        return m & ~(shifted(m, 1, 0) & shifted(m, -1, 0) & shifted(m, 0, 1) & shifted(m, 0, -1))

    def outline(self, m, c=None):
        self.img[self.edge(m)] = INK[0] if c is None else c

    def cast(self, x0, x1, y, rows=2):
        """Contact shadow strip below a base: darkest against the base."""
        self.rect(x0 + 1, y, x1 + 1, y + 1, INK[2])
        if rows > 1:
            self.rect(x0 + 2, y + 1, x1 + 2, y + rows, INK[3])


# ------------------------------------------------------------------ floor

def floor(r):
    r.img[:] = STONE[3]
    # Broad slabs: 32 x 32 running bond, joints in the stone mid tone.
    for row in range(0, H, 32):
        r.rect(0, row, W, row + 1, STONE[2])
        off = 16 if (row // 32) % 2 else 0
        for col in range(off, W, 32):
            r.rect(col, row, col + 1, row + 32, STONE[2])
    # Sparse wear: two-pixel chips on a few slabs, never on the route.
    rnd = random.Random(11)
    for _ in range(34):
        x, y = rnd.randrange(4, W - 6), rnd.randrange(40, H - 4)
        if 72 <= y <= 108 and x >= 176:
            continue
        r.img[y, x:x + 2] = STONE[2]
    # Garden walking ring: inlay border two cells out from the planter, corner squares.
    x0, y0, x1, y1 = 72, 56, 200, 156
    band = r.mask(x0, y0, x1, y1) & ~r.mask(x0 + 8, y0 + 8, x1 - 8, y1 - 8)
    r.img[band] = STONE[2]
    r.img[band & ~r.mask(x0 + 1, y0 + 1, x1 - 1, y1 - 1)] = STONE[1]
    inner = r.mask(x0 + 7, y0 + 7, x1 - 7, y1 - 7) & ~r.mask(x0 + 8, y0 + 8, x1 - 8, y1 - 8)
    r.img[inner] = STONE[1]
    r.img[band & (r.y < y0 + 2) & (r.x > x0 + 1) & (r.x < x1 - 1)] = STONE[3]  # lit top edge
    for cx, cy in [(x0, y0), (x1 - 12, y0), (x0, y1 - 12), (x1 - 12, y1 - 12)]:
        sq = r.mask(cx, cy, cx + 12, cy + 12)
        r.img[sq] = STONE[1]
        r.rect(cx + 2, cy + 2, cx + 10, cy + 10, STONE[2])
        r.rect(cx + 4, cy + 4, cx + 8, cy + 8, STONE[3])
        r.outline(sq, STONE[0])


GLYPHS = {  # 3x5 sign lettering
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "E": ["###", "#..", "##.", "#..", "###"],
    "C": [".##", "#..", "#..", "#..", ".##"],
    "O": [".#.", "#.#", "#.#", "#.#", ".#."],
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "S": [".##", "#..", ".#.", "..#", "##."],
}


def route(r):
    """Two-cell route to the Records door, ending on a lit brass threshold rug."""
    # Inlay edge lines guide the eye along the route.
    r.rect(200, 74, 260, 75, STONE[2])
    r.rect(200, 106, 260, 107, STONE[2])
    # Threshold rug in front of the door: the brightest floor in the room.
    rug = r.mask(260, 76, 292, 106)
    r.img[rug] = BRASS[3]
    r.img[r.edge(rug)] = BRASS[2]
    # Inlaid wayfinding: RECORDS and an arrow toward the door, in dark brass.
    x = 262
    for ch in "RECORDS":
        for dy, row in enumerate(GLYPHS[ch]):
            for dx, bit in enumerate(row):
                if bit == "#":
                    r.img[82 + dy, x + dx] = BRASS[0]
        x += 4
    r.rect(264, 96, 284, 98, BRASS[0])  # arrow shaft
    for i in range(5):  # arrow head
        r.rect(284 + i, 92 + i, 285 + i, 102 - i, BRASS[0])


# ------------------------------------------------------------------ walls

def north_wall(r):
    # Wall top plane (seen from above), then the lit face with glass bays.
    r.rect(0, 0, W, 6, INK[1])
    r.rect(0, 0, W, 1, INK[2])
    r.rect(0, 4, W, 5, GLASS[2])  # lit trim on the wall cap
    r.rect(0, 5, W, 6, INK[0])
    r.rect(0, 6, W, 31, STONE[1])
    r.rect(0, 6, W, 7, STONE[2])
    # Printer alcove: brighter stone with a brass wayfinding plaque.
    r.rect(134, 6, 202, 31, STONE[2])
    r.rect(134, 6, 136, 31, STONE[1])
    r.rect(200, 6, 202, 31, STONE[0])
    plaque = r.mask(154, 10, 182, 17)
    r.img[plaque] = BRASS[2]
    r.rect(154, 10, 182, 11, BRASS[3])
    r.rect(154, 16, 182, 17, BRASS[0])
    for x in (160, 167, 174):
        r.rect(x, 12, x + 3, 15, INK[1])
    # Glass bays with dark frames, cooler lower pane, one stepped reflection band.
    for i, x in enumerate([6, 38, 84, 212, 244, 284]):
        w = 26
        r.rect(x - 2, 9, x + w + 2, 29, INK[0])
        pane = r.mask(x, 11, x + w, 27)
        r.img[pane] = GLASS[1]
        r.img[pane & (r.y > 20)] = GLASS[0]
        band = pane & (np.abs((r.x - x) - (r.y - 11) * 0.8 - (6 + 4 * (i % 2))) < 1.6)
        r.img[band] = GLASS[3]
        r.img[pane & (np.abs((r.x - x) - (r.y - 11) * 0.8 - (11 + 4 * (i % 2))) < 0.6)] = GLASS[2]
        r.rect(x + w // 2, 11, x + w // 2 + 1, 27, INK[0])
        r.rect(x, 26, x + w, 27, GLASS[2])  # glass glow sill, one hard step
    # Baseboard and the wall's cast shadow on the floor.
    r.rect(0, 30, W, 32, INK[0])
    r.rect(0, 32, W, 33, INK[2])
    r.rect(0, 33, W, 34, INK[3])


def east_wall(r, door_open=0.0):
    """Thick east wall with lit trim and the sliding glass Records door.

    door_open: 0 = closed, 1 = both panels slid fully into the wall pockets."""
    x0 = 292
    mass = r.mask(x0, 34, W, H) & ~r.mask(x0, 72, W, 110)
    r.img[mass] = INK[1]
    r.img[mass & (r.x >= x0 + 3)] = INK[0]
    r.img[mass & (r.x < x0 + 1)] = INK[2]
    r.img[mass & (r.x >= x0 + 1) & (r.x < x0 + 2)] = GLASS[2]  # lit trim
    # Open doorway: Records' sea-blue floor visible through it, lit near the threshold.
    room = r.mask(x0, 72, W, 110)
    r.img[room] = GLASS[1]
    for yy in range(80, 110, 10):  # Records floor tiles
        r.rect(x0, yy, W, yy + 1, GLASS[0])
    r.rect(x0 + 14, 72, x0 + 15, 110, GLASS[0])
    r.img[room & (r.x < x0 + 8)] = GLASS[2]  # light pooling at the threshold
    r.rect(x0, 72, W, 75, INK[0])  # shadow under the lintel
    r.rect(x0, 75, W, 76, GLASS[0])
    # A filing cabinet inside Records, so the opening reads as another room.
    cab = r.mask(x0 + 18, 82, W, 100)
    r.img[cab] = STONE[2]
    r.rect(x0 + 18, 82, W, 84, STONE[3])
    for yy in (88, 94):
        r.rect(x0 + 18, yy, W, yy + 1, STONE[0])
        r.rect(x0 + 21, yy + 2, x0 + 24, yy + 3, BRASS[2])
    r.outline(cab)
    r.cast(x0 + 18, W - 1, 100, rows=1)
    # Sliding glass panels: framed glass with one stepped reflection band,
    # meeting at a centre seam and sliding into pockets behind the jambs.
    travel = int(round(15 * max(0.0, min(1.0, door_open))))
    for ya, yb, sgn in ((72, 91, -1), (91, 110, 1)):
        ya2, yb2 = ya + sgn * travel, yb + sgn * travel
        panel = r.mask(x0 - 1, ya2, x0 + 7, yb2) & r.mask(x0 - 1, 64, x0 + 7, 118)
        r.img[panel] = GLASS[2]
        r.img[panel & (r.x >= x0 + 4)] = GLASS[1]
        band = panel & (np.abs((r.y - ya2) - (r.x - x0) * 1.2 - 6) < 1.5)
        r.img[band] = GLASS[3]
        r.img[r.edge(panel)] = BRASS[1]
        edge_y = yb2 - 1 if sgn < 0 else ya2
        r.rect(x0 - 1, edge_y, x0 + 7, edge_y + 1, INK[0])  # meeting stile
        r.rect(x0 + 1, (ya2 + yb2) // 2 - 2, x0 + 2, (ya2 + yb2) // 2 + 2, BRASS[3])  # pull
    # Floor track the panels run in.
    r.rect(x0 - 2, 72, x0 - 1, 110, INK[2])
    # Brass door frame: jambs with lit faces, lintel line above.
    for y0 in (64, 110):
        post = r.mask(x0 - 2, y0, W, y0 + 8)
        r.img[post] = BRASS[1]
        r.rect(x0 - 2, y0, W, y0 + 2, BRASS[3])
        r.rect(x0 - 2, y0 + 2, W, y0 + 3, BRASS[2])
        r.rect(x0 - 2, y0 + 7, W, y0 + 8, BRASS[0])
        r.outline(post)
    # Records sign on the lintel: brass plaque with a folder icon.
    plaque = r.mask(x0 + 2, 50, x0 + 22, 62)
    r.img[plaque] = BRASS[2]
    r.rect(x0 + 2, 50, x0 + 22, 51, BRASS[3])
    r.rect(x0 + 2, 61, x0 + 22, 62, BRASS[0])
    r.outline(plaque)
    r.rect(x0 + 7, 54, x0 + 17, 59, INK[1])
    r.rect(x0 + 7, 53, x0 + 11, 54, INK[1])
    r.rect(x0 + 8, 55, x0 + 16, 58, CORAL[2])
    # Brass threshold.
    r.rect(x0 - 3, 72, x0, 110, BRASS[2])
    r.rect(x0 - 3, 72, x0 - 2, 110, BRASS[3])
    # Lamps on the jambs, two hard glow steps each.
    for cy in (52, 126):
        lamp(r, x0 - 8, cy)


def lamp(r, cx, cy, wall=False):
    if not wall:
        r.rect(cx - 1, cy, cx + 2, cy + 9, INK[1])
        r.rect(cx - 1, cy, cx, cy + 9, INK[2])
        r.cast(cx - 2, cx + 2, cy + 9, rows=1)
    halo = r.disc(cx + 0.5, cy - 0.5, 5.2)
    r.img[halo & (np.all(r.img == STONE[3], axis=2))] = BRASS[3]
    head = r.mask(cx - 2, cy - 4, cx + 3, cy + 1)
    r.img[head] = BRASS[2]
    r.rect(cx - 1, cy - 3, cx + 2, cy, BRASS[3])
    r.outline(head, INK[0])


# ------------------------------------------------------------------ props

def block(r, x0, y0, x1, y1, face, top, side, shadow=True):
    """Top plane, darker front face, dark underside, outline, contact shadow."""
    if shadow:
        r.cast(x0, x1, y1)
    t = r.mask(x0, y0, x1, y1 - face)
    r.img[t] = top[2]
    r.rect(x0, y0, x1, y0 + 1, top[3])
    r.rect(x0, y0, x0 + 1, y1 - face, top[3])
    f = r.mask(x0, y1 - face, x1, y1)
    r.img[f] = side[1]
    r.rect(x0, y1 - face, x1, y1 - face + 1, side[2])
    r.rect(x0, y1 - 1, x1, y1, side[0])
    r.outline(r.mask(x0, y0, x1, y1))


def leaves(r, cx, cy, rad, seed, ramp=GREEN, count=5, spread=None, clip=None):
    """Rich-finish leaf fans (kit/rich_finish.py): five tones, dark edge, two layers, sparkle tips."""
    return rich_finish.leaves(r, cx, cy, rad, seed, ramp, count=count, spread=spread, clip=clip)


def pot_plant(r, x, y, seed):
    """Blue planter with a leaf fan, the 08 prop that frames every edge (rich finish)."""
    rich_finish.planter(r, x, y, seed, GREEN)


def desk(r, x0, y0, seed):
    block(r, x0, y0, x0 + 34, y0 + 16, 5, WOOD, WOOD)
    # Monitor: dark housing first, then the cool screen with one reflection step.
    r.rect(x0 + 9, y0 - 5, x0 + 23, y0 + 6, INK[0])
    r.rect(x0 + 10, y0 - 4, x0 + 22, y0 + 4, GLASS[1])
    r.rect(x0 + 10, y0 - 4, x0 + 22, y0 - 2, GLASS[2])
    r.rect(x0 + 11, y0 - 3, x0 + 14, y0 - 2, GLASS[3])
    r.rect(x0 + 15, y0 + 6, x0 + 17, y0 + 8, INK[1])
    # Keyboard and a paper on the top plane.
    r.rect(x0 + 10, y0 + 8, x0 + 21, y0 + 10, INK[2])
    r.rect(x0 + 25, y0 + 3, x0 + 31, y0 + 8, STONE[3])
    r.outline(r.mask(x0 + 25, y0 + 3, x0 + 31, y0 + 8), STONE[1])
    # Small plant at the desk end.
    leaves(r, x0 + 4, y0 + 2, 3.6, seed, count=4, spread=3)
    chair(r, x0 + 11, y0 + 18)


def chair(r, x0, y0):
    """Coral task chair seen from above: backrest, seat plane, front face, base."""
    r.cast(x0 + 1, x0 + 11, y0 + 10, rows=1)
    seat = r.mask(x0, y0 + 3, x0 + 12, y0 + 10)
    r.img[seat] = CORAL[2]
    r.rect(x0 + 1, y0 + 4, x0 + 11, y0 + 5, CORAL[3])
    r.rect(x0, y0 + 8, x0 + 12, y0 + 10, CORAL[1])
    r.outline(seat)
    back = r.mask(x0 + 1, y0, x0 + 11, y0 + 4)
    r.img[back] = CORAL[1]
    r.rect(x0 + 2, y0 + 1, x0 + 10, y0 + 2, CORAL[2])
    r.outline(back)


def sofa(r, x0, y0, w=30):
    """Terracotta lounge sofa seen from above: backrest, cushions, arms."""
    r.cast(x0, x0 + w, y0 + 14)
    body = r.mask(x0, y0, x0 + w, y0 + 14)
    r.img[body] = WOOD[1]
    r.rect(x0 + 3, y0 + 4, x0 + w - 3, y0 + 11, WOOD[2])
    for cx in range(x0 + 3, x0 + w - 3, (w - 6) // 2):
        r.rect(cx, y0 + 4, cx + 1, y0 + 11, WOOD[1])
    r.rect(x0 + 3, y0 + 4, x0 + w - 3, y0 + 5, WOOD[3])
    r.rect(x0, y0, x0 + w, y0 + 3, WOOD[0])
    r.rect(x0, y0 + 12, x0 + w, y0 + 14, WOOD[0])
    r.outline(body)


def side_table(r, cx, cy):
    top = r.disc(cx, cy, 6, 4.5)
    r.cast(cx - 5, cx + 5, cy + 5, rows=1)
    r.img[top] = INK[2]
    r.img[top & ~shifted(top, -1, -1)] = INK[3]
    r.outline(top)
    leaves(r, cx, cy - 2, 3.2, 9, count=4, spread=2.5)


def bench(r, x0, y0):
    block(r, x0, y0, x0 + 32, y0 + 10, 4, WOOD, WOOD)
    for i in range(1, 4):
        r.rect(x0 + i * 8, y0 + 1, x0 + i * 8 + 1, y0 + 6, WOOD[1])


def printer(r):
    """Badge printer terminal in the alcove: housing first, then the teal screen."""
    block(r, 138, 33, 198, 50, 6, STONE, STONE)
    body = r.mask(152, 26, 184, 42)
    r.img[body] = STONE[3]
    r.rect(152, 36, 184, 42, STONE[1])
    r.rect(152, 36, 184, 37, STONE[2])
    r.outline(body)
    scr = r.mask(156, 29, 170, 35)
    r.img[scr] = GLASS[2]
    r.rect(156, 29, 170, 30, GLASS[3])
    r.outline(scr, GLASS[0])
    r.rect(174, 31, 181, 33, INK[0])  # card slot
    for i, c in enumerate([CORAL[2], GLASS[2], BRASS[2]]):
        card = r.mask(142 + i * 4, 40 + i, 149 + i * 4, 45 + i)
        r.img[card] = c
        r.outline(card, INK[1])


def mail_counter(r, x0, y0):
    block(r, x0, y0, x0 + 52, y0 + 16, 6, WOOD, WOOD)
    for i, (dx, w, h, c) in enumerate([(4, 8, 6, STONE), (14, 9, 7, WOOD), (25, 7, 5, STONE), (34, 10, 7, WOOD)]):
        bx, by = x0 + dx, y0 + 7 - h
        box = r.mask(bx, by, bx + w, by + h)
        r.img[box] = c[3] if c is STONE else c[2]
        r.rect(bx, by, bx + w, by + 2, c[3] if c is WOOD else STONE[3])
        r.rect(bx + w // 2, by, bx + w // 2 + 1, by + h, BRASS[1] if c is WOOD else STONE[1])
        r.outline(box)
    r.rect(x0 + 44, y0 + 4, x0 + 50, y0 + 6, CORAL[2])  # courier strap


# ------------------------------------------------------------------ garden landmark

def garden(r, stage=None):
    """The garden landmark. `stage(name)` is called as each part is complete (base, foliage, rocks,
    canopy, trunk, accents) so the kit can capture the parts; drawing does not depend on it."""
    stage = stage or (lambda name: None)
    x0, y0, x1, y1, face = 96, 78, 176, 134, 8
    r.cast(x0, x1, y1, rows=2)
    # Rim: lit top plane, jointed side face, dark base.
    f = r.mask(x0, y1 - face, x1, y1)
    r.img[f] = STONE[1]
    r.rect(x0, y1 - face, x1, y1 - face + 1, STONE[2])
    r.rect(x0, y1 - 1, x1, y1, STONE[0])
    for x in range(x0 + 16, x1, 16):
        r.rect(x, y1 - face + 1, x + 1, y1 - 1, STONE[0])
    rim = r.mask(x0, y0, x1, y1 - face) & ~r.mask(x0 + 4, y0 + 4, x1 - 4, y1 - face - 2)
    r.img[rim] = STONE[2]
    r.img[rim & (r.y < y0 + 1)] = STONE[3]
    r.img[rim & (r.x < x0 + 1)] = STONE[3]
    r.outline(r.mask(x0, y0, x1, y1))
    bed = r.mask(x0 + 4, y0 + 4, x1 - 4, y1 - face - 2)
    r.img[bed] = GREEN[0]
    # Stream: a winding channel with a pool, cool ramp, one highlight step, then ripples, a sheen and a lily.
    water = np.zeros((H, W), bool)
    for t in np.linspace(0, 1, 40):
        cx = 150 + 10 * math.sin(t * 5.0)
        cy = y0 + 10 + t * 30
        water |= r.disc(cx, cy, 4.2 + 2.5 * t)
    water |= r.disc(146, 116, 9, 5.5)
    water &= bed
    r.img[water] = GLASS[1]
    r.img[water & ~shifted(water, 0, -1)] = GLASS[0]
    r.img[water & ~shifted(water, 0, 2) & shifted(water, 0, -1)] = GLASS[2]
    for lx, ly in [(143, 116), (151, 99)]:
        pad = r.disc(lx, ly, 2.2, 1.6)
        r.img[pad & water] = GREEN[3]
    rich_finish.pond_detail(r, water, GLASS)
    stage("base")
    # Ground cover and shrubs around the edge, back to front.
    clip = bed & ~water
    for i, (sx, sy) in enumerate([(106, 88), (118, 86), (164, 88), (104, 104), (166, 104), (108, 118), (122, 120), (164, 118)]):
        leaves(r, sx, sy, 5.5, 40 + i, count=5, spread=5, clip=clip)
    stage("foliage")
    # Grey rocks with a moss cap and a crack.
    for rx, ry, rr in [(111, 113, 5), (161, 108, 4)]:
        rich_finish.rock(r, rx, ry, rr, bed, bst)
    stage("rocks")
    # Canopy: seven smaller fans per crown, overhanging the rim.
    canopy = np.zeros((H, W), bool)
    for i, (cx, cy, cr) in enumerate([(117, 84, 10), (149, 84, 10), (133, 77, 10), (122, 94, 7), (145, 94, 7), (133, 89, 9)]):
        canopy |= leaves(r, cx, cy, cr, 70 + i, count=6, spread=cr * 0.8)
    stage("canopy")
    # Trunk with root flare, bark and limbs, drawn over the canopy's lower edge.
    rich_finish.trunk(r, WOOD, bst)
    stage("trunk")
    # Canopy shadow: one flat step of dark green on the bed below-right of the crown.
    shadow = r.disc(140, 104, 17, 7) & clip & ~canopy
    r.img[shadow & np.all(r.img == GREEN[0], axis=2)] = rich_finish.FOLIAGE_EDGE
    # Grass tufts, then white flowers with orange centres.
    rich_finish.grass_tufts(r, clip & ~canopy, [GREEN[0], rich_finish.FOLIAGE_EDGE], [GREEN[2], GREEN[3]])
    for i, (fx, fy) in enumerate([(104, 112), (106, 120), (168, 110), (124, 121), (162, 121)]):
        rich_finish.flower(r, fx, fy, pair=bool(i % 2))
    # Lamp posts at the rim corners.
    for cx, cy in [(92, 72), (180, 72), (180, 130)]:  # the inset covers the fourth corner
        lamp(r, cx, cy)


# ------------------------------------------------------------------ room

def draw(r, door_open=0.0):
    floor(r)
    route(r)
    north_wall(r)
    east_wall(r, door_open)
    for i, (x, y) in enumerate([(4, 30), (24, 30), (66, 30), (98, 30), (206, 30), (226, 30),
                                (272, 30), (56, 96), (196, 128), (238, 126), (140, 166), (176, 166)]):
        pot_plant(r, x, y, 100 + i)
    sofa(r, 200, 150)
    side_table(r, 240, 160)
    printer(r)
    desk(r, 16, 78, 7)
    desk(r, 246, 46, 8)
    bench(r, 228, 112)
    garden(r)
