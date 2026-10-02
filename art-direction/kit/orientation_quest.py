"""Orientation quest props: the named props levels 01-06 and the Morning Mail route refer to.

New art only, drawn with palette constants in the Orientation palette (STYLE_BIBLE section 3), captured
into atlas pieces with orientation_kit.make (two sentinel backgrounds, so nothing depends on what is under
a piece). Builders that other districts will reuse (elevator door set, desk occluder, artifact props)
live in shared_pieces.py; this module only uses them with the Orientation Pal and adds the Orientation-only
props. orientation_kit.build_pieces() calls build() below; nothing here edits an existing entry.

Drawing coordinates are room pixels on the 320 x 192 env.Room scratch canvas. Every piece is cropped to a
fixed box so the frames of one state set share one origin and a state swap never shifts a pixel.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("gate1", "scale-test", "palettes"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import build_scale_test as bst  # noqa: E402
import environment as env  # noqa: E402
import kitlib  # noqa: E402
import shared_pieces as shp  # noqa: E402

INK, STONE, GLASS, WOOD, GREEN, BRASS, CORAL = env.INK, env.STONE, env.GLASS, env.WOOD, env.GREEN, env.BRASS, env.CORAL
shifted = bst.shifted
PAL = shp.Pal("orientation")
T = 16
X0, Y0 = 64, 64   # scratch origin for every piece (footprint cells start here)


def _ok():
    import orientation_kit
    return orientation_kit


def mk(name, draw, box, fp, cells, coll, layer, kind="prop", shadow=True, **kw):
    """ok.make with a fixed crop box (x0, y0, x1, y1) in scratch coordinates."""
    return _ok().make(name, draw, fp, cells, coll, layer, kind, box=box, shadow=shadow, **kw)


def rel(x0, y0, dx0, dy0, dx1, dy1):
    return (x0 + dx0, y0 + dy0, x0 + dx1, y0 + dy1)


def compose(r, parts, contour=INK[0]):
    """parts: [(mask, fill, lit, dark)]. Paints each, upper-left edge lit, lower-right edge dark, then
    one contour around the union."""
    union = np.zeros_like(parts[0][0])
    for m, fill, lit, dark in parts:
        r.img[m] = fill
        if lit is not None:
            r.img[m & ~shifted(m, -1, -1)] = lit
        if dark is not None:
            r.img[m & ~shifted(m, 1, 1)] = dark
        union |= m
    r.outline(union, contour)
    return union


# ------------------------------------------------------------------ elevator

def elevator_pieces():
    x0, y0 = X0, Y0
    box = (x0, y0, x0 + 48, y0 + 48)
    out = []
    for nm, t, coll, note in (
            ("elevator_closed", 0.0, ["111", "111", "000"],
             "elevator, doors shut: two steel leaves meet at a centre seam, brass casing with two lamps, lit floor indicator, "
             "lit LIFT mat in front"),
            ("elevator_half", 0.5, ["111", "111", "000"],
             "elevator, leaves slid 6 px into the jamb pockets: the warm cab shows between them"),
            ("elevator_open", 1.0, ["111", "101", "000"],
             "elevator, leaves fully in the pockets (11 px, a 1 px lip stays): the cab is open and the centre cell walks in")):
        p = mk(nm, lambda r, t=t: shp.elevator_doors(r, x0, y0, PAL, t), box, (x0, y0), (3, 3), coll, "rear_wall", "door",
               shadow=False, note=note + ". Replaces three wall_n_plain columns; rows 0-1 are wall, row 2 is the mat.",
               tags=["elevator", "door", "sliding", nm.split("_")[1]])
        p.shadow = (0, 32, 48, 2)
        out.append(p)
    out.append(mk("elevator_call_panel", lambda r: shp.elevator_call_panel(r, x0, y0, PAL), rel(x0, y0, 0, 0, 12, 22),
                  (x0, y0), (1, 2), ["0", "0"], "rear_wall", "wall", shadow=False,
                  note="wall call panel for the elevator: steel plate, small lit display, up and down buttons with arrows. "
                       "Overlay on wall_n_plain (no collision of its own); place it on the wall face 9 px below the wall top, "
                       "one cell beside the elevator", tags=["elevator", "panel", "interact"]))
    return out


# ------------------------------------------------------------------ turnstile

def turnstile(r, x0, y0, open_):
    """Reception turnstile: two glass pedestals with card readers and a glass flap barrier across the lane.
    Footprint is 3 x 1 cells at (x0, y0); the sprite rises 11 px above it. open_: flaps folded away and the
    pedestal lights lit."""
    G, A = GLASS, BRASS
    for px0 in (x0 + 3, x0 + 35):
        env.block(r, px0, y0 - 1, px0 + 10, y0 + 16, 7, G, G)
        # card reader on the top plane: housing first, then the lit face and the slot
        r.rect(px0 + 2, y0 - 6, px0 + 8, y0, INK[0])
        r.rect(px0 + 3, y0 - 5, px0 + 7, y0 - 1, INK[1])
        r.rect(px0 + 3, y0 - 5, px0 + 7, y0 - 3, G[3])
        r.rect(px0 + 4, y0 - 2, px0 + 6, y0 - 1, A[2])
        # indicator stripe on the pedestal face
        r.rect(px0 + 2, y0 + 11, px0 + 8, y0 + 13, A[3] if open_ else INK[2])
        r.rect(px0 + 2, y0 + 13, px0 + 8, y0 + 14, A[1] if open_ else INK[1])
    if open_:
        for sx in (x0 + 13, x0 + 34):                    # flaps folded into the pedestals: two slits
            r.rect(sx, y0 + 2, sx + 1, y0 + 8, INK[0])
    else:
        for fx in (x0 + 13, x0 + 24):                    # two glass flaps meeting mid lane
            flap = r.mask(fx, y0 + 1, fx + 11, y0 + 9)
            r.img[flap] = G[2]
            r.rect(fx, y0 + 6, fx + 11, y0 + 9, G[1])
            r.rect(fx, y0 + 1, fx + 11, y0 + 2, G[3])
            r.rect(fx + 3, y0 + 2, fx + 5, y0 + 6, G[3])           # reflection step
            r.outline(flap)


def turnstile_lane(r, x0, y0):
    """Lit floor inlay in the lane (floor_marking): a brass square with a dark brass arrow, north."""
    sq = r.mask(x0 + 18, y0 + 2, x0 + 30, y0 + 14)
    r.img[sq] = BRASS[3]
    r.img[r.edge(sq)] = BRASS[2]
    for i in range(4):                       # arrow head
        r.rect(x0 + 24 - i, y0 + 4 + i, x0 + 24 + i + 1, y0 + 5 + i, BRASS[0])
    r.rect(x0 + 23, y0 + 8, x0 + 25, y0 + 12, BRASS[0])


def turnstile_pieces():
    x0, y0 = X0, Y0
    box = (x0, y0 - 11, x0 + 48, y0 + 19)
    out = []
    for nm, op, coll in (("turnstile_closed", False, ["111"]), ("turnstile_open", True, ["101"])):
        out.append(mk(nm, lambda r, op=op: turnstile(r, x0, y0, op), box, (x0, y0), (3, 1), coll, "rear_prop", "prop",
                      y_sort=True, tags=["turnstile", "gate", "reception", "open" if op else "closed"],
                      note=("flaps folded away and both pedestal stripes lit in brass: the lane is walkable (centre cell)" if op
                            else "two glass flaps meet across the lane, pedestal stripes dark: all three cells block")
                      + ". Glass pedestals with card readers, 3 cells wide, y-sorted"))
    out.append(mk("turnstile_lane_lit", lambda r: turnstile_lane(r, x0, y0), (x0, y0, x0 + 48, y0 + 16), (x0, y0), (3, 1),
                  ["000"], "floor_marking", "tile", shadow=False,
                  note="lit brass floor inlay with a north arrow in the lane cell; belongs to the open state only, so the "
                       "closed to open swap changes flaps, pedestal lights and floor", tags=["turnstile", "floor", "lit"]))
    return out


# ------------------------------------------------------------------ twin clock, conference door, projected form

HANDS = {  # (hour tip, minute tip) offsets from the face centre
    "10:10": ((-2, -2), (4, -2)),
    "4:40": ((2, 3), (-4, 2)),
}


def clock_twin(r, x0, y0, synced):
    """Twin-faced clock on the glass divider: two faces 14 px apart, different times when unsynced.
    A status lamp under the glass is dark until the faces agree. Sprite 30 x 20 at (x0, y0)."""
    G, A = GLASS, BRASS
    body = r.mask(x0, y0, x0 + 30, y0 + 20)
    r.img[body] = INK[1]
    r.rect(x0, y0, x0 + 30, y0 + 1, INK[2])
    r.outline(body)
    for fcx, time in ((x0 + 8, "10:10"), (x0 + 22, "10:10" if synced else "4:40")):
        cy = y0 + 8
        face = r.disc(fcx, cy, 5.6)
        r.img[face] = STONE[3]
        r.img[r.edge(face)] = INK[0]
        for dx, dy in ((0, -4), (4, 0), (0, 4), (-4, 0)):       # 12, 3, 6, 9
            r.img[cy + dy, fcx + dx] = INK[1]
        (hx, hy), (mx, my) = HANDS[time]
        shp.line(r, fcx, cy, fcx + hx, cy + hy, INK[0])
        shp.line(r, fcx, cy, fcx + mx, cy + my, INK[0])
        r.img[cy, fcx] = INK[0]
    r.rect(x0 + 14, y0 + 2, x0 + 16, y0 + 15, G[2])               # the glass between the faces
    r.rect(x0 + 14, y0 + 2, x0 + 15, y0 + 15, G[3])
    r.rect(x0 + 15, y0 + 2, x0 + 16, y0 + 15, G[1])
    lamp = r.mask(x0 + 13, y0 + 16, x0 + 17, y0 + 19)
    r.img[lamp] = A[3] if synced else INK[2]
    r.rect(x0 + 13, y0 + 16, x0 + 17, y0 + 17, A[2] if synced else INK[3])
    r.outline(lamp)


def clock_pieces():
    x0, y0 = X0, Y0
    out = []
    for nm, sy in (("clock_twin_unsynced", False), ("clock_twin_synced", True)):
        out.append(mk(nm, lambda r, sy=sy: clock_twin(r, x0, y0, sy), (x0, y0, x0 + 30, y0 + 20), (x0, y0), (2, 2),
                      ["00", "00"], "rear_wall", "wall", shadow=False,
                      note=("two faces behind one pane of glass show different times (10:10 and 4:40); status lamp dark" if not sy else
                            "both faces show 10:10; the status lamp under the glass is lit brass")
                      + ". Wall overlay, 30 x 20 px, no collision of its own; place on the wall face",
                      tags=["clock", "twin", "wall", "synced" if sy else "unsynced"]))
    return out


def conference_door(r, x0, y0, t):
    """Sunlit conference-room glass door set, 48 x 48 at (x0, y0): wall slice, a dark frame with a lit cap, a
    clock-icon plaque, two glass leaves that slide into the frame, the lit room seen through the opening,
    two lamps and a lit threshold mat (t = 0 closed, 0.5 half, 1 open)."""
    G, A = GLASS, BRASS
    shp.wall_slice(r, x0, y0, 48, PAL)
    ox0, ox1, oy0, oy1 = x0 + 8, x0 + 40, y0 + 14, y0 + 31
    # frame: dark with lit cap, like the glass partitions
    fr = r.mask(x0 + 5, y0 + 11, x0 + 43, y0 + 32)
    r.img[fr] = G[0]
    r.rect(x0 + 5, y0 + 11, x0 + 43, y0 + 13, G[2])
    r.rect(x0 + 5, y0 + 11, x0 + 43, y0 + 12, G[3])
    r.rect(x0 + 5, y0 + 13, x0 + 8, y0 + 31, G[1])
    r.rect(x0 + 5, y0 + 13, x0 + 6, y0 + 31, G[2])
    r.rect(x0 + 40, y0 + 13, x0 + 43, y0 + 31, G[0])
    r.outline(fr)
    # the room beyond, in daylight: bright wall, a light patch, a table edge and two chair backs
    room = r.mask(ox0, oy0, ox1, oy1)
    r.img[room] = STONE[3]
    r.rect(ox0, oy0, ox1, oy0 + 2, INK[0])
    r.rect(ox0, oy0 + 2, ox1, oy0 + 3, INK[2])
    patch = np.zeros_like(room)
    for i in range(0, 12):                                 # daylight patch, one hard step
        patch |= r.mask(ox0 + 12 + i // 2, oy0 + 3 + i, ox0 + 22 + i // 2, oy0 + 4 + i)
    r.img[patch & room] = BRASS[3]
    r.rect(ox0 + 2, oy0 + 9, ox1 - 2, oy0 + 12, WOOD[2])   # table top
    r.rect(ox0 + 2, oy0 + 9, ox1 - 2, oy0 + 10, WOOD[3])
    r.rect(ox0 + 2, oy0 + 12, ox1 - 2, oy0 + 13, WOOD[1])
    for cx in (ox0 + 6, ox0 + 22):                         # chair backs
        r.rect(cx, oy0 + 5, cx + 5, oy0 + 9, CORAL[1])
        r.rect(cx, oy0 + 5, cx + 5, oy0 + 6, CORAL[2])
    r.rect(ox0, oy1 - 3, ox1, oy1, STONE[2])
    # leaves
    tr = int(round(15 * max(0.0, min(1.0, t))))
    for k, lx in enumerate((ox0 - tr, ox0 + 16 + tr)):
        a0, a1 = max(lx, ox0), min(lx + 16, ox1)
        if a0 >= a1:
            continue
        leaf = r.mask(a0, oy0, a1, oy1)
        r.img[leaf & (r.y >= oy0 + 3)] = G[1] if False else G[2]
        r.img[leaf & (r.y >= oy1 - 7)] = G[1]
        r.rect(a0, oy0, a1, oy0 + 3, G[0])                                   # leaf frame, top
        r.rect(a0, oy1 - 2, a1, oy1, G[0])
        if lx >= a0:
            r.rect(lx, oy0, lx + 1, oy1, G[0])
        if lx + 16 <= a1:
            r.rect(lx + 15, oy0, lx + 16, oy1, G[0])
        band = leaf & (np.abs((r.x - lx) - (r.y - oy0 - 3) * 0.8 - 4) < 1.4) & (r.y >= oy0 + 3) & (r.y < oy1 - 7)
        r.img[band] = G[3]
        r.img[leaf & (np.abs((r.x - lx) - (r.y - oy0 - 3) * 0.8 - 9) < 0.6) & (r.y >= oy0 + 3) & (r.y < oy1 - 7)] = G[2]
        # brass pull on the meeting edge
        px = lx + 13 if k == 0 else lx + 2
        if a0 <= px < a1 - 1:
            r.rect(px, oy0 + 5, px + 1, oy0 + 10, A[3])
    r.rect(ox0 - 3, oy1, ox1 + 3, oy1 + 1, INK[0])
    # plaque with a clock icon, lamps, mat
    pl = r.mask(x0 + 18, y0 + 7, x0 + 30, y0 + 11)
    r.img[pl] = A[2]
    r.rect(x0 + 18, y0 + 7, x0 + 30, y0 + 8, A[3])
    r.rect(x0 + 18, y0 + 10, x0 + 30, y0 + 11, A[0])
    r.outline(pl)
    r.img[y0 + 9, x0 + 22:x0 + 26] = INK[1]
    r.img[y0 + 8, x0 + 23] = INK[1]
    shp.sconce(r, x0 + 2, y0 + 18, PAL)
    shp.sconce(r, x0 + 46, y0 + 18, PAL)
    shp.lit_mat(r, x0 + 8, y0 + 36, 32, 9, PAL, "MEET", chevrons=False)


def conference_pieces():
    x0, y0 = X0, Y0
    box = (x0, y0, x0 + 48, y0 + 48)
    out = []
    for nm, t, coll, note in (
            ("conference_glass_door_closed", 0.0, ["111", "111", "000"],
             "meeting-room glass door shut: two glass leaves with a reflection band and brass pulls meet mid frame; the lit room is visible through them"),
            ("conference_glass_door_half", 0.5, ["111", "111", "000"],
             "leaves slid 8 px apart: the sunlit room shows through the gap"),
            ("conference_glass_door_open", 1.0, ["111", "101", "000"],
             "leaves fully slid aside (15 px): the doorway is open, the centre cell walks in")):
        p = mk(nm, lambda r, t=t: conference_door(r, x0, y0, t), box, (x0, y0), (3, 3), coll, "rear_wall", "door",
               shadow=False, note=note + ". Replaces three wall_n_plain columns; rows 0-1 are wall, row 2 is the lit MEET mat.",
               tags=["door", "sliding glass", "conference", nm.rsplit("_", 1)[1]])
        p.shadow = (0, 32, 48, 2)
        out.append(p)
    return out


def projected_form(r, x0, y0):
    """Form projected on the wall: a lit rectangle, a title bar, three fields and a clear focus outline around
    the second field. The first field's entry is jammed together (the missing spaces), the second has gaps.
    62 x 22 px at (x0, y0)."""
    G = GLASS
    beam = r.mask(x0, y0, x0 + 62, y0 + 22)
    r.img[beam] = STONE[3]
    r.img[r.edge(beam)] = STONE[2]
    r.rect(x0 + 3, y0 + 2, x0 + 27, y0 + 4, INK[2])          # title bar
    r.rect(x0 + 3, y0 + 2, x0 + 27, y0 + 3, INK[1])
    r.rect(x0 + 50, y0 + 2, x0 + 59, y0 + 4, INK[3])         # form number
    for i, (lab, txt) in enumerate(((7, (4, 10, 3)), (12, (4, 3, 3, 4)), (17, (5, 4)))):
        fy = y0 + lab
        r.rect(x0 + 3, fy + 1, x0 + 11, fy + 2, INK[1])        # label
        fld = r.mask(x0 + 14, fy - 1, x0 + 59, fy + 4)
        r.img[fld] = STONE[2]
        r.img[r.edge(fld)] = INK[3]
        tx = x0 + 16
        for w in txt:
            r.rect(tx, fy, tx + w, fy + 2, INK[1])
            tx += w + (0 if i == 0 else 2)                    # row 0: words run together
    # focus outline: a clear double line around field two, with corner ticks
    fx0, fy0, fx1, fy1 = x0 + 12, y0 + 10, x0 + 61, y0 + 17
    for (ax, ay, bx, by) in ((fx0, fy0, fx1, fy0 + 1), (fx0, fy1 - 1, fx1, fy1), (fx0, fy0, fx0 + 1, fy1), (fx1 - 1, fy0, fx1, fy1)):
        r.rect(ax, ay, bx, by, G[1])
    for (cx, cy) in ((fx0 - 1, fy0 - 1), (fx1, fy0 - 1), (fx0 - 1, fy1), (fx1, fy1)):
        if x0 <= cx < x0 + 62 and y0 <= cy < y0 + 22:
            r.img[cy, cx] = G[3]


def form_piece():
    x0, y0 = X0, Y0
    return mk("projected_form_wall", lambda r: projected_form(r, x0, y0), (x0, y0, x0 + 62, y0 + 22), (x0, y0), (4, 2),
              ["0000", "0000"], "rear_wall", "wall", shadow=False,
              note="scheduling form projected on a wall: lit rectangle, title bar, three fields (the first entry has no spaces), "
                   "and a blue double-line focus outline around the second field (level 03's Tab target). Wall overlay, 62 x 22 px, "
                   "no collision of its own", tags=["form", "projection", "focus", "wall", "level 03"])


# ------------------------------------------------------------------ stamps (left desk a-d, right desk e-h)

STAMP_W, STAMP_H = 8, 8


def stamp(r, x0, y0, kind):
    """Small desk prop, 8 x 8 px at (x0, y0), body rows 0-7, contact shadow at row 8. Left-desk stamps (a-d) hold
    their grip centred or to the left; right-desk stamps (e-h) lean to the right."""
    M = r.mask
    base = lambda a, b: (M(x0 + a, y0 + 6, x0 + b, y0 + 8), BRASS[2], BRASS[3], BRASS[0])  # noqa: E731
    if kind == "a":      # mushroom: round coral knob on a neck over a wide plate
        parts = [(r.disc(x0 + 3.5, y0 + 2.5, 2.7), CORAL[2], CORAL[3], CORAL[1]),
                 (M(x0 + 3, y0 + 4, x0 + 5, y0 + 6), INK[1], None, None), base(0, 7)]
    elif kind == "b":    # T handle: a bar over a thin stem and a small plate
        parts = [(M(x0 + 0, y0, x0 + 6, y0 + 2), GREEN[2], GREEN[3], GREEN[1]),
                 (M(x0 + 2, y0 + 2, x0 + 4, y0 + 6), WOOD[1], None, None), base(1, 5)]
    elif kind == "c":    # rocker: a wide glass dome with a small knob on top and a flat plate
        dome = r.disc(x0 + 4, y0 + 8, 4.4, 4.6) & (r.y < y0 + 7)
        parts = [(dome, GLASS[2], GLASS[3], GLASS[1]), (M(x0 + 3, y0 + 1, x0 + 5, y0 + 3), WOOD[2], WOOD[3], WOOD[1]),
                 (M(x0, y0 + 7, x0 + 8, y0 + 8), BRASS[1], BRASS[3], BRASS[0])]
    elif kind == "d":    # dater box: a square brass body with a window and two dials
        parts = [(M(x0 + 1, y0 + 2, x0 + 7, y0 + 8), BRASS[2], BRASS[3], BRASS[1])]
    elif kind == "e":    # hook: a grip leaning right over a post and plate
        parts = [(M(x0 + 2, y0, x0 + 8, y0 + 2), WOOD[3], WOOD[3], WOOD[2]),
                 (M(x0 + 2, y0 + 2, x0 + 4, y0 + 6), WOOD[2], None, None), base(0, 6)]
    elif kind == "f":    # cone: a green wedge that widens to its plate
        cone = (np.abs(r.x - (x0 + 3.5)) <= (r.y - y0) * 0.38 + 0.6) & (r.y >= y0) & (r.y < y0 + 6) & (r.x >= x0) & (r.x < x0 + 7)
        parts = [(cone, GREEN[2], GREEN[3], GREEN[1]), base(1, 6)]
    elif kind == "g":    # dater wheel: a ringed disc with a side tab on a stem
        parts = [(r.disc(x0 + 3.5, y0 + 3, 3.4), WOOD[1], WOOD[2], WOOD[0]),
                 (M(x0 + 6, y0 + 2, x0 + 8, y0 + 4), WOOD[2], None, None),
                 (M(x0 + 3, y0 + 5, x0 + 5, y0 + 6), INK[1], None, None), base(1, 6)]
    elif kind == "h":    # pen stamp: a long thin diagonal grip with a brass tip
        diag = (np.abs((r.x - x0) + (r.y - y0) - 8.0) < 1.3) & (r.x >= x0) & (r.x < x0 + 8) & (r.y >= y0) & (r.y < y0 + 8)
        parts = [(diag, WOOD[3], WOOD[3], WOOD[2])]
    else:
        raise ValueError(kind)
    compose(r, parts)
    if kind == "d":
        r.rect(x0 + 2, y0 + 3, x0 + 6, y0 + 5, INK[1])
        r.rect(x0 + 2, y0 + 6, x0 + 3, y0 + 7, INK[0])
        r.rect(x0 + 5, y0 + 6, x0 + 6, y0 + 7, INK[0])
    if kind == "c":
        r.rect(x0 + 3, y0 + 4, x0 + 4, y0 + 6, GLASS[3])
    if kind == "g":
        r.disc(x0 + 3.5, y0 + 3, 1.6)
        r.img[r.disc(x0 + 3.5, y0 + 3, 1.6)] = GLASS[1]
        r.img[y0 + 2, x0 + 3] = GLASS[3]
    if kind == "h":
        r.img[y0 + 6, x0 + 1] = BRASS[2]
        r.img[y0 + 7, x0 + 0] = BRASS[2]
        r.img[y0 + 7, x0 + 1] = INK[0]
    r.cast(x0, x0 + STAMP_W - 1, y0 + 8, rows=1)


def stamp_pieces():
    x0, y0 = X0, Y0
    out = []
    side = {"a": "left", "b": "left", "c": "left", "d": "left", "e": "right", "f": "right", "g": "right", "h": "right"}
    shape = {"a": "mushroom knob on a neck and wide plate (coral)", "b": "T handle over a thin stem (green)",
             "c": "rocker dome (glass blue)", "d": "square dater box with window and dials (brass)",
             "e": "hook grip leaning right (warm wood)", "f": "cone widening to its plate (green)",
             "g": "dater wheel with a side tab on a stem (plum wood)", "h": "pen stamp: a long thin diagonal grip (peach wood)"}
    for k in "abcdefgh":
        out.append(mk(f"stamp_{k}", lambda r, k=k: stamp(r, x0, y0, k), (x0, y0, x0 + 8, y0 + 9), (x0, y0), (1, 1), ["0"],
                      "front_prop", "prop",
                      note=f"{side[k]}-desk approval stamp {k.upper()}: {shape[k]}. 8 x 9 px with a one-row contact shadow. "
                           "Drawn after the desk, no collision; the four stamps of a desk sit 8 px apart along the front of the top plane",
                      tags=["stamp", "desk prop", f"{side[k]} desk"]))
    return out


# ------------------------------------------------------------------ pinboard (states empty, before, after)

PB_W, PB_H = 48, 23


def _sheet(r, x, y, w, h, tone=3, marks=(), c_mark=None):
    m = r.mask(x, y, x + w, y + h)
    r.img[m] = STONE[tone]
    r.outline(m, INK[1])
    for i in range(marks[0] if marks else 0):
        r.rect(x + 1, y + 2 + i * 2, x + w - 2 - (i % 2), y + 3 + i * 2, INK[3])
    if c_mark is not None:
        r.rect(x + w - 4, y + h - 4, x + w - 2, y + h - 2, c_mark)
    return m


def pinboard(r, x0, y0, state):
    """Cork board in a wood frame, 48 x 23 px at (x0, y0). empty: four faint outlines and bare pins.
    before: four identical sheets in a symmetrical row with centred pins and a centred header strip (orderly).
    after: seven items of different sizes and heights, a sticky note, a string, and a hand-drawn map whose
    route arrow points right, toward the review desk (asymmetrical, human)."""
    frame = r.mask(x0, y0, x0 + PB_W, y0 + PB_H)
    r.img[frame] = WOOD[1]
    r.rect(x0, y0, x0 + PB_W, y0 + 1, WOOD[2])
    r.rect(x0, y0, x0 + 1, y0 + PB_H, WOOD[2])
    r.rect(x0, y0 + PB_H - 1, x0 + PB_W, y0 + PB_H, WOOD[0])
    r.outline(frame)
    cork = r.mask(x0 + 2, y0 + 2, x0 + PB_W - 2, y0 + PB_H - 2)
    r.img[cork] = WOOD[2]
    for (cx, cy) in ((6, 5), (14, 17), (23, 6), (33, 18), (41, 8), (9, 11), (28, 13), (44, 16), (19, 12)):
        r.img[y0 + cy, x0 + cx] = WOOD[1]           # cork grain, a few clusters
    r.rect(x0 + 2, y0 + 2, x0 + PB_W - 2, y0 + 3, WOOD[3])   # lit top edge of the cork
    ix, iy = x0 + 2, y0 + 2                                    # interior origin (44 x 19)
    if state == "empty":
        for i in range(4):
            sx = ix + 2 + i * 11
            r.rect(sx, iy + 4, sx + 7, iy + 5, WOOD[1])
            r.rect(sx, iy + 15, sx + 7, iy + 16, WOOD[1])
            r.rect(sx, iy + 4, sx + 1, iy + 16, WOOD[1])
            r.rect(sx + 6, iy + 4, sx + 7, iy + 16, WOOD[1])
            r.img[iy + 3, sx + 3] = CORAL[2]
    elif state == "before":
        hdr = r.mask(ix + 12, iy + 1, ix + 32, iy + 3)         # centred header strip
        r.img[hdr] = STONE[2]
        r.outline(hdr, INK[1])
        for i in range(4):
            sx = ix + 2 + i * 11
            _sheet(r, sx, iy + 5, 7, 11, marks=(3,))
            r.rect(sx + 2, iy + 12, sx + 5, iy + 14, INK[1])    # the same approval mark on each sheet
            r.img[iy + 4, sx + 3] = CORAL[2]                    # one centred pin each
    elif state == "after":
        specs = [  # x, y, w, h, tone, marks
            (1, 3, 7, 9, 3, 3), (9, 6, 6, 11, 3, 3), (16, 2, 7, 10, 2, 2), (4, 12, 7, 6, 3, 1), (24, 8, 5, 5, 3, 0)]
        for (sx, sy, w, h, tone, nm) in specs:
            _sheet(r, ix + sx, iy + sy, w, h, tone, marks=(nm,))
        # a sticky note and a curled corner
        sn = r.mask(ix + 10, iy + 3, ix + 14, iy + 7)
        r.img[sn] = CORAL[3]
        r.outline(sn, CORAL[1])
        r.rect(ix + 12, iy + 4, ix + 13, iy + 5, CORAL[1])
        # a tilted sheet: stair-stepped
        for k in range(8):
            r.rect(ix + 19 + k // 2, iy + 11 + k, ix + 24 + k // 2, iy + 12 + k, STONE[3])
        for k in range(8):
            r.img[iy + 11 + k, ix + 19 + k // 2] = INK[1]
            r.img[iy + 11 + k, ix + 23 + k // 2] = INK[1]
        r.rect(ix + 20, iy + 18, ix + 24, iy + 19, INK[1])
        # the hand-drawn map: a larger sheet at the right with a route and an arrow toward the review desk
        mp = _sheet(r, ix + 30, iy + 2, 13, 14, 3)
        shp.line(r, ix + 32, iy + 13, ix + 32, iy + 8, INK[2])          # route out
        shp.line(r, ix + 32, iy + 8, ix + 36, iy + 8, INK[2])
        shp.line(r, ix + 36, iy + 8, ix + 36, iy + 12, INK[2])
        shp.line(r, ix + 36, iy + 12, ix + 40, iy + 12, CORAL[1])        # arrow shaft ...
        r.rect(ix + 40, iy + 11, ix + 41, iy + 14, CORAL[1])            # ... and head, pointing right
        r.rect(ix + 41, iy + 12, ix + 42, iy + 13, CORAL[1])
        r.rect(ix + 31, iy + 4, ix + 36, iy + 5, INK[3])                # map title scrawl
        r.rect(ix + 38, iy + 5, ix + 41, iy + 8, GREEN[2])              # garden block on the map
        r.rect(ix + 38, iy + 5, ix + 41, iy + 6, GREEN[3])
        # string from a pin on the map to the first sheet
        shp.line(r, ix + 5, iy + 3, ix + 30, iy + 3, CORAL[1])
        for (px_, py_) in ((4, 2), (12, 5), (19, 1), (33, 1), (26, 7), (5, 11)):
            r.img[iy + py_, ix + px_] = CORAL[2]
    else:
        raise ValueError(state)


def pinboard_pieces():
    x0, y0 = X0, Y0
    box = (x0, y0, x0 + PB_W, y0 + PB_H)
    notes = {"empty": "bare cork with four faint sheet outlines and pins: the board before level 04",
             "before": "orderly: four identical sheets in a symmetrical row, one centred pin each, a centred header strip. "
                       "The board after level 04 (each approved sheet joined it)",
             "after": "asymmetrical and human: sheets of different sizes at different heights, a sticky note, a tilted sheet, "
                      "a string, and a hand-drawn map whose route arrow points right toward the review desk. After level 05"}
    out = []
    for st in ("empty", "before", "after"):
        out.append(mk(f"pinboard_{st}", lambda r, st=st: pinboard(r, x0, y0, st), box, (x0, y0), (3, 2), ["000", "000"],
                      "rear_wall", "wall", shadow=False, note=notes[st] + ". Wall overlay, 48 x 23 px, no collision of its own",
                      tags=["pinboard", "wall", st]))
    return out


# ------------------------------------------------------------------ desks

CHERRY_TOP = [WOOD[0], CORAL[0], WOOD[1], WOOD[2]]
CHERRY_SIDE = [WOOD[0], CORAL[0], WOOD[1], WOOD[2]]


def _desk_common(r, x0, y0, top, side, brass_pull=True):
    env.block(r, x0, y0, x0 + 34, y0 + 16, 5, top, side)
    if brass_pull:
        r.rect(x0 + 15, y0 + 12, x0 + 19, y0 + 13, BRASS[2])
    # shallow stamp tray along the front of the top plane: four slots 8 px apart
    for i in range(4):
        sx = x0 + 2 + i * 8
        r.rect(sx, y0 + 9, sx + 7, y0 + 10, top[1])


def desk_left_cherry(r, x0, y0):
    """Left desk: cherry wood (deeper and redder than desk_a), a small monitor, a stack of sheets, an ink pad
    and a four-slot stamp tray. The monitor ends above the stamps' tops (row 2), so the four stamp props
    stand clear of it. No chair, no lamp (the floor lamp is a separate state set)."""
    _desk_common(r, x0, y0, CHERRY_TOP, CHERRY_SIDE)
    # grain on the top plane: short dark streaks
    for (gx, gy, gl) in ((3, 4, 4), (24, 6, 3), (28, 2, 4)):
        r.rect(x0 + gx, y0 + gy, x0 + gx + gl, y0 + gy + 1, CORAL[0])
    # monitor: housing first, then screen
    r.rect(x0 + 10, y0 - 6, x0 + 24, y0 + 3, INK[0])
    r.rect(x0 + 11, y0 - 5, x0 + 23, y0 + 1, GLASS[1])
    r.rect(x0 + 11, y0 - 5, x0 + 23, y0 - 3, GLASS[2])
    r.rect(x0 + 12, y0 - 4, x0 + 15, y0 - 3, GLASS[3])
    r.rect(x0 + 16, y0 + 3, x0 + 18, y0 + 4, INK[1])
    # stack of approved sheets (left) and an ink pad (right)
    _sheet(r, x0 + 1, y0 + 1, 7, 4, 3)
    r.rect(x0 + 2, y0 + 5, x0 + 8, y0 + 6, INK[1])
    pad = r.mask(x0 + 26, y0 + 1, x0 + 32, y0 + 5)
    r.img[pad] = INK[1]
    r.rect(x0 + 27, y0 + 2, x0 + 31, y0 + 4, CORAL[2])
    r.outline(pad)


def desk_right_mirror(r, x0, y0):
    """Right desk: the same family with a mirrored layout (monitor and keyboard on the left, sheets and the pad
    on the right) and the same four-slot tray. Warm terracotta top as desk_a. The warm lamp is the separate
    lamp_warm state set."""
    _desk_common(r, x0, y0, WOOD, WOOD, brass_pull=False)
    r.rect(x0 + 18, y0 + 12, x0 + 22, y0 + 13, BRASS[2])
    r.rect(x0 + 8, y0 - 6, x0 + 22, y0 + 3, INK[0])
    r.rect(x0 + 9, y0 - 5, x0 + 21, y0 + 1, GLASS[1])
    r.rect(x0 + 9, y0 - 5, x0 + 21, y0 - 3, GLASS[2])
    r.rect(x0 + 18, y0 - 4, x0 + 21, y0 - 3, GLASS[3])
    r.rect(x0 + 14, y0 + 3, x0 + 16, y0 + 4, INK[1])
    for (gx, gy, gl) in ((2, 3, 4), (26, 5, 3)):
        r.rect(x0 + gx, y0 + gy, x0 + gx + gl, y0 + gy + 1, WOOD[1])
    pad = r.mask(x0 + 2, y0 + 1, x0 + 8, y0 + 5)
    r.img[pad] = INK[1]
    r.rect(x0 + 3, y0 + 2, x0 + 7, y0 + 4, CORAL[2])
    r.outline(pad)
    _sheet(r, x0 + 26, y0 + 0, 7, 5, 3)
    r.rect(x0 + 27, y0 + 5, x0 + 33, y0 + 6, INK[1])


def desk_pieces():
    x0, y0 = X0, Y0
    box = (x0 - 1, y0 - 6, x0 + 36, y0 + 18)
    out = []
    out.append(mk("desk_left_cherry", lambda r: desk_left_cherry(r, x0, y0), box, (x0, y0), (2, 1), ["11"], "rear_prop", "prop",
                  y_sort=True, note="left desk (level 04): cherry wood, small monitor, sheet stack, ink pad and a four-slot stamp "
                                    "tray along the front. Same footprint as desk_a; place stamp_a to stamp_d at x +2, +10, +18, +26 "
                                    "px, y +1 px (tops sit under the monitor line)", tags=["desk", "left desk", "cherry"]))
    out.append(mk("desk_right_mirror", lambda r: desk_right_mirror(r, x0, y0), box, (x0, y0), (2, 1), ["11"], "rear_prop", "prop",
                  y_sort=True, note="right desk (level 05): the desk_a family with a mirrored layout (monitor left, sheets and pad "
                                    "right) and the same four-slot tray; place stamp_e to stamp_h at x +2, +10, +18, +26 px, y +1 px",
                  tags=["desk", "right desk", "mirror"]))
    return out


def desk_front_pieces():
    """desk_a_front and desk_b_front: the front_prop occluders, cut from the palette-driven desk."""
    # The plant's lit tips depend on (x + y) % 3 of the room pixel, so draw at an origin with the same parity as
    # the room's desks (16 + 78 and 246 + 46 are both 1 mod 3) and the occluder matches desk_a and desk_b exactly.
    x0, y0 = X0, Y0 + 2
    assert (x0 + y0) % 3 == (16 + 78) % 3 == (246 + 46) % 3
    out = []
    for nm, seed in (("desk_a_front", 7), ("desk_b_front", 8)):
        out.append(mk(nm, lambda r, seed=seed: shp.desk_front(r, x0, y0, PAL, seed), (x0, y0 + shp.FRONT_TOP, x0 + 35, y0 + shp.FRONT_BOT),
                      (x0, y0), (2, 1), ["00"], "front_prop", "prop", shadow=False, y_sort=True,
                      note=f"occluder for {nm[:6]}: the desk's monitor and first 8 px of top plane redrawn on front_prop so a seated worker's "
                           "lower body is hidden; seamless over the desk (same pixels). See ORIENTATION_KIT_SPEC for the rows it covers",
                      tags=["desk", "front", "occluder"]))
    return out


# ------------------------------------------------------------------ review table and keyboards

def review_table(r, x0, y0):
    """Garden review table, 3 cells: wood top with two inlaid blotters where the keyboards sit (left 16 px,
    right 24 px), a brass edge strip and a roster clip."""
    env.block(r, x0, y0, x0 + 48, y0 + 16, 5, WOOD, WOOD)
    for (bx0, bx1) in ((x0 + 3, x0 + 19), (x0 + 22, x0 + 46)):
        b = r.mask(bx0, y0 + 1, bx1, y0 + 10)
        r.img[b] = WOOD[1]
        r.rect(bx0, y0 + 1, bx1, y0 + 2, WOOD[0])
    r.rect(x0 + 1, y0 + 11, x0 + 47, y0 + 12, BRASS[1])        # brass edge strip on the face
    r.rect(x0 + 1, y0 + 11, x0 + 47, y0 + 12, BRASS[1])
    r.rect(x0 + 20, y0 + 2, x0 + 21, y0 + 9, WOOD[2])           # divider between the two stations


def keyboard_macbook(r, x0, y0):
    """Laptop, open, seen from above: dark bezel and lit screen behind a hinge, a silver deck with three key
    rows and a trackpad. 14 x 9 px at (x0, y0)."""
    r.cast(x0, x0 + 13, y0 + 9, rows=1)
    scr = r.mask(x0 + 1, y0, x0 + 13, y0 + 4)
    r.img[scr] = INK[0]
    r.rect(x0 + 2, y0 + 1, x0 + 12, y0 + 3, GLASS[2])
    r.rect(x0 + 2, y0 + 1, x0 + 12, y0 + 2, GLASS[3])
    deck = r.mask(x0, y0 + 4, x0 + 14, y0 + 9)
    r.img[deck] = INK[3]
    r.rect(x0, y0 + 4, x0 + 14, y0 + 5, STONE[3])
    r.rect(x0 + 1, y0 + 5, x0 + 13, y0 + 6, INK[2])              # key row 1
    for kx in range(x0 + 2, x0 + 12, 2):
        r.img[y0 + 5, kx] = INK[0]
    for kx in range(x0 + 2, x0 + 12, 2):
        r.img[y0 + 6, kx] = INK[1]
    r.rect(x0 + 5, y0 + 7, x0 + 9, y0 + 8, INK[2])             # trackpad
    r.outline(r.mask(x0, y0, x0 + 14, y0 + 9))


def keyboard_spare(r, x0, y0):
    """Spare full-size keyboard with a cable: a stone-beige body, light keycaps in four rows with dark gaps, a
    separated number pad at the right, a thick lit top edge. 24 x 8 px at (x0, y0); the cable leaves the top left."""
    r.cast(x0, x0 + 23, y0 + 8, rows=1)
    body = r.mask(x0, y0, x0 + 24, y0 + 8)
    r.img[body] = STONE[1]
    r.rect(x0, y0, x0 + 24, y0 + 1, STONE[2])
    for row in range(3):
        for kx in range(x0 + 1, x0 + 17, 2):
            r.img[y0 + 1 + row * 2, kx] = STONE[3]
            r.img[y0 + 2 + row * 2, kx] = STONE[0]
        for kx in range(x0 + 18, x0 + 23, 2):
            r.img[y0 + 1 + row * 2, kx] = STONE[3]
            r.img[y0 + 2 + row * 2, kx] = STONE[0]
    r.rect(x0 + 4, y0 + 7, x0 + 13, y0 + 8, STONE[3])        # space bar
    r.rect(x0 + 17, y0 + 1, x0 + 18, y0 + 7, STONE[0])         # gap before the number pad
    r.outline(body)
    r.rect(x0 + 2, y0 - 2, x0 + 3, y0, INK[1])                 # cable
    r.rect(x0 + 3, y0 - 3, x0 + 6, y0 - 2, INK[1])


def table_pieces():
    x0, y0 = X0, Y0
    out = []
    out.append(mk("review_table", lambda r: review_table(r, x0, y0), (x0 - 1, y0, x0 + 50, y0 + 19), (x0, y0), (3, 1), ["111"],
                  "rear_prop", "prop", y_sort=True,
                  note="garden review table (level 06): 3 cells, wood top with two inlaid blotters, one 16 px wide for the laptop on "
                       "the left and one 24 px for the spare keyboard on the right. Place keyboard_macbook at x +3 px, y +1 px and "
                       "keyboard_spare at x +22 px, y +2 px", tags=["table", "review", "level 06"]))
    out.append(mk("keyboard_macbook", lambda r: keyboard_macbook(r, x0, y0), (x0, y0, x0 + 14, y0 + 11), (x0, y0), (1, 1), ["0"],
                  "front_prop", "prop",
                  note="MacBook-style laptop seen from above: dark bezel and lit screen, silver deck, key rows and a trackpad. 14 x 9 px, "
                       "no collision; the default physical diagram for level 06", tags=["keyboard", "macbook", "laptop", "level 06"]))
    out.append(mk("keyboard_spare", lambda r: keyboard_spare(r, x0, y0), (x0, y0 - 3, x0 + 24, y0 + 10), (x0, y0), (2, 1), ["00"],
                  "front_prop", "prop",
                  note="spare full-size wired keyboard: beige body, light keycaps in rows, a separate number pad and a cable. 24 x 8 px, "
                       "physically different from keyboard_macbook (wider, flat, corded, number pad, beige against silver); no collision",
                  tags=["keyboard", "spare", "wired", "level 06"]))
    return out


# ------------------------------------------------------------------ mailroom

MEDAL_RIBBONS = [CORAL[3], GREEN[3], WOOD[3], INK[1], BRASS[3], GLASS[2]]   # Mira's patch colours, palette-limited
MB_W, MB_H = 48, 30
MEDAL_CX = [6 + 7 * i for i in range(6)]


def mail_board(r, x0, y0, medals=0, medals_only=False):
    """Free-standing mailroom board, 48 x 30 px (3 cells wide), with a brass MAIL plate and six medal hooks. With
    medals_only the board is not drawn and only the first `medals` medals are painted, for the overlay entries."""
    if not medals_only:
        r.cast(x0 + 2, x0 + 46, y0 + 30, rows=2)
        panel = r.mask(x0, y0, x0 + MB_W, y0 + 26)
        r.img[panel] = WOOD[1]
        r.rect(x0, y0, x0 + MB_W, y0 + 1, WOOD[2])
        r.rect(x0, y0, x0 + 1, y0 + 26, WOOD[2])
        r.rect(x0, y0 + 25, x0 + MB_W, y0 + 26, WOOD[0])
        r.outline(panel)
        plate = r.mask(x0 + 14, y0 + 2, x0 + 34, y0 + 9)
        r.img[plate] = BRASS[2]
        r.rect(x0 + 14, y0 + 2, x0 + 34, y0 + 3, BRASS[3])
        r.rect(x0 + 14, y0 + 8, x0 + 34, y0 + 9, BRASS[0])
        r.outline(plate)
        env_i = r.mask(x0 + 20, y0 + 4, x0 + 28, y0 + 8)           # an envelope icon: a letter with its flap
        r.img[env_i] = STONE[3]
        r.outline(env_i, INK[1])
        shp.line(r, x0 + 21, y0 + 4, x0 + 23, y0 + 6, INK[2])
        shp.line(r, x0 + 26, y0 + 4, x0 + 24, y0 + 6, INK[2])
        cork = r.mask(x0 + 2, y0 + 11, x0 + 46, y0 + 24)
        r.img[cork] = STONE[2]
        r.rect(x0 + 2, y0 + 11, x0 + 46, y0 + 12, STONE[1])
        r.outline(cork, WOOD[0])
        for cx in MEDAL_CX:                               # empty medal slots: a ring and a hook
            ring = r.disc(x0 + cx, y0 + 19, 2.6)
            r.img[r.edge(ring)] = STONE[1]
            r.img[y0 + 13, x0 + cx] = INK[2]
        for lx in (x0 + 5, x0 + 39):                      # legs
            r.rect(lx, y0 + 26, lx + 4, y0 + 30, WOOD[0])
            r.rect(lx, y0 + 26, lx + 1, y0 + 30, WOOD[1])
    for i in range(medals):
        cx = x0 + MEDAL_CX[i]
        rb = MEDAL_RIBBONS[i]
        r.rect(cx - 1, y0 + 13, cx + 1, y0 + 17, rb)
        r.rect(cx - 1, y0 + 13, cx, y0 + 17, rb)
        disc = r.disc(cx, y0 + 19.5, 2.9)
        r.img[disc] = BRASS[2]
        r.img[disc & (r.x < cx) & (r.y < y0 + 19.5)] = BRASS[3]
        r.img[r.edge(disc)] = INK[0]
        r.img[y0 + 19, cx] = BRASS[0]


def mail_pieces():
    x0, y0 = X0, Y0
    box = (x0, y0, x0 + MB_W, y0 + MB_H + 3)
    fp = (x0, y0 + 14)
    out = [mk("mail_board", lambda r: mail_board(r, x0, y0), box, fp, (3, 1), ["111"], "rear_prop", "prop", y_sort=True,
              note="free-standing mailroom board on two legs: a brass MAIL plate over a cork strip with six empty medal slots "
                   "(Mira's route medals). State set mail_medals draws it plus 0 to 6 medals",
              tags=["mailroom", "board", "medals"])]
    for k in range(1, 7):
        out.append(mk(f"mail_medals_{k}", lambda r, k=k: mail_board(r, x0, y0, k, medals_only=True), box, fp, (3, 1), ["000"],
                      "rear_prop", "prop", shadow=False, y_sort=True,
                      note=f"overlay with the first {k} medal(s) hung on mail_board, drawn over it; same origin and size as the board. "
                           "Ribbons follow Mira's patch colours (peach, lime, warm wood, ink, pale brass, glass)",
                      tags=["mailroom", "medals", f"{k}"]))
    return out


def mail_tray(r, x0, y0):
    r.cast(x0, x0 + 12, y0 + 9, rows=1)
    tray = r.mask(x0, y0 + 3, x0 + 12, y0 + 9)
    r.img[tray] = GLASS[1]
    r.rect(x0, y0 + 3, x0 + 12, y0 + 4, GLASS[3])
    r.rect(x0, y0 + 8, x0 + 12, y0 + 9, GLASS[0])
    r.outline(tray)
    for (ex, ey, c) in ((1, 0, STONE[3]), (4, 1, STONE[3]), (7, 0, STONE[2])):    # envelopes in the tray
        env_m = r.mask(x0 + ex, y0 + ey, x0 + ex + 5, y0 + ey + 5)
        r.img[env_m] = c
        r.outline(env_m, INK[1])
        r.rect(x0 + ex + 1, y0 + ey + 1, x0 + ex + 4, y0 + ey + 2, INK[3])
    r.rect(x0 + 6, y0 + 2, x0 + 7, y0 + 3, CORAL[2])                               # a coral stamp corner


def desk_folder(r, x0, y0):
    r.cast(x0 + 1, x0 + 12, y0 + 9, rows=1)
    back = r.mask(x0 + 1, y0 + 1, x0 + 12, y0 + 9)
    r.img[back] = WOOD[2]
    r.rect(x0 + 1, y0, x0 + 6, y0 + 2, WOOD[2])                                    # the tab
    r.outline(r.mask(x0 + 1, y0, x0 + 6, y0 + 2) | back, INK[0])
    r.rect(x0 + 2, y0 + 2, x0 + 11, y0 + 4, STONE[3])                              # papers peeking out
    r.rect(x0, y0 + 4, x0 + 11, y0 + 9, WOOD[3])                                   # front flap, lit
    r.rect(x0, y0 + 4, x0 + 11, y0 + 5, BRASS[3])
    r.rect(x0, y0 + 8, x0 + 11, y0 + 9, WOOD[1])
    r.outline(r.mask(x0, y0 + 4, x0 + 11, y0 + 9))
    r.rect(x0 + 4, y0 + 6, x0 + 8, y0 + 7, INK[1])                                 # label


def small_pieces():
    x0, y0 = X0, Y0
    return [
        mk("mail_tray", lambda r: mail_tray(r, x0, y0), (x0, y0, x0 + 14, y0 + 10), (x0, y0), (1, 1), ["0"], "front_prop", "prop",
           note="First Delivery reward for the player's desk: a glass letter tray with three envelopes. 12 x 10 px, no collision",
           tags=["mail", "reward", "desk prop"]),
        mk("desk_folder", lambda r: desk_folder(r, x0, y0), (x0, y0, x0 + 14, y0 + 10), (x0, y0), (1, 1), ["0"], "front_prop", "prop",
           note="Archive Loop reward: a manila folder with a tab, papers peeking out and a label. 12 x 10 px, no collision",
           tags=["folder", "reward", "desk prop"]),
    ]


# ------------------------------------------------------------------ lamp_warm, route stripe

def route_stripe_piece():
    sp = np.zeros((3, 16, 4), np.uint8)
    sp[0, :, :3] = BRASS[3]
    sp[1, :, :3] = BRASS[2]
    sp[2, :, :3] = BRASS[3]
    sp[:, :, 3] = 255
    return _ok().Piece("route_stripe_lit", sp, (0, 0), (0, 1), (1, 1), ["0"], "floor_marking", "tile",
                       note="lit corridor stripe: a 3 px brass band (mid tone core, pale edges) that replaces the 1 px route_inlay "
                            "line in the same row. Place at the route_inlay's cell with a y offset of 1 less, or use state set "
                            "corridor_stripe",
                       tags=["floor", "route", "lit", "level 04"])


def warm_lamp_pieces(by):
    """lamp_warm family: the approved lamp recoloured one step warmer (peach head, amber glow). The off state is lamp_off."""
    ok = _ok()
    out = []
    swaps = {"lamp": [(BRASS[2], WOOD[3]), (BRASS[3], CORAL[3])],
             "lamp_glow_on": [(BRASS[3], WOOD[3])], "lamp_glow_pulse": [(BRASS[3], WOOD[3])]}
    for src, nm, note in (("lamp", "lamp_warm", "warm lamp for the right desk: the approved lamp with an amber head and a peach lit step"),
                          ("lamp_glow_on", "lamp_warm_glow_on", "warm glow, one hard amber step (radius 5.2); paints only on lit stone"),
                          ("lamp_glow_pulse", "lamp_warm_glow_pulse", "warm pulse glow, radius 6.4")):
        p = by[src]
        sp = p.sprite.copy()
        rgb = sp[:, :, :3]
        for a, b in swaps[src]:
            m = np.all(rgb == a, axis=2) & (sp[:, :, 3] > 0)
            rgb[m] = b
        q = ok.Piece(nm, sp, p.tl, p.fp_room, p.fp_cells, p.collision, p.layer, p.kind, y_sort=p.y_sort, composite=p.composite,
                     shadow=p.shadow, note=note, tags=["lamp", "warm"] + [t for t in p.tags if t in ("glow", "on", "pulse")])
        out.append(q)
    return out


# ------------------------------------------------------------------ assembly

def build(by):
    """Return (pieces, animations). `by` maps the names of the existing pieces (for the warm lamp)."""
    pieces = []
    pieces += elevator_pieces()
    pieces += turnstile_pieces()
    pieces += clock_pieces()
    pieces += conference_pieces()
    pieces.append(form_piece())
    pieces += stamp_pieces()
    pieces += pinboard_pieces()
    pieces += desk_pieces()
    pieces += desk_front_pieces()
    pieces += table_pieces()
    pieces += mail_pieces()
    pieces += small_pieces()
    pieces.append(route_stripe_piece())
    pieces += warm_lamp_pieces(by)
    for k in shp.ARTIFACT_KINDS[:4]:
        nm = f"artifact_{k}"
        pieces.append(mk(nm, lambda r, k=k: shp.artifact_prop(r, X0, Y0, PAL, k), (X0, Y0, X0 + 16, Y0 + 16), (X0, Y0), (1, 1), ["0"],
                         "front_prop", "prop", note=ARTIFACT_NOTES[k] + ". 16 x 16 px with a baked contact shadow and a small pale-blue "
                         "glint at the upper left (glass step 3) as the inspectable cue. No collision: lay it on a desk, a table or a "
                         "blocked cell", tags=["artifact", "inspectable", k]))
    anims = {
        "elevator": {"kind": "state_set", "default": "closed",
                     "states": {"closed": {"entries": ["elevator_closed"], "blocked": True},
                                "half": {"entries": ["elevator_half"], "blocked": True},
                                "open": {"entries": ["elevator_open"], "blocked": False}},
                     "play": ["closed", "half", "open"], "ms_per_frame": 120,
                     "note": "play forward on approach or arrival, backward on leave; only open lets the centre cell through"},
        "turnstile": {"kind": "state_set", "default": "closed",
                      "states": {"closed": {"entries": ["turnstile_closed"], "blocked": True},
                                 "open": {"entries": ["turnstile_open", "turnstile_lane_lit"], "blocked": False}},
                      "note": "level 01 opens it: flaps, pedestal lights and the lane inlay change together (Ivo's wave to a nod is level data)"},
        "clock_twin": {"kind": "state_set", "default": "unsynced",
                       "states": {"unsynced": {"entries": ["clock_twin_unsynced"]}, "synced": {"entries": ["clock_twin_synced"]}},
                       "note": "level 03: the right face's hands move to match the left and the status lamp lights; the conference_door swaps with it"},
        "conference_door": {"kind": "state_set", "default": "closed",
                            "states": {"closed": {"entries": ["conference_glass_door_closed"], "blocked": True},
                                       "half": {"entries": ["conference_glass_door_half"], "blocked": True},
                                       "open": {"entries": ["conference_glass_door_open"], "blocked": False}},
                            "play": ["closed", "half", "open"], "ms_per_frame": 120,
                            "note": "level 03 slides it aside as the clock synchronizes; same frame timing as the Records door"},
        "pinboard": {"kind": "state_set", "default": "empty",
                     "states": {"empty": {"entries": ["pinboard_empty"]}, "before": {"entries": ["pinboard_before"]},
                                "after": {"entries": ["pinboard_after"]}},
                     "note": "empty before level 04; before = orderly and symmetrical after level 04; after = asymmetrical and human after level 05"},
        "mail_medals": {"kind": "state_set", "default": "0",
                        "states": {"0": {"entries": ["mail_board"]},
                                   **{str(k): {"entries": ["mail_board", f"mail_medals_{k}"]} for k in range(1, 7)}},
                        "note": "state k hangs Mira's first k route medals (one per clean baseline); entries are drawn in order at one placement point"},
        "lamp_warm": {"kind": "state_set", "default": "on",
                      "states": {"off": {"entries": ["lamp_off"]}, "on": {"entries": ["lamp_warm", "lamp_warm_glow_on"]},
                                 "pulse": {"entries": ["lamp_warm", "lamp_warm_glow_pulse"]}},
                      "loop": ["on", "pulse"], "ms_per_frame": 600,
                      "note": "the right desk's warmer lamp: same states as lamp (off, on, pulse), amber instead of brass"},
        "corridor_stripe": {"kind": "state_set", "default": "unlit",
                            "states": {"unlit": {"entries": ["route_inlay"]}, "lit": {"entries": ["route_stripe_lit"]}},
                            "note": "level 04: the corridor stripe beside the left desk lights as the lamp (state set lamp, off to on) wakes; "
                                    "place the stripe in the route_inlay's row (route_stripe_lit's origin is already 1 px up)"},
    }
    return pieces, anims


ARTIFACT_NOTES = {
    "unissued_badge": "Unissued badge (level 02): a staff badge with a warm department band that differs from today's sign, a photo "
                      "block and a blank name bar",
    "training_card": "Training card, first printing (level 04): a card with three short steps, shorter than Pace's script",
    "mirror_card": "Mirror card (level 05): a card with a reversed R and a handwritten arrow for the right-hand route",
    "first_route_receipt": "First route receipt (level 06): a torn receipt with a looping detour line and an approved tick",
}
