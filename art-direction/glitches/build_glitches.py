"""Build the glitch review outputs.

Run: python3 build_glitches.py     (needs Pillow + numpy)
Writes into this folder:
  glitches-sheet.png          every frame at x8, x2 and x1, anchors marked, plus a greyscale read test
  glitches-atlas.png / .json  native atlas, one row per animation, with frame size, anchor,
                              footprint, and per-animation frames, ms and movement
  glitches-in-room.png        the approved review room at x4 (1366x768) with the three glitches on the floor
  glitches-in-room-native.png the same 320x180 logical view
  glitches-roam.gif           the three glitches roaming and misregistering in the room (x6 crop)
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

FLOOR = tuple(bst.STONE[3])


def rgba(frame):
    """Key grid of any size to an RGBA image (g.frame_rgba is fixed at 16x24)."""
    h, w = len(frame), len(frame[0])
    img = np.zeros((h, w, 4), np.uint8)
    for y, row in enumerate(frame):
        for x, ch in enumerate(row):
            c = G.PAL[ch]
            if c:
                img[y, x, :3] = bst.hx(c)
                img[y, x, 3] = 255
    return Image.fromarray(img, "RGBA")


def on_floor(im, scale):
    bg = Image.new("RGBA", (im.width * scale, im.height * scale), FLOOR + (255,))
    bg.alpha_composite(im.resize((im.width * scale, im.height * scale), Image.NEAREST))
    return bg


# ------------------------------------------------------------------ atlas

def build_atlas():
    rows = G.ANIMATIONS
    atlas = Image.new("RGBA", (128, 16 * len(rows)), (0, 0, 0, 0))
    anims, archs = {}, {}
    for r, (arch, kind) in enumerate(rows):
        d = G.ARCHETYPES[arch]
        w, h = d["grid"]["size"]
        frs = d["grid"][kind]
        for i, fr in enumerate(frs):
            atlas.paste(rgba(fr), (i * w, r * 16))
        entry = {"archetype": arch, "row": r, "x": 0, "y": r * 16, "frames": len(frs),
                 "frame": {"w": w, "h": h}, "ms": d[kind]["ms"], "loop": kind == "roam"}
        if kind == "roam":
            entry.update({"move_px_per_frame": d["roam"]["move_px_per_frame"],
                          "lift_px": d["roam"]["lift_px"], "note": d["roam"]["note"]})
        else:
            entry.update({"play": "flicker",
                          "note": "show each frame once for its ms, then return to the roam frame; "
                                  "trigger every 1.2-2.4 s while roaming or idle, and on contact"})
        anims[f"{arch}_{kind}"] = entry
        archs[arch] = {"frame": {"w": w, "h": h}, "footprint_cells": list(d["grid"]["footprint"]),
                       "anchor": {"name": "base_bc", "x": d["anchor"][0], "y": d["anchor"][1],
                                  "note": "pixel edge at the bottom centre of the frame"},
                       "contact_shadow": {"x0": d["shadow"]["x0"], "x1": d["shadow"]["x1"],
                                          "row": d["shadow"]["row"],
                                          "note": "drawn by the renderer under the real object; shrink 2 px "
                                                  "while lifted 2 px or more"},
                       "flippable": False}
    atlas.save(os.path.join(HERE, "glitches-atlas.png"))
    meta = {"status": "Candidate, pending director review",
            "atlas": {"w": 128, "h": 16 * len(rows), "row_h": 16,
                      "note": "each animation is one row, frames left to right at the archetype's frame width"},
            "archetypes": archs, "animations": anims,
            "palette": {k: v for k, v in G.PAL.items() if v},
            "rules": "violet is the anomaly only; light from the upper left, so frames are never mirrored"}
    with open(os.path.join(HERE, "glitches-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=2)


# ------------------------------------------------------------------ sheet

def build_sheet():
    pad, label_h = 24, 22
    cell_h = 16 * 8 + 12 + 32 + 4 + label_h
    n_rows = len(G.ANIMATIONS)
    max_w = max(sum(len(G.frames(a, k)) * (G.ARCHETYPES[a]["grid"]["size"][0] * 8 + pad)
                    for a, k in [(a, k)]) for a, k in G.ANIMATIONS)
    grey_h = 190
    sheet = Image.new("RGB", (max(max_w + pad, 1180), 56 + n_rows * cell_h + grey_h), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((pad, 16), "Glitches · every frame at x8 (diagnosis) · x2 · x1 native · anchor marked in coral",
           font=bst.font(18, bold=True), fill="#F4F2EC")
    for r, (arch, kind) in enumerate(G.ANIMATIONS):
        dd = G.ARCHETYPES[arch]
        w, h = dd["grid"]["size"]
        x = pad
        y = 56 + r * cell_h
        for i, fr in enumerate(dd["grid"][kind]):
            sp = rgba(fr)
            sheet.paste(on_floor(sp, 8).convert("RGB"), (x, y))
            sheet.paste(on_floor(sp, 2).convert("RGB"), (x, y + 16 * 8 + 12))
            sheet.paste(on_floor(sp, 1).convert("RGB"), (x + w * 2 + 12, y + 16 * 8 + 12))
            ax = x + dd["anchor"][0] * 8
            d.line([(ax, y + 16 * 8 - 6), (ax, y + 16 * 8 + 4)], fill="#EC776D", width=1)
            d.line([(ax - 8, y + 16 * 8), (ax + 8, y + 16 * 8)], fill="#EC776D", width=1)
            d.text((x, y + 16 * 8 + 12 + 40), f"{arch} {kind} {i}", font=bst.font(15, bold=True), fill="#E6B750")
            x += w * 8 + pad
    # Greyscale read test: the three rest frames at x1 and x4 on the greyscale floor, side by side.
    y0 = 56 + n_rows * cell_h + 10
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


def place_glitch(c, arch, frame, ax, ay, lifted=0):
    w, h = G.ARCHETYPES[arch]["grid"]["size"]
    contact_shadow(c, arch, ax, ay, lifted)
    sp = np.array(rgba(frame))
    x0, y0 = ax - w // 2, ay - h
    a = sp[:, :, 3] > 0
    region = c.img[y0:y0 + h, x0:x0 + w]
    region[a] = sp[:, :, :3][a]


def room(frames_by_arch, offsets=None, with_engineer=True):
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
        place_glitch(c, arch, G.frames(arch, kind)[i], ax + off, ay, lifted)
        if arch == MARKER_ARCH:  # violet folded-page marker, floating above the form
            real_marker(c, "glitch", (ax + off) / g.T, (ay - 16 - 10) / g.T)
    return c


def build_room():
    c = room({a: ("roam", 0) for a in G.ARCHETYPES})
    native, screen = g.to_screen(c)
    native.save(os.path.join(HERE, "glitches-in-room-native.png"))
    screen.save(os.path.join(HERE, "glitches-in-room.png"))


# ------------------------------------------------------------------ gif

TICK = 40
DURATION = 4800          # ms: integer cycles for all three roams
LEG = 2400               # ms out, then 2400 ms back
FLICKER_AT = {"stapler": 900, "chair": 1700, "form": 2500}


def state_at(arch, t):
    d = G.ARCHETYPES[arch]["roam"]
    ms, n, move = d["ms"], len(G.ARCHETYPES[arch]["grid"]["roam"]), d["move_px_per_frame"]

    def cum(tt):  # px travelled by frame boundaries 1..tt//ms
        return sum(move[j % n] for j in range(1, tt // ms + 1))

    off = cum(t) if t <= LEG else 2 * cum(LEG) - cum(t)  # out, then the same steps back
    return (t // ms) % n, off


def build_gif():
    # Crop around the route: native x 180..300, y 44..124 at x6.
    x0, y0, x1, y1 = 180, 44, 300, 124
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
        c = room(sel, offs)
        crop = Image.fromarray(c.img[y0:y1, x0:x1]).resize(((x1 - x0) * 6, (y1 - y0) * 6), Image.NEAREST)
        frames.append(crop)
    frames[0].save(os.path.join(HERE, "glitches-roam.gif"), save_all=True, append_images=frames[1:],
                   duration=TICK, loop=0, optimize=False)


def main():
    build_atlas()
    build_sheet()
    build_room()
    build_gif()
    print("built glitches-sheet.png, glitches-atlas.png/.json, glitches-in-room.png, glitches-roam.gif")


if __name__ == "__main__":
    main()
