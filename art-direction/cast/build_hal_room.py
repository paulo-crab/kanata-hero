"""Hal in a Systems-palette room (task 6.2): the Orientation review room recoloured to Systems.

Run: python3 build_hal_room.py   (needs Pillow + numpy)
Writes hal-in-systems.png (1366x768, x4): the room's furniture is drawn by gate1/environment.py and
recoloured with build_palettes.palette_swap (an exact hex swap, 0 unmapped pixels is expected), then the
people are drawn with their own palettes on top, so no person pixel is ever swapped. The Engineer, Hal
idle S, a Hal walk-east contact and a Hal walk-west frame stand on the route for scale.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("palettes", "gate1", "scale-test", "cast"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import build_gate1 as g  # noqa: E402
import build_palettes as bp  # noqa: E402
import build_scale_test as bst  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import environment as env  # noqa: E402
import hal_sprites as hal  # noqa: E402

DISTRICT = "systems"
ZOOM = 4


def room_without_people():
    c = bst.Canvas(20, 12, g.T)
    room = env.Room()
    room.img = c.img
    env.floor(room)
    env.route(room)
    env.north_wall(room)
    env.east_wall(room, 0.0)
    for i, (x, y) in enumerate([(4, 30), (24, 30), (66, 30), (98, 30), (206, 30), (226, 30), (272, 30),
                                (56, 96), (238, 126), (140, 166), (176, 166)]):
        env.pot_plant(room, x, y, 100 + i)
    env.side_table(room, 240, 160)
    env.printer(room)
    env.desk(room, 16, 78, 7)
    env.desk(room, 246, 46, 8)
    env.bench(room, 228, 112)
    return c


def build():
    c = room_without_people()
    unmapped, img = bp.palette_swap(c.img, DISTRICT)
    c.img = img
    print(f"systems room: {unmapped} pixels without a palette mapping")
    y = g.ROUTE_Y
    people = [(hal.WALK["w"][0], hal.PAL, 106), (eng.IDLE["s"][0], eng.PAL, 138),
              (hal.IDLE["s"][0], hal.PAL, 164), (hal.WALK["e"][0], hal.PAL, 198),
              (hal.IDLE["n"][0], hal.PAL, 228)]
    for frame, pal, x in people:
        g.place_px(c, g.frame_rgba(frame, pal), x, y)
    native = Image.fromarray(c.img[:180, :320])
    scaled = native.resize((320 * ZOOM, 180 * ZOOM), Image.NEAREST)
    screen = Image.new("RGB", (1366, 768), "#151C2B")
    screen.paste(scaled, ((1366 - scaled.width) // 2, (768 - scaled.height) // 2))
    screen.save(os.path.join(HERE, "hal-in-systems.png"))
    print("wrote hal-in-systems.png")


if __name__ == "__main__":
    build()
