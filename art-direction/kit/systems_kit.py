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

T = 16
KIT = "systems"
PAL = sp.Pal("systems")
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


# ------------------------------------------------------------------ assembly

def build_pieces():
    atlas = kitlib.Atlas(ORIENT_ATLAS)
    pieces = recoloured_pieces(atlas)
    pieces += route_arrows()
    pieces += conduit_pieces()
    pieces += shared_pieces()
    pieces += racks_and_wall_pieces()
    pieces += landmark_pieces()
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
    return pieces, anims, landmarks()


def group_rank(p):
    n = p.name
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
            (7, "LANDMARK: THE ROUTING MACHINE (registered parts)")]


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
