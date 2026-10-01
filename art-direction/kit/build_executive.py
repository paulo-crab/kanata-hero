"""Build the Executive environment kit and its reference room.

Run: python3 build_executive.py   (Pillow + numpy; run from anywhere)
Writes into this folder:
  executive-atlas.png / .json                  the atlas (check with check_atlas.py)
  executive-atlas-sheet.png                    every entry at x4 with footprint, collision, anchor
  executive-landmark-states.png                the atrium tree before, after and changed pixels at x4
  executive-reference-room.json                cell layout built only from the atlas
  executive-reference-room-native.png          the room, before state (320x192, Vale under the tree, Engineer on the route)
  executive-reference-room-1366x768.png        the x4 view (320x180), before state, no inset
  executive-reference-room-keyboard-inset.png  the same with the keyboard inset rectangle overlaid
  executive-reference-room-after-native.png / -after-1366x768.png   landmark after, final door open, windows in daylight
  executive-reference-room-route.png           collision grid, the BFS route and the inset, for review
  executive-vale-wall-check.png                diagnostic: Vale against the navy north wall, the alcove, the east wall and the navy sofa
Then runs the programmatic review (route BFS on the collision grid, nothing required under the inset,
doorway brighter than its walls, palette-only atlas, Vale against the walls) and exits 1 if any check fails.
"""
import json
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_kit  # noqa: E402
import build_records as br  # noqa: E402  (to_screen, corridor_route, luminance: generic helpers, not edited)
import kitlib  # noqa: E402
import executive_kit as xk  # noqa: E402
import build_gate1 as g  # noqa: E402
import build_scale_test as bst  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import district_palettes as dp  # noqa: E402
import vale_sprites as vale  # noqa: E402

T = 16
W_CELLS, H_CELLS = 20, 12
BACK = {"floor", "rear_wall", "floor_marking", "rear_prop", "shadow"}
FRONT = {"front_prop", "light"}
STATES_BEFORE = {"final_door": "closed", "lamp": "on", "atrium_tree": "before", "window_a": "overcast", "window_b": "overcast",
                 "window_light": "overcast"}
STATES_AFTER = {"final_door": "open", "lamp": "pulse", "atrium_tree": "after", "window_a": "daylight", "window_b": "daylight",
                "window_light": "daylight"}

ENGINEER = (eng.IDLE["n"][0], 176, 146, eng.PAL)               # frame, anchor x, anchor y, palette: centre of the 2-cell corridor
VALE = (vale.IDLE["s"][0], 119, 103, vale.PAL)                 # beside the planter, inside the well, on the bare floor
INSET_VIEW = br.INSET_VIEW                                     # keyboard inset in view px (Gate 1 overlay geometry, /4)
WELL_FP = (32, 48)                                             # landmark footprint origin in the room: cell (2, 3)


# ------------------------------------------------------------------ layout

def at(x, y):
    d = {"cell": [x // T, y // T]}
    if (x % T, y % T) != (0, 0):
        d["offset"] = [x % T, y % T]
    return d


def floor_rows():
    import orientation_kit as ok
    return ok.floor_rows()[:H_CELLS]


def reference_layout():
    pl = []

    def entry(name, x, y):
        pl.append({"entry": name, **at(x, y)})

    def anim(name, x, y):
        pl.append({"anim": name, **at(x, y)})

    # floor wear: a few chips away from the route and the well, none in the corridor
    rnd = random.Random(31)
    n = 0
    while n < 18:
        x, y = rnd.randrange(4, 300), rnd.randrange(40, 180)
        if 156 <= x < 296 and 60 <= y < 100 or 156 <= x < 196 and y >= 96 or 28 <= x < 148 and 40 <= y < 132:
            continue
        entry("floor_chip", x, y)
        n += 1
    # north wall: plain wall, copper trim under the windows, windows (state sets), the reception alcove
    for c in range(W_CELLS):
        entry("wall_n_plain", c * T, 0)
    for c in range(W_CELLS):
        entry("wall_n_trim", c * T, 22)
    for nm, x in (("window_a", 4), ("window_b", 36)):
        anim(nm, x, 9)
    entry("wall_n_alcove", 204, 6)
    # east wall: plain above and below the door, which carries its own wall mass
    entry("wall_e_plain", 288, 34)
    for y in range(96, H_CELLS * T, T):
        entry("wall_e_plain", 288, y)
    anim("final_door", 288, 58)
    for x, y in ((277, 45), (277, 115)):
        anim("lamp", x, y)
    # route: neutral inlay lines on the corridor edges, copper arrows on its middle
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
        entry("route_arrow_e", x, 68)
    # window light under the first window pair
    anim("window_light", 4, 34)
    # north wall furniture
    entry("shelf_2x1_a", 150, 32)
    entry("cabinet_1x1", 184, 32)
    entry("terminal_desk", 216, 44)
    # the landmark
    pl.append({"landmark": "atrium_tree", **at(*WELL_FP)})
    # south-east boardroom: glass partitions behind the long table, navy chairs on the near side
    entry("partition_2x1", 192, 112)
    entry("partition_2x1", 224, 112)
    entry("partition_1x1", 256, 112)
    entry("boardroom_table", 200, 134)
    for x in (206, 226, 246):
        entry("boardroom_chair", x, 168)
    entry("pot_plant_c", 268, 150)
    # south-west lounge (under the keyboard inset: decoration only)
    entry("sofa", 12, 148)
    entry("side_table", 54, 152)
    entry("bench", 66, 168)
    # planters
    for nm, x, y in (("pot_plant_a", 96, 146), ("pot_plant_b", 298, 150 - 4 + 22)):
        entry(nm, x, y + 4)
    return {
        "kit": "executive", "atlas": "executive-atlas.json", "tile": T, "size_cells": [W_CELLS, H_CELLS],
        "note": "Executive reference room, built only from executive-atlas. Floor is a cell grid; every other element is a placement at "
                "cell + pixel offset of its footprint origin. Draw order = layer order, then list order. Vale and the Engineer are added by the "
                "renderer, not the layout. The main route enters at the bottom (cols 10-11), runs north, turns east along rows 4-5 and ends at the "
                "final door, which is visible from the entry. The atrium well is a landmark at cell (2, 3).",
        "states": dict(STATES_BEFORE),
        "floor": {"legend": {"J": "floor_j", "H": "floor_h", "V": "floor_v", "P": "floor_p"}, "rows": floor_rows()},
        "placements": pl,
    }


# ------------------------------------------------------------------ render

def render(layout, atlas, states, actors=None):
    lay = br.with_states(layout, **states)
    canvas = np.zeros((H_CELLS * T, W_CELLS * T, 3), np.uint8)
    kitlib.render_layout(lay, atlas, layers=BACK, base=canvas)
    c = type("C", (), {})()
    c.img = canvas
    for frame, ax, ay, pal in (VALE, ENGINEER) if actors is None else actors:
        g.place_px(c, g.frame_rgba(frame, pal), ax, ay)
    kitlib.render_layout(lay, atlas, layers=FRONT, base=canvas)
    return canvas


def blocked_grid(layout, atlas, states):
    return kitlib.collision_grid(br.with_states(layout, **states), atlas)


# ------------------------------------------------------------------ programmatic review

def dE76(a, b):
    def lab(c):
        c = np.array(c, float) / 255.0
        c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
        x = (0.4124 * c[0] + 0.3576 * c[1] + 0.1805 * c[2]) / 0.95047
        y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
        z = (0.0193 * c[0] + 0.1192 * c[1] + 0.9505 * c[2]) / 1.08883
        f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)  # noqa: E731
        return np.array([116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))])
    return float(np.linalg.norm(lab(a) - lab(b)))


def vale_wall_check(atlas):
    """Vale stands in front of each Executive wall surface; his 1 px ink contour and suit have to separate from it.
    Returns (rows, worst) with the smallest contour-to-wall dE76 over the wall steps that appear behind him."""
    rows = []
    body = g.frame_rgba(vale.IDLE["s"][0], vale.PAL)
    outline = np.array(kitlib.hex2rgb(dp.INK[0]), np.uint8)
    suit = {np.array(kitlib.hex2rgb(vale.PAL[k]), np.uint8).tobytes() for k in "pqrs"}
    for name, walls in (("north wall face", dp.DISTRICTS["executive"]["wall"][1:3]), ("east wall mass", dp.DISTRICTS["executive"]["wall"][0:1]),
                        ("alcove", dp.DISTRICTS["executive"]["wall"][2:4]), ("navy seating", dp.DISTRICTS["executive"]["wall"][0:3])):
        worst = min(dE76(outline, kitlib.hex2rgb(w)) for w in walls)
        lit = min(dE76(kitlib.hex2rgb(vale.PAL["s"]), kitlib.hex2rgb(w)) for w in walls)
        rows.append((name, worst, lit))
    return rows


def review(layout, atlas):
    results = []

    def check(name, ok_, detail=""):
        results.append((name, ok_, detail))
        print(("PASS " if ok_ else "FAIL ") + name + (f": {detail}" if detail else ""))

    # route, with the door open (it opens on approach)
    open_door = dict(STATES_BEFORE, final_door="open")
    grid = blocked_grid(layout, atlas, open_door)
    start, goal = (10, 10), (17, 4)
    path = br.corridor_route(grid, start, goal)
    check("main route is a 2-cell-wide corridor from the entrance to the final door (BFS on the collision grid)", path is not None,
          f"{len(path)} steps, {start} -> {goal}" if path else "no path")
    closed = blocked_grid(layout, atlas, STATES_BEFORE)
    check("the closed final door blocks the route (the door state drives the collision)", br.corridor_route(closed, start, goal) is None)
    if path:
        cells = {(x + dx, y + dy) for x, y in path for dx in (0, 1) for dy in (0, 1)}
        check("route cells are free of props", not any(grid[y, x] for x, y in cells), f"{len(cells)} cells")
    # the well: balustrade ring blocks, the three south cells are the steps, the planter blocks two rows
    fx, fy = WELL_FP[0] // T, WELL_FP[1] // T
    sub = grid[fy:fy + 5, fx:fx + 7]
    expect = np.array([[c == "1" for c in row] for row in ["1111111", "1011101", "1011101", "1000001", "1100011"]])
    check("atrium well collision: rail ring, planter, open steps", np.array_equal(sub, expect))
    # the steps are reachable from the route area: a free path from the corridor into the well's south row
    reach = [(fx + 3, fy + 4)]
    check("the steps (south gap) are free cells", not any(grid[y, x] for x, y in reach))
    # nothing required under the keyboard inset
    ix0, iy0, ix1, iy1 = INSET_VIEW
    required = {"atrium well (footprint, steps)": (32, 48, 144, 126), "planter and tree": (64, 14, 112, 102), "Vale": (111, 79, 127, 103),
                "final door": (288, 36, 320, 104), "reception console": (216, 37, 248, 60), "route start": (160, 160, 192, 180),
                "route corner": (160, 64, 192, 96), "boardroom table": (200, 134, 264, 166)}
    bad = [n for n, (x0, y0, x1, y1) in required.items() if x0 < ix1 and x1 > ix0 and y0 < iy1 and y1 > iy0]
    check("no required element sits under the keyboard inset (view x 5-125, y 126.5-175)", not bad, ", ".join(bad) or "all clear")
    # the doorway is brighter than the walls beside it
    room = render(layout, atlas, open_door, actors=[])
    opening = room[62:94, 300:320]
    wall = np.concatenate([room[112:150, 296:320], room[34:50, 296:320]])
    lo, lw = br.luminance(opening), br.luminance(wall)
    check("final doorway (open) is brighter than the adjacent east wall", lo > lw * 1.5, f"{lo:.0f} vs {lw:.0f} luma")
    # the door's wall mass matches the plain east wall (navy), so the door reads as set into one wall
    room_closed = render(layout, atlas, STATES_BEFORE, actors=[])
    cm = {tuple(c) for c in np.unique(room_closed[34:50, 306:320].reshape(-1, 3), axis=0)}
    pm = {tuple(c) for c in np.unique(room_closed[130:150, 300:320].reshape(-1, 3), axis=0)}
    check("the wall above the door and the plain east wall below it share the navy mass colour",
          tuple(kitlib.hex2rgb(dp.DISTRICTS["executive"]["wall"][0])) in cm and tuple(kitlib.hex2rgb(dp.DISTRICTS["executive"]["wall"][0])) in pm)
    # palette discipline
    allowed = {h.upper() for role in ("ink", "floor", "wall", "glass", "wood", "foliage", "accent") for h in dp.DISTRICTS["executive"][role]}
    violet = {h.upper() for h in dp.VIOLET}
    used = {kitlib.hexs(c) for c in np.unique(atlas.img[atlas.img[:, :, 3] > 0][:, :3], axis=0)}
    check("every atlas pixel is an Executive ramp step; no violet", used <= allowed and not (used & violet),
          f"{len(used)} colours" + (f", stray {sorted(used - allowed)}" if used - allowed else ""))
    # Vale against the walls: contour dE and lit edge dE
    rows = vale_wall_check(atlas)
    worst = min(r[1] for r in rows)
    check("Vale's ink contour separates from every navy surface he stands against (dE76 >= 8)", worst >= 8.0,
          "; ".join(f"{n}: contour {c:.1f}, lit edge {l:.1f}" for n, c, l in rows))
    # clear floor in front of the navy walls: nothing but wall furniture within one cell of the route, and Vale and the Engineer stand >= 24 px from walls
    check("the Engineer and Vale keep a clear floor margin (>= 16 px) below the north wall and >= 24 px from the east wall",
          all(a[2] - 24 - 34 >= 16 and 292 - (a[1] + 8) >= 24 for a in (VALE, ENGINEER)))
    row3 = [grid[3, c] for c in range(10, 18)]
    check("the floor row in front of the north furniture along the corridor is clear (cols 10-17, row 3)", not any(row3))
    # the landmark's two states differ in at least two visible parts
    lm = atlas.landmarks["atrium_tree"]
    diff = set(lm["states"]["before"]["parts"]) ^ set(lm["states"]["after"]["parts"])
    check("landmark after state changes at least two visible things", len(diff) >= 2 and len(lm["states"]["after"]["lamps"]) > 0,
          f"{len(diff)} parts differ, lamps switch")
    return all(r[1] for r in results)


# ------------------------------------------------------------------ images

def landmark_states(layout, atlas):
    box = (0, 14, 176, 174)
    Z = 4
    imgs = {}
    for st in ("before", "after"):
        imgs[st] = render(layout, atlas, dict(STATES_BEFORE, atrium_tree=st, lamp="on" if st == "before" else "pulse"), actors=[])[box[1]:box[3], box[0]:box[2]]
    changed = np.any(imgs["before"] != imgs["after"], axis=2)
    dim = imgs["after"].copy()
    dim[~changed] = (imgs["after"][~changed] * 0.35 + np.array(bst.INK[0]) * 0.65).astype(np.uint8)  # diagnostic only
    panels = [("BEFORE: the three repairs not yet made", imgs["before"]),
              ("AFTER: three accurate repairs", imgs["after"]), (f"CHANGED: {int(changed.sum())} px (rest dimmed)", dim)]
    pw, ph = (box[2] - box[0]) * Z, (box[3] - box[1]) * Z
    sheet = Image.new("RGB", (len(panels) * (pw + 20) + 20, ph + 190), build_kit.BG)
    d = ImageDraw.Draw(sheet)
    for i, (title, im) in enumerate(panels):
        x = 20 + i * (pw + 20)
        sheet.paste(Image.fromarray(im).resize((pw, ph), Image.NEAREST), (x, 50))
        d.text((x, 16), title, font=bst.font(20, bold=True), fill="#F4F2EC")
    lm = atlas.landmarks["atrium_tree"]
    for i, line in enumerate(lm["changes_after"]):
        d.text((20, ph + 62 + i * 20), "+ " + line[:230], font=bst.font(13), fill="#C5CED0")
    sheet.save(os.path.join(HERE, "executive-landmark-states.png"))
    return int(changed.sum())


def route_image(layout, atlas, canvas):
    Z = 4
    grid = blocked_grid(layout, atlas, dict(STATES_BEFORE, final_door="open"))
    path = br.corridor_route(grid, (10, 10), (17, 4))
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
    Image.alpha_composite(img, ov).convert("RGB").save(os.path.join(HERE, "executive-reference-room-route.png"))


def vale_wall_image(layout, atlas):
    """Diagnostic: Vale idle S against the north wall face, the alcove, the east wall mass and the navy sofa, at x4."""
    spots = [(26, 48), (262, 48), (306, 128), (24, 168), (44, 168), (230, 52)]
    states = dict(STATES_BEFORE)
    actors = [(vale.IDLE["s"][0], x, y, vale.PAL) for x, y in spots]
    canvas = render(layout, atlas, states, actors=actors)
    to = br.to_screen(canvas)
    d = ImageDraw.Draw(to)
    d.text((54, 4), "Vale (state 0) against the navy north wall, the alcove, the east wall and the navy sofa: contour and lit edge", font=bst.font(14, bold=True), fill="#F4F2EC")
    to.save(os.path.join(HERE, "executive-vale-wall-check.png"))


# ------------------------------------------------------------------ main

def main():
    pieces, anims, lms = xk.build_pieces()
    pieces.sort(key=xk.group_rank)
    img, rects = kitlib.pack([(p.name, p.sprite) for p in pieces])
    img.save(os.path.join(HERE, "executive-atlas.png"))
    meta = xk.atlas_json(pieces, rects, anims, lms)
    with open(os.path.join(HERE, "executive-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
        fh.write("\n")
    layout = reference_layout()
    with open(os.path.join(HERE, "executive-reference-room.json"), "w") as fh:
        json.dump(layout, fh, indent=1)
        fh.write("\n")
    atlas = kitlib.Atlas(os.path.join(HERE, "executive-atlas.json"))
    build_kit.atlas_sheet(pieces, meta, rank_fn=xk.group_rank, sections=xk.SECTIONS, out="executive-atlas-sheet.png",
                          title="Executive kit atlas, x4 on a checker. Coral box: footprint cells. Coral cross: anchor. "
                                "Tags under each name: layer, footprint, size in px.")
    nchg = landmark_states(layout, atlas)
    before = render(layout, atlas, STATES_BEFORE)
    after = render(layout, atlas, STATES_AFTER)
    Image.fromarray(before).save(os.path.join(HERE, "executive-reference-room-native.png"))
    Image.fromarray(after).save(os.path.join(HERE, "executive-reference-room-after-native.png"))
    br.to_screen(before).save(os.path.join(HERE, "executive-reference-room-1366x768.png"))
    br.to_screen(before, inset=True).save(os.path.join(HERE, "executive-reference-room-keyboard-inset.png"))
    br.to_screen(after).save(os.path.join(HERE, "executive-reference-room-after-1366x768.png"))
    route_image(layout, atlas, before)
    vale_wall_image(layout, atlas)
    print(f"{len(pieces)} entries; landmark before/after differ in {nchg} px; {len(layout['placements'])} placements")
    ok_ = review(layout, atlas)
    sys.exit(0 if ok_ else 1)


if __name__ == "__main__":
    main()
