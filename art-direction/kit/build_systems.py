"""Build the Systems environment kit and its reference room.

Run: python3 build_systems.py   (Pillow + numpy; run from anywhere)
Writes into this folder:
  systems-atlas.png / .json                  the atlas (check with check_atlas.py)
  systems-atlas-sheet.png                    every entry at x4 with footprint, collision, anchor
  systems-landmark-states.png                the routing machine before, after and changed pixels at x4
  systems-reference-room.json                cell layout built only from the atlas
  systems-reference-room-native.png          the room, before state (320x192, Engineer on the route)
  systems-reference-room-1366x768.png        the x4 view (320x180), before state, no inset
  systems-reference-room-keyboard-inset.png  the same with the keyboard inset rectangle overlaid
  systems-reference-room-after-native.png / -after-1366x768.png   landmark after, conduits lit, door open
  systems-reference-room-route.png           collision grid, the BFS route and the inset, for review
Then runs the programmatic review (route BFS on the collision grid, nothing required under the inset,
doorway brighter than its walls, palette discipline) and exits 1 if any check fails.

The renderer, BFS and screen helpers are reused from build_records.py (not edited).
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
import build_records as br  # noqa: E402
import kitlib  # noqa: E402
import systems_kit as sk  # noqa: E402
import build_scale_test as bst  # noqa: E402
import district_palettes as dp  # noqa: E402
import hal_sprites as hal  # noqa: E402

T = 16
W_CELLS, H_CELLS = br.W_CELLS, br.H_CELLS
STATES_BEFORE = {"service_door": "closed", "lamp": "on", "routing_machine": "before"}
CONDUIT_ANIMS = [f"conduit_{shape}_{fam}" for fam in ("cobalt", "mint", "orange") for shape in ("h", "v", "ne", "nw")]
STATES_AFTER = dict({"service_door": "open", "lamp": "pulse", "routing_machine": "after"}, **{a: "lit" for a in CONDUIT_ANIMS})
INSET_VIEW = br.INSET_VIEW
ENGINEER = br.ENGINEER
at = br.at

# conduit runs: (family, [(entry shape, x, y)]) in room pixels; the landmark's stubs end at y 124
WEST_RUN = ("mint", [("ne", 9, 124), ("h", 25, 124), ("h", 41, 124), ("nw", 57, 124)])
EAST_RUN = ("cobalt", [("ne", 119, 124)] + [("h", x, 124) for x in range(135, 231, 16)] + [("nw", 231, 124)])
UPLINK_RUN = ("orange", [("h", 144, 50), ("h", 160, 50), ("h", 176, 50), ("nw", 192, 50)])


# ------------------------------------------------------------------ layout

def reference_layout():
    pl = []

    def entry(name, x, y):
        pl.append({"entry": name, **at(x, y)})

    def anim(name, x, y):
        pl.append({"anim": name, **at(x, y)})

    # floor wear: a few chips away from the route
    rnd = random.Random(31)
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
    for nm, x in (("wall_n_window_a", 198), ("wall_n_window_b", 238)):
        entry(nm, x, 9)
    entry("status_board", 72, 8)
    for y in range(34, H_CELLS * T, T):
        if 66 <= y < 112:   # the door entries replace the wall here
            continue
        entry("wall_e_plain", 288, y)
    anim("service_door", 288, 72)
    for x, y in ((277, 45), (277, 119)):
        anim("lamp", x, y)
    # route: inlay lines and cobalt arrows
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
    # floor conduits, three families: each run is a state set so the circuit can light up
    for fam, run in (WEST_RUN, EAST_RUN, UPLINK_RUN):
        for shape, x, y in run:
            anim(f"conduit_{shape}_{fam}", x, y)
    # server racks along the north wall
    entry("rack_2x1_a", 0, 32)
    entry("rack_1x1", 32, 32)
    entry("rack_2x1_b", 144, 32)
    entry("rack_1x1", 176, 32)
    # the landmark
    pl.append({"landmark": "routing_machine", "cell": [3, 3]})
    # alarm terminal at the end of the mint run, payroll terminal at the end of the cobalt run
    entry("terminal_desk", 0, 108)
    entry("terminal_desk", 222, 108)
    # south-east service nook: parts shelving, lockers, a glass partition and a short bridge gallery
    entry("shelf_2x1_a", 192, 156)
    for x in range(224, 288, T):
        entry("bridge_deck", x, 160)
    for x in range(224, 288, T):
        entry("bridge_rail", x, 144)
    entry("cabinet_1x1", 200, 108)
    # planters
    for nm, x, y in (("pot_plant_a", 130, 140), ("pot_plant_b", 256, 52), ("pot_plant_a", 4, 150)):
        entry(nm, x, y + 4)
    return {
        "kit": "systems", "atlas": "systems-atlas.json", "tile": T, "size_cells": [W_CELLS, H_CELLS],
        "note": "Systems reference room, built only from systems-atlas. Floor is a cell grid; every other element is a placement at "
                "cell + pixel offset of its footprint origin. Draw order = layer order, then list order. The Engineer is added by the "
                "renderer, not the layout. The main route enters at the bottom (cols 10-11), runs north, turns east along rows 4-5 and ends at the door. "
                "Three conduit runs leave the routing machine: mint west to the alarm terminal, cobalt east to the payroll terminal, orange east and up to the wall.",
        "states": dict(STATES_BEFORE),
        "floor": {"legend": {"J": "floor_j", "H": "floor_h", "V": "floor_v", "P": "floor_p"}, "rows": br.ok_floor_rows()},
        "placements": pl,
    }


# ------------------------------------------------------------------ programmatic review

def review(layout, atlas):
    results = []

    def check(name, ok_, detail=""):
        results.append((name, ok_, detail))
        print(("PASS " if ok_ else "FAIL ") + name + (f": {detail}" if detail else ""))

    grid = br.blocked_grid(layout, atlas, dict(STATES_BEFORE, service_door="open"))
    start, goal = (10, 10), (17, 4)
    path = br.corridor_route(grid, start, goal)
    check("main route is a 2-cell-wide corridor from the entrance to the door (BFS on the collision grid)", path is not None,
          f"{len(path)} steps, {start} -> {goal}" if path else "no path")
    closed = br.blocked_grid(layout, atlas, STATES_BEFORE)
    check("the closed door blocks the route (the door state drives the collision)", br.corridor_route(closed, start, goal) is None)
    if path:
        cells = {(x + dx, y + dy) for x, y in path for dx in (0, 1) for dy in (0, 1)}
        check("route cells are free of props", not any(grid[y, x] for x, y in cells), f"{len(cells)} cells")
    mach = grid[3:7, 3:9]
    check("the routing machine blocks its 6x4 footprint (cells 3-8, rows 3-6)", bool(mach.all()), "24 cells")
    wk = grid[4:6, 9:11]
    check("the service walkway (after state) is walkable: the cells it covers are free", not wk.any(), "cells (9-10, 4-5)")
    conduit_cells = [(p["cell"][0], p["cell"][1]) for p in layout["placements"] if p.get("anim", "").startswith("conduit_")]
    check("conduit channels never block (they are floor markings)", all(not grid[y, x] for x, y in conduit_cells), f"{len(conduit_cells)} segments")
    ix0, iy0, ix1, iy1 = INSET_VIEW
    required = {"routing machine": (48, 48, 144, 112), "machine top and beacon": (48, 34, 144, 48), "service walkway": (144, 64, 176, 96),
                "door": (288, 50, 320, 118), "alarm terminal": (0, 101, 34, 124), "payroll terminal": (222, 101, 256, 124),
                "route start": (160, 160, 192, 180), "route corner": (160, 64, 192, 96), "north racks": (0, 20, 48, 48),
                "east racks": (144, 20, 192, 48), "status board": (72, 8, 120, 30), "orange uplink": (144, 50, 208, 62)}
    bad = [n for n, (x0, y0, x1, y1) in required.items() if x0 < ix1 and x1 > ix0 and y0 < iy1 and y1 > iy0]
    check("no required element sits under the keyboard inset (view x 5-125, y 126.5-175)", not bad, ", ".join(bad) or "all clear")
    room = br.render(layout, atlas, dict(STATES_BEFORE, service_door="open"), engineer=None)
    opening = room[76:108, 292:320]
    wall = np.concatenate([room[120:152, 292:320], room[36:60, 292:320]])
    lo, lw = br.luminance(opening), br.luminance(wall)
    check("doorway (open) is brighter than the adjacent east wall", lo > lw * 1.5, f"{lo:.0f} vs {lw:.0f} luma")
    allowed = {h.upper() for role in ("ink", "floor", "wall", "glass", "wood", "foliage", "accent") for h in dp.DISTRICTS["systems"][role]}
    violet = {h.upper() for h in dp.VIOLET}
    used = {kitlib.hexs(c) for c in np.unique(atlas.img[atlas.img[:, :, 3] > 0][:, :3], axis=0)}
    check("every atlas pixel is a Systems ramp step; no violet", used <= allowed and not (used & violet),
          f"{len(used)} colours" + (f", stray {sorted(used - allowed)}" if used - allowed else ""))
    markers = {h.upper() for h in dp.MARKERS.values()}
    check("no UI marker colour on art (teal, coral, violet, gold hex)", not (used & markers))
    # no violet-family floor or wall: floor and wall ramp steps are outside hue 260-320 above 12% saturation
    import colorsys
    bad_ramp = []
    for role in ("floor", "wall"):
        for h in dp.DISTRICTS["systems"][role]:
            r_, g_, b_ = [v / 255 for v in kitlib.hex2rgb(h)]
            hh, ll, ss = colorsys.rgb_to_hls(r_, g_, b_)
            if 260 <= hh * 360 <= 320 and ss > 0.12:
                bad_ramp.append(h)
    check("no violet-family floor or wall step", not bad_ramp, ", ".join(bad_ramp) or "hue clear")
    # the accent stays trim: orange pixels and mint pixels as a share of the room (before and after)
    for nm, st in (("before", STATES_BEFORE), ("after", STATES_AFTER)):
        rm = br.render(layout, atlas, st, engineer=None)
        flat = rm.reshape(-1, 3)
        orange = {h.upper() for h in dp.DISTRICTS["systems"]["accent"]}
        n_or = sum(int(np.all(flat == np.array(kitlib.hex2rgb(h)), axis=1).sum()) for h in orange)
        share = n_or / len(flat)
        check(f"safety orange stays small trim in the {nm} room (under 4% of pixels)", share < 0.04, f"{share * 100:.2f}%")
    lm = atlas.landmarks["routing_machine"]
    diff = set(lm["states"]["before"]["parts"]) ^ set(lm["states"]["after"]["parts"])
    check("landmark after state changes at least two visible things", len(diff) >= 2 and len(lm["states"]["after"]["lamps"]) > 0,
          f"{len(diff)} parts differ, lamps switch")
    return all(r[1] for r in results)


# ------------------------------------------------------------------ images

def landmark_states(layout, atlas):
    box = (16, 8, 176, 152)
    Z = 4
    imgs = {}
    for st in ("before", "after"):
        imgs[st] = br.render(layout, atlas, STATES_BEFORE if st == "before" else STATES_AFTER, engineer=None)[box[1]:box[3], box[0]:box[2]]
    changed = np.any(imgs["before"] != imgs["after"], axis=2)
    dim = imgs["after"].copy()
    dim[~changed] = (imgs["after"][~changed] * 0.35 + np.array(bst.INK[0]) * 0.65).astype(np.uint8)  # diagnostic only
    panels = [("BEFORE: the Systems review not yet complete", imgs["before"]),
              ("AFTER: review complete", imgs["after"]), (f"CHANGED: {int(changed.sum())} px (rest dimmed)", dim)]
    pw, ph = (box[2] - box[0]) * Z, (box[3] - box[1]) * Z
    lm = atlas.landmarks["routing_machine"]
    sheet = Image.new("RGB", (len(panels) * (pw + 20) + 20, ph + 80 + 20 * len(lm["changes_after"])), build_kit.BG)
    d = ImageDraw.Draw(sheet)
    for i, (title, im) in enumerate(panels):
        x = 20 + i * (pw + 20)
        sheet.paste(Image.fromarray(im).resize((pw, ph), Image.NEAREST), (x, 50))
        d.text((x, 16), title, font=bst.font(20, bold=True), fill="#F4F2EC")
    for i, line in enumerate(lm["changes_after"]):
        d.text((20, ph + 62 + i * 20), "+ " + line[:250], font=bst.font(13), fill="#C5CED0")
    sheet.save(os.path.join(HERE, "systems-landmark-states.png"))
    return int(changed.sum())


def route_image(layout, atlas, canvas):
    Z = 4
    grid = br.blocked_grid(layout, atlas, dict(STATES_BEFORE, service_door="open"))
    path = br.corridor_route(grid, (10, 10), (17, 4))
    img = Image.fromarray(canvas).resize((canvas.shape[1] * Z, canvas.shape[0] * Z), Image.NEAREST).convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(grid.shape[0]):
        for x in range(grid.shape[1]):
            b = [x * T * Z, y * T * Z, (x + 1) * T * Z - 1, (y + 1) * T * Z - 1]
            if grid[y, x]:
                d.rectangle(b, fill=(236, 119, 109, 70), outline=(236, 119, 109, 160))
    if path:
        cells = {(x + dx, y + dy) for x, y in path for dx in (0, 1) for dy in (0, 1)}
        for x, y in cells:
            d.rectangle([x * T * Z + 2, y * T * Z + 2, (x + 1) * T * Z - 3, (y + 1) * T * Z - 3], outline=(25, 175, 162, 255), width=3)
    ix0, iy0, ix1, iy1 = [v * Z for v in INSET_VIEW]
    d.rectangle([ix0, iy0, ix1, iy1], outline=(230, 183, 80, 255), width=4)
    d.text((ix0 + 8, iy0 + 8), "keyboard inset", font=bst.font(18, bold=True), fill=(230, 183, 80, 255))
    d.text((8, img.size[1] - 26), "coral cells block, teal cells are the 2-wide route found by BFS (door open), gold is the keyboard inset",
           font=bst.font(14), fill=(244, 242, 236, 255))
    Image.alpha_composite(img, ov).convert("RGB").save(os.path.join(HERE, "systems-reference-room-route.png"))


# ------------------------------------------------------------------ quest props: second composition and proofs
# QUEST_PROP_AUDIT.md rows S1 to S25. The reference room above is untouched. The quest room places every new Systems quest
# entry in its before and after state; the helpers come from build_records (br).

QUEST_BEFORE = {"payroll_keypad": "off", "bridge_span": "retracted", "refund_sign": "red", "calc_display": "charge", "alarm_strip": "merged",
                "bridge_shutter": "closed", "formula_wall": "dark", "courier_chute": "idle", "lamp": "on"}
QUEST_AFTER = {"payroll_keypad": "lit", "bridge_span": "extended", "refund_sign": "green", "calc_display": "refund", "alarm_strip": "separated",
               "bridge_shutter": "open", "formula_wall": "lit", "courier_chute": "ready", "lamp": "pulse"}
SPAN_CELL = (10, 6)   # the bridge span's cell (4 x 2); rails run along the rows above and below it
QUEST_PEOPLE = [(br.mira, br.mira.IDLE["s"][0], 236, 150), (hal, hal.IDLE["s"][0], 122, 92), (br.eng, br.eng.IDLE["e"][0], 140, 128)]
QUEST_REQUIRED = {"alarm strip": (8, 9, 72, 27), "formula wall": (84, 8, 180, 30), "refund sign": (186, 10, 210, 24),
                  "payroll keypad": (6, 38, 40, 70), "calculator display": (56, 50, 92, 68), "bridge span": (160, 96, 224, 128),
                  "courier chute": (244, 116, 278, 159), "shutters": (222, 9, 288, 29)}


def quest_layout():
    pl = []

    def entry(name, x, y):
        pl.append({"entry": name, **at(x, y)})

    def anim(name, x, y):
        pl.append({"anim": name, **at(x, y)})

    rnd = random.Random(37)
    n = 0
    while n < 16:
        x, y = rnd.randrange(4, 300), rnd.randrange(40, 180)
        if 156 <= x < 228 and 76 <= y < 150:
            continue
        entry("floor_chip", x, y)
        n += 1
    for c in range(W_CELLS):
        entry("wall_n_plain", c * T, 0)
    for y in range(34, H_CELLS * T, T):
        entry("wall_e_plain", 288, y)
    # the wall run, left to right: alarm strip, formula wall, refund sign, two shuttered windows
    anim("alarm_strip", 8, 9)
    anim("formula_wall", 84, 8)
    anim("refund_sign", 186, 10)
    anim("bridge_shutter", 222, 9)
    anim("bridge_shutter", 256, 9)
    # the payroll wing and the side room
    anim("payroll_keypad", 6, 52)
    anim("calc_display", 56, 50)
    entry("folding_stool", 98, 68)
    entry("cabinet_1x1", 128, 52)
    entry("mira_decor_signed_sent", 129, 31)
    entry("cabinet_2x1", 150, 52)
    entry("mira_decor_relay", 160, 30)
    # the bridge: span in the middle, glass rails above and below it
    anim("bridge_span", SPAN_CELL[0] * T, SPAN_CELL[1] * T)
    for x in range(160, 224, T):
        entry("bridge_rail", x, 80)
        entry("bridge_rail", x, 128)
    # Mira's chute at the end of the bridge
    anim("courier_chute", 244, 128)
    for x, y in ((120, 96), (232, 84), (277, 160)):
        anim("lamp", x, y)
    for nm, x, y in (("pot_plant_a", 6, 146), ("pot_plant_b", 100, 140), ("pot_plant_a", 272, 52)):
        entry(nm, x, y + 4)
    return {
        "kit": "systems", "atlas": "systems-atlas.json", "tile": T, "size_cells": [W_CELLS, H_CELLS],
        "note": "Systems quest-prop room, built only from systems-atlas (QUEST_PROP_AUDIT.md S1-S25). Every new quest entry appears in it; "
                "the state sets are switched between the before and after renders. The north wall carries the alarm strip, formula wall, "
                "refund sign and shutters; the bridge span crosses the middle of the room to Mira's chute. People are added by the renderer.",
        "states": dict(QUEST_BEFORE),
        "floor": {"legend": {"J": "floor_j", "H": "floor_h", "V": "floor_v", "P": "floor_p"}, "rows": br.ok_floor_rows()},
        "placements": pl,
    }


def render_quest(layout, atlas, states, people=QUEST_PEOPLE):
    return br.render_quest(layout, atlas, states, people)


def quest_proofs(atlas, meta):
    layout = quest_layout()
    layout_ok = br.write_quest_layout("systems", layout, meta)
    before, after = br.quest_images("systems", layout, atlas, QUEST_BEFORE, QUEST_AFTER, render_quest)
    print(f"systems quest props: {len(layout['placements'])} placements; before/after differ in {int(np.any(before != after, axis=2).sum())} px")
    cx, cy = SPAN_CELL
    retracted = br.blocked_grid(layout, atlas, dict(QUEST_BEFORE))
    extended = br.blocked_grid(layout, atlas, dict(QUEST_BEFORE, bridge_span="extended"))
    mid = [(cx + 1, cy), (cx + 2, cy), (cx + 1, cy + 1), (cx + 2, cy + 1)]
    ends = [(cx, cy), (cx + 3, cy), (cx, cy + 1), (cx + 3, cy + 1)]
    path = br.corridor_route(extended, (cx - 1, cy), (cx + 4, cy))
    extra = [("the retracted bridge span blocks its two middle columns and the extended span is walkable end to end",
              all(retracted[y, x] for x, y in mid) and not any(retracted[y, x] for x, y in ends) and not any(extended[y, x] for x, y in mid + ends),
              "4 pit cells blocked, 4 end cells free, 8 cells free when extended"),
             ("the extended span is a two-cell-wide walkway between its rails (BFS on the collision grid)", path is not None, f"{len(path)} steps" if path else "no path"),
             ("the retracted span leaves no two-cell-wide way across", br.corridor_route(retracted, (cx - 1, cy), (cx + 4, cy)) is None, "")]
    ok_ = br.quest_review("systems", layout, atlas, sk.QUEST_NAMES, QUEST_BEFORE, QUEST_AFTER, QUEST_REQUIRED, extra=extra)
    return ok_ and layout_ok


# ------------------------------------------------------------------ main

def main():
    pieces, anims, lms = sk.build_pieces()
    pieces.sort(key=sk.group_rank)
    img, rects = kitlib.pack([(p.name, p.sprite) for p in pieces])
    img.save(os.path.join(HERE, "systems-atlas.png"))
    meta = sk.atlas_json(pieces, rects, anims, lms)
    with open(os.path.join(HERE, "systems-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
        fh.write("\n")
    layout = reference_layout()
    with open(os.path.join(HERE, "systems-reference-room.json"), "w") as fh:
        json.dump(layout, fh, indent=1)
        fh.write("\n")
    atlas = kitlib.Atlas(os.path.join(HERE, "systems-atlas.json"))
    build_kit.atlas_sheet(pieces, meta, rank_fn=sk.group_rank, sections=sk.SECTIONS, out="systems-atlas-sheet.png",
                          title="Systems kit atlas, x4 on a checker. Coral box: footprint cells. Coral cross: anchor. "
                                "Tags under each name: layer, footprint, size in px.")
    nchg = landmark_states(layout, atlas)
    before = br.render(layout, atlas, STATES_BEFORE, engineer=ENGINEER)
    after = br.render(layout, atlas, STATES_AFTER, engineer=ENGINEER)
    Image.fromarray(before).save(os.path.join(HERE, "systems-reference-room-native.png"))
    Image.fromarray(after).save(os.path.join(HERE, "systems-reference-room-after-native.png"))
    br.to_screen(before).save(os.path.join(HERE, "systems-reference-room-1366x768.png"))
    br.to_screen(before, inset=True).save(os.path.join(HERE, "systems-reference-room-keyboard-inset.png"))
    br.to_screen(after).save(os.path.join(HERE, "systems-reference-room-after-1366x768.png"))
    route_image(layout, atlas, before)
    print(f"{len(pieces)} entries; landmark before/after differ in {nchg} px; {len(layout['placements'])} placements")
    ok_ = review(layout, atlas)
    qok = quest_proofs(atlas, meta)
    sys.exit(0 if ok_ and qok else 1)


if __name__ == "__main__":
    main()
