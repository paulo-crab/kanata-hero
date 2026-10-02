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
import quest_props as qp  # noqa: E402

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


# ------------------------------------------------------------------ 4. quest props (levels 07, 08, 09, 10, 11 and Mira's routes)
# Audit: QUEST_PROP_AUDIT.md (rows R1 to R30). Everything here is drawn from the Records ramps.

QUEST_NAMES = set()
QS = (64, 64)   # capture origin for every quest prop


def _quest(name, draw, fp, cells, collision, layer, kind, note, tags, y_sort=True, shadow=True, box=None, composite=None):
    p = ok.make(name, draw, fp, cells, collision, layer, kind, box=box, shadow=shadow, y_sort=y_sort, note=note, tags=tags)
    if composite:
        p.composite = composite
    QUEST_NAMES.add(name)
    return p


def _text_window(r, x, y, kind):
    """A door text window, 11 x 8: kind 'a' the address line with the cursor, 'b' the two sides of the cursor."""
    G, W, A = PAL.glass, PAL.wall, PAL.accent
    r.rect(x, y, x + 11, y + 8, INK[0])
    r.rect(x + 1, y + 1, x + 10, y + 7, W[3] if kind == "a" else W[2])
    if kind == "a":
        for bx in (1, 3, 7, 9):                                       # thin characters either side of the cursor
            r.rect(x + bx, y + 2, x + bx + 1, y + 6, INK[2])
            r.rect(x + bx, y + 2, x + bx + 1, y + 3, INK[1])
        r.rect(x + 2, y + 4, x + 3, y + 5, INK[2])                    # a crossbar joins the first pair, as in a typed word
        r.rect(x + 8, y + 4, x + 9, y + 5, INK[2])
    else:
        r.rect(x + 6, y + 1, x + 10, y + 7, W[3])                     # the forward side is the lighter half
        for dx, dy in ((3, 2), (2, 3), (3, 4)):                       # chevron left: Backspace side
            r.img[y + dy, x + dx] = A[1]
        for dx, dy in ((7, 2), (8, 3), (7, 4)):                       # chevron right: Forward Delete side
            r.img[y + dy, x + dx] = G[2]
    r.rect(x + 5, y + 1, x + 6, y + 6, A[2])                          # the cursor, between the two sides
    r.img[y + 1, x + 5] = A[3]


def _door_leaf(r, x, y, w):
    """One cherry leaf with a glass pane, rows y..y+13."""
    G, WD = PAL.glass, PAL.wood
    r.rect(x, y, x + w, y + 14, INK[0])
    r.rect(x + 1, y + 1, x + w - 1, y + 13, WD[1])
    r.rect(x + 1, y + 1, x + w - 1, y + 2, WD[2])
    r.rect(x + 1, y + 1, x + 2, y + 13, WD[2])
    if w >= 8:
        px0, px1 = x + 3, x + w - 2
        r.rect(px0, y + 3, px1, y + 12, G[2])
        r.rect(px0, y + 9, px1, y + 12, G[1])
        for k in range(5):
            if px0 + 2 + k < px1:
                r.img[y + 3 + k, px0 + 2 + k] = G[3]


def draw_repair_door(r, x0, y0, state):
    """The repair door of level 07, a north-wall door 2 cells wide and 34 px tall (the wall's own height, so it
    replaces two plain wall tiles). Above the leaves a display band holds the two text windows: the address line
    with its cursor, and the two sides of the cursor (Backspace to the left, Forward Delete to the right).
    states: closed, half (leaves 6 px into the jamb pockets), open (leaves 12 px in, a lit archive beyond)."""
    G, W, WD, F, A = PAL.glass, PAL.wall, PAL.wood, PAL.floor, PAL.accent
    w = 32
    r.rect(x0, y0, x0 + w, y0 + 1, INK[2])                             # the wall's cap, as wall_n_plain draws it
    r.rect(x0, y0 + 1, x0 + w, y0 + 4, INK[1])
    r.rect(x0, y0 + 4, x0 + w, y0 + 5, G[2])
    r.rect(x0, y0 + 5, x0 + w, y0 + 6, INK[0])
    r.rect(x0, y0 + 6, x0 + w, y0 + 32, INK[0])                        # frame mass
    r.rect(x0 + 1, y0 + 7, x0 + 3, y0 + 31, WD[1])                      # jambs, lit on the left
    r.rect(x0 + 1, y0 + 7, x0 + 2, y0 + 31, WD[2])
    r.rect(x0 + w - 3, y0 + 7, x0 + w - 1, y0 + 31, WD[1])
    r.rect(x0 + w - 2, y0 + 7, x0 + w - 1, y0 + 31, WD[0])
    r.rect(x0 + 1, y0 + 7, x0 + w - 1, y0 + 18, WD[1])                  # display band
    r.rect(x0 + 1, y0 + 7, x0 + w - 1, y0 + 8, WD[2])
    r.rect(x0 + 3, y0 + 17, x0 + w - 3, y0 + 18, WD[0])
    _text_window(r, x0 + 4, y0 + 8, "a")
    _text_window(r, x0 + 17, y0 + 8, "b")
    # opening: rows 18..31, x 3..28
    ox0, ox1, oy0, oy1 = x0 + 3, x0 + w - 3, y0 + 18, y0 + 31
    if state == "closed":
        _door_leaf(r, ox0, oy0, 13)
        _door_leaf(r, ox0 + 13, oy0, 13)
        for px_ in (ox0 + 10, ox0 + 15):                                 # pulls by the seam
            r.rect(px_, oy0 + 6, px_ + 1, oy0 + 10, W[3])
    else:
        # the lit archive beyond: back wall, shelf-end stripes, a pale floor with a mat
        r.rect(ox0, oy0, ox1, oy1, W[1])
        r.rect(ox0, oy0, ox1, oy0 + 1, INK[1])
        r.rect(ox0, oy0 + 1, ox1, oy0 + 2, INK[2])
        r.rect(ox0, oy0 + 6, ox1, oy1, F[3])
        r.rect(ox0, oy0 + 6, ox1, oy0 + 7, F[2])
        for sx in range(ox0 + 2, ox1 - 1, 6):
            r.rect(sx, oy0 + 2, sx + 2, oy0 + 6, A[1])
            r.rect(sx, oy0 + 2, sx + 1, oy0 + 6, A[2])
        r.rect(ox0 + 7, oy0 + 9, ox1 - 7, oy0 + 12, F[2])
        if state == "half":
            _door_leaf(r, ox0, oy0, 7)
            _door_leaf(r, ox1 - 7, oy0, 7)
        else:
            _door_leaf(r, ox0, oy0, 2)
            _door_leaf(r, ox1 - 2, oy0, 2)
    r.rect(x0 + 1, y0 + 31, x0 + w - 1, y0 + 32, WD[0])                 # threshold
    if state != "open":
        r.rect(x0, y0 + 32, x0 + w, y0 + 33, INK[2])                    # cast shadow, as the wall draws it
        r.rect(x0, y0 + 33, x0 + w, y0 + 34, INK[3])
    else:
        r.rect(x0 + 3, y0 + 32, x0 + w - 3, y0 + 33, F[2])             # the lit threshold continues onto the floor line


def shelf_end_light(r, x0, y0, on):
    """An end-of-shelf light, 6 x 12: an ink strip with a tall pane. Off: dull sea-blue glass. On: a linen core with a
    peach edge (never gold: gold is the UI's opened-route marker)."""
    G, W, A = PAL.glass, PAL.wall, PAL.accent
    r.rect(x0, y0, x0 + 6, y0 + 12, INK[0])
    r.rect(x0 + 1, y0 + 1, x0 + 5, y0 + 9, G[1])
    if on:
        r.rect(x0 + 1, y0 + 1, x0 + 5, y0 + 9, A[3])
        r.rect(x0 + 2, y0 + 2, x0 + 4, y0 + 8, W[3])
        r.img[y0 + 1, x0 + 1] = W[3]
    else:
        r.rect(x0 + 1, y0 + 1, x0 + 5, y0 + 2, G[2])
        r.rect(x0 + 1, y0 + 1, x0 + 2, y0 + 9, G[2])
    r.rect(x0 + 1, y0 + 9, x0 + 5, y0 + 11, G[0])
    r.rect(x0 + 1, y0 + 10, x0 + 5, y0 + 11, G[1])


FOLDER_DRIFT = [(0, 1), (3, 0), (1, 2), (4, 0), (2, 1), (0, 2)]   # (tab rise, tab x shift) per folder


def draw_folder_rack(r, x0, y0, state):
    """A low open file rack, 2 cells wide: six sea-blue folders standing on a cherry top plane behind a front lip.
    drift: tabs at uneven heights and shifts, folders of uneven height, dull linen labels. aligned: every tab on one line
    in a regular rhythm, labels linen with a coral mark."""
    G, W, WD, A = PAL.glass, PAL.wall, PAL.wood, PAL.accent
    env.block(r, x0, y0 + 11, x0 + 32, y0 + 27, 7, WD, WD)
    for i in range(6):
        fx = x0 + 1 + 5 * i
        rise, shift = FOLDER_DRIFT[i] if state == "drift" else (0, i % 2)
        top = y0 + 9 + (rise // 2 if state == "drift" else 0)
        bot = y0 + 19
        r.rect(fx, top, fx + 4, bot, G[2])
        r.rect(fx, top, fx + 1, bot, G[3])
        r.rect(fx + 3, top, fx + 4, bot, G[1])
        ty = top - 2 - (rise if state == "drift" else 1)
        tx = fx + (shift if state == "drift" else 0)
        r.rect(tx, ty, tx + 3, top, W[2] if state == "drift" else W[3])
        r.outline(r.mask(tx, ty, tx + 3, top + 1) | r.mask(fx, top, fx + 4, bot), INK[0])
        if state == "aligned":
            r.img[ty + 1, tx + 1] = A[2]
    r.rect(x0 + 1, y0 + 19, x0 + 31, y0 + 20, WD[3])                    # the front lip hides the folders' feet
    r.rect(x0 + 1, y0 + 20, x0 + 31, y0 + 21, WD[1])


def draw_ledger_table(r, x0, y0, state):
    """The two-sided ledger table of level 09, 4 cells wide: a long cherry table with one long open folio lying along
    it. before: Pace's revision put both sign-offs in the middle and the table is dull. after: the sign-offs sit at
    both margins and both ends of the table are lit (lit wood and bright pages)."""
    W, WD, A = PAL.wall, PAL.wood, PAL.accent
    env.block(r, x0, y0 + 6, x0 + 64, y0 + 22, 6, WD, WD)
    if state == "after":
        for ex0, ex1 in ((x0 + 2, x0 + 20), (x0 + 44, x0 + 62)):        # the lit wood at each end
            r.rect(ex0, y0 + 7, ex1, y0 + 15, WD[3])
    fol = r.mask(x0 + 4, y0 + 7, x0 + 60, y0 + 15)
    r.img[fol] = W[2]
    r.rect(x0 + 31, y0 + 8, x0 + 33, y0 + 14, W[1])                      # the spine
    if state == "after":
        r.rect(x0 + 5, y0 + 8, x0 + 18, y0 + 14, W[3])
        r.rect(x0 + 46, y0 + 8, x0 + 59, y0 + 14, W[3])
    for sx in list(range(x0 + 6, x0 + 30, 4)) + list(range(x0 + 35, x0 + 59, 4)):   # ruled text, short runs
        r.rect(sx, y0 + 9, sx + 3, y0 + 10, INK[2])
        r.rect(sx, y0 + 12, sx + 3, y0 + 13, INK[2])
    marks = [(x0 + 24, y0 + 10), (x0 + 36, y0 + 10)] if state == "before" else [(x0 + 6, y0 + 10), (x0 + 52, y0 + 10)]
    for mx, my in marks:                                                 # the sign-off: a coral scrawl on the line
        r.rect(mx, my, mx + 6, my + 2, A[2])
        r.rect(mx, my + 1, mx + 6, my + 2, A[1])
        r.img[my, mx + 1] = A[3]
        r.img[my - 1, mx + 4] = A[2]
    r.outline(fol, INK[0])


def draw_rolling_ladder(r, x0, y0, state):
    """The rolling ladder of level 09, a 4-cell gallery wall: a shelf cell at each end, a two-cell opening that shows
    the stair to the upper gallery, a rail across the top, and a cherry ladder hung from the rail. closed: the
    ladder stands across the opening. open: it has rolled in front of the left shelf and the stair is free."""
    G, W, WD, F = PAL.glass, PAL.wall, PAL.wood, PAL.floor
    sp.shelf(r, x0, y0 + 4, 1, PAL, 5)
    sp.shelf(r, x0 + 48, y0 + 4, 1, PAL, 6)
    # the opening: dark back, seven treads receding into the gallery, cherry posts either side
    r.rect(x0 + 16, y0 + 4, x0 + 48, y0 + 32, INK[0])
    r.rect(x0 + 17, y0 + 5, x0 + 47, y0 + 32, INK[1])
    surf = [F[3], F[2], F[2], F[1], F[1], F[0], F[0]]
    riser = [F[2], F[1], F[1], F[0], F[0], INK[2], INK[2]]
    for i in range(7):
        yb = y0 + 31 - 3 * i
        r.rect(x0 + 19, yb - 1, x0 + 45, yb, surf[i])
        r.rect(x0 + 19, yb - 2, x0 + 45, yb - 1, surf[i])
        r.rect(x0 + 19, yb, x0 + 45, yb + 1, riser[i])
    r.rect(x0 + 17, y0 + 5, x0 + 19, y0 + 32, WD[1])
    r.rect(x0 + 17, y0 + 5, x0 + 18, y0 + 32, WD[2])
    r.rect(x0 + 45, y0 + 5, x0 + 47, y0 + 32, WD[1])
    r.rect(x0 + 46, y0 + 5, x0 + 47, y0 + 32, WD[0])
    # the rail the ladder hangs from
    r.rect(x0, y0, x0 + 64, y0 + 4, INK[0])
    r.rect(x0, y0 + 1, x0 + 64, y0 + 3, G[2])
    r.rect(x0, y0 + 1, x0 + 64, y0 + 2, G[3])
    r.rect(x0, y0 + 3, x0 + 64, y0 + 4, G[1])
    lx = x0 + 22 if state == "closed" else x0 + 3
    for rx in (lx, lx + 15):                                             # the two ladder rails
        r.rect(rx, y0 + 2, rx + 3, y0 + 32, INK[0])
        r.rect(rx + 1, y0 + 3, rx + 2, y0 + 32, WD[2])
        r.rect(rx + 1, y0 + 3, rx + 2, y0 + 4, WD[3])
    for ry in range(y0 + 8, y0 + 31, 4):                                 # rungs
        r.rect(lx + 3, ry, lx + 15, ry + 1, WD[3])
        r.rect(lx + 3, ry + 1, lx + 15, ry + 2, WD[0])
    for rx in (lx + 1, lx + 16):                                          # the wheels on the rail
        r.rect(rx - 1, y0, rx + 2, y0 + 4, INK[0])
        r.rect(rx, y0 + 1, rx + 1, y0 + 3, G[3])


def draw_report_table(r, x0, y0, state):
    """The report table of level 10, 2 cells wide: a cherry table with Pace's grey summary (three orderly bars). after:
    the original report lies beside it, a cherry cover with a coral spine and a linen label."""
    W, WD, A = PAL.wall, PAL.wood, PAL.accent
    env.block(r, x0, y0, x0 + 34, y0 + 16, 5, WD, WD)
    sm = r.mask(x0 + 5, y0 + 2, x0 + 16, y0 + 9)
    r.img[sm] = W[2]
    r.rect(x0 + 5, y0 + 2, x0 + 16, y0 + 3, W[3])
    for by in (4, 6):                                                    # Pace's orderly horizontal bars
        r.rect(x0 + 7, y0 + by, x0 + 14, y0 + by + 1, INK[2])
    r.outline(sm)
    if state == "after":
        om = r.mask(x0 + 19, y0 + 3, x0 + 30, y0 + 10)
        r.img[om] = WD[1]
        r.rect(x0 + 19, y0 + 3, x0 + 30, y0 + 4, WD[2])
        r.rect(x0 + 19, y0 + 3, x0 + 22, y0 + 10, A[2])
        r.rect(x0 + 19, y0 + 3, x0 + 20, y0 + 10, A[3])
        r.rect(x0 + 24, y0 + 5, x0 + 29, y0 + 8, W[3])
        r.rect(x0 + 25, y0 + 6, x0 + 28, y0 + 7, INK[1])
        r.outline(om)


def decor_piece(name, kind, note, tags, pal=None):
    w, h = {"courier_loop": (12, 12), "archive_folder": (12, 10)}[kind]
    x0, y0 = QS
    return _quest(name, lambda r: qp.mira_decor(r, kind, x0, y0, pal or PAL), (x0 - (16 - w) // 2, y0 + h - 16), (1, 1), ["0"], "rear_prop", "prop",
                  note, tags, shadow=False)


def quest_pieces():
    """The Records quest props. Returns (pieces, state sets)."""
    out = []
    sx, sy = QS
    door_notes = {"closed": "both cherry leaves shut: the leaves meet at a seam with pulls and glass panes",
                  "half": "leaves slid 6 px into the jamb pockets: the lit archive shows in the gap",
                  "open": "leaves nearly in the pockets: a lit archive with shelf-end stripes and a mat shows through, and the threshold is lit"}
    for st in ("closed", "half", "open"):
        p = _quest(f"repair_door_{st}", lambda r, st=st: draw_repair_door(r, sx, sy, st), (sx, sy), (2, 2),
                   ["11", "11"] if st != "open" else ["00", "00"], "rear_wall", "door",
                   "the level 07 repair door, a north-wall door 32 x 34 px that replaces two plain wall tiles: a display band with two clear text windows "
                   "(the address line with its cursor, and the two sides of the cursor: Backspace chevron left, Forward Delete chevron right), then "
                   "cherry leaves with glass panes. " + door_notes[st] + ". Closed and half block; open walks. No flashing failure state",
                   ["door", "repair door", "level 07", st], y_sort=False, shadow=False, box=(sx, sy, sx + 32, sy + 34))
        if st != "open":
            p.shadow = (0, 32, 32, 2)
        out.append(p)
    for st in ("off", "on"):
        out.append(_quest(f"shelf_end_light_{st}", lambda r, st=st: shelf_end_light(r, sx, sy, st == "on"), (sx - 5, sy - 4), (1, 1), ["0"], "rear_prop", "prop",
                          "a 6 x 12 end-of-shelf light (level 07: shelf-end lights change when the door answers). "
                          + ("off: dull sea-blue glass" if st == "off" else "on: a linen core with a peach edge (not gold: gold is the UI's opened-route marker)")
                          + ". Place against the end of a shelf unit, one cell wide, no collision", ["light", "shelf", "level 07", st], shadow=False, box=(sx, sy, sx + 6, sy + 12)))
    for st in ("idle", "ready"):
        out.append(_quest(f"courier_chute_{st}", lambda r, st=st: qp.courier_chute(r, sx, sy, PAL, st == "ready"), (sx, sy + 12), (2, 1), ["11"], "rear_prop", "prop",
                          "Mira's courier chute, 2 x 1: a metal cabinet with a slot, a tube rising into the ceiling, a catch tray and an indicator lamp. "
                          + ("idle: the lamp is dull, the slot empty" if st == "idle" else "ready (Mira has a route to offer): a slip stands in the slot and the lamp is lit in coral"),
                          ["chute", "mira", "courier", st], box=(sx, sy, sx + 34, sy + 30)))
    for st in ("drift", "aligned"):
        out.append(_quest(f"folder_rack_{st}", lambda r, st=st: draw_folder_rack(r, sx, sy, st), (sx, sy + 11), (2, 1), ["11"], "rear_prop", "prop",
                          "a low open file rack, 2 x 1 (level 08): six sea-blue folders. "
                          + ("drift: label tabs at uneven heights and shifts, uneven folders, dull labels" if st == "drift"
                             else "aligned: every tab on one line in a regular rhythm, linen labels with a coral mark"),
                          ["folder", "file rack", "level 08", st], box=(sx, sy + 5, sx + 34, sy + 29)))
    for st in ("before", "after"):
        out.append(_quest(f"ledger_table_{st}", lambda r, st=st: draw_ledger_table(r, sx, sy, st), (sx, sy + 6), (4, 1), ["1111"], "rear_prop", "prop",
                          "the two-sided ledger table, 4 x 1 (level 09): a long cherry table with an open folio along it. "
                          + ("before: both sign-offs sit in the middle, the table is dull" if st == "before"
                             else "after: sign-offs at both margins, both ends lit (lit wood, bright pages)")
                          + ". Put one or two light_shaft entries across it for the beam of daylight", ["table", "ledger", "level 09", st], box=(sx, sy + 6, sx + 66, sy + 24)))
    for st in ("closed", "open"):
        out.append(_quest(f"rolling_ladder_{st}", lambda r, st=st: draw_rolling_ladder(r, sx, sy, st), (sx, sy + 16), (4, 1),
                          ["1111"] if st == "closed" else ["1001"], "rear_prop", "prop",
                          "the rolling ladder gallery wall, 4 x 1 (level 09): a shelf cell at each end, a two-cell opening onto the stair to the upper gallery, a rail with wheels, a cherry ladder. "
                          + ("closed: the ladder stands across the opening (cols 0-3 block)" if st == "closed"
                             else "open: the ladder has rolled in front of the left shelf; cols 1-2 are free"),
                          ["ladder", "gallery", "level 09", st], box=(sx, sy, sx + 66, sy + 34)))
    for st in ("before", "after"):
        out.append(_quest(f"report_table_{st}", lambda r, st=st: draw_report_table(r, sx, sy, st), (sx, sy), (2, 1), ["11"], "rear_prop", "prop",
                          "the report table, 2 x 1 (level 10): a cherry table. "
                          + ("before: Pace's grey summary alone (three orderly bars)" if st == "before"
                             else "after: Noor has placed the original report beside the summary (cherry cover, coral spine, linen label)"),
                          ["table", "report", "level 10", st], box=(sx, sy, sx + 36, sy + 18)))
    out.append(decor_piece("mira_decor_courier_loop", "courier_loop",
                           "Courier Loop reward (after level 07): a loop-arrow medal on a small stand; a desk decoration, 1 x 1, no collision", ["decor", "mira", "desk"]))
    out.append(decor_piece("mira_decor_archive_folder", "archive_folder",
                           "Archive Loop reward (after level 11): a coral desk folder with a lit tab and a sheet showing; a desk decoration, 1 x 1, no collision", ["decor", "mira", "desk"]))
    anims = {
        "repair_door": {"kind": "state_set", "default": "closed",
                        "states": {"closed": {"entries": ["repair_door_closed"], "blocked": True}, "half": {"entries": ["repair_door_half"], "blocked": True},
                                   "open": {"entries": ["repair_door_open"], "blocked": False}},
                        "play": ["closed", "half", "open"], "ms_per_frame": 120,
                        "note": "level 07: the door retracts when the address is accepted; play forward, backward when the player leaves. Only open is walkable. Do not place plain wall tiles under it"},
        "shelf_end_light": {"kind": "state_set", "default": "off",
                            "states": {"off": {"entries": ["shelf_end_light_off"]}, "on": {"entries": ["shelf_end_light_on"]}},
                            "play": ["off", "on"], "ms_per_frame": 200,
                            "note": "level 07: the shelf-end lights come on when the repair door answers"},
        "courier_chute": {"kind": "state_set", "default": "idle",
                          "states": {"idle": {"entries": ["courier_chute_idle"]}, "ready": {"entries": ["courier_chute_ready"]}},
                          "play": ["idle", "ready"], "ms_per_frame": 300,
                          "note": "Mira's chute: ready while she has a route to offer"},
        "folder_rack": {"kind": "state_set", "default": "drift",
                        "states": {"drift": {"entries": ["folder_rack_drift"]}, "aligned": {"entries": ["folder_rack_aligned"]}},
                        "play": ["drift", "aligned"], "ms_per_frame": 150,
                        "note": "level 08: the repaired folders align"},
        "ledger_table": {"kind": "state_set", "default": "before",
                         "states": {"before": {"entries": ["ledger_table_before"]}, "after": {"entries": ["ledger_table_after"]}},
                         "play": ["before", "after"], "ms_per_frame": 200,
                         "note": "level 09: correct margins light both ends of the ledger table"},
        "rolling_ladder": {"kind": "state_set", "default": "closed",
                           "states": {"closed": {"entries": ["rolling_ladder_closed"], "blocked": True}, "open": {"entries": ["rolling_ladder_open"], "blocked": False}},
                           "play": ["closed", "open"], "ms_per_frame": 200,
                           "note": "level 09: the rolling ladder moves and reveals the stair to the upper gallery (slide it about 19 px over 4 steps)"},
        "report_table": {"kind": "state_set", "default": "before",
                         "states": {"before": {"entries": ["report_table_before"]}, "after": {"entries": ["report_table_after"]}},
                         "play": ["before", "after"], "ms_per_frame": 200,
                         "note": "level 10: Noor places the original report beside the summary"},
    }
    return out, anims


# ------------------------------------------------------------------ assembly

def build_pieces():
    atlas = kitlib.Atlas(ORIENT_ATLAS)
    pieces = recoloured_pieces(atlas)
    pieces += route_arrows()
    pieces += shared_pieces()
    pieces += file_wall()
    pieces += landmark_pieces()
    qpieces, qanims = quest_pieces()
    pieces += qpieces
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
    anims.update(qanims)
    return pieces, anims, landmarks()


def group_rank(p):
    n = p.name
    if n in QUEST_NAMES:
        return 7
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
            (6, "LANDMARK: THE CIRCULAR ARCHIVE DESK (registered parts)"),
            (7, "QUEST PROPS (levels 07 to 11, Mira's routes): repair door, shelf-end light, courier chute, folder rack, ledger table, rolling ladder, report table, Mira decor")]


def atlas_json(pieces, rects, anims, lms):
    return {
        "schema": "atlas.schema.json",
        "kit": KIT,
        "image": "records-atlas.png",
        "tile": T,
        "layers": kitlib.LAYERS,
        "status": "Approved by the director 2026-10-02",
        "source": "Orientation pieces recoloured by exact hex swap (records_kit.py), new pieces from shared_pieces.py, Records landmark; build_records.py",
        "entries": [p.entry(rects[p.name]) for p in pieces],
        "animations": anims,
        "landmarks": lms,
    }
