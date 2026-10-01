"""Rebuild the Orientation review room from the atlas and a cell layout, and prove it is identical.

Run: python3 build_room.py   (Pillow + numpy)
Reads  orientation-atlas.json/.png and orientation-review-room.json (this folder).
Writes orientation-review-room-native.png (320x192, no actors) and
       orientation-review-room-1366x768.png (the Gate 1 still, drawn from the atlas).
Exit code 1 unless every comparison below has zero differing pixels:
  1. rebuilt room vs the approved room (env.draw + env.mail_counter), door closed / half / open
  2. build_gate1.scene() with environment.py swapped for the atlas renderer, vs the original scene()
     (actors, markers and counter included), door closed / half / open
  3. the x4 1366x768 screen of that scene vs the original screen
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for sub in ("gate1", "scale-test", "cast"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import kitlib  # noqa: E402
import build_gate1 as g  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import environment as env  # noqa: E402

DOOR_STATE = {0.0: "closed", 0.5: "half", 1.0: "open"}
STILL = (eng.IDLE["s"][0], g.START_X + 32, g.ROUTE_Y)


def load(atlas_path=None, layout_path=None):
    import json
    atlas = kitlib.Atlas(atlas_path or os.path.join(HERE, "orientation-atlas.json"))
    with open(layout_path or os.path.join(HERE, "orientation-review-room.json")) as fh:
        layout = json.load(fh)
    return atlas, layout


def with_states(layout, **states):
    out = dict(layout)
    out["states"] = dict(layout["states"], **states)
    return out


def rebuild(layout, atlas, door_open=0.0, layers=None, base=None):
    lay = with_states(layout, records_door=DOOR_STATE[door_open])
    return kitlib.render_layout(lay, atlas, layers=layers, base=base)


class AtlasEnvironment:
    """Context manager: swap environment.draw / mail_counter for the atlas renderer so the
    unmodified build_gate1.scene() draws the room from atlas data."""

    def __init__(self, layout, atlas):
        self.layout, self.atlas = layout, atlas

    def __enter__(self):
        self.saved = (env.draw, env.mail_counter)
        back = set(kitlib.LAYERS) - {"front_prop"}

        def draw(room, door_open=0.0):
            rebuild(self.layout, self.atlas, door_open, layers=back, base=room.img)

        def mail_counter(room, x, y):
            assert (x, y) == (246, 150)
            rebuild(self.layout, self.atlas, 0.0, layers={"front_prop"}, base=room.img)

        env.draw, env.mail_counter = draw, mail_counter
        return self

    def __exit__(self, *exc):
        env.draw, env.mail_counter = self.saved


def approved_room(door_open):
    r = env.Room()
    env.draw(r, door_open)
    env.mail_counter(r, 246, 150)
    return r.img


def count(a, b):
    return int(np.any(a != b, axis=2).sum())


def verify(layout, atlas, verbose=True):
    results = {}
    for d in DOOR_STATE:
        results[f"room, door {DOOR_STATE[d]}"] = count(rebuild(layout, atlas, d), approved_room(d))
    originals = {d: g.scene(*STILL, door_open=d) for d in DOOR_STATE}
    screens = {d: g.to_screen(originals[d])[1] for d in DOOR_STATE}
    with AtlasEnvironment(layout, atlas):
        for d in DOOR_STATE:
            c = g.scene(*STILL, door_open=d)
            results[f"scene, door {DOOR_STATE[d]}"] = count(c.img, originals[d].img)
            scr = g.to_screen(c)[1]
            results[f"x4 screen, door {DOOR_STATE[d]}"] = int(
                np.any(np.array(scr) != np.array(screens[d]), axis=2).sum())
    if verbose:
        for k, v in results.items():
            print(f"{k:28s} differing pixels: {v}")
    return results


def build(write=True):
    atlas, layout = load()
    results = verify(layout, atlas)
    if write:
        room = rebuild(layout, atlas, 0.0)
        Image.fromarray(room).save(os.path.join(HERE, "orientation-review-room-native.png"))
        with AtlasEnvironment(layout, atlas):
            screen = g.to_screen(g.scene(*STILL))[1]
        screen.save(os.path.join(HERE, "orientation-review-room-1366x768.png"))
    return results


if __name__ == "__main__":
    res = build()
    bad = {k: v for k, v in res.items() if v}
    print("ZERO DIFF" if not bad else f"DIFFERS: {bad}")
    sys.exit(1 if bad else 0)
