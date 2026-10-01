"""Ada in a Night Shift room (task 6.3), plus the lantern rim-light ruling renders.

Run: python3 build_ada_room.py   (needs Pillow + numpy)
Writes into this folder:
  ada-in-nightshift.png   a Night Shift room at x4 on 1366x768: Engineer, Ada idle S and a walk frame
                          in a lamp pool, with the renderer's edge-light rule, lamp pools and night shadow
  ada-rim-ruling.png      the ruling at x8: renderer rim only (A) against baked lantern rim plus the
                          renderer rim (B), on the dark floor and inside a lamp pool

The room reuses the palette-swap renderer of palettes/build_palettes.py (palette_swap, lamp_pool,
rim_light, shadow) and the Orientation environment pieces. Nothing is edited there.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("palettes", "gate1", "cast", "scale-test"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import ada_sprites as ada  # noqa: E402
import build_gate1 as g  # noqa: E402
import build_palettes as bp  # noqa: E402
import build_scale_test as bst  # noqa: E402
import district_palettes as dp  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import environment as env  # noqa: E402

NIGHT = dp.DISTRICTS["nightshift"]
RIM_HEX = NIGHT["accent"][3]
ZOOM = 4


def person(img, mod, frame, ax, ay, night_shadow=(NIGHT["floor"][0], dp.INK[0]), rim=True):
    """The Night Shift renderer order: contact shadow, sprite, then the rim over every outline pixel
    that has a transparent pixel above or to the left. Baked pixels (key R) are not outline and are
    left as drawn."""
    sp = g.frame_rgba(frame, mod.PAL)
    if rim:
        sp = bp.rim_light(sp, RIM_HEX)
    bp.shadow(img, ax, ay, *night_shadow)
    holder = type("C", (), {})()
    holder.img = img
    g.place_px(holder, sp, ax, ay, shadow=False)


def build_room():
    r = env.Room()
    env.floor(r)
    env.north_wall(r)
    # Two rows of inert desks (their chairs are the coral ramp, which the swap turns into lamp light).
    for x, y, seed in ((16, 78, 7), (62, 78, 8), (246, 46, 9), (272, 84, 10)):
        env.desk(r, x, y, seed)
    for i, (x, y) in enumerate(((4, 30), (24, 30), (66, 30), (98, 30), (206, 30), (226, 30), (272, 30))):
        env.pot_plant(r, x, y, 100 + i)
    env.sofa(r, 214, 128)
    env.side_table(r, 252, 140)
    env.bench(r, 140, 62)
    unmapped, img = bp.palette_swap(r.img, "nightshift")
    # Islands of desk light: three pools. One catches Ada's walk frame; the idle pair stands outside.
    bp.lamp_pool(img, "nightshift", 36, 96, 34, 14)
    bp.lamp_pool(img, "nightshift", 80, 96, 34, 14)
    bp.lamp_pool(img, "nightshift", 168, 150, 30, 12)
    # Actors, back to front.
    person(img, ada, ada.IDLE["n"][0], 224, 118)
    person(img, eng, eng.IDLE["s"][0], 96, 150)
    person(img, ada, ada.IDLE["s"][0], 120, 150)
    person(img, ada, ada.WALK["e"][0], 168, 152)
    person(img, ada, ada.IDLE["w"][0], 206, 166)
    return unmapped, img


def to_screen(img):
    native = Image.fromarray(img[:180, :320])
    vw, vh = 320 * ZOOM, 180 * ZOOM
    screen = Image.new("RGB", (1366, 768), "#151C2B")
    screen.paste(native.resize((vw, vh), Image.NEAREST), ((1366 - vw) // 2, (768 - vh) // 2))
    return native, screen


def rim_ruling():
    """x8 tiles: rows = dark floor, lamp pool; groups = A (renderer rim only), B (baked + renderer rim)."""
    z = 8
    facings = (("s", ada.S), ("n", ada.N), ("e", ada.E), ("w", ada.W))
    cell_w, cell_h = 16 * z + 8, 24 * z + 8
    lab_h = 34
    W = 8 * cell_w + 3 * 16 + 24
    im = Image.new("RGB", (W, 2 * cell_h + 2 * lab_h + 36), "#151C2B")
    d = ImageDraw.Draw(im)
    d.text((12, 8), "Lantern rim-light ruling, idle 0 at x8: A = renderer rim only, B = baked lantern-side rim + renderer rim",
           font=bst.font(15, bold=True), fill="#F4F2EC")
    for row, (name, floor_hex) in enumerate((("dark floor, Night Shift fill", NIGHT["floor"][3]),
                                             ("inside a lamp pool", NIGHT["accent"][1]))):
        y0 = 36 + row * (cell_h + lab_h)
        d.text((12, y0 + 4), name, font=bst.font(13), fill="#9FB3BD")
        y0 += lab_h - 12
        for group, baked in enumerate((False, True)):
            for i, (f, fr) in enumerate(facings):
                sp = g.frame_rgba(ada.finish(fr, f, baked=baked), ada.PAL)
                sp = bp.rim_light(sp, RIM_HEX)
                tile = np.zeros((24, 16, 3), np.uint8)
                tile[:] = bp.rgb(floor_hex)
                a = sp[:, :, 3] > 0
                tile[a] = sp[:, :, :3][a]
                big = Image.fromarray(np.kron(tile, np.ones((z, z, 1), np.uint8)))
                x = 12 + (group * 4 + i) * cell_w + group * 16
                im.paste(big, (x, y0))
            d.text((12 + group * (4 * cell_w + 16), y0 + 24 * z + 2), "B  baked + renderer" if baked else "A  renderer only",
                   font=bst.font(13, bold=True), fill="#E6B750")
    return im


def build():
    unmapped, img = build_room()
    native, screen = to_screen(img)
    screen.save(os.path.join(HERE, "ada-in-nightshift.png"))
    rim_ruling().save(os.path.join(HERE, "ada-rim-ruling.png"))
    print(f"room: {unmapped} pixels without a palette mapping; wrote ada-in-nightshift.png, ada-rim-ruling.png")


if __name__ == "__main__":
    build()
