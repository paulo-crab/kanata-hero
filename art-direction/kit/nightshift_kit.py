"""Night Shift environment kit (task 7.3): atlas pieces, the long interior window landmark and the
night-readability helpers.

Same method as records_kit.py, with the dark-floor rules of PALETTES_SPEC.md ("Night Shift edge-light rule"):

  1. Orientation pieces recoloured by an exact hex swap (swap raises on any unmapped pixel), then two
     Night Shift passes: contact shadows re-keyed so they are darker than the floor (the ink steps used
     in Orientation are lighter than this floor and would read as a glow), and a lit edge: every
     upper-left silhouette pixel that would not reach 3:1 against the floor fill becomes silver.
  2. Shared pieces from shared_pieces.py (partition, terminal desk, shelf, cabinet), drawn with the
     Night Shift ramps and given the same two passes.
  3. Night-Shift-only pieces: lamp pools (light layer, where_color), route arrows, the break-room counter,
     the noticeboard, the security vestibule gate, the ledger desk and the landmark.

People get a cool moonlight rim (glass step 2, #8E96B8) from the renderer by the per-pixel rule `night_rim`
(palettes/night_rim.py, player decision 2026-10-02), which replaced the warm #F9D79A people rim. Props get a
silver edge (glass step 3), so a person and a piece of furniture never share an edge colour. The landmark's
coworker silhouettes behind the lit window keep the warm rim: the room behind them is lit.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kitlib  # noqa: E402
import orientation_kit as ok  # noqa: E402
import records_kit as rk  # noqa: E402  (recolour, from_orientation: read only)
import shared_pieces as sp  # noqa: E402
import build_scale_test as bst  # noqa: E402
import district_palettes as dp  # noqa: E402
import night_rim as nr  # noqa: E402  (the people rim: one reference implementation)
import environment as env  # noqa: E402
import quest_props as qp  # noqa: E402

T = 16
KIT = "nightshift"
PAL = sp.Pal("nightshift")
N = dp.DISTRICTS["nightshift"]
O = dp.DISTRICTS["orientation"]
INK, shifted = bst.INK, bst.shifted


class Col(np.ndarray):
    """An RGB triple that also answers .upper() with its hex string, so the same ramp object drives both the
    drawing code (numpy assignment) and the hex-swap tables of records_kit.recolour."""

    def __new__(cls, hexstr):
        return np.array([int(hexstr[i:i + 2], 16) for i in (1, 3, 5)], np.uint8).view(cls)

    def upper(self):
        return "#%02X%02X%02X" % tuple(int(v) for v in np.asarray(self))


def _ramp(role):
    return [Col(h) for h in N[role]]


def rgb(c):
    return tuple(int(v) for v in (kitlib.hex2rgb(c) if isinstance(c, str) else c))


FLOOR, WALL, GLASS, WOOD, FOLI, ACC = (_ramp(r) for r in ("floor", "wall", "glass", "wood", "foliage", "accent"))
FLOOR_FILL, FLOOR_JOINT = FLOOR[3], FLOOR[2]
SILVER = GLASS[3]            # prop edge light
RIM = ACC[3]                 # WARM rim: only the landmark's backlit window silhouettes use it (draw_figs). Never people.
PEOPLE_RIM = GLASS[2]        # people's cool moonlight rim, #8E96B8 = dp.NIGHT_RIM (the single source of truth)
assert PEOPLE_RIM.upper() == dp.DISTRICTS[dp.NIGHT_RIM[0]][dp.NIGHT_RIM[1]][dp.NIGHT_RIM[2]].upper()
MIN_EDGE = 3.0               # WCAG contrast an upper-left silhouette edge must reach on the dark floor

ORIENT_ATLAS = os.path.join(HERE, "orientation-atlas.json")
STONE_S, GLASS_S, WOOD_S, GREEN_S, BRASS_S = (O["floor"], O["glass"], O["wood"], O["foliage"], O["accent"])
CORAL_S = dp.ORIENTATION_EXTRA["coral"]


# ------------------------------------------------------------------ colour maths

luminance, contrast = nr.luminance, nr.contrast   # WCAG maths shared with the people rim (palettes/night_rim.py)
night_rim = nr.night_rim                           # reference implementation of the people rim, see night_rim.py
night_rim_on_scene = nr.night_rim_on_scene


# ------------------------------------------------------------------ night shadows

def night_cast(self, x0, x1, y, rows=2):
    """env.Room.cast for a dark floor: the first row (against the base) is the floor's darkest step, the
    second row the outline ink. Both are darker than the floor fill, so a shadow can never read as a glow."""
    self.rect(x0 + 1, y, x1 + 1, y + 1, FLOOR[0])
    if rows > 1:
        self.rect(x0 + 2, y + 1, x1 + 2, y + rows, INK[0])


env.Room.cast = night_cast   # build_nightshift.py is its own process; Orientation's build is unaffected


def night_shadow(sprite, rect):
    """Re-key an Orientation contact shadow (ink steps 2 and 3, lighter than this floor) inside rect."""
    if not rect:
        return sprite
    out = sprite.copy()
    x, y, w, h = rect
    reg = out[y:y + h, x:x + w, :3]
    a = out[y:y + h, x:x + w, 3] > 0
    m2 = a & np.all(reg == INK[2], axis=2)
    m3 = a & np.all(reg == INK[3], axis=2)
    reg[m2] = FLOOR[0]
    reg[m3] = INK[0]
    return out


# ------------------------------------------------------------------ the lit edge

def edge_light(sprite, rim=SILVER, bg=FLOOR_FILL, shadow=None, skip_rows=None, minimum=MIN_EDGE, denoise=False, sides=("up", "left")):
    """Night Shift edge light for a prop: every opaque upper-left silhouette pixel (transparent above or to
    the left) whose colour is below `minimum`:1 against `bg` becomes `rim`. Pixels already bright enough
    (a lit top step, a glowing screen) are kept. `shadow` [x, y, w, h] and `skip_rows` (y0, y1) are left alone."""
    out = sprite.copy()
    h, w = sprite.shape[:2]
    a = sprite[:, :, 3] > 0
    up = np.zeros_like(a)
    lf = np.zeros_like(a)
    up[0] = True
    up[1:] = ~a[:-1]
    lf[:, 0] = True
    lf[:, 1:] = ~a[:, :-1]
    edge = a & ((up if "up" in sides else False) | (lf if "left" in sides else False))
    if shadow:
        x, y, sw, sh = shadow
        edge[y:y + sh, x:x + sw] = False
    if skip_rows:
        edge[skip_rows[0]:skip_rows[1]] = False
    rimc = rgb(rim)
    lit = np.zeros_like(a)
    for y, x in zip(*np.nonzero(edge)):
        if contrast(sprite[y, x, :3], bg) < minimum:
            out[y, x, :3] = rimc
            lit[y, x] = True
    if denoise:
        # ragged silhouettes (leaves): an isolated lit pixel reads as a speck of frost, so it keeps its outline
        pad = np.pad(lit, 1)
        near = sum(pad[1 + dy:1 + dy + lit.shape[0], 1 + dx:1 + dx + lit.shape[1]] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dx, dy) != (0, 0))
        lone = lit & (near == 0)
        out[lone, :3] = sprite[lone, :3]
        # a lone leaf-edge pixel too dark against the floor takes the foliage tip (a sunlit leaf tip, not a frost speck)
        tip = rgb(dp.FOLIAGE_EXTRA["nightshift"]["tip"])
        for y, x in zip(*np.nonzero(lone)):
            if contrast(sprite[y, x, :3], bg) < minimum:
                out[y, x, :3] = tip
    return out


def finish_piece(p, skip_rows=None, edge=True, denoise=False, sides=("up", "left")):
    """Night passes on a Piece: shadow re-key, then the lit edge."""
    p.sprite = night_shadow(p.sprite, p.shadow)
    if edge:
        p.sprite = edge_light(p.sprite, shadow=p.shadow, skip_rows=skip_rows, denoise=denoise, sides=sides)
    return p


# ------------------------------------------------------------------ 1. recoloured Orientation pieces

def night_from_orientation(atlas, src, new, maps, regions=(), note="", tags=(), comp_color=None, edge=True, skip_rows=None, denoise=False, sides=("up", "left")):
    p = rk.from_orientation(atlas, src, new, maps, regions, note=note, tags=tags, comp_color=comp_color)
    return finish_piece(p, skip_rows=skip_rows, edge=edge, denoise=denoise, sides=sides)


def ramp(vals):
    return list(vals)


def recoloured_pieces(atlas):
    pieces = []
    floor_maps = [(STONE_S, FLOOR)]
    for nm, desc in (("floor_j", "slab corner: joint on the top row and the left column"),
                     ("floor_h", "slab edge: joint on the top row"), ("floor_v", "slab edge: joint on the left column"),
                     ("floor_p", "slab interior, plain")):
        pieces.append(night_from_orientation(atlas, nm, nm, floor_maps, edge=False, tags=["floor", "slab"],
                                             note=f"Night Shift floor, {desc}. Dark cool slate, broad slabs, no grain"))
    pieces.append(night_from_orientation(atlas, "floor_chip", "floor_chip", floor_maps, edge=False,
                                         note="2x1 px wear mark on the floor layer; placed with a pixel offset"))
    pieces.append(night_from_orientation(atlas, "route_inlay", "route_inlay", [([STONE_S[2]], [GLASS[2]])], edge=False,
                                         note="1 px inlay line in muted silver (glass step 2) that marks a lit route; repeat every 16 px (horizontal). "
                                              "Brighter than the floor, so a route reads on the dark slate without a label"))
    v = np.rot90(pieces[-1].sprite, 1).copy()
    pieces.append(ok.Piece("route_inlay_v", v, (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                           note="route_inlay turned 90 degrees: the same line for vertical corridor edges", tags=["floor", "route"]))
    # Walls: indigo faces, the lit trim of the cap in silver (glass step 3), baseboard and cast shadow re-keyed.
    wall_maps = [(STONE_S, WALL), (GLASS_S, GLASS), ([GLASS_S[2]], [GLASS[3]])]
    pieces.append(night_from_orientation(atlas, "wall_n_plain", "wall_n_plain", wall_maps, sides=("up",),
                                         note="north wall segment: lit cap (silver top edge and trim), deep indigo face, baseboard, contact shadow darker than the floor; tiles horizontally",
                                         tags=["wall", "north", "top plane", "lit edge"]))
    for nm in ("wall_n_window_a", "wall_n_window_b"):
        pieces.append(_window(atlas, nm, wall_maps))
    pieces.append(night_from_orientation(atlas, "wall_e_plain", "wall_e_plain", wall_maps, edge=False,
                                         note="east wall segment, side plane; the lit trim line is silver. Tiles vertically. Content starts 4 px into the first cell",
                                         tags=["wall", "east", "side plane", "lit edge"]))
    # Service door (east wall): the Orientation door, cherry-free: warm lamp-ramp frame, silver glass, stair sign.
    door_maps = [(BRASS_S, ACC), (STONE_S, WALL), (GLASS_S, GLASS), (CORAL_S, ACC)]
    sign_rows = [(0, 13, [(BRASS_S, ACC), (CORAL_S, ACC), (STONE_S, WALL), (GLASS_S, GLASS)])]
    for st, note in (("closed", "both glass leaves shut: warm lamp-ramp frame, leaves, seam, pulls, stair sign on a lit plate"),
                     ("half", "leaves slid 8 px into the jamb pockets: the corridor beyond shows through"),
                     ("open", "leaves fully in the pockets (15 px): the doorway is open and the threshold is lit")):
        p = rk.from_orientation(atlas, f"records_door_{st}", f"service_door_{st}", door_maps, regions=sign_rows, note=note,
                                tags=["door", "sliding glass", "service corridor", st])
        p.sprite = stair_sign(p.sprite)
        pieces.append(p)
    # Lamp: post, head, glow. The glow is a step darker than the head so a lamp reads as a lit object, not a hole.
    lamp_maps = [(BRASS_S, ACC)]
    glow_maps = [(BRASS_S, [ACC[0], ACC[1], ACC[2], ACC[2]])]
    pieces.append(night_from_orientation(atlas, "lamp", "lamp", lamp_maps, skip_rows=(0, 6),
                                         note="floor lamp: post with a silver left edge, warm head with one lit step, contact shadow"))
    pieces.append(night_from_orientation(atlas, "lamp_off", "lamp_off", lamp_maps, skip_rows=(0, 6),
                                         note="unlit lamp: head in the ink ramp, no glow"))
    pieces.append(night_from_orientation(atlas, "lamp_glow_on", "lamp_glow_on", glow_maps, comp_color=FLOOR_FILL.upper(), edge=False,
                                         note=f"glow, one hard step in the lamp ramp (accent step 2), radius 5.2. Paints only where the floor is the bare fill {FLOOR_FILL.upper()}"))
    pieces.append(night_from_orientation(atlas, "lamp_glow_pulse", "lamp_glow_pulse", glow_maps, comp_color=FLOOR_FILL.upper(), edge=False,
                                         note="pulse frame of the glow, radius 6.4; alternate with lamp_glow_on at about 600 ms each"))
    # Desks. dead: legacy stations that have gone dark (ink screen). lit: a working station (silver screen).
    wood_green = [(WOOD_S, WOOD), (GREEN_S, FOLI), (STONE_S, [GLASS[1], GLASS[2], GLASS[3], GLASS[3]])]
    lit_glass = (GLASS_S, [GLASS[1], GLASS[2], GLASS[3], ACC[3]])
    dead_glass = (GLASS_S, [dp.INK[1], dp.INK[1], dp.INK[2], dp.INK[3]])
    for kind, gl, desc in (("dead", dead_glass, "legacy station gone dark: dim wood, ink screen with one pale glint, keyboard, paper and a small plant"),
                           ("lit", lit_glass, "working station: dim wood, silver-lit screen, keyboard, paper and a small plant")):
        for nm in ("a", "b"):
            pieces.append(night_from_orientation(atlas, f"desk_{nm}", f"desk_{kind}_{nm}", wood_green + [gl],
                                                 note=desc + "; a and b differ only in the plant leaves. The chair is a separate entry",
                                                 tags=["desk", kind]))
    pieces.append(night_from_orientation(atlas, "chair", "chair", [(CORAL_S, WALL)],
                                         note="indigo task chair seen from above with a silver edge; place 11 px right and 18 px below a desk origin"))
    for nm in ("pot_plant_a", "pot_plant_b", "pot_plant_c", "pot_plant_d"):
        pieces.append(night_from_orientation(atlas, nm, nm, [(GREEN_S, FOLI)], denoise=True,
                                             note="slate planter with a night-green plant; four leaf layouts (a to d); silver edge on the upper-left of pot and leaves"))
    pieces.append(night_from_orientation(atlas, "sofa", "sofa", [(WOOD_S, WOOD)],
                                         note="break-room lounge sofa seen from above, dim terracotta wood"))
    pieces.append(night_from_orientation(atlas, "side_table", "side_table", [(GREEN_S, FOLI)], denoise=True,
                                         note="round slate side table with a small plant"))
    return pieces


def _window(atlas, nm, wall_maps):
    """Window overlay: the frame's upper-left edge is silver (the 'silver frames' of the district brief). The
    overlay sits on the indigo wall, so its edge is measured against the wall face and not the floor."""
    p = rk.from_orientation(atlas, nm, nm, wall_maps,
                            note="high window overlay for the north wall: silver-edged dark frame, indigo pane, one stepped reflection band, lit sill",
                            tags=["wall", "window", "glass", "lit edge"])
    p.sprite = edge_light(p.sprite, bg=WALL[1])
    return p


def stair_sign(sprite):
    """Replace the Orientation folder icon on the door's sign plate by a stair icon (the service stair)."""
    out = sprite.copy()
    plate = rgb(ACC[2])
    ink = INK[1]
    out[3:9, 10:20, :3] = plate
    out[3:9, 10:20, 3] = 255
    for x0, x1, y0 in ((10, 13, 7), (13, 16, 5), (16, 20, 3)):
        out[y0:9, x0:x1, :3] = ink
    return out


# ------------------------------------------------------------------ 2. shared pieces, night ramps

def shared_pieces():
    out = []
    sx, sy = 64, 64
    note_shelf = "{n}-cell archive shelving for the ledger room: top plane, front face with three bays, boxes in warm, indigo, slate and wood clusters, kick plate; silver edge"
    out.append(ok.make("shelf_1x1", lambda r: sp.shelf(r, sx, sy, 1, PAL, 3), (sx, sy + sp.SHELF_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note=note_shelf.format(n=1), tags=["shelf", "archive"]))
    for nm, seed in (("shelf_2x1_a", 1), ("shelf_2x1_b", 2)):
        out.append(ok.make(nm, lambda r, seed=seed: sp.shelf(r, sx, sy, 2, PAL, seed), (sx, sy + sp.SHELF_H - 16), (2, 1), ["11"],
                           "rear_prop", "prop", y_sort=True, note=note_shelf.format(n=2) + "; a and b differ only in the box layout",
                           tags=["shelf", "archive"]))
    out.append(ok.make("partition_1x1", lambda r: sp.partition(r, sx, sy, 1, PAL), (sx, sy + sp.PART_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note="security-glass partition, one cell: dark frame with a silver cap, indigo pane, one reflection band, floor rail",
                       tags=["partition", "glass"]))
    out.append(ok.make("partition_2x1", lambda r: sp.partition(r, sx, sy, 2, PAL), (sx, sy + sp.PART_H - 16), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True, note="security-glass partition, two cells, with a middle post and a reflection band per pane",
                       tags=["partition", "glass"]))
    out.append(ok.make("terminal_desk", lambda r: sp.terminal_desk(r, sx, sy + 8, PAL), (sx, sy + 8), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True,
                       note="two-cell console desk: ink housing first, then a silver-lit screen, a one-step glow on the desk top, keyboard and card reader",
                       tags=["terminal", "desk", "interact"]))
    out.append(ok.make("cabinet_1x1", lambda r: sp.cabinet(r, sx, sy, 1, PAL), (sx, sy + sp.CAB_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note="dim wood filing cabinet, one cell: paper stack on the top plane, three drawers with label plates",
                       tags=["cabinet", "archive"]))
    return [finish_piece(p) for p in out]


# ------------------------------------------------------------------ 3. Night-Shift-only pieces

def _px_piece(name, rgba, fp_cells, collision, layer, kind, note, tags, fp_room=(0, 0), composite=None, tl=(0, 0)):
    return ok.Piece(name, rgba, tl, fp_room, fp_cells, collision, layer, kind, composite=composite, note=note, tags=tags)


def route_arrows():
    """Warm wayfinding arrows inlaid in the floor (east and north): accent step 2 with a lit upper edge."""
    a = np.zeros((16, 16, 4), np.uint8)

    def px(x, y, c):
        a[y, x, :3] = rgb(c)
        a[y, x, 3] = 255
    for x in range(3, 10):
        px(x, 7, ACC[3])
        px(x, 8, ACC[2])
    for i in range(5):
        for y in range(3 + i, 13 - i):
            px(10 + i, y, ACC[2])
    for i in range(5):
        px(10 + i, 3 + i, ACC[3])
    east = _px_piece("route_arrow_e", a, (1, 1), ["0"], "floor_marking", "tile",
                     "warm wayfinding arrow inlaid in the floor, pointing east (accent steps 2 and 3, 3.4:1 and above against the floor fill); "
                     "place on bare floor, outside a lamp pool", ["wayfinding", "route"])
    north = _px_piece("route_arrow_n", np.rot90(a, 1).copy(), (1, 1), ["0"], "floor_marking", "tile",
                      "the same arrow pointing north", ["wayfinding", "route"])
    return [east, north]


def ellipse_mask(w, h, rx, ry):
    yy, xx = np.mgrid[0:h, 0:w]
    return ((xx + 0.5 - w / 2) / rx) ** 2 + ((yy + 0.5 - h / 2) / ry) ** 2 <= 1


def pool_pieces(name, rx, ry, origin, note, tags):
    """A lamp pool as two `light` entries: `<name>_fill` recolours the bare floor fill to accent step 1 and
    `<name>_seam` the slab joints and wear chips to accent step 0 (the rule of PALETTES_SPEC: islands of desk
    light). Both use the same mask, so they always travel together. origin: where the placement point sits in
    the sprite (footprint origin)."""
    w, h = 2 * rx, 2 * ry
    m = ellipse_mask(w, h, rx, ry)
    out = []
    for suffix, col, dest, what in (("fill", FLOOR_FILL, ACC[1], "the bare floor fill"), ("seam", FLOOR_JOINT, ACC[0], "the slab joints and wear chips")):
        rgba = np.zeros((h, w, 4), np.uint8)
        rgba[m, :3] = rgb(dest)
        rgba[m, 3] = 255
        out.append(_px_piece(f"{name}_{suffix}", rgba, (1, 1), ["0"], "light", "light", f"{note} This entry recolours {what} ({col.upper()}) to {dest.upper()}; "
                                                                               f"place it with {name}_{'seam' if suffix == 'fill' else 'fill'}.",
                             tags=["light", "pool"] + tags, fp_room=origin, composite={"mode": "where_color", "color": col.upper()}))
    return out


DESK_POOL_ORIGIN = (26 - 17, 11 - 14)   # pool centre = desk footprint origin + (17, 14)


def lamp_pools():
    out = []
    out += pool_pieces("pool_desk", 26, 11, DESK_POOL_ORIGIN,
                       "Pool of desk light, 52x22 px: centre sits 14 px below the desk's footprint origin and 17 px right, so place it at the desk's cell.", ["desk"])
    out += pool_pieces("pool_route", 22, 11, (22, 11),
                       "Route pool, 44x22 px, placement point = centre. Spaced every 4 to 5 cells along a route it makes the route brighter than its dead ends.", ["route"])
    out += pool_pieces("pool_door", 13, 20, (13, 20),
                       "Doorway pool, 26x40 px, placement point = centre. Put it on the floor in front of a door so the doorway is the brightest thing in the wall.", ["door"])
    out += pool_pieces("pool_break", 31, 11, (31, 11),
                       "Break-room pool, 62x22 px, placement point = centre: the safe, well-lit place at the start of the district.", ["break room"])
    out += pool_pieces("pool_ledger", 20, 10, (20 - 16, 10 - 8),
                       "Ledger pool, 40x20 px: centre 16 px right and 8 px below the ledger desk's footprint origin.", ["ledger"])
    return out


def break_counter(lit=True):
    """Break-room counter, 3x1: kettle, mugs and a small warm lamp on a dim wood top, cupboard doors on the front.
    lit=False is the dim state of the break room (quest props): the lamp is off, the kettle cold, no glow on the top plane."""
    sx, sy = 64, 64
    HOT3, HOT2 = (ACC[3], ACC[2]) if lit else (GLASS[3], GLASS[1])

    def draw(r):
        x0, y0 = sx, sy + 3
        env.block(r, x0, y0, x0 + 46, y0 + 16, 7, WOOD, WOOD)
        # cupboard doors on the front face
        for dx in (1, 16, 31):
            r.rect(x0 + dx + 1, y0 + 11, x0 + dx + 14, y0 + 15, WOOD[1])
            r.rect(x0 + dx + 1, y0 + 11, x0 + dx + 14, y0 + 12, WOOD[2])
            r.rect(x0 + dx + 7, y0 + 13, x0 + dx + 9, y0 + 14, GLASS[3])    # pull
        # kettle: steel body with a lit left column, spout, handle, lid knob
        kx, ky = x0 + 6, y0 + 1
        kb = r.mask(kx, ky + 2, kx + 9, ky + 8)
        r.img[kb] = GLASS[2]
        r.rect(kx, ky + 2, kx + 2, ky + 8, GLASS[3])
        r.rect(kx + 7, ky + 2, kx + 9, ky + 8, GLASS[1])
        r.rect(kx, ky + 6, kx + 9, ky + 8, GLASS[1])
        r.outline(kb)
        r.rect(kx + 9, ky + 3, kx + 12, ky + 4, GLASS[2])                      # spout
        r.rect(kx + 10, ky + 2, kx + 12, ky + 3, INK[0])
        r.rect(kx + 3, ky, kx + 6, ky + 2, GLASS[3])                           # lid and knob
        r.outline(r.mask(kx + 3, ky, kx + 6, ky + 2))
        r.rect(kx + 3, ky + 3, kx + 5, ky + 4, HOT3)                         # warm reflection, one lit step
        # mugs
        for i, (mx, col) in enumerate(((x0 + 22, HOT2), (x0 + 28, GLASS[3]))):
            m = r.mask(mx, y0 + 3, mx + 5, y0 + 8)
            r.img[m] = col
            r.rect(mx, y0 + 3, mx + 5, y0 + 4, HOT3 if i == 0 else GLASS[3])
            r.rect(mx + 4, y0 + 4, mx + 5, y0 + 8, WOOD[1] if i == 0 else GLASS[1])
            r.outline(m)
            r.rect(mx + 5, y0 + 4, mx + 6, y0 + 6, INK[0])
        # small lamp at the right end: stem, warm shade, one hard glow step on the counter top
        lx, ly = x0 + 37, y0 + 1
        r.rect(lx + 3, ly + 3, lx + 5, ly + 9, INK[1])
        sh = r.mask(lx, ly, lx + 8, ly + 4)
        r.img[sh] = HOT2
        r.rect(lx, ly, lx + 8, ly + 1, HOT3)
        r.rect(lx + 1, ly + 3, lx + 7, ly + 4, HOT3)
        r.outline(sh)
        if lit:
            r.rect(lx - 1, ly + 7, lx + 9, ly + 9, ACC[1])                     # glow on the top plane
    p = ok.make("break_counter" if lit else "break_counter_dim", draw, (sx, sy + 3), (3, 1), ["111"], "rear_prop", "prop", y_sort=True,
                note=("break-room counter: kettle, two mugs and a small warm lamp on a dim wood top, three cupboard doors; the warm lamp is the focus of the pool_break light" if lit else
                      "the break-room counter in its dim state (levels 17 and 19: the break room is not yet warm): the same counter with the lamp off, the kettle cold and no glow on the top plane"),
                tags=["counter", "break room", "kettle"] + ([] if lit else ["dim"]))
    return finish_piece(p)


def noticeboard():
    """Wall overlay for the north wall: a framed cork board with pinned notes (one warm, three pale)."""
    sx, sy = 64, 64

    def draw(r):
        x0, y0 = sx, sy
        r.rect(x0, y0, x0 + 28, y0 + 18, INK[0])
        r.rect(x0 + 1, y0 + 1, x0 + 27, y0 + 17, GLASS[2])                     # silver frame
        board = r.mask(x0 + 2, y0 + 2, x0 + 26, y0 + 16)
        r.img[board] = WOOD[1]
        r.rect(x0 + 2, y0 + 2, x0 + 26, y0 + 3, WOOD[2])
        for (nx, ny, nw, nh, col) in ((4, 4, 6, 6, GLASS[3]), (12, 5, 5, 7, ACC[3]), (19, 4, 5, 5, GLASS[3]), (8, 11, 7, 4, GLASS[2])):
            n = r.mask(x0 + nx, y0 + ny, x0 + nx + nw, y0 + ny + nh)
            r.img[n] = col
            r.rect(x0 + nx + 1, y0 + ny + 2, x0 + nx + nw - 1, y0 + ny + 3, INK[2])   # a line of text
            r.img[y0 + ny, x0 + nx + nw // 2] = ACC[1]                                  # pin
        r.rect(x0, y0 + 17, x0 + 28, y0 + 18, INK[1])
    rgba, painted = ok.cap(draw)
    b = kitlib.bbox(painted)
    sprite = edge_light(kitlib.crop_rgba(rgba, b), bg=WALL[1])
    return _px_piece("wall_n_noticeboard", sprite, (2, 2), ["00", "00"], "rear_wall", "wall",
                     "noticeboard overlay for the north wall: silver frame, cork board, four pinned notes (one warm). Place at the wall's pixel row 9; "
                     "the break room's pinned practice reminders",
                     ["wall", "sign", "break room"])


def ledger_desk():
    """The ledger desk: a wide desk with an open ledger and the one warm ledger lamp."""
    sx, sy = 64, 64

    def draw(r):
        x0, y0 = sx, sy
        env.block(r, x0, y0, x0 + 34, y0 + 16, 5, WOOD, WOOD)
        # open ledger: wood cover, two pale pages, lines, a coral-free warm bookmark
        cv = r.mask(x0 + 3, y0 + 2, x0 + 21, y0 + 9)
        r.img[cv] = WOOD[0]
        r.outline(cv)
        r.rect(x0 + 4, y0 + 3, x0 + 12, y0 + 8, GLASS[3])
        r.rect(x0 + 12, y0 + 3, x0 + 20, y0 + 8, GLASS[3])
        r.rect(x0 + 12, y0 + 3, x0 + 13, y0 + 8, GLASS[1])                    # spine
        for ly_ in (4, 6):
            r.rect(x0 + 5, y0 + ly_, x0 + 11, y0 + ly_ + 1, GLASS[2])
            r.rect(x0 + 14, y0 + ly_, x0 + 19, y0 + ly_ + 1, GLASS[2])
        r.rect(x0 + 16, y0 + 3, x0 + 17, y0 + 8, ACC[1])                      # ribbon
        # lamp: base, arm and a warm shade casting one hard step on the desk top
        r.rect(x0 + 25, y0 + 6, x0 + 31, y0 + 8, INK[1])
        r.rect(x0 + 27, y0 - 3, x0 + 29, y0 + 6, INK[1])
        sh = r.mask(x0 + 23, y0 - 8, x0 + 33, y0 - 2)
        r.img[sh] = ACC[2]
        r.rect(x0 + 23, y0 - 8, x0 + 33, y0 - 7, ACC[3])
        r.rect(x0 + 24, y0 - 3, x0 + 32, y0 - 2, ACC[3])
        r.outline(sh)
        r.rect(x0 + 22, y0 + 8, x0 + 32, y0 + 10, ACC[1])                     # glow on the top plane
    p = ok.make("ledger_desk", draw, (sx, sy), (2, 1), ["11"], "rear_prop", "prop", y_sort=True,
                note="the ledger desk: an open ledger with a bookmark and one warm lamp whose shade is the brightest warm pixel in the room; footprint 2x1",
                tags=["desk", "ledger", "lamp"])
    return finish_piece(p)


GATE_W, GATE_H = 64, sp.PART_H


def draw_gate(r, sx, sy, open_):
    """Security vestibule gate across a 2-cell route: two glass-and-steel posts with card readers and a glass
    leaf. Closed, the leaf spans the gap and shows an amber lock bar; open it is folded edge-on against the left post."""
    for px_ in (sx, sx + 48):
        sp.partition(r, px_, sy, 1, PAL)
        # card reader on the post front: ink housing, a lit window, one LED
        rx_, ry_ = px_ + 4, sy + 10
        r.rect(rx_, ry_, rx_ + 8, ry_ + 8, INK[0])
        r.rect(rx_ + 1, ry_ + 1, rx_ + 7, ry_ + 7, INK[1])
        r.rect(rx_ + 2, ry_ + 2, rx_ + 6, ry_ + 4, GLASS[2])
        r.rect(rx_ + 2, ry_ + 2, rx_ + 6, ry_ + 3, GLASS[3])
        r.img[ry_ + 5, rx_ + 3] = GLASS[3] if open_ else ACC[3]
        r.img[ry_ + 5, rx_ + 4] = GLASS[3] if open_ else ACC[2]
    if not open_:
        lx0, lx1 = sx + 16, sx + 48
        r.cast(lx0, lx1, sy + GATE_H)
        leaf = r.mask(lx0, sy + 6, lx1, sy + GATE_H)
        r.img[leaf] = GLASS[1]
        r.rect(lx0, sy + 7, lx1, sy + 8, GLASS[3])                              # lit top rail
        pane = r.mask(lx0 + 1, sy + 9, lx1 - 1, sy + 22)
        r.img[pane] = GLASS[2]
        r.img[pane & (r.y >= sy + 16)] = GLASS[1]
        band = pane & (np.abs((r.x - lx0) - (r.y - sy - 9) * 0.8 - 8) < 1.6)
        r.img[band] = GLASS[3]
        band2 = pane & (np.abs((r.x - lx0) - (r.y - sy - 9) * 0.8 - 18) < 0.6)
        r.img[band2] = GLASS[3]
        r.rect(lx0 + 1, sy + 14, lx1 - 1, sy + 16, ACC[2])                      # amber lock bar
        r.rect(lx0 + 1, sy + 14, lx1 - 1, sy + 15, ACC[3])
        r.rect(lx0 + 1, sy + 22, lx1 - 1, sy + GATE_H - 1, GLASS[0])           # kick rail
        r.rect(lx0 + 1, sy + 22, lx1 - 1, sy + 23, GLASS[2])
        r.outline(leaf)
    else:
        lx0 = sx + 16
        r.cast(lx0, lx0 + 5, sy + GATE_H)
        leaf = r.mask(lx0, sy + 6, lx0 + 5, sy + GATE_H)
        r.img[leaf] = GLASS[1]
        r.rect(lx0, sy + 7, lx0 + 5, sy + 8, GLASS[3])
        r.rect(lx0, sy + 8, lx0 + 1, sy + GATE_H - 1, GLASS[3])
        r.rect(lx0 + 2, sy + 9, lx0 + 4, sy + 22, GLASS[2])
        r.outline(leaf)


def vestibule_gate():
    out = []
    sx, sy = 64, 64
    box = (sx, sy, sx + GATE_W, sy + GATE_H + 3)
    fp = (sx, sy + GATE_H - 16)
    for st, coll, note in (("closed", "1111", "two security-glass posts with card readers and an amber lock bar across the glass leaf: cols 0-3 block"),
                           ("open", "1001", "the leaf folded edge-on against the left post, readers switched to silver: cols 1-2 are a two-cell walkway")):
        p = ok.make(f"vestibule_gate_{st}", lambda r, st=st: draw_gate(r, sx, sy, st == "open"), fp, (4, 1), [coll], "rear_prop", "prop", box=box,
                    shadow=False, y_sort=True, note="security vestibule gate, " + note + ". Contact shadows are baked per piece",
                    tags=["gate", "vestibule", "state", st])
        out.append(finish_piece(p))
    return out


# ------------------------------------------------------------------ landmark: the long interior window

OX, OY = 64, 64          # capture position of the 192 x 64 box in the 320 x 192 room
BOX_W, BOX_H = 192, 64
FP = (0, 0)              # footprint origin inside the box: the 12 x 2 cell wall run
FP_CELLS = (12, 2)
PANE_X0, PANE_W, MULL_W, NPANES = 8, 26, 4, 6
PANE_Y0, PANE_Y1 = 10, 26     # pane rows (local), sill row below
FRAME = (6, 8, 186, 29)       # outer frame rect (local)


def pane_x(i):
    return PANE_X0 + i * (PANE_W + MULL_W)


class P:
    """Painter in landmark-local coordinates over an env.Room."""

    def __init__(self, r):
        self.r = r

    def rect(self, x0, y0, x1, y1, c):
        self.r.rect(OX + x0, OY + y0, OX + x1, OY + y1, c)

    def mask(self, x0, y0, x1, y1):
        return self.r.mask(OX + x0, OY + y0, OX + x1, OY + y1)

    def put(self, x, y, c):
        self.r.img[OY + y, OX + x] = c


def draw_window_base(r, wall_tile):
    """The 12-cell wall run: the recoloured wall tiles, then a continuous glazing frame with a silver top and
    left edge, six mullions, a silver sill and the dark baseboard. The panes themselves are separate parts."""
    p = P(r)
    for i in range(12):
        t = wall_tile
        h, w = t.shape[:2]
        ys, xs = np.nonzero(t[:, :, 3] > 0)
        for y, x in zip(ys, xs):
            r.img[OY + y, OX + i * 16 + x] = t[y, x, :3]
    x0, y0, x1, y1 = FRAME
    p.rect(x0, y0, x1, y1, INK[0])
    p.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 2, GLASS[3])                 # silver head rail
    p.rect(x0 + 1, y0 + 1, x0 + 2, y1 - 1, GLASS[3])                 # silver left jamb
    p.rect(x1 - 2, y0 + 1, x1 - 1, y1 - 1, GLASS[1])                 # shaded right jamb
    for i in range(NPANES - 1):                                      # mullions between the panes
        mx = pane_x(i) + PANE_W
        p.rect(mx, PANE_Y0 - 1, mx + MULL_W, PANE_Y1 + 1, GLASS[1])
        p.rect(mx, PANE_Y0 - 1, mx + 1, PANE_Y1 + 1, GLASS[3])
        p.rect(mx + MULL_W - 1, PANE_Y0 - 1, mx + MULL_W, PANE_Y1 + 1, INK[0])
    p.rect(PANE_X0 - 1, PANE_Y1, PANE_X0 + NPANES * (PANE_W + MULL_W) - MULL_W + 1, PANE_Y1 + 1, GLASS[3])   # sill, one hard silver step
    p.rect(PANE_X0 - 1, PANE_Y1 + 1, PANE_X0 + NPANES * (PANE_W + MULL_W) - MULL_W + 1, PANE_Y1 + 2, INK[0])


def draw_panes(r, state):
    """before: a dark empty room, cool two-tone glass; after: the room behind is lit warm: a strip light along the
    ceiling, a pale back wall that silhouettes read against, a wainscot, a lit floor, and per pane either a shelf
    of mugs or a pendant lamp."""
    p = P(r)
    for i in range(NPANES):
        x0 = pane_x(i)
        x1 = x0 + PANE_W
        pane = p.mask(x0, PANE_Y0, x1, PANE_Y1)
        if state == "before":
            r.img[pane] = GLASS[1]
            p.rect(x0, PANE_Y0 + 9, x1, PANE_Y1, GLASS[0])               # the dark floor of the room beyond
            p.rect(x0, PANE_Y0, x1, PANE_Y0 + 1, GLASS[0])               # shadow under the head rail
        else:
            r.img[pane] = ACC[2]                                         # lit back wall
            p.rect(x0, PANE_Y0, x1, PANE_Y0 + 1, ACC[3])                 # strip light across the ceiling
            p.rect(x0, PANE_Y1 - 8, x1, PANE_Y1 - 5, ACC[1])             # wainscot
            p.rect(x0, PANE_Y1 - 5, x1, PANE_Y1, ACC[0])                 # floor of the room beyond
            p.rect(x0, PANE_Y1 - 5, x1, PANE_Y1 - 4, ACC[1])             # skirting line
            if i in (1, 3, 4):                                           # a shelf of mugs on the right of the pane
                p.rect(x0 + 15, PANE_Y0 + 7, x0 + 25, PANE_Y0 + 8, WOOD[1])
                for k, mx in enumerate((16, 19, 22)):
                    p.rect(x0 + mx, PANE_Y0 + 5, x0 + mx + 2, PANE_Y0 + 7, ACC[3] if k != 1 else GLASS[3])
                    p.rect(x0 + mx, PANE_Y0 + 6, x0 + mx + 2, PANE_Y0 + 7, ACC[0] if k != 1 else GLASS[1])
            else:                                                        # a pendant lamp: dark shade, lit bulb
                lx = x0 + 13
                p.rect(lx, PANE_Y0 + 1, lx + 1, PANE_Y0 + 4, INK[1])
                p.rect(lx - 2, PANE_Y0 + 4, lx + 3, PANE_Y0 + 5, INK[1])
                p.rect(lx - 3, PANE_Y0 + 5, lx + 4, PANE_Y0 + 6, INK[1])
                p.rect(lx - 2, PANE_Y0 + 6, lx + 3, PANE_Y0 + 7, ACC[3])


# silhouette figures: (pane index, x centre in pane, head variant)
FIGS_A = [(1, 7, "crop"), (3, 7, "bun"), (4, 6, "cap")]
FIGS_B = [(1, 10, "crop"), (3, 5, "bun"), (4, 4, "cap")]
HEAD = {"crop": [".X.XXX.", "XXXXXXX", "XXXXXXX", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX.."],
        "bun": ["...XX..", "..XXX..", ".XXXXX.", "XXXXXXX", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX.."],
        "cap": [".XXXXX.", "XXXXXXXXX", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX.."]}
SHOULDERS = [9, 12, 14, 14, 14]


def draw_figs(r, figs):
    """Silhouettes of three coworkers behind the glass, cropped by the sill. Ink fill, ink outline, and the
    WARM rim (accent step 3, `RIM`) on the upper-left edge: they are backlit by the warm room, unlike the cool-rimmed
    people on the floor (PEOPLE_RIM)."""
    p = P(r)
    m = np.zeros(r.img.shape[:2], bool)
    for pi, fx, head in figs:
        cx = pane_x(pi) + fx
        rows = HEAD[head]
        y = PANE_Y0 + 2
        for row in rows:
            w = len(row)
            for k, ch in enumerate(row):
                if ch == "X":
                    m[OY + y, OX + cx - w // 2 + k] = True
            y += 1
        y -= 1                                   # the last head row is the neck
        for w in SHOULDERS:
            y += 1
            if y >= PANE_Y1:
                break
            m[OY + y, OX + cx - w // 2:OX + cx - w // 2 + w] = True
        while y + 1 < PANE_Y1:
            y += 1
            m[OY + y, OX + cx - 7:OX + cx + 7] = True
    pane_area = np.zeros_like(m)
    for i in range(NPANES):
        pane_area |= p.mask(pane_x(i), PANE_Y0, pane_x(i) + PANE_W, PANE_Y1)
    m &= pane_area
    r.img[m] = INK[1]
    edge = r.edge(m)
    r.img[edge] = INK[0]
    up = ~shifted(m, 0, -1)      # transparent above
    lf = ~shifted(m, -1, 0)
    r.img[edge & (up | lf)] = RIM


BAND_PHASE = {0: 5, 1: 16, 2: 9, 3: 16, 4: 16, 5: 9}   # panes with a silhouette keep their band on the right


def draw_glass(r):
    """Reflection bands over the panes, one stepped band each: glass step 3 core, glass step 2 shoulder."""
    p = P(r)
    for i in range(NPANES):
        x0 = pane_x(i)
        pane = p.mask(x0, PANE_Y0, x0 + PANE_W, PANE_Y1)
        ph = BAND_PHASE[i]
        band = pane & (np.abs((r.x - OX - x0) - (r.y - OY - PANE_Y0) * 0.8 - ph) < 1.2)
        r.img[band] = GLASS[3]
        r.img[pane & (np.abs((r.x - OX - x0) - (r.y - OY - PANE_Y0) * 0.8 - ph - 4) < 0.6)] = GLASS[2]


def draw_spill(r, core):
    """After: the lit room spills six slanted bands of warm light across the floor below the window, one hard step
    wide (fill) and a narrower brighter core. Local rows 34..61. Composited only on the bare floor fill."""
    p = P(r)
    for i in range(NPANES):
        x0 = pane_x(i)
        for dy in range(26):
            sx = x0 + 3 + int(dy * 0.55) if core else x0 + 1 + int(dy * 0.55)
            w = PANE_W - 12 if core else PANE_W - 6
            if core and dy > 18:
                continue
            p.rect(sx, 35 + dy, sx + w, 36 + dy, ACC[1] if core else ACC[0])


def landmark_pieces():
    parts = []
    box = (OX, OY, OX + BOX_W, OY + BOX_H)
    fp_room = (OX + FP[0], OY + FP[1])
    wall_tile = _wall_tile()

    def mk(name, draw, layer, collision, y_sort, note, tags, composite=None):
        rgba, painted = ok.cap(draw)
        outside = painted.copy()
        outside[box[1]:box[3], box[0]:box[2]] = False
        assert not outside.any(), f"{name} leaves the landmark box"
        sprite = rgba[box[1]:box[3], box[0]:box[2]].copy()
        p = ok.Piece(name, sprite, (OX, OY), fp_room, FP_CELLS, collision, layer, "landmark_part", y_sort=y_sort,
                     composite=composite, tags=["landmark", "interior window"] + tags, note=note)
        parts.append(p)
        return p

    zero = ["0" * FP_CELLS[0]] * FP_CELLS[1]
    full = ["1" * FP_CELLS[0]] * FP_CELLS[1]
    mk("window_wall_base", lambda r: draw_window_base(r, wall_tile), "rear_wall", full, False,
       "the 12-cell wall run: night wall tiles, silver head rail and left jamb, six mullions, silver sill. Carries the collision of the whole run", ["base"])
    mk("window_panes_before", lambda r: draw_panes(r, "before"), "rear_wall", zero, False,
       "before: six panes of dark glass, an empty unlit room beyond", ["quest state", "before"])
    mk("window_panes_after", lambda r: draw_panes(r, "after"), "rear_wall", zero, False,
       "after: the room beyond is lit warm: strip light, pendant lamps with a halo step, a shelf of mugs, a lit floor strip", ["quest state", "after", "light"])
    mk("window_figs_after_a", lambda r: draw_figs(r, FIGS_A), "rear_wall", zero, False,
       "after: three coworker silhouettes behind the glass, cropped by the sill, with a warm rim (frame a)", ["quest state", "after", "silhouettes"])
    mk("window_figs_after_b", lambda r: draw_figs(r, FIGS_B), "rear_wall", zero, False,
       "after: the same three silhouettes one step later (two have moved): alternate a and b at about 700 ms to make them move independently", ["quest state", "after", "silhouettes"])
    mk("window_glass", draw_glass, "rear_wall", zero, False,
       "reflection bands over the panes, one stepped band each, drawn above the interior and the silhouettes in both states", ["glass"])
    mk("window_spill_after", lambda r: draw_spill(r, False), "light", zero, False,
       "after: the lit room spills six slanted bands of warm light on the floor below the window (accent step 0); composited only on the bare floor fill",
       ["quest state", "after", "light"], composite={"mode": "where_color", "color": FLOOR_FILL.upper()})
    mk("window_spill_core_after", lambda r: draw_spill(r, True), "light", zero, False,
       "after: the brighter core of each band (accent step 1); composited only where the spill band is already accent step 0, so draw it after window_spill_after",
       ["quest state", "after", "light"], composite={"mode": "where_color", "color": ACC[0].upper()})
    # the contact shadow of the wall is baked into the base (rows 32-33 of the run)
    parts[0].shadow = (0, 32, BOX_W, 2)
    return parts


_WALL_TILE = None


def _wall_tile():
    global _WALL_TILE
    if _WALL_TILE is None:
        atlas = kitlib.Atlas(ORIENT_ATLAS)
        wall_maps = [(STONE_S, WALL), (GLASS_S, GLASS), ([GLASS_S[2]], [GLASS[3]])]
        _WALL_TILE = night_from_orientation(atlas, "wall_n_plain", "wall_n_plain", wall_maps, sides=("up",)).sprite
    return _WALL_TILE


# lamp positions relative to the landmark footprint origin (lamp footprint origins): one at each end of the run
LAMP_OFFSETS = [[-10, 56], [184, 40]]


def landmarks():
    before = ["window_wall_base", "window_panes_before", "window_glass"]
    after = ["window_wall_base", "window_panes_after", "window_figs_after_a", "window_glass", "window_spill_after", "window_spill_core_after"]
    return {
        "interior_window": {
            "note": "Night Shift landmark: the long interior window of the break room, 12 cells of glazing along a wall. Every part is a full-size "
                    "sprite registered at one footprint origin, so a state is a list of parts; place them all at the same cell. The base carries "
                    "the wall's collision; the spill parts are on the light layer and only recolour bare floor.",
            "size_px": [BOX_W, BOX_H],
            "footprint_origin_px": list(FP),
            "default_state": "before",
            "states": {
                "before": {"parts": before, "lamps": {"anim": "lamp", "state": "on", "offsets_px": LAMP_OFFSETS}},
                "after": {"parts": after, "lamps": {"anim": "lamp", "state": "pulse", "offsets_px": LAMP_OFFSETS}},
            },
            "part_roles": {
                "window_wall_base": "base wall", "window_panes_before": "quest state", "window_panes_after": "quest state",
                "window_figs_after_a": "quest state", "window_figs_after_b": "quest state animation frame", "window_glass": "glass",
                "window_spill_after": "quest state", "window_spill_core_after": "quest state", "lamp": "light accents",
            },
            "changes_after": [
                "the room behind the glass lights warm: strip light, pendant lamps and a lit floor (levels.md 18-19: the break room gains warm light)",
                "three coworker silhouettes appear behind the panes (levels.md 18: a coworker silhouette appears behind the interior window; 19: silhouettes move independently, frames a and b)",
                "six slanted bands of warm light fall on the floor below the window",
                "both end lamps switch from the steady glow to the wider pulse glow",
            ],
        }
    }


# ------------------------------------------------------------------ 4. quest props (levels 17 to 19 and Mira's route after 18)
# Audit: QUEST_PROP_AUDIT.md (rows N1 to N18). Night Shift ramps only. Every prop gets the district's two passes
# (shadow re-keyed darker than the floor, silver lit edge); wall overlays are lit against the indigo wall face. People are
# untouched: the rim rules of palettes/night_rim.py apply to everything placed in a room, rugs included (a rug is darker
# than the slate floor, so the moonlight rim shows on it).

QUEST_NAMES = set()
QS = (64, 64)   # capture origin for every quest prop
PAL.paper = PAL.glass   # paper, slips and label plates are the silver ramp; read only by quest_props.py


def _nq(name, draw, fp, cells, collision, layer, kind, note, tags, y_sort=True, shadow=True, box=None, wall=False, skip_rows=None, shadow_rect=None):
    """Capture a quest prop and run the Night Shift passes: shadow re-key plus silver edge against the floor fill, or, for a
    wall overlay (wall=True), against the indigo wall face."""
    p = ok.make(name, draw, fp, cells, collision, layer, kind, box=box, shadow=shadow, y_sort=y_sort, note=note, tags=tags)
    if shadow_rect:
        p.shadow = shadow_rect          # a baked shadow the capture cannot find (a wall's cast rows): known before the passes so they leave it alone
    if wall:
        p.sprite = night_shadow(p.sprite, p.shadow)
        p.sprite = edge_light(p.sprite, bg=WALL[1], shadow=p.shadow)
    else:
        finish_piece(p, skip_rows=skip_rows)
    QUEST_NAMES.add(name)
    return p


def draw_reader_pedestal(r, x0, y0, open_):
    """A free-standing card-reader pedestal for the security vestibule, 12 x 22: a silver post under a reader head with a
    slot and a status LED. locked: the LED is a warm amber. open: the LED pair is silver (confirmed)."""
    r.cast(x0 + 1, x0 + 11, y0 + 22)
    r.rect(x0 + 2, y0 + 9, x0 + 10, y0 + 22, INK[0])                      # the post
    r.rect(x0 + 3, y0 + 10, x0 + 9, y0 + 21, GLASS[1])
    r.rect(x0 + 3, y0 + 10, x0 + 4, y0 + 21, GLASS[2])
    r.rect(x0 + 8, y0 + 10, x0 + 9, y0 + 21, GLASS[0])
    r.rect(x0 + 2, y0 + 20, x0 + 10, y0 + 22, GLASS[0])                   # the base plate
    r.rect(x0 + 2, y0 + 20, x0 + 10, y0 + 21, GLASS[1])
    r.rect(x0, y0 + 1, x0 + 12, y0 + 11, INK[0])                          # the reader head
    r.rect(x0 + 1, y0 + 2, x0 + 11, y0 + 10, GLASS[1])
    r.rect(x0 + 1, y0 + 2, x0 + 11, y0 + 3, GLASS[3])
    r.rect(x0 + 2, y0 + 4, x0 + 10, y0 + 7, INK[1])                       # the card slot
    r.rect(x0 + 3, y0 + 5, x0 + 9, y0 + 6, GLASS[2])
    led = (GLASS[3], GLASS[3]) if open_ else (ACC[3], ACC[2])
    r.rect(x0 + 3, y0 + 8, x0 + 5, y0 + 9, led[1])
    r.img[y0 + 8, x0 + 3] = led[0]
    r.rect(x0 + 7, y0 + 8, x0 + 9, y0 + 9, GLASS[2])


def draw_exit_sign(r, x0, y0, lit):
    """The vestibule's back-exit sign, a 24 x 10 wall plate: a stair and an arrow. dim: a dull plate with the icon barely
    visible. lit: a warm plate with the icon in ink."""
    r.rect(x0, y0, x0 + 24, y0 + 10, INK[0])
    plate, edge, icon = (ACC[3], ACC[2], INK[0]) if lit else (GLASS[1], GLASS[0], GLASS[2])
    r.rect(x0 + 1, y0 + 1, x0 + 23, y0 + 9, plate)
    r.rect(x0 + 1, y0 + 8, x0 + 23, y0 + 9, edge)
    for xa, xb, ya in ((3, 6, 6), (6, 9, 4), (9, 12, 2)):                 # three stair steps
        r.rect(x0 + xa, y0 + ya, x0 + xb, y0 + 8, icon)
    r.rect(x0 + 13, y0 + 5, x0 + 20, y0 + 6, icon)                        # the arrow
    for k in range(4):
        r.rect(x0 + 18 + k, y0 + 3 + k, x0 + 19 + k, y0 + 8 - k, icon)


def draw_north_stair(r, x0, y0, state):
    """The north stair door of level 18, a north-wall door 2 cells wide and 34 px tall (the wall's own height; it replaces
    two plain wall tiles and carries their cap). A stair sign on the lintel. closed: a silver lock grille with an amber lock
    bar. open: the grille is folded to the left and the stair climbs to a warm landing."""
    t = _wall_tile()
    for i in range(2):
        for y in range(6):
            for x in range(16):
                if t[y, x, 3]:
                    r.img[y0 + y, x0 + i * 16 + x] = t[y, x, :3]
    r.rect(x0, y0 + 6, x0 + 32, y0 + 32, INK[0])
    r.rect(x0 + 1, y0 + 7, x0 + 3, y0 + 32, GLASS[1])
    r.rect(x0 + 1, y0 + 7, x0 + 2, y0 + 32, GLASS[3])
    r.rect(x0 + 29, y0 + 7, x0 + 31, y0 + 32, GLASS[1])
    r.rect(x0 + 30, y0 + 7, x0 + 31, y0 + 32, GLASS[0])
    r.rect(x0 + 1, y0 + 7, x0 + 31, y0 + 14, GLASS[1])                    # lintel
    r.rect(x0 + 3, y0 + 7, x0 + 29, y0 + 8, GLASS[3])
    r.rect(x0 + 10, y0 + 8, x0 + 22, y0 + 14, ACC[2])                     # the stair sign
    r.rect(x0 + 10, y0 + 8, x0 + 22, y0 + 9, ACC[3])
    for xa, xb, ya in ((11, 14, 12), (14, 17, 10), (17, 21, 9)):
        r.rect(x0 + xa, y0 + ya, x0 + xb, y0 + 14, INK[1])
    ox0, ox1, oy0, oy1 = x0 + 3, x0 + 29, y0 + 14, y0 + 31
    if state == "closed":
        r.rect(ox0, oy0, ox1, oy1, INK[1])
        for bx in range(ox0 + 1, ox1 - 1, 3):                             # grille bars
            r.rect(bx, oy0, bx + 1, oy1, GLASS[2])
            r.rect(bx, oy0, bx + 1, oy0 + 1, GLASS[3])
        r.rect(ox0 + 1, oy0 + 7, ox1 - 1, oy0 + 9, ACC[2])               # the lock bar
        r.rect(ox0 + 1, oy0 + 7, ox1 - 1, oy0 + 8, ACC[3])
        r.rect(ox0, oy1 - 3, ox1, oy1, GLASS[0])
        r.rect(ox0, oy1 - 3, ox1, oy1 - 2, GLASS[2])
    else:
        r.rect(ox0, oy0, ox1, oy1, WALL[0])
        r.rect(ox0, oy0, ox1, oy0 + 3, ACC[0])                            # the warm landing above
        r.rect(ox0 + 6, oy0, ox1 - 6, oy0 + 2, ACC[1])
        surf = [GLASS[2], GLASS[1], WALL[3], WALL[2], WALL[1]]            # five treads, near to far
        for i in range(5):
            y = oy1 - 3 - 3 * i
            r.rect(ox0 + 2, y, ox1 - 2, y + 2, surf[i])
            r.rect(ox0 + 2, y + 2, ox1 - 2, y + 3, INK[1])
        r.rect(ox0, oy0, ox0 + 6, oy1, INK[1])                            # the folded grille at the left
        for bx in (ox0 + 1, ox0 + 3):
            r.rect(bx, oy0, bx + 1, oy1, GLASS[2])
            r.rect(bx, oy0, bx + 1, oy0 + 1, GLASS[3])
    r.rect(x0 + 1, y0 + 31, x0 + 31, y0 + 32, GLASS[0])                   # threshold
    if state == "closed":
        r.rect(x0, y0 + 32, x0 + 32, y0 + 33, FLOOR[0])                   # cast shadow, as the wall draws it (darker than the floor)
        r.rect(x0, y0 + 33, x0 + 32, y0 + 34, INK[0])


def _rug(kind):
    """A 3 x 2 cell rug as a 48 x 32 RGBA sprite. Three patterns so the three desk islands of level 18 are told apart by
    the floor, not only by the lamps: a (indigo diamonds, blue border), b (warm stripes, wood border), c (green chevrons). Every rug
    colour is dark enough (under 0.19 luminance) that the silver edge of a desk or chair standing on it keeps 3:1."""
    H, W = 32, 48
    yy, xx = np.mgrid[0:H, 0:W]
    edge0 = (yy == 0) | (yy == H - 1) | (xx == 0) | (xx == W - 1)
    edge1 = ((yy == 1) | (yy == H - 2) | (xx == 1) | (xx == W - 2)) & ~edge0
    inner = (yy >= 4) & (yy < H - 4) & (xx >= 4) & (xx < W - 4)
    if kind == "a":
        field, border, deep, line = WALL[1], GLASS[1], WALL[0], WALL[2]
        pat = (((xx + yy) % 8 == 0) | ((xx - yy) % 8 == 0)) & inner
    elif kind == "b":
        field, border, deep, line = WOOD[1], WOOD[2], WOOD[0], WOOD[2]
        pat = (((yy - 4) % 6) < 2) & inner
    else:
        field, border, deep, line = FOLI[0], FOLI[2], INK[0], FOLI[1]
        zig = np.abs((xx % 12) - 6)
        pat = (((yy + zig) % 8) < 2) & inner
    rgba = np.zeros((H, W, 4), np.uint8)
    for m, col in ((np.ones((H, W), bool), field), (pat, line), (edge1, deep), (edge0, border)):
        rgba[m, :3] = rgb(col)
    rgba[:, :, 3] = 255
    if kind == "b":
        rgba[(((yy - 4) % 6) == 3) & inner, :3] = rgb(WOOD[0])
    return rgba


def quest_pieces():
    """The Night Shift quest props. Returns (pieces, state sets)."""
    out = []
    sx, sy = QS
    for st in ("locked", "open"):
        out.append(_nq(f"reader_pedestal_{st}", lambda r, st=st: draw_reader_pedestal(r, sx, sy, st == "open"), (sx, sy + 6), (1, 1), ["1"], "rear_prop", "prop",
                       "a free-standing card-reader pedestal for the security vestibule, 12 x 22, 1 x 1 (level 17). "
                       + ("locked: an amber status LED" if st == "locked" else "open: the status LEDs are silver, the reader confirmed")
                       + ". It blocks its cell in both states (the gate, not the pedestal, opens the way)", ["reader", "vestibule", "security", "level 17", st],
                       box=(sx, sy, sx + 13, sy + 24)))
    for st in ("dim", "lit"):
        out.append(_nq(f"exit_sign_{st}", lambda r, st=st: draw_exit_sign(r, sx, sy, st == "lit"), (sx, sy), (2, 1), ["00"], "rear_wall", "wall",
                       "the vestibule's back-exit sign (level 17: a vestibule with a clear back exit), a 24 x 10 wall plate with a stair and an arrow. "
                       + ("dim: a dull plate, the icon barely visible" if st == "dim" else "lit: a warm plate with the icon in ink") + ". Place above the back exit; the plain wall already blocks",
                       ["sign", "exit", "vestibule", "level 17", st], y_sort=False, shadow=False, wall=True, box=(sx, sy, sx + 24, sy + 10)))
    for st in ("closed", "open"):
        out.append(_nq(f"north_stair_{st}", lambda r, st=st: draw_north_stair(r, sx, sy, st), (sx, sy), (2, 2), ["11", "11"] if st == "closed" else ["00", "00"],
                "rear_wall", "door",
                "the north stair door of level 18 (Ada opens the north stair), a north-wall door 32 x 34 px that replaces two plain wall tiles and carries their cap: a stair sign on the lintel. "
                + ("closed: a silver lock grille with an amber lock bar; blocks" if st == "closed" else "open: the grille is folded to the left, the stair climbs to a warm landing; walkable")
                + ". Do not put plain wall tiles under it", ["door", "stair", "north stair", "level 18", st], y_sort=False, shadow=False, wall=True,
                box=(sx, sy, sx + 32, sy + 34), shadow_rect=(0, 32, 32, 2) if st == "closed" else None))
    for k in ("a", "b", "c"):
        rgba = _rug(k)
        out.append(_px_piece(f"carpet_cue_{k}", rgba, (3, 2), ["000", "000"], "floor_marking", "tile",
                             "a 3 x 2 rug on the floor markings (level 18: the Caps route uses varied lamp and carpet cues): "
                             + {"a": "indigo diamonds with a blue border", "b": "warm stripes with a wood border", "c": "green chevrons with a green border"}[k]
                             + ". Darker than the slate floor, so people keep the moonlight rim on it; never uses the lamp-pool accent steps 0 and 1. Walkable",
                             ["rug", "carpet", "level 18", k]))
        QUEST_NAMES.add(f"carpet_cue_{k}")
    for st in ("idle", "ready"):
        out.append(_nq(f"courier_chute_{st}", lambda r, st=st: qp.courier_chute(r, sx, sy, PAL, st == "ready"), (sx, sy + 12), (2, 1), ["11"], "rear_prop", "prop",
                       "Mira's courier chute, 2 x 1: a metal cabinet with a slot, a tube rising into the ceiling, a catch tray and an indicator lamp. "
                       + ("idle: the lamp is dull, the slot empty" if st == "idle" else "ready (Mira has a route to offer): a slip stands in the slot and the lamp is lit warm")
                       + ". Silver edge", ["chute", "mira", "courier", st], box=(sx, sy, sx + 34, sy + 30)))
    out.append(_nq("mira_decor_night_courier", lambda r: qp.mira_decor(r, "night_courier", sx, sy, PAL), (sx - 2, sy + 10 - 16), (1, 1), ["0"], "rear_prop", "prop",
                   "Night Courier reward (after level 18): a small satchel with a warm strap and a crescent charm; a desk decoration, 1 x 1, no collision. Silver edge",
                   ["decor", "mira", "desk"], shadow=False))
    out.append(break_counter(lit=False))
    QUEST_NAMES.add("break_counter_dim")
    out += pool_pieces("pool_breaktop", 31, 11, (31 - 24, 11 - 14),
                       "Break-counter pool, 62x22 px: centre 24 px right and 14 px below the break counter's footprint origin, so a state set can carry the counter and its pool together.",
                       ["break room", "counter"])
    for p in out[-2:]:
        QUEST_NAMES.add(p.name)
    anims = {
        "reader_pedestal": {"kind": "state_set", "default": "locked",
                            "states": {"locked": {"entries": ["reader_pedestal_locked"]}, "open": {"entries": ["reader_pedestal_open"]}},
                            "play": ["locked", "open"], "ms_per_frame": 200,
                            "note": "level 17: the vestibule reader confirms; pair with vestibule_gate"},
        "exit_sign": {"kind": "state_set", "default": "dim",
                      "states": {"dim": {"entries": ["exit_sign_dim"]}, "lit": {"entries": ["exit_sign_lit"]}},
                      "play": ["dim", "lit"], "ms_per_frame": 200,
                      "note": "level 17: the back-exit sign comes on once the player confirms the exit instruction"},
        "north_stair": {"kind": "state_set", "default": "closed",
                        "states": {"closed": {"entries": ["north_stair_closed"], "blocked": True}, "open": {"entries": ["north_stair_open"], "blocked": False}},
                        "play": ["closed", "open"], "ms_per_frame": 200,
                        "note": "level 18: Ada opens the north stair; open leaves rows 0-1 of its cells walkable"},
        "courier_chute": {"kind": "state_set", "default": "idle",
                          "states": {"idle": {"entries": ["courier_chute_idle"]}, "ready": {"entries": ["courier_chute_ready"]}},
                          "play": ["idle", "ready"], "ms_per_frame": 300,
                          "note": "Mira's chute: ready while she has a route to offer (Lights-Out Delivery, after level 18)"},
        "break_room": {"kind": "state_set", "default": "dim",
                       "states": {"dim": {"entries": ["break_counter_dim"]}, "warm": {"entries": ["break_counter", "pool_breaktop_fill", "pool_breaktop_seam"]}},
                       "play": ["dim", "warm"], "ms_per_frame": 300,
                       "note": "levels 17 and 19: the break room's warm-light state. Place at the counter's cell; warm adds the counter's lit lamp and its pool of light. The long window's own light is the interior_window landmark"},
        "corridor_light": {"kind": "state_set", "default": "dim",
                           "states": {"dim": {"entries": ["lamp_off"]}, "lit": {"entries": ["lamp", "lamp_glow_on", "pool_route_fill", "pool_route_seam"]}},
                           "play": ["dim", "lit"], "ms_per_frame": 300,
                           "note": "level 19: the service corridor lights up. Place one per 4 to 5 cells along the corridor: an unlit lamp, then the lamp with a pool of route light centred on it"},
    }
    return out, anims


# ------------------------------------------------------------------ 6. wave 2: district integration
# The shared elevator set and call panel, the Executive-stop panel, one artifact (quest_props.integration_pieces, drawn with the
# Night Shift ramps and run through the same silver-edge and shadow passes as every other prop) and the Night Shift props the level
# data names (design/levels/nightshift/NEEDS_ART.md): wall_w_plain and the desk_dawn_lamp reward. Night Shift has no desk_a or
# desk_b (its desks are desk_dead_* and desk_lit_*), so there are no occluders here.

INTEGRATION_NAMES = set()


def _imk(name, draw, box, fp, cells, coll, layer, kind, shadow=True, shadow_rect=None, y_sort=False, note="", tags=()):
    wall = layer == "rear_wall"
    if name in ("elevator_closed", "elevator_half", "elevator_open"):
        # the elevator is a full wall slice: its cap and casing already carry the wall's own trim, and a silver outline round the whole
        # module would draw seams down the wall at its sides. Shadow re-key and the top-edge light only (as wall_n_plain), no side edges.
        p = ok.make(name, draw, fp, cells, coll, layer, kind, box=box, shadow=shadow, y_sort=y_sort, note=note, tags=list(tags))
        p.shadow = shadow_rect
        p.sprite = night_shadow(p.sprite, p.shadow)
        p.sprite = edge_light(p.sprite, bg=WALL[1], shadow=p.shadow, sides=("up",))   # the same top-edge light as wall_n_plain, so the cap runs on
    else:
        p = _nq(name, draw, fp, cells, coll, layer, kind, note, list(tags), y_sort=y_sort, shadow=shadow, box=box, wall=wall, shadow_rect=shadow_rect)
    INTEGRATION_NAMES.add(name)
    QUEST_NAMES.discard(name)   # _nq registers every name as a quest prop; these belong to the integration proof room
    return p


def wall_w_plain():
    """The west-wall side plane: 13 x 16 px, tiles vertically. The wall mass is the ink ramp; its room-facing edge is on the RIGHT and
    faces away from the upper-left light, so it takes no lit trim there (a mirror of wall_e_plain would light the wrong edge): a 1 px silver line on the
    left (the lit side, so the silhouette keeps its 3:1 edge), ink mass, a one-step indigo shoulder, and a dim wall-ramp edge line."""
    a = np.zeros((16, 13, 4), np.uint8)
    cols = [GLASS[3]] + [INK[0]] * 9 + [INK[1], WALL[1], WALL[2]]
    for x, c in enumerate(cols):
        a[:, x, :3] = rgb(c)
        a[:, x, 3] = 255
    return _px_piece("wall_w_plain", a, (1, 1), ["0"], "rear_wall", "wall",
                     "west wall segment, side plane seen from inside (the face between the service corridor and the hall): ink mass with a 1 px silver line on its left (the edge that catches the upper-left light) and its room-facing edge on the right. "
                     "That face looks away from the light, so its trim is a dim indigo step, not the silver of wall_e_plain, which cannot be mirrored. Tiles vertically; "
                     "no collision of its own (the map blocks the wall elsewhere). Place so its right edge is the cell boundary: the sprite fills the cell's left 13 px",
                     ["wall", "west", "side plane", "wave 2"])


def _integration():
    out, anims = qp.integration_pieces(lambda *a, **k: _imk(*a, **k), PAL, "nightshift", None)
    x0, y0 = qp.IX0, qp.IY0
    out.append(wall_w_plain())
    INTEGRATION_NAMES.add("wall_w_plain")
    out.append(_imk("desk_dawn_lamp", lambda r: qp.reward_decor(r, "dawn_lamp", x0, y0, PAL), (x0, y0, x0 + 10, y0 + 13), (x0 - 3, y0 + 13 - 16), (1, 1), ["0"], "front_prop", "prop",
                    shadow=False, y_sort=False,
                    note="Desk for Dawn reward: a small desk lamp (wood foot and stem under a warm shade with one lit step and a pale glint), 10 x 13, 1 x 1, no collision, "
                         "silver edge. A desk decoration like mail_tray and desk_folder; never placed on the map", tags=["decor", "desk", "reward", "dawn"]))
    return out, anims


# ------------------------------------------------------------------ assembly

def build_pieces():
    atlas = kitlib.Atlas(ORIENT_ATLAS)
    pieces = recoloured_pieces(atlas)
    pieces += route_arrows()
    pieces += lamp_pools()
    pieces += shared_pieces()
    pieces.append(break_counter())
    pieces.append(ledger_desk())
    pieces.append(noticeboard())
    pieces += vestibule_gate()
    pieces += landmark_pieces()
    qpieces, qanims = quest_pieces()
    pieces += qpieces
    ipieces, ianims = _integration()
    pieces += ipieces
    anims = {
        "service_door": {
            "kind": "state_set", "default": "closed",
            "states": {"closed": {"entries": ["service_door_closed"], "blocked": True},
                       "half": {"entries": ["service_door_half"], "blocked": True},
                       "open": {"entries": ["service_door_open"], "blocked": False}},
            "play": ["closed", "half", "open"], "ms_per_frame": 120,
            "note": "play forward on approach, backward on leave; Orientation's sliding glass door recoloured with a lamp-ramp frame and a stair sign",
        },
        "lamp": {
            "kind": "state_set", "default": "on",
            "states": {"off": {"entries": ["lamp_off"]}, "on": {"entries": ["lamp", "lamp_glow_on"]},
                       "pulse": {"entries": ["lamp", "lamp_glow_pulse"]}},
            "loop": ["on", "pulse"], "ms_per_frame": 600,
            "note": "glow states: off, on (steady), pulse (wider ring). Wake = off -> on; idle breathing = on <-> pulse. Level 18: each repaired ticket wakes a different lamp.",
        },
        "vestibule_gate": {
            "kind": "state_set", "default": "closed",
            "states": {"closed": {"entries": ["vestibule_gate_closed"], "blocked": True},
                       "open": {"entries": ["vestibule_gate_open"], "blocked": False}},
            "play": ["closed", "open"], "ms_per_frame": 200,
            "note": "the security vestibule gate (level 17): opens after the player confirms the practice-mode exit; open leaves a two-cell walkway",
        },
        "station_a": {
            "kind": "state_set", "default": "dead",
            "states": {"dead": {"entries": ["desk_dead_a"]},
                       "lit": {"entries": ["desk_lit_a", "pool_desk_fill", "pool_desk_seam"]}},
            "play": ["dead", "lit"], "ms_per_frame": 300,
            "note": "an office station that wakes (level 18: each repaired ticket wakes a different lamp): the legacy desk goes dark to lit and its pool of desk light switches on. Place at the desk's cell; the chair is a separate entry",
        },
        "station_b": {
            "kind": "state_set", "default": "dead",
            "states": {"dead": {"entries": ["desk_dead_b"]},
                       "lit": {"entries": ["desk_lit_b", "pool_desk_fill", "pool_desk_seam"]}},
            "play": ["dead", "lit"], "ms_per_frame": 300,
            "note": "the b variant of station_a (plant leaves differ)",
        },
        "window_figs": {
            "kind": "state_set", "default": "a",
            "states": {"a": {"entries": ["window_figs_after_a"]}, "b": {"entries": ["window_figs_after_b"]}},
            "loop": ["a", "b"], "ms_per_frame": 700,
            "note": "the silhouettes behind the interior window in the after state; swap window_figs_after_a for this loop (level 19: silhouettes move independently)",
        },
    }
    anims.update(qanims)
    anims.update(ianims)
    return pieces, anims, landmarks()


def group_rank(p):
    n = p.name
    if n in INTEGRATION_NAMES:
        return 9
    if n in QUEST_NAMES:
        return 8
    if n.startswith(("floor_", "route_")):
        return 0
    if n.startswith("wall_"):
        return 1
    if n.startswith("service_door"):
        return 2
    if n.startswith("lamp"):
        return 3
    if n.startswith("pool_"):
        return 4
    if n.startswith(("desk_", "chair", "pot_plant", "sofa", "side_table")):
        return 5
    if n.startswith(("shelf", "partition", "terminal", "cabinet", "break_counter", "ledger_desk", "vestibule")):
        return 6
    return 7


SECTIONS = [(0, "FLOOR, ROUTE AND WAYFINDING"), (1, "WALLS (lit edges)"), (2, "SLIDING GLASS SERVICE DOOR (closed, half, open)"),
            (3, "LAMP (post, off, glow states)"), (4, "LAMP POOLS (light layer: fill + seam pairs)"),
            (5, "RECOLOURED ORIENTATION PROPS (dead and lit stations, chair, plants, sofa)"),
            (6, "NIGHT SHIFT KIT: shared pieces, break counter, ledger desk, vestibule gate"),
            (7, "LANDMARK: THE LONG INTERIOR WINDOW (registered parts)"),
            (8, "QUEST PROPS (levels 17 to 19, Mira's route): reader pedestal, exit sign, north stair, rugs, courier chute, dim break counter, Mira decor"),
            (9, "DISTRICT INTEGRATION (wave 2): elevator set, call panel (base and Executive stop lit), west-wall side plane, Ada's shift book, the dawn lamp")]


def atlas_json(pieces, rects, anims, lms):
    return {
        "schema": "atlas.schema.json",
        "kit": KIT,
        "image": "nightshift-atlas.png",
        "tile": T,
        "layers": kitlib.LAYERS,
        "status": "Approved by the director 2026-10-02",
        "source": "Orientation pieces recoloured by exact hex swap (nightshift_kit.py) plus the Night Shift shadow and lit-edge passes, "
                  "shared pieces from shared_pieces.py, Night Shift pieces and landmark; build_nightshift.py",
        "entries": [p.entry(rects[p.name]) for p in pieces],
        "animations": anims,
        "landmarks": lms,
    }
