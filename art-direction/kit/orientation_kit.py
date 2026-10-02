"""Orientation environment kit: atlas pieces extracted from the approved review room.

Nothing in gate1/environment.py is copied or edited. Each piece is produced by
calling the approved drawing function onto two sentinel backgrounds and keeping the
pixels it painted (kitlib.capture), so the atlas is pixel-identical to the room by
construction, and build_room.py proves it with a zero-pixel diff.

New art lives only in the "new art" section at the bottom: the lamp's off and pulse
states, the garden's "after" quest overlays, and the shelving and glass partitions drawn
by shared_pieces.py in the Orientation palette (spec coverage; the review room has none).
They use palette constants only.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("gate1", "scale-test", "cast", "palettes"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import build_scale_test as bst  # noqa: E402
import district_palettes as dp  # noqa: E402
import environment as env  # noqa: E402
import rich_finish as rf  # noqa: E402
import kitlib  # noqa: E402
import shared_pieces as shp  # noqa: E402

T = 16
W, H = env.W, env.H  # 320 x 192
STONE, GLASS, BRASS, INK, GREEN, CORAL, WOOD = env.STONE, env.GLASS, env.BRASS, env.INK, env.GREEN, env.CORAL, env.WOOD

# Original coordinates (cells are 16 px). These repeat the placement arguments that
# env.draw() passes, so each piece is captured exactly where the room draws it.
POTS = [(4, 30), (24, 30), (66, 30), (98, 30), (206, 30), (226, 30), (272, 30), (56, 96),
        (196, 128), (238, 126), (140, 166), (176, 166)]
POT_SEEDS = [100 + i for i in range(12)]
EAST_LAMPS = [(284, 52), (284, 126)]
GARDEN_LAMPS = [(92, 72), (180, 72), (180, 130)]
DESKS = [("desk_a", 16, 78, 7), ("desk_b", 246, 46, 8)]
BAYS = [6, 38, 84, 212, 244, 284]  # glass bay x positions in north_wall()
RING = (72, 56, 200, 156)           # garden walking ring (floor())
GARDEN_BOX = RING                   # landmark registration box: the ring bounds every garden part
GARDEN_FP = (96, 78)                # garden bed rim top-left: the landmark's footprint origin
X0E = 292                           # east wall x0
LIT = "#F0DEC0"                     # STONE[3], the lit floor a lamp glow may replace


class Piece:
    def __init__(self, name, sprite, tl, fp_room, fp_cells, collision, layer, kind,
                 y_sort=False, composite=None, shadow=None, tags=(), note=""):
        self.name, self.sprite, self.tl = name, sprite, tl
        self.fp_room, self.fp_cells, self.collision = fp_room, fp_cells, collision
        self.layer, self.kind, self.y_sort = layer, kind, y_sort
        self.composite = composite or {"mode": "over"}
        self.shadow, self.tags, self.note = shadow, list(tags), note

    def entry(self, rect):
        h, w = self.sprite.shape[:2]
        ox, oy = self.fp_room[0] - self.tl[0], self.fp_room[1] - self.tl[1]
        fw, fh = self.fp_cells
        e = {
            "name": self.name, "kind": self.kind, "rect": rect, "size_px": [w, h],
            "footprint": {"cells": [fw, fh], "origin_px": [ox, oy]},
            "collision": self.collision, "layer": self.layer, "y_sort": self.y_sort,
            "anchor": [ox + fw * T // 2, oy + fh * T],
            "composite": self.composite,
            "tags": self.tags,
        }
        if self.shadow:
            e["contact_shadow"] = list(self.shadow)
        if self.note:
            e["note"] = self.note
        return e


def new_room():
    return env.Room()


def cap(draw, nocast=False):
    """kitlib.capture, optionally with env.Room.cast disabled (to locate the shadow)."""
    if not nocast:
        return kitlib.capture(draw, new_room)
    saved = env.Room.cast
    env.Room.cast = lambda *a, **k: None
    try:
        return kitlib.capture(draw, new_room)
    finally:
        env.Room.cast = saved


def make(name, draw, fp_room, fp_cells, collision, layer, kind, box=None, shadow=True, **kw):
    """Capture draw(room), crop to its painted bbox (or box), locate its contact shadow."""
    rgba, painted = cap(draw)
    b = box or kitlib.bbox(painted)
    sp = kitlib.crop_rgba(rgba, b)
    sh = None
    if shadow:
        _, p2 = cap(draw, nocast=True)
        sm = painted & ~p2
        if sm.any():
            sb = kitlib.bbox(sm)
            sh = (sb[0] - b[0], sb[1] - b[1], sb[2] - sb[0], sb[3] - sb[1])
    return Piece(name, sp, (b[0], b[1]), fp_room, fp_cells, collision, layer, kind, shadow=sh, **kw)


def crop_piece(name, rgba, mask, box, fp_room, fp_cells, collision, layer, kind, **kw):
    """Piece from an already captured full-room rgba, keeping only `mask` pixels inside box."""
    m = np.zeros(mask.shape, bool)
    x0, y0, x1, y1 = box
    m[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
    out = rgba.copy()
    out[~m] = 0
    b = kitlib.bbox(m) if box is None or kw.pop("tight", True) else box
    return Piece(name, kitlib.crop_rgba(out, b), (b[0], b[1]), fp_room, fp_cells, collision, layer, kind, **kw)


def one_cell(n=1, m=1, v="0"):
    return [v * n for _ in range(m)]


# ------------------------------------------------------------------ extraction

def extract_floor(pieces, placements):
    """Slab cells (J/H/V/P), wear chips and the garden ring."""
    # Record the wear-chip RNG so the chip positions are the room's own.
    chips = []
    real_random = env.random

    class Rec:
        def __init__(self, seed):
            self.r = real_random.Random(seed)

        def randrange(self, *a):
            v = self.r.randrange(*a)
            chips.append(v)
            return v

    class Shim:
        Random = Rec
    env.random = Shim
    try:
        rgba, painted = cap(env.floor)
    finally:
        env.random = real_random
    full = rgba[:, :, :3]
    pairs = [(chips[i], chips[i + 1]) for i in range(0, len(chips), 2)]
    pairs = [(x, y) for x, y in pairs if not (72 <= y <= 108 and x >= 176)]
    chip_set = {(x + dx, y) for x, y in pairs for dx in (0, 1)}
    # Slab cells: one tile per joint class, taken from cells that hold no chip and
    # lie outside the ring; every qualifying cell of a class must be identical.
    rx0, ry0, rx1, ry1 = RING
    classes = {}
    for cy in range(H // T):
        for cx in range(W // T):
            x0, y0 = cx * T, cy * T
            if x0 < rx1 + 1 and x0 + T > rx0 - 1 and y0 < ry1 + 1 and y0 + T > ry0 - 1:
                continue
            if any((x, y) in chip_set for x in range(x0, x0 + T) for y in range(y0, y0 + T)):
                continue
            hj = cy % 2 == 0
            vj = (cx % 2 == 0) if (cy // 2) % 2 == 0 else (cx % 2 == 1)
            classes.setdefault((hj, vj), set()).add(full[y0:y0 + T, x0:x0 + T].tobytes())
    names = {(True, True): "floor_j", (True, False): "floor_h", (False, True): "floor_v", (False, False): "floor_p"}
    for key, nm in names.items():
        assert len(classes[key]) == 1, f"slab class {nm} not uniform"
        sp = np.zeros((T, T, 4), np.uint8)
        sp[:, :, :3] = np.frombuffer(next(iter(classes[key])), np.uint8).reshape(T, T, 3)
        sp[:, :, 3] = 255
        hj, vj = key
        desc = {"floor_j": "slab corner: joint on the top row and the left column",
                "floor_h": "slab edge: joint on the top row", "floor_v": "slab edge: joint on the left column",
                "floor_p": "slab interior, plain"}[nm]
        pieces.append(Piece(nm, sp, (0, 0), (0, 0), (1, 1), ["0"], "floor", "tile", note=desc, tags=["floor", "slab"]))
    # Chip: a 2x1 px wear mark. The room scatters them across the floor.
    chip = np.zeros((1, 2, 4), np.uint8)
    chip[0, :, :3] = STONE[2]
    chip[0, :, 3] = 255
    pieces.append(Piece("floor_chip", chip, (0, 0), (0, 0), (1, 1), ["0"], "floor", "tile",
                        note="2x1 px wear mark, placed with a pixel offset; drawn on the floor layer so walls and props cover it", tags=["floor", "wear"]))
    placements.extend(("floor_chip", x, y) for x, y in pairs)
    return rgba, pairs


def garden_ring(pieces, floor_rgba):
    x0, y0, x1, y1 = RING
    m = np.zeros((H, W), bool)
    m[y0:y1, x0:x1] = True
    m[y0 + 8:y1 - 8, x0 + 8:x1 - 8] = False
    for cx, cy in [(x0, y0), (x1 - 12, y0), (x0, y1 - 12), (x1 - 12, y1 - 12)]:
        m[cy:cy + 12, cx:cx + 12] = True
    rgba = floor_rgba.copy()
    rgba[~m] = 0
    sp = kitlib.crop_rgba(rgba, GARDEN_BOX)
    pieces.append(Piece("garden_ring", sp, (x0, y0), GARDEN_FP, (5, 4), ["0" * 5] * 4, "floor_marking", "landmark_part",
                        note="ring path: inlay border and four corner squares, registered at the landmark origin",
                        tags=["garden", "landmark", "ring path"]))


def extract_route(pieces, placements):
    rgba, painted = cap(env.route)
    ys, xs = np.nonzero(painted)
    line = np.zeros((H, W), bool)
    line[:, :260] = painted[:, :260]
    # One 16 px run of the inlay line.
    seg = rgba[74:75, 200:216].copy()
    assert (seg[:, :, 3] == 255).all()
    pieces.append(Piece("route_inlay", seg, (200, 74), (200, 74), (1, 1), ["0"], "floor_marking", "tile",
                        note="1 px inlay line that guides the eye along the route; repeat every 16 px",
                        tags=["floor", "route"]))
    for y in (74, 106):
        assert painted[y, 200:260].all() and not painted[y, 260:].any() or y == 106
    placements.extend(("route_inlay", x, y) for y in (74, 106) for x in (200, 216, 232, 244))
    # The mat. Its last three columns (x >= 289) are the door threshold, drawn by the door.
    mat_mask = painted.copy()
    mat_mask[:, :260] = False
    mat_mask[:, 289:] = False
    b = kitlib.bbox(mat_mask)
    sp = kitlib.crop_rgba(np.where(mat_mask[:, :, None], rgba, 0).astype(np.uint8), b)
    pieces.append(Piece("records_mat", sp, (b[0], b[1]), (b[0], b[1]), (2, 2), ["00", "00"], "floor_marking", "tile",
                        note="RECORDS mat: brightest floor in the room, lettering and arrow in dark brass; "
                             "trimmed 3 px short of the door so the door threshold finishes it",
                        tags=["wayfinding", "route", "RECORDS"]))
    placements.append(("records_mat", b[0], b[1]))


def extract_north_wall(pieces, placements):
    rgba, painted = cap(env.north_wall)
    assert painted[:34].all() and not painted[34:].any()
    strip = rgba[:34]
    plain = strip[:, 112:128].copy()  # cell 7 holds no bay and no alcove
    # Every column of the plain wall is the same: check against cell 7 where nothing overlays.
    plain_full = np.tile(plain, (1, W // T, 1))
    diff = np.any(strip != plain_full, axis=2)
    pieces.append(Piece("wall_n_plain", plain, (0, 0), (0, 0), (1, 2), ["1", "1"], "rear_wall", "wall",
                        shadow=(0, 32, 16, 2),
                        note="north wall segment: top plane (cap and lit trim), stone face, baseboard and the "
                             "wall's cast shadow on the floor; tiles horizontally",
                        tags=["wall", "north", "top plane"]))
    placements.extend(("wall_n_plain", c * T, 0) for c in range(W // T))
    # Glass bays: two reflection phases (i % 2), identical at every x.
    crops = {}
    for i, x in enumerate(BAYS):
        b = (x - 2, 9, x + 28, 29)
        d = diff[b[1]:b[3], b[0]:b[2]]
        sp = strip[b[1]:b[3], b[0]:b[2]].copy()
        sp[~d] = 0
        crops.setdefault(i % 2, []).append((x, sp))
    for ph, nm in ((0, "wall_n_window_a"), (1, "wall_n_window_b")):
        first = crops[ph][0][1]
        for _, sp in crops[ph]:
            assert np.array_equal(sp, first), f"window phase {ph} varies with x"
        pieces.append(Piece(nm, first, (0, 0), (0, 0), (2, 2), ["00", "00"], "rear_wall", "wall",
                            note="glass bay overlay for the north wall: dark frame, cool lower pane, one stepped "
                                 "reflection band, lit sill. Phase a and b differ only in the band position.",
                            tags=["wall", "window", "glass"]))
    win_pos = {"wall_n_window_a": [x for x, _ in crops[0]], "wall_n_window_b": [x for x, _ in crops[1]]}
    for nm, xs in win_pos.items():
        for x in xs:
            placements.append((nm, x - 2, 9))
    # Printer alcove overlay.
    a = (134, 6, 202, 31)
    d = diff[a[1]:a[3], a[0]:a[2]]
    sp = strip[a[1]:a[3], a[0]:a[2]].copy()
    sp[~d] = 0
    bb = kitlib.bbox(d)
    sp = sp[bb[1]:bb[3], bb[0]:bb[2]]
    pieces.append(Piece("wall_n_alcove", sp, (0, 0), (0, 0), (5, 2), ["0" * 5] * 2, "rear_wall", "wall",
                        note="brighter stone alcove with a brass wayfinding plaque, behind the printer terminal",
                        tags=["wall", "alcove", "sign"]))
    placements.append(("wall_n_alcove", a[0] + bb[0], a[1] + bb[1]))
    # Overlay pieces are placed at their own top-left, so tl == the placement point.
    return diff


def extract_east_wall(pieces, placements, anims):
    no_lamp = lambda *a, **k: None  # noqa: E731
    saved = env.lamp
    env.lamp = no_lamp
    try:
        states = {}
        for nm, d in (("closed", 0.0), ("half", 0.5), ("open", 1.0)):
            states[nm] = cap(lambda r, d=d: env.east_wall(r, d))
    finally:
        env.lamp = saved
    rgba0, painted0 = states["closed"]
    # Plain east wall: one 16 px tall slice away from the door.
    m = np.zeros((H, W), bool)
    m[128:144, 288:320] = painted0[128:144, 288:320]
    b = kitlib.bbox(m)
    sp = kitlib.crop_rgba(rgba0, b)
    assert b == (X0E, 128, 320, 144)
    tilesp = sp.copy()
    # Check vertical uniformity: row 134 and 40 share the same pixels.
    assert np.array_equal(rgba0[34:50, X0E:320], rgba0[128:144, X0E:320])
    pieces.append(Piece("wall_e_plain", tilesp, (X0E, 128), (288, 128), (2, 1), ["11"], "rear_wall", "wall",
                        note="east wall segment, side plane: dark mass with a lit trim line; tiles vertically. "
                             "Content starts 4 px into the first cell (the wall's offset in the room).",
                        tags=["wall", "east", "side plane"]))
    ys = range(34, H, T)
    placements.extend(("wall_e_plain", 288, y) for y in ys)
    # Door states over the box that holds sign, lintel, jambs, opening and threshold.
    box = (289, 50, 320, 118)
    union = np.zeros((H, W), bool)
    for nm in states:
        m = np.zeros((H, W), bool)
        m[box[1]:box[3], box[0]:box[2]] = states[nm][1][box[1]:box[3], box[0]:box[2]]
        union |= m
    b = kitlib.bbox(union)
    door_cells = (2, 3)
    for nm, blocked in (("closed", True), ("half", True), ("open", False)):
        rgba, painted = states[nm]
        m = np.zeros((H, W), bool)
        m[b[1]:b[3], b[0]:b[2]] = painted[b[1]:b[3], b[0]:b[2]]
        out = np.where(m[:, :, None], rgba, 0).astype(np.uint8)
        pieces.append(Piece(f"records_door_{nm}", kitlib.crop_rgba(out, b), (b[0], b[1]), (288, 72), door_cells,
                            ["11"] * 3 if blocked else ["00"] * 3, "rear_wall", "door",
                            note={"closed": "both glass leaves shut: frame, leaves, seam, pulls, lit RECORDS sign",
                                  "half": "leaves slid 8 px into the jamb pockets: Records floor and cabinet show",
                                  "open": "leaves fully in the pockets (15 px): doorway open, lit threshold"}[nm],
                            tags=["door", "sliding glass", "RECORDS", nm]))
    placements.append(("anim:records_door", 288, 72))
    anims["records_door"] = {
        "kind": "state_set", "default": "closed",
        "states": {"closed": {"entries": ["records_door_closed"], "blocked": True},
                   "half": {"entries": ["records_door_half"], "blocked": True},
                   "open": {"entries": ["records_door_open"], "blocked": False}},
        "play": ["closed", "half", "open"], "ms_per_frame": 120,
        "note": "play forward on approach, backward on leave; the build room's door_for() opens it over 32 px of approach",
    }


def extract_lamp(pieces, anims):
    cx, cy = EAST_LAMPS[0]
    rgba, painted = cap(lambda r: env.lamp(r, cx, cy))
    b = kitlib.bbox(painted)
    fp = (cx - 7, cy - 7)
    shadow_p = cap(lambda r: env.lamp(r, cx, cy), nocast=True)[1]
    sm = painted & ~shadow_p
    sb = kitlib.bbox(sm)
    body = make("lamp", lambda r: env.lamp(r, cx, cy), fp, (1, 1), ["1"], "rear_prop", "prop", y_sort=True,
                note="floor lamp: dark post, brass lamp head with one lit step, contact shadow",
                tags=["lamp", "light accent"])
    pieces.append(body)
    # Glow: run on lit floor; whatever is painted beyond the body is the halo.
    lit = np.array(kitlib.hex2rgb(LIT), np.uint8)
    r = new_room()
    r.img[:] = lit
    env.lamp(r, cx, cy)
    changed = np.any(r.img != lit, axis=2)
    halo = changed & ~painted
    hb = kitlib.bbox(halo)
    g = np.zeros((H, W, 4), np.uint8)
    g[halo, :3] = BRASS[3]
    g[halo, 3] = 255
    comp = {"mode": "where_color", "color": LIT}
    pieces.append(Piece("lamp_glow_on", kitlib.crop_rgba(g, hb), (hb[0], hb[1]), fp, (1, 1), ["0"], "light", "light",
                        composite=comp,
                        note="glow, one hard brass step (radius 5.2). Paints only where the floor is lit stone "
                             "#F0DEC0, so it never washes over slab joints, inlays, props or walls.",
                        tags=["lamp", "glow", "on"]))
    return body, painted, hb, fp


def extract_props(pieces, placements):
    for i, (x, y) in enumerate(POTS):
        pieces.append(make(f"pot_plant_{'abcdefghijkl'[i]}", lambda r, x=x, y=y, i=i: env.pot_plant(r, x, y, POT_SEEDS[i]),
                           (x, y + 4), (1, 1), ["1"], "rear_prop", "prop", y_sort=True,
                           note="slate planter with a leafy plant; the 12 variants differ only in leaf layout",
                           tags=["plant", "planter"]))
    pieces.append(make("sofa", lambda r: env.sofa(r, 200, 150), (200, 150), (2, 1), ["11"], "rear_prop", "prop",
                       y_sort=True, note="terracotta lounge sofa seen from above", tags=["seating"]))
    pieces.append(make("side_table", lambda r: env.side_table(r, 240, 160), (234, 156), (1, 1), ["1"], "rear_prop",
                       "prop", y_sort=True, note="round slate side table with a small plant", tags=["table", "plant"]))
    pieces.append(make("printer", env.printer, (138, 33), (4, 1), ["1111"], "rear_prop", "prop", y_sort=True,
                       note="badge printer terminal: stone housing, teal screen, card slot, three badges. "
                            "Sits in the north alcove.", tags=["terminal"]))
    saved = env.chair
    env.chair = lambda *a, **k: None
    try:
        for nm, x, y, seed in DESKS:
            pieces.append(make(nm, lambda r, x=x, y=y, seed=seed: env.desk(r, x, y, seed), (x, y), (2, 1), ["11"],
                               "rear_prop", "prop", y_sort=True,
                               note="two-cell wood desk with monitor, keyboard, paper and a small plant "
                                    "(a and b differ only in the plant leaves). The chair is a separate entry.",
                               tags=["desk"]))
    finally:
        env.chair = saved
    pieces.append(make("chair", lambda r: env.chair(r, 27, 96), (27, 96), (1, 1), ["1"], "rear_prop", "prop",
                       y_sort=True, note="coral task chair seen from above; place 11 px right and 18 px below a desk origin",
                       tags=["seating"]))
    pieces.append(make("bench", lambda r: env.bench(r, 228, 112), (228, 112), (2, 1), ["11"], "rear_prop", "prop",
                       y_sort=True, note="slatted wood bench", tags=["seating"]))
    pieces.append(make("bench_v", lambda r: env.bench_v(r, 84, 94), (84, 94), (1, 2), ["1", "1"], "rear_prop", "prop",
                       y_sort=True, note="vertical-plank garden bench, 10 x 28 px: one stands each side of the garden between the ring path and the rim "
                       "(a rich-finish detail, Mock 2.1). Blocks its two cells", tags=["seating", "garden", "rich finish"]))
    pieces.append(make("mail_counter", lambda r: env.mail_counter(r, 246, 150), (246, 150), (3, 1), ["111"],
                       "front_prop", "prop", y_sort=True,
                       note="mailroom counter with parcels and a coral courier strap; drawn after actors so "
                            "people pass behind it", tags=["counter", "occluder"]))
    for i, (x, y) in enumerate(POTS):
        placements.append((f"pot_plant_{'abcdefghijkl'[i]}", x, y + 4))
    placements.extend([("sofa", 200, 150), ("side_table", 234, 156), ("printer", 138, 33)])
    for nm, x, y, _ in DESKS:
        placements.append((nm, x, y))
        placements.append(("chair", x + 11, y + 18))
    placements.extend([("bench", 228, 112), ("bench_v", 84, 94), ("bench_v", 178, 94), ("mail_counter", 246, 150)])


def extract_garden(pieces, placements):
    """Stage-by-stage capture of env.garden(): each hook closes one named stage."""
    snaps_by_bg = []
    saved_lamp = env.lamp
    for bg in kitlib.SENTINELS:
        snaps = [("start", np.full((H, W, 3), bg, np.uint8))]
        r = new_room()
        r.img[:] = bg
        env.lamp = lambda *a, **k: None
        try:
            env.garden(r, stage=lambda name: snaps.append((name, r.img.copy())))
        finally:
            env.lamp = saved_lamp
        snaps.append(("accents", r.img.copy()))
        snaps_by_bg.append(snaps)
    names = [n for n, _ in snaps_by_bg[0]]
    assert names == ["start", "base", "foliage", "rocks", "canopy", "trunk", "accents"], names
    stage = {}
    for k in range(1, len(names)):
        mk = np.zeros((H, W), bool)
        col = np.zeros((H, W, 3), np.uint8)
        for snaps in snaps_by_bg:
            ch = np.any(snaps[k][1] != snaps[k - 1][1], axis=2)
            col[ch] = snaps[k][1][ch]
            mk |= ch
        stage[names[k]] = (mk, col)
    allm = np.zeros((H, W), bool)
    for mk, _ in stage.values():
        allm |= mk
    x0, y0, x1, y1 = GARDEN_BOX
    outside = allm.copy()
    outside[y0:y1, x0:x1] = False
    assert not outside.any(), "a garden part leaves the landmark box"

    def part(name, parts, note, tags, collision=False):
        """parts: list of (mask, colour) painted in order into one registered sprite."""
        rgba = np.zeros((H, W, 4), np.uint8)
        for mk, col in parts:
            rgba[mk, :3] = col[mk]
            rgba[mk, 3] = 255
        sp = rgba[y0:y1, x0:x1].copy()
        coll = ["11111"] * 4 if collision else ["00000"] * 4
        p = Piece(name, sp, (x0, y0), GARDEN_FP, (5, 4), coll, "rear_prop", "landmark_part",
                  note=note, tags=["garden", "landmark"] + tags)
        pieces.append(p)
        return p

    # Accents split by colour: canopy shadow is the dark foliage edge green; flowers and grass tufts are the rest.
    am, ac = stage["accents"]
    shadow_m = am & np.all(ac == rf.FOLIAGE_EDGE, axis=2)
    bloom_m = am & ~shadow_m
    base = part("garden_base", [stage["base"]], "rim, jointed side face, cast shadow, planted bed, stream with pool "
                "and lily pads", ["base", "water"], collision=True)
    _, sh_p = cap(lambda r: r.cast(96, 176, 134, rows=2))
    sb = kitlib.bbox(sh_p)
    base.shadow = (sb[0] - x0, sb[1] - y0, sb[2] - sb[0], sb[3] - sb[1])
    part("garden_foliage", [stage["foliage"]], "eight shrub clusters around the bed edge", ["foliage"])
    part("garden_rocks", [stage["rocks"]], "two grey rocks with a moss cap and a crack", ["rocks"])
    part("garden_centrepiece", [stage["canopy"], stage["trunk"]],
         "the tree: a layered canopy of leaf fans that overhangs the rim, with the trunk, root flare, bark and two limbs drawn over its lower edge", ["centrepiece", "tree"])
    part("garden_canopy_shadow", [(shadow_m, ac)], "one cool step of shadow on the bed below the crown", ["shadow"])
    part("garden_blooms", [(bloom_m, ac)], "grass tufts and five white flowers with orange centres (every second one has two yellow dots)", ["blooms"])
    placements.append(("landmark:garden", GARDEN_FP[0], GARDEN_FP[1]))


GARDEN_PARTS_BEFORE = ["garden_base", "garden_foliage", "garden_rocks", "garden_centrepiece",
                       "garden_canopy_shadow", "garden_blooms"]


# ------------------------------------------------------------------ new art (palette only)

def lamp_off(lamp_piece):
    """Unlit lamp: the head's brass steps become the ink ramp; post and shadow unchanged."""
    sp = lamp_piece.sprite.copy()
    rgb = sp[:, :, :3]
    for src, dst in ((BRASS[2], INK[2]), (BRASS[3], INK[3])):
        m = np.all(rgb == src, axis=2) & (sp[:, :, 3] > 0)
        rgb[m] = dst
    p = Piece("lamp_off", sp, lamp_piece.tl, lamp_piece.fp_room, (1, 1), ["1"], "rear_prop", "prop", y_sort=True,
              shadow=lamp_piece.shadow, note="unlit lamp: same post, head in the ink ramp, no glow",
              tags=["lamp", "light accent", "off"])
    return p


def lamp_glow_pulse(lamp_body_mask, cx, cy, fp):
    """Wider glow for the pulse frame: radius 6.4, the same single brass step."""
    r = new_room()
    halo = r.disc(cx + 0.5, cy - 0.5, 6.4) & ~lamp_body_mask
    g = np.zeros((H, W, 4), np.uint8)
    g[halo, :3] = BRASS[3]
    g[halo, 3] = 255
    b = kitlib.bbox(halo)
    return Piece("lamp_glow_pulse", kitlib.crop_rgba(g, b), (b[0], b[1]), fp, (1, 1), ["0"], "light", "light",
                 composite={"mode": "where_color", "color": LIT},
                 note="pulse frame of the glow, radius 6.4; alternate with lamp_glow_on at about 600 ms each",
                 tags=["lamp", "glow", "pulse"])


# ---- shelving and glass partitions (spec coverage; not placed in the review room)

PAL = shp.Pal("orientation")


def shelf_triples():
    """(light, body, dark) file-box colours: brass, stone and wood mostly. Coral and garden green are one
    slot in twelve each, so a run of them reads as the occasional odd box, not a rainbow."""
    def tri(r):
        return (r[3], r[2], r[1])
    D = dp.DISTRICTS["orientation"]
    brass, stone, wood = tri(D["accent"]), tri(D["floor"]), tri(D["wood"])
    return [brass, stone, wood] * 3 + [tri(dp.ORIENTATION_EXTRA["coral"]), tri(D["foliage"]), stone]


def shared_pieces():
    out = []
    sx, sy = 64, 64
    tri = [tuple(bst.hx(h) for h in t) for t in shelf_triples()]
    note_shelf = ("{n}-cell archive shelving: blue-glass frame with a lit top plane, front face with three bays, "
                  "file boxes in brass, stone and wood runs with the odd coral or garden box, kick plate")
    out.append(make("shelf_1x1", lambda r: shp.shelf(r, sx, sy, 1, PAL, 3, tri), (sx, sy + shp.SHELF_H - 16), (1, 1), ["1"],
                    "rear_prop", "prop", y_sort=True, note=note_shelf.format(n=1), tags=["shelf", "shelving", "archive"]))
    for nm, seed in (("shelf_2x1_a", 1), ("shelf_2x1_b", 2)):
        out.append(make(nm, lambda r, seed=seed: shp.shelf(r, sx, sy, 2, PAL, seed, tri), (sx, sy + shp.SHELF_H - 16), (2, 1), ["11"],
                        "rear_prop", "prop", y_sort=True, note=note_shelf.format(n=2) + "; a and b differ only in the box layout",
                        tags=["shelf", "shelving", "archive"]))
    out.append(make("partition_1x1", lambda r: shp.partition(r, sx, sy, 1, PAL), (sx, sy + shp.PART_H - 16), (1, 1), ["1"],
                    "rear_prop", "prop", y_sort=True,
                    note="free-standing glass partition, one cell: dark frame with lit cap, cool pane, one reflection band, floor rail",
                    tags=["partition", "glass"]))
    out.append(make("partition_2x1", lambda r: shp.partition(r, sx, sy, 2, PAL), (sx, sy + shp.PART_H - 16), (2, 1), ["11"],
                    "rear_prop", "prop", y_sort=True,
                    note="free-standing glass partition, two cells, with a middle post and a reflection band per pane",
                    tags=["partition", "glass"]))
    return out


# ------------------------------------------------------------------ assembly

def build_pieces():
    """Return (pieces, placements, animations, landmarks); placements keep the room's draw order."""
    pieces, placements, anims = [], [], {}
    floor_rgba, chip_pairs = extract_floor(pieces, placements)
    garden_ring(pieces, floor_rgba)
    extract_route(pieces, placements)
    extract_north_wall(pieces, placements)
    extract_east_wall(pieces, placements, anims)
    lamp_body, lamp_painted, glow_box, lamp_fp = extract_lamp(pieces, anims)
    cx, cy = EAST_LAMPS[0]
    pieces.append(lamp_off(lamp_body))
    pieces.append(lamp_glow_pulse(lamp_painted, cx, cy, lamp_fp))
    anims["lamp"] = {
        "kind": "state_set", "default": "on",
        "states": {"off": {"entries": ["lamp_off"]},
                   "on": {"entries": ["lamp", "lamp_glow_on"]},
                   "pulse": {"entries": ["lamp", "lamp_glow_pulse"]}},
        "loop": ["on", "pulse"], "ms_per_frame": 600,
        "note": "glow states: off, on (approved look), pulse (wider ring). Wake = off -> on; idle breathing = on <-> pulse.",
    }
    for x, y in EAST_LAMPS:
        placements.append(("anim:lamp", x - 7, y - 7))
    extract_props(pieces, placements)
    extract_garden(pieces, placements)
    pieces.extend(garden_after_pieces())
    pieces.extend(shared_pieces())
    # quest props (appended last, so every earlier entry keeps its exact pixels, metadata and atlas rect)
    import orientation_quest as oq
    quest, quest_anims = oq.build({p.name: p for p in pieces})
    pieces.extend(quest)
    anims.update(quest_anims)
    # orientation completion (west wall, garden through-route, seating nook): appended after the quest props too
    done, done_anims = completion_pieces({p.name: p for p in pieces})
    pieces.extend(done)
    anims.update(done_anims)
    mail = [p for p in placements if p[0] == "mail_counter"]
    placements = [p for p in placements if p[0] != "mail_counter"] + mail
    return pieces, placements, anims


def floor_rows():
    rows = []
    for cy in range(H // T):
        row = ""
        for cx in range(W // T):
            hj = cy % 2 == 0
            vj = (cx % 2 == 0) if (cy // 2) % 2 == 0 else (cx % 2 == 1)
            row += "J" if hj and vj else "H" if hj else "V" if vj else "P"
        rows.append(row)
    return rows


def make_layout(placements, states):
    out = []
    for name, x, y in placements:
        d = {"cell": [x // T, y // T]}
        off = [x % T, y % T]
        if off != [0, 0]:
            d["offset"] = off
        key, _, nm = name.partition(":")
        if nm:
            d[key] = nm
        else:
            d["entry"] = name
        out.append(d)
    return {
        "kit": "orientation", "atlas": "orientation-atlas.json", "tile": T, "size_cells": [W // T, H // T],
        "note": "Review room rebuilt from the atlas. Floor is a cell grid; every other element is a placement at "
                "cell + pixel offset of its footprint origin. Draw order = layer order, then list order.",
        "states": states,
        "floor": {"legend": {"J": "floor_j", "H": "floor_h", "V": "floor_v", "P": "floor_p"}, "rows": floor_rows()},
        "placements": out,
    }


QUEST_GROUPS = [  # (rank, name prefixes or exact names), checked before the older groups
    (7, ("elevator_", "turnstile_")),
    (8, ("clock_twin_", "conference_glass_door_", "projected_form_wall")),
    (9, ("stamp_", "pinboard_", "desk_left_cherry", "desk_right_mirror", "desk_a_front", "desk_b_front")),
    (10, ("review_table", "keyboard_", "mail_board", "mail_medals_", "mail_tray", "desk_folder")),
    (11, ("route_stripe_lit", "lamp_warm")),
    (12, ("artifact_",)),
    (13, ("wall_w_plain", "garden_base_open", "garden_north_rim_open", "seating_nook_")),
]


def group_rank(p):
    n = p.name
    for rank, keys in QUEST_GROUPS:
        if n.startswith(keys):
            return rank
    if n.startswith("floor_") or n.startswith("route_") or n == "records_mat":
        return 0
    if n.startswith("wall_"):
        return 1
    if n.startswith("records_door"):
        return 2
    if n.startswith("lamp"):
        return 3
    if n.startswith("garden_"):
        return 5
    if n.startswith(("shelf_", "partition_")):
        return 6
    return 4


def atlas_json(pieces, rects, anims, landmarks):
    entries = [p.entry(rects[p.name]) for p in pieces]
    return {
        "schema": "atlas.schema.json",
        "kit": "orientation",
        "image": "orientation-atlas.png",
        "tile": T,
        "layers": kitlib.LAYERS,
        "status": "Approved by the director 2026-10-02",
        "source": "extracted from art-direction/gate1/environment.py (approved review room); build_kit.py",
        "entries": entries,
        "animations": anims,
        "landmarks": landmarks,
    }


# ---- garden "after" state: the Orientation quest reopens the cut-through and the bed blooms

def _slab(r, x, y, w=8, h=5):
    """Flagstone seen from above: lit top edge, stone face, darker front row, contour, contact shadow."""
    r.rect(x + 1, y + h, x + w + 1, y + h + 1, INK[2])
    m = r.mask(x, y, x + w, y + h)
    r.img[m] = STONE[2]
    r.rect(x, y, x + w, y + 1, STONE[3])
    r.rect(x, y, x + 1, y + h, STONE[3])
    r.rect(x + 1, y + h - 1, x + w, y + h, STONE[1])
    r.outline(m)


def draw_cutthrough(r):
    """A built opening in the south rim (x 112-128): end caps, a stepped threshold, and an inlaid
    path strip that the flagstones meet, so the route runs through."""
    r.rect(112, 124, 128, 136, STONE[3])          # lit floor through the opening, clears the rim's cast shadow
    r.rect(112, 124, 128, 125, STONE[2])          # threshold step: nosing ...
    r.rect(112, 125, 128, 126, STONE[1])          # ... and its shaded riser (two-tone joint)
    r.rect(118, 124, 126, 134, STONE[2])          # inlaid path strip continues the flagstones
    r.rect(118, 124, 119, 133, STONE[3])          # lit left edge
    r.rect(125, 124, 126, 133, STONE[1])          # shaded right edge
    r.rect(118, 133, 126, 134, STONE[1])          # strip ends on the slab joint line
    # Left cap: top plane turns down into a lit side tone, cut face in the ink contour.
    r.rect(109, 124, 111, 126, STONE[3])
    r.rect(110, 126, 111, 133, STONE[2])
    r.rect(111, 124, 112, 134, INK[0])
    # Right cap: cut face in the contour, shaded side plane beside it.
    r.rect(128, 124, 129, 134, INK[0])
    r.rect(129, 126, 130, 133, STONE[0])
    _slab(r, 118, 118)
    _slab(r, 122, 112)
    _slab(r, 118, 106)


def draw_bloom_cluster(r):
    """Three coral blooms on green tufts with brass centres, and four single-pixel brass glints."""
    for bx, by in [(109, 102), (114, 99), (112, 106)]:
        tuft = r.mask(bx - 1, by + 3, bx + 5, by + 5)
        r.img[tuft] = GREEN[2]
        r.img[by + 3, bx - 1:bx + 5] = GREEN[3]
        r.img[by + 4, bx - 1:bx + 5] = GREEN[1]
        m = r.mask(bx, by, bx + 4, by + 4)
        r.img[m] = CORAL[2]
        r.img[by, bx:bx + 3] = CORAL[3]
        r.img[by + 1, bx] = CORAL[3]
        r.img[by + 3, bx + 1:bx + 4] = CORAL[1]
        r.img[by + 2, bx + 3] = CORAL[1]
        r.img[by + 1:by + 3, bx + 1:bx + 3] = BRASS[3]
        r.img[by + 1, bx + 2] = BRASS[2]
        r.img[by + 2, bx + 2] = BRASS[2]
    for gx, gy in [(108, 98), (118, 100), (108, 109), (117, 108)]:
        r.img[gy, gx] = BRASS[3]


def garden_after_pieces():
    out = []
    x0, y0, x1, y1 = GARDEN_BOX
    for nm, fn, note, tags in (
            ("garden_after_path", draw_cutthrough, "after: a built opening in the south rim (end caps, stepped threshold, inlaid path strip) "
             "with flagstones leading into the clearing, so the cut-through reads as reopened", ["after", "path"]),
            ("garden_after_blooms", draw_bloom_cluster, "after: a new cluster of four coral blooms with brass "
             "centres and three brass glints in the clearing", ["after", "blooms", "glints"])):
        rgba, painted = kitlib.capture(fn, new_room)
        sp = rgba[y0:y1, x0:x1].copy()
        outside = painted.copy()
        outside[y0:y1, x0:x1] = False
        assert not outside.any()
        out.append(Piece(nm, sp, (x0, y0), GARDEN_FP, (5, 4), ["00000"] * 4, "rear_prop", "landmark_part",
                         note=note, tags=["garden", "landmark"] + tags))
    return out


# After state: the same parts, but `garden_base_open` (identical pixels, collision with column 1 walkable) replaces
# `garden_base`, and `garden_north_rim_open` is drawn last so the opening cuts through the crown.
GARDEN_PARTS_AFTER = (["garden_base_open"] + GARDEN_PARTS_BEFORE[1:]
                      + ["garden_after_path", "garden_after_blooms", "garden_north_rim_open"])
# Lamp footprint origins relative to the garden footprint origin (96, 78): lamp (cx, cy) -> (cx - 7 - 96, cy - 7 - 78)
GARDEN_LAMP_OFFSETS = [[cx - 7 - GARDEN_FP[0], cy - 7 - GARDEN_FP[1]] for cx, cy in GARDEN_LAMPS]


def garden_landmark():
    return {
        "garden": {
            "note": "Orientation landmark. Every part is a full-size sprite registered at the same origin, so a state is "
                    "just a list of parts drawn in order; place them all at the same footprint origin.",
            "size_px": [128, 100],
            "footprint_origin_px": [GARDEN_FP[0] - GARDEN_BOX[0], GARDEN_FP[1] - GARDEN_BOX[1]],
            "default_state": "before",
            "states": {
                "before": {"parts": ["garden_ring"] + GARDEN_PARTS_BEFORE,
                           "lamps": {"anim": "lamp", "state": "on", "offsets_px": GARDEN_LAMP_OFFSETS}},
                "after": {"parts": ["garden_ring"] + GARDEN_PARTS_AFTER,
                          "lamps": {"anim": "lamp", "state": "pulse", "offsets_px": GARDEN_LAMP_OFFSETS}},
            },
            "part_roles": {"garden_ring": "ring path", "garden_base": "base bed", "garden_foliage": "foliage masses",
                           "garden_rocks": "foliage masses", "garden_centrepiece": "centrepiece",
                           "garden_canopy_shadow": "centrepiece", "garden_blooms": "foliage masses",
                           "garden_after_path": "quest state", "garden_after_blooms": "quest state",
                           "garden_base_open": "base bed", "garden_north_rim_open": "quest state",
                           "lamp": "light accents"},
            "changes_after": ["a built opening in the south rim (end caps, stepped threshold, inlay strip) with three flagstones: the reopened cut-through",
                              "the north rim opens too (garden_north_rim_open: a gap cut through the crown, a stepped sill and the inlaid strip), so the path runs through the bed",
                              "collision: garden_base_open replaces garden_base, and cell column 1 of the 5x4 footprint (rows 0 to 3) becomes walkable",
                              "a new cluster of four coral blooms with brass centres and three brass glints",
                              "all three garden lamps switch from the steady glow to the wider pulse glow"],
        }
    }


# ------------------------------------------------------------------ orientation completion (wave 2)
# West wall piece, the garden's through-route (north rim opening and an open-collision base) and the seating nook.
# Everything is appended after the quest props, so every earlier entry keeps its pixels, metadata and atlas rect.

def wall_w_piece():
    """West wall side plane, 28 px thick plus a 2 px cast shadow on the floor (30 x 16 px, footprint 2x1, tiles vertically).

    Light is upper-left, so this is not a flipped wall_e_plain: the east wall's inner face looks west into the light and
    carries the lit trim on its inner edge; the west wall's inner face looks east into shade, so the lit trim moves to the
    outer (left) edge and the inner edge is dark, then the wall casts its shadow east onto the floor like the north wall."""
    w = 30
    sp = np.zeros((T, w, 4), np.uint8)
    sp[:, :, 3] = 255
    cols = {0: INK[2], 1: GLASS[2], 2: INK[1], 25: INK[1], 26: INK[0], 27: INK[0], 28: INK[2], 29: INK[3]}
    for c in range(w):
        sp[:, c, :3] = cols.get(c, INK[0])
    return Piece("wall_w_plain", sp, (0, 0), (0, 0), (2, 1), ["11"], "rear_wall", "wall", shadow=(28, 0, 2, T),
                 note="west wall segment, side plane: dark mass, lit trim on the outer edge (light is upper-left, so the inner face "
                      "is in shade), then a 2 px cast shadow on the floor; tiles vertically, 28 px thick plus the shadow, "
                      "content starts at the cell edge (x = 0)",
                 tags=["wall", "west", "side plane"])


def draw_north_opening(r):
    """The garden's north rim opens above the cut-through column (x 112-128, the same column as the south opening). The
    crown is parted over the path strip only: the rim ends reappear as two stubs with contour on the cut faces, a stepped sill closes
    the gap, and the inlaid path strip runs from the ring, through the shade under the crown, to the first south flagstone.
    Drawn last in the after state, over the crown."""
    # shaded corridor under the crown: a narrow dark verge either side of the strip. The crown itself stays (the
    # rich-finish canopy is dense, so a wide flat cut read as half the tree vanishing); only the strip crosses it.
    for y in range(78, 102):
        j = (y // 3) % 2
        r.rect(116 + j, y, 118, y + 1, GREEN[0])
        r.rect(126, y, 128 - j, y + 1, GREEN[0])
    r.rect(116, 101, 128, 102, GREEN[0])                # corridor meets the bed floor: leaf shade at the lower end
    # inlaid path strip, same recipe as the south opening's strip: lit under the sky, shaded under the crown
    for y0, y1, body, lit, dark in ((64, 84, STONE[2], STONE[3], STONE[1]), (84, 101, STONE[1], STONE[2], STONE[0]),
                                    (101, 107, STONE[2], STONE[3], STONE[1])):
        r.rect(118, y0, 126, y1, body)
        r.rect(118, y0, 119, y1, lit)                   # lit left edge
        r.rect(125, y0, 126, y1, dark)                  # shaded right edge
    for y in (89, 95):                                  # flagstone joints
        r.rect(119, y, 125, y + 1, STONE[0])
    # rim ends: the hidden north rim reappears either side of the gap (contour, lit top plane, inner contour)
    r.rect(106, 78, 112, 79, INK[0])
    r.rect(106, 79, 111, 80, STONE[3])
    r.rect(106, 80, 111, 83, STONE[2])
    r.rect(106, 83, 112, 84, INK[0])
    r.rect(111, 78, 112, 84, INK[0])                    # west cut face
    r.rect(129, 78, 135, 79, INK[0])
    r.rect(130, 79, 135, 82, STONE[2])
    r.rect(130, 82, 135, 83, STONE[1])
    r.rect(129, 83, 135, 84, INK[0])
    r.rect(129, 78, 130, 84, INK[0])                    # east cut face
    r.rect(130, 79, 131, 83, STONE[0])                  # shaded side plane beside the face
    # sill across the gap: lit floor, nosing and shaded riser (two-tone joint, as in the south threshold)
    r.rect(112, 78, 129, 83, STONE[3])
    r.rect(112, 82, 129, 83, STONE[2])
    r.rect(112, 83, 129, 84, STONE[1])
    r.rect(118, 78, 126, 84, STONE[2])
    r.rect(118, 78, 119, 84, STONE[3])
    r.rect(125, 78, 126, 84, STONE[1])


def completion_pieces(by_name):
    """wall_w_plain, garden_base_open, garden_north_rim_open, the seating nook and its glow; plus the nook's state set."""
    out = [wall_w_piece()]
    # garden: same pixels as garden_base, collision opens column 1 (the cut-through) on all four rows
    base = by_name["garden_base"]
    out.append(Piece("garden_base_open", base.sprite.copy(), base.tl, base.fp_room, (5, 4), ["10111"] * 4, "rear_prop",
                     "landmark_part", shadow=base.shadow,
                     note="after state's base bed: pixel-identical to garden_base, but cell column 1 of the footprint walks, so the "
                          "cut-through is a real route; garden_base keeps the full block for the before state",
                     tags=["garden", "landmark", "after", "collision"]))
    x0, y0, x1, y1 = GARDEN_BOX
    rgba, painted = kitlib.capture(draw_north_opening, new_room)
    outside = painted.copy()
    outside[y0:y1, x0:x1] = False
    assert not outside.any(), "north opening leaves the landmark box"
    out.append(Piece("garden_north_rim_open", rgba[y0:y1, x0:x1].copy(), (x0, y0), GARDEN_FP, (5, 4), ["00000"] * 4,
                     "rear_prop", "landmark_part",
                     note="after: the north rim opens above the cut-through column: inlaid strip from the ring, a gap cut through the "
                          "crown, flagstone joints, a stepped sill and end caps. Landmark part, drawn last over the crown; a 1x1 "
                          "floor marking could not paint over the canopy.",
                     tags=["garden", "landmark", "after", "path"]))
    # seating nook: planter, side table, lamp and sofa from the existing pieces on one 3x2 footprint
    canvas = np.zeros((96, 112, 4), np.uint8)
    FX, FY = 24, 40                                     # footprint origin on the canvas

    def put(piece, cx, cy, dx=0, dy=0):
        ox, oy = piece.fp_room[0] - piece.tl[0], piece.fp_room[1] - piece.tl[1]
        x, y = FX + cx * T + dx - ox, FY + cy * T + dy - oy
        sp = piece.sprite
        h, w = sp.shape[:2]
        a = sp[:, :, 3] > 0
        reg = canvas[y:y + h, x:x + w]
        reg[a] = sp[a]
    put(by_name["pot_plant_g"], 0, 0)                   # row 0: planter, side table, lamp
    put(by_name["side_table"], 1, 0, 2, 0)
    put(by_name["lamp"], 2, 0)
    put(by_name["sofa"], 0, 1)                          # row 1: the sofa, two cells
    ys, xs = np.nonzero(canvas[:, :, 3])
    b = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    out.append(Piece("seating_nook_after", kitlib.crop_rgba(canvas, b), (b[0], b[1]), (FX, FY), (3, 2), ["111", "110"],
                     "rear_prop", "prop", y_sort=True,
                     note="the hidden seating nook the cut-through reveals: terracotta sofa, side table, planter and a floor lamp on a "
                          "3x2 footprint, assembled from the existing sofa, side_table, pot_plant_g and lamp sprites. Collision 111/110; "
                          "the lamp's glow pool is seating_nook_glow. State set seating_nook: hidden (nothing) then shown.",
                     tags=["seating", "nook", "after", "composition"]))
    # one extra lamp pool: the lamp's halo (radius 5.2, where_color on lit floor), registered at the nook's footprint origin.
    # The lamp stands in nook cell (2, 0) and the glow shares the lamp's footprint, so it is offset by two cells.
    g = by_name["lamp_glow_on"]
    gx, gy = FX + 2 * T - (g.fp_room[0] - g.tl[0]), FY - (g.fp_room[1] - g.tl[1])
    out.append(Piece("seating_nook_glow", g.sprite.copy(), (gx, gy), (FX, FY), (3, 2), ["000", "000"], "light", "light",
                     composite=dict(g.composite),
                     note="the nook lamp's glow pool: the same single brass step as lamp_glow_on, on lit floor only",
                     tags=["seating", "nook", "glow", "lamp"]))
    anims = {"seating_nook": {
        "kind": "state_set", "default": "hidden",
        "states": {"hidden": {"entries": []}, "shown": {"entries": ["seating_nook_after", "seating_nook_glow"]}},
        "note": "hidden draws nothing and blocks nothing; shown adds the composition and one lamp pool (revealed with the "
                "garden cut-through, level 06)"}}
    return out, anims
