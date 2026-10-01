"""Build the Pace signage outputs.

Run: python3 build_pace.py   (needs Pillow + numpy)
Writes into this folder:
  pace-sheet.png               every piece at x8, x2 and x1 on its own background
  pace-atlas.png / .json       packed native atlas with footprint, origin, layer, collision
  pace-in-room-1366x768.png    the approved review room at x4 with the signage placed
  pace-in-room-native.png      the same room at 320x180

The in-room render reuses build_gate1.scene() and the approved environment module
unchanged. Pace's pieces are drawn by wrapping three environment draw steps (north
wall, route, garden) so they land on the right layer: wall signs with the walls,
floor inlays after the route, the directory with the rear props, all before the actors.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("gate1", "cast", "scale-test"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
sys.path.insert(0, HERE)
import build_gate1 as g  # noqa: E402
import build_scale_test as bst  # noqa: E402
import environment as env  # noqa: E402
import pace_art as pa  # noqa: E402

# Placements in the review room, in logical pixels (top-left of each sprite).
# The north wall is all glass bays and the HUD and Ivo's marker cover its left half, so the
# wall sign goes on the east wall below the Records door, right of the lamp. The hanging sign
# has no clear bay in this room and is shown on the sheet and in the atlas only.
WALL_PLACEMENTS = [("pace_logo_plate_1x1", 297, 124)]
FLOOR_PLACEMENTS = [("pace_floor_arrow_e", 224, 83)]
PROP_PLACEMENTS = [("pace_directory", 210, 42)]


def stamp(img, sprite, x, y):
    h, w = sprite.shape[:2]
    m = sprite[:, :, 3] > 0
    img[y:y + h, x:x + w][m] = sprite[:, :, :3][m]


def install_hooks(pieces):
    orig = {n: getattr(env, n) for n in ("east_wall", "route", "garden")}

    def hook(name, placements):
        def wrapped(r, *a, **k):
            orig[name](r, *a, **k)
            for piece, x, y in placements:
                stamp(r.img, pieces[piece], x, y)
        setattr(env, name, wrapped)

    hook("east_wall", WALL_PLACEMENTS)
    hook("route", FLOOR_PLACEMENTS)
    hook("garden", PROP_PLACEMENTS)
    return orig


def remove_hooks(orig):
    for n, f in orig.items():
        setattr(env, n, f)


def hexc(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def build_sheet(pieces):
    names = list(pieces)
    cols = 3
    cell_w = 32 * 8 + 24
    row_h = []
    rows = [names[i:i + cols] for i in range(0, len(names), cols)]
    for r in rows:
        row_h.append(max(pieces[n].shape[0] * 10 for n in r) + 84)
    sheet = Image.new("RGB", (cols * cell_w + 24, sum(row_h) + 70), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), "Pace signage · x8 (diagnosis, cell grid in ink) · x2 · x1 native · wall pieces on wall stone, floor pieces on floor stone",
           font=bst.font(18, bold=True), fill="#F4F2EC")
    y = 56
    for r, rh in zip(rows, row_h):
        for i, n in enumerate(r):
            a = pieces[n]
            h, w = a.shape[:2]
            gx, gy = 24 + i * cell_w, y
            bg = hexc(pa.FLOOR if pa.PIECES[n]["bg"] == "floor" else pa.WALL)
            sp = Image.fromarray(a, "RGBA")
            for sc, ox, oy in ((8, 0, 0), (2, 0, h * 8 + 12), (1, w * 2 + 16, h * 8 + 12)):
                tile = Image.new("RGBA", (w * sc, h * sc), bg + (255,))
                tile.alpha_composite(sp.resize((w * sc, h * sc), Image.NEAREST))
                sheet.paste(tile.convert("RGB"), (gx + ox, gy + oy))
            # 16 px cell lines over the x8 view, on the origin cell of the footprint.
            ox_f, oy_f = pa.PIECES[n]["origin"]
            for cx in range(0, w + 1, 16):
                d.line([(gx + cx * 8, gy), (gx + cx * 8, gy + h * 8)], fill="#535971")
            for cy in range(0, h + 1, 16):
                d.line([(gx, gy + cy * 8), (gx + w * 8, gy + cy * 8)], fill="#535971")
            d.text((gx, gy + h * 8 + 12 + 2 * h + 6), f"{n}  {w}x{h}", font=bst.font(14, bold=True), fill="#E6B750")
        y += rh
    sheet.save(os.path.join(HERE, "pace-sheet.png"))


def build_atlas(pieces):
    pad = 2
    # Shelf pack: tallest first, rows up to 192 px wide.
    order = sorted(pieces, key=lambda n: (-pieces[n].shape[0], n))
    x = y = row_h = 0
    pos = {}
    max_w = 192
    for n in order:
        h, w = pieces[n].shape[:2]
        if x + w > max_w:
            x, y, row_h = 0, y + row_h + pad, 0
        pos[n] = (x, y)
        x += w + pad
        row_h = max(row_h, h)
    atlas = Image.new("RGBA", (max_w, y + row_h), (0, 0, 0, 0))
    entries = {}
    for n in order:
        a = pieces[n]
        h, w = a.shape[:2]
        atlas.paste(Image.fromarray(a, "RGBA"), pos[n])
        s = pa.PIECES[n]
        fw, fh = s["footprint"]
        ox, oy = s["origin"]
        entries[n] = {
            "rect": [pos[n][0], pos[n][1], w, h],
            "footprint_cells": [fw, fh],
            "origin_px": [ox, oy],
            "anchor": {"name": "footprint_bl", "x": ox, "y": min(oy + fh * 16, h),
                       "note": "bottom-left pixel corner of the footprint, clamped to the sprite bottom"},
            "layer": s["layer"],
            "collision_cells": [list(c) for c in s["collision"]],
            "state": s["state"],
            "baked_shadow": n in ("pace_directory", "pace_directory_repeat", "pace_directory_optional")
                            or s["layer"] == "wall" and n != "pace_icon_16" and n != "pace_icon_8",
            "note": s["note"],
        }
    atlas.save(os.path.join(HERE, "pace-atlas.png"))
    meta = {
        "status": "Candidate, pending director review",
        "tile": 16,
        "placement": "sprite top-left = footprint cell top-left minus origin_px",
        "layers": "floor -> wall and floor-marking -> rear-prop -> contact shadows -> actors -> front props",
        "states": {"default": "orderly bars", "repeat": "errors accumulating: bars repeat at one length",
                   "optional": "epilogue: unlit stone, optional guidance"},
        "entries": entries,
    }
    with open(os.path.join(HERE, "pace-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=2)


def build_room(pieces):
    orig = install_hooks(pieces)
    try:
        c = g.scene(g.eng.IDLE["s"][0], g.START_X + 32, g.ROUTE_Y)
        native, screen = g.to_screen(c)
    finally:
        remove_hooks(orig)
    native.save(os.path.join(HERE, "pace-in-room-native.png"))
    screen.save(os.path.join(HERE, "pace-in-room-1366x768.png"))


def build():
    pieces = pa.build_all()
    build_sheet(pieces)
    build_atlas(pieces)
    build_room(pieces)


if __name__ == "__main__":
    build()
