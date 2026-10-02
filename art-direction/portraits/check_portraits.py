"""Objective portrait checks for the seven chibi portraits (every expression, and Mira's patch states).

Run: python3 check_portraits.py     Exit code 1 on any failure.
Rules (PORTRAIT_RULES.md): 48x48; every key is a key of the character's world-sprite PAL with the same
hex (recorded extras are pale eye-glint keys that already exist in that PAL; Mira's patch icons use
mira_patches.PATCH_PAL); no UI marker hex; no violet; row 0 and the side columns empty; a closed
outline (every opaque pixel that touches transparency is #0E1020); an oversized head; skin steps within
a budget of two (the blush key is counted apart); hair and clothing identity cues; the standard
expressions neutral, concerned and pleased exist and differ; shoulders identical across expressions;
the signature expressions differ from the standard ones; no two characters share a face (feature
masks); Mira's bun notch, her blush off the strap coral, and her six patch states.
"""
import colorsys
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("portraits", "gate1", "cast"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import chibi  # noqa: E402
import portrait_ada  # noqa: E402
import portrait_engineer  # noqa: E402
import portrait_hal  # noqa: E402
import portrait_ivo  # noqa: E402
import portrait_mira  # noqa: E402
import portrait_noor  # noqa: E402
import portrait_vale  # noqa: E402

MARKERS, VIOLET, OUTLINE = chibi.MARKERS, chibi.VIOLET, chibi.OUTLINE
CAST = [("engineer", portrait_engineer), ("ivo", portrait_ivo), ("mira", portrait_mira), ("noor", portrait_noor),
        ("hal", portrait_hal), ("ada", portrait_ada), ("vale", portrait_vale)]
SKIN_BUDGET = 2
fails = []
count = 0
NB = ((1, 0), (-1, 0), (0, 1), (0, -1))


def hls(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, l, s * 100


def diff(a, b):
    return sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def check_grid(name, grid, mod, pal):
    global count
    count += 1
    spr = mod.SPRITE
    if len(grid) != 48 or any(len(r) != 48 for r in grid):
        fails.append(f"{name}: not 48x48")
        return
    used = {ch for r in grid for ch in r} - {"."}
    patch_keys = set(getattr(mod, "PATCH_PAL", {})) - set(spr.PAL)
    for ch in used:
        if ch not in pal:
            fails.append(f"{name}: key {ch!r} is not in the palette")
        elif ch in spr.PAL:
            if pal[ch] != spr.PAL[ch]:
                fails.append(f"{name}: key {ch!r} differs from the world sprite ({pal[ch]} vs {spr.PAL[ch]})")
        elif ch not in patch_keys:
            fails.append(f"{name}: key {ch!r} is not a key of the sprite's PAL")
    hexes = {pal[ch] for ch in used if ch in pal}
    if hexes & MARKERS:
        fails.append(f"{name}: UI marker hex {sorted(hexes & MARKERS)}")
    if hexes & VIOLET:
        fails.append(f"{name}: violet on a person")
    if pal.get("o") != OUTLINE:
        fails.append(f"{name}: outline key is not {OUTLINE}")
    # frame: row 0 and the side columns empty; the shoulders run off the bottom edge
    if any(ch != "." for ch in grid[0]):
        fails.append(f"{name}: row 0 must stay clear (headroom)")
    if any(r[0] != "." or r[47] != "." for r in grid):
        fails.append(f"{name}: pixels on a side column")
    if not any(ch != "." for ch in grid[47]):
        fails.append(f"{name}: nothing on the crop row (the shoulders must run off the frame)")
    # closed outline: every opaque pixel that touches transparency is outline ink
    for y in range(48):
        for x in range(48):
            ch = grid[y][x]
            if ch in (".", "o"):
                continue
            for dy, dx in NB:
                yy, xx = y + dy, x + dx
                if 0 <= yy < 48 and 0 <= xx < 48 and grid[yy][xx] == ".":
                    fails.append(f"{name}: open silhouette at ({x},{y}) key {ch!r}")
                    break
    # an oversized head: wide at the eye line, and the head reaches high in the frame
    w24 = sum(ch != "." for ch in grid[24])
    if w24 < 32:
        fails.append(f"{name}: only {w24} px wide at row 24 (the chibi head must fill the frame)")
    top = next(y for y, r in enumerate(grid) if any(ch != "." for ch in r))
    if top > 3:
        fails.append(f"{name}: topmost row is {top} (hair starts at row 1-3)")
    # skin budget: two ramp steps on the portrait, the blush key apart
    skin = set(mod.SLOTS["skin"]) - {mod.SKIN["4"]}
    n_skin = len(used & skin)
    if n_skin > SKIN_BUDGET:
        fails.append(f"{name}: {n_skin} skin steps {sorted(used & skin)} (budget {SKIN_BUDGET})")
    # identity: the sprite's hair ramp and clothing are present, and the character's prop
    if len(used & set(mod.SLOTS["hair"])) < 3:
        fails.append(f"{name}: hair ramp barely used ({sorted(used & set(mod.SLOTS['hair']))})")
    if not used & set(mod.SLOTS["jacket"]):
        fails.append(f"{name}: no clothing key of the sprite")
    for k in mod.PROP_KEYS:
        if k not in used:
            fails.append(f"{name}: identity prop key {k!r} is missing")
    # glint limits of the world sprite, scaled by 4 for the larger area
    for key, limit in getattr(spr, "GLINT_LIMITS", {}).items():
        n = sum(r.count(key) for r in grid)
        if n > limit * 4:
            fails.append(f"{name}: {n} px of glint key {key!r} (limit {limit * 4})")
    check_darkest(name, grid, mod)
    # teal clothing stays muted
    for key in mod.SLOTS.get("jacket", ""):
        h, _, s = hls(spr.PAL[key])
        if 160 <= h <= 200 and s > 60:
            fails.append(f"{name}: clothing {spr.PAL[key]} is {s:.0f}% saturated teal")


def ramps(mod):
    """Ramps as groups of four keys, darkest first (Mira's jacket holds two ramps)."""
    out = []
    for slot, keys in mod.SLOTS.items():
        if len(keys) == 4 or slot in ("hair", "skin"):
            out.append(keys)
        elif len(keys) == 8:
            out += [keys[:4], keys[4:]]
    return out


def check_darkest(name, grid, mod):
    """A ramp's darkest step belongs on contours and occlusion edges, never as a fill."""
    for keys in ramps(mod):
        dark, ramp = keys[0], set(keys)
        for y in range(1, 47):
            for x in range(1, 47):
                if grid[y][x] == dark and {grid[y][x - 1], grid[y][x + 1], grid[y - 1][x], grid[y + 1][x]} <= ramp:
                    fails.append(f"{name}: darkest step {dark!r} used as fill at ({x},{y})")


def features(grid, mod):
    """Where the face is drawn: ink, brow and glint pixels inside the face window."""
    keys = {"o", mod.BROW, mod.SKIN["5"]}
    return {(y, x) for y in range(15, 35) for x in range(9, 39) if grid[y][x] in keys}


grids_of = {}
for cname, mod in CAST:
    # recorded extras: pale keys that exist in the sprite's PAL with the same hex
    for key, info in mod.EXTRA.items():
        if key not in mod.SPRITE.PAL or mod.SPRITE.PAL[key] != info["hex"]:
            fails.append(f"{cname}: recorded extra {key!r} is not a PAL step with that hex")
        elif hls(info["hex"])[1] < 0.82:
            fails.append(f"{cname}: recorded extra {key!r} is not a pale key")
    if mod.SKIN["5"] not in mod.EXTRA:
        fails.append(f"{cname}: the eye-glint key {mod.SKIN['5']!r} is not recorded in EXTRA")
    grids = mod.EXPRESSIONS
    grids_of[cname] = grids
    for e in chibi.STANDARD:
        if e not in grids:
            fails.append(f"{cname}: missing the standard expression {e!r}")
    for s in mod.SIGNATURES:
        if s not in grids:
            fails.append(f"{cname}: missing the signature expression {s!r}")
        if not s.startswith(cname + "_"):
            fails.append(f"{cname}: signature {s!r} must be named {cname}_<name>")
    if set(grids) != set(chibi.STANDARD) | set(mod.SIGNATURES):
        fails.append(f"{cname}: unexpected expressions {sorted(set(grids) - set(chibi.STANDARD) - set(mod.SIGNATURES))}")
    for e, grid in grids.items():
        check_grid(f"{cname}/{e}", grid, mod, mod.PAL)
    names = list(grids)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d = diff(grids[names[i]], grids[names[j]])
            if d < 12:
                fails.append(f"{cname}: {names[i]} and {names[j]} differ by only {d} px")
    base = grids["neutral"]
    for e in names[1:]:                # one body: rows 38-47 identical across expressions
        if grids[e][38:] != base[38:]:
            fails.append(f"{cname}/{e}: shoulders differ from neutral")

# No two characters share a face: for every shared expression the feature masks differ.
for e in chibi.STANDARD:
    for i in range(len(CAST)):
        for j in range(i + 1, len(CAST)):
            (a, ma), (b, mb) = CAST[i], CAST[j]
            d = len(features(grids_of[a][e], ma) ^ features(grids_of[b][e], mb))
            if d < 14:
                fails.append(f"{e}: {a} and {b} faces differ by only {d} feature px")

# Mira: the bun is separate from the dome (an ink notch inside the hair), and her blush is not the strap coral.
mg = portrait_mira.EXPRESSIONS["neutral"]
hair = set(portrait_mira.SLOTS["hair"])
notch = sum(1 for y in range(3, 10) for x in range(28, 36)
            if mg[y][x] == "o" and any(mg[y][x - k] in hair for k in (1, 2, 3)) and any(mg[y][x + k] in hair for k in (1, 2, 3)))
if notch < 5:
    fails.append(f"mira: the bun notch is too small ({notch} interior ink px; the bun must read separate from the dome)")
if portrait_mira.SKIN["4"] in "cdef":
    fails.append("mira: the blush uses a strap coral key")
for y in range(24, 31):
    if any(ch in "cdef" for ch in mg[y][8:40]):
        fails.append(f"mira: strap coral on the face at row {y}")

# Mira's patch states on the portrait: each is a valid portrait and adds at least five pixels; icons sit on the jacket.
mod = portrait_mira
patches = mod.patches
for e in mod.EXPRESSIONS:
    prev = mod.EXPRESSIONS[e]
    for k in range(1, 7):
        cur = mod.with_patches(mod.EXPRESSIONS[e], k)
        check_grid(f"mira/{e}/patch{k}", cur, mod, mod.PATCH_PAL)
        d = diff(cur, prev)
        if d < 5:
            fails.append(f"mira/{e}: patch {k} adds only {d} px to the portrait")
        prev = cur
base = mod.EXPRESSIONS["neutral"]
cells = {}
for k, patch in enumerate(patches.PORTRAIT_PATCHES, 1):
    n_px = 0
    for top, left, art in patch["stamps"]:
        if not (4 <= len(art) <= 6 and 4 <= max(len(r) for r in art) <= 6):
            fails.append(f"patch {k} icon is {max(len(r) for r in art)}x{len(art)} (4-6 px each way)")
        for dy, line in enumerate(art):
            for dx, ch in enumerate(line):
                if ch == ".":
                    continue
                n_px += 1
                cells[(left + dx, top + dy)] = k
                under = base[top + dy][left + dx]
                if under not in patches.JACKET:
                    fails.append(f"patch {k} icon pixel ({left + dx},{top + dy}) lies on {under!r}, not on the jacket")
                if top + dy < 38:
                    fails.append(f"patch {k} icon pixel ({left + dx},{top + dy}) is above the shoulders")
for (x, y), k in cells.items():
    for dx, dy in NB:
        m = cells.get((x + dx, y + dy))
        if m and m != k:
            fails.append(f"portrait patch icons {k} and {m} touch at ({x},{y})")
# icons must be distinct shapes at x4: no two icons share an outline mask
shapes = {k: frozenset((x - min(px for px, _ in [c for c, kk in cells.items() if kk == k]),
                        y - min(py for _, py in [c for c, kk in cells.items() if kk == k]))
                       for (x, y), kk in cells.items() if kk == k) for k in range(1, 7)}
if len(set(shapes.values())) != 6:
    fails.append("two patch icons share the same shape")

for f in fails:
    print("FAIL", f)
print(f"{count} portraits checked, {len(fails)} failures")
sys.exit(1 if fails else 0)
