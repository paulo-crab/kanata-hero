"""Build review outputs for a cast sprite module.

Run: python3 build_cast.py ivo   (needs Pillow + numpy)
Writes <name>-sheet.png (every frame at x8, x2, x1 with the anchor marked),
<name>-atlas.png/.json (rows S N E W idle, then S N E W walk) and
<name>-walks.gif (all four walks looping at x6) into this folder.
"""
import importlib
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
sys.path.insert(0, os.path.join(HERE, "..", "scale-test"))
import build_gate1 as g  # noqa: E402
import build_scale_test as bst  # noqa: E402


def build(name):
    mod = importlib.import_module(f"{name}_sprites")
    rgba = lambda fr: Image.fromarray(g.frame_rgba(fr, mod.PAL), "RGBA")  # noqa: E731

    rows = [mod.IDLE[f] for f in "snew"] + [mod.WALK[f] for f in "snew"]
    atlas = Image.new("RGBA", (16 * 4, 24 * len(rows)), (0, 0, 0, 0))
    for r, fs in enumerate(rows):
        for i, fr in enumerate(fs):
            atlas.paste(rgba(fr), (i * 16, r * 24))
    atlas.save(os.path.join(HERE, f"{name}-atlas.png"))
    anims = {f"{name}_idle_{f}": {"row": i, "frames": 2, "ms": g.IDLE_MS} for i, f in enumerate("snew")}
    anims.update({f"{name}_walk_{f}": {"row": 4 + i, "frames": 4, "ms": g.WALK_MS, "px_per_frame": 8,
                                       "contact_frames": [0, 2]} for i, f in enumerate("snew")})
    meta = {"frame": {"w": 16, "h": 24}, "anchor": {"name": "feet_bc", "x": 8, "y": 24},
            "footprint_cells": [1, 1], "animations": anims,
            "shadow": "drawn by the renderer at the anchor, not baked into frames"}
    with open(os.path.join(HERE, f"{name}-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=2)

    frames = [(f"idle {f.upper()} {i}", fr) for f in "snew" for i, fr in enumerate(mod.IDLE[f])]
    frames += [(f"walk {f.upper()} {i}", fr) for f in "snew" for i, fr in enumerate(mod.WALK[f])]
    cell_w, cell_h, cols = 16 * 8 + 24, 24 * 8 + 120, 8
    sheet = Image.new("RGB", (cols * cell_w + 24, ((len(frames) + cols - 1) // cols) * cell_h + 60), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), f"{name.capitalize()} frames · x8 (diagnosis) · x2 · x1 native · anchor marked in coral",
           font=bst.font(18, bold=True), fill="#F4F2EC")
    for n, (label, fr) in enumerate(frames):
        gx, gy = 24 + (n % cols) * cell_w, 52 + (n // cols) * cell_h
        sp = rgba(fr)
        for sc, ox, oy in ((8, 0, 0), (2, 0, 24 * 8 + 12), (1, 48, 24 * 8 + 12)):
            bg = Image.new("RGBA", (16 * sc, 24 * sc), tuple(bst.STONE[3]) + (255,))
            bg.alpha_composite(sp.resize((16 * sc, 24 * sc), Image.NEAREST))
            sheet.paste(bg.convert("RGB"), (gx + ox, gy + oy))
        d.line([(gx + 64, gy + 24 * 8 - 6), (gx + 64, gy + 24 * 8 + 4)], fill="#EC776D", width=1)
        d.line([(gx + 56, gy + 24 * 8), (gx + 72, gy + 24 * 8)], fill="#EC776D", width=1)
        d.text((gx, gy + 24 * 8 + 12 + 52), label, font=bst.font(15, bold=True), fill="#E6B750")
    sheet.save(os.path.join(HERE, f"{name}-sheet.png"))

    loop = []
    for i in range(4):
        im = Image.new("RGB", (4 * 96 + 5 * 24, 144 + 48), tuple(bst.STONE[3]))
        for n, f in enumerate("snew"):
            sp = rgba(mod.WALK[f][i]).resize((96, 144), Image.NEAREST)
            im.paste(sp, (24 + n * 120, 24), sp)
        loop.append(im)
    loop[0].save(os.path.join(HERE, f"{name}-walks.gif"), save_all=True, append_images=loop[1:],
                 duration=g.WALK_MS, loop=0)


if __name__ == "__main__":
    build(sys.argv[1])
