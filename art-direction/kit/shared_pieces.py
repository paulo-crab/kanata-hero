"""District-agnostic kit pieces: shelving, free-standing glass partition, terminal desk,
filing cabinet and the window light shaft.

Each piece is a drawing function in the style of gate1/environment.py: it paints palette
constants only (hard pixels, light from the upper left) onto an env.Room, and takes a `Pal`
so a later district recolours it by passing its own ramps. Nothing here names Records.
Pieces are captured into atlas sprites by kitlib.capture (see records_kit.py).

Palette roles (district_palettes.py): ink is shared verbatim, `glass` is the glass / metal /
device ramp, `wall` the linen or panel ramp, `wood` desks and trim, `accent` the district's
files / equipment colour, `floor` the broad floor. Ramps are numpy RGB triples, shadow to light.
"""
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("gate1", "scale-test", "palettes"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import build_scale_test as bst  # noqa: E402
import district_palettes as dp  # noqa: E402
import environment as env  # noqa: E402

INK = bst.INK  # shared by every district


class Pal:
    """A district's eight ramps as RGB arrays (shadow -> light)."""

    def __init__(self, district):
        d = dp.DISTRICTS[district]
        self.name = district
        for role in dp.ROLES:
            setattr(self, role, [bst.hx(h) for h in d[role]])
        assert all(np.array_equal(a, b) for a, b in zip(self.ink, INK))


def box_triples(pal):
    """(light, body, dark) triples for archive boxes and folders: coral files, linen, sea blue, cherry."""
    return [(pal.accent[3], pal.accent[2], pal.accent[1]),
            (pal.wall[3], pal.wall[2], pal.wall[1]),
            (pal.floor[3], pal.floor[2], pal.floor[1]),
            (pal.wood[3], pal.wood[2], pal.wood[1])]


# ------------------------------------------------------------------ shelving

SHELF_H = 28  # sprite body height; the footprint is the bottom 16 px


def shelf(r, x0, y0, cells, pal, seed, triples=None):
    """Archive shelving seen from the high overhead camera: a top plane, a front face with three
    bays, uprights, boards and a kick plate. File boxes sit in runs of one or two colours, so they
    read as clusters. cells = 1 or 2 (16 or 32 px wide). Body y0..y0+27; contact shadow below."""
    triples = triples or box_triples(pal)
    G, wall = pal.glass, pal.wall
    w, h = 16 * cells, SHELF_H
    r.cast(x0, x0 + w, y0 + h)
    body = r.mask(x0, y0, x0 + w, y0 + h)
    r.img[body] = G[1]
    # top plane: lit edge, mid, front lip
    r.rect(x0, y0 + 1, x0 + w, y0 + 2, G[3])
    r.rect(x0, y0 + 2, x0 + w, y0 + 5, G[2])
    r.rect(x0, y0 + 5, x0 + w, y0 + 6, G[1])
    # uprights (lit left edge) and, for two cells, the middle one
    ups = [x0 + 1, x0 + w - 3] + ([x0 + w // 2 - 1] if cells == 2 else [])
    for ux in ups:
        r.rect(ux, y0 + 6, ux + 2, y0 + h - 3, G[1])
        r.rect(ux, y0 + 6, ux + 1, y0 + h - 3, G[2])
    segs = [(x0 + 3, x0 + w - 3)] if cells == 1 else [(x0 + 3, x0 + w // 2 - 1), (x0 + w // 2 + 1, x0 + w - 3)]
    rnd = random.Random(seed)
    for lv in range(3):
        cy0 = y0 + 7 + 6 * lv  # cavity rows cy0 .. cy0+4, board row cy0+5
        for sx0, sx1 in segs:
            r.rect(sx0, cy0, sx1, cy0 + 5, G[0])
            x = sx0 + rnd.randrange(0, 2)
            while x + 3 <= sx1:
                if rnd.random() < 0.07:  # an empty stretch
                    x += rnd.randrange(3, 5)
                    continue
                light, body_c, dark = triples[rnd.randrange(len(triples))]
                hb = rnd.choice((4, 5))
                for _ in range(rnd.randrange(2, 5)):
                    wb = rnd.choice((3, 4))
                    if x + wb > sx1:
                        break
                    top = cy0 + 5 - hb
                    r.rect(x, top, x + wb, cy0 + 5, body_c)
                    r.rect(x, top, x + wb, top + 1, light)
                    r.rect(x + wb - 1, top + 1, x + wb, cy0 + 5, dark)
                    if wb == 4 and hb >= 4:
                        r.rect(x + 1, top + 2, x + 3, top + 3, wall[3])  # linen label
                    x += wb
                x += rnd.randrange(1, 3)
        r.rect(x0 + 3, cy0 + 5, x0 + w - 3, cy0 + 6, G[2])  # board, lit front edge
    r.rect(x0 + 1, y0 + h - 3, x0 + w - 1, y0 + h, G[0])   # kick plate
    r.rect(x0 + 1, y0 + h - 3, x0 + w - 1, y0 + h - 2, G[1])
    r.outline(body)


# ------------------------------------------------------------------ glass partition

PART_H = 26


def partition(r, x0, y0, cells, pal):
    """Free-standing glass partition: dark frame with a lit cap, cooler pane with one stepped
    reflection band, a floor rail. cells = 1 or 2. Body y0..y0+25; contact shadow below."""
    G = pal.glass
    w, h = 16 * cells, PART_H
    r.cast(x0, x0 + w, y0 + h)
    body = r.mask(x0, y0, x0 + w, y0 + h)
    r.img[body] = G[1]
    r.rect(x0, y0 + 1, x0 + w, y0 + 2, G[3])    # lit cap
    r.rect(x0, y0 + 2, x0 + w, y0 + 4, G[2])
    panes = [(x0 + 2, x0 + w - 2)] if cells == 1 else [(x0 + 2, x0 + w // 2 - 1), (x0 + w // 2 + 1, x0 + w - 2)]
    for i, (px0, px1) in enumerate(panes):
        pane = r.mask(px0, y0 + 5, px1, y0 + 22)
        r.img[pane] = G[2]
        r.img[pane & (r.y >= y0 + 17)] = G[1]   # floor seen through the lower pane
        band = pane & (np.abs((r.x - px0) - (r.y - y0 - 5) * 0.8 - (4 + 3 * i)) < 1.6)
        r.img[band] = G[3]
        r.rect(px0, y0 + 5, px1, y0 + 6, G[0])  # shadow under the cap
    if cells == 2:
        mid = x0 + w // 2 - 1
        r.rect(mid, y0 + 4, mid + 2, y0 + 22, G[1])
        r.rect(mid, y0 + 4, mid + 1, y0 + 22, G[2])
    r.rect(x0 + 1, y0 + 4, x0 + 2, y0 + 22, G[2])   # lit left post
    r.rect(x0, y0 + 22, x0 + w, y0 + 25, G[1])      # rail
    r.rect(x0, y0 + 22, x0 + w, y0 + 23, G[2])
    r.rect(x0, y0 + 24, x0 + w, y0 + 25, G[0])
    r.outline(body)


# ------------------------------------------------------------------ terminal desk

def terminal_desk(r, x0, y0, pal):
    """Two-cell console desk. The terminal housing is drawn first (ink), then the screen in the
    glass / device ramp: one body step and one lit step, and one hard glow step on the desk top.
    Body y0..y0+15, housing rises 7 px above it."""
    G, wall = pal.glass, pal.wall
    env.block(r, x0, y0, x0 + 34, y0 + 16, 5, wall, G)
    # glow on the desk top below the screen: one hard step in the device ramp
    r.rect(x0 + 5, y0 + 7, x0 + 21, y0 + 9, G[3])
    # housing first, then bezel, then the lit face
    r.rect(x0 + 4, y0 - 7, x0 + 22, y0 + 7, INK[0])
    r.rect(x0 + 5, y0 - 6, x0 + 21, y0 + 6, INK[1])
    scr = r.mask(x0 + 6, y0 - 5, x0 + 20, y0 + 4)
    r.img[scr] = G[2]
    r.rect(x0 + 6, y0 - 5, x0 + 20, y0 - 4, G[3])
    for (lx, ly, lw) in ((7, -3, 7), (7, -1, 4), (7, 1, 9)):  # text clusters
        r.rect(x0 + lx, y0 + ly, x0 + lx + lw, y0 + ly + 1, G[3])
    r.rect(x0 + 15, y0 - 3, x0 + 19, y0 - 2, G[1])
    r.outline(scr, G[0])
    # keyboard
    r.rect(x0 + 7, y0 + 9, x0 + 19, y0 + 11, INK[2])
    for kx in range(8, 19, 2):
        r.img[y0 + 9, x0 + kx] = INK[3]
    # card reader at the right end
    r.rect(x0 + 25, y0 + 3, x0 + 31, y0 + 8, INK[1])
    r.rect(x0 + 26, y0 + 4, x0 + 30, y0 + 5, G[3])
    r.outline(r.mask(x0 + 25, y0 + 3, x0 + 31, y0 + 8))


# ------------------------------------------------------------------ cabinet

CAB_H = 26


def cabinet(r, x0, y0, cells, pal):
    """Filing cabinet: top plane with a paper stack, three drawers with label plates and pulls.
    Body y0..y0+25."""
    W, wd = pal.wall, pal.wood
    w, h = 16 * cells, CAB_H
    env.block(r, x0, y0, x0 + w, y0 + h, 19, wd, wd)
    # paper stack on the top plane
    r.rect(x0 + 2, y0 + 2, x0 + 9, y0 + 5, W[3])
    r.rect(x0 + 2, y0 + 4, x0 + 9, y0 + 5, W[1])
    r.outline(r.mask(x0 + 2, y0 + 2, x0 + 9, y0 + 5), W[1])
    fy = y0 + h - 19
    for d in range(3):
        dy = fy + 1 + d * 6
        for c in range(cells):
            dx = x0 + c * 16
            r.rect(dx + 2, dy + 1, dx + 14, dy + 5, wd[1])
            r.rect(dx + 2, dy + 1, dx + 14, dy + 2, wd[2])             # lit drawer lip
            r.rect(dx + 2, dy + 5, dx + 14, dy + 6, wd[0])             # seam
            r.rect(dx + 5, dy + 2, dx + 11, dy + 4, W[3])              # label plate
            r.rect(dx + 7, dy + 3, dx + 9, dy + 4, INK[1])             # inked label
            r.rect(dx + 6, dy + 4, dx + 10, dy + 5, W[1])              # pull


# ------------------------------------------------------------------ light shaft

def light_shaft(r, x0, y0, lit):
    """Two parallelogram bands of daylight falling from a window pair to the lower right: 28 px
    wide, 36 px long, one hard step. Drawn in `lit`, composited only over the bare floor fill."""
    for pane in range(2):
        for dy in range(36):
            sx = x0 + pane * 15 + int(dy * 0.7)
            r.rect(sx, y0 + dy, sx + 11, y0 + dy + 1, lit)
