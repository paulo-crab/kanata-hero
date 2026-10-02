"""Executive environment kit (task 7.4): atlas pieces, the atrium tree landmark and the reference room layout.

Four sources of art, all palette-only (Executive ramps: ink, floor, wall, glass, wood, foliage, accent):
  1. Orientation pieces recoloured by an exact hex swap (floor, walls, windows, door, lamp, desk, chair,
     sofa, bench, planters). `recolour_rect` raises on any pixel without a mapping.
  2. District-agnostic pieces from shared_pieces.py (shelving, partition, terminal desk, cabinet, light
     shaft), drawn with Executive ramps (a walnut / paper variant of the Pal for the bookcase and credenza).
  3. Executive-only pieces: long boardroom table, boardroom chair, glass balustrade, copper wall trim,
     copper route arrows.
  4. The landmark: the atrium tree in a raised planter inside a sunken atrium well.

Local helpers live here (not in kitlib.py / shared_pieces.py, which other districts share).
"""
import copy
import math
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
KIT = "executive"
PAL = sp.Pal("executive")
E = dp.DISTRICTS["executive"]
O = dp.DISTRICTS["orientation"]
INK, shifted, hx = bst.INK, bst.shifted, bst.hx

FLOOR, WALL, GLASS, WOOD, FOL, ACC = (PAL.floor, PAL.wall, PAL.glass, PAL.wood, PAL.foliage, PAL.accent)
FLOOR_FILL = E["floor"][3]    # the bare floor colour a light composite may recolour
WELL_FLOOR = E["floor"][2]    # inside the well the floor is the stone mid step; the daylight pool paints floor step 3 over it
COOL_LIGHT = E["glass"][3]    # overcast window light
WARM_LIGHT = E["accent"][3]   # daylight that has warmed

ORIENT_ATLAS = os.path.join(HERE, "orientation-atlas.json")
STONE_S, GLASS_S, WOOD_S, GREEN_S, BRASS_S = (O["floor"], O["glass"], O["wood"], O["foliage"], O["accent"])
CORAL_S = dp.ORIENTATION_EXTRA["coral"]


# ------------------------------------------------------------------ 1. recoloured Orientation pieces

def _ramp_map(src, dst):
    return {s.upper(): d.upper() for s, d in zip(src, dst)}


def _merge(maps):
    out = {}
    for s, d in maps:
        out.update(_ramp_map(s, d))
    return out


def recolour_rect(sprite, maps, rules=()):
    """Exact hex swap. maps: [(src_ramp, dst_ramp)]. rules: [(x0, y0, x1, y1, maps)]: inside that rectangle
    the rule's maps replace the base maps (and may remap ink steps). Ink is otherwise shared and left alone.
    Raises on an unmapped colour."""
    out = sprite.copy()
    base = _merge(maps)
    rms = [(r[0], r[1], r[2], r[3], _merge(r[4])) for r in rules]
    ink = {h.upper() for h in dp.INK}
    for y in range(sprite.shape[0]):
        for x in range(sprite.shape[1]):
            if sprite[y, x, 3] == 0:
                continue
            m = base
            for x0, y0, x1, y1, rm in rms:
                if x0 <= x < x1 and y0 <= y < y1:
                    m = rm
            h = kitlib.hexs(sprite[y, x, :3])
            if h in m:
                out[y, x, :3] = kitlib.hex2rgb(m[h])
            elif h in ink:
                continue
            else:
                raise AssertionError(f"unmapped colour {h} at ({x},{y})")
    return out


def from_orientation(atlas, src, new, maps, rules=(), note="", tags=(), comp_color=None, name_map=None):
    e = atlas.entries[src]
    sprite = recolour_rect(atlas.sprite(src), maps, rules)
    ox, oy = e["footprint"]["origin_px"]
    comp = dict(e.get("composite", {"mode": "over"}))
    if comp["mode"] == "where_color":
        comp["color"] = comp_color
    return ok.Piece(new, sprite, (0, 0), (ox, oy), tuple(e["footprint"]["cells"]), list(e["collision"]), e["layer"],
                    e["kind"], y_sort=e.get("y_sort", False), composite=comp, shadow=e.get("contact_shadow"),
                    tags=list(tags) or list(e.get("tags", [])), note=note or e.get("note", ""))


def draw_sun_sign(sprite):
    """Final-door sign icon: a sunrise (the door opens to daylight) replacing Orientation's folder icon.
    The icon sits in the frame rows 3-8, columns 10-19 of the door sprite. Palette steps only."""
    g3, g2, c3, c2 = kitlib.hex2rgb(E["glass"][3]), kitlib.hex2rgb(E["glass"][2]), kitlib.hex2rgb(E["accent"][3]), kitlib.hex2rgb(E["accent"][2])
    ink1, ink0 = kitlib.hex2rgb(dp.INK[1]), kitlib.hex2rgb(dp.INK[0])

    def put(x, y, c):
        sprite[y, x, :3] = c
        sprite[y, x, 3] = 255
    for y in range(3, 9):               # frame ground
        for x in range(10, 20):
            put(x, y, ink1)
    for y in (3, 8):
        for x in range(10, 20):
            put(x, y, ink0)
    for y in range(3, 9):
        put(10, y, ink0)
        put(19, y, ink0)
    for x in range(11, 19):             # horizon line in copper
        put(x, 7, c2)
    for x in (13, 14, 15, 16):          # sun disc rising on the horizon
        put(x, 6, g3)
    for x in (14, 15):
        put(x, 5, g3)
    for x, y in ((11, 5), (12, 4), (17, 4), (18, 5)):   # rays
        put(x, y, c3)
    put(14, 4, c3)
    put(15, 4, c3)
    return sprite


def recoloured_pieces(atlas):
    pieces = []
    floor_maps = [(STONE_S, E["floor"])]
    for nm, desc in (("floor_j", "slab corner: joint on the top row and the left column"),
                     ("floor_h", "slab edge: joint on the top row"), ("floor_v", "slab edge: joint on the left column"),
                     ("floor_p", "slab interior, plain")):
        pieces.append(from_orientation(atlas, nm, nm, floor_maps, note=f"Executive floor, {desc}. Pale limestone, broad slabs, no grain",
                                       tags=["floor", "slab"]))
    pieces.append(from_orientation(atlas, "floor_chip", "floor_chip", floor_maps,
                                   note="2x1 px wear mark on the floor layer; placed with a pixel offset"))
    pieces.append(from_orientation(atlas, "route_inlay", "route_inlay", [([STONE_S[2]], [E["floor"][1]])],
                                   note="1 px inlay line in floor step 1 along a route edge; repeat every 16 px (horizontal). "
                                        "Neutral stone: copper is kept for the landmark's floor lines and the arrows"))
    v = np.rot90(pieces[-1].sprite, 1).copy()
    pieces.append(ok.Piece("route_inlay_v", v, (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                           note="route_inlay turned 90 degrees: the same line for vertical corridor edges", tags=["floor", "route"]))
    # walls: navy faces, sky-glass windows
    wall_maps = [(STONE_S, E["wall"]), (GLASS_S, E["glass"])]
    pieces.append(from_orientation(atlas, "wall_n_plain", "wall_n_plain", wall_maps,
                                   note="north wall segment: ink cap with a sky-glass trim, navy face, baseboard and cast shadow; tiles horizontally"))
    for nm in ("wall_n_window_a", "wall_n_window_b"):
        pieces.append(from_orientation(atlas, nm, nm, wall_maps,
                                       note="high window overlay, daylight state: dark frame, sky-blue pane, one stepped reflection band, lit sill. "
                                            "Phase a and b differ only in the band position"))
    dim = [(STONE_S, E["wall"]), ([GLASS_S[0], GLASS_S[1], GLASS_S[2], GLASS_S[3]], [E["glass"][0], E["glass"][0], E["glass"][1], E["glass"][1]])]
    for nm in ("a", "b"):
        pieces.append(from_orientation(atlas, f"wall_n_window_{nm}", f"wall_n_window_{nm}_dim", dim,
                                       note="high window overlay, overcast state (before the third repair): flat dark panes, no reflection band, a dull sill. "
                                            "The daylight state is wall_n_window_" + nm, tags=["wall", "window", "overcast"]))
    pieces.append(from_orientation(atlas, "wall_n_alcove", "wall_n_alcove", wall_maps + [(BRASS_S, E["accent"])],
                                   note="brighter navy alcove with a copper nameplate bar and three inked marks, behind a reception console or Vale's post"))
    # east wall: the navy ramp replaces the ink mass, so the wall matches the north wall
    east = [([STONE_S[0]], [E["wall"][0]]), ([GLASS_S[2]], [E["glass"][2]])]
    ink_navy = [(dp.INK[0:3], E["wall"][0:3])]
    pieces.append(from_orientation(atlas, "wall_e_plain", "wall_e_plain", east + ink_navy,
                                   note="east wall segment, side plane in the navy ramp with a sky-glass lit trim; tiles vertically. Content starts 4 px into the first cell"))
    # Door: copper frame, sky-glass leaves, a daylit terrace beyond and a sunrise sign on the lintel.
    door_maps = [(BRASS_S, E["accent"]), (GLASS_S, E["glass"]), (STONE_S, E["floor"]), (CORAL_S, [E["glass"][3]] * 4)]
    beyond = [(0, 0, 31, 68, door_maps)]
    # interior beyond the leaves (x >= 10, rows 25 to 59): glass1/0 grid -> daylit terrace; cabinet -> hedge with copper blooms
    terrace = [([GLASS_S[1], GLASS_S[0]], [E["floor"][3], E["floor"][2]]),
               ([STONE_S[3], STONE_S[2], STONE_S[0]], [E["foliage"][3], E["foliage"][2], E["foliage"][0]]),
               ([BRASS_S[2]], [E["foliage"][3]]), ([GLASS_S[3]], [E["foliage"][3]])]
    mass = [(dp.INK[0:1], [E["wall"][0]]), (dp.INK[1:2], [E["wall"][1]])]
    rules = [(11, 25, 31, 60, terrace),
             (25, 0, 31, 14, door_maps + mass),
             (5, 12, 31, 14, door_maps + mass),
             (3, 0, 5, 14, door_maps + [(dp.INK[2:3], [E["wall"][2]])])]
    for st, note in (("closed", "both glass leaves shut: copper frame, sky-glass leaves, seam, pulls, sunrise sign; a daylit terrace shows through"),
                     ("half", "leaves slid 8 px into the jamb pockets: the terrace and its hedge show through"),
                     ("open", "leaves fully in the pockets (15 px): the doorway is open and bright with daylight")):
        p = from_orientation(atlas, f"records_door_{st}", f"final_door_{st}", door_maps, rules=rules, note=note,
                             tags=["door", "sliding glass", "final door", st])
        draw_sun_sign(p.sprite)
        pieces.append(p)
    lamp_maps = [(BRASS_S, E["accent"])]
    pieces.append(from_orientation(atlas, "lamp", "lamp", lamp_maps, note="floor lamp: dark post, copper lamp head with one lit step, contact shadow"))
    pieces.append(from_orientation(atlas, "lamp_off", "lamp_off", lamp_maps, note="unlit lamp: head in the ink ramp, no glow"))
    pieces.append(from_orientation(atlas, "lamp_glow_on", "lamp_glow_on", lamp_maps, comp_color=FLOOR_FILL,
                                   note="glow, one hard warm step (radius 5.2). Paints only where the floor is the bare fill "
                                        f"{FLOOR_FILL}, so it never washes over joints, inlays, props or walls"))
    pieces.append(from_orientation(atlas, "lamp_glow_pulse", "lamp_glow_pulse", lamp_maps, comp_color=FLOOR_FILL,
                                   note="pulse frame of the glow, radius 6.4; alternate with lamp_glow_on at about 600 ms each"))
    desk_maps = [(WOOD_S, E["wood"]), (GLASS_S, E["glass"]), (STONE_S, E["floor"]), (GREEN_S, E["foliage"])]
    for nm in ("desk_a", "desk_b"):
        pieces.append(from_orientation(atlas, nm, nm, desk_maps,
                                       note="two-cell walnut desk with monitor, keyboard, paper and a small plant (a and b differ only in the plant leaves); the chair is a separate entry"))
    navy = [(CORAL_S, E["wall"])]
    pieces.append(from_orientation(atlas, "chair", "chair", navy,
                                   note="dark navy task chair seen from above; place 11 px right and 18 px below a desk origin"))
    pieces.append(from_orientation(atlas, "sofa", "sofa", [(WOOD_S, E["wall"])],
                                   note="dark navy lounge sofa seen from above: the seating Vale has to read against (suit lit-edge step)", tags=["seating", "navy"]))
    pieces.append(from_orientation(atlas, "bench", "bench", [(WOOD_S, E["wood"])],
                                   note="slatted walnut bench", tags=["seating"]))
    pieces.append(from_orientation(atlas, "side_table", "side_table", [(GREEN_S, E["foliage"])],
                                   note="round slate side table with a small plant", tags=["table", "plant"]))
    for nm in ("pot_plant_a", "pot_plant_b", "pot_plant_c", "pot_plant_d"):
        pieces.append(from_orientation(atlas, nm, nm, [(GREEN_S, E["foliage"])],
                                       note="slate planter with a living-green plant; four leaf layouts (a to d)"))
    return pieces


# ------------------------------------------------------------------ 2. shared pieces, captured

def paper_pal(glass_as_wood=False):
    """A Pal clone for the credenza and bookcase: pale paper and labels (floor ramp) instead of navy;
    optionally walnut for the frame (shelf frames use the glass ramp in the shared piece)."""
    p = copy.copy(PAL)
    p.wall = PAL.floor
    if glass_as_wood:
        p.glass = PAL.wood
    return p


def book_triples():
    """(light, body, dark) triples for bound volumes: copper, navy, pale stone, sky glass."""
    return [(ACC[3], ACC[2], ACC[1]), (WALL[3], WALL[2], WALL[1]), (FLOOR[3], FLOOR[2], FLOOR[1]),
            (GLASS[3], GLASS[2], GLASS[1])]


def shared_pieces():
    out = []
    sx, sy = 64, 64
    bookcase = paper_pal(glass_as_wood=True)
    note_shelf = "{n}-cell walnut bookcase: top plane, front face with three bays, bound volumes in clusters (copper, navy, pale stone, sky blue), kick plate"
    out.append(ok.make("shelf_1x1", lambda r: sp.shelf(r, sx, sy, 1, bookcase, 3, triples=book_triples()), (sx, sy + sp.SHELF_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note=note_shelf.format(n=1), tags=["shelf", "bookcase"]))
    for nm, seed in (("shelf_2x1_a", 1), ("shelf_2x1_b", 2)):
        out.append(ok.make(nm, lambda r, seed=seed: sp.shelf(r, sx, sy, 2, bookcase, seed, triples=book_triples()), (sx, sy + sp.SHELF_H - 16), (2, 1), ["11"],
                           "rear_prop", "prop", y_sort=True, note=note_shelf.format(n=2) + "; a and b differ only in the volume layout",
                           tags=["shelf", "bookcase"]))
    out.append(ok.make("partition_1x1", lambda r: sp.partition(r, sx, sy, 1, PAL), (sx, sy + sp.PART_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note="free-standing glass partition, one cell: sky-blue frame with lit cap, pale pane, one reflection band, floor rail",
                       tags=["partition", "glass"]))
    out.append(ok.make("partition_2x1", lambda r: sp.partition(r, sx, sy, 2, PAL), (sx, sy + sp.PART_H - 16), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True, note="free-standing glass partition, two cells, with a middle post and a reflection band per pane",
                       tags=["partition", "glass"]))
    out.append(ok.make("terminal_desk", lambda r: sp.terminal_desk(r, sx, sy + 8, PAL), (sx, sy + 8), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True,
                       note="two-cell reception console: navy top, sky-blue front, ink terminal housing first, then a screen with one body step and one lit step, a one-step glow on the desk top, keyboard and card reader",
                       tags=["terminal", "desk", "interact"]))
    cred = paper_pal()
    out.append(ok.make("cabinet_1x1", lambda r: sp.cabinet(r, sx, sy, 1, cred), (sx, sy + sp.CAB_H - 16), (1, 1), ["1"],
                       "rear_prop", "prop", y_sort=True, note="walnut credenza, one cell: paper stack on the top plane, three drawers with pale label plates",
                       tags=["cabinet", "credenza"]))
    out.append(ok.make("cabinet_2x1", lambda r: sp.cabinet(r, sx, sy, 2, cred), (sx, sy + sp.CAB_H - 16), (2, 1), ["11"],
                       "rear_prop", "prop", y_sort=True, note="walnut credenza, two cells wide", tags=["cabinet", "credenza"]))
    for nm, colour, note in (("light_shaft_cool", COOL_LIGHT, "overcast: two bands of pale sky light from a window pair, one hard step that barely lifts the floor"),
                             ("light_shaft_warm", WARM_LIGHT, "daylight: the same two bands once the window views resolve, one hard warm step")):
        rgba, painted = ok.cap(lambda r, c=colour: sp.light_shaft(r, sx, sy, bst.hx(c)))
        b = kitlib.bbox(painted)
        out.append(ok.Piece(nm, kitlib.crop_rgba(rgba, b), (b[0], b[1]), (b[0], b[1]), (4, 3), ["0000"] * 3, "light", "light",
                            composite={"mode": "where_color", "color": FLOOR_FILL},
                            note=note + "; paints only on the bare floor fill, so shelves, desks and joints stay untouched. Place at the window's bottom-left; "
                                 "state set window_light switches between the two",
                            tags=["light", "window", "daylight"]))
    return out


# ------------------------------------------------------------------ 3. Executive-only pieces

def draw_post(r, x, y0, y1):
    """Rail post: copper, lit left edge, shaded right edge, ink contour."""
    m = r.mask(x, y0, x + 3, y1)
    r.img[m] = ACC[2]
    r.rect(x, y0, x + 1, y1, ACC[3])
    r.rect(x + 2, y0, x + 3, y1, ACC[1])
    r.outline(m)


def rail_run_h(r, x0, x1, y0, posts=None):
    """Glass balustrade seen from the front: a copper cap, a pale pane that darkens toward the floor with
    one reflection band per 16 px, a copper base and a posts every 16 px. Body y0 .. y0+15, contact shadow below."""
    r.cast(x0, x1, y0 + 15)
    body = r.mask(x0, y0, x1, y0 + 15)
    r.img[body] = GLASS[2]
    r.rect(x0, y0, x1, y0 + 2, ACC[2])             # cap
    r.rect(x0, y0, x1, y0 + 1, ACC[3])
    r.rect(x0, y0 + 2, x1, y0 + 3, ACC[1])
    r.rect(x0, y0 + 9, x1, y0 + 12, GLASS[1])      # floor seen through the lower pane
    for bx in range(x0, x1, 16):
        for k in range(8):                          # stepped reflection band
            xx = bx + 5 + (k * 4) // 5
            if xx < x1:
                r.img[y0 + 3 + k, xx:xx + 2] = GLASS[3]
    r.rect(x0, y0 + 12, x1, y0 + 15, ACC[1])       # base rail
    r.rect(x0, y0 + 12, x1, y0 + 13, ACC[2])
    r.rect(x0, y0 + 14, x1, y0 + 15, ACC[0])
    r.outline(body)
    for px_ in (posts if posts is not None else range(x0, x1, 16)):
        draw_post(r, px_ - 1 if px_ > x0 else x0, y0 - 1, y0 + 15)
    if posts is None:
        draw_post(r, x1 - 3, y0 - 1, y0 + 15)


def rail_run_v(r, x0, y0, y1):
    """Side run of the balustrade seen from above: 6 px wide, a copper cap line either side of a pale glass
    edge with one reflection stripe, a small copper post cap at each end and every 32 px."""
    body = r.mask(x0, y0, x0 + 6, y1)
    r.img[body] = GLASS[2]
    r.rect(x0 + 1, y0, x0 + 2, y1, ACC[3])
    r.rect(x0 + 4, y0, x0 + 5, y1, ACC[1])
    r.rect(x0 + 2, y0, x0 + 4, y1, GLASS[2])
    for by in range(y0 + 3, y1, 8):
        r.rect(x0 + 2, by, x0 + 3, by + 3, GLASS[3])
    r.outline(body)
    for py in list(range(y0, y1 - 3, 32)) + [y1 - 4]:
        pm = r.mask(x0 - 1, py, x0 + 7, py + 4)
        r.img[pm] = ACC[2]
        r.rect(x0 - 1, py, x0 + 7, py + 1, ACC[3])
        r.rect(x0 - 1, py + 3, x0 + 7, py + 4, ACC[1])
        r.outline(pm)


def boardroom_table(r, x0, y0, cells):
    """Long boardroom table, 2 cells deep: walnut top plane with a copper inlay border and a pale runner,
    papers at the stations, water glasses and a conference puck, front face with copper studs. Body y0..y0+32."""
    w = 16 * cells
    env.block(r, x0, y0, x0 + w, y0 + 32, 7, WOOD, WOOD)
    top_h = 25
    # copper inlay border one step inside the lit edge
    r.rect(x0 + 3, y0 + 3, x0 + w - 3, y0 + 4, ACC[2])
    r.rect(x0 + 3, y0 + top_h - 4, x0 + w - 3, y0 + top_h - 3, ACC[1])
    r.rect(x0 + 3, y0 + 3, x0 + 4, y0 + top_h - 3, ACC[2])
    r.rect(x0 + w - 4, y0 + 3, x0 + w - 3, y0 + top_h - 3, ACC[1])
    # runner down the middle
    r.rect(x0 + 7, y0 + 10, x0 + w - 7, y0 + 16, WOOD[3])
    r.rect(x0 + 7, y0 + 15, x0 + w - 7, y0 + 16, WOOD[2])
    # papers at the stations, north and south of the runner
    for i in range(cells * 2 - 1):
        px_ = x0 + 9 + i * 8
        for py in (y0 + 6, y0 + 18):
            r.rect(px_, py, px_ + 5, py + 3, FLOOR[3])
            r.rect(px_ + 1, py + 2, px_ + 4, py + 3, FLOOR[1])
    # water glasses and the conference puck on the runner
    for i in range(1, cells):
        gx = x0 + 16 * i - 3
        gm = r.mask(gx, y0 + 11, gx + 3, y0 + 15)
        r.img[gm] = GLASS[2]
        r.rect(gx, y0 + 11, gx + 1, y0 + 14, GLASS[3])
        r.outline(gm, GLASS[0])
    px_ = x0 + w // 2 - 4
    pm = r.mask(px_, y0 + 10, px_ + 8, y0 + 16)
    r.img[pm] = INK[1]
    r.rect(px_ + 1, y0 + 11, px_ + 7, y0 + 12, GLASS[2])
    r.rect(px_ + 1, y0 + 13, px_ + 5, y0 + 14, GLASS[3])
    r.outline(pm)
    # copper studs on the front face
    for i in range(cells * 2):
        r.img[y0 + 29, x0 + 4 + i * 8] = ACC[3]
        r.img[y0 + 29, x0 + 5 + i * 8] = ACC[2]


def boardroom_chair(r, x0, y0):
    """Dark navy high-back chair seen from above (14 x 16): tall back with a copper stud row and a lit top
    edge, seat plane with arms, front face, floor shadow. Facing south."""
    r.cast(x0 + 1, x0 + 13, y0 + 15, rows=1)
    back = r.mask(x0 + 1, y0, x0 + 13, y0 + 6)
    r.img[back] = WALL[1]
    r.rect(x0 + 1, y0, x0 + 13, y0 + 1, WALL[3])
    r.rect(x0 + 1, y0 + 1, x0 + 13, y0 + 2, WALL[2])
    r.rect(x0 + 4, y0 + 3, x0 + 10, y0 + 4, ACC[2])
    r.img[y0 + 3, x0 + 4] = ACC[3]
    r.outline(back)
    seat = r.mask(x0, y0 + 5, x0 + 14, y0 + 15)
    r.img[seat] = WALL[2]
    r.rect(x0 + 1, y0 + 6, x0 + 13, y0 + 7, WALL[3])
    r.rect(x0 + 3, y0 + 8, x0 + 11, y0 + 12, WALL[1])      # cushion
    r.rect(x0 + 3, y0 + 8, x0 + 11, y0 + 9, WALL[2])
    r.rect(x0, y0 + 13, x0 + 14, y0 + 15, WALL[0])         # front face
    r.rect(x0 + 6, y0 + 14, x0 + 8, y0 + 15, ACC[2])       # copper pull / foot
    r.outline(seat)


def wall_trim(r, x0, y0, w):
    """Copper wall trim: a 3 px picture rail, lit top row, shaded bottom row, studs every 8 px."""
    r.rect(x0, y0, x0 + w, y0 + 1, ACC[3])
    r.rect(x0, y0 + 1, x0 + w, y0 + 2, ACC[2])
    r.rect(x0, y0 + 2, x0 + w, y0 + 3, ACC[1])
    for sx in range(x0 + 3, x0 + w, 8):
        r.img[y0 + 1, sx] = ACC[3]


def route_arrows():
    """Copper wayfinding arrows inlaid in the floor (east and north)."""
    a = np.zeros((16, 16, 4), np.uint8)

    def px(x, y, c):
        a[y, x, :3] = kitlib.hex2rgb(c)
        a[y, x, 3] = 255
    for x in range(3, 10):          # shaft
        px(x, 7, E["accent"][1])
        px(x, 8, E["accent"][1])
    for i in range(5):              # head, tip to the right
        for y in range(3 + i, 13 - i):
            px(10 + i, y, E["accent"][1])
    for i in range(5):              # lit upper-left edge of the head
        px(10 + i, 3 + i, E["accent"][2])
    for x in range(3, 10):
        px(x, 7, E["accent"][2])
    east = ok.Piece("route_arrow_e", a, (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                    note="copper wayfinding arrow inlaid in the floor, pointing east; Executive wayfinding uses the copper ramp",
                    tags=["wayfinding", "route"])
    north = ok.Piece("route_arrow_n", np.rot90(a, 1).copy(), (0, 0), (0, 0), (1, 1), ["0"], "floor_marking", "tile",
                     note="the same arrow pointing north", tags=["wayfinding", "route"])
    return [east, north]


def executive_pieces():
    out = []
    sx, sy = 64, 64
    out.append(ok.make("boardroom_table", lambda r: boardroom_table(r, sx, sy, 4), (sx, sy), (4, 2), ["1111", "1111"],
                       "rear_prop", "prop", y_sort=True,
                       note="long boardroom table, 4 x 2 cells: walnut top plane with a copper inlay border, pale runner, papers at eight stations, "
                            "water glasses and a conference puck, copper studs on the front face. Chairs are separate entries",
                       tags=["table", "boardroom", "copper"]))
    out.append(ok.make("boardroom_chair", lambda r: boardroom_chair(r, sx, sy), (sx, sy), (1, 1), ["1"], "rear_prop", "prop", y_sort=True,
                       note="dark navy high-back boardroom chair seen from above, copper stud row on the back; place 1 cell south of the table's south edge "
                            "(or north of its north edge, mirrored by the layout)", tags=["seating", "navy", "boardroom"]))
    out.append(ok.make("glass_rail_1x1", lambda r: rail_run_h(r, sx, sx + 16, sy, posts=[sx]), (sx, sy + 2), (1, 1), ["1"], "rear_prop", "prop", y_sort=True,
                       note="glass balustrade, one cell: copper cap and base, pale pane, one reflection band, a post on the left edge; run several to edge an atrium well or mezzanine",
                       tags=["balustrade", "glass", "copper"]))
    out.append(ok.make("glass_rail_2x1", lambda r: rail_run_h(r, sx, sx + 32, sy, posts=[sx, sx + 16]), (sx, sy + 2), (2, 1), ["11"], "rear_prop", "prop", y_sort=True,
                       note="glass balustrade, two cells, a post every cell", tags=["balustrade", "glass", "copper"]))
    out.append(ok.make("glass_rail_side", lambda r: rail_run_v(r, sx, sy, sy + 16), (sx - 5, sy), (1, 1), ["1"], "rear_prop", "prop", y_sort=True, shadow=False,
                       note="balustrade side run seen from above: a 6 px copper and glass edge, one cell tall; place down the east or west side of a well, "
                            "the sprite sits centred in its cell",
                       tags=["balustrade", "glass", "copper", "side"]))
    # wall trim overlay: 16 x 3, tiles along the wall face
    rgba, painted = ok.cap(lambda r: wall_trim(r, sx, sy, 16))
    b = kitlib.bbox(painted)
    out.append(ok.Piece("wall_n_trim", kitlib.crop_rgba(rgba, b), (b[0], b[1]), (b[0], b[1]), (1, 1), ["0"], "rear_wall", "wall",
                        note="copper picture rail for the north wall face, 16 x 3 px, lit top row, studs every 8 px; place at wall y 22 under the window overlays",
                        tags=["wall", "copper", "trim"]))
    return out


# ------------------------------------------------------------------ 4. landmark: the atrium tree

OX, OY = 16, 8           # capture position of the box in the 320 x 192 room
BOX_W, BOX_H = 176, 160  # 11 x 10 cells
WELL = (32, 30, 144, 110)  # box coordinates of the well's outer edge: 112 x 80 px, 7 x 5 cells
FP = (32, 34)            # footprint origin inside the box: 4 px below the well's visual top-left, so the collision rows sit under the visual rail rows
FP_CELLS = (7, 5)
C = (88, 62)             # planter centre (box coordinates)
RX, RY = 24, 14          # planter top plane radii
FACE = 11                # planter face height
GAP = (64, 112)          # south steps, box x range (footprint cols 2 to 4)
LINE_Y, LINE_X = 62, 88  # floor-line axes (box coordinates)


def X(v):
    return OX + v


def Y(v):
    return OY + v


def erode(m, k):
    for _ in range(k):
        m = m & shifted(m, 1, 0) & shifted(m, -1, 0) & shifted(m, 0, 1) & shifted(m, 0, -1)
    return m


class Geo:
    """Masks of the well and planter in room coordinates."""

    def __init__(self, r):
        self.r = r
        x0, y0, x1, y1 = X(WELL[0]), Y(WELL[1]), X(WELL[2]), Y(WELL[3])
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        ch = 6
        outer = r.mask(x0, y0, x1, y1)
        dxl, dxr, dyt, dyb = r.x - x0, x1 - r.x, r.y - y0, y1 - r.y
        for a, b in ((dxl, dyt), (dxr, dyt), (dxl, dyb), (dxr, dyb)):
            outer &= (a + b) >= ch
        self.outer = outer
        self.inner = erode(outer, 6)
        self.coping = outer & ~self.inner
        face = np.zeros_like(outer)
        for k in range(1, 7):
            face |= shifted(self.coping, 0, -k)
        self.face = face & self.inner
        cx, cy = X(C[0]), Y(C[1])
        self.cx, self.cy = cx, cy
        self.top = r.disc(cx, cy, RX, RY)
        down = np.zeros_like(self.top)
        for k in range(1, FACE + 1):
            down |= shifted(self.top, 0, -k)
        self.pface = down & ~self.top
        self.planter = self.top | self.pface
        self.gap = r.mask(X(GAP[0]), y1 - 14, X(GAP[1]), y1 + 1)


def draw_well(r):
    """The sunken atrium well: coping ring in the stone mid step, an inner north face, a bright well floor,
    a copper ring inlay around the planter and three steps down through the south gap."""
    g = Geo(r)
    F, A = FLOOR, ACC
    r.img[g.coping] = F[3]
    r.img[g.coping & ~shifted(g.outer, 1, 1)] = F[2]            # shaded lower-right edge
    r.img[g.inner] = F[2]
    r.img[g.face] = F[1]                                       # the north wall of the well, seen from the south
    lip = g.inner & shifted(g.coping, 0, -1)
    r.img[lip] = F[0]
    west = g.inner & ~g.face & (~shifted(g.inner, -1, 0) | ~shifted(g.inner, -2, 0))
    r.img[west] = F[1]                                         # the west wall's shade
    r.img[r.edge(g.outer)] = F[0]
    # copper ring inlay around the planter, with four nodes where the floor lines meet it
    ring = r.disc(g.cx, g.cy, 38, 23) & ~r.disc(g.cx, g.cy, 37, 22)  # thin copper ring
    r.img[ring & g.inner & ~g.face] = A[1]
    for dx, dy in ((38, 0), (-38, 0), (0, 23)):
        nx, ny = g.cx + dx, g.cy + dy
        node = r.mask(nx - 1, ny - 1, nx + 1, ny + 1)
        r.img[node & g.inner] = A[2]
    # steps through the gap: four 3 px treads, lit nosing, shaded riser
    gx0, gx1 = X(GAP[0]), X(GAP[1])
    sy1 = g.y1
    for i in range(5):
        ty = sy1 - 14 + i * 3 + 1
        r.rect(gx0, ty, gx1, ty + 3, F[3] if i % 2 == 0 else F[2])
        r.rect(gx0, ty, gx1, ty + 1, F[3])
        r.rect(gx0, ty + 2, gx1, ty + 3, F[1])
    r.rect(gx0, sy1 + 1, gx1, sy1 + 2, F[0])                   # contour at the foot of the steps
    for x in (gx0 - 1, gx1):                                   # stringers
        r.rect(x, sy1 - 14, x + 1, sy1 + 2, F[0])
        r.rect(x, sy1 - 14, x + 1, sy1 - 13, F[0])
    return g


def draw_planter(r):
    """Raised round planter: pale stone face with cylinder shading and a copper band, a lit rim, dark soil,
    ground cover, and two roots spilling over the rim. Casts the contact shadow; carries the well's collision."""
    g = Geo(r)
    F, A, W, Fo = FLOOR, ACC, WOOD, FOL
    pl = g.planter
    s1 = shifted(pl, -1, -1) & ~pl
    s2 = shifted(pl, -2, -2) & ~pl & ~s1
    r.img[s1] = INK[2]
    r.img[s2] = INK[3]
    cx = g.cx
    # face: three cylinder bands, bottom edge, copper band
    face = g.pface
    xi = (r.x - cx) / RX
    r.img[face] = F[2]
    r.img[face & (xi < -0.45)] = F[3]
    r.img[face & (xi > 0.4)] = F[1]
    r.img[face & (xi > 0.78)] = F[0]
    r.img[face & ~shifted(face, 0, 1)] = F[0]
    band = face & shifted(g.top, 0, -3)
    r.img[band] = A[2]
    r.img[face & shifted(g.top, 0, -4)] = A[1]
    r.img[band & (xi < -0.45)] = A[3]
    # top plane: lit stone rim, then soil
    rim = g.top & ~erode(g.top, 3)
    r.img[g.top] = W[0]
    r.img[g.top & ~shifted(g.top, 1, 1) & (r.y < g.cy + 4)] = W[0]
    soil = erode(g.top, 3)
    r.img[soil] = W[1]
    r.img[soil & ~shifted(soil, -1, -1)] = W[2]
    rnd = random.Random(7)
    for _ in range(26):
        a = rnd.uniform(0, 6.283)
        d = rnd.uniform(0.2, 0.85)
        px_, py = int(g.cx + math.cos(a) * (RX - 4) * d), int(g.cy + math.sin(a) * (RY - 4) * d)
        if soil[py, px_]:
            r.img[py, px_] = W[0]
    r.img[rim] = F[2]
    r.img[rim & ~shifted(g.top, -1, -1)] = F[3]
    r.img[rim & ~shifted(g.top, 1, 1)] = F[1]
    # ground cover: small tufts around the soil edge
    cover = soil & ~r.disc(g.cx, g.cy - 1, 7, 4)
    for i, (dx, dy, rad) in enumerate([(-15, -2, 3.2), (-9, 5, 3), (11, 4, 3.4), (16, -1, 3), (-3, 7, 3), (6, -6, 2.8), (-12, -6, 2.6), (13, -6, 2.6)]):
        env.leaves(r, g.cx + dx, g.cy + dy, rad, 300 + i, ramp=Fo, count=4, spread=rad * 0.7, clip=cover)
    r.img[r.edge(g.planter)] = INK[0]
    # roots over the rim, down the face
    for rx0, ry0, sgn in ((-16, 12, -1), (13, 13, 1)):
        for k in range(FACE - 1):
            xx = g.cx + rx0 + sgn * (k // 4)
            yy = g.cy + ry0 + k - 1
            if 0 <= yy < r.img.shape[0]:
                r.img[yy, xx:xx + 2] = W[2]
                r.img[yy, xx + (1 if sgn < 0 else 0)] = W[1]
        r.img[g.cy + ry0 - 2, g.cx + rx0 + (0 if sgn < 0 else 1): g.cx + rx0 + (3 if sgn < 0 else 4)] = W[2]
    return g


PLATE_Y0 = 5  # plate rows within the face


def draw_nameplates(r, state):
    """Five nameplates on the planter face, 4 px tall. before: five identical blank pale plates (the names are
    not yet restored); after: five distinct plates, different widths and colours, each with its own inked mark."""
    g = Geo(r)
    F, A, W = FLOOR, ACC, WALL
    xs = (-16, -8, 0, 8, 16)
    # (width, body, edge, ink, marks)
    styles = [(7, F[3], F[1], INK[0], [(1, 1), (2, 1), (4, 1), (5, 1), (2, 2), (3, 2), (4, 2)]),
              (5, A[2], A[1], INK[0], [(1, 1), (3, 1), (2, 2)]),
              (7, W[2], W[0], F[3], [(1, 1), (2, 1), (3, 1), (5, 1), (1, 2), (4, 2), (5, 2)]),
              (5, F[3], F[1], INK[0], [(1, 1), (2, 1), (3, 1), (1, 2)]),
              (6, A[3], A[1], INK[0], [(1, 1), (4, 1), (2, 2), (3, 2)])]
    for i, dx in enumerate(xs):
        nx = g.cx + dx
        ty = int(g.cy + RY * math.sqrt(max(0.0, 1 - (dx / RX) ** 2))) + PLATE_Y0
        if state == "before":
            w, body, edge, ink, marks = 6, F[3], F[1], INK[0], []
        else:
            w, body, edge, ink, marks = styles[i]
        x0 = nx - w // 2
        r.rect(x0, ty, x0 + w, ty + 4, body)
        r.rect(x0, ty + 3, x0 + w, ty + 4, edge)
        for mx, my in marks:
            r.img[ty + my, x0 + mx] = ink


# crown: blobs (cx, cy, radius) in box coordinates; a columnar ovoid with a skirt, distinct from the garden's wide dome
CROWN = [(88, 8, 6), (82, 13, 7), (94, 13, 7), (88, 18, 8), (79, 24, 8), (97, 24, 8), (88, 27, 10), (77, 32, 8), (99, 32, 8), (88, 36, 9),
         (82, 41, 6), (94, 41, 6), (88, 45, 5), (66, 38, 5), (109, 43, 4)]


def draw_trunk(r):
    """Slim trunk with a fork under the crown and a root flare, walnut ramp."""
    g = Geo(r)
    W = WOOD
    cx, cy = g.cx, g.cy
    base = cy - 1
    trunk = r.mask(cx - 3, base - 26, cx + 3, base) | r.mask(cx - 6, base - 5, cx + 6, base) | r.mask(cx - 8, base - 2, cx + 8, base)
    br_l = np.zeros_like(trunk)
    br_r = np.zeros_like(trunk)
    for t in range(14):
        br_l |= r.mask(cx - 3 - t // 2, base - 26 - t, cx - 1 - t // 2, base - 25 - t)
        br_r |= r.mask(cx + 1 + t // 2, base - 26 - t, cx + 3 + t // 2, base - 25 - t)
    allm = trunk | br_l | br_r
    shade = allm
    bst.shade_mask(r.img, shade, W, k_shadow=1, k_light=1)
    r.outline(allm, W[0])
    return g


def draw_canopy(r):
    """Layered canopy of living green: nine leaf clusters in a tall oval with an airy skirt, lit upper left."""
    g = Geo(r)
    whole = np.zeros_like(g.top)
    for i, (bx, by, br) in enumerate(CROWN):
        whole |= env.leaves(r, X(bx), Y(by), br, 500 + i, ramp=FOL, count=6, spread=br * 0.8)
    return whole


def draw_canopy_shadow(r):
    """One cool step of shadow on the well floor, to the lower right of the planter."""
    g = Geo(r)
    sh = r.disc(g.cx + 6, g.cy + 8, 30, 15) & g.inner & ~g.face & ~g.planter
    r.img[sh] = FLOOR[1]


def draw_rail_back(r):
    """North, west and east runs of the glass balustrade (behind actors): the north run is a front-facing pane
    on the north coping, the sides are 6 px runs on the west and east coping."""
    g = Geo(r)
    x0, y0, x1, y1 = g.x0, g.y0, g.x1, g.y1
    # north: from the chamfer to the chamfer, base at y0 + 6
    rail_run_h(r, x0 + 8, x1 - 8, y0 - 7, posts=list(range(x0 + 8, x1 - 8, 16)))
    draw_post(r, x1 - 8 - 3, y0 - 8, y0 + 8)
    draw_post(r, x0 + 7, y0 - 8, y0 + 8)
    # west and east sides
    rail_run_v(r, x0 + 1, y0 + 12, y1 - 10)
    rail_run_v(r, x1 - 7, y0 + 12, y1 - 10)
    return g


def draw_rail_front(r):
    """South runs flanking the steps (in front of actors), with taller newel posts at the gap."""
    g = Geo(r)
    x0, y0, x1, y1 = g.x0, g.y0, g.x1, g.y1
    gx0, gx1 = X(GAP[0]), X(GAP[1])
    rail_run_h(r, x0 + 8, gx0 - 3, y1 - 12, posts=list(range(x0 + 8, gx0 - 3, 16)))
    rail_run_h(r, gx1 + 3, x1 - 8, y1 - 12, posts=list(range(gx1 + 3, x1 - 8, 16)))
    for px_ in (gx0 - 4, gx1 + 1):                               # newels: taller posts with a ball cap
        draw_post(r, px_, y1 - 18, y1 + 3)
        ball = r.mask(px_, y1 - 21, px_ + 3, y1 - 18)
        r.img[ball] = ACC[3]
        r.outline(ball)
    draw_post(r, x0 + 5, y1 - 13, y1 + 3)
    draw_post(r, x1 - 8, y1 - 13, y1 + 3)
    return g


POT_POS = [(-12, -12), (WELL[2] - WELL[0] + 5, -12), (-12, 80 + 2), (WELL[2] - WELL[0] + 5, 80 + 2)]  # relative to the well's top-left


def draw_pots(r, state):
    """Four corner pots outside the coping. before: identical square-clipped box cubes (repeated geometry);
    after: soft shrubs of different sizes with copper-pink blossoms (the geometry is varied)."""
    g = Geo(r)
    sizes = [7, 6, 8, 6]
    for i, (dx, dy) in enumerate(POT_POS):
        px_, py = g.x0 + dx, g.y0 + dy
        r.cast(px_, px_ + 10, py + 13, rows=1)
        pot = r.mask(px_, py + 7, px_ + 10, py + 13)
        r.img[pot] = INK[1]
        r.rect(px_, py + 7, px_ + 10, py + 8, INK[2])
        r.rect(px_, py + 7, px_ + 1, py + 13, INK[2])
        r.rect(px_, py + 12, px_ + 10, py + 13, INK[0])
        r.outline(pot)
        if state == "before":
            cube = r.mask(px_ + 1, py, px_ + 9, py + 8)
            r.img[cube] = FOL[2]
            r.rect(px_ + 1, py, px_ + 9, py + 1, FOL[3])
            r.rect(px_ + 1, py, px_ + 2, py + 8, FOL[3])
            r.rect(px_ + 1, py + 6, px_ + 9, py + 8, FOL[1])
            r.rect(px_ + 8, py + 1, px_ + 9, py + 8, FOL[1])
            r.rect(px_ + 3, py + 3, px_ + 8, py + 4, FOL[1])     # clipped groove
            r.outline(cube)
            for cx_, cy_ in ((px_ + 1, py), (px_ + 8, py)):      # squared corners: ink chips
                r.img[cy_, cx_] = INK[0]
        else:
            rad = sizes[i]
            env.leaves(r, px_ + 5, py + 2, rad * 0.9, 700 + i, ramp=FOL, count=5, spread=rad * 0.6)
            for bx, by in ((-3, -1), (2, -3), (3, 2), (-1, 2))[: 2 + i % 3]:
                r.img[py + 2 + by, px_ + 5 + bx] = ACC[3]
                r.img[py + 2 + by, px_ + 6 + bx] = ACC[2]


def draw_inlay(r, state):
    """The copper floor lines that leave the well. before: rigid and wandering, jogs and dead ends that go
    nowhere; after: straight, with chevrons, running to the box edge where the routes continue."""
    g = Geo(r)
    A = ACC
    ly, lx = Y(LINE_Y), X(LINE_X)

    def hline(x0, x1, y, c=A[1]):
        r.rect(min(x0, x1), y, max(x0, x1) + 1, y + 1, c)

    def vline(x, y0, y1, c=A[1]):
        r.rect(x, min(y0, y1), x + 1, max(y0, y1) + 1, c)

    def knot(x, y):
        r.rect(x - 1, y - 1, x + 1, y + 1, A[2])

    def chevron_e(x, y):
        for k in range(3):
            r.img[y - 2 + k, x + k] = A[2]
            r.img[y + 2 - k, x + k] = A[2]

    def chevron_w(x, y):
        for k in range(3):
            r.img[y - 2 + k, x - k] = A[2]
            r.img[y + 2 - k, x - k] = A[2]

    def chevron_s(x, y):
        for k in range(3):
            r.img[y + k, x - 2 + k] = A[2]
            r.img[y + k, x + 2 - k] = A[2]
    ex1, wx0 = g.x1, g.x0
    bx1, bx0, by1 = X(BOX_W), X(0), Y(BOX_H)
    if state == "before":
        # east: out, drop, run, climb, stub
        hline(ex1, ex1 + 8, ly)
        vline(ex1 + 8, ly, ly + 9)
        hline(ex1 + 8, ex1 + 22, ly + 9)
        vline(ex1 + 22, ly + 9, ly - 6)
        hline(ex1 + 22, ex1 + 27, ly - 6)
        for kx, ky in ((ex1 + 8, ly + 9), (ex1 + 22, ly + 9), (ex1 + 22, ly - 6)):
            knot(kx, ky)
        # west
        hline(wx0, wx0 - 9, ly)
        vline(wx0 - 9, ly, ly - 8)
        hline(wx0 - 9, wx0 - 21, ly - 8)
        vline(wx0 - 21, ly - 8, ly + 6)
        hline(wx0 - 21, wx0 - 26, ly + 6)
        for kx, ky in ((wx0 - 9, ly - 8), (wx0 - 21, ly - 8), (wx0 - 21, ly + 6)):
            knot(kx, ky)
        # south
        vline(lx, g.y1 + 2, g.y1 + 12)
        hline(lx, lx + 8, g.y1 + 12)
        vline(lx + 8, g.y1 + 12, g.y1 + 26)
        hline(lx + 8, lx - 6, g.y1 + 26)
        vline(lx - 6, g.y1 + 26, g.y1 + 31)
        for kx, ky in ((lx, g.y1 + 12), (lx + 8, g.y1 + 12), (lx + 8, g.y1 + 26), (lx - 6, g.y1 + 26)):
            knot(kx, ky)
    else:
        hline(ex1, bx1 - 1, ly)
        hline(bx0, wx0, ly)
        vline(lx, g.y1 + 2, by1 - 1)
        for x in range(ex1 + 8, bx1 - 4, 20):
            chevron_e(x, ly)
        for x in range(wx0 - 8, bx0 + 4, -20):
            chevron_w(x, ly)
        for y in range(g.y1 + 8, by1 - 4, 20):
            chevron_s(lx, y)
        knot(ex1 + 2, ly)
        knot(wx0 - 2, ly)
        knot(lx, g.y1 + 3)


def draw_pool(r):
    """After: the roof glass lets daylight onto the well floor, a warm pool around the planter, one hard step.
    Paints only on the bare well floor."""
    g = Geo(r)
    pool = r.disc(g.cx + 2, g.cy + 4, 44, 27) & ~r.disc(g.cx, g.cy + 4, 32, 18)
    r.img[pool & g.inner & ~g.face] = FLOOR[3]


def landmark_pieces():
    parts = []
    box = (OX, OY, OX + BOX_W, OY + BOX_H)
    fp_room = (X(FP[0]), Y(FP[1]))

    def mk(name, draw, layer, collision, y_sort, note, tags, composite=None):
        rgba, painted = ok.cap(draw)
        outside = painted.copy()
        outside[box[1]:box[3], box[0]:box[2]] = False
        assert not outside.any(), f"{name} leaves the landmark box"
        sprite = rgba[box[1]:box[3], box[0]:box[2]].copy()
        p = ok.Piece(name, sprite, (OX, OY), fp_room, FP_CELLS, collision, layer, "landmark_part", y_sort=y_sort,
                     composite=composite, tags=["landmark", "atrium tree"] + tags, note=note)
        parts.append(p)
        return p

    zero = ["0" * FP_CELLS[0]] * FP_CELLS[1]
    # footprint: the balustrade ring blocks, the three south cells are the steps, the planter blocks its two rows
    coll = ["1111111", "1011101", "1011101", "1000001", "1100011"]
    mk("atrium_well", draw_well, "floor_marking", zero, False,
       "the sunken well: octagonal coping ring in the stone mid step, a shaded inner north face, a bright floor, a copper ring inlay around the planter and "
       "three steps down through the three-cell south gap", ["well", "base"])
    mk("atrium_inlay_before", lambda r: draw_inlay(r, "before"), "floor_marking", zero, False,
       "before: copper floor lines leave the well rigid and wandering, with right-angle jogs, knots and dead-end stubs that connect to nothing",
       ["quest state", "before", "copper lines"])
    mk("atrium_inlay_after", lambda r: draw_inlay(r, "after"), "floor_marking", zero, False,
       "after: the same lines straightened into three clean paths with chevrons, east, west and south, running to the box edge where the routes continue (levels.md 20: copper floor lines straighten into useful paths)",
       ["quest state", "after", "copper lines"])
    mk("atrium_planter", draw_planter, "rear_prop", coll, True,
       "raised round planter: pale stone face with a copper band, lit rim, dark soil, ground cover and two roots over the rim. Carries the collision of the whole well "
       "(rail ring, planter, open steps)", ["planter", "base"])
    mk("atrium_nameplates_before", lambda r: draw_nameplates(r, "before"), "rear_prop", zero, True,
       "before: five identical blank pale nameplates on the planter face", ["quest state", "before", "nameplates"])
    mk("atrium_nameplates_after", lambda r: draw_nameplates(r, "after"), "rear_prop", zero, True,
       "after: the same five plates distinct: different widths, copper, navy and pale, each with its own inked mark (levels.md 20: nameplates become distinct)",
       ["quest state", "after", "nameplates"])
    mk("atrium_trunk", draw_trunk, "rear_prop", zero, True,
       "slim walnut trunk with a root flare and a fork under the crown", ["tree", "trunk"])
    mk("atrium_rail_back", draw_rail_back, "rear_prop", zero, True,
       "north, west and east runs of the glass balustrade: copper caps and bases, pale panes, posts every cell", ["balustrade"])
    mk("atrium_pots_before", lambda r: draw_pots(r, "before"), "rear_prop", zero, True,
       "before: four corner pots with identical square-clipped box cubes (repeated geometry)", ["quest state", "before", "pots"])
    mk("atrium_pots_after", lambda r: draw_pots(r, "after"), "rear_prop", zero, True,
       "after: the same four pots with soft shrubs of different sizes and copper blossoms (repeated geometry becomes varied)", ["quest state", "after", "pots"])
    mk("atrium_canopy", draw_canopy, "rear_prop", zero, True,
       "the crown: nine leaf clusters in a tall oval with an airy skirt, a different silhouette from the garden's wide dome; separate part so a renderer can sway it",
       ["tree", "canopy", "centrepiece"])
    mk("atrium_canopy_shadow", draw_canopy_shadow, "shadow", zero, False,
       "one cool stone step on the well floor, lower right of the planter", ["shadow"])
    mk("atrium_rail_front", draw_rail_front, "front_prop", zero, True,
       "south runs of the balustrade flanking the steps, with newel posts; drawn after actors so a person on the steps passes behind the rail ends",
       ["balustrade", "occluder"])
    mk("atrium_daylight_after", draw_pool, "light", zero, False,
       "after: a warm pool of daylight on the well floor around the planter; paints only on the bare well floor (levels.md 20: window light warms)",
       ["quest state", "after", "light"], composite={"mode": "where_color", "color": WELL_FLOOR})
    # contact shadow of the planter (baked into the planter part)
    r1 = env.Room()
    g1 = Geo(r1)
    pl = g1.planter
    s1 = shifted(pl, -1, -1) & ~pl
    s2 = shifted(pl, -2, -2) & ~pl & ~s1
    b = kitlib.bbox(s1 | s2)
    next(p for p in parts if p.name == "atrium_planter").shadow = (b[0] - OX, b[1] - OY, b[2] - b[0], b[3] - b[1])
    return parts


LAMP_OFFSETS = [[-26, -4], [-26, 50], [117, -4], [117, 50]]   # relative to the footprint origin (lamp footprint origins)

COMMON = ["atrium_well", "atrium_rail_back", "atrium_planter", "atrium_trunk", "atrium_canopy_shadow"]


def landmarks():
    before = ["atrium_well", "atrium_inlay_before", "atrium_rail_back", "atrium_planter", "atrium_nameplates_before", "atrium_trunk",
              "atrium_pots_before", "atrium_canopy_shadow", "atrium_canopy", "atrium_rail_front"]
    after = ["atrium_well", "atrium_inlay_after", "atrium_rail_back", "atrium_planter", "atrium_nameplates_after", "atrium_trunk",
             "atrium_pots_after", "atrium_canopy_shadow", "atrium_daylight_after", "atrium_canopy", "atrium_rail_front"]
    def branch_state(name_done, route_done, count_done):
        """The three branches change one atrium feature each (levels.md 20): The Name the nameplates, The Route the copper floor lines
        (and the pots, the repeated geometry), The Count the daylight (the warm pool here, the window sets in the room) and the lamps."""
        parts = ["atrium_well", "atrium_inlay_after" if route_done else "atrium_inlay_before", "atrium_rail_back", "atrium_planter",
                 "atrium_nameplates_after" if name_done else "atrium_nameplates_before", "atrium_trunk",
                 "atrium_pots_after" if route_done else "atrium_pots_before", "atrium_canopy_shadow"]
        if count_done:
            parts.append("atrium_daylight_after")
        parts += ["atrium_canopy", "atrium_rail_front"]
        return {"parts": parts, "lamps": {"anim": "lamp", "state": "pulse" if count_done else "on", "offsets_px": LAMP_OFFSETS}}
    assert branch_state(0, 0, 0)["parts"] == before and branch_state(1, 1, 1)["parts"] == after
    partial = {f"repaired_{k}": branch_state(*flags) for k, flags in (
        ("name", (1, 0, 0)), ("route", (0, 1, 0)), ("count", (0, 0, 1)),
        ("name_route", (1, 1, 0)), ("name_count", (1, 0, 1)), ("route_count", (0, 1, 1)))}
    return {
        "atrium_tree": {
            "note": "Executive landmark: a tall single tree in a raised round planter, inside a sunken atrium well edged with a glass balustrade. Every part is a full-size "
                    "sprite registered at one footprint origin, so a state is a list of parts; place them all at the same cell. The canopy is its own part (draws over the "
                    "rail and the trunk); the south rail runs are front_prop so a person on the steps passes behind the newel posts. "
                    "The three incident branches of level 20 can be done in any order, so besides before and after there is a state for every combination: "
                    "repaired_name (The Name: the planter's nameplates become distinct), repaired_route (The Route: the copper floor lines straighten and the corner pots vary), "
                    "repaired_count (The Count: the warm daylight pool and the lamps), and repaired_name_route, repaired_name_count, repaired_route_count. "
                    "after is all three.",
            "size_px": [BOX_W, BOX_H],
            "footprint_origin_px": list(FP),
            "default_state": "before",
            "states": {
                "before": {"parts": before, "lamps": {"anim": "lamp", "state": "on", "offsets_px": LAMP_OFFSETS}},
                "after": {"parts": after, "lamps": {"anim": "lamp", "state": "pulse", "offsets_px": LAMP_OFFSETS}},
                **partial,
            },
            "part_roles": {
                "atrium_well": "base well", "atrium_rail_back": "base balustrade", "atrium_rail_front": "base balustrade", "atrium_planter": "base planter",
                "atrium_trunk": "centrepiece", "atrium_canopy": "centrepiece", "atrium_canopy_shadow": "centrepiece",
                "atrium_inlay_before": "quest state", "atrium_inlay_after": "quest state", "atrium_nameplates_before": "quest state",
                "atrium_nameplates_after": "quest state", "atrium_pots_before": "quest state", "atrium_pots_after": "quest state",
                "atrium_daylight_after": "quest state", "lamp": "light accents",
            },
            "changes_after": [
                "the copper floor lines straighten into three clean paths with chevrons (levels.md 20: copper floor lines straighten into useful paths)",
                "the five nameplates on the planter become distinct plates with their own marks (levels.md 20: nameplates become distinct)",
                "the four corner pots go from identical clipped cubes to soft, varied shrubs with copper blossoms (levels.md district row: repeated geometry becomes varied)",
                "a warm pool of daylight lights the well floor around the planter (levels.md 20: window light warms)",
                "all four atrium lamps switch from the steady glow to the wider pulse glow",
            ],
        }
    }


# ------------------------------------------------------------------ 5. quest props (level 20: the three incident branches and the arriving coworkers' places)
# Audit: QUEST_PROP_AUDIT.md (rows E1 to E11). Executive ramps only; copper is trim and wayfinding.

QUEST_NAMES = set()
QS = (64, 64)   # capture origin for every quest prop
PAL.paper = PAL.floor      # paper and label plates are the pale limestone ramp; read only by quest_props.py


def _quest(name, draw, fp, cells, collision, layer, kind, note, tags, y_sort=True, shadow=True, box=None):
    p = ok.make(name, draw, fp, cells, collision, layer, kind, box=box, shadow=shadow, y_sort=y_sort, note=note, tags=tags)
    QUEST_NAMES.add(name)
    return p


def draw_branch_name(r, x0, y0, state):
    """The Name branch's nameplate, a 40 x 12 copper wall plate on the navy wall. before: Pace's replacement, three orderly
    pale bars (no name, no mark). after: the department's original name, irregular lettering runs after a small crest."""
    r.rect(x0, y0, x0 + 40, y0 + 12, INK[0])
    r.rect(x0 + 1, y0 + 1, x0 + 39, y0 + 11, ACC[2])
    r.rect(x0 + 1, y0 + 1, x0 + 39, y0 + 2, ACC[3])
    r.rect(x0 + 1, y0 + 10, x0 + 39, y0 + 11, ACC[1])
    r.rect(x0 + 3, y0 + 3, x0 + 37, y0 + 9, WALL[0])                    # the recessed text field
    r.rect(x0 + 3, y0 + 3, x0 + 37, y0 + 4, INK[1])
    if state == "before":
        for by in (4, 6, 8):
            r.rect(x0 + 5, y0 + by, x0 + 35, y0 + by + 1, FLOOR[2])
    else:
        crest = r.mask(x0 + 5, y0 + 4, x0 + 10, y0 + 9)                  # a small crest: a doorway
        r.img[crest] = ACC[3]
        r.rect(x0 + 7, y0 + 6, x0 + 8, y0 + 9, WALL[0])
        x = x0 + 12
        for w, tall in ((3, 1), (2, 0), (4, 1), (2, 1), (3, 0), (1, 1), (4, 0), (2, 1), (3, 0)):   # lettering: runs of letters of different widths
            if x + w > x0 + 35:
                break
            r.rect(x, y0 + 5, x + w, y0 + 8, FLOOR[3])
            if tall:
                r.rect(x, y0 + 4, x + 1, y0 + 5, FLOOR[3])
            r.rect(x + 1, y0 + 6, x + w - 1 if w > 2 else x + 1, y0 + 7, WALL[0])
            x += w + 1


def draw_branch_route(r, x0, y0, state):
    """The Route branch's floor line, 4 x 2 cells on the floor markings, in copper. before: a rewarded detour, an S of right
    angles with knots at the corners between the west and east edges. after: one straight line with four chevrons."""
    def hline(xa, xb, y, thick=2):
        r.rect(x0 + xa, y0 + y, x0 + xb, y0 + y + thick, ACC[1])
        r.rect(x0 + xa, y0 + y, x0 + xb, y0 + y + 1, ACC[2])

    def vline(x, ya, yb, thick=2):
        r.rect(x0 + x, y0 + ya, x0 + x + thick, y0 + yb, ACC[1])
        r.rect(x0 + x, y0 + ya, x0 + x + 1, y0 + yb, ACC[2])
    if state == "before":
        hline(0, 14, 15)
        vline(12, 4, 17)
        hline(12, 30, 4)
        vline(28, 4, 29)
        hline(28, 46, 28)
        vline(44, 15, 30)
        hline(44, 64, 15)
        for kx, ky in ((12, 4), (28, 4), (28, 28), (44, 28), (12, 15), (44, 15)):     # knots at the corners
            r.rect(x0 + kx - 1, y0 + ky - 1, x0 + kx + 3, y0 + ky + 3, ACC[2])
            r.rect(x0 + kx - 1, y0 + ky - 1, x0 + kx + 1, y0 + ky + 1, ACC[3])
    else:
        hline(0, 64, 15)
        for cx in (10, 26, 42, 58):                                                  # chevrons pointing east
            for k in range(4):
                r.rect(x0 + cx + k, y0 + 11 + k, x0 + cx + k + 2, y0 + 12 + k, ACC[2])
                r.rect(x0 + cx + k, y0 + 20 - k, x0 + cx + k + 2, y0 + 21 - k, ACC[2])
            r.rect(x0 + cx, y0 + 11, x0 + cx + 1, y0 + 12, ACC[3])
            r.rect(x0 + cx, y0 + 20, x0 + cx + 1, y0 + 21, ACC[3])


def draw_branch_count(r, x0, y0, state):
    """The Count branch's tally board, 2 cells wide on two walnut feet: a pale panel with four sky-blue bars and a total plate.
    before: the total reads 47 in a dull plate and the bars do not add up (no tick). after: the corrected total 52, a copper
    plate and a green tick."""
    r.cast(x0 + 2, x0 + 30, y0 + 27)
    for fx in (x0 + 4, x0 + 25):                                        # feet
        r.rect(fx, y0 + 22, fx + 3, y0 + 27, INK[0])
        r.rect(fx + 1, y0 + 22, fx + 2, y0 + 26, WOOD[2])
    r.rect(x0, y0, x0 + 32, y0 + 23, INK[0])
    r.rect(x0 + 1, y0 + 1, x0 + 31, y0 + 22, WOOD[2])
    r.rect(x0 + 1, y0 + 1, x0 + 31, y0 + 2, WOOD[3])
    r.rect(x0 + 1, y0 + 21, x0 + 31, y0 + 22, WOOD[0])
    r.rect(x0 + 3, y0 + 3, x0 + 29, y0 + 20, FLOOR[3])
    r.rect(x0 + 3, y0 + 3, x0 + 29, y0 + 4, FLOOR[2])
    heights = (7, 5, 8, 4) if state == "before" else (6, 5, 7, 4)
    for i, h in enumerate(heights):
        bx = x0 + 4 + i * 4
        r.rect(bx, y0 + 17 - h, bx + 3, y0 + 17, GLASS[1])
        r.rect(bx, y0 + 17 - h, bx + 1, y0 + 17, GLASS[2])
    r.rect(x0 + 4, y0 + 17, x0 + 20, y0 + 18, INK[2])                  # baseline
    plate = (ACC[2], ACC[3], INK[0]) if state == "after" else (WALL[2], WALL[3], WALL[0])
    r.rect(x0 + 21, y0 + 4, x0 + 30, y0 + 11, INK[0])
    r.rect(x0 + 22, y0 + 5, x0 + 29, y0 + 10, plate[0])
    qp.text(r, x0 + 22, y0 + 5, "52" if state == "after" else "47", INK[0] if state == "after" else plate[1])
    if state == "after":                                                # the tick: a corrected total
        for tx, ty in ((22, 14), (23, 15), (24, 16), (25, 15), (26, 14), (27, 13), (28, 12)):
            r.img[y0 + ty, x0 + tx] = FOL[2]
            r.img[y0 + ty - 1, x0 + tx] = FOL[3] if tx > 23 else FOL[2]
    else:
        r.rect(x0 + 23, y0 + 13, x0 + 28, y0 + 14, WALL[2])             # a mismatch dash under the total


def draw_place_ivo(r, x0, y0):
    """Ivo's place: a reception lectern, 1 cell, with his tablet standing on the slanted top."""
    r.cast(x0 + 2, x0 + 12, y0 + 22, rows=2)
    r.rect(x0 + 3, y0 + 19, x0 + 11, y0 + 22, INK[0])                    # base
    r.rect(x0 + 4, y0 + 19, x0 + 10, y0 + 21, WOOD[1])
    r.rect(x0 + 5, y0 + 10, x0 + 9, y0 + 19, INK[0])                     # post
    r.rect(x0 + 6, y0 + 10, x0 + 8, y0 + 19, WOOD[1])
    r.rect(x0 + 6, y0 + 10, x0 + 7, y0 + 19, WOOD[2])
    top = r.mask(x0 + 1, y0 + 7, x0 + 13, y0 + 11)                       # slanted top
    r.img[top] = WOOD[2]
    r.rect(x0 + 1, y0 + 7, x0 + 13, y0 + 8, WOOD[3])
    r.outline(top)
    tab = r.mask(x0 + 2, y0 + 1, x0 + 12, y0 + 8)                        # the tablet
    r.img[tab] = INK[0]
    r.rect(x0 + 3, y0 + 2, x0 + 11, y0 + 7, GLASS[2])
    r.rect(x0 + 3, y0 + 2, x0 + 11, y0 + 3, GLASS[3])
    r.rect(x0 + 4, y0 + 4, x0 + 8, y0 + 5, GLASS[1])
    r.img[y0 + 6, x0 + 9] = ACC[2]


def draw_place_noor(r, x0, y0):
    """Noor's place: a small walnut table, 1 cell, with her stamp and a file tray of copper-tabbed folders."""
    env.block(r, x0, y0 + 6, x0 + 16, y0 + 22, 6, WOOD, WOOD)
    r.rect(x0 + 2, y0 + 3, x0 + 10, y0 + 12, FLOOR[3])                  # the file tray: two folders with copper tabs
    r.rect(x0 + 2, y0 + 3, x0 + 10, y0 + 4, FLOOR[2])
    r.rect(x0 + 3, y0 + 7, x0 + 10, y0 + 12, FLOOR[2])
    r.rect(x0 + 3, y0 + 7, x0 + 10, y0 + 8, FLOOR[3])
    r.rect(x0 + 3, y0 + 2, x0 + 6, y0 + 4, ACC[2])
    r.rect(x0 + 7, y0 + 6, x0 + 10, y0 + 8, ACC[3])
    r.outline(r.mask(x0 + 2, y0 + 2, x0 + 10, y0 + 12))
    r.rect(x0 + 12, y0 + 6, x0 + 14, y0 + 11, WOOD[3])                  # her stamp: post and knob
    r.rect(x0 + 11, y0 + 4, x0 + 15, y0 + 6, WOOD[3])
    r.rect(x0 + 11, y0 + 4, x0 + 15, y0 + 5, ACC[3])
    r.outline(r.mask(x0 + 12, y0 + 6, x0 + 14, y0 + 11) | r.mask(x0 + 11, y0 + 4, x0 + 15, y0 + 6))


def draw_place_ada(r, x0, y0):
    """Ada's place: a copper lantern stand, 1 cell: a post on a round base with a hook arm and a lit lantern."""
    r.cast(x0 + 1, x0 + 9, y0 + 22, rows=2)
    base = r.disc(x0 + 5, y0 + 20, 4.5, 2)
    r.img[base] = ACC[1]
    r.img[base & ~shifted(base, -1, -1)] = ACC[2]
    r.outline(base)
    r.rect(x0 + 4, y0 + 6, x0 + 7, y0 + 20, INK[0])                      # post
    r.rect(x0 + 5, y0 + 6, x0 + 6, y0 + 20, ACC[2])
    r.rect(x0 + 5, y0 + 6, x0 + 12, y0 + 8, INK[0])                      # hook arm
    r.rect(x0 + 5, y0 + 7, x0 + 12, y0 + 8, ACC[2])
    lan = r.mask(x0 + 9, y0 + 8, x0 + 15, y0 + 17)                       # the lantern
    r.img[lan] = ACC[1]
    r.rect(x0 + 10, y0 + 10, x0 + 14, y0 + 16, ACC[3])
    r.rect(x0 + 11, y0 + 11, x0 + 13, y0 + 15, FLOOR[3])
    r.rect(x0 + 9, y0 + 8, x0 + 15, y0 + 9, ACC[2])
    r.outline(lan)


def draw_place_mira(r, x0, y0):
    """Mira's place: a round navy cushion, 1 cell, with her courier satchel and its copper strap resting on it."""
    r.cast(x0 + 1, x0 + 15, y0 + 17, rows=2)
    cus = r.disc(x0 + 8, y0 + 13, 7.5, 3.8)
    r.img[cus] = WALL[2]
    r.img[cus & ~shifted(cus, -1, -1)] = WALL[3]
    r.img[cus & ~shifted(cus, 1, 1)] = WALL[1]
    r.outline(cus)
    qp.mira_decor(r, "night_courier", x0 + 2, y0 + 1, PAL)


def quest_pieces():
    """The Executive quest props. Returns (pieces, state sets)."""
    out = []
    sx, sy = QS
    for st in ("before", "after"):
        out.append(_quest(f"branch_name_{st}", lambda r, st=st: draw_branch_name(r, sx, sy, st), (sx, sy), (3, 1), ["000"], "rear_wall", "wall",
                          "the Name branch's nameplate (level 20, The Name: a renamed department), a 40 x 12 copper wall plate. "
                          + ("before: Pace's replacement, three orderly pale bars, no name" if st == "before" else "after: the department's original name in irregular lettering after a small crest")
                          + ". Place on the navy north wall face; the plain wall already blocks. Also the plate for the Names on the Wall side quest",
                          ["nameplate", "branch", "the name", "level 20", st], y_sort=False, shadow=False, box=(sx, sy, sx + 40, sy + 12)))
    for st in ("before", "after"):
        out.append(_quest(f"branch_route_{st}", lambda r, st=st: draw_branch_route(r, sx, sy, st), (sx, sy), (4, 2), ["0000", "0000"], "floor_marking", "tile",
                          "the Route branch's floor line (level 20, The Route: a rewarded detour), 4 x 2 cells in copper on the floor markings, west edge to east edge. "
                          + ("before: an S of right angles with knots at the corners, a detour that is rewarded" if st == "before" else "after: one straight line with four chevrons pointing east")
                          + ". Walkable; lay several end to end for a longer branch", ["route", "branch", "the route", "level 20", st],
                          y_sort=False, shadow=False, box=(sx, sy, sx + 64, sy + 32)))
    for st in ("before", "after"):
        out.append(_quest(f"branch_count_{st}", lambda r, st=st: draw_branch_count(r, sx, sy, st), (sx, sy + 11), (2, 1), ["11"], "rear_prop", "prop",
                          "the Count branch's tally board (level 20, The Count: a corrected total), 2 x 1 on two walnut feet: a pale panel with four sky-blue bars and a total plate. "
                          + ("before: the total reads 47 in a dull plate and the bars do not add up" if st == "before" else "after: the corrected total 52 in a copper plate with a green tick"),
                          ["board", "tally", "branch", "the count", "level 20", st], box=(sx, sy, sx + 34, sy + 29)))
    places = (("ivo", draw_place_ivo, (14, 22), "Ivo's place: a reception lectern with his tablet on the slanted top"),
              ("noor", draw_place_noor, (16, 22), "Noor's place: a small walnut table with her stamp and a file tray of copper-tabbed folders"),
              ("hal", None, (16, 15), "Hal's place: his folding stool with the tool roll leaning on it (the shared drawing, Executive ramps)"),
              ("ada", draw_place_ada, (15, 22), "Ada's place: a copper lantern stand with a lit lantern on a hook arm"),
              ("mira", draw_place_mira, (16, 17), "Mira's place: a round navy cushion with her courier satchel and its copper strap"))
    for who, fn, (w, h), note in places:
        if who == "hal":
            draw = lambda r: qp.folding_stool(r, sx, sy, PAL)   # noqa: E731
        else:
            draw = lambda r, fn=fn: fn(r, sx, sy)               # noqa: E731
        out.append(_quest(f"place_{who}", draw, (sx, sy + 6) if who in ("ivo", "noor", "ada") else (sx, sy), (1, 1), ["1"], "rear_prop", "prop",
                          note + " (level 20: an arriving coworker's place; the coworker arrives as a silhouette, then as a sprite, standing here), 1 x 1, blocks its cell", ["place", who, "level 20"]))
    anims = {
        "branch_name": {"kind": "state_set", "default": "before",
                        "states": {"before": {"entries": ["branch_name_before"]}, "after": {"entries": ["branch_name_after"]}},
                        "play": ["before", "after"], "ms_per_frame": 250,
                        "note": "level 20, The Name: the renamed department gets its original name back. Pair with landmark state repaired_name (the planter's nameplates become distinct)"},
        "branch_route": {"kind": "state_set", "default": "before",
                         "states": {"before": {"entries": ["branch_route_before"]}, "after": {"entries": ["branch_route_after"]}},
                         "play": ["before", "after"], "ms_per_frame": 250,
                         "note": "level 20, The Route: the rewarded detour becomes a straight line. Pair with landmark state repaired_route (the atrium's copper lines straighten and the pots vary)"},
        "branch_count": {"kind": "state_set", "default": "before",
                         "states": {"before": {"entries": ["branch_count_before"]}, "after": {"entries": ["branch_count_after"]}},
                         "play": ["before", "after"], "ms_per_frame": 250,
                         "note": "level 20, The Count: the total is corrected. Pair with landmark state repaired_count and the window_a, window_b and window_light sets going to daylight"},
    }
    return out, anims


# ------------------------------------------------------------------ 6. wave 2: district integration
# The shared elevator set, call panel, desk occluders and the audit-copy artifact (quest_props.integration_pieces, drawn with the
# Executive ramps) and the Names on the Wall reward (design/levels/executive/NEEDS_ART.md): desk_name_plaque.

INTEGRATION_NAMES = set()


def _imk(name, draw, box, fp, cells, coll, layer, kind, shadow=True, shadow_rect=None, y_sort=False, note="", tags=()):
    p = ok.make(name, draw, fp, cells, coll, layer, kind, box=box, shadow=shadow, y_sort=y_sort, note=note, tags=list(tags))
    if shadow_rect:
        p.shadow = shadow_rect
    INTEGRATION_NAMES.add(name)
    return p


def _integration(desks):
    out, anims = qp.integration_pieces(lambda *a, **k: _imk(*a, **k), PAL, "executive", desks, desk_pal=qp.artifact_pal(PAL))
    x0, y0 = qp.IX0, qp.IY0
    out.append(_imk("desk_name_plaque", lambda r: qp.reward_decor(r, "name_plaque", x0, y0, PAL), (x0, y0, x0 + 14, y0 + 9), (x0 - 1, y0 + 9 - 16), (1, 1), ["0"], "front_prop", "prop",
                    shadow=False, y_sort=False,
                    note="Names on the Wall reward: a small desk plaque (copper plate with three inked name lines on a walnut base), 14 x 9, 1 x 1, no collision. "
                         "A desk decoration like mail_tray and desk_folder; never placed on the map", tags=["decor", "desk", "reward", "names"]))
    return out, anims


# ------------------------------------------------------------------ assembly

def build_pieces():
    atlas = kitlib.Atlas(ORIENT_ATLAS)
    pieces = recoloured_pieces(atlas)
    pieces += route_arrows()
    pieces += shared_pieces()
    pieces += executive_pieces()
    pieces += landmark_pieces()
    qpieces, qanims = quest_pieces()
    pieces += qpieces
    desks = {p.name: p for p in pieces if p.name in ("desk_a", "desk_b")}
    ipieces, ianims = _integration(desks)
    pieces += ipieces
    anims = {
        "final_door": {
            "kind": "state_set", "default": "closed",
            "states": {"closed": {"entries": ["final_door_closed"], "blocked": True},
                       "half": {"entries": ["final_door_half"], "blocked": True},
                       "open": {"entries": ["final_door_open"], "blocked": False}},
            "play": ["closed", "half", "open"], "ms_per_frame": 120,
            "note": "the last door, visible from the entrance; it opens after the third accurate repair. Same frames as Orientation's sliding door, recoloured; "
                    "the doorway shows a daylit terrace",
        },
        "lamp": {
            "kind": "state_set", "default": "on",
            "states": {"off": {"entries": ["lamp_off"]}, "on": {"entries": ["lamp", "lamp_glow_on"]},
                       "pulse": {"entries": ["lamp", "lamp_glow_pulse"]}},
            "loop": ["on", "pulse"], "ms_per_frame": 600,
            "note": "glow states: off, on (steady), pulse (wider ring). Wake = off -> on; idle breathing = on <-> pulse.",
        },
        "window_a": {
            "kind": "state_set", "default": "overcast",
            "states": {"overcast": {"entries": ["wall_n_window_a_dim"]}, "daylight": {"entries": ["wall_n_window_a"]}},
            "play": ["overcast", "daylight"], "ms_per_frame": 300,
            "note": "window views resolve into real daylight (levels.md 20): overcast flat panes, then the reflecting sky",
        },
        "window_b": {
            "kind": "state_set", "default": "overcast",
            "states": {"overcast": {"entries": ["wall_n_window_b_dim"]}, "daylight": {"entries": ["wall_n_window_b"]}},
            "play": ["overcast", "daylight"], "ms_per_frame": 300,
            "note": "the second reflection phase of window_a",
        },
        "window_light": {
            "kind": "state_set", "default": "overcast",
            "states": {"overcast": {"entries": ["light_shaft_cool"]}, "daylight": {"entries": ["light_shaft_warm"]}},
            "play": ["overcast", "daylight"], "ms_per_frame": 300,
            "note": "the light shaft under a window pair: barely-there cool light, then warm daylight",
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
    if n.startswith("final_door"):
        return 2
    if n.startswith("lamp"):
        return 3
    if n.startswith(("desk_", "chair", "pot_plant", "sofa", "bench", "side_table")):
        return 4
    if n.startswith(("shelf", "partition", "terminal", "cabinet", "light_shaft")):
        return 5
    if n.startswith(("boardroom", "glass_rail")):
        return 6
    return 7


SECTIONS = [(0, "FLOOR, ROUTE AND WAYFINDING"), (1, "WALLS (navy, high windows in two states, copper trim)"), (2, "FINAL DOOR (closed, half, open)"),
            (3, "LAMP (post, off, glow states)"), (4, "REUSED ORIENTATION PROPS (recoloured): desks, navy seating, planters"),
            (5, "SHARED KIT: bookcase, partition, reception console, credenza, window light"),
            (6, "EXECUTIVE-ONLY: boardroom table and chair, glass balustrade"),
            (7, "LANDMARK: THE ATRIUM TREE (registered parts)"),
            (8, "QUEST PROPS (level 20): the three branch props (nameplate, floor line, tally board) and the arriving coworkers' places"),
            (9, "DISTRICT INTEGRATION (wave 2): elevator set and call panel, desk-front occluders, the audit-copy artifact, the name plaque")]


def atlas_json(pieces, rects, anims, lms):
    return {
        "schema": "atlas.schema.json",
        "kit": KIT,
        "image": "executive-atlas.png",
        "tile": T,
        "layers": kitlib.LAYERS,
        "status": "Approved by the director 2026-10-02",
        "source": "Orientation pieces recoloured by exact hex swap (executive_kit.py), shared pieces from shared_pieces.py, Executive-only pieces and the atrium tree landmark; build_executive.py",
        "entries": [p.entry(rects[p.name]) for p in pieces],
        "animations": anims,
        "landmarks": lms,
    }
