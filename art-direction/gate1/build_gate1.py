"""Gate 1 review build: the Engineer's four idle facings and one walk cycle.

Keeps the scale-test Orientation layout at 16 px but replaces its placeholder
art (STYLE_BIBLE section 8): environment.py redraws the room to the finish of
reference 08, engineer_sprites.py holds the hand-placed Engineer, and contact
shadows use palette pixels only. Ivo and Mira use their cast sprite modules;
they are scene context, not part of this review.

Run: python3 build_gate1.py   (needs Pillow + numpy)
Outputs (this folder):
  gate1-scene-1366x768.png   still at x4, keyboard inset open
  gate1-scene-native.png     320x180 logical view
  gate1-walk-1366x768.gif    walk east along the route, then all four idles
  gate1-sheet.png            every frame at x1, x2 and x8 with anchor marks
  engineer-atlas.png         native 16x24 atlas, rows S N E W idle, then S N E W walk
  engineer-atlas.json        frame size, anchor, footprint, timing
  engineer-walks.gif         S N E W walk cycles looping at x6
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scale-test"))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
import build_scale_test as bst  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import environment as env  # noqa: E402
import ivo_sprites as ivo  # noqa: E402
import mira_sprites as mira  # noqa: E402

T = 16
ZOOM = 4
IDLE_MS = 500
WALK_MS = 133
SHADOW_OUTER = bst.hx("#3A4160")
SHADOW_CORE = bst.hx("#1C2038")


def frame_rgba(frame, pal=None):
    pal = pal or eng.PAL
    img = np.zeros((len(frame), len(frame[0]), 4), np.uint8)
    for y, row in enumerate(frame):
        for x, ch in enumerate(row):
            c = pal[ch]
            if c:
                img[y, x, :3] = bst.hx(c)
                img[y, x, 3] = 255
    return img


def contact_shadow(c, ax, ay):
    """Compact blue-purple shadow under the anchor, palette pixels only."""
    c.img[ay - 1, ax - 6:ax + 6] = SHADOW_OUTER
    c.img[ay - 1, ax - 4:ax + 4] = SHADOW_CORE
    c.img[ay, ax - 5:ax + 5] = SHADOW_OUTER


def place_px(c, sprite, ax, ay, shadow=True):
    """Paste a 16x24 sprite so its anchor edge (cols 7|8, under row 23) is at (ax, ay)."""
    if shadow:
        contact_shadow(c, ax, ay)
    h, w = sprite.shape[:2]
    x0, y0 = ax - w // 2, ay - h
    a = sprite[:, :, 3] > 0
    region = c.img[y0:y0 + h, x0:x0 + w]
    region[a] = sprite[:, :, :3][a]


def npc(c, kind, foot_x, foot_y):
    place_px(c, bst.character(kind, 1), c.px(foot_x), c.px(foot_y))


def scene(engineer_frame=None, eng_ax=None, eng_ay=None, door_open=0.0):
    c = bst.Canvas(20, 12, T)  # 320x192; the 320x180 view is cropped from it
    room = env.Room()
    room.img = c.img
    env.draw(room, door_open)
    place_px(c, frame_rgba(ivo.IDLE["s"][0], ivo.PAL), c.px(8.0), c.px(3.95))
    if engineer_frame is not None:
        place_px(c, frame_rgba(engineer_frame), eng_ax, eng_ay)
    place_px(c, frame_rgba(mira.IDLE["s"][0], mira.PAL), c.px(17.1), c.px(9.55))
    env.mail_counter(room, 246, 150)  # front occluder, drawn after the actors
    bst.marker(c, "talk", 8.0, 1.95)
    bst.marker(c, "terminal", 10.6, 0.95)
    bst.marker(c, "route", 17.55, 4.45)
    bst.marker(c, "glitch", 3.6, 3.4)
    return c


def overlay(screen, vx, vy, vw, vh):
    """Scale-test HUD and keyboard inset, teaching the east step shown in the walk."""
    d = ImageDraw.Draw(screen)
    f = bst.font
    d.rounded_rectangle([vx + 20, vy + 18, vx + 470, vy + 66], 10, fill=(24, 43, 56, 235))
    d.text((vx + 38, vy + 29), "Visit the four desks", font=f(21, bold=True), fill="#F4F2EC")
    d.text((vx + 285, vy + 31), "2 / 4   ·   Seals 0", font=f(18), fill="#A0DDD4")
    x0, y0, x1, y1 = vx + 20, vy + vh - 214, vx + 500, vy + vh - 20
    d.rounded_rectangle([x0, y0, x1, y1], 14, fill=(24, 43, 56, 242), outline="#19AFA2", width=2)
    d.text((x0 + 22, y0 + 16), "Move east", font=f(22, bold=True), fill="#F4F2EC")
    for lab, lx in [("KEY POSITION", x0 + 22), ("OUTPUT", x0 + 262), ("EFFECT", x0 + 362)]:
        d.text((lx, y0 + 58), lab, font=f(13, bold=True), fill="#9FB3BD")
    bst.keycap(d, x0 + 22, y0 + 84, 104, "Caps", held=True, size=22)
    d.text((x0 + 138, y0 + 98), "+", font=f(26, bold=True), fill="#F4F2EC")
    bst.keycap(d, x0 + 166, y0 + 84, 60, "L")
    d.text((x0 + 262, y0 + 88), "→", font=f(34, mono=True), fill="#F4F2EC")
    d.text((x0 + 262, y0 + 130), "Right arrow", font=f(15), fill="#C5CED0")
    d.text((x0 + 362, y0 + 92), "Step east", font=f(19, bold=True), fill="#E6B750")
    d.text((x0 + 22, y0 + 156), "Hold Caps, then tap L. Release Caps to type.", font=f(16), fill="#C5CED0")


def to_screen(c):
    native = Image.fromarray(c.img[:180, :320])
    vw, vh = 320 * ZOOM, 180 * ZOOM
    scaled = native.resize((vw, vh), Image.NEAREST)
    screen = Image.new("RGBA", (1366, 768), "#151C2B")
    vx, vy = (1366 - vw) // 2, (768 - vh) // 2
    screen.paste(scaled, (vx, vy))
    ov = Image.new("RGBA", screen.size, (0, 0, 0, 0))
    overlay(ov, vx, vy, vw, vh)
    return native, Image.alpha_composite(screen, ov).convert("RGB")


# Engineer stands on the route centre line; feet at y = 6.2 cells.
ROUTE_Y = int(6.2 * T)
START_X = int(11.5 * T)


def door_for(x):
    """The sliding door opens over the last 4 walk frames as the Engineer approaches."""
    return max(0.0, min(1.0, (x - 216) / 32))


def build():
    # Still: south idle at the start of the route.
    native, screen = to_screen(scene(eng.IDLE["s"][0], START_X + 32, ROUTE_Y))
    native.save(os.path.join(HERE, "gate1-scene-native.png"))
    screen.save(os.path.join(HERE, "gate1-scene-1366x768.png"))

    # Walk east two full cycles (4 cells, 8 px per frame), then the four idles.
    frames, durations = [], []
    x = START_X
    for _ in range(2):
        for fr in eng.WALK_E:
            x += 8
            frames.append(to_screen(scene(fr, x, ROUTE_Y, door_for(x)))[1])
            durations.append(WALK_MS)
    for facing in "eswn":
        for _ in range(2):
            for fr in eng.IDLE[facing]:
                frames.append(to_screen(scene(fr, x, ROUTE_Y, door_for(x)))[1])
                durations.append(IDLE_MS)
    frames[0].save(os.path.join(HERE, "gate1-walk-1366x768.gif"), save_all=True,
                   append_images=frames[1:], duration=durations, loop=0, optimize=False)

    # Native atlas: row 0 S, 1 N, 2 E, 3 W idle (2 frames); row 4 E walk (4 frames).
    rows = [eng.IDLE[f] for f in "snew"] + [eng.WALK[f] for f in "snew"]
    atlas = Image.new("RGBA", (16 * 4, 24 * len(rows)), (0, 0, 0, 0))
    for r, fs in enumerate(rows):
        for i, fr in enumerate(fs):
            atlas.paste(Image.fromarray(frame_rgba(fr), "RGBA"), (i * 16, r * 24))
    atlas.save(os.path.join(HERE, "engineer-atlas.png"))
    meta = {
        "status": "Gate 1 approved 2026-10-02; walks S/N/W added after the gate",
        "frame": {"w": 16, "h": 24},
        "anchor": {"name": "feet_bc", "x": 8, "y": 24, "note": "pixel edge between cols 7|8, under row 23"},
        "footprint_cells": [1, 1],
        "animations": {
            "engineer_idle_s": {"row": 0, "frames": 2, "ms": IDLE_MS},
            "engineer_idle_n": {"row": 1, "frames": 2, "ms": IDLE_MS},
            "engineer_idle_e": {"row": 2, "frames": 2, "ms": IDLE_MS},
            "engineer_idle_w": {"row": 3, "frames": 2, "ms": IDLE_MS},
            **{f"engineer_walk_{f}": {"row": 4 + i, "frames": 4, "ms": WALK_MS, "px_per_frame": 8,
                                      "contact_frames": [0, 2]} for i, f in enumerate("snew")},
        },
        "shadow": "drawn by the renderer at the anchor, not baked into frames",
    }
    with open(os.path.join(HERE, "engineer-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=2)

    # Diagnosis sheet: each frame at x1, x2, x8 on the floor colour with anchor marks.
    all_frames = [(f"idle {f.upper()} {i}", fr) for f in "snew" for i, fr in enumerate(eng.IDLE[f])]
    all_frames += [(f"walk {f.upper()} {i}", fr) for f in "snew" for i, fr in enumerate(eng.WALK[f])]
    cell_w, cell_h = 16 * 8 + 24, 24 * 8 + 120
    cols = 8
    sheet = Image.new("RGB", (cols * cell_w + 24, ((len(all_frames) + cols - 1) // cols) * cell_h + 60), "#151C2B")
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), "Engineer Gate 1 frames · x8 (diagnosis) · x2 · x1 native · anchor marked in coral",
           font=bst.font(18, bold=True), fill="#F4F2EC")
    for n, (label, fr) in enumerate(all_frames):
        gx, gy = 24 + (n % cols) * cell_w, 52 + (n // cols) * cell_h
        sp = Image.fromarray(frame_rgba(fr), "RGBA")
        for sc, ox, oy in ((8, 0, 0), (2, 0, 24 * 8 + 12), (1, 48, 24 * 8 + 12)):
            bg = Image.new("RGBA", (16 * sc, 24 * sc), tuple(bst.FLOOR) + (255,))
            bg.alpha_composite(sp.resize((16 * sc, 24 * sc), Image.NEAREST))
            sheet.paste(bg.convert("RGB"), (gx + ox, gy + oy))
        # Anchor: vertical tick at the 7|8 edge, horizontal under row 23 (x8 view).
        d.line([(gx + 64, gy + 24 * 8 - 6), (gx + 64, gy + 24 * 8 + 4)], fill="#EC776D", width=1)
        d.line([(gx + 56, gy + 24 * 8), (gx + 72, gy + 24 * 8)], fill="#EC776D", width=1)
        d.text((gx, gy + 24 * 8 + 12 + 52), label, font=bst.font(15, bold=True), fill="#E6B750")
    sheet.save(os.path.join(HERE, "gate1-sheet.png"))

    # Walk preview: all four directions looping side by side at x6 on the floor colour.
    loop = []
    for i in range(4):
        im = Image.new("RGB", (4 * 16 * 6 + 5 * 24, 24 * 6 + 48), tuple(bst.STONE[3]))
        for n, f in enumerate("snew"):
            sp = Image.fromarray(frame_rgba(eng.WALK[f][i]), "RGBA").resize((96, 144), Image.NEAREST)
            im.paste(sp, (24 + n * 120, 24), sp)
        loop.append(im)
    loop[0].save(os.path.join(HERE, "engineer-walks.gif"), save_all=True, append_images=loop[1:],
                 duration=WALK_MS, loop=0)


if __name__ == "__main__":
    build()
