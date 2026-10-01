"""Objective checks for the Pace signage set. Exit code 1 on any failure.

Run: python3 check_pace.py   (needs numpy; Pillow to compare the built atlas)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pace_art as pa  # noqa: E402

fails = []
hexes = set(pa.PAL.values())
EDGE_OK = {pa.PAL[k] for k in "otakDdpb"}  # contour, shadow and trim steps only


def hexof(px):
    return "#%02X%02X%02X" % tuple(int(v) for v in px[:3])


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# Palette hygiene.
for k, h in pa.PAL.items():
    if h in pa.MARKERS:
        fails.append(f"PAL {k}: UI marker hex {h}")
    if h in pa.VIOLET:
        fails.append(f"PAL {k}: violet {h}")
for name, rows, n in (("ICON16", pa.ICON16, 16), ("ICON8", pa.ICON8, 8)):
    if len(rows) != n or any(len(r) != n for r in rows):
        fails.append(f"{name}: not {n}x{n}")
    if set("".join(rows)) - set(pa.PAL) - {"."}:
        fails.append(f"{name}: unknown keys")

pieces = pa.build_all()
for name, a in pieces.items():
    h, w = a.shape[:2]
    spec = pa.PIECES[name]
    fp = spec["footprint"]
    # On the grid: half-cell multiples (as for the 16x24 person), whole cells for floor markings.
    if w % 8 or h % 8:
        fails.append(f"{name}: {w}x{h} off the 8 px grid")
    if spec["layer"] == "floor_marking" and (w % 16 or h % 16):
        fails.append(f"{name}: floor marking {w}x{h} is not whole cells")
    if name != "pace_icon_8":
        ox, oy = spec["origin"]
        if spec["layer"] == "rear_prop":
            if (w, h) != (fp[0] * 16 + ox, oy + fp[1] * 16):
                fails.append(f"{name}: {w}x{h} does not match footprint + origin")
        elif w > fp[0] * 16 or h > fp[1] * 16:
            fails.append(f"{name}: {w}x{h} larger than its {fp} footprint")
    if set(np.unique(a[:, :, 3])) - {0, 255}:
        fails.append(f"{name}: partial alpha")
    op = a[:, :, 3] == 255
    ys, xs = np.nonzero(op)
    used = {hexof(a[y, x]) for y, x in zip(ys, xs)}
    if used - hexes:
        fails.append(f"{name}: colours outside PAL {sorted(used - hexes)}")
    if used & pa.MARKERS:
        fails.append(f"{name}: UI marker hex {used & pa.MARKERS}")
    if used & pa.VIOLET:
        fails.append(f"{name}: violet {used & pa.VIOLET}")
    for key, limit in pa.GLINT_LIMITS.items():
        n = sum(1 for y, x in zip(ys, xs) if hexof(a[y, x]) == pa.PAL[key])
        if n > limit:
            fails.append(f"{name}: {n} px of glint {pa.PAL[key]} (limit {limit})")
    # Lit glass (the teal-looking steps) stays a small share: no teal-glow look.
    lit = sum(1 for y, x in zip(ys, xs) if hexof(a[y, x]) in (pa.PAL["g"], pa.PAL["h"]))
    if lit / op.sum() > 0.15:
        fails.append(f"{name}: lit glass is {lit / op.sum():.0%} of the piece (limit 15%)")
    # Contours: any pixel touching transparency is an ink, stone-dark, shadow or trim step,
    # so no glass or cream pixel ever forms a halo or glow edge.
    bad = []
    for y, x in zip(ys, xs):
        if hexof(a[y, x]) in EDGE_OK:
            continue
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and a[yy, xx, 3] == 0:
                bad.append((x, y, hexof(a[y, x])))
                break
    if bad:
        fails.append(f"{name}: non-contour pixels on the edge {bad[:3]}")
    # Floor glyphs stay legible on their slab.
    if spec["layer"] == "floor_marking":
        c = contrast(pa.PAL["f"], pa.PAL["s"])
        if c < 3:
            fails.append(f"{name}: glyph contrast {c:.1f}:1 on the slab (min 3:1)")

# The 16x16 icon keeps its three bars (rows with a 6-wide cream run) and a route chevron.
if sum(1 for r in pa.ICON16 if "SSSSSS" in r) < 2 or sum(r[1:-1].count("S") for r in pa.ICON16) < 20:
    fails.append("ICON16 lost its bars")

# The atlas must match a rebuild of the source.
atlas_png = os.path.join(HERE, "pace-atlas.png")
atlas_json = os.path.join(HERE, "pace-atlas.json")
if os.path.exists(atlas_png) and os.path.exists(atlas_json):
    from PIL import Image
    atlas = np.array(Image.open(atlas_png).convert("RGBA"))
    meta = json.load(open(atlas_json))
    for name, a in pieces.items():
        e = meta["entries"].get(name)
        if not e:
            fails.append(f"atlas json missing {name}")
            continue
        x, y, w, h = e["rect"]
        if not np.array_equal(atlas[y:y + h, x:x + w], a):
            fails.append(f"atlas pixels differ from source for {name}")
        if e["layer"] not in ("rear_wall", "floor_marking", "rear_prop"):
            fails.append(f"{name}: bad layer {e['layer']}")
else:
    fails.append("atlas not built yet (run build_pace.py)")

for f in fails:
    print("FAIL", f)
print(f"{len(pieces)} pieces checked, {len(fails)} failures")
sys.exit(1 if fails else 0)
