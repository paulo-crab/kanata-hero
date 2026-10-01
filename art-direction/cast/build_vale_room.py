"""Vale in an Executive-palette room, at x4 on a 1366x768 screen (task 6.4).

Run: python3 build_vale_room.py   (needs Pillow + numpy; writes vale-in-executive.png here)

Reuses the palette-swap renderer in ../palettes/build_palettes.py: Orientation's environment pieces
are recoloured into the Executive ramps by an exact hex swap, then people are drawn with their own
palettes and the same contact shadow as the district tiles. Nothing here edits those modules.

What the render tests:
  - Vale idle S and a walk frame next to the Engineer (scale, silhouette, suit against teal).
  - Vale in front of a plain navy wall panel, in front of a glass bay and in front of the navy
    seating: the lit-edge step on the suit has to separate from the Executive wall and seat ramps.
  - Vale on the pale floor, where the dark suit carries the silhouette.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("palettes", "gate1", "cast", "scale-test"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import build_gate1 as g  # noqa: E402  (frame_rgba, place_px)
import build_palettes as bp  # noqa: E402  (palette_swap, shadow)
import build_scale_test as bst  # noqa: E402
import district_palettes as dp  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import environment as env  # noqa: E402
import vale_sprites as vale  # noqa: E402

ZOOM = 4
DISTRICT = "executive"
PAL = dp.DISTRICTS[DISTRICT]


def rgb(h):
    return bp.rgb(h)


def navy_seating(img, sofa_room):
    """Executive seating is dark navy (levels.md): the sofa's wood steps become the wall ramp."""
    mapping = {tuple(w): rgb(n) for w, n in zip(bst.WOOD, PAL["wall"])}
    mask = sofa_room.img.any(axis=2)
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        c = tuple(int(v) for v in sofa_room.img[y, x])
        img[y, x] = mapping.get(c, c)  # ink (shared ramp) stays as drawn


def actor(img, mod, frame, ax, ay):
    sp = g.frame_rgba(frame, mod.PAL)
    bp.shadow(img, ax, ay, dp.INK[2], dp.INK[1])
    c = type("C", (), {})()
    c.img = img
    g.place_px(c, sp, ax, ay, shadow=False)


def room():
    r = env.Room()
    env.floor(r)
    env.north_wall(r)
    for i, (x, y) in enumerate([(98, 30), (226, 30), (272, 30)]):
        env.pot_plant(r, x, y, 100 + i)
    env.garden(r)  # the atrium tree: Orientation's garden recoloured to the Executive foliage and wood ramps
    env.side_table(r, 236, 152)
    unmapped, img = bp.palette_swap(r.img, DISTRICT)
    sofa_room = env.Room()
    env.sofa(sofa_room, 12, 146, w=34)
    navy_seating(img, sofa_room)
    return unmapped, img


def build():
    unmapped, img = room()
    print(f"executive room: {unmapped} pixels without a palette mapping")
    # Next to the Engineer: Engineer, Vale idle S, Vale walking (south, then an east contact frame).
    actor(img, eng, eng.IDLE["s"][0], 222, 84)
    actor(img, vale, vale.IDLE["s"][0], 244, 84)
    actor(img, vale, vale.WALK["s"][1], 268, 92)
    actor(img, vale, vale.WALK["e"][0], 296, 100)
    # Against the wall (feet at y 40, so head and shoulders sit on the wall face): a plain navy panel,
    # a glass bay (seen from behind), and the brighter alcove wall under the copper plaque.
    actor(img, vale, vale.IDLE["s"][0], 75, 40)
    actor(img, vale, vale.IDLE["n"][0], 19, 40)
    actor(img, vale, vale.IDLE["w"][0], 168, 40)
    actor(img, vale, vale.IDLE["e"][0], 50, 40)
    # Against the navy seating: in front of the sofa and beside it, with the Engineer for contrast.
    actor(img, vale, vale.IDLE["s"][0], 24, 176)
    actor(img, vale, vale.IDLE["e"][1], 58, 166)
    actor(img, eng, eng.IDLE["s"][0], 244, 176)

    native = Image.fromarray(img[:180, :320])
    vw, vh = 320 * ZOOM, 180 * ZOOM
    screen = Image.new("RGB", (1366, 768), bp.BG)
    vx, vy = (1366 - vw) // 2, (768 - vh) // 2
    screen.paste(native.resize((vw, vh), Image.NEAREST), (vx, vy))
    d = ImageDraw.Draw(screen)
    d.text((vx, 4), "Vale in the Executive palette, x4 · state 0 (rigid) · idle S, walk S, walk E, idle N, idle W · "
           "Engineer for scale", font=bst.font(13), fill=bp.INK_TXT)
    # 1x native strip of the same frames (bottom margin), to judge the silhouette at real size.
    strip = Image.new("RGBA", (16 * 6, 24), (0, 0, 0, 0))
    for i, (mod, fr) in enumerate([(eng, eng.IDLE["s"][0]), (vale, vale.IDLE["s"][0]), (vale, vale.IDLE["n"][0]),
                                   (vale, vale.IDLE["e"][0]), (vale, vale.IDLE["w"][0]), (vale, vale.WALK["s"][1])]):
        strip.alpha_composite(Image.fromarray(g.frame_rgba(fr, mod.PAL), "RGBA"), (i * 16, 0))
    bg = Image.new("RGBA", strip.size, rgb(PAL["floor"][3]) + (255,))
    bg.alpha_composite(strip)
    screen.paste(bg.convert("RGB"), (vx + vw - bg.width, vy + vh + 0))
    d.text((vx + vw - bg.width - 150, vy + vh + 6), "1x native on the floor fill", font=bst.font(13), fill=bp.DIM_TXT)
    out = os.path.join(HERE, "vale-in-executive.png")
    screen.save(out)
    print("wrote", out)


if __name__ == "__main__":
    build()
