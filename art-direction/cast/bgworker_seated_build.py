"""Seated-at-desk outputs for the background workers (called by build_bgworkers.build()).

Outputs (this folder):
  <body>-seated-atlas.png / .json         slate atlas, rows idle, typing, phone, coffee (2 frames each, facing S)
  <body>-seated-atlas-<palette>.png       olive and ash, same layout
  <body>-seated-atlas-silhouette[-lit].png  silhouette treatment, same layout
  bgworkers-seated-sheet.png              every frame at x8 with the hidden rows shaded, then every palette
                                          as the player sees it (real desk, chair and occluder) at x4, silhouettes
  bgworkers-seated-room-1366x768.png      Orientation floor, walls, desks, chairs and occluders at x4: a synced
                                          row (before level 06) over an individual row (after)
  bgworkers-seated-1366x768.gif           the same room animated (8 steps of 250 ms)

Everything is composed from the real kit atlas (kit/orientation-atlas.json) through kitlib: floor to rear props,
then the workers on the actor layer, then front_prop (the desk-front occluders) on top.
"""
import copy
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(HERE, "..", "kit")
sys.path.insert(0, HERE)
sys.path.insert(0, KIT)
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
sys.path.insert(0, os.path.join(HERE, "..", "scale-test"))
import bgworker_a_sprites as body_a  # noqa: E402
import bgworker_b_sprites as body_b  # noqa: E402
import build_gate1 as g  # noqa: E402
import build_scale_test as bst  # noqa: E402
import kitlib  # noqa: E402
from bgworker_common import SEATED_SETS  # noqa: E402

BODIES = {"bgworker_a": body_a, "bgworker_b": body_b}
CHAIR_OFF = (8, -12)       # chair footprint origin = desk origin + this
FEET_OFF = (16, 4)         # worker feet_bc = desk origin + this (the chair's bottom-centre)
FRAME_OFF = (FEET_OFF[0] - 8, FEET_OFF[1] - 24)   # frame top-left = desk origin + (8, -20)
DESKS = {"bgworker_a": "desk_a", "bgworker_b": "desk_b"}   # default pairing; either desk takes either body
TYPING_MS = 250
SET_MS = {"idle": 500, "typing": TYPING_MS, "phone": 500, "coffee": 500}
FLOOR = tuple(bst.FLOOR)
GLASS_BG = tuple(bst.GLASS[1])


def rgba(frame, pal):
    return g.frame_rgba(frame, pal)


def pil(frame, pal, tf=None):
    return Image.fromarray(rgba(tf(frame) if tf else frame, pal), "RGBA")


# ------------------------------------------------------------------ atlases

def atlas_image(mod, pal, transform=None):
    im = Image.new("RGBA", (16 * 2, 24 * len(SEATED_SETS)), (0, 0, 0, 0))
    for r, s in enumerate(SEATED_SETS):
        for i, fr in enumerate(mod.SEATED[s]):
            im.paste(pil(fr, pal, transform), (i * 16, r * 24))
    return im


def build_atlases():
    for body, mod in BODIES.items():
        pre = f"{body}-seated-atlas"
        atlas_image(mod, mod.make_pal("slate")).save(os.path.join(HERE, f"{pre}.png"))
        for pname in (p for p in mod.PALETTES if p != "slate"):
            atlas_image(mod, mod.make_pal(pname)).save(os.path.join(HERE, f"{pre}-{pname}.png"))
        atlas_image(mod, mod.SILHOUETTE_PAL, mod.silhouette).save(os.path.join(HERE, f"{pre}-silhouette.png"))
        atlas_image(mod, mod.SILHOUETTE_LIT_PAL, mod.silhouette_lit).save(
            os.path.join(HERE, f"{pre}-silhouette-lit.png"))
        desk = DESKS[body]
        seat = {
            "facing": "s",
            "pairs_with": {"default_desk": desk, "occluder": desk + "_front", "chair": "chair",
                           "also_fits": {d: d + "_front" for d in DESKS.values()},
                           "note": "desk_a and desk_b share the same shape and occluder rows, so either body "
                                   "may sit at either desk"},
            "chair_offset_from_desk_origin_px": list(CHAIR_OFF),
            "feet_bc_offset_from_desk_origin_px": list(FEET_OFF),
            "frame_offset_from_desk_origin_px": list(FRAME_OFF),
            "draw_order": ["desk (rear_prop)", "chair (rear_prop, after the desk)", "worker (actor layer)",
                           "desk front occluder (front_prop, at the desk origin)"],
            "visible_rows": [0, 14],
            "hidden_by_occluder": {"rows_15_19": "columns 1-14", "rows_20_23": "all columns"},
            "note": "head, shoulders, hands and props live in rows 0-14; rows 15-23 hold the standing lower body, "
                    "drawn but hidden; columns 0 and 15 are empty below row 14",
        }
        anims = {f"{body}_seated_{s}": {"row": r, "frames": 2, "ms": SET_MS[s], "facing": "s",
                                        "loop": True, "pairs_with": desk, "seat": "see top-level seat"}
                 for r, s in enumerate(SEATED_SETS)}
        anims[f"{body}_seated_typing"]["note"] = "hands alternate each frame; no 1 px settle (the head holds still)"
        meta = {
            "status": "Seated set, director review 2026-10-02 (see BACKGROUND_WORKERS_SPEC.md, seated at desk)",
            "frame": {"w": 16, "h": 24},
            "anchor": {"name": "feet_bc", "x": 8, "y": 24},
            "image": f"{pre}.png",
            "layer": "actor",
            "animations": anims,
            "seat": seat,
            "palettes": {
                "default": "slate",
                **{p: {"atlas": f"{pre}{'' if p == 'slate' else '-' + p}.png"} for p in mod.PALETTES},
                "note": "ramp swaps of one set of grids; slot hexes are in the standing atlas JSON",
            },
            "silhouette": {"atlas": f"{pre}-silhouette.png", "atlas_lit_edge": f"{pre}-silhouette-lit.png"},
            "sync": {
                "before_level_06": "every seated worker in a group plays seated_typing on one shared clock, "
                                   "frame = floor(t_ms / 250) % 2, with no per-worker offset",
                "after_level_06": "each worker takes one of idle, typing, phone or coffee with a random "
                                  "start_offset_ms (0-999) and the shared clock is dropped",
            },
            "shadow": "none baked in; the desk and chair carry their own contact shadows",
        }
        with open(os.path.join(HERE, f"{pre}.json"), "w") as fh:
            json.dump(meta, fh, indent=2)


# ------------------------------------------------------------------ room composition (real kit pieces)

_ATLAS = None


def atlas():
    global _ATLAS
    if _ATLAS is None:
        _ATLAS = kitlib.Atlas(os.path.join(KIT, "orientation-atlas.json"))
    return _ATLAS


def base_layout(cw, ch, walls=False):
    with open(os.path.join(KIT, "orientation-review-room.json")) as fh:
        ref = json.load(fh)
    fl = copy.deepcopy(ref["floor"])
    fl["rows"] = [(r * 2)[:cw] for r in fl["rows"]][:ch]
    while len(fl["rows"]) < ch:
        fl["rows"].append(fl["rows"][len(fl["rows"]) % 2])
    pl = []
    if walls:
        pl += [{"entry": "wall_n_plain", "cell": [x, 0]} for x in range(cw)]
    return {"size_cells": [cw, ch], "floor": fl, "placements": pl}


def at(entry, x, y):
    d = {"entry": entry, "cell": [x // 16, y // 16]}
    if (x % 16, y % 16) != (0, 0):
        d["offset"] = [x % 16, y % 16]
    return d


def render(layout, desks, workers):
    """desks: [(entry, x, y)] desk origins; workers: [(frame_rgba or None, desk_index)].
    Back layers, then the chairs and workers, then front_prop (occluders) on top."""
    at_ = atlas()
    lay = copy.deepcopy(layout)
    for entry, x, y in desks:
        lay["placements"].append(at(entry, x, y))
    for entry, x, y in desks:
        lay["placements"].append(at("chair", x + CHAIR_OFF[0], y + CHAIR_OFF[1]))
    canvas = kitlib.render_layout(lay, at_, layers={"floor", "rear_wall", "floor_marking", "rear_prop", "shadow"})
    for (entry, x, y), spr in zip(desks, workers):
        if spr is not None:
            kitlib.blit(canvas, spr, x + FRAME_OFF[0], y + FRAME_OFF[1], {"mode": "over"})
    front = copy.deepcopy(layout)
    front["placements"] = [at(e + "_front", x, y) for e, x, y in desks]
    return kitlib.render_layout(front, at_, layers={"front_prop", "light"}, base=canvas)


def seat_tile(frame, pal, desk, tf=None, scale=4):
    lay = base_layout(3, 3)
    sp = rgba(tf(frame) if tf else frame, pal)
    img = render(lay, [(desk, 4, 24)], [sp])
    return Image.fromarray(img).resize((img.shape[1] * scale, img.shape[0] * scale), Image.NEAREST)


# ------------------------------------------------------------------ sheet

def shaded(frame, pal, scale):
    """The frame at `scale` on the floor colour with the occluder-hidden rows tinted."""
    cell = Image.new("RGBA", (16 * scale, 24 * scale), FLOOR + (255,))
    cell.alpha_composite(pil(frame, pal).resize((16 * scale, 24 * scale), Image.NEAREST))
    ov = Image.new("RGBA", cell.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([1 * scale, 15 * scale, 15 * scale - 1, 20 * scale - 1], fill=(21, 28, 43, 150))
    d.rectangle([0, 20 * scale, 16 * scale - 1, 24 * scale - 1], fill=(21, 28, 43, 150))
    cell.alpha_composite(ov)
    d.line([0, 15 * scale, 16 * scale, 15 * scale], fill=(236, 119, 109, 255), width=1)
    cell.alpha_composite(ov)
    return cell.convert("RGB")


def build_sheet():
    f13, f16 = bst.font(13, bold=True), bst.font(17, bold=True)
    names = [(s, i) for s in SEATED_SETS for i in range(2)]
    tile_w, tile_h = 48 * 4, 48 * 4
    width = max(8 * (16 * 8 + 20) + 24, 8 * (tile_w + 8) + 24)
    height = 56 + len(BODIES) * (24 * 8 + 52) + 40 + len(BODIES) * 3 * (tile_h + 30) + 40 + len(BODIES) * (tile_h + 30) + 24
    sheet = Image.new("RGB", (width, height), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((24, 14), "Background workers, seated at desk: x8 frames (red line = first covered row 15; shaded = hidden "
           "by the occluder), then composed with the real desk, chair and occluder at x4", font=f16, fill="#F4F2EC")
    y = 48
    for body, mod in BODIES.items():
        d.text((24, y), body, font=f16, fill="#A0DDD4")
        y += 24
        for n, (s, i) in enumerate(names):
            x = 24 + n * (16 * 8 + 20)
            sheet.paste(shaded(mod.SEATED[s][i], mod.make_pal("slate"), 8), (x, y))
            d.text((x, y + 24 * 8 + 3), f"{s} {i}", font=f13, fill="#E6B750")
        y += 24 * 8 + 28
    y += 8
    d.text((24, y), "In place at x4 (every palette, every frame)", font=f16, fill="#A0DDD4")
    y += 28
    for body, mod in BODIES.items():
        for pname in mod.PALETTES:
            pal = mod.make_pal(pname)
            for n, (s, i) in enumerate(names):
                sheet.paste(seat_tile(mod.SEATED[s][i], pal, DESKS[body]), (24 + n * (tile_w + 8), y))
            d.text((24, y + tile_h + 2), f"{body} {pname}", font=f13, fill="#E6B750")
            y += tile_h + 30
    y += 8
    d.text((24, y), "Silhouettes in place (flat ink and lit edge), idle and typing", font=f16, fill="#A0DDD4")
    y += 28
    for body, mod in BODIES.items():
        x = 24
        for pal, tf in ((mod.SILHOUETTE_PAL, mod.silhouette), (mod.SILHOUETTE_LIT_PAL, mod.silhouette_lit)):
            for s in ("idle", "typing"):
                sheet.paste(seat_tile(mod.SEATED[s][0], pal, DESKS[body], tf), (x, y))
                x += tile_w + 8
        y += tile_h + 30
    sheet.crop((0, 0, width, y)).save(os.path.join(HERE, "bgworkers-seated-sheet.png"))


# ------------------------------------------------------------------ room

ROOM_W, ROOM_H = 20, 12     # cells, the 320x192 view at x4 is 1280x768, centred on a 1366x768 screen
TOP_ROW_Y, BOT_ROW_Y = 56, 128
DESK_XS = [16, 96, 176, 256]
# (body key, palette, desk entry) per desk; the top row is synced (typing), the bottom row individual
TOP = [("bgworker_a", "slate"), ("bgworker_b", "olive"), ("bgworker_a", "ash"), ("bgworker_b", "slate")]
BOTTOM = [("bgworker_b", "ash", "phone", 0), ("bgworker_a", "olive", "coffee", 1),
          ("bgworker_b", "slate", "idle", 1), ("bgworker_a", "slate", "typing", 0)]


def room_frame(step):
    """step counts 250 ms ticks. Top row: shared clock, same frame for everyone. Bottom: own set and offset."""
    desks, workers = [], []
    for k, (body, pname) in enumerate(TOP):
        mod = BODIES[body]
        desks.append((DESKS[body], DESK_XS[k], TOP_ROW_Y))
        workers.append(rgba(mod.SEATED["typing"][step % 2], mod.make_pal(pname)))
    for k, (body, pname, s, off) in enumerate(BOTTOM):
        mod = BODIES[body]
        desks.append((DESKS[body], DESK_XS[k], BOT_ROW_Y))
        per = 1 if s == "typing" else 2          # idle, phone, coffee flip every 500 ms
        workers.append(rgba(mod.SEATED[s][((step + off * per) // per) % 2], mod.make_pal(pname)))
    lay = base_layout(ROOM_W, ROOM_H, walls=True)
    lay["placements"] += [at("pot_plant_a", 288, 150)]
    native = render(lay, desks, workers)
    img = Image.fromarray(native).resize((ROOM_W * 16 * 4, ROOM_H * 16 * 4), Image.NEAREST)
    screen = Image.new("RGB", (1366, 768), "#151C2B")
    screen.paste(img, ((1366 - img.width) // 2, 0))
    return screen


def build_room():
    frames = [room_frame(t) for t in range(8)]
    frames[1].save(os.path.join(HERE, "bgworkers-seated-room-1366x768.png"))
    frames[0].save(os.path.join(HERE, "bgworkers-seated-1366x768.gif"), save_all=True, append_images=frames[1:],
                   duration=TYPING_MS, loop=0, optimize=False)


def build():
    build_atlases()
    build_sheet()
    build_room()


if __name__ == "__main__":
    build()
