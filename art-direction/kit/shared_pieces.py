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


# ================================================================== quest-prop builders (wave 2 shared)
# Everything below is additive: the pieces above are untouched, so every kit that already uses them
# keeps byte-identical output. Each builder takes a `Pal`, paints palette constants only, and is
# captured into atlas sprites by kitlib.capture (see orientation_kit.py and orientation_quest.py).

GLYPHS5 = {  # 3x5 lettering for mats and plaques (env.GLYPHS has R E C O D S; these add the rest)
    "L": ["#..", "#..", "#..", "#..", "###"], "I": ["###", ".#.", ".#.", ".#.", "###"],
    "F": ["###", "#..", "##.", "#..", "#.."], "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "M": ["#.#", "###", "###", "#.#", "#.#"], "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "N": ["##.", "#.#", "#.#", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"], "P": ["##.", "#.#", "##.", "#..", "#.."],
}
GLYPHS5.update(env.GLYPHS)


def px(r, x, y, c):
    r.img[y, x] = c


def line(r, x0, y0, x1, y1, c):
    """Hard 1 px Bresenham line."""
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        r.img[y0, x0] = c
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def text5(r, x, y, word, c, gap=1):
    for ch in word:
        for dy, row in enumerate(GLYPHS5[ch]):
            for dx, bit in enumerate(row):
                if bit == "#":
                    r.img[y + dy, x + dx] = c
        x += 3 + gap
    return x


def text_width(word, gap=1):
    return len(word) * (3 + gap) - gap


def coral_of(pal):
    """Coral people / upholstery ramp. Orientation has one; other districts reuse their accent."""
    if pal.name == "orientation":
        return [bst.hx(h) for h in dp.ORIENTATION_EXTRA["coral"]]
    return pal.accent


# ------------------------------------------------------------------ wall module (north wall slice)

WALL_H = 34


def wall_slice(r, x0, y0, w, pal):
    """The north wall's 34 px column, as env.north_wall draws it: cap with lit trim, stone face,
    baseboard and the cast shadow on the floor. w px wide."""
    G, Wl = pal.glass, pal.wall
    r.rect(x0, y0, x0 + w, y0 + 6, INK[1])
    r.rect(x0, y0, x0 + w, y0 + 1, INK[2])
    r.rect(x0, y0 + 4, x0 + w, y0 + 5, G[2])
    r.rect(x0, y0 + 5, x0 + w, y0 + 6, INK[0])
    r.rect(x0, y0 + 6, x0 + w, y0 + 31, Wl[1])
    r.rect(x0, y0 + 6, x0 + w, y0 + 7, Wl[2])
    r.rect(x0, y0 + 30, x0 + w, y0 + 32, INK[0])
    r.rect(x0, y0 + 32, x0 + w, y0 + 33, INK[2])
    r.rect(x0, y0 + 33, x0 + w, y0 + 34, INK[3])


def sconce(r, cx, cy, pal):
    """Small wall lamp: brass head with one lit step and a contour (door lamps)."""
    A = pal.accent
    head = r.mask(cx - 2, cy - 3, cx + 3, cy + 2)
    r.img[head] = A[2]
    r.rect(cx - 1, cy - 2, cx + 2, cy + 1, A[3])
    r.outline(head)


def lit_mat(r, x0, y0, w, h, pal, word=None, chevrons=True):
    """Lit floor mat: the brightest tone of the accent ramp, a mid-tone edge, lettering in the
    darkest step (the Records mat's recipe)."""
    A = pal.accent
    m = r.mask(x0, y0, x0 + w, y0 + h)
    r.img[m] = A[3]
    r.img[r.edge(m)] = A[2]
    if word:
        tw = text_width(word)
        ty = y0 + (h - 5) // 2
        text5(r, x0 + (w - tw) // 2, ty, word, A[0])
        if chevrons:
            for side in (x0 + 5, x0 + w - 10):
                for i in range(3):  # up chevron, 5 px wide
                    r.rect(side + i, ty + 2 - i, side + i + 1, ty + 3 - i, A[0])
                    r.rect(side + 4 - i, ty + 2 - i, side + 5 - i, ty + 3 - i, A[0])


# ------------------------------------------------------------------ elevator

EL_TRAVEL = 11   # leaf travel (px) at "open"; 1 px of leaf stays visible in each pocket
EL_BOX = 48      # the module is 3 cells x 3 cells: wall (rows 0-1) and the lit mat (row 2)


def elevator_doors(r, x0, y0, pal, t=0.0, mat=True):
    """Elevator door set, 48 x 48 px with its top-left at (x0, y0): north-wall slice, brass casing with
    two lamps, a floor-indicator housing, two steel leaves that slide into pockets behind the jambs
    (t = 0 closed, 0.5 half, 1 open) and a lit floor mat below the wall. Doors read as doors:
    frame, lamps, an opening you can see through, a lit mat with lettering."""
    G, Wl, A = pal.glass, pal.wall, pal.accent
    wall_slice(r, x0, y0, 48, pal)
    # casing (jambs and lintel), then the opening
    ox0, ox1, oy0, oy1 = x0 + 12, x0 + 36, y0 + 14, y0 + 30
    r.rect(x0 + 7, y0 + 11, x0 + 41, y0 + 12, INK[0])
    cas = r.mask(x0 + 8, y0 + 12, x0 + 40, y0 + 32)
    r.img[cas] = A[1]
    r.rect(x0 + 8, y0 + 12, x0 + 40, y0 + 13, A[3])     # lit lintel
    r.rect(x0 + 8, y0 + 13, x0 + 40, y0 + 14, A[2])
    r.rect(x0 + 8, y0 + 14, x0 + 9, y0 + 30, A[3])      # lit left jamb face
    r.rect(x0 + 9, y0 + 14, x0 + 12, y0 + 30, A[1])
    r.rect(x0 + 36, y0 + 14, x0 + 39, y0 + 30, A[1])
    r.rect(x0 + 39, y0 + 14, x0 + 40, y0 + 30, A[0])    # shaded right edge
    r.rect(x0 + 8, y0 + 30, x0 + 40, y0 + 31, A[3])     # sill, lit edge
    r.rect(x0 + 8, y0 + 31, x0 + 40, y0 + 32, A[2])
    r.rect(x0 + 7, y0 + 12, x0 + 8, y0 + 32, INK[0])
    r.rect(x0 + 40, y0 + 12, x0 + 41, y0 + 32, INK[0])
    # cab seen through the opening: warm stone back wall, handrail, lit floor, shadow under the lintel
    cab = r.mask(ox0, oy0, ox1, oy1)
    r.img[cab] = Wl[2]
    r.rect(ox0, oy0 + 2, ox1, oy0 + 7, Wl[3])
    r.rect(ox0, oy0 + 8, ox1, oy0 + 9, A[2])            # handrail
    r.rect(ox0, oy0 + 9, ox1, oy0 + 10, A[0])
    r.rect(ox0, oy1 - 3, ox1, oy1, Wl[3])               # cab floor, lit
    r.rect(ox0 + 11, oy0 + 2, ox0 + 13, oy1 - 3, Wl[1])  # panel joint
    r.rect(ox0, oy0, ox1, oy0 + 2, INK[0])              # shadow under the lintel
    r.rect(ox0, oy0 + 2, ox1, oy0 + 3, INK[2])
    # leaves
    tr = int(round(EL_TRAVEL * max(0.0, min(1.0, t))))
    for k, lx in enumerate((ox0 - tr, ox0 + 12 + tr)):
        a0, a1 = max(lx, ox0), min(lx + 12, ox1)
        if a0 >= a1:
            continue
        leaf = r.mask(a0, oy0, a1, oy1)
        r.img[leaf] = G[2]
        r.rect(a0, oy0, a1, oy0 + 2, G[3])                                   # lit top
        r.rect(a0, oy1 - 4, a1, oy1, G[1])                                   # kick plate
        r.rect(a0, oy1 - 4, a1, oy1 - 3, G[0])
        if lx >= a0:
            r.rect(lx, oy0, lx + 1, oy1, G[3] if k == 0 else INK[0])         # leaf edge facing out / seam
        if lx + 12 <= a1:
            r.rect(lx + 11, oy0, lx + 12, oy1, INK[0] if k == 0 else G[1])
        band = leaf & (np.abs((r.x - lx) - (r.y - oy0) * 0.7 - 2.5) < 0.9) & (r.y > oy0 + 2) & (r.y < oy1 - 4)
        r.img[band] = G[3]
    # floor-indicator housing above the casing: lit arrow and a floor number
    r.rect(x0 + 16, y0 + 7, x0 + 32, y0 + 11, INK[0])
    r.rect(x0 + 17, y0 + 8, x0 + 31, y0 + 10, INK[1])
    r.rect(x0 + 17, y0 + 9, x0 + 20, y0 + 10, G[3])      # arrow: head and tip
    r.rect(x0 + 18, y0 + 8, x0 + 19, y0 + 9, G[3])
    r.rect(x0 + 24, y0 + 8, x0 + 27, y0 + 9, G[3])       # floor label, two lit rows
    r.rect(x0 + 24, y0 + 9, x0 + 27, y0 + 10, G[2])
    # lamps flank the casing
    sconce(r, x0 + 3, y0 + 18, pal)
    sconce(r, x0 + 44, y0 + 18, pal)
    if mat:
        lit_mat(r, x0 + 4, y0 + 36, 40, 11, pal, "LIFT")


def elevator_call_panel(r, x0, y0, pal):
    """Wall call panel, 12 x 22 px: housing, a small lit display, up and down buttons with arrows."""
    G, A = pal.glass, pal.accent
    body = r.mask(x0, y0, x0 + 12, y0 + 22)
    r.img[body] = G[2]
    r.rect(x0, y0, x0 + 12, y0 + 1, G[3])
    r.rect(x0, y0, x0 + 1, y0 + 22, G[3])
    r.rect(x0 + 11, y0 + 1, x0 + 12, y0 + 22, G[1])
    r.rect(x0 + 1, y0 + 21, x0 + 12, y0 + 22, G[1])
    r.outline(body)
    scr = r.mask(x0 + 2, y0 + 2, x0 + 10, y0 + 6)
    r.img[scr] = INK[1]
    r.rect(x0 + 3, y0 + 3, x0 + 5, y0 + 4, G[3])
    r.rect(x0 + 6, y0 + 4, x0 + 9, y0 + 5, G[3])
    r.outline(scr, INK[0])
    for by, up in ((8, True), (15, False)):
        btn = r.disc(x0 + 6, y0 + by + 2.5, 3.2)
        r.img[btn] = A[2]
        r.img[btn & (r.x < x0 + 5.5) & (r.y < y0 + by + 2.5)] = A[3]
        r.img[r.edge(btn)] = INK[0]
        if up:
            r.rect(x0 + 6, y0 + by + 1, x0 + 7, y0 + by + 2, INK[0])
            r.rect(x0 + 5, y0 + by + 2, x0 + 8, y0 + by + 3, INK[0])
        else:
            r.rect(x0 + 5, y0 + by + 2, x0 + 8, y0 + by + 3, INK[0])
            r.rect(x0 + 6, y0 + by + 3, x0 + 7, y0 + by + 4, INK[0])


# ------------------------------------------------------------------ desk (palette-driven) and its front occluder

DESK_W, DESK_H = 34, 16
FRONT_TOP, FRONT_BOT = -5, 8   # occluder rows relative to the desk's top edge: monitor top .. 8 px of top plane


def desk_a(r, x0, y0, pal, seed):
    """env.desk without the chair, driven by a Pal. With the Orientation palette it is pixel-identical to
    env.desk (the build asserts it)."""
    G, wall, wd, gr = pal.glass, pal.wall, pal.wood, pal.foliage
    env.block(r, x0, y0, x0 + DESK_W, y0 + DESK_H, 5, wd, wd)
    r.rect(x0 + 9, y0 - 5, x0 + 23, y0 + 6, INK[0])
    r.rect(x0 + 10, y0 - 4, x0 + 22, y0 + 4, G[1])
    r.rect(x0 + 10, y0 - 4, x0 + 22, y0 - 2, G[2])
    r.rect(x0 + 11, y0 - 3, x0 + 14, y0 - 2, G[3])
    r.rect(x0 + 15, y0 + 6, x0 + 17, y0 + 8, INK[1])
    r.rect(x0 + 10, y0 + 8, x0 + 21, y0 + 10, INK[2])
    r.rect(x0 + 25, y0 + 3, x0 + 31, y0 + 8, wall[3])
    r.outline(r.mask(x0 + 25, y0 + 3, x0 + 31, y0 + 8), wall[1])
    env.leaves(r, x0 + 4, y0 + 2, 3.6, seed, ramp=gr, count=4, spread=3)


def desk_front(r, x0, y0, pal, seed):
    """Desk-front occluder (layer front_prop): the desk's own pixels from FRONT_TOP to FRONT_BOT rows around
    its top edge (monitor housing plus 8 px of top plane), cut from desk_a so it is seamless over the desk.
    Drawn after actors it hides a seated worker's lower body. Contact shadow excluded."""
    keep = np.zeros((env.H, env.W), bool)
    keep[max(0, y0 + FRONT_TOP):y0 + FRONT_BOT, x0:x0 + DESK_W + 1] = True
    got = []
    for bg in ((7, 11, 13), (243, 241, 239)):
        t = env.Room()
        t.cast = lambda *a, **k: None
        t.img[:] = bg
        desk_a(t, x0, y0, pal, seed)
        got.append((t.img.copy(), np.any(t.img != np.array(bg, np.uint8), axis=2)))
    m = (got[0][1] | got[1][1]) & keep
    r.img[m] = got[0][0][m]


# ------------------------------------------------------------------ artifacts (16 x 16, inspectable)

ARTIFACT_KINDS = ("unissued_badge", "training_card", "mirror_card", "first_route_receipt", "carbon_copy_a",
                  "margin_stamp", "uncut_index", "noors_annotation", "id_envelope", "alarm_strip", "scoring_proof",
                  "original_routing_diagram", "adas_shift_book", "public_audit_copy")


def _paper(r, x0, y0, x1, y1, pal, tone=3):
    m = r.mask(x0, y0, x1, y1)
    r.img[m] = pal.wall[tone]
    r.outline(m)
    return m


def _lines(r, x, y, widths, c, gap=2):
    for i, w in enumerate(widths):
        r.rect(x, y + i * gap, x + w, y + i * gap + 1, c)


def artifact_cue(r, x0, y0, pal):
    """The faint inspectable cue shared by every artifact: a small pale-glass glint at the upper left
    (glass step 3, never a UI marker colour)."""
    G = pal.glass
    px(r, x0 + 1, y0 + 2, G[3])
    px(r, x0 + 2, y0 + 1, G[3])
    px(r, x0 + 2, y0 + 3, G[3])
    px(r, x0 + 3, y0 + 2, G[3])


def artifact_prop(r, x0, y0, pal, kind):
    """One optional artifact in a 16 x 16 cell with its top-left at (x0, y0). `kind` is one of
    ARTIFACT_KINDS. Item body is roughly 11 x 11 px, outlined in the contour ink, over a baked contact
    shadow; every artifact carries the same glint cue. Palette roles: paper = wall step 3, ink = ink ramp,
    accent = the district's trim, wood and glass for card bands and folds."""
    G, wd, A, ink = pal.glass, pal.wood, pal.accent, INK
    cor = coral_of(pal)
    bx, by = x0 + 3, y0 + 3     # body origin
    if kind == "unissued_badge":
        r.cast(bx + 1, bx + 10, by + 11, rows=1)
        r.rect(bx + 3, by - 2, bx + 6, by + 1, ink[2])               # lanyard clip
        r.rect(bx + 4, by - 2, bx + 5, by + 1, ink[3])
        _paper(r, bx, by, bx + 10, by + 11, pal)
        r.rect(bx + 1, by + 1, bx + 9, by + 3, wd[1])                  # old department band, a warm colour
        r.rect(bx + 1, by + 4, bx + 5, by + 8, ink[2])                  # photo block
        r.rect(bx + 2, by + 5, bx + 4, by + 7, ink[3])
        _lines(r, bx + 6, by + 4, (3, 3), ink[1])
        r.rect(bx + 1, by + 9, bx + 9, by + 10, A[2])                   # blank name bar
    elif kind == "training_card":
        r.cast(bx + 1, bx + 10, by + 11, rows=1)
        _paper(r, bx, by, bx + 10, by + 11, pal)
        r.rect(bx + 1, by + 1, bx + 9, by + 3, G[2])
        r.rect(bx + 1, by + 1, bx + 9, by + 2, G[3])
        for i in range(3):                                              # three short steps
            r.rect(bx + 1, by + 4 + i * 2, bx + 2, by + 5 + i * 2, A[1])
            r.rect(bx + 3, by + 4 + i * 2, bx + 6 + (i % 2) * 2, by + 5 + i * 2, ink[1])
        r.rect(bx + 6, by + 9, bx + 9, by + 10, wd[2])                  # worn corner
    elif kind == "mirror_card":
        r.cast(bx + 1, bx + 10, by + 11, rows=1)
        _paper(r, bx, by, bx + 10, by + 11, pal)
        r.rect(bx + 1, by + 1, bx + 9, by + 3, wd[2])
        for i, row in enumerate(GLYPHS5["R"]):                          # a reversed R, printed backwards
            for j, bit in enumerate(row):
                if bit == "#":
                    px(r, bx + 5 - j, by + 4 + i, ink[1])
        line(r, bx + 5, by + 8, bx + 8, by + 8, cor[1])                 # handwritten arrow, right-hand route
        px(r, bx + 7, by + 7, cor[1])
        px(r, bx + 7, by + 9, cor[1])
        _lines(r, bx + 1, by + 9, (4,), ink[3])
    elif kind == "first_route_receipt":
        r.cast(bx + 2, bx + 9, by + 12, rows=1)
        m = r.mask(bx + 1, by - 1, bx + 9, by + 12)
        r.img[m] = pal.wall[3]
        r.outline(m)
        for k in range(4):                                              # torn zigzag top edge
            px(r, bx + 1 + k * 2, by - 1, pal.wall[2])
        line(r, bx + 3, by + 2, bx + 6, by + 4, ink[1])                  # the detour: out, around, back
        line(r, bx + 6, by + 4, bx + 3, by + 6, ink[1])
        line(r, bx + 3, by + 6, bx + 7, by + 8, ink[1])
        r.rect(bx + 6, by + 9, bx + 8, by + 10, G[2])                    # approved tick
        px(r, bx + 7, by + 10, G[2])
    elif kind == "carbon_copy_a":
        r.cast(bx + 1, bx + 11, by + 12, rows=1)
        _paper(r, bx + 1, by + 1, bx + 11, by + 12, pal, 2)               # carbon sheet behind
        _paper(r, bx, by, bx + 10, by + 11, pal)
        r.rect(bx + 1, by + 1, bx + 5, by + 3, cor[1])
        _lines(r, bx + 1, by + 4, (8, 6, 8, 4), ink[3])
    elif kind == "margin_stamp":
        r.cast(bx + 1, bx + 10, by + 11, rows=1)
        _paper(r, bx, by, bx + 10, by + 11, pal)
        _lines(r, bx + 1, by + 1, (7, 8), ink[3])
        st = r.disc(bx + 6.5, by + 7.5, 3.3)
        r.img[r.edge(st)] = cor[1]
        r.rect(bx + 5, by + 6, bx + 9, by + 7, cor[2])
        r.rect(bx + 4, by + 8, bx + 8, by + 9, cor[2])
    elif kind == "uncut_index":
        r.cast(bx + 1, bx + 10, by + 11, rows=1)
        _paper(r, bx, by, bx + 10, by + 11, pal)
        for i in range(4):
            r.rect(bx, by + 1 + i * 3, bx + 3, by + 3 + i * 3, A[1 + (i % 2)])   # tabs on the long edge
            r.rect(bx + 4, by + 2 + i * 3, bx + 9, by + 3 + i * 3, ink[3])
        r.rect(bx + 7, by + 8, bx + 10, by + 9, wd[2])
    elif kind == "noors_annotation":
        r.cast(bx + 1, bx + 11, by + 9, rows=1)
        _paper(r, bx + 1, by + 1, bx + 11, by + 9, pal, 2)
        _paper(r, bx, by, bx + 8, by + 8, pal)
        _lines(r, bx + 1, by + 1, (5, 4, 5), ink[3])
        line(r, bx + 1, by + 7, bx + 6, by + 7, cor[1])                   # dry underline
        r.rect(bx + 6, by + 3, bx + 10, by + 4, cor[1])                   # margin note
    elif kind == "id_envelope":
        r.cast(bx, bx + 11, by + 10, rows=1)
        env_m = r.mask(bx, by + 1, bx + 11, by + 10)
        r.img[env_m] = A[3]
        r.outline(env_m)
        line(r, bx + 1, by + 2, bx + 5, by + 5, A[1])                     # flap
        line(r, bx + 9, by + 2, bx + 5, by + 5, A[1])
        r.rect(bx + 2, by + 7, bx + 6, by + 8, ink[2])                    # address block
        r.rect(bx + 7, by + 7, bx + 9, by + 9, ink[1])                    # stamp for a vanished department
    elif kind == "alarm_strip":
        r.cast(bx, bx + 12, by + 8, rows=1)
        strip = r.mask(bx, by + 1, bx + 12, by + 8)
        r.img[strip] = pal.wall[3]
        r.outline(strip)
        for i, c in enumerate((G[2], A[2], G[1], wd[2], G[3], A[1])):     # six alert pictograms
            r.rect(bx + 1 + i * 2, by + 2, bx + 2 + i * 2, by + 5, c)
        r.rect(bx + 1, by + 6, bx + 11, by + 7, ink[3])
        r.rect(bx + 9, by + 6, bx + 11, by + 7, cor[1])                   # the extra department
    elif kind == "scoring_proof":
        r.cast(bx + 1, bx + 10, by + 11, rows=1)
        _paper(r, bx, by, bx + 10, by + 11, pal)
        for i, h in enumerate((2, 4, 7)):                                 # rising bars: longer route, higher score
            r.rect(bx + 1 + i * 3, by + 9 - h, bx + 3 + i * 3, by + 9, (G[2], G[1], A[2])[i])
        r.rect(bx + 1, by + 9, bx + 9, by + 10, ink[2])
        r.rect(bx + 1, by + 1, bx + 5, by + 2, ink[3])
    elif kind == "original_routing_diagram":
        r.cast(bx + 1, bx + 10, by + 11, rows=1)
        _paper(r, bx, by, bx + 10, by + 11, pal)
        for (ax, ay, bxx, byy) in ((2, 3, 5, 3), (5, 3, 5, 7), (5, 7, 8, 7)):
            line(r, bx + ax, by + ay, bx + bxx, by + byy, ink[2])
        for (nx, ny) in ((2, 3), (5, 7), (8, 7)):
            r.rect(bx + nx - 1, by + ny - 1, bx + nx + 1, by + ny + 1, A[2])
        for i, c in enumerate((cor[1], G[1], A[1])):                      # signatures along the bottom
            r.rect(bx + 1 + i * 3, by + 9, bx + 3 + i * 3, by + 10, c)
    elif kind == "adas_shift_book":
        r.cast(bx, bx + 11, by + 11, rows=1)
        bk = r.mask(bx, by, bx + 11, by + 11)
        r.img[bk] = wd[1]
        r.rect(bx, by, bx + 11, by + 1, wd[2])
        r.rect(bx, by, bx + 1, by + 11, wd[2])
        r.rect(bx + 10, by + 1, bx + 11, by + 11, wd[0])
        r.outline(bk)
        r.rect(bx + 2, by + 2, bx + 9, by + 5, pal.wall[3])               # name label
        r.rect(bx + 3, by + 3, bx + 8, by + 4, ink[2])
        r.rect(bx + 2, by + 7, bx + 3, by + 11, A[1])                     # ribbon marker
    elif kind == "public_audit_copy":
        r.cast(bx + 1, bx + 11, by + 12, rows=1)
        _paper(r, bx + 1, by + 1, bx + 11, by + 12, pal, 2)
        _paper(r, bx, by, bx + 10, by + 11, pal)
        r.rect(bx + 1, by + 1, bx + 9, by + 3, A[2])
        _lines(r, bx + 1, by + 4, (8, 7, 8), ink[3])
        r.img[r.edge(r.disc(bx + 7.5, by + 8.5, 2.2))] = A[1]            # seal
    else:
        raise ValueError(kind)
    artifact_cue(r, x0, y0, pal)
