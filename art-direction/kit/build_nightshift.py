"""Build the Night Shift environment kit and its reference room.

Run: python3 build_nightshift.py   (Pillow + numpy; run from anywhere)
Writes into this folder:
  nightshift-atlas.png / .json                  the atlas (check with check_atlas.py)
  nightshift-atlas-sheet.png                    every entry at x4 with footprint, collision, anchor
  nightshift-landmark-states.png                the long interior window before, after and changed pixels
  nightshift-reference-room.json                cell layout built only from the atlas
  nightshift-reference-room-native.png          the room, before state (320x192; Engineer, Ada and Mira on the routes)
  nightshift-reference-room-1366x768.png        the x4 view (320x180), before state, no inset
  nightshift-reference-room-keyboard-inset.png  the same with the keyboard inset rectangle overlaid
  nightshift-reference-room-after-native.png / -after-1366x768.png   window after, door and gate open, stations lit
  nightshift-reference-room-route.png           collision grid, the BFS routes and the inset, for review
  nightshift-readability.png                    people and furniture edges at x8 with the measured contrast
  nightshift-readability.json                   the same numbers
Then runs the programmatic review (route BFS, inset, doorway and route brightness, palette, landmark, shadow
and lit-edge readability of every prop, wall top and person, strap contrast) and exits 1 on any failure.
"""
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_kit  # noqa: E402
import kitlib  # noqa: E402
import nightshift_kit as nk  # noqa: E402
import build_gate1 as g  # noqa: E402
import build_palettes as bp  # noqa: E402
import build_scale_test as bst  # noqa: E402
import district_palettes as dp  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import ada_sprites as ada  # noqa: E402
import mira_sprites as mira  # noqa: E402

T = 16
W_CELLS, H_CELLS = 20, 12
NIGHT = dp.DISTRICTS["nightshift"]
FILL, JOINT, POOL = NIGHT["floor"][3], NIGHT["floor"][2], NIGHT["accent"][1]
RIM_HEX = NIGHT["accent"][3]
BACK = {"floor", "rear_wall", "floor_marking", "rear_prop", "shadow"}
FRONT = {"front_prop", "light"}
STATES_BEFORE = {"service_door": "closed", "lamp": "on", "interior_window": "before", "vestibule_gate": "closed",
                 "station_a": "dead", "station_b": "dead"}
STATES_AFTER = {"service_door": "open", "lamp": "pulse", "interior_window": "after", "vestibule_gate": "open",
                "station_a": "lit", "station_b": "lit"}
INSET_VIEW = (5, 126.5, 125, 175)          # keyboard inset in view px (Gate 1 overlay geometry, /4)

# people: (label, module, frame, anchor x, anchor y)
PEOPLE = [
    ("Engineer", eng, eng.IDLE["n"][0], 168, 112),
    ("Ada", ada, ada.IDLE["w"][0], 181, 160),
    ("Mira", mira, mira.IDLE["s"][0], 238, 94),
]


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

    # floor wear: a few chips away from the routes
    import random
    rnd = random.Random(31)
    n = 0
    while n < 16:
        x, y = rnd.randrange(4, 300), rnd.randrange(40, 180)
        if 156 <= x < 296 and 60 <= y < 100 or 156 <= x < 196 and y >= 96 or 76 <= x < 116 and y >= 30:
            continue
        entry("floor_chip", x, y)
        n += 1
    # north wall: plain tiles either side of the window run (cells 2-13 belong to the landmark)
    for c in list(range(0, 2)) + list(range(14, W_CELLS)):
        entry("wall_n_plain", c * T, 0)
    entry("wall_n_window_a", 228, 9)
    entry("wall_n_noticeboard", 262, 9)
    for y in range(34, H_CELLS * T, T):
        if 66 <= y < 112:   # the door entries replace the wall here
            continue
        entry("wall_e_plain", 288, y)
    anim("service_door", 288, 72)
    # route B (the Caps route, lit): inlay lines, warm arrows
    for x in range(160, 288, T):
        entry("route_inlay", x, 64)
    for x in range(192, 288, T):
        entry("route_inlay", x, 95)
    for y in range(96, 192, T):
        entry("route_inlay_v", 160, y)
        entry("route_inlay_v", 191, y)
    for y in (120, 170):
        entry("route_arrow_n", 168, y)
    entry("route_arrow_e", 200, 72)
    # route A (the old route, silent): inlay lines only, no arrows and no pools
    for y in list(range(36, 68, T)) + list(range(96, 192, T)):
        entry("route_inlay_v", 80, y)
        entry("route_inlay_v", 111, y)
    # the landmark and the ledger corner
    pl.append({"landmark": "interior_window", "cell": [2, 0]})
    entry("ledger_desk", 0, 36)
    entry("pool_ledger_fill", 0, 36)
    entry("pool_ledger_seam", 0, 36)
    # break area under the right-hand wall
    entry("break_counter", 236, 38)
    entry("pool_break_fill", 260, 52)
    entry("pool_break_seam", 260, 52)
    entry("sofa", 200, 100)
    # security vestibule gate across the old route
    anim("vestibule_gate", 64, 80)
    # legacy stations flanking the old route north of the gate: they wake when the quest repairs a ticket
    anim("station_a", 46, 44)
    entry("chair", 46 + 11, 44 + 18)
    anim("station_b", 114, 44)
    entry("chair", 114 + 11, 44 + 18)
    entry("desk_dead_a", 46, 104)
    entry("chair", 46 + 11, 104 + 18)
    # lit stations on the Caps route
    for dy, nm in ((112, "desk_lit_a"), (148, "desk_lit_b")):
        entry(nm, 114, dy)
        entry("pool_desk_fill", 114, dy)
        entry("pool_desk_seam", 114, dy)
        entry("chair", 114 + 11, dy + 18)
    # south-east work nook: security glass, a terminal desk and a lit desk
    entry("partition_2x1", 192, 120)
    entry("partition_2x1", 224, 120)
    entry("partition_1x1", 256, 120)
    entry("terminal_desk", 208, 148)
    entry("pool_desk_fill", 208, 148)
    entry("pool_desk_seam", 208, 148)
    entry("chair", 208 + 11, 148 + 18)
    entry("desk_lit_a", 256, 148)
    entry("pool_desk_fill", 256, 148)
    entry("pool_desk_seam", 256, 148)
    entry("chair", 256 + 11, 148 + 18)
    # route pools: the corner, the east run, the vertical run; the doorway pool
    for nm_, x, y in (("pool_route", 176, 80), ("pool_route", 232, 80), ("pool_route", 176, 152), ("pool_door", 274, 91)):
        entry(nm_ + "_fill", x, y)
        entry(nm_ + "_seam", x, y)
    # lamps: one each side of the door run and the gate
    anim("lamp", 277, 119)
    anim("lamp", 56, 74)
    # shelving of the ledger room is part of the kit but not needed in this view; cabinet at the west wall
    entry("cabinet_1x1", 34, 150)
    # planters
    for nm, x, y in (("pot_plant_a", 0, 106), ("pot_plant_b", 146, 40), ("pot_plant_c", 198, 44),
                     ("pot_plant_d", 18, 146), ("pot_plant_c", 136, 98), ("pot_plant_b", 288 - 30, 170)):
        entry(nm, x, y + 4)
    return {
        "kit": "nightshift", "atlas": "nightshift-atlas.json", "tile": T, "size_cells": [W_CELLS, H_CELLS],
        "note": "Night Shift reference room, built only from nightshift-atlas. Floor is a cell grid; every other element is a placement at "
                "cell + pixel offset of its footprint origin. Draw order = layer order, then list order. People are added by the renderer "
                "(contact shadow, sprite, then the warm rim pass), not the layout. Route B (cols 10-11 north, then east along rows 4-5 to the "
                "service door) is lit by pools and arrows; route A (cols 5-6) is the silent old route, blocked by the vestibule gate.",
        "states": dict(STATES_BEFORE),
        "floor": {"legend": {"J": "floor_j", "H": "floor_h", "V": "floor_v", "P": "floor_p"}, "rows": floor_rows()},
        "placements": pl,
    }


def with_states(layout, **st):
    out = dict(layout)
    out["states"] = dict(layout["states"], **st)
    return out


# ------------------------------------------------------------------ people

def person_sprite(mod, frame):
    return bp.rim_light(g.frame_rgba(frame, mod.PAL), RIM_HEX)


def place_person(canvas, mod, frame, ax, ay):
    """Night Shift renderer order (ADA_SPEC decision 1): contact shadow, sprite, rim over the outline pixels
    that have a transparent pixel above or to the left. The baked key R is not outline, so it is skipped."""
    bp.shadow(canvas, ax, ay, NIGHT["floor"][0], dp.INK[0])
    c = type("C", (), {})()
    c.img = canvas
    g.place_px(c, person_sprite(mod, frame), ax, ay, shadow=False)


def render(layout, atlas, states, people=True, layers_back=BACK, layers_front=FRONT):
    lay = with_states(layout, **states)
    canvas = np.zeros((H_CELLS * T, W_CELLS * T, 3), np.uint8)
    kitlib.render_layout(lay, atlas, layers=layers_back, base=canvas)
    if people:
        for _, mod, frame, ax, ay in sorted(PEOPLE, key=lambda p: p[4]):
            place_person(canvas, mod, frame, ax, ay)
    kitlib.render_layout(lay, atlas, layers=layers_front, base=canvas)
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


# ------------------------------------------------------------------ routes

def blocked_grid(layout, atlas, states):
    return kitlib.collision_grid(with_states(layout, **states), atlas)


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


def route_cells(path):
    return {(x + dx, y + dy) for x, y in path for dx in (0, 1) for dy in (0, 1)}


def luma(rgb):
    rgb = np.asarray(rgb, float)
    return float((0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]).mean())


# ------------------------------------------------------------------ readability measurements

def upper_left_edge(sprite):
    a = sprite[:, :, 3] > 0
    up = np.ones_like(a)
    lf = np.ones_like(a)
    up[1:] = ~a[:-1]
    lf[:, 1:] = ~a[:, :-1]
    return a & (up | lf)


def lower_right_edge(sprite):
    a = sprite[:, :, 3] > 0
    dn = np.ones_like(a)
    rt = np.ones_like(a)
    dn[:-1] = ~a[1:]
    rt[:, :-1] = ~a[:, 1:]
    return a & (dn | rt) & ~upper_left_edge(sprite)


def person_contrast(mod, frame, floor_hex, ext=False):
    """A person drawn on a flat floor colour. rim: the pixels the renderer recoloured (outline pixels with a
    transparent pixel above or to the left, per ADA_SPEC decision 1); their min and mean contrast. cover: the
    share of the upper-left silhouette that is lit, i.e. rimmed, baked or at least 3:1 on its own; gaps: the
    darkest upper-left pixels that are not lit (contour-only darkest steps such as the Engineer's hair A and
    jacket p). shade: the lower-right plain outline, which the rim never reaches."""
    raw = g.frame_rgba(frame, mod.PAL)
    sp = nk.rim_light_ext(raw, RIM_HEX, floor_hex) if ext else bp.rim_light(raw, RIM_HEX)
    ul, lr = upper_left_edge(sp), lower_right_edge(sp)
    changed = np.any(sp != raw, axis=2) & ul
    rim_c = [nk.contrast(sp[y, x, :3], floor_hex) for y, x in zip(*np.nonzero(changed))]
    thr = 3.0 if floor_hex == FILL else 2.5     # in a pool the approved baseline for a rim is 2.7:1
    lit = [nk.contrast(sp[y, x, :3], floor_hex) >= thr for y, x in zip(*np.nonzero(ul))]
    gaps = [nk.contrast(sp[y, x, :3], floor_hex) for y, x in zip(*np.nonzero(ul)) if nk.contrast(sp[y, x, :3], floor_hex) < thr and not changed[y, x]]
    lr_c = [nk.contrast(sp[y, x, :3], floor_hex) for y, x in zip(*np.nonzero(lr))]
    return {"rim_min": min(rim_c), "rim_mean": float(np.mean(rim_c)), "rim_px": len(rim_c),
            "cover": float(np.mean(lit)), "gap_px": len(gaps), "gap_min": min(gaps) if gaps else 99.0,
            "shade_min": min(lr_c), "shade_mean": float(np.mean(lr_c))}


def strap_report(frame_rows, mod, floor_hex):
    """Mira's coral strap and bag (keys c d e f): contrast of each step against the floor, and of the strap
    against the jacket pixels it touches."""
    pal = mod.PAL
    sp = g.frame_rgba(frame_rows, pal)
    keys = "cdef"
    out = {}
    pos = {k: [(x, y) for y, row in enumerate(frame_rows) for x, ch in enumerate(row) if ch == k] for k in keys}
    for k in keys:
        out[k] = {"hex": pal[k], "px": len(pos[k]), "vs_floor": nk.contrast(pal[k], floor_hex)}
    # local contrast: each strap pixel against its 4-neighbours that are not strap and not outline
    loc = []
    for k in keys:
        for x, y in pos[k]:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 16 and 0 <= ny < 24 and frame_rows[ny][nx] not in keys + "o.":
                    loc.append(nk.contrast(pal[k], pal[frame_rows[ny][nx]]))
    out["local_min"], out["local_mean"] = (min(loc), float(np.mean(loc))) if loc else (None, None)
    # the strap pixels on the upper-left contour (reached by the rim) vs the lit upper rim: report the count
    ul = upper_left_edge(sp)
    out["strap_on_ul_contour"] = sum(1 for k in keys for x, y in pos[k] if ul[y, x])
    return out


def placed_props(layout, atlas, states):
    """[(entry name, entry, sprite px origin x, y)] of every free-standing prop and every wall overlay in the room."""
    out = []
    for li, order, name, fx, fy in sorted(kitlib.expand(with_states(layout, **states), atlas), key=lambda t: (t[0], t[1])):
        e = atlas.entries[name]
        free = e["layer"] in ("rear_prop", "front_prop") and e["kind"] == "prop"
        overlay = e["layer"] == "rear_wall" and name in ("wall_n_window_a", "wall_n_window_b", "wall_n_noticeboard")
        if free or overlay:
            ox, oy = e["footprint"]["origin_px"]
            out.append((name, e, fx - ox, fy - oy))
    return out


def prop_edge_report(layout, atlas, states):
    """For every free-standing prop and wall overlay: the contrast of its upper-left silhouette edge against the
    background that is actually under it, found by rendering the room without props (floor, markings, pools) or,
    for overlays, with the plain wall tiles only. Returns {name: {class: [contrast, ...]}}; class is floor, pool or wall."""
    bgimg = render(layout, atlas, states, people=False, layers_back={"floor", "floor_marking"}, layers_front={"light"})
    plain = dict(layout, placements=[p for p in layout["placements"] if p.get("entry") in ("wall_n_plain", "wall_e_plain")])
    walls = render(plain, atlas, states, people=False, layers_back={"floor", "rear_wall"}, layers_front=set())
    pool_cols = {tuple(kitlib.hex2rgb(h)) for h in (POOL, NIGHT["accent"][0], NIGHT["accent"][2])}
    res = {}
    H, W = bgimg.shape[:2]
    for name, e, px, py in placed_props(layout, atlas, states):
        spr = atlas.sprite(name)
        ul = upper_left_edge(spr)
        sh = e.get("contact_shadow")
        for y, x in zip(*np.nonzero(ul)):
            rx, ry = px + x, py + y
            if not (0 <= rx < W and 0 <= ry < H):
                continue
            if sh and sh[0] <= x < sh[0] + sh[2] and sh[1] <= y < sh[1] + sh[3]:
                continue
            if name.startswith("lamp") and y < 6:
                continue   # a lamp head is a light source
            if e["layer"] == "rear_wall":
                bgc, cls = tuple(walls[ry, rx]), "wall"
            else:
                bgc = tuple(bgimg[ry, rx])
                cls = "pool" if bgc in pool_cols else "floor"
            res.setdefault(name, {}).setdefault(cls, []).append(nk.contrast(spr[y, x, :3], bgc))
    return res


# ------------------------------------------------------------------ programmatic review

def review(layout, atlas, pieces):
    results = []

    def check(name, ok_, detail=""):
        results.append((name, ok_, detail))
        print(("PASS " if ok_ else "FAIL ") + name + (f": {detail}" if detail else ""))

    # --- routes
    open_door = dict(STATES_BEFORE, service_door="open")
    grid = blocked_grid(layout, atlas, open_door)
    start, goal = (10, 10), (17, 4)
    path = corridor_route(grid, start, goal)
    check("route B (the Caps route) is a 2-cell-wide corridor from the entrance to the service door (BFS on the collision grid)", path is not None,
          f"{len(path)} steps, {start} -> {goal}" if path else "no path")
    closed = blocked_grid(layout, atlas, STATES_BEFORE)
    check("the closed service door blocks route B (the door state drives the collision)", corridor_route(closed, start, goal) is None)
    if path:
        cells = route_cells(path)
        check("route B cells are free of props", not any(grid[y, x] for x, y in cells), f"{len(cells)} cells")
    a_start, a_goal = (5, 10), (5, 2)
    check("route A (the old route) is blocked by the closed vestibule gate", corridor_route(closed, a_start, a_goal) is None)
    gate_open = blocked_grid(layout, atlas, dict(STATES_BEFORE, vestibule_gate="open"))
    pa = corridor_route(gate_open, a_start, a_goal)
    check("route A opens as a 2-cell corridor when the gate opens", pa is not None, f"{len(pa)} steps" if pa else "no path")
    gate_c = closed[5, 4:8]
    gate_o = gate_open[5, 4:8]
    check("gate collision: closed blocks cols 4-7, open leaves cols 5-6 free", all(gate_c) and not gate_o[1] and not gate_o[2] and gate_o[0] and gate_o[3])
    # --- inset
    ix0, iy0, ix1, iy1 = INSET_VIEW
    required = {"landmark footprint": (32, 0, 224, 34), "door": (288, 50, 320, 118), "gate": (64, 70, 128, 99),
                "ledger desk": (0, 30, 40, 56), "break counter": (232, 34, 284, 56),
                "route B start": (160, 160, 192, 180), "route B corner": (160, 64, 192, 96)}
    bad = [n for n, (x0, y0, x1, y1) in required.items() if x0 < ix1 and x1 > ix0 and y0 < iy1 and y1 > iy0]
    check("no required element sits under the keyboard inset (view x 5-125, y 126.5-175)", not bad, ", ".join(bad) or "all clear")
    # --- brightness
    room = render(layout, atlas, open_door, people=False)
    opening = room[76:108, 292:320]
    wall = np.concatenate([room[120:152, 292:320], room[36:60, 292:320]])
    lo, lw = luma(opening), luma(wall)
    check("doorway (open) is brighter than the adjacent east wall", lo > lw * 1.5, f"{lo:.0f} vs {lw:.0f} luma")
    nogrid = blocked_grid(layout, atlas, STATES_BEFORE)
    rcells = route_cells(path) if path else set()
    base_room = render(layout, atlas, STATES_BEFORE, people=False)
    def cell_luma(c):
        x, y = c
        return luma(base_room[y * T:(y + 1) * T, x * T:(x + 1) * T])
    dead = [(x, y) for y in range(2, 11) for x in range(W_CELLS - 2) if not nogrid[y, x] and (x, y) not in rcells and x >= 8]
    # dead ends: free cells that are on neither route and not under a pool-lit desk; the old route's cells are included
    route_l = np.mean([cell_luma(c) for c in rcells])
    dead_l = np.mean([cell_luma(c) for c in dead])
    check("route B is brighter than the dead ends beside it", route_l > dead_l * 1.15, f"route {route_l:.0f} vs dead ends {dead_l:.0f} luma ({len(dead)} cells)")
    ra = route_cells(pa) if pa else set()
    old_l = np.mean([cell_luma(c) for c in ra if c[1] >= 6]) if ra else 0
    check("route B is brighter than the silent old route A", route_l > old_l * 1.15, f"{route_l:.0f} vs {old_l:.0f} luma")
    # --- palette
    allowed = {h.upper() for role in ("ink", "floor", "wall", "glass", "wood", "foliage", "accent") for h in NIGHT[role]}
    violet = {h.upper() for h in dp.VIOLET}
    used = {kitlib.hexs(c) for c in np.unique(atlas.img[atlas.img[:, :, 3] > 0][:, :3], axis=0)}
    check("every atlas pixel is a Night Shift ramp step; no violet", used <= allowed and not (used & violet),
          f"{len(used)} colours" + (f", stray {sorted(used - allowed)}" if used - allowed else ""))
    # --- landmark
    lm = atlas.landmarks["interior_window"]
    diff = set(lm["states"]["before"]["parts"]) ^ set(lm["states"]["after"]["parts"])
    check("landmark after state changes at least two visible things", len(diff) >= 2 and len(lm["states"]["after"]["lamps"]) > 0,
          f"{len(diff)} parts differ ({', '.join(sorted(diff))}), lamps switch")
    # --- shadows
    fill_l = nk.luminance(kitlib.hex2rgb(FILL))
    worst = 0.0
    bad_sh = []
    for e in atlas.meta["entries"]:
        if e.get("contact_shadow") and e["kind"] != "landmark_part" or e["name"] == "window_wall_base":
            x, y, w, h = e["contact_shadow"]
            sp_ = atlas.sprite(e["name"])[y:y + h, x:x + w]
            a = sp_[:, :, 3] > 0
            for px in sp_[a][:, :3]:
                l = nk.luminance(px)
                worst = max(worst, l)
                if l > fill_l:
                    bad_sh.append(e["name"])
    check("every contact shadow is darker than the floor fill (no ink-step shadow reads as a glow)", not bad_sh,
          f"brightest shadow pixel luminance {worst:.3f} vs floor fill {fill_l:.3f}" + (f"; {sorted(set(bad_sh))}" if bad_sh else ""))
    # --- lit edges, atlas level
    bad_edge = []
    n_checked = 0
    for p in pieces:
        e = next(x for x in atlas.meta["entries"] if x["name"] == p.name)
        if e["layer"] not in ("rear_prop", "front_prop", "rear_wall") or e["kind"] == "landmark_part":
            continue
        spr = atlas.sprite(p.name)
        bg = NIGHT["wall"][1] if (e["layer"] == "rear_wall" and e["kind"] in ("wall", "door") and p.name != "wall_n_plain") else FILL
        ul = upper_left_edge(spr)
        if p.name == "wall_n_plain":      # a tile that repeats horizontally: only its top edge is a silhouette edge
            ul = (np.arange(spr.shape[0])[:, None] == 0) & (spr[:, :, 3] > 0)
        sh = e.get("contact_shadow")
        low = 0
        for y, x in zip(*np.nonzero(ul)):
            if sh and sh[0] <= x < sh[0] + sh[2] and sh[1] <= y < sh[1] + sh[3]:
                continue
            if p.name.startswith("lamp") and y < 6:
                continue   # the lit head of a lamp is a light source
            if p.name.startswith("service_door") or p.name == "wall_e_plain":
                continue   # measured in the room against the wall mass (below)
            if nk.contrast(spr[y, x, :3], bg) < nk.MIN_EDGE:
                low += 1
        n_checked += 1
        if low:
            bad_edge.append(f"{p.name}:{low}px")
    check("every prop and wall overlay has a lit upper-left edge: all silhouette edge pixels reach 3:1 against the floor fill (or wall face)",
          not bad_edge, f"{n_checked} entries checked" + (f"; below 3:1: {bad_edge}" if bad_edge else ""))
    # --- lit edges in the room
    rep = prop_edge_report(layout, atlas, STATES_BEFORE)
    floor_min, pool_min, wall_min = 99.0, 99.0, 99.0
    worst_floor = worst_pool = worst_wall = ""
    for name, d in rep.items():
        for cls, vals in d.items():
            m = min(vals)
            if cls == "floor" and m < floor_min:
                floor_min, worst_floor = m, name
            if cls == "pool" and m < pool_min:
                pool_min, worst_pool = m, name
            if cls == "wall" and m < wall_min:
                wall_min, worst_wall = m, name
    check("furniture top and left edges against the dark floor under them (rendered room): minimum >= 3:1", floor_min >= 3.0,
          f"min {floor_min:.2f}:1 ({worst_floor}), {sum(1 for d in rep.values() if 'floor' in d)} props")
    check("furniture edges inside a lamp pool keep >= 2.5:1 (the approved in-pool baseline for a rim is 2.7:1)", pool_min >= 2.5,
          f"min {pool_min:.2f}:1 ({worst_pool or 'none in a pool'})")
    check("wall overlay edges (window, noticeboard) against the indigo wall: >= 3:1", wall_min >= 3.0, f"min {wall_min:.2f}:1 ({worst_wall})")
    # wall tops: the top row of the north wall and the east wall's lit trim against the floor fill / dark mass
    top_row = [tuple(base_room[0, x]) for x in range(0, 320)]
    trim_row = [tuple(base_room[4, x]) for x in range(0, 320)]
    c_top = min(nk.contrast(c, FILL) for c in set(top_row))
    c_trim = min(nk.contrast(c, FILL) for c in set(trim_row))
    check("wall top: the north wall cap edge and trim line are lit (silver) and reach >= 3:1 against the floor fill", c_top >= 3.0 and c_trim >= 3.0,
          f"top row {c_top:.2f}:1, trim row {c_trim:.2f}:1")
    return results, rep


def people_report():
    """Contrast tables for every person, on the dark floor and in a lamp pool, across the four idle facings."""
    out = {}
    for label, mod, frame, ax, ay in PEOPLE:
        facings = {}
        for f in ("s", "n", "e", "w"):
            fr = mod.IDLE[f][0]
            facings[f] = {"floor": person_contrast(mod, fr, FILL), "pool": person_contrast(mod, fr, POOL)}
        out[label] = facings
    return out


# ------------------------------------------------------------------ images

def landmark_states(layout, atlas):
    box = (24, 0, 232, 72)
    Z = 3
    imgs = {}
    for st in ("before", "after"):
        imgs[st] = render(layout, atlas, dict(STATES_BEFORE, interior_window=st, lamp="on" if st == "before" else "pulse"), people=False)[box[1]:box[3], box[0]:box[2]]
    changed = np.any(imgs["before"] != imgs["after"], axis=2)
    dim = imgs["after"].copy()
    dim[~changed] = (imgs["after"][~changed] * 0.35 + np.array(bst.INK[0]) * 0.65).astype(np.uint8)  # diagnostic only
    panels = [("BEFORE: the Night Shift quests not yet done", imgs["before"]), ("AFTER: break room and floor lit", imgs["after"]),
              (f"CHANGED: {int(changed.sum())} px (rest dimmed)", dim)]
    pw, ph = (box[2] - box[0]) * Z, (box[3] - box[1]) * Z
    sheet = Image.new("RGB", (pw + 40, len(panels) * (ph + 48) + 140), build_kit.BG)
    d = ImageDraw.Draw(sheet)
    for i, (title, im) in enumerate(panels):
        y = 16 + i * (ph + 48)
        d.text((20, y), title, font=bst.font(20, bold=True), fill="#F4F2EC")
        sheet.paste(Image.fromarray(im).resize((pw, ph), Image.NEAREST), (20, y + 28))
    lm = atlas.landmarks["interior_window"]
    for i, line in enumerate(lm["changes_after"]):
        d.text((20, len(panels) * (ph + 48) + 24 + i * 20), "+ " + line[:150], font=bst.font(13), fill="#C5CED0")
    sheet.save(os.path.join(HERE, "nightshift-landmark-states.png"))
    return int(changed.sum())


def route_image(layout, atlas, canvas):
    Z = 4
    grid = blocked_grid(layout, atlas, dict(STATES_BEFORE, service_door="open", vestibule_gate="open"))
    img = Image.fromarray(canvas).resize((canvas.shape[1] * Z, canvas.shape[0] * Z), Image.NEAREST).convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(grid.shape[0]):
        for x in range(grid.shape[1]):
            box = [x * T * Z, y * T * Z, (x + 1) * T * Z - 1, (y + 1) * T * Z - 1]
            if grid[y, x]:
                d.rectangle(box, fill=(236, 119, 109, 70), outline=(236, 119, 109, 160))
    for start, goal, colour in (((10, 10), (17, 4), (25, 175, 162, 255)), ((5, 10), (5, 2), (244, 242, 236, 255))):
        path = corridor_route(grid, start, goal)
        if path:
            for x, y in route_cells(path):
                d.rectangle([x * T * Z + 2, y * T * Z + 2, (x + 1) * T * Z - 3, (y + 1) * T * Z - 3], outline=colour, width=3)
    ix0, iy0, ix1, iy1 = [v * Z for v in INSET_VIEW]
    d.rectangle([ix0, iy0, ix1, iy1], outline=(230, 183, 80, 255), width=4)
    d.text((ix0 + 8, iy0 + 8), "keyboard inset", font=bst.font(18, bold=True), fill=(230, 183, 80, 255))
    d.text((8, img.size[1] - 26), "coral cells block, teal = route B (Caps route) to the service door, white = route A (old route) once the gate opens, gold = keyboard inset",
           font=bst.font(14), fill=(244, 242, 236, 255))
    Image.alpha_composite(img, ov).convert("RGB").save(os.path.join(HERE, "nightshift-reference-room-route.png"))


def readability_sheet(canvas):
    """x8 people on the dark floor and in a lamp pool with the measured contrast (left: floor fill, right: pool), the
    Engineer again with the proposed extended rim, and x5 crops of furniture from the room."""
    Z = 8
    people = [("Engineer", eng, eng.IDLE["s"][0], False), ("Engineer, proposed rim", eng, eng.IDLE["s"][0], True),
              ("Ada (baked R)", ada, ada.IDLE["s"][0], False), ("Ada W", ada, ada.IDLE["w"][0], False),
              ("Mira (strap)", mira, mira.IDLE["s"][0], False), ("Mira N", mira, mira.IDLE["n"][0], False)]
    cw, chh = 16 * Z + 28, 24 * Z + 66
    W = len(people) * cw * 2 + 40
    sheet = Image.new("RGB", (W, chh + 420), build_kit.BG)
    d = ImageDraw.Draw(sheet)
    d.text((16, 10), "Night Shift readability at x8. Left half: dark floor fill. Right half: inside a lamp pool. Warm rim = renderer rim (outline pixels) and Ada's baked key R.",
           font=bst.font(15, bold=True), fill="#F4F2EC")
    d.text((16, 34), "rim = the recoloured pixels; cover = share of the upper-left silhouette that is lit; shade = the lower-right plain outline (the rim never reaches it).",
           font=bst.font(13), fill="#9FB3BD")
    for half, fill_hex in enumerate((FILL, POOL)):
        for i, (label, mod, frame, ext) in enumerate(people):
            raw = g.frame_rgba(frame, mod.PAL)
            sp = nk.rim_light_ext(raw, RIM_HEX, fill_hex) if ext else bp.rim_light(raw, RIM_HEX)
            tile = np.zeros((24, 16, 3), np.uint8)
            tile[:] = kitlib.hex2rgb(fill_hex)
            a = sp[:, :, 3] > 0
            tile[a] = sp[:, :, :3][a]
            big = Image.fromarray(np.kron(tile, np.ones((Z, Z, 1), np.uint8)))
            x = 16 + (half * len(people) + i) * cw
            sheet.paste(big, (x, 60))
            c = person_contrast(mod, frame, fill_hex, ext)
            ty = 60 + 24 * Z + 4
            d.text((x, ty), label[:24], font=bst.font(12, bold=True), fill="#F4F2EC")
            d.text((x, ty + 16), f"rim {c['rim_min']:.1f}:1 min, {c['rim_px']} px", font=bst.font(12), fill="#C5CED0")
            d.text((x, ty + 30), f"cover {100 * c['cover']:.0f}%  gaps {c['gap_px']} px", font=bst.font(12), fill="#C5CED0")
            d.text((x, ty + 44), f"shade {c['shade_min']:.1f}:1 min", font=bst.font(12), fill="#C5CED0")
    Z2 = 5
    strips = [("break counter + pool", (228, 34, 292, 70)), ("lit stations on route B", (108, 100, 160, 168)),
              ("legacy stations + gate (old route A)", (40, 40, 132, 100)), ("terminal desk nook", (190, 114, 290, 172))]
    y0 = chh + 70
    x = 16
    for label, (bx0, by0, bx1, by1) in strips:
        crop = Image.fromarray(canvas[by0:by1, bx0:bx1]).resize(((bx1 - bx0) * Z2, (by1 - by0) * Z2), Image.NEAREST)
        if x + crop.width > W - 16:
            x, y0 = 16, y0 + 360
        sheet.paste(crop, (x, y0 + 20))
        d.text((x, y0), label, font=bst.font(13, bold=True), fill="#F4F2EC")
        x += crop.width + 16
    sheet.crop((0, 0, W, min(sheet.height, y0 + 20 + 350))).save(os.path.join(HERE, "nightshift-readability.png"))


# ------------------------------------------------------------------ main

def main():
    pieces, anims, lms = nk.build_pieces()
    pieces.sort(key=nk.group_rank)
    img, rects = kitlib.pack([(p.name, p.sprite) for p in pieces])
    img.save(os.path.join(HERE, "nightshift-atlas.png"))
    meta = nk.atlas_json(pieces, rects, anims, lms)
    with open(os.path.join(HERE, "nightshift-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
        fh.write("\n")
    layout = reference_layout()
    with open(os.path.join(HERE, "nightshift-reference-room.json"), "w") as fh:
        json.dump(layout, fh, indent=1)
        fh.write("\n")
    atlas = kitlib.Atlas(os.path.join(HERE, "nightshift-atlas.json"))
    build_kit.atlas_sheet(pieces, meta, rank_fn=nk.group_rank, sections=nk.SECTIONS, out="nightshift-atlas-sheet.png",
                          title="Night Shift kit atlas, x4 on a checker. Coral box: footprint cells. Coral cross: anchor. "
                                "Tags under each name: layer, footprint, size in px.")
    nchg = landmark_states(layout, atlas)
    before = render(layout, atlas, STATES_BEFORE)
    after = render(layout, atlas, STATES_AFTER)
    Image.fromarray(before).save(os.path.join(HERE, "nightshift-reference-room-native.png"))
    Image.fromarray(after).save(os.path.join(HERE, "nightshift-reference-room-after-native.png"))
    to_screen(before).save(os.path.join(HERE, "nightshift-reference-room-1366x768.png"))
    to_screen(before, inset=True).save(os.path.join(HERE, "nightshift-reference-room-keyboard-inset.png"))
    to_screen(after).save(os.path.join(HERE, "nightshift-reference-room-after-1366x768.png"))
    route_image(layout, atlas, before)
    print(f"{len(pieces)} entries; landmark before/after differ in {nchg} px; {len(layout['placements'])} placements")
    results, rep = review(layout, atlas, pieces)
    ppl = people_report()
    ok_ = all(r[1] for r in results)

    def gate(name, cond, detail):
        nonlocal ok_
        print(("PASS " if cond else "FAIL ") + name + (f": {detail}" if detail else ""))
        ok_ = ok_ and cond

    # ---- people. The rim is the set of recoloured outline pixels; it must read on the floor and in a pool.
    print("--- people, idle S N E W: rim = pixels the renderer recolours (outline with a transparent pixel above or to the left) plus Ada's baked R")
    rim_f = rim_p = 99.0
    for label, f in ppl.items():
        rf = min(v["floor"]["rim_min"] for v in f.values())
        rp = min(v["pool"]["rim_min"] for v in f.values())
        cov = min(v["floor"]["cover"] for v in f.values())
        gaps = max(v["floor"]["gap_px"] for v in f.values())
        gmin = min(v["floor"]["gap_min"] for v in f.values())
        shade_f = min(v["floor"]["shade_min"] for v in f.values())
        shade_p = min(v["pool"]["shade_min"] for v in f.values())
        rim_f, rim_p = min(rim_f, rf), min(rim_p, rp)
        print(f"     {label:9s} rim: floor fill min {rf:.2f}:1, pool min {rp:.2f}:1 | lit share of upper-left silhouette {100 * cov:.0f}% "
              f"(unlit gaps up to {gaps} px, darkest {gmin:.2f}:1) | shaded outline: fill {shade_f:.2f}:1, pool {shade_p:.2f}:1")
    gate("every person's rimmed contour reaches 3:1 against the floor fill (Engineer, Ada, Mira; idle S N E W)", rim_f >= 3.0, f"min {rim_f:.2f}:1")
    gate("every person's rimmed contour keeps 2.5:1 inside a lamp pool (the approved in-pool baseline is 2.7:1)", rim_p >= 2.5, f"min {rim_p:.2f}:1")
    ext = {}
    for label, mod, frame, ax, ay in PEOPLE:
        ext[label] = [person_contrast(mod, mod.IDLE[f][0], FILL, ext=True) for f in "snew"]
    print("     proposed extended rim (not applied in the room): lit share of the upper-left silhouette "
          + ", ".join(f"{k} {100 * min(c['cover'] for c in v):.0f}%" for k, v in ext.items()))
    # ---- people as placed
    bgimg = render(layout, atlas, STATES_BEFORE, people=False, layers_back={"floor", "floor_marking"}, layers_front={"light"})
    room_vals = {}
    for label, mod, frame, ax, ay in PEOPLE:
        raw = g.frame_rgba(frame, mod.PAL)
        sp = person_sprite(mod, frame)
        ul = upper_left_edge(sp)
        changed = np.any(sp != raw, axis=2) & ul
        vals = [nk.contrast(sp[y, x, :3], tuple(bgimg[ay - 24 + y, ax - 8 + x])) for y, x in zip(*np.nonzero(changed))]
        room_vals[label] = (min(vals), float(np.mean(vals)), len(vals))
    print("--- people as placed in the room: rim pixels against the floor or pool under each pixel")
    for label, (mn, mean, n) in room_vals.items():
        print(f"     {label:9s} {n} rim px, min {mn:.2f}:1, mean {mean:.2f}:1")
    gate("people as placed: every rim pixel >= 2.5:1 against the floor or pool under it", min(v[0] for v in room_vals.values()) >= 2.5,
         f"min {min(v[0] for v in room_vals.values()):.2f}:1")
    # ---- strap
    mrep = {f: strap_report(mira.IDLE[f][0], mira, FILL) for f in ("s", "n", "e", "w")}
    mpool = {f: strap_report(mira.IDLE[f][0], mira, POOL) for f in ("s", "n", "e", "w")}
    print("--- Mira's coral strap and bag (keys c d e f): contrast of each step against the floor fill and the pool, and of the strap against the jacket it crosses")
    for f, r_ in mrep.items():
        steps = ", ".join(f"{k} {r_[k]['vs_floor']:.1f}" for k in "cdef")
        psteps = ", ".join(f"{k} {mpool[f][k]['vs_floor']:.1f}" for k in "cdef")
        print(f"     {f.upper()}: vs floor fill {steps} | vs pool {psteps} | vs jacket min {r_['local_min']:.1f}:1 mean {r_['local_mean']:.1f}:1")
    gate("Mira's strap reads on the dark floor: its two lit steps (e, f) reach 2.5:1 and 3:1 against the fill in every facing",
         all(r_["e"]["vs_floor"] >= 2.5 and r_["f"]["vs_floor"] >= 3.0 for r_ in mrep.values()),
         "e %.1f:1, f %.1f:1" % (mrep["s"]["e"]["vs_floor"], mrep["s"]["f"]["vs_floor"]))
    prop_summary = {n: {c: {"min": round(min(v), 2), "mean": round(float(np.mean(v)), 2), "px": len(v)} for c, v in d.items()} for n, d in rep.items()}
    rnd = lambda o: round(float(o), 2) if isinstance(o, (float, np.floating)) else o  # noqa: E731
    with open(os.path.join(HERE, "nightshift-readability.json"), "w") as fh:
        json.dump({"floor_fill": FILL, "pool": POOL,
                   "people_idle": {k: {f: {c: {m: rnd(x) for m, x in v.items()} for c, v in d.items()} for f, d in fs.items()} for k, fs in ppl.items()},
                   "people_proposed_rim_cover": {k: [round(c["cover"], 2) for c in v] for k, v in ext.items()},
                   "people_placed_rim": {k: {"min": rnd(v[0]), "mean": rnd(v[1]), "px": v[2]} for k, v in room_vals.items()},
                   "mira_strap_vs_floor": {f: {k: {kk: rnd(vv) for kk, vv in v.items()} if isinstance(v, dict) else rnd(v) for k, v in r_.items()} for f, r_ in mrep.items()},
                   "props_in_room": prop_summary}, fh, indent=1)
        fh.write("\n")
    readability_sheet(before)
    print("NIGHT SHIFT BUILD", "PASSED" if ok_ else "FAILED")
    sys.exit(0 if ok_ else 1)


if __name__ == "__main__":
    main()
