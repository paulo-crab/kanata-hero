"""Proofs for the Orientation quest props, all drawn from orientation-atlas.json and the shared builders.

Called by build_kit.py after the atlas is written. Outputs (this folder):
  orientation-quest-reference-room.json       26 x 15 cell layout (416 x 240 px, the 427 x 240 view at x3) with every P0 prop
  orientation-quest-room-before-native.png / -1366x768.png   start state: elevator open, doors shut, board empty, lamps off
  orientation-quest-room-after-native.png  / -1366x768.png   Orientation done: turnstile open, clock synced, board changed
  orientation-quest-states.png                every state of every state set at x4, with changed-pixel counts
  orientation-seated-fit.png                  desk_a_front over a stand-in worker, with the rows it covers
  orientation-shared-builders-proof.png       the wave-2 builders (elevator, desk occluder, 14 artifacts) in the Records palette
The checks that fail the build live in verify(): palette, silhouettes, symmetry, seated coverage, route reachability.
"""
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for sub in ("gate1", "scale-test", "palettes"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import build_scale_test as bst  # noqa: E402
import district_palettes as dp  # noqa: E402
import environment as env  # noqa: E402
import kitlib  # noqa: E402
import orientation_kit as ok  # noqa: E402
import shared_pieces as shp  # noqa: E402

T = 16
CW, CH = 26, 15
BG = "#151C2B"
BACK = {"floor", "rear_wall", "floor_marking", "rear_prop", "shadow"}
FRONT = {"front_prop", "light"}
CAST = os.path.join(HERE, "..", "cast")
GATE1 = os.path.join(HERE, "..", "gate1")

STATES_BEFORE = {"elevator": "open", "turnstile": "closed", "clock_twin": "unsynced", "conference_door": "closed",
                 "pinboard": "empty", "mail_medals": "0", "lamp": "off", "lamp_warm": "off", "corridor_stripe": "unlit",
                 "garden": "before", "records_door": "closed"}
STATES_AFTER = {"elevator": "closed", "turnstile": "open", "clock_twin": "synced", "conference_door": "open",
                "pinboard": "after", "mail_medals": "3", "lamp": "on", "lamp_warm": "on", "corridor_stripe": "lit",
                "garden": "after", "records_door": "closed"}


# ------------------------------------------------------------------ layout

def at(x, y):
    d = {"cell": [x // T, y // T]}
    if (x % T, y % T) != (0, 0):
        d["offset"] = [x % T, y % T]
    return d


def layout():
    pl = []

    def E(name, x, y):
        pl.append({"entry": name, **at(x, y)})

    def A(name, x, y):
        pl.append({"anim": name, **at(x, y)})

    # north wall; the conference door replaces three columns
    for c in range(CW):
        if c not in (7, 8, 9):
            E("wall_n_plain", c * T, 0)
    for nm, x in (("wall_n_window_a", 248), ("wall_n_window_b", 280), ("wall_n_window_a", 330), ("wall_n_window_b", 362)):
        E(nm, x, 9)
    A("pinboard", 16, 9)
    A("clock_twin", 78, 9)
    A("conference_door", 112, 0)
    E("projected_form_wall", 168, 9)
    # west lift core: a short wall band with the elevator in it and the call panel beside it. The arrival lobby
    # below it is closed by glass partitions, and the reception turnstile is its only way out
    for c in (0, 4, 5, 6, 7):
        E("wall_n_plain", c * T, 128)
    A("elevator", 16, 128)
    E("elevator_call_panel", 68, 137)
    E("partition_1x1", 128, 160)
    E("partition_1x1", 128, 176)
    E("partition_2x1", 0, 192)
    E("partition_2x1", 32, 192)
    E("partition_2x1", 112, 192)
    A("turnstile", 64, 192)
    # left desk (level 04): cherry desk, four stamps, chair, floor lamp, corridor stripe
    E("desk_left_cherry", 24, 48)
    for i, k in enumerate("abcd"):
        E(f"stamp_{k}", 24 + 2 + 8 * i, 48 + 1)
    E("chair", 35, 66)
    A("lamp", 62, 52)
    for x in range(80, 144, T):
        A("corridor_stripe", x, 76)
    # garden landmark
    pl.append({"landmark": "garden", **at(168, 102)})
    # right desk (level 05)
    E("desk_right_mirror", 332, 104)
    for i, k in enumerate("efgh"):
        E(f"stamp_{k}", 332 + 2 + 8 * i, 104 + 1)
    E("chair", 343, 122)
    A("lamp_warm", 320, 106)
    # review table (level 06) with the two keyboards and two chairs
    E("review_table", 184, 196)
    E("keyboard_macbook", 187, 197)
    E("keyboard_spare", 206, 198)
    E("chair", 189, 214)
    E("chair", 215, 214)
    # the player's desk: First Delivery tray and Archive Loop folder
    E("desk_a", 24, 92)
    E("chair", 35, 110)
    E("mail_tray", 46, 92)
    E("desk_folder", 28, 94)
    # a seated background worker at a desk_b: the chair sits behind the desk (SEAT_CHAIR), the worker's feet anchor is
    # SEAT_ANCHOR from the desk origin, and desk_b_front is drawn after the actors to hide the lower body
    E("desk_b", 264, 56)
    E("chair", 264 + SEAT_CHAIR[0], 56 + SEAT_CHAIR[1])
    E("desk_b_front", 264, 56)
    # mailroom: counter and medal board
    A("mail_medals", 344, 146)
    # artifacts lie on a side table, the left desk's floor, and the review table
    E("side_table", 300, 76)
    E("artifact_unissued_badge", 294, 68)
    E("artifact_training_card", 62, 80)
    E("artifact_mirror_card", 366, 94)
    E("artifact_first_route_receipt", 236, 196)
    # plants frame the room's edges
    for nm, x, y in (("pot_plant_a", 4, 30), ("pot_plant_b", 94, 30), ("pot_plant_c", 232, 30), ("pot_plant_d", 396, 30),
                     ("pot_plant_e", 150, 120), ("pot_plant_f", 290, 118), ("pot_plant_g", 150, 214), ("pot_plant_h", 4, 120),
                     ("pot_plant_i", 380, 150), ("pot_plant_j", 262, 214)):
        E(nm, x, y + 4)
    E("sofa", 280, 190)
    E("mail_counter", 340, 192)
    return {
        "kit": "orientation", "atlas": "orientation-atlas.json", "tile": T, "size_cells": [CW, CH],
        "note": "Proof room for the Orientation quest props (26 x 15 cells = 416 x 240 px, the optional 427 x 240 view at x3). "
                "Every named quest prop is placed once; states are the start of the game (before) or the end of Orientation (after).",
        "states": dict(STATES_BEFORE),
        "floor": {"legend": {"J": "floor_j", "H": "floor_h", "V": "floor_v", "P": "floor_p"}, "rows": floor_rows()},
        "placements": pl,
    }


def floor_rows():
    rows = []
    for cy in range(CH):
        row = ""
        for cx in range(CW):
            hj = cy % 2 == 0
            vj = (cx % 2 == 0) if (cy // 2) % 2 == 0 else (cx % 2 == 1)
            row += "J" if hj and vj else "H" if hj else "V" if vj else "P"
        rows.append(row)
    return rows


# ------------------------------------------------------------------ actors

def person(path, col=0, row=0):
    im = np.array(Image.open(path).convert("RGBA"))
    return im[row * 24:(row + 1) * 24, col * 16:(col + 1) * 16]


class Canvas:
    def __init__(self, img):
        self.img = img


def place(canvas, sprite, ax, ay, shadow=True):
    h, w = sprite.shape[:2]
    if shadow:
        canvas[ay - 1, ax - 6:ax + 6] = bst.hx("#535971")
        canvas[ay - 1, ax - 4:ax + 4] = bst.hx("#343650")
    x0, y0 = ax - w // 2, ay - h
    a = sprite[:, :, 3] > 0
    reg = canvas[y0:y0 + h, x0:x0 + w]
    reg[a] = sprite[:, :, :3][a]


ACTORS = [("gate1/engineer-atlas.png", 30, 180), ("cast/ivo-atlas.png", 96, 226), ("cast/mira-atlas.png", 334, 224),
          ("cast/bgworker_b-atlas.png", 264 + 16, 56 + 4)]


def render(lay, atlas, actors=True):
    back = kitlib.render_layout(lay, atlas, layers=BACK)
    if actors:
        for p, x, y in ACTORS:
            place(back, person(os.path.join(HERE, "..", p)), x, y)
    kitlib.render_layout(lay, atlas, layers=FRONT, base=back)
    return back


def screen(native, zoom=3):
    h, w = native.shape[:2]
    scr = Image.new("RGB", (1366, 768), BG)
    im = Image.fromarray(native).resize((w * zoom, h * zoom), Image.NEAREST)
    scr.paste(im, ((1366 - im.width) // 2, (768 - im.height) // 2))
    return scr


# ------------------------------------------------------------------ route check

def reachable(lay, atlas, start, goals):
    grid = kitlib.collision_grid(lay, atlas)
    ch, cw = grid.shape
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < cw and 0 <= ny < ch and (nx, ny) not in seen and not grid[ny, nx]:
                seen.add((nx, ny))
                q.append((nx, ny))
    return {name: cell in seen for name, cell in goals.items()}, grid


# ------------------------------------------------------------------ state strip

def mini(atlas, anim, state, cells, items, extra=()):
    """Render one frame of a state set on a small floor: items = placements around it (walls)."""
    cw, ch = cells
    rows = [("P" * cw) for _ in range(ch)]
    lay = {"size_cells": [cw, ch], "states": {}, "floor": {"legend": {"P": "floor_p"}, "rows": rows}, "placements": []}
    for e in items:
        lay["placements"].append(e)
    lay["placements"].append({"anim": anim, "state": state, **at(*extra)})
    return kitlib.render_layout(lay, atlas)


def walls(n, y=0):
    return [{"entry": "wall_n_plain", **at(c * T, y)} for c in range(n)]


STRIP_RECIPES = {  # anim: (cells, extra px position of the anim, background placements)
    "elevator": ((5, 3), (16, 0), [{"entry": "wall_n_plain", **at(0, 0)}, {"entry": "wall_n_plain", **at(64, 0)}]),
    "conference_door": ((5, 3), (16, 0), [{"entry": "wall_n_plain", **at(0, 0)}, {"entry": "wall_n_plain", **at(64, 0)}]),
    "turnstile": ((5, 3), (16, 16), []),
    "clock_twin": ((3, 2), (9, 9), walls(3)),
    "pinboard": ((4, 2), (8, 9), walls(4)),
    "mail_medals": ((5, 3), (16, 16), []),
    "lamp_warm": ((3, 3), (16, 16), []),
    "lamp": ((3, 3), (16, 16), []),
    "corridor_stripe": ((3, 1), (0, 7), []),
}
REGION_OF = {"corridor_stripe": [(0, 7), (16, 7), (32, 7)]}


def changed_regions(a, b):
    """(changed px, separate visible regions: connected after a 1 px dilation) between two renders."""
    m = np.any(a != b, axis=2)
    n = int(m.sum())
    if not n:
        return 0, 0
    d = m.copy()
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            d |= np.roll(np.roll(m, dx, 1), dy, 0)
    lab = np.zeros(d.shape, int)
    k = 0
    for y, x in zip(*np.nonzero(d)):
        if lab[y, x]:
            continue
        k += 1
        stack = [(y, x)]
        lab[y, x] = k
        while stack:
            cy, cx = stack.pop()
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < d.shape[0] and 0 <= nx < d.shape[1] and d[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = k
                    stack.append((ny, nx))
    return n, k


def render_state(atlas, anim, st):
    cells, pos, bgp = STRIP_RECIPES.get(anim, ((3, 3), (16, 16), []))
    if anim == "corridor_stripe":
        lay = {"size_cells": [3, 1], "states": {}, "floor": {"legend": {"P": "floor_p"}, "rows": ["PPP"]},
               "placements": [{"anim": anim, "state": st, **at(x, 7)} for x in (0, 16, 32)]}
        return kitlib.render_layout(lay, atlas)
    return mini(atlas, anim, st, cells, bgp, pos)


# What each level's quest swaps (levels.md "Art and state"): the state sets that change together. A swap must
# change at least two separate visible regions across them. NPC poses (Ivo, Noor) are level data, not counted.
LEVEL_SWAPS = {
    "01 turnstile opens": [("turnstile", "closed", "open")],
    "03 clock syncs, glass door slides": [("clock_twin", "unsynced", "synced"), ("conference_door", "closed", "open")],
    "04 sheets join the board, lamp and stripe light": [("pinboard", "empty", "before"), ("lamp", "off", "on"),
                                                         ("corridor_stripe", "unlit", "lit")],
    "05 board turns human, warm lamp wakes": [("pinboard", "before", "after"), ("lamp_warm", "off", "on")],
}


def level_swaps(atlas):
    out = {}
    for lvl, swaps in LEVEL_SWAPS.items():
        total, parts = 0, []
        for anim, s0, s1 in swaps:
            n, k = changed_regions(render_state(atlas, anim, s0), render_state(atlas, anim, s1))
            total += k
            parts.append(f"{anim} {s0}->{s1}: {n} px, {k} region(s)")
        out[lvl] = (total, parts)
    return out


def states_sheet(atlas):
    Z = 4
    order = ["elevator", "turnstile", "clock_twin", "conference_door", "pinboard", "mail_medals", "lamp", "lamp_warm", "corridor_stripe"]
    f_h, f_s = bst.font(20, bold=True), bst.font(14)
    rows, report = [], {}
    for anim in order:
        a = atlas.animations[anim]
        frames = [(st, render_state(atlas, anim, st)) for st in a["states"]]
        names = [s for s, _ in frames]
        diffs = {f"{names[i]} to {names[i + 1]}": changed_regions(frames[i][1], frames[i + 1][1]) for i in range(len(frames) - 1)}
        report[anim] = diffs
        rows.append((anim, frames, diffs))
    # lay out: each state set is a row
    pad, lab_h = 16, 54
    W = max(sum(f.shape[1] * Z + pad for _, f in fr) for _, fr, _ in rows) + pad
    H = sum(max(f.shape[0] for _, f in fr) * Z + lab_h + 10 for _, fr, _ in rows) + 400
    sheet = Image.new("RGB", (max(W, 1300), H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 16), "Orientation quest state sets at x4. Under each frame: state name; between frames: changed px and visible regions.",
           font=f_h, fill="#F4F2EC")
    y = 60
    for anim, frames, diffs in rows:
        d.text((pad, y), f"state set: {anim}", font=f_h, fill="#E6B750" if False else "#F4F2EC")
        y += 28
        x = pad
        h = max(f.shape[0] for _, f in frames) * Z
        for i, (st, f) in enumerate(frames):
            im = Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST)
            sheet.paste(im, (x, y))
            d.text((x, y + h + 2), f"{st}", font=f_s, fill="#C5CED0")
            if i < len(frames) - 1:
                n, k = list(diffs.values())[i]
                d.text((x, y + h + 18), f"to next: {n} px, {k} region(s)", font=f_s, fill="#9FB3BD")
            x += im.width + pad
        y += h + lab_h
    sheet = sheet.crop((0, 0, sheet.width, y + 10))
    sheet.save(os.path.join(HERE, "orientation-quest-states.png"))
    return report


# ------------------------------------------------------------------ seated fit

SEAT_ANCHOR = (16, 4)       # worker feet_bc relative to the desk origin
SEAT_CHAIR = (8, -12)       # chair footprint origin relative to the desk origin


def seated_fit(atlas):
    """Desk with chair at the seat convention, a stand-in worker, and the occluder over them. Returns coverage rows."""
    X, Y = 24, 40
    W_, H_ = 64, 64
    work = person(os.path.join(GATE1, "engineer-atlas.png"))
    lay_back = {"size_cells": [4, 4], "states": {}, "floor": {"legend": {"P": "floor_p"}, "rows": ["PPPP"] * 4},
                "placements": [{"entry": "desk_a", **at(X, Y)}, {"entry": "chair", **at(X + SEAT_CHAIR[0], Y + SEAT_CHAIR[1])}]}
    front = {"size_cells": [4, 4], "states": {}, "floor": {"legend": {"P": "floor_p"}, "rows": ["PPPP"] * 4},
             "placements": [{"entry": "desk_a_front", **at(X, Y)}]}
    ax, ay = X + SEAT_ANCHOR[0], Y + SEAT_ANCHOR[1]
    frames = []
    for with_front in (False, True):
        img = kitlib.render_layout(lay_back, atlas, layers=BACK)
        place(img, work, ax, ay, shadow=False)
        if with_front:
            kitlib.render_layout(front, atlas, layers={"front_prop"}, base=img)
        frames.append(img)
    # coverage of the 16 x 24 frame by the occluder (drawn alone)
    occ = kitlib.render_layout({**front, "floor": {"legend": {"P": "floor_p"}, "rows": ["PPPP"] * 4}}, atlas, layers={"front_prop"},
                               base=np.zeros((64, 64, 3), np.uint8) + np.array([255, 0, 255], np.uint8))
    mask = np.any(occ != np.array([255, 0, 255], np.uint8), axis=2)
    fx0, fy0 = ax - 8, ay - 24
    cov = mask[fy0:fy0 + 24, fx0:fx0 + 16]
    Z = 8
    sheet = Image.new("RGB", (3 * (W_ * Z + 20) + 20, H_ * Z + 90), BG)
    d = ImageDraw.Draw(sheet)
    f = bst.font(18, bold=True)
    titles = ["desk_a, chair and a worker, no occluder", "with desk_a_front: rows 16-23 hidden", "occluder coverage of the 16x24 frame"]
    cov_img = np.zeros((H_, W_, 3), np.uint8)
    cov_img[:] = bst.hx("#2B3043")
    for yy in range(24):
        for xx in range(16):
            cov_img[fy0 + yy, fx0 + xx] = bst.hx("#E67A70") if False else (bst.hx("#A0DDD4") if cov[yy, xx] else bst.hx("#535971"))
    for i, (t, im) in enumerate(zip(titles, (frames[0], frames[1], cov_img))):
        x = 20 + i * (W_ * Z + 20)
        sheet.paste(Image.fromarray(im).resize((W_ * Z, H_ * Z), Image.NEAREST), (x, 60))
        d.text((x, 20), t, font=f, fill="#F4F2EC")
    sheet.save(os.path.join(HERE, "orientation-seated-fit.png"))
    rows = ["".join("#" if cov[y, x] else "." for x in range(16)) for y in range(24)]
    return rows, frames


# ------------------------------------------------------------------ shared builders proof (Records palette)

def shared_proof():
    REC = shp.Pal("records")
    Z = 6
    X, Y = 64, 16
    panels = []

    def cap(fn, box):
        rgba, _ = kitlib.capture(fn, env.Room)
        x0, y0, x1, y1 = box
        sp = rgba[y0:y1, x0:x1]
        out = np.zeros((y1 - y0, x1 - x0, 3), np.uint8)
        out[:] = bst.hx(REC.floor[3] if False else dp.DISTRICTS["records"]["floor"][3])
        a = sp[:, :, 3] > 0
        out[a] = sp[:, :, :3][a]
        return out
    for t in (0.0, 0.5, 1.0):
        panels.append((f"elevator t={t}", cap(lambda r, t=t: shp.elevator_doors(r, X, Y, REC, t), (X, Y, X + 48, Y + 48))))
    panels.append(("call panel", cap(lambda r: shp.elevator_call_panel(r, X, Y, REC), (X, Y, X + 12, Y + 22))))
    rec_floor = bst.hx(dp.DISTRICTS["records"]["floor"][3])
    # desk with occluder and a stand-in worker, Records palette
    DX, DY = 24, 40
    img = np.zeros((56, 64, 3), np.uint8)
    img[:] = rec_floor
    def draw_all(front):
        r = env.Room()
        r.img[:] = rec_floor
        shp.desk_a(r, DX, DY, REC, 7)
        work = person(os.path.join(GATE1, "engineer-atlas.png"))
        place(r.img, work, DX + SEAT_ANCHOR[0], DY + SEAT_ANCHOR[1], shadow=False)
        if front:
            shp.desk_front(r, DX, DY, REC, 7)
        return r.img[:64, :64].copy()
    panels.append(("Records desk, no occluder", draw_all(False)))
    panels.append(("Records desk + desk_front", draw_all(True)))
    # 14 artifacts
    arts = []
    for k in shp.ARTIFACT_KINDS:
        arts.append((k, cap(lambda r, k=k: shp.artifact_prop(r, X, Y, REC, k), (X, Y, X + 16, Y + 16))))
    f = bst.font(15, bold=True)
    fs = bst.font(12)
    W = 1600
    sheet = Image.new("RGB", (W, 2000), BG)
    d = ImageDraw.Draw(sheet)
    d.text((16, 12), "Shared builders in the Records palette (wave 2 proof). Row 1: elevator door set, call panel, desk occluder. "
           "Row 2: all 14 artifacts (the first four are in the Orientation atlas; the other ten are proof only).", font=f, fill="#F4F2EC")
    x = y = 50
    rowh = 0
    for lab, im in panels:
        pim = Image.fromarray(im).resize((im.shape[1] * Z, im.shape[0] * Z), Image.NEAREST)
        if x + pim.width > W:
            x, y = 16, y + rowh + 40
            rowh = 0
        sheet.paste(pim, (x, y))
        d.text((x, y + pim.height + 4), lab, font=fs, fill="#C5CED0")
        x += pim.width + 18
        rowh = max(rowh, pim.height)
    x, y = 16, y + rowh + 50
    rowh = 0
    for lab, im in arts:
        pim = Image.fromarray(im).resize((im.shape[1] * 8, im.shape[0] * 8), Image.NEAREST)
        if x + pim.width > W:
            x, y = 16, y + rowh + 40
            rowh = 0
        sheet.paste(pim, (x, y))
        d.text((x, y + pim.height + 4), lab, font=fs, fill="#C5CED0")
        x += pim.width + 18
        rowh = max(rowh, pim.height)
    sheet = sheet.crop((0, 0, W, y + rowh + 40))
    sheet.save(os.path.join(HERE, "orientation-shared-builders-proof.png"))


# ------------------------------------------------------------------ verification

QUEST_NAMES = None


def allowed_palette():
    D = dp.DISTRICTS["orientation"]
    hexes = set()
    for role in ("ink", "floor", "glass", "wood", "foliage", "accent"):
        hexes |= {h.upper() for h in D[role]}
    hexes |= {h.upper() for h in dp.ORIENTATION_EXTRA["coral"]}
    return hexes


def verify(atlas, lay_before, lay_after, report, cov_rows):
    errs = []
    new = [e for e in atlas.meta["entries"] if e["name"] in new_names(atlas)]
    ok_hex = allowed_palette()
    used = set()
    for e in new:
        sp = atlas.sprite(e["name"])
        px = sp[sp[:, :, 3] > 0][:, :3]
        for c in np.unique(px, axis=0):
            h = kitlib.hexs(c)
            used.add(h)
            if h not in ok_hex:
                errs.append(f"{e['name']}: colour {h} is outside the Orientation palette")
    # stamp silhouettes are pairwise distinct
    masks = {}
    for k in "abcdefgh":
        masks[k] = atlas.sprite(f"stamp_{k}")[:, :, 3] > 0
    for a in "abcdefgh":
        for b in "abcdefgh":
            if a < b:
                ma, mb = masks[a], masks[b]
                h, w = max(ma.shape[0], mb.shape[0]), max(ma.shape[1], mb.shape[1])
                A_, B_ = np.zeros((h, w), bool), np.zeros((h, w), bool)
                A_[:ma.shape[0], :ma.shape[1]] = ma
                B_[:mb.shape[0], :mb.shape[1]] = mb
                iou = (A_ & B_).sum() / (A_ | B_).sum()
                if iou > 0.8:
                    errs.append(f"stamp_{a} and stamp_{b} silhouettes overlap {iou:.2f}")
    # pinboard: before is symmetric (sheets and pins), after is not
    def inner(name):
        """Everything on the board that is not bare cork: sheets (with their lines), strips and pins."""
        sp = atlas.sprite(name)[3:21, 2:46, :3]
        cork = [np.all(sp == np.array(c, np.uint8), axis=2) for c in (bst.WOOD[1], bst.WOOD[2], bst.WOOD[3])]
        return ~(cork[0] | cork[1] | cork[2])
    pb = inner("pinboard_before")
    pa = inner("pinboard_after")
    if not np.array_equal(pb, pb[:, ::-1]):
        errs.append("pinboard_before is not mirror symmetric")
    if np.array_equal(pa, pa[:, ::-1]):
        errs.append("pinboard_after is symmetric")
    # quest swaps change at least two visible elements
    for lvl, (total, parts) in level_swaps(atlas).items():
        if total < 2:
            errs.append(f"level swap '{lvl}' changes only {total} visible region(s)")
    # seated fit: rows 16-23 covered at columns 1-14, 20-23 fully
    for y in range(16, 24):
        if cov_rows[y][1:15] != "#" * 14:
            errs.append(f"seat coverage row {y} leaves columns 1-14 open: {cov_rows[y]}")
    for y in range(20, 24):
        if cov_rows[y] != "#" * 16:
            errs.append(f"seat coverage row {y} is not full: {cov_rows[y]}")
    for y in range(0, 15):
        if "#" in cov_rows[y]:
            errs.append(f"seat coverage row {y} hides part of the upper body: {cov_rows[y]}")
    # the occluder is seamless over the desk: desk_a_front pixels equal desk_a's pixels at the same spot
    for desk in ("desk_a", "desk_b"):
        ea, ef = atlas.entries[desk], atlas.entries[desk + "_front"]
        sa, sf = atlas.sprite(desk), atlas.sprite(desk + "_front")
        bad = 0
        for y in range(sf.shape[0]):
            for x in range(sf.shape[1]):
                if sf[y, x, 3]:
                    yy = y - ef["footprint"]["origin_px"][1] + ea["footprint"]["origin_px"][1]
                    xx = x - ef["footprint"]["origin_px"][0] + ea["footprint"]["origin_px"][0]
                    if not (0 <= yy < sa.shape[0] and 0 <= xx < sa.shape[1]) or not np.array_equal(sa[yy, xx], sf[y, x]):
                        bad += 1
        if bad:
            errs.append(f"{desk}_front differs from {desk} at {bad} px")
    # no marker colour (check_atlas also does this), and collision of states
    # reachability on the proof room
    # from the elevator mat: the lobby is reachable in both states, the rest of the room only once the turnstile is open
    far = {"left desk front": (1, 4), "player's desk front": (1, 6), "right desk front": (20, 7), "review table": (12, 13),
           "garden west": (9, 8), "mail counter": (22, 13), "turnstile lane": (5, 12)}
    near = {"lobby": (3, 10), "elevator centre cell": (2, 9)}
    res_b, _ = reachable(lay_before, atlas, (2, 10), {**near, **far})
    res_a, _ = reachable(lay_after, atlas, (2, 10), {**near, **far})
    for g in near:
        if not res_b[g] and g != "elevator centre cell":
            errs.append(f"before: {g} unreachable from the elevator mat")
    if not res_b["elevator centre cell"]:
        pass
    if not res_a["lobby"]:
        errs.append("after: lobby unreachable")
    for g in far:
        if res_b[g]:
            errs.append(f"before: {g} is reachable although the turnstile is closed")
        if not res_a[g]:
            errs.append(f"after: {g} {far[g]} is not reachable from the elevator mat")
    return errs, len(used)


def new_names(atlas):
    names = []
    for e in atlas.meta["entries"]:
        n = e["name"]
        if n.startswith(("elevator_", "turnstile_", "clock_twin_", "conference_glass_door_", "projected_form_wall", "stamp_",
                         "pinboard_", "desk_left_cherry", "desk_right_mirror", "desk_a_front", "desk_b_front", "review_table",
                         "keyboard_", "mail_board", "mail_medals_", "mail_tray", "desk_folder", "route_stripe_lit", "lamp_warm",
                         "artifact_")):
            names.append(n)
    return set(names)


def build():
    atlas = kitlib.Atlas(os.path.join(HERE, "orientation-atlas.json"))
    lay = layout()
    with open(os.path.join(HERE, "orientation-quest-reference-room.json"), "w") as fh:
        json.dump(lay, fh, indent=1)
        fh.write("\n")
    import build_room
    lay_before = build_room.with_states(lay, **STATES_BEFORE)
    lay_after = build_room.with_states(lay, **STATES_AFTER)
    for nm, l in (("before", lay_before), ("after", lay_after)):
        img = render(l, atlas)
        Image.fromarray(img).save(os.path.join(HERE, f"orientation-quest-room-{nm}-native.png"))
        screen(img, 3).save(os.path.join(HERE, f"orientation-quest-room-{nm}-1366x768.png"))
    report = states_sheet(atlas)
    cov_rows, _ = seated_fit(atlas)
    shared_proof()
    errs, ncol = verify(atlas, lay_before, lay_after, report, cov_rows)
    print(f"quest props: {len(new_names(atlas))} new entries, {ncol} distinct colours, all inside the Orientation palette"
          if not any("palette" in e for e in errs) else "palette FAILED")
    for anim, d in report.items():
        print("  " + anim + ": " + "; ".join(f"{k}: {n} px / {r} region(s)" for k, (n, r) in d.items()))
    for lvl, (total, parts) in level_swaps(atlas).items():
        print(f"  level {lvl}: {total} region(s) = " + "; ".join(parts))
    print("seat coverage (16 x 24 frame, # = hidden by desk_a_front):")
    for y, row in enumerate(cov_rows):
        print(f"  row {y:2d} {row}")
    for e in errs:
        print("FAIL", e)
    return errs


if __name__ == "__main__":
    sys.exit(1 if build() else 0)
