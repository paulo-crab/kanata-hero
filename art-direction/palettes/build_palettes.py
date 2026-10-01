"""Build the district palette review renders (tasks 5.1, 5.2).

Run: python3 build_palettes.py   (needs Pillow + numpy)
Writes into this folder:
  palettes-sheet.png            all five districts' 8 ramps with hexes, the five sample tiles,
                                the seven-character skin/hair ramps and the 1x head comparison
  palettes-tile-<district>.png  one sample tile per district at x4 (floor, wall, desk, plants,
                                two people): Orientation's environment pieces recoloured by an
                                exact palette swap, people drawn with their own palettes
  cast-heads-x8.png             the seven heads at x8 on two head templates, for diagnosis
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("palettes", "gate1", "cast", "scale-test"):
    sys.path.insert(0, os.path.join(HERE, "..", sub) if sub != "palettes" else HERE)
import build_gate1 as g  # noqa: E402  (frame_rgba, place_px)
import build_scale_test as bst  # noqa: E402
import district_palettes as dp  # noqa: E402
import engineer_sprites as eng  # noqa: E402
import environment as env  # noqa: E402
import ivo_sprites as ivo  # noqa: E402

BG = "#151C2B"
INK_TXT = "#F4F2EC"
DIM_TXT = "#9FB3BD"
ZOOM = 4
TILE_W, TILE_H = 88, 84  # logical px of a sample tile
WALL_ROWS = 34  # env.north_wall occupies rows 0-33; its stone is the wall ramp

ORIENT = dp.DISTRICTS["orientation"]
# Orientation pieces use these ramps; role -> source ramp of environment.py
SWAP_SRC = {
    "floor": bst.STONE, "glass": bst.GLASS, "wood": bst.WOOD, "foliage": bst.GREEN,
    "accent": bst.BRASS,
}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def text_on(h):
    r, gg, b = rgb(h)
    return "#101420" if 0.299 * r + 0.587 * gg + 0.114 * b > 140 else "#F4F2EC"


# ------------------------------------------------------------------ tile render

def palette_swap(img, district):
    """Recolour an Orientation-drawn image into a district by exact hex match.

    Stone above WALL_ROWS becomes the wall ramp, stone below it the floor ramp; brass and
    coral both become the accent ramp. Returns the number of pixels with no mapping."""
    pal = dp.DISTRICTS[district]
    out = img.copy()
    rows = np.arange(img.shape[0])[:, None] < WALL_ROWS
    done = np.zeros(img.shape[:2], bool)

    def swap(src_ramp, dst_ramp, region=None):
        for s, d in zip(src_ramp, dst_ramp):
            m = np.all(img == s, axis=2) & ~done
            if region is not None:
                m &= region
            out[m] = rgb(d)
            done[m] = True

    for s in bst.INK:  # shared ramp: leave as is
        done |= np.all(img == s, axis=2)
    swap(bst.STONE, pal["wall"], rows & np.ones(img.shape[:2], bool))
    swap(bst.STONE, pal["floor"])
    swap(bst.GLASS, pal["glass"])
    swap(bst.WOOD, pal["wood"])
    swap(bst.GREEN, pal["foliage"])
    swap(bst.BRASS, pal["accent"])
    swap(bst.CORAL, dp.ORIENTATION_EXTRA["coral"] if district == "orientation" else pal["accent"])
    return int((~done).sum()), out


def rim_light(sprite, rim_hex):
    """Night Shift edge-light rule: the outline pixels facing the light (upper-left, i.e. with a
    transparent pixel above or to the left) are drawn in the rim colour."""
    out = sprite.copy()
    h, w = sprite.shape[:2]
    outline = np.array(rgb(dp.INK[0]), np.uint8)
    for y in range(h):
        for x in range(w):
            if sprite[y, x, 3] and np.array_equal(sprite[y, x, :3], outline):
                up = y == 0 or not sprite[y - 1, x, 3]
                left = x == 0 or not sprite[y, x - 1, 3]
                if up or left:
                    out[y, x, :3] = rgb(rim_hex)
    return out


def lamp_pool(img, district, cx, cy, rx, ry):
    """Night Shift pool of desk light: floor fill becomes accent[1], slab joints accent[0]."""
    pal = dp.DISTRICTS[district]
    yy, xx = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    pool = ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1
    for src, dst in ((pal["floor"][3], pal["accent"][1]), (pal["floor"][2], pal["accent"][0]),
                     (pal["floor"][1], pal["accent"][0])):
        m = pool & np.all(img == rgb(src), axis=2)
        img[m] = rgb(dst)


def shadow(img, ax, ay, outer, core):
    img[ay - 1, ax - 6:ax + 6] = rgb(outer)
    img[ay - 1, ax - 4:ax + 4] = rgb(core)
    img[ay, ax - 5:ax + 5] = rgb(outer)


def render_tile(district):
    r = env.Room()
    env.floor(r)
    env.north_wall(r)
    env.desk(r, 6, 44, 7)
    env.pot_plant(r, 4, 31, 100)
    env.pot_plant(r, 56, 31, 103)
    unmapped, img = palette_swap(r.img, district)
    pal = dp.DISTRICTS[district]
    night = district == "nightshift"
    if night:
        lamp_pool(img, district, 24, 76, 30, 13)
    outer, core = (pal["floor"][0], dp.INK[0]) if night else (dp.INK[2], dp.INK[1])
    c = type("C", (), {})()
    c.img = img
    people = [(eng, eng.IDLE["s"][0], 40, 78), (ivo, ivo.IDLE["s"][0], 68, 82)]
    for mod, frame, ax, ay in people:
        sp = g.frame_rgba(frame, mod.PAL)
        if night:
            sp = rim_light(sp, dp.DISTRICTS[dp.NIGHT_RIM[0]][dp.NIGHT_RIM[1]][dp.NIGHT_RIM[2]])
        shadow(img, ax, ay, outer, core)
        g.place_px(c, sp, ax, ay, shadow=False)
    crop = img[:TILE_H, :TILE_W]
    return unmapped, Image.fromarray(crop).resize((TILE_W * ZOOM, TILE_H * ZOOM), Image.NEAREST)


# ------------------------------------------------------------------ cast heads

def head_template(mod):
    return [row for row in mod.S[:10]] if hasattr(mod, "S") else [row for row in mod.IDLE["s"][0][:10]]


def head_img(rows, hair, skin):
    pal = {".": None, "o": dp.INK[0]}
    pal.update({k: v for k, v in zip("ABCD", hair)})
    pal.update({k: v for k, v in zip("klmn", skin)})
    arr = np.zeros((len(rows), 16, 4), np.uint8)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != "." and pal.get(ch):
                arr[y, x, :3] = rgb(pal[ch])
                arr[y, x, 3] = 255
    return Image.fromarray(arr, "RGBA")


def heads_strip(rows, scale, floor_hex, gap=6, pad=4):
    names = dp.CAST_ORDER
    allc = dp.all_cast_ramps()
    w = len(names) * (16 * scale + gap) + gap
    h = 10 * scale + 2 * pad
    im = Image.new("RGBA", (w, h), floor_hex)
    for i, n in enumerate(names):
        hd = head_img(rows, allc[n]["hair"], allc[n]["skin"]).resize((16 * scale, 10 * scale), Image.NEAREST)
        im.alpha_composite(hd, (gap + i * (16 * scale + gap), pad))
    return im


# ------------------------------------------------------------------ sheet

def swatch_row(d, x, y, steps, sw=46, sh=40):
    f = bst.font(10)
    for i, h in enumerate(steps):
        d.rectangle([x + i * sw, y, x + (i + 1) * sw - 1, y + sh - 1], fill=h)
        d.text((x + i * sw + 3, y + sh - 14), h.lstrip("#"), font=f, fill=text_on(h))


def build():
    tiles, notes = {}, []
    for district in dp.DISTRICTS:
        unmapped, tile = render_tile(district)
        tile.save(os.path.join(HERE, f"palettes-tile-{district}.png"))
        tiles[district] = tile
        notes.append((district, unmapped))
    for district, n in notes:
        print(f"tile {district}: {n} pixels without a palette mapping")

    allc = dp.all_cast_ramps()
    # heads at x8 for diagnosis
    t_eng, t_ivo = head_template(eng), head_template(ivo)
    floor = dp.DISTRICTS["orientation"]["floor"][3]
    x8 = Image.new("RGB", (1100, 2 * 10 * 8 + 3 * 28), BG)
    for k, rows in enumerate((t_eng, t_ivo)):
        strip = heads_strip(rows, 8, floor).convert("RGB")
        x8.paste(strip, (12, 28 + k * (10 * 8 + 8 + 28)))
    d = ImageDraw.Draw(x8)
    d.text((12, 6), "Cast heads x8 · " + " · ".join(n.capitalize() for n in dp.CAST_ORDER),
           font=bst.font(14, bold=True), fill=INK_TXT)
    x8 = x8.crop((0, 0, 12 + strip.width + 12, x8.height))
    x8.save(os.path.join(HERE, "cast-heads-x8.png"))

    # --- sheet
    SW, SH, RG = 46, 40, 16
    ramp_w = 4 * SW
    left = 150
    sheet_w = left + 9 * (ramp_w + RG) + 20
    block_h = SH + 34
    y_top = 64
    y_tiles = y_top + 5 * block_h + 30
    y_cast = y_tiles + TILE_H * ZOOM + 70
    cast_h = 7 * 56 + 40
    y_heads = y_cast + cast_h + 10
    sheet = Image.new("RGB", (sheet_w, y_heads + 220), BG)
    d = ImageDraw.Draw(sheet)
    d.text((20, 16), "Kanata Hero district palettes · 8 ramps x 4 steps, shadow to light · Director decision 2026-10-02",
           font=bst.font(18, bold=True), fill=INK_TXT)
    d.text((20, 40), "Ink and violet are identical in every district. Orientation is the approved palette (wall shares the stone "
           "ramp; coral shown as ninth ramp).", font=bst.font(13), fill=DIM_TXT)
    for row, (district, pal) in enumerate(dp.DISTRICTS.items()):
        y = y_top + row * block_h
        d.text((20, y + 6), dp.NAMES[district], font=bst.font(17, bold=True), fill=INK_TXT)
        if district == "orientation":
            d.text((20, y + 26), "approved 2026-10-01", font=bst.font(11), fill=DIM_TXT)
        elif district == "nightshift":
            d.text((20, y + 26), "dark floor: edge-light rule", font=bst.font(11), fill=DIM_TXT)
        for i, role in enumerate(dp.ROLES):
            x = left + i * (ramp_w + RG)
            swatch_row(d, x, y, pal[role], SW, SH)
            tag = role + (" (device)" if role in dp.DEVICE_RAMPS[district] else "")
            d.text((x, y + SH + 4), tag, font=bst.font(11), fill=DIM_TXT)
    # Orientation's ninth ramp
    swatch_row(d, left + 8 * (ramp_w + RG), y_top, dp.ORIENTATION_EXTRA["coral"], SW, SH)
    d.text((left + 8 * (ramp_w + RG), y_top + SH + 4), "coral (people, Orientation only)", font=bst.font(11), fill=DIM_TXT)

    d.text((20, y_tiles - 22), "Sample tiles at x4: Orientation's floor, glass wall, desk and planters recoloured by palette swap; "
           "Engineer and Ivo drawn with their own palettes", font=bst.font(13), fill=DIM_TXT)
    for i, district in enumerate(dp.DISTRICTS):
        x = 20 + i * (TILE_W * ZOOM + 16)
        sheet.paste(tiles[district], (x, y_tiles))
        d.text((x, y_tiles + TILE_H * ZOOM + 4), dp.NAMES[district], font=bst.font(13, bold=True), fill=INK_TXT)

    # cast ramps
    d.text((20, y_cast - 8), "Cast skin and hair ramps, shadow to light. New: Noor, Hal, Ada, Vale", font=bst.font(13), fill=DIM_TXT)
    for i, n in enumerate(dp.CAST_ORDER):
        y = y_cast + 16 + i * 56
        d.text((20, y + 8), n.capitalize(), font=bst.font(15, bold=True), fill=INK_TXT)
        d.text((20, y + 28), "approved" if n not in dp.CAST_RAMPS else "new (5.2)", font=bst.font(11), fill=DIM_TXT)
        swatch_row(d, left, y, allc[n]["hair"], SW, 44)
        d.text((left + 4 * SW + 6, y + 14), "hair", font=bst.font(11), fill=DIM_TXT)
        swatch_row(d, left + 4 * SW + 50, y, allc[n]["skin"], SW, 44)
        d.text((left + 8 * SW + 56, y + 14), "skin", font=bst.font(11), fill=DIM_TXT)

    # 1x head comparison beside the ramps
    hx = left + 8 * SW + 120
    d.text((hx, y_cast - 8), "Heads at 1x, then x4 (Engineer head template, Ivo head template)", font=bst.font(13), fill=DIM_TXT)
    for k, rows in enumerate((t_eng, t_ivo)):
        s1 = heads_strip(rows, 1, floor)
        sheet.paste(s1.convert("RGB"), (hx, y_cast + 16 + k * 22))
    for k, rows in enumerate((t_eng, t_ivo)):
        s4 = heads_strip(rows, 4, floor)
        sheet.paste(s4.convert("RGB"), (hx, y_cast + 70 + k * (10 * 4 + 14)))
    names_y = y_cast + 70 + 2 * (10 * 4 + 14)
    for i, n in enumerate(dp.CAST_ORDER):
        d.text((hx + 6 + i * (16 * 4 + 6), names_y), n.capitalize(), font=bst.font(11), fill=INK_TXT)
    sheet = sheet.crop((0, 0, sheet_w, y_cast + cast_h + 10))
    sheet.save(os.path.join(HERE, "palettes-sheet.png"))
    print("wrote palettes-sheet.png, 5 tiles, cast-heads-x8.png")


if __name__ == "__main__":
    build()
