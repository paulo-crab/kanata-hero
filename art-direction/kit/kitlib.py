"""Generic district-kit helpers: pack an atlas, load it, and render a layout from it.

Nothing here is Orientation-specific, so every district kit reuses it. The format
is described in ORIENTATION_KIT_SPEC.md and enforced by atlas.schema.json.

Pieces:
  capture(...)      render a drawing function onto two sentinel backgrounds and keep
                    only the pixels it painted (transparent elsewhere)
  pack(...)         shelf-pack sprites onto a 16 px grid and return (png, rects)
  Atlas             loads <name>-atlas.json + png, resolves entries and state sets
  render_layout()   composite a layout (floor grid + placements) from an atlas
"""
import json
import os

import numpy as np
from PIL import Image

T = 16
LAYERS = ["floor", "rear_wall", "floor_marking", "rear_prop", "shadow", "actor", "front_prop", "light"]
SENTINELS = ((7, 11, 13), (243, 241, 239))  # never palette colours


def hexs(c):
    return "#%02X%02X%02X" % tuple(int(v) for v in c)


def hex2rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ capture

def painted_diff(prev, cur, bg=None):
    """Mask of pixels that changed between two RGB snapshots."""
    return np.any(prev != cur, axis=2)


def capture(draw, make_room, size=None):
    """Run draw(room) on two sentinel backgrounds.

    Returns (rgba, painted_mask) at room size. A pixel counts as painted when it
    differs from the sentinel on either run; the two runs must agree on its colour,
    which proves the piece does not depend on what is underneath it."""
    outs = []
    for bg in SENTINELS:
        r = make_room()
        r.img[:] = bg
        draw(r)
        outs.append(r.img.copy())
    masks = [np.any(o != np.array(bg, np.uint8), axis=2) for o, bg in zip(outs, SENTINELS)]
    painted = masks[0] | masks[1]
    if not np.array_equal(outs[0][painted], outs[1][painted]):
        bad = np.any(outs[0] != outs[1], axis=2) & painted
        ys, xs = np.nonzero(bad)
        raise AssertionError(f"piece depends on its background at {len(ys)} px, first ({xs[0]},{ys[0]})")
    rgba = np.zeros(outs[0].shape[:2] + (4,), np.uint8)
    rgba[painted, :3] = outs[0][painted]
    rgba[painted, 3] = 255
    return rgba, painted


def bbox(mask):
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def crop_rgba(rgba, box):
    x0, y0, x1, y1 = box
    return rgba[y0:y1, x0:x1].copy()


# ------------------------------------------------------------------ packing

def cells(n):
    return -(-n // T)


def pack(sprites, width_cells=40):
    """sprites: ordered list of (name, rgba). Shelf-packs left to right, rounding each
    rect up to whole cells. Returns (PIL image, {name: [x, y, w, h]})."""
    rects = {}
    x = y = row_h = 0
    for name, sp in sprites:
        w, h = cells(sp.shape[1]) * T, cells(sp.shape[0]) * T
        if x and x + w > width_cells * T:
            x, y, row_h = 0, y + row_h, 0
        rects[name] = [x, y, w, h]
        x += w
        row_h = max(row_h, h)
    H = y + row_h
    img = np.zeros((H, width_cells * T, 4), np.uint8)
    for name, sp in sprites:
        rx, ry, _, _ = rects[name]
        img[ry:ry + sp.shape[0], rx:rx + sp.shape[1]] = sp
    return Image.fromarray(img, "RGBA"), rects


# ------------------------------------------------------------------ atlas

class Atlas:
    def __init__(self, json_path, png_path=None):
        self.path = json_path
        with open(json_path) as fh:
            self.meta = json.load(fh)
        png_path = png_path or os.path.join(os.path.dirname(json_path), self.meta["image"])
        self.img = np.array(Image.open(png_path).convert("RGBA"))
        self.entries = {e["name"]: e for e in self.meta["entries"]}
        self.animations = self.meta.get("animations", {})
        self.landmarks = self.meta.get("landmarks", {})

    def sprite(self, name):
        e = self.entries[name]
        x, y, _, _ = e["rect"]
        w, h = e["size_px"]
        return self.img[y:y + h, x:x + w]

    def state_entries(self, anim, state=None):
        a = self.animations[anim]
        return a["states"][state or a["default"]]["entries"]


# ------------------------------------------------------------------ layout

def floor_cell_names(layout):
    fl = layout["floor"]
    out = []
    for cy, row in enumerate(fl["rows"]):
        for cx, ch in enumerate(row):
            out.append((fl["legend"][ch], cx * T, cy * T))
    return out


def expand(layout, atlas):
    """Flatten a layout into draw items [(layer_index, order, entry_name, px, py)].

    px, py is the placed footprint origin in room pixels (cell * 16 + offset); the
    sprite is drawn at that point minus the entry's footprint.origin_px."""
    items = []
    order = 0
    states = layout.get("states", {})

    def add(name, fx, fy):
        nonlocal order
        e = atlas.entries[name]
        items.append((LAYERS.index(e["layer"]), order, name, fx, fy))
        order += 1

    for name, x, y in floor_cell_names(layout):
        add(name, x, y)
    for p in layout["placements"]:
        fx = p["cell"][0] * T + p.get("offset", [0, 0])[0]
        fy = p["cell"][1] * T + p.get("offset", [0, 0])[1]
        if "entry" in p:
            add(p["entry"], fx, fy)
        elif "anim" in p:
            st = p.get("state") or states.get(p["anim"])
            for n in atlas.state_entries(p["anim"], st):
                add(n, fx, fy)
        elif "landmark" in p:
            lm = atlas.landmarks[p["landmark"]]
            st = p.get("state") or states.get(p["landmark"]) or lm["default_state"]
            for n in lm["states"][st]["parts"]:
                add(n, fx, fy)
            lamps = lm["states"][st].get("lamps")
            if lamps:
                for dx, dy in lamps["offsets_px"]:
                    for n in atlas.state_entries(lamps["anim"], lamps["state"]):
                        add(n, fx + dx, fy + dy)
    return items


def blit(canvas, rgba, x, y, composite):
    h, w = rgba.shape[:2]
    H, W = canvas.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    src = rgba[y0 - y:y1 - y, x0 - x:x1 - x]
    dst = canvas[y0:y1, x0:x1]
    m = src[:, :, 3] > 0
    mode = composite.get("mode", "over")
    if mode == "where_color":
        m &= np.all(dst == np.array(hex2rgb(composite["color"]), np.uint8), axis=2)
    dst[m] = src[:, :, :3][m]


def render_layout(layout, atlas, layers=None, base=None):
    """Composite the layout into an RGB array. layers limits which draw layers run."""
    cw, ch = layout["size_cells"]
    canvas = np.zeros((ch * T, cw * T, 3), np.uint8) if base is None else base
    for li, _, name, fx, fy in sorted(expand(layout, atlas), key=lambda t: (t[0], t[1])):
        if layers is not None and LAYERS[li] not in layers:
            continue
        e = atlas.entries[name]
        ox, oy = e["footprint"]["origin_px"]
        blit(canvas, atlas.sprite(name), fx - ox, fy - oy, e.get("composite", {"mode": "over"}))
    return canvas


def collision_grid(layout, atlas, states=None):
    """Blocked cells (bool array [rows, cols]) from every placement's collision mask."""
    cw, ch = layout["size_cells"]
    grid = np.zeros((ch, cw), bool)
    for li, _, name, fx, fy in expand(layout, atlas):
        e = atlas.entries[name]
        for ry, row in enumerate(e["collision"]):
            for rx, c in enumerate(row):
                if c == "1":
                    cx, cy = fx // T + rx, fy // T + ry
                    if 0 <= cx < cw and 0 <= cy < ch:
                        grid[cy, cx] = True
    return grid
