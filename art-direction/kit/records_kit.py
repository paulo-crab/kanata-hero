"""Records environment kit (task 7.1): atlas pieces, the circular archive desk landmark and the
reference room layout.

Three sources of art, all palette-only:
  1. Orientation pieces recoloured by an exact hex swap (floor, walls, windows, door, lamp, desk,
     chair, planters). The swap asserts that every pixel has a mapping.
  2. District-agnostic new pieces from shared_pieces.py (shelving, partition, terminal desk,
     cabinet, light shaft), drawn with the Records ramps.
  3. Records-only pieces: route arrows, the sliding file wall, and the landmark.
"""
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kitlib  # noqa: E402
import orientation_kit as ok  # noqa: E402
import shared_pieces as sp  # noqa: E402
import build_scale_test as bst  # noqa: E402
import district_palettes as dp  # noqa: E402
import environment as env  # noqa: E402

T = 16
KIT = "records"
PAL = sp.Pal("records")
R = dp.DISTRICTS["records"]
O = dp.DISTRICTS["orientation"]
INK, shifted = bst.INK, bst.shifted
FLOOR_FILL = R["floor"][3]   # the bare floor colour a light composite may recolour
LIGHT_FILL = R["wall"][3]    # linen: daylight and lamp light on the cool floor

ORIENT_ATLAS = os.path.join(HERE, "orientation-atlas.json")


# ------------------------------------------------------------------ 1. recoloured Orientation pieces

def _ramp_map(src, dst):
    return {s.upper(): d.upper() for s, d in zip(src, dst)}


STONE_S, GLASS_S, WOOD_S, GREEN_S, BRASS_S = (O["floor"], O["glass"], O["wood"], O["foliage"], O["accent"])
CORAL_S = dp.ORIENTATION_EXTRA["coral"]


def recolour(sprite, maps, regions=()):
    """Exact hex swap. maps: list of (src_ramp, dst_ramp); regions: [(row0, row1, maps)] override
    the default maps for those sprite rows. Ink is shared and left alone. Raises on an unmapped pixel."""
    out = sprite.copy()
    base = {}
    for s, d in maps:
        base.update(_ramp_map(s, d))
    ink = {h.upper() for h in dp.INK}
    for y in range(sprite.shape[0]):
        m = dict(base)
        for r0, r1, rm in regions:
            if r0 <= y < r1:
                m = {}
                for s, d in rm:
                    m.update(_ramp_map(s, d))
        for x in range(sprite.shape[1]):
            if sprite[y, x, 3] == 0:
                continue
            h = kitlib.hexs(sprite[y, x, :3])
            if h in ink:
                continue
            if h not in m:
                raise AssertionError(f"unmapped colour {h} at ({x},{y})")
            out[y, x, :3] = kitlib.hex2rgb(m[h])
    return out


def from_orientation(atlas, src, new, maps, regions=(), note="", tags=(), comp_color=None):
    e = atlas.entries[src]
    sprite = recolour(atlas.sprite(src), maps, regions)
    ox, oy = e["footprint"]["origin_px"]
    comp = dict(e.get("composite", {"mode": "over"}))
    if comp["mode"] == "where_color":
        comp["color"] = comp_color
    sh = e.get("contact_shadow")
    p = ok.Piece(new, sprite, (0, 0), (ox, oy), tuple(e["footprint"]["cells"]), list(e["collision"]), e["layer"],
                 e["kind"], y_sort=e.get("y_sort", False), composite=comp, shadow=sh, tags=list(tags) or list(e.get("tags", [])),
                 note=note or e.get("note", ""))
    return p


def recoloured_pieces(atlas):
    pieces = []
    floor_maps = [(STONE_S, R["floor"])]
    for nm, desc in (("floor_j", "slab corner: joint on the top row and the left column"),
                     ("floor_h", "slab edge: joint on the top row"), ("floor_v", "slab edge: joint on the left column"),
                     ("floor_p", "slab interior, plain")):
        pieces.append(from_orientation(atlas, nm, nm, floor_maps, note=f"Records floor, {desc}. Pale sea blue, broad slabs, no grain",
                                       tags=["floor", "slab"]))
    pieces.append(from_orientation(atlas, "floor_chip", "floor_chip", floor_maps,
                                   note="2x1 px wear mark on the floor layer; placed with a pixel offset"))
    pieces.append(from_orientation(atlas, "route_inlay", "route_inlay", [([STONE_S[2]], [R["floor"][1]])],
                                   note="1 px inlay line in the deep sea-blue floor step that guides the eye along the route; repeat every 16 px (horizontal). "
                                        "One step darker than Orientation's, because the Records floor is darker and cooler"))
    v = np.rot90(pieces[-1].sprite, 1).copy()
    pieces.append(ok.Piece("route_inlay_v", v, (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                           note="route_inlay turned 90 degrees: the same line for vertical corridor edges", tags=["floor", "route"]))
    wall_maps = [(STONE_S, R["wall"]), (GLASS_S, R["glass"])]
    pieces.append(from_orientation(atlas, "wall_n_plain", "wall_n_plain", wall_maps,
                                   note="north wall segment: ink cap with a lit trim, linen face, baseboard and cast shadow; tiles horizontally"))
    for nm in ("wall_n_window_a", "wall_n_window_b"):
        pieces.append(from_orientation(atlas, nm, nm, wall_maps,
                                       note="high window overlay for the north wall: dark frame, cool lower pane, one stepped reflection band, lit sill"))
    pieces.append(from_orientation(atlas, "wall_e_plain", "wall_e_plain", wall_maps,
                                   note="east wall segment, side plane; tiles vertically. Content starts 4 px into the first cell"))
    # Door: frame in cherry wood (decision 5 of PALETTES_SPEC), linen sign plate with a coral folder icon.
    sign_rows = [(0, 13, [(BRASS_S, R["wall"]), (CORAL_S, R["accent"]), (STONE_S, R["wall"]), (GLASS_S, R["glass"])])]
    door_maps = [(BRASS_S, R["wood"]), (STONE_S, R["wall"]), (GLASS_S, R["glass"]), (CORAL_S, R["accent"])]
    for st, note in (("closed", "both glass leaves shut: cherry frame, leaves, seam, pulls, linen RECORDS sign with a coral folder"),
                     ("half", "leaves slid 8 px into the jamb pockets: the corridor and a cabinet show through"),
                     ("open", "leaves fully in the pockets (15 px): the doorway is open and the threshold is lit")):
        pieces.append(from_orientation(atlas, f"records_door_{st}", f"archive_door_{st}", door_maps, regions=sign_rows,
                                       note=note, tags=["door", "sliding glass", st]))
    lamp_maps = [(BRASS_S, [R["wall"][0], R["wall"][1], R["wall"][2], R["wall"][3]])]
    pieces.append(from_orientation(atlas, "lamp", "lamp", lamp_maps, note="floor lamp: dark post, linen lamp head with one lit step, contact shadow"))
    pieces.append(from_orientation(atlas, "lamp_off", "lamp_off", lamp_maps, note="unlit lamp: head in the ink ramp, no glow"))
    pieces.append(from_orientation(atlas, "lamp_glow_on", "lamp_glow_on", lamp_maps, comp_color=FLOOR_FILL,
                                   note="glow, one hard linen step (radius 5.2). Paints only where the floor is the bare fill "
                                        f"{FLOOR_FILL}, so it never washes over joints, inlays, props or walls"))
    pieces.append(from_orientation(atlas, "lamp_glow_pulse", "lamp_glow_pulse", lamp_maps, comp_color=FLOOR_FILL,
                                   note="pulse frame of the glow, radius 6.4; alternate with lamp_glow_on at about 600 ms each"))
    desk_maps = [(WOOD_S, R["wood"]), (GLASS_S, R["glass"]), (STONE_S, R["wall"]), (GREEN_S, R["foliage"])]
    for nm in ("desk_a", "desk_b"):
        pieces.append(from_orientation(atlas, nm, nm, desk_maps,
                                       note="two-cell cherry desk with monitor, keyboard, paper and a small plant (a and b differ only in the plant leaves); the chair is a separate entry"))
    pieces.append(from_orientation(atlas, "chair", "chair", [(CORAL_S, R["glass"])],
                                   note="sea-blue task chair seen from above; place 11 px right and 18 px below a desk origin"))
    for nm in ("pot_plant_a", "pot_plant_b", "pot_plant_c", "pot_plant_d"):
        pieces.append(from_orientation(atlas, nm, nm, [(GREEN_S, R["foliage"])],
                                       note="slate planter with a dusty-sage plant; four leaf layouts (a to d)"))
    return pieces


# ------------------------------------------------------------------ 2. shared pieces, captured

def shared_pieces():
    out = []
    sx, sy = 64, 64
    note_shelf = "{n}-cell archive shelving: top plane, front face with three bays, boxes in colour clusters (coral, linen, sea blue, cherry), kick plate"
    out.append(ok.make("shelf_1x1", lambda r: sp.shelf(r, sx, sy, 1, PAL, 3), (sx, sy + sp.SHELF_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note=note_shelf.format(n=1), tags=["shelf", "archive"]))
    for nm, seed in (("shelf_2x1_a", 1), ("shelf_2x1_b", 2)):
        out.append(ok.make(nm, lambda r, seed=seed: sp.shelf(r, sx, sy, 2, PAL, seed), (sx, sy + sp.SHELF_H - 16), (2, 1), ["11"],
                           "rear_prop", "prop", y_sort=True, note=note_shelf.format(n=2) + "; a and b differ only in the box layout",
                           tags=["shelf", "archive"]))
    out.append(ok.make("partition_1x1", lambda r: sp.partition(r, sx, sy, 1, PAL), (sx, sy + sp.PART_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note="free-standing glass partition, one cell: dark frame with lit cap, cool pane, one reflection band, floor rail",
                       tags=["partition", "glass"]))
    out.append(ok.make("partition_2x1", lambda r: sp.partition(r, sx, sy, 2, PAL), (sx, sy + sp.PART_H - 16), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True, note="free-standing glass partition, two cells, with a middle post and a reflection band per pane",
                       tags=["partition", "glass"]))
    out.append(ok.make("terminal_desk", lambda r: sp.terminal_desk(r, sx, sy + 8, PAL), (sx, sy + 8), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True,
                       note="two-cell console desk: ink terminal housing first, then a screen with one body step and one lit step in the glass ramp, a one-step glow on the desk top, keyboard and card reader",
                       tags=["terminal", "desk", "interact"]))
    out.append(ok.make("cabinet_1x1", lambda r: sp.cabinet(r, sx, sy, 1, PAL), (sx, sy + sp.CAB_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note="cherry filing cabinet, one cell: paper stack on the top plane, three drawers with label plates",
                       tags=["cabinet", "archive"]))
    out.append(ok.make("cabinet_2x1", lambda r: sp.cabinet(r, sx, sy, 2, PAL), (sx, sy + sp.CAB_H - 16), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True, note="cherry filing cabinet, two cells wide", tags=["cabinet", "archive"]))
    # light shaft
    rgba, painted = ok.cap(lambda r: sp.light_shaft(r, sx, sy, bst.hx(LIGHT_FILL)))
    b = kitlib.bbox(painted)
    out.append(ok.Piece("light_shaft", kitlib.crop_rgba(rgba, b), (b[0], b[1]), (b[0], b[1]), (4, 3), ["0000"] * 3, "light", "light",
                        composite={"mode": "where_color", "color": FLOOR_FILL},
                        note="two bands of daylight falling from a window pair to the lower right, one hard linen step; "
                             "paints only on the bare floor fill, so shelves, desks and joints stay untouched. Place at the window's bottom-left",
                        tags=["light", "window", "daylight"]))
    return out


# ------------------------------------------------------------------ 3. Records-only pieces

def route_arrows():
    """Cherry wayfinding arrows inlaid in the floor (east and north)."""
    a = np.zeros((16, 16, 4), np.uint8)
    wood = R["wood"]

    def px(x, y, c):
        a[y, x, :3] = kitlib.hex2rgb(c)
        a[y, x, 3] = 255
    for x in range(3, 10):          # shaft
        px(x, 7, wood[1])
        px(x, 8, wood[1])
    for i in range(5):              # head, tip to the right
        for y in range(3 + i, 13 - i):
            px(10 + i, y, wood[1])
    for i in range(5):              # lit upper-left edge of the head
        px(10 + i, 3 + i, wood[2])
    for x in range(3, 10):
        px(x, 7, wood[2])
    east = ok.Piece("route_arrow_e", a, (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                    note="cherry wayfinding arrow inlaid in the floor, pointing east; Records signage uses the wood ramp, not brass",
                    tags=["wayfinding", "route"])
    north = ok.Piece("route_arrow_n", np.rot90(a, 1).copy(), (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                     note="the same arrow pointing north", tags=["wayfinding", "route"])
    return [east, north]


def file_wall():
    """Sliding file wall: two 2x1 shelf units on a floor rail. Closed they meet in the middle and block;
    open they have slid one cell outward and leave a two-cell corridor."""
    out = []
    sx, sy = 64, 64
    box = (sx, sy, sx + 96, sy + sp.SHELF_H + 2)
    fp = (sx, sy + sp.SHELF_H - 16)
    for st, (xa, xb), coll in (("closed", (16, 48), "011110"), ("open", (0, 64), "110011")):
        def draw(r, xa=xa, xb=xb):
            sp.shelf(r, sx + xa, sy, 2, PAL, 1)
            sp.shelf(r, sx + xb, sy, 2, PAL, 2)
        out.append(ok.make(f"file_wall_{st}", draw, fp, (6, 1), [coll], "rear_prop", "prop", box=box, shadow=False, y_sort=True,
                           note={"closed": "two shelf units meet in the middle (cells 1-4 block); the wall reads as one run of shelving",
                                 "open": "the units have slid one cell outward along the rail (cells 0-1 and 4-5 block); cells 2-3 are a two-cell corridor"}[st]
                                + ". Contact shadows are baked per unit",
                           tags=["file wall", "state", st]))

    def rail(r):
        for x in range(sx, sx + 96):
            r.img[sy + 22, x] = INK[1]
            r.img[sy + 23, x] = INK[2]
        r.rect(sx, sy + 20, sx + 2, sy + 25, INK[0])
        r.rect(sx + 94, sy + 20, sx + 96, sy + 25, INK[0])
    rgba, painted = ok.cap(rail)
    b = (sx, sy + 20, sx + 96, sy + 25)
    out.append(ok.Piece("file_wall_rail", kitlib.crop_rgba(rgba, b), (b[0], b[1]), (sx, sy + 12), (6, 1), ["000000"], "floor_marking", "tile",
                        note="floor rail the file wall slides on, with end stops. Place at the same cell as the file wall, 12 px below the sprite top; it shows in the open state",
                        tags=["file wall", "rail"]))
    return out


# ------------------------------------------------------------------ landmark: the circular archive desk

OX, OY = 80, 40          # capture position of the 128 x 96 box in the 320 x 192 room
BOX_W, BOX_H = 128, 96
FP = (24, 20)            # footprint origin inside the box: 5 x 4 cells (80 x 64 px)
FP_CELLS = (5, 4)


class Geo:
    """Masks of the desk in room coordinates: top plane ring, face, hole, with an opening to the south."""

    def __init__(self, r):
        self.r = r
        self.cx, self.cy = OX + 64, OY + 48
        cx, cy = self.cx, self.cy
        outer = r.disc(cx, cy, 40, 28)
        self.hole = r.disc(cx, cy, 22, 13)
        gap = (r.x > cx - 8) & (r.x < cx + 8) & (r.y > cy)
        self.top = outer & ~self.hole & ~gap
        face = np.zeros_like(self.top)
        for k in range(1, 9):
            face |= shifted(self.top, 0, -k)
        self.face = face & ~self.top
        self.desk = self.top | self.face
        self.front = self.desk & (r.y > cy)
        self.back = self.desk & ~self.front


class Paint:
    def __init__(self, r, keep=None):
        self.r = r
        self.keep = np.ones(r.img.shape[:2], bool) if keep is None else keep

    def __call__(self, mask, colour):
        self.r.img[mask & self.keep] = colour

    def rect(self, x0, y0, x1, y1, colour):
        self(self.r.mask(x0, y0, x1, y1), colour)


def draw_desk(r, side):
    """The ring desk: 'back' (north half, inner face, items' base, cast shadow) or 'front' (south arc)."""
    g = Geo(r)
    w = PAL.wood
    keep = g.back if side == "back" else g.front
    P = Paint(r, keep if side == "front" else None)
    # Cast shadow (back part only: it lies on the floor, under actors).
    if side == "back":
        s1 = shifted(g.desk, -1, -1) & ~g.desk
        s2 = shifted(g.desk, -2, -2) & ~g.desk & ~s1
        P(s1, INK[2])
        P(s2, INK[3])
        P = Paint(r, keep)
    top, face, desk = g.top, g.face, g.desk
    xi = r.x.astype(int)
    P(top, w[2])
    P(top & ~(shifted(top, 1, 1) & shifted(top, 2, 2)), w[1])
    P(top & ~(shifted(top, -1, -1) & shifted(top, -2, -2)), w[3])
    n = ((r.x - g.cx) / 31.0) ** 2 + ((r.y - g.cy) / 20.5) ** 2
    P(top & (n > 0.93) & (n < 1.07), w[3])           # inlaid line around the writing surface
    P(face, w[1])
    P(face & shifted(top, 0, -1), w[2])              # lit edge below the top plane
    P(face & ~g.hole & ((xi - g.cx) % 10 == 0) & ~shifted(top, 0, -1), w[0])  # panel joints
    P(face & ~shifted(face, 0, 1), w[0])             # dark base
    # drawer fronts: a linen label plate and a pull on each panel of the outer face
    outer_face = face & ~g.hole
    for px_ in range(g.cx - 40, g.cx + 40):
        if (px_ - g.cx) % 10 != 5:
            continue
        col = np.nonzero(outer_face[:, px_ - 1:px_ + 2].all(axis=1))[0]
        col = col[col > g.cy]
        if len(col) >= 6:
            y0 = int(col.min()) + 2
            P(r.mask(px_ - 1, y0, px_ + 2, y0 + 1), PAL.wall[3])
            P(r.mask(px_, y0 + 1, px_ + 1, y0 + 2), PAL.wall[1])
    P(r.edge(desk), INK[0])                          # contour
    return g


def draw_items(r):
    """Things on the desk top: ledger base is a separate part (it has quest marks)."""
    g = Geo(r)
    P = Paint(r, g.back)
    cx, cy = g.cx, g.cy
    G, W, w = PAL.glass, PAL.wall, PAL.wood
    # card-index drawer box: metal with two label plates
    x, y = cx + 12, cy - 21
    P(r.mask(x, y, x + 12, y + 6), G[2])
    P(r.mask(x, y, x + 12, y + 1), G[3])
    P(r.mask(x, y + 4, x + 12, y + 6), G[1])
    P(r.mask(x + 2, y + 2, x + 5, y + 3), W[3])
    P(r.mask(x + 7, y + 2, x + 10, y + 3), W[3])
    P(r.edge(r.mask(x, y, x + 12, y + 6)), INK[0])
    # small terminal on the east band: housing first, screen, a lit step
    x, y = cx + 24, cy - 9
    P(r.mask(x, y, x + 9, y + 8), INK[0])
    P(r.mask(x + 1, y + 1, x + 8, y + 7), INK[1])
    P(r.mask(x + 2, y + 2, x + 7, y + 6), G[2])
    P(r.mask(x + 2, y + 2, x + 7, y + 3), G[3])
    P(r.mask(x + 3, y + 4, x + 6, y + 5), G[3])
    # stamp and ink pad on the west band: Noor's cherry stamp standing on the pad
    x, y = cx - 36, cy - 10
    P(r.mask(x, y + 2, x + 9, y + 7), PAL.accent[1])
    P(r.mask(x, y + 2, x + 9, y + 3), PAL.accent[2])
    P(r.edge(r.mask(x, y + 2, x + 9, y + 7)), INK[0])
    P(r.mask(x + 3, y - 3, x + 5, y + 3), w[2])           # post
    P(r.mask(x + 2, y - 5, x + 6, y - 3), w[3])           # knob
    P(r.mask(x + 2, y - 3, x + 6, y - 2), w[1])
    P(r.edge(r.mask(x + 2, y - 5, x + 6, y - 3) | r.mask(x + 3, y - 3, x + 5, y + 3)), INK[0])


def draw_ledger(r, state):
    """Open ledger at the north-west of the ring. before: a rejected mark (coral cross) on the left
    page; after: an accepted mark (coral tick) on the right page and a stamped seal."""
    g = Geo(r)
    P = Paint(r, g.back)
    cx, cy = g.cx, g.cy
    W, w, A = PAL.wall, PAL.wood, PAL.accent
    x, y = cx - 14, cy - 24
    P(r.mask(x, y, x + 12, y + 7), w[0])            # cover
    P(r.mask(x + 1, y + 1, x + 6, y + 6), W[3])     # left page
    P(r.mask(x + 6, y + 1, x + 11, y + 6), W[3])    # right page
    P(r.mask(x + 5, y + 1, x + 6, y + 6), W[1])     # spine
    for lx, ly, lw in ((2, 2, 3), (7, 2, 3), (7, 4, 2)):
        P(r.mask(x + lx, y + ly, x + lx + lw, y + ly + 1), W[1])
    P(r.edge(r.mask(x, y, x + 12, y + 7)), INK[0])
    if state == "before":
        for i in range(3):                             # coral cross: rejected
            P(r.mask(x + 2 + i, y + 3 + i - 1, x + 3 + i, y + 4 + i - 1), A[2])
            P(r.mask(x + 4 - i, y + 3 + i - 1, x + 5 - i, y + 4 + i - 1), A[2])
    else:
        for (dx, dy) in ((7, 4), (8, 5), (9, 4), (10, 3), (10, 2)):   # tick: accepted
            P(r.mask(x + dx, y + dy, x + dx + 1, y + dy + 1), A[2])
        P(r.mask(x + 2, y + 4, x + 4, y + 6), A[1])                     # round seal, lit corner
        P(r.mask(x + 2, y + 4, x + 3, y + 5), A[3])


def draw_folders(r, state):
    """Two folder stacks on the ring. before: every label and folder the same dull linen (Pace's
    revision stripped the colour); after: coral and sea-blue variation with lit labels."""
    g = Geo(r)
    P = Paint(r, g.back)
    cx, cy = g.cx, g.cy
    W, A, F = PAL.wall, PAL.accent, PAL.floor
    stacks = [((cx - 27, cy - 15), [0, 1, 0]), ((cx + 1, cy - 25), [1, 0, 2])]
    after = {0: (A[3], A[2], A[1]), 1: (F[3], F[2], F[1]), 2: (W[3], W[2], W[1])}
    before = (W[2], W[1], W[0])
    for (x, y), cols in stacks:
        for i, c in enumerate(cols):
            fx, fy = x + (i % 2), y + 4 - 2 * i
            light, body, dark = (before if state == "before" else after[c])
            P(r.mask(fx, fy, fx + 8, fy + 3), body)
            P(r.mask(fx, fy, fx + 8, fy + 1), light)
            P(r.mask(fx, fy + 2, fx + 8, fy + 3), dark)
            lab = (W[1] if state == "before" else W[3])
            P(r.mask(fx + 5, fy, fx + 8, fy + 1), lab)         # label tab
            if state == "after":
                P(r.mask(fx + 6, fy, fx + 7, fy + 1), INK[1])
    # outline each stack's silhouette
    for (x, y), cols in stacks:
        m = np.zeros(r.img.shape[:2], bool)
        for i in range(len(cols)):
            fx, fy = x + (i % 2), y + 4 - 2 * i
            m |= r.mask(fx, fy, fx + 8, fy + 3)
        # draw the contour on the pixels just outside the stack
        ring = (shifted(m, 1, 0) | shifted(m, -1, 0) | shifted(m, 0, 1) | shifted(m, 0, -1)) & ~m
        P(ring, INK[0])


def draw_ring_inlay(r):
    g = Geo(r)
    P = Paint(r)
    cx, cy = g.cx, g.cy
    F = PAL.floor
    outer = r.disc(cx, cy, 58, 40)
    band = outer & ~r.disc(cx, cy, 52, 35.5)
    P(band, F[2])
    P(band & ~shifted(outer, 1, 0) | band & ~shifted(outer, 0, 1) | band & ~shifted(outer, -1, 0) | band & ~shifted(outer, 0, -1), F[1])
    thin = r.disc(cx, cy, 46, 31) & ~r.disc(cx, cy, 45, 30)
    P(thin, F[2])
    rug = r.disc(cx, cy + 2, 17, 8)                       # round mat inside the ring, where the clerk stands
    P(rug, PAL.wall[2])
    P(rug & ~shifted(rug, 1, 0) | rug & ~shifted(rug, -1, 0) | rug & ~shifted(rug, 0, 1) | rug & ~shifted(rug, 0, -1), PAL.wall[1])
    P(r.disc(cx, cy + 2, 11, 5) & ~r.disc(cx, cy + 2, 10, 4), PAL.wall[3])


def draw_ring_glow(r):
    """After: the luminous ring lights its pool on the floor, one hard linen step inside the inlay."""
    g = Geo(r)
    P = Paint(r)
    pool = r.disc(g.cx, g.cy, 51, 35.5) & ~r.disc(g.cx, g.cy, 41, 29.5)
    P(pool, bst.hx(LIGHT_FILL))


def landmark_pieces():
    parts = []
    box = (OX, OY, OX + BOX_W, OY + BOX_H)
    fp_room = (OX + FP[0], OY + FP[1])

    def mk(name, draw, layer, collision, y_sort, note, tags, composite=None, kind="landmark_part"):
        rgba, painted = ok.cap(draw)
        outside = painted.copy()
        outside[box[1]:box[3], box[0]:box[2]] = False
        assert not outside.any(), f"{name} leaves the landmark box"
        sprite = rgba[box[1]:box[3], box[0]:box[2]].copy()
        p = ok.Piece(name, sprite, (OX, OY), fp_room, FP_CELLS, collision, layer, kind, y_sort=y_sort,
                     composite=composite, tags=["landmark", "archive desk"] + tags, note=note)
        parts.append(p)
        return p

    # collision from the desk mask: a cell blocks when 25% of it is desk
    r0 = env.Room()
    g = Geo(r0)
    coll = []
    for cy_ in range(FP_CELLS[1]):
        row = ""
        for cx_ in range(FP_CELLS[0]):
            x0, y0 = fp_room[0] + cx_ * T, fp_room[1] + cy_ * T
            frac = g.desk[y0:y0 + T, x0:x0 + T].mean()
            row += "1" if frac >= 0.25 else "0"
        coll.append(row)
    zero = ["0" * FP_CELLS[0]] * FP_CELLS[1]

    mk("archive_ring_inlay", draw_ring_inlay, "floor_marking", zero, False,
       "floor inlay: two sea-blue rings around the desk, echoing the luminous ceiling ring", ["inlay", "ring"])
    back = mk("archive_desk_back", lambda r: draw_desk(r, "back"), "rear_prop", coll, True,
              "the ring desk's north half: cherry top plane with an inlaid line, panelled face, inner north face, cast shadow. "
              "Carries the collision of the whole desk; people walk in through the opening to the south",
              ["desk", "base", "back"])
    mk("archive_desk_front", lambda r: draw_desk(r, "front"), "front_prop", zero, True,
       "the ring desk's south arc, drawn after actors so a person standing inside is hidden by the near desk edge; "
       "one cell opening at the bottom centre", ["desk", "front", "occluder"])
    mk("archive_desk_items", draw_items, "rear_prop", zero, True,
       "card-index drawer, small terminal, stamp and ink pad, on the north half", ["items", "terminal"])
    mk("archive_ledger_before", lambda r: draw_ledger(r, "before"), "rear_prop", zero, True,
       "before: open ledger with a coral cross, the stamp mark rejected", ["quest state", "before"])
    mk("archive_ledger_after", lambda r: draw_ledger(r, "after"), "rear_prop", zero, True,
       "after: the same ledger with a coral tick and a stamped seal, the mark accepted", ["quest state", "after"])
    mk("archive_folders_before", lambda r: draw_folders(r, "before"), "rear_prop", zero, True,
       "before: two folder stacks, every folder and label the same dull linen", ["quest state", "before", "folders"])
    mk("archive_folders_after", lambda r: draw_folders(r, "after"), "rear_prop", zero, True,
       "after: the same stacks, labels regained: coral, sea blue and linen folders with lit label tabs", ["quest state", "after", "folders"])
    mk("archive_ring_glow_after", draw_ring_glow, "light", zero, False,
       "after: the luminous ceiling ring lights a linen pool on the floor inside the inlay; paints only on the bare floor fill",
       ["quest state", "after", "light"], composite={"mode": "where_color", "color": FLOOR_FILL}, kind="landmark_part")
    # contact shadow of the desk (baked into the back part): bounding box of what cast adds
    r1 = env.Room()
    g1 = Geo(r1)
    s1 = shifted(g1.desk, -1, -1) & ~g1.desk
    s2 = shifted(g1.desk, -2, -2) & ~g1.desk & ~s1
    smask = (s1 | s2)
    b = kitlib.bbox(smask)
    back.shadow = (b[0] - OX, b[1] - OY, b[2] - b[0], b[3] - b[1])
    return parts


# lamp positions relative to the landmark footprint origin (lamp footprint origins)
LAMP_OFFSETS = [[-26, 2], [90, 2], [-26, 52], [90, 52]]


def landmarks():
    before = ["archive_ring_inlay", "archive_desk_back", "archive_desk_items", "archive_ledger_before",
              "archive_folders_before", "archive_desk_front"]
    after = ["archive_ring_inlay", "archive_desk_back", "archive_desk_items", "archive_ledger_after",
             "archive_folders_after", "archive_ring_glow_after", "archive_desk_front"]
    return {
        "archive_desk": {
            "note": "Records landmark: the circular archive desk under a luminous ceiling ring. Every part is a full-size sprite "
                    "registered at one footprint origin, so a state is a list of parts; place them all at the same cell. The desk is split "
                    "into a back half (rear_prop, carries collision) and a front arc (front_prop) so a person inside the ring stands between them.",
            "size_px": [BOX_W, BOX_H],
            "footprint_origin_px": list(FP),
            "default_state": "before",
            "states": {
                "before": {"parts": before, "lamps": {"anim": "lamp", "state": "on", "offsets_px": LAMP_OFFSETS}},
                "after": {"parts": after, "lamps": {"anim": "lamp", "state": "pulse", "offsets_px": LAMP_OFFSETS}},
            },
            "part_roles": {
                "archive_ring_inlay": "floor inlay", "archive_desk_back": "base desk", "archive_desk_front": "base desk",
                "archive_desk_items": "desk items", "archive_ledger_before": "quest state", "archive_ledger_after": "quest state",
                "archive_folders_before": "quest state", "archive_folders_after": "quest state",
                "archive_ring_glow_after": "quest state", "lamp": "light accents",
            },
            "changes_after": [
                "the folder stacks regain colour: coral, sea-blue and linen folders with lit labels (levels.md 11: folder labels regain coral and sea-blue variation)",
                "the luminous ceiling ring lights a pool on the floor around the desk (levels.md 11: beneath the luminous ring)",
                "the ledger's rejected mark (cross) becomes an accepted tick and a stamped seal (levels.md 08: stamp mark rejected to accepted)",
                "all four ring lamps switch from the steady glow to the wider pulse glow",
            ],
        }
    }


# ------------------------------------------------------------------ assembly

def build_pieces():
    atlas = kitlib.Atlas(ORIENT_ATLAS)
    pieces = recoloured_pieces(atlas)
    pieces += route_arrows()
    pieces += shared_pieces()
    pieces += file_wall()
    pieces += landmark_pieces()
    anims = {
        "archive_door": {
            "kind": "state_set", "default": "closed",
            "states": {"closed": {"entries": ["archive_door_closed"], "blocked": True},
                       "half": {"entries": ["archive_door_half"], "blocked": True},
                       "open": {"entries": ["archive_door_open"], "blocked": False}},
            "play": ["closed", "half", "open"], "ms_per_frame": 120,
            "note": "play forward on approach, backward on leave; the same frames as Orientation's door, recoloured",
        },
        "lamp": {
            "kind": "state_set", "default": "on",
            "states": {"off": {"entries": ["lamp_off"]}, "on": {"entries": ["lamp", "lamp_glow_on"]},
                       "pulse": {"entries": ["lamp", "lamp_glow_pulse"]}},
            "loop": ["on", "pulse"], "ms_per_frame": 600,
            "note": "glow states: off, on (steady), pulse (wider ring). Wake = off -> on; idle breathing = on <-> pulse.",
        },
        "file_wall": {
            "kind": "state_set", "default": "closed",
            "states": {"closed": {"entries": ["file_wall_rail", "file_wall_closed"], "blocked": True},
                       "open": {"entries": ["file_wall_rail", "file_wall_open"], "blocked": False}},
            "play": ["closed", "open"], "ms_per_frame": 200,
            "note": "the sliding file wall. Slide each unit one cell outward over about 4 steps (4 px per 50 ms) when the review completes; "
                    "the open state leaves a two-cell corridor.",
        },
    }
    return pieces, anims, landmarks()


def group_rank(p):
    n = p.name
    if n.startswith(("floor_", "route_")):
        return 0
    if n.startswith("wall_"):
        return 1
    if n.startswith("archive_door"):
        return 2
    if n.startswith("lamp"):
        return 3
    if n.startswith(("desk_", "chair", "pot_plant")):
        return 4
    if n.startswith(("shelf", "partition", "terminal", "cabinet", "file_wall", "light_shaft")):
        return 5
    return 6


SECTIONS = [(0, "FLOOR, ROUTE AND WAYFINDING"), (1, "WALLS"), (2, "SLIDING GLASS DOOR (closed, half, open)"),
            (3, "LAMP (post, off, glow states)"), (4, "REUSED ORIENTATION PROPS (recoloured)"),
            (5, "NEW SHARED KIT: shelving, partition, terminal desk, cabinet, file wall, light"),
            (6, "LANDMARK: THE CIRCULAR ARCHIVE DESK (registered parts)")]


def atlas_json(pieces, rects, anims, lms):
    return {
        "schema": "atlas.schema.json",
        "kit": KIT,
        "image": "records-atlas.png",
        "tile": T,
        "layers": kitlib.LAYERS,
        "status": "Candidate, pending director review",
        "source": "Orientation pieces recoloured by exact hex swap (records_kit.py), new pieces from shared_pieces.py, Records landmark; build_records.py",
        "entries": [p.entry(rects[p.name]) for p in pieces],
        "animations": anims,
        "landmarks": lms,
    }
