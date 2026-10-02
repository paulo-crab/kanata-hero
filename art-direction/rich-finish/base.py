"""Shared helpers for the richness mock-ups: render today's approved Orientation scene natively."""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
AD = os.path.join(HERE, "..")
for sub in ("gate1", "scale-test", "cast", "kit"):
    sys.path.insert(0, os.path.join(AD, sub))
import build_gate1 as g  # noqa: E402
import engineer_sprites as eng  # noqa: E402


def baseline():
    """Today's scene: 320x192 canvas, actors included (Engineer idle S on the route)."""
    c = g.scene(eng.IDLE["s"][0], g.START_X + 32, g.ROUTE_Y)
    return c.img.copy()


def save_x4(arr, path, h=180):
    im = Image.fromarray(arr[:h, :320]).resize((1280, h * 4), Image.NEAREST)
    im.save(path)


def scene_parts():
    """Today's scene split so passes run before the floating interaction markers are drawn."""
    import build_scale_test as bst
    import environment as env
    import ivo_sprites as ivo
    import mira_sprites as mira
    c = bst.Canvas(20, 12, g.T)
    room = env.Room()
    room.img = c.img
    env.draw(room, 0.0)
    g.place_px(c, g.frame_rgba(ivo.IDLE["s"][0], ivo.PAL), c.px(8.0), c.px(3.95))
    g.place_px(c, g.frame_rgba(eng.IDLE["s"][0]), g.START_X + 32, g.ROUTE_Y)
    g.place_px(c, g.frame_rgba(mira.IDLE["s"][0], mira.PAL), c.px(17.1), c.px(9.55))
    env.mail_counter(room, 246, 150)
    return c, room


def add_markers(c):
    import build_scale_test as bst
    bst.marker(c, "talk", 8.0, 1.95)
    bst.marker(c, "terminal", 10.6, 0.95)
    bst.marker(c, "route", 17.55, 4.45)
    bst.marker(c, "glitch", 3.6, 3.4)
