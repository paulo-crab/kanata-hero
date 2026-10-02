"""Build the glitch review outputs.

Run: python3 build_glitches.py     (needs Pillow + numpy)
Writes into this folder:
  glitches-sheet.png             every frame at x8, x2 and x1, anchors marked, plus a greyscale read test
  glitches-before-after.png      per archetype, glitch rest | misregister | snap | ordinary prop, at x8 and x4
  glitches-variants-sheet.png    the three palette variants on a light floor and, as dark_steps, on the Night Shift floor
  glitches-atlas.png / .json     native atlas (128x192), one row per animation, with frame size, anchor, footprint,
                                 frames, ms, movement; the ordinary props; the variant catalogue and the district table
  glitches-in-room.png           the approved review room at x4 (1366x768) with the three glitches on the floor
  glitches-in-room-native.png    the same 320x180 logical view
  glitches-in-room-repaired.png  the same room after the repairs: the three ordinary props
  glitches-in-nightshift.png     the Night Shift reference room at x4 (1280x768), glitching, dark_steps and recoloured chair
  glitches-in-nightshift-repaired.png   the same room after the repairs
  glitches-roam.gif              the three roaming and flickering in the room (x6 crop), 4.8 s loop
  glitches-repair.gif            glitch -> snap -> ordinary prop, per archetype in turn (x6 crop), 4.8 s loop
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
sys.path.insert(0, os.path.join(HERE, "..", "scale-test"))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
import build_gate1 as g  # noqa: E402  (the approved review room: scene, to_screen)
import build_scale_test as bst  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import glitch_sprites as G  # noqa: E402
import glitch_variants as V  # noqa: E402

FLOOR = tuple(bst.STONE[3])
NIGHT_FLOOR = tuple(bst.hx(V.DARK_FLOORS["fill"]))
ATLAS_W = 128


def rgba(frame, swap=None):
    """Key grid of any size to an RGBA image (g.frame_rgba is fixed at 16x24).

    `swap` is an exact hex swap {from: to}, the way the renderer applies a palette variant
    and a district chair recolour."""
    h, w = len(frame), len(frame[0])
    img = np.zeros((h, w, 4), np.uint8)
    for y, row in enumerate(frame):
        for x, ch in enumerate(row):
            c = G.PAL[ch]
            if c:
                if swap:
                    c = swap.get(c, c)
                img[y, x, :3] = bst.hx(c)
                img[y, x, 3] = 255
    return Image.fromarray(img, "RGBA")


def on_floor(im, scale, floor=FLOOR):
    bg = Image.new("RGBA", (im.width * scale, im.height * scale), tuple(floor) + (255,))
    bg.alpha_composite(im.resize((im.width * scale, im.height * scale), Image.NEAREST))
    return bg


# ------------------------------------------------------------------ atlas

def _shadow(d):
    return {"x0": d["shadow"]["x0"], "x1": d["shadow"]["x1"], "row": d["shadow"]["row"],
            "note": "drawn by the renderer under the real object; shrink 2 px while lifted 2 px or more"}


def _anchor(d):
    return {"name": "base_bc", "x": d["anchor"][0], "y": d["anchor"][1],
            "note": "pixel edge at the bottom centre of the frame"}


def district_table():
    out = {}
    for did, d in V.DISTRICTS.items():
        e = json.loads(json.dumps(d))   # deep copy
        e["palette_steps"] = "dark_steps" if d.get("dark_floor") else "steps"
        e["chair_recolour"] = V.chair_swap(did)
        out[did] = e
    return out


def variant_table():
    pal = {}
    for k, v in V.PALETTE_VARIANTS.items():
        pal[k] = {"name": v["name"], "duel": v["duel"], "steps": v["steps"], "dark_steps": v["dark_steps"],
                  "swap": V.palette_swap(k), "swap_dark": V.palette_swap(k, dark=True), "note": v["note"]}
    beh = {}
    for k, b in V.BEHAVIOURS.items():
        beh[k] = {"name": b["name"], "tone": b["tone"], "roam_ms": b["roam_ms"], "path": b["path"],
                  "pause": b["pause"], "misregister": dict(V.expand_misregister(k), frame_ms=80),
                  "note": b["note"]}
    return {
        "palettes": pal,
        "palette_rule": "The sprites are drawn in the standard violet. To use a variant, replace each standard hex "
                        "(#413755 #67547C #9477AF #C3A6D6) by `swap[hex]`, in every frame of the glitch, or by `swap_dark` "
                        "when the district's palette_steps is dark_steps. Change nothing else; never tint the ordinary props.",
        "behaviours": beh,
        "contact_frames": V.CONTACT_FRAMES,
        "behaviour_rule": "roam_ms replaces the animation's ms; the frames and move_px_per_frame are unchanged. path.lane_px is "
                          "the patrol length in px. pause: after after_cycles full roam cycles, show roam frame 0 for hold_ms. "
                          "misregister.frames lists misregister frame indices, each shown for frame_ms; every_ms is [lo, hi] "
                          "(random wait between flickers, null = never unprompted); on_pause plays one burst when a pause starts. "
                          "On contact, before the duel opens, play contact_frames whatever the behaviour.",
    }


def build_atlas():
    rows = G.ANIMATIONS
    atlas = Image.new("RGBA", (ATLAS_W, 16 * len(rows)), (0, 0, 0, 0))
    anims, archs = {}, {}
    for r, (arch, kind) in enumerate(rows):
        d = G.ARCHETYPES[arch]
        w, h = d["grid"]["size"]
        frs = d["grid"][kind]
        for i, fr in enumerate(frs):
            atlas.paste(rgba(fr), (i * w, r * 16))
        entry = {"archetype": arch, "row": r, "x": 0, "y": r * 16, "frames": len(frs), "frame": {"w": w, "h": h}}
        if kind == "roam":
            entry.update({"ms": d[kind]["ms"], "loop": True, "move_px_per_frame": d["roam"]["move_px_per_frame"],
                          "lift_px": d["roam"]["lift_px"], "note": d["roam"]["note"]})
        elif kind == "misregister":
            entry.update({"ms": d[kind]["ms"], "loop": False, "play": "flicker",
                          "note": "show each frame once for its ms, then return to the roam frame; "
                                  "trigger every 1.2-2.4 s while roaming or idle, and on contact"})
        elif kind == "repaired":
            entry.update({"ms": G.REPAIRED_MS, "loop": False, "play": "once", "then": f"{arch}_ordinary",
                          "note": "the snap into register: show this one frame for ms, in place of the roam frame "
                                  "at the glitch's current position, then swap to the ordinary prop and stop roaming. "
                                  f"Cue: {d['repaired']['cue']}"})
        else:
            entry.update({"loop": False, "static": True,
                          "note": "the ordinary prop the glitch becomes; static, no violet, placed at the repaired "
                                  "position with the same anchor"})
        anims[f"{arch}_{kind}"] = entry
        if arch not in archs:
            ord_row = rows.index((arch, "ordinary"))
            archs[arch] = {
                "frame": {"w": w, "h": h}, "footprint_cells": list(d["grid"]["footprint"]),
                "anchor": _anchor(d), "contact_shadow": _shadow(d), "flippable": False,
                "ordinary": {
                    "animation": f"{arch}_ordinary", "row": ord_row,
                    "footprint": {"cells": list(d["grid"]["footprint"]), "origin_px": [0, 0]},
                    "collision": d["ordinary"]["collision"],
                    "layer": "actor", "y_sort": True,
                    "anchor": _anchor(d), "contact_shadow": _shadow(d), "flippable": False,
                    "note": d["ordinary"]["note"],
                },
            }
    atlas.save(os.path.join(HERE, "glitches-atlas.png"))
    meta = {"status": "Approved by the director 2026-10-02",
            "atlas": {"w": ATLAS_W, "h": 16 * len(rows), "row_h": 16,
                      "note": "each animation is one row, frames left to right at the archetype's frame width"},
            "archetypes": archs, "animations": anims,
            "repair": {
                "sequence": ["<archetype>_roam / _misregister (glitch)", "<archetype>_repaired (play once)",
                             "<archetype>_ordinary (static, stays)"],
                "ms": G.REPAIRED_MS,
                "rule": "When the repair duel succeeds: stop moving, draw <archetype>_repaired at the current anchor for "
                        "ms, then draw <archetype>_ordinary at that anchor and stop roaming. The ordinary prop is a "
                        "district-neutral office object (stapler: ink ramp; sheet: paper ramp; chair: coral upholstery, "
                        "recoloured by the district's chair_recolour). It has the archetype's renderer contact shadow, "
                        "no violet, and its collision grid. Remove the glitch marker and the interaction outline when the "
                        "snap frame starts; the room keeps the ordinary prop across visits.",
            },
            "variants": variant_table(),
            "districts": district_table(),
            "palette": {k: v for k, v in G.PAL.items() if v},
            "rules": "violet is the anomaly only; light from the upper left, so frames are never mirrored"}
    with open(os.path.join(HERE, "glitches-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")


# ------------------------------------------------------------------ sheet

def sheet_rows():
    """(label, arch, [(name, frame)]) per row: roam, misregister, then repaired + ordinary together."""
    out = []
    for arch in G.ARCHETYPES:
        for kind in ("roam", "misregister"):
            out.append((f"{arch} {kind}", arch,
                        [(f"{arch} {kind} {i}", fr) for i, fr in enumerate(G.frames(arch, kind))]))
        out.append((f"{arch} repaired + ordinary", arch,
                    [(f"{arch} repaired (snap, {G.REPAIRED_MS} ms)", G.frames(arch, "repaired")[0]),
                     (f"{arch} ordinary prop", G.frames(arch, "ordinary")[0])]))
    return out


def build_sheet():
    pad, label_h = 24, 22
    cell_h = 16 * 8 + 12 + 32 + 4 + label_h
    rows = sheet_rows()
    max_w = max(sum(G.ARCHETYPES[a]["grid"]["size"][0] * 8 + pad for _ in frs) for _, a, frs in rows)
    grey_h = 190
    sheet = Image.new("RGB", (max(max_w + pad, 1180), 56 + len(rows) * cell_h + grey_h), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((pad, 16), "Glitches · every frame at x8 (diagnosis) · x2 · x1 native · anchor marked in coral",
           font=bst.font(18, bold=True), fill="#F4F2EC")
    for r, (_, arch, frs) in enumerate(rows):
        dd = G.ARCHETYPES[arch]
        w, h = dd["grid"]["size"]
        x = pad
        y = 56 + r * cell_h
        for name, fr in frs:
            sp = rgba(fr)
            sheet.paste(on_floor(sp, 8).convert("RGB"), (x, y))
            sheet.paste(on_floor(sp, 2).convert("RGB"), (x, y + 16 * 8 + 12))
            sheet.paste(on_floor(sp, 1).convert("RGB"), (x + w * 2 + 12, y + 16 * 8 + 12))
            ax = x + dd["anchor"][0] * 8
            d.line([(ax, y + 16 * 8 - 6), (ax, y + 16 * 8 + 4)], fill="#EC776D", width=1)
            d.line([(ax - 8, y + 16 * 8), (ax + 8, y + 16 * 8)], fill="#EC776D", width=1)
            d.text((x, y + 16 * 8 + 12 + 40), name, font=bst.font(15, bold=True), fill="#E6B750")
            x += w * 8 + pad
    # Greyscale read test: the three rest frames at x1 and x4 on the floor in greyscale, side by side.
    y0 = 56 + len(rows) * cell_h + 10
    d.text((pad, y0), "Greyscale read: rest frames at x1 (native) and x4, on the floor in greyscale",
           font=bst.font(16, bold=True), fill="#F4F2EC")
    x = pad
    for arch in G.ARCHETYPES:
        fr = rgba(G.ARCHETYPES[arch]["grid"]["roam"][0])
        for sc in (1, 4):
            tile = on_floor(fr, sc).convert("L").convert("RGB")
            sheet.paste(tile, (x, y0 + 30))
            x += tile.width + 12
        x += 24
    sheet.save(os.path.join(HERE, "glitches-sheet.png"))


def build_before_after():
    """Per archetype: glitch rest | misregister | snap | ordinary prop. x8 on the top band, x4 below."""
    pad, label_h = 24, 24
    steps = [("glitch (rest)", "roam", 0), ("misregister", "misregister", 0),
             (f"snap ({G.REPAIRED_MS} ms)", "repaired", 0), ("ordinary prop", "ordinary", 0)]
    h8, h4 = 16 * 8, 16 * 4
    width = pad + max(sum(G.ARCHETYPES[a]["grid"]["size"][0] * s + pad for _ in steps) for a in G.ARCHETYPES for s in (8,))
    sheet = Image.new("RGB", (width, 56 + len(G.ARCHETYPES) * (h8 + label_h + h4 + label_h + 16)), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((pad, 16), "Glitches · before and after the repair · x8 above, x4 below · violet only until the snap",
           font=bst.font(18, bold=True), fill="#F4F2EC")
    y = 56
    for arch in G.ARCHETYPES:
        w = G.ARCHETYPES[arch]["grid"]["size"][0]
        for scale, hh in ((8, h8), (4, h4)):
            x = pad
            for name, kind, i in steps:
                sp = rgba(G.frames(arch, kind)[i])
                sheet.paste(on_floor(sp, scale).convert("RGB"), (x, y))
                if scale == 8:
                    d.text((x, y + hh + 2), f"{arch}: {name}", font=bst.font(14, bold=True), fill="#E6B750")
                x += w * 8 + pad
            y += hh + label_h
        y += 16
    sheet.save(os.path.join(HERE, "glitches-before-after.png"))


def build_variants_sheet():
    """Each palette variant, the three archetype rest frames: on the light stone floor, then as dark_steps on the Night Shift floor."""
    pad = 20
    scale = 6
    tiles = [(a, G.frames(a, "roam")[0]) for a in G.ARCHETYPES]
    group_w = sum(rgba(fr).width * scale + pad for _, fr in tiles)
    sheet = Image.new("RGB", (pad + 2 * group_w + 40, 80 + len(V.PALETTE_VARIANTS) * (16 * scale + 56)), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((pad, 14), "Glitch palette variants · exact hex swaps of the four violet steps · light floor | Night Shift floor (dark_steps)",
           font=bst.font(17, bold=True), fill="#F4F2EC")
    d.text((pad, 42), "variant: duel kind", font=bst.font(14), fill="#9AA4BC")
    y = 80
    for vid, v in V.PALETTE_VARIANTS.items():
        d.text((pad, y), f"{vid}: {v['duel']} duel   steps {' '.join(v['steps'])}   dark {' '.join(v['dark_steps'])}",
               font=bst.font(14, bold=True), fill="#E6B750")
        for gi, (dark, floor) in enumerate(((False, FLOOR), (True, NIGHT_FLOOR))):
            x = pad + gi * (group_w + 40)
            swap = V.palette_swap(vid, dark)
            if vid == "standard" and not dark:
                swap = None
            for arch, fr in tiles:
                im = on_floor(rgba(fr, swap), scale, floor)
                sheet.paste(im.convert("RGB"), (x, y + 22))
                x += im.width + pad
        y += 16 * scale + 56
    sheet.save(os.path.join(HERE, "glitches-variants-sheet.png"))


# ------------------------------------------------------------------ room

# Anchors (bottom centre of the frame) on the floor, in native px, plus the direction each
# glitch patrols in the GIF. The chair shadow sits north of the route, the folded form on
# it, the stapler south of it. The approved scene's own glitch marker is moved over the form.
PLACEMENT = {
    "chair": (216, 66, 1),
    "form": (246, 98, -1),
    "stapler": (214, 110, 1),
}
MARKER_ARCH = "form"
GLITCH_KINDS = ("roam", "misregister")


def contact_shadow(c, arch, ax, ay, lifted=0):
    s = G.ARCHETYPES[arch]["shadow"]
    w, h = G.ARCHETYPES[arch]["grid"]["size"]
    x0, y0 = ax - w // 2, ay - h
    sh = 2 if lifted >= 2 else 0
    a, b = x0 + s["x0"] + sh, x0 + s["x1"] - sh
    row = y0 + s["row"]
    c.img[row, a:b] = g.SHADOW_OUTER
    c.img[row, a + 1:b - 1] = g.SHADOW_CORE
    c.img[row + 1, a + 1:b - 1] = g.SHADOW_OUTER


def stamp(img, arch, frame, ax, ay, swap=None):
    """Draw a frame's opaque pixels onto an (H, W, 3) array with its anchor at (ax, ay)."""
    w, h = G.ARCHETYPES[arch]["grid"]["size"]
    sp = np.array(rgba(frame, swap))
    x0, y0 = ax - w // 2, ay - h
    a = sp[:, :, 3] > 0
    region = img[y0:y0 + h, x0:x0 + w]
    region[a] = sp[:, :, :3][a]


def place_glitch(c, arch, frame, ax, ay, lifted=0, swap=None):
    contact_shadow(c, arch, ax, ay, lifted)
    stamp(c.img, arch, frame, ax, ay, swap)


def room(frames_by_arch, offsets=None, with_engineer=True, swaps=None):
    """The approved scene with each glitch's current frame placed at its anchor (+ offset)."""
    eng_frame = eng.IDLE["e"][0] if with_engineer else None
    real_marker = bst.marker

    def marker(c, kind, x, y):  # the scene's own glitch marker sits at a placeholder spot
        if kind != "glitch":
            real_marker(c, kind, x, y)

    bst.marker = marker
    try:
        c = g.scene(eng_frame, 196, g.ROUTE_Y) if with_engineer else g.scene()
    finally:
        bst.marker = real_marker
    for arch, (kind, i) in frames_by_arch.items():
        ax, ay, direction = PLACEMENT[arch]
        off = (offsets or {}).get(arch, 0) * direction
        lifted = G.ARCHETYPES[arch]["roam"]["lift_px"][i] if kind == "roam" else 0
        place_glitch(c, arch, G.frames(arch, kind)[i], ax + off, ay, lifted, (swaps or {}).get(arch))
        if arch == MARKER_ARCH and kind in GLITCH_KINDS:  # violet folded-page marker, floating above the form
            real_marker(c, "glitch", (ax + off) / g.T, (ay - 16 - 10) / g.T)
    return c


def build_room():
    c = room({a: ("roam", 0) for a in G.ARCHETYPES})
    native, screen = g.to_screen(c)
    native.save(os.path.join(HERE, "glitches-in-room-native.png"))
    screen.save(os.path.join(HERE, "glitches-in-room.png"))
    c = room({a: ("ordinary", 0) for a in G.ARCHETYPES})
    g.to_screen(c)[1].save(os.path.join(HERE, "glitches-in-room-repaired.png"))


# Night Shift (dark floor) from the approved reference room: the glitches in dark_steps, with the
# district's chair recolour, on open floor beside Route B. Positions are native px (anchor x, y).
NS_ROOM = os.path.join(HERE, "..", "kit", "nightshift-reference-room-native.png")
NS_PLACEMENT = {"chair": (97, 71), "form": (259, 81), "stapler": (64, 176)}
NS_VARIANT = {"chair": "standard", "form": "plum", "stapler": "dusk"}


def build_nightshift():
    base = np.array(Image.open(NS_ROOM).convert("RGB"))
    chair_swap = V.chair_swap("nightshift")
    for suffix, kinds in (("", {"chair": "roam", "form": "roam", "stapler": "roam"}),
                          ("-repaired", {a: "ordinary" for a in G.ARCHETYPES})):
        img = base.copy()

        class C:  # the tiny canvas place_glitch needs
            pass
        c = C()
        c.img = img
        for arch, (ax, ay) in NS_PLACEMENT.items():
            kind = kinds[arch]
            swap = dict(chair_swap) if arch == "chair" else {}
            if kind != "ordinary":
                swap.update(V.palette_swap(NS_VARIANT[arch], dark=True))
            place_glitch(c, arch, G.frames(arch, kind)[0], ax, ay, 0, swap)
        Image.fromarray(img).resize((img.shape[1] * 4, img.shape[0] * 4), Image.NEAREST).save(
            os.path.join(HERE, f"glitches-in-nightshift{suffix}.png"))


# ------------------------------------------------------------------ gifs

TICK = 40
DURATION = 4800          # ms: integer cycles for all three roams
LEG = 2400               # ms out, then 2400 ms back
FLICKER_AT = {"stapler": 900, "chair": 1700, "form": 2500}
CROP = (180, 44, 300, 124)   # native x0, y0, x1, y1 around the route; shown at x6


def state_at(arch, t):
    d = G.ARCHETYPES[arch]["roam"]
    ms, n, move = d["ms"], len(G.ARCHETYPES[arch]["grid"]["roam"]), d["move_px_per_frame"]

    def cum(tt):  # px travelled by frame boundaries 1..tt//ms
        return sum(move[j % n] for j in range(1, tt // ms + 1))

    off = cum(t) if t <= LEG else 2 * cum(LEG) - cum(t)  # out, then the same steps back
    return (t // ms) % n, off


def crop6(c):
    x0, y0, x1, y1 = CROP
    return Image.fromarray(c.img[y0:y1, x0:x1]).resize(((x1 - x0) * 6, (y1 - y0) * 6), Image.NEAREST)


def save_gif(frames, name):
    frames[0].save(os.path.join(HERE, name), save_all=True, append_images=frames[1:],
                   duration=TICK, loop=0, optimize=False)


def build_roam_gif():
    flicker_len = 2
    frames = []
    for t in range(0, DURATION, TICK):
        sel, offs = {}, {}
        for arch in G.ARCHETYPES:
            i, off = state_at(arch, t)
            sel[arch] = ("roam", i)
            offs[arch] = off
            fl = FLICKER_AT[arch]
            for k in range(flicker_len):
                if fl + k * 80 <= t < fl + (k + 1) * 80:
                    sel[arch] = ("misregister", k)
        frames.append(crop6(room(sel, offs)))
    save_gif(frames, "glitches-roam.gif")


# Repair sequence: each glitch roams and flickers, snaps for REPAIRED_MS at its own time, then stays as the
# ordinary prop where it stopped. The violet marker above the form goes with the glitch.
SNAP_AT = {"stapler": 1200, "chair": 2000, "form": 2800}


def build_repair_gif():
    frames = []
    for t in range(0, DURATION, TICK):
        sel, offs = {}, {}
        for arch in G.ARCHETYPES:
            snap = SNAP_AT[arch]
            if t < snap:
                i, off = state_at(arch, t)
                sel[arch] = ("roam", i)
                fl = FLICKER_AT[arch] - 600
                for k in range(2):
                    if fl + k * 80 <= t < fl + (k + 1) * 80:
                        sel[arch] = ("misregister", k)
            else:
                _, off = state_at(arch, snap)
                sel[arch] = ("repaired", 0) if t < snap + G.REPAIRED_MS else ("ordinary", 0)
            offs[arch] = off
        frames.append(crop6(room(sel, offs)))
    save_gif(frames, "glitches-repair.gif")


def main():
    build_atlas()
    build_sheet()
    build_before_after()
    build_variants_sheet()
    build_room()
    build_nightshift()
    build_roam_gif()
    build_repair_gif()
    print("built glitches-sheet/before-after/variants-sheet.png, glitches-atlas.png/.json, "
          "glitches-in-room*.png, glitches-in-nightshift*.png, glitches-roam.gif, glitches-repair.gif")


if __name__ == "__main__":
    main()
