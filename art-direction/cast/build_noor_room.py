"""Noor in a Records-palette room (task 6.1).

Run: python3 build_noor_room.py   (needs Pillow + numpy)
Writes noor-in-records.png: the approved review room (environment.py) recoloured to the Records
palette by the exact swap in palettes/build_palettes.py, shown at x4 on the 1280x720 view.
On the route, left to right: Noor idle N, the Engineer and Noor idle S side by side for scale,
Noor mid-stride walking east, and Noor idle W. People keep their own palettes (they are placed
after the swap), so nothing on a person is recoloured.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("gate1", "palettes", "scale-test"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
sys.path.insert(0, HERE)
import build_gate1 as g  # noqa: E402  (frame_rgba, place_px)
import build_palettes as bp  # noqa: E402  (palette_swap)
import build_scale_test as bst  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import environment as env  # noqa: E402
import noor_sprites as noor  # noqa: E402

ZOOM = 4
ROUTE_Y = int(6.2 * g.T)   # the Engineer's route centre line, as in the Gate 1 scene
ROW2_Y = 146               # open floor below the route, for the other facings
ACTORS = [  # (module, frame, anchor x, anchor y)
    # the route: Noor walking east toward the Engineer and Noor standing beside him, for scale
    (noor, noor.WALK["e"][0], 168, ROUTE_Y),
    (eng, eng.IDLE["s"][0], 204, ROUTE_Y),
    (noor, noor.IDLE["s"][0], 228, ROUTE_Y),
    # the other facings, idle and walking
    (noor, noor.IDLE["n"][0], 40, ROW2_Y),
    (noor, noor.IDLE["e"][0], 100, ROW2_Y),
    (noor, noor.IDLE["w"][0], 126, ROW2_Y),
    (noor, noor.WALK["s"][1], 152, ROW2_Y),
    (noor, noor.WALK["n"][2], 176, ROW2_Y),
    (noor, noor.WALK["w"][0], 218, ROW2_Y),
]


def records_room():
    """The review room's pieces without the Orientation garden, so the floor stays open."""
    c = bst.Canvas(20, 12, g.T)
    room = env.Room()
    room.img = c.img
    env.floor(room)
    env.route(room)
    env.north_wall(room)
    env.east_wall(room, 0.0)
    for i, (x, y) in enumerate([(4, 30), (24, 30), (66, 30), (98, 30), (206, 30), (226, 30), (272, 30),
                                (140, 166), (176, 166), (238, 126)]):
        env.pot_plant(room, x, y, 100 + i)
    env.printer(room)
    env.desk(room, 246, 46, 8)
    env.mail_counter(room, 246, 150)
    unmapped, c.img = bp.palette_swap(c.img, "records")
    return unmapped, c


def build():
    unmapped, c = records_room()
    for mod, frame, ax, ay in sorted(ACTORS, key=lambda a: a[3]):   # back to front
        g.place_px(c, g.frame_rgba(frame, mod.PAL), ax, ay)
    native = Image.fromarray(c.img[:180, :320])
    native.resize((320 * ZOOM, 180 * ZOOM), Image.NEAREST).save(os.path.join(HERE, "noor-in-records.png"))
    print(f"records room: {unmapped} pixels without a palette mapping; wrote noor-in-records.png")


if __name__ == "__main__":
    build()
