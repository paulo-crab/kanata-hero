"""Build review outputs for a cast sprite module.

Run: python3 build_cast.py ivo   (needs Pillow + numpy; names: ivo, mira, engineer)
Writes <stem>-sheet.png (every frame at x8, x2, x1 with the anchor marked),
<stem>-atlas.png/.json (rows S N E W idle, then S N E W walk, then one row per EXTRA set and
key), <name>-walks.gif (all four walks looping at x6) and <name>-extra.gif (every EXTRA set
at x6, each frame held for exactly its EXTRA_MS) into this folder.

Engineer: the approved atlas, sheet and walk GIF are owned by gate1/build_gate1.py, so
`build_cast.py engineer` writes the superset files next to them as engineer-full-atlas.png/.json,
engineer-full-sheet.png and engineer-extra.gif (gate1 folder) and leaves the approved files alone.

EXTRA (task 8): EXTRA[set][key] = [frames]; keys are facings s n e w (or adjacent facing pairs
se en nw ws for "turn"); EXTRA_MS[set] = ms per frame; EXTRA_MODE[set] = "once" (play, then hold
the last frame) or "loop" (default "once").
"""
import importlib
import json
import math
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GATE1 = os.path.join(HERE, "..", "gate1")
sys.path.insert(0, GATE1)
sys.path.insert(0, os.path.join(HERE, "..", "scale-test"))
import build_gate1 as g  # noqa: E402
import build_scale_test as bst  # noqa: E402

TURN_HOLD_MS = 400      # how long the GIF holds each facing around a turn transition
PAIR_FACINGS = {"se": "se", "en": "en", "nw": "nw", "ws": "ws"}


def extra_sets(mod):
    """[(set, key, frames, ms, mode)] in declaration order."""
    ms, mode = getattr(mod, "EXTRA_MS", {}), getattr(mod, "EXTRA_MODE", {})
    return [(sn, key, fs, ms[sn], mode.get(sn, "once"))
            for sn, by_key in getattr(mod, "EXTRA", {}).items() for key, fs in by_key.items()]


def build(name):
    mod = importlib.import_module(f"{name}_sprites")
    rgba = lambda fr: Image.fromarray(g.frame_rgba(fr, mod.PAL), "RGBA")  # noqa: E731
    out = GATE1 if name == "engineer" else HERE
    stem = "engineer-full" if name == "engineer" else name
    extras = extra_sets(mod)

    rows = [mod.IDLE[f] for f in "snew"] + [mod.WALK[f] for f in "snew"] + [fs for _, _, fs, _, _ in extras]
    atlas = Image.new("RGBA", (16 * 4, 24 * len(rows)), (0, 0, 0, 0))
    for r, fs in enumerate(rows):
        assert len(fs) <= 4, f"atlas rows hold at most 4 frames (row {r})"
        for i, fr in enumerate(fs):
            atlas.paste(rgba(fr), (i * 16, r * 24))
    atlas.save(os.path.join(out, f"{stem}-atlas.png"))
    anims = {f"{name}_idle_{f}": {"row": i, "frames": 2, "ms": g.IDLE_MS} for i, f in enumerate("snew")}
    anims.update({f"{name}_walk_{f}": {"row": 4 + i, "frames": 4, "ms": g.WALK_MS, "px_per_frame": 8,
                                       "contact_frames": [0, 2]} for i, f in enumerate("snew")})
    for n, (sn, key, fs, ms, mode) in enumerate(extras):
        entry = {"row": 8 + n, "frames": len(fs), "ms": ms, "mode": mode}
        if sn == "turn":
            entry["between"] = [key[0], key[1]]
            entry["note"] = "play between the two idle facings; the same frame serves both directions"
        anims[f"{name}_{sn}_{key}"] = entry
    meta = {"frame": {"w": 16, "h": 24}, "anchor": {"name": "feet_bc", "x": 8, "y": 24},
            "footprint_cells": [1, 1], "animations": anims,
            "shadow": "drawn by the renderer at the anchor, not baked into frames"}
    with open(os.path.join(out, f"{stem}-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=2)

    frames = [(f"idle {f.upper()} {i}", fr) for f in "snew" for i, fr in enumerate(mod.IDLE[f])]
    frames += [(f"walk {f.upper()} {i}", fr) for f in "snew" for i, fr in enumerate(mod.WALK[f])]
    frames += [(f"{sn.replace('react_', 'r_')} {key.upper()} {i}", fr) for sn, key, fs, _, _ in extras for i, fr in enumerate(fs)]
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
    sheet.save(os.path.join(out, f"{stem}-sheet.png"))

    if name != "engineer":   # the Engineer's walk GIF is built by build_gate1.py
        loop = []
        for i in range(4):
            im = Image.new("RGB", (4 * 96 + 5 * 24, 144 + 48), tuple(bst.STONE[3]))
            for n, f in enumerate("snew"):
                sp = rgba(mod.WALK[f][i]).resize((96, 144), Image.NEAREST)
                im.paste(sp, (24 + n * 120, 24), sp)
            loop.append(im)
        loop[0].save(os.path.join(HERE, f"{name}-walks.gif"), save_all=True, append_images=loop[1:],
                     duration=g.WALK_MS, loop=0)

    if extras:
        build_extra_gif(mod, name, os.path.join(out, f"{name}-extra.gif"))


def build_extra_gif(mod, name, path):
    """One GIF: every EXTRA set in turn, one tile per key, each frame held for exactly EXTRA_MS."""
    rgba = lambda fr: Image.fromarray(g.frame_rgba(fr, mod.PAL), "RGBA")  # noqa: E731
    Z, tile_w, tile_h, pad, cap = 6, 96, 144, 24, 40
    W, H = 4 * tile_w + 5 * pad, tile_h + 2 * pad + cap
    font = bst.font(15, bold=True)
    imgs, durs = [], []

    def panel(label, tiles):
        im = Image.new("RGB", (W, H), tuple(bst.STONE[3]))
        ImageDraw.Draw(im).text((pad, 10), label, font=font, fill=(32, 35, 55))
        for n, fr in enumerate(tiles):
            sp = rgba(fr).resize((tile_w, tile_h), Image.NEAREST)
            im.paste(sp, (pad + n * (tile_w + pad), pad + cap), sp)
        return im

    ms_of, mode_of = mod.EXTRA_MS, getattr(mod, "EXTRA_MODE", {})
    for sn, by_key in mod.EXTRA.items():
        ms = ms_of[sn]
        if sn == "turn":
            for pair_set in (["se", "en", "nw", "ws"],):
                seq = []   # (facing-or-mid per tile, ms)
                for k in range(2):
                    seq.append(([mod.IDLE[p[k]][0] for p in pair_set], TURN_HOLD_MS))
                    seq.append(([by_key[p][0] for p in pair_set], ms))
                for tiles, t in seq * 2:
                    imgs.append(panel(f"{sn} · idle {TURN_HOLD_MS} ms · in-between {ms} ms · "
                                      f"pairs {' '.join(pair_set).upper()}", tiles))
                    durs.append(t)
            continue
        keys = list(by_key)
        n_frames = max(len(by_key[k]) for k in keys)
        reps = max(2, math.ceil(1500 / (n_frames * ms)))
        loop_mode = mode_of.get(sn, "once") == "loop"
        for _ in range(reps):
            for i in range(n_frames):
                tiles = [by_key[k][i % len(by_key[k]) if loop_mode else min(i, len(by_key[k]) - 1)] for k in keys]
                # the frame counter keeps neighbouring panels distinct, so the GIF writer never merges
                # identical frames and every delay stays exactly EXTRA_MS
                imgs.append(panel(f"{sn} · {ms} ms per frame · {'loops' if loop_mode else 'plays once, holds last'}"
                                  f" · frame {i + 1}/{n_frames}", tiles))
                durs.append(ms)
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=durs, loop=0, optimize=False)


if __name__ == "__main__":
    build(sys.argv[1])
