"""Build the Records environment kit and its reference room.

Run: python3 build_records.py   (Pillow + numpy; run from anywhere)
Writes into this folder:
  records-atlas.png / .json                  the atlas (check with check_atlas.py)
  records-atlas-sheet.png                    every entry at x4 with footprint, collision, anchor
  records-landmark-states.png                the archive desk before, after and changed pixels at x4
  records-reference-room.json                cell layout built only from the atlas
  records-reference-room-native.png          the room, before state (320x192, Engineer on the route)
  records-reference-room-1366x768.png        the x4 view (320x180), before state, no inset
  records-reference-room-keyboard-inset.png  the same with the keyboard inset rectangle overlaid
  records-reference-room-after-native.png / -after-1366x768.png   landmark after, door and file wall open
  records-reference-room-route.png           collision grid, the BFS route and the inset, for review
Then runs the programmatic review (route BFS on the collision grid, nothing required under the inset,
doorway brighter than its walls) and exits 1 if any check fails.
"""
import json
import os
import random
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_kit  # noqa: E402
import kitlib  # noqa: E402
import rich_finish as rf  # noqa: E402
import records_kit as rk  # noqa: E402
import build_gate1 as g  # noqa: E402
import build_scale_test as bst  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import mira_sprites as mira  # noqa: E402
import check_atlas  # noqa: E402

T = 16
W_CELLS, H_CELLS = 20, 12
BACK = {"floor", "rear_wall", "floor_marking", "rear_prop", "shadow"}
FRONT = {"front_prop", "light"}
STATES_BEFORE = {"archive_door": "closed", "lamp": "on", "archive_desk": "before", "file_wall": "closed"}
STATES_AFTER = {"archive_door": "open", "lamp": "pulse", "archive_desk": "after", "file_wall": "open"}

ENGINEER = (eng.IDLE["n"][0], 176, 146)   # frame, anchor x, anchor y: centre of the 2-cell corridor
INSET_VIEW = (5, 126.5, 125, 175)          # keyboard inset in view px (Gate 1 overlay geometry, /4)


# ------------------------------------------------------------------ layout

def at(x, y):
    d = {"cell": [x // T, y // T]}
    if (x % T, y % T) != (0, 0):
        d["offset"] = [x % T, y % T]
    return d


def reference_layout():
    pl = []

    def entry(name, x, y):
        pl.append({"entry": name, **at(x, y)})

    def anim(name, x, y):
        pl.append({"anim": name, **at(x, y)})

    # floor wear: a few chips away from the route, none on the corridor
    rnd = random.Random(23)
    n = 0
    while n < 18:
        x, y = rnd.randrange(4, 300), rnd.randrange(40, 180)
        if 156 <= x < 296 and 60 <= y < 100 or 156 <= x < 196 and y >= 96:
            continue
        entry("floor_chip", x, y)
        n += 1
    # walls
    for c in range(W_CELLS):
        entry("wall_n_plain", c * T, 0)
    for nm, x in (("wall_n_window_a", 60), ("wall_n_window_b", 100), ("wall_n_window_a", 198), ("wall_n_window_b", 238)):
        entry(nm, x, 9)
    for y in range(34, H_CELLS * T, T):
        if 66 <= y < 112:   # the door entries replace the wall here, so the plain wall's collision must not sit in the doorway
            continue
        entry("wall_e_plain", 288, y)
    anim("archive_door", 288, 72)
    for x, y in ((277, 45), (277, 119)):
        anim("lamp", x, y)
    # route: inlay lines and cherry arrows
    for x in range(160, 288, T):
        entry("route_inlay", x, 64)
    for x in range(192, 288, T):
        entry("route_inlay", x, 95)
    for y in range(96, 192, T):
        entry("route_inlay_v", 160, y)
        entry("route_inlay_v", 191, y)
    for y in (126, 166):
        entry("route_arrow_n", 168, y)
    for x in (216, 256):
        entry("route_arrow_e", x, 72)
    # shelving and cabinets along the north wall, the sliding file wall at the east end
    entry("shelf_2x1_a", 0, 32)
    entry("shelf_1x1", 32, 32)
    entry("cabinet_2x1", 144, 32)
    entry("cabinet_1x1", 176, 32)
    pl.append({"anim": "file_wall", **at(192, 32)})
    for nm, x in (("light_shaft", 198), ("light_shaft", 238)):
        entry(nm, x, 34)
    # the landmark
    pl.append({"landmark": "archive_desk", "cell": [3, 3]})
    # south-east work nook: partitions, a terminal desk and a plain desk
    entry("partition_2x1", 192, 120)
    entry("partition_2x1", 224, 120)
    entry("partition_1x1", 256, 120)
    entry("terminal_desk", 208, 148)
    entry("chair", 208 + 11, 148 + 18)
    entry("desk_a", 256, 148)
    entry("chair", 256 + 11, 148 + 18)
    # planters
    for nm, x, y in (("pot_plant_a", 0, 100), ("pot_plant_b", 146, 52), ("pot_plant_c", 256, 52),
                     ("pot_plant_d", 146, 132), ("pot_plant_c", 48, 36), ("pot_plant_b", 128, 36),
                      ("pot_plant_a", 96, 150), ("pot_plant_d", 18, 146)):
        entry(nm, x, y + 4)
    return {
        "kit": "records", "atlas": "records-atlas.json", "tile": T, "size_cells": [W_CELLS, H_CELLS],
        "note": "Records reference room, built only from records-atlas. Floor is a cell grid; every other element is a placement at "
                "cell + pixel offset of its footprint origin. Draw order = layer order, then list order. The Engineer is added by the "
                "renderer, not the layout. The main route enters at the bottom (cols 10-11), runs north, turns east along rows 4-5 and ends at the door.",
        "states": dict(STATES_BEFORE),
        "floor": {"legend": {"J": "floor_j", "H": "floor_h", "V": "floor_v", "P": "floor_p"}, "rows": ok_floor_rows()},
        "placements": pl,
    }


def ok_floor_rows():
    import orientation_kit as ok
    return ok.floor_rows()[:H_CELLS]


def with_states(layout, **st):
    out = dict(layout)
    out["states"] = dict(layout["states"], **st)
    return out


# ------------------------------------------------------------------ render

def render(layout, atlas, states, engineer=ENGINEER):
    lay = with_states(layout, **states)
    canvas = np.zeros((H_CELLS * T, W_CELLS * T, 3), np.uint8)
    kitlib.render_layout(lay, atlas, layers=BACK, base=canvas)
    if engineer:
        frame, ax, ay = engineer
        c = type("C", (), {})()
        c.img = canvas
        g.place_px(c, g.frame_rgba(frame), ax, ay)
    kitlib.render_layout(lay, atlas, layers=FRONT, base=canvas)
    return canvas


def to_screen(canvas, inset=False):
    native = Image.fromarray(canvas[:180, :320])
    vw, vh = 1280, 720
    scaled = native.resize((vw, vh), Image.NEAREST)
    screen = Image.new("RGB", (1366, 768), "#151C2B")
    vx, vy = (1366 - vw) // 2, (768 - vh) // 2
    screen.paste(scaled, (vx, vy))
    if inset:
        d = ImageDraw.Draw(screen, "RGBA")
        x0, y0, x1, y1 = vx + 20, vy + vh - 214, vx + 500, vy + vh - 20
        d.rounded_rectangle([x0, y0, x1, y1], 14, fill=(24, 43, 56, 242), outline="#19AFA2", width=2)
        d.text((x0 + 22, y0 + 16), "Keyboard inset (bottom-left third)", font=bst.font(22, bold=True), fill="#F4F2EC")
        d.text((x0 + 22, y0 + 56), "Nothing the task needs is drawn under this panel.", font=bst.font(16), fill="#C5CED0")
    return screen


# ------------------------------------------------------------------ programmatic review

def blocked_grid(layout, atlas, states):
    lay = with_states(layout, **states)
    grid = kitlib.collision_grid(lay, atlas)
    # the walls on the outer edge are not in the room: rows 0-1 are the north wall (placements block them)
    return grid


def corridor_route(grid, start, goal):
    """BFS over 2x2 windows (top-left cell) that are all walkable: a corridor two cells wide."""
    h, w = grid.shape

    def ok2(x, y):
        return 0 <= x < w - 1 and 0 <= y < h - 1 and not grid[y:y + 2, x:x + 2].any()
    if not ok2(*start) or not ok2(*goal):
        return None
    prev, q = {start: None}, deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            path = []
            while cur:
                path.append(cur)
                cur = prev[cur]
            return path[::-1]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (cur[0] + dx, cur[1] + dy)
            if nxt not in prev and ok2(*nxt):
                prev[nxt] = cur
                q.append(nxt)
    return None


def luminance(rgb):
    rgb = np.asarray(rgb, float)
    return float((0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]).mean())


def review(layout, atlas):
    results = []

    def check(name, ok_, detail=""):
        results.append((name, ok_, detail))
        print(("PASS " if ok_ else "FAIL ") + name + (f": {detail}" if detail else ""))

    # route, with the door open (it opens on approach)
    grid = blocked_grid(layout, atlas, dict(STATES_BEFORE, archive_door="open"))
    start, goal = (10, 10), (17, 4)
    path = corridor_route(grid, start, goal)
    check("main route is a 2-cell-wide corridor from the entrance to the door (BFS on the collision grid)", path is not None,
          f"{len(path)} steps, {start} -> {goal}" if path else "no path")
    closed = blocked_grid(layout, atlas, STATES_BEFORE)
    check("the closed door blocks the route (the door state drives the collision)", corridor_route(closed, start, goal) is None)
    # the route must be prop-free: every cell of the corridor path is walkable and no prop footprint sits on it
    if path:
        cells = {(x + dx, y + dy) for x, y in path for dx in (0, 1) for dy in (0, 1)}
        check("route cells are free of props", not any(grid[y, x] for x, y in cells), f"{len(cells)} cells")
    # the file wall in its open state leaves a 2-cell corridor
    gate = blocked_grid(layout, atlas, dict(STATES_BEFORE, file_wall="open"))
    check("file wall open leaves two free cells (cols 14-15)", not gate[2, 14] and not gate[2, 15] and gate[2, 13] and gate[2, 16])
    check("file wall closed blocks cols 13-16", all(grid[2, c] for c in (13, 14, 15, 16)))
    # nothing required under the keyboard inset
    ix0, iy0, ix1, iy1 = INSET_VIEW
    required = {"landmark footprint": (48, 48, 128, 112), "landmark ring": (24, 28, 152, 124), "door": (288, 50, 320, 118),
                "terminal desk": (208, 141, 240, 164), "route start": (160, 160, 192, 180), "route corner": (160, 64, 192, 96),
                "file wall": (192, 20, 288, 48)}
    bad = [n for n, (x0, y0, x1, y1) in required.items() if x0 < ix1 and x1 > ix0 and y0 < iy1 and y1 > iy0]
    check("no required element sits under the keyboard inset (view x 5-125, y 126.5-175)", not bad, ", ".join(bad) or "all clear")
    # the doorway is brighter than the walls beside it
    room = render(layout, atlas, dict(STATES_BEFORE, archive_door="open"), engineer=None)
    opening = room[76:108, 292:320]
    wall = np.concatenate([room[120:152, 292:320], room[36:60, 292:320]])
    lo, lw = luminance(opening), luminance(wall)
    check("doorway (open) is brighter than the adjacent east wall", lo > lw * 1.5, f"{lo:.0f} vs {lw:.0f} luma")
    # palette discipline: every opaque atlas pixel is a Records ramp step (ink and violet shared); no violet at all
    import district_palettes as dp
    allowed = {h.upper() for role in ("ink", "floor", "wall", "glass", "wood", "foliage", "accent") for h in dp.DISTRICTS["records"][role]}
    allowed |= {h.upper() for h in dp.FOLIAGE_EXTRA['records'].values()} | {h.upper() for v in dp.RICH_EXTRAS.values() for h in v}  # rich finish: leaf edge and tip, planters
    violet = {h.upper() for h in dp.VIOLET}
    used = {kitlib.hexs(c) for c in np.unique(atlas.img[atlas.img[:, :, 3] > 0][:, :3], axis=0)}
    check("every atlas pixel is a Records ramp step; no violet", used <= allowed and not (used & violet),
          f"{len(used)} colours" + (f", stray {sorted(used - allowed)}" if used - allowed else ""))
    # the landmark's two states differ in at least two visible parts
    lm = atlas.landmarks["archive_desk"]
    diff = set(lm["states"]["before"]["parts"]) ^ set(lm["states"]["after"]["parts"])
    check("landmark after state changes at least two visible things", len(diff) >= 2 and len(lm["states"]["after"]["lamps"]) > 0,
          f"{len(diff)} parts differ, lamps switch")
    return all(r[1] for r in results)


# ------------------------------------------------------------------ images

def landmark_states(layout, atlas):
    box = (16, 24, 160, 132)
    Z = 4
    imgs = {}
    for st in ("before", "after"):
        imgs[st] = render(layout, atlas, dict(STATES_BEFORE, archive_desk=st, lamp="on" if st == "before" else "pulse"), engineer=None)[box[1]:box[3], box[0]:box[2]]
    changed = np.any(imgs["before"] != imgs["after"], axis=2)
    dim = imgs["after"].copy()
    dim[~changed] = (imgs["after"][~changed] * 0.35 + np.array(bst.INK[0]) * 0.65).astype(np.uint8)  # diagnostic only
    panels = [("BEFORE: the Records review not yet complete", imgs["before"]),
              ("AFTER: review complete", imgs["after"]), (f"CHANGED: {int(changed.sum())} px (rest dimmed)", dim)]
    pw, ph = (box[2] - box[0]) * Z, (box[3] - box[1]) * Z
    sheet = Image.new("RGB", (len(panels) * (pw + 20) + 20, ph + 150), build_kit.BG)
    d = ImageDraw.Draw(sheet)
    for i, (title, im) in enumerate(panels):
        x = 20 + i * (pw + 20)
        sheet.paste(Image.fromarray(im).resize((pw, ph), Image.NEAREST), (x, 50))
        d.text((x, 16), title, font=bst.font(20, bold=True), fill="#F4F2EC")
    lm = atlas.landmarks["archive_desk"]
    for i, line in enumerate(lm["changes_after"]):
        d.text((20, ph + 62 + i * 20), "+ " + line[:210], font=bst.font(13), fill="#C5CED0")
    sheet.save(os.path.join(HERE, "records-landmark-states.png"))
    return int(changed.sum())


def route_image(layout, atlas, canvas):
    Z = 4
    grid = blocked_grid(layout, atlas, dict(STATES_BEFORE, archive_door="open"))
    path = corridor_route(grid, (10, 10), (17, 4))
    img = Image.fromarray(canvas).resize((canvas.shape[1] * Z, canvas.shape[0] * Z), Image.NEAREST).convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(grid.shape[0]):
        for x in range(grid.shape[1]):
            box = [x * T * Z, y * T * Z, (x + 1) * T * Z - 1, (y + 1) * T * Z - 1]
            if grid[y, x]:
                d.rectangle(box, fill=(236, 119, 109, 70), outline=(236, 119, 109, 160))
    if path:
        cells = {(x + dx, y + dy) for x, y in path for dx in (0, 1) for dy in (0, 1)}
        for x, y in cells:
            d.rectangle([x * T * Z + 2, y * T * Z + 2, (x + 1) * T * Z - 3, (y + 1) * T * Z - 3], outline=(25, 175, 162, 255), width=3)
    ix0, iy0, ix1, iy1 = [v * Z for v in INSET_VIEW]
    d.rectangle([ix0, iy0, ix1, iy1], outline=(230, 183, 80, 255), width=4)
    d.text((ix0 + 8, iy0 + 8), "keyboard inset", font=bst.font(18, bold=True), fill=(230, 183, 80, 255))
    d.text((8, img.size[1] - 26), "coral cells block, teal cells are the 2-wide route found by BFS (door open), gold is the keyboard inset",
           font=bst.font(14), fill=(244, 242, 236, 255))
    Image.alpha_composite(img, ov).convert("RGB").save(os.path.join(HERE, "records-reference-room-route.png"))


# ------------------------------------------------------------------ quest props: second composition and proofs
# QUEST_PROP_AUDIT.md rows R1 to R30. The reference room above is untouched; this room places every new quest entry
# in its before and after state, built only from records-atlas entries. The helpers below are shared by the Systems,
# Night Shift and Executive builds (build_systems.py imports this module as `br`).

QUEST_BEFORE = {"repair_door": "closed", "shelf_end_light": "off", "courier_chute": "idle", "folder_rack": "drift",
                "ledger_table": "before", "rolling_ladder": "closed", "report_table": "before", "lamp": "on"}
QUEST_AFTER = {"repair_door": "open", "shelf_end_light": "on", "courier_chute": "ready", "folder_rack": "aligned",
               "ledger_table": "after", "rolling_ladder": "open", "report_table": "after", "lamp": "pulse"}
QUEST_PEOPLE = [(mira, mira.IDLE["s"][0], 226, 140), (eng, eng.IDLE["n"][0], 144, 124)]   # module, frame, anchor x, anchor y
QUEST_REQUIRED = {"door": (128, 0, 160, 34), "ledger table": (196, 52, 260, 80), "report table": (192, 96, 226, 114),
                  "courier chute": (236, 100, 268, 128), "rolling ladder": (32, 84, 96, 116), "corridor start": (128, 160, 160, 180),
                  "folder rack": (72, 25, 104, 66), "shelf lights": (30, 24, 70, 50)}


def quest_layout():
    pl = []

    def entry(name, x, y):
        pl.append({"entry": name, **at(x, y)})

    def anim(name, x, y):
        pl.append({"anim": name, **at(x, y)})

    rnd = random.Random(41)
    n = 0
    while n < 16:
        x, y = rnd.randrange(4, 300), rnd.randrange(40, 180)
        if 124 <= x < 164:
            continue
        entry("floor_chip", x, y)
        n += 1
    for c in range(W_CELLS):
        if c not in (8, 9):                       # the repair door replaces two wall tiles
            entry("wall_n_plain", c * T, 0)
    for nm, x in (("wall_n_window_a", 40), ("wall_n_window_b", 96), ("wall_n_window_a", 200), ("wall_n_window_b", 240)):
        entry(nm, x, 9)
    for y in range(34, H_CELLS * T, T):
        entry("wall_e_plain", 288, y)
    anim("repair_door", 128, 0)
    # the corridor to the door: inlay lines and arrows
    for y in range(36, 192, T):
        entry("route_inlay_v", 128, y)
        entry("route_inlay_v", 159, y)
    for y in (96, 150):
        entry("route_arrow_n", 136, y)
    # north wall furniture: shelving with end lights, a folder rack, cabinets carrying Mira's desk decorations
    entry("shelf_2x1_a", 0, 32)
    anim("shelf_end_light", 29, 18)
    entry("shelf_1x1", 44, 32)
    anim("shelf_end_light", 57, 18)
    anim("folder_rack", 72, 36)
    entry("cabinet_1x1", 108, 32)
    entry("mira_decor_archive_folder", 109, 14)
    entry("cabinet_2x1", 166, 32)
    entry("mira_decor_courier_loop", 184, 15)
    for x in (200, 240):
        entry("light_shaft", x, 34)
    anim("ledger_table", 196, 58)
    anim("rolling_ladder", 32, 100)
    anim("report_table", 192, 100)
    anim("courier_chute", 236, 112)
    for x, y in ((120, 118), (166, 92)):
        anim("lamp", x, y)
    for nm, x, y in (("pot_plant_a", 6, 146), ("pot_plant_b", 100, 140), ("pot_plant_c", 270, 60), ("pot_plant_d", 276, 148)):
        entry(nm, x, y + 4)
    return {
        "kit": "records", "atlas": "records-atlas.json", "tile": T, "size_cells": [W_CELLS, H_CELLS],
        "note": "Records quest-prop room, built only from records-atlas (QUEST_PROP_AUDIT.md R1-R30). Every new quest entry appears in it; "
                "the state sets are switched between the before and after renders. The corridor (cols 8-9) leads north to the repair door. "
                "People are added by the renderer.",
        "states": dict(QUEST_BEFORE),
        "floor": {"legend": {"J": "floor_j", "H": "floor_h", "V": "floor_v", "P": "floor_p"}, "rows": ok_floor_rows()},
        "placements": pl,
    }


def render_people(canvas, people):
    for mod, frame, ax, ay in sorted(people, key=lambda p: p[3]):
        c = type("C", (), {})()
        c.img = canvas
        g.place_px(c, g.frame_rgba(frame, mod.PAL), ax, ay)


def render_quest(layout, atlas, states, people=QUEST_PEOPLE):
    lay = with_states(layout, **states)
    canvas = np.zeros((H_CELLS * T, W_CELLS * T, 3), np.uint8)
    kitlib.render_layout(lay, atlas, layers=BACK, base=canvas)
    render_people(canvas, people)
    kitlib.render_layout(lay, atlas, layers=FRONT, base=canvas)
    return canvas


def write_quest_layout(prefix, layout, meta):
    """Write <prefix>-quest-props-room.json and run check_atlas.check_layout on it. Returns True when it is clean."""
    path = os.path.join(HERE, f"{prefix}-quest-props-room.json")
    with open(path, "w") as fh:
        json.dump(layout, fh, indent=1)
        fh.write("\n")
    check_atlas.fails.clear()
    check_atlas.check_layout(path, {layout["atlas"]: meta})
    return not check_atlas.fails


def quest_images(prefix, layout, atlas, before_states, after_states, render_fn, to_screen_fn=None):
    """Write <prefix>-quest-props-{before,after}-{native,1366x768}.png. Returns (before, after) canvases."""
    to_screen_fn = to_screen_fn or to_screen
    before, after = render_fn(layout, atlas, before_states), render_fn(layout, atlas, after_states)
    for tag, cv in (("before", before), ("after", after)):
        Image.fromarray(cv).save(os.path.join(HERE, f"{prefix}-quest-props-{tag}-native.png"))
        to_screen_fn(cv).save(os.path.join(HERE, f"{prefix}-quest-props-{tag}-1366x768.png"))
    return before, after


def layout_names(layout, atlas, state_dicts):
    """Every entry a layout draws, across the given state dictionaries."""
    used = set()
    for st in state_dicts:
        used |= {name for _, _, name, _, _ in kitlib.expand(with_states(layout, **st), atlas)}
    # a placed state set also plays its transitional states (a door's half frame), so every one of its entries counts as drawn
    for p in layout["placements"]:
        if "anim" in p:
            for s in atlas.animations[p["anim"]]["states"].values():
                used |= set(s["entries"])
    return used


def quest_review(prefix, layout, atlas, quest_names, before, after, required, door=None, goal=None, start=(8, 10), blocked_fn=None, extra=()):
    """Checks shared by the four districts. door = (state-set name, open state): the corridor start -> goal is a two-cell-wide
    walkway when the door is open and none when it is closed. required = {label: (x0, y0, x1, y1)} view rectangles that
    must stay clear of the keyboard inset. Returns True when every check passes."""
    blocked_fn = blocked_fn or blocked_grid
    results = []

    def check(name, ok_, detail=""):
        results.append(ok_)
        print(("PASS " if ok_ else "FAIL ") + name + (f": {detail}" if detail else ""))
    used = layout_names(layout, atlas, (before, after))
    missing = sorted(set(quest_names) - used)
    check(f"every new {prefix} quest entry appears in the quest-prop room (before or after)", not missing,
          f"{len(quest_names)} entries" + (f"; missing {missing}" if missing else ""))
    if door:
        anim, open_state = door
        grid = blocked_fn(layout, atlas, dict(before, **{anim: open_state}))
        path = corridor_route(grid, start, goal)
        check("the corridor to the quest door is two cells wide when the door is open (BFS on the collision grid)", path is not None,
              f"{len(path)} steps, {start} -> {goal}" if path else "no path")
        check("the closed quest door blocks the corridor", corridor_route(blocked_fn(layout, atlas, before), start, goal) is None)
        if path:
            cells = {(x + dx, y + dy) for x, y in path for dx in (0, 1) for dy in (0, 1)}
            check("corridor cells are free of props", not any(grid[y, x] for x, y in cells), f"{len(cells)} cells")
    ix0, iy0, ix1, iy1 = INSET_VIEW
    bad = [n for n, (x0, y0, x1, y1) in required.items() if x0 < ix1 and x1 > ix0 and y0 < iy1 and y1 > iy0]
    check("no required quest element sits under the keyboard inset (view x 5-125, y 126.5-175)", not bad, ", ".join(bad) or "all clear")
    for name, ok_, detail in extra:
        check(name, ok_, detail)
    return all(results)


def quest_proofs(atlas, meta):
    layout = quest_layout()
    layout_ok = write_quest_layout("records", layout, meta)
    before, after = quest_images("records", layout, atlas, QUEST_BEFORE, QUEST_AFTER, render_quest)
    print(f"records quest props: {len(layout['placements'])} placements; before/after differ in {int(np.any(before != after, axis=2).sum())} px")
    ok_ = quest_review("records", layout, atlas, rk.QUEST_NAMES, QUEST_BEFORE, QUEST_AFTER, QUEST_REQUIRED, door=("repair_door", "open"), goal=(8, 0))
    return ok_ and layout_ok


# ------------------------------------------------------------------ wave 2: district integration proof room
# One room per district (20 x 12 cells) built only from the district atlas: three elevators across the north wall (closed,
# half, open) with the call panel, a seated worker behind desk_a with its desk_a_front occluder over the actor, desk_b with
# an artifact lying on it, and one cabinet per artifact carrying it. Each district adds the placements of its own new props.
# The helpers are shared by the Systems, Night Shift and Executive builds (they import this module as `br`).

SEAT = {"chair": (8, -12), "worker": (16, 4)}   # ORIENTATION_KIT_SPEC seat convention, relative to the desk origin
ELEVATORS = {"anim": (16, 0), "half": (96, 0), "open": (176, 0)}
ARTIFACT_CABINETS = [(176, 150), (208, 150), (240, 150), (272, 150)]


def integration_layout(kit, atlas_name, artifacts, extras, wall_tile="wall_n_plain", panel=None, desks=True, states=None, note=""):
    """Placement list for the district integration proof. `extras` is a list of placement dicts (use br.at for positions);
    `panel` is {"entry": name} or {"anim": name} for the call panel next to the first elevator."""
    pl = []

    def entry(name, x, y):
        pl.append({"entry": name, **at(x, y)})

    def anim(name, x, y):
        pl.append({"anim": name, **at(x, y)})

    rnd = random.Random(53)
    n = 0
    while n < 14:
        x, y = rnd.randrange(4, 300), rnd.randrange(56, 180)
        if 170 <= x < 300 and y >= 120 or x < 130 and y >= 120:
            continue
        entry("floor_chip", x, y)
        n += 1
    covered = {c for x in ELEVATORS.values() for c in range(x[0] // T, x[0] // T + 3)}
    for c in range(W_CELLS):
        if c not in covered:
            entry(wall_tile, c * T, 0)
    anim("elevator", *ELEVATORS["anim"])
    entry("elevator_half", *ELEVATORS["half"])
    entry("elevator_open", *ELEVATORS["open"])
    if panel:
        (kind, nm), = panel.items()
        (anim if kind == "anim" else entry)(nm, 68, 9)
    if desks:
        ax, ay = 32, 84
        entry("chair", ax + SEAT["chair"][0], ay + SEAT["chair"][1])
        entry("desk_a", ax, ay)
        entry("desk_a_front", ax, ay)               # after the actor, see render_integration
        bx, by = 112, 84
        entry("chair", bx + SEAT["chair"][0], by + SEAT["chair"][1])
        entry("desk_b", bx, by)
        entry("desk_b_front", bx, by)
        entry(f"artifact_{artifacts[0]}", bx + 19, by - 5)
    for i, slug in enumerate(artifacts[1:] if desks else artifacts):
        cx, cy = ARTIFACT_CABINETS[i]
        entry("cabinet_1x1", cx, cy)
        entry(f"artifact_{slug}", cx, cy - 18)
    pl.extend(extras)
    return {"kit": kit, "atlas": atlas_name, "tile": T, "size_cells": [W_CELLS, H_CELLS],
            "note": note or f"{kit} integration proof room, built only from {atlas_name}: the shared elevator set (closed, half, open) with the call panel, "
                            "a seated worker behind desk_a with its occluder, an artifact on desk_b and on cabinets, and the district's new props. People are added by the renderer.",
            "states": dict(states or {}),
            "floor": {"legend": {"J": "floor_j", "H": "floor_h", "V": "floor_v", "P": "floor_p"}, "rows": ok_floor_rows()},
            "placements": pl}


def integration_images(prefix, layout, atlas, before, after, render_fn, to_screen_fn=None):
    """Write <prefix>-integration-proof-{before,after}-{native,1366x768}.png. Returns (before, after) canvases."""
    to_screen_fn = to_screen_fn or to_screen
    b, a = render_fn(layout, atlas, before), render_fn(layout, atlas, after)
    for tag, cv in (("before", b), ("after", a)):
        Image.fromarray(cv).save(os.path.join(HERE, f"{prefix}-integration-proof-{tag}-native.png"))
        to_screen_fn(cv).save(os.path.join(HERE, f"{prefix}-integration-proof-{tag}-1366x768.png"))
    return b, a


def worker_stand_in(canvas, mod, frame, pal, desk=(32, 84)):
    """Place a person frame behind the desk by the seat convention (feet_bc at desk origin + (16, 4))."""
    c = type("C", (), {})()
    c.img = canvas
    g.place_px(c, g.frame_rgba(frame, pal), desk[0] + SEAT["worker"][0], desk[1] + SEAT["worker"][1])


def render_integration(layout, atlas, states, people=None):
    """BACK layers, the people, then the FRONT layers (the occluders and artifacts draw over the actors)."""
    lay = with_states(layout, **states)
    canvas = np.zeros((H_CELLS * T, W_CELLS * T, 3), np.uint8)
    kitlib.render_layout(lay, atlas, layers=BACK, base=canvas)
    for fn in (people if people is not None else [lambda cv: worker_stand_in(cv, eng, eng.IDLE["s"][0], eng.PAL)]):
        fn(canvas)
    kitlib.render_layout(lay, atlas, layers=FRONT, base=canvas)
    return canvas


def write_integration_layout(prefix, layout, meta):
    path = os.path.join(HERE, f"{prefix}-integration-room.json")
    with open(path, "w") as fh:
        json.dump(layout, fh, indent=1)
        fh.write("\n")
    check_atlas.fails.clear()
    check_atlas.check_layout(path, {layout["atlas"]: meta})
    return not check_atlas.fails


def integration_review(prefix, layout, atlas, meta, names, before, after, required, desk_front_covers=True, extra=()):
    """Shared checks: every new integration entry is drawn, the elevator/panel/occluder/artifact geometry is Orientation's,
    the occluder hides the seated worker's lower body, nothing required sits under the keyboard inset."""
    with open(os.path.join(HERE, "orientation-atlas.json")) as fh:
        orient = json.load(fh)
    ents = {e["name"]: e for e in meta["entries"]}
    try:
        import quest_props
        quest_props.check_elevator_geometry(ents, orient)
        geom, detail = True, "elevator set, panel, occluders and artifacts match orientation-atlas.json"
    except AssertionError as e:
        geom, detail = False, str(e)
    checks = [("the shared elevator, call panel, occluder and artifact entries have Orientation's geometry (size, footprint, collision, layer, anchor, shadow)", geom, detail)]
    if desk_front_covers:
        lay = with_states(layout, **before)
        canvas = np.zeros((H_CELLS * T, W_CELLS * T, 3), np.uint8)
        kitlib.render_layout(lay, atlas, layers=BACK, base=canvas)
        worker_stand_in(canvas, eng, eng.IDLE["s"][0], eng.PAL)
        with_occ = render_integration(layout, atlas, before)
        ax, ay = 32 + SEAT["worker"][0], 84 + SEAT["worker"][1]
        region = (slice(ay - 24, ay), slice(ax - 8, ax + 8))
        hidden = int(np.any(canvas[region] != with_occ[region], axis=2).sum())
        checks.append(("desk_a_front hides part of the seated worker's frame (the occluder draws over the actor)", hidden > 0, f"{hidden} px of the 16x24 frame are covered"))
    checks += list(extra)
    return quest_review(prefix, layout, atlas, names, before, after, required, extra=checks)


# ------------------------------------------------------------------ Records integration proof

INTEG_BEFORE = {"elevator": "closed", "cabinet_gate": "misaligned", "cabinet_labels": "offset", "ledger_mark": "rejected", "lamp": "on"}
INTEG_AFTER = {"elevator": "open", "cabinet_gate": "aligned", "cabinet_labels": "aligned", "ledger_mark": "accepted", "lamp": "pulse"}
INTEG_REQUIRED = {"elevators": (16, 0, 224, 48), "seated worker and desk": (32, 60, 150, 110), "gate and cabinets": (192, 56, 280, 90),
                  "ledger desk": (224, 99, 262, 124), "artifact cabinets": (176, 130, 290, 170)}


def rk_artifacts():
    return ["carbon_copy_a", "margin_stamp", "uncut_index", "noor_annotation"]


def records_integration_layout():
    desk = (224, 104)
    extras = [{"anim": "cabinet_gate", **at(192, 72)}, {"anim": "cabinet_labels", **at(240, 72)},
              {"entry": "door_panel_address_idle", **at(230, 15)},
              {"entry": "desk_b", **at(*desk)}, {"anim": "ledger_mark", **at(desk[0] + 22, desk[1] + 2)}]
    return integration_layout("records", "records-atlas.json", rk_artifacts(), extras, panel={"entry": "elevator_call_panel"}, states=INTEG_BEFORE,
                              note="Records integration proof room, built only from records-atlas: the shared elevator set (closed, half, open) and call panel, "
                                   "a seated worker behind desk_a with its occluder, artifacts on desk_b and on cabinets, the cabinet gate, the log cabinets, the address panel "
                                   "and the ledger mark overlay on a desk. People are added by the renderer.")


def ledger_overlay_matches(atlas):
    """The ledger mark overlays are the landmark's own ledger pixels: same colours at the same place."""
    lx, ly = rk._ledger_origin()
    by = {p.name: p for p in rk.landmark_pieces()}
    ok_ = True
    detail = []
    for st, src in (("rejected", "archive_ledger_before"), ("accepted", "archive_ledger_after")):
        ov = atlas.sprite(f"archive_ledger_mark_{st}")
        reg = by[src].sprite[ly - rk.OY: ly - rk.OY + 7, lx - rk.OX: lx - rk.OX + 12]
        same = bool(np.array_equal(ov, reg))
        ok_ &= same
        detail.append(f"{st} {'==' if same else '!='} {src}")
    return ok_, ", ".join(detail)


def integration_proofs(atlas, meta):
    layout = records_integration_layout()
    layout_ok = write_integration_layout("records", layout, meta)
    before, after = integration_images("records", layout, atlas, INTEG_BEFORE, INTEG_AFTER, render_integration)
    print(f"records integration: {len(layout['placements'])} placements; before/after differ in {int(np.any(before != after, axis=2).sum())} px")
    mark_ok, mark_detail = ledger_overlay_matches(atlas)
    gb = blocked_grid(layout, atlas, INTEG_BEFORE)
    ga = blocked_grid(layout, atlas, INTEG_AFTER)
    gate_cells = [(12, 4), (13, 4)]
    extra = [("ledger mark overlays are the landmark's own ledger pixels (a state swap cannot show two marks)", mark_ok, mark_detail),
             ("cabinet gate misaligned blocks its two cells and aligned frees them", all(gb[y, x] for x, y in gate_cells) and not any(ga[y, x] for x, y in gate_cells), "cells (12-13, 4)")]
    ok_ = integration_review("records", layout, atlas, meta, rk.INTEGRATION_NAMES, INTEG_BEFORE, INTEG_AFTER, INTEG_REQUIRED, extra=extra)
    return ok_ and layout_ok


# ------------------------------------------------------------------ main

def main():
    pieces, anims, lms = rk.build_pieces()
    pieces.sort(key=rk.group_rank)
    img, rects = kitlib.pack([(p.name, p.sprite) for p in pieces])
    img.save(os.path.join(HERE, "records-atlas.png"))
    meta = rk.atlas_json(pieces, rects, anims, lms)
    with open(os.path.join(HERE, "records-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
        fh.write("\n")
    layout = reference_layout()
    with open(os.path.join(HERE, "records-reference-room.json"), "w") as fh:
        json.dump(layout, fh, indent=1)
        fh.write("\n")
    atlas = kitlib.Atlas(os.path.join(HERE, "records-atlas.json"))
    build_kit.atlas_sheet(pieces, meta, rank_fn=rk.group_rank, sections=rk.SECTIONS, out="records-atlas-sheet.png",
                          title="Records kit atlas, x4 on a checker. Coral box: footprint cells. Coral cross: anchor. "
                                "Tags under each name: layer, footprint, size in px.")
    nchg = landmark_states(layout, atlas)
    before = render(layout, atlas, STATES_BEFORE)
    after = render(layout, atlas, STATES_AFTER)
    before, after = rf.light_layout(before, layout, atlas, "records"), rf.light_layout(after, layout, atlas, "records")  # rich finish light, display only
    Image.fromarray(before).save(os.path.join(HERE, "records-reference-room-native.png"))
    Image.fromarray(after).save(os.path.join(HERE, "records-reference-room-after-native.png"))
    to_screen(before).save(os.path.join(HERE, "records-reference-room-1366x768.png"))
    to_screen(before, inset=True).save(os.path.join(HERE, "records-reference-room-keyboard-inset.png"))
    to_screen(after).save(os.path.join(HERE, "records-reference-room-after-1366x768.png"))
    route_image(layout, atlas, before)
    print(f"{len(pieces)} entries; landmark before/after differ in {nchg} px; {len(layout['placements'])} placements")
    ok_ = review(layout, atlas)
    qok = quest_proofs(atlas, meta)
    iok = integration_proofs(atlas, meta)
    sys.exit(0 if ok_ and qok and iok else 1)


if __name__ == "__main__":
    main()
