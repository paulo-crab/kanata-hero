"""Objective portrait checks for Engineer, Ivo and Mira (every expression, and Mira's patch states).

Run: python3 check_portraits.py     Exit code 1 on any failure.
Rules (PORTRAIT_RULES.md): 48x48, every hex belongs to the character's world-sprite palette
(or a recorded extra), no UI marker hex, no violet, a closed outline, darkest steps on
contours only, row 0 and the side columns empty, no outline on the crop row, hair against
skin where flagged, teal jacket saturation, expressions distinct, patches on the jacket.
"""
import colorsys
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("portraits", "gate1", "cast"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import portrait_engineer  # noqa: E402
import portrait_hal  # noqa: E402
import portrait_ivo  # noqa: E402
import portrait_mira  # noqa: E402
import portrait_vale  # noqa: E402
import portrait_template as T  # noqa: E402

MARKERS = {"#19AFA2", "#EC776D", "#9876D5", "#E6B750"}
VIOLET = {"#413755", "#67547C", "#9477AF", "#C3A6D6"}
OUTLINE = "#202337"
fails = []
count = 0


def hsl(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, s * 100


def ramps(mod):
    """Ramps as groups of four keys, darkest first (Mira's jacket holds two ramps)."""
    out = []
    for slot, keys in mod.SLOTS.items():
        if len(keys) == 4 or slot in ("hair", "skin"):
            out.append(keys)
        elif len(keys) == 8:
            out += [keys[:4], keys[4:]]
    return out


def check_grid(name, grid, mod, pal, jacket_under=None):
    global count
    count += 1
    spr = mod.SPRITE
    if len(grid) != 48 or any(len(r) != 48 for r in grid):
        fails.append(f"{name}: not 48x48")
        return
    used = {ch for r in grid for ch in r} - {"."}
    # palette: same hex as the world sprite, or a recorded extra, or a patch key
    for ch in used:
        if ch not in pal:
            fails.append(f"{name}: key {ch!r} is not in the palette")
            continue
        if ch in spr.PAL and pal[ch] != spr.PAL[ch]:
            fails.append(f"{name}: key {ch!r} differs from the world sprite ({pal[ch]} vs {spr.PAL[ch]})")
        if ch not in spr.PAL and ch not in mod.EXTRA and not (hasattr(mod, "PATCH_PAL") and ch in mod.patches.PATCH_PAL):
            fails.append(f"{name}: key {ch!r} is neither a sprite key nor a recorded extra")
    hexes = {pal[ch] for ch in used if ch in pal}
    if hexes & MARKERS:
        fails.append(f"{name}: UI marker hex {sorted(hexes & MARKERS)}")
    if hexes & VIOLET:
        fails.append(f"{name}: violet on a person")
    # frame: row 0 and the side columns empty, nothing outlined on the crop row
    if any(ch != "." for ch in grid[0]):
        fails.append(f"{name}: row 0 must stay clear (headroom)")
    if any(r[0] != "." or r[47] != "." for r in grid):
        fails.append(f"{name}: pixels on a side column")
    if any(ch == "o" for ch in grid[47][2:46]):
        fails.append(f"{name}: outline on the crop row")
    if not any(ch != "." for ch in grid[47]):
        fails.append(f"{name}: nothing on the crop row (shoulders must run off the frame)")
    # closed outline: every opaque pixel touching transparency is outline ink or a contour-swap step
    contour = {"o"} | {r[0] for r in ramps(mod)}
    for y in range(47):
        for x in range(48):
            ch = grid[y][x]
            if ch == ".":
                continue
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < 48 and 0 <= xx < 48 and grid[yy][xx] == "." and ch not in contour:
                    fails.append(f"{name}: open silhouette at ({x},{y}) key {ch!r}")
                    break
    n_o = sum(r.count("o") for r in grid)
    if n_o < 60:
        fails.append(f"{name}: only {n_o} outline pixels")
    # darkest step of each ramp on contours only
    for keys in ramps(mod):
        dark, ramp = keys[0], set(keys)
        for y in range(1, 47):
            for x in range(1, 47):
                if grid[y][x] == dark and {grid[y][x - 1], grid[y][x + 1], grid[y - 1][x], grid[y + 1][x]} <= ramp:
                    fails.append(f"{name}: darkest step {dark!r} used as fill at ({x},{y})")
    # hair against skin
    hair, skin = mod.SLOTS["hair"], mod.SLOTS["skin"]
    nb = ((1, 0), (-1, 0), (0, 1), (0, -1))
    if getattr(mod, "HAIR_SKIN_SEPARATED", False):
        light_hair, lit_skin = set(hair[1:]), set(skin[1:])
        bad = [(x, y) for y in range(1, 47) for x in range(1, 47) if grid[y][x] in light_hair
               and any(grid[y + dy][x + dx] in lit_skin for dy, dx in nb)]
        if bad:
            fails.append(f"{name}: light hair touches lit skin at {bad[:4]}")
    only = getattr(mod, "HAIR_TOUCH_SKIN", None)
    if only:
        bad = [(x, y) for y in range(1, 47) for x in range(1, 47) if grid[y][x] in hair
               and any(grid[y + dy][x + dx] in skin and grid[y + dy][x + dx] not in only for dy, dx in nb)]
        if bad:
            fails.append(f"{name}: hair touches a skin step outside {only!r} at {bad[:4]}")
    # glint limits of the world sprite, scaled by the 3x area of a portrait detail (x4 as a cap)
    for key, limit in getattr(spr, "GLINT_LIMITS", {}).items():
        n = sum(r.count(key) for r in grid)
        if n > limit * 4:
            fails.append(f"{name}: {n} px of glint key {key!r} (limit {limit * 4})")
    # teal jackets stay muted
    for key in mod.SLOTS.get("jacket", ""):
        h, s = hsl(spr.PAL[key])
        if 160 <= h <= 200 and s > 60:
            fails.append(f"{name}: jacket {spr.PAL[key]} is {s:.0f}% saturated")


def diff(a, b):
    return sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


for cname, mod in (("engineer", portrait_engineer), ("ivo", portrait_ivo), ("mira", portrait_mira), ("vale", portrait_vale), ("hal", portrait_hal)):
    # extras: recorded, at most one per ramp
    per_ramp = {}
    for key, info in mod.EXTRA.items():
        per_ramp[info["ramp"]] = per_ramp.get(info["ramp"], 0) + 1
    for ramp, n in per_ramp.items():
        if n > 1:
            fails.append(f"{cname}: {n} extra steps on ramp {ramp!r} (limit 1)")
    grids = {}
    for e in mod.EXPRESSIONS:      # the three standard expressions plus any character-specific extras
        grid = mod.EXPRESSIONS[e]
        grids[e] = grid
        check_grid(f"{cname}/{e}", grid, mod, mod.PAL)
    for e in T.KIT:
        if e not in grids:
            fails.append(f"{cname}: missing the standard expression {e!r}")
    names = list(T.KIT)
    for i in range(3):
        for j in range(i + 1, 3):
            d = diff(grids[names[i]], grids[names[j]])
            if d < 40:
                fails.append(f"{cname}: {names[i]} and {names[j]} differ by only {d} px")
    # the three expressions share one body: rows 36-47 identical
    for e in names[1:]:
        if grids[e][36:] != grids[names[0]][36:]:
            fails.append(f"{cname}/{e}: shoulders differ from neutral")

# Mira's patch states on the portrait: each state is a valid portrait and differs from the last
mod = portrait_mira
patches = mod.patches
for e in T.KIT:
    prev = mod.EXPRESSIONS[e]
    for k in range(1, 7):
        cur = mod.with_patches(mod.EXPRESSIONS[e], k)
        check_grid(f"mira/{e}/patch{k}", cur, mod, mod.PATCH_PAL)
        d = diff(cur, prev)
        if d < 5:
            fails.append(f"mira/{e}: patch {k} adds only {d} px to the portrait")
        prev = cur
for k, patch in enumerate(patches.PORTRAIT_PATCHES, 1):
    for top, left, art in patch["stamps"]:
        for dy, line in enumerate(art):
            for dx, ch in enumerate(line):
                if ch == ".":
                    continue
                base = mod.BASE[top + dy][left + dx]
                if base not in patches.JACKET:
                    fails.append(f"patch {k} icon pixel ({left + dx},{top + dy}) lies on {base!r}, not on the jacket")
for e in T.KIT:   # icons keep clear of each other
    cells = {}
    for k, patch in enumerate(patches.PORTRAIT_PATCHES, 1):
        for top, left, art in patch["stamps"]:
            for dy, line in enumerate(art):
                for dx, ch in enumerate(line):
                    if ch != ".":
                        cells[(left + dx, top + dy)] = k
    for (x, y), k in cells.items():
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            m = cells.get((x + dx, y + dy))
            if m and m != k:
                fails.append(f"portrait patch icons {k} and {m} touch at ({x},{y})")
    break

for f in fails:
    print("FAIL", f)
print(f"{count} portraits checked, {len(fails)} failures")
sys.exit(1 if fails else 0)
