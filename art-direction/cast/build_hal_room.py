"""Hal in a Systems-palette room (task 6.2): the Orientation review room recoloured to Systems.

Run: python3 build_hal_room.py   (needs Pillow + numpy)
Writes hal-in-systems.png (1366x768, x4): the room's furniture is drawn by gate1/environment.py and
recoloured with build_palettes.palette_swap (an exact hex swap, 0 unmapped pixels is expected), then the
people are drawn with their own palettes on top, so no person pixel is ever swapped. The Engineer, Hal
idle S, a Hal walk-east contact and a Hal walk-west frame stand on the route for scale.

Also writes hal-props-atlas.png/.json (the stool prop), hal-poses-in-systems.png (crouch, seated on the
stool and the false-panel pull in the real Systems reference room) and hal-poses-x8.png.
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


# ---------------------------------------------------------------------------------------------------------------
# Working poses and the stool prop (feat/cast-vale-hal-poses)
# ---------------------------------------------------------------------------------------------------------------
def build_props():
    """hal-props-atlas.png/.json: the one-cell stool prop, in the format of the kit atlases (kit/atlas.schema.json)."""
    import json
    art = Image.fromarray(g.frame_rgba(hal.STOOL[6:], hal.PAL), "RGBA")    # the 16x10 art, cell rows 6-15
    assert art.size == (16, 10)
    sp = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    sp.paste(art, (0, 0))                                                   # kit convention: content at the top-left
    sp.save(os.path.join(HERE, "hal-props-atlas.png"))
    entry = dict(hal.STOOL_ENTRY, rect=[0, 0, 16, 16])
    entry["note"] = ("folding stool, steel frame and dark canvas from the ink ramp; placed under a seated Hal "
                     "(hal-atlas.json: hal_seated_stool_*, stool_cell_in_frame_px [0, 8]) so the stool anchor (8, 16) "
                     "lands on Hal's anchor (8, 24): the sprite's top-left is then (0, 14) in Hal's 16x24 frame. Draw it in "
                     "rear_prop, then Hal in actor: Hal always draws over it")
    meta = {"schema": "kanata-hero/kit/atlas.schema.json", "kit": "hal_props", "image": "hal-props-atlas.png",
            "tile": 16,
            "layers": ["floor", "rear_wall", "floor_marking", "rear_prop", "shadow", "actor", "front_prop", "light"],
            "status": "Candidate (poses branch)", "source": "cast/hal_sprites.py STOOL", "entries": [entry]}
    with open(os.path.join(HERE, "hal-props-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print("wrote hal-props-atlas.png/.json")
    import subprocess   # the kit checker validates it against kit/atlas.schema.json (rects, anchor, shadow, collision)
    kit = os.path.join(HERE, "..", "kit")
    r = subprocess.run([sys.executable, "check_atlas.py", os.path.join(HERE, "hal-props-atlas.json")],
                       cwd=kit, capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1])
    if r.returncode:
        print(r.stdout)
        sys.exit(1)


def _actor(img, frame, ax, ay, shadow=True):
    from build_palettes import shadow as drop
    import district_palettes as dp
    sp = g.frame_rgba(frame, hal.PAL)
    if shadow:
        drop(img, ax, ay, dp.INK[2], dp.INK[1])
    c = type("C", (), {})()
    c.img = img
    g.place_px(c, sp, ax, ay, shadow=False)


def _stool(img, ax, ay):
    """Blit the stool cell with its anchor (8, 16) on (ax, ay)."""
    sp = g.frame_rgba(hal.STOOL, hal.PAL)
    x0, y0 = ax - 8, ay - 16
    a = sp[:, :, 3] > 0
    img[y0:y0 + 16, x0:x0 + 16][a] = sp[:, :, :3][a]


def _systems_room(state="before"):
    import json
    sys.path.insert(0, os.path.join(HERE, "..", "kit"))
    import kitlib
    atlas = kitlib.Atlas(os.path.join(HERE, "..", "kit", "systems-atlas.json"))
    with open(os.path.join(HERE, "..", "kit", "systems-reference-room.json")) as fh:
        layout = json.load(fh)
    layout["states"] = dict(layout["states"], routing_machine=state)
    return kitlib.render_layout(layout, atlas)


def build_poses():
    """hal-poses-in-systems.png: crouching, seated on the stool and pulling the false panel, in the real Systems
    reference room at x4 (the room is drawn from systems-atlas; Hal and the stool sit on top), and
    hal-poses-x8.png: the same poses at x8 for the silhouette read."""
    from PIL import ImageDraw
    X = hal.EXTRA
    img = _systems_room("before").copy()
    # crouching at the machine's west port (N), and in the open floor facing S, E and W
    _actor(img, X["crouch_repair"]["n"][0], 68, 126)
    for f, x in (("e", 26), ("s", 56), ("w", 86)):
        _actor(img, X["crouch_repair"][f][0], x, 176)
    # seated on the stool (S and E)
    for f, x in (("s", 124), ("e", 156)):
        _stool(img, x, 176)
        _actor(img, X["seated_stool"][f][0], x, 176)
    # pulling the false panel (N), four frames of the one-shot along the machine's face
    for i, x in enumerate((96, 120, 144, 168)):
        _actor(img, X["false_panel_pull"]["n"][i], x, 126)
    scale = 4
    big = Image.fromarray(img).resize((320 * scale, 192 * scale), Image.NEAREST)
    screen = Image.new("RGB", (1366, 768), "#151C2B")
    ox = (1366 - big.width) // 2
    screen.paste(big, (ox, 0))
    d = ImageDraw.Draw(screen)
    bg = "#151C2B"

    def label(nx, ny, text):
        x, y = ox + nx * scale, ny * scale
        d.rectangle((x - 2, y - 2, x + 9 * len(text) + 2, y + 15), fill=bg)
        d.text((x, y), text, font=bst.font(12), fill="#F4F2EC")
    label(4, 181, "crouch_repair E, S, W (frame 0)")
    label(108, 181, "seated_stool S, E on the stool prop")
    label(150, 74, "crouch_repair N at the west port (left of the panel)")
    label(150, 82, "false_panel_pull N, frames 0-3 (along the face)")
    screen.save(os.path.join(HERE, "hal-poses-in-systems.png"))
    print("wrote hal-poses-in-systems.png")

    # x8 sheet: the silhouettes at the size the gestures must read
    Z, gap = 8, 12
    floor = (233, 229, 218)
    rows = [
        [(f"crouch {f.upper()}", X["crouch_repair"][f][0], None) for f in "snew"]
        + [(f"seated {f.upper()} + stool", X["seated_stool"][f][0], True) for f in "sew"],
        [(f"pull N {i}", X["false_panel_pull"]["n"][i], None) for i in range(4)]
        + [(f"pull E {i}", X["false_panel_pull"]["e"][i], None) for i in range(4)],
    ]
    W = 1366
    sheet = Image.new("RGB", (W, 2 * (24 * Z + 40) + 40), bg)
    d = ImageDraw.Draw(sheet)
    d.text((16, 8), "Hal working poses at x8 (silhouette read): crouch_repair, seated_stool with the stool prop, "
           "false_panel_pull", font=bst.font(13), fill="#F4F2EC")
    for r, row in enumerate(rows):
        for i, (label_, fr, stool) in enumerate(row):
            frame = fr
            if stool:
                sf = ["." * 16] * 8 + hal.STOOL
                frame = ["".join(hc if hc != "." else sc for hc, sc in zip(hrow, srow)) for hrow, srow in zip(fr, sf)]
            sp = Image.fromarray(g.frame_rgba(frame, hal.PAL), "RGBA")
            cell = Image.new("RGBA", sp.size, floor + (255,))
            cell.alpha_composite(sp)
            x, y = 16 + i * (16 * Z + gap), 32 + r * (24 * Z + 40)
            sheet.paste(cell.resize((16 * Z, 24 * Z), Image.NEAREST).convert("RGB"), (x, y))
            d.text((x, y + 24 * Z + 4), label_, font=bst.font(12), fill="#9FB3BD")
    sheet.save(os.path.join(HERE, "hal-poses-x8.png"))
    print("wrote hal-poses-x8.png")


if __name__ == "__main__":
    build()
    build_props()
    build_poses()
