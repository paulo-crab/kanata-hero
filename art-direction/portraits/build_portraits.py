"""Build the portrait outputs: template sheet, character sheet, atlas.

Run: python3 build_portraits.py   (needs Pillow + numpy)
Writes into this folder:
  portrait-template.png   construction guides, mannequin and the expression kit at x4
  portraits-sheet.png     each expression at x4 next to the world sprite at x4, with ramp swatches
  portraits-atlas.png/json  native 48x48 cells: rows are characters, columns are expressions
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("portraits", "gate1", "cast", "scale-test"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import build_scale_test as bst  # noqa: E402
import portrait_engineer  # noqa: E402
import portrait_hal  # noqa: E402
import portrait_ivo  # noqa: E402
import portrait_mira  # noqa: E402
import portrait_vale  # noqa: E402
import portrait_template as T  # noqa: E402

CHARACTERS = [("engineer", portrait_engineer), ("ivo", portrait_ivo), ("mira", portrait_mira),
              ("vale", portrait_vale), ("hal", portrait_hal)]
EXPRESSIONS = list(T.KIT)
ZOOM = 4          # the world's zoom on 1366x768; portraits are shown at the same factor
BG = "#151C2B"
PLATE = "#343650"  # stand-in dialogue plate; the real plate comes from the UI tokens (task 10.1)
PAPER = "#F0DEC0"


def grid_img(grid, pal):
    """A 48x48 key grid as an RGBA image (generic sibling of build_gate1.frame_rgba, which is 16x24)."""
    h, w = len(grid), len(grid[0])
    arr = np.zeros((h, w, 4), np.uint8)
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            c = pal[ch]
            if c:
                arr[y, x, :3] = bst.hx(c)
                arr[y, x, 3] = 255
    return Image.fromarray(arr, "RGBA")


def sprite_img(mod, facing="s"):
    import build_gate1 as g
    return Image.fromarray(g.frame_rgba(mod.SPRITE.IDLE[facing][0], mod.PAL), "RGBA")


def up(im, z):
    return im.resize((im.width * z, im.height * z), Image.NEAREST)


def on(im, color, z):
    bg = Image.new("RGBA", im.size, color)
    bg.alpha_composite(im)
    return up(bg, z)


# ---- mannequin: a neutral stand-in drawn only from the ink and stone ramps ------------------
MAN_PAL = {".": None, "o": "#202337", "A": "#343650", "B": "#535971", "C": "#777A8C", "D": "#968A85",
           "k": "#665D65", "l": "#968A85", "m": "#C7B7A0", "n": "#F0DEC0",
           "p": "#343650", "q": "#535971", "r": "#777A8C", "s": "#968A85"}


def mannequin():
    g = [["."] * 48 for _ in range(48)]
    def span(r, a, b, k):
        for c in range(a, b + 1):
            g[r][c] = k
    for r, (a, b) in T.FACE.items():
        span(r, a, b, "m" if r > 17 else "m")
    for r, (a, b) in T.NECK.items():
        span(r, a, b, "l")
    for r, (a, b) in T.TORSO.items():
        span(r, a, b, "r" if r < 40 else "q")
    for r in range(19, 25):
        span(r, 11, 12, "m")
        span(r, 35, 36, "m")
    dome = {3: (19, 28), 4: (17, 30), 5: (15, 32), 6: (14, 33), 7: (13, 34), 8: (13, 34), 9: (13, 34),
            10: (13, 34), 11: (13, 34), 12: (14, 33), 13: (14, 33), 14: (14, 15), 15: (14, 15), 16: (14, 14)}
    for r, (a, b) in dome.items():
        span(r, a, b, "C")
        if r in (14, 15, 16):
            span(r, 32, 33, "C")
    # light: lit left cheek, shadowed right side
    for r in range(14, 32):
        a, b = T.FACE[r] if r >= 12 else (14, 33)
        for c in range(a, b + 1):
            if g[r][c] == "m" and c <= 21 - (r - 17) // 2:
                g[r][c] = "n"
            elif g[r][c] == "m" and c >= b - 1:
                g[r][c] = "l"
    out = [row[:] for row in g]
    for y in range(48):
        for x in range(48):
            if g[y][x] != ".":
                continue
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < 48 and 0 <= xx < 48 and g[yy][xx] != ".":
                    out[y][x] = "o"
                    break
    return ["".join(r) for r in out]


def guides(draw, ox, oy, z, label=True, font=None):
    """Draw the construction guides over a portrait drawn at (ox, oy) with zoom z."""
    G = T.GUIDE
    def hline(r, color, name, side="r", span=(0, 48)):
        y = oy + r * z
        draw.line([(ox + span[0] * z, y), (ox + span[1] * z, y)], fill=color, width=1)
        if label and font:
            if side == "r":
                draw.text((ox + 48 * z + 8, y - 8), name, font=font, fill=color)
            else:
                draw.text((ox - 8, y - 8), name, font=font, fill=color, anchor="ra")
    def vline(c, color, span=(0, 48)):
        x = ox + c * z
        draw.line([(x, oy + span[0] * z), (x, oy + span[1] * z)], fill=color, width=1)
    for c in range(16, 48, 16):                       # world tile grid
        vline(c, "#535971")
        draw.line([(ox, oy + c * z), (ox + 48 * z, oy + c * z)], fill="#535971", width=1)
    hline(G["hair_top_row"], "#5AA3AE", f"hair top  r{G['hair_top_row']}")
    hline(G["hairline_row"], "#5AA3AE", f"hairline  r{G['hairline_row']}", "l")
    hline(G["brow_row"], "#B2CE78", f"brows  r{G['brow_row']}")
    hline(G["eye_rows"][0], "#E67A70", f"eye line  r{G['eye_rows'][0]}-{G['eye_rows'][1]}", "l")
    hline(G["nose_row"], "#B2CE78", f"nose  r{G['nose_row']}")
    hline(G["mouth_row"], "#E67A70", f"mouth  r{G['mouth_row']}", "l")
    hline(G["chin_row"], "#5AA3AE", f"chin  r{G['chin_row']}")
    hline(G["shoulder_row"], "#E1AC62", f"shoulder line  r{G['shoulder_row']}", "l")
    hline(G["crop_row"] + 1, "#E1AC62", f"crop  r{G['crop_row']} (no outline below)")
    vline(24, "#F5D580")                               # centre axis between columns 23 and 24
    for c in (G["face_cols"][0] - 1, G["face_cols"][1] + 2):
        vline(c, "#B2CE78", span=(12, 33))
    for a, b in G["ear_cols"]:
        vline(a, "#96AAB6", span=(19, 25))
        vline(b + 1, "#96AAB6", span=(19, 25))
    vline(G["shoulder_cols"][0], "#E1AC62", span=(35, 48))
    vline(G["shoulder_cols"][1] + 1, "#E1AC62", span=(35, 48))
    if label and font:
        draw.text((ox + 24 * z + 4, oy + 1), "axis (23|24)", font=font, fill="#F5D580")


def build_template():
    f_t, f_s, f_n = bst.font(20, bold=True), bst.font(13), bst.font(12)
    z = ZOOM
    pw = 48 * z
    margin = 150
    W = margin + pw + margin + 40 + pw + 40 + 3 * (pw + 20) + 40
    H = 48 * z + 330
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((24, 14), "Portrait template · 48×48 logical px, head and shoulders · x4 (the world's zoom) · "
                     "light from the upper left · transparent background", font=f_t, fill="#F4F2EC")
    man = mannequin()
    mim = grid_img(man, MAN_PAL)
    oy = 70
    # A: guides on the mannequin
    ox = margin
    sheet.paste(on(mim, PLATE, z).convert("RGB"), (ox, oy))
    guides(d, ox, oy, z, True, f_s)
    d.text((ox, oy + pw + 10), "A  construction guides", font=bst.font(15, bold=True), fill="#E1AC62")
    # B: guides alone on a blank grid with the head box
    bx = ox + pw + margin + 40
    blank = Image.new("RGB", (pw, pw), PLATE)
    sheet.paste(blank, (bx, oy))
    guides(d, bx, oy, z, False)
    G = T.GUIDE
    d.rectangle([bx + 12 * z, oy + 1 * z, bx + 37 * z, oy + 33 * z], outline="#F4F2EC")
    d.text((bx + 13 * z, oy + 2 * z), "hair + head box\ncols 12-36, rows 1-32", font=f_n, fill="#F4F2EC")
    d.text((bx + 14 * z, oy + 36 * z), "shoulders\ncols 2-45", font=f_n, fill="#F4F2EC")
    d.text((bx, oy + pw + 10), "B  the same guides, blank", font=bst.font(15, bold=True), fill="#E1AC62")
    # C: kit on the mannequin
    cx = bx + pw + 40
    for i, e in enumerate(EXPRESSIONS):
        grid = T.compose(man, e, "klmn", "B")
        sheet.paste(on(grid_img(grid, MAN_PAL), PLATE, z).convert("RGB"), (cx + i * (pw + 20), oy))
        d.text((cx + i * (pw + 20), oy + pw + 10), f"C  {e}", font=bst.font(15, bold=True), fill="#E1AC62")
    # notes
    ny = oy + pw + 50
    notes = [
        "Frame: head rows 1-32 (hair top to chin), eye line rows 19-20 (a little over half way down the head), shoulders reach the full width by row 40-41, last row 47 is a crop with no outline.",
        "Light: upper left. Lit-edge swaps run along the upper-left contours (hair A, skin k, jacket p); the right and lower contours stay #202337. Darkest steps sit on contours only.",
        "Expression: brows, eyelids, mouth and a 1-px head tilt (rows 0-14 shift). Eyes are drawn with outline ink and skin; the sprite's 2-pixel face grows, it never changes identity.",
        "Palette: only the character's own world-sprite ramps. At most one extra step per ramp, recorded in the module's EXTRA dict. Background transparent: the dialogue panel provides the plate.",
        "Placement: shown at the world's zoom (x4 on 1366x768 = 192x192 screen px, x6 on 1920x1080 = 288x288), whole numbers only.",
    ]
    for i, n in enumerate(notes):
        d.text((24, ny + i * 22), n, font=f_s, fill="#C7B7A0")
    # native 1x thumbnail
    d.text((24, ny + 5 * 22 + 12), "Native 1×:", font=f_s, fill="#C7B7A0")
    sheet.paste(on(mim, PLATE, 1).convert("RGB"), (110, ny + 5 * 22 + 6))
    sheet.save(os.path.join(HERE, "portrait-template.png"))


def ramp_swatches(mod, d, x, y, used):
    """Swatches for every key the portrait uses, grouped by the world sprite's ramps."""
    f = bst.font(11)
    keys = [k for k in sorted(used) if k != "."]
    for i, k in enumerate(keys):
        d.rectangle([x + i * 26, y, x + i * 26 + 22, y + 14], fill=mod.PAL[k], outline="#535971")
        d.text((x + i * 26 + 11, y + 17), k, font=f, fill="#C7B7A0", anchor="ma")


def build_sheet():
    f_t, f_h = bst.font(20, bold=True), bst.font(16, bold=True)
    z = ZOOM
    pw = 48 * z
    sw, sh = 16 * z, 24 * z
    cell = pw + 24
    W = max(24 + 140 + 130 + 3 * cell, 1000)
    H = 70 + len(CHARACTERS) * (pw + 110)
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), "Portraits beside the world sprite · x4 · every portrait key is a key of the sprite's PAL",
           font=f_t, fill="#F4F2EC")
    y = 60
    for name, mod in CHARACTERS:
        d.text((24, y + 6), name.capitalize(), font=f_h, fill="#E1AC62")
        sx = 24 + 140
        spim = sprite_img(mod)
        sheet.paste(on(spim, PLATE, z).convert("RGB"), (sx, y + pw - sh))
        d.text((sx, y + pw + 6), "world sprite (S idle)", font=bst.font(12), fill="#C7B7A0")
        used = set()
        for i, e in enumerate(EXPRESSIONS):
            grid = mod.EXPRESSIONS[e]
            used |= {ch for r in grid for ch in r}
            px = sx + 130 + i * cell
            sheet.paste(on(grid_img(grid, mod.PAL), PLATE, z).convert("RGB"), (px, y))
            d.text((px, y + pw + 6), e, font=bst.font(14, bold=True), fill="#F4F2EC")
        ramp_swatches(mod, d, sx, y + pw + 34, used)
        d.text((sx, y + pw + 72), "keys used (same hex as the sprite)", font=bst.font(11), fill="#777A8C")
        y += pw + 110
    sheet.save(os.path.join(HERE, "portraits-sheet.png"))


def build_atlas():
    rows = [("engineer", portrait_engineer, 0), ("ivo", portrait_ivo, 0), ("mira", portrait_mira, 0)]
    rows += [(f"mira_patch{k}", portrait_mira, k) for k in range(1, 7)]
    rows += [("vale", portrait_vale, 0), ("hal", portrait_hal, 0)]
    atlas = Image.new("RGBA", (48 * len(EXPRESSIONS), 48 * len(rows)), (0, 0, 0, 0))
    entries = {}
    for r, (name, mod, k) in enumerate(rows):
        for c, e in enumerate(EXPRESSIONS):
            grid = mod.EXPRESSIONS[e]
            pal = mod.PAL
            if k:
                grid = mod.with_patches(grid, k)
                pal = mod.PATCH_PAL
            atlas.paste(grid_img(grid, pal), (c * 48, r * 48))
            entries[f"{name}_{e}"] = {"x": c * 48, "y": r * 48, "w": 48, "h": 48}
    atlas.save(os.path.join(HERE, "portraits-atlas.png"))
    meta = {
        "frame": {"w": 48, "h": 48},
        "columns": EXPRESSIONS,
        "rows": [name for name, _, _ in rows],
        "zoom": "same integer factor as the world (x4 at 1366x768, x6 at 1920x1080); never fractional",
        "origin": "top-left of the 48x48 cell sits on the dialogue panel's portrait slot; background is transparent",
        "mira_patch_rows": "mira_patchK is Mira wearing patches 1..K (the row 'mira' is K = 0)",
        "portraits": entries,
    }
    with open(os.path.join(HERE, "portraits-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=2)


if __name__ == "__main__":
    build_template()
    build_sheet()
    build_atlas()
    print("built portrait-template.png, portraits-sheet.png, portraits-atlas.png/json")
