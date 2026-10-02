"""Build review outputs for the background workers (both bodies, all palettes).

Run: python3 build_bgworkers.py   (needs Pillow + numpy; writes into this folder)

Per body (bgworker_a, bgworker_b):
  <body>-atlas.png / .json   native atlas, default palette (slate). Rows: S N E W idle, S N E W walk,
                              then the individual idles (phone, coffee, typing; facing S).
  <body>-atlas-<palette>.png one atlas per palette, same layout
  <body>-atlas-silhouette.png / -silhouette-lit.png   the silhouette treatment, same layout
Shared:
  bgworkers-sheet.png        every frame at x8 (default palette), then every body x palette at x2 and x1,
                             plus the silhouette frames on floor and through glass
  bgworkers-lineup.png       the Engineer, Ivo and Mira beside all six workers at x4 and x1
  bgworkers-in-room.png      the approved review room at x4 (1366x768) with a synced pair mid-loop
  bgworkers-sync-1366x768.gif  that pair walking the same tiny loop in lockstep (16 frames)
  bgworkers-relaxed-1366x768.png  after level 06: the loops have broken into individual idles
Seated at a desk (written by bgworker_seated_build.py, called at the end of build()):
  <body>-seated-atlas*.png / .json, bgworkers-seated-sheet.png, bgworkers-seated-room-1366x768.png,
  bgworkers-seated-1366x768.gif
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
sys.path.insert(0, os.path.join(HERE, "..", "scale-test"))
import build_gate1 as g  # noqa: E402
import build_scale_test as bst  # noqa: E402
import bgworker_a_sprites as body_a  # noqa: E402
import bgworker_b_sprites as body_b  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import ivo_sprites as ivo  # noqa: E402
import mira_sprites as mira  # noqa: E402

BODIES = {"bgworker_a": body_a, "bgworker_b": body_b}
FLOOR = tuple(bst.FLOOR)
GLASS_BG = tuple(bst.GLASS[1])
VARIANTS = ["phone_s", "coffee_s", "typing_s"]
ROW_NAMES = (["idle_" + f for f in "snew"] + ["walk_" + f for f in "snew"] + ["idle_" + v for v in VARIANTS])


def rgba(frame, pal):
    return Image.fromarray(g.frame_rgba(frame, pal), "RGBA")


def rows_of(mod):
    return ([mod.IDLE[f] for f in "snew"] + [mod.WALK[f] for f in "snew"]
            + [mod.IDLE_VARIANTS[v] for v in VARIANTS])


def atlas_image(mod, pal, transform=None):
    rows = rows_of(mod)
    im = Image.new("RGBA", (16 * 4, 24 * len(rows)), (0, 0, 0, 0))
    for r, fs in enumerate(rows):
        for i, fr in enumerate(fs):
            im.paste(rgba(transform(fr) if transform else fr, pal), (i * 16, r * 24))
    return im


def hexes(mod, name):
    pal = mod.make_pal(name)
    return {slot: [pal[k] for k in keys] for slot, keys in mod.SLOTS.items()}


def build_atlases():
    for body, mod in BODIES.items():
        atlas_image(mod, mod.make_pal("slate")).save(os.path.join(HERE, f"{body}-atlas.png"))
        for pname in (p for p in mod.PALETTES if p != "slate"):
            atlas_image(mod, mod.make_pal(pname)).save(os.path.join(HERE, f"{body}-atlas-{pname}.png"))
        atlas_image(mod, mod.SILHOUETTE_PAL, mod.silhouette).save(os.path.join(HERE, f"{body}-atlas-silhouette.png"))
        atlas_image(mod, mod.SILHOUETTE_LIT_PAL, mod.silhouette_lit).save(
            os.path.join(HERE, f"{body}-atlas-silhouette-lit.png"))

        anims = {f"{body}_idle_{f}": {"row": i, "frames": 2, "ms": g.IDLE_MS} for i, f in enumerate("snew")}
        anims.update({f"{body}_walk_{f}": {"row": 4 + i, "frames": 4, "ms": g.WALK_MS, "px_per_frame": 8,
                                           "contact_frames": [0, 2]} for i, f in enumerate("snew")})
        variants = {f"{body}_idle_{v}": {"row": 8 + i, "frames": 2, "ms": g.IDLE_MS, "facing": "s",
                                         "start_offset_ms": "random 0-999, per worker"}
                    for i, v in enumerate(VARIANTS)}
        meta = {
            "status": "Approved by the director 2026-10-02",
            "frame": {"w": 16, "h": 24},
            "anchor": {"name": "feet_bc", "x": 8, "y": 24},
            "footprint_cells": [1, 1],
            "animations": anims,
            "variants": variants,
            "palettes": {
                "default": "slate",
                **{p: {"atlas": f"{body}-atlas{'' if p == 'slate' else '-' + p}.png", "slots": hexes(mod, p)}
                   for p in mod.PALETTES},
                "note": "palettes are ramp swaps on the same key grids; pick one per worker instance",
            },
            "silhouette": {
                "atlas": f"{body}-atlas-silhouette.png",
                "atlas_lit_edge": f"{body}-atlas-silhouette-lit.png",
                "fill": mod.SILHOUETTE_PAL["S"],
                "contour": mod.SILHOUETTE_PAL["o"],
                "lit_edge": mod.SILHOUETTE_LIT_PAL["L"],
                "use": "distant or through-glass figures; same rows and frame timing as the full-colour atlas",
            },
            "sync": {
                "walk_clock": "frame = floor(t_ms / 133) % 4 on one shared clock, with no per-actor offset, "
                              "so every worker in a synced group is on the same frame at the same moment",
                "synced_state": "orientation before level 06: groups share the clock and walk the same loop",
                "relaxed_state": "after level 06: each worker picks an idle or variant with a random "
                                 "start_offset_ms and the shared clock is dropped",
            },
            "shadow": "drawn by the renderer at the anchor, not baked into frames",
        }
        with open(os.path.join(HERE, f"{body}-atlas.json"), "w") as fh:
            json.dump(meta, fh, indent=2)


# ------------------------------------------------------------------ sheet

def cell(sp, scale, bg=FLOOR):
    b = Image.new("RGBA", (16 * scale, 24 * scale), bg + (255,))
    b.alpha_composite(sp.resize((16 * scale, 24 * scale), Image.NEAREST))
    return b.convert("RGB")


def labelled_row(sheet, d, x0, y0, items, scale, gap, label_font, bg=FLOOR):
    for n, (label, fr, pal, tf) in enumerate(items):
        sp = rgba(tf(fr) if tf else fr, pal)
        gx = x0 + n * (16 * scale + gap)
        sheet.paste(cell(sp, scale, bg), (gx, y0))
        if label:
            d.text((gx, y0 + 24 * scale + 3), label, font=label_font, fill="#E6B750")


def build_sheet():
    f13, f16 = bst.font(13, bold=True), bst.font(17, bold=True)
    cols, cw = 8, 16 * 8 + 24
    x8_height = 0
    sections = []
    for body, mod in BODIES.items():
        slate = mod.make_pal("slate")
        idle = [(f"idle {f.upper()} {i}", fr, slate, None) for f in "snew" for i, fr in enumerate(mod.IDLE[f])]
        walk = [(f"walk {f.upper()} {i}", fr, slate, None) for f in "snew" for i, fr in enumerate(mod.WALK[f])]
        var = [(f"{v[:-2]} {i}", fr, slate, None) for v in VARIANTS for i, fr in enumerate(mod.IDLE_VARIANTS[v])]
        sil = [(f"sil {f.upper()}", mod.IDLE[f][0], mod.SILHOUETTE_PAL, mod.silhouette) for f in "snew"]
        sil += [(f"sil lit {f.upper()}", mod.IDLE[f][0], mod.SILHOUETTE_LIT_PAL, mod.silhouette_lit) for f in "snew"]
        sections.append((body, mod, idle + walk + var + sil))
    row_h = 24 * 8 + 28
    n_rows = sum((len(items) + cols - 1) // cols for _, _, items in sections)
    strip_h = 24 * 2 + 24 * 1 + 22
    height = 60 + n_rows * row_h + 40 + len(BODIES) * 3 * strip_h + 60 + 2 * (24 * 8 + 12) + 80
    sheet = Image.new("RGB", (cols * cw + 24, height), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), "Background workers · x8 (diagnosis, slate palette) · x2 and x1 for every palette · "
           "silhouettes", font=f16, fill="#F4F2EC")
    y = 52
    for body, mod, items in sections:
        d.text((24, y), body, font=f16, fill="#A0DDD4")
        y += 26
        for r in range(0, len(items), cols):
            chunk = items[r:r + cols]
            labelled_row(sheet, d, 24, y, chunk, 8, 24, f13)
            y += row_h
    y += 8
    d.text((24, y), "All palettes · x2 above, x1 below (idle 8, walk 16, individual idles 6)", font=f16, fill="#A0DDD4")
    y += 28
    for body, mod in BODIES.items():
        for pname in mod.PALETTES:
            pal = mod.make_pal(pname)
            frames = ([fr for f in "snew" for fr in mod.IDLE[f]] + [fr for f in "snew" for fr in mod.WALK[f]]
                      + [fr for v in VARIANTS for fr in mod.IDLE_VARIANTS[v]])
            items = [("", fr, pal, None) for fr in frames]
            labelled_row(sheet, d, 24, y, items, 2, 4, f13)
            labelled_row(sheet, d, 24, y + 24 * 2 + 4, items, 1, 20, f13)
            d.text((24 + len(items) * 36 + 8, y + 18), f"{body} · {pname}", font=f13, fill="#E6B750")
            y += strip_h
    y += 8
    d.text((24, y), "Silhouettes through glass (blue-glass panel) and on the floor, x8", font=f16, fill="#A0DDD4")
    y += 28
    for body, mod in BODIES.items():
        gx = 24
        for f in "se":
            for pal, tf, bg in ((mod.SILHOUETTE_PAL, mod.silhouette, GLASS_BG),
                                (mod.SILHOUETTE_LIT_PAL, mod.silhouette_lit, GLASS_BG),
                                (mod.SILHOUETTE_PAL, mod.silhouette, FLOOR)):
                sheet.paste(cell(rgba(tf(mod.IDLE[f][0]), pal), 8, bg), (gx, y))
                gx += 16 * 8 + 12
        y += 24 * 8 + 12
    sheet = sheet.crop((0, 0, sheet.width, min(sheet.height, y + 12)))
    sheet.save(os.path.join(HERE, "bgworkers-sheet.png"))


def build_lineup():
    names = [("Engineer", eng, eng.PAL), ("Ivo", ivo, ivo.PAL), ("Mira", mira, mira.PAL)]
    for body, mod in BODIES.items():
        for p in mod.PALETTES:
            names.append((f"{body[-1].upper()} {p}", mod, mod.make_pal(p)))
    w = len(names) * (16 * 4 + 20) + 20
    im = Image.new("RGB", (w, 2 * (24 * 4 + 34) + 24 * 1 + 70), tuple(bst.FLOOR))
    d = ImageDraw.Draw(im)
    f = bst.font(12, bold=True)
    for r, face in enumerate("se"):
        for n, (label, mod, pal) in enumerate(names):
            x, y = 20 + n * (16 * 4 + 20), 12 + r * (24 * 4 + 34)
            sp = rgba(mod.IDLE[face][0], pal).resize((64, 96), Image.NEAREST)
            d.rectangle([x + 8, y + 94, x + 56, y + 97], fill=tuple(bst.INK[2]))
            im.paste(sp, (x, y), sp)
            if r == 0:
                d.text((x, y + 100), label, font=f, fill="#343650")
    for n, (label, mod, pal) in enumerate(names):  # x1 strip, as the player sees them at 1x
        sp = rgba(mod.IDLE["s"][0], pal)
        im.paste(sp, (20 + n * (16 * 4 + 20) + 24, 2 * (24 * 4 + 34) + 22), sp)
    d.text((20, 2 * (24 * 4 + 34) + 4), "x4 above (S, E facings) · x1 below", font=f, fill="#343650")
    im.save(os.path.join(HERE, "bgworkers-lineup.png"))


# ------------------------------------------------------------------ in-room

LOOP_START = (212, 90)   # worker A's feet at the loop's top-left corner; 16 px square loop
PAIR_OFFSET = 24         # worker B walks the identical loop 24 px to the right
DIRS = [("e", 8, 0), ("s", 0, 8), ("w", -8, 0), ("n", 0, -8)]  # two walk frames per side


def loop_positions():
    """16 frames = 2 laps of the 16x16 square at 8 px per frame; frame t uses walk frame t % 4."""
    x, y = LOOP_START
    out = []
    for t in range(16):
        facing, dx, dy = DIRS[(t // 2) % 4]
        out.append((facing, x, y, t % 4))
        x, y = x + dx, y + dy
    return out


def sync_scene(t_frame):
    c = g.scene(None)
    facing, x, y, wf = loop_positions()[t_frame]
    pa, pb = body_a.make_pal("slate"), body_b.make_pal("olive")
    # back to front by feet y; the pair is a rigid translation, so both share one y
    g.place_px(c, g.frame_rgba(body_a.WALK[facing][wf], pa), x, y)
    g.place_px(c, g.frame_rgba(body_b.WALK[facing][wf], pb), x + PAIR_OFFSET, y)
    return c


def build_room():
    frames = []
    for t in range(16):
        frames.append(g.to_screen(sync_scene(t))[1])
    # still: a contact frame where the pair is mid-stride on the east side
    frames[1].save(os.path.join(HERE, "bgworkers-in-room.png"))
    frames[0].save(os.path.join(HERE, "bgworkers-sync-1366x768.gif"), save_all=True, append_images=frames[1:],
                   duration=g.WALK_MS, loop=0, optimize=False)

    # Relaxed state (after level 06): three workers settle into their own idles, no shared clock.
    c = g.scene(None)
    spots = [(body_a, "slate", "phone_s", 0, 210, 100), (body_b, "olive", "coffee_s", 1, 234, 94),
             (body_a, "ash", "typing_s", 0, 250, 102)]
    for mod, pname, var, fr, x, y in sorted(spots, key=lambda s: s[5]):
        g.place_px(c, g.frame_rgba(mod.IDLE_VARIANTS[var][fr], mod.make_pal(pname)), x, y)
    g.to_screen(c)[1].save(os.path.join(HERE, "bgworkers-relaxed-1366x768.png"))


def build():
    build_atlases()
    build_sheet()
    build_lineup()
    build_room()
    import bgworker_seated_build  # seated-at-desk sets and proofs (own module, same folder)
    bgworker_seated_build.build()


if __name__ == "__main__":
    build()
