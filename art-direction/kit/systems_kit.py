"""Systems environment kit (task 7.2): atlas pieces, the routing machine landmark and the reference
room layout.

Palette: cool porcelain floor, steel-blue wall panels, cobalt equipment (glass ramp), cool sand wood,
mint circuit light (foliage ramp, a device ramp) and a safety-orange accent (palettes/district_palettes.py).

Sources of art, all palette-only:
  1. Orientation pieces recoloured by an exact hex swap (floor, walls, windows, door, lamp, desk,
     chair, planters). The swap raises on any unmapped pixel.
  2. District-agnostic pieces from shared_pieces.py (shelving, partition, terminal desk, cabinet),
     drawn with the Systems ramps.
  3. Systems-only pieces, drawn as functions here: floor conduit channels in three families, server
     racks, a status board, glass-bridge deck and rail, route arrows, and the routing machine.

Shared changes proposed instead of made (see SYSTEMS_KIT_SPEC.md): none of the shared files is edited.
"""
import os
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
KIT = "systems"
PAL = sp.Pal("systems")
PAL.paper = PAL.floor      # paper, slips and label plates are porcelain (the wall ramp is steel blue); read only by quest_props.py
S = dp.DISTRICTS["systems"]
O = dp.DISTRICTS["orientation"]
INK, shifted = bst.INK, bst.shifted
FLOOR_FILL = S["floor"][3]   # bare porcelain: the colour a light composite may recolour
FLOOR, WALL, GLASS, WOOD, MINT, ORANGE = PAL.floor, PAL.wall, PAL.glass, PAL.wood, PAL.foliage, PAL.accent
FAMILIES = {"cobalt": GLASS, "mint": MINT, "orange": ORANGE}   # the three conduit families

ORIENT_ATLAS = os.path.join(HERE, "orientation-atlas.json")
STONE_S, GLASS_S, WOOD_S, GREEN_S, BRASS_S = (O["floor"], O["glass"], O["wood"], O["foliage"], O["accent"])
CORAL_S = dp.ORIENTATION_EXTRA["coral"]


# ------------------------------------------------------------------ 1. recoloured Orientation pieces

def _ramp_map(src, dst):
    return {s.upper(): d.upper() for s, d in zip(src, dst)}


def recolour_xy(sprite, base, rules=()):
    """Exact hex swap. base: list of (src_ramp, dst_ramp). rules: [(predicate(x, y), maps)] override the
    base maps for pixels where the predicate holds (first match wins). Ink is shared and left alone.
    Raises on an unmapped pixel."""
    out = sprite.copy()
    bmap = {}
    for s, d in base:
        bmap.update(_ramp_map(s, d))
    rmaps = []
    for pred, maps in rules:
        m = {}
        for s, d in maps:
            m.update(_ramp_map(s, d))
        rmaps.append((pred, m))
    ink = {h.upper() for h in dp.INK}
    for y in range(sprite.shape[0]):
        for x in range(sprite.shape[1]):
            if sprite[y, x, 3] == 0:
                continue
            h = kitlib.hexs(sprite[y, x, :3])
            if h in ink:
                continue
            m = bmap
            for pred, rm in rmaps:
                if pred(x, y):
                    m = rm
                    break
            if h not in m:
                raise AssertionError(f"unmapped colour {h} at ({x},{y})")
            out[y, x, :3] = kitlib.hex2rgb(m[h])
    return out


def from_orientation(atlas, src, new, base, rules=(), note="", tags=(), comp_color=None):
    e = atlas.entries[src]
    sprite = recolour_xy(atlas.sprite(src), base, rules)
    ox, oy = e["footprint"]["origin_px"]
    comp = dict(e.get("composite", {"mode": "over"}))
    if comp["mode"] == "where_color":
        comp["color"] = comp_color
    return ok.Piece(new, sprite, (0, 0), (ox, oy), tuple(e["footprint"]["cells"]), list(e["collision"]), e["layer"],
                    e["kind"], y_sort=e.get("y_sort", False), composite=comp, shadow=e.get("contact_shadow"),
                    tags=list(tags) or list(e.get("tags", [])), note=note or e.get("note", ""))


def recoloured_pieces(atlas):
    pieces = []
    floor_maps = [(STONE_S, S["floor"])]
    for nm, desc in (("floor_j", "slab corner: joint on the top row and the left column"),
                     ("floor_h", "slab edge: joint on the top row"), ("floor_v", "slab edge: joint on the left column"),
                     ("floor_p", "slab interior, plain")):
        pieces.append(from_orientation(atlas, nm, nm, floor_maps, note=f"Systems floor, {desc}. Near-white porcelain, broad slabs, no grain",
                                       tags=["floor", "slab"]))
    pieces.append(from_orientation(atlas, "floor_chip", "floor_chip", floor_maps,
                                   note="2x1 px wear mark on the floor layer; placed with a pixel offset"))
    pieces.append(from_orientation(atlas, "route_inlay", "route_inlay", [([STONE_S[2]], [S["floor"][1]])],
                                   note="1 px inlay line in floor step 1 that guides the eye along the route; repeat every 16 px (horizontal). "
                                        "One step darker than the slab joints so the line outranks them"))
    v = np.rot90(pieces[-1].sprite, 1).copy()
    pieces.append(ok.Piece("route_inlay_v", v, (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                           note="route_inlay turned 90 degrees: the same line for vertical corridor edges", tags=["floor", "route"]))
    wall_maps = [(STONE_S, S["wall"]), (GLASS_S, S["glass"])]
    pieces.append(from_orientation(atlas, "wall_n_plain", "wall_n_plain", wall_maps,
                                   note="north wall segment: ink cap with a cobalt trim, steel-blue panel face, baseboard and cast shadow; tiles horizontally"))
    for nm in ("wall_n_window_a", "wall_n_window_b"):
        pieces.append(from_orientation(atlas, nm, nm, wall_maps,
                                       note="service window overlay for the north wall: dark frame, cobalt lower pane, one stepped reflection band, lit sill"))
    pieces.append(from_orientation(atlas, "wall_e_plain", "wall_e_plain", wall_maps,
                                   note="east wall segment, side plane; tiles vertically. Content starts 4 px into the first cell"))

    # Door: cool-sand frame (PALETTES_SPEC decision 5: wood or glass ramps, not brass), cobalt leaves,
    # porcelain sign plate with an orange chevron. Half and open show a lit porcelain corridor beyond,
    # because the cobalt interior would be darker than the steel-blue wall beside it.
    sign = (lambda x, y: y < 14,
            [(BRASS_S, S["floor"]), (CORAL_S, S["accent"]), (STONE_S, S["floor"]), (GLASS_S, S["glass"])])
    door_maps = [(BRASS_S, S["wood"]), (STONE_S, S["wall"]), (GLASS_S, S["glass"]), (CORAL_S, S["accent"])]
    beyond = [(GLASS_S, S["floor"]), (STONE_S, S["wall"]), (BRASS_S, S["wood"]), (CORAL_S, S["accent"])]
    beyond_rule = {"closed": None,
                   "half": (lambda x, y: 25 <= y < 60 and 3 <= x < 10, beyond),
                   "open": (lambda x, y: 25 <= y < 60 and 3 <= x < 21, beyond)}
    for st, note in (("closed", "both cobalt glass leaves shut: sand frame, leaves, seam, pulls, porcelain SERVICE sign with an orange chevron"),
                     ("half", "leaves slid 8 px into the jamb pockets: the lit corridor and a locker show through"),
                     ("open", "leaves fully in the pockets (15 px): the doorway is open onto a lit porcelain corridor")):
        rules = [sign] + ([beyond_rule[st]] if beyond_rule[st] else [])
        rules = [rules[-1]] + rules[:-1] if beyond_rule[st] else rules   # the corridor rule wins inside the opening
        pieces.append(from_orientation(atlas, f"records_door_{st}", f"service_door_{st}", door_maps, rules=rules,
                                       note=note, tags=["door", "sliding glass", st]))
    lamp_maps = [(BRASS_S, S["foliage"])]
    pieces.append(from_orientation(atlas, "lamp", "lamp", lamp_maps, note="floor lamp: dark post, mint circuit-light head with one lit step, contact shadow"))
    pieces.append(from_orientation(atlas, "lamp_off", "lamp_off", lamp_maps, note="unlit lamp: head in the ink ramp, no glow"))
    pieces.append(from_orientation(atlas, "lamp_glow_on", "lamp_glow_on", lamp_maps, comp_color=FLOOR_FILL,
                                   note="glow, one hard pale-mint step (radius 5.2). Paints only where the floor is the bare fill "
                                        f"{FLOOR_FILL}, so it never washes over joints, inlays, channels, props or walls"))
    pieces.append(from_orientation(atlas, "lamp_glow_pulse", "lamp_glow_pulse", lamp_maps, comp_color=FLOOR_FILL,
                                   note="pulse frame of the glow, radius 6.4; alternate with lamp_glow_on at about 600 ms each"))
    desk_maps = [(WOOD_S, S["wood"]), (GLASS_S, S["glass"]), (STONE_S, S["floor"]), (GREEN_S, S["foliage"])]
    for nm in ("desk_a", "desk_b"):
        pieces.append(from_orientation(atlas, nm, nm, desk_maps,
                                       note="two-cell sand bench with monitor, keyboard, paper and a small mint-lit plant (a and b differ only in the plant leaves); the chair is a separate entry"))
    pieces.append(from_orientation(atlas, "chair", "chair", [(CORAL_S, S["glass"])],
                                   note="cobalt task chair seen from above; place 11 px right and 18 px below a desk origin"))
    for nm in ("pot_plant_a", "pot_plant_b"):
        pieces.append(from_orientation(atlas, nm, nm, [(GREEN_S, S["foliage"])],
                                       note="slate planter with a circuit-lit mint plant (device ramp, not living foliage); two leaf layouts. Use sparingly"))
    return pieces


# ------------------------------------------------------------------ 2. shared pieces, captured

def shared_pieces():
    out = []
    sx, sy = 64, 64
    note_shelf = "{n}-cell parts shelving: cobalt frame, bays of orange, steel, porcelain and sand bins in clusters, kick plate"
    out.append(ok.make("shelf_1x1", lambda r: sp.shelf(r, sx, sy, 1, PAL, 3), (sx, sy + sp.SHELF_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note=note_shelf.format(n=1), tags=["shelf", "parts"]))
    for nm, seed in (("shelf_2x1_a", 1), ("shelf_2x1_b", 2)):
        out.append(ok.make(nm, lambda r, seed=seed: sp.shelf(r, sx, sy, 2, PAL, seed), (sx, sy + sp.SHELF_H - 16), (2, 1), ["11"],
                           "rear_prop", "prop", y_sort=True, note=note_shelf.format(n=2) + "; a and b differ only in the bin layout",
                           tags=["shelf", "parts"]))
    out.append(ok.make("partition_1x1", lambda r: sp.partition(r, sx, sy, 1, PAL), (sx, sy + sp.PART_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note="free-standing cobalt glass partition, one cell: dark frame with lit cap, pane, one reflection band, floor rail",
                       tags=["partition", "glass"]))
    out.append(ok.make("partition_2x1", lambda r: sp.partition(r, sx, sy, 2, PAL), (sx, sy + sp.PART_H - 16), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True, note="free-standing cobalt glass partition, two cells, with a middle post and a reflection band per pane",
                       tags=["partition", "glass"]))
    out.append(ok.make("terminal_desk", lambda r: sp.terminal_desk(r, sx, sy + 8, PAL), (sx, sy + 8), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True,
                       note="two-cell console desk: steel-blue top, cobalt face, ink terminal housing first, then a cobalt screen with one body step and one lit step, a one-step glow on the desk top, keyboard and card reader",
                       tags=["terminal", "desk", "interact"]))
    out.append(ok.make("cabinet_1x1", lambda r: sp.cabinet(r, sx, sy, 1, PAL), (sx, sy + sp.CAB_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note="cool-sand tool locker, one cell: paper stack on the top plane, three drawers with steel label plates",
                       tags=["cabinet", "locker"]))
    out.append(ok.make("cabinet_2x1", lambda r: sp.cabinet(r, sx, sy, 2, PAL), (sx, sy + sp.CAB_H - 16), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True, note="cool-sand tool locker, two cells wide", tags=["cabinet", "locker"]))
    return out


# ------------------------------------------------------------------ 3a. route arrows (cobalt, inlaid)

def route_arrows():
    a = np.zeros((16, 16, 4), np.uint8)

    def px(x, y, c):
        a[y, x, :3] = c
        a[y, x, 3] = 255
    for x in range(3, 10):          # shaft
        px(x, 7, GLASS[2])
        px(x, 8, GLASS[1])
    for i in range(5):              # head, tip to the right
        for y in range(3 + i, 13 - i):
            px(10 + i, y, GLASS[1])
    for i in range(5):              # lit upper edge of the head
        px(10 + i, 3 + i, GLASS[2])
    east = ok.Piece("route_arrow_e", a, (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                    note="cobalt wayfinding arrow inlaid in the floor, pointing east; Systems wayfinding uses the glass ramp, safety orange stays on warning trim",
                    tags=["wayfinding", "route"])
    north = ok.Piece("route_arrow_n", np.rot90(a, 1).copy(), (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                     note="the same arrow pointing north", tags=["wayfinding", "route"])
    return [east, north]


# ------------------------------------------------------------------ 3b. floor conduit channels

def channel_pixels(arms, fam, lit, x0=0, y0=0, n=16, band=(4, 12), core=(6, 10)):
    """RGBA 16x16 of a flush floor channel with a conduit in family colour `fam`.

    arms: subset of "NESW". A steel trench (8 px wide) with a lit-left/top rim, and a 4 px conduit
    core: unlit it is the family's two darker steps, lit it is its two lighter steps. Drawn on a
    3x3-tile canvas so arms that leave the tile are shaded as continuing, then cropped."""
    ramp = FAMILIES[fam]
    N = 3 * n
    trench = np.zeros((N, N), bool)
    pipe = np.zeros((N, N), bool)
    b0, b1 = band
    c0, c1 = core
    o = n
    trench[o + b0:o + b1, o + b0:o + b1] = True
    pipe[o + c0:o + c1, o + c0:o + c1] = True
    if "E" in arms:
        trench[o + b0:o + b1, o + b0:] = True
        pipe[o + c0:o + c1, o + c0:] = True
    if "W" in arms:
        trench[o + b0:o + b1, :o + b1] = True
        pipe[o + c0:o + c1, :o + c1] = True
    if "N" in arms:
        trench[:o + b1, o + b0:o + b1] = True
        pipe[:o + c1, o + c0:o + c1] = True
    if "S" in arms:
        trench[o + b0:, o + b0:o + b1] = True
        pipe[o + c0:, o + c0:o + c1] = True
    inner = trench & shifted(trench, 1, 0) & shifted(trench, -1, 0) & shifted(trench, 0, 1) & shifted(trench, 0, -1)
    edge = trench & ~inner
    rim = (shifted(trench, 1, 0) | shifted(trench, -1, 0) | shifted(trench, 0, 1) | shifted(trench, 0, -1)) & ~trench
    rim_tl = rim & (shifted(trench, 1, 0) | shifted(trench, 0, 1))      # the trench lies to the right or below: shadow side
    img = np.zeros((N, N, 3), np.uint8)
    paint = np.zeros((N, N), bool)

    def put(m, c):
        img[m] = c
        paint[m] = True
    put(rim, FLOOR[2])
    put(rim_tl, FLOOR[0])
    put(edge, WALL[1])
    put(inner, WALL[0])
    # the conduit core
    up, lf = ~shifted(pipe, 0, -1), ~shifted(pipe, -1, 0)
    dn, rt = ~shifted(pipe, 0, 1), ~shifted(pipe, 1, 0)
    if lit:
        put(pipe, ramp[2])
        put(pipe & (up | lf), ramp[3])
        put(pipe & (dn | rt) & ~(up | lf), ramp[1])
    else:
        put(pipe, ramp[1])
        put(pipe & (dn | rt), ramp[0])
    # clamp collars on straight runs: two px wide, steel with a lit top/left row
    straight = arms == "EW"
    vstraight = arms == "NS"
    if straight:
        put(_rect(N, o + 7, o + 5, o + 9, o + 11), WALL[2])
        put(_rect(N, o + 7, o + 5, o + 9, o + 6), WALL[3])
        put(_rect(N, o + 7, o + 10, o + 9, o + 11), WALL[1])
    if vstraight:
        put(_rect(N, o + 5, o + 7, o + 11, o + 9), WALL[2])
        put(_rect(N, o + 5, o + 7, o + 6, o + 9), WALL[3])
        put(_rect(N, o + 10, o + 7, o + 11, o + 9), WALL[1])
    crop = (slice(o, o + n), slice(o, o + n))
    rgba = np.zeros((n, n, 4), np.uint8)
    rgba[:, :, :3] = img[crop]
    rgba[:, :, 3] = np.where(paint[crop], 255, 0)
    return rgba


def _rect(N, x0, y0, x1, y1):
    m = np.zeros((N, N), bool)
    m[y0:y1, x0:x1] = True
    return m


CONDUIT_SHAPES = {"h": "EW", "v": "NS", "ne": "NE", "nw": "NW"}
CONDUIT_DESC = {"h": "straight, east-west", "v": "straight, north-south",
                "ne": "corner: arms north and east", "nw": "corner: arms north and west"}
FAM_DESC = {"cobalt": "cobalt (payroll)", "mint": "mint (alarm)", "orange": "orange (formula and bridge)"}


def conduit_pieces():
    out = []
    for fam in FAMILIES:
        for shape, arms in CONDUIT_SHAPES.items():
            for lit in (False, True):
                name = f"conduit_{shape}_{fam}" + ("_lit" if lit else "")
                rgba = channel_pixels(arms, fam, lit)
                out.append(ok.Piece(name, rgba, (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                                    note=f"flush floor channel, {CONDUIT_DESC[shape]}: steel trench with a {FAM_DESC[fam]} conduit, "
                                         + ("LIT: the conduit core in the family's two lighter steps (the circuit is complete)" if lit
                                            else "UNLIT: the core in the family's two darker steps"),
                                    tags=["conduit", fam, "lit" if lit else "unlit", shape]))
    return out


def conduit_anims():
    anims = {}
    for fam in FAMILIES:
        for shape in CONDUIT_SHAPES:
            nm = f"conduit_{shape}_{fam}"
            anims[nm] = {"kind": "state_set", "default": "off",
                         "states": {"off": {"entries": [nm]}, "lit": {"entries": [nm + "_lit"]}},
                         "play": ["off", "lit"], "ms_per_frame": 150,
                         "note": "swap to lit when the circuit it carries is completed; light a run of segments one per ~150 ms from the hub outward"}
    return anims


# ------------------------------------------------------------------ 3c. server racks, status board, bridge

RACK_H = 28


def rack(r, x0, y0, cells, seed):
    """Server rack seen from the high overhead camera: cobalt top plane, a front face with four porcelain
    blades per cell (mint status lights, a few orange warnings), one patch row with hanging cables in the
    three conduit-family colours, uprights and a kick plate. Body y0..y0+27; contact shadow below."""
    import random
    G = GLASS
    w, h = 16 * cells, RACK_H
    r.cast(x0, x0 + w, y0 + h)
    body = r.mask(x0, y0, x0 + w, y0 + h)
    r.img[body] = G[1]
    r.rect(x0, y0 + 1, x0 + w, y0 + 2, G[3])
    r.rect(x0, y0 + 2, x0 + w, y0 + 5, G[2])
    r.rect(x0, y0 + 5, x0 + w, y0 + 6, G[1])
    for c in range(cells):                     # a cooling grille on each cell's top plane
        for gx in range(x0 + c * 16 + 3, x0 + c * 16 + 13, 2):
            r.rect(gx, y0 + 3, gx + 1, y0 + 5, G[1])
    ups = [x0 + 1, x0 + w - 3] + ([x0 + w // 2 - 1] if cells == 2 else [])
    for ux in ups:
        r.rect(ux, y0 + 6, ux + 2, y0 + h - 3, G[0])
        r.rect(ux, y0 + 6, ux + 1, y0 + h - 3, G[2])
    segs = [(x0 + 3, x0 + w - 3)] if cells == 1 else [(x0 + 3, x0 + w // 2 - 1), (x0 + w // 2 + 1, x0 + w - 3)]
    rnd = random.Random(seed)
    for si, (sx0, sx1) in enumerate(segs):
        r.rect(sx0, y0 + 6, sx1, y0 + h - 3, INK[1])
        patch_row = rnd.randrange(1, 4)
        for k in range(4):
            by = y0 + 7 + 5 * k
            if k == patch_row:             # patch panel: a row of sockets, three cables hanging
                r.rect(sx0, by, sx1, by + 4, WALL[0])
                r.rect(sx0, by, sx1, by + 1, WALL[1])
                for i, fam in enumerate(("cobalt", "mint", "orange")):
                    cx = sx0 + 1 + i * 3
                    if cx + 1 > sx1:
                        break
                    r.rect(cx, by + 1, cx + 1, by + 3, INK[0])
                    ramp = FAMILIES[fam]
                    r.rect(cx, by + 3, cx + 1, by + 5, ramp[2])
                    r.rect(cx, by + 3, cx + 1, by + 4, ramp[3])
                continue
            r.rect(sx0, by, sx1, by + 4, FLOOR[2])        # porcelain blade
            r.rect(sx0, by, sx1, by + 1, FLOOR[3])
            r.rect(sx0, by + 3, sx1, by + 4, FLOOR[1])
            lx = sx0 + 1
            for j in range(2):                              # status lights
                col = MINT[3] if rnd.random() < 0.8 else ORANGE[2]
                if rnd.random() < 0.15:
                    col = MINT[1]
                r.img[by + 1, lx + 2 * j] = col
            for vx in range(sx0 + 5, sx1 - 1, 2):           # vent slits
                r.img[by + 1, vx] = FLOOR[0]
                r.img[by + 2, vx] = FLOOR[0]
    r.rect(x0 + 1, y0 + h - 3, x0 + w - 1, y0 + h, G[0])
    r.rect(x0 + 1, y0 + h - 3, x0 + w - 1, y0 + h - 2, G[1])
    r.outline(body)


def status_board(r, x0, y0):
    """Wall-mounted status board, 48 x 22 px: ink frame with a cobalt rim, a porcelain label strip and six
    indicator lights in the three family colours (two each), the fixture of the alarm hall."""
    w, h = 48, 22
    body = r.mask(x0, y0, x0 + w, y0 + h)
    r.img[body] = GLASS[0]
    r.rect(x0, y0, x0 + w, y0 + 1, GLASS[3])
    r.rect(x0, y0 + 1, x0 + w, y0 + 2, GLASS[2])
    r.rect(x0, y0 + 2, x0 + 1, y0 + h - 1, GLASS[2])
    r.rect(x0 + 2, y0 + 3, x0 + w - 2, y0 + h - 2, INK[1])
    r.rect(x0 + 3, y0 + 4, x0 + w - 3, y0 + 8, FLOOR[2])       # label strip
    r.rect(x0 + 3, y0 + 4, x0 + w - 3, y0 + 5, FLOOR[3])
    for i in range(6):
        lx = x0 + 5 + i * 7
        r.rect(lx, y0 + 6, lx + 5, y0 + 7, INK[2])            # inked pictogram line
        r.img[y0 + 6, lx + 2] = INK[0]
    fams = ("cobalt", "cobalt", "mint", "mint", "orange", "orange")
    for i, fam in enumerate(fams):
        lx = x0 + 5 + i * 7
        ramp = FAMILIES[fam]
        r.rect(lx - 1, y0 + 10, lx + 6, y0 + 18, INK[0])
        r.rect(lx, y0 + 11, lx + 5, y0 + 17, ramp[2])
        r.rect(lx, y0 + 11, lx + 5, y0 + 12, ramp[3])
        r.rect(lx, y0 + 16, lx + 5, y0 + 17, ramp[1])
        r.img[y0 + 12, lx + 1] = FLOOR[3]
    r.outline(body)


def bridge_deck(r, x0, y0):
    """Glass-bridge deck tile: slatted steel grating (porcelain-blue), lit left and top rows."""
    r.rect(x0, y0, x0 + 16, y0 + 16, FLOOR[1])
    for yy in range(0, 16, 4):
        r.rect(x0, y0 + yy, x0 + 16, y0 + yy + 1, FLOOR[2])
        for xx in range(1 + (yy // 4 % 2) * 2, 16, 4):
            r.rect(x0 + xx, y0 + yy + 2, x0 + xx + 2, y0 + yy + 3, INK[3])
    r.rect(x0, y0, x0 + 1, y0 + 16, FLOOR[3])
    r.rect(x0 + 15, y0, x0 + 16, y0 + 16, FLOOR[0])


BRAIL_H = 24


def bridge_rail(r, x0, y0):
    """Glass balustrade on the deck edge, one cell: orange top rail with a lit upper row, end posts with
    orange caps, a cobalt glass pane with one reflection band, a steel kerb. Body y0..y0+23."""
    r.cast(x0, x0 + 16, y0 + BRAIL_H, rows=1)
    body = r.mask(x0, y0, x0 + 16, y0 + BRAIL_H)
    r.img[body] = GLASS[2]
    r.rect(x0, y0, x0 + 16, y0 + 3, ORANGE[2])           # top rail
    r.rect(x0, y0, x0 + 16, y0 + 1, ORANGE[3])
    r.rect(x0, y0 + 2, x0 + 16, y0 + 3, ORANGE[1])
    pane = r.mask(x0 + 2, y0 + 4, x0 + 14, y0 + 20)
    r.img[pane] = GLASS[1]
    r.img[pane & (r.y >= y0 + 14)] = GLASS[0]
    band = pane & (np.abs((r.x - x0 - 2) - (r.y - y0 - 4) * 0.8 - 3) < 1.6)
    r.img[band] = GLASS[3]
    for px_ in (x0, x0 + 14):                             # posts
        r.rect(px_, y0 + 3, px_ + 2, y0 + 21, WALL[1])
        r.rect(px_, y0 + 3, px_ + 1, y0 + 21, WALL[2])
    r.rect(x0, y0 + 20, x0 + 16, y0 + 24, WALL[0])       # kerb
    r.rect(x0, y0 + 20, x0 + 16, y0 + 21, WALL[1])
    r.outline(body)


def racks_and_wall_pieces():
    out = []
    sx, sy = 64, 64
    note = "{n}-cell server rack: cobalt top plane with cooling grille, porcelain blades with mint status lights and a few orange warnings, one patch row with three family-colour cables, kick plate"
    out.append(ok.make("rack_1x1", lambda r: rack(r, sx, sy, 1, 5), (sx, sy + RACK_H - 16), (1, 1), ["1"], "rear_prop", "prop", y_sort=True,
                       note=note.format(n=1), tags=["rack", "server"]))
    for nm, seed in (("rack_2x1_a", 7), ("rack_2x1_b", 11)):
        out.append(ok.make(nm, lambda r, seed=seed: rack(r, sx, sy, 2, seed), (sx, sy + RACK_H - 16), (2, 1), ["11"], "rear_prop", "prop", y_sort=True,
                           note=note.format(n=2) + "; a and b differ only in the blade and patch layout", tags=["rack", "server"]))
    out.append(ok.make("status_board", lambda r: status_board(r, sx, sy), (sx, sy), (3, 2), ["000", "000"], "rear_wall", "wall", shadow=False,
                       note="wall-mounted status board, 48x22 px: cobalt rim, porcelain label strip and six indicator lights in the three family colours. Place on the north wall face; the plain wall already blocks",
                       tags=["wall", "alarm", "board"]))
    out.append(ok.make("bridge_deck", lambda r: bridge_deck(r, sx, sy), (sx, sy), (1, 1), ["0"], "floor_marking", "tile", shadow=False,
                       note="glass-bridge and service-walkway deck tile: slatted grating. Walkable. Tiles in both directions",
                       tags=["bridge", "walkway", "floor"]))
    out.append(ok.make("bridge_rail", lambda r: bridge_rail(r, sx, sy), (sx, sy + BRAIL_H - 16), (1, 1), ["1"], "rear_prop", "prop", y_sort=True,
                       note="glass balustrade for a bridge or walkway edge, one cell: orange top rail, post at each end, cobalt pane, steel kerb. Blocks its cell",
                       tags=["bridge", "rail", "edge"]))
    return out


# ------------------------------------------------------------------ 4. landmark: the routing machine

OX, OY = 16, 8           # capture position of the 160 x 144 box in the 320 x 192 room
BOX_W, BOX_H = 160, 144
FP = (32, 40)            # footprint origin inside the box: 6 x 4 cells (96 x 64 px)
FP_CELLS = (6, 4)
FX, FY = OX + FP[0], OY + FP[1]   # footprint origin in room pixels (48, 48)
W_M = 96                 # machine width
DOME = (48, 18, 17, 12)  # centre x, y (relative to the footprint origin), radii of the housing ring
CORE = (48, 18, 13, 8.5)
NODE_X = [11 + 8 * i for i in range(10)]
WELL_W = (6, 28)         # west port well, x range
WELL_E = (68, 90)        # east port well
HATCH = (34, 62)         # false panel x range (face recess y 49..60)
STUB_W_X, STUB_E_X = 9, 71   # tile left edge of the floor stubs under the two wells, relative to the footprint origin
STUB_LEN = 12


class Q:
    """Drawing helper: coordinates relative to the machine's footprint origin."""

    def __init__(self, r, keep=None):
        self.r = r
        self.keep = keep

    def rect(self, x0, y0, x1, y1, c):
        self.r.rect(FX + x0, FY + y0, FX + x1, FY + y1, c)

    def mask(self, x0, y0, x1, y1):
        return self.r.mask(FX + x0, FY + y0, FX + x1, FY + y1)

    def disc(self, cx, cy, rx, ry=None):
        return self.r.disc(FX + cx, FY + cy, rx, ry)

    def paint(self, m, c):
        self.r.img[m] = c

    def px(self, x, y, c):
        self.r.img[FY + y, FX + x] = c

    def outline(self, m, c=None):
        self.r.outline(m, c)


def _lit_edge(m, k=2):
    return m & ~(shifted(m, -1, -1) & shifted(m, -2, -2)) if k == 2 else m & ~shifted(m, -1, -1)


def _dark_edge(m):
    return m & ~(shifted(m, 1, 1) & shifted(m, 2, 2))


def draw_machine(r):
    """The routing machine's static body: a cobalt chassis with porcelain service hatches, a glass dome
    housing (the core part fills it), ten node sockets, three recesses, a hazard-striped base."""
    q = Q(r)
    G = GLASS
    r.cast(FX, FX + W_M, FY + 64, rows=3)
    body = q.mask(0, 0, W_M, 64)
    q.paint(body, G[1])
    # top plane (y 0..38): cobalt, lit rim on the upper and left edges, shaded right and lower edges
    q.rect(0, 0, W_M, 38, G[2])
    q.rect(0, 0, W_M, 1, G[3])
    q.rect(0, 0, 1, 38, G[3])
    q.rect(1, 1, W_M - 1, 2, G[3])
    q.rect(W_M - 2, 1, W_M - 1, 37, G[1])
    q.rect(1, 36, W_M - 1, 37, G[1])
    q.rect(0, 37, W_M, 38, G[0])
    # panel seams and bolts on the top plane
    for sx_ in (29, 67):
        q.rect(sx_, 8, sx_ + 1, 35, G[1])
        q.rect(sx_ + 1, 8, sx_ + 2, 35, G[3])
    q.rect(3, 33, 29, 34, G[1])
    q.rect(3, 34, 29, 35, G[3])
    q.rect(68, 33, 93, 34, G[1])
    q.rect(68, 34, 93, 35, G[3])
    for bx, by in ((3, 9), (3, 30), (26, 34), (93, 9), (93, 30), (70, 34)):
        q.px(bx, by, G[0])
    # rear vents
    for vx in range(18, 78, 4):
        q.rect(vx, 3, vx + 2, 7, G[1])
        q.rect(vx, 3, vx + 2, 4, G[0])
    # porcelain service hatches either side of the dome
    for hx0, hx1 in ((6, 26), (70, 90)):
        q.rect(hx0, 10, hx1, 32, FLOOR[2])
        q.rect(hx0, 10, hx1, 11, FLOOR[3])
        q.rect(hx0, 10, hx0 + 1, 32, FLOOR[3])
        q.rect(hx0, 31, hx1, 32, FLOOR[1])
        q.rect(hx1 - 1, 10, hx1, 32, FLOOR[1])
        for yy in range(13, 22, 3):                                # louvres
            q.rect(hx0 + 3, yy, hx1 - 3, yy + 1, FLOOR[1])
        q.rect(hx0 + 5, 24, hx1 - 5, 29, INK[1])                   # recessed handle bay
        q.rect(hx0 + 5, 24, hx1 - 5, 25, INK[0])
        q.rect(hx0 + 7, 26, hx1 - 7, 28, FLOOR[3])
        q.rect(hx0 + 7, 27, hx1 - 7, 28, FLOOR[1])
        for bx, by in ((hx0 + 1, 11), (hx1 - 2, 11), (hx0 + 1, 30), (hx1 - 2, 30)):
            q.px(bx, by, G[0])
        q.outline(q.mask(hx0, 10, hx1, 32), G[0])
    q.rect(72, 12, 80, 14, ORANGE[2])                              # warning plate on the right hatch
    q.rect(72, 12, 80, 13, ORANGE[3])
    q.rect(74, 13, 78, 14, INK[0])
    # dome housing: porcelain ring around the core
    cx, cy, rx, ry = DOME
    outer = q.disc(cx, cy, rx, ry)
    core = q.disc(CORE[0], CORE[1], CORE[2], CORE[3])
    ring = outer & ~core
    q.paint(ring, FLOOR[2])
    q.paint(_lit_edge(ring), FLOOR[3])
    q.paint(_dark_edge(ring), FLOOR[1])
    q.outline(outer)
    around = (shifted(core, 1, 0) | shifted(core, -1, 0) | shifted(core, 0, 1) | shifted(core, 0, -1)) & ~core
    q.paint(around, INK[0])
    # face (y 38..64)
    q.rect(0, 38, W_M, 39, G[2])
    q.rect(0, 39, W_M, 64, G[1])
    q.rect(0, 38, 1, 64, G[3])
    for px_ in (0, W_M - 4):                                        # corner posts
        q.rect(px_, 38, px_ + 4, 64, G[0])
        q.rect(px_ + 1, 39, px_ + 2, 61, G[2])
    q.rect(W_M - 5, 39, W_M - 4, 61, G[1])
    # node strip
    q.rect(7, 40, 89, 47, FLOOR[2])
    q.rect(7, 40, 89, 41, FLOOR[3])
    q.rect(7, 46, 89, 47, FLOOR[1])
    q.outline(q.mask(7, 40, 89, 47), G[0])
    for sx in NODE_X:
        q.rect(sx - 1, 41, sx + 3, 46, INK[0])
        q.rect(sx, 42, sx + 2, 45, INK[1])
    # three recesses: west port, false panel, east port
    for x0, x1 in (WELL_W, (HATCH[0], HATCH[1]), WELL_E):
        q.rect(x0, 49, x1, 60, INK[1])
        q.outline(q.mask(x0, 49, x1, 60), INK[0])
    for sx in (31, 65):                                             # seams between the recesses
        q.rect(sx, 48, sx + 1, 61, G[0])
        q.rect(sx + 1, 48, sx + 2, 61, G[2])
    # hazard base: safety orange and ink stripes
    for yy in (61, 62):
        for xx in range(4, W_M - 4):
            q.px(xx, yy, ORANGE[2] if ((xx + yy) // 3) % 2 == 0 else INK[1])
    q.outline(body)
    # mast for the beacon (the lamp head is a state part)
    q.rect(12, -2, 14, 6, INK[1])
    q.rect(12, -2, 13, 6, INK[2])
    q.rect(10, 4, 16, 8, INK[0])
    q.rect(11, 4, 15, 7, INK[1])


def draw_core(r, state):
    """Dome interior: a dark cobalt field with a hub, a ring and three spokes, one per conduit family. Before:
    traces barely visible; after: every trace lit in its family colour and the hub bright."""
    q = Q(r)
    cx, cy, rx, ry = CORE
    core = q.disc(cx, cy, rx, ry)
    q.paint(core, GLASS[0])
    ring = q.disc(cx, cy, 8.5, 5.5) & ~q.disc(cx, cy, 7.5, 4.6)
    spokes = {"west": q.mask(37, 17, 44, 19), "east": q.mask(53, 17, 60, 19), "north": q.mask(47, 6, 49, 13)}
    fam_ramp = {"west": MINT, "east": GLASS, "north": ORANGE}
    nodes = {"west": (36, 17), "east": (59, 17), "north": (47, 6)}
    if state == "before":
        q.paint(ring & core, GLASS[1])
        for k, m in spokes.items():
            q.paint(m & core, fam_ramp[k][0])
        for k, (nx, ny) in nodes.items():
            q.paint(q.mask(nx, ny, nx + 2, ny + 2) & core, fam_ramp[k][0])
        q.paint(q.mask(46, 17, 50, 21) & core, GLASS[1])
    else:
        q.paint(ring & core, MINT[1])
        for k, m in spokes.items():
            q.paint(m & core, fam_ramp[k][2])
        for k, (nx, ny) in nodes.items():
            q.paint(q.mask(nx, ny, nx + 2, ny + 2) & core, fam_ramp[k][3])
        q.paint(q.mask(45, 16, 51, 22) & core, MINT[2])
        q.paint(q.mask(46, 17, 50, 21) & core, MINT[3])
        q.paint(q.mask(47, 18, 49, 20) & core, FLOOR[3])
    # glass reflection, both states: two hard steps on the upper left
    for (x, y), c in (((38, 11), GLASS[3]), ((39, 10), GLASS[3]), ((40, 10), GLASS[3]), ((37, 12), GLASS[2]), ((41, 9), GLASS[2])):
        if core[FY + y, FX + x]:
            q.px(x, y, c)


def draw_nodes(r, state):
    """Ten routing nodes on the face (levels.md 12: ten individually lit nodes). Before: all dark; after: every
    node lit, mint with a pale head, and a lit step under it."""
    q = Q(r)
    for sx in NODE_X:
        if state == "before":
            q.rect(sx, 43, sx + 2, 45, MINT[0])
        else:
            q.rect(sx, 43, sx + 2, 45, MINT[3])
            q.px(sx, 43, FLOOR[3])
            q.rect(sx - 1, 41, sx + 3, 42, MINT[1])


def draw_beacon(r, state):
    """Warning beacon on the mast. Before: orange, with a one-pixel halo (the machine is alarming); after:
    steady mint without the halo (levels.md 13: the warning light steadies)."""
    q = Q(r)
    head = q.disc(13, -5, 3.6, 3.6)
    ramp = ORANGE if state == "before" else MINT
    if state == "before":
        halo = q.disc(13, -5, 6.2, 6.2) & ~q.disc(13, -5, 4.6, 4.6) & ~head
        q.paint(halo, ORANGE[1])
    q.paint(head, ramp[2])
    q.paint(head & (r.y < FY - 5) & (r.x < FX + 13), ramp[3])
    q.paint(head & (r.y > FY - 4), ramp[1])
    q.outline(head)


def draw_ports(r, state):
    """The three ports: a mint nozzle in the west well, a cobalt nozzle in the east well and an orange riser on the
    top plane. Before: the dull ramp steps. After: the lit steps with a lit step beside each flange."""
    q = Q(r)
    lit = state == "after"
    for (x0, x1), fam in ((WELL_W, "mint"), (WELL_E, "cobalt")):
        ramp = FAMILIES[fam]
        c = (x0 + x1) // 2
        q.rect(c - 7, 51, c + 7, 57, ramp[2] if lit else ramp[1])
        q.rect(c - 7, 51, c + 7, 52, ramp[3] if lit else ramp[1])
        q.rect(c - 7, 56, c + 7, 57, ramp[1] if lit else ramp[0])
        q.rect(c - 3, 53, c + 3, 55, INK[1])
        q.outline(q.mask(c - 7, 51, c + 7, 57), INK[0])
        q.rect(c - 2, 57, c + 2, 60, ramp[2] if lit else ramp[1])
        q.rect(c - 2, 57, c - 1, 60, ramp[3] if lit else ramp[1])
        if lit:
            q.rect(x0 + 1, 52, x0 + 2, 57, ramp[1])
            q.rect(x1 - 2, 52, x1 - 1, 57, ramp[1])
    # orange riser on the top plane, rising into the ceiling toward the bridge
    ramp = ORANGE
    pipe = q.mask(81, -12, 84, 6)
    q.paint(pipe, ramp[2] if lit else ramp[1])
    q.rect(81, -12, 82, 6, ramp[3] if lit else ramp[1])
    q.rect(83, -12, 84, 6, ramp[1] if lit else ramp[0])
    q.paint(q.mask(80, -13, 85, -11), INK[0])
    q.paint(q.mask(80, 5, 85, 8), INK[0])
    q.rect(81, 6, 84, 7, INK[1])
    q.outline(pipe)


def draw_stubs(r, state):
    """Floor conduit stubs leaving the west (mint) and east (cobalt) ports, the first 12 px of the run."""
    lit = state == "after"
    for tx, fam in ((STUB_W_X, "mint"), (STUB_E_X, "cobalt")):
        rgba = channel_pixels("NS", fam, lit)
        a = rgba[:STUB_LEN]
        ys, xs = np.nonzero(a[:, :, 3])
        r.img[FY + 64 + ys, FX + tx + xs] = a[ys, xs, :3]


def draw_panel(r, state):
    """The false panel under the node strip. Closed: a porcelain hatch with orange tick marks and latches. Open
    (levels.md 16: Hal pulls down a false panel): the panel hangs forward on its hinge and the cavity shows the
    Night Shift elevator stop, a lit mint plate with two doors and call arrows."""
    q = Q(r)
    x0, x1 = HATCH
    if state == "closed":
        q.rect(x0 + 1, 50, x1 - 1, 59, FLOOR[2])
        q.rect(x0 + 1, 50, x1 - 1, 51, FLOOR[3])
        q.rect(x0 + 1, 50, x0 + 2, 59, FLOOR[3])
        q.rect(x0 + 1, 58, x1 - 1, 59, FLOOR[1])
        q.rect(x1 - 2, 50, x1 - 1, 59, FLOOR[1])
        q.rect(x0 + 4, 51, x0 + 8, 52, ORANGE[2])                   # orange edge ticks
        q.rect(x1 - 8, 51, x1 - 4, 52, ORANGE[2])
        q.rect(x0 + 3, 56, x0 + 7, 58, WALL[1])                      # latches
        q.rect(x1 - 7, 56, x1 - 3, 58, WALL[1])
        q.rect(x0 + 3, 56, x0 + 7, 57, WALL[2])
        q.rect(x1 - 7, 56, x1 - 3, 57, WALL[2])
        q.rect(44, 53, 52, 56, FLOOR[3])                             # label plate
        q.rect(45, 54, 51, 55, INK[2])
    else:
        q.rect(x0 + 1, 50, x1 - 1, 59, MINT[0])                      # cavity
        q.rect(x0 + 1, 50, x1 - 1, 51, MINT[2])
        q.rect(x0 + 1, 51, x0 + 2, 59, MINT[1])
        q.rect(x1 - 2, 51, x1 - 1, 59, MINT[1])
        q.rect(40, 52, 47, 59, FLOOR[2])                             # elevator doors
        q.rect(47, 52, 54, 59, FLOOR[1])
        q.rect(40, 52, 54, 53, FLOOR[3])
        q.rect(47, 52, 48, 59, INK[0])
        q.rect(40, 52, 41, 59, FLOOR[3])
        q.rect(56, 52, 59, 53, MINT[3])                              # up and down call arrows
        q.rect(56, 55, 59, 56, MINT[3])
        q.rect(57, 56, 58, 57, MINT[3])
        q.rect(57, 53, 58, 54, MINT[3])
        # the flap, hanging forward on its hinge
        q.rect(x0 - 1, 60, x1 + 1, 67, FLOOR[1])
        q.rect(x0 - 1, 60, x1 + 1, 61, FLOOR[2])
        q.rect(x0 - 1, 66, x1 + 1, 67, FLOOR[0])
        q.outline(q.mask(x0 - 1, 60, x1 + 1, 67), INK[0])
        q.px(x0 + 1, 61, WALL[0])
        q.px(x1 - 2, 61, WALL[0])
        q.rect(x0 + 3, 63, x0 + 8, 64, ORANGE[2])
        q.rect(x1 - 8, 63, x1 - 3, 64, ORANGE[2])
        r.cast(FX + x0, FX + x1, FY + 67, rows=2)


def draw_walkway(r):
    """After: the service walkway opens along the route. A grated deck, two cells wide, with safety-orange hazard
    edges and ink posts, running east from the machine's flank."""
    q = Q(r)
    x0, x1, y0, y1 = 96, 128, 16, 48
    q.rect(x0, y0, x1, y1, FLOOR[1])
    for yy in range(y0 + 4, y1 - 4, 4):
        q.rect(x0, yy, x1, yy + 1, FLOOR[2])
        for xx in range(x0 + 1 + ((yy - y0) // 4 % 2) * 2, x1 - 2, 4):
            q.rect(xx, yy + 2, xx + 2, yy + 3, INK[3])
    for yy0 in (y0, y1 - 4):                                        # hazard bands
        for yy in range(yy0, yy0 + 4):
            for xx in range(x0, x1):
                q.px(xx, yy, ORANGE[2] if ((xx + yy) // 3) % 2 == 0 else INK[1])
    q.rect(x0, y0 + 4, x1, y0 + 5, ORANGE[1])
    q.rect(x0, y1 - 5, x1, y1 - 4, ORANGE[1])
    q.rect(x0, y0, x0 + 1, y1, FLOOR[3])
    q.outline(q.mask(x0, y0, x1, y1), INK[0])
    for py_ in (y0 + 1, y1 - 3):                                    # posts
        q.rect(x1 - 4, py_, x1 - 2, py_ + 2, INK[0])


def draw_deck_plate(r):
    """Static floor plate under the machine: a darker deck apron with orange corner trim, so the machine sits on
    its own pad and the conduits visibly leave it."""
    q = Q(r)
    x0, x1, y0, y1 = -6, W_M + 6, 6, 70
    q.rect(x0, y0, x1, y1, FLOOR[2])
    q.rect(x0, y0, x1, y0 + 1, FLOOR[0])
    q.rect(x0, y0, x0 + 1, y1, FLOOR[0])
    q.rect(x0, y1 - 1, x1, y1, FLOOR[3])
    q.rect(x1 - 1, y0, x1, y1, FLOOR[3])
    for cx_, cy_, dx, dy in ((x0, y0, 1, 1), (x1 - 1, y0, -1, 1), (x0, y1 - 1, 1, -1), (x1 - 1, y1 - 1, -1, -1)):
        for i in range(5):
            q.px(cx_ + dx * i, cy_, ORANGE[2])
            q.px(cx_, cy_ + dy * i, ORANGE[2])
            if i < 3:
                q.px(cx_ + dx * i, cy_ + dy, ORANGE[1])
                q.px(cx_ + dx, cy_ + dy * i, ORANGE[1])


def landmark_pieces():
    parts = []
    box = (OX, OY, OX + BOX_W, OY + BOX_H)
    fp_room = (FX, FY)

    def mk(name, draw, layer, collision, y_sort, note, tags, composite=None, shadow=None):
        rgba, painted = ok.cap(draw)
        outside = painted.copy()
        outside[box[1]:box[3], box[0]:box[2]] = False
        assert not outside.any(), f"{name} leaves the landmark box"
        sprite = rgba[box[1]:box[3], box[0]:box[2]].copy()
        p = ok.Piece(name, sprite, (OX, OY), fp_room, FP_CELLS, collision, layer, "landmark_part", y_sort=y_sort,
                     composite=composite, shadow=shadow, tags=["landmark", "routing machine"] + tags, note=note)
        parts.append(p)
        return p

    full = ["111111"] * 4
    zero = ["000000"] * 4
    mk("routing_deck_plate", draw_deck_plate, "floor_marking", zero, False,
       "floor pad under the machine: porcelain apron with orange corner trim", ["floor", "base"])
    mk("routing_stubs_before", lambda r: draw_stubs(r, "before"), "floor_marking", zero, False,
       "before: the first 12 px of the mint (west) and cobalt (east) floor conduits, unlit", ["quest state", "before", "conduit"])
    mk("routing_stubs_after", lambda r: draw_stubs(r, "after"), "floor_marking", zero, False,
       "after: the same two stubs, lit", ["quest state", "after", "conduit"])
    mk("routing_walkway_after", draw_walkway, "floor_marking", zero, False,
       "after: the service walkway opens along the route: grated deck, orange hazard edges, ink posts. Walkable", ["quest state", "after", "walkway"])
    mk("routing_machine", draw_machine, "rear_prop", full, True,
       "the routing machine's body: cobalt chassis, porcelain service hatches, dome housing, ten node sockets, three face recesses, "
       "hazard-striped base, beacon mast, cast shadow. Carries the collision of the whole machine (6x4 cells)",
       ["machine", "base"], shadow=(1, 104, 97, 3))
    mk("routing_core_before", lambda r: draw_core(r, "before"), "rear_prop", zero, True,
       "before: the dome shows a dark field with the hub, ring and three spokes barely visible", ["quest state", "before", "core"])
    mk("routing_core_after", lambda r: draw_core(r, "after"), "rear_prop", zero, True,
       "after: every trace lit in its family colour (mint west, cobalt east, orange north) and a bright hub", ["quest state", "after", "core"])
    mk("routing_nodes_before", lambda r: draw_nodes(r, "before"), "rear_prop", zero, True,
       "before: ten routing nodes dark", ["quest state", "before", "nodes"])
    mk("routing_nodes_after", lambda r: draw_nodes(r, "after"), "rear_prop", zero, True,
       "after: ten routing nodes lit mint with a pale head (levels.md 12)", ["quest state", "after", "nodes"])
    mk("routing_beacon_before", lambda r: draw_beacon(r, "before"), "rear_prop", zero, True,
       "before: orange warning beacon with a halo (the alarm)", ["quest state", "before", "beacon"])
    mk("routing_beacon_after", lambda r: draw_beacon(r, "after"), "rear_prop", zero, True,
       "after: the beacon steady mint, no halo (levels.md 13)", ["quest state", "after", "beacon"])
    mk("routing_ports_before", lambda r: draw_ports(r, "before"), "rear_prop", zero, True,
       "before: mint and cobalt nozzles in the face wells and the orange riser on the top plane, in their dull steps", ["quest state", "before", "ports"])
    mk("routing_ports_after", lambda r: draw_ports(r, "after"), "rear_prop", zero, True,
       "after: the same three ports in their lit steps", ["quest state", "after", "ports"])
    mk("routing_panel_closed", lambda r: draw_panel(r, "closed"), "rear_prop", zero, True,
       "before: the false panel, a porcelain hatch with orange ticks and latches", ["quest state", "before", "panel"])
    mk("routing_panel_open", lambda r: draw_panel(r, "open"), "rear_prop", zero, True,
       "after: the panel hangs forward and the cavity reveals the Night Shift elevator stop (levels.md 16)", ["quest state", "after", "panel"])
    return parts


LAMP_OFFSETS = [[-22, 2], [-22, 34], [-6, 60], [106, 60]]


def landmarks():
    common = ["routing_deck_plate", "routing_machine"]
    before = ["routing_deck_plate", "routing_stubs_before", "routing_machine", "routing_core_before", "routing_nodes_before",
              "routing_beacon_before", "routing_ports_before", "routing_panel_closed"]
    after = ["routing_deck_plate", "routing_stubs_after", "routing_walkway_after", "routing_machine", "routing_core_after",
             "routing_nodes_after", "routing_beacon_after", "routing_ports_after", "routing_panel_open"]
    assert set(common) <= set(before) & set(after)
    roles = {"routing_deck_plate": "floor pad", "routing_machine": "base machine"}
    for n in before + after:
        roles.setdefault(n, "quest state")
    roles["lamp"] = "light accents"
    return {
        "routing_machine": {
            "note": "Systems landmark: the large routing machine. Every part is a full-size sprite registered at one footprint origin, "
                    "so a state is a list of parts; place them all at the same cell. The body carries the collision (6x4 cells); the stubs and "
                    "walkway are floor markings; the other parts are small quest-state overlays.",
            "size_px": [BOX_W, BOX_H],
            "footprint_origin_px": list(FP),
            "default_state": "before",
            "states": {
                "before": {"parts": before, "lamps": {"anim": "lamp", "state": "on", "offsets_px": LAMP_OFFSETS}},
                "after": {"parts": after, "lamps": {"anim": "lamp", "state": "pulse", "offsets_px": LAMP_OFFSETS}},
            },
            "part_roles": roles,
            "changes_after": [
                "the ten routing nodes on the face light up (levels.md 12: ten individually lit routing nodes)",
                "the dome core lights every circuit trace in its conduit family: mint, cobalt and orange (levels.md 16: the machine lights in an intelligible sequence)",
                "the warning beacon steadies from orange with a halo to calm mint (levels.md 13: the machine's warning light steadies)",
                "the port nozzles, the orange riser and the two floor conduit stubs switch from dull to lit (levels.md 12, 16: each correct node lights a conduit)",
                "a grated service walkway with orange hazard edges opens along the route (levels.md 16: a service walkway opens)",
                "the false panel drops open and reveals the Night Shift elevator stop (levels.md 16: Hal pulls down a false panel)",
                "all four lamps switch from the steady glow to the wider pulse glow",
            ],
        }
    }


# ------------------------------------------------------------------ 5. quest props (levels 12 to 16 and Mira's routes after 13 and 16)
# Audit: QUEST_PROP_AUDIT.md (rows S1 to S25). Systems ramps only; safety orange stays trim, mint is circuit light.

QUEST_NAMES = set()
QS = (64, 64)   # capture origin for every quest prop


def _quest(name, draw, fp, cells, collision, layer, kind, note, tags, y_sort=True, shadow=True, box=None):
    p = ok.make(name, draw, fp, cells, collision, layer, kind, box=box, shadow=shadow, y_sort=y_sort, note=note, tags=tags)
    QUEST_NAMES.add(name)
    return p


def _key(r, x, y, lit):
    """One keypad node, 4 x 3: dark glass, or a mint-lit node with a pale head."""
    r.rect(x - 1, y - 1, x + 5, y + 4, INK[0])
    if lit:
        r.rect(x, y, x + 4, y + 3, MINT[2])
        r.rect(x, y, x + 2, y + 1, MINT[3])
    else:
        r.rect(x, y, x + 4, y + 3, GLASS[1])
        r.rect(x, y, x + 4, y + 1, GLASS[2])


def draw_payroll_keypad(r, x0, y0, n_lit):
    """The relocated payroll keypad of level 12, 2 cells wide: a glass-backed ID tray (five cards behind a cobalt pane),
    a steel top plane with ten key nodes in two rows, a cobalt face with ten progress lights. n_lit nodes are lit
    (row-major: the first row is digits 1-5, the second 6-0)."""
    r.cast(x0, x0 + 32, y0 + 30)
    r.rect(x0, y0, x0 + 32, y0 + 30, INK[0])
    r.rect(x0 + 1, y0 + 1, x0 + 31, y0 + 11, GLASS[1])                  # the ID tray's back panel
    r.rect(x0 + 2, y0 + 2, x0 + 30, y0 + 10, GLASS[2])
    for i in range(5):                                                  # five ID cards standing in the tray
        cx = x0 + 4 + i * 5
        r.rect(cx, y0 + 3, cx + 4, y0 + 10, FLOOR[3])
        r.rect(cx, y0 + 3, cx + 4, y0 + 4, FLOOR[2])
        r.rect(cx + 1, y0 + 5, cx + 3, y0 + 7, GLASS[1])                # the photo block
        r.rect(cx, y0 + 8, cx + 4, y0 + 9, ORANGE[2] if i == 2 else GLASS[2])
    for k in range(6):                                                  # one reflection band across the glass
        r.img[y0 + 2 + k, x0 + 22 + k // 2: x0 + 25 + k // 2] = GLASS[3]
    r.rect(x0 + 1, y0 + 10, x0 + 31, y0 + 11, GLASS[0])
    r.rect(x0 + 1, y0 + 12, x0 + 31, y0 + 22, WALL[2])                  # steel top plane
    r.rect(x0 + 1, y0 + 12, x0 + 31, y0 + 13, WALL[3])
    for i in range(10):
        _key(r, x0 + 4 + (i % 5) * 5 + 2, y0 + 14 + (i // 5) * 4, i < n_lit)
    r.rect(x0 + 27, y0 + 14, x0 + 30, y0 + 20, WALL[1])                 # a card slot at the right of the keys
    r.rect(x0 + 28, y0 + 15, x0 + 29, y0 + 19, INK[1])
    r.rect(x0 + 1, y0 + 22, x0 + 31, y0 + 29, GLASS[1])                 # cobalt face
    r.rect(x0 + 1, y0 + 22, x0 + 31, y0 + 23, GLASS[2])
    for i in range(10):                                                 # ten progress lights, one per node
        r.rect(x0 + 3 + i * 3, y0 + 25, x0 + 5 + i * 3, y0 + 27, MINT[3] if i < n_lit else GLASS[0])
    r.rect(x0 + 1, y0 + 28, x0 + 4, y0 + 29, ORANGE[1])                 # orange trim at the ends
    r.rect(x0 + 28, y0 + 28, x0 + 31, y0 + 29, ORANGE[1])
    r.rect(x0 + 1, y0 + 29, x0 + 31, y0 + 30, GLASS[0])
    r.outline(r.mask(x0, y0, x0 + 32, y0 + 30))


def draw_bridge_span(r, x0, y0, state):
    """The glass bridge's span of level 12, 4 x 2 cells on the floor markings: a deck tile at each end, a steel-trussed
    pit between them. retracted: the middle two cells are open pit (a service conduit shows below). extended: deck
    from end to end. Orange hazard stripes mark the two long edges either way."""
    cells_x = range(4)
    for j in range(2):
        for i in cells_x:
            if state == "extended" or i in (0, 3):
                bridge_deck(r, x0 + 16 * i, y0 + 16 * j)
    if state == "retracted":
        r.rect(x0 + 16, y0, x0 + 48, y0 + 32, INK[0])                    # the pit
        r.rect(x0 + 17, y0 + 2, x0 + 47, y0 + 30, INK[1])
        r.rect(x0 + 17, y0 + 2, x0 + 47, y0 + 4, INK[0])                 # shadow under the north lip
        for gy in (y0 + 8, y0 + 24):                                     # girders across the pit
            r.rect(x0 + 17, gy, x0 + 47, gy + 2, WALL[1])
            r.rect(x0 + 17, gy, x0 + 47, gy + 1, WALL[2])
        r.rect(x0 + 17, y0 + 14, x0 + 47, y0 + 18, GLASS[0])             # a cobalt service conduit at the bottom of the pit
        r.rect(x0 + 17, y0 + 15, x0 + 47, y0 + 17, GLASS[1])
        r.rect(x0 + 17, y0 + 15, x0 + 47, y0 + 16, GLASS[2])
        r.rect(x0 + 16, y0, x0 + 17, y0 + 32, WALL[2])                   # lit west lip
        r.rect(x0 + 47, y0, x0 + 48, y0 + 32, WALL[0])
    for k in range(0, 64, 4):                                           # hazard stripes on the long edges
        for ey in (y0, y0 + 30):
            r.rect(x0 + k, ey, x0 + k + 2, ey + 2, ORANGE[2])
            r.rect(x0 + k + 2, ey, x0 + k + 4, ey + 2, INK[0])


def draw_refund_sign(r, x0, y0, green):
    """The refund sign of level 13, a 24 x 14 wall plate. red (the ledger turned a refund into a charge): a safety-orange
    plate with a plus. green (the sign is restored): a mint plate with a minus. Systems has no pure red or green, so
    red is the orange trim ramp and green the mint circuit ramp; the glyph (plus or minus) carries the meaning."""
    body, lit, deep = (MINT[2], MINT[3], MINT[0]) if green else (ORANGE[1], ORANGE[3], ORANGE[0])
    r.rect(x0, y0, x0 + 24, y0 + 14, INK[0])
    r.rect(x0 + 1, y0 + 1, x0 + 23, y0 + 13, deep)
    r.rect(x0 + 2, y0 + 2, x0 + 22, y0 + 12, body)
    r.rect(x0 + 2, y0 + 2, x0 + 22, y0 + 3, lit)
    r.rect(x0 + 2, y0 + 2, x0 + 3, y0 + 12, lit)
    r.rect(x0 + 2, y0 + 11, x0 + 22, y0 + 12, deep)
    gx, gy = x0 + 4, y0 + 4                                               # a 7 x 7 sign glyph, porcelain with a shadow step
    bars = [(gx, gy + 2, 7, 2)] + ([] if green else [(gx + 2, gy, 2, 6)])    # a minus is one bar, a plus adds the upright
    for (bx, by, bw, bh) in bars:
        r.rect(bx + 1, by + 1, bx + bw + 1, by + bh + 1, deep)
    for (bx, by, bw, bh) in bars:
        r.rect(bx, by, bx + bw, by + bh, FLOOR[3])
    for k, ch in enumerate("85"):                                         # the amount, so the plate reads as a price tag, not a first-aid cross
        for yy, row in enumerate(qp.FONT[ch]):
            for xx, v in enumerate(row):
                if v == "X":
                    r.img[y0 + 5 + yy + 1, x0 + 13 + k * 4 + xx + 1] = deep
                    r.img[y0 + 5 + yy, x0 + 13 + k * 4 + xx] = FLOOR[3]
    r.rect(x0 + 13, y0 + 11, x0 + 21, y0 + 12, deep)


def draw_calc_display(r, x0, y0, refund):
    """The inset calculator display of level 13, 2 cells wide: a steel desk top with a display sunk into it (ink bezel,
    lit digits with the sign in front) and an open ledger beside it. charge: '+85' in orange; refund: '-85' in mint."""
    env.block(r, x0, y0, x0 + 34, y0 + 16, 5, WALL, GLASS)
    r.rect(x0 + 3, y0 + 1, x0 + 23, y0 + 10, INK[0])                      # the bezel, sunk: lit lower and right edge
    r.rect(x0 + 4, y0 + 2, x0 + 22, y0 + 9, INK[1])
    r.rect(x0 + 22, y0 + 2, x0 + 23, y0 + 10, WALL[3])
    r.rect(x0 + 3, y0 + 10, x0 + 23, y0 + 11, WALL[3])
    sign_col = MINT[3] if refund else ORANGE[3]
    qp.text(r, x0 + 6, y0 + 3, "-" if refund else "+", sign_col)
    qp.text(r, x0 + 11, y0 + 3, "85", FLOOR[3])
    r.rect(x0 + 17, y0 + 7, x0 + 21, y0 + 8, GLASS[2])                    # a unit bar
    pg = r.mask(x0 + 25, y0 + 2, x0 + 33, y0 + 11)                       # the open ledger
    r.img[pg] = FLOOR[3]
    r.rect(x0 + 29, y0 + 2, x0 + 30, y0 + 11, FLOOR[1])
    for ly in (4, 6, 8):
        r.rect(x0 + 26, y0 + ly, x0 + 29, y0 + ly + 1, GLASS[1])
    r.rect(x0 + 30, y0 + 5, x0 + 32, y0 + 8, sign_col if refund else ORANGE[2])
    r.rect(x0 + 30, y0 + 6, x0 + 32, y0 + 7, MINT[1] if refund else ORANGE[0])
    r.outline(pg)


def draw_folding_stool(r, x0, y0):
    """Hal's folding stool, 1 cell: a sand canvas seat on crossed steel legs, his orange tool roll leaning on the right."""
    r.cast(x0 + 2, x0 + 12, y0 + 15, rows=1)
    for k in range(7):                                                   # crossed legs
        r.img[y0 + 8 + k, x0 + 3 + k] = WALL[1]
        r.img[y0 + 8 + k, x0 + 10 - k] = INK[1]
    r.rect(x0 + 2, y0 + 14, x0 + 5, y0 + 15, INK[1])
    r.rect(x0 + 9, y0 + 14, x0 + 12, y0 + 15, INK[1])
    seat = r.disc(x0 + 7, y0 + 5.5, 6, 3.6)
    r.img[seat] = WOOD[2]
    r.img[seat & ~shifted(seat, -1, -1)] = WOOD[3]
    r.img[seat & ~shifted(seat, 1, 1)] = WOOD[1]
    r.rect(x0 + 5, y0 + 5, x0 + 10, y0 + 6, WOOD[1])                      # a canvas seam
    r.outline(seat)
    roll = r.mask(x0 + 11, y0 + 4, x0 + 15, y0 + 13)                      # orange tool roll
    r.img[roll] = ORANGE[2]
    r.rect(x0 + 11, y0 + 4, x0 + 12, y0 + 13, ORANGE[3])
    r.rect(x0 + 14, y0 + 4, x0 + 15, y0 + 13, ORANGE[1])
    r.rect(x0 + 11, y0 + 7, x0 + 15, y0 + 8, INK[1])                      # straps
    r.rect(x0 + 11, y0 + 10, x0 + 15, y0 + 11, INK[1])
    r.outline(roll)


ALARM_LIGHTS = [GLASS[2], MINT[2], ORANGE[2], WOOD[3], GLASS[3], MINT[3]]   # blue, green, orange, sand, pale blue, pale green
PICTO = {
    0: ("XXXXX", "XXXXX", "XXXXX", "XXXXX"),   # solid block
    1: (".XXX.", "X...X", "X...X", ".XXX."),   # ring
    2: ("..X..", ".XXX.", ".XXX.", "XXXXX"),   # triangle
    3: ("XXXXX", "X...X", "X...X", "XXXXX"),   # square
    4: ("..X..", ".X.X.", ".X.X.", "..X.."),   # diamond
    5: ("X...X", ".X.X.", "..X..", ".X.X."),   # cross
}
PICTO_ORDER = [1, 2, 3, 4, 5, 0]    # ring, triangle, square, diamond, cross, bar


def draw_alarm_strip(r, x0, y0, state):
    """The alarm hall's strip of level 14, 64 x 18: six alert cells, each a lamp above a porcelain label plate.
    merged (Pace lost the labels): six identical cobalt lamps over blank plates, so two alerts look the same.
    separated: six lamps in six hues (blue, green, orange, sand, pale blue, pale green) and six pictograms (ring, triangle,
    square, diamond, cross, bar). muted (the Quiet Alarm side quest): separated, with the sixth lamp dark and slashed."""
    r.rect(x0, y0, x0 + 64, y0 + 18, INK[0])
    r.rect(x0 + 1, y0 + 1, x0 + 63, y0 + 17, GLASS[1])
    r.rect(x0 + 1, y0 + 1, x0 + 63, y0 + 2, GLASS[3])
    r.rect(x0 + 1, y0 + 1, x0 + 2, y0 + 17, GLASS[2])
    for i in range(6):
        cx = x0 + 3 + i * 10
        merged = state == "merged"
        dark = state == "muted" and i == 5
        col = GLASS[2] if merged else (GLASS[0] if dark else ALARM_LIGHTS[i])
        r.rect(cx, y0 + 3, cx + 9, y0 + 9, INK[0])
        r.rect(cx + 1, y0 + 4, cx + 8, y0 + 8, col)
        if not dark:
            r.rect(cx + 1, y0 + 4, cx + 8, y0 + 5, GLASS[3] if merged else FLOOR[3])
            r.img[y0 + 4, cx + 1] = FLOOR[3]
        r.rect(cx, y0 + 10, cx + 9, y0 + 17, FLOOR[3])                      # the porcelain label plate
        r.rect(cx, y0 + 10, cx + 9, y0 + 11, FLOOR[2])
        r.rect(cx, y0 + 16, cx + 9, y0 + 17, FLOOR[1])
        if not merged:
            for yy, row in enumerate(PICTO[PICTO_ORDER[i]]):
                for xx, ch in enumerate(row):
                    if ch == "X":
                        r.img[y0 + 11 + yy, cx + 2 + xx] = INK[1]
        if dark:
            for k in range(4):                                                # a mute slash across the plate
                r.img[y0 + 11 + k, cx + 6 - k] = ORANGE[1]
    r.outline(r.mask(x0, y0, x0 + 64, y0 + 18))


def draw_bridge_shutter(r, x0, y0, state):
    """A shutter for the glass bridge's window (level 15), 30 x 20, drawn like the window overlay. closed: steel louvres
    cover the whole pane. open: the louvres are stacked at both sides and the cobalt pane shows."""
    r.rect(x0, y0, x0 + 30, y0 + 20, INK[0])
    r.rect(x0 + 2, y0 + 2, x0 + 28, y0 + 17, GLASS[1])
    if state == "closed":
        for k, yy in enumerate(range(y0 + 2, y0 + 17, 3)):
            r.rect(x0 + 2, yy, x0 + 28, yy + 1, WALL[3])
            r.rect(x0 + 2, yy + 1, x0 + 28, yy + 2, WALL[2])
            r.rect(x0 + 2, yy + 2, x0 + 28, yy + 3, INK[1])
        r.rect(x0 + 13, y0 + 17, x0 + 17, y0 + 18, ORANGE[2])             # the pull tag
    else:
        r.rect(x0 + 6, y0 + 2, x0 + 24, y0 + 17, GLASS[2])
        r.rect(x0 + 6, y0 + 11, x0 + 24, y0 + 17, GLASS[1])
        for k in range(8):
            r.img[y0 + 2 + k, x0 + 9 + k: x0 + 11 + k] = GLASS[3]
        for xa, xb in ((x0 + 2, x0 + 6), (x0 + 24, x0 + 28)):              # the stacked louvres
            for k, yy in enumerate(range(y0 + 2, y0 + 17, 3)):
                r.rect(xa, yy, xb, yy + 1, WALL[3])
                r.rect(xa, yy + 1, xb, yy + 3, WALL[1])
    r.rect(x0, y0 + 18, x0 + 30, y0 + 20, WALL[2])
    r.rect(x0, y0 + 18, x0 + 30, y0 + 19, WALL[3])
    r.rect(x0, y0 + 19, x0 + 30, y0 + 20, INK[0])


FORMULA_GLYPHS = "&*()_+"


def draw_formula_wall(r, x0, y0, n_lit):
    """The formula wall of level 15, 96 x 22: six clause boxes joined by traces, each holding one symbol (& * ( ) _ +)
    at double size. n_lit boxes are lit from the left (mint glyph and trace); the rest are dark glass."""
    r.rect(x0, y0, x0 + 96, y0 + 22, INK[0])
    r.rect(x0 + 1, y0 + 1, x0 + 95, y0 + 21, GLASS[0])
    r.rect(x0 + 1, y0 + 1, x0 + 95, y0 + 2, GLASS[2])
    r.rect(x0 + 1, y0 + 1, x0 + 2, y0 + 21, GLASS[2])
    for i in range(6):
        bx = x0 + 4 + i * 15
        lit = i < n_lit
        if i < 5:                                                          # the trace to the next box
            r.rect(bx + 13, y0 + 10, bx + 17, y0 + 12, MINT[2] if (lit and i + 1 < n_lit) else GLASS[1])
        r.rect(bx, y0 + 3, bx + 13, y0 + 19, INK[0])
        r.rect(bx + 1, y0 + 4, bx + 12, y0 + 18, FOLIAGE0 if lit else GLASS[1])
        if lit:
            r.rect(bx + 1, y0 + 4, bx + 12, y0 + 5, MINT[1])
            r.rect(bx + 1, y0 + 4, bx + 2, y0 + 18, MINT[1])
        qp.text(r, bx + 3, y0 + 6, FORMULA_GLYPHS[i], MINT[3] if lit else GLASS[2], scale=2)
    r.rect(x0 + 1, y0 + 21, x0 + 95, y0 + 22, INK[0])


FOLIAGE0 = MINT[0]


def decor_piece(name, kind, w, h, note, tags):
    x0, y0 = QS
    return _quest(name, lambda r: qp.mira_decor(r, kind, x0, y0, PAL), (x0 - (16 - w) // 2, y0 + h - 16), (1, 1), ["0"], "rear_prop", "prop",
                  note, tags, shadow=False)


def quest_pieces():
    """The Systems quest props. Returns (pieces, state sets)."""
    out = []
    sx, sy = QS
    for st, n in (("off", 0), ("half", 5), ("lit", 10)):
        out.append(_quest(f"payroll_keypad_{st}", lambda r, n=n: draw_payroll_keypad(r, sx, sy, n), (sx, sy + 14), (2, 1), ["11"], "rear_prop", "prop",
                          "the relocated payroll keypad of level 12, 2 x 1: a glass-backed ID tray with five cards, a steel top plane with ten key nodes, a cobalt face with ten progress lights. "
                          + {"off": "off: every node dark", "half": "half: the first five nodes (digits 1-5) lit mint", "lit": "lit: all ten nodes lit mint"}[st],
                          ["keypad", "payroll", "level 12", st], box=(sx, sy, sx + 34, sy + 32)))
    for st in ("retracted", "extended"):
        out.append(_quest(f"bridge_span_{st}", lambda r, st=st: draw_bridge_span(r, sx, sy, st), (sx, sy), (4, 2),
                          ["0110", "0110"] if st == "retracted" else ["0000", "0000"], "floor_marking", "tile",
                          "the glass bridge's span, 4 x 2 (level 12: the first completed batch extends the bridge toward Mira's chute). "
                          + ("retracted: a deck tile at each end and an open trussed pit between them with a cobalt conduit below; the two middle columns block"
                             if st == "retracted" else "extended: deck from end to end, all cells walkable")
                          + ". Orange hazard stripes on both long edges; add `bridge_rail` entries along them", ["bridge", "walkway", "level 12", st],
                          y_sort=False, shadow=False, box=(sx, sy, sx + 64, sy + 32)))
    for st in ("red", "green"):
        out.append(_quest(f"refund_sign_{st}", lambda r, st=st: draw_refund_sign(r, sx, sy, st == "green"), (sx, sy), (2, 1), ["00"], "rear_wall", "wall",
                          "the refund sign of level 13, a 24 x 14 wall plate. "
                          + ("red: a safety-orange plate with a plus, the ledger turned a refund into a charge" if st == "red"
                             else "green: a mint plate with a minus, the sign restored")
                          + ". Systems has no pure red or green: red is the orange trim ramp, green the mint circuit ramp; the glyph carries the meaning. "
                            "Place on the north wall face (the plain wall already blocks)",
                          ["sign", "refund", "level 13", st], y_sort=False, shadow=False, box=(sx, sy, sx + 24, sy + 14)))
    for st in ("charge", "refund"):
        out.append(_quest(f"calc_display_{st}", lambda r, st=st: draw_calc_display(r, sx, sy, st == "refund"), (sx, sy), (2, 1), ["11"], "rear_prop", "prop",
                          "the inset calculator display of level 13, 2 x 1: a steel desk top with a display sunk into it and an open ledger beside it. "
                          + ("charge: '+85' in orange, the ledger marked with an orange plus" if st == "charge" else "refund: '-85' in mint, the ledger marked with a mint minus"),
                          ["calculator", "display", "level 13", st], box=(sx, sy, sx + 36, sy + 18)))
    out.append(_quest("folding_stool", lambda r: draw_folding_stool(r, sx, sy), (sx, sy), (1, 1), ["1"], "rear_prop", "prop",
                      "Hal's folding stool, 1 x 1 (level 13: Hal sits instead of crouching): a sand canvas seat on crossed steel legs with his orange tool roll leaning on it",
                      ["stool", "hal", "level 13"]))
    for st in ("merged", "separated", "muted"):
        out.append(_quest(f"alarm_strip_{st}", lambda r, st=st: draw_alarm_strip(r, sx, sy, st), (sx, sy), (4, 2), ["0000", "0000"], "rear_wall", "wall",
                          "the alarm hall strip of level 14, a 64 x 18 wall overlay: six lamps above six porcelain label plates. "
                          + {"merged": "merged: six identical cobalt lamps over blank plates (Pace lost the labels, two alerts look the same)",
                             "separated": "separated: six hues (blue, green, orange, sand, pale blue, pale green) and six pictograms (ring, triangle, square, diamond, cross, bar), so colour is never the only cue",
                             "muted": "muted (Quiet Alarm): as separated, with the sixth lamp dark and slashed in orange"}[st],
                          ["alarm", "strip", "level 14", st], y_sort=False, shadow=False, box=(sx, sy, sx + 64, sy + 18)))
    for st in ("closed", "open"):
        out.append(_quest(f"bridge_shutter_{st}", lambda r, st=st: draw_bridge_shutter(r, sx, sy, st), (sx, sy), (2, 2), ["00", "00"], "rear_wall", "wall",
                          "a bridge window shutter of level 15, a 30 x 20 wall overlay like the window overlay. "
                          + ("closed: steel louvres cover the pane" if st == "closed" else "open: the louvres are stacked at both sides and the cobalt pane shows"),
                          ["shutter", "bridge", "level 15", st], y_sort=False, shadow=False, box=(sx, sy, sx + 30, sy + 20)))
    for st, n in (("dark", 0), ("half", 3), ("lit", 6)):
        out.append(_quest(f"formula_wall_{st}", lambda r, n=n: draw_formula_wall(r, sx, sy, n), (sx, sy), (6, 2), ["000000", "000000"], "rear_wall", "wall",
                          "the formula wall of level 15, a 96 x 22 wall overlay: six clause boxes joined by traces, each with one symbol (& * ( ) _ +). "
                          + {"dark": "dark: every box dark glass", "half": "half: the first three boxes and the traces between them lit mint", "lit": "lit: all six lit"}[st],
                          ["formula", "wall", "level 15", st], y_sort=False, shadow=False, box=(sx, sy, sx + 96, sy + 22)))
    for st in ("idle", "ready"):
        out.append(_quest(f"courier_chute_{st}", lambda r, st=st: qp.courier_chute(r, sx, sy, PAL, st == "ready"), (sx, sy + 12), (2, 1), ["11"], "rear_prop", "prop",
                          "Mira's courier chute, 2 x 1: a metal cabinet with a slot, a tube rising into the ceiling, a catch tray and an indicator lamp. "
                          + ("idle: the lamp is dull, the slot empty" if st == "idle" else "ready (Mira has a route to offer): a slip stands in the slot and the lamp is lit orange"),
                          ["chute", "mira", "courier", st], box=(sx, sy, sx + 34, sy + 30)))
    out.append(decor_piece("mira_decor_signed_sent", "signed_sent", 13, 9,
                           "Signed and Sent reward (after level 13): an envelope with a stamped seal and a signature line; a desk decoration, 1 x 1, no collision", ["decor", "mira", "desk"]))
    out.append(decor_piece("mira_decor_relay", "relay", 12, 11,
                           "Signal Keeper reward (after level 16): a miniature relay, a cobalt block with a copper coil, two terminals and a mint LED; a desk decoration, 1 x 1, no collision", ["decor", "mira", "desk"]))
    anims = {
        "payroll_keypad": {"kind": "state_set", "default": "off",
                           "states": {"off": {"entries": ["payroll_keypad_off"]}, "half": {"entries": ["payroll_keypad_half"]}, "lit": {"entries": ["payroll_keypad_lit"]}},
                           "play": ["off", "half", "lit"], "ms_per_frame": 200,
                           "note": "level 12: each correct digit lights its node and progress light; off, half (five digits), lit (ten). Light individual conduits with the conduit_* state sets"},
        "bridge_span": {"kind": "state_set", "default": "retracted",
                        "states": {"retracted": {"entries": ["bridge_span_retracted"], "blocked": True}, "extended": {"entries": ["bridge_span_extended"], "blocked": False}},
                        "play": ["retracted", "extended"], "ms_per_frame": 200,
                        "note": "level 12: the first completed payroll batch extends the bridge; retracted blocks the two middle columns, extended is walkable. Rails stay as bridge_rail entries"},
        "refund_sign": {"kind": "state_set", "default": "red",
                        "states": {"red": {"entries": ["refund_sign_red"]}, "green": {"entries": ["refund_sign_green"]}},
                        "play": ["red", "green"], "ms_per_frame": 200,
                        "note": "level 13: the refund sign flips to green when the minus is restored (orange plate with a plus, then mint plate with a minus)"},
        "calc_display": {"kind": "state_set", "default": "charge",
                         "states": {"charge": {"entries": ["calc_display_charge"]}, "refund": {"entries": ["calc_display_refund"]}},
                         "play": ["charge", "refund"], "ms_per_frame": 200,
                         "note": "level 13: the inset calculator display reverses from a charge to a refund"},
        "alarm_strip": {"kind": "state_set", "default": "merged",
                        "states": {"merged": {"entries": ["alarm_strip_merged"]}, "separated": {"entries": ["alarm_strip_separated"]}, "muted": {"entries": ["alarm_strip_muted"]}},
                        "play": ["merged", "separated"], "ms_per_frame": 250,
                        "note": "level 14: correct labels separate the alarms into six hues and pictograms; muted is the Quiet Alarm side quest"},
        "bridge_shutter": {"kind": "state_set", "default": "closed",
                           "states": {"closed": {"entries": ["bridge_shutter_closed"]}, "open": {"entries": ["bridge_shutter_open"]}},
                           "play": ["closed", "open"], "ms_per_frame": 200,
                           "note": "level 15: the bridge shutters open; place one per window"},
        "formula_wall": {"kind": "state_set", "default": "dark",
                         "states": {"dark": {"entries": ["formula_wall_dark"]}, "half": {"entries": ["formula_wall_half"]}, "lit": {"entries": ["formula_wall_lit"]}},
                         "play": ["dark", "half", "lit"], "ms_per_frame": 250,
                         "note": "level 15: as clauses become valid the connected parts of the formula illuminate (dark, half, lit)"},
        "courier_chute": {"kind": "state_set", "default": "idle",
                          "states": {"idle": {"entries": ["courier_chute_idle"]}, "ready": {"entries": ["courier_chute_ready"]}},
                          "play": ["idle", "ready"], "ms_per_frame": 300,
                          "note": "Mira's chute: ready while she has a route to offer"},
    }
    return out, anims


# ------------------------------------------------------------------ assembly

def build_pieces():
    atlas = kitlib.Atlas(ORIENT_ATLAS)
    pieces = recoloured_pieces(atlas)
    pieces += route_arrows()
    pieces += conduit_pieces()
    pieces += shared_pieces()
    pieces += racks_and_wall_pieces()
    pieces += landmark_pieces()
    qpieces, qanims = quest_pieces()
    pieces += qpieces
    anims = {
        "service_door": {
            "kind": "state_set", "default": "closed",
            "states": {"closed": {"entries": ["service_door_closed"], "blocked": True},
                       "half": {"entries": ["service_door_half"], "blocked": True},
                       "open": {"entries": ["service_door_open"], "blocked": False}},
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
    }
    anims.update(conduit_anims())
    anims.update(qanims)
    return pieces, anims, landmarks()


def group_rank(p):
    n = p.name
    if n in QUEST_NAMES:
        return 8
    if n.startswith(("floor_", "route_")):
        return 0
    if n.startswith("conduit_"):
        return 1
    if n.startswith(("wall_", "status_board")):
        return 2
    if n.startswith("service_door"):
        return 3
    if n.startswith("lamp"):
        return 4
    if n.startswith(("desk_", "chair", "pot_plant")):
        return 5
    if n.startswith(("shelf", "partition", "terminal", "cabinet", "rack", "bridge")):
        return 6
    return 7


SECTIONS = [(0, "FLOOR, ROUTE AND WAYFINDING"), (1, "FLOOR CONDUITS: three families (cobalt payroll, mint alarm, orange formula), unlit and lit"),
            (2, "WALLS AND STATUS BOARD"), (3, "SLIDING GLASS DOOR (closed, half, open)"),
            (4, "LAMP (post, off, glow states)"), (5, "REUSED ORIENTATION PROPS (recoloured)"),
            (6, "SHARED AND SYSTEMS PROPS: shelving, partition, terminal, locker, server racks, bridge deck and rail"),
            (7, "LANDMARK: THE ROUTING MACHINE (registered parts)"),
            (8, "QUEST PROPS (levels 12 to 16, Mira's routes): payroll keypad, bridge span, refund sign, calculator display, stool, alarm strip, shutter, formula wall, courier chute, Mira decor")]


def atlas_json(pieces, rects, anims, lms):
    return {
        "schema": "atlas.schema.json",
        "kit": KIT,
        "image": "systems-atlas.png",
        "tile": T,
        "layers": kitlib.LAYERS,
        "status": "Approved by the director 2026-10-02",
        "source": "Orientation pieces recoloured by exact hex swap (systems_kit.py), shared pieces from shared_pieces.py, Systems-only pieces and landmark; build_systems.py",
        "entries": [p.entry(rects[p.name]) for p in pieces],
        "animations": anims,
        "landmarks": lms,
    }
