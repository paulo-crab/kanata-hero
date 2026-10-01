"""Build the Orientation environment kit.

Run: python3 build_kit.py   (Pillow + numpy; run from anywhere)
Writes into this folder:
  orientation-atlas.png / .json          16 px tile and prop atlas with metadata
  orientation-review-room.json           cell layout that rebuilds the approved review room
  orientation-atlas-sheet.png            every entry at x4 with footprint, anchor and labels
  orientation-garden-states.png          garden landmark before / after at x4, plus changed pixels
  orientation-review-room-native.png     the room rebuilt from the atlas (320x192, no actors)
  orientation-review-room-1366x768.png   the Gate 1 still drawn from the atlas
Then runs the zero-diff proof (build_room.verify) and exits 1 if any pixel differs.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_room  # noqa: E402
import kitlib  # noqa: E402
import orientation_kit as ok  # noqa: E402
import build_scale_test as bst  # noqa: E402

CORAL_MARK = "#EC776D"
BG = "#151C2B"
SECTIONS = [(0, "FLOOR AND ROUTE"), (1, "WALLS"), (2, "SLIDING GLASS DOOR (closed, half, open)"),
            (3, "LAMP (post, off, glow states)"), (4, "PROPS"), (5, "GARDEN LANDMARK (registered parts)")]


def build_atlas():
    pieces, placements, anims = ok.build_pieces()
    pieces.sort(key=ok.group_rank)
    img, rects = kitlib.pack([(p.name, p.sprite) for p in pieces])
    img.save(os.path.join(HERE, "orientation-atlas.png"))
    meta = ok.atlas_json(pieces, rects, anims, ok.garden_landmark())
    with open(os.path.join(HERE, "orientation-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
        fh.write("\n")
    layout = ok.make_layout(placements, {"records_door": "closed", "lamp": "on", "garden": "before"})
    with open(os.path.join(HERE, "orientation-review-room.json"), "w") as fh:
        json.dump(layout, fh, indent=1)
        fh.write("\n")
    return pieces, meta, layout


def atlas_sheet(pieces, meta, rank_fn=None, sections=None, title=None, out="orientation-atlas-sheet.png"):
    """rank_fn, sections, title and out default to the Orientation sheet; other districts pass their own."""
    rank_fn = rank_fn or ok.group_rank
    sections = SECTIONS if sections is None else sections
    Z = 4
    f_name, f_small, f_head = bst.font(15, bold=True), bst.font(13), bst.font(20, bold=True)
    max_w = 2480
    pad = 18
    cells = []
    for p in pieces:
        e = next(x for x in meta["entries"] if x["name"] == p.name)
        h, w = p.sprite.shape[:2]
        fw, fh = e["footprint"]["cells"]
        ox, oy = e["footprint"]["origin_px"]
        # the box must hold the sprite and its footprint, which may sit outside it
        x0, y0 = min(0, ox), min(0, oy)
        x1, y1 = max(w, ox + fw * 16), max(h, oy + fh * 16)
        cells.append((p, e, x0, y0, (x1 - x0) * Z, (y1 - y0) * Z))
    # layout pass
    pos, x, y, row_h, rank = {}, pad, 70, 0, None
    for c in cells:
        p, e, x0, y0, bw, bh = c
        r = rank_fn(p)
        if r != rank:
            x, y = pad, y + row_h + (36 if rank is not None else 0)
            row_h, rank = 0, r
            pos[("head", r)] = (pad, y)
            y += 34
        cw = max(bw, 250)
        if x + cw > max_w:
            x, y, row_h = pad, y + row_h + 12, 0
        pos[p.name] = (x, y)
        x += cw + pad
        row_h = max(row_h, bh + 52)
    H = y + row_h + pad
    sheet = Image.new("RGB", (max_w + pad, H), BG)
    d = ImageDraw.Draw(sheet)
    title = title or ("Orientation kit atlas, x4 on a checker. Coral box: footprint cells. Coral cross: anchor. "
                      "Tags under each name: layer, footprint, size in px.")
    d.text((pad, 16), title, font=f_head, fill="#F4F2EC")
    for r, sec in sections:
        if ("head", r) in pos:
            d.text(pos[("head", r)], sec, font=f_head, fill="#E6B750")
    for p, e, x0, y0, bw, bh in cells:
        px, py = pos[p.name]
        # checker
        chk = Image.new("RGB", (bw, bh))
        cd = ImageDraw.Draw(chk)
        for cy in range(0, bh, 16):
            for cx in range(0, bw, 16):
                cd.rectangle([cx, cy, cx + 15, cy + 15], fill="#2B3043" if (cx // 16 + cy // 16) % 2 == 0 else "#262A3B")
        sp = Image.fromarray(p.sprite, "RGBA").resize((p.sprite.shape[1] * Z, p.sprite.shape[0] * Z), Image.NEAREST)
        chk.paste(sp, (-x0 * Z, -y0 * Z), sp)
        sheet.paste(chk, (px, py))
        d = ImageDraw.Draw(sheet)
        ox, oy = e["footprint"]["origin_px"]
        fw, fh = e["footprint"]["cells"]
        fx, fy = px + (ox - x0) * Z, py + (oy - y0) * Z
        blocked = e["collision"]
        for ry, row in enumerate(blocked):
            for rx, ch in enumerate(row):
                cxp, cyp = fx + rx * 16 * Z, fy + ry * 16 * Z
                d.rectangle([cxp, cyp, cxp + 16 * Z - 1, cyp + 16 * Z - 1], outline=CORAL_MARK, width=1 if ch == "0" else 3)
        ax, ay = px + (e["anchor"][0] - x0) * Z, py + (e["anchor"][1] - y0) * Z
        d.line([(ax - 8, ay), (ax + 8, ay)], fill=CORAL_MARK, width=2)
        d.line([(ax, ay - 8), (ax, ay + 8)], fill=CORAL_MARK, width=2)
        if "contact_shadow" in e:
            sx, sy, sw, sh = e["contact_shadow"]
            d.rectangle([px + (sx - x0) * Z, py + (sy - y0) * Z, px + (sx - x0 + sw) * Z - 1, py + (sy - y0 + sh) * Z - 1],
                        outline="#A0DDD4", width=1)
        ty = py + bh + 4
        d.text((px, ty), p.name, font=f_name, fill="#F4F2EC")
        fw_h = f"{fw}x{fh}"
        d.text((px, ty + 18), f"{e['layer']} · fp {fw_h} · {e['size_px'][0]}x{e['size_px'][1]}px"
               + ("" if e["composite"]["mode"] == "over" else " · where_color"), font=f_small, fill="#C5CED0")
    d.text((pad, H - 26), "Heavy coral cell outline = blocked, thin = walkable. Teal rectangle = contact shadow baked "
           "into the sprite.", font=f_small, fill="#9FB3BD")
    sheet.save(os.path.join(HERE, out))


def garden_states(layout, atlas):
    box = (64, 48, 208, 168)
    Z = 4
    imgs = {}
    for st in ("before", "after"):
        lay = build_room.with_states(layout, garden=st)
        imgs[st] = build_room.rebuild(lay, atlas, 0.0)[box[1]:box[3], box[0]:box[2]]
    changed = np.any(imgs["before"] != imgs["after"], axis=2)
    dim = imgs["after"].copy()
    dim[~changed] = (imgs["after"][~changed] * 0.35 + np.array(bst.INK[0]) * 0.65).astype(np.uint8)  # diagnostic only
    panels = [("BEFORE: the approved room", imgs["before"]), ("AFTER: Orientation quest complete", imgs["after"]),
              (f"CHANGED: {int(changed.sum())} px (rest dimmed)", dim)]
    pw, ph = (box[2] - box[0]) * Z, (box[3] - box[1]) * Z
    sheet = Image.new("RGB", (len(panels) * (pw + 20) + 20, ph + 80), BG)
    d = ImageDraw.Draw(sheet)
    for i, (title, im) in enumerate(panels):
        x = 20 + i * (pw + 20)
        sheet.paste(Image.fromarray(im).resize((pw, ph), Image.NEAREST), (x, 50))
        d.text((x, 16), title, font=bst.font(20, bold=True), fill="#F4F2EC")
    sheet.save(os.path.join(HERE, "orientation-garden-states.png"))
    return int(changed.sum())


def main():
    pieces, meta, layout = build_atlas()
    atlas = kitlib.Atlas(os.path.join(HERE, "orientation-atlas.json"))
    atlas_sheet(pieces, meta)
    n = garden_states(layout, atlas)
    print(f"{len(pieces)} entries; garden before/after differ in {n} px")
    res = build_room.build()
    bad = {k: v for k, v in res.items() if v}
    print("ZERO DIFF" if not bad else f"DIFFERS: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
