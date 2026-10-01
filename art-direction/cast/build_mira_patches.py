"""Build the review outputs for Mira's six patch states (mira_patches.py).

Run: python3 build_mira_patches.py   (needs Pillow + numpy)
Writes into this folder:
  mira-patches-sheet.png   x4 strips of states 0-6 for S, E, N and W, then the portrait at x4
  mira-patches-atlas.png   native atlas: one block per state (0..6), each laid out like mira-atlas.png
  mira-patches-atlas.json  frame size, block layout and the patch table
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("gate1", "scale-test", "portraits"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import build_gate1 as g  # noqa: E402
import build_scale_test as bst  # noqa: E402
import mira_patches as mp  # noqa: E402
import portrait_mira as pm  # noqa: E402

Z = 4
FLOOR = tuple(bst.STONE[2]) + (255,)


def sprite(frame):
    return Image.fromarray(g.frame_rgba(frame, mp.PAL), "RGBA")


def portrait(grid):
    import build_portraits as bp
    return bp.grid_img(grid, pm.PATCH_PAL)


def cell(im, z, bg=FLOOR):
    base = Image.new("RGBA", im.size, bg)
    base.alpha_composite(im)
    return base.resize((im.width * z, im.height * z), Image.NEAREST)


def build_sheet():
    f_t, f_h, f_s = bst.font(20, bold=True), bst.font(15, bold=True), bst.font(12)
    sw, sh = 16 * Z, 24 * Z
    pw = 48 * Z
    gap = 14
    W = 24 + 70 + 7 * (pw + gap) + 24
    H = 70 + 4 * (sh + 40) + 60 + (pw + 90) + 190 + 2 * (11 * 8 + 40) + 60
    sheet = Image.new("RGB", (W, H), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), "Mira's six patches · states 0-6 · x4 · each state adds one patch (cumulative)",
           font=f_t, fill="#F4F2EC")
    y = 60
    for f in "sewn":
        d.text((24, y + 36), f.upper(), font=f_h, fill="#E1AC62")
        for k in range(7):
            idle, _ = mp.state_frames(k)
            x = 24 + 70 + k * (pw + gap)
            sheet.paste(cell(sprite(idle[f][0]), Z).convert("RGB"), (x + (pw - sw) // 2, y))
            if f == "s":
                label = "state 0 (approved)" if k == 0 else f"{k}  {mp.PATCHES[k - 1]['name']}"
                d.text((x, y + sh + 6), label, font=f_s, fill="#C7B7A0")
        y += sh + 40
    y += 16
    d.text((24, y), "Portrait (pleased) at x4: the same colours as large icons", font=f_h, fill="#E1AC62")
    y += 28
    for k in range(7):
        x = 24 + 70 + k * (pw + gap)
        grid = pm.with_patches(pm.EXPRESSIONS["pleased"], k)
        sheet.paste(cell(portrait(grid), Z, tuple(bst.hx("#343650")) + (255,)).convert("RGB"), (x, y))
        d.text((x, y + pw + 6), "state 0" if k == 0 else f"{k}  {mp.PORTRAIT_PATCHES[k - 1]['icon'].split(':')[0]}", font=f_s, fill="#C7B7A0")
    y += pw + 40
    d.text((24, y), "Jacket close-up at x8 (diagnosis; rows 9-19 of idle frame 0), S then E", font=f_h, fill="#E1AC62")
    y += 28
    for f in "se":
        for k in range(7):
            idle, _ = mp.state_frames(k)
            crop = sprite(idle[f][0]).crop((0, 9, 16, 20))
            sheet.paste(cell(crop, 8).convert("RGB"), (24 + 70 + k * (pw + gap) + 30, y))
        d.text((24, y + 40), f.upper(), font=f_h, fill="#E1AC62")
        y += 11 * 8 + 40
    for n, p in enumerate(mp.PATCHES, 1):
        world_px = max(len(v) for v in p["world"].values())
        d.text((24, y + (n - 1) * 24),
               f"{n}  {p['name']}: earned on {p['earned']}, {p['district']}. World: {p['design']}, {world_px} px. Portrait: {mp.PORTRAIT_PATCHES[n - 1]['icon']}.",
               font=f_s, fill="#C7B7A0")
    sheet.save(os.path.join(HERE, "mira-patches-sheet.png"))


def build_atlas():
    block_w, block_h = 16 * 4, 24 * 8
    atlas = Image.new("RGBA", (block_w * 7, block_h), (0, 0, 0, 0))
    for k in range(7):
        idle, walk = mp.state_frames(k)
        rows = [idle[f] for f in "snew"] + [walk[f] for f in "snew"]
        for r, frames in enumerate(rows):
            for i, fr in enumerate(frames):
                atlas.paste(sprite(fr), (k * block_w + i * 16, r * 24))
    atlas.save(os.path.join(HERE, "mira-patches-atlas.png"))
    meta = {
        "frame": {"w": 16, "h": 24},
        "anchor": {"name": "feet_bc", "x": 8, "y": 24},
        "states": 7,
        "state_block": {"w": block_w, "h": block_h, "x_of_state_k": "k * 64"},
        "block_layout": "rows S N E W idle (2 frames), then S N E W walk (4 frames), exactly as mira-atlas.png",
        "state_meaning": "state k wears patches 1..k; state 0 equals mira-atlas.png",
        "patches": [{"n": n, "id": p["id"], "name": p["name"], "earned_on": p["earned"], "district": p["district"],
                     "design": p["design"], "portrait_icon": mp.PORTRAIT_PATCHES[n - 1]["icon"]} for n, p in enumerate(mp.PATCHES, 1)],
        "colour_keys": mp.PATCH_PAL,
    }
    with open(os.path.join(HERE, "mira-patches-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=2)


if __name__ == "__main__":
    build_sheet()
    build_atlas()
    print("built mira-patches-sheet.png, mira-patches-atlas.png/json")
